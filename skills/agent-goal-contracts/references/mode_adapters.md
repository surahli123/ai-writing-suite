# Mode Adapters

Mode adapters describe how to use the same contract in different collaboration modes. Each adapter changes emphasis, not the required schema.

## Quick Contract

Use for a routine bounded task. Keep the contract compact and name one clear Oracle.

## Implementation Contract

Use for code changes. Emphasize read-first files, protected files, tests, and diff boundaries.

## Debugging Contract

Use for failures. Emphasize reproduction, root-cause evidence, regression tests, and repeated-failure stop rules.

## Research Contract

Use for source-backed investigation. Emphasize source quality, citation requirements, confidence, and non-authoritative evidence boundaries.

## Long-Run Contract

Use only when the user explicitly asks for long autonomous work. Emphasize budget, checkpoint cadence, stagnation rules, and durable state.

## Handoff Contract

Use when the output is a next-session prompt. Emphasize exact artifacts, current state, first bounded step, and stop line.

## Interview

Use when the objective, scope, or success evidence is unclear. Ask only questions that affect implementation, verification, or safety.

## Tighten

Use when a draft exists but weakens scope, omits the Oracle, or has vague completion criteria. Preserve settled decisions and remove untestable claims.

## Compile

Use when the spec is clear enough to produce a `/goal` contract. Compile to the nine-section schema and validate it.

## Check

Use when the user wants to know whether a runner can safely execute the contract. Check length, runtime assumptions, verification availability, and stop rules.
