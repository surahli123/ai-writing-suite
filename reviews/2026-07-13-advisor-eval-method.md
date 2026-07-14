# Advisor review — is the paired-artifact + deterministic-checker method sound?

Date: 2026-07-13. Scope: method-level judgment on batch 2 (feat/behavioral-evals-draft-voice,
cb04b30), per the advisor brief. Line-level findings belong to the other two lanes and are not
repeated here.

State note: the fix pass (agentI) was editing the working tree while I reviewed. As of my
probes, the fabrication check on disk is already tokenized (`_num_key ... in src_nums`) and
catches the `50/15/1 vs 150` evasion; `check_learns_habit_word` still passes a profile that
says "ledger — she never writes this word" (probe output below). My verdicts are about the
method, which is stable across those edits.

Probe evidence (run against the working tree):

```
fabrications found in novel evasion: ['50%', '15', '1']          # post-fix: caught
inverse-claim profile passes learns_habit_word: (True, "'ledger' (4x, clears 3+) is learned")
```

---

## Q1 — Structurally doomed, or sloppy implementation? Neither; it's a third thing.

The four-failure recurrence is not a coincidence, and it is also not doom. It is the
predictable signature of a specific process flaw: **the checker and both artifacts were
authored in the same pass, so the checker's acceptance test was "separate these two known
points."** In classifier terms: one positive and one negative example per failure mode,
training set == test set. With N=1 per class the separating boundary is wildly
underdetermined, and an author optimizing for "the planted positive trips" will converge on
the cheapest discriminator that separates the pair — substring lookup, presence/absence,
polarity-blind mention counts. All four MAJOR/BLOCKER findings are instances of exactly that
degenerate-discriminator shape. Any team re-running this process would reproduce the same
failure family; that is why it recurred across four independent checks.

This is the same lesson batch 1 already taught one level down: the constant always-FAIL judge
aced the negative cohort until the confusion matrix added the other cohort. A checker
validated only on the pair it ships with is the same bug — it looks discriminating because
nobody showed it a point off its training set. The reviewer's novel evasions were the missing
holdout, and the checkers failed the holdout. Predictable, fixable, and the fix (every evasion
becomes a permanent regression case) is the right one — but see Q3 for why hand-collected
evasions alone don't close the gap.

Separately, there IS a structural ceiling, and it should be named without embarrassment:
**this suite never executes the skill.** Both artifacts are hand-authored; no LLM behavior
passes through the eval. Even a perfect checker therefore measures zero bits about what
comms-draft actually does when invoked. What the deterministic suite really is:

1. **Unit tests for a grader.** The checkers are output-graders; the paired artifacts and
   evasion corpus validate the grader itself.
2. **A regression fence on the artifact contract** (output shape, [NEEDS:] discipline,
   question budget, criteria dimensions, profile-vs-corpus consistency).

Both are genuinely valuable — (1) is exactly what makes any future live run trustworthy.
Neither is "behavioral eval coverage of the skill." The method is sound *for what it can
claim*; the implementation flaw and the overclaim are separable problems.

A second ceiling, illustrated by the still-open direction-blindness: deterministic checks on
free prose approximate semantics with lexical proxies. Each hardening round narrows the gap
(tokenized numbers, negation windows) but never closes it — claim polarity in arbitrary prose
is not decidable by stdlib regex. The right response is usually not a smarter parser but a
**more checkable artifact contract** (see Q3c/Q4: make the profile carry numbers, then assert
on numbers).

## Q2 — The honest claim

"Behavioral eval coverage" overclaims twice: no skill behavior is exercised, and the checks
verify surface/contract properties, not semantics. Honest wording, parallel to the
"synthetic regression fence" narrowing already done for the FP suite:

> **comms-draft and voice-onboard ship deterministic output-contract checks**: graders that
> score a produced artifact against the SKILL.md contract (fabrication shape, [NEEDS:]
> discipline, question budget, criteria dimensions; habit/noise/absence/genre consistency
> against a counted synthetic corpus). The graders are themselves regression-tested against
> paired good/bad exemplars and an adversarial evasion corpus. **The skills' live behavior is
> exercised only by the opt-in LLM-judge lane (advisory, never gates CI)** and is otherwise
> unmeasured.

Drop the word "behavioral" from README/CHANGELOG for the deterministic lane entirely. If a
sentence can't survive the reader asking "did an LLM ever run?", it's the wrong sentence.

