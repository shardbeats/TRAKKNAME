"""High-level generation facade used by the UI (and tests)."""
from __future__ import annotations

import random
import sqlite3

from app.generator.engine import GenerationResult, generate_title


class GenerationService:
    def __init__(self, db_path, settings):
        self.db_path = str(db_path)
        self.settings = settings
        self._rng = random.Random()

    def _conn(self) -> sqlite3.Connection:
        from app.database.connection import get_connection
        return get_connection(self.db_path)

    def generate(self, genre: str | None = None, language: str | None = None,
                 artist_count: int | None = None, style: str | None = None,
                 save: bool = True, single_word: bool | None = None,
                 moods: list[str] | None = None, artist_pool: str | None = None) -> GenerationResult:
        s = self.settings.data if hasattr(self.settings, "data") else {}
        language = language or s.get("default_language", "en")
        genre = genre or s.get("default_genre")
        artist_count = s.get("artists_per_generation", 2) if artist_count is None else artist_count
        style = style or s.get("default_style", "Random")
        if single_word is None:
            single_word = bool(s.get("single_word", False))
        if moods is None:
            moods = list(s.get("selected_moods", []))
        if artist_pool is None:
            artist_pool = s.get("artist_pool", "all")
        allowed = set()
        if s.get("use_verbs", True):
            allowed.add("verb")
        if s.get("use_adjectives", True):
            allowed.add("adjective")
        if s.get("use_nouns", True):
            allowed.add("noun")
        if not allowed:
            allowed = {"verb", "adjective", "noun"}
        conn = self._conn()
        try:
            return generate_title(
                conn, genre_name=genre, language=language, artist_count=int(artist_count),
                style=style, w_genre=float(s.get("w_genre", 0.70)), w_related=float(s.get("w_related", 0.20)),
                w_global=float(s.get("w_global", 0.10)), artist_influence=float(s.get("artist_influence", 0.5)),
                allowed_pos=allowed, recent_limit=int(s.get("recent_exclusion_count", 100)),
                rng=self._rng, save=save, single_word=bool(single_word),
                moods=moods, w_mood=float(s.get("w_mood", 1.0)), artist_pool=artist_pool)
        finally:
            conn.close()
