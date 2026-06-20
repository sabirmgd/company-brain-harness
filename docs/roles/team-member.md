# Team Member

Team Members make the brain useful by contributing what they know.

## What To Say

```text
I want to add what I know to the company brain.
```

or:

```text
$brain-contribute
```

## What The Agent Will Ask

- What is your role?
- What decisions or workflows do you own?
- What should the company brain know about your area?
- What is stale or wrong today?
- Which source systems do you use?
- Which sources are company/shared and which are personal?
- Who should review notes from your area?
- What should stay out or go to `brain/restricted/`?

## What Happens Next

In the governed profile, the agent drafts a staged proposal. A reviewer
approves, rejects, or asks for a revision before anything becomes shared
knowledge.

In `simple-team`, you can also add safe files to `ADD_TO_BRAIN/`. The operator
digest processes low-risk company material and flags anything sensitive or
unclear.

## Guardrails

- Do not add private personal material.
- Do not paste secrets.
- Do not assume personal app accounts are company sources.
- Do not add personal, HR, legal, finance, or credential material to
  `ADD_TO_BRAIN/`.
- When unsure, mark the answer as an open question.
