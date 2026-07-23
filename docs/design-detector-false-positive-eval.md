# Design — Known-Human-Negative False-Positive Eval (E1)

Date: 2026-07-22
Status: BUILT (feat/w3-e1-known-human-eval, 2026-07-22) — machinery + an 8-sample seed public corpus ship per this design; the 100-sample falsifiable next step remains open

## Problem and boundary

The current `evals/fixtures/false_positives.json` suite is a synthetic regression
fence. Its samples were written with knowledge of the detector and explicitly
disclaim benchmark validity. It proves that known rules do not regress on those
examples; it does not measure the detector's false-positive rate on real human
writing.

This design adds a known-human-negative evaluation at the detector's existing
operating point. A public-domain set can broaden reproducible coverage, but it is
supplemental evidence only. Claims about current real writers remain gated on a
separate, owner-approved set of real writing.

The detector/checker remains a regression signal, not a measure of writing
quality or a product KPI.

## Evidence sets

Two sets have different jobs and must never be pooled into one headline rate.

| Set | Purpose | May support a real-writer claim? | Storage |
| --- | --- | --- | --- |
| Owner-gated real-writer set | Measure behavior on current, in-domain writers across relevant genres, L1 backgrounds, and styles | Yes, with cohort counts and uncertainty disclosed | Outside the repository; de-identified local manifest and samples |
| Reproducible public set | Exercise independently authored human prose and catch detector regressions in CI | No; supplemental only | Redistributable excerpts plus provenance manifest, if the item-level license permits |

The owner-gated set requires affirmative permission for evaluation, a declared
retention period, and de-identification before scoring. Results are reported by
genre and declared cohort; raw text and direct identifiers do not enter commits
or CI logs. Small cohorts are aggregated or withheld rather than exposed.

The first public candidates should be works whose human authorship predates
generative-writing systems and whose reuse status is clear at the item level:

- public-domain letters, essays, and technical prose from Project Gutenberg or
  an equivalent archive, after checking the work's jurisdiction-specific rights
  notice rather than treating the host collection as one blanket license;
- United States federal works that carry an item-level public-domain statement;
- modern prose under an explicit permissive or Creative Commons license, only
  when attribution, share-alike, excerpting, and redistribution conditions can
  be satisfied in this repository.

Every candidate gets a license review before inclusion. A URL alone is not
license evidence. The manifest records the author, title, publication date,
source URL, retrieval date, license or public-domain basis, jurisdiction where
relevant, required attribution, excerpt boundaries, genre, language, byte
checksum, and local sample path. A sample with ambiguous authorship, an
ambiguous license, post-publication AI editing, or a failed checksum is excluded.

Public-domain prose is likely to be older and distributionally different from
Slack, PR, README, LinkedIn, and memo writing. Results therefore stay stratified
by source and genre proxy. A large historical set cannot compensate for a
missing current real-writer set.

## Operating point

The evaluated operating point is the detector's shipped flag rule:

```text
flagged := analyze(sample)["score"] >= 14
```

`14` is read from the same source that defines the existing
`flag_threshold`/`baseline_threshold` contract. It is frozen before the
known-human samples are scored. The negative corpus must not be used to tune the
threshold and then evaluate that same threshold.

For each set and declared stratum, report:

```text
false positives = count(flagged known-human samples)
eligible samples = count(samples that passed provenance and integrity checks)
FP rate = false positives / eligible samples
```

The report includes the numerator, denominator, threshold, score distribution,
and a 95% Wilson interval implemented with `math.sqrt`. It never emits only a
percentage. Sample-level scores are retained in a local receipt for error
analysis; owner-gated text is not printed.

## Stdlib capability shape

A future build can use only `json`, `hashlib`, `pathlib`, `argparse`,
`statistics`, and `math`:

```text
evals/
├── capabilities/
│   └── known_human_negatives.py
└── known_human/
    ├── manifest.json
    ├── run_known_human.py
    └── samples/
```

`manifest.json` contains only the reproducible public set and declares
`evidence_role: supplemental_public`. `run_known_human.py` validates provenance
fields and checksums, reads the detector threshold, scores each sample, and
prints the bounded report. A `--manifest` option permits a local owner-gated
manifest whose records declare `evidence_role: owner_gated_real_writer`; that
path is never committed.

`evals/capabilities/known_human_negatives.py` exports the normal discovered
`SPEC` and `run(context)` pair and shells out to the dedicated runner. The public
capability may fail on malformed provenance, checksum drift, an empty cohort, or
an owner-ratified false-positive ceiling. Its output must always say
`SUPPLEMENTAL PUBLIC SET — NOT A REAL-WRITER BENCHMARK`.

This capability never imports `fixtures.calibration`, never writes
`evals/fixtures/fixtures.json`, and never calls `run_fixtures.py`. It is a
separate discovered capability, so its samples cannot enter the eight-example
calibration denominator or alter the pinned `3/8 = 38%` line.

An external receipt may summarize both runs, but the two numerators and
denominators remain separate. A release claim about real-writer specificity is
invalid unless the receipt includes a fresh owner-gated run.

## Acceptance criteria

- The public manifest rejects any sample without item-level authorship,
  provenance, rights basis, excerpt boundary, and checksum fields.
- The public run is visibly labeled supplemental and cannot be presented as a
  substitute for the owner-gated real-writer set.
- The detector threshold under test is the pre-existing shipped threshold
  (`14` at design time), read rather than retuned on the known-human corpus.
- Reports include false-positive counts, eligible counts, rates, score
  distributions, and uncertainty, separated by evidence set and stratum.
- Owner-gated raw text and direct identifiers remain outside the repository and
  outside test output.
- Capability discovery can add the eval without changing
  `fixtures.json`, `run_fixtures.py`, or the calibration denominator.
- A checksum, license, or provenance failure makes the affected sample
  ineligible and makes an empty required cohort fail loudly.

**Falsifiable next step:** License-audit and score 100 public-domain samples
(25 each across four declared genre proxies) at threshold 14; if more than 5
samples are flagged, the detector's specificity is overclaimed and the public
set must report that failure without changing the threshold. This result remains
supplemental until a separately consented owner-gated real-writer set is run.
