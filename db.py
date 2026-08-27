import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATABASE_FILE = BASE_DIR / "cm01.db"
SCHEMA_FILE = BASE_DIR / "schema.sql"

def get_connection():
    connection = sqlite3.connect(DATABASE_FILE)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection

def init_database():
    DATABASE_FILE.parent.mkdir(parents=True, exist_ok=True)

    with get_connection() as connection:
        if SCHEMA_FILE.exists():
            connection.executescript(
                SCHEMA_FILE.read_text(encoding="utf-8")
            )