## Q3 — The better design inside the constraints

The honest answer to the sub-question is yes: **deterministic checks can only guard the
artifact contract; real behavioral signal requires a model in the loop, and should be labeled
as such.** Within that, four upgrades, all stdlib/key-free:

- **(a) Generated mutant families instead of one hand-authored bad artifact.** For each
  failure mode, programmatically mutate the good artifact: inject a random number absent from
  the sources, swap a habit word for a 0x word, collapse the two genre figures into their
  mean, strip the [NEEDS:] block. The checker must catch k/N generated mutants — report a
  catch rate, not a binary planted positive. This is mutation testing for graders: mutants
  are drawn from a family, not memorized, so a checker rigged to the shipped exemplar fails
  immediately. This one change removes the Q1 failure class at its root; hand-collected
  evasions then become the *hard* tail of the corpus rather than the whole defense.
- **(b) Adversarial authorship as process, not accident.** The evasion corpus stays
  append-only and is authored by a different lane/model than the checker author (this batch's
  reviewer did it by luck; make it the rule). A checker PR that doesn't survive the corpus
  doesn't merge.
- **(c) Assert on numbers wherever truth is countable.** The voice corpus already declares
  and recomputes ground truth — the strongest part of this design. Extend that: when a
  profile states a figure, recompute it and require agreement, instead of parsing prose
  claims for polarity.
- **(d) The real behavioral lane exists in the plan already — build it (plan item #8).** A
  scheduled `workflow_dispatch` job (repo secret, never the default CI path) that actually
  RUNS comms-draft/voice-onboard against these briefs/corpora and grades the transcripts with
  these same deterministic graders + judge. That is the only design in which this batch's
  work measures the skill — the checkers become the grader for real outputs rather than a
  stand-in for behavior. Everything in (a)-(c) is what makes (d) trustworthy when it lands.

## Q4 — Sequencing: the harden-first call was right; it is now paying diminishing returns

"Harden evals first" was correct and has receipts (the constant-judge catch alone justified
batch 1). But cost-of-error accounting now points the other way: this layer gates nothing
user-facing; a residual checker false-negative costs a missed regression in a fence that
didn't exist a month ago. Against that, three review lanes plus an advisor are currently
pointed at ~600 lines of fixture-grader code. The tell that this is tipping into
procrastination: batch 2's failure modes were found by reviewers reviewing the eval of a
skill that has never been run — a self-referential loop with no user or live output anywhere
in it.

Recommended order: **finish the in-flight fix pass + the Q2 rewording + (a) mutant
generation, then stop hardening and ship differentiators.** Specifically:

1. **#15 stylometric fingerprint next** — it is a product differentiator AND it retroactively
   strengthens this very eval: measured numbers in the profile are directly assertable
   (Q3c), which is the honest fix for direction-blindness that no regex will ever be.
2. **#25 KB-ingestion tooling** — the highest-stakes untooled item; the entire company-fork
   bet rests on it, and it is ordinary validation code with ordinary tests.
3. **#9 narrative-shape category** — judge-only by design, so it does not depend on this
   deterministic layer at all; nothing in eval-land blocks it.
4. Plan item #8 (scheduled live run) whenever an owner-approved key cadence exists — that is
   the moment "behavioral" becomes an honest word.

Eval work after this batch should be pulled by features (each new capability lands with its
graders) rather than pushed as a standalone hardening program.

## The one change that matters most

Replace the single hand-authored bad artifact per failure mode with a programmatic mutant
generator plus the append-only, separately-authored evasion corpus, and report a catch rate.
Everything else in this batch is salvageable detail; that change removes the failure class
instead of patching its instances.

## Risk lines

- If the owner intends never to run the scheduled live lane (#8), the Q2 wording matters even
  more: without it, the deterministic suite is permanently the only "coverage" and the word
  "behavioral" is permanently wrong.
- Mutant generation can itself be rigged (mutants too easy); pair it with the human evasion
  corpus, and treat a 100% catch rate on mutants alone as suspicious, not reassuring — same
  30-40%-baseline instinct as CLAUDE.md's eval-calibration rule.
- My probes ran against a working tree being edited mid-review; line-level statements
  (tokenized fabrication check in, direction-blindness still open) reflect that snapshot.
