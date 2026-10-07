"""Words tab reloader (with language/type/search filters)."""
from __future__ import annotations

from PySide6.QtWidgets import QTableWidgetItem


def reload_words(conn, tab) -> None:
    from app.database.repositories import words as w
    lang = tab["lang"].currentText()
    pos = tab["pos"].currentText()
    rows = w.search_words(
        conn,
        "" if lang == "All" else lang,
        "" if pos == "All" else pos,
        None,
        tab["search"].text().strip(),
        limit=800,
    )
    tab["table"].setColumnCount(5)
    tab["table"].setHorizontalHeaderLabels(["Word", "Lang", "Type", "Weight", "Genres"])
    tab["table"].setRowCount(len(rows))
    tab["ids"] = [r["id"] for r in rows]
    for i, r in enumerate(rows):
        tab["table"].setItem(i, 0, QTableWidgetItem(r["word"]))
        tab["table"].setItem(i, 1, QTableWidgetItem(r["language"]))
        tab["table"].setItem(i, 2, QTableWidgetItem(r["part_of_speech"]))
        tab["table"].setItem(i, 3, QTableWidgetItem(str(r["weight"])))
        tab["table"].setItem(i, 4, QTableWidgetItem(r["genre_names"] or "global"))
