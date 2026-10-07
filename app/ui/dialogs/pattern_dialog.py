"""Pattern CRUD dialog."""
from __future__ import annotations

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDoubleSpinBox,
    QFormLayout,
    QLineEdit,
)

from app.ui.dialogs.base import (
    make_enabled_checkbox,
    make_ok_cancel,
    show_validation_error,
)


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
        self.enabled = make_enabled_checkbox()
        form = QFormLayout(self)
        form.addRow("Name", self.name)
        form.addRow("Language", self.lang)
        form.addRow("Template", self.template)
        form.addRow("Weight", self.weight)
        form.addRow(self.enabled)
        form.addWidget(make_ok_cancel(self))
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
            show_validation_error(self, str(e))
            return
        super().accept()
