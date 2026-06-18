# Customer Handoff Message

Use this as a starting point when handing a new Company Brain Harness deployment
to a company owner or team lead.

## Message

Your Company Brain Harness is ready for a first team pilot.

The important distinction: this is not just "a bunch of docs in Drive" or a
generic chat-over-docs setup. The storage folder is the backend. The harness is
the operating layer that tells Claude, Codex, and other agents how to connect,
route, stage, approve, score, and safely grow the company brain.

To start, open Claude Code or Codex in the brain folder and say:

```text
I want to set up my company brain.
```

For daily operations, say:

```text
Run today's company brain check.
```

## What Is Ready

- The brain root is mounted or available as a local working folder.
- The brain root has routing, conventions, staging, source registry, schedule,
  and folder indexes.
- The harness installs into both Claude Code and Codex.
- The package has fourteen reusable skills: four simple role-based entry
  points plus ten lower-level action skills.
  - brain start
  - brain owner
  - brain operator
  - brain contribute
  - brain setup
  - brain health
  - sources check
  - brain intake
  - teammate/company onboarding interview
  - meeting-to-brain
  - staged-note approval
  - brain schedule
  - brain lint
  - repo-aware POC guardrails
- The package has generic CLIs for:
  - setup scaffolding
  - connection checks
  - source registry validation
  - brain health scoring
  - freshness/provenance lint
  - schedule generation
  - staging notes
  - approving/rejecting/revising notes
  - promoting approved notes into the right folder

## What Was Tested

- Local package validation passes.
- GitHub Actions validation passes.
- Claude plugin manifest validates.
- Claude marketplace manifest validates.
- Codex plugin manifest validates.
- A synthetic generic smoke test passes, proving the harness is not tied to one company.

## Current Health

The harness can be operational before the brain is populated.

Expected early state:

- Routing: ready
- Integrity: ready
- Brain root access: ready
- Source registry: ready for owner review
- Main gap: company/team knowledge still needs to be added by the team

That is expected. The harness is ready. The knowledge base now needs to be
filled through the staged workflow.

## What Still Needs Company Approval

- Approve the capture policy before any scheduled meeting/email capture.
- Decide whether the company will use a company-controlled meeting recorder workspace/API key.
- Decide whether shared Apollo/CRM is an approved company source, and what it may stage.
- Decide the company automation identity.
- Approve Google Workspace or equivalent service-account access.
- Lock restricted folders, especially owner/legal/finance/HR material.
- Pick who reviews the morning staging queue during the first 2-3 week pilot.

## How Information Gets Added

Nothing should go straight from raw source to shared brain.

The approved path is:

```text
source -> private staging -> proposed note -> human review -> approved note -> brain folder
```

People can add knowledge in three ways:

1. Drop/paste a document and run the intake skill.
2. Answer a guided onboarding interview.
3. Use an approved company source after the capture policy is approved.

Personal Fireflies/Gmail/Calendar/Apollo are not company capture sources. They
can help an individual work in their own Claude or Codex session, but they are
not the team engine.

## First Operating Schedule

For the first two weeks, run this manually or semi-automatically:

```text
Morning:
  run connection check
  run source registry check
  run brain health
  run brain lint
  review staged notes
  approve/reject/revise proposed notes

During the day:
  teammates use intake/onboarding skills to stage useful knowledge

Evening:
  optional lint/health pass
  produce next-day punch list
```

After the queue is clean for a week, low-risk categories can be considered for
auto-promotion. Meeting-derived, sensitive, HR/legal/finance, and strategy notes
should stay human-approved.

## What This Becomes

Once this works in the pilot, the same harness becomes the customer onboarding
blueprint: connect sources, create routing, interview the business, stage
knowledge, approve notes, score readiness, then train the company to operate it.
