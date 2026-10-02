"""Reusable widgets: chips, toast, section headers."""
from __future__ import annotations

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QHBoxLayout, QLabel, QWidget


class Chip(QLabel):
    def __init__(self, text: str, on_click=None):
        super().__init__(text)
        self.setObjectName("chip")
        self.setCursor(Qt.PointingHandCursor)
        self.setToolTip("Click to copy")
        self._on_click = on_click

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self._on_click:
            self._on_click(self.text())
        super().mousePressEvent(event)


class ChipRow(QWidget):
    chip_clicked = Signal(str)

    def __init__(self):
        super().__init__()
        self.layout_: QHBoxLayout = QHBoxLayout(self)
        self.layout_.setContentsMargins(0, 0, 0, 0)
        self.layout_.setSpacing(6)
        self.layout_.setAlignment(Qt.AlignLeft)

    def set_chips(self, items: list[str], empty_text: str = "No artists configured for this genre.") -> None:
        while self.layout_.count():
            w = self.layout_.takeAt(0).widget()
            if w:
                w.deleteLater()
        if not items:
            lbl = QLabel(empty_text)
            lbl.setObjectName("chipEmpty")
            self.layout_.addWidget(lbl)
            return
        for it in items:
            self.layout_.addWidget(Chip(it, on_click=self._copy_chip))

    def _copy_chip(self, text: str) -> None:
        QGuiApplication.clipboard().setText(text)
        self.chip_clicked.emit(text)


class SectionTitle(QLabel):
    def __init__(self, text: str):
        super().__init__(text.upper())
        self.setObjectName("sectionTitle")


class Toast(QLabel):
    def __init__(self, parent: QWidget):
        super().__init__("Copied!", parent)
        self.setObjectName("toast")
        self.setWindowFlags(Qt.SubWindow)
        self.hide()
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self.hide)

    def show_toast(self, text: str = "Copied!") -> None:
        self.setText(text)
        self.adjustSize()
        pw = self.parentWidget().width() if self.parentWidget() else 300
        self.move(max(0, pw // 2 - self.width() // 2), 10)
        self.show()
        self.raise_()
        self._timer.start(1400)
