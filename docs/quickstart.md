# Company Brain Harness Quickstart

This harness is a portable plugin marketplace plus helper CLIs. It does not
assume Google Drive. The brain root can be a mounted Drive folder, a git repo, a
shared volume, or a local directory.

## 1. Install From GitHub

After this repo is published, install the marketplace from GitHub:

```bash
claude plugin marketplace add sabirmgd/company-brain-harness
claude plugin install company-brain-harness@company-brain

codex plugin marketplace add sabirmgd/company-brain-harness
codex plugin add company-brain-harness@company-brain
```

## 2. Install From A Local Checkout

For development:

```bash
git clone git@github.com:sabirmgd/company-brain-harness.git
cd company-brain-harness

claude plugin marketplace add .
claude plugin install company-brain-harness@company-brain

codex plugin marketplace add .
codex plugin add company-brain-harness@company-brain
```

## 3. Point The Agent At A Brain Root

Set the root before running skills or CLIs:

```bash
export BRAIN_ROOT="/path/to/company-brain-root"
```

The root should contain:

- `CLAUDE.md` or the configured routing file.
- A conventions folder with `README.md`.
- `CAPTURE_POLICY.md`.
- `HARNESS_FLOWS.md`.
- `HARNESS_STATUS.md`.
- A staging folder for proposed notes.

Optional config file:

```yaml
schema_version: "1.0"
kind: company_brain_config
brain:
  routing_file: CLAUDE.md
  conventions_dir: 00_README_Drive_Conventions
  staging_dir: 00_README_Drive_Conventions/90_Staging
  restricted_prefixes:
    - 14_Owner_Vault
health:
  priority_folders:
    - 02_Strategy_and_Vision
    - 03_Platform_Architecture
```

Supported config names:

- `company-brain.yml`
- `company-os.yml`
- `<conventions_dir>/company-brain.yml`
- `<conventions_dir>/company-os.yml`

## 4. Verify

From the harness checkout:

```bash
bash scripts/validate.sh
```

Against a real brain:

```bash
python3 plugins/company-brain-harness/bin/connections-check.py --root "$BRAIN_ROOT" --live
python3 plugins/company-brain-harness/bin/brain-health.py --root "$BRAIN_ROOT"
```

## 5. Use The Skills

Claude Code:

```text
/company-brain-harness:brain-health
/company-brain-harness:brain-intake
/company-brain-harness:brain-onboard
/company-brain-harness:meeting-to-brain
/company-brain-harness:approve-brain-notes
/company-brain-harness:repo-aware-poc
```

Codex:

```text
$brain-health
$brain-intake
$brain-onboard
$meeting-to-brain
$approve-brain-notes
$repo-aware-poc
```

## 6. Team Setup Model

Every teammate connects to the same brain root. Each person can use their own
Claude/Codex session, but shared writes go through the same staged approval
path:

```text
raw/input -> staged proposal -> human review -> approved note -> brain folder
```

Personal connectors are not team-engine connectors. Meeting/email/calendar
capture must come from company-controlled sources and follow the approved
capture policy.
