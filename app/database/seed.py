"""Seed orchestration: schema fill + idempotent ensure_* migrations.

Raw data lives in app/database/seed_data/ (edit lists there, not here).
Re-exports below keep backwards compatibility for tests and callers.
"""
from __future__ import annotations

import sqlite3

from app.database.seed_data.artists import ARTIST_META, ARTISTS
from app.database.seed_data.genres import GENRE_RELATIONS, GENRE_VIBES, GENRES
from app.database.seed_data.moods import MOOD_VIBES, MOODS
from app.database.seed_data.patterns import (
    PATTERNS,
    REMOVED_PATTERNS,
    RETIRED_PATTERNS,
    STYLE_RENAMES,
)
from app.database.seed_data.vocabulary import (
    EN_ADJECTIVES,
    EN_NOUNS,
    EN_VERBS,
    ES_ADJECTIVES,
    ES_NOUNS_RAW,
    ES_VERBS,
)

__all__ = [
    "SCHEMA_VERSION",
    "GENRES", "GENRE_RELATIONS", "GENRE_VIBES",
    "ARTISTS", "ARTIST_META",
    "EN_VERBS", "EN_ADJECTIVES", "EN_NOUNS",
    "ES_VERBS", "ES_ADJECTIVES", "ES_NOUNS_RAW",
    "MOODS", "MOOD_VIBES",
    "PATTERNS", "RETIRED_PATTERNS", "REMOVED_PATTERNS", "STYLE_RENAMES",
    "seed_database", "seed_moods", "ensure_artists", "ensure_artist_meta",
    "ensure_patterns",
]

SCHEMA_VERSION = "1"


def ensure_patterns(conn: sqlite3.Connection) -> None:
    """Insert missing curated patterns; disable retired ones; delete removed ones. Idempotent."""
    with conn:
        for old, new in STYLE_RENAMES.items():
            conn.execute("UPDATE patterns SET name = ? WHERE name = ?", (new, old))
        for name, lang, template, weight in PATTERNS:
            row = conn.execute("SELECT id FROM patterns WHERE name = ?", (name,)).fetchone()
            if not row:
                conn.execute("INSERT INTO patterns(name, language, template, weight, enabled) VALUES (?,?,?,?,1)",
                             (name, lang, template, weight))
        for name in RETIRED_PATTERNS:
            conn.execute("UPDATE patterns SET enabled = 0 WHERE name = ?", (name,))
        for name in REMOVED_PATTERNS:
            conn.execute("DELETE FROM patterns WHERE name = ?", (name,))


def seed_database(conn: sqlite3.Connection) -> None:
    from .schema import get_meta, set_meta
    if get_meta(conn, "schema_version") == SCHEMA_VERSION and conn.execute("SELECT COUNT(*) c FROM genres").fetchone()["c"]:
        return
    with conn:
        gids: dict[str, int] = {}
        for name, desc in GENRES:
            conn.execute("INSERT OR IGNORE INTO genres(name, description) VALUES (?, ?)", (name, desc))
            row = conn.execute("SELECT id FROM genres WHERE name = ?", (name,)).fetchone()
            gids[name] = row["id"]
        for artist, links in ARTISTS.items():
            conn.execute("INSERT OR IGNORE INTO artists(name) VALUES (?)", (artist,))
            aid = conn.execute("SELECT id FROM artists WHERE name = ?", (artist,)).fetchone()["id"]
            for gname, w in links:
                if gname in gids:
                    conn.execute("INSERT OR REPLACE INTO artist_genres(artist_id, genre_id, weight) VALUES (?,?,?)", (aid, gids[gname], w))
        for gname, rname, w in GENRE_RELATIONS:
            if gname in gids and rname in gids:
                conn.execute("INSERT OR REPLACE INTO genre_relations(genre_id, related_genre_id, weight) VALUES (?,?,?)", (gids[gname], gids[rname], w))
        # words
        def add_word(word, lang, pos, gender=None, number=None):
            cur = conn.execute(
                "INSERT INTO words(word, language, part_of_speech, weight, enabled, gender, number) VALUES (?,?,?,?,?,?,?)",
                (word, lang, pos, 1.0, 1, gender, number))
            return cur.lastrowid
        word_index: dict[tuple[str, str], int] = {}
        for v in EN_VERBS:
            word_index[("en", v.lower())] = add_word(v.lower(), "en", "verb")
        for a in EN_ADJECTIVES:
            word_index[("en", a.lower())] = add_word(a.lower(), "en", "adjective")
        for n in EN_NOUNS:
            word_index[("en", n.lower())] = add_word(n.lower(), "en", "noun")
        for v in ES_VERBS:
            word_index[("es", v.lower())] = add_word(v.lower(), "es", "verb")
        for a in ES_ADJECTIVES:
            word_index[("es", a.lower())] = add_word(a.lower(), "es", "adjective")
        for w, g, n_ in ES_NOUNS_RAW:
            word_index[("es", w.lower())] = add_word(w.lower(), "es", "noun", g, n_)
        # genre vibes -> word_genres
        for gname, vibes in GENRE_VIBES.items():
            gid = gids.get(gname)
            if not gid:
                continue
            for lang in ("en", "es"):
                for v in vibes:
                    wid = word_index.get((lang, v.lower()))
                    if wid:
                        conn.execute("INSERT OR REPLACE INTO word_genres(word_id, genre_id, weight) VALUES (?,?,?)", (wid, gid, 3.0))
        for name, lang, template, weight in PATTERNS:
            conn.execute("INSERT INTO patterns(name, language, template, weight) VALUES (?,?,?,?)", (name, lang, template, weight))
        set_meta(conn, "schema_version", SCHEMA_VERSION)
    seed_moods(conn)
    ensure_artist_meta(conn)


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


def ensure_no_placeholders(conn: sqlite3.Connection) -> int:
    """Delete legacy seed placeholders (versoNNN, sombraNNN) from dirty DBs.

    Safe: no legitimate word in our dataset contains a digit.
    Cascades to word_genres/word_moods via FK. Idempotent.
    """
    with conn:
        cur = conn.execute("DELETE FROM words WHERE word GLOB '*[0-9]*'")
        return cur.rowcount


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
