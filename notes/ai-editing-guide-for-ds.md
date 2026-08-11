# AI Editing Guide for Data Scientists

> **TL;DR.** Use AI to challenge your draft, sweep jargon, and triage review feedback. Don't ask it to write your conclusions. This page covers stages 2–4 of an analysis doc (drafting, self-edit, review). Five prompt templates inside; the §5 self-check is a menu you sample from. ≈6-min read.

---

## 1. Mental model: sparring partner, not ghostwriter

AI is most useful in DS writing when it does the things you'd skip when tired:

- Catch jargon you no longer notice
- Pressure-test claims that lack evidence
- Surface counterarguments you didn't consider
- Reorganize sections that drift off-thesis

It hurts you most when it writes the conclusions. Your judgment about *what the data means* is the artifact your readers are paying for, and AI cannot defend that judgment in a peer review. You can.

Use AI to make your draft harder to defend, then to help you defend it.

---

## 2. Setup once: the context preamble

RovoDev only knows what you give it. Before any editing session, paste in or reference:

| Source | What it teaches AI | Where to get it |
| --- | --- | --- |
| **DS comms playbook** | Voice, structure, hedge-density norms | (link to internal page) |
| **Glossary** | Accepted shorthand the team already uses | Confluence; partial coverage today |
| **Style guide fragments** | Format rules (numbers, citations, abbreviations) | Same; partial |
| **1–2 prior team-favorited analysis docs** | What "good" looks like on this team | Pick from the past quarter |

**Minimum-viable preamble** (paste at the top of any new RovoDev session):

```
Context for this editing session:
- Voice/structure: [link to DS comms playbook, or paste 5–10 lines]
- Glossary: [paste 10–20 accepted shorthand terms]
- Reference doc (what "good" looks like): [URL or attached file]
- Audience: [exec / cross-functional / DS peer]
```

If you'll do this more than twice, set up an `AGENTS.md` instead. See §8.

> **Partial coverage today.** Where the glossary or style guide is silent, attach a prior team-favorited doc as the implicit reference.

> **Restricted or confidential docs.** When you can't paste full context (sensitive metrics, embargoed analyses, customer data), paste section skeletons with synthetic metric labels, ask only for structural or jargon critique, and keep claim-evidence checks local. Skip §4.2 entirely; AI can't verify what it can't see.

---

## 3. Per-stage prompt menu

Stages map to where you are in the doc lifecycle. Pick the stage you're in; skip the ones where you'd rather work alone.

### Stage 2: Drafting (organizing findings into prose)

Your numbers are fixed. The work is *argument structure*. Two patterns; pick one:

- **Outline-first.** Paste raw findings + hypotheses. Ask: *"Suggest 2–3 outline structures (chronological, problem-solution, claim-evidence). Note tradeoffs for an exec audience."* Pick one, draft yourself. *Use this when the argument isn't clear yet.*
- **Scaffold-then-rewrite.** Paste raw findings. Ask AI to draft section-by-section. Rewrite each section by hand. Over time, this teaches AI your voice (see §8). *Use this when the argument is clear but you're stuck on prose.*

### Stage 3: Self-edit (polishing your own draft)

Apply the prompt templates in §4 only when you sense a specific problem. You won't need all five on every doc:

- A claim feels unsupported → **claim-evidence audit**
- The doc reads jargon-dense → **jargon sweep**
- Hedging too much (or not enough) → **hedge calibration**
- Structure feels off → **structural critique**

### Stage 4: Incorporating review feedback

AI helps most at **triage** and hurts most when **applying changes blindly**.

- **Triage prompt.** *"Here are 12 review comments and the doc. Group them: (1) factual corrections, (2) scope changes, (3) stylistic suggestions, (4) reviewers disagreeing with each other. For each, propose a one-line response."*
- **Apply prompt.** *"Apply [specific comment] to [section X] only. Show the diff. Do not edit other sections."*

---

## 4. Prompt templates (v0.1)

Drop into RovoDev with your context preamble already pasted. Templates 4.1–4.4 are **diagnostic** (flag without fixing); template 4.5 is **generative** (drafts bounded responses you approve before sending). You decide what changes ship.

> **Preflight for every template.** Prepend each prompt with: *"First list any missing inputs (line numbers, glossary terms, chart references, hedge thresholds) and flag them before producing findings."* Without this, AI confabulates instead of reporting gaps.

### 4.1 Jargon sweep

