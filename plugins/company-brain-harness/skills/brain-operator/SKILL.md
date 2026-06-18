---
name: brain-operator
description: Run the simple operating loop for a Company Brain. Use when the user asks for today's brain check, morning review, staging queue, source warnings, health, lint, or operational next actions.
---

# Brain Operator

Run the operating loop and explain results in plain language. The operator can be a person, consultant, or AI agent.

## Daily Loop

1. Resolve the brain root.
2. Run connection check.
3. Run source registry check.
4. Run brain health.
5. Run brain lint.
6. Inspect the staged proposal queue.
7. Produce a punch list.

## Command Pattern

Run internally:

```bash
python3 <plugin-root>/bin/connections-check.py --root "$BRAIN_ROOT"
python3 <plugin-root>/bin/source-registry-check.py --root "$BRAIN_ROOT"
python3 <plugin-root>/bin/brain-health.py --root "$BRAIN_ROOT"
python3 <plugin-root>/bin/brain-lint.py --root "$BRAIN_ROOT" --stale-days 30
```

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
- invite missing teammates

## Guardrails

- Do not promote staged notes without explicit approval.
- Do not auto-enable proposed sources.
- Do not inspect restricted folders.
- Treat warnings as review tasks, not proof that the brain is wrong.
