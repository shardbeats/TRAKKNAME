"""Title generation engine — independent of PySide6 (testable)."""
from __future__ import annotations

import random
import sqlite3
from dataclasses import dataclass, field

from app.database.repositories import history as history_repo
from app.database.repositories import moods as moods_repo
from app.database.repositories import patterns as patterns_repo
from app.database.repositories import words as words_repo
from app.generator import weighted_random as wr
from app.generator.grammar import agree_pair
from app.generator.templates import parse_template
from app.models.enums import LEGACY_POOL_MAP
from app.utils.text import normalize_title, title_case


@dataclass
class GenerationResult:
    title: str
    genre_name: str
    genre_id: int | None
    language: str
    artists: list[str]
    pattern_name: str
    pattern_template: str
    moods: list[str] = field(default_factory=list)


class GenerationError(Exception):
    pass


@dataclass
class GenContext:
    """Everything generate_title resolves before attempting patterns."""
    genre_id: int | None
    genre_label: str
    language: str
    artists: list[str]
    related_ids: list[int]
    mood_names: list[str]
    mood_boost: dict[int, float]
    artist_boost: dict[int, float]
    artist_pool: str | None


def _related_ids(conn: sqlite3.Connection, genre_id: int) -> list[int]:
    rows = conn.execute("SELECT related_genre_id FROM genre_relations WHERE genre_id = ?", (genre_id,)).fetchall()
    return [r["related_genre_id"] for r in rows]


def select_artists(conn: sqlite3.Connection, genre_id: int | None, count: int,
                   rng: random.Random, pool: str | None = None) -> list[str]:
    if not genre_id or count <= 0:
        return []
    pool = LEGACY_POOL_MAP.get(pool, pool) if pool else None
    q = """SELECT a.id, a.name, ag.weight FROM artists a
           JOIN artist_genres ag ON ag.artist_id = a.id
           WHERE ag.genre_id = ? AND a.enabled = 1"""
    args: list = [genre_id]
    if pool == "es":
        q += " AND a.language = 'es'"
    elif pool == "en":
        q += " AND COALESCE(a.language, 'en') = 'en'"
    q += " ORDER BY ag.weight DESC"
    rows = conn.execute(q, args).fetchall()
    if not rows:
        return []
    names = [r["name"] for r in rows]
    weights = [max(float(r["weight"]), 0.0) for r in rows]
    return wr.sample_weighted_unique(names, weights, min(count, len(names)), rng)


def _pick_word(pool: list[tuple[str, str | None, str | None, float]], rng: random.Random) -> tuple[str, str | None, str | None]:
    if not pool:
        raise GenerationError("No words available in pool.")
    words = [p[0] for p in pool]
    weights = [p[3] for p in pool]
    idx = wr.choose_weighted(list(range(len(words))), weights, rng)
    w, g, n, _ = pool[int(idx)]
    return w, g, n


def resolve_context(conn: sqlite3.Connection, genre_name: str | None, language: str,
                    artist_count: int, artist_influence: float,
                    moods: list[str] | None, artist_pool: str | None,
                    rng: random.Random) -> GenContext:
    """Stage 1: resolve genre, artists, related genres, mood/artist boosts."""
    language = language if language in ("en", "es") else "en"
    grow = conn.execute("SELECT id, name FROM genres WHERE name = ?", (genre_name,)).fetchone() if genre_name else None
    if genre_name and not grow:
        grow = conn.execute("SELECT id, name FROM genres WHERE enabled = 1 ORDER BY name LIMIT 1").fetchone()
    genre_id = grow["id"] if grow else None
    genre_label = grow["name"] if grow else (genre_name or "Unknown")

    pool = LEGACY_POOL_MAP.get(artist_pool, artist_pool) if artist_pool else None
    artists = select_artists(conn, genre_id, artist_count, rng, pool)
    related = _related_ids(conn, genre_id) if genre_id else []
    mood_names, mood_boost = _resolve_moods(conn, moods)
    artist_boost = _resolve_artist_boost(conn, artists, genre_id, artist_influence)
    return GenContext(genre_id, genre_label, language, artists, related,
                      mood_names, mood_boost, artist_boost, pool)


