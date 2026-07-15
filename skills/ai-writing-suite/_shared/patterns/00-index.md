# AI-Tell Pattern Catalog — Index

This is the consolidated catalog of AI-writing "tells" that `comms-polish` draws
on. It merges seven source catalogs into one set of patterns organized by
category, with each pattern carrying a source tag so `NOTICE.md` attribution stays
accurate later. Where two entries describe the same phenomenon, one is the
**canonical** entry and the narrower ones are marked **aliases/subtypes** with a
precedence note ("if both match, apply the canonical fix") rather than silently
duplicated — see C2/H7/H8 (signposting) and S9↔L1 (consultant vocabulary).

## Why this catalog exists

Every source repo repeated most of the same tells in slightly different words.
Carrying seven overlapping lists would mean seven places to update and seven
chances to disagree with ourselves. One deduped catalog is the single source of
truth: `comms-polish` reads these files; the eventual programmatic detector
(Layer 3) and `NOTICE.md` attribution both key off the same `id` + `sources`
fields here.

## How to read a pattern entry

Each pattern uses this shape:

```
### <id> — <name>
- **Tell:** what the model does and why it reads as AI.
- **Fix:** the editing move that removes it.
- **Before / After:** a short concrete example (only where it earns its keep).
- **Sources:** which source catalogs this pattern came from (for attribution).
```

`id`s are stable. They are *not* the same as any single source's numbering
(blader P1-P43, aboudjem 1-30, avoid-ai categories) because those numbering
schemes overlap and conflict. Where a source had its own id, it is listed in
`Sources` so the lineage is traceable.

## Categories

