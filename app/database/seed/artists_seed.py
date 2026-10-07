"""Seed-artist migrations (never overwrite user edits)."""
from __future__ import annotations

import sqlite3

from app.database.seed_data.artists import ARTIST_META, ARTISTS


def ensure_artists(conn: sqlite3.Connection) -> int:
    """Add seed artists missing from an existing DB.

    INSERT OR IGNORE everywhere: never touches user edits or custom weights.
    Returns the number of newly added artists.
    """
    added = 0
    with conn:
        gids = {r["name"]: r["id"] for r in conn.execute("SELECT id, name FROM genres")}
        for artist, links in ARTISTS.items():
            cur = conn.execute("INSERT OR IGNORE INTO artists(name) VALUES (?)", (artist,))
            if cur.rowcount > 0:
                added += 1
            aid = conn.execute("SELECT id FROM artists WHERE name = ?", (artist,)).fetchone()["id"]
            for gname, w in links:
                if gname in gids:
                    conn.execute("INSERT OR IGNORE INTO artist_genres(artist_id, genre_id, weight) VALUES (?,?,?)",
                                 (aid, gids[gname], w))
    return added


def ensure_artist_meta(conn: sqlite3.Connection) -> int:
    """Fill missing region/language from ARTIST_META (never overwrites user edits)."""
    touched = 0
    with conn:
        for name, (region, language) in ARTIST_META.items():
            row = conn.execute("SELECT id, region, language FROM artists WHERE name = ?", (name,)).fetchone()
            if not row:
                continue
            if row["region"] is None and region is not None:
                conn.execute("UPDATE artists SET region = ? WHERE id = ?", (region, row["id"]))
                touched += 1
            if row["language"] is None:
                conn.execute("UPDATE artists SET language = ? WHERE id = ?", (language, row["id"]))
                touched += 1
    return touched
