# Team Operating Model

The Company Brain Harness is a team system. It should not depend on one
founder's personal connectors or one local machine.

## Roles

| Role | Owns |
|---|---|
| Brain Owner | Policy, source approval, review standards, restricted access |
| Brain Operator | Daily checks, lint, staging queue, schedule execution |
| Team Member | Role knowledge, source suggestions, corrections, review feedback |

One person can hold multiple roles during a pilot. Before broad rollout, make
the roles explicit.

## Daily Flow

```text
connections -> sources -> health -> lint -> staged queue -> punch list
```

The punch list should say:

- blockers
- warnings
- staged proposals waiting for review
- stale or contradictory notes
- next three fixes

## Team Member Inputs

Ask each teammate:

- What role do you play and what decisions do you own?
- What workflows do people ask you about repeatedly?
- Which company-owned or shared tools do you use?
- Which personal tools should stay excluded?
- Is there a shared Apollo, CRM, Fireflies, Slack, Drive, Calendar, GitHub, or Notion workspace?
- What source-derived notes would help the team if curated?
- Who should review notes from your area?
- What current brain knowledge is stale, wrong, or risky?
- What must route to `Restricted/` or stay out entirely?

## Source Promotion

Source suggestions become source registry entries only after the Brain Owner
decides:

- exact source instance
- control tier
- owner and review owner
- capture scope and exclusions
- destination route
- retention rule
- approval requirement

Personal accounts are excluded by default. A delegated personal account is an
exception, not the normal operating model.

## Knowledge Maintenance

The brain should evolve in place:

- update canonical notes instead of creating `v2` duplicates
- keep raw evidence outside broad shared knowledge unless policy allows it
- add provenance comments for source-backed claims
- use `last_verified` to make freshness visible
- archive deprecated notes when they are no longer useful
- route contradictions to the source owner or Brain Owner

## Pilot Readiness

A team pilot is ready when:

- `brain-setup.py` has produced the scaffold
- source registry validates
- restricted folder permissions are checked
- first two-week schedule is chosen
- Brain Owner and Brain Operator are named
- every teammate understands staging before promotion
- no personal connector is treated as a company source
