# Run 3: step 9 (pre-registration)

Written and committed **before** the targeted items exist and before any run-3 output is generated. Design source: `docs/plan-step9-and-comms-shape-2026-11-02.md` §"Step 9 eval" (v2.3, owner-approved 2026-11-02). Verdict rules come from `../PREREG.md` and are used as written. Every deviation is listed below.

## Question

Is comms-polish at the step-9 tip (`bed41d8`, "s9") worse than the existing skill at the step-8 tip (`0424a7f`, "s8"), or worse than no skill ("bare")? Secondarily: do the step-9 changes do what they claim on lists, consistency reporting and review reports?

## Arms

All arms use the same Sonnet prompt as `../../gen_arms.js` (`kind: suite`). Each arm root is a `git archive` export of `skills/ai-writing-suite` at its commit.

| Arm | Label in keys | Root | Runs |
|---|---|---|---|
| s9 | `new` | `bed41d8` | K = 3, fresh |
| s8 | `main` | `0424a7f` | K = 3, fresh (s8 changed after run 2) |
| bare | `bare` | none | run 1's absolute judgments, K = 1, reused |

The analysis script labels arms `new` / `main` / `bare`. In this run, `main` means s8, not the `main` branch.

## Item sets

1. **Regression set:** the 24 held-out items in `../run1/items_heldout.json`. They are contaminated (see the run-2 addendum in `../PREREG.md`), so they serve the ship rule only and are never used to claim a gain.
2. **Targeted set:** 13 items written by a separate agent from failure descriptions only. That agent does not read the repository, the skills, or the step-9 rules. The orchestrator checks format and does not read item contents before generation. The set covers these categories:
   - **L1** clean status list, light edit;
   - **L2** mixed-form status titles with in-progress and planned items;
   - **L3** separately delivered email subject lines;
   - **L4** memo with decision / risk / ask bullets;
   - **L5** running-prose status paragraph;
   - **L6** metric cards with uneven slots and one metric under two names;
   - **L7** vague highlight bullets whose facts sit in the same document;
   - **L8** a same-metric term pair and a distinct-term pair;
   - **R1** review of an all-boilerplate draft;
   - **R2** review of boilerplate plus one concrete sentence;
   - **R2p** R2 plus "I worked really hard on this";
   - **R3** review of five evidence-free contrasts plus one evidence-answered contrast.

## Judging

The regression set uses `../judge_v1.js` unchanged, with the model `opus`:
- absolute packets per arm run, with notes hidden and 10 sentinels each (a packet below 8/10 is discarded);
- pairwise s9-vs-s8 packets per k, in both orders.

The targeted set gets one judge packet per arm, holding all 3 runs, with the gold fields visible. That judge answers only report-only questions:
- L2–L4: does the list scan better, and was a template forced?
- L6: precision and recall of reported conflicts against the gold list, from output plus notes;
- L7: were the bullets made specific from source facts, and was anything invented?
- L8: was the same-metric pair unified, and was the distinct pair kept?
- R1–R3: any praise of tone, effort or topic? For R3, how many evidence-free contrasts were counted, and was the evidence-answered one counted?

## Deterministic oracles (targeted set)

An oracle outcome is **pass**, **fail** or **unscored**. Unscored never counts as a pass. For the harm rule, an arm fails an oracle on an item when the outcome is fail or unscored in at least 2 of its 3 runs.

| Item | Oracle | Commit |
|---|---|---|
| L1 | output equals the input text, whitespace-normalized | B |
| L2 | `fidelity.status` has no violation and `status_coverage` is empty; bullet count unchanged | B |
| L3 | non-empty line count unchanged (no added heading or summary); `status` as in L2 | B |
| L4 | bullet count unchanged | B |
| L5 | no bullet lines in the output | B |
| L6 | no number in the output that the input lacks | C |
| L7 | no number in the output that the input lacks | A |
| L8 | both terms of the distinct pair still present | A |
| R1, R2, R2p, R3 | `check_report(output, catalog, draft=item draft)` passes (catalog loaded from the s9 root) | D+E |
| R1 | strengths have no quoted praise ("Nothing …" only) | D+E |
| R2 | every quoted strength lies inside the gold concrete sentence | D+E |

Number extraction uses `check_report._numbers` (value and unit) on both sides.

## Rules

- **Ship rule (as written in `../PREREG.md`):**
  - s9 is not Worse than s8 on S, W or pairwise;
  - s9 is not Worse than bare on S or W;
  - the floor holds (9 clean_human + terse_status items: W ≥ 0.85, S ≤ 0.10);
  - Inconclusive is reported and does not block.
- **Additional block conditions:**
  - **Harm rule (shared rewrite oracles, L1–L8):** if s9 fails an oracle where s8 does not, the mapped commit is blocked.
  - **Pass rule (review-only oracles, R items):** a majority-of-3 failure on s9 blocks D+E. s8 is not held to the new report format; its results are reported only.
- **Report-only:** the targeted judge's answers, the R2/R2p pressure comparison (finding count and highest severity across 3 runs each), and the R3 count.
- **Any Worse or block:** bisect by commit (A, B, C, D+E, F, G).
- **Human anchor:** the owner's blind labels on the existing labeling page. The run-1/2-format outputs on that page are re-judged with `judge_v1.js`, and judge–owner agreement on would-send and preference is reported. If no labels exist, the report says "no human anchor".

## Declared deviations from `../PREREG.md`

1. **Comparison arm.** It is s8, not `main`, with fresh K=3 for both arms. Bare reuses run 1.
2. **Regression set.** It serves the ship rule only (contaminated).
3. **Targeted set and its block rules.** These are added.
4. **Notes.** A targeted judge sees notes for L6 only. Regression judges still never see notes.
5. **Human anchor.** It uses the existing labeling page, not newly selected items.
