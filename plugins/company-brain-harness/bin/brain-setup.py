#!/usr/bin/env python3
"""Scaffold a portable, team-first Company Brain root."""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import date
from pathlib import Path


DEFAULT_ROOT = (
    os.environ.get("BRAIN_ROOT")
    or os.environ.get("COMPANY_BRAIN_ROOT")
    or os.environ.get("COMPANY_OS_ROOT")
    or os.getcwd()
)
CONVENTIONS_DIR = "system"
STAGING_DIR = f"{CONVENTIONS_DIR}/staging"
DIGESTS_DIR = f"{CONVENTIONS_DIR}/digests"
DROP_ZONE_DIR = "ADD_TO_BRAIN"
PROFILE_GOVERNED = "governed"
PROFILE_SIMPLE_TEAM = "simple-team"
OPERATING_PROFILES = (PROFILE_GOVERNED, PROFILE_SIMPLE_TEAM)
FOLDERS = {
    "brain": "Curated company knowledge. Harness state lives under system/.",
    "brain/company": "Stable company context, operating model, strategy, history, and principles.",
    "brain/product": "Product state, launch readiness, roadmap, decisions, and active product work.",
    "brain/engineering": "Engineering routes, repo maps, architecture notes, and implementation evidence.",
    "brain/engineering/repos": "Repository maps and implementation source routes.",
    "brain/go-to-market": "Positioning, pricing, launch motion, sales assets, and growth experiments.",
    "brain/go-to-market/accounts": "Approved account and prospect intelligence for go-to-market work.",
    "brain/customers": "Customer onboarding, support, success, feedback, and customer evidence.",
    "brain/customers/accounts": "Approved customer account context, commitments, feedback, and follow-up notes.",
    "brain/operations": "Daily loops, departments, team profiles, and reusable workflows.",
    "brain/operations/daily": "Morning checks, daily decisions, ships, incidents, blockers, and follow-ups.",
    "brain/operations/departments": "Department SOPs, role-specific workflows, ownership, and review expectations.",
    "brain/operations/team": "Teammate profiles, owned workflows, preferences, and contribution notes.",
    "brain/operations/skills": "Company-specific prompts, skills, and reusable operating procedures.",
    "brain/intelligence": "Meetings, market notes, customer voice, and decision history.",
    "brain/intelligence/meetings": "Curated meeting intelligence, timelines, and meeting summaries.",
    "brain/sources": "Curated source-derived notes and source reference maps.",
    "brain/sources/confluence": "Curated Confluence-derived notes.",
    "brain/restricted": "Sensitive material. Excluded from default agent scans and broad team access.",
    "brain/archive": "Deprecated or superseded knowledge retained for auditability.",
}


def is_simple_team(operating_profile: str) -> bool:
    return operating_profile == PROFILE_SIMPLE_TEAM


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "company"


def frontmatter(tags: list[str]) -> str:
    today = date.today().isoformat()
    lines = ["---", "status: active", "tags:"]
    lines.extend(f"  - {tag}" for tag in tags)
    lines.append(f"last_verified: {today}")
    lines.extend(["---", ""])
    return "\n".join(lines)


def root_claude(company: str, champion: str, operating_profile: str = PROFILE_GOVERNED) -> str:
    simple = is_simple_team(operating_profile)
    drop_zone_route = f"| Team drop-zone contributions | `{DROP_ZONE_DIR}/` |\n" if simple else ""
    shared_write_rule = (
        f"Team contributions in `{DROP_ZONE_DIR}/` may be digested and processed automatically when low-risk; "
        "sensitive, unclear, private, or restricted material still requires owner/operator review."
        if simple else
        "Shared writes go through staging unless the Brain Owner explicitly approves direct admin edits."
    )
    simple_profile_section = f"""
## Simple Team Profile

This brain uses the `simple-team` operating profile. Nontechnical teammates can
drop material into `{DROP_ZONE_DIR}/` or ask the agent to add it. The operator
loop should scan the drop zone, produce a digest, process low-risk manual
contributions into curated notes, and flag anything sensitive or unclear.

Source connectors remain governed. Do not use this profile as permission to
capture broad personal email, calendar, meeting, CRM, or chat data.
""" if simple else ""
    return f"""# {company} Company Brain

This repo is the company's shared brain: curated operating knowledge, source
references, and private harness state. Claude Code, Claude Cowork, Codex, and
other agents should treat this file as the root routing contract.

Operating profile: `{operating_profile}`

## Session Startup

1. Read this file first.
2. Identify the active teammate or role.
3. Read that person's `brain/operations/team/<name>/profile.md` when present.
4. Read the target folder's `README.md` before writing there.
5. Use source registry and capture policy before touching external data.

## Knowledge Routing

| Type | Route to |
|---|---|
| Strategy, company context, operating model | `brain/company/` |
| Product state, launch readiness, roadmap, decisions | `brain/product/` |
| Engineering repo maps and implementation routes | `brain/engineering/` |
| GTM, positioning, pricing, launch motion | `brain/go-to-market/` |
| Customer onboarding, support, success material | `brain/customers/` |
| Daily operations, departments, team, reusable workflows | `brain/operations/` |
| Meetings, market notes, customer voice, decisions | `brain/intelligence/` |
| Source-derived notes and source maps | `brain/sources/` |
| Teammate profiles, preferences, tasks | `brain/operations/team/<name>/` |
| Shared skills and prompt workflows | `brain/operations/skills/` |
| Sensitive HR, legal, finance, owner-only material | `brain/restricted/` |
| Superseded or retained history | `brain/archive/` |
| Harness configuration, staging, evidence, raw source capture | `system/` |
{drop_zone_route}
{simple_profile_section}

## Rules

1. {shared_write_rule}
2. Personal connectors are excluded by default unless narrowly delegated, scoped, approved, and registered.
3. Every org-wide source instance must exist in `{CONVENTIONS_DIR}/source-registry.yml`.
4. Source-derived notes need provenance: `<!-- src: <source-id>/<item-id> @ YYYY-MM-DD -->`.
5. Every content note needs frontmatter with `status`, `tags`, and `last_verified`.
6. Never create files at the root except routing, config, and setup guide files.
7. Never read, index, summarize, or write `brain/restricted/` unless the owner explicitly grants access.
8. Prefer updating existing notes over creating duplicate versions.
9. If a newer source contradicts an older claim, edit the old claim in place with a dated warning.
10. If unsure where something belongs, suggest two destinations and ask the Brain Owner.

## Operating Roles

- Brain Owner: {champion}. Owns policy, review, adoption, and source approval.
- Brain Operator: configured in `{CONVENTIONS_DIR}/team.yml`. Runs checks, lint, staging, and schedules.

## Anti-Patterns

- Capturing from "Fireflies" or "Apollo" in the abstract. Register the specific workspace/account first.
- Ingesting every teammate's personal Gmail, calendar, or meeting recorder.
- Treating raw transcripts or emails as shared knowledge.
- Letting daily notes, source registry, or `last_verified` fields go stale.
- Forking `strategy-v2.md` instead of updating the canonical strategy note with provenance.
"""


