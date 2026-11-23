# THIRD-PARTY-NOTICES — TRAKKNAME

TRAKKNAME code (including `seed_data/` vocabulary, artists, moods
and patterns) is GPL-3.0-only (`LICENSE`, see `LICENSING.md`; versions published before 2026-11-23 remain MIT). The components below keep their
own licenses, in source runs AND inside the frozen exe.

| Component | License | Notes |
|---|---|---|
| PySide6 + Qt | LGPLv3 | GUI toolkit. https://www.qt.io + https://pypi.org/project/PySide6/ |
| Python stdlib (sqlite3) | PSF | Local database, no network. |

Build tool only (not shipped): PyInstaller (GPLv2 with bootloader
exception), pytest/pytest-bdd/pytest-cov (MIT, dev only).

Compliance: ship `LICENSE` + `LICENSING.md` + `LICENSING.md` + `NOTICE.md` + this file with the app;
LGPL texts via the links above.
