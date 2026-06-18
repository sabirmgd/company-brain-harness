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
- `00_Company_Brain_Conventions/README.md` or equivalent conventions doc.
- `00_Company_Brain_Conventions/CAPTURE_POLICY.md`.
- `00_Company_Brain_Conventions/source-registry.yml`.
- `00_Company_Brain_Conventions/HARNESS_FLOWS.md`.
- `00_Company_Brain_Conventions/HARNESS_STATUS.md`.
- `00_Company_Brain_Conventions/90_Staging/`.

The defaults can be overridden by `company-brain.yml` or `company-os.yml`:

```yaml
brain:
  routing_file: CLAUDE.md
  conventions_dir: 00_Company_Brain_Conventions
  staging_dir: 00_Company_Brain_Conventions/90_Staging
  restricted_prefixes:
    - Restricted
```

Existing deployments may use the legacy `00_README_Drive_Conventions` path.
Future customers may rename this layer, but the staging, capture-policy, and
routing concepts remain the same.

## Capture Policy

Default posture is source-separated capture:

- Company-controlled sources can feed the engine.
- Connector capture uses registered source instances, not broad app names.
- Personal accounts and personal Fireflies/Gmail/Calendar/Apollo keys are not company sources by default.
- Raw material lands in private staging, not the shared brain.
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

## Maintenance

Daily operating checks should include:

1. `connections-check.py`.
2. `source-registry-check.py`.
3. `brain-health.py`.
4. `brain-lint.py`.
5. staged proposal review.
