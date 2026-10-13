"""JSON import/export + reset. Never silently overwrite: caller confirms."""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

# A backup bigger than this is almost certainly not ours: refuse before
# loading the whole file into RAM (runs on the GUI thread).
MAX_IMPORT_BYTES = 100 * 1024 * 1024


def export_database(conn: sqlite3.Connection, dest: Path) -> Path:
    data: dict = {}
    for table in ("genres", "artists", "artist_genres", "words", "word_genres", "patterns", "genre_relations", "moods", "word_moods", "generation_history"):
        try:
            data[table] = [dict(r) for r in conn.execute(f"SELECT * FROM {table}")]
        except Exception:
            data[table] = []
    dest.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return dest


def _req(row, *keys) -> bool:
    """True when every required key is present and not None (dict-safe)."""
    return isinstance(row, dict) and all(row.get(k) is not None for k in keys)


def import_database(conn: sqlite3.Connection, src: Path) -> int:
    """Replace DB contents from a JSON backup. Returns malformed rows skipped.

    - Files over MAX_IMPORT_BYTES are rejected before parsing (RAM guard).
    - Rows missing required keys are skipped (counted), never aborting the
      whole import midway with a KeyError.
    """
    try:
        if src.stat().st_size > MAX_IMPORT_BYTES:
            mb = MAX_IMPORT_BYTES // (1024 * 1024)
            raise ValueError(f"Import file too large (>{mb} MB).")
    except OSError as exc:
        raise ValueError(f"Cannot read import file: {exc}")
    try:
        payload = json.loads(src.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Invalid backup file: {exc}")
    if not isinstance(payload, dict):
        raise ValueError("Invalid backup file: expected a JSON object.")
    skipped = 0
    with conn:
        for table in ("generation_history", "word_moods", "word_genres", "artist_genres", "genre_relations", "patterns", "words", "artists", "moods", "genres"):
            if table in payload:
                try:
                    conn.execute(f"DELETE FROM {table}")
                except Exception:
                    pass
        for g in payload.get("genres", []):
            if not _req(g, "id", "name"):
                skipped += 1
                continue
            conn.execute("INSERT OR REPLACE INTO genres(id, name, description, enabled) VALUES (?,?,?,?)",
                         (g["id"], g["name"], g.get("description", ""), g.get("enabled", 1)))
        for a in payload.get("artists", []):
            if not _req(a, "id", "name"):
                skipped += 1
                continue
            try:
                has_cols = any(r["name"] == "region" for r in conn.execute("PRAGMA table_info(artists)"))
            except Exception:
                has_cols = False
            if has_cols:
                conn.execute("INSERT OR REPLACE INTO artists(id, name, enabled, region, language) VALUES (?,?,?,?,?)",
                             (a["id"], a["name"], a.get("enabled", 1), a.get("region"), a.get("language")))
            else:
                conn.execute("INSERT OR REPLACE INTO artists(id, name, enabled) VALUES (?,?,?)", (a["id"], a["name"], a.get("enabled", 1)))
        for r in payload.get("artist_genres", []):
            if not _req(r, "artist_id", "genre_id"):
                skipped += 1
                continue
            conn.execute("INSERT OR REPLACE INTO artist_genres(artist_id, genre_id, weight) VALUES (?,?,?)",
                         (r["artist_id"], r["genre_id"], r.get("weight", 1.0)))
        for w in payload.get("words", []):
            if not _req(w, "id", "word", "language", "part_of_speech"):
                skipped += 1
                continue
            conn.execute("INSERT OR REPLACE INTO words(id, word, language, part_of_speech, weight, enabled, gender, number) VALUES (?,?,?,?,?,?,?,?)",
                         (w["id"], w["word"], w["language"], w["part_of_speech"], w.get("weight", 1.0), w.get("enabled", 1), w.get("gender"), w.get("number")))
        for wg in payload.get("word_genres", []):
            if not _req(wg, "word_id", "genre_id"):
                skipped += 1
                continue
            conn.execute("INSERT OR REPLACE INTO word_genres(word_id, genre_id, weight) VALUES (?,?,?)",
                         (wg["word_id"], wg["genre_id"], wg.get("weight", 1.0)))
        for p in payload.get("patterns", []):
            if not _req(p, "name", "template"):
                skipped += 1
                continue
            conn.execute("INSERT OR REPLACE INTO patterns(id, name, language, template, weight, enabled) VALUES (?,?,?,?,?,?)",
                         (p.get("id"), p["name"], p.get("language", "any"), p["template"], p.get("weight", 1.0), p.get("enabled", 1)))
        for md in payload.get("moods", []):
            if not _req(md, "name"):
                skipped += 1
                continue
            conn.execute("INSERT OR REPLACE INTO moods(id, name, description, icon, enabled) VALUES (?,?,?,?,?)",
                         (md.get("id"), md["name"], md.get("description", ""), md.get("icon", ""), md.get("enabled", 1)))
        for wm in payload.get("word_moods", []):
            if not _req(wm, "word_id", "mood_id"):
                skipped += 1
                continue
            conn.execute("INSERT OR REPLACE INTO word_moods(word_id, mood_id, weight) VALUES (?,?,?)",
                         (wm["word_id"], wm["mood_id"], wm.get("weight", 1.0)))
        for gr in payload.get("genre_relations", []):
            if not _req(gr, "genre_id", "related_genre_id"):
                skipped += 1
                continue
            conn.execute("INSERT OR REPLACE INTO genre_relations(genre_id, related_genre_id, weight) VALUES (?,?,?)",
                         (gr["genre_id"], gr["related_genre_id"], gr.get("weight", 1.0)))
        # history optional
        has_moods_col = any(r["name"] == "moods_json" for r in conn.execute("PRAGMA table_info(generation_history)"))
        for h in payload.get("generation_history", []):
            if not isinstance(h, dict):
                skipped += 1
                continue
            if has_moods_col:
                conn.execute("INSERT OR REPLACE INTO generation_history(id, title, genre_id, language, artists_json, pattern, created_at, moods_json) VALUES (?,?,?,?,?,?,?,?)",
                             (h.get("id"), h.get("title"), h.get("genre_id"), h.get("language"), h.get("artists_json", "[]"), h.get("pattern", ""), h.get("created_at", ""), h.get("moods_json", "[]")))
            else:
                conn.execute("INSERT OR REPLACE INTO generation_history(id, title, genre_id, language, artists_json, pattern, created_at) VALUES (?,?,?,?,?,?,?)",
                             (h.get("id"), h.get("title"), h.get("genre_id"), h.get("language"), h.get("artists_json", "[]"), h.get("pattern", ""), h.get("created_at", "")))
    return skipped


def reset_database(db_path: Path) -> None:
    from app.database.connection import get_connection
    from app.database.schema import create_schema
    from app.database.seed import seed_database
    if db_path.exists():
        db_path.unlink()
    conn = get_connection(db_path)
    try:
        create_schema(conn)
        seed_database(conn)
    finally:
        conn.close()
