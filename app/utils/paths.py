"""User data paths with full-portable mode.

Normal runs (source): ``%APPDATA%\\TRAKKNAME`` as before — never inside the repo.

Frozen runs (PyInstaller ``.exe``): **portable by default** — everything lives in
``<exe-dir>/data`` (``trakkname.db``, ``settings.json``, ``logs/``), so the app
can travel on a USB stick without leaving traces. Opt out with either:

- env ``TRAKKNAME_APPDATA=1``, or
- an empty file ``use_appdata.flag`` next to the ``.exe``.

Overrides (both modes): env ``TRAKKNAME_DATA_DIR`` points to a custom folder.

First launch in portable mode copies any existing ``%APPDATA%`` DB/settings
into ``data/`` once (never overwrites), plus the pre-rebrand
``BeatNameGenerator`` migration still applies to the APPDATA side.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

APP_NAME = "TRAKKNAME"
DB_FILENAME = "trakkname.db"
PORTABLE_DIRNAME = "data"
# Pre-rebrand location (auto-migrated on first launch, never overwritten).
LEGACY_APP_NAME = "BeatNameGenerator"
LEGACY_DB_FILENAME = "beat_names.db"


def is_frozen() -> bool:
    return bool(getattr(sys, "frozen", False))


def exe_dir() -> Path | None:
    if is_frozen():
        try:
            return Path(sys.executable).resolve().parent
        except Exception:
            return None
    return None


def is_portable_mode() -> bool:
    """True when a frozen app should keep data next to the .exe."""
    if os.environ.get("TRAKKNAME_DATA_DIR"):
        return True
    ed = exe_dir()
    if ed is None:
        return False
    if os.environ.get("TRAKKNAME_APPDATA") == "1":
        return False
    if (ed / "use_appdata.flag").exists():
        return False
    return True


def portable_dir() -> Path:
    ed = exe_dir()
    base = ed if ed is not None else Path.cwd()
    return base / PORTABLE_DIRNAME


def get_appdata_dir() -> Path:
    if os.name == "nt":
        base = os.environ.get("APPDATA") or str(Path.home() / "AppData" / "Roaming")
        p = Path(base) / APP_NAME
    else:
        p = Path.home() / f".{APP_NAME.lower()}"
    return p


def get_app_dir() -> Path:
    override = os.environ.get("TRAKKNAME_DATA_DIR")
    if override:
        p = Path(override).expanduser()
        p.mkdir(parents=True, exist_ok=True)
        (p / "logs").mkdir(parents=True, exist_ok=True)
        return p
    if is_portable_mode():
        p = portable_dir()
        p.mkdir(parents=True, exist_ok=True)
        (p / "logs").mkdir(parents=True, exist_ok=True)
        _migrate_appdata_to_portable(p)
        return p
    p = get_appdata_dir()
    p.mkdir(parents=True, exist_ok=True)
    (p / "logs").mkdir(parents=True, exist_ok=True)
    _migrate_legacy(p)
    return p


def _migrate_appdata_to_portable(portable: Path) -> None:
    """One-time copy %APPDATA% -> ./data (DB + settings), never overwrites."""
    try:
        src_dir = get_appdata_dir()
        for name in (DB_FILENAME, "settings.json"):
            src, dst = src_dir / name, portable / name
            if src.exists() and not dst.exists() and src.resolve() != dst.resolve():
                import shutil
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
    except Exception:
        pass


def _migrate_legacy(new_dir: Path) -> None:
    """One-time copy from the old BeatNameGenerator dir (DB + settings)."""
    try:
        if os.name == "nt":
            base = os.environ.get("APPDATA") or str(Path.home() / "AppData" / "Roaming")
            legacy = Path(base) / LEGACY_APP_NAME
        else:
            legacy = Path.home() / f".{LEGACY_APP_NAME.lower()}"
        pairs = [(legacy / LEGACY_DB_FILENAME, new_dir / DB_FILENAME),
                 (legacy / "settings.json", new_dir / "settings.json")]
        for src, dst in pairs:
            if src.exists() and not dst.exists():
                import shutil
                shutil.copy2(src, dst)
    except Exception:
        pass


def get_db_path() -> Path:
    return get_app_dir() / DB_FILENAME


def get_settings_path() -> Path:
    return get_app_dir() / "settings.json"


def get_log_dir() -> Path:
    d = get_app_dir() / "logs"
    d.mkdir(parents=True, exist_ok=True)
    return d
