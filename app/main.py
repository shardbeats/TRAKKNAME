"""Entry point: init dirs, logging, DB+seed, settings, launch UI."""
from __future__ import annotations

import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.database.connection import get_connection
from app.database.schema import create_schema, migrate_database
from app.database.seed import seed_database, seed_moods, ensure_artists, ensure_artist_meta, ensure_patterns, ensure_no_placeholders
from app.services.generation_service import GenerationService
from app.services.settings_service import SettingsService
from app.ui.main_window import MainWindow
from app.utils import logging as applog
from app.utils.paths import get_app_dir, get_db_path, get_log_dir, get_settings_path


def ensure_database(db_path: Path, logger) -> None:
    first = not db_path.exists()
    conn = get_connection(db_path)
    try:
        create_schema(conn)
        count = conn.execute("SELECT COUNT(*) c FROM genres").fetchone()["c"]
        if first or count == 0:
            logger.info("Seeding database (first launch)…")
            seed_database(conn)
            logger.info("Seed complete.")
        else:
            migrate_database(conn)
            seed_moods(conn)
            n = ensure_artists(conn)
            if n:
                logger.info("Added %d new seed artists.", n)
            ensure_artist_meta(conn)
            ensure_patterns(conn)
            n = ensure_no_placeholders(conn)
            if n:
                logger.info("Removed %d placeholder words.", n)
    finally:
        conn.close()


def main() -> int:
    get_app_dir()
    logger = applog.setup_logging(get_log_dir())
    try:
        db_path = get_db_path()
        ensure_database(db_path, logger)
        settings = SettingsService(get_settings_path())
        service = GenerationService(db_path, settings)
        from PySide6.QtWidgets import QApplication
        app = QApplication(sys.argv)
        app.setApplicationName("TRAKKNAME")
        for _icon in (Path(__file__).resolve().parent / "resources" / "trakkname.ico",
                      Path(__file__).resolve().parent / "resources" / "trakkname.png"):
            if _icon.exists():
                from PySide6.QtGui import QIcon
                app.setWindowIcon(QIcon(str(_icon)))
                break
        win = MainWindow(service, settings, str(db_path))
        win.show()
        return app.exec()
    except Exception as e:
        logger.exception("Fatal startup error")
        try:
            from PySide6.QtWidgets import QApplication, QMessageBox
            q = QApplication.instance() or QApplication(sys.argv)
            QMessageBox.critical(None, "TRAKKNAME", f"Unable to start the application.\n{e}\nSee logs for details.")
        except Exception:
            print(f"FATAL: {e}\n{traceback.format_exc()}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
