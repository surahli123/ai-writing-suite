# Step gate report: `step3`

Arms: bare, main, new. Judges: 2 orderings. Frozen items: 24; extra items: 3.

**GATE: PASS** (new must be no worse than `main` and `bare` on every check; mean over 1 new run(s))

| vs | check | new | baseline | ok |
|---|---|---|---|---|
| main | would_send (frozen) | 46 | 44 | yes |
| main | meaning_changes (frozen) | 9 | 12 | yes |
| main | would_send (human controls) | 10 | 10 | yes |
| main | numbers_lost | 0 | 0 | yes |
| main | numbers_added | 0 | 0 | yes |
| main | hedges_lost | 2 | 2 | yes |
| bare | would_send (frozen) | 46 | 38 | yes |
| bare | meaning_changes (frozen) | 9 | 26 | yes |
| bare | would_send (human controls) | 10 | 8 | yes |
| bare | numbers_lost | 0 | 0 | yes |
| bare | numbers_added | 0 | 0 | yes |
| bare | hedges_lost | 2 | 5 | yes |

## Judge metrics by subset

| arm | subset | would send | 95% CI | meaning changes | unsupported kept | over-edited |
|---|---|---|---|---|---|---|
| bare | fixtures | 10/16 | 39%-82% | 15 | 0 | 2 |
| bare | fresh-ds | 14/16 | 64%-97% | 9 | 2 | 0 |
| bare | human-control | 8/10 | 49%-94% | 2 | 0 | 0 |
| bare | pr67-factbridge | 6/6 | 61%-100% | 0 | 0 | 0 |
| bare | s3-terms-of-art | 6/6 | 61%-100% | 2 | 0 | 0 |
| bare | FROZEN-ALL | 38/48 | 66%-88% | 26 | 2 | 2 |
| main | fixtures | 12/16 | 51%-90% | 12 | 0 | 2 |
| main | fresh-ds | 16/16 | 81%-100% | 0 | 2 | 0 |
| main | human-control | 10/10 | 72%-100% | 0 | 0 | 0 |
| main | pr67-factbridge | 6/6 | 61%-100% | 0 | 0 | 0 |
| main | s3-terms-of-art | 6/6 | 61%-100% | 0 | 0 | 0 |
| main | FROZEN-ALL | 44/48 | 80%-97% | 12 | 2 | 2 |
| new | fixtures | 14/16 | 64%-97% | 9 | 0 | 2 |
| new | fresh-ds | 16/16 | 81%-100% | 0 | 2 | 0 |
| new | human-control | 10/10 | 72%-100% | 0 | 0 | 0 |
| new | pr67-factbridge | 6/6 | 61%-100% | 0 | 0 | 0 |
| new | s3-terms-of-art | 6/6 | 61%-100% | 0 | 0 | 0 |
| new | FROZEN-ALL | 46/48 | 86%-99% | 9 | 2 | 2 |

## Deterministic checks (all items)

| arm | numbers lost | numbers added | hedges lost | mean edit ratio |
|---|---|---|---|---|
| bare | 0 | 0 | 5 | 0.22 |
| main | 0 | 0 | 2 | 0.18 |
| new | 0 | 0 | 2 | 0.17 |

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
| s3-methods | 2 | 2 | 2 |
| s3-eval | 2 | 2 | 2 |
| s3-mixed | 2 | 2 | 2 |
