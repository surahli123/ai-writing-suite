Reading prompt from stdin...
OpenAI Codex v0.137.0
--------
workdir: /Users/surahli/Documents/ai-writing-suite
model: gpt-5.5
provider: chatgpt_http
approval: never
sandbox: read-only
reasoning effort: high
reasoning summaries: none
session id: 019ea520-1106-7b63-8da6-20df36af1fec
--------
user
You are an adversarial code reviewer. SINGLE-PASS, DIRECT review. CRITICAL CONSTRAINT: do NOT invoke any code-review skill, do NOT spawn, delegate to, or wait on sub-agents/lanes — a prior run exhausted its time budget doing that. Read the files yourself in THIS context and OUTPUT THE FINDINGS LIST + VERDICT NOW. Be fast and concrete.

CONTEXT: "Phase 2a" of the AI Writing Suite wires an OPTIONAL, OPT-IN, ADVISORY LLM judge into an existing eval harness, under skills/ai-writing-suite/evals/. Read these files directly (use sed/nl/cat):
- skills/ai-writing-suite/evals/fixtures/judge.py
- skills/ai-writing-suite/evals/fixtures/run_fixtures.py
- skills/ai-writing-suite/evals/fixtures/test_fixtures.py
- skills/ai-writing-suite/evals/test_voice_contract.py
- skills/ai-writing-suite/evals/run_all.sh and .github/workflows/ci.yml

Check these invariants and report only REAL defects with file:line + concrete fix:
1. CI stays stdlib-only AND key-free: the deterministic path (run_all.sh -> run_fixtures, no --judge, no key) makes ZERO network calls and does NOT import judge.py (lazy import inside run_judge). run_all.sh / ci.yml unchanged.
2. Secrets fail LOUD: wrong/expired key (HTTP 401/403/5xx) or transport error must raise -> nonzero exit, NOT a silent SKIP. Key never logged. A stray key without AIWS_JUDGE_RUN=1 must NOT fire a call.
3. no_fabrication enforceable on EVERY fixture: build_judge_prompt always asks for it even when rubric_focus omits it; aggregate() recomputes in Python (no_fabrication FAIL -> overall FAIL), ignores the model's "VERDICT:" line; unparseable or missing-required-dim -> None (SKIP), never fake PASS.
4. Calibration untouched: fixtures.json change is field-only (expected_verdict), no fixture added/removed, so naive-baseline miss stays 3/8=38%.
5. Judge is ADVISORY: PASS/FAIL counts do NOT change exit code; only deterministic fails + the liveness "configured but scored 0/N" do.
6. Robustness edges: the verdict parser regex (_DIM_LINE), _extract_text envelope handling, majority_vote (ties + a dim present in only some reps), the score() 3-state gate.
7. Test quality: do the new tests actually prove the above or pass vacuously? Any invariant with no test? Is test_voice_contract's path resolution + header normalization correct?

OUTPUT NOW:
- Findings, each [BLOCKER]/[CONCERN]/[SUGGESTION] with file:line, problem, concrete fix.
- One-line verdict: SAFE-TO-COMMIT / COMMIT-WITH-FIXES / NEEDS-REWORK.
- End with: VERIFIED_AGAINST: feat/phase2a-judge-wirein @ <HEAD-sha> @ <timestamp>

