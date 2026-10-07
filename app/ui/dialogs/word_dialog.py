"""Word CRUD dialog (genre weights + mood weights)."""
from __future__ import annotations

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDoubleSpinBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QVBoxLayout,
)

from app.ui.dialogs.base import (
    make_enabled_checkbox,
    make_ok_cancel,
    make_weight_rows,
    show_validation_error,
)


class WordDialog(QDialog):
    def __init__(self, parent, conn, wid: int | None = None):
        super().__init__(parent)
        self.conn = conn
        self.wid = wid
        self.setWindowTitle("Word")
        self.setMinimumWidth(420)
        self.word = QLineEdit()
        self.lang = QComboBox()
        self.lang.addItems(["en", "es"])
        self.pos = QComboBox()
        self.pos.addItems(["verb", "adjective", "noun"])
        self.weight = QDoubleSpinBox()
        self.weight.setRange(0, 10)
        self.weight.setValue(1.0)
        self.enabled = make_enabled_checkbox()
        self.gender = QComboBox()
        self.gender.addItems(["", "masculine", "feminine", "neutral"])
        self.number = QComboBox()
        self.number.addItems(["", "singular", "plural"])
        genres = conn.execute("SELECT id, name FROM genres ORDER BY name").fetchall()
        self._spins: dict[int, QDoubleSpinBox] = {}
        self._mood_spins: dict[int, QDoubleSpinBox] = {}
        existing: dict[int, float] = {}
        existing_moods: dict[int, float] = {}
        try:
            moods = conn.execute("SELECT id, name FROM moods ORDER BY name").fetchall()
        except Exception:
            moods = []
        self._moods = moods
        if wid:
            r = conn.execute("SELECT * FROM words WHERE id=?", (wid,)).fetchone()
            self.word.setText(r["word"])
            self.lang.setCurrentText(r["language"])
            self.pos.setCurrentText(r["part_of_speech"])
            self.weight.setValue(float(r["weight"]))
            self.enabled.setChecked(bool(r["enabled"]))
            if r["gender"]:
                self.gender.setCurrentText(r["gender"])
            if r["number"]:
                self.number.setCurrentText(r["number"])
            for x in conn.execute("SELECT genre_id, weight FROM word_genres WHERE word_id=?", (wid,)):
                existing[x["genre_id"]] = x["weight"]
            try:
                for x in conn.execute("SELECT mood_id, weight FROM word_moods WHERE word_id=?", (wid,)):
                    existing_moods[x["mood_id"]] = x["weight"]
            except Exception:
                pass
        lay = QVBoxLayout(self)
        form = QFormLayout()
        form.addRow("Word", self.word)
        form.addRow("Language", self.lang)
        form.addRow("Part of speech", self.pos)
        form.addRow("Weight", self.weight)
        form.addRow("Gender (ES nouns)", self.gender)
        form.addRow("Number (ES nouns)", self.number)
        form.addRow(self.enabled)
        lay.addLayout(form)
        lay.addWidget(QLabel("Genre weights (0 = global pool)"))
        self.genre_list, self._spins = make_weight_rows(
            [(g["id"], g["name"]) for g in genres], existing)
        self.genre_list.setMaximumHeight(180)
        lay.addWidget(self.genre_list)
        if moods:
            lay.addWidget(QLabel("Mood weights (0 = no boost)"))
            self.mood_list, self._mood_spins = make_weight_rows(
                [(m["id"], m["name"]) for m in moods], existing_moods)
            self.mood_list.setMaximumHeight(150)
            lay.addWidget(self.mood_list)
        lay.addWidget(make_ok_cancel(self))

    def accept(self):
        from app.database.repositories import words as w
        weights = {gid: s.value() for gid, s in self._spins.items()}
        mood_weights = {mid: s.value() for mid, s in self._mood_spins.items()}
        try:
            w.save_word(self.conn, self.word.text(), self.lang.currentText(), self.pos.currentText(),
                        self.weight.value(), self.enabled.isChecked(),
                        self.gender.currentText() or None, self.number.currentText() or None,
                        weights, self.wid, mood_weights)
        except Exception as e:
            show_validation_error(self, str(e))
            return
        super().accept()
