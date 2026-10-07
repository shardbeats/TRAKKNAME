"""CRUD dialogs with inline validation.

Backwards-compat package: ``from app.ui.dialogs import X`` keeps working.
New code can import from ``app.ui.dialogs.<name>_dialog`` directly.
"""
from __future__ import annotations

from app.ui.dialogs.artist_dialog import ArtistDialog
from app.ui.dialogs.base import (
    make_enabled_checkbox,
    make_ok_cancel,
    make_weight_rows,
    show_validation_error,
)
from app.ui.dialogs.genre_dialog import GenreDialog
from app.ui.dialogs.mood_dialog import MoodDialog
from app.ui.dialogs.pattern_dialog import PatternDialog
from app.ui.dialogs.word_dialog import WordDialog

__all__ = [
    "ArtistDialog",
    "GenreDialog",
    "MoodDialog",
    "PatternDialog",
    "WordDialog",
    "make_enabled_checkbox",
    "make_ok_cancel",
    "make_weight_rows",
    "show_validation_error",
]

# Old private names (kept so external imports don't break).
_err = show_validation_error
_enabled_checkbox = make_enabled_checkbox
_ok_cancel = make_ok_cancel
_weight_rows = make_weight_rows
