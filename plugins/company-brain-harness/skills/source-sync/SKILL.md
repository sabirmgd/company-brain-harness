---
name: source-sync
description: Run source-governed capture from approved source instances into private evidence and staged brain proposals. Use when the user says sync sources, pull new emails, pull Slack updates, pull Confluence pages, sync CRM changes, process approved sources, update from source data, run source capture, or stage new source updates.
---

# Source Sync

Run approved source capture without leaking raw private material into the shared brain.

## Pipeline

```text
approved source -> scoped pull -> private evidence -> extraction -> staged proposal -> review -> approved brain note
```

## Workflow

1. Resolve the brain root.
2. Validate the exact source instance with `source-registry-check.py --for-capture`.
3. Read `source-sync-state.json` for cursor and dedupe state.
4. Pull only new or changed items from the approved source scope.
5. Normalize records into JSONL for `source-pull.py`.
6. Let `source-pull.py` privacy-filter, dedupe, and store evidence.
7. Let `source-extract.py` create staged proposals from allowed artifact types.
8. Report accepted, skipped, unchanged, staged, and blocked counts.
9. Never promote final notes from this skill unless the user explicitly routes to approval.

## Generic Script Pattern

```bash
python3 <plugin-root>/bin/source-pull.py \
  --root "$BRAIN_ROOT" \
  --source-id "<source-id>" \
  --input-jsonl "<normalized-records.jsonl>" \
  --cursor "<next-cursor>" \
  --write

python3 <plugin-root>/bin/source-extract.py \
  --root "$BRAIN_ROOT" \
  --source-id "<source-id>" \
  --write
```

Connector adapters should produce normalized JSONL. The harness owns policy,
privacy, state, extraction, and staging.

## Guardrails

- Refuse personal/private visibility by default.
- Refuse restricted visibility unless a restricted workflow is explicit.
- Refuse records that look like secrets.
- Respect `artifact_policy.allowed` and `artifact_policy.not_allowed`.
- Respect source cursor and content hash dedupe.
- Stage only; approval is separate.
