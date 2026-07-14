# Communication Artifacts (chat-interface leaks)

Tics from the chat interface that leak into published prose. The text was
generated as correspondence *to the user*, not as content, and got pasted without
removing the conversational framing. Most of these are credibility killers — fix
immediately.

---

### C1 — Chatbot artifacts

- **Tell:** Conversational tics from the chat UI: "I hope this helps," "Of
  course!," "Certainly!," "Feel free to reach out," "Let me know if you need
  anything else," "Here is a…," "Would you like me to…"
- **Fix:** Remove entirely. Start with the actual content.
- **Sources:** blader (P19), aboudjem (§20), avoid-ai (chatbot artifacts).

---

### C2 — Collaborative-framing leaks

- **Tell:** Instructional framing meant for the user leaking into published
  output: "In this article, we will explore," "Let me walk you through," "Here's
  what you need to know," instructions to the reader about what they should do.
  Distinct from C1 (identity disclosure) — this is the tutorial-script framing.
- **Fix:** Delete the meta-commentary; start with the content.
- **Before:** In this article, we will explore the characteristics that make this
  framework worth using.
- **After:** This framework solves three problems React Router doesn't.
- **Canonical / precedence:** C2 is the **canonical** entry for *first-person
  tutorial narration* ("we will explore," "let me walk you through"). Bare
  announcement openers ("Let's dive in," "Here's what you need to know") overlap
  H7 (signposting), which is **canonical for those**; the "Let's + verb" form is
  its H8 subtype. If a line matches both, apply the canonical fix — H7 for an
  announcement opener, C2 for tutorial narration.
- **Sources:** blader (P32), aboudjem (§20), avoid-ai (chatbot meta-narration).

---

### C3 — Sycophantic tone

- **Tell:** Conversational rewards validating the reader: "Great question!,"
  "Excellent point!," "You're absolutely right!," "That's a really insightful
  observation."
- **Fix:** Remove. Distinct from C1: sycophancy specifically flatters the
  questioner rather than performing helpfulness.
- **Sources:** blader (P21), aboudjem (§22), avoid-ai (sycophantic tone),
  stop-slop.

---

### C4 — Acknowledgment loops

- **Tell:** Restating the prompt before answering: "You're asking about," "To
  answer your question," "The question of whether…," "That's a great question. The
  …" Also opening a section by summarizing the previous one.
- **Fix:** Just answer. The reader knows what they asked.
- **Sources:** avoid-ai (acknowledgment loops).

---

### C5 — Cutoff disclaimers

- **Tell:** Model limitations leaking into prose: "As of my last update," "Up to
  my last training update," "While specific details are limited based on available
  information," "I don't have access to real-time data."
- **Fix:** Find the information or remove the hedge. Never publish a sentence that
  admits the writer didn't look something up. (Distinct from S8 speculative
  gap-filling, which *hides* the gap; this one admits it.)
- **Sources:** blader (P20), aboudjem (§21 first half), avoid-ai (cutoff
  disclaimers).

---

### C6 — Reasoning-chain artifacts

- **Tell:** Chain-of-thought scaffolding leaking into published prose: "Let me
  think step by step," "Breaking this down," "To approach this systematically,"
  "Step 1:," "First, let's consider," "Working through this logically." Plus
  numbered reasoning steps that read like internal monologue.
- **Fix:** The reader doesn't need the scaffolding. State the conclusion, then the
  evidence.
- **Sources:** avoid-ai (reasoning-chain artifacts).

---

### C7 — Infomercial engagement hooks

- **Tell:** Punchy fragment-hooks teeing up a reveal: "The catch?," "The
  kicker?," "Here's the thing.," "But here's the kicker:," "The best part?,"
  "Plot twist:," "Sound familiar?" Fake momentum and manufactured suspense around
  ordinary information.
- **Fix:** Delete the hook; state the thing. "The catch? It only works on
  weekends." → "It only works on weekends." If you want a rhythm break, use a
  short declarative fragment, not a question.
- **Sources:** blader (P41), avoid-ai (infomercial engagement hooks).

---

### C8 — Rhetorical-question openers

- **Tell:** Rhetorical questions used to stall before the point, dropped as
  section transitions: "But what does this mean for developers?," "So why should
  you care?," "What's next?" Also FAQ-style question headings: "What makes X
  unique?," "Why is Y important?"
- **Fix:** If you know the answer, say it. Rhetorical questions are earned by
  strong setup, not used as transitions.
- **Sources:** avoid-ai (rhetorical-question openers), blader (P27 question
  titles).

---

### C9 — Emotional flatline

- **Tell:** Claiming an emotion as a structural crutch without conveying it:
  "What surprised me most," "I was fascinated to discover," "What struck me was,"
  "The most interesting part," and the bare header form "Interesting thing here:."
  Tell-don't-show, and massively overused as list intros. Also "hit differently"
  / "hits different" as a shortcut to sound relatable.
- **Fix:** If you claim an emotion, the writing around it should earn it.
  Otherwise cut the claim and present the thing directly. (Also a sign of lazy
  human writing — flag it either way.)
- **Sources:** avoid-ai (emotional flatline).

---

### C10 — Parenthetical hedging

- **Tell:** Parenthetical asides that sound nuanced without committing: "(and,
  increasingly, Z)," "(or, more precisely, Y)," "(and perhaps more importantly,
  W)."
- **Fix:** If the aside matters, give it its own sentence. If it doesn't, cut it.
- **Sources:** avoid-ai (parenthetical hedging).

---

### C11 — Register / style shift (mixed authorship)

This is the single **canonical** entry for register shift. The false-positive
guardrail in `rhythm-stylometric.md` ("Mixed casual/formal register") points here
and does not re-flag it; apply the validity condition below before flagging.

- **Tell:** A sudden, *unexplained* change in voice, register, or error profile
  mid-document — one paragraph of perfect formal English next to casual text with
  errors; graduate-thesis prose dropped into casual notes. Such a discontinuity
  *can* mark a seam where AI-generated text was pasted into human writing.
- **Fix:** Only when the validity condition holds, rewrite the out-of-place
  section so its register is continuous with the author's natural voice. If the
  shift is explained (a quoted passage, a deliberate aside, a code comment, a
  section aimed at a different audience), leave it alone.
- **Validity condition (do not skip this):**
  > A register shift is a tell ONLY when it is an *unexplained discontinuity
  > corroborated by other signals* in the same passage — e.g. the out-of-place
  > section also carries rule-of-three, AI vocabulary, or low burstiness. Ordinary
  > mixed register is NOT a tell: a technical field, a young writer, a
  > second-language writer, or neurodivergent prose habits all produce legitimate
  > register mixing. Never flag mixed register on its own — require the
  > corroborating cluster.
- **Advisory, not mandatory (quality-first):** this is a weak provenance signal,
  not a prose-quality defect. Flag the seam for review; never mandate a rewrite on
  register alone.
- **Sources:** blader (P36); validity condition added 2026-07-13, cross-referencing
  the `rhythm-stylometric.md` false-positive guardrail.