def company_brain_yml(company: str, operating_profile: str = PROFILE_GOVERNED) -> str:
    simple = is_simple_team(operating_profile)
    human_required = "false" if simple else "true"
    drop_zone_value = DROP_ZONE_DIR if simple else "null"
    manual_default = "auto_digest_and_process_low_risk" if simple else "staged_review"
    auto_promote_manual = "true" if simple else "false"
    daily_digest = "true" if simple else "false"
    return f"""schema_version: "1.0"
kind: company_brain_config
operating_profile: {operating_profile}
company:
  name: "{company}"
  implementation_status: setup
brain:
  routing_file: CLAUDE.md
  conventions_dir: {CONVENTIONS_DIR}
  staging_dir: {STAGING_DIR}
  restricted_prefixes:
    - brain/restricted
policy:
  capture_policy: {CONVENTIONS_DIR}/capture-policy.md
  require_human_approval_for_shared_writes: {human_required}
  human_review_required_for_sensitive_or_unclear: true
  personal_connectors_are_company_sources: false
intake:
  profile: {operating_profile}
  drop_zone: {drop_zone_value}
  manual_contribution_default: {manual_default}
  team_members_need_source_registry: false
  flag_sensitive_for_review: true
promotion:
  preview_by_default: true
  require_write_flag: true
  require_provenance: true
  require_two_tags: true
  auto_promote_manual_drop_zone_low_risk: {auto_promote_manual}
  never_auto_promote_restricted_or_sensitive: true
evidence:
  normalized_dir: {STAGING_DIR}/evidence
  raw_dir: {STAGING_DIR}/raw
  raw_is_shared_knowledge: false
  raw_requires_source_policy: true
automation:
  daily_digest: {daily_digest}
  add_to_brain_digest: {DIGESTS_DIR}/latest.md
  source_connectors_still_require_registry: true
health:
  priority_folders:
    - brain/company
    - brain/product
    - brain/engineering
    - brain/operations
    - brain/intelligence
    - brain/sources
"""