```
Read [section]. List every term a smart PM outside DS would not understand
without explanation. For each, propose: (a) a plain-English replacement, OR
(b) a one-sentence inline definition. Do NOT suggest cuts to terms that are
in [glossary]. Do NOT rewrite the section yourself.
```

### 4.2 Claim-evidence audit

```
For each numerical or causal claim in [section], cite the supporting
evidence (table, chart, prior section). Flag claims with no evidence or
weak evidence. Do NOT rewrite the claim — just list flags with line refs.
```

### 4.3 Hedge calibration

```
Highlight every hedge ("might", "suggests", "appears to") and every
absolute claim ("proves", "shows definitively"). For each, judge whether
the strength matches the evidence on a 3-point scale: under-claimed /
well-calibrated / over-claimed. Do NOT change the text.
```

### 4.4 Structural critique

```
The thesis of this doc is: [one sentence]. For each section, judge whether
it advances the thesis, supports it, or drifts. Flag any section that
drifts. Suggest one structural fix per drift, but do NOT rewrite.
```

### 4.5 Feedback triage

```
Here are review comments [paste]. The doc is [paste/attach]. Group comments
into: factual / scope / stylistic / reviewer-conflicts. For each, draft a
one-line response and identify the section to edit. Do NOT make edits.
```

---

## 5. Self-check (a menu, not a pipeline)

Pick the layers that match your doc; not every doc needs all four.

| Layer | What to ask AI | When it matters |
| --- | --- | --- |
| ① Hard rules | "Find any forbidden formatting, jargon not in glossary, or hedge density >X per paragraph." | Short reviews, polish pass |
| ② Claim-evidence integrity | "List any claim without a numbered citation or chart reference." | High-stakes docs, exec readouts |
| ③ Audience fit | "If the reader is a PM/eng with no DS background, where would they get lost?" | Cross-functional docs |
| ④ "Real analyst" pass | "Does this read like a careful analyst presenting honest findings, or like a confident report generator?" | Final pass, every doc |

If you write the same kind of doc weekly, turn this checklist into your own RovoDev skill. Hardcode your team's hedge thresholds and citation conventions; reuse it.

---

## 6. Don't do this

| Anti-pattern | Why it fails |
| --- | --- |
| Paste full doc + all review comments → *"address feedback"* | AI silently rewrites voice; contradicts adjacent sections |
| Let AI write the conclusion / "so what" / recommendation | Your judgment is the artifact; AI can't defend it in review |
| Accept stat language ("statistically significant", "causal", "drives") unchecked | AI doesn't know the test design; will over-claim |
| Run all five templates on every doc | Edits compound; voice flattens; you stop reading carefully |

---

## 7. ⚠️ Prompts go stale

> Templates here work on RovoDev's current model and harness. Model upgrades, harness changes, and tool updates will break some prompts silently. Output will look fine but skip steps. Treat every template as **v0.1**, re-test after major model upgrades, and date-stamp your `AGENTS.md` or writing skill so you know when it was last calibrated.

*This page: last updated **2026-05-04**. Tested against RovoDev as of that date.*

---

## 8. Going further: ship an `AGENTS.md`

If you'll edit more than two analysis docs with AI, stop pasting the preamble and put it in `AGENTS.md` instead. RovoDev's CLI reads `AGENTS.md` at session start when launched from the project root. Other surfaces (web, non-CLI) may not. Verify in your environment before relying on it. Drop this in your project root and edit:

```
# AGENTS.md — DS analysis docs

## Voice
- Match the DS comms playbook: [link]
- Hedge density: ~1 hedge per claim; none in the TL;DR
- No first-person in findings; first-person OK in implications

## Glossary (accepted shorthand — do not suggest cuts)
NDCG, MRR, recall@K, precision@K, A/B test, p-value, [team-specific terms]

## Reference doc (what "good" looks like)
[link to a team-favorited analysis doc]

## Editing rules
- Templates ask AI to flag, not fix.
- Feedback edits stay scoped to the cited section.

Last calibrated against RovoDev: [date]
```

Two compounding moves once your personal `AGENTS.md` works:

- **Share it.** Promote `personal/AGENTS.md` to `team/AGENTS.md` in a shared repo. Every DS gets this on session one, no guide required. The most-scaled version of this guide is the team `AGENTS.md`, not a doc.
- **Run the iterative voice loop.** AI drafts → you rewrite → AI diffs the two → bake the diff back into `AGENTS.md`. Three or four rounds gets it close to your voice. ~2 hours spread across a couple of weeks.

---

*v0.1. Open to feedback; comments on the page or DM.*