2026-06-08T02:46:49.599262Z ERROR rmcp::transport::worker: worker quit with fatal: Transport channel closed, when AuthRequired(AuthRequiredError { www_authenticate_header: "Bearer realm=\"OAuth\", resource_metadata=\"https://mcp.cloudflare.com/.well-known/oauth-protected-resource/mcp\", error=\"invalid_token\"" })
hook: SessionStart
hook: SessionStart
hook: SessionStart
hook: SessionStart Completed
hook: SessionStart Completed
hook: SessionStart Completed
hook: UserPromptSubmit
hook: UserPromptSubmit
hook: UserPromptSubmit
hook: UserPromptSubmit Completed
hook: UserPromptSubmit Completed
hook: UserPromptSubmit Completed
codex
Mode: direct review only. I’ll read the named files plus HEAD metadata locally, then return only concrete defects and a verdict.
hook: PreToolUse
hook: PreToolUse
hook: PreToolUse
hook: PreToolUse
hook: PreToolUse
hook: PreToolUse
hook: PreToolUse Completed
hook: PreToolUse Completed
hook: PreToolUse Completed
hook: PreToolUse Completed
hook: PreToolUse Completed
hook: PreToolUse Completed
codex(13088) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
codex(13095) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
codex(13101) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
codex(13102) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
codex(13103) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
codex(13104) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
exec
/bin/zsh -lc 'nl -ba skills/ai-writing-suite/evals/fixtures/judge.py' in /Users/surahli/Documents/ai-writing-suite
exec
/bin/zsh -lc 'nl -ba skills/ai-writing-suite/evals/fixtures/test_fixtures.py' in /Users/surahli/Documents/ai-writing-suite
exec
/bin/zsh -lc 'nl -ba skills/ai-writing-suite/evals/run_all.sh' in /Users/surahli/Documents/ai-writing-suite
exec
/bin/zsh -lc 'nl -ba .github/workflows/ci.yml && git rev-parse --abbrev-ref HEAD && git rev-parse HEAD && date -u +%Y-%m-%dT%H:%M:%SZ' in /Users/surahli/Documents/ai-writing-suite
exec
/bin/zsh -lc 'nl -ba skills/ai-writing-suite/evals/test_voice_contract.py' in /Users/surahli/Documents/ai-writing-suite
exec
/bin/zsh -lc 'nl -ba skills/ai-writing-suite/evals/fixtures/run_fixtures.py' in /Users/surahli/Documents/ai-writing-suite
 succeeded in 252ms:
     1	#!/usr/bin/env bash
     2	# run_all.sh — run every v1 regression check in one shot, fail-fast.
     3	#
     4	# Stdlib-only: no pip installs, no external deps. Works from any cwd (resolves
     5	# its own directory). Used both by humans pre-commit and by CI (.github/workflows/ci.yml).
     6	#
     7	# Checks, in order (any nonzero aborts the run):
     8	#   1. unit tests   — detector logic + fixture well-formedness (~23 tests)
     9	#   2. KB smoke     — end-to-end ingestion/retrieval over the seed KB (3 cases)
    10	#   3. fixtures     — deterministic detector bands + 30-40% baseline calibration assert
    11	
    12	set -euo pipefail
    13	
    14	cd "$(dirname "${BASH_SOURCE[0]}")"   # the evals/ directory
    15	
    16	echo "== [1/3] unit tests =="
    17	python3 -m unittest discover -p 'test_*.py'
    18	
    19	echo "== [2/3] KB smoke =="
    20	python3 smoke_test.py
    21	
    22	echo "== [3/3] fixtures (deterministic + calibration) =="
    23	python3 -m fixtures.run_fixtures
    24	
    25	echo
    26	echo "ALL CHECKS PASSED"

 succeeded in 312ms:
     1	"""Schema-contract test for the voice profile (Phase 2a tripwire).
     2	
     3	comms-polish reads the learned voice by `## H2` header from
     4	`_shared/host-profile-template.md` (the blank form voice-onboard fills, and the
     5	shape voice-profile.md inherits). If a header is renamed or dropped, comms-polish
     6	SILENTLY falls back to generic voice with no error (see voice-onboard/SKILL.md +
     7	comms-polish/SKILL.md "Voice Matching"). This stdlib-only test turns that silent
     8	failure into a loud CI failure.
     9	
    10	Scope: it does NOT judge voice quality (that needs a sample corpus — deferred to
    11	Phase 2b). It only guards the header contract the two skills agree on.
    12	"""
    13	
    14	import os
    15	import re
    16	import unittest
    17	
    18	# Headers comms-polish reads (comms-polish/SKILL.md "Voice Matching"). Apostrophes
    19	# are normalized before comparison so a straight/curly swap doesn't false-fail.
    20	REQUIRED_HEADERS = [
    21	    "Tone",
    22	    "Sentence Length",
    23	    "Vocabulary Do",
    24	    "Vocabulary Don't",
    25	    "Signature Moves",
    26	    "Punctuation & Formatting",
    27	    "Openings & Closings",
    28	    "Uncertainty Style",
    29	    "Things To Avoid",
    30	    "Scope & Calibration",
    31	]
    32	
    33	TEMPLATE = os.path.join(
    34	    os.path.dirname(os.path.abspath(__file__)),
    35	    "..", "_shared", "host-profile-template.md")
    36	
    37	
    38	def _norm(s):
    39	    return s.replace("’", "'").strip()
    40	
    41	
    42	class VoiceProfileContract(unittest.TestCase):
    43	    def test_template_exists(self):
    44	        self.assertTrue(os.path.exists(TEMPLATE),
    45	                        f"voice profile template missing: {TEMPLATE}")
    46	
    47	    def test_all_consumer_headers_present(self):
    48	        with open(TEMPLATE, encoding="utf-8") as fh:
    49	            headers = {_norm(m.group(1))
    50	                       for m in re.finditer(r"^##\s+(.+)$", fh.read(), re.M)}
    51	        for h in REQUIRED_HEADERS:
    52	            self.assertIn(
    53	                _norm(h), headers,
    54	                f"host-profile-template.md missing '## {h}' — comms-polish reads "
    55	                f"this header; renaming it silently breaks voice matching")
    56	
    57	
    58	if __name__ == "__main__":
    59	    unittest.main()

 succeeded in 312ms:
     1	#!/usr/bin/env python3
     2	"""Run the before/after fixtures. Deterministic half always; LLM half on demand.
     3	
     4	Run from `evals/`:
     5	    python3 -m fixtures.run_fixtures            # deterministic + calibration
     6	    python3 -m fixtures.run_fixtures --judge    # also emit LLM-judge prompts
     7	
     8	WHY a model is NOT required: the deterministic half (detector score bands +
     9	naive-baseline miss rate) is the part that gates CI. The LLM half needs a model;
    10	when none is wired in we print the judge prompts and mark them SKIPPED so a
    11	reader can see exactly what *would* run, instead of a green check that proved
    12	nothing. There is intentionally no API call here — this repo ships zero deps and
    13	no key. A host integration calls `build_judge_prompt()` and sends it to whatever
    14	model the surface provides.
    15	"""
    16	
    17	import argparse
    18	import json
    19	import os
    20	import sys
    21	
    22	# Allow running both as a module (-m fixtures.run_fixtures) and as a script.
    23	sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    24	from detector.detector import analyze  # noqa: E402
    25	
    26	HERE = os.path.dirname(os.path.abspath(__file__))
    27	FIXTURES_PATH = os.path.join(HERE, "fixtures.json")
    28	RUBRIC_PATH = os.path.join(HERE, "rubric.md")
    29	
    30	
    31	def load_fixtures():
    32	    with open(FIXTURES_PATH, encoding="utf-8") as fh:
    33	        return json.load(fh)
    34	
    35	
    36	def _in_band(score, lo=None, hi=None):
    37	    if lo is not None and score < lo:
    38	        return False
    39	    if hi is not None and score > hi:
    40	        return False
    41	    return True
    42	
    43	
    44	def run_deterministic(data):
    45	    """Assert detector scores land in the declared bands. Returns (passes, fails)."""
    46	    threshold = data["baseline_threshold"]
    47	    passes = fails = 0
    48	    miss = total = 0
    49	
    50	    print("=== Deterministic check (detector score bands) ===\n")
    51	    for f in data["fixtures"]:
    52	        before = analyze(f["before"])["score"]
    53	        after = analyze(f["after"])["score"]
    54	
    55	        ok = True
    56	        reasons = []
    57	        if not _in_band(before, f.get("before_band_min"), f.get("before_band_max")):
    58	            ok = False
    59	            reasons.append(
    60	                f"before={before} outside "
    61	                f"[{f.get('before_band_min', '-')}, {f.get('before_band_max', '-')}]")
    62	        if not _in_band(after, hi=f.get("after_band_max")):
    63	            ok = False
    64	            reasons.append(f"after={after} > {f.get('after_band_max')}")
    65	
    66	        if ok:
    67	            passes += 1
    68	        else:
    69	            fails += 1
    70	
    71	        # Naive-baseline accounting: a flat threshold flags `before` as AI iff
    72	        # score >= threshold. A "miss" is an AI draft that scores below it.
    73	        total += 1
    74	        caught = before >= threshold
    75	        if not caught:
    76	            miss += 1
    77	
    78	        mark = "PASS" if ok else "FAIL"
    79	        print(f"[{mark}] {f['id']:22} before={before:3} after={after:3} "
    80	              f"baseline={'CATCH' if caught else 'MISS '}")
    81	        for r in reasons:
    82	            print(f"        {r}")
    83	
    84	    miss_pct = 100 * miss / total if total else 0
    85	    print(f"\nNaive-baseline miss rate: {miss}/{total} = {miss_pct:.0f}% "
    86	          f"(threshold={threshold}; calibration target 30-40%)")
    87	    calib_ok = 30 <= miss_pct <= 40
    88	    print(f"Calibration in target band: {'YES' if calib_ok else 'NO'}")
    89	    if not calib_ok:
    90	        fails += 1  # treat out-of-band calibration as a suite failure
    91	    return passes, fails
    92	
    93	
    94	def build_judge_prompt(fixture, rubric_template):
    95	    """Fill the rubric.md judge template for one fixture.
    96	
    97	    no_fabrication is appended to the focus list when the fixture omits it, so the
    98	    judge is ALWAYS told to score it. rubric.md requires no_fabrication for every
    99	    verdict, but 3/8 fixtures don't list it in rubric_focus — without this the
   100	    highest-stakes dimension would go unscored on those fixtures.
   101	    """
   102	    focus = list(fixture["rubric_focus"])
   103	    if "no_fabrication" not in focus:
   104	        focus.append("no_fabrication")
   105	    return (rubric_template
   106	            .replace("{genre}", fixture["genre"])
   107	            .replace("{subtle_tell}", fixture.get("subtle_tell",
   108	                     "obvious AI vocabulary and formatting"))
   109	            .replace("{rubric_focus}", ", ".join(focus))
   110	            .replace("{before}", fixture["before"])
   111	            .replace("{after}", fixture["after"]))
   112	
   113	
   114	def _extract_judge_template():
   115	    """Pull the fenced judge-prompt template out of rubric.md."""
   116	    with open(RUBRIC_PATH, encoding="utf-8") as fh:
   117	        text = fh.read()
   118	    start = text.find("```", text.find("Judge prompt template"))
   119	    end = text.find("```", start + 3)
   120	    return text[start + 3:end].strip()
   121	
   122	
   123	def run_judge(data):
   124	    """Score fixtures with the optional LLM judge, or SKIP when unconfigured.
   125	
   126	    Honesty stance: when no judge is configured (no key, or not opted in via
   127	    AIWS_JUDGE_RUN=1) we print the filled prompt heads and mark every fixture
   128	    SKIPPED — we never fabricate a verdict offline. When a judge IS configured we
   129	    POST each prompt, parse the per-dimension PASS/FAIL lines, and RE-COMPUTE the
   130	    verdict in Python (no_fabrication-overrides-FAIL, per rubric.md) instead of
   131	    trusting the model's self-reported VERDICT line. A transport/auth error raises
   132	    loudly (caller exits nonzero) — never a silent SKIP.
   133	
   134	    Returns (passes, fails, skipped, live_error). The judge is ADVISORY in v1:
   135	    its PASS/FAIL counts do NOT drive the process exit code. The ONE judge
   136	    condition that does is `live_error` — configured but 0/N scored, meaning the
   137	    provider response envelope likely changed (a broken harness, surfaced loudly).
   138	    """
   139	    from fixtures import judge  # lazy: never imported on the deterministic path
   140	    template = _extract_judge_template()
   141	    configured = judge.is_configured()
   142	
   143	    print("\n=== LLM-judge check ===")
   144	    if not configured:
   145	        print("No judge configured (set AIWS_JUDGE_URL/MODEL/KEY + AIWS_JUDGE_RUN=1) "
   146	              "— emitting the prompts that WOULD be sent, marked SKIPPED.\n")
   147	    else:
   148	        print("Judge configured — scoring each fixture against the rubric.\n")
   149	
   150	    passes = fails = skipped = 0
   151	    agree = gold_total = 0
   152	    for f in data["fixtures"]:
   153	        prompt = build_judge_prompt(f, template)
   154	
   155	        if not configured:
   156	            skipped += 1
   157	            print(f"[SKIP] {f['id']} (focus: {', '.join(f['rubric_focus'])})")
   158	            # Show the first 2 lines of the filled prompt as proof it built.
   159	            head = "\n".join(prompt.splitlines()[:2])
   160	            print(f"        prompt[0:2]: {head[:90]}...")
   161	            continue
   162	
   163	        raw = judge.score(prompt)  # raises JudgeError on transport/auth (loud)
   164	        verdict = (judge.aggregate([judge.parse_dimension_lines(raw)],
   165	                                   f["rubric_focus"]) if raw is not None else None)
   166	        if verdict is None:
   167	            skipped += 1
   168	            print(f"[SKIP] {f['id']} — no parseable verdict returned")
   169	            continue
   170	
   171	        if verdict == "PASS":
   172	            passes += 1
   173	        else:
   174	            fails += 1
   175	        gold = f.get("expected_verdict")
   176	        if gold is not None:
   177	            gold_total += 1
   178	            agree += int(gold == verdict)
   179	        print(f"[{verdict}] {f['id']}" + (f"  (gold={gold})" if gold else ""))
   180	
   181	    scored = passes + fails
   182	    if not configured:
   183	        print(f"\nLLM-judge: 0 scored, all {skipped} SKIPPED "
   184	              f"(configure a judge to run).")
   185	        return passes, fails, skipped, False
   186	
   187	    print(f"\nLLM-judge: {scored} scored ({passes} PASS / {fails} FAIL), "
   188	          f"{skipped} skipped.")
   189	    if gold_total:
   190	        print(f"Judge-vs-gold agreement: {agree}/{gold_total} "
   191	              f"(advisory — directional only at this n; NOT kappa).")
   192	
   193	    # Liveness: configured but nothing scored => provider envelope likely changed.
   194	    # This is the one judge condition that fails the run (a broken harness, loud),
   195	    # distinct from the keyless all-SKIP path above which exits 0.
   196	    live_error = scored == 0
   197	    if live_error:
   198	        print(f"ERROR: judge configured but scored 0/{len(data['fixtures'])} — "
   199	              f"provider response envelope likely changed "
   200	              f"(check AIWS_JUDGE_URL/MODEL).")
   201	    return passes, fails, skipped, live_error
   202	
   203	
   204	def main(argv=None):
   205	    argv = argv if argv is not None else sys.argv[1:]
   206	    ap = argparse.ArgumentParser(description="Run before/after eval fixtures.")
   207	    ap.add_argument("--judge", action="store_true",
   208	                    help="also run the LLM-judge half (SKIPPED unless a judge is "
   209	                         "configured via AIWS_JUDGE_* env vars)")
   210	    args = ap.parse_args(argv)
   211	
   212	    data = load_fixtures()
   213	    passes, fails = run_deterministic(data)
   214	
   215	    # The judge is ADVISORY: its PASS/FAIL counts do NOT change the exit code, so
   216	    # CI (which never passes --judge and sets no key) stays deterministic and
   217	    # key-free. The only judge condition that fails the run is a configured-but-
   218	    # broken judge (live_error: scored 0/N) — a harness error, surfaced loudly.
   219	    judge_live_error = False
   220	    if args.judge:
   221	        _jp, _jf, _js, judge_live_error = run_judge(data)
   222	
   223	    print(f"\nDeterministic: {passes} passed, {fails} failed.")
   224	    return 1 if (fails or judge_live_error) else 0
   225	
   226	
   227	if __name__ == "__main__":
   228	    sys.exit(main())

 succeeded in 382ms:
     1	"""Unit tests for the fixtures harness. Run: python3 -m unittest discover.
     2	
     3	These tests assert the fixture SUITE is well-formed and stays calibrated:
     4	  - every fixture has the required fields
     5	  - detector scores land in the declared bands (so a fixture can't silently rot)
     6	  - the naive-baseline miss rate stays in the 30-40% calibration band
     7	  - the LLM-judge prompt builds for every fixture (the SKIP path is sound)
     8	"""
     9	
    10	import unittest
    11	
    12	from detector.detector import analyze
    13	from fixtures import judge
    14	from fixtures.run_fixtures import (
    15	    load_fixtures, build_judge_prompt, _extract_judge_template)
    16	
    17	REQUIRED = {"id", "genre", "difficulty", "before", "after",
    18	            "rubric_focus", "expect_baseline"}
    19	
    20	
    21	class FixtureShape(unittest.TestCase):
    22	    def test_all_fixtures_have_required_fields(self):
    23	        for f in load_fixtures()["fixtures"]:
    24	            missing = REQUIRED - set(f)
    25	            self.assertFalse(missing, f"{f.get('id')} missing {missing}")
    26	
    27	    def test_four_genres_present(self):
    28	        genres = {f["genre"] for f in load_fixtures()["fixtures"]}
    29	        self.assertEqual(genres, {"tweet", "linkedin", "readme", "memo"})
    30	
    31	
    32	class ScoreBands(unittest.TestCase):
    33	    def test_before_after_scores_in_band(self):
    34	        for f in load_fixtures()["fixtures"]:
    35	            before = analyze(f["before"])["score"]
    36	            after = analyze(f["after"])["score"]
    37	            if "before_band_min" in f:
    38	                self.assertGreaterEqual(before, f["before_band_min"],
    39	                                        f"{f['id']} before={before}")
    40	            if "before_band_max" in f:
    41	                self.assertLessEqual(before, f["before_band_max"],
    42	                                     f"{f['id']} before={before}")
    43	            self.assertLessEqual(after, f["after_band_max"],
    44	                                 f"{f['id']} after={after}")
    45	
    46	
    47	class Calibration(unittest.TestCase):
    48	    def test_naive_baseline_misses_30_to_40_percent(self):
    49	        data = load_fixtures()
    50	        thr = data["baseline_threshold"]
    51	        miss = sum(1 for f in data["fixtures"]
    52	                   if analyze(f["before"])["score"] < thr)
    53	        total = len(data["fixtures"])
    54	        pct = 100 * miss / total
    55	        self.assertTrue(30 <= pct <= 40,
    56	                        f"miss rate {pct:.0f}% outside 30-40% target")
    57	
    58	    def test_expect_baseline_matches_actual(self):
    59	        # The declared expect_baseline must match what the detector actually does.
    60	        data = load_fixtures()
    61	        thr = data["baseline_threshold"]
    62	        for f in data["fixtures"]:
    63	            caught = analyze(f["before"])["score"] >= thr
    64	            expected = "catch" if caught else "miss"
    65	            self.assertEqual(f["expect_baseline"], expected,
    66	                             f"{f['id']}: declared {f['expect_baseline']} "
    67	                             f"but detector would {expected}")
    68	
    69	
    70	class JudgePrompt(unittest.TestCase):
    71	    def test_prompt_builds_for_every_fixture(self):
    72	        template = _extract_judge_template()
    73	        self.assertIn("{before}", template)  # template has the slots
    74	        for f in load_fixtures()["fixtures"]:
    75	            prompt = build_judge_prompt(f, template)
    76	            # All slots filled — no stray placeholders left.
    77	            for slot in ("{before}", "{after}", "{genre}", "{rubric_focus}"):
    78	                self.assertNotIn(slot, prompt, f"{f['id']} left {slot} unfilled")
    79	            self.assertIn(f["before"], prompt)
    80	            self.assertIn(f["after"], prompt)
    81	
    82	
    83	class JudgePromptAlwaysScoresNoFabrication(unittest.TestCase):
    84	    """no_fabrication must be requested for EVERY fixture, even the 3 whose
    85	    rubric_focus omits it — otherwise the highest-stakes dimension goes
    86	    unscored on those fixtures."""
    87	
    88	    def test_every_prompt_requests_no_fabrication(self):
    89	        template = _extract_judge_template()
    90	        for f in load_fixtures()["fixtures"]:
    91	            prompt = build_judge_prompt(f, template)
    92	            self.assertIn("no_fabrication", prompt,
    93	                          f"{f['id']} prompt does not request no_fabrication")
    94	
    95	
    96	class GoldLabels(unittest.TestCase):
    97	    def test_expected_verdict_is_valid_when_present(self):
    98	        for f in load_fixtures()["fixtures"]:
    99	            gv = f.get("expected_verdict")
   100	            if gv is not None:
   101	                self.assertIn(gv, ("PASS", "FAIL"),
   102	                              f"{f['id']} expected_verdict={gv!r} not PASS/FAIL")
   103	
   104	
   105	class JudgeParsing(unittest.TestCase):
   106	    """Parse + aggregate the model's verdict from CANNED responses — no network,
   107	    no key, runs in CI. Guards the judge logic the way ScoreBands/Calibration
   108	    guard the deterministic half."""
   109	
   110	    def test_clean_all_pass(self):
   111	        text = ("meaning_preserved: PASS — facts kept\n"
   112	                "tells_removed: PASS — vocab cleaned\n"
   113	                "voice_kept: PASS — sounds human\n"
   114	                "no_fabrication: PASS — nothing invented\n"
   115	                "VERDICT: PASS")
   116	        verdict = judge.aggregate([judge.parse_dimension_lines(text)],
   117	                                  ["meaning_preserved", "tells_removed", "voice_kept"])
   118	        self.assertEqual(verdict, "PASS")
   119	
   120	    def test_no_fabrication_fail_forces_overall_fail(self):
   121	        # focus does NOT list no_fabrication (mirrors readme-01) yet a fabricated
   122	        # rewrite must still FAIL — the load-bearing asymmetry. Also proves we
   123	        # IGNORE the model's self-reported "VERDICT: PASS" line.
   124	        text = ("meaning_preserved: PASS\n"
   125	                "tells_removed: PASS\n"
   126	                "specificity_added: PASS\n"
   127	                "no_fabrication: FAIL — invented a 2GB figure not in the source\n"
   128	                "VERDICT: PASS")
   129	        verdict = judge.aggregate([judge.parse_dimension_lines(text)],
   130	                                  ["meaning_preserved", "tells_removed",
   131	                                   "specificity_added"])
   132	        self.assertEqual(verdict, "FAIL")
   133	
   134	    def test_fabrication_trap_caught(self):
   135	        # A fluent rewrite that invents a metric: every other dim PASS, only
   136	        # no_fabrication FAIL. The single discrimination the judge exists to make.
   137	        text = ("meaning_preserved: PASS\n"
   138	                "voice_kept: PASS\n"
   139	                "genre_fit: PASS\n"
   140	                "no_fabrication: FAIL — '37% faster' appears nowhere in before\n"
   141	                "VERDICT: PASS")
   142	        verdict = judge.aggregate([judge.parse_dimension_lines(text)],
   143	                                  ["voice_kept", "genre_fit"])
   144	        self.assertEqual(verdict, "FAIL")
   145	
   146	    def test_focus_dim_fail_forces_fail(self):
   147	        text = ("meaning_preserved: FAIL — dropped the retention number\n"
   148	                "tells_removed: PASS\n"
   149	                "no_fabrication: PASS\n"
   150	                "VERDICT: FAIL")
   151	        verdict = judge.aggregate([judge.parse_dimension_lines(text)],
   152	                                  ["meaning_preserved", "tells_removed"])
   153	        self.assertEqual(verdict, "FAIL")
   154	
   155	    def test_unparseable_returns_none(self):
   156	        text = "The rewrite reads well overall and keeps the meaning."
   157	        self.assertEqual(judge.parse_dimension_lines(text), {})
   158	        self.assertIsNone(
   159	            judge.aggregate([judge.parse_dimension_lines(text)], ["voice_kept"]))
   160	
   161	    def test_missing_required_dim_returns_none(self):
   162	        # no_fabrication line absent -> can't enforce the load-bearing rule ->
   163	        # SKIP (None), never a fabricated PASS.
   164	        text = ("meaning_preserved: PASS\n"
   165	                "tells_removed: PASS\n"
   166	                "specificity_added: PASS")
   167	        self.assertIsNone(
   168	            judge.aggregate([judge.parse_dimension_lines(text)],
   169	                            ["meaning_preserved", "tells_removed",
   170	                             "specificity_added"]))
   171	
   172	    def test_parse_excludes_self_reported_verdict_line(self):
   173	        dims = judge.parse_dimension_lines("voice_kept: PASS\nVERDICT: FAIL")
   174	        self.assertEqual(dims, {"voice_kept": "PASS"})
   175	        self.assertNotIn("verdict", dims)
   176	
   177	    def test_majority_vote_across_reps(self):
   178	        reps = [{"meaning_preserved": "PASS", "no_fabrication": "PASS"},
   179	                {"meaning_preserved": "FAIL", "no_fabrication": "PASS"},
   180	                {"meaning_preserved": "PASS", "no_fabrication": "PASS"}]
   181	        self.assertEqual(judge.aggregate(reps, ["meaning_preserved"]), "PASS")
   182	
   183	    def test_majority_vote_tie_resolves_fail(self):
   184	        reps = [{"meaning_preserved": "PASS", "no_fabrication": "PASS"},
   185	                {"meaning_preserved": "FAIL", "no_fabrication": "PASS"}]
   186	        self.assertEqual(judge.aggregate(reps, ["meaning_preserved"]), "FAIL")
   187	
   188	
   189	class JudgeGate(unittest.TestCase):
   190	    """The 3-state gate, exercised with NO network."""
   191	
   192	    def test_not_configured_by_default_returns_none(self):
   193	        import os
   194	        from unittest import mock
   195	        with mock.patch.dict(os.environ, {"AIWS_JUDGE_RUN": "0"}, clear=False):
   196	            self.assertFalse(judge.is_configured())
   197	            self.assertIsNone(judge.score("anything"))
   198	
   199	    def test_key_without_optin_does_not_fire(self):
   200	        # Credentials present but AIWS_JUDGE_RUN unset -> still not configured, so
   201	        # a stray key in the environment cannot trigger a billed call.
   202	        import os
   203	        from unittest import mock
   204	        env = {"AIWS_JUDGE_URL": "https://x/v1", "AIWS_JUDGE_MODEL": "m",
   205	               "AIWS_JUDGE_KEY": "sk-test", "AIWS_JUDGE_RUN": "0"}
   206	        with mock.patch.dict(os.environ, env, clear=True):
   207	            self.assertFalse(judge.is_configured())
   208	            self.assertIsNone(judge.score("anything"))
   209	
   210	
   211	class CIClean(unittest.TestCase):
   212	    """The 'CI stays stdlib-only / key-free' invariant, enforced as a TEST
   213	    rather than a convention."""
   214	
   215	    def test_judge_not_imported_at_module_load(self):
   216	        # judge must be imported lazily INSIDE run_judge, never at run_fixtures
   217	        # module load — so the deterministic path can't pull in the network code.
   218	        import fixtures.run_fixtures as rf
   219	        self.assertFalse(hasattr(rf, "judge"),
   220	                         "run_fixtures imported judge at module load (must be lazy)")
   221	
   222	    def test_deterministic_and_offline_judge_make_no_network_call(self):
   223	        import io
   224	        import os
   225	        import contextlib
   226	        import urllib.request
   227	        from unittest import mock
   228	        from fixtures.run_fixtures import run_deterministic, main
   229	
   230	        def boom(*a, **k):
   231	            raise AssertionError("network call attempted in a no-key run")
   232	
   233	        buf = io.StringIO()
   234	        with mock.patch.dict(os.environ, {"AIWS_JUDGE_RUN": "0"}, clear=False), \
   235	                mock.patch.object(urllib.request, "urlopen", boom), \
   236	                contextlib.redirect_stdout(buf):
   237	            run_deterministic(load_fixtures())   # deterministic path
   238	            rc_plain = main([])                  # CI's exact invocation
   239	            rc_judge = main(["--judge"])         # offline judge -> all SKIP
   240	        self.assertEqual(rc_plain, 0)
   241	        self.assertEqual(rc_judge, 0)
   242	
   243	
   244	class JudgeIntegration(unittest.TestCase):
   245	    """run_judge end-to-end with a STUBBED model (no network, no key spend):
   246	    proves the configured path scores every fixture, computes judge-vs-gold
   247	    agreement, and that the liveness 0/N gate fires when nothing parses."""
   248	
   249	    def _run(self, fake_score):
   250	        import os
   251	        import io
   252	        import contextlib
   253	        from unittest import mock
   254	        from fixtures.run_fixtures import run_judge
   255	        env = {"AIWS_JUDGE_URL": "https://x", "AIWS_JUDGE_MODEL": "m",
   256	               "AIWS_JUDGE_KEY": "k", "AIWS_JUDGE_RUN": "1"}
   257	        buf = io.StringIO()
   258	        with mock.patch.dict(os.environ, env, clear=True), \
   259	                mock.patch("fixtures.judge.score", side_effect=fake_score), \
   260	                contextlib.redirect_stdout(buf):
   261	            result = run_judge(load_fixtures())
   262	        return result, buf.getvalue()
   263	
   264	    def test_all_pass_scores_full_agreement_no_live_error(self):
   265	        # Emit PASS for every dimension any fixture could ask about (+ the base
   266	        # six), so each fixture's required dims are present and PASS.
   267	        all_dims = {"meaning_preserved", "tells_removed", "no_fabrication",
   268	                    "voice_kept", "specificity_added", "genre_fit"}
   269	        for f in load_fixtures()["fixtures"]:
   270	            all_dims |= set(f["rubric_focus"])
   271	        reply = "\n".join(f"{d}: PASS" for d in all_dims)
   272	        (p, f, s, live), out = self._run(lambda prompt: reply)
   273	        self.assertEqual((p, f, s, live), (8, 0, 0, False))
   274	        self.assertIn("agreement: 8/8", out)  # all gold=PASS, judge=PASS
   275	
   276	    def test_all_unparseable_triggers_live_error(self):
   277	        (p, f, s, live), out = self._run(lambda prompt: "no verdict here")
   278	        self.assertEqual((p, f), (0, 0))
   279	        self.assertTrue(live)
   280	        self.assertIn("envelope likely changed", out)
   281	
   282	    def test_fabrication_makes_a_fixture_fail(self):
   283	        # Same all-PASS reply but no_fabrication FAIL -> every fixture FAILs
   284	        # overall (no_fabrication is always required), agreement drops to 0/8.
   285	        all_dims = {"meaning_preserved", "tells_removed", "voice_kept",
   286	                    "specificity_added", "genre_fit"}
   287	        for f in load_fixtures()["fixtures"]:
   288	            all_dims |= set(f["rubric_focus"])
   289	        all_dims.discard("no_fabrication")
   290	        reply = "\n".join(f"{d}: PASS" for d in all_dims) + "\nno_fabrication: FAIL"
   291	        (p, f, s, live), out = self._run(lambda prompt: reply)
   292	        self.assertEqual((p, f, s, live), (0, 8, 0, False))
   293	        self.assertIn("agreement: 0/8", out)
   294	
   295	
   296	if __name__ == "__main__":
   297	    unittest.main()

 succeeded in 383ms:
     1	"""Optional LLM-judge for the before/after fixtures (Phase 2a wire-in).
     2	
     3	DEV-ONLY + OPT-IN. This module is the ONLY place the eval can talk to a model.
     4	It is never imported at module load and never reached by the deterministic CI
     5	path: `run_all.sh` runs `python3 -m fixtures.run_fixtures` (no `--judge`) with no
     6	key, so CI stays Python-3-stdlib-only and green. This module uses only the stdlib
     7	(`urllib` + `json` + `os`) — wiring a judge adds NO pip line to CI.
     8	
     9	Honesty stance (inherited from run_fixtures.run_judge): we NEVER fabricate a
    10	verdict. If the judge is not configured, the caller SKIPs.
    11	
    12	Three-state gate (`score()`):
    13	  1. NOT configured (any of URL/MODEL/KEY missing, or AIWS_JUDGE_RUN != "1")
    14	     -> return None  ->  caller SKIPs (process exits 0; the offline honesty path).
    15	  2. configured + opted in
    16	     -> ONE HTTP POST; return the model's raw text.
    17	  3. configured but the call fails (transport / auth / HTTP 4xx-5xx)
    18	     -> raise JudgeError (LOUD; the caller exits nonzero). An auth failure must
    19	        NOT be laundered into a SKIP (CLAUDE.md: "FAIL LOUDLY if config and
    20	        runtime disagree").
    21	
    22	Provider is PURELY env-driven — NO baked-in vendor — to keep the
    23	host-provides-the-model philosophy and avoid a second-vendor dependency:
    24	
    25	  AIWS_JUDGE_URL    full chat/completions endpoint URL (e.g. an OpenAI-compatible
    26	                    .../v1/chat/completions)
    27	  AIWS_JUDGE_MODEL  model id to send
    28	  AIWS_JUDGE_KEY    the API key (read once, sent as a Bearer header, never logged)
    29	  AIWS_JUDGE_RUN    must be "1" to actually spend — a stray key in the env alone
    30	                    will NOT trigger a billed call.
    31	
    32	Cross-family note: if your rewrites come from Claude, point AIWS_JUDGE_MODEL at a
    33	different model family to avoid judge self-preference (~10-25% PASS inflation).
    34	For v1 the fixtures' `after` strings are hand-written (not model output), so this
    35	is a recommendation, not a hard requirement — see evals/README.md.
    36	"""
    37	
    38	import json
    39	import os
    40	import re
    41	import urllib.error
    42	import urllib.request
    43	
    44	# no_fabrication is ALWAYS required for an overall PASS, even when a fixture's
    45	# rubric_focus does not list it (rubric.md: "Verdict aggregation"). This is the
    46	# single load-bearing asymmetry the judge exists to enforce.
    47	ALWAYS_REQUIRED = "no_fabrication"
    48	
    49	# One attempt, generous timeout. No retry/backoff in v1 — retry logic is the part
    50	# a minimal-debugger owner can't maintain, and a clean loud failure is better than
    51	# silent flakiness (the liveness check in run_judge surfaces a dead provider).
    52	_TIMEOUT_S = 60
    53	
    54	# Matches a rubric per-dimension line: "<snake_case_dim>: PASS|FAIL — reason".
    55	_DIM_LINE = re.compile(r"^\s*([a-z][a-z_]+)\s*:\s*(PASS|FAIL)\b", re.IGNORECASE)
    56	
    57	
    58	class JudgeError(RuntimeError):
    59	    """Transport/auth/HTTP failure — must reach the user loudly, never a SKIP."""
    60	
    61	
    62	def is_configured():
    63	    """True only when fully configured AND explicitly opted in to spend.
    64	
    65	    Requiring AIWS_JUDGE_RUN=="1" on top of the credentials means a stray
    66	    API key already in the environment cannot, by itself, trigger a billed call.
    67	    """
    68	    return bool(os.environ.get("AIWS_JUDGE_URL")
    69	                and os.environ.get("AIWS_JUDGE_MODEL")
    70	                and os.environ.get("AIWS_JUDGE_KEY")
    71	                and os.environ.get("AIWS_JUDGE_RUN") == "1")
    72	
    73	
    74	def score(prompt):
    75	    """Return the model's raw text for `prompt`, or None if not configured.
    76	
    77	    State 1 (not configured) -> None (caller SKIPs).
    78	    State 2 (configured)     -> one POST, return raw text (or None if the 200
    79	                               response carries no extractable text — the caller
    80	                               treats that as unparseable and the liveness check
    81	                               in run_judge turns a whole-suite failure loud).
    82	    State 3 (call fails)     -> raise JudgeError.
    83	    """
    84	    if not is_configured():
    85	        return None  # honesty stance: no fabrication, caller SKIPs
    86	
    87	    url = os.environ["AIWS_JUDGE_URL"]
    88	    model = os.environ["AIWS_JUDGE_MODEL"]
    89	    key = os.environ["AIWS_JUDGE_KEY"]
    90	
    91	    body = json.dumps({
    92	        "model": model,
    93	        "messages": [{"role": "user", "content": prompt}],
    94	        "temperature": 0,
    95	    }).encode("utf-8")
    96	
    97	    req = urllib.request.Request(url, data=body, method="POST")
    98	    req.add_header("Content-Type", "application/json")
    99	    req.add_header("Authorization", f"Bearer {key}")  # never logged/printed
   100	
   101	    try:
   102	        with urllib.request.urlopen(req, timeout=_TIMEOUT_S) as resp:
   103	            payload = json.loads(resp.read().decode("utf-8"))
   104	    except urllib.error.HTTPError as e:
   105	        # 401/403/429/5xx etc. Surface the status, never the key. Loud, not SKIP.
   106	        raise JudgeError(
   107	            f"judge HTTP {e.code} from provider — check "
   108	            f"AIWS_JUDGE_URL / AIWS_JUDGE_KEY / AIWS_JUDGE_MODEL") from None
   109	    except (urllib.error.URLError, TimeoutError, OSError) as e:
   110	        raise JudgeError(f"judge transport error: {e}") from None
   111	
   112	    return _extract_text(payload)
   113	
   114	
   115	def _extract_text(payload):
   116	    """Pull assistant text out of a provider response envelope, tolerantly.
   117	
   118	    Handles the two common shapes (OpenAI chat-completions, Anthropic messages)
   119	    plus a couple of fallbacks. Returns None if no text is found — run_judge's
   120	    liveness check turns an all-None run (with a key present) into a loud nonzero
   121	    exit ("provider envelope likely changed"), so a silent shape drift can't
   122	    masquerade as 'all SKIPPED'.
   123	    """
   124	    if not isinstance(payload, dict):
   125	        return None
   126	    # OpenAI-style: choices[0].message.content
   127	    choices = payload.get("choices")
   128	    if isinstance(choices, list) and choices:
   129	        msg = choices[0].get("message") if isinstance(choices[0], dict) else None
   130	        if isinstance(msg, dict) and isinstance(msg.get("content"), str):
   131	            return msg["content"]
   132	        # some completion APIs put text directly on the choice
   133	        if isinstance(choices[0], dict) and isinstance(choices[0].get("text"), str):
   134	            return choices[0]["text"]
   135	    # Anthropic-style: content[0].text
   136	    content = payload.get("content")
   137	    if isinstance(content, list) and content and isinstance(content[0], dict):
   138	        if isinstance(content[0].get("text"), str):
   139	            return content[0]["text"]
   140	    # Last-ditch flat fields.
   141	    for k in ("output_text", "text", "completion"):
   142	        if isinstance(payload.get(k), str):
   143	            return payload[k]
   144	    return None
   145	
   146	
   147	def parse_dimension_lines(model_text):
   148	    """Parse a model verdict into {dimension: 'PASS'|'FAIL'}.
   149	
   150	    Reads the per-dimension lines (rubric.md output format) and IGNORES the
   151	    model's self-reported final 'VERDICT:' line — we recompute the verdict
   152	    ourselves in aggregate(). Returns {} when nothing parses.
   153	    """
   154	    out = {}
   155	    if not isinstance(model_text, str):
   156	        return out
   157	    for line in model_text.splitlines():
   158	        m = _DIM_LINE.match(line)
   159	        if not m:
   160	            continue
   161	        dim = m.group(1).lower()
   162	        if dim == "verdict":  # never trust the model's self-reported overall line
   163	            continue
   164	        out[dim] = m.group(2).upper()
   165	    return out
   166	
   167	
   168	def majority_vote(per_rep_results):
   169	    """Merge N per-rep dimension dicts into one by majority vote per dimension.
   170	
   171	    For v1 reps=1 this just returns a copy. Ties (or a 50/50 split) resolve to
   172	    FAIL — the conservative choice for a judge whose job is to catch problems.
   173	    """
   174	    if not per_rep_results:
   175	        return {}
   176	    if len(per_rep_results) == 1:
   177	        return dict(per_rep_results[0])
   178	    dims = set().union(*(d.keys() for d in per_rep_results))
   179	    merged = {}
   180	    for d in dims:
   181	        passes = sum(1 for r in per_rep_results if r.get(d) == "PASS")
   182	        fails = sum(1 for r in per_rep_results if r.get(d) == "FAIL")
   183	        merged[d] = "PASS" if passes > fails else "FAIL"
   184	    return merged
   185	
   186	
   187	def aggregate(per_rep_results, rubric_focus):
   188	    """Recompute the overall verdict in Python from per-dimension results.
   189	
   190	    overall PASS  iff  every required dimension is present AND PASS, where
   191	    required = the fixture's rubric_focus PLUS no_fabrication (always).
   192	    Returns None (-> SKIP, never a fake PASS) if any required dimension is
   193	    missing from the model's output — we do not guess the load-bearing call.
   194	    """
   195	    merged = majority_vote(per_rep_results)
   196	    required = set(rubric_focus) | {ALWAYS_REQUIRED}
   197	    if any(dim not in merged for dim in required):
   198	        return None  # incomplete verdict — SKIP, do not fabricate
   199	    return "PASS" if all(merged[dim] == "PASS" for dim in required) else "FAIL"

