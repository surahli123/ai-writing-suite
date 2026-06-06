# Evals — AI Writing Suite (Layer 3)

The eval subsystem for the suite. Three independent pieces, all **Python 3
stdlib only** (no pip, no Node, no API key required to run the deterministic
parts):

| Piece | What it does | Needs a model? |
| --- | --- | --- |
| `detector/` | Mechanical AI-tell scanner — cheap deterministic regression gate | No |
| `fixtures/` | Before/after pairs across 4 genres, score bands + LLM-judge rubric | Judge half only |
| `smoke_test.py` | Automates the KB ingestion+retrieval smoke chain (design D12) | No |

> Design lineage: D10 (eval harness + Autorefine-style self-improvement) and D12
> (prove one end-to-end KB retrieval chain). See
> `docs/design-ai-writing-suite-v1-2026-06-06.md`.

## How to run each piece

All commands run **from this `evals/` directory**.

```bash
# 1. Mechanical detector — unit tests
python3 -m unittest detector.test_detector

# 1b. Detector on any file (or stdin)
python3 -m detector.cli path/to/draft.md
cat draft.md | python3 -m detector.cli -

# 2. Fixtures — deterministic score-band check + calibration report
python3 -m fixtures.run_fixtures
python3 -m fixtures.run_fixtures --judge      # also emits the LLM-judge prompts (SKIPPED offline)
python3 -m unittest fixtures.test_fixtures    # asserts the suite stays calibrated

# 3. KB smoke test — ingestion+retrieval chain
python3 smoke_test.py

# Everything at once
python3 -m unittest discover -p 'test_*.py'   # all unit tests
python3 smoke_test.py                         # smoke (own runner)
```

Exit code `0` = pass for every command. CI should run all three.

## The three pieces in detail

### 1. `detector/` — mechanical detector

A faithful-but-pragmatic Python port of the avoid-ai JS engine
(`/tmp/grill-refs/avoid-ai-writing/detector/patterns.js`, MIT). It keys off the
same AI-tell categories the `comms-polish` skill reads from
`_shared/patterns/`. Pure regex + arithmetic — no model.

- `patterns.py` — the rule data (vocab tiers, phrase regexes, weights). One
  block per `_shared/patterns/` category.
- `detector.py` — `analyze(text)` returns `{score, label, issues, stats,
  classification, confidence}`. Scoring: collect issues → dedup by (type, text)
  → sum category weights → normalize by `log2(words/50)`.
- `cli.py` — `python3 -m detector.cli <file>`.
- `test_detector.py` — mirrors the JS test coverage (length gates, AI-heavy vs
  human, per-category detectors, FN-biased classifier, dedup math).

**Role:** the cheap regression gate. It runs on every commit and never costs an
API call. It catches *vocabulary and density* regressions; it does **not** judge
whether a rewrite kept meaning or invented a fact — that is the LLM judge's job.

### 2. `fixtures/` — before/after fixtures + LLM judge

`fixtures.json` holds 8 fixtures (2 per genre: tweet / linkedin / readme /
memo). Each has an AI-shaped `before`, a good human `after`, detector score
bands, and `rubric_focus` (which rubric dimensions matter here).

- `run_fixtures.py` — runs the **deterministic** half (assert score bands +
  report naive-baseline miss rate). With `--judge` it fills the rubric prompt
  per fixture and marks them **SKIPPED** (no model wired in — it never fabricates
  a verdict offline).
- `rubric.md` — the LLM-judge scoring contract (dimensions, verdict aggregation,
  a model-agnostic zero-shot prompt template). `no_fabrication` is always
  required: a fluent rewrite that invents a number FAILS.
- `test_fixtures.py` — asserts the suite stays well-formed, in-band, and
  calibrated.

### 3. `smoke_test.py` — KB retrieval chain

