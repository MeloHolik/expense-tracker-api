import sqlite3
from typing import Generator

DB_PATH = "expenses.db"


def get_connection() -> Generator[sqlite3.Connection, None, None]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = (
        sqlite3.Row
    )  # чтобы результаты SELECT были "словари-подобные": row["category"], а не только
    # tuple row[0]
    try:
        yield conn
    finally:
        conn.close()
