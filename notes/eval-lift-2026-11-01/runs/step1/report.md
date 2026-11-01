# Step gate report: `step1`

Arms: bare, main, new. Judges: 2 orderings. Frozen items: 24; extra items: 5.

**GATE: FAIL** (new must be no worse than `main` and `bare` on every check; mean over 1 new run(s))

| vs | check | new | baseline | ok |
|---|---|---|---|---|
| main | would_send (frozen) | 44 | 44 | yes |
| main | meaning_changes (frozen) | 17 | 15 | **NO** |
| main | would_send (human controls) | 10 | 10 | yes |
| main | numbers_lost | 0 | 0 | yes |
| main | numbers_added | 0 | 0 | yes |
| main | hedges_lost | 2 | 2 | yes |
| bare | would_send (frozen) | 44 | 38 | yes |
| bare | meaning_changes (frozen) | 17 | 27 | yes |
| bare | would_send (human controls) | 10 | 8 | yes |
| bare | numbers_lost | 0 | 0 | yes |
| bare | numbers_added | 0 | 0 | yes |
| bare | hedges_lost | 2 | 5 | yes |

## Judge metrics by subset

| arm | subset | would send | 95% CI | meaning changes | unsupported kept | over-edited |
|---|---|---|---|---|---|---|
| bare | fixtures | 10/16 | 39%-82% | 15 | 0 | 3 |
| bare | fresh-ds | 14/16 | 64%-97% | 8 | 0 | 0 |
| bare | human-control | 8/10 | 49%-94% | 2 | 0 | 0 |
| bare | pr67-factbridge | 6/6 | 61%-100% | 2 | 0 | 0 |
| bare | s1-restraint | 7/10 | 40%-89% | 8 | 0 | 0 |
| bare | FROZEN-ALL | 38/48 | 66%-88% | 27 | 0 | 3 |
| main | fixtures | 12/16 | 51%-90% | 13 | 0 | 1 |
| main | fresh-ds | 16/16 | 81%-100% | 0 | 0 | 0 |
| main | human-control | 10/10 | 72%-100% | 0 | 0 | 0 |
| main | pr67-factbridge | 6/6 | 61%-100% | 2 | 0 | 0 |
| main | s1-restraint | 10/10 | 72%-100% | 4 | 0 | 0 |
| main | FROZEN-ALL | 44/48 | 80%-97% | 15 | 0 | 1 |
| new | fixtures | 12/16 | 51%-90% | 13 | 0 | 1 |
| new | fresh-ds | 16/16 | 81%-100% | 0 | 0 | 0 |
| new | human-control | 10/10 | 72%-100% | 2 | 0 | 0 |
| new | pr67-factbridge | 6/6 | 61%-100% | 2 | 0 | 0 |
| new | s1-restraint | 10/10 | 72%-100% | 4 | 0 | 0 |
| new | FROZEN-ALL | 44/48 | 80%-97% | 17 | 0 | 1 |

## Deterministic checks (all items)

| arm | numbers lost | numbers added | hedges lost | mean edit ratio |
|---|---|---|---|---|
| bare | 0 | 0 | 5 | 0.23 |
| main | 0 | 0 | 2 | 0.18 |
| new | 0 | 0 | 2 | 0.16 |

## Per-item would-send (sum of 2 orderings)

| item | bare | main | new |
|---|---|---|---|
| ds-01-abtest | 2 | 2 | 2 |
| ds-02-churn | 2 | 2 | 2 |
| ds-03-dataincident | 2 | 2 | 2 |
| ds-04-forecast | 2 | 2 | 2 |
| ds-05-fraudmodel | 2 | 2 | 2 |
| ds-06-survey | 2 | 2 | 2 |
| ds-07-nullresult | 0 | 2 | 2 |
| ds-08-latency | 2 | 2 | 2 |
| factbridge-01-unsupported-cause-en | 2 | 2 | 2 |
| factbridge-02-cooccurrence-en | 2 | 2 | 2 |
| factbridge-04-supported-possibility-en | 2 | 2 | 2 |
| tweet-01-obvious | 0 | 2 | 0 |
| linkedin-01-obvious | 0 | 2 | 2 |
| memo-01-obvious | 0 | 0 | 2 |
| memo-02-subtle | 2 | 2 | 2 |
| overstep-05-payoff-en | 2 | 0 | 0 |
| overstep-06-strawman-en | 2 | 2 | 2 |
| narrshape-04-absent-ambiguity-en | 2 | 2 | 2 |
| artifact-01-status-card-en | 2 | 2 | 2 |
| fp-terse-04 | 2 | 2 | 2 |
| fp-pro-linkedin-07 | 2 | 2 | 2 |
| fp-pro-memo-09 | 2 | 2 | 2 |
| fp-academic-05 | 2 | 2 | 2 |
| fp-esl-03-memo | 0 | 2 | 2 |
| s1-light-edit | 2 | 2 | 2 |
| s1-timeline | 2 | 2 | 2 |
| s1-stance | 0 | 2 | 2 |
| s1-attribution | 1 | 2 | 2 |
| s1-terse-status | 2 | 2 | 2 |
