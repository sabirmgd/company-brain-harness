# Company Brain Harness

Portable harness for building and operating a team-owned company brain that
Claude, Codex, and other agents can read, maintain, and safely grow.

The product category is Company Brain Harness: source-governed organizational
memory for humans and agents.

## What This Is

The harness is the operating layer around a filesystem-backed knowledge root. It
provides:

- a reusable Claude/Codex plugin
- Agent Skills for setup, intake, onboarding, meeting capture, approval,
  scheduling, health, lint, sources, and repo-aware POCs
- preview-first CLIs for setup, validation, staging, approval, promotion, lint,
  and scheduling
- templates for capture policy, source registry, team onboarding, and operating
  cadence
- a testable release gate that proves the harness works against a generic brain
  root

The brain root can be:

- Google Drive for Desktop
- a git repo
- a shared volume
- a local directory
- any other filesystem-backed root

Google Drive is one backend. It is not the product.

## Core Promise

A team can install the plugin, point Claude or Codex at a brain root, scaffold a
safe structure, register org-wide sources, stage proposed knowledge, approve
curated notes, and keep the brain fresh over time.

The harness does not populate company knowledge by itself. Each company's team
members supply the real context through onboarding, intake, approved source
capture, and review.

## Simple User Experience

The intended first interaction is not a command. It is a sentence:

```text
I want to set up my company brain.
```

Claude or Codex should route that to `brain-start`, ask which role the user is
playing, and run the lower-level harness tools in the background.

Public roles:

| Role | What they do |
|---|---|
| Brain Owner | Approves setup, policy, restricted access, sources, and pilot launch |
| Brain Operator | Runs daily checks, reviews queue, and keeps the brain healthy |
| Team Member | Contributes role knowledge and flags stale/private material |

The CLIs remain available for developers and automation, but the normal user
flow should be role-based and guided.

## Layer Decisions

| Layer | Decision | Why |
|---|---|---|
| Product category | Company Brain Harness | The generic product is team/company memory with source governance |
| Storage | Filesystem-backed brain root | Works with Drive, git, shared volumes, and local folders |
| Distribution | One Claude/Codex plugin | Versioned, installable, reviewable, team-distributable |
| Skills | Shared `SKILL.md` surfaces | Same workflows work in Claude and Codex |
| CLIs | Stdlib Python, preview-first | Portable, easy to validate, no dependency setup |
| Writes | `--write` required for side effects | Prevents accidental shared-brain mutation |
| Knowledge flow | source/interview -> staging -> approval -> brain | Raw material is not automatically shared knowledge |
| Source model | Source instance, not connector type | "Fireflies" or "Apollo" is too broad; exact workspace/account must be approved |
| Team model | Brain Owner, Brain Operator, Team Member | A company brain is not one person's private second brain |
| Safety | Restricted prefixes skipped and refused by default | Sensitive HR/legal/finance/owner material must not be broadly indexed |
| Freshness | `last_verified`, provenance, lint | Company knowledge decays unless checked |
| Scheduling | Human-gated first, autonomous later | Trust the staging/review loop before automation |
| Productization | Policy and source registry are customer-facing primitives | Trust and governance must be part of onboarding |
| User experience | Role-based front door | Users say what they want; agents run the harness internally |

Full details: [docs/harness-architecture.md](docs/harness-architecture.md) and
[docs/decision-log.md](docs/decision-log.md).

## Repository Layout

```text
.
├── .agents/plugins/marketplace.json          # Codex marketplace
├── .claude-plugin/marketplace.json           # Claude marketplace
├── docs/                                     # Published harness docs
├── plugins/company-brain-harness/
│   ├── .codex-plugin/plugin.json             # Codex plugin manifest
│   ├── .claude-plugin/plugin.json            # Claude plugin manifest
│   ├── bin/                                  # Portable CLIs
│   ├── references/                           # Contract used by skills
│   └── skills/                               # Shared Claude/Codex skills
└── scripts/
    ├── validate.sh                           # Release gate
    ├── validate_skills.py                    # Skill structure checks
    ├── validate_skill_routing.py             # Plain-English skill trigger checks
    └── smoke-test.sh                         # Generic portability smoke test
```

## Install

From GitHub:

```bash
claude plugin marketplace add sabirmgd/company-brain-harness
claude plugin install company-brain-harness@company-brain

codex plugin marketplace add sabirmgd/company-brain-harness
codex plugin add company-brain-harness@company-brain
```

From a local checkout:

```bash
git clone git@github.com:sabirmgd/company-brain-harness.git
cd company-brain-harness

claude plugin marketplace add .
claude plugin install company-brain-harness@company-brain

codex plugin marketplace add .
codex plugin add company-brain-harness@company-brain
```

Claude Code can also test the plugin directly:

