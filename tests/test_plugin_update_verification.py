"""Focused checks use synthetic plugin copies, never the user's installation."""

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.verify_plugin_update import SAMPLES, compare, main


class PluginUpdateVerificationTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.source = Path(self.directory.name) / "source"
        self.installed = Path(self.directory.name) / "installed"
        for root in (self.source, self.installed):
            for relative in SAMPLES["happy-core"]:
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text('{"version":"0.2.0"}' if relative.endswith(".json") else "old", encoding="utf-8")
        self.skill = "skills/home-bootstrap/assets/AGENTS.md"

    def report(self):
        return compare("happy-core", self.source, self.installed)

    def test_allowlisted_samples_exist_in_current_distribution(self):
        root = Path(__file__).resolve().parent.parent / "plugins"
        for plugin, samples in SAMPLES.items():
            for relative in samples:
                with self.subTest(plugin=plugin, file=relative):
                    self.assertTrue((root / plugin / relative).is_file())

    def test_matching_samples_do_not_claim_session_load(self):
        self.assertEqual(self.report()["status"], "samples_match")
        self.assertEqual(self.report()["session_load"], "not_checked")

    def test_same_version_does_not_hide_changed_content(self):
        (self.source / self.skill).write_text("new", encoding="utf-8")
        self.assertEqual(self.report()["status"], "mismatch")

    def test_new_version_does_not_hide_stale_content(self):
        for root in (self.source, self.installed):
            (root / ".codex-plugin/plugin.json").write_text('{"version":"0.2.1"}', encoding="utf-8")
        (self.source / self.skill).write_text("new", encoding="utf-8")
        self.assertEqual(self.report()["status"], "mismatch")

    def test_missing_file_does_not_match(self):
        (self.installed / self.skill).unlink()
        self.assertEqual(self.report()["status"], "mismatch")
        (self.source / self.skill).unlink()
        self.assertEqual(self.report()["status"], "mismatch")

    def test_absent_installed_path_is_not_checked(self):
        self.assertEqual(compare("happy-core", self.source, None)["status"], "not_checked")
        missing = Path(self.directory.name) / "missing"
        self.assertEqual(compare("happy-core", self.source, missing)["status"], "mismatch")

    def test_unselected_preview_is_not_read(self):
        output = json.dumps(self.report())
        self.assertNotIn("pr-delivery", output)
        self.assertNotIn("happy-preview", output)
        self.assertNotIn(self.directory.name, output)

    def test_symlink_outside_root_is_not_read(self):
        path = self.installed / self.skill
        path.unlink()
        try:
            path.symlink_to(self.source / self.skill)
        except OSError:
            self.skipTest("Symlinks unavailable on this platform")
        self.assertIn("outside_root", json.dumps(self.report()))
        self.assertEqual(self.report()["status"], "mismatch")

    def test_cli_exit_code_and_path_free_json(self):
        args = ["verify", "--plugin", "happy-core", "--source", str(self.source), "--installed", str(self.installed)]
        with patch("sys.argv", args), contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(main(), 0)
        self.assertEqual(json.loads(output.getvalue())["status"], "samples_match")
        with patch("sys.argv", args[:-2]), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(main(), 1)


if __name__ == "__main__":
    unittest.main()