def source_registry(company: str, champion: str, operating_profile: str = PROFILE_GOVERNED) -> str:
    source_id = slugify(company)
    drop_zone_source = f"""

  - id: {source_id}-add-to-brain-drop-zone
    connector: filesystem
    display_name: Manual team contribution drop zone
    control_tier: company_owned
    status: active
    credential_ref: manual:none
    owner: {champion}
    review_owner: {champion}
    capture:
      allowed: true
      mode: mounted_folder
      approval_required: false
      raw_retention_days: 0
    scope:
      include:
        - low-risk manual team contributions under {DROP_ZONE_DIR}
        - source documents intentionally added by teammates
        - meeting notes intentionally added by teammates
      exclude:
        - credentials
        - personal/private material
        - HR/legal/finance unless routed restricted and reviewed
        - broad connector exports
        - personal inbox/calendar/meeting recorder dumps
    raw_policy:
      store_raw: false
      retention_days: 0
    routing:
      default_destination: brain/sources
      staging_destination: {STAGING_DIR}
      restricted_prefixes:
        - brain/restricted
    artifact_policy:
      allowed:
        - curated_note
        - source_reference
        - decision
        - action_item
        - reusable_fact
      not_allowed:
        - credential_value
        - raw_export_by_default
        - personal_message
    dedupe:
      external_id_field: path
      strategy: path_plus_hash
    sync:
      enabled: true
      cursor: null
      last_successful_pull: null
    audit:
      last_reviewed: {date.today().isoformat()}
      approved_by: {champion}
""" if is_simple_team(operating_profile) else ""
    return f"""schema_version: "1.0"
kind: company_brain_source_registry

defaults:
  raw_retention_days: 14
  approval_required: true
  auto_promote_allowed: false
  personal_connectors_are_company_sources: false

sources:
  - id: {source_id}-brain-root
    connector: filesystem
    display_name: {company} Brain Root
    control_tier: company_owned
    status: active
    credential_ref: manual:none
    owner: {champion}
    review_owner: {champion}
    capture:
      allowed: true
      mode: mounted_folder
      approval_required: false
      raw_retention_days: 0
    scope:
      include:
        - curated markdown brain notes
        - approved source documents inside the brain root
      exclude:
        - credential values
        - private personal material
        - restricted material
    raw_policy:
      store_raw: false
      retention_days: 0
    routing:
      default_destination: "."
      staging_destination: {STAGING_DIR}
      restricted_prefixes:
        - brain/restricted
    artifact_policy:
      allowed:
        - curated_note
        - source_reference
      not_allowed:
        - credential_value
    dedupe:
      external_id_field: path
      strategy: path
    sync:
      enabled: false
      cursor: null
      last_successful_pull: null
    audit:
      last_reviewed: {date.today().isoformat()}
      approved_by: {champion}
{drop_zone_source}

  - id: example-company-meetings
    connector: fireflies
    display_name: Company meeting workspace
    control_tier: company_owned
    status: proposed
    credential_ref: env:COMPANY_FIREFLIES_API_KEY
    owner: {champion}
    review_owner: {champion}
    capture:
      allowed: false
      mode: scheduled
      approval_required: true
      raw_retention_days: 14
    scope:
      include:
        - company-controlled meetings
        - meetings tagged company-brain
      exclude:
        - personal meetings
        - HR/legal/finance unless routed restricted
    raw_policy:
      store_raw: private_only
      retention_days: 14
    routing:
      default_destination: brain/intelligence/meetings
      staging_destination: {STAGING_DIR}
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
      last_reviewed: null
      approved_by: null

  - id: example-shared-apollo
    connector: apollo
    display_name: Shared Apollo Workspace
    control_tier: company_owned
    status: proposed
    credential_ref: env:COMPANY_APOLLO_API_KEY
    owner: {champion}
    review_owner: {champion}
    capture:
      allowed: false
      mode: scheduled
      approval_required: true
      raw_retention_days: 14
    scope:
      include:
        - company-owned Apollo accounts and contacts approved for GTM use
        - enrichment fields approved by the Brain Owner
      exclude:
        - personal prospecting lists
        - private notes owned by an individual teammate
        - credentials or billing data
    raw_policy:
      store_raw: private_only
      retention_days: 14
    routing:
      default_destination: brain/go-to-market/accounts
      staging_destination: {STAGING_DIR}
      restricted_prefixes:
        - brain/restricted
    artifact_policy:
      allowed:
        - account_summary
        - customer_fact
        - reusable_gtm_note
      not_allowed:
        - raw_export_by_default
        - credential_value
    dedupe:
      external_id_field: apollo_id
      strategy: source_id_plus_external_id
    sync:
      enabled: false
      cursor: null
      last_successful_pull: null
    audit:
      last_reviewed: null
      approved_by: null

  - id: example-company-confluence
    connector: confluence
    display_name: Company Confluence spaces
    control_tier: company_owned
    status: proposed
    credential_ref: env:COMPANY_CONFLUENCE_TOKEN
    owner: {champion}
    review_owner: {champion}
    capture:
      allowed: false
      mode: scheduled
      approval_required: true
      raw_retention_days: 14
    scope:
      include:
        - company spaces approved for brain use
        - published pages with company-wide visibility
      exclude:
        - user spaces
        - drafts
        - restricted spaces unless routed restricted
        - HR/legal/finance unless routed restricted
    raw_policy:
      store_raw: private_only
      retention_days: 14
    routing:
      default_destination: brain/sources/confluence
      staging_destination: {STAGING_DIR}
      restricted_prefixes:
        - brain/restricted
    artifact_policy:
      allowed:
        - canonical_summary
        - sop_update
        - decision
        - source_reference
      not_allowed:
        - raw_page_dump
        - credential_value
    dedupe:
      external_id_field: page_id
      strategy: source_id_plus_external_id
    sync:
      enabled: false
      cursor: null
      last_successful_pull: null
    audit:
      last_reviewed: null
      approved_by: null

  - id: example-delegated-client-email
    connector: email
    display_name: Delegated client-scoped email example
    control_tier: delegated_personal
    status: proposed
    credential_ref: keychain:delegated-client-email
    owner: account-owner
    review_owner: account-owner
    capture:
      allowed: false
      mode: scheduled
      approval_required: true
      raw_retention_days: 7
    scope:
      include:
        - client:example-client
        - label:company-brain
        - from_domain:example-client.com
      exclude:
        - personal
        - family
        - HR
        - legal
        - finance
    raw_policy:
      store_raw: private_only
      retention_days: 7
    routing:
      default_destination: brain/customers/accounts
      staging_destination: {STAGING_DIR}
      restricted_prefixes:
        - brain/restricted
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
    dedupe:
      external_id_field: thread_id
      strategy: source_id_plus_external_id
    sync:
      enabled: false
      cursor: null
      last_successful_pull: null
    audit:
      last_reviewed: null
      approved_by: null

  - id: example-personal-meetings
    connector: fireflies
    display_name: Personal meeting recorder example
    control_tier: personal_private
    status: excluded
    credential_ref: none
    owner: individual
    review_owner: {champion}
    capture:
      allowed: false
      mode: none
      approval_required: true
      raw_retention_days: 0
    scope:
      include: []
      exclude:
        - all scheduled company-brain capture
    raw_policy:
      store_raw: false
      retention_days: 0
    routing:
      default_destination: null
      staging_destination: {STAGING_DIR}
      restricted_prefixes:
        - brain/restricted
    artifact_policy:
      allowed: []
      not_allowed:
        - raw_transcript
        - meeting_summary
    dedupe:
      external_id_field: null
      strategy: none
    sync:
      enabled: false
      cursor: null
      last_successful_pull: null
    audit:
      last_reviewed: null
      approved_by: null

rules:
  - "A connector type is not a source; every account/workspace/channel needs its own source id."
  - "A source can stage proposals only when status is active or approved_staging_only and capture.allowed is true."
  - "Personal/private sources are excluded from scheduled company-brain capture."
  - "Credentials are referenced, never stored in the brain."
"""


