import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


class TestPortablePaths(unittest.TestCase):
    def test_data_dir_override(self):
        from app.utils import paths as p
        with tempfile.TemporaryDirectory() as tmp:
            target = str(Path(tmp) / "custom")
            with mock.patch.dict(os.environ, {"TRAKKNAME_DATA_DIR": target}, clear=False):
                # ensure no frozen interference
                with mock.patch.object(sys, "frozen", False, create=True):
                    d = p.get_app_dir()
                    self.assertEqual(d, Path(target))
                    self.assertTrue((d / "logs").exists())
                    self.assertEqual(p.get_db_path().parent, d)

    def test_source_mode_is_not_portable(self):
        from app.utils import paths as p
        env = {k: v for k, v in os.environ.items() if k not in ("TRAKKNAME_DATA_DIR", "TRAKKNAME_APPDATA")}
        with mock.patch.dict(os.environ, env, clear=True):
            with mock.patch.object(sys, "frozen", False, create=True):
                self.assertFalse(p.is_portable_mode())

    def test_frozen_defaults_to_portable_data_dir(self):
        from app.utils import paths as p
        with tempfile.TemporaryDirectory() as tmp:
            fake_exe = str(Path(tmp) / "TRAKKNAME.exe")
            env = {k: v for k, v in os.environ.items() if k not in ("TRAKKNAME_DATA_DIR", "TRAKKNAME_APPDATA")}
            with mock.patch.dict(os.environ, env, clear=True):
                with mock.patch.object(sys, "frozen", True, create=True):
                    with mock.patch.object(sys, "executable", fake_exe, create=True):
                        self.assertTrue(p.is_portable_mode())
                        d = p.get_app_dir()
                        self.assertEqual(d, Path(tmp) / "data")
                        self.assertTrue((d / "logs").exists())

    def test_frozen_opt_out_flag(self):
        from app.utils import paths as p
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "use_appdata.flag").write_text("", encoding="utf-8")
            fake_exe = str(Path(tmp) / "TRAKKNAME.exe")
            env = {k: v for k, v in os.environ.items() if k not in ("TRAKKNAME_DATA_DIR", "TRAKKNAME_APPDATA")}
            with mock.patch.dict(os.environ, env, clear=True):
                with mock.patch.object(sys, "frozen", True, create=True):
                    with mock.patch.object(sys, "executable", fake_exe, create=True):
                        self.assertFalse(p.is_portable_mode())


if __name__ == "__main__":
    unittest.main()
