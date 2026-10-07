"""Streaming collector: dump JSONL -> {(word, lang, pos): (gender, number)}."""
from __future__ import annotations

import json
from pathlib import Path

from tools.kaikki.constants import LANG_CODE, POS_MAP
from tools.kaikki.filters import entry_ok, es_gender_number, relations, structural_ok


def collect(path: Path, lang: str, seeds: dict, existing: dict, mode: str, min_links: int, min_len: int) -> dict[tuple[str, str, str], tuple[str | None, str | None]]:
    """Stream the dump. Returns {(word, lang, pos): (gender, number)}."""
    found: dict[tuple[str, str, str], tuple[str | None, str | None]] = {}
    checked = kept = skipped_pos = skipped_struct = skipped_entry = skipped_dup = skipped_aff = 0
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            checked += 1
            pos = POS_MAP.get(obj.get("pos", ""))
            if not pos or obj.get("lang_code") != LANG_CODE[lang]:
                skipped_pos += 1
                continue
            word = (obj.get("word") or "").strip().lower()
            if not structural_ok(word, obj.get("pos", ""), obj.get("lang_code", ""), min_len):
                skipped_struct += 1
                continue
            if not entry_ok(obj):
                skipped_entry += 1
                continue
            key = (word, lang, pos)
            if key in existing or key in found:
                skipped_dup += 1
                continue
            if mode == "affinity":
                seeds_pos = seeds.get((lang, pos), set())
                if len(relations(obj) & seeds_pos) < min_links:
                    skipped_aff += 1
                    continue
            gender, number = es_gender_number(obj) if lang == "es" and pos == "noun" else (None, None)
            found[key] = (gender, number)
            kept += 1
            if checked % 200_000 == 0:
                print(f"  [{lang}] {checked:,} entries scanned, {kept:,} candidates…", flush=True)
    print(f"  [{lang}] scanned={checked:,} kept={kept:,} "
          f"(pos={skipped_pos:,} struct={skipped_struct:,} entry={skipped_entry:,} dup={skipped_dup:,} affinity={skipped_aff:,})")
    return found
