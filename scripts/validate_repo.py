#!/usr/bin/env python3
"""Validate marketplace, plugin manifests, skills, local links, and obvious secrets."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LINK_RE = re.compile(r"\[[^]]+\]\(([^)]+)\)")
SECRET_RE = re.compile(
    r"(?:gh" + r"p_|github_" + r"pat_|s" + r"k-[A-Za-z0-9_-]{20,}|AK" + r"IA[0-9A-Z]{16})"
)
REQUIRED_CODING_SKILLS = {
    "ci-debug",
    "debug",
    "deep-review",
    "design-and-plan",
    "domain-modeling",
    "dotnet",
    "dotnet-framework-bridge",
    "implement",
    "implementation-eval-gate",
    "interview-with-docs",
    "nuget-local",
    "python",
    "repo-onboarding",
    "rust",
    "tauri",
    "to-prd",
    "typescript",
    "wpf",
}
REQUIRED_CORE_SKILLS = {
    "deep-edit",
    "draft-writing",
    "furikaeri",
    "home-bootstrap",
    "interview-me",
    "skill-eval",
    "workspace-bootstrap",
    "writing-plan",
}


def fail(message: str, failures: list[str]) -> None:
    failures.append(message)


def validate_json(failures: list[str]) -> None:
    marketplace_path = ROOT / ".agents" / "plugins" / "marketplace.json"
    marketplace = json.loads(marketplace_path.read_text(encoding="utf-8"))
    if marketplace.get("name") != "happy-ai-work-marketplace":
        fail("marketplace name is incorrect", failures)
    entries = marketplace.get("plugins", [])
    if [entry.get("name") for entry in entries] != ["happy-core", "happy-coding"]:
        fail("marketplace plugin order or names are incorrect", failures)
    for entry in entries:
        name = entry["name"]
        expected_path = f"./plugins/{name}"
        if entry.get("source", {}).get("path") != expected_path:
            fail(f"{name}: marketplace source path must be {expected_path}", failures)
        policy = entry.get("policy", {})
        if not {"installation", "authentication"} <= policy.keys():
            fail(f"{name}: marketplace policy is incomplete", failures)
        manifest_path = ROOT / "plugins" / name / ".codex-plugin" / "plugin.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest.get("name") != name:
            fail(f"{name}: folder and manifest names differ", failures)
        if manifest.get("skills") != "./skills/":
            fail(f"{name}: skills path is incorrect", failures)


def validate_skills(failures: list[str]) -> None:
    skill_files = list(ROOT.glob("plugins/*/skills/*/SKILL.md"))
    coding_skills = {
        skill_file.parent.name
        for skill_file in skill_files
        if skill_file.parts[-4] == "happy-coding"
    }
    missing = REQUIRED_CODING_SKILLS - coding_skills
    if missing:
        fail(f"happy-coding: missing required skills {sorted(missing)}", failures)

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
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts:
            continue
        if path.suffix.lower() not in {".md", ".py", ".json", ".yaml", ".yml", ".toml"}:
            continue
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
    if failures:
        print("validation failed:")
        for item in failures:
            print(f"- {item}")
        return 1
    print("validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
