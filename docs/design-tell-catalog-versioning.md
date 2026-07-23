# Design — Tell-Catalog Versioning and Decay (E2)

Date: 2026-07-22
Status: DESIGN ONLY — no catalog schema or lint is changed in this lane

## Problem and boundary

The tell catalog currently has 72 stable IDs. Each entry carries `Severity` and
`Enforcement`, and `aiws/catalog.py` projects that metadata into
`_shared/patterns/00-index.md`. The registry is internally consistent, but it is
a timeless snapshot: an entry does not say when its evidence was last reviewed,
which revision of the tell is active, or when a moving regex target must be
retested.

Versioning must preserve stable tell IDs and attribution while making evidence
age visible. Decay is a review trigger, not automatic proof that a tell became
false. An old entry is never silently deleted or rewritten.

The detector/checker remains a regression signal, not a writing-quality metric
or product KPI.

## Entry identity and revision

The catalog ID remains the semantic identity used by reports and consumers:
`L1`, `S4`, `C8`. Each entry adds a monotonic positive integer `Version` and an
ISO date `Reviewed` to its existing metadata table:

```markdown
### L1 — AI vocabulary words (tiered)

| Severity | Enforcement | Version | Reviewed |
| --- | --- | --- | --- |
| medium | regex | 3 | 2026-07-22 |
```

This is a schema replacement, not two columns appended to a permissive parser.
`aiws/catalog.py`'s `_META_HEADER` and `_META_ROW` regexes
(`catalog.py:60-61`) are hard-pinned to exactly
`| Severity | Enforcement |` plus a two-value row. The current parser rejects
the four-column table above, so a future implementation must change both regexes
and their validation tests in the same change before any catalog entry adopts
the new shape.

The addressable revision is `L1@3`. The bare ID still means "the active revision
of L1", so existing audit reports and by-ID consumers do not break.

Increment `Version` when any behaviorally meaningful part changes:

- the tell definition, trigger boundary, or validity condition;
- the prescribed fix;
- severity or enforcement;
- a regex term, weight, threshold, or deterministic matching rule;
- source lineage that changes the evidence basis.

Do not increment it for spelling, wrapping, or an example-only clarification
that leaves behavior unchanged. `Reviewed` advances only when a reviewer
examines fresh evidence at the active revision; touching the date to silence
staleness is invalid.

A future append-only `_shared/patterns/review-ledger.jsonl` records each review:

```json
{"id":"L1","version":3,"reviewed":"2026-07-22","decision":"retain","evidence":["fp-public-2026-07","holdout-2026-07"],"note":"target and false-positive boundary rechecked"}
```

JSON Lines keeps the history diffable and stdlib-readable. The catalog entry is
the current state; the ledger is the evidence trail. A ledger row cannot activate
a revision that is absent from the catalog.

## Review cadence

Cadence follows enforcement mechanism because deterministic targets decay
faster than editorial concepts:

| Enforcement | Review due after | Reason |
| --- | --- | --- |
| `regex` | 90 days | Exact words, shapes, and model artifacts move quickly and are easy to overfit |
| `judge` | 180 days | The concept is more durable, but examples and validity boundaries still drift |
| `advisory` | 365 days | These are human-review prompts and are not automatic gates |

The due date is computed from `Reviewed`, not checked in. A future stdlib lint
accepts an explicit `--as-of YYYY-MM-DD` for reproducible tests and uses
`datetime.date` arithmetic. It reports:

```text
STALE L1@3 enforcement=regex reviewed=2026-07-22 age=91d cadence=90d
```

Missing or malformed `Version`/`Reviewed` fields fail lint. An overdue entry is
not auto-retired; it is marked stale and requires a recorded `retain`, `revise`,
or `retire` decision. CI should fail on stale `regex` entries because they drive
deterministic flags. Stale `judge` and `advisory` entries produce a review report
until the owner decides whether to make them blocking.

New entries begin at version 1 and receive a review date backed by their
admission evidence. A repository-wide bootstrap may assign version 1 to the
current 72 entries only if the date is labeled as a baseline inventory, not
misrepresented as a fresh evidence review.

