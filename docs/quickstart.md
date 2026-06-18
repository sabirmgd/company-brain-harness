# Company Brain Harness Quickstart

This harness is a portable plugin plus helper CLIs. It does not assume Google
Drive. The brain root can be a mounted Drive folder, a git repo, a shared
volume, or a local directory.

HeyFlora is the dogfood deployment. The category is Company Brain Harness.

For the reasoning behind each layer, read
[Harness Architecture](harness-architecture.md) and
[Decision Log](decision-log.md).

## 1. Install

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

For an existing root:

```bash
export BRAIN_ROOT="/path/to/company-brain-root"
```

For a new root, preview first:

```bash
python3 plugins/company-brain-harness/bin/brain-setup.py \
  --root "$BRAIN_ROOT" \
  --company-name "Acme Co" \
  --champion "Brain Champion" \
  --operator "Brain Operator"
```

Then write the scaffold:

```bash
python3 plugins/company-brain-harness/bin/brain-setup.py \
  --root "$BRAIN_ROOT" \
  --company-name "Acme Co" \
  --champion "Brain Champion" \
  --operator "Brain Operator" \
  --write
```

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
- customer-owned workspace for that customer's brain

Do not register broad app names or every teammate's personal account.

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

## 6. Team Operating Model

Every teammate connects to the same brain root. Each person can use their own
Claude/Codex session, but shared writes go through the same staged approval
path:

```text
source or interview -> staged proposal -> review -> approved note -> brain folder
```

The first two weeks should normally be human-gated:

- checks can run daily
- approved sources can create staged proposals
- promotion requires explicit approve/reject/revise
- sensitive material stays restricted or out

After trust is established, scheduled checks and approved-source staging can run
unattended. Auto-promotion should stay limited to low-risk categories with an
explicit policy rule.
