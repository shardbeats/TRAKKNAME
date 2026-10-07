"""First-launch / migration orchestration (extracted from main.py)."""
from __future__ import annotations

from pathlib import Path

from app.database.connection import get_connection
from app.database.schema import create_schema, migrate_database
from app.database.seed import (
    ensure_artist_meta,
    ensure_artists,
    ensure_no_placeholders,
    ensure_patterns,
    seed_database,
    seed_moods,
)


def ensure_database(db_path: Path, logger) -> None:
    first = not db_path.exists()
    conn = get_connection(db_path)
    try:
        create_schema(conn)
        count = conn.execute("SELECT COUNT(*) c FROM genres").fetchone()["c"]
        if first or count == 0:
            logger.info("Seeding database (first launch)…")
            seed_database(conn)
            logger.info("Seed complete.")
        else:
            migrate_database(conn)
            seed_moods(conn)
            n = ensure_artists(conn)
            if n:
                logger.info("Added %d new seed artists.", n)
            ensure_artist_meta(conn)
            ensure_patterns(conn)
            n = ensure_no_placeholders(conn)
            if n:
                logger.info("Removed %d placeholder words.", n)
    finally:
        conn.close()