def connections_doc(operating_profile: str = PROFILE_GOVERNED) -> str:
    simple_row = (
        f"| Manual team drop zone | Active | `{DROP_ZONE_DIR}/`; low-risk manual contributions can be digested and processed |\n"
        if is_simple_team(operating_profile) else ""
    )
    return frontmatter(["connections", "sources", "team"]) + """# Connections

Connection inventory for this company brain. This is a human-readable companion to `source-registry.yml`.

## Principles

- Register source instances, not broad app names.
- Prefer company-owned or shared accounts for team capture.
- Keep personal accounts excluded unless explicitly delegated and scoped.
- Store credentials outside the brain and reference them by name only.

## Initial Source Categories

| Category | Default Status | Notes |
|---|---|---|
| Brain root | Active | Curated markdown and approved source documents |
""" + simple_row + """\
| Company meeting workspace | Proposed | Can stage curated meeting notes after approval |
| Company Google Workspace | Proposed | Scope Drive/Docs/Calendar/Gmail before any sync |
| Company Confluence spaces | Proposed | Company spaces only; user spaces excluded by default |
| Delegated client email | Proposed | Narrow, revocable, client-scoped, staging-only |
| Shared Apollo/CRM workspace | Proposed | Can stage GTM/account facts after approval |
| Company GitHub org | Proposed | Can refresh repo maps after approval |
| Personal Gmail/Calendar/Fireflies/Apollo | Excluded | Not a company engine source by default |

## Before Enabling A Connector

1. Add or update the exact source instance in `source-registry.yml`.
2. Run `source-registry-check.py --for-capture --source-id <id>`.
3. Confirm owner, review owner, routing, retention, and exclusions.
4. Run `source-pull.py` and `source-extract.py` once in preview or staging before scheduling.
"""


def capture_policy(company: str, operating_profile: str = PROFILE_GOVERNED) -> str:
    simple_section = f"""
## Simple Team Manual Contribution Rule

This brain uses the `simple-team` profile. Teammates may add low-risk material
to `{DROP_ZONE_DIR}/` or ask an agent to add it. The operator may process those
manual contributions into curated notes without item-by-item owner approval
when the material is clearly company-owned, non-sensitive, and relevant.

Anything private, personal, credential-like, HR, legal, finance,
customer-confidential, strategy-changing, or unclear must be flagged for
owner/operator review before promotion.
""" if is_simple_team(operating_profile) else ""
    return frontmatter(["capture-policy", "privacy", "governance"]) + f"""# Capture Policy

This policy controls what may enter the {company} company brain.

## Default Posture

- Company-owned sources can feed the shared brain after approval.
- Customer-owned sources can feed only that customer's brain after approval.
- Personal sources are excluded by default.
- Raw material stays in private raw evidence staging unless source policy says otherwise.
- Normalized evidence is used for extraction and review; raw evidence is retained for audit and deeper source review.
- Curated notes enter the brain only after review or an explicitly approved automation rule.
{simple_section}

## Team Source Rule

Ask each teammate what sources they can contribute, but register source instances at the org level:

- company meeting workspace
- shared calendar or room calendar
- company inbox or alias
- shared Apollo/CRM workspace
- approved Slack channels
- company GitHub/org repos
- teammate-owned personal accounts explicitly delegated for a narrow scope

Do not connect "everyone's personal account" as a shortcut.

## Sensitive Routing

HR, legal, finance, fundraising, compensation, private customer data, and owner-only strategy route to `brain/restricted/` or stay out.

## Approval Checklist

- [ ] Brain Owner approves this policy.
- [ ] Source registry is valid.
- [ ] Restricted folder permissions are correct.
- [ ] Review owner is named.
- [ ] Retention and purge rules are chosen.
"""


def harness_flows(operating_profile: str = PROFILE_GOVERNED) -> str:
    simple_section = f"""
## Simple Team Drop-Zone Flow

Use this profile when the company wants the easiest team adoption path.

```text
teammate drops file in {DROP_ZONE_DIR}/ -> operator digest -> low-risk note update
                                      -> sensitive/unclear review queue
```

Run `add-to-brain-digest.py` during the operator loop. The digest is not shared
knowledge by itself; it tells the operator or agent what changed and what needs
review.
""" if is_simple_team(operating_profile) else ""
    return frontmatter(["harness", "flows", "team"]) + """# Harness Flows

## Setup

Run `brain-setup` once per company brain. Then run `brain-health`, `sources-check`, and `brain-lint`.
""" + simple_section + """

## Intake

Classify source -> route -> draft note -> preview -> stage with `--write` only when approved for review.

## Team Onboarding

Interview each teammate for:

- role and owned workflows
- source systems they use
- what they can contribute to the shared brain
- what should stay personal/private
- review expectations

## Source Approval

Every tool account/workspace/channel becomes a source instance. A shared Apollo account is one company-owned source. A teammate's personal Apollo login is not a company source unless delegated, scoped, approved, and registered.

## Source Sync

Approved sources follow this path:

```text
approved source -> scoped pull -> private evidence -> extraction -> staged proposal -> review -> approved brain note
```

Use `source-pull.py` for normalized connector records. If the source policy
allows raw retention and the connector emits `raw_body`, `raw_text`,
`raw_content`, `raw_payload`, or `raw`, raw material is written under
`system/staging/raw/` and the normalized evidence receives a private pointer.
Then use `source-extract.py` to create staged proposals. Cursor and dedupe state
lives in `source-sync-state.json`.

## Maintenance

Daily: connection check, source registry check, approved source pull/extract, health, lint, staged queue review.
Weekly: stale-note review, source ownership review, routing cleanup.
Monthly: permissions, retention, auto-promotion, and adoption review.
"""


