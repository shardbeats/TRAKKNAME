"""Main window: header + tabbed sections. Ctrl+H / Ctrl+, / Ctrl+Shift+D shortcuts."""
from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (QHBoxLayout, QLabel, QMainWindow, QTabWidget,
                               QVBoxLayout, QWidget)

from app.ui.database_view import DatabaseView
from app.ui.generator_view import GeneratorView
from app.ui.history_view import HistoryView
from app.ui.mood_sidebar import MoodSidebar
from app.ui.settings_view import SettingsView
from app.ui.theme import apply_theme

APP_TITLE = "TRAKKNAME"


class MainWindow(QMainWindow):
    def __init__(self, service, settings, db_path):
        super().__init__()
        self.service = service
        self.settings = settings
        self.db_path = db_path
        self.setWindowTitle(APP_TITLE)
        self.setMinimumSize(900, 620)
        s = settings.data
        self.resize(int(s.get("window_width", 980)), int(s.get("window_height", 720)))
        apply_theme(self)
        self._build()
        self._shortcuts()

    def _build(self):
        central = QWidget()
        central.setObjectName("central")
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        # header
        header = QWidget()
        hl = QHBoxLayout(header)
        hl.setContentsMargins(18, 12, 18, 10)
        icon = QLabel()
        icon.setObjectName("headerIcon")
        try:
            from PySide6.QtGui import QPixmap
            _icon_path = Path(__file__).resolve().parent.parent / "resources" / "trakkname.png"
            if _icon_path.exists():
                icon.setPixmap(QPixmap(str(_icon_path)).scaledToHeight(22, Qt.SmoothTransformation))
        except Exception:
            pass
        title = QLabel(APP_TITLE)
        title.setObjectName("appTitle")
        hl.addWidget(icon)
        hl.addWidget(title)
        hl.addStretch(1)
        hint = QLabel("Space = Generate")
        hint.setObjectName("headerHint")
        hl.addWidget(hint)
        root.addWidget(header)
        # tabs + mood sidebar
        body = QWidget()
        body_layout = QHBoxLayout(body)
        body_layout.setContentsMargins(10, 6, 10, 10)
        body_layout.setSpacing(10)
        self.sidebar = MoodSidebar()
        self.sidebar.moods_changed.connect(self._on_moods_changed)
        self.sidebar.toggle_btn.clicked.connect(self._persist_sidebar)
        body_layout.addWidget(self.sidebar)
        self.tabs = QTabWidget()
        self.generator = GeneratorView(self.service, self.settings, on_generated=self._on_generated)
        self.database = DatabaseView(self.db_path)
        self.history = HistoryView(self.db_path)
        self.settings_view = SettingsView(self.settings, on_changed=self._on_settings_changed)
        self.tabs.addTab(self.generator, "GENERATOR")
        self.tabs.addTab(self.database, "DATABASE")
        self.tabs.addTab(self.history, "HISTORY")
        self.tabs.addTab(self.settings_view, "SETTINGS")
        body_layout.addWidget(self.tabs, 1)
        root.addWidget(body, 1)
        self.statusBar().showMessage(f"Database: {self.db_path}")
        self._load_sidebar()

    def _db(self):
        from app.database.connection import get_connection
        return get_connection(self.db_path)

    def _load_sidebar(self):
        from app.database.repositories import moods as moods_repo
        conn = self._db()
        try:
            rows = moods_repo.list_moods(conn, only_enabled=True)
        finally:
            conn.close()
        self.sidebar.set_moods(rows, self.settings.data.get("selected_moods", []))
        self.sidebar.set_collapsed(bool(self.settings.data.get("sidebar_collapsed", False)))

    def _on_moods_changed(self, names: list[str]):
        self.settings.data["selected_moods"] = names
        self.settings.save()
        if names:
            self.statusBar().showMessage(f"Mood: {' + '.join(names)}", 4000)
        else:
            self.statusBar().showMessage("Mood: any", 4000)

    def _persist_sidebar(self):
        self.settings.data["sidebar_collapsed"] = self.sidebar.is_collapsed()
        self.settings.save()

    def _on_generated(self):
        self.history.reload()
        try:
            t = self.generator.current_title
            if t:
                self.statusBar().showMessage(f"Generated: {t}", 4000)
        except Exception:
            pass

    def _on_settings_changed(self):
        self.generator.refresh_options()

    def _shortcuts(self):
        def go(idx: int):
            self.tabs.setCurrentIndex(idx)
        for seq, idx in [("Ctrl+H", 2), ("Ctrl+,", 3)]:
            act = QAction(self)
            act.setShortcut(seq)
            act.triggered.connect(lambda _=False, i=idx: go(i))
            self.addAction(act)
        db_act = QAction(self)
        db_act.setShortcut("Ctrl+Shift+D")
        db_act.triggered.connect(lambda: go(1))
        self.addAction(db_act)

    def closeEvent(self, event):
        self.settings.data["window_width"] = self.width()
        self.settings.data["window_height"] = self.height()
        try:
            self.settings.save()
        except Exception:
            pass
        super().closeEvent(event)
