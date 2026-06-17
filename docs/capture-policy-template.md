# Capture Policy Template

Use this as `CAPTURE_POLICY.md` inside a company brain root. The policy must be
approved by the brain owner before scheduled capture runs.

## Default Posture

Source-separated capture.

The engine captures only company-controlled sources. Personal accounts are never
treated as company data sources by default.

## Allowed Sources

| Source | Status | Notes |
|---|---|---|
| Company Drive / shared brain root | Allowed | Storage backend for curated knowledge |
| Company Fireflies workspace | Allowed after owner approval | Shared company meeting source |
| Company Google Workspace account or service account | Allowed after admin approval | Gmail, Calendar, Docs, Sheets automation |
| Company GitHub org | Allowed | Repo index and stack guardrails |
| Personal Fireflies account | Not allowed | Can contain private/non-company meetings |
| Personal Gmail/Calendar | Not allowed for engine capture | Teammates may use personal connectors in their own sessions |

## Meeting Capture

Meeting capture is allowed only when all conditions are true:

- The source is company-controlled.
- The meeting has company or customer relevance.
- The capture policy has been approved.
- Raw transcript material stays in private staging.
- Only curated notes enter the shared brain.

Default meeting artifact:

```text
decisions + action items + reusable knowledge + open questions + provenance link
```

The shared brain should not receive full raw transcripts unless the owner
explicitly approves that behavior.

## Staging And Approval

All automatic capture uses this path:

```text
source -> private staging -> proposal -> human review -> approved note
```

Rejected or personal material is not promoted to the shared brain.

## Sensitive Routing

Company material can still be restricted. HR, finance, legal, fundraising,
compensation, cap table, and sensitive IP go to a restricted folder or stay out
of the broad shared brain.

Restricted folders must be declared in `company-brain.yml`:

```yaml
brain:
  restricted_prefixes:
    - 14_Owner_Vault
```

## Approval Checklist

- [ ] Owner approves this policy.
- [ ] Restricted folders are permissioned correctly.
- [ ] Company-controlled meeting source exists.
- [ ] Engine credentials are stored outside the brain root.
- [ ] Capture jobs stage proposals instead of writing final notes directly.
- [ ] Morning review/digest process is assigned to an owner.
