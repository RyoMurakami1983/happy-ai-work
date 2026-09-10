from __future__ import annotations

import importlib.util
import json
import unittest
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "plugins" / "happy-coding" / "skills" / "business-understanding-survey"
SCRIPT = SKILL / "scripts" / "validate_questionnaire.py"
TEMPLATE = SKILL / "assets" / "questionnaire-template.json"
SPEC = importlib.util.spec_from_file_location("validate_questionnaire", SCRIPT)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("could not load questionnaire validator")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class BusinessUnderstandingSurveyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.document = json.loads(TEMPLATE.read_text(encoding="utf-8"))

    def test_template_is_valid(self) -> None:
        self.assertEqual([], MODULE.validate_document(self.document))

    def test_rejects_duplicate_question_id(self) -> None:
        duplicate = deepcopy(self.document["sections"][0]["questions"][0])
        self.document["sections"][1]["questions"].append(duplicate)

        errors = MODULE.validate_document(self.document)

        self.assertTrue(any("重複" in error for error in errors))

    def test_comparison_requires_reason_and_decision_axis(self) -> None:
        question = self.document["sections"][2]["questions"][0]
        question.pop("reason_prompt")
        question.pop("decision_axis")

        errors = MODULE.validate_document(self.document)

        self.assertTrue(any("reason_prompt" in error for error in errors))
        self.assertTrue(any("decision_axis" in error for error in errors))

    def test_depends_choice_requires_condition_prompt(self) -> None:
        question = self.document["sections"][1]["questions"][0]
        question.pop("conditional_note_prompt")

        errors = MODULE.validate_document(self.document)

        self.assertTrue(any("conditional_note_prompt" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
