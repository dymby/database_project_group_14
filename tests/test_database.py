"""Run with:  python -m unittest discover tests"""
import contextlib
import io
import shutil
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

DB_DIR = Path(__file__).resolve().parent.parent / "database"
sys.path.insert(0, str(DB_DIR))

import build_db
import check_db
import export_real_data
import load_data
import run_queries

EXPECTED_ROWS = {"City": 1075, "Postcode": 35, "address": 5998, "People": 9114, "Renter": 5, "Landlord": 9109,
                 "Contract": 6, "House": 5950, "Neighbourhood": 22, "Listing": 10465}


def quiet(function, *args):
    with contextlib.redirect_stdout(io.StringIO()):
        return function(*args)


def dump(conn):
    # coordinates lose their last digit when SQLite reads them back from text
    return {t: [tuple(round(v, 9) if isinstance(v, float) else v for v in row)
                for row in conn.execute(f"SELECT * FROM [{t}] ORDER BY 1")] for t in check_db.TABLES}


class DatabaseTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp())
        cls.built = cls.tmp / "built.db"
        quiet(build_db.build, cls.built, True)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp)

    def setUp(self):
        self.db = self.tmp / "work.db"
        shutil.copy(self.built, self.db)
        self.conn = sqlite3.connect(self.db)
        self.conn.execute("PRAGMA foreign_keys = ON")

    def tearDown(self):
        self.conn.close()

    def count(self, sql, *params):
        return self.conn.execute(sql, params).fetchone()[0]

    def rejects(self, sql, *params):
        with self.assertRaises(sqlite3.IntegrityError):
            self.conn.execute(sql, params)


class BuildTest(DatabaseTest):
    def test_row_counts(self):
        for table, expected in EXPECTED_ROWS.items():
            self.assertEqual(self.count(f"SELECT COUNT(*) FROM [{table}]"), expected, table)

    def test_check_db_passes(self):
        self.assertEqual(quiet(check_db.check, self.db), [])

    def test_check_db_finds_orphans(self):
        self.conn.execute("PRAGMA foreign_keys = OFF")
        self.conn.execute("DELETE FROM address WHERE addressID = 1")
        self.conn.commit()
        self.assertIn("foreign_key_violations", quiet(check_db.check, self.db))

    def test_loading_twice_is_refused(self):
        with self.assertRaises(SystemExit):
            quiet(load_data.load_all, self.db)
        for table, expected in EXPECTED_ROWS.items():
            self.assertEqual(self.count(f"SELECT COUNT(*) FROM [{table}]"), expected, table)

    def test_failed_build_keeps_old_database(self):
        raw = load_data.RAW
        load_data.RAW = self.tmp / "missing"
        try:
            with self.assertRaises(FileNotFoundError):
                quiet(build_db.build, self.db, True)
        finally:
            load_data.RAW = raw
        self.assertEqual(self.count("SELECT COUNT(*) FROM Listing"), EXPECTED_ROWS["Listing"])
        self.assertFalse((self.tmp / "work.db.tmp").exists())

    def test_real_data_sql_gives_the_same_database(self):
        out = self.tmp / "real_data.sql"
        quiet(export_real_data.export, self.db, out)
        replay = sqlite3.connect(":memory:")
        self.addCleanup(replay.close)
        replay.executescript(build_db.SCHEMA_PATH.read_text(encoding="utf-8"))
        replay.executescript(build_db.SEED_PATH.read_text(encoding="utf-8"))
        replay.executescript(out.read_text(encoding="utf-8"))
        self.assertEqual(dump(replay), dump(self.conn))

    def test_queries_run(self):
        blocks = run_queries.read_queries()
        self.assertEqual(len(blocks), 9)
        for block in blocks:
            rows = self.conn.execute(block).fetchall()
            if not block.startswith("-- Q4"):
                self.assertGreater(len(rows), 0, block.splitlines()[0])

    def test_address_full_covers_every_address(self):
        self.assertEqual(self.count("SELECT COUNT(*) FROM address_full WHERE Street IS NOT NULL AND City_CityID IS NOT NULL"),
                         EXPECTED_ROWS["address"])


class CleaningTest(unittest.TestCase):
    def test_lot_size(self):
        self.assertEqual(load_data.parse_lot_size("251 m²"), 251)
        self.assertEqual(load_data.parse_lot_size("5.440 m²"), 5440)
        self.assertEqual(load_data.parse_lot_size("120.615 m²"), 120615)

    def test_split_address(self):
        cases = {
            "Bovenweg 223": ("Bovenweg", 223, None, None),
            "Dorpsstraat 12 a": ("Dorpsstraat", 12, "A", None),
            "3e Kekerstraat 59": ("3e Kekerstraat", 59, None, None),
            "17 Septemberstraat 4": ("17 Septemberstraat", 4, None, None),
            "Maastrichterweg 62 64": ("Maastrichterweg", 62, None, "64"),
            "Boschweg 75 + 75a": ("Boschweg", 75, None, "+ 75a"),
            "Zonder Nummer": ("Zonder Nummer", None, None, None),
        }
        for address, expected in cases.items():
            self.assertEqual(load_data.split_address(address), expected, address)

    def test_bag_postcode_format(self):
        addr, _ = quiet(load_data.clean_bag)
        self.assertTrue(addr.postcode.str.fullmatch(r"\d{4} [A-Z]{2}").all())


