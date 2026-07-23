# KB Smoke Test — one end-to-end ingestion + retrieval chain

> **Why this file exists (design decision D12).** The whole product promise is
> "the company just drops in a Confluence page — they add data, not build a
> retrieval engine." That promise is hollow unless we prove ONE complete chain
> works end-to-end on the generic KB: a raw page comes in → it gets indexed →
> a natural-language query resolves to the correct entry and passage.
>
> This doc establishes and documents that chain as a **repeatable test**. The
> Layer 3 eval will automate it (query in → assert the agent retrieves the
> expected entry + passage). For now it is the manual, reproducible proof.

---

## The chain, in three steps

```
[1] INGESTION                [2] INDEX UPDATE              [3] RETRIEVAL
raw markdown page    ──▶      add 1 row to INDEX.md   ──▶  NL query → INDEX scan
("Confluence-style")         (file + summary + keywords)   → open entry → quote passage
```

No embeddings, no vectors, no MCP. Every step is a file read/write an agent (or a
human) can do on any surface (D5).

---

## Step 1 — Sample incoming page (the "Confluence-style" drop-in)

This is what a company contributor would paste in — a normal markdown page. For
the generic KB we already shipped five such entries; `clarity.md` is the one this
test traces. Its load-bearing passage is:

> **One idea per sentence.** If you find an "and" joining two full claims, make
> two sentences.

(That passage is the expected retrieval target in Step 3.)

## Step 2 — Ingestion = add one row to `INDEX.md`

Indexing a page is a single edit: append a row to the **Entries** table in
`INDEX.md` with three fields.

- **Entry file:** `clarity.md`
- **Summary (one line):** Say one idea per sentence in plain, concrete words; cut filler.
- **Keywords / aliases:** clarity, clear, concise, plain language, wordy, verbose,
  filler, jargon, simplify, hard to read, confusing, cut words, concrete, vague

That row IS the ingestion. No build step, no re-index job. (This is exactly what
a company fork does with its Confluence page — see `README.md`.)

## Step 3 — Retrieval = scan INDEX, open entry, quote passage

Follow the retrieval protocol at the top of `INDEX.md`.

