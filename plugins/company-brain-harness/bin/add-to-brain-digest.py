#!/usr/bin/env python3
"""Create an operator digest for the simple-team ADD_TO_BRAIN drop zone."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from harness_common import path_has_prefix, resolve_root, restricted_prefixes, safe_relative_path


DEFAULT_ROOT = (
    os.environ.get("BRAIN_ROOT")
    or os.environ.get("COMPANY_BRAIN_ROOT")
    or os.environ.get("COMPANY_OS_ROOT")
    or os.getcwd()
)
DEFAULT_DROP_ZONE = "ADD_TO_BRAIN"
DEFAULT_OUTPUT = "system/digests/latest.md"
SKIP_FILENAMES = {"README.md"}
SENSITIVE_MARKERS = (
    "api_key",
    "apikey",
    "bank",
    "compensation",
    "credential",
    "finance",
    "hr",
    "key=",
    "legal",
    "password",
    "payroll",
    "private",
    "secret",
    "ssn",
    "token",
)
LOW_RISK_EXTENSIONS = {
    ".csv",
    ".doc",
    ".docx",
    ".html",
    ".json",
    ".md",
    ".pdf",
    ".ppt",
    ".pptx",
    ".rtf",
    ".txt",
    ".xls",
    ".xlsx",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def human_size(size: int) -> str:
    units = ("B", "KB", "MB", "GB")
    value = float(size)
    for unit in units:
        if value < 1024 or unit == units[-1]:
            return f"{value:.1f} {unit}" if unit != "B" else f"{size} B"
        value /= 1024
    return f"{size} B"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def text_sample(path: Path, limit: int = 65536) -> str:
    try:
        return path.read_bytes()[:limit].decode("utf-8", errors="ignore").lower()
    except OSError:
        return ""


def classify(path: Path, rel: Path) -> tuple[str, str]:
    lowered = rel.as_posix().lower()
    if path.is_symlink():
        return "review", "symlink needs operator review"
    if path.suffix.lower() not in LOW_RISK_EXTENSIONS:
        return "review", "unknown file type"
    if any(marker in lowered for marker in SENSITIVE_MARKERS):
        return "review", "path suggests sensitive material"
    sample = text_sample(path)
    if sample and any(marker in sample for marker in SENSITIVE_MARKERS):
        return "review", "content suggests sensitive material"
    return "ready", "low-risk manual contribution candidate"


def iter_drop_zone_files(root: Path, drop_zone: Path) -> list[dict[str, object]]:
    base = root / drop_zone
    if not base.exists():
        return []
    base_resolved = base.resolve()
    items: list[dict[str, object]] = []
    restricted = restricted_prefixes(root)
    for path in sorted(base.rglob("*")):
        if any(part.startswith(".") for part in path.relative_to(base).parts):
            continue
        if not path.is_file() and not path.is_symlink():
            continue
        if path.name in SKIP_FILENAMES:
            continue
        rel = path.relative_to(root)
        if any(path_has_prefix(rel, prefix) for prefix in restricted):
            items.append({
                "path": rel.as_posix(),
                "status": "review",
                "reason": "restricted-prefix path",
                "size": None,
                "modified": None,
                "sha256": None,
            })
            continue
        if path.is_symlink():
            status, reason = classify(path, rel)
            items.append({
                "path": rel.as_posix(),
                "status": status,
                "reason": reason,
                "size": None,
                "modified": None,
                "sha256": None,
            })
            continue
        try:
            path.resolve().relative_to(base_resolved)
        except ValueError:
            items.append({
                "path": rel.as_posix(),
                "status": "review",
                "reason": "path escapes drop zone",
                "size": None,
                "modified": None,
                "sha256": None,
            })
            continue
        stat = path.stat()
        status, reason = classify(path, rel)
        items.append({
            "path": rel.as_posix(),
            "status": status,
            "reason": reason,
            "size": stat.st_size,
            "modified": datetime.fromtimestamp(stat.st_mtime, timezone.utc).replace(microsecond=0).isoformat(),
            "sha256": sha256_file(path),
        })
    return items


def digest_markdown(root: Path, drop_zone: Path, items: list[dict[str, object]]) -> str:
    generated_at = utc_now()
    ready = [item for item in items if item["status"] == "ready"]
    review = [item for item in items if item["status"] != "ready"]
    if not items:
        table = "No files found in the drop zone.\n"
    else:
        rows = [
            "| Status | Path | Size | Modified | Reason |",
            "|---|---|---:|---|---|",
        ]
        for item in items:
            size = human_size(int(item["size"])) if item.get("size") is not None else "-"
            modified = str(item.get("modified") or "-")
            rows.append(
                f"| {item['status']} | `{item['path']}` | {size} | {modified} | {item['reason']} |"
            )
        table = "\n".join(rows) + "\n"
    return f"""---
status: active
tags:
  - digest
  - add-to-brain
last_verified: {generated_at[:10]}
---

# Add-To-Brain Digest

Generated: `{generated_at}`
Root: `{root}`
Drop zone: `{drop_zone.as_posix()}`

## Summary

- ready to process: {len(ready)}
- needs review: {len(review)}
- total files: {len(items)}

## Files

{table}
## Operator Guidance

- Process `ready` items only when they are clearly company-owned and relevant.
- Review flagged items before any staging or promotion.
- Do not copy credentials, personal/private material, HR, legal, finance, or restricted content into shared notes.
- Source connectors still need `source-registry.yml`; this digest is for manual team contributions.
"""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Create an ADD_TO_BRAIN operator digest.")
    parser.add_argument("--root", default=DEFAULT_ROOT, help="brain root")
    parser.add_argument("--drop-zone", default=DEFAULT_DROP_ZONE, help="drop-zone path relative to root")
    parser.add_argument("--output", default=DEFAULT_OUTPUT, help="digest output path relative to root")
    parser.add_argument("--write", action="store_true", help="write the digest; default is preview-only")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    root = resolve_root(args.root)
    if not root.is_dir():
        print(json.dumps({"error": f"brain root not found: {root}"}), file=sys.stderr)
        return 2

    try:
        drop_zone = safe_relative_path(args.drop_zone, name="drop zone")
        output = safe_relative_path(args.output, name="output path")
    except ValueError as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 2

    if any(path_has_prefix(output, prefix) for prefix in restricted_prefixes(root)):
        print(json.dumps({"error": "output path must not be under a restricted prefix"}), file=sys.stderr)
        return 2

    items = iter_drop_zone_files(root, drop_zone)
    body = digest_markdown(root, drop_zone, items)
    target = root / output
    if args.write:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(body, encoding="utf-8")

    result = {
        "action": "wrote" if args.write else "would-write",
        "root": str(root),
        "drop_zone": drop_zone.as_posix(),
        "output": output.as_posix(),
        "ready": sum(1 for item in items if item["status"] == "ready"),
        "review": sum(1 for item in items if item["status"] != "ready"),
        "total": len(items),
        "items": items,
        "note": None if args.write else "preview only; rerun with --write to persist",
    }
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(body)
        if not args.write:
            print("\n# preview only; rerun with --write to persist", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
