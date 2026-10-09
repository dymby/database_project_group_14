"""
build_db.py — rebuilds mock.db from schema.sql + seed_data.sql + the real data in data/raw/.
 
We commit mock.db directly to the repo, so most people never need to run
this. It exists as a FALLBACK for two situations:
 
  1. mock.db gets corrupted or lost in a bad merge (binary files can't be
     merged by Git — see the repo README for why we accepted that tradeoff).
  2. You change schema.sql, seed_data.sql or load_data.py and need to
     regenerate the actual .db file to match before committing it.
 
Usage:
    python database/build_db.py          # asks before overwriting
    python database/build_db.py --yes    # no question asked
 
This OVERWRITES mock.db. If you have uncommitted data changes made by
hand (e.g. via a notebook), they will be lost. When in doubt, ask in the
team channel before running this. A failed build leaves mock.db untouched.
"""
 
import os
import sqlite3
import sys
from pathlib import Path
 
import check_db
import load_data
 
DB_DIR = Path(__file__).resolve().parent
DB_PATH = DB_DIR / "mock.db"
SCHEMA_PATH = DB_DIR / "schema.sql"
SEED_PATH = DB_DIR / "seed_data.sql"
 
 
def build(db_path=DB_PATH, yes=False):
    db_path = Path(db_path)
    if db_path.exists() and not yes:
        confirm = input(f"{db_path.name} already exists and will be OVERWRITTEN. Continue? [y/N] ")
        if confirm.strip().lower() != "y":
            print("Aborted.")
            return
 
    # build in a temporary file and swap it in only if the checks pass
    tmp_path = db_path.with_name(db_path.name + ".tmp")
    tmp_path.unlink(missing_ok=True)
    try:
        conn = sqlite3.connect(tmp_path)
        try:
            conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
            conn.executescript(SEED_PATH.read_text(encoding="utf-8"))
            conn.commit()
        finally:
            conn.close()
        load_data.load_all(tmp_path)
        if check_db.check(tmp_path):
            raise SystemExit(f"Build failed the checks - {db_path.name} was left untouched.")
        os.replace(tmp_path, db_path)
    finally:
        tmp_path.unlink(missing_ok=True)
    print(f"Built {db_path} from {SCHEMA_PATH.name} + {SEED_PATH.name} + data/raw/")
 
 
if __name__ == "__main__":
    build(yes="--yes" in sys.argv[1:])
