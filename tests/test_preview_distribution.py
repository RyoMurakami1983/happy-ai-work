import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import validate_repo  # noqa: E402


class PreviewDistributionTests(unittest.TestCase):
    def test_preview_requires_opt_in(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            entries = []
            for name in ("happy-core", "happy-coding", "happy-preview"):
                manifest = root / "plugins" / name / ".codex-plugin" / "plugin.json"
                manifest.parent.mkdir(parents=True)
                manifest.write_text(
                    json.dumps({"name": name, "skills": "./skills/"}), encoding="utf-8"
                )
                entries.append({
                    "name": name,
                    "source": {"path": f"./plugins/{name}"},
                    "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
                })
            marketplace = root / ".agents" / "plugins" / "marketplace.json"
            marketplace.parent.mkdir(parents=True)
            for installation in ("AVAILABLE", "INSTALLED_BY_DEFAULT"):
                entries[-1]["policy"] = {
                    "installation": installation, "authentication": "ON_INSTALL"
                }
                marketplace.write_text(json.dumps({
                    "name": "happy-ai-work-marketplace", "plugins": entries
                }), encoding="utf-8")
                with patch.object(validate_repo, "ROOT", root):
                    failures: list[str] = []
                    validate_repo.validate_json(failures)
                if installation == "AVAILABLE":
                    self.assertEqual(failures, [])
                else:
                    self.assertEqual(failures, [
                        "happy-preview: installation must be opt-in (AVAILABLE)"
                    ])

            del entries[-1]["name"]
            marketplace.write_text(json.dumps({
                "name": "happy-ai-work-marketplace", "plugins": entries
            }), encoding="utf-8")
            with patch.object(validate_repo, "ROOT", root):
                failures = []
                validate_repo.validate_json(failures)
            self.assertEqual(failures, [
                "marketplace plugin order or names are incorrect",
                "marketplace entry: name must be a valid plugin name",
            ])

    def test_invalid_policy_is_reported_without_crashing(self) -> None:
        original = json.loads(
            (validate_repo.ROOT / ".agents/plugins/marketplace.json").read_text(encoding="utf-8")
        )
        for invalid_policy in (None, [], "AVAILABLE", 42):
            with self.subTest(policy=invalid_policy), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                for entry in original["plugins"]:
                    manifest = root / "plugins" / entry["name"] / ".codex-plugin/plugin.json"
                    manifest.parent.mkdir(parents=True)
                    manifest.write_text(json.dumps({
                        "name": entry["name"], "skills": "./skills/"
                    }), encoding="utf-8")
                original["plugins"][-1]["policy"] = invalid_policy
                marketplace = root / ".agents/plugins/marketplace.json"
                marketplace.parent.mkdir(parents=True)
                marketplace.write_text(json.dumps(original), encoding="utf-8")
                with patch.object(validate_repo, "ROOT", root):
                    failures: list[str] = []
                    validate_repo.validate_json(failures)
                self.assertEqual(failures, [
                    "happy-preview: marketplace policy must be an object",
                    "happy-preview: installation must be opt-in (AVAILABLE)",
                    "happy-preview: marketplace policy is incomplete",
                ])

    def test_preview_cannot_duplicate_regular_skill(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for plugin in ("happy-coding", "happy-preview"):
                skill = root / "plugins" / plugin / "skills" / "sample" / "SKILL.md"
                skill.parent.mkdir(parents=True)
                skill.write_text(
                    "---\nname: sample\ndescription: Sample workflow.\n---\nBody.\n",
                    encoding="utf-8",
                )
            with patch.object(validate_repo, "ROOT", root):
                failures: list[str] = []
                validate_repo.validate_skills(failures)
            self.assertTrue(any("duplicate skills" in failure for failure in failures))
