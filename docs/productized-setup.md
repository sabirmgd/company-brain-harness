# Productized Setup Plan

The harness should feel simple even though the engine is technical.

## Product Principle

Users should not think:

```text
Which CLI do I run?
```

They should think:

```text
I want to set up my company brain.
```

Claude or Codex routes the request through `brain-start`, identifies the user's
role, and runs the lower-level harness tools internally.

## Public Roles

| Role | Primary job | Skill |
|---|---|---|
| Brain Owner | Approve setup, policy, source rules, restricted access, pilot launch | `brain-owner` |
| Brain Operator | Run daily checks, review queue, keep the brain healthy | `brain-operator` |
| Team Member | Contribute role knowledge and source suggestions | `brain-contribute` |

Internal concepts like source owner, registry status, and promotion rules still
exist, but they should not be the first thing a nontechnical user sees.

## Claude/Codex First Session

User says:

```text
I want to set up my company brain.
```

Agent flow:

1. Route to `brain-start`.
2. Ask whether the user is setting up, operating, or contributing.
3. If setup, route to `brain-owner`.
4. Ask for company name, brain root, Brain Operator, and starter/team mode.
5. Preview scaffold.
6. Write scaffold only after explicit approval.
7. Run readiness checks.
8. Give one next action.

## What Gets Baked Into The Scaffold

`brain-setup.py` should create:

- `START_HERE.md`
- `OWNER_GUIDE.md`
- `OPERATOR_GUIDE.md`
- `TEAM_MEMBER_GUIDE.md`
- `INVITE_TEAM.md`
- `TODAY.md`
- `NEXT_ACTIONS.md`
- routing/config/policy/source registry/staging/indexes

These files turn the brain root itself into an onboarding product.

## Progressive Rollout

### 1. First 20 Minutes

- Create scaffold.
- Choose Brain Owner and Brain Operator.
- Keep sources proposed or excluded.
- Keep the schedule human-gated.
- Do not populate company facts yet.

### 2. First Week

- Team Members run `brain-contribute`.
- Operator runs daily check.
- Owner reviews staged notes and source proposals.
- Personal sources stay excluded.

### 3. Source-Governed Pilot

- Approve company-owned source instances.
- Stage from approved sources.
- Keep final promotion human-approved.
- Review lint and stale notes weekly.

### 4. Operating Brain

- Daily digest can run automatically.
- Approved low-risk sources may stage unattended.
- Auto-promotion remains narrow and explicit.

## Website Documentation Shape

A customer-facing website should have:

1. Start Here
2. Choose Your Role
3. First 20 Minutes
4. First Week
5. Connect Sources Safely
6. Daily Operator Loop
7. Review Queue
8. Advanced Automation

Developer docs should be secondary:

- CLIs
- config file
- source registry schema
- smoke tests
- plugin manifests

## Future Product Surface

The harness can later support a web UI:

- Create client/company brain
- Generate setup commands
- Owner approval checklist
- Source registry editor
- Team invite links
- Staged note review queue
- Daily health digest
- Multi-client operator dashboard

The repo should remain the source of truth for the engine, skills, docs, and
contract even when a website is added.