def harness_status(operating_profile: str = PROFILE_GOVERNED) -> str:
    simple_built = (
        f"- simple team drop zone at `{DROP_ZONE_DIR}/`\n"
        f"- operator digest folder at `{DIGESTS_DIR}/`\n"
        if is_simple_team(operating_profile) else ""
    )
    return frontmatter(["harness", "status"]) + """# Harness Status

This file prevents overclaiming.

## Built At Setup

- root routing file
- conventions folder
- capture policy
- source registry
- team map
- staging folder
- operating schedule
- folder indexes
""" + simple_built + """

## Not Populated Yet

The company owner and teammates still need to add real strategy, customer, project, team, and operational knowledge.

## First Pilot Gate

- source registry valid
- restricted permissions checked
- schedule chosen
- Brain Owner assigned
- first teammate onboarded
- no personal connector used as a company source
"""


def naming_conventions_md() -> str:
    return frontmatter(["naming", "taxonomy", "harness"]) + """# Naming Conventions

This brain uses product-grade repository naming, not drive-folder numbering.

## Rules

- Use lowercase kebab-case for non-conventional paths.
- Use domain nouns, not numbers, to organize knowledge.
- Keep curated knowledge under `brain/`.
- Keep harness state, staging, evidence, and raw captures under `system/`.
- Use `README.md` as the folder entry point.
- Keep raw source files private under `system/staging/raw/`.
- Do not encode sort order in folder names. Use README files for navigation.

## Reserved Conventional Names

- `README.md` is the repo and folder entry point.
- `CLAUDE.md` is the Claude/Codex routing contract.
- `company-brain.yml` is the harness config.
"""


def team_yml(champion: str, operator: str) -> str:
    return f"""schema_version: "1.0"
kind: company_brain_team_map
roles:
  champion:
    description: "Brain Owner: human owner of policy, review, source approval, and adoption."
  operator:
    description: "Brain Operator: agent or teammate that runs checks, lint, staging, and schedules."
  teammate:
    description: "Team Member: contributes knowledge and approved source context from their role."
known_people:
  {slugify(champion)}:
    role: champion
    status: active
  {slugify(operator)}:
    role: operator
    status: proposed
rules:
  - "Role routing is a starting point; CLAUDE.md and folder indexes decide final destination."
  - "No role grants restricted access unless permissions and owner approval allow it."
  - "Each teammate may suggest sources; the Brain Owner approves org-wide source instances."
"""


def schedule_md(champion: str, operator: str, operating_profile: str = PROFILE_GOVERNED) -> str:
    if is_simple_team(operating_profile):
        first_two_weeks = f"""- Run checks manually each morning or schedule them through Claude/Codex.
- Scan `{DROP_ZONE_DIR}/` and write `{DIGESTS_DIR}/latest.md`.
- Process clearly low-risk manual contributions into curated notes.
- Flag sensitive, unclear, personal, HR, legal, finance, or restricted items for review.
- Keep connector-based source pulls governed by `source-registry.yml`.
- Ask teammates to mention what they added during the first week, then move toward automatic daily digests.
"""
        after_trust = """- Schedule daily checks and drop-zone digest generation.
- Allow low-risk manual contributions to be processed without item-by-item owner review.
- Let approved source connectors create staged proposals only after registry approval.
- Keep source registry, lint, restricted permissions, and flagged digest items in the daily report.
"""
    else:
        first_two_weeks = """- Run checks manually each morning.
- Pull approved source records into private evidence.
- Extract allowed artifacts into staged proposals.
- Stage every proposed note.
- Require human approval before promotion.
- Keep meeting-derived and sensitive material human-approved.
"""
        after_trust = """- Schedule daily checks.
- Allow approved sources to create staged proposals.
- Track source cursors and hashes in `source-sync-state.json`.
- Consider autonomous promotion only for explicitly low-risk categories.
- Keep source registry, lint, and restricted permissions in the daily report.
"""
    return frontmatter(["schedule", "operator"]) + f"""# Operating Schedule

Brain Owner: {champion}
Brain Operator: {operator}
Operating profile: `{operating_profile}`

## First Two Weeks

{first_two_weeks}

## After Trust Is Established

{after_trust}
"""


