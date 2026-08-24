import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = ROOT / "scripts" / "validate_quality.py"
sys.path.insert(0, str(ROOT / "scripts"))

import validate_repo  # noqa: E402


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_quality", VALIDATOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load quality validator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class RepositoryTraversalTests(unittest.TestCase):
    def test_owned_files_exclude_local_and_generated_trees(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            owned = root / "plugins" / "happy-core" / "skills" / "sample" / "SKILL.md"
            owned.parent.mkdir(parents=True)
            owned.write_text("owned", encoding="utf-8")

            generated = root / "site" / "node_modules" / "package" / "README.md"
            generated.parent.mkdir(parents=True)
            generated.write_text("generated", encoding="utf-8")

            private = root / "docs" / "local_skill_evals" / "run.md"
            private.parent.mkdir(parents=True)
            private.write_text("private", encoding="utf-8")

            files = set(validate_repo.iter_owned_files(root))

            self.assertIn(owned, files)
            self.assertNotIn(generated, files)
            self.assertNotIn(private, files)


class QualityValidatorTests(unittest.TestCase):
    def test_toolchain_is_pinned_to_python_314(self) -> None:
        validator = load_validator()

        self.assertEqual(validator.PYTHON_VERSION, "3.14")
        self.assertRegex(validator.PYYAML_VERSION, r"^\d+\.\d+\.\d+$")
        self.assertRegex(validator.RUFF_VERSION, r"^\d+\.\d+\.\d+$")
        self.assertRegex(validator.TY_VERSION, r"^\d+\.\d+\.\d+$")

        command = validator.build_uvx_command(
            "ty",
            validator.TY_VERSION,
            ["check", "scripts"],
            offline=True,
            with_packages=(f"PyYAML=={validator.PYYAML_VERSION}",),
        )
        self.assertEqual(
            command[:5],
            [
                "uvx",
                "--offline",
                "--with",
                f"PyYAML=={validator.PYYAML_VERSION}",
                f"ty@{validator.TY_VERSION}",
            ],
        )


class Python314ContractTests(unittest.TestCase):
    def test_repo_and_ci_use_the_shared_python_314_entrypoint(self) -> None:
        pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        workflow = (ROOT / ".github" / "workflows" / "quality.yml").read_text(
            encoding="utf-8"
        )
        agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        validation_doc = (
            ROOT / "docs" / "development" / "QUALITY_VALIDATION.md"
        ).read_text(encoding="utf-8")

        self.assertIn('target-version = "py314"', pyproject)
        self.assertIn('[tool.ty.environment]', pyproject)
        self.assertIn('python-version = "3.14"', pyproject)

        self.assertIn("astral-sh/setup-uv@v7", workflow)
        self.assertIn('version: "0.12.5"', workflow)
        self.assertIn('python-version: "3.14"', workflow)
        self.assertIn("uv run --script scripts/validate_quality.py", workflow)
        self.assertNotIn("pip install ruff", workflow)

        for contract in (agents, readme, validation_doc, workflow):
            self.assertIn("validate_quality.py", contract)
            self.assertNotIn("validate_skill_authoring", contract)
            self.assertNotIn("--skill-creator-root", contract)


if __name__ == "__main__":
    unittest.main()
