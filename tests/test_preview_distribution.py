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
                    self.assertTrue(any("opt-in" in failure for failure in failures))

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
