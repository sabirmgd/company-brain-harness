# Simple Team Profile

The `simple-team` profile is for companies that want the brain to be easy to
operate before they have a formal knowledge-management process.

## Who It Fits

- small teams
- founder-led teams
- agencies or consultants setting up a client brain
- teams that trust manual teammate contributions but do not want broad personal
  account capture

## Customer Experience

Team members do not need to learn source registries, staging folders, or CLI
flags.

They can say:

```text
I added something to the company brain folder.
```

Or they can put material in:

```text
ADD_TO_BRAIN/
```

The operator loop scans that folder, writes `system/digests/latest.md`, processes
low-risk manual company material, and flags anything sensitive or unclear.

## Setup

Preview:

```bash
python3 plugins/company-brain-harness/bin/brain-setup.py \
  --root "$BRAIN_ROOT" \
  --company-name "Acme Co" \
  --champion "Brain Owner" \
  --operator "Brain Operator" \
  --operating-profile simple-team
```

Write:

```bash
python3 plugins/company-brain-harness/bin/brain-setup.py \
  --root "$BRAIN_ROOT" \
  --company-name "Acme Co" \
  --champion "Brain Owner" \
  --operator "Brain Operator" \
  --operating-profile simple-team \
  --write
```

## Operator Digest

```bash
python3 plugins/company-brain-harness/bin/add-to-brain-digest.py \
  --root "$BRAIN_ROOT" \
  --write
```

The digest records metadata and risk flags. It does not copy full document
contents into the digest.

## Guardrails

- Personal email, calendar, meeting recorder, chat, CRM, and other personal
  accounts are still excluded by default.
- Source connectors still require `source-registry.yml`.
- Raw connector exports are not shared knowledge.
- Credentials, HR, legal, finance, payroll, compensation, owner-only strategy,
  and unclear material must be flagged for review.
- `brain/restricted/` is still excluded from default agent scans.

## Mental Model

```text
manual teammate contribution -> ADD_TO_BRAIN -> digest -> low-risk update
                                               -> review flag

connector source -> source registry -> private evidence -> staged proposal
                                                   -> review or approved automation
```
