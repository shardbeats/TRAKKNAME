"""Shared constants for kaikki.org vocabulary mining."""
from __future__ import annotations

import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

TOKEN_RE = re.compile(r"^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+$")
POS_MAP = {"noun": "noun", "verb": "verb", "adj": "adjective"}
MIN_LEN, MAX_LEN = 3, 12
STALE_TAGS = {"archaic", "obsolete", "dated"}
# Skip the whole entry if ANY sense carries one of these (beat titles).
TOXIC_TAGS = {"vulgar", "offensive", "derogatory"}

FILES = {
    "en": PROJECT_ROOT / "kaikki" / "kaikki.org-dictionary-English.jsonl",
    "es": PROJECT_ROOT / "kaikki" / "kaikki.org-dictionary-Spanish.jsonl",
}
LANG_CODE = {"en": "en", "es": "es"}
