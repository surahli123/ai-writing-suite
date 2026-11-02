## Judge results (2 orderings x items; would_send rate with Wilson 95% CI, mean meaning changes, mean reads-human rank 1=best)

| arm | subset | n | would send | 95% CI | meaning changes / cand | unsupported kept / cand | mean rank | picked best |
|---|---|---|---|---|---|---|---|---|
| bare | fresh-ds | 16 | 88% | 64%-97% | 0.38 | 0.00 | 1.75 | 7 |
| bare | pr67-factbridge | 6 | 100% | 61%-100% | 0.00 | 0.00 | 3.17 | 0 |
| bare | fixtures | 16 | 69% | 44%-86% | 0.88 | 0.00 | 2.69 | 3 |
| bare | human-control | 10 | 80% | 49%-94% | 0.40 | 0.00 | 3.50 | 1 |
| bare | ALL | 48 | 81% | 68%-90% | 0.50 | 0.00 | 2.60 | 11 |
| oneliner | fresh-ds | 16 | 100% | 81%-100% | 0.00 | 0.00 | 4.12 | 1 |
| oneliner | pr67-factbridge | 6 | 100% | 61%-100% | 0.00 | 0.00 | 3.17 | 1 |
| oneliner | fixtures | 16 | 62% | 39%-82% | 0.19 | 0.00 | 4.12 | 4 |
| oneliner | human-control | 10 | 80% | 49%-94% | 0.20 | 0.00 | 3.00 | 1 |
| oneliner | ALL | 48 | 83% | 70%-91% | 0.10 | 0.00 | 3.77 | 7 |
| suite-main | fresh-ds | 16 | 100% | 81%-100% | 0.00 | 0.00 | 3.38 | 4 |
| suite-main | pr67-factbridge | 6 | 100% | 61%-100% | 0.00 | 0.00 | 3.50 | 1 |
| suite-main | fixtures | 16 | 62% | 39%-82% | 0.56 | 0.00 | 4.06 | 1 |
| suite-main | human-control | 10 | 100% | 72%-100% | 0.00 | 0.00 | 3.40 | 3 |
| suite-main | ALL | 48 | 88% | 75%-94% | 0.19 | 0.00 | 3.62 | 9 |
| suite-pr67 | fresh-ds | 16 | 100% | 81%-100% | 0.12 | 0.00 | 2.62 | 3 |
| suite-pr67 | pr67-factbridge | 6 | 33% | 10%-70% | 0.00 | 0.67 | 5.50 | 0 |
| suite-pr67 | fixtures | 16 | 56% | 33%-77% | 0.88 | 0.00 | 2.88 | 4 |
| suite-pr67 | human-control | 10 | 100% | 72%-100% | 0.00 | 0.00 | 3.80 | 0 |
| suite-pr67 | ALL | 48 | 77% | 63%-87% | 0.33 | 0.08 | 3.31 | 7 |
| cursor-unslop | fresh-ds | 16 | 31% | 14%-56% | 0.19 | 0.00 | 5.31 | 1 |
| cursor-unslop | pr67-factbridge | 6 | 100% | 61%-100% | 0.00 | 0.00 | 1.83 | 3 |
| cursor-unslop | fixtures | 16 | 44% | 23%-67% | 1.12 | 0.00 | 3.50 | 1 |
| cursor-unslop | human-control | 10 | 60% | 31%-83% | 0.30 | 0.00 | 3.70 | 3 |
| cursor-unslop | ALL | 48 | 50% | 36%-64% | 0.50 | 0.00 | 3.94 | 8 |
| clay-unslop | fresh-ds | 16 | 100% | 81%-100% | 0.00 | 0.00 | 3.81 | 0 |
| clay-unslop | pr67-factbridge | 6 | 100% | 61%-100% | 0.00 | 0.00 | 3.83 | 1 |
| clay-unslop | fixtures | 16 | 62% | 39%-82% | 0.62 | 0.00 | 3.75 | 3 |
| clay-unslop | human-control | 10 | 100% | 72%-100% | 0.00 | 0.00 | 3.60 | 2 |
| clay-unslop | ALL | 48 | 88% | 75%-94% | 0.21 | 0.00 | 3.75 | 6 |

## Meaning-change types (ALL)

