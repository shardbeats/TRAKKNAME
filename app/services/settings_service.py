"""Persistent user settings (JSON next to the DB: ./data or %APPDATA%)."""
from __future__ import annotations

import json
from pathlib import Path

DEFAULTS = {
    "default_language": "en",
    "default_genre": "Trap",
    "artists_per_generation": 2,
    "recent_exclusion_count": 100,
    "w_genre": 0.70,
    "w_related": 0.20,
    "w_global": 0.10,
    "artist_influence": 0.5,  # 0..1
    "default_style": "Random",
    "single_word": False,
    "selected_moods": [],
    "artist_pool": "all",
    "w_mood": 1.0,
    "sidebar_collapsed": False,
    "use_verbs": True,
    "use_adjectives": True,
    "use_nouns": True,
    "theme": "dark",
    "window_width": 980,
    "window_height": 720,
}


class SettingsService:
    def __init__(self, path: Path):
        self.path = path
        self.data: dict = dict(DEFAULTS)
        self.load()

    def load(self) -> dict:
        try:
            if self.path.exists():
                self.data = {**DEFAULTS, **json.loads(self.path.read_text(encoding="utf-8"))}
                # legacy region-based pool -> language-based
                if self.data.get("artist_pool") == "latam":
                    self.data["artist_pool"] = "es"
        except Exception:
            self.data = dict(DEFAULTS)
        return self.data

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.data, indent=2, ensure_ascii=False), encoding="utf-8")

    def get(self, key: str, default=None):
        return self.data.get(key, DEFAULTS.get(key, default))

    def set(self, key: str, value) -> None:
        self.data[key] = value
        self.save()
