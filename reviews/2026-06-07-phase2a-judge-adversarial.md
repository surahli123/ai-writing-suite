Reading prompt from stdin...
codex(47145) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
codex(47276) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
codex(47298) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
codex(47299) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
codex(47300) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
codex(47308) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
codex(47309) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
OpenAI Codex v0.137.0
--------
workdir: /Users/surahli/Documents/ai-writing-suite
model: gpt-5.5
provider: chatgpt_http
approval: never
sandbox: read-only
reasoning effort: high
reasoning summaries: none
session id: 019ea513-1a43-7580-8d95-279bd3abce8c
--------
user
You are an adversarial code reviewer. Default to skepticism — no rubber-stamping, no praise-then-bury. Find real defects. Be specific: cite file:line and give a concrete fix.

CONTEXT: This is "Phase 2a" of the AI Writing Suite — wiring an OPTIONAL, OPT-IN, ADVISORY LLM judge into an existing eval harness. The change is under `skills/ai-writing-suite/evals/`. Read the diff at /tmp/phase2a.diff, then read the actual files in the repo for full context (skills/ai-writing-suite/evals/fixtures/{judge.py,run_fixtures.py,fixtures.json,test_fixtures.py}, skills/ai-writing-suite/evals/test_voice_contract.py, evals/README.md, evals/run_all.sh, .github/workflows/ci.yml, skills/ai-writing-suite/_shared/host-profile-template.md, skills/ai-writing-suite/skills/comms-polish/SKILL.md).

The change MUST hold these invariants. Verify each and report any violation:
1. CI stays Python-3-stdlib-only AND key-free. The deterministic path (`run_all.sh` -> `python3 -m fixtures.run_fixtures` with NO --judge, no key) must make ZERO network calls and must NOT import judge.py. Confirm the judge import is lazy (inside run_judge), and that run_all.sh / ci.yml / .gitignore are unchanged. Is there ANY path where CI could touch the network or need a key?
2. Secret handling fails LOUD, never silent. A wrong/expired key (HTTP 401/403/5xx) or transport error must raise and cause a nonzero exit — NOT be laundered into a SKIP. The API key must never be logged/printed. A stray key in the env WITHOUT AIWS_JUDGE_RUN=1 must NOT trigger a billed call. Find any way a secret leaks or a silent fallback hides a real failure.
3. no_fabrication is the highest-stakes dimension and must be enforceable on EVERY fixture. Verify build_judge_prompt always asks the model to score no_fabrication even when rubric_focus omits it (3/8 fixtures omit it). Verify aggregate() RECOMPUTES the verdict in Python (no_fabrication FAIL -> overall FAIL) and IGNORES the model's self-reported "VERDICT:" line. Verify unparseable output or a missing required dimension returns None (SKIP), never a fabricated PASS.
4. Calibration is a knife-edge: the naive-baseline miss rate must stay 3/8 = 38% (run_fixtures.py asserts 30<=pct<=40). Confirm the fixtures.json change is FIELD-ONLY (added expected_verdict) with NO fixture added/removed/reordered, so calibration is untouched.
5. The judge is ADVISORY: its PASS/FAIL counts must NOT change the process exit code. The ONE judge condition that fails the run is "configured but scored 0/N" (liveness — likely a changed provider envelope). Verify main()'s exit logic matches this.
6. Correctness/robustness: the verdict parser regex, the response-envelope extractor (_extract_text), majority_vote (incl. ties), the score() 3-state gate. Find edge cases that break or silently misbehave.
7. Test quality: do the new tests actually PROVE the above, or do any pass vacuously? Is there a gap (an invariant with no test)? Is the voice-contract test's path resolution and header normalization correct?

OUTPUT FORMAT:
- A list of findings, each tagged [BLOCKER] / [CONCERN] / [SUGGESTION], with file:line, the problem, evidence, and a concrete fix.
- A one-line overall verdict: SAFE-TO-COMMIT / COMMIT-WITH-FIXES / NEEDS-REWORK.
- End with: VERIFIED_AGAINST: feat/phase2a-judge-wirein @ <HEAD-sha-you-see> @ <your-timestamp>

2026-06-08T02:32:47.582966Z ERROR rmcp::transport::worker: worker quit with fatal: Transport channel closed, when AuthRequired(AuthRequiredError { www_authenticate_header: "Bearer realm=\"OAuth\", resource_metadata=\"https://mcp.cloudflare.com/.well-known/oauth-protected-resource/mcp\", error=\"invalid_token\"" })
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
Using `code-review` because this is explicitly a review gate. I’ll verify the Phase 2a diff against the stated invariants, then cross-check the real files and report only concrete defects or gaps.
hook: PreToolUse
hook: PreToolUse
hook: PreToolUse
hook: PreToolUse Completed
hook: PreToolUse Completed
hook: PreToolUse Completed
codex(49980) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
codex(49984) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
codex(49985) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
exec
/bin/zsh -lc "git rev-parse --abbrev-ref HEAD && git rev-parse HEAD && date '+%Y-%m-%dT%H:%M:%S%z'" in /Users/surahli/Documents/ai-writing-suite
exec
/bin/zsh -lc 'rg -n "ai-writing-suite|Phase 2a|judge|evals" /Users/surahli/.codex/memories/MEMORY.md' in /Users/surahli/Documents/ai-writing-suite
exec
/bin/zsh -lc "sed -n '1,220p' /Users/surahli/.codex/skills/code-review/SKILL.md" in /Users/surahli/Documents/ai-writing-suite
 succeeded in 132ms:
---
name: code-review
description: "[OMX] Run a comprehensive severity-rated code review for correctness, tests, security, performance, maintainability, and project standards. Use when the user asks for code review, PR review, review this diff, or an adversarial implementation check."
---

# Code Review Skill

Conduct a thorough code review for quality, security, and maintainability with severity-rated feedback.

## When to Use

This skill activates when:
- User requests "review this code", "code review"
- Before merging a pull request
- After implementing a major feature
- User wants quality assessment

## GPT-5.5 Guidance Alignment

- Default to outcome-first progress and completion reporting: state the target result, evidence, validation status, and stop condition before adding process detail.
- Treat newer user task updates as local overrides for the active workflow branch while preserving earlier non-conflicting constraints.
- If correctness depends on additional inspection, retrieval, execution, or verification, keep using the relevant tools until the review is grounded; stop once enough evidence exists.
- Continue through clear, low-risk, reversible next steps automatically; ask only when the next step is materially branching, destructive, credentialed, external-production, or preference-dependent.

Delegates to the `code-reviewer` and `architect` agents in parallel for a two-lane review:

1. **Identify Changes**
   - Run `git diff` to find changed files
   - Determine scope of review (specific files or entire PR)

2. **Launch Parallel Review Lanes**
   - **`code-reviewer` lane** - owns spec compliance, security, code quality, performance, and maintainability findings
   - **`architect` lane** - owns the devil's-advocate / design-tradeoff perspective
   - Both lanes run in parallel and produce distinct outputs before final synthesis
   - If either lane cannot be launched or does not return evidence, report `independent review unavailable`; do **not** substitute the current/authoring lane, and do **not** approve or mark the review merge-ready.

3. **Review Categories**
   - **Security** - Hardcoded secrets, injection risks, XSS, CSRF
   - **Code Quality** - Function size, complexity, nesting depth
   - **Performance** - Algorithm efficiency, N+1 queries, caching
   - **Best Practices** - Naming, documentation, error handling
   - **Maintainability** - Duplication, coupling, testability

4. **Severity Rating**
   - **CRITICAL** - Security vulnerability (must fix before merge)
   - **HIGH** - Bug or major code smell (should fix before merge)
   - **MEDIUM** - Minor issue (fix when possible)
   - **LOW** - Style/suggestion (consider fixing)

5. **Architectural Status Contract**
   - **CLEAR** - No unresolved architectural blocker was found
   - **WATCH** - Non-blocking design/tradeoff concern that must appear in the final synthesis
   - **BLOCK** - Unresolved design concern that prevents a merge-ready verdict

6. **Specific Recommendations**
   - File:line locations for each issue
   - Concrete fix suggestions
   - Code examples where applicable

7. **Final Synthesis**
   - Combine the `code-reviewer` recommendation and the architect status into one final verdict
   - Approval requires explicit evidence from both independent lanes; missing or failed delegation is a blocking unavailable-review state, not an approval fallback
   - Deterministic merge gating rules:
     - If architect status is **BLOCK**, final recommendation is **REQUEST CHANGES**
     - Else if `code-reviewer` recommendation is **REQUEST CHANGES**, final recommendation is **REQUEST CHANGES**
     - Else if architect status is **WATCH**, final recommendation is **COMMENT**
     - Else final recommendation follows the `code-reviewer` lane
   - The final report must make architect blockers impossible to miss

## Agent Delegation

Do not self-review as a fallback. If the `code-reviewer` or `architect` agent path is missing, unavailable, skipped, or fails, emit a clear unavailable-review result and block approval until the independent lane evidence exists.

```
delegate(
  role="code-reviewer",
  tier="THOROUGH",
  prompt="CODE REVIEW TASK

Review code changes for quality, security, and maintainability.

This is the code/spec/security lane. Do not absorb architectural ownership.

Scope: [git diff or specific files]

Review Checklist:
- Security vulnerabilities (OWASP Top 10)
- Code quality (complexity, duplication)
- Performance issues (N+1, inefficient algorithms)
- Best practices (naming, documentation, error handling)
- Maintainability (coupling, testability)

Output: Code review report with:
- Files reviewed count
- Issues by severity (CRITICAL, HIGH, MEDIUM, LOW)
- Specific file:line locations
- Fix recommendations
- Approval recommendation (APPROVE / REQUEST CHANGES / COMMENT)"
)

delegate(
  role="architect",
  tier="THOROUGH",
  prompt="ARCHITECTURE / DEVIL'S-ADVOCATE REVIEW TASK

Review the same code changes from the architecture/tradeoff perspective.

Scope: [git diff or specific files]

Focus:
- System boundaries and interfaces
- Hidden coupling or long-term maintainability risks
- Tradeoff tension the main reviewer might miss
- Strongest counterargument against approving as-is

Output:
- Architectural Status: CLEAR / WATCH / BLOCK
- File:line evidence for each concern
- Concrete tradeoff or design recommendation"
)

Run both lanes in parallel, then synthesize them with the deterministic rules above.
```

## External Model Consultation (Preferred)

The code-reviewer agent SHOULD consult Codex for cross-validation.

### Protocol
1. **Form your OWN review FIRST** - Complete the review independently
2. **Consult for validation** - Cross-check findings with Codex
3. **Critically evaluate** - Never blindly adopt external findings
4. **Graceful optional consultation fallback** - Never block because optional external consultation tools are unavailable; this does not waive the required independent `code-reviewer` and `architect` lanes

### When to Consult
- Security-sensitive code changes
- Complex architectural patterns
- Unfamiliar codebases or languages
- High-stakes production code

### When to Skip
- Simple refactoring
- Well-understood patterns
- Time-critical reviews
- Small, isolated changes

