#!/usr/bin/env python3
"""stage-brain-note - create a proposed note for later approval.

Generic staging for a filesystem-backed company brain. It does not write to the
final destination. By default it previews the proposed staging write. Use
--write to persist the proposal under the staging area, including the intended
target path and provenance metadata.

Default staging directory:
  <brain root>/00_README_Drive_Conventions/90_Staging/proposed

Usage:
    echo '# Note\n\nBody' | bin/stage-brain-note.py \
      --target 02_Strategy_and_Vision/02_Category_and_Positioning/category.md \
      --tag strategy --tag positioning \
      --source-type interview --source-ref owner-interview --author brain-operator

Exit codes:
    0 = valid preview / staged
    1 = validation failed
    2 = bad local configuration / missing root
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

from harness_common import resolve_root, restricted_prefixes, staging_dir


DEFAULT_ROOT = (
    os.environ.get("BRAIN_ROOT")
    or os.environ.get("COMPANY_BRAIN_ROOT")
    or os.environ.get("COMPANY_OS_ROOT")
    or os.getcwd()
)


class StageError(RuntimeError):
    pass


def slugify(text: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s or "untitled"


def parse_tags(values: list[str]) -> list[str]:
    tags: list[str] = []
    for raw in values:
        tags.extend(t.strip() for t in raw.split(",") if t.strip())
    out: list[str] = []
    seen: set[str] = set()
    for tag in tags:
        key = tag.lower()
        if key not in seen:
            seen.add(key)
            out.append(tag)
    return out


def safe_target(target: str, *, restricted: set[str]) -> Path:
    rel = Path(target)
    if rel.is_absolute():
        raise StageError("--target must be relative to the brain root")
    if any(part in {"", ".", ".."} for part in rel.parts):
        raise StageError("--target must not contain empty, '.', or '..' path parts")
    if len(rel.parts) < 2:
        raise StageError("--target must live under a folder; root-level writes are refused")
    if rel.suffix.lower() != ".md":
        raise StageError("--target must end in .md")
    if rel.parts[0] in restricted:
        raise StageError(f"target is under restricted prefix {rel.parts[0]!r}")
    return rel


def yaml_scalar(value: str) -> str:
    if value == "":
        return '""'
    needs_quote = (
        value.strip() != value
        or any(ch in value for ch in [":", "#", "{", "}", "[", "]", ","])
        or value.lower() in {"true", "false", "null", "yes", "no"}
    )
    if not needs_quote:
        return value
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def dump_frontmatter(metadata: dict[str, Any], body: str) -> str:
    lines = ["---"]
    for key, value in metadata.items():
        if isinstance(value, list):
            lines.append(f"{key}:")
            for item in value:
                lines.append(f"  - {yaml_scalar(str(item))}")
        else:
            lines.append(f"{key}: {yaml_scalar(str(value))}")
    lines.extend(["---", "", body.strip(), ""])
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Stage a proposed company-brain note.")
    parser.add_argument("--root", default=DEFAULT_ROOT, help="knowledge root / brain root")
    parser.add_argument("--staging-dir", default=None, help="staging dir relative to root; defaults from brain config")
    parser.add_argument("--source", type=Path, default=None, help="source markdown/text; defaults to stdin")
    parser.add_argument("--target", required=True, help="intended destination path relative to root")
    parser.add_argument("--title", default=None, help="human title; default from first heading or target")
    parser.add_argument("--tag", action="append", default=[], help="tag to add; can repeat or comma-separate")
    parser.add_argument("--source-type", required=True, help="provenance type, e.g. interview, fireflies, doc")
    parser.add_argument("--source-ref", required=True, help="provenance id/link/reference")
    parser.add_argument("--author", required=True, help="human/source author for attribution")
    parser.add_argument("--owner", default=None, help="business owner")
    parser.add_argument("--sensitivity", default="internal", help="internal, public, confidential, restricted, etc.")
    parser.add_argument("--staged-by", default="company-brain-harness")
    parser.add_argument("--id", default=None, help="explicit staged id; default generated from target")
    parser.add_argument("--overwrite", action="store_true", help="replace an existing staged proposal")
    parser.add_argument("--write", action="store_true", help="actually stage; default is preview-only")
    args = parser.parse_args(argv)

    root = resolve_root(args.root)
    if not root.is_dir():
        print(json.dumps({"error": f"brain root not found: {root}"}), file=sys.stderr)
        return 2

    try:
        target = safe_target(args.target, restricted=set(restricted_prefixes(root)))
        if args.source:
            if not args.source.is_file():
                raise StageError(f"source not found: {args.source}")
            body = args.source.read_text(encoding="utf-8").strip()
        else:
            body = sys.stdin.read().strip()
        if not body:
            raise StageError("source body is empty")

        tags = parse_tags(args.tag)
        if len(tags) < 2:
            raise StageError("staged notes need at least two tags")

        title = args.title
        if not title:
            first_heading = next(
                (line.lstrip("# ").strip() for line in body.splitlines() if line.startswith("#")),
                None,
            )
            title = first_heading or target.stem.replace("-", " ").replace("_", " ").title()

        today = date.today().isoformat()
        staged_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        stage_id = args.id or f"{today}-{slugify(target.with_suffix('').as_posix())}"
        stage_path = staging_dir(root, args.staging_dir) / "proposed" / f"{stage_id}.md"
        if stage_path.exists() and not args.overwrite:
            raise StageError(f"staged proposal already exists: {stage_path.relative_to(root)}")

        metadata: dict[str, Any] = {
            "status": "proposed",
            "tags": tags,
            "last_verified": today,
            "title": title,
            "target_path": target.as_posix(),
            "source_type": args.source_type,
            "source_ref": args.source_ref,
            "author": args.author,
            "sensitivity": args.sensitivity,
            "staged_by": args.staged_by,
            "staged_at": staged_at,
        }
        if args.owner:
            metadata["owner"] = args.owner

        if "<!-- src:" not in body:
            body = f"<!-- src: {args.source_type}/{args.source_ref} @ {today} -->\n\n{body}"

        rendered = dump_frontmatter(metadata, body)
        if args.write:
            stage_path.parent.mkdir(parents=True, exist_ok=True)
            stage_path.write_text(rendered, encoding="utf-8")

        print(json.dumps({
            "action": "staged" if args.write else "would-stage",
            "id": stage_id,
            "path": str(stage_path.relative_to(root)),
            "target": target.as_posix(),
            "sensitivity": args.sensitivity,
            "bytes": len(rendered.encode("utf-8")),
            "note": None if args.write else "preview only; rerun with --write to persist",
        }, indent=2, sort_keys=True))
        return 0
    except StageError as e:
        print(json.dumps({"error": str(e)}, indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
