---
name: meeting-to-brain
description: Convert a company-approved meeting transcript, recap, or recording export into staged company-brain notes with decisions, action items, and reusable knowledge. Use for Fireflies or meeting material only when the source is company-controlled or explicitly approved by capture policy.
---

# Meeting To Brain

Convert approved meeting material into staged knowledge. Never bulk-ingest personal meetings.

## Workflow

1. Read `CAPTURE_POLICY.md` before using any meeting source.
2. Verify the source is company-controlled or explicitly approved. If it is a personal Fireflies account/key, stop and explain the risk.
3. Extract only useful company knowledge:
   - decisions
   - action items
   - customer facts
   - product/architecture facts
   - open questions
   - follow-up owners
4. Split outputs by destination folder when the meeting covers multiple domains.
5. Stage each note with `source-type=meeting` and a source reference that can be audited later.
6. Do not place raw transcripts in the shared brain unless policy explicitly allows it. Curated notes are the default shared artifact.

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
