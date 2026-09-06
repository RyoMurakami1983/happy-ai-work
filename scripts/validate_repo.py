#!/usr/bin/env python3
"""Validate marketplace, plugin manifests, skills, local links, and obvious secrets."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import validate_constitution
import validate_eval_manifest_links
import validate_evals

ROOT = Path(__file__).resolve().parent.parent
OWNED_ROOTS = (
    ".agents",
    ".github",
    "docs",
    "evals",
    "incubator",
    "plugins",
    "scripts",
    "tests",
)
EXCLUDED_DIRECTORY_NAMES = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "node_modules",
    "site-packages",
}
EXCLUDED_RELATIVE_PREFIXES = (
    Path("docs/local_references"),
    Path("docs/local_skill_evals"),
)
VALIDATED_SUFFIXES = {".md", ".py", ".json", ".yaml", ".yml", ".toml"}
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LINK_RE = re.compile(r"\[[^]]+\]\(([^)]+)\)")
SECRET_RE = re.compile(
    r"(?:gh" + r"p_|github_" + r"pat_|s" + r"k-[A-Za-z0-9_-]{20,}|AK" + r"IA[0-9A-Z]{16})"
)
REQUIRED_CODING_SKILLS = {
    "ci-debug",
    "coding",
    "debug-and-fix",
    "deep-review",
    "domain-modeling",
    "dotnet",
    "dotnet-framework-bridge",
    "implement",
    "implementation-plan",
    "interview-with-docs",
    "nuget-local",
    "python",
    "repo-onboarding",
    "rust",
    "tauri",
    "technical-design",
    "to-prd",
    "typescript",
    "ui-design",
    "wpf",
}
RETIRED_CODING_SKILLS = {
    "debug",
    "design-and-plan",
    "implementation-eval-gate",
}
REQUIRED_CORE_SKILLS = {
    "deep-edit",
    "draft-writing",
    "furikaeri",
    "github-issue",
    "happy-add-issue",
    "home-bootstrap",
    "improvement-loop",
    "interview-me",
    "skill-eval",
    "workspace-bootstrap",
    "writing-plan",
}


def fail(message: str, failures: list[str]) -> None:
    failures.append(message)


def is_excluded(relative_path: Path) -> bool:
    if any(part in EXCLUDED_DIRECTORY_NAMES for part in relative_path.parts):
        return True
    return any(
        relative_path == prefix or prefix in relative_path.parents
        for prefix in EXCLUDED_RELATIVE_PREFIXES
    )


def iter_owned_files(root: Path = ROOT):
    for path in sorted(root.iterdir()):
        if path.is_file() and path.suffix.lower() in VALIDATED_SUFFIXES:
            yield path
    for root_name in OWNED_ROOTS:
        owned_root = root / root_name
        if not owned_root.is_dir():
            continue
        for path in sorted(owned_root.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in VALIDATED_SUFFIXES:
                continue
            if is_excluded(path.relative_to(root)):
                continue
            yield path


def validate_json(failures: list[str]) -> None:
    marketplace_path = ROOT / ".agents" / "plugins" / "marketplace.json"
    marketplace = json.loads(marketplace_path.read_text(encoding="utf-8"))
    if not isinstance(marketplace, dict):
        fail("marketplace must be an object", failures)
        return
    if marketplace.get("name") != "happy-ai-work-marketplace":
        fail("marketplace name is incorrect", failures)
    entries = marketplace.get("plugins", [])
    if not isinstance(entries, list):
        fail("marketplace plugins must be a list", failures)
        return
    if [entry.get("name") if isinstance(entry, dict) else None for entry in entries] != [
        "happy-core", "happy-coding", "happy-preview"
    ]:
        fail("marketplace plugin order or names are incorrect", failures)
    for entry in entries:
        if not isinstance(entry, dict):
            fail("marketplace entry must be an object", failures)
            continue
        name = entry.get("name")
        if not isinstance(name, str) or not NAME_RE.fullmatch(name):
            fail("marketplace entry: name must be a valid plugin name", failures)
            continue
        expected_path = f"./plugins/{name}"
        source = entry.get("source")
        if not isinstance(source, dict) or source.get("path") != expected_path:
            fail(f"{name}: marketplace source path must be {expected_path}", failures)
        policy = entry.get("policy", {})
        if not isinstance(policy, dict):
            fail(f"{name}: marketplace policy must be an object", failures)
            policy = {}
        if name == "happy-preview" and policy.get("installation") != "AVAILABLE":
            fail("happy-preview: installation must be opt-in (AVAILABLE)", failures)
        if not {"installation", "authentication"} <= policy.keys():
            fail(f"{name}: marketplace policy is incomplete", failures)
        manifest_path = ROOT / "plugins" / name / ".codex-plugin" / "plugin.json"
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as error:
            fail(f"{name}: cannot read plugin manifest: {error}", failures)
            continue
        if not isinstance(manifest, dict):
            fail(f"{name}: plugin manifest must be an object", failures)
            continue
        if manifest.get("name") != name:
            fail(f"{name}: folder and manifest names differ", failures)
        if manifest.get("skills") != "./skills/":
            fail(f"{name}: skills path is incorrect", failures)


def validate_skills(failures: list[str]) -> None:
    skill_files = list(ROOT.glob("plugins/*/skills/*/SKILL.md"))
    preview_names = {
        path.parent.name for path in skill_files if path.parts[-4] == "happy-preview"
    }
    regular_names = {
        path.parent.name for path in skill_files if path.parts[-4] != "happy-preview"
    }
    duplicates = preview_names & regular_names
    if duplicates:
        fail(f"preview and regular plugins duplicate skills: {sorted(duplicates)}", failures)
    coding_skills = {
        skill_file.parent.name
        for skill_file in skill_files
        if skill_file.parts[-4] == "happy-coding"
    }
    missing = REQUIRED_CODING_SKILLS - coding_skills
    if missing:
        fail(f"happy-coding: missing required skills {sorted(missing)}", failures)
    retired = RETIRED_CODING_SKILLS & coding_skills
    if retired:
        fail(f"happy-coding: retired skills are still public {sorted(retired)}", failures)

    coding_policy = (
        ROOT
        / "plugins"
        / "happy-coding"
        / "skills"
        / "coding"
        / "agents"
        / "openai.yaml"
    )
    if not coding_policy.exists():
        fail("coding: agents/openai.yaml is missing", failures)
    elif "allow_implicit_invocation: false" not in coding_policy.read_text(encoding="utf-8"):
        fail("coding: implicit invocation must be disabled", failures)

    core_skills = {
        skill_file.parent.name
        for skill_file in skill_files
        if skill_file.parts[-4] == "happy-core"
    }
    missing_core = REQUIRED_CORE_SKILLS - core_skills
    if missing_core:
        fail(f"happy-core: missing required skills {sorted(missing_core)}", failures)

    incubator_skills = list((ROOT / "incubator").rglob("SKILL.md"))
    if incubator_skills:
        fail("incubator must not contain discoverable SKILL.md files", failures)

    for skill_file in skill_files:
        text = skill_file.read_text(encoding="utf-8")
        folder_name = skill_file.parent.name
        if not NAME_RE.fullmatch(folder_name):
            fail(f"{skill_file}: invalid skill folder name", failures)
        if not text.startswith("---\n"):
            fail(f"{skill_file}: missing YAML frontmatter", failures)
            continue
        frontmatter = text.split("---", 2)[1]
        if f"name: {folder_name}" not in frontmatter:
            fail(f"{skill_file}: name does not match folder", failures)
        if "description:" not in frontmatter:
            fail(f"{skill_file}: description is missing", failures)
        if "[TODO" in text:
            fail(f"{skill_file}: unfinished TODO placeholder", failures)


def validate_links_and_secrets(failures: list[str]) -> None:
    for path in iter_owned_files():
        text = path.read_text(encoding="utf-8")
        if SECRET_RE.search(text):
            fail(f"{path}: possible secret", failures)
        if path.suffix.lower() == ".md":
            for target in LINK_RE.findall(text):
                if target.startswith(("http://", "https://", "#", "mailto:")) or "<" in target:
                    continue
                target_path = target.split("#", 1)[0]
                if target_path and not (path.parent / target_path).resolve().exists():
                    fail(f"{path}: broken local link {target}", failures)


def main() -> int:
    failures: list[str] = []
    validate_json(failures)
    validate_skills(failures)
    validate_links_and_secrets(failures)
    try:
        constitution_sync = validate_constitution.load_sync()
        for item in validate_constitution.validate_local(constitution_sync):
            fail(f"constitution: {item}", failures)
    except (OSError, json.JSONDecodeError, TypeError, ValueError) as exc:
        fail(f"constitution: {exc}", failures)
    eval_exit = validate_evals.main()
    if eval_exit:
        fail("evaluation asset validation failed", failures)
    for item in validate_eval_manifest_links.validate_records(ROOT):
        fail(f"evaluation manifest: {item}", failures)
    if failures:
        print("validation failed:")
        for item in failures:
            print(f"- {item}")
        return 1
    print("validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
