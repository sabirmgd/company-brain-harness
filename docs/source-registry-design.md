# Source Registry Design

The harness must support many tools, many accounts, many workspaces, and many
companies without turning into a privacy or routing mess.

The rule:

> A connector is not a source. A specific approved account/workspace/channel is
> a source.

Fireflies, Google Workspace, Slack, GitHub, HubSpot, Notion, and CRM systems are
connector types. The company brain should never ingest from "Fireflies" in the
abstract. It ingests from an approved source instance, such as
`heyflora-fireflies-company-workspace`.

## Core Objects

### Connector Type

The tool family:

- `fireflies`
- `google_workspace`
- `slack`
- `github`
- `hubspot`
- `notion`
- `filesystem`
- `manual`

### Source Instance

One specific account, workspace, channel, folder, org, inbox, calendar, or API
key.

Examples:

- `heyflora-fireflies-company`
- `scott-fireflies-personal`
- `heyflora-google-workspace-engine`
- `heyflora-slack-customer-success-channels`
- `heyflora-github-org`
- `customer-acme-hubspot-production`

### Credential Reference

A pointer to where credentials live. Never the credential value.

Examples:

- `env:FIREFLIES_API_KEY`
- `gws:service-account`
- `secret-manager:company-brain/heyflora/fireflies`
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
id: heyflora-fireflies-company
connector: fireflies
display_name: HeyFlora Company Fireflies
control_tier: company_owned
status: approved_staging_only
credential_ref: env:HEYFLORA_FIREFLIES_API_KEY
owner: Scott
review_owner: Sabir
capture:
  allowed: true
  mode: scheduled
  approval_required: true
  raw_retention_days: 14
scope:
  include:
    - meetings with heyflora.ai participants
    - meetings tagged company-brain
  exclude:
    - personal meetings
    - HR/compensation/legal unless routed restricted
routing:
  default_destination: 12_Research_and_Industry_Intelligence/03_Customer_Research
  staging_destination: 00_README_Drive_Conventions/90_Staging
  restricted_prefixes:
    - 14_Owner_Vault
brain_artifacts:
  allowed:
    - curated_summary
    - decisions
    - action_items
    - reusable_facts
  not_allowed:
    - raw_transcript_by_default
dedupe:
  external_id_field: meeting_id
  strategy: source_id_plus_external_id
audit:
  last_reviewed: 2026-06-18
  approved_by: Scott
```

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

Raw material can live in private staging or a separate evidence store. The
shared brain gets the approved, useful version.

## Multi-Account Rules

Multiple accounts per connector are allowed. Each must be separately registered,
scoped, approved, and audited.

Allowed:

```text
fireflies:
  - heyflora company workspace
  - customer A company workspace
  - customer B company workspace

google_workspace:
  - heyflora service account
  - customer A delegated service account

slack:
  - heyflora selected channels
  - customer A selected channels
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
