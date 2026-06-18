# Capture Policy Template

Use this as `CAPTURE_POLICY.md` inside a company brain root. The policy must be
approved by the brain owner before scheduled capture runs.

## Default Posture

Source-separated capture.

The engine captures only company-controlled sources by default. Personal
accounts are excluded unless a teammate explicitly delegates a narrow scope and
the brain owner approves the privacy rules.

Every connected tool must be represented as one or more explicit source
instances in `source-registry.yml`. A connector type is not enough. For example,
the brain does not ingest from "Fireflies"; it ingests from one approved
Fireflies workspace or account with a source id, owner, scope, routing rule, and
review policy.

## Allowed Sources

| Source | Status | Notes |
|---|---|---|
| Company Drive / shared brain root | Allowed | Storage backend for curated knowledge |
| Company Fireflies workspace | Allowed after owner approval | Shared company meeting source |
| Company Google Workspace account or service account | Allowed after admin approval | Gmail, Calendar, Docs, Sheets automation |
| Company GitHub org | Allowed | Repo index and stack guardrails |
| Shared Apollo/CRM workspace | Allowed after owner approval | GTM/customer/account facts |
| Personal Fireflies account | Excluded by default | Can contain private/non-company meetings; narrow delegation requires owner approval |
| Personal Gmail/Calendar/Apollo | Excluded by default | Client/project scopes can be delegated only with explicit include/exclude rules |

Multiple accounts per connector are allowed only when each account/workspace is
separately registered and approved.

Examples:

- `company-fireflies`
- `customer-acme-fireflies`
- `company-google-workspace-engine`
- `company-slack-selected-channels`
- `company-shared-apollo`
- `personal-fireflies-example` with `status: excluded`

## Team Member Source Inventory

Ask every teammate about sources from a team perspective:

- Which company/shared tools do you use?
- Which exact account, workspace, channel, folder, or org should be considered?
- Which personal tools should remain excluded?
- What source-derived notes would help the team if curated?
- Who owns and reviews notes from that source?
- What must never be captured?

Suggestions become source registry entries only after owner approval.

## Meeting Capture

Meeting capture is allowed only when all conditions are true:

- The source is company-controlled.
- The meeting has company or customer relevance.
- The capture policy has been approved.
- Raw transcript material stays in private evidence staging.
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
source -> private evidence -> proposal -> human review -> approved note
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
    - Restricted
```

## Approval Checklist

- [ ] Owner approves this policy.
- [ ] `source-registry.yml` exists and every source has owner, scope, status,
      routing, and credential reference.
- [ ] Restricted folders are permissioned correctly.
- [ ] Company-controlled meeting source exists.
- [ ] Engine credentials are stored outside the brain root.
- [ ] Capture jobs stage proposals instead of writing final notes directly.
- [ ] Morning review/digest process is assigned to an owner.
