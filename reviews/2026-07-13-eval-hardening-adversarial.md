The branch is not merge-ready. All 125 tests pass, calibration remains `3/8 = 38%`, gold-FAIL stays outside the denominator, manifests agree on `1.1.0`, and the non-judge path made no network call.

## BLOCKER (must fix before merge)

1. [judge.py:76](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/evals/fixtures/judge.py:76), [judge.py:232](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/evals/fixtures/judge.py:232) — quoted evidence is neither verbatim-validated nor parsed safely.

   Why it breaks: any invented quoted string suppresses the warning even if it appears nowhere in `before` or `after`. The regex also accepts mismatched quote characters: `EVIDENCE: "We're behind"` is parsed as `"We"` because the apostrophe is treated as a closing quote. My probe returned `evidence_missing=False` for both fabricated and truncated evidence. Moreover, [run_fixtures.py:299](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/evals/fixtures/run_fixtures.py:299) discards accepted quotes, so users cannot audit them.

   Concrete fix: use paired-quote parsing, then validate that the extracted evidence is an exact substring of `fixture["before"]` or `fixture["after"]`. Distinguish `missing`, `malformed`, and `not_verbatim`; print or persist accepted evidence. Keep `parse_dimension_lines()` as the unchanged projection. Add tests for contractions, mismatched quotes, hallucinated quotes, smart quotes, and multiline model formatting.

   Hard question: which captured outputs from at least two real judge families prove the demanded `EVIDENCE` format survives normal Markdown and multiline formatting? Without that evidence, why should operators trust either silence or a flood of warnings?

2. [run_fixtures.py:203](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/evals/fixtures/run_fixtures.py:203), [test_fixtures.py:658](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/evals/fixtures/test_fixtures.py:658) — the gold-FAIL metric rewards a constant always-FAIL judge as perfect discrimination.

   Why it breaks: `run_fail_judge()` counts any overall `FAIL` as caught without checking the declared `fail_dimension`. I reproduced `payoff_clear: PASS` plus unrelated `no_fabrication: FAIL`; the fixture was still counted as matching gold. The test explicitly asserts that a judge failing everything “discriminates all.” That is 100% negative recall from a constant classifier, not discrimination.

   Concrete fix: evaluate PASS and FAIL fixtures together as a confusion matrix and report sensitivity, specificity, and balanced accuracy. For gold-FAIL fixtures, also require `parsed_dimensions[fail_dimension] == "FAIL"` for driver-level agreement; report “right verdict, wrong reason” separately. Add a canned test where the intended driver passes but an unrelated dimension fails.

   Hard question: with four negative fixtures and a constant always-FAIL judge scoring `4/4`, what observable result currently distinguishes a discriminating judge from a broken one?

## CONCERN (should address)

1. [fixtures.json:243](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/evals/fixtures/fixtures.json:243), [rubric.md:44](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/evals/fixtures/rubric.md:44) — the O2 gold label conflicts with the rubric’s load-bearing validity rule.

   Why it breaks: the fixture declares “a bigger context window always means better answers” a manufactured strawman. That belief is plausibly widespread in LLM product discourse. The rubric says a widespread prior makes the contrast legitimate and penalizes its removal. An unsupported subjective judgment is being installed as gold truth.

   Concrete fix: obtain blinded labels from multiple reviewers on whether the prior is manufactured or widespread. If agreement is weak, mark it ambiguous and exclude it from agreement claims; replace it only with an independently adjudicated example, not prose tuned to keep tests green.

   Hard question: what evidence establishes that this prior is manufactured rather than a real widespread belief?

2. [false_positives.json:2](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/evals/fixtures/false_positives.json:2), [test_false_positives.py:124](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/evals/fixtures/test_false_positives.py:124) — the false-positive suite is a synthetic smoke fence, not evidence about non-native writers.

   Why it breaks: all nine negatives are hand-authored pseudo-human samples; eight score `0` and one scores `5` against threshold `14`. They were written with knowledge of detector tells, so they are not adversarial hard negatives. The “checker can fail” test appends obvious AI slop, making the sample no longer clean; it proves control flow, not false-positive sensitivity.

   Concrete fix: narrow the release claim to “synthetic regression fence.” Build a de-identified held-out corpus from real writers across several L1 backgrounds, genres, and lengths, with provenance and independent human labels. Include legitimate human prose near the threshold and containing isolated flagged phrases. Replace the poisoned-clean test with either a mocked threshold-crossing runner test or an authentic human hard negative.

   Hard question: are nine author-synthesized ESL caricatures a defensible proxy for the real non-native-writer risk cited by the suite? If yes, show the sampling and labeling argument.

3. [comms-polish/SKILL.md:3](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/skills/comms-polish/SKILL.md:3), [comms-draft/SKILL.md:3](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/skills/comms-draft/SKILL.md:3), [test_skill_manifests.py:49](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/evals/test_skill_manifests.py:49) — the router seam is claimed fixed without behavioral evidence.

   Why it breaks: CI only proves each description is non-empty. It cannot detect whether hosts still choose `comms-polish`, select both skills, or fail to activate either for mixed requests.

   Concrete fix: record a routing smoke matrix with at least pure polish, pure drafting, mixed polish-plus-add, KB question, and ambiguous edit prompts across supported hosts. Assert expected single-skill selection and document any model-dependent ambiguity.

## SUGGESTION (nice to have)

1. [judge.py:295](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/evals/fixtures/judge.py:295) — the runtime warning states same-family judging inflates PASS by `~10–25%` without an in-repo citation or experiment. Remove the numerical range or attach the source and applicability limits.

2. [fixtures_fail.json:2](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/evals/fixtures/fixtures_fail.json:2), [run_all.sh:8](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/evals/run_all.sh:8) — comments already say 13 fixtures and ~23 tests while the branch runs 14 PASS fixtures and 125 tests. Replace volatile counts with cohort names or derive them in output.

VERDICT: REVISE
