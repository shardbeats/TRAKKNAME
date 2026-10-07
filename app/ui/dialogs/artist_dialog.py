"""Artist CRUD dialog (region is informational, pools filter by language)."""
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


class ArtistDialog(QDialog):
    REGIONS = ["", "US", "UK", "Canada", "LATAM", "Caribbean", "Spain", "Africa", "Europe", "Other"]

    def __init__(self, parent, conn, aid: int | None = None):
        super().__init__(parent)
        self.conn = conn
        self.aid = aid
        self.setWindowTitle("Artist")
        self.setMinimumWidth(420)
        self.name = QLineEdit()
        self.enabled = make_enabled_checkbox()
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
        self.genre_list, self._spins = make_weight_rows(
            [(g["id"], g["name"]) for g in genres], existing, step=0.5)
        lay.addWidget(self.genre_list)
        lay.addWidget(make_ok_cancel(self))

    def accept(self):
        from app.database.repositories import artists as a
        weights = {gid: s.value() for gid, s in self._spins.items()}
        try:
            a.save_artist(self.conn, self.name.text(), weights, self.enabled.isChecked(), self.aid,
                          self.region.currentText() or None, self.language.currentText() or None)
        except Exception as e:
            show_validation_error(self, str(e))
            return
        super().accept()
