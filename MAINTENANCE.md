# MAINTENANCE — TRAKKNAME Desktop

Operations handover for keeping this project healthy. Read before touching seed, migrations, or releases.

## Environment
- Python 3.11+ with `.venv` at the root (`start.bat` creates it and installs `requirements.txt`; `run.bat` only launches).
- Deps: PySide6 (+ pytest for tests only).
- User data lives **outside the repo**: `%APPDATA%\TRAKKNAME\trakkname.db`, `settings.json`, `logs\app.log`. Never store DB/settings inside the project.
- First launch migrates once from the legacy `BeatNameGenerator` folder (`app/utils/paths.py`) — don't touch that block except on rebrand.

## Routines
```bat
python -m pytest tests/ -q        :: 43 tests, must pass before any change
python app\main.py                :: run from source
set QT_QPA_PLATFORM=offscreen     :: for windowless UI smoke tests
```

## Seed rules (important)
- Editable lists live in `app/database/seed_data/` (genres, artists, moods, patterns, vocabulary). `app/database/seed.py` only orchestrates idempotent migrations — **never edit data there**.
- `ensure_*` conventions: `INSERT OR IGNORE` / never overwrite user edits. Read `seed.py` before adding a new `ensure_*`.
- Patterns have three states with different semantics —
  - `PATTERNS` = active curated set (currently 8: 4 EN + 4 ES),
  - `RETIRED_PATTERNS` = **disabled** (reversible in the UI),
  - `REMOVED_PATTERNS` = **deleted** from existing DBs (irreversible; currently `Single Noun`, `Una Palabra`, legacy variant).
- `STYLE_RENAMES` maps old names → new ones; don't remove entries (old DBs need them).
- Tests pin counts (`test_generator.py`: 8 enabled, exact ES set). If the curated set changes, update tests + `README.md` + re-export the seed to the mobile project.
- The mobile project's `seed-json/` + `tools/export_seed_json.py` regenerate from the real DB: after curated-seed changes, re-export and verify `manifest.json` (artists/words/moods/patterns/relations).

## Known gotchas
- `GenerationResult.title` comes title-cased from the engine; the view shows UPPER but copies the original. Don't "fix" — intentional parity with mobile.
- `ArtistDialog.region` is informational only; pools filter by `language` (`LEGACY_POOL_MAP` maps `latam` → `es`).
- `MoodDialog.icon`: legacy glyphs are retired in `seed_moods`; the field accepts custom icons but the UI is 100% text.
- FKs use `ON DELETE CASCADE` + `PRAGMA foreign_keys = ON` in `connection.py`: repo deletes rely on cascade, don't delete table-by-table by hand.
- `WAL` can fail in odd folders — there is already a fallback to normal journal, leave it.

## Don't touch without reason
- `app/database/schema.py::migrate_database` (legacy columns per DB version).
- `tools/import_kaikki.py`: vocabulary mining, inserts only, never overwrites; requires a DB backup first.
- The mobile seed (`seed-json/` + `tools/export_seed_json.py`) lives in the mobile project: desktop curated-seed changes force a re-export there.

## Typical curation checklist
1. Edit a list in `seed_data/` → 2. `pytest tests/ -q` → 3. Open the app (migrates the local DB) → 4. Verify in Database → 5. Re-export the seed to mobile if applicable.
