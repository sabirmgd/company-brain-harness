# Company Brain Harness

Portable harness for building and operating a team-owned company brain that
Claude, Codex, and other agents can read, maintain, and safely grow.

HeyFlora's `Company_Master` is the dogfood deployment. The product category is
not "second brain for landscaping." It is Company Brain Harness: source-governed
organizational memory for humans and agents.

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
- a testable release gate that proves the harness works outside HeyFlora

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

The harness does not populate company knowledge by itself. Scott or each
company's team members supply the real context through onboarding, intake,
approved source capture, and review.

## Layer Decisions

| Layer | Decision | Why |
|---|---|---|
| Product category | Company Brain Harness, not landscaping second brain | HeyFlora is dogfood; the generic product is team/company memory |
| Storage | Filesystem-backed brain root | Works with Drive, git, shared volumes, and local folders |
| Distribution | One Claude/Codex plugin | Versioned, installable, reviewable, team-distributable |
| Skills | Shared `SKILL.md` surfaces | Same workflows work in Claude and Codex |
| CLIs | Stdlib Python, preview-first | Portable, easy to validate, no dependency setup |
| Writes | `--write` required for side effects | Prevents accidental shared-brain mutation |
| Knowledge flow | source/interview -> staging -> approval -> brain | Raw material is not automatically shared knowledge |
| Source model | Source instance, not connector type | "Fireflies" or "Apollo" is too broad; exact workspace/account must be approved |
| Team model | Champion, Operator, teammate, source owner | A company brain is not one person's private second brain |
| Safety | Restricted prefixes skipped and refused by default | Sensitive HR/legal/finance/owner material must not be broadly indexed |
| Freshness | `last_verified`, provenance, lint | Company knowledge decays unless checked |
| Scheduling | Human-gated first, autonomous later | Trust the staging/review loop before automation |
| Productization | Policy and source registry are customer-facing primitives | Trust and governance must be part of onboarding |

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
    └── smoke-test.sh                         # Non-HeyFlora portability smoke test
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

## Fast Start

Set the brain root:

```bash
export BRAIN_ROOT="/path/to/company-brain-root"
```

Preview a new scaffold:

```bash
python3 plugins/company-brain-harness/bin/brain-setup.py \
  --root "$BRAIN_ROOT" \
  --company-name "Acme Co" \
  --champion "Brain Champion" \
  --operator "Brain Operator"
```

Write the scaffold:

```bash
python3 plugins/company-brain-harness/bin/brain-setup.py \
  --root "$BRAIN_ROOT" \
  --company-name "Acme Co" \
  --champion "Brain Champion" \
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
| `brain-setup` | Scaffold a new team-first brain root without populating data |
| `brain-health` | Check connection, policy, and readiness |
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
/company-brain-harness:brain-setup
/company-brain-harness:brain-health
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
$brain-setup
$brain-health
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
- `personal-fireflies-sabir` with `status: excluded`

Before connector capture:

```bash
python3 plugins/company-brain-harness/bin/source-registry-check.py \
  --root "$BRAIN_ROOT" \
  --source-id "<source-id>" \
  --for-capture
```

## Team Operating Model

The default roles are:

- Champion: owns policy, source approval, review standards, and adoption
- Operator: runs checks, lint, staging queue, and schedule
- Teammate: contributes role knowledge and source suggestions
- Source owner: owns source scope, credentials, retention, and accuracy

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
- non-HeyFlora smoke test

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
- [Quickstart](docs/quickstart.md)
- [Harness Architecture](docs/harness-architecture.md)
- [Decision Log](docs/decision-log.md)
- [Team Operating Model](docs/team-operating-model.md)
- [Scheduling Guide](docs/scheduling-guide.md)
- [Team Onboarding Form](docs/team-onboarding-form.md)
- [Capture Policy Template](docs/capture-policy-template.md)
- [Source Registry Design](docs/source-registry-design.md)
- [Source Registry Template](docs/source-registry-template.yml)
- [Scott Readiness Checklist](docs/scott-readiness.md)
- [Productionization Plan](docs/productionization-plan.md)

## Release

Current plugin metadata version: `0.2.0`.

Before publishing a release:

```bash
bash scripts/validate.sh
git tag v0.2.0
git push origin main --tags
```

Do not tag until the pushed commit is the version you want Claude and Codex
users to install.
