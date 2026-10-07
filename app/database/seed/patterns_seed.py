"""Curated pattern migrations (retire = disable, remove = delete). Idempotent."""
from __future__ import annotations

import sqlite3

from app.database.seed_data.patterns import PATTERNS, REMOVED_PATTERNS, RETIRED_PATTERNS, STYLE_RENAMES


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
