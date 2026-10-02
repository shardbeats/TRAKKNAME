"""Generator view — the visual focal point. Hierarchy: title > generate > genre > artists."""
from __future__ import annotations

import random

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QGuiApplication
from PySide6.QtWidgets import (QCheckBox, QComboBox, QFrame, QHBoxLayout, QLabel,
                               QPushButton, QSizePolicy, QSlider, QSpinBox,
                               QVBoxLayout, QWidget)

from app.generator.engine import select_artists
from app.models.enums import ARTIST_POOLS, LANGUAGE_LABELS, POOL_EMPTY_TEXT
from app.ui.widgets import ChipRow, SectionTitle, Toast
from app.utils.logging import get_logger


def meta_text(genre: str, lang_label: str, moods: list[str], artists: list[str], empty: str) -> str:
    """Result-card subline: 'Genre · Language [+ moods]' + newline + 'a × b'."""
    head = f"{genre} · {lang_label}"
    if moods:
        head += f" · {' + '.join(moods)}"
    artists_txt = " × ".join(artists) if artists else empty
    return f"{head}\n{artists_txt}"


class GeneratorView(QWidget):
    def __init__(self, service, settings, on_generated=None):
        super().__init__()
        self.service = service
        self.settings = settings
        self.on_generated = on_generated
        self.current_title = ""
        self._build()
        self.refresh_options()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(18, 14, 18, 10)
        root.setSpacing(10)

        top = QHBoxLayout()
        genre_box = QVBoxLayout()
        genre_box.addWidget(SectionTitle("Genre"))
        self.genre_combo = QComboBox()
        self.genre_combo.setEditable(True)
        self.genre_combo.setInsertPolicy(QComboBox.NoInsert)
        self.genre_combo.setMinimumWidth(280)
        genre_box.addWidget(self.genre_combo)
        top.addLayout(genre_box, 3)

        lang_box = QVBoxLayout()
        lang_box.addWidget(SectionTitle("Language"))
        self.lang_combo = QComboBox()
        for code, label in LANGUAGE_LABELS.items():
            self.lang_combo.addItem(label, code)
        lang_box.addWidget(self.lang_combo)
        top.addLayout(lang_box, 2)

        count_box = QVBoxLayout()
        count_box.addWidget(SectionTitle("Artists per generation"))
        self.count_spin = QSpinBox()
        self.count_spin.setRange(1, 5)
        count_box.addWidget(self.count_spin)
        top.addLayout(count_box, 1)

        pool_box = QVBoxLayout()
        pool_box.addWidget(SectionTitle("Artist pool"))
        self.pool_combo = QComboBox()
        for code, label in ARTIST_POOLS.items():
            self.pool_combo.addItem(label, code)
        self.pool_combo.setToolTip("Filter artists by region/language")
        pool_box.addWidget(self.pool_combo)
        top.addLayout(pool_box, 2)
        root.addLayout(top)

        art_row = QHBoxLayout()
        art_row.addWidget(SectionTitle("Artists"))
        self.reroll_btn = QPushButton("Re-roll")
        self.reroll_btn.setToolTip("Re-roll artists only (keeps the title)")
        art_row.addWidget(self.reroll_btn)
        art_row.addStretch(1)
        self.influence_label = QLabel("Artist influence")
        self.influence_label.setStyleSheet("color:#92959A;font-size:11px;")
        art_row.addWidget(self.influence_label)
        self.influence_slider = QSlider(Qt.Horizontal)
        self.influence_slider.setRange(0, 100)
        self.influence_slider.setFixedWidth(130)
        art_row.addWidget(self.influence_slider)
        root.addLayout(art_row)
        self.chips = ChipRow()
        root.addWidget(self.chips)

        # Result card
        self.card = QFrame()
        self.card.setObjectName("resultCard")
        self.card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        cl = QVBoxLayout(self.card)
        cl.setContentsMargins(20, 26, 20, 26)
        self.result_label = QLabel("Press Generate")
        self.result_label.setObjectName("resultTitle")
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.result_label.setWordWrap(True)
        cl.addWidget(self.result_label)
        self.meta_label = QLabel("")
        self.meta_label.setObjectName("resultMeta")
        self.meta_label.setAlignment(Qt.AlignCenter)
        cl.addWidget(self.meta_label)
        root.addWidget(self.card, 1)

        btn_row = QHBoxLayout()
        btn_row.addStretch(1)
        self.generate_btn = QPushButton("GENERATE")
        self.generate_btn.setObjectName("accentButton")
        self.generate_btn.setMinimumWidth(220)
        self.generate_btn.setCursor(Qt.PointingHandCursor)
        self.copy_btn = QPushButton("Copy")
        self.copy_btn.setMinimumWidth(120)
        btn_row.addWidget(self.generate_btn)
        btn_row.addWidget(self.copy_btn)
        btn_row.addStretch(1)
        root.addLayout(btn_row)

        # Style + word options
        opt = QHBoxLayout()
        style_box = QVBoxLayout()
        style_box.addWidget(SectionTitle("Generation Style"))
        style_row = QHBoxLayout()
        self.style_combo = QComboBox()
        style_row.addWidget(self.style_combo, 1)
        self.single_btn = QPushButton("1-WORD")
        self.single_btn.setObjectName("singleBtn")
        self.single_btn.setCheckable(True)
        self.single_btn.setToolTip("Single-word titles: one noun only (Ctrl+1)")
        style_row.addWidget(self.single_btn)
        style_box.addLayout(style_row)
        opt.addLayout(style_box, 2)
        words_box = QVBoxLayout()
        words_box.addWidget(SectionTitle("Words"))
        wr = QHBoxLayout()
        self.cb_verbs = QCheckBox("Verbs")
        self.cb_adj = QCheckBox("Adjectives")
        self.cb_nouns = QCheckBox("Nouns")
        wr.addWidget(self.cb_verbs)
        wr.addWidget(self.cb_adj)
        wr.addWidget(self.cb_nouns)
        wr.addStretch(1)
        words_box.addLayout(wr)
        opt.addLayout(words_box, 2)
        root.addLayout(opt)

        self.toast = Toast(self)
        self.chips.chip_clicked.connect(lambda text: self.toast.show_toast(f"{text} copied!"))

        # signals
        self.generate_btn.clicked.connect(self.do_generate)
        self.copy_btn.clicked.connect(self.do_copy)
        self.genre_combo.currentIndexChanged.connect(self._preview_artists)
        self.count_spin.valueChanged.connect(lambda _: self._preview_artists())
        self.pool_combo.currentIndexChanged.connect(self._on_pool_changed)
        self.lang_combo.currentIndexChanged.connect(self._on_language_changed)
        self.reroll_btn.clicked.connect(self._reroll_artists)
        self.single_btn.toggled.connect(self._on_single_toggled)

        self.gen_act = QAction(self)
        self.gen_act.setShortcut("Space")
        self.gen_act.triggered.connect(self.do_generate)
        self.addAction(self.gen_act)
        single_act = QAction(self)
        single_act.setShortcut("Ctrl+1")
        single_act.triggered.connect(lambda: self.single_btn.toggle())
        self.addAction(single_act)
        copy_act = QAction(self)
        copy_act.setShortcut("Ctrl+C")
        copy_act.triggered.connect(self.do_copy)
        self.addAction(copy_act)

    # ---- data ----
    def _db(self):
        from app.database.connection import get_connection
        return get_connection(self.service.db_path)

    def refresh_options(self):
        s = self.settings.data
        conn = self._db()
        try:
            genres = [r["name"] for r in conn.execute("SELECT name FROM genres WHERE enabled=1 ORDER BY name")]
            cur = self.genre_combo.currentText()
            self.genre_combo.clear()
            self.genre_combo.addItems(genres)
            target = cur or s.get("default_genre", "Trap")
            idx = self.genre_combo.findText(target)
            if idx >= 0:
                self.genre_combo.setCurrentIndex(idx)
            lang = s.get("default_language", "en")
            self.lang_combo.setCurrentIndex(0 if lang == "en" else 1)
            self.count_spin.setValue(int(s.get("artists_per_generation", 2)))
            self.influence_slider.setValue(int(float(s.get("artist_influence", 0.5)) * 100))
            self.cb_verbs.setChecked(bool(s.get("use_verbs", True)))
            self.cb_adj.setChecked(bool(s.get("use_adjectives", True)))
            self.cb_nouns.setChecked(bool(s.get("use_nouns", True)))
            # styles (linked to the active language: only applicable ones)
            self._reload_styles(self.lang_combo.currentData() or "en",
                                keep=s.get("default_style", "Random"))
            self.single_btn.setChecked(bool(s.get("single_word", False)))
            self.style_combo.setEnabled(not self.single_btn.isChecked())
            pool = s.get("artist_pool", "all")
            pi = self.pool_combo.findData(pool)
            self.pool_combo.setCurrentIndex(pi if pi >= 0 else 0)
        finally:
            conn.close()
        self._preview_artists()

    def _reload_styles(self, lang: str, keep: str | None = None) -> None:
        """Refill the style combo with Random + patterns for `lang` only."""
        conn = self._db()
        try:
            rows = conn.execute(
                "SELECT name FROM patterns WHERE enabled = 1 AND language IN ('any', ?) ORDER BY name",
                (lang,)).fetchall()
        finally:
            conn.close()
        want = keep if keep is not None else self.style_combo.currentText()
        if not want:
            want = self.settings.data.get("default_style", "Random")
        try:
            from app.database.seed import STYLE_RENAMES
            want = STYLE_RENAMES.get(want, want)
        except Exception:
            pass
        self.style_combo.clear()
        self.style_combo.addItem("Random")
        for r in rows:
            self.style_combo.addItem(r["name"])
        i = self.style_combo.findText(want)
        self.style_combo.setCurrentIndex(i if i >= 0 else 0)

    def _on_language_changed(self) -> None:
        lang = self.lang_combo.currentData() or "en"
        self._reload_styles(lang)
        # pool follows language (en <-> English, es <-> En español);
        # user can still override it manually afterwards.
        pi = self.pool_combo.findData(lang if lang in ("en", "es") else "all")
        if pi >= 0:
            self.pool_combo.setCurrentIndex(pi)  # fires _on_pool_changed
        else:
            self._persist_opts()

    def _current_opts(self):
        return {
            "genre": self.genre_combo.currentText().strip(),
            "language": self.lang_combo.currentData(),
            "artist_count": self.count_spin.value(),
            "style": self.style_combo.currentText(),
            "single_word": self.single_btn.isChecked(),
            "artist_pool": self.pool_combo.currentData() or "all",
        }

    def _persist_opts(self):
        o = self._current_opts()
        self.settings.data.update({
            "default_genre": o["genre"], "default_language": o["language"],
            "artists_per_generation": o["artist_count"], "default_style": o["style"],
            "artist_influence": self.influence_slider.value() / 100.0,
            "use_verbs": self.cb_verbs.isChecked(), "use_adjectives": self.cb_adj.isChecked(),
            "use_nouns": self.cb_nouns.isChecked(),
            "single_word": self.single_btn.isChecked(),
            "artist_pool": o["artist_pool"],
        })
        self.settings.save()

    def _on_single_toggled(self, checked: bool) -> None:
        self.style_combo.setEnabled(not checked)
        self._persist_opts()

    def _on_pool_changed(self) -> None:
        self._persist_opts()
        self._preview_artists()

    def _fetch_artists(self) -> tuple[list[str], dict]:
        """Weighted artist pick for the current opts (preview AND re-roll)."""
        o = self._current_opts()
        conn = self._db()
        try:
            grow = conn.execute("SELECT id FROM genres WHERE name=?", (o["genre"],)).fetchone()
            gid = grow["id"] if grow else None
            pool = o["artist_pool"] if o["artist_pool"] != "all" else None
            return select_artists(conn, gid, o["artist_count"], random.Random(), pool), o
        finally:
            conn.close()

    def _preview_artists(self):
        names, o = self._fetch_artists()
        self.chips.set_chips(names, POOL_EMPTY_TEXT.get(o["artist_pool"], POOL_EMPTY_TEXT["all"]))

    def _reroll_artists(self) -> None:
        """New weighted artist pick for the CURRENT title (no regeneration)."""
        names, o = self._fetch_artists()
        empty = POOL_EMPTY_TEXT.get(o["artist_pool"], POOL_EMPTY_TEXT["all"])
        self.chips.set_chips(names, empty)
        if self.current_title:
            self.meta_label.setText(meta_text(
                o["genre"], LANGUAGE_LABELS.get(o["language"], o["language"]),
                self.settings.data.get("selected_moods", []), names, empty))

    def do_generate(self):
        self._persist_opts()
        o = self._current_opts()
        try:
            res = self.service.generate(genre=o["genre"] or None, language=o["language"],
                                        artist_count=o["artist_count"], style=o["style"],
                                        single_word=o["single_word"], artist_pool=o["artist_pool"])
        except Exception as e:
            get_logger().exception("generation failed")
            self.result_label.setText("Unable to generate")
            self.meta_label.setText(str(e))
            return
        self.current_title = res.title
        self.result_label.setText(res.title.upper())
        lang_label = LANGUAGE_LABELS.get(res.language, res.language)
        self.meta_label.setText(meta_text(
            res.genre_name, lang_label, res.moods, res.artists,
            POOL_EMPTY_TEXT.get(o["artist_pool"], POOL_EMPTY_TEXT["all"])))
        self.chips.set_chips(res.artists, POOL_EMPTY_TEXT.get(o["artist_pool"], POOL_EMPTY_TEXT["all"]))
        if self.on_generated:
            self.on_generated()

    def do_copy(self):
        text = self.current_title or self.result_label.text()
        if not text or text == "Press Generate":
            return
        QGuiApplication.clipboard().setText(text)
        self.toast.show_toast("Copied!")
