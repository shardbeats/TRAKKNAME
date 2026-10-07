"""Title generation engine — independent of PySide6 (testable).

Thin orchestrator: stages live in focused submodules
(``results`` / ``artists`` / ``context`` / ``patterns`` / ``renderer``).
This module keeps the historic import surface so tests, services and
UI keep doing ``from app.generator.engine import generate_title, ...``.
"""
from __future__ import annotations

import random
import sqlite3

from app.database.repositories import history as history_repo
from app.generator import weighted_random as wr
from app.generator.artists import select_artists
from app.generator.context import (
    _related_ids,
    _resolve_artist_boost,
    _resolve_moods,
    related_ids,
    resolve_artist_boost,
    resolve_context,
    resolve_moods,
)
from app.generator.patterns import pick_patterns
from app.generator.renderer import _pick_word, pick_word, render_title
from app.generator.results import GenContext, GenerationError, GenerationResult
from app.utils.text import normalize_title

__all__ = [
    "GenContext",
    "GenerationError",
    "GenerationResult",
    "generate_title",
    "pick_patterns",
    "pick_word",
    "related_ids",
    "render_title",
    "resolve_artist_boost",
    "resolve_context",
    "resolve_moods",
    "select_artists",
]


def generate_title(conn: sqlite3.Connection, genre_name: str | None = None, language: str = "en",
                   artist_count: int = 2, style: str = "Random",
                   w_genre: float = 0.70, w_related: float = 0.20, w_global: float = 0.10,
                   artist_influence: float = 0.5, allowed_pos: set[str] | None = None,
                   recent_limit: int = 100, rng: random.Random | None = None,
                   save: bool = True, single_word: bool = False,
                   moods: list[str] | None = None, w_mood: float = 1.0,
                   artist_pool: str | None = None) -> GenerationResult:
    rng = rng or random.Random()
    ctx = resolve_context(conn, genre_name, language, artist_count, artist_influence,
                          moods, artist_pool, rng)
    language = ctx.language
    prows = pick_patterns(conn, language, style, single_word)
    recent = history_repo.recent_titles(conn, recent_limit) if recent_limit > 0 else set()
    if single_word:
        # Single-word titles are always nouns; don't let word-type
        # checkboxes block the mode.
        allowed_pos = set(allowed_pos) | {"noun"} if allowed_pos else {"noun"}

    last_err: Exception | None = None
    for _attempt in range(30):
        prow = wr.choose_weighted(list(prows), [max(float(r["weight"]), 0) for r in prows], rng)
        try:
            title = render_title(conn, ctx, prow["template"], language,
                                 w_genre, w_related, w_global, w_mood, allowed_pos, rng)
        except GenerationError as e:
            last_err = e
            continue
        if normalize_title(title) in recent:
            continue
        res = GenerationResult(title=title, genre_name=ctx.genre_label, genre_id=ctx.genre_id,
                               language=language, artists=ctx.artists,
                               pattern_name=prow["name"], pattern_template=prow["template"],
                               moods=ctx.mood_names)
        if save:
            history_repo.save_history(conn, title, ctx.genre_id, language, ctx.artists,
                                      prow["name"], ctx.mood_names,
                                      ctx.artist_pool if ctx.artist_pool else "all")
            recent.add(normalize_title(title))
        return res
    raise GenerationError(str(last_err) if last_err else "Unable to generate a title. No enabled words are available for this genre.")