hook: PostToolUse
hook: PostToolUse
hook: PostToolUse
hook: PostToolUse
hook: PostToolUse
hook: PostToolUse
 succeeded in 2017ms:
     1	name: CI
     2	
     3	on:
     4	  push:
     5	    branches: [main]
     6	  pull_request:
     7	
     8	jobs:
     9	  checks:
    10	    name: regression checks (stdlib-only)
    11	    runs-on: ubuntu-latest
    12	    steps:
    13	      - uses: actions/checkout@v4
    14	      - uses: actions/setup-python@v5
    15	        with:
    16	          python-version: "3.12"
    17	      - name: Run all v1 checks
    18	        run: bash skills/ai-writing-suite/evals/run_all.sh
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
feat/phase2a-judge-wirein
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
1278567e4be76056ffced4472ec115f0c5f091f8
2026-06-08T02:47:48Z

hook: PostToolUse Completed
hook: PostToolUse Completed
hook: PostToolUse Completed
hook: PostToolUse Completed
hook: PostToolUse Completed
hook: PostToolUse Completed
codex
The core wiring matches the intended lazy/opt-in shape at first read. I’m checking the fixture diff now because the calibration invariant depends on whether the data changed only by `expected_verdict`.
hook: PreToolUse
hook: PreToolUse
hook: PreToolUse
hook: PreToolUse
hook: PreToolUse
hook: PreToolUse
hook: PreToolUse Completed
hook: PreToolUse Completed
hook: PreToolUse Completed
hook: PreToolUse Completed
hook: PreToolUse Completed
hook: PreToolUse Completed
codex(16150) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
codex(16152) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
codex(16153) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
codex(16154) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
codex(16155) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
codex(16156) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
exec
/bin/zsh -lc 'nl -ba skills/ai-writing-suite/evals/fixtures/fixtures.json' in /Users/surahli/Documents/ai-writing-suite
exec
/bin/zsh -lc 'git diff --name-status main...HEAD' in /Users/surahli/Documents/ai-writing-suite
exec
/bin/zsh -lc 'git diff main...HEAD -- skills/ai-writing-suite/evals/fixtures/fixtures.json' in /Users/surahli/Documents/ai-writing-suite
exec
/bin/zsh -lc "python3 -m unittest discover -s skills/ai-writing-suite/evals -p 'test_*.py'" in /Users/surahli/Documents/ai-writing-suite
 succeeded in 6ms:
     1	{
     2	  "_doc": "Before/after LLM-judge fixtures across 4 genres (tweet/linkedin/readme/memo). Each fixture: an AI-shaped `before`, a good human `after`, and what we expect. `before_band_min`/`before_band_max`/`after_band_max` are detector score-band expectations (mechanical, deterministic regression guards bracketing the observed score). `rubric_focus` lists which rubric dimensions the LLM judge should weigh. Difficulty is calibrated so a NAIVE baseline (flag-if-detector-score >= baseline_threshold) misses ~30-40% of the `before` items: the `subtle` ones are AI-written but score LOW because they avoid vocabulary tells and lean on structural/rhythm tells a flat threshold underweights. See README calibration section. `expected_verdict` (PASS|FAIL) is the owner's gold label for advisory judge-vs-gold agreement: all current fixtures are good rewrites (PASS); FAIL exemplars live in the unit tests (test_fixtures.py), not here, to preserve the 30-40% calibration band.",
     3	  "baseline_threshold": 14,
     4	  "fixtures": [
     5	    {
     6	      "id": "tweet-01-obvious",
     7	      "expected_verdict": "PASS",
     8	      "genre": "tweet",
     9	      "difficulty": "obvious",
    10	      "before": "In today's ever-evolving landscape, we're thrilled to delve into a game-changing paradigm. This seamless, robust solution will revolutionize how you work. The future looks bright! 🚀 #innovation #growth #tech #startup #ai #future #buildinpublic",
    11	      "after": "Shipped the new import flow today. Cut setup from 11 steps to 3. Early users went from 40% drop-off to 12%.",
    12	      "before_band_min": 45,
    13	      "after_band_max": 20,
    14	      "rubric_focus": [
    15	        "meaning_preserved",
    16	        "tells_removed",
    17	        "voice_kept",
    18	        "no_fabrication"
    19	      ],
    20	      "expect_baseline": "catch"
    21	    },
    22	    {
    23	      "id": "tweet-02-subtle",
    24	      "expected_verdict": "PASS",
    25	      "genre": "tweet",
    26	      "difficulty": "subtle",
    27	      "before": "Spent the week thinking about retrieval. Keyword search is underrated. Vector search is overhyped. Most teams reach for embeddings when an index would do. Worth sitting with that.",
    28	      "after": "Spent the week on retrieval. Keyword search beat our embedding setup on the eval — cheaper, and recall was 4 points higher. We were reaching for vectors out of habit.",
    29	      "before_band_max": 20,
    30	      "after_band_max": 20,
    31	      "rubric_focus": [
    32	        "specificity_added",
    33	        "negative_parallelism_removed",
    34	        "no_fabrication"
    35	      ],
    36	      "expect_baseline": "miss",
    37	      "subtle_tell": "negative parallelism (X is underrated / Y is overhyped), vague 'worth sitting with that' closer, zero specifics — all AI structural tells that carry NO vocabulary words, so a flat detector threshold scores it low and misses it."
    38	    },
    39	    {
    40	      "id": "linkedin-01-obvious",
    41	      "expected_verdict": "PASS",
    42	      "genre": "linkedin",
    43	      "difficulty": "obvious",
    44	      "before": "I recently had the pleasure of attending a pivotal conference. It was truly a transformative experience that underscored the importance of fostering meaningful connections. Moreover, the keynote was a testament to the power of innovation. As we navigate this dynamic ecosystem, let's embrace the journey. What's next? Only time will tell.",
    45	      "after": "Went to the data conf last week. One talk stuck with me: a team at Stripe cut their feature pipeline from 6 hours to 40 minutes by dropping a caching layer nobody had questioned in two years. Sometimes the win is deleting code.",
    46	      "before_band_min": 28,
    47	      "after_band_max": 20,
    48	      "rubric_focus": [
    49	        "meaning_preserved",
    50	        "tells_removed",
    51	        "specificity_added",
    52	        "no_fabrication"
    53	      ],
    54	      "expect_baseline": "catch"
    55	    },
    56	    {
    57	      "id": "linkedin-02-subtle",
    58	      "expected_verdict": "PASS",
    59	      "genre": "linkedin",
    60	      "difficulty": "subtle",
    61	      "before": "Three things I learned shipping our first ML model.\n\nFirst, data quality matters more than model choice.\n\nSecond, stakeholders care about latency, not accuracy.\n\nThird, the simplest baseline is often hard to beat.\n\nWhat would you add?",
    62	      "after": "We shipped our first ranking model last month and I was wrong about almost everything going in. I thought the model would be the hard part. It wasn't — a week of cleaning label noise moved offline NDCG more than any architecture change. And the thing the PM actually cared about was p99 latency, which I'd barely measured.",
    63	      "before_band_max": 20,
    64	      "after_band_max": 20,
    65	      "rubric_focus": [
    66	        "rule_of_three_removed",
    67	        "specificity_added",
    68	        "engagement_hook_removed",
    69	        "no_fabrication"
    70	      ],
    71	      "expect_baseline": "miss",
    72	      "subtle_tell": "rule-of-three list scaffolding + 'What would you add?' engagement-bait closer. Reads clean to a vocabulary detector (no tier-1 words) so a flat threshold misses it; an LLM judge keyed to STRUCTURE catches it."
    73	    },
    74	    {
    75	      "id": "readme-01-obvious",
    76	      "expected_verdict": "PASS",
    77	      "genre": "readme",
    78	      "difficulty": "obvious",
    79	      "before": "## Overview\n\nThis comprehensive, cutting-edge library leverages a robust architecture to seamlessly streamline your workflow. It empowers developers to harness the full potential of modern tooling. Whether you're a beginner or an expert, this powerful solution has you covered.",
    80	      "after": "## What this does\n\nParses CSV files up to 2GB without loading them into memory. Streams rows, so it works on machines with 512MB of RAM. No dependencies outside the standard library.",
    81	      "before_band_min": 20,
    82	      "after_band_max": 20,
    83	      "rubric_focus": [
    84	        "meaning_preserved",
    85	        "tells_removed",
    86	        "specificity_added"
    87	      ],
    88	      "expect_baseline": "catch"
    89	    },
    90	    {
    91	      "id": "readme-02-subtle",
    92	      "expected_verdict": "PASS",
    93	      "genre": "readme",
    94	      "difficulty": "subtle",
    95	      "before": "## Installation\n\nTo get started, simply install the package. Once installed, you can begin using it right away. The setup process is designed to be straightforward and intuitive, ensuring a smooth onboarding experience for users of all skill levels.",
    96	      "after": "## Installation\n\n```\npip install fastcsv\n```\n\nPython 3.9+. No other dependencies.",
    97	      "before_band_max": 20,
    98	      "after_band_max": 20,
    99	      "rubric_focus": [
   100	        "filler_removed",
   101	        "specificity_added",
   102	        "meaning_preserved"
   103	      ],
   104	      "expect_baseline": "miss",
   105	      "subtle_tell": "all filler, zero content ('simply', 'right away', 'smooth onboarding experience') but no flagged vocabulary — it's empty calories that a word-list detector rates clean. An LLM judge measuring information density catches it."
   106	    },
   107	    {
   108	      "id": "memo-01-obvious",
   109	      "expected_verdict": "PASS",
   110	      "genre": "memo",
   111	      "difficulty": "obvious",
   112	      "before": "It is important to note that, as we move forward, we must delve into the intricacies of our strategy. Experts believe that fostering a culture of innovation is paramount. Furthermore, this pivotal initiative will undoubtedly elevate our position. Let's break this down step by step to ensure a holistic approach.",
   113	      "after": "We're behind on Q3 targets by 14%. Two causes: the API migration slipped three weeks, and we lost two engineers. Proposed fix: pause the redesign, put everyone on migration, revisit the redesign in October.",
   114	      "before_band_min": 36,
   115	      "after_band_max": 20,
   116	      "rubric_focus": [
   117	        "meaning_preserved",
   118	        "tells_removed",
   119	        "vague_attribution_removed",
   120	        "specificity_added"
   121	      ],
   122	      "expect_baseline": "catch"
   123	    },
   124	    {
   125	      "id": "memo-02-subtle",
   126	      "expected_verdict": "PASS",
   127	      "genre": "memo",
   128	      "difficulty": "subtle",
   129	      "before": "While our current approach has served us well, there is room for improvement. It is important to note that research suggests engagement is trending in a positive direction. That said, we should remain mindful of potential headwinds, and a measured strategy could potentially position us well. Ultimately, this balanced approach will help us capture emerging opportunities going forward.",
   130	      "after": "Sign-ups are up 9% since the March redesign, but week-2 retention dropped from 31% to 24%. We're acquiring people the product doesn't keep. Before we spend more on acquisition, I want a week to dig into the retention cliff.",
   131	      "before_band_min": 12,
   132	      "before_band_max": 25,
   133	      "after_band_max": 20,
   134	      "rubric_focus": [
   135	        "false_concession_removed",
   136	        "hedge_stack_removed",
   137	        "specificity_added",
   138	        "no_fabrication"
   139	      ],
   140	      "expect_baseline": "catch",
   141	      "subtle_tell": "false concession ('served us well, but...'), hedge-stacking ('could potentially position us'), vague-attribution ('research suggests') with NO numbers. This is the BORDERLINE fixture: it scores ~15, just above the naive threshold, so the mechanical detector catches it but only barely — an LLM judge is still needed to confirm the rewrite added real specifics rather than just swapping words."
   142	    }
   143	  ]
   144	}
