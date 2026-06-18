---
name: brain-schedule
description: Create or update the Company Brain operating schedule for human-gated or autonomous runs. Use when the user says schedule the brain check, set the morning review, automate daily checks, run without a human, keep human in the loop, set cron, or define auto-capture guardrails.
---

# Brain Schedule

Generate the operating schedule. The schedule is about checks, staging, review, and maintenance; it is not a data-population shortcut.

## Workflow

1. Resolve the brain root.
2. Choose `human` mode for the first two weeks unless the user explicitly asks for autonomous mode.
3. Preview `SCHEDULE.md`.
4. Write only with explicit permission or when the user asked to update the schedule.
5. Include daily checks: connections, sources, health, lint, staged queue, and punch list.
6. State what can run unattended and what always needs human approval.

## Command Pattern

Preview:

```bash
python3 <plugin-root>/bin/brain-schedule.py \
  --root "$BRAIN_ROOT" \
  --mode human \
  --time 08:30 \
  --timezone local \
  --champion "<Brain Owner>" \
  --operator "<Brain Operator>"
```

Write:

```bash
python3 <plugin-root>/bin/brain-schedule.py \
  --root "$BRAIN_ROOT" \
  --mode human \
  --time 08:30 \
  --timezone local \
  --champion "<Brain Owner>" \
  --operator "<Brain Operator>" \
  --write
```

## Modes

- `human`: checks and staging can run, promotion requires explicit human approve/reject/revise.
- `autonomous`: approved sources may stage proposals unattended; auto-promotion is only for explicit low-risk categories.

## Guardrails

- Meeting-derived, HR, legal, finance, customer-confidential, and strategy-changing notes stay human-approved.
- Personal connectors never run as scheduled company-brain sources.
- Source registry and lint must run before scheduled capture is trusted.
- The schedule should name a Brain Owner and a Brain Operator, not depend on one hidden local machine.
