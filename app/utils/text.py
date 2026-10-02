"""Small text helpers: normalization, title-casing."""
from __future__ import annotations

import re


def normalize_title(title: str) -> str:
    """Lowercase + collapse whitespace for duplicate comparison."""
    return " ".join(title.lower().split())


def title_case(title: str, language: str = "en") -> str:
    """Title-case each word; keep small Spanish connectors lowercase mid-title."""
    words = " ".join(title.split()).split(" ")
    if not words:
        return title
    if language == "es":
        lower_keep = {"de", "la", "los", "las", "el", "y", "en"}
        out = [words[0].capitalize()]
        for w in words[1:]:
            out.append(w.lower() if w.lower() in lower_keep else w.capitalize())
        return " ".join(out)
    return " ".join(w.capitalize() for w in words)


def slug_words(text: str) -> list[str]:
    return re.findall(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+", text)
