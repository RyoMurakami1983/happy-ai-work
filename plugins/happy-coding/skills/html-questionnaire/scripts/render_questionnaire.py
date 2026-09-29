from __future__ import annotations

import argparse
import ast
import re
import sys
from html import escape
from pathlib import Path
from string import Template
from typing import Any

TEMPLATE = Path(__file__).resolve().parent.parent / "assets" / "form.html"
ID_PATTERN = re.compile(r"^[a-z][a-z0-9-]*$")
QUESTION_TYPES = {"single_choice", "short_text", "long_text"}
TEXT_TYPES = {"short_text", "long_text"}


def load_definition(path: Path) -> Any:
    """Read one literal QUESTIONNAIRE assignment without executing Python code."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    if (
        len(tree.body) != 1
        or not isinstance(tree.body[0], ast.Assign)
        or len(tree.body[0].targets) != 1
        or not isinstance(tree.body[0].targets[0], ast.Name)
        or tree.body[0].targets[0].id != "QUESTIONNAIRE"
    ):
        raise ValueError("QUESTIONNAIREへの単一のリテラル代入だけを指定してください")
    try:
        return ast.literal_eval(tree.body[0].value)
    except (ValueError, TypeError, SyntaxError, RecursionError) as exc:
        raise ValueError("QUESTIONNAIREにはPythonリテラルだけを指定してください") from exc


def _keys(
    value: dict[str, Any], required: set[str], optional: set[str], path: str, errors: list[str]
) -> None:
    named_keys = {key for key in value if isinstance(key, str)}
    if len(named_keys) != len(value):
        errors.append(f"{path}: 項目名は文字列にしてください")
    for key in sorted(required - named_keys):
        errors.append(f"{path}.{key}: 必須です")
    for key in sorted(named_keys - required - optional):
        errors.append(f"{path}.{key}: 未対応の項目です")


def _string(value: Any, path: str, errors: list[str], *, empty: bool = False) -> None:
    if not isinstance(value, str) or (not empty and not value.strip()):
        errors.append(f"{path}: {'文字列' if empty else '空でない文字列'}が必要です")


def _id(value: Any, path: str, errors: list[str]) -> str | None:
    if not isinstance(value, str) or not ID_PATTERN.fullmatch(value):
        errors.append(f"{path}: 英小文字で始まる小文字英数字・ハイフンのIDが必要です")
        return None
    return value


def validate_definition(document: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(document, dict):
        return ["QUESTIONNAIRE: 辞書が必要です"]
    _keys(document, {"id", "title", "sections"}, {"intro"}, "QUESTIONNAIRE", errors)
    _id(document.get("id"), "id", errors)
    _string(document.get("title"), "title", errors)
    if "intro" in document:
        _string(document["intro"], "intro", errors, empty=True)

    sections = document.get("sections")
    if not isinstance(sections, list) or not sections:
        return errors + ["sections: 1件以上のリストが必要です"]

    section_ids: set[str] = set()
    question_ids: set[str] = set()
    for section_index, section in enumerate(sections):
        where = f"sections[{section_index}]"
        if not isinstance(section, dict):
            errors.append(f"{where}: 辞書が必要です")
            continue
        _keys(section, {"id", "title", "questions"}, set(), where, errors)
        section_id = _id(section.get("id"), f"{where}.id", errors)
        if section_id:
            if section_id in section_ids:
                errors.append(f"{where}.id: 重複しています ({section_id})")
            section_ids.add(section_id)
        _string(section.get("title"), f"{where}.title", errors)
        questions = section.get("questions")
        if not isinstance(questions, list) or not questions:
            errors.append(f"{where}.questions: 1件以上のリストが必要です")
            continue
        for question_index, question in enumerate(questions):
            item = f"{where}.questions[{question_index}]"
            if not isinstance(question, dict):
                errors.append(f"{item}: 辞書が必要です")
                continue
            _keys(
                question,
                {"id", "type", "prompt", "required"},
                {"hint", "placeholder", "choices", "note"},
                item,
                errors,
            )
            question_id = _id(question.get("id"), f"{item}.id", errors)
            if question_id:
                if question_id in question_ids:
                    errors.append(f"{item}.id: 重複しています ({question_id})")
                question_ids.add(question_id)
            kind = question.get("type")
            if not isinstance(kind, str) or kind not in QUESTION_TYPES:
                errors.append(f"{item}.type: 対応する型を指定してください")
            _string(question.get("prompt"), f"{item}.prompt", errors)
            if not isinstance(question.get("required"), bool):
                errors.append(f"{item}.required: 真偽値が必要です")
            for optional in ("hint", "placeholder"):
                if optional in question:
                    _string(question[optional], f"{item}.{optional}", errors, empty=True)

            choice_ids: set[str] = set()
            if kind == "single_choice":
                choices = question.get("choices")
                if not isinstance(choices, list) or len(choices) < 2:
                    errors.append(f"{item}.choices: 2件以上のリストが必要です")
                else:
                    for choice_index, choice in enumerate(choices):
                        choice_path = f"{item}.choices[{choice_index}]"
                        if not isinstance(choice, dict):
                            errors.append(f"{choice_path}: 辞書が必要です")
                            continue
                        _keys(choice, {"id", "label"}, set(), choice_path, errors)
                        choice_id = _id(choice.get("id"), f"{choice_path}.id", errors)
                        if choice_id:
                            if choice_id in choice_ids:
                                errors.append(f"{choice_path}.id: 重複しています ({choice_id})")
                            choice_ids.add(choice_id)
                        _string(choice.get("label"), f"{choice_path}.label", errors)
                if "placeholder" in question:
                    errors.append(f"{item}.placeholder: 選択式には設定しません")
            elif kind in TEXT_TYPES:
                for forbidden in ("choices", "note"):
                    if forbidden in question:
                        errors.append(f"{item}.{forbidden}: 記述式には設定しません")

            if "note" in question and kind == "single_choice":
                note = question["note"]
                if not isinstance(note, dict):
                    errors.append(f"{item}.note: 辞書が必要です")
                    continue
                _keys(note, {"label", "type"}, {"required_if"}, f"{item}.note", errors)
                _string(note.get("label"), f"{item}.note.label", errors)
                note_type = note.get("type")
                if not isinstance(note_type, str) or note_type not in TEXT_TYPES:
                    errors.append(f"{item}.note.type: short_textかlong_textが必要です")
                required_if = note.get("required_if", [])
                if (
                    not isinstance(required_if, list)
                    or any(not isinstance(code, str) for code in required_if)
                ):
                    errors.append(f"{item}.note.required_if: 選択肢IDのリストが必要です")
                else:
                    if len(required_if) != len(set(required_if)):
                        errors.append(f"{item}.note.required_if: 重複しています")
                    for code in required_if:
                        if code not in choice_ids:
                            errors.append(f"{item}.note.required_if: 選択肢にありません ({code})")
    return errors


def _tag_text(value: str) -> str:
    return escape(value, quote=True)


def _render_question(question: dict[str, Any]) -> str:
    question_id = question["id"]
    control_id = f"q-{question_id}"
    legend_id = f"legend-{control_id}"
    required = " required" if question["required"] else ""
    parts = [
        f'<fieldset class="question" data-question-id="{question_id}">',
        f'<legend id="{legend_id}">{_tag_text(question["prompt"])}</legend>',
    ]
    if question.get("hint"):
        parts.append(f'<p class="hint">{_tag_text(question["hint"])}</p>')
    if question["type"] == "single_choice":
        parts.append(
            f'<select id="{control_id}" aria-labelledby="{legend_id}" '
            f'data-role="value"{required}>'
        )
        parts.append('<option value="">選択してください</option>')
        for choice in question["choices"]:
            parts.append(
                f'<option value="{choice["id"]}">{_tag_text(choice["label"])}</option>'
            )
        parts.append("</select>")
        note = question.get("note")
        if note:
            note_id = f"{control_id}-note"
            required_if = ",".join(note.get("required_if", []))
            parts.append(f'<label for="{note_id}">{_tag_text(note["label"])}</label>')
            if note["type"] == "long_text":
                parts.append(
                    f'<textarea id="{note_id}" data-role="note" '
                    f'data-required-if="{required_if}"></textarea>'
                )
            else:
                parts.append(
                    f'<input id="{note_id}" type="text" data-role="note" '
                    f'data-required-if="{required_if}">'
                )
    elif question["type"] == "long_text":
        placeholder = _tag_text(question.get("placeholder", ""))
        parts.append(
            f'<textarea id="{control_id}" aria-labelledby="{legend_id}" data-role="value" '
            f'placeholder="{placeholder}"{required}></textarea>'
        )
    else:
        placeholder = _tag_text(question.get("placeholder", ""))
        parts.append(
            f'<input id="{control_id}" aria-labelledby="{legend_id}" type="text" data-role="value" '
            f'placeholder="{placeholder}"{required}>'
        )
    parts.append("</fieldset>")
    return "\n".join(parts)


def render_html(document: dict[str, Any], template: str) -> str:
    """Render a validated definition into a standalone offline HTML document."""
    sections = []
    for section in document["sections"]:
        section_id = f'section-{section["id"]}'
        questions = "\n".join(_render_question(item) for item in section["questions"])
        sections.append(
            f'<section class="card" aria-labelledby="{section_id}">\n'
            f'<h2 id="{section_id}">{_tag_text(section["title"])}</h2>\n'
            f"{questions}\n</section>"
        )
    intro = document.get("intro", "")
    return Template(template).substitute(
        TITLE=_tag_text(document["title"]),
        INTRO=f"<p>{_tag_text(intro)}</p>" if intro else "",
        FORM_ID=document["id"],
        SECTIONS="\n".join(sections),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Python質問定義からオフラインHTML質問票を生成します")
    parser.add_argument("definition", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    if args.definition.resolve() == args.output.resolve():
        parser.error("定義ファイルと出力ファイルには異なるパスを指定してください")
    try:
        document = load_definition(args.definition)
        errors = validate_definition(document)
        if errors:
            for error in errors:
                print(f"ERROR: {error}", file=sys.stderr)
            return 1
        html = render_html(document, TEMPLATE.read_text(encoding="utf-8"))
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(html, encoding="utf-8")
    except (OSError, SyntaxError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"OK: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
