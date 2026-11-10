"""Build the portable TRAKKNAME (one-dir inside a ZIP).

Portable contract: the frozen app keeps ``trakkname.db`` + ``settings.json`` +
``logs/`` in ``<exe-dir>/data`` (see ``app/utils/paths.py``). This script packs
code + Qt + resources into a one-dir folder and zips it:

    dist\\TRAKKNAME-portable-<version>.zip
        TRAKKNAME\\
            TRAKKNAME.exe
            _internal\\   (Qt, resources, style.qss, ...)
            README.md / LICENSE / NOTICE.md / THIRD-PARTY-NOTICES.md

Run from the project folder:

    .venv\\Scripts\\python.exe build_portable.py --version 1.3.1
    .venv\\Scripts\\python.exe build_portable.py --console
    .venv\\Scripts\\python.exe build_portable.py --skip-tests

The old `build_exe.py` produced a one-file exe that re-extracted the payload
to %TMP% on EVERY launch; it was removed on purpose.
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
APP_NAME = "TRAKKNAME"
EXE_DIR = ROOT / "dist" / "portable" / APP_NAME
DOCS = ("README.md", "LICENSE", "NOTICE.md", "THIRD-PARTY-NOTICES.md")


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


def git_version() -> str:
    """Latest tag without the leading v (e.g. v1.3.0 -> 1.3.0)."""
    try:
        r = subprocess.run(["git", "describe", "--tags", "--abbrev=0"],
                           capture_output=True, text=True, cwd=ROOT)
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip().lstrip("v")
    except OSError:
        pass
    return "dev"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Build the portable TRAKKNAME ZIP.")
    ap.add_argument("--console", action="store_true",
                    help="Console build for diagnostics (default: windowed).")
    ap.add_argument("--skip-tests", action="store_true",
                    help="Skip pytest before building.")
    ap.add_argument("--version", default=None,
                    help="Version for the ZIP name (default: latest git tag).")
    args = ap.parse_args(argv)

    version = args.version or git_version()
    print(f"TRAKKNAME portable version: {version}")

    if not check_sources():
        return 1
    if not args.skip_tests:
        print("== pytest (must pass before packaging) ==")
        rc = run([sys.executable, "-m", "pytest", "tests/", "-q"])
        if rc != 0:
            print("ERROR: tests failed — build not produced.")
            return rc
    try:
        import PySide6  # noqa: F401
        print(f"PySide6 {__import__('PySide6').__version__}")
    except Exception:
        print("ERROR: PySide6 is not installed in this interpreter.")
        return 1

    sep = ";" if sys.platform.startswith("win") else ":"
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--clean",
        "--onedir",
        "--name", APP_NAME,
        "--distpath", "dist/portable",
        "--workpath", "build/portable",
        "--specpath", "build/portable",
        "--icon", str(ROOT / "app" / "resources" / "trakkname.ico"),
        "--add-data", f"{ROOT / 'app' / 'resources'}{sep}app/resources",
        "--add-data", f"{ROOT / 'app' / 'ui' / 'style.qss'}{sep}app/ui",
        # Qt plugins/platforms/SSL are pulled by PyInstaller's PySide6 hooks.
        # (Avoid --collect-all PySide6: it drags Qt3D/WebEngine/multimedia and
        #  balloons the build for no benefit here.)
        "--collect-submodules", "app",
        "--exclude-module", "pytest",
        "--exclude-module", "tests",
        "--exclude-module", "tkinter",
        str(ROOT / "app" / "main.py"),
    ]
    cmd.insert(5, "--console" if args.console else "--windowed")

    if EXE_DIR.exists():
        shutil.rmtree(EXE_DIR, ignore_errors=True)
    rc = run(cmd)
    if rc != 0:
        return rc

    exe = EXE_DIR / (APP_NAME + (".exe" if sys.platform.startswith("win") else ""))
    if not exe.exists():
        print(f"ERROR: expected {exe} was not created.")
        return 1

    for name in DOCS:
        src = ROOT / name
        if src.is_file():
            shutil.copy2(src, EXE_DIR / name)

    out = ROOT / "dist" / f"{APP_NAME}-portable-{version}.zip"
    if out.exists():
        out.unlink()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        for p in sorted(EXE_DIR.rglob("*")):
            if p.is_file():
                zf.write(p, Path(APP_NAME) / p.relative_to(EXE_DIR))

    print(f"OK: {out} ({out.stat().st_size / 1e6:.1f} MB)")
    print(f"Unzip once, then run {APP_NAME}\\{APP_NAME}.exe "
          "(portable data lives in ./data, created on first launch).")
    print("Tip: run the --console build first on a clean PC to see startup errors.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