def start_here_md(company: str, operating_profile: str = PROFILE_GOVERNED) -> str:
    if is_simple_team(operating_profile):
        safe_rule = f"""For normal team use, put material in `{DROP_ZONE_DIR}/` or ask the agent:

```text
Add this to the company brain.
```

The operator digest checks what changed, processes low-risk manual
contributions, and flags anything sensitive or unclear.

Connector sources still follow the governed path:

```text
approved source -> private evidence -> staged proposal -> review/automation rule -> approved note
```
"""
    else:
        safe_rule = """Nothing from raw sources becomes shared knowledge automatically. The default path is:

```text
source -> private evidence -> staged proposal -> review -> approved note
interview -> staged proposal -> review -> approved note
```
"""
    return frontmatter(["start-here", "roles", "setup"]) + f"""# Start Here

Welcome to the {company} company brain.

Operating profile: `{operating_profile}`

Install the Company Brain Harness plugin once in Claude Code or Codex. The
plugin includes the skills and helper scripts; this brain folder stores company
knowledge and system state, not the harness code.

After the plugin is installed, open Claude Code or Codex in this folder and say:

```text
I want to set up my company brain.
```

or:

```text
Run today's company brain check.
```

## Choose Your Role

| Role | Use this when |
|---|---|
| Brain Owner | You approve policy, sources, restricted access, and launch |
| Brain Operator | You run checks, review the queue, and keep the brain healthy |
| Team Member | You contribute what you know |

## First Safe Rule

{safe_rule}

## Next Files

- `owner-guide.md`
- `operator-guide.md`
- `team-member-guide.md`
- `invite-team.md`
- `today.md`
- `next-actions.md`
"""


def owner_guide_md(champion: str, operating_profile: str = PROFILE_GOVERNED) -> str:
    simple_decision = (
        f"6. Confirm whether `{DROP_ZONE_DIR}/` can auto-process clearly low-risk manual contributions.\n"
        "7. Decide what must always be flagged for review.\n"
        if is_simple_team(operating_profile) else
        "6. Keep the first two weeks human-gated unless you have a reason not to.\n"
    )
    return frontmatter(["owner-guide", "approval"]) + f"""# Owner Guide

Brain Owner: {champion}
Operating profile: `{operating_profile}`

You are accountable for trust.

## First Decisions

1. Confirm this brain root is in the right shared location.
2. Confirm restricted folder permissions.
3. Approve or edit `system/capture-policy.md`.
4. Review `system/source-registry.yml`.
5. Choose the first Brain Operator.
{simple_decision}

## Say This

```text
I am the Brain Owner. Help me review the setup.
```

## Do Not Do Yet

- Do not connect personal accounts as company sources.
- Do not auto-promote meeting, legal, HR, finance, or strategy-changing notes.
- Do not treat the `brain/restricted/` folder as secure until permissions are checked.
"""


def operator_guide_md(operator: str, operating_profile: str = PROFILE_GOVERNED) -> str:
    digest_step = (
        f"5. Scan `{DROP_ZONE_DIR}/` and refresh `{DIGESTS_DIR}/latest.md`.\n"
        "6. Process low-risk manual contributions.\n"
        "7. Review flagged sensitive or unclear items.\n"
        "8. Next three actions."
        if is_simple_team(operating_profile) else
        "5. Staged proposal review.\n"
        "6. Next three actions."
    )
    flagged_line = "- flagged drop-zone files:\n" if is_simple_team(operating_profile) else ""
    return frontmatter(["operator-guide", "daily-check"]) + f"""# Operator Guide

Brain Operator: {operator}
Operating profile: `{operating_profile}`

You keep the brain useful and safe.

## Say This

```text
Run today's company brain check.
```

## Daily Loop

1. Connection check.
2. Source registry check.
3. Brain health.
4. Brain lint.
{digest_step}

## Output The Team Needs

```text
Today's brain check: Ready / Needs review / Blocked

Needs review:
- staged notes
- proposed sources
- stale notes
- broken links
{flagged_line}

Next three actions:
1.
2.
3.
```
"""


def team_member_guide_md(operating_profile: str = PROFILE_GOVERNED) -> str:
    simple_path = f"""
## Easiest Path

Put the file, note, or exported document in `{DROP_ZONE_DIR}/` and say:

```text
I added something to the company brain folder.
```

Use the subfolders to make intent clear:

- `{DROP_ZONE_DIR}/team-contributions/`
- `{DROP_ZONE_DIR}/meeting-notes/`
- `{DROP_ZONE_DIR}/source-documents/`

Do not add personal, private, credential, HR, legal, or finance material.
""" if is_simple_team(operating_profile) else ""
    return frontmatter(["team-member-guide", "contribution"]) + """# Team Member Guide

You contribute what you know. You do not need to understand the harness.
""" + simple_path + """

## Say This

```text
I want to add what I know to the company brain.
```

## The Agent Will Ask

- What is your role?
- What decisions or workflows do you own?
- What should the company brain know about your area?
- What is stale or wrong today?
- Which tools do you use?
- Which tools are company/shared and which are personal?
- Who should review notes from your area?
- What should stay private or restricted?

## Safety

Your contributions are checked before they become trusted shared knowledge.
Low-risk manual contributions may be processed automatically when the brain is
configured for that model; sensitive or unclear material is flagged for review.
"""


def invite_team_md(company: str, operating_profile: str = PROFILE_GOVERNED) -> str:
    if is_simple_team(operating_profile):
        contribution_path = f"""If you already have a document, put it in `{DROP_ZONE_DIR}/` and tell the agent:

I added something to the company brain folder.

The agent/operator will process normal company material and flag anything
sensitive or unclear.
"""
    else:
        contribution_path = """The agent will ask a few questions and stage a proposal for review. Nothing goes
directly into shared knowledge without approval.
"""
    return frontmatter(["invite", "team"]) + f"""# Invite Team

Use this message to invite teammates into the {company} company brain.

```text
We are setting up a shared company brain so Claude, Codex, and teammates can
reuse trusted company context.

Please open Claude Code or Codex in the brain folder and say:

I want to add what I know to the company brain.

{contribution_path}
Personal accounts and private material are excluded by default.
```
"""


