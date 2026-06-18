# Scott Handoff Message

Scott,

We now have the first usable version of the Company Brain harness.

The important distinction: this is not "a bunch of docs in Drive." The Drive is
the storage layer. The harness is the operating layer that tells Claude/Codex how
to connect, route, stage, approve, score, and safely grow the company brain.

## What is ready

- `Company_Master` is mounted and readable as a local working folder.
- The Drive has a root `CLAUDE.md` routing file and top-level folder indexes.
- The harness is packaged as a private GitHub repo:
  `https://github.com/sabirmgd/company-brain-harness`
- The package installs into both Claude Code and Codex.
- The package has ten reusable skills:
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

## What we tested

- Local package validation passes.
- GitHub Actions validation passes.
- Claude plugin manifest validates.
- Claude marketplace manifest validates.
- Codex plugin manifest validates.
- A non-HeyFlora smoke test passes, proving the harness is generic.
- The plugin was installed from GitHub into Claude Code.
- The plugin was installed from GitHub into Codex.
- The installed Codex package successfully ran against the live `Company_Master`
  Drive.

## Current health

The brain is operational but not populated.

- Routing: strong
- Integrity: strong
- Drive access: ready
- GitHub repo awareness: ready
- Brain health score: 59/100, "Working"
- Main gap: most folders are still empty

That is expected. The harness is ready. The knowledge base now needs to be
filled through the staged workflow.

## What still needs your approval

- Approve the capture policy before any scheduled meeting/email capture.
- Decide whether HeyFlora will create a company Fireflies workspace/API key.
- Decide whether shared Apollo/CRM is an approved company source, and what it
  may stage.
- Decide the company automation identity, for example `flora-bot@heyflora.ai`.
- Approve Google Workspace access for the engine identity.
- Lock restricted folders, especially owner/legal/finance/HR material.
- Pick who reviews the morning staging queue during the first 2-3 week pilot.

## How information gets added

Nothing should go straight from raw source to shared brain.

The approved path is:

```text
source -> private staging -> proposed note -> human review -> approved note -> brain folder
```

People can add knowledge in three ways:

1. Drop/paste a document and run the intake skill.
2. Answer a guided onboarding interview.
3. Use an approved company meeting source after the capture policy is approved.

Personal Fireflies/Gmail/Calendar/Apollo are not company capture sources. They
can help an individual work in their own Claude session, but they are not the
team engine.

## First operating schedule

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

## What this becomes

The HeyFlora company brain is the dogfood implementation.

Once this works internally, the same harness becomes the customer onboarding
blueprint: connect sources, create routing, interview the business, stage
knowledge, approve notes, score readiness, then train the company to operate it.
