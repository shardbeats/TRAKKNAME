from __future__ import annotations

import json

from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import (QHBoxLayout, QLineEdit, QMessageBox, QPushButton,
                               QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget)

from app.models.enums import ARTIST_POOLS, LEGACY_POOL_MAP


class HistoryView(QWidget):
    def __init__(self, db_path):
        super().__init__()
        self.db_path = db_path
        self._build()
        self.reload()

    def _db(self):
        from app.database.connection import get_connection
        return get_connection(self.db_path)

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(18, 14, 18, 14)
        bar = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search history…")
        self.search.textChanged.connect(lambda _: self.reload())
        bar.addWidget(self.search, 1)
        self.copy_btn = QPushButton("Copy")
        self.del_btn = QPushButton("Delete")
        self.clear_btn = QPushButton("Clear all")
        for b in (self.copy_btn, self.del_btn, self.clear_btn):
            bar.addWidget(b)
        root.addLayout(bar)
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["Title", "Genre", "Language", "Mood", "Pool", "Date"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.doubleClicked.connect(lambda _: self.copy_selected())
        root.addWidget(self.table)
        self.copy_btn.clicked.connect(self.copy_selected)
        self.del_btn.clicked.connect(self.delete_selected)
        self.clear_btn.clicked.connect(self.clear_all)

    def reload(self):
        from app.database.repositories import history as h
        conn = self._db()
        try:
            rows = h.list_history(conn, search=self.search.text().strip())
        finally:
            conn.close()
        self.table.setRowCount(len(rows))
        self._ids = [r["id"] for r in rows]
        for i, r in enumerate(rows):
            try:
                moods = json.loads(r["moods_json"] or "[]") if "moods_json" in r.keys() else []
            except Exception:
                moods = []
            try:
                pool = r["artist_pool"] or "all"
            except Exception:
                pool = "all"
            self.table.setItem(i, 0, QTableWidgetItem(r["title"]))
            self.table.setItem(i, 1, QTableWidgetItem(r["genre_name"] or ""))
            self.table.setItem(i, 2, QTableWidgetItem(r["language"] or ""))
            self.table.setItem(i, 3, QTableWidgetItem(" + ".join(moods)))
            self.table.setItem(i, 4, QTableWidgetItem(ARTIST_POOLS.get(LEGACY_POOL_MAP.get(pool, pool), pool)))
            self.table.setItem(i, 5, QTableWidgetItem(r["created_at"] or ""))

    def _selected_id(self):
        row = self.table.currentRow()
        if row < 0 or row >= len(self._ids):
            return None
        return self._ids[row]

    def copy_selected(self):
        row = self.table.currentRow()
        if row < 0:
            return
        QGuiApplication.clipboard().setText(self.table.item(row, 0).text())

    def delete_selected(self):
        from app.database.repositories import history as h
        hid = self._selected_id()
        if hid is None:
            return
        conn = self._db()
        try:
            h.delete_history(conn, hid)
        finally:
            conn.close()
        self.reload()

    def clear_all(self):
        from app.database.repositories import history as h
        if QMessageBox.question(self, "Clear history", "Delete all history?") != QMessageBox.Yes:
            return
        conn = self._db()
        try:
            h.clear_history(conn)
        finally:
            conn.close()
        self.reload()
