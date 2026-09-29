"""Check basic offline HTML structure; interactive behavior still needs browser review."""

from __future__ import annotations

import argparse
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

RESOURCE_ATTRIBUTES = {
    "script": ("src",),
    "img": ("src", "srcset"),
    "source": ("src", "srcset"),
    "iframe": ("src",),
    "audio": ("src",),
    "video": ("src", "poster"),
    "object": ("data",),
    "embed": ("src",),
    "track": ("src",),
    "image": ("href",),
    "use": ("href",),
}
RESOURCE_LINK_RELS = {
    "stylesheet",
    "icon",
    "preload",
    "modulepreload",
    "prefetch",
    "preconnect",
    "dns-prefetch",
    "manifest",
    "mask-icon",
}
CSS_URL = re.compile(r"""url\(\s*(['"]?)(.*?)\1\s*\)""", re.IGNORECASE | re.DOTALL)
CSS_IMPORT = re.compile(r"""@import\s+(['"])(.*?)\1""", re.IGNORECASE | re.DOTALL)
CSS_COMMENT = re.compile(r"/\*.*?\*/", re.DOTALL)


def is_external(url: str) -> bool:
    url = url.strip()
    return url.startswith("//") or urlsplit(url).scheme in {"http", "https"}


def css_references(css: str) -> list[str]:
    css = CSS_COMMENT.sub("", css)
    references = [match.group(2) for match in CSS_URL.finditer(css)]
    references.extend(match.group(2) for match in CSS_IMPORT.finditer(css))
    return references


def srcset_references(srcset: str) -> list[str]:
    return [candidate.split(maxsplit=1)[0] for part in srcset.split(",")
            if (candidate := part.strip())]


class PrototypeParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.tags: set[str] = set()
        self.language = ""
        self.has_viewport = False
        self.in_title = False
        self.in_style = False
        self.title_parts: list[str] = []
        self.external_resources: list[str] = []

    def record(self, references: list[str]) -> None:
        self.external_resources.extend(url for url in references if is_external(url))

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.tags.add(tag)
        values = dict(attrs)
        if tag == "html":
            self.language = values.get("lang") or ""
        elif tag == "title":
            self.in_title = True
        elif tag == "style":
            self.in_style = True
        elif tag == "meta" and (values.get("name") or "").lower() == "viewport":
            self.has_viewport = True

        for attr in RESOURCE_ATTRIBUTES.get(tag, ()):
            value = values.get(attr) or ""
            self.record(srcset_references(value) if attr == "srcset" else [value])
        if tag == "link" and RESOURCE_LINK_RELS.intersection(
            (values.get("rel") or "").lower().split()
        ):
            self.record([values.get("href") or ""])
        if tag == "form":
            self.record([values.get("action") or ""])
        if tag == "input" and (values.get("type") or "").lower() == "image":
            self.record([values.get("src") or ""])
        if style := values.get("style"):
            self.record(css_references(style))

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self.in_title = False
        elif tag == "style":
            self.in_style = False

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title_parts.append(data)
        if self.in_style:
            self.record(css_references(data))


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
