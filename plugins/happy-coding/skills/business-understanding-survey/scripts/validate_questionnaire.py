from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

QUESTION_TYPES = {
    "fact_confirmation",
    "single_choice_rule",
    "tradeoff_comparison",
    "free_text_example",
}
STATUSES = {"confirmed", "inferred", "unknown", "contradicted"}


def _choice_codes(question: dict[str, Any]) -> list[str]:
    choices = question.get("choices", [])
    if not isinstance(choices, list):
        return []
    return [choice.get("code", "") for choice in choices if isinstance(choice, dict)]


def validate_document(document: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(document, dict):
        return ["root: JSON objectである必要があります"]

    metadata = document.get("metadata")
    if not isinstance(metadata, dict):
        errors.append("metadata: objectが必要です")
    else:
        for field in ("title", "purpose", "respondent_roles", "source_paths"):
            if not metadata.get(field):
                errors.append(f"metadata.{field}: 値が必要です")

    sections = document.get("sections")
    if not isinstance(sections, list) or not sections:
        return errors + ["sections: 1件以上必要です"]

    seen_ids: set[str] = set()
    for section_index, section in enumerate(sections):
        section_path = f"sections[{section_index}]"
        if not isinstance(section, dict):
            errors.append(f"{section_path}: objectである必要があります")
            continue
        questions = section.get("questions")
        if not isinstance(questions, list) or not questions:
            errors.append(f"{section_path}.questions: 1件以上必要です")
            continue

        for question_index, question in enumerate(questions):
            path = f"{section_path}.questions[{question_index}]"
            if not isinstance(question, dict):
                errors.append(f"{path}: objectである必要があります")
                continue

            question_id = question.get("id")
            if not isinstance(question_id, str) or not question_id.strip():
                errors.append(f"{path}.id: 空でない文字列が必要です")
            elif question_id in seen_ids:
                errors.append(f"{path}.id: 重複しています ({question_id})")
            else:
                seen_ids.add(question_id)

            question_type = question.get("type")
            if question_type not in QUESTION_TYPES:
                errors.append(f"{path}.type: 未対応の型です ({question_type})")

            if question.get("status") not in STATUSES:
                errors.append(f"{path}.status: confirmed/inferred/unknown/contradictedから選びます")

            for field in ("topic", "prompt", "why_it_matters", "evidence_refs"):
                if not question.get(field):
                    errors.append(f"{path}.{field}: 値が必要です")

            model_mapping = question.get("model_mapping")
            if not isinstance(model_mapping, dict) or not model_mapping.get("category"):
                errors.append(f"{path}.model_mapping.category: 更新先が必要です")

            codes = _choice_codes(question)
            if question_type == "fact_confirmation":
                required = {"confirm", "correction", "unknown"}
                if not required.issubset(codes):
                    errors.append(f"{path}.choices: confirm/correction/unknownが必要です")
                if not question.get("correction_prompt"):
                    errors.append(f"{path}.correction_prompt: 修正内容の質問が必要です")

            if question_type == "single_choice_rule":
                domain_choices = [code for code in codes if code not in {"depends", "unknown"}]
                if len(domain_choices) < 2 or "unknown" not in codes:
                    errors.append(f"{path}.choices: 具体的な選択肢2件以上とunknownが必要です")
                if "depends" in codes and not question.get("conditional_note_prompt"):
                    errors.append(f"{path}.conditional_note_prompt: dependsの条件欄が必要です")

            if question_type == "tradeoff_comparison":
                scenarios = [code for code in codes if code not in {"depends", "unknown"}]
                if not 2 <= len(scenarios) <= 3:
                    errors.append(f"{path}.choices: 比較案は2〜3件必要です")
                if not question.get("decision_axis"):
                    errors.append(f"{path}.decision_axis: 比較する判断軸が必要です")
                if not question.get("reason_prompt"):
                    errors.append(f"{path}.reason_prompt: 選択理由の質問が必要です")

            if question_type == "free_text_example":
                if "choices" in question:
                    errors.append(f"{path}.choices: 自由記述型には設定しません")
                if not question.get("example_prompt"):
                    errors.append(f"{path}.example_prompt: 具体例の観点が必要です")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="業務理解アンケートJSONを検査します")
    parser.add_argument("questionnaire", type=Path)
    args = parser.parse_args()

    try:
        document = json.loads(args.questionnaire.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}")
        return 1

    errors = validate_document(document)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print(f"OK: {args.questionnaire}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
