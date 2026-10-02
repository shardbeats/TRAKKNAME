"""Database section: Genres / Artists / Words / Patterns tabs with filters + import/export."""
from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import (QComboBox, QFileDialog, QHBoxLayout, QLineEdit,
                               QMessageBox, QPushButton, QTabWidget, QTableWidget,
                               QTableWidgetItem, QVBoxLayout, QWidget)

from app.ui.dialogs import ArtistDialog, GenreDialog, MoodDialog, PatternDialog, WordDialog


class DatabaseView(QWidget):
    def __init__(self, db_path):
        super().__init__()
        self.db_path = db_path
        self._build()
        self.reload_all()

    def _db(self):
        from app.database.connection import get_connection
        return get_connection(self.db_path)

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(18, 14, 18, 14)
        # utility bar
        bar = QHBoxLayout()
        bar.addStretch(1)
        self.export_btn = QPushButton("Export Database")
        self.import_btn = QPushButton("Import Database")
        self.reset_btn = QPushButton("Reset Seed Data")
        for b in (self.export_btn, self.import_btn, self.reset_btn):
            bar.addWidget(b)
        root.addLayout(bar)
        self.tabs = QTabWidget()
        root.addWidget(self.tabs)
        self.genre_tab = self._make_tab("genres")
        self.artist_tab = self._make_tab("artists")
        self.word_tab = self._make_tab("words", with_filters=True)
        self.pattern_tab = self._make_tab("patterns")
        self.mood_tab = self._make_tab("moods")
        self.tabs.addTab(self.genre_tab["root"], "Genres")
        self.tabs.addTab(self.artist_tab["root"], "Artists")
        self.tabs.addTab(self.word_tab["root"], "Words")
        self.tabs.addTab(self.pattern_tab["root"], "Patterns")
        self.tabs.addTab(self.mood_tab["root"], "Moods")
        self.export_btn.clicked.connect(self.export_db)
        self.import_btn.clicked.connect(self.import_db)
        self.reset_btn.clicked.connect(self.reset_db)

    def _make_tab(self, kind: str, with_filters: bool = False):
        root = QWidget()
        lay = QVBoxLayout(root)
        if with_filters:
            # Words filters: language + type + text. (No genre filter: only a
            # handful of words carry genre links — the rest is global pool —
            # so it almost always shows an empty list.)
            fbar = QHBoxLayout()
            lang = QComboBox()
            lang.addItems(["All", "en", "es"])
            pos = QComboBox()
            pos.addItems(["All", "verb", "adjective", "noun"])
            search = QLineEdit()
            search.setPlaceholderText("Search…")
            fbar.addWidget(lang)
            fbar.addWidget(pos)
            fbar.addWidget(search, 1)
            lay.addLayout(fbar)
        else:
            lang = pos = search = None
        table = QTableWidget(0, 4)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        lay.addWidget(table)
        brow = QHBoxLayout()
        add_btn = QPushButton("Add")
        edit_btn = QPushButton("Edit")
        del_btn = QPushButton("Delete")
        brow.addStretch(1)
        brow.addWidget(add_btn)
        brow.addWidget(edit_btn)
        brow.addWidget(del_btn)
        lay.addLayout(brow)
        info = {"root": root, "table": table, "add": add_btn, "edit": edit_btn, "del": del_btn,
                "lang": lang, "pos": pos, "search": search, "kind": kind, "ids": []}
        add_btn.clicked.connect(lambda: self._add(info))
        edit_btn.clicked.connect(lambda: self._edit(info))
        del_btn.clicked.connect(lambda: self._delete(info))
        if with_filters:
            for w in (lang, pos, search):
                if isinstance(w, QLineEdit):
                    w.textChanged.connect(lambda _: self.reload_all())
                else:
                    w.currentIndexChanged.connect(lambda _: self.reload_all())
        table.doubleClicked.connect(lambda _: self._edit(info))
        return info

    # ---- reload ----
    def reload_all(self):
        conn = self._db()
        try:
            self._reload_genres(conn)
            self._reload_artists(conn)
            self._reload_words(conn)
            self._reload_patterns(conn)
            self._reload_moods(conn)
        finally:
            conn.close()

    def _reload_genres(self, conn):
        t = self.genre_tab
        rows = list(conn.execute("SELECT * FROM genres ORDER BY name"))
        t["table"].setColumnCount(3)
        t["table"].setHorizontalHeaderLabels(["Name", "Description", "Enabled"])
        t["table"].setRowCount(len(rows))
        t["ids"] = [r["id"] for r in rows]
        for i, r in enumerate(rows):
            t["table"].setItem(i, 0, QTableWidgetItem(r["name"]))
            t["table"].setItem(i, 1, QTableWidgetItem(r["description"] or ""))
            t["table"].setItem(i, 2, QTableWidgetItem("Yes" if r["enabled"] else "No"))

    def _reload_artists(self, conn):
        t = self.artist_tab
        try:
            rows = list(conn.execute("SELECT * FROM artists ORDER BY name"))
            has_meta = "region" in rows[0].keys() if rows else True
        except Exception:
            rows = list(conn.execute("SELECT id, name, enabled FROM artists ORDER BY name"))
            has_meta = False
        t["table"].setColumnCount(5)
        t["table"].setHorizontalHeaderLabels(["Name", "Genres", "Region", "Lang", "Enabled"])
        t["table"].setRowCount(len(rows))
        t["ids"] = [r["id"] for r in rows]
        for i, r in enumerate(rows):
            links = conn.execute("SELECT g.name, ag.weight FROM artist_genres ag JOIN genres g ON g.id=ag.genre_id WHERE ag.artist_id=? ORDER BY ag.weight DESC", (r["id"],)).fetchall()
            txt = ", ".join(f"{x['name']} ({x['weight']:g})" for x in links)
            t["table"].setItem(i, 0, QTableWidgetItem(r["name"]))
            t["table"].setItem(i, 1, QTableWidgetItem(txt))
            try:
                region = r["region"] or "—" if has_meta else "—"
                lang = r["language"] or "en" if has_meta else "en"
            except Exception:
                region, lang = "—", "en"
            t["table"].setItem(i, 2, QTableWidgetItem(region))
            t["table"].setItem(i, 3, QTableWidgetItem(lang))
            t["table"].setItem(i, 4, QTableWidgetItem("Yes" if r["enabled"] else "No"))

    def _reload_words(self, conn):
        from app.database.repositories import words as w
        t = self.word_tab
        lang = t["lang"].currentText()
        pos = t["pos"].currentText()
        rows = w.search_words(conn, "" if lang == "All" else lang, "" if pos == "All" else pos, None, t["search"].text().strip(), limit=800)
        t["table"].setColumnCount(5)
        t["table"].setHorizontalHeaderLabels(["Word", "Lang", "Type", "Weight", "Genres"])
        t["table"].setRowCount(len(rows))
        t["ids"] = [r["id"] for r in rows]
        for i, r in enumerate(rows):
            t["table"].setItem(i, 0, QTableWidgetItem(r["word"]))
            t["table"].setItem(i, 1, QTableWidgetItem(r["language"]))
            t["table"].setItem(i, 2, QTableWidgetItem(r["part_of_speech"]))
            t["table"].setItem(i, 3, QTableWidgetItem(str(r["weight"])))
            t["table"].setItem(i, 4, QTableWidgetItem(r["genre_names"] or "global"))

    def _reload_patterns(self, conn):
        t = self.pattern_tab
        rows = list(conn.execute("SELECT * FROM patterns ORDER BY language, weight DESC"))
        t["table"].setColumnCount(4)
        t["table"].setHorizontalHeaderLabels(["Name", "Lang", "Template", "Weight"])
        t["table"].setRowCount(len(rows))
        t["ids"] = [r["id"] for r in rows]
        for i, r in enumerate(rows):
            t["table"].setItem(i, 0, QTableWidgetItem(r["name"]))
            t["table"].setItem(i, 1, QTableWidgetItem(r["language"]))
            t["table"].setItem(i, 2, QTableWidgetItem(r["template"]))
            t["table"].setItem(i, 3, QTableWidgetItem(str(r["weight"])))

    def _reload_moods(self, conn):
        from app.database.repositories import moods as m
        t = self.mood_tab
        try:
            rows = list(m.list_moods(conn))
        except Exception:
            rows = []
        t["table"].setColumnCount(4)
        t["table"].setHorizontalHeaderLabels(["Icon", "Name", "Vibe words", "Enabled"])
        t["table"].setRowCount(len(rows))
        t["ids"] = [r["id"] for r in rows]
        for i, r in enumerate(rows):
            try:
                n = m.word_count_for_mood(conn, r["id"])
            except Exception:
                n = 0
            t["table"].setItem(i, 0, QTableWidgetItem(r["icon"] or ""))
            t["table"].setItem(i, 1, QTableWidgetItem(r["name"]))
            t["table"].setItem(i, 2, QTableWidgetItem(str(n)))
            t["table"].setItem(i, 3, QTableWidgetItem("Yes" if r["enabled"] else "No"))

    # ---- crud ----
    def _selected_id(self, info) -> int | None:
        row = info["table"].currentRow()
        if row < 0 or row >= len(info["ids"]):
            return None
        return info["ids"][row]

    def _add(self, info):
        conn = self._db()
        try:
            dlg = self._dialog(info, conn, None)
            if dlg.exec():
                self.reload_all()
        finally:
            conn.close()

    def _edit(self, info):
        _id = self._selected_id(info)
        if _id is None:
            return
        conn = self._db()
        try:
            dlg = self._dialog(info, conn, _id)
            if dlg.exec():
                self.reload_all()
        finally:
            conn.close()

    def _dialog(self, info, conn, _id):
        kind = info["kind"]
        if kind == "genres":
            return GenreDialog(self, conn, _id)
        if kind == "artists":
            return ArtistDialog(self, conn, _id)
        if kind == "words":
            return WordDialog(self, conn, _id)
        if kind == "moods":
            return MoodDialog(self, conn, _id)
        return PatternDialog(self, conn, _id)

    def _delete(self, info):
        _id = self._selected_id(info)
        if _id is None:
            return
        if QMessageBox.question(self, "Delete", "Delete selected item?") != QMessageBox.Yes:
            return
        from app.database.repositories import artists as artists_repo
        from app.database.repositories import genres as genres_repo
        from app.database.repositories import moods as moods_repo
        from app.database.repositories import patterns as patterns_repo
        from app.database.repositories import words as words_repo
        conn = self._db()
        try:
            kind = info["kind"]
            if kind == "genres":
                genres_repo.delete_genre(conn, _id)
            elif kind == "artists":
                artists_repo.delete_artist(conn, _id)
            elif kind == "words":
                words_repo.delete_word(conn, _id)
            elif kind == "moods":
                moods_repo.delete_mood(conn, _id)
            else:
                patterns_repo.delete_pattern(conn, _id)
        finally:
            conn.close()
        self.reload_all()

    # ---- import/export ----
    def export_db(self):
        from app.services.import_export import export_database
        from app.database.connection import get_connection
        path, _ = QFileDialog.getSaveFileName(self, "Export database", "trakkname_backup.json", "JSON (*.json)")
        if not path:
            return
        conn = get_connection(self.db_path)
        try:
            export_database(conn, Path(path))
        except Exception as e:
            QMessageBox.warning(self, "Export failed", str(e))
            return
        finally:
            conn.close()
        QMessageBox.information(self, "Export", "Database exported.")

    def import_db(self):
        from app.services.import_export import import_database
        from app.database.connection import get_connection
        path, _ = QFileDialog.getOpenFileName(self, "Import database", "", "JSON (*.json)")
        if not path:
            return
        if QMessageBox.question(self, "Import", "Replace current database with imported file?") != QMessageBox.Yes:
            return
        conn = get_connection(self.db_path)
        try:
            import_database(conn, Path(path))
        except Exception as e:
            QMessageBox.warning(self, "Import failed", str(e))
            return
        finally:
            conn.close()
        self.reload_all()
        QMessageBox.information(self, "Import", "Database imported.")

    def reset_db(self):
        if QMessageBox.question(self, "Reset", "Delete all data and restore seed data?") != QMessageBox.Yes:
            return
        from app.services.import_export import reset_database
        reset_database(Path(self.db_path))
        self.reload_all()
