"""Writes the real-world rows of mock.db to real_data.sql as plain INSERT statements."""
import sqlite3
from pathlib import Path

DB_DIR = Path(__file__).resolve().parent
DB_PATH = DB_DIR / "mock.db"
OUT_PATH = DB_DIR / "real_data.sql"

BAG = "bag_address_id IS NOT NULL"
KAGGLE = "Postalcode IS NULL"
HOST = "source_host_id IS NOT NULL"

EXPORTS = [
    ("City", "INSERT OR IGNORE", "CityID, Name",
     f"WHERE CityID IN (SELECT City_CityID FROM Postcode WHERE Postalcode IN (SELECT Postalcode FROM address WHERE {BAG}))"),
    ("Postcode", "INSERT", "Postalcode, Street, City_CityID",
     f"WHERE Postalcode IN (SELECT Postalcode FROM address WHERE {BAG})"),
    ("address", "INSERT", "addressID, Postalcode, Number, Letter, Addition, bag_address_id", f"WHERE {BAG}"),
    ("House", "INSERT", "address_addressID, size_sqm, contract_contractID",
     f"WHERE address_addressID IN (SELECT addressID FROM address WHERE {BAG})"),
    ("People", "INSERT", "PeopleID, First_Name, Last_Name, Age, address_addressID, source_host_id", f"WHERE {HOST}"),
    ("Landlord", "INSERT", "People_PeopleID", f"WHERE People_PeopleID IN (SELECT PeopleID FROM People WHERE {HOST})"),
    ("Neighbourhood", "INSERT", "NeighbourhoodID, Name, City_CityID", ""),
    ("Listing", "INSERT", "ListingID, Name, Landlord_PeopleID, Neighbourhood_NeighbourhoodID, room_type, "
     "price_per_night, minimum_nights, latitude, longitude, last_review", ""),
    ("City", "INSERT OR IGNORE", "CityID, Name", f"WHERE CityID IN (SELECT City_CityID FROM address WHERE {KAGGLE})"),
    ("address", "INSERT", "addressID, Street, City_CityID, Number, Letter, Addition", f"WHERE {KAGGLE}"),
    ("House", "INSERT", "address_addressID, lot_size_sqm",
     f"WHERE address_addressID IN (SELECT addressID FROM address WHERE {KAGGLE})"),
]

HEADER = """\
-- real_data.sql - the real-world data as plain INSERT statements.
--
-- GENERATED FILE. Produced by database/export_real_data.py from mock.db, after
-- database/load_data.py has cleaned and loaded the two source datasets.
-- Do not edit by hand: change the cleaning in load_data.py and re-export.
--
-- Why this file exists: the cleaning (reformatting postcodes, joining the three
-- BAG files, dropping outliers, type casting) is done in Python because SQL
-- cannot read or reshape CSV files. This file is the SQL *result* of that work,
-- so the inserted data can be read, reviewed and replayed without pandas.
--
-- Contains ONLY rows originating from the real datasets; the week 3/4 mock rows
-- live in seed_data.sql. Load order matters (foreign keys).
--
-- Usage, real data only:
--     sqlite3 fresh.db < database/schema.sql
--     sqlite3 fresh.db < database/real_data.sql
--
-- Usage, mock data as well (same result as build_db.py):
--     sqlite3 fresh.db < database/schema.sql
--     sqlite3 fresh.db < database/seed_data.sql
--     sqlite3 fresh.db < database/real_data.sql
--
-- Sources: Inside Airbnb Amsterdam (CC BY 4.0, compiled 2026-06-15);
--          Amsterdam BAG (CC0 1.0). Full details in docs/data_sources.md.

PRAGMA foreign_keys = ON;
BEGIN TRANSACTION;

"""


def literal(value):
    if value is None:
        return "NULL"
    if isinstance(value, str):
        return "'" + value.replace("'", "''") + "'"
    return repr(value)


def export(db_path=DB_PATH, out_path=OUT_PATH):
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    parts = [HEADER]
    for table, verb, cols, where in EXPORTS:
        rows = conn.execute(f"SELECT {cols} FROM [{table}] {where} ORDER BY 1").fetchall()
        values = ",\n".join("    (" + ", ".join(literal(v) for v in r) + ")" for r in rows)
        parts.append(f"\n-- {table}: {len(rows)} row(s)\n{verb} INTO {table} ({cols}) VALUES\n{values};\n")
    parts.append("\nCOMMIT;\n")
    conn.close()
    Path(out_path).write_text("".join(parts), encoding="utf-8")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    export()
