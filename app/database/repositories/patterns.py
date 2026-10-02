from __future__ import annotations

import sqlite3


def list_patterns(conn: sqlite3.Connection, language: str = ""):
    if language:
        return conn.execute("SELECT * FROM patterns WHERE language IN ('any', ?) ORDER BY weight DESC", (language,)).fetchall()
    return conn.execute("SELECT * FROM patterns ORDER BY language, weight DESC").fetchall()


def save_pattern(conn: sqlite3.Connection, name: str, language: str, template: str, weight: float = 1.0, enabled: bool = True, pid: int | None = None) -> int:
    name, template = name.strip(), template.strip()
    if not name or not template:
        raise ValueError("Pattern name and template must not be empty.")
    toks = template.split()
    valid = {"ADJ", "NOUN", "VERB"}
    for t in toks:
        if t in valid or (t[0].isupper() and t not in valid):
            continue
        # allow literals like de/la/Los/The/After/of/Dreams/Nights/Lost
    if weight < 0:
        raise ValueError("Weight must be >= 0.")
    with conn:
        if pid is None:
            cur = conn.execute("INSERT INTO patterns(name, language, template, weight, enabled) VALUES (?,?,?,?,?)",
                               (name, language, template, weight, int(enabled)))
            return cur.lastrowid
        conn.execute("UPDATE patterns SET name=?, language=?, template=?, weight=?, enabled=? WHERE id=?",
                     (name, language, template, weight, int(enabled), pid))
        return pid


def delete_pattern(conn: sqlite3.Connection, pid: int) -> None:
    with conn:
        conn.execute("DELETE FROM patterns WHERE id = ?", (pid,))
