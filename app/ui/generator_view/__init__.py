"""Generator section (backwards-compat package).

``from app.ui.generator_view import GeneratorView, meta_text`` keeps working;
implementation lives in ``view.py`` / ``presenter.py`` / ``meta.py``.
"""
from __future__ import annotations

from app.ui.generator_view.meta import meta_text
from app.ui.generator_view.presenter import GeneratorOptions, GeneratorPresenter
from app.ui.generator_view.view import GeneratorView

__all__ = ["GeneratorOptions", "GeneratorPresenter", "GeneratorView", "meta_text"]
