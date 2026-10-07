"""Shared helpers for CRUD dialogs (validation + weight rows)."""
from __future__ import annotations

from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QWidget,
)


def show_validation_error(parent: QWidget, msg: str) -> None:
    QMessageBox.warning(parent, "Validation", msg)


def make_enabled_checkbox(checked: bool = True) -> QCheckBox:
    cb = QCheckBox("Enabled")
    cb.setChecked(checked)
    return cb


def make_ok_cancel(dlg: QDialog) -> QDialogButtonBox:
    btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
    btns.accepted.connect(dlg.accept)
    btns.rejected.connect(dlg.reject)
    return btns


def make_weight_rows(
    items: list[tuple[int, str]],
    existing: dict[int, float],
    step: float = 1.0,
) -> tuple[QListWidget, dict[int, QDoubleSpinBox]]:
    """Label + spin rows for genre/mood weights. Returns (list, {id: spin})."""
    lst = QListWidget()
    spins: dict[int, QDoubleSpinBox] = {}
    for _id, name in items:
        row = QWidget()
        hl = QHBoxLayout(row)
        hl.setContentsMargins(0, 0, 0, 0)
        lbl = QLabel(name)
        lbl.setMinimumWidth(160)
        spin = QDoubleSpinBox()
        spin.setRange(0, 10)
        spin.setSingleStep(step)
        spin.setValue(existing.get(_id, 0.0))
        spins[_id] = spin
        hl.addWidget(lbl)
        hl.addWidget(spin)
        item = QListWidgetItem()
        item.setSizeHint(row.sizeHint())
        lst.addItem(item)
        lst.setItemWidget(item, row)
    return lst, spins


# Backwards-compat aliases (old private names used inside dialogs).
_err = show_validation_error
_enabled_checkbox = make_enabled_checkbox
_ok_cancel = make_ok_cancel
_weight_rows = make_weight_rows
