"""Runs every query in queries.sql (split on '-- Q' headers) and prints row counts + first rows."""
import sqlite3
import re
from pathlib import Path

DB = Path(__file__).resolve().parent / "mock.db"
text = (Path(__file__).resolve().parent / "queries.sql").read_text()
blocks = re.split(r"(?m)^(?=-- Q\d+[: ])", text)[1:]
conn = sqlite3.connect(DB)
conn.execute("PRAGMA foreign_keys = ON")
for b in blocks:
    title = b.splitlines()[0]
    rows = conn.execute(b).fetchall()
    print(f"\n{title}\n  -> {len(rows)} rows")
    for r in rows[:5]:
        print("    ", r)
