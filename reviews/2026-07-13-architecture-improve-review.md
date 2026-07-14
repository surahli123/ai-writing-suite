# Codex External Review — /improve + architecture review of ai-writing-suite

Model: gpt-5.6-sol xhigh, read-only. Date: 2026-07-13. VERDICT: ARCHITECTURE NEEDS-WORK
Scope: whole suite at feat/behavioral-evals-draft-voice + the four lane branches.

---

## Architecture review

The suite is operationally healthy but has outgrown its original eval and registry layout. Fresh validation passed all six steps, including 243 unit tests; the problem is future change locality, especially once the four open branches merge.

1. **Replace ordinal shell orchestration with decentralized capability runners.**

   - **What:** Introduce `evals/run.py` that discovers capability-local descriptors rather than reading a centrally edited step list. Each capability exposes a small uniform interface: `SPEC = {id, kind, needs_model, depends_on}` plus `run(context) -> EvalResult`. Runtime discovery computes `[n/N]`; [run_all.sh](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/evals/run_all.sh:7) becomes a compatibility wrapper with no numbering.
   - **Target shape:**
     ```text
     evals/
       core/                 # runner protocol, result type, shared judging
       capabilities/
         detector/
         polish/
         false_positive/
         draft/
           cases/
           mutants.py
         voice/
           corpora/
           artifacts/
           mutants.py
         audit_report/
         kb/
       run.py
       manifest.md           # generated/check-time human-readable projection
       run_all.sh            # python3 -m evals.run
     ```
   - **Fixtures:** Eliminate the global junk-drawer meaning of `fixtures/`. Cases, corpora, artifacts, graders, and mutant generators belong beside the capability whose contract gives them meaning. Mutants remain capability-local; only the mutation result/catch-rate protocol belongs in `evals/core/`.
   - **Why:** The current six-step branch and the incoming three-/four-step variants prove that positional orchestration is merge-hostile. A central hand-maintained manifest would merely relocate the hotspot; decentralized descriptors preserve locality while a generated `manifest.md` provides the readable inventory.
   - **Cost:** M, largely mechanical after characterization tests.
   - **When:** **Safe NOW** to add the runner protocol, discovery test, and wrapper contract. Move `fixtures/` and cut over `run_all.sh` **after the open branches merge**, because both are merge-hot.
   - **Growth debt addressed:** #8’s scheduled live lane becomes another `kind="live"` capability, not a second CI orchestration system.

2. **Make the pattern Markdown itself the structured registry.**

   - **What:** Keep the nine category files, but give every `### <id> — <name>` entry a uniform, visible Markdown metadata table:
     ```markdown
     | Metadata | Value |
     | --- | --- |
     | Severity | high |
     | Enforcement | mechanical |
     | Detector rule | tier1_words |
     | Judge dimensions | tells_removed |
     | Languages | en |
     | Sources | avoid-ai, blader |
     ```
     Add one strict stdlib loader, such as `aiws/catalog.py`, that returns typed catalog records.
   - **Derivations:** Generate marker-bounded, checked-in projections for `00-index.md`, the judge-dimension section of `rubric.md`, and the detector coverage matrix. Literal rule data such as Tier-1 replacements can be loaded directly from Markdown; complex detector implementations remain Python functions named by `Detector rule`. Checkers consume the same loader instead of writing their own regex parsers.
   - **Prose:** The four `SKILL.md` files should reference categories or registry queries, not re-enumerate tell names as [comms-polish currently does](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/skills/comms-polish/SKILL.md:35). Detailed Tell/Fix/validity prose stays where hosts can read it.
   - **Why:** The catalog already claims stable IDs as its source of truth in [00-index.md](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/_shared/patterns/00-index.md:8), but [test_catalog_sync.py](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/evals/test_catalog_sync.py:1) synchronizes only one table, while the incoming audit checker independently parses live headings and narrative shape separately extends `rubric.md`. #10/#11 will multiply these parallel registries.
   - **Cost:** M. The parser/generator is small; annotating and reviewing every existing entry is the real cost.
   - **When:** **After the open branches merge** because patterns, `rubric.md`, and the audit checker are all changing. The loader contract can be designed now.
   - **Growth debt addressed:** #10/#11 become ordinary metadata additions with a generated detector/judge coverage report, rather than new ad-hoc sync tests.