Automates the TEST CASE blocks in `_shared/knowledge/SMOKE-TEST.md`. It parses
each block (query / expected entry / expected passage), replicates the INDEX.md
retrieval protocol **in code** (keyword overlap, summary-intent tie-break — zero
embeddings, design D5), opens the chosen entry file, and asserts the expected
passage is present. This proves the "drop in a markdown page → retrieval works"
promise end to end.

## Calibration rule (read before adding fixtures)

Per the project rule (`CLAUDE.md` → "Evals"): **a naive baseline must miss
~30-40% of cases.** If the baseline catches >80%, the evals are too lenient to
catch regressions — a broken ruler.

Here the "naive baseline" is: *flag the `before` as AI iff the detector score
≥ `baseline_threshold`*. The current suite sits at **3/8 = 38% miss** (verified
by `test_fixtures.Calibration`).

**How the fixtures are made hard:** half the `before` items are `subtle` — they
are AI-written but carry **no vocabulary tells**, only structural / rhythm tells
the flat detector underweights on short text:

- `tweet-02` — negative parallelism + vague closer, zero specifics.
- `linkedin-02` — rule-of-three scaffolding + engagement-bait closer.
- `readme-02` — pure filler, zero content ("smooth onboarding experience").
- `memo-02` — false concession + hedge-stacking (the borderline case: scores
  ~15, just over threshold).

The mechanical detector misses the first three by design. That gap is exactly
what the LLM judge exists to cover — and why the suite needs both halves.

### Adding a new fixture

1. Add an object to `fixtures.json > fixtures` with: `id`, `genre`,
   `difficulty` (`obvious`|`subtle`), `before`, `after`, `after_band_max`,
   `rubric_focus`, `expect_baseline` (`catch`|`miss`), and — for subtle ones —
   a `subtle_tell` explaining the non-vocabulary tell.
2. Run `python3 -m fixtures.run_fixtures` to read the actual detector scores.
3. Set `before_band_min`/`before_band_max` to bracket the observed score (a
   regression guard, not an aspiration). Set `expect_baseline` to match what the
   detector actually does at the threshold.
4. Re-run `python3 -m unittest fixtures.test_fixtures`. If the calibration test
   fails, the miss rate drifted out of 30-40% — rebalance obvious vs subtle
   fixtures (don't move the threshold to paper over it).

## Wiring into self-improvement (Autorefine methodology, D10)

The suite's `_shared/self-improvement.md` proposes new tell rules over time.
This eval subsystem is the **gate** those proposals pass through, following the
Autorefine Three-Gulfs loop (`~/.claude/skills/autorefine/`):

1. **Error analysis (Gulf 1).** When `comms-polish` mishandles a draft, capture
   it as a new fixture (a failing `before`). The fixture set IS the failure
   taxonomy.
2. **Judge calibration (Gulf 2).** A proposed rule must be expressible as either
   a detector pattern (add to `detector/patterns.py` + a `test_detector` case)
   or a rubric dimension (add to `rubric.md` + a fixture `rubric_focus`). If it
   can be neither, it is not measurable and does not ship.
3. **Mutation, eval-gated (Gulf 3).** Apply the proposed rule, then re-run this
   suite. Keep the change only if (a) all unit tests still pass, (b) the new
   fixture flips from FAIL to PASS, and (c) the calibration miss rate stays in
   30-40% (no regression on the rest of the suite). A proposed rule that
   over-fires drops the miss rate below 30% — the calibration test catches it.

This subsystem wires the **measurement**. The full mutation loop (generate
candidate rules, auto-apply, auto-score, keep/discard) is Autorefine's job and
is **not** built here — D10 scopes v1 to "each proposed rule is eval-measured
before human approval," which is exactly what steps 2-3 provide.

## Attribution

The detector is a Python port of `conorbronsdon/avoid-ai-writing` (MIT). Pattern
categories trace to the seven source catalogs credited in
`_shared/patterns/00-index.md` and the skill `NOTICE.md`.
