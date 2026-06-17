---
name: repo-aware-poc
description: Keep prototypes and proof-of-concepts aligned with the company's GitHub org, repo map, stack conventions, and build patterns. Use when planning or building a POC, choosing where code should live, checking stack fit, or making an agent aware of existing repositories.
---

# Repo Aware POC

Before building a prototype, ground the work in the company repo map and stack conventions.

## Workflow

1. Resolve the brain root.
2. Read the repository index and stack conventions when present, commonly:
   - `10_Engineering_and_Tech/06_Repositories_Index/`
   - `10_Engineering_and_Tech/02_Tech_Stack_Documentation/`
3. If those docs are stale or missing and GitHub access is configured, run `connections-check.py --live` and refresh the repo map through the company's approved GitHub process.
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
