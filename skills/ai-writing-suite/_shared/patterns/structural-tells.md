# Structural Tells (shape & flow)

How the text is built, not which words it uses. Structure is the single hardest
tell to mask: detectors weight structural regularity above vocabulary, so fixing
every flagged word while leaving the shape untouched still reads as AI.

---

### T1 — Rule of three

| Severity | Enforcement |
| --- | --- |
| low | judge |

- **Tell:** Forcing ideas into groups of three to sound authoritative:
  "innovation, inspiration, and industry insights." Humans don't always think in
  triads.
- **Fix:** Use the natural number. Sometimes one, sometimes four. Two is
  underrated. Max one "adjective, adjective, and adjective" per piece.
- **Sources:** blader (P10), aboudjem (§10), avoid-ai, anti-vibe (三连排比).

---

### T2 — Negative parallelism / tailing negation

| Severity | Enforcement |
| --- | --- |
| low | judge |

- **Tell:** "Not only X but Y," "It's not just about X, it's Y," used as a
  reflex. Also clipped tailing negations tacked on: "no guessing," "no wasted
  motion." Once is fine; three times is a chatbot.
- **Fix:** State the point directly. Make the claim, drop the theatrical setup.
  One per piece at most.
- **Before:** This isn't about speed. It's about trust.
- **After:** This is about trust.
- **Sources:** blader (P9), aboudjem (§9), avoid-ai, anti-vibe, stop-slop.

---

### T3 — Formulaic challenges section

| Severity | Enforcement |
| --- | --- |
| medium | regex |

- **Tell:** A "challenges" block generated from nothing: "Despite [good thing],
  [vague problems]. Despite these challenges, [optimistic platitude]." Also the
  stock headings: "Challenges and Legacy," "Future Outlook," "The road ahead."
- **Fix:** State specific problems with dates and data, or cut the section.
- **Before:** Despite its prosperity, faces challenges typical of urban areas.
  Despite these, continues to thrive.
- **After:** Traffic worsened after 2015 when three IT parks opened. A stormwater
  project started in 2022.
- **Sources:** blader (P6), aboudjem (§6), avoid-ai (formulaic challenges).

---

### T4 — False concession structure

| Severity | Enforcement |
| --- | --- |
| medium | regex |

- **Tell:** "While X is impressive, Y remains a challenge," "Although X has made
  strides, Y is still an open question." Sounds balanced without weighing
  anything; both halves stay vague.
- **Fix:** Make the concession specific (name what's impressive, name the actual
  challenge) or pick a side and argue it.
- **Sources:** avoid-ai (false concession).

---

### T5 — Excessive / decorative structure

| Severity | Enforcement |
| --- | --- |
| medium | judge |

- **Tell:** Visible structure standing in for clear thinking: a heading for every
  paragraph, more than 3 headings in under 300 words, 8+ bullets in under 200
  words, numbered frameworks that don't clarify a real sequence, summaries before
  the reader has seen the argument. Plus stock section modules that appear because
  the model likes the shape: Overview, Key Features, Benefits, Why It Matters, In
  Summary, Conclusion, FAQ with invented questions.
- **Fix:** Keep the headings and lists the reader will actually use. Collapse the
  rest into prose. Use headers that tell the reader something specific.
- **Sources:** avoid-ai (excessive structure), anti-vibe (over-structured
  outlines + stock modules), blader (P14/P15 partial), aboudjem (§16).

---

### T6 — Inline-header vertical lists

| Severity | Enforcement |
| --- | --- |
| low | judge |

- **Tell:** Bullets where each item starts with a bold header that repeats
  itself: "**Performance:** Performance improved by…," "**Security:** Security
  has been strengthened…"
- **Fix:** Strip the bold header and write the point directly, or convert the
  list to a prose paragraph.
- **Before:** - **User Experience:** The user experience has been improved with a
  new interface.
- **After:** The update improves the interface, speeds up load times, and adds
  end-to-end encryption.
- **Sources:** aboudjem (§16), blader (P15), avoid-ai (inline-header lists).

---

### T7 — Bullet lists of bare noun phrases

| Severity | Enforcement |
| --- | --- |
| low | regex |

- **Tell:** 5+ consecutive bullets, each a short (≤6-word) adjective+noun phrase
  with no verb and nothing checkable: "Stable mining efficiency / Reliable pool
  connectivity / Optimized RandomX performance." The tell is the *symmetry* —
  every item the same shape and length.
- **Fix:** Convert to prose, or rewrite items as full claims ("Failed shares
  stayed under 1% across a 12-hour run"). Does **not** apply to genuine list
  content (changelog, parameter docs, ingredients) where bare phrases are correct.
- **Sources:** avoid-ai (bullet-NP lists).

---

### T8 — Numbered-list inflation

| Severity | Enforcement |
| --- | --- |
| low | judge |

- **Tell:** "Three key takeaways," "Five things to know," "Here are the top
  seven." Numbered lists are structurally safe, so the model defaults to them even
  when the content isn't that many discrete parallel items.
- **Fix:** Use a numbered list only when the content genuinely has that many
  parallel items. If you're padding to hit a number, the list shouldn't exist.
- **Sources:** avoid-ai (numbered-list inflation).

---

### T9 — Paragraph-reshuffle immunity

| Severity | Enforcement |
| --- | --- |
| medium | judge |

- **Tell:** The model writes parallel self-contained blocks instead of an
  unfolding argument. Test: can you swap paragraph 2 and paragraph 4 without
  breaking the piece? If yes, it's AI-shaped.
- **Fix:** Make paragraph N+1 depend on something concrete in paragraph N
  (references, callbacks, "this is why…"). If two paragraphs are interchangeable,
  merge or cut one. If they're all independent, the piece is missing a thesis.
- **Validity condition:** the reshuffle test only indicts *argumentative* prose.
  Reference docs, FAQs, API entries, changelogs, glossaries, and deliberately
  modular documents have independent, swappable blocks by design — that is correct
  structure, not an AI tell. Ask: is this piece building one unfolding argument,
  or is it a reference whose entries are meant to stand alone?
- **Sources:** blader (P38), avoid-ai (paragraph-reshuffle immunity).

---

### T10 — Treadmill effect (low information density)

| Severity | Enforcement |
| --- | --- |
| medium | judge |

- **Tell:** A 500-word section carrying 100 words of new information and 400 of
  restatement. Humans advance; AI circles. Inside-paragraph markers: "In other
  words," "Put simply," "Essentially," "That is to say."
- **Fix:** For each sentence, ask "what's actually new here?" Delete anything that
  only rephrases what came before. A paragraph that loses 40-60% of its words and
  reads better is the right outcome.
- **Sources:** blader (P43), avoid-ai (treadmill effect).

---

### T11 — Fragmented headers

| Severity | Enforcement |
| --- | --- |
| low | judge |

- **Tell:** A heading followed by a one-line paragraph that just restates the
  heading before the real content starts. ("## Performance" → "Speed matters.")
- **Fix:** Cut the warm-up line; let the real content follow the heading.
- **Sources:** aboudjem (§29).

---

### T12 — Diff-anchored writing

| Severity | Enforcement |
| --- | --- |
| low | judge |

- **Tell:** Documentation written as if narrating a change rather than describing
  the thing as it is: "This function was added to replace the previous approach…,"
  "We've now updated the API to also support streaming." (Fine for changelogs and
  migration guides — those are inherently version-scoped.)
- **Fix:** Describe the current state. "The API supports streaming." Unless the
  change itself is the point.
- **Sources:** aboudjem (§30), anti-vibe (diff-anchored writing).
