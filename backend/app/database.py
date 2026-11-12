
import sqlite3
from pathlib import Path


# Locate the main project directory
BASE_DIR = Path(__file__).resolve().parents[2]

# Database and schema locations
DATABASE_PATH = BASE_DIR / "database" / "yottaflex_risk.db"
SCHEMA_PATH = BASE_DIR / "database" / "schema.sql"


def get_connection():
    """Connect to the SQLite database."""

    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row

    connection.execute("PRAGMA foreign_keys = ON")

    return connection


def initialize_database():
    """Create database tables from schema.sql."""

    if not SCHEMA_PATH.exists():
        raise FileNotFoundError(
            f"Schema file not found: {SCHEMA_PATH}"
        )

    connection = get_connection()

    try:
        with open(SCHEMA_PATH, "r", encoding="utf-8") as file:
            schema = file.read()

        connection.executescript(schema)
        connection.commit()

        print("Database initialized successfully!")

    finally:
        connection.close()


if __name__ == "__main__":
    initialize_database()
