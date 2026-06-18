#!/usr/bin/env python3
"""Validate source-registry.yml and enforce source-instance capture eligibility."""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from harness_common import resolve_root
from source_registry import find_source, is_capture_eligible, load_registry


DEFAULT_ROOT = (
    os.environ.get("BRAIN_ROOT")
    or os.environ.get("COMPANY_BRAIN_ROOT")
    or os.environ.get("COMPANY_OS_ROOT")
    or os.getcwd()
)


def render(report_json: dict, *, selected: dict | None = None) -> str:
    lines = []
    lines.append("")
    lines.append("SOURCE REGISTRY CHECK [" + ("ok" if report_json["ok"] else "needs attention") + "]")
    lines.append(f"path: {report_json['path']}")
    lines.append("")
    if report_json["errors"]:
        lines.append("Blocking issues:")
        for error in report_json["errors"]:
            lines.append(f"- {error}")
        lines.append("")
    if report_json["warnings"]:
        lines.append("Warnings:")
        for warning in report_json["warnings"]:
            lines.append(f"- {warning}")
        lines.append("")
    lines.append("Sources:")
    for source in report_json["sources"]:
        eligible = "capture-ready" if source["eligible_for_capture"] else "not capture-ready"
        lines.append(
            f"- {source['id']} ({source['connector']}): {source['status']}, "
            f"{source['control_tier']}, {eligible}"
        )
    if selected:
        lines.append("")
        lines.append(
            f"Selected source: {selected['id']} -> "
            f"{'capture allowed' if selected['eligible_for_capture'] else 'capture refused'}"
        )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate Company Brain source registry.")
    parser.add_argument("--root", default=DEFAULT_ROOT, help="brain root")
    parser.add_argument("--registry", default=None, help="registry path relative to root")
    parser.add_argument("--source-id", default=None, help="specific source instance id")
    parser.add_argument("--connector", default=None, help="specific connector type")
    parser.add_argument("--for-capture", action="store_true", help="require selected source to be capture-eligible")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    root = resolve_root(args.root)
    if not root.is_dir():
        print(json.dumps({"error": f"brain root not found: {root}"}), file=sys.stderr)
        return 2

    report = load_registry(root, args.registry)
    data = report.to_json()
    selected_json = None
    selected = None

    if args.source_id or args.connector:
        selected = find_source(report, source_id=args.source_id, connector=args.connector)
        if selected is None:
            message = "no unique source matched"
            if args.source_id:
                message += f" id={args.source_id!r}"
            if args.connector:
                message += f" connector={args.connector!r}"
            data["errors"].append(message)
            data["ok"] = False
        else:
            selected_json = {
                "id": selected.id,
                "connector": selected.connector,
                "control_tier": selected.control_tier,
                "status": selected.status,
                "capture_allowed": selected.capture_allowed,
                "eligible_for_capture": is_capture_eligible(selected),
            }
            data["selected_source"] = selected_json
            if args.for_capture and not is_capture_eligible(selected):
                data["errors"].append(f"{selected.id}: source is not eligible for capture")
                data["ok"] = False

    print(json.dumps(data, indent=2, sort_keys=True) if args.json else render(data, selected=selected_json))
    return 0 if data["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
