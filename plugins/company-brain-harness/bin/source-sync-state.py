#!/usr/bin/env python3
"""Inspect source sync cursors and evidence state."""
from __future__ import annotations

import argparse
import json
import os

from harness_common import resolve_root
from source_sync_common import load_state, save_state, source_state, utc_now


DEFAULT_ROOT = (
    os.environ.get("BRAIN_ROOT")
    or os.environ.get("COMPANY_BRAIN_ROOT")
    or os.environ.get("COMPANY_OS_ROOT")
    or os.getcwd()
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Inspect or update Company Brain source sync state.")
    parser.add_argument("--root", default=DEFAULT_ROOT, help="Company Brain root")
    parser.add_argument("--source-id", default=None)
    parser.add_argument("--set-cursor", default=None)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)

    root = resolve_root(args.root)
    if not root.is_dir():
        print(json.dumps({"error": f"brain root not found: {root}"}))
        return 2

    state = load_state(root)
    if args.source_id and args.set_cursor is not None:
        current = source_state(state, args.source_id)
        current["cursor"] = args.set_cursor
        current["cursor_updated_at"] = utc_now()
        if args.write:
            save_state(root, state)
    elif args.source_id:
        state = source_state(state, args.source_id)

    result = {
        "action": "updated" if args.write and args.set_cursor is not None else "preview",
        "state": state,
        "note": None if args.write or args.set_cursor is None else "preview only; rerun with --write to persist",
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
