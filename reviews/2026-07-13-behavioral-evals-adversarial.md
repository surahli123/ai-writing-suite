# Codex Adversarial Review — behavioral evals for comms-draft + voice-onboard

Model: gpt-5.6-sol, reasoning effort xhigh, read-only sandbox
Date: 2026-07-13
VERIFIED_AGAINST: feat/behavioral-evals-draft-voice @ cb04b30
VERDICT: REJECTED

Reviews research items #3/#4 (see `docs/improvement-plan-deslop-landscape-2026-07-11.md`).
Codex was asked to TRY TO BREAK THE CHECKERS — to construct novel evasions rather than
re-run the shipped planted positives. It did, and it found a defect neither the
orchestrator's own mutation probes nor the OMC code-reviewer caught: **the GOOD artifact
itself violates the contract the eval exists to test.**

Independently confirmed by the orchestrator against HEAD before acting:
- `voice-onboard/SKILL.md` says mixed genres must yield an offer to extract TWO profiles
  ("Don't average across genres ... Mixed samples -> split, don't flatten").
  `voice_profile_good.md` is one blended profile — it commits the forbidden failure.
- The 3+ occurrence rule is absolute, yet the good profile lists `forecast` (corpus 2x)
  under `## Vocabulary` and `boring` (corpus 1x) under `## Vocabulary Do` — both positive
  claim sections.
- The declared ground truth counts `ledger` at 4x CROSS-GENRE (tweet 3 + memo 1). The spec
  forbids exactly that aggregation; it clears the 3+ bar only by luck.

Note the truncation caveat: this file preserves the tail of the reviewer's structured
output (the last BLOCKER onward through the verdict). The earlier BLOCKERs are summarized
in the remediation commit and in `2026-07-13-behavioral-evals-remediation.md`.

---

## CONCERN (should address)

1. [test_draft_cases.py:59](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/evals/fixtures/test_draft_cases.py:59) and [test_voice_extraction.py:88](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/evals/fixtures/test_voice_extraction.py:88) — tests mostly restate the exact planted artifacts and implementation choices. That is why 201 tests pass while held-out bad artifacts escape and good variants fail.

   Fix: add independent adversarial tables and metamorphic tests covering paraphrase, negation, capitalization, Unicode, unit changes, word-number forms, morphology, equivalent numeric representations, and legitimate explanatory mentions of excluded traits.

2. [run_voice_extraction.py:65](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/evals/fixtures/run_voice_extraction.py:65) — morphology is intentionally ignored. `delved` counts as zero uses of `delve`; case handling does work (`Ledger LEDGER ledger` counted as three). This can falsely publish “never uses delve” about an author who writes “delved.”

   Fix: define whether the contract means exact surface token or lexical family. For lexical-family semantics, use fixture-declared inflection aliases or a small stdlib normalizer. For exact-token semantics, state “exact token absent” rather than the broader “never uses this word.”

3. [run_draft_cases.py:380](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/evals/fixtures/run_draft_cases.py:380) — judge evidence verification excludes `kb_facts`, although KB facts are legitimate sources, and verification warnings do not affect aggregation.

   Fix: verify against brief, KB, and draft; mark artifacts with missing/non-verbatim required evidence as unscored. Keep the judge opt-in and advisory.

## SUGGESTION (nice to have)

1. [README.md:21](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/evals/README.md:21) — the documented eval surface still lists three components and omits both new runners.

   Fix: document steps 5 and 6 and label them honestly as synthetic regression fences, not end-to-end behavioral evidence.

Fresh `bash run_all.sh` exited 0: 201 tests passed, calibration remained `3/8 = 38%`, and the default path stayed key-free/offline. Those results prove the current tests agree with the current fixtures; the break tests above prove they do not establish construct validity.

VERDICT: REJECTED
