---
name: brain-operator
description: Run the daily operator loop for a Company Brain. Use when the user says run today's brain check, do the morning review, check the queue, what needs review, show blockers, check sources, run maintenance, process the ADD_TO_BRAIN folder, I added something to the company brain folder, or give me the next actions.
---

# Brain Operator

Run the operating loop and explain results in plain language. The operator can be a person, consultant, or AI agent.

## Daily Loop

1. Resolve the brain root.
2. Run connection check.
3. Run source registry check.
4. Run brain health.
5. Run brain lint.
6. If `ADD_TO_BRAIN/` exists, run the drop-zone digest.
7. Inspect the staged proposal queue and flagged digest items.
8. Produce a punch list.

## Command Pattern

Run internally:

```bash
python3 <plugin-root>/bin/connections-check.py --root "$BRAIN_ROOT"
python3 <plugin-root>/bin/source-registry-check.py --root "$BRAIN_ROOT"
python3 <plugin-root>/bin/brain-health.py --root "$BRAIN_ROOT"
python3 <plugin-root>/bin/brain-lint.py --root "$BRAIN_ROOT" --stale-days 30
python3 <plugin-root>/bin/add-to-brain-digest.py --root "$BRAIN_ROOT" --write
```

Run `add-to-brain-digest.py` only when the brain root contains `ADD_TO_BRAIN/`
or `company-brain.yml` uses `operating_profile: simple-team`.

## Output Shape

```text
Today's brain check: Ready / Needs review / Blocked

Needs review:
- staged notes:
- proposed sources:
- stale notes:
- broken links:

Next three actions:
1.
2.
3.
```

## Weekly Loop

- review stale notes
- review source ownership
- review restricted access
- review schedule and auto-promotion rules
- review simple-team digest automation and flagged drop-zone files
- invite missing teammates

## Guardrails

- In the default governed profile, do not promote staged notes without explicit approval.
- In `simple-team`, low-risk manual drop-zone contributions may be processed when policy allows it.
- Do not auto-enable proposed sources.
- Do not treat the drop zone as permission to ingest broad personal source exports.
- Do not inspect restricted folders.
- Treat warnings as review tasks, not proof that the brain is wrong.
