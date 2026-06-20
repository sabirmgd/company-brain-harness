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

mkdir -p "$TMP_ROOT/system" "$TMP_ROOT/brain/company" "$TMP_ROOT/brain/operations/daily" "$TMP_ROOT/brain/restricted"

cat > "$TMP_ROOT/CLAUDE.md" <<'EOF'
# Smoke Brain Routing

Route strategy notes to brain/company/ and operational notes to brain/operations/daily/.
EOF

cat > "$TMP_ROOT/system/README.md" <<'EOF'
# Smoke Brain Conventions

This is a synthetic brain root used by the Company Brain Harness smoke test.
EOF

cat > "$TMP_ROOT/system/capture-policy.md" <<'EOF'
# Capture Policy

Only company-controlled sources may enter this smoke brain.
EOF

cat > "$TMP_ROOT/system/flows.md" <<'EOF'
# Harness Flows

Stage, approve, then promote.
EOF

cat > "$TMP_ROOT/system/status.md" <<'EOF'
# Harness Status

Smoke test fixture.
EOF

cat > "$TMP_ROOT/company-brain.yml" <<'EOF'
schema_version: "1.0"
kind: company_brain_config
brain:
  routing_file: CLAUDE.md
  conventions_dir: system
  staging_dir: system/staging
  restricted_prefixes:
    - brain/restricted
health:
  priority_folders:
    - brain/company
    - brain/operations/daily
EOF

cat > "$TMP_ROOT/brain/company/README.md" <<'EOF'
---
status: active
tags:
  - index
  - strategy
last_verified: 2026-06-18
---

# brain/company Index
EOF

cat > "$TMP_ROOT/brain/operations/daily/README.md" <<'EOF'
---
status: active
tags:
  - index
  - operations
last_verified: 2026-06-18
---

# brain/operations/daily Index
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
    --target brain/company/smoke-note.md \
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

test -f "$TMP_ROOT/brain/company/smoke-note.md"
test -f "$TMP_ROOT/system/staging/approval-ledger.jsonl"

set +e
printf '# brain/restricted\n\nNope.\n' |
  python3 "$BIN_DIR/promote-to-brain.py" \
    --root "$TMP_ROOT" \
    --target brain/restricted/nope.md \
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
test -f "$SCAFFOLD_ROOT/start-here.md"
test -f "$SCAFFOLD_ROOT/owner-guide.md"
test -f "$SCAFFOLD_ROOT/operator-guide.md"
test -f "$SCAFFOLD_ROOT/team-member-guide.md"
test -f "$SCAFFOLD_ROOT/invite-team.md"
test -f "$SCAFFOLD_ROOT/today.md"
test -f "$SCAFFOLD_ROOT/next-actions.md"
test -f "$SCAFFOLD_ROOT/company-brain.yml"
test -f "$SCAFFOLD_ROOT/system/source-registry.yml"
test -f "$SCAFFOLD_ROOT/system/source-sync-state.json"
test -f "$SCAFFOLD_ROOT/system/connections.md"
test -f "$SCAFFOLD_ROOT/system/staging/approval-ledger.jsonl"
test -f "$SCAFFOLD_ROOT/system/staging/evidence/README.md"
test -f "$SCAFFOLD_ROOT/system/staging/raw/README.md"

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
  --include-raw \
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
if record.get("raw_format") != "md":
    raise SystemExit(f"Confluence raw evidence should be markdown: {record}")
raw_body = record.get("raw_body", "")
for expected in ("# Raw Confluence Page: Confluence Smoke Page", "## Readable Extract", "## Original Storage Body", "This page should normalize"):
    if expected not in raw_body:
        raise SystemExit(f"Confluence raw evidence is not readable: missing {expected!r}")
PY

cat >/tmp/company-brain-fireflies-fixture.json <<'EOF'
{
  "data": {
    "transcripts": [
      {
        "id": "meeting-123",
        "title": "Project Weekly Sync",
        "dateString": "2026-06-18T07:00:00.000Z",
        "duration": 42,
        "organizer_email": "operator@example.com",
        "participants": ["operator@example.com", "teammate@example.com"],
        "privacy": "link",
        "transcript_url": "https://app.fireflies.ai/view/meeting-123",
        "sentences": [
          {"index": 0, "speaker_name": "Operator", "start_time": 3.2, "end_time": 4.5, "text": "We need the launch checklist ready."},
          {"index": 1, "speaker_name": "Teammate", "start_time": 65.0, "end_time": 66.4, "text": "I will confirm the owner."}
        ],
        "summary": {
          "short_summary": "The team agreed on the launch checklist.",
          "topics_discussed": ["Launch", "Risks"],
          "action_items": "- Prepare checklist\\n- Confirm owner",
          "keywords": ["launch", "checklist"]
        }
      }
    ]
  }
}
EOF

python3 "$BIN_DIR/fireflies-export.py" \
  --input-json /tmp/company-brain-fireflies-fixture.json \
  --search Project \
  --include-raw-transcript \
  --output-jsonl /tmp/company-brain-fireflies-records.jsonl >/tmp/company-brain-fireflies-export.json

