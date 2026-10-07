"""Database section shell: utility bar + tabbed CRUD tables.

Each tab's reload logic lives in ``app.ui.database_view.tabs.*``;
CRUD dispatch in ``crud.py``; file actions in ``io_actions.py``.
This module only wires layout + delegation.
"""
from __future__ import annotations

from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QTableWidget,
    QVBoxLayout,
    QWidget,
)

from app.ui.database_view import crud
from app.ui.database_view import io_actions
from app.ui.database_view.tabs import artists, genres, moods, patterns, words


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

    # ---- reload (delegates per tab) ----
    def reload_all(self):
        conn = self._db()
        try:
            genres.reload_genres(conn, self.genre_tab)
            artists.reload_artists(conn, self.artist_tab)
            words.reload_words(conn, self.word_tab)
            patterns.reload_patterns(conn, self.pattern_tab)
            moods.reload_moods(conn, self.mood_tab)
        finally:
            conn.close()

    # Backward-compat shims (old private methods now delegate).
    def _reload_genres(self, conn):
        genres.reload_genres(conn, self.genre_tab)

    def _reload_artists(self, conn):
        artists.reload_artists(conn, self.artist_tab)

    def _reload_words(self, conn):
        words.reload_words(conn, self.word_tab)

    def _reload_patterns(self, conn):
        patterns.reload_patterns(conn, self.pattern_tab)

    def _reload_moods(self, conn):
        moods.reload_moods(conn, self.mood_tab)

    # ---- crud (delegates to crud.py) ----
    def _selected_id(self, info) -> int | None:
        return crud.selected_id(info)

    def _add(self, info):
        conn = self._db()
        try:
            dlg = crud.make_dialog(info, self, conn, None)
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
            dlg = crud.make_dialog(info, self, conn, _id)
            if dlg.exec():
                self.reload_all()
        finally:
            conn.close()

    def _dialog(self, info, conn, _id):
        return crud.make_dialog(info, self, conn, _id)

    def _delete(self, info):
        _id = self._selected_id(info)
        if _id is None:
            return
        if QMessageBox.question(self, "Delete", "Delete selected item?") != QMessageBox.Yes:
            return
        conn = self._db()
        try:
            crud.delete_by_kind(conn, info["kind"], _id)
        finally:
            conn.close()
        self.reload_all()

    # ---- import/export (delegates to io_actions.py) ----
    def export_db(self):
        io_actions.export_database_action(self, self.db_path)

    def import_db(self):
        io_actions.import_database_action(self, self.db_path, self.reload_all)

    def reset_db(self):
        io_actions.reset_database_action(self, self.db_path, self.reload_all)
