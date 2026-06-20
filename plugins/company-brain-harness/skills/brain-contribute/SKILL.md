---
name: brain-contribute
description: Help a Team Member contribute knowledge safely through a short guided interview or simple drop-zone flow. Use when the user says I want to add what I know, document my role, share my process, add an SOP, update stale facts, suggest team sources, I added a file, or tell the brain about my work.
---

# Brain Contribute

Make contribution easy for a teammate. Do not require them to understand the harness.

## Teammate Promise

```text
Answer a few questions.
Or drop a file in ADD_TO_BRAIN.
The agent handles routing, review flags, and next steps.
```

## Workflow

1. Resolve the brain root.
2. Ask the teammate's name and role.
3. Ask what people ask them about repeatedly.
4. Ask what docs/SOPs/projects they own.
5. Ask what tools they use and whether each is company-owned, shared, customer-owned, or personal.
6. Ask what should stay private or restricted.
7. Summarize the proposed contribution.
8. If `ADD_TO_BRAIN/` exists and the teammate has a file, point them there.
9. Stage only with `stage-brain-note.py --write` after the teammate agrees, unless `simple-team` policy allows low-risk manual processing.

## Questions

Ask one at a time:

- What is your role?
- What decisions or workflows do you own?
- What should the company brain know about your area?
- What is stale or wrong today?
- Which source systems do you use?
- Which sources are company/shared and which are personal?
- Who should review notes from your area?
- What should stay out or go to `brain/restricted/`?

## Output Shape

```text
Proposed contribution:
- destination:
- reviewer:
- sensitive material:
- open questions:

Next action:
- preview / stage / revise
```

## Guardrails

- Do not store personal/private material in the shared brain.
- Do not register a personal account as a company source.
- Do not invent answers when the teammate is unsure.
- Prefer small staged notes over one large mixed note.
- Do not make a teammate learn source registry or CLI details before they can contribute.
