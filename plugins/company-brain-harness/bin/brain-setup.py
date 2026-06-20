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
CONVENTIONS_DIR = "00_Company_Brain_Conventions"
STAGING_DIR = f"{CONVENTIONS_DIR}/90_Staging"
FOLDERS = {
    "Context": "Stable company context: strategy, ICP, voice, goals, operating principles.",
    "Daily": "Company-wide daily log: decisions, ships, incidents, blockers.",
    "Projects": "Active and completed projects with owners, specs, notes, and outcomes.",
    "Departments": "Department SOPs, role-specific guidance, and operating workflows.",
    "Intelligence": "Meetings, customer voice, market notes, competitors, decisions.",
    "Resources": "Reusable templates, prompts, frameworks, and external references.",
    "Team": "One folder per teammate: profile, daily notes, tasks, and preferences.",
    "Skills": "Company skills that reference this brain instead of duplicating context.",
    "Restricted": "Sensitive material. Excluded from default agent scans and broad team access.",
    "Archive": "Deprecated or superseded knowledge retained for auditability.",
}


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "company"


def frontmatter(tags: list[str]) -> str:
    today = date.today().isoformat()
    lines = ["---", "status: active", "tags:"]
    lines.extend(f"  - {tag}" for tag in tags)
    lines.append(f"last_verified: {today}")
    lines.extend(["---", ""])
    return "\n".join(lines)


def root_claude(company: str, champion: str) -> str:
    return f"""# {company} Company Brain

This folder is the company's shared brain: routed markdown knowledge plus source references.
Claude Code, Claude Cowork, Codex, and other agents should treat this file as the root routing contract.

## Session Startup

1. Read this file first.
2. Identify the active teammate or role.
3. Read that person's `Team/<name>/profile.md` when present.
4. Read the target folder's `00_INDEX.md` before writing there.
5. Use source registry and capture policy before touching external data.

## Knowledge Routing

| Type | Route to |
|---|---|
| Strategy, ICP, brand, goals, org context | `Context/` |
| Company daily log, ships, blockers, decisions | `Daily/` |
| Project briefs, specs, drafts, feedback | `Projects/` |
| Department SOPs and workflows | `Departments/` |
| Meetings, competitors, customer voice, decisions | `Intelligence/` |
| Reusable templates and frameworks | `Resources/` |
| Teammate profiles, preferences, tasks | `Team/<name>/` |
| Shared skills and prompt workflows | `Skills/` |
| Sensitive HR, legal, finance, owner-only material | `Restricted/` |

## Rules

1. Shared writes go through staging unless the Brain Owner explicitly approves direct admin edits.
2. Personal connectors are excluded by default unless narrowly delegated, scoped, approved, and registered.
3. Every org-wide source instance must exist in `{CONVENTIONS_DIR}/source-registry.yml`.
4. Source-derived notes need provenance: `<!-- src: <source-id>/<item-id> @ YYYY-MM-DD -->`.
5. Every content note needs frontmatter with `status`, `tags`, and `last_verified`.
6. Never create files at the root except routing, config, and setup guide files.
7. Never read, index, summarize, or write `Restricted/` unless the owner explicitly grants access.
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


def company_brain_yml(company: str) -> str:
    return f"""schema_version: "1.0"
kind: company_brain_config
company:
  name: "{company}"
  implementation_status: setup
brain:
  routing_file: CLAUDE.md
  conventions_dir: {CONVENTIONS_DIR}
  staging_dir: {STAGING_DIR}
  restricted_prefixes:
    - Restricted
policy:
  capture_policy: {CONVENTIONS_DIR}/CAPTURE_POLICY.md
  require_human_approval_for_shared_writes: true
  personal_connectors_are_company_sources: false
promotion:
  preview_by_default: true
  require_write_flag: true
  require_provenance: true
  require_two_tags: true
evidence:
  normalized_dir: {STAGING_DIR}/evidence
  raw_dir: {STAGING_DIR}/raw
  raw_is_shared_knowledge: false
  raw_requires_source_policy: true
health:
  priority_folders:
    - Context
    - Daily
    - Projects
    - Intelligence
    - Team
