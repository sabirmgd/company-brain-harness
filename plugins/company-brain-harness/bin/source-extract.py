#!/usr/bin/env python3
"""Extract approved evidence records into staged company-brain proposals."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

from harness_common import resolve_root
from source_registry import errors_for_source, find_source, is_capture_eligible, load_registry
from source_sync_common import (
    allowed_artifacts,
    blocked_artifacts,
    evidence_path,
    iter_jsonl,
    load_state,
    normalize_tags,
    slugify,
    source_state,
    save_state,
    utc_now,
    visibility,
    PRIVATE_VISIBILITIES,
    RESTRICTED_VISIBILITIES,
)


DEFAULT_ROOT = (
    os.environ.get("BRAIN_ROOT")
    or os.environ.get("COMPANY_BRAIN_ROOT")
    or os.environ.get("COMPANY_OS_ROOT")
    or os.getcwd()
)


def default_target(source, record: dict) -> str:
    target = record.get("target_path")
    if target:
        return str(target)
    destination = str(source.routing.get("default_destination") or "").strip("/")
    if not destination or destination in {".", "null", "None"}:
        raise ValueError(f"{record.get('external_id')}: missing target_path and source has no default destination")
    return f"{destination}/{slugify(str(record.get('title') or record.get('external_id')))}.md"


def note_body(record: dict) -> str:
    title = str(record.get("title") or "Source Update").strip()
    summary = str(record.get("summary") or "").strip()
    url = record.get("url")
    occurred_at = record.get("occurred_at")
    parts = [f"# {title}", ""]
    if summary:
        parts.extend([summary, ""])
    if occurred_at:
        parts.extend([f"Occurred at: {occurred_at}", ""])
    if url:
        parts.extend([f"Source link: {url}", ""])
    return "\n".join(parts).strip() + "\n"


def latest_records_by_external_id(records: list[dict]) -> list[dict]:
    latest: dict[str, dict] = {}
    order: list[str] = []
    missing_id_records: list[dict] = []
    for record in records:
        external_id = str(record.get("external_id") or "").strip()
        if not external_id:
            missing_id_records.append(record)
            continue
        if external_id not in latest:
            order.append(external_id)
        latest[external_id] = record
    return missing_id_records + [latest[external_id] for external_id in order]


def stage_record(root: Path, source, record: dict, *, write: bool, overwrite: bool) -> dict:
    stage_script = Path(__file__).resolve().parent / "stage-brain-note.py"
    tags = normalize_tags(record.get("tags"), [str(source.connector or "source"), "source-sync"])
    target = default_target(source, record)
    stage_id = f"{slugify(source.id)}-{slugify(str(record.get('external_id')))}"
    cmd = [
        sys.executable,
        str(stage_script),
        "--root", str(root),
        "--target", target,
        "--title", str(record.get("title") or record.get("external_id")),
        "--source-type", str(source.connector or "source"),
        "--source-ref", str(record.get("source_ref") or f"{source.id}/{record.get('external_id')}"),
        "--author", str(record.get("author") or source.display_name or source.id),
        "--owner", str(source.review_owner or source.owner or "brain-owner"),
        "--sensitivity", str(record.get("sensitivity") or "internal"),
        "--staged-by", "source-extract.py",
        "--id", stage_id,
    ]
    for tag in tags:
        cmd.extend(["--tag", tag])
    if overwrite:
        cmd.append("--overwrite")
    if write:
        cmd.append("--write")
    result = subprocess.run(cmd, input=note_body(record), capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "stage-brain-note failed")
    return json.loads(result.stdout)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Extract source evidence into staged company-brain notes.")
    parser.add_argument("--root", default=DEFAULT_ROOT, help="Company Brain root")
    parser.add_argument("--source-id", required=True, help="approved source instance id")
    parser.add_argument("--evidence", type=Path, default=None, help="evidence JSONL; defaults to source evidence path")
    parser.add_argument("--external-id", default=None, help="only extract one external id")
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--allow-restricted", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--write", action="store_true", help="persist staged proposals and sync state")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    root = resolve_root(args.root)
    if not root.is_dir():
        print(json.dumps({"error": f"brain root not found: {root}"}), file=sys.stderr)
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

    path = args.evidence or evidence_path(root, source.id)
    if not path.is_file():
        print(json.dumps({"error": f"evidence file not found: {path}"}), file=sys.stderr)
        return 2

    allowed = set(allowed_artifacts(source))
    blocked = set(blocked_artifacts(source))
    state = load_state(root)
    current = source_state(state, source.id)
    items = current.setdefault("items", {})
    staged = []
    skipped = []
    staged_count = 0

    try:
        records = latest_records_by_external_id(list(iter_jsonl(path)))
    except ValueError as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 1

    for record in records:
        external_id = str(record.get("external_id") or "").strip()
        if args.external_id and external_id != args.external_id:
            continue
        if staged_count >= args.limit:
            break
        current_visibility = visibility(record)
        if current_visibility in PRIVATE_VISIBILITIES:
            skipped.append({"external_id": external_id, "reason": "private visibility"})
            continue
        if current_visibility in RESTRICTED_VISIBILITIES and not args.allow_restricted:
            skipped.append({"external_id": external_id, "reason": "restricted visibility"})
            continue
        artifact_type = str(record.get("artifact_type") or "curated_summary")
        if allowed and artifact_type not in allowed:
            skipped.append({"external_id": external_id, "reason": f"artifact_type {artifact_type!r} is not allowed"})
            continue
        if artifact_type in blocked:
            skipped.append({"external_id": external_id, "reason": f"artifact_type {artifact_type!r} is blocked"})
            continue
        previous = items.get(external_id, {})
        if previous.get("staged_hash") == record.get("hash") and not args.overwrite:
            skipped.append({"external_id": external_id, "reason": "already staged with same hash"})
            continue
        try:
            result = stage_record(root, source, record, write=args.write, overwrite=args.overwrite)
        except (RuntimeError, ValueError) as exc:
            skipped.append({"external_id": external_id, "reason": str(exc)})
            continue
        staged.append(result)
        staged_count += 1
        if args.write:
            previous["staged_hash"] = record.get("hash")
            previous["last_staged_at"] = utc_now()
            items[external_id] = previous

    if args.write:
        current["last_successful_extract"] = utc_now()
        current["last_extract_counts"] = {"staged": len(staged), "skipped": len(skipped)}
        save_state(root, state)

    output = {
        "action": "extracted" if args.write else "would-extract",
        "source_id": source.id,
        "evidence": str(path.relative_to(root)) if path.is_relative_to(root) else str(path),
        "staged": staged,
        "skipped": skipped,
        "note": None if args.write else "preview only; rerun with --write to persist",
    }
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
