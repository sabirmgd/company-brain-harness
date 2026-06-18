---
name: repo-aware-poc
description: Keep prototypes and proof-of-concepts aligned with the company's repo map, GitHub org, stack conventions, and build patterns. Use when the user says build a POC, prototype this, where should this code live, check existing repos, use our stack, make the agent repo-aware, or plan an MVP.
---

# Repo Aware POC

Before building a prototype, ground the work in the company repo map and stack conventions.

## Workflow

1. Resolve the brain root.
2. Read the repository index and stack conventions when present. Common generic destinations are:
   - `Departments/Engineering/`
   - `Projects/`
   - `Context/`
   - a deployment-specific repo map folder named in `CLAUDE.md`
3. If those docs are stale or missing and GitHub access is configured, validate the approved GitHub source instance before refreshing the repo map.
4. Decide where the POC belongs:
   - existing product repo
   - site/template repo
   - proof-of-concepts repo
   - throwaway local scratch
5. State the chosen stack, why it matches existing conventions, and what not to introduce.
6. If the POC creates reusable knowledge, stage a brain note through `brain-intake`.

## Guardrails

- Do not create a new repo when an existing POC or template repo is the right home.
- Do not introduce a new framework because the agent prefers it.
- Keep skills, agents, and role bundles in the registry/control-plane repo when that is the established source of truth.
- Keep tenant data and customer-specific runtime state out of central definitions.
- Do not scrape personal GitHub accounts for company repo knowledge unless they are explicitly registered and approved sources.
