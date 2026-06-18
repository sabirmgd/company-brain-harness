---
name: sources-check
description: Validate source registry entries and decide whether a specific account, workspace, channel, folder, inbox, calendar, repo org, or API key may feed staged capture. Use when the user says connect a source, can Slack or Gmail or Calendar or Fireflies or Apollo feed the brain, is this personal account allowed, check source ownership, or validate capture eligibility.
---

# Sources Check

Validate source instances. A connector type is not enough: the registry must name the exact account, workspace, channel, folder, org, inbox, calendar, or API key reference.

## Workflow

1. Resolve the brain root.
2. Read `company-brain.yml` to find the conventions directory.
3. Run `source-registry-check.py`.
4. For a connector job, select a specific `--source-id` and use `--for-capture`.
5. Refuse personal, unknown, proposed, excluded, suspended, or unapproved sources.
6. Report what source can run, who owns it, who reviews it, and what must change before capture.

## Command Patterns

Whole registry:

```bash
python3 <plugin-root>/bin/source-registry-check.py --root "$BRAIN_ROOT"
```

Specific source before capture:

```bash
python3 <plugin-root>/bin/source-registry-check.py \
  --root "$BRAIN_ROOT" \
  --source-id "<source-id>" \
  --for-capture
```

## Source Rules

- Company-owned and explicitly scoped customer-owned sources can feed staged capture after approval.
- Shared Apollo, CRM, Slack, Fireflies, GitHub, Google Workspace, or Notion accounts must each be represented as source instances.
- Personal accounts are excluded by default, even if a teammate uses that app for work.
- Delegated personal sources require narrow scope, owner approval, review owner, and source registry entry.
- Credentials are references only. Never store API keys, OAuth tokens, passwords, or service-account JSON in the brain.

## Team Prompts

When onboarding a teammate, ask:

- Which systems do you use for company work?
- Is each one company-owned, shared, customer-owned, or personal?
- What exact workspace/account/channel/folder should be considered?
- What should never be captured?
- Who should review notes from that source?
- Which folder should approved knowledge land in?
