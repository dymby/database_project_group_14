import sqlite3
from pathlib import Path
 
# Path to the database file, resolved relative to THIS file's location —
# not relative to wherever Jupyter happens to be launched from.
# src/db.py -> ../database/mock.db
DB_PATH = Path(__file__).resolve().parent.parent / "database" / "mock.db"
 
 
def get_connection() -> sqlite3.Connection:
    """
    Returns a connection to the shared mock database.
 
    Caller is responsible for closing it (or use it in a `with` block).
    Raises a clear error if the DB file doesn't exist yet, instead of a
    cryptic sqlite3 failure later.
    """
    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"Database not found at {DB_PATH}.\n"
            f"If it's missing, rebuild it from schema.sql "
            f"and seed_data.sql."
        )
 
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # access columns by name: row["customer_id"]
    conn.execute("PRAGMA foreign_keys = ON")
    return conn
 
 
def run_query(sql: str, params: tuple = ()) -> list[dict]:

    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(sql, params)
        return [dict(row) for row in cur.fetchall()]
    finally:
        conn.close()
 
 
def execute(sql: str, params: tuple = ()) -> None:
    """
    Runs an INSERT/UPDATE/DELETE statement and commits.
    """
    conn = get_connection()
    try:
        conn.execute(sql, params)
        conn.commit()
    finally:
        conn.close()
 
 
if __name__ == "__main__":
    conn = get_connection()
    tables = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()
    conn.close()
    print(f"Connected to {DB_PATH}")
    print(f"Tables found: {[t['name'] for t in tables]}")
