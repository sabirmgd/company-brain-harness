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

printf '# Smoke Note\n\nThis note proves staging and approval work. It may mention stale source handling without becoming a contradiction marker.\n' |
  python3 "$BIN_DIR/stage-brain-note.py" \
    --root "$TMP_ROOT" \
    --target Strategy/smoke-note.md \
    --title "Smoke Note" \
    --tag strategy --tag smoke \
    --source-type smoke \
    --source-ref smoke-test \
    --author smoke-runner \
    --id smoke-note \
    --write >/tmp/company-brain-stage.json

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

SCAFFOLD_ROOT="$TMP_ROOT/scaffolded-company"

python3 "$BIN_DIR/brain-setup.py" \
  --root "$SCAFFOLD_ROOT" \
  --company-name "Acme Co" \
  --champion "Alex" \
  --operator "Ops Bot" >/tmp/company-brain-setup-preview.txt

if [[ -e "$SCAFFOLD_ROOT/CLAUDE.md" ]]; then
  echo "brain-setup preview unexpectedly wrote files" >&2
  exit 1
fi

python3 "$BIN_DIR/brain-setup.py" \
  --root "$SCAFFOLD_ROOT" \
  --company-name "Acme Co" \
  --champion "Alex" \
  --operator "Ops Bot" \
  --write >/tmp/company-brain-setup-write.txt

test -f "$SCAFFOLD_ROOT/CLAUDE.md"
test -f "$SCAFFOLD_ROOT/START_HERE.md"
test -f "$SCAFFOLD_ROOT/OWNER_GUIDE.md"
test -f "$SCAFFOLD_ROOT/OPERATOR_GUIDE.md"
test -f "$SCAFFOLD_ROOT/TEAM_MEMBER_GUIDE.md"
test -f "$SCAFFOLD_ROOT/INVITE_TEAM.md"
test -f "$SCAFFOLD_ROOT/TODAY.md"
test -f "$SCAFFOLD_ROOT/NEXT_ACTIONS.md"
test -f "$SCAFFOLD_ROOT/company-brain.yml"
test -f "$SCAFFOLD_ROOT/00_Company_Brain_Conventions/source-registry.yml"
test -f "$SCAFFOLD_ROOT/00_Company_Brain_Conventions/source-sync-state.json"
test -f "$SCAFFOLD_ROOT/00_Company_Brain_Conventions/CONNECTIONS.md"
test -f "$SCAFFOLD_ROOT/00_Company_Brain_Conventions/90_Staging/approval-ledger.jsonl"
test -f "$SCAFFOLD_ROOT/00_Company_Brain_Conventions/90_Staging/evidence/README.md"

python3 "$BIN_DIR/source-registry-check.py" \
  --root "$SCAFFOLD_ROOT" \
  --source-id acme-co-brain-root \
  --for-capture >/tmp/company-brain-sources.txt

cat >/tmp/company-brain-confluence-fixture.json <<'EOF'
{
  "results": [
    {
      "id": "12345",
      "title": "Confluence Smoke Page",
      "space": {"key": "DOCS", "name": "Docs"},
      "version": {"when": "2026-06-18T06:00:00.000Z", "by": {"displayName": "Docs Owner"}},
      "body": {"storage": {"value": "<h1>Confluence Smoke Page</h1><p>This page should normalize into a staged source record.</p>"}},
      "_links": {"base": "https://example.atlassian.net/wiki", "webui": "/spaces/DOCS/pages/12345/Confluence+Smoke+Page"}
    }
  ]
}
EOF

python3 "$BIN_DIR/confluence-export.py" \
  --input-json /tmp/company-brain-confluence-fixture.json \
  --space-key DOCS \
  --output-jsonl /tmp/company-brain-confluence-records.jsonl >/tmp/company-brain-confluence-export.json

python3 - <<'PY'
import json
from pathlib import Path