| File | Category | What it covers |
| --- | --- | --- |
| [`lexical-tells.md`](lexical-tells.md) | Word-level tells | AI vocabulary, copula avoidance, synonym cycling, false ranges, hyphen-pair overuse |
| [`significance-attribution.md`](significance-attribution.md) | Inflation & sourcing | Significance/novelty inflation, vague attribution, promotional language, name-dropping, superficial -ing, speculative gap-filling, invented jargon / coined pseudo-terms |
| [`structural-tells.md`](structural-tells.md) | Structure & shape | Rule of three, negative parallelism, formulaic challenges, over-structure, inline-header lists, reshuffle immunity, treadmill effect, false concession |
| [`hedging-filler.md`](hedging-filler.md) | Hedging & filler | Filler phrases, excessive/stacked hedging, generic conclusions, future-narrative closers, confidence-calibration phrases, signposting, "let's" openers |
| [`punctuation-formatting.md`](punctuation-formatting.md) | Punctuation & formatting | Em/en dashes, bold overuse, emoji headers, curly quotes, title case, hashtag stuffing, placeholders, citation-markup leaks, UTM params |
| [`communication-artifacts.md`](communication-artifacts.md) | Chat artifacts | Chatbot tics, sycophancy, acknowledgment loops, cutoff disclaimers, collaborative-framing leaks, reasoning-chain leaks, engagement hooks, emotional flatline, register/style shift (canonical C11) |
| [`rhythm-stylometric.md`](rhythm-stylometric.md) | Rhythm & stylometry | Sentence/paragraph uniformity (burstiness), low vocabulary diversity (TTR), perplexity |
| [`overstepping-presumption.md`](overstepping-presumption.md) | Over-stepping (反代入式越位感) | Presumed cognition, presumed-misconception strawman, presumed mental image, self-Q&A-as-judge — plus the validity condition (judge-only, advisory) |
| [`narrative-shape.md`](narrative-shape.md) | Document / narrative shape (文档叙事形状) | Over-explained themes, tidy single-track resolution, flat escalation (reported as Claude's own StoryScope fingerprint), absent ambiguity — document-altitude, plus the validity condition (judge-only, advisory) |

## Inventory (entry counts)

> **Generated block — do not edit by hand.** Projected from the catalog by
> `aiws/catalog.py`; regenerate with `python3 -m aiws.catalog`.
> `evals/test_catalog_projection.py` fails CI if it drifts (Q5 lockfile model,
> `docs/decisions-2026-07-13.md`).

<!-- BEGIN GENERATED: inventory (aiws/catalog.py) -->
| File | Entries |
| --- | --- |
| [`lexical-tells.md`](lexical-tells.md) | 6 (L1–L6) |
| [`significance-attribution.md`](significance-attribution.md) | 10 (S1–S10) |
| [`structural-tells.md`](structural-tells.md) | 12 (T1–T12) |
| [`hedging-filler.md`](hedging-filler.md) | 10 (H1–H10) |
| [`punctuation-formatting.md`](punctuation-formatting.md) | 10 (F1–F10) |
| [`communication-artifacts.md`](communication-artifacts.md) | 11 (C1–C11) |
| [`rhythm-stylometric.md`](rhythm-stylometric.md) | 5 (R1–R5) |
| [`overstepping-presumption.md`](overstepping-presumption.md) | 4 (O1–O4) |
| [`narrative-shape.md`](narrative-shape.md) | 4 (N1–N4) |
| **Total** | **72** |
<!-- END GENERATED: inventory -->

(Plus L1's three vocabulary tiers in `lexical-tells.md`.)

## Registry (generated)

> **Generated block — do not edit by hand.** Machine-readable projection of every
> tell's id, name, severity (editorial harm), and enforcement (mechanism),
> rendered from the per-entry metadata tables by `aiws/catalog.py`. Regenerate
> with `python3 -m aiws.catalog`; `evals/test_catalog_projection.py` fails CI if
> it drifts from the catalog.

<!-- BEGIN GENERATED: registry (aiws/catalog.py) -->
| ID | Name | Severity | Enforcement |
| --- | --- | --- | --- |
| L1 | AI vocabulary words (tiered) | medium | regex |
| L2 | Copula avoidance | low | judge |
| L3 | Synonym / noun-phrase cycling (elegant variation) | medium | judge |
| L4 | False ranges | medium | judge |
| L5 | Hyphenated-pair overuse | low | judge |
| L6 | Hollow / "real-actual" intensifiers | low | regex |
| S1 | Significance inflation | high | regex |
| S2 | Symbolic gloss / meaning-telling | medium | judge |
| S3 | Novelty inflation | high | regex |
| S4 | Vague attribution / weasel words | high | regex |
| S5 | Notability name-dropping / source-listing as content | high | judge |
| S6 | Promotional / advertisement language | medium | judge |
| S7 | Superficial -ing analyses | medium | judge |
| S8 | Speculative gap-filling | high | judge |
| S9 | Consultant-speak / business jargon | medium | judge |
| S10 | Invented jargon / coined pseudo-terms | medium | advisory |
| T1 | Rule of three | low | judge |
| T2 | Negative parallelism / tailing negation | low | judge |
| T3 | Formulaic challenges section | medium | regex |
| T4 | False concession structure | medium | regex |
| T5 | Excessive / decorative structure | medium | judge |
| T6 | Inline-header vertical lists | low | judge |
| T7 | Bullet lists of bare noun phrases | low | regex |
| T8 | Numbered-list inflation | low | judge |
| T9 | Paragraph-reshuffle immunity | medium | judge |
| T10 | Treadmill effect (low information density) | medium | judge |
| T11 | Fragmented headers | low | judge |
| T12 | Diff-anchored writing | low | judge |
| H1 | Filler phrases | medium | regex |
| H2 | Excessive / stacked hedging | medium | regex |
| H3 | Generic positive conclusions | medium | regex |
| H4 | Generic future-narrative closers | medium | regex |
| H5 | Confidence-calibration phrases | medium | regex |
| H6 | Self-labeling significance | low | judge |
| H7 | Signposting / announcements | medium | regex |
| H8 | "Let's" false-collaborative openers | low | regex |
| H9 | Vague endorsement ("worth [verb]ing") | low | judge |
| H10 | Vague abstraction | medium | judge |
| F1 | Em / en dashes | low | regex |
| F2 | Bold overuse / erratic inline bolding | medium | regex |
| F3 | Emoji / icon dressing in headers | low | judge |
| F4 | Curly quotes & typographic signatures | low | judge |
| F5 | Title case in headings | low | regex |
| F6 | Markdown bleeding | medium | judge |
| F7 | Hashtag stuffing | medium | regex |
| F8 | Unfilled placeholders | high | regex |
| F9 | Chatbot citation-markup leaks (fingerprint) | high | regex |
| F10 | AI-tool URL parameters (fingerprint) | high | regex |
| C1 | Chatbot artifacts | high | regex |
| C2 | Collaborative-framing leaks | high | regex |
| C3 | Sycophantic tone | high | regex |
| C4 | Acknowledgment loops | medium | regex |
| C5 | Cutoff disclaimers | high | regex |
| C6 | Reasoning-chain artifacts | high | regex |
| C7 | Infomercial engagement hooks | medium | judge |
| C8 | Rhetorical-question openers | medium | regex |
| C9 | Emotional flatline | medium | regex |
| C10 | Parenthetical hedging | low | judge |
| C11 | Register / style shift (mixed authorship) | low | advisory |
| R1 | Sentence-length uniformity (low burstiness) | medium | regex |
| R2 | Paragraph-length uniformity | low | judge |
| R3 | Low vocabulary diversity (low TTR) | low | regex |
| R4 | Low perplexity (predictable word choice) | low | judge |
| R5 | Missing first-person / no stance | medium | judge |
| O1 | Presumed cognition (manufactured prior) | medium | advisory |
| O2 | Presumed-misconception strawman | medium | advisory |
| O3 | Presumed mental image | medium | advisory |
| O4 | Self-Q&A as judge | medium | advisory |
| N1 | Over-explained theme (states its own moral) | medium | advisory |
| N2 | Tidy single-track resolution (every thread closes, no residue) | medium | advisory |
| N3 | Flat escalation (uniform stakes curve) | medium | advisory |
| N4 | Absent ambiguity (no competing reading, no unresolved tension) | medium | advisory |
<!-- END GENERATED: registry -->

Severity ∈ {high, medium, low} is editorial harm; enforcement ∈ {regex (a
`evals/detector/` pattern flags it), judge (LLM-judge decidable), advisory
(judge-only, never auto-edited/CI-gated)}. Detection *confidence* is not here — it
stays in the detector's tier weights (owner ruling Q1).

## Source legend (for `Sources` tags)

| Tag | Source repo / skill | License |
| --- | --- | --- |
| `blader` | `blader/humanizer` (43-pattern catalog, P1-P43) | MIT |
| `aboudjem` | `Aboudjem/humanizer-skill` (Wikipedia "Signs of AI writing", 30 patterns) | MIT |
| `stop-slop` | `stop-slop` by Hardik Pandya (8 core rules + scoring rubric) | MIT |
| `avoid-ai` | `conorbronsdon/avoid-ai-writing` (tiered vocab + CATEGORIES taxonomy) | MIT |
| `anti-vibe` | `weijt606/anti-vibe-writing` (bilingual patterns, consultant-speak) | MIT |
| `ai-vibe` | `donghuixin/AI-Vibe-Writing-Skills` (style-extractor / reviewer prompts) | MIT |
| `nature` | `Yuan1z0825/nature-skills` (`nature-writing` + `nature-polishing`) | MIT |

> The corrupted `blader` reference (P31-P43 had duplicated/run-together "Fix /
> What's happening / Triggers / Source" blocks collapsed onto single lines) was
> **re-derived from intent**, not copied. Each affected pattern was reduced back
> to one clean Tell / Fix / example. The per-pattern `Sources` tag is the lineage
> record if a provenance question comes up.