def today_md() -> str:
    return frontmatter(["today", "operator"]) + """# Today

Use this as the daily operator scratchpad.

## Morning Check

- [ ] connection check
- [ ] source registry check
- [ ] brain health
- [ ] brain lint
- [ ] staged queue

## Needs Review

- staged notes:
- proposed sources:
- stale notes:
- blocked setup:

## End Of Day

- [ ] next actions copied to `next-actions.md`
- [ ] owner decisions flagged
"""


def next_actions_md(operating_profile: str = PROFILE_GOVERNED) -> str:
    actions = (
        f"""1. Add the first safe company document to `{DROP_ZONE_DIR}/source-documents/`.
2. Run the drop-zone digest.
3. Review the flagged items and process low-risk notes.
""" if is_simple_team(operating_profile) else
        """1. Review capture policy.
2. Confirm restricted folder permissions.
3. Invite the first teammate to contribute.
"""
    )
    return frontmatter(["next-actions", "operator"]) + f"""# Next Actions

Keep this list short. The operator should update it after each daily check.

{actions}
"""


def index_md(name: str, description: str) -> str:
    return frontmatter(["index", slugify(name)]) + f"""# {name}

{description}

## What Belongs Here

- Add small, source-backed markdown notes.
- Link source files or source ids through provenance comments.
- Update this index when important notes are added.

## What Does Not Belong Here

- Credential values.
- Unreviewed raw dumps.
- Personal/private material.
"""


def staging_readme() -> str:
    return frontmatter(["staging", "approval"]) + """# Staging

Human approval buffer between raw material and shared knowledge.

| Folder | Purpose |
|---|---|
| `proposed/` | Candidate notes waiting for review |
| `approved/` | Reviewed notes that were promoted |
| `rejected/` | Notes rejected as personal, irrelevant, unsafe, or wrong |
| `revise/` | Notes that need edits before approval |
| `evidence/` | Normalized private source evidence before extraction |
| `raw/` | Private raw source material retained by policy for audit or deeper review |

No proposed note becomes shared knowledge until approved.
Raw files are not shared knowledge and should not be indexed by default.
"""


def add_to_brain_readme(company: str) -> str:
    return frontmatter(["add-to-brain", "team", "intake"]) + f"""# Add To Brain

Use this folder when a teammate wants the {company} company brain to consider a
document, note, transcript excerpt, process, or source reference.

## How To Use It

1. Put the file in the clearest subfolder.
2. Open Claude Code or Codex in the brain root.
3. Say:

```text
I added something to the company brain folder.
```

The operator digest will list new material, process low-risk company knowledge,
and flag sensitive or unclear items.

## Subfolders

| Folder | Use for |
|---|---|
| `team-contributions/` | Role knowledge, workflows, SOPs, stale-fact corrections |
| `meeting-notes/` | Meeting notes or transcript excerpts intentionally added by a teammate |
| `source-documents/` | Company documents, exports, decks, PDFs, customer-approved docs |

## Do Not Add

- credentials, API keys, tokens, passwords, or secrets
- personal/private emails, messages, calendars, or meeting dumps
- HR, legal, finance, payroll, compensation, or owner-only material
- broad connector exports that should be governed by `system/source-registry.yml`

If you are unsure, ask the agent before adding it.
"""


def drop_zone_subfolder_readme(name: str, description: str) -> str:
    return frontmatter(["add-to-brain", slugify(name)]) + f"""# {name}

{description}

Keep file names descriptive and use lowercase kebab-case when you create new
markdown files. Do not put personal, private, credential, HR, legal, finance, or
restricted material here.
"""


def digest_readme() -> str:
    return frontmatter(["digest", "operator"]) + f"""# Digests

Operator digests summarize what changed in `{DROP_ZONE_DIR}/` and what needs
review. They are operational status, not final shared knowledge.

Run:

```bash
python3 <plugin-root>/bin/add-to-brain-digest.py --root "$BRAIN_ROOT" --write
```

The latest digest is written to `latest.md`.
"""


def latest_digest_md() -> str:
    return frontmatter(["digest", "operator"]) + f"""# Latest Add-To-Brain Digest

No digest has been generated yet.

Run:

```bash
python3 <plugin-root>/bin/add-to-brain-digest.py --root "$BRAIN_ROOT" --write
```
"""


def simple_team_profile_md() -> str:
    return frontmatter(["operating-profile", "simple-team"]) + f"""# Simple Team Operating Profile

This profile is for teams that want the company brain to be easy to operate
before they have a formal knowledge-management process.

## Promise

Team members can use plain English or a shared folder:

```text
I added something to the company brain folder.
```

The agent/operator handles scanning, routing, digesting, and low-risk updates.

## What Is Automated

- scan `{DROP_ZONE_DIR}/`
- write `{DIGESTS_DIR}/latest.md`
- process clearly low-risk manual contributions
- flag sensitive, private, or unclear items
- keep source connectors behind `source-registry.yml`

## What Is Not Automated By Default

- personal inbox, calendar, meeting recorder, chat, or CRM capture
- restricted-folder inspection
- credential storage
- legal, HR, finance, payroll, compensation, or owner-only promotion
- broad raw transcript/email/export ingestion

## Operating Loop

1. Team member drops a file or asks the agent to add material.
2. Operator runs the digest.
3. Agent processes low-risk company material into curated notes.
4. Sensitive or unclear items stay flagged for review.
5. Owner reviews exceptions and adjusts policy over time.
"""


def source_sync_state() -> str:
    return json.dumps({
        "schema_version": "1.0",
        "sources": {},
    }, indent=2, sort_keys=True) + "\n"


