---
name: agent-goal-contracts
description: Convert a rough implementation request into a portable /goal contract with explicit success criteria, Oracle evidence, runtime boundaries, and runner-specific adaptation notes.
---

# Agent Goal Contracts

Agent Goal Contracts helps turn a rough software task into a compact, executable `/goal` contract for an autonomous coding agent.

Use it when the user wants to:

- clarify an implementation objective before execution
- compile a repo handoff into a paste-ready `/goal`
- make success criteria measurable
- define stop rules before a long local run
- adapt the same task to different agent runners

The public default is runner-neutral. Local Codex behavior is an optional Runner Adapter, not the core contract.

## Core Ideas

- A goal contract is a short operational brief, not a full product spec.
- The Oracle is the evidence source that proves the task is done.
- The Runner Adapter maps a stable contract into a specific agent runtime, prompt, or CLI.
- The contract should make the first action, allowed scope, verification path, and stop condition obvious.
- Detailed background belongs in linked artifacts; the `/goal` body stays compact.

## Contract Sections

Use these headings for the portable contract:

1. `GOAL`
2. `CONTEXT`
3. `CONSTRAINTS`
4. `ORACLE`
5. `DONE WHEN`
6. `VERIFY`
7. `ITERATION POLICY`
8. `STOP RULES`
9. `OUTPUT`

The `ORACLE` section names the evidence source. It can be a test command, build result, static analysis output, manual acceptance check, generated artifact, review gate, or external API response when that source is safe to query.

## Workflow

1. Interview only for decisions that affect scope, risk, or verification.
2. Draft the contract using the nine required sections.
3. Check that each `DONE WHEN` item maps to `VERIFY` or `ORACLE`.
4. Apply a Runner Adapter only after the portable contract is sound.
5. Validate the final text with `scripts/validate_contract.py`.

## Runner Adapter

A Runner Adapter may add runtime-specific launch instructions, length targets, or handoff phrasing. It must not change the goal, broaden scope, weaken stop rules, or hide local assumptions.

Examples:

- Codex `/goal` prompt
- Claude Code task prompt
- GitHub issue handoff
- CI-backed agent runner
- local private Codex runner prompt

## Output

Return the final contract, the chosen Runner Adapter if any, validation status, and any remaining risks that prevent safe execution.
