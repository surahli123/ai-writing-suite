# Audit Report Contract Detail

`detect` and `review` output is a fixed report so two audits of the same draft —
even by different models — can be diffed and skimmed. Produce these sections **in
this order**. Inside each section the wording is yours (genre-appropriate); the
structure below is the contract, not a straitjacket.

**Conformance is byte-literal for structure, normalized for punctuation style.**
Section headings, the four field markers (`**Quote:**` / `**Tell:**` / `**Why:**`
/ `**Fix:**`), their order, and the tier names must appear exactly as written
here — that's what makes two reports diffable. Straight `"..."`, typographic
`"..."`, and guillemet `«...»` quotes are treated as equivalent wherever a quoted
snippet is required (paste-from-Word and model output both carry typographic
quotes routinely); a leading byte-order-mark is stripped before checking. Genre
flexibility applies to the *prose inside* each field, never to the markers,
order, or tier names themselves.

1. **Lead line — the one biggest problem, in plain words.** First line, format
   `**Biggest problem:** <one sentence>`. Name the single worst thing a reader
   would react to (Ogilvy: lead with the one thing). Plain language, **never a
   number** — the 0-100 score is not the lead, and severity never collapses into a
   single headline figure.

2. **Findings, grouped under three named severity tiers, each tier defined.**
   Use `## Critical`, `## Moderate`, `## Minor` headings in that order. The line
   immediately under each heading is a one-clause *italic* definition of the tier,
   so two audits sort the same finding the same way:
   - **Critical** — *tells that make the whole piece read as machine-written at a
     glance, or that distort meaning or trust.*
   - **Moderate** — *clear tells a careful reader notices, but that don't dominate
     the piece.*
   - **Minor** — *cosmetic or low-frequency tells only a scan catches.*
   A tier with no findings still keeps its heading and definition, with a single
   `- None.` bullet and **no other bullets in that tier** — `- None.` never sits
   alongside real findings in the same tier.
   Every finding uses this four-part shape, **in exactly this order, once each**:
   - `**Quote:**` the exact snippet from the draft, quoted (not paraphrased).
   - `**Tell:**` the catalog id + name it matches — e.g. `S1 — Significance
     inflation` — and the id **must** be a real entry from `_shared/patterns/`.
   - `**Why:**` one line on why it reads as AI.
   - `**Fix:**` the corrected snippet, **shown** — quoted or in a code span —
     never just described in prose.

3. **`## What already reads well`.** One or two genuinely strong things, tied to a
   specific passage, so the report is calibrated instead of a pile-on. Per the
   repo's review standard, **no fake praise**: if nothing reads well yet, say so
   plainly (e.g. `- Nothing here reads well yet — the draft is AI throughout.`).

4. **Score — only when asked, always last.** When the user requested a score,
   place the 0-100 AI-tell score as the **final non-blank line of the entire
   report** — nothing follows it, no trailing commentary or sign-off —
   `**AI-tell score:** NN/100`, scored per the Scoring table. Never as the lead;
   omit it entirely when no score was requested.
