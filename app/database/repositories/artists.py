from __future__ import annotations

import sqlite3


def save_artist(conn: sqlite3.Connection, name: str, genre_weights: dict[int, float], enabled: bool = True, artist_id: int | None = None, region: str | None = None, language: str | None = None) -> int:
    name = name.strip()
    if not name:
        raise ValueError("Artist name must not be empty.")
    for w in genre_weights.values():
        if w < 0:
            raise ValueError("Weights must be >= 0.")
    with conn:
        if artist_id is None:
            cur = conn.execute("INSERT INTO artists(name, enabled, region, language) VALUES (?,?,?,?) ON CONFLICT(name) DO UPDATE SET enabled=excluded.enabled, region=excluded.region, language=excluded.language", (name, int(enabled), region, language))
            aid = conn.execute("SELECT id FROM artists WHERE name = ?", (name,)).fetchone()["id"]
        else:
            conn.execute("UPDATE artists SET name = ?, enabled = ?, region = ?, language = ? WHERE id = ?", (name, int(enabled), region, language, artist_id))
            aid = artist_id
            conn.execute("DELETE FROM artist_genres WHERE artist_id = ?", (aid,))
        for gid, w in genre_weights.items():
            if w > 0:
                conn.execute("INSERT OR REPLACE INTO artist_genres(artist_id, genre_id, weight) VALUES (?,?,?)", (aid, gid, float(w)))
        return aid


def delete_artist(conn: sqlite3.Connection, artist_id: int) -> None:
    with conn:
        conn.execute("DELETE FROM artists WHERE id = ?", (artist_id,))
