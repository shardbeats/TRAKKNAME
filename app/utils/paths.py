"""User-specific paths. Never store user data inside the repo during normal use."""
from __future__ import annotations

import os
from pathlib import Path

APP_NAME = "TRAKKNAME"
DB_FILENAME = "trakkname.db"
# Pre-rebrand location (auto-migrated on first launch, never overwritten).
LEGACY_APP_NAME = "BeatNameGenerator"
LEGACY_DB_FILENAME = "beat_names.db"


def get_app_dir() -> Path:
    if os.name == "nt":
        base = os.environ.get("APPDATA") or str(Path.home() / "AppData" / "Roaming")
        p = Path(base) / APP_NAME
    else:
        p = Path.home() / f".{APP_NAME.lower()}"
    p.mkdir(parents=True, exist_ok=True)
    (p / "logs").mkdir(parents=True, exist_ok=True)
    _migrate_legacy(p)
    return p


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
