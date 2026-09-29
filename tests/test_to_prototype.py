from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "plugins" / "happy-preview" / "skills" / "to-prototype"
INIT_SCRIPT = SKILL / "scripts" / "init_prototype.py"
VALIDATE_SCRIPT = SKILL / "scripts" / "validate_prototype.py"
TEMPLATE = SKILL / "assets" / "starter.html"


def load_script(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


INIT = load_script("init_prototype", INIT_SCRIPT)
VALIDATE = load_script("validate_prototype", VALIDATE_SCRIPT)


class ToPrototypeTests(unittest.TestCase):
    def test_starter_is_offline_and_marks_simulated_behavior(self) -> None:
        html = INIT.render("試作 <画面>", TEMPLATE.read_text(encoding="utf-8"))
        self.assertEqual([], VALIDATE.validate_html(html))
        self.assertIn("試作 &lt;画面&gt;", html)
        self.assertIn("入力は送信・保存しません", html)
        self.assertIn("固定の表示例", html)

    def test_initializer_refuses_to_overwrite_existing_prototype(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "nested" / "prototype.html"
            command = [
                sys.executable,
                str(INIT_SCRIPT),
                "--title",
                "試作",
                "--output",
                str(output),
            ]
            created = subprocess.run(command, capture_output=True, text=True, check=False)
            self.assertEqual(0, created.returncode, created.stderr)
            first = output.read_bytes()
            again = subprocess.run(command, capture_output=True, text=True, check=False)
            self.assertNotEqual(0, again.returncode)
            self.assertEqual(first, output.read_bytes())

    def test_validator_rejects_external_assets_and_unfinished_title(self) -> None:
        html = TEMPLATE.read_text(encoding="utf-8").replace(
            "</head>", '<script src="https://example.com/app.js"></script></head>'
        )
        errors = VALIDATE.validate_html(html)
        self.assertTrue(any("プレースホルダー" in error for error in errors))
        self.assertTrue(any("外部資産" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
