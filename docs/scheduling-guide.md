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
  --champion "<Brain Owner>" \
  --operator "<Brain Operator>" \
  --write
```

`brain-schedule.py` reads `operating_profile` from `company-brain.yml` by
default and adds the `ADD_TO_BRAIN/` digest step for `simple-team` roots.

Daily loop:

1. `connections-check.py --live`
2. `source-registry-check.py`
3. `source-pull.py` for approved source instances only
4. `source-extract.py` to create staged proposals from allowed artifacts
5. `brain-health.py`
6. `brain-lint.py --stale-days 30`
7. `add-to-brain-digest.py` when `ADD_TO_BRAIN/` exists
8. review staged proposals and flagged drop-zone items
9. publish a short punch list

During this period, governed-profile promotions require human
approve/reject/revise. In `simple-team`, low-risk manual drop-zone contributions
may be processed automatically only when the owner has chosen that policy.

## Autonomous Mode

Autonomous mode can be introduced after the team trusts the staging path:

```bash
python3 plugins/company-brain-harness/bin/brain-schedule.py \
  --root "$BRAIN_ROOT" \
  --mode autonomous \
  --time 08:30 \
  --timezone local \
  --champion "<Brain Owner>" \
  --operator "<Brain Operator>" \
  --write
```

Allowed unattended work:

- connection checks
- source registry validation
- brain health scoring
- lint
- cursor-based source pulls into private evidence
- extraction of allowed artifacts into staged proposals
- staged proposals from approved source instances
- daily digest generation
- `ADD_TO_BRAIN/` digest and low-risk manual contribution processing when
  `simple-team` policy allows it

Keep these human-approved:

- final promotion from staging
- meeting-derived notes during pilot
- HR, legal, finance, compensation, fundraising, and sensitive customer data
- notes that change strategy or commitments
- restricted-folder access
- new source approvals
- broad personal-source capture

## Cron Shape

The harness does not require a specific scheduler. A cron, launchd job, GitHub
Action, CI runner, or teammate laptop can run the daily loop if it has access to
the brain root and credentials.

Use a wrapper script that exports:

```bash
export BRAIN_ROOT="/path/to/company-brain-root"
```

Then run the daily commands from the generated `schedule.md`.

Connector adapters should produce normalized JSONL before calling
`source-pull.py`; the harness owns privacy filtering, dedupe state, extraction,
and staging.

The harness does not require a scheduler product. Claude/Codex scheduled tasks,
cron, launchd, CI, or a local operator agent can run the same commands.

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

Manual drop-zone contributions in `simple-team` follow the same safety spirit:
only clearly low-risk company material can bypass item-by-item approval, and
anything sensitive or unclear is flagged.
