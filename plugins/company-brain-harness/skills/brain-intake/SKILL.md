---
name: brain-intake
description: Stage or process one document, link, pasted text, transcript, note, or raw artifact into the company brain flow. Use when the user says add this to the brain, ingest this doc, file this note, where should this go, turn this into a brain note, add this document from ADD_TO_BRAIN, or stage this for review.
---

# Brain Intake

Turn raw material into a staged proposal. Do not write directly to final knowledge folders.

## Workflow

1. Resolve the brain root.
2. Read the configured routing file, folder indexes, `capture-policy.md`, `flows.md`, and `source-registry.yml` if present.
3. Classify the input:
   - company knowledge
   - personal/private
   - sensitive company material
   - team-owned source material
   - unknown
4. Refuse to stage personal/private material into a shared brain. For unknown material, stage only after marking it for review.
5. If the material comes from a connector, identify the exact source instance. Do not accept "Fireflies", "Apollo", "Gmail", or "Slack" as a source by itself.
6. Choose a target path under the appropriate knowledge folder. Never target the restricted folder unless the user is explicitly authorized and the policy allows it.
7. Draft a concise markdown note with:
   - title
   - summary
   - decisions/facts
   - open questions
   - source/provenance
8. If the brain uses `simple-team` and the artifact is a low-risk manual contribution from `ADD_TO_BRAIN/`, process it according to `company-brain.yml`; otherwise stage it for review.
9. Preview with `stage-brain-note.py` when staging. Add `--write` only when the user explicitly wants a staged proposal created.
10. Return the staged proposal id or processed note path, plus what was checked.

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

Pipe the proposed markdown note on stdin. This previews by default. Add `--write` to persist under the staging folder.

For `simple-team`, dropped files live under `ADD_TO_BRAIN/`. Use the digest
first when processing a batch:

```bash
python3 <plugin-root>/bin/add-to-brain-digest.py --root "$BRAIN_ROOT" --write
```

## Team Source Prompts

When a teammate provides source material, ask:

- Is this from a company/shared source, customer source, delegated personal source, or private personal source?
- What exact account/workspace/channel/folder/item is the source?
- Who owns this source?
- Who should review the staged note?
- Should any part route to `brain/restricted/` or stay out?

## Simple-Team Rule

Do not make team members understand staging folders. If they dropped a safe
file into `ADD_TO_BRAIN/`, classify it, preserve provenance, and either process
it as a low-risk manual contribution or flag it for review. Personal/private,
credential-like, HR, legal, finance, customer-confidential, or unclear material
must not be silently promoted.