python3 - <<'PY'
import json
from pathlib import Path

summary = json.loads(Path("/tmp/company-brain-fireflies-export.json").read_text())
records = [json.loads(line) for line in Path("/tmp/company-brain-fireflies-records.jsonl").read_text().splitlines()]
if summary["count"] != 1 or len(records) != 1:
    raise SystemExit(f"unexpected Fireflies export output: {summary}, {records}")
record = records[0]
if record["external_id"] != "meeting-123" or record["artifact_type"] != "meeting_summary":
    raise SystemExit(f"unexpected normalized Fireflies record: {record}")
if "Prepare checklist" not in record["summary"]:
    raise SystemExit(f"Fireflies summary fields were not normalized: {record}")
if record.get("raw_format") != "md":
    raise SystemExit(f"Fireflies raw evidence should be markdown: {record}")
raw_body = record.get("raw_body", "")
for expected in ("# Raw Fireflies Transcript: Project Weekly Sync", "## Meeting Metadata", "## Transcript", "### 00:00", "**Operator:** We need the launch checklist ready."):
    if expected not in raw_body:
        raise SystemExit(f"Fireflies raw transcript is not readable: missing {expected!r}")
PY

REPO_FIXTURE="$TMP_ROOT/repo-fixture"
mkdir -p "$REPO_FIXTURE/src"
git -C "$REPO_FIXTURE" init >/tmp/company-brain-repo-fixture-git.txt
cat >"$REPO_FIXTURE/README.md" <<'EOF'
# Repo Fixture
EOF
cat >"$REPO_FIXTURE/package.json" <<'EOF'
{"dependencies":{"@nestjs/core":"latest","react":"latest"}}
EOF

python3 "$BIN_DIR/repo-map-export.py" \
  --repo "$REPO_FIXTURE" \
  --output-jsonl /tmp/company-brain-repo-map-records.jsonl >/tmp/company-brain-repo-map-export.json

python3 - <<'PY'
import json
from pathlib import Path

summary = json.loads(Path("/tmp/company-brain-repo-map-export.json").read_text())
records = [json.loads(line) for line in Path("/tmp/company-brain-repo-map-records.jsonl").read_text().splitlines()]
if summary["count"] != 1 or len(records) != 1:
    raise SystemExit(f"unexpected repo map export output: {summary}, {records}")
record = records[0]
if record["artifact_type"] != "repo_map":
    raise SystemExit(f"unexpected normalized repo map record: {record}")
if "nestjs" not in record["tags"] or "react" not in record["tags"]:
    raise SystemExit(f"repo stack markers were not normalized: {record}")
PY

cat >/tmp/company-brain-source-records.jsonl <<'EOF'
{"external_id":"source-doc-1","title":"Source Sync Smoke","summary":"This normalized source record should stage into the brain review queue.","target_path":"brain/sources/source-sync-smoke.md","tags":["source","smoke"],"artifact_type":"curated_note","visibility":"team","author":"Smoke Source","cursor":"smoke-cursor-1"}
{"external_id":"private-source-1","title":"Private Source","summary":"This private record should be skipped.","target_path":"brain/sources/private.md","tags":["source","private"],"artifact_type":"curated_note","visibility":"personal","author":"Smoke Source"}
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
state = json.loads(Path(os.environ["SCAFFOLD_ROOT"], "system", "source-sync-state.json").read_text())
cursor = state["sources"]["acme-co-brain-root"].get("cursor")
if cursor != "smoke-cursor-1":
    raise SystemExit(f"expected cursor smoke-cursor-1, got {cursor!r}")
PY

test -f "$SCAFFOLD_ROOT/system/staging/evidence/acme-co-brain-root.jsonl"
test -f "$SCAFFOLD_ROOT/system/staging/proposed/acme-co-brain-root-source-doc-1.md"

SCAFFOLD_ROOT="$SCAFFOLD_ROOT" python3 - <<'PY'
from pathlib import Path
import os

path = Path(os.environ["SCAFFOLD_ROOT"], "system", "source-registry.yml")
source = """
  - id: raw-smoke-source
    connector: manual
    display_name: Raw Smoke Source
    control_tier: company_owned
    status: approved_staging_only
    credential_ref: manual:none
    owner: smoke-reviewer
    review_owner: smoke-reviewer
    capture:
      allowed: true
      mode: manual
      approval_required: true
      raw_retention_days: 14
    scope:
      include:
        - smoke raw fixture
      exclude:
        - secrets
        - personal material
    raw_policy:
      store_raw: private_only
      retention_days: 14
    routing:
      default_destination: brain/sources/raw-smoke
      staging_destination: system/staging
      restricted_prefixes:
        - brain/restricted
    artifact_policy:
      allowed:
        - curated_note
      not_allowed:
        - credential_value
    dedupe:
      external_id_field: external_id
      strategy: source_id_plus_external_id
    sync:
      enabled: true
      cursor: null
      last_successful_pull: null
    audit:
      last_reviewed: 2026-06-18
      approved_by: smoke-reviewer
"""
text = path.read_text()
path.write_text(text.replace("\nrules:\n", source + "\nrules:\n"))
PY

