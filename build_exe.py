"""Build a fully-portable one-file TRAKKNAME.exe with PyInstaller.

Portable contract: the frozen app keeps ``trakkname.db`` + ``settings.json`` +
``logs/`` in ``<exe-dir>/data`` (see ``app/utils/paths.py``), so no Python and
no %APPDATA% traces are needed. This script only packs code + Qt + resources;
the data folder is created at first launch (migrating any %APPDATA% copy once).

Run from the project folder:

    .venv\\Scripts\\python.exe build_exe.py              # windowed, runs tests first
    .venv\\Scripts\\python.exe build_exe.py --console   # console build (diagnostics)
    .venv\\Scripts\\python.exe build_exe.py --skip-tests # skip pytest (not recommended)
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
APP_NAME = "TRAKKNAME"


def run(cmd: list[str]) -> int:
    print("+", " ".join(str(c) for c in cmd))
    return subprocess.call(cmd, cwd=ROOT)


def check_sources() -> bool:
    ok = True
    for rel in ("app/main.py", "app/ui/style.qss", "app/resources/trakkname.ico"):
        if not (ROOT / rel).exists():
            print(f"ERROR: missing {rel}")
            ok = False
    return ok


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Build the portable TRAKKNAME.exe.")
    ap.add_argument("--console", action="store_true", help="Console build for diagnostics (default: windowed).")
    ap.add_argument("--skip-tests", action="store_true", help="Skip pytest before building.")
    args = ap.parse_args(argv)

    if not check_sources():
        return 1
    if not args.skip_tests:
        print("== pytest (must pass before packaging) ==")
        rc = run([sys.executable, "-m", "pytest", "tests/", "-q"])
        if rc != 0:
            print("ERROR: tests failed — exe not built.")
            return rc
    try:
        import PySide6  # noqa: F401
        print(f"PySide6 {__import__('PySide6').__version__}")
    except Exception:
        print("ERROR: PySide6 is not installed in this interpreter.")
        return 1

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--clean",
        "--onefile",
        "--name", APP_NAME,
        "--icon", str(ROOT / "app" / "resources" / "trakkname.ico"),
        "--add-data", f"{ROOT / 'app' / 'resources'}{';' if sys.platform.startswith('win') else ':'}app/resources",
        "--add-data", f"{ROOT / 'app' / 'ui' / 'style.qss'}{';' if sys.platform.startswith('win') else ':'}app/ui",
        # Qt plugins/platforms/SSL are pulled by PyInstaller's PySide6 hooks.
        # (Avoid --collect-all PySide6: it drags Qt3D/WebEngine/multimedia and
        #  balloons the exe from ~50 MB to ~250 MB for no benefit here.)
        "--collect-submodules", "app",
        "--exclude-module", "pytest",
        "--exclude-module", "tests",
        "--exclude-module", "tkinter",
        str(ROOT / "app" / "main.py"),
    ]
    if not args.console:
        cmd.insert(5, "--windowed")
    else:
        cmd.insert(5, "--console")

    rc = run(cmd)
    if rc != 0:
        return rc

    exe = ROOT / "dist" / (APP_NAME + (".exe" if sys.platform.startswith("win") else ""))
    if not exe.exists():
        print(f"ERROR: expected {exe} was not created.")
        return 1
    size_mb = exe.stat().st_size / 1_000_000
    print(f"OK: {exe} ({size_mb:.1f} MB)")
    print("Portable data lives next to the exe in ./data (created on first launch).")
    print("Tip: run the --console build first on a clean PC to see startup errors.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
