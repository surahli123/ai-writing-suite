# Wave-2 Implementation Plan — ai-writing-suite (2026-07-22)

**Status: EXECUTION-READY.** The owner approved the full scope below (Q2-A+B+C+D+E) plus
rulings Q3-1 (artifact density-budget ruling file) and Q5-1 (comms-polish progressive
disclosure). There is no open interview. Open concerns live in the RISKS section, not as
questions.

**BASE for every branch:** `main` @ `84aca44` (Wave-1 fully merged: PRs #42–#51 + #52).
Every anchor in this plan was opened and verified against this HEAD this session.

**Where the code lives.** Suite package root: `skills/ai-writing-suite/`. Inside it:
`aiws/` (stdlib Python: `text.py`, `kb/`), `_shared/` (markdown contracts + `stylometry.py`
+ `patterns/` catalog + `knowledge/` seed KB), `skills/` (the four sub-skills), `evals/`
(capability-discovery harness), and the router `SKILL.md`. The packaging validator lives
at repo-root `scripts/validate_packaging.py`; docs at repo-root `docs/`; the changelog at
`skills/ai-writing-suite/CHANGELOG.md`; the committed ignore file at repo-root `.gitignore`.

**Verified baseline (this session, `84aca44`, `bash evals/run_all.sh` from the package
root):**
```
== [1/7] unit tests ==
Ran 394 tests in 3.028s
...
Naive-baseline miss rate: 3/8 = 38% (threshold=14; calibration target 30-40%)
Calibration in target band: YES
[PASS] overstep-04-selfqa-zh refusal: as declared
Voice extraction eval: 71 passed, 0 failed.
ALL CHECKS PASSED
```
The holdout NOTE also prints on every run: `100% on the black-box holdout means the current
probes are all closed — add a HARDER verbatim probe` (this is A3's target — a standing
nag, not a failing gate).

---

## 1. Lane / wave table

Eight lanes. One stacked dependency (`w2-artifact-lane` on `w2-polish-train`); everything
else is parallel from `84aca44`.

| Lane | Branch | Items | Depends on | Diff | Merge slot |
|---|---|---|---|---|---|
| w2-eval-integrity | `feat/w2-eval-integrity` | A1, A2, A3 | — | M | parallel |
| w2-eval-additions | `feat/w2-eval-additions` | B3, B4, B5, B6 | — | M | parallel |
| w2-packaging | `feat/w2-packaging` | B7 | — | S–M | parallel |
| w2-text-seam | `feat/w2-text-seam` | B8 | — | S (likely escape-hatch) → M | parallel |
| w2-hygiene | `docs/w2-hygiene` | D1, D2, D3, D4 | — | M | parallel (anytime) |
| w2-research-designs | `docs/w2-research-designs` | E1, E2, E3, E4 | — | L | parallel (anytime) |
| w2-polish-train | `feat/w2-polish-train` | B1→B2 (stacked in-lane, sequential) | — | M–L | before artifact-lane |
| w2-artifact-lane | `feat/w2-artifact-lane` | C1, C2, C3, C4 | **w2-polish-train** | M–L | **last** (stacks on polish-train) |

**Merge order.**
1. The six parallel lanes (`w2-eval-integrity`, `w2-eval-additions`, `w2-packaging`,
   `w2-text-seam`, `w2-hygiene`, `w2-research-designs`) — any order among themselves; their
   file sets are disjoint (verified, §RISKS file-overlap matrix). Hygiene and
   research-designs are docs-only and may land at any point.
2. `w2-polish-train` — edits `comms-polish/SKILL.md` and `comms-draft/SKILL.md`. No other
   lane writes those two files, so it may also land inside the parallel window; it only
   needs to be merged **before** `w2-artifact-lane`.
3. `w2-artifact-lane` — branches from `w2-polish-train`'s merged state and edits
   `comms-polish/SKILL.md` too. Merges last.

**Why the stack (A→ nothing here; polish-train → artifact-lane).** Both `w2-polish-train`
(B1 voice-lookup extraction, B2 progressive disclosure) and `w2-artifact-lane` (C3 routes
edit mode to a new reference) edit `comms-polish/SKILL.md`. Building artifact-lane on
polish-train's branch means C3 inserts against the already-slimmed file instead of fighting
B2's section moves at merge time. This is the same load-bearing-stack rationale Wave-1 used
for A→H→I/J.

**Why the rest are parallel.** Their write sets are disjoint (see the file-overlap matrix
in RISKS). The two eval lanes are deliberately kept apart: `w2-eval-integrity` owns
`smoke_test.py` / `SMOKE-TEST.md` / `test_untrusted_content_contract.py` /
`holdout_adversary.py`; `w2-eval-additions` owns `test_router_*` (new) /
`test_kb_retrieval_protocol.py` / the draft-coupling test (new) / `test_text_seam.py`. No
file is written by both.

---

## 2. Hard Constraints Block (HCB) — post-Wave-1

*Repeated verbatim into every SPEC because executors do not share context. Obey all of it.*

1. Branch from `main` @ `84aca44` (or, for `w2-artifact-lane`, from the merged
   `feat/w2-polish-train`). Work ONLY in your assigned worktree/branch. Never commit to
   `main`. Never edit a file outside your spec's "in scope" list, and never edit another
   lane's files.
2. **Stdlib-only Python.** No new dependencies, no `pip install`, no network calls in tests.
   `aiws/` imports from neither `evals/` nor `tools/`.
3. **INDEX.md retrieval semantics are FROZEN.** Never edit
   `_shared/knowledge/INDEX.md`, the five seed KB entry files (`audience.md`, `clarity.md`,
   `revision.md`, `structure.md`, `tone.md`), or existing eval fixture VALUES to make a
   check pass. Adding a NEW schema FIELD or a NEW fixture is allowed only where a spec says
   so explicitly (A1 edits `SMOKE-TEST.md`, which is a test-chain doc, not INDEX/KB
   semantics; C4 adds one `detector_blind` fixture; these are called out per-lane).
4. **Calibration must stay exactly `3/8 = 38%`.** Run `bash evals/run_all.sh` from the
   package root BEFORE you change anything and AFTER; paste both tails into your task
   report. Both must show `ALL CHECKS PASSED`,
   `Naive-baseline miss rate: 3/8 = 38%`, `Calibration in target band: YES`,
   `overstep-04-selfqa-zh refusal: as declared`, and `Voice extraction eval: 71 passed`.
5. The AI-tell **detector / checker is a regression signal, never a quality KPI.** Do not
   tune detector or holdout-checker scoring to move numbers on existing fixtures. Eval
   lanes ADD probes and pins; they never change what an existing checker scores.
6. **Match existing conventions.** Each spec names one exemplar file — read it and copy its
   structure, naming, and docstring register.
7. Commit in small logical chunks; each message describes the change's purpose. **No commit
   trailers.** Never push.
8. **No fake completion.** No `TODO`/placeholder, no `test.skip`/`.only`, no stub tests, no
   unimplemented branch. If you discover the spec's premise is wrong, STOP and write
   `BLOCKED: <one-line reason + evidence>` to your task report — do not improvise a
   different design.
9. Never claim a check passed without pasting its command output.
10. **Do not touch `CHANGELOG.md` from any lane except `w2-hygiene`.** Wave-2 code lanes
    ship no changelog entries (hygiene owns the changelog; per-lane edits would collide).
11. **Preserve the exactly-once untrusted-content reference.** Every `SKILL.md`
    (`test_untrusted_content_contract.py` asserts `body.count("_shared/untrusted-content.md")
    == 1`). Lanes that edit a `SKILL.md` (B1, B2, C3) must not add, remove, or duplicate
    that reference line.

---

## 3. Per-lane verification gate (used later by reviewers)

A lane passes only when ALL of these hold, with pasted evidence:

- **Full suite green:** from `skills/ai-writing-suite/`, `bash evals/run_all.sh` prints
  `ALL CHECKS PASSED` and exits 0.
- **Calibration unchanged:** the tail still shows `Naive-baseline miss rate: 3/8 = 38%` and
  `Calibration in target band: YES`.
- **Refusal + voice invariants intact:** `overstep-04-selfqa-zh refusal: as declared` and
  `Voice extraction eval: 71 passed, 0 failed` (unless the spec legitimately raises the 71 —
  none in Wave-2 does).
- **Item regression tests green:** the specific new test names in the spec's test plan pass.
- **Diff scope clean:** `git diff --stat 84aca44` (or the lane's base) lists only the
  spec's in-scope files.
- **No fake-completion patterns** on the diff (`grep -rnE
  'TODO|FIXME|\.skip\(|\.only\(|raise NotImplementedError|pass  # stub'` on changed files is
  empty).

---

## SPEC — Lane w2-eval-integrity (A1, A2, A3): close the three eval-validity gaps

**Goal.** Three independent eval-integrity fixes: (A1) replace the smoke test's hardcoded
tie special-case with a doc-driven per-case expected-files marker; (A2) pin the
untrusted-content contract's *body* so gutting it goes red; (A3) append one genuinely harder
verbatim probe to the black-box holdout.

**Why (1–2 lines).** Each is a place where the suite can go green on a weakened artifact:
`smoke_test.py` special-cases Case-1 by index (`if i == 1`) instead of reading the doc;
`test_untrusted_content_contract.py` never checks the contract's rules survive; and the
holdout prints "all probes are closed — add a harder one" on every run.

**In scope.**
- `skills/ai-writing-suite/evals/smoke_test.py` (A1: parser + drop the index special-case)
- `skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md` (A1: add one explicit
  expected-files line per case — a test-chain doc, NOT INDEX/KB semantics)
- `skills/ai-writing-suite/evals/test_untrusted_content_contract.py` (A2: add a body-phrase
  pin)
- `skills/ai-writing-suite/evals/fixtures/holdout_adversary.py` (A3: one appended probe)

**Out of scope.** `_shared/knowledge/INDEX.md`, the five seed KB entries, `retrieval.py`,
`_shared/untrusted-content.md` (A2 pins its content, never edits it), the detector /
checker scoring logic (A3 appends a probe, never changes what a checker scores).

**Verified current state (`84aca44`).**
- `smoke_test.py:103-133` — the loop hardcodes the Case-1 tie by index:
  `expected_files = (["clarity.md", "revision.md"] if i == 1 else [c["entry"]])`, then
  `if i == 1: entry_ok = sorted(files or []) == sorted(expected_files)` else
  `entry_ok = files == expected_files`. The parser `load_cases()` (`smoke_test.py:42-70+`)
  already extracts `(query, expected_entry, expected_passage)` by regex-anchoring on
  `**Expected entry(?: retrieved)?:** \`...\`` / `**Query...:**` / `**Expected passage...:**`
  blockquotes.
- `SMOKE-TEST.md` — five cases. Case 1 (line 71) says `**Expected entry retrieved:**
  \`clarity.md\` (must be among the results)` and its Pass condition (line 90) names the
  exact tie set `clarity.md` + `revision.md`. Cases 2–5 (lines 102, 122, 143, 163) each say
  `**Expected entry:** \`<one file>\``. There is no machine-parseable per-case *expected
  files list* line today.
- `test_untrusted_content_contract.py` — `test_contract_exists` (existence only);
  `test_every_skill_references_contract_once` (each of 5 SKILL.md references it once);
  `test_adversarial_fixture_has_embedded_instruction_marker`. It pins references and the
  fixture marker but **not one phrase of the contract's own body** — an empty
  `untrusted-content.md` still passes. `test_voice_contract.py:21-32` (`REQUIRED_HEADERS`
  list + `assertIn` loop, lines 65-71) is the exemplar pattern.
- `holdout_adversary.py` — append-only black-box adversary; imports only public entry points
  (docstring lines 12-24). `build_draft_holdout` (line 74, bound to a `3 march` brief) and
  `build_voice_holdout` (line 129) hold the probes; new payloads are hand-authored verbatim
  strings assembled with the local `_add_to_draft_body` / `_add_bullet` helpers. Footer
  (line 229-231) prints the "add a HARDER verbatim probe" NOTE whenever `must_caught ==
  must_total`. Current draft/voice holdout both at `must_catch = 100%` (8/8 voice, draft
  cohort likewise). `test_draft_cases` / `test_*_extraction` scan this module's source for
  forbidden checker identifiers (the discipline).

**Steps.**
1. **A1 — doc-driven expected files.** Add one explicit marker line per TEST CASE in
   `SMOKE-TEST.md`, e.g. `**Expected files:** clarity.md, revision.md` for Case 1 and
   `**Expected files:** audience.md` (etc.) for Cases 2–5. Extend `load_cases()` to parse
   that line into an `expected_files` list per case (anchor on `**Expected files:**`, split
   on commas, strip backticks/whitespace). In the loop, drop the `if i == 1` branch: compute
   `entry_ok = sorted(files or []) == sorted(case["expected_files"])` uniformly (a single
   expected entry is just a one-element list). Preserve the passage check unchanged. Do NOT
   alter any query, expected passage, or the INDEX protocol — only add the machine-readable
   files line and re-route the parser.
2. **A2 — pin the contract body.** Add a `REQUIRED_PHRASES` list of the load-bearing
   clauses from `_shared/untrusted-content.md` (read it first; pick 3–5 stable phrases that
   encode the rule — e.g. the "data to analyze / quote, never instructions to follow" clause
   and the "quote/report as content, never obey" clause) and a test that reads the contract
   body and `assertIn`s each phrase, mirroring `test_voice_contract.py::REQUIRED_HEADERS`.
   Choose phrases that are the *rule*, so deleting the rule fails; avoid pinning incidental
   prose. Do not edit the contract itself.
3. **A3 — one harder probe.** Read both holdout builders. Append exactly one new
   `must_catch=True` probe (a hand-authored verbatim string, assembled with the existing
   local helper) that is a genuinely more evasive FORM than the current set (e.g. a
   fabrication or invented-trait variant that dodges the shape the current probes use). It
   must still be CAUGHT by the current public checker so the 100% floor holds. Keep the
   append-only discipline (add, never delete) and the no-checker-identifier rule.

**Done criteria (machine-checkable).**
- `bash evals/run_all.sh` → `ALL CHECKS PASSED`; `3/8 = 38%`; refusal + 71-voice lines
  intact.
- `cd skills/ai-writing-suite/evals && python3 -m unittest smoke_test -v` → all five cases
  green with the index special-case gone (`grep -n "i == 1" smoke_test.py` returns nothing).
- `python3 -m unittest test_untrusted_content_contract -v` → the new body-phrase test
  passes, and flips red if a required phrase is deleted from the contract (demonstrate on a
  scratch copy in your report, then revert).
- The holdout footer still prints `must_catch ... = 100%` with the new probe included, and
  the run stays green.
- `git diff --stat 84aca44` lists only the four in-scope files.

**Test plan.** A1: extend the existing `smoke_test` cases (they already run under the
`kb_smoke` capability). A2: model on `test_voice_contract.py`. A3: the holdout runs inside
`run_all.sh`; the new probe is verified by the footer line + a green suite.

**Escape hatch.** A3 — if the harder probe you construct ESCAPES the current checker, you
have found a genuine blind spot. STOP and write `BLOCKED: holdout probe <id> escapes —
genuine checker blind spot, needs a scoring fix outside w2-eval-integrity` (this lane is
eval-only; it must not change checker scoring semantics). A1 — if a case's expected files
cannot be expressed as a static list without re-deriving the INDEX tie (i.e. the doc and the
live tie disagree), STOP and write `BLOCKED: SMOKE-TEST expected-files line conflicts with
frozen INDEX tie at <case>`.

**HCB (obey all):** branch from `84aca44`, worktree only, never `main`/other lanes ·
stdlib-only, no deps/network · INDEX/KB FROZEN (editing `SMOKE-TEST.md` is allowed for A1;
never touch INDEX or seed entries) · run `bash evals/run_all.sh` before+after, paste both
tails, keep `3/8 = 38%` + refusal + 71-voice · checker/detector is a regression signal, not
a KPI · match the exemplar file · small commits, no trailers, never push · no CHANGELOG edit
· preserve exactly-once untrusted-content refs · no TODO/skip/stub; STOP + `BLOCKED: …` if
the premise breaks · no claim without output.

---

## SPEC — Lane w2-polish-train (B1, B2): voice-lookup extraction + progressive disclosure

**STACKED, sequential in-lane: do B1, then B2, on the same branch.** Both edit
`comms-polish/SKILL.md`; doing them in sequence in one lane avoids an intra-file merge.

**Goal.** (B1) Extract the drifted voice-profile-lookup protocol into ONE canonical
`_shared/voice-lookup.md`, referenced by both `comms-polish` and `comms-draft`, resolving
the drift toward the canonical rule. (B2, = owner ruling Q5-1) Move `comms-polish/SKILL.md`'s
two biggest conditionally-used chunks behind `references/` with CONDITIONAL pointers, per the
Agent Skills spec (load-on-demand, keep the main file lean).

**Why (1–2 lines).** The banner-rejection rule drifted: `comms-polish` rejects a
`> SAMPLE PROFILE.`-carrying file only in its legacy-fallback branch, while `comms-draft`
and the canonical `voice-profile.md` rule reject it in *either* location. And
`comms-polish/SKILL.md` is 437 lines with two large chunks (worked examples;
detect/review-only contract detail) that most runs never need in context.

**In scope.**
- NEW `skills/ai-writing-suite/_shared/voice-lookup.md` (the canonical lookup protocol)
- `skills/ai-writing-suite/skills/comms-polish/SKILL.md` (B1: Voice Matching references the
  new file, drift resolved; B2: two chunks moved behind references + pointers)
- `skills/ai-writing-suite/skills/comms-draft/SKILL.md` (B1: Inputs voice block references
  the new file)
- NEW `skills/ai-writing-suite/skills/comms-polish/references/before-after-examples.md`
  (B2: the moved worked-examples block)
- NEW `skills/ai-writing-suite/skills/comms-polish/references/audit-report-contract.md`
  (B2: the moved contract *body* detail)

**Out of scope.** The 15-header voice-profile contract in `_shared/voice-profile.md` (do NOT
change headers — `test_voice_contract.py` guards them). `voice-onboard/SKILL.md` (its Step 5
banner rule is already canonical; leave it). The pattern-catalog and scenario-presets
sections of `comms-polish/SKILL.md` (`test_catalog_projection.py` / `test_scenario_presets.py`
read them). The `### Audit Report Contract` heading, its section ordering, and its
mode-firewall sentence (see the B2 constraint below).

**Verified current state (`84aca44`).**
- **The drift (B1).** Canonical rule — `_shared/voice-profile.md:79-82`: "**Consumers
  (`comms-polish`, `comms-draft`) must treat any file carrying this `> SAMPLE PROFILE.`
  banner as NO profile** — degrade to inferred voice and make the Q8 voice-onboard offer,
  exactly as if the file were absent." `comms-draft/SKILL.md:67-70` already matches: "Any
  profile file carrying the `> SAMPLE PROFILE.` banner — **in `voice-profiles/` or the legacy
  path** — counts as NO profile." `comms-polish/SKILL.md:108-112` gates the banner ONLY
  inside the legacy-fallback branch ("Directory absent or empty → fall back to the legacy
  single file ... still gated by the `> SAMPLE PROFILE.` banner ... A profile is valid only
  with the banner absent"); the per-genre `<state>/voice-profiles/*.md` selection (lines
  90-107) never mentions rejecting a banner-carrying file. That is the drift to resolve
  toward the canonical "ANY carrying file, either location, is invalid."
- **The chunks (B2).** `comms-polish/SKILL.md` is 437 lines. Two genuinely conditional,
  large blocks: **"## Before And After Examples"** (lines 253-315, ~63 lines — illustrative;
  no rewrite strictly needs them inline; no test asserts their presence) and the detail under
  **"### Audit Report Contract"** (lines 378-437, ~60 lines — the section itself says "This
  contract governs `detect` and `review` output only"). The scenario/genre routing detail is
  already externalized to `references/scenario-presets.md` (SKILL.md lines 18, 56, 190-193
  only *point* at it), so it is NOT a candidate.
- **B2 TEST CONSTRAINT (load-bearing).** `evals/audit_report/test_report_contract.py::
  ModeFirewall` (lines 130-144) opens `comms-polish/SKILL.md` and requires: the literal
  heading `### Audit Report Contract` is present; `## Rewrite Workflow` and `## File Edits`
  both precede it; and the text from that heading onward contains both "`rewrite` and `edit`"
  and "are unchanged by it". Moving the whole contract section out breaks this test.

**Steps.**
1. **B1.** Write `_shared/voice-lookup.md` as the single canonical lookup protocol: the
   source-order precedence (learned per-genre profile → pasted sample → inferred), the
   directory-list + normalized-exact selection rules, the graceful-degradation + Q8 offer
   budget, and — resolved toward the canonical rule — "**any file carrying the
   `> SAMPLE PROFILE.` banner counts as NO profile, whether it sits in
   `<state>/voice-profiles/` or the legacy `_shared/voice-profile.md` path.**" Follow the
   "referenced, never copied" register of `_shared/self-improvement.md`.
2. **B1.** In `comms-polish/SKILL.md` "## Voice Matching", replace the inline lookup detail
   with a reference to `_shared/voice-lookup.md` (keep the section, cite the file, do not
   paste its body), and make sure the resolved text no longer restricts the banner check to
   the legacy branch. In `comms-draft/SKILL.md` "## Inputs" voice bullet, reference the same
   file. Keep every existing `_shared/untrusted-content.md` reference exactly once in each
   file (HCB #11). Anchor edits by heading / quoted string, never by bare line number.
3. **B2.** Move "## Before And After Examples" (the three worked examples) to
   `references/before-after-examples.md`; in `comms-polish/SKILL.md` leave a one-line
   CONDITIONAL pointer where the section was — e.g. "For worked before/after examples, read
   `references/before-after-examples.md`."
4. **B2.** Move the field-by-field contract DETAIL (the four-part Quote/Tell/Why/Fix shape,
   the tier definitions, the byte-literal conformance rules — SKILL.md sections numbered 1–4
   under the contract) to `references/audit-report-contract.md`. In `comms-polish/SKILL.md`
   **keep**: the `### Audit Report Contract` heading (still after Rewrite Workflow and File
   Edits), the two firewall sentences ("This contract governs `detect` and `review` output
   only." and "`rewrite` and `edit` are unchanged by it"), and a CONDITIONAL pointer ("Full
   field-by-field contract in `references/audit-report-contract.md` — read it when producing
   `detect`/`review` output"). This satisfies `ModeFirewall`. (The existing pointer at
   SKILL.md:436-437 to `references/audit-report-format.md`, the worked example, stays.)
5. Justify the two chosen chunks in the spec commit message: both are conditional (examples
   are optional illustration; the contract detail is detect/review-only), they are the two
   largest such blocks, and the scenario-routing detail is already externalized.

**Done criteria (machine-checkable).**
- `bash evals/run_all.sh` → `ALL CHECKS PASSED`; `3/8 = 38%`; refusal + 71-voice intact.
- `python3 -m unittest audit_report.test_report_contract -v` (from `evals/`) → `ModeFirewall`
  passes (heading present, ordering held, firewall phrases present).
- `wc -l skills/ai-writing-suite/skills/comms-polish/SKILL.md` is materially lower (~320–340,
  down from 437) and both new `references/*.md` exist.
- `grep -c "_shared/untrusted-content.md" comms-polish/SKILL.md` and the `comms-draft` file
  each return 1.
- `_shared/voice-lookup.md` exists, states the "any banner-carrying file, either location =
  NO profile" rule, and both SKILL.md files reference it.
- `git diff --stat 84aca44` lists only the five in-scope files.

**Test plan.** Prose/reference lane guarded by existing tests: `test_report_contract.py`
(contract heading/ordering/firewall), `test_voice_contract.py` (headers), `test_untrusted_
content_contract.py` (exactly-once refs), `test_catalog_projection.py` /
`test_scenario_presets.py` (untouched sections). A tiny optional tripwire asserting
`voice-lookup.md` exists + is referenced by both skills is welcome, modeled on
`test_voice_contract.py`, but `run_all.sh` green is the gate.

**Escape hatch.** If resolving the drift toward "any banner-carrying file is invalid" would
change a shipped behavior a test depends on (it should not — the canonical rule is already
in `comms-draft` and `voice-profile.md`), STOP and write `BLOCKED: banner-rule
canonicalization changes tested behavior at <path:line>`. If moving the Audit Report
Contract body forces removing the heading or a firewall phrase to keep the file coherent,
STOP and write `BLOCKED: B2 move collides with ModeFirewall — cannot keep heading+firewall
in place` rather than deleting them.

**HCB (obey all):** branch from `84aca44`, worktree only, never `main`/other lanes ·
stdlib-only · INDEX/KB FROZEN · run `bash evals/run_all.sh` before+after, keep `3/8 = 38%` +
refusal + 71-voice · detector/checker is a regression signal, not a KPI · match the exemplar
(`self-improvement.md` referenced-not-copied register) · small commits, no trailers, never
push · no CHANGELOG edit · preserve exactly-once untrusted-content refs · no TODO/skip/stub;
STOP + `BLOCKED: …` if the premise breaks · no claim without output.

---

## SPEC — Lane w2-eval-additions (B3, B4, B5, B6): four deterministic eval pins

**Parallel-safe, evals-only. Must not touch any file `w2-eval-integrity` touches** (it owns
`smoke_test.py`, `SMOKE-TEST.md`, `test_untrusted_content_contract.py`,
`holdout_adversary.py`).

**Goal.** Four static/deterministic pins: (B3) router routing-decision fixtures; (B4)
`retrieve()` zero-overlap negative tests; (B5) a coupling test that comms-draft's SKILL.md
prose and `run_draft_cases.py`'s constants agree; (B6) extend `StylometrySyncPin` to pin
`aiws.text._CJK_RE` identical to `_shared/stylometry.py`'s copy.

**Why (1–2 lines).** Each closes an unguarded surface: the router's decision table has no
test; `retrieve()`'s zero-overlap path is untested; `run_draft_cases.py`'s hand-copied
acceptance-criteria constants can silently drift from the SKILL.md they claim to mirror; and
the two `_CJK_RE` copies have no sync-pin (only `_SENT_SPLIT` is pinned).

**In scope.**
- NEW `skills/ai-writing-suite/evals/test_router_routing.py` (B3)
- `skills/ai-writing-suite/evals/test_kb_retrieval_protocol.py` (B4: add negative tests)
- NEW `skills/ai-writing-suite/evals/fixtures/test_draft_criteria_coupling.py` (B5)
  *(or add a class to `evals/fixtures/test_draft_cases.py` — either is fine; a new file keeps
  the diff isolated)*
- `skills/ai-writing-suite/evals/test_text_seam.py` (B6: add a `_CJK_RE` pin to
  `StylometrySyncPin`)

**Out of scope.** The router `SKILL.md`, `comms-draft/SKILL.md`, `retrieval.py`,
`aiws/text.py`, `_shared/stylometry.py` — B3/B4/B5/B6 are all read-only against production
code; they only ADD tests. Do NOT change any production behavior to make a new test pass.
**Do not edit `smoke_test.py` (that is B4's lane-separation twin — negative retrieval tests
go in `test_kb_retrieval_protocol.py`, NOT `smoke_test.py`).**

**Verified current state (`84aca44`).**
- **B3.** Router `SKILL.md:34-47` — the "How to route (executable)" decision table maps
  intents to sub-skills, plus the "Precedence rule for mixed requests" (line 41): any
  request adding substance routes to `comms-draft`, even "polish this and add a risks
  section"; pure rewording → `comms-polish`; "translate this, no other change" → say so and
  pick the closest fit (line 49). These phrasings are the fixtures.
- **B4.** `test_kb_retrieval_protocol.py` currently has exactly two positive tests:
  `test_summary_heavy_entry_outscores_incidental_keyword_entry` (asserts
  `retrieve("alpha beta", entries) == (["summary.md"], (2, 2))` — confirming the shipped
  **union-primary / summary-tiebreak** scoring the owner ruled canonical, NOT keyword-first)
  and `test_full_tie_returns_both_filenames` (`== (["first.md","second.md"], (2, 1))`). There
  is no zero-overlap / no-match test. The shipped `retrieve()` returns an empty result on
  zero total overlap (its zero-overlap guard).
- **B5.** `run_draft_cases.py:52` — `CRITERIA_DIMENSIONS = ("style", "format", "length",
  "content integration", "depth")`, with the comment (lines 49-51) "The five
  acceptance-criteria dimensions comms-draft/SKILL.md step 1 requires." The source prose is
  `comms-draft/SKILL.md:115-119` (Drafting Workflow step 1), which names **style / format /
  length / content integration / depth**. Today only a comment ties them; nothing fails if
  they drift.
- **B6.** `test_text_seam.py::StylometrySyncPin` (line 157) has ONE pin,
  `test_sent_split_pattern_and_flags_identical_to_stylometry` (line 164), comparing
  `aiws.text.SENT_SPLIT` to `stylometry._SENT_SPLIT` by `(pattern, flags)`. `aiws/text.py:62`
  defines `_CJK_RE = re.compile("[぀-ヿ㐀-䶿一-鿿가-힯ｦ-ﾟ]")`; `_shared/stylometry.py:175`
  defines its own `_CJK_RE` (identical pattern + flags, verified equal this session). The
  `_CJK_RE` pair is unpinned — that is B6's target. The threshold/refusal boundary is already
  behaviorally pinned (`SegmentContract` lines 147-154).

**Steps.**
1. **B3.** Add `test_router_routing.py` (stdlib `unittest`): read `SKILL.md`, and for a table
   of `(request phrasing → expected sub-skill)` pairs derived from the router prose
   (polish-only → comms-polish; new page / new section / mixed polish+add → comms-draft; KB
   question → comms-qa; "learn my voice" → voice-onboard; the mixed-precedence example
   "polish this and add a risks section" → comms-draft), assert the router text encodes each
   routing (anchor on the decision-table rows and the precedence paragraph — a static parse
   of the prose, NOT a live-model classification). Follow `test_voice_contract.py`'s
   file-reading assertion style.
2. **B4.** Add to `test_kb_retrieval_protocol.py`: `test_zero_overlap_returns_empty` (a query
   sharing no term with any entry → empty result / no file) and a `test_no_match_*` variant,
   built with hand-made `entries` dicts in the `load_index` shape
   (`{"file","summary","keywords","summary_kw"}`), never reading INDEX.md. Follow the two
   existing tests exactly.
3. **B5.** Add `test_draft_criteria_coupling.py`: read `comms-draft/SKILL.md`, parse the five
   acceptance-criteria dimension names out of the step-1 prose (anchor on the "Derive per-task
   acceptance criteria" heading and the bolded dimension labels), import
   `CRITERIA_DIMENSIONS` from `run_draft_cases.py`, and assert the two sets match exactly
   (heading/string-anchored parse). This makes a future edit to either side that desyncs the
   list go red.
4. **B6.** In `StylometrySyncPin`, add `test_cjk_pattern_and_flags_identical_to_stylometry`
   mirroring the existing SENT_SPLIT pin: import `_CJK_RE` from `aiws.text` and from
   `stylometry`, assert `(pattern, flags)` equal. Do not touch either `_CJK_RE` definition.

**Done criteria (machine-checkable).**
- `bash evals/run_all.sh` → `ALL CHECKS PASSED`; `3/8 = 38%`; refusal + 71-voice intact.
- From `evals/`: `python3 -m unittest test_router_routing -v`,
  `python3 -m unittest test_kb_retrieval_protocol -v` (4 tests now),
  `python3 -m unittest fixtures.test_draft_criteria_coupling -v`, and
  `python3 -m unittest test_text_seam -v` (StylometrySyncPin now has 2 pins) all pass.
- Each new test is demonstrably able to go red (e.g. B5 fails if you locally rename a
  dimension in `CRITERIA_DIMENSIONS`; B6 fails if you locally perturb one `_CJK_RE` — show
  the red on a scratch copy in your report, then revert).
- `git diff --stat 84aca44` lists only the (up to) four in-scope files.

**Test plan.** All four follow `test_voice_contract.py` (read a file, assert on parsed
content) or `test_kb_retrieval_protocol.py` (hand-built inputs, exact-output asserts). They
run under the `unit_tests` capability (unittest discovery over `evals/`).

**Escape hatch.** B5 — if the SKILL.md step-1 prose cannot be parsed into exactly the five
dimension names without ambiguity, STOP and write `BLOCKED: comms-draft criteria prose not
statically parseable — <what you saw>` rather than loosening the assertion to a substring
check. B6 — if the two `_CJK_RE` copies are NOT identical at your HEAD (they were this
session), that is a real drift: STOP and write `BLOCKED: _CJK_RE already drifted between
aiws.text and stylometry` (a drift the pin should surface, not a test to weaken).

**HCB (obey all):** branch from `84aca44`, worktree only, never `main`/other lanes ·
stdlib-only · INDEX/KB FROZEN; ADD tests only, never change production code to green a new
test · run `bash evals/run_all.sh` before+after, keep `3/8 = 38%` + refusal + 71-voice ·
detector/checker is a regression signal, not a KPI · match the exemplar file · small commits,
no trailers, never push · no CHANGELOG edit · no TODO/skip/stub; STOP + `BLOCKED: …` if the
premise breaks · no claim without output.

---

## SPEC — Lane w2-packaging (B7): 4th manifest + root-router check + validator self-test

**Goal.** Teach `scripts/validate_packaging.py` about the 4th documented manifest
(`.agents/plugins/marketplace.json`, the Codex root marketplace), add a root-router manifest
check, and add a self-test proving the validator itself goes red on a broken manifest.

**Why (1–2 lines).** The validator checks only 3 of the 4 documented manifests, so the Codex
root marketplace can rot silently, and the validator has no test of its own — a regression
in the validator would be invisible.

**In scope.**
- `scripts/validate_packaging.py` (add the 4th manifest to the checks; add a root-router
  check; adjust the name-field count expectation)
- NEW `skills/ai-writing-suite/evals/test_validate_packaging.py` (self-test — lives under
  `evals/` so it runs in the `unit_tests` capability under `run_all.sh`)

**Out of scope.** The manifest JSON files themselves (they are correct — the validator just
doesn't check the 4th). `test_skill_manifests.py` (the validator imports its `_frontmatter`
predicate; do not fork that logic). The eval fixtures / detector / KB.

**Verified current state (`84aca44`).**
- `scripts/validate_packaging.py:48-53` — `check_manifests` builds a 3-entry dict:
  `marketplace` = `.claude-plugin/marketplace.json`, `claude-plugin` =
  `.claude-plugin/plugin.json`, `codex-plugin` = `.codex-plugin/plugin.json`. It does NOT
  include `.agents/plugins/marketplace.json`. Line 78: `if len(names) < 4: _fail(...)` — the
  current 3 files yield exactly 4 name fields. Line 98-99: `check_frontmatter` requires
  `>= 4 SKILL.md`.
- The 4th manifest EXISTS on disk: `.agents/plugins/marketplace.json` (393 bytes), documented
  in `docs/packaging.md:11-18` as the Codex root marketplace whose
  `plugins[].source = {source:"local", path:"./skills/ai-writing-suite"}`.
- There is NO test for `validate_packaging.py` today; it is invoked directly in CI
  (`.github/workflows/ci.yml`), separate from `run_all.sh`.

**Steps.**
1. Add `.agents/plugins/marketplace.json` to the `manifests` dict in `check_manifests`
   (label e.g. `agents-marketplace`). Parse it, pull its `name` and `plugins[0].name` into
   the `names` map, and RAISE the `len(names) < 4` threshold to match the new expected count
   (now up to 6 name fields across 4 files). Keep the "all names agree / all versions agree"
   invariants.
2. Add a **root-router manifest check**: assert each root marketplace's `plugins[].source`
   resolves to the suite tree (`./skills/ai-writing-suite`, in whichever shape each host
   uses per `docs/packaging.md:15,17`), so a manifest pointing at a wrong/missing source path
   fails. Keep it stdlib-only and path-existence based (do not fetch anything).
3. Add `evals/test_validate_packaging.py`: import the validator module (add `scripts/` to
   `sys.path`), assert it returns 0 / prints OK on the real tree, and — the load-bearing part
   — assert it returns non-zero when pointed at a temporarily-mutated manifest (e.g. a
   `tmp_path` copy with a mismatched name or a missing 4th manifest). Model the "must go red"
   half on `test_draft_cases.py::test_declawed_bad_draft_exits_nonzero`.

**Done criteria (machine-checkable).**
- `python3 scripts/validate_packaging.py` → exits 0, prints the OK line, and its checks now
  cover 4 manifests (verify the 4th is parsed — e.g. temporarily corrupt
  `.agents/plugins/marketplace.json` on a scratch copy and confirm the validator fails, then
  revert).
- `bash evals/run_all.sh` → `ALL CHECKS PASSED`; `3/8 = 38%`; refusal + 71-voice intact; the
  new `test_validate_packaging` is discovered and green under `unit_tests`.
- `cd skills/ai-writing-suite/evals && python3 -m unittest test_validate_packaging -v` — the
  OK-on-good-tree and red-on-broken-manifest tests both pass.
- `git diff --stat 84aca44` lists only `scripts/validate_packaging.py` +
  `evals/test_validate_packaging.py`.

**Test plan.** The validator self-test uses `tempfile`/`tmp_path`-style scratch copies of the
manifests to prove red-on-break without editing the real manifests. Import the validator's
functions rather than shelling out, so a failure is a Python assertion, not a parsed string.

**Escape hatch.** If importing `scripts/validate_packaging.py` from under `evals/` proves
fragile (it in turn imports `test_skill_manifests` by manipulating `sys.path`), STOP and
write `BLOCKED: validator not cleanly importable from evals/ — <error>` and propose keeping
the self-test in `scripts/` invoked by CI instead — do NOT duplicate the validator's logic
into the test.

**HCB (obey all):** branch from `84aca44`, worktree only, never `main`/other lanes ·
stdlib-only, no deps/network · INDEX/KB FROZEN · run `bash evals/run_all.sh` before+after,
keep `3/8 = 38%` + refusal + 71-voice · detector/checker is a regression signal, not a KPI ·
match the exemplar file · small commits, no trailers, never push · no CHANGELOG edit · no
TODO/skip/stub; STOP + `BLOCKED: …` if the premise breaks · no claim without output.

---

## SPEC — Lane w2-text-seam (B8): unify the remaining stylometry primitives (or document the mirror)

**Goal.** Remove the last duplicated primitives: `_shared/stylometry.py` keeps its own
`_CJK_RE` and `_SENT_SPLIT` copies. Spec the deepening — stylometry imports the primitives
from `aiws.text` (single source), all existing behavior pins stay green, zero band movement.
**If import-direction constraints block it, take the escape hatch: document the seam as
intentionally mirrored with B6's sync-pin as the guard, and STOP.**

**Why (1–2 lines).** Post-Wave-1 the detector and voice-extraction already route through
`aiws.text`; the only remaining duplication is stylometry's private regex copies. Single-
sourcing them (if portability allows) removes a drift surface.

**In scope.**
- `skills/ai-writing-suite/_shared/stylometry.py` (import the primitives from `aiws.text`, OR
  add a comment documenting the intentional mirror)
- `skills/ai-writing-suite/aiws/text.py` (only if a primitive stylometry needs is not yet
  exported — e.g. expose a `_SENT_SPLIT` counterpart)

**Out of scope.** `evals/test_text_seam.py` — that file is owned by lane `w2-eval-additions`
(B6 adds the `_CJK_RE` pin there). B8 must NOT edit `test_text_seam.py`. The detector,
calibration fixtures, INDEX/KB. Do not move any band.

**Verified current state (`84aca44`).**
- `_shared/stylometry.py:139` `_SENT_SPLIT = re.compile(r"[.!?]+(?:\s+|$)")`; `:175`
  `_CJK_RE = re.compile("[぀-ヿ㐀-䶿一-鿿가-힯ｦ-ﾟ]")`. The module imports only stdlib
  (`math`, `re`, `sys`) — **zero intra-repo imports**.
- `aiws/text.py` exports `SENT_SPLIT` (no underscore; the `StylometrySyncPin` imports it) and
  `_CJK_RE` (line 62, identical pattern+flags to stylometry's, verified equal). It has NO
  `_SENT_SPLIT` constant — its sentence splitter is exposed as `SENT_SPLIT` /
  `split_sentences`.
- **The portability constraint (decisive).** `StylometrySyncPin`'s own docstring
  (`test_text_seam.py:157-162`) states: "stylometry.py stays self-contained for portability
  (it ships inside `_shared/` to end users, stdlib-only, **zero intra-repo imports**), so it
  keeps its own copy ... instead of importing the seam." The CHANGELOG `[Unreleased]`
  "Text-analysis seam" entry says the same: "stylometry stays self-contained for portability
  ... with a (pattern, flags) sync-pin test." And `voice-onboard/SKILL.md:159` invokes it as
  a standalone script: `python3 <suite-root>/_shared/stylometry.py --genre <genre> <files>`,
  run from `_shared/` where `aiws/` is not guaranteed on `sys.path`.

**Steps.**
1. Read `stylometry.py`'s standalone entry points (its `__main__` / CLI at the top, the
   `--genre`/`--demo` handling) and confirm whether it can `from aiws.text import _CJK_RE`
   (and an equivalent SENT_SPLIT) **without breaking the standalone `python3
   _shared/stylometry.py ...` invocation** from a cwd where `aiws/` is not importable.
2. **If (and only if) the standalone invocation still works** — e.g. stylometry can resolve
   the suite root and add it to `sys.path` before importing, with a clean stdlib fallback —
   replace stylometry's private `_CJK_RE` (and, if `aiws.text` exposes a matching splitter,
   `_SENT_SPLIT`) with imports from `aiws.text`, keeping the same public names so
   `StylometrySyncPin` still resolves them. Re-run the full suite; every existing pin and the
   voice-extraction band must stay green with zero number movement.
3. **Escape hatch (the likely outcome — see RISKS).** If single-sourcing breaks the
   standalone portability guarantee (it almost certainly does — stylometry is run from
   `_shared/` with no `aiws/` on the path), do NOT force it. Add a short comment at each
   mirrored primitive documenting that the copy is *intentionally* mirrored for standalone
   portability and that `test_text_seam.py::StylometrySyncPin` (B6's expanded pin) is the
   drift guard, then STOP and write `BLOCKED: stylometry single-sourcing breaks standalone
   portability — seam left intentionally mirrored, guarded by StylometrySyncPin`. This is a
   legitimate, spec-sanctioned completion, not a failure.

**Done criteria (machine-checkable).**
- `bash evals/run_all.sh` → `ALL CHECKS PASSED`; `3/8 = 38%`; refusal + 71-voice intact;
  `Voice extraction eval: 71 passed` with **identical numbers** (zero band movement).
- Standalone invocation still works: `python3 skills/ai-writing-suite/_shared/stylometry.py
  --demo` (and a `--genre` run) prints its fingerprint from an arbitrary cwd.
- `StylometrySyncPin` is green either way (unified → trivially equal; mirrored → equal by the
  pin).
- `git diff --stat 84aca44` lists only `stylometry.py` (+ optionally `aiws/text.py`); it does
  NOT list `test_text_seam.py`.

**Test plan.** Guarded by `test_text_seam.py` (`StylometrySyncPin` + `TextPrimitiveParity` +
`SegmentContract`) and the voice-extraction band. The standalone-invocation check is manual
(run the script from `/tmp`).

**Escape hatch.** As step 3. Also: if the escape hatch is taken and B6 has not yet landed the
`_CJK_RE` pin, note in your report that the `_CJK_RE` mirror is guarded only by B6 — do not
add the pin yourself (that file belongs to `w2-eval-additions`).

**HCB (obey all):** branch from `84aca44`, worktree only, never `main`/other lanes ·
stdlib-only, no deps/network · INDEX/KB FROZEN · run `bash evals/run_all.sh` before+after,
keep `3/8 = 38%` + refusal + 71-voice, ZERO band movement · detector/checker is a regression
signal, not a KPI · match the exemplar file · small commits, no trailers, never push · no
CHANGELOG edit · never edit `test_text_seam.py` (B6 owns it) · no TODO/skip/stub; STOP +
`BLOCKED: …` if the premise breaks · no claim without output.

---

## SPEC — Lane w2-artifact-lane (C1, C2, C3, C4): artifact-aware edit mode for comms-polish

**STACKED after `w2-polish-train`.** Branch from the merged `feat/w2-polish-train` (it edits
`comms-polish/SKILL.md` too). If polish-train has not landed, STOP (escape hatch).

**Goal.** (C1, = owner ruling Q3-1) an artifact-lane-only density-budget ruling file. (C2) a
`references/artifact-preflight.md` for comms-polish edit mode. (C3) route comms-polish edit
mode to the preflight reference with a conditional pointer; plain markdown/email keeps the
lightweight path. (C4) one artifact-editing eval slice exercising `must_preserve` + a
must-keep presence check, added WITHOUT changing the calibration denominator.

**Why (1–2 lines).** Editing a rendered artifact (a page whose visible copy comes from a
static file, template, generated output, JS render, sidecar, or deploy copy) needs
source-tracing, a must-keep inventory, and hard density budgets that the deletion-first prose
lane deliberately does not use — and the one testable slice (fact preservation) can be gated
deterministically.

**Owner rulings baked in.** Q3-1: artifact-lane hard budgets only; prose lanes stay
deletion-first. D2 (rendered verification): browser/screenshot verification is RUNTIME-
ADVISORY guidance only — it must NEVER enter `evals/run_all.sh`'s gating path.

**In scope.**
- NEW `skills/ai-writing-suite/skills/comms-polish/references/artifact-density-budget.md`
  (C1: the ruling)
- NEW `skills/ai-writing-suite/skills/comms-polish/references/artifact-preflight.md` (C2)
- `skills/ai-writing-suite/skills/comms-polish/SKILL.md` (C3: conditional pointer from edit
  mode)
- `skills/ai-writing-suite/evals/fixtures/fixtures.json` (C4: ONE new artifact case, marked
  `detector_blind: true`)
- `skills/ai-writing-suite/evals/fixtures/test_fixtures.py` (C4: must-keep presence test)

**Out of scope.** The 8 detector-targeted calibration fixtures and every `before`/`after`
text (C4 only ADDS a new `detector_blind` fixture; it never edits an existing fixture's prose
or bands). `baseline_threshold`. The detector. INDEX/KB. Any browser/CSS/screenshot infra
(D2 — advisory only, never in CI).

**Verified current state (`84aca44`).**
- **C1 home + style.** The existing ruling-ledger style is inline in `comms-polish/SKILL.md:
  125-130`: "**Voice precedence over the catalog (C3 ruling, 2026-07-15).** When a
  construction is both a learned voice habit ... and a listed catalog tell, the voice profile
  wins ...". `references/final-pass-checklist.md` carries the "never a hard length target"
  rule that C1's budget tension sits against (systematic-improvement D1). **Recommended C1
  home: `comms-polish/references/artifact-density-budget.md`** (a reference, load-on-demand),
  NOT inline in SKILL.md and NOT `_shared/`. Justification: the budget is comms-polish-
  artifact-specific (not suite-wide, so not `_shared/`), and keeping it out of the SKILL.md
  hot path means prose lanes never load it — consistent with B2's progressive-disclosure
  direction and with "prose lanes stay deletion-first."
- **C2/C3 edit mode.** `comms-polish/SKILL.md:333-341` "## File Edits" is the current `edit`
  mode: read file → preserve frontmatter/structure → targeted prose edits → re-read →
  `git diff --check`. It has no artifact-source-tracing or must-keep inventory. This is where
  C3's conditional pointer attaches.
- **C4 must_preserve is already shipped.** `run_fixtures.py:91,116-180` — `run_deterministic`
  already loops `for literal in f.get("must_preserve", [])` and flags a dropped literal
  (Wave-1 Lane G). Four fixtures already carry `must_preserve` (`tweet-01`, `linkedin-01`,
  `readme-01`, `memo-01`).
- **C4 calibration-denominator fact (load-bearing).** `fixtures.json` has 18 fixtures.
  `run_fixtures.py:189` `if not f.get("detector_blind"): total += 1` — the naive-baseline
  denominator counts ONLY the non-`detector_blind` fixtures. There are exactly 8 of those
  (the tweet/linkedin/readme/memo pairs); 3 are `miss` → `3/8 = 38%`. The other 10 fixtures
  are `detector_blind: true` (overstep-*, narrshape-*) and are EXCLUDED from the denominator.
  A new fixture that is NOT `detector_blind` would shift the denominator to 9 and break the
  pinned `3/8`.

**Steps.**
1. **C1.** Write `references/artifact-density-budget.md` in the C3-ruling ledger style
   (bolded title + dated ruling + rule body), scoped explicitly to the artifact edit lane:
   hard density/length budgets MAY apply when editing a rendered artifact (space-constrained
   surfaces); prose lanes (plain markdown/email) stay deletion-first with "never a hard length
   target" intact. Cite the `final-pass-checklist.md` tension and state that this ruling does
   NOT override the deletion-first default outside the artifact lane.
2. **C2.** Write `references/artifact-preflight.md`: (a) trace visible copy to its durable
   source — classify each as static / template / generated / JS-rendered / sidecar / deploy
   copy; (b) classify visibility — visible-now / user-expandable / permanently-hidden /
   generated-only; (c) hotspot-first protocol — user names a component → inspect the rendered
   output → trace to source → fix source → re-verify; (d) a must-keep inventory as acceptance
   criteria; (e) edit-summary additions; (f) stop conditions. Mark rendered verification
   (browser/screenshots) as RUNTIME-ADVISORY (D2) — explicitly "never a CI gate."
3. **C3.** In `comms-polish/SKILL.md` "## File Edits", add ONE conditional pointer: when the
   target is a rendered artifact (a component/page whose visible copy is generated or
   templated), read `references/artifact-preflight.md` and `references/artifact-density-
   budget.md` first; plain markdown/email keeps the lightweight File Edits path. Anchor by
   heading/string; preserve the exactly-once untrusted-content reference.
4. **C4.** Add ONE fixture to `fixtures.json` representing an artifact-editing scenario, with
   a `must_preserve` list (literals genuinely present in its `after`) AND — the new bit — a
   must-keep presence assertion. **Mark it `detector_blind: true` with `expect_baseline:
   "miss"`** (the same mechanism the 10 overstep/narrshape fixtures use) so it is EXCLUDED
   from the naive-baseline denominator and `3/8 = 38%` is preserved. Add a `test_fixtures.py`
   test that (a) the artifact fixture's `must_preserve` literals survive in its `after`
   (present) and (b) a mutated copy that drops one is flagged by `run_deterministic` — proving
   the must-keep check can go red. Anything needing a browser stays out of CI (D2).

**Done criteria (machine-checkable).**
- `bash evals/run_all.sh` → `ALL CHECKS PASSED`; **`Naive-baseline miss rate: 3/8 = 38%`
  unchanged** (proving the new fixture did not enter the denominator); `Calibration in target
  band: YES`; refusal + 71-voice intact.
- `cd skills/ai-writing-suite/evals && python3 -m unittest fixtures.test_fixtures -v` → the
  present-literal-passes and dropped-literal-fails artifact tests both pass.
- `python3 -c "import json;d=json.load(open('skills/ai-writing-suite/evals/fixtures/
  fixtures.json'));print(sum(1 for f in d['fixtures'] if not f.get('detector_blind')))"`
  still prints `8`.
- `comms-polish/SKILL.md` "File Edits" contains a conditional pointer to both new references;
  both `references/*.md` exist; `grep -c "_shared/untrusted-content.md" comms-polish/SKILL.md`
  is 1.
- `git diff --stat` (relative to the polish-train base) lists only the five in-scope files.

**Test plan.** C4 follows `test_fixtures.py` and the `run_deterministic` must_preserve loop;
the must-go-red half models on `test_draft_cases.py::test_declawed_bad_draft_exits_nonzero`.
C1–C3 are prose/reference lanes guarded by the existing SKILL.md contract tests + `run_all.sh`.

**Escape hatch.** If `w2-polish-train` has not landed, STOP and write `BLOCKED: w2-artifact-
lane must branch from merged w2-polish-train`. If you cannot construct an honest artifact
fixture whose `must_preserve` literals are already present in its `after` without inventing
text, STOP and write `BLOCKED: no honest artifact must_preserve fixture` rather than planting
one. If adding the fixture as `detector_blind` still perturbs the `3/8` line, STOP and write
`BLOCKED: artifact fixture shifted the calibration denominator` — do NOT touch the exclusion
filter.

**HCB (obey all):** branch from merged `w2-polish-train`, worktree only, never `main`/other
lanes · stdlib-only, no deps/network · INDEX/KB FROZEN; adding ONE `detector_blind` fixture +
a `must_preserve` list is allowed for this lane, never edit an existing fixture's prose/bands ·
run `bash evals/run_all.sh` before+after, keep `3/8 = 38%` + refusal + 71-voice · rendered
verification is ADVISORY, never a CI gate (D2) · detector/checker is a regression signal, not
a KPI · match the exemplar file · small commits, no trailers, never push · no CHANGELOG edit ·
preserve exactly-once untrusted-content ref · no TODO/skip/stub; STOP + `BLOCKED: …` if the
premise breaks · no claim without output.

---

## SPEC — Lane w2-hygiene (D1, D2, D3, D4): docs + ignore hygiene (docs-only)

**Goal.** (D1) CHANGELOG `[Unreleased]` entries for the genre presets (PR #41) and the
Wave-1 train (#42–#51). (D2) a `docs/00-index.md` separating current from historical docs.
(D3) add `.omx/` to the committed `.gitignore`. (D4) extend the design-doc historical banner
to cover the stale v1/v2 scope split.

**Why (1–2 lines).** The changelog omits an entire merged wave; docs/ has no index; `.omx/`
is ignored only locally (not via the committed ignore file, so it can be committed by a fresh
clone); and the v1 design doc still describes shipped features (comms-qa, comms-draft) as v2.

**In scope.**
- `skills/ai-writing-suite/CHANGELOG.md` (D1)
- NEW `docs/00-index.md` (D2)
- `.gitignore` (repo root; D3)
- `docs/design-ai-writing-suite-v1-2026-06-06.md` (D4: extend the top banner only)

**Out of scope.** Any source file, any moving of doc files (D2 is an index, not a
reorganization). The other design docs' bodies. `.omc/` (already ignored).

**Verified current state (`84aca44`).**
- **D1.** `CHANGELOG.md:10-105` — the `[Unreleased]` section is populated with pre-Wave-1
  (genre-presets-era) entries (multi-genre voice profiles, S10 tell, FP gate, epistemic
  modality, deletion-first density, machine-readable registry, capability-runner,
  text-analysis seam, aiws/kb, judge facade, Q7/Q8/Q9/C3, narrative-shape, stylometry,
  audit-report, KB ingestion, behavioral-eval lanes). It contains **zero** Wave-1-train items
  — no state-location, precedence-policy, untrusted-content, must_preserve, CJK-refusal
  routing, self-report divergence, or verbatim anchors — and no genre-presets (scenario-
  presets expansion) entry. Note the `[Unreleased]` block has two `### Added` sub-headers
  (lines 12 and 64) — a pre-existing structural quirk to consolidate, not multiply.
- **D2.** `docs/00-index.md` does NOT exist. `docs/` holds design docs, `packaging.md`, the
  two 2026-07-21 plans, the Wave-1 completion report, handovers, and session closeouts.
- **D3.** Committed `.gitignore` (repo root, 8 lines) has `__pycache__/`, `*.py[cod]`,
  `.omc/`, `.claude/worktrees/` — NO `.omx/`. `.omx/` exists on disk and is currently ignored
  (via a non-committed mechanism — global excludes / `.git/info/exclude`), so a fresh clone
  would not ignore it. D3 makes the ignore committed.
- **D4.** `docs/design-ai-writing-suite-v1-2026-06-06.md:1-6` — the historical banner covers
  only the packaging restructure ("packaging prescriptions ... were removed; read
  docs/packaging.md"). It does NOT flag the stale v1/v2 scope split: the doc's decision log +
  v2 roadmap describe `comms-qa` and `comms-draft` as v2 (e.g. line 51, and the "v1 Scope vs
  v2 Deferral" in CHANGELOG 1.0.0), but both shipped in v1.1.

**Steps.**
1. **D1.** In `[Unreleased]`, consolidate to one `### Added`/`### Changed`/`### Fixed`
   structure and add: (a) a genre-presets entry (the tweet/LinkedIn/README/memo/PR-desc/
   release-note scenario-preset weighting shipped in PR #41); (b) the Wave-1 train (#42–#51):
   per-user state boundary + `$AIWS_STATE_DIR` resolver, KB retriever tie-set protocol, CJK
   refusal routing through the detector, honest fabrication gate + verb-claim class,
   versioned calibration-policy note, `must_preserve` fact-preservation capability,
   self-report-vs-corpus divergence loop, verbatim voice anchors, `_shared` precedence
   policy, and the shared untrusted-content contract. Keep entries factual and terse; verify
   each against the completion report before writing.
2. **D2.** Write `docs/00-index.md`: a two-section index — **Current** (design, packaging,
   plans, completion reports) and **Historical** (handovers, session closeouts) — each a
   bulleted list of the actual files in `docs/` with a one-line description. No file moves.
3. **D3.** Add a `.omx/` line to the committed `.gitignore` (near the existing `.omc/` line,
   with a one-line comment matching the file's style).
4. **D4.** Extend the design-doc banner (lines 1-6) with one clause noting the v1/v2 scope
   split is also historical: QA and drafting (`comms-qa`, `comms-draft`) shipped in v1.1, so
   the "Deferred to v2" list in this doc is stale — see the CHANGELOG for shipped scope.

**Done criteria (machine-checkable).**
- `bash evals/run_all.sh` → `ALL CHECKS PASSED` (docs-only; nothing should perturb the
  suite).
- `git grep -n "^\.omx/" .gitignore` (or equivalent) returns the new line.
- `docs/00-index.md` exists with a Current/Historical split naming the real `docs/` files.
- `CHANGELOG.md [Unreleased]` names both the genre presets and the Wave-1-train items; the
  duplicate `### Added` sub-headers are consolidated.
- The design-doc banner mentions the stale v1/v2 scope split.
- `git diff --stat 84aca44` lists only the four in-scope files.

**Test plan.** Docs-only. The only executable check is `run_all.sh` staying green (it does
not read these files). Optionally add nothing.

**Escape hatch.** If, verifying against the completion report, any Wave-1 item you were about
to changelog turns out NOT to have landed on `main`, STOP and write `BLOCKED: changelog item
<X> not present at HEAD` rather than documenting unshipped work. If `.omx/` turns out to be
already ignored via the committed `.gitignore` at your HEAD, note it and skip D3 (do not
duplicate the line).

**HCB (obey all):** branch from `84aca44`, worktree only, never `main`/other lanes ·
stdlib-only · INDEX/KB FROZEN · run `bash evals/run_all.sh` before+after (docs-only, must
stay green) · detector/checker is a regression signal, not a KPI · match the surrounding doc
style · small commits, no trailers, never push · this lane IS the CHANGELOG owner · no
TODO/skip/stub; STOP + `BLOCKED: …` if the premise breaks · no claim without output.

---

## SPEC — Lane w2-research-designs (E1, E2, E3, E4): four design docs (DESIGN, not code)

**Goal.** Four design documents, each with its own acceptance criteria and a falsifiable next
step. No production code (E4's optional one-line SKILL.md hook is flagged as a follow-up, NOT
built here — see below).

**Why (1–2 lines).** These are the plan's four named open gaps (detector false-positive rate,
tell-catalog decay, audience/register conditioning, corpus consent/PII). Each needs a
designed, stdlib-implementable shape before any future build lane.

**In scope (design docs only, under `docs/`).**
- NEW `docs/design-detector-false-positive-eval.md` (E1)
- NEW `docs/design-tell-catalog-versioning.md` (E2)
- NEW `docs/design-audience-register-conditioning.md` (E3)
- NEW `docs/design-corpus-consent-pii.md` (E4)

**Out of scope.** All production code and evals. In particular, do NOT edit
`voice-onboard/SKILL.md` — E4's consent/impersonation hook is documented as a follow-up in the
E4 design doc, and flagged in RISKS as the sole potential code touch in Group E, to be built
in a later lane. Keep this lane docs-only so it stays trivially parallel.

**Verified current state (`84aca44`).**
- **E1.** `plan-systematic-improvement-2026-07-21.md:110` explicitly rejects "public corpus
  as *substitute* for owner-gated real-writer eval (supplement only — `false_positives.json`
  disclaims benchmark validity)." The shipped `evals/fixtures/false_positives.json` +
  `run_false_positives.py` is a synthetic regression fence (CHANGELOG 1.1.0), NOT a
  known-human-negative eval. E1 designs the real thing.
- **E2.** The catalog is 72 entries (CHANGELOG `[Unreleased]`: "catalog registry 71 → 72"),
  a static snapshot; `_shared/patterns/00-index.md` + `aiws/catalog.py` carry Severity/
  Enforcement metadata with `enforcement=regex` entries. No version stamps or decay cadence
  exist.
- **E3.** Voice is modeled as one fixed profile per genre (`voice-onboard`,
  `_shared/voice-profile.md`'s 15-header contract). There is no per-channel register (Slack
  vs doc vs PR) conditioning layer. E3 designs how profiles/genre files would extend without
  breaking existing consumers (`comms-polish`, `comms-draft` read by header).
- **E4.** `voice-onboard/SKILL.md` Step 1 (lines 66-98) ingests real writing; "## Safety &
  boundaries" (lines 251-262) has "Never invent voice" / "Stay in your lane" but NO consent,
  PII, or impersonation-refusal rule. The one-line hook, IF built later, would attach in that
  Safety section.

**Steps (per doc — each is self-contained).**
1. **E1.** Design a known-human-negative false-positive eval on real human text: corpus
   sourcing (public-domain candidates + licensing) that SUPPLEMENTS but never SUBSTITUTES the
   owner-gated real-writer set; the operating point (detector threshold under test); a
   stdlib-implementable capability shape (how it plugs into `evals/capabilities/` without
   entering the calibration denominator). Acceptance criteria + one falsifiable next step
   (e.g. "measure FP rate on N public-domain samples; if > X%, the detector's specificity is
   overclaimed").
2. **E2.** Design tell-catalog versioning/decay: per-entry version stamps, a staleness-review
   cadence, and how `enforcement=regex` entries roll over as the adversarial target moves.
   Acceptance criteria + a falsifiable next step (e.g. "an entry unreviewed for N months
   flags in a lint").
3. **E3.** Design audience/register conditioning: voice as one fixed profile vs a per-channel
   register layer; how profiles/genre files would carry a register axis without breaking the
   15-header contract or the by-header consumers. Acceptance criteria + a falsifiable next
   step.
4. **E4.** Design corpus consent/PII/impersonation handling for `voice-onboard`: the consent
   gate (author confirms the samples are theirs to use), PII handling in ingested samples, and
   the impersonation refusal rule (refuse to profile a named third party's writing without
   consent). Specify the one-line SKILL.md hook as a FOLLOW-UP (name where it attaches — the
   Safety section — but do NOT edit the file in this lane). Acceptance criteria + a falsifiable
   next step.

**Done criteria (machine-checkable).**
- `bash evals/run_all.sh` → `ALL CHECKS PASSED` (docs-only).
- All four `docs/design-*.md` exist, each with an explicit "Acceptance criteria" section and a
  "Falsifiable next step" line.
- `git diff --stat 84aca44` lists only the four new docs (and NOT `voice-onboard/SKILL.md`).

**Test plan.** Docs-only; `run_all.sh` green is the gate. Each doc's own acceptance-criteria
section is the review target.

**Escape hatch.** If E4's design cannot express the impersonation refusal without a model
judgment, say so in the doc (design the human-gated fallback) rather than forcing a
deterministic rule — this is a design lane, so a documented open question is a valid outcome,
not a `BLOCKED`.

**HCB (obey all):** branch from `84aca44`, worktree only, never `main`/other lanes ·
stdlib-only (N/A — no code) · INDEX/KB FROZEN · run `bash evals/run_all.sh` before+after
(docs-only, must stay green) · detector/checker is a regression signal, not a KPI · match the
existing `docs/design-*.md` register · small commits, no trailers, never push · no CHANGELOG
edit · do NOT edit any SKILL.md (E4 hook is a flagged follow-up) · no TODO/skip/stub; STOP +
`BLOCKED: …` if the premise breaks · no claim without output.

---

## 4. RISKS

**R1 — File-overlap matrix (verified this session; the task's claimed separations hold, with
two additions).**

| File | Lanes that WRITE it | Verdict |
|---|---|---|
| `comms-polish/SKILL.md` | w2-polish-train (B1, B2), w2-artifact-lane (C3) | **Handled by the stack.** artifact-lane branches from merged polish-train, so C3 edits the already-slimmed file. Not parallel. |
| `comms-draft/SKILL.md` | w2-polish-train (B1) only | Clean. B5 (w2-eval-additions) only READS it in a test; no write collision. |
| `smoke_test.py` | w2-eval-integrity (A1) only | Clean. B4 deliberately targets `test_kb_retrieval_protocol.py` instead — verified separate. |
| `SMOKE-TEST.md` | w2-eval-integrity (A1) only | Clean (test-chain doc, not INDEX/KB). |
| `test_kb_retrieval_protocol.py` | w2-eval-additions (B4) only | Clean. |
| `test_text_seam.py` | w2-eval-additions (B6) only | **Clean IF B8 respects its out-of-scope.** B8 must NOT edit this file (see R2). |
| `_shared/stylometry.py` | w2-text-seam (B8) only | Clean. B6 only READS it. |
| `test_untrusted_content_contract.py` | w2-eval-integrity (A2) only | Clean. |
| `holdout_adversary.py` | w2-eval-integrity (A3) only | Clean. |
| `scripts/validate_packaging.py` | w2-packaging (B7) only | Clean. |
| `fixtures.json` / `test_fixtures.py` | w2-artifact-lane (C4) only | Clean. |
| `CHANGELOG.md` | w2-hygiene (D1) only | Clean — enforced by HCB #10 (no other lane may touch it). |
| root `SKILL.md` | none write it | B3 only READS it. Clean. |
| `.gitignore` | w2-hygiene (D3) only | Clean. |
| `docs/*.md` | w2-hygiene (D2, D4), w2-research-designs (E1–E4) | Different files (D2 = `00-index.md`, D4 = the v1 design doc; E = four new design docs). No write collision; see R6 for the soft index-freshness note. |

**R2 — B6 ↔ B8 semantic interaction (the one interaction the task's matrix did not call out).**
B6 (w2-eval-additions) ADDS a `_CJK_RE` sync-pin to `StylometrySyncPin` in `test_text_seam.py`.
B8 (w2-text-seam) tries to single-source stylometry's `_CJK_RE` from `aiws.text`. If B8 were
to unify, the pin becomes trivially-true and B8 would be tempted to edit `test_text_seam.py` —
which is B6's file. **Mitigation:** B8's out-of-scope forbids touching `test_text_seam.py`;
B8's escape hatch (the likely outcome, see R3) leaves the mirror in place with B6's pin as the
guard. Recommended merge order: land B6 (or all of w2-eval-additions) before w2-text-seam, so
the `_CJK_RE` pin exists as the guard regardless of B8's outcome. B6 is load-bearing and must
land whether or not B8 unifies.

**R3 — B8 almost certainly hits its escape hatch (import-direction / portability).** Three
independent sources at HEAD say stylometry is deliberately self-contained: `StylometrySyncPin`'s
docstring ("zero intra-repo imports ... for portability"), the CHANGELOG "Text-analysis seam"
entry ("stylometry stays self-contained for portability ... deliberately not unified"), and
`voice-onboard/SKILL.md:159` invoking it as a standalone `python3 _shared/stylometry.py` from a
cwd where `aiws/` is not on the path. So B8's realistic, correct outcome is to DOCUMENT the
intentional mirror and STOP (escape hatch), with B6's pin as the guard — not to remove the
duplication. The lane's value is confirming + documenting the seam, and this is spec-sanctioned,
not a failure. Do not let an executor force the unification and break the standalone script.

**R4 — C4 must NOT change the calibration denominator (verified numeric).** The naive-baseline
denominator is the 8 non-`detector_blind` fixtures (`run_fixtures.py:189`), of which 3 are `miss`
→ `3/8 = 38%`. Adding C4's artifact fixture as a normal (detector-targeted) fixture would make
it `3/9 = 33%` — still in the 30–40% band, but it changes the pinned `3/8` string the HCB and
`test_calibration.py` depend on (`test_calibration.py:19-27` pins `valid_miss_counts(8)==[3]`,
`miss_target(8)==3`). **Mitigation, baked into C4:** the new artifact fixture is
`detector_blind: true` (excluded from the denominator), exactly as the 10 overstep/narrshape
fixtures are; the done-criteria include a `sum(...not detector_blind...) == 8` assertion. Never
touch the exclusion filter to "fix" a shifted band.

**R5 — B2 progressive disclosure is test-guarded (verified).** `test_report_contract.py::
ModeFirewall` (lines 130-144) requires `comms-polish/SKILL.md` to keep the literal
`### Audit Report Contract` heading (after Rewrite Workflow + File Edits) AND the firewall
phrases "`rewrite` and `edit`" + "are unchanged by it". B2 therefore moves only the contract
*body* to `references/audit-report-contract.md`, keeping the heading + firewall + a conditional
pointer in place. The Before/After Examples block has no such guard and moves wholesale. An
executor who moves the whole contract section out will red the suite — the spec calls this out
explicitly.

**R6 — Soft: docs index freshness (D2 vs E) and comms-draft section-anchor stability (B1 vs
B5).** (a) D2's `docs/00-index.md` lists current docs; if the four E design docs land after D2,
the index won't name them until a follow-up touch — cosmetic, not a conflict (different files).
(b) B1 edits `comms-draft/SKILL.md`'s Inputs voice block; B5's coupling test parses the
acceptance-criteria step-1 block (a different section). B1 must not disturb the five dimension
labels in step 1 (it has no reason to). If B1 and B5 land in either order, B5's test parses the
merged file and stays green as long as the dimension labels are untouched. Flagged so a reviewer
watches the step-1 anchors.

**R7 — A2 characterization correction (evidence-first).** The task described
`test_untrusted_content_contract.py` as "only checks the contract file exists." Verified: it
also pins the 5 reference counts and the fixture marker (lines 27-48). The real gap A2 closes is
narrower and accurate: the contract *body's rules* are unpinned (an emptied
`untrusted-content.md` still passes). A2 adds a `REQUIRED_PHRASES` body pin; the spec states the
accurate current state so the executor targets the actual gap.

**R8 — Calibration + refusal + voice invariants are shared across all eight lanes.** Only
w2-artifact-lane (C4) touches `fixtures.json` and only additively as `detector_blind`; no lane
touches the detector control flow or the calibration set. Every lane's gate re-runs
`bash evals/run_all.sh` before+after and pastes both tails, so a silent shift in `3/8 = 38%`,
the `overstep-04-selfqa-zh refusal` line, or the `71 passed` voice count is caught at that
lane's gate rather than at integration.

**R9 — E4's SKILL.md hook is deliberately deferred.** E4 designs the consent/PII/impersonation
rule but does NOT edit `voice-onboard/SKILL.md`, to keep w2-research-designs docs-only and
trivially parallel. The one-line hook is flagged here as the sole potential Group-E code touch,
to be built in a future lane once the design is approved. If the owner wants it in Wave-2, it
should be a separate one-line follow-up lane (it edits `voice-onboard/SKILL.md`, which no other
Wave-2 lane writes, so it stays conflict-free).