cat >/tmp/company-brain-raw-source-records.jsonl <<'EOF'
{"external_id":"raw-doc-1","title":"Raw Smoke Doc","summary":"Normalized summary for extraction.","raw_body":"# Raw Smoke Doc\n\nThis raw material is private evidence only.","raw_format":"md","target_path":"brain/sources/raw-smoke/raw-doc-1.md","tags":["source","raw-smoke"],"artifact_type":"curated_note","visibility":"team","author":"Smoke Source","cursor":"raw-cursor-1"}
EOF

python3 "$BIN_DIR/source-registry-check.py" \
  --root "$SCAFFOLD_ROOT" \
  --source-id raw-smoke-source \
  --for-capture >/tmp/company-brain-raw-source-check.json

python3 "$BIN_DIR/source-pull.py" \
  --root "$SCAFFOLD_ROOT" \
  --source-id raw-smoke-source \
  --input-jsonl /tmp/company-brain-raw-source-records.jsonl \
  --cursor raw-cursor-1 \
  --write >/tmp/company-brain-raw-source-pull.json

python3 "$BIN_DIR/source-extract.py" \
  --root "$SCAFFOLD_ROOT" \
  --source-id raw-smoke-source \
  --write >/tmp/company-brain-raw-source-extract.json

SCAFFOLD_ROOT="$SCAFFOLD_ROOT" python3 - <<'PY'
import json
import os
from pathlib import Path

root = Path(os.environ["SCAFFOLD_ROOT"])
pull = json.loads(Path("/tmp/company-brain-raw-source-pull.json").read_text())
if pull["accepted"] != 1 or pull["raw_stored"] != 1:
    raise SystemExit(f"expected one raw sidecar: {pull}")
raw_path = root / "system" / "staging" / "raw" / "raw-smoke-source" / "raw-doc-1.md"
if not raw_path.is_file():
    raise SystemExit(f"missing raw sidecar: {raw_path}")
evidence = [json.loads(line) for line in (root / "system" / "staging" / "evidence" / "raw-smoke-source.jsonl").read_text().splitlines()]
if evidence[0].get("raw_evidence_path") != "system/staging/raw/raw-smoke-source/raw-doc-1.md":
    raise SystemExit(f"raw evidence path missing from normalized evidence: {evidence}")
proposal = (root / "system" / "staging" / "proposed" / "raw-smoke-source-raw-doc-1.md").read_text()
if "Private raw evidence:" not in proposal:
    raise SystemExit("staged proposal did not reference private raw evidence")
PY

cat >/tmp/company-brain-source-records-update.jsonl <<'EOF'
{"external_id":"source-doc-1","title":"Source Sync Smoke","summary":"This is the latest normalized source record and should replace the older staged proposal.","target_path":"brain/sources/source-sync-smoke.md","tags":["source","smoke"],"artifact_type":"curated_note","visibility":"team","author":"Smoke Source","cursor":"smoke-cursor-2"}
EOF

python3 "$BIN_DIR/source-pull.py" \
  --root "$SCAFFOLD_ROOT" \
  --source-id acme-co-brain-root \
  --input-jsonl /tmp/company-brain-source-records-update.jsonl \
  --cursor smoke-cursor-2 \
  --write >/tmp/company-brain-source-pull-update.json

python3 "$BIN_DIR/source-extract.py" \
  --root "$SCAFFOLD_ROOT" \
  --source-id acme-co-brain-root \
  --overwrite \
  --write >/tmp/company-brain-source-extract-update.json

SCAFFOLD_ROOT="$SCAFFOLD_ROOT" python3 - <<'PY'
import json
import os
from pathlib import Path

result = json.loads(Path("/tmp/company-brain-source-extract-update.json").read_text())
if len(result["staged"]) != 1:
    raise SystemExit(f"expected latest evidence to stage once: {result}")
proposal = Path(
    os.environ["SCAFFOLD_ROOT"],
    "system",
    "staging",
    "proposed",
    "acme-co-brain-root-source-doc-1.md",
).read_text()
if "latest normalized source record" not in proposal:
    raise SystemExit("latest source evidence did not replace the staged proposal")
state = json.loads(Path(os.environ["SCAFFOLD_ROOT"], "system", "source-sync-state.json").read_text())
cursor = state["sources"]["acme-co-brain-root"].get("cursor")
if cursor != "smoke-cursor-2":
    raise SystemExit(f"expected cursor smoke-cursor-2, got {cursor!r}")
PY

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

test -f "$SCAFFOLD_ROOT/system/schedule.md"

python3 "$BIN_DIR/brain-lint.py" --root "$SCAFFOLD_ROOT" >/tmp/company-brain-lint.txt

echo "smoke test passed"
