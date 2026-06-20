---
name: brain-setup
description: Scaffold a new team-first Company Brain root without populating company data. Use when the user asks to create the brain files, generate the scaffold, initialize a brain root, create routing, create config, create policy, create source registry, or run the setup step after owner guidance.
---

# Brain Setup

Create the reusable Company Brain structure. Do not populate strategy, customer, employee, project, or private company data during setup.

## Workflow

1. Choose the filesystem-backed root: Google Drive, git repo, shared volume, or local folder.
2. Identify the Brain Owner and Brain Operator.
3. Preview the scaffold with `brain-setup.py` before writing.
4. Write only when the user explicitly wants the scaffold created.
5. Run `source-registry-check.py`, `brain-health.py`, and `brain-lint.py` after setup.
6. End with the population checklist for team members, not with invented content.

## Package Boundary

Setup writes the brain root. It does not copy the harness code into the brain.
The installed plugin already contains the skills, scripts, and references.

The created brain root should contain customer-owned files such as `CLAUDE.md`,
`company-brain.yml`, `brain/`, and `system/`.

## Command Pattern

Preview:

```bash
python3 <plugin-root>/bin/brain-setup.py \
  --root "$BRAIN_ROOT" \
  --company-name "<Company Name>" \
  --champion "<Brain Owner Name>" \
  --operator "<Brain Operator Name>"
```

Write:

```bash
python3 <plugin-root>/bin/brain-setup.py \
  --root "$BRAIN_ROOT" \
  --company-name "<Company Name>" \
  --champion "<Brain Owner Name>" \
  --operator "<Brain Operator Name>" \
  --write
```

## Team Setup Questions

Ask only what is needed to scaffold safely:

- company name
- brain root location
- Brain Owner for policy and approvals
- Brain Operator for daily checks
- first teammates to onboard
- which shared source systems exist
- which systems are personal and excluded
- whether the first two weeks should be human-gated or autonomous staging only

## Guardrails

- Setup creates structure, policy, registry, schedule, and staging.
- Teammates populate actual company knowledge later.
- Personal Gmail, Calendar, Fireflies, Apollo, or other personal accounts are excluded by default.
- Shared Apollo/CRM/workspace accounts can be registered as company sources, but only after source review.
- `brain/restricted/` exists as a routing destination, not as permission proof. The owner must still set filesystem permissions.