### Tool Usage
Prefer native `code-reviewer` agent consultation or CLI-backed `ask_codex` surfaces when available. Optional MCP compatibility ask tools may be used only when already enabled. If optional external consultation tools are unavailable, continue with the required independent `code-reviewer` and `architect` lanes; do not replace those lanes with self-review.

**Note:** Codex calls can take up to 1 hour. Consider the review timeline before consulting.

## Output Format

```
CODE REVIEW REPORT
==================

Files Reviewed: 8
Total Issues: 12
Architectural Status: WATCH

CRITICAL (0)
-----------
(none)

HIGH (0)
--------
(none)

MEDIUM (7)
----------
1. src/api/auth.ts:42
   Issue: Email normalization logic is duplicated instead of reusing the shared helper
   Risk: Validation rules can drift between authentication paths
   Fix: Route both paths through the shared normalization helper

2. src/components/UserProfile.tsx:89
   Issue: Derived permissions are recalculated on every render
   Risk: Avoidable work during profile refreshes
   Fix: Memoize the derived permissions list or compute it upstream

3. src/utils/validation.ts:15
   Issue: Form-layer and server-layer validation messages are defined separately
   Risk: User-facing validation guidance can become inconsistent
   Fix: Share one validation message helper across both call sites

LOW (5)
-------
...

ARCHITECTURE WATCHLIST
----------------------
- src/review/orchestrator.ts:88
  Concern: Review result synthesis relies on implicit ordering rather than an explicit blocker contract
  Status: WATCH
  Recommendation: Define deterministic merge gating before expanding reviewers

SYNTHESIS
---------
- code-reviewer recommendation: COMMENT
- architect status: WATCH
- final recommendation: COMMENT

RECOMMENDATION: COMMENT

Address any WATCH concerns before treating the change as merge-ready.
```

## Review Checklist

The `code-reviewer` lane checks:

### Security
- [ ] No hardcoded secrets (API keys, passwords, tokens)
- [ ] All user inputs sanitized
- [ ] SQL/NoSQL injection prevention
- [ ] XSS prevention (escaped outputs)
- [ ] CSRF protection on state-changing operations
- [ ] Authentication/authorization properly enforced


hook: PostToolUse
hook: PostToolUse
 succeeded in 587ms:
63:- extensions/chronicle/resources/2026-06-06T02-23-00-YfEG-10min-memory-summary.md (cwd=/Users/surahli/Documents/projects/SMA_v2, rollout_path=/Users/surahli/.codex/memories/extensions/chronicle/resources/2026-06-06T02-23-00-YfEG-10min-memory-summary.md, updated_at=2026-06-06T02:23:00+00:00, thread_id=None, Chronicle window showing fresh Claude Code orientation, branch `codex/sma-rewrite-evidence-bridge-shadow-run`, dirty `.agents/skills/sma_rewrite/evals/`, and planning prompts grounded in data-agent / skill-system references)
67:- SMA_v2, codex/sma-rewrite-evidence-bridge-shadow-run, .agents/skills/sma_rewrite/evals/, codegraph, data agent, skill system best practices, claude --dangerously-skip-permissions, ultracode
78:- notes/sma-rewrite-improvement-discussion-2026-06-05.md, .agents/skills/sma_rewrite/run_plan/plan.py, SCHEMA_VERSION = "sma.run_plan.v0", build_p1_run_plan, .agents/skills/sma_rewrite/evals, runner/adapters/sma_rewrite.py, plan-only, AI slop, Gotchas
102:- The fresh SMA rewrite orientation found the repo on branch `codex/sma-rewrite-evidence-bridge-shadow-run`, with dirty files already present under `.agents/skills/sma_rewrite/evals/`; future continuation should classify existing dirt before adding new changes [Task 1]
103:- The critical contract finding was that `run_plan/plan.py` is adapter-facing, not just test-facing: eval adapter code under `.agents/skills/sma_rewrite/evals/.../runner/adapters/sma_rewrite.py` loads it and expects `SCHEMA_VERSION = "sma.run_plan.v0"` plus `build_p1_run_plan()` [Task 2]
148:- The bounded C4 lane already had strong verification evidence: the fixture/schema/judge trio under `.agents/skills/sma_rewrite/evals/tests/` passed as `45 passed`, and `git diff --check` on the lane was clean; the remaining work was contract-wording reconciliation around `permission_denial_expected` and `expected_denied_evidence_ids` [Task 1]
333:# Task Group: ai-writing-suite / local repo migration, layered implementation, and publish-surface review
334:scope: June 6-7 AI Writing Suite work covering the move out of the umbrella repo into a standalone local repo, Layer 0-3 implementation, isolated review, and the later Codex/Claude packaging-surface checks; use when the user resumes `ai-writing-suite` or asks how the standalone repo was supposed to proceed.
335:applies_to: cwd=/Users/surahli/Documents/ai-writing-suite with antecedent design/handoff context in /Users/surahli/Documents/Codex/2026-06-01/personal-productivity-skills; reuse_rule=safe for the standalone `ai-writing-suite` repo while the same local migration and layered implementation plan are still current, but re-check whether GitHub/PR changes have since been reconciled.
341:- extensions/chronicle/resources/2026-06-06T16-13-00-pqvH-10min-memory-summary.md (cwd=/Users/surahli/Documents/Codex/2026-06-01/personal-productivity-skills and /Users/surahli/Documents/ai-writing-suite, rollout_path=/Users/surahli/.codex/memories/extensions/chronicle/resources/2026-06-06T16-13-00-pqvH-10min-memory-summary.md, updated_at=2026-06-06T16:13:00+00:00, thread_id=None, Chronicle window showing the AI Writing Suite wrapup, PR #4 state, migration discussion, and the local-only history-preserving repo move decision)
345:- ai-writing-suite, personal-productivity-skills, independent local repo, local-only migration, preserve history, PR #4, rename-ai-writing-suite, docs/design-ai-writing-suite-v1-2026-06-06.md, docs/handover-2026-06-06-ai-writing-suite-v1.md, memory/project_ai_writing_suite.md
351:- extensions/chronicle/resources/2026-06-06T19-58-00-oHuw-10min-memory-summary.md (cwd=/Users/surahli/Documents/ai-writing-suite, rollout_path=/Users/surahli/.codex/memories/extensions/chronicle/resources/2026-06-06T19-58-00-oHuw-10min-memory-summary.md, updated_at=2026-06-06T19:58:00+00:00, thread_id=None, Chronicle window showing standalone-repo commit history, Layer 1 verification, and Layer 2 parallel executor work)
355:- /Users/surahli/Documents/ai-writing-suite, d4ed984, e1368db, 7bdf986, Layer 0, Layer 1, Layer 2, comms-polish, voice-onboard, _shared/voice-profile.md, _shared/knowledge/structure.md, _shared/self-improvement.md
361:- extensions/chronicle/resources/2026-06-06T20-02-00-CcyZ-10min-memory-summary.md (cwd=/Users/surahli/Documents/ai-writing-suite, rollout_path=/Users/surahli/.codex/memories/extensions/chronicle/resources/2026-06-06T20-02-00-CcyZ-10min-memory-summary.md, updated_at=2026-06-06T20:02:00+00:00, thread_id=None, Chronicle window showing Layer 1 commit `7bdf906`, KB-agent inspection, and the Layer 2 follow-up context)
362:- extensions/chronicle/resources/2026-06-06T21-01-00-tkIN-10min-memory-summary.md (cwd=/Users/surahli/Documents/ai-writing-suite, rollout_path=/Users/surahli/.codex/memories/extensions/chronicle/resources/2026-06-06T21-01-00-tkIN-10min-memory-summary.md, updated_at=2026-06-06T21:01:00+00:00, thread_id=None, Chronicle window showing the user choosing `Python detector now` and the Layer 3 split into eval/docs/packaging)
372:- extensions/chronicle/resources/2026-06-07T00-09-00-PFCN-10min-memory-summary.md (cwd=/Users/surahli/Documents/ai-writing-suite, rollout_path=/Users/surahli/.codex/memories/extensions/chronicle/resources/2026-06-07T00-09-00-PFCN-10min-memory-summary.md, updated_at=2026-06-07T00:09:00+00:00, thread_id=None, Chronicle window showing the v1 layer table, isolated code-review pass, and follow-up findings around docs/smoke/detector details)
373:- extensions/chronicle/resources/2026-06-07T00-26-00-xsag-10min-memory-summary.md (cwd=/Users/surahli/Documents/ai-writing-suite, rollout_path=/Users/surahli/.codex/memories/extensions/chronicle/resources/2026-06-07T00-26-00-xsag-10min-memory-summary.md, updated_at=2026-06-07T00:26:00+00:00, thread_id=None, Chronicle window showing `main` fast-forward to `c3f1713` and the pre-publish check that treated `packaging/codex/.codex-plugin/plugin.json` as speculative)
377:- feat/ai-writing-suite-v1, code-reviewer pass, 17/17 detector, 6/6 fixtures, AI-slop 62/100 -> 0/100, c3f1713, packaging/codex/.codex-plugin/plugin.json, SKILL.md, references/, manifest verification
383:- extensions/chronicle/resources/2026-06-07T16-54-00-FOWx-10min-memory-summary.md (cwd=/Users/surahli/Documents/ai-writing-suite, rollout_path=/Users/surahli/.codex/memories/extensions/chronicle/resources/2026-06-07T16-54-00-FOWx-10min-memory-summary.md, updated_at=2026-06-07T16:54:00+00:00, thread_id=None, Chronicle window showing the packaging/installability blocker, `docs/plan-publish-cleanup-test-2026-06-07.md`, and the later host-scope choices)
399:- The AI Writing Suite work started inside `/Users/surahli/Documents/Codex/2026-06-01/personal-productivity-skills` with PR `#4`, `docs/design-ai-writing-suite-v1-2026-06-06.md`, `docs/handover-2026-06-06-ai-writing-suite-v1.md`, `memory/project_ai_writing_suite.md`, and a repo `CLAUDE.md`; the later migration discussion treated that as antecedent context, not the final repo home [Task 1]
401:- By the later Chronicle window, the standalone repo existed at `/Users/surahli/Documents/ai-writing-suite` with visible commit sequence `d4ed984 Extract ai-writing-suite into standalone local repo`, `e1368db Layer 0: suite skeleton, thin router, consolidated pattern catalog`, and `7bdf986 Layer 1: enrich comms-polish + build voice-onboard` [Task 2]
402:- Layer 1 verification depended on one shared contract surface: `skills/ai-writing-suite/_shared/voice-profile.md` is written by `voice-onboard` and read by `comms-polish`, with graceful degradation when the profile is absent [Task 2]
403:- The next visible Layer 2 split was intentionally parallel and disjoint: one executor wrote `skills/ai-writing-suite/_shared/knowledge/structure.md` for a generic KB seed plus retrieval smoke path, and the other wrote `skills/ai-writing-suite/_shared/self-improvement.md` for a human-gated self-improvement hook [Task 2]
404:- The visible Layer 3 decision was explicit and bounded: keep the mechanical detector in Python for now, then split the final layer into `evals/`, docs/attribution surfaces, and Codex/Claude packaging lanes with separate ownership [Task 3]
437:- rollout_summaries/2026-06-07T00-28-17-urrl-darwin_skillopt_autorefine_direct_evaluation.md (cwd=/Users/surahli/Documents/projects/skill-improvement, rollout_path=/Users/surahli/.codex/sessions/2026/06/06/rollout-2026-06-06T17-28-17-019e9f7a-fb83-71a3-ab98-3c320cc345fb.jsonl, updated_at=2026-06-07T01:39:56+00:00, thread_id=019e9f7a-fb83-71a3-ab98-3c320cc345fb, isolated AutoRefine copy, custom SkillOpt adapter, tiny Darwin/SkillOpt run, and judge/adversarial review)
629:- symptom: the prototype scorecard mirrors the fixture author's assumptions instead of measuring routing quality -> cause: the same perspective authors the fixture, labels the acceptable set, and judges the outcome -> fix: insert blind/independent labeling and a calibration gate before implementation/optimization work [Task 4]
784:- The review document `outputs/codex-onboarding/07-ds-audience-review-x-style-gap.md` stayed central to packaging decisions: the package was judged too wiki-like, and the stronger teaching direction was `one pain, one diagnosis, one workflow, one artifact` plus the hero line `Start with a workflow. End with a receipt.` [Task 1]
1056:- The package location decision is closed as `plugins/sma-metric-diagnosis/`; install/export mechanics remain open, and protected paths `.agents/skills/sma/`, `.agents/skills/sma_rewrite/evals/`, and `plugins/` stayed untouched during Slice 0 [Task 2]
1087:- permission_denial_expected, judge/protocol.py, judge/rubric.md, diagnostic_cases.schema.json, run_plan/corpus_eval.py protected, runs/slice4-scorecard.html protected, codex-c4-scope-reconciliation-2026-06-01.md, 100 passed, 140 passed
1092:- when the user said `EDIT only: .agents/skills/sma_rewrite/evals/synthetic_enterprise_search/**` -> preserve strict write-scope boundaries and keep adjacent `run_loop/`, `run_plan/`, and old-SMA surfaces read-only unless explicitly reopened [Task 1]
1099:- The v1 judge scaffold is permission-only by design and intentionally omits confidence scoring because the contract lacks ground-truth confidence labels [Task 1]
1101:- For the later C4 lane, `git status --short --branch`, recent `git log`, `docs/sma-rewrite-c-to-b/handoff.md`, and `notes/slice-4-scoping-and-c4-overlap.md` were enough to separate Claude's slice-4 runner/observability lane from Codex's judge lane before editing [Task 2]
1103:- The permission judge must distinguish three cases: expected-denial cases where denied rows disappearing is a failure, non-permission cases with unrelated ACL denies that should not fail, and real leaked denied evidence that must fail [Task 2]
1108:- symptom: a permission case incorrectly passes or becomes `not_applicable` after deny rows disappear -> cause: the judge only checked the explicit flag or only looked for any denied evidence at all -> fix: fail closed from permission-case indicators and separately verify the expected denied result/citation ids [Task 2]
1431:- rollout_summaries/2026-05-30T15-01-38-313y-ai_trade_agent_morning_digest_health_check.md (cwd=/Users/surahli/Documents/projects/ai-trade-agent, rollout_path=/Users/surahli/.codex/sessions/2026/05/30/rollout-2026-05-30T08-01-38-019e7967-ad67-7433-af6c-06b3ec14a988.jsonl, updated_at=2026-05-30T15:18:37+00:00, thread_id=019e7967-ad67-7433-af6c-06b3ec14a988, strict read-only health check with exact evidence and trust judgement)
1450:- when the user asks whether the digest works or whether it is safe to trust -> report `pass/fail`, exact evidence, blockers, and the trust judgement, not a loose summary [Task 1]
1765:- mini-schema-implementation-plan.md, ralplan-consensus-handoff.md, 240 docs, 10 cases, 4 source systems, no optional connectors, no_score, permission leakage, judge_calibration_failed, contamination fingerprints, no code yet
2315:- when the user said "Do not reopen strategy. Keep reasoning path unchanged" -> treat lumina runtime fixes as strictly narrow, reasoning-neutral patches and avoid planner/judge/harness/model-routing drift [Task 1]

hook: PostToolUse
 succeeded in 914ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
feat/phase2a-judge-wirein
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
1278567e4be76056ffced4472ec115f0c5f091f8
2026-06-07T19:33:40-0700

hook: PostToolUse Completed
hook: PostToolUse Completed
hook: PostToolUse Completed
codex
I have the branch and HEAD. I’m splitting the review into two independent lanes now: one for invariant/security/test defects, one for design/robustness counterexamples, then I’ll synthesize only findings with file evidence.
hook: PreToolUse
hook: PreToolUse Completed
collab: SpawnAgent
codex(52103) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
codex(52106) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
codex(52120) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
codex(52121) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
codex(52132) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
hook: PostToolUse
2026-06-08T02:34:23.900886Z ERROR rmcp::transport::worker: worker quit with fatal: Transport channel closed, when AuthRequired(AuthRequiredError { www_authenticate_header: "Bearer realm=\"OAuth\", resource_metadata=\"https://mcp.cloudflare.com/.well-known/oauth-protected-resource/mcp\", error=\"invalid_token\"" })
hook: PostToolUse Completed
hook: PreToolUse
codex(55106) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
codex(55107) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
codex(55105) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
hook: PreToolUse Completed
collab: SpawnAgent
codex(55421) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
codex(55422) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
codex(55423) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
codex(55449) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
codex(55450) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
hook: PostToolUse
hook: PostToolUse Completed
2026-06-08T02:35:18.550621Z ERROR rmcp::transport::worker: worker quit with fatal: Transport channel closed, when AuthRequired(AuthRequiredError { www_authenticate_header: "Bearer realm=\"OAuth\", resource_metadata=\"https://mcp.cloudflare.com/.well-known/oauth-protected-resource/mcp\", error=\"invalid_token\"" })
codex
Target result: a merge gate verdict, not a general summary. I’m checking the exact deterministic path and optional judge path separately so advisory behavior cannot hide CI or secret-handling defects.
hook: PreToolUse
hook: PreToolUse
hook: PreToolUse
hook: PreToolUse Completed
hook: PreToolUse Completed
hook: PreToolUse Completed
codex(57621) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
codex(57620) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
codex(57632) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
codex(57633) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
codex(57634) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
codex(57635) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
codex(57636) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
exec
/bin/zsh -lc "nl -ba skills/ai-writing-suite/evals/fixtures/judge.py | sed -n '1,260p'" in /Users/surahli/Documents/ai-writing-suite
exec
/bin/zsh -lc "nl -ba skills/ai-writing-suite/evals/fixtures/run_fixtures.py | sed -n '1,320p'" in /Users/surahli/Documents/ai-writing-suite
exec
/bin/zsh -lc "sed -n '1,260p' /tmp/phase2a.diff" in /Users/surahli/Documents/ai-writing-suite
 succeeded in 258ms:
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

 succeeded in 228ms:
diff --git a/skills/ai-writing-suite/evals/README.md b/skills/ai-writing-suite/evals/README.md
index b93acf9..a0475cf 100644
--- a/skills/ai-writing-suite/evals/README.md
+++ b/skills/ai-writing-suite/evals/README.md
@@ -7,7 +7,7 @@ parts):
 | Piece | What it does | Needs a model? |
 | --- | --- | --- |
 | `detector/` | Mechanical AI-tell scanner — cheap deterministic regression gate | No |
