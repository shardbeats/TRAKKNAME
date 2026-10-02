"""Seed data: Generation patterns (curated set + retired + renames)."""
from __future__ import annotations


PATTERNS: list[tuple[str, str, str, float]] = [
    # Concise curated set: 2-word shapes dominate (the classic beat-title
    # form), one 3-word shape each. Single words live ONLY in the 1-WORD
    # toggle (engine falls back to a lone NOUN template when no NOUN-only
    # pattern exists), never as style options.
    ("Adj + Noun", "en", "ADJ NOUN", 10),
    ("Noun + Noun", "en", "NOUN NOUN", 5),
    ("Verb + Noun", "en", "VERB NOUN", 3),
    ("Noun of Noun", "en", "NOUN of NOUN", 2),
    ("Sustantivo + Adjetivo", "es", "NOUN ADJ", 10),
    ("Adjetivo + Sustantivo", "es", "ADJ NOUN", 6),
    ("Sustantivo de Sustantivo", "es", "NOUN de NOUN", 4),
    ("Verbo + Sustantivo", "es", "VERB NOUN", 3),
]

# Single-word patterns removed from the options (2026-10-02): the 1-WORD
# toggle is the only single-word path. Deleted from existing DBs by
# ensure_patterns (not merely disabled).
REMOVED_PATTERNS: list[str] = [
    "Single Noun",
    "Una Palabra",
    "Single Noun (ES)",  # legacy pre-rename variant
]

# Old ES names -> new Spanish names (one-time rename of seed rows).


# Old ES names -> new Spanish names (one-time rename of seed rows).
STYLE_RENAMES: dict[str, str] = {
    "Adj + Noun (ES)": "Adjetivo + Sustantivo",
    "Noun + Adj (ES)": "Sustantivo + Adjetivo",
    "Noun de Noun": "Sustantivo de Sustantivo",
    "Verb + Noun (ES)": "Verbo + Sustantivo",
    "Single Noun (ES)": "Una Palabra",
}

# Patterns retired from the curated set (kept in DB, auto-disabled;
# user can re-enable in Database -> Patterns).


# Patterns retired from the curated set (kept in DB, auto-disabled;
# user can re-enable in Database -> Patterns).
RETIRED_PATTERNS: list[str] = [
    "Adj Adj Noun",
    "Verb Adj Noun",
    "Lost + Noun",
    "The + Adj + Noun",
    "Noun After Noun",
    "Adj Dreams",
    "Noun Nights",
    "Noun + Noun (ES)",
    "Los + Noun",
    "La + Noun",
]
