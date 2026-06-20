# Company Brain Harness Docs

Start here when reviewing, installing, operating, or productizing the harness.

## Orientation

- [Start Here](start-here.md): plain-language first session flow for Claude or Codex.
- [Plain-English Skill Routing](skill-routing.md): what customers say and which
  skill should run.
- [First 20 Minutes](first-20-minutes.md): starter setup with the Brain Owner.
- [First Week](first-week.md): teammate contribution and review loop.
- [Productized Setup Plan](productized-setup.md): how the role-based setup
  becomes a customer-facing product.
- [Quickstart](quickstart.md): install, scaffold, verify, and use skills.
- [Harness Architecture](harness-architecture.md): how the layers fit together.
- [Naming Conventions](naming-conventions.md): canonical brain/system taxonomy
  and path naming rules.
- [Decision Log](decision-log.md): why each major layer exists.

## Operating The Brain

- [Team Operating Model](team-operating-model.md): Brain Owner, Brain Operator,
  and Team Member responsibilities.
- [Operating Rhythm](operating-rhythm.md): daily, weekly, and monthly operating loops.
- [Brain Owner Role](roles/brain-owner.md): owner decisions and approval path.
- [Brain Operator Role](roles/brain-operator.md): daily operations and review queue.
- [Team Member Role](roles/team-member.md): contribution flow and source questions.
- [Scheduling Guide](scheduling-guide.md): human-gated and autonomous operating
  loops.
- [Team Onboarding Form](team-onboarding-form.md): prompts for team members to
  populate the brain later.

## Governance

- [Capture Policy Template](capture-policy-template.md): policy boundary for
  source capture, raw material, and sensitive routing.
- [Source Registry Design](source-registry-design.md): many accounts per tool,
  source ownership, approval, routing, and enforcement.
- [Source-Governed Capture](source-governed-capture.md): privacy-first pull,
  evidence, extraction, cursor, and staging flow.
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
