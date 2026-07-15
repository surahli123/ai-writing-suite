# Plan — Phase 2: comms-polish Quality Eval (LLM judge) — 2026-06-07

**Status: PLAN ONLY — awaiting owner go before any mutation.**
Target: feature branch off `main` → PR → rebase-ff. (Repo hooks block direct `main`
commits + committing plan/handover files — this plan stays UNTRACKED.)

---

## How this plan was produced

Multi-agent planning workflow `wf_a1b1aacf-266` (10 agents): 3 grounding readers + 2
web-research briefs → 2 design passes (architecture + methodology) → **3 adversarial
critics** (DS-rigor / engineering / product-scope), authored and reviewed in separate
lanes. I then **independently re-verified the two load-bearing BLOCKER facts** against the
real code before committing them here (see Evidence appendix).

## Headline finding

The **integration architecture is sound**; the **methodology was over-scoped for a v1
wire-in.** All three critics independently said: *sequence it.* So Phase 2 splits into:

- **Phase 2a — the cheap, critique-hardened, runnable slice (recommended now).** Wire the
  judge over the existing 8 fixtures, add gold labels, make `no_fabrication` always-scored,
  fix the secret/CI safety holes, add canned-response + CI-clean + voice-schema tests.
  Deliverable = a judge you can actually run, framed honestly as "this proves the judge
  *wiring*, not the skill *quality*."
- **Phase 2b — the eval-research program (deferred; gated on 2a looking promising).** Grow
  to ~24 real before/after items, frozen holdout, cross-family judge, replication,
  per-dimension kappa, live end-to-end eval.

## Verified BLOCKER facts (I re-ran these myself)

1. **`no_fabrication` — the highest-stakes dimension — is never scored on 3 of 8
   fixtures.** `readme-01-obvious`, `readme-02-subtle`, `memo-01-obvious` omit
   `no_fabrication` from `rubric_focus`, and the judge prompt only injects `rubric_focus`
   (rubric.md:54 ← run_fixtures.py:100). So the model is never asked to score the one
   dimension rubric.md:42-44 calls "always required." *Verified by enumerating fixtures.json.*
2. **The 30-40% calibration band at n=8 admits exactly one value: 3 misses (37.5%).**
   2/8=25% and 4/8=50% both FAIL the hard assert (run_fixtures.py:87, test_fixtures.py:54).
   *Verified by arithmetic over every miss count.* ⇒ any *added* fixture can flip CI red;
   adding a *field* to existing fixtures cannot.

## The 5 BLOCKERs and how this plan resolves each

| # | BLOCKER (critic) | Resolution in 2a |
|---|---|---|
| 1 | Degenerate kappa gold set — all 8 `after` are good → 0 FAIL → kappa undefined; an always-PASS judge scores 100% (DS) | 2a does **not** report kappa. The judge's negative class lives in **canned-response unit tests** (fabrication-trap, dropped-fact, re-AI'd) where aggregation correctness is what matters — no `fixtures.json` change, no calibration break. Real two-class gold + kappa → 2b at ≥40 items (kappa on ≤24 is noise per research). |
| 2 | Broken-ruler guard not enforced for the judge — detector has a code-asserted band, judge has none (DS) | The fabrication-trap canned test is a **hard code gate**: the judge must mark an invented-number rewrite FAIL-on-`no_fabrication` before any agreement number is trusted. |
| 3 | `no_fabrication` unscored on 3/8 (DS + Product) | **Always inject `no_fabrication`** into the judge prompt regardless of `rubric_focus`; a test asserts every response carries a `no_fabrication` line. |
| 4 | "CI stays clean by construction" is convention, not enforced (Eng) | Add a **test** that the deterministic path makes no network call (monkeypatch `urlopen` to raise) and that `judge` is not imported at module load (lazy import inside `run_judge`). `run_all.sh:23` stays `python3 -m fixtures.run_fixtures` (no `--judge`). |
| 5 | Secret handling unsafe-by-default + silent SKIP on auth failure (violates your "FAIL LOUDLY" rule); methodology over-scoped (Eng + Product) | **3-state gate:** (a) config absent → SKIP (exit 0); (b) configured + explicit `AIWS_JUDGE_RUN=1` → one call; (c) transport/auth/HTTP error → loud ERROR, exit nonzero (never SKIP). Keys never logged. **Liveness signal:** `--judge` with a key but 0/N parsed → exit nonzero ("provider envelope likely changed") so a broken judge can't masquerade as SKIPPED. Provider **purely env-driven, no baked-in vendor**. |

## Settled architecture (Option A, hardened)

- New dev-only `evals/fixtures/judge.py` — stdlib `urllib`+`json`+`os` only (NO SDK, NO pip
  line in ci.yml). Co-located with `build_judge_prompt`; `evals/` is already dev-only (not
  in the shipped plugin body).
- `score(prompt)` — env-driven (`AIWS_JUDGE_URL` / `AIWS_JUDGE_MODEL` / key var), the
  3-state gate above, ≤40 lines, one attempt, **no retry/backoff in v1** (retry logic is the
  part a minimal-debugger owner can't maintain and v1 doesn't need).
- `parse_dimension_lines(text)` + `aggregate(dim_results, rubric_focus)` — pure functions.
  Aggregation **recomputes the verdict in Python** (overall PASS iff all `rubric_focus` PASS
  AND `no_fabrication` PASS), ignoring the model's self-reported `VERDICT:` line → the
  `no_fabrication`-overrides-FAIL rule is deterministic and unit-testable. Unparseable → None
  (SKIP, never fake PASS). A majority-vote helper accepts a list of per-rep results (reps=1
  in 2a; 3× is a 2b setting).