class ConstraintTest(DatabaseTest):
    def test_postcode_format(self):
        self.rejects("INSERT INTO Postcode VALUES ('1015NR', 'Straat', 2)")

    def test_house_size(self):
        self.conn.execute("INSERT INTO address (Postalcode, Number) VALUES ('1012 AB', 500)")
        new = self.count("SELECT MAX(addressID) FROM address")
        self.rejects("INSERT INTO House (address_addressID, size_sqm) VALUES (?, 1)", new)
        self.rejects("INSERT INTO House (address_addressID, size_sqm) VALUES (?, 1205)", new)
        self.rejects("INSERT INTO House (address_addressID) VALUES (?)", new)
        self.rejects("INSERT INTO House (address_addressID, lot_size_sqm) VALUES (?, x'01')", new)

    def test_number_must_be_integer(self):
        self.rejects("INSERT INTO address (Postalcode, Number) VALUES ('1012 AB', x'01')")

    def test_age(self):
        self.rejects("INSERT INTO People (First_Name, Age) VALUES ('X', 130)")

    def test_contract_dates(self):
        self.rejects("INSERT INTO Contract (amount, start_date, expiration_date) VALUES (900, '2026-01-01', '2025-01-01')")

    def test_duplicate_city(self):
        self.rejects("INSERT INTO City (Name) VALUES ('Amsterdam')")

    def test_duplicate_host(self):
        host = self.count("SELECT source_host_id FROM People WHERE source_host_id IS NOT NULL LIMIT 1")
        self.rejects("INSERT INTO People (source_host_id) VALUES (?)", host)

    def test_duplicate_address(self):
        self.rejects("INSERT INTO address (Postalcode, Number) VALUES ('5611 AB', 12)")
        street, city, number = self.conn.execute(
            "SELECT Street, City_CityID, Number FROM address WHERE Postalcode IS NULL AND Letter IS NULL "
            "AND Addition IS NULL LIMIT 1").fetchone()
        self.rejects("INSERT INTO address (Street, City_CityID, Number) VALUES (?, ?, ?)", street, city, number)

    def test_address_needs_postcode_or_street(self):
        self.rejects("INSERT INTO address (Number) VALUES (1)")
        self.rejects("INSERT INTO address (Postalcode, Street, City_CityID, Number) VALUES ('1012 AB', 'Straat', 2, 1)")

    def test_room_type(self):
        self.rejects("INSERT INTO Listing (ListingID, Neighbourhood_NeighbourhoodID, room_type) VALUES (1, 1, 'Tent')")


class DeleteTest(DatabaseTest):
    def test_delete_person_keeps_listings(self):
        person, listings = self.conn.execute(
            "SELECT Landlord_PeopleID, COUNT(*) FROM Listing WHERE Landlord_PeopleID IS NOT NULL "
            "GROUP BY 1 ORDER BY 2 DESC LIMIT 1").fetchone()
        self.conn.execute("DELETE FROM People WHERE PeopleID = ?", (person,))
        self.assertEqual(self.count("SELECT COUNT(*) FROM Landlord WHERE People_PeopleID = ?", person), 0)
        self.assertEqual(self.count("SELECT COUNT(*) FROM Listing"), EXPECTED_ROWS["Listing"])
        self.assertEqual(self.count("SELECT COUNT(*) FROM Listing WHERE Landlord_PeopleID IS NULL"), 96 + listings)

    def test_delete_renter_person(self):
        self.conn.execute("DELETE FROM People WHERE PeopleID = 1")
        self.assertEqual(self.count("SELECT COUNT(*) FROM Renter"), 4)

    def test_delete_contract_keeps_houses(self):
        self.conn.execute("DELETE FROM Contract WHERE contractID = 1")
        self.assertEqual(self.count("SELECT COUNT(*) FROM House"), EXPECTED_ROWS["House"])
        self.assertEqual(self.count("SELECT COUNT(*) FROM House WHERE address_addressID IN (1, 7) "
                                    "AND contract_contractID IS NULL"), 2)

    def test_delete_address_with_house_is_refused(self):
        self.rejects("DELETE FROM address WHERE addressID = 1")

    def test_delete_address_keeps_residents(self):
        self.conn.execute("DELETE FROM House WHERE address_addressID = 1")
        self.conn.execute("DELETE FROM address WHERE addressID = 1")
        self.assertEqual(self.count("SELECT COUNT(*) FROM People WHERE PeopleID = 1 AND address_addressID IS NULL"), 1)

    def test_delete_referenced_rows_is_refused(self):
        self.rejects("DELETE FROM City WHERE Name = 'Amsterdam'")
        self.rejects("DELETE FROM City WHERE Name = 'Sint Pancras'")
        self.rejects("DELETE FROM Postcode WHERE Postalcode = '5611 AB'")
        self.rejects("DELETE FROM Neighbourhood WHERE NeighbourhoodID = 1")

    def test_rename_postcode_follows(self):
        self.conn.execute("UPDATE Postcode SET Postalcode = '5611 ZZ' WHERE Postalcode = '5611 AB'")
        self.assertEqual(self.count("SELECT Postalcode FROM address WHERE addressID = 1"), "5611 ZZ")


if __name__ == "__main__":
    unittest.main()
