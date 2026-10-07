"""Mood CRUD dialog."""
from __future__ import annotations

from PySide6.QtWidgets import QDialog, QFormLayout, QLineEdit

from app.ui.dialogs.base import (
    make_enabled_checkbox,
    make_ok_cancel,
    show_validation_error,
)


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
        self.enabled = make_enabled_checkbox()
        form = QFormLayout(self)
        form.addRow("Name (English tag)", self.name)
        form.addRow("Description", self.desc)
        form.addRow("Icon", self.icon)
        form.addRow(self.enabled)
        form.addWidget(make_ok_cancel(self))
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
            show_validation_error(self, str(e))
            return
        super().accept()
