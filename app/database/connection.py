"""SQLite connection helpers."""
from __future__ import annotations

import sqlite3
from pathlib import Path


def get_connection(db_path: str | Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        conn.execute("PRAGMA journal_mode = WAL;")
    except sqlite3.DatabaseError:
        pass
    try:
        # Don't fail instantly under rapid clicks: wait for the lock briefly.
        conn.execute("PRAGMA busy_timeout = 5000;")
    except sqlite3.DatabaseError:
        pass
    return conn