def planned_files(
    company: str,
    champion: str,
    operator: str,
    operating_profile: str = PROFILE_GOVERNED,
) -> dict[str, str]:
    files: dict[str, str] = {
        "CLAUDE.md": root_claude(company, champion, operating_profile),
        "start-here.md": start_here_md(company, operating_profile),
        "owner-guide.md": owner_guide_md(champion, operating_profile),
        "operator-guide.md": operator_guide_md(operator, operating_profile),
        "team-member-guide.md": team_member_guide_md(operating_profile),
        "invite-team.md": invite_team_md(company, operating_profile),
        "today.md": today_md(),
        "next-actions.md": next_actions_md(operating_profile),
        "company-brain.yml": company_brain_yml(company, operating_profile),
        f"{CONVENTIONS_DIR}/README.md": index_md(CONVENTIONS_DIR, "Operating manual for this company brain."),
        f"{CONVENTIONS_DIR}/capture-policy.md": capture_policy(company, operating_profile),
        f"{CONVENTIONS_DIR}/connections.md": connections_doc(operating_profile),
        f"{CONVENTIONS_DIR}/flows.md": harness_flows(operating_profile),
        f"{CONVENTIONS_DIR}/status.md": harness_status(operating_profile),
        f"{CONVENTIONS_DIR}/naming-conventions.md": naming_conventions_md(),
        f"{CONVENTIONS_DIR}/source-registry.yml": source_registry(company, champion, operating_profile),
        f"{CONVENTIONS_DIR}/source-sync-state.json": source_sync_state(),
        f"{CONVENTIONS_DIR}/team.yml": team_yml(champion, operator),
        f"{CONVENTIONS_DIR}/schedule.md": schedule_md(champion, operator, operating_profile),
        f"{STAGING_DIR}/README.md": staging_readme(),
        f"{STAGING_DIR}/approval-ledger.jsonl": json.dumps({
            "event": "ledger_initialized",
            "schema_version": "1.0",
            "created_at": date.today().isoformat(),
        }) + "\n",
    }
    for folder, description in FOLDERS.items():
        files[f"{folder}/README.md"] = index_md(folder, description)
    for sub in ("proposed", "approved", "rejected", "revise"):
        files[f"{STAGING_DIR}/{sub}/README.md"] = index_md(sub, f"Staging queue folder for {sub} notes.")
    files[f"{STAGING_DIR}/evidence/README.md"] = index_md(
        "evidence",
        "Private normalized source evidence for extraction. This is not final brain knowledge.",
    )
    files[f"{STAGING_DIR}/raw/README.md"] = index_md(
        "raw",
        "Private raw source evidence retained by source policy. This is not final brain knowledge and should not be broadly indexed.",
    )
    if is_simple_team(operating_profile):
        files[f"{DROP_ZONE_DIR}/README.md"] = add_to_brain_readme(company)
        files[f"{DROP_ZONE_DIR}/team-contributions/README.md"] = drop_zone_subfolder_readme(
            "Team Contributions",
            "Role knowledge, workflows, SOPs, corrections, and other teammate-authored contributions.",
        )
        files[f"{DROP_ZONE_DIR}/meeting-notes/README.md"] = drop_zone_subfolder_readme(
            "Meeting Notes",
            "Meeting notes or transcript excerpts that a teammate intentionally adds for company-brain use.",
        )
        files[f"{DROP_ZONE_DIR}/source-documents/README.md"] = drop_zone_subfolder_readme(
            "Source Documents",
            "Company documents, exports, PDFs, decks, and approved source material for operator review.",
        )
        files[f"{DIGESTS_DIR}/README.md"] = digest_readme()
        files[f"{DIGESTS_DIR}/latest.md"] = latest_digest_md()
        files[f"{CONVENTIONS_DIR}/simple-team-operating-profile.md"] = simple_team_profile_md()
    return files


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Scaffold a portable Company Brain root.")
    parser.add_argument("--root", default=DEFAULT_ROOT, help="target brain root")
    parser.add_argument("--company-name", required=True)
    parser.add_argument("--champion", default="brain-owner", help="Brain Owner name")
    parser.add_argument("--operator", default="brain-operator", help="Brain Operator name")
    parser.add_argument(
        "--operating-profile",
        choices=OPERATING_PROFILES,
        default=PROFILE_GOVERNED,
        help="operating model to scaffold: governed approval flow or simple team drop-zone automation",
    )
    parser.add_argument("--write", action="store_true", help="actually create files; default is preview-only")
    parser.add_argument("--force", action="store_true", help="overwrite existing generated files")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    root = Path(args.root).expanduser().resolve()
    files = planned_files(args.company_name, args.champion, args.operator, args.operating_profile)
    existing = [rel for rel in files if (root / rel).exists()]
    if args.write and existing and not args.force:
        print(json.dumps({"error": "target files already exist", "files": existing[:20]}), file=sys.stderr)
        return 1

    if args.write:
        root.mkdir(parents=True, exist_ok=True)
        for rel, body in files.items():
            path = root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(body, encoding="utf-8")

    result = {
        "action": "wrote" if args.write else "would-write",
        "root": str(root),
        "operating_profile": args.operating_profile,
        "files": sorted(files),
        "file_count": len(files),
        "note": None if args.write else "preview only; rerun with --write to persist",
    }
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"{result['action']} {result['file_count']} files under {root}")
        for rel in result["files"]:
            print(f"- {rel}")
        if not args.write:
            print("preview only; rerun with --write to persist")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
