"""DB helpers: existing words + seed neighborhood per (lang, pos)."""
from __future__ import annotations

import sqlite3


def load_db_words(conn: sqlite3.Connection) -> tuple[dict[tuple[str, str, str], int], dict[tuple[str, str], set[str]]]:
    """(existing (word, lang, pos) set, seed neighborhood per (lang, pos))."""
    existing: dict[tuple[str, str, str], int] = {}
    seeds: dict[tuple[str, str], set[str]] = {}
    for r in conn.execute("SELECT word, language, part_of_speech FROM words"):
        key = (r["word"].lower(), r["language"], r["part_of_speech"])
        existing[key] = 1
        seeds.setdefault((r["language"], r["part_of_speech"]), set()).add(r["word"].lower())
    return existing, seeds
