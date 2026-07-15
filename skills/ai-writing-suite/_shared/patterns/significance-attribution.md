# Significance & Attribution Tells

The model inflates importance and fakes sourcing. These are credibility killers:
they make confident claims the text can't back up, so they are the highest
priority to fix in any professional or factual document.

---

### S1 — Significance inflation

| Severity | Enforcement |
| --- | --- |
| high | regex |

- **Tell:** Puffing routine facts into history-making ones: "marking a pivotal
  moment in the evolution of…," "a watershed moment for the industry," "stands as
  a testament to," "underscores the importance of," "represents a shift."
- **Fix:** State what happened and let the reader judge significance. If the
  sentence still works after deleting the inflation clause, delete it.
- **Before:** established in 1989, marking a pivotal moment in the evolution of
  regional statistics.
- **After:** established in 1989 to collect regional statistics.
- **Validity condition:** flag only *unearned* significance — puffery the text
  can't back. If the claim is evidence-backed (the sentence, or one near it, shows
  the concrete consequence that makes the moment pivotal), it is analysis, not
  inflation — keep it. Ask: does the genre and evidence justify the significance
  claim, or is the claim doing the work the evidence should?
- **Sources:** blader (P1), aboudjem (§1), avoid-ai, anti-vibe.

---

### S2 — Symbolic gloss / meaning-telling

| Severity | Enforcement |
| --- | --- |
| medium | judge |

- **Tell:** Narrating the *meaning* of a mundane fact instead of trusting the
  fact: "this represents a broader shift," "the decision symbolizes a commitment
  to excellence," "speaks to a larger trend." Distinct from S1's "pivotal /
  testament" framing — this is the interpretive layer telling readers what to
  feel.
- **Fix:** Cut the meaning sentence. State the fact; if the significance is real,
  show it with a concrete consequence.
- **Before:** The closed factory represents the decline of American manufacturing
  and speaks to broader anxieties about post-industrial identity.
- **After:** The factory closed in 2009. Three hundred jobs. The town's high
  school dropped football the next year.
- **Validity condition:** flag only interpretation *substituting* for the fact.
  When interpretation IS the document's job (an essay, an analysis, a review whose
  reader wants the "what it means"), the meaning layer is the deliverable — keep
  it and make it specific. Ask: is meaning-making this document's purpose, or is
  it glossing a fact the reader could judge alone?
- **Sources:** blader (P40), avoid-ai (folded into superficial -ing), aboudjem.

---

### S3 — Novelty inflation

| Severity | Enforcement |
| --- | --- |
| high | regex |

- **Tell:** Treating an established concept as if the subject invented it: "he
  coined the term," "a failure mode nobody talks about," "the insight everyone's
  missing." Factually risky (the idea often already has a Wikipedia page) and
  reads as promotional.
- **Fix:** Describe what the person *did with* the concept, not that they
  discovered it. When unsure whether something is novel, assume it isn't.
- **Sources:** avoid-ai (novelty inflation).

---

### S4 — Vague attribution / weasel words

| Severity | Enforcement |
| --- | --- |
| high | regex |

- **Tell:** Phantom authorities give opinions weight: "Experts believe,"
  "Studies show," "Research suggests," "Industry leaders agree," "several
  sources" — with no named source.
- **Fix:** Name the specific expert, paper, or report, or drop the claim. One
  sourced reference beats four vague ones.
- **Before:** Experts believe it plays a crucial role in the regional ecosystem.
- **After:** A 2019 Chinese Academy of Sciences survey found 12 endemic fish
  species.
- **Sources:** blader (P5), aboudjem (§5), avoid-ai, anti-vibe.

---

### S5 — Notability name-dropping / source-listing as content

| Severity | Enforcement |
| --- | --- |
| high | judge |

- **Tell:** Proving importance by listing coverage instead of saying what the
  coverage reported: "cited in NYT, BBC, FT, and The Hindu," "maintains an active
  social media presence."
- **Fix:** Pick one source and say what it reported. Or cut the list.
- **Before:** Her insights have been featured in Wired, Refinery29, and other
  prominent outlets.
- **After:** Wired profiled her 2024 research on algorithmic bias in hiring
  software.
- **Sources:** blader (P2 + P37), aboudjem (§2), avoid-ai.

---

### S6 — Promotional / advertisement language

