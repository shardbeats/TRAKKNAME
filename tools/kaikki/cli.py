"""CLI orchestration for kaikki.org imports (argparse + per-language loop)."""
from __future__ import annotations

import argparse
from pathlib import Path

from tools.kaikki.collect import collect
from tools.kaikki.constants import FILES
from tools.kaikki.db import load_db_words


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description="Import kaikki.org words into the beat-name DB.")
    ap.add_argument("--lang", choices=["en", "es", "both"], default="both")
    ap.add_argument("--mode", choices=["affinity", "broad"], default="affinity")
    ap.add_argument("--limit", type=int, default=3000, help="Max new words per language (shortest first).")
    ap.add_argument("--min-links", type=int, default=2, help="Affinity mode: min. synonym/related/antonym links to DB words.")
    ap.add_argument("--min-len", type=int, default=3, help="Minimum word length (broad mode: use 4-5 to skip abbreviations).")
    ap.add_argument("--dry-run", action="store_true", help="Show what would be imported, write nothing.")
    ap.add_argument("--db", default=None, help="DB path (default: %%APPDATA%%/TRAKKNAME/trakkname.db).")
    return ap


def run(args) -> int:
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


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    return run(args)
