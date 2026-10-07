"""Stage 1: resolve genre, artists, related genres, mood/artist boosts."""
from __future__ import annotations

import random
import sqlite3

from app.database.repositories import moods as moods_repo
from app.generator.artists import select_artists
from app.generator.results import GenContext
from app.models.enums import LEGACY_POOL_MAP


def related_ids(conn: sqlite3.Connection, genre_id: int) -> list[int]:
    rows = conn.execute(
        "SELECT related_genre_id FROM genre_relations WHERE genre_id = ?", (genre_id,)
    ).fetchall()
    return [r["related_genre_id"] for r in rows]


def resolve_moods(conn: sqlite3.Connection, moods: list[str] | None) -> tuple[list[str], dict[int, float]]:
    requested = [m.strip() for m in (moods or []) if m and m.strip()][:2]
    mood_ids = moods_repo.mood_ids_for_names(conn, requested)
    names: list[str] = []
    if mood_ids:
        rows = conn.execute(
            f"SELECT name FROM moods WHERE id IN ({','.join('?' * len(mood_ids))})", mood_ids
        ).fetchall()
        names = [r["name"] for r in rows]
    return names, moods_repo.mood_word_weights(conn, mood_ids) if mood_ids else {}


def resolve_artist_boost(conn: sqlite3.Connection, artists: list[str],
                         genre_id: int | None, artist_influence: float) -> dict[int, float]:
    """Words linked to the artists' *other* genres get a mild boost."""
    boost: dict[int, float] = {}
    if not (artists and artist_influence > 0 and genre_id):
        return boost
    for aname in artists:
        aid = conn.execute("SELECT id FROM artists WHERE name = ?", (aname,)).fetchone()
        if not aid:
            continue
        others = conn.execute(
            "SELECT genre_id FROM artist_genres WHERE artist_id = ? AND genre_id != ?",
            (aid["id"], genre_id),
        ).fetchall()
        if not others:
            continue
        ph = ",".join("?" * len(others))
        factor = 1.0 + float(artist_influence) * 0.5
        for wr_ in conn.execute(
            f"SELECT word_id FROM word_genres WHERE genre_id IN ({ph})",
            [r["genre_id"] for r in others],
        ):
            boost[wr_["word_id"]] = factor
    return boost


def resolve_context(conn: sqlite3.Connection, genre_name: str | None, language: str,
                    artist_count: int, artist_influence: float,
                    moods: list[str] | None, artist_pool: str | None,
                    rng: random.Random) -> GenContext:
    """Resolve genre, artists, related genres, mood/artist boosts."""
    language = language if language in ("en", "es") else "en"
    grow = conn.execute("SELECT id, name FROM genres WHERE name = ?", (genre_name,)).fetchone() if genre_name else None
    if genre_name and not grow:
        grow = conn.execute("SELECT id, name FROM genres WHERE enabled = 1 ORDER BY name LIMIT 1").fetchone()
    genre_id = grow["id"] if grow else None
    genre_label = grow["name"] if grow else (genre_name or "Unknown")

    pool = LEGACY_POOL_MAP.get(artist_pool, artist_pool) if artist_pool else None
    artists = select_artists(conn, genre_id, artist_count, rng, pool)
    related = related_ids(conn, genre_id) if genre_id else []
    mood_names, mood_boost = resolve_moods(conn, moods)
    artist_boost = resolve_artist_boost(conn, artists, genre_id, artist_influence)
    return GenContext(genre_id, genre_label, language, artists, related,
                      mood_names, mood_boost, artist_boost, pool)


# Backwards-compat aliases for the old private helpers.
_related_ids = related_ids
_resolve_moods = resolve_moods
_resolve_artist_boost = resolve_artist_boost
