---
name: meeting-to-brain
description: Convert a company-approved meeting transcript, recap, or recording export into staged company-brain notes with decisions, action items, and reusable knowledge. Use for Fireflies or meeting material only when the source is company-controlled or explicitly approved by capture policy.
---

# Meeting To Brain

Convert approved meeting material into staged knowledge. Never bulk-ingest personal meetings.

## Workflow

1. Read `CAPTURE_POLICY.md` and `source-registry.yml` before using any meeting source.
2. Verify the exact meeting source instance with `source-registry-check.py --source-id <id> --for-capture`.
3. If it is a personal Fireflies, Calendar, Gmail, Zoom, or meeting recorder account, stop unless it is explicitly delegated, scoped, approved, and registered.
4. Extract only useful company knowledge:
   - decisions
   - action items
   - customer facts
   - product/architecture facts
   - open questions
   - follow-up owners
5. Split outputs by destination folder when the meeting covers multiple domains.
6. Stage each note with `source-type=meeting` and a source reference that can be audited later.
7. Do not place raw transcripts in the shared brain unless policy explicitly allows it. Curated notes are the default shared artifact.

## Source Check

```bash
python3 <plugin-root>/bin/source-registry-check.py \
  --root "$BRAIN_ROOT" \
  --source-id "<meeting-source-id>" \
  --for-capture
```

## Output Shape

Use concise markdown:

```markdown
# <Meeting Topic>

## Summary

## Decisions

## Action Items

## Knowledge To Reuse

## Open Questions

## Provenance
```
