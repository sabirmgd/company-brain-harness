# Source Registry Design

The harness must support many tools, many accounts, many workspaces, and many
companies without turning into a privacy or routing mess.

The rule:

> A connector is not a source. A specific approved account/workspace/channel is
> a source.

Fireflies, Google Workspace, Slack, GitHub, HubSpot, Apollo, Notion, and CRM
systems are connector types. The company brain should never ingest from
"Fireflies" in the abstract. It ingests from an approved source instance, such as
`company-fireflies-workspace`.

## Core Objects

### Connector Type

The tool family:

- `fireflies`
- `google_workspace`
- `slack`
- `github`
- `hubspot`
- `apollo`
- `notion`
- `filesystem`
- `manual`

### Source Instance

One specific account, workspace, channel, folder, org, inbox, calendar, or API
key.

Examples:

- `company-fireflies-workspace`
- `personal-fireflies-example`
- `company-google-workspace-engine`
- `company-slack-selected-channels`
- `company-github-org`
- `customer-acme-hubspot-production`
- `company-shared-apollo-workspace`

### Credential Reference

A pointer to where credentials live. Never the credential value.

Examples:

- `env:FIREFLIES_API_KEY`
- `gws:service-account`
- `secret-manager:company-brain/acme/fireflies`
- `manual:none`

### Control Tier

Who controls the source:

- `company_owned` - company account/workspace/service account
- `customer_owned` - customer account connected for that customer's brain
- `delegated_personal` - a person's account explicitly delegated for limited
  scope
- `personal_private` - personal account; not eligible for engine capture
- `unknown` - not eligible until classified

Default posture: only `company_owned` and explicitly scoped `customer_owned`
sources can feed a shared company brain.

## Source Lifecycle

Use explicit states:

- `excluded` - known source, never ingest
- `proposed` - discovered or requested, not approved
- `approved_staging_only` - can stage proposals, cannot auto-promote
- `active` - can run under its capture policy
- `suspended` - temporarily disabled
- `retired` - historical source, no new capture

Only `active` and `approved_staging_only` can produce staged proposals.
Auto-promotion is a separate policy and should be rare.

## Required Fields

Every source instance should declare:

```yaml
id: company-fireflies-workspace
connector: fireflies
display_name: Company Fireflies Workspace
control_tier: company_owned
status: approved_staging_only
credential_ref: env:COMPANY_FIREFLIES_API_KEY
owner: Company Owner
review_owner: Brain Owner
capture:
  allowed: true
  mode: scheduled
  approval_required: true
  raw_retention_days: 14
scope:
  include:
    - meetings with company-domain participants
    - meetings tagged company-brain
  exclude:
    - personal meetings
    - HR/compensation/legal unless routed restricted
raw_policy:
  store_raw: private_only
  retention_days: 14
routing:
  default_destination: brain/intelligence/meetings
  staging_destination: system/staging
  restricted_prefixes:
    - brain/restricted
artifact_policy:
  allowed:
    - curated_summary
    - decisions
    - action_items
    - reusable_facts
  not_allowed:
    - raw_transcript_by_default
    - credential_value
dedupe:
  external_id_field: meeting_id
  strategy: source_id_plus_external_id
sync:
  enabled: false
  cursor: null
  last_successful_pull: null
audit:
  last_reviewed: 2026-06-18
  approved_by: Company Owner
```

## Source-Governed Capture Pipeline

Raw access is not brain access.

```text
approved source -> scoped pull -> private evidence -> extraction -> staged proposal -> review -> approved brain note
```

The harness stores sync state separately from source policy:

```text
system/source-sync-state.json
```

Each source keeps:

- cursor or page token
- last successful pull time
- per-item content hashes
- last staged hash
- last pull/extract counts

This lets operators pull only new or changed items without reprocessing the
same email thread, Slack message, Confluence page, CRM record, or meeting recap.

## Connector-Specific Privacy Rules

### Email

- Shared inboxes and aliases can be company-owned sources.
- Personal inboxes are excluded by default.
- Delegated personal email must be scoped by client, label, sender/domain,
  thread, or date range.
- Raw email bodies stay private/temporary evidence unless explicitly approved.
- Brain artifacts should be commitments, customer facts, decisions, account
  updates, and action items, not raw emails.

### Slack

- Public/company channels can be source instances.
- Private channels require explicit approval and reviewer assignment.
- DMs are excluded by default.
- Brain artifacts should be decisions, blockers, incidents, account facts, and
  reusable SOP updates.

### Confluence

- Company spaces can be source instances.
- User/personal spaces are excluded by default.
- brain/restricted spaces route to restricted staging or stay out.
- Brain artifacts should be canonical summaries, source references, and changed
  decisions, not page dumps.

### CRM

