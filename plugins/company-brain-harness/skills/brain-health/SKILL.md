---
name: brain-health
description: Check whether a filesystem-backed company brain is connected, policy-safe, healthy, and ready for teammate use. Use when the user asks for brain health, connection status, harness readiness, setup verification, missing integrations, or a morning/company-brain check.
---

# Brain Health

Run a read-only readiness pass over the current company brain. Do not inspect restricted vault folders.

## Workflow

1. Resolve the brain root from `--root`, `BRAIN_ROOT`, `COMPANY_BRAIN_ROOT`, `COMPANY_OS_ROOT`, or the current working directory.
2. Read the configured routing file and harness docs when present. Defaults are:
   - `CLAUDE.md`
   - `00_README_Drive_Conventions/HARNESS_STATUS.md`
   - `00_README_Drive_Conventions/CAPTURE_POLICY.md`
   Use `company-brain.yml` / `company-os.yml` if the deployment renamed these paths.
3. Run the bundled checks:
   - `connections-check.py --root <brain-root> --live`
   - `brain-health.py --root <brain-root>`
4. Treat missing optional connectors as setup nudges, not failures. Treat missing brain root/routing as blocking.
5. Call out personal connector risk clearly. A personal Fireflies key is not a company capture source unless the capture policy is approved and the source is marked company-controlled.
6. Report:
   - overall status
   - blocking issues
   - warnings
   - next three highest-leverage fixes

## Bundled CLIs

The plugin CLIs live at `../../bin` relative to this skill folder.

For Claude Code, `${CLAUDE_SKILL_DIR}/../../bin/connections-check.py` is available.
For Codex, use the path of this `SKILL.md` and resolve `../../bin`.
