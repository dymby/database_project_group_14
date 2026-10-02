"""
load_data.py - cleans the three real-world datasets and inserts them into mock.db
in normalized form. Every cleaning decision is documented in docs/data_cleaning.md.

Datasets (raw copies in data/raw/):
  A. Inside Airbnb Amsterdam listings (CC BY 4.0, compiled 2026-06-15)
  B. Amsterdam BAG: nummeraanduidingen + verblijfsobjecten (CC0 1.0, 2022-11-04)
  C. Kaggle Dutch housing: address, city, lot size

Usage:  python database/load_data.py      (called by build_db.py)
"""
import re
import sqlite3
from pathlib import Path

import pandas as pd

DB_DIR = Path(__file__).resolve().parent
RAW = DB_DIR.parent / "data" / "raw"
DB_PATH = DB_DIR / "mock.db"

stats = {}


def log(key, value):
    stats[key] = value
    print(f"  {key}: {value}")


def clean_bag():
    addr = pd.read_csv(RAW / "bag-nummeraanduidingen.csv", dtype=str)
    vbo = pd.read_csv(RAW / "bag-verblijfsobjecten.csv", dtype=str)
    streets = pd.read_csv(RAW / "bag-openbareruimtes-lookup.csv", dtype=str)
    log("bag_address_rows_raw", len(addr))
    log("bag_dwelling_rows_raw", len(vbo))

    # duplicates
    log("bag_duplicate_address_ids", int(addr.identificatie.duplicated().sum()))
    addr = addr.drop_duplicates("identificatie")

    # missing postcode -> address cannot be stored (the postcode is the key to street and city)
    missing_pc = addr.postcode.isna()
    log("bag_dropped_missing_postcode", int(missing_pc.sum()))
    addr = addr[~missing_pc].copy()

    # postcode '1015NR' -> '1015 NR' (same format as the rest of the database)
    addr["postcode"] = addr.postcode.str.strip().str.upper().str[:4] + " " + addr.postcode.str.strip().str.upper().str[4:]
    addr["huisnummer"] = addr.huisnummer.astype(int)
    addr = addr.merge(streets.rename(columns={"identificatie": "ligtAanOpenbareruimteId", "naam": "street"}),
                      on="ligtAanOpenbareruimteId", how="left")
    assert addr.street.notna().all(), "street lookup incomplete"

    # dwellings: keep only plausible surface areas
    vbo["oppervlakte"] = vbo.oppervlakte.astype(int)
    bad = ~vbo.oppervlakte.between(5, 1000)
    log("bag_dropped_implausible_area", int(bad.sum()))
    vbo = vbo[~bad]
    houses = vbo.merge(addr[["identificatie", "postcode"]], left_on="heeftHoofdadresId",
                       right_on="identificatie", suffixes=("_v", ""))
    log("bag_dwellings_without_matching_address", len(vbo) - len(houses))
    return addr, houses


def clean_airbnb():
    lst = pd.read_csv(RAW / "airbnb-amsterdam-listings.csv", dtype={"host_id": str})
    log("airbnb_rows_raw", len(lst))
    log("airbnb_duplicate_ids", int(lst.id.duplicated().sum()))
    for c in ["name", "host_name", "neighbourhood", "room_type"]:
        lst[c] = lst[c].str.strip()
    lst["host_id"] = lst.host_id.str.replace(r"\.0$", "", regex=True)
    log("airbnb_price_missing_set_null", int(lst.price.isna().sum()))
    log("airbnb_host_id_missing", int(lst.host_id.isna().sum()))
    lst["last_review"] = pd.to_datetime(lst.last_review, format="%Y-%m-%d", errors="coerce").dt.strftime("%Y-%m-%d")
    return lst


def split_address(address):
    """'Bovenweg 12 a' -> ('Bovenweg', 12, 'A', None)"""
    m = re.match(r"^(.*?)\s+(\d+)\s*(.*)$", address.strip())
    if not m:
        return address.strip(), None, None, None
    street, number, rest = m.group(1), int(m.group(2)), m.group(3).strip()
    if len(rest) == 1 and rest.isalpha():
        return street, number, rest.upper(), None
    return street, number, None, rest or None


def parse_lot_size(text):
    """'5.440 m²' -> 5440 (the dot is a thousands separator)"""
    return int(text.replace("m²", "").replace(".", "").strip())


def clean_kaggle():
    df = pd.read_csv(RAW / "kaggle_housing.csv", dtype=str)
    log("kaggle_rows_raw", len(df))
    for c in ["Address", "City"]:
        df[c] = df[c].str.strip()
    dup = df.duplicated()
    log("kaggle_duplicate_rows_dropped", int(dup.sum()))
    df = df[~dup].copy()
    parts = [split_address(a) for a in df["Address"]]
    df["street"] = [p[0] for p in parts]
    df["number"] = pd.array([p[1] for p in parts], dtype="Int64")
    df["letter"] = [p[2] for p in parts]
    df["addition"] = [p[3] for p in parts]
    log("kaggle_address_without_number", int(df.number.isna().sum()))
    log("kaggle_lot_size_with_thousands_separator", int(df["Lot size (m2)"].str.contains(".", regex=False).sum()))
    df["lot_size_sqm"] = df["Lot size (m2)"].map(parse_lot_size)
    return df


def none(x):
    return None if pd.isna(x) else x