-| `fixtures/` | Before/after pairs across 4 genres, score bands + LLM-judge rubric | Judge half only |
+| `fixtures/` | Before/after pairs across 4 genres, score bands + LLM-judge rubric | Judge half only (opt-in) |
 | `smoke_test.py` | Automates the KB ingestion+retrieval smoke chain (design D12) | No |
 
 > Design lineage: D10 (eval harness + Autorefine-style self-improvement) and D12
@@ -28,7 +28,7 @@ cat draft.md | python3 -m detector.cli -
 
 # 2. Fixtures — deterministic score-band check + calibration report
 python3 -m fixtures.run_fixtures
-python3 -m fixtures.run_fixtures --judge      # also emits the LLM-judge prompts (SKIPPED offline)
+python3 -m fixtures.run_fixtures --judge      # LLM-judge half: SKIPPED unless AIWS_JUDGE_* is set (see "The LLM judge" below)
 python3 -m unittest fixtures.test_fixtures    # asserts the suite stays calibrated
 
 # 3. KB smoke test — ingestion+retrieval chain
@@ -70,14 +70,49 @@ memo). Each has an AI-shaped `before`, a good human `after`, detector score
 bands, and `rubric_focus` (which rubric dimensions matter here).
 
 - `run_fixtures.py` — runs the **deterministic** half (assert score bands +
-  report naive-baseline miss rate). With `--judge` it fills the rubric prompt
-  per fixture and marks them **SKIPPED** (no model wired in — it never fabricates
-  a verdict offline).
+  report naive-baseline miss rate). With `--judge` it runs the LLM-judge half:
+  **SKIPPED** unless a judge is configured (see "The LLM judge" below); when
+  configured it scores each fixture, re-computes the verdict in Python, and
+  reports judge-vs-gold agreement. It never fabricates a verdict offline.
+- `judge.py` — the opt-in, stdlib-only judge client (env-driven provider; parses
+  per-dimension PASS/FAIL; re-computes the verdict, enforcing
+  `no_fabrication`-overrides-FAIL in code). Dev-only; never reached by CI.
 - `rubric.md` — the LLM-judge scoring contract (dimensions, verdict aggregation,
   a model-agnostic zero-shot prompt template). `no_fabrication` is always
   required: a fluent rewrite that invents a number FAILS.
 - `test_fixtures.py` — asserts the suite stays well-formed, in-band, and
-  calibrated.
+  calibrated, and that the judge parse/aggregate logic + the CI-stays-key-free
+  invariant hold (canned responses, no network).
+
+**The LLM judge (opt-in, advisory).** The judge is OFF by default — CI never runs
+it and needs no key. To run it locally, set all four env vars (the run flag is a
+deliberate spend guard, so a stray key alone cannot trigger a billed call):
+
+```bash
+export AIWS_JUDGE_URL=...      # an OpenAI-compatible chat/completions endpoint
+export AIWS_JUDGE_MODEL=...    # the judge model id
+export AIWS_JUDGE_KEY=...      # API key (sent as a Bearer header, never logged)
+export AIWS_JUDGE_RUN=1        # opt in to actually spend
+python3 -m fixtures.run_fixtures --judge
+```
+
+- **Advisory in v1.** The judge's PASS/FAIL counts do NOT change the exit code;
+  only the deterministic checks gate CI (which keeps CI key-free). The one judge
+  condition that fails the run is a configured-but-broken judge (scored 0/N —
+  likely a changed provider response envelope), surfaced loudly; an auth/transport
+  error also fails loudly and is never laundered into a SKIP.
+- **Cross-family recommended.** Point `AIWS_JUDGE_MODEL` at a different model
+  family than the one that wrote the text, to avoid judge self-preference
+  (~10-25% PASS inflation). For the current static `after` fixtures (hand-written,
+  not model output) this is a recommendation, not a hard requirement.
+- **What a green judge means.** It proves the judge *wiring* works (parse +
+  re-aggregate + `no_fabrication` enforcement), measured against the
+  `expected_verdict` gold labels as a directional agreement count. It does NOT yet
+  prove `comms-polish` writes well end to end (it scores curated rewrites, not live
+  skill output), and the agreement count is NOT a Cohen's kappa — at n=8 a kappa
+  would be statistical noise. Real two-class gold, kappa, a frozen holdout,
+  replication, and a live end-to-end eval are **Phase 2b** (see
+  `docs/test-plan-v1-2026-06-07.md`).
 
 ### 3. `smoke_test.py` — KB retrieval chain
 
