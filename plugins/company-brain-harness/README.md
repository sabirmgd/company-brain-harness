# Company Brain Harness

Portable skills and helper CLIs for operating a company brain on any filesystem-backed root:
Google Drive for Desktop, a git repo, a shared volume, or a local folder.

This plugin is intentionally generic. Set the target brain with `BRAIN_ROOT` or
`COMPANY_BRAIN_ROOT`; HeyFlora's `Company_Master` Drive is only one configured
deployment.

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
claude plugin marketplace add .
claude plugin install company-brain-harness@company-brain

codex plugin marketplace add .
codex plugin add company-brain-harness@company-brain
```

For local development without installing, Claude can load the plugin directly:

```bash
claude --plugin-dir ./plugins/company-brain-harness
```

## Skills

- `brain-health` - connection and health check.
- `brain-intake` - stage a document, link, or pasted text for review.
- `brain-onboard` - interview a person and stage structured brain notes.
- `meeting-to-brain` - convert company-approved meeting material into staged notes.
- `approve-brain-notes` - review staged notes and approve/reject/revise.
- `repo-aware-poc` - keep prototypes aligned to the company repo map and stack conventions.

## CLIs

The bundled `bin/` CLIs are preview-first and generic:

- `connections-check.py`
- `brain-health.py`
- `stage-brain-note.py`
- `approve-staged-note.py`
- `promote-to-brain.py`

No CLI should ingest personal connectors into a shared company brain. Company capture
requires an approved `CAPTURE_POLICY.md` and a company-controlled source.

## Verify

From the repository root:

```bash
bash scripts/validate.sh
```
