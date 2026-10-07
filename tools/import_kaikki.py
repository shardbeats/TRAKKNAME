"""Enrich the word database from kaikki.org Wiktionary dumps (streaming, low RAM).

Thin CLI wrapper: implementation lives in ``tools/kaikki/``
(``constants`` / ``filters`` / ``db`` / ``collect`` / ``cli``).
Usage stays identical: ``python tools/import_kaikki.py --lang es --dry-run``.
"""
from __future__ import annotations

from tools.kaikki.cli import build_parser, main, run
from tools.kaikki.collect import collect
from tools.kaikki.constants import FILES, LANG_CODE, MAX_LEN, MIN_LEN, POS_MAP, STALE_TAGS, TOKEN_RE, TOXIC_TAGS
from tools.kaikki.db import load_db_words
from tools.kaikki.filters import entry_ok, es_gender_number, is_form_of, is_stale, relations, structural_ok

__all__ = [
    "FILES", "LANG_CODE", "MAX_LEN", "MIN_LEN", "POS_MAP", "STALE_TAGS", "TOKEN_RE", "TOXIC_TAGS",
    "build_parser", "collect", "entry_ok", "es_gender_number", "is_form_of", "is_stale",
    "load_db_words", "main", "relations", "run", "structural_ok",
]

if __name__ == "__main__":
    raise SystemExit(main())
