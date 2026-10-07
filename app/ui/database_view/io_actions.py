"""Import/export/reset actions for DatabaseView (Qt file dialogs + service calls)."""
from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import QFileDialog, QMessageBox, QWidget


def export_database_action(parent: QWidget, db_path) -> None:
    from app.database.connection import get_connection
    from app.services.import_export import export_database
    path, _ = QFileDialog.getSaveFileName(parent, "Export database", "trakkname_backup.json", "JSON (*.json)")
    if not path:
        return
    conn = get_connection(db_path)
    try:
        export_database(conn, Path(path))
    except Exception as e:
        QMessageBox.warning(parent, "Export failed", str(e))
        return
    finally:
        conn.close()
    QMessageBox.information(parent, "Export", "Database exported.")


def import_database_action(parent: QWidget, db_path, on_done) -> None:
    from app.database.connection import get_connection
    from app.services.import_export import import_database
    path, _ = QFileDialog.getOpenFileName(parent, "Import database", "", "JSON (*.json)")
    if not path:
        return
    if QMessageBox.question(parent, "Import", "Replace current database with imported file?") != QMessageBox.Yes:
        return
    conn = get_connection(db_path)
    try:
        import_database(conn, Path(path))
    except Exception as e:
        QMessageBox.warning(parent, "Import failed", str(e))
        return
    finally:
        conn.close()
    on_done()
    QMessageBox.information(parent, "Import", "Database imported.")


def reset_database_action(parent: QWidget, db_path, on_done) -> None:
    if QMessageBox.question(parent, "Reset", "Delete all data and restore seed data?") != QMessageBox.Yes:
        return
    from app.services.import_export import reset_database
    reset_database(Path(db_path))
    on_done()