summary = json.loads(Path("/tmp/company-brain-confluence-export.json").read_text())
records = [json.loads(line) for line in Path("/tmp/company-brain-confluence-records.jsonl").read_text().splitlines()]
if summary["count"] != 1 or len(records) != 1:
    raise SystemExit(f"unexpected Confluence export output: {summary}, {records}")
record = records[0]
if record["external_id"] != "12345" or record["artifact_type"] != "curated_note":
    raise SystemExit(f"unexpected normalized Confluence record: {record}")
if "This page should normalize" not in record["summary"]:
    raise SystemExit(f"Confluence body text was not normalized: {record}")
PY

cat >/tmp/company-brain-source-records.jsonl <<'EOF'
{"external_id":"source-doc-1","title":"Source Sync Smoke","summary":"This normalized source record should stage into the brain review queue.","target_path":"Resources/source-sync-smoke.md","tags":["source","smoke"],"artifact_type":"curated_note","visibility":"team","author":"Smoke Source","cursor":"smoke-cursor-1"}
{"external_id":"private-source-1","title":"Private Source","summary":"This private record should be skipped.","target_path":"Resources/private.md","tags":["source","private"],"artifact_type":"curated_note","visibility":"personal","author":"Smoke Source"}
EOF

python3 "$BIN_DIR/source-pull.py" \
  --root "$SCAFFOLD_ROOT" \
  --source-id acme-co-brain-root \
  --input-jsonl /tmp/company-brain-source-records.jsonl \
  --cursor smoke-cursor-1 \
  --write >/tmp/company-brain-source-pull.json

python3 - <<'PY'
import json
from pathlib import Path

result = json.loads(Path("/tmp/company-brain-source-pull.json").read_text())
if result["accepted"] != 1:
    raise SystemExit(f"expected one accepted source record: {result}")
if len(result["skipped"]) != 1:
    raise SystemExit(f"expected one skipped private source record: {result}")
PY

python3 "$BIN_DIR/source-extract.py" \
  --root "$SCAFFOLD_ROOT" \
  --source-id acme-co-brain-root \
  --write >/tmp/company-brain-source-extract.json

SCAFFOLD_ROOT="$SCAFFOLD_ROOT" python3 - <<'PY'
import json
import os
from pathlib import Path

result = json.loads(Path("/tmp/company-brain-source-extract.json").read_text())
if len(result["staged"]) != 1:
    raise SystemExit(f"expected one staged source proposal: {result}")
state = json.loads(Path(os.environ["SCAFFOLD_ROOT"], "00_Company_Brain_Conventions", "source-sync-state.json").read_text())
cursor = state["sources"]["acme-co-brain-root"].get("cursor")
if cursor != "smoke-cursor-1":
    raise SystemExit(f"expected cursor smoke-cursor-1, got {cursor!r}")
PY

test -f "$SCAFFOLD_ROOT/00_Company_Brain_Conventions/90_Staging/evidence/acme-co-brain-root.jsonl"
test -f "$SCAFFOLD_ROOT/00_Company_Brain_Conventions/90_Staging/proposed/acme-co-brain-root-source-doc-1.md"

set +e
python3 "$BIN_DIR/source-registry-check.py" \
  --root "$SCAFFOLD_ROOT" \
  --source-id example-shared-apollo \
  --for-capture >/tmp/company-brain-apollo.txt
apollo_status=$?
set -e
if [[ "$apollo_status" -eq 0 ]]; then
  echo "proposed Apollo source unexpectedly allowed capture" >&2
  exit 1
fi

python3 "$BIN_DIR/brain-schedule.py" \
  --root "$SCAFFOLD_ROOT" \
  --mode human \
  --champion "Alex" \
  --operator "Ops Bot" >/tmp/company-brain-schedule-preview.md

python3 "$BIN_DIR/brain-schedule.py" \
  --root "$SCAFFOLD_ROOT" \
  --mode human \
  --champion "Alex" \
  --operator "Ops Bot" \
  --write >/tmp/company-brain-schedule-write.md

python3 "$BIN_DIR/brain-lint.py" --root "$SCAFFOLD_ROOT" >/tmp/company-brain-lint.txt

echo "smoke test passed"
