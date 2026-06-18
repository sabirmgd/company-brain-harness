#!/usr/bin/env python3
"""approve-staged-note - approve/reject/revise staged brain notes.

Approved notes are promoted via promote-to-brain.py, so the generic write path
remains centralized. This script writes an append-only JSONL approval ledger and
moves staged proposals to approved/rejected/revise folders.

Default staging directory:
  <brain root>/00_Company_Brain_Conventions/90_Staging

Usage:
    bin/approve-staged-note.py --id 2026-06-17-example --decision approve --reviewer brain-owner --write
    bin/approve-staged-note.py --id 2026-06-17-example --decision reject --reviewer brain-owner --note "personal"

Exit codes:
    0 = decision recorded
    1 = validation failed or refused write
    2 = bad local configuration / missing root
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from harness_common import resolve_root, staging_dir


DEFAULT_ROOT = (
    os.environ.get("BRAIN_ROOT")
    or os.environ.get("COMPANY_BRAIN_ROOT")
    or os.environ.get("COMPANY_OS_ROOT")
    or os.getcwd()
)


class ApprovalError(RuntimeError):
    pass


def parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---\n"):
        return {}, text.strip()
    end = text.find("\n---", 4)
    if end == -1:
        return {}, text.strip()
    raw = text[4:end].strip()
    body_start = end + len("\n---")
    if text[body_start:body_start + 1] == "\n":
        body_start += 1
    data: dict[str, Any] = {}
    current: str | None = None
    for line in raw.splitlines():
        if line.startswith("  - ") and current:
            data.setdefault(current, []).append(line[4:].strip().strip('"'))
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if value == "":
            data[key] = []
            current = key
        else:
            data[key] = value.strip('"')
            current = key
    return data, text[body_start:].strip()


def find_stage(staging_root: Path, stage_id: str) -> Path:
    candidate = staging_root / "proposed" / f"{stage_id}.md"
    if candidate.exists():
        return candidate
    matches = sorted((staging_root / "proposed").glob(f"{stage_id}*.md"))
    if len(matches) == 1:
        return matches[0]
    if not matches:
        raise ApprovalError(f"no staged proposal found for id {stage_id!r}")
    raise ApprovalError(f"multiple staged proposals match {stage_id!r}; use full id")


def append_ledger(staging_root: Path, event: dict[str, Any], *, write: bool) -> Path:
    ledger = staging_root / "approval-ledger.jsonl"
    if write:
        ledger.parent.mkdir(parents=True, exist_ok=True)
        with ledger.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(event, sort_keys=True) + "\n")
    return ledger


def move_stage(path: Path, dest_dir: Path, *, write: bool, overwrite: bool) -> Path:
    dest = dest_dir / path.name
    if dest.exists() and not overwrite:
        raise ApprovalError(f"destination already exists: {dest}")
    if write:
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(path), str(dest))
    return dest


def promote(root: Path, stage: Path, metadata: dict[str, Any], args: argparse.Namespace) -> dict:
    script = Path(__file__).resolve().parent / "promote-to-brain.py"
    target = metadata.get("target_path")
    if not target:
        raise ApprovalError("staged note is missing target_path frontmatter")

    cmd = [
        sys.executable,
        str(script),
        "--root", str(root),
        "--source", str(stage),
        "--target", str(target),
        "--status", "active",
        "--overwrite" if args.overwrite_target else "--no-require-author",
    ]
    # The conditional above needs a stable list shape; remove the sentinel when
    # not overwriting and always pass no-require-author only if stage lacks author.
    if not args.overwrite_target:
        cmd.pop()
    if args.overwrite_target:
        pass
    if not metadata.get("author"):
        cmd.append("--no-require-author")
    if args.write:
        cmd.append("--write")

    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise ApprovalError(result.stderr.strip() or result.stdout.strip() or "promotion failed")
    return json.loads(result.stdout)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Approve, reject, or revise a staged brain note.")
    parser.add_argument("--root", default=DEFAULT_ROOT, help="knowledge root / brain root")
    parser.add_argument("--staging-dir", default=None, help="staging dir relative to root; defaults from brain config")
    parser.add_argument("--id", required=True, help="staged proposal id or unique prefix")
    parser.add_argument("--decision", required=True, choices=["approve", "reject", "revise"])
    parser.add_argument("--reviewer", required=True)
    parser.add_argument("--note", default=None, help="review note/reason")
    parser.add_argument("--write", action="store_true", help="actually promote/move/write ledger")
    parser.add_argument("--overwrite-target", action="store_true", help="allow replacing an existing promoted target")
    parser.add_argument("--overwrite-stage", action="store_true", help="allow replacing approved/rejected/revise copy")
    args = parser.parse_args(argv)

    root = resolve_root(args.root)
    if not root.is_dir():
        print(json.dumps({"error": f"brain root not found: {root}"}), file=sys.stderr)
        return 2

    try:
        staging_root = staging_dir(root, args.staging_dir)
        stage = find_stage(staging_root, args.id)
        metadata, _body = parse_frontmatter(stage.read_text(encoding="utf-8"))
        event = {
            "event": "staged_note_reviewed",
            "decision": args.decision,
            "id": stage.stem,
            "stage_path": str(stage.relative_to(root)),
            "target_path": metadata.get("target_path"),
            "reviewer": args.reviewer,
            "reviewed_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            "note": args.note,
            "write": bool(args.write),
        }

        promotion_result = None
        if args.decision == "approve":
            promotion_result = promote(root, stage, metadata, args)
            event["promotion"] = promotion_result
            dest = move_stage(stage, staging_root / "approved", write=args.write, overwrite=args.overwrite_stage)
        elif args.decision == "reject":
            dest = move_stage(stage, staging_root / "rejected", write=args.write, overwrite=args.overwrite_stage)
        else:
            dest = move_stage(stage, staging_root / "revise", write=args.write, overwrite=args.overwrite_stage)
        event["decision_path"] = str(dest.relative_to(root))
        ledger = append_ledger(staging_root, event, write=args.write)

        print(json.dumps({
            "action": "recorded" if args.write else "would-record",
            "decision": args.decision,
            "id": stage.stem,
            "ledger": str(ledger.relative_to(root)),
            "decision_path": str(dest.relative_to(root)),
            "promotion": promotion_result,
            "note": "preview only; rerun with --write to persist" if not args.write else None,
        }, indent=2, sort_keys=True))
        return 0
    except ApprovalError as e:
        print(json.dumps({"error": str(e)}, indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