## Regex rollover

`enforcement=regex` entries have two coupled surfaces: the prose definition in
the catalog and detector behavior. They roll over through these states:

1. **Observe.** Collect fresh misses, false positives, and adversarial examples
   without changing the active rule.
2. **Candidate.** Define `L1@4` and its expected behavior. Run it in shadow
   against positive probes, synthetic false-positive fixtures, the supplemental
   known-human set when available, and the unchanged calibration suite.
3. **Decide.** Compare candidate and active revisions with counts and concrete
   changed cases. A candidate cannot be promoted by improving catches while
   silently increasing known-human flags.
4. **Activate.** Update the catalog entry, detector rule, generated projection,
   and ledger in one change. The stable ID remains `L1`; `Version` increments.
5. **Retain or retire.** If fresh evidence does not justify the candidate, record
   `retain`. If the underlying tell no longer discriminates, change enforcement
   to `advisory` or retire it through an owner-reviewed decision; do not keep a
   dead regex merely to preserve counts.

Only one revision is active in production. Shadow revisions are test data or
review artifacts, not duplicate catalog H3 entries, so `load_catalog_ids()` keeps
its unique-ID invariant.

Thresholds and regexes are frozen before the comparison cohort is scored. The
same examples cannot be used both to tune a candidate and to claim its held-out
performance. Any known-human result stays separate from the calibration
denominator.

## Stdlib implementation shape

A future change can extend `CatalogEntry` with `version` and `reviewed`, replace
the two-column `_META_HEADER`/`_META_ROW` parser pin with the four-column schema,
and render those fields in the generated registry. Changing `render_registry()`
also changes the marker-bounded GENERATED registry block in
`_shared/patterns/00-index.md`. `evals/test_catalog_projection.py` regenerates
that block and diffs it byte-for-byte, so `python3 -m aiws.catalog` regeneration
of `00-index.md` must land in the same change or the projection test goes red.
The separate `evals/test_catalog_sync.py` guard remains untouched: it pins only
the L1 replace-on-sight table against detector `TIER1`, not catalog metadata or
the generated registry.

A small `aiws.catalog_decay` module can:

- load entries through `aiws.catalog`;
- parse dates with `datetime.date.fromisoformat`;
- calculate cadence from the closed enforcement vocabulary;
- parse the JSONL ledger with `json`;
- emit stable, sorted stale-entry output;
- exit nonzero for schema errors, ledger/catalog mismatches, or stale regex
  entries.

The corresponding test uses a temporary catalog and a fixed `--as-of` date.
Wall-clock time never decides a fixture's result.

## Acceptance criteria

- Every catalog entry has a stable ID, a positive integer version, and an ISO
  review date; the active revision can be named as `<id>@<version>`.
- Behavioral changes increment the version, while formatting-only changes do
  not.
- Review evidence is append-only and distinguishes a baseline inventory date
  from a fresh evidence review.
- Cadence is deterministic by enforcement: 90 days for `regex`, 180 for
  `judge`, and 365 for `advisory`.
- A fixed `--as-of` date produces stable stale-entry output, and malformed or
  missing metadata fails loudly.
- An overdue regex entry fails lint but is not silently deleted, re-dated, or
  auto-retired.
- Regex rollover compares active and candidate behavior on positive,
  false-positive, and calibration evidence without changing the calibration
  denominator.
- Stable IDs and unique H3 entries remain compatible with current by-ID
  consumers and `00-index.md` projection.
- The implementation changes the exact two-column metadata regex pin before
  accepting four-column entries; it does not treat the new fields as a
  parser-compatible append.
- The `render_registry()` change and regenerated marker-bounded registry in
  `00-index.md` land together and keep `evals/test_catalog_projection.py` green,
  while the independent L1/`TIER1` `test_catalog_sync.py` contract is unchanged.

**Falsifiable next step:** Prototype the parser and lint on a temporary two-entry
catalog, then evaluate it with `--as-of 2026-04-02`; a regex entry reviewed on
`2026-01-01` must be reported stale at age 91 days while a judge entry with the
same date must remain current. If either result differs, the proposed cadence
contract is not implementable as specified.
