# Operating Rhythm

The Company Brain works because it is operated, not because it was scaffolded.

## Daily Loop

Brain Operator:

```text
Run today's company brain check.
```

The agent should run:

1. connection check
2. source registry check
3. approved source pull into private evidence
4. extraction into staged proposals
5. health check
6. lint
7. `ADD_TO_BRAIN/` digest when using `simple-team`
8. staged queue and flagged item review
9. punch list

Output:

```text
Today's brain check: Ready / Needs review / Blocked

Needs review:
- staged notes
- proposed sources
- stale notes
- broken links

Next three actions:
1.
2.
3.
```

## Weekly Loop

- review stale notes
- review source ownership
- invite missing teammates
- resolve staged proposals
- update source registry
- check restricted access

## Monthly Loop

- review capture policy
- review auto-promotion rules
- review retention
- review active/inactive team members
- archive deprecated knowledge

## Automation Rule

Automate checks before automating writes.

Good first automation:

- daily health/lint/source digest
- `ADD_TO_BRAIN/` digest for simple-team manual contributions
- staged proposals from approved low-risk sources
- low-risk manual drop-zone processing when policy allows it

Keep human-approved:

- meeting-derived notes during pilot
- HR/legal/finance/customer-confidential notes
- strategy-changing notes
- restricted access
- new source approvals
- broad personal-source connector capture
