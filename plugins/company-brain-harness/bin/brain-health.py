#!/usr/bin/env python3
"""brain-health — read-only Brain Health Score for a Company Brain root.

Scores a filesystem-backed knowledge root 0-100 across five dimensions and
prints a punch-list of what to populate next. Read-only: never writes to the
brain root, never descends into `14_Owner_Vault` (off-limits by policy).

Dimensions (20 each):
  Coverage    - % of leaf knowledge folders that contain real content
  Freshness   - % of curated notes verified within --fresh-days
  Routing     - nervous system present (root CLAUDE.md, conventions, folder indexes)
  Integrity   - notes have frontmatter and no broken internal links
  Activation  - content growth proxy (note count vs target + recent edits)

Usage:
    bin/brain-health.py                 # score the current directory / configured root
    bin/brain-health.py --root <path>   # score an alternate root (e.g. local draft)
    bin/brain-health.py --json          # machine-readable output
    bin/brain-health.py --fresh-days 45 # freshness window (default 45)

Exit codes:
    0 = score >= 60 (Working or better)
    1 = score 21-59 (Seeded / building)
    2 = score <= 20 (Skeleton)
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import date, datetime, timezone
from pathlib import Path

from harness_common import (
    config_list,
    conventions_dir,
    resolve_root,
    restricted_prefixes,
    routing_file,
)

DEFAULT_ROOT = (
    os.environ.get("BRAIN_ROOT")
    or os.environ.get("COMPANY_BRAIN_ROOT")
    or os.environ.get("COMPANY_OS_ROOT")
    or os.getcwd()
)

INDEX_NAME = "00_INDEX.md"
META_MD = {INDEX_NAME, "README.md", "CLAUDE.md"}
ACTIVATION_TARGET = 40  # content notes for a "healthy early" brain

MD_LINK_RE = re.compile(r"\[[^\]]+\]\((?!https?:|mailto:|#)([^)]+)\)")
FM_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def _archive_like(name: str) -> bool:
    lowered = name.lower()
    return lowered in {"archive", "99_archive"} or lowered.endswith("_archive")


def _top_names(root: Path) -> list[str]:
    return sorted(p.name for p in root.iterdir() if p.is_dir() and not p.name.startswith("."))


def _conventions_top(root: Path) -> str:
    rel = conventions_dir(root).relative_to(root)
    return rel.parts[0] if rel.parts else ""


def _content_excluded_top(root: Path) -> set[str]:
    return {
        _conventions_top(root),
        *restricted_prefixes(root),
        *(name for name in _top_names(root) if _archive_like(name)),
    }


def _index_required_top(root: Path) -> list[str]:
    excluded = {_conventions_top(root), *restricted_prefixes(root)}
    return [name for name in _top_names(root) if name not in excluded]


def _priority_top(root: Path) -> set[str]:
    return set(config_list(root, "health", "priority_folders", ()))


def _is_excluded(rel: Path, root: Path) -> bool:
    parts = rel.parts
    return bool(parts) and parts[0] in _content_excluded_top(root)


def walk_files(root: Path):
    """Yield (path, rel) for every file, skipping dotfiles and excluded tops."""
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]
        d = Path(dirpath)
        rel_dir = d.relative_to(root)
        # prune excluded top-level subtrees
        if _is_excluded(rel_dir, root):
            dirnames[:] = []
            continue
        for fn in filenames:
            if fn.startswith("."):
                continue
            yield d / fn, (rel_dir / fn)


def leaf_folders(root: Path):
    """Immediate subfolders (depth-2) of included top-levels = leaf knowledge folders."""
    excluded = _content_excluded_top(root)
    leaves = []
    for top in sorted(p for p in root.iterdir() if p.is_dir()):
        if top.name.startswith(".") or top.name in excluded:
            continue
        subs = [s for s in top.iterdir() if s.is_dir() and not s.name.startswith(".")]
        if subs:
            leaves.extend(subs)
        else:
            leaves.append(top)  # top with no subfolders is itself a leaf
    return leaves


def has_content(folder: Path) -> bool:
    """True if folder (recursively) holds any file that isn't a 00_INDEX.md."""
    for dirpath, dirnames, filenames in os.walk(folder):
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]
        for fn in filenames:
            if fn.startswith("."):
                continue
            if fn != INDEX_NAME:
                return True
    return False


