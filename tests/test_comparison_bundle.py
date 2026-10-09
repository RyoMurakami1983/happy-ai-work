"""Public preparation contracts, not model performance tests."""

import tempfile
import unittest
from pathlib import Path

from scripts.comparison_bundle import prepare_bundle

ROOT = Path(__file__).resolve().parent.parent


class ComparisonBundleTests(unittest.TestCase):
    def test_baseline_bundle_has_task_fixture_and_skill_but_no_grading_assets(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "fresh"
            prepare_bundle(ROOT, "baseline", "small-fix-normal", target)
            self.assertTrue((target / "task.md").is_file())
            self.assertTrue((target / "workspace" / "arithmetic.py").is_file())
            self.assertTrue((target / ".agents/skills/implement/SKILL.md").is_file())
            self.assertFalse(list(target.rglob("cases.v*.json")))
            self.assertFalse(list(target.rglob("*schema*")))
            self.assertNotIn("lambda", (target / "task.md").read_text(encoding="utf-8"))

    def test_existing_destination_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(FileExistsError):
                prepare_bundle(ROOT, "baseline", "small-fix-normal", Path(tmp))

    def test_invalid_selectors_fail_without_writing(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "fresh"
            for condition, case in [("../baseline", "small-fix-normal"), ("baseline", "../cases")]:
                with self.subTest(condition=condition, case=case), self.assertRaises(ValueError):
                    prepare_bundle(ROOT, condition, case, target)
            self.assertFalse(target.exists())

    def test_all_four_families_and_conditions_are_frozen(self):
        import json

        manifest = json.loads((ROOT / "evals/openai-first-implement/preparation.v1.json").read_text(encoding="utf-8"))
        families = [value["family"] for value in manifest["tasks"].values()]
        self.assertEqual(set(families), {"small-fix", "docs", "ui", "unapproved"})
        self.assertTrue(all(families.count(family) == 3 for family in set(families)))
        for condition in ("baseline", "candidate"):
            base = ROOT / "evals/openai-first-implement" / condition
            expected = {
                ".agents/skills/" + path.relative_to(base).as_posix()
                for path in base.rglob("*")
                if path.is_file() and "__pycache__" not in path.parts
                and path.relative_to(base).parts[0] in {"implement", "implementation-plan"}
            }
            self.assertEqual(set(manifest["conditions"][condition]), expected)
        with tempfile.TemporaryDirectory() as tmp:
            for condition in ("baseline", "candidate"):
                for case in manifest["tasks"]:
                    target = Path(tmp) / f"{condition}-{case}"
                    result = prepare_bundle(ROOT, condition, case, target)
                    self.assertFalse(result["isolation_verified"])
                    self.assertFalse(result["trial_authorized"])
                    self.assertTrue((target / ".agents/skills/implement/SKILL.md").is_file())
                    self.assertTrue((target / "workspace/README.md").is_file())
                    self.assertFalse(list(target.rglob("*.fixture")))

    def test_changed_source_hash_is_rejected_before_output_creation(self):
        import shutil

        with tempfile.TemporaryDirectory() as tmp:
            repository = Path(tmp) / "repository"
            source = repository / "evals/openai-first-implement"
            shutil.copytree(ROOT / "evals/openai-first-implement", source)
            (source / "tasks/small-fix-normal.md").write_text("changed input", encoding="utf-8")
            output = Path(tmp) / "actor"
            with self.assertRaisesRegex(ValueError, "hash mismatch"):
                prepare_bundle(repository, "baseline", "small-fix-normal", output)
            self.assertFalse(output.exists())

    def test_actor_destination_cannot_be_within_evaluation_repository(self):
        with self.assertRaisesRegex(ValueError, "outside"):
            prepare_bundle(ROOT, "baseline", "small-fix-normal", ROOT / "actor-not-created")

    def test_manifest_output_paths_and_collisions_fail_closed(self):
        import copy
        import json
        import shutil

        with tempfile.TemporaryDirectory() as tmp:
            repository = Path(tmp) / "repository"
            source = repository / "evals/openai-first-implement"
            shutil.copytree(ROOT / "evals/openai-first-implement", source)
            path = source / "preparation.v1.json"
            original = json.loads(path.read_text(encoding="utf-8"))
            condition_key = next(iter(original["conditions"]["baseline"]))
            for invalid in ["C:escape.txt", "SOURCE.json", "source.JSON", "workspace/CON.txt",
                            "workspace/README.md.", "workspace//other.txt", "Task.md", condition_key,
                            "workspace/README.md/child"]:
                with self.subTest(output=invalid):
                    manifest = copy.deepcopy(original)
                    entries = manifest["tasks"]["small-fix-normal"]["files"]
                    entries[invalid] = entries["task.md"]
                    path.write_text(json.dumps(manifest), encoding="utf-8")
                    output = Path(tmp) / "actor"
                    with self.assertRaises(ValueError):
                        prepare_bundle(repository, "baseline", "small-fix-normal", output)
                    self.assertFalse(output.exists())
