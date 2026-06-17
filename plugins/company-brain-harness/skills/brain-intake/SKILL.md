---
name: brain-intake
description: Stage a document, link, pasted text, transcript, or raw artifact into the company brain review flow. Use when the user wants to add knowledge, file a note, ingest a doc, sort where something belongs, or convert raw material into a staged company-brain proposal.
---

# Brain Intake

Turn raw material into a staged proposal. Do not write directly to final knowledge folders.

## Workflow

1. Resolve the brain root.
2. Read the configured routing file, folder indexes, `CAPTURE_POLICY.md`, and `HARNESS_FLOWS.md` if present.
3. Classify the input:
   - company knowledge
   - personal/private
   - sensitive company material
   - unknown
4. Refuse to stage personal/private material into a shared brain. For unknown material, stage only after marking it for review.
5. Choose a target path under the appropriate knowledge folder. Never target the restricted vault unless the user is explicitly authorized and the policy allows it.
6. Draft a concise markdown note with:
   - title
   - summary
   - decisions/facts
   - open questions
   - source/provenance
7. Stage with `stage-brain-note.py`, including target path, at least two tags, `source-type`, `source-ref`, and `author`.
8. Return the staged proposal id and what a reviewer should check.

## Command Pattern

```bash
python3 <plugin-root>/bin/stage-brain-note.py \
  --root "$BRAIN_ROOT" \
  --target "02_Strategy/example.md" \
  --tag strategy --tag source-note \
  --source-type manual \
  --source-ref "<source reference>" \
  --author "<person>" \
  --id "<optional-id>"
```

Pipe the proposed markdown note on stdin.
