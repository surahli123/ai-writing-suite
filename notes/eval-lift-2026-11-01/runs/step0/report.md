# Step gate report: `step0`

Arms: bare, main, new. Judges: 2 orderings. Frozen items: 24; extra items: 3.

**GATE: FAIL** (new must be no worse than `main` and `bare` on every check; mean over 1 new run(s))

| vs | check | new | baseline | ok |
|---|---|---|---|---|
| main | would_send (frozen) | 41 | 45 | **NO** |
| main | meaning_changes (frozen) | 19 | 12 | **NO** |
| main | would_send (human controls) | 10 | 10 | yes |
| main | numbers_lost | 0 | 0 | yes |
| main | numbers_added | 0 | 0 | yes |
| main | hedges_lost | 2 | 2 | yes |
| bare | would_send (frozen) | 41 | 40 | yes |
| bare | meaning_changes (frozen) | 19 | 24 | yes |
| bare | would_send (human controls) | 10 | 8 | yes |
| bare | numbers_lost | 0 | 0 | yes |
| bare | numbers_added | 0 | 0 | yes |
| bare | hedges_lost | 2 | 5 | yes |

## Judge metrics by subset

| arm | subset | would send | 95% CI | meaning changes | unsupported kept | over-edited |
|---|---|---|---|---|---|---|
| bare | fixtures | 12/16 | 51%-90% | 15 | 0 | 3 |
| bare | fresh-ds | 14/16 | 64%-97% | 5 | 0 | 0 |
| bare | human-control | 8/10 | 49%-94% | 4 | 0 | 0 |
| bare | pr67-factbridge | 6/6 | 61%-100% | 0 | 0 | 0 |
| bare | s0-source-align | 4/4 | 51%-100% | 1 | 1 | 0 |
| bare | s0-withheld-authority | 2/2 | 34%-100% | 0 | 2 | 0 |
| bare | FROZEN-ALL | 40/48 | 70%-91% | 24 | 0 | 3 |
| main | fixtures | 13/16 | 57%-93% | 12 | 0 | 1 |
| main | fresh-ds | 16/16 | 81%-100% | 0 | 0 | 0 |
| main | human-control | 10/10 | 72%-100% | 0 | 0 | 0 |
| main | pr67-factbridge | 6/6 | 61%-100% | 0 | 0 | 0 |
| main | s0-source-align | 2/4 | 15%-85% | 0 | 2 | 0 |
| main | s0-withheld-authority | 2/2 | 34%-100% | 0 | 2 | 0 |
| main | FROZEN-ALL | 45/48 | 83%-98% | 12 | 0 | 1 |
| new | fixtures | 9/16 | 33%-77% | 19 | 0 | 2 |
| new | fresh-ds | 16/16 | 81%-100% | 0 | 0 | 0 |
| new | human-control | 10/10 | 72%-100% | 0 | 0 | 0 |
| new | pr67-factbridge | 6/6 | 61%-100% | 0 | 0 | 0 |
| new | s0-source-align | 4/4 | 51%-100% | 0 | 0 | 0 |
| new | s0-withheld-authority | 2/2 | 34%-100% | 0 | 2 | 0 |
| new | FROZEN-ALL | 41/48 | 73%-93% | 19 | 0 | 2 |

## Deterministic checks (all items)

| arm | numbers lost | numbers added | hedges lost | mean edit ratio |
|---|---|---|---|---|
| bare | 0 | 0 | 5 | 0.25 |
| main | 0 | 0 | 2 | 0.21 |
| new | 0 | 0 | 2 | 0.23 |

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
| tweet-01-obvious | 0 | 2 | 2 |
| linkedin-01-obvious | 0 | 2 | 2 |
| memo-01-obvious | 2 | 1 | 1 |
| memo-02-subtle | 2 | 2 | 0 |
| overstep-05-payoff-en | 2 | 0 | 0 |
| overstep-06-strawman-en | 2 | 2 | 2 |
| narrshape-04-absent-ambiguity-en | 2 | 2 | 0 |
| artifact-01-status-card-en | 2 | 2 | 2 |
| fp-terse-04 | 2 | 2 | 2 |
| fp-pro-linkedin-07 | 2 | 2 | 2 |
| fp-pro-memo-09 | 2 | 2 | 2 |
| fp-academic-05 | 2 | 2 | 2 |
| fp-esl-03-memo | 0 | 2 | 2 |
| s0-churn-cause | 2 | 0 | 2 |
| s0-latency-cause | 2 | 2 | 2 |
| s0-keep-conclusion | 2 | 2 | 2 |
