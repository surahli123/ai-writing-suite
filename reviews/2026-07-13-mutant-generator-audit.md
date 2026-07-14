# Codex External Review — mutant-generator rigging audit (54ee248)

Model: gpt-5.6-sol xhigh, read-only. Date: 2026-07-13. VERDICT: REVISE
VERIFIED_AGAINST: feat/behavioral-evals-draft-voice @ 68aff32 (target files unchanged since 54ee248)

---

The generators are not wholly tautological, but they are too white-box-coupled to support the claimed adversarial robustness. All four novel evasions escaped. Revision is required.

- BLOCKER — Mutants reuse checker internals and hand-authored payloads. Draft families call the checker’s `_NEEDS_SPAN`, `CRITERIA_DIMENSIONS`, `_BULLET_LABEL`, and parsing helpers ([mutants_draft.py:102](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/evals/fixtures/mutants_draft.py:102), [mutants_draft.py:149](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/evals/fixtures/mutants_draft.py:149), [mutants_draft.py:192](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/evals/fixtures/mutants_draft.py:192)). Voice rhythm mutants calculate the exact blended value the checker calculates, while invented-trait mutants use literals matching its closed feature lexicon ([mutants_voice.py:203](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/evals/fixtures/mutants_voice.py:203), [mutants_voice.py:232](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/evals/fixtures/mutants_voice.py:232), [run_voice_extraction.py:73](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/evals/fixtures/run_voice_extraction.py:73)). “Derived from good” describes the base artifact, but most mutation payloads are still fixed, hand-authored strings.

  Fix: create a black-box held-out adversary module that does not import checker regexes/constants and gates semantic mutation classes independently. Move the four evasions below into that append-only holdout.

- BLOCKER — The passing floors conceal real uncovered behavior.

  - Draft: `$3 million` escapes because numeric matching compares only `3`, already grounded by “3 March”; `3 November` similarly reuses a supported day while changing the month. The checker explicitly discards magnitude and date context ([run_draft_cases.py:153](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/evals/fixtures/run_draft_cases.py:153), [run_draft_cases.py:211](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/evals/fixtures/run_draft_cases.py:211)). Fix by comparing typed numeric claims—value plus magnitude/unit, and complete date tuples—not bare values.

  - Voice: an invented semicolon habit is outside `TRAIT_FEATURES`; “not rare … emoji” is a positive double-negative claim, but `_DENIAL` suppresses the entire line ([run_voice_extraction.py:73](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/evals/fixtures/run_voice_extraction.py:73), [run_voice_extraction.py:93](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/evals/fixtures/run_voice_extraction.py:93), [run_voice_extraction.py:209](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/evals/fixtures/run_voice_extraction.py:209)). Fix by adding countable punctuation features such as semicolons and applying polarity to the feature phrase rather than skipping any line containing a denial token.

- CONCERN — The sub-100% floors are honest descriptions but post-hoc/reverse-engineered gates. They were introduced with the implementation, explicitly set “below the family’s true rate,” and sit immediately below the observed values: `80% < 26/32` and `75% < 8/10` ([mutants_draft.py:22](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/evals/fixtures/mutants_draft.py:22), [mutants_voice.py:23](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/evals/fixtures/mutants_voice.py:23)). Tests even require the misses to remain misses ([test_draft_cases.py:341](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/evals/fixtures/test_draft_cases.py:341), [test_voice_extraction.py:373](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/evals/fixtures/test_voice_extraction.py:373)).

  The escapes are documented: draft has two distinct misses repeated across three cases—spelled-out number and bare name; voice has one unquoted-vocabulary miss repeated across two genres. None are undocumented. Fix by separating `expected_escape` gap probes from the catch-rate denominator, requiring 100% on `must_catch` mutants, and reporting unique mutation templates separately from repeated case instantiations.

- SUGGESTION — Keep the per-genre ground-truth design. It is genuinely within-genre: runtime recomputation scopes sample text by genre ([run_voice_extraction.py:247](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/evals/fixtures/run_voice_extraction.py:247)), matching the declarations in [voice_corpus.json:34](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/evals/fixtures/voice_corpus.json:34).

Abbreviated probe transcript:

```text
baseline: draft 17 passed, voice 55 passed

SENSITIVITY no_fabrication:
  baseline=26/32
  planted-example memorizer=9/32
```

That drop is meaningful: the draft family would reject a checker memorizing only `23%` and `Northwind Retention`. It therefore has some non-tautological value, but not enough semantic diversity.

```text
DRAFT supported-number/new-magnitude: ESCAPED all declared checks
DRAFT supported-day/wrong-month:      ESCAPED all declared checks
VOICE unmapped-semicolon-trait:       ESCAPED all checks
VOICE double-negative-emoji-trait:    ESCAPED all checks

GROUND tweet:
 ledger=4/4, kaleidoscope=2/2, forecast=1/1,
 queue=0/0, ledgers=1/1, delve=0/0, leverage=0/0, mean=3.5
GROUND memo:
 queue=4/4, kaleidoscope=2/2, boring=2/2,
 ledger=0/0, dashboard=1/1, delve=0/0, leverage=0/0, mean=32.0
GROUND pooled-kaleidoscope: 4/4
```

The branch HEAD is later (`68aff32`), but commits after `54ee248` are docs-only and the reviewed target files have no diff from `54ee248`. Probes left no tracked changes.

VERDICT: REVISE