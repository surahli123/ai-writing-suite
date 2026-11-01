# Owner rulings — 2026-11-01

Recorded after the skill-lift eval's adversarial review (`notes/eval-lift-2026-11-01/review/`).
That review found that the eval's judge rubric had pre-decided these questions, so
they are product decisions for the owner, not eval results.

## R1. A user-supplied source authorizes aligning the draft (PR #67 follow-up)

When the user pastes their own notes or source with the draft, and the draft
claims more than the notes support, comms-polish **corrects the draft to match
the notes and says in `Notes:` what changed and why**. Preserve-and-flag
applies only to standalone drafts (no source supplied) or when the user says
"don't change my conclusion". Implemented in step 0
(`claude/laughing-rubin-mkkadx-s0-pr67-fix`): `_shared/fact-interpretation-boundary.md`,
comms-polish step 6, before-after examples, contract tests.

## R2. A presumed objection answered with evidence is kept (overstepping O1)

"You might think X, but Y" is **not** the O1 tell when X is a plausible reader
objection **and** the text answers it with concrete evidence (a number, an
observed incident, a source). Without evidence it stays a tell. When in doubt,
flag as advisory; never strip. Implemented in step 7 (catalog):
- the O1 validity condition;
- the rubric note;
- `overstep-05` changed to the evidence-free variant, with its stub partner
  updated in step;
- new `overstep-07-evidence-answered-en` (PASS, keep) and
  `fail-overstep-evidence-stripped-en` (gold-FAIL).

This supersedes the June gold label for the evidence-answered form only.

## R3. Eval redesign and human anchor

- The per-step "no worse than main" gate is retired: it fails identical text
  9/12 times.
- The final stacked version is evaluated once with a pre-registered,
  noise-calibrated design. If that run shows a regression, bisect to find the
  step that caused it.
- The owner labels about 10 discriminating items to anchor the judges.
