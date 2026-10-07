"""Fresh-database bootstrap (first launch only)."""
from __future__ import annotations

import sqlite3

from app.database.seed_data.artists import ARTIST_META, ARTISTS
from app.database.seed_data.genres import GENRE_RELATIONS, GENRE_VIBES, GENRES
from app.database.seed_data.patterns import PATTERNS
from app.database.seed_data.vocabulary import (
    EN_ADJECTIVES,
    EN_NOUNS,
    EN_VERBS,
    ES_ADJECTIVES,
    ES_NOUNS_RAW,
    ES_VERBS,
)


def seed_database(conn: sqlite3.Connection) -> None:
    from app.database.schema import get_meta, set_meta
    from app.database.seed.artists_seed import ensure_artist_meta
    from app.database.seed.moods_seed import seed_moods

    from app.database.seed import SCHEMA_VERSION

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
    # Silence unused import (ARTIST_META is the source of truth for meta).
    _ = ARTIST_META