```bash
claude --plugin-dir ./plugins/company-brain-harness
```

## Fast Start For Users

After install, open Claude Code or Codex and say:

```text
I want to set up my company brain.
```

Or invoke the entry skill directly:

```text
/company-brain-harness:brain-start
```

```text
$brain-start
```

The agent will ask whether you are the Brain Owner, Brain Operator, or a Team
Member, then guide only the relevant next steps.

## Plain-English Use Cases

Users do not need to call skills manually. The skill metadata is written so
Claude and Codex can route common sentences:

| User says | Expected route |
|---|---|
| "I want to set up my company brain." | `brain-start`, then `brain-owner` |
| "I own this brain and want to launch it." | `brain-owner` |
| "Run today's brain check." | `brain-operator` |
| "What needs review?" | `brain-operator` or `approve-brain-notes` |
| "I want to add what I know." | `brain-contribute` |
| "Add this doc to the brain." | `brain-intake` |
| "Process this meeting transcript." | `meeting-to-brain` |
| "Can Slack or Gmail feed the brain?" | `sources-check` |
| "Schedule the daily check." | `brain-schedule` |
| "What is outdated?" | `brain-lint` |
| "Where should this POC live?" | `repo-aware-poc` |

More examples: [docs/skill-routing.md](docs/skill-routing.md).

## Developer And Automation Path

Set the brain root:

```bash
export BRAIN_ROOT="/path/to/company-brain-root"
```

Preview a new scaffold:

```bash
python3 plugins/company-brain-harness/bin/brain-setup.py \
  --root "$BRAIN_ROOT" \
  --company-name "Acme Co" \
  --champion "Brain Owner" \
  --operator "Brain Operator"
```

Write the scaffold:

```bash
python3 plugins/company-brain-harness/bin/brain-setup.py \
  --root "$BRAIN_ROOT" \
  --company-name "Acme Co" \
  --champion "Brain Owner" \
  --operator "Brain Operator" \
  --write
```

Run readiness checks:

```bash
python3 plugins/company-brain-harness/bin/connections-check.py --root "$BRAIN_ROOT" --live
python3 plugins/company-brain-harness/bin/source-registry-check.py --root "$BRAIN_ROOT"
python3 plugins/company-brain-harness/bin/brain-health.py --root "$BRAIN_ROOT"
python3 plugins/company-brain-harness/bin/brain-lint.py --root "$BRAIN_ROOT" --stale-days 30
```

## Skills

| Skill | Purpose |
|---|---|
| `brain-start` | Main entry point for setup, operation, or contribution |
| `brain-owner` | Guide owner setup decisions and approvals |
| `brain-operator` | Run daily checks and operational punch lists |
| `brain-contribute` | Help a teammate contribute knowledge safely |
| `brain-setup` | Scaffold a new team-first brain root without populating data |
| `brain-health` | Check connection, policy, and readiness |
| `source-setup` | Safely scope and approve app/workspace/account sources |
| `source-sync` | Pull approved source records into private evidence and staged proposals |
| `sources-check` | Validate source registry and capture eligibility |
| `brain-intake` | Stage documents, links, pasted text, or raw artifacts |
| `brain-onboard` | Interview teammates into staged notes |
| `meeting-to-brain` | Convert approved meeting material into staged notes |
| `approve-brain-notes` | Approve, reject, or revise staged proposals |
| `brain-schedule` | Generate a human-gated or autonomous operating schedule |
| `brain-lint` | Check freshness, provenance, dead links, duplicates, contradictions |
| `repo-aware-poc` | Ground prototypes in repo map and stack conventions |

Claude Code:

```text
/company-brain-harness:brain-start
/company-brain-harness:brain-owner
/company-brain-harness:brain-operator
/company-brain-harness:brain-contribute
/company-brain-harness:brain-setup
/company-brain-harness:brain-health
/company-brain-harness:source-setup
/company-brain-harness:source-sync
/company-brain-harness:sources-check
/company-brain-harness:brain-intake
/company-brain-harness:brain-onboard
/company-brain-harness:meeting-to-brain
/company-brain-harness:approve-brain-notes
/company-brain-harness:brain-schedule
/company-brain-harness:brain-lint
/company-brain-harness:repo-aware-poc
```

Codex:

```text
$brain-start
$brain-owner
$brain-operator
$brain-contribute
$brain-setup
$brain-health
$source-setup
$source-sync
$sources-check
$brain-intake
$brain-onboard
$meeting-to-brain
$approve-brain-notes
$brain-schedule
$brain-lint
$repo-aware-poc
```

## CLIs

All CLIs resolve the brain root from:

1. explicit `--root`
2. `BRAIN_ROOT`
3. `COMPANY_BRAIN_ROOT`
4. `COMPANY_OS_ROOT` legacy alias
5. current working directory

