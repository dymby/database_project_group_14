"""Read-only check of mock.db: integrity, foreign keys and row counts against the raw CSV files."""
import contextlib
import io
import sqlite3
import sys
from pathlib import Path

import load_data

DB_PATH = Path(__file__).resolve().parent / "mock.db"
TABLES = ["City", "Postcode", "address", "People", "Renter", "Landlord", "Contract", "House",
          "Neighbourhood", "Listing"]


def check(db_path=DB_PATH):
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    failed = []

    def expect(name, actual, expected):
        ok = actual == expected
        print(f"  {'OK  ' if ok else 'FAIL'} {name}: {actual}" + ("" if ok else f" (expected {expected})"))
        if not ok:
            failed.append(name)

    def count(sql):
        return conn.execute(sql).fetchone()[0]

    try:
        print("Integrity")
        expect("integrity_check", conn.execute("PRAGMA integrity_check").fetchone()[0], "ok")
        expect("foreign_key_violations", len(conn.execute("PRAGMA foreign_key_check").fetchall()), 0)

        print("Rows per table")
        for t in TABLES:
            print(f"       {t}: {count(f'SELECT COUNT(*) FROM [{t}]')}")

        print("Database against the raw files")
        with contextlib.redirect_stdout(io.StringIO()):
            addr, houses = load_data.clean_bag()
            lst = load_data.clean_airbnb()
            kaggle = load_data.clean_kaggle()
        expect("bag_addresses", count("SELECT COUNT(*) FROM address WHERE bag_address_id IS NOT NULL"), len(addr))
        expect("bag_houses", count("SELECT COUNT(*) FROM House JOIN address ON addressID = address_addressID "
                                   "WHERE bag_address_id IS NOT NULL"), len(houses))
        expect("bag_postcodes", count("SELECT COUNT(DISTINCT Postalcode) FROM address WHERE bag_address_id IS NOT NULL"),
               addr.postcode.nunique())
        expect("airbnb_hosts", count("SELECT COUNT(*) FROM People WHERE source_host_id IS NOT NULL"),
               lst.host_id.nunique())
        expect("airbnb_hosts_are_landlords", count("SELECT COUNT(*) FROM People JOIN Landlord ON People_PeopleID = PeopleID "
                                                   "WHERE source_host_id IS NOT NULL"), lst.host_id.nunique())
        expect("airbnb_listings", count("SELECT COUNT(*) FROM Listing"), len(lst))
        expect("airbnb_listings_without_price", count("SELECT COUNT(*) FROM Listing WHERE price_per_night IS NULL"),
               int(lst.price.isna().sum()))
        expect("airbnb_listings_without_host", count("SELECT COUNT(*) FROM Listing WHERE Landlord_PeopleID IS NULL"),
               int(lst.host_id.isna().sum()))
        expect("airbnb_neighbourhoods", count("SELECT COUNT(*) FROM Neighbourhood"), lst.neighbourhood.nunique())
        expect("kaggle_addresses", count("SELECT COUNT(*) FROM address WHERE Postalcode IS NULL"), len(kaggle))
        expect("kaggle_houses", count("SELECT COUNT(*) FROM House WHERE lot_size_sqm IS NOT NULL"), len(kaggle))
        expect("kaggle_total_lot_size", count("SELECT IFNULL(SUM(lot_size_sqm), 0) FROM House"),
               int(kaggle.lot_size_sqm.sum()))
    finally:
        conn.close()

    print("All checks passed." if not failed else f"{len(failed)} check(s) FAILED: {', '.join(failed)}")
    return failed


if __name__ == "__main__":
    if not DB_PATH.exists():
        raise SystemExit("mock.db not found - run build_db.py first")
    sys.exit(1 if check() else 0)
