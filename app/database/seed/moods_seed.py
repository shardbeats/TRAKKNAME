"""Mood seed (idempotent: safe on fresh and existing databases)."""
from __future__ import annotations

import sqlite3

from app.database.seed_data.moods import MOOD_VIBES, MOODS


def seed_moods(conn: sqlite3.Connection) -> None:
    """Idempotent: safe to run on fresh and existing databases."""
    with conn:
        for name, desc, icon in MOODS:
            conn.execute("INSERT OR IGNORE INTO moods(name, description, icon) VALUES (?, ?, ?)", (name, desc, icon))
        # Retire legacy icon glyphs (text-only UI; custom user icons untouched).
        conn.execute("UPDATE moods SET icon = '' WHERE icon IN ('◼','☂','⚡','■','☁','◆','♪','☀','♫','●','○','♥','♦','☾','☆','★','▲','✦','♠','◇')")
        index: dict[tuple[str, str], int] = {}
        for r in conn.execute("SELECT id, word, language FROM words"):
            index[(r["language"], r["word"].lower())] = r["id"]
        for mname, vibes in MOOD_VIBES.items():
            row = conn.execute("SELECT id FROM moods WHERE name = ?", (mname,)).fetchone()
            if not row:
                continue
            mid = row["id"]
            for lang in ("en", "es"):
                for v in vibes:
                    wid = index.get((lang, v.lower()))
                    if wid:
                        conn.execute("INSERT OR REPLACE INTO word_moods(word_id, mood_id, weight) VALUES (?,?,?)", (wid, mid, 1.0))
