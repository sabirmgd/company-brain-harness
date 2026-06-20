# Company Brain Harness

Portable skills and helper CLIs for operating a company brain on any filesystem-backed root:
Google Drive for Desktop, a git repo, a shared volume, or a local folder.

This plugin is intentionally generic. Set the target brain with `BRAIN_ROOT` or
`COMPANY_BRAIN_ROOT`; the storage backend can be Drive, git, a shared volume, or
any filesystem-backed root.

The scaffold supports two profiles: `governed` for strict staged approval and
`simple-team` for an `ADD_TO_BRAIN/` drop zone plus operator digest automation.
Source connectors remain governed in both profiles.

## Install

Install this as one plugin bundle. The bundle includes the `skills/` routing
surfaces, `bin/` helper CLIs, and `references/` contract. Users should not
download isolated skills and then look for scripts separately.

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

Users normally speak in plain English. The skill descriptions route requests
like "I want to set up my company brain", "run today's brain check", "I want to
add what I know", or "can Slack feed the brain" to the right skill.

- `brain-start` - main entry point for setup, operation, or contribution.
- `brain-owner` - guide owner setup decisions and approvals.
- `brain-operator` - run daily checks and operational punch lists.
- `brain-contribute` - help a teammate contribute knowledge safely.
- `brain-setup` - scaffold a new team-first brain root.
- `brain-health` - connection and health check.
- `source-setup` - safely scope and approve tool source instances.
- `source-sync` - pull approved sources into private evidence and staged notes.
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
- `add-to-brain-digest.py`
- `connections-check.py`
- `source-registry-check.py`
- `confluence-export.py`
- `fireflies-export.py`
- `repo-map-export.py`
- `source-pull.py`
- `source-extract.py`
- `source-sync-state.py`
- `brain-health.py`
- `brain-lint.py`
- `brain-schedule.py`
- `stage-brain-note.py`
- `approve-staged-note.py`
- `promote-to-brain.py`

`source-pull.py` keeps an append-only evidence log. `source-extract.py` stages
the latest eligible record per external item so updated pulls do not create
stale duplicate proposals.
Optional raw source material is stored only under `system/staging/raw/` when the
registered source policy allows raw retention; it is never promoted directly as
shared knowledge.
`add-to-brain-digest.py` is for manual team drop-zone contributions; it does not
replace source registry enforcement for connectors.

No CLI should ingest personal connectors into a shared company brain. Company capture
requires an approved `capture-policy.md` and a registered source instance in
`source-registry.yml`.

## Verify

From the repository root:

```bash
bash scripts/validate.sh
```

## Full Documentation

The published docs live at the repository root under `docs/`. Start with:

- `docs/start-here.md`
- `docs/skill-routing.md`
- `docs/first-20-minutes.md`
- `docs/operating-rhythm.md`
- `docs/quickstart.md`
- `docs/harness-architecture.md`
- `docs/decision-log.md`
