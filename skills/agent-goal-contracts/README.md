# Agent Goal Contracts

Turn a messy coding-agent request into a compact `/goal` contract with a real finish line.

Agent Goal Contracts helps Codex, Claude Code, Cursor, and similar coding agents start with the information they need: one goal, context to inspect, constraints to preserve, proof of completion, and stop rules for risk.

It is not a runner, board, or long-running automation system. It prepares the contract that a runner can execute.

## The Problem

Weak prompts sound useful but give the agent too much room to wander:

```text
Fix the billing page and make it better. Keep going until it works.
```

A better contract tells the agent what to read, what not to touch, how to prove success, and when to stop:

```text
/goal
GOAL:
Make the billing settings page usable on desktop and mobile without changing Stripe webhook or pricing logic.

CONTEXT:
- Read AGENTS.md and the existing billing settings page before editing.
- Start from the current loading, error, and mobile states.

CONSTRAINTS:
- Do not change Stripe webhook handling, pricing logic, database schema, or public API shapes.
- Keep the UI aligned with the existing settings patterns.

ORACLE:
- Focused UI tests or the repo-local equivalent pass.
- Manual desktop and mobile checks show loading, error, and upgrade states working.

DONE WHEN:
- Loading, error, and upgrade states are visible and usable.
- Mobile layout has no overlap or clipped controls.
- Verification evidence is reported in the final output.

VERIFY:
- Run the focused repo-local test command.
- Run the repo-local lint or typecheck command if available.
- Capture manual desktop and mobile evidence if automated browser checks are not available.

ITERATION POLICY:
- Make one focused UI change, verify it, then continue only on the next failing state.

STOP RULES:
- Stop before touching payment-risky systems, schema, secrets, production credentials, or unclear product decisions.
- Stop after three failed attempts on the same symptom and report the root-cause hypothesis.

OUTPUT:
- Report changed files, verification, remaining risk, and any follow-up that stayed out of scope.
```

## What It Produces

Every portable contract uses nine sections:

| Section | Purpose |
| --- | --- |
| `GOAL` | The single owner outcome. |
| `CONTEXT` | Files, docs, logs, issues, screenshots, or plans to read first. |
| `CONSTRAINTS` | Scope boundaries, non-goals, protected files, and safety rules. |
| `ORACLE` | The observable evidence source that proves completion. |
| `DONE WHEN` | Concrete acceptance criteria. |
| `VERIFY` | Commands, checks, screenshots, reports, or review gates to run fresh. |
| `ITERATION POLICY` | How the agent chooses the next action after each attempt. |
| `STOP RULES` | When to stop instead of guessing or widening scope. |
| `OUTPUT` | What the final report must include. |

The `/goal` itself should stay short. Put long background, candidate ideas, and detailed plans in linked artifacts unless they are execution-critical.

## How It Thinks

```text
Intent -> Contract -> Oracle -> Runner Adapter -> Proof
```

- `Intent`: the rough thing the user actually wants.
- `Contract`: the portable nine-section goal.
- `Oracle`: the test, artifact, screenshot, benchmark, source-backed answer, or human decision that proves the outcome.
- `Runner Adapter`: optional runtime-specific phrasing for Codex `/goal`, Claude Code, a GitHub issue, or a private local runner.
- `Proof`: the final evidence report mapped back to `DONE WHEN`.

No Oracle, no serious goal.

## Modes

Use the same contract shape with different emphasis:

- `quick_contract`: routine bounded work.
- `implementation_contract`: code changes with tests and file boundaries.
- `debugging_contract`: reproduction, root cause, fix, and regression proof.
- `research_contract`: source quality, confidence, and evidence boundaries.
- `long_run_contract`: explicit budget, checkpoints, stagnation rules, and durable state.
- `handoff_contract`: exact artifacts, current state, first bounded step, and stop line.

## Install

Clone or copy this repo, then symlink the skill into your Codex skills directory:

```bash
ln -s "$(pwd)/skills/agent-goal-contracts" ~/.codex/skills/agent-goal-contracts
```

Restart Codex so the skill list refreshes.

## Use

Ask for a contract from a rough request:

```text
Use $agent-goal-contracts to turn this into a bounded /goal:
<paste messy task here>
```

Ask for a review-only pass when you do not want an executable contract yet:

```text
Use $agent-goal-contracts to tighten this goal contract, but do not execute it.
```

## Validate

Validate a contract file:

```bash
python3 scripts/validate_contract.py path/to/GOAL.md
```

Validate piped text:

```bash
cat path/to/GOAL.md | python3 scripts/validate_contract.py
```

Validate paste-ready slash-command text against the stricter runtime target:

```bash
python3 scripts/validate_contract.py --strict-runtime-target path/to/GOAL.md
```

The validator checks:

- text starts with `/goal`
- required sections are present
- required sections are not empty
- hidden flag-shaped slash text is rejected
- hard length limit is respected
- optional runtime target is respected

## Good For

- turning vague feature work into a verifiable task
- preparing a clean handoff for another agent session
- stopping goal loops from drifting into adjacent work
- defining proof before long-running agent work begins
- converting rescue prompts into bounded contracts

## Not For

- one-line edits that are easier to do directly
- broad strategy with no auditable finish line
- tasks requiring missing secrets or production credentials
- replacing a real project plan when the work still needs design decisions

## References And Attribution

This is an adapted, independently named public skill. It uses high-level ideas from several goal-related projects while keeping attribution explicit:

- [`michaelpersonal/goal-forge`](https://github.com/michaelpersonal/goal-forge): adapted base idea for compact autonomous goal contracts.
- [`grp06/goalcraft`](https://github.com/grp06/goalcraft): MIT-licensed inspiration for concise `/goal` launcher contracts, verification surfaces, and stop conditions.
- [`tolibear/goalbuddy`](https://github.com/tolibear/goalbuddy): MIT-licensed inspiration for the Oracle and proof-loop framing.
- [`majiayu000/awesome-goal-prompts`](https://github.com/majiayu000/awesome-goal-prompts): CC0 reference patterns for runnable rescue contracts and goal templates.
- [`lidangzzz/goal-driven`](https://github.com/lidangzzz/goal-driven): conceptual inspiration for criteria-driven continuation. goal-driven is used as conceptual inspiration only because no license endpoint was available during the attribution check.

See [`NOTICE.md`](NOTICE.md) for the reuse boundary.
