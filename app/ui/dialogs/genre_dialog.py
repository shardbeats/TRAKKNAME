"""Genre CRUD dialog."""
from __future__ import annotations

from PySide6.QtWidgets import QDialog, QFormLayout, QLineEdit

from app.ui.dialogs.base import (
    make_enabled_checkbox,
    make_ok_cancel,
    show_validation_error,
)


class GenreDialog(QDialog):
    def __init__(self, parent, conn, gid: int | None = None):
        super().__init__(parent)
        self.conn = conn
        self.gid = gid
        self.setWindowTitle("Genre")
        self.name = QLineEdit()
        self.desc = QLineEdit()
        self.enabled = make_enabled_checkbox()
        form = QFormLayout(self)
        form.addRow("Name", self.name)
        form.addRow("Description", self.desc)
        form.addRow(self.enabled)
        form.addWidget(make_ok_cancel(self))
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
            show_validation_error(self, str(e))
            return
        super().accept()
