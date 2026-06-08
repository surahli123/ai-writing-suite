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

Structural-tell dimensions appear in `rubric_focus` by name for fixtures that
target them: `negative_parallelism_removed`, `rule_of_three_removed`,
`engagement_hook_removed`, `false_concession_removed`, `hedge_stack_removed`,
`vague_attribution_removed`, `filler_removed`.

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
```

## What the judge must NOT do

- Do not reward fluency that came from inventing facts. A vague-but-honest
  rewrite beats a specific-but-fabricated one.
- Do not penalize the `after` for being shorter — concision is the goal.
- Do not re-flag tells the fixture did not ask about (scope to `rubric_focus`).
