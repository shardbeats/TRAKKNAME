"""Simple settings form bound to SettingsService."""
from __future__ import annotations

from PySide6.QtWidgets import (QComboBox, QDoubleSpinBox, QFormLayout, QHBoxLayout,
                               QPushButton, QSpinBox, QVBoxLayout, QWidget)


class SettingsView(QWidget):
    def __init__(self, settings, on_changed=None):
        super().__init__()
        self.settings = settings
        self.on_changed = on_changed
        self._build()
        self.load()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(18, 14, 18, 14)
        form = QFormLayout()
        self.lang = QComboBox()
        self.lang.addItem("English", "en")
        self.lang.addItem("Spanish", "es")
        self.genre = QComboBox()
        self.genre.setEditable(True)
        self.artist_count = QSpinBox()
        self.artist_count.setRange(1, 5)
        self.recent = QSpinBox()
        self.recent.setRange(0, 1000)
        self.w_genre = QDoubleSpinBox()
        self.w_related = QDoubleSpinBox()
        self.w_global = QDoubleSpinBox()
        for w in (self.w_genre, self.w_related, self.w_global):
            w.setRange(0, 1)
            w.setSingleStep(0.05)
        self.w_mood = QDoubleSpinBox()
        self.w_mood.setRange(0, 3)
        self.w_mood.setSingleStep(0.25)
        self.w_mood.setToolTip("Mood word boost: 1.0 = mood words twice as likely")
        form.addRow("Default language", self.lang)
        form.addRow("Default genre", self.genre)
        form.addRow("Artists per generation", self.artist_count)
        form.addRow("Avoid last N titles", self.recent)
        form.addRow("Genre vocabulary weight", self.w_genre)
        form.addRow("Related genre weight", self.w_related)
        form.addRow("Global vocabulary weight", self.w_global)
        form.addRow("Mood influence", self.w_mood)
        root.addLayout(form)
        row = QHBoxLayout()
        self.save_btn = QPushButton("Save settings")
        self.save_btn.setObjectName("accentButton")
        row.addStretch(1)
        row.addWidget(self.save_btn)
        root.addLayout(row)
        root.addStretch(1)
        self.save_btn.clicked.connect(self.save)

    def load(self):
        from app.database.connection import get_connection
        s = self.settings.data
        self.lang.setCurrentIndex(0 if s.get("default_language") == "en" else 1)
        self.artist_count.setValue(int(s.get("artists_per_generation", 2)))
        self.recent.setValue(int(s.get("recent_exclusion_count", 100)))
        self.w_genre.setValue(float(s.get("w_genre", 0.70)))
        self.w_related.setValue(float(s.get("w_related", 0.20)))
        self.w_global.setValue(float(s.get("w_global", 0.10)))
        self.w_mood.setValue(float(s.get("w_mood", 1.0)))
        # genres for default
        try:
            conn = get_connection(self.settings.path.parent / "trakkname.db")
            genres = [r["name"] for r in conn.execute("SELECT name FROM genres ORDER BY name")]
            conn.close()
        except Exception:
            genres = ["Trap"]
        cur = self.genre.currentText()
        self.genre.clear()
        self.genre.addItems(genres)
        t = cur or s.get("default_genre", "Trap")
        i = self.genre.findText(t)
        if i >= 0:
            self.genre.setCurrentIndex(i)

    def save(self):
        self.settings.data.update({
            "default_language": self.lang.currentData(),
            "default_genre": self.genre.currentText().strip(),
            "artists_per_generation": self.artist_count.value(),
            "recent_exclusion_count": self.recent.value(),
            "w_genre": self.w_genre.value(),
            "w_related": self.w_related.value(),
            "w_global": self.w_global.value(),
            "w_mood": self.w_mood.value(),
        })
        self.settings.save()
        if self.on_changed:
            self.on_changed()