exec
/bin/zsh -lc 'git diff -- skills/ai-writing-suite/evals/run_all.sh .github/workflows/ci.yml' in /Users/surahli/Documents/ai-writing-suite
exec
/bin/zsh -lc 'bash skills/ai-writing-suite/evals/run_all.sh' in /Users/surahli/Documents/ai-writing-suite
hook: PostToolUse
hook: PostToolUse
hook: PostToolUse
hook: PostToolUse
 succeeded in 406ms:
 succeeded in 553ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead

 succeeded in 553ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead

hook: PostToolUse Completed
hook: PostToolUse Completed
hook: PostToolUse Completed
hook: PostToolUse Completed
 succeeded in 3935ms:
...........................................
----------------------------------------------------------------------
Ran 43 tests in 0.771s

OK

hook: PostToolUse
hook: PostToolUse
 succeeded in 5315ms:
== [1/3] unit tests ==
...........................................
----------------------------------------------------------------------
Ran 43 tests in 0.748s

OK
== [2/3] KB smoke ==
KB smoke test — 3 case(s), 5 index entries

[PASS] Case 1: query -> clarity.md (expected clarity.md, overlap=(1, 1))
[PASS] Case 2: query -> audience.md (expected audience.md, overlap=(1, 0))
[PASS] Case 3: query -> audience.md (expected audience.md, overlap=(4, 1))

