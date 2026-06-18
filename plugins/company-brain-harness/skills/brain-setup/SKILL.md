---
name: brain-setup
description: Scaffold a new team-first Company Brain root without populating company data. Use when setting up a brain for a new company, creating the routing/config/policy/source-registry/staging structure, or making setup easy for Claude and Codex users.
---

# Brain Setup

Create the reusable Company Brain structure. Do not populate strategy, customer, employee, project, or private company data during setup.

## Workflow

1. Choose the filesystem-backed root: Google Drive, git repo, shared volume, or local folder.
2. Identify the Champion and Operator.
3. Preview the scaffold with `brain-setup.py` before writing.
4. Write only when the user explicitly wants the scaffold created.
5. Run `source-registry-check.py`, `brain-health.py`, and `brain-lint.py` after setup.
6. End with the population checklist for Scott/team members, not with invented content.

## Command Pattern

Preview:

```bash
python3 <plugin-root>/bin/brain-setup.py \
  --root "$BRAIN_ROOT" \
  --company-name "<Company Name>" \
  --champion "<Champion Name>" \
  --operator "<Operator Name>"
```

Write:

```bash
python3 <plugin-root>/bin/brain-setup.py \
  --root "$BRAIN_ROOT" \
  --company-name "<Company Name>" \
  --champion "<Champion Name>" \
  --operator "<Operator Name>" \
  --write
```

## Team Setup Questions

Ask only what is needed to scaffold safely:

- company name
- brain root location
- Champion for policy and approvals
- Operator for daily checks
- first teammates to onboard
- which shared source systems exist
- which systems are personal and excluded
- whether the first two weeks should be human-gated or autonomous staging only

## Guardrails

- Setup creates structure, policy, registry, schedule, and staging.
- Teammates populate actual company knowledge later.
- Personal Gmail, Calendar, Fireflies, Apollo, or other personal accounts are excluded by default.
- Shared Apollo/CRM/workspace accounts can be registered as company sources, but only after source review.
- `Restricted/` exists as a routing destination, not as permission proof. The owner must still set filesystem permissions.
