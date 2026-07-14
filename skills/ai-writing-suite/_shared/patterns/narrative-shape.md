# Document / Narrative Shape (文档叙事形状)

Every other category in this catalog operates at the **sentence or paragraph**
level: a word, a clause, a rhythm. This one operates one altitude higher — at the
**shape of the whole document**: how its themes are stated, how its threads
resolve, how its stakes rise, whether it leaves anything unresolved. A piece can
pass every lexical, rhythm, and punctuation check line by line and still read as
machine-written because its *overall arc* is the giveaway.

This is why the category matters. Lexical de-slopping is now a commodity — a dozen
public tools scrub AI vocabulary. But structure is a different fingerprint. As
reported in the StoryScope press coverage (UMD + DeepMind work, 2026-07 — we have
not independently verified the arXiv id or re-run the 93.2% figure ourselves), a
model classified human-vs-AI writing with high accuracy from narrative structure
alone, and — the load-bearing claim — that signal reportedly **survives adversarial
lexical cleanup**: *you cannot prose-edit your way out of a structural fingerprint.*
Swapping every flagged word leaves the arc untouched. So this category has to be
caught at draft-*shaping* time, not sentence-polish time.

Like `overstepping-presumption.md`, this is a **stance/shape tell, not a
vocabulary tell**: every word can be clean while the document over-explains its own
theme or ties every thread in a bow. The mechanical detector (`evals/detector/`)
scores these `before` texts near **zero** — it reads words and density, and there
is no word to flag. **This category is judge-only and advisory. It never gates
CI.** It is applied by the LLM judge (`narrative_shape_ok` in
`evals/fixtures/rubric.md`) and, at draft time, by `comms-draft`'s structural
planning step.

The load-bearing rule is the **validity condition** (below): a structural property
is a tell **only when it is unmotivated**. A genuinely simple update *should*
resolve tidily; a 200-word status memo has no room for ambiguity, and demanding it
would be over-correction — a *worse* failure than the tell, because it manufactures
fake complexity. Apply the validity condition before flagging anything here.

---

### N1 — Over-explained theme (states its own moral)

- **Tell:** The piece names its own lesson instead of letting the material carry
  it: "The real lesson here is…," "This just goes to show…," "a reminder that
  impact rarely comes from the big launches." A human writer trusts the reader to
  draw the moral from the facts; the machine spells it out, then admires it. The
  content was already in the facts — the moral sentence only performs a takeaway.
- **Fix (少写):** Delete the stated moral and keep the material that earned it. If
  the facts genuinely don't carry the point, that's a *content* gap — add a
  concrete detail, don't add an abstraction about the detail.
- **Before:** We shipped the billing fix Tuesday. Double-charge tickets dropped
  from 40 a week to 3. The real lesson here is that small, unglamorous fixes
  deliver the most value.
- **After:** We shipped the billing fix Tuesday. Double-charge tickets dropped
  from 40 a week to 3.
- **Self-test:** Does the point survive if I delete the sentence that *names* it?
  If yes, the naming was the tell.

---

### N2 — Tidy single-track resolution (every thread closes, no residue)

- **Tell:** Every thread the piece opened is closed by the end, every risk "turned
  out fine," and the writer "came out stronger." Real accounts leave residue — an
  open question, a thing that still doesn't work, a cost that didn't pay off. A
  document where *nothing* is left unresolved reads as authored to a template, not
  lived through.
- **Fix (多写, honestly):** Surface a thread that genuinely stays open. **Only a
  real one** — see the validity condition. Do not manufacture a loose end to look
  authentic; that is the over-correction this category's failure fixture guards
  against.
- **Before:** We ran the migration over the weekend. The database moved cleanly and
  the API held. Every risk we'd listed turned out fine, and the team came out
  stronger for it.
- **After:** We ran the migration over the weekend. The database moved cleanly and
  the API held. But I'm not ready to call every risk closed — a couple of things we
  flagged are still shaking out, and I'd rather sit with that than declare a clean
  win.
- **Self-test:** Is *anything* left open — and is that open thread **real**, or did
  I invent it to dodge the tell? (Note the fix here is a qualitative walk-back of
  the overclaim, not a new invented stat — inventing a specific new fact, like a
  metric never mentioned before, would trade a narrative-shape tell for a
  fabrication, which `no_fabrication` in `evals/fixtures/rubric.md` treats as the
  higher-stakes failure.)

---

### N3 — Flat escalation (uniform stakes curve)

- **Tell:** Each beat lands with the same weight; nothing is the peak. "Day one we
  found a bug. Day two we found a bug. Day three we found a bug. We fixed each and
  moved on." The events are listed at a constant altitude with no rise, no climax,
  no beat that matters more than the others. StoryScope press coverage reports flat
  escalation as a **per-model fingerprint — specifically associated with Claude's
  own output** (see the citation hedge above) — so name it honestly: this is
  plausibly *our* structural tell, and it reportedly survives word-swapping.
- **Fix (re-weight, not add):** Re-weight to where the stakes actually peaked using
  the SAME events the material already gives you. One beat carried more effort or
  consequence; make the arc rise to it instead of pacing every beat identically. Do
  not invent a bigger event or a new consequence to manufacture a peak — that trades
  the shape tell for a fabrication.
