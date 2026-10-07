"""Structural + relevance filters for kaikki.org entries."""
from __future__ import annotations

from tools.kaikki.constants import MAX_LEN, POS_MAP, STALE_TAGS, TOXIC_TAGS, TOKEN_RE


def is_form_of(sense: dict) -> bool:
    if "form_of" in sense:
        return True
    return "form-of" in (sense.get("tags") or [])


def is_stale(sense: dict) -> bool:
    tags = set(sense.get("tags") or [])
    return bool(tags & STALE_TAGS)


def structural_ok(word: str, pos: str, lang_code: str, min_len: int = 3) -> bool:
    if pos not in POS_MAP or lang_code not in ("en", "es"):
        return False
    if not word or word[0].isupper():
        return False
    if not (min_len <= len(word) <= MAX_LEN):
        return False
    return bool(TOKEN_RE.match(word))


def entry_ok(obj: dict) -> bool:
    """Reject form-of-only, archaic-only, and toxic (vulgar/offensive) entries."""
    senses = obj.get("senses") or []
    if not senses:
        return False
    if all(is_form_of(s) for s in senses):
        return False
    if all(is_stale(s) for s in senses):
        return False
    for s in senses:
        if TOXIC_TAGS & set(s.get("tags") or []):
            return False
    return True


def relations(obj: dict) -> set[str]:
    """Synonym/related/antonym headwords (same-language neighborhood)."""
    out: set[str] = set()
    fields = ("synonyms", "related", "antonyms")
    senses = obj.get("senses") or []
    pools: list[dict] = list(obj.get("synonyms") or []) + list(obj.get("related") or [])
    for s in senses:
        for f in fields:
            pools.extend(s.get(f) or [])
    for rel in pools:
        if isinstance(rel, dict) and rel.get("word"):
            out.add(str(rel["word"]).strip().lower())
    return out


def es_gender_number(obj: dict) -> tuple[str | None, str | None]:
    """Majority vote over non-form-of senses; None when ambiguous."""
    genders = [t for s in (obj.get("senses") or []) if not is_form_of(s)
               for t in (s.get("tags") or []) if t in ("masculine", "feminine")]
    numbers = [t for s in (obj.get("senses") or []) if not is_form_of(s)
               for t in (s.get("tags") or []) if t in ("singular", "plural")]
    gender = genders[0] if genders and all(g == genders[0] for g in genders) else None
    number = numbers[0] if numbers and all(n == numbers[0] for n in numbers) else None
    return gender, number
