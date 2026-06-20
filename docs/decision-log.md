# Decision Log

This log records the major decisions behind the Company Brain Harness. It is not
a complete git history; it is the reasoning map for future maintainers.

## D001: Category Is Company Brain Harness

Decision: position the generic product as Company Brain Harness.

Accepted:

- Company Brain Harness as the reusable category.
- Customer-specific deployments as implementations, not product boundaries.

Rejected:

- Industry-specific "second brain" framing because it makes the generic harness
  sound narrower than the product.
- "Chat with docs" because it ignores governance, source ownership, freshness,
  review, and agent workflows.

Implication:

- Generic docs and code must avoid customer-specific or industry-specific assumptions.
- Customer-specific policy belongs in that customer's brain root.

## D002: Filesystem Root Is The Backend Contract

Decision: treat the brain root as any filesystem-backed folder.

Accepted:

- Google Drive for Desktop.
- Git repo.
- Shared volume.
- Local directory.

Rejected:

- Hardcoding Google Drive as the product.
- Starting with a database or hosted RAG layer before the operating model is
  proven.

Implication:

- Every CLI accepts `--root`.
- Config is relative to the root.
- Smoke tests must use a synthetic generic root.

## D003: Plugin Is The Distribution Unit

Decision: distribute through `plugins/company-brain-harness/`.

Accepted:

- Claude plugin manifest.
- Codex plugin manifest.
- Shared skills.
- Shared CLIs.
- Shared references.

Rejected:

- Local-only installed skills as the source of truth.

Implication:

- The repo is installable and reviewable.
- Version metadata must change when the installed workflow changes.

## D004: Skills Are UX, CLIs Are Enforcement

Decision: skills guide agent behavior; CLIs enforce filesystem behavior.

Accepted:

- Human-friendly workflows in `skills/*/SKILL.md`.
- Policy-sensitive checks in `bin/*.py`.

Rejected:

- Relying only on prompt instructions for safety-critical behavior.
- Hiding setup/schedule/source logic in prose only.

Implication:

- Source checks, path checks, write flags, and validation must be executable.
- Skills should call or reference the CLIs.

## D005: Preview First And `--write` Required

Decision: side-effecting CLIs preview by default and require `--write`.

Accepted:

- `brain-setup.py` writes only with `--write`.
- `brain-schedule.py` writes only with `--write`.
- `stage-brain-note.py` writes only with `--write`.
- Approval/promotion CLIs keep explicit write behavior.

Rejected:

- Silent staging or direct writes from agent instructions.

Implication:

- Smoke tests assert preview behavior.
- Docs must show preview first, then write.

## D006: Source Instance Is The Capture Unit

Decision: every connector job must route through a source instance.

Accepted:

- `source-registry.yml` owns source id, connector, control tier, status,
  credential reference, owner, review owner, capture policy, scope, and routing.

Rejected:

- "Capture from Fireflies" as a broad instruction.
- "Use everyone's personal Gmail/Calendar/Fireflies/Apollo" as a team source.

Implication:

- Shared Apollo/CRM is allowed only as an approved source instance.
- Personal accounts are excluded by default.
- `source-registry-check.py --for-capture` is a gate for adapters.

## D007: Team Brain, Not Personal Brain

Decision: model team roles explicitly.

Accepted:

- Brain Owner.
- Brain Operator.
- Team Member.

Rejected:

- One founder's private connectors becoming the company source of truth.
- Treating a teammate's personal app account as team infrastructure by default.

Implication:

- Setup creates `team.yml`.
- Onboarding asks what each teammate can contribute and what must remain
  personal/private.

## D008: Raw Material Is Not Shared Knowledge

Decision: raw source material stays outside broad shared knowledge by default.

Accepted:

- Curated summaries.
- Decisions.
- Action items.
- Reusable facts.
- Provenance links.

Rejected:

