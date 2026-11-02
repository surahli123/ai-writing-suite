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
     One instance goes inline: `**Quote:** "…"`. Several instances of the same
     pattern go one per indented sub-bullet under a bare `**Quote:**` line
     (`  - "…"`).
   - `**Tell:**` the catalog id + name it matches — e.g. `S1 — Significance
     inflation` — and the id **must** be a real entry from `_shared/patterns/`.
   - `**Why:**` one line on why it reads as AI. When the Quote carries more
     than one instance, Why **starts** with `×N`, where N is the number of
     instances counted as the tell, optionally followed by `(+M set aside:
     <reasons>)`.
   - `**Fix:**` the corrected snippet, **shown** — quoted or in a code span —
     never just described in prose. A Fix uses only material in the draft. When
     a better sentence would need a fact the draft lacks, the Fix cuts the
     words or shows a quoted `[NEEDS: …]`; it never invents a number, name, or
     outcome.

   **Instances and counts.**
   - An instance is one contiguous span of the draft that shows the pattern.
     Quote the shortest complete span, with no ellipses. The outer quote marks
     open the snippet and close it at the last matching mark, so quotation
     marks inside the draft stay intact. An optional location in parentheses
     may follow, e.g. `"…" (¶2)`; the location contains no quote marks.
   - Within one finding, each instance is a different, non-overlapping span of
     the draft. Different findings may quote the same sentence. (The checker
     cannot see the same span quoted by two different findings.)
   - Quote every instance when N ≤ 5. When N > 5, quote the clearest 3–5 and
     say in Why where the rest are.
   - Set aside, and report as set aside rather than count, instances that are
     evidence-answered (owner ruling R2), documented habits in a loaded voice
     profile, or inside quotes or code.
   - **Counts describe; they never become quotas or rewrite targets.**

3. **`## What already reads well`.** One or two genuinely strong things, so the
   report is calibrated instead of a pile-on. Assume your pull is toward
   crediting the draft, and correct for it:
   - Each strength is a verbatim quote from the draft plus a reason that fits
     only that passage.
   - Don't praise a property the report criticizes elsewhere. A sentence can
     hold a checkable fact and a vague modifier at once; praising the fact
     while flagging the modifier is fine.
   - No praise for tone, effort, topic, or general structure.
   - **No fake praise.** If nothing reads well yet, say so plainly, with no
     verdict about who wrote it:
     `- Nothing here reads well yet: every sentence carries a flagged pattern.`
     A "Nothing" bullet never sits next to quoted strengths.

3b. **`## Consistency and evidence gaps` — optional, report-only.** Place it
   after `## What already reads well` and before the Coverage and score lines.
   Each bullet gives a location and what differs: a metric reported with n and
   an interval in one row but not its siblings, one metric under two names, or
   a slot the genre needs that is missing. These are not AI tells, so bullets
   carry no catalog id and no Fix, and nothing is filled in. A gap that matches
   a catalog entry (S2, S4, S8) stays a finding with Quote / Tell / Why / Fix;
   never report it in both places. Omit the section when it is empty.

4. **Score — only when asked, always last.** When the user requested a score,
   place the 0-100 AI-tell score as the **final non-blank line of the entire
   report** — nothing follows it, no trailing commentary or sign-off —
   `**AI-tell score:** NN/100 (surface patterns only, not authorship)`, scored
   per the Scoring table. Never as the lead; omit it entirely when no score was
   requested. The line **directly before** the score (ignoring blank lines) is
   the coverage statement, `**Coverage:** <what was checked by rule, what by
   judgment, what was not checked>`, so the reader knows what the number does
   and does not cover.

5. **No authorship verdicts, anywhere.** The report describes the text, never its
   origin. Never write that the draft "was written by AI", "is AI-generated", or
   that "detectors will catch it". Findings say *reads as* or *pattern*, not
   *was produced by*.
