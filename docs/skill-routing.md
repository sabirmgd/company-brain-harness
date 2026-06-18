# Plain-English Skill Routing

Users do not need to call skills by name. They should open Claude Code or Codex
in the brain root and say what they want.

The skill name and description are the routing surface. Each skill description
therefore includes plain-English trigger phrases that an owner, operator, or
team member is likely to type.

## Default Rule

If the request is broad or the user's role is unclear, route to `brain-start`.

Examples:

- "I want to set up my company brain."
- "Help me start."
- "I want to use the brain."
- "What should I do next?"
- "I want to add knowledge, but I do not know where to start."

`brain-start` should ask a simple role question, then hand off to the right
workflow.

## Brain Owner Use Cases

| User says | Skill | What the agent should do |
|---|---|---|
| "I own this brain." | `brain-owner` | Walk through owner decisions. |
| "I want to launch the company brain." | `brain-owner` | Check setup, policy, source approvals, and launch readiness. |
| "Approve the capture policy." | `brain-owner` | Review policy implications before approval. |
| "Approve these sources." | `brain-owner` and `sources-check` | Validate exact source instances, then route approval decision. |
| "Choose the operator." | `brain-owner` | Record or guide the Brain Operator decision. |
| "Invite the team." | `brain-owner` | Use the invite/team onboarding flow. |
| "Is this ready for a pilot?" | `brain-owner` and `brain-health` | Check readiness and owner blockers. |
| "Create the brain files." | `brain-setup` | Preview scaffold, then write only after explicit approval. |

Owner setup should stay guided and plain-language. The agent may run CLIs
internally, but it should not make the owner choose scripts.

## Brain Operator Use Cases

| User says | Skill | What the agent should do |
|---|---|---|
| "Run today's brain check." | `brain-operator` | Run connection, source, health, lint, and queue checks. |
| "Do the morning review." | `brain-operator` | Produce status, review items, and next actions. |
| "What needs review?" | `brain-operator` | Inspect staged notes, proposed sources, stale notes, and blockers. |
| "Check the queue." | `approve-brain-notes` | List staged proposals and recommend decisions. |
| "Approve these notes." | `approve-brain-notes` | Preview decisions and write only after explicit approval. |
| "What is outdated?" | `brain-lint` | Find stale notes, broken links, missing provenance, and contradictions. |
| "Is the brain ready?" | `brain-health` | Report readiness and blockers. |
| "Schedule the daily check." | `brain-schedule` | Create human-gated or autonomous operating schedule. |
| "Run this without a human." | `brain-schedule` | Define automation guardrails and what still requires approval. |

Operator workflows can be automated over time, but promotion and sensitive
capture remain explicit decisions unless policy says otherwise.

## Team Member Use Cases

| User says | Skill | What the agent should do |
|---|---|---|
| "I want to add what I know." | `brain-contribute` | Ask a short contribution interview and stage a proposal. |
| "Document my role." | `brain-contribute` | Capture role knowledge and reviewer. |
| "Share my process." | `brain-contribute` | Turn workflow knowledge into staged notes. |
| "Add this SOP." | `brain-contribute` or `brain-intake` | Use contribution for Q&A, intake for a provided artifact. |
| "This fact is stale." | `brain-contribute` and `brain-lint` | Stage a correction and flag stale source. |
| "Can my personal account feed the brain?" | `sources-check` | Default to no unless delegated, scoped, approved, and registered. |
| "Where should this doc go?" | `brain-intake` | Classify and stage the artifact for review. |

Team members should not need to understand source registries, staging folders,
or CLI flags. The agent handles those mechanics.

## Source And Capture Use Cases

| User says | Skill | What the agent should do |
|---|---|---|
| "Connect Slack." | `sources-check` | Ask which workspace/channel and who owns it. |
| "Can Gmail feed the brain?" | `sources-check` | Require org-wide scope and exclude personal inboxes by default. |
| "Use our Fireflies meetings." | `sources-check` and `meeting-to-brain` | Validate the company-controlled source before staging meeting notes. |
| "Add this meeting transcript." | `meeting-to-brain` | Convert approved meeting material into staged notes. |
| "Process this call recording." | `meeting-to-brain` | Extract decisions, action items, and reusable facts. |
| "Use our Apollo account." | `sources-check` | Validate exact workspace/account, scope, approval, and route. |

A connector type is never enough. The skill should look for the exact approved
account, workspace, channel, folder, inbox, calendar, repo org, or API key
reference.

## Artifact And Project Use Cases

| User says | Skill | What the agent should do |
|---|---|---|
| "Add this doc to the brain." | `brain-intake` | Stage the artifact with provenance. |
| "Turn this into a brain note." | `brain-intake` | Create a proposed note, not a direct write. |
| "Interview me to populate the brain." | `brain-onboard` | Ask structured questions and stage notes. |
| "Build a POC." | `repo-aware-poc` | Read repo map and stack rules before implementation. |
| "Where should this code live?" | `repo-aware-poc` | Use existing repo conventions and approved GitHub source. |

## Collision Rules

- Broad setup, unclear role, or first session: `brain-start`.
- Owner/founder/admin/team lead decisions: `brain-owner`.
- Daily checks, queue review, next actions: `brain-operator`.
- A team member adding what they personally know: `brain-contribute`.
- A structured interview to collect broader context: `brain-onboard`.
- A provided artifact, doc, pasted text, or link: `brain-intake`.
- A meeting transcript, recap, or recording export: `meeting-to-brain`.
- A source account, workspace, channel, inbox, calendar, repo org, or API key:
  `sources-check`.
- Staged proposal decisions: `approve-brain-notes`.
- Schedule or automation policy: `brain-schedule`.
- Staleness, contradictions, broken links, or provenance cleanup: `brain-lint`.
- POCs, prototypes, repo placement, and stack fit: `repo-aware-poc`.

## Safety Rule

Implicit skill invocation is not implicit permission to mutate the shared brain.

Skills may preview, inspect, and guide automatically. Writes still follow the
harness rules: preview first, `--write` for side effects, and explicit approval
for promotion or sensitive capture.
