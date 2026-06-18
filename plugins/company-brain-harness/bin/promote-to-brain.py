#!/usr/bin/env python3
"""promote-to-brain - generic approved-note promotion into a knowledge root.

This script is deliberately backend-neutral. The destination can be a mounted
Google Drive, a git repo, a shared volume, or any filesystem-backed knowledge
root. Google Drive is only one possible storage backend.

Default behavior is preview-only. Use --write for side effects.

Usage:
    bin/promote-to-brain.py \
      --source /tmp/proposed-note.md \
      --target 02_Strategy_and_Vision/02_Category_and_Positioning/category.md \
      --tag strategy --tag positioning \
      --source-type interview --source-ref owner-interview-2026-06-17 \
      --author brain-operator

    bin/promote-to-brain.py ... --write

Exit codes:
    0 = success / valid preview
    1 = validation failed or refused write
    2 = bad local configuration / missing source/root
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

from harness_common import resolve_root, restricted_prefixes


DEFAULT_ROOT = (
    os.environ.get("BRAIN_ROOT")
    or os.environ.get("COMPANY_BRAIN_ROOT")
    or os.environ.get("COMPANY_OS_ROOT")
    or os.getcwd()
)
SRC_COMMENT_PREFIX = "<!-- src:"


class PromoteError(RuntimeError):
    """Validation error surfaced to the CLI."""


@dataclass
class Note:
    metadata: dict[str, Any]
    content: str


def parse_note(text: str) -> Note:
    """Parse the small YAML subset used by brain notes.

    Supports `key: value` scalars and simple lists:

        tags:
          - strategy
          - positioning

    This keeps the promotion CLI portable even when the caller's system Python
    does not have python-frontmatter installed. It is intentionally small; the
    harness should emit simple frontmatter.
    """
    if not text.startswith("---\n"):
        return Note(metadata={}, content=text.strip())

    end = text.find("\n---", 4)
    if end == -1:
        return Note(metadata={}, content=text.strip())

    raw_fm = text[4:end].strip("\n")
    body_start = end + len("\n---")
    if text[body_start:body_start + 1] == "\n":
        body_start += 1
    metadata: dict[str, Any] = {}
    current_key: str | None = None
    for raw_line in raw_fm.splitlines():
        line = raw_line.rstrip()
        if not line.strip():
            continue
        if line.startswith("  - ") and current_key:
            metadata.setdefault(current_key, []).append(_unquote(line[4:].strip()))
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            continue
        if value == "":
            metadata[key] = []
            current_key = key
        else:
            metadata[key] = _parse_scalar(value)
            current_key = key
    return Note(metadata=metadata, content=text[body_start:].strip())


def _parse_scalar(value: str) -> Any:
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [_unquote(part.strip()) for part in inner.split(",") if part.strip()]
    return _unquote(value)


def _unquote(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def dump_note(note: Note) -> str:
    lines = ["---"]
    for key, value in note.metadata.items():
        if isinstance(value, (list, tuple)):
            lines.append(f"{key}:")
            for item in value:
                lines.append(f"  - {_yaml_scalar(str(item))}")
        else:
            lines.append(f"{key}: {_yaml_scalar(str(value))}")
    lines.append("---")
    lines.append("")
    lines.append(note.content.strip())
    return "\n".join(lines).rstrip() + "\n"


def _yaml_scalar(value: str) -> str:
    if value == "":
        return '""'
    needs_quote = (
        value.strip() != value
        or any(ch in value for ch in [":", "#", "{", "}", "[", "]", ","])
        or value.lower() in {"true", "false", "null", "yes", "no"}
    )
    if not needs_quote:
        return value
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def parse_tags(values: list[str], existing: Any) -> list[str]:
    tags: list[str] = []
    if isinstance(existing, str):
        tags.extend(t.strip() for t in existing.split(",") if t.strip())
    elif isinstance(existing, (list, tuple)):
        tags.extend(str(t).strip() for t in existing if str(t).strip())
    for raw in values:
        tags.extend(t.strip() for t in raw.split(",") if t.strip())

    seen: set[str] = set()
    out: list[str] = []
    for tag in tags:
        key = tag.lower()
        if key not in seen:
            seen.add(key)
            out.append(tag)
    return out


def safe_target(root: Path, target: str, *, allow_root_target: bool) -> Path:
    rel = Path(target)
    if rel.is_absolute():
        raise PromoteError("--target must be relative to the brain root")
    if any(part in {"", ".", ".."} for part in rel.parts):
        raise PromoteError("--target must not contain empty, '.', or '..' path parts")
    if len(rel.parts) < 2 and not allow_root_target:
        raise PromoteError("--target must live under a folder; root-level writes are refused")
    if rel.suffix.lower() != ".md":
        raise PromoteError("--target must be a markdown file ending in .md")

    resolved_root = root.resolve()
    resolved_target = (root / rel).resolve()
    if resolved_root != resolved_target and resolved_root not in resolved_target.parents:
        raise PromoteError("--target resolves outside the brain root")
    return resolved_target


def validate_restricted(target_rel: Path, prefixes: list[str], *, allow_restricted: bool) -> None:
    if allow_restricted:
        return
    first = target_rel.parts[0] if target_rel.parts else ""
    if first in set(prefixes):
        raise PromoteError(
            f"target is under restricted prefix {first!r}; use a restricted workflow instead"
        )


def load_source(path: Path | None) -> Note:
    if path is None:
        text = sys.stdin.read()
        if not text.strip():
            raise PromoteError("stdin source is empty")
        return parse_note(text)
    if not path.exists():
        raise PromoteError(f"source not found: {path}")
    if not path.is_file():
        raise PromoteError(f"source is not a file: {path}")
    return parse_note(path.read_text(encoding="utf-8"))


def ensure_source_metadata(note: Note, args: argparse.Namespace) -> tuple[str, str]:
    source_type = args.source_type or note.metadata.get("source_type")
    source_ref = args.source_ref or note.metadata.get("source_ref")
    if not source_type or not source_ref:
        if args.allow_missing_provenance:
            return str(source_type or "manual"), str(source_ref or "unverified")
        raise PromoteError(
            "source provenance is required: pass --source-type and --source-ref "
            "or use --allow-missing-provenance for an explicitly unverified note"
        )
    return str(source_type), str(source_ref)


def build_note(note: Note, args: argparse.Namespace) -> tuple[Note, dict]:
    metadata = dict(note.metadata)
    for staging_key in ("target_path", "staged_by", "staged_at"):
        metadata.pop(staging_key, None)
    today = date.today().isoformat()
    source_type, source_ref = ensure_source_metadata(note, args)

    metadata["status"] = args.status or metadata.get("status") or "active"
    metadata["tags"] = parse_tags(args.tag, metadata.get("tags"))
    metadata["last_verified"] = args.last_verified or metadata.get("last_verified") or today
    metadata["source_type"] = source_type
    metadata["source_ref"] = source_ref

    if args.owner:
        metadata["owner"] = args.owner
    elif "owner" not in metadata and args.require_owner:
        raise PromoteError("--owner is required unless source frontmatter already has owner")

    author = args.author or metadata.get("author") or metadata.get("captured_by")
    if author:
        metadata["author"] = str(author)
    elif args.require_author:
        raise PromoteError("--author is required unless source frontmatter already has author/captured_by")

    metadata["promoted_by"] = args.promoted_by or metadata.get("promoted_by") or "company-brain-harness"
    metadata["promoted_at"] = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    metadata["sensitivity"] = args.sensitivity or metadata.get("sensitivity") or "internal"

    tags = metadata.get("tags") or []
    if not isinstance(tags, list) or len(tags) < 2:
        raise PromoteError("promoted notes need at least two tags")

    body = note.content.strip()
    if not body:
        raise PromoteError("source note body is empty")

    provenance = f"<!-- src: {source_type}/{source_ref} @ {today} -->"
    if not args.no_provenance_comment and SRC_COMMENT_PREFIX not in body:
        body = provenance + "\n\n" + body

    out = Note(metadata=metadata, content=body)
    summary = {
        "source_type": source_type,
        "source_ref": source_ref,
        "tags": metadata["tags"],
        "sensitivity": metadata["sensitivity"],
        "status": metadata["status"],
        "has_provenance_comment": SRC_COMMENT_PREFIX in body,
    }
    return out, summary


def write_or_preview(
    note: Note,
    *,
    root: Path,
    target: Path,
    write: bool,
    overwrite: bool,
    mkdir: bool,
) -> dict:
    rel = target.relative_to(root)
    if target.exists() and not overwrite:
        raise PromoteError(f"target already exists: {rel}; use --overwrite to replace it")
    if not target.parent.exists():
        if not mkdir:
            raise PromoteError(f"target parent does not exist: {target.parent.relative_to(root)}")
        if write:
            target.parent.mkdir(parents=True, exist_ok=True)

    text = dump_note(note)
    if write:
        target.write_text(text, encoding="utf-8")
        action = "wrote"
    else:
        action = "would-write"
    return {
        "action": action,
        "root": str(root),
        "target": str(rel),
        "bytes": len(text.encode("utf-8")),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Promote an approved markdown note into a filesystem-backed knowledge root."
    )
    parser.add_argument("--root", default=DEFAULT_ROOT, help="knowledge root / brain root")
    parser.add_argument("--source", type=Path, default=None, help="source markdown note; defaults to stdin")
    parser.add_argument("--target", required=True, help="relative destination markdown path")
    parser.add_argument("--tag", action="append", default=[], help="tag to add; can repeat or comma-separate")
    parser.add_argument("--status", default=None, help="frontmatter status (default active)")
    parser.add_argument("--last-verified", default=None, help="YYYY-MM-DD; default today")
    parser.add_argument("--source-type", default=None, help="provenance type, e.g. interview, fireflies, doc")
    parser.add_argument("--source-ref", default=None, help="provenance id/link/reference")
    parser.add_argument("--owner", default=None, help="business owner for the promoted note")
    parser.add_argument("--author", default=None, help="human/source author for attribution")
    parser.add_argument("--promoted-by", default=None, help="promotion actor")
    parser.add_argument("--sensitivity", default=None, help="internal, public, confidential, restricted, etc.")
    parser.add_argument("--restricted-prefix", action="append", default=[])
    parser.add_argument("--allow-restricted", action="store_true", help="allow restricted-prefix target")
    parser.add_argument("--allow-root-target", action="store_true", help="allow root-level target")
    parser.add_argument("--allow-missing-provenance", action="store_true")
    parser.add_argument("--no-provenance-comment", action="store_true")
    parser.add_argument("--require-owner", action="store_true")
    parser.add_argument("--require-author", action="store_true", default=True)
    parser.add_argument("--no-require-author", dest="require_author", action="store_false")
    parser.add_argument("--mkdir", action="store_true", help="create target parent directories")
    parser.add_argument("--overwrite", action="store_true", help="replace existing target")
    parser.add_argument("--write", action="store_true", help="actually write; default is preview-only")
    args = parser.parse_args(argv)

    root = resolve_root(args.root)
    if not root.is_dir():
        print(json.dumps({"error": f"brain root not found: {root}"}), file=sys.stderr)
        return 2

    try:
        target = safe_target(root, args.target, allow_root_target=args.allow_root_target)
        validate_restricted(
            target.relative_to(root),
            restricted_prefixes(root, args.restricted_prefix),
            allow_restricted=args.allow_restricted,
        )
        source = load_source(args.source)
        note, summary = build_note(source, args)
        result = write_or_preview(
            note,
            root=root.resolve(),
            target=target,
            write=args.write,
            overwrite=args.overwrite,
            mkdir=args.mkdir,
        )
        result["metadata"] = summary
        if not args.write:
            result["note"] = "preview only; rerun with --write to persist"
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    except PromoteError as e:
        print(json.dumps({"error": str(e)}, indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
