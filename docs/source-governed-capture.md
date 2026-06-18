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

Disallowed by default:

- personal recorder accounts
- raw transcript dumps into shared knowledge

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
- updates cursor and hash state

`source-extract.py`:

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
