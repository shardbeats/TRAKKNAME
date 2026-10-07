"""Stage 2: candidate pattern rows for the attempt loop."""
from __future__ import annotations

import sqlite3

from app.database.repositories import patterns as patterns_repo


def pick_patterns(conn: sqlite3.Connection, language: str, style: str, single_word: bool):
    if single_word:
        # Only patterns rendering exactly one word (a lone NOUN slot —
        # no literals like "Lost NOUN" or "NOUN Nights").
        singles = [r for r in patterns_repo.list_patterns(conn, language)
                   if r["enabled"] == 1 and r["template"].strip().upper() == "NOUN"]
        if singles:
            return singles
        return [{"id": 0, "name": "Single word", "language": language,
                 "template": "NOUN", "weight": 1.0, "enabled": 1}]
    if style and style != "Random":
        prows = [r for r in patterns_repo.list_patterns(conn, language) if r["name"] == style and r["enabled"] == 1]
        if prows:
            return prows
    prows = [r for r in patterns_repo.list_patterns(conn, language) if r["enabled"] == 1]
    if not prows:
        from app.generator.results import GenerationError
        raise GenerationError("No generation patterns available.")
    return prows
