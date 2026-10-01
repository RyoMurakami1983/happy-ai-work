"""Exercise the release gate against real, temporary Git histories."""

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from scripts.validate_plugin_versions import check_versions


class PluginVersionGateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.git("init", "-q")
        self.git("config", "user.name", "Fixture")
        self.git("config", "user.email", "fixture@example.invalid")
        self.write("plugins/example/.codex-plugin/plugin.json", json.dumps({"name": "example", "version": "1.2.3"}))
        self.write("plugins/example/skills/example/SKILL.md", "old")
        self.base = self.commit()

    def git(self, *args):
        return subprocess.check_output(["git", *args], cwd=self.root, text=True).strip()

    def write(self, relative, content):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def commit(self):
        self.git("add", "-A")
        self.git("commit", "-qm", "fixture")
        return self.git("rev-parse", "HEAD")

    def test_skill_edit_without_bump_fails(self):
        self.write("plugins/example/skills/example/SKILL.md", "new")
        self.assertTrue(check_versions(self.root, self.base, self.commit()))


    def bump(self, version="1.2.4", plugin="example"):
        self.write(f"plugins/{plugin}/.codex-plugin/plugin.json", json.dumps({"name": plugin, "version": version}))

    def test_payload_edit_with_bump_passes(self):
        self.write("plugins/example/skills/example/SKILL.md", "new")
        self.bump()
        self.assertEqual(check_versions(self.root, self.base, self.commit()), [])

    def test_root_docs_and_readme_are_exempt(self):
        self.write("README.md", "new")
        self.write("docs/guide.md", "new")
        self.assertEqual(check_versions(self.root, self.base, self.commit()), [])

    def test_every_distributed_file_type_requires_bump(self):
        for relative in ("references/guide.md", "scripts/task.py", "agents/openai.yaml", "README.md", "asset.bin"):
            with self.subTest(relative=relative):
                base = self.git("rev-parse", "HEAD")
                self.write(f"plugins/example/{relative}", "new")
                self.assertTrue(check_versions(self.root, base, self.commit()))

    def test_metadata_only_bump_and_downgrade_fail(self):
        for version in ("1.2.3+new", "1.2.2", "1.1.99", "0.99.99"):
            with self.subTest(version=version):
                self.bump(version)
                self.assertTrue(check_versions(self.root, self.base, self.commit()))

    def test_invalid_release_versions_fail(self):
        for version in ("01.2.4", "1.2", "garbage", "1.2.4-rc.1", 123):
            with self.subTest(version=version):
                self.bump(version)
                self.assertTrue(check_versions(self.root, self.base, self.commit()))

    def test_numeric_comparison_and_existing_build_metadata(self):
        self.bump("1.2.9+codex.old")
        base = self.commit()
        self.bump("1.2.10")
        self.assertEqual(check_versions(self.root, base, self.commit()), [])

    def test_deleted_skill_requires_bump(self):
        (self.root / "plugins/example/skills/example/SKILL.md").unlink()
        self.assertTrue(check_versions(self.root, self.base, self.commit()))

    def test_renamed_skill_requires_bump(self):
        path = self.root / "plugins/example/skills/example/SKILL.md"
        path.rename(path.with_name("RENAMED.md"))
        self.assertTrue(check_versions(self.root, self.base, self.commit()))

    def test_each_affected_plugin_needs_its_own_bump(self):
        self.bump("0.1.0", "second")
        self.write("plugins/second/skill.md", "old")
        base = self.commit()
        self.write("plugins/second/skill.md", "new")
        self.write("plugins/example/skill.md", "new")
        self.bump()
        errors = check_versions(self.root, base, self.commit())
        self.assertEqual(len(errors), 1)
        self.assertIn("second", errors[0])

    def test_file_move_between_plugins_requires_both_bumps(self):
        self.bump("0.1.0", "second")
        base = self.commit()
        source = self.root / "plugins/example/skills/example/SKILL.md"
        source.rename(self.root / "plugins/second/moved.md")
        self.assertEqual(len(check_versions(self.root, base, self.commit())), 2)
        self.bump()
        self.bump("0.1.1", "second")
        self.assertEqual(check_versions(self.root, base, self.commit()), [])

    def test_new_plugin_needs_valid_manifest(self):
        self.write("plugins/new/skill.md", "new")
        self.assertTrue(check_versions(self.root, self.base, self.commit()))
        self.bump("0.1.0", "new")
        self.assertEqual(check_versions(self.root, self.base, self.commit()), [])

    def test_manifest_removal_with_remaining_files_fails(self):
        (self.root / "plugins/example/.codex-plugin/plugin.json").unlink()
        self.assertTrue(check_versions(self.root, self.base, self.commit()))

    def test_full_plugin_retirement_has_no_version_to_bump(self):
        self.git("rm", "-qr", "plugins/example")
        self.write("README.md", "retired")
        self.assertEqual(check_versions(self.root, self.base, self.commit()), [])

    def test_plugin_directory_rename_requires_matching_identity(self):
        (self.root / "plugins/example").rename(self.root / "plugins/renamed")
        self.assertTrue(check_versions(self.root, self.base, self.commit()))
        self.bump("0.1.0", "renamed")
        self.assertEqual(check_versions(self.root, self.base, self.commit()), [])

    def test_base_only_changes_do_not_count_as_pr_changes(self):
        self.git("checkout", "-qb", "base-side")
        self.write("plugins/example/skill.md", "base change")
        self.bump("1.2.5")
        base_tip = self.commit()
        self.git("checkout", "-qb", "head-side", self.base)
        self.write("docs/guide.md", "only PR docs")
        self.assertEqual(check_versions(self.root, base_tip, self.commit()), [])

    def test_changed_plugin_must_exceed_current_base_not_just_merge_base(self):
        self.git("checkout", "-qb", "base-side")
        self.bump("1.2.5")
        base_tip = self.commit()
        self.git("checkout", "-qb", "head-side", self.base)
        self.bump("1.2.4")
        self.assertTrue(check_versions(self.root, base_tip, self.commit()))

    def test_unresolvable_ref_fails_closed(self):
        with self.assertRaises(ValueError):
            check_versions(self.root, "missing-ref", self.base)

    def test_workflow_automatically_checks_exact_pr_commits(self):
        workflow = (Path(__file__).resolve().parent.parent / ".github/workflows/quality.yml").read_text()
        self.assertIn("github.event.pull_request.base.sha", workflow)
        self.assertIn("github.event.pull_request.head.sha", workflow)
        self.assertIn('python scripts/validate_plugin_versions.py --base "$BASE_SHA" --head "$HEAD_SHA"', workflow)


if __name__ == "__main__":
    unittest.main()
