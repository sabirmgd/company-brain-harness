---
name: brain-health
description: Check whether a company brain is connected, policy-safe, healthy, and ready for team use. Use when the user says is the brain ready, check health, check setup, verify connections, are integrations working, can the team use this, or show readiness status.
---

# Brain Health

Run a read-only readiness pass over the current company brain. Do not inspect restricted folders.

## Workflow

1. Resolve the brain root from `--root`, `BRAIN_ROOT`, `COMPANY_BRAIN_ROOT`, `COMPANY_OS_ROOT`, or the current working directory.
2. Read the configured routing file and harness docs when present. Defaults are:
   - `CLAUDE.md`
   - `00_Company_Brain_Conventions/HARNESS_STATUS.md`
   - `00_Company_Brain_Conventions/CAPTURE_POLICY.md`
   Use `company-brain.yml` / `company-os.yml` if the deployment renamed these paths.
3. Run the bundled checks:
   - `connections-check.py --root <brain-root> --live`
   - `source-registry-check.py --root <brain-root>`
   - `brain-health.py --root <brain-root>`
   - `brain-lint.py --root <brain-root> --stale-days 30`
4. Treat missing optional connectors as setup nudges, not failures. Treat missing brain root/routing as blocking.
5. Call out personal connector risk clearly. A personal Fireflies, Gmail, Calendar, Apollo, or Slack account is not a company capture source unless delegated, scoped, approved, and registered.
6. Report:
   - overall status
   - blocking issues
   - warnings
   - next three highest-leverage fixes
   - whether the brain is ready for teammates to populate

## Bundled CLIs

The plugin CLIs live at `../../bin` relative to this skill folder.

For Claude Code, `${CLAUDE_SKILL_DIR}/../../bin/connections-check.py` is available.
For Codex, use the path of this `SKILL.md` and resolve `../../bin`.
