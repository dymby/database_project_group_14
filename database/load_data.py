"""
load_data.py - cleans the two real-world datasets and inserts them into mock.db
in normalized form. Every cleaning decision is documented in docs/data_cleaning.md.

Datasets (raw copies in data/raw/):
  A. Inside Airbnb Amsterdam listings (CC BY 4.0, compiled 2026-06-15)
  B. Amsterdam BAG: nummeraanduidingen + verblijfsobjecten (CC0 1.0, 2022-11-04)

Usage:  python database/load_data.py      (called by build_db.py)
"""
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
    addr = addr.drop_duplicates("identificatie")
    log("bag_duplicate_address_ids", 0)

    # missing postcode -> address cannot be stored (Postalcode NOT NULL / FK)
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


def none(x):
    return None if pd.isna(x) else x


def load():
    if not DB_PATH.exists():
        raise SystemExit("mock.db not found - run build_db.py first")
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
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

    conn.commit()
    bad = conn.execute("PRAGMA foreign_key_check").fetchall()
    log("foreign_key_violations", len(bad))
    conn.close()


if __name__ == "__main__":
    load()
