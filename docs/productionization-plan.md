# Productionization Plan

The harness is intentionally small today: plugin manifests, skills, portable
CLIs, docs, and smoke tests. Productionization means making it safe to install
for more teams without hand-holding.

## Release Gate

Before each release:

```bash
bash scripts/validate.sh
```

Required proof:

- Python CLIs compile.
- Skill folders validate.
- Codex plugin manifest validates when the local Codex validator is available.
- Claude plugin and marketplace validate when the Claude CLI is available.
- Smoke test passes against a synthetic generic brain root.
- GitHub Actions validation is green.

## Built In The Current Harness

- Config scaffold that creates `company-brain.yml`, `CLAUDE.md`, conventions
  docs, capture policy, connections inventory, source registry, schedule, folder
  indexes, and staging folders for a new company.
- Source registry validator/enforcer that refuses unapproved or personal source
  instances before connector jobs run.
- Generic source-governed capture scripts for normalized connector output:
  `source-pull.py`, `source-extract.py`, and `source-sync-state.py`.
- Schedule generator for human-gated or autonomous operating loops.
- `simple-team` scaffold profile with `ADD_TO_BRAIN/` and
  `add-to-brain-digest.py` for low-friction manual contribution.
- Read-only lint for stale, duplicate, broken-link, contradiction, and
  provenance review.

## Missing Before Broad Reuse

- Connector adapters for company-controlled sources:
  - Google Workspace via `gws`
  - Fireflies company workspace
  - GitHub org repo index
  - shared Apollo/CRM workspace
  - Slack later
- Connector-specific normalizers that produce the generic JSONL record format.
- Managed runner recipe for cron, launchd, Claude/Codex scheduled tasks,
  Choreon-style jobs, or CI-based morning reviews.
- Clean service-account guide for Google Workspace domain-wide delegation.
- Example brain root fixtures for CI and docs.
- Versioned release tags and changelog.

## Design Rules

- Keep storage backend-neutral. Google Drive is only one root backend.
- Keep company-specific docs in deployment config, not harness code.
- Treat optional connectors as nudges, not failures.
- Treat personal connectors as personal, not company engine sources.
- Treat connector accounts/workspaces/channels as source instances. Multiple
  accounts are fine; unregistered accounts are not.
- Preview by default; require `--write` for side effects.
- Never index restricted prefixes by default.
- Prefer staged proposals over direct writes.

## Productization Path

1. Run a first pilot with one internal or customer brain.
2. Turn repeated setup into a new-company wizard.
3. Turn health score into an onboarding progress metric.
4. Turn capture policy into a customer-facing trust primitive.
5. Publish a stable plugin marketplace release.
6. Add connector adapters only after the policy and staging path are proven.
