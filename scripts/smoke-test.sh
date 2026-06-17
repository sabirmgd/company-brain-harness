#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PLUGIN_DIR="$ROOT_DIR/plugins/company-brain-harness"
BIN_DIR="$PLUGIN_DIR/bin"
TMP_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/company-brain-smoke.XXXXXX")"

cleanup() {
  rm -rf "$TMP_ROOT"
}
trap cleanup EXIT

mkdir -p "$TMP_ROOT/Brain_Conventions" "$TMP_ROOT/Strategy" "$TMP_ROOT/Operations" "$TMP_ROOT/Restricted"

cat > "$TMP_ROOT/CLAUDE.md" <<'EOF'
# Smoke Brain Routing

Route strategy notes to Strategy/ and operational notes to Operations/.
EOF

cat > "$TMP_ROOT/Brain_Conventions/README.md" <<'EOF'
# Smoke Brain Conventions

This is a synthetic brain root used by the Company Brain Harness smoke test.
EOF

cat > "$TMP_ROOT/Brain_Conventions/CAPTURE_POLICY.md" <<'EOF'
# Capture Policy

Only company-controlled sources may enter this smoke brain.
EOF

cat > "$TMP_ROOT/Brain_Conventions/HARNESS_FLOWS.md" <<'EOF'
# Harness Flows

Stage, approve, then promote.
EOF

cat > "$TMP_ROOT/Brain_Conventions/HARNESS_STATUS.md" <<'EOF'
# Harness Status

Smoke test fixture.
EOF

cat > "$TMP_ROOT/company-brain.yml" <<'EOF'
schema_version: "1.0"
kind: company_brain_config
brain:
  routing_file: CLAUDE.md
  conventions_dir: Brain_Conventions
  staging_dir: Brain_Conventions/Staging
  restricted_prefixes:
    - Restricted
health:
  priority_folders:
    - Strategy
EOF

cat > "$TMP_ROOT/Strategy/00_INDEX.md" <<'EOF'
---
status: active
tags:
  - index
  - strategy
last_verified: 2026-06-18
---

# Strategy Index
EOF

cat > "$TMP_ROOT/Operations/00_INDEX.md" <<'EOF'
---
status: active
tags:
  - index
  - operations
last_verified: 2026-06-18
---

# Operations Index
EOF

python3 "$BIN_DIR/connections-check.py" --root "$TMP_ROOT" --json >/tmp/company-brain-connections.json

set +e
python3 "$BIN_DIR/brain-health.py" --root "$TMP_ROOT" --json >/tmp/company-brain-health.json
health_status=$?
set -e
if [[ "$health_status" -gt 2 ]]; then
  echo "brain-health exited with unexpected status $health_status" >&2
  exit 1
fi

python3 - "$TMP_ROOT" <<'PY'
import json
import sys
from pathlib import Path

connections = json.loads(Path("/tmp/company-brain-connections.json").read_text())
health = json.loads(Path("/tmp/company-brain-health.json").read_text())
if connections["overall"] != "ready":
    raise SystemExit(f"connections not ready: {connections['overall']}")
if health["stats"]["index_files_present"] != 2:
    raise SystemExit(f"unexpected index count: {health['stats']['index_files_present']}")
PY

printf '# Smoke Note\n\nThis note proves staging and approval work.\n' |
  python3 "$BIN_DIR/stage-brain-note.py" \
    --root "$TMP_ROOT" \
    --target Strategy/smoke-note.md \
    --title "Smoke Note" \
    --tag strategy --tag smoke \
    --source-type smoke \
    --source-ref smoke-test \
    --author smoke-runner \
    --id smoke-note >/tmp/company-brain-stage.json

python3 "$BIN_DIR/approve-staged-note.py" \
  --root "$TMP_ROOT" \
  --id smoke-note \
  --decision approve \
  --reviewer smoke-reviewer \
  --write >/tmp/company-brain-approve.json

test -f "$TMP_ROOT/Strategy/smoke-note.md"
test -f "$TMP_ROOT/Brain_Conventions/Staging/approval-ledger.jsonl"

set +e
printf '# Restricted\n\nNope.\n' |
  python3 "$BIN_DIR/promote-to-brain.py" \
    --root "$TMP_ROOT" \
    --target Restricted/nope.md \
    --tag restricted --tag smoke \
    --source-type smoke \
    --source-ref smoke-test \
    --author smoke-runner \
    --write >/tmp/company-brain-restricted.out 2>/tmp/company-brain-restricted.err
restricted_status=$?
set -e
if [[ "$restricted_status" -eq 0 ]]; then
  echo "restricted promotion unexpectedly succeeded" >&2
  exit 1
fi

echo "smoke test passed"