3. **Create one deep text-analysis module before multilingual support.**

   - **What:** Add `aiws/text.py` with a small interface such as `segment(text, language="auto") -> TextDocument`, returning script classification, support status, tokens, sentences, paragraphs, and word counts. Detector scoring and stylometric metrics consume that result rather than tokenizing independently.
   - **Why:** The detector currently defines its own whitespace word count and ASCII sentence split in [detector.py](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/evals/detector/detector.py:18); the voice grader uses another `.split()` implementation in [run_voice_extraction.py](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/evals/fixtures/run_voice_extraction.py:101); the incoming `_shared/stylometry.py` introduces a third engine with different word, sentence, and CJK rules. Once #14 lands, every metric would otherwise disagree by language.
   - **Seam:** Start with one whitespace-language implementation plus an explicit unsupported/partial-script result. Add a real CJK adapter only when #14 provides the second implementation; do not invent a provider-style adapter hierarchy prematurely. Version the measurement policy so detector bands do not silently shift.
   - **Cost:** M, with fixture recalibration risk.
   - **When:** **After `feat/stylometric-fingerprint` merges**, then do this before #14.
   - **Growth debt addressed:** #14 changes one seam rather than detector, voice, stylometry, documentation, and calibration independently.

4. **Deepen `judge.py` behind one evaluation interface.**

   - **What:** Expose one interface such as `evaluate(JudgeRequest) -> JudgeResult`, where the result includes configuration state, parsed dimensions, verified evidence, aggregated verdict, warnings, and transport failure. Capability packages remain responsible only for prompt construction and gold-label accounting.
   - **Why:** The 468-line [judge.py](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/evals/fixtures/judge.py:160) currently owns transport, response-envelope parsing, evidence parsing/verification, family detection, voting, and aggregation, while both [run_fixtures.py](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/evals/fixtures/run_fixtures.py:405) and [run_draft_cases.py](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/evals/fixtures/run_draft_cases.py:465) reproduce the call/parse/verify/aggregate lifecycle. The scheduled live lane would become a third copy.
   - **Depth rule:** Do not split this into five shallow utility modules. Keep those concerns internal behind the façade. Likewise, retain the current OpenAI-compatible transport internally until a second real transport requires an adapter seam.
   - **Cost:** S–M.
   - **When:** **Safe NOW** to add façade characterization tests; switch existing runners **after the fixture branches merge**.
   - **Growth debt addressed:** #8 reuses a trustworthy judge module instead of coupling CI scheduling directly to parser and provider details.

5. **Reverse the `tools → evals` dependency before merging KB tooling.**

   - **What:** Move reusable KB behavior into `aiws/kb/`: `load_index/retrieve`, entry enumeration, structural validation, and `validate_kb(path) -> ValidationReport`. Tools become thin entrypoints; evals import and test the product module.
   - **Why:** The incoming `kb_validate.py` adds `evals/` to `sys.path`, imports `kb_lint` and `smoke_test`, calls private `_entry_files`, and temporarily mutates `smoke_test.INDEX_PATH`. That makes evaluation scaffolding an accidental production interface and reverses the intended dependency direction.
   - **Cheapest refactor:** Move the existing functions unchanged first; do not redesign ingestion. Standardize invocation as `python3 -m aiws.kb.validate`, with optional thin compatibility scripts under `tools/`.
   - **Cost:** S–M.
   - **When:** **After `feat/kb-ingestion-tooling` merges**, before other tools reuse those internals.
   - **Moat impact:** This gives the pluggable-KB moat a real module seam rather than making company-fork tooling depend on test files.

## Keep

- Keep the stdlib-only, key-free default CI lane and explicit `AIWS_JUDGE_RUN=1` spend guard.
- Keep deterministic output-contract checks explicitly separate from claims about live skill behavior; the methodological distinction in [the advisor review](/Users/surahli/Documents/ai-writing-suite/reviews/2026-07-13-advisor-eval-method.md:43) is excellent.
- Keep paired good/bad artifacts, generated mutant-family catch rates, declared known misses, and the separately authored append-only hard tail.
- Keep `no_fabrication` as the always-required judge dimension and verbatim evidence as an auditable protocol.
- Keep stable tell IDs, source attribution, human-readable Tell/Fix prose, and validity conditions that prevent detector-driven over-correction.
- Keep voice measurement per genre; never restore pooled “average voice” metrics.
- Keep the engine/fuel split and the Markdown `INDEX.md` KB contract—improve the tooling module around it, not the product model.
- Keep independent capability execution: orchestration should compose runners, not turn them into one monolithic test program.

## Hard questions

1. Does catalog “severity” mean editorial harm, confidence of detection, or enforcement strength? Those are different axes and should not share one field.
2. Should the scheduled live lane measure provider availability, skill quality, or release regression? Each requires different retention, baselines, and failure semantics.
3. Are tell IDs language-universal with per-language evidence/rules, or will each language receive distinct IDs? Decide before #14 or the registry migration will be repeated.
4. Is the detector’s numeric score a compatibility contract? Shared tokenization may shift every band even when qualitative behavior improves.
5. Should checked-in generated Markdown projections be mandatory review artifacts, or should hosts always navigate the canonical per-pattern metadata directly?
6. When a judge-only tell such as narrative shape has several sub-pattern IDs, should the judge score one aggregate dimension or one dimension per ID? The answer affects evidence quality and coverage reporting.

ARCHITECTURE: NEEDS-WORK