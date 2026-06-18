# Scheduling Guide

The schedule makes the harness reliable. It is not a license to ingest every
available source.

## Recommended First Two Weeks

Use human-gated mode:

```bash
python3 plugins/company-brain-harness/bin/brain-schedule.py \
  --root "$BRAIN_ROOT" \
  --mode human \
  --time 08:30 \
  --timezone local \
  --champion "<Champion>" \
  --operator "<Operator>" \
  --write
```

Daily loop:

1. `connections-check.py --live`
2. `source-registry-check.py`
3. `brain-health.py`
4. `brain-lint.py --stale-days 30`
5. review staged proposals
6. publish a short punch list

During this period, all promotions require human approve/reject/revise.

## Autonomous Mode

Autonomous mode can be introduced after the team trusts the staging path:

```bash
python3 plugins/company-brain-harness/bin/brain-schedule.py \
  --root "$BRAIN_ROOT" \
  --mode autonomous \
  --time 08:30 \
  --timezone local \
  --champion "<Champion>" \
  --operator "<Operator>" \
  --write
```

Allowed unattended work:

- connection checks
- source registry validation
- brain health scoring
- lint
- staged proposals from approved source instances
- daily digest generation

Keep these human-approved:

- final promotion from staging
- meeting-derived notes during pilot
- HR, legal, finance, compensation, fundraising, and sensitive customer data
- notes that change strategy or commitments
- restricted-folder access
- new source approvals

## Cron Shape

The harness does not require a specific scheduler. A cron, launchd job, GitHub
Action, CI runner, or teammate laptop can run the daily loop if it has access to
the brain root and credentials.

Use a wrapper script that exports:

```bash
export BRAIN_ROOT="/path/to/company-brain-root"
```

Then run the daily commands from the generated `SCHEDULE.md`.

## Promotion Rule

Auto-promotion should be explicit and narrow:

- source is `active`
- source has `capture.allowed: true`
- source has owner and review owner
- source policy permits auto-promotion
- destination is not restricted
- category is low-risk
- note has provenance and tags

If any condition is missing, stage only.
