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


## Lane completion status (updated after all four landed)

| Lane | Branch @ SHA | Size | Agent-reported suite state |
|---|---|---|---|
| #9 narrative | feat/narrative-shape-category @ 6141dd3 | 6 files, +347 | green, 38%, 78 tests |
| #15 stylometry | feat/stylometric-fingerprint @ 13e944e | 6 files, +870 | green, 38%, 98 tests |
| #19 audit-report | feat/audit-report-contract @ 5ea555c | 9 files, +564 | green, 38%, 92 tests |
| #25 kb-ingestion | feat/kb-ingestion-tooling @ 19d1300 | 4 files, +1106 | green, 38%, 85 tests |

Reviews in flight: OMC code-reviewer (all four) + Codex xhigh (A/B: stylometry+kb;
C/D: narrative+audit). Verdicts to be appended.

## Additional integration facts

- `feat/audit-report-template` (2026-07-03) is an EMPTY branch (0 commits past main)
  — the plan it was made for lived only as an untracked file
  (docs/plan-audit-report-template-2026-07-03.md, never committed). The audit lane's
  build was reconciled against that plan: consistent on every load-bearing decision
  (worst-offender lead without a number; C/M/M tiers; quote→tell→why→fix;
  "What already reads well"; score separation; detect/review-only firewall).
  Safe to delete the empty branch at cleanup.
- NEW collision beyond the earlier list: run_all.sh step NUMBERING. audit lane adds
  its checker as step [4/4] off main; the behavioral-evals branch already renumbered
  to [5/6]+[6/6] on its own stack. Post-merge the step headers must be renumbered
  once, in whatever order the branches land.
- kb lane adds tools/ + evals/test_kb_ingest.py — no file overlap with any other
  lane (verified by diff --stat), only run_all discovery picks the tests up
  automatically.

## Architecture roadmap (from the external /improve review — DO NOT start before merges)

Full review: reviews/2026-07-13-architecture-improve-review.md (verdict NEEDS-WORK).
Five refactors, ranked; every one except the two "safe NOW" preparation items is
gated on the open branches merging (run_all.sh and evals/fixtures/ are merge-hot):

1. Capability-runner discovery replaces ordinal run_all.sh numbering (the 3-branch
   renumbering collision proved the point). Safe NOW: design the runner protocol only.
2. Pattern markdown becomes the typed registry (metadata table per tell entry + one
   stdlib loader); 00-index/rubric/coverage-matrix become generated projections.
3. One text-analysis seam (aiws/text.py) before multilingual #14 — three tokenizers
   already disagree (detector, voice grader, stylometry).
4. judge.py behind one evaluate() façade (deep module — do NOT split into shallow utils).
5. Reverse the tools→evals dependency (aiws/kb/ module; kb_validate currently imports
   test scaffolding via sys.path hacks).

OWNER DECISIONS needed before the registry/refactor work (the review's hard questions):
(a) does catalog "severity" mean editorial harm, detection confidence, or enforcement
strength — one axis per field; (b) what is the scheduled live lane FOR (availability vs
quality vs release regression); (c) are tell IDs language-universal before #14;
(d) is the detector's numeric score a compatibility contract (shared tokenization will
shift bands); (e) are generated markdown projections mandatory review artifacts;
(f) does a multi-sub-type judge dimension score aggregate or per-ID.

## Post-decision fix lanes (2026-07-13, late)

- fix/release-hygiene @ 7f27ad9 (off main): manifests version-neutral, root LICENSE,
  NOTICE nature-skills provenance (MIT-era bounds proven; upstream SHA candidate w/ TODO),
  scripts/validate_packaging.py + CI step, .gitignore worktrees, README reconciliation +
  quickstart, RovoDev claim narrowed (Q15), design-doc banner.
- fix/assets-catalog-lifecycle @ 9f98f06 (off main): register-shift canonicalized w/
  validity condition (Q16), C2/H7/H8 + S9/L1 dedup via canonical/alias, R1→C8 loop fixed,
  S1/S2/T9 validity conditions, lifecycle schema repaired (graduated, 4 scopes, concrete
  promotion procedure), SMOKE-TEST corrections, 00-index inventory/links.
- New merge-conflict notes: fix/assets touches 00-index.md (narrative lane appends a row —
  both kept append-only, expect trivial conflict); fix/release-hygiene touches suite README
  (kb lane was told to stay off it — clean) and .github/workflows/ci.yml (audit lane's
  run_all renumbering does NOT touch ci.yml — clean).
- REMAINING QUEUED: prose mega-fix (1.8–1.13) + Q7 full-document mixed mode + Q8 rider
  (post-edit voice-capture offers) + Q9 frontmatter fix + Q10 multi-genre profile contract
  (DESIGN DOC FIRST, owner review, then build) — starts after the six feature/fix branches
  merge, to avoid a fourth concurrent editor on the SKILL.md files.

## Recommended merge order (updated)

1. PR #15 (feat/eval-hardening-now) — owner merges + tags v1.1.0.
2. feat/behavioral-evals-draft-voice — rebase onto main, PR (carries all review records
   + decisions + this ledger).
3. fix/release-hygiene, fix/assets-catalog-lifecycle — small PRs, independent.
4. feat/narrative-shape-category (resolve fixtures_fail.json add/add + rubric/fixtures/
   00-index unions per the earlier collision list), then feat/audit-report-contract
   (run_all step renumbering), then feat/stylometric-fingerprint, then
   feat/kb-ingestion-tooling.
5. Full-suite verification after EACH merge: run_all.sh green + calibration 38% + 
   validate_packaging.py green.
6. Then the prose mega-fix branch + Q10 design doc.
