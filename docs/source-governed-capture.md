# Source-Governed Capture

Source-governed capture is the product layer that keeps the company brain useful
without turning it into surveillance.

## Core Principle

```text
Raw source access is not brain access.
```

Every connector follows the same path:

```text
approved source -> scoped pull -> private evidence -> extraction -> staged proposal -> review -> approved brain note
```

Private evidence has two lanes:

| Lane | Location | Purpose |
|---|---|---|
| Normalized evidence | `00_Company_Brain_Conventions/90_Staging/evidence/` | JSONL records used for dedupe, extraction, review, and promotion. |
| Raw evidence | `00_Company_Brain_Conventions/90_Staging/raw/` | Optional raw source material retained by policy for audit or deeper review. |

Raw evidence is not shared brain knowledge. A staged or approved note may point
to a private raw evidence file, but it should not copy raw transcripts, emails,
or code into the shared note.

## Role Responsibilities

| Role | Responsibilities |
|---|---|
| Brain Owner | Approves tools, scope, visibility, retention, restricted routes, and reviewers. |
| Brain Operator | Configures credentials, runs source checks, syncs approved sources, monitors cursors and failures. |
| Team Member | Contributes knowledge, suggests sources, delegates personal sources narrowly, and can revoke delegation. |

## Source Types

### Email

Email is valuable, but personal inboxes are private by default.

Allowed patterns:

- shared inboxes
- company aliases
- delegated personal email scoped by client, label, sender domain, thread, or date range

Disallowed by default:

- whole personal mailboxes
- family/personal threads
- HR, legal, finance, compensation, and private threads unless explicitly restricted

Allowed brain artifacts:

- customer facts
- commitments
- account updates
- action items
- decisions

Not allowed:

- raw emails by default
- private messages
- credential values

### Slack

Allowed patterns:

- public/company channels
- approved private channels with named reviewer

Disallowed by default:

- DMs
- private channels without approval
- broad workspace scrape

### Confluence

Allowed patterns:

- company spaces
- published pages with company-wide visibility

Disallowed by default:

- user spaces
- drafts
- restricted spaces unless routed restricted

Adapter:

```bash
python3 plugins/company-brain-harness/bin/confluence-export.py \
  --base-url "https://example.atlassian.net/wiki" \
  --space-key "TEAM" \
  --output-jsonl records.jsonl
```

`confluence-export.py` reads Atlassian credentials from
`ATLASSIAN_EMAIL` and `ATLASSIAN_API_TOKEN` by default. It writes normalized
JSONL only; `source-pull.py` and `source-extract.py` still own evidence,
dedupe, privacy checks, and staging.

Use `--include-raw` only when the source registry allows raw retention. The raw
Confluence storage body is stored privately by `source-pull.py`, not promoted to
shared knowledge.

### CRM

Allowed patterns:

- company-owned account records
- approved account-manager notes

Disallowed by default:

- private notes
- billing credentials
- personal prospecting lists

### Meetings

Allowed patterns:

- company meeting recorder workspace
- customer-owned meeting source for that customer brain
- delegated personal recorder scoped by project/client/search term

Disallowed by default:

- personal recorder accounts
- raw transcript dumps into shared knowledge

Adapter:

```bash
python3 plugins/company-brain-harness/bin/fireflies-export.py \
  --search "Project Name" \
  --output-jsonl records.jsonl
```

`fireflies-export.py` exports Fireflies summary fields by default. Use
`--include-raw-transcript` only when the source registry allows raw retention.
Sentence-level transcript text is stored privately by `source-pull.py`, not
promoted to shared knowledge.

### Code Repositories

Code is a source of operating truth. It should feed the brain as repo maps and
architecture references, while detailed implementation discovery can remain
on-demand through GitHub, GitLab, or local git.

Allowed patterns:

- company-owned repos
- local checked-out repos used by the team
- GitHub/GitLab repos with approved org/project scope

Disallowed by default:

- private personal forks
- credential files, local `.env`, logs, and generated dependency folders
- broad scans of every repo on a developer machine

Adapter:

```bash
python3 plugins/company-brain-harness/bin/repo-map-export.py \
  --repo /path/to/api \
  --repo /path/to/frontend \
  --output-jsonl records.jsonl
```

The brain should store repo maps, stack markers, key docs, recent commits, and
source links. Agents can then decide when to inspect live code directly rather
than copying large code bodies into the brain.

## Executable Contract

Connector adapters should produce normalized JSONL records:

```json
{
  "external_id": "thread-123",
  "title": "Client renewal thread",
  "summary": "Client confirmed renewal timing and asked for implementation checklist.",
  "target_path": "Intelligence/accounts/client-renewal.md",
  "tags": ["email", "client"],
  "artifact_type": "customer_fact",
  "visibility": "team",
  "author": "Shared Inbox",
  "cursor": "next-page-token"
}
```

Adapters may also provide raw material for private storage:

```json
{
  "external_id": "meeting-123",
  "title": "Project weekly sync",
  "summary": "The team agreed on the launch checklist.",
  "raw_body": "Speaker A: ...",
  "raw_format": "md",
  "artifact_type": "meeting_summary",
  "visibility": "team"
}
```

`source-pull.py` writes raw fields to `90_Staging/raw/<source-id>/...` only
when the source has `raw_policy.store_raw: private_only` or `temporary`.
Sources with `raw_policy.store_raw: false` keep only normalized evidence.

Then the operator runs:

```bash
python3 plugins/company-brain-harness/bin/source-pull.py \
  --root "$BRAIN_ROOT" \
  --source-id "<source-id>" \
  --input-jsonl records.jsonl \
  --cursor "<next-cursor>" \
  --write

python3 plugins/company-brain-harness/bin/source-extract.py \
  --root "$BRAIN_ROOT" \
  --source-id "<source-id>" \
  --write
```

`source-pull.py`:

- validates the source is capture-eligible
- refuses personal/private visibility by default
- refuses records that look like secrets
- writes normalized evidence under staging
- writes optional raw sidecars only when source policy allows it
- updates cursor and hash state

`source-extract.py`:

- collapses repeated evidence to the latest record per external item
- respects `artifact_policy.allowed`
- refuses blocked artifact types
- creates staged proposals only
- updates staged hash state

## State

The harness tracks state in:

```text
00_Company_Brain_Conventions/source-sync-state.json
```

This records cursors, last successful pull/extract, per-item hashes, and staged
hashes. Repeated runs should pull or stage only new or changed records.

## Schedule Integration

The daily operator loop should include source sync only after sources are
approved:

1. connection check
2. source registry check
3. pull approved source records
4. extract allowed artifacts into staged proposals
5. health check
6. lint
7. review queue

Final promotion remains a separate approval step.
