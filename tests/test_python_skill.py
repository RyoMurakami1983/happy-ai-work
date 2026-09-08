import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYTHON_SKILL = ROOT / "plugins" / "happy-coding" / "skills" / "python"


class PythonSkillTests(unittest.TestCase):
    def test_skill_routes_windows_sandbox_and_uv_preflight(self) -> None:
        skill = (PYTHON_SKILL / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn("windows-sandbox-and-uv.md", skill)
        self.assertIn("sandbox", skill)

    def test_windows_uv_preflight_avoids_retry_and_project_pollution(self) -> None:
        reference = (
            PYTHON_SKILL / "references" / "windows-sandbox-and-uv.md"
        ).read_text(encoding="utf-8")

        for required in (
            "Get-Command python",
            "Get-Command uv",
            "Get-Command uvx",
            ".venv\\pyvenv.cfg",
            "UV_CACHE_DIR",
            "sandbox外",
            "権限昇格",
            "--no-project",
            "PYTHONUTF8",
            "uv.lock",
        ):
            with self.subTest(required=required):
                self.assertIn(required, reference)

        self.assertNotIn("$HOME", reference)
        self.assertNotIn("Remove-Item -Recurse", reference)


if __name__ == "__main__":
    unittest.main()
