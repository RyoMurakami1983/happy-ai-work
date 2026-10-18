"""Focused checks use synthetic plugin copies, never the user's installation."""

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.verify_plugin_update import ABSENT_PATHS, SAMPLES, compare, main

PLANNING_SAMPLES = (
    "skills/implement/references/planning.md",
    "skills/implement/references/html-plan.md",
    "skills/implement/assets/NNN_PLAN_TEMPLATE.md",
    "skills/implement/assets/plan.html",
    "skills/implement/scripts/render_plan.py",
)


class PluginUpdateVerificationTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.source = Path(self.directory.name) / "source"
        self.installed = Path(self.directory.name) / "installed"
        self.populate_samples("happy-core")
        self.skill = "skills/home-bootstrap/assets/AGENTS.md"

    def populate_samples(self, plugin):
        for root in (self.source, self.installed):
            for relative in SAMPLES[plugin]:
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text('{"version":"0.2.0"}' if relative.endswith(".json") else "old", encoding="utf-8")

    def report(self, plugin="happy-core"):
        return compare(plugin, self.source, self.installed)

    def test_allowlisted_samples_exist_in_current_distribution(self):
        root = Path(__file__).resolve().parent.parent / "plugins"
        for plugin, samples in SAMPLES.items():
            for relative in samples:
                with self.subTest(plugin=plugin, file=relative):
                    self.assertTrue((root / plugin / relative).is_file())
        for plugin, paths in ABSENT_PATHS.items():
            for relative in paths:
                with self.subTest(plugin=plugin, absent_path=relative):
                    self.assertFalse((root / plugin / relative).exists())

    def test_integrated_planning_samples_are_allowlisted(self):
        self.assertTrue(set(PLANNING_SAMPLES).issubset(SAMPLES["happy-coding"]))
        self.assertIn("skills/implementation-plan", ABSENT_PATHS["happy-coding"])

    def test_stale_planning_reference_alone_does_not_match(self):
        self.populate_samples("happy-coding")
        self.assertEqual(self.report("happy-coding")["status"], "samples_match")
        relative = "skills/implement/references/planning.md"
        (self.installed / relative).write_text("stale planning instructions", encoding="utf-8")
        report = self.report("happy-coding")
        self.assertEqual(report["status"], "mismatch")
        self.assertEqual([entry["file"] for entry in report["files"] if not entry["matches"]], [relative])
        self.assertEqual(report["session_load"], "not_checked")

    def test_stale_or_missing_planning_assets_do_not_match(self):
        self.populate_samples("happy-coding")
        for relative in PLANNING_SAMPLES[1:]:
            with self.subTest(file=relative):
                path = self.installed / relative
                path.write_text("stale planning asset", encoding="utf-8")
                self.assertEqual(self.report("happy-coding")["status"], "mismatch")
                path.unlink()
                self.assertEqual(self.report("happy-coding")["status"], "mismatch")
                path.write_bytes((self.source / relative).read_bytes())
                self.assertEqual(self.report("happy-coding")["status"], "samples_match")

    def test_retired_directory_or_entrypoint_does_not_match(self):
        self.populate_samples("happy-coding")
        retired = self.installed / "skills/implementation-plan"
        retired.mkdir()
        for entrypoint in (False, True):
            with self.subTest(entrypoint=entrypoint):
                if entrypoint:
                    (retired / "SKILL.md").write_text("obsolete entrypoint", encoding="utf-8")
                report = self.report("happy-coding")
                self.assertTrue(all(entry["matches"] for entry in report["files"]))
                self.assertEqual(report["status"], "mismatch")
                self.assertEqual(report["absent_paths"], [{
                    "path": "skills/implementation-plan",
                    "source": {"state": "absent"},
                    "installed": {"state": "present"},
                    "matches": False,
                }])
                self.assertEqual(report["session_load"], "not_checked")
                self.assertNotIn(self.directory.name, json.dumps(report))

    def test_matching_retired_paths_in_source_and_installed_still_fail(self):
        self.populate_samples("happy-coding")
        for root in (self.source, self.installed):
            (root / "skills/implementation-plan").mkdir()
        self.assertEqual(self.report("happy-coding")["status"], "mismatch")

    def test_retired_symlinks_are_not_treated_as_absent(self):
        self.populate_samples("happy-coding")
        retired = self.installed / "skills/implementation-plan"
        targets = ((self.installed / "missing-target", "present"), (self.source, "outside_root"))
        for target, expected in targets:
            with self.subTest(state=expected):
                try:
                    retired.symlink_to(target, target_is_directory=True)
                except OSError:
                    self.skipTest("Symlinks unavailable on this platform")
                report = self.report("happy-coding")
                self.assertEqual(report["status"], "mismatch")
                self.assertEqual(report["absent_paths"][0]["installed"], {"state": expected})
                self.assertNotIn(self.directory.name, json.dumps(report))
                retired.unlink()

    def test_retirement_check_without_installed_path_is_not_checked(self):
        self.populate_samples("happy-coding")
        report = compare("happy-coding", self.source, None)
        self.assertEqual(report["status"], "not_checked")
        self.assertEqual(report["absent_paths"], [{
            "path": "skills/implementation-plan",
            "source": {"state": "absent"},
            "installed": {"state": "not_checked"},
            "matches": False,
        }])
        self.assertEqual(report["session_load"], "not_checked")

    def test_matching_samples_do_not_check_other_installation_files(self):
        self.populate_samples("happy-coding")
        (self.installed / "unselected-file.md").write_text("stale unsampled content", encoding="utf-8")
        report = self.report("happy-coding")
        self.assertEqual(report["status"], "samples_match")
        self.assertEqual(report["session_load"], "not_checked")
        self.assertNotIn("unselected-file.md", json.dumps(report))

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
        self.assertNotIn(self.directory.name, output.getvalue())
        with patch("sys.argv", args[:-2]), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(main(), 1)

    def test_cli_retired_entrypoint_reports_mismatch_without_private_paths(self):
        self.populate_samples("happy-coding")
        retired = self.installed / "skills/implementation-plan/SKILL.md"
        retired.parent.mkdir()
        retired.write_text("obsolete entrypoint", encoding="utf-8")
        args = ["verify", "--plugin", "happy-coding", "--source", str(self.source), "--installed", str(self.installed)]
        with patch("sys.argv", args), contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(main(), 1)
        report = json.loads(output.getvalue())
        self.assertEqual(report["status"], "mismatch")
        self.assertEqual(report["session_load"], "not_checked")
        self.assertNotIn(self.directory.name, output.getvalue())


if __name__ == "__main__":
    unittest.main()
