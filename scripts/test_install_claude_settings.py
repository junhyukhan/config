import importlib.util
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import tempfile
import unittest

SCRIPT = Path(__file__).with_name("install-claude-settings.py")
spec = importlib.util.spec_from_file_location("install_settings", SCRIPT)
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)


class InstallSettingsTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root / "repo"
        self.home = self.root / "home"
        self.home.mkdir()
        self.source = self.repo / "claude/.claude/settings.json"
        self.source.parent.mkdir(parents=True)
        self.payload = b'{"permissions":{"defaultMode":"auto"},"hooks":{},"autoMode":{"environment":["synthetic private context"]}}\n'
        self.source.write_bytes(self.payload)
        self.target = self.home / ".claude/settings.json"

    def install(self):
        return installer.install(self.repo, self.home)

    def test_fresh_install_is_private_regular_file(self):
        self.install()
        self.assertFalse(self.target.is_symlink())
        self.assertEqual(self.target.read_bytes(), self.payload)
        self.assertEqual(stat.S_IMODE(self.target.stat().st_mode), 0o600)

    def test_migration_preserves_exact_bytes_and_source(self):
        self.target.parent.mkdir()
        self.target.symlink_to(self.source)
        self.install()
        self.assertFalse(self.target.is_symlink())
        self.assertEqual(self.target.read_bytes(), self.payload)
        self.assertEqual(self.source.read_bytes(), self.payload)

    def test_relative_legacy_link(self):
        self.target.parent.mkdir()
        self.target.symlink_to(os.path.relpath(self.source, self.target.parent))
        self.install()
        self.assertEqual(self.target.read_bytes(), self.payload)
        self.assertFalse(self.target.is_symlink())

    def test_existing_local_preferences_and_inventory_survive_new_defaults(self):
        self.install()
        self.source.write_text('{"theme":"different","autoMode":{"environment":[]}}')
        self.install()
        self.assertEqual(self.target.read_bytes(), self.payload)

    def test_local_changes_do_not_write_back_to_source(self):
        self.install()
        self.target.write_text('{"theme":"local"}')
        self.assertEqual(self.source.read_bytes(), self.payload)

    def test_unfamiliar_symlink_is_refused(self):
        self.target.parent.mkdir()
        unknown = self.root / "unknown"
        unknown.write_text("not settings")
        self.target.symlink_to(unknown)
        with self.assertRaises(installer.SettingsError):
            self.install()
        self.assertTrue(self.target.is_symlink())
        self.assertEqual(unknown.read_text(), "not settings")

    def test_symlinked_directory_is_refused(self):
        other = self.root / "other"
        other.mkdir()
        self.target.parent.symlink_to(other)
        with self.assertRaises(installer.SettingsError):
            self.install()
        self.assertEqual(list(other.iterdir()), [])

    def test_malformed_template_leaves_legacy_link_intact(self):
        self.target.parent.mkdir()
        self.target.symlink_to(self.source)
        self.source.write_text("not JSON")
        with self.assertRaises(installer.SettingsError):
            self.install()
        self.assertTrue(self.target.is_symlink())

    def test_non_object_template_is_refused(self):
        self.source.write_text("[]")
        with self.assertRaises(installer.SettingsError):
            self.install()
        self.assertFalse(self.target.exists())

    def test_malformed_local_file_is_not_overwritten(self):
        self.target.parent.mkdir()
        self.target.write_text("not JSON")
        with self.assertRaises(installer.SettingsError):
            self.install()
        self.assertEqual(self.target.read_text(), "not JSON")

    @unittest.skipUnless(shutil.which("stow"), "GNU Stow is not installed")
    def test_stow_and_restow_keep_local_settings_private(self):
        package = self.repo / "claude"
        (package / ".stow-local-ignore").write_bytes(
            (SCRIPT.parent.parent / "claude/.stow-local-ignore").read_bytes()
        )
        hook = package / ".claude/hooks/synthetic.py"
        hook.parent.mkdir()
        hook.write_text("# synthetic fixture\n")
        self.target.parent.mkdir()
        self.target.symlink_to(self.source)
        self.install()
        self.source.write_text('{"generic":"defaults"}')
        for _ in range(2):
            result = subprocess.run(
                ["stow", "-d", str(self.repo), "-R", "--no-folding", "-t", str(self.home), "claude"],
                capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse(self.target.is_symlink())
            self.assertEqual(self.target.read_bytes(), self.payload)
            self.assertTrue((self.home / ".claude/hooks/synthetic.py").is_symlink())

    def test_cli_does_not_log_settings_values(self):
        self.target.parent.mkdir()
        self.target.write_text(json.dumps({"private": "synthetic-only-marker"}))
        result = subprocess.run(["python3", str(SCRIPT)], env={**os.environ, "HOME": str(self.home)}, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertNotIn("synthetic-only-marker", result.stdout + result.stderr)

    def test_cli_parse_errors_do_not_log_values(self):
        self.target.parent.mkdir()
        self.target.write_text("synthetic-only-invalid-marker")
        result = subprocess.run(["python3", str(SCRIPT)], env={**os.environ, "HOME": str(self.home)}, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("synthetic-only-invalid-marker", result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
