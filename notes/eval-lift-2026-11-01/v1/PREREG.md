# Skill-lift eval v1: pre-registration (2026-11-01)

Written and committed **before** the held-out items were read and before any v1
output was generated. It replaces the retired per-step gate. That gate failed
identical text in 9 of 12 run pairs; see `../review/README.md`.

## Question

Is the final stacked version of the suite (step 8 tip, which contains steps
0–8) **worse** than the current suite (`main`), or worse than no skill
(`bare`), at polishing a data-science team's writing? Secondarily, is it
better?

## Items

- **Primary: 24 held-out items.** A separate agent wrote them from failure
  descriptions only. It was told not to read the repo, the skills, or the
  rules (`items_heldout.json`). The orchestrator does not read their contents
  before the run; it checks format only.
- Categories:
  - 6 clean human texts;
  - 8 AI-style drafts with real content that must be kept;
  - 5 notes-vs-draft conflicts;
  - 3 terse status updates;
  - 2 long documents with an internal inconsistency.
- **Secondary: the 24 v0 frozen items** (`../items.json`). These are
  contaminated, because they were seen while designing the steps. Reported,
  never decisive.

## Arms

All arms are Sonnet with the same prompts as `../gen_arms.js`. Each arm run
handles one item set in one context.

| Arm | Root | Held-out runs | Frozen runs |
|---|---|---|---|
| `new` | step 8 tip | K = 3 | 1 |
| `main` | `main` @ 233d54a | K = 3 | cached v0 (1) |
| `bare` | none | K = 1 (floor only) | cached v0 (1) |

K is fixed in advance. Runs are never added or redrawn after seeing a result.

## Judging (session model, logged)

1. **Absolute, notes hidden.** One judge per arm run. Judges see the author's
   request and a single candidate's text, never the assistant's notes. For
   each item a judge records:
   - `would_send` (bool);
   - `severe_changes`: a typed list from {number_change, added_claim,
     dropped_fact, strengthened_certainty, weakened_certainty, scope_change};
   - `over_edited` (bool).
2. **Sentinels.** Every absolute packet includes 10 known-answer candidates
   built from `fixtures.json` / `fixtures_fail.json`: 4 faithful and 6 with a
   planted defect. Their ids are disguised and they are interleaved with the
   real items.
   - A faithful sentinel is scored correct if it has no severe change and
     would_send is true.
   - A defective sentinel is scored correct if a severe change is listed or
     would_send is false.
   - **A judge packet with fewer than 8 of 10 sentinels correct is
     discarded** and re-judged once.
3. **Pairwise, `new` against `main`.** On the held-out items, run k of `new`
   is paired with run k of `main`, for k = 1..3. Each pair is judged in both
   orders, with notes hidden. A side wins only if it wins in both orders;
   otherwise the pair is a tie.

## Metrics and decision rules

Per item, an arm's score is the mean over its runs of:

- **S** = any severe change (0/1);
- **W** = would_send (0/1).

The paired item-level difference is `new − main` (or `new − bare`). A 90% CI
comes from 10,000 bootstrap resamples of items (seed 20261101).

| Verdict | S (lower is better) | W (higher is better) |
|---|---|---|
| **Worse** | CI lower bound of ΔS > 0 | CI upper bound of ΔW < 0 |
| **Not worse (non-inferior)** | CI upper bound of ΔS ≤ +0.10 | CI lower bound of ΔW ≥ −0.10 |
| **Inconclusive** | otherwise | otherwise |

**Pairwise.** Count item-level net wins: for each item, wins − losses over
k = 1..3, ties excluded. Run a one-sided sign test over the items with a
nonzero net. **Worse** if `main` is preferred with p < 0.10.

**Floor.** On held-out clean_human + terse_status items (9 items), `new` must
have W ≥ 0.85 and S ≤ 0.10, absolute.

**Ship rule.**

- **Open the step PRs** if `new` is not "Worse" on S, W, or pairwise against
  `main`, is not "Worse" on S or W against `bare`, and meets the floor.
  "Inconclusive" is reported as such and does not block.
- **If any "Worse":** bisect. Run steps 4, then 2 or 6, with the same protocol
  at K = 1 on the held-out set. This localizes the regression; that step is
  fixed or dropped.

## What this design cannot do

- **Judges are Claude-family** (no cross-vendor model is available).
- **Sentinels measure the judge's sensitivity to planted defects, not its
  taste.**
- **The human anchor is the counterweight.** The owner labels about 10
  discriminating items on a separate page; the judge and owner agreement rate
  is reported.
- **Power is limited.** With 24 items the design detects only large
  differences (roughly 0.15 or more on S or W). Smaller effects come out
  "inconclusive", and the report says so.

## Addendum (2026-11-01, before run 2)

Run 1 triggered BISECT. The pairwise loss was 3 items to 10. The judges' written
reasons localized it to step 1's restraint: `new` returned "make this read better"
requests unchanged, where `main` made a light readability polish. The owner ruled
"allow light polish". Step 1 now calibrates restraint to the request type, and the
fix is merged forward into steps 2–8 (final tip `7f230eb`).

Run 2 re-tests the final tip with the **same rules**:

- 3 fresh `new` generations on the same 24 held-out items;
- absolute judging of `new` only, reusing run 1's absolute judgments of
  `main`/`bare`, which are per-candidate and independent of the other arms;
- pairwise `new` run k against run 1's `main` run k, k = 1..3, in both
  orders.

**Disclosed contamination.** The orchestrator read run 1's judge reasons on
these held-out items while designing the fix. The fix is generic: request-type
calibration, not item-specific wording. Still, run 2 is no longer a pure
held-out test; read it as a confirmation of direction. If run 2 shows no WORSE,
the step PRs open, with this caveat stated in each PR.
