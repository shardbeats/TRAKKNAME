"""Entry point: init dirs, logging, DB+seed, settings, launch UI."""
from __future__ import annotations

import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.database.startup import ensure_database
from app.services.generation_service import GenerationService
from app.services.settings_service import SettingsService
from app.ui.main_window import MainWindow
from app.utils import logging as applog
from app.utils.paths import get_app_dir, get_db_path, get_log_dir, get_settings_path


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
