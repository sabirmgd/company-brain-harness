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
- Smoke test passes against a non-HeyFlora brain root.
- GitHub Actions validation is green.

## Missing Before Broad Reuse

- Config wizard that creates `company-brain.yml`, `CLAUDE.md`, conventions docs,
  capture policy, harness flows, and staging folders for a new company.
- Connector adapters for company-controlled sources:
  - Google Workspace via `gws`
  - Fireflies company workspace
  - GitHub org repo index
  - Slack later
- Source registry validator/enforcer that refuses unapproved or personal source
  instances before connector jobs run.
- Scheduled runner that stages proposals and produces a morning review digest.
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

1. Dogfood with HeyFlora.
2. Turn repeated setup into a new-company wizard.
3. Turn health score into an onboarding progress metric.
4. Turn capture policy into a customer-facing trust primitive.
5. Publish a stable plugin marketplace release.
6. Add connector adapters only after the policy and staging path are proven.
