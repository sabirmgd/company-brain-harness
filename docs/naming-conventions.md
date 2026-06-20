# Naming Conventions

The harness uses domain-first names so a new team can understand the brain
without learning a numbering scheme or a customer-specific folder tradition.

## Principles

- Use `brain/` for curated company knowledge.
- Use `system/` for harness configuration, staging, evidence, raw captures,
  source registry, sync state, and operating policy.
- Use lowercase kebab-case for normal files and folders.
- Use `README.md` as the entrypoint for every folder.
- Prefer durable business domains over temporary team names.
- Do not encode sort order in folder names.
- Do not name folders after a dogfood customer, implementation person, or
  storage backend.
- Keep raw source material private under `system/staging/raw/`; raw material is
  evidence, not shared knowledge.

## Canonical Top Level

```text
CLAUDE.md
README.md
company-brain.yml
start-here.md
owner-guide.md
operator-guide.md
team-member-guide.md
invite-team.md
today.md
next-actions.md
brain/
system/
```

## Canonical Brain Domains

```text
brain/company/
brain/product/
brain/engineering/
brain/go-to-market/
brain/customers/
brain/operations/
brain/intelligence/
brain/sources/
brain/restricted/
brain/archive/
```

## Canonical System Domains

```text
system/capture-policy.md
system/connections.md
system/flows.md
system/status.md
system/schedule.md
system/naming-conventions.md
system/source-registry.yml
system/source-sync-state.json
system/team.yml
system/staging/
```

## Why This Shape

The old numbered-folder model was optimized for a single drive view. The new
model is optimized for agents, operators, source governance, and new customers:

- humans can infer folder purpose from the name
- agents can route by domain nouns
- system state is separated from curated knowledge
- raw evidence is kept away from shared notes
- another company can adopt the harness without inheriting dogfood assumptions
