"""Non-Qt presenter: options persistence + artist fetch + generation.

The view stays thin (layout + signals); all DB/service access lives here
so it can be unit-tested without Qt.
"""
from __future__ import annotations

import random
from dataclasses import dataclass


@dataclass
class GeneratorOptions:
    genre: str = ""
    language: str = "en"
    artist_count: int = 2
    style: str = "Random"
    single_word: bool = False
    artist_pool: str = "all"


class GeneratorPresenter:
    def __init__(self, service, settings):
        self.service = service
        self.settings = settings
        self.db_path = getattr(service, "db_path", None)

    def _db(self):
        from app.database.connection import get_connection
        return get_connection(self.db_path or self.service.db_path)

    # ---- options ----
    def persist(self, opts: GeneratorOptions, extras: dict) -> None:
        self.settings.data.update({
            "default_genre": opts.genre,
            "default_language": opts.language,
            "artists_per_generation": opts.artist_count,
            "default_style": opts.style,
            "artist_influence": extras.get("artist_influence", 0.5),
            "use_verbs": extras.get("use_verbs", True),
            "use_adjectives": extras.get("use_adjectives", True),
            "use_nouns": extras.get("use_nouns", True),
            "single_word": opts.single_word,
            "artist_pool": opts.artist_pool,
        })
        self.settings.save()

    # ---- data ----
    def list_genres(self) -> list[str]:
        conn = self._db()
        try:
            return [r["name"] for r in conn.execute("SELECT name FROM genres WHERE enabled=1 ORDER BY name")]
        finally:
            conn.close()

    def list_styles(self, lang: str) -> list[str]:
        conn = self._db()
        try:
            rows = conn.execute(
                "SELECT name FROM patterns WHERE enabled = 1 AND language IN ('any', ?) ORDER BY name",
                (lang,)).fetchall()
            return [r["name"] for r in rows]
        finally:
            conn.close()

    def fetch_artists(self, opts: GeneratorOptions) -> tuple[list[str], GeneratorOptions]:
        """Weighted artist pick for the current opts (preview AND re-roll)."""
        from app.generator.engine import select_artists
        conn = self._db()
        try:
            grow = conn.execute("SELECT id FROM genres WHERE name=?", (opts.genre,)).fetchone()
            gid = grow["id"] if grow else None
            pool = opts.artist_pool if opts.artist_pool != "all" else None
            return select_artists(conn, gid, opts.artist_count, random.Random(), pool), opts
        finally:
            conn.close()

    def generate(self, opts: GeneratorOptions):
        return self.service.generate(
            genre=opts.genre or None, language=opts.language,
            artist_count=opts.artist_count, style=opts.style,
            single_word=opts.single_word, artist_pool=opts.artist_pool)