def load(conn):
    cur = conn.cursor()

    print("Dataset B - BAG")
    addr, houses = clean_bag()
    cur.execute("INSERT OR IGNORE INTO City (Name) VALUES ('Amsterdam')")   # woonplaats 3594
    city_id = cur.execute("SELECT CityID FROM City WHERE Name='Amsterdam'").fetchone()[0]
    pcs = addr[["postcode", "street"]].drop_duplicates()
    assert not pcs.postcode.duplicated().any(), "postcode maps to >1 street: 3NF assumption broken"
    cur.executemany("INSERT INTO Postcode (Postalcode, Street, City_CityID) VALUES (?,?,?)",
                    [(r.postcode, r.street, city_id) for r in pcs.itertuples()])
    cur.executemany(
        "INSERT INTO address (Postalcode, Number, Letter, Addition, bag_address_id) VALUES (?,?,?,?,?)",
        [(r.postcode, r.huisnummer, none(r.huisletter), none(r.huisnummertoevoeging), r.identificatie)
         for r in addr.itertuples()])
    ids = dict(cur.execute("SELECT bag_address_id, addressID FROM address WHERE bag_address_id IS NOT NULL"))
    cur.executemany("INSERT INTO House (address_addressID, size_sqm) VALUES (?,?)",
                    [(ids[r.heeftHoofdadresId], r.oppervlakte) for r in houses.itertuples()])
    log("loaded_postcodes", len(pcs)); log("loaded_addresses", len(addr)); log("loaded_houses", len(houses))

    print("Dataset A - Airbnb")
    lst = clean_airbnb()
    hosts = lst.dropna(subset=["host_id"]).drop_duplicates("host_id")
    cur.executemany("INSERT INTO People (First_Name, source_host_id) VALUES (?,?)",
                    [(none(r.host_name), r.host_id) for r in hosts.itertuples()])
    cur.execute("INSERT INTO Landlord (People_PeopleID) SELECT PeopleID FROM People WHERE source_host_id IS NOT NULL")
    hostmap = dict(cur.execute("SELECT source_host_id, PeopleID FROM People WHERE source_host_id IS NOT NULL"))
    cur.executemany("INSERT INTO Neighbourhood (Name, City_CityID) VALUES (?,?)",
                    [(n, city_id) for n in sorted(lst.neighbourhood.unique())])
    nmap = dict(cur.execute("SELECT Name, NeighbourhoodID FROM Neighbourhood"))
    cur.executemany(
        "INSERT INTO Listing (ListingID, Name, Landlord_PeopleID, Neighbourhood_NeighbourhoodID, room_type, "
        "price_per_night, minimum_nights, latitude, longitude, last_review) VALUES (?,?,?,?,?,?,?,?,?,?)",
        [(int(r.id), none(r.name), hostmap.get(r.host_id) if pd.notna(r.host_id) else None, nmap[r.neighbourhood],
          r.room_type, None if pd.isna(r.price) else int(round(r.price)),
          None if pd.isna(r.minimum_nights) else int(r.minimum_nights), r.latitude, r.longitude, none(r.last_review))
         for r in lst.itertuples()])
    log("loaded_hosts", len(hosts)); log("loaded_neighbourhoods", len(nmap)); log("loaded_listings", len(lst))


def load_kaggle(conn):
    cur = conn.cursor()

    print("Dataset C - Kaggle")
    df = clean_kaggle()
    cur.executemany("INSERT OR IGNORE INTO City (Name) VALUES (?)", [(c,) for c in sorted(df.City.unique())])
    citymap = dict(cur.execute("SELECT Name, CityID FROM City"))
    first_id = cur.execute("SELECT IFNULL(MAX(addressID), 0) FROM address").fetchone()[0] + 1
    cur.executemany(
        "INSERT INTO address (addressID, Street, City_CityID, Number, Letter, Addition) VALUES (?,?,?,?,?,?)",
        [(first_id + i, r.street, citymap[r.City], None if pd.isna(r.number) else int(r.number),
          none(r.letter), none(r.addition)) for i, r in enumerate(df.itertuples())])
    cur.executemany("INSERT INTO House (address_addressID, lot_size_sqm) VALUES (?,?)",
                    [(first_id + i, int(r.lot_size_sqm)) for i, r in enumerate(df.itertuples())])
    log("loaded_kaggle_cities", int(df.City.nunique())); log("loaded_kaggle_addresses", len(df))
    log("loaded_kaggle_houses", len(df))


def load_all(db_path=DB_PATH):
    if not Path(db_path).exists():
        raise SystemExit("mock.db not found - run build_db.py first")
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        loaded = conn.execute("SELECT (SELECT COUNT(*) FROM address WHERE bag_address_id IS NOT NULL OR Postalcode IS NULL)"
                              " + (SELECT COUNT(*) FROM Listing)").fetchone()[0]
        if loaded:
            raise SystemExit("real data is already loaded - rebuild with build_db.py instead of loading twice")
        load(conn)
        load_kaggle(conn)
        bad = conn.execute("PRAGMA foreign_key_check").fetchall()
        log("foreign_key_violations", len(bad))
        if bad:
            raise SystemExit("foreign key violations after loading - nothing was saved")
        conn.commit()
    finally:
        conn.rollback()
        conn.close()


if __name__ == "__main__":
    load_all()