def parse_last_verified(text: str):
    m = FM_RE.match(text)
    if not m:
        return None
    fm = m.group(1)
    lv = re.search(r"^last_verified:\s*(\d{4}-\d{2}-\d{2})", fm, re.MULTILINE)
    if not lv:
        return None
    try:
        return datetime.strptime(lv.group(1), "%Y-%m-%d").date()
    except ValueError:
        return None


def has_frontmatter(text: str) -> bool:
    m = FM_RE.match(text)
    if not m:
        return False
    fm = m.group(1)
    return "status:" in fm and "tags:" in fm


def score(root: Path, fresh_days: int) -> dict:
    today = date.today()
    md_files, content_notes, source_files = [], [], []
    for path, rel in walk_files(root):
        if path.suffix.lower() == ".md":
            md_files.append((path, rel))
            if path.name not in META_MD:
                content_notes.append((path, rel))
        else:
            source_files.append((path, rel))

    # --- Coverage ---
    leaves = leaf_folders(root)
    populated = [lf for lf in leaves if has_content(lf)]
    coverage = 20.0 * (len(populated) / len(leaves)) if leaves else 0.0
    empty_leaves = [lf.relative_to(root) for lf in leaves if lf not in populated]

    # --- Freshness ---
    fresh = stale = undated = 0
    for path, _ in content_notes:
        lv = parse_last_verified(path.read_text(errors="ignore"))
        if lv is None:
            undated += 1
        elif (today - lv).days <= fresh_days:
            fresh += 1
        else:
            stale += 1
    freshness = 20.0 * (fresh / len(content_notes)) if content_notes else 0.0

    # --- Routing ---
    checks = []
    route = routing_file(root)
    conv = conventions_dir(root)
    checks.append((str(route.relative_to(root)), route.exists()))
    checks.append(("conventions README", (conv / "README.md").exists()))
    index_required_top = _index_required_top(root)
    idx_present = sum(
        1 for t in index_required_top if (root / t / INDEX_NAME).exists()
    )
    structural = sum(1 for _, ok in checks if ok)
    index_score = (idx_present / len(index_required_top)) if index_required_top else 1.0
    routing = (structural / 2) * 8 + index_score * 12
    missing_idx = [t for t in index_required_top if not (root / t / INDEX_NAME).exists()]

    # --- Integrity ---
    dead_links, no_fm = [], []
    for path, rel in md_files:
        text = path.read_text(errors="ignore")
        if path.name not in META_MD and not has_frontmatter(text):
            no_fm.append(str(rel))
        for target in MD_LINK_RE.findall(text):
            tgt = target.split("#")[0].strip()
            if not tgt:
                continue
            resolved = (path.parent / tgt).resolve()
            if not resolved.exists():
                dead_links.append(f"{rel} -> {tgt}")
    passing = sum(
        1
        for path, rel in md_files
        if (path.name in META_MD or has_frontmatter(path.read_text(errors="ignore")))
        and not any(str(rel) in d for d in dead_links)
    )
    integrity = 20.0 * (passing / len(md_files)) if md_files else 20.0

    # --- Activation (proxy) ---
    recent_edits = 0
    cutoff = datetime.now(timezone.utc).timestamp() - 7 * 86400
    for path, _ in content_notes:
        if path.stat().st_mtime >= cutoff:
            recent_edits += 1
    growth = min(1.0, len(content_notes) / ACTIVATION_TARGET)
    recency = min(1.0, recent_edits / 10)
    activation = 20.0 * (0.7 * growth + 0.3 * recency)

    total = round(coverage + freshness + routing + integrity + activation)
    band = (
        "Operating" if total >= 81 else
        "Strong" if total >= 61 else
        "Working" if total >= 41 else
        "Seeded" if total >= 21 else
        "Skeleton"
    )
    return {
        "score": total,
        "band": band,
        "dimensions": {
            "coverage": round(coverage, 1),
            "freshness": round(freshness, 1),
            "routing": round(routing, 1),
            "integrity": round(integrity, 1),
            "activation": round(activation, 1),
        },
        "stats": {
            "leaf_folders": len(leaves),
            "populated_leaves": len(populated),
            "content_notes": len(content_notes),
            "source_files": len(source_files),
            "index_files_present": idx_present,
            "fresh_notes": fresh, "stale_notes": stale, "undated_notes": undated,
            "dead_links": len(dead_links), "notes_missing_frontmatter": len(no_fm),
        },
        "punch_list": {
            "empty_priority_folders": sorted(
                str(e) for e in empty_leaves if e.parts and e.parts[0] in _priority_top(root)
            ),
            "empty_other_folders": sorted(
                str(e) for e in empty_leaves if not (e.parts and e.parts[0] in _priority_top(root))
            ),
            "missing_indexes": missing_idx,
            "dead_links": dead_links,
            "notes_missing_frontmatter": no_fm,
        },
    }


