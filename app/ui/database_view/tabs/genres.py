"""Genres tab reloader."""
from __future__ import annotations

from PySide6.QtWidgets import QTableWidgetItem


def reload_genres(conn, tab) -> None:
    rows = list(conn.execute("SELECT * FROM genres ORDER BY name"))
    tab["table"].setColumnCount(3)
    tab["table"].setHorizontalHeaderLabels(["Name", "Description", "Enabled"])
    tab["table"].setRowCount(len(rows))
    tab["ids"] = [r["id"] for r in rows]
    for i, r in enumerate(rows):
        tab["table"].setItem(i, 0, QTableWidgetItem(r["name"]))
        tab["table"].setItem(i, 1, QTableWidgetItem(r["description"] or ""))
        tab["table"].setItem(i, 2, QTableWidgetItem("Yes" if r["enabled"] else "No"))
