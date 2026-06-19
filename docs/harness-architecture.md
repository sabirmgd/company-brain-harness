# Harness Architecture

This document explains the architecture of the Company Brain Harness and the
responsibility of each layer.

## System Shape

```text
Claude / Codex / agent
        |
        v
installed Company Brain Harness plugin
        |
        +-- skills/       role-based workflows and lower-level actions
        +-- bin/          executable policy and filesystem operations
        +-- references/   shared contract for skills and agents
        |
        v
filesystem-backed brain root
        |
        +-- CLAUDE.md / routing file
        +-- company-brain.yml
        +-- conventions/
        +-- source-registry.yml
        +-- staging/
        +-- routed knowledge folders
```

The harness is deliberately small. It is not a database, a RAG service, or a
connector platform yet. It is the portable operating contract that lets humans
and agents safely build a company memory system from files.

## Layer 1: Product Category

Decision: define the product as Company Brain Harness.

Reasoning:

- "Second brain" sounds individual and private.
- The reusable category is organizational memory with source governance,
  team roles, review, freshness, and agent-readable routing.

Consequence:

- Docs and skills talk about teams, source owners, review owners, and company
  sources.
- Customer-specific industry assumptions do not belong in generic harness code.

## Layer 2: Storage Backend

Decision: use a filesystem-backed root.

Supported roots:

- mounted Google Drive
- git repo
- shared volume
- local directory

Reasoning:

- Claude and Codex can already read/write files.
- Markdown is inspectable, portable, and easy to diff.
- Google Drive is useful for teams, but should not be hardcoded as the product.

Consequence:

- All CLIs accept `--root`.
- Root resolution also supports `BRAIN_ROOT`, `COMPANY_BRAIN_ROOT`, and the
  legacy `COMPANY_OS_ROOT`.
- Config lives in `company-brain.yml` / `company-os.yml`.

## Layer 3: Plugin Distribution

Decision: ship one plugin that works in Claude and Codex.

Reasoning:

- Local-only skills under `~/.claude/skills` or `~/.codex/skills` are hard to
  version, review, and distribute.
- A plugin can carry skills, CLIs, references, and manifest metadata together.
- Both Claude and Codex users should get the same workflows.

Consequence:

- `plugins/company-brain-harness/.claude-plugin/plugin.json` defines Claude
  metadata.
- `plugins/company-brain-harness/.codex-plugin/plugin.json` defines Codex
  metadata.
- `skills/` uses portable `SKILL.md` files with small OpenAI interface YAML.

## Layer 4: Skills

Decision: expose role-based workflows as the public front door, with lower-level
action skills underneath.

Public entry skills:

- `brain-start`
- `brain-owner`
- `brain-operator`
- `brain-contribute`
- `source-setup`
- `source-sync`

Lower-level action skills:

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

Reasoning:

- Skills are the UX layer for humans using Claude or Codex.
- Skill instructions keep the same workflow portable across agents.
- Skills should reference the brain root and CLIs instead of duplicating company
  facts inside prompt files.
- Most users should not need to know which CLI or lower-level skill exists.

Consequence:

- A new user can say "I want to set up my company brain" and be routed through
  `brain-start`.
- A teammate can say `$brain-contribute` or `/company-brain-harness:brain-contribute`
  and get a guided contribution flow.
- Skills stay generic and rely on the active brain root for company-specific
  context.

## Layer 5: CLIs

Decision: implement executable behavior as stdlib Python CLIs.

Reasoning:

- Skills are instructions; CLIs are enforcement.
- Stdlib Python avoids npm/pip setup and runs on fresh machines.
- Shellable tools make smoke tests and future automation straightforward.

CLI responsibilities:

| CLI | Responsibility |
|---|---|
| `brain-setup.py` | Create the portable scaffold |
| `connections-check.py` | Check root, routing, and optional connector readiness |
| `source-registry-check.py` | Enforce source-instance capture eligibility |
| `confluence-export.py` | Export scoped Confluence pages into normalized JSONL |
| `fireflies-export.py` | Export scoped Fireflies meeting summaries into normalized JSONL |
| `repo-map-export.py` | Export local git repo maps into normalized JSONL |
| `source-pull.py` | Pull normalized connector records into private evidence |
| `source-extract.py` | Extract latest allowed artifacts from evidence into staged proposals |
| `source-sync-state.py` | Inspect or update source cursors and dedupe state |
| `brain-health.py` | Score root readiness |
| `brain-lint.py` | Detect stale, unprovenanced, duplicate, broken, or contradictory notes |
| `brain-schedule.py` | Generate operating cadence |
| `stage-brain-note.py` | Create staged proposals |
| `approve-staged-note.py` | Record approve/reject/revise decisions |
| `promote-to-brain.py` | Promote approved notes to final destinations |

