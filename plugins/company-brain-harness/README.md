# Company Brain Harness

Portable skills and helper CLIs for operating a company brain on any filesystem-backed root:
Google Drive for Desktop, a git repo, a shared volume, or a local folder.

This plugin is intentionally generic. Set the target brain with `BRAIN_ROOT` or
`COMPANY_BRAIN_ROOT`; the storage backend can be Drive, git, a shared volume, or
any filesystem-backed root.

## Install

From GitHub:

```bash
claude plugin marketplace add <github-owner>/company-brain-harness
claude plugin install company-brain-harness@company-brain

codex plugin marketplace add <github-owner>/company-brain-harness
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

- `brain-setup` - scaffold a new team-first brain root.
- `brain-health` - connection and health check.
- `sources-check` - validate source registry and capture eligibility.
- `brain-intake` - stage a document, link, or pasted text for review.
- `brain-onboard` - interview a person and stage structured brain notes.
- `meeting-to-brain` - convert company-approved meeting material into staged notes.
- `approve-brain-notes` - review staged notes and approve/reject/revise.
- `brain-schedule` - create the human-gated or autonomous operating schedule.
- `brain-lint` - check freshness, provenance, links, duplicates, and contradictions.
- `repo-aware-poc` - keep prototypes aligned to the company repo map and stack conventions.

## CLIs

The bundled `bin/` CLIs are preview-first and generic:

- `brain-setup.py`
- `connections-check.py`
- `source-registry-check.py`
- `brain-health.py`
- `brain-lint.py`
- `brain-schedule.py`
- `stage-brain-note.py`
- `approve-staged-note.py`
- `promote-to-brain.py`

No CLI should ingest personal connectors into a shared company brain. Company capture
requires an approved `CAPTURE_POLICY.md` and a registered source instance in
`source-registry.yml`.

## Verify

From the repository root:

```bash
bash scripts/validate.sh
```

## Full Documentation

The published docs live at the repository root under `docs/`. Start with:

- `docs/quickstart.md`
- `docs/harness-architecture.md`
- `docs/decision-log.md`
