---
name: brain-onboard
description: Run a guided interview that helps a brain owner or teammate fill the company brain safely. Use when setting up a new company brain, onboarding a teammate, collecting strategy/brand/customer/SOP context, or turning spoken answers into staged knowledge notes.
---

# Brain Onboard

Interview one person and stage structured notes. Do not directly fill final folders.

## Workflow

1. Resolve the brain root.
2. Read `team.yml`, `company-brain.yml`, `source-registry.yml`, folder indexes, and routing docs if present.
3. Identify the interview scope: company setup, role setup, customer context, SOP, brand, sales/GTM, engineering/repo, source inventory, or meeting capture.
4. Ask one question at a time. Keep questions concrete and short.
5. After 3-6 useful answers, summarize back the candidate note before staging.
6. Stage notes through `stage-brain-note.py --write` only when the user wants the proposal saved for review.
7. Attribute the note to the interviewee and the agent/operator who staged it.
8. End with what is still missing and which folder should be populated next.

## Team Member Prompts

Use these prompts to build a team brain without treating personal accounts as company sources:

- What is your role and what decisions do you own?
- What workflows do people ask you about repeatedly?
- Which company-owned or shared tools do you use?
- Which personal tools contain private material and should stay excluded?
- Is there a shared Apollo/CRM/meeting/calendar/workspace account the company controls?
- What source-derived notes would help the team if curated?
- Who should review notes from your area?
- What knowledge is stale, wrong, or risky if agents rely on it?
- What should route to `Restricted/` or stay out entirely?

## Guardrails

- Personal accounts are not company sources.
- Sensitive HR/legal/finance material needs restricted routing and explicit owner approval.
- If the user does not know an answer, record it as an open question instead of inventing content.
- Prefer several small staged notes over one large mixed note.
