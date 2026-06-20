#!/usr/bin/env python3
"""Generate a Company Brain operating schedule."""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import date
from pathlib import Path

from harness_common import conventions_dir, find_config_path, resolve_root


DEFAULT_ROOT = (
    os.environ.get("BRAIN_ROOT")
    or os.environ.get("COMPANY_BRAIN_ROOT")
    or os.environ.get("COMPANY_OS_ROOT")
    or os.getcwd()
)
PROFILE_GOVERNED = "governed"
PROFILE_SIMPLE_TEAM = "simple-team"
PROFILE_AUTO = "auto"


def detect_operating_profile(root: Path) -> str:
    path = find_config_path(root)
    if path is None:
        return PROFILE_GOVERNED
    for raw in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        stripped = raw.strip()
        if stripped.startswith("operating_profile:"):
            value = stripped.split(":", 1)[1].strip().strip("\"'")
            if value in {PROFILE_GOVERNED, PROFILE_SIMPLE_TEAM}:
                return value
    return PROFILE_GOVERNED


def schedule_markdown(
    *,
    mode: str,
    time: str,
    timezone: str,
    champion: str,
    operator: str,
    operating_profile: str,
) -> str:
    autonomous = mode == "autonomous"
    simple_team = operating_profile == PROFILE_SIMPLE_TEAM
    review_line = (
        "Review flagged changes daily; routine low-risk staging may run without pre-approval."
        if autonomous else
        "Review every proposed note before promotion. No unattended promotion."
    )
    if simple_team:
        review_line = (
            "Process clearly low-risk manual ADD_TO_BRAIN contributions when policy allows it; "
            "review sensitive or unclear items daily."
        )
    promotion_line = (
        "Auto-promote only if source registry allows it, destination is non-sensitive, and category is explicitly low-risk."
        if autonomous else
        "Promotion requires an explicit human approve/reject/revise decision."
    )
    if simple_team:
        promotion_line = (
            "Manual drop-zone contributions can bypass item-by-item approval only when low-risk; "
            "connector-derived proposals still follow source policy."
        )
    digest_step = "7. Run ADD_TO_BRAIN digest and review flagged drop-zone items.\n" if simple_team else ""
    review_step_number = "8" if simple_team else "7"
    publish_step_number = "9" if simple_team else "8"
    command_digest = "python3 <plugin-root>/bin/add-to-brain-digest.py --root \"$BRAIN_ROOT\" --write\n" if simple_team else ""
    return f"""---
status: active
tags:
  - schedule
  - company-brain
last_verified: {date.today().isoformat()}
---

# Company Brain Operating Schedule

Mode: `{mode}`
Operating profile: `{operating_profile}`
Local run time: `{time}` `{timezone}`
Brain Owner: `{champion}`
Operator identity: `{operator}`

## Daily Morning Loop

1. Run connection check.
2. Validate source registry.
3. Pull approved source records into private evidence.
4. Extract allowed artifacts into staged proposals.
5. Run brain health.
6. Run brain lint for stale, duplicate, broken, or unprovenanced notes.
{digest_step}{review_step_number}. Review staged proposals.
{publish_step_number}. Publish one short punch list: blockers, warnings, next three fixes.

## Commands

```bash
export BRAIN_ROOT="/path/to/company-brain-root"
python3 <plugin-root>/bin/connections-check.py --root "$BRAIN_ROOT" --live
python3 <plugin-root>/bin/source-registry-check.py --root "$BRAIN_ROOT"
# For each approved source, connector adapters produce normalized JSONL first.
python3 <plugin-root>/bin/source-pull.py --root "$BRAIN_ROOT" --source-id "<source-id>" --input-jsonl "<records.jsonl>" --write
python3 <plugin-root>/bin/source-extract.py --root "$BRAIN_ROOT" --source-id "<source-id>" --write
python3 <plugin-root>/bin/brain-health.py --root "$BRAIN_ROOT"
python3 <plugin-root>/bin/brain-lint.py --root "$BRAIN_ROOT" --stale-days 30
{command_digest}```

## Human Review Policy

- {review_line}
- {promotion_line}
- Meeting-derived, HR, legal, finance, customer-confidential, and strategy-changing notes stay human-approved.
- Personal connectors never feed the shared brain unless explicitly delegated, scoped, approved, and source-registered.
{"- ADD_TO_BRAIN is for manual team contributions only, not broad connector exports." if simple_team else ""}

## Autonomous Mode Guardrails

{"- Enabled: scheduled checks, lint, source validation, staging from approved sources, and flagged digests." if autonomous else "- Disabled for now: autonomous source capture and auto-promotion."}
{"- Disabled: personal connectors, broad email capture, unrestricted transcript dumps, restricted-folder writes." if autonomous else "- To graduate: run the manual loop for 1-2 weeks, then allow only low-risk staging."}

## Escalation

Escalate to the Brain Owner when:

- a source registry entry is invalid or newly proposed
- a connector fails auth or scope checks
- two notes contradict each other
- a note is stale but still used by a skill or routing file
- a teammate requests deletion/correction
- restricted folder access appears broader than policy

## Cadence

- Daily: run checks and review queue.
- Weekly: prune stale docs, review source registry, and update the operator role.
- Monthly: review permissions, source ownership, retention, and auto-promotion rules.
"""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate a Company Brain operating schedule.")
    parser.add_argument("--root", default=DEFAULT_ROOT, help="brain root")
    parser.add_argument("--mode", choices=["human", "autonomous"], default="human")
    parser.add_argument(
        "--operating-profile",
        choices=[PROFILE_AUTO, PROFILE_GOVERNED, PROFILE_SIMPLE_TEAM],
        default=PROFILE_AUTO,
        help="override profile; auto reads company-brain.yml when available",
    )
    parser.add_argument("--time", default="08:30", help="local time for daily loop")
    parser.add_argument("--timezone", default="local")
    parser.add_argument("--champion", default="brain-owner", help="Brain Owner name")
    parser.add_argument("--operator", default="brain-operator", help="Brain Operator name")
    parser.add_argument("--write", action="store_true", help="write schedule.md under conventions dir")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    root = resolve_root(args.root)
    if not root.is_dir():
        print(json.dumps({"error": f"brain root not found: {root}"}), file=sys.stderr)
        return 2
    operating_profile = (
        detect_operating_profile(root)
        if args.operating_profile == PROFILE_AUTO else
        args.operating_profile
    )

    body = schedule_markdown(
        mode=args.mode,
        time=args.time,
        timezone=args.timezone,
        champion=args.champion,
        operator=args.operator,
        operating_profile=operating_profile,
    )
    target = conventions_dir(root) / "schedule.md"
    if args.write:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(body, encoding="utf-8")
    result = {
        "action": "wrote" if args.write else "would-write",
        "path": str(target.relative_to(root)),
        "mode": args.mode,
        "operating_profile": operating_profile,
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
