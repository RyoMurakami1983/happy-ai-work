"""Create a one-file offline UI prototype starter without overwriting work."""

from __future__ import annotations

import argparse
from html import escape
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parent.parent / "assets" / "starter.html"
PLACEHOLDER = "__TITLE__"


def render(title: str, template: str) -> str:
    if not title.strip():
        raise ValueError("title must not be empty")
    if template.count(PLACEHOLDER) != 2:
        raise ValueError("starter template has an unexpected title placeholder count")
    return template.replace(PLACEHOLDER, escape(title.strip(), quote=True))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--title", required=True, help="Visible screen title")
    parser.add_argument("--output", required=True, type=Path, help="New HTML file")
    args = parser.parse_args()
    try:
        html = render(args.title, TEMPLATE.read_text(encoding="utf-8"))
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("x", encoding="utf-8", newline="\n") as output:
            output.write(html)
    except (OSError, ValueError) as exc:
        parser.exit(1, f"prototype not created: {exc}\n")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