def render(result: dict) -> str:
    d = result["dimensions"]
    s = result["stats"]
    p = result["punch_list"]
    bar = lambda v: "█" * int(round(v)) + "░" * (20 - int(round(v)))
    out = []
    out.append(f"\n  BRAIN HEALTH SCORE   {result['score']}/100   [{result['band']}]\n")
    out.append(f"  Coverage    {bar(d['coverage'])}  {d['coverage']:>4}/20   "
               f"({s['populated_leaves']}/{s['leaf_folders']} folders have content)")
    out.append(f"  Freshness   {bar(d['freshness'])}  {d['freshness']:>4}/20   "
               f"({s['fresh_notes']} fresh, {s['stale_notes']} stale, {s['undated_notes']} undated)")
    out.append(f"  Routing     {bar(d['routing'])}  {d['routing']:>4}/20   "
               f"({s['index_files_present']} folder indexes present)")
    out.append(f"  Integrity   {bar(d['integrity'])}  {d['integrity']:>4}/20   "
               f"({s['dead_links']} dead links, {s['notes_missing_frontmatter']} missing frontmatter)")
    out.append(f"  Activation  {bar(d['activation'])}  {d['activation']:>4}/20   "
               f"({s['content_notes']} content notes)")
    out.append("")
    if p["empty_priority_folders"]:
        out.append("  ── Punch-list: empty PRIORITY folders (populate first) ──")
        for e in p["empty_priority_folders"]:
            out.append(f"    □ {e}")
        out.append("")
    if p["missing_indexes"]:
        out.append("  ⚠ missing folder indexes: " + ", ".join(p["missing_indexes"]))
    if p["dead_links"]:
        out.append("  ⚠ dead links:")
        for dl in p["dead_links"]:
            out.append(f"    {dl}")
    if p["notes_missing_frontmatter"]:
        out.append("  ⚠ notes missing frontmatter: " + ", ".join(p["notes_missing_frontmatter"]))
    rest = len(p["empty_other_folders"])
    if rest:
        out.append(f"\n  (+ {rest} more empty non-priority folders)")
    return "\n".join(out) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description="Read-only Brain Health Score for a Company Brain root.")
    ap.add_argument("--root", default=DEFAULT_ROOT, help="brain root to score")
    ap.add_argument("--fresh-days", type=int, default=45, help="freshness window in days")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args()

    root = Path(args.root).expanduser().resolve()
    if not root.is_dir():
        print(f"error: root not found: {root}", file=sys.stderr)
        return 3

    result = score(root, args.fresh_days)
    result["root"] = str(root)
    result["generated"] = date.today().isoformat()
    print(json.dumps(result, indent=2) if args.json else render(result))

    return 0 if result["score"] >= 60 else (1 if result["score"] >= 21 else 2)


if __name__ == "__main__":
    sys.exit(main())