"""


def source_registry(company: str, champion: str) -> str:
    source_id = slugify(company)
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
        - Restricted
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
      default_destination: Intelligence/meetings
      staging_destination: {STAGING_DIR}
      restricted_prefixes:
        - Restricted
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
      default_destination: Intelligence/gtm
      staging_destination: {STAGING_DIR}
      restricted_prefixes:
        - Restricted
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
      default_destination: Resources/confluence
      staging_destination: {STAGING_DIR}
      restricted_prefixes:
        - Restricted
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
      default_destination: Intelligence/accounts
      staging_destination: {STAGING_DIR}
      restricted_prefixes:
        - Restricted
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
        - Restricted
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


def connections_doc() -> str:
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


def capture_policy(company: str) -> str:
    return frontmatter(["capture-policy", "privacy", "governance"]) + f"""# Capture Policy

This policy controls what may enter the {company} company brain.

## Default Posture

- Company-owned sources can feed the shared brain after approval.
- Customer-owned sources can feed only that customer's brain after approval.
- Personal sources are excluded by default.
- Raw material stays in private raw evidence staging unless source policy says otherwise.
- Normalized evidence is used for extraction and review; raw evidence is retained for audit and deeper source review.
- Curated notes enter the brain only after review or an explicitly approved automation rule.

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

HR, legal, finance, fundraising, compensation, private customer data, and owner-only strategy route to `Restricted/` or stay out.

## Approval Checklist

- [ ] Brain Owner approves this policy.
- [ ] Source registry is valid.
- [ ] Restricted folder permissions are correct.
- [ ] Review owner is named.
- [ ] Retention and purge rules are chosen.
"""


def harness_flows() -> str:
    return frontmatter(["harness", "flows", "team"]) + """# Harness Flows

## Setup

Run `brain-setup` once per company brain. Then run `brain-health`, `sources-check`, and `brain-lint`.

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
`90_Staging/raw/` and the normalized evidence receives a private pointer.
Then use `source-extract.py` to create staged proposals. Cursor and dedupe state
lives in `source-sync-state.json`.

## Maintenance

Daily: connection check, source registry check, approved source pull/extract, health, lint, staged queue review.
Weekly: stale-note review, source ownership review, routing cleanup.
Monthly: permissions, retention, auto-promotion, and adoption review.
"""


def harness_status() -> str:
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


def schedule_md(champion: str, operator: str) -> str:
    return frontmatter(["schedule", "operator"]) + f"""# Operating Schedule

Brain Owner: {champion}
Brain Operator: {operator}

## First Two Weeks

- Run checks manually each morning.
- Pull approved source records into private evidence.
- Extract allowed artifacts into staged proposals.
- Stage every proposed note.
- Require human approval before promotion.
- Keep meeting-derived and sensitive material human-approved.

## After Trust Is Established

- Schedule daily checks.
- Allow approved sources to create staged proposals.
- Track source cursors and hashes in `source-sync-state.json`.
- Consider autonomous promotion only for explicitly low-risk categories.
- Keep source registry, lint, and restricted permissions in the daily report.
"""


def start_here_md(company: str) -> str:
    return frontmatter(["start-here", "roles", "setup"]) + f"""# Start Here

Welcome to the {company} company brain.

You do not need to know the harness commands. Open Claude Code or Codex in this
folder and say:

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

Nothing from raw sources becomes shared knowledge automatically. The default path is:

```text
source -> private evidence -> staged proposal -> review -> approved note
interview -> staged proposal -> review -> approved note
```

## Next Files

- `OWNER_GUIDE.md`
- `OPERATOR_GUIDE.md`
- `TEAM_MEMBER_GUIDE.md`
- `INVITE_TEAM.md`
- `TODAY.md`
- `NEXT_ACTIONS.md`
"""


def owner_guide_md(champion: str) -> str:
    return frontmatter(["owner-guide", "approval"]) + f"""# Owner Guide

Brain Owner: {champion}

You are accountable for trust.

## First Decisions

1. Confirm this brain root is in the right shared location.
2. Confirm restricted folder permissions.
3. Approve or edit `00_Company_Brain_Conventions/CAPTURE_POLICY.md`.
4. Review `00_Company_Brain_Conventions/source-registry.yml`.
5. Choose the first Brain Operator.
6. Keep the first two weeks human-gated unless you have a reason not to.

## Say This

```text
I am the Brain Owner. Help me review the setup.
```

## Do Not Do Yet

- Do not connect personal accounts as company sources.
- Do not auto-promote meeting, legal, HR, finance, or strategy-changing notes.
- Do not treat the `Restricted/` folder as secure until permissions are checked.
"""


def operator_guide_md(operator: str) -> str:
    return frontmatter(["operator-guide", "daily-check"]) + f"""# Operator Guide

