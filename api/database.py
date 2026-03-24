"""Database connection management."""

import sqlite3
from contextlib import contextmanager
from pathlib import Path

_db_path: str | None = None


def set_db_path(path: str):
    global _db_path
    _db_path = str(path)


def get_connection() -> sqlite3.Connection:
    if _db_path is None:
        raise RuntimeError("Database path not set. Call set_db_path() first.")
    conn = sqlite3.connect(_db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


@contextmanager
def get_db():
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()
