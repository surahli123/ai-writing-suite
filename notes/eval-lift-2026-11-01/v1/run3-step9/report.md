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
| new − main | W would-send (higher better) | 24 | +0.000 | [-0.028, +0.028] | **NOT WORSE** |
| new − bare | S severe-change rate (lower better) | 24 | -0.083 | [-0.167, +0.000] | **NOT WORSE** |
| new − bare | W would-send (higher better) | 24 | +0.042 | [-0.083, +0.167] | **NOT WORSE** |

## Arm means

| arm | S | W | items |
|---|---|---|---|
| new | 0.000 | 0.958 | 24 |
| main | 0.000 | 0.958 | 24 |
| bare | 0.083 | 0.917 | 24 |

## Pairwise new vs main (a side wins only if both orders agree)

Item-level net: new preferred on 4 items, main on 5; non-decisive pairs: 58. One-sided p(main better) = 0.500 → **NOT WORSE**

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
| notes_vs_draft | new | 0.00 | 0.80 |
| notes_vs_draft | main | 0.00 | 0.80 |
| notes_vs_draft | bare | 0.40 | 0.60 |
| terse_status | new | 0.00 | 1.00 |
| terse_status | main | 0.00 | 1.00 |
| terse_status | bare | 0.00 | 1.00 |

## Ship rule: OPEN PRs (no WORSE / FAIL)
