#!/usr/bin/env python3
"""Generate/check an offline design booklet using Python's standard library.

Markdown subset: ATX headings, plain paragraphs, simple unordered/ordered lists,
fenced code, simple pipe tables, inline code/bold, and safe local links. Other
syntax falls back to the complete escaped source with a visible notice. SVG is
supplied, not rendered from PlantUML. Static checks are not a semantic review or
a browser test. No network, browser, dependency installation, or external writes.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from datetime import date
from hashlib import sha256
from html import escape
from html.parser import HTMLParser
from pathlib import Path, PureWindowsPath
from string import Template
from urllib.parse import unquote, urlsplit


class DesignError(ValueError):
    pass


def fail(message):
    raise DesignError(message)


def sha(path):
    return sha256(path.read_bytes()).hexdigest()


def text(value, label, empty=False):
    if not isinstance(value, str) or (not empty and not value.strip()):
        fail(f"{label}: expected {'a' if empty else 'a nonempty'} string")
    return value


def shape(value, required, optional, label):
    if not isinstance(value, dict):
        fail(f"{label}: expected object")
    missing = set(required) - value.keys()
    unknown = value.keys() - set(required) - set(optional)
    if missing or unknown:
        fail(f"{label}: missing keys {sorted(missing)}; unknown keys {sorted(unknown)}")


def items(value, label):
    if not isinstance(value, list):
        fail(f"{label}: expected array")
    return value


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            fail(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def within(path, root):
    return path == root or root in path.parents


def local_file(value, base, root, label, traversal=False):
    value = text(value, label)
    decoded = unquote(value).replace("\\", "/")
    parts = decoded.split("/")
    if (
        urlsplit(decoded).scheme
        or urlsplit(decoded).netloc
        or "?" in decoded
        or "#" in decoded
        or "\x00" in decoded
        or ":" in decoded
        or decoded.startswith("/")
        or PureWindowsPath(decoded).is_absolute()
        or (not traversal and ".." in parts)
    ):
        fail(f"{label}: only permitted relative local paths are accepted")
    candidate = (base / decoded).resolve()
    if not within(candidate, root) or not candidate.is_file():
        fail(f"{label}: file missing or outside permitted root: {value}")
    return candidate


def relative(path, base):
    return Path(os.path.relpath(path, base)).as_posix()


def link(path, output):
    return escape(relative(path, output.parent), quote=True)


def heading_records(source):
    records = []
    fence = False
    counts = Counter()
    for line in source.splitlines():
        if line.startswith("```"):
            fence = not fence
            continue
        match = re.fullmatch(r"(#{1,6}) (.+)", line)
        if match and not fence:
            name = re.sub(r"\s+#+\s*$", "", match[2]).rstrip()
            slug = re.sub(r"[^\w-]+", "-", name.casefold()).strip("-") or "heading"
            counts[slug] += 1
            anchor = "md-" + slug + (f"-{counts[slug]}" if counts[slug] > 1 else "")
            records.append((name, anchor, len(match[1])))
    return records


def source_refs(value, headings, label):
    refs = items(value, label)
    if not refs:
        fail(f"{label}: at least one canonical heading reference is required")
    for index, name in enumerate(refs):
        text(name, f"{label}[{index}]")
        if headings.count(name) != 1:
            fail(f"{label}: heading must exist once in canonical MD: {name}")


def refs_html(refs, anchors):
    if not refs:
        return ""
    return (
        '<p class="caption">正本の参照：'
        + " / ".join(f'<a href="#{escape(anchors[name], quote=True)}">{escape(name)}</a>' for name in refs)
        + "</p>"
    )


SAFE_SVG = set(
    (
        "svg g defs marker path rect circle ellipse line polyline polygon text tspan title desc style "
        "clipPath linearGradient radialGradient stop pattern symbol use"
    ).split()
)
URL_CSS = re.compile(r"url\(\s*(['\"]?)(.*?)\1\s*\)", re.I)


def clean_svg(path, prefix):
    raw = path.read_text(encoding="utf-8")
    if re.search(r"<!DOCTYPE|<!ENTITY|<\?xml-stylesheet", raw, re.I):
        fail(f"{path.name}: DTD/entity/stylesheet instructions are prohibited")
    try:
        root = ET.fromstring(raw)
    except ET.ParseError as exc:
        fail(f"{path.name}: invalid SVG XML: {exc}")
    if root.tag != "{http://www.w3.org/2000/svg}svg":
        fail(f"{path.name}: expected SVG namespace root")
    ids = []
    for element in root.iter():
        tag = element.tag.rsplit("}", 1)[-1]
        if tag not in SAFE_SVG or (
            element.tag.startswith("{") and not element.tag.startswith("{http://www.w3.org/2000/svg}")
        ):
            fail(f"{path.name}: prohibited SVG element {tag}")
        for key, value in element.attrib.items():
            name = key.rsplit("}", 1)[-1]
            if name.lower().startswith("on") or name.lower() == "base":
                fail(f"{path.name}: prohibited SVG attribute {name}")
            if name == "id":
                if not re.fullmatch(r"[A-Za-z_][\w.-]*", value):
                    fail(f"{path.name}: invalid SVG id")
                ids.append(value)
            if name == "href" and not re.fullmatch(r"#[A-Za-z_][\w.-]*", value):
                fail(f"{path.name}: SVG href must refer to a local id")
            check_css(value, path.name)
        if tag == "style":
            check_css(element.text or "", path.name)
    if len(ids) != len(set(ids)):
        fail(f"{path.name}: duplicate SVG ids")
    mapping = {item: prefix + "-" + item for item in ids}

    def rewrite(value):
        def url_match(match):
            old = match[2][1:]
            if old not in mapping:
                fail(f"{path.name}: missing SVG fragment {old}")
            return "url(#" + mapping[old] + ")"

        return URL_CSS.sub(url_match, value)

    for element in root.iter():
        for key, value in list(element.attrib.items()):
            name = key.rsplit("}", 1)[-1]
            if name == "id":
                element.set(key, mapping[value])
            elif name == "href":
                if value[1:] not in mapping:
                    fail(f"{path.name}: missing SVG fragment {value}")
                element.set(key, "#" + mapping[value[1:]])
            elif name in ("aria-labelledby", "aria-describedby"):
                if any(ref not in mapping for ref in value.split()):
                    fail(f"{path.name}: missing SVG accessibility id")
                element.set(key, " ".join(mapping[ref] for ref in value.split()))
            else:
                element.set(key, rewrite(value))
        if element.tag.rsplit("}", 1)[-1] == "style":
            css = rewrite(element.text or "")
            for old, new in mapping.items():
                css = re.sub(r"#" + re.escape(old) + r"(?![\w.-])", "#" + new, css)
            element.text = css
    ET.register_namespace("", "http://www.w3.org/2000/svg")
    ET.register_namespace("xlink", "http://www.w3.org/1999/xlink")
    return ET.tostring(root, encoding="unicode")


def check_css(value, label):
    if (
        re.search(
            r"@import|(?:javascript|vbscript|https?|data|file|ftp):|//|expression\s*\(|-moz-binding|(?<![\w-])behavior\s*:",
            value,
            re.I,
        )
        or "\\" in value
    ):
        fail(f"{label}: prohibited active/escaped SVG style")
    for match in URL_CSS.finditer(value):
        if not re.fullmatch(r"#[A-Za-z_][\w.-]*", match[2]):
            fail(f"{label}: external SVG url is prohibited")
    stripped = URL_CSS.sub("", value)
    if re.search(r"url\s*\(", stripped, re.I):
        fail(f"{label}: unsupported SVG URL syntax")


class MarkdownFallback(ValueError):
    pass


def render_markdown(source, records, base, reference_root, output):
    """Preserve all source if syntax is outside the deliberately small subset."""
    record_iter = iter(records)
    lines = source.splitlines()
    result = []
    i = 0

    def inline(value):
        tokens = []

        def token(html):
            tokens.append(html)
            return f"\x00{len(tokens) - 1}\x00"

        if re.search(r"!\[|<[^>]+>|~~|(?<!\*)\*(?!\*)|(?<!`)``|(?<!\w)_[^_]+_(?!\w)", value):
            raise MarkdownFallback("対応外のインライン構文")
        value = re.sub(r"`([^`]+)`", lambda m: token("<code>" + escape(m[1]) + "</code>"), value)

        def md_link(match):
            try:
                target = local_file(match[2], base, reference_root, "Markdown link", traversal=True)
            except DesignError as exc:
                raise MarkdownFallback("外部URL・未解決リンクを含むため原文を表示") from exc
            return token(f'<a href="{link(target, output)}">{escape(match[1])}</a>')

        value = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", md_link, value)
        if "[" in value or "](" in value or "`" in value:
            raise MarkdownFallback("対応外または不完全なインライン構文")
        value = escape(value)
        value = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", value)
        if "**" in re.sub(r"<strong>.*?</strong>", "", value):
            raise MarkdownFallback("不完全な強調構文")
        return re.sub(r"\x00(\d+)\x00", lambda m: tokens[int(m[1])], value)

    try:
        while i < len(lines):
            line = lines[i]
            if not line.strip():
                i += 1
                continue
            if line.startswith("```"):
                code = []
                i += 1
                while i < len(lines) and lines[i] != "```":
                    code.append(lines[i])
                    i += 1
                if i == len(lines):
                    raise MarkdownFallback("閉じていないコードブロック")
                result.append("<pre><code>" + escape("\n".join(code)) + "</code></pre>")
                i += 1
                continue
            if re.fullmatch(r"#{1,6} .+", line):
                name, anchor, level = next(record_iter)
                level = min(level + 2, 6)
                result.append(f'<h{level} id="{anchor}">{inline(name)}</h{level}>')
                i += 1
                continue
            if line.startswith((">", "    ", "\t", "~~~")) or (line.startswith("  ") and line.strip()):
                raise MarkdownFallback("引用・入れ子・インデント等の対応外構文")
            if line.startswith("|"):
                table_lines = []
                while i < len(lines) and lines[i].startswith("|"):
                    table_lines.append(lines[i])
                    i += 1
                cells = [[part.strip() for part in row.strip().strip("|").split("|")] for row in table_lines]
                if (
                    len(cells) < 2
                    or not all(re.fullmatch(r":?-{3,}:?", c) for c in cells[1])
                    or any(len(row) != len(cells[0]) for row in cells)
                    or any("\\|" in row for row in table_lines)
                ):
                    raise MarkdownFallback("対応外の表構文")
                result.append(table_html(cells[0], cells[2:], inline))
                continue
            ordered = bool(re.match(r"^\d+\. ", line))
            if line.startswith("- ") or ordered:
                tag = "ol" if ordered else "ul"
                body = []
                while i < len(lines) and (
                    bool(re.match(r"^\d+\. ", lines[i])) if ordered else lines[i].startswith("- ")
                ):
                    body.append("<li>" + inline(re.sub(r"^(?:- |\d+\. )", "", lines[i])) + "</li>")
                    i += 1
                result.append(f"<{tag}>" + "".join(body) + f"</{tag}>")
                continue
            if re.fullmatch(r"(?:---+|\*\*\*+)", line):
                result.append("<hr>")
                i += 1
                continue
            if re.match(r"^(?:[-*+] |\d+\) |\[.+\]:|[=-]{3,}$|#{1,6}[^ ])", line):
                raise MarkdownFallback("対応外のMarkdown構文")
            result.append("<p>" + inline(line) + "</p>")
            i += 1
        return "\n".join(result), "supported-subset", None
    except (MarkdownFallback, StopIteration) as exc:
        anchors = "".join(f'<li id="{anchor}">{escape(name)}</li>' for name, anchor, _ in records)
        note = "対応外のMarkdown構文があるため、欠落を避けて正本の全文を原文表示しています。"
        return (
            ('<div class="notice"><p>' + note + "</p></div><ul>" + anchors + "</ul><pre>" + escape(source) + "</pre>"),
            "full-source-fallback",
            str(exc),
        )


def table_html(headers, rows, render=escape):
    return (
        '<div class="table-wrap"><table><thead><tr>'
        + "".join("<th>" + render(cell) + "</th>" for cell in headers)
        + "</tr></thead><tbody>"
        + "".join("<tr>" + "".join("<td>" + render(cell) + "</td>" for cell in row) + "</tr>" for row in rows)
        + "</tbody></table></div>"
    )


class StaticHTML(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids = []
        self.links = []
        self.events = []

    def handle_starttag(self, tag, attrs):
        for name, value in attrs:
            if name == "id":
                self.ids.append(value)
            if name in ("href", "src", "xlink:href") and value:
                self.links.append(value)
            if name.startswith("on"):
                self.events.append(name)

    handle_startendtag = handle_starttag


def validate_html(html, output, roots):
    parser = StaticHTML()
    parser.feed(html)
    parser.close()
    if len(parser.ids) != len(set(parser.ids)):
        fail("generated HTML has duplicate ids")
    if parser.events:
        fail("generated HTML has active event attributes")
    if re.search(r"<(?:base|iframe|object|embed|form)\b", html, re.I):
        fail("generated HTML has unsupported active/container elements")
    for style in re.findall(r"<style\b[^>]*>(.*?)</style>", html, re.I | re.S):
        check_css(style, "HTML style")
    for script in re.findall(r"<script\b[^>]*>(.*?)</script>", html, re.I | re.S):
        if re.search(r"\b(?:fetch|XMLHttpRequest|WebSocket|sendBeacon)\b|\bimport\s*\(|https?://", script, re.I):
            fail("generated HTML has unsupported network/dynamic script")
    for value in parser.links:
        if value.startswith("#"):
            if unquote(value[1:]) not in parser.ids:
                fail(f"generated HTML has missing anchor: {value}")
        else:
            decoded = unquote(value)
            if (
                urlsplit(decoded).scheme
                or urlsplit(decoded).netloc
                or "?" in decoded
                or "#" in decoded
                or decoded.startswith("/")
                or ":" in decoded
            ):
                fail(f"generated HTML has nonlocal link: {value}")
            target = (output.parent / decoded).resolve()
            if not target.is_file() or not any(within(target, root) for root in roots):
                fail(f"generated HTML has missing/out-of-root link: {value}")
    return {
        "unique_ids": True,
        "local_links_and_anchors": True,
        "svg_xml_and_passive_content": True,
        "canonical_heading_refs": True,
        "no_external_resources": True,
    }


def build(spec_path, output, reference_root):
    base = spec_path.parent
    spec = json.loads(spec_path.read_text(encoding="utf-8-sig"), object_pairs_hook=unique_object)
    required = {"schema_version", "number", "title", "subtitle", "date", "revision", "status", "canonical_document"}
    shape(spec, required, {"summary_cards", "diagrams", "sections", "references"}, "spec")
    if type(spec["schema_version"]) is not int or spec["schema_version"] != 1:
        fail("schema_version: expected integer 1")
    for key in required - {"schema_version"}:
        text(spec[key], key, empty=key == "subtitle")
    if not re.fullmatch(r"\d{3}", spec["number"]):
        fail("number: expected three-digit string, e.g. 001")
    try:
        if date.fromisoformat(spec["date"]).isoformat() != spec["date"]:
            fail("date: expected YYYY-MM-DD")
    except ValueError:
        fail("date: expected YYYY-MM-DD")
    canonical = local_file(spec["canonical_document"], base, base, "canonical_document")
    if canonical.suffix.lower() != ".md":
        fail("canonical_document: expected .md file")
    canonical_text = canonical.read_text(encoding="utf-8-sig")
    records = heading_records(canonical_text)
    headings = [name for name, _, _ in records]
    anchors = {name: anchor for name, anchor, _ in records}
    inputs = {spec_path, canonical}
    main = []
    nav = []
    reserved_ids = {"overview", "details", "references"}
    used_ids = set(reserved_ids)
    diagram_reports = []
    cards = []
    for index, card in enumerate(items(spec.get("summary_cards", []), "summary_cards")):
        label = f"summary_cards[{index}]"
        shape(card, {"title", "body", "source_refs"}, set(), label)
        source_refs(card["source_refs"], headings, label + ".source_refs")
        cards.append(
            '<article class="tile"><h3>'
            + escape(text(card["title"], label + ".title"))
            + "</h3><p>"
            + escape(text(card["body"], label + ".body"))
            + "</p>"
            + refs_html(card["source_refs"], anchors)
            + "</article>"
        )
    if cards:
        main.append(
            '<section class="card" id="overview"><h2>設計の要点</h2><div class="grid">'
            + "".join(cards)
            + "</div></section>"
        )
        nav.append('<a href="#overview">要点</a>')

    def item_id(value, label):
        value = text(value, label)
        if not re.fullmatch(r"[a-z][a-z0-9-]*", value) or value.startswith("md-") or value in used_ids:
            fail(f"{label}: invalid/reserved/duplicate id")
        used_ids.add(value)
        return value

    for index, diagram in enumerate(items(spec.get("diagrams", []), "diagrams")):
        label = f"diagrams[{index}]"
        shape(
            diagram,
            {
                "id",
                "title",
                "question",
                "description",
                "svg",
                "source",
                "caption",
                "source_refs",
                "sync_mode",
                "sync_note",
            },
            set(),
            label,
        )
        ident = item_id(diagram["id"], label + ".id")
        for key in {"title", "question", "description", "caption", "sync_note"}:
            text(diagram[key], label + "." + key)
        if diagram["sync_mode"] not in ("single-source", "reviewed-pair"):
            fail(label + ".sync_mode: invalid choice")
        source_refs(diagram["source_refs"], headings, label + ".source_refs")
        svg = local_file(diagram["svg"], base, base, label + ".svg")
        source = local_file(diagram["source"], base, base, label + ".source")
        if svg.suffix.lower() != ".svg":
            fail(label + ".svg: expected .svg file")
        inputs.update((svg, source))
        diagram_html = clean_svg(svg, "diagram-" + ident)
        main.append(
            f'<section class="card diagram-section" id="{ident}"><h2>{escape(diagram["title"])}</h2>'
            + '<p class="lead">'
            + escape(diagram["question"])
            + "</p><p>"
            + escape(diagram["description"])
            + "</p>"
            + '<div class="diagram-tools"><button type="button" class="zoom" aria-pressed="false">図を拡大</button>'
            + f'<a href="{link(svg, output)}">図だけ開く</a><a href="{link(source, output)}">図ソース</a></div>'
            + '<div class="diagram-scroll">'
            + diagram_html
            + '</div><p class="caption">'
            + escape(diagram["caption"])
            + "</p>"
            + '<p class="caption">図の同期方法（入力の申告）：'
            + escape(diagram["sync_mode"])
            + " / "
            + escape(diagram["sync_note"])
            + "</p>"
            + refs_html(diagram["source_refs"], anchors)
            + "</section>"
        )
        nav.append(f'<a href="#{ident}">{escape(diagram["title"])}</a>')
        diagram_reports.append(
            {
                "id": ident,
                "sync_mode_declared": diagram["sync_mode"],
                "sync_note": diagram["sync_note"],
                "semantic_equivalence_verified": False,
            }
        )
    for index, section in enumerate(items(spec.get("sections", []), "sections")):
        label = f"sections[{index}]"
        shape(section, {"id", "title", "paragraphs", "bullets", "source_refs"}, {"table"}, label)
        ident = item_id(section["id"], label + ".id")
        title = text(section["title"], label + ".title")
        source_refs(section["source_refs"], headings, label + ".source_refs")
        body = "".join(
            "<p>" + escape(text(value, label + ".paragraphs")) + "</p>"
            for value in items(section["paragraphs"], label + ".paragraphs")
        )
        bullets = [escape(text(value, label + ".bullets")) for value in items(section["bullets"], label + ".bullets")]
        if bullets:
            body += "<ul>" + "".join("<li>" + value + "</li>" for value in bullets) + "</ul>"
        if "table" in section:
            table = section["table"]
            shape(table, {"headers", "rows"}, set(), label + ".table")
            headers = [
                text(value, label + ".table.headers") for value in items(table["headers"], label + ".table.headers")
            ]
            if not headers:
                fail(label + ".table.headers: cannot be empty")
            rows = items(table["rows"], label + ".table.rows")
            for row in rows:
                items(row, label + ".table.row")
                if len(row) != len(headers):
                    fail(label + ".table: row/header sizes differ")
                for cell in row:
                    text(cell, label + ".table.cell", empty=True)
            body += table_html(headers, rows)
        main.append(
            f'<section class="card" id="{ident}"><h2>{escape(title)}</h2>'
            + body
            + refs_html(section["source_refs"], anchors)
            + "</section>"
        )
        nav.append(f'<a href="#{ident}">{escape(title)}</a>')
    detail, md_mode, md_notice = render_markdown(canonical_text, records, canonical.parent, reference_root, output)
    main.append(
        '<section class="card" id="details"><h2>設計の詳細（MD正本）</h2>'
        '<p>HTMLは正本を読むための派生資料です。図の意味や判断の正確性は別途レビューしてください。</p>'
        + f'<p><a href="{link(canonical, output)}">MD正本を開く</a></p><details><summary>正本の全文</summary><div>'
        + detail
        + "</div></details></section>"
    )
    nav.append('<a href="#details">詳細</a>')
    references = []
    for index, reference in enumerate(items(spec.get("references", []), "references")):
        label = f"references[{index}]"
        shape(reference, {"label", "path"}, set(), label)
        name = text(reference["label"], label + ".label")
        path = local_file(reference["path"], base, reference_root, label + ".path", traversal=True)
        inputs.add(path)
        references.append(f'<a href="{link(path, output)}">{escape(name)}</a>')
    if references:
        main.append(
            '<section class="card" id="references"><h2>関連資料</h2><div class="references">'
            + "".join(references)
            + "</div></section>"
        )
        nav.append('<a href="#references">資料</a>')
    script = Path(__file__).resolve()
    template_path = script.parent.parent / "assets" / "design.html"
    if not template_path.is_file():
        fail("missing assets/design.html")
    template_text = template_path.read_text(encoding="utf-8-sig")
    inputs.update((script, template_path))
    html = Template(template_text).substitute(
        TITLE=escape(spec["title"]),
        LABEL=escape("DESIGN " + spec["number"]),
        DATE=escape(spec["date"]),
        REVISION=escape(spec["revision"]),
        STATUS=escape(spec["status"]),
        SUBTITLE=escape(spec["subtitle"]),
        NAV="".join(nav),
        MAIN="\n".join(main),
        FOOTER=escape(f"Design {spec['number']} / {spec['revision']} / 派生資料・静的検証と意味レビューは別です。"),
    )
    static = validate_html(html, output, (base, reference_root))
    input_hashes = {relative(path, base): sha(path) for path in inputs if path not in (script, template_path)}
    manifest = {
        "schema_version": 1,
        "design_number": spec["number"],
        "revision": spec["revision"],
        "reference_root": relative(reference_root, base),
        "output": relative(output, base),
        "inputs_sha256": dict(sorted(input_hashes.items())),
        "generator_sha256": sha(script),
        "template_sha256": sha(template_path),
        "output_sha256": sha256(html.encode("utf-8")).hexdigest(),
        "static_validation": static,
        "markdown_mode": md_mode,
        "markdown_notice": md_notice,
        "diagram_sync": diagram_reports,
        "browser_runtime_verified": False,
        "semantic_review_verified": False,
        "validation_scope": "Static local generation only; no browser, network, external mutation, or UML rendering.",
    }
    return html, manifest, inputs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("spec", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument(
        "--reference-root", type=Path, help="explicit local root for references; default spec directory"
    )
    parser.add_argument("--force", action="store_true", help="replace output and validation.json, never inputs")
    parser.add_argument("--check", action="store_true", help="check current generated HTML/manifest without writing")
    args = parser.parse_args()
    try:
        spec_path = args.spec.resolve()
        if not spec_path.is_file():
            fail("spec: existing JSON file required")
        base = spec_path.parent
        output = args.output.resolve()
        reference_root = args.reference_root.resolve() if args.reference_root else base
        if not reference_root.is_dir():
            fail("reference-root: existing directory required")
        if not within(output, base) or output == base or output.suffix.lower() != ".html":
            fail("output must be an HTML file inside spec directory")
        manifest_path = (output.parent / "validation.json").resolve()
        if not within(manifest_path, base):
            fail("manifest must remain inside spec directory")
        html, manifest, inputs = build(spec_path, output, reference_root)
        if output in inputs or manifest_path.resolve() in inputs:
            fail("output or manifest would overwrite an input")
        if args.check:
            if not output.is_file() or not manifest_path.is_file():
                fail("check requires existing HTML and validation.json")
            old = json.loads(manifest_path.read_text(encoding="utf-8-sig"), object_pairs_hook=unique_object)
            if old != manifest or output.read_bytes() != html.encode("utf-8"):
                fail("check failed: stale/changed input, output, manifest, or reference-root")
            validate_html(output.read_text(encoding="utf-8"), output, (base, reference_root))
            print("CHECK PASSED: hashes, local links, anchors and static content match; no files written.")
        else:
            if (output.exists() or manifest_path.exists()) and not args.force:
                fail("output/validation.json already exists; use --force to replace generated artifacts")
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(html, encoding="utf-8", newline="\n")
            manifest_path.write_text(
                json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n"
            )
            print(f"GENERATED: {output.name} and validation.json; browser and semantic review remain unverified.")
        return 0
    except (DesignError, OSError, UnicodeError, json.JSONDecodeError, KeyError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
