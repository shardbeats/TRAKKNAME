"""CRUD dialogs with inline validation."""
from __future__ import annotations

from PySide6.QtWidgets import (QCheckBox, QComboBox, QDialog, QDialogButtonBox,
                               QDoubleSpinBox, QFormLayout, QHBoxLayout, QLabel,
                               QLineEdit, QListWidget, QListWidgetItem, QMessageBox,
                               QVBoxLayout, QWidget)


def _err(parent, msg: str):
    QMessageBox.warning(parent, "Validation", msg)


def _enabled_checkbox() -> QCheckBox:
    cb = QCheckBox("Enabled")
    cb.setChecked(True)
    return cb


def _ok_cancel(dlg: QDialog) -> QDialogButtonBox:
    btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
    btns.accepted.connect(dlg.accept)
    btns.rejected.connect(dlg.reject)
    return btns


def _weight_rows(items: list[tuple[int, str]], existing: dict[int, float],
                 step: float = 1.0) -> tuple[QListWidget, dict[int, QDoubleSpinBox]]:
    """Label + spin rows for genre/mood weights. Returns (list, {id: spin})."""
    lst = QListWidget()
    spins: dict[int, QDoubleSpinBox] = {}
    for _id, name in items:
        row = QWidget()
        hl = QHBoxLayout(row)
        hl.setContentsMargins(0, 0, 0, 0)
        lbl = QLabel(name)
        lbl.setMinimumWidth(160)
        spin = QDoubleSpinBox()
        spin.setRange(0, 10)
        spin.setSingleStep(step)
        spin.setValue(existing.get(_id, 0.0))
        spins[_id] = spin
        hl.addWidget(lbl)
        hl.addWidget(spin)
        item = QListWidgetItem()
        item.setSizeHint(row.sizeHint())
        lst.addItem(item)
        lst.setItemWidget(item, row)
    return lst, spins


class GenreDialog(QDialog):
    def __init__(self, parent, conn, gid: int | None = None):
        super().__init__(parent)
        self.conn = conn
        self.gid = gid
        self.setWindowTitle("Genre")
        self.name = QLineEdit()
        self.desc = QLineEdit()
        self.enabled = _enabled_checkbox()
        form = QFormLayout(self)
        form.addRow("Name", self.name)
        form.addRow("Description", self.desc)
        form.addRow(self.enabled)
        form.addWidget(_ok_cancel(self))
        if gid:
            r = conn.execute("SELECT * FROM genres WHERE id=?", (gid,)).fetchone()
            self.name.setText(r["name"])
            self.desc.setText(r["description"] or "")
            self.enabled.setChecked(bool(r["enabled"]))

    def accept(self):
        from app.database.repositories import genres as g
        try:
            if self.gid:
                g.update_genre(self.conn, self.gid, self.name.text(), self.desc.text(),
                               self.enabled.isChecked())
            else:
                g.upsert_genre(self.conn, self.name.text(), self.desc.text(), self.enabled.isChecked())
        except Exception as e:
            _err(self, str(e))
            return
        super().accept()


