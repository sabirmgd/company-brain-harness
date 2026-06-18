# Start Here

This is the customer-facing starting point for the Company Brain Harness.

You do not need to know the CLIs. Claude or Codex can run them internally.

## Install

```bash
claude plugin marketplace add sabirmgd/company-brain-harness
claude plugin install company-brain-harness@company-brain
```

or:

```bash
codex plugin marketplace add sabirmgd/company-brain-harness
codex plugin add company-brain-harness@company-brain
```

## First Session

Open Claude Code or Codex and say:

```text
I want to set up my company brain.
```

If you prefer an explicit skill:

```text
$brain-start
```

Claude Code:

```text
/company-brain-harness:brain-start
```

## Choose Your Role

The agent will ask which role you are playing:

| Role | Use this when |
|---|---|
| Brain Owner | You are responsible for approving setup, policy, sources, and launch |
| Brain Operator | You run checks, review queue, and keep the brain healthy |
| Team Member | You want to contribute what you know |

If you are unsure, choose Brain Owner for the first setup session.

## What Happens In The Background

The agent may run harness tools internally:

- setup scaffold
- source registry check
- health check
- lint
- schedule generation
- staging and approval

You should see plain-language status and next actions, not command output.

## What The Harness Will Not Do Automatically

- It will not populate company knowledge during setup.
- It will not connect personal accounts as company sources.
- It will not promote notes without approval.
- It will not inspect restricted folders.
- It will not ask you to paste secrets into chat.
