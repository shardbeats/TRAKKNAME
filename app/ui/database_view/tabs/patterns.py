"""Patterns tab reloader."""
from __future__ import annotations

from PySide6.QtWidgets import QTableWidgetItem


def reload_patterns(conn, tab) -> None:
    rows = list(conn.execute("SELECT * FROM patterns ORDER BY language, weight DESC"))
    tab["table"].setColumnCount(4)
    tab["table"].setHorizontalHeaderLabels(["Name", "Lang", "Template", "Weight"])
    tab["table"].setRowCount(len(rows))
    tab["ids"] = [r["id"] for r in rows]
    for i, r in enumerate(rows):
        tab["table"].setItem(i, 0, QTableWidgetItem(r["name"]))
        tab["table"].setItem(i, 1, QTableWidgetItem(r["language"]))
        tab["table"].setItem(i, 2, QTableWidgetItem(r["template"]))
        tab["table"].setItem(i, 3, QTableWidgetItem(str(r["weight"])))
