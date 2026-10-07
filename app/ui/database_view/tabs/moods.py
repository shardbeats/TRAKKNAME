"""Moods tab reloader."""
from __future__ import annotations

from PySide6.QtWidgets import QTableWidgetItem


def reload_moods(conn, tab) -> None:
    from app.database.repositories import moods as m
    try:
        rows = list(m.list_moods(conn))
    except Exception:
        rows = []
    tab["table"].setColumnCount(4)
    tab["table"].setHorizontalHeaderLabels(["Icon", "Name", "Vibe words", "Enabled"])
    tab["table"].setRowCount(len(rows))
    tab["ids"] = [r["id"] for r in rows]
    for i, r in enumerate(rows):
        try:
            n = m.word_count_for_mood(conn, r["id"])
        except Exception:
            n = 0
        tab["table"].setItem(i, 0, QTableWidgetItem(r["icon"] or ""))
        tab["table"].setItem(i, 1, QTableWidgetItem(r["name"]))
        tab["table"].setItem(i, 2, QTableWidgetItem(str(n)))
        tab["table"].setItem(i, 3, QTableWidgetItem("Yes" if r["enabled"] else "No"))
