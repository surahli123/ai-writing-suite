# Personal Productivity Skills

Small public skills for making agent work easier to start, easier to verify, and harder to let drift.

This repo begins with one skill:

- [`agent-goal-contracts`](skills/agent-goal-contracts/README.md): turn a messy coding-agent request into a compact, verifiable `/goal` contract.

## Why This Exists

Coding agents often fail for boring reasons:

- the goal is too vague
- the scope keeps expanding
- "done" depends on vibes
- the agent changes files it should not touch
- verification is skipped or remembered instead of rerun

These skills are meant to package the opposite habit: one clear outcome, real context, hard constraints, proof, and stop rules.

## Start Here

Use `agent-goal-contracts` when you have a rough task like:

```text
The billing settings page is half-done. The upgrade button works, but loading and error states are rough, and mobile may be broken. Make it usable without touching Stripe webhook logic.
```

The skill turns that into a contract with:

```text
GOAL:
CONTEXT:
CONSTRAINTS:
ORACLE:
DONE WHEN:
VERIFY:
ITERATION POLICY:
STOP RULES:
OUTPUT:
```

The important field is `ORACLE`: the evidence source that proves the work is complete, such as tests, a screenshot, a generated artifact, a benchmark, or a review gate.

## Repo Layout

```text
skills/
  agent-goal-contracts/
    SKILL.md
    README.md
    NOTICE.md
    references/
    scripts/
    tests/
```

## Validate

Run the current tests:

```bash
cd skills/agent-goal-contracts
python3 -m unittest discover -s tests
```

Validate a contract:

```bash
python3 scripts/validate_contract.py path/to/GOAL.md
```

Validate paste-ready `/goal` text against the stricter runtime target:

```bash
python3 scripts/validate_contract.py --strict-runtime-target path/to/GOAL.md
```

## Attribution

Each skill carries its own attribution boundary. Start with:

- [`agent-goal-contracts/NOTICE.md`](skills/agent-goal-contracts/NOTICE.md)
- [`agent-goal-contracts/README.md`](skills/agent-goal-contracts/README.md)