- `run_judge()` swaps the **code** line `verdict = None` at **run_fixtures.py:125** (NOT the
  docstring mention at :117), returns `(passes, fails, skipped, agreement_counts)`; `main()`
  at :143 captures it and prints a judge summary + plain judge-vs-gold **agreement counts**
  (NOT kappa). Exit code (:146) stays deterministic-only → **judge is advisory in v1**
  (folding an un-validated judge into CI gates the build on a noisy ruler).

## Phase 2a — work items (the recommended build, ordered)

1. **Prompt:** always-score `no_fabrication` (in `build_judge_prompt` or the template) + a test.
2. **`judge.py`:** `score` (3-state, env-driven, key-redacted, ≤40 lines) + `parse_dimension_lines` + `aggregate` (Python recompute, majority-vote helper).
3. **`run_fixtures.py`:** swap line 125; add `--judge` flag; liveness 0/N → nonzero; capture return in `main()`; intentional-advisory comment; agreement-count print.
4. **Gold labels:** add `expected_verdict` (+ optional per-dimension gold) to the existing 8 — **FIELD ONLY**, n=8 untouched, miss=3/38% preserved (CI provably unchanged).
5. **`test_fixtures.py` JudgeParsing tests** (canned responses, no network): all-PASS→PASS; `no_fabrication`=FAIL + rest PASS → overall FAIL (the load-bearing asymmetry); fabrication-trap (invented number) → FAIL; unparseable→None; majority-vote 2-of-3; every response has a `no_fabrication` line.
6. **CI-clean guard test:** deterministic path makes no network call; `judge` lazy-imported.
7. **Voice tripwire:** ~15-line stdlib test asserting `voice-profile.md` template has its expected H2 headers (guards the documented silent-fallback bug; the voice *judge* eval is deferred to 2b — needs a corpus).
8. **Docs:** `evals/README.md` — judge is opt-in / env-driven / advisory / SKIPPED-offline / never-gates-CI; green = "judge wiring works," NOT "skill produces good rewrites"; cross-family = opt-in recommendation; kappa deferred to ≥40 items.
9. **Verify (the real gate):** `run_all.sh` green with NO judge call, exit 0; new tests pass with no network/key; **from a fresh clone / `git stash -u`** prove the parsing tests pass from *committed* files (closes the local-vs-remote gap that broke v1); `git ls-files .../judge.py` confirms it's tracked; `.gitignore` unchanged; calibration still 3/8=38%.

## Phase 2b — deferred (only if 2a's 8-item agreement looks promising)

- Grow to ~24 (4 genres × 6, ~2 easy/3 med/1 hard) — **your real AI-shaped drafts** as the
  primary `before` + synthetic fill; a precomputed miss-target table so every batch lands
  ~33% (CI never flips); real two-class GOLD incl. fabrication-trap *fixtures* paired with
  rebalancing catch fixtures.
- Frozen dev(~14)/test(~10) holdout, stratified, physically separated; self-improvement loop
  reads dev only.
- Cross-family judge (env), 3× replication majority-vote.
- Per-dimension kappa (≥0.6 to trust, ≥0.8 before any local-only gate), TPR/TNR,
  error-analysis on disagreements; extend the 30-40%-fail calibration concept to the judge.
- Live end-to-end eval: feed a real `before` through comms-polish, judge the **live** `after`
  (v1 scores static hand-written `after` strings — that proves the judge, not the skill).

## Owner decisions — RESOLVED 2026-06-07

1. **2a-first resequencing → ACCEPTED.** Build the small hardened 2a slice now; decide 2b
   after seeing 2a's agreement.
2. **Live judge in 2a → PLUMBING + CANNED TESTS ONLY.** No live model call, no API key, no
   spend this session. Canned-response unit tests prove parse/aggregate/`no_fabrication`
   logic. Owner runs `--judge` live later when a provider key is set.
3. **2b eval set → HYBRID** (real drafts primary + synthetic fill). **Real drafts will be
   collected on the owner's ENTERPRISE computer**, so 2b real-draft collection happens later
   on the work machine. Does not block 2a.

## Verification gates — "done" for 2a

`run_all.sh` green, exit 0, NO judge/network call; new tests green with no key; fresh-clone
CI proof; `judge.py` tracked; `.gitignore` unchanged; calibration still 3/8=38%.

## Risks (top)

- Adding any fixture flips the n=8 calibration band → 2a adds NONE (field-only); 2b uses a miss-target table.
- Silent judge rot for a minimal-debugger owner → liveness 0/N nonzero + loud auth errors.
- Self-preference if judge family == rewriter family → moot for static fixtures in 2a; cross-family required before any live/end-to-end run.
- Over-trusting kappa at small n → 2a reports agreement counts only; kappa deferred to ≥40.

## Evidence appendix

- Workflow `wf_a1b1aacf-266` (10 agents). Full critiques: workflow output +
  `~/.claude/projects/-Users-surahli/.../tool-results/beawkwwn0.txt`.
- Verified: `no_fabrication` missing from `readme-01`/`readme-02`/`memo-01` `rubric_focus`;
  n=8 band admits only 3 misses; detector calibration 3/8=38% in band (re-run this session).
- Code anchors: `run_fixtures.py` :94-102 (`build_judge_prompt`), :105-111 (template
  extract), :114-130 (`run_judge`), :125 (`verdict=None` swap), :133-146 (`main`), :87-90
  (detector calib assert); `rubric.md` :42-44 (`no_fabrication` always required), :46-66
  (template); `test_fixtures.py` :47-66 (calib asserts); `run_all.sh` :23.
