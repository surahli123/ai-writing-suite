# Integration notes — four product lanes (2026-07-13)

Orchestrator's ledger for merging the four Opus lanes. Do not lose these.

## Branch topology at dispatch time

- `feat/eval-hardening-now` — PR #15, OPEN, awaiting owner merge + v1.1.0 tag.
- `feat/behavioral-evals-draft-voice` — stacked ON #15 (HEAD 54ee248, reviews closed).
- Four product lanes branched off LOCAL `main` (8691e88), which is BEHIND origin/main
  (f0c77d0, PR #14) and behind both branches above:
  - feat/narrative-shape-category (committed: 6141dd3)
  - feat/stylometric-fingerprint (in flight)
  - feat/audit-report-contract (in flight)
  - feat/kb-ingestion-tooling (in flight)

## Known collisions to resolve at integration

1. **fixtures_fail.json created independently on TWO branches.** PR #15 ships it with
   run_fail_deterministic() enforcing FAIL_REQUIRED = {id, genre, difficulty, before,
   after, rubric_focus, expected_verdict, fail_dimension} and required archetypes.
   feat/narrative-shape-category creates its own 16-line version (narrative
   over-correction exemplar), NOT wired into run_fixtures on that branch. On merge:
   union the two files' fixture arrays, verify the narrative exemplar satisfies
   FAIL_REQUIRED (add missing fields if not), and confirm run_fail_deterministic
   passes with the merged set.
2. **rubric.md modified on both** #15 (quoted-evidence protocol + one-line EVIDENCE
   constraint) and narrative lane (narrative_shape_ok block). Textual merge expected
   clean-ish but verify the fenced judge template still extracts (single fence pair —
   _extract_judge_template takes the FIRST fence after "Judge prompt template").
3. **fixtures.json** gains overstep-06 (on #15) and 4 narrshape fixtures (narrative
   lane) — both additive; calibration must still read 3/8 = 38% after union (all new
   fixtures detector_blind).
4. **comms-draft/SKILL.md** modified on #15 (frontmatter seam clause) and narrative
   lane (steps 1/5 wiring) — different regions, expect clean merge; verify frontmatter
   still single-line YAML.
5. Voice lanes: feat/stylometric-fingerprint touches host-profile-template.md +
   voice-onboard/SKILL.md + test_voice_contract.py; feat/behavioral-evals-draft-voice
   rewrote the voice fixture artifacts per-genre. The stylometry lane was FORBIDDEN
   from evals/fixtures/**, so no file overlap — but SEMANTIC coupling: once both land,
   the per-genre profile artifacts should eventually carry the measured-fingerprint
   section too (follow-up, not a blocker; test_voice_contract must stay green on both).

## Planned integration order

1. Owner merges PR #15, tags v1.1.0.
2. Rebase feat/behavioral-evals-draft-voice onto main → PR.
3. Rebase each product lane onto main; resolve collisions per above; run the FULL
   suite after each (run_all.sh green + calibration 38% + unittest discover).
4. One PR per lane (small, reviewable), each with its review evidence.

