# Rhythm & Stylometric Tells

Whole-document patterns in how the text flows, not individual words or phrases.
Structure is the #1 detection signal: classifiers weight rhythm and uniformity
above vocabulary. Fix every flagged word but leave the rhythm metronomic and the
text still reads as AI.

Important counterweight: over-applying these rules pushes human writing *toward*
the AI profile. Natural disfluency, idiosyncratic word choice, and uneven pacing
are what keep text out of the "AI-generated" bucket. Don't sand away all
personality chasing clean prose.

---

### R1 — Sentence-length uniformity (low burstiness)

- **Tell:** Detectors measure "burstiness" — sentence-length variance. Human
  writing has high burstiness; AI has low. If most sentences run 15-25 words with
  no short punches and no long flowing thoughts, it reads robotic.
- **Fix:** Mix short (3-8 words), medium (12-20), and long (25-40) in every
  paragraph. Never 3+ consecutive sentences of similar length. Fragments work.
  Questions break monotony. Let one sentence run long when the thought needs room.
- **Sources:** blader (P30 + burstiness principle), avoid-ai (rhythm and
  uniformity), stop-slop (vary rhythm), aboudjem (variety in sentence length).

---

### R2 — Paragraph-length uniformity

- **Tell:** Every paragraph 3-5 sentences and roughly the same size.
- **Fix:** Vary deliberately. Some paragraphs one sentence. Some longer.
- **Sources:** avoid-ai (paragraph length uniformity), anti-vibe.

---

### R3 — Low vocabulary diversity (low TTR)

- **Tell:** Type-token ratio (distinct word types / total tokens) is a classical
  stylometric signal readable by eye. Human prose at 200+ words usually lands
  ~0.50-0.65; AI trends flatter, sometimes under 0.40 when locked on a small
  vocabulary loop.
- **Fix:** Don't thesaurus the text. Broaden the *what*: name specific things,
  cite specific cases, replace a re-used abstract noun with the concrete instance.
  **Calibration:** low TTR is not proof — narrow topics, technical reference, and
  second-language writing legitimately compress vocabulary.
- **Sources:** avoid-ai (vocabulary diversity / stylometric).

---

### R4 — Low perplexity (predictable word choice)

- **Tell:** Detectors also measure "perplexity" — how predictable each word is. AI
  text is low-perplexity (it picks the most statistically likely next word); human
  text is higher (more surprising choices).
- **Fix:** Choose the second or third word that comes to mind, not the first. Use
  audience-appropriate jargon or slang. Make unexpected analogies from real
  experience. (Don't force it — surprise that reads as random is its own tell.)
- **Sources:** blader (perplexity principle).

---

### R5 — Missing first-person / no stance

- **Tell:** Relentlessly neutral where the genre expects a voice. No "I think," no
  stated preference, no reaction. The absence is itself a tell in opinion / blog /
  founder writing.
- **Fix:** Where appropriate, have opinions and state them. **Carve-out:** for
  encyclopedic, technical, legal, or reference text, neutral and plain *is* the
  correct human voice — don't inject opinions there.
- **Sources:** avoid-ai (missing first-person), aboudjem (personality and soul),
  stop-slop (put the reader in the room).

---

## What NOT to flag (false-positive guardrails)

A clean human writer can hit many patterns above with no AI involvement. Before
rewriting, sanity-check you aren't gutting legitimate prose. None of these are
reliable AI indicators on their own:

- Perfect grammar and consistent style. Polish ≠ AI; many writers are edited.
- Mixed casual/formal register. Often signals a technical field, a young writer,
  or neurodivergent prose habits.
- "Bland" or "robotic" prose. AI has *specific* tells; generic dryness is just
  dry writing.
- Formal/academic vocabulary. AI overuses *specific* fancy words, not all of them.
- A lone em dash, lone curly quotes, a single "however," letter-style salutations.
- Unsourced claims. Most of the web is unsourced.

**Look for clusters, not isolated tells.** A single em dash is nothing; em dashes
plus rule-of-three plus "vibrant tapestry" plus a "Conclusion" section is a
confession.

> Detector false-positive rates exceed 60% on non-native English writers (Liang
> et al., Stanford, *Patterns* 2023) and 70%+ on open-source detectors (Jabarian
> & Imas, BFI 2025). These are signals, not proof — never the sole basis for a
> consequential decision.
>
> Sources for this section: aboudjem (detection guidance), avoid-ai (what this
> skill is and isn't).
