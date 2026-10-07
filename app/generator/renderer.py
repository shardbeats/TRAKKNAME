"""Stage 3: fill one template's slots -> title-cased title."""
from __future__ import annotations

import random
import sqlite3

from app.database.repositories import words as words_repo
from app.generator import weighted_random as wr
from app.generator.grammar import agree_pair
from app.generator.results import GenContext, GenerationError
from app.generator.templates import parse_template
from app.utils.text import title_case


def pick_word(pool: list[tuple[str, str | None, str | None, float]], rng: random.Random) -> tuple[str, str | None, str | None]:
    if not pool:
        raise GenerationError("No words available in pool.")
    words = [p[0] for p in pool]
    weights = [p[3] for p in pool]
    idx = wr.choose_weighted(list(range(len(words))), weights, rng)
    w, g, n, _ = pool[int(idx)]
    return w, g, n


def render_title(conn: sqlite3.Connection, ctx: GenContext, template: str, language: str,
                 w_genre: float, w_related: float, w_global: float, w_mood: float,
                 allowed_pos: set[str] | None, rng: random.Random) -> str:
    """Fill one template's slots -> title-cased title."""
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
            pieces.append(("slot", val, pick_word(pools[val], rng)))
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


# Backwards-compat alias.
_pick_word = pick_word
