from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = (
    ROOT / "plugins" / "happy-core" / "skills" / "home-bootstrap" / "scripts" / "home_bootstrap.py"
)
SPEC = importlib.util.spec_from_file_location("home_bootstrap", SCRIPT)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("could not load home bootstrap module")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class HomeBootstrapTests(unittest.TestCase):
    def test_first_insertion_preserves_trailing_whitespace(self) -> None:
        managed = f"{MODULE.START}\nnew\n{MODULE.END}\n"
        cases = [
            ("", ""),
            ("# Personal\nkeep  ", "\n\n"),
            ("# Personal\r\nkeep\r\n", "\n"),
            ("# Personal\r\nkeep\r\n\r\n\r\n", ""),
            ("  \r\n\t\r\n", "\n"),
        ]
        for existing, separator in cases:
            with self.subTest(existing=existing):
                updated = MODULE.merge(existing, managed)
                self.assertEqual(updated, existing + separator + managed)
                self.assertEqual(MODULE.merge(updated, managed), updated)

    def test_adds_managed_section_without_replacing_existing_content(self) -> None:
        existing = "# Personal\n\n- keep this\n"
        managed = "<!-- happy-ai-work:start -->\n- managed\n<!-- happy-ai-work:end -->\n"
        result = MODULE.merge(existing, managed)
        self.assertIn("- keep this", result)
        self.assertIn("- managed", result)

    def test_updates_only_managed_section(self) -> None:
        existing = "before\n<!-- happy-ai-work:start -->\nold\n<!-- happy-ai-work:end -->\nafter\n"
        managed = "<!-- happy-ai-work:start -->\nnew\n<!-- happy-ai-work:end -->\n"
        result = MODULE.merge(existing, managed)
        self.assertIn("before", result)
        self.assertIn("new", result)
        self.assertIn("after", result)
        self.assertNotIn("old", result)

    def test_rejects_partial_markers(self) -> None:
        with self.assertRaises(ValueError):
            MODULE.merge(
                "<!-- happy-ai-work:start -->\n",
                "<!-- happy-ai-work:start -->\nx\n<!-- happy-ai-work:end -->",
            )

    def test_managed_section_at_start_is_unchanged_on_repeated_updates(self) -> None:
        managed = (SCRIPT.parent.parent / "assets" / "AGENTS.md").read_text(encoding="utf-8")
        existing = f"{MODULE.START}\nold\n{MODULE.END}\n"
        updated = MODULE.merge(existing, managed)
        self.assertEqual(updated, managed)
        self.assertEqual(MODULE.merge(updated, managed), updated)

    def test_preserves_whitespace_outside_managed_markers(self) -> None:
        before = "# Personal\r\n\r\n- keep this  \r\n\r\n"
        after = "\r\n\r\n# Local rules\r\n\r\n- keep this too\r\n"
        existing = f"{before}{MODULE.START}\nold\n{MODULE.END}{after}"
        managed = f"{MODULE.START}\nnew\n{MODULE.END}\n"
        expected = before + managed.rstrip("\n") + after
        self.assertEqual(MODULE.merge(existing, managed), expected)

    def test_cli_dry_run_and_apply_preserve_personal_content_and_backup_bytes(self) -> None:
        before = "# 個人設定\r\n\r\n- keep this  \r\n\r\n"
        after = "\r\n\r\n# Local rules\r\n- keep this too\r\n"
        original = f"{before}{MODULE.START}\r\nold\r\n{MODULE.END}{after}".encode()
        managed = (SCRIPT.parent.parent / "assets" / "AGENTS.md").read_text(encoding="utf-8")
        expected = (before + managed.strip() + after).encode("utf-8")
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "AGENTS.md"
            target.write_bytes(original)
            command = [sys.executable, str(SCRIPT), "--target", str(target)]
            subprocess.run([*command, "--dry-run"], check=True, capture_output=True)
            self.assertEqual(target.read_bytes(), original)
            self.assertEqual(list(target.parent.glob("*.bak")), [])

            subprocess.run([*command, "--apply"], check=True, capture_output=True)
            self.assertEqual(target.read_bytes(), expected)
            backups = list(target.parent.glob("*.bak"))
            self.assertEqual(len(backups), 1)
            self.assertEqual(backups[0].read_bytes(), original)

            subprocess.run([*command, "--apply"], check=True, capture_output=True)
            self.assertEqual(target.read_bytes(), expected)
            self.assertEqual(list(target.parent.glob("*.bak")), backups)


if __name__ == "__main__":
    unittest.main()
