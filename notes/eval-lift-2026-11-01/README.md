# Skill-lift eval v0: does the suite beat no skill? (2026-11-01)

**Status: ADVISORY EXPERIMENT.** This is one run, with Claude as both writer and judge. It is directional evidence, not a benchmark. It is not wired into `run_all.sh` (ruling D2).

## Question

On `comms-polish`-style requests, does the suite produce text the author would rather send than what a bare model or a one-line instruction produces? Does the unmerged PR #67 (fact-to-interpretation boundary) change that? How do two popular external skills compare?

## Setup

**Six arms.** Every rewrite was done by Sonnet. Each arm handled the same 24 requests in one context.

| Arm | What the model got |
|---|---|
| `bare` | The request only |
| `oneliner` | Request + "Rewrite so it does not read AI-generated. Keep every fact, number, name, the author's voice and their level of certainty; add nothing new; if a passage is already fine, leave it alone." |
| `suite-main` | The skill at `main` @ `233d54a`. It reads `skills/comms-polish/SKILL.md` and follows it, including the `_shared/` reads. No voice profile. |
| `suite-pr67` | The same as `suite-main`, at PR #67 head `e6776fc` (main + the fact-interpretation boundary) |
| `cursor-unslop` | [cursor/plugins](https://github.com/cursor/plugins) `pstack/skills/unslop` (MIT, Lauren Tan) |
| `clay-unslop` | [theclaymethod/unslop](https://github.com/theclaymethod/unslop) v2.3.0 @ `17ed39c` (MIT). Its bundled scripts were not run. |

**24 items in 4 subsets** (`items.json`):

| Subset | n | What it tests |
|---|---|---|
| `fresh-ds` | 8 | Data-science updates (A/B readout, churn email, data incident, forecast memo, model launch, survey summary, null result, latency incident). Sonnet wrote them with no skill from notes containing deliberate hedges (`briefs.json` → `drafts.json`). Five requests include the notes. This is realistic 2026 input. |
| `pr67-factbridge` | 3 | PR #67's own fixtures: a memo sentence plus a source note that does or does not support its causal clause |
| `fixtures` | 8 | Existing `fixtures.json` "before" texts: heavy classic slop, overstepping, narrative shape, an artifact card |
| `human-control` | 5 | `false_positives.json` human-style texts (terse, pro LinkedIn, pro memo, academic, ESL memo). The right move is little or no change. |

**Judging.** Four blind judges ran on the session model (Opus): two orderings, each split into two halves of the items. Each judge saw all six candidates per item under shuffled labels A–F. For each candidate it recorded:

- `would_send`, meaning "as the author, would you send this as-is?";
- typed `meaning_changes`;
- `unsupported_claims_kept`, scored only when notes were given;
- `over_edited`.

Judges also gave a reads-human rank and a best pick.

Agreement between the two orderings: `would_send` matched 134 of 144 times. The best pick matched only 11 of 24 times, so best-pick counts are noise.

**Deterministic checks** (`score.py`): the suite's stdlib detector before and after; numbers lost or added; a hedge list and a scope-word list; `must_preserve`; word-level edit ratio; length ratio.

Rerun: `python3 -I score.py <dir with items.json + result.json> skills/ai-writing-suite/evals`. Full tables are in `tables.md`.

## Results

| Arm | Would send (all, n=48) | Meaning changes per candidate | Human controls would send | Fresh-DS would send | Fresh-DS mean edit ratio |
|---|---|---|---|---|---|
| bare | 81% (68–90) | 0.50 | 80% | 88% | 0.06 |
| oneliner | 83% (70–91) | **0.10** | 80% | 100% | 0.00 |
| **suite-main** | **88%** (75–94) | 0.19 | **100%** | 100% | 0.01 |
| suite-pr67 | 77% (63–87) | 0.33 | 100% | 100% | 0.02 |
| cursor-unslop | 50% (36–64) | 0.50 | 60% | **31%** | 0.19 |
| clay-unslop | **88%** (75–94) | 0.21 | 100% | 100% | 0.00 |

Paired item-level sign tests, counting how many items each arm did better or worse on:

- **suite-main vs bare:** would-send 3/2, p=1.0. Fewer meaning changes on 8 items, more on 1 (p=0.04). This is the only significant lift over no skill.
- **suite-main vs oneliner:** would-send 3/2, meaning changes 2/4. **No measurable difference.** The one-liner also beats bare on meaning changes (7/0, p=0.02).
- **suite-main vs clay-unslop:** 2/2, a tie.
- **suite-main vs cursor-unslop:** 12/1 on would-send (p<0.01) and 8/0 on meaning changes. Clearly better.
- **suite-pr67 vs suite-main:** 1/3 on would-send and 0/3 on meaning changes. Slightly worse, not significant. The whole loss is explained below.
- 7 of 24 items did not separate the arms at all: every arm was sent by both judges.

## What it means

1. **On Sonnet-class polish requests, the suite's measurable lift over no skill is fidelity, and a one-line instruction gets the same.** Bare Sonnet already strips classic tells: the detector mean on fixtures went from 19.1 to between 0.6 and 3.8 for *every* arm, bare included. Bare Sonnet's failure mode is small meaning drift: "no evidence" softened to "no clear evidence", an ambiguous deadline resolved one way, a register shift. Telling it to keep facts, certainty, and voice removes most of that. This matches the outside evidence in `../research-landscape-2026-11-01.md`: long rulesets must beat a one-liner, and several projects shrank theirs without losing anything.
2. **The suite is safe on human text and on already-good drafts.** It scored 100% would-send on human controls, edited fresh DS drafts by 1%, and lost no hedges or numbers. cursor-unslop, a short opinionated skill, over-edits: it turned terse Slack bullets into prose and lost 3 hedges and 1 number on fresh drafts. Being conservative pays.
3. **PR #67 does what its rule says, and readers don't want that rule.** When the user's own source note contradicted the draft's causal clause, #67's polish path *kept* the clause and flagged it in a note ("I left the clause in because it is your claim"). That follows its "do not silently erase the author's position unless factual revision was authorized" rule. Every other arm, including bare, cut the clause and said why. The judges would send #67's version 2 times out of 6 versus 6 out of 6 for the others. PR #67's own fixtures also expect the cut (`factbridge-01` `after`), so **the PR's rule contradicts the PR's own gold answers.**
   - Suggested fix: when the user supplies the source packet in the same request, treat that as authorization to align claims with it (cut or qualify, then say what changed). Keep preserve-and-flag for standalone drafts only.
   - On fresh-DS and human controls, #67 matched main.
4. **Catalog rules versus reader judgment.** On `overstep-05-payoff`, the suite produced *exactly* the gold rewrite: it deleted "You might think X, but…". Both judges rejected it as over-editing, an anticipated objection the evidence answers. bare, oneliner and clay-unslop all kept the setup. On `memo-01` and `linkedin-01`, removing a vague "Experts believe" attribution and "transformative experience" sentiment cost would-send even though the notes flagged the cuts. This is the over-editing evidence for proposal A2 (edit restraint). It is also a reason to revisit the overstepping validity condition: a setup answered with concrete evidence may be earned.
5. **The regex detector cannot see 2026 model output.** All 8 fresh Sonnet drafts scored 0 before editing. It also cannot tell the arms apart on fixtures (all end at 0.6–3.8). It remains a regression fence for the catalog, but it cannot measure skill lift. That needs judged, paired evals like this one.

## Limits

- **One run per arm.** Each arm saw all 24 items in a single context, not fresh chats, so later items may be affected by earlier ones.
- **n is small:** 24 items and 48 judgments per arm. The confidence intervals overlap everywhere except cursor-unslop.
- **Writer, arms, and judges are all Claude** (Sonnet writes, Opus judges). No cross-vendor panel.
- **Only `comms-polish` rewrite was tested.** The suite's other value is untested: comms-draft from the KB/playbook, voice profiles, review/detect reports, long documents, and weaker host models.
- **The fixtures were written by the suite's author**, which favors the suite's style. Their gold `after` texts add facts not in the `before` (aspirational), so they were not used as targets.

## Next runs worth doing

1. **Re-run with the fixes:**
   - #67 with the "user-supplied source = authorization" change;
   - A2's light-edit and named-failure rule;
   - softened overstepping on evidence-answered setups.

   Compare each against `oneliner`.
2. **Test where a one-liner cannot compete:**
   - drafting from a KB/playbook (comms-draft);
   - voice-profile matching on the owner's real writing;
   - review-mode findings quality;
   - 600–1500-word DS documents.
3. **Raise statistical power:**
   - Haiku as the arm model, since outside reports say rule lift is larger at lower tiers;
   - K≥3 fresh contexts per arm;
   - real de-identified DS drafts as items, which unblocks P3.
