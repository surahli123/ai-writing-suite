# Final-Pass Checklist

Run this before returning any rewritten or edited copy. It's the last gate — the
quick read-through that catches the tell you reintroduced while fixing another one.

Adapted from `weijt606/anti-vibe-writing` (`final-pass-checklist.md`, MIT); the
optional scoring pass is adapted from the `stop-slop` rubric (MIT).

## The checklist (layered — clear each layer in order)

**L1 — Mechanical floor (non-negotiable).** A single failure here blocks the return, no
matter how good the prose reads. This layer is never traded off against style.

- **Facts, numbers, technical claims, code, commands, and quotes are unchanged.**
- **The fact-to-interpretation boundary still matches source support.** No edit
  turned co-occurrence into cause, possibility into certainty, or a fact into an
  unsupported motive, significance, trend, or conclusion. A supported relation
  was not deleted merely because it used an `-ing` clause or a cue such as
  `reflecting`, `meaning`, or `表明`: this is a relation check, not a word blacklist.
  When the draft was the only source, substantive author analysis was preserved
  and any note says support was not assessed.
- **The author's stance, attributions, and commitments survive.** Wording may
  change; who claims what, and how the author evaluates it, may not.
- **The document agrees with itself.** Applies to multi-paragraph documents with
  numbers, such as readouts, memos, and incident notes. Check five things:
  - every number repeated across the lead, body, and tables matches;
  - shares of a whole add to about 100%;
  - a defined metric keeps one name throughout;
  - whatever the title or lead promises, the body delivers;
  - parallel items that report comparable metrics (rows, cards, bullets) carry
    the same slots (n, interval, baseline, unit), or the difference is
    reported, and one metric or status keeps one name across them. This applies
    only when the metrics are comparable and the slot applies to all of them.

  **Report** each conflict with its locations: in `Notes:` for `rewrite` and
  `edit`, under `## Consistency and evidence gaps` for `detect` and `review`.
  Never fill a missing slot, delete the extra one, or pick a winner; which
  number is right is the author's call. If
  you can run Python, `python3 tools/consistency_check.py <file>` lists the
  numeric conflicts. Run it from the suite root; it is stdlib only.

**L1b — Restraint (run before style).**

- **Reversion test:** compare each changed sentence with the original. If the
  original was correct, clear, and not padded, restore it.
- **Cut check:** after any deletion, re-read the neighbors for dangling
  references ("this", "them", "these results") and broken transitions.
- **Unchanged is allowed:** if no sentence had a named failure (see SKILL.md,
  Edit restraint), the right output is the input. For a `rewrite` request, a
  readability problem the reader would notice counts as a failure. Fix it
  without changing meaning.

**L2 — Slop removal (style).**

- The opening reaches the point quickly — no runway.
- The main point appears early.
- The wording is concrete enough that a reader can picture the thing described.
- No template phrases or startup jargon ("leverage", "seamless", "robust",
  "circle back").
- Headings and bullets remain only where they help the reader.
- Emoji, icons, and decorative markdown are gone — unless the genre preset allows
  them and the author's voice uses them.
- Stock sections (Overview, Key Features, Conclusion) are gone unless they earn
  their keep.
- Repeated content is gone. Repeated structure and terms across the items of a
  parallel set (a status list, feed or card set) stay; they make the set scan.
- **Portability test:** could this sentence sit unchanged in another company's
  or project's document? If so, it says nothing about this one. Make it specific
  using facts already in the source, or cut it. Never invent specifics. Adapted
  from petergyang/no-ai-slop (#33, MIT) and pstack `unslop` rule 27 (MIT).
- The tone has a point of view instead of manufactured balance.
- Warmth comes from specificity and cadence, not filler friendliness.
- The prose sounds written, not assembled.
- Necessary nuance is carried in the sentence, not bolted on as a hedge.
- The result is shorter or sharper, not just different.
- **Deletion-first density:** for each sentence, would deleting it lose a fact,
  reason, condition, consequence, exception, or decision? If nothing is lost, cut
  it — have you deleted every sentence that earns nothing? (Density is
  genre-sensitive and never the sole goal: a reference doc or a careful caveat may
  *need* the extra sentence. This is a question you answer per sentence, never a
  hard length target. Adapted from Hamel Husain's writing recipe.)

**L3 — Genre + voice fit.** Run the cross-checks in the next section.

**L4 — Acceptance (one honest question).** *Would a specific, informed human have written
this?* If no, make another pass before returning.

## Genre + voice cross-checks

Two checks that depend on the layer above this skill:

- **Genre fit:** re-read against the matching `scenario-presets.md` preset. Did the
  rewrite respect that genre's *leave alone* list? (Don't strip a README's real
  lists; don't add a heading to a tweet.)
- **Voice fit:** if `_shared/voice-profile.md` was loaded, does the rewrite still
  sound like that author — sentence rhythm, punctuation habits, preferred terms?
  If no profile existed, did you keep the original's own voice rather than
  flattening it to generic-clean?

## Optional scoring pass

For a borderline draft, score five dimensions (1–10 each) before returning.
Adapted from the `stop-slop` rubric.

- **Directness** — states things; doesn't announce it's about to state them.
- **Rhythm** — in running prose, rhythm follows the content; no march of
  identical moves. (Not a sentence-length target; parallel items keep one shape.)
- **Trust** — respects the reader's intelligence; no over-explaining the obvious.
- **Authenticity** — reads like a person chose the words, not a system.
- **Density** — every sentence earns its place; no filler.

Revisit any dimension you would rate weak. There is no total and no pass
threshold: a numeric bar invites editing toward the number instead of the reader.

> This is a *qualitative* check, separate from the 0–100 AI-tell score in
> `SKILL.md`. The 0–100 score reports density to the user; this checklist is the
> editor's own pre-ship sweep.
