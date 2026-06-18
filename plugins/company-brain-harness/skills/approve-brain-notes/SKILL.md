---
name: approve-brain-notes
description: Review staged company-brain proposals and approve, reject, or request revision through the approval ledger. Use when the user asks to review staged notes, promote approved notes, clear the staging queue, or inspect pending brain proposals.
---

# Approve Brain Notes

Review staged proposals and record an approval decision. Shared-brain writes require an explicit decision.

## Workflow

1. Resolve the brain root.
2. List staged proposals from the configured staging directory. Default:
   `00_README_Drive_Conventions/90_Staging/proposed/*.md`.
3. For each proposal, inspect metadata, target path, sensitivity, author, source id/reference, and content summary.
4. If a proposal came from a connector, confirm the source exists in `source-registry.yml` before approving.
5. Do not inspect restricted folder contents.
6. Recommend one decision:
   - approve
   - reject
   - revise
7. Preview the command first unless the user explicitly requested execution.
8. Execute with `approve-staged-note.py --write` only after an explicit approval instruction.
9. Report the ledger entry, target path, and any remaining queue.

## Command Pattern

```bash
python3 <plugin-root>/bin/approve-staged-note.py \
  --root "$BRAIN_ROOT" \
  --id "<proposal-id>" \
  --decision approve \
  --reviewer "<person>" \
  --write
```

For reject or revise, include `--note`.
