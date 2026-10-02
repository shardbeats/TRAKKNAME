from __future__ import annotations

import sqlite3


def list_moods(conn: sqlite3.Connection, only_enabled: bool = False):
    q = "SELECT * FROM moods"
    if only_enabled:
        q += " WHERE enabled = 1"
    q += " ORDER BY name"
    return conn.execute(q).fetchall()


def mood_ids_for_names(conn: sqlite3.Connection, names: list[str]) -> list[int]:
    if not names:
        return []
    ph = ",".join("?" * len(names))
    return [r["id"] for r in conn.execute(
        f"SELECT id FROM moods WHERE name IN ({ph}) AND enabled = 1", names)]


def mood_word_weights(conn: sqlite3.Connection, mood_ids: list[int]) -> dict[int, float]:
    """Max link weight per word for the given moods (single query)."""
    if not mood_ids:
        return {}
    ph = ",".join("?" * len(mood_ids))
    rows = conn.execute(
        f"SELECT word_id, MAX(weight) AS w FROM word_moods WHERE mood_id IN ({ph}) GROUP BY word_id",
        mood_ids).fetchall()
    return {r["word_id"]: float(r["w"]) for r in rows}


def word_count_for_mood(conn: sqlite3.Connection, mood_id: int) -> int:
    return conn.execute("SELECT COUNT(*) c FROM word_moods WHERE mood_id = ?", (mood_id,)).fetchone()["c"]


def save_mood(conn: sqlite3.Connection, name: str, description: str = "", icon: str = "",
              enabled: bool = True, mood_id: int | None = None) -> int:
    name = name.strip()
    if not name:
        raise ValueError("Mood name must not be empty.")
    with conn:
        if mood_id is None:
            conn.execute("INSERT INTO moods(name, description, icon, enabled) VALUES (?,?,?,?) "
                         "ON CONFLICT(name) DO UPDATE SET description=excluded.description, icon=excluded.icon, enabled=excluded.enabled",
                         (name, description, icon, int(enabled)))
            return conn.execute("SELECT id FROM moods WHERE name = ?", (name,)).fetchone()["id"]
        conn.execute("UPDATE moods SET name=?, description=?, icon=?, enabled=? WHERE id=?",
                     (name, description, icon, int(enabled), mood_id))
        return mood_id


def delete_mood(conn: sqlite3.Connection, mood_id: int) -> None:
    with conn:
        conn.execute("DELETE FROM moods WHERE id = ?", (mood_id,))