- Raw transcript dumps by default.
- Raw email/calendar capture into shared folders.
- Unreviewed sensitive material in team-readable folders.

Implication:

- The write path is stage -> review -> approve/reject/revise -> promote.
- Capture policy must define exceptions.

## D009: Restricted Paths Are Skipped And Refused By Default

Decision: restricted prefixes are never broad-scanned or written by default.

Accepted:

- Configurable `restricted_prefixes`.
- Default scaffolded prefix `brain/restricted`.
- Legacy prefix `14_Owner_Vault` remains recognized for existing deployments.

Rejected:

- Indexing sensitive folders just because the filesystem is readable.

Implication:

- Health and lint avoid restricted content.
- Promotion/staging refuses restricted targets unless future explicit policy
  support is added.

## D010: Freshness Is A First-Class Concern

Decision: stale and contradictory knowledge must be detected.

Accepted:

- `last_verified`.
- provenance comments.
- `brain-lint.py`.
- source owner review.

Rejected:

- Treating the brain as a write-only archive.

Implication:

- brain/operations/daily/weekly operations include lint.
- Teammates are asked what is stale or risky.

## D011: First Pilot Is Human-Gated

Decision: start with human review before autonomous promotion.

Accepted:

- Scheduled checks.
- Approved-source staging.
- Human approval for final promotion.

Rejected:

- Broad unattended ingestion from day one.
- Auto-promotion for meeting-derived or sensitive material.

Implication:

- `brain-schedule.py` supports `human` and `autonomous` modes.
- The default docs recommend human-gated first two weeks.

## D012: Productization Comes After Governance Works

Decision: connector adapters and hosted product UI come after policy, registry,
staging, and review are proven.

Accepted next:

- Google Workspace adapter.
- Fireflies company workspace adapter.
- GitHub org repo map adapter.
- Shared Apollo/CRM adapter.
- Scheduled runner and digest.
- Customer onboarding form that generates config and registry entries.

Rejected for now:

- Website/product shell before the harness can be safely operated.
- Connector-first product without source governance.

Implication:

- The current harness is usable for pilots.
- The next product layer should automate setup, source approval, scheduling, and
  review without weakening safety.

## D013: Role-Based Front Door Is The Default UX

Decision: make `brain-start` the default entry point and expose Brain Owner,
Brain Operator, and Team Member as the public roles.

Accepted:

- `brain-start` routes ambiguous setup/use requests.
- `brain-owner` guides setup and approvals.
- `brain-operator` runs the daily operating loop.
- `brain-contribute` guides teammate contributions.
- `brain-setup.py` generates root-level role guides and next-action files.

Rejected:

- Making nontechnical users choose between low-level CLIs.
- Leading with internal terms like source registry, promotion CLI, or lint.
- Treating setup as a one-shot scaffold instead of a guided first-session flow.

Implication:

- Docs should start with what users say to Claude/Codex.
- CLIs remain the engine and verification surface.
- The website should mirror the same roles and progressive setup stages.

## D014: Simple-Team Profile Supports Low-Friction Manual Contribution

Decision: support an explicit `simple-team` operating profile alongside the
default `governed` profile.

Accepted:

- `ADD_TO_BRAIN/` as a customer-facing manual contribution drop zone.
- `add-to-brain-digest.py` as the deterministic operator digest.
- Low-risk manual contributions may be processed automatically when policy
  allows it.
- Sensitive, private, credential-like, HR, legal, finance, or unclear material
  remains review-gated.

Rejected:

- Making every customer start with strict item-by-item approval.
- Treating the simple profile as permission to capture personal email, calendar,
  meeting recorder, chat, CRM, or broad raw exports.

Implication:

- `brain-setup.py --operating-profile simple-team` generates the drop zone,
  digest folder, profile docs, and matching config.
- Source connectors remain governed by `source-registry.yml` in all profiles.
- Docs and skill routing must include phrases like "I added something to the
  company brain folder."