They also read `company-brain.yml` / `company-os.yml` when present.

| CLI | Purpose | Writes? |
|---|---|---|
| `brain-setup.py` | Scaffold a new team brain | Only with `--write` |
| `connections-check.py` | Check root, routing, optional connectors | No |
| `source-registry-check.py` | Validate source instances and capture eligibility | No |
| `confluence-export.py` | Export scoped Confluence pages to normalized JSONL | No brain writes |
| `fireflies-export.py` | Export scoped Fireflies meeting summaries to normalized JSONL | No brain writes |
| `repo-map-export.py` | Export local git repo maps to normalized JSONL | No brain writes |
| `source-pull.py` | Pull normalized source records into private evidence | Only with `--write` |
| `source-extract.py` | Extract latest allowed source artifacts into staged proposals | Only with `--write` |
| `source-sync-state.py` | Inspect or update source cursor/dedupe state | Only with `--write` for cursor updates |
| `brain-health.py` | Score readiness and folder health | No |
| `brain-lint.py` | Check stale notes, provenance, links, duplicates | No |
| `brain-schedule.py` | Generate `SCHEDULE.md` | Only with `--write` |
| `stage-brain-note.py` | Create staged proposal | Only with `--write` |
| `approve-staged-note.py` | Approve/reject/revise proposals | Only with `--write` |
| `promote-to-brain.py` | Promote approved note to final folder | Only with `--write` |

## Safety Model

The harness defaults to no-surprise behavior:

- preview by default
- `--write` required for side effects
- root-level content writes refused
- path traversal refused
- restricted prefixes refused by default
- secrets must be referenced, never stored
- personal connectors are excluded by default
- raw transcripts/emails/exports are not shared knowledge by default
- raw sidecars, when allowed by source policy, live under `90_Staging/raw/`
- staged proposals require provenance and at least two tags
- final promotion requires explicit approval

## Source Registry

A connector is not a source. A specific approved account, workspace, channel,
folder, org, inbox, calendar, or API key reference is a source.

Examples:

- `company-fireflies`
- `company-shared-apollo`
- `company-google-workspace-engine`
- `company-github-org`
- `customer-acme-slack-selected-channels`
- `personal-fireflies-example` with `status: excluded`

Before connector capture:

```bash
python3 plugins/company-brain-harness/bin/source-registry-check.py \
  --root "$BRAIN_ROOT" \
  --source-id "<source-id>" \
  --for-capture
```

## Team Operating Model

The default roles are:

- Brain Owner: owns policy, source approval, review standards, and adoption
- Brain Operator: runs checks, lint, staging queue, and schedule
- Team Member: contributes role knowledge and source suggestions

First two weeks:

```text
connections -> sources -> health -> lint -> staged queue -> punch list
```

Keep the first pilot human-gated. After the staging queue is trusted, scheduled
checks and approved-source staging can run without constant supervision.
Auto-promotion should stay narrow and explicitly approved.

## Validation

Run the release gate:

```bash
bash scripts/validate.sh
```

This performs:

- Python compile
- skill structure validation
- Codex plugin manifest validation when available
- Claude plugin and marketplace validation when available
- generic smoke test

The smoke test proves:

- generic root support
- setup preview does not write
- setup write creates the scaffold
- source registry enforcement allows active root source
- proposed Apollo source is refused for capture
- schedule preview/write works
- lint passes on the scaffold
- staged note approval and promotion work
- restricted-folder promotion is refused

## Documentation

- [Docs Index](docs/README.md)
- [Start Here](docs/start-here.md)
- [Plain-English Skill Routing](docs/skill-routing.md)
- [First 20 Minutes](docs/first-20-minutes.md)
- [First Week](docs/first-week.md)
- [Operating Rhythm](docs/operating-rhythm.md)
- [Productized Setup Plan](docs/productized-setup.md)
- [Quickstart](docs/quickstart.md)
- [Harness Architecture](docs/harness-architecture.md)
- [Decision Log](docs/decision-log.md)
- [Team Operating Model](docs/team-operating-model.md)
- [Scheduling Guide](docs/scheduling-guide.md)
- [Team Onboarding Form](docs/team-onboarding-form.md)
- [Capture Policy Template](docs/capture-policy-template.md)
- [Source Registry Design](docs/source-registry-design.md)
- [Source Registry Template](docs/source-registry-template.yml)
- [Pilot Readiness Checklist](docs/pilot-readiness.md)
- [Customer Handoff Message](docs/customer-handoff-message.md)
- [Productionization Plan](docs/productionization-plan.md)

## Release

Current plugin metadata version: `0.3.0`.

Before publishing a release:

```bash
bash scripts/validate.sh
git tag v0.3.0
git push origin main --tags
```

Do not tag until the pushed commit is the version you want Claude and Codex
users to install.
