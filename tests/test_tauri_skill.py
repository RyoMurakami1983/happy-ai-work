import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TAURI_SKILL = ROOT / "plugins" / "happy-coding" / "skills" / "tauri"


class TauriSkillTests(unittest.TestCase):
    def test_skill_routes_windows_development_and_binary_lock_diagnosis(self) -> None:
        skill = (TAURI_SKILL / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn("windows-development-loop.md", skill)
        self.assertIn("アクセス拒否", skill)

    def test_windows_development_loop_preserves_repository_commands_and_process_safety(
        self,
    ) -> None:
        reference = (
            TAURI_SKILL / "references" / "windows-development-loop.md"
        ).read_text(encoding="utf-8")

        for required in (
            "package manager",
            "dev script",
            "Tauri major",
            "frontend build",
            "Rust build",
            "生成済みEXE",
            "bundle／installer",
            "ExecutablePath",
            "ProcessId",
            "影響",
        ):
            with self.subTest(required=required):
                self.assertIn(required, reference)

        self.assertNotIn("npm run", reference)
        self.assertNotIn("app.exe", reference)
        self.assertNotIn("taskkill /IM", reference)


if __name__ == "__main__":
    unittest.main()
