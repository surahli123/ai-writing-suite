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
| [`significance-attribution.md`](significance-attribution.md) | Inflation & sourcing | Significance/novelty inflation, vague attribution, promotional language, name-dropping, superficial -ing, speculative gap-filling |
| [`structural-tells.md`](structural-tells.md) | Structure & shape | Rule of three, negative parallelism, formulaic challenges, over-structure, inline-header lists, reshuffle immunity, treadmill effect, false concession |
| [`hedging-filler.md`](hedging-filler.md) | Hedging & filler | Filler phrases, excessive/stacked hedging, generic conclusions, future-narrative closers, confidence-calibration phrases, signposting, "let's" openers |
| [`punctuation-formatting.md`](punctuation-formatting.md) | Punctuation & formatting | Em/en dashes, bold overuse, emoji headers, curly quotes, title case, hashtag stuffing, placeholders, citation-markup leaks, UTM params |
| [`communication-artifacts.md`](communication-artifacts.md) | Chat artifacts | Chatbot tics, sycophancy, acknowledgment loops, cutoff disclaimers, collaborative-framing leaks, reasoning-chain leaks, engagement hooks, emotional flatline, register/style shift (canonical C11) |
| [`rhythm-stylometric.md`](rhythm-stylometric.md) | Rhythm & stylometry | Sentence/paragraph uniformity (burstiness), low vocabulary diversity (TTR), perplexity |
| [`overstepping-presumption.md`](overstepping-presumption.md) | Over-stepping (反代入式越位感) | Presumed cognition, presumed-misconception strawman, presumed mental image, self-Q&A-as-judge — plus the validity condition (judge-only, advisory) |

## Inventory (entry counts)

| File | Entries |
| --- | --- |
| [`lexical-tells.md`](lexical-tells.md) | 6 (L1–L6) |
| [`significance-attribution.md`](significance-attribution.md) | 9 (S1–S9) |
| [`structural-tells.md`](structural-tells.md) | 12 (T1–T12) |
| [`hedging-filler.md`](hedging-filler.md) | 10 (H1–H10) |
| [`punctuation-formatting.md`](punctuation-formatting.md) | 10 (F1–F10) |
| [`communication-artifacts.md`](communication-artifacts.md) | 11 (C1–C11) |
| [`rhythm-stylometric.md`](rhythm-stylometric.md) | 5 (R1–R5) |
| [`overstepping-presumption.md`](overstepping-presumption.md) | 4 (O1–O4) |
| **Total** | **67** |

(Plus L1's three vocabulary tiers in `lexical-tells.md`.)

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