## Layer 6: Brain Root Contract

Decision: every root needs routing, config, conventions, staging, and indexes.

Generated scaffold:

```text
CLAUDE.md
START_HERE.md
OWNER_GUIDE.md
OPERATOR_GUIDE.md
TEAM_MEMBER_GUIDE.md
INVITE_TEAM.md
TODAY.md
NEXT_ACTIONS.md
company-brain.yml
00_Company_Brain_Conventions/
  README.md
  CAPTURE_POLICY.md
  CONNECTIONS.md
  HARNESS_FLOWS.md
  HARNESS_STATUS.md
  SCHEDULE.md
  source-registry.yml
  source-sync-state.json
  team.yml
  90_Staging/
    evidence/
Context/
Daily/
Projects/
Departments/
Intelligence/
Resources/
Team/
Skills/
Restricted/
Archive/
```

Reasoning:

- Agents need one root routing file.
- Humans need role guides at the root.
- Humans need a conventions folder.
- Writes need a staging area.
- Teams need a source registry and team map.
- Source pulls need cursor/dedupe state and private evidence staging.
- Sensitive material needs an explicit restricted route.

## Layer 7: Source Registry

Decision: source instance is the unit of capture.

Wrong:

```text
Capture Fireflies.
Capture Apollo.
Capture Gmail.
```

Right:

```text
source_id: company-fireflies
connector: fireflies
control_tier: company_owned
status: approved_staging_only
capture.allowed: true
review_owner: Brain Owner
```

Reasoning:

- One connector can have many accounts, workspaces, channels, inboxes, or API
  keys.
- Personal accounts can contain private material.
- Teams need to know who owns each source and what the source may produce.

Consequence:

- `source-registry-check.py --for-capture` refuses personal, unknown, proposed,
  excluded, suspended, or retired sources.
- Connector adapters must select a specific source id before running.
- Legacy `brain_artifacts` registry entries are still accepted, but new
  registries should use `artifact_policy`.

## Layer 8: Capture And Promotion

Decision: raw source access is not brain access.

Default flow:

```text
approved source
  -> private evidence
  -> extracted staged proposal
  -> human or owner review
  -> approve/reject/revise
  -> final brain note

interview/document
  -> staged proposal
  -> human or owner review
  -> approve/reject/revise
  -> final brain note
```

Reasoning:

- Raw transcripts, emails, and exports are noisy and can be sensitive.
- A company brain should contain reusable knowledge with provenance.
- Review is how the team builds trust in the system.

Consequence:

- `source-pull.py` stores only scoped, non-private evidence.
- `source-extract.py` stages only allowed artifact types.
- `stage-brain-note.py` previews by default.
- `--write` is required to create a staged proposal.
- Final promotion goes through the approval ledger.

## Layer 9: Safety

Decision: default to no-surprise, no-broad-capture behavior.

Safety controls:

- preview by default
- `--write` required
- path traversal blocked
- root-level content writes refused
- restricted prefixes refused
- secrets not stored in brain
- personal connectors excluded
- raw material not promoted by default
- provenance required
- two tags required for staged/promoted notes

Reasoning:

- Shared company memory is high trust and high leverage.
- Mistaken writes and broad capture damage trust quickly.
- The harness should be safe before it is automated.

## Layer 10: Team Operations

Decision: operate as a team system with roles and cadence.

Public roles:

- Brain Owner: policy, source approval, adoption
- Brain Operator: daily checks, schedules, staging queue
- Team Member: knowledge contribution and corrections

First two-week cadence:

```text
connections -> sources -> pull/extract -> health -> lint -> staged queue -> punch list
```

Reasoning:

- Team adoption depends on visible review and correction.
- Every teammate should be able to see what feeds the brain.
- The brain should get better as people use it.

## Layer 11: Freshness And Evolution

Decision: knowledge must be maintained, not only captured.

Principles:

- use `last_verified`
- keep provenance comments
- update canonical notes instead of creating duplicates
- mark or archive deprecated knowledge
- route contradictions to source owners
- lint regularly

Reasoning:

- Company context changes.
- Stale docs are worse when agents rely on them confidently.
- Freshness and provenance are part of the trust model.

## Layer 12: Testing And Release

Decision: release only through a reproducible validation script.

Release gate:

```bash
bash scripts/validate.sh
```

What it proves:

- Python compiles.
- Skills have required structure.
- plugin manifests validate.
- smoke test passes on a synthetic generic root.
- setup, source checks, schedule, lint, staging, approval, and restricted refusal
  work together.

Reasoning:

- The harness is generic only if synthetic non-customer-specific smoke tests pass.
- Installability is part of product quality.
- Safety claims need executable proof.
