#!/usr/bin/env python3
"""Validate synchronized, portable Code Crew release surfaces."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "plugins" / "code-crew"
SKILL_DIR = PACKAGE / "skills" / "code-crew"


class Validation:
    def __init__(self) -> None:
        self.errors: list[str] = []

    def check(self, condition: bool, message: str) -> None:
        if not condition:
            self.errors.append(message)


def load_json(path: Path, validation: Validation) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        validation.errors.append(f"{path.relative_to(ROOT)}: invalid JSON: {exc}")
        return {}

    if not isinstance(value, dict):
        validation.errors.append(f"{path.relative_to(ROOT)}: root must be an object")
        return {}
    return value


def load_frontmatter(path: Path, validation: Validation) -> dict[str, Any]:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        validation.errors.append(f"{path.relative_to(ROOT)}: cannot read: {exc}")
        return {}

    match = re.match(r"\A---\s*\n(.*?)\n---\s*(?:\n|\Z)", text, re.DOTALL)
    if not match:
        validation.errors.append(f"{path.relative_to(ROOT)}: missing YAML frontmatter")
        return {}

    try:
        value = yaml.safe_load(match.group(1))
    except yaml.YAMLError as exc:
        validation.errors.append(f"{path.relative_to(ROOT)}: invalid YAML: {exc}")
        return {}

    if not isinstance(value, dict):
        validation.errors.append(
            f"{path.relative_to(ROOT)}: frontmatter must be a mapping"
        )
        return {}
    return value


def find_marketplace_plugin(
    marketplace: dict[str, Any], path: Path, validation: Validation
) -> dict[str, Any]:
    plugins = marketplace.get("plugins")
    if not isinstance(plugins, list):
        validation.errors.append(f"{path.relative_to(ROOT)}: plugins must be a list")
        return {}

    matches = [
        plugin
        for plugin in plugins
        if isinstance(plugin, dict) and plugin.get("name") == "code-crew"
    ]
    if len(matches) != 1:
        validation.errors.append(
            f"{path.relative_to(ROOT)}: expected exactly one code-crew plugin entry"
        )
        return {}
    return matches[0]


def validate_versions(validation: Validation, skill_metadata: dict[str, Any]) -> str:
    expected = str(skill_metadata.get("version", ""))
    validation.check(
        bool(re.fullmatch(r"\d+\.\d+\.\d+", expected)),
        "SKILL.md metadata.version must be semver",
    )

    claude_marketplace = load_json(
        ROOT / ".claude-plugin" / "marketplace.json", validation
    )
    codex_marketplace = load_json(
        ROOT / ".agents" / "plugins" / "marketplace.json", validation
    )
    claude_plugin = load_json(PACKAGE / ".claude-plugin" / "plugin.json", validation)
    codex_plugin = load_json(PACKAGE / ".codex-plugin" / "plugin.json", validation)
    cursor_plugin = load_json(PACKAGE / ".cursor-plugin" / "plugin.json", validation)
    openclaw_plugin = load_json(PACKAGE / "openclaw.plugin.json", validation)
    claude_entry = find_marketplace_plugin(
        claude_marketplace,
        ROOT / ".claude-plugin" / "marketplace.json",
        validation,
    )
    codex_entry = find_marketplace_plugin(
        codex_marketplace,
        ROOT / ".agents" / "plugins" / "marketplace.json",
        validation,
    )

    versions: list[tuple[str, Any]] = [
        (".claude-plugin/marketplace.json version", claude_marketplace.get("version")),
        (
            ".claude-plugin/marketplace.json metadata.version",
            claude_marketplace.get("metadata", {}).get("version"),
        ),
        (
            "plugins/code-crew/.claude-plugin/plugin.json version",
            claude_plugin.get("version"),
        ),
        (
            "plugins/code-crew/.codex-plugin/plugin.json version",
            codex_plugin.get("version"),
        ),
        (
            "plugins/code-crew/.cursor-plugin/plugin.json version",
            cursor_plugin.get("version"),
        ),
        (
            "plugins/code-crew/openclaw.plugin.json version",
            openclaw_plugin.get("version"),
        ),
        (
            ".claude-plugin/marketplace.json code-crew version",
            claude_entry.get("version"),
        ),
    ]

    for label, value in versions:
        validation.check(
            value == expected, f"{label} is {value!r}; expected {expected!r}"
        )

    validation.check(
        codex_plugin.get("name") == "code-crew", "Codex plugin name must be code-crew"
    )
    validation.check(
        claude_plugin.get("name") == "code-crew", "Claude plugin name must be code-crew"
    )
    validation.check(
        cursor_plugin.get("name") == "code-crew", "Cursor plugin name must be code-crew"
    )
    validation.check(
        openclaw_plugin.get("id") == "code-crew", "OpenClaw plugin id must be code-crew"
    )
    validation.check(
        claude_marketplace.get("name") == "code-crew",
        "Claude marketplace name must be code-crew",
    )
    validation.check(
        claude_entry.get("source") == "./plugins/code-crew",
        "Claude marketplace code-crew source must be ./plugins/code-crew",
    )
    validation.check(
        codex_marketplace.get("name") == "code-crew",
        "Codex marketplace name must be code-crew",
    )
    validation.check(
        codex_entry.get("source") == {"source": "local", "path": "./plugins/code-crew"},
        "Codex marketplace code-crew source must point to ./plugins/code-crew",
    )
    return expected


def validate_skill(validation: Validation, frontmatter: dict[str, Any]) -> None:
    validation.check(
        frontmatter.get("name") == "code-crew", "SKILL.md name must be code-crew"
    )
    metadata = frontmatter.get("metadata")
    validation.check(isinstance(metadata, dict), "SKILL.md metadata must be a mapping")
    if isinstance(metadata, dict):
        for key, value in metadata.items():
            validation.check(
                isinstance(key, str) and isinstance(value, str),
                f"SKILL.md metadata values must be strings: {key!r}={value!r}",
            )

    required_references = [
        "artifact-format.md",
        "dijkstra.md",
        "hickey.md",
        "implementation-discipline.md",
        "knuth.md",
        "liskov.md",
        "pike.md",
        "synthesis.md",
        "torvalds.md",
        "triage.md",
        "verify.md",
    ]
    skill_text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    for filename in required_references:
        path = SKILL_DIR / "references" / filename
        validation.check(
            path.is_file(), f"missing skill reference: references/{filename}"
        )
        validation.check(
            f"references/{filename}" in skill_text,
            f"SKILL.md does not link references/{filename}",
        )

    validation.check(
        not (SKILL_DIR / "briefs").exists(), "legacy briefs/ directory must not ship"
    )
    validation.check(
        not (SKILL_DIR / "procedures").exists(),
        "legacy procedures/ directory must not ship",
    )

    for persona in ("knuth", "hickey", "torvalds", "dijkstra", "liskov", "pike"):
        source = ROOT / "agents" / f"{persona}_agent.md"
        packaged = SKILL_DIR / "references" / f"{persona}.md"
        if source.is_file() and packaged.is_file():
            validation.check(
                source.read_bytes() == packaged.read_bytes(),
                f"packaged persona differs from source brief: {persona}",
            )

    openai_yaml = SKILL_DIR / "agents" / "openai.yaml"
    validation.check(
        openai_yaml.is_file(), "missing Codex skill UI metadata: agents/openai.yaml"
    )
    if openai_yaml.is_file():
        try:
            config = yaml.safe_load(openai_yaml.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            validation.errors.append(f"agents/openai.yaml: invalid YAML: {exc}")
        else:
            interface = config.get("interface", {}) if isinstance(config, dict) else {}
            short_description = interface.get("short_description", "")
            default_prompt = interface.get("default_prompt", "")
            validation.check(
                isinstance(short_description, str)
                and 25 <= len(short_description) <= 64,
                "openai.yaml short_description must be a 25-64 character string",
            )
            validation.check(
                isinstance(default_prompt, str) and "$code-crew" in default_prompt,
                "openai.yaml default_prompt must mention $code-crew",
            )


def validate_duplicates(validation: Validation) -> None:
    rule_paths = [
        ROOT / ".cursor" / "rules" / "code-crew.mdc",
        PACKAGE / "cursor" / "code-crew.mdc",
        PACKAGE / "rules" / "code-crew.mdc",
    ]
    for path in rule_paths:
        validation.check(
            path.is_file(), f"missing Cursor rule: {path.relative_to(ROOT)}"
        )
    if all(path.is_file() for path in rule_paths):
        root_rule = (
            rule_paths[0]
            .read_text(encoding="utf-8")
            .replace(
                "For the full portable skill, install or copy `plugins/code-crew/skills/code-crew/`.",
                "For the full portable skill, install or copy <skill-root>.",
            )
        )
        for path in rule_paths[1:]:
            package_rule = path.read_text(encoding="utf-8").replace(
                "For the full portable skill from this package, install or copy `skills/code-crew/`.",
                "For the full portable skill, install or copy <skill-root>.",
            )
            validation.check(
                package_rule == root_rule,
                f"Cursor rule drift: {path.relative_to(ROOT)} differs from {rule_paths[0].relative_to(ROOT)}",
            )


def validate_portability(validation: Validation) -> None:
    release_files = [
        ROOT / "README.md",
        ROOT / "INSTALL.md",
        ROOT / "CURSOR.md",
        ROOT / "CLAUDE.md",
        ROOT / "AGENTS.md",
        ROOT / "project_workflow.md",
        ROOT / "RESEARCH.md",
        ROOT / "PRIVACY.md",
        ROOT / ".claude-plugin" / "marketplace.json",
        ROOT / ".agents" / "plugins" / "marketplace.json",
    ]
    release_files.extend(path for path in PACKAGE.rglob("*") if path.is_file())

    forbidden = {
        "macOS home path": re.compile(r"/Users/[^/\s]+/"),
        "Linux home path": re.compile(r"/home/[^/\s]+/"),
        "Windows home path": re.compile(r"[A-Za-z]:\\Users\\[^\\\s]+\\"),
        "OpenAI-style secret": re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
        "GitHub token": re.compile(r"\b(?:ghp|github_pat)_[A-Za-z0-9_]{20,}\b"),
        "AWS access key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
        "private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    }
    for path in release_files:
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for label, pattern in forbidden.items():
            validation.check(
                not pattern.search(text),
                f"{path.relative_to(ROOT)} contains a {label}",
            )


def main() -> int:
    validation = Validation()
    frontmatter = load_frontmatter(SKILL_DIR / "SKILL.md", validation)
    metadata = frontmatter.get("metadata", {}) if isinstance(frontmatter, dict) else {}
    version = validate_versions(
        validation, metadata if isinstance(metadata, dict) else {}
    )
    validate_skill(validation, frontmatter)
    validate_duplicates(validation)
    validate_portability(validation)

    if validation.errors:
        print("Release validation failed:", file=sys.stderr)
        for error in validation.errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"Release validation passed (version {version}).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
