"""Packaging and executable-contract checks, not a model-behavior evaluation.

The comparative pilot must independently verify semantic preservation. These
checks exercise relocation, pinned dependencies, and the required-artifact
checkpoint rather than claiming that keyword matches prove model behavior.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from urllib.parse import unquote, urlsplit

import yaml

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "evals/openai-first-implement/candidate"
SKILL = CANDIDATE / "implement"
BASELINE = ROOT / "evals/openai-first-implement/baseline"
BASELINE_REVISION = "ab32391c9612ad7983a4805040a6331ad5f576db"
LINK_RE = re.compile(r"\[[^]]+\]\(([^)]+)\)")


def linked_files(root: Path, start: Path) -> set[Path]:
    """Follow the installed skill's relative links, rejecting escaping paths."""
    pending = [start]
    visited: set[Path] = set()
    while pending:
        path = pending.pop().resolve()
        if path in visited:
            continue
        if not path.is_relative_to(root.resolve()):
            raise AssertionError(f"instruction dependency escapes installed skill: {path}")
        if not path.is_file():
            raise AssertionError(f"missing instruction dependency: {path}")
        visited.add(path)
        if path.suffix != ".md":
            continue
        for link in LINK_RE.findall(path.read_text(encoding="utf-8")):
            parsed = urlsplit(link)
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            pending.append(path.parent / unquote(parsed.path))
    return visited


class CandidatePackagingTests(unittest.TestCase):
    def test_skill_is_relocatable_without_repository_or_sibling_skills(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            installed = Path(temporary) / "skills" / "implement"
            shutil.copytree(SKILL, installed)
            reachable = linked_files(installed, installed / "SKILL.md")
            for path in installed.rglob("*"):
                self.assertFalse(path.is_symlink(), f"external symlink: {path}")
                if path.suffix == ".md":
                    self.assertIn(path.resolve(), reachable, f"unrouted reference: {path}")

    def test_link_check_rejects_missing_and_escaping_dependencies(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "implement"
            root.mkdir()
            entry = root / "SKILL.md"
            entry.write_text("[required](missing.md)", encoding="utf-8")
            with self.assertRaisesRegex(AssertionError, "missing instruction"):
                linked_files(root, entry)
            outside = root.parent / "outside.md"
            outside.write_text("outside", encoding="utf-8")
            entry.write_text("[required](../outside.md)", encoding="utf-8")
            with self.assertRaisesRegex(AssertionError, "escapes installed"):
                linked_files(root, entry)

    def test_frontmatter_is_unchanged_and_candidate_has_no_release_manifest(self) -> None:
        provenance = json.loads((CANDIDATE / "provenance.json").read_text(encoding="utf-8"))
        content = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        frontmatter = content.split("---", 2)[1]
        self.assertEqual(yaml.safe_load(frontmatter), provenance["baseline_frontmatter"])
        baseline_frontmatter = (BASELINE / "implement/SKILL.md").read_text(encoding="utf-8").split("---", 2)[1]
        self.assertEqual(frontmatter, baseline_frontmatter)
        self.assertEqual(yaml.safe_load(frontmatter)["name"], SKILL.name)
        self.assertFalse(list(CANDIDATE.rglob("plugin.json")))
        self.assertFalse(list(CANDIDATE.rglob("marketplace.json")))

    def test_preserved_resources_match_pinned_baseline_bytes(self) -> None:
        provenance = json.loads((CANDIDATE / "provenance.json").read_text(encoding="utf-8"))
        self.assertEqual(provenance["baseline_revision"], BASELINE_REVISION)
        self.assertTrue(provenance["preserved_resources"])
        for record in provenance["preserved_resources"]:
            with self.subTest(resource=record["candidate_path"]):
                path = CANDIDATE / record["candidate_path"]
                self.assertTrue(path.resolve().is_relative_to(SKILL.resolve()))
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), record["sha256"])
                source_path = Path(record["source_path"]).relative_to("plugins/happy-coding/skills")
                self.assertEqual(path.read_bytes(), (BASELINE / source_path).read_bytes())

    def test_installed_tree_contains_only_declared_skill_resources(self) -> None:
        provenance = json.loads((CANDIDATE / "provenance.json").read_text(encoding="utf-8"))
        declared = {
            record["candidate_path"]
            for record in provenance["preserved_resources"] + provenance["adapted_resources"]
        }
        actual = {path.relative_to(CANDIDATE).as_posix() for path in SKILL.rglob("*") if path.is_file()}
        self.assertEqual(actual, declared)

    def test_executable_surface_is_unchanged_from_baseline(self) -> None:
        baseline = BASELINE / "implement"
        expected = {path.relative_to(baseline) for path in baseline.rglob("*.py")}
        actual = {path.relative_to(SKILL) for path in SKILL.rglob("*.py")}
        self.assertEqual(actual, expected)
        for relative in expected:
            with self.subTest(helper=str(relative)):
                self.assertEqual((SKILL / relative).read_bytes(), (baseline / relative).read_bytes())

    def test_baseline_entrypoint_digest_is_pinned(self) -> None:
        provenance = json.loads((CANDIDATE / "provenance.json").read_text(encoding="utf-8"))
        self.assertEqual(
            provenance["baseline_entrypoint_sha256"],
            "9ff5265ff752ce8186e0be61db1b7852b480a77ae4db68c3385ac862b534b653",
        )
        self.assertEqual(
            hashlib.sha256((BASELINE / "implement/SKILL.md").read_bytes()).hexdigest(),
            provenance["baseline_entrypoint_sha256"],
        )


