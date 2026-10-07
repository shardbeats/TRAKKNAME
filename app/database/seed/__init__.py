"""Seed orchestration: schema fill + idempotent ensure_* migrations.

Raw data lives in app/database/seed_data/ (edit lists there, not here).
Backwards-compat package: ``from app.database.seed import X`` keeps working;
implementation lives in focused submodules.
"""
from __future__ import annotations

from app.database.seed.artists_seed import ensure_artist_meta, ensure_artists
from app.database.seed.bootstrap import seed_database
from app.database.seed.moods_seed import seed_moods
from app.database.seed.patterns_seed import ensure_patterns
from app.database.seed.placeholders import ensure_no_placeholders
from app.database.seed_data.artists import ARTIST_META, ARTISTS
from app.database.seed_data.genres import GENRE_RELATIONS, GENRE_VIBES, GENRES
from app.database.seed_data.moods import MOOD_VIBES, MOODS
from app.database.seed_data.patterns import (
    PATTERNS,
    REMOVED_PATTERNS,
    RETIRED_PATTERNS,
    STYLE_RENAMES,
)
from app.database.seed_data.vocabulary import (
    EN_ADJECTIVES,
    EN_NOUNS,
    EN_VERBS,
    ES_ADJECTIVES,
    ES_NOUNS_RAW,
    ES_VERBS,
)

__all__ = [
    "SCHEMA_VERSION",
    "GENRES", "GENRE_RELATIONS", "GENRE_VIBES",
    "ARTISTS", "ARTIST_META",
    "EN_VERBS", "EN_ADJECTIVES", "EN_NOUNS",
    "ES_VERBS", "ES_ADJECTIVES", "ES_NOUNS_RAW",
    "MOODS", "MOOD_VIBES",
    "PATTERNS", "RETIRED_PATTERNS", "REMOVED_PATTERNS", "STYLE_RENAMES",
    "seed_database", "seed_moods", "ensure_artists", "ensure_artist_meta",
    "ensure_patterns", "ensure_no_placeholders",
]

SCHEMA_VERSION = "1"
