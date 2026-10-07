"""Database section (backwards-compat package).

``from app.ui.database_view import DatabaseView`` keeps working;
implementation lives in ``view.py`` with tabs in ``tabs/``.
"""
from __future__ import annotations

from app.ui.database_view.view import DatabaseView

__all__ = ["DatabaseView"]
