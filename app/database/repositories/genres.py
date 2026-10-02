"""Repository helpers — parameterized SQL, no GUI logic here."""
from __future__ import annotations

import sqlite3


def upsert_genre(conn: sqlite3.Connection, name: str, description: str = "", enabled: bool = True) -> int:
    name = name.strip()
    if not name:
        raise ValueError("Genre name must not be empty.")
    with conn:
        conn.execute("INSERT INTO genres(name, description, enabled) VALUES (?,?,?) ON CONFLICT(name) DO UPDATE SET description=excluded.description, enabled=excluded.enabled", (name, description, int(enabled)))
        return conn.execute("SELECT id FROM genres WHERE name = ?", (name,)).fetchone()["id"]


def update_genre(conn: sqlite3.Connection, genre_id: int, name: str, description: str = "", enabled: bool = True) -> None:
    name = name.strip()
    if not name:
        raise ValueError("Genre name must not be empty.")
    with conn:
        conn.execute("UPDATE genres SET name=?, description=?, enabled=? WHERE id=?",
                     (name, description, int(enabled), genre_id))


def delete_genre(conn: sqlite3.Connection, genre_id: int) -> None:
    with conn:
        conn.execute("DELETE FROM genres WHERE id = ?", (genre_id,))
