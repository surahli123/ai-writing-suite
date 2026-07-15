# Over-stepping / Presumption (反代入式越位感)

When the writer thinks *for* the reader instead of *to* them: presuming a belief,
painting a thought into the reader's head, or asking-then-answering its own
rhetorical question — then correcting from above. The text stops conveying
content and starts *performing insight*. This is a **stance** tell, not a
vocabulary tell: every word can be clean while the line over-steps, so a
mechanical detector is blind to it. It is judge-only and advisory.

The load-bearing rule is the **validity condition** below: a presumption is
over-stepping ONLY when the prior it corrects is a manufactured strawman. When the
prior is a belief the reader genuinely holds, the same framing is a *legitimate*
correction — removing it loses information. Apply the validity condition before
flagging anything here.

---

### O1 — Presumed cognition (manufactured prior)

| Severity | Enforcement |
| --- | --- |
| medium | advisory |

- **Tell:** Asserting what the reader thinks, then correcting it — where the
  presumed belief is invented, not one the reader actually holds: "You probably
  assume more data always means a better model, but…," "很多人以为 X，其实 Y." The
  reader never agreed to the premise; the line installs a strawman to knock down.
- **Fix:** State the claim directly. The point survives without presuming the
  reader was wrong: drop "you assume X, but" and keep Y.
- **Before:** You probably assume more data always means a better model, but data
  quality matters more than quantity.
- **After:** Data quality matters more than quantity for model performance.
- **Sources:** anti-vibe (反代入式越位感, bilingual).

---

### O2 — Presumed-misconception strawman

| Severity | Enforcement |
| --- | --- |
| medium | advisory |

- **Tell:** Framing a setup as a widely-held misconception that the writer alone
  sees through: "Most people get this wrong…," "Contrary to popular belief…,"
  "大家都以为 X 是错的." The "popular belief" is asserted, never evidenced, and is
  there to make the correction feel like a revelation.
- **Fix:** If a real, common belief is being corrected, name it specifically and
  keep the contrast (it carries information). If the "misconception" is
  manufactured, cut the setup and make the claim plainly.
- **Sources:** anti-vibe (反代入式越位感, bilingual), avoid-ai.

---

### O3 — Presumed mental image

| Severity | Enforcement |
| --- | --- |
| medium | advisory |

- **Tell:** Painting a thought into the reader's head, then correcting it: "When
  you hear X, you picture Y. In reality…," "你脑子里浮现的是 Y，其实是 Z." The
  projected image is the writer's, attributed to the reader.
- **Fix:** Keep the definition or claim; drop the projected image. The content
  was never in the image, only in the correction.
- **Before:** When you hear "caching," you picture some magic speed boost. In
  reality, it's just a smaller, faster store of recent results.
- **After:** A cache is just a smaller, faster store of recent results.
- **Sources:** anti-vibe (反代入式越位感, bilingual).

---

### O4 — Self-Q&A as judge

| Severity | Enforcement |
| --- | --- |
| medium | advisory |

- **Tell:** Asking a rhetorical question on the reader's behalf and immediately
  answering it, then ruling on the reader's expected reaction: "Can you set this
  up yourself? Yes — and it's simpler than you might think," "要不要自己写个爬虫？
  要，而且比你想象的简单." The "simpler than you think" clause presumes the reader's
  doubt and overrules it from above.
- **Fix:** Drop the question-and-answer theater and the "than you think" ruling.
  State the answer as a plain claim.
- **Before:** Can you set this up yourself? Yes — and it's simpler than you might
  think.
- **After:** You can set this up yourself; it's fairly simple.
- **Sources:** anti-vibe (反代入式越位感, bilingual), stop-slop.

---

## The four self-test questions

Run these on any candidate line before flagging it:

1. Is the writer thinking **for** the reader (asserting what they believe,
   picture, or doubt)?
2. Is this a misconception the reader **actually** holds? *(the validity
   condition — the decisive question)*
3. Is the line conveying content, or **performing insight**?
4. Does the point still hold after deleting "you think / 你以为 / 很多人以为"?

If 1 and 3 are yes and 4 still holds (the point stands without the presumption),
the frame is over-stepping → remove it. If 2 is yes (the prior is a real,
widespread belief), the contrast is legitimate → keep it.

## The validity condition (do not skip this)

> A presumption is over-stepping ONLY when the prior X is a manufactured
> strawman. When X is a genuinely common belief the reader holds, the contrast is
> legitimate — removing it loses information.

Worked contrast:

- "You probably assume **more data = better model**, but…" → X is a manufactured
  framing the reader need not hold → **over-stepping** → remove.
- "Love **isn't** a feeling, it **is** a behavior" / 爱**不是**感觉，**而是**行为 →
  X ("love = a feeling") is a real, widespread prior → **legitimate flip** →
  keep; deleting "isn't a feeling" loses real information.

Boundary cases (a *semi-real* lay belief — e.g. "推荐系统就是猜你喜欢什么") are
**ambiguous**: whether the correction is legitimate depends on the reader's actual
prior, which text alone cannot decide. Leave ambiguous cases alone; flag only the
**clearly manufactured** sub-types above.

## 少写 / 多写 (write-less / write-more) substitution

The fix is almost always **write less**, not rephrase:

- **少写 (write less) — the default:** delete the presumption layer and keep the
  payload. "你以为 X，其实 Y" → "Y." The content was always in Y; the X-shell only
  staged a reaction. Most over-stepping lines shrink to a plain claim.
- **多写 (write more) — only when the prior is real:** if X is a belief the reader
  genuinely holds, do **not** delete the contrast. Instead, make X *specific* —
  name the real belief and why it falls short — so the flip earns its keep. Adding
  evidence converts a presumed contrast into a documented one.

The discriminator between the two is the validity condition: manufactured prior →
少写; real prior → 多写 (or leave the legitimate contrast intact).

**Leave the payload crystal-clear.** After 少写 deletes the presumption layer, the
surviving claim must still read as a complete, self-standing statement — not a stub
whose pronouns lost the antecedent the deleted frame supplied ("It reduces them" →
name the subject: "Merging reduces outages"). The eval checks this as `payoff_clear`,
paired with `overstepping_removed` (see `evals/fixtures/rubric.md`).

## Scope

- Targets only the **clearly manufactured** sub-types above (O1–O4).
- **Excludes** intent-dependent cases where whether the line over-steps cannot be
  decided from text alone — those need to know the reader's real priors, which is
  an audience question, not a prose-pattern question.
- Detector-blind by design: no vocabulary or density signal. This pattern is
  applied by the LLM judge (`overstepping_removed` in
  `evals/fixtures/rubric.md`), never by the mechanical detector, and it never
  gates CI.
