"""Check basic offline HTML structure; interactive behavior still needs browser review."""

from __future__ import annotations

import argparse
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit


class PrototypeParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.tags: set[str] = set()
        self.language = ""
        self.has_viewport = False
        self.in_title = False
        self.title_parts: list[str] = []
        self.external_resources: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.tags.add(tag)
        values = dict(attrs)
        if tag == "html":
            self.language = values.get("lang") or ""
        elif tag == "title":
            self.in_title = True
        elif tag == "meta" and (values.get("name") or "").lower() == "viewport":
            self.has_viewport = True

        resource = ""
        if tag in {"script", "img", "iframe", "audio", "video", "source"}:
            resource = values.get("src") or ""
        elif tag == "link" and (values.get("rel") or "").lower() in {
            "stylesheet", "icon", "preload", "modulepreload"
        }:
            resource = values.get("href") or ""
        if resource and (resource.startswith("//") or urlsplit(resource).scheme in {"http", "https"}):
            self.external_resources.append(resource)

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self.in_title = False

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title_parts.append(data)


def validate_html(html: str) -> list[str]:
    parser = PrototypeParser()
    parser.feed(html)
    errors: list[str] = []
    if "__TITLE__" in html:
        errors.append("未置換のtitleプレースホルダーがあります")
    if not parser.language:
        errors.append("html要素にlangを指定してください")
    if not parser.has_viewport:
        errors.append("viewportメタ情報がありません")
    for tag in ("html", "head", "body", "main"):
        if tag not in parser.tags:
            errors.append(f"{tag}要素がありません")
    if not "".join(parser.title_parts).strip():
        errors.append("title要素が空です")
    for resource in parser.external_resources:
        errors.append(f"オフラインで使えない外部資産: {resource}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("html", type=Path)
    args = parser.parse_args()
    try:
        errors = validate_html(args.html.read_text(encoding="utf-8"))
    except OSError as exc:
        parser.exit(1, f"prototype not checked: {exc}\n")
    if errors:
        for error in errors:
            print(error)
        return 1
    print("基本構造と外部資産の検証に通過しました。操作と表示はブラウザで確認してください。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
