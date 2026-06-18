#!/usr/bin/env python3
"""Normalize connector output into private source evidence with cursor state."""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from harness_common import resolve_root
from source_registry import errors_for_source, find_source, is_capture_eligible, load_registry
from source_sync_common import (
    allowed_to_store_evidence,
    evidence_path,
    evidence_record,
    iter_jsonl,
    load_state,
    save_state,
    source_state,
    utc_now,
)


DEFAULT_ROOT = (
    os.environ.get("BRAIN_ROOT")
    or os.environ.get("COMPANY_BRAIN_ROOT")
    or os.environ.get("COMPANY_OS_ROOT")
    or os.getcwd()
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Pull normalized source records into private evidence staging.")
    parser.add_argument("--root", default=DEFAULT_ROOT, help="Company Brain root")
    parser.add_argument("--source-id", required=True, help="approved source instance id")
    parser.add_argument("--input-jsonl", type=Path, required=True, help="normalized connector output JSONL")
    parser.add_argument("--cursor", default=None, help="connector cursor/page token after this pull")
    parser.add_argument("--allow-restricted-evidence", action="store_true")
    parser.add_argument("--write", action="store_true", help="persist evidence and sync state")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    root = resolve_root(args.root)
    if not root.is_dir():
        print(json.dumps({"error": f"brain root not found: {root}"}), file=sys.stderr)
        return 2
    if not args.input_jsonl.is_file():
        print(json.dumps({"error": f"input JSONL not found: {args.input_jsonl}"}), file=sys.stderr)
        return 2

    report = load_registry(root)
    source = find_source(report, source_id=args.source_id)
    if source is None:
        print(json.dumps({"error": f"source not found or ambiguous: {args.source_id}"}), file=sys.stderr)
        return 1
    source_errors = errors_for_source(report, source.id)
    if source_errors:
        print(json.dumps({"error": "source registry errors", "source_id": source.id, "errors": source_errors}), file=sys.stderr)
        return 1
    if not is_capture_eligible(source):
        print(json.dumps({"error": f"source is not capture-eligible: {source.id}"}), file=sys.stderr)
        return 1

    state = load_state(root)
    current = source_state(state, source.id)
    items = current.setdefault("items", {})
    pulled_at = utc_now()
    accepted = []
    skipped = []
    unchanged = 0

    try:
        records = list(iter_jsonl(args.input_jsonl))
    except ValueError as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 1

    for raw in records:
        external_id = str(raw.get("external_id") or raw.get("id") or "").strip()
        if not external_id:
            skipped.append({"external_id": None, "reason": "missing external_id"})
            continue
        allowed, reason = allowed_to_store_evidence(raw, allow_restricted=args.allow_restricted_evidence)
        if not allowed:
            skipped.append({"external_id": external_id, "reason": reason})
            continue
        normalized = evidence_record(source, raw, pulled_at=pulled_at)
        previous = items.get(external_id, {})
        if previous.get("hash") == normalized["hash"]:
            unchanged += 1
            continue
        accepted.append(normalized)
        if args.write:
            items[external_id] = {
                "hash": normalized["hash"],
                "last_seen_at": pulled_at,
                "visibility": normalized["visibility"],
            }

    target = evidence_path(root, source.id)
    if args.write and accepted:
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("a", encoding="utf-8") as handle:
            for record in accepted:
                handle.write(json.dumps(record, sort_keys=True) + "\n")
    if args.write:
        current["last_successful_pull"] = pulled_at
        if args.cursor:
            current["cursor"] = args.cursor
        elif accepted and accepted[-1].get("cursor"):
            current["cursor"] = accepted[-1]["cursor"]
        current["last_pull_counts"] = {
            "accepted": len(accepted),
            "skipped": len(skipped),
            "unchanged": unchanged,
        }
        save_state(root, state)

    result = {
        "action": "pulled" if args.write else "would-pull",
        "source_id": source.id,
        "evidence_path": str(target.relative_to(root)),
        "accepted": len(accepted),
        "skipped": skipped,
        "unchanged": unchanged,
        "note": None if args.write else "preview only; rerun with --write to persist",
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