| arm | added_claim | dropped_fact | other | strengthened_certainty | weakened_certainty |
|---|---|---|---|---|---|
| bare | 4 | 0 | 12 | 0 | 8 |
| oneliner | 1 | 0 | 3 | 0 | 1 |
| suite-main | 0 | 3 | 4 | 0 | 2 |
| suite-pr67 | 0 | 5 | 4 | 1 | 6 |
| cursor-unslop | 3 | 2 | 13 | 2 | 4 |
| clay-unslop | 1 | 3 | 0 | 0 | 6 |

## Deterministic checks (per subset: totals over items)

| arm | subset | items | detector before->after (mean) | numbers lost | new numbers | hedges lost | scope words lost | must_preserve lost | mean edit ratio | mean len ratio |
|---|---|---|---|---|---|---|---|---|---|---|
| bare | fresh-ds | 8 | 0.0 -> 0.0 | 0 | 0 | 4 | 0 | 0 | 0.06 | 1.01 |
| bare | pr67-factbridge | 3 | 0.0 -> 0.0 | 0 | 0 | 0 | 0 | 0 | 0.24 | 0.77 |
| bare | fixtures | 8 | 19.1 -> 1.0 | 0 | 0 | 1 | 3 | 0 | 0.48 | 0.71 |
| bare | human-control | 5 | 0.0 -> 0.0 | 0 | 0 | 0 | 1 | 0 | 0.04 | 1.01 |
| oneliner | fresh-ds | 8 | 0.0 -> 0.0 | 0 | 0 | 0 | 0 | 0 | 0.00 | 1.00 |
| oneliner | pr67-factbridge | 3 | 0.0 -> 0.0 | 0 | 0 | 0 | 0 | 0 | 0.21 | 0.76 |
| oneliner | fixtures | 8 | 19.1 -> 3.8 | 0 | 0 | 1 | 3 | 0 | 0.39 | 0.72 |
| oneliner | human-control | 5 | 0.0 -> 0.0 | 0 | 0 | 0 | 1 | 0 | 0.03 | 1.00 |
| suite-main | fresh-ds | 8 | 0.0 -> 0.0 | 0 | 0 | 0 | 0 | 0 | 0.01 | 1.00 |
| suite-main | pr67-factbridge | 3 | 0.0 -> 0.0 | 0 | 0 | 0 | 0 | 0 | 0.21 | 0.76 |
| suite-main | fixtures | 8 | 19.1 -> 0.6 | 0 | 0 | 2 | 3 | 0 | 0.44 | 0.60 |
| suite-main | human-control | 5 | 0.0 -> 0.0 | 0 | 0 | 0 | 1 | 0 | 0.03 | 1.01 |
| suite-pr67 | fresh-ds | 8 | 0.0 -> 0.4 | 0 | 0 | 0 | 0 | 0 | 0.02 | 0.98 |
| suite-pr67 | pr67-factbridge | 3 | 0.0 -> 0.0 | 0 | 0 | 0 | 0 | 0 | 0.00 | 1.00 |
| suite-pr67 | fixtures | 8 | 19.1 -> 0.6 | 0 | 0 | 2 | 3 | 0 | 0.46 | 0.59 |
| suite-pr67 | human-control | 5 | 0.0 -> 0.0 | 0 | 0 | 0 | 1 | 0 | 0.03 | 1.01 |
| cursor-unslop | fresh-ds | 8 | 0.0 -> 0.0 | 1 | 0 | 3 | 1 | 0 | 0.19 | 1.08 |
| cursor-unslop | pr67-factbridge | 3 | 0.0 -> 0.0 | 0 | 0 | 0 | 0 | 0 | 0.25 | 0.76 |
| cursor-unslop | fixtures | 8 | 19.1 -> 0.6 | 0 | 0 | 2 | 3 | 0 | 0.51 | 0.57 |
| cursor-unslop | human-control | 5 | 0.0 -> 0.0 | 0 | 0 | 0 | 1 | 0 | 0.03 | 1.00 |
| clay-unslop | fresh-ds | 8 | 0.0 -> 0.0 | 0 | 0 | 0 | 0 | 0 | 0.00 | 1.00 |
| clay-unslop | pr67-factbridge | 3 | 0.0 -> 0.0 | 0 | 0 | 0 | 0 | 0 | 0.21 | 0.76 |
| clay-unslop | fixtures | 8 | 19.1 -> 1.2 | 0 | 0 | 1 | 3 | 0 | 0.37 | 0.67 |
| clay-unslop | human-control | 5 | 0.0 -> 0.0 | 0 | 0 | 0 | 1 | 0 | 0.03 | 1.01 |
