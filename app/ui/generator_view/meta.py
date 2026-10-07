"""Result-card subline: 'Genre · Language [+ moods]' + newline + 'a × b'."""
from __future__ import annotations


def meta_text(genre: str, lang_label: str, moods: list[str], artists: list[str], empty: str) -> str:
    head = f"{genre} · {lang_label}"
    if moods:
        head += f" · {' + '.join(moods)}"
    artists_txt = " × ".join(artists) if artists else empty
    return f"{head}\n{artists_txt}"
