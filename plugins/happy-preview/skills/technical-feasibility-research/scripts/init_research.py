"""Create an unassessed research report without overwriting existing work."""

from __future__ import annotations

import argparse
import sys
from io import TextIOWrapper
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parent.parent / "assets" / "research-report.md"
PLACEHOLDER = "__TITLE__"


def render(title: str, template: str) -> str:
    if not title.strip() or "\n" in title or "\r" in title:
        raise ValueError("title must be a nonempty single line")
    if template.count(PLACEHOLDER) != 1:
        raise ValueError("report template must contain exactly one title placeholder")
    return template.replace(PLACEHOLDER, title.strip())


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        if isinstance(stream, TextIOWrapper):
            stream.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--title", required=True, help="Research question or report title")
    parser.add_argument("--output", required=True, type=Path, help="New Markdown report")
    args = parser.parse_args()
    try:
        report = render(args.title, TEMPLATE.read_text(encoding="utf-8"))
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("x", encoding="utf-8", newline="\n") as output:
            output.write(report)
    except (OSError, ValueError) as exc:
        parser.exit(1, f"research report not created: {exc}\n")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