class ArtistDialog(QDialog):
    REGIONS = ["", "US", "UK", "Canada", "LATAM", "Caribbean", "Spain", "Africa", "Europe", "Other"]

    def __init__(self, parent, conn, aid: int | None = None):
        super().__init__(parent)
        self.conn = conn
        self.aid = aid
        self.setWindowTitle("Artist")
        self.setMinimumWidth(420)
        self.name = QLineEdit()
        self.enabled = _enabled_checkbox()
        self.region = QComboBox()
        self.region.addItems(self.REGIONS)
        self.region.setToolTip("Informational only — pools filter by language")
        self.language = QComboBox()
        self.language.addItems(["", "en", "es"])
        self.language.setToolTip("Empty = English")
        genres = conn.execute("SELECT id, name FROM genres ORDER BY name").fetchall()
        self._spins: dict[int, QDoubleSpinBox] = {}
        existing: dict[int, float] = {}
        if aid:
            r = conn.execute("SELECT * FROM artists WHERE id=?", (aid,)).fetchone()
            self.name.setText(r["name"])
            self.enabled.setChecked(bool(r["enabled"]))
            try:
                if r["region"]:
                    self.region.setCurrentText(r["region"])
                if r["language"]:
                    self.language.setCurrentText(r["language"])
            except Exception:
                pass
            for x in conn.execute("SELECT genre_id, weight FROM artist_genres WHERE artist_id=?", (aid,)):
                existing[x["genre_id"]] = x["weight"]
        lay = QVBoxLayout(self)
        form = QFormLayout()
        form.addRow("Name", self.name)
        form.addRow("Region", self.region)
        form.addRow("Language", self.language)
        form.addRow(self.enabled)
        lay.addLayout(form)
        lay.addWidget(QLabel("Genre weights (0 = not linked)"))
        self.genre_list, self._spins = _weight_rows(
            [(g["id"], g["name"]) for g in genres], existing, step=0.5)
        lay.addWidget(self.genre_list)
        lay.addWidget(_ok_cancel(self))

    def accept(self):
        from app.database.repositories import artists as a
        weights = {gid: s.value() for gid, s in self._spins.items()}
        try:
            a.save_artist(self.conn, self.name.text(), weights, self.enabled.isChecked(), self.aid,
                          self.region.currentText() or None, self.language.currentText() or None)
        except Exception as e:
            _err(self, str(e))
            return
        super().accept()


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
        self.enabled = _enabled_checkbox()
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
        self.genre_list, self._spins = _weight_rows(
            [(g["id"], g["name"]) for g in genres], existing)
        self.genre_list.setMaximumHeight(180)
        lay.addWidget(self.genre_list)
        if moods:
            lay.addWidget(QLabel("Mood weights (0 = no boost)"))
            self.mood_list, self._mood_spins = _weight_rows(
                [(m["id"], m["name"]) for m in moods], existing_moods)
            self.mood_list.setMaximumHeight(150)
            lay.addWidget(self.mood_list)
        lay.addWidget(_ok_cancel(self))

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
            _err(self, str(e))
            return
        super().accept()


class PatternDialog(QDialog):
    def __init__(self, parent, conn, pid: int | None = None):
        super().__init__(parent)
        self.conn = conn
        self.pid = pid
        self.setWindowTitle("Pattern")
        self.name = QLineEdit()
        self.lang = QComboBox()
        self.lang.addItems(["en", "es", "any"])
        self.template = QLineEdit()
        self.template.setPlaceholderText("e.g. ADJ NOUN / NOUN de NOUN")
        self.weight = QDoubleSpinBox()
        self.weight.setRange(0, 10)
        self.weight.setValue(1.0)
        self.enabled = _enabled_checkbox()
        form = QFormLayout(self)
        form.addRow("Name", self.name)
        form.addRow("Language", self.lang)
        form.addRow("Template", self.template)
        form.addRow("Weight", self.weight)
        form.addRow(self.enabled)
        form.addWidget(_ok_cancel(self))
        if pid:
            r = conn.execute("SELECT * FROM patterns WHERE id=?", (pid,)).fetchone()
            self.name.setText(r["name"])
            self.lang.setCurrentText(r["language"])
            self.template.setText(r["template"])
            self.weight.setValue(float(r["weight"]))
            self.enabled.setChecked(bool(r["enabled"]))

    def accept(self):
        from app.database.repositories import patterns as p
        try:
            p.save_pattern(self.conn, self.name.text(), self.lang.currentText(), self.template.text(),
                           self.weight.value(), self.enabled.isChecked(), self.pid)
        except Exception as e:
            _err(self, str(e))
            return
        super().accept()


class MoodDialog(QDialog):
    def __init__(self, parent, conn, mid: int | None = None):
        super().__init__(parent)
        self.conn = conn
        self.mid = mid
        self.setWindowTitle("Mood")
        self.setMinimumWidth(360)
        self.name = QLineEdit()
        self.desc = QLineEdit()
        self.icon = QLineEdit()
        self.icon.setMaxLength(4)
        self.icon.setPlaceholderText("optional")
        self.enabled = _enabled_checkbox()
        form = QFormLayout(self)
        form.addRow("Name (English tag)", self.name)
        form.addRow("Description", self.desc)
        form.addRow("Icon", self.icon)
        form.addRow(self.enabled)
        form.addWidget(_ok_cancel(self))
        if mid:
            r = conn.execute("SELECT * FROM moods WHERE id=?", (mid,)).fetchone()
            self.name.setText(r["name"])
            self.desc.setText(r["description"] or "")
            self.icon.setText(r["icon"] or "")
            self.enabled.setChecked(bool(r["enabled"]))

    def accept(self):
        from app.database.repositories import moods as m
        try:
            m.save_mood(self.conn, self.name.text(), self.desc.text(), self.icon.text(),
                        self.enabled.isChecked(), self.mid)
        except Exception as e:
            _err(self, str(e))
            return
        super().accept()
