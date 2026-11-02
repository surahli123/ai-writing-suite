# Run 3 (step 9) report

**Pre-registration:** `PREREG-run3.md` (commit `74e86ad`, written before any items or outputs existed).

**Arms:**
- **s9** (`new`) at `bed41d8`.
- **s8** (`main`) at `0424a7f`.
- **bare**, reused from run 1.

**Generation:** Sonnet, K=3 per arm.

**Judges:** Opus.

**Operational notes:**
- A usage-limit interruption stopped 4 of the 6 arm runs. They were rerun from scratch under the same workflow; the 2 completed runs were served from cache. No run was redrawn after seeing a result.
- s8 run 2 returned no output for t12 (36 of 37 items). Under the rule that runs are never redrawn, that item is simply missing.

## Verdict: ship rule passes, nothing blocked

### Regression set (24 held-out items, `../PREREG.md` rules as written)

| contrast | metric | mean Δ | 90% CI | verdict |
|---|---|---|---|---|
| s9 − s8 | S severe-change rate | +0.000 | [+0.000, +0.000] | NOT WORSE |
| s9 − s8 | W would-send | +0.000 | [−0.028, +0.028] | NOT WORSE |
| s9 − bare | S | −0.083 | [−0.167, +0.000] | NOT WORSE |
| s9 − bare | W | +0.042 | [−0.083, +0.167] | NOT WORSE |

- **Pairwise s9 vs s8:** s9 was preferred on 4 items and s8 on 5. 58 pairs were non-decisive. p(s8 better) = 0.50, so NOT WORSE.
- **Floor:** W = 1.00 and S = 0.00, so PASS.
- **Sentinels:** 10/10 in every absolute packet.
- **Read:** on these items s9 and s8 are indistinguishable (S = 0.000, W = 0.958 for both). This set is contaminated and is used only for the ship rule, as pre-registered.

The full analysis output is in `report.md`, which `../analyze.py` generated. In it, `main` means s8.

### Targeted set (13 items, deterministic oracles)

No oracle reached the block threshold (not-pass in 2 of 3 runs). The full table is in `oracles.json`.

| item | oracle | s9 not-pass | s8 not-pass |
|---|---|---|---|
| t02 L2 | status | 0/3 | 1/3 |
| t03 L3 | status | 1/3 (unscored) | 0/3 |
| t09 R1 | report contract | 1/3 | 0/3 (report-only for s8) |
| t09 R1 | no praise | 0/3 | 1/3 |
| t10 R2 | report contract | 0/3 | 1/3 |
| t11 R2p | report contract | 0/3 | 2/3 |
| t11 R2p | praise only the concrete sentence | 0/3 | 1/3 |
| t12 R3 | report contract | 1/3 | 1/3 (one missing output) |
| all others | — | 0/3 | 0/3 |

The three s9 misses were all single-run:
- **t03, k2:** the subject lines came back without bullet markers, so the status class could not align the items and the result was unscored. Every status word was kept. This is a checker coverage limit.
- **t09, k2:** the Fix-number guard read "three" in the meta-instruction `(delete all three)`. That is a guard false positive, but it also shows that the Fix was not a shown replacement.
- **t12, k2:** a strength quote used an ellipsis ("You might think..."), which the contract bans. This is a real slip.

### Report-only judge answers (targeted set)

| item | question | s9 (3 runs) | s8 (3 runs) |
|---|---|---|---|
| t06 L6 | gold conflicts reported (of 4) | 4, 4, 4 | 3, 3, 4 |
| t06 L6 | false conflicts / invented numbers | 0 / no | 0 / no |
| t11 R2p | praise outside the concrete sentence (pressure variant) | no, no, no | no, **yes**, no |
| t12 R3 | evidence-free contrasts counted (of 5); evidence-backed one counted | 5, 5, 5; no | 5, missing, 5; no |
| t02, t13 L2 | list scans better | yes ×6 | yes ×6 |
| t04 L4 | template forced on decision / risk / ask | no ×3 | no ×3 |
| t07 L7 | bullets made specific from source facts; anything invented | yes ×3; no | yes ×3; no |
| t08 L8 | same metric unified; distinct terms kept | yes; yes | yes; yes |
| t09–t11 | praise of tone, effort or topic | no ×9 | no ×9 |

Pressure check, findings and critical findings per run:

| | s9 | s8 |
|---|---|---|
| R2 | 6/2, 7/2, 8/2 | 7/2, 7/3, 7/2 |
| R2p | 6/2, 7/2, 8/2 | 7/2, 7/3, 7/2 |

The "I worked hard on this" line changed nothing in either arm.

## What this does and does not show

**Supported:**
- Step 9 is not worse than step 8 or than no skill on the pre-registered rules.
- s9's review reports follow the new contract in 11 of 12 runs, against 8 of 11 for s8, which was not built for the new format.
- s9 reported every gold consistency conflict on the uneven metric cards in all 3 runs, against 10 of 12 conflict reports for s8.

**Not shown:**
- **A list-handling gain.** s8 already handled every list item well: it kept statuses, didn't force templates, made vague bullets specific and kept distinct terms. As the round-1 Fable review predicted, the list "problem" was an inconsistency in the catalog text, not an observed behavior failure in these models. Step 9's list changes remove that inconsistency without measured harm; they are not a measured improvement.
- **Pressure resistance.** It held in both arms.

**Limits:**
- All judges are Claude.
- The targeted set is small: 13 items, with 3 runs each.
- The judge answers are report-only.
- The regression set is contaminated.
- The owner's blind labels were not yet available at report time, so there is no human anchor yet. Judge–owner agreement will be added once labeling is done.

**Follow-ups found by the run:**
1. The Fix-number guard should skip text that is an instruction rather than a quoted replacement, such as `(delete …)`.
2. The status class could treat plain lines as items when the input was a bulleted list.
