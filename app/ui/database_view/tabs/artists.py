"""Artists tab reloader."""
from __future__ import annotations

from PySide6.QtWidgets import QTableWidgetItem


def reload_artists(conn, tab) -> None:
    try:
        rows = list(conn.execute("SELECT * FROM artists ORDER BY name"))
        has_meta = "region" in rows[0].keys() if rows else True
    except Exception:
        rows = list(conn.execute("SELECT id, name, enabled FROM artists ORDER BY name"))
        has_meta = False
    tab["table"].setColumnCount(5)
    tab["table"].setHorizontalHeaderLabels(["Name", "Genres", "Region", "Lang", "Enabled"])
    tab["table"].setRowCount(len(rows))
    tab["ids"] = [r["id"] for r in rows]
    for i, r in enumerate(rows):
        links = conn.execute(
            "SELECT g.name, ag.weight FROM artist_genres ag "
            "JOIN genres g ON g.id=ag.genre_id WHERE ag.artist_id=? ORDER BY ag.weight DESC",
            (r["id"],),
        ).fetchall()
        txt = ", ".join(f"{x['name']} ({x['weight']:g})" for x in links)
        tab["table"].setItem(i, 0, QTableWidgetItem(r["name"]))
        tab["table"].setItem(i, 1, QTableWidgetItem(txt))
        try:
            region = r["region"] or "—" if has_meta else "—"
            lang = r["language"] or "en" if has_meta else "en"
        except Exception:
            region, lang = "—", "en"
        tab["table"].setItem(i, 2, QTableWidgetItem(region))
        tab["table"].setItem(i, 3, QTableWidgetItem(lang))
        tab["table"].setItem(i, 4, QTableWidgetItem("Yes" if r["enabled"] else "No"))
