from __future__ import annotations

import sqlite3


def search_words(conn: sqlite3.Connection, language: str = "", pos: str = "", genre_id: int | None = None, search: str = "", limit: int = 500):
    q = """SELECT w.*, GROUP_CONCAT(g.name, ', ') AS genre_names FROM words w
           LEFT JOIN word_genres wg ON wg.word_id = w.id
           LEFT JOIN genres g ON g.id = wg.genre_id WHERE 1=1"""
    args: list = []
    if language:
        q += " AND w.language = ?"; args.append(language)
    if pos:
        q += " AND w.part_of_speech = ?"; args.append(pos)
    if search:
        q += " AND w.word LIKE ?"; args.append(f"%{search}%")
    if genre_id:
        q += " AND w.id IN (SELECT word_id FROM word_genres WHERE genre_id = ?)"
        args.append(genre_id)
    q += " GROUP BY w.id ORDER BY w.word LIMIT ?"
    args.append(limit)
    return conn.execute(q, args).fetchall()


def pool_words(conn: sqlite3.Connection, language: str, pos: str, genre_id: int | None,
               related_ids: list[int], w_genre: float, w_related: float, w_global: float,
               allowed_pos: set[str] | None = None, artist_boost: dict[int, float] | None = None,
               mood_boost: dict[int, float] | None = None, w_mood: float = 0.0):
    """Return [(word, gender, number, eff_weight)] mixing genre/related/global pools.

    mood_boost maps word_id -> link weight; linked words get
    ``eff *= (1 + w_mood * link_weight)``. ``w_mood = 1.0`` doubles them.
    """
    if allowed_pos and pos not in allowed_pos:
        return []
    rows = conn.execute(
        "SELECT id, word, weight, gender, number FROM words WHERE language = ? AND part_of_speech = ? AND enabled = 1",
        (language, pos)).fetchall()
    if not rows:
        return []
    # one query for ALL genre links (was N+1 before): word_id -> {genre_id: weight}
    links: dict[int, dict[int, float]] = {}
    for r in conn.execute("SELECT word_id, genre_id, weight FROM word_genres"):
        links.setdefault(r["word_id"], {})[r["genre_id"]] = float(r["weight"])
    related_set = set(related_ids or [])
    out = []
    for r in rows:
        wid = r["id"]
        base = max(float(r["weight"]), 0.0)
        wl = links.get(wid, {})
        if genre_id is not None and genre_id in wl:
            eff = base * wl[genre_id] * w_genre
        elif related_set and any(g in related_set for g in wl):
            eff = base * w_related
        else:
            eff = base * w_global
        if artist_boost and wid in artist_boost:
            eff *= float(artist_boost[wid])
        if mood_boost and wid in mood_boost and w_mood > 0:
            eff *= (1.0 + float(w_mood) * float(mood_boost[wid]))
        if eff <= 0:
            continue
        out.append((r["word"], r["gender"], r["number"], eff))
    return out


def save_word(conn: sqlite3.Connection, word: str, language: str, pos: str, weight: float = 1.0,
              enabled: bool = True, gender: str | None = None, number: str | None = None,
              genre_weights: dict[int, float] | None = None, word_id: int | None = None,
              mood_weights: dict[int, float] | None = None) -> int:
    word = word.strip().lower()
    if not word:
        raise ValueError("Word must not be empty.")
    if language not in ("en", "es"):
        raise ValueError("Invalid language.")
    if pos not in ("verb", "adjective", "noun"):
        raise ValueError("Invalid part of speech.")
    if weight < 0:
        raise ValueError("Weight must be >= 0.")
    with conn:
        if word_id is None:
            cur = conn.execute("INSERT INTO words(word, language, part_of_speech, weight, enabled, gender, number) VALUES (?,?,?,?,?,?,?)",
                               (word, language, pos, weight, int(enabled), gender, number))
            wid = cur.lastrowid
        else:
            conn.execute("UPDATE words SET word=?, language=?, part_of_speech=?, weight=?, enabled=?, gender=?, number=? WHERE id=?",
                         (word, language, pos, weight, int(enabled), gender, number, word_id))
            wid = word_id
            conn.execute("DELETE FROM word_genres WHERE word_id = ?", (wid,))
            conn.execute("DELETE FROM word_moods WHERE word_id = ?", (wid,))
        for gid, w in (genre_weights or {}).items():
            if w > 0:
                conn.execute("INSERT OR REPLACE INTO word_genres(word_id, genre_id, weight) VALUES (?,?,?)", (wid, gid, float(w)))
        for mid, w in (mood_weights or {}).items():
            if w > 0:
                conn.execute("INSERT OR REPLACE INTO word_moods(word_id, mood_id, weight) VALUES (?,?,?)", (wid, mid, float(w)))
        return wid


def delete_word(conn: sqlite3.Connection, word_id: int) -> None:
    with conn:
        conn.execute("DELETE FROM words WHERE id = ?", (word_id,))
