# Step gate report: `step2`

Arms: bare, main, new. Judges: 2 orderings. Frozen items: 24; extra items: 4.

**GATE: FAIL** (new must be no worse than `main` and `bare` on every check; mean over 1 new run(s))

| vs | check | new | baseline | ok |
|---|---|---|---|---|
| main | would_send (frozen) | 43 | 43 | yes |
| main | meaning_changes (frozen) | 6 | 6 | yes |
| main | would_send (human controls) | 8 | 10 | **NO** |
| main | numbers_lost | 0 | 0 | yes |
| main | numbers_added | 0 | 0 | yes |
| main | hedges_lost | 2 | 2 | yes |
| bare | would_send (frozen) | 43 | 39 | yes |
| bare | meaning_changes (frozen) | 6 | 18 | yes |
| bare | would_send (human controls) | 8 | 9 | **NO** |
| bare | numbers_lost | 0 | 0 | yes |
| bare | numbers_added | 0 | 0 | yes |
| bare | hedges_lost | 2 | 5 | yes |

## Judge metrics by subset

| arm | subset | would send | 95% CI | meaning changes | unsupported kept | over-edited |
|---|---|---|---|---|---|---|
| bare | fixtures | 10/16 | 39%-82% | 14 | 0 | 0 |
| bare | fresh-ds | 14/16 | 64%-97% | 3 | 0 | 0 |
| bare | human-control | 9/10 | 60%-98% | 1 | 0 | 0 |
| bare | pr67-factbridge | 6/6 | 61%-100% | 0 | 0 | 0 |
| bare | s2-fidelity | 8/8 | 68%-100% | 0 | 0 | 0 |
| bare | FROZEN-ALL | 39/48 | 68%-90% | 18 | 0 | 0 |
| main | fixtures | 11/16 | 44%-86% | 6 | 0 | 2 |
| main | fresh-ds | 16/16 | 81%-100% | 0 | 0 | 0 |
| main | human-control | 10/10 | 72%-100% | 0 | 0 | 0 |
| main | pr67-factbridge | 6/6 | 61%-100% | 0 | 0 | 0 |
| main | s2-fidelity | 8/8 | 68%-100% | 0 | 0 | 0 |
| main | FROZEN-ALL | 43/48 | 78%-95% | 6 | 0 | 2 |
| new | fixtures | 13/16 | 57%-93% | 4 | 0 | 2 |
| new | fresh-ds | 16/16 | 81%-100% | 0 | 0 | 0 |
| new | human-control | 8/10 | 49%-94% | 2 | 0 | 0 |
| new | pr67-factbridge | 6/6 | 61%-100% | 0 | 0 | 0 |
| new | s2-fidelity | 8/8 | 68%-100% | 0 | 0 | 0 |
| new | FROZEN-ALL | 43/48 | 78%-95% | 6 | 0 | 2 |

## Deterministic checks (all items)

| arm | numbers lost | numbers added | hedges lost | mean edit ratio |
|---|---|---|---|---|
| bare | 0 | 0 | 5 | 0.21 |
| main | 0 | 0 | 2 | 0.17 |
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
| tweet-01-obvious | 0 | 2 | 1 |
| linkedin-01-obvious | 0 | 1 | 2 |
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
| fp-esl-03-memo | 1 | 2 | 0 |
| s2-readout | 2 | 2 | 2 |
| s2-scope | 2 | 2 | 2 |
| s2-null | 2 | 2 | 2 |
| s2-forecast | 2 | 2 | 2 |
