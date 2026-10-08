from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from copy import deepcopy
from dataclasses import dataclass
from html import escape
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
RENDERERS = {
    "design": ROOT / "plugins/happy-coding/skills/technical-design/scripts/render_design.py",
    "plan": ROOT / "plugins/happy-coding/skills/implementation-plan/scripts/render_plan.py",
}
SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 100">
<defs><marker id="arrow"><path d="M0 0L3 3"/></marker></defs>
<rect id="box" x="0" y="0" width="100" height="70"/>
<path d="M10 10L20 20" marker-end="url(#arrow)"/><text>図</text></svg>"""
CANONICAL = "# Document\n\n## Boundaries\n\nA **safe** boundary.\n\n## Unknowns\n\n- Adapter not verified.\n"


@dataclass
class DocumentFixture:
    base: Path
    script: Path
    spec: dict[str, Any]
    spec_path: Path
    output: Path

    @property
    def manifest_path(self) -> Path:
        return self.output.parent / "validation.json"

    def save_spec(self) -> None:
        self.spec_path.write_text(json.dumps(self.spec, ensure_ascii=False), encoding="utf-8")

    def html(self) -> str:
        return self.output.read_text(encoding="utf-8")

    def manifest(self) -> dict[str, Any]:
        return json.loads(self.manifest_path.read_text(encoding="utf-8"))


class HtmlInventory(HTMLParser):
    def __init__(self, html: str) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: list[str] = []
        self.links: list[str] = []
        self.tags: list[str] = []
        self.events: list[str] = []
        self.feed(html)
        self.close()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.tags.append(tag)
        for name, value in attrs:
            if name == "id" and value is not None:
                self.ids.append(value)
            if name in {"href", "src", "xlink:href"} and value is not None:
                self.links.append(value)
            if name.startswith("on"):
                self.events.append(name)

    handle_startendtag = handle_starttag


def snapshot(folder: Path) -> dict[str, tuple[bytes | None, int]]:
    return {
        path.relative_to(folder).as_posix(): (
            path.read_bytes() if path.is_file() else None,
            path.stat().st_mtime_ns,
        )
        for path in folder.rglob("*")
    }


class RenderWorkDocumentTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory(prefix="work-document-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)

    def fixture(self, kind: str, variant: str = "case") -> DocumentFixture:
        base = self.root / kind / variant
        base.mkdir(parents=True)
        (base / "canonical.md").write_text(CANONICAL, encoding="utf-8")
        (base / "diagram.svg").write_text(SVG, encoding="utf-8")
        (base / "diagram.puml").write_text("@startuml\nA -> B\n@enduml\n", encoding="utf-8")
        spec = {
            "schema_version": 1,
            "number": "037",
            "title": "汎用例 <>&",
            "subtitle": "Review the boundary before implementation.",
            "date": "2026-10-08",
            "revision": "v1",
            "status": "Draft",
            "canonical_document": "canonical.md",
            "summary_cards": [
                {
                    "title": "Responsibility",
                    "body": 'Plain <script>alert(1)</script> <img src="x" onerror="alert(2)">',
                    "source_refs": ["Boundaries"],
                }
            ],
            "diagrams": [
                {
                    "id": "architecture",
                    "title": "構成",
                    "question": "誰が責任を持つか",
                    "description": "候補の構成",
                    "svg": "diagram.svg",
                    "source": "diagram.puml",
                    "caption": "矢印は呼出しを表す",
                    "source_refs": ["Boundaries"],
                    "sync_mode": "reviewed-pair",
                    "sync_note": "Semantic review remains necessary.",
                }
            ],
            "sections": [
                {
                    "id": "limitations",
                    "title": "未確認",
                    "paragraphs": ["Not approved."],
                    "bullets": ["Check adapter."],
                    "source_refs": ["Unknowns"],
                    "table": {"headers": ["Item", "State"], "rows": [["API", "Unverified"]]},
                }
            ],
            "references": [],
        }
        fixture = DocumentFixture(
            base, RENDERERS[kind], spec, base / "spec.json", base / f"037_{kind.upper()}.html"
        )
        fixture.save_spec()
        return fixture

    def run_script(
        self,
        fixture: DocumentFixture,
        *extra: str | Path,
        expected: int = 0,
        output: Path | None = None,
        script: Path | None = None,
    ) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(
            [
                sys.executable,
                str(script or fixture.script),
                str(fixture.spec_path),
                "--output",
                str(output or fixture.output),
                *map(str, extra),
            ],
            cwd=self.root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        self.assertEqual(expected, result.returncode, result.stdout + result.stderr)
        return result

    def test_generate_escapes_inputs_and_check_preserves_bytes_and_timestamps(self) -> None:
        for kind in RENDERERS:
            with self.subTest(renderer=kind):
                fixture = self.fixture(kind)
                inputs = snapshot(fixture.base)
                self.run_script(fixture)
                generated = snapshot(fixture.base)
                for name, state in inputs.items():
                    self.assertEqual(state, generated[name], name)
                html = fixture.html()
                inventory = HtmlInventory(html)
                self.assertIn(escape(fixture.spec["summary_cards"][0]["body"]), html)
                self.assertNotIn("img", inventory.tags)
                self.assertEqual([], inventory.events)
                self.assertIn("diagram-architecture-arrow", inventory.ids)
                manifest = fixture.manifest()
                self.assertFalse(manifest["browser_runtime_verified"])
                self.assertFalse(manifest["semantic_review_verified"])
                self.assertFalse(manifest["diagram_sync"][0]["semantic_equivalence_verified"])
                before = snapshot(self.root)
                self.run_script(fixture, "--check")
                self.assertEqual(before, snapshot(self.root))

    def test_check_detects_stale_inputs_and_artifacts_without_writing(self) -> None:
        changes = ("canonical.md", "diagram.svg", "diagram.puml", "spec", "reference", "html", "manifest")
        for kind in RENDERERS:
            for change in changes:
                with self.subTest(renderer=kind, change=change):
                    fixture = self.fixture(kind, change)
                    reference = fixture.base / "requirements.md"
                    reference.write_text("# Requirements\n", encoding="utf-8")
                    fixture.spec["references"] = [{"label": "Requirements", "path": reference.name}]
                    fixture.save_spec()
                    self.run_script(fixture)
                    if change == "spec":
                        fixture.spec["revision"] = "v2"
                        fixture.save_spec()
                    elif change == "manifest":
                        manifest = fixture.manifest()
                        manifest["revision"] = "altered"
                        fixture.manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
                    else:
                        target = (
                            fixture.output if change == "html" else reference if change == "reference"
                            else fixture.base / change
                        )
                        with target.open("a", encoding="utf-8") as handle:
                            handle.write("\n")
                    before = snapshot(self.root)
                    self.run_script(fixture, "--check", expected=2)
                    self.assertEqual(before, snapshot(self.root))

    def test_check_missing_artifacts_does_not_create_output_directory(self) -> None:
        for kind in RENDERERS:
            with self.subTest(renderer=kind):
                fixture = self.fixture(kind)
                output = fixture.base / "preview" / "document.html"
                before = snapshot(self.root)
                self.run_script(fixture, "--check", output=output, expected=2)
                self.assertEqual(before, snapshot(self.root))

    def test_replacing_artifacts_requires_force_and_preserves_inputs(self) -> None:
        for kind in RENDERERS:
            with self.subTest(renderer=kind):
                fixture = self.fixture(kind)
                inputs = snapshot(fixture.base)
                self.run_script(fixture)
                before = snapshot(self.root)
                self.run_script(fixture, expected=2)
                self.assertEqual(before, snapshot(self.root))
                self.run_script(fixture, "--force")
                generated = snapshot(fixture.base)
                for name, state in inputs.items():
                    self.assertEqual(state, generated[name], name)
                self.run_script(fixture, "--check")

    def test_force_cannot_overwrite_reference_diagram_source_or_manifest_input(self) -> None:
        for kind in RENDERERS:
            for collision in ("reference", "diagram-source", "manifest"):
                with self.subTest(renderer=kind, collision=collision):
                    fixture = self.fixture(kind, collision)
                    name = "validation.json" if collision == "manifest" else "input.html"
                    input_path = fixture.base / name
                    input_path.write_text("Source must survive.\n", encoding="utf-8")
                    if collision == "diagram-source":
                        fixture.spec["diagrams"][0]["source"] = name
                    else:
                        fixture.spec["references"] = [{"label": "Input", "path": name}]
                    fixture.save_spec()
                    output = fixture.output if collision == "manifest" else input_path
                    before = snapshot(self.root)
                    self.run_script(fixture, "--force", output=output, expected=2)
                    self.assertEqual(before, snapshot(self.root))

    def test_external_and_escaping_input_paths_and_output_are_rejected(self) -> None:
        outside = self.root / "outside.md"
        outside.write_text("# Outside\n", encoding="utf-8")
        variants = ("parent", "encoded-parent", "absolute", "url", "reference-url", "output")
        for kind in RENDERERS:
            for variant in variants:
                with self.subTest(renderer=kind, variant=variant):
                    fixture = self.fixture(kind, variant)
                    output = fixture.output
                    if variant == "parent":
                        fixture.spec["canonical_document"] = "../../outside.md"
                    elif variant == "encoded-parent":
                        fixture.spec["diagrams"][0]["svg"] = "%2e%2e/diagram.svg"
                    elif variant == "absolute":
                        fixture.spec["canonical_document"] = str(fixture.base / "canonical.md")
                    elif variant == "url":
                        fixture.spec["canonical_document"] = "https://example.invalid/source.md"
                    elif variant == "reference-url":
                        fixture.spec["references"] = [{"label": "External", "path": "https://example.invalid/a"}]
                    else:
                        output = self.root / "outside.html"
                    fixture.save_spec()
                    before = snapshot(self.root)
                    self.run_script(fixture, output=output, expected=2)
                    self.assertEqual(before, snapshot(self.root))

    def test_parent_reference_requires_explicit_root_and_check_repeats_that_root(self) -> None:
        reference = self.root / "requirements.md"
        reference.write_text("# Requirements\n", encoding="utf-8")
        for kind in RENDERERS:
            with self.subTest(renderer=kind):
                fixture = self.fixture(kind)
                fixture.spec["references"] = [{"label": "Requirements", "path": "../../requirements.md"}]
                fixture.save_spec()
                before = snapshot(self.root)
                self.run_script(fixture, expected=2)
                self.assertEqual(before, snapshot(self.root))
                self.run_script(fixture, "--reference-root", self.root)
                self.assertIn('href="../../requirements.md"', fixture.html())
                self.assertEqual("../..", fixture.manifest()["reference_root"])
                before = snapshot(self.root)
                self.run_script(fixture, "--reference-root", self.root, "--check")
                self.run_script(fixture, "--check", expected=2)
                self.assertEqual(before, snapshot(self.root))

    def test_active_svg_and_invalid_fragment_graphs_produce_no_artifacts(self) -> None:
        unsafe_content = (
            "<script>alert(1)</script>",
            "<foreignObject/>",
            '<rect onclick="x"/>',
            '<use href="https://example.invalid/x"/>',
            '<style>@import "https://example.invalid/x";</style>',
            '<rect fill="url(https://example.invalid/x)"/>',
            '<style>svg{background-image:image-set("https://example.invalid/x" 1x)}</style>',
            '<rect fill="url(#missing)"/>',
            '<rect id="duplicate"/><rect id="duplicate"/>',
        )
        for kind in RENDERERS:
            for index, unsafe in enumerate(unsafe_content):
                with self.subTest(renderer=kind, svg=unsafe):
                    fixture = self.fixture(kind, str(index))
                    (fixture.base / "diagram.svg").write_text(
                        '<svg xmlns="http://www.w3.org/2000/svg">' + unsafe + "</svg>", encoding="utf-8"
                    )
                    before = snapshot(self.root)
                    self.run_script(fixture, expected=2)
                    self.assertEqual(before, snapshot(self.root))

    def test_optional_and_repeated_diagrams_keep_ids_and_local_fragments_unique(self) -> None:
        for kind in RENDERERS:
            with self.subTest(renderer=kind):
                fixture = self.fixture(kind)
                diagram = deepcopy(fixture.spec["diagrams"][0])
                fixture.spec["diagrams"] = []
                fixture.save_spec()
                self.run_script(fixture)
                self.assertNotIn("svg", HtmlInventory(fixture.html()).tags)
                self.assertEqual([], fixture.manifest()["diagram_sync"])
                fixture.spec["diagrams"] = [diagram, {**diagram, "id": "behavior"}]
                fixture.save_spec()
                self.run_script(fixture, "--force")
                inventory = HtmlInventory(fixture.html())
                self.assertEqual(len(inventory.ids), len(set(inventory.ids)))
                for ident in ("architecture", "behavior"):
                    self.assertIn(f"diagram-{ident}-arrow", inventory.ids)
                    self.assertIn(f"url(#diagram-{ident}-arrow)", fixture.html())
                self.run_script(fixture, "--check")

    def test_unsupported_markdown_preserves_complete_escaped_source(self) -> None:
        sources = (
            "# Document\n\n## Boundaries\n\n> Quote <danger>\n\n## Unknowns\n\nLast line remains.\n",
            "# Document\n\n## Boundaries\n\n[Official](https://example.invalid/docs)\n\n## Unknowns\n\nEnd.\n",
        )
        for kind in RENDERERS:
            for index, source in enumerate(sources):
                with self.subTest(renderer=kind, source=index):
                    fixture = self.fixture(kind, str(index))
                    (fixture.base / "canonical.md").write_text(source, encoding="utf-8")
                    self.run_script(fixture)
                    html = fixture.html()
                    self.assertIn("<pre>" + escape(source) + "</pre>", html)
                    self.assertEqual("full-source-fallback", fixture.manifest()["markdown_mode"])
                    for link in HtmlInventory(html).links:
                        self.assertFalse(link.startswith(("https:", "http:", "//")), link)

    def test_nested_canonical_links_and_other_number_resolve_from_nested_output(self) -> None:
        for kind in RENDERERS:
            with self.subTest(renderer=kind):
                fixture = self.fixture(kind)
                canonical_folder = fixture.base / "canonical"
                canonical_folder.mkdir()
                neighbor = canonical_folder / "neighbor.md"
                neighbor.write_text("# Neighbor\n", encoding="utf-8")
                canonical = canonical_folder / "nested.md"
                canonical.write_text(
                    "# Document\n\n## Boundaries\n\n[Neighbor](neighbor.md)\n\n## Unknowns\n\nUnverified.\n",
                    encoding="utf-8",
                )
                fixture.spec["canonical_document"] = "canonical/nested.md"
                fixture.spec["number"] = "218"
                fixture.output = fixture.base / "218_preview" / f"218_{kind.upper()}.html"
                fixture.save_spec()
                self.run_script(fixture)
                html = fixture.html()
                self.assertIn(f"{kind.upper()} 218", html)
                self.assertIn('href="../canonical/nested.md"', html)
                self.assertIn('href="../canonical/neighbor.md"', html)
                self.assertEqual("supported-subset", fixture.manifest()["markdown_mode"])
                inventory = HtmlInventory(html)
                for link in inventory.links:
                    if not link.startswith("#"):
                        self.assertTrue((fixture.output.parent / link).resolve().is_file(), link)
                before = snapshot(self.root)
                self.run_script(fixture, "--check")
                self.assertEqual(before, snapshot(self.root))

    def test_standalone_skill_copy_checks_generator_and_template_freshness(self) -> None:
        for kind in RENDERERS:
            with self.subTest(renderer=kind):
                fixture = self.fixture(kind)
                copied_skill = self.root / "portable" / kind
                shutil.copytree(
                    fixture.script.parent.parent, copied_skill, ignore=shutil.ignore_patterns("__pycache__")
                )
                script = copied_skill / "scripts" / fixture.script.name
                self.run_script(fixture, script=script)
                before = snapshot(self.root)
                self.run_script(fixture, "--check", script=script)
                self.assertEqual(before, snapshot(self.root))
                template = copied_skill / "assets" / f"{kind}.html"
                original_template = template.read_bytes()
                with template.open("a", encoding="utf-8") as handle:
                    handle.write("\n")
                self.run_script(fixture, "--check", script=script, expected=2)
                template.write_bytes(original_template)
                with script.open("a", encoding="utf-8") as handle:
                    handle.write("\n# Changed generator.\n")
                self.run_script(fixture, "--check", script=script, expected=2)

    def test_summary_sources_must_exist_once_and_json_keys_cannot_be_ambiguous(self) -> None:
        variants = ("empty-ref", "missing-ref", "duplicate-heading", "unknown-key", "duplicate-key")
        for kind in RENDERERS:
            for variant in variants:
                with self.subTest(renderer=kind, variant=variant):
                    fixture = self.fixture(kind, variant)
                    if variant == "empty-ref":
                        fixture.spec["summary_cards"][0]["source_refs"] = []
                    elif variant == "missing-ref":
                        fixture.spec["summary_cards"][0]["source_refs"] = ["Missing"]
                    elif variant == "duplicate-heading":
                        with (fixture.base / "canonical.md").open("a", encoding="utf-8") as handle:
                            handle.write("\n## Boundaries\nDuplicate heading.\n")
                    elif variant == "unknown-key":
                        fixture.spec["diagrams"][0]["run_command"] = "unrequested"
                    fixture.save_spec()
                    if variant == "duplicate-key":
                        body = fixture.spec_path.read_text(encoding="utf-8")
                        fixture.spec_path.write_text(
                            body.replace('"schema_version": 1', '"schema_version": 1, "schema_version": 1'),
                            encoding="utf-8",
                        )
                    before = snapshot(self.root)
                    self.run_script(fixture, expected=2)
                    self.assertEqual(before, snapshot(self.root))

    def test_plan_task_states_remain_readonly_and_preserve_canonical_source(self) -> None:
        fixture = self.fixture("plan")
        source = (
            "# Plan\n\n## Boundaries\n\n- [ ] Pending **preview**\n"
            "- [x] Confirmed observation\n- [X] Completed check\n\n## Unknowns\n\n- Not approved.\n"
        )
        canonical = fixture.base / "canonical.md"
        canonical.write_text(source, encoding="utf-8")
        before = (canonical.read_bytes(), canonical.stat().st_mtime_ns)
        self.run_script(fixture)
        html = fixture.html()
        self.assertIn('<span class="task-state">未完了</span> Pending <strong>preview</strong>', html)
        self.assertIn('<span class="task-state">完了</span> Confirmed observation', html)
        self.assertIn('<span class="task-state">完了</span> Completed check', html)
        self.assertNotIn("input", HtmlInventory(html).tags)
        self.assertEqual("supported-subset", fixture.manifest()["markdown_mode"])
        self.assertEqual(before, (canonical.read_bytes(), canonical.stat().st_mtime_ns))


if __name__ == "__main__":
    unittest.main()