| Severity | Enforcement |
| --- | --- |
| medium | judge |

- **Tell:** Tourism-brochure prose: "nestled within the breathtaking foothills,"
  "a vibrant hub of innovation," "a thriving ecosystem," "rich cultural
  heritage," "must-visit," "world-class."
- **Fix:** Plain description. "is a town in the Gonder region," "has 12
  startups." If you wouldn't say it in conversation, cut it.
- **Sources:** blader (P4), aboudjem (§4), avoid-ai, anti-vibe (consultant tone).

---

### S7 — Superficial -ing analyses

| Severity | Enforcement |
| --- | --- |
| medium | judge |

- **Tell:** Present-participle phrases tacked on to fake depth: "…symbolizing the
  region's commitment to progress, reflecting decades of investment, and
  showcasing a new era." The written equivalent of nodding while saying nothing.
- **Fix:** Delete the -ing clause. If it carried real information, promote it to
  its own sentence with a specific source.
- **Sources:** blader (P3), aboudjem (§3), avoid-ai.

---

### S8 — Speculative gap-filling

| Severity | Enforcement |
| --- | --- |
| high | judge |

- **Tell:** When the model lacks a fact, it fills the gap with hedged
  speculation dressed as background: "maintains a relatively low public profile,"
  "is believed to have," "likely began his career in," "appears to have
  studied." Worse than an honest cutoff disclaimer because the reader can't tell
  what's known from what's invented.
- **Fix:** Cut the speculation or replace it with a sourced fact. Say what isn't
  known rather than guessing.
- **Sources:** aboudjem (§21 second half), avoid-ai (adapted from blader P21).

---

### S9 — Consultant-speak / business jargon

| Severity | Enforcement |
| --- | --- |
| medium | judge |

- **Tell:** Polished-but-evasive language that signals work without carrying it:
  best-in-class, value-add, key learnings, actionable insights, holistic
  approach, strategic lever, future-proof, synergy. (Chinese equivalents: 赋能 /
  打通 / 闭环 / 抓手 / 链路.)
- **Fix:** If the draft makes a claim, say the claim plainly. Replace the
  abstraction with what actually happened, exists, or should be done.
- **Canonical / precedence:** the single-word AI-vocabulary items here
  (best-in-class, learnings, actionable, holistic, synergy) are **owned by L1** in
  `lexical-tells.md` — its tiered lists and replace-on-sight table are canonical
  for them. If a word matches both, apply L1's tier rule. S9 remains canonical for
  what L1 does not cover: multi-word consultant phrases (value-add, strategic
  lever, future-proof, actionable insights, holistic approach) and the Chinese
  buzzwords (赋能 / 打通 / 闭环 / 抓手 / 链路).
- **Sources:** anti-vibe (consultant tone + Chinese buzzwords), avoid-ai.

---

### S10 — Invented jargon / coined pseudo-terms

| Severity | Enforcement |
| --- | --- |
| medium | advisory |

- **Tell:** A domain-sounding term the model appears to have coined — it reads as
  sophisticated but has no established meaning in the field, or is an alien-syntax
  calque of a real term. Distinct from S9 (known consultant buzzwords) and L1
  (known AI vocabulary): those catch *established* filler words; this catches a
  *novel* term that sounds authoritative yet carries no agreed meaning. Reported
  independently for English, Polish, and Mandarin.
- **Fix (applies only once the validity condition below holds and the suite's
  cluster rule warrants acting):** replace with the plain established term the
  field actually uses. If the concept is real but genuinely lacks a standard term,
  define it in plain words on first use. If neither is possible, flag it for
  removal — do not invent a definition to justify the coinage.
- **Validity condition (both must hold — advisory, judge-only):** flag only when
  the term is BOTH (a) absent from the domain's standard usage AND (b) something
  the writer could not define plainly if asked. A real term of art the field uses,
  a deliberate new coinage the author defines, or a clearly intentional nonce word
  are NOT this tell — real fields have real jargon. When you cannot check the
  domain's usage, keep this advisory: note it, do not force an edit. No detector
  regex backs this entry; it is a quality-first, judge-only signal.
- **Sources:** Shreya Shankar thread (@sh_reya), cross-confirmed for English,
  Polish, and Mandarin by three independent repliers (research 2026-07-14).
