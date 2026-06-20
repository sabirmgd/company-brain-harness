# Company Brain Harness Quickstart

This harness is a portable plugin plus helper CLIs. It does not assume Google
Drive. The brain root can be a mounted Drive folder, a git repo, a shared
volume, or a local directory.

The category is Company Brain Harness: a reusable operating layer for
team-owned company memory.

For the reasoning behind each layer, read
[Harness Architecture](harness-architecture.md) and
[Decision Log](decision-log.md).

## 1. Install

Install the plugin bundle. This installs the skill routing files and the
supporting `bin/` scripts together. A normal customer does not need to clone the
repo after installing the plugin.

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

## 2. Create Or Point At A Brain Root

The brain root is separate from the installed plugin. It is the customer-owned
folder or repo where `CLAUDE.md`, `company-brain.yml`, `brain/`, and `system/`
live.

For the simplest path, open Claude Code or Codex and say:

```text
I want to set up my company brain.
```

The agent should route you through `brain-start`.

For an existing root:

```bash
export BRAIN_ROOT="/path/to/company-brain-root"
```

For a new root, preview first:

```bash
python3 plugins/company-brain-harness/bin/brain-setup.py \
  --root "$BRAIN_ROOT" \
  --company-name "Acme Co" \
  --champion "Brain Owner" \
  --operator "Brain Operator"
```

Choose an operating profile:

- `governed`: default. Every shared note goes through staged review.
- `simple-team`: creates `ADD_TO_BRAIN/`, `system/digests/`, and a low-friction
  manual contribution loop for small teams.

For the simple team model:

```bash
python3 plugins/company-brain-harness/bin/brain-setup.py \
  --root "$BRAIN_ROOT" \
  --company-name "Acme Co" \
  --champion "Brain Owner" \
  --operator "Brain Operator" \
  --operating-profile simple-team
```

Then write the scaffold. For the default governed model:

```bash
python3 plugins/company-brain-harness/bin/brain-setup.py \
  --root "$BRAIN_ROOT" \
  --company-name "Acme Co" \
  --champion "Brain Owner" \
  --operator "Brain Operator" \
  --write
```

For the simple team model, add `--operating-profile simple-team`.

This creates routing, policy, source registry, staging, schedule, folder
indexes, and team scaffolding. It does not populate company data.

## 3. Verify The Harness

From the harness checkout:

```bash
bash scripts/validate.sh
```

Against a real brain:

```bash
python3 plugins/company-brain-harness/bin/connections-check.py --root "$BRAIN_ROOT" --live
python3 plugins/company-brain-harness/bin/source-registry-check.py --root "$BRAIN_ROOT"
python3 plugins/company-brain-harness/bin/brain-health.py --root "$BRAIN_ROOT"
python3 plugins/company-brain-harness/bin/brain-lint.py --root "$BRAIN_ROOT" --stale-days 30
```

## 4. Register Sources Before Capture

Every source must be a specific instance:

- company Fireflies workspace
- shared Apollo or CRM workspace
- company GitHub org
- selected Slack channels
- Google Workspace service account
- approved Confluence spaces
- delegated client/project email scope
- customer-owned workspace for that customer's brain

Do not register broad app names or every teammate's personal account. A
teammate can delegate a narrow email/calendar scope, but the registry must say
what is included, what is excluded, who owns it, who reviews it, and what raw
material may be stored.

Before a connector job runs:

```bash
python3 plugins/company-brain-harness/bin/source-registry-check.py \
  --root "$BRAIN_ROOT" \
  --source-id "<source-id>" \
  --for-capture
```

## 5. Use The Skills

Claude Code:

```text
/company-brain-harness:brain-start
/company-brain-harness:brain-owner
/company-brain-harness:brain-operator
/company-brain-harness:brain-contribute
/company-brain-harness:brain-setup
/company-brain-harness:brain-health
/company-brain-harness:sources-check
/company-brain-harness:source-setup
/company-brain-harness:source-sync
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
$sources-check
$source-setup
$source-sync
$brain-intake
$brain-onboard
$meeting-to-brain
$approve-brain-notes
$brain-schedule
$brain-lint
$repo-aware-poc
```

## 6. Team Operating Model

Every teammate connects to the same brain root. Each person can use their own
Claude/Codex session. The default governed path is:

```text
source or interview -> staged proposal -> review -> approved note -> brain folder
```

The simpler team path is:

```text
teammate drops file in ADD_TO_BRAIN -> operator digest -> low-risk update or review flag
```

The first two weeks should normally be human-gated:

- checks can run daily
- approved sources can create staged proposals
- promotion requires explicit approve/reject/revise
- sensitive material stays restricted or out

After trust is established, scheduled checks and approved-source staging can run
unattended. Auto-promotion should stay limited to low-risk categories with an
explicit policy rule.

Source connectors stay governed in both profiles. The drop zone is for manual
team contributions, not broad personal email/calendar/meeting/chat exports.
