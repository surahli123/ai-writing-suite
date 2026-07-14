# OMC Code Review — four product lanes (2026-07-13)

Reviewer: oh-my-claudecode:code-reviewer, isolated worktree + git-archive extracts.
All four suites run independently: green, calibration exactly 3/8 = 38% on each.
Verdicts: narrative REQUEST-CHANGES | stylometry APPROVE-WITH-MINORS | audit APPROVE-WITH-MINORS | kb REQUEST-CHANGES (BLOCKER).
Companion Codex xhigh runs: C/D = BLOCK|BLOCK (see 2026-07-13-lanes-narrative-audit-adversarial.md); A/B capture mostly lost to a truncating pipe — surviving summary line (verbatim): "Branch B's targeted probes reproduced an INDEX/file split-brain on no-force re-ingest, loss of human INDEX edits, a shared-keyword retrieval false-pass, table-cell concatenation, Unicode slug collapse, blank entry metadata passing validation, and partial --force writes." Branch A (stylometry) structured findings did NOT survive capture; stylometry relies on the OMC hand-recomputation below.

---

All evidence gathered. Compiling final review.

## Code Review — 4 product lanes (off main @8691e88)

Ran each branch's `run_all.sh` + `unittest discover` from clean `git archive` extracts (branches held by other worktrees, can't checkout). **All 4 green; all 4 calibration lines read EXACTLY `Naive-baseline miss rate: 3/8 = 38%`.** Unittests: narrative 78, stylometry 98, audit 92, kb 85 — all OK.

---

### 1. feat/narrative-shape-category (6141dd3) → REQUEST-CHANGES

**[MAJOR] Construct/internal-contradiction — 3 of 4 narrshape PASS fixtures inject unsourced facts their own `no_fabrication` dimension defines as FAIL.**
`fixtures.json` narrshape-02/03/04 (the +72 lines). Each lists `rubric_focus:[narrative_shape_ok, meaning_preserved, no_fabrication]`, `expected_verdict:PASS`. But:
- narrshape-04 `after` adds "raised refund requests **2%**" — a number absent from `before`, presented as fact.
- narrshape-03 `after` adds "silently corrupting balances **for a month**" + "**halt the release**" — new facts; also drops before's "we fixed each one and moved on" → contradicts it (`meaning_preserved` FAIL too).
- narrshape-02 `after` adds "replica lag under load still spikes past our threshold".

`rubric.md` `no_fabrication` FAIL condition = *"`after` invents a number, source, or quote that `before` did not contain and presents it as fact"* (marked "highest-stakes dimension"). Its PASS escape is only "plausible **placeholders** the author would fill" — these are concrete real-presented facts, not bracketed placeholders. → A judge correctly applying `no_fabrication` FAILs 02/03/04, contradicting their `PASS` label. The `narrative_shape_ok` validity-condition ("surface a REAL residue") permits it, but the judge sees only before-text — no source field establishes "realness", so the fixtures train the judge to reward confident invented detail. **This is exactly the "license to inject the fault" risk the fixtures_fail doc warns about — landing in the PASS set.** Judge-only/advisory/never-gates-CI limits blast radius.
Fix: give each narrshape fixture a `source`/`brief` field carrying the residue facts (then `no_fabrication` is checkable) OR rewrite the `after`s to surface residue/ambiguity without new specifics (e.g. N4: "but the picture isn't clean — I'd want another week before calling it decisive").

**[MINOR] Unverifiable citation.** `narrative-shape.md:` "arXiv **2604.03136**", "**93.2%**", and "flat escalation ... **specifically Claude's own**". Number matches the internal improvement-plan but arXiv id + the per-model attribution are register-(c) claims I can't verify. Advisory doc → low stakes; consider hedging the id.

Positives: pattern doc's validity-condition + shipping the over-correction FAIL exemplar (`fixtures_fail.json`, not loaded by run_fixtures → calibration safe) is the correct "ship the checker with the exemplar of over-applying it" design. before/after ARE word-identical outside the structural sentence for 01/02 (verified); 03 re-weights (day-one identical only, as its note states). comms-draft wiring is at draft-shaping time (step 1), correct altitude.

