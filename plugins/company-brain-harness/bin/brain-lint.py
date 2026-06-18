#!/usr/bin/env python3
"""Read-only maintenance lint for a filesystem-backed company brain."""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path

from harness_common import conventions_dir, resolve_root, restricted_prefixes


DEFAULT_ROOT = (
    os.environ.get("BRAIN_ROOT")
    or os.environ.get("COMPANY_BRAIN_ROOT")
    or os.environ.get("COMPANY_OS_ROOT")
    or os.getcwd()
)
FM_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
MD_LINK_RE = re.compile(r"\[[^\]]+\]\((?!https?:|mailto:|#)([^)]+)\)")
WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)")
META_FILES = {
    "CLAUDE.md",
    "README.md",
    "00_INDEX.md",
    "index.md",
    "START_HERE.md",
    "OWNER_GUIDE.md",
    "OPERATOR_GUIDE.md",
    "TEAM_MEMBER_GUIDE.md",
    "INVITE_TEAM.md",
    "TODAY.md",
    "NEXT_ACTIONS.md",
}


def _excluded_tops(root: Path) -> set[str]:
    tops = set(restricted_prefixes(root))
    try:
        rel = conventions_dir(root).relative_to(root)
        if rel.parts:
            tops.add(rel.parts[0])
    except ValueError:
        pass
    return tops


def _is_excluded(rel: Path, root: Path) -> bool:
    return bool(rel.parts) and rel.parts[0] in _excluded_tops(root)


def walk_md(root: Path):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]
        d = Path(dirpath)
        rel_dir = d.relative_to(root)
        if _is_excluded(rel_dir, root):
            dirnames[:] = []
            continue
        for filename in filenames:
            if filename.startswith(".") or not filename.endswith(".md"):
                continue
            path = d / filename
            yield path, rel_dir / filename


def parse_frontmatter(text: str) -> dict[str, str]:
    match = FM_RE.match(text)
    if not match:
        return {}
    data: dict[str, str] = {}
    for raw in match.group(1).splitlines():
        if ":" not in raw:
            continue
        key, value = raw.split(":", 1)
        data[key.strip()] = value.strip().strip('"')
    return data


def parse_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return datetime.strptime(value[:10], "%Y-%m-%d").date()
    except ValueError:
        return None


def is_content_note(rel: Path) -> bool:
    return rel.name not in META_FILES and not rel.parts[-2:-1] == ("90_Staging",)


def lint(root: Path, *, stale_days: int) -> dict:
    today = date.today()
    missing_frontmatter: list[str] = []
    missing_provenance: list[str] = []
    stale_notes: list[str] = []
    undated_notes: list[str] = []
    dead_links: list[str] = []
    duplicate_names: dict[str, list[str]] = defaultdict(list)
    possible_contradictions: list[str] = []

    md_files = list(walk_md(root))
    existing_rel = {rel.as_posix() for _, rel in md_files}
    by_stem: dict[str, list[str]] = defaultdict(list)

    for path, rel in md_files:
        rel_s = rel.as_posix()
        by_stem[rel.stem.lower()].append(rel_s)
        text = path.read_text(encoding="utf-8", errors="ignore")
        frontmatter = parse_frontmatter(text)

        if is_content_note(rel):
            if not frontmatter:
                missing_frontmatter.append(rel_s)
            verified = parse_date(frontmatter.get("last_verified"))
            if verified is None:
                undated_notes.append(rel_s)
            elif (today - verified).days > stale_days:
                stale_notes.append(rel_s)
            if "<!-- src:" not in text:
                missing_provenance.append(rel_s)

        if is_content_note(rel) and (
            "contradict" in text.lower() or "superseded" in text.lower() or "stale" in text.lower()
        ):
            possible_contradictions.append(rel_s)

        for target in MD_LINK_RE.findall(text):
            target = target.split("#")[0].strip()
            if not target:
                continue
            resolved = (path.parent / target).resolve()
            try:
                if root.resolve() not in resolved.parents and root.resolve() != resolved:
                    dead_links.append(f"{rel_s} -> {target} (outside root)")
                elif not resolved.exists():
                    dead_links.append(f"{rel_s} -> {target}")
            except RuntimeError:
                dead_links.append(f"{rel_s} -> {target} (bad path)")

        for target in WIKILINK_RE.findall(text):
            normalized = target.strip().replace(" ", "-").lower()
            if normalized and normalized not in by_stem:
                # Second pass below avoids false positives before all stems are known.
                pass

    duplicate_names = {
        stem: paths for stem, paths in sorted(by_stem.items()) if len(paths) > 1 and stem not in {"readme", "claude", "00_index", "index"}
    }

    wiki_stems = set(by_stem)
    for path, rel in md_files:
        text = path.read_text(encoding="utf-8", errors="ignore")
        for target in WIKILINK_RE.findall(text):
            stem = Path(target.strip()).stem.lower().replace(" ", "-")
            if stem and stem not in wiki_stems:
                dead_links.append(f"{rel.as_posix()} -> [[{target}]]")

    issues = {
        "missing_frontmatter": sorted(missing_frontmatter),
        "missing_provenance": sorted(missing_provenance),
        "stale_notes": sorted(stale_notes),
        "undated_notes": sorted(undated_notes),
        "dead_links": sorted(set(dead_links)),
        "duplicate_names": duplicate_names,
        "possible_contradictions": sorted(set(possible_contradictions)),
    }
    issue_count = (
        len(missing_frontmatter)
        + len(missing_provenance)
        + len(stale_notes)
        + len(undated_notes)
        + len(set(dead_links))
        + sum(len(paths) for paths in duplicate_names.values())
        + len(set(possible_contradictions))
    )
    return {
        "root": str(root),
        "generated": today.isoformat(),
        "ok": issue_count == 0,
        "stale_days": stale_days,
        "stats": {
            "markdown_files": len(md_files),
            "issue_count": issue_count,
        },
        "issues": issues,
    }


def render(result: dict) -> str:
    lines = ["", "BRAIN LINT [" + ("ok" if result["ok"] else "needs attention") + "]"]
    lines.append(f"root: {result['root']}")
    lines.append(f"markdown files: {result['stats']['markdown_files']}")
    lines.append(f"issues: {result['stats']['issue_count']}")
    for key, value in result["issues"].items():
        count = len(value) if not isinstance(value, dict) else sum(len(v) for v in value.values())
        if not count:
            continue
        lines.append("")
        lines.append(f"{key.replace('_', ' ').title()} ({count})")
        if isinstance(value, dict):
            for stem, paths in list(value.items())[:10]:
                lines.append(f"- {stem}: " + ", ".join(paths))
        else:
            for item in value[:20]:
                lines.append(f"- {item}")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Read-only lint for company brain freshness and integrity.")
    parser.add_argument("--root", default=DEFAULT_ROOT, help="brain root")
    parser.add_argument("--stale-days", type=int, default=30)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    root = resolve_root(args.root)
    if not root.is_dir():
        print(json.dumps({"error": f"brain root not found: {root}"}), file=sys.stderr)
        return 2

    result = lint(root, stale_days=args.stale_days)
    print(json.dumps(result, indent=2, sort_keys=True) if args.json else render(result))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
