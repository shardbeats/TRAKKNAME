"""Application theme (external QSS so it can be tweaked without touching code).

Same pattern as TRAKKOUT: app/ui/style.qss is the source of truth.
"""
from __future__ import annotations

from pathlib import Path


def load_stylesheet() -> str:
    """Read style.qss next to this module. Empty if missing."""
    qss = Path(__file__).with_name("style.qss")
    try:
        if qss.exists():
            return qss.read_text(encoding="utf-8")
    except OSError:
        pass
    return ""


def apply_theme(app_or_widget) -> None:
    css = load_stylesheet()
    if css:
        try:
            app_or_widget.setStyleSheet(css)
        except Exception:
            pass