All 3 case(s) passed.
== [3/3] fixtures (deterministic + calibration) ==
=== Deterministic check (detector score bands) ===

[PASS] tweet-01-obvious       before= 57 after=  0 baseline=CATCH
[PASS] tweet-02-subtle        before=  0 after=  4 baseline=MISS 
[PASS] linkedin-01-obvious    before= 36 after=  0 baseline=CATCH
[PASS] linkedin-02-subtle     before=  0 after=  4 baseline=MISS 
[PASS] readme-01-obvious      before= 26 after=  0 baseline=CATCH
[PASS] readme-02-subtle       before=  0 after=  0 baseline=MISS 
[PASS] memo-01-obvious        before= 45 after=  0 baseline=CATCH
[PASS] memo-02-subtle         before= 15 after=  0 baseline=CATCH

Naive-baseline miss rate: 3/8 = 38% (threshold=14; calibration target 30-40%)
Calibration in target band: YES

Deterministic: 8 passed, 0 failed.

ALL CHECKS PASSED

hook: PostToolUse Completed
hook: PostToolUse Completed
codex
Verification evidence is clean: 43 unit tests pass, `run_all.sh` passes, and the deterministic fixture run reports `3/8 = 38%`. I’m doing one final adversarial pass over parser/liveness/test gaps before issuing the verdict.
hook: PreToolUse
hook: PreToolUse
hook: PreToolUse
hook: PreToolUse Completed
hook: PreToolUse Completed
hook: PreToolUse Completed
codex(19927) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
codex(19928) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
codex(19929) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
exec
/bin/zsh -lc 'git diff main...HEAD --stat' in /Users/surahli/Documents/ai-writing-suite
exec
/bin/zsh -lc 'git status --short' in /Users/surahli/Documents/ai-writing-suite
exec
/bin/zsh -lc 'nl -ba skills/ai-writing-suite/evals/fixtures/rubric.md' in /Users/surahli/Documents/ai-writing-suite
 succeeded in 0ms:
     1	# LLM-Judge Rubric — comms-polish before/after
     2	
     3	This is the scoring contract for the **judgment** half of the eval. The
     4	mechanical detector (`evals/detector/`) catches vocabulary and density tells; it
     5	cannot tell whether a rewrite *preserved meaning* or *invented a number*. That
     6	is what this rubric is for: a model reads the `before`, the `after`, and the
     7	expected outcome, and scores the rewrite on the dimensions below.
     8	
     9	> **Why both halves exist.** The detector is the cheap, deterministic regression
    10	> gate (runs every commit, no API key). The LLM judge is the quality gate (runs
    11	> on demand, needs a model). A rewrite can pass the detector — score drops to 0 —
    12	> while *failing* the judge by deleting a fact or fabricating evidence. Neither
    13	> half alone is sufficient.
    14	
    15	## Inputs the judge receives
    16	
    17	- `before` — the AI-shaped draft.
    18	- `after` — the candidate human rewrite (this is what's being scored).
    19	- `genre` — tweet / linkedin / readme / memo (sets length + tone expectations).
    20	- `rubric_focus` — the dimensions that matter most for this fixture.
    21	- `subtle_tell` (when present) — what the AI tell actually is, so the judge
    22	  knows what a good rewrite had to remove.
    23	
    24	## Dimensions (score each PASS / FAIL, with a one-line reason)
    25	
    26	| Dimension | PASS when | FAIL when |
    27	| --- | --- | --- |
    28	| `meaning_preserved` | Every claim, fact, number, and name in `before` survives in `after` (unless the fixture asks to add specifics). | A claim was dropped or its meaning changed. |
    29	| `tells_removed` | The AI tells named in `subtle_tell` (or the obvious vocabulary tells) are gone. | A flagged tell still reads as AI. |
    30	| `no_fabrication` | Any new specifics in `after` are plausible *placeholders the author would fill*, not invented facts presented as real. **This is the highest-stakes dimension.** | `after` invents a number, source, or quote that `before` did not contain and presents it as fact. |
    31	| `voice_kept` | `after` reads like a competent human in this genre, not generic corporate rewrite. | `after` traded one robotic register for another. |
    32	| `specificity_added` | Where `before` was vague, `after` is concrete (only scored when in `rubric_focus`). | `after` is still vague / empty calories. |
    33	| `genre_fit` | Length and tone fit the genre (tweet ≤ 280 chars, readme is scannable, memo leads with the decision). | Wrong shape for the channel. |
    34	
    35	Structural-tell dimensions appear in `rubric_focus` by name for fixtures that
    36	target them: `negative_parallelism_removed`, `rule_of_three_removed`,
    37	`engagement_hook_removed`, `false_concession_removed`, `hedge_stack_removed`,
    38	`vague_attribution_removed`, `filler_removed`.
    39	
    40	## Verdict aggregation
    41	
    42	- **PASS overall** = all `rubric_focus` dimensions PASS **and** `no_fabrication`
    43	  PASS (no_fabrication is always required, even when not listed in focus).
    44	- **FAIL overall** = any focus dimension FAIL, or any fabrication.
    45	
    46	## Judge prompt template (zero-shot, model-agnostic)
    47	
    48	```
    49	You are evaluating a prose rewrite. The "before" is AI-shaped writing; the
    50	"after" is a human rewrite of it. Judge ONLY the "after".
    51	
    52	GENRE: {genre}
    53	WHAT THE AI TELL WAS: {subtle_tell or "obvious AI vocabulary and formatting"}
    54	DIMENSIONS TO WEIGH: {rubric_focus}
    55	
    56	BEFORE:
    57	{before}
    58	
    59	AFTER:
    60	{after}
    61	
    62	For each dimension, output: <dimension>: PASS|FAIL — <one-line reason>.
    63	Then output: VERDICT: PASS|FAIL.
    64	Rule: no_fabrication must PASS or the whole verdict is FAIL, regardless of how
    65	good the prose reads.
    66	```
    67	
    68	## What the judge must NOT do
    69	
    70	- Do not reward fluency that came from inventing facts. A vague-but-honest
    71	  rewrite beats a specific-but-fabricated one.
    72	- Do not penalize the `after` for being shorter — concision is the goal.
    73	- Do not re-flag tells the fixture did not ask about (scope to `rubric_focus`).

hook: PostToolUse
hook: PostToolUse
hook: PostToolUse
 succeeded in 166ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead

 succeeded in 180ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
 M skills/ai-writing-suite/evals/README.md
 M skills/ai-writing-suite/evals/fixtures/fixtures.json
 A skills/ai-writing-suite/evals/fixtures/judge.py
 M skills/ai-writing-suite/evals/fixtures/run_fixtures.py
 M skills/ai-writing-suite/evals/fixtures/test_fixtures.py
 A skills/ai-writing-suite/evals/test_voice_contract.py
?? docs/handover-2026-06-02-personal-productivity-skills-next.md
?? docs/handover-2026-06-06-ai-writing-suite-v1.md
?? docs/handover-2026-06-06-v1-shipped.md
?? docs/handover-2026-06-07-publish-and-ci.md
?? docs/plan-phase2-quality-eval-2026-06-07.md
?? docs/plan-publish-cleanup-test-2026-06-07.md
?? docs/session-closeout-2026-06-02-ai-writing-humanizer.md
?? docs/test-plan-v1-2026-06-07.md
?? reviews/

hook: PostToolUse Completed
hook: PostToolUse Completed
hook: PostToolUse Completed
hook: PreToolUse
hook: PreToolUse
hook: PreToolUse Completed
hook: PreToolUse Completed
codex(25466) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
codex(25485) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
hook: PostToolUse
hook: PostToolUse
hook: PostToolUse Completed
hook: PostToolUse Completed
hook: PreToolUse
hook: PreToolUse
hook: PreToolUse Completed
hook: PreToolUse Completed
codex(27758) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
codex(27759) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
exec
/bin/zsh -lc "PYTHONPATH=skills/ai-writing-suite/evals python3 -c \"from fixtures import judge; reps=[{'meaning_preserved':'PASS','no_fabrication':'PASS'}, {'meaning_preserved':'PASS'}, {'meaning_preserved':'PASS'}]; print(judge.aggregate(reps, ['meaning_preserved']))\"" in /Users/surahli/Documents/ai-writing-suite
exec
/bin/zsh -lc "PYTHONPATH=skills/ai-writing-suite/evals python3 -c \"from fixtures.run_fixtures import load_fixtures,build_judge_prompt,_extract_judge_template; f=load_fixtures()['fixtures'][1]; p=build_judge_prompt(f,_extract_judge_template()); print('\\n'.join(p.splitlines()[:8]))\"" in /Users/surahli/Documents/ai-writing-suite
hook: PostToolUse
 succeeded in 594ms:
You are evaluating a prose rewrite. The "before" is AI-shaped writing; the
"after" is a human rewrite of it. Judge ONLY the "after".

GENRE: tweet
WHAT THE AI TELL WAS: {subtle_tell or "obvious AI vocabulary and formatting"}
DIMENSIONS TO WEIGH: specificity_added, negative_parallelism_removed, no_fabrication

BEFORE:

hook: PostToolUse
 succeeded in 871ms:
PASS

hook: PostToolUse Completed
hook: PostToolUse Completed
codex
Findings:

[BLOCKER] `skills/ai-writing-suite/evals/fixtures/run_fixtures.py:107` + `skills/ai-writing-suite/evals/fixtures/rubric.md:53`  
`build_judge_prompt()` never replaces the subtle-tell placeholder because the template contains `{subtle_tell or "obvious AI vocabulary and formatting"}`, but the code replaces only `{subtle_tell}`. The prompt currently leaks the literal placeholder, so the judge does not receive the fixture-specific tell.  
Concrete fix: change the rubric template slot to `{subtle_tell}` or replace the full current token in code. Strengthen `test_prompt_builds_for_every_fixture` at `test_fixtures.py:77` to assert no `{` / `}` placeholders remain, including subtle_tell.

[CONCERN] `skills/ai-writing-suite/evals/fixtures/judge.py:178` and `skills/ai-writing-suite/evals/fixtures/judge.py:195`  
`majority_vote()` treats a required dimension present in only one rep as present overall. Example: one rep has `no_fabrication: PASS`, two reps omit it, and `aggregate()` returns `PASS`. That violates the “missing-required-dim -> None, never fake PASS” invariant for multi-rep scoring.  
Concrete fix: in `aggregate()`, compute `required` before voting and return `None` if any required dimension is absent from any rep being counted, or explicitly discard incomplete reps and return `None` if none complete. Add a test for “required dim present in only some reps”.

One-line verdict: COMMIT-WITH-FIXES.

VERIFIED_AGAINST: feat/phase2a-judge-wirein @ 1278567e4be76056ffced4472ec115f0c5f091f8 @ 2026-06-08T02:47:48Z
hook: Stop
hook: Stop
hook: Stop Completed
hook: Stop Completed
tokens used
104,914
Findings:

[BLOCKER] `skills/ai-writing-suite/evals/fixtures/run_fixtures.py:107` + `skills/ai-writing-suite/evals/fixtures/rubric.md:53`  
`build_judge_prompt()` never replaces the subtle-tell placeholder because the template contains `{subtle_tell or "obvious AI vocabulary and formatting"}`, but the code replaces only `{subtle_tell}`. The prompt currently leaks the literal placeholder, so the judge does not receive the fixture-specific tell.  
Concrete fix: change the rubric template slot to `{subtle_tell}` or replace the full current token in code. Strengthen `test_prompt_builds_for_every_fixture` at `test_fixtures.py:77` to assert no `{` / `}` placeholders remain, including subtle_tell.

[CONCERN] `skills/ai-writing-suite/evals/fixtures/judge.py:178` and `skills/ai-writing-suite/evals/fixtures/judge.py:195`  
`majority_vote()` treats a required dimension present in only one rep as present overall. Example: one rep has `no_fabrication: PASS`, two reps omit it, and `aggregate()` returns `PASS`. That violates the “missing-required-dim -> None, never fake PASS” invariant for multi-rep scoring.  
Concrete fix: in `aggregate()`, compute `required` before voting and return `None` if any required dimension is absent from any rep being counted, or explicitly discard incomplete reps and return `None` if none complete. Add a test for “required dim present in only some reps”.

One-line verdict: COMMIT-WITH-FIXES.

VERIFIED_AGAINST: feat/phase2a-judge-wirein @ 1278567e4be76056ffced4472ec115f0c5f091f8 @ 2026-06-08T02:47:48Z
