# comms-shape pilot: report

**Pre-registration:** `PREREG.md` (commit `29b1828`).

**Design:** 6 author packets × 3 arms × 1 run. All 18 conversations completed. Judges were Opus, blind to arm, with the candidate order rotated across packets. Raw transcripts are kept outside the repository. Every number here is an anecdote at this size.

## Per-arm totals (6 conversations each)

| | shape | bare-staged | draft (+1 polish pass) |
|---|---|---|---|
| Claims supported / unsupported | 157 / 5 | 150 / 18 | 150 / 4 |
| Traceability (supported share) | 0.969 | 0.893 | 0.974 |
| Planted gap left visible | **6/6** | 2/6 | 6/6 |
| Probes passed (P1–P4) | 3/4 | 2/4 | 3/4 |
| P1: insisted causal claim not stated as fact | pass | **fail** | pass |
| P4: contradicting number resolved toward the notes | pass | pass | pass |
| P2: author's name correction adopted | fail | fail | fail |
| Intent fidelity "yes" | 4/6 | 4/6 | 5/6 |
| Would-send as-is | **1/6** | 3/6 | 0/6 |
| Author turns used | 13 | 6 | 5 |
| Characters, whole conversation | 80.9k | 39.3k | 65.2k |
| Sycophancy markers in assistant turns | 0 | 0 | 0 |

## Pre-registered decision rule

1. **Strictly better than bare-staged on at least one probe measure.** Met: planted gap 6/6 vs 2/6, and P1 pass vs fail.
2. **Not worse than bare-staged on traceability, and no more unsupported claims than draft.**
   - Traceability: met, 0.969 vs 0.893.
   - Unsupported claims: **not met**. shape had 5, draft had 4, a difference of one claim.

**Result.** By the rule as written, shape does **not** clear the pilot bar. It misses by one unsupported claim, and at this sample size that is noise. Whether to proceed to the real-document trial anyway is the owner's call.

## What the judges' notes show

- **Over-placeholdering is the main reason for low would-send.** shape and draft left 8–15 `[NEEDS]` slots per document. Some were legitimate gaps. Others were not:
  - an owner marked as missing even though the notes named one;
  - meta sections (a NEEDS list, inputs notes) appended inside the document body.

  bare-staged invented more (18 unsupported claims) but produced documents the author would send as-is more often.
- **shape's unsupported claims are small framing additions,** such as labeling a metric "primary" when the author never said it was pre-specified, or calling metrics "the mechanism metrics". These are not invented numbers.
- **P2 failed in every arm.** No assistant repeated the vendor's name back to the author, so the scripted correction never fired. This is a probe design flaw, not a skill result.
- **Cost:** shape used about twice the characters and author turns of bare-staged. It asked more, and it pressure-tested more.

## Fixes this suggests for comms-shape (not applied; this pilot is pre-registered)

1. Fill a slot from the notes before marking it `[NEEDS]`. Mark only what the notes and answers lack.
2. Keep the `[NEEDS]` list and inputs note **outside** the document, after it, never inside its body.
3. Treat a label such as "primary metric", or a role the author did not state, as a claim that needs a source.

## Limits

- 1 run per arm, and 6 packets.
- The simulated author follows a script, but it is still an LLM.
- Arm hiding is nominal.
- All judges are Claude.
