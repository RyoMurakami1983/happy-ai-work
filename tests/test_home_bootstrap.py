from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = (
    ROOT / "plugins" / "happy-core" / "skills" / "home-bootstrap" / "scripts" / "home_bootstrap.py"
)
SPEC = importlib.util.spec_from_file_location("home_bootstrap", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class HomeBootstrapTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
