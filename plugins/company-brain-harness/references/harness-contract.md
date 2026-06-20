# Company Brain Harness Contract

Use this reference when a skill needs the operating rules behind the harness.

## Brain Root

The brain root is any filesystem-backed folder containing a routed knowledge system.
Google Drive is a backend, not the product. Resolve the root in this order:

1. Explicit `--root`.
2. `BRAIN_ROOT`.
3. `COMPANY_BRAIN_ROOT`.
4. `COMPANY_OS_ROOT` legacy alias.
5. Current working directory.

## Required Brain Files

Defaults:

- `CLAUDE.md` or equivalent root routing instructions.
- `system/README.md` or equivalent conventions doc.
- `system/capture-policy.md`.
- `system/source-registry.yml`.
- `system/source-sync-state.json`.
- `system/flows.md`.
- `system/status.md`.
- `system/staging/`.
- `system/staging/evidence/`.

The defaults can be overridden by `company-brain.yml` or `company-os.yml`:

```yaml
brain:
  routing_file: CLAUDE.md
  conventions_dir: system
  staging_dir: system/staging
  restricted_prefixes:
    - brain/restricted
```

Existing deployments may use legacy `00_Company_Brain_Conventions` or
`00_README_Drive_Conventions` paths.
Future customers may rename this layer, but the staging, capture-policy, and
routing concepts remain the same.

## Capture Policy

Default posture is source-separated capture:

- Company-controlled sources can feed the engine.
- Connector capture uses registered source instances, not broad app names.
- Personal accounts are excluded by default unless a narrow delegated scope is
  explicitly approved with privacy exclusions.
- Raw material lands in private evidence staging, not the shared brain.
- Curated notes reach the brain only after approval.
- Sensitive company material routes to a restricted folder; never index restricted folders.

## Write Path

All write workflows use:

1. Stage: `stage-brain-note.py --write`.
2. Review: human or owner reviews staged proposal.
3. Approve/reject/revise: `approve-staged-note.py`.
4. Promote: approval calls `promote-to-brain.py`.

Direct writes to final knowledge folders are allowed only for explicitly approved
administrative harness docs or local dry-run tests.

`stage-brain-note.py` previews by default. A proposal file is created only when
`--write` is present.

## Source Sync Path

Approved source workflows use:

1. Check: `source-registry-check.py --for-capture`.
2. Pull: `source-pull.py` stores scoped, non-private evidence.
3. Extract: `source-extract.py` creates staged proposals from allowed artifacts.
4. Review: approved proposals follow the standard write path.

Connector adapters must normalize app data before `source-pull.py`. The harness
owns privacy filtering, dedupe hashes, source cursors, staging, and promotion.

## Maintenance

Daily operating checks should include:

1. `connections-check.py`.
2. `source-registry-check.py`.
3. `source-pull.py` for approved source instances.
4. `source-extract.py`.
5. `brain-health.py`.
6. `brain-lint.py`.
7. staged proposal review.