Two kinds of match can fire, and the protocol uses both: an **exact alias match**
(a query term appears verbatim in an entry's Keywords/aliases column) and a
**semantic Summary match** (the query's intent lines up with an entry's Summary
even when no keyword token overlaps). They are different retrieval signals — the
deterministic replica scores overlap across their union, then uses Summary overlap
to break total-overlap ties. Case 1 below is carried by Summary terms, not by an
exact alias.

---

## TEST CASE (run this to verify the chain)

**Query (natural language):**
> "My sentences are too long and try to say too much at once — how do I fix that?"

**Expected entry retrieved:** `clarity.md` (must be among the results)
**Expected files:** `clarity.md`, `revision.md`

- *Why:* canonical token scoring produces a genuine two-way tie. The query token
  `say` overlaps `clarity.md`'s Summary, giving it `(total, summary) = (1, 1)`.
  The query token `fix` overlaps `revision.md`'s Summary ("fix it in editing
  passes"), also giving it `(1, 1)`. The INDEX protocol's tie clause therefore
  opens both `clarity.md` and `revision.md`; `clarity.md` remains required because
  it contains the within-sentence guidance and expected passage. The earlier
  narrative claim that "No other entry carries within-sentence-overload signal"
  was an overlooked token collision in the original hand computation —
  `revision.md` and this smoke case entered the KB in the same commit.

**Expected passage quoted:**
> **One idea per sentence.** If you find an "and" joining two full claims, make
> two sentences.

(plus, acceptable to also surface the Before/After in `clarity.md`:
"It is worth noting that... → The team cut three slow queries.")

**Pass condition:** the agent returns exactly the two-entry tie
`clarity.md` + `revision.md`, opens both, AND quotes the "One idea per sentence"
Move (or the clarity Before/After). A missing or additional entry is a retrieval
failure even if the prose answer sounds reasonable.

---

## A second case (negative / disambiguation check)

**Query:**
> "Who am I even writing this for? It feels like it's aimed at no one."

**Expected entry:** `audience.md`
**Expected files:** `audience.md`
**Expected passage:**
> State the reader and their job before drafting. "An on-call engineer who needs
> to decide whether to roll back." That sentence fixes tone, length, and jargon level.

**Why it must NOT return `tone.md`:** the word "feels" and "aimed" can lure a
match to tone, but the intent — *no identified reader* — maps to `audience.md`.
This case exists to confirm the index discriminates between near-neighbors.

---

## A third case (genuine near-neighbor — both entries score > 0)

Case 2 above discriminates on a single token ("who"), so the tie-break is never
truly exercised (review finding m1). This case fixes that: the query hits BOTH
`audience.md` and `tone.md` on keywords, and `audience.md` must win on total overlap.

**Query:**
> "Who is the reader for this? It sounds too technical and a bit corporate."

**Expected entry:** `audience.md`
**Expected files:** `audience.md`
**Expected passage:**
> State the reader and their job before drafting. "An on-call engineer who needs
> to decide whether to roll back." That sentence fixes tone, length, and jargon level.

**Why this is the real disambiguation test:** `tone.md` genuinely scores here —
"sounds" and "corporate" are tone keywords (overlap 2) — but `audience.md` wins on
total term overlap ("who" + "reader" + "technical" = 3). Unlike Case 2 there is a
competing signal to beat, so a PASS proves the keyword/intent tie-break actually works.

---

## A fourth case (comms-qa question-path — "how do I open an exec update?")

The three cases above are problem-statement queries ("my sentences are too long").
The `comms-qa` sub-skill answers *question-shaped* traffic instead ("how should I
open X?"). This case represents that path: a real question a user would ask the KB.

**Query:**
> "How should I open a status update for an exec — where do I put the main point?"

**Expected entry:** `structure.md`
**Expected files:** `structure.md`
**Expected passage:**
> BLUF — bottom line up front. Open with the decision, result, or ask.

**Why `structure.md`:** the question is about *ordering* — where the main point
goes — which is exactly `structure.md`'s domain. Its Keywords match "where" (from
"where to start") and its Summary matches "point" (from "Lead with the point").
`audience.md` scores only on "exec" (one keyword, "exec vs engineer") and loses on
total overlap, so the question-path query still resolves to the ordering entry.

---

## A fifth case (comms-qa question-path — "who is this for?")

A second question-shaped `comms-qa` case: the user asks *who the reader is*, the
question `audience.md` exists to answer.

**Query:**
> "Who is the target reader I should be writing this for — a stakeholder or an engineer?"

**Expected entry:** `audience.md`
**Expected files:** `audience.md`
**Expected passage:**
> State the reader and their job before drafting. "An on-call engineer who needs
> to decide whether to roll back." That sentence fixes tone, length, and jargon level.

**Why `audience.md`:** the question's content terms — "target," "reader,"
"writing," "stakeholder," "engineer" — all sit in `audience.md`'s Keywords/aliases
column ("target reader," "stakeholder," "exec vs engineer"), so it dominates total
overlap. No other entry carries reader/stakeholder vocabulary, so there is no
near-neighbor to beat here — this case confirms a plain who-is-this-for question
resolves cleanly on the question path.

## How Layer 3 will automate this

The eval harness reads each TEST CASE block, sends the **Query** to the agent
under the retrieval protocol, and asserts: (a) Case 1 returns its exact documented
tie set while Cases 2–5 return only **Expected entry**, and (b) the quoted text
contains the **Expected passage**.
Calibrate by adding harder near-neighbor queries until the baseline misses
~30-40% (per the project eval-calibration rule), then tighten the index keywords
to recover recall. Until Layer 3, run all five cases by hand after any KB edit.
