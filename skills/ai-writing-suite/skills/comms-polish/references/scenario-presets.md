# Scenario Presets

Different writing scenarios carry different hard constraints — length, structure,
whether emoji belong, the scale of reader attention. This file pins down those
constraints for the four genres comms-polish targets in v1: **tweet / X, LinkedIn,
README, memo**.

> Why presets exist: the AI-tell catalog under `_shared/patterns/` (suite-root-relative;
> resolved per the comms-polish "Locating shared assets" protocol) says
> *what* reads as machine-written. A preset says *which of those tells matter most
> here* and *what to leave alone*, so a README isn't edited like a tweet. Presets
> shape **form**; a voice profile (when one exists) shapes **voice**. They stack
> when they don't conflict; when they do, voice loses to a hard form constraint
> (a tweet's 280-char limit beats a profile's love of long sentences).

Adapted from `weijt606/anti-vibe-writing` (`scenario-presets.md`, MIT). The
original ships five Chinese-platform scenarios; this is the English subset mapped
to the v1 genres. Bilingual presets are a v2 item (deferred).

## How to use a preset

1. Detect the genre from the request (or ask if ambiguous).
2. Load the matching preset below.
3. **Weight** the named catalog categories harder during the scan — those are the
   tells that hurt most in this genre.
4. Respect the **leave alone** list — these are not tells *here*, even if the
   catalog flags them in general.
5. Hold the target tone/length as the rewrite goal.

Each preset names catalog categories by their file id (e.g. `structural-tells`,
`punctuation-formatting`) so the weighting stays traceable to the single source of
truth instead of re-listing patterns inline.

---

## 1. Tweet / X

**Form constraints:**
- One tweet ≤ 280 characters. A thread: every tweet stands alone; tweet #1 must
  read on its own.
- No heading levels. No markdown lists (the platform won't render them).
- Links and @mentions used sparingly.

**Weight these tells harder** (from the catalog):
- `hedging-filler` — "let's", "today I want to share", "first, some context"
  openers. The first line must hook; drop the runway.
- `structural-tells` — rule-of-three and "not X but Y" theatrics read as
  performance, not a person.
- `significance-attribution` — "many / some / a lot": replace with the actual
  number **only when the source provides it**; otherwise flag the missing number
  and leave the vague quantifier — never invent a figure (see *Cross-scenario
  invariants*: don't invent facts, numbers are immutable).

**Target tone/length:** punchy, one idea per tweet, leave a reason to read the
next line. Inversion, fragments, and an incomplete sentence are fine here.

**Leave alone:**
- Sentence fragments and missing connectives — they're native to the genre, not a
  tell.
- Casual punctuation and lowercase, *only* if the author's voice already does
  this. Never touch numbers, names, or links.

**Endings that work:** a sharp question, a concrete next step, one quotable line,
or just stop on the fact. Never "more in the next tweet" — the next tweet starts
itself.

---

## 2. LinkedIn

**Form constraints:**
- Short-to-medium. The first 1–2 lines show before the "see more" fold — they
  carry the whole post.
- Line breaks between short paragraphs; long blocks die on a phone screen.
- Hashtags by platform habit (a few, at the end), not stuffed inline.

**Weight these tells harder:**
- `communication-artifacts` — engagement hooks ("Agree? 👇"), sycophancy, and
  the LinkedIn-broetry "one sentence per line for fake gravity" pattern.
- `punctuation-formatting` — emoji-as-bullets, decorative section markers, hashtag
  stuffing.
- `significance-attribution` — promotional adjectives and self-congratulation
  ("thrilled", "humbled", "game-changer").

**Target tone/length:** professional but human; a point of view, not balanced
neutrality. Specific story or claim up front, payoff the reader can take away.

**Leave alone:**
- A genuine first-person opinion or a real anecdote — these are the point.
- A single emoji *if* it's the author's habit and earns its place.

**Endings that work:** a concrete takeaway, a real question (not bait), or a
specific next step. Drop "What do you think? Let me know in the comments."

---

## 3. README

**Form constraints:**
- Headings, lists, code blocks, and tables are allowed and often required.
- Code, commands, file paths, flags, and version numbers are sacred — never
  reworded.
- Length follows the project; a quickstart is short, a reference is long.

**Weight these tells harder:**
- `structural-tells` — stock sections (Overview, Key Features, Conclusion) that
  exist to fill a template; over-structure; inline-header lists that should be
  prose.
- `significance-attribution` — "powerful", "seamless", "robust", "enterprise-grade"
  promotional adjectives; significance inflation about what the tool "enables".
- `lexical-tells` — "leverage", "utilize", "facilitate" where a plain verb works.

**Target tone/length:** show, don't sell. Lead with what it does and how to run
it. Each heading must carry information, not decorate.

**Leave alone:**
- Real lists, tables, and code blocks — structure is *correct* here, not a tell.
- Necessary headings — a README *should* be navigable.
- Technical terms — define on first use only if the reader isn't assumed to be a
  peer.

**Endings that work:** stop after the last real instruction. No "Conclusion"
section restating the intro.

---

## 4. Memo / Internal Doc

**Form constraints:**
- Tight structure; layered headings are fine.
- Long sentences and long paragraphs are allowed when they stay precise.
- Data and citations must be checkable (links, doc refs, ticket numbers).
- No emoji. Jargon allowed, defined on first use unless the audience is named as
  expert.

**Weight these tells harder:**
- `hedging-filler` — stacked hedging that hides the actual uncertainty ("perhaps",
  "to some extent", "it could be argued"); signposting; non-conclusions like
  "it depends" or "consider all factors".
- `significance-attribution` — vague attribution ("studies show", "experts
  agree") with no source; consultant-speak.
- `structural-tells` — rule-of-three; data dropped into a table with no reading.

**Target tone/length:** state the conclusion. Quantify uncertainty instead of
hiding it. Use explicit branches ("if X, then Y; else Z"). Write the tradeoff:
what was chosen, what was dropped, and why.

**Leave alone:**
- A real caveat that carries genuine uncertainty — keep it, just make it specific.
- Long precise sentences — length isn't a tell when every word is load-bearing.
- Legal, security, financial, or safety warnings — never polished away.

**Endings that work:** a clear recommendation or decision, not a balanced summary
that refuses to judge.

---

## Cross-scenario invariants

No matter the genre, these never change (these are the bottom line, not preset
preferences):

- Don't invent facts.
- Don't strengthen the author's position for them.
- Keep caveats that carry real uncertainty.
- Numbers, names, and quotes are immutable unless the user asks.
- Drop empty buzzwords ("leverage", "synergy", "circle back", "move the needle").

Scenarios change which tells you weight. The anti-AI floor stays fixed.
