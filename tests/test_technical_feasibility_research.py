from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = (
    ROOT / "plugins/happy-preview/skills/technical-feasibility-research"
    / "scripts/init_research.py"
)


class ResearchInitializerTests(unittest.TestCase):
    def run_cli(self, title: str, output: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--title", title, "--output", str(output)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )

    def test_creates_report_and_preserves_existing_work_on_rerun(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "調査" / "report.md"
            result = self.run_cli("配布方式の成立条件", output)
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertIn("配布方式の成立条件", output.read_text(encoding="utf-8"))
            original = "# 利用者の調査結果\n実測値を記録済み。\n".encode()
            output.write_bytes(original)
            rerun = self.run_cli("別の題名", output)
            self.assertNotEqual(0, rerun.returncode)
            self.assertEqual(original, output.read_bytes())

    def test_invalid_title_does_not_create_output_or_parent(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "new" / "report.md"
            for title in ("   ", "first\nsecond", "first\rsecond"):
                with self.subTest(title=title):
                    result = self.run_cli(title, output)
                    self.assertNotEqual(0, result.returncode)
                    self.assertFalse(output.parent.exists())

    def test_directory_output_is_rejected_without_changing_contents(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            existing = output / "keep.txt"
            existing.write_bytes(b"preserve")
            result = self.run_cli("Research", output)
            self.assertNotEqual(0, result.returncode)
            self.assertEqual(b"preserve", existing.read_bytes())
            self.assertEqual([existing], list(output.iterdir()))


if __name__ == "__main__":
    unittest.main()
