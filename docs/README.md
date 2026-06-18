# Company Brain Harness Docs

Start here when reviewing, installing, operating, or productizing the harness.

## Orientation

- [Quickstart](quickstart.md): install, scaffold, verify, and use skills.
- [Harness Architecture](harness-architecture.md): how the layers fit together.
- [Decision Log](decision-log.md): why each major layer exists.

## Operating The Brain

- [Team Operating Model](team-operating-model.md): Champion, Operator,
  teammate, and source-owner responsibilities.
- [Scheduling Guide](scheduling-guide.md): human-gated and autonomous operating
  loops.
- [Team Onboarding Form](team-onboarding-form.md): prompts for team members to
  populate the brain later.

## Governance

- [Capture Policy Template](capture-policy-template.md): policy boundary for
  source capture, raw material, and sensitive routing.
- [Source Registry Design](source-registry-design.md): many accounts per tool,
  source ownership, approval, routing, and enforcement.
- [Source Registry Template](source-registry-template.yml): starter
  `source-registry.yml`.

## Pilot And Productization

- [Pilot Readiness Checklist](pilot-readiness.md): new-customer pilot readiness.
- [Customer Handoff Message](customer-handoff-message.md): concise handoff
  language.
- [Productionization Plan](productionization-plan.md): what remains before a
  broader product.

## Maintenance Rule

When a behavior, safety rule, source policy, or install path changes, update:

1. the relevant CLI or skill
2. the top-level `README.md`
3. the architecture or decision doc when the change affects a layer decision
4. the smoke test if the behavior is executable
