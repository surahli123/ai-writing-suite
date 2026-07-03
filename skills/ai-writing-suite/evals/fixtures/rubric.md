# LLM-Judge Rubric — comms-polish before/after

This is the scoring contract for the **judgment** half of the eval. The
mechanical detector (`evals/detector/`) catches vocabulary and density tells; it
cannot tell whether a rewrite *preserved meaning* or *invented a number*. That
is what this rubric is for: a model reads the `before`, the `after`, and the
expected outcome, and scores the rewrite on the dimensions below.

> **Why both halves exist.** The detector is the cheap, deterministic regression
> gate (runs every commit, no API key). The LLM judge is the quality gate (runs
> on demand, needs a model). A rewrite can pass the detector — score drops to 0 —
> while *failing* the judge by deleting a fact or fabricating evidence. Neither
> half alone is sufficient.

## Inputs the judge receives

- `before` — the AI-shaped draft.
- `after` — the candidate human rewrite (this is what's being scored).
- `genre` — tweet / linkedin / readme / memo (sets length + tone expectations).
- `rubric_focus` — the dimensions that matter most for this fixture.
- `subtle_tell` (when present) — what the AI tell actually is, so the judge
  knows what a good rewrite had to remove.

## Dimensions (score each PASS / FAIL, with a one-line reason)

| Dimension | PASS when | FAIL when |
| --- | --- | --- |
| `meaning_preserved` | Every claim, fact, number, and name in `before` survives in `after` (unless the fixture asks to add specifics). | A claim was dropped or its meaning changed. |
| `tells_removed` | The AI tells named in `subtle_tell` (or the obvious vocabulary tells) are gone. | A flagged tell still reads as AI. |
| `no_fabrication` | Any new specifics in `after` are plausible *placeholders the author would fill*, not invented facts presented as real. **This is the highest-stakes dimension.** | `after` invents a number, source, or quote that `before` did not contain and presents it as fact. |
| `voice_kept` | `after` reads like a competent human in this genre, not generic corporate rewrite. | `after` traded one robotic register for another. |
| `specificity_added` | Where `before` was vague, `after` is concrete (only scored when in `rubric_focus`). | `after` is still vague / empty calories. |
| `genre_fit` | Length and tone fit the genre (tweet ≤ 280 chars, readme is scannable, memo leads with the decision). | Wrong shape for the channel. |
| `overstepping_removed` | `after` removes a **manufactured** reader-presumption — "you assume/think X", "很多人以为 X", a self-Q&A ("Can you…? Yes —"), or a projected mental image ("you picture…") — whose presumed prior X is **not** a real, widespread belief, **and** the underlying claim survives. | The presumption still reads in `after`; **or** `after` stripped a contrast whose X **was** a real widespread belief (that loses information → also fails `meaning_preserved`). |

Structural-tell dimensions appear in `rubric_focus` by name for fixtures that
target them: `negative_parallelism_removed`, `rule_of_three_removed`,
`engagement_hook_removed`, `false_concession_removed`, `hedge_stack_removed`,
`vague_attribution_removed`, `filler_removed`.

### The over-stepping validity condition (the load-bearing rule)

> **A presumption is over-stepping ONLY when the prior X is a manufactured
> strawman. When X is a genuinely common belief the reader holds, the contrast is
> legitimate — removing it loses information.**

This single rule decides every over-stepping case across all sub-types
(presumed-cognition / presumed-misconception strawman / presumed-mental-image /
self-Q&A-as-judge). It pairs `overstepping_removed` with `meaning_preserved`:

- **Positive:** presumption removed **and** claim kept → both PASS → overall PASS.
- **Over-correction trap:** `after` deleted a *legitimate* contrast whose X was a
  real widespread belief (e.g. "love **isn't** a feeling, it **is** behavior") →
  `meaning_preserved` **FAIL** → overall FAIL — even though a naive reading might
  reward "a `不是X而是Y` was removed, good." Do not reward that.

The judge's test: does the point still stand after deleting "you think / 你以为 /
很多人以为"? Stands → the frame was over-stepping (`overstepping_removed` PASS if
`after` dropped it). Collapses → X was a real prior, the contrast was legitimate
(`meaning_preserved` FAIL if `after` dropped it).

This dimension is **judge-only and advisory** — the mechanical detector is blind
to it (the tell is in stance, not vocabulary), and whether a line over-steps is
partly intent-dependent, so it never gates CI.

## Verdict aggregation

- **PASS overall** = all `rubric_focus` dimensions PASS **and** `no_fabrication`
  PASS (no_fabrication is always required, even when not listed in focus).
- **FAIL overall** = any focus dimension FAIL, or any fabrication.

## Judge prompt template (zero-shot, model-agnostic)

```
You are evaluating a prose rewrite. The "before" is AI-shaped writing; the
"after" is a human rewrite of it. Judge ONLY the "after".

GENRE: {genre}
WHAT THE AI TELL WAS: {subtle_tell}
DIMENSIONS TO WEIGH: {rubric_focus}

BEFORE:
{before}

AFTER:
{after}

For each dimension, output: <dimension>: PASS|FAIL — <one-line reason>.
Then output: VERDICT: PASS|FAIL.
Rule: no_fabrication must PASS or the whole verdict is FAIL, regardless of how
good the prose reads.

OVER-STEPPING CHECK (dimension: overstepping_removed)
A line "over-steps" when it thinks FOR the reader: presuming a belief/misconception,
painting a mental picture, or asking-then-answering its own rhetorical question, then
correcting from above. It is over-stepping ONLY IF the presumed prior is a manufactured
strawman. If the prior is a real, widespread belief, the contrast is LEGITIMATE — do not
reward its removal; deleting it loses information (fail meaning_preserved).
Test: does the point still stand after deleting "you think / 你以为 / 很多人以为"?
  - stands → the frame was over-stepping → overstepping_removed: PASS if `after` dropped it
  - collapses (X was a real prior) → contrast was legitimate → meaning_preserved: FAIL if `after` dropped it
```

## What the judge must NOT do

- Do not reward fluency that came from inventing facts. A vague-but-honest
  rewrite beats a specific-but-fabricated one.
- Do not penalize the `after` for being shorter — concision is the goal.
- Do not re-flag tells the fixture did not ask about (scope to `rubric_focus`).
