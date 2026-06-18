#!/usr/bin/env python3
"""Validate Company Brain skill folders without external dependencies."""
from __future__ import annotations

import sys
from pathlib import Path


EXPECTED = {
    "approve-brain-notes",
    "brain-contribute",
    "brain-health",
    "brain-intake",
    "brain-lint",
    "brain-onboard",
    "brain-operator",
    "brain-owner",
    "brain-schedule",
    "brain-setup",
    "brain-start",
    "meeting-to-brain",
    "repo-aware-poc",
    "sources-check",
}


def parse_frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError(f"{path}: missing YAML frontmatter")
    end = text.find("\n---", 4)
    if end == -1:
        raise ValueError(f"{path}: unterminated YAML frontmatter")
    data: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip('"')
    return data


def validate_skill(skill_dir: Path) -> list[str]:
    errors: list[str] = []
    name = skill_dir.name
    skill_md = skill_dir / "SKILL.md"
    agent_yaml = skill_dir / "agents" / "openai.yaml"

    if not skill_md.is_file():
        return [f"{name}: missing SKILL.md"]
    if not agent_yaml.is_file():
        errors.append(f"{name}: missing agents/openai.yaml")

    try:
        fm = parse_frontmatter(skill_md)
    except ValueError as exc:
        errors.append(str(exc))
        fm = {}

    if fm.get("name") != name:
        errors.append(f"{name}: frontmatter name must match folder name")
    if not fm.get("description"):
        errors.append(f"{name}: missing description")

    text = skill_md.read_text(encoding="utf-8")
    if "[TODO" in text or "FIXME" in text:
        errors.append(f"{name}: TODO/FIXME placeholder found")

    if agent_yaml.is_file():
        agent_text = agent_yaml.read_text(encoding="utf-8")
        if f"${name}" not in agent_text:
            errors.append(f"{name}: openai.yaml default_prompt should mention ${name}")

    return errors


def main(argv: list[str]) -> int:
    root = Path(argv[1]).expanduser().resolve() if len(argv) > 1 else Path.cwd()
    skills_root = root / "plugins" / "company-brain-harness" / "skills"
    if not skills_root.is_dir():
        print(f"error: skills root not found: {skills_root}", file=sys.stderr)
        return 2

    found = {p.name for p in skills_root.iterdir() if p.is_dir()}
    errors = []
    missing = sorted(EXPECTED - found)
    extra = sorted(found - EXPECTED)
    if missing:
        errors.append("missing skills: " + ", ".join(missing))
    if extra:
        errors.append("unexpected skills: " + ", ".join(extra))

    for skill_dir in sorted(p for p in skills_root.iterdir() if p.is_dir()):
        errors.extend(validate_skill(skill_dir))

    if errors:
        for error in errors:
            print(f"error: {error}", file=sys.stderr)
        return 1

    print(f"validated {len(EXPECTED)} skills")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
