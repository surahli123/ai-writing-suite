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

---

## TEST CASE (run this to verify the chain)

**Query (natural language):**
> "My sentences are too long and try to say too much at once — how do I fix that?"

**Expected entry retrieved:** `clarity.md`

- *Why:* the query terms "too long," "say too much at once," and "fix" overlap
  the `clarity.md` keywords (`wordy`, `verbose`, `one idea`, `cut words`) and its
  Summary ("Say one idea per sentence... cut filler"). No other entry's keyword
  set matches "one sentence saying too much" — `structure.md` is about
  document/paragraph order, not within-sentence overload.

**Expected passage quoted:**
> **One idea per sentence.** If you find an "and" joining two full claims, make
> two sentences.

(plus, acceptable to also surface the Before/After in `clarity.md`:
"It is worth noting that... → The team cut three slow queries.")

**Pass condition:** the agent returns `clarity.md` as the entry AND quotes the
"One idea per sentence" Move (or the clarity Before/After). Returning a different
entry, or inventing advice not in the file, is a FAIL.

---

## A second case (negative / disambiguation check)

**Query:**
> "Who am I even writing this for? It feels like it's aimed at no one."

**Expected entry:** `audience.md`
**Expected passage:**
> State the reader and their job before drafting. "An on-call engineer who needs
> to decide whether to roll back." That sentence fixes tone, length, and jargon level.

**Why it must NOT return `tone.md`:** the word "feels" and "aimed" can lure a
match to tone, but the intent — *no identified reader* — maps to `audience.md`.
This case exists to confirm the index discriminates between near-neighbors.

---

## How Layer 3 will automate this

The eval harness reads each TEST CASE block, sends the **Query** to the agent
under the retrieval protocol, and asserts: (a) the returned entry filename equals
**Expected entry**, and (b) the quoted text contains the **Expected passage**.
Calibrate by adding harder near-neighbor queries until the baseline misses
~30-40% (per the project eval-calibration rule), then tighten the index keywords
to recover recall. Until Layer 3, run these two cases by hand after any KB edit.