- Company account records can be source instances.
- Account-manager private notes require explicit scope and reviewer.
- Brain artifacts should be account summaries, risks, lifecycle changes, next
  steps, and customer facts.

### Meetings

- Company recorder workspaces can be source instances.
- Personal recorder accounts are excluded unless delegated and scoped.
- Raw transcripts are not shared brain notes.
- Brain artifacts should be decisions, action items, objections, customer facts,
  and reusable context.

## What Goes Into The Brain

Shared brain contents should be curated artifacts, not raw dumps.

Default allowed artifacts:

- summaries
- decisions
- action items
- reusable facts
- SOP updates
- customer/account facts
- repo/stack facts
- open questions
- provenance links

Default not allowed:

- raw transcripts
- raw emails
- private calendar details
- credential values
- personal notes
- unreviewed sensitive material

Raw material can live in private evidence staging or a separate evidence store. The
shared brain gets the approved, useful version.

## Multi-Account Rules

Multiple accounts per connector are allowed. Each must be separately registered,
scoped, approved, and audited.

Allowed:

```text
fireflies:
  - company primary workspace
  - customer A company workspace
  - customer B company workspace

google_workspace:
  - company service account
  - customer A delegated service account

slack:
  - company selected channels
  - customer A selected channels

apollo:
  - company shared Apollo workspace
  - customer A owned Apollo workspace
```

Not allowed:

```text
fireflies:
  - every employee's personal Fireflies account

gmail:
  - everyone personal Gmail
```

Personal connectors may help an individual in their own agent session, but they
are not shared engine sources unless explicitly delegated, scoped, and approved.

## Delegated Personal Sources

Delegated personal sources are allowed only when all of these are true:

- the teammate opts in
- the scope is narrow and written down
- the reviewer is named
- raw evidence is private or temporary
- the teammate can revoke access
- only curated artifacts can become shared brain notes

Example:

```yaml
id: delegated-email-owner-silz
connector: email
display_name: Owner email threads for SILZ only
control_tier: delegated_personal
status: approved_staging_only
credential_ref: keychain:owner-email-delegated
owner: Account Owner
review_owner: Account Owner
capture:
  allowed: true
  mode: scheduled
  approval_required: true
  raw_retention_days: 7
scope:
  include:
    - client:SILZ
    - label:company-brain
    - from_domain:silz.example
  exclude:
    - personal
    - HR
    - legal
    - finance
    - family
raw_policy:
  store_raw: private_only
  retention_days: 7
artifact_policy:
  allowed:
    - customer_fact
    - commitment
    - action_item
    - account_update
  not_allowed:
    - raw_email
    - private_message
    - credential_value
sync:
  enabled: false
  cursor: null
  last_successful_pull: null
```

## Angles To Protect

### Privacy

Never capture broadly and classify later when source separation is possible.
Prefer company-controlled sources. Unknown or personal sources stay out.

### Trust

Every teammate should be able to see what sources feed the brain, who approved
them, and what artifacts are created.

### Security

Store only credential references in the registry. Secrets live in env vars,
keychains, secret managers, or service-account files outside the brain.

### Governance

Every source has an owner, review owner, approval state, and retention rule.
Sensitive routes are explicit.

### Scale

One brain root has one registry. A multi-customer product has one registry per
customer brain. Never mix customer sources in one global registry.

### AI Quality

Raw data is noisy. The brain should contain curated notes with provenance,
frontmatter, tags, and routing, not raw connector payloads.

### Cost

Each source defines capture frequency and scope. Avoid fetching every channel,
every email, or every meeting when a filter would do.

### Offboarding

If a person leaves, company-owned sources continue. Personal/delegated sources
are suspended and reviewed.

## Product Rule

The customer-facing product should ask:

1. What tool do you want to connect?
2. Which account/workspace/channel should feed the company brain?
3. Who controls it?
4. What should be captured?
5. What should never be captured?
6. Who approves staged notes?
7. Where should approved knowledge land?

That interview produces `source-registry.yml`, not hidden magic.

## Executable Enforcement

The current harness includes a registry validator:

```bash
python3 plugins/company-brain-harness/bin/source-registry-check.py --root "$BRAIN_ROOT"
```

Connector jobs should gate capture on a specific source:

```bash
python3 plugins/company-brain-harness/bin/source-registry-check.py \
  --root "$BRAIN_ROOT" \
  --source-id "<source-id>" \
  --for-capture
```

This enforces the core policy before connector code runs:

- source exists
- source is not personal or unknown
- source status is `active` or `approved_staging_only`
- `capture.allowed` is true
- credential reference does not look like a secret value
- required owner, review owner, status, control tier, and capture fields exist

Adapter-specific enforcement is still required for scope filters, retention,
pagination, dedupe, raw evidence storage, and connector API authorization.
