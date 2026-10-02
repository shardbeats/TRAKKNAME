"""Shared test fixtures: in-memory DBs (schema-only or fully seeded)."""
from __future__ import annotations

import sqlite3

from app.database.schema import create_schema
from app.database.seed import seed_database


def memdb() -> sqlite3.Connection:
    """Fresh in-memory DB with full schema + seed data."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    create_schema(conn)
    seed_database(conn)
    return conn
