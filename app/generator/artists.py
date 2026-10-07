"""Weighted artist selection (genre + pool predicate)."""
from __future__ import annotations

import random
import sqlite3

from app.generator import weighted_random as wr
from app.models.enums import LEGACY_POOL_MAP


def select_artists(conn: sqlite3.Connection, genre_id: int | None, count: int,
                   rng: random.Random, pool: str | None = None) -> list[str]:
    if not genre_id or count <= 0:
        return []
    pool = LEGACY_POOL_MAP.get(pool, pool) if pool else None
    q = """SELECT a.id, a.name, ag.weight FROM artists a
           JOIN artist_genres ag ON ag.artist_id = a.id
           WHERE ag.genre_id = ? AND a.enabled = 1"""
    args: list = [genre_id]
    if pool == "es":
        q += " AND a.language = 'es'"
    elif pool == "en":
        q += " AND COALESCE(a.language, 'en') = 'en'"
    q += " ORDER BY ag.weight DESC"
    rows = conn.execute(q, args).fetchall()
    if not rows:
        return []
    names = [r["name"] for r in rows]
    weights = [max(float(r["weight"]), 0.0) for r in rows]
    return wr.sample_weighted_unique(names, weights, min(count, len(names)), rng)
