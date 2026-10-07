# MAINTENANCE — TRAKKNAME Desktop

Operations handover for keeping this project healthy. Read before touching seed, migrations, or releases.

## Environment
- Python 3.11+ with `.venv` at the root (`start.bat` creates it and installs `requirements.txt`; `run.bat` only launches).
- Deps: PySide6 (+ pytest for tests only).
- User data lives **outside the repo**: source runs use `%APPDATA%\TRAKKNAME\trakkname.db`, `settings.json`, `logs\app.log`; the frozen `.exe` is fully portable and uses `<exe-dir>\data\` instead (see `app/utils/paths.py`: `TRAKKNAME_DATA_DIR` override, `use_appdata.flag` / `TRAKKNAME_APPDATA=1` opt-out, one-time `%APPDATA%` → `data` migration). Never store DB/settings inside the project.
- First launch migrates once from the legacy `BeatNameGenerator` folder (`app/utils/paths.py`) — don't touch that block except on rebrand.

## Routines
```bat
python -m pytest tests/ -q        :: 47 tests, must pass before any change
python app\main.py                :: run from source
set QT_QPA_PLATFORM=offscreen     :: for windowless UI smoke tests
.venv\Scripts\python.exe build_exe.py          :: tests + portable one-file exe (~50 MB, dist/ is gitignored)
.venv\Scripts\python.exe build_exe.py --console :: console build to diagnose startup failures on clean PCs
```

## Seed rules (important)
- Editable lists live in `app/database/seed_data/` (genres, artists, moods, patterns, vocabulary). `app/database/seed/` only orchestrates idempotent migrations — **never edit data there** (`bootstrap.py` = fresh fill, `artists_seed.py` / `patterns_seed.py` / `moods_seed.py` / `placeholders.py` = ensures).
- `ensure_*` conventions: `INSERT OR IGNORE` / never overwrite user edits. Read `app/database/seed/__init__.py` before adding a new `ensure_*`.
- First-launch/migration orchestration lives in `app/database/startup.py::ensure_database` (called from `app/main.py`) — don't duplicate it.
- Engine stages: `app/generator/results.py` (types) → `context.py` → `patterns.py` → `renderer.py`, with `engine.py` as thin facade. Keep the engine free of PySide6.
- UI: `generator_view/` = `view.py` (Qt only) + `presenter.py` (DB/service, testable) + `meta.py` + `widgets/`; `database_view/` = `view.py` + `tabs/*` + `crud.py` + `io_actions.py`; `dialogs/` = `base.py` + one module per dialog.
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
- `tools/kaikki/` (constants/filters/db/collect/cli): vocabulary mining, inserts only, never overwrites; requires a DB backup first. `tools/import_kaikki.py` is only a thin wrapper.
- The mobile seed (`seed-json/` + `tools/export_seed_json.py`) lives in the mobile project: desktop curated-seed changes force a re-export there.

## Typical curation checklist
1. Edit a list in `seed_data/` → 2. `pytest tests/ -q` → 3. Open the app (migrates the local DB) → 4. Verify in Database → 5. Re-export the seed to mobile if applicable.
