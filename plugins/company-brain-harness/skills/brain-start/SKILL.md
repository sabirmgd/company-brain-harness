---
name: brain-start
description: Front door for plain-English Company Brain requests when the user's role or next step is unclear. Use when the user says I want to set up my company brain, help me start, I want to use the brain, what should I do next, create a company brain, operate the brain, or add knowledge but the right role is not clear.
---

# Brain Start

Be the front door. Hide the harness internals unless the user asks. Do not start by listing CLIs.

## User Promise

The user should feel like this:

```text
I say what I want.
The agent asks a few simple questions.
The agent runs the harness safely in the background.
I review the next action.
```

## Workflow

1. Resolve whether a brain root already exists.
2. Ask one question: "Are you setting this up, operating it, or contributing knowledge?"
3. Route by role:
   - setup/owner -> use `brain-owner`
   - daily checks/maintenance -> use `brain-operator`
   - teammate contribution -> use `brain-contribute`
4. If the user is unsure, default to owner setup.
5. Explain only the next step, not the whole system.
6. Run lower-level skills or CLIs internally as needed.
7. End with one clear next action.

## Runtime Assumption

This skill is normally loaded from an installed plugin bundle. The bundle
already includes `skills/`, `bin/`, and `references/`.

- Do not tell a normal user to download individual skills.
- Do not tell a normal user to clone the harness repo unless they are doing
  local development or auditing the package.
- When a script is needed, resolve it from the installed plugin root's `bin/`
  directory.
- Treat the company brain root as customer data, separate from the installed
  harness plugin.

## Role Names

Use these public names:

- Brain Owner: approves policy, sources, restricted access, and launch readiness.
- Brain Operator: runs daily checks, reviews queue, and keeps the brain healthy.
- Team Member: contributes role knowledge and flags stale or private material.

Do not lead with internal role labels, source-owner, registry, or CLI language unless the user is technical or asks.

## First Questions

Ask these progressively, one at a time:

1. "Are you creating a new company brain or using an existing one?"
2. "Where should the brain live?"
3. "Are you the Brain Owner, Brain Operator, or a Team Member?"
4. "Do you want the 20-minute starter setup or the team pilot setup?"
5. For setup: "Do you want the governed review model or the simpler team drop-zone model?"

## Background Actions

When needed, run:

```bash
python3 <plugin-root>/bin/brain-setup.py ...
python3 <plugin-root>/bin/connections-check.py ...
python3 <plugin-root>/bin/source-registry-check.py ...
python3 <plugin-root>/bin/brain-health.py ...
python3 <plugin-root>/bin/brain-lint.py ...
python3 <plugin-root>/bin/brain-schedule.py ...
python3 <plugin-root>/bin/add-to-brain-digest.py ...
```

Show results as plain-language status:

- Ready
- Needs review
- Blocked
- Next action

## Guardrails

- Setup and schedule commands preview first unless the user explicitly asks to create/update files.
- Do not populate company facts during setup.
- Use `--operating-profile simple-team` only when the owner wants a shared drop zone and digest automation.
- Do not connect personal accounts as company sources.
- Do not promote governed-profile, sensitive, or unclear notes without approval.
- Do not inspect restricted folders.
