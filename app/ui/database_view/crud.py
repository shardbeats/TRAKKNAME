"""CRUD dispatch for DatabaseView tabs (dialog factory + delete)."""
from __future__ import annotations


def make_dialog(info, parent, conn, _id):
    from app.ui.dialogs import ArtistDialog, GenreDialog, MoodDialog, PatternDialog, WordDialog
    kind = info["kind"]
    if kind == "genres":
        return GenreDialog(parent, conn, _id)
    if kind == "artists":
        return ArtistDialog(parent, conn, _id)
    if kind == "words":
        return WordDialog(parent, conn, _id)
    if kind == "moods":
        return MoodDialog(parent, conn, _id)
    return PatternDialog(parent, conn, _id)


def delete_by_kind(conn, kind: str, _id: int) -> None:
    from app.database.repositories import artists as artists_repo
    from app.database.repositories import genres as genres_repo
    from app.database.repositories import moods as moods_repo
    from app.database.repositories import patterns as patterns_repo
    from app.database.repositories import words as words_repo
    if kind == "genres":
        genres_repo.delete_genre(conn, _id)
    elif kind == "artists":
        artists_repo.delete_artist(conn, _id)
    elif kind == "words":
        words_repo.delete_word(conn, _id)
    elif kind == "moods":
        moods_repo.delete_mood(conn, _id)
    else:
        patterns_repo.delete_pattern(conn, _id)


def selected_id(info) -> int | None:
    row = info["table"].currentRow()
    if row < 0 or row >= len(info["ids"]):
        return None
    return info["ids"][row]
