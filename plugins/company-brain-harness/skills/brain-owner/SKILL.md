---
name: brain-owner
description: Guide the Brain Owner, founder, admin, or team lead through setup and approval decisions. Use when the user says I own this brain, I want to launch the company brain, approve policy, approve sources, choose the operator, invite the team, decide restricted access, or check pilot readiness.
---

# Brain Owner

Help the person accountable for the company brain make the minimum decisions needed to start safely.

## Owner Responsibilities

- choose the brain root location
- approve the capture policy
- approve or reject source instances
- decide restricted folder access
- name the operator
- approve the first operating schedule
- decide when the pilot is ready for teammates

## Setup Flow

1. Ask for the company name.
2. Ask where the brain should live.
3. Ask who should be the Brain Operator.
4. Preview setup with `brain-setup.py`.
5. If the user asks to proceed, run setup with `--write`.
6. Run readiness checks.
7. Walk the owner through the first three approvals:
   - capture policy
   - restricted folder access
   - source registry defaults
8. Produce a short launch checklist.

## Plain-Language Output

Use this shape:

```text
Brain setup status: Ready / Needs review / Blocked

Owner decisions:
- ...

Next action:
- ...
```

## What Not To Ask First

Do not begin with connector details. The owner needs the brain root and safety rules first.

Do not ask for credentials in chat. Ask for credential references only.

## Guardrails

- Personal accounts are excluded by default.
- Shared company accounts can be proposed, not silently activated.
- Meeting, HR, legal, finance, and strategy-changing notes stay human-approved during the pilot.
- Restricted access is a permission decision, not just a folder name.
