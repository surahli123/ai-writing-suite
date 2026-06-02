# Oracle And Proof

The Oracle is the source of evidence that determines whether the contract is complete.

Good Oracle examples:

- a targeted test command exits 0
- a typecheck or lint command passes
- a generated artifact exists and matches required fields
- a manual acceptance checklist is completed
- a review gate returns no blocker findings

Proof is the final report that cites Oracle evidence. A proof report should include changed files, commands run, command results, known gaps, and the stop condition reached.

Avoid Oracles that depend on vague judgment, unavailable credentials, hidden production systems, or unverifiable future behavior.
