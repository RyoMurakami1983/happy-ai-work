from __future__ import annotations

import importlib.util
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "plugins" / "happy-coding" / "skills" / "html-questionnaire"
SCRIPT = SKILL / "scripts" / "render_questionnaire.py"
TEMPLATE = SKILL / "assets" / "form.html"
SPEC = importlib.util.spec_from_file_location("render_questionnaire", SCRIPT)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("could not load questionnaire renderer")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def sample_definition() -> dict:
    return {
        "id": "sample-001",
        "title": "作業手順の確認",
        "intro": "回答を確認してください。",
        "sections": [
            {
                "id": "work",
                "title": "作業",
                "questions": [
                    {
                        "id": "example",
                        "type": "long_text",
                        "prompt": "最近の作業は？",
                        "required": True,
                    },
                    {
                        "id": "review",
                        "type": "single_choice",
                        "prompt": "誰が確認しますか？",
                        "required": True,
                        "choices": [
                            {"id": "worker", "label": "作業者"},
                            {"id": "other", "label": "その他"},
                        ],
                        "note": {
                            "label": "担当者",
                            "type": "short_text",
                            "required_if": ["other"],
                        },
                    },
                ],
            }
        ],
    }


class HtmlQuestionnaireTests(unittest.TestCase):
    def setUp(self) -> None:
        self.document = sample_definition()

    def test_valid_definition_renders_offline_form_and_stable_answer_keys(self) -> None:
        self.assertEqual([], MODULE.validate_definition(self.document))
        html = MODULE.render_html(self.document, TEMPLATE.read_text(encoding="utf-8"))
        self.assertIn('data-form-id="sample-001"', html)
        self.assertIn('data-question-id="example"', html)
        self.assertIn('data-question-id="review"', html)
        self.assertIn('data-required-if="other"', html)
        self.assertIn("schema_version: 1", html)
        self.assertNotIn('src="http', html)
        self.assertNotIn('href="http', html)

    def test_rejects_duplicate_question_and_choice_ids(self) -> None:
        duplicate = deepcopy(self.document["sections"][0]["questions"][0])
        self.document["sections"][0]["questions"].append(duplicate)
        self.document["sections"][0]["questions"][1]["choices"][1]["id"] = "worker"
        errors = MODULE.validate_definition(self.document)
        self.assertTrue(any("重複" in error and ".id" in error for error in errors))
        self.assertGreaterEqual(sum("重複" in error for error in errors), 2)

    def test_rejects_missing_required_and_unknown_conditional_choice(self) -> None:
        self.document["sections"][0]["questions"][0].pop("required")
        self.document["sections"][0]["questions"][1]["note"]["required_if"] = ["missing"]
        errors = MODULE.validate_definition(self.document)
        self.assertTrue(any("required" in error for error in errors))
        self.assertTrue(any("選択肢にありません" in error for error in errors))

    def test_escapes_question_text_and_html_contexts(self) -> None:
        self.document["title"] = '</title><script>alert(1)</script>'
        self.document["sections"][0]["questions"][0]["prompt"] = '</legend><script>alert(2)</script>'
        self.document["sections"][0]["questions"][1]["choices"][0]["label"] = '<img src=x onerror=alert(3)>'
        self.document["sections"][0]["questions"][0]["placeholder"] = '" autofocus onfocus="alert(4)'
        html = MODULE.render_html(self.document, TEMPLATE.read_text(encoding="utf-8"))
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", html)
        self.assertIn("&lt;img src=x onerror=alert(3)&gt;", html)
        self.assertIn('placeholder="&quot; autofocus onfocus=&quot;alert(4)"', html)
        self.assertNotIn("<script>alert(1)</script>", html)

    def test_does_not_execute_definition_code(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            marker = folder / "executed.txt"
            source = folder / "questions.py"
            source.write_text(
                f'QUESTIONNAIRE = __import__("pathlib").Path({str(marker)!r}).write_text("x")',
                encoding="utf-8",
            )
            with self.assertRaises(ValueError):
                MODULE.load_definition(source)
            self.assertFalse(marker.exists())


if __name__ == "__main__":
    unittest.main()
