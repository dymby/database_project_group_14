"""
build_db.py — rebuilds mock.db from schema.sql + seed_data.sql.
 
We commit mock.db directly to the repo, so most people never need to run
this. It exists as a FALLBACK for two situations:
 
  1. mock.db gets corrupted or lost in a bad merge (binary files can't be
     merged by Git — see the repo README for why we accepted that tradeoff).
  2. You change schema.sql or seed_data.sql and need to regenerate the
     actual .db file to match before committing it.
 
Usage:
    cd database/
    python build_db.py
 
This OVERWRITES mock.db. If you have uncommitted data changes made by
hand (e.g. via a notebook), they will be lost. When in doubt, ask in the
team channel before running this.
"""
 
import sqlite3
from pathlib import Path
 
DB_DIR = Path(__file__).resolve().parent
DB_PATH = DB_DIR / "mock.db"
SCHEMA_PATH = DB_DIR / "schema.sql"
SEED_PATH = DB_DIR / "seed_data.sql"
 
 
def build():
    if DB_PATH.exists():
        confirm = input(f"{DB_PATH.name} already exists and will be OVERWRITTEN. Continue? [y/N] ")
        if confirm.strip().lower() != "y":
            print("Aborted.")
            return
        DB_PATH.unlink()
 
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.executescript(SCHEMA_PATH.read_text())
        conn.executescript(SEED_PATH.read_text())
        conn.commit()
        print(f"Built {DB_PATH} from {SCHEMA_PATH.name} + {SEED_PATH.name}")
    finally:
        conn.close()
 
 
if __name__ == "__main__":
    build()
