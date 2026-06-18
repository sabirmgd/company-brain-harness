---
name: brain-lint
description: Run read-only maintenance lint for stale knowledge, missing provenance, duplicate notes, dead links, and possible contradictions. Use when the user says what is outdated, find stale notes, check broken links, find contradictions, cleanup the brain, or can we rely on this.
---

# Brain Lint

Inspect the brain without modifying it. This protects team trust as knowledge changes over time.

## Workflow

1. Resolve the brain root.
2. Run `brain-lint.py` with the agreed stale window.
3. Do not inspect restricted prefixes.
4. Summarize issues by severity: missing provenance, stale notes, broken links, duplicates, possible contradictions.
5. Recommend whether to update, archive, delete, or ask the source owner.
6. Do not invent fixes for stale knowledge. Route corrections to the owner or stage a revision.

## Command Pattern

```bash
python3 <plugin-root>/bin/brain-lint.py \
  --root "$BRAIN_ROOT" \
  --stale-days 30
```

## What It Checks

- content notes missing frontmatter
- notes missing provenance comments
- stale or undated `last_verified` fields
- dead markdown and wiki links
- duplicate note names
- notes that mention stale, superseded, or contradictory information

## Guardrails

- Read-only by design.
- Restricted folders are skipped.
- A lint warning is not proof that the note is wrong; it is a review task.
- Freshness belongs to the team. The source owner should verify high-impact updates.