def _resolve_moods(conn: sqlite3.Connection, moods: list[str] | None) -> tuple[list[str], dict[int, float]]:
    requested = [m.strip() for m in (moods or []) if m and m.strip()][:2]
    mood_ids = moods_repo.mood_ids_for_names(conn, requested)
    names: list[str] = []
    if mood_ids:
        rows = conn.execute(
            f"SELECT name FROM moods WHERE id IN ({','.join('?' * len(mood_ids))})", mood_ids).fetchall()
        names = [r["name"] for r in rows]
    return names, moods_repo.mood_word_weights(conn, mood_ids) if mood_ids else {}


def _resolve_artist_boost(conn: sqlite3.Connection, artists: list[str],
                          genre_id: int | None, artist_influence: float) -> dict[int, float]:
    """Words linked to the artists' *other* genres get a mild boost."""
    boost: dict[int, float] = {}
    if not (artists and artist_influence > 0 and genre_id):
        return boost
    for aname in artists:
        aid = conn.execute("SELECT id FROM artists WHERE name = ?", (aname,)).fetchone()
        if not aid:
            continue
        others = conn.execute("SELECT genre_id FROM artist_genres WHERE artist_id = ? AND genre_id != ?",
                              (aid["id"], genre_id)).fetchall()
        if not others:
            continue
        ph = ",".join("?" * len(others))
        factor = 1.0 + float(artist_influence) * 0.5
        for wr_ in conn.execute(f"SELECT word_id FROM word_genres WHERE genre_id IN ({ph})",
                                [r["genre_id"] for r in others]):
            boost[wr_["word_id"]] = factor
    return boost


def pick_patterns(conn: sqlite3.Connection, language: str, style: str, single_word: bool):
    """Stage 2: candidate pattern rows for the attempt loop."""
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
        raise GenerationError("No generation patterns available.")
    return prows


def render_title(conn: sqlite3.Connection, ctx: GenContext, template: str, language: str,
                 w_genre: float, w_related: float, w_global: float, w_mood: float,
                 allowed_pos: set[str] | None, rng: random.Random) -> str:
    """Stage 3: fill one template's slots -> title-cased title."""
    parts = parse_template(template)
    needed = [v for k, v in parts if k == "slot"]
    if allowed_pos is not None and any(n not in allowed_pos for n in needed):
        raise GenerationError(f"Template needs disabled word types: {template}")
    pools: dict[str, list] = {}
    for slot in set(needed):
        pool = words_repo.pool_words(conn, language, slot, ctx.genre_id, ctx.related_ids,
                                     w_genre, w_related, w_global,
                                     allowed_pos, ctx.artist_boost, ctx.mood_boost, w_mood)
        if not pool:
            pool = words_repo.pool_words(conn, language, slot, None, [], 0, 0, 1.0,
                                         allowed_pos, None, ctx.mood_boost, w_mood)
        if not pool:
            raise GenerationError(f"No enabled {slot}s are available for this genre.")
        pools[slot] = pool
    pieces = []
    for kind, val in parts:
        if kind == "literal":
            pieces.append(("lit", val, None))
        else:
            pieces.append(("slot", val, _pick_word(pools[val], rng)))
    noun_metas = [(w, g, n) for k, s, m in pieces if k == "slot" and s == "noun" for (w, g, n) in [m]]
    first_noun = noun_metas[0] if noun_metas else (None, None, None)
    rendered: list[str] = []
    for kind, slot_or_lit, meta in pieces:
        if kind == "lit":
            rendered.append(slot_or_lit)
        else:
            w, g, n = meta
            if language == "es" and slot_or_lit == "adjective" and first_noun[0]:
                _, w = agree_pair(first_noun[0], w, first_noun[1], first_noun[2])
            rendered.append(w)
    return title_case(" ".join(rendered), language)


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
