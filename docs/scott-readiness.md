# Scott Readiness Checklist

This is the checklist before presenting the HeyFlora company brain harness to
Scott as something the team can start using.

## What Is Ready

- Portable plugin package for Claude Code and Codex.
- Six installable skills:
  - `brain-health`
  - `brain-intake`
  - `brain-onboard`
  - `meeting-to-brain`
  - `approve-brain-notes`
  - `repo-aware-poc`
- Generic preview-first CLIs:
  - `connections-check.py`
  - `brain-health.py`
  - `stage-brain-note.py`
  - `approve-staged-note.py`
  - `promote-to-brain.py`
- Config-driven brain root support via `company-brain.yml` / `company-os.yml`.
- Policy guardrail: personal Fireflies/Gmail/Calendar are not company capture
  sources.
- Smoke test proving the harness works against a non-HeyFlora brain shape.

## What Scott Needs To Approve

- Capture policy for meetings and email.
- Whether HeyFlora will create a company Fireflies workspace/key.
- Whether the engine identity is a dedicated account such as
  `flora-bot@heyflora.ai`.
- Workspace admin approval for Google Workspace CLI/service-account access.
- Restricted folder permissions, especially owner/legal/finance/HR material.
- Who reviews the morning staging queue for the first 2-3 weeks.

## What We Should Demo

1. Open `Company_Master` as the brain root.
2. Run connection check.
3. Run brain health.
4. Stage a small safe note with `brain-intake`.
5. Approve it with `approve-brain-notes`.
6. Show the final note in the correct folder with provenance.
7. Show that a restricted-folder write is refused by default.
8. Show `repo-aware-poc` reading repo/stack guardrails before a prototype.

## What Not To Demo Yet

- Personal Fireflies capture.
- Broad automatic Gmail/Calendar ingestion.
- Raw transcript dumping into the shared brain.
- Anything in restricted folders unless Scott explicitly grants and scopes it.

## First Production Pilot

For the first two weeks:

- Capture nothing automatically except explicitly approved company sources.
- Stage every note before promotion.
- Require human approval for every promoted note.
- Review `brain-health` and `connections-check` daily.
- Track missing docs as a punch list, not as failure.

After the pilot:

- Allow low-risk categories to auto-promote only if the staging queue has been
  clean for at least one week.
- Keep sensitive and meeting-derived material human-approved.
- Convert the process into the customer onboarding blueprint.
