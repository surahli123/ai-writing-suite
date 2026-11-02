# v1 report (pre-registered rules in PREREG.md)

Judge model(s): ['opus']. Items: 24 held-out.

## Sentinel accuracy per absolute packet (keep if >= 8/10)

- bare_k1: 10/10
- main_k1: 10/10
- main_k2: 10/10
- main_k3: 10/10
- new_k1: 10/10
- new_k2: 10/10
- new_k3: 10/10

## Paired item-level differences (bootstrap 90% CI)

| contrast | metric | items | mean Δ | 90% CI | verdict |
|---|---|---|---|---|---|
| new − main | S severe-change rate (lower better) | 24 | +0.000 | [+0.000, +0.000] | **NOT WORSE** |
| new − main | W would-send (higher better) | 24 | +0.000 | [+0.000, +0.000] | **NOT WORSE** |
| new − bare | S severe-change rate (lower better) | 24 | -0.083 | [-0.167, +0.000] | **NOT WORSE** |
| new − bare | W would-send (higher better) | 24 | +0.083 | [+0.000, +0.167] | **NOT WORSE** |

## Arm means

| arm | S | W | items |
|---|---|---|---|
| new | 0.000 | 1.000 | 24 |
| main | 0.000 | 1.000 | 24 |
| bare | 0.083 | 0.917 | 24 |

## Pairwise new vs main (a side wins only if both orders agree)

Item-level net: new preferred on 3 items, main on 10; non-decisive pairs: 46. One-sided p(main better) = 0.046 → **WORSE**

## Floor (clean_human + terse_status, 9 items)

new: W = 1.00 (need ≥ 0.85), S = 0.00 (need ≤ 0.10) → **PASS**

## By category (mean S / W)

| category | arm | S | W |
|---|---|---|---|
| ai_draft_with_content | new | 0.00 | 1.00 |
| ai_draft_with_content | main | 0.00 | 1.00 |
| ai_draft_with_content | bare | 0.00 | 1.00 |
| clean_human | new | 0.00 | 1.00 |
| clean_human | main | 0.00 | 1.00 |
| clean_human | bare | 0.00 | 1.00 |
| long_doc_inconsistency | new | 0.00 | 1.00 |
| long_doc_inconsistency | main | 0.00 | 1.00 |
| long_doc_inconsistency | bare | 0.00 | 1.00 |
| notes_vs_draft | new | 0.00 | 1.00 |
| notes_vs_draft | main | 0.00 | 1.00 |
| notes_vs_draft | bare | 0.40 | 0.60 |
| terse_status | new | 0.00 | 1.00 |
| terse_status | main | 0.00 | 1.00 |
| terse_status | bare | 0.00 | 1.00 |

## Ship rule: BISECT (pairwise vs main)

## Orchestrator notes (added after the pre-registered analysis; nothing above was changed)

- **Pre-registered outcome: BISECT.** `main` was preferred pairwise on 10 items and
  `new` on 3, with 46 of 72 pairs indecisive (p = 0.046).
- **The absolute metrics are at the ceiling for both** (S = 0, W = 1.00 on all 24
  held-out items, sentinels 10/10). So the pairwise loss is not a fidelity
  regression.
- **Mechanism, from the judges' written reasons on the decisive pairs:**
  - `main` won on readability: paragraph breaks, a smoother lead, and a light
    polish where `new` returned the text unchanged. Examples are h-04 and h-20
    (terse status, where "the author asked for a light cleanup") and h-06
    (paragraph breaks).
  - `new` won where it kept the author's evaluation or attribution ("a meaningful
    win", h-15 ×3, h-09, h-12). That is the step-1 "keep the claim" rule
    working.
- **Working hypothesis:** step 1's restraint rules make `new` under-edit when the
  request asks to improve readability. The localization step is to calibrate
  restraint to the request type, then re-test.
- **Design limit:** notes are hidden from the gated metrics, so step 5's
  consistency findings, which are reported in notes, are invisible here. For
  example, `new` flagged h-07's 410k vs 401k in its notes.
- **bare** made severe changes on 40% of the notes-vs-draft items (S = 0.40 there).
  The suite's alignment-with-notes behavior is real against no skill.