---

### 2. feat/stylometric-fingerprint (13e944e) → APPROVE-WITH-MINORS

Hand-verified the math (independent recompute): population variance correct (`a b c./d e./f g h i` → var 0.6667→0.7, stdev 0.8, cv 0.27 ✓); `test_stylometry.py` expected values are genuinely hand-derived (docstring says so; 2.5/0.2/28.6/950.0 all check out — note var uses banker's rounding, 0.25→0.2, tests account for it). `test_voice_contract` recomputes profile numbers from corpus and asserts equality (advisor Q3c done right, not tautological). CJK edge confirmed: 0.19→supported, 0.20→refuse (inclusive), 0.21→refuse. Empty/single-sentence → no crash.

**[MINOR] `_NUMBER_RE` over-counts.** `stylometry.py` `_NUMBER_RE` — "v1.1"→1 figure, "2025"→1. Years documented as intended; version strings inflate testable-number density. Low impact.
**[MINOR] Sub-0.20-CJK silently drops CJK content.** `is_cjk_dominant` threshold 0.20; below it a 19%-CJK doc gets full numeric treatment but `_WORD_RE`=`[A-Za-z0-9]` never matches CJK and `。` isn't a sentence terminator → the fingerprint measures only the English fraction with no caveat, `total_words` undercounts. Threshold defensible; the silent partial-measurement deserves a note.
**[MINOR] All-empty samples → `supported:True` all-zero fingerprint** (only n<3 warning). `compute_fingerprint([""])` renders a zeros fingerprint. An explicit no-content marker (like the CJK one) would be cleaner.

Positives: honest CJK detect-and-refuse; per-genre no-pool discipline proven by `--demo` + `test_pooling_changes_the_answer` (structural assert, not echo); baseline table honestly labeled register-(c).

---

### 3. feat/audit-report-contract (5ea555c) → APPROVE-WITH-MINORS

`check_report.py` resolves tell-ids against the **LIVE** `_shared/patterns/` (`load_catalog_ids` reads the actual `*.md`, loaded 67 ids; catches `Z9 not in catalog`) — not a copy ✓. Honestly scoped structure-only (cites the advisor review). conforming/nonconforming discriminate (nonconforming → 5 violations).

**[MAJOR] Input-normalization false-rejects legitimate reports.** `_check_findings` Quote check `'"' not in qm.group(1)` hardcodes ASCII `"`. Constructed break: took `conforming.md`, replaced straight quotes with paired typographic `" "` → **REJECTED**, `['Critical finding #1: **Quote:** is not a quoted snippet', ...]` (all 4 findings). Also BOM prefix → `lead: first line is not **Biggest problem:**`. comms-polish is a prose tool whose own output/paste-from-Word easily carries smart quotes → false-reject on genuinely-conforming output. (CRLF handled fine — `splitlines` strips `\r`, verified clean.) Doesn't gate CI + fixtures use straight quotes, so not a blocker, but fix before pointing at real reports.
Fix: normalize at entry — `text = text.lstrip('\ufeff')`; Quote check accept `any(q in val for q in '"“”«»')`.

---

### 4. feat/kb-ingestion-tooling (19d1300) → REQUEST-CHANGES

`kb_validate.py` **genuinely reuses** `kb_lint` (imports `check_index_sync/check_related_entries/check_bidirectional/check_keywords`) + `smoke_test.retrieve` — not shadowed ✓. Hostile-export results: HTML entities decode correctly (`&amp;`→&, `&#39;`→', `&mdash;`→—, `&#8217;`→' — `convert_charrefs` default; my earlier concern retracted). No-heading page → TODOs, no crash. Case-dup titles ("Voice Guide"/"voice guide") → `voice-guide.md` + `voice-guide-2.md` + duplicate-topic TODO ✓.

**[BLOCKER] Title collision with an existing shipped entry silently desyncs INDEX from the file.** `kb_ingest.py` `ingest()`: `used` (Pass 1) seeded only with `NON_ENTRY_FILES` — **not** existing on-disk entries → a new page titled "Tone and Voice" slugs to `tone-and-voice.md` which already ships. Pass 3 correctly SKIPS the file (no-clobber holds). But Pass 4 index merge does `body_rows.append(_index_row(f, e["summary"], e["keywords"]))` for **every** parsed entry regardless of skip → the shipped row is overwritten with the NEW page's fields.
Constructed + confirmed: shipped `tone-and-voice.md` file = "The house tone is warm and direct" (preserved), but merged `INDEX.md` row = `| tone-and-voice.md | Kubernetes autoscaling keeps the deployment pipeline... | tone, voice, deployment, pipeline, related, entries |`. → retrieval matches "kubernetes" → opens the house-tone file → wrong answer. **The new page's content is dropped from all files** (survives only as the mismatched row). Run report says only `Skipped: tone-and-voice.md (exists)` — no collision/overwrite/content-loss warning. This is the exact "retrieval silently degrades on the company's first day" failure the tool exists to prevent.
Worse: **`kb_validate` is blind to it** — isolated clean-collision test showed identical `FAIL — 1/7` before and after the collision (desync added zero detections); `check_index_sync` verifies row↔file *existence*, nothing compares row summary/keywords against the file's `kb-entry-meta`.
Fix: (a) seed `used` with existing entry filenames in `out_dir` so a collision auto-renames to `-2.md` + duplicate-topic TODO (content preserved, no desync); (b) in Pass 4, for a skipped-existing file preserve `existing_rows[f]` instead of writing the new fields; (c) add a kb_validate check asserting INDEX row summary/keywords match the entry's meta header.

**[MINOR] Keyword pollution from structural headings.** `extract_keywords` pulled `related, entries` from a "## Related entries" heading. Exclude boilerplate headings.

Positives: honest TODO-on-genuine-gap contract; idempotent no-timestamp design; INDEX protocol header frozen/re-asserted.

---

### Cross-branch collisions (the 4 product lanes vs ledger)

The four lanes share **no files with each other** (`uniq -d` empty) — clean partition, ledger correct there. But two collisions with `feat/behavioral-evals-draft-voice` (the ledger's own branch) are **absent from its collision list (items 1-5)**:

- **[MAJOR, ledger-missed] `evals/run_all.sh` double-edited by audit + behavioral in OVERLAPPING region** (audit `@@ -8,19`, behavioral `@@ -5,22` → both ~L5-27). Hard merge conflict + `[N/4]` step renumbering. Ledger items 1-5 never mention run_all.sh.
- **[MINOR, ledger-missed] `comms-polish/SKILL.md` double-edited by audit (append §, `@@ -242`) + behavioral (frontmatter, `@@ -1,6`).** Disjoint → clean auto-merge, but unlisted; verify frontmatter stays single-line YAML (same caution ledger gave comms-draft in item 4). Note ledger item 4 covers comms-**draft** only, not comms-**polish**.

Ledger IS accurate on: narrative↔behavioral (4 files = items 1-4 ✓); stylometry↔behavioral semantic-only coupling (item 5) — verified NO textual overlap, and stylometry's new voice tests assert against `host-profile-template.md` + an in-test `CORPUS`, not behavioral's rewritten fixtures, so "follow-up, not a blocker" holds.

---

### Verdicts
1. feat/narrative-shape-category — **REQUEST-CHANGES** (fix narrshape-02/03/04 no_fabrication contradiction; rest strong)
2. feat/stylometric-fingerprint — **APPROVE-WITH-MINORS**
3. feat/audit-report-contract — **APPROVE-WITH-MINORS** (fix smart-quote/BOM normalization before real-report use)
4. feat/kb-ingestion-tooling — **REQUEST-CHANGES** (BLOCKER: collision index-desync)

Open question (low-confidence, non-blocking): narrative arXiv id `2604.03136` — can't verify here; matches internal plan, so likely fine.
