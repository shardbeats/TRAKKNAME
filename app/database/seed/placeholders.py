"""Legacy placeholder cleanup (versoNNN, sombraNNN). Idempotent + FK-cascaded."""
from __future__ import annotations

import sqlite3


def ensure_no_placeholders(conn: sqlite3.Connection) -> int:
    """Delete legacy seed placeholders (versoNNN, sombraNNN) from dirty DBs.

    Safe: no legitimate word in our dataset contains a digit.
    Cascades to word_genres/word_moods via FK. Idempotent.
    """
    with conn:
        cur = conn.execute("DELETE FROM words WHERE word GLOB '*[0-9]*'")
        return cur.rowcount