Brain Operator: {operator}

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
5. Staged proposal review.
6. Next three actions.

## Output The Team Needs

```text
Today's brain check: Ready / Needs review / Blocked

Needs review:
- staged notes
- proposed sources
- stale notes
- broken links

Next three actions:
1.
2.
3.
```
"""


def team_member_guide_md() -> str:
    return frontmatter(["team-member-guide", "contribution"]) + """# Team Member Guide

You contribute what you know. You do not need to understand the harness.

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

Your answers become staged proposals first. A reviewer approves, rejects, or
asks for revisions before anything becomes shared knowledge.
"""


def invite_team_md(company: str) -> str:
    return frontmatter(["invite", "team"]) + f"""# Invite Team

Use this message to invite teammates into the {company} company brain.

```text
We are setting up a shared company brain so Claude, Codex, and teammates can
reuse trusted company context.

Please open Claude Code or Codex in the brain folder and say:

I want to add what I know to the company brain.

The agent will ask a few questions and stage a proposal for review. Nothing goes
directly into shared knowledge without approval. Personal accounts and private
material are excluded by default.
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

- [ ] next actions copied to `NEXT_ACTIONS.md`
- [ ] owner decisions flagged
"""


def next_actions_md() -> str:
    return frontmatter(["next-actions", "operator"]) + """# Next Actions

Keep this list short. The operator should update it after each daily check.

1. Review capture policy.
2. Confirm restricted folder permissions.
3. Invite the first teammate to contribute.
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


def source_sync_state() -> str:
    return json.dumps({
        "schema_version": "1.0",
        "sources": {},
    }, indent=2, sort_keys=True) + "\n"


def planned_files(company: str, champion: str, operator: str) -> dict[str, str]:
    files: dict[str, str] = {
        "CLAUDE.md": root_claude(company, champion),
        "START_HERE.md": start_here_md(company),
        "OWNER_GUIDE.md": owner_guide_md(champion),
        "OPERATOR_GUIDE.md": operator_guide_md(operator),
        "TEAM_MEMBER_GUIDE.md": team_member_guide_md(),
        "INVITE_TEAM.md": invite_team_md(company),
        "TODAY.md": today_md(),
        "NEXT_ACTIONS.md": next_actions_md(),
        "company-brain.yml": company_brain_yml(company),
        f"{CONVENTIONS_DIR}/README.md": index_md(CONVENTIONS_DIR, "Operating manual for this company brain."),
        f"{CONVENTIONS_DIR}/CAPTURE_POLICY.md": capture_policy(company),
        f"{CONVENTIONS_DIR}/CONNECTIONS.md": connections_doc(),
        f"{CONVENTIONS_DIR}/HARNESS_FLOWS.md": harness_flows(),
        f"{CONVENTIONS_DIR}/HARNESS_STATUS.md": harness_status(),
        f"{CONVENTIONS_DIR}/source-registry.yml": source_registry(company, champion),
        f"{CONVENTIONS_DIR}/source-sync-state.json": source_sync_state(),
        f"{CONVENTIONS_DIR}/team.yml": team_yml(champion, operator),
        f"{CONVENTIONS_DIR}/SCHEDULE.md": schedule_md(champion, operator),
        f"{STAGING_DIR}/README.md": staging_readme(),
        f"{STAGING_DIR}/approval-ledger.jsonl": json.dumps({
            "event": "ledger_initialized",
            "schema_version": "1.0",
            "created_at": date.today().isoformat(),
        }) + "\n",
    }
    for folder, description in FOLDERS.items():
        files[f"{folder}/00_INDEX.md"] = index_md(folder, description)
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
    return files


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Scaffold a portable Company Brain root.")
    parser.add_argument("--root", default=DEFAULT_ROOT, help="target brain root")
    parser.add_argument("--company-name", required=True)
    parser.add_argument("--champion", default="brain-owner", help="Brain Owner name")
    parser.add_argument("--operator", default="brain-operator", help="Brain Operator name")
    parser.add_argument("--write", action="store_true", help="actually create files; default is preview-only")
    parser.add_argument("--force", action="store_true", help="overwrite existing generated files")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    root = Path(args.root).expanduser().resolve()
    files = planned_files(args.company_name, args.champion, args.operator)
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
