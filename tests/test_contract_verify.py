"""Regression checks for the limited multi-repo contract checkpoint."""

from __future__ import annotations

import hashlib
import importlib.util
import sys
import tempfile
import unittest
from collections.abc import Callable
from copy import deepcopy
from pathlib import Path
from typing import Any
from unittest.mock import patch

import yaml

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "plugins/happy-coding/skills/implement/checkpoints/contract_verify.py"
SPEC = importlib.util.spec_from_file_location("contract_verify", SCRIPT)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("could not load contract checkpoint module")
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class ContractVerificationTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory(prefix="contract-verify-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.plan_path = self.root / "plan.md"
        self.artifact = self.root / "api.json"
        self.artifact.write_bytes(b'{"version": 1}\n')
        self.checksum = hashlib.sha256(self.artifact.read_bytes()).hexdigest()
        self.metadata: dict[str, Any] = {
            "id": "fleet-plan-059",
            "title": "契約検証",
            "status": "approved",
            "owner": "reviewer",
            "acceptance": [{"id": "AC-001", "criterion": "Preserve external metadata"}],
            "extension": {"owners": ["reviewer"], "optional": None, "enabled": False},
            "project_context": {"repo": "consumer", "unknown": {"keep": "context"}},
            "dependencies": {
                "blocking": ["upstream"],
                "unknown": {"keep": "dependency"},
                "contracts": {
                    "provides": [{"artifact": "client", "checksum": "keep-provided-checksum"}],
                    "unknown": ["keep-contract-metadata"],
                    "requires": [{
                        "source_repo": "upstream",
                        "artifact": "api",
                        "path": "api.json",
                        "version": "1",
                        "checksum": None,
                        "unknown": {"keep": "requirement"},
                    }],
                },
            },
        }

    def write_plan(self, *, newline: str = "\n", body: bytes = b"\n# Plan\n\nKeep **this** body.\n") -> bytes:
        front_matter = yaml.safe_dump(self.metadata, sort_keys=False, allow_unicode=True, line_break=newline)
        content = ("---" + newline + front_matter + "---" + newline).encode("utf-8") + body
        self.plan_path.write_bytes(content)
        return content

    def read_metadata(self) -> dict[str, Any]:
        return yaml.safe_load(self.plan_path.read_text(encoding="utf-8").split("---", 2)[1])

    def caller_plan(self) -> dict[str, Any]:
        # A caller may only know the checkpoint's required schema fields.
        requires = deepcopy(self.metadata["dependencies"]["contracts"]["requires"])
        for require in requires:
            require.pop("unknown", None)
        return {"dependencies": {"contracts": {"requires": requires}}}

    def assert_no_write(self, action: Callable[[], Any]) -> None:
        before = (self.plan_path.read_bytes(), self.plan_path.stat().st_mtime_ns)
        with patch.object(Path, "write_bytes") as write_bytes, patch.object(Path, "write_text") as write_text:
            action()
        write_bytes.assert_not_called()
        write_text.assert_not_called()
        self.assertEqual((self.plan_path.read_bytes(), self.plan_path.stat().st_mtime_ns), before)

    def test_null_checksum_update_preserves_all_unknown_metadata(self) -> None:
        self.write_plan()
        plan = self.caller_plan()
        plan["project_context"] = {"repo": "stale-context-must-not-overwrite-disk"}
        plan["dependencies"]["blocking"] = []

        result = MODULE.verify_contracts(plan, self.root)

        self.assertEqual(result.status, "PASS", result.reason)
        expected = deepcopy(self.metadata)
        expected["dependencies"]["contracts"]["requires"][0]["checksum"] = self.checksum
        self.assertEqual(self.read_metadata(), expected)
        self.assertEqual(plan["dependencies"]["contracts"]["requires"][0]["checksum"], self.checksum)

    def test_existing_and_null_checksums_are_handled_together(self) -> None:
        existing = deepcopy(self.metadata["dependencies"]["contracts"]["requires"][0])
        existing.update({"artifact": "pinned-api", "checksum": self.checksum})
        self.metadata["dependencies"]["contracts"]["requires"].insert(0, existing)
        self.write_plan()

        result = MODULE.verify_contracts(self.caller_plan(), self.root)

        self.assertEqual(result.status, "PASS", result.reason)
        expected = deepcopy(self.metadata)
        expected["dependencies"]["contracts"]["requires"][1]["checksum"] = self.checksum
        self.assertEqual(self.read_metadata(), expected)

    def test_missing_checksum_field_is_initialized_without_replacing_requirement(self) -> None:
        del self.metadata["dependencies"]["contracts"]["requires"][0]["checksum"]
        self.write_plan()

        result = MODULE.verify_contracts(self.caller_plan(), self.root)

        self.assertEqual(result.status, "PASS", result.reason)
        expected = deepcopy(self.metadata)
        expected["dependencies"]["contracts"]["requires"][0]["checksum"] = self.checksum
        self.assertEqual(self.read_metadata(), expected)

    def test_matching_checksum_does_not_rewrite_formatted_front_matter(self) -> None:
        self.metadata["dependencies"]["contracts"]["requires"][0]["checksum"] = self.checksum
        content = self.write_plan()
        self.plan_path.write_bytes(content.replace(b"title:", b"# Keep this comment and formatting\ntitle:", 1))

        def verify() -> None:
            result = MODULE.verify_contracts(self.caller_plan(), self.root)
            self.assertEqual(result.status, "PASS", result.reason)

        self.assert_no_write(verify)

    def test_checksum_initialization_is_idempotent_after_reload(self) -> None:
        self.write_plan()
        first = MODULE.verify_contracts(self.caller_plan(), self.root)
        self.assertEqual(first.status, "PASS", first.reason)

        def verify_again() -> None:
            result = MODULE.verify_contracts(self.read_metadata(), self.root)
            self.assertEqual(result.status, "PASS", result.reason)

        self.assert_no_write(verify_again)

    def test_body_bytes_and_line_endings_survive_checksum_update(self) -> None:
        bodies = (
            b"",
            b"\n# Plan\n---\n\n```yaml\nkey: value\n```\n",
            "\r\n日本語  \r\nNo final newline".encode(),
        )
        for newline in ("\n", "\r\n"):
            for body in bodies:
                with self.subTest(newline=newline, body=body):
                    self.write_plan(newline=newline, body=body)
                    result = MODULE.verify_contracts(self.caller_plan(), self.root)
                    self.assertEqual(result.status, "PASS", result.reason)
                    content = self.plan_path.read_bytes()
                    self.assertEqual(content.split(("---" + newline).encode(), 2)[2], body)
                    self.assertTrue(content.startswith(("---" + newline).encode()))

    def test_saving_partial_reordered_contracts_changes_only_matching_checksums(self) -> None:
        other = deepcopy(self.metadata["dependencies"]["contracts"]["requires"][0])
        other.update({"version": "2", "checksum": "keep-other-version"})
        self.metadata["dependencies"]["contracts"]["requires"].insert(0, other)
        self.write_plan()
        plan = self.caller_plan()
        plan["dependencies"]["contracts"]["requires"].pop(0)
        plan["dependencies"]["contracts"]["requires"][0]["checksum"] = self.checksum

        MODULE.save_plan_with_updated_checksums(self.plan_path, plan)

        expected = deepcopy(self.metadata)
        expected["dependencies"]["contracts"]["requires"][1]["checksum"] = self.checksum
        self.assertEqual(self.read_metadata(), expected)

    def test_aliases_in_unrelated_metadata_keep_their_original_values(self) -> None:
        self.metadata["reviewed_dependencies"] = self.metadata["dependencies"]
        original_dependencies = deepcopy(self.metadata["dependencies"])
        self.write_plan()

        result = MODULE.verify_contracts(self.caller_plan(), self.root)

        self.assertEqual(result.status, "PASS", result.reason)
        actual = self.read_metadata()
        self.assertEqual(actual["reviewed_dependencies"], original_dependencies)
        self.assertEqual(actual["dependencies"]["contracts"]["requires"][0]["checksum"], self.checksum)

    def test_saving_no_checksum_changes_does_not_rewrite(self) -> None:
        self.write_plan()
        self.assert_no_write(lambda: MODULE.save_plan_with_updated_checksums(self.plan_path, self.caller_plan()))
        self.assert_no_write(lambda: MODULE.save_plan_with_updated_checksums(self.plan_path, {}))

    def test_verification_failure_never_writes_plan(self) -> None:
        for failure in ("missing", "checksum_mismatch"):
            with self.subTest(failure=failure):
                bad = deepcopy(self.metadata["dependencies"]["contracts"]["requires"][0])
                bad["artifact"] = "bad-api"
                if failure == "missing":
                    bad["path"] = "missing.json"
                else:
                    bad["checksum"] = "wrong-checksum"
                metadata = deepcopy(self.metadata)
                metadata["dependencies"]["contracts"]["requires"].append(bad)
                self.write_plan()

                def verify_failure(plan: dict[str, Any] = metadata) -> None:
                    result = MODULE.verify_contracts(plan, self.root)
                    self.assertEqual(result.status, "FAIL", result.reason)

                self.assert_no_write(verify_failure)

    def test_no_required_contracts_does_not_rewrite_plan(self) -> None:
        self.write_plan()
        self.assert_no_write(lambda: MODULE.verify_contracts({}, self.root))

    def test_missing_front_matter_or_closing_delimiter_is_not_overwritten(self) -> None:
        plan = self.caller_plan()
        plan["dependencies"]["contracts"]["requires"][0]["checksum"] = self.checksum
        for content in (b"# Plan\n\n---\nKeep this body.\n", b"---\ntitle: Unfinished\n", b""):
            with self.subTest(content=content):
                self.plan_path.write_bytes(content)
                self.assert_no_write(lambda: MODULE.save_plan_with_updated_checksums(self.plan_path, plan))

    def test_verifying_without_plan_file_does_not_create_it(self) -> None:
        result = MODULE.verify_contracts(self.caller_plan(), self.root)
        self.assertEqual(result.status, "PASS", result.reason)
        self.assertFalse(self.plan_path.exists())


if __name__ == "__main__":
    unittest.main()
