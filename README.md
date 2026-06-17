# Company Brain Harness

The Company Brain Harness is the portable operating layer for a
filesystem-backed company brain. A brain root can be a mounted Google Drive
folder, a git repo, a shared volume, or a local directory. HeyFlora's
`Company_Master` Google Drive is the dogfood deployment, not a product-specific
assumption in the harness.

## Architecture Decision

Do not ship the harness as local-only skills under `~/.codex/skills` or
`~/.claude/skills`. Local skills are useful for experiments, but they are not
versioned, installable, reviewable, or team-distributable.

The durable distribution unit is:

```text
plugins/company-brain-harness/
```

That one plugin contains:

- `.codex-plugin/plugin.json` for Codex.
- `.claude-plugin/plugin.json` for Claude Code.
- `skills/` with shared Agent Skills-compatible `SKILL.md` files.
- `bin/` with generic, preview-first harness CLIs.
- `references/` with the portable harness contract.

The repo exposes the plugin through both marketplaces:

```text
.agents/plugins/marketplace.json       # Codex
.claude-plugin/marketplace.json        # Claude Code
```

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
git clone git@github.com:sabirmgd/company-brain-harness.git
cd company-brain-harness

claude plugin marketplace add .
claude plugin install company-brain-harness@company-brain

codex plugin marketplace add .
codex plugin add company-brain-harness@company-brain
```

Claude Code can also test the plugin directly without installing:

```bash
claude --plugin-dir ./plugins/company-brain-harness
```

## Skills

| Skill | Purpose |
|---|---|
| `brain-health` | Read-only connection and health check |
| `brain-intake` | Stage raw material into a routed proposal |
| `brain-onboard` | Interview a teammate or owner into staged notes |
| `meeting-to-brain` | Convert approved meeting material into staged notes |
| `approve-brain-notes` | Approve, reject, or revise staged proposals |
| `repo-aware-poc` | Keep prototypes aligned to repo map and stack guardrails |

Claude Code invokes plugin skills as:

```text
/company-brain-harness:brain-health
```

Codex uses the installed plugin/skill through the plugin directory or skill
selector, for example:

```text
$brain-health
```

## CLIs

All CLIs are generic and take `--root` or resolve the brain root from:

1. `BRAIN_ROOT`
2. `COMPANY_BRAIN_ROOT`
3. `COMPANY_OS_ROOT` legacy alias
4. current working directory

They also read `company-brain.yml` / `company-os.yml` when present, including
custom routing file, conventions folder, staging folder, and restricted
prefixes.

Bundled commands:

```text
bin/connections-check.py
bin/brain-health.py
bin/stage-brain-note.py
bin/approve-staged-note.py
bin/promote-to-brain.py
```

Write behavior:

- preview by default
- `--write` required for side effects
- provenance required
- at least two tags required
- restricted prefixes refused by default

## Policy Boundary

The harness must not treat personal connectors as company sources. Meeting,
email, calendar, Slack, or Drive capture must come from company-controlled
sources and pass through private staging plus approval before entering the
shared brain.

For HeyFlora, the live policy and dogfood config live in:

```text
Company_Master/00_README_Drive_Conventions/
```

Future customer deployments should reuse the plugin and supply their own brain
root/config/policy.

## Validate

```bash
bash scripts/validate.sh
```

This compiles the CLIs, validates skills, validates available plugin manifests,
and runs a smoke test against a synthetic non-HeyFlora brain root.

## Docs

- `docs/quickstart.md`
- `docs/capture-policy-template.md`
- `docs/scott-readiness.md`
- `docs/productionization-plan.md`
