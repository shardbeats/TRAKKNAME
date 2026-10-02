"""Collapsible mood sidebar (TRAKKOUT family: sidebar frame + real collapse).

Multi-select up to 2 moods (store-taxonomy best practice). Empty = any mood.
"""
from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (QFrame, QHBoxLayout, QLabel, QLineEdit, QListWidget,
                               QListWidgetItem, QPushButton, QVBoxLayout, QWidget)

MAX_SELECTION = 2


class MoodSidebar(QFrame):
    moods_changed = Signal(list)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self._order: list[str] = []  # check order, oldest first
        self._updating = False
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(6)

        top = QHBoxLayout()
        top.setContentsMargins(0, 0, 0, 0)
        self.toggle_btn = QPushButton("<<")
        self.toggle_btn.setObjectName("sidebarToggle")
        self.toggle_btn.setFixedWidth(30)
        self.toggle_btn.setToolTip("Collapse sidebar")
        self.toggle_btn.clicked.connect(self.toggle_collapsed)
        self.title = QLabel("MOOD")
        self.title.setObjectName("sectionTitle")
        top.addWidget(self.title, 1)
        top.addWidget(self.toggle_btn)
        root.addLayout(top)

        self.content = QWidget()
        cl = QVBoxLayout(self.content)
        cl.setContentsMargins(0, 0, 0, 0)
        cl.setSpacing(6)

        hint_row = QHBoxLayout()
        hint = QLabel("Empty = any")
        hint.setObjectName("moodHint")
        self.count = QLabel("")
        self.count.setObjectName("moodCount")
        hint_row.addWidget(hint, 1)
        hint_row.addWidget(self.count)
        cl.addLayout(hint_row)

        self.search = QLineEdit()
        self.search.setPlaceholderText("Search moods…")
        self.search.textChanged.connect(self._apply_filter)
        cl.addWidget(self.search)

        self.list = QListWidget()
        self.list.setObjectName("moodList")
        self.list.itemChanged.connect(self._on_item_changed)
        cl.addWidget(self.list, 1)

        clear_row = QHBoxLayout()
        clear_row.addStretch(1)
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.clicked.connect(self.clear_selection)
        clear_row.addWidget(self.clear_btn)
        cl.addLayout(clear_row)

        root.addWidget(self.content, 1)

    # ---- data ----
    def set_moods(self, rows, selected: list[str] | None = None) -> None:
        """rows: sqlite rows with name/icon/description. Preserves selection."""
        keep = set(selected if selected is not None else self.selected())
        self._updating = True
        try:
            self.list.clear()
            self._order = []
            for r in rows:
                name = r["name"]
                icon = r["icon"] or ""
                item = QListWidgetItem(f"{icon}  {name}" if icon else name)
                item.setData(Qt.UserRole, name)
                item.setToolTip(r["description"] or "")
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                item.setCheckState(Qt.Checked if name in keep else Qt.Unchecked)
                if name in keep:
                    self._order.append(name)
                self.list.addItem(item)
        finally:
            self._updating = False
        self._apply_filter(self.search.text())
        self._refresh_count()

    def selected(self) -> list[str]:
        return list(self._order)

    def set_selected(self, names: list[str]) -> None:
        want = [n for n in names if n][:MAX_SELECTION]
        self._updating = True
        try:
            self._order = []
            for i in range(self.list.count()):
                item = self.list.item(i)
                on = item.data(Qt.UserRole) in want
                item.setCheckState(Qt.Checked if on else Qt.Unchecked)
                if on:
                    self._order.append(item.data(Qt.UserRole))
        finally:
            self._updating = False
        self._refresh_count()

    def clear_selection(self) -> None:
        self.set_selected([])
        self.moods_changed.emit([])

    # ---- collapse ----
    def is_collapsed(self) -> bool:
        return not self.content.isVisible()

    def set_collapsed(self, collapsed: bool) -> None:
        self.content.setVisible(not collapsed)
        self.title.setVisible(not collapsed)
        self.toggle_btn.setText(">>" if collapsed else "<<")
        self.toggle_btn.setToolTip("Expand sidebar" if collapsed else "Collapse sidebar")
        self.setFixedWidth(44 if collapsed else 205)

    def toggle_collapsed(self) -> None:
        self.set_collapsed(not self.is_collapsed())

    # ---- internals ----
    def _on_item_changed(self, item: QListWidgetItem) -> None:
        if self._updating:
            return
        name = item.data(Qt.UserRole)
        if item.checkState() == Qt.Checked:
            if name not in self._order:
                self._order.append(name)
            while len(self._order) > MAX_SELECTION:
                oldest = self._order.pop(0)
                self._uncheck(oldest)
        else:
            if name in self._order:
                self._order.remove(name)
        self._refresh_count()
        self.moods_changed.emit(list(self._order))

    def _uncheck(self, name: str) -> None:
        self._updating = True
        try:
            for i in range(self.list.count()):
                item = self.list.item(i)
                if item.data(Qt.UserRole) == name:
                    item.setCheckState(Qt.Unchecked)
                    break
        finally:
            self._updating = False

    def _apply_filter(self, text: str) -> None:
        q = (text or "").strip().lower()
        for i in range(self.list.count()):
            item = self.list.item(i)
            item.setHidden(bool(q) and q not in item.data(Qt.UserRole).lower())

    def _refresh_count(self) -> None:
        n = len(self._order)
        self.count.setText(f"{n}/{MAX_SELECTION}" if n else "")
