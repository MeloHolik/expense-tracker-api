import sqlite3

SCHEMA = """
        CREATE TABLE IF NOT EXISTS expenses(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            category VARCHAR(15) NOT NULL,
            amount REAL NOT NULL,
            comment VARCHAR(50) 
        );
    """


def init_db(db_path: str) -> None:
    conn = sqlite3.connect(db_path)
    try:
        conn.execute(SCHEMA)
        conn.commit()
    finally:
        conn.close()
