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
| `payoff_clear` | **(Pairs with `overstepping_removed`; score ONLY when a presumption was removed — N/A otherwise.)** After the manufactured presumption is deleted, the surviving claim reads as a complete, self-standing statement. | The leftover is a stub that lost the antecedent the deleted frame supplied — e.g. "It reduces them" after "you think X causes more outages, but" was cut, so "it"/"them" no longer resolve. |
| `narrative_shape_ok` | The **whole document's arc** carries its point without a machine-shape tell: no stated-own-moral (N1), no tidy single-track close where the material has real residue (N2), no flat/uniform stakes curve (N3), no flattened-away competing reading (N4) — **and** any residue/ambiguity/peak the `after` shows is **real**, not manufactured. | The `after` still names its own moral / ties every thread in a bow / paces every beat flat / admits only one reading **when the material supports more**; **OR** it manufactured fake ambiguity or an artificial loose end to *look* human where the update was genuinely simple (over-correction → also fails, harder). |

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

### `payoff_clear` — the leftover must stand on its own

`payoff_clear` **pairs with** `overstepping_removed`. When the manufactured
presumption is deleted via 少写 (write-less), check the **surviving** claim: does
it read as a complete, unambiguous statement, or a **stub** that lost the
antecedent the deleted frame supplied?

- "You think merging causes more outages, **but it reduces them**" → over-stripped
  to "**It reduces them**" strands "it"/"them" → `payoff_clear` **FAIL**.
- The clear fix names the subject: "**Merging reduces outages**" → `payoff_clear`
  **PASS**.

Score `payoff_clear` **ONLY when a removal happened**; when no presumption was removed,
emit an explicit `payoff_clear: N/A` (never silently omit the line — `aggregate()` treats
an explicit N/A as vacuously satisfied and drops it from the verdict, whereas an omitted
required line would void the whole fixture's verdict). This is a *repair-quality* check (is
the fix complete), not a general "is this sentence clear" check — it stays scoped to the
少写 leftover. Judge-only/advisory; never gates CI.

### `narrative_shape_ok` — the document's ARC, not its sentences

`narrative_shape_ok` is the one dimension scored at **document altitude**. Every
other dimension reads sentences; this one reads the whole arc. It exists because
lexical de-slopping is a commodity but structure is a separate fingerprint — as
reported in the StoryScope press coverage (2026-07; we have not independently
verified the arXiv id or re-run the reported accuracy figure), narrative structure
alone was enough to classify human-vs-AI writing, and the signal reportedly
**survives lexical cleanup**. A rewrite can pass `tells_removed`,
`meaning_preserved`, and every vocabulary check while its shape stays machine-made.

The judge weighs four sub-shapes: over-explained theme (states its own moral, N1),
tidy single-track resolution (every thread closes with no residue, N2), flat
escalation (uniform stakes curve — reportedly associated with Claude's own output
per the same press coverage, N3), and absent ambiguity (one reading where the
material supports more, N4). See `_shared/patterns/narrative-shape.md` for the full
citation hedge.

**The load-bearing rule is the same shape as over-stepping's validity condition:**

> A narrative-shape property is a tell **only when it is unmotivated**. A genuinely
> simple update SHOULD resolve tidily; a single-outcome result IS unambiguous; a
> truly uniform sequence HAS a flat curve. Demanding residue/ambiguity/a peak the
> material doesn't supply is **over-correction** — injected fake complexity, a
> *worse* failure than the tell.

So `narrative_shape_ok` FAILs in **two** directions:

- **Under-corrected:** the `after` keeps a shape tell (names its moral, ties every
  thread, paces flat, admits one reading) **when the material supported more**.
- **Over-corrected:** the `after` manufactured fake ambiguity or an artificial loose
  end to *look* human on a genuinely simple update. Do not reward "it left a thread
  open, good" — an invented open thread is over-correction and FAILs `narrative_shape_ok`.

The judge's test: **does the material supply the residue / ambiguity / peak, or was
it invented to pass a shape check?** Real and shown → PASS. Real but flattened away
→ FAIL (under). Invented → FAIL (over). This dimension is **judge-only and
advisory** — the mechanical detector is blind to structure (it scores these `before`
texts near 0) and whether a shape is motivated is partly a task question, so it
**never gates CI**. It is applied at draft-*shaping* time by `comms-draft`, not as a
line-edit self-scan.

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

PAYOFF-CLEAR CHECK (dimension: payoff_clear) — score ONLY when a presumption was removed
After deleting a manufactured presumption, does the surviving claim stand on its own as a
complete, unambiguous statement? FAIL if the leftover is a stub whose pronouns/references
lost the antecedent the deleted frame supplied (e.g. "It reduces them" with no named
subject). PASS if the fix names the subject ("Merging reduces outages"). If nothing was
removed, output `payoff_clear: N/A` (do NOT drop the line — the aggregator treats an
explicit N/A as vacuously satisfied; a silently omitted line would void the whole verdict).

NARRATIVE-SHAPE CHECK (dimension: narrative_shape_ok) — judge the WHOLE arc, not sentences
A document's SHAPE can be a machine tell even when every sentence is clean (structure
survives lexical de-slopping). Four sub-shapes: N1 over-explained theme (states its own
moral); N2 tidy single-track resolution (every thread closes, no residue); N3 flat escalation
(uniform stakes, no peak — Claude's own fingerprint); N4 absent ambiguity (one reading where
the material supports more).
VALIDITY CONDITION: a shape is a tell ONLY IF it is UNMOTIVATED. A genuinely simple update
SHOULD resolve tidily; a single-outcome result IS unambiguous. Test: does the material supply
the residue/ambiguity/peak, or was it invented to pass a shape check?
  - `after` keeps the tell when the material supported more -> narrative_shape_ok: FAIL (under)
  - `after` manufactured fake ambiguity / an artificial loose end on a genuinely simple update
    -> narrative_shape_ok: FAIL (over-correction — do NOT reward "it left a thread open")
  - `after` reshaped to show a REAL residue/ambiguity/peak, or correctly left a motivated tidy
    shape alone -> narrative_shape_ok: PASS
```

## What the judge must NOT do

- Do not reward fluency that came from inventing facts. A vague-but-honest
  rewrite beats a specific-but-fabricated one.
- Do not penalize the `after` for being shorter — concision is the goal.
- Do not re-flag tells the fixture did not ask about (scope to `rubric_focus`).
