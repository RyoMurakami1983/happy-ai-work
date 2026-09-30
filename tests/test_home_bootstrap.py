from __future__ import annotations

import importlib.util
import os
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
    def run_cli(self, target: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--target", str(target), *arguments],
            capture_output=True, text=True, encoding="utf-8",
            env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        )

    def test_cli_update_removes_enabled_yohaku(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "AGENTS.md"
            target.write_text(
                f"{MODULE.START}\nold\n<!-- happy-ai-work:yohaku=enabled -->\n"
                f"- old startup instruction\n{MODULE.END}\n", encoding="utf-8",
            )
            subprocess.run(
                [sys.executable, str(SCRIPT), "--target", str(target), "--apply"],
                check=True, capture_output=True,
            )
            updated = target.read_text(encoding="utf-8")
            self.assertNotIn("happy-ai-work:yohaku", updated)
            self.assertNotIn("startup instruction", updated)
            self.assertNotIn("新しい会話の開始時", updated)

    def test_cli_migrates_old_preferences_without_revival(self) -> None:
        before = b"# Personal\r\n<!-- happy-ai-work:yohaku=outside -->\r\n\r\n"
        after = b"\r\n# Local\r\nkeep  \r\n"
        for state in ("enabled", "disabled", "unknown", "enabled --><!-- happy-ai-work:yohaku=disabled"):
            with self.subTest(state=state), tempfile.TemporaryDirectory() as d:
                target = Path(d) / "AGENTS.md"
                original = before + (
                    f"{MODULE.START}\n<!-- happy-ai-work:yohaku={state} -->\n"
                    f"- old startup instruction\n{MODULE.END}"
                ).encode() + after
                target.write_bytes(original)
                dry = self.run_cli(target, "--dry-run")
                self.assertEqual(dry.returncode, 0, dry.stderr)
                self.assertEqual(target.read_bytes(), original)
                self.assertEqual(list(Path(d).glob("*.bak")), [])
                result = self.run_cli(target, "--apply")
                self.assertEqual(result.returncode, 0, result.stderr)
                content = target.read_bytes()
                self.assertTrue(content.startswith(before))
                self.assertTrue(content.endswith(after))
                body = MODULE.managed_body(content.decode())
                self.assertNotIn("yohaku", body)
                self.assertNotIn("startup instruction", body)
                backups = list(Path(d).glob("*.bak"))
                self.assertEqual(len(backups), 1)
                self.assertEqual(backups[0].read_bytes(), original)
                result = self.run_cli(target, "--apply")
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(target.read_bytes(), content)
                self.assertEqual(list(Path(d).glob("*.bak")), backups)

    def test_cli_first_dry_run_does_not_create_directory(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            target = Path(d) / "new" / "AGENTS.md"
            result = self.run_cli(target)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertNotIn("yohaku=", result.stdout)
            self.assertFalse(target.parent.exists())

    def test_removed_option_cannot_restore_startup(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            target = Path(d) / "AGENTS.md"
            result = self.run_cli(target, "--apply", "--yohaku", "enable")
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(target.exists())

    def test_cli_rejects_invalid_markers_in_existing_or_template(self) -> None:
        invalid = (MODULE.START, f"{MODULE.END}\n{MODULE.START}",
                   f"{MODULE.START}\n{MODULE.START}\n{MODULE.END}")
        valid = f"{MODULE.START}\nbase\n{MODULE.END}\n"
        for content in invalid:
            for location in ("existing", "template"):
                with self.subTest(content=content, location=location), tempfile.TemporaryDirectory() as d:
                    target = Path(d) / "AGENTS.md"
                    template = Path(d) / "template.md"
                    original = (content if location == "existing" else valid).encode()
                    target.write_bytes(original)
                    template.write_text(content if location == "template" else valid, encoding="utf-8")
                    result = self.run_cli(target, "--apply", "--template", str(template))
                    self.assertNotEqual(result.returncode, 0)
                    self.assertEqual(target.read_bytes(), original)
                    self.assertEqual(list(Path(d).glob("*.bak")), [])

    def test_cli_custom_template_rejects_old_startup_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            target = Path(d) / "AGENTS.md"
            template = Path(d) / "template.md"
            template.write_text(f"{MODULE.START}\n- custom{MODULE.END}", encoding="utf-8")
            result = self.run_cli(target, "--apply", "--template", str(template))
            self.assertEqual(result.returncode, 0, result.stderr)
            original = target.read_bytes()
            result = self.run_cli(target, "--apply", "--template", str(template))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(target.read_bytes(), original)
            self.assertEqual(list(Path(d).glob("*.bak")), [])
            template.write_text(
                f"{MODULE.START}\n<!-- happy-ai-work:yohaku=enabled -->\n{MODULE.END}",
                encoding="utf-8",
            )
            result = self.run_cli(target, "--apply", "--template", str(template))
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("base template", result.stderr)
            self.assertEqual(target.read_bytes(), original)
            self.assertEqual(list(Path(d).glob("*.bak")), [])

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
            dry_run = subprocess.run(
                [*command, "--dry-run"], check=True, capture_output=True,
                env={**os.environ, "PYTHONIOENCODING": "cp1252"},
            )
            self.assertIn("共通の作業方針", dry_run.stdout.decode("utf-8"))
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
