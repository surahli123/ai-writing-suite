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
| new − main | S severe-change rate (lower better) | 24 | +0.014 | [+0.000, +0.042] | **NOT WORSE** |
| new − main | W would-send (higher better) | 24 | -0.014 | [-0.042, +0.000] | **NOT WORSE** |
| new − bare | S severe-change rate (lower better) | 24 | -0.069 | [-0.153, +0.000] | **NOT WORSE** |
| new − bare | W would-send (higher better) | 24 | +0.069 | [+0.000, +0.153] | **NOT WORSE** |

## Arm means

| arm | S | W | items |
|---|---|---|---|
| new | 0.014 | 0.986 | 24 |
| main | 0.000 | 1.000 | 24 |
| bare | 0.083 | 0.917 | 24 |

## Pairwise new vs main (a side wins only if both orders agree)

Item-level net: new preferred on 9 items, main on 3; non-decisive pairs: 53. One-sided p(main better) = 0.981 → **NOT WORSE**

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
| notes_vs_draft | new | 0.07 | 0.93 |
| notes_vs_draft | main | 0.00 | 1.00 |
| notes_vs_draft | bare | 0.40 | 0.60 |
| terse_status | new | 0.00 | 1.00 |
| terse_status | main | 0.00 | 1.00 |
| terse_status | bare | 0.00 | 1.00 |

## Ship rule: OPEN PRs (no WORSE / FAIL)

## Orchestrator notes (added after the pre-registered analysis; nothing above was changed)

- **Pre-registered outcome: OPEN PRs.** There is no WORSE on S, W, pairwise, or
  the floor.
- **Pairwise flipped from run 1.** `new` was preferred on 9 items and `main` on
  3 (run 1: 3 vs 10). That is consistent with the step-1 calibration fix
  removing the under-editing.
- **The only severe change by `new`** was one run, one item, in a
  notes-vs-draft case. The notes said only desktop was tested, and `new`
  narrowed the author's "ship to all platforms" recommendation to desktop. The
  judge scored that as overstepping the author's decision. This is an edge of
  owner ruling R1 (align claims to the supplied notes): it should apply to
  claims of fact, not to the author's recommendation. Flagged for the owner in
  the step-0 PR.
- **Caveats:**
  - Run 2 reuses the held-out items whose run-1 judge reasons informed the fix,
    so it confirms direction and is not a pure held-out test.
  - All judges are Claude.
  - Absolute metrics sit at the ceiling for both `main` and `new`. On these
    items, the fidelity steps (2–5) show no advantage over `main`. Their value
    is only regression protection plus deterministic tests.
  - Notes are hidden, so step 5's consistency findings are not measured.