class BundledArtifactCheckpointTests(unittest.TestCase):
    """The copied helper must still execute correctly after isolated installation."""

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        root = Path(self.temporary.name)
        installed = root / "skills" / "implement"
        shutil.copytree(SKILL, installed)
        checkpoint = installed / "checkpoints" / "contract_verify.py"
        name = "lean_candidate_checkpoint_test"
        spec = importlib.util.spec_from_file_location(name, checkpoint)
        if spec is None or spec.loader is None:
            raise AssertionError("bundled checkpoint is not importable")
        self.checkpoint = importlib.util.module_from_spec(spec)
        sys.modules[name] = self.checkpoint
        self.addCleanup(sys.modules.pop, name, None)
        spec.loader.exec_module(self.checkpoint)
        self.repo = root / "target"
        self.repo.mkdir()

    def plan(self, checksum: str | None) -> dict:
        return {
            "dependencies": {
                "contracts": {
                    "requires": [{
                        "source_repo": "synthetic-upstream",
                        "artifact": "public-api",
                        "path": "api.json",
                        "checksum": checksum,
                    }]
                }
            }
        }

    def test_no_dependencies_require_no_artifact(self) -> None:
        result = self.checkpoint.verify_contracts({}, self.repo)
        self.assertEqual(result.status, "PASS")
        self.assertEqual(list(self.repo.iterdir()), [])

    def test_missing_required_artifact_fails(self) -> None:
        plan = self.plan(None)
        result = self.checkpoint.verify_contracts(plan, self.repo)
        self.assertEqual(result.status, "FAIL")
        self.assertIn("Missing artifact", result.reason)
        self.assertIsNone(plan["dependencies"]["contracts"]["requires"][0]["checksum"])

    def test_first_verification_records_content_digest(self) -> None:
        content = b'{"version": 1}\n'
        (self.repo / "api.json").write_bytes(content)
        plan = self.plan(None)
        result = self.checkpoint.verify_contracts(plan, self.repo)
        self.assertEqual(result.status, "PASS")
        self.assertEqual(
            plan["dependencies"]["contracts"]["requires"][0]["checksum"],
            hashlib.sha256(content).hexdigest(),
        )

    def test_changed_artifact_fails_without_rebaselining(self) -> None:
        expected = hashlib.sha256(b'{"version": 1}\n').hexdigest()
        (self.repo / "api.json").write_bytes(b'{"version": 2}\n')
        plan = self.plan(expected)
        result = self.checkpoint.verify_contracts(plan, self.repo)
        self.assertEqual(result.status, "FAIL")
        self.assertIn("Checksum mismatch", result.reason)
        self.assertEqual(plan["dependencies"]["contracts"]["requires"][0]["checksum"], expected)

    def test_matching_artifact_passes(self) -> None:
        content = b'{"version": 1}\n'
        (self.repo / "api.json").write_bytes(content)
        result = self.checkpoint.verify_contracts(self.plan(hashlib.sha256(content).hexdigest()), self.repo)
        self.assertEqual(result.status, "PASS")


if __name__ == "__main__":
    unittest.main()
