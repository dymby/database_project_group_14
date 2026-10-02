"""Runs every query in queries.sql (split on '-- Q' headers) and prints row counts + first rows."""
import sqlite3
import re
from pathlib import Path

DB = Path(__file__).resolve().parent / "mock.db"
QUERIES = Path(__file__).resolve().parent / "queries.sql"


def read_queries():
    blocks = re.split(r"(?m)^(?=-- Q\d+[: ])", QUERIES.read_text(encoding="utf-8"))[1:]
    if not blocks:
        raise SystemExit("no '-- Q1: ...' headers found in queries.sql")
    return blocks


def run(db_path=DB):
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    for b in read_queries():
        title = b.splitlines()[0]
        rows = conn.execute(b).fetchall()
        print(f"\n{title}\n  -> {len(rows)} rows")
        for r in rows[:5]:
            print("    ", r)
    conn.close()


if __name__ == "__main__":
    run()
