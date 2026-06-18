---
name: source-setup
description: Guide Brain Owners and Operators through safe setup of email, Slack, Confluence, Google Workspace, Fireflies, CRM, GitHub, Notion, or other source instances. Use when the user says connect a source, connect Gmail, connect email, connect Slack, connect Confluence, connect CRM, approve a workspace, scope a personal source, or decide what a tool may feed into the brain.
---

# Source Setup

Set up source instances without turning the company brain into surveillance.

## Core Rule

Do not ask "Can we access this app?" first.

Ask:

```text
What part of this app is company knowledge?
Who owns it?
Who reviews it?
What must stay private?
What artifact may enter the brain?
```

## Role Split

- Brain Owner: approves tool, scope, visibility, retention, restricted routes, and reviewer.
- Brain Operator: configures credentials, registry entry, smoke checks, and schedule.
- Team Member: may delegate a personal source only with narrow scope and revocation path.

## Workflow

1. Identify connector family: email, Slack, Confluence, Google Workspace, Fireflies, CRM, GitHub, Notion, filesystem, manual.
2. Identify exact source instance: workspace, inbox, label, channel, space, folder, account, calendar, repo org, or API key reference.
3. Classify control tier:
   - company-owned
   - customer-owned
   - delegated personal
   - personal/private
   - unknown
4. Define scope:
   - include exact clients, labels, folders, channels, spaces, calendars, accounts, or domains
   - exclude personal, DMs, user spaces, HR, legal, finance, credentials, and private notes
5. Define raw policy:
   - default: raw material is private or temporary evidence, not shared brain knowledge
6. Define artifact policy:
   - allowed: summary, decision, action item, account update, customer fact, SOP update
   - not allowed: raw email, raw transcript, private message, credential value
7. Register or update `source-registry.yml`.
8. Run `source-registry-check.py --source-id <id> --for-capture`.
9. Do not pull anything until the source is capture-eligible.

## Plain Output

```text
Source setup status: Proposed / Capture-ready / Blocked

Owner decisions:
- ...

Operator actions:
- ...

Privacy boundaries:
- ...
```

## Guardrails

- Personal email, calendars, DMs, personal meeting recorders, and user spaces are excluded by default.
- Delegated personal sources must be narrow, revocable, and reviewed by the delegating person or owner.
- Raw source access is not brain access.
- The first scheduled run should stage proposals only.
