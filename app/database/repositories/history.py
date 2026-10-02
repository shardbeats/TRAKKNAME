from __future__ import annotations

import json
import sqlite3
from datetime import datetime


def save_history(conn: sqlite3.Connection, title: str, genre_id: int | None, language: str, artists: list[str], pattern: str, moods: list[str] | None = None, artist_pool: str = "all") -> int:
    with conn:
        try:
            has_pool = any(r["name"] == "artist_pool" for r in conn.execute("PRAGMA table_info(generation_history)"))
        except Exception:
            has_pool = False
        if has_pool:
            cur = conn.execute(
                "INSERT INTO generation_history(title, genre_id, language, artists_json, pattern, created_at, moods_json, artist_pool) VALUES (?,?,?,?,?,?,?,?)",
                (title, genre_id, language, json.dumps(artists, ensure_ascii=False), pattern, datetime.now().isoformat(timespec="seconds"), json.dumps(moods or [], ensure_ascii=False), artist_pool))
        else:
            cur = conn.execute(
                "INSERT INTO generation_history(title, genre_id, language, artists_json, pattern, created_at, moods_json) VALUES (?,?,?,?,?,?,?)",
                (title, genre_id, language, json.dumps(artists, ensure_ascii=False), pattern, datetime.now().isoformat(timespec="seconds"), json.dumps(moods or [], ensure_ascii=False)))
        return cur.lastrowid


def recent_titles(conn: sqlite3.Connection, limit: int = 100) -> set[str]:
    from app.utils.text import normalize_title
    rows = conn.execute("SELECT title FROM generation_history ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    return {normalize_title(r["title"]) for r in rows}


def list_history(conn: sqlite3.Connection, limit: int = 300, search: str = ""):
    if search:
        return conn.execute(
            """SELECT h.*, g.name AS genre_name FROM generation_history h
               LEFT JOIN genres g ON g.id = h.genre_id
               WHERE h.title LIKE ? ORDER BY h.id DESC LIMIT ?""", (f"%{search}%", limit)).fetchall()
    return conn.execute(
        """SELECT h.*, g.name AS genre_name FROM generation_history h
           LEFT JOIN genres g ON g.id = h.genre_id ORDER BY h.id DESC LIMIT ?""", (limit,)).fetchall()


def delete_history(conn: sqlite3.Connection, hid: int) -> None:
    with conn:
        conn.execute("DELETE FROM generation_history WHERE id = ?", (hid,))


def clear_history(conn: sqlite3.Connection) -> None:
    with conn:
        conn.execute("DELETE FROM generation_history")
