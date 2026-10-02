"""Enrich the word database from kaikki.org Wiktionary dumps (streaming, low RAM).

Strategy — only useful, relevant words:
  1. Structural filters: noun/verb/adj only, single alphabetic token,
     3-12 chars, no proper nouns, no form-of-only entries
     (plurals, conjugations...), no archaic-only entries.
  2. Relevance filter (default `affinity` mode): keep a kaikki word only if
     it is listed as synonym/related/antonym of a word already in our DB
     (same language + POS). This grows the vocabulary around the aesthetic
     we already curated instead of dumping the whole dictionary.
  3. `broad` mode skips the affinity check (noisier; capped, shortest first).

Spanish nouns also inherit gender/number from Wiktionary tags when
unambiguous, so ES adjective agreement keeps working.

New words enter as GLOBAL pool (no genre/mood links), weight 1.0, enabled.

Usage (PowerShell):
  python tools/import_kaikki.py --lang es --dry-run
  python tools/import_kaikki.py --lang both --mode affinity --limit 3000
  python tools/import_kaikki.py --lang en --mode broad --limit 5000 --db "C:\\path\\trakkname.db"

Dumps expected at: kaikki/kaikki.org-dictionary-English.jsonl
                   kaikki/kaikki.org-dictionary-Spanish.jsonl
"""
from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
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


def is_form_of(sense: dict) -> bool:
    if "form_of" in sense:
        return True
    return "form-of" in (sense.get("tags") or [])


def is_stale(sense: dict) -> bool:
    tags = set(sense.get("tags") or [])
    return bool(tags & STALE_TAGS)


def structural_ok(word: str, pos: str, lang_code: str, min_len: int = MIN_LEN) -> bool:
    if pos not in POS_MAP or lang_code not in ("en", "es"):
        return False
    if not word or word[0].isupper():
        return False
    if not (min_len <= len(word) <= MAX_LEN):
        return False
    return bool(TOKEN_RE.match(word))


def entry_ok(obj: dict) -> bool:
    """Reject form-of-only, archaic-only, and toxic (vulgar/offensive) entries."""
    senses = obj.get("senses") or []
    if not senses:
        return False
    if all(is_form_of(s) for s in senses):
        return False
    if all(is_stale(s) for s in senses):
        return False
    for s in senses:
        if TOXIC_TAGS & set(s.get("tags") or []):
            return False
    return True


def relations(obj: dict) -> set[str]:
    """Synonym/related/antonym headwords (same-language neighborhood)."""
    out: set[str] = set()
    fields = ("synonyms", "related", "antonyms")
    senses = obj.get("senses") or []
    pools: list[dict] = list(obj.get("synonyms") or []) + list(obj.get("related") or [])
    for s in senses:
        for f in fields:
            pools.extend(s.get(f) or [])
    for rel in pools:
        if isinstance(rel, dict) and rel.get("word"):
            out.add(str(rel["word"]).strip().lower())
    return out


def es_gender_number(obj: dict) -> tuple[str | None, str | None]:
    """Majority vote over non-form-of senses; None when ambiguous."""
    genders = [t for s in (obj.get("senses") or []) if not is_form_of(s)
               for t in (s.get("tags") or []) if t in ("masculine", "feminine")]
    numbers = [t for s in (obj.get("senses") or []) if not is_form_of(s)
               for t in (s.get("tags") or []) if t in ("singular", "plural")]
    gender = genders[0] if genders and all(g == genders[0] for g in genders) else None
    number = numbers[0] if numbers and all(n == numbers[0] for n in numbers) else None
    return gender, number


def load_db_words(conn: sqlite3.Connection) -> tuple[dict[tuple[str, str, str], int], dict[tuple[str, str], set[str]]]:
    """(existing (word, lang, pos) set, seed neighborhood per (lang, pos))."""
    existing: dict[tuple[str, str, str], int] = {}
    seeds: dict[tuple[str, str], set[str]] = {}
    for r in conn.execute("SELECT word, language, part_of_speech FROM words"):
        key = (r["word"].lower(), r["language"], r["part_of_speech"])
        existing[key] = 1
        seeds.setdefault((r["language"], r["part_of_speech"]), set()).add(r["word"].lower())
    return existing, seeds


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


def main() -> int:
    ap = argparse.ArgumentParser(description="Import kaikki.org words into the beat-name DB.")
    ap.add_argument("--lang", choices=["en", "es", "both"], default="both")
    ap.add_argument("--mode", choices=["affinity", "broad"], default="affinity")
    ap.add_argument("--limit", type=int, default=3000, help="Max new words per language (shortest first).")
    ap.add_argument("--min-links", type=int, default=2, help="Affinity mode: min. synonym/related/antonym links to DB words.")
    ap.add_argument("--min-len", type=int, default=3, help="Minimum word length (broad mode: use 4-5 to skip abbreviations).")
    ap.add_argument("--dry-run", action="store_true", help="Show what would be imported, write nothing.")
    ap.add_argument("--db", default=None, help="DB path (default: %%APPDATA%%/TRAKKNAME/trakkname.db).")
    args = ap.parse_args()

    if args.db:
        db_path = Path(args.db)
    else:
        from app.utils.paths import get_db_path
        db_path = get_db_path()
    for lang in ([args.lang] if args.lang != "both" else ["en", "es"]):
        if not FILES[lang].exists():
            print(f"Missing dump: {FILES[lang]}")
            return 1

    from app.database.connection import get_connection
    conn = get_connection(str(db_path))
    try:
        existing, seeds = load_db_words(conn)
        print(f"DB words: {len(existing):,}")
        for lang in ([args.lang] if args.lang != "both" else ["en", "es"]):
            print(f"Streaming {FILES[lang].name} …")
            found = collect(FILES[lang], lang, seeds, existing, args.mode, args.min_links, args.min_len)
            # shortest first = punchier title words
            ordered = sorted(found.items(), key=lambda kv: (len(kv[0][0]), kv[0][0]))[:args.limit]
            print(f"  [{lang}] importing {len(ordered):,} (limit {args.limit})")
            if args.dry_run:
                preview = [w for (w, _, _), _ in ordered[:40]]
                print(f"  [{lang}] preview: {', '.join(preview)}")
                continue
            with conn:
                for (word, lang_, pos), (gender, number) in ordered:
                    conn.execute(
                        "INSERT INTO words(word, language, part_of_speech, weight, enabled, gender, number)"
                        " VALUES (?,?,?,?,?,?,?)",
                        (word, lang_, pos, 1.0, 1, gender, number))
            print(f"  [{lang}] done.")
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
