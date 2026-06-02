# Contract Schema

A portable goal contract begins with `/goal` and includes these required sections:

1. `GOAL`
2. `CONTEXT`
3. `CONSTRAINTS`
4. `ORACLE`
5. `DONE WHEN`
6. `VERIFY`
7. `ITERATION POLICY`
8. `STOP RULES`
9. `OUTPUT`

## Section Intent

- `GOAL`: the bounded objective.
- `CONTEXT`: repo, files, handoff docs, evidence, and first read targets.
- `CONSTRAINTS`: scope limits, protected files, non-goals, safety rules.
- `ORACLE`: the evidence source that proves completion.
- `DONE WHEN`: measurable acceptance criteria.
- `VERIFY`: commands or manual checks.
- `ITERATION POLICY`: how to loop after failures.
- `STOP RULES`: when to stop instead of widening scope.
- `OUTPUT`: final report requirements.

The contract should be concise enough for a runtime prompt while linking to larger specs when needed.
