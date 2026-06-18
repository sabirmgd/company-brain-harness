#!/usr/bin/env python3
"""Validate skill metadata for plain-English routing."""
from __future__ import annotations

import sys
from pathlib import Path


REQUIRED_TRIGGERS = {
    "approve-brain-notes": [
        "review pending notes",
        "approve these notes",
        "clear the queue",
        "promote staged",
    ],
    "brain-contribute": [
        "add what i know",
        "document my role",
        "share my process",
        "update stale facts",
    ],
    "brain-health": [
        "is the brain ready",
        "check setup",
        "verify connections",
        "readiness status",
    ],
    "brain-intake": [
        "add this to the brain",
        "ingest this doc",
        "file this note",
        "where should this go",
    ],
    "brain-lint": [
        "what is outdated",
        "find stale notes",
        "check broken links",
        "can we rely on this",
    ],
    "brain-onboard": [
        "interview me",
        "onboard me",
        "ask me questions",
        "populate the brain",
    ],
    "brain-operator": [
        "run today's brain check",
        "morning review",
        "check the queue",
        "what needs review",
    ],
    "brain-owner": [
        "i own this brain",
        "launch the company brain",
        "approve policy",
        "invite the team",
    ],
    "brain-schedule": [
        "schedule the brain check",
        "morning review",
        "automate daily checks",
        "human in the loop",
    ],
    "brain-setup": [
        "create the brain files",
        "generate the scaffold",
        "initialize a brain root",
        "run the setup step",
    ],
    "brain-start": [
        "set up my company brain",
        "help me start",
        "use the brain",
        "role is unclear",
    ],
    "meeting-to-brain": [
        "process this meeting",
        "summarize a transcript",
        "fireflies recap",
        "extract action items",
    ],
    "repo-aware-poc": [
        "build a poc",
        "prototype this",
        "where should this code live",
        "use our stack",
    ],
    "source-setup": [
        "connect gmail",
        "connect slack",
        "connect confluence",
        "scope a personal source",
    ],
    "source-sync": [
        "sync sources",
        "pull new emails",
        "pull confluence pages",
        "stage new source updates",
    ],
    "sources-check": [
        "connect a source",
        "fireflies",
        "personal account allowed",
        "capture eligibility",
    ],
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


def main(argv: list[str]) -> int:
    root = Path(argv[1]).expanduser().resolve() if len(argv) > 1 else Path.cwd()
    skills_root = root / "plugins" / "company-brain-harness" / "skills"
    routing_doc = root / "docs" / "skill-routing.md"
    errors: list[str] = []

    if not routing_doc.is_file():
        errors.append("docs/skill-routing.md is missing")
        routing_text = ""
    else:
        routing_text = routing_doc.read_text(encoding="utf-8").lower()

    for skill, triggers in REQUIRED_TRIGGERS.items():
        skill_md = skills_root / skill / "SKILL.md"
        openai_yaml = skills_root / skill / "agents" / "openai.yaml"
        if not skill_md.is_file():
            errors.append(f"{skill}: missing SKILL.md")
            continue
        if not openai_yaml.is_file():
            errors.append(f"{skill}: missing agents/openai.yaml")
            continue

        frontmatter = parse_frontmatter(skill_md)
        description = frontmatter.get("description", "")
        if "use when" not in description.lower():
            errors.append(f"{skill}: description must include 'Use when'")

        yaml_text = openai_yaml.read_text(encoding="utf-8")
        combined = f"{description}\n{yaml_text}".lower()
        missing = [trigger for trigger in triggers if trigger not in combined]
        if missing:
            errors.append(f"{skill}: missing routing triggers: {', '.join(missing)}")

        if "allow_implicit_invocation: true" not in yaml_text:
            errors.append(f"{skill}: implicit invocation must be enabled")

        if f"${skill}" not in yaml_text:
            errors.append(f"{skill}: default prompt must mention ${skill}")

        if f"`{skill}`" not in routing_text:
            errors.append(f"{skill}: not documented in docs/skill-routing.md")

    if errors:
        for error in errors:
            print(f"error: {error}", file=sys.stderr)
        return 1

    print(f"validated plain-English routing for {len(REQUIRED_TRIGGERS)} skills")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
