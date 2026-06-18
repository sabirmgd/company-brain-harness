# Pilot Readiness Checklist

Use this checklist before presenting a Company Brain Harness deployment to a
new company, founder, or team lead.

## What Is Ready

- Portable plugin package for Claude Code and Codex.
- Four role-based entry skills:
  - `brain-start`
  - `brain-owner`
  - `brain-operator`
  - `brain-contribute`
- Ten lower-level action skills:
  - `brain-setup`
  - `brain-health`
  - `sources-check`
  - `brain-intake`
  - `brain-onboard`
  - `meeting-to-brain`
  - `approve-brain-notes`
  - `brain-schedule`
  - `brain-lint`
  - `repo-aware-poc`
- Generic preview-first CLIs:
  - `brain-setup.py`
  - `connections-check.py`
  - `source-registry-check.py`
  - `brain-health.py`
  - `brain-lint.py`
  - `brain-schedule.py`
  - `stage-brain-note.py`
  - `approve-staged-note.py`
  - `promote-to-brain.py`
- Config-driven brain root support via `company-brain.yml` / `company-os.yml`.
- Policy guardrail: personal Fireflies/Gmail/Calendar/Apollo are not company
  capture sources.
- Team source registry: every org-wide app account/workspace/channel needs its
  own owner, scope, approval, and route.
- Smoke test proving the harness works against a synthetic generic brain shape.

## What The Company Owner Needs To Approve

- Capture policy for meetings, email, calendar, and shared business systems.
- Whether the company has a company-controlled meeting recorder workspace/key.
- Whether shared Apollo/CRM is an approved company source, and what it may stage.
- Whether the engine identity is a dedicated company account.
- Workspace admin approval for Google Workspace or equivalent service-account access.
- Restricted folder permissions, especially owner/legal/finance/HR material.
- Who reviews the morning staging queue for the first 2-3 weeks.

## What To Demo

1. Open Claude Code or Codex in the configured brain root.
2. Say: "I want to set up my company brain."
3. Show the role choice: Brain Owner, Brain Operator, Team Member.
4. Run the Brain Operator daily check.
5. Stage a small safe contribution with `brain-contribute`.
6. Approve it with `approve-brain-notes`.
7. Show the final note in the correct folder with provenance.
8. Show that a restricted-folder write is refused by default.
9. Show `repo-aware-poc` reading repo/stack guardrails before a prototype.

## What Not To Demo Yet

- Personal Fireflies capture.
- Broad automatic Gmail/Calendar ingestion.
- Personal Apollo/CRM capture.
- Raw transcript dumping into the shared brain.
- Anything in restricted folders unless the company owner explicitly grants and scopes it.

## First Production Pilot

For the first two weeks:

- Capture nothing automatically except explicitly approved company sources.
- Stage every note before promotion.
- Require human approval for every promoted note.
- Review `connections-check`, `sources-check`, `brain-health`, and `brain-lint`
  daily.
- Track missing docs as a punch list, not as failure.

After the pilot:

- Allow low-risk categories to auto-promote only if the staging queue has been
  clean for at least one week.
- Keep sensitive and meeting-derived material human-approved.
- Convert the process into the customer onboarding blueprint.