- **Before:** Day one, a bug in the export job. Day two, a bug in the import job.
  Day three, a bug in the reconciliation job. We fixed each one and moved on.
- **After:** Day one, a bug in the export job — fixed it, moved on. Day two, one in
  the import job — fixed it, moved on. Day three, the reconciliation job: that one
  took real digging, and we didn't move on until we were sure it was right.
- **Self-test:** Which beat is the peak? If every beat weighs the same, the curve is
  flat. (The re-weighting above uses only the three bugs and the "fixed and moved
  on" claim already in `before` — no new bug, no new invented consequence.)

---

### N4 — Absent ambiguity (no competing reading, no unresolved tension)

- **Tell:** The document admits exactly one reading and one recommended action, with
  no competing signal, no tension the writer is still holding. "The test is clear:
  variant B won. Roll it out." Real analysis usually carries a live tension — a
  countervailing number, a reading the writer *hasn't* ruled out. A piece with zero
  ambiguity where the situation actually has some reads as a machine that resolved
  what a human would still be weighing.
- **Fix (多写, honestly):** Name the competing signal you're actually holding. **Only
  if one exists** — the validity condition forbids inventing doubt to look human.
- **Before:** The A/B test is clear: variant B lifted conversion 6%. Roll it out to
  everyone next week.
- **After:** The A/B test showed variant B lifted conversion 6%. But the picture
  isn't as clean as "roll it out" makes it sound, and I want another week before
  calling it decisive.
- **Self-test:** Is there a real competing signal I flattened out to sound decisive?
  If the situation genuinely has only one reading, leave it alone (see below). (The
  6% figure is preserved verbatim from `before` — the fix holds the ambiguity
  qualitatively rather than inventing a second metric, which would fabricate a fact
  `before` never contained.)

---

## The four self-test questions

Run these on the whole draft, not on a single line:

1. Does the draft **name its own moral** — and does the point survive deleting that
   sentence? (N1)
2. Does **every** thread close with **no** residue? (N2)
3. Is there a **peak**, or does every beat weigh the same? (N3)
4. Did I flatten a **real** competing reading to sound decisive? (N4)

If a shape tell is present **and** the validity condition below is met (the tidy
shape is *unmotivated*), it's a tell → reshape. If the shape is *motivated* by the
task (a genuinely simple, single-outcome update), leave it — forcing complexity in
is the worse error.

## The validity condition (do not skip this)

> A structural property is a narrative-shape tell **only when it is unmotivated**.
> A genuinely simple update SHOULD resolve tidily (N2); a single-outcome result IS
> unambiguous (N4); a truly uniform sequence of equal events HAS a flat curve (N3).
> Demanding residue, ambiguity, or a manufactured peak where the material doesn't
> supply one is **over-correction** — it injects fake complexity, which is a worse
> failure than the tell it dodges.

Worked contrast:

- A retro that claims **every** risk "turned out fine" and the team "came out
  stronger," when the writer privately knows a couple of those risks are still
  shaking out → the tidy resolution is **unmotivated** (real residue exists and was
  hidden) → **N2 tell** → surface it *qualitatively* (see N2's fix) rather than by
  inventing a new metric to make the residue sound concrete.
- A 200-word "the nightly backup is green again; it was a one-character cron typo"
  update → the tidy resolution is **motivated** (the fix genuinely closed the
  thread) → **not a tell** → leave it. Bolting on "though I keep wondering whether
  something deeper is unresolved…" manufactures fake ambiguity → **over-correction**
  (this is the failure fixture in `evals/fixtures/fixtures_fail.json`).

The discriminator is always: **does the material supply the residue / ambiguity /
peak, or am I inventing it to pass a shape check?** Real → reshape to show it.
Invented → the flat shape was honest; leave it.

## 少写 / 多写 (write-less / write-more) substitution

- **少写 (write less) — for N1:** delete the sentence that names the moral; the
  facts already carried it. Over-explained-theme almost always shrinks.
- **多写 (write more) — for N2 / N4, only when real:** surface the open thread or the
  competing signal the material actually contains. This is *not* padding — it's
  reporting a real thing the tidy draft omitted. If the material has no such thing,
  writing more here is the over-correction the validity condition forbids.
- **Re-weight, not add — for N3:** flat escalation is usually fixed by shifting
  emphasis to the beat that already mattered most, not by inventing a bigger event.

## Scope

- Operates at **document altitude** — the arc of the whole piece, not any single
  sentence. All eight other catalog categories work below this level; this is the
  only one that reads the shape.
- **Detector-blind by design:** no vocabulary or density signal. Applied by the LLM
  judge (`narrative_shape_ok` in `evals/fixtures/rubric.md`) and by `comms-draft`'s
  **structural planning** step (draft-shaping time), never by the mechanical
  detector, and it **never gates CI**.
- **Excludes motivated shapes.** Whether a tidy resolution or a single reading is a
  tell depends on what the material can support — a task question, not a
  prose-pattern question. Flag only shapes that are *unmotivated* by the material.
- Paired with a failure mode: an over-correction that manufactures fake ambiguity /
  artificial loose ends to dodge the tell (`fixtures_fail.json`,
  `fail_dimension: narrative_shape_ok`) — a category that can be over-applied must
  ship the exemplar of over-applying it.