@@ -115,8 +150,11 @@ what the LLM judge exists to cover — and why the suite needs both halves.
 
 1. Add an object to `fixtures.json > fixtures` with: `id`, `genre`,
    `difficulty` (`obvious`|`subtle`), `before`, `after`, `after_band_max`,
-   `rubric_focus`, `expect_baseline` (`catch`|`miss`), and — for subtle ones —
-   a `subtle_tell` explaining the non-vocabulary tell.
+   `rubric_focus`, `expect_baseline` (`catch`|`miss`), `expected_verdict`
+   (`PASS`|`FAIL`, the gold label for judge-vs-gold agreement), and — for subtle
+   ones — a `subtle_tell` explaining the non-vocabulary tell. Note: adding a
+   fixture changes the calibration denominator (step 4) — at small n the 30-40%
+   band is a knife-edge, so design each addition to keep the miss count in band.
 2. Run `python3 -m fixtures.run_fixtures` to read the actual detector scores.
 3. Set `before_band_min`/`before_band_max` to bracket the observed score (a
    regression guard, not an aspiration). Set `expect_baseline` to match what the
diff --git a/skills/ai-writing-suite/evals/fixtures/fixtures.json b/skills/ai-writing-suite/evals/fixtures/fixtures.json
index 26003e3..b8f7387 100644
--- a/skills/ai-writing-suite/evals/fixtures/fixtures.json
+++ b/skills/ai-writing-suite/evals/fixtures/fixtures.json
@@ -1,9 +1,10 @@
 {
-  "_doc": "Before/after LLM-judge fixtures across 4 genres (tweet/linkedin/readme/memo). Each fixture: an AI-shaped `before`, a good human `after`, and what we expect. `before_band_min`/`before_band_max`/`after_band_max` are detector score-band expectations (mechanical, deterministic regression guards bracketing the observed score). `rubric_focus` lists which rubric dimensions the LLM judge should weigh. Difficulty is calibrated so a NAIVE baseline (flag-if-detector-score >= baseline_threshold) misses ~30-40% of the `before` items: the `subtle` ones are AI-written but score LOW because they avoid vocabulary tells and lean on structural/rhythm tells a flat threshold underweights. See README calibration section.",
+  "_doc": "Before/after LLM-judge fixtures across 4 genres (tweet/linkedin/readme/memo). Each fixture: an AI-shaped `before`, a good human `after`, and what we expect. `before_band_min`/`before_band_max`/`after_band_max` are detector score-band expectations (mechanical, deterministic regression guards bracketing the observed score). `rubric_focus` lists which rubric dimensions the LLM judge should weigh. Difficulty is calibrated so a NAIVE baseline (flag-if-detector-score >= baseline_threshold) misses ~30-40% of the `before` items: the `subtle` ones are AI-written but score LOW because they avoid vocabulary tells and lean on structural/rhythm tells a flat threshold underweights. See README calibration section. `expected_verdict` (PASS|FAIL) is the owner's gold label for advisory judge-vs-gold agreement: all current fixtures are good rewrites (PASS); FAIL exemplars live in the unit tests (test_fixtures.py), not here, to preserve the 30-40% calibration band.",
   "baseline_threshold": 14,
   "fixtures": [
     {
       "id": "tweet-01-obvious",
+      "expected_verdict": "PASS",
       "genre": "tweet",
       "difficulty": "obvious",
       "before": "In today's ever-evolving landscape, we're thrilled to delve into a game-changing paradigm. This seamless, robust solution will revolutionize how you work. The future looks bright! 🚀 #innovation #growth #tech #startup #ai #future #buildinpublic",
@@ -20,6 +21,7 @@
     },
     {
       "id": "tweet-02-subtle",
+      "expected_verdict": "PASS",
       "genre": "tweet",
       "difficulty": "subtle",
       "before": "Spent the week thinking about retrieval. Keyword search is underrated. Vector search is overhyped. Most teams reach for embeddings when an index would do. Worth sitting with that.",
@@ -36,6 +38,7 @@
     },
     {
       "id": "linkedin-01-obvious",
+      "expected_verdict": "PASS",
       "genre": "linkedin",
       "difficulty": "obvious",
       "before": "I recently had the pleasure of attending a pivotal conference. It was truly a transformative experience that underscored the importance of fostering meaningful connections. Moreover, the keynote was a testament to the power of innovation. As we navigate this dynamic ecosystem, let's embrace the journey. What's next? Only time will tell.",
@@ -52,6 +55,7 @@
     },
     {
       "id": "linkedin-02-subtle",
+      "expected_verdict": "PASS",
       "genre": "linkedin",
       "difficulty": "subtle",
       "before": "Three things I learned shipping our first ML model.\n\nFirst, data quality matters more than model choice.\n\nSecond, stakeholders care about latency, not accuracy.\n\nThird, the simplest baseline is often hard to beat.\n\nWhat would you add?",
@@ -69,6 +73,7 @@
     },
     {
       "id": "readme-01-obvious",
+      "expected_verdict": "PASS",
       "genre": "readme",
       "difficulty": "obvious",
       "before": "## Overview\n\nThis comprehensive, cutting-edge library leverages a robust architecture to seamlessly streamline your workflow. It empowers developers to harness the full potential of modern tooling. Whether you're a beginner or an expert, this powerful solution has you covered.",
@@ -84,6 +89,7 @@
     },
     {
       "id": "readme-02-subtle",
+      "expected_verdict": "PASS",
       "genre": "readme",
       "difficulty": "subtle",
       "before": "## Installation\n\nTo get started, simply install the package. Once installed, you can begin using it right away. The setup process is designed to be straightforward and intuitive, ensuring a smooth onboarding experience for users of all skill levels.",
@@ -100,6 +106,7 @@
     },
     {
       "id": "memo-01-obvious",
+      "expected_verdict": "PASS",
       "genre": "memo",
       "difficulty": "obvious",
       "before": "It is important to note that, as we move forward, we must delve into the intricacies of our strategy. Experts believe that fostering a culture of innovation is paramount. Furthermore, this pivotal initiative will undoubtedly elevate our position. Let's break this down step by step to ensure a holistic approach.",
@@ -116,6 +123,7 @@
     },
     {
       "id": "memo-02-subtle",
+      "expected_verdict": "PASS",
       "genre": "memo",
       "difficulty": "subtle",
       "before": "While our current approach has served us well, there is room for improvement. It is important to note that research suggests engagement is trending in a positive direction. That said, we should remain mindful of potential headwinds, and a measured strategy could potentially position us well. Ultimately, this balanced approach will help us capture emerging opportunities going forward.",
diff --git a/skills/ai-writing-suite/evals/fixtures/judge.py b/skills/ai-writing-suite/evals/fixtures/judge.py
new file mode 100644
index 0000000..2827bf7
--- /dev/null
+++ b/skills/ai-writing-suite/evals/fixtures/judge.py
@@ -0,0 +1,199 @@
+"""Optional LLM-judge for the before/after fixtures (Phase 2a wire-in).
+
+DEV-ONLY + OPT-IN. This module is the ONLY place the eval can talk to a model.
+It is never imported at module load and never reached by the deterministic CI
+path: `run_all.sh` runs `python3 -m fixtures.run_fixtures` (no `--judge`) with no
+key, so CI stays Python-3-stdlib-only and green. This module uses only the stdlib
+(`urllib` + `json` + `os`) — wiring a judge adds NO pip line to CI.
+
+Honesty stance (inherited from run_fixtures.run_judge): we NEVER fabricate a
+verdict. If the judge is not configured, the caller SKIPs.
+
+Three-state gate (`score()`):
+  1. NOT configured (any of URL/MODEL/KEY missing, or AIWS_JUDGE_RUN != "1")
+     -> return None  ->  caller SKIPs (process exits 0; the offline honesty path).
+  2. configured + opted in
+     -> ONE HTTP POST; return the model's raw text.
+  3. configured but the call fails (transport / auth / HTTP 4xx-5xx)
+     -> raise JudgeError (LOUD; the caller exits nonzero). An auth failure must
+        NOT be laundered into a SKIP (CLAUDE.md: "FAIL LOUDLY if config and
+        runtime disagree").
+
+Provider is PURELY env-driven — NO baked-in vendor — to keep the
+host-provides-the-model philosophy and avoid a second-vendor dependency:
+
+  AIWS_JUDGE_URL    full chat/completions endpoint URL (e.g. an OpenAI-compatible
+                    .../v1/chat/completions)
+  AIWS_JUDGE_MODEL  model id to send
+  AIWS_JUDGE_KEY    the API key (read once, sent as a Bearer header, never logged)
+  AIWS_JUDGE_RUN    must be "1" to actually spend — a stray key in the env alone
+                    will NOT trigger a billed call.
+
+Cross-family note: if your rewrites come from Claude, point AIWS_JUDGE_MODEL at a
+different model family to avoid judge self-preference (~10-25% PASS inflation).
+For v1 the fixtures' `after` strings are hand-written (not model output), so this
+is a recommendation, not a hard requirement — see evals/README.md.
+"""
+
+import json
+import os
+import re
+import urllib.error
+import urllib.request
+
+# no_fabrication is ALWAYS required for an overall PASS, even when a fixture's
+# rubric_focus does not list it (rubric.md: "Verdict aggregation"). This is the
+# single load-bearing asymmetry the judge exists to enforce.
+ALWAYS_REQUIRED = "no_fabrication"
+
+# One attempt, generous timeout. No retry/backoff in v1 — retry logic is the part
+# a minimal-debugger owner can't maintain, and a clean loud failure is better than
+# silent flakiness (the liveness check in run_judge surfaces a dead provider).
+_TIMEOUT_S = 60
+
+# Matches a rubric per-dimension line: "<snake_case_dim>: PASS|FAIL — reason".
+_DIM_LINE = re.compile(r"^\s*([a-z][a-z_]+)\s*:\s*(PASS|FAIL)\b", re.IGNORECASE)
+
+
+class JudgeError(RuntimeError):
+    """Transport/auth/HTTP failure — must reach the user loudly, never a SKIP."""
+
+
+def is_configured():
+    """True only when fully configured AND explicitly opted in to spend.
+
+    Requiring AIWS_JUDGE_RUN=="1" on top of the credentials means a stray
+    API key already in the environment cannot, by itself, trigger a billed call.
+    """
+    return bool(os.environ.get("AIWS_JUDGE_URL")
+                and os.environ.get("AIWS_JUDGE_MODEL")
+                and os.environ.get("AIWS_JUDGE_KEY")
+                and os.environ.get("AIWS_JUDGE_RUN") == "1")
+
+
+def score(prompt):
+    """Return the model's raw text for `prompt`, or None if not configured.
+
+    State 1 (not configured) -> None (caller SKIPs).
+    State 2 (configured)     -> one POST, return raw text (or None if the 200
+                               response carries no extractable text — the caller
+                               treats that as unparseable and the liveness check
+                               in run_judge turns a whole-suite failure loud).
+    State 3 (call fails)     -> raise JudgeError.
+    """
+    if not is_configured():
+        return None  # honesty stance: no fabrication, caller SKIPs
+
+    url = os.environ["AIWS_JUDGE_URL"]
+    model = os.environ["AIWS_JUDGE_MODEL"]
+    key = os.environ["AIWS_JUDGE_KEY"]
+
+    body = json.dumps({
+        "model": model,

hook: PostToolUse
 succeeded in 267ms:
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

hook: PostToolUse
hook: PostToolUse
hook: PostToolUse Completed
hook: PostToolUse Completed
hook: PostToolUse Completed
codex(58087) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
hook: PreToolUse
hook: PreToolUse
hook: PreToolUse
hook: PreToolUse Completed
hook: PreToolUse Completed
hook: PreToolUse Completed
codex(59223) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
codex(59224) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
codex(59225) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
exec
/bin/zsh -lc "nl -ba skills/ai-writing-suite/evals/test_voice_contract.py | sed -n '1,280p'" in /Users/surahli/Documents/ai-writing-suite
exec
/bin/zsh -lc "nl -ba skills/ai-writing-suite/evals/fixtures/test_fixtures.py | sed -n '1,360p'" in /Users/surahli/Documents/ai-writing-suite
exec
/bin/zsh -lc "sed -n '260,620p' /tmp/phase2a.diff" in /Users/surahli/Documents/ai-writing-suite
 succeeded in 199ms:
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

 succeeded in 199ms:
+        "model": model,
+        "messages": [{"role": "user", "content": prompt}],
+        "temperature": 0,
+    }).encode("utf-8")
+
+    req = urllib.request.Request(url, data=body, method="POST")
+    req.add_header("Content-Type", "application/json")
+    req.add_header("Authorization", f"Bearer {key}")  # never logged/printed
+
+    try:
+        with urllib.request.urlopen(req, timeout=_TIMEOUT_S) as resp:
+            payload = json.loads(resp.read().decode("utf-8"))
+    except urllib.error.HTTPError as e:
+        # 401/403/429/5xx etc. Surface the status, never the key. Loud, not SKIP.
+        raise JudgeError(
+            f"judge HTTP {e.code} from provider — check "
+            f"AIWS_JUDGE_URL / AIWS_JUDGE_KEY / AIWS_JUDGE_MODEL") from None
+    except (urllib.error.URLError, TimeoutError, OSError) as e:
+        raise JudgeError(f"judge transport error: {e}") from None
+
+    return _extract_text(payload)
+
+
+def _extract_text(payload):
+    """Pull assistant text out of a provider response envelope, tolerantly.
+
+    Handles the two common shapes (OpenAI chat-completions, Anthropic messages)
+    plus a couple of fallbacks. Returns None if no text is found — run_judge's
+    liveness check turns an all-None run (with a key present) into a loud nonzero
+    exit ("provider envelope likely changed"), so a silent shape drift can't
+    masquerade as 'all SKIPPED'.
+    """
+    if not isinstance(payload, dict):
+        return None
+    # OpenAI-style: choices[0].message.content
+    choices = payload.get("choices")
+    if isinstance(choices, list) and choices:
+        msg = choices[0].get("message") if isinstance(choices[0], dict) else None
+        if isinstance(msg, dict) and isinstance(msg.get("content"), str):
+            return msg["content"]
+        # some completion APIs put text directly on the choice
+        if isinstance(choices[0], dict) and isinstance(choices[0].get("text"), str):
+            return choices[0]["text"]
+    # Anthropic-style: content[0].text
+    content = payload.get("content")
+    if isinstance(content, list) and content and isinstance(content[0], dict):
+        if isinstance(content[0].get("text"), str):
+            return content[0]["text"]
+    # Last-ditch flat fields.
+    for k in ("output_text", "text", "completion"):
+        if isinstance(payload.get(k), str):
+            return payload[k]
+    return None
+
+
+def parse_dimension_lines(model_text):
+    """Parse a model verdict into {dimension: 'PASS'|'FAIL'}.
+
+    Reads the per-dimension lines (rubric.md output format) and IGNORES the
+    model's self-reported final 'VERDICT:' line — we recompute the verdict
+    ourselves in aggregate(). Returns {} when nothing parses.
+    """
+    out = {}
+    if not isinstance(model_text, str):
+        return out
+    for line in model_text.splitlines():
+        m = _DIM_LINE.match(line)
+        if not m:
+            continue
+        dim = m.group(1).lower()
+        if dim == "verdict":  # never trust the model's self-reported overall line
+            continue
+        out[dim] = m.group(2).upper()
+    return out
+
+
+def majority_vote(per_rep_results):
+    """Merge N per-rep dimension dicts into one by majority vote per dimension.
+
+    For v1 reps=1 this just returns a copy. Ties (or a 50/50 split) resolve to
+    FAIL — the conservative choice for a judge whose job is to catch problems.
+    """
+    if not per_rep_results:
+        return {}
+    if len(per_rep_results) == 1:
+        return dict(per_rep_results[0])
+    dims = set().union(*(d.keys() for d in per_rep_results))
+    merged = {}
+    for d in dims:
+        passes = sum(1 for r in per_rep_results if r.get(d) == "PASS")
+        fails = sum(1 for r in per_rep_results if r.get(d) == "FAIL")
+        merged[d] = "PASS" if passes > fails else "FAIL"
+    return merged
+
+
+def aggregate(per_rep_results, rubric_focus):
+    """Recompute the overall verdict in Python from per-dimension results.
+
+    overall PASS  iff  every required dimension is present AND PASS, where
+    required = the fixture's rubric_focus PLUS no_fabrication (always).
+    Returns None (-> SKIP, never a fake PASS) if any required dimension is
+    missing from the model's output — we do not guess the load-bearing call.
+    """
+    merged = majority_vote(per_rep_results)
+    required = set(rubric_focus) | {ALWAYS_REQUIRED}
+    if any(dim not in merged for dim in required):
+        return None  # incomplete verdict — SKIP, do not fabricate
+    return "PASS" if all(merged[dim] == "PASS" for dim in required) else "FAIL"
diff --git a/skills/ai-writing-suite/evals/fixtures/run_fixtures.py b/skills/ai-writing-suite/evals/fixtures/run_fixtures.py
index 5c458bf..46f4808 100644
--- a/skills/ai-writing-suite/evals/fixtures/run_fixtures.py
+++ b/skills/ai-writing-suite/evals/fixtures/run_fixtures.py
@@ -92,12 +92,21 @@ def run_deterministic(data):
 
 
 def build_judge_prompt(fixture, rubric_template):
-    """Fill the rubric.md judge template for one fixture."""
+    """Fill the rubric.md judge template for one fixture.
+
+    no_fabrication is appended to the focus list when the fixture omits it, so the
+    judge is ALWAYS told to score it. rubric.md requires no_fabrication for every
+    verdict, but 3/8 fixtures don't list it in rubric_focus — without this the
+    highest-stakes dimension would go unscored on those fixtures.
+    """
+    focus = list(fixture["rubric_focus"])
+    if "no_fabrication" not in focus:
+        focus.append("no_fabrication")
     return (rubric_template
             .replace("{genre}", fixture["genre"])
             .replace("{subtle_tell}", fixture.get("subtle_tell",
                      "obvious AI vocabulary and formatting"))
-            .replace("{rubric_focus}", ", ".join(fixture["rubric_focus"]))
+            .replace("{rubric_focus}", ", ".join(focus))
             .replace("{before}", fixture["before"])
             .replace("{after}", fixture["after"]))
 
@@ -112,38 +121,107 @@ def _extract_judge_template():
 
 
 def run_judge(data):
-    """Emit the filled judge prompts and mark them SKIPPED (no model wired in).
-
-    A host integration would replace the `verdict = None` line with a real model
-    call and aggregate per rubric.md. We never fabricate a verdict offline."""
+    """Score fixtures with the optional LLM judge, or SKIP when unconfigured.
+
+    Honesty stance: when no judge is configured (no key, or not opted in via
+    AIWS_JUDGE_RUN=1) we print the filled prompt heads and mark every fixture
+    SKIPPED — we never fabricate a verdict offline. When a judge IS configured we
+    POST each prompt, parse the per-dimension PASS/FAIL lines, and RE-COMPUTE the
+    verdict in Python (no_fabrication-overrides-FAIL, per rubric.md) instead of
+    trusting the model's self-reported VERDICT line. A transport/auth error raises
+    loudly (caller exits nonzero) — never a silent SKIP.
+
+    Returns (passes, fails, skipped, live_error). The judge is ADVISORY in v1:
+    its PASS/FAIL counts do NOT drive the process exit code. The ONE judge
+    condition that does is `live_error` — configured but 0/N scored, meaning the
+    provider response envelope likely changed (a broken harness, surfaced loudly).
+    """
+    from fixtures import judge  # lazy: never imported on the deterministic path
     template = _extract_judge_template()
+    configured = judge.is_configured()
+
     print("\n=== LLM-judge check ===")
-    print("No model is configured in this offline harness — emitting the prompts "
-          "that WOULD be sent, marked SKIPPED.\n")
+    if not configured:
+        print("No judge configured (set AIWS_JUDGE_URL/MODEL/KEY + AIWS_JUDGE_RUN=1) "
+              "— emitting the prompts that WOULD be sent, marked SKIPPED.\n")
+    else:
+        print("Judge configured — scoring each fixture against the rubric.\n")
+
+    passes = fails = skipped = 0
+    agree = gold_total = 0
     for f in data["fixtures"]:
         prompt = build_judge_prompt(f, template)
-        verdict = None  # offline: never invent a verdict
-        print(f"[SKIP] {f['id']} (focus: {', '.join(f['rubric_focus'])})")
-        # Show the first 2 lines of the filled prompt as proof it built.
-        head = "\n".join(prompt.splitlines()[:2])
-        print(f"        prompt[0:2]: {head[:90]}...")
-    print("\nLLM-judge: 0 scored, all SKIPPED (wire a model to run).")
+
+        if not configured:
+            skipped += 1
+            print(f"[SKIP] {f['id']} (focus: {', '.join(f['rubric_focus'])})")
+            # Show the first 2 lines of the filled prompt as proof it built.
+            head = "\n".join(prompt.splitlines()[:2])
+            print(f"        prompt[0:2]: {head[:90]}...")
+            continue
+
+        raw = judge.score(prompt)  # raises JudgeError on transport/auth (loud)
+        verdict = (judge.aggregate([judge.parse_dimension_lines(raw)],
+                                   f["rubric_focus"]) if raw is not None else None)
+        if verdict is None:
+            skipped += 1
+            print(f"[SKIP] {f['id']} — no parseable verdict returned")
+            continue
+
+        if verdict == "PASS":
+            passes += 1
+        else:
+            fails += 1
+        gold = f.get("expected_verdict")
+        if gold is not None:
+            gold_total += 1
+            agree += int(gold == verdict)
+        print(f"[{verdict}] {f['id']}" + (f"  (gold={gold})" if gold else ""))
+
+    scored = passes + fails
+    if not configured:
+        print(f"\nLLM-judge: 0 scored, all {skipped} SKIPPED "
+              f"(configure a judge to run).")
+        return passes, fails, skipped, False
+
+    print(f"\nLLM-judge: {scored} scored ({passes} PASS / {fails} FAIL), "
+          f"{skipped} skipped.")
+    if gold_total:
+        print(f"Judge-vs-gold agreement: {agree}/{gold_total} "
+              f"(advisory — directional only at this n; NOT kappa).")
+
+    # Liveness: configured but nothing scored => provider envelope likely changed.
+    # This is the one judge condition that fails the run (a broken harness, loud),
+    # distinct from the keyless all-SKIP path above which exits 0.
+    live_error = scored == 0
+    if live_error:
+        print(f"ERROR: judge configured but scored 0/{len(data['fixtures'])} — "
+              f"provider response envelope likely changed "
+              f"(check AIWS_JUDGE_URL/MODEL).")
+    return passes, fails, skipped, live_error
 
 
 def main(argv=None):
     argv = argv if argv is not None else sys.argv[1:]
     ap = argparse.ArgumentParser(description="Run before/after eval fixtures.")
     ap.add_argument("--judge", action="store_true",
-                    help="also emit LLM-judge prompts (skipped offline)")
+                    help="also run the LLM-judge half (SKIPPED unless a judge is "
+                         "configured via AIWS_JUDGE_* env vars)")
     args = ap.parse_args(argv)
 
     data = load_fixtures()
     passes, fails = run_deterministic(data)
+
+    # The judge is ADVISORY: its PASS/FAIL counts do NOT change the exit code, so
+    # CI (which never passes --judge and sets no key) stays deterministic and
+    # key-free. The only judge condition that fails the run is a configured-but-
+    # broken judge (live_error: scored 0/N) — a harness error, surfaced loudly.
+    judge_live_error = False
     if args.judge:
-        run_judge(data)
+        _jp, _jf, _js, judge_live_error = run_judge(data)
 
     print(f"\nDeterministic: {passes} passed, {fails} failed.")
-    return 1 if fails else 0
+    return 1 if (fails or judge_live_error) else 0
 
 
 if __name__ == "__main__":
diff --git a/skills/ai-writing-suite/evals/fixtures/test_fixtures.py b/skills/ai-writing-suite/evals/fixtures/test_fixtures.py
index f95ea45..47c5a7b 100644
--- a/skills/ai-writing-suite/evals/fixtures/test_fixtures.py
+++ b/skills/ai-writing-suite/evals/fixtures/test_fixtures.py
@@ -10,6 +10,7 @@ These tests assert the fixture SUITE is well-formed and stays calibrated:
 import unittest
 
 from detector.detector import analyze
+from fixtures import judge
 from fixtures.run_fixtures import (
     load_fixtures, build_judge_prompt, _extract_judge_template)
 
@@ -79,5 +80,218 @@ class JudgePrompt(unittest.TestCase):
             self.assertIn(f["after"], prompt)
 
 
+class JudgePromptAlwaysScoresNoFabrication(unittest.TestCase):
+    """no_fabrication must be requested for EVERY fixture, even the 3 whose
+    rubric_focus omits it — otherwise the highest-stakes dimension goes
+    unscored on those fixtures."""
+
+    def test_every_prompt_requests_no_fabrication(self):
+        template = _extract_judge_template()
+        for f in load_fixtures()["fixtures"]:
+            prompt = build_judge_prompt(f, template)
+            self.assertIn("no_fabrication", prompt,
+                          f"{f['id']} prompt does not request no_fabrication")
+
+
+class GoldLabels(unittest.TestCase):
+    def test_expected_verdict_is_valid_when_present(self):
+        for f in load_fixtures()["fixtures"]:
+            gv = f.get("expected_verdict")
+            if gv is not None:
+                self.assertIn(gv, ("PASS", "FAIL"),
+                              f"{f['id']} expected_verdict={gv!r} not PASS/FAIL")
+
+
+class JudgeParsing(unittest.TestCase):
+    """Parse + aggregate the model's verdict from CANNED responses — no network,
+    no key, runs in CI. Guards the judge logic the way ScoreBands/Calibration
+    guard the deterministic half."""
+
+    def test_clean_all_pass(self):
+        text = ("meaning_preserved: PASS — facts kept\n"
+                "tells_removed: PASS — vocab cleaned\n"
+                "voice_kept: PASS — sounds human\n"
+                "no_fabrication: PASS — nothing invented\n"
+                "VERDICT: PASS")
+        verdict = judge.aggregate([judge.parse_dimension_lines(text)],
+                                  ["meaning_preserved", "tells_removed", "voice_kept"])
+        self.assertEqual(verdict, "PASS")
+
+    def test_no_fabrication_fail_forces_overall_fail(self):
+        # focus does NOT list no_fabrication (mirrors readme-01) yet a fabricated
+        # rewrite must still FAIL — the load-bearing asymmetry. Also proves we
+        # IGNORE the model's self-reported "VERDICT: PASS" line.
+        text = ("meaning_preserved: PASS\n"
+                "tells_removed: PASS\n"
+                "specificity_added: PASS\n"
+                "no_fabrication: FAIL — invented a 2GB figure not in the source\n"
+                "VERDICT: PASS")
+        verdict = judge.aggregate([judge.parse_dimension_lines(text)],
+                                  ["meaning_preserved", "tells_removed",
+                                   "specificity_added"])
+        self.assertEqual(verdict, "FAIL")
+
+    def test_fabrication_trap_caught(self):
+        # A fluent rewrite that invents a metric: every other dim PASS, only
+        # no_fabrication FAIL. The single discrimination the judge exists to make.
+        text = ("meaning_preserved: PASS\n"
+                "voice_kept: PASS\n"
+                "genre_fit: PASS\n"
+                "no_fabrication: FAIL — '37% faster' appears nowhere in before\n"
+                "VERDICT: PASS")
+        verdict = judge.aggregate([judge.parse_dimension_lines(text)],
+                                  ["voice_kept", "genre_fit"])
+        self.assertEqual(verdict, "FAIL")
+
+    def test_focus_dim_fail_forces_fail(self):
+        text = ("meaning_preserved: FAIL — dropped the retention number\n"
+                "tells_removed: PASS\n"
+                "no_fabrication: PASS\n"
+                "VERDICT: FAIL")
+        verdict = judge.aggregate([judge.parse_dimension_lines(text)],
+                                  ["meaning_preserved", "tells_removed"])
+        self.assertEqual(verdict, "FAIL")
+
+    def test_unparseable_returns_none(self):
+        text = "The rewrite reads well overall and keeps the meaning."
+        self.assertEqual(judge.parse_dimension_lines(text), {})
+        self.assertIsNone(
+            judge.aggregate([judge.parse_dimension_lines(text)], ["voice_kept"]))
+
+    def test_missing_required_dim_returns_none(self):
+        # no_fabrication line absent -> can't enforce the load-bearing rule ->
+        # SKIP (None), never a fabricated PASS.
+        text = ("meaning_preserved: PASS\n"
+                "tells_removed: PASS\n"
+                "specificity_added: PASS")
+        self.assertIsNone(
+            judge.aggregate([judge.parse_dimension_lines(text)],

 succeeded in 199ms:
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

hook: PostToolUse
hook: PostToolUse
hook: PostToolUse
hook: PostToolUse Completed
hook: PostToolUse Completed
hook: PostToolUse Completed
codex(59441) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
codex(59442) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
codex(59443) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
codex(59444) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
codex(59446) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
codex(60380) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
codex(60381) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
codex(60382) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
codex(60383) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
codex
The implementation does keep the production deterministic path separate at first pass, but I’m now checking the surrounding CI/test invocation because a test importing `judge.py` can still violate the “CI never imports judge.py” invariant depending on workflow wiring.
hook: PreToolUse
hook: PreToolUse
hook: PreToolUse
hook: PreToolUse
hook: PreToolUse Completed
hook: PreToolUse Completed
hook: PreToolUse Completed
hook: PreToolUse Completed
codex(62186) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
codex(62185) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
codex(62207) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
codex(62208) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
codex(62211) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
codex(62212) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
codex(62224) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
codex(62225) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
exec
/bin/zsh -lc "nl -ba .gitignore | sed -n '1,220p'" in /Users/surahli/Documents/ai-writing-suite
exec
/bin/zsh -lc "nl -ba .github/workflows/ci.yml | sed -n '1,260p'" in /Users/surahli/Documents/ai-writing-suite
exec
/bin/zsh -lc "nl -ba skills/ai-writing-suite/evals/run_all.sh | sed -n '1,220p'" in /Users/surahli/Documents/ai-writing-suite
exec
/bin/zsh -lc 'git diff --name-status -- /tmp/phase2a.diff .gitignore .github/workflows/ci.yml skills/ai-writing-suite/evals/run_all.sh skills/ai-writing-suite/evals/fixtures/fixtures.json skills/ai-writing-suite/evals/fixtures/run_fixtures.py skills/ai-writing-suite/evals/fixtures/test_fixtures.py skills/ai-writing-suite/evals/test_voice_contract.py skills/ai-writing-suite/evals/fixtures/judge.py' in /Users/surahli/Documents/ai-writing-suite
 succeeded in 3366ms:
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

 succeeded in 3460ms:
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

 succeeded in 3481ms:
     1	__pycache__/
     2	*.py[cod]
     3	
     4	# OMC runtime state
     5	.omc/

hook: PostToolUse
hook: PostToolUse
hook: PostToolUse
hook: PostToolUse
 exited 128 in 4107ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
fatal: /tmp/phase2a.diff: '/tmp/phase2a.diff' is outside repository at '/Users/surahli/Documents/ai-writing-suite'

hook: PostToolUse Completed
hook: PostToolUse Completed
hook: PostToolUse Completed
hook: PostToolUse Completed
codex(63503) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
codex(63504) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
codex(63507) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
codex(63508) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
hook: PreToolUse
hook: PreToolUse
hook: PreToolUse
hook: PreToolUse Completed
hook: PreToolUse Completed
hook: PreToolUse Completed
codex(65366) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
codex(65367) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
codex(65365) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
codex(65368) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
codex(65369) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
codex(65370) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
codex(65371) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
codex(65372) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
exec
/bin/zsh -lc "git diff -- skills/ai-writing-suite/evals/fixtures/fixtures.json | rg -n '"'^[+-]'"\\s*\"id\"|"'^[+-]'"\\s*\"expected_verdict\"|"'^[+-]'"\\s*\"_doc\"|"'^[+-]'"'" in /Users/surahli/Documents/ai-writing-suite
exec
/bin/zsh -lc 'git diff -- .gitignore .github/workflows/ci.yml skills/ai-writing-suite/evals/run_all.sh' in /Users/surahli/Documents/ai-writing-suite
exec
/bin/zsh -lc 'git diff --name-status' in /Users/surahli/Documents/ai-writing-suite
hook: PostToolUse
hook: PostToolUse
hook: PostToolUse
 succeeded in 1051ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead

 succeeded in 1057ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
M	skills/ai-writing-suite/evals/README.md
M	skills/ai-writing-suite/evals/fixtures/fixtures.json
A	skills/ai-writing-suite/evals/fixtures/judge.py
M	skills/ai-writing-suite/evals/fixtures/run_fixtures.py
M	skills/ai-writing-suite/evals/fixtures/test_fixtures.py
A	skills/ai-writing-suite/evals/test_voice_contract.py

 succeeded in 1168ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
3:--- a/skills/ai-writing-suite/evals/fixtures/fixtures.json
4:+++ b/skills/ai-writing-suite/evals/fixtures/fixtures.json
7:-  "_doc": "Before/after LLM-judge fixtures across 4 genres (tweet/linkedin/readme/memo). Each fixture: an AI-shaped `before`, a good human `after`, and what we expect. `before_band_min`/`before_band_max`/`after_band_max` are detector score-band expectations (mechanical, deterministic regression guards bracketing the observed score). `rubric_focus` lists which rubric dimensions the LLM judge should weigh. Difficulty is calibrated so a NAIVE baseline (flag-if-detector-score >= baseline_threshold) misses ~30-40% of the `before` items: the `subtle` ones are AI-written but score LOW because they avoid vocabulary tells and lean on structural/rhythm tells a flat threshold underweights. See README calibration section.",
8:+  "_doc": "Before/after LLM-judge fixtures across 4 genres (tweet/linkedin/readme/memo). Each fixture: an AI-shaped `before`, a good human `after`, and what we expect. `before_band_min`/`before_band_max`/`after_band_max` are detector score-band expectations (mechanical, deterministic regression guards bracketing the observed score). `rubric_focus` lists which rubric dimensions the LLM judge should weigh. Difficulty is calibrated so a NAIVE baseline (flag-if-detector-score >= baseline_threshold) misses ~30-40% of the `before` items: the `subtle` ones are AI-written but score LOW because they avoid vocabulary tells and lean on structural/rhythm tells a flat threshold underweights. See README calibration section. `expected_verdict` (PASS|FAIL) is the owner's gold label for advisory judge-vs-gold agreement: all current fixtures are good rewrites (PASS); FAIL exemplars live in the unit tests (test_fixtures.py), not here, to preserve the 30-40% calibration band.",
13:+      "expected_verdict": "PASS",
21:+      "expected_verdict": "PASS",
29:+      "expected_verdict": "PASS",
37:+      "expected_verdict": "PASS",
45:+      "expected_verdict": "PASS",
53:+      "expected_verdict": "PASS",
61:+      "expected_verdict": "PASS",
69:+      "expected_verdict": "PASS",

hook: PostToolUse Completed
hook: PostToolUse Completed
hook: PostToolUse Completed
codex(66367) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
codex(66379) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
codex(66380) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
codex(66381) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
codex
One important point is emerging: the new judge tests may not be on the same path as the deterministic harness, so I’m verifying actual unittest discovery rather than assuming the filename placement is enough.
hook: PreToolUse
hook: PreToolUse
hook: PreToolUse
hook: PreToolUse Completed
hook: PreToolUse Completed
hook: PreToolUse Completed
codex(68012) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
codex(68013) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
codex(68019) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
codex(68040) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
codex(68041) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
codex(68042) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
codex(68043) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
exec
/bin/zsh -lc 'cd skills/ai-writing-suite/evals && PYTHONDONTWRITEBYTECODE=1 python3 -m fixtures.run_fixtures' in /Users/surahli/Documents/ai-writing-suite
exec
/bin/zsh -lc 'find skills/ai-writing-suite/evals -maxdepth 3 -type f | sort' in /Users/surahli/Documents/ai-writing-suite
exec
/bin/zsh -lc "cd skills/ai-writing-suite/evals && PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -p 'test_*.py' -v" in /Users/surahli/Documents/ai-writing-suite
 succeeded in 482ms:
skills/ai-writing-suite/evals/.omc/state/last-tool-error.json
skills/ai-writing-suite/evals/README.md
skills/ai-writing-suite/evals/__pycache__/smoke_test.cpython-314.pyc
skills/ai-writing-suite/evals/__pycache__/test_voice_contract.cpython-314.pyc
skills/ai-writing-suite/evals/__pycache__/test_zzz_canary.cpython-314.pyc
skills/ai-writing-suite/evals/detector/__init__.py
skills/ai-writing-suite/evals/detector/__pycache__/__init__.cpython-314.pyc
skills/ai-writing-suite/evals/detector/__pycache__/cli.cpython-314.pyc
skills/ai-writing-suite/evals/detector/__pycache__/detector.cpython-314.pyc
skills/ai-writing-suite/evals/detector/__pycache__/patterns.cpython-314.pyc
skills/ai-writing-suite/evals/detector/__pycache__/test_detector.cpython-314.pyc
skills/ai-writing-suite/evals/detector/cli.py
skills/ai-writing-suite/evals/detector/detector.py
skills/ai-writing-suite/evals/detector/patterns.py
skills/ai-writing-suite/evals/detector/test_detector.py
skills/ai-writing-suite/evals/fixtures/__init__.py
skills/ai-writing-suite/evals/fixtures/__pycache__/__init__.cpython-314.pyc
skills/ai-writing-suite/evals/fixtures/__pycache__/judge.cpython-314.pyc
skills/ai-writing-suite/evals/fixtures/__pycache__/run_fixtures.cpython-314.pyc
skills/ai-writing-suite/evals/fixtures/__pycache__/test_fixtures.cpython-314.pyc
skills/ai-writing-suite/evals/fixtures/fixtures.json
skills/ai-writing-suite/evals/fixtures/judge.py
skills/ai-writing-suite/evals/fixtures/rubric.md
skills/ai-writing-suite/evals/fixtures/run_fixtures.py
skills/ai-writing-suite/evals/fixtures/test_fixtures.py
skills/ai-writing-suite/evals/run_all.sh
skills/ai-writing-suite/evals/smoke_test.py
skills/ai-writing-suite/evals/test_voice_contract.py

hook: PostToolUse
 succeeded in 2331ms:
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

hook: PostToolUse Completed
hook: PostToolUse
 succeeded in 3289ms:
test_chatbot_artifact (detector.test_detector.CategoryDetectors.test_chatbot_artifact) ... ok
test_citation_markup_leak (detector.test_detector.CategoryDetectors.test_citation_markup_leak) ... ok
test_cutoff_disclaimer (detector.test_detector.CategoryDetectors.test_cutoff_disclaimer) ... ok
test_hashtag_stuffing (detector.test_detector.CategoryDetectors.test_hashtag_stuffing) ... ok
test_placeholder_fingerprint (detector.test_detector.CategoryDetectors.test_placeholder_fingerprint) ... ok
test_tier2_cluster_requires_two (detector.test_detector.CategoryDetectors.test_tier2_cluster_requires_two) ... ok
test_title_case_header_general_mode (detector.test_detector.CategoryDetectors.test_title_case_header_general_mode) ... ok
test_title_case_header_skipped_in_technical_mode (detector.test_detector.CategoryDetectors.test_title_case_header_skipped_in_technical_mode) ... ok
test_vague_attribution (detector.test_detector.CategoryDetectors.test_vague_attribution) ... ok
test_empty (detector.test_detector.LengthGates.test_empty) ... ok
test_too_long (detector.test_detector.LengthGates.test_too_long) ... ok
test_too_short (detector.test_detector.LengthGates.test_too_short) ... ok
test_ai_heavy_scores_high (detector.test_detector.ScoreBands.test_ai_heavy_scores_high) ... ok
test_plain_human_prose_stays_low (detector.test_detector.ScoreBands.test_plain_human_prose_stays_low) ... ok
test_dedup_counts_distinct_signals (detector.test_detector.ScoringMath.test_dedup_counts_distinct_signals) ... ok
test_cutoff_disclaimer_forces_ai_only (detector.test_detector.TrinaryClassifier.test_cutoff_disclaimer_forces_ai_only) ... ok
test_human_prose_never_ai_only (detector.test_detector.TrinaryClassifier.test_human_prose_never_ai_only) ... ok
test_deterministic_and_offline_judge_make_no_network_call (fixtures.test_fixtures.CIClean.test_deterministic_and_offline_judge_make_no_network_call) ... ok
test_judge_not_imported_at_module_load (fixtures.test_fixtures.CIClean.test_judge_not_imported_at_module_load) ... ok
test_expect_baseline_matches_actual (fixtures.test_fixtures.Calibration.test_expect_baseline_matches_actual) ... ok
test_naive_baseline_misses_30_to_40_percent (fixtures.test_fixtures.Calibration.test_naive_baseline_misses_30_to_40_percent) ... ok
test_all_fixtures_have_required_fields (fixtures.test_fixtures.FixtureShape.test_all_fixtures_have_required_fields) ... ok
test_four_genres_present (fixtures.test_fixtures.FixtureShape.test_four_genres_present) ... ok
test_expected_verdict_is_valid_when_present (fixtures.test_fixtures.GoldLabels.test_expected_verdict_is_valid_when_present) ... ok
test_key_without_optin_does_not_fire (fixtures.test_fixtures.JudgeGate.test_key_without_optin_does_not_fire) ... ok
test_not_configured_by_default_returns_none (fixtures.test_fixtures.JudgeGate.test_not_configured_by_default_returns_none) ... ok
test_all_pass_scores_full_agreement_no_live_error (fixtures.test_fixtures.JudgeIntegration.test_all_pass_scores_full_agreement_no_live_error) ... ok
test_all_unparseable_triggers_live_error (fixtures.test_fixtures.JudgeIntegration.test_all_unparseable_triggers_live_error) ... ok
test_fabrication_makes_a_fixture_fail (fixtures.test_fixtures.JudgeIntegration.test_fabrication_makes_a_fixture_fail) ... ok
test_clean_all_pass (fixtures.test_fixtures.JudgeParsing.test_clean_all_pass) ... ok
test_fabrication_trap_caught (fixtures.test_fixtures.JudgeParsing.test_fabrication_trap_caught) ... ok
test_focus_dim_fail_forces_fail (fixtures.test_fixtures.JudgeParsing.test_focus_dim_fail_forces_fail) ... ok
test_majority_vote_across_reps (fixtures.test_fixtures.JudgeParsing.test_majority_vote_across_reps) ... ok
test_majority_vote_tie_resolves_fail (fixtures.test_fixtures.JudgeParsing.test_majority_vote_tie_resolves_fail) ... ok
test_missing_required_dim_returns_none (fixtures.test_fixtures.JudgeParsing.test_missing_required_dim_returns_none) ... ok
test_no_fabrication_fail_forces_overall_fail (fixtures.test_fixtures.JudgeParsing.test_no_fabrication_fail_forces_overall_fail) ... ok
test_parse_excludes_self_reported_verdict_line (fixtures.test_fixtures.JudgeParsing.test_parse_excludes_self_reported_verdict_line) ... ok
test_unparseable_returns_none (fixtures.test_fixtures.JudgeParsing.test_unparseable_returns_none) ... ok
test_prompt_builds_for_every_fixture (fixtures.test_fixtures.JudgePrompt.test_prompt_builds_for_every_fixture) ... ok
test_every_prompt_requests_no_fabrication (fixtures.test_fixtures.JudgePromptAlwaysScoresNoFabrication.test_every_prompt_requests_no_fabrication) ... ok
test_before_after_scores_in_band (fixtures.test_fixtures.ScoreBands.test_before_after_scores_in_band) ... ok
test_all_consumer_headers_present (test_voice_contract.VoiceProfileContract.test_all_consumer_headers_present) ... ok
test_template_exists (test_voice_contract.VoiceProfileContract.test_template_exists) ... ok

----------------------------------------------------------------------
Ran 43 tests in 0.478s

OK

hook: PostToolUse
hook: PostToolUse Completed
hook: PostToolUse Completed
hook: PreToolUse
codex(70790) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
codex(70791) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
hook: PreToolUse Completed
codex(70803) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
codex(70804) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
exec
/bin/zsh -lc 'PYTHONDONTWRITEBYTECODE=1 bash skills/ai-writing-suite/evals/run_all.sh' in /Users/surahli/Documents/ai-writing-suite
 succeeded in 3451ms:
== [1/3] unit tests ==
...........................................
----------------------------------------------------------------------
Ran 43 tests in 0.460s

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

hook: PostToolUse
hook: PostToolUse Completed
codex
The checks pass, but passing tests are not enough here: `run_all.sh` currently imports `fixtures.judge` during unit discovery, which conflicts with the stated CI/no-import invariant even though it does not make a network call. I’m checking for additional silent-failure edges before finalizing.
hook: PreToolUse
hook: PreToolUse
hook: PreToolUse
hook: PreToolUse Completed
hook: PreToolUse Completed
hook: PreToolUse Completed
codex(73577) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
codex(73602) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
codex(73613) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
exec
/bin/zsh -lc "nl -ba skills/ai-writing-suite/_shared/host-profile-template.md | sed -n '1,220p'" in /Users/surahli/Documents/ai-writing-suite
exec
/bin/zsh -lc "nl -ba skills/ai-writing-suite/evals/fixtures/rubric.md | sed -n '1,260p'" in /Users/surahli/Documents/ai-writing-suite
exec
/bin/zsh -lc 'rg -n "Voice Matching|Tone|Sentence Length|Vocabulary|Signature Moves|Punctuation|Openings|Uncertainty|Things To Avoid|Scope" skills/ai-writing-suite/skills/comms-polish/SKILL.md' in /Users/surahli/Documents/ai-writing-suite
 succeeded in 340ms:
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

 succeeded in 337ms:
     1	<!--
     2	================================================================================
     3	  host-profile-template.md  —  BLANK VOICE FORM
     4	================================================================================
     5	
     6	  WHAT THIS IS
     7	  ------------
     8	  The reusable blank form that `voice-onboard` fills in, one field at a time,
     9	  from your interview answers + writing samples. When complete, its contents
    10	  are written out to `voice-profile.md` (the contract file `comms-polish`
    11	  reads).
    12	
    13	  HOW TO USE
    14	  ----------
    15	  Copy this file. Fill each field from the user's samples. Keep the SAME H2
    16	  headers as `voice-profile.md` — that file is the contract, this is its blank
    17	  twin. Renaming headers here breaks the hand-off.
    18	
    19	  THE ONE RULE
    20	  ------------
    21	  Every field needs sample evidence. No evidence -> write "Unknown — not enough
    22	  signal in samples". Do NOT invent a trait to fill a blank. A guessed profile
    23	  is worse than an empty one, because the reader skill will trust it.
    24	
    25	  CONFIDENCE
    26	  ----------
    27	  A trait counts only if it shows up 3+ times. One occurrence is noise, not a
    28	  habit. With <5 samples, mark Confidence = Low and fill conservatively.
    29	================================================================================
    30	-->
    31	
    32	# Host Profile — [author name]
    33	
    34	## Meta
    35	
    36	- **Author:** [name / id]
    37	- **Extracted:** [YYYY-MM-DD]
    38	- **Sample count:** [N]
    39	- **Sample sources:** [blog / LinkedIn / X / internal memos / other]
    40	- **Sample time span:** [earliest — latest]
    41	- **Confidence:** [Low (N<5) / Medium (5-10) / High (10+)]
    42	
    43	## Tone
    44	
    45	- [overall register in 1-2 sentences: e.g. direct / warm / dry / formal]
    46	
    47	> Evidence: [paste 1 sentence that shows the tone]
    48	
    49	## Sentence Length
    50	
    51	- **Average words/sentence:** [number]
    52	- **Short sentences (<10 words) share:** [%]
    53	- **Long sentences (>30 words) share:** [%]
    54	- **Rhythm habit:** [e.g. "short hook, then long qualifier"; or "Unknown"]
    55	
    56	> Evidence: [paste 1-2 sentences]
    57	
    58	## Vocabulary
    59	
    60	- **First person:** ["I" / "we" / subject-less / depends]
    61	- **Signature words:** [3-8 distinctive words, after stripping generic ones]
    62	- **Stock phrases / tics:** [list, or "none obvious"]
    63	- **Domain / in-group terms:** [3-5]
    64	
    65	## Vocabulary Do
    66	
    67	- [words / constructions the author actively reaches for]
    68	
    69	## Vocabulary Don't
    70	
    71	<!-- STRONGEST signal. Common words the author NEVER uses. -->
    72	- [forbidden words: e.g. "delve", "leverage", "unlock", hype punctuation]
    73	
    74	## Signature Moves
    75	
    76	- [characteristic ways they build a point: e.g. "not X but Y" reframes, leads
    77	  with a number, ends on a consequence]
    78	
    79	## Punctuation & Formatting
    80	
    81	- **Period vs comma:** [period-heavy / comma-heavy / balanced]
    82	- **Em-dash density:** [often / occasional / never]
    83	- **Ellipsis / exclamation:** [density]
    84	- **Lists:** [uses bullets? numbered steps?]
    85	- **Emoji:** [yes / no / which ones / position]
    86	
    87	## Openings & Closings
    88	
    89	- **Opening habit:** [scene / claim / question / number / contrarian / other]
    90	- **Closing habit:** [hook / consequence / open question / trails off / other]
    91	
    92	> Evidence (open): "[paste original opening]"
    93	> Evidence (close): "[paste original closing]"
    94	
    95	## Uncertainty Style
    96	
    97	- [quantified ("70% sure") / blunt ("I don't know") / hedged ("perhaps") / avoids]
    98	
    99	> Evidence: [paste 1 sentence]
   100	
   101	## Things To Avoid
   102	
   103	- [author-specific anti-patterns beyond the forbidden word list: registers,
   104	  structures, moves that read as "not them"]
   105	
   106	## Scope & Calibration
   107	
   108	- **Applies to:** [genres these samples cover]
   109	- **Re-calibrate for:** [genres not covered — flag so the reader doesn't misapply]
   110	
   111	## Changelog
   112	
   113	- [YYYY-MM-DD] First created from N samples.
   114	- [YYYY-MM-DD] [added/removed trait X — reason: user said "X felt off"]
   115	
   116	<!--
   117	  ATTRIBUTION
   118	  -----------
   119	  Adapted from weijt606/anti-vibe-writing host-profile-template.md (MIT):
   120	  ported from Chinese to English and aligned to the suite's voice-profile.md
   121	  field contract. Do's/Don'ts framing borrowed from
   122	  donghuixin/AI-Vibe-Writing-Skills 1_style_extractor.md (MIT). Full copyright
   123	  lines in the suite NOTICE.md. Bilingual (Chinese) path = v2 per design D-scope.
   124	-->

hook: PostToolUse
hook: PostToolUse
hook: PostToolUse
 succeeded in 478ms:
24:  so rewrites bias toward how *they* write (see Voice Matching).
68:## Voice Matching
77:   present: Tone, Sentence Length, Vocabulary Do / Vocabulary Don't, Signature
78:   Moves, Punctuation & Formatting, Openings & Closings, Uncertainty Style, Things
79:   To Avoid, and Scope & Calibration (which says where the profile applies). Read
116:   (see Voice Matching). Degrade gracefully when absent.

hook: PostToolUse Completed
hook: PostToolUse Completed
hook: PostToolUse Completed
codex(73774) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
codex(73775) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
codex(73776) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
codex(73777) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
hook: PreToolUse
codex(75895) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
hook: PreToolUse Completed
exec
/bin/zsh -lc "nl -ba skills/ai-writing-suite/skills/comms-polish/SKILL.md | sed -n '60,95p'" in /Users/surahli/Documents/ai-writing-suite
 succeeded in 149ms:
    60	
    61	| Mode | Use When | Output |
    62	| --- | --- | --- |
    63	| `detect` | The user wants to know what sounds AI-written. | Findings and examples, no rewrite. |
    64	| `review` | The user wants prioritized writing feedback. | Findings first, with examples. |
    65	| `rewrite` | The user pasted text and wants a polished version. | Polished text only unless notes are requested. |
    66	| `edit` | The user asks to modify a file. | Targeted file edits plus verification. |
    67	
    68	## Voice Matching
    69	
    70	Voice has three sources, in priority order:
    71	
    72	1. **A learned voice profile** at `../../_shared/voice-profile.md` (canonical path:
    73	   `_shared/voice-profile.md`). This is produced by the `voice-onboard` sub-skill.
    74	   **Before any rewrite, check whether this file exists and read it if it does.**
    75	   It is loose coupling: comms-polish does not create or own that file — it reads
    76	   whatever fields are present and biases edits toward them. Sections to use when
    77	   present: Tone, Sentence Length, Vocabulary Do / Vocabulary Don't, Signature
    78	   Moves, Punctuation & Formatting, Openings & Closings, Uncertainty Style, Things
    79	   To Avoid, and Scope & Calibration (which says where the profile applies). Read
    80	   what's there; ignore what isn't — never fail on a missing section.
    81	2. **A writing sample the user pastes** in this request — match it directly.
    82	3. **Inferred voice** from the draft itself, when neither of the above exists.
    83	
    84	**Graceful degradation:** if `_shared/voice-profile.md` is absent, do not error
    85	and do not block. Note briefly that no profile was found, then polish normally
    86	using a pasted sample or inferred voice. The profile is a bias signal, never a
    87	hard dependency. A hard genre constraint (e.g. a tweet's 280-char limit) still
    88	wins over a profile preference.
    89	
    90	When a profile or sample exists, match:
    91	
    92	- sentence length and rhythm
    93	- plainness or formality
    94	- punctuation habits
    95	- paragraph shape

hook: PostToolUse
hook: PostToolUse Completed
codex(75989) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
codex(75990) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
2026-06-08T02:40:10.928827Z ERROR codex_models_manager::manager: failed to renew cache TTL: EOF while parsing a value at line 1 column 0
codex(79747) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
codex(79768) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
codex(79774) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
codex(83103) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
codex(83104) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
codex(83105) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
codex
Independent code-review lane found the same lazy-import/test-boundary issue plus a majority-vote edge. I’m waiting for the architecture lane, then I’ll collapse duplicates and keep the final list tight.
hook: PreToolUse
hook: PreToolUse Completed
collab: Wait
codex(85656) MallocStackLogging: can't turn off malloc stack logging because it was not enabled.
