# Install And Runtime Flow

This harness is distributed as one plugin bundle. Customers do not install
standalone skill files.

## What Install Downloads

When Claude Code or Codex installs `company-brain-harness@company-brain`, the
installed plugin contains:

```text
skills/       plain-English workflows loaded by Claude or Codex
bin/          Python helper CLIs used by the skills and by automation
references/   shared harness contract used by the skills
README.md     plugin-local usage notes
```

The skill files are the routing and instruction layer. The `bin/` scripts are
the deterministic action layer. Installing the plugin brings both.

## What Install Does Not Create

Installing the plugin does not create a company brain and does not populate
company knowledge. The company brain is a separate filesystem-backed root:

```text
Google Drive folder
git repository
shared volume
local folder
```

The plugin only mutates a brain root after the user chooses one and approves a
write path.

## First User Flow

1. Install the plugin once in Claude Code or Codex.
2. Open Claude Code or Codex in the target brain folder, or set `BRAIN_ROOT`.
3. Say: `I want to set up my company brain.`
4. The agent routes to `brain-start`.
5. The agent identifies the role: Brain Owner, Brain Operator, or Team Member.
6. Setup previews the scaffold first.
7. Setup writes only after explicit approval.
8. Daily operation uses the same installed plugin to run checks, lint, source
   registry validation, staging, approval, and promotion.

## Where The Scripts Run From

For installed plugins, the agent should run scripts from the installed plugin
root, for example:

```text
<installed-plugin-root>/bin/brain-setup.py
<installed-plugin-root>/bin/brain-health.py
<installed-plugin-root>/bin/source-registry-check.py
```

For local development, the same scripts live in:

```text
plugins/company-brain-harness/bin/
```

Do not tell a normal customer to clone the repository after the plugin is
installed. Cloning is only for development, auditing, or offline/manual CLI use.

## Brain Root Versus Harness

The harness and the brain are different things:

| Thing | Purpose |
|---|---|
| Installed plugin | Skills, CLIs, and harness contract |
| Brain root | Customer's company memory and private system state |
| Source systems | External apps such as Slack, Confluence, CRM, Fireflies, GitHub |

The brain root stores `company-brain.yml`, `CLAUDE.md`, `brain/`, and
`system/`. It should not copy the harness scripts into every brain.
