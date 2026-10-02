"""Normalized schema for the beat-name vocabulary engine."""
from __future__ import annotations

import sqlite3

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS genres (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT DEFAULT '',
    enabled INTEGER NOT NULL DEFAULT 1
);
CREATE TABLE IF NOT EXISTS artists (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    enabled INTEGER NOT NULL DEFAULT 1,
    region TEXT,
    language TEXT
);
CREATE TABLE IF NOT EXISTS artist_genres (
    artist_id INTEGER NOT NULL,
    genre_id INTEGER NOT NULL,
    weight REAL NOT NULL DEFAULT 1.0,
    PRIMARY KEY (artist_id, genre_id),
    FOREIGN KEY (artist_id) REFERENCES artists(id) ON DELETE CASCADE,
    FOREIGN KEY (genre_id) REFERENCES genres(id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS words (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    word TEXT NOT NULL,
    language TEXT NOT NULL,
    part_of_speech TEXT NOT NULL,
    weight REAL NOT NULL DEFAULT 1.0,
    enabled INTEGER NOT NULL DEFAULT 1,
    gender TEXT,
    number TEXT
);
CREATE INDEX IF NOT EXISTS idx_words_lang_pos ON words(language, part_of_speech);
CREATE TABLE IF NOT EXISTS word_genres (
    word_id INTEGER NOT NULL,
    genre_id INTEGER NOT NULL,
    weight REAL NOT NULL DEFAULT 1.0,
    PRIMARY KEY (word_id, genre_id),
    FOREIGN KEY (word_id) REFERENCES words(id) ON DELETE CASCADE,
    FOREIGN KEY (genre_id) REFERENCES genres(id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    language TEXT NOT NULL DEFAULT 'any',
    template TEXT NOT NULL,
    weight REAL NOT NULL DEFAULT 1.0,
    enabled INTEGER NOT NULL DEFAULT 1
);
CREATE TABLE IF NOT EXISTS genre_relations (
    genre_id INTEGER NOT NULL,
    related_genre_id INTEGER NOT NULL,
    weight REAL NOT NULL DEFAULT 1.0,
    PRIMARY KEY (genre_id, related_genre_id),
    FOREIGN KEY (genre_id) REFERENCES genres(id) ON DELETE CASCADE,
    FOREIGN KEY (related_genre_id) REFERENCES genres(id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS generation_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    genre_id INTEGER,
    language TEXT,
    artists_json TEXT DEFAULT '[]',
    pattern TEXT DEFAULT '',
    created_at TEXT NOT NULL,
    moods_json TEXT DEFAULT '[]',
    artist_pool TEXT DEFAULT 'all',
    FOREIGN KEY (genre_id) REFERENCES genres(id) ON DELETE SET NULL
);
CREATE TABLE IF NOT EXISTS moods (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT DEFAULT '',
    icon TEXT DEFAULT '',
    enabled INTEGER NOT NULL DEFAULT 1
);
CREATE TABLE IF NOT EXISTS word_moods (
    word_id INTEGER NOT NULL,
    mood_id INTEGER NOT NULL,
    weight REAL NOT NULL DEFAULT 1.0,
    PRIMARY KEY (word_id, mood_id),
    FOREIGN KEY (word_id) REFERENCES words(id) ON DELETE CASCADE,
    FOREIGN KEY (mood_id) REFERENCES moods(id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS meta (
    key TEXT PRIMARY KEY,
    value TEXT
);
"""


def create_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA_SQL)
    ensure_indexes(conn)
    conn.commit()


def ensure_indexes(conn: sqlite3.Connection) -> None:
    try:
        conn.execute("CREATE INDEX IF NOT EXISTS idx_artists_language ON artists(language)")
    except sqlite3.OperationalError:
        pass  # very old DB without the column; migrate_database handles it


def get_meta(conn: sqlite3.Connection, key: str) -> str | None:
    row = conn.execute("SELECT value FROM meta WHERE key = ?", (key,)).fetchone()
    return row["value"] if row else None


def set_meta(conn: sqlite3.Connection, key: str, value: str) -> None:
    conn.execute("INSERT OR REPLACE INTO meta(key, value) VALUES (?, ?)", (key, value))
    conn.commit()


def migrate_database(conn: sqlite3.Connection) -> None:
    """Bring older databases up to the current schema (tables + columns)."""
    create_schema(conn)  # IF NOT EXISTS covers new tables on old DBs
    cols = {r["name"] for r in conn.execute("PRAGMA table_info(generation_history)")}
    if "moods_json" not in cols:
        conn.execute("ALTER TABLE generation_history ADD COLUMN moods_json TEXT DEFAULT '[]'")
    if "artist_pool" not in {r["name"] for r in conn.execute("PRAGMA table_info(generation_history)")}:
        conn.execute("ALTER TABLE generation_history ADD COLUMN artist_pool TEXT DEFAULT 'all'")
    acols = {r["name"] for r in conn.execute("PRAGMA table_info(artists)")}
    if "region" not in acols:
        conn.execute("ALTER TABLE artists ADD COLUMN region TEXT")
    if "language" not in acols:
        conn.execute("ALTER TABLE artists ADD COLUMN language TEXT")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_artists_language ON artists(language)")
    conn.commit()
