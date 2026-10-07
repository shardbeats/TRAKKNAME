"""Result card widget (title + meta subline)."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QLabel, QSizePolicy, QVBoxLayout


class ResultCard(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("resultCard")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(20, 26, 20, 26)
        self.title_label = QLabel("Press Generate")
        self.title_label.setObjectName("resultTitle")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.title_label.setWordWrap(True)
        lay.addWidget(self.title_label)
        self.meta_label = QLabel("")
        self.meta_label.setObjectName("resultMeta")
        self.meta_label.setAlignment(Qt.AlignCenter)
        lay.addWidget(self.meta_label)

    def set_title(self, text: str) -> None:
        self.title_label.setText(text)

    def set_meta(self, text: str) -> None:
        self.meta_label.setText(text)

    def title_text(self) -> str:
        return self.title_label.text()
