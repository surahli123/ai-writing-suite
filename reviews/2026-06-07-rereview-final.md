Reading prompt from stdin...
OpenAI Codex v0.137.0
--------
workdir: /Users/surahli/Documents/ai-writing-suite
model: gpt-5.5
provider: chatgpt_http
approval: never
sandbox: read-only
reasoning effort: medium
reasoning summaries: none
session id: 019ea3df-c303-7443-994f-abb812bff36c
--------
user
You are an ADVERSARIAL code reviewer with independent context. In THIS git repo run `git diff main..HEAD` (final commit 41333e9) and read whatever files you need. Produce a structured adversarial review of the FINAL state.

This is a REVISION. An earlier commit took a "commit the Codex plugin body" approach; a prior review flagged that Claude then shipped a nested duplicate of the suite. THIS final commit resolves that by switching to **source-pointing**: both Claude and Codex install directly from the single source tree `skills/ai-writing-suite/` via repo-root marketplace manifests, and the entire generate-and-sync packaging (packaging/ + sync.sh + the committed body + the drift guardrail) was DELETED.

Final structure to assess:
 - Repo-root `.claude-plugin/marketplace.json` → plugin source `./skills/ai-writing-suite`
 - Repo-root `.agents/plugins/marketplace.json` (Codex) → plugin source {source:local, path:./skills/ai-writing-suite}
 - In-source `skills/ai-writing-suite/.claude-plugin/plugin.json` and `skills/ai-writing-suite/.codex-plugin/plugin.json`
 - `.gitignore` simplified (packaging carve-outs removed)
 - README per-host install (Claude/Codex no --sparse; Cursor copy), `docs/packaging.md` maintainer note
 - `packaging/` and `sync.sh` removed entirely

Already verified by me (local CLIs): Claude `plugin install` discovers 4 skills; Codex installs from the root marketplace resolving to the source tree; tests 23/23 + smoke 3/3 + fixtures 8/8.

Focus on the DELTA and the final state:
 1. Does removing packaging/ + sync.sh introduce any new problem (dangling references in docs/manifests, broken links, lost capability)? grep the repo for stale `packaging/` or `sync.sh` references.
 2. Is the Codex root `.agents/plugins/marketplace.json` with a non-`plugins/`-relative source path (`./skills/ai-writing-suite`) robust/portable, or did my local smoke pass by luck? Any resolution risk on a fresh GitHub clone vs my local path test?
 3. Two manifests now live INSIDE the published source tree (.claude-plugin, .codex-plugin) and the tree also ships evals/ to consumers — any real problem (double-discovery, foreign-manifest confusion, bloat)?
 4. README/docs correctness: are the install commands right for the new layout (no --sparse for Codex; root marketplace for both)?
 5. Any footgun in version/update flow now that there's no sync version-lockstep check?

Output EXACTLY:
  ## BLOCKER (must fix before merge)
  ## CONCERN (should address)
  ## SUGGESTION (nice to have)
Constraints: minimum 2 hard questions; every critique includes a concrete fix or a clear "this needs to change because…"; if strong, say why in one sentence and move on; do not pad severity. If the revision is clean, say so plainly.

2026-06-07T20:57:05.577878Z ERROR rmcp::transport::worker: worker quit with fatal: Transport channel closed, when AuthRequired(AuthRequiredError { www_authenticate_header: "Bearer realm=\"OAuth\", resource_metadata=\"https://mcp.cloudflare.com/.well-known/oauth-protected-resource/mcp\", error=\"invalid_token\"" })
hook: SessionStart
hook: SessionStart
hook: SessionStart
hook: SessionStart Completed
hook: SessionStart Completed
hook: SessionStart Failed
hook: UserPromptSubmit
hook: UserPromptSubmit
hook: UserPromptSubmit
hook: UserPromptSubmit Completed
hook: UserPromptSubmit Completed
hook: UserPromptSubmit Completed
codex
I’ll review the final diff against `main`, then verify the specific stale-reference and manifest-path questions from the checked-out repo state. This is read-only under the current sandbox, so I’ll focus on evidence from git/file inspection and report only actionable issues.
hook: PreToolUse
hook: PreToolUse
hook: PreToolUse
hook: PreToolUse Completed
hook: PreToolUse Completed
hook: PreToolUse Completed
exec
/bin/zsh -lc "git status --short --branch && git rev-parse --short HEAD && git merge-base --is-ancestor 41333e9 HEAD; printf 'ancestor_status=%s\\n' "'$?' in /Users/surahli/Documents/ai-writing-suite
exec
/bin/zsh -lc "sed -n '1,220p' /Users/surahli/.codex/skills/code-review/SKILL.md" in /Users/surahli/Documents/ai-writing-suite
exec
/bin/zsh -lc "rg -n \"ai-writing-suite|packaging|sync\\.sh|marketplace|Codex|Claude\" /Users/surahli/.codex/memories/MEMORY.md" in /Users/surahli/Documents/ai-writing-suite
hook: PostToolUse
 succeeded in 169ms:
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
 succeeded in 362ms:
39:- when the user objected that Goal Forge had confused the `whole goal` with the `immediate restarted session` -> future goal packaging must separate program scope from current phase/session execution budget explicitly [Task 2][Task 3]
63:- extensions/chronicle/resources/2026-06-06T02-23-00-YfEG-10min-memory-summary.md (cwd=/Users/surahli/Documents/projects/SMA_v2, rollout_path=/Users/surahli/.codex/memories/extensions/chronicle/resources/2026-06-06T02-23-00-YfEG-10min-memory-summary.md, updated_at=2026-06-06T02:23:00+00:00, thread_id=None, Chronicle window showing fresh Claude Code orientation, branch `codex/sma-rewrite-evidence-bridge-shadow-run`, dirty `.agents/skills/sma_rewrite/evals/`, and planning prompts grounded in data-agent / skill-system references)
164:- extensions/chronicle/resources/2026-06-06T02-23-00-YfEG-10min-memory-summary.md (cwd=/Users/surahli/Documents/projects/travel-agent, rollout_path=/Users/surahli/.codex/memories/extensions/chronicle/resources/2026-06-06T02-23-00-YfEG-10min-memory-summary.md, updated_at=2026-06-06T02:23:00+00:00, thread_id=None, Chronicle window showing the user choosing tracks 1 and 3 first, Claude Code research over competition pages/app source, and the open PR context in `agentic-search-online-eval`)
207:- when the user continued this lane from a prior Claude Code session and wanted the existing research artifacts reused -> begin from the repo-local notes and reported smoke results instead of redoing the baseline study from scratch [Task 4]
250:- rollout_summaries/2026-06-06T06-07-03-B2Ti-chinatravel_calib30_crosscheck_p0_hard_filter_vs_receipt_hyg.md (cwd=/Users/surahli/Documents/projects/travel-agent, rollout_path=/Users/surahli/.codex/sessions/2026/06/05/rollout-2026-06-05T23-07-03-019e9b8a-c389-78b3-b022-8e74e90a89c4.jsonl, updated_at=2026-06-07T02:19:51+00:00, thread_id=019e9b8a-c389-78b3-b022-8e74e90a89c4, read-only cross-check of the Claude handoff, scorer mismatch, and the higher-leverage hard-filter direction)
270:- when the user wanted the next-session prompt to say whether OMX should be used -> state plainly that Codex App should use direct execution/native subagents outside attached OMX tmux, rather than implying team mode by default [Task 1]
333:# Task Group: ai-writing-suite / local repo migration, layered implementation, and publish-surface review
334:scope: June 6-7 AI Writing Suite work covering the move out of the umbrella repo into a standalone local repo, Layer 0-3 implementation, isolated review, and the later Codex/Claude packaging-surface checks; use when the user resumes `ai-writing-suite` or asks how the standalone repo was supposed to proceed.
335:applies_to: cwd=/Users/surahli/Documents/ai-writing-suite with antecedent design/handoff context in /Users/surahli/Documents/Codex/2026-06-01/personal-productivity-skills; reuse_rule=safe for the standalone `ai-writing-suite` repo while the same local migration and layered implementation plan are still current, but re-check whether GitHub/PR changes have since been reconciled.
341:- extensions/chronicle/resources/2026-06-06T16-13-00-pqvH-10min-memory-summary.md (cwd=/Users/surahli/Documents/Codex/2026-06-01/personal-productivity-skills and /Users/surahli/Documents/ai-writing-suite, rollout_path=/Users/surahli/.codex/memories/extensions/chronicle/resources/2026-06-06T16-13-00-pqvH-10min-memory-summary.md, updated_at=2026-06-06T16:13:00+00:00, thread_id=None, Chronicle window showing the AI Writing Suite wrapup, PR #4 state, migration discussion, and the local-only history-preserving repo move decision)
345:- ai-writing-suite, personal-productivity-skills, independent local repo, local-only migration, preserve history, PR #4, rename-ai-writing-suite, docs/design-ai-writing-suite-v1-2026-06-06.md, docs/handover-2026-06-06-ai-writing-suite-v1.md, memory/project_ai_writing_suite.md
351:- extensions/chronicle/resources/2026-06-06T19-58-00-oHuw-10min-memory-summary.md (cwd=/Users/surahli/Documents/ai-writing-suite, rollout_path=/Users/surahli/.codex/memories/extensions/chronicle/resources/2026-06-06T19-58-00-oHuw-10min-memory-summary.md, updated_at=2026-06-06T19:58:00+00:00, thread_id=None, Chronicle window showing standalone-repo commit history, Layer 1 verification, and Layer 2 parallel executor work)
355:- /Users/surahli/Documents/ai-writing-suite, d4ed984, e1368db, 7bdf986, Layer 0, Layer 1, Layer 2, comms-polish, voice-onboard, _shared/voice-profile.md, _shared/knowledge/structure.md, _shared/self-improvement.md
357:## Task 3: choose a Python detector for Layer 3 and split the final implementation into eval, docs, and packaging lanes, outcome partial
361:- extensions/chronicle/resources/2026-06-06T20-02-00-CcyZ-10min-memory-summary.md (cwd=/Users/surahli/Documents/ai-writing-suite, rollout_path=/Users/surahli/.codex/memories/extensions/chronicle/resources/2026-06-06T20-02-00-CcyZ-10min-memory-summary.md, updated_at=2026-06-06T20:02:00+00:00, thread_id=None, Chronicle window showing Layer 1 commit `7bdf906`, KB-agent inspection, and the Layer 2 follow-up context)
362:- extensions/chronicle/resources/2026-06-06T21-01-00-tkIN-10min-memory-summary.md (cwd=/Users/surahli/Documents/ai-writing-suite, rollout_path=/Users/surahli/.codex/memories/extensions/chronicle/resources/2026-06-06T21-01-00-tkIN-10min-memory-summary.md, updated_at=2026-06-06T21:01:00+00:00, thread_id=None, Chronicle window showing the user choosing `Python detector now` and the Layer 3 split into eval/docs/packaging)
366:- 7bdf906, Layer 2, Layer 3, Python detector now, eval subsystem, docs lane, packaging lane, _shared/knowledge/audience.md, _shared/knowledge/.gitkeep, Claude Code, Ghostty
368:## Task 4: review the v1 state in isolation and flag speculative Codex plugin-manifest packaging, outcome partial
372:- extensions/chronicle/resources/2026-06-07T00-09-00-PFCN-10min-memory-summary.md (cwd=/Users/surahli/Documents/ai-writing-suite, rollout_path=/Users/surahli/.codex/memories/extensions/chronicle/resources/2026-06-07T00-09-00-PFCN-10min-memory-summary.md, updated_at=2026-06-07T00:09:00+00:00, thread_id=None, Chronicle window showing the v1 layer table, isolated code-review pass, and follow-up findings around docs/smoke/detector details)
373:- extensions/chronicle/resources/2026-06-07T00-26-00-xsag-10min-memory-summary.md (cwd=/Users/surahli/Documents/ai-writing-suite, rollout_path=/Users/surahli/.codex/memories/extensions/chronicle/resources/2026-06-07T00-26-00-xsag-10min-memory-summary.md, updated_at=2026-06-07T00:26:00+00:00, thread_id=None, Chronicle window showing `main` fast-forward to `c3f1713` and the pre-publish check that treated `packaging/codex/.codex-plugin/plugin.json` as speculative)
377:- feat/ai-writing-suite-v1, code-reviewer pass, 17/17 detector, 6/6 fixtures, AI-slop 62/100 -> 0/100, c3f1713, packaging/codex/.codex-plugin/plugin.json, SKILL.md, references/, manifest verification
379:## Task 5: catch the packaging false-ready state before publish and lock the source tree as the installable truth, outcome partial
383:- extensions/chronicle/resources/2026-06-07T16-54-00-FOWx-10min-memory-summary.md (cwd=/Users/surahli/Documents/ai-writing-suite, rollout_path=/Users/surahli/.codex/memories/extensions/chronicle/resources/2026-06-07T16-54-00-FOWx-10min-memory-summary.md, updated_at=2026-06-07T16:54:00+00:00, thread_id=None, Chronicle window showing the packaging/installability blocker, `docs/plan-publish-cleanup-test-2026-06-07.md`, and the later host-scope choices)
387:- docs/plan-publish-cleanup-test-2026-06-07.md, packaging false-ready, source tree as single source of truth, manifest-only package, plugin body missing, Claude + Codex + Cursor, cursor not found, cursor-agent not found
394:- when the user answered the Layer 3 question by choosing `Python detector now` -> default the first eval detector path to Python before widening to JS or packaging-specific variants [Task 3]
399:- The AI Writing Suite work started inside `/Users/surahli/Documents/Codex/2026-06-01/personal-productivity-skills` with PR `#4`, `docs/design-ai-writing-suite-v1-2026-06-06.md`, `docs/handover-2026-06-06-ai-writing-suite-v1.md`, `memory/project_ai_writing_suite.md`, and a repo `CLAUDE.md`; the later migration discussion treated that as antecedent context, not the final repo home [Task 1]
401:- By the later Chronicle window, the standalone repo existed at `/Users/surahli/Documents/ai-writing-suite` with visible commit sequence `d4ed984 Extract ai-writing-suite into standalone local repo`, `e1368db Layer 0: suite skeleton, thin router, consolidated pattern catalog`, and `7bdf986 Layer 1: enrich comms-polish + build voice-onboard` [Task 2]
402:- Layer 1 verification depended on one shared contract surface: `skills/ai-writing-suite/_shared/voice-profile.md` is written by `voice-onboard` and read by `comms-polish`, with graceful degradation when the profile is absent [Task 2]
403:- The next visible Layer 2 split was intentionally parallel and disjoint: one executor wrote `skills/ai-writing-suite/_shared/knowledge/structure.md` for a generic KB seed plus retrieval smoke path, and the other wrote `skills/ai-writing-suite/_shared/self-improvement.md` for a human-gated self-improvement hook [Task 2]
404:- The visible Layer 3 decision was explicit and bounded: keep the mechanical detector in Python for now, then split the final layer into `evals/`, docs/attribution surfaces, and Codex/Claude packaging lanes with separate ownership [Task 3]
406:- The pre-publish packaging check found that installed Codex skills under `~/.codex/skills/` are folders containing `SKILL.md` plus optional `references/`, without a required `plugin.json`; treat `packaging/codex/.codex-plugin/plugin.json` as speculative until host docs prove otherwise [Task 4]
407:- The later packaging recon caught a more serious publish blocker than the speculative manifest question: the remote/installable package appeared to contain only manifest files while the plugin body was missing, so the next real Step 1 was to fix install-path/package contents before publish [Task 5][chronicle memory]
408:- The locked-in host/publish direction from the later terminal pass was to use the source tree as the single source of truth and target Claude + Codex + Cursor host scope, while recording that local Cursor CLIs were absent (`cursor not found`, `cursor-agent not found`) and needed separate fact-finding rather than assumption [Task 5][chronicle memory]
415:- symptom: publish-surface scaffolding assumes Codex consumes plugin manifests the same way another host does -> cause: packaging copies a speculative `.codex-plugin/plugin.json` shape instead of checking the installed Codex skill surface first -> fix: inspect `~/.codex/skills/` and host docs before treating a manifest file as required [Task 4]
419:scope: June 7 direct-evaluation work on using Darwin 2.0 and SkillOpt against the shipped `autorefine/` bundle, including scope correction, isolated adapter-based smoke evaluation, and the decision not to apply back a shallow candidate; use when the user resumes the AutoRefine evaluation lane rather than the older `goal-forge` packaging lane.
420:applies_to: cwd=/Users/surahli/Documents/projects/skill-improvement; reuse_rule=safe for this repo's AutoRefine evaluation lane while the ask stays about direct external evaluation/improvement of the shipped bundle, but re-check whether the user still wants execution rather than design borrowing or packaging discussion.
512:# Task Group: Codex workflow / OMX auto-activation triage and imported CLAUDE.md baggage
513:scope: Codex-side diagnosis of unexpected OMX workflow activation, including local prompt-routing config, hook surfaces, and legacy `~/.claude/CLAUDE.md` imports; use when the user asks why OMX workflow blocks are appearing unexpectedly in Codex App sessions.
514:applies_to: cwd=/Users/surahli/.codex and /Users/surahli/.claude; reuse_rule=safe for this local Codex/OMX configuration lane, but re-check the current hook/config state before assuming the same activation path still applies.
520:- rollout_summaries/2026-06-06T00-26-58-1T8s-omx_disable_by_default_explicit_only_hooks.md (cwd=/Users/surahli/Documents/Codex/2026-06-05/can-we-revisit-how-omx-is, rollout_path=/Users/surahli/.codex/sessions/2026/06/05/rollout-2026-06-05T17-26-58-019e9a53-6bbc-7341-86c9-d3ab7a730f90.jsonl, updated_at=2026-06-06T00:39:41+00:00, thread_id=019e9a53-6bbc-7341-86c9-d3ab7a730f90, explicit-only hook wrapper, OMO ultrawork hook removal, and `USE_OMX_EXPLORE_CMD=0` confirmation)
529:- The visible Codex-side config surface for advisory prompt routing was `~/.codex/.omx-config.json`, and `promptRouting.triage.enabled=false` was identified as the setting relevant to disabling advisory prompt triage while preserving explicit workflow keyword use [Task 1]
531:- `~/.claude/CLAUDE.md` was explicitly surfaced as legacy Claude-side baggage that Codex was still importing, so unexpected OMX activation can come from imported bare-word workflow instructions even when local skill-active state is absent [Task 1]
538:- symptom: `codex doctor` hangs or gives no useful output during hook debugging -> cause: the Codex-side doctor path is less reliable than the OMX/user-scope hook surfaces in this environment -> fix: fall back to targeted hook tests plus `omx doctor` instead of waiting on an unresponsive doctor run [Task 1]
579:## Task 4: bound v0 to six hand-authored synthetic fixtures, research generation workflow, and use Claude outside voice to tighten the measurement plan, outcome success
583:- rollout_summaries/2026-06-06T04-24-18-oT0F-asoe_prototype_grill_fixture_research_claude_advisor.md (cwd=/Users/surahli/Documents/projects/agentic-search-online-eval, rollout_path=/Users/surahli/.codex/sessions/2026/06/05/rollout-2026-06-05T21-24-18-019e9b2c-b218-7c70-bfe5-5ffd613c1825.jsonl, updated_at=2026-06-06T21:12:25+00:00, thread_id=019e9b2c-b218-7c70-bfe5-5ffd613c1825, fixture-generation workflow research, packetized workflow verification, and Claude advisor critique)
599:- when the user asked for an `outside voice from Claude` and then wanted it actually exercised -> install/use the local Claude advisor path, not just mention it as an option [Task 4]
619:- The Claude advisor lane added two durable guards before implementation: add a blind/independent labeling step so fixture authoring and evaluator labels do not collapse into the same bias source, and add a calibration gate so synthetic cost bands stay anchored to at least one real priced/timed trace [Task 4]
631:# Task Group: Codex workflow / OpenCLI web-to-markdown setup and reusable workflow packaging
632:scope: June 6 Codex-side workflow packaging around OpenCLI/web-to-markdown setup, executing a social-post workflow instead of only documenting it, and turning repeated workflow lessons into reusable local artifacts; use when the user asks to operationalize a workflow from a post or to update Codex-local automation packaging.
633:applies_to: cwd=/Users/surahli/.codex and transient non-repo workspaces; reuse_rule=safe for local Codex/OpenCLI workflow setup and automation packaging, but re-check the current installed tool surfaces and whether the user wants documentation, execution, or both.
649:- extensions/chronicle/resources/2026-06-06T04-36-00-wBXW-10min-memory-summary.md (cwd=/Users/surahli/.codex and local workflow-packaging context, rollout_path=/Users/surahli/.codex/memories/extensions/chronicle/resources/2026-06-06T04-36-00-wBXW-10min-memory-summary.md, updated_at=2026-06-06T04:36:00+00:00, thread_id=None, Chronicle window showing `outputs/opencli-web-to-markitdown-setup.md`, the user correction that the goal was to execute not just document, and nearby workflow-packaging work)
650:- rollout_summaries/2026-06-06T04-20-44-CLnn-weekly_codex_context_review_enhancement.md (cwd=/Users/surahli/Documents/Codex/2026-06-05/use-opencli-and-web-to-markitdown, rollout_path=/Users/surahli/.codex/sessions/2026/06/05/rollout-2026-06-05T21-20-44-019e9b29-6e4c-73b2-bb95-e7b0a37cbbc5.jsonl, updated_at=2026-06-06T05:02:20+00:00, thread_id=019e9b29-6e4c-73b2-bb95-e7b0a37cbbc5, enhancement of `weekly-codex-context-review` to use `workflow-distillation` and emit one setup decision)
651:- extensions/chronicle/resources/2026-06-06T04-56-00-xlwj-10min-memory-summary.md (cwd=/Users/surahli/.codex and automation packaging context, rollout_path=/Users/surahli/.codex/memories/extensions/chronicle/resources/2026-06-06T04-56-00-xlwj-10min-memory-summary.md, updated_at=2026-06-06T04:56:00+00:00, thread_id=None, Chronicle window showing the `weekly-codex-context-review` automation update, workflow-distillation checks, and duplicate checks across skill locations)
668:- The nearby automation update treated workflow-distillation evidence checks, duplicate checks across skill locations, and OpenCLI/web-to-markdown health as recurring setup-drift evidence for `weekly-codex-context-review`, which is the right packaging direction when the same setup problem recurs [Task 2]
670:- The wider packaging context in the same window showed the user exploring reusable workflow structure in other places too, including `ai-writing-humanizer/` and a local `deep-research-tiered` workflow harness; this reinforces that local artifact packaging is a recurring preference, not a one-off trick [Task 2]
691:## Task 4: continue passive DataCamp Claude / Claude Code course browsing after the workshop, outcome success
695:- extensions/chronicle/resources/2026-06-06T00-43-00-dPpu-10min-memory-summary.md (cwd=Chrome passive learning context, rollout_path=/Users/surahli/.codex/memories/extensions/chronicle/resources/2026-06-06T00-43-00-dPpu-10min-memory-summary.md, updated_at=2026-06-06T00:43:00+00:00, thread_id=None, Chronicle window showing merged `agentic-search-online-eval` PR context plus DataCamp Claude Models / shell / Claude Code browsing)
696:- extensions/chronicle/resources/2026-06-06T00-53-00-BoUC-10min-memory-summary.md (cwd=Chrome passive learning context, rollout_path=/Users/surahli/.codex/memories/extensions/chronicle/resources/2026-06-06T00-53-00-BoUC-10min-memory-summary.md, updated_at=2026-06-06T00:53:00+00:00, thread_id=None, Chronicle window showing more DataCamp Claude Code / Claude Models exercises and agent-course searching)
698:- extensions/chronicle/resources/2026-06-06T05-06-00-fzoy-10min-memory-summary.md (cwd=Chrome passive learning context, rollout_path=/Users/surahli/.codex/memories/extensions/chronicle/resources/2026-06-06T05-06-00-fzoy-10min-memory-summary.md, updated_at=2026-06-06T05:06:00+00:00, thread_id=None, Chronicle window showing the `Software Development with Claude Code` exercises, `music-analytics-api`, `CLAUDE.md` rules, and the later `agents` chapter)
702:- DataCamp, Introduction to Claude Models, Anthropic API, Introduction to Shell, Software Development with Claude Code, music-analytics-api, CLAUDE.md, init -> Explore -> Plan -> Review -> Code -> Test, agents chapter, passive learning
704:## Task 5: continue the Claude Code course into safe refactoring, hooks, and MCP lessons, outcome success
708:- extensions/chronicle/resources/2026-06-07T00-36-00-xwjx-10min-memory-summary.md (cwd=Chrome passive learning context, rollout_path=/Users/surahli/.codex/memories/extensions/chronicle/resources/2026-06-07T00-36-00-xwjx-10min-memory-summary.md, updated_at=2026-06-07T00:36:00+00:00, thread_id=None, Chronicle window showing browser-only Claude Code coursework on safe refactoring, hooks, and MCP)
741:- The later browser-only windows reinforced that DataCamp Claude/Claude Code coursework was learning context rather than implementation: visible topics included Anthropic API basics, an intro shell course, a `Software Development with Claude Code` lesson, and an embedded `music-analytics-api` exercise about `CLAUDE.md`, architecture questions, search-endpoint tradeoffs, and the next `agents` chapter, all without local code execution on this machine [Task 4]
750:# Task Group: ds-skills-teaching / Codex tutorial packaging and Data Analytics plugin reconnaissance
751:scope: packaging a standalone `projects/codex_tutorial/` inside an existing teaching repo, preserving the review framing that the material must start from pain/workflow/artifact rather than concepts, and capturing the follow-on Codex App plugin inspection context; use when the user resumes the `Prepare Codex 101 storyline` lane or asks how the tutorial package/PRs were scoped.
752:applies_to: cwd=ds-skills-teaching / Codex tutorial packaging workflow; reuse_rule=safe for this teaching/package lane when the task is still about a self-contained project inside the existing repo, but re-check whether the ask is packaging, PR follow-through, or unrelated plugin usage.
758:- extensions/chronicle/resources/2026-06-03T02-21-00-DADY-10min-memory-summary.md (cwd=ds-skills-teaching / Codex tutorial packaging workflow, rollout_path=/Users/surahli/.codex/memories/extensions/chronicle/resources/2026-06-03T02-21-00-DADY-10min-memory-summary.md, updated_at=2026-06-03T02:21:00+00:00, thread_id=None, Chronicle window showing the finished `projects/codex_tutorial/` package, commit `33fd8c3`, branch `package-codex-tutorial`, and PR `#5`)
759:- extensions/chronicle/resources/2026-06-03T02-11-00-CsfG-10min-memory-summary.md (cwd=ds-skills-teaching / Codex tutorial packaging workflow, rollout_path=/Users/surahli/.codex/memories/extensions/chronicle/resources/2026-06-03T02-11-00-CsfG-10min-memory-summary.md, updated_at=2026-06-03T02:11:00+00:00, thread_id=None, Chronicle window showing the earlier root-landing polish, the rejected separate-repo attempt, and the initial `projects/codex_tutorial/` packaging steps)
763:- Prepare Codex 101 storyline, ds-skills-teaching, projects/codex_tutorial/, sessions/codex-onboarding/hub, outputs/codex-onboarding/07-ds-audience-review-x-style-gap.md, polish-root-landing, 1311aea, PR #4, package-codex-tutorial, 33fd8c3, PR #5, feature/initial-materials, scripts/check-links.mjs, Start with a workflow. End with a receipt.
765:## Task 2: inspect the Codex App Data Analytics plugin and `Jupyter Notebooks` skill after the package PR, outcome success
769:- extensions/chronicle/resources/2026-06-03T02-21-00-DADY-10min-memory-summary.md (cwd=ds-skills-teaching / Codex tutorial packaging workflow, rollout_path=/Users/surahli/.codex/memories/extensions/chronicle/resources/2026-06-03T02-21-00-DADY-10min-memory-summary.md, updated_at=2026-06-03T02:21:00+00:00, thread_id=None, Chronicle window showing post-PR plugin inspection in Codex App)
777:- when Codex tried to create `surahli123/codex_tutorial`, the user asked why the existing repo could not be reused and then confirmed they wanted `projects/codex_tutorial/` inside the current repo -> default packaging work toward a self-contained project folder in the existing repo before proposing a new GitHub repository [Task 1]
778:- when the user accepted the framing that this should be an `independent project folder, not a broad repo reshape` -> keep packaging slices narrow and explicit instead of turning them into general repo reorganization [Task 1]
782:- The packaging lane had two separate but related PR surfaces: root landing polish shipped as commit `1311aea` on branch `polish-root-landing` into PR `#4`, then the standalone tutorial package shipped as commit `33fd8c3` on branch `package-codex-tutorial` into PR `#5`, both against `feature/initial-materials` [Task 1]
784:- The review document `outputs/codex-onboarding/07-ds-audience-review-x-style-gap.md` stayed central to packaging decisions: the package was judged too wiki-like, and the stronger teaching direction was `one pain, one diagnosis, one workflow, one artifact` plus the hero line `Start with a workflow. End with a receipt.` [Task 1]
786:- The post-PR plugin reconnaissance established only surface facts worth remembering: the user inspected the Codex App `Data Analytics` plugin, saw category `Analytics`, developer `OpenAI`, capabilities `Interactive, Read, Write`, and opened the `Jupyter Notebooks` skill modal; the modal text itself was plugin content, not user preference or repo guidance [Task 2]
790:- symptom: the agent proposes a fresh GitHub repo for a packaging task the user meant to keep local to the current repo -> cause: `new repo` language is interpreted as a new remote repository instead of a self-contained project folder -> fix: for tutorial/package work, first test whether the user means an independent folder inside the existing repo and preserve the current repo unless they explicitly ask for a separate GitHub repo [Task 1]
856:# Task Group: Codex workflow / agent-goal-contracts packaging and CLAUDE.md resident-budget pruning
857:scope: local agent-tooling work around turning `goal-forge` into a public `agent-goal-contracts` package and reducing resident `CLAUDE.md` instruction weight with planned or in-progress file surgery; use when resuming goal-contract packaging, public skill publication, or local Claude-config budget pruning.
912:# Task Group: Codex onboarding / Codex 101 storyline and agenda-aligned package
913:scope: workshop/onboarding packaging for Codex App adoption, including agenda-aligned document bundles, skill-management split decisions, and the later narrative/visual rewrite direction; use when resuming the Codex 101 teaching lane rather than unrelated repo work.
914:applies_to: cwd=/Users/surahli/Documents/Codex/2026-06-01/i-am-going-to-host-a; reuse_rule=safe for this Codex 101/offsite lane, but re-check whether the ask is bookmark classification, agenda alignment, or the polished narrative/visual rewrite.
916:## Task 1: split the skill-management lane out of the main Codex 101 material, align outputs to the live agenda screenshot, and keep the generator rerunnable, outcome partial
920:- extensions/chronicle/resources/2026-06-02T03-57-00-bBOZ-10min-memory-summary.md (cwd=/Users/surahli/Documents/Codex/2026-06-01/i-am-going-to-host-a, rollout_path=/Users/surahli/.codex/memories/extensions/chronicle/resources/2026-06-02T03-57-00-bBOZ-10min-memory-summary.md, updated_at=2026-06-02T03:57:00+00:00, thread_id=None, Chronicle window showing the agenda screenshot alignment, deliverable bundle, and separate skill-management doc)
924:- Prepare Codex 101 storyline, outputs/codex-101-agenda-aligned-plan.md, outputs/codex-101-facilitator-runbook.md, outputs/codex-101-x-bookmarks-storyline.md, outputs/codex-101-ds-demo-prompts.md, outputs/codex-101-enterprise-safe-boundaries.md, outputs/codex-claude-skill-management-bookmarks.md, work/classify-x-bookmarks.mjs, 497 bookmarks, 143 candidates
930:- extensions/chronicle/resources/2026-06-02T05-13-00-MqlM-10min-memory-summary.md (cwd=/Users/surahli/Documents/Codex/2026-06-01/i-am-going-to-host-a, rollout_path=/Users/surahli/.codex/memories/extensions/chronicle/resources/2026-06-02T05-13-00-MqlM-10min-memory-summary.md, updated_at=2026-06-02T05:13:00+00:00, thread_id=None, Chronicle window showing `08-improvement-plan-x-style-rewrite.md`, three spawned subagents, and the narrative/receipt-driven rewrite direction)
934:- codex-onboarding/08-improvement-plan-x-style-rewrite.md, Start with a workflow. End with a receipt., outputs/codex-onboarding/02-offsite-codex-setup-daily-workflow.md, Atlassian MCP, RovoDev-to-Codex migration, three subagents, docs 09 and 10
940:- extensions/chronicle/resources/2026-06-02T14-41-00-DmPc-10min-memory-summary.md (cwd=/Users/surahli/Documents/Codex/2026-06-01/i-am-going-to-host-a, rollout_path=/Users/surahli/.codex/memories/extensions/chronicle/resources/2026-06-02T14-41-00-DmPc-10min-memory-summary.md, updated_at=2026-06-02T14:41:00+00:00, thread_id=None, Chronicle window showing `07-ds-audience-review-x-style-gap.md`, the reduced-subagent rewrite pass, and generator preservation of `09-live-demo-workflow-receipt.md`)
948:- when the user said the latest Codex/Claude Code skill-management material should stay `as a separate document` -> keep skill-management content out of the main Codex 101 live-session narrative [Task 1]
956:- The visible workshop shape was: 10 minutes tool landscape, 30 minutes Codex setup/migration from RovoDev CLI, 15 minutes workflow routing/recommendations, then a separate second session for skill sharing [Task 1]
957:- The durable framing that kept recurring was that Codex should be taught as a workspace that reads files, writes artifacts, tracks state, and verifies work, not as "just another chat" [Task 1][Task 2]
964:- symptom: the main Codex 101 storyline gets noisy and loses its teaching arc -> cause: skill-management/version-drift material stays mixed into the core workshop narrative -> fix: keep that lane in `outputs/codex-claude-skill-management-bookmarks.md` or equivalent separate artifacts [Task 1]
1045:- when the user said "create the Slice 0 example artifacts referenced in the v0 implementation plan before touching any plugin skeleton path" -> default this lane to docs/examples first and treat skeleton packaging as a later slice [Task 1]
1054:- The architect block cleared only after the docs separated Slice 0 paper examples, Slice 1 skeleton-only packaging, and Slice 2 executable wrapper validation; `sma-diagnose` is wrapper-contract territory for Slice 2, not Slice 1 [Task 2]
1066:scope: latest `SMA_v2` eval-lane work that reframed Stream-B as an offline diagnosis-vs-ground-truth set and then hardened Codex-owned C4 permission judging while avoiding Claude's slice-4 runner files; use when resuming the most recent eval lane rather than older comparison-probe or planning stages.
1079:## Task 2: read live slice-4 changes first, protect Claude-owned files, and harden C4 permission denial cases with TDD plus review-fix loops, outcome success
1101:- For the later C4 lane, `git status --short --branch`, recent `git log`, `docs/sma-rewrite-c-to-b/handoff.md`, and `notes/slice-4-scoping-and-c4-overlap.md` were enough to separate Claude's slice-4 runner/observability lane from Codex's judge lane before editing [Task 2]
1110:- symptom: Codex edits the wrong slice-4 files during a parallel session -> cause: the protected-file boundary was not re-read from live dirty state -> fix: inspect the current diff first and keep `run_plan/corpus_eval.py`, `.omc/project-memory.json`, and `runs/slice4-scorecard.html` protected unless the user reopens them [Task 2]
1177:- The current missing-source symptom was structural at first: `custom/orchestrator.py` only called autocli/native readers (`autocli_news`, `stub_news`, `x_autocli`, `polymarket`, `reddit_autocli`), and the local morning env disabled the optional autocli/news/social readers, so Codex-side AnySearch availability alone could not affect launchd output until a new adapter was wired in [Task 1]
1269:- rollout_summaries/2026-05-30T05-07-53-CPMl-wbfa_ceo_evidence_workspace_closeout_and_branch_split.md (cwd=/Users/surahli/Documents/projects/water_bottle_finance_analyzer, rollout_path=/Users/surahli/.codex/sessions/2026/05/29/rollout-2026-05-29T22-07-53-019e7748-15b6-7343-bd6a-657ee9110ad1.jsonl, updated_at=2026-05-31T06:37:20+00:00, thread_id=019e7748-15b6-7343-bd6a-657ee9110ad1, CEO grilling, evidence-workspace framing, backlog packaging, and new frontend branch)
1286:- Open Design could be launched locally by preferring the bundled Codex runtime Node at `/Users/surahli/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin`, with web port `7457` and daemon port `7456`, instead of changing the user’s Homebrew Node install [Task 1]
1291:- The prior backlog-packaging baseline for this lane is commit `2f6bc5b` on branch `codex/wbfa-frontend-evidence-flashcards`; `scripts/path_portability_check.py` can fail only on known `.codex/goals/*` artifact paths while the intended repo slice is otherwise clean [Task 3]
1298:- symptom: backlog packaging drifts into generated local state or new-branch work -> cause: old Trust Audit files and new frontend artifacts are staged together -> fix: inspect the dirty tree, exclude `.codegraph/`, and commit the bounded backlog before creating the new flashcard branch [Task 3]
1301:scope: local Codex desktop/runtime recovery work spanning SQLite lock diagnosis, thread/session repair, and sidebar/app-server cache interpretation; use when the user reports lost sessions, stale sidebar visibility, or `database is locked` startup failures under local Codex/OMX state.
1302:applies_to: cwd=/Users/surahli/Documents/Codex/* and local Codex state under /Users/surahli/.codex; reuse_rule=safe for this machine-local Codex runtime context, but treat process lists, counts, and app-server visibility as snapshot evidence that should be rechecked live.
1308:- rollout_summaries/2026-05-21T17-21-21-e6EH-codex_omx_database_locked_live_process_contention.md (cwd=/Users/surahli/Documents/Codex/2026-05-21/help-me-fix-this-issue-when, rollout_path=/Users/surahli/.codex/sessions/2026/05/21/rollout-2026-05-21T10-21-21-019e4b8e-5add-76e2-8692-ba49dd440533.jsonl, updated_at=2026-05-21T17:32:10+00:00, thread_id=019e4b8e-5add-76e2-8692-ba49dd440533, live contention diagnosis and stop-on-recovery rule)
1316:- when the user asked to fix a local Codex startup failure with `database is locked` -> inspect live processes and file holders first instead of guessing at config or deleting state files [Task 1]
1325:- symptom: Codex/OMX startup throws `error returned from database: (code: 5) database is locked` -> cause: multiple live Codex processes are holding the runtime SQLite files open -> fix: inspect `lsof`, `tmux list-sessions`, and live `codex|omx` processes, then close competing sessions instead of deleting `-wal` or `-shm` files [Task 1]
1328:scope: read-only Codex/OMX/OpenCLI setup audits that inventory config, MCP servers, skills, automations, and health-check warnings without changing local setup; use when the user wants a local environment health report rather than repair work.
1329:applies_to: cwd=/Users/surahli/Documents/Codex/* and local Codex tooling under /Users/surahli/.codex; reuse_rule=safe for this machine-local audit workflow, but treat warnings as snapshot findings and keep suggested fixes approval-gated unless the user explicitly reopens setup changes.
1331:## Task 1: run a read-only Codex setup drift audit and separate facts from suggested next actions, outcome success
1335:- rollout_summaries/2026-06-01T20-01-45-FA4R-codex_setup_drift_audit_readonly_health_check.md (cwd=/Users/surahli/Documents/Codex/2026-05-27/use-opencli-or-web-to-markdown, rollout_path=/Users/surahli/.codex/sessions/2026/06/01/rollout-2026-06-01T13-01-45-019e84c7-29f0-7352-9436-9ad7f65110e5.jsonl, updated_at=2026-06-01T20:03:35+00:00, thread_id=019e84c7-29f0-7352-9436-9ad7f65110e5, audit.py run, health-command verification, and automation-memory update)
1343:- when the user said `Run a read-only local Codex setup drift audit` and `Do not install, delete, rewrite config, change automations, or modify global defaults` -> keep these audits non-destructive and reporting-only [Task 1]
1363:## Task 1: close the finished ultragoal locally, write exact handoff artifacts, and route the next evidence-bridge slice to a regular Codex App session, outcome success
1368:- rollout_summaries/2026-05-30T03-12-21-bfVS-sma_evidence_bridge_handoff_and_session_wrapup_skill_update.md (cwd=/Users/surahli/Documents/projects/SMA_v2, rollout_path=/Users/surahli/.codex/sessions/2026/05/29/rollout-2026-05-29T20-12-21-019e76de-4fe4-7fe1-b8e6-3f17a86183d8.jsonl, updated_at=2026-05-30T03:28:25+00:00, thread_id=019e76de-4fe4-7fe1-b8e6-3f17a86183d8, exact handoff-file rule, branch-action rule, and regular-Codex-App routing)
1372:- omx ultragoal complete-goals, get_goal, 0c60f7f, 81700e4, docs/handover-2026-05-29-sma-rewrite-evidence-bridge-next.md, exact handoff file, branch action, regular Codex App, not OMX
1402:- when the user asked whether to use `regular codex app or OMX` for the next narrow evidence-bridge slice -> choose the execution surface explicitly; default this kind of local evidence slice to regular Codex App solo mode unless runtime/team value is concrete [Task 1]
1430:- rollout_summaries/2026-05-30T03-49-03-JkMm-ai_trade_agent_morning_digest_launchd_codex_health_check.md (cwd=/Users/surahli/Documents/projects/ai-trade-agent, rollout_path=/Users/surahli/.codex/sessions/2026/05/29/rollout-2026-05-29T20-49-03-019e76ff-ea9c-7c42-8b2c-23f1178b0f3e.jsonl, updated_at=2026-05-30T04:12:17+00:00, thread_id=019e76ff-ea9c-7c42-8b2c-23f1178b0f3e, launchd/live log verification and read-only Codex automation creation)
1451:- when the user says `Do not send Telegram, do not edit files, do not modify launchd, pmset, crontab, git state, or Codex automations` -> keep health checks strictly read-only and observational [Task 1]
1621:- `AGENTS.md` in this repo keeps learnings newest-first under `## Codex Learnings (Newest First)`, so validated additions should be prepended instead of scattering edits through unrelated governance sections [Task 2]
1796:- `omx ultragoal create-goals --brief-file ...` updates Ultragoal ledger/state files; it does not create a new Codex chat on its own. Relevant state surfaces include `.omx/ultragoal/goals.json`, `.omx/ultragoal/ledger.jsonl`, and snapshot evidence like `get-goal-null-20260529.json` when reconciliation is confused [Task 3]
1923:- The first Codex-worker launch path was unstable; the working recovery was `omx team status` + Claude-worker fallback + manual task reassignment correction instead of assuming the first pane startup actually executed [Task 6]
1932:- symptom: OMX worker panes exist but the prompts do not reliably execute -> cause: the initial Codex-worker launch path was unstable -> fix: verify through `omx team status`, use the supported Claude-worker fallback, and correct assignment drift explicitly rather than trusting pane presence [Task 6]
2189:# Task Group: Codex workflow / goal-spec contracts, environment hygiene, and provider boundaries
2190:scope: repeatable Codex/OMX operating defaults that are still supported by ad-hoc notes: goal/spec contract shape, cleanup safety, and provider boundaries; use when future agents need cross-repo operating defaults rather than repo-local implementation detail.
2191:applies_to: cwd=/Users/surahli/.codex/memories and related local Codex homes, plus repo-specific notes for KDD and lumina; reuse_rule=safe for personal workflow defaults and local environment hygiene, but repo-specific provider contracts must stay scoped to their named repos.
2240:- symptom: `keep-codex-fast` refuses `--apply` even though the real Codex app is closed -> cause: `notify-dispatcher.js` processes carried historical `app-server` text and looked like blockers -> fix: confirm no real app-server remains, terminate only the notification helpers, then run the cleanup script path directly [Task 2]
2286:- rollout_summaries/2026-05-23T06-56-55-yYg4-lumina_pr_stack_runtime_safety_handover.md (cwd=/Users/surahli/Documents/projects/lumina-v6-rollback-inherit, rollout_path=/Users/surahli/.codex/sessions/2026/05/22/rollout-2026-05-22T20-56-55-019e539f-63fa-78d2-81eb-20a7fc634fa4.jsonl, updated_at=2026-05-23T07:48:39+00:00, thread_id=019e539f-63fa-78d2-81eb-20a7fc634fa4, stacked PR packaging and repo-visible handover expectations)

hook: PostToolUse
 succeeded in 944ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
## feat/make-v1-installable-3hosts
?? docs/handover-2026-06-02-personal-productivity-skills-next.md
?? docs/handover-2026-06-06-ai-writing-suite-v1.md
?? docs/handover-2026-06-06-v1-shipped.md
?? docs/plan-publish-cleanup-test-2026-06-07.md
?? docs/session-closeout-2026-06-02-ai-writing-humanizer.md
?? reviews/
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
41333e9
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
ancestor_status=0

hook: PostToolUse Completed
hook: PostToolUse Completed
hook: PostToolUse Completed
codex
I’m using the `code-review` skill because this is an explicit adversarial review. I’ll run two independent review lanes, then synthesize only findings that survive direct repo evidence.
hook: PreToolUse
hook: PreToolUse Completed
collab: SpawnAgent
hook: PostToolUse
2026-06-07T20:58:23.341244Z ERROR rmcp::transport::worker: worker quit with fatal: Transport channel closed, when AuthRequired(AuthRequiredError { www_authenticate_header: "Bearer realm=\"OAuth\", resource_metadata=\"https://mcp.cloudflare.com/.well-known/oauth-protected-resource/mcp\", error=\"invalid_token\"" })
hook: PostToolUse Completed
hook: PreToolUse
hook: PreToolUse Completed
collab: SpawnAgent
2026-06-07T20:58:39.183407Z ERROR rmcp::transport::worker: worker quit with fatal: Transport channel closed, when AuthRequired(AuthRequiredError { www_authenticate_header: "Bearer realm=\"OAuth\", resource_metadata=\"https://mcp.cloudflare.com/.well-known/oauth-protected-resource/mcp\", error=\"invalid_token\"" })
hook: PostToolUse
hook: PostToolUse Completed
codex
Target result: a merge-readiness review of the final source-pointing layout, not a re-litigation of the old committed-body approach. I’m checking the diff, manifests, and docs first, then I’ll pressure-test the portability assumptions.
hook: PreToolUse
hook: PreToolUse
hook: PreToolUse
hook: PreToolUse Completed
hook: PreToolUse Completed
hook: PreToolUse Completed
exec
/bin/zsh -lc 'git diff --stat main..HEAD && git diff --name-status main..HEAD' in /Users/surahli/Documents/ai-writing-suite
exec
/bin/zsh -lc "find . -maxdepth 4 -type f | sort | sed 's#"'^./##'"'" in /Users/surahli/Documents/ai-writing-suite
exec
/bin/zsh -lc "rg -n \"packaging/|sync\\.sh|packaging|sparse|marketplace|\\.agents/plugins|\\.claude-plugin|\\.codex-plugin|plugin install|plugin add|skills/ai-writing-suite\" ." in /Users/surahli/Documents/ai-writing-suite
hook: PostToolUse
hook: PostToolUse
hook: PostToolUse
 succeeded in 586ms:
./reviews/2026-06-07-rereview-final.md:16:This is a REVISION. An earlier commit took a "commit the Codex plugin body" approach; a prior review flagged that Claude then shipped a nested duplicate of the suite. THIS final commit resolves that by switching to **source-pointing**: both Claude and Codex install directly from the single source tree `skills/ai-writing-suite/` via repo-root marketplace manifests, and the entire generate-and-sync packaging (packaging/ + sync.sh + the committed body + the drift guardrail) was DELETED.
./reviews/2026-06-07-rereview-final.md:19: - Repo-root `.claude-plugin/marketplace.json` → plugin source `./skills/ai-writing-suite`
./reviews/2026-06-07-rereview-final.md:20: - Repo-root `.agents/plugins/marketplace.json` (Codex) → plugin source {source:local, path:./skills/ai-writing-suite}
./reviews/2026-06-07-rereview-final.md:21: - In-source `skills/ai-writing-suite/.claude-plugin/plugin.json` and `skills/ai-writing-suite/.codex-plugin/plugin.json`
./reviews/2026-06-07-rereview-final.md:22: - `.gitignore` simplified (packaging carve-outs removed)
./reviews/2026-06-07-rereview-final.md:23: - README per-host install (Claude/Codex no --sparse; Cursor copy), `docs/packaging.md` maintainer note
./reviews/2026-06-07-rereview-final.md:24: - `packaging/` and `sync.sh` removed entirely
./reviews/2026-06-07-rereview-final.md:26:Already verified by me (local CLIs): Claude `plugin install` discovers 4 skills; Codex installs from the root marketplace resolving to the source tree; tests 23/23 + smoke 3/3 + fixtures 8/8.
./reviews/2026-06-07-rereview-final.md:29: 1. Does removing packaging/ + sync.sh introduce any new problem (dangling references in docs/manifests, broken links, lost capability)? grep the repo for stale `packaging/` or `sync.sh` references.
./reviews/2026-06-07-rereview-final.md:30: 2. Is the Codex root `.agents/plugins/marketplace.json` with a non-`plugins/`-relative source path (`./skills/ai-writing-suite`) robust/portable, or did my local smoke pass by luck? Any resolution risk on a fresh GitHub clone vs my local path test?
./reviews/2026-06-07-rereview-final.md:31: 3. Two manifests now live INSIDE the published source tree (.claude-plugin, .codex-plugin) and the tree also ships evals/ to consumers — any real problem (double-discovery, foreign-manifest confusion, bloat)?
./reviews/2026-06-07-rereview-final.md:32: 4. README/docs correctness: are the install commands right for the new layout (no --sparse for Codex; root marketplace for both)?
./reviews/2026-06-07-rereview-final.md:67:/bin/zsh -lc "rg -n \"ai-writing-suite|packaging|sync\\.sh|marketplace|Codex|Claude\" /Users/surahli/.codex/memories/MEMORY.md" in /Users/surahli/Documents/ai-writing-suite
./reviews/2026-06-07-rereview-final.md:293:39:- when the user objected that Goal Forge had confused the `whole goal` with the `immediate restarted session` -> future goal packaging must separate program scope from current phase/session execution budget explicitly [Task 2][Task 3]
./reviews/2026-06-07-rereview-final.md:300:334:scope: June 6-7 AI Writing Suite work covering the move out of the umbrella repo into a standalone local repo, Layer 0-3 implementation, isolated review, and the later Codex/Claude packaging-surface checks; use when the user resumes `ai-writing-suite` or asks how the standalone repo was supposed to proceed.
./reviews/2026-06-07-rereview-final.md:306:357:## Task 3: choose a Python detector for Layer 3 and split the final implementation into eval, docs, and packaging lanes, outcome partial
./reviews/2026-06-07-rereview-final.md:308:362:- extensions/chronicle/resources/2026-06-06T21-01-00-tkIN-10min-memory-summary.md (cwd=/Users/surahli/Documents/ai-writing-suite, rollout_path=/Users/surahli/.codex/memories/extensions/chronicle/resources/2026-06-06T21-01-00-tkIN-10min-memory-summary.md, updated_at=2026-06-06T21:01:00+00:00, thread_id=None, Chronicle window showing the user choosing `Python detector now` and the Layer 3 split into eval/docs/packaging)
./reviews/2026-06-07-rereview-final.md:309:366:- 7bdf906, Layer 2, Layer 3, Python detector now, eval subsystem, docs lane, packaging lane, _shared/knowledge/audience.md, _shared/knowledge/.gitkeep, Claude Code, Ghostty
./reviews/2026-06-07-rereview-final.md:310:368:## Task 4: review the v1 state in isolation and flag speculative Codex plugin-manifest packaging, outcome partial
./reviews/2026-06-07-rereview-final.md:312:373:- extensions/chronicle/resources/2026-06-07T00-26-00-xsag-10min-memory-summary.md (cwd=/Users/surahli/Documents/ai-writing-suite, rollout_path=/Users/surahli/.codex/memories/extensions/chronicle/resources/2026-06-07T00-26-00-xsag-10min-memory-summary.md, updated_at=2026-06-07T00:26:00+00:00, thread_id=None, Chronicle window showing `main` fast-forward to `c3f1713` and the pre-publish check that treated `packaging/codex/.codex-plugin/plugin.json` as speculative)
./reviews/2026-06-07-rereview-final.md:313:377:- feat/ai-writing-suite-v1, code-reviewer pass, 17/17 detector, 6/6 fixtures, AI-slop 62/100 -> 0/100, c3f1713, packaging/codex/.codex-plugin/plugin.json, SKILL.md, references/, manifest verification
./reviews/2026-06-07-rereview-final.md:314:379:## Task 5: catch the packaging false-ready state before publish and lock the source tree as the installable truth, outcome partial
./reviews/2026-06-07-rereview-final.md:315:383:- extensions/chronicle/resources/2026-06-07T16-54-00-FOWx-10min-memory-summary.md (cwd=/Users/surahli/Documents/ai-writing-suite, rollout_path=/Users/surahli/.codex/memories/extensions/chronicle/resources/2026-06-07T16-54-00-FOWx-10min-memory-summary.md, updated_at=2026-06-07T16:54:00+00:00, thread_id=None, Chronicle window showing the packaging/installability blocker, `docs/plan-publish-cleanup-test-2026-06-07.md`, and the later host-scope choices)
./reviews/2026-06-07-rereview-final.md:316:387:- docs/plan-publish-cleanup-test-2026-06-07.md, packaging false-ready, source tree as single source of truth, manifest-only package, plugin body missing, Claude + Codex + Cursor, cursor not found, cursor-agent not found
./reviews/2026-06-07-rereview-final.md:317:394:- when the user answered the Layer 3 question by choosing `Python detector now` -> default the first eval detector path to Python before widening to JS or packaging-specific variants [Task 3]
./reviews/2026-06-07-rereview-final.md:320:402:- Layer 1 verification depended on one shared contract surface: `skills/ai-writing-suite/_shared/voice-profile.md` is written by `voice-onboard` and read by `comms-polish`, with graceful degradation when the profile is absent [Task 2]
./reviews/2026-06-07-rereview-final.md:321:403:- The next visible Layer 2 split was intentionally parallel and disjoint: one executor wrote `skills/ai-writing-suite/_shared/knowledge/structure.md` for a generic KB seed plus retrieval smoke path, and the other wrote `skills/ai-writing-suite/_shared/self-improvement.md` for a human-gated self-improvement hook [Task 2]
./reviews/2026-06-07-rereview-final.md:322:404:- The visible Layer 3 decision was explicit and bounded: keep the mechanical detector in Python for now, then split the final layer into `evals/`, docs/attribution surfaces, and Codex/Claude packaging lanes with separate ownership [Task 3]
./reviews/2026-06-07-rereview-final.md:323:406:- The pre-publish packaging check found that installed Codex skills under `~/.codex/skills/` are folders containing `SKILL.md` plus optional `references/`, without a required `plugin.json`; treat `packaging/codex/.codex-plugin/plugin.json` as speculative until host docs prove otherwise [Task 4]
./reviews/2026-06-07-rereview-final.md:324:407:- The later packaging recon caught a more serious publish blocker than the speculative manifest question: the remote/installable package appeared to contain only manifest files while the plugin body was missing, so the next real Step 1 was to fix install-path/package contents before publish [Task 5][chronicle memory]
./reviews/2026-06-07-rereview-final.md:326:415:- symptom: publish-surface scaffolding assumes Codex consumes plugin manifests the same way another host does -> cause: packaging copies a speculative `.codex-plugin/plugin.json` shape instead of checking the installed Codex skill surface first -> fix: inspect `~/.codex/skills/` and host docs before treating a manifest file as required [Task 4]
./reviews/2026-06-07-rereview-final.md:327:419:scope: June 7 direct-evaluation work on using Darwin 2.0 and SkillOpt against the shipped `autorefine/` bundle, including scope correction, isolated adapter-based smoke evaluation, and the decision not to apply back a shallow candidate; use when the user resumes the AutoRefine evaluation lane rather than the older `goal-forge` packaging lane.
./reviews/2026-06-07-rereview-final.md:328:420:applies_to: cwd=/Users/surahli/Documents/projects/skill-improvement; reuse_rule=safe for this repo's AutoRefine evaluation lane while the ask stays about direct external evaluation/improvement of the shipped bundle, but re-check whether the user still wants execution rather than design borrowing or packaging discussion.
./reviews/2026-06-07-rereview-final.md:340:631:# Task Group: Codex workflow / OpenCLI web-to-markdown setup and reusable workflow packaging
./reviews/2026-06-07-rereview-final.md:341:632:scope: June 6 Codex-side workflow packaging around OpenCLI/web-to-markdown setup, executing a social-post workflow instead of only documenting it, and turning repeated workflow lessons into reusable local artifacts; use when the user asks to operationalize a workflow from a post or to update Codex-local automation packaging.
./reviews/2026-06-07-rereview-final.md:342:633:applies_to: cwd=/Users/surahli/.codex and transient non-repo workspaces; reuse_rule=safe for local Codex/OpenCLI workflow setup and automation packaging, but re-check the current installed tool surfaces and whether the user wants documentation, execution, or both.
./reviews/2026-06-07-rereview-final.md:343:649:- extensions/chronicle/resources/2026-06-06T04-36-00-wBXW-10min-memory-summary.md (cwd=/Users/surahli/.codex and local workflow-packaging context, rollout_path=/Users/surahli/.codex/memories/extensions/chronicle/resources/2026-06-06T04-36-00-wBXW-10min-memory-summary.md, updated_at=2026-06-06T04:36:00+00:00, thread_id=None, Chronicle window showing `outputs/opencli-web-to-markitdown-setup.md`, the user correction that the goal was to execute not just document, and nearby workflow-packaging work)
./reviews/2026-06-07-rereview-final.md:345:651:- extensions/chronicle/resources/2026-06-06T04-56-00-xlwj-10min-memory-summary.md (cwd=/Users/surahli/.codex and automation packaging context, rollout_path=/Users/surahli/.codex/memories/extensions/chronicle/resources/2026-06-06T04-56-00-xlwj-10min-memory-summary.md, updated_at=2026-06-06T04:56:00+00:00, thread_id=None, Chronicle window showing the `weekly-codex-context-review` automation update, workflow-distillation checks, and duplicate checks across skill locations)
./reviews/2026-06-07-rereview-final.md:346:668:- The nearby automation update treated workflow-distillation evidence checks, duplicate checks across skill locations, and OpenCLI/web-to-markdown health as recurring setup-drift evidence for `weekly-codex-context-review`, which is the right packaging direction when the same setup problem recurs [Task 2]
./reviews/2026-06-07-rereview-final.md:347:670:- The wider packaging context in the same window showed the user exploring reusable workflow structure in other places too, including `ai-writing-humanizer/` and a local `deep-research-tiered` workflow harness; this reinforces that local artifact packaging is a recurring preference, not a one-off trick [Task 2]
./reviews/2026-06-07-rereview-final.md:356:750:# Task Group: ds-skills-teaching / Codex tutorial packaging and Data Analytics plugin reconnaissance
./reviews/2026-06-07-rereview-final.md:357:751:scope: packaging a standalone `projects/codex_tutorial/` inside an existing teaching repo, preserving the review framing that the material must start from pain/workflow/artifact rather than concepts, and capturing the follow-on Codex App plugin inspection context; use when the user resumes the `Prepare Codex 101 storyline` lane or asks how the tutorial package/PRs were scoped.
./reviews/2026-06-07-rereview-final.md:358:752:applies_to: cwd=ds-skills-teaching / Codex tutorial packaging workflow; reuse_rule=safe for this teaching/package lane when the task is still about a self-contained project inside the existing repo, but re-check whether the ask is packaging, PR follow-through, or unrelated plugin usage.
./reviews/2026-06-07-rereview-final.md:359:758:- extensions/chronicle/resources/2026-06-03T02-21-00-DADY-10min-memory-summary.md (cwd=ds-skills-teaching / Codex tutorial packaging workflow, rollout_path=/Users/surahli/.codex/memories/extensions/chronicle/resources/2026-06-03T02-21-00-DADY-10min-memory-summary.md, updated_at=2026-06-03T02:21:00+00:00, thread_id=None, Chronicle window showing the finished `projects/codex_tutorial/` package, commit `33fd8c3`, branch `package-codex-tutorial`, and PR `#5`)
./reviews/2026-06-07-rereview-final.md:360:759:- extensions/chronicle/resources/2026-06-03T02-11-00-CsfG-10min-memory-summary.md (cwd=ds-skills-teaching / Codex tutorial packaging workflow, rollout_path=/Users/surahli/.codex/memories/extensions/chronicle/resources/2026-06-03T02-11-00-CsfG-10min-memory-summary.md, updated_at=2026-06-03T02:11:00+00:00, thread_id=None, Chronicle window showing the earlier root-landing polish, the rejected separate-repo attempt, and the initial `projects/codex_tutorial/` packaging steps)
./reviews/2026-06-07-rereview-final.md:363:769:- extensions/chronicle/resources/2026-06-03T02-21-00-DADY-10min-memory-summary.md (cwd=ds-skills-teaching / Codex tutorial packaging workflow, rollout_path=/Users/surahli/.codex/memories/extensions/chronicle/resources/2026-06-03T02-21-00-DADY-10min-memory-summary.md, updated_at=2026-06-03T02:21:00+00:00, thread_id=None, Chronicle window showing post-PR plugin inspection in Codex App)
./reviews/2026-06-07-rereview-final.md:364:777:- when Codex tried to create `surahli123/codex_tutorial`, the user asked why the existing repo could not be reused and then confirmed they wanted `projects/codex_tutorial/` inside the current repo -> default packaging work toward a self-contained project folder in the existing repo before proposing a new GitHub repository [Task 1]
./reviews/2026-06-07-rereview-final.md:365:778:- when the user accepted the framing that this should be an `independent project folder, not a broad repo reshape` -> keep packaging slices narrow and explicit instead of turning them into general repo reorganization [Task 1]
./reviews/2026-06-07-rereview-final.md:366:782:- The packaging lane had two separate but related PR surfaces: root landing polish shipped as commit `1311aea` on branch `polish-root-landing` into PR `#4`, then the standalone tutorial package shipped as commit `33fd8c3` on branch `package-codex-tutorial` into PR `#5`, both against `feature/initial-materials` [Task 1]
./reviews/2026-06-07-rereview-final.md:367:784:- The review document `outputs/codex-onboarding/07-ds-audience-review-x-style-gap.md` stayed central to packaging decisions: the package was judged too wiki-like, and the stronger teaching direction was `one pain, one diagnosis, one workflow, one artifact` plus the hero line `Start with a workflow. End with a receipt.` [Task 1]
./reviews/2026-06-07-rereview-final.md:369:790:- symptom: the agent proposes a fresh GitHub repo for a packaging task the user meant to keep local to the current repo -> cause: `new repo` language is interpreted as a new remote repository instead of a self-contained project folder -> fix: for tutorial/package work, first test whether the user means an independent folder inside the existing repo and preserve the current repo unless they explicitly ask for a separate GitHub repo [Task 1]
./reviews/2026-06-07-rereview-final.md:370:856:# Task Group: Codex workflow / agent-goal-contracts packaging and CLAUDE.md resident-budget pruning
./reviews/2026-06-07-rereview-final.md:371:857:scope: local agent-tooling work around turning `goal-forge` into a public `agent-goal-contracts` package and reducing resident `CLAUDE.md` instruction weight with planned or in-progress file surgery; use when resuming goal-contract packaging, public skill publication, or local Claude-config budget pruning.
./reviews/2026-06-07-rereview-final.md:373:913:scope: workshop/onboarding packaging for Codex App adoption, including agenda-aligned document bundles, skill-management split decisions, and the later narrative/visual rewrite direction; use when resuming the Codex 101 teaching lane rather than unrelated repo work.
./reviews/2026-06-07-rereview-final.md:385:1045:- when the user said "create the Slice 0 example artifacts referenced in the v0 implementation plan before touching any plugin skeleton path" -> default this lane to docs/examples first and treat skeleton packaging as a later slice [Task 1]
./reviews/2026-06-07-rereview-final.md:386:1054:- The architect block cleared only after the docs separated Slice 0 paper examples, Slice 1 skeleton-only packaging, and Slice 2 executable wrapper validation; `sma-diagnose` is wrapper-contract territory for Slice 2, not Slice 1 [Task 2]
./reviews/2026-06-07-rereview-final.md:392:1269:- rollout_summaries/2026-05-30T05-07-53-CPMl-wbfa_ceo_evidence_workspace_closeout_and_branch_split.md (cwd=/Users/surahli/Documents/projects/water_bottle_finance_analyzer, rollout_path=/Users/surahli/.codex/sessions/2026/05/29/rollout-2026-05-29T22-07-53-019e7748-15b6-7343-bd6a-657ee9110ad1.jsonl, updated_at=2026-05-31T06:37:20+00:00, thread_id=019e7748-15b6-7343-bd6a-657ee9110ad1, CEO grilling, evidence-workspace framing, backlog packaging, and new frontend branch)
./reviews/2026-06-07-rereview-final.md:394:1291:- The prior backlog-packaging baseline for this lane is commit `2f6bc5b` on branch `codex/wbfa-frontend-evidence-flashcards`; `scripts/path_portability_check.py` can fail only on known `.codex/goals/*` artifact paths while the intended repo slice is otherwise clean [Task 3]
./reviews/2026-06-07-rereview-final.md:395:1298:- symptom: backlog packaging drifts into generated local state or new-branch work -> cause: old Trust Audit files and new frontend artifacts are staged together -> fix: inspect the dirty tree, exclude `.codegraph/`, and commit the bounded backlog before creating the new flashcard branch [Task 3]
./reviews/2026-06-07-rereview-final.md:420:2286:- rollout_summaries/2026-05-23T06-56-55-yYg4-lumina_pr_stack_runtime_safety_handover.md (cwd=/Users/surahli/Documents/projects/lumina-v6-rollback-inherit, rollout_path=/Users/surahli/.codex/sessions/2026/05/22/rollout-2026-05-22T20-56-55-019e539f-63fa-78d2-81eb-20a7fc634fa4.jsonl, updated_at=2026-05-23T07:48:39+00:00, thread_id=019e539f-63fa-78d2-81eb-20a7fc634fa4, stacked PR packaging and repo-visible handover expectations)
./reviews/2026-06-07-rereview-final.md:467:/bin/zsh -lc "rg -n \"packaging/|sync\\.sh|packaging|sparse|marketplace|\\.agents/plugins|\\.claude-plugin|\\.codex-plugin|plugin install|plugin add|skills/ai-writing-suite\" ." in /Users/surahli/Documents/ai-writing-suite
./skills/ai-writing-suite/NOTICE.md:27:**Contribution:** Programmatic JavaScript detector with test suite, tiered AI-vocabulary taxonomy (Tier 1/2/3 classification), CATEGORIES taxonomy for AI-writing patterns, multi-surface packaging patterns (Claude plugin, Cursor `.mdc` format), and sync tooling scaffold.
./skills/ai-writing-suite/NOTICE.md:29:**Used in:** AI-tell pattern catalog (lexical tells, significance attribution, structural patterns), the Python detector port shipped in v1 (`evals/detector/`), packaging and sync conventions.
./skills/ai-writing-suite/NOTICE.md:55:**Used in:** AI-tell pattern catalog (rhythm, stylometry, structural tells), `comms-polish` scoring and review rubric, Codex packaging conventions.
./README.md:34:One source of truth (`skills/ai-writing-suite/`) published to three hosts.
./README.md:39:claude plugin marketplace add surahli123/ai-writing-suite
./README.md:40:claude plugin install ai-writing-suite@ai-writing-suite
./README.md:49:codex plugin marketplace add surahli123/ai-writing-suite
./README.md:50:codex plugin add ai-writing-suite@ai-writing-suite
./README.md:53:Codex resolves the plugin from the same source tree — no `--sparse` needed; the Codex
./README.md:54:marketplace manifest sits at the repo root (`.agents/plugins/marketplace.json`).
./README.md:58:Cursor reads Anthropic-format **Agent Skills** from `.cursor/skills/` — there is no marketplace, so
./README.md:63:cp -R ai-writing-suite/skills/ai-writing-suite ~/.cursor/skills/ai-writing-suite
./README.md:72:.claude-plugin/marketplace.json    # Claude marketplace  → points at the source tree
./README.md:73:.agents/plugins/marketplace.json   # Codex marketplace   → points at the source tree
./README.md:78:    .claude-plugin/plugin.json     # Claude plugin manifest
./README.md:79:    .codex-plugin/plugin.json      # Codex plugin manifest
./README.md:84:docs/                              # design docs, handovers, plans, packaging  (* = v2 stub)
./README.md:90:preserved and credited in [`skills/ai-writing-suite/NOTICE.md`](skills/ai-writing-suite/NOTICE.md).
./reviews/2026-06-07-adversarial-synthesis.md:14:- Codex found no path/resolution bug. Confirmed the Claude marketplace `source: "./skills/ai-writing-suite"`
./reviews/2026-06-07-adversarial-synthesis.md:21:- **What:** Claude's plugin = the whole `skills/ai-writing-suite/` tree. We committed the Codex body at
./reviews/2026-06-07-adversarial-synthesis.md:22:  `skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/`, so Claude consumers receive a
./reviews/2026-06-07-adversarial-synthesis.md:23:  **full second copy of the suite (~33 files)** nested inside the plugin's `packaging/` dir.
./reviews/2026-06-07-adversarial-synthesis.md:27:  `evals/` + `packaging/` bloat already accepted under the Option-A "ship the source tree" choice.
./reviews/2026-06-07-adversarial-synthesis.md:28:- **Disk-arbitration:** `git ls-files skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/skills`
./reviews/2026-06-07-adversarial-synthesis.md:30:- **Options:** (a) **accept for v1** + a v2 follow-up to de-nest `packaging/` out of the published plugin
./reviews/2026-06-07-adversarial-synthesis.md:31:  dir; (b) restructure now (relocate Codex packaging to repo root, change the Codex `--sparse` path,
./reviews/2026-06-07-adversarial-synthesis.md:42:   re-runs `claude plugin update` / `marketplace update`. v1 is `1.0.0`; the packaging README documents
./skills/ai-writing-suite/README.md:145:cp -r skills/ai-writing-suite ~/.claude/skills/ai-writing-suite
./skills/ai-writing-suite/README.md:154:cp -r skills/ai-writing-suite ~/.codex/skills/ai-writing-suite
./skills/ai-writing-suite/README.md:161:See `packaging/` for surface-specific installation instructions (coming in v2).
./skills/ai-writing-suite/README.md:214:2. **conorbronsdon/avoid-ai-writing** — JS detector, CATEGORIES taxonomy, packaging patterns.
./docs/handover-2026-06-06-v1-shipped.md:13:independent Opus code review (fixed all findings), verified both Claude + Codex packaging against
./docs/handover-2026-06-06-v1-shipped.md:18:- **v1 suite** under `skills/ai-writing-suite/`: thin router + `comms-polish` (enriched) +
./docs/handover-2026-06-06-v1-shipped.md:20:  human-gated self-improvement + Python detector/eval harness + Claude & Codex packaging.
./docs/handover-2026-06-06-v1-shipped.md:26:  conformant marketplace layout (`.agents/plugins/marketplace.json` + `plugins/ai-writing-suite/`)
./docs/handover-2026-06-06-v1-shipped.md:27:  and live-verified via `codex plugin marketplace add` (then removed — config restored).
./docs/handover-2026-06-06-v1-shipped.md:32:1. **(optional) Publish to a marketplace** — manifests validate; would need a marketplace listing
./docs/handover-2026-06-06-v1-shipped.md:33:   (Claude: `claude plugin tag` to release-tag; Codex: host the marketplace dir).
./docs/handover-2026-06-06-v1-shipped.md:38:   packaging, Confluence ingestion, CJK detector scoring.
./docs/handover-2026-06-06-v1-shipped.md:46:- **Packaging is generated**: `packaging/{claude,codex}/` content is gitignored; only the
./docs/handover-2026-06-06-v1-shipped.md:47:  hand-maintained manifests are tracked. Regenerate with `bash skills/ai-writing-suite/packaging/sync.sh`.
./docs/handover-2026-06-06-v1-shipped.md:48:  Never hand-edit generated package content — edit the source under `skills/ai-writing-suite/`.
./docs/handover-2026-06-06-v1-shipped.md:54:  `claude plugin tag --dry-run`. Codex is marketplace-based (`codex plugin marketplace add/remove`).
./docs/handover-2026-06-06-v1-shipped.md:60:- `skills/ai-writing-suite/SKILL.md` — the router (entry point).
./docs/handover-2026-06-06-v1-shipped.md:61:- `skills/ai-writing-suite/packaging/README.md` — verified Claude + Codex packaging specs.
./docs/handover-2026-06-06-v1-shipped.md:62:- `skills/ai-writing-suite/evals/README.md` — how to run the detector + fixtures + smoke test.
./docs/handover-2026-06-06-v1-shipped.md:69:> published; Claude + Codex packaging are live-verified. Read `docs/handover-2026-06-06-v1-shipped.md`
./docs/handover-2026-06-06-v1-shipped.md:71:> ff-merge. I want to work on: <PICK — marketplace publish / umbrella cleanup / v2 (comms-qa RAG,
./docs/handover-2026-06-06-v1-shipped.md:72:> comms-draft, Cursor+RovoDev packaging) / something else>. Plan first, then wait for my go.
./CLAUDE.md:7:- `skills/ai-writing-suite/` — AI writing-assistant suite (currently ships the polish/humanize capability; growing into a full suite — see plan below).
./docs/code-review-v1-2026-06-06.md:23:stdlib-only confirmed (no package.json/requirements/pyproject) → D5 holds. `sync.sh` idempotent;
./docs/code-review-v1-2026-06-06.md:40:generic 5-entry KB; full comms-qa retrieval is v2." Re-run `sync.sh`.
./docs/code-review-v1-2026-06-06.md:67:- **n1** `evals/` excluded from packaged targets (CI-only) — document why in `packaging/README.md`.
./docs/code-review-v1-2026-06-06.md:80:- Honest scaffolding (v2 stubs labeled; P31-P43 corruption disclosed; sync.sh single-source rule).
./docs/packaging.md:4:The single source of truth is `skills/ai-writing-suite/`. Each host gets a tiny manifest that
./docs/packaging.md:8:> This replaces the earlier generate-and-sync approach (`packaging/` + `sync.sh`), which was
./docs/packaging.md:15:| `/.claude-plugin/marketplace.json` | Claude | Marketplace catalog; `plugins[].source = "./skills/ai-writing-suite"` |
./docs/packaging.md:16:| `/skills/ai-writing-suite/.claude-plugin/plugin.json` | Claude | Plugin identity (name, version, metadata) |
./docs/packaging.md:17:| `/.agents/plugins/marketplace.json` | Codex | Marketplace catalog; `plugins[].source = {source:"local", path:"./skills/ai-writing-suite"}` |
./docs/packaging.md:18:| `/skills/ai-writing-suite/.codex-plugin/plugin.json` | Codex | Plugin identity (+ `"skills": "./skills/"`, `interface{}`) |
./docs/packaging.md:20:Both root marketplaces point at the **same** source tree. Claude auto-discovers the sub-skills
./docs/packaging.md:21:under `skills/ai-writing-suite/skills/`; the root `SKILL.md` is a documentation router.
./docs/packaging.md:25:- **Claude:** `claude plugin marketplace add surahli123/ai-writing-suite` → `claude plugin install ai-writing-suite@ai-writing-suite`
./docs/packaging.md:26:- **Codex:** `codex plugin marketplace add surahli123/ai-writing-suite` → `codex plugin add ai-writing-suite@ai-writing-suite`
./docs/packaging.md:27:- **Cursor:** copy `skills/ai-writing-suite/` into `~/.cursor/skills/ai-writing-suite/` (or a project's `.cursor/skills/`). Cursor reads Anthropic-format `SKILL.md` Agent Skills natively; no manifest needed. (Not `.cursor/rules/*.mdc` — that is passive context injection, the wrong primitive for callable skills.)
./docs/packaging.md:32:   files (`.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`).
./docs/packaging.md:33:2. Commit + push. Consumers refresh via `claude plugin update` / `codex plugin marketplace upgrade`.
./docs/packaging.md:39:- `claude plugin validate .` and `claude plugin validate skills/ai-writing-suite` (both must pass).
./docs/packaging.md:40:- Local install smoke per host (add the local path as a marketplace, install, confirm the skill
./docs/packaging.md:44:  (`marketplace add surahli123/ai-writing-suite`) before tagging a release.
./docs/packaging.md:54:RovoDev packaging. It will follow the same source-pointing model (explicit intent routing via the
./docs/design-ai-writing-suite-v1-2026-06-06.md:59:| **conorbronsdon/avoid-ai-writing** | Programmatic JS detector + tests + CI, CATEGORIES taxonomy, multi-surface packaging (Claude plugin + Cursor `.mdc`) + `sync-plugin-skill.sh` | Detector (v2), packaging/sync scaffold, Cursor target |
./docs/design-ai-writing-suite-v1-2026-06-06.md:61:| **Yuan1z0825/nature-skills** (`nature-writing` + `nature-polishing` only) | Academic polish/writing rubric, codex/plugin manifest conventions | `comms-polish` rubric, packaging conventions |
./docs/design-ai-writing-suite-v1-2026-06-06.md:88:├── packaging/
./docs/design-ai-writing-suite-v1-2026-06-06.md:89:│   ├── sync.sh                        # single source → 4 targets
./docs/design-ai-writing-suite-v1-2026-06-06.md:90:│   ├── .claude-plugin/ .codex-plugin/ cursor-rules/ rovodev/
./docs/design-ai-writing-suite-v1-2026-06-06.md:133:programmatic JS/Python detector, Cursor + RovoDev packaging, bilingual Chinese path,
./docs/design-ai-writing-suite-v1-2026-06-06.md:149:- **R4 — 4-surface sync drift.** Single source of truth + `sync.sh` (avoid-ai pattern).
./docs/design-ai-writing-suite-v1-2026-06-06.md:178:→ Cursor + RovoDev packaging → bilingual path → company fork with real playbook.
./docs/design-ai-writing-suite-v1-2026-06-06.md:185:- 4 MIT repos → detectors, scenario presets, voice templates, packaging/sync scaffolds.
./docs/design-ai-writing-suite-v1-2026-06-06.md:194:- Cursor + RovoDev packaging — v2 (Claude + Codex only).
./docs/handover-2026-06-06-ai-writing-suite-v1.md:22:- **No suite implementation exists.** The renamed `skills/ai-writing-suite/` still
./docs/handover-2026-06-06-ai-writing-suite-v1.md:48:   → human-gated self-improvement hook → NOTICE/CHANGELOG/README → Claude+Codex packaging.
./docs/handover-2026-06-06-ai-writing-suite-v1.md:63:- `skills/ai-writing-suite/SKILL.md` (current = humanizer content)
./docs/handover-2026-06-02-personal-productivity-skills-next.md:76:- Do not modify installed local skills under `/Users/surahli/.codex/skills/*` while packaging public repo copies unless explicitly asked.
./docs/handover-2026-06-02-personal-productivity-skills-next.md:94:- `$session-wrapup`: source material and closeout shape for packaging a smaller public `session-wrapup-lite`.
./docs/migration-plan-local-repo-2026-06-06.md:36:2. In the new copy: delete `skills/agent-goal-contracts/`, flatten/keep `skills/ai-writing-suite/`,
./docs/migration-plan-local-repo-2026-06-06.md:45:- Extract only `skills/ai-writing-suite/` history into a brand-new repo.
./docs/migration-plan-local-repo-2026-06-06.md:85:#   + (optional) flatten skills/ai-writing-suite/* to repo root — DECISION below
./docs/migration-plan-local-repo-2026-06-06.md:93:- **Keep `skills/ai-writing-suite/`** (no flatten) → matches the design doc's eventual multi-sub-skill
./docs/plan-publish-cleanup-test-2026-06-07.md:12:The handover/memory say "v1 shipped + packaging live-verified," but that verification only ever
./docs/plan-publish-cleanup-test-2026-06-07.md:16:   content (SKILL.md, skills/, _shared/, NOTICE/LICENSE) under `packaging/{claude,codex}/` is
./docs/plan-publish-cleanup-test-2026-06-07.md:17:   ignored. `gh api` confirms the remote `packaging/claude/` contains **only** `.claude-plugin/`
./docs/plan-publish-cleanup-test-2026-06-07.md:18:   and `packaging/codex/plugins/ai-writing-suite/` contains **only** `.codex-plugin/`. A user who
./docs/plan-publish-cleanup-test-2026-06-07.md:20:2. **The marketplace manifest is in the wrong place for one-liner install.** `claude plugin
./docs/plan-publish-cleanup-test-2026-06-07.md:21:   marketplace add <src>` looks for `<src>/.claude-plugin/marketplace.json`. The repo has **no
./docs/plan-publish-cleanup-test-2026-06-07.md:22:   root** `.claude-plugin/` (`gh api` → 404); the only one is buried 4 levels deep. So
./docs/plan-publish-cleanup-test-2026-06-07.md:23:   `claude plugin marketplace add surahli123/ai-writing-suite` 404s. Codex's is similarly nested
./docs/plan-publish-cleanup-test-2026-06-07.md:24:   (needs a long, fragile `--sparse skills/ai-writing-suite/packaging/codex`).
./docs/plan-publish-cleanup-test-2026-06-07.md:32:**Consequence:** "Step 1: publish to a marketplace" is really **two** things — (1a) *make the repo
./docs/plan-publish-cleanup-test-2026-06-07.md:48:| What | Add a **repo-root** `.claude-plugin/marketplace.json` whose `source` points at the already-tracked `skills/ai-writing-suite/`. No gitignore change. | Un-ignore `packaging/{claude,codex}/` output, run `sync.sh`, commit the generated tree. |
./docs/plan-publish-cleanup-test-2026-06-07.md:49:| Install UX | `claude plugin marketplace add surahli123/ai-writing-suite` (one-liner) | Same one-liner if manifest moved to root |
./docs/plan-publish-cleanup-test-2026-06-07.md:51:| Con | Ships `evals/` + `packaging/` to consumers (minor bloat) | Reintroduces the **sync-drift risk R4 was created to prevent** → needs a CI guardrail (`sync.sh` + "fail if committed tree stale") |
./docs/plan-publish-cleanup-test-2026-06-07.md:55:straight at the source tree). **Codex** needs its specific `.agents/plugins/marketplace.json` +
./docs/plan-publish-cleanup-test-2026-06-07.md:56:`plugins/<name>/.codex-plugin/plugin.json` layout with the body beside it, so Codex effectively
./docs/plan-publish-cleanup-test-2026-06-07.md:62:- Add repo-root marketplace manifest (Claude; mirror for Codex per its layout).
./docs/plan-publish-cleanup-test-2026-06-07.md:67:  exact `marketplace add` + `install` commands per host.
./docs/plan-publish-cleanup-test-2026-06-07.md:73:  registry exists in `claude` 2.1.168 (`marketplace add` only takes URL/path/owner+repo; no
./docs/plan-publish-cleanup-test-2026-06-07.md:89:- **Remove:** `skills/ai-writing-suite/` (4 tracked files) + `docs/design-ai-writing-suite-v1-2026-06-06.md`
./docs/plan-publish-cleanup-test-2026-06-07.md:166:- `gh api .../contents/.claude-plugin` → **404** (no root manifest on remote).
./docs/plan-publish-cleanup-test-2026-06-07.md:167:- `gh api .../packaging/claude` → only `.claude-plugin/`; `.../packaging/codex/plugins/ai-writing-suite` → only `.codex-plugin/` (no body on remote).
./docs/plan-publish-cleanup-test-2026-06-07.md:168:- `git check-ignore -v .../packaging/claude/SKILL.md` → ignored (`.gitignore:9`).
./docs/plan-publish-cleanup-test-2026-06-07.md:169:- `claude plugin marketplace add /tmp/empty` → "Marketplace file not found at <src>/.claude-plugin/marketplace.json" (proves resolution path).
./docs/plan-publish-cleanup-test-2026-06-07.md:171:- `codex` 0.137.0; `marketplace add` supports `--ref`, `--sparse`; working git marketplaces (EveryInc/compound-engineering) **commit** their plugin body.
./docs/plan-publish-cleanup-test-2026-06-07.md:189:  **No plugin/marketplace concept.** (Source: cursor.com/docs/skills, /docs/rules.)
./docs/plan-publish-cleanup-test-2026-06-07.md:190:- **DOC BUG to fix:** design doc §4 + `packaging/README.md:189` + `CHANGELOG.md` (`cursor-rules/`)
./docs/plan-publish-cleanup-test-2026-06-07.md:198:| Host | Can it point straight at `skills/ai-writing-suite/`? | What it actually needs |
./docs/plan-publish-cleanup-test-2026-06-07.md:200:| **Claude** | ✅ Yes | Root `.claude-plugin/marketplace.json` (+`plugin.json`) whose `source` = the tracked source tree. **No committed body.** |
./docs/plan-publish-cleanup-test-2026-06-07.md:201:| **Cursor** | ✅ Yes (as a copy) | Install doc: copy `skills/ai-writing-suite/` → user's `.cursor/skills/ai-writing-suite/`. Source SKILL.md is already Cursor-valid. **No committed body** (accepts evals/ bloat, like Claude). |
./docs/plan-publish-cleanup-test-2026-06-07.md:202:| **Codex** | ❌ No | Codex marketplace entry `source:{source:local, path:./plugins/<name>}` needs the body **committed at that path**. A relative `../../` escape to the source tree is unverified/risky. → Codex is the **one host that needs a committed generated body**. |
./docs/plan-publish-cleanup-test-2026-06-07.md:207:  source subtree (no body); **Codex** gets a committed generated body via `sync.sh` + a drift
./docs/plan-publish-cleanup-test-2026-06-07.md:208:  guardrail (`sync.sh --check` in CI). Smallest committed surface; honors Option A everywhere it can.
./docs/plan-publish-cleanup-test-2026-06-07.md:213:1. **Doc-correct Cursor primitive** (design doc / packaging README / CHANGELOG: rules → skills). Small.
./docs/plan-publish-cleanup-test-2026-06-07.md:214:2. **Wire `sync.sh`** for the chosen plan: add a Cursor target (generates `.cursor/skills/...`); for
./docs/plan-publish-cleanup-test-2026-06-07.md:215:   Codex ensure the body is produced + (per plan) tracked; add `sync.sh --check` (stale-detect).
./docs/plan-publish-cleanup-test-2026-06-07.md:216:3. **Add tracked manifests:** root `.claude-plugin/marketplace.json` (+ plugin.json) → source tree;
./docs/plan-publish-cleanup-test-2026-06-07.md:217:   root-level Codex `.agents/plugins/marketplace.json` (relocate from the deep path for one-liner UX)
./docs/plan-publish-cleanup-test-2026-06-07.md:219:4. **README Quickstart:** exact install per host (Claude `marketplace add surahli123/ai-writing-suite`
./docs/plan-publish-cleanup-test-2026-06-07.md:220:   + `plugin install`; Codex `marketplace add … [--sparse]`; Cursor copy-dir / GitHub import).
./docs/plan-publish-cleanup-test-2026-06-07.md:222:   - Claude: fresh-clone `marketplace add` + `plugin install` → canned prompt → `comms-polish` fires. ✅ local
./docs/plan-publish-cleanup-test-2026-06-07.md:223:   - Codex: fresh-clone `marketplace add` + `plugin add` → canned prompt. ✅ local
./skills/ai-writing-suite/CHANGELOG.md:15:  and the Claude marketplace manifest was not at a resolvable location. Both Claude
./skills/ai-writing-suite/CHANGELOG.md:17:  marketplace manifests (`.claude-plugin/marketplace.json` and
./skills/ai-writing-suite/CHANGELOG.md:18:  `.agents/plugins/marketplace.json`), each backed by an in-source `plugin.json`.
./skills/ai-writing-suite/CHANGELOG.md:22:  `.cursor/skills/`; install = copy `skills/ai-writing-suite/` into a Cursor skills
./skills/ai-writing-suite/CHANGELOG.md:26:  maintainer packaging note at `docs/packaging.md`.
./skills/ai-writing-suite/CHANGELOG.md:29:- **Generate-and-sync packaging** (`packaging/` + `sync.sh`) — obsolete now that every
./skills/ai-writing-suite/CHANGELOG.md:42:- **Directory structure** — standardized layout with `skills/`, `_shared/` (knowledge, patterns, voice profiles), and `packaging/` for multi-surface distribution.
./skills/ai-writing-suite/CHANGELOG.md:89:- **Sync tooling scaffold** (`packaging/sync.sh`) — single source of truth distributed to four surfaces (Claude, Codex, Cursor, RovoDev).
./skills/ai-writing-suite/CHANGELOG.md:90:- **Multi-surface manifests** — `.claude-plugin/`, `.codex-plugin/`, `cursor-rules/`, `rovodev/` directories (v1: Claude + Codex only; v2: Cursor + RovoDev).
./skills/ai-writing-suite/CHANGELOG.md:109:- **Ships in v1:** Suite skeleton, `comms-polish`, `voice-onboard`, generic KB seed, self-improvement hook, eval harness, Claude + Codex packaging, NOTICE/CHANGELOG/README.
./skills/ai-writing-suite/CHANGELOG.md:110:- **Deferred to v2:** `comms-qa` full RAG, `comms-draft`, Confluence ingestion, programmatic detector, Cursor + RovoDev packaging, bilingual Chinese path, embedding index.
./skills/ai-writing-suite/CHANGELOG.md:136:- Cursor + RovoDev packaging — surface-specific manifests.
./reviews/2026-06-07-make-v1-installable.md:14:You are an ADVERSARIAL code reviewer with independent context. In THIS git repo, run `git diff main..HEAD` (the changes are commit 8c612d8) and read whatever files you need: the new repo-root .claude-plugin/marketplace.json, skills/ai-writing-suite/.claude-plugin/plugin.json, skills/ai-writing-suite/packaging/sync.sh, .gitignore, README.md, skills/ai-writing-suite/packaging/README.md, and the Codex manifests under skills/ai-writing-suite/packaging/codex/. Then produce a structured adversarial review.
./reviews/2026-06-07-make-v1-installable.md:17: (a) repo-root .claude-plugin/marketplace.json with plugin source "./skills/ai-writing-suite" + a source-tree skills/ai-writing-suite/.claude-plugin/plugin.json — Claude points at the TRACKED SOURCE TREE, no committed body;
./reviews/2026-06-07-make-v1-installable.md:18: (b) commits the Codex plugin body under skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/ and un-ignores it in .gitignore (Codex marketplace source {source:local, path:./plugins/ai-writing-suite});
./reviews/2026-06-07-make-v1-installable.md:19: (c) sync.sh gains a --check drift guardrail (builds the body into a temp dir, `diff -r --exclude=.codex-plugin` against the committed body, exit 1 on drift);
./reviews/2026-06-07-make-v1-installable.md:21: (e) corrects the Cursor packaging primitive from .cursor/rules/*.mdc to .cursor/skills/ Agent Skills.
./reviews/2026-06-07-make-v1-installable.md:22:The ~33 committed files under packaging/codex/plugins/ai-writing-suite/ are a GENERATED byte-copy of the source tree (via sync.sh) — review the APPROACH, not each duplicated file.
./reviews/2026-06-07-make-v1-installable.md:26: 1. Does pointing the Claude marketplace source at "./skills/ai-writing-suite" reliably install, and will Claude discover the nested skills/ sub-skills (router SKILL.md sits at the plugin root)? Any resolution pitfall once published to GitHub (vs the local smoke that already passed)?
./reviews/2026-06-07-make-v1-installable.md:27: 2. Codex committed-body + the .gitignore re-include rules: does the body actually reach the remote, and is the marketplace source path correct relative to the marketplace.json location? Any path bug?
./reviews/2026-06-07-make-v1-installable.md:28: 3. sync.sh --check correctness: false negatives, BSD/macOS `diff --exclude` portability, interaction with `set -euo pipefail` + the EXIT trap, mktemp cleanup.
./reviews/2026-06-07-make-v1-installable.md:29: 4. README GitHub-URL install commands: is `claude plugin marketplace add surahli123/ai-writing-suite` + `claude plugin install ai-writing-suite@ai-writing-suite` correct, and is the Codex `--sparse skills/ai-writing-suite/packaging/codex` form correct?
./reviews/2026-06-07-make-v1-installable.md:287:/bin/zsh -lc 'rg -n "ai-writing-suite|Claude marketplace|Codex plugin|packaging/codex|marketplace" /Users/surahli/.codex/memories/MEMORY.md' in /Users/surahli/Documents/ai-writing-suite
./reviews/2026-06-07-make-v1-installable.md:291:290:scope: June 6-7 AI Writing Suite work covering the move out of the umbrella repo into a standalone local repo, Layer 0-3 implementation, isolated review, and the later Codex/Claude packaging-surface checks; use when the user resumes `ai-writing-suite` or asks how the standalone repo was supposed to proceed.
./reviews/2026-06-07-make-v1-installable.md:298:318:- extensions/chronicle/resources/2026-06-06T21-01-00-tkIN-10min-memory-summary.md (cwd=/Users/surahli/Documents/ai-writing-suite, rollout_path=/Users/surahli/.codex/memories/extensions/chronicle/resources/2026-06-06T21-01-00-tkIN-10min-memory-summary.md, updated_at=2026-06-06T21:01:00+00:00, thread_id=None, Chronicle window showing the user choosing `Python detector now` and the Layer 3 split into eval/docs/packaging)
./reviews/2026-06-07-make-v1-installable.md:299:324:## Task 4: review the v1 state in isolation and flag speculative Codex plugin-manifest packaging, outcome partial
./reviews/2026-06-07-make-v1-installable.md:301:329:- extensions/chronicle/resources/2026-06-07T00-26-00-xsag-10min-memory-summary.md (cwd=/Users/surahli/Documents/ai-writing-suite, rollout_path=/Users/surahli/.codex/memories/extensions/chronicle/resources/2026-06-07T00-26-00-xsag-10min-memory-summary.md, updated_at=2026-06-07T00:26:00+00:00, thread_id=None, Chronicle window showing `main` fast-forward to `c3f1713` and the pre-publish check that treated `packaging/codex/.codex-plugin/plugin.json` as speculative)
./reviews/2026-06-07-make-v1-installable.md:302:333:- feat/ai-writing-suite-v1, code-reviewer pass, 17/17 detector, 6/6 fixtures, AI-slop 62/100 -> 0/100, c3f1713, packaging/codex/.codex-plugin/plugin.json, SKILL.md, references/, manifest verification
./reviews/2026-06-07-make-v1-installable.md:305:348:- Layer 1 verification depended on one shared contract surface: `skills/ai-writing-suite/_shared/voice-profile.md` is written by `voice-onboard` and read by `comms-polish`, with graceful degradation when the profile is absent [Task 2]
./reviews/2026-06-07-make-v1-installable.md:306:349:- The next visible Layer 2 split was intentionally parallel and disjoint: one executor wrote `skills/ai-writing-suite/_shared/knowledge/structure.md` for a generic KB seed plus retrieval smoke path, and the other wrote `skills/ai-writing-suite/_shared/self-improvement.md` for a human-gated self-improvement hook [Task 2]
./reviews/2026-06-07-make-v1-installable.md:307:352:- The pre-publish packaging check found that installed Codex skills under `~/.codex/skills/` are folders containing `SKILL.md` plus optional `references/`, without a required `plugin.json`; treat `packaging/codex/.codex-plugin/plugin.json` as speculative until host docs prove otherwise [Task 4]
./reviews/2026-06-07-make-v1-installable.md:321:c6156ce Pre-publish: restructure Codex packaging to conformant marketplace layout
./reviews/2026-06-07-make-v1-installable.md:322:55cd13c Pre-publish: document verified Codex marketplace standard
./reviews/2026-06-07-make-v1-installable.md:325: .claude-plugin/marketplace.json                    |  17 ++
./reviews/2026-06-07-make-v1-installable.md:328: skills/ai-writing-suite/.claude-plugin/plugin.json |  12 ++
./reviews/2026-06-07-make-v1-installable.md:329: skills/ai-writing-suite/CHANGELOG.md               |  19 ++
./reviews/2026-06-07-make-v1-installable.md:330: skills/ai-writing-suite/packaging/README.md        |  22 +-
./reviews/2026-06-07-make-v1-installable.md:363: skills/ai-writing-suite/packaging/sync.sh          |  37 +++-
./reviews/2026-06-07-make-v1-installable.md:392:/bin/zsh -lc "nl -ba .claude-plugin/marketplace.json skills/ai-writing-suite/.claude-plugin/plugin.json skills/ai-writing-suite/packaging/sync.sh .gitignore README.md skills/ai-writing-suite/packaging/README.md | sed -n '1,260p'" in /Users/surahli/Documents/ai-writing-suite
./reviews/2026-06-07-make-v1-installable.md:394:/bin/zsh -lc 'find skills/ai-writing-suite/packaging/codex -maxdepth 4 -type f | sort' in /Users/surahli/Documents/ai-writing-suite
./reviews/2026-06-07-make-v1-installable.md:396:/bin/zsh -lc 'git diff --find-renames --find-copies main..HEAD -- .claude-plugin/marketplace.json skills/ai-writing-suite/.claude-plugin/plugin.json skills/ai-writing-suite/packaging/sync.sh .gitignore README.md skills/ai-writing-suite/packaging/README.md' in /Users/surahli/Documents/ai-writing-suite
./reviews/2026-06-07-make-v1-installable.md:398:/bin/zsh -lc 'git ls-files skills/ai-writing-suite/packaging/codex | sort' in /Users/surahli/Documents/ai-writing-suite
./reviews/2026-06-07-make-v1-installable.md:404:skills/ai-writing-suite/packaging/codex/.agents/plugins/marketplace.json
./reviews/2026-06-07-make-v1-installable.md:405:skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/.codex-plugin/plugin.json
./reviews/2026-06-07-make-v1-installable.md:406:skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/CHANGELOG.md
./reviews/2026-06-07-make-v1-installable.md:407:skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/LICENSE
./reviews/2026-06-07-make-v1-installable.md:408:skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/NOTICE.md
./reviews/2026-06-07-make-v1-installable.md:409:skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/README.md
./reviews/2026-06-07-make-v1-installable.md:410:skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/SKILL.md
./reviews/2026-06-07-make-v1-installable.md:411:skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/_shared/host-profile-template.md
./reviews/2026-06-07-make-v1-installable.md:412:skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/_shared/learned-rules.md
./reviews/2026-06-07-make-v1-installable.md:413:skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/_shared/self-improvement.md
./reviews/2026-06-07-make-v1-installable.md:414:skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/_shared/voice-profile.md
./reviews/2026-06-07-make-v1-installable.md:423:skills/ai-writing-suite/packaging/codex/.agents/plugins/marketplace.json
./reviews/2026-06-07-make-v1-installable.md:424:skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/.codex-plugin/plugin.json
./reviews/2026-06-07-make-v1-installable.md:425:skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/CHANGELOG.md
./reviews/2026-06-07-make-v1-installable.md:426:skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/LICENSE
./reviews/2026-06-07-make-v1-installable.md:427:skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/NOTICE.md
./reviews/2026-06-07-make-v1-installable.md:428:skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/README.md
./reviews/2026-06-07-make-v1-installable.md:429:skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/SKILL.md
./reviews/2026-06-07-make-v1-installable.md:430:skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/_shared/host-profile-template.md
./reviews/2026-06-07-make-v1-installable.md:431:skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/_shared/knowledge/.gitkeep
./reviews/2026-06-07-make-v1-installable.md:432:skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/_shared/knowledge/INDEX.md
./reviews/2026-06-07-make-v1-installable.md:433:skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/_shared/knowledge/README.md
./reviews/2026-06-07-make-v1-installable.md:434:skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md
./reviews/2026-06-07-make-v1-installable.md:435:skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/_shared/knowledge/audience.md
./reviews/2026-06-07-make-v1-installable.md:436:skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/_shared/knowledge/clarity.md
./reviews/2026-06-07-make-v1-installable.md:437:skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/_shared/knowledge/revision.md
./reviews/2026-06-07-make-v1-installable.md:438:skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/_shared/knowledge/structure.md
./reviews/2026-06-07-make-v1-installable.md:439:skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/_shared/knowledge/tone.md
./reviews/2026-06-07-make-v1-installable.md:440:skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/_shared/learned-rules.md
./reviews/2026-06-07-make-v1-installable.md:441:skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/_shared/patterns/00-index.md
./reviews/2026-06-07-make-v1-installable.md:442:skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/_shared/patterns/communication-artifacts.md
./reviews/2026-06-07-make-v1-installable.md:443:skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/_shared/patterns/hedging-filler.md
./reviews/2026-06-07-make-v1-installable.md:444:skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/_shared/patterns/lexical-tells.md
./reviews/2026-06-07-make-v1-installable.md:445:skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/_shared/patterns/punctuation-formatting.md
./reviews/2026-06-07-make-v1-installable.md:446:skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/_shared/patterns/rhythm-stylometric.md
./reviews/2026-06-07-make-v1-installable.md:447:skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/_shared/patterns/significance-attribution.md
./reviews/2026-06-07-make-v1-installable.md:448:skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/_shared/patterns/structural-tells.md
./reviews/2026-06-07-make-v1-installable.md:449:skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/_shared/self-improvement.md
./reviews/2026-06-07-make-v1-installable.md:450:skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/_shared/voice-profile.md
./reviews/2026-06-07-make-v1-installable.md:451:skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/skills/comms-draft/SKILL.md
./reviews/2026-06-07-make-v1-installable.md:452:skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/skills/comms-polish/SKILL.md
./reviews/2026-06-07-make-v1-installable.md:453:skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/skills/comms-polish/references/final-pass-checklist.md
./reviews/2026-06-07-make-v1-installable.md:454:skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/skills/comms-polish/references/scenario-presets.md
./reviews/2026-06-07-make-v1-installable.md:455:skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/skills/comms-qa/SKILL.md
./reviews/2026-06-07-make-v1-installable.md:456:skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/skills/voice-onboard/SKILL.md
./reviews/2026-06-07-make-v1-installable.md:461:diff --git a/.claude-plugin/marketplace.json b/.claude-plugin/marketplace.json
./reviews/2026-06-07-make-v1-installable.md:465:+++ b/.claude-plugin/marketplace.json
./reviews/2026-06-07-make-v1-installable.md:468:+  "$schema": "https://json.schemastore.org/claude-code-marketplace.json",
./reviews/2026-06-07-make-v1-installable.md:477:+      "source": "./skills/ai-writing-suite",
./reviews/2026-06-07-make-v1-installable.md:490: skills/ai-writing-suite/packaging/claude/*
./reviews/2026-06-07-make-v1-installable.md:491: !skills/ai-writing-suite/packaging/claude/.claude-plugin
./reviews/2026-06-07-make-v1-installable.md:492:-# Codex marketplace: keep hand-maintained manifests, ignore generated content
./reviews/2026-06-07-make-v1-installable.md:493:+# Codex marketplace: the marketplace manifest is hand-maintained; the plugin BODY
./reviews/2026-06-07-make-v1-installable.md:496:+# generated from the source tree by sync.sh — keep it in sync (sync.sh --check guards
./reviews/2026-06-07-make-v1-installable.md:498: skills/ai-writing-suite/packaging/codex/*
./reviews/2026-06-07-make-v1-installable.md:499: !skills/ai-writing-suite/packaging/codex/.agents
./reviews/2026-06-07-make-v1-installable.md:500: !skills/ai-writing-suite/packaging/codex/plugins
./reviews/2026-06-07-make-v1-installable.md:501: skills/ai-writing-suite/packaging/codex/plugins/*
./reviews/2026-06-07-make-v1-installable.md:502: !skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite
./reviews/2026-06-07-make-v1-installable.md:503:-skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/*
./reviews/2026-06-07-make-v1-installable.md:504:-!skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/.codex-plugin
./reviews/2026-06-07-make-v1-installable.md:526:+One source of truth (`skills/ai-writing-suite/`) published to three hosts.
./reviews/2026-06-07-make-v1-installable.md:531:+claude plugin marketplace add surahli123/ai-writing-suite
./reviews/2026-06-07-make-v1-installable.md:532:+claude plugin install ai-writing-suite@ai-writing-suite
./reviews/2026-06-07-make-v1-installable.md:541:+codex plugin marketplace add surahli123/ai-writing-suite --sparse skills/ai-writing-suite/packaging/codex
./reviews/2026-06-07-make-v1-installable.md:542:+codex plugin add ai-writing-suite@ai-writing-suite
./reviews/2026-06-07-make-v1-installable.md:545:+The `--sparse` path points Codex at the marketplace directory committed inside the repo.
./reviews/2026-06-07-make-v1-installable.md:549:+Cursor reads Anthropic-format **Agent Skills** from `.cursor/skills/` — there is no marketplace, so
./reviews/2026-06-07-make-v1-installable.md:554:+cp -R ai-writing-suite/skills/ai-writing-suite ~/.cursor/skills/ai-writing-suite
./reviews/2026-06-07-make-v1-installable.md:563:+.claude-plugin/marketplace.json    # Claude marketplace (points at the source tree)
./reviews/2026-06-07-make-v1-installable.md:573:+    .claude-plugin/plugin.json     # Claude plugin manifest
./reviews/2026-06-07-make-v1-installable.md:577:+    packaging/                     # sync.sh + Codex marketplace (codex/)
./reviews/2026-06-07-make-v1-installable.md:583:diff --git a/skills/ai-writing-suite/.claude-plugin/plugin.json b/skills/ai-writing-suite/.claude-plugin/plugin.json
./reviews/2026-06-07-make-v1-installable.md:587:+++ b/skills/ai-writing-suite/.claude-plugin/plugin.json
./reviews/2026-06-07-make-v1-installable.md:601:diff --git a/skills/ai-writing-suite/packaging/README.md b/skills/ai-writing-suite/packaging/README.md
./reviews/2026-06-07-make-v1-installable.md:603:--- a/skills/ai-writing-suite/packaging/README.md
./reviews/2026-06-07-make-v1-installable.md:604:+++ b/skills/ai-writing-suite/packaging/README.md
./reviews/2026-06-07-make-v1-installable.md:617:+Cursor has no plugin marketplace; distribution is "copy the skill tree into a
./reviews/2026-06-07-make-v1-installable.md:619:+a user copies `skills/ai-writing-suite/` into `~/.cursor/skills/ai-writing-suite/`
./reviews/2026-06-07-make-v1-installable.md:627:-Cursor (`.cursor/rules/` + `.mdc` file) and RovoDev packaging are deferred to
./reviews/2026-06-07-make-v1-installable.md:629:-sync.sh gains a new `sync_target` call; the new target dir gets a manually-
./reviews/2026-06-07-make-v1-installable.md:631:+RovoDev packaging is deferred to v2. When added it follows the same pattern:
./reviews/2026-06-07-make-v1-installable.md:632:+sync.sh gains a new `sync_target` call; generated content is never hand-edited.
./reviews/2026-06-07-make-v1-installable.md:633:diff --git a/skills/ai-writing-suite/packaging/sync.sh b/skills/ai-writing-suite/packaging/sync.sh
./reviews/2026-06-07-make-v1-installable.md:635:--- a/skills/ai-writing-suite/packaging/sync.sh
./reviews/2026-06-07-make-v1-installable.md:636:+++ b/skills/ai-writing-suite/packaging/sync.sh
./reviews/2026-06-07-make-v1-installable.md:639: #   bash packaging/sync.sh            # from repo root OR from packaging/
./reviews/2026-06-07-make-v1-installable.md:640: #   bash packaging/sync.sh --dry-run  # print what would happen, copy nothing
./reviews/2026-06-07-make-v1-installable.md:641:+#   bash packaging/sync.sh --check    # verify committed Codex body matches source; no writes (CI gate)
./reviews/2026-06-07-make-v1-installable.md:671:+# and diffs, excluding the hand-maintained .codex-plugin manifest.
./reviews/2026-06-07-make-v1-installable.md:682:+  if diff -r --exclude=.codex-plugin "$TMP" "$CODEX_TARGET" >/dev/null 2>&1; then
./reviews/2026-06-07-make-v1-installable.md:686:+    log "DRIFT: committed Codex body is STALE vs source. Run 'bash packaging/sync.sh' and commit."
./reviews/2026-06-07-make-v1-installable.md:687:+    diff -r --exclude=.codex-plugin "$TMP" "$CODEX_TARGET" | sed 's/^/  /' || true
./reviews/2026-06-07-make-v1-installable.md:707:web search: Claude Code plugin marketplace add GitHub repository plugin install syntax official docs
./reviews/2026-06-07-make-v1-installable.md:709:web search: site:developers.openai.com codex plugins marketplace sparse
./reviews/2026-06-07-make-v1-installable.md:711:web search: https://code.claude.com/docs/en/plugin-marketplaces
./reviews/2026-06-07-make-v1-installable.md:713:The first material fact is that Claude’s current docs allow a marketplace source to be any relative plugin directory under the marketplace root, but `plugin.json` versioning changes update behavior. I’m checking whether this commit creates an installable first version but a stale-update trap.
./reviews/2026-06-07-make-v1-installable.md:730:/bin/zsh -lc "for f in .claude-plugin/marketplace.json skills/ai-writing-suite/.claude-plugin/plugin.json skills/ai-writing-suite/packaging/sync.sh .gitignore README.md skills/ai-writing-suite/packaging/README.md skills/ai-writing-suite/packaging/codex/.agents/plugins/marketplace.json skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/.codex-plugin/plugin.json skills/ai-writing-suite/SKILL.md; do printf '\\n### %s\\n' \""'$f"; nl -ba "$f" | sed -n '"'1,220p'; done" in /Users/surahli/Documents/ai-writing-suite
./reviews/2026-06-07-make-v1-installable.md:732:/bin/zsh -lc "bash skills/ai-writing-suite/packaging/sync.sh --check; printf 'exit=%s\\n' "'$?' in /Users/surahli/Documents/ai-writing-suite
./reviews/2026-06-07-make-v1-installable.md:736:/bin/zsh -lc "find skills/ai-writing-suite -maxdepth 3 -type f | sort | sed -n '1,220p'" in /Users/surahli/Documents/ai-writing-suite
./reviews/2026-06-07-make-v1-installable.md:738:skills/ai-writing-suite/.claude-plugin/plugin.json
./reviews/2026-06-07-make-v1-installable.md:739:skills/ai-writing-suite/CHANGELOG.md
./reviews/2026-06-07-make-v1-installable.md:740:skills/ai-writing-suite/LICENSE
./reviews/2026-06-07-make-v1-installable.md:741:skills/ai-writing-suite/NOTICE.md
./reviews/2026-06-07-make-v1-installable.md:742:skills/ai-writing-suite/README.md
./reviews/2026-06-07-make-v1-installable.md:743:skills/ai-writing-suite/SKILL.md
./reviews/2026-06-07-make-v1-installable.md:744:skills/ai-writing-suite/_shared/host-profile-template.md
./reviews/2026-06-07-make-v1-installable.md:745:skills/ai-writing-suite/_shared/knowledge/.gitkeep
./reviews/2026-06-07-make-v1-installable.md:746:skills/ai-writing-suite/_shared/knowledge/INDEX.md
./reviews/2026-06-07-make-v1-installable.md:747:skills/ai-writing-suite/_shared/knowledge/README.md
./reviews/2026-06-07-make-v1-installable.md:748:skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md
./reviews/2026-06-07-make-v1-installable.md:749:skills/ai-writing-suite/_shared/knowledge/audience.md
./reviews/2026-06-07-make-v1-installable.md:750:skills/ai-writing-suite/_shared/knowledge/clarity.md
./reviews/2026-06-07-make-v1-installable.md:751:skills/ai-writing-suite/_shared/knowledge/revision.md
./reviews/2026-06-07-make-v1-installable.md:752:skills/ai-writing-suite/_shared/knowledge/structure.md
./reviews/2026-06-07-make-v1-installable.md:753:skills/ai-writing-suite/_shared/knowledge/tone.md
./reviews/2026-06-07-make-v1-installable.md:754:skills/ai-writing-suite/_shared/learned-rules.md
./reviews/2026-06-07-make-v1-installable.md:755:skills/ai-writing-suite/_shared/patterns/00-index.md
./reviews/2026-06-07-make-v1-installable.md:756:skills/ai-writing-suite/_shared/patterns/communication-artifacts.md
./reviews/2026-06-07-make-v1-installable.md:757:skills/ai-writing-suite/_shared/patterns/hedging-filler.md
./reviews/2026-06-07-make-v1-installable.md:758:skills/ai-writing-suite/_shared/patterns/lexical-tells.md
./reviews/2026-06-07-make-v1-installable.md:759:skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md
./reviews/2026-06-07-make-v1-installable.md:760:skills/ai-writing-suite/_shared/patterns/rhythm-stylometric.md
./reviews/2026-06-07-make-v1-installable.md:761:skills/ai-writing-suite/_shared/patterns/significance-attribution.md
./reviews/2026-06-07-make-v1-installable.md:762:skills/ai-writing-suite/_shared/patterns/structural-tells.md
./reviews/2026-06-07-make-v1-installable.md:763:skills/ai-writing-suite/_shared/self-improvement.md
./reviews/2026-06-07-make-v1-installable.md:764:skills/ai-writing-suite/_shared/voice-profile.md
./reviews/2026-06-07-make-v1-installable.md:765:skills/ai-writing-suite/evals/README.md
./reviews/2026-06-07-make-v1-installable.md:766:skills/ai-writing-suite/evals/__pycache__/smoke_test.cpython-314.pyc
./reviews/2026-06-07-make-v1-installable.md:767:skills/ai-writing-suite/evals/detector/__init__.py
./reviews/2026-06-07-make-v1-installable.md:768:skills/ai-writing-suite/evals/detector/cli.py
./reviews/2026-06-07-make-v1-installable.md:769:skills/ai-writing-suite/evals/detector/detector.py
./reviews/2026-06-07-make-v1-installable.md:770:skills/ai-writing-suite/evals/detector/patterns.py
./reviews/2026-06-07-make-v1-installable.md:771:skills/ai-writing-suite/evals/detector/test_detector.py
./reviews/2026-06-07-make-v1-installable.md:772:skills/ai-writing-suite/evals/fixtures/__init__.py
./reviews/2026-06-07-make-v1-installable.md:773:skills/ai-writing-suite/evals/fixtures/fixtures.json
./reviews/2026-06-07-make-v1-installable.md:774:skills/ai-writing-suite/evals/fixtures/rubric.md
./reviews/2026-06-07-make-v1-installable.md:775:skills/ai-writing-suite/evals/fixtures/run_fixtures.py
./reviews/2026-06-07-make-v1-installable.md:776:skills/ai-writing-suite/evals/fixtures/test_fixtures.py
./reviews/2026-06-07-make-v1-installable.md:777:skills/ai-writing-suite/evals/smoke_test.py
./reviews/2026-06-07-make-v1-installable.md:778:skills/ai-writing-suite/packaging/.gitkeep
./reviews/2026-06-07-make-v1-installable.md:779:skills/ai-writing-suite/packaging/README.md
./reviews/2026-06-07-make-v1-installable.md:780:skills/ai-writing-suite/packaging/claude/CHANGELOG.md
./reviews/2026-06-07-make-v1-installable.md:781:skills/ai-writing-suite/packaging/claude/LICENSE
./reviews/2026-06-07-make-v1-installable.md:782:skills/ai-writing-suite/packaging/claude/NOTICE.md
./reviews/2026-06-07-make-v1-installable.md:783:skills/ai-writing-suite/packaging/claude/README.md
./reviews/2026-06-07-make-v1-installable.md:784:skills/ai-writing-suite/packaging/claude/SKILL.md
./reviews/2026-06-07-make-v1-installable.md:785:skills/ai-writing-suite/packaging/sync.sh
./reviews/2026-06-07-make-v1-installable.md:786:skills/ai-writing-suite/skills/comms-draft/SKILL.md
./reviews/2026-06-07-make-v1-installable.md:787:skills/ai-writing-suite/skills/comms-polish/SKILL.md
./reviews/2026-06-07-make-v1-installable.md:788:skills/ai-writing-suite/skills/comms-qa/SKILL.md
./reviews/2026-06-07-make-v1-installable.md:789:skills/ai-writing-suite/skills/voice-onboard/SKILL.md
./reviews/2026-06-07-make-v1-installable.md:807:A	.claude-plugin/marketplace.json
./reviews/2026-06-07-make-v1-installable.md:810:A	skills/ai-writing-suite/.claude-plugin/plugin.json
./reviews/2026-06-07-make-v1-installable.md:811:M	skills/ai-writing-suite/CHANGELOG.md
./reviews/2026-06-07-make-v1-installable.md:812:M	skills/ai-writing-suite/packaging/README.md
./reviews/2026-06-07-make-v1-installable.md:813:A	skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/CHANGELOG.md
./reviews/2026-06-07-make-v1-installable.md:814:A	skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/LICENSE
./reviews/2026-06-07-make-v1-installable.md:815:A	skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/NOTICE.md
./reviews/2026-06-07-make-v1-installable.md:816:A	skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/README.md
./reviews/2026-06-07-make-v1-installable.md:817:A	skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/SKILL.md
./reviews/2026-06-07-make-v1-installable.md:818:A	skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/_shared/host-profile-template.md
./reviews/2026-06-07-make-v1-installable.md:819:A	skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/_shared/knowledge/.gitkeep
./reviews/2026-06-07-make-v1-installable.md:820:A	skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/_shared/knowledge/INDEX.md
./reviews/2026-06-07-make-v1-installable.md:821:A	skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/_shared/knowledge/README.md
./reviews/2026-06-07-make-v1-installable.md:822:A	skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md
./reviews/2026-06-07-make-v1-installable.md:823:A	skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/_shared/knowledge/audience.md
./reviews/2026-06-07-make-v1-installable.md:824:A	skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/_shared/knowledge/clarity.md
./reviews/2026-06-07-make-v1-installable.md:825:A	skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/_shared/knowledge/revision.md
./reviews/2026-06-07-make-v1-installable.md:826:A	skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/_shared/knowledge/structure.md
./reviews/2026-06-07-make-v1-installable.md:827:A	skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/_shared/knowledge/tone.md
./reviews/2026-06-07-make-v1-installable.md:828:A	skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/_shared/learned-rules.md
./reviews/2026-06-07-make-v1-installable.md:829:A	skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/_shared/patterns/00-index.md
./reviews/2026-06-07-make-v1-installable.md:830:A	skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/_shared/patterns/communication-artifacts.md
./reviews/2026-06-07-make-v1-installable.md:831:A	skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/_shared/patterns/hedging-filler.md
./reviews/2026-06-07-make-v1-installable.md:832:A	skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/_shared/patterns/lexical-tells.md
./reviews/2026-06-07-make-v1-installable.md:833:A	skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/_shared/patterns/punctuation-formatting.md
./reviews/2026-06-07-make-v1-installable.md:834:A	skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/_shared/patterns/rhythm-stylometric.md
./reviews/2026-06-07-make-v1-installable.md:835:A	skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/_shared/patterns/significance-attribution.md
./reviews/2026-06-07-make-v1-installable.md:836:A	skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/_shared/patterns/structural-tells.md
./reviews/2026-06-07-make-v1-installable.md:837:A	skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/_shared/self-improvement.md
./reviews/2026-06-07-make-v1-installable.md:838:A	skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/_shared/voice-profile.md
./reviews/2026-06-07-make-v1-installable.md:839:A	skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/skills/comms-draft/SKILL.md
./reviews/2026-06-07-make-v1-installable.md:840:A	skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/skills/comms-polish/SKILL.md
./reviews/2026-06-07-make-v1-installable.md:841:A	skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/skills/comms-polish/references/final-pass-checklist.md
./reviews/2026-06-07-make-v1-installable.md:842:A	skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/skills/comms-polish/references/scenario-presets.md
./reviews/2026-06-07-make-v1-installable.md:843:A	skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/skills/comms-qa/SKILL.md
./reviews/2026-06-07-make-v1-installable.md:844:A	skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/skills/voice-onboard/SKILL.md
./reviews/2026-06-07-make-v1-installable.md:845:M	skills/ai-writing-suite/packaging/sync.sh
./reviews/2026-06-07-make-v1-installable.md:849:### .claude-plugin/marketplace.json
./reviews/2026-06-07-make-v1-installable.md:851:     2	  "$schema": "https://json.schemastore.org/claude-code-marketplace.json",
./reviews/2026-06-07-make-v1-installable.md:860:    11	      "source": "./skills/ai-writing-suite",
./reviews/2026-06-07-make-v1-installable.md:868:### skills/ai-writing-suite/.claude-plugin/plugin.json
./reviews/2026-06-07-make-v1-installable.md:882:### skills/ai-writing-suite/packaging/sync.sh
./reviews/2026-06-07-make-v1-installable.md:884:     2	# sync.sh — Single-source → target assembler for AI Writing Suite packaging.
./reviews/2026-06-07-make-v1-installable.md:886:     4	# SOURCE OF TRUTH: skills/ai-writing-suite/ (the directory above packaging/)
./reviews/2026-06-07-make-v1-installable.md:887:     5	# GENERATED:      packaging/claude/   packaging/codex/
./reviews/2026-06-07-make-v1-installable.md:889:     7	# Rule: NEVER hand-edit files inside packaging/claude/ or packaging/codex/.
./reviews/2026-06-07-make-v1-installable.md:890:     8	#       Edit the source under skills/ai-writing-suite/ and re-run this script.
./reviews/2026-06-07-make-v1-installable.md:891:     9	#       See packaging/README.md for the full rationale (design R4).
./reviews/2026-06-07-make-v1-installable.md:894:    12	#   bash packaging/sync.sh            # from repo root OR from packaging/
./reviews/2026-06-07-make-v1-installable.md:895:    13	#   bash packaging/sync.sh --dry-run  # print what would happen, copy nothing
./reviews/2026-06-07-make-v1-installable.md:896:    14	#   bash packaging/sync.sh --check    # verify committed Codex body matches source; no writes (CI gate)
./reviews/2026-06-07-make-v1-installable.md:904:    22	# Works whether invoked from repo root, from packaging/, or via symlink.
./reviews/2026-06-07-make-v1-installable.md:906:    24	PACKAGING="$SCRIPT_DIR"                        # packaging/
./reviews/2026-06-07-make-v1-installable.md:907:    25	SOURCE="$SCRIPT_DIR/.."                        # skills/ai-writing-suite/
./reviews/2026-06-07-make-v1-installable.md:910:    28	#   Claude → packaging/claude/                       (content at marketplace root)
./reviews/2026-06-07-make-v1-installable.md:911:    29	#   Codex  → packaging/codex/plugins/ai-writing-suite/ (content inside the plugin;
./reviews/2026-06-07-make-v1-installable.md:963:    81	# directory name differs (.claude-plugin vs .codex-plugin).
./reviews/2026-06-07-make-v1-installable.md:983:   101	  # We only wipe the content dirs, never the manifest dir (.claude-plugin /
./reviews/2026-06-07-make-v1-installable.md:984:   102	  # .codex-plugin) because those contain hand-maintained manifests.
./reviews/2026-06-07-make-v1-installable.md:1012:   130	# and diffs, excluding the hand-maintained .codex-plugin manifest.
./reviews/2026-06-07-make-v1-installable.md:1023:   141	  if diff -r --exclude=.codex-plugin "$TMP" "$CODEX_TARGET" >/dev/null 2>&1; then
./reviews/2026-06-07-make-v1-installable.md:1027:   145	    log "DRIFT: committed Codex body is STALE vs source. Run 'bash packaging/sync.sh' and commit."
./reviews/2026-06-07-make-v1-installable.md:1028:   146	    diff -r --exclude=.codex-plugin "$TMP" "$CODEX_TARGET" | sed 's/^/  /' || true
./reviews/2026-06-07-make-v1-installable.md:1064:   182	  check_manifest_version "$CLAUDE_TARGET/.claude-plugin/plugin.json" "claude"
./reviews/2026-06-07-make-v1-installable.md:1065:   183	  check_manifest_version "$CODEX_TARGET/.codex-plugin/plugin.json"   "codex"
./reviews/2026-06-07-make-v1-installable.md:1066:   184	  # Note: $CODEX_TARGET now points at packaging/codex/plugins/ai-writing-suite/,
./reviews/2026-06-07-make-v1-installable.md:1079:     7	# Generated suite packages — regenerate with: bash skills/ai-writing-suite/packaging/sync.sh
./reviews/2026-06-07-make-v1-installable.md:1081:     9	skills/ai-writing-suite/packaging/claude/*
./reviews/2026-06-07-make-v1-installable.md:1082:    10	!skills/ai-writing-suite/packaging/claude/.claude-plugin
./reviews/2026-06-07-make-v1-installable.md:1083:    11	# Codex marketplace: the marketplace manifest is hand-maintained; the plugin BODY
./reviews/2026-06-07-make-v1-installable.md:1086:    14	# generated from the source tree by sync.sh — keep it in sync (sync.sh --check guards
./reviews/2026-06-07-make-v1-installable.md:1088:    16	skills/ai-writing-suite/packaging/codex/*
./reviews/2026-06-07-make-v1-installable.md:1089:    17	!skills/ai-writing-suite/packaging/codex/.agents
./reviews/2026-06-07-make-v1-installable.md:1090:    18	!skills/ai-writing-suite/packaging/codex/plugins
./reviews/2026-06-07-make-v1-installable.md:1091:    19	skills/ai-writing-suite/packaging/codex/plugins/*
./reviews/2026-06-07-make-v1-installable.md:1092:    20	!skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite
./reviews/2026-06-07-make-v1-installable.md:1128:    34	One source of truth (`skills/ai-writing-suite/`) published to three hosts.
./reviews/2026-06-07-make-v1-installable.md:1133:    39	claude plugin marketplace add surahli123/ai-writing-suite
./reviews/2026-06-07-make-v1-installable.md:1134:    40	claude plugin install ai-writing-suite@ai-writing-suite
./reviews/2026-06-07-make-v1-installable.md:1143:    49	codex plugin marketplace add surahli123/ai-writing-suite --sparse skills/ai-writing-suite/packaging/codex
./reviews/2026-06-07-make-v1-installable.md:1144:    50	codex plugin add ai-writing-suite@ai-writing-suite
./reviews/2026-06-07-make-v1-installable.md:1147:    53	The `--sparse` path points Codex at the marketplace directory committed inside the repo.
./reviews/2026-06-07-make-v1-installable.md:1151:    57	Cursor reads Anthropic-format **Agent Skills** from `.cursor/skills/` — there is no marketplace, so
./reviews/2026-06-07-make-v1-installable.md:1156:    62	cp -R ai-writing-suite/skills/ai-writing-suite ~/.cursor/skills/ai-writing-suite
./reviews/2026-06-07-make-v1-installable.md:1165:    71	.claude-plugin/marketplace.json    # Claude marketplace (points at the source tree)
./reviews/2026-06-07-make-v1-installable.md:1169:    75	    .claude-plugin/plugin.json     # Claude plugin manifest
./reviews/2026-06-07-make-v1-installable.md:1173:    79	    packaging/                     # sync.sh + Codex marketplace (codex/)
./reviews/2026-06-07-make-v1-installable.md:1181:    87	preserved and credited in [`skills/ai-writing-suite/NOTICE.md`](skills/ai-writing-suite/NOTICE.md).
./reviews/2026-06-07-make-v1-installable.md:1183:### skills/ai-writing-suite/packaging/README.md
./reviews/2026-06-07-make-v1-installable.md:1188:     5	All skill logic lives under `skills/ai-writing-suite/` (one level up from this
./reviews/2026-06-07-make-v1-installable.md:1189:     6	directory). Everything inside `packaging/claude/` and `packaging/codex/` is
./reviews/2026-06-07-make-v1-installable.md:1190:     7	**generated** by `sync.sh`. Do not hand-edit generated packages.
./reviews/2026-06-07-make-v1-installable.md:1193:    10	skills/ai-writing-suite/   ← SOURCE (edit here)
./reviews/2026-06-07-make-v1-installable.md:1198:    15	    packaging/
./reviews/2026-06-07-make-v1-installable.md:1199:    16	        sync.sh            ← assembler
./reviews/2026-06-07-make-v1-installable.md:1201:    18	        codex/             ← Codex marketplace (manual manifests; generated
./reviews/2026-06-07-make-v1-installable.md:1205:    22	> **WARNING: Do NOT hand-edit files inside `packaging/claude/` or
./reviews/2026-06-07-make-v1-installable.md:1206:    23	> `packaging/codex/`. Those directories are wiped and regenerated every time
./reviews/2026-06-07-make-v1-installable.md:1207:    24	> `sync.sh` runs. Any manual edits will be silently lost. Edit the source and
./reviews/2026-06-07-make-v1-installable.md:1218:    35	bash packaging/sync.sh            # from repo root or from packaging/
./reviews/2026-06-07-make-v1-installable.md:1219:    36	bash packaging/sync.sh --dry-run  # preview what would be copied, nothing written
./reviews/2026-06-07-make-v1-installable.md:1225:    42	- Claude content root → `packaging/claude/` (content sits at the marketplace root).
./reviews/2026-06-07-make-v1-installable.md:1226:    43	- Codex content root → `packaging/codex/plugins/ai-writing-suite/` (content sits
./reviews/2026-06-07-make-v1-installable.md:1227:    44	  inside the plugin; `packaging/codex/` itself is the *marketplace* root, not the
./reviews/2026-06-07-make-v1-installable.md:1244:    61	- Claude: `packaging/claude/.claude-plugin/`.
./reviews/2026-06-07-make-v1-installable.md:1245:    62	- Codex: `packaging/codex/.agents/plugins/marketplace.json` (marketplace manifest)
./reviews/2026-06-07-make-v1-installable.md:1246:    63	  and `packaging/codex/plugins/ai-writing-suite/.codex-plugin/plugin.json` (plugin
./reviews/2026-06-07-make-v1-installable.md:1250:    67	Idempotent: running sync.sh twice produces the same result.
./reviews/2026-06-07-make-v1-installable.md:1258:    75	### Claude (`packaging/claude/`)
./reviews/2026-06-07-make-v1-installable.md:1262:    79	├── .claude-plugin/
./reviews/2026-06-07-make-v1-installable.md:1264:    81	│   └── marketplace.json   # Claude marketplace listing (maintained manually)
./reviews/2026-06-07-make-v1-installable.md:1279:    96	`code.claude.com/docs/en/plugins-reference.md` + `/plugin-marketplaces.md`.
./reviews/2026-06-07-make-v1-installable.md:1280:    97	`.claude-plugin/plugin.json` — only `name` is required; `description`, `version`,
./reviews/2026-06-07-make-v1-installable.md:1285:   102	default). `.claude-plugin/marketplace.json` is correct as-is (`name` + `owner` +
./reviews/2026-06-07-make-v1-installable.md:1289:   106	### Codex (`packaging/codex/`)
./reviews/2026-06-07-make-v1-installable.md:1291:   108	`packaging/codex/` is a **marketplace** that contains one **plugin**. The
./reviews/2026-06-07-make-v1-installable.md:1292:   109	marketplace manifest lives at the root; the plugin (manifest + all generated
./reviews/2026-06-07-make-v1-installable.md:1296:   113	codex/                                       # marketplace root
./reviews/2026-06-07-make-v1-installable.md:1297:   114	├── .agents/plugins/marketplace.json         # marketplace manifest (maintained manually)
./reviews/2026-06-07-make-v1-installable.md:1299:   116	    ├── .codex-plugin/plugin.json            # plugin manifest (maintained manually)
./reviews/2026-06-07-make-v1-installable.md:1314:   131	The `codex` CLI (codex-cli 0.137.0) uses a **marketplace** model:
./reviews/2026-06-07-make-v1-installable.md:1315:   132	`codex plugin marketplace add <local|owner/repo|git-url>` → `codex plugin add <plugin>`.
./reviews/2026-06-07-make-v1-installable.md:1316:   133	The earlier bare-`.codex-plugin/plugin.json`-at-root layout was rejected with:
./reviews/2026-06-07-make-v1-installable.md:1318:   135	    Error: invalid marketplace file .../packaging/codex: marketplace root does not
./reviews/2026-06-07-make-v1-installable.md:1321:   138	The layout above is the verified-conformant shape, matching a working marketplace
./reviews/2026-06-07-make-v1-installable.md:1322:   139	(`~/.codex/.tmp/marketplaces/claude-plugin-codex`) and the `nature-skills` repo:
./reviews/2026-06-07-make-v1-installable.md:1324:   141	    <marketplace-root>/
./reviews/2026-06-07-make-v1-installable.md:1325:   142	    ├── .agents/plugins/marketplace.json   # MARKETPLACE manifest (REQUIRED)
./reviews/2026-06-07-make-v1-installable.md:1327:   144	        ├── .codex-plugin/plugin.json      # plugin manifest
./reviews/2026-06-07-make-v1-installable.md:1331:   148	Two manifests are maintained by hand (sync.sh never touches them):
./reviews/2026-06-07-make-v1-installable.md:1333:   150	- `codex/.agents/plugins/marketplace.json` — marketplace manifest. Shape:
./reviews/2026-06-07-make-v1-installable.md:1338:   155	- `codex/plugins/ai-writing-suite/.codex-plugin/plugin.json` — plugin manifest.
./reviews/2026-06-07-make-v1-installable.md:1345:   162	`README.md`, `CHANGELOG.md`) lands under `plugins/ai-writing-suite/` via sync.sh.
./reviews/2026-06-07-make-v1-installable.md:1346:   163	Add to a local marketplace with:
./reviews/2026-06-07-make-v1-installable.md:1347:   164	`codex plugin marketplace add ./skills/ai-writing-suite/packaging/codex`.
./reviews/2026-06-07-make-v1-installable.md:1357:   174	| `claude/.claude-plugin/plugin.json` | Claude plugin identity | version bump, metadata change |
./reviews/2026-06-07-make-v1-installable.md:1358:   175	| `claude/.claude-plugin/marketplace.json` | Claude marketplace listing | name/description/category change |
./reviews/2026-06-07-make-v1-installable.md:1359:   176	| `codex/.agents/plugins/marketplace.json` | Codex marketplace listing | name/category/plugin-path change |
./reviews/2026-06-07-make-v1-installable.md:1360:   177	| `codex/plugins/ai-writing-suite/.codex-plugin/plugin.json` | Codex plugin identity | version bump, metadata change |
./reviews/2026-06-07-make-v1-installable.md:1364:   181	2. Update `"version"` in the two `plugin.json` files above (the marketplace
./reviews/2026-06-07-make-v1-installable.md:1366:   183	3. Run `bash packaging/sync.sh` — it will confirm version parity.
./reviews/2026-06-07-make-v1-installable.md:1378:   195	Cursor has no plugin marketplace; distribution is "copy the skill tree into a
./reviews/2026-06-07-make-v1-installable.md:1380:   197	a user copies `skills/ai-writing-suite/` into `~/.cursor/skills/ai-writing-suite/`
./reviews/2026-06-07-make-v1-installable.md:1388:   205	RovoDev packaging is deferred to v2. When added it follows the same pattern:
./reviews/2026-06-07-make-v1-installable.md:1389:   206	sync.sh gains a new `sync_target` call; generated content is never hand-edited.
./reviews/2026-06-07-make-v1-installable.md:1391:### skills/ai-writing-suite/packaging/codex/.agents/plugins/marketplace.json
./reviews/2026-06-07-make-v1-installable.md:1413:### skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/.codex-plugin/plugin.json
./reviews/2026-06-07-make-v1-installable.md:1434:### skills/ai-writing-suite/SKILL.md
./reviews/2026-06-07-make-v1-installable.md:1518:The generated Codex body is tracked despite the prior ignore, and its marketplace path resolves relative to `packaging/codex`. The higher-risk area is the guardrail: it depends on non-POSIX `diff --exclude` while the repo explicitly targets macOS developer workflows.
./reviews/2026-06-07-make-v1-installable.md:1534:/bin/zsh -lc "git show main:.gitignore | nl -ba | sed -n '1,80p'; printf '\\nHEAD tracked ignore check:\\n'; git check-ignore -v skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/SKILL.md skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/.codex-plugin/plugin.json skills/ai-writing-suite/packaging/codex/plugins/other/SKILL.md || true" in /Users/surahli/Documents/ai-writing-suite
./reviews/2026-06-07-make-v1-installable.md:1536:/bin/zsh -lc "git diff main..HEAD -- skills/ai-writing-suite/packaging/codex/.agents/plugins/marketplace.json skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/.codex-plugin/plugin.json skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/SKILL.md skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/README.md | sed -n '1,260p'" in /Users/surahli/Documents/ai-writing-suite
./reviews/2026-06-07-make-v1-installable.md:1538:/bin/zsh -lc "find skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite -type f | sed 's#skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/##' | sort > /tmp/codex_body_files.txt 2>/dev/null || true; find skills/ai-writing-suite -path 'skills/ai-writing-suite/packaging' -prune -o -type f -print | sed 's#skills/ai-writing-suite/##' | sort > /tmp/source_files.txt 2>/dev/null || true; printf 'extra in source not in codex body (excluding .claude-plugin, evals, packaging):\\n'; comm -23 /tmp/source_files.txt /tmp/codex_body_files.txt | sed -n '1,80p'; printf '\\nextra in codex body not in source:\\n'; comm -13 /tmp/source_files.txt /tmp/codex_body_files.txt | sed -n '1,80p'" in /Users/surahli/Documents/ai-writing-suite
./reviews/2026-06-07-make-v1-installable.md:1543:extra in source not in codex body (excluding .claude-plugin, evals, packaging):
./reviews/2026-06-07-make-v1-installable.md:1560:diff --git a/skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/README.md b/skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/README.md
./reviews/2026-06-07-make-v1-installable.md:1564:+++ b/skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/README.md
./reviews/2026-06-07-make-v1-installable.md:1710:+cp -r skills/ai-writing-suite ~/.claude/skills/ai-writing-suite
./reviews/2026-06-07-make-v1-installable.md:1719:+cp -r skills/ai-writing-suite ~/.codex/skills/ai-writing-suite
./reviews/2026-06-07-make-v1-installable.md:1726:+See `packaging/` for surface-specific installation instructions (coming in v2).
./reviews/2026-06-07-make-v1-installable.md:1779:+2. **conorbronsdon/avoid-ai-writing** — JS detector, CATEGORIES taxonomy, packaging patterns.
./reviews/2026-06-07-make-v1-installable.md:1806:diff --git a/skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/SKILL.md b/skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/SKILL.md
./reviews/2026-06-07-make-v1-installable.md:1810:+++ b/skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/SKILL.md
./reviews/2026-06-07-make-v1-installable.md:1829:     7	# Generated suite packages — regenerate with: bash skills/ai-writing-suite/packaging/sync.sh
./reviews/2026-06-07-make-v1-installable.md:1831:     9	skills/ai-writing-suite/packaging/claude/*
./reviews/2026-06-07-make-v1-installable.md:1832:    10	!skills/ai-writing-suite/packaging/claude/.claude-plugin
./reviews/2026-06-07-make-v1-installable.md:1833:    11	# Codex marketplace: keep hand-maintained manifests, ignore generated content
./reviews/2026-06-07-make-v1-installable.md:1834:    12	skills/ai-writing-suite/packaging/codex/*
./reviews/2026-06-07-make-v1-installable.md:1835:    13	!skills/ai-writing-suite/packaging/codex/.agents
./reviews/2026-06-07-make-v1-installable.md:1836:    14	!skills/ai-writing-suite/packaging/codex/plugins
./reviews/2026-06-07-make-v1-installable.md:1837:    15	skills/ai-writing-suite/packaging/codex/plugins/*
./reviews/2026-06-07-make-v1-installable.md:1838:    16	!skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite
./reviews/2026-06-07-make-v1-installable.md:1839:    17	skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/*
./reviews/2026-06-07-make-v1-installable.md:1840:    18	!skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/.codex-plugin
./reviews/2026-06-07-make-v1-installable.md:1844:.gitignore:19:skills/ai-writing-suite/packaging/codex/plugins/*	skills/ai-writing-suite/packaging/codex/plugins/other/SKILL.md
./reviews/2026-06-07-make-v1-installable.md:1864:web search: site:docs.anthropic.com Claude Code plugins marketplace add install plugin source relative path
./reviews/2026-06-07-make-v1-installable.md:1869:web search: https://code.claude.com/docs/en/plugin-marketplaces.md
./reviews/2026-06-07-make-v1-installable.md:1892:/bin/zsh -lc "codex plugin marketplace add --help 2>&1 | sed -n '1,220p'; printf '\\n--- add help ---\\n'; codex plugin add --help 2>&1 | sed -n '1,220p'; printf '\\n--- list help ---\\n'; codex plugin marketplace --help 2>&1 | sed -n '1,220p'" in /Users/surahli/Documents/ai-writing-suite
./reviews/2026-06-07-make-v1-installable.md:1896:/bin/zsh -lc "claude plugin marketplace add --help 2>&1 | sed -n '1,220p'; printf '\\n--- install help ---\\n'; claude plugin install --help 2>&1 | sed -n '1,220p'; printf '\\n--- validate help ---\\n'; claude plugin validate --help 2>&1 | sed -n '1,160p'" in /Users/surahli/Documents/ai-writing-suite
./reviews/2026-06-07-make-v1-installable.md:1904:Add a local or Git marketplace to the configured marketplace sources
./reviews/2026-06-07-make-v1-installable.md:1906:Usage: codex plugin marketplace add [OPTIONS] <SOURCE>
./reviews/2026-06-07-make-v1-installable.md:1922:          Git ref to fetch for Git marketplace sources
./reviews/2026-06-07-make-v1-installable.md:1927:      --sparse <PATH>
./reviews/2026-06-07-make-v1-installable.md:1928:          Sparse checkout path for Git marketplace sources. Can be repeated
./reviews/2026-06-07-make-v1-installable.md:1937:  codex plugin marketplace add ./path/to/marketplace
./reviews/2026-06-07-make-v1-installable.md:1938:  codex plugin marketplace add owner/repo --ref main
./reviews/2026-06-07-make-v1-installable.md:1939:  codex plugin marketplace add https://github.com/owner/repo --sparse plugins/foo
./reviews/2026-06-07-make-v1-installable.md:1943:Install a plugin from a configured marketplace snapshot.
./reviews/2026-06-07-make-v1-installable.md:1945:Pass either `PLUGIN@MARKETPLACE` or pass `PLUGIN` with `--marketplace MARKETPLACE`.
./reviews/2026-06-07-make-v1-installable.md:1947:Usage: codex plugin add [OPTIONS] <PLUGIN[@MARKETPLACE]>
./reviews/2026-06-07-make-v1-installable.md:1951:          Plugin selector to install: either PLUGIN@MARKETPLACE or PLUGIN with --marketplace
./reviews/2026-06-07-make-v1-installable.md:1962:  -m, --marketplace <MARKETPLACE>
./reviews/2026-06-07-make-v1-installable.md:1963:          Configured marketplace name to use when PLUGIN does not include @MARKETPLACE
./reviews/2026-06-07-make-v1-installable.md:1975:  codex plugin add sample@debug
./reviews/2026-06-07-make-v1-installable.md:1976:  codex plugin add sample --marketplace debug
./reviews/2026-06-07-make-v1-installable.md:1980:Add, list, upgrade, or remove configured plugin marketplaces
./reviews/2026-06-07-make-v1-installable.md:1982:Usage: codex plugin marketplace [OPTIONS] <COMMAND>
./reviews/2026-06-07-make-v1-installable.md:1985:  add      Add a local or Git marketplace to the configured marketplace sources
./reviews/2026-06-07-make-v1-installable.md:1986:  list     List plugin marketplaces Codex is currently considering and their roots
./reviews/2026-06-07-make-v1-installable.md:1987:  upgrade  Refresh configured Git marketplace snapshots
./reviews/2026-06-07-make-v1-installable.md:1988:  remove   Remove a configured marketplace source by name
./reviews/2026-06-07-make-v1-installable.md:2037:Usage: claude plugin marketplace add [options] <source>
./reviews/2026-06-07-make-v1-installable.md:2039:Add a marketplace from a URL, path, or GitHub repo
./reviews/2026-06-07-make-v1-installable.md:2043:  --scope <scope>      Where to declare the marketplace: user (default),
./reviews/2026-06-07-make-v1-installable.md:2045:  --sparse <paths...>  Limit checkout to specific directories via git
./reviews/2026-06-07-make-v1-installable.md:2046:                       sparse-checkout (for monorepos). Example: --sparse
./reviews/2026-06-07-make-v1-installable.md:2047:                       .claude-plugin plugins
./reviews/2026-06-07-make-v1-installable.md:2050:Usage: claude plugin install|i [options] <plugin>
./reviews/2026-06-07-make-v1-installable.md:2052:Install a plugin from available marketplaces (use plugin@marketplace for
./reviews/2026-06-07-make-v1-installable.md:2053:specific marketplace)
./reviews/2026-06-07-make-v1-installable.md:2067:Validate a plugin or marketplace manifest
./reviews/2026-06-07-make-v1-installable.md:2080:The local CLI help confirms the documented command shapes for both hosts. It also exposes one README risk: Codex sparse checkout syntax is valid, but the install claim still depends on the marketplace manifest inside that sparse root being fetched, not on the repo root.
./reviews/2026-06-07-make-v1-installable.md:2111:/bin/zsh -lc "for f in skills/ai-writing-suite/packaging/codex/.agents/plugins/marketplace.json skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/.codex-plugin/plugin.json .claude-plugin/marketplace.json skills/ai-writing-suite/.claude-plugin/plugin.json; do printf '\\n### %s\\n' \""'$f"; python3 -m json.tool "$f" >/dev/null && echo valid-json || echo invalid-json; done' in /Users/surahli/Documents/ai-writing-suite
./reviews/2026-06-07-make-v1-installable.md:2113:/bin/zsh -lc 'codex plugin marketplace add ./skills/ai-writing-suite/packaging/codex --help >/dev/null; true' in /Users/surahli/Documents/ai-writing-suite
./reviews/2026-06-07-make-v1-installable.md:2119:/bin/zsh -lc "claude plugin validate skills/ai-writing-suite --strict 2>&1 | sed -n '1,220p'; printf 'exit=%s\\n' "'${pipestatus[1]:-${PIPESTATUS[1]}}' in /Users/surahli/Documents/ai-writing-suite
./reviews/2026-06-07-make-v1-installable.md:2124:### skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/.codex-plugin/plugin.json
./reviews/2026-06-07-make-v1-installable.md:2127:### .claude-plugin/marketplace.json
./reviews/2026-06-07-make-v1-installable.md:2130:### skills/ai-writing-suite/.claude-plugin/plugin.json
./reviews/2026-06-07-make-v1-installable.md:2142:Validating marketplace manifest: /Users/surahli/Documents/ai-writing-suite/.claude-plugin/marketplace.json
./reviews/2026-06-07-make-v1-installable.md:2148:Validating plugin manifest: /Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/.claude-plugin/plugin.json
./reviews/2026-06-07-make-v1-installable.md:2176:  add          Install a plugin from a configured marketplace snapshot
./reviews/2026-06-07-make-v1-installable.md:2177:  list         List plugins available from configured marketplace snapshots
./reviews/2026-06-07-make-v1-installable.md:2178:  marketplace  Add, list, upgrade, or remove configured plugin marketplaces
./reviews/2026-06-07-make-v1-installable.md:2219:Claude strict validation passes for both the repo-root marketplace and source-tree plugin manifest, which is evidence against a merge-blocking Claude path bug. It does not prove sub-skill runtime dispatch, so I’m treating that as a defended-but-still-testable assumption rather than a blocker.
./reviews/2026-06-07-make-v1-installable.md:2230:/bin/zsh -lc "rg -n \"plugin marketplace|plugin.json|marketplace.json|skills\" /Users/surahli/.claude /Users/surahli/.codex -g '*.md' -g '*.json' -g '*.toml' 2>/dev/null | sed -n '1,220p'" in /Users/surahli/Documents/ai-writing-suite
./reviews/2026-06-07-make-v1-installable.md:2232:/bin/zsh -lc "rg -n \"name: comms-|name: voice|version:\" skills/ai-writing-suite skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite -g 'SKILL.md' | sed -n '1,220p'" in /Users/surahli/Documents/ai-writing-suite
./reviews/2026-06-07-make-v1-installable.md:2244:skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/skills/comms-qa/SKILL.md:2:name: comms-qa
./reviews/2026-06-07-make-v1-installable.md:2245:skills/ai-writing-suite/skills/comms-polish/SKILL.md:2:name: comms-polish
./reviews/2026-06-07-make-v1-installable.md:2246:skills/ai-writing-suite/skills/comms-draft/SKILL.md:2:name: comms-draft
./reviews/2026-06-07-make-v1-installable.md:2247:skills/ai-writing-suite/skills/voice-onboard/SKILL.md:2:name: voice-onboard
./reviews/2026-06-07-make-v1-installable.md:2248:skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/skills/voice-onboard/SKILL.md:2:name: voice-onboard
./reviews/2026-06-07-make-v1-installable.md:2249:skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/skills/voice-onboard/SKILL.md:2:name: voice-onboard
./reviews/2026-06-07-make-v1-installable.md:2250:skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/skills/comms-polish/SKILL.md:2:name: comms-polish
./reviews/2026-06-07-make-v1-installable.md:2251:skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/skills/comms-qa/SKILL.md:2:name: comms-qa
./reviews/2026-06-07-make-v1-installable.md:2252:skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/skills/comms-draft/SKILL.md:2:name: comms-draft
./reviews/2026-06-07-make-v1-installable.md:2253:skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/skills/comms-polish/SKILL.md:2:name: comms-polish
./reviews/2026-06-07-make-v1-installable.md:2254:skills/ai-writing-suite/skills/comms-qa/SKILL.md:2:name: comms-qa
./reviews/2026-06-07-make-v1-installable.md:2255:skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/skills/comms-draft/SKILL.md:2:name: comms-draft
./reviews/2026-06-07-make-v1-installable.md:2264:/Users/surahli/.codex/memories/memory_summary.md:39:- For Codex skill packaging, check the real installed surface under `~/.codex/skills` first; local Codex skills are folders with `SKILL.md` plus optional `references/`, so `.codex-plugin/plugin.json` may be speculative. [chronicle memory]
./reviews/2026-06-07-make-v1-installable.md:2265:/Users/surahli/.codex/memories/memory_summary.md:87:- Layer 3 eval/docs/packaging + publish-surface review: Python detector now, feat/ai-writing-suite-v1, 17/17 detector, 6/6 fixtures, packaging/codex/.codex-plugin/plugin.json
./reviews/2026-06-07-make-v1-installable.md:2267:/Users/surahli/.codex/memories/memory_summary.md:184:  - desc: Covers keeping tutorial packaging inside the existing repo, plus the later Codex App plugin inspection; cwd=ds-skills-teaching / Codex tutorial packaging workflow
./reviews/2026-06-07-make-v1-installable.md:2270:/Users/surahli/.codex/memories/memory_summary.md:192:  - desc: Covers packaging `goal-forge` into a public skill/repo and the backup-first resident-budget reduction plan for local Claude config; cwd=/Users/surahli/Documents/projects/personal-productivity-skills and /Users/surahli/Documents/projects/skill-improvement
./reviews/2026-06-07-make-v1-installable.md:2387:/Users/surahli/.codex/memories/skills/codex-skill-install-scope-check/SKILL.md:23:- plugin installs that belong to the Codex plugin marketplace flow
./reviews/2026-06-07-make-v1-installable.md:2429:/Users/surahli/.codex/compound-engineering/legacy-backup/2026-04-26T05-40-13-471Z/skills/ce-update/SKILL.md:29:`~/.claude/plugins/cache/<marketplace>/compound-engineering/<version>/skills/ce-update`,
./reviews/2026-06-07-make-v1-installable.md:2430:/Users/surahli/.codex/compound-engineering/legacy-backup/2026-04-26T05-40-13-471Z/skills/ce-update/SKILL.md:32:The upstream version comes from `plugins/compound-engineering/.claude-plugin/plugin.json`
./reviews/2026-06-07-make-v1-installable.md:2431:/Users/surahli/.codex/compound-engineering/legacy-backup/2026-04-26T05-40-13-471Z/skills/ce-update/SKILL.md:42:!`version=$(gh api repos/EveryInc/compound-engineering-plugin/contents/plugins/compound-engineering/.claude-plugin/plugin.json --jq '.content | @base64d | fromjson | .version' 2>/dev/null) && [ -n "$version" ] && echo "$version" || echo '__CE_UPDATE_VERSION_FAILED__'`
./reviews/2026-06-07-make-v1-installable.md:2453:/Users/surahli/.codex/superpowers/README.md:29:**Note:** Installation differs by platform. Claude Code or Cursor have built-in plugin marketplaces. Codex and OpenCode require manual setup.
./reviews/2026-06-07-make-v1-installable.md:2454:/Users/surahli/.codex/superpowers/README.md:37:/plugin marketplace add obra/superpowers-marketplace
./reviews/2026-06-07-make-v1-installable.md:2502:/bin/zsh -lc "nl -ba skills/ai-writing-suite/README.md | sed -n '1,260p'" in /Users/surahli/Documents/ai-writing-suite
./reviews/2026-06-07-make-v1-installable.md:2648:   145	cp -r skills/ai-writing-suite ~/.claude/skills/ai-writing-suite
./reviews/2026-06-07-make-v1-installable.md:2657:   154	cp -r skills/ai-writing-suite ~/.codex/skills/ai-writing-suite
./reviews/2026-06-07-make-v1-installable.md:2664:   161	See `packaging/` for surface-specific installation instructions (coming in v2).
./reviews/2026-06-07-make-v1-installable.md:2717:   214	2. **conorbronsdon/avoid-ai-writing** — JS detector, CATEGORIES taxonomy, packaging patterns.
./reviews/2026-06-07-make-v1-installable.md:2747:/bin/zsh -lc "nl -ba skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/README.md | sed -n '1,260p'" in /Users/surahli/Documents/ai-writing-suite
./reviews/2026-06-07-make-v1-installable.md:2893:   145	cp -r skills/ai-writing-suite ~/.claude/skills/ai-writing-suite
./reviews/2026-06-07-make-v1-installable.md:2902:   154	cp -r skills/ai-writing-suite ~/.codex/skills/ai-writing-suite
./reviews/2026-06-07-make-v1-installable.md:2909:   161	See `packaging/` for surface-specific installation instructions (coming in v2).
./reviews/2026-06-07-make-v1-installable.md:2962:   214	2. **conorbronsdon/avoid-ai-writing** — JS detector, CATEGORIES taxonomy, packaging patterns.
./reviews/2026-06-07-make-v1-installable.md:2994:/bin/zsh -lc "find skills/ai-writing-suite/evals -maxdepth 3 -type f | sort | nl -ba | sed -n '1,120p'; printf '\\ntracked evals?\\n'; git ls-files skills/ai-writing-suite/evals | sort | sed -n '1,120p'" in /Users/surahli/Documents/ai-writing-suite
./reviews/2026-06-07-make-v1-installable.md:2997:/bin/zsh -lc "git ls-files skills/ai-writing-suite/packaging/claude skills/ai-writing-suite/packaging/codex | sed -n '1,120p'" in /Users/surahli/Documents/ai-writing-suite
./reviews/2026-06-07-make-v1-installable.md:3000:skills/ai-writing-suite/packaging/claude/.claude-plugin/marketplace.json
./reviews/2026-06-07-make-v1-installable.md:3001:skills/ai-writing-suite/packaging/claude/.claude-plugin/plugin.json
./reviews/2026-06-07-make-v1-installable.md:3002:skills/ai-writing-suite/packaging/codex/.agents/plugins/marketplace.json
./reviews/2026-06-07-make-v1-installable.md:3003:skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/.codex-plugin/plugin.json
./reviews/2026-06-07-make-v1-installable.md:3004:skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/CHANGELOG.md
./reviews/2026-06-07-make-v1-installable.md:3005:skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/LICENSE
./reviews/2026-06-07-make-v1-installable.md:3006:skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/NOTICE.md
./reviews/2026-06-07-make-v1-installable.md:3007:skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/README.md
./reviews/2026-06-07-make-v1-installable.md:3008:skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/SKILL.md
./reviews/2026-06-07-make-v1-installable.md:3009:skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/_shared/host-profile-template.md
./reviews/2026-06-07-make-v1-installable.md:3010:skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/_shared/knowledge/.gitkeep
./reviews/2026-06-07-make-v1-installable.md:3011:skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/_shared/knowledge/INDEX.md
./reviews/2026-06-07-make-v1-installable.md:3012:skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/_shared/knowledge/README.md
./reviews/2026-06-07-make-v1-installable.md:3013:skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md
./reviews/2026-06-07-make-v1-installable.md:3014:skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/_shared/knowledge/audience.md
./reviews/2026-06-07-make-v1-installable.md:3015:skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/_shared/knowledge/clarity.md
./reviews/2026-06-07-make-v1-installable.md:3016:skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/_shared/knowledge/revision.md
./reviews/2026-06-07-make-v1-installable.md:3017:skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/_shared/knowledge/structure.md
./reviews/2026-06-07-make-v1-installable.md:3018:skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/_shared/knowledge/tone.md
./reviews/2026-06-07-make-v1-installable.md:3019:skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/_shared/learned-rules.md
./reviews/2026-06-07-make-v1-installable.md:3020:skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/_shared/patterns/00-index.md
./reviews/2026-06-07-make-v1-installable.md:3021:skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/_shared/patterns/communication-artifacts.md
./reviews/2026-06-07-make-v1-installable.md:3022:skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/_shared/patterns/hedging-filler.md
./reviews/2026-06-07-make-v1-installable.md:3023:skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/_shared/patterns/lexical-tells.md
./reviews/2026-06-07-make-v1-installable.md:3024:skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/_shared/patterns/punctuation-formatting.md
./reviews/2026-06-07-make-v1-installable.md:3025:skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/_shared/patterns/rhythm-stylometric.md
./reviews/2026-06-07-make-v1-installable.md:3026:skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/_shared/patterns/significance-attribution.md
./reviews/2026-06-07-make-v1-installable.md:3027:skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/_shared/patterns/structural-tells.md
./reviews/2026-06-07-make-v1-installable.md:3028:skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/_shared/self-improvement.md
./reviews/2026-06-07-make-v1-installable.md:3029:skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/_shared/voice-profile.md
./reviews/2026-06-07-make-v1-installable.md:3030:skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/skills/comms-draft/SKILL.md
./reviews/2026-06-07-make-v1-installable.md:3031:skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/skills/comms-polish/SKILL.md
./reviews/2026-06-07-make-v1-installable.md:3032:skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/skills/comms-polish/references/final-pass-checklist.md
./reviews/2026-06-07-make-v1-installable.md:3033:skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/skills/comms-polish/references/scenario-presets.md
./reviews/2026-06-07-make-v1-installable.md:3034:skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/skills/comms-qa/SKILL.md
./reviews/2026-06-07-make-v1-installable.md:3035:skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/skills/voice-onboard/SKILL.md
./reviews/2026-06-07-make-v1-installable.md:3039:skills/ai-writing-suite/evals/README.md
./reviews/2026-06-07-make-v1-installable.md:3040:skills/ai-writing-suite/evals/detector/__init__.py
./reviews/2026-06-07-make-v1-installable.md:3041:skills/ai-writing-suite/evals/detector/cli.py
./reviews/2026-06-07-make-v1-installable.md:3042:skills/ai-writing-suite/evals/detector/detector.py
./reviews/2026-06-07-make-v1-installable.md:3043:skills/ai-writing-suite/evals/detector/patterns.py
./reviews/2026-06-07-make-v1-installable.md:3044:skills/ai-writing-suite/evals/detector/test_detector.py
./reviews/2026-06-07-make-v1-installable.md:3045:skills/ai-writing-suite/evals/fixtures/__init__.py
./reviews/2026-06-07-make-v1-installable.md:3046:skills/ai-writing-suite/evals/fixtures/fixtures.json
./reviews/2026-06-07-make-v1-installable.md:3047:skills/ai-writing-suite/evals/fixtures/rubric.md
./reviews/2026-06-07-make-v1-installable.md:3048:skills/ai-writing-suite/evals/fixtures/run_fixtures.py
./reviews/2026-06-07-make-v1-installable.md:3049:skills/ai-writing-suite/evals/fixtures/test_fixtures.py
./reviews/2026-06-07-make-v1-installable.md:3050:skills/ai-writing-suite/evals/smoke_test.py
./reviews/2026-06-07-make-v1-installable.md:3058:One concrete package hygiene issue is visible: Claude points at the tracked source tree, and that tree now includes `packaging/codex/` with the full generated Codex body. Even if Claude discovers only root `skills/`, this still ships packaging internals to Claude users unless the host excludes them.
./reviews/2026-06-07-make-v1-installable.md:3117:/bin/zsh -lc "mkdir -p ./.does-not-exist-for-review 2>/dev/null || true; diff -r --exclude=.codex-plugin skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite >/dev/null; printf 'diff-exit=%s\\n' "'$?' in /Users/surahli/Documents/ai-writing-suite
./reviews/2026-06-07-make-v1-installable.md:3123:/bin/zsh -lc "diff -r --exclude=.codex-plugin skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite 2>&1 | sed -n '1,40p'" in /Users/surahli/Documents/ai-writing-suite
./reviews/2026-06-07-make-v1-installable.md:3127:/bin/zsh -lc "git ls-files skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/evals skills/ai-writing-suite/evals | sed -n '1,160p'" in /Users/surahli/Documents/ai-writing-suite
./reviews/2026-06-07-make-v1-installable.md:3130:skills/ai-writing-suite/evals/README.md
./reviews/2026-06-07-make-v1-installable.md:3131:skills/ai-writing-suite/evals/detector/__init__.py
./reviews/2026-06-07-make-v1-installable.md:3132:skills/ai-writing-suite/evals/detector/cli.py
./reviews/2026-06-07-make-v1-installable.md:3133:skills/ai-writing-suite/evals/detector/detector.py
./reviews/2026-06-07-make-v1-installable.md:3134:skills/ai-writing-suite/evals/detector/patterns.py
./reviews/2026-06-07-make-v1-installable.md:3135:skills/ai-writing-suite/evals/detector/test_detector.py
./reviews/2026-06-07-make-v1-installable.md:3136:skills/ai-writing-suite/evals/fixtures/__init__.py
./reviews/2026-06-07-make-v1-installable.md:3137:skills/ai-writing-suite/evals/fixtures/fixtures.json
./reviews/2026-06-07-make-v1-installable.md:3138:skills/ai-writing-suite/evals/fixtures/rubric.md
./reviews/2026-06-07-make-v1-installable.md:3139:skills/ai-writing-suite/evals/fixtures/run_fixtures.py
./reviews/2026-06-07-make-v1-installable.md:3140:skills/ai-writing-suite/evals/fixtures/test_fixtures.py
./reviews/2026-06-07-make-v1-installable.md:3141:skills/ai-writing-suite/evals/smoke_test.py
./reviews/2026-06-07-make-v1-installable.md:3148:skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/NOTICE.md:9: trailing whitespace.
./reviews/2026-06-07-make-v1-installable.md:3150:skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/NOTICE.md:10: trailing whitespace.
./reviews/2026-06-07-make-v1-installable.md:3152:skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/NOTICE.md:11: trailing whitespace.
./reviews/2026-06-07-make-v1-installable.md:3154:skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/NOTICE.md:22: trailing whitespace.
./reviews/2026-06-07-make-v1-installable.md:3156:skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/NOTICE.md:23: trailing whitespace.
./reviews/2026-06-07-make-v1-installable.md:3158:skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/NOTICE.md:24: trailing whitespace.
./reviews/2026-06-07-make-v1-installable.md:3160:skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/NOTICE.md:35: trailing whitespace.
./reviews/2026-06-07-make-v1-installable.md:3162:skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/NOTICE.md:36: trailing whitespace.
./reviews/2026-06-07-make-v1-installable.md:3164:skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/NOTICE.md:37: trailing whitespace.
./reviews/2026-06-07-make-v1-installable.md:3166:skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/NOTICE.md:48: trailing whitespace.
./reviews/2026-06-07-make-v1-installable.md:3168:skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/NOTICE.md:49: trailing whitespace.
./reviews/2026-06-07-make-v1-installable.md:3170:skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/NOTICE.md:50: trailing whitespace.
./reviews/2026-06-07-make-v1-installable.md:3172:skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/NOTICE.md:61: trailing whitespace.
./reviews/2026-06-07-make-v1-installable.md:3174:skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/NOTICE.md:62: trailing whitespace.
./reviews/2026-06-07-make-v1-installable.md:3176:skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/NOTICE.md:63: trailing whitespace.
./reviews/2026-06-07-make-v1-installable.md:3178:skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/NOTICE.md:74: trailing whitespace.
./reviews/2026-06-07-make-v1-installable.md:3180:skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/NOTICE.md:75: trailing whitespace.
./reviews/2026-06-07-make-v1-installable.md:3182:skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/NOTICE.md:76: trailing whitespace.
./reviews/2026-06-07-make-v1-installable.md:3184:skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/NOTICE.md:87: trailing whitespace.
./reviews/2026-06-07-make-v1-installable.md:3186:skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/NOTICE.md:88: trailing whitespace.
./reviews/2026-06-07-make-v1-installable.md:3188:skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/NOTICE.md:89: trailing whitespace.

 succeeded in 700ms:
.agents/plugins/marketplace.json
.claude-plugin/marketplace.json
.git/COMMIT_EDITMSG
.git/FETCH_HEAD
.git/HEAD
.git/ORIG_HEAD
.git/config
.git/description
.git/hooks/applypatch-msg.sample
.git/hooks/commit-msg.sample
.git/hooks/fsmonitor-watchman.sample
.git/hooks/post-update.sample
.git/hooks/pre-applypatch.sample
.git/hooks/pre-commit.sample
.git/hooks/pre-merge-commit.sample
.git/hooks/pre-push.sample
.git/hooks/pre-rebase.sample
.git/hooks/pre-receive.sample
.git/hooks/prepare-commit-msg.sample
.git/hooks/push-to-checkout.sample
.git/hooks/update.sample
.git/index
.git/info/exclude
.git/logs/HEAD
.git/objects/02/c646b173bcd445c6ba5fb59d0ee9c6327d207e
.git/objects/02/ddfffbb521d5aefa5118ad8288e737be5e7438
.git/objects/04/bedcd2339690c40f6e14d33b3fc5471fc520b4
.git/objects/05/04b210ab733f1c32efc6d1b4b9f1b3c8a43915
.git/objects/06/c04d214f26fc7560ddc06378746d0b943d1ccb
.git/objects/08/336761aa5ff99246d49755139083e3c0aa9617
.git/objects/08/f49e2c0fa0189e20a3783f9f1150ec3953f4c8
.git/objects/09/7f6466c1e2c68f6e50deb432470790566706ea
.git/objects/0d/29e3b0eaf0359b89af0ad528b5e018697442a1
.git/objects/10/ee60e173e5ed1526a53b2b1192268891f58b92
.git/objects/11/0e50da058557a188ac2950042f1b1c684eaeed
.git/objects/18/59bd53936c826ff504540c2eccfa1e682fe285
.git/objects/18/7b6a8e8711b613281f22c9f53c6c0734782c22
.git/objects/18/c86e2fab2627789e375538428fe0b1231c4ce2
.git/objects/19/ed391699966254a3d9eb8daa6df9d55bbe76c0
.git/objects/1a/21a8703081ef634ee35472cd6de212f639bb6d
.git/objects/1b/4eb2c83a71a4e35a5cc5ea11ea5dc26c8de07e
.git/objects/1b/f1ec9c61df6e0243b9c33c0750a3d5db483be8
.git/objects/1c/634e51d13c928d2d5a7e9e82fa29eb7d369e14
.git/objects/1c/8669f0e00fc3d937488858a4fd2b47ccd5cb27
.git/objects/1c/896e3974641c9b3f7fcb96a8d2922526432a41
.git/objects/1d/045679dc240577a8fb089d5d038be380e76348
.git/objects/1e/6181b815e9aad141dff32ea3aaeb1f640b8083
.git/objects/1e/de7d325da4b70601bac784c78621580796633f
.git/objects/1f/8a06960f373f833375863a216bafc66661ced8
.git/objects/21/28ba4e58b48ed11a8196bc425011ab7ea0ba26
.git/objects/22/1f41ecaa99f25c613c9c416fbbd7454da18e67
.git/objects/22/4dac6d6af75b1155cf0f1278c1054192e4e550
.git/objects/23/48be3f9b5eb127b2bdea2c9b21315f90d01bdd
.git/objects/26/003e3a0c9c79a0ff12163775367203bb8eefe9
.git/objects/26/163bbddfea64571feaf76d655c934c762d4ea6
.git/objects/29/e9c5efbde95d41882e72ccbe3638b3b042aeae
.git/objects/2a/61813fd8f668163f5ec5191945b0a57023af6e
.git/objects/2b/67c5cc5456a294a37acfe74fa160630b62a124
.git/objects/2e/678e0a8056992d9cdc9e8065957ba62e9589da
.git/objects/31/d2163e90477f4cb97c9971af6099392aca0b7b
.git/objects/32/fad45e54507a64760d7257511e72f9e8c98d42
.git/objects/33/eb5fb5d55cd7a19a63837fb0e43152afc00ace
.git/objects/34/012c1cedfe74cb4a3d892b46230b3f92f4d65c
.git/objects/34/8c5f2c1bea2f73d74f004debd503fb23e3a0a9
.git/objects/34/b75d2d176bc4b86ccb8264cdcbce330ef24c2f
.git/objects/36/504284e81483163e5e221d09057219f275600d
.git/objects/36/bc38dcaa65517df0b53e6c24dd870f4b05b8cd
.git/objects/36/dcbc54e8a7cb045ed8f9206f54bcd32c35685e
.git/objects/38/610550be0ce27fc5c9ba7266eec0507c76a6c3
.git/objects/3b/95433cc9d45796cee473fb54691643e48b0566
.git/objects/3b/d0ea31e6cebf17d6335f5ab7b0c5e23dcf5395
.git/objects/3e/bbaefbf4154dfa123fa0e8c411a89be1620e65
.git/objects/40/80ec67f230feb3ce148351a86a47b0f93a8f34
.git/objects/41/0ae25097049a389cf4b6ad75e40bd0baaf62c3
.git/objects/41/333e9e42238269710f7e3ec081fcdb46915579
.git/objects/42/2cf78030947b8daee38008d66614ccd37f0cff
.git/objects/42/a4d19bbf0810a5c0e63a4bd9998f4a8f07cc43
.git/objects/43/27fcd2ea5866d4212082871f098a037c2f5870
.git/objects/43/ae0e2a6c6d8fca34872506ca0f2e64194fec7c
.git/objects/44/1c93b81ad95ce813211972a978ef7e105bedbc
.git/objects/44/6522b2de7f030e65d81da38b0a958aa90474cd
.git/objects/45/50a3935c599f5d6750abdcbbc4e5dbdf09f997
.git/objects/45/7cbc155f7d73274bc0c6efac5031541bd46e64
.git/objects/46/1b2649114d9b45db76ed5c4e39c82250891cab
.git/objects/47/de6e97701fd6bd4abae6f3a7c30ea857263676
.git/objects/48/f0ef0dab94018ad398b6adc3b77ad68d8c6382
.git/objects/49/8a5cb0608ebb4f7d1003616e4ef17419ea1ce6
.git/objects/49/ec8f1dadd2bc8fa49629f24c1d39d9d0ce70bd
.git/objects/4b/825dc642cb6eb9a060e54bf8d69288fbee4904
.git/objects/4b/f937352c97ddbbdff6e78b66b21c1c082b0da9
.git/objects/4d/0667b80691e57fa7b5c0fdeb8de73a9ef1c397
.git/objects/4e/8081b6e0adf37755b846404e096dc57ba692ba
.git/objects/53/7d6621ea4fc240a48ce4d502f3a21cd4cf1ed2
.git/objects/55/cd13c40ec7171d68586f258f93195a62ff1eea
.git/objects/56/e53e231f172d8154abed86e7c4567f865fe11e
.git/objects/58/bb73589f5c8bf2792d2337161387d6b0faebc8
.git/objects/59/14ac4cf53618c3c1d3ca3cc8074702bb42eae4
.git/objects/59/3ffe1b26453205c7967e2bc33b95fe9625b6ba
.git/objects/59/845667c9bb261102a0935b5e93faac6c7fc324
.git/objects/5a/722b011795c2872b6e768028fac0d82e09e7df
.git/objects/5b/08d198bcd1029911b3783f4d5cc679b6d6e964
.git/objects/5b/0929cec94588d6c1fbc2fd5115dddea5ebd632
.git/objects/5b/aaec3432137c1eaf51a0bdd481c3fd40193a1e
.git/objects/5b/ff3dee76d7e29293e2a273a43bec318c1c50b1
.git/objects/5c/458bfd9d163587b1d620a2cb4b333a2519058c
.git/objects/5c/ec3ee7e5a7a34c69dbefce3460aa7cffcba48c
.git/objects/5c/f8da7f951e451ea3beae0c986e2df3cca7cb2e
.git/objects/5d/4d897f74efb0cb3d55956ed204dd3c2f00ee75
.git/objects/5d/8c75c54d89f90b6ad6b2adc39174037676cb00
.git/objects/5d/9d7ce870fbb9dbd79a322743d127be96fe03fa
.git/objects/5e/0a017668bf35ac6ff5ec370ae03213efac69d6
.git/objects/5f/014fce2f62970236275db7717e6998a0cddeae
.git/objects/60/463e01a2442dc215e75d8da8583e71fadc5719
.git/objects/60/f5d15a52c990a020dc25758397aabf19ab3e85
.git/objects/62/2ed32cc4f32727f067bd7b44fc79ea5e605c9e
.git/objects/64/cc13dcd51d3f73c82254cd30fd85dca0f0fcaf
.git/objects/6a/a7cbabbde24394612b0be9a46619f5cd7d3d34
.git/objects/6a/bbdf96740005ad85f1eb3c3b88bd99a6d461ec
.git/objects/6d/0fc232f540e028eb3cb03a9c0e17a9b5952608
.git/objects/6d/220fa8050aabda73933b236e7e6c8954179843
.git/objects/70/b9a8bd4e0c791ebd8af2a005be523d59d58a29
.git/objects/71/5699a5c4bab2be5f5cc2ae8db8cb5be7abf456
.git/objects/74/7f7720db37aa90672a5adf05ef20571bfe1b18
.git/objects/74/978b0ea50adaa00c01d3cc71cf9cc4c64b6802
.git/objects/74/f60ae378b6b5a88da8810afaa1459158f2bf88
.git/objects/75/989a01423868c8fd40ffa18e30d0fd323b6a93
.git/objects/76/0a2eecb0749460d4112cae7e2e1a5c02e323e2
.git/objects/76/27b776cfa77313fadb901126d8eefd9b8c4bbe
.git/objects/78/034b95c25a6d71f872f87df8f3742b3562a13d
.git/objects/79/db8acc4e6fc04dc7b1b3c70daf986ee3cac3d1
.git/objects/7a/a22581ba79db14b8c9c2b260ba01bf5f68e9e2
.git/objects/7b/6d885f4cb67bc22dfa4a4ad0a6b15563e42588
.git/objects/7b/872736a483dcceb2de97c40adc331bc3cb55e9
.git/objects/7b/901c20909a3083a5411b8587f2602a933dc455
.git/objects/7b/df906490ff4d9f85307306d0958cf21a2d3e11
.git/objects/7c/198357ed75debf16c1939685e965850265ffde
.git/objects/7d/aac74b8a3eed9360d2124148098238346737e9
.git/objects/7f/3eda986c43723475be1487231609ba7ec50c1d
.git/objects/84/b238687a8396a53aad675610d0e9ca4b567d94
.git/objects/86/7ce664c15ae1b92e17a572fdb2c6de4519091f
.git/objects/86/89d1ddcd8d5b696c6662dd2b7f7c3e36e7b23a
.git/objects/87/99a134022ce1890b262957f76ddc22ef86ce4f
.git/objects/88/052b7edf9c3d569559016db865912663b1713a
.git/objects/88/394fb850b6349820880575bed10a052a7fab63
.git/objects/8a/b4b46b15cafcb39bff8e089952aa0b25246345
.git/objects/8b/91246b10ead3834fb1862c4ddb13a5ba194a88
.git/objects/8b/d577650b1e69ae1d119e09b6a92a962e95b830
.git/objects/8b/f3498bf4f292ceeecbb1931b65b9fc63a2b6be
.git/objects/8c/612d875c3b313e342433914fd9f0d17f34dc23
.git/objects/8e/7ffe6597015bc587d8b3aa603037766ec68a08
.git/objects/8f/629a058e87249a3f09796e7a91194ca7835f1e
.git/objects/90/512d1f616653236360093034cfc863c2b91946
.git/objects/92/8bec7b91a217b8c1aa21730628596352d840d3
.git/objects/92/e9c926025520d918a9fd8744837252658c1751
.git/objects/94/1515c6d9ade7787dfae54529efd67402d4ebd1
.git/objects/94/deec7d4561ab061b86625659327c03d7ff2433
.git/objects/95/56d8663fcaa5045bcd055ced0a2147b99b2900
.git/objects/99/b2286cdad18bda117fe63d62b8922bcff832de
.git/objects/9a/16aa2d8ef39ae756607f44e9e6af81d3e794bd
.git/objects/9a/5c34dd366f14f92351d9b8366860e7fcc77c14
.git/objects/9c/5935c5743804a2d97c467d07f0eac43bed3c75
.git/objects/9d/b8742b5d2fdf1644b5a87aebed8a147dc9bfe5
.git/objects/a0/e5646e6298809a02fb16eb2903df5c944c13c8
.git/objects/a2/283d7f6a3ef276f1a8118715425a2fbd66272b
.git/objects/a2/7309693b3798475b5743532e5e8b26a0edd799
.git/objects/a4/a6d895a7236e6bdb862f6f1474114b884545a4
.git/objects/a6/16e427b2c926789e82415eef74f108f968333b
.git/objects/a6/8dd9d44a7d3947afc0a2f8be967985ab198f18
.git/objects/a6/dc8f848dd4c196e445b4f23ecabf264c280bf7
.git/objects/a7/b5ce1bd4683bcf55e671998bd2e25f0a72be23
.git/objects/a7/c9556ad3eb3c4799dc820755a14bf64be10fe0
.git/objects/a9/4522b34e6442ba1256ec304fa1899f5f684d27
.git/objects/a9/62b2815176e3dd49bbd78f72a7cdfa07dbe115
.git/objects/a9/87c42e01a5c743575b67bfd5a8e8e1947b13e9
.git/objects/a9/cd10dba29210a5c28582469b879d138d491195
.git/objects/ac/3952ea985c967d733f6d664c97bf9a1c923bde
.git/objects/ac/550b1821cc1beac9f8deedeba7bd6d33d9e2de
.git/objects/ac/757e37d2086017a23ec12d4fce52a1f18e8cb8
.git/objects/ac/80dd40a55e4815d2d1468013690e0f6572e47e
.git/objects/ac/8da5f72383193bd7242d634649198423361be3
.git/objects/ac/f8d6da7fe1f9d3045be845a23c405a7c9f4325
.git/objects/b0/28d683742411f12f2cf7c5d49ad16aef36c219
.git/objects/b0/6d6958c850e52d04bd36f6f7cc8c3a574af48b
.git/objects/b0/e085401cc4193aeb1df4a1853d2b90559b109d
.git/objects/b1/81f04d8f4516893c5c71175345c0f903e45898
.git/objects/b1/c8a0c0f23f2b41fc98f364b3ac392aa74986cf
.git/objects/b3/025b37eb8c2823cd1656cd3ca879ab070be906
.git/objects/b3/0bf5b7be154de56e73723f780089e7462c79c6
.git/objects/b3/7b52e955d1bc0f1e4ae285057ea90ea36d7d13
.git/objects/b5/17f68720823e830a915bbb08ad003a3e1a28a5
.git/objects/b5/80a37fca095e7c01aa9dee569ca2dbf7c52d59
.git/objects/b6/3b1f307f92c374f5e95d1c088441f1380fb4a9
.git/objects/b6/45f8eee17a740d2e6357675ca50334a43b4482
.git/objects/b6/6a5e196faa2102a974ff025cb4f5726e0e3562
.git/objects/b6/aa99dc0f35feedc8dcff8dc42d736b4cd4c27e
.git/objects/b6/f0a58502444eecfa2e41cd87d21972d16cc7f1
.git/objects/b7/f1efab753a1c5738514002f71bb69562405955
.git/objects/b8/9a19cde1826a6ef678588a0ddb5b2c2741f873
.git/objects/b8/ea56344c81df5652040bc4c8ba5b05f6b3de72
.git/objects/b9/0282c1fe345f283e3750301870ecb3bbcff3b2
.git/objects/b9/3acf9114896a9640203c760f49f50c9a38066f
.git/objects/ba/a6323f7a1ac769a24837018a29fe0aa52aa0e1
.git/objects/bb/4e165ce428a3e33b8fd428a1496b5596315aa0
.git/objects/bb/86aeee5a18f3d150606ae30bc7f7014ea39ed2
.git/objects/bb/e3f12818da37dc2ed3e50e91afb18802b520ca
.git/objects/bc/0d7105a314d731b57fab2b602639a396a0cbc9
.git/objects/bc/40e21e9801db00c0b9b9c1a7c82477ae84590e
.git/objects/bd/ed6b6064d880c6be436592ad335954b06ed7b1
.git/objects/be/123254262a1fcff860e90fbd4826ca73f8769b
.git/objects/be/264989f265b8877deaa11ea59944ab2acce776
.git/objects/bf/1e71246200514726f6f823948d50343c7e49c2
.git/objects/bf/2acbb60b1d5631dbc40d58e92d197fdd752159
.git/objects/bf/bda9e7256f7668dd4ecccc107bf111c0747a57
.git/objects/c0/70d03064f404bb43b6aecf5f8b07e2be7ba562
.git/objects/c2/e5bd20eb459b19798cb6fd056ebfa571d4f8d7
.git/objects/c3/f17130ceca97e15883fe56d139c919c9d97526
.git/objects/c4/455a1520dc3eb26ab7bc9cbf4af96ecc05284c
.git/objects/c4/55018608dc735fd3f37ab8a700d89945772bb8
.git/objects/c6/0e71e70a715d4fee1581d56ae6bb44f8fa8aa5
.git/objects/c6/156cef485f0df289aeb06649485d6754544735
.git/objects/c6/48a65718bc2d743593cc5390d9c8841daa2cda
.git/objects/c6/5f5389a9a5733a24a08e3826a67d6b39f2ade7
.git/objects/c8/5c17597863d5337fe2871f038406d52b58efe4
.git/objects/ca/429a76b545a98f400d393250fbe49222810476
.git/objects/cb/d9524787a589bd4faecda95cd2d5a7e04d89e6
.git/objects/ce/2d54f05fe79a08862e9d5477a2750a3029a4cc
.git/objects/cf/488314db714f8954a935bde6c8ab9f5ee0ac31
.git/objects/cf/5b4c01aab856c5c0c5664dc0ce076bc93a8b8c
.git/objects/cf/b839059c745ce5efb9880968b862c2a8eb4ec5
.git/objects/cf/f318d250ece463c2071f5867f1b6e864fa1671
.git/objects/d0/28b426324825ebad907e4d8aad843aea805190
.git/objects/d2/197f2808949859669ed4cb0ed6bbaf0dc542e1
.git/objects/d2/7c9ed7ca4c063579485624181920e03a88a75b
.git/objects/d2/c4f86673062980077b65261633ba76d0def131
.git/objects/d3/2e289a049bce06f47e3fa15f1f18586d488b52
.git/objects/d4/ed9045fae428c042a5774922d4597595aebe0f
.git/objects/d5/64d0bc3dd917926892c55e3706cc116d5b165e
.git/objects/d6/172afef5e19c0ae30fefb5986c1eff95939f8d
.git/objects/d6/5f6d688265fb744520e2873a59462b391ab681
.git/objects/d6/616a48d5c314accc2fbd7b57662af82035e9e8
.git/objects/d6/631d22fcc79c2220d5e70ce2b6e162beda275e
.git/objects/d7/27906153ef656ffab945f4d366990e51e094ae
.git/objects/d7/4b6d2bebb6be360418c2d9dc54b8f7659c3113
.git/objects/d8/e06e2c51906cb1bbcf7b47576ae2ffe628bdaa
.git/objects/d9/4aed83509a54a459c92408b85cce996a80fda6
.git/objects/d9/4b5c0c2af8b1d31afdcb61b0dfa87c54d1c248
.git/objects/d9/62f53dfa5681852b3777df7d7a97d7d8eef547
.git/objects/dc/050737262168cb1d2b1b3de2081ddd5b94f0ed
.git/objects/dc/9dde8f7490d06a5f66771a5d9ff6bdf9c438d9
.git/objects/dd/40013d7dc4e13d238bfe6905dfcff8253c1a91
.git/objects/de/46ae0be86db0981085d62d6c038ba967dafe3f
.git/objects/de/a060cceff161fdae57ce57ce11c62c5ff752b6
.git/objects/df/a1facdd514dae21d2184b077b545f2ba552886
.git/objects/e0/324a10bc21c7dbbc5e3c290486b2cb1859390f
.git/objects/e0/8e3656ef49e094eab2900c68c96f1e59bacfee
.git/objects/e1/368db7ee8ec56c92ebbeb89d09fe836f75e24f
.git/objects/e2/796f2abda929d5286fc1eac7c44cba3d59932e
.git/objects/e3/0c7316092af5301250b33bed45ead0474aff27
.git/objects/e3/145fa293629883a8ab38996ee2f4025638620a
.git/objects/e3/c63ace2dcebfe0ea86b0e1d6109c1accddbc30
.git/objects/e5/50c7b86fe67268c9c77b9ce8c70fc1fab78c77
.git/objects/e6/9de29bb2d1d6434b8b29ae775ad8c2e48c5391
.git/objects/e7/be4be64d5b933038f2dd417bd8849f9753c64a
.git/objects/e8/82f233e9cf5d33e317ec58b8d7dc390b21473c
.git/objects/e8/c44148c7edf39aa6447860819394ca9d1fe461
.git/objects/eb/dd0a53549ffc51913b09b8ee1f1abe3137cd49
.git/objects/ec/74bf3159901e679c9c3ddb26be4dab1287ac10
.git/objects/ed/d34047c304098af6fc35257067b993ef89b62f
.git/objects/ee/988fd66b884b843e28a84ef8709b55086662f2
.git/objects/ee/a097cdcd11d8c484b4a533f0c67d3f40193821
.git/objects/ee/efc3f6dcade82940210069785eb03e0abff504
.git/objects/ef/1137bba4b8af06d596041df828ad86d7851bb8
.git/objects/ef/b1a2f6459828eaa7a9b7d44d37d180e27c457f
.git/objects/f0/b8b77710a7d98c5f07e694a19d94b0ccdf98c7
.git/objects/f1/4e4cdc1c61ee49370eb9356c0b0aa9d018c917
.git/objects/f1/c96d1de37322cd019fe17a70b00025a23c46e7
.git/objects/f2/67b7a94f076544f8623e6992cae03898453c65
.git/objects/f5/16d85630cd6f20e77bafc6bd7cce7bb72ff2f5
.git/objects/f6/307112f464af0ff270ccecd24c7b78b780a18b
.git/objects/f8/889572d9a3638173f03c126fa7e7deff20574b
.git/objects/f8/8c301a7ce99887fa3fa7653889780f21eaf9b3
.git/objects/f9/5ea45b9bc759c61b255177ddcafa60c53ab218
.git/objects/f9/bc5c494d7abaef493f954bbc4f0a6f3749c1fb
.git/objects/fc/33a5fe27cb45c8a7fd70bd5d8a0714dc48d32d
.git/objects/ff/0bfbc71c1489b1e7417486cbca798b128c1b2b
.git/objects/ff/b3c4059bbd9434fa58cdc5462562814d9f0089
.git/packed-refs
.git/refs/heads/main
.gitignore
.omc/sessions/e6d3f8a4-a57a-48c3-b06d-9faf9b83d79a.json
.omc/state/agent-replay-48e619cb-8efc-4470-ba03-e60495035ed5.jsonl
.omc/state/hud-stdin-cache.json
.omc/state/last-tool-error.json
.omc/state/mission-state.json
.omc/state/subagent-tracking.json
.omx/logs/notify-hook-2026-06-07.jsonl
.omx/logs/omx-2026-06-07.jsonl
.omx/logs/tmux-hook-2026-06-07.jsonl
.omx/logs/turns-2026-06-07.jsonl
.omx/metrics.json
.omx/state/current-task-baseline.json
.omx/state/session.json
.omx/state/subagent-tracking.json
.omx/state/team-leader-nudge.json
.omx/state/tmux-hook-state.json
CLAUDE.md
README.md
docs/code-review-v1-2026-06-06.md
docs/design-ai-writing-suite-v1-2026-06-06.md
docs/handover-2026-06-02-personal-productivity-skills-next.md
docs/handover-2026-06-06-ai-writing-suite-v1.md
docs/handover-2026-06-06-v1-shipped.md
docs/migration-plan-local-repo-2026-06-06.md
docs/packaging.md
docs/plan-publish-cleanup-test-2026-06-07.md
docs/session-closeout-2026-06-02-ai-writing-humanizer.md
reviews/2026-06-07-adversarial-synthesis.md
reviews/2026-06-07-make-v1-installable.md
reviews/2026-06-07-rereview-final.md
skills/ai-writing-suite/.claude-plugin/plugin.json
skills/ai-writing-suite/.codex-plugin/plugin.json
skills/ai-writing-suite/CHANGELOG.md
skills/ai-writing-suite/LICENSE
skills/ai-writing-suite/NOTICE.md
skills/ai-writing-suite/README.md
skills/ai-writing-suite/SKILL.md
skills/ai-writing-suite/_shared/host-profile-template.md
skills/ai-writing-suite/_shared/learned-rules.md
skills/ai-writing-suite/_shared/self-improvement.md
skills/ai-writing-suite/_shared/voice-profile.md
skills/ai-writing-suite/evals/README.md
skills/ai-writing-suite/evals/smoke_test.py

 succeeded in 734ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
 .../.agents => .agents}/plugins/marketplace.json   |   2 +-
 .../marketplace.json                               |   8 +-
 .gitignore                                         |  13 --
 README.md                                          |  62 ++++++-
 docs/packaging.md                                  |  55 ++++++
 .../claude => }/.claude-plugin/plugin.json         |   2 +-
 .../.codex-plugin/plugin.json                      |   4 +-
 skills/ai-writing-suite/CHANGELOG.md               |  25 +++
 skills/ai-writing-suite/packaging/.gitkeep         |   0
 skills/ai-writing-suite/packaging/README.md        | 192 ---------------------
 skills/ai-writing-suite/packaging/sync.sh          | 159 -----------------
 11 files changed, 141 insertions(+), 381 deletions(-)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
R088	skills/ai-writing-suite/packaging/codex/.agents/plugins/marketplace.json	.agents/plugins/marketplace.json
R065	skills/ai-writing-suite/packaging/claude/.claude-plugin/marketplace.json	.claude-plugin/marketplace.json
M	.gitignore
M	README.md
A	docs/packaging.md
R095	skills/ai-writing-suite/packaging/claude/.claude-plugin/plugin.json	skills/ai-writing-suite/.claude-plugin/plugin.json
R093	skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/.codex-plugin/plugin.json	skills/ai-writing-suite/.codex-plugin/plugin.json
M	skills/ai-writing-suite/CHANGELOG.md
D	skills/ai-writing-suite/packaging/.gitkeep
D	skills/ai-writing-suite/packaging/README.md
D	skills/ai-writing-suite/packaging/sync.sh

2026-06-07T20:59:32.922032Z ERROR rmcp::transport::worker: worker quit with fatal: Transport channel closed, when AuthRequired(AuthRequiredError { www_authenticate_header: "Bearer realm=\"OAuth\", resource_metadata=\"https://mcp.cloudflare.com/.well-known/oauth-protected-resource/mcp\", error=\"invalid_token\"" })
hook: PostToolUse Completed
hook: PostToolUse Completed
hook: PostToolUse Completed
codex
A note on scope: the worktree has untracked review/handoff files, so I’m separating tracked final-state evidence from local untracked artifacts. Stale-reference findings will be based on tracked files unless an untracked file would actually ship.
hook: PreToolUse
hook: PreToolUse
hook: PreToolUse
hook: PreToolUse Completed
hook: PreToolUse Completed
hook: PreToolUse Completed
exec
/bin/zsh -lc "nl -ba README.md | sed -n '1,260p' && nl -ba docs/packaging.md | sed -n '1,220p' && nl -ba skills/ai-writing-suite/README.md | sed -n '1,240p'" in /Users/surahli/Documents/ai-writing-suite
exec
/bin/zsh -lc 'nl -ba .agents/plugins/marketplace.json && nl -ba .claude-plugin/marketplace.json && nl -ba skills/ai-writing-suite/.claude-plugin/plugin.json && nl -ba skills/ai-writing-suite/.codex-plugin/plugin.json' in /Users/surahli/Documents/ai-writing-suite
exec
/bin/zsh -lc "git ls-files -z | xargs -0 rg -n \"packaging/|sync\\.sh|packaging|sparse|marketplace|\\.agents/plugins|\\.claude-plugin|\\.codex-plugin|plugin install|plugin add|skills/ai-writing-suite\"" in /Users/surahli/Documents/ai-writing-suite
hook: PostToolUse
hook: PostToolUse
 succeeded in 362ms:
     1	# AI Writing Suite
     2	
     3	An open-source, MIT-licensed agent skill suite for **writing assistance** — the public
     4	version of a writing-assistant skillset for a company Data Science team. It polishes,
     5	drafts, and reviews prose against a **pluggable knowledge base** (a "DS Comms Playbook"
     6	in the company fork; a generic best-practices KB in this OSS build).
     7	
     8	> **Engine vs fuel:** this repo is the *engine*. The knowledge base is *fuel* — swappable.
     9	> The OSS build ships a generic KB; a company fork drops its real playbook into the same
    10	> slot. The proprietary playbook never enters this public repo.
    11	
    12	## What it does (target)
    13	
    14	1. **Polish / review** — de-AI and tighten prose while preserving meaning and author voice.
    15	2. **Voice learning** — interview + distill a writer's historical style into a reusable profile.
    16	3. **Knowledge QA (mini-RAG)** — answer questions over the playbook + best practices *(v2)*.
    17	4. **Guided drafting** — draft a page using the playbook *(v2)*.
    18	
    19	Plus a **human-gated self-improvement** loop: each session can *propose* new rules; you
    20	approve before anything is written. Core skill logic is never auto-edited.
    21	
    22	## Status
    23	
    24	**v1 — built, verified, and installable on Claude, Codex, and Cursor.** Ships the polish/de-AI
    25	capability (`comms-polish`), voice learning (`voice-onboard`), a generic pluggable KB seed with an
    26	end-to-end retrieval smoke path, an eval harness (Python AI-tell detector + fixtures), and a
    27	human-gated self-improvement hook. `comms-qa` (KB Q&A) and `comms-draft` are v2 stubs.
    28	
    29	- **Plan (read first):** [`docs/design-ai-writing-suite-v1-2026-06-06.md`](docs/design-ai-writing-suite-v1-2026-06-06.md)
    30	  — decision log D1–D12, v1 scope, risks, eng+ceo review report.
    31	
    32	## Install
    33	
    34	One source of truth (`skills/ai-writing-suite/`) published to three hosts.
    35	
    36	### Claude Code
    37	
    38	```bash
    39	claude plugin marketplace add surahli123/ai-writing-suite
    40	claude plugin install ai-writing-suite@ai-writing-suite
    41	```
    42	
    43	Claude auto-discovers the sub-skills (`comms-polish`, `voice-onboard`, …); invoke by asking it to
    44	polish/review prose, or call a skill by name.
    45	
    46	### Codex
    47	
    48	```bash
    49	codex plugin marketplace add surahli123/ai-writing-suite
    50	codex plugin add ai-writing-suite@ai-writing-suite
    51	```
    52	
    53	Codex resolves the plugin from the same source tree — no `--sparse` needed; the Codex
    54	marketplace manifest sits at the repo root (`.agents/plugins/marketplace.json`).
    55	
    56	### Cursor
    57	
    58	Cursor reads Anthropic-format **Agent Skills** from `.cursor/skills/` — there is no marketplace, so
    59	copy the skill tree into a discovery location:
    60	
    61	```bash
    62	git clone https://github.com/surahli123/ai-writing-suite
    63	cp -R ai-writing-suite/skills/ai-writing-suite ~/.cursor/skills/ai-writing-suite
    64	```
    65	
    66	(Or copy into your project's `.cursor/skills/` for project-scoped use.) Cursor discovers the skills
    67	on the next session; invoke with `/comms-polish`, `/voice-onboard`, … or by intent.
    68	
    69	## Repo Layout
    70	
    71	```text
    72	.claude-plugin/marketplace.json    # Claude marketplace  → points at the source tree
    73	.agents/plugins/marketplace.json   # Codex marketplace   → points at the source tree
    74	skills/
    75	  ai-writing-suite/                # THE SUITE — single source of truth
    76	                                   #   (Claude + Codex install this; Cursor copies it)
    77	    SKILL.md                       # thin router
    78	    .claude-plugin/plugin.json     # Claude plugin manifest
    79	    .codex-plugin/plugin.json      # Codex plugin manifest
    80	    skills/                        # sub-skills: comms-polish, voice-onboard, comms-qa*, comms-draft*
    81	    _shared/                       # patterns (engine) + knowledge (swappable KB) + voice profile
    82	    evals/                         # AI-tell detector + fixtures + smoke tests
    83	    NOTICE.md  LICENSE  README.md  CHANGELOG.md
    84	docs/                              # design docs, handovers, plans, packaging  (* = v2 stub)
    85	```
    86	
    87	## Attribution
    88	
    89	Absorbed material from other repos is MIT-licensed; each source's copyright + license is
    90	preserved and credited in [`skills/ai-writing-suite/NOTICE.md`](skills/ai-writing-suite/NOTICE.md).
     1	# Packaging & Publishing (maintainer note)
     2	
     3	**Model: one source tree, read directly by every host.** There is no build/generate step.
     4	The single source of truth is `skills/ai-writing-suite/`. Each host gets a tiny manifest that
     5	*points at* that tree (or, for Cursor, copies it). Nothing is duplicated or generated, so there
     6	is no sync-drift surface.
     7	
     8	> This replaces the earlier generate-and-sync approach (`packaging/` + `sync.sh`), which was
     9	> removed: its generated bodies were gitignored, which is what made v1 uninstallable.
    10	
    11	## The four manifests
    12	
    13	| File | Host | Role |
    14	|---|---|---|
    15	| `/.claude-plugin/marketplace.json` | Claude | Marketplace catalog; `plugins[].source = "./skills/ai-writing-suite"` |
    16	| `/skills/ai-writing-suite/.claude-plugin/plugin.json` | Claude | Plugin identity (name, version, metadata) |
    17	| `/.agents/plugins/marketplace.json` | Codex | Marketplace catalog; `plugins[].source = {source:"local", path:"./skills/ai-writing-suite"}` |
    18	| `/skills/ai-writing-suite/.codex-plugin/plugin.json` | Codex | Plugin identity (+ `"skills": "./skills/"`, `interface{}`) |
    19	
    20	Both root marketplaces point at the **same** source tree. Claude auto-discovers the sub-skills
    21	under `skills/ai-writing-suite/skills/`; the root `SKILL.md` is a documentation router.
    22	
    23	## Install (end users)
    24	
    25	- **Claude:** `claude plugin marketplace add surahli123/ai-writing-suite` → `claude plugin install ai-writing-suite@ai-writing-suite`
    26	- **Codex:** `codex plugin marketplace add surahli123/ai-writing-suite` → `codex plugin add ai-writing-suite@ai-writing-suite`
    27	- **Cursor:** copy `skills/ai-writing-suite/` into `~/.cursor/skills/ai-writing-suite/` (or a project's `.cursor/skills/`). Cursor reads Anthropic-format `SKILL.md` Agent Skills natively; no manifest needed. (Not `.cursor/rules/*.mdc` — that is passive context injection, the wrong primitive for callable skills.)
    28	
    29	## Versioning / updates
    30	
    31	1. Bump `version:` in the source `SKILL.md` frontmatter (if present) and in the two `plugin.json`
    32	   files (`.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`).
    33	2. Commit + push. Consumers refresh via `claude plugin update` / `codex plugin marketplace upgrade`.
    34	3. (Optional) cut a git tag (`claude plugin tag` for Claude; a git tag for Codex `--ref` pinning)
    35	   **after** verifying a real-remote install.
    36	
    37	## Verify before publishing
    38	
    39	- `claude plugin validate .` and `claude plugin validate skills/ai-writing-suite` (both must pass).
    40	- Local install smoke per host (add the local path as a marketplace, install, confirm the skill
    41	  loads, then remove — restore your config). For Cursor, validate the `SKILL.md` frontmatter `name:`
    42	  matches each folder.
    43	- **Local green ≠ remote-installable.** After pushing, run a real-remote smoke
    44	  (`marketplace add surahli123/ai-writing-suite`) before tagging a release.
    45	
    46	## Engine vs fuel
    47	
    48	`_shared/patterns/` is the *engine* (de-AI rules) and must survive a KB swap. `_shared/knowledge/`
    49	is the *fuel* — the generic OSS KB; a company fork drops its real playbook into the same slot
    50	(never committed to this public repo).
    51	
    52	## Deferred (v2)
    53	
    54	RovoDev packaging. It will follow the same source-pointing model (explicit intent routing via the
    55	suite router, since RovoDev does not auto-trigger skills).
     1	# AI Writing Suite
     2	
     3	Polish prose that sounds AI-written without changing what the author meant.
     4	
     5	The differentiator is not "rewrite this better." It is:
     6	
     7	```text
     8	preserve meaning, remove AI slop, keep author voice
     9	```
    10	
    11	Use it when a draft has the usual model tells: filler, vague claims, inflated importance, forced structure, and rhythm that sounds too even.
    12	
    13	## What It Does
    14	
    15	`ai-writing-suite` is a four-part writing-assistant skillset:
    16	
    17	1. **comms-polish** (v1) — identify tells, preserve meaning, remove AI-shaped prose patterns, match author voice or register.
    18	2. **voice-onboard** (v1) — interview, collect writing samples, distill your voice signature.
    19	3. **comms-qa** (v2) — knowledge QA over a pluggable writing playbook.
    20	4. **comms-draft** (v2) — guided drafting workflow using playbook best practices.
    21	
    22	An agent using the suite can:
    23	
    24	1. Identify the audience and purpose
    25	2. Preserve facts, citations, numbers, commands, and claims
    26	3. Remove AI-shaped prose patterns
    27	4. Match the author's voice or the document's register
    28	5. Return either a rewrite, a review, a detection score, or targeted file edits
    29	
    30	## Engine vs Fuel
    31	
    32	The OSS version ships the **engine** (comms-polish, voice-onboard, eval harness, self-improvement) with a generic **knowledge base** distilled from four open-source projects.
    33	
    34	The company version reuses the same engine and swaps a proprietary **DS Comms Playbook** into the knowledge slot via a Confluence page. The playbook never enters this public repository.
    35	
    36	```
    37	OSS:     engine + generic KB
    38	Company: engine + proprietary playbook (dropped in as data, not code)
    39	```
    40	
    41	No code changes needed to switch playbooks.
    42	
    43	## When To Use It
    44	
    45	Use the suite for:
    46	
    47	- docs and README prose
    48	- emails and status updates
    49	- social posts and personal notes
    50	- reports and summaries
    51	- launch notes and user-facing copy
    52	
    53	Do not use it for source-code cleanup. Use a code cleanup or refactoring skill for that.
    54	
    55	## Sub-Skills
    56	
    57	### comms-polish (Ships in v1)
    58	
    59	Polish prose and detect AI tells.
    60	
    61	**Modes:**
    62	- `detect` — find AI tells and estimate density without rewriting.
    63	- `rewrite` — produce polished prose from pasted text.
    64	- `edit` — modify a prose file in place while preserving structure.
    65	- `review` — give prioritized writing findings without rewriting everything.
    66	
    67	**Features:**
    68	- Consolidated AI-tell pattern catalog (seven deduplicated sources, each pattern source-tagged for attribution).
    69	- Scenario presets (tweet, LinkedIn, README, memo).
    70	- Final-pass checklist before publishing.
    71	- Voice matching (reads `_shared/voice-profile.md` to calibrate tone and style if present).
    72	- 0–100 AI-tell density score for before/after comparison.
    73	
    74	**Example:**
    75	
    76	Before:
    77	```text
    78	This robust workflow enables teams to seamlessly leverage contextual insights, ensuring a more effective and streamlined development experience.
    79	```
    80	
    81	After:
    82	```text
    83	This workflow gives teams the context they need before they start editing.
    84	```
    85	
    86	### voice-onboard (Ships in v1)
    87	
    88	Interview and distill your writing voice.
    89	
    90	**Features:**
    91	- Guided conversation to collect writing samples (local files or pasted text).
    92	- Extracts voice signature (tone, vocabulary, sentence shape, register preferences).
    93	- Writes `_shared/voice-profile.md` for reuse across sessions.
    94	- Structured host-profile template for consistent capture.
    95	
    96	### comms-qa (v2)
    97	
    98	Knowledge QA over a pluggable playbook.
    99	
   100	**Features:**
   101	- Wiki-style markdown KB (zero external dependencies, portable across Claude / Codex / Cursor / RovoDev).
   102	- Pure markdown + `INDEX.md` navigation; no host-specific MCP tools.
   103	- Pluggable slot: OSS ships generic KB; company forks and drops a Confluence-sourced playbook.
   104	- End-to-end smoke test in v1 proves the company step is "drop in a page", not "build a RAG engine".
   105	
   106	### comms-draft (v2)
   107	
   108	Guided drafting workflow using playbook best practices.
   109	
   110	**Features:**
   111	- Playbook-driven interview flow.
   112	- Real-time feedback on audience, structure, clarity.
   113	- Cite-as-you-go pattern matching against the KB.
   114	
   115	## Self-Improvement (Human-Gated)
   116	
   117	After each session, the suite proposes new rules based on error analysis:
   118	
   119	1. Analyze edits you made or approved.
   120	2. Propose candidate rules (e.g., "remove 'seamlessly'" or "tighten 'important to note'").
   121	3. You approve; we eval-test the rule against the baseline.
   122	4. Approved rules append to `_shared/learned-rules.md` (append-only, never auto-editing core logic).
   123	
   124	Rules improve over time without drift or degradation.
   125	
   126	## Knowledge Base
   127	
   128	The knowledge base lives in `_shared/knowledge/`:
   129	
   130	- `INDEX.md` — wiki-style navigation index.
   131	- Topic markdown files — audience, clarity, revision, structure, tone, and more.
   132	
   133	**For OSS:** Generic best-practices entries distilled from four MIT-licensed source projects.
   134	
   135	**For company:** Drop in a Confluence page link; the engine reads and retrieves from your playbook.
   136	
   137	## Install
   138	
   139	Clone or copy this repo, then symlink the skill into your target environment.
   140	
   141	### Claude
   142	
   143	```bash
   144	# Copy to your Claude Code skills directory
   145	cp -r skills/ai-writing-suite ~/.claude/skills/ai-writing-suite
   146	```
   147	
   148	Restart Claude Code so the skill list refreshes.
   149	
   150	### Codex
   151	
   152	```bash
   153	# Copy to your Codex skills directory
   154	cp -r skills/ai-writing-suite ~/.codex/skills/ai-writing-suite
   155	```
   156	
   157	Restart Codex so the skill list refreshes.
   158	
   159	### Cursor / RovoDev (v2)
   160	
   161	See `packaging/` for surface-specific installation instructions (coming in v2).
   162	
   163	## How to Use
   164	
   165	### Invoke comms-polish
   166	
   167	```
   168	I wrote this: "[pasted text]"
   169	Rewrite it to sound less AI-generated, keeping the facts and my voice.
   170	Mode: rewrite
   171	Audience: technical docs / LinkedIn post / memo / etc.
   172	```
   173	
   174	Or:
   175	
   176	```
   177	Detect AI tells in this: "[pasted text]"
   178	Give me a score and top three edits I could make.
   179	Mode: detect
   180	```
   181	
   182	### Invoke voice-onboard
   183	
   184	```
   185	I want to teach you my writing voice. Here are some samples: [paste or link files]
   186	```
   187	
   188	The skill interviews you, extracts your voice signature, and saves it for all future sessions.
   189	
   190	### Read the learned rules
   191	
   192	```
   193	What rules have we learned so far?
   194	```
   195	
   196	The suite shows `_shared/learned-rules.md`, which grows as new patterns emerge from your writing.
   197	
   198	## Evaluation
   199	
   200	The suite ships with:
   201	
   202	- **Before/after fixtures** across genres (tweet, LinkedIn, README, memo).
   203	- **LLM-judged scoring** — a rubric calibrated so the baseline fails 30–40% of cases.
   204	- **Mechanical regression gate** — ported from avoid-ai JavaScript detector.
   205	- **Self-improvement integration** — each proposed rule is eval-tested before you approve it.
   206	
   207	See `evals/` for details.
   208	
   209	## Attribution
   210	
   211	This suite absorbs and extends patterns, templates, and methodologies from seven open-source projects, all MIT-licensed:
   212	
   213	1. **weijt606/anti-vibe-writing** — bilingual patterns, scenario presets, host-profile template.
   214	2. **conorbronsdon/avoid-ai-writing** — JS detector, CATEGORIES taxonomy, packaging patterns.
   215	3. **donghuixin/AI-Vibe-Writing-Skills** — style-extractor prompts, memory patterns, self-improvement shape.
   216	4. **Yuan1z0825/nature-skills** — academic polish rubric, structural patterns, plugin conventions.
   217	5. **stop-slop** by Hardik Pandya — core directness rules, scoring methodology.
   218	6. **blader/humanizer** by Brandon Wise — 43-pattern catalog, voice calibration.
   219	7. **aboudjem/humanizer-skill** — 30-pattern catalog derived from Wikipedia "Signs of AI writing".
   220	
   221	See `NOTICE.md` for full copyright and license details. Every absorbed pattern is source-tagged in `_shared/patterns/00-index.md` for traceability.
   222	
   223	## Design Decisions
   224	
   225	For a full account of why the suite is built this way, see:
   226	
   227	- `docs/design-ai-writing-suite-v1-2026-06-06.md` — decision log (D1–D12), risks, success criteria.
   228	- `CLAUDE.md` — project-specific conventions and working style.
   229	
   230	Key decisions include:
   231	
   232	- **D1 (Product):** Full suite, not a narrow humanizer; OSS face of a company DS skillset.
   233	- **D2 (Reuse):** Absorb all MIT sources with preserved attribution.
   234	- **D5 (RAG):** Pure markdown + convention, not host-specific MCP tools; portable across Claude / Codex / Cursor / RovoDev.
   235	- **D6 (Safety):** Human-gated self-improvement; never auto-edit core logic.
   236	- **D12 (v1 Scope):** Prove one end-to-end KB smoke path so company step is "drop in a page", not "build a RAG".
   237	
   238	## License
   239	
   240	MIT License. See `LICENSE` and `NOTICE.md` for details.

 succeeded in 367ms:
     1	{
     2	  "name": "ai-writing-suite",
     3	  "interface": {
     4	    "displayName": "AI Writing Suite"
     5	  },
     6	  "plugins": [
     7	    {
     8	      "name": "ai-writing-suite",
     9	      "source": {
    10	        "source": "local",
    11	        "path": "./skills/ai-writing-suite"
    12	      },
    13	      "policy": {
    14	        "installation": "AVAILABLE",
    15	        "authentication": "ON_INSTALL"
    16	      },
    17	      "category": "Productivity"
    18	    }
    19	  ]
    20	}
     1	{
     2	  "$schema": "https://json.schemastore.org/claude-code-marketplace.json",
     3	  "name": "ai-writing-suite",
     4	  "description": "Writing-assistant skill suite — polish/de-AI prose, learn an author's voice, and (v2) answer questions from a knowledge base and draft from it.",
     5	  "owner": {
     6	    "name": "surahli123"
     7	  },
     8	  "plugins": [
     9	    {
    10	      "name": "ai-writing-suite",
    11	      "source": "./skills/ai-writing-suite",
    12	      "description": "Suite of writing-assistant skills for professional and product communication. Polish and de-AI prose, learn an author's voice, and (v2) answer KB questions and draft from a knowledge base.",
    13	      "category": "productivity",
    14	      "keywords": ["writing", "editing", "humanize", "voice", "comms", "polish"]
    15	    }
    16	  ]
    17	}
     1	{
     2	  "name": "ai-writing-suite",
     3	  "description": "Suite of writing-assistant skills for professional and product communication. Polish and de-AI prose, learn an author's voice, answer KB questions, and draft from a knowledge base.",
     4	  "version": "1.0.0",
     5	  "author": {
     6	    "name": "surahli123"
     7	  },
     8	  "homepage": "https://github.com/surahli123/ai-writing-suite",
     9	  "repository": "https://github.com/surahli123/ai-writing-suite",
    10	  "license": "MIT",
    11	  "keywords": ["writing", "editing", "humanize", "voice", "comms", "polish"]
    12	}
     1	{
     2	  "name": "ai-writing-suite",
     3	  "version": "1.0.0",
     4	  "description": "Suite of writing-assistant skills for professional and product communication. Polish and de-AI prose, learn an author's voice, answer KB questions, and draft from a knowledge base.",
     5	  "author": { "name": "surahli123" },
     6	  "homepage": "https://github.com/surahli123/ai-writing-suite",
     7	  "repository": "https://github.com/surahli123/ai-writing-suite",
     8	  "license": "MIT",
     9	  "keywords": ["writing", "editing", "humanize", "voice", "comms", "polish"],
    10	  "skills": "./skills/",
    11	  "interface": {
    12	    "displayName": "AI Writing Suite",
    13	    "shortDescription": "Polish/de-AI prose, learn an author's voice, KB-guided writing.",
    14	    "longDescription": "A suite of writing-assistant skills: polish and de-AI prose while preserving meaning and voice, learn an author's historical voice into a reusable profile, and (in v2) answer questions from and draft against a pluggable knowledge base.",
    15	    "developerName": "surahli123",
    16	    "category": "Productivity",
    17	    "capabilities": ["Read", "Write"]
    18	  }
    19	}

hook: PostToolUse
 succeeded in 741ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
README.md:34:One source of truth (`skills/ai-writing-suite/`) published to three hosts.
README.md:39:claude plugin marketplace add surahli123/ai-writing-suite
README.md:40:claude plugin install ai-writing-suite@ai-writing-suite
README.md:49:codex plugin marketplace add surahli123/ai-writing-suite
README.md:50:codex plugin add ai-writing-suite@ai-writing-suite
README.md:53:Codex resolves the plugin from the same source tree — no `--sparse` needed; the Codex
README.md:54:marketplace manifest sits at the repo root (`.agents/plugins/marketplace.json`).
README.md:58:Cursor reads Anthropic-format **Agent Skills** from `.cursor/skills/` — there is no marketplace, so
README.md:63:cp -R ai-writing-suite/skills/ai-writing-suite ~/.cursor/skills/ai-writing-suite
README.md:72:.claude-plugin/marketplace.json    # Claude marketplace  → points at the source tree
README.md:73:.agents/plugins/marketplace.json   # Codex marketplace   → points at the source tree
README.md:78:    .claude-plugin/plugin.json     # Claude plugin manifest
README.md:79:    .codex-plugin/plugin.json      # Codex plugin manifest
README.md:84:docs/                              # design docs, handovers, plans, packaging  (* = v2 stub)
README.md:90:preserved and credited in [`skills/ai-writing-suite/NOTICE.md`](skills/ai-writing-suite/NOTICE.md).
docs/code-review-v1-2026-06-06.md:23:stdlib-only confirmed (no package.json/requirements/pyproject) → D5 holds. `sync.sh` idempotent;
docs/code-review-v1-2026-06-06.md:40:generic 5-entry KB; full comms-qa retrieval is v2." Re-run `sync.sh`.
docs/code-review-v1-2026-06-06.md:67:- **n1** `evals/` excluded from packaged targets (CI-only) — document why in `packaging/README.md`.
docs/code-review-v1-2026-06-06.md:80:- Honest scaffolding (v2 stubs labeled; P31-P43 corruption disclosed; sync.sh single-source rule).
docs/design-ai-writing-suite-v1-2026-06-06.md:59:| **conorbronsdon/avoid-ai-writing** | Programmatic JS detector + tests + CI, CATEGORIES taxonomy, multi-surface packaging (Claude plugin + Cursor `.mdc`) + `sync-plugin-skill.sh` | Detector (v2), packaging/sync scaffold, Cursor target |
docs/design-ai-writing-suite-v1-2026-06-06.md:61:| **Yuan1z0825/nature-skills** (`nature-writing` + `nature-polishing` only) | Academic polish/writing rubric, codex/plugin manifest conventions | `comms-polish` rubric, packaging conventions |
docs/design-ai-writing-suite-v1-2026-06-06.md:88:├── packaging/
docs/design-ai-writing-suite-v1-2026-06-06.md:89:│   ├── sync.sh                        # single source → 4 targets
docs/design-ai-writing-suite-v1-2026-06-06.md:90:│   ├── .claude-plugin/ .codex-plugin/ cursor-rules/ rovodev/
docs/design-ai-writing-suite-v1-2026-06-06.md:133:programmatic JS/Python detector, Cursor + RovoDev packaging, bilingual Chinese path,
docs/design-ai-writing-suite-v1-2026-06-06.md:149:- **R4 — 4-surface sync drift.** Single source of truth + `sync.sh` (avoid-ai pattern).
docs/design-ai-writing-suite-v1-2026-06-06.md:178:→ Cursor + RovoDev packaging → bilingual path → company fork with real playbook.
docs/design-ai-writing-suite-v1-2026-06-06.md:185:- 4 MIT repos → detectors, scenario presets, voice templates, packaging/sync scaffolds.
docs/design-ai-writing-suite-v1-2026-06-06.md:194:- Cursor + RovoDev packaging — v2 (Claude + Codex only).
CLAUDE.md:7:- `skills/ai-writing-suite/` — AI writing-assistant suite (currently ships the polish/humanize capability; growing into a full suite — see plan below).
skills/ai-writing-suite/README.md:145:cp -r skills/ai-writing-suite ~/.claude/skills/ai-writing-suite
skills/ai-writing-suite/README.md:154:cp -r skills/ai-writing-suite ~/.codex/skills/ai-writing-suite
skills/ai-writing-suite/README.md:161:See `packaging/` for surface-specific installation instructions (coming in v2).
skills/ai-writing-suite/README.md:214:2. **conorbronsdon/avoid-ai-writing** — JS detector, CATEGORIES taxonomy, packaging patterns.
skills/ai-writing-suite/NOTICE.md:27:**Contribution:** Programmatic JavaScript detector with test suite, tiered AI-vocabulary taxonomy (Tier 1/2/3 classification), CATEGORIES taxonomy for AI-writing patterns, multi-surface packaging patterns (Claude plugin, Cursor `.mdc` format), and sync tooling scaffold.
skills/ai-writing-suite/NOTICE.md:29:**Used in:** AI-tell pattern catalog (lexical tells, significance attribution, structural patterns), the Python detector port shipped in v1 (`evals/detector/`), packaging and sync conventions.
skills/ai-writing-suite/NOTICE.md:55:**Used in:** AI-tell pattern catalog (rhythm, stylometry, structural tells), `comms-polish` scoring and review rubric, Codex packaging conventions.
skills/ai-writing-suite/CHANGELOG.md:15:  and the Claude marketplace manifest was not at a resolvable location. Both Claude
skills/ai-writing-suite/CHANGELOG.md:17:  marketplace manifests (`.claude-plugin/marketplace.json` and
skills/ai-writing-suite/CHANGELOG.md:18:  `.agents/plugins/marketplace.json`), each backed by an in-source `plugin.json`.
skills/ai-writing-suite/CHANGELOG.md:22:  `.cursor/skills/`; install = copy `skills/ai-writing-suite/` into a Cursor skills
skills/ai-writing-suite/CHANGELOG.md:26:  maintainer packaging note at `docs/packaging.md`.
skills/ai-writing-suite/CHANGELOG.md:29:- **Generate-and-sync packaging** (`packaging/` + `sync.sh`) — obsolete now that every
skills/ai-writing-suite/CHANGELOG.md:42:- **Directory structure** — standardized layout with `skills/`, `_shared/` (knowledge, patterns, voice profiles), and `packaging/` for multi-surface distribution.
skills/ai-writing-suite/CHANGELOG.md:89:- **Sync tooling scaffold** (`packaging/sync.sh`) — single source of truth distributed to four surfaces (Claude, Codex, Cursor, RovoDev).
skills/ai-writing-suite/CHANGELOG.md:90:- **Multi-surface manifests** — `.claude-plugin/`, `.codex-plugin/`, `cursor-rules/`, `rovodev/` directories (v1: Claude + Codex only; v2: Cursor + RovoDev).
skills/ai-writing-suite/CHANGELOG.md:109:- **Ships in v1:** Suite skeleton, `comms-polish`, `voice-onboard`, generic KB seed, self-improvement hook, eval harness, Claude + Codex packaging, NOTICE/CHANGELOG/README.
skills/ai-writing-suite/CHANGELOG.md:110:- **Deferred to v2:** `comms-qa` full RAG, `comms-draft`, Confluence ingestion, programmatic detector, Cursor + RovoDev packaging, bilingual Chinese path, embedding index.
skills/ai-writing-suite/CHANGELOG.md:136:- Cursor + RovoDev packaging — surface-specific manifests.
.claude-plugin/marketplace.json:2:  "$schema": "https://json.schemastore.org/claude-code-marketplace.json",
.claude-plugin/marketplace.json:11:      "source": "./skills/ai-writing-suite",
.agents/plugins/marketplace.json:11:        "path": "./skills/ai-writing-suite"
docs/packaging.md:4:The single source of truth is `skills/ai-writing-suite/`. Each host gets a tiny manifest that
docs/packaging.md:8:> This replaces the earlier generate-and-sync approach (`packaging/` + `sync.sh`), which was
docs/packaging.md:15:| `/.claude-plugin/marketplace.json` | Claude | Marketplace catalog; `plugins[].source = "./skills/ai-writing-suite"` |
docs/packaging.md:16:| `/skills/ai-writing-suite/.claude-plugin/plugin.json` | Claude | Plugin identity (name, version, metadata) |
docs/packaging.md:17:| `/.agents/plugins/marketplace.json` | Codex | Marketplace catalog; `plugins[].source = {source:"local", path:"./skills/ai-writing-suite"}` |
docs/packaging.md:18:| `/skills/ai-writing-suite/.codex-plugin/plugin.json` | Codex | Plugin identity (+ `"skills": "./skills/"`, `interface{}`) |
docs/packaging.md:20:Both root marketplaces point at the **same** source tree. Claude auto-discovers the sub-skills
docs/packaging.md:21:under `skills/ai-writing-suite/skills/`; the root `SKILL.md` is a documentation router.
docs/packaging.md:25:- **Claude:** `claude plugin marketplace add surahli123/ai-writing-suite` → `claude plugin install ai-writing-suite@ai-writing-suite`
docs/packaging.md:26:- **Codex:** `codex plugin marketplace add surahli123/ai-writing-suite` → `codex plugin add ai-writing-suite@ai-writing-suite`
docs/packaging.md:27:- **Cursor:** copy `skills/ai-writing-suite/` into `~/.cursor/skills/ai-writing-suite/` (or a project's `.cursor/skills/`). Cursor reads Anthropic-format `SKILL.md` Agent Skills natively; no manifest needed. (Not `.cursor/rules/*.mdc` — that is passive context injection, the wrong primitive for callable skills.)
docs/packaging.md:32:   files (`.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`).
docs/packaging.md:33:2. Commit + push. Consumers refresh via `claude plugin update` / `codex plugin marketplace upgrade`.
docs/packaging.md:39:- `claude plugin validate .` and `claude plugin validate skills/ai-writing-suite` (both must pass).
docs/packaging.md:40:- Local install smoke per host (add the local path as a marketplace, install, confirm the skill
docs/packaging.md:44:  (`marketplace add surahli123/ai-writing-suite`) before tagging a release.
docs/packaging.md:54:RovoDev packaging. It will follow the same source-pointing model (explicit intent routing via the
docs/migration-plan-local-repo-2026-06-06.md:36:2. In the new copy: delete `skills/agent-goal-contracts/`, flatten/keep `skills/ai-writing-suite/`,
docs/migration-plan-local-repo-2026-06-06.md:45:- Extract only `skills/ai-writing-suite/` history into a brand-new repo.
docs/migration-plan-local-repo-2026-06-06.md:85:#   + (optional) flatten skills/ai-writing-suite/* to repo root — DECISION below
docs/migration-plan-local-repo-2026-06-06.md:93:- **Keep `skills/ai-writing-suite/`** (no flatten) → matches the design doc's eventual multi-sub-skill

hook: PostToolUse Completed
hook: PostToolUse Completed
hook: PostToolUse Completed
codex
The main root install instructions look consistent with the new source-pointing model. The strongest issue I see so far is not the root marketplace docs, but the README that ships inside the installable source tree still telling users to copy into host skill dirs and to see a deleted `packaging/` directory.
hook: PreToolUse
hook: PreToolUse
hook: PreToolUse
hook: PreToolUse Completed
exec
/bin/zsh -lc "find skills/ai-writing-suite -maxdepth 3 -type f | sort | sed 's#"'^#/#'"' | nl -ba" in /Users/surahli/Documents/ai-writing-suite
hook: PostToolUse
 succeeded in 115ms:
     1	/skills/ai-writing-suite/.claude-plugin/plugin.json
     2	/skills/ai-writing-suite/.codex-plugin/plugin.json
     3	/skills/ai-writing-suite/CHANGELOG.md
     4	/skills/ai-writing-suite/LICENSE
     5	/skills/ai-writing-suite/NOTICE.md
     6	/skills/ai-writing-suite/README.md
     7	/skills/ai-writing-suite/SKILL.md
     8	/skills/ai-writing-suite/_shared/host-profile-template.md
     9	/skills/ai-writing-suite/_shared/knowledge/.gitkeep
    10	/skills/ai-writing-suite/_shared/knowledge/INDEX.md
    11	/skills/ai-writing-suite/_shared/knowledge/README.md
    12	/skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md
    13	/skills/ai-writing-suite/_shared/knowledge/audience.md
    14	/skills/ai-writing-suite/_shared/knowledge/clarity.md
    15	/skills/ai-writing-suite/_shared/knowledge/revision.md
    16	/skills/ai-writing-suite/_shared/knowledge/structure.md
    17	/skills/ai-writing-suite/_shared/knowledge/tone.md
    18	/skills/ai-writing-suite/_shared/learned-rules.md
    19	/skills/ai-writing-suite/_shared/patterns/00-index.md
    20	/skills/ai-writing-suite/_shared/patterns/communication-artifacts.md
    21	/skills/ai-writing-suite/_shared/patterns/hedging-filler.md
    22	/skills/ai-writing-suite/_shared/patterns/lexical-tells.md
    23	/skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md
    24	/skills/ai-writing-suite/_shared/patterns/rhythm-stylometric.md
    25	/skills/ai-writing-suite/_shared/patterns/significance-attribution.md
    26	/skills/ai-writing-suite/_shared/patterns/structural-tells.md
    27	/skills/ai-writing-suite/_shared/self-improvement.md
    28	/skills/ai-writing-suite/_shared/voice-profile.md
    29	/skills/ai-writing-suite/evals/README.md
    30	/skills/ai-writing-suite/evals/__pycache__/smoke_test.cpython-314.pyc
    31	/skills/ai-writing-suite/evals/detector/__init__.py
    32	/skills/ai-writing-suite/evals/detector/cli.py
    33	/skills/ai-writing-suite/evals/detector/detector.py
    34	/skills/ai-writing-suite/evals/detector/patterns.py
    35	/skills/ai-writing-suite/evals/detector/test_detector.py
    36	/skills/ai-writing-suite/evals/fixtures/__init__.py
    37	/skills/ai-writing-suite/evals/fixtures/fixtures.json
    38	/skills/ai-writing-suite/evals/fixtures/rubric.md
    39	/skills/ai-writing-suite/evals/fixtures/run_fixtures.py
    40	/skills/ai-writing-suite/evals/fixtures/test_fixtures.py
    41	/skills/ai-writing-suite/evals/smoke_test.py
    42	/skills/ai-writing-suite/skills/comms-draft/SKILL.md
    43	/skills/ai-writing-suite/skills/comms-polish/SKILL.md
    44	/skills/ai-writing-suite/skills/comms-qa/SKILL.md
    45	/skills/ai-writing-suite/skills/voice-onboard/SKILL.md

hook: PreToolUse Completed
exec
/bin/zsh -lc 'git diff main..HEAD -- .agents/plugins/marketplace.json .claude-plugin/marketplace.json skills/ai-writing-suite/.claude-plugin/plugin.json skills/ai-writing-suite/.codex-plugin/plugin.json README.md docs/packaging.md skills/ai-writing-suite/README.md skills/ai-writing-suite/CHANGELOG.md .gitignore' in /Users/surahli/Documents/ai-writing-suite
hook: PreToolUse Completed
exec
/bin/zsh -lc "nl -ba skills/ai-writing-suite/CHANGELOG.md | sed -n '1,170p'" in /Users/surahli/Documents/ai-writing-suite
 succeeded in 0ms:
     1	# Changelog
     2	
     3	All notable changes to the AI Writing Suite are documented here.
     4	
     5	The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
     6	and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
     7	
     8	---
     9	
    10	## [Unreleased]
    11	
    12	### Fixed
    13	- **Publishable installs across hosts** — the published repo was not actually
    14	  installable: the plugin body was gitignored (only manifests reached the remote)
    15	  and the Claude marketplace manifest was not at a resolvable location. Both Claude
    16	  and Codex now install **directly from the single source tree** via repo-root
    17	  marketplace manifests (`.claude-plugin/marketplace.json` and
    18	  `.agents/plugins/marketplace.json`), each backed by an in-source `plugin.json`.
    19	
    20	### Added
    21	- **Cursor support** — Cursor reads Anthropic-format `SKILL.md` Agent Skills from
    22	  `.cursor/skills/`; install = copy `skills/ai-writing-suite/` into a Cursor skills
    23	  directory. (Corrects the earlier plan that targeted `.cursor/rules/*.mdc`, the wrong
    24	  primitive for callable skills.)
    25	- **Per-host install Quickstart** in the README (Claude, Codex, Cursor) and a
    26	  maintainer packaging note at `docs/packaging.md`.
    27	
    28	### Removed
    29	- **Generate-and-sync packaging** (`packaging/` + `sync.sh`) — obsolete now that every
    30	  host reads the source tree directly. This eliminates the gitignored-body trap that
    31	  made v1 uninstallable and removes the per-host sync-drift surface entirely.
    32	
    33	---
    34	
    35	## [1.0.0] — 2026-06-06
    36	
    37	### Added
    38	
    39	#### Suite Foundation
    40	- **Suite skeleton and router** (`SKILL.md`) — unified entry point for writing-assistant features. Routes user intent to appropriate sub-skills.
    41	- **Sub-skill stubs** — `comms-qa` (v2), `comms-draft` (v2), `comms-polish` (v1), `voice-onboard` (v1). Each includes README and "coming in v2" notes where applicable.
    42	- **Directory structure** — standardized layout with `skills/`, `_shared/` (knowledge, patterns, voice profiles), and `packaging/` for multi-surface distribution.
    43	
    44	#### comms-polish (Enriched Humanizer)
    45	- **Consolidated pattern catalog** (`_shared/patterns/`) — deduplicated and merged seven overlapping AI-writing pattern lists into a single source of truth.
    46	  - Seven pattern files: `lexical-tells.md`, `significance-attribution.md`, `structural-tells.md`, `hedging-filler.md`, `punctuation-formatting.md`, `communication-artifacts.md`, `rhythm-stylometric.md`.
    47	  - Each pattern includes: Tell (what the model does), Fix (editing move), Before/After examples, and source attribution.
    48	  - Pattern IDs are stable and not source-specific; source lineage is traceable via `Sources` field.
    49	- **Scenario presets** (`skills/comms-polish/references/scenario-presets.md`) — templates for common write contexts: tweet, LinkedIn post, technical README, memo.
    50	- **Final-pass checklist** (`skills/comms-polish/references/final-pass-checklist.md`) — structured review points before publishing.
    51	- **Voice matching** — reads `_shared/voice-profile.md` (if present) to calibrate tone and style to the author's historical writing.
    52	- **Multiple modes** — detect (find AI tells without rewriting), review (prioritized findings), rewrite (produce polished prose), edit (modify files in place).
    53	- **0–100 score** — quantified AI-tell density for before/after comparison.
    54	- **Corrupted source cleanup** — `blader/humanizer` patterns (P31-P43) were re-derived cleanly from intent, not copied verbatim; duplicated/run-together blocks fixed.
    55	
    56	#### voice-onboard
    57	- **Interview flow** — guided conversation to collect writing samples (local files or pasted text).
    58	- **Profile distillation** — extracts author voice signature (tone, vocabulary, sentence shape, register preferences) into `_shared/voice-profile.md`.
    59	- **Host-profile template** — structured markdown format (from anti-vibe-writing) for consistent voice capture and reuse.
    60	- **Multi-surface support** — works in Claude and Codex (v1); Cursor and RovoDev support deferred to v2.
    61	
    62	#### Generic Knowledge Base Slot
    63	- **Pluggable KB foundation** (`_shared/knowledge/`) — wiki-style markdown structure (zero external dependencies) for portable knowledge ingestion and retrieval.
    64	- **INDEX.md** — navigation index for manual and programmatic lookup.
    65	- **Seed topics** — starter entries on audience, clarity, revision, structure, tone (distilled from source repos).
    66	- **Smoke-test path** (`_shared/knowledge/SMOKE-TEST.md`) — proves end-to-end ingestion → retrieval chain before `comms-qa` full RAG lands in v2.
    67	- **Design rationale:** Pure markdown + convention, not host-specific MCP tools (OMC wiki), so the slot remains portable across Claude, Codex, Cursor, and RovoDev.
    68	
    69	#### Self-Improvement Loop (Human-Gated)
    70	- **Lifecycle hook** — wired into `comms-polish` and `voice-onboard`.
    71	- **Propose → Approve → Append workflow** — after each session, suggest candidate rules based on error analysis (Autorefine methodology).
    72	- **Side-file storage** — proposed rules append to `_shared/learned-rules.md` (append-only, never auto-editing core SKILL.md).
    73	- **Eval-gated approval** — each proposed rule is measured against the eval harness before human confirmation.
    74	- **Memory patterns** — soft (session-scoped) and hard (persistent) memory shape from AI-Vibe-Writing-Skills.
    75	
    76	#### Evaluation Harness
    77	- **Before/after fixtures** (`evals/`) — across genres (tweet, LinkedIn post, README, memo).
    78	- **LLM-judged scoring** — rubric-based evaluation using Claude as a judge.
    79	- **Baseline calibration** — tuned so the baseline fails 30–40% of cases, enabling regressions to surface.
    80	- **Mechanical regression gate** — ported avoid-ai JavaScript detector as a language-agnostic reference test (Python detector to follow in v2).
    81	- **Self-improvement loop integration** — Autorefine-style error analysis and mutation; each proposed rule is eval-measured before user approval.
    82	
    83	#### Attribution & Licensing
    84	- **NOTICE.md** — comprehensive attribution for all seven source projects (anti-vibe-writing, avoid-ai-writing, AI-Vibe-Writing-Skills, nature-skills, stop-slop, blader/humanizer, aboudjem/humanizer-skill). Preserves copyright and MIT license for each.
    85	- **Pattern source legend** (`_shared/patterns/00-index.md`) — cross-reference for tracing pattern lineage.
    86	- **LICENSE** (MIT) — full license text in repository root.
    87	
    88	#### Packaging & Distribution
    89	- **Sync tooling scaffold** (`packaging/sync.sh`) — single source of truth distributed to four surfaces (Claude, Codex, Cursor, RovoDev).
    90	- **Multi-surface manifests** — `.claude-plugin/`, `.codex-plugin/`, `cursor-rules/`, `rovodev/` directories (v1: Claude + Codex only; v2: Cursor + RovoDev).
    91	- **README.md** (suite-level) — explains the four sub-skills, engine-vs-fuel KB model, self-improvement workflow, installation, and use.
    92	
    93	#### Documentation
    94	- **Design plan** (`docs/design-ai-writing-suite-v1-2026-06-06.md`) — decision log (D1–D12), risk analysis, success criteria, and v2 roadmap.
    95	- **Project CLAUDE.md** — project-specific conventions and working style.
    96	
    97	### Technical Details
    98	
    99	#### Architecture Decisions (from design plan)
   100	- **D1 (Product identity):** Full writing-assistant suite (not a narrow humanizer); OSS face of a company DS skillset.
   101	- **D2 (Reuse of 7 sources):** Absorb all MIT-licensed sources with preserved attribution.
   102	- **D3 (Architecture):** Suite = router + `comms-qa` + `comms-draft` + `comms-polish` + `voice-onboard`; self-improvement = cross-cutting hook.
   103	- **D5 (RAG mechanism):** Pure markdown KB + INDEX.md navigation, zero-dep; wiki-style structure/convention only (not OMC wiki MCP tools).
   104	- **D6 (Self-improvement safety):** Human-gated — propose deltas, user approves, append to side files; never auto-edit core logic.
   105	- **D10 (Eval framework):** Baseline calibrated to fail 30–40%; ported avoid-ai JS detector as mechanical gate; Autorefine-style error analysis.
   106	- **D12 (KB coherence):** v1 must prove one end-to-end ingestion+retrieval smoke path to guarantee company step is "drop in a Confluence page", not "build a retrieval engine".
   107	
   108	#### v1 Scope vs v2 Deferral
   109	- **Ships in v1:** Suite skeleton, `comms-polish`, `voice-onboard`, generic KB seed, self-improvement hook, eval harness, Claude + Codex packaging, NOTICE/CHANGELOG/README.
   110	- **Deferred to v2:** `comms-qa` full RAG, `comms-draft`, Confluence ingestion, programmatic detector, Cursor + RovoDev packaging, bilingual Chinese path, embedding index.
   111	
   112	### Compatibility
   113	
   114	- **Target environments:** Claude, Codex (v1); Cursor, RovoDev (v2).
   115	- **Dependencies:** None (pure markdown, zero external packages).
   116	- **Knowledge base:** Pluggable slot designed for OSS (generic best-practices KB shipped) and company use (proprietary DS Comms Playbook via Confluence).
   117	
   118	### Verification
   119	
   120	- Suite loads without error in Claude and Codex.
   121	- One end-to-end polish demo: before/after text with score.
   122	- Pattern catalog deduplication verified; no orphaned source references.
   123	- Self-improvement loop proposed and approved a rule end-to-end.
   124	- Generic KB smoke test: markdown page ingested, correct passage retrieved.
   125	
   126	---
   127	
   128	## Future Versions
   129	
   130	### v2 Roadmap (Not in this release)
   131	
   132	- `comms-qa` — full wiki-RAG over knowledge base.
   133	- `comms-draft` — playbook-guided drafting flow.
   134	- Confluence ingestion — company step adds playbook via web page link.
   135	- Programmatic detector — Python version + CI integration.
   136	- Cursor + RovoDev packaging — surface-specific manifests.
   137	- Bilingual Chinese path — full support for 中 content.
   138	- Optional embedding index — dense retrieval for large playbooks.
   139	
   140	---
   141	
   142	## Contributing
   143	
   144	See `docs/design-ai-writing-suite-v1-2026-06-06.md` for design decisions and the engine-vs-fuel principle. All absorbed material is MIT-licensed; new contributions should follow the same.
   145	
   146	---
   147	
   148	## License
   149	
   150	MIT License. See `LICENSE` and `NOTICE.md` for details.

hook: PostToolUse
hook: PostToolUse
 succeeded in 616ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
diff --git a/.agents/plugins/marketplace.json b/.agents/plugins/marketplace.json
new file mode 100644
index 0000000..c60e71e
--- /dev/null
+++ b/.agents/plugins/marketplace.json
@@ -0,0 +1,20 @@
+{
+  "name": "ai-writing-suite",
+  "interface": {
+    "displayName": "AI Writing Suite"
+  },
+  "plugins": [
+    {
+      "name": "ai-writing-suite",
+      "source": {
+        "source": "local",
+        "path": "./skills/ai-writing-suite"
+      },
+      "policy": {
+        "installation": "AVAILABLE",
+        "authentication": "ON_INSTALL"
+      },
+      "category": "Productivity"
+    }
+  ]
+}
diff --git a/.claude-plugin/marketplace.json b/.claude-plugin/marketplace.json
new file mode 100644
index 0000000..5cec3ee
--- /dev/null
+++ b/.claude-plugin/marketplace.json
@@ -0,0 +1,17 @@
+{
+  "$schema": "https://json.schemastore.org/claude-code-marketplace.json",
+  "name": "ai-writing-suite",
+  "description": "Writing-assistant skill suite — polish/de-AI prose, learn an author's voice, and (v2) answer questions from a knowledge base and draft from it.",
+  "owner": {
+    "name": "surahli123"
+  },
+  "plugins": [
+    {
+      "name": "ai-writing-suite",
+      "source": "./skills/ai-writing-suite",
+      "description": "Suite of writing-assistant skills for professional and product communication. Polish and de-AI prose, learn an author's voice, and (v2) answer KB questions and draft from a knowledge base.",
+      "category": "productivity",
+      "keywords": ["writing", "editing", "humanize", "voice", "comms", "polish"]
+    }
+  ]
+}
diff --git a/.gitignore b/.gitignore
index 64cc13d..bded6b6 100644
--- a/.gitignore
+++ b/.gitignore
@@ -3,16 +3,3 @@ __pycache__/
 
 # OMC runtime state
 .omc/
-
-# Generated suite packages — regenerate with: bash skills/ai-writing-suite/packaging/sync.sh
-# (manifest dirs are kept as source; only the copied/generated content is ignored)
-skills/ai-writing-suite/packaging/claude/*
-!skills/ai-writing-suite/packaging/claude/.claude-plugin
-# Codex marketplace: keep hand-maintained manifests, ignore generated content
-skills/ai-writing-suite/packaging/codex/*
-!skills/ai-writing-suite/packaging/codex/.agents
-!skills/ai-writing-suite/packaging/codex/plugins
-skills/ai-writing-suite/packaging/codex/plugins/*
-!skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite
-skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/*
-!skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/.codex-plugin
diff --git a/README.md b/README.md
index dfa1fac..49ec8f1 100644
--- a/README.md
+++ b/README.md
@@ -21,23 +21,67 @@ approve before anything is written. Core skill logic is never auto-edited.
 
 ## Status
 
-**v1 in progress.** Today the suite ships the polish/humanize capability; the v1 build adds
-a suite skeleton + router, an enriched `comms-polish`, `voice-onboard`, a generic KB seed
-with an end-to-end retrieval smoke path, an eval harness, and the self-improvement hook.
+**v1 — built, verified, and installable on Claude, Codex, and Cursor.** Ships the polish/de-AI
+capability (`comms-polish`), voice learning (`voice-onboard`), a generic pluggable KB seed with an
+end-to-end retrieval smoke path, an eval harness (Python AI-tell detector + fixtures), and a
+human-gated self-improvement hook. `comms-qa` (KB Q&A) and `comms-draft` are v2 stubs.
 
 - **Plan (read first):** [`docs/design-ai-writing-suite-v1-2026-06-06.md`](docs/design-ai-writing-suite-v1-2026-06-06.md)
   — decision log D1–D12, v1 scope, risks, eng+ceo review report.
 
+## Install
+
+One source of truth (`skills/ai-writing-suite/`) published to three hosts.
+
+### Claude Code
+
+```bash
+claude plugin marketplace add surahli123/ai-writing-suite
+claude plugin install ai-writing-suite@ai-writing-suite
+```
+
+Claude auto-discovers the sub-skills (`comms-polish`, `voice-onboard`, …); invoke by asking it to
+polish/review prose, or call a skill by name.
+
+### Codex
+
+```bash
+codex plugin marketplace add surahli123/ai-writing-suite
+codex plugin add ai-writing-suite@ai-writing-suite
+```
+
+Codex resolves the plugin from the same source tree — no `--sparse` needed; the Codex
+marketplace manifest sits at the repo root (`.agents/plugins/marketplace.json`).
+
+### Cursor
+
+Cursor reads Anthropic-format **Agent Skills** from `.cursor/skills/` — there is no marketplace, so
+copy the skill tree into a discovery location:
+
+```bash
+git clone https://github.com/surahli123/ai-writing-suite
+cp -R ai-writing-suite/skills/ai-writing-suite ~/.cursor/skills/ai-writing-suite
+```
+
+(Or copy into your project's `.cursor/skills/` for project-scoped use.) Cursor discovers the skills
+on the next session; invoke with `/comms-polish`, `/voice-onboard`, … or by intent.
+
 ## Repo Layout
 
 ```text
+.claude-plugin/marketplace.json    # Claude marketplace  → points at the source tree
+.agents/plugins/marketplace.json   # Codex marketplace   → points at the source tree
 skills/
-  ai-writing-suite/        # the suite (router + sub-skills as the build progresses)
-    SKILL.md
-    README.md
-    NOTICE.md
-    LICENSE
-docs/                      # design docs, handovers, migration notes
+  ai-writing-suite/                # THE SUITE — single source of truth
+                                   #   (Claude + Codex install this; Cursor copies it)
+    SKILL.md                       # thin router
+    .claude-plugin/plugin.json     # Claude plugin manifest
+    .codex-plugin/plugin.json      # Codex plugin manifest
+    skills/                        # sub-skills: comms-polish, voice-onboard, comms-qa*, comms-draft*
+    _shared/                       # patterns (engine) + knowledge (swappable KB) + voice profile
+    evals/                         # AI-tell detector + fixtures + smoke tests
+    NOTICE.md  LICENSE  README.md  CHANGELOG.md
+docs/                              # design docs, handovers, plans, packaging  (* = v2 stub)
 ```
 
 ## Attribution
diff --git a/docs/packaging.md b/docs/packaging.md
new file mode 100644
index 0000000..ebdd0a5
--- /dev/null
+++ b/docs/packaging.md
@@ -0,0 +1,55 @@
+# Packaging & Publishing (maintainer note)
+
+**Model: one source tree, read directly by every host.** There is no build/generate step.
+The single source of truth is `skills/ai-writing-suite/`. Each host gets a tiny manifest that
+*points at* that tree (or, for Cursor, copies it). Nothing is duplicated or generated, so there
+is no sync-drift surface.
+
+> This replaces the earlier generate-and-sync approach (`packaging/` + `sync.sh`), which was
+> removed: its generated bodies were gitignored, which is what made v1 uninstallable.
+
+## The four manifests
+
+| File | Host | Role |
+|---|---|---|
+| `/.claude-plugin/marketplace.json` | Claude | Marketplace catalog; `plugins[].source = "./skills/ai-writing-suite"` |
+| `/skills/ai-writing-suite/.claude-plugin/plugin.json` | Claude | Plugin identity (name, version, metadata) |
+| `/.agents/plugins/marketplace.json` | Codex | Marketplace catalog; `plugins[].source = {source:"local", path:"./skills/ai-writing-suite"}` |
+| `/skills/ai-writing-suite/.codex-plugin/plugin.json` | Codex | Plugin identity (+ `"skills": "./skills/"`, `interface{}`) |
+
+Both root marketplaces point at the **same** source tree. Claude auto-discovers the sub-skills
+under `skills/ai-writing-suite/skills/`; the root `SKILL.md` is a documentation router.
+
+## Install (end users)
+
+- **Claude:** `claude plugin marketplace add surahli123/ai-writing-suite` → `claude plugin install ai-writing-suite@ai-writing-suite`
+- **Codex:** `codex plugin marketplace add surahli123/ai-writing-suite` → `codex plugin add ai-writing-suite@ai-writing-suite`
+- **Cursor:** copy `skills/ai-writing-suite/` into `~/.cursor/skills/ai-writing-suite/` (or a project's `.cursor/skills/`). Cursor reads Anthropic-format `SKILL.md` Agent Skills natively; no manifest needed. (Not `.cursor/rules/*.mdc` — that is passive context injection, the wrong primitive for callable skills.)
+
+## Versioning / updates
+
+1. Bump `version:` in the source `SKILL.md` frontmatter (if present) and in the two `plugin.json`
+   files (`.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`).
+2. Commit + push. Consumers refresh via `claude plugin update` / `codex plugin marketplace upgrade`.
+3. (Optional) cut a git tag (`claude plugin tag` for Claude; a git tag for Codex `--ref` pinning)
+   **after** verifying a real-remote install.
+
+## Verify before publishing
+
+- `claude plugin validate .` and `claude plugin validate skills/ai-writing-suite` (both must pass).
+- Local install smoke per host (add the local path as a marketplace, install, confirm the skill
+  loads, then remove — restore your config). For Cursor, validate the `SKILL.md` frontmatter `name:`
+  matches each folder.
+- **Local green ≠ remote-installable.** After pushing, run a real-remote smoke
+  (`marketplace add surahli123/ai-writing-suite`) before tagging a release.
+
+## Engine vs fuel
+
+`_shared/patterns/` is the *engine* (de-AI rules) and must survive a KB swap. `_shared/knowledge/`
+is the *fuel* — the generic OSS KB; a company fork drops its real playbook into the same slot
+(never committed to this public repo).
+
+## Deferred (v2)
+
+RovoDev packaging. It will follow the same source-pointing model (explicit intent routing via the
+suite router, since RovoDev does not auto-trigger skills).
diff --git a/skills/ai-writing-suite/.claude-plugin/plugin.json b/skills/ai-writing-suite/.claude-plugin/plugin.json
new file mode 100644
index 0000000..7daac74
--- /dev/null
+++ b/skills/ai-writing-suite/.claude-plugin/plugin.json
@@ -0,0 +1,12 @@
+{
+  "name": "ai-writing-suite",
+  "description": "Suite of writing-assistant skills for professional and product communication. Polish and de-AI prose, learn an author's voice, answer KB questions, and draft from a knowledge base.",
+  "version": "1.0.0",
+  "author": {
+    "name": "surahli123"
+  },
+  "homepage": "https://github.com/surahli123/ai-writing-suite",
+  "repository": "https://github.com/surahli123/ai-writing-suite",
+  "license": "MIT",
+  "keywords": ["writing", "editing", "humanize", "voice", "comms", "polish"]
+}
diff --git a/skills/ai-writing-suite/.codex-plugin/plugin.json b/skills/ai-writing-suite/.codex-plugin/plugin.json
new file mode 100644
index 0000000..d74b6d2
--- /dev/null
+++ b/skills/ai-writing-suite/.codex-plugin/plugin.json
@@ -0,0 +1,19 @@
+{
+  "name": "ai-writing-suite",
+  "version": "1.0.0",
+  "description": "Suite of writing-assistant skills for professional and product communication. Polish and de-AI prose, learn an author's voice, answer KB questions, and draft from a knowledge base.",
+  "author": { "name": "surahli123" },
+  "homepage": "https://github.com/surahli123/ai-writing-suite",
+  "repository": "https://github.com/surahli123/ai-writing-suite",
+  "license": "MIT",
+  "keywords": ["writing", "editing", "humanize", "voice", "comms", "polish"],
+  "skills": "./skills/",
+  "interface": {
+    "displayName": "AI Writing Suite",
+    "shortDescription": "Polish/de-AI prose, learn an author's voice, KB-guided writing.",
+    "longDescription": "A suite of writing-assistant skills: polish and de-AI prose while preserving meaning and voice, learn an author's historical voice into a reusable profile, and (in v2) answer questions from and draft against a pluggable knowledge base.",
+    "developerName": "surahli123",
+    "category": "Productivity",
+    "capabilities": ["Read", "Write"]
+  }
+}
diff --git a/skills/ai-writing-suite/CHANGELOG.md b/skills/ai-writing-suite/CHANGELOG.md
index 8bd5776..84b2386 100644
--- a/skills/ai-writing-suite/CHANGELOG.md
+++ b/skills/ai-writing-suite/CHANGELOG.md
@@ -7,6 +7,31 @@ and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0
 
 ---
 
+## [Unreleased]
+
+### Fixed
+- **Publishable installs across hosts** — the published repo was not actually
+  installable: the plugin body was gitignored (only manifests reached the remote)
+  and the Claude marketplace manifest was not at a resolvable location. Both Claude
+  and Codex now install **directly from the single source tree** via repo-root
+  marketplace manifests (`.claude-plugin/marketplace.json` and
+  `.agents/plugins/marketplace.json`), each backed by an in-source `plugin.json`.
+
+### Added
+- **Cursor support** — Cursor reads Anthropic-format `SKILL.md` Agent Skills from
+  `.cursor/skills/`; install = copy `skills/ai-writing-suite/` into a Cursor skills
+  directory. (Corrects the earlier plan that targeted `.cursor/rules/*.mdc`, the wrong
+  primitive for callable skills.)
+- **Per-host install Quickstart** in the README (Claude, Codex, Cursor) and a
+  maintainer packaging note at `docs/packaging.md`.
+
+### Removed
+- **Generate-and-sync packaging** (`packaging/` + `sync.sh`) — obsolete now that every
+  host reads the source tree directly. This eliminates the gitignored-body trap that
+  made v1 uninstallable and removes the per-host sync-drift surface entirely.
+
+---
+
 ## [1.0.0] — 2026-06-06
 
 ### Added

hook: PostToolUse Completed
hook: PostToolUse Completed
hook: PostToolUse Completed
codex
The source tree also contains ignored `__pycache__` output under `evals/`, but it is not tracked and `.gitignore` covers it. I’m not treating that as a merge issue for the final commit.
hook: PreToolUse
hook: PreToolUse
hook: PreToolUse
hook: PreToolUse Completed
hook: PreToolUse Completed
hook: PreToolUse Completed
exec
/bin/zsh -lc "nl -ba skills/ai-writing-suite/SKILL.md | sed -n '1,120p'" in /Users/surahli/Documents/ai-writing-suite
 succeeded in 0ms:
     1	---
     2	name: ai-writing-suite
     3	description: A suite of writing-assistant skills for professional and product communication — polish/de-AI prose, learn an author's voice, and (later) answer questions from a knowledge base and draft from it. Routes a request to the right sub-skill. Use for docs, emails, posts, reports, and user-facing copy; not for source-code cleanup.
     4	---
     5	
     6	# AI Writing Suite (router)
     7	
     8	This is a thin router. It does not contain polishing or drafting logic itself —
     9	it points the host at the sub-skill that does the work. Think of it as the
    10	dispatch layer in front of four specialized writers.
    11	
    12	## Sub-skills
    13	
    14	| Sub-skill | What it does | Status |
    15	| --- | --- | --- |
    16	| `comms-polish` | Polish, review, detect, or edit prose to remove AI tells while preserving meaning and voice. 0-100 AI-tell score on demand. | **available (v1)** |
    17	| `voice-onboard` | Interview the author and distill their historical writing into a reusable voice profile that `comms-polish` reads. | built in Layer 1 |
    18	| `comms-qa` | Answer questions from the knowledge base (mini-RAG over the pluggable KB). | coming in v2 |
    19	| `comms-draft` | Draft a new page guided by the knowledge base / playbook. | coming in v2 |
    20	
    21	The sub-skills live under `skills/<name>/SKILL.md`. Shared assets (the AI-tell
    22	pattern catalog, and later the voice profile and learned-rules log) live under
    23	`_shared/`.
    24	
    25	## How routing works
    26	
    27	The right dispatch path depends on the host. Two cases:
    28	
    29	### Claude / Codex / Cursor — host-native dispatch
    30	
    31	These hosts already discover and trigger skills by their `name` + `description`.
    32	Do **not** intercept or re-route here. Let the host pick the sub-skill from the
    33	request. This router exists mainly as documentation and as the package entry
    34	point; it is not a runtime interceptor on these surfaces. (Reinventing host
    35	dispatch is a Layer 1 concern, deliberately out of scope.)
    36	
    37	### RovoDev — explicit intent routing
    38	
    39	RovoDev does not auto-trigger skills. When invoked there, read the user's intent
    40	and route explicitly:
    41	
    42	| If the user wants to… | Route to |
    43	| --- | --- |
    44	| clean up / de-AI / polish / review / score a draft | `comms-polish` |
    45	| teach the tool their writing style, build a voice profile | `voice-onboard` (Layer 1; until then, fall back to `comms-polish` voice matching) |
    46	| ask a question answered by the knowledge base | `comms-qa` (v2; until then, say it's not built yet) |
    47	| draft a new page from the playbook | `comms-draft` (v2; until then, say it's not built yet) |
    48	
    49	If intent is ambiguous, default to `comms-polish` (the most common job) and say
    50	which sub-skill you chose.
    51	
    52	## Boundary
    53	
    54	This suite edits and produces prose, not code. For source-code cleanup or
    55	refactoring, use a code-cleanup skill instead.
    56	
    57	## Engine vs fuel
    58	
    59	The suite is the *engine*; the knowledge base under `_shared/knowledge/` is the
    60	*fuel*. The open-source build ships a generic KB; a company fork drops its own
    61	playbook into the same slot. The playbook never enters this public repo. (This
    62	build ships a generic 5-entry KB seed + `INDEX.md` + a working retrieval smoke
    63	path; the full `comms-qa` question-answering sub-skill is v2.)

hook: PostToolUse
exec
/bin/zsh -lc "git ls-files skills/ai-writing-suite/evals | sort | nl -ba && git ls-files | rg -n '("'^|/)packaging/|sync'"\\.sh"'$'"'" in /Users/surahli/Documents/ai-writing-suite
exec
/bin/zsh -lc "git ls-files -z | xargs -0 rg -n \"\\[.*\\]\\(["'^)]*(packaging|sync'"\\.sh)["'^)]*'"\\)|"'`packaging/`|`sync'"\\.sh"'`|packaging/sync'"\\.sh|See "'`packaging/`"' in /Users/surahli/Documents/ai-writing-suite
hook: PostToolUse
 exited 1 in 474ms:
     1	skills/ai-writing-suite/evals/README.md
     2	skills/ai-writing-suite/evals/detector/__init__.py
     3	skills/ai-writing-suite/evals/detector/cli.py
     4	skills/ai-writing-suite/evals/detector/detector.py
     5	skills/ai-writing-suite/evals/detector/patterns.py
     6	skills/ai-writing-suite/evals/detector/test_detector.py
     7	skills/ai-writing-suite/evals/fixtures/__init__.py
     8	skills/ai-writing-suite/evals/fixtures/fixtures.json
     9	skills/ai-writing-suite/evals/fixtures/rubric.md
    10	skills/ai-writing-suite/evals/fixtures/run_fixtures.py
    11	skills/ai-writing-suite/evals/fixtures/test_fixtures.py
    12	skills/ai-writing-suite/evals/smoke_test.py
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead

hook: PostToolUse
 succeeded in 593ms:
zsh:1: no such file or directory: packaging/
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
zsh:1: command not found: sync.sh
zsh:1: no such file or directory: packaging/
CLAUDE.md:1:# AI Writing Suite — Project Instructions
CLAUDE.md:2:
CLAUDE.md:3:Public, MIT-licensed agent skill suite for writing assistance, packaged under `skills/`.
CLAUDE.md:4:
CLAUDE.md:5:## Repo Layout
CLAUDE.md:6:
CLAUDE.md:7:- `skills/ai-writing-suite/` — AI writing-assistant suite (currently ships the polish/humanize capability; growing into a full suite — see plan below).
CLAUDE.md:8:- `docs/` — design docs, handovers, migration notes, session closeouts.
CLAUDE.md:9:
CLAUDE.md:10:**Dedicated repo.** This was extracted (local-only) from the `personal-productivity-skills`
CLAUDE.md:11:umbrella repo on 2026-06-06; `agent-goal-contracts` stays in the umbrella. GitHub migration
CLAUDE.md:12:is deferred — there is no remote yet. Do not push or create a remote without explicit owner approval.
CLAUDE.md:13:
CLAUDE.md:14:## AI Writing Suite (active work)
CLAUDE.md:15:
CLAUDE.md:16:The OSS version of a writing-assistant skillset for a company DS team, driven by a
CLAUDE.md:17:proprietary **DS Comms Playbook** through a **pluggable knowledge base**.
CLAUDE.md:18:
CLAUDE.md:19:- **Plan (read first):** `docs/design-ai-writing-suite-v1-2026-06-06.md` — decision log
CLAUDE.md:20:  D1–D12, v1 scope, risks, eng+ceo review report.
CLAUDE.md:21:- **Engine vs fuel:** OSS ships the engine + a generic KB (distilled from 4 MIT repos).
CLAUDE.md:22:  The company forks and drops the real playbook into `_shared/knowledge/` via a Confluence
CLAUDE.md:23:  page. The playbook never enters this public repo.
CLAUDE.md:24:- **Target surfaces:** Claude + Codex (v1), Cursor + RovoDev (v2). Single source of truth
CLAUDE.md:25:  SKILL.md synced to each; do not hand-edit generated packages.
CLAUDE.md:26:- **Keep separate** from the personal `writing-vault` pipeline. That project's "AI scaffolds,
CLAUDE.md:27:  never ghostwrites" rule does NOT apply here — this suite may draft and rewrite.
CLAUDE.md:28:
CLAUDE.md:29:## Conventions
CLAUDE.md:30:
CLAUDE.md:31:- **Attribution:** absorbed material from other repos is MIT; preserve each source's
CLAUDE.md:32:  copyright + license and credit it in the skill's `NOTICE.md`.
CLAUDE.md:33:- **Skill structure:** each skill = `SKILL.md` (frontmatter `name` + `description`) +
CLAUDE.md:34:  `README.md` + `NOTICE.md` + `LICENSE`, optional `references/`, `assets/`, `evals/`.
CLAUDE.md:35:- **RAG/KB:** pure markdown + `INDEX.md`, zero external deps, portable across all target
CLAUDE.md:36:  surfaces. Do not depend on host-specific MCP tools (e.g. OMC wiki) for core retrieval.
CLAUDE.md:37:- **Evals:** a self-improving skill needs a holdout. Keep `evals/` fixtures; calibrate the
CLAUDE.md:38:  baseline to fail ~30-40% of cases so regressions are catchable.
CLAUDE.md:39:
CLAUDE.md:40:## Working Style
CLAUDE.md:41:
CLAUDE.md:42:- **Plan first.** Outline → approve → build in visible stages. The owner is the product owner.
CLAUDE.md:43:- **Git:** never commit to `main`; feature branch → PR. Show staged files before committing.
CLAUDE.md:44:- **Verify:** for skills, "done" = loads without error on target surfaces + an eval/demo
CLAUDE.md:45:  with before/after evidence, not "no errors thrown".
skills/ai-writing-suite/CHANGELOG.md:1:# Changelog
skills/ai-writing-suite/CHANGELOG.md:2:
skills/ai-writing-suite/CHANGELOG.md:3:All notable changes to the AI Writing Suite are documented here.
skills/ai-writing-suite/CHANGELOG.md:4:
skills/ai-writing-suite/CHANGELOG.md:5:The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
skills/ai-writing-suite/CHANGELOG.md:6:and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
skills/ai-writing-suite/CHANGELOG.md:7:
skills/ai-writing-suite/CHANGELOG.md:8:---
skills/ai-writing-suite/CHANGELOG.md:9:
skills/ai-writing-suite/CHANGELOG.md:10:## [Unreleased]
skills/ai-writing-suite/CHANGELOG.md:11:
skills/ai-writing-suite/CHANGELOG.md:12:### Fixed
skills/ai-writing-suite/CHANGELOG.md:13:- **Publishable installs across hosts** — the published repo was not actually
skills/ai-writing-suite/CHANGELOG.md:14:  installable: the plugin body was gitignored (only manifests reached the remote)
skills/ai-writing-suite/CHANGELOG.md:15:  and the Claude marketplace manifest was not at a resolvable location. Both Claude
skills/ai-writing-suite/CHANGELOG.md:16:  and Codex now install **directly from the single source tree** via repo-root
skills/ai-writing-suite/CHANGELOG.md:17:  marketplace manifests (`.claude-plugin/marketplace.json` and
skills/ai-writing-suite/CHANGELOG.md:18:  `.agents/plugins/marketplace.json`), each backed by an in-source `plugin.json`.
skills/ai-writing-suite/CHANGELOG.md:19:
skills/ai-writing-suite/CHANGELOG.md:20:### Added
skills/ai-writing-suite/CHANGELOG.md:21:- **Cursor support** — Cursor reads Anthropic-format `SKILL.md` Agent Skills from
skills/ai-writing-suite/CHANGELOG.md:22:  `.cursor/skills/`; install = copy `skills/ai-writing-suite/` into a Cursor skills
skills/ai-writing-suite/CHANGELOG.md:23:  directory. (Corrects the earlier plan that targeted `.cursor/rules/*.mdc`, the wrong
skills/ai-writing-suite/CHANGELOG.md:24:  primitive for callable skills.)
skills/ai-writing-suite/CHANGELOG.md:25:- **Per-host install Quickstart** in the README (Claude, Codex, Cursor) and a
skills/ai-writing-suite/CHANGELOG.md:26:  maintainer packaging note at `docs/packaging.md`.
skills/ai-writing-suite/CHANGELOG.md:27:
skills/ai-writing-suite/CHANGELOG.md:28:### Removed
skills/ai-writing-suite/CHANGELOG.md:29:- **Generate-and-sync packaging** (`packaging/` + `sync.sh`) — obsolete now that every
skills/ai-writing-suite/CHANGELOG.md:30:  host reads the source tree directly. This eliminates the gitignored-body trap that
skills/ai-writing-suite/CHANGELOG.md:31:  made v1 uninstallable and removes the per-host sync-drift surface entirely.
skills/ai-writing-suite/CHANGELOG.md:32:
skills/ai-writing-suite/CHANGELOG.md:33:---
skills/ai-writing-suite/CHANGELOG.md:34:
skills/ai-writing-suite/CHANGELOG.md:35:## [1.0.0] — 2026-06-06
skills/ai-writing-suite/CHANGELOG.md:36:
skills/ai-writing-suite/CHANGELOG.md:37:### Added
skills/ai-writing-suite/CHANGELOG.md:38:
skills/ai-writing-suite/CHANGELOG.md:39:#### Suite Foundation
skills/ai-writing-suite/CHANGELOG.md:40:- **Suite skeleton and router** (`SKILL.md`) — unified entry point for writing-assistant features. Routes user intent to appropriate sub-skills.
skills/ai-writing-suite/CHANGELOG.md:41:- **Sub-skill stubs** — `comms-qa` (v2), `comms-draft` (v2), `comms-polish` (v1), `voice-onboard` (v1). Each includes README and "coming in v2" notes where applicable.
skills/ai-writing-suite/CHANGELOG.md:42:- **Directory structure** — standardized layout with `skills/`, `_shared/` (knowledge, patterns, voice profiles), and `packaging/` for multi-surface distribution.
skills/ai-writing-suite/CHANGELOG.md:43:
skills/ai-writing-suite/CHANGELOG.md:44:#### comms-polish (Enriched Humanizer)
skills/ai-writing-suite/CHANGELOG.md:45:- **Consolidated pattern catalog** (`_shared/patterns/`) — deduplicated and merged seven overlapping AI-writing pattern lists into a single source of truth.
skills/ai-writing-suite/CHANGELOG.md:46:  - Seven pattern files: `lexical-tells.md`, `significance-attribution.md`, `structural-tells.md`, `hedging-filler.md`, `punctuation-formatting.md`, `communication-artifacts.md`, `rhythm-stylometric.md`.
skills/ai-writing-suite/CHANGELOG.md:47:  - Each pattern includes: Tell (what the model does), Fix (editing move), Before/After examples, and source attribution.
skills/ai-writing-suite/CHANGELOG.md:48:  - Pattern IDs are stable and not source-specific; source lineage is traceable via `Sources` field.
skills/ai-writing-suite/CHANGELOG.md:49:- **Scenario presets** (`skills/comms-polish/references/scenario-presets.md`) — templates for common write contexts: tweet, LinkedIn post, technical README, memo.
skills/ai-writing-suite/CHANGELOG.md:50:- **Final-pass checklist** (`skills/comms-polish/references/final-pass-checklist.md`) — structured review points before publishing.
skills/ai-writing-suite/CHANGELOG.md:51:- **Voice matching** — reads `_shared/voice-profile.md` (if present) to calibrate tone and style to the author's historical writing.
skills/ai-writing-suite/CHANGELOG.md:52:- **Multiple modes** — detect (find AI tells without rewriting), review (prioritized findings), rewrite (produce polished prose), edit (modify files in place).
skills/ai-writing-suite/CHANGELOG.md:53:- **0–100 score** — quantified AI-tell density for before/after comparison.
skills/ai-writing-suite/CHANGELOG.md:54:- **Corrupted source cleanup** — `blader/humanizer` patterns (P31-P43) were re-derived cleanly from intent, not copied verbatim; duplicated/run-together blocks fixed.
skills/ai-writing-suite/CHANGELOG.md:55:
skills/ai-writing-suite/CHANGELOG.md:56:#### voice-onboard
skills/ai-writing-suite/CHANGELOG.md:57:- **Interview flow** — guided conversation to collect writing samples (local files or pasted text).
skills/ai-writing-suite/CHANGELOG.md:58:- **Profile distillation** — extracts author voice signature (tone, vocabulary, sentence shape, register preferences) into `_shared/voice-profile.md`.
skills/ai-writing-suite/CHANGELOG.md:59:- **Host-profile template** — structured markdown format (from anti-vibe-writing) for consistent voice capture and reuse.
skills/ai-writing-suite/CHANGELOG.md:60:- **Multi-surface support** — works in Claude and Codex (v1); Cursor and RovoDev support deferred to v2.
skills/ai-writing-suite/CHANGELOG.md:61:
skills/ai-writing-suite/CHANGELOG.md:62:#### Generic Knowledge Base Slot
skills/ai-writing-suite/CHANGELOG.md:63:- **Pluggable KB foundation** (`_shared/knowledge/`) — wiki-style markdown structure (zero external dependencies) for portable knowledge ingestion and retrieval.
skills/ai-writing-suite/CHANGELOG.md:64:- **INDEX.md** — navigation index for manual and programmatic lookup.
skills/ai-writing-suite/CHANGELOG.md:65:- **Seed topics** — starter entries on audience, clarity, revision, structure, tone (distilled from source repos).
skills/ai-writing-suite/CHANGELOG.md:66:- **Smoke-test path** (`_shared/knowledge/SMOKE-TEST.md`) — proves end-to-end ingestion → retrieval chain before `comms-qa` full RAG lands in v2.
skills/ai-writing-suite/CHANGELOG.md:67:- **Design rationale:** Pure markdown + convention, not host-specific MCP tools (OMC wiki), so the slot remains portable across Claude, Codex, Cursor, and RovoDev.
skills/ai-writing-suite/CHANGELOG.md:68:
skills/ai-writing-suite/CHANGELOG.md:69:#### Self-Improvement Loop (Human-Gated)
skills/ai-writing-suite/CHANGELOG.md:70:- **Lifecycle hook** — wired into `comms-polish` and `voice-onboard`.
skills/ai-writing-suite/CHANGELOG.md:71:- **Propose → Approve → Append workflow** — after each session, suggest candidate rules based on error analysis (Autorefine methodology).
skills/ai-writing-suite/CHANGELOG.md:72:- **Side-file storage** — proposed rules append to `_shared/learned-rules.md` (append-only, never auto-editing core SKILL.md).
skills/ai-writing-suite/CHANGELOG.md:73:- **Eval-gated approval** — each proposed rule is measured against the eval harness before human confirmation.
skills/ai-writing-suite/CHANGELOG.md:74:- **Memory patterns** — soft (session-scoped) and hard (persistent) memory shape from AI-Vibe-Writing-Skills.
skills/ai-writing-suite/CHANGELOG.md:75:
skills/ai-writing-suite/CHANGELOG.md:76:#### Evaluation Harness
skills/ai-writing-suite/CHANGELOG.md:77:- **Before/after fixtures** (`evals/`) — across genres (tweet, LinkedIn post, README, memo).
skills/ai-writing-suite/CHANGELOG.md:78:- **LLM-judged scoring** — rubric-based evaluation using Claude as a judge.
skills/ai-writing-suite/CHANGELOG.md:79:- **Baseline calibration** — tuned so the baseline fails 30–40% of cases, enabling regressions to surface.
skills/ai-writing-suite/CHANGELOG.md:80:- **Mechanical regression gate** — ported avoid-ai JavaScript detector as a language-agnostic reference test (Python detector to follow in v2).
skills/ai-writing-suite/CHANGELOG.md:81:- **Self-improvement loop integration** — Autorefine-style error analysis and mutation; each proposed rule is eval-measured before user approval.
skills/ai-writing-suite/CHANGELOG.md:82:
skills/ai-writing-suite/CHANGELOG.md:83:#### Attribution & Licensing
skills/ai-writing-suite/CHANGELOG.md:84:- **NOTICE.md** — comprehensive attribution for all seven source projects (anti-vibe-writing, avoid-ai-writing, AI-Vibe-Writing-Skills, nature-skills, stop-slop, blader/humanizer, aboudjem/humanizer-skill). Preserves copyright and MIT license for each.
skills/ai-writing-suite/CHANGELOG.md:85:- **Pattern source legend** (`_shared/patterns/00-index.md`) — cross-reference for tracing pattern lineage.
skills/ai-writing-suite/CHANGELOG.md:86:- **LICENSE** (MIT) — full license text in repository root.
skills/ai-writing-suite/CHANGELOG.md:87:
skills/ai-writing-suite/CHANGELOG.md:88:#### Packaging & Distribution
skills/ai-writing-suite/CHANGELOG.md:89:- **Sync tooling scaffold** (`packaging/sync.sh`) — single source of truth distributed to four surfaces (Claude, Codex, Cursor, RovoDev).
skills/ai-writing-suite/CHANGELOG.md:90:- **Multi-surface manifests** — `.claude-plugin/`, `.codex-plugin/`, `cursor-rules/`, `rovodev/` directories (v1: Claude + Codex only; v2: Cursor + RovoDev).
skills/ai-writing-suite/CHANGELOG.md:91:- **README.md** (suite-level) — explains the four sub-skills, engine-vs-fuel KB model, self-improvement workflow, installation, and use.
skills/ai-writing-suite/CHANGELOG.md:92:
skills/ai-writing-suite/CHANGELOG.md:93:#### Documentation
skills/ai-writing-suite/CHANGELOG.md:94:- **Design plan** (`docs/design-ai-writing-suite-v1-2026-06-06.md`) — decision log (D1–D12), risk analysis, success criteria, and v2 roadmap.
skills/ai-writing-suite/CHANGELOG.md:95:- **Project CLAUDE.md** — project-specific conventions and working style.
skills/ai-writing-suite/CHANGELOG.md:96:
skills/ai-writing-suite/CHANGELOG.md:97:### Technical Details
skills/ai-writing-suite/CHANGELOG.md:98:
skills/ai-writing-suite/CHANGELOG.md:99:#### Architecture Decisions (from design plan)
skills/ai-writing-suite/CHANGELOG.md:100:- **D1 (Product identity):** Full writing-assistant suite (not a narrow humanizer); OSS face of a company DS skillset.
skills/ai-writing-suite/CHANGELOG.md:101:- **D2 (Reuse of 7 sources):** Absorb all MIT-licensed sources with preserved attribution.
skills/ai-writing-suite/CHANGELOG.md:102:- **D3 (Architecture):** Suite = router + `comms-qa` + `comms-draft` + `comms-polish` + `voice-onboard`; self-improvement = cross-cutting hook.
skills/ai-writing-suite/CHANGELOG.md:103:- **D5 (RAG mechanism):** Pure markdown KB + INDEX.md navigation, zero-dep; wiki-style structure/convention only (not OMC wiki MCP tools).
skills/ai-writing-suite/CHANGELOG.md:104:- **D6 (Self-improvement safety):** Human-gated — propose deltas, user approves, append to side files; never auto-edit core logic.
skills/ai-writing-suite/CHANGELOG.md:105:- **D10 (Eval framework):** Baseline calibrated to fail 30–40%; ported avoid-ai JS detector as mechanical gate; Autorefine-style error analysis.
skills/ai-writing-suite/CHANGELOG.md:106:- **D12 (KB coherence):** v1 must prove one end-to-end ingestion+retrieval smoke path to guarantee company step is "drop in a Confluence page", not "build a retrieval engine".
skills/ai-writing-suite/CHANGELOG.md:107:
skills/ai-writing-suite/CHANGELOG.md:108:#### v1 Scope vs v2 Deferral
skills/ai-writing-suite/CHANGELOG.md:109:- **Ships in v1:** Suite skeleton, `comms-polish`, `voice-onboard`, generic KB seed, self-improvement hook, eval harness, Claude + Codex packaging, NOTICE/CHANGELOG/README.
skills/ai-writing-suite/CHANGELOG.md:110:- **Deferred to v2:** `comms-qa` full RAG, `comms-draft`, Confluence ingestion, programmatic detector, Cursor + RovoDev packaging, bilingual Chinese path, embedding index.
skills/ai-writing-suite/CHANGELOG.md:111:
skills/ai-writing-suite/CHANGELOG.md:112:### Compatibility
skills/ai-writing-suite/CHANGELOG.md:113:
skills/ai-writing-suite/CHANGELOG.md:114:- **Target environments:** Claude, Codex (v1); Cursor, RovoDev (v2).
skills/ai-writing-suite/CHANGELOG.md:115:- **Dependencies:** None (pure markdown, zero external packages).
skills/ai-writing-suite/CHANGELOG.md:116:- **Knowledge base:** Pluggable slot designed for OSS (generic best-practices KB shipped) and company use (proprietary DS Comms Playbook via Confluence).
skills/ai-writing-suite/CHANGELOG.md:117:
skills/ai-writing-suite/CHANGELOG.md:118:### Verification
skills/ai-writing-suite/CHANGELOG.md:119:
skills/ai-writing-suite/CHANGELOG.md:120:- Suite loads without error in Claude and Codex.
skills/ai-writing-suite/CHANGELOG.md:121:- One end-to-end polish demo: before/after text with score.
skills/ai-writing-suite/CHANGELOG.md:122:- Pattern catalog deduplication verified; no orphaned source references.
skills/ai-writing-suite/CHANGELOG.md:123:- Self-improvement loop proposed and approved a rule end-to-end.
skills/ai-writing-suite/CHANGELOG.md:124:- Generic KB smoke test: markdown page ingested, correct passage retrieved.
skills/ai-writing-suite/CHANGELOG.md:125:
skills/ai-writing-suite/CHANGELOG.md:126:---
skills/ai-writing-suite/CHANGELOG.md:127:
skills/ai-writing-suite/CHANGELOG.md:128:## Future Versions
skills/ai-writing-suite/CHANGELOG.md:129:
skills/ai-writing-suite/CHANGELOG.md:130:### v2 Roadmap (Not in this release)
skills/ai-writing-suite/CHANGELOG.md:131:
skills/ai-writing-suite/CHANGELOG.md:132:- `comms-qa` — full wiki-RAG over knowledge base.
skills/ai-writing-suite/CHANGELOG.md:133:- `comms-draft` — playbook-guided drafting flow.
skills/ai-writing-suite/CHANGELOG.md:134:- Confluence ingestion — company step adds playbook via web page link.
skills/ai-writing-suite/CHANGELOG.md:135:- Programmatic detector — Python version + CI integration.
skills/ai-writing-suite/CHANGELOG.md:136:- Cursor + RovoDev packaging — surface-specific manifests.
skills/ai-writing-suite/CHANGELOG.md:137:- Bilingual Chinese path — full support for 中 content.
skills/ai-writing-suite/CHANGELOG.md:138:- Optional embedding index — dense retrieval for large playbooks.
skills/ai-writing-suite/CHANGELOG.md:139:
skills/ai-writing-suite/CHANGELOG.md:140:---
skills/ai-writing-suite/CHANGELOG.md:141:
skills/ai-writing-suite/CHANGELOG.md:142:## Contributing
skills/ai-writing-suite/CHANGELOG.md:143:
skills/ai-writing-suite/CHANGELOG.md:144:See `docs/design-ai-writing-suite-v1-2026-06-06.md` for design decisions and the engine-vs-fuel principle. All absorbed material is MIT-licensed; new contributions should follow the same.
skills/ai-writing-suite/CHANGELOG.md:145:
skills/ai-writing-suite/CHANGELOG.md:146:---
skills/ai-writing-suite/CHANGELOG.md:147:
skills/ai-writing-suite/CHANGELOG.md:148:## License
skills/ai-writing-suite/CHANGELOG.md:149:
skills/ai-writing-suite/CHANGELOG.md:150:MIT License. See `LICENSE` and `NOTICE.md` for details.
docs/design-ai-writing-suite-v1-2026-06-06.md:1:# Design Plan — AI Writing Suite (OSS) v1
docs/design-ai-writing-suite-v1-2026-06-06.md:2:
docs/design-ai-writing-suite-v1-2026-06-06.md:3:Date: 2026-06-06
docs/design-ai-writing-suite-v1-2026-06-06.md:4:Author: surahli (product owner) + Claude (grill-me session)
docs/design-ai-writing-suite-v1-2026-06-06.md:5:Status: **PLAN ONLY — awaiting explicit "go" before any code**
docs/design-ai-writing-suite-v1-2026-06-06.md:6:Repo: `~/Documents/Codex/2026-06-01/personal-productivity-skills`
docs/design-ai-writing-suite-v1-2026-06-06.md:7:Current branch: `add-ai-writing-humanizer` (behind `origin/main`, PR #3 merged)
docs/design-ai-writing-suite-v1-2026-06-06.md:8:
docs/design-ai-writing-suite-v1-2026-06-06.md:9:---
docs/design-ai-writing-suite-v1-2026-06-06.md:10:
docs/design-ai-writing-suite-v1-2026-06-06.md:11:## 1. Vision
docs/design-ai-writing-suite-v1-2026-06-06.md:12:
docs/design-ai-writing-suite-v1-2026-06-06.md:13:Turn the existing single-purpose `ai-writing-humanizer` skill into the **open-source
docs/design-ai-writing-suite-v1-2026-06-06.md:14:version of a writing-assistant skill SET** that surahli will build for the company's
docs/design-ai-writing-suite-v1-2026-06-06.md:15:Data Scientists. The company version is driven by a proprietary **DS Comms Playbook**;
docs/design-ai-writing-suite-v1-2026-06-06.md:16:the OSS version ships the same engine with a generic best-practices knowledge base.
docs/design-ai-writing-suite-v1-2026-06-06.md:17:
docs/design-ai-writing-suite-v1-2026-06-06.md:18:The suite does four things:
docs/design-ai-writing-suite-v1-2026-06-06.md:19:1. **Knowledge QA / mini-RAG** over the comms playbook + real-world best practices.
docs/design-ai-writing-suite-v1-2026-06-06.md:20:2. **Guided drafting** of a page, using the playbook.
docs/design-ai-writing-suite-v1-2026-06-06.md:21:3. **Polish / review** of a page, using the playbook + best practices (this is the
docs/design-ai-writing-suite-v1-2026-06-06.md:22:   piece that already half-exists today as `ai-writing-humanizer`).
docs/design-ai-writing-suite-v1-2026-06-06.md:23:4. **Voice learning + proactive self-improvement** — learn the user's historical
docs/design-ai-writing-suite-v1-2026-06-06.md:24:   writing style; each session propose new rules (human-gated) to get better.
docs/design-ai-writing-suite-v1-2026-06-06.md:25:
docs/design-ai-writing-suite-v1-2026-06-06.md:26:> **Engine vs Fuel principle:** the OSS repo is the *engine*; the playbook is *fuel*.
docs/design-ai-writing-suite-v1-2026-06-06.md:27:> The knowledge base is a pluggable asset. OSS bundles a generic KB distilled from the
docs/design-ai-writing-suite-v1-2026-06-06.md:28:> 4 reference repos. The company fork drops the real DS Comms Playbook into the same slot.
docs/design-ai-writing-suite-v1-2026-06-06.md:29:> The playbook **never** enters the public repo.
docs/design-ai-writing-suite-v1-2026-06-06.md:30:
docs/design-ai-writing-suite-v1-2026-06-06.md:31:---
docs/design-ai-writing-suite-v1-2026-06-06.md:32:
docs/design-ai-writing-suite-v1-2026-06-06.md:33:## 2. Decision Log (resolved in grill-me session)
docs/design-ai-writing-suite-v1-2026-06-06.md:34:
docs/design-ai-writing-suite-v1-2026-06-06.md:35:| # | Decision | Choice | Rationale |
docs/design-ai-writing-suite-v1-2026-06-06.md:36:|---|----------|--------|-----------|
docs/design-ai-writing-suite-v1-2026-06-06.md:37:| D1 | Product identity | **Full writing-assistant suite** (not a narrow humanizer) | OSS face of a company DS skillset |
docs/design-ai-writing-suite-v1-2026-06-06.md:38:| D2 | Reuse of 4 ref repos | **Absorb all**, attribute in NOTICE | All MIT-licensed → copy/derive OK with copyright + license retained |
docs/design-ai-writing-suite-v1-2026-06-06.md:39:| D2b | nature-skills scope | **Only `nature-writing` + `nature-polishing`** | Other 28k lines are paper2ppt/citation/academic — irrelevant |
docs/design-ai-writing-suite-v1-2026-06-06.md:40:| D3 | Architecture | **Suite**: router + `comms-qa` + `comms-draft` + `comms-polish` + `voice-onboard`; self-improvement = cross-cutting hook | Matches the 4 functions; nature-skills suite shape |
docs/design-ai-writing-suite-v1-2026-06-06.md:41:| D3b | Router weight (eng-review) | **Thin router**: a documentation/entry skill listing sub-skills. Claude/Codex/Cursor use host-native skill dispatch (no interception). Explicit intent routing ONLY on RovoDev (no auto-trigger). | Avoids reinventing host dispatch ([Layer 1]) |
docs/design-ai-writing-suite-v1-2026-06-06.md:42:| D10 | Eval + self-improvement (eng-review) | **eval harness in v1**: (a) before/after fixtures across genres, LLM-judged, baseline calibrated to fail 30-40%; (b) ported avoid-ai JS detector as mechanical regression gate; (c) self-improvement loop borrows **Autorefine** methodology — Hamel Three Gulfs + error analysis + Karpathy mutation. Each proposed rule is eval-measured before human approval. | A self-improving skill needs a holdout; matches CLAUDE.md eval-calibration rule |
docs/design-ai-writing-suite-v1-2026-06-06.md:43:| D11 | Build sequencing (ceo-review) | **OSS engine first; playbook dropped in later via Confluence page → `knowledge/` slot** (company step = add data, not build engine). | OSS-first is low-risk + produces public artifact; playbook integration designed as near-zero-effort |
docs/design-ai-writing-suite-v1-2026-06-06.md:44:| D12 | Ingestion/retrieval coherence (ceo-review) | **v1 must prove ONE end-to-end ingestion+retrieval smoke path** (markdown/Confluence page → INDEX → correct passage retrieved), even though full `comms-qa` is v2. | Without it, the "just add a Confluence page" promise is hollow — company step would still need an unbuilt RAG engine |
docs/design-ai-writing-suite-v1-2026-06-06.md:45:| D4 | OSS / company boundary | **Pluggable KB + bundled generic KB** | Engine reusable, playbook stays private |
docs/design-ai-writing-suite-v1-2026-06-06.md:46:| D5 | RAG mechanism | **Pure markdown KB + INDEX.md navigation, zero-dep.** "Wiki-style" = structure/convention only (entries + index + cross-links), NOT OMC wiki MCP tools (those are Claude+OMC-only and break on Codex/Cursor/RovoDev). OMC `wiki_*` tools = optional Claude-side accelerator. | Portable across all 4 surfaces (D8); keyword/navigation recall beats dense retrieval for a moderate playbook |
docs/design-ai-writing-suite-v1-2026-06-06.md:47:| D6 | Self-improvement safety | **Human-gated** — propose deltas, user approves, append to side files; never auto-edit core SKILL.md | Prevents drift/degradation; suits high-value/company use |
docs/design-ai-writing-suite-v1-2026-06-06.md:48:| D7 | Voice sample source | **Local files/paste (primary) + Confluence page link** | Company DS history lives in folders + Confluence; KB can use same ingestion |
docs/design-ai-writing-suite-v1-2026-06-06.md:49:| D8 | Target environments | **Claude + Codex + Cursor + RovoDev** (single source → 4 packages) | surahli uses Claude; company may use any; RovoDev = constrained in-house agent |
docs/design-ai-writing-suite-v1-2026-06-06.md:50:| D9 | v1 scope | **Vertical slice: enriched polish + voice-onboard + suite skeleton** | Polish is half-built; voice is the differentiator; QA/draft are heaviest net-new |
docs/design-ai-writing-suite-v1-2026-06-06.md:51:
docs/design-ai-writing-suite-v1-2026-06-06.md:52:---
docs/design-ai-writing-suite-v1-2026-06-06.md:53:
docs/design-ai-writing-suite-v1-2026-06-06.md:54:## 3. What each reference repo contributes (all MIT)
docs/design-ai-writing-suite-v1-2026-06-06.md:55:
docs/design-ai-writing-suite-v1-2026-06-06.md:56:| Repo | Absorbed contribution | Lands in |
docs/design-ai-writing-suite-v1-2026-06-06.md:57:|---|---|---|
docs/design-ai-writing-suite-v1-2026-06-06.md:58:| **weijt606/anti-vibe-writing** | Bilingual (中/EN) pattern sets, `scenario-presets`, `learning-mode`, `host-profile` voice template, `final-pass-checklist`, before/after benchmarks | `comms-polish` references + `voice-onboard` template |
docs/design-ai-writing-suite-v1-2026-06-06.md:59:| **conorbronsdon/avoid-ai-writing** | Programmatic JS detector + tests + CI, CATEGORIES taxonomy, multi-surface packaging (Claude plugin + Cursor `.mdc`) + `sync-plugin-skill.sh` | Detector (v2), packaging/sync scaffold, Cursor target |
docs/design-ai-writing-suite-v1-2026-06-06.md:60:| **donghuixin/AI-Vibe-Writing-Skills** | Local AI-detector idea, style-extractor / reviewer agent prompts, soft/hard memory pattern | Optional detector (v2), `voice-onboard` distillation prompt, self-improvement memory shape |
docs/design-ai-writing-suite-v1-2026-06-06.md:61:| **Yuan1z0825/nature-skills** (`nature-writing` + `nature-polishing` only) | Academic polish/writing rubric, codex/plugin manifest conventions | `comms-polish` rubric, packaging conventions |
docs/design-ai-writing-suite-v1-2026-06-06.md:62:| **(existing) installed refs** | `stop-slop` (8 rules), `blader-humanizer` (43 patterns — **corrupted text, must clean**), `aboudjem-humanizer` (Wikipedia 30 patterns) | Consolidated into ONE clean pattern catalog |
docs/design-ai-writing-suite-v1-2026-06-06.md:63:
docs/design-ai-writing-suite-v1-2026-06-06.md:64:**Attribution rule:** `NOTICE.md` lists every source repo + author + MIT copyright line +
docs/design-ai-writing-suite-v1-2026-06-06.md:65:link. Replaces the current "we avoided wholesale reuse" wording (D2 reverses that stance,
docs/design-ai-writing-suite-v1-2026-06-06.md:66:which is fine under MIT as long as notices are preserved).
docs/design-ai-writing-suite-v1-2026-06-06.md:67:
docs/design-ai-writing-suite-v1-2026-06-06.md:68:---
docs/design-ai-writing-suite-v1-2026-06-06.md:69:
docs/design-ai-writing-suite-v1-2026-06-06.md:70:## 4. Target architecture (full, eventual)
docs/design-ai-writing-suite-v1-2026-06-06.md:71:
docs/design-ai-writing-suite-v1-2026-06-06.md:72:```
docs/design-ai-writing-suite-v1-2026-06-06.md:73:ai-writing-suite/                      # OSS repo (rename or keep ai-writing-humanizer)
docs/design-ai-writing-suite-v1-2026-06-06.md:74:├── SKILL.md (router)                  # detects intent → routes to qa/draft/polish/voice
docs/design-ai-writing-suite-v1-2026-06-06.md:75:├── skills/
docs/design-ai-writing-suite-v1-2026-06-06.md:76:│   ├── comms-qa/        SKILL.md      # ① mini-RAG over KB (wiki-style)
docs/design-ai-writing-suite-v1-2026-06-06.md:77:│   ├── comms-draft/     SKILL.md      # ② playbook-guided drafting
docs/design-ai-writing-suite-v1-2026-06-06.md:78:│   ├── comms-polish/    SKILL.md      # ③ polish/review/de-AI (enriched humanizer)
docs/design-ai-writing-suite-v1-2026-06-06.md:79:│   └── voice-onboard/   SKILL.md      # ④ interview + distill historical writing
docs/design-ai-writing-suite-v1-2026-06-06.md:80:├── _shared/
docs/design-ai-writing-suite-v1-2026-06-06.md:81:│   ├── knowledge/                     # PLUGGABLE KB (OSS=generic; company=playbook)
docs/design-ai-writing-suite-v1-2026-06-06.md:82:│   │   ├── INDEX.md                   # wiki-style index for navigation/recall
docs/design-ai-writing-suite-v1-2026-06-06.md:83:│   │   └── *.md                       # topic entries (ingested via wiki_ingest pattern)
docs/design-ai-writing-suite-v1-2026-06-06.md:84:│   ├── patterns/                      # ONE consolidated AI-tell catalog (dedup of 3+4 sources)
docs/design-ai-writing-suite-v1-2026-06-06.md:85:│   ├── voice-profile.md              # learned user style (read every session)
docs/design-ai-writing-suite-v1-2026-06-06.md:86:│   ├── learned-rules.md             # human-gated self-improvement log (append-only)
docs/design-ai-writing-suite-v1-2026-06-06.md:87:│   └── host-profile-template.md     # from anti-vibe
docs/design-ai-writing-suite-v1-2026-06-06.md:88:├── packaging/
docs/design-ai-writing-suite-v1-2026-06-06.md:89:│   ├── sync.sh                        # single source → 4 targets
docs/design-ai-writing-suite-v1-2026-06-06.md:90:│   ├── .claude-plugin/ .codex-plugin/ cursor-rules/ rovodev/
docs/design-ai-writing-suite-v1-2026-06-06.md:91:├── NOTICE.md  LICENSE  README.md  CHANGELOG.md
docs/design-ai-writing-suite-v1-2026-06-06.md:92:```
docs/design-ai-writing-suite-v1-2026-06-06.md:93:
docs/design-ai-writing-suite-v1-2026-06-06.md:94:Self-improvement = lifecycle hook in **every** sub-skill: on start, read
docs/design-ai-writing-suite-v1-2026-06-06.md:95:`voice-profile.md` + `learned-rules.md`; on end, **propose** candidate rules → user
docs/design-ai-writing-suite-v1-2026-06-06.md:96:approves → append. Core SKILL.md logic is never auto-modified.
docs/design-ai-writing-suite-v1-2026-06-06.md:97:
docs/design-ai-writing-suite-v1-2026-06-06.md:98:---
docs/design-ai-writing-suite-v1-2026-06-06.md:99:
docs/design-ai-writing-suite-v1-2026-06-06.md:100:## 5. v1 scope (this build)
docs/design-ai-writing-suite-v1-2026-06-06.md:101:
docs/design-ai-writing-suite-v1-2026-06-06.md:102:**Ships:**
docs/design-ai-writing-suite-v1-2026-06-06.md:103:1. **Suite skeleton + router** — directory structure above; router SKILL.md that routes
docs/design-ai-writing-suite-v1-2026-06-06.md:104:   intent (v1 router only needs to reach `comms-polish` + `voice-onboard`; qa/draft are
docs/design-ai-writing-suite-v1-2026-06-06.md:105:   stubs with "coming in v2" notes).
docs/design-ai-writing-suite-v1-2026-06-06.md:106:2. **`comms-polish`** — enrich the existing humanizer:
docs/design-ai-writing-suite-v1-2026-06-06.md:107:   - Consolidate the 3 existing refs + 4 repos into ONE clean `_shared/patterns/` catalog
docs/design-ai-writing-suite-v1-2026-06-06.md:108:     (fix the corrupted `blader-humanizer` text; dedup overlapping patterns; keep source
docs/design-ai-writing-suite-v1-2026-06-06.md:109:     tags for attribution).
docs/design-ai-writing-suite-v1-2026-06-06.md:110:   - Add `scenario-presets` (tweet / LinkedIn / README / memo) from anti-vibe.
docs/design-ai-writing-suite-v1-2026-06-06.md:111:   - Add `final-pass-checklist`.
docs/design-ai-writing-suite-v1-2026-06-06.md:112:   - Reads `voice-profile.md` if present (voice matching).
docs/design-ai-writing-suite-v1-2026-06-06.md:113:   - Keep modes: detect / review / rewrite / edit + 0–100 score.
docs/design-ai-writing-suite-v1-2026-06-06.md:114:3. **`voice-onboard`** — interview + distill from local files/paste → writes
docs/design-ai-writing-suite-v1-2026-06-06.md:115:   `voice-profile.md` using the host-profile template. (Confluence link = v2.)
docs/design-ai-writing-suite-v1-2026-06-06.md:116:4. **Generic KB seed** — `_shared/knowledge/INDEX.md` + a few topic entries distilled
docs/design-ai-writing-suite-v1-2026-06-06.md:117:   from the 4 repos (wiki-style), proving the pluggable slot. (Full `comms-qa` retrieval = v2.)
docs/design-ai-writing-suite-v1-2026-06-06.md:118:5. **Self-improvement hook (human-gated)** wired into `comms-polish` + `voice-onboard`:
docs/design-ai-writing-suite-v1-2026-06-06.md:119:   propose → approve → append to `learned-rules.md`.
docs/design-ai-writing-suite-v1-2026-06-06.md:120:6. **NOTICE.md** rewritten with all attributions; **CHANGELOG** entry; README updated.
docs/design-ai-writing-suite-v1-2026-06-06.md:121:7. **Packaging: Claude + Codex** only in v1 (the two surfaces surahli can test now).
docs/design-ai-writing-suite-v1-2026-06-06.md:122:8. **Eval harness (D10)** — `evals/` with before/after fixtures across genres (tweet /
docs/design-ai-writing-suite-v1-2026-06-06.md:123:   LinkedIn / README / memo), expected score bands, LLM-judge rubric calibrated so the
docs/design-ai-writing-suite-v1-2026-06-06.md:124:   baseline fails 30-40%; + ported avoid-ai JS detector as a mechanical regression gate;
docs/design-ai-writing-suite-v1-2026-06-06.md:125:   + self-improvement loop wired to Autorefine-style error analysis + mutation, eval-gated
docs/design-ai-writing-suite-v1-2026-06-06.md:126:   before each human-approved rule append.
docs/design-ai-writing-suite-v1-2026-06-06.md:127:9. **KB ingestion+retrieval smoke path (D12)** — prove ONE end-to-end chain on the generic
docs/design-ai-writing-suite-v1-2026-06-06.md:128:   KB: a markdown/Confluence-style page → `_shared/knowledge/INDEX.md` → agent retrieves the
docs/design-ai-writing-suite-v1-2026-06-06.md:129:   correct passage for a query. NOT full `comms-qa` (that's v2); just enough to guarantee the
docs/design-ai-writing-suite-v1-2026-06-06.md:130:   company step is "drop in a Confluence page", not "build a retrieval engine".
docs/design-ai-writing-suite-v1-2026-06-06.md:131:
docs/design-ai-writing-suite-v1-2026-06-06.md:132:**Deferred to v2:** `comms-qa` full RAG, `comms-draft`, Confluence ingestion,
docs/design-ai-writing-suite-v1-2026-06-06.md:133:programmatic JS/Python detector, Cursor + RovoDev packaging, bilingual Chinese path,
docs/design-ai-writing-suite-v1-2026-06-06.md:134:optional embedding index.
docs/design-ai-writing-suite-v1-2026-06-06.md:135:
docs/design-ai-writing-suite-v1-2026-06-06.md:136:---
docs/design-ai-writing-suite-v1-2026-06-06.md:137:
docs/design-ai-writing-suite-v1-2026-06-06.md:138:## 6. Risks & flags
docs/design-ai-writing-suite-v1-2026-06-06.md:139:
docs/design-ai-writing-suite-v1-2026-06-06.md:140:- **R1 — Ghostwriting philosophy conflict.** surahli's writing-vault rule is "AI
docs/design-ai-writing-suite-v1-2026-06-06.md:141:  scaffolds, never ghostwrites." This suite *does* draft/rewrite. Resolution: this is a
docs/design-ai-writing-suite-v1-2026-06-06.md:142:  **separate, general/company tool**, not the personal writing-vault. Keep them distinct;
docs/design-ai-writing-suite-v1-2026-06-06.md:143:  do not let suite rewrite-mode bleed into `/distill`/`/voicecheck` behavior.
docs/design-ai-writing-suite-v1-2026-06-06.md:144:- **R2 — RovoDev constraints.** No skill auto-trigger, general-purpose subagents only,
docs/design-ai-writing-suite-v1-2026-06-06.md:145:  limited tools (`reference_inhouse_agent.md`). The human-gated self-improvement and
docs/design-ai-writing-suite-v1-2026-06-06.md:146:  file-read RAG must degrade gracefully there. Company version targets RovoDev explicitly.
docs/design-ai-writing-suite-v1-2026-06-06.md:147:- **R3 — Self-improvement drift.** Mitigated by D6 (human gate + append-only side files +
docs/design-ai-writing-suite-v1-2026-06-06.md:148:  periodic lint/dedup). Never auto-edit core logic.
docs/design-ai-writing-suite-v1-2026-06-06.md:149:- **R4 — 4-surface sync drift.** Single source of truth + `sync.sh` (avoid-ai pattern).
docs/design-ai-writing-suite-v1-2026-06-06.md:150:  Don't hand-edit generated packages.
docs/design-ai-writing-suite-v1-2026-06-06.md:151:- **R5 — Scope.** Full vision is large; v1 deliberately a vertical slice (D9).
docs/design-ai-writing-suite-v1-2026-06-06.md:152:- **R6 — Corrupted `blader-humanizer` reference.** Must be re-derived cleanly, not copied
docs/design-ai-writing-suite-v1-2026-06-06.md:153:  verbatim.
docs/design-ai-writing-suite-v1-2026-06-06.md:154:
docs/design-ai-writing-suite-v1-2026-06-06.md:155:---
docs/design-ai-writing-suite-v1-2026-06-06.md:156:
docs/design-ai-writing-suite-v1-2026-06-06.md:157:## 7. Pre-build checklist (before "go")
docs/design-ai-writing-suite-v1-2026-06-06.md:158:
docs/design-ai-writing-suite-v1-2026-06-06.md:159:1. `git checkout main && git pull` to sync local to `origin/main` (currently behind).
docs/design-ai-writing-suite-v1-2026-06-06.md:160:2. Cut fresh branch `feat/ai-writing-suite-v1` (do NOT build on stale `add-ai-writing-humanizer`).
docs/design-ai-writing-suite-v1-2026-06-06.md:161:3. Confirm repo rename decision: keep `ai-writing-humanizer` package name vs `ai-writing-suite`.
docs/design-ai-writing-suite-v1-2026-06-06.md:162:4. (Optional, recommended) one plan review pass: `/plan-eng-review`.
docs/design-ai-writing-suite-v1-2026-06-06.md:163:
docs/design-ai-writing-suite-v1-2026-06-06.md:164:## 8. Success criteria (what "done" looks like for v1)
docs/design-ai-writing-suite-v1-2026-06-06.md:165:
docs/design-ai-writing-suite-v1-2026-06-06.md:166:- `comms-polish` runs in Claude + Codex, consolidated catalog, scenario presets, voice
docs/design-ai-writing-suite-v1-2026-06-06.md:167:  matching when a profile exists, 0–100 score, no corrupted text.
docs/design-ai-writing-suite-v1-2026-06-06.md:168:- `voice-onboard` produces a usable `voice-profile.md` from pasted/local samples.
docs/design-ai-writing-suite-v1-2026-06-06.md:169:- Self-improvement proposes a rule, waits for approval, appends on yes.
docs/design-ai-writing-suite-v1-2026-06-06.md:170:- Generic KB slot present and documented as swappable for the company playbook.
docs/design-ai-writing-suite-v1-2026-06-06.md:171:- NOTICE.md credits all 4 repos; licenses preserved; CHANGELOG + README updated.
docs/design-ai-writing-suite-v1-2026-06-06.md:172:- Verification: skill loads without error in both targets; one end-to-end polish demo
docs/design-ai-writing-suite-v1-2026-06-06.md:173:  shown with before/after + score.
docs/design-ai-writing-suite-v1-2026-06-06.md:174:
docs/design-ai-writing-suite-v1-2026-06-06.md:175:## 9. v2 roadmap (not now)
docs/design-ai-writing-suite-v1-2026-06-06.md:176:
docs/design-ai-writing-suite-v1-2026-06-06.md:177:`comms-qa` full wiki-RAG → `comms-draft` → Confluence ingestion → programmatic detector
docs/design-ai-writing-suite-v1-2026-06-06.md:178:→ Cursor + RovoDev packaging → bilingual path → company fork with real playbook.
docs/design-ai-writing-suite-v1-2026-06-06.md:179:
docs/design-ai-writing-suite-v1-2026-06-06.md:180:---
docs/design-ai-writing-suite-v1-2026-06-06.md:181:
docs/design-ai-writing-suite-v1-2026-06-06.md:182:## What already exists (reuse, don't rebuild)
docs/design-ai-writing-suite-v1-2026-06-06.md:183:
docs/design-ai-writing-suite-v1-2026-06-06.md:184:- Installed `ai-writing-humanizer` + 3 refs (`stop-slop`, `blader`, `aboudjem`) → polish/detect base.
docs/design-ai-writing-suite-v1-2026-06-06.md:185:- 4 MIT repos → detectors, scenario presets, voice templates, packaging/sync scaffolds.
docs/design-ai-writing-suite-v1-2026-06-06.md:186:- User's own `/distill`, `/voicecheck`, `write` skills → personal voice/polish (keep separate, R1).
docs/design-ai-writing-suite-v1-2026-06-06.md:187:- avoid-ai JS detector + tests → port as regression gate (D10).
docs/design-ai-writing-suite-v1-2026-06-06.md:188:- Autorefine skill → borrow eval + mutation methodology (D10).
docs/design-ai-writing-suite-v1-2026-06-06.md:189:
docs/design-ai-writing-suite-v1-2026-06-06.md:190:## NOT in scope (v1)
docs/design-ai-writing-suite-v1-2026-06-06.md:191:
docs/design-ai-writing-suite-v1-2026-06-06.md:192:- `comms-qa` full retrieval, `comms-draft` — deferred (KB seed only in v1).
docs/design-ai-writing-suite-v1-2026-06-06.md:193:- Confluence ingestion — v2 (local files/paste only in v1).
docs/design-ai-writing-suite-v1-2026-06-06.md:194:- Cursor + RovoDev packaging — v2 (Claude + Codex only).
docs/design-ai-writing-suite-v1-2026-06-06.md:195:- Bilingual Chinese path — v2.
docs/design-ai-writing-suite-v1-2026-06-06.md:196:- Embedding/vector index — v2 (markdown+INDEX only).
docs/design-ai-writing-suite-v1-2026-06-06.md:197:
docs/design-ai-writing-suite-v1-2026-06-06.md:198:## GSTACK REVIEW REPORT
docs/design-ai-writing-suite-v1-2026-06-06.md:199:
docs/design-ai-writing-suite-v1-2026-06-06.md:200:| Review | Trigger | Why | Runs | Status | Findings |
docs/design-ai-writing-suite-v1-2026-06-06.md:201:|--------|---------|-----|------|--------|----------|
docs/design-ai-writing-suite-v1-2026-06-06.md:202:| CEO Review | `/plan-ceo-review` | Scope & strategy | 1 | HOLD_SCOPE, issues_resolved | sequencing confirmed (OSS-first via Confluence drop-in, D11); 1 coherence gap fixed (v1 smoke path, D12) |
docs/design-ai-writing-suite-v1-2026-06-06.md:203:| Eng Review | `/plan-eng-review` | Architecture & tests (required) | 1 | clean | 4 issues: scope(kept full per owner), D5 portability fix, thin router, eval harness added |
docs/design-ai-writing-suite-v1-2026-06-06.md:204:| Design Review | `/plan-design-review` | UI/UX gaps | 0 | n/a | prompt-only, no UI |
docs/design-ai-writing-suite-v1-2026-06-06.md:205:
docs/design-ai-writing-suite-v1-2026-06-06.md:206:- **CROSS-REVIEW:** eng (architecture) + ceo (strategy) agree the plan is sound after D5/D3b/D10/D11/D12; no tension.
docs/design-ai-writing-suite-v1-2026-06-06.md:207:- **UNRESOLVED:** 0. Scope kept full by owner; all findings resolved into D3b/D5/D10/D11/D12.
docs/design-ai-writing-suite-v1-2026-06-06.md:208:- **VERDICT:** CEO + ENG CLEARED — ready to implement. Pre-build checklist §7 still applies (sync main, cut `feat/ai-writing-suite-v1`).
docs/design-ai-writing-suite-v1-2026-06-06.md:209:
.gitignore:1:__pycache__/
.gitignore:2:*.py[cod]
.gitignore:3:
.gitignore:4:# OMC runtime state
.gitignore:5:.omc/
.claude-plugin/marketplace.json:1:{
.claude-plugin/marketplace.json:2:  "$schema": "https://json.schemastore.org/claude-code-marketplace.json",
.claude-plugin/marketplace.json:3:  "name": "ai-writing-suite",
.claude-plugin/marketplace.json:4:  "description": "Writing-assistant skill suite — polish/de-AI prose, learn an author's voice, and (v2) answer questions from a knowledge base and draft from it.",
.claude-plugin/marketplace.json:5:  "owner": {
.claude-plugin/marketplace.json:6:    "name": "surahli123"
.claude-plugin/marketplace.json:7:  },
.claude-plugin/marketplace.json:8:  "plugins": [
.claude-plugin/marketplace.json:9:    {
.claude-plugin/marketplace.json:10:      "name": "ai-writing-suite",
.claude-plugin/marketplace.json:11:      "source": "./skills/ai-writing-suite",
.claude-plugin/marketplace.json:12:      "description": "Suite of writing-assistant skills for professional and product communication. Polish and de-AI prose, learn an author's voice, and (v2) answer KB questions and draft from a knowledge base.",
.claude-plugin/marketplace.json:13:      "category": "productivity",
.claude-plugin/marketplace.json:14:      "keywords": ["writing", "editing", "humanize", "voice", "comms", "polish"]
.claude-plugin/marketplace.json:15:    }
.claude-plugin/marketplace.json:16:  ]
.claude-plugin/marketplace.json:17:}
skills/ai-writing-suite/.codex-plugin/plugin.json:1:{
skills/ai-writing-suite/.codex-plugin/plugin.json:2:  "name": "ai-writing-suite",
skills/ai-writing-suite/.codex-plugin/plugin.json:3:  "version": "1.0.0",
skills/ai-writing-suite/.codex-plugin/plugin.json:4:  "description": "Suite of writing-assistant skills for professional and product communication. Polish and de-AI prose, learn an author's voice, answer KB questions, and draft from a knowledge base.",
skills/ai-writing-suite/.codex-plugin/plugin.json:5:  "author": { "name": "surahli123" },
skills/ai-writing-suite/.codex-plugin/plugin.json:6:  "homepage": "https://github.com/surahli123/ai-writing-suite",
skills/ai-writing-suite/.codex-plugin/plugin.json:7:  "repository": "https://github.com/surahli123/ai-writing-suite",
skills/ai-writing-suite/.codex-plugin/plugin.json:8:  "license": "MIT",
skills/ai-writing-suite/.codex-plugin/plugin.json:9:  "keywords": ["writing", "editing", "humanize", "voice", "comms", "polish"],
skills/ai-writing-suite/.codex-plugin/plugin.json:10:  "skills": "./skills/",
skills/ai-writing-suite/.codex-plugin/plugin.json:11:  "interface": {
skills/ai-writing-suite/.codex-plugin/plugin.json:12:    "displayName": "AI Writing Suite",
skills/ai-writing-suite/.codex-plugin/plugin.json:13:    "shortDescription": "Polish/de-AI prose, learn an author's voice, KB-guided writing.",
skills/ai-writing-suite/.codex-plugin/plugin.json:14:    "longDescription": "A suite of writing-assistant skills: polish and de-AI prose while preserving meaning and voice, learn an author's historical voice into a reusable profile, and (in v2) answer questions from and draft against a pluggable knowledge base.",
skills/ai-writing-suite/.codex-plugin/plugin.json:15:    "developerName": "surahli123",
skills/ai-writing-suite/.codex-plugin/plugin.json:16:    "category": "Productivity",
skills/ai-writing-suite/.codex-plugin/plugin.json:17:    "capabilities": ["Read", "Write"]
skills/ai-writing-suite/.codex-plugin/plugin.json:18:  }
skills/ai-writing-suite/.codex-plugin/plugin.json:19:}
.agents/plugins/marketplace.json:1:{
.agents/plugins/marketplace.json:2:  "name": "ai-writing-suite",
.agents/plugins/marketplace.json:3:  "interface": {
.agents/plugins/marketplace.json:4:    "displayName": "AI Writing Suite"
.agents/plugins/marketplace.json:5:  },
.agents/plugins/marketplace.json:6:  "plugins": [
.agents/plugins/marketplace.json:7:    {
.agents/plugins/marketplace.json:8:      "name": "ai-writing-suite",
.agents/plugins/marketplace.json:9:      "source": {
.agents/plugins/marketplace.json:10:        "source": "local",
.agents/plugins/marketplace.json:11:        "path": "./skills/ai-writing-suite"
.agents/plugins/marketplace.json:12:      },
.agents/plugins/marketplace.json:13:      "policy": {
.agents/plugins/marketplace.json:14:        "installation": "AVAILABLE",
.agents/plugins/marketplace.json:15:        "authentication": "ON_INSTALL"
.agents/plugins/marketplace.json:16:      },
.agents/plugins/marketplace.json:17:      "category": "Productivity"
.agents/plugins/marketplace.json:18:    }
.agents/plugins/marketplace.json:19:  ]
.agents/plugins/marketplace.json:20:}
README.md:1:# AI Writing Suite
README.md:2:
README.md:3:An open-source, MIT-licensed agent skill suite for **writing assistance** — the public
README.md:4:version of a writing-assistant skillset for a company Data Science team. It polishes,
README.md:5:drafts, and reviews prose against a **pluggable knowledge base** (a "DS Comms Playbook"
README.md:6:in the company fork; a generic best-practices KB in this OSS build).
README.md:7:
README.md:8:> **Engine vs fuel:** this repo is the *engine*. The knowledge base is *fuel* — swappable.
README.md:9:> The OSS build ships a generic KB; a company fork drops its real playbook into the same
README.md:10:> slot. The proprietary playbook never enters this public repo.
README.md:11:
README.md:12:## What it does (target)
README.md:13:
README.md:14:1. **Polish / review** — de-AI and tighten prose while preserving meaning and author voice.
README.md:15:2. **Voice learning** — interview + distill a writer's historical style into a reusable profile.
README.md:16:3. **Knowledge QA (mini-RAG)** — answer questions over the playbook + best practices *(v2)*.
README.md:17:4. **Guided drafting** — draft a page using the playbook *(v2)*.
README.md:18:
README.md:19:Plus a **human-gated self-improvement** loop: each session can *propose* new rules; you
README.md:20:approve before anything is written. Core skill logic is never auto-edited.
README.md:21:
README.md:22:## Status
README.md:23:
README.md:24:**v1 — built, verified, and installable on Claude, Codex, and Cursor.** Ships the polish/de-AI
README.md:25:capability (`comms-polish`), voice learning (`voice-onboard`), a generic pluggable KB seed with an
README.md:26:end-to-end retrieval smoke path, an eval harness (Python AI-tell detector + fixtures), and a
README.md:27:human-gated self-improvement hook. `comms-qa` (KB Q&A) and `comms-draft` are v2 stubs.
README.md:28:
README.md:29:- **Plan (read first):** [`docs/design-ai-writing-suite-v1-2026-06-06.md`](docs/design-ai-writing-suite-v1-2026-06-06.md)
README.md:30:  — decision log D1–D12, v1 scope, risks, eng+ceo review report.
README.md:31:
README.md:32:## Install
README.md:33:
README.md:34:One source of truth (`skills/ai-writing-suite/`) published to three hosts.
README.md:35:
README.md:36:### Claude Code
README.md:37:
README.md:38:```bash
README.md:39:claude plugin marketplace add surahli123/ai-writing-suite
README.md:40:claude plugin install ai-writing-suite@ai-writing-suite
README.md:41:```
README.md:42:
README.md:43:Claude auto-discovers the sub-skills (`comms-polish`, `voice-onboard`, …); invoke by asking it to
README.md:44:polish/review prose, or call a skill by name.
README.md:45:
README.md:46:### Codex
README.md:47:
README.md:48:```bash
README.md:49:codex plugin marketplace add surahli123/ai-writing-suite
README.md:50:codex plugin add ai-writing-suite@ai-writing-suite
README.md:51:```
README.md:52:
README.md:53:Codex resolves the plugin from the same source tree — no `--sparse` needed; the Codex
README.md:54:marketplace manifest sits at the repo root (`.agents/plugins/marketplace.json`).
README.md:55:
README.md:56:### Cursor
README.md:57:
README.md:58:Cursor reads Anthropic-format **Agent Skills** from `.cursor/skills/` — there is no marketplace, so
README.md:59:copy the skill tree into a discovery location:
README.md:60:
README.md:61:```bash
README.md:62:git clone https://github.com/surahli123/ai-writing-suite
README.md:63:cp -R ai-writing-suite/skills/ai-writing-suite ~/.cursor/skills/ai-writing-suite
README.md:64:```
README.md:65:
README.md:66:(Or copy into your project's `.cursor/skills/` for project-scoped use.) Cursor discovers the skills
README.md:67:on the next session; invoke with `/comms-polish`, `/voice-onboard`, … or by intent.
README.md:68:
README.md:69:## Repo Layout
README.md:70:
README.md:71:```text
README.md:72:.claude-plugin/marketplace.json    # Claude marketplace  → points at the source tree
README.md:73:.agents/plugins/marketplace.json   # Codex marketplace   → points at the source tree
README.md:74:skills/
README.md:75:  ai-writing-suite/                # THE SUITE — single source of truth
README.md:76:                                   #   (Claude + Codex install this; Cursor copies it)
README.md:77:    SKILL.md                       # thin router
README.md:78:    .claude-plugin/plugin.json     # Claude plugin manifest
README.md:79:    .codex-plugin/plugin.json      # Codex plugin manifest
README.md:80:    skills/                        # sub-skills: comms-polish, voice-onboard, comms-qa*, comms-draft*
README.md:81:    _shared/                       # patterns (engine) + knowledge (swappable KB) + voice profile
README.md:82:    evals/                         # AI-tell detector + fixtures + smoke tests
README.md:83:    NOTICE.md  LICENSE  README.md  CHANGELOG.md
README.md:84:docs/                              # design docs, handovers, plans, packaging  (* = v2 stub)
README.md:85:```
README.md:86:
README.md:87:## Attribution
README.md:88:
README.md:89:Absorbed material from other repos is MIT-licensed; each source's copyright + license is
README.md:90:preserved and credited in [`skills/ai-writing-suite/NOTICE.md`](skills/ai-writing-suite/NOTICE.md).
docs/code-review-v1-2026-06-06.md:1:# Code Review — AI Writing Suite v1 (Opus, independent worktree pass)
docs/code-review-v1-2026-06-06.md:2:
docs/code-review-v1-2026-06-06.md:3:Date: 2026-06-06
docs/code-review-v1-2026-06-06.md:4:Reviewer: oh-my-claudecode:code-reviewer (Opus), isolated git worktree
docs/code-review-v1-2026-06-06.md:5:Scope: `feat/ai-writing-suite-v1`, commits `d4ed904..d6616a4` (Layers 0-3)
docs/code-review-v1-2026-06-06.md:6:
docs/code-review-v1-2026-06-06.md:7:## Verdict
docs/code-review-v1-2026-06-06.md:8:
docs/code-review-v1-2026-06-06.md:9:**v1 is sound and ship-able. No BLOCKERs.** Must-fix before OSS release = two stale-doc
docs/code-review-v1-2026-06-06.md:10:contradictions (M1, M2). Detector is logically correct + crash-proof on every adversarial
docs/code-review-v1-2026-06-06.md:11:input. Eval calibration genuinely enforces the 30-40% band (real 38%; cannot pass vacuously).
docs/code-review-v1-2026-06-06.md:12:Voice-profile contract aligns field-for-field. D5 (zero-dep), D6 (human-gated), D12 (real
docs/code-review-v1-2026-06-06.md:13:smoke chain) all honored.
docs/code-review-v1-2026-06-06.md:14:
docs/code-review-v1-2026-06-06.md:15:## Tests (run by reviewer)
docs/code-review-v1-2026-06-06.md:16:
docs/code-review-v1-2026-06-06.md:17:| Command | Result | Exit |
docs/code-review-v1-2026-06-06.md:18:|---|---|---|
docs/code-review-v1-2026-06-06.md:19:| `python3 -m unittest discover -p 'test_*.py'` | 23 tests OK | 0 |
docs/code-review-v1-2026-06-06.md:20:| `python3 smoke_test.py` | 2/2 PASS | 0 |
docs/code-review-v1-2026-06-06.md:21:| `python3 -m fixtures.run_fixtures` | 8/8, miss 38%, "in target band: YES" | 0 |
docs/code-review-v1-2026-06-06.md:22:
docs/code-review-v1-2026-06-06.md:23:stdlib-only confirmed (no package.json/requirements/pyproject) → D5 holds. `sync.sh` idempotent;
docs/code-review-v1-2026-06-06.md:24:packaged SKILLs byte-identical to source → no drift.
docs/code-review-v1-2026-06-06.md:25:
docs/code-review-v1-2026-06-06.md:26:## Adversarial detector inputs → all crash-proof, no nonsense scores
docs/code-review-v1-2026-06-06.md:27:
docs/code-review-v1-2026-06-06.md:28:empty / whitespace / 1-word / emoji-only / fenced code / CJK / unicode-mix → UNSCORED (length
docs/code-review-v1-2026-06-06.md:29:gate). huge 35k words → "Text too long" (MAX_WORDS=10000). AI control → 82 AI_ONLY. human
docs/code-review-v1-2026-06-06.md:30:control → 0 HUMAN_ONLY. Zero crashes.
docs/code-review-v1-2026-06-06.md:31:
docs/code-review-v1-2026-06-06.md:32:---
docs/code-review-v1-2026-06-06.md:33:
docs/code-review-v1-2026-06-06.md:34:## MAJOR
docs/code-review-v1-2026-06-06.md:35:
docs/code-review-v1-2026-06-06.md:36:**M1 — Stale "empty KB slot" claims contradict the seeded KB.**
docs/code-review-v1-2026-06-06.md:37:`SKILL.md:62` ("the slot is present but empty in this build") + `skills/comms-qa/SKILL.md:11-13`
docs/code-review-v1-2026-06-06.md:38:("KB slot exists but is empty"). Layer 2 actually seeded 5 entries + INDEX + SMOKE-TEST. Readers
docs/code-review-v1-2026-06-06.md:39:conclude the KB doesn't work → undermines the D11/D12 product claim. Fix: update both to "ships a
docs/code-review-v1-2026-06-06.md:40:generic 5-entry KB; full comms-qa retrieval is v2." Re-run `sync.sh`.
docs/code-review-v1-2026-06-06.md:41:
docs/code-review-v1-2026-06-06.md:42:**M2 — NOTICE marks the detector "(v2)" but it ships in v1.**
docs/code-review-v1-2026-06-06.md:43:`NOTICE.md:29` "detector foundation (v2)". The Python port (`evals/detector/`) is a v1
docs/code-review-v1-2026-06-06.md:44:deliverable. Wrong scope tag on the one piece of executable ported logic = worst place to be
docs/code-review-v1-2026-06-06.md:45:sloppy on attribution. Fix: drop "(v2)".
docs/code-review-v1-2026-06-06.md:46:
docs/code-review-v1-2026-06-06.md:47:## MINOR
docs/code-review-v1-2026-06-06.md:48:
docs/code-review-v1-2026-06-06.md:49:**m1 — Smoke Case 2 discriminates on a SINGLE token → near-vacuous.**
docs/code-review-v1-2026-06-06.md:50:`smoke_test.py` + `SMOKE-TEST.md:84-96`. Query retrieves `audience.md` overlap (1,0) — only
docs/code-review-v1-2026-06-06.md:51:"who" matches; lure words hit zero entries, `tone.md` scores 0. No competing signal → proves
docs/code-review-v1-2026-06-06.md:52:little. Fix: add a query where both `tone.md` and `audience.md` score >0 so the tie-break is real.
docs/code-review-v1-2026-06-06.md:53:
docs/code-review-v1-2026-06-06.md:54:**m2 — Empty/garbage query passes Case 1 by stable-order fallback (no overlap guard).**
docs/code-review-v1-2026-06-06.md:55:`smoke_test.py retrieve()`. `""` returns `clarity.md` (overlap (0,0), first-table default) →
docs/code-review-v1-2026-06-06.md:56:would vacuously satisfy Case 1. Fix: assert `best_score > 0`; treat zero-overlap as no match.
docs/code-review-v1-2026-06-06.md:57:
docs/code-review-v1-2026-06-06.md:58:**m3 — Dead branch in `_classify`.** `detector.py:342` `elif score >= 40 and strong >= 1:` is
docs/code-review-v1-2026-06-06.md:59:unreachable (line 340 already catches every `strong>=1`). Delete lines 342-343.
docs/code-review-v1-2026-06-06.md:60:
docs/code-review-v1-2026-06-06.md:61:**m4 — Detector blind to CJK / non-space scripts.** `_count_words` (`\S+`) collapses Japanese/
docs/code-review-v1-2026-06-06.md:62:Chinese to wordCount=1 → always "Too short", silently UNSCORED (reads as "clean"). Acceptable for
docs/code-review-v1-2026-06-06.md:63:v1 (bilingual = v2) but fix: note the limitation in the docstring so UNSCORED isn't misread.
docs/code-review-v1-2026-06-06.md:64:
docs/code-review-v1-2026-06-06.md:65:## NIT
docs/code-review-v1-2026-06-06.md:66:
docs/code-review-v1-2026-06-06.md:67:- **n1** `evals/` excluded from packaged targets (CI-only) — document why in `packaging/README.md`.
docs/code-review-v1-2026-06-06.md:68:- **n2** `_sentences` splits on `[.!?]+` → abbreviations over-split, mild burstiness skew. Low impact.
docs/code-review-v1-2026-06-06.md:69:- **n3** `run_fixtures` reads `before_band_min/max` but `test_fixtures REQUIRED` omits them; a
docs/code-review-v1-2026-06-06.md:70:  typo'd key would silently skip the assert. Consider asserting band presence per difficulty.
docs/code-review-v1-2026-06-06.md:71:
docs/code-review-v1-2026-06-06.md:72:## Positive observations
docs/code-review-v1-2026-06-06.md:73:
docs/code-review-v1-2026-06-06.md:74:- Calibration is real, not theater (3/8 subtle fixtures score literally 0; flip one → band breaks).
docs/code-review-v1-2026-06-06.md:75:- Detector port faithful + defensively correct (dedup, log2 normalization, tiered thresholds,
docs/code-review-v1-2026-06-06.md:76:  FN-biased classifier, length gates).
docs/code-review-v1-2026-06-06.md:77:- Voice contract aligns field-for-field (identical 10 H2 names writer↔reader); degradation real.
docs/code-review-v1-2026-06-06.md:78:- D6 self-improvement genuinely human-gated (read+propose autonomously; append needs approval;
docs/code-review-v1-2026-06-06.md:79:  core never auto-edited). Router stays thin.
docs/code-review-v1-2026-06-06.md:80:- Honest scaffolding (v2 stubs labeled; P31-P43 corruption disclosed; sync.sh single-source rule).
skills/ai-writing-suite/_shared/knowledge/README.md:1:# Knowledge base (pluggable slot)
skills/ai-writing-suite/_shared/knowledge/README.md:2:
skills/ai-writing-suite/_shared/knowledge/README.md:3:This directory is the **fuel** slot. The suite is the engine; the knowledge base
skills/ai-writing-suite/_shared/knowledge/README.md:4:is the fuel.
skills/ai-writing-suite/_shared/knowledge/README.md:5:
skills/ai-writing-suite/_shared/knowledge/README.md:6:This OSS build ships a **generic best-practices KB** (markdown topic entries +
skills/ai-writing-suite/_shared/knowledge/README.md:7:`INDEX.md` navigation, distilled from four MIT reference repos). A company fork
skills/ai-writing-suite/_shared/knowledge/README.md:8:drops its own writing playbook into this *same slot* via a Confluence page or
skills/ai-writing-suite/_shared/knowledge/README.md:9:markdown files. The playbook never enters the public repo.
skills/ai-writing-suite/_shared/knowledge/README.md:10:
skills/ai-writing-suite/_shared/knowledge/README.md:11:## What's in this slot
skills/ai-writing-suite/_shared/knowledge/README.md:12:
skills/ai-writing-suite/_shared/knowledge/README.md:13:| File | Role |
skills/ai-writing-suite/_shared/knowledge/README.md:14:| --- | --- |
skills/ai-writing-suite/_shared/knowledge/README.md:15:| `INDEX.md` | **Retrieval backbone.** Lists every entry with a one-line summary + keywords/aliases so an agent can resolve a natural-language query to the right entry. Pure markdown, zero deps (design decision **D5**). |
skills/ai-writing-suite/_shared/knowledge/README.md:16:| `clarity.md`, `structure.md`, `audience.md`, `tone.md`, `revision.md` | Generic professional-writing best-practice entries. Each is attributed (`Sources` section) and small. |
skills/ai-writing-suite/_shared/knowledge/README.md:17:| `SMOKE-TEST.md` | **Proof the chain works (D12).** One end-to-end ingestion + retrieval test: sample page → INDEX row → query → expected entry + passage. Layer 3 eval automates it. |
skills/ai-writing-suite/_shared/knowledge/README.md:18:| `README.md` | This file. |
skills/ai-writing-suite/_shared/knowledge/README.md:19:
skills/ai-writing-suite/_shared/knowledge/README.md:20:## How retrieval works (no engine to build)
skills/ai-writing-suite/_shared/knowledge/README.md:21:
skills/ai-writing-suite/_shared/knowledge/README.md:22:Retrieval is an agent reading `INDEX.md`, matching the question against the
skills/ai-writing-suite/_shared/knowledge/README.md:23:keywords/summary, opening the one matching entry, and quoting the passage. There
skills/ai-writing-suite/_shared/knowledge/README.md:24:are **no embeddings, no vector DB, and no host-specific MCP tools** in the core
skills/ai-writing-suite/_shared/knowledge/README.md:25:path — so it runs identically on Claude, Codex, Cursor, and RovoDev (D5). The
skills/ai-writing-suite/_shared/knowledge/README.md:26:OMC `wiki_*` tools are an optional Claude-side accelerator only; they are never
skills/ai-writing-suite/_shared/knowledge/README.md:27:required.
skills/ai-writing-suite/_shared/knowledge/README.md:28:
skills/ai-writing-suite/_shared/knowledge/README.md:29:Full `comms-qa` retrieval logic (multi-passage, ranking, citations) is **v2**.
skills/ai-writing-suite/_shared/knowledge/README.md:30:v1 ships the seed + the proven smoke path, nothing heavier.
skills/ai-writing-suite/_shared/knowledge/README.md:31:
skills/ai-writing-suite/_shared/knowledge/README.md:32:## Swapping in a company playbook (the company step)
skills/ai-writing-suite/_shared/knowledge/README.md:33:
skills/ai-writing-suite/_shared/knowledge/README.md:34:A company fork turns "generic KB" into "DS Comms Playbook" by **adding data, not
skills/ai-writing-suite/_shared/knowledge/README.md:35:building an engine** (decisions D11 + D12). The steps:
skills/ai-writing-suite/_shared/knowledge/README.md:36:
skills/ai-writing-suite/_shared/knowledge/README.md:37:1. **Export each Confluence page / playbook section to markdown** and drop the
skills/ai-writing-suite/_shared/knowledge/README.md:38:   file(s) into this directory (replace the generic entries, or add alongside
skills/ai-writing-suite/_shared/knowledge/README.md:39:   them). One page = one `*.md` entry. Keep entries small and topic-scoped.
skills/ai-writing-suite/_shared/knowledge/README.md:40:2. **Add one row per entry to `INDEX.md`** — `entry file | one-line summary |
skills/ai-writing-suite/_shared/knowledge/README.md:41:   keywords/aliases`. That single row IS the ingestion step (see `SMOKE-TEST.md`
skills/ai-writing-suite/_shared/knowledge/README.md:42:   Step 2). No build, no re-index job.
skills/ai-writing-suite/_shared/knowledge/README.md:43:3. **Add company test cases to `SMOKE-TEST.md`** (query → expected entry →
skills/ai-writing-suite/_shared/knowledge/README.md:44:   expected passage) so the eval can verify the company KB resolves correctly.
skills/ai-writing-suite/_shared/knowledge/README.md:45:4. **Do not push the company KB to the public repo.** The playbook is private; it
skills/ai-writing-suite/_shared/knowledge/README.md:46:   lives only in the fork. The engine (everything outside this slot) stays shared.
skills/ai-writing-suite/_shared/knowledge/README.md:47:
skills/ai-writing-suite/_shared/knowledge/README.md:48:That's the whole integration. Because the index and entries are plain markdown,
skills/ai-writing-suite/_shared/knowledge/README.md:49:the company never touches retrieval code — they edit a table and drop in pages.
docs/packaging.md:1:# Packaging & Publishing (maintainer note)
docs/packaging.md:2:
docs/packaging.md:3:**Model: one source tree, read directly by every host.** There is no build/generate step.
docs/packaging.md:4:The single source of truth is `skills/ai-writing-suite/`. Each host gets a tiny manifest that
docs/packaging.md:5:*points at* that tree (or, for Cursor, copies it). Nothing is duplicated or generated, so there
docs/packaging.md:6:is no sync-drift surface.
docs/packaging.md:7:
docs/packaging.md:8:> This replaces the earlier generate-and-sync approach (`packaging/` + `sync.sh`), which was
docs/packaging.md:9:> removed: its generated bodies were gitignored, which is what made v1 uninstallable.
docs/packaging.md:10:
docs/packaging.md:11:## The four manifests
docs/packaging.md:12:
docs/packaging.md:13:| File | Host | Role |
docs/packaging.md:14:|---|---|---|
docs/packaging.md:15:| `/.claude-plugin/marketplace.json` | Claude | Marketplace catalog; `plugins[].source = "./skills/ai-writing-suite"` |
docs/packaging.md:16:| `/skills/ai-writing-suite/.claude-plugin/plugin.json` | Claude | Plugin identity (name, version, metadata) |
docs/packaging.md:17:| `/.agents/plugins/marketplace.json` | Codex | Marketplace catalog; `plugins[].source = {source:"local", path:"./skills/ai-writing-suite"}` |
docs/packaging.md:18:| `/skills/ai-writing-suite/.codex-plugin/plugin.json` | Codex | Plugin identity (+ `"skills": "./skills/"`, `interface{}`) |
docs/packaging.md:19:
docs/packaging.md:20:Both root marketplaces point at the **same** source tree. Claude auto-discovers the sub-skills
docs/packaging.md:21:under `skills/ai-writing-suite/skills/`; the root `SKILL.md` is a documentation router.
docs/packaging.md:22:
docs/packaging.md:23:## Install (end users)
docs/packaging.md:24:
docs/packaging.md:25:- **Claude:** `claude plugin marketplace add surahli123/ai-writing-suite` → `claude plugin install ai-writing-suite@ai-writing-suite`
docs/packaging.md:26:- **Codex:** `codex plugin marketplace add surahli123/ai-writing-suite` → `codex plugin add ai-writing-suite@ai-writing-suite`
docs/packaging.md:27:- **Cursor:** copy `skills/ai-writing-suite/` into `~/.cursor/skills/ai-writing-suite/` (or a project's `.cursor/skills/`). Cursor reads Anthropic-format `SKILL.md` Agent Skills natively; no manifest needed. (Not `.cursor/rules/*.mdc` — that is passive context injection, the wrong primitive for callable skills.)
docs/packaging.md:28:
docs/packaging.md:29:## Versioning / updates
docs/packaging.md:30:
docs/packaging.md:31:1. Bump `version:` in the source `SKILL.md` frontmatter (if present) and in the two `plugin.json`
docs/packaging.md:32:   files (`.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`).
docs/packaging.md:33:2. Commit + push. Consumers refresh via `claude plugin update` / `codex plugin marketplace upgrade`.
docs/packaging.md:34:3. (Optional) cut a git tag (`claude plugin tag` for Claude; a git tag for Codex `--ref` pinning)
docs/packaging.md:35:   **after** verifying a real-remote install.
docs/packaging.md:36:
docs/packaging.md:37:## Verify before publishing
docs/packaging.md:38:
docs/packaging.md:39:- `claude plugin validate .` and `claude plugin validate skills/ai-writing-suite` (both must pass).
docs/packaging.md:40:- Local install smoke per host (add the local path as a marketplace, install, confirm the skill
docs/packaging.md:41:  loads, then remove — restore your config). For Cursor, validate the `SKILL.md` frontmatter `name:`
docs/packaging.md:42:  matches each folder.
docs/packaging.md:43:- **Local green ≠ remote-installable.** After pushing, run a real-remote smoke
docs/packaging.md:44:  (`marketplace add surahli123/ai-writing-suite`) before tagging a release.
docs/packaging.md:45:
docs/packaging.md:46:## Engine vs fuel
docs/packaging.md:47:
docs/packaging.md:48:`_shared/patterns/` is the *engine* (de-AI rules) and must survive a KB swap. `_shared/knowledge/`
docs/packaging.md:49:is the *fuel* — the generic OSS KB; a company fork drops its real playbook into the same slot
docs/packaging.md:50:(never committed to this public repo).
docs/packaging.md:51:
docs/packaging.md:52:## Deferred (v2)
docs/packaging.md:53:
docs/packaging.md:54:RovoDev packaging. It will follow the same source-pointing model (explicit intent routing via the
docs/packaging.md:55:suite router, since RovoDev does not auto-trigger skills).
skills/ai-writing-suite/NOTICE.md:1:# Attribution & Licenses
skills/ai-writing-suite/NOTICE.md:2:
skills/ai-writing-suite/NOTICE.md:3:AI Writing Suite is a consolidated writing-assistant skill that absorbs and extends patterns, templates, and methodologies from seven open-source projects, all MIT-licensed. This document preserves the copyright and license notice for each source.
skills/ai-writing-suite/NOTICE.md:4:
skills/ai-writing-suite/NOTICE.md:5:## Source Projects
skills/ai-writing-suite/NOTICE.md:6:
skills/ai-writing-suite/NOTICE.md:7:### 1. anti-vibe-writing
skills/ai-writing-suite/NOTICE.md:8:
skills/ai-writing-suite/NOTICE.md:9:**Author:** weijt606  
skills/ai-writing-suite/NOTICE.md:10:**Repository:** [weijt606/anti-vibe-writing](https://github.com/weijt606/anti-vibe-writing)  
skills/ai-writing-suite/NOTICE.md:11:**License:** MIT  
skills/ai-writing-suite/NOTICE.md:12:**Copyright:** Copyright (c) 2026 weijt606
skills/ai-writing-suite/NOTICE.md:13:
skills/ai-writing-suite/NOTICE.md:14:**Contribution:** Bilingual (Chinese/English) pattern sets, scenario presets (tweet, LinkedIn, README, memo templates), learning-mode framework, host-profile voice template structure, and final-pass checklist.
skills/ai-writing-suite/NOTICE.md:15:
skills/ai-writing-suite/NOTICE.md:16:**Used in:** `comms-polish` scenario presets, `voice-onboard` host-profile template.
skills/ai-writing-suite/NOTICE.md:17:
skills/ai-writing-suite/NOTICE.md:18:---
skills/ai-writing-suite/NOTICE.md:19:
skills/ai-writing-suite/NOTICE.md:20:### 2. avoid-ai-writing
skills/ai-writing-suite/NOTICE.md:21:
skills/ai-writing-suite/NOTICE.md:22:**Author:** Conor Bronsdon  
skills/ai-writing-suite/NOTICE.md:23:**Repository:** [conorbronsdon/avoid-ai-writing](https://github.com/conorbronsdon/avoid-ai-writing)  
skills/ai-writing-suite/NOTICE.md:24:**License:** MIT  
skills/ai-writing-suite/NOTICE.md:25:**Copyright:** Copyright (c) 2026 Conor Bronsdon
skills/ai-writing-suite/NOTICE.md:26:
skills/ai-writing-suite/NOTICE.md:27:**Contribution:** Programmatic JavaScript detector with test suite, tiered AI-vocabulary taxonomy (Tier 1/2/3 classification), CATEGORIES taxonomy for AI-writing patterns, multi-surface packaging patterns (Claude plugin, Cursor `.mdc` format), and sync tooling scaffold.
skills/ai-writing-suite/NOTICE.md:28:
skills/ai-writing-suite/NOTICE.md:29:**Used in:** AI-tell pattern catalog (lexical tells, significance attribution, structural patterns), the Python detector port shipped in v1 (`evals/detector/`), packaging and sync conventions.
skills/ai-writing-suite/NOTICE.md:30:
skills/ai-writing-suite/NOTICE.md:31:---
skills/ai-writing-suite/NOTICE.md:32:
skills/ai-writing-suite/NOTICE.md:33:### 3. AI-Vibe-Writing-Skills
skills/ai-writing-suite/NOTICE.md:34:
skills/ai-writing-suite/NOTICE.md:35:**Author:** AI Vibe Writing Skill Contributors  
skills/ai-writing-suite/NOTICE.md:36:**Repository:** [donghuixin/AI-Vibe-Writing-Skills](https://github.com/donghuixin/AI-Vibe-Writing-Skills)  
skills/ai-writing-suite/NOTICE.md:37:**License:** MIT  
skills/ai-writing-suite/NOTICE.md:38:**Copyright:** Copyright (c) 2024 AI Vibe Writing Skill Contributors
skills/ai-writing-suite/NOTICE.md:39:
skills/ai-writing-suite/NOTICE.md:40:**Contribution:** Local AI-detector methodology, style-extractor and reviewer agent prompts, soft/hard memory patterns for voice learning, and self-improvement loop structure.
skills/ai-writing-suite/NOTICE.md:41:
skills/ai-writing-suite/NOTICE.md:42:**Used in:** `voice-onboard` distillation prompts, `comms-polish` voice-matching review, self-improvement memory patterns.
skills/ai-writing-suite/NOTICE.md:43:
skills/ai-writing-suite/NOTICE.md:44:---
skills/ai-writing-suite/NOTICE.md:45:
skills/ai-writing-suite/NOTICE.md:46:### 4. nature-skills
skills/ai-writing-suite/NOTICE.md:47:
skills/ai-writing-suite/NOTICE.md:48:**Author:** Yuan Yizhe  
skills/ai-writing-suite/NOTICE.md:49:**Repository:** [Yuan1z0825/nature-skills](https://github.com/Yuan1z0825/nature-skills)  
skills/ai-writing-suite/NOTICE.md:50:**License:** MIT  
skills/ai-writing-suite/NOTICE.md:51:**Copyright:** Copyright (c) 2026 Yuan Yizhe
skills/ai-writing-suite/NOTICE.md:52:
skills/ai-writing-suite/NOTICE.md:53:**Contribution:** Academic and technical writing polish rubric, structural editing patterns (from `nature-writing` and `nature-polishing` subskills), Codex plugin manifest conventions.
skills/ai-writing-suite/NOTICE.md:54:
skills/ai-writing-suite/NOTICE.md:55:**Used in:** AI-tell pattern catalog (rhythm, stylometry, structural tells), `comms-polish` scoring and review rubric, Codex packaging conventions.
skills/ai-writing-suite/NOTICE.md:56:
skills/ai-writing-suite/NOTICE.md:57:---
skills/ai-writing-suite/NOTICE.md:58:
skills/ai-writing-suite/NOTICE.md:59:### 5. stop-slop
skills/ai-writing-suite/NOTICE.md:60:
skills/ai-writing-suite/NOTICE.md:61:**Author:** Hardik Pandya  
skills/ai-writing-suite/NOTICE.md:62:**Repository:** [stop-slop](https://github.com/stop-slop)  
skills/ai-writing-suite/NOTICE.md:63:**License:** MIT  
skills/ai-writing-suite/NOTICE.md:64:**Copyright:** Copyright (c) Hardik Pandya
skills/ai-writing-suite/NOTICE.md:65:
skills/ai-writing-suite/NOTICE.md:66:**Contribution:** Eight core directness rules, scoring rubric, and baseline calibration methodology.
skills/ai-writing-suite/NOTICE.md:67:
skills/ai-writing-suite/NOTICE.md:68:**Used in:** Consolidated pattern catalog, eval baseline calibration, detection scoring.
skills/ai-writing-suite/NOTICE.md:69:
skills/ai-writing-suite/NOTICE.md:70:---
skills/ai-writing-suite/NOTICE.md:71:
skills/ai-writing-suite/NOTICE.md:72:### 6. blader/humanizer
skills/ai-writing-suite/NOTICE.md:73:
skills/ai-writing-suite/NOTICE.md:74:**Author:** Brandon Wise  
skills/ai-writing-suite/NOTICE.md:75:**Repository:** [blader/humanizer](https://github.com/blader/humanizer)  
skills/ai-writing-suite/NOTICE.md:76:**License:** MIT  
skills/ai-writing-suite/NOTICE.md:77:**Copyright:** Copyright (c) Brandon Wise
skills/ai-writing-suite/NOTICE.md:78:
skills/ai-writing-suite/NOTICE.md:79:**Contribution:** 43-pattern humanizer catalog with Tell / Fix / example structure and voice calibration framework.
skills/ai-writing-suite/NOTICE.md:80:
skills/ai-writing-suite/NOTICE.md:81:**Used in:** Consolidated pattern catalog (`_shared/patterns/`), core detection baseline. *Note: Patterns P31-P43 were re-derived cleanly from intent due to formatting corruption in the original source; lineage and attribution preserved.*
skills/ai-writing-suite/NOTICE.md:82:
skills/ai-writing-suite/NOTICE.md:83:---
skills/ai-writing-suite/NOTICE.md:84:
skills/ai-writing-suite/NOTICE.md:85:### 7. aboudjem/humanizer-skill
skills/ai-writing-suite/NOTICE.md:86:
skills/ai-writing-suite/NOTICE.md:87:**Author:** Aboudjem  
skills/ai-writing-suite/NOTICE.md:88:**Repository:** [Aboudjem/humanizer-skill](https://github.com/Aboudjem/humanizer-skill)  
skills/ai-writing-suite/NOTICE.md:89:**License:** MIT  
skills/ai-writing-suite/NOTICE.md:90:**Copyright:** Copyright (c) Aboudjem
skills/ai-writing-suite/NOTICE.md:91:
skills/ai-writing-suite/NOTICE.md:92:**Contribution:** 30-pattern catalog derived from Wikipedia's "Signs of AI writing," with structured Tell / Fix / example format.
skills/ai-writing-suite/NOTICE.md:93:
skills/ai-writing-suite/NOTICE.md:94:**Used in:** Consolidated pattern catalog (`_shared/patterns/`), detection baseline, pattern structure conventions.
skills/ai-writing-suite/NOTICE.md:95:
skills/ai-writing-suite/NOTICE.md:96:---
skills/ai-writing-suite/NOTICE.md:97:
skills/ai-writing-suite/NOTICE.md:98:## Consolidated Pattern Catalog
skills/ai-writing-suite/NOTICE.md:99:
skills/ai-writing-suite/NOTICE.md:100:The file `_shared/patterns/00-index.md` serves as the single source of truth for all AI-writing patterns used by `comms-polish`. It deduplicates and cross-references patterns from all seven sources above, with each pattern tagged by its source origin (via `Sources` field) so lineage is traceable.
skills/ai-writing-suite/NOTICE.md:101:
skills/ai-writing-suite/NOTICE.md:102:See `_shared/patterns/00-index.md` for:
skills/ai-writing-suite/NOTICE.md:103:- **Source legend:** mapping of source tags (e.g., `blader`, `aboudjem`, `stop-slop`, `avoid-ai`, `anti-vibe`, `ai-vibe`, `nature`) to source projects and licenses.
skills/ai-writing-suite/NOTICE.md:104:- **Pattern IDs:** stable identifiers for each pattern, not source-specific numbering.
skills/ai-writing-suite/NOTICE.md:105:- **Deduplicated catalog:** seven overlapping lists merged into one, with every pattern preserving its source credits.
skills/ai-writing-suite/NOTICE.md:106:
skills/ai-writing-suite/NOTICE.md:107:---
skills/ai-writing-suite/NOTICE.md:108:
skills/ai-writing-suite/NOTICE.md:109:## License Summary
skills/ai-writing-suite/NOTICE.md:110:
skills/ai-writing-suite/NOTICE.md:111:All source material is MIT-licensed. Under MIT, this work is permitted to:
skills/ai-writing-suite/NOTICE.md:112:- Reproduce, prepare derivative works of, distribute, and sublicense the material
skills/ai-writing-suite/NOTICE.md:113:- **On the condition that:** copyright notices and license text are included in any distribution
skills/ai-writing-suite/NOTICE.md:114:
skills/ai-writing-suite/NOTICE.md:115:**Full MIT License text:** See `LICENSE` in the repository root.
skills/ai-writing-suite/NOTICE.md:116:
skills/ai-writing-suite/NOTICE.md:117:---
skills/ai-writing-suite/NOTICE.md:118:
skills/ai-writing-suite/NOTICE.md:119:## How to Use This Notice
skills/ai-writing-suite/NOTICE.md:120:
skills/ai-writing-suite/NOTICE.md:121:When redistributing or forking AI Writing Suite:
skills/ai-writing-suite/NOTICE.md:122:1. Keep this file (`NOTICE.md`) intact in every distribution.
skills/ai-writing-suite/NOTICE.md:123:2. Keep the `LICENSE` file in the repository root.
skills/ai-writing-suite/NOTICE.md:124:3. Preserve the source tags in `_shared/patterns/00-index.md` so pattern lineage remains traceable.
skills/ai-writing-suite/NOTICE.md:125:4. Update the source legend in `_shared/patterns/00-index.md` if you add new sources.
skills/ai-writing-suite/NOTICE.md:126:
skills/ai-writing-suite/NOTICE.md:127:---
skills/ai-writing-suite/NOTICE.md:128:
skills/ai-writing-suite/NOTICE.md:129:## No Private Material
skills/ai-writing-suite/NOTICE.md:130:
skills/ai-writing-suite/NOTICE.md:131:This package contains **no private prompts, local user configuration, secrets, or installed-skill internals**. All content is:
skills/ai-writing-suite/NOTICE.md:132:- Derived from the seven source projects above, or
skills/ai-writing-suite/NOTICE.md:133:- Newly written for the OSS suite, or
skills/ai-writing-suite/NOTICE.md:134:- Scaffolding and metadata to make the skill portable across Claude, Codex, Cursor, and RovoDev.
skills/ai-writing-suite/NOTICE.md:135:
skills/ai-writing-suite/NOTICE.md:136:The company version (not in this public repo) layers a proprietary **DS Comms Playbook** into the `_shared/knowledge/` slot via a Confluence page, keeping the playbook private while reusing the public engine.
skills/ai-writing-suite/NOTICE.md:137:
skills/ai-writing-suite/NOTICE.md:138:---
skills/ai-writing-suite/NOTICE.md:139:
skills/ai-writing-suite/NOTICE.md:140:## Questions or Corrections?
skills/ai-writing-suite/NOTICE.md:141:
skills/ai-writing-suite/NOTICE.md:142:If a copyright holder is incorrectly attributed, or if a source should be added, please open an issue or contact the repository maintainer.
skills/ai-writing-suite/README.md:1:# AI Writing Suite
skills/ai-writing-suite/README.md:2:
skills/ai-writing-suite/README.md:3:Polish prose that sounds AI-written without changing what the author meant.
skills/ai-writing-suite/README.md:4:
skills/ai-writing-suite/README.md:5:The differentiator is not "rewrite this better." It is:
skills/ai-writing-suite/README.md:6:
skills/ai-writing-suite/README.md:7:```text
skills/ai-writing-suite/README.md:8:preserve meaning, remove AI slop, keep author voice
skills/ai-writing-suite/README.md:9:```
skills/ai-writing-suite/README.md:10:
skills/ai-writing-suite/README.md:11:Use it when a draft has the usual model tells: filler, vague claims, inflated importance, forced structure, and rhythm that sounds too even.
skills/ai-writing-suite/README.md:12:
skills/ai-writing-suite/README.md:13:## What It Does
skills/ai-writing-suite/README.md:14:
skills/ai-writing-suite/README.md:15:`ai-writing-suite` is a four-part writing-assistant skillset:
skills/ai-writing-suite/README.md:16:
skills/ai-writing-suite/README.md:17:1. **comms-polish** (v1) — identify tells, preserve meaning, remove AI-shaped prose patterns, match author voice or register.
skills/ai-writing-suite/README.md:18:2. **voice-onboard** (v1) — interview, collect writing samples, distill your voice signature.
skills/ai-writing-suite/README.md:19:3. **comms-qa** (v2) — knowledge QA over a pluggable writing playbook.
skills/ai-writing-suite/README.md:20:4. **comms-draft** (v2) — guided drafting workflow using playbook best practices.
skills/ai-writing-suite/README.md:21:
skills/ai-writing-suite/README.md:22:An agent using the suite can:
skills/ai-writing-suite/README.md:23:
skills/ai-writing-suite/README.md:24:1. Identify the audience and purpose
skills/ai-writing-suite/README.md:25:2. Preserve facts, citations, numbers, commands, and claims
skills/ai-writing-suite/README.md:26:3. Remove AI-shaped prose patterns
skills/ai-writing-suite/README.md:27:4. Match the author's voice or the document's register
skills/ai-writing-suite/README.md:28:5. Return either a rewrite, a review, a detection score, or targeted file edits
skills/ai-writing-suite/README.md:29:
skills/ai-writing-suite/README.md:30:## Engine vs Fuel
skills/ai-writing-suite/README.md:31:
skills/ai-writing-suite/README.md:32:The OSS version ships the **engine** (comms-polish, voice-onboard, eval harness, self-improvement) with a generic **knowledge base** distilled from four open-source projects.
skills/ai-writing-suite/README.md:33:
skills/ai-writing-suite/README.md:34:The company version reuses the same engine and swaps a proprietary **DS Comms Playbook** into the knowledge slot via a Confluence page. The playbook never enters this public repository.
skills/ai-writing-suite/README.md:35:
skills/ai-writing-suite/README.md:36:```
skills/ai-writing-suite/README.md:37:OSS:     engine + generic KB
skills/ai-writing-suite/README.md:38:Company: engine + proprietary playbook (dropped in as data, not code)
skills/ai-writing-suite/README.md:39:```
skills/ai-writing-suite/README.md:40:
skills/ai-writing-suite/README.md:41:No code changes needed to switch playbooks.
skills/ai-writing-suite/README.md:42:
skills/ai-writing-suite/README.md:43:## When To Use It
skills/ai-writing-suite/README.md:44:
skills/ai-writing-suite/README.md:45:Use the suite for:
skills/ai-writing-suite/README.md:46:
skills/ai-writing-suite/README.md:47:- docs and README prose
skills/ai-writing-suite/README.md:48:- emails and status updates
skills/ai-writing-suite/README.md:49:- social posts and personal notes
skills/ai-writing-suite/README.md:50:- reports and summaries
skills/ai-writing-suite/README.md:51:- launch notes and user-facing copy
skills/ai-writing-suite/README.md:52:
skills/ai-writing-suite/README.md:53:Do not use it for source-code cleanup. Use a code cleanup or refactoring skill for that.
skills/ai-writing-suite/README.md:54:
skills/ai-writing-suite/README.md:55:## Sub-Skills
skills/ai-writing-suite/README.md:56:
skills/ai-writing-suite/README.md:57:### comms-polish (Ships in v1)
skills/ai-writing-suite/README.md:58:
skills/ai-writing-suite/README.md:59:Polish prose and detect AI tells.
skills/ai-writing-suite/README.md:60:
skills/ai-writing-suite/README.md:61:**Modes:**
skills/ai-writing-suite/README.md:62:- `detect` — find AI tells and estimate density without rewriting.
skills/ai-writing-suite/README.md:63:- `rewrite` — produce polished prose from pasted text.
skills/ai-writing-suite/README.md:64:- `edit` — modify a prose file in place while preserving structure.
skills/ai-writing-suite/README.md:65:- `review` — give prioritized writing findings without rewriting everything.
skills/ai-writing-suite/README.md:66:
skills/ai-writing-suite/README.md:67:**Features:**
skills/ai-writing-suite/README.md:68:- Consolidated AI-tell pattern catalog (seven deduplicated sources, each pattern source-tagged for attribution).
skills/ai-writing-suite/README.md:69:- Scenario presets (tweet, LinkedIn, README, memo).
skills/ai-writing-suite/README.md:70:- Final-pass checklist before publishing.
skills/ai-writing-suite/README.md:71:- Voice matching (reads `_shared/voice-profile.md` to calibrate tone and style if present).
skills/ai-writing-suite/README.md:72:- 0–100 AI-tell density score for before/after comparison.
skills/ai-writing-suite/README.md:73:
skills/ai-writing-suite/README.md:74:**Example:**
skills/ai-writing-suite/README.md:75:
skills/ai-writing-suite/README.md:76:Before:
skills/ai-writing-suite/README.md:77:```text
skills/ai-writing-suite/README.md:78:This robust workflow enables teams to seamlessly leverage contextual insights, ensuring a more effective and streamlined development experience.
skills/ai-writing-suite/README.md:79:```
skills/ai-writing-suite/README.md:80:
skills/ai-writing-suite/README.md:81:After:
skills/ai-writing-suite/README.md:82:```text
skills/ai-writing-suite/README.md:83:This workflow gives teams the context they need before they start editing.
skills/ai-writing-suite/README.md:84:```
skills/ai-writing-suite/README.md:85:
skills/ai-writing-suite/README.md:86:### voice-onboard (Ships in v1)
skills/ai-writing-suite/README.md:87:
skills/ai-writing-suite/README.md:88:Interview and distill your writing voice.
skills/ai-writing-suite/README.md:89:
skills/ai-writing-suite/README.md:90:**Features:**
skills/ai-writing-suite/README.md:91:- Guided conversation to collect writing samples (local files or pasted text).
skills/ai-writing-suite/README.md:92:- Extracts voice signature (tone, vocabulary, sentence shape, register preferences).
skills/ai-writing-suite/README.md:93:- Writes `_shared/voice-profile.md` for reuse across sessions.
skills/ai-writing-suite/README.md:94:- Structured host-profile template for consistent capture.
skills/ai-writing-suite/README.md:95:
skills/ai-writing-suite/README.md:96:### comms-qa (v2)
skills/ai-writing-suite/README.md:97:
skills/ai-writing-suite/README.md:98:Knowledge QA over a pluggable playbook.
skills/ai-writing-suite/README.md:99:
skills/ai-writing-suite/README.md:100:**Features:**
skills/ai-writing-suite/README.md:101:- Wiki-style markdown KB (zero external dependencies, portable across Claude / Codex / Cursor / RovoDev).
skills/ai-writing-suite/README.md:102:- Pure markdown + `INDEX.md` navigation; no host-specific MCP tools.
skills/ai-writing-suite/README.md:103:- Pluggable slot: OSS ships generic KB; company forks and drops a Confluence-sourced playbook.
skills/ai-writing-suite/README.md:104:- End-to-end smoke test in v1 proves the company step is "drop in a page", not "build a RAG engine".
skills/ai-writing-suite/README.md:105:
skills/ai-writing-suite/README.md:106:### comms-draft (v2)
skills/ai-writing-suite/README.md:107:
skills/ai-writing-suite/README.md:108:Guided drafting workflow using playbook best practices.
skills/ai-writing-suite/README.md:109:
skills/ai-writing-suite/README.md:110:**Features:**
skills/ai-writing-suite/README.md:111:- Playbook-driven interview flow.
skills/ai-writing-suite/README.md:112:- Real-time feedback on audience, structure, clarity.
skills/ai-writing-suite/README.md:113:- Cite-as-you-go pattern matching against the KB.
skills/ai-writing-suite/README.md:114:
skills/ai-writing-suite/README.md:115:## Self-Improvement (Human-Gated)
skills/ai-writing-suite/README.md:116:
skills/ai-writing-suite/README.md:117:After each session, the suite proposes new rules based on error analysis:
skills/ai-writing-suite/README.md:118:
skills/ai-writing-suite/README.md:119:1. Analyze edits you made or approved.
skills/ai-writing-suite/README.md:120:2. Propose candidate rules (e.g., "remove 'seamlessly'" or "tighten 'important to note'").
skills/ai-writing-suite/README.md:121:3. You approve; we eval-test the rule against the baseline.
skills/ai-writing-suite/README.md:122:4. Approved rules append to `_shared/learned-rules.md` (append-only, never auto-editing core logic).
skills/ai-writing-suite/README.md:123:
skills/ai-writing-suite/README.md:124:Rules improve over time without drift or degradation.
skills/ai-writing-suite/README.md:125:
skills/ai-writing-suite/README.md:126:## Knowledge Base
skills/ai-writing-suite/README.md:127:
skills/ai-writing-suite/README.md:128:The knowledge base lives in `_shared/knowledge/`:
skills/ai-writing-suite/README.md:129:
skills/ai-writing-suite/README.md:130:- `INDEX.md` — wiki-style navigation index.
skills/ai-writing-suite/README.md:131:- Topic markdown files — audience, clarity, revision, structure, tone, and more.
skills/ai-writing-suite/README.md:132:
skills/ai-writing-suite/README.md:133:**For OSS:** Generic best-practices entries distilled from four MIT-licensed source projects.
skills/ai-writing-suite/README.md:134:
skills/ai-writing-suite/README.md:135:**For company:** Drop in a Confluence page link; the engine reads and retrieves from your playbook.
skills/ai-writing-suite/README.md:136:
skills/ai-writing-suite/README.md:137:## Install
skills/ai-writing-suite/README.md:138:
skills/ai-writing-suite/README.md:139:Clone or copy this repo, then symlink the skill into your target environment.
skills/ai-writing-suite/README.md:140:
skills/ai-writing-suite/README.md:141:### Claude
skills/ai-writing-suite/README.md:142:
skills/ai-writing-suite/README.md:143:```bash
skills/ai-writing-suite/README.md:144:# Copy to your Claude Code skills directory
skills/ai-writing-suite/README.md:145:cp -r skills/ai-writing-suite ~/.claude/skills/ai-writing-suite
skills/ai-writing-suite/README.md:146:```
skills/ai-writing-suite/README.md:147:
skills/ai-writing-suite/README.md:148:Restart Claude Code so the skill list refreshes.
skills/ai-writing-suite/README.md:149:
skills/ai-writing-suite/README.md:150:### Codex
skills/ai-writing-suite/README.md:151:
skills/ai-writing-suite/README.md:152:```bash
skills/ai-writing-suite/README.md:153:# Copy to your Codex skills directory
skills/ai-writing-suite/README.md:154:cp -r skills/ai-writing-suite ~/.codex/skills/ai-writing-suite
skills/ai-writing-suite/README.md:155:```
skills/ai-writing-suite/README.md:156:
skills/ai-writing-suite/README.md:157:Restart Codex so the skill list refreshes.
skills/ai-writing-suite/README.md:158:
skills/ai-writing-suite/README.md:159:### Cursor / RovoDev (v2)
skills/ai-writing-suite/README.md:160:
skills/ai-writing-suite/README.md:161:See `packaging/` for surface-specific installation instructions (coming in v2).
skills/ai-writing-suite/README.md:162:
skills/ai-writing-suite/README.md:163:## How to Use
skills/ai-writing-suite/README.md:164:
skills/ai-writing-suite/README.md:165:### Invoke comms-polish
skills/ai-writing-suite/README.md:166:
skills/ai-writing-suite/README.md:167:```
skills/ai-writing-suite/README.md:168:I wrote this: "[pasted text]"
skills/ai-writing-suite/README.md:169:Rewrite it to sound less AI-generated, keeping the facts and my voice.
skills/ai-writing-suite/README.md:170:Mode: rewrite
skills/ai-writing-suite/README.md:171:Audience: technical docs / LinkedIn post / memo / etc.
skills/ai-writing-suite/README.md:172:```
skills/ai-writing-suite/README.md:173:
skills/ai-writing-suite/README.md:174:Or:
skills/ai-writing-suite/README.md:175:
skills/ai-writing-suite/README.md:176:```
skills/ai-writing-suite/README.md:177:Detect AI tells in this: "[pasted text]"
skills/ai-writing-suite/README.md:178:Give me a score and top three edits I could make.
skills/ai-writing-suite/README.md:179:Mode: detect
skills/ai-writing-suite/README.md:180:```
skills/ai-writing-suite/README.md:181:
skills/ai-writing-suite/README.md:182:### Invoke voice-onboard
skills/ai-writing-suite/README.md:183:
skills/ai-writing-suite/README.md:184:```
skills/ai-writing-suite/README.md:185:I want to teach you my writing voice. Here are some samples: [paste or link files]
skills/ai-writing-suite/README.md:186:```
skills/ai-writing-suite/README.md:187:
skills/ai-writing-suite/README.md:188:The skill interviews you, extracts your voice signature, and saves it for all future sessions.
skills/ai-writing-suite/README.md:189:
skills/ai-writing-suite/README.md:190:### Read the learned rules
skills/ai-writing-suite/README.md:191:
skills/ai-writing-suite/README.md:192:```
skills/ai-writing-suite/README.md:193:What rules have we learned so far?
skills/ai-writing-suite/README.md:194:```
skills/ai-writing-suite/README.md:195:
skills/ai-writing-suite/README.md:196:The suite shows `_shared/learned-rules.md`, which grows as new patterns emerge from your writing.
skills/ai-writing-suite/README.md:197:
skills/ai-writing-suite/README.md:198:## Evaluation
skills/ai-writing-suite/README.md:199:
skills/ai-writing-suite/README.md:200:The suite ships with:
skills/ai-writing-suite/README.md:201:
skills/ai-writing-suite/README.md:202:- **Before/after fixtures** across genres (tweet, LinkedIn, README, memo).
skills/ai-writing-suite/README.md:203:- **LLM-judged scoring** — a rubric calibrated so the baseline fails 30–40% of cases.
skills/ai-writing-suite/README.md:204:- **Mechanical regression gate** — ported from avoid-ai JavaScript detector.
skills/ai-writing-suite/README.md:205:- **Self-improvement integration** — each proposed rule is eval-tested before you approve it.
skills/ai-writing-suite/README.md:206:
skills/ai-writing-suite/README.md:207:See `evals/` for details.
skills/ai-writing-suite/README.md:208:
skills/ai-writing-suite/README.md:209:## Attribution
skills/ai-writing-suite/README.md:210:
skills/ai-writing-suite/README.md:211:This suite absorbs and extends patterns, templates, and methodologies from seven open-source projects, all MIT-licensed:
skills/ai-writing-suite/README.md:212:
skills/ai-writing-suite/README.md:213:1. **weijt606/anti-vibe-writing** — bilingual patterns, scenario presets, host-profile template.
skills/ai-writing-suite/README.md:214:2. **conorbronsdon/avoid-ai-writing** — JS detector, CATEGORIES taxonomy, packaging patterns.
skills/ai-writing-suite/README.md:215:3. **donghuixin/AI-Vibe-Writing-Skills** — style-extractor prompts, memory patterns, self-improvement shape.
skills/ai-writing-suite/README.md:216:4. **Yuan1z0825/nature-skills** — academic polish rubric, structural patterns, plugin conventions.
skills/ai-writing-suite/README.md:217:5. **stop-slop** by Hardik Pandya — core directness rules, scoring methodology.
skills/ai-writing-suite/README.md:218:6. **blader/humanizer** by Brandon Wise — 43-pattern catalog, voice calibration.
skills/ai-writing-suite/README.md:219:7. **aboudjem/humanizer-skill** — 30-pattern catalog derived from Wikipedia "Signs of AI writing".
skills/ai-writing-suite/README.md:220:
skills/ai-writing-suite/README.md:221:See `NOTICE.md` for full copyright and license details. Every absorbed pattern is source-tagged in `_shared/patterns/00-index.md` for traceability.
skills/ai-writing-suite/README.md:222:
skills/ai-writing-suite/README.md:223:## Design Decisions
skills/ai-writing-suite/README.md:224:
skills/ai-writing-suite/README.md:225:For a full account of why the suite is built this way, see:
skills/ai-writing-suite/README.md:226:
skills/ai-writing-suite/README.md:227:- `docs/design-ai-writing-suite-v1-2026-06-06.md` — decision log (D1–D12), risks, success criteria.
skills/ai-writing-suite/README.md:228:- `CLAUDE.md` — project-specific conventions and working style.
skills/ai-writing-suite/README.md:229:
skills/ai-writing-suite/README.md:230:Key decisions include:
skills/ai-writing-suite/README.md:231:
skills/ai-writing-suite/README.md:232:- **D1 (Product):** Full suite, not a narrow humanizer; OSS face of a company DS skillset.
skills/ai-writing-suite/README.md:233:- **D2 (Reuse):** Absorb all MIT sources with preserved attribution.
skills/ai-writing-suite/README.md:234:- **D5 (RAG):** Pure markdown + convention, not host-specific MCP tools; portable across Claude / Codex / Cursor / RovoDev.
skills/ai-writing-suite/README.md:235:- **D6 (Safety):** Human-gated self-improvement; never auto-edit core logic.
skills/ai-writing-suite/README.md:236:- **D12 (v1 Scope):** Prove one end-to-end KB smoke path so company step is "drop in a page", not "build a RAG".
skills/ai-writing-suite/README.md:237:
skills/ai-writing-suite/README.md:238:## License
skills/ai-writing-suite/README.md:239:
skills/ai-writing-suite/README.md:240:MIT License. See `LICENSE` and `NOTICE.md` for details.
docs/migration-plan-local-repo-2026-06-06.md:1:# Migration Plan — AI Writing Suite → Independent LOCAL Repo
docs/migration-plan-local-repo-2026-06-06.md:2:
docs/migration-plan-local-repo-2026-06-06.md:3:Date: 2026-06-06
docs/migration-plan-local-repo-2026-06-06.md:4:Status: **PLAN ONLY — awaiting explicit "go"**
docs/migration-plan-local-repo-2026-06-06.md:5:Scope: **Local filesystem + local git only. NO GitHub actions in this phase.**
docs/migration-plan-local-repo-2026-06-06.md:6:
docs/migration-plan-local-repo-2026-06-06.md:7:---
docs/migration-plan-local-repo-2026-06-06.md:8:
docs/migration-plan-local-repo-2026-06-06.md:9:## 0. Restate (confirm before I act)
docs/migration-plan-local-repo-2026-06-06.md:10:
docs/migration-plan-local-repo-2026-06-06.md:11:- **(a) Plan-only or plan+build?** Plan-only now → migrate after you approve → build the v1 suite
docs/migration-plan-local-repo-2026-06-06.md:12:  in a *separate* approved phase. This doc covers the **migration only**, not the v1 build.
docs/migration-plan-local-repo-2026-06-06.md:13:- **(b) In scope:** create a new independent local repo for `ai-writing-suite`; the existing
docs/migration-plan-local-repo-2026-06-06.md:14:  Codex-path copy stays untouched as a backup until you confirm deletion.
docs/migration-plan-local-repo-2026-06-06.md:15:- **(c) Expected output:** a working independent local git repo + a 3-line "done" report.
docs/migration-plan-local-repo-2026-06-06.md:16:
docs/migration-plan-local-repo-2026-06-06.md:17:---
docs/migration-plan-local-repo-2026-06-06.md:18:
docs/migration-plan-local-repo-2026-06-06.md:19:## 1. Your decisions (this session)
docs/migration-plan-local-repo-2026-06-06.md:20:
docs/migration-plan-local-repo-2026-06-06.md:21:| Q | Decision | Effect on plan |
docs/migration-plan-local-repo-2026-06-06.md:22:|---|----------|----------------|
docs/migration-plan-local-repo-2026-06-06.md:23:| Migration shape | **Move local folder only** + override: *"local repo, not GitHub as of now"* | Local-only. No new GitHub repo, no push, no remote rename. |
docs/migration-plan-local-repo-2026-06-06.md:24:| Git history | **Preserve suite history** | Use `git clone` (local), not fresh `git init`. |
docs/migration-plan-local-repo-2026-06-06.md:25:| PR #4 | "Close PR #4" — **but** GitHub override defers it | PR #4 left OPEN for now; close it later when we do the GitHub phase. |
docs/migration-plan-local-repo-2026-06-06.md:26:
docs/migration-plan-local-repo-2026-06-06.md:27:---
docs/migration-plan-local-repo-2026-06-06.md:28:
docs/migration-plan-local-repo-2026-06-06.md:29:## 2. The one open decision in this plan
docs/migration-plan-local-repo-2026-06-06.md:30:
docs/migration-plan-local-repo-2026-06-06.md:31:**How much to carry over + the mechanic.** Two clean options — I recommend **A**:
docs/migration-plan-local-repo-2026-06-06.md:32:
docs/migration-plan-local-repo-2026-06-06.md:33:### Option A — Local clone, then prune (RECOMMENDED)
docs/migration-plan-local-repo-2026-06-06.md:34:1. `git clone` the umbrella repo (local path → local path). Full history preserved automatically,
docs/migration-plan-local-repo-2026-06-06.md:35:   including the design doc, the rename commit, and everything else.
docs/migration-plan-local-repo-2026-06-06.md:36:2. In the new copy: delete `skills/agent-goal-contracts/`, flatten/keep `skills/ai-writing-suite/`,
docs/migration-plan-local-repo-2026-06-06.md:37:   update `README.md` + `CLAUDE.md` to be suite-only. Commit that as one "extract to standalone repo" commit.
docs/migration-plan-local-repo-2026-06-06.md:38:3. Remove the `origin` remote so we can't accidentally push to the umbrella. (No GitHub this phase.)
docs/migration-plan-local-repo-2026-06-06.md:39:
docs/migration-plan-local-repo-2026-06-06.md:40:- **Pros:** simplest, safest, preserves *all* history (incl. root-level `docs/`), nothing on GitHub touched.
docs/migration-plan-local-repo-2026-06-06.md:41:- **Cons:** the new repo's *history* still mentions `agent-goal-contracts` (it's deleted in the latest
docs/migration-plan-local-repo-2026-06-06.md:42:  commit, just visible in `git log`). Cosmetic only.
docs/migration-plan-local-repo-2026-06-06.md:43:
docs/migration-plan-local-repo-2026-06-06.md:44:### Option B — `git subtree split` (surgical extract)
docs/migration-plan-local-repo-2026-06-06.md:45:- Extract only `skills/ai-writing-suite/` history into a brand-new repo.
docs/migration-plan-local-repo-2026-06-06.md:46:- **Pros:** history contains *only* suite commits.
docs/migration-plan-local-repo-2026-06-06.md:47:- **Cons:** (1) misses root-level `docs/` (design doc, handovers live at repo root, not under the skill);
docs/migration-plan-local-repo-2026-06-06.md:48:  (2) the `ai-writing-humanizer → ai-writing-suite` rename means pre-rename history may not follow the
docs/migration-plan-local-repo-2026-06-06.md:49:  prefix cleanly. More steps, more gotchas. Overkill for a personal project.
docs/migration-plan-local-repo-2026-06-06.md:50:
docs/migration-plan-local-repo-2026-06-06.md:51:> **My recommendation: Option A.** It honors "preserve history" with the least risk, and the only
docs/migration-plan-local-repo-2026-06-06.md:52:> downside is cosmetic log entries. You're a learner — A is the boring, safe choice.
docs/migration-plan-local-repo-2026-06-06.md:53:
docs/migration-plan-local-repo-2026-06-06.md:54:---
docs/migration-plan-local-repo-2026-06-06.md:55:
docs/migration-plan-local-repo-2026-06-06.md:56:## 3. Proposed new local home
docs/migration-plan-local-repo-2026-06-06.md:57:
docs/migration-plan-local-repo-2026-06-06.md:58:`~/Documents/ai-writing-suite/`  (out of `~/Documents/Codex/2026-06-01/...`)
docs/migration-plan-local-repo-2026-06-06.md:59:
docs/migration-plan-local-repo-2026-06-06.md:60:Confirm this path or give me another.
docs/migration-plan-local-repo-2026-06-06.md:61:
docs/migration-plan-local-repo-2026-06-06.md:62:---
docs/migration-plan-local-repo-2026-06-06.md:63:
docs/migration-plan-local-repo-2026-06-06.md:64:## 4. Step-by-step (Option A) — what I'll run after "go"
docs/migration-plan-local-repo-2026-06-06.md:65:
docs/migration-plan-local-repo-2026-06-06.md:66:```bash
docs/migration-plan-local-repo-2026-06-06.md:67:# 1. Sanity: confirm clean-ish state, current branch (rename-ai-writing-suite has the latest content)
docs/migration-plan-local-repo-2026-06-06.md:68:cd ~/Documents/Codex/2026-06-01/personal-productivity-skills
docs/migration-plan-local-repo-2026-06-06.md:69:git status --short
docs/migration-plan-local-repo-2026-06-06.md:70:git branch --show-current
docs/migration-plan-local-repo-2026-06-06.md:71:
docs/migration-plan-local-repo-2026-06-06.md:72:# 2. Local clone to the new home (full history, local-to-local, no network)
docs/migration-plan-local-repo-2026-06-06.md:73:git clone . ~/Documents/ai-writing-suite
docs/migration-plan-local-repo-2026-06-06.md:74:
docs/migration-plan-local-repo-2026-06-06.md:75:# 3. In the new repo: check out the branch that has the rename + v1 design, make it the working line
docs/migration-plan-local-repo-2026-06-06.md:76:cd ~/Documents/ai-writing-suite
docs/migration-plan-local-repo-2026-06-06.md:77:git checkout rename-ai-writing-suite      # or merge it into a fresh main locally
docs/migration-plan-local-repo-2026-06-06.md:78:
docs/migration-plan-local-repo-2026-06-06.md:79:# 4. Remove the GitHub remote (no GitHub actions this phase)
docs/migration-plan-local-repo-2026-06-06.md:80:git remote remove origin
docs/migration-plan-local-repo-2026-06-06.md:81:
docs/migration-plan-local-repo-2026-06-06.md:82:# 5. Prune to suite-only (separate, reviewable commit — I'll show staged files first)
docs/migration-plan-local-repo-2026-06-06.md:83:git rm -r skills/agent-goal-contracts
docs/migration-plan-local-repo-2026-06-06.md:84:#   + edit README.md / CLAUDE.md to drop umbrella + agent-goal-contracts language
docs/migration-plan-local-repo-2026-06-06.md:85:#   + (optional) flatten skills/ai-writing-suite/* to repo root — DECISION below
docs/migration-plan-local-repo-2026-06-06.md:86:
docs/migration-plan-local-repo-2026-06-06.md:87:# 6. Commit the extraction (after you approve the staged file list)
docs/migration-plan-local-repo-2026-06-06.md:88:
docs/migration-plan-local-repo-2026-06-06.md:89:# 7. Verify (see §6)
docs/migration-plan-local-repo-2026-06-06.md:90:```
docs/migration-plan-local-repo-2026-06-06.md:91:
docs/migration-plan-local-repo-2026-06-06.md:92:### Sub-decision: flatten or keep nesting?
docs/migration-plan-local-repo-2026-06-06.md:93:- **Keep `skills/ai-writing-suite/`** (no flatten) → matches the design doc's eventual multi-sub-skill
docs/migration-plan-local-repo-2026-06-06.md:94:  layout (`skills/comms-polish/`, etc.). **Recommended** — the suite *grows into* sub-skills.
docs/migration-plan-local-repo-2026-06-06.md:95:- **Flatten to root** → simpler now, but fights the planned architecture later.
docs/migration-plan-local-repo-2026-06-06.md:96:
docs/migration-plan-local-repo-2026-06-06.md:97:> Recommend **keep nesting** — the v1 design already assumes a `skills/` + `_shared/` layout.
docs/migration-plan-local-repo-2026-06-06.md:98:
docs/migration-plan-local-repo-2026-06-06.md:99:---
docs/migration-plan-local-repo-2026-06-06.md:100:
docs/migration-plan-local-repo-2026-06-06.md:101:## 5. What I will NOT do (guardrails)
docs/migration-plan-local-repo-2026-06-06.md:102:
docs/migration-plan-local-repo-2026-06-06.md:103:- ❌ No `git push`, no new GitHub repo, no closing PR #4, no remote rename — **nothing on GitHub**.
docs/migration-plan-local-repo-2026-06-06.md:104:- ❌ No deleting the original Codex-path copy until you confirm (it's our backup/rollback).
docs/migration-plan-local-repo-2026-06-06.md:105:- ❌ No starting the v1 suite build — that's a separate approval.
docs/migration-plan-local-repo-2026-06-06.md:106:- ❌ No new deps, no new files beyond this plan + the migration commits.
docs/migration-plan-local-repo-2026-06-06.md:107:
docs/migration-plan-local-repo-2026-06-06.md:108:---
docs/migration-plan-local-repo-2026-06-06.md:109:
docs/migration-plan-local-repo-2026-06-06.md:110:## 6. Verification (how I'll prove the migration worked)
docs/migration-plan-local-repo-2026-06-06.md:111:
docs/migration-plan-local-repo-2026-06-06.md:112:1. `git -C ~/Documents/ai-writing-suite log --oneline -10` → history present (preserved).
docs/migration-plan-local-repo-2026-06-06.md:113:2. `git -C ~/Documents/ai-writing-suite remote -v` → **empty** (no GitHub remote).
docs/migration-plan-local-repo-2026-06-06.md:114:3. `ls ~/Documents/ai-writing-suite/skills/` → `ai-writing-suite/` present, `agent-goal-contracts/` gone.
docs/migration-plan-local-repo-2026-06-06.md:115:4. `git -C ~/Documents/ai-writing-suite status` → clean tree.
docs/migration-plan-local-repo-2026-06-06.md:116:5. Original `~/Documents/Codex/.../personal-productivity-skills` → **untouched** (verify git log + remote intact).
docs/migration-plan-local-repo-2026-06-06.md:117:
docs/migration-plan-local-repo-2026-06-06.md:118:Report back as a 5-line PASS/FAIL table, then ask before any cleanup of the original.
docs/migration-plan-local-repo-2026-06-06.md:119:
docs/migration-plan-local-repo-2026-06-06.md:120:---
docs/migration-plan-local-repo-2026-06-06.md:121:
docs/migration-plan-local-repo-2026-06-06.md:122:## 7. After migration (NOT now — your call later)
docs/migration-plan-local-repo-2026-06-06.md:123:
docs/migration-plan-local-repo-2026-06-06.md:124:- GitHub phase (when you're ready): create `surahli123/ai-writing-suite`, push, close PR #4 on the umbrella.
docs/migration-plan-local-repo-2026-06-06.md:125:- v1 suite build: follow `docs/design-ai-writing-suite-v1-2026-06-06.md` §5 (separate approval).
docs/migration-plan-local-repo-2026-06-06.md:126:- Update memory `project_ai_writing_suite.md` with the new local path.
docs/migration-plan-local-repo-2026-06-06.md:127:
docs/migration-plan-local-repo-2026-06-06.md:128:---
docs/migration-plan-local-repo-2026-06-06.md:129:
docs/migration-plan-local-repo-2026-06-06.md:130:## 8. Open questions for you (answer inline, I'll proceed)
docs/migration-plan-local-repo-2026-06-06.md:131:
docs/migration-plan-local-repo-2026-06-06.md:132:1. **Option A (clone-then-prune)** or B (subtree split)? — I recommend **A**.
docs/migration-plan-local-repo-2026-06-06.md:133:2. **New local path** = `~/Documents/ai-writing-suite/`? — yes / give another.
docs/migration-plan-local-repo-2026-06-06.md:134:3. **Keep `skills/` nesting** (recommended) or flatten to root?
docs/migration-plan-local-repo-2026-06-06.md:135:4. Anything else you want carried/dropped (e.g. the `.omc/` state dir, untracked handovers)?
skills/ai-writing-suite/SKILL.md:1:---
skills/ai-writing-suite/SKILL.md:2:name: ai-writing-suite
skills/ai-writing-suite/SKILL.md:3:description: A suite of writing-assistant skills for professional and product communication — polish/de-AI prose, learn an author's voice, and (later) answer questions from a knowledge base and draft from it. Routes a request to the right sub-skill. Use for docs, emails, posts, reports, and user-facing copy; not for source-code cleanup.
skills/ai-writing-suite/SKILL.md:4:---
skills/ai-writing-suite/SKILL.md:5:
skills/ai-writing-suite/SKILL.md:6:# AI Writing Suite (router)
skills/ai-writing-suite/SKILL.md:7:
skills/ai-writing-suite/SKILL.md:8:This is a thin router. It does not contain polishing or drafting logic itself —
skills/ai-writing-suite/SKILL.md:9:it points the host at the sub-skill that does the work. Think of it as the
skills/ai-writing-suite/SKILL.md:10:dispatch layer in front of four specialized writers.
skills/ai-writing-suite/SKILL.md:11:
skills/ai-writing-suite/SKILL.md:12:## Sub-skills
skills/ai-writing-suite/SKILL.md:13:
skills/ai-writing-suite/SKILL.md:14:| Sub-skill | What it does | Status |
skills/ai-writing-suite/SKILL.md:15:| --- | --- | --- |
skills/ai-writing-suite/SKILL.md:16:| `comms-polish` | Polish, review, detect, or edit prose to remove AI tells while preserving meaning and voice. 0-100 AI-tell score on demand. | **available (v1)** |
skills/ai-writing-suite/SKILL.md:17:| `voice-onboard` | Interview the author and distill their historical writing into a reusable voice profile that `comms-polish` reads. | built in Layer 1 |
skills/ai-writing-suite/SKILL.md:18:| `comms-qa` | Answer questions from the knowledge base (mini-RAG over the pluggable KB). | coming in v2 |
skills/ai-writing-suite/SKILL.md:19:| `comms-draft` | Draft a new page guided by the knowledge base / playbook. | coming in v2 |
skills/ai-writing-suite/SKILL.md:20:
skills/ai-writing-suite/SKILL.md:21:The sub-skills live under `skills/<name>/SKILL.md`. Shared assets (the AI-tell
skills/ai-writing-suite/SKILL.md:22:pattern catalog, and later the voice profile and learned-rules log) live under
skills/ai-writing-suite/SKILL.md:23:`_shared/`.
skills/ai-writing-suite/SKILL.md:24:
skills/ai-writing-suite/SKILL.md:25:## How routing works
skills/ai-writing-suite/SKILL.md:26:
skills/ai-writing-suite/SKILL.md:27:The right dispatch path depends on the host. Two cases:
skills/ai-writing-suite/SKILL.md:28:
skills/ai-writing-suite/SKILL.md:29:### Claude / Codex / Cursor — host-native dispatch
skills/ai-writing-suite/SKILL.md:30:
skills/ai-writing-suite/SKILL.md:31:These hosts already discover and trigger skills by their `name` + `description`.
skills/ai-writing-suite/SKILL.md:32:Do **not** intercept or re-route here. Let the host pick the sub-skill from the
skills/ai-writing-suite/SKILL.md:33:request. This router exists mainly as documentation and as the package entry
skills/ai-writing-suite/SKILL.md:34:point; it is not a runtime interceptor on these surfaces. (Reinventing host
skills/ai-writing-suite/SKILL.md:35:dispatch is a Layer 1 concern, deliberately out of scope.)
skills/ai-writing-suite/SKILL.md:36:
skills/ai-writing-suite/SKILL.md:37:### RovoDev — explicit intent routing
skills/ai-writing-suite/SKILL.md:38:
skills/ai-writing-suite/SKILL.md:39:RovoDev does not auto-trigger skills. When invoked there, read the user's intent
skills/ai-writing-suite/SKILL.md:40:and route explicitly:
skills/ai-writing-suite/SKILL.md:41:
skills/ai-writing-suite/SKILL.md:42:| If the user wants to… | Route to |
skills/ai-writing-suite/SKILL.md:43:| --- | --- |
skills/ai-writing-suite/SKILL.md:44:| clean up / de-AI / polish / review / score a draft | `comms-polish` |
skills/ai-writing-suite/SKILL.md:45:| teach the tool their writing style, build a voice profile | `voice-onboard` (Layer 1; until then, fall back to `comms-polish` voice matching) |
skills/ai-writing-suite/SKILL.md:46:| ask a question answered by the knowledge base | `comms-qa` (v2; until then, say it's not built yet) |
skills/ai-writing-suite/SKILL.md:47:| draft a new page from the playbook | `comms-draft` (v2; until then, say it's not built yet) |
skills/ai-writing-suite/SKILL.md:48:
skills/ai-writing-suite/SKILL.md:49:If intent is ambiguous, default to `comms-polish` (the most common job) and say
skills/ai-writing-suite/SKILL.md:50:which sub-skill you chose.
skills/ai-writing-suite/SKILL.md:51:
skills/ai-writing-suite/SKILL.md:52:## Boundary
skills/ai-writing-suite/SKILL.md:53:
skills/ai-writing-suite/SKILL.md:54:This suite edits and produces prose, not code. For source-code cleanup or
skills/ai-writing-suite/SKILL.md:55:refactoring, use a code-cleanup skill instead.
skills/ai-writing-suite/SKILL.md:56:
skills/ai-writing-suite/SKILL.md:57:## Engine vs fuel
skills/ai-writing-suite/SKILL.md:58:
skills/ai-writing-suite/SKILL.md:59:The suite is the *engine*; the knowledge base under `_shared/knowledge/` is the
skills/ai-writing-suite/SKILL.md:60:*fuel*. The open-source build ships a generic KB; a company fork drops its own
skills/ai-writing-suite/SKILL.md:61:playbook into the same slot. The playbook never enters this public repo. (This
skills/ai-writing-suite/SKILL.md:62:build ships a generic 5-entry KB seed + `INDEX.md` + a working retrieval smoke
skills/ai-writing-suite/SKILL.md:63:path; the full `comms-qa` question-answering sub-skill is v2.)
skills/ai-writing-suite/_shared/knowledge/revision.md:1:# Revision — the draft is raw material; editing makes it good
skills/ai-writing-suite/_shared/knowledge/revision.md:2:
skills/ai-writing-suite/_shared/knowledge/revision.md:3:> **Generic best-practice entry.** Distilled from the four MIT reference repos
skills/ai-writing-suite/_shared/knowledge/revision.md:4:> (see `Sources`). Open-source KB; company forks swap via the same slot
skills/ai-writing-suite/_shared/knowledge/revision.md:5:> (`README.md`).
skills/ai-writing-suite/_shared/knowledge/revision.md:6:
skills/ai-writing-suite/_shared/knowledge/revision.md:7:## Principle
skills/ai-writing-suite/_shared/knowledge/revision.md:8:
skills/ai-writing-suite/_shared/knowledge/revision.md:9:No one writes well in one pass. The first draft exists to get the ideas down;
skills/ai-writing-suite/_shared/knowledge/revision.md:10:revision is where clarity, structure, and tone actually get fixed. Treat the
skills/ai-writing-suite/_shared/knowledge/revision.md:11:first draft as disposable and the editing pass as the real work.
skills/ai-writing-suite/_shared/knowledge/revision.md:12:
skills/ai-writing-suite/_shared/knowledge/revision.md:13:## Moves
skills/ai-writing-suite/_shared/knowledge/revision.md:14:
skills/ai-writing-suite/_shared/knowledge/revision.md:15:- **Separate drafting from editing.** Get the whole thing down before you polish
skills/ai-writing-suite/_shared/knowledge/revision.md:16:  any of it. Editing while drafting stalls both.
skills/ai-writing-suite/_shared/knowledge/revision.md:17:- **Read it aloud.** Sentences you stumble over are sentences the reader will
skills/ai-writing-suite/_shared/knowledge/revision.md:18:  stumble over. This catches rhythm problems no checklist will.
skills/ai-writing-suite/_shared/knowledge/revision.md:19:- **Cut 10% on the second pass.** Almost every draft is too long. Delete the
skills/ai-writing-suite/_shared/knowledge/revision.md:20:  weakest sentence in each paragraph; the paragraph usually improves.
skills/ai-writing-suite/_shared/knowledge/revision.md:21:- **Check the opening last.** After the body is solid, you know what the piece is
skills/ai-writing-suite/_shared/knowledge/revision.md:22:  actually about — rewrite the first line to earn the read.
skills/ai-writing-suite/_shared/knowledge/revision.md:23:- **Run a final tell-sweep.** Before sending, scan for the AI tells: forced
skills/ai-writing-suite/_shared/knowledge/revision.md:24:  triads, em-dash overuse, "it's not just X, it's Y," sycophancy, hype words.
skills/ai-writing-suite/_shared/knowledge/revision.md:25:  See the pattern catalog in `_shared/patterns/`.
skills/ai-writing-suite/_shared/knowledge/revision.md:26:
skills/ai-writing-suite/_shared/knowledge/revision.md:27:## Before / After
skills/ai-writing-suite/_shared/knowledge/revision.md:28:
skills/ai-writing-suite/_shared/knowledge/revision.md:29:- **Before (first draft):** I think that this approach could potentially be quite
skills/ai-writing-suite/_shared/knowledge/revision.md:30:  beneficial in a number of ways, and it's worth noting that there are several
skills/ai-writing-suite/_shared/knowledge/revision.md:31:  considerations to keep in mind.
skills/ai-writing-suite/_shared/knowledge/revision.md:32:- **After (revised):** This approach has two real benefits and one cost. Here they
skills/ai-writing-suite/_shared/knowledge/revision.md:33:  are.
skills/ai-writing-suite/_shared/knowledge/revision.md:34:
skills/ai-writing-suite/_shared/knowledge/revision.md:35:## When this matters most
skills/ai-writing-suite/_shared/knowledge/revision.md:36:
skills/ai-writing-suite/_shared/knowledge/revision.md:37:Every piece that matters. The gap between a mediocre writer and a good one is
skills/ai-writing-suite/_shared/knowledge/revision.md:38:mostly the willingness to do a second and third pass.
skills/ai-writing-suite/_shared/knowledge/revision.md:39:
skills/ai-writing-suite/_shared/knowledge/revision.md:40:## Sources
skills/ai-writing-suite/_shared/knowledge/revision.md:41:
skills/ai-writing-suite/_shared/knowledge/revision.md:42:- `anti-vibe` (`final-pass-checklist`, `human-passes`)
skills/ai-writing-suite/_shared/knowledge/revision.md:43:- `nature` (`nature-polishing` writing-strategy: revise in passes)
skills/ai-writing-suite/_shared/knowledge/revision.md:44:- `_shared/patterns/` (the full AI-tell catalog used in the final sweep)
skills/ai-writing-suite/_shared/knowledge/audience.md:1:# Audience — write for the specific reader, not "everyone"
skills/ai-writing-suite/_shared/knowledge/audience.md:2:
skills/ai-writing-suite/_shared/knowledge/audience.md:3:> **Generic best-practice entry.** Distilled from the four MIT reference repos
skills/ai-writing-suite/_shared/knowledge/audience.md:4:> (see `Sources`). Open-source KB; company forks swap via the same slot
skills/ai-writing-suite/_shared/knowledge/audience.md:5:> (`README.md`).
skills/ai-writing-suite/_shared/knowledge/audience.md:6:
skills/ai-writing-suite/_shared/knowledge/audience.md:7:## Principle
skills/ai-writing-suite/_shared/knowledge/audience.md:8:
skills/ai-writing-suite/_shared/knowledge/audience.md:9:Every piece has one primary reader with a job to do. Naming that reader — their
skills/ai-writing-suite/_shared/knowledge/audience.md:10:role, what they already know, what decision they need to make — settles most
skills/ai-writing-suite/_shared/knowledge/audience.md:11:style questions automatically. Writing for "everyone" produces text that lands
skills/ai-writing-suite/_shared/knowledge/audience.md:12:with no one.
skills/ai-writing-suite/_shared/knowledge/audience.md:13:
skills/ai-writing-suite/_shared/knowledge/audience.md:14:## Moves
skills/ai-writing-suite/_shared/knowledge/audience.md:15:
skills/ai-writing-suite/_shared/knowledge/audience.md:16:- **State the reader and their job before drafting.** "An on-call engineer who
skills/ai-writing-suite/_shared/knowledge/audience.md:17:  needs to decide whether to roll back." That sentence fixes tone, length, and
skills/ai-writing-suite/_shared/knowledge/audience.md:18:  jargon level.
skills/ai-writing-suite/_shared/knowledge/audience.md:19:- **Calibrate jargon to shared knowledge.** Define a term once if the reader
skills/ai-writing-suite/_shared/knowledge/audience.md:20:  might not know it; never define terms the reader uses daily (it reads as
skills/ai-writing-suite/_shared/knowledge/audience.md:21:  condescending or AI-padded).
skills/ai-writing-suite/_shared/knowledge/audience.md:22:- **Lead with what the reader cares about,** not what you find interesting. An
skills/ai-writing-suite/_shared/knowledge/audience.md:23:  exec wants the decision; an engineer wants the repro steps.
skills/ai-writing-suite/_shared/knowledge/audience.md:24:- **Cut the throat-clearing.** "In today's fast-paced world" and "as we all
skills/ai-writing-suite/_shared/knowledge/audience.md:25:  know" address no one. Address the actual reader directly.
skills/ai-writing-suite/_shared/knowledge/audience.md:26:
skills/ai-writing-suite/_shared/knowledge/audience.md:27:## Before / After
skills/ai-writing-suite/_shared/knowledge/audience.md:28:
skills/ai-writing-suite/_shared/knowledge/audience.md:29:- **Before:** This guide is designed to help users of all skill levels
skills/ai-writing-suite/_shared/knowledge/audience.md:30:  understand the fundamentals of our deployment process.
skills/ai-writing-suite/_shared/knowledge/audience.md:31:- **After:** If you're on-call and a deploy is failing, run `./rollback.sh`. The
skills/ai-writing-suite/_shared/knowledge/audience.md:32:  rest of this page explains what it does.
skills/ai-writing-suite/_shared/knowledge/audience.md:33:
skills/ai-writing-suite/_shared/knowledge/audience.md:34:## When this matters most
skills/ai-writing-suite/_shared/knowledge/audience.md:35:
skills/ai-writing-suite/_shared/knowledge/audience.md:36:Cross-functional writing — when an engineer writes for a PM, or a DS writes for
skills/ai-writing-suite/_shared/knowledge/audience.md:37:leadership. Mismatched audience is the most common reason good content fails to
skills/ai-writing-suite/_shared/knowledge/audience.md:38:land.
skills/ai-writing-suite/_shared/knowledge/audience.md:39:
skills/ai-writing-suite/_shared/knowledge/audience.md:40:## Sources
skills/ai-writing-suite/_shared/knowledge/audience.md:41:
skills/ai-writing-suite/_shared/knowledge/audience.md:42:- `anti-vibe` (`host-profile` + scenario-presets: reader-shaped voice)
skills/ai-writing-suite/_shared/knowledge/audience.md:43:- `ai-vibe` (`style-extractor` / reviewer prompts: audience modeling)
skills/ai-writing-suite/_shared/knowledge/audience.md:44:- `nature` (`nature-writing`: audience-aware framing per journal)
skills/ai-writing-suite/.claude-plugin/plugin.json:1:{
skills/ai-writing-suite/.claude-plugin/plugin.json:2:  "name": "ai-writing-suite",
skills/ai-writing-suite/.claude-plugin/plugin.json:3:  "description": "Suite of writing-assistant skills for professional and product communication. Polish and de-AI prose, learn an author's voice, answer KB questions, and draft from a knowledge base.",
skills/ai-writing-suite/.claude-plugin/plugin.json:4:  "version": "1.0.0",
skills/ai-writing-suite/.claude-plugin/plugin.json:5:  "author": {
skills/ai-writing-suite/.claude-plugin/plugin.json:6:    "name": "surahli123"
skills/ai-writing-suite/.claude-plugin/plugin.json:7:  },
skills/ai-writing-suite/.claude-plugin/plugin.json:8:  "homepage": "https://github.com/surahli123/ai-writing-suite",
skills/ai-writing-suite/.claude-plugin/plugin.json:9:  "repository": "https://github.com/surahli123/ai-writing-suite",
skills/ai-writing-suite/.claude-plugin/plugin.json:10:  "license": "MIT",
skills/ai-writing-suite/.claude-plugin/plugin.json:11:  "keywords": ["writing", "editing", "humanize", "voice", "comms", "polish"]
skills/ai-writing-suite/.claude-plugin/plugin.json:12:}
skills/ai-writing-suite/_shared/knowledge/INDEX.md:1:# Knowledge Base — Navigation Index
skills/ai-writing-suite/_shared/knowledge/INDEX.md:2:
skills/ai-writing-suite/_shared/knowledge/INDEX.md:3:> **This file is the retrieval backbone.** There is no embedding store, no vector
skills/ai-writing-suite/_shared/knowledge/INDEX.md:4:> DB, no MCP dependency (design decision **D5**). "Retrieval" = an agent reads
skills/ai-writing-suite/_shared/knowledge/INDEX.md:5:> this index, matches the user's question against the **Summary** and **Keywords
skills/ai-writing-suite/_shared/knowledge/INDEX.md:6:> / aliases** columns, then opens the one entry that fits and quotes the relevant
skills/ai-writing-suite/_shared/knowledge/INDEX.md:7:> passage. This works identically on Claude, Codex, Cursor, and RovoDev because
skills/ai-writing-suite/_shared/knowledge/INDEX.md:8:> it is pure markdown + file reads — nothing host-specific.
skills/ai-writing-suite/_shared/knowledge/INDEX.md:9:>
skills/ai-writing-suite/_shared/knowledge/INDEX.md:10:> Keep this index in sync with the entries. Adding a KB entry = add one file +
skills/ai-writing-suite/_shared/knowledge/INDEX.md:11:> one row here (the "ingestion" step — see `SMOKE-TEST.md`).
skills/ai-writing-suite/_shared/knowledge/INDEX.md:12:
skills/ai-writing-suite/_shared/knowledge/INDEX.md:13:## How an agent uses this index (retrieval protocol)
skills/ai-writing-suite/_shared/knowledge/INDEX.md:14:
skills/ai-writing-suite/_shared/knowledge/INDEX.md:15:1. Read the user's question.
skills/ai-writing-suite/_shared/knowledge/INDEX.md:16:2. Scan the **Keywords / aliases** column for term overlap, then the **Summary**
skills/ai-writing-suite/_shared/knowledge/INDEX.md:17:   column for intent overlap. Pick the single best-matching entry.
skills/ai-writing-suite/_shared/knowledge/INDEX.md:18:3. Open that entry file. Find the section (Principle / Moves / Before-After) that
skills/ai-writing-suite/_shared/knowledge/INDEX.md:19:   answers the question.
skills/ai-writing-suite/_shared/knowledge/INDEX.md:20:4. Answer from that passage; cite the entry filename. If two entries tie, open
skills/ai-writing-suite/_shared/knowledge/INDEX.md:21:   both and synthesize. If nothing matches, say so — do not invent guidance.
skills/ai-writing-suite/_shared/knowledge/INDEX.md:22:
skills/ai-writing-suite/_shared/knowledge/INDEX.md:23:## Entries
skills/ai-writing-suite/_shared/knowledge/INDEX.md:24:
skills/ai-writing-suite/_shared/knowledge/INDEX.md:25:| Entry file | Summary (one line) | Keywords / aliases |
skills/ai-writing-suite/_shared/knowledge/INDEX.md:26:| --- | --- | --- |
skills/ai-writing-suite/_shared/knowledge/INDEX.md:27:| `clarity.md` | Say one idea per sentence in plain, concrete words; cut filler. | clarity, clear, concise, plain language, wordy, verbose, filler, jargon, simplify, hard to read, confusing, cut words, concrete, vague |
skills/ai-writing-suite/_shared/knowledge/INDEX.md:28:| `structure.md` | Lead with the point (BLUF), one idea per paragraph, shape to channel. | structure, organization, order, BLUF, bottom line up front, flow, outline, headings, rambling, where to start, lead with, top-down, paragraph |
skills/ai-writing-suite/_shared/knowledge/INDEX.md:29:| `audience.md` | Write for one specific reader and their job, not "everyone." | audience, reader, who is this for, target reader, stakeholder, exec vs engineer, jargon level, too technical, condescending, tailor |
skills/ai-writing-suite/_shared/knowledge/INDEX.md:30:| `tone.md` | Sound like a competent colleague: direct, no sycophancy, no hype, varied rhythm. | tone, voice, formal, casual, sounds robotic, sounds like AI, stiff, corporate, hype, salesy, sycophantic, cheesy, register, how it sounds |
skills/ai-writing-suite/_shared/knowledge/INDEX.md:31:| `revision.md` | Treat the first draft as raw; fix it in editing passes; final tell-sweep. | revision, editing, revise, edit, second draft, polish, proofread, rewrite, read aloud, cut length, final pass, self-edit, improve a draft |
skills/ai-writing-suite/_shared/knowledge/INDEX.md:32:
skills/ai-writing-suite/_shared/knowledge/INDEX.md:33:## Categories (for browsing, not required for retrieval)
skills/ai-writing-suite/_shared/knowledge/INDEX.md:34:
skills/ai-writing-suite/_shared/knowledge/INDEX.md:35:- **Sentence-level:** `clarity.md`, `tone.md`
skills/ai-writing-suite/_shared/knowledge/INDEX.md:36:- **Document-level:** `structure.md`, `audience.md`
skills/ai-writing-suite/_shared/knowledge/INDEX.md:37:- **Process:** `revision.md`
skills/ai-writing-suite/_shared/knowledge/INDEX.md:38:
skills/ai-writing-suite/_shared/knowledge/INDEX.md:39:## Provenance
skills/ai-writing-suite/_shared/knowledge/INDEX.md:40:
skills/ai-writing-suite/_shared/knowledge/INDEX.md:41:All entries are generic professional-writing best practices distilled from four
skills/ai-writing-suite/_shared/knowledge/INDEX.md:42:MIT-licensed reference repos (`anti-vibe-writing`, `avoid-ai-writing`,
skills/ai-writing-suite/_shared/knowledge/INDEX.md:43:`AI-Vibe-Writing-Skills`, `nature-skills`). Per-entry `Sources` sections carry
skills/ai-writing-suite/_shared/knowledge/INDEX.md:44:the lineage; full attribution lives in the skill `NOTICE.md`. This is the
skills/ai-writing-suite/_shared/knowledge/INDEX.md:45:**open-source** KB. A company fork drops its proprietary playbook into this same
skills/ai-writing-suite/_shared/knowledge/INDEX.md:46:slot and updates this index — see `README.md` ("Swapping in a company playbook").
skills/ai-writing-suite/_shared/learned-rules.md:1:<!--
skills/ai-writing-suite/_shared/learned-rules.md:2:================================================================================
skills/ai-writing-suite/_shared/learned-rules.md:3:  learned-rules.md  —  HUMAN-GATED, APPEND-ONLY SELF-IMPROVEMENT LOG
skills/ai-writing-suite/_shared/learned-rules.md:4:================================================================================
skills/ai-writing-suite/_shared/learned-rules.md:5:
skills/ai-writing-suite/_shared/learned-rules.md:6:  WHAT THIS IS
skills/ai-writing-suite/_shared/learned-rules.md:7:  ------------
skills/ai-writing-suite/_shared/learned-rules.md:8:  The single place approved self-improvement rules live. The suite's sub-skills
skills/ai-writing-suite/_shared/learned-rules.md:9:  (`comms-polish`, `voice-onboard`) READ this file on start and apply matching
skills/ai-writing-suite/_shared/learned-rules.md:10:  active rules. The self-improvement hook APPENDS to it — but ONLY after the user
skills/ai-writing-suite/_shared/learned-rules.md:11:  explicitly approves a proposed rule. See `_shared/self-improvement.md` for the
skills/ai-writing-suite/_shared/learned-rules.md:12:  full protocol. Anti-drift design: plan §6 (D6), risk R3.
skills/ai-writing-suite/_shared/learned-rules.md:13:
skills/ai-writing-suite/_shared/learned-rules.md:14:  THE RULES OF THIS FILE
skills/ai-writing-suite/_shared/learned-rules.md:15:  ----------------------
skills/ai-writing-suite/_shared/learned-rules.md:16:  1. APPEND-ONLY. Never rewrite or delete an existing entry's rule text. To
skills/ai-writing-suite/_shared/learned-rules.md:17:     change a rule, append a NEW entry and set the old one's `status:` to
skills/ai-writing-suite/_shared/learned-rules.md:18:     `retired` (a one-line status flip is the only permitted edit to a past
skills/ai-writing-suite/_shared/learned-rules.md:19:     entry — its rule/rationale text stays as written, for audit).
skills/ai-writing-suite/_shared/learned-rules.md:20:  2. HUMAN-GATED. Nothing lands here without an explicit user "yes". The hook
skills/ai-writing-suite/_shared/learned-rules.md:21:     proposes; the user approves; only then does an entry appear.
skills/ai-writing-suite/_shared/learned-rules.md:22:  3. CORE LOGIC IS NEVER TOUCHED. Rules live here, not in any SKILL.md or in the
skills/ai-writing-suite/_shared/learned-rules.md:23:     pattern catalog. This file is the *only* mutable surface of the loop.
skills/ai-writing-suite/_shared/learned-rules.md:24:
skills/ai-writing-suite/_shared/learned-rules.md:25:  ENTRY FORMAT (stable schema — keep every field)
skills/ai-writing-suite/_shared/learned-rules.md:26:  -----------------------------------------------
skills/ai-writing-suite/_shared/learned-rules.md:27:  Each entry is one `### LR-NNN` block with these fields, in this order:
skills/ai-writing-suite/_shared/learned-rules.md:28:    - id        : LR-001, LR-002, ... (zero-padded, never reused)
skills/ai-writing-suite/_shared/learned-rules.md:29:    - rule      : the imperative the skill should follow (one or two sentences)
skills/ai-writing-suite/_shared/learned-rules.md:30:    - rationale : why — grounded in a real session correction, not theory
skills/ai-writing-suite/_shared/learned-rules.md:31:    - scope     : comms-polish | voice-onboard | all
skills/ai-writing-suite/_shared/learned-rules.md:32:    - date      : YYYY-MM-DD it was approved
skills/ai-writing-suite/_shared/learned-rules.md:33:    - status    : proposed | active | retired
skills/ai-writing-suite/_shared/learned-rules.md:34:                  (proposed = approved by user, not yet eval-measured in Layer 3;
skills/ai-writing-suite/_shared/learned-rules.md:35:                   active   = trusted/eval-passed, applied on every run;
skills/ai-writing-suite/_shared/learned-rules.md:36:                   retired  = superseded — see the entry that replaced it)
skills/ai-writing-suite/_shared/learned-rules.md:37:    - source    : short note on the session that produced it (auditable trail)
skills/ai-writing-suite/_shared/learned-rules.md:38:
skills/ai-writing-suite/_shared/learned-rules.md:39:  STATUS LIFECYCLE
skills/ai-writing-suite/_shared/learned-rules.md:40:  ----------------
skills/ai-writing-suite/_shared/learned-rules.md:41:  proposed --(Layer 3 eval passes, or user says "make it active")--> active
skills/ai-writing-suite/_shared/learned-rules.md:42:  active   --(a later entry supersedes it)--> retired
skills/ai-writing-suite/_shared/learned-rules.md:43:
skills/ai-writing-suite/_shared/learned-rules.md:44:  HOW SUB-SKILLS USE IT
skills/ai-writing-suite/_shared/learned-rules.md:45:  ---------------------
skills/ai-writing-suite/_shared/learned-rules.md:46:  On start, read this file and apply every entry whose status is `active` and
skills/ai-writing-suite/_shared/learned-rules.md:47:  whose scope matches the running skill (`all` matches both). Ignore `proposed`
skills/ai-writing-suite/_shared/learned-rules.md:48:  and `retired` entries when deciding behavior — `proposed` rules are not yet
skills/ai-writing-suite/_shared/learned-rules.md:49:  trusted; `retired` rules have been superseded.
skills/ai-writing-suite/_shared/learned-rules.md:50:================================================================================
skills/ai-writing-suite/_shared/learned-rules.md:51:-->
skills/ai-writing-suite/_shared/learned-rules.md:52:
skills/ai-writing-suite/_shared/learned-rules.md:53:# Learned Rules (append-only)
skills/ai-writing-suite/_shared/learned-rules.md:54:
skills/ai-writing-suite/_shared/learned-rules.md:55:Approved, human-gated self-improvement rules for the AI Writing Suite. Read on
skills/ai-writing-suite/_shared/learned-rules.md:56:start by the sub-skills; appended to only on explicit user approval. See
skills/ai-writing-suite/_shared/learned-rules.md:57:`_shared/self-improvement.md` for the protocol.
skills/ai-writing-suite/_shared/learned-rules.md:58:
skills/ai-writing-suite/_shared/learned-rules.md:59:<!-- ──────────────────────────────────────────────────────────────────────────
skills/ai-writing-suite/_shared/learned-rules.md:60:     EXAMPLE ENTRY (illustration only — NOT an active rule)
skills/ai-writing-suite/_shared/learned-rules.md:61:     This block shows the exact shape a real entry takes. It is intentionally
skills/ai-writing-suite/_shared/learned-rules.md:62:     marked status: retired and id LR-000 so no skill ever applies it. Delete
skills/ai-writing-suite/_shared/learned-rules.md:63:     it once real rules exist, or leave it as the format reference.
skills/ai-writing-suite/_shared/learned-rules.md:64:─────────────────────────────────────────────────────────────────────────── -->
skills/ai-writing-suite/_shared/learned-rules.md:65:
skills/ai-writing-suite/_shared/learned-rules.md:66:### LR-000  (EXAMPLE — do not apply)
skills/ai-writing-suite/_shared/learned-rules.md:67:
skills/ai-writing-suite/_shared/learned-rules.md:68:- **rule:** When polishing LinkedIn posts, do not flag a single leading rhetorical
skills/ai-writing-suite/_shared/learned-rules.md:69:  question as an AI tell; this author opens that way on purpose.
skills/ai-writing-suite/_shared/learned-rules.md:70:- **rationale:** Example only. In a real entry this cites a session where the user
skills/ai-writing-suite/_shared/learned-rules.md:71:  overrode the catalog's "engagement hook" flag because the opener was genuinely
skills/ai-writing-suite/_shared/learned-rules.md:72:  theirs, and the correction would recur on every LinkedIn post.
skills/ai-writing-suite/_shared/learned-rules.md:73:- **scope:** comms-polish
skills/ai-writing-suite/_shared/learned-rules.md:74:- **date:** 2026-06-06
skills/ai-writing-suite/_shared/learned-rules.md:75:- **status:** retired
skills/ai-writing-suite/_shared/learned-rules.md:76:- **source:** Example seed entry showing the schema. Not produced by a real
skills/ai-writing-suite/_shared/learned-rules.md:77:  session; kept as the format reference.
skills/ai-writing-suite/_shared/learned-rules.md:78:
skills/ai-writing-suite/_shared/learned-rules.md:79:<!-- ──────────────────────────────────────────────────────────────────────────
skills/ai-writing-suite/_shared/learned-rules.md:80:     REAL ENTRIES START BELOW. The hook appends new `### LR-NNN` blocks here,
skills/ai-writing-suite/_shared/learned-rules.md:81:     one per approved rule, newest at the bottom.
skills/ai-writing-suite/_shared/learned-rules.md:82:─────────────────────────────────────────────────────────────────────────── -->
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:1:# Punctuation & Formatting Tells
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:2:
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:3:Surface marks and formatting. Some of these (citation-markup leaks, UTM params,
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:4:unfilled placeholders) are *fingerprints* — near-proof the text was pasted from a
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:5:chat tool without cleanup — and are worth catching even when nothing else in the
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:6:text reads as AI. Others (curly quotes, a lone em dash) are weak signals that
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:7:only count in clusters.
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:8:
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:9:---
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:10:
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:11:### F1 — Em / en dashes
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:12:
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:13:- **Tell:** Overuse of em dashes (—) and en dashes (–), mimicking punchy
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:14:  sales/editorial rhythm. One of the most reliable single AI formatting tells.
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:15:  Catch spaced em dashes ( — ) and double-hyphen substitutes ( -- ) too.
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:16:- **Fix:** Replace, in rough order of preference: period (new sentence), comma
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:17:  (tight aside), colon (introducing an explanation), parentheses (true aside), or
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:18:  restructure. **Calibration:** a lone em dash means nothing — many editors use
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:19:  them. It's evidence only when paired with other tells, or above ~1 per 1,000
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:20:  words.
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:21:- **Sources:** blader (P13), aboudjem (§14), avoid-ai (em dashes), stop-slop.
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:22:
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:23:---
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:24:
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:25:### F2 — Bold overuse / erratic inline bolding
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:26:
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:27:- **Tell:** Two shapes. (a) Mechanical bold on every other phrase or term. (b)
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:28:  Patternless bold mid-paragraph — the model decided some words felt important
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:29:  with no consistent rule.
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:30:- **Fix:** Strip inline bold except glossary terms and UI labels. One bolded
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:31:  phrase per major section at most. If something deserves emphasis, sentence
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:32:  structure should provide it.
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:33:- **Sources:** blader (P14 + P42), aboudjem (§15), avoid-ai (bold overuse),
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:34:  anti-vibe (decorative bolding).
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:35:
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:36:---
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:37:
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:38:### F3 — Emoji / icon dressing in headers
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:39:
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:40:- **Tell:** Decorative emoji on headings or bullets: "🚀 Launch Phase," "💡 Key
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:41:  Insight," "✨ Key Features." Adds template feel, not energy.
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:42:- **Fix:** Remove. **Exception:** social posts may use one or two sparingly, at
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:43:  end of line, never mid-sentence.
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:44:- **Sources:** aboudjem (§18), avoid-ai (emoji in headers), anti-vibe (emoji /
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:45:  icon dressing).
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:46:
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:47:---
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:48:
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:49:### F4 — Curly quotes & typographic signatures
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:50:
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:51:- **Tell:** ChatGPT emits curly quotes (" " ' ') where the target context would
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:52:  use straight ones; consistent Oxford commas.
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:53:- **Fix:** Replace with straight quotes **only in plain-text / code contexts**
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:54:  (code comments, commit messages, plaintext drafts) where nothing auto-curls.
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:55:  **Calibration — weak signal:** Word, Google Docs, macOS, iOS all auto-curl, so
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:56:  most human prose has curly quotes. Never conclusive alone; don't flag curly
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:57:  apostrophes on their own. Leave them in finished publications and locale-correct
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:58:  punctuation (« », „ ").
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:59:- **Sources:** blader (P17), aboudjem (§19), avoid-ai (curly quotes).
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:60:
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:61:---
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:62:
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:63:### F5 — Title case in headings
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:64:
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:65:- **Tell:** Capitalizing all main words: "Strategic Negotiations And Global
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:66:  Partnerships."
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:67:- **Fix:** Sentence case for subheadings: "Strategic negotiations and global
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:68:  partnerships." Title case only for the piece's main title, if at all.
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:69:- **Sources:** blader (P16), aboudjem (§17), avoid-ai (title case headings).
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:70:
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:71:---
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:72:
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:73:### F6 — Markdown bleeding
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:74:
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:75:- **Tell:** Markdown syntax appearing where it won't render: `**bold**` in emails,
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:76:  social posts, or Word docs.
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:77:- **Fix:** Strip the markup for the target medium.
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:78:- **Sources:** blader (P28).
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:79:
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:80:---
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:81:
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:82:### F7 — Hashtag stuffing
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:83:
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:84:- **Tell:** Long trailing hashtag blocks (6+ on a short post) mixing a project
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:85:  tag with broad category tags (#AI #Crypto #Web3 #Innovation #FutureTech). Near-
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:86:  universal in LLM social content, rare in thoughtful human posts.
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:87:- **Fix:** 2-3 specific tags max, or none. If a tag wouldn't help a reader find
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:88:  related work, it's filler. (Threshold: 6+ is a hard flag; 5+ a soft tell on
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:89:  LinkedIn / investor profiles.)
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:90:- **Sources:** avoid-ai (hashtag stuffing).
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:91:
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:92:---
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:93:
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:94:### F8 — Unfilled placeholders
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:95:
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:96:- **Tell:** Bracketed slot-fillers shipped without replacement: `[Your Name]`,
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:97:  `[INSERT SOURCE URL]`, `[Describe the specific section]`, `2025-XX-XX`,
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:98:  `<!-- Add citation if available -->`. Near-definitive evidence of pasted
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:99:  boilerplate.
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:100:- **Fix:** Fill with real content or delete the sentence. Treat any visible
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:101:  placeholder as a publishing bug.
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:102:- **Sources:** blader (P33), avoid-ai (unfilled placeholders).
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:103:
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:104:---
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:105:
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:106:### F9 — Chatbot citation-markup leaks (fingerprint)
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:107:
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:108:- **Tell:** Internal citation tokens that survive copy-paste from chat UIs:
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:109:  `citeturn0search0`, `contentReference[oaicite:0]{index=0}`, `oai_citation`,
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:110:  `[attached_file:1]`, `grok_card`. Not a pattern — a fingerprint. Essentially
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:111:  proof the text was generated by a specific tool and pasted without cleanup.
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:112:- **Fix:** Strip every markup token. If a citation was meaningful, replace with a
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:113:  real reference. Don't humanize the markup — delete it. Worth catching even when
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:114:  nothing else reads as AI.
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:115:- **Sources:** blader (P34), avoid-ai (citation-markup leaks).
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:116:
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:117:---
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:118:
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:119:### F10 — AI-tool URL parameters (fingerprint)
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:120:
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:121:- **Tell:** Tracking params AI tools auto-append to generated URLs:
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:122:  `utm_source=chatgpt.com`, `utm_source=copilot.com`, `utm_source=openai`,
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:123:  `utm_source=claude.ai`, `utm_source=perplexity.ai`, `referrer=grok.com`. The
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:124:  parameter is the signature regardless of surrounding text.
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:125:- **Fix:** Strip the parameter from every URL; keep the URL if the link is
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:126:  meaningful.
skills/ai-writing-suite/_shared/patterns/punctuation-formatting.md:127:- **Sources:** blader (P35), avoid-ai (AI-tool URL parameters).
skills/ai-writing-suite/_shared/patterns/structural-tells.md:1:# Structural Tells (shape & flow)
skills/ai-writing-suite/_shared/patterns/structural-tells.md:2:
skills/ai-writing-suite/_shared/patterns/structural-tells.md:3:How the text is built, not which words it uses. Structure is the single hardest
skills/ai-writing-suite/_shared/patterns/structural-tells.md:4:tell to mask: detectors weight structural regularity above vocabulary, so fixing
skills/ai-writing-suite/_shared/patterns/structural-tells.md:5:every flagged word while leaving the shape untouched still reads as AI.
skills/ai-writing-suite/_shared/patterns/structural-tells.md:6:
skills/ai-writing-suite/_shared/patterns/structural-tells.md:7:---
skills/ai-writing-suite/_shared/patterns/structural-tells.md:8:
skills/ai-writing-suite/_shared/patterns/structural-tells.md:9:### T1 — Rule of three
skills/ai-writing-suite/_shared/patterns/structural-tells.md:10:
skills/ai-writing-suite/_shared/patterns/structural-tells.md:11:- **Tell:** Forcing ideas into groups of three to sound authoritative:
skills/ai-writing-suite/_shared/patterns/structural-tells.md:12:  "innovation, inspiration, and industry insights." Humans don't always think in
skills/ai-writing-suite/_shared/patterns/structural-tells.md:13:  triads.
skills/ai-writing-suite/_shared/patterns/structural-tells.md:14:- **Fix:** Use the natural number. Sometimes one, sometimes four. Two is
skills/ai-writing-suite/_shared/patterns/structural-tells.md:15:  underrated. Max one "adjective, adjective, and adjective" per piece.
skills/ai-writing-suite/_shared/patterns/structural-tells.md:16:- **Sources:** blader (P10), aboudjem (§10), avoid-ai, anti-vibe (三连排比).
skills/ai-writing-suite/_shared/patterns/structural-tells.md:17:
skills/ai-writing-suite/_shared/patterns/structural-tells.md:18:---
skills/ai-writing-suite/_shared/patterns/structural-tells.md:19:
skills/ai-writing-suite/_shared/patterns/structural-tells.md:20:### T2 — Negative parallelism / tailing negation
skills/ai-writing-suite/_shared/patterns/structural-tells.md:21:
skills/ai-writing-suite/_shared/patterns/structural-tells.md:22:- **Tell:** "Not only X but Y," "It's not just about X, it's Y," used as a
skills/ai-writing-suite/_shared/patterns/structural-tells.md:23:  reflex. Also clipped tailing negations tacked on: "no guessing," "no wasted
skills/ai-writing-suite/_shared/patterns/structural-tells.md:24:  motion." Once is fine; three times is a chatbot.
skills/ai-writing-suite/_shared/patterns/structural-tells.md:25:- **Fix:** State the point directly. Make the claim, drop the theatrical setup.
skills/ai-writing-suite/_shared/patterns/structural-tells.md:26:  One per piece at most.
skills/ai-writing-suite/_shared/patterns/structural-tells.md:27:- **Before:** This isn't about speed. It's about trust.
skills/ai-writing-suite/_shared/patterns/structural-tells.md:28:- **After:** This is about trust.
skills/ai-writing-suite/_shared/patterns/structural-tells.md:29:- **Sources:** blader (P9), aboudjem (§9), avoid-ai, anti-vibe, stop-slop.
skills/ai-writing-suite/_shared/patterns/structural-tells.md:30:
skills/ai-writing-suite/_shared/patterns/structural-tells.md:31:---
skills/ai-writing-suite/_shared/patterns/structural-tells.md:32:
skills/ai-writing-suite/_shared/patterns/structural-tells.md:33:### T3 — Formulaic challenges section
skills/ai-writing-suite/_shared/patterns/structural-tells.md:34:
skills/ai-writing-suite/_shared/patterns/structural-tells.md:35:- **Tell:** A "challenges" block generated from nothing: "Despite [good thing],
skills/ai-writing-suite/_shared/patterns/structural-tells.md:36:  [vague problems]. Despite these challenges, [optimistic platitude]." Also the
skills/ai-writing-suite/_shared/patterns/structural-tells.md:37:  stock headings: "Challenges and Legacy," "Future Outlook," "The road ahead."
skills/ai-writing-suite/_shared/patterns/structural-tells.md:38:- **Fix:** State specific problems with dates and data, or cut the section.
skills/ai-writing-suite/_shared/patterns/structural-tells.md:39:- **Before:** Despite its prosperity, faces challenges typical of urban areas.
skills/ai-writing-suite/_shared/patterns/structural-tells.md:40:  Despite these, continues to thrive.
skills/ai-writing-suite/_shared/patterns/structural-tells.md:41:- **After:** Traffic worsened after 2015 when three IT parks opened. A stormwater
skills/ai-writing-suite/_shared/patterns/structural-tells.md:42:  project started in 2022.
skills/ai-writing-suite/_shared/patterns/structural-tells.md:43:- **Sources:** blader (P6), aboudjem (§6), avoid-ai (formulaic challenges).
skills/ai-writing-suite/_shared/patterns/structural-tells.md:44:
skills/ai-writing-suite/_shared/patterns/structural-tells.md:45:---
skills/ai-writing-suite/_shared/patterns/structural-tells.md:46:
skills/ai-writing-suite/_shared/patterns/structural-tells.md:47:### T4 — False concession structure
skills/ai-writing-suite/_shared/patterns/structural-tells.md:48:
skills/ai-writing-suite/_shared/patterns/structural-tells.md:49:- **Tell:** "While X is impressive, Y remains a challenge," "Although X has made
skills/ai-writing-suite/_shared/patterns/structural-tells.md:50:  strides, Y is still an open question." Sounds balanced without weighing
skills/ai-writing-suite/_shared/patterns/structural-tells.md:51:  anything; both halves stay vague.
skills/ai-writing-suite/_shared/patterns/structural-tells.md:52:- **Fix:** Make the concession specific (name what's impressive, name the actual
skills/ai-writing-suite/_shared/patterns/structural-tells.md:53:  challenge) or pick a side and argue it.
skills/ai-writing-suite/_shared/patterns/structural-tells.md:54:- **Sources:** avoid-ai (false concession).
skills/ai-writing-suite/_shared/patterns/structural-tells.md:55:
skills/ai-writing-suite/_shared/patterns/structural-tells.md:56:---
skills/ai-writing-suite/_shared/patterns/structural-tells.md:57:
skills/ai-writing-suite/_shared/patterns/structural-tells.md:58:### T5 — Excessive / decorative structure
skills/ai-writing-suite/_shared/patterns/structural-tells.md:59:
skills/ai-writing-suite/_shared/patterns/structural-tells.md:60:- **Tell:** Visible structure standing in for clear thinking: a heading for every
skills/ai-writing-suite/_shared/patterns/structural-tells.md:61:  paragraph, more than 3 headings in under 300 words, 8+ bullets in under 200
skills/ai-writing-suite/_shared/patterns/structural-tells.md:62:  words, numbered frameworks that don't clarify a real sequence, summaries before
skills/ai-writing-suite/_shared/patterns/structural-tells.md:63:  the reader has seen the argument. Plus stock section modules that appear because
skills/ai-writing-suite/_shared/patterns/structural-tells.md:64:  the model likes the shape: Overview, Key Features, Benefits, Why It Matters, In
skills/ai-writing-suite/_shared/patterns/structural-tells.md:65:  Summary, Conclusion, FAQ with invented questions.
skills/ai-writing-suite/_shared/patterns/structural-tells.md:66:- **Fix:** Keep the headings and lists the reader will actually use. Collapse the
skills/ai-writing-suite/_shared/patterns/structural-tells.md:67:  rest into prose. Use headers that tell the reader something specific.
skills/ai-writing-suite/_shared/patterns/structural-tells.md:68:- **Sources:** avoid-ai (excessive structure), anti-vibe (over-structured
skills/ai-writing-suite/_shared/patterns/structural-tells.md:69:  outlines + stock modules), blader (P14/P15 partial), aboudjem (§16).
skills/ai-writing-suite/_shared/patterns/structural-tells.md:70:
skills/ai-writing-suite/_shared/patterns/structural-tells.md:71:---
skills/ai-writing-suite/_shared/patterns/structural-tells.md:72:
skills/ai-writing-suite/_shared/patterns/structural-tells.md:73:### T6 — Inline-header vertical lists
skills/ai-writing-suite/_shared/patterns/structural-tells.md:74:
skills/ai-writing-suite/_shared/patterns/structural-tells.md:75:- **Tell:** Bullets where each item starts with a bold header that repeats
skills/ai-writing-suite/_shared/patterns/structural-tells.md:76:  itself: "**Performance:** Performance improved by…," "**Security:** Security
skills/ai-writing-suite/_shared/patterns/structural-tells.md:77:  has been strengthened…"
skills/ai-writing-suite/_shared/patterns/structural-tells.md:78:- **Fix:** Strip the bold header and write the point directly, or convert the
skills/ai-writing-suite/_shared/patterns/structural-tells.md:79:  list to a prose paragraph.
skills/ai-writing-suite/_shared/patterns/structural-tells.md:80:- **Before:** - **User Experience:** The user experience has been improved with a
skills/ai-writing-suite/_shared/patterns/structural-tells.md:81:  new interface.
skills/ai-writing-suite/_shared/patterns/structural-tells.md:82:- **After:** The update improves the interface, speeds up load times, and adds
skills/ai-writing-suite/_shared/patterns/structural-tells.md:83:  end-to-end encryption.
skills/ai-writing-suite/_shared/patterns/structural-tells.md:84:- **Sources:** aboudjem (§16), blader (P15), avoid-ai (inline-header lists).
skills/ai-writing-suite/_shared/patterns/structural-tells.md:85:
skills/ai-writing-suite/_shared/patterns/structural-tells.md:86:---
skills/ai-writing-suite/_shared/patterns/structural-tells.md:87:
skills/ai-writing-suite/_shared/patterns/structural-tells.md:88:### T7 — Bullet lists of bare noun phrases
skills/ai-writing-suite/_shared/patterns/structural-tells.md:89:
skills/ai-writing-suite/_shared/patterns/structural-tells.md:90:- **Tell:** 5+ consecutive bullets, each a short (≤6-word) adjective+noun phrase
skills/ai-writing-suite/_shared/patterns/structural-tells.md:91:  with no verb and nothing checkable: "Stable mining efficiency / Reliable pool
skills/ai-writing-suite/_shared/patterns/structural-tells.md:92:  connectivity / Optimized RandomX performance." The tell is the *symmetry* —
skills/ai-writing-suite/_shared/patterns/structural-tells.md:93:  every item the same shape and length.
skills/ai-writing-suite/_shared/patterns/structural-tells.md:94:- **Fix:** Convert to prose, or rewrite items as full claims ("Failed shares
skills/ai-writing-suite/_shared/patterns/structural-tells.md:95:  stayed under 1% across a 12-hour run"). Does **not** apply to genuine list
skills/ai-writing-suite/_shared/patterns/structural-tells.md:96:  content (changelog, parameter docs, ingredients) where bare phrases are correct.
skills/ai-writing-suite/_shared/patterns/structural-tells.md:97:- **Sources:** avoid-ai (bullet-NP lists).
skills/ai-writing-suite/_shared/patterns/structural-tells.md:98:
skills/ai-writing-suite/_shared/patterns/structural-tells.md:99:---
skills/ai-writing-suite/_shared/patterns/structural-tells.md:100:
skills/ai-writing-suite/_shared/patterns/structural-tells.md:101:### T8 — Numbered-list inflation
skills/ai-writing-suite/_shared/patterns/structural-tells.md:102:
skills/ai-writing-suite/_shared/patterns/structural-tells.md:103:- **Tell:** "Three key takeaways," "Five things to know," "Here are the top
skills/ai-writing-suite/_shared/patterns/structural-tells.md:104:  seven." Numbered lists are structurally safe, so the model defaults to them even
skills/ai-writing-suite/_shared/patterns/structural-tells.md:105:  when the content isn't that many discrete parallel items.
skills/ai-writing-suite/_shared/patterns/structural-tells.md:106:- **Fix:** Use a numbered list only when the content genuinely has that many
skills/ai-writing-suite/_shared/patterns/structural-tells.md:107:  parallel items. If you're padding to hit a number, the list shouldn't exist.
skills/ai-writing-suite/_shared/patterns/structural-tells.md:108:- **Sources:** avoid-ai (numbered-list inflation).
skills/ai-writing-suite/_shared/patterns/structural-tells.md:109:
skills/ai-writing-suite/_shared/patterns/structural-tells.md:110:---
skills/ai-writing-suite/_shared/patterns/structural-tells.md:111:
skills/ai-writing-suite/_shared/patterns/structural-tells.md:112:### T9 — Paragraph-reshuffle immunity
skills/ai-writing-suite/_shared/patterns/structural-tells.md:113:
skills/ai-writing-suite/_shared/patterns/structural-tells.md:114:- **Tell:** The model writes parallel self-contained blocks instead of an
skills/ai-writing-suite/_shared/patterns/structural-tells.md:115:  unfolding argument. Test: can you swap paragraph 2 and paragraph 4 without
skills/ai-writing-suite/_shared/patterns/structural-tells.md:116:  breaking the piece? If yes, it's AI-shaped.
skills/ai-writing-suite/_shared/patterns/structural-tells.md:117:- **Fix:** Make paragraph N+1 depend on something concrete in paragraph N
skills/ai-writing-suite/_shared/patterns/structural-tells.md:118:  (references, callbacks, "this is why…"). If two paragraphs are interchangeable,
skills/ai-writing-suite/_shared/patterns/structural-tells.md:119:  merge or cut one. If they're all independent, the piece is missing a thesis.
skills/ai-writing-suite/_shared/patterns/structural-tells.md:120:- **Sources:** blader (P38), avoid-ai (paragraph-reshuffle immunity).
skills/ai-writing-suite/_shared/patterns/structural-tells.md:121:
skills/ai-writing-suite/_shared/patterns/structural-tells.md:122:---
skills/ai-writing-suite/_shared/patterns/structural-tells.md:123:
skills/ai-writing-suite/_shared/patterns/structural-tells.md:124:### T10 — Treadmill effect (low information density)
skills/ai-writing-suite/_shared/patterns/structural-tells.md:125:
skills/ai-writing-suite/_shared/patterns/structural-tells.md:126:- **Tell:** A 500-word section carrying 100 words of new information and 400 of
skills/ai-writing-suite/_shared/patterns/structural-tells.md:127:  restatement. Humans advance; AI circles. Inside-paragraph markers: "In other
skills/ai-writing-suite/_shared/patterns/structural-tells.md:128:  words," "Put simply," "Essentially," "That is to say."
skills/ai-writing-suite/_shared/patterns/structural-tells.md:129:- **Fix:** For each sentence, ask "what's actually new here?" Delete anything that
skills/ai-writing-suite/_shared/patterns/structural-tells.md:130:  only rephrases what came before. A paragraph that loses 40-60% of its words and
skills/ai-writing-suite/_shared/patterns/structural-tells.md:131:  reads better is the right outcome.
skills/ai-writing-suite/_shared/patterns/structural-tells.md:132:- **Sources:** blader (P43), avoid-ai (treadmill effect).
skills/ai-writing-suite/_shared/patterns/structural-tells.md:133:
skills/ai-writing-suite/_shared/patterns/structural-tells.md:134:---
skills/ai-writing-suite/_shared/patterns/structural-tells.md:135:
skills/ai-writing-suite/_shared/patterns/structural-tells.md:136:### T11 — Fragmented headers
skills/ai-writing-suite/_shared/patterns/structural-tells.md:137:
skills/ai-writing-suite/_shared/patterns/structural-tells.md:138:- **Tell:** A heading followed by a one-line paragraph that just restates the
skills/ai-writing-suite/_shared/patterns/structural-tells.md:139:  heading before the real content starts. ("## Performance" → "Speed matters.")
skills/ai-writing-suite/_shared/patterns/structural-tells.md:140:- **Fix:** Cut the warm-up line; let the real content follow the heading.
skills/ai-writing-suite/_shared/patterns/structural-tells.md:141:- **Sources:** aboudjem (§29).
skills/ai-writing-suite/_shared/patterns/structural-tells.md:142:
skills/ai-writing-suite/_shared/patterns/structural-tells.md:143:---
skills/ai-writing-suite/_shared/patterns/structural-tells.md:144:
skills/ai-writing-suite/_shared/patterns/structural-tells.md:145:### T12 — Diff-anchored writing
skills/ai-writing-suite/_shared/patterns/structural-tells.md:146:
skills/ai-writing-suite/_shared/patterns/structural-tells.md:147:- **Tell:** Documentation written as if narrating a change rather than describing
skills/ai-writing-suite/_shared/patterns/structural-tells.md:148:  the thing as it is: "This function was added to replace the previous approach…,"
skills/ai-writing-suite/_shared/patterns/structural-tells.md:149:  "We've now updated the API to also support streaming." (Fine for changelogs and
skills/ai-writing-suite/_shared/patterns/structural-tells.md:150:  migration guides — those are inherently version-scoped.)
skills/ai-writing-suite/_shared/patterns/structural-tells.md:151:- **Fix:** Describe the current state. "The API supports streaming." Unless the
skills/ai-writing-suite/_shared/patterns/structural-tells.md:152:  change itself is the point.
skills/ai-writing-suite/_shared/patterns/structural-tells.md:153:- **Sources:** aboudjem (§30), anti-vibe (diff-anchored writing).
skills/ai-writing-suite/_shared/patterns/00-index.md:1:# AI-Tell Pattern Catalog — Index
skills/ai-writing-suite/_shared/patterns/00-index.md:2:
skills/ai-writing-suite/_shared/patterns/00-index.md:3:This is the consolidated, deduplicated catalog of AI-writing "tells" that
skills/ai-writing-suite/_shared/patterns/00-index.md:4:`comms-polish` draws on. It merges seven source catalogs into one set of
skills/ai-writing-suite/_shared/patterns/00-index.md:5:patterns organized by category, with each pattern carrying a source tag so
skills/ai-writing-suite/_shared/patterns/00-index.md:6:`NOTICE.md` attribution stays accurate later.
skills/ai-writing-suite/_shared/patterns/00-index.md:7:
skills/ai-writing-suite/_shared/patterns/00-index.md:8:## Why this catalog exists
skills/ai-writing-suite/_shared/patterns/00-index.md:9:
skills/ai-writing-suite/_shared/patterns/00-index.md:10:Every source repo repeated most of the same tells in slightly different words.
skills/ai-writing-suite/_shared/patterns/00-index.md:11:Carrying seven overlapping lists would mean seven places to update and seven
skills/ai-writing-suite/_shared/patterns/00-index.md:12:chances to disagree with ourselves. One deduped catalog is the single source of
skills/ai-writing-suite/_shared/patterns/00-index.md:13:truth: `comms-polish` reads these files; the eventual programmatic detector
skills/ai-writing-suite/_shared/patterns/00-index.md:14:(Layer 3) and `NOTICE.md` attribution both key off the same `id` + `sources`
skills/ai-writing-suite/_shared/patterns/00-index.md:15:fields here.
skills/ai-writing-suite/_shared/patterns/00-index.md:16:
skills/ai-writing-suite/_shared/patterns/00-index.md:17:## How to read a pattern entry
skills/ai-writing-suite/_shared/patterns/00-index.md:18:
skills/ai-writing-suite/_shared/patterns/00-index.md:19:Each pattern uses this shape:
skills/ai-writing-suite/_shared/patterns/00-index.md:20:
skills/ai-writing-suite/_shared/patterns/00-index.md:21:```
skills/ai-writing-suite/_shared/patterns/00-index.md:22:### <id> — <name>
skills/ai-writing-suite/_shared/patterns/00-index.md:23:- **Tell:** what the model does and why it reads as AI.
skills/ai-writing-suite/_shared/patterns/00-index.md:24:- **Fix:** the editing move that removes it.
skills/ai-writing-suite/_shared/patterns/00-index.md:25:- **Before / After:** a short concrete example (only where it earns its keep).
skills/ai-writing-suite/_shared/patterns/00-index.md:26:- **Sources:** which source catalogs this pattern came from (for attribution).
skills/ai-writing-suite/_shared/patterns/00-index.md:27:```
skills/ai-writing-suite/_shared/patterns/00-index.md:28:
skills/ai-writing-suite/_shared/patterns/00-index.md:29:`id`s are stable. They are *not* the same as any single source's numbering
skills/ai-writing-suite/_shared/patterns/00-index.md:30:(blader P1-P43, aboudjem 1-30, avoid-ai categories) because those numbering
skills/ai-writing-suite/_shared/patterns/00-index.md:31:schemes overlap and conflict. Where a source had its own id, it is listed in
skills/ai-writing-suite/_shared/patterns/00-index.md:32:`Sources` so the lineage is traceable.
skills/ai-writing-suite/_shared/patterns/00-index.md:33:
skills/ai-writing-suite/_shared/patterns/00-index.md:34:## Categories
skills/ai-writing-suite/_shared/patterns/00-index.md:35:
skills/ai-writing-suite/_shared/patterns/00-index.md:36:| File | Category | What it covers |
skills/ai-writing-suite/_shared/patterns/00-index.md:37:| --- | --- | --- |
skills/ai-writing-suite/_shared/patterns/00-index.md:38:| `lexical-tells.md` | Word-level tells | AI vocabulary, copula avoidance, synonym cycling, false ranges, hyphen-pair overuse |
skills/ai-writing-suite/_shared/patterns/00-index.md:39:| `significance-attribution.md` | Inflation & sourcing | Significance/novelty inflation, vague attribution, promotional language, name-dropping, superficial -ing, speculative gap-filling |
skills/ai-writing-suite/_shared/patterns/00-index.md:40:| `structural-tells.md` | Structure & shape | Rule of three, negative parallelism, formulaic challenges, over-structure, inline-header lists, reshuffle immunity, treadmill effect, false concession |
skills/ai-writing-suite/_shared/patterns/00-index.md:41:| `hedging-filler.md` | Hedging & filler | Filler phrases, excessive/stacked hedging, generic conclusions, future-narrative closers, confidence-calibration phrases, signposting, "let's" openers |
skills/ai-writing-suite/_shared/patterns/00-index.md:42:| `punctuation-formatting.md` | Punctuation & formatting | Em/en dashes, bold overuse, emoji headers, curly quotes, title case, hashtag stuffing, placeholders, citation-markup leaks, UTM params |
skills/ai-writing-suite/_shared/patterns/00-index.md:43:| `communication-artifacts.md` | Chat artifacts | Chatbot tics, sycophancy, acknowledgment loops, cutoff disclaimers, collaborative-framing leaks, reasoning-chain leaks, engagement hooks, emotional flatline |
skills/ai-writing-suite/_shared/patterns/00-index.md:44:| `rhythm-stylometric.md` | Rhythm & stylometry | Sentence/paragraph uniformity (burstiness), low vocabulary diversity (TTR), perplexity, register shift |
skills/ai-writing-suite/_shared/patterns/00-index.md:45:
skills/ai-writing-suite/_shared/patterns/00-index.md:46:## Source legend (for `Sources` tags)
skills/ai-writing-suite/_shared/patterns/00-index.md:47:
skills/ai-writing-suite/_shared/patterns/00-index.md:48:| Tag | Source repo / skill | License |
skills/ai-writing-suite/_shared/patterns/00-index.md:49:| --- | --- | --- |
skills/ai-writing-suite/_shared/patterns/00-index.md:50:| `blader` | `blader/humanizer` (43-pattern catalog, P1-P43) | MIT |
skills/ai-writing-suite/_shared/patterns/00-index.md:51:| `aboudjem` | `Aboudjem/humanizer-skill` (Wikipedia "Signs of AI writing", 30 patterns) | MIT |
skills/ai-writing-suite/_shared/patterns/00-index.md:52:| `stop-slop` | `stop-slop` by Hardik Pandya (8 core rules + scoring rubric) | MIT |
skills/ai-writing-suite/_shared/patterns/00-index.md:53:| `avoid-ai` | `conorbronsdon/avoid-ai-writing` (tiered vocab + CATEGORIES taxonomy) | MIT |
skills/ai-writing-suite/_shared/patterns/00-index.md:54:| `anti-vibe` | `weijt606/anti-vibe-writing` (bilingual patterns, consultant-speak) | MIT |
skills/ai-writing-suite/_shared/patterns/00-index.md:55:| `ai-vibe` | `donghuixin/AI-Vibe-Writing-Skills` (style-extractor / reviewer prompts) | MIT |
skills/ai-writing-suite/_shared/patterns/00-index.md:56:| `nature` | `Yuan1z0825/nature-skills` (`nature-writing` + `nature-polishing`) | MIT |
skills/ai-writing-suite/_shared/patterns/00-index.md:57:
skills/ai-writing-suite/_shared/patterns/00-index.md:58:> The corrupted `blader` reference (P31-P43 had duplicated/run-together "Fix /
skills/ai-writing-suite/_shared/patterns/00-index.md:59:> What's happening / Triggers / Source" blocks collapsed onto single lines) was
skills/ai-writing-suite/_shared/patterns/00-index.md:60:> **re-derived from intent**, not copied. Each affected pattern was reduced back
skills/ai-writing-suite/_shared/patterns/00-index.md:61:> to one clean Tell / Fix / example. See `notes/` if a lineage question comes up.
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:1:# Hedging & Filler Tells
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:2:
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:3:The model adds words that add no meaning, and qualifies claims until they assert
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:4:nothing. These slow the writing down and give it a tutorial-script, committee-
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:5:written feel.
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:6:
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:7:---
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:8:
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:9:### H1 — Filler phrases
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:10:
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:11:- **Tell:** Mechanical padding that adds words without meaning: "It is important
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:12:  to note that," "In order to," "Due to the fact that," "At this point in time,"
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:13:  "In the event that," "The system has the ability to," "In terms of," "The
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:14:  reality is that."
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:15:- **Fix:** Cut to the point. "It is important to note that the data shows" → "The
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:16:  data shows." "In order to" → "To." "Due to the fact that" → "Because."
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:17:- **Sources:** aboudjem (§23), avoid-ai (filler phrases), anti-vibe, stop-slop.
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:18:
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:19:---
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:20:
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:21:### H2 — Excessive / stacked hedging
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:22:
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:23:- **Tell:** Over-qualifying: "could potentially possibly," "it might perhaps be
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:24:  argued." And hedge-stacked predictions where a modal piles on a hedge adverb:
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:25:  "could potentially create," "may eventually unlock," "might ultimately
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:26:  transform." Each hedge cancels the next, leaving a cautious-sounding sentence
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:27:  that asserts nothing.
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:28:- **Fix:** Pick one. "could create" or "potentially creates," not both. Keep
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:29:  nuance where it matters; remove it where it only weakens the sentence.
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:30:- **Sources:** aboudjem (§24), avoid-ai (hedge-stacked predictions), anti-vibe
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:31:  (over-balanced tone), stop-slop.
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:32:
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:33:---
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:34:
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:35:### H3 — Generic positive conclusions
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:36:
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:37:- **Tell:** Vague upbeat endings: "The future looks bright," "Exciting times lie
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:38:  ahead," "continues its journey toward excellence," "a step in the right
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:39:  direction," "As we move forward," "Only time will tell."
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:40:- **Fix:** Cut them. If the piece needs a closing thought, make it specific to the
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:41:  argument. "The company plans to open two more locations next year."
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:42:- **Sources:** blader (P24), aboudjem (§25), avoid-ai (generic conclusions),
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:43:  anti-vibe.
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:44:
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:45:---
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:46:
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:47:### H4 — Generic future-narrative closers
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:48:
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:49:- **Tell:** A closer that's grammatically a prediction but contains no testable
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:50:  content: modal (may / could / will / is poised to) + "become" + "one of the
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:51:  most [adjective]" + (narrative / story / trend / chapter / movement). "May
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:52:  become one of the most important narratives of the next market cycle."
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:53:- **Fix:** Pick the falsifiable version. "DePIN compute may exceed AWS spot
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:54:  pricing for parallel workloads by 2027" is a prediction; the original is not.
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:55:- **Sources:** avoid-ai (future-narrative closers).
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:56:
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:57:---
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:58:
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:59:### H5 — Confidence-calibration phrases
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:60:
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:61:- **Tell:** Telling the reader how to feel about a fact instead of letting it
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:62:  speak: "It's worth noting that," "Interestingly," "Surprisingly," "Notably,"
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:63:  "Importantly," "Certainly," "Undoubtedly." Plus persuasive-authority tropes
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:64:  that announce depth: "the real question is," "at its core," "fundamentally,"
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:65:  "make no mistake," "the truth is."
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:66:- **Fix:** Cut the cue and lead with the substance. One "notably" in 2,000 words
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:67:  is fine; three in 500 is emphasis-stacking — flag by density.
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:68:- **Sources:** avoid-ai (confidence calibration), blader (P27 persuasive
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:69:  authority), anti-vibe.
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:70:
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:71:---
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:72:
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:73:### H6 — Self-labeling significance
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:74:
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:75:- **Tell:** After a list, pointing back at one item to label it
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:76:  clever/contrarian/surprising/key: "That last move is the contrarian one," "This
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:77:  is the interesting part," "Here's where it gets clever." The label does the work
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:78:  the content should have done.
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:79:- **Fix:** Cut the labeling sentence and let the explanation do the work, or
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:80:  restructure so the highlighted item carries weight on its own.
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:81:- **Sources:** avoid-ai (self-labeling significance).
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:82:
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:83:---
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:84:
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:85:### H7 — Signposting / announcements
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:86:
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:87:- **Tell:** Announcing what the text is about to do instead of doing it: "Let's
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:88:  dive in," "Let's explore," "Here's what you need to know," "Now let's look at,"
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:89:  "Without further ado," "But first."
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:90:- **Fix:** Say the thing. The reader doesn't need a tour guide.
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:91:- **Before:** Let's dive into how caching works in Next.js. Here's what you need
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:92:  to know.
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:93:- **After:** Next.js caches data at several layers: request memoization, the data
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:94:  cache, and the router cache.
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:95:- **Sources:** aboudjem (§28), avoid-ai (chatbot artifacts / "let's"
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:96:  constructions), anti-vibe (signposting), stop-slop (meta-joiners).
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:97:
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:98:---
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:99:
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:100:### H8 — "Let's" false-collaborative openers
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:101:
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:102:- **Tell:** "Let's + verb" used as a transition rather than a genuine invitation:
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:103:  "Let's take a look," "Let's break this down," "Let's examine." A false-
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:104:  collaborative ease-in that delays the point.
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:105:- **Fix:** Start with the point. (Related to H7 but broader than "let's dive in.")
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:106:- **Sources:** avoid-ai ("let's" constructions).
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:107:
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:108:---
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:109:
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:110:### H9 — Vague endorsement ("worth [verb]ing")
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:111:
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:112:- **Tell:** A generic thumbs-up substituting for a specific reason: "worth
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:113:  reading," "worth paying attention to," "worth a look," "worth your time."
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:114:- **Fix:** Say *why* it matters instead.
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:115:- **Sources:** avoid-ai (vague endorsement).
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:116:
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:117:---
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:118:
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:119:### H10 — Vague abstraction
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:120:
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:121:- **Tell:** Abstract wording where a concrete fact belongs: "improve
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:122:  collaboration across stakeholders," "enhance strategic alignment," "deliver
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:123:  meaningful outcomes."
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:124:- **Fix:** Replace with what actually happened, exists, or should be done. "Reduce
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:125:  setup time from thirty minutes to five." "Make the tradeoff explicit before
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:126:  implementation starts."
skills/ai-writing-suite/_shared/patterns/hedging-filler.md:127:- **Sources:** anti-vibe (vague abstraction), avoid-ai, stop-slop (be specific).
skills/ai-writing-suite/LICENSE:1:MIT License
skills/ai-writing-suite/LICENSE:2:
skills/ai-writing-suite/LICENSE:3:Copyright (c) 2026 AI Writing Humanizer contributors
skills/ai-writing-suite/LICENSE:4:
skills/ai-writing-suite/LICENSE:5:Permission is hereby granted, free of charge, to any person obtaining a copy
skills/ai-writing-suite/LICENSE:6:of this software and associated documentation files (the "Software"), to deal
skills/ai-writing-suite/LICENSE:7:in the Software without restriction, including without limitation the rights
skills/ai-writing-suite/LICENSE:8:to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
skills/ai-writing-suite/LICENSE:9:copies of the Software, and to permit persons to whom the Software is
skills/ai-writing-suite/LICENSE:10:furnished to do so, subject to the following conditions:
skills/ai-writing-suite/LICENSE:11:
skills/ai-writing-suite/LICENSE:12:The above copyright notice and this permission notice shall be included in all
skills/ai-writing-suite/LICENSE:13:copies or substantial portions of the Software.
skills/ai-writing-suite/LICENSE:14:
skills/ai-writing-suite/LICENSE:15:THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
skills/ai-writing-suite/LICENSE:16:IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
skills/ai-writing-suite/LICENSE:17:FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
skills/ai-writing-suite/LICENSE:18:AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
skills/ai-writing-suite/LICENSE:19:LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
skills/ai-writing-suite/LICENSE:20:OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
skills/ai-writing-suite/LICENSE:21:SOFTWARE.
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:1:# KB Smoke Test — one end-to-end ingestion + retrieval chain
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:2:
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:3:> **Why this file exists (design decision D12).** The whole product promise is
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:4:> "the company just drops in a Confluence page — they add data, not build a
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:5:> retrieval engine." That promise is hollow unless we prove ONE complete chain
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:6:> works end-to-end on the generic KB: a raw page comes in → it gets indexed →
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:7:> a natural-language query resolves to the correct entry and passage.
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:8:>
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:9:> This doc establishes and documents that chain as a **repeatable test**. The
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:10:> Layer 3 eval will automate it (query in → assert the agent retrieves the
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:11:> expected entry + passage). For now it is the manual, reproducible proof.
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:12:
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:13:---
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:14:
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:15:## The chain, in three steps
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:16:
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:17:```
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:18:[1] INGESTION                [2] INDEX UPDATE              [3] RETRIEVAL
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:19:raw markdown page    ──▶      add 1 row to INDEX.md   ──▶  NL query → INDEX scan
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:20:("Confluence-style")         (file + summary + keywords)   → open entry → quote passage
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:21:```
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:22:
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:23:No embeddings, no vectors, no MCP. Every step is a file read/write an agent (or a
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:24:human) can do on any surface (D5).
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:25:
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:26:---
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:27:
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:28:## Step 1 — Sample incoming page (the "Confluence-style" drop-in)
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:29:
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:30:This is what a company contributor would paste in — a normal markdown page. For
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:31:the generic KB we already shipped five such entries; `clarity.md` is the one this
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:32:test traces. Its load-bearing passage is:
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:33:
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:34:> **One idea per sentence.** If you find an "and" joining two full claims, make
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:35:> two sentences.
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:36:
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:37:(That passage is the expected retrieval target in Step 3.)
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:38:
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:39:## Step 2 — Ingestion = add one row to `INDEX.md`
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:40:
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:41:Indexing a page is a single edit: append a row to the **Entries** table in
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:42:`INDEX.md` with three fields.
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:43:
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:44:- **Entry file:** `clarity.md`
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:45:- **Summary (one line):** Say one idea per sentence in plain, concrete words; cut filler.
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:46:- **Keywords / aliases:** clarity, clear, concise, plain language, wordy, verbose,
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:47:  filler, jargon, simplify, hard to read, confusing, cut words, concrete, vague
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:48:
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:49:That row IS the ingestion. No build step, no re-index job. (This is exactly what
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:50:a company fork does with its Confluence page — see `README.md`.)
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:51:
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:52:## Step 3 — Retrieval = scan INDEX, open entry, quote passage
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:53:
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:54:Follow the retrieval protocol at the top of `INDEX.md`.
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:55:
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:56:---
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:57:
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:58:## TEST CASE (run this to verify the chain)
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:59:
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:60:**Query (natural language):**
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:61:> "My sentences are too long and try to say too much at once — how do I fix that?"
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:62:
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:63:**Expected entry retrieved:** `clarity.md`
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:64:
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:65:- *Why:* the query terms "too long," "say too much at once," and "fix" overlap
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:66:  the `clarity.md` keywords (`wordy`, `verbose`, `one idea`, `cut words`) and its
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:67:  Summary ("Say one idea per sentence... cut filler"). No other entry's keyword
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:68:  set matches "one sentence saying too much" — `structure.md` is about
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:69:  document/paragraph order, not within-sentence overload.
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:70:
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:71:**Expected passage quoted:**
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:72:> **One idea per sentence.** If you find an "and" joining two full claims, make
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:73:> two sentences.
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:74:
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:75:(plus, acceptable to also surface the Before/After in `clarity.md`:
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:76:"It is worth noting that... → The team cut three slow queries.")
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:77:
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:78:**Pass condition:** the agent returns `clarity.md` as the entry AND quotes the
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:79:"One idea per sentence" Move (or the clarity Before/After). Returning a different
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:80:entry, or inventing advice not in the file, is a FAIL.
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:81:
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:82:---
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:83:
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:84:## A second case (negative / disambiguation check)
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:85:
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:86:**Query:**
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:87:> "Who am I even writing this for? It feels like it's aimed at no one."
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:88:
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:89:**Expected entry:** `audience.md`
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:90:**Expected passage:**
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:91:> State the reader and their job before drafting. "An on-call engineer who needs
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:92:> to decide whether to roll back." That sentence fixes tone, length, and jargon level.
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:93:
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:94:**Why it must NOT return `tone.md`:** the word "feels" and "aimed" can lure a
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:95:match to tone, but the intent — *no identified reader* — maps to `audience.md`.
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:96:This case exists to confirm the index discriminates between near-neighbors.
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:97:
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:98:---
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:99:
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:100:## A third case (genuine near-neighbor — both entries score > 0)
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:101:
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:102:Case 2 above discriminates on a single token ("who"), so the tie-break is never
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:103:truly exercised (review finding m1). This case fixes that: the query hits BOTH
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:104:`audience.md` and `tone.md` on keywords, and `audience.md` must win on total overlap.
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:105:
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:106:**Query:**
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:107:> "Who is the reader for this? It sounds too technical and a bit corporate."
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:108:
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:109:**Expected entry:** `audience.md`
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:110:**Expected passage:**
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:111:> State the reader and their job before drafting. "An on-call engineer who needs
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:112:> to decide whether to roll back." That sentence fixes tone, length, and jargon level.
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:113:
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:114:**Why this is the real disambiguation test:** `tone.md` genuinely scores here —
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:115:"sounds" and "corporate" are tone keywords (overlap 2) — but `audience.md` wins on
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:116:total term overlap ("who" + "reader" + "technical" = 3). Unlike Case 2 there is a
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:117:competing signal to beat, so a PASS proves the keyword/intent tie-break actually works.
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:118:
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:119:## How Layer 3 will automate this
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:120:
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:121:The eval harness reads each TEST CASE block, sends the **Query** to the agent
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:122:under the retrieval protocol, and asserts: (a) the returned entry filename equals
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:123:**Expected entry**, and (b) the quoted text contains the **Expected passage**.
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:124:Calibrate by adding harder near-neighbor queries until the baseline misses
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:125:~30-40% (per the project eval-calibration rule), then tighten the index keywords
skills/ai-writing-suite/_shared/knowledge/SMOKE-TEST.md:126:to recover recall. Until Layer 3, run these two cases by hand after any KB edit.
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:1:# Communication Artifacts (chat-interface leaks)
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:2:
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:3:Tics from the chat interface that leak into published prose. The text was
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:4:generated as correspondence *to the user*, not as content, and got pasted without
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:5:removing the conversational framing. Most of these are credibility killers — fix
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:6:immediately.
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:7:
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:8:---
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:9:
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:10:### C1 — Chatbot artifacts
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:11:
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:12:- **Tell:** Conversational tics from the chat UI: "I hope this helps," "Of
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:13:  course!," "Certainly!," "Feel free to reach out," "Let me know if you need
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:14:  anything else," "Here is a…," "Would you like me to…"
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:15:- **Fix:** Remove entirely. Start with the actual content.
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:16:- **Sources:** blader (P19), aboudjem (§20), avoid-ai (chatbot artifacts).
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:17:
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:18:---
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:19:
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:20:### C2 — Collaborative-framing leaks
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:21:
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:22:- **Tell:** Instructional framing meant for the user leaking into published
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:23:  output: "In this article, we will explore," "Let me walk you through," "Here's
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:24:  what you need to know," instructions to the reader about what they should do.
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:25:  Distinct from C1 (identity disclosure) — this is the tutorial-script framing.
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:26:- **Fix:** Delete the meta-commentary; start with the content.
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:27:- **Before:** In this article, we will explore the characteristics that make this
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:28:  framework worth using.
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:29:- **After:** This framework solves three problems React Router doesn't.
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:30:- **Sources:** blader (P32), aboudjem (§20), avoid-ai (chatbot meta-narration).
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:31:
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:32:---
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:33:
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:34:### C3 — Sycophantic tone
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:35:
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:36:- **Tell:** Conversational rewards validating the reader: "Great question!,"
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:37:  "Excellent point!," "You're absolutely right!," "That's a really insightful
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:38:  observation."
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:39:- **Fix:** Remove. Distinct from C1: sycophancy specifically flatters the
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:40:  questioner rather than performing helpfulness.
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:41:- **Sources:** blader (P21), aboudjem (§22), avoid-ai (sycophantic tone),
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:42:  stop-slop.
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:43:
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:44:---
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:45:
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:46:### C4 — Acknowledgment loops
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:47:
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:48:- **Tell:** Restating the prompt before answering: "You're asking about," "To
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:49:  answer your question," "The question of whether…," "That's a great question. The
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:50:  …" Also opening a section by summarizing the previous one.
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:51:- **Fix:** Just answer. The reader knows what they asked.
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:52:- **Sources:** avoid-ai (acknowledgment loops).
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:53:
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:54:---
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:55:
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:56:### C5 — Cutoff disclaimers
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:57:
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:58:- **Tell:** Model limitations leaking into prose: "As of my last update," "Up to
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:59:  my last training update," "While specific details are limited based on available
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:60:  information," "I don't have access to real-time data."
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:61:- **Fix:** Find the information or remove the hedge. Never publish a sentence that
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:62:  admits the writer didn't look something up. (Distinct from S8 speculative
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:63:  gap-filling, which *hides* the gap; this one admits it.)
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:64:- **Sources:** blader (P20), aboudjem (§21 first half), avoid-ai (cutoff
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:65:  disclaimers).
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:66:
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:67:---
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:68:
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:69:### C6 — Reasoning-chain artifacts
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:70:
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:71:- **Tell:** Chain-of-thought scaffolding leaking into published prose: "Let me
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:72:  think step by step," "Breaking this down," "To approach this systematically,"
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:73:  "Step 1:," "First, let's consider," "Working through this logically." Plus
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:74:  numbered reasoning steps that read like internal monologue.
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:75:- **Fix:** The reader doesn't need the scaffolding. State the conclusion, then the
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:76:  evidence.
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:77:- **Sources:** avoid-ai (reasoning-chain artifacts).
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:78:
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:79:---
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:80:
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:81:### C7 — Infomercial engagement hooks
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:82:
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:83:- **Tell:** Punchy fragment-hooks teeing up a reveal: "The catch?," "The
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:84:  kicker?," "Here's the thing.," "But here's the kicker:," "The best part?,"
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:85:  "Plot twist:," "Sound familiar?" Fake momentum and manufactured suspense around
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:86:  ordinary information.
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:87:- **Fix:** Delete the hook; state the thing. "The catch? It only works on
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:88:  weekends." → "It only works on weekends." If you want a rhythm break, use a
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:89:  short declarative fragment, not a question.
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:90:- **Sources:** blader (P41), avoid-ai (infomercial engagement hooks).
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:91:
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:92:---
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:93:
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:94:### C8 — Rhetorical-question openers
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:95:
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:96:- **Tell:** Rhetorical questions used to stall before the point, dropped as
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:97:  section transitions: "But what does this mean for developers?," "So why should
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:98:  you care?," "What's next?" Also FAQ-style question headings: "What makes X
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:99:  unique?," "Why is Y important?"
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:100:- **Fix:** If you know the answer, say it. Rhetorical questions are earned by
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:101:  strong setup, not used as transitions.
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:102:- **Sources:** avoid-ai (rhetorical-question openers), blader (P27 question
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:103:  titles).
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:104:
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:105:---
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:106:
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:107:### C9 — Emotional flatline
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:108:
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:109:- **Tell:** Claiming an emotion as a structural crutch without conveying it:
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:110:  "What surprised me most," "I was fascinated to discover," "What struck me was,"
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:111:  "The most interesting part," and the bare header form "Interesting thing here:."
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:112:  Tell-don't-show, and massively overused as list intros. Also "hit differently"
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:113:  / "hits different" as a shortcut to sound relatable.
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:114:- **Fix:** If you claim an emotion, the writing around it should earn it.
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:115:  Otherwise cut the claim and present the thing directly. (Also a sign of lazy
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:116:  human writing — flag it either way.)
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:117:- **Sources:** avoid-ai (emotional flatline).
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:118:
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:119:---
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:120:
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:121:### C10 — Parenthetical hedging
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:122:
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:123:- **Tell:** Parenthetical asides that sound nuanced without committing: "(and,
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:124:  increasingly, Z)," "(or, more precisely, Y)," "(and perhaps more importantly,
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:125:  W)."
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:126:- **Fix:** If the aside matters, give it its own sentence. If it doesn't, cut it.
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:127:- **Sources:** avoid-ai (parenthetical hedging).
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:128:
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:129:---
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:130:
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:131:### C11 — Register / style shift (mixed authorship)
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:132:
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:133:- **Tell:** A sudden change in voice, register, or error profile mid-document —
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:134:  one paragraph of perfect formal English next to casual text with errors;
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:135:  graduate-thesis prose in the middle of casual notes. Catches mixed human+AI
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:136:  authorship.
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:137:- **Fix:** Maintain a consistent register throughout. Rewrite the AI-generated
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:138:  sections to match the author's natural voice.
skills/ai-writing-suite/_shared/patterns/communication-artifacts.md:139:- **Sources:** blader (P36).
skills/ai-writing-suite/_shared/voice-profile.md:1:<!--
skills/ai-writing-suite/_shared/voice-profile.md:2:================================================================================
skills/ai-writing-suite/_shared/voice-profile.md:3:  voice-profile.md  —  CANONICAL VOICE PROFILE (CONTRACT FILE)
skills/ai-writing-suite/_shared/voice-profile.md:4:================================================================================
skills/ai-writing-suite/_shared/voice-profile.md:5:
skills/ai-writing-suite/_shared/voice-profile.md:6:  WHAT THIS IS
skills/ai-writing-suite/_shared/voice-profile.md:7:  ------------
skills/ai-writing-suite/_shared/voice-profile.md:8:  This is a SAMPLE/EXAMPLE voice profile. It is shipped filled-in so you can see
skills/ai-writing-suite/_shared/voice-profile.md:9:  the shape, but it is meant to be OVERWRITTEN per user. `voice-onboard` produces
skills/ai-writing-suite/_shared/voice-profile.md:10:  the real one by interviewing you + reading your writing samples.
skills/ai-writing-suite/_shared/voice-profile.md:11:
skills/ai-writing-suite/_shared/voice-profile.md:12:  WHY IT EXISTS (the contract)
skills/ai-writing-suite/_shared/voice-profile.md:13:  ----------------------------
skills/ai-writing-suite/_shared/voice-profile.md:14:  Think of this file as a SHARED SCHEMA between two skills, the way a feature
skills/ai-writing-suite/_shared/voice-profile.md:15:  table is a contract between the pipeline that writes it and the model that
skills/ai-writing-suite/_shared/voice-profile.md:16:  reads it:
skills/ai-writing-suite/_shared/voice-profile.md:17:    - WRITER:  `voice-onboard`  fills this in from your samples.
skills/ai-writing-suite/_shared/voice-profile.md:18:    - READER:  `comms-polish`   reads it every run to match YOUR voice instead
skills/ai-writing-suite/_shared/voice-profile.md:19:               of imposing a generic "clean" register.
skills/ai-writing-suite/_shared/voice-profile.md:20:
skills/ai-writing-suite/_shared/voice-profile.md:21:  Because both sides depend on it, the FIELD NAMES below are stable. Treat the
skills/ai-writing-suite/_shared/voice-profile.md:22:  `## H2 headers` as the column names of the contract. Add evidence and detail
skills/ai-writing-suite/_shared/voice-profile.md:23:  under them freely, but do not rename or drop the headers, or `comms-polish`
skills/ai-writing-suite/_shared/voice-profile.md:24:  will silently fall back to generic behavior (a silent-fallback bug we want to
skills/ai-writing-suite/_shared/voice-profile.md:25:  avoid).
skills/ai-writing-suite/_shared/voice-profile.md:26:
skills/ai-writing-suite/_shared/voice-profile.md:27:  EVERY claim needs sample evidence. No evidence -> leave the field "Unknown"
skills/ai-writing-suite/_shared/voice-profile.md:28:  rather than inventing a trait. A profile built on guesses is worse than no
skills/ai-writing-suite/_shared/voice-profile.md:29:  profile, because `comms-polish` will trust it.
skills/ai-writing-suite/_shared/voice-profile.md:30:
skills/ai-writing-suite/_shared/voice-profile.md:31:  STATUS OF THIS FILE: example only. Replace via `voice-onboard`.
skills/ai-writing-suite/_shared/voice-profile.md:32:================================================================================
skills/ai-writing-suite/_shared/voice-profile.md:33:-->
skills/ai-writing-suite/_shared/voice-profile.md:34:
skills/ai-writing-suite/_shared/voice-profile.md:35:# Voice Profile
skills/ai-writing-suite/_shared/voice-profile.md:36:
skills/ai-writing-suite/_shared/voice-profile.md:37:> SAMPLE PROFILE. Replace by running `voice-onboard`. The example below is a
skills/ai-writing-suite/_shared/voice-profile.md:38:> fictional author ("Sam, a data-scientist who blogs about search ranking") so
skills/ai-writing-suite/_shared/voice-profile.md:39:> the field shapes are concrete. Your real profile overwrites all of it.
skills/ai-writing-suite/_shared/voice-profile.md:40:
skills/ai-writing-suite/_shared/voice-profile.md:41:## Meta
skills/ai-writing-suite/_shared/voice-profile.md:42:
skills/ai-writing-suite/_shared/voice-profile.md:43:- **Author:** Sam (example)
skills/ai-writing-suite/_shared/voice-profile.md:44:- **Extracted:** 2026-06-06
skills/ai-writing-suite/_shared/voice-profile.md:45:- **Sample count:** 7
skills/ai-writing-suite/_shared/voice-profile.md:46:- **Sample sources:** personal blog posts, internal memos
skills/ai-writing-suite/_shared/voice-profile.md:47:- **Sample time span:** 2025-11 to 2026-05
skills/ai-writing-suite/_shared/voice-profile.md:48:- **Confidence:** Medium  <!-- Low if N<5, Medium if 5-10, High if 10+ -->
skills/ai-writing-suite/_shared/voice-profile.md:49:
skills/ai-writing-suite/_shared/voice-profile.md:50:## Tone
skills/ai-writing-suite/_shared/voice-profile.md:51:
skills/ai-writing-suite/_shared/voice-profile.md:52:<!-- The overall register. One or two sentences, plus the dominant flavor. -->
skills/ai-writing-suite/_shared/voice-profile.md:53:Direct and analytical, with dry humor. Confident but not salesy. Reads like a
skills/ai-writing-suite/_shared/voice-profile.md:54:practitioner explaining a tradeoff to a peer, not a brand talking to a market.
skills/ai-writing-suite/_shared/voice-profile.md:55:
skills/ai-writing-suite/_shared/voice-profile.md:56:> Evidence: "The reranker helped NDCG by 2 points. It also doubled our latency,
skills/ai-writing-suite/_shared/voice-profile.md:57:> which nobody wanted to talk about."
skills/ai-writing-suite/_shared/voice-profile.md:58:
skills/ai-writing-suite/_shared/voice-profile.md:59:## Sentence Length
skills/ai-writing-suite/_shared/voice-profile.md:60:
skills/ai-writing-suite/_shared/voice-profile.md:61:<!-- Quantify. comms-polish uses this to avoid flattening rhythm to one length. -->
skills/ai-writing-suite/_shared/voice-profile.md:62:- **Average words/sentence:** ~16
skills/ai-writing-suite/_shared/voice-profile.md:63:- **Short sentences (<10 words) share:** ~30%
skills/ai-writing-suite/_shared/voice-profile.md:64:- **Long sentences (>30 words) share:** ~10%
skills/ai-writing-suite/_shared/voice-profile.md:65:- **Rhythm habit:** opens with a short punchy claim, then a longer sentence that
skills/ai-writing-suite/_shared/voice-profile.md:66:  qualifies it. "Claim. Then the caveat."
skills/ai-writing-suite/_shared/voice-profile.md:67:
skills/ai-writing-suite/_shared/voice-profile.md:68:> Evidence: "It worked. But only because the query distribution was unusually
skills/ai-writing-suite/_shared/voice-profile.md:69:> clean that quarter, and we never re-tested on the messy tail."
skills/ai-writing-suite/_shared/voice-profile.md:70:
skills/ai-writing-suite/_shared/voice-profile.md:71:## Vocabulary
skills/ai-writing-suite/_shared/voice-profile.md:72:
skills/ai-writing-suite/_shared/voice-profile.md:73:- **First person:** uses "I" for opinions, "we" for team work; rarely subject-less.
skills/ai-writing-suite/_shared/voice-profile.md:74:- **Signature words:** "tradeoff", "signal", "tail", "calibrate", "noisy".
skills/ai-writing-suite/_shared/voice-profile.md:75:- **Stock phrases / tics:** "the honest answer is...", "in practice".
skills/ai-writing-suite/_shared/voice-profile.md:76:- **Domain / in-group terms:** NDCG, reranker, query understanding, holdout.
skills/ai-writing-suite/_shared/voice-profile.md:77:
skills/ai-writing-suite/_shared/voice-profile.md:78:## Vocabulary Do
skills/ai-writing-suite/_shared/voice-profile.md:79:
skills/ai-writing-suite/_shared/voice-profile.md:80:<!-- Words/constructions the author DOES reach for. comms-polish may keep these. -->
skills/ai-writing-suite/_shared/voice-profile.md:81:- Concrete metrics over adjectives ("2 points" not "significantly").
skills/ai-writing-suite/_shared/voice-profile.md:82:- Hedging that is quantified ("about 70% sure") rather than vague.
skills/ai-writing-suite/_shared/voice-profile.md:83:
skills/ai-writing-suite/_shared/voice-profile.md:84:## Vocabulary Don't
skills/ai-writing-suite/_shared/voice-profile.md:85:
skills/ai-writing-suite/_shared/voice-profile.md:86:<!-- The forbidden list. THIS IS THE STRONGEST SIGNAL. Words the author never
skills/ai-writing-suite/_shared/voice-profile.md:87:     uses are more diagnostic than words they do. comms-polish must avoid these. -->
skills/ai-writing-suite/_shared/voice-profile.md:88:- Never: "delve", "leverage", "synergy", "unlock", "in today's fast-paced world".
skills/ai-writing-suite/_shared/voice-profile.md:89:- Never: exclamation-point hype ("Amazing results!").
skills/ai-writing-suite/_shared/voice-profile.md:90:- Never: em-dash-heavy throat-clearing intros.
skills/ai-writing-suite/_shared/voice-profile.md:91:
skills/ai-writing-suite/_shared/voice-profile.md:92:## Signature Moves
skills/ai-writing-suite/_shared/voice-profile.md:93:
skills/ai-writing-suite/_shared/voice-profile.md:94:<!-- The structural fingerprints: how this author characteristically builds a
skills/ai-writing-suite/_shared/voice-profile.md:95:     point. These are positive patterns comms-polish can preserve. -->
skills/ai-writing-suite/_shared/voice-profile.md:96:- "Not X, but Y" reframes to correct a common assumption.
skills/ai-writing-suite/_shared/voice-profile.md:97:- Drops a number early to anchor the claim, then explains it.
skills/ai-writing-suite/_shared/voice-profile.md:98:- Ends on a concrete consequence, not a summary.
skills/ai-writing-suite/_shared/voice-profile.md:99:
skills/ai-writing-suite/_shared/voice-profile.md:100:## Punctuation & Formatting
skills/ai-writing-suite/_shared/voice-profile.md:101:
skills/ai-writing-suite/_shared/voice-profile.md:102:- **Period vs comma:** period-heavy; short declaratives over long comma chains.
skills/ai-writing-suite/_shared/voice-profile.md:103:- **Em-dash density:** occasional, for asides.
skills/ai-writing-suite/_shared/voice-profile.md:104:- **Ellipsis / exclamation:** ellipsis rare; exclamation almost never.
skills/ai-writing-suite/_shared/voice-profile.md:105:- **Lists:** uses bullets for tradeoffs; avoids numbered steps in prose.
skills/ai-writing-suite/_shared/voice-profile.md:106:- **Emoji:** none.
skills/ai-writing-suite/_shared/voice-profile.md:107:
skills/ai-writing-suite/_shared/voice-profile.md:108:## Openings & Closings
skills/ai-writing-suite/_shared/voice-profile.md:109:
skills/ai-writing-suite/_shared/voice-profile.md:110:- **Opening habit:** leads with the counterintuitive result or a number.
skills/ai-writing-suite/_shared/voice-profile.md:111:- **Closing habit:** lands on a specific consequence or open question, not a
skills/ai-writing-suite/_shared/voice-profile.md:112:  motivational wrap-up.
skills/ai-writing-suite/_shared/voice-profile.md:113:
skills/ai-writing-suite/_shared/voice-profile.md:114:> Evidence (open): "We shipped the model nobody on the team liked."
skills/ai-writing-suite/_shared/voice-profile.md:115:> Evidence (close): "So the real question is whether the tail ever gets clean."
skills/ai-writing-suite/_shared/voice-profile.md:116:
skills/ai-writing-suite/_shared/voice-profile.md:117:## Uncertainty Style
skills/ai-writing-suite/_shared/voice-profile.md:118:
skills/ai-writing-suite/_shared/voice-profile.md:119:<!-- How the author signals they're unsure. comms-polish should match this rather
skills/ai-writing-suite/_shared/voice-profile.md:120:     than flattening everything to false confidence. -->
skills/ai-writing-suite/_shared/voice-profile.md:121:- Quantified and explicit ("about 60% confident", "I haven't tested the edge case").
skills/ai-writing-suite/_shared/voice-profile.md:122:
skills/ai-writing-suite/_shared/voice-profile.md:123:## Things To Avoid
skills/ai-writing-suite/_shared/voice-profile.md:124:
skills/ai-writing-suite/_shared/voice-profile.md:125:<!-- A catch-all for author-specific anti-patterns that don't fit the forbidden
skills/ai-writing-suite/_shared/voice-profile.md:126:     vocabulary list: structures, registers, or moves that read as "not them". -->
skills/ai-writing-suite/_shared/voice-profile.md:127:- Marketing register / superlatives.
skills/ai-writing-suite/_shared/voice-profile.md:128:- Symmetric "on one hand / on the other hand" balance that dodges a stance.
skills/ai-writing-suite/_shared/voice-profile.md:129:- Over-explaining domain terms to an expert audience.
skills/ai-writing-suite/_shared/voice-profile.md:130:
skills/ai-writing-suite/_shared/voice-profile.md:131:## Scope & Calibration
skills/ai-writing-suite/_shared/voice-profile.md:132:
skills/ai-writing-suite/_shared/voice-profile.md:133:<!-- A profile is genre-specific. Note where it applies and where it needs a
skills/ai-writing-suite/_shared/voice-profile.md:134:     fresh pass, so comms-polish doesn't misapply blog voice to a formal report. -->
skills/ai-writing-suite/_shared/voice-profile.md:135:- **Applies to:** blog posts, internal memos, LinkedIn.
skills/ai-writing-suite/_shared/voice-profile.md:136:- **Re-calibrate for:** formal external reports, customer-facing comms.
skills/ai-writing-suite/_shared/voice-profile.md:137:
skills/ai-writing-suite/_shared/voice-profile.md:138:## Changelog
skills/ai-writing-suite/_shared/voice-profile.md:139:
skills/ai-writing-suite/_shared/voice-profile.md:140:<!-- voice-onboard appends here on each update. Living file, not a one-shot. -->
skills/ai-writing-suite/_shared/voice-profile.md:141:- 2026-06-06: Example profile shipped as the schema contract (placeholder).
skills/ai-writing-suite/_shared/voice-profile.md:142:
skills/ai-writing-suite/_shared/voice-profile.md:143:<!--
skills/ai-writing-suite/_shared/voice-profile.md:144:  ATTRIBUTION
skills/ai-writing-suite/_shared/voice-profile.md:145:  -----------
skills/ai-writing-suite/_shared/voice-profile.md:146:  Field set adapted from:
skills/ai-writing-suite/_shared/voice-profile.md:147:    - weijt606/anti-vibe-writing (host-profile-template.md, MIT) — the 10-dimension
skills/ai-writing-suite/_shared/voice-profile.md:148:      voice taxonomy (sentence length, vocabulary, punctuation rhythm, openings/
skills/ai-writing-suite/_shared/voice-profile.md:149:      closings, uncertainty style).
skills/ai-writing-suite/_shared/voice-profile.md:150:    - donghuixin/AI-Vibe-Writing-Skills (1_style_extractor.md, MIT) — the
skills/ai-writing-suite/_shared/voice-profile.md:151:      Do's / Don'ts "Style DNA" framing.
skills/ai-writing-suite/_shared/voice-profile.md:152:  Both MIT-licensed; see the suite NOTICE.md for full copyright lines.
skills/ai-writing-suite/_shared/voice-profile.md:153:-->
skills/ai-writing-suite/_shared/knowledge/clarity.md:1:# Clarity — say one thing per sentence, plainly
skills/ai-writing-suite/_shared/knowledge/clarity.md:2:
skills/ai-writing-suite/_shared/knowledge/clarity.md:3:> **Generic best-practice entry.** Distilled from the four MIT reference repos
skills/ai-writing-suite/_shared/knowledge/clarity.md:4:> (see `Sources` below + `NOTICE.md`). This is the open-source KB. A company fork
skills/ai-writing-suite/_shared/knowledge/clarity.md:5:> replaces or augments these entries with its own playbook via the same slot —
skills/ai-writing-suite/_shared/knowledge/clarity.md:6:> see `README.md`.
skills/ai-writing-suite/_shared/knowledge/clarity.md:7:
skills/ai-writing-suite/_shared/knowledge/clarity.md:8:## Principle
skills/ai-writing-suite/_shared/knowledge/clarity.md:9:
skills/ai-writing-suite/_shared/knowledge/clarity.md:10:A reader should grasp each sentence on the first pass. Clarity is not
skills/ai-writing-suite/_shared/knowledge/clarity.md:11:dumbing-down; it is removing everything between the reader and the point. When a
skills/ai-writing-suite/_shared/knowledge/clarity.md:12:sentence carries two ideas, split it. When a word can be cut without losing
skills/ai-writing-suite/_shared/knowledge/clarity.md:13:meaning, cut it.
skills/ai-writing-suite/_shared/knowledge/clarity.md:14:
skills/ai-writing-suite/_shared/knowledge/clarity.md:15:## Moves
skills/ai-writing-suite/_shared/knowledge/clarity.md:16:
skills/ai-writing-suite/_shared/knowledge/clarity.md:17:- **One idea per sentence.** If you find an "and" joining two full claims, make
skills/ai-writing-suite/_shared/knowledge/clarity.md:18:  two sentences.
skills/ai-writing-suite/_shared/knowledge/clarity.md:19:- **Concrete over abstract.** "We cut p95 latency from 800ms to 120ms" beats "We
skills/ai-writing-suite/_shared/knowledge/clarity.md:20:  significantly improved performance." Numbers, names, dates — not "robust,"
skills/ai-writing-suite/_shared/knowledge/clarity.md:21:  "significant," "various."
skills/ai-writing-suite/_shared/knowledge/clarity.md:22:- **Subject-verb-object, early.** Put the actor and the action at the front. Long
skills/ai-writing-suite/_shared/knowledge/clarity.md:23:  windups ("In order to be able to...") bury the verb.
skills/ai-writing-suite/_shared/knowledge/clarity.md:24:- **Cut filler.** Delete "it's worth noting that," "in today's fast-paced world,"
skills/ai-writing-suite/_shared/knowledge/clarity.md:25:  "at the end of the day." They add length, not meaning.
skills/ai-writing-suite/_shared/knowledge/clarity.md:26:- **Prefer the short word.** "Use" not "utilize." "Help" not "facilitate."
skills/ai-writing-suite/_shared/knowledge/clarity.md:27:
skills/ai-writing-suite/_shared/knowledge/clarity.md:28:## Before / After
skills/ai-writing-suite/_shared/knowledge/clarity.md:29:
skills/ai-writing-suite/_shared/knowledge/clarity.md:30:- **Before:** It is worth noting that, in order to facilitate improved outcomes,
skills/ai-writing-suite/_shared/knowledge/clarity.md:31:  the team undertook various optimizations across the system.
skills/ai-writing-suite/_shared/knowledge/clarity.md:32:- **After:** The team cut three slow queries. p95 latency dropped from 800ms to
skills/ai-writing-suite/_shared/knowledge/clarity.md:33:  120ms.
skills/ai-writing-suite/_shared/knowledge/clarity.md:34:
skills/ai-writing-suite/_shared/knowledge/clarity.md:35:## When this matters most
skills/ai-writing-suite/_shared/knowledge/clarity.md:36:
skills/ai-writing-suite/_shared/knowledge/clarity.md:37:Technical memos, status updates, PR descriptions — anywhere a busy reader skims.
skills/ai-writing-suite/_shared/knowledge/clarity.md:38:Clarity is the first thing to check and the cheapest to fix.
skills/ai-writing-suite/_shared/knowledge/clarity.md:39:
skills/ai-writing-suite/_shared/knowledge/clarity.md:40:## Sources
skills/ai-writing-suite/_shared/knowledge/clarity.md:41:
skills/ai-writing-suite/_shared/knowledge/clarity.md:42:- `nature` (`nature-polishing` style-guardrails: concrete claims, cut hedging)
skills/ai-writing-suite/_shared/knowledge/clarity.md:43:- `anti-vibe` (consultant-speak removal, "数据放具体数字")
skills/ai-writing-suite/_shared/knowledge/clarity.md:44:- `stop-slop` (plain-word rules)
skills/ai-writing-suite/_shared/knowledge/clarity.md:45:- `avoid-ai` (vague-attribution / vocabulary tiers)
skills/ai-writing-suite/evals/detector/cli.py:1:"""Command-line entry: `python3 -m detector.cli <file>` (or `-` for stdin).
skills/ai-writing-suite/evals/detector/cli.py:2:
skills/ai-writing-suite/evals/detector/cli.py:3:WHY a CLI: lets a human or a CI step run the detector on any draft without
skills/ai-writing-suite/evals/detector/cli.py:4:importing the package. Prints the score band, classification, and flagged spans
skills/ai-writing-suite/evals/detector/cli.py:5:grouped by type — the same view comms-polish surfaces in `detect` mode.
skills/ai-writing-suite/evals/detector/cli.py:6:
skills/ai-writing-suite/evals/detector/cli.py:7:Run from the `evals/` directory:
skills/ai-writing-suite/evals/detector/cli.py:8:    python3 -m detector.cli path/to/draft.md
skills/ai-writing-suite/evals/detector/cli.py:9:    cat draft.md | python3 -m detector.cli -
skills/ai-writing-suite/evals/detector/cli.py:10:"""
skills/ai-writing-suite/evals/detector/cli.py:11:
skills/ai-writing-suite/evals/detector/cli.py:12:import sys
skills/ai-writing-suite/evals/detector/cli.py:13:
skills/ai-writing-suite/evals/detector/cli.py:14:from .detector import analyze
skills/ai-writing-suite/evals/detector/cli.py:15:
skills/ai-writing-suite/evals/detector/cli.py:16:
skills/ai-writing-suite/evals/detector/cli.py:17:def _read(arg):
skills/ai-writing-suite/evals/detector/cli.py:18:    if arg == "-":
skills/ai-writing-suite/evals/detector/cli.py:19:        return sys.stdin.read()
skills/ai-writing-suite/evals/detector/cli.py:20:    with open(arg, "r", encoding="utf-8") as fh:
skills/ai-writing-suite/evals/detector/cli.py:21:        return fh.read()
skills/ai-writing-suite/evals/detector/cli.py:22:
skills/ai-writing-suite/evals/detector/cli.py:23:
skills/ai-writing-suite/evals/detector/cli.py:24:def main(argv=None):
skills/ai-writing-suite/evals/detector/cli.py:25:    argv = argv if argv is not None else sys.argv[1:]
skills/ai-writing-suite/evals/detector/cli.py:26:    if not argv:
skills/ai-writing-suite/evals/detector/cli.py:27:        print("usage: python3 -m detector.cli <file|->", file=sys.stderr)
skills/ai-writing-suite/evals/detector/cli.py:28:        return 2
skills/ai-writing-suite/evals/detector/cli.py:29:
skills/ai-writing-suite/evals/detector/cli.py:30:    result = analyze(_read(argv[0]))
skills/ai-writing-suite/evals/detector/cli.py:31:    print(f"Score:          {result['score']}/100  ({result['label']})")
skills/ai-writing-suite/evals/detector/cli.py:32:    print(f"Classification: {result['classification']}  "
skills/ai-writing-suite/evals/detector/cli.py:33:          f"(confidence: {result['confidence']})")
skills/ai-writing-suite/evals/detector/cli.py:34:    print(f"Words:          {result['stats'].get('wordCount', 0)}")
skills/ai-writing-suite/evals/detector/cli.py:35:    print(f"Distinct tells: {len(result['issues'])}")
skills/ai-writing-suite/evals/detector/cli.py:36:    if result["issues"]:
skills/ai-writing-suite/evals/detector/cli.py:37:        print("\nFlagged:")
skills/ai-writing-suite/evals/detector/cli.py:38:        # Group by type so the output reads as a fix list, not a flat dump.
skills/ai-writing-suite/evals/detector/cli.py:39:        by_type = {}
skills/ai-writing-suite/evals/detector/cli.py:40:        for it in result["issues"]:
skills/ai-writing-suite/evals/detector/cli.py:41:            by_type.setdefault(it["type"], []).append(it["text"])
skills/ai-writing-suite/evals/detector/cli.py:42:        for typ in sorted(by_type):
skills/ai-writing-suite/evals/detector/cli.py:43:            spans = ", ".join(by_type[typ][:8])
skills/ai-writing-suite/evals/detector/cli.py:44:            more = "" if len(by_type[typ]) <= 8 else f" (+{len(by_type[typ]) - 8} more)"
skills/ai-writing-suite/evals/detector/cli.py:45:            print(f"  [{typ}] {spans}{more}")
skills/ai-writing-suite/evals/detector/cli.py:46:    return 0
skills/ai-writing-suite/evals/detector/cli.py:47:
skills/ai-writing-suite/evals/detector/cli.py:48:
skills/ai-writing-suite/evals/detector/cli.py:49:if __name__ == "__main__":
skills/ai-writing-suite/evals/detector/cli.py:50:    sys.exit(main())
skills/ai-writing-suite/evals/README.md:1:# Evals — AI Writing Suite (Layer 3)
skills/ai-writing-suite/evals/README.md:2:
skills/ai-writing-suite/evals/README.md:3:The eval subsystem for the suite. Three independent pieces, all **Python 3
skills/ai-writing-suite/evals/README.md:4:stdlib only** (no pip, no Node, no API key required to run the deterministic
skills/ai-writing-suite/evals/README.md:5:parts):
skills/ai-writing-suite/evals/README.md:6:
skills/ai-writing-suite/evals/README.md:7:| Piece | What it does | Needs a model? |
skills/ai-writing-suite/evals/README.md:8:| --- | --- | --- |
skills/ai-writing-suite/evals/README.md:9:| `detector/` | Mechanical AI-tell scanner — cheap deterministic regression gate | No |
skills/ai-writing-suite/evals/README.md:10:| `fixtures/` | Before/after pairs across 4 genres, score bands + LLM-judge rubric | Judge half only |
skills/ai-writing-suite/evals/README.md:11:| `smoke_test.py` | Automates the KB ingestion+retrieval smoke chain (design D12) | No |
skills/ai-writing-suite/evals/README.md:12:
skills/ai-writing-suite/evals/README.md:13:> Design lineage: D10 (eval harness + Autorefine-style self-improvement) and D12
skills/ai-writing-suite/evals/README.md:14:> (prove one end-to-end KB retrieval chain). See
skills/ai-writing-suite/evals/README.md:15:> `docs/design-ai-writing-suite-v1-2026-06-06.md`.
skills/ai-writing-suite/evals/README.md:16:
skills/ai-writing-suite/evals/README.md:17:## How to run each piece
skills/ai-writing-suite/evals/README.md:18:
skills/ai-writing-suite/evals/README.md:19:All commands run **from this `evals/` directory**.
skills/ai-writing-suite/evals/README.md:20:
skills/ai-writing-suite/evals/README.md:21:```bash
skills/ai-writing-suite/evals/README.md:22:# 1. Mechanical detector — unit tests
skills/ai-writing-suite/evals/README.md:23:python3 -m unittest detector.test_detector
skills/ai-writing-suite/evals/README.md:24:
skills/ai-writing-suite/evals/README.md:25:# 1b. Detector on any file (or stdin)
skills/ai-writing-suite/evals/README.md:26:python3 -m detector.cli path/to/draft.md
skills/ai-writing-suite/evals/README.md:27:cat draft.md | python3 -m detector.cli -
skills/ai-writing-suite/evals/README.md:28:
skills/ai-writing-suite/evals/README.md:29:# 2. Fixtures — deterministic score-band check + calibration report
skills/ai-writing-suite/evals/README.md:30:python3 -m fixtures.run_fixtures
skills/ai-writing-suite/evals/README.md:31:python3 -m fixtures.run_fixtures --judge      # also emits the LLM-judge prompts (SKIPPED offline)
skills/ai-writing-suite/evals/README.md:32:python3 -m unittest fixtures.test_fixtures    # asserts the suite stays calibrated
skills/ai-writing-suite/evals/README.md:33:
skills/ai-writing-suite/evals/README.md:34:# 3. KB smoke test — ingestion+retrieval chain
skills/ai-writing-suite/evals/README.md:35:python3 smoke_test.py
skills/ai-writing-suite/evals/README.md:36:
skills/ai-writing-suite/evals/README.md:37:# Everything at once
skills/ai-writing-suite/evals/README.md:38:python3 -m unittest discover -p 'test_*.py'   # all unit tests
skills/ai-writing-suite/evals/README.md:39:python3 smoke_test.py                         # smoke (own runner)
skills/ai-writing-suite/evals/README.md:40:```
skills/ai-writing-suite/evals/README.md:41:
skills/ai-writing-suite/evals/README.md:42:Exit code `0` = pass for every command. CI should run all three.
skills/ai-writing-suite/evals/README.md:43:
skills/ai-writing-suite/evals/README.md:44:## The three pieces in detail
skills/ai-writing-suite/evals/README.md:45:
skills/ai-writing-suite/evals/README.md:46:### 1. `detector/` — mechanical detector
skills/ai-writing-suite/evals/README.md:47:
skills/ai-writing-suite/evals/README.md:48:A faithful-but-pragmatic Python port of the avoid-ai JS engine
skills/ai-writing-suite/evals/README.md:49:(`/tmp/grill-refs/avoid-ai-writing/detector/patterns.js`, MIT). It keys off the
skills/ai-writing-suite/evals/README.md:50:same AI-tell categories the `comms-polish` skill reads from
skills/ai-writing-suite/evals/README.md:51:`_shared/patterns/`. Pure regex + arithmetic — no model.
skills/ai-writing-suite/evals/README.md:52:
skills/ai-writing-suite/evals/README.md:53:- `patterns.py` — the rule data (vocab tiers, phrase regexes, weights). One
skills/ai-writing-suite/evals/README.md:54:  block per `_shared/patterns/` category.
skills/ai-writing-suite/evals/README.md:55:- `detector.py` — `analyze(text)` returns `{score, label, issues, stats,
skills/ai-writing-suite/evals/README.md:56:  classification, confidence}`. Scoring: collect issues → dedup by (type, text)
skills/ai-writing-suite/evals/README.md:57:  → sum category weights → normalize by `log2(words/50)`.
skills/ai-writing-suite/evals/README.md:58:- `cli.py` — `python3 -m detector.cli <file>`.
skills/ai-writing-suite/evals/README.md:59:- `test_detector.py` — mirrors the JS test coverage (length gates, AI-heavy vs
skills/ai-writing-suite/evals/README.md:60:  human, per-category detectors, FN-biased classifier, dedup math).
skills/ai-writing-suite/evals/README.md:61:
skills/ai-writing-suite/evals/README.md:62:**Role:** the cheap regression gate. It runs on every commit and never costs an
skills/ai-writing-suite/evals/README.md:63:API call. It catches *vocabulary and density* regressions; it does **not** judge
skills/ai-writing-suite/evals/README.md:64:whether a rewrite kept meaning or invented a fact — that is the LLM judge's job.
skills/ai-writing-suite/evals/README.md:65:
skills/ai-writing-suite/evals/README.md:66:### 2. `fixtures/` — before/after fixtures + LLM judge
skills/ai-writing-suite/evals/README.md:67:
skills/ai-writing-suite/evals/README.md:68:`fixtures.json` holds 8 fixtures (2 per genre: tweet / linkedin / readme /
skills/ai-writing-suite/evals/README.md:69:memo). Each has an AI-shaped `before`, a good human `after`, detector score
skills/ai-writing-suite/evals/README.md:70:bands, and `rubric_focus` (which rubric dimensions matter here).
skills/ai-writing-suite/evals/README.md:71:
skills/ai-writing-suite/evals/README.md:72:- `run_fixtures.py` — runs the **deterministic** half (assert score bands +
skills/ai-writing-suite/evals/README.md:73:  report naive-baseline miss rate). With `--judge` it fills the rubric prompt
skills/ai-writing-suite/evals/README.md:74:  per fixture and marks them **SKIPPED** (no model wired in — it never fabricates
skills/ai-writing-suite/evals/README.md:75:  a verdict offline).
skills/ai-writing-suite/evals/README.md:76:- `rubric.md` — the LLM-judge scoring contract (dimensions, verdict aggregation,
skills/ai-writing-suite/evals/README.md:77:  a model-agnostic zero-shot prompt template). `no_fabrication` is always
skills/ai-writing-suite/evals/README.md:78:  required: a fluent rewrite that invents a number FAILS.
skills/ai-writing-suite/evals/README.md:79:- `test_fixtures.py` — asserts the suite stays well-formed, in-band, and
skills/ai-writing-suite/evals/README.md:80:  calibrated.
skills/ai-writing-suite/evals/README.md:81:
skills/ai-writing-suite/evals/README.md:82:### 3. `smoke_test.py` — KB retrieval chain
skills/ai-writing-suite/evals/README.md:83:
skills/ai-writing-suite/evals/README.md:84:Automates the TEST CASE blocks in `_shared/knowledge/SMOKE-TEST.md`. It parses
skills/ai-writing-suite/evals/README.md:85:each block (query / expected entry / expected passage), replicates the INDEX.md
skills/ai-writing-suite/evals/README.md:86:retrieval protocol **in code** (keyword overlap, summary-intent tie-break — zero
skills/ai-writing-suite/evals/README.md:87:embeddings, design D5), opens the chosen entry file, and asserts the expected
skills/ai-writing-suite/evals/README.md:88:passage is present. This proves the "drop in a markdown page → retrieval works"
skills/ai-writing-suite/evals/README.md:89:promise end to end.
skills/ai-writing-suite/evals/README.md:90:
skills/ai-writing-suite/evals/README.md:91:## Calibration rule (read before adding fixtures)
skills/ai-writing-suite/evals/README.md:92:
skills/ai-writing-suite/evals/README.md:93:Per the project rule (`CLAUDE.md` → "Evals"): **a naive baseline must miss
skills/ai-writing-suite/evals/README.md:94:~30-40% of cases.** If the baseline catches >80%, the evals are too lenient to
skills/ai-writing-suite/evals/README.md:95:catch regressions — a broken ruler.
skills/ai-writing-suite/evals/README.md:96:
skills/ai-writing-suite/evals/README.md:97:Here the "naive baseline" is: *flag the `before` as AI iff the detector score
skills/ai-writing-suite/evals/README.md:98:≥ `baseline_threshold`*. The current suite sits at **3/8 = 38% miss** (verified
skills/ai-writing-suite/evals/README.md:99:by `test_fixtures.Calibration`).
skills/ai-writing-suite/evals/README.md:100:
skills/ai-writing-suite/evals/README.md:101:**How the fixtures are made hard:** half the `before` items are `subtle` — they
skills/ai-writing-suite/evals/README.md:102:are AI-written but carry **no vocabulary tells**, only structural / rhythm tells
skills/ai-writing-suite/evals/README.md:103:the flat detector underweights on short text:
skills/ai-writing-suite/evals/README.md:104:
skills/ai-writing-suite/evals/README.md:105:- `tweet-02` — negative parallelism + vague closer, zero specifics.
skills/ai-writing-suite/evals/README.md:106:- `linkedin-02` — rule-of-three scaffolding + engagement-bait closer.
skills/ai-writing-suite/evals/README.md:107:- `readme-02` — pure filler, zero content ("smooth onboarding experience").
skills/ai-writing-suite/evals/README.md:108:- `memo-02` — false concession + hedge-stacking (the borderline case: scores
skills/ai-writing-suite/evals/README.md:109:  ~15, just over threshold).
skills/ai-writing-suite/evals/README.md:110:
skills/ai-writing-suite/evals/README.md:111:The mechanical detector misses the first three by design. That gap is exactly
skills/ai-writing-suite/evals/README.md:112:what the LLM judge exists to cover — and why the suite needs both halves.
skills/ai-writing-suite/evals/README.md:113:
skills/ai-writing-suite/evals/README.md:114:### Adding a new fixture
skills/ai-writing-suite/evals/README.md:115:
skills/ai-writing-suite/evals/README.md:116:1. Add an object to `fixtures.json > fixtures` with: `id`, `genre`,
skills/ai-writing-suite/evals/README.md:117:   `difficulty` (`obvious`|`subtle`), `before`, `after`, `after_band_max`,
skills/ai-writing-suite/evals/README.md:118:   `rubric_focus`, `expect_baseline` (`catch`|`miss`), and — for subtle ones —
skills/ai-writing-suite/evals/README.md:119:   a `subtle_tell` explaining the non-vocabulary tell.
skills/ai-writing-suite/evals/README.md:120:2. Run `python3 -m fixtures.run_fixtures` to read the actual detector scores.
skills/ai-writing-suite/evals/README.md:121:3. Set `before_band_min`/`before_band_max` to bracket the observed score (a
skills/ai-writing-suite/evals/README.md:122:   regression guard, not an aspiration). Set `expect_baseline` to match what the
skills/ai-writing-suite/evals/README.md:123:   detector actually does at the threshold.
skills/ai-writing-suite/evals/README.md:124:4. Re-run `python3 -m unittest fixtures.test_fixtures`. If the calibration test
skills/ai-writing-suite/evals/README.md:125:   fails, the miss rate drifted out of 30-40% — rebalance obvious vs subtle
skills/ai-writing-suite/evals/README.md:126:   fixtures (don't move the threshold to paper over it).
skills/ai-writing-suite/evals/README.md:127:
skills/ai-writing-suite/evals/README.md:128:## Wiring into self-improvement (Autorefine methodology, D10)
skills/ai-writing-suite/evals/README.md:129:
skills/ai-writing-suite/evals/README.md:130:The suite's `_shared/self-improvement.md` proposes new tell rules over time.
skills/ai-writing-suite/evals/README.md:131:This eval subsystem is the **gate** those proposals pass through, following the
skills/ai-writing-suite/evals/README.md:132:Autorefine Three-Gulfs loop (`~/.claude/skills/autorefine/`):
skills/ai-writing-suite/evals/README.md:133:
skills/ai-writing-suite/evals/README.md:134:1. **Error analysis (Gulf 1).** When `comms-polish` mishandles a draft, capture
skills/ai-writing-suite/evals/README.md:135:   it as a new fixture (a failing `before`). The fixture set IS the failure
skills/ai-writing-suite/evals/README.md:136:   taxonomy.
skills/ai-writing-suite/evals/README.md:137:2. **Judge calibration (Gulf 2).** A proposed rule must be expressible as either
skills/ai-writing-suite/evals/README.md:138:   a detector pattern (add to `detector/patterns.py` + a `test_detector` case)
skills/ai-writing-suite/evals/README.md:139:   or a rubric dimension (add to `rubric.md` + a fixture `rubric_focus`). If it
skills/ai-writing-suite/evals/README.md:140:   can be neither, it is not measurable and does not ship.
skills/ai-writing-suite/evals/README.md:141:3. **Mutation, eval-gated (Gulf 3).** Apply the proposed rule, then re-run this
skills/ai-writing-suite/evals/README.md:142:   suite. Keep the change only if (a) all unit tests still pass, (b) the new
skills/ai-writing-suite/evals/README.md:143:   fixture flips from FAIL to PASS, and (c) the calibration miss rate stays in
skills/ai-writing-suite/evals/README.md:144:   30-40% (no regression on the rest of the suite). A proposed rule that
skills/ai-writing-suite/evals/README.md:145:   over-fires drops the miss rate below 30% — the calibration test catches it.
skills/ai-writing-suite/evals/README.md:146:
skills/ai-writing-suite/evals/README.md:147:This subsystem wires the **measurement**. The full mutation loop (generate
skills/ai-writing-suite/evals/README.md:148:candidate rules, auto-apply, auto-score, keep/discard) is Autorefine's job and
skills/ai-writing-suite/evals/README.md:149:is **not** built here — D10 scopes v1 to "each proposed rule is eval-measured
skills/ai-writing-suite/evals/README.md:150:before human approval," which is exactly what steps 2-3 provide.
skills/ai-writing-suite/evals/README.md:151:
skills/ai-writing-suite/evals/README.md:152:## Attribution
skills/ai-writing-suite/evals/README.md:153:
skills/ai-writing-suite/evals/README.md:154:The detector is a Python port of `conorbronsdon/avoid-ai-writing` (MIT). Pattern
skills/ai-writing-suite/evals/README.md:155:categories trace to the seven source catalogs credited in
skills/ai-writing-suite/evals/README.md:156:`_shared/patterns/00-index.md` and the skill `NOTICE.md`.
skills/ai-writing-suite/_shared/knowledge/tone.md:1:# Tone — sound like a person, calibrated to the context
skills/ai-writing-suite/_shared/knowledge/tone.md:2:
skills/ai-writing-suite/_shared/knowledge/tone.md:3:> **Generic best-practice entry.** Distilled from the four MIT reference repos
skills/ai-writing-suite/_shared/knowledge/tone.md:4:> (see `Sources`). Open-source KB; company forks swap via the same slot
skills/ai-writing-suite/_shared/knowledge/tone.md:5:> (`README.md`).
skills/ai-writing-suite/_shared/knowledge/tone.md:6:
skills/ai-writing-suite/_shared/knowledge/tone.md:7:## Principle
skills/ai-writing-suite/_shared/knowledge/tone.md:8:
skills/ai-writing-suite/_shared/knowledge/tone.md:9:Tone is the voice the reader hears. Good professional tone is direct, warm
skills/ai-writing-suite/_shared/knowledge/tone.md:10:enough to be human, and free of both corporate stiffness and AI's over-eager
skills/ai-writing-suite/_shared/knowledge/tone.md:11:cheerfulness. The target is "a competent colleague explaining something," not a
skills/ai-writing-suite/_shared/knowledge/tone.md:12:press release and not a chatbot.
skills/ai-writing-suite/_shared/knowledge/tone.md:13:
skills/ai-writing-suite/_shared/knowledge/tone.md:14:## Moves
skills/ai-writing-suite/_shared/knowledge/tone.md:15:
skills/ai-writing-suite/_shared/knowledge/tone.md:16:- **Drop the sycophancy.** "Great question!", "I'd be happy to help", "Certainly!"
skills/ai-writing-suite/_shared/knowledge/tone.md:17:  are chatbot tics. Start with the substance.
skills/ai-writing-suite/_shared/knowledge/tone.md:18:- **Vary sentence length.** Uniformly medium sentences read as machine-generated
skills/ai-writing-suite/_shared/knowledge/tone.md:19:  (low burstiness). Mix a short punch with a longer explanation.
skills/ai-writing-suite/_shared/knowledge/tone.md:20:- **No hype inflation.** "Revolutionary," "game-changing," "seamless,"
skills/ai-writing-suite/_shared/knowledge/tone.md:21:  "robust" — claims the text can't back up. State what it actually does.
skills/ai-writing-suite/_shared/knowledge/tone.md:22:- **Hedge only where there's real uncertainty.** Stacked hedges ("it might
skills/ai-writing-suite/_shared/knowledge/tone.md:23:  perhaps be somewhat possible") signal an AI covering itself. Say what you know
skills/ai-writing-suite/_shared/knowledge/tone.md:24:  plainly; flag the one thing you don't.
skills/ai-writing-suite/_shared/knowledge/tone.md:25:- **Match formality to the channel.** A Slack update is looser than a board memo.
skills/ai-writing-suite/_shared/knowledge/tone.md:26:  Don't write Slack like a contract or a memo like Slack.
skills/ai-writing-suite/_shared/knowledge/tone.md:27:
skills/ai-writing-suite/_shared/knowledge/tone.md:28:## Before / After
skills/ai-writing-suite/_shared/knowledge/tone.md:29:
skills/ai-writing-suite/_shared/knowledge/tone.md:30:- **Before:** Great question! This is a really powerful, game-changing approach
skills/ai-writing-suite/_shared/knowledge/tone.md:31:  that could potentially help streamline your workflow seamlessly.
skills/ai-writing-suite/_shared/knowledge/tone.md:32:- **After:** This cuts the manual step. You paste the link; it returns the draft.
skills/ai-writing-suite/_shared/knowledge/tone.md:33:
skills/ai-writing-suite/_shared/knowledge/tone.md:34:## When this matters most
skills/ai-writing-suite/_shared/knowledge/tone.md:35:
skills/ai-writing-suite/_shared/knowledge/tone.md:36:Anything customer- or leadership-facing, and anything passed off as your own
skills/ai-writing-suite/_shared/knowledge/tone.md:37:writing. Tone is what makes a reader trust — or distrust — the content.
skills/ai-writing-suite/_shared/knowledge/tone.md:38:
skills/ai-writing-suite/_shared/knowledge/tone.md:39:## Sources
skills/ai-writing-suite/_shared/knowledge/tone.md:40:
skills/ai-writing-suite/_shared/knowledge/tone.md:41:- `blader` / `aboudjem` (sycophancy, hype, hedging tells)
skills/ai-writing-suite/_shared/knowledge/tone.md:42:- `rhythm-stylometric` patterns (burstiness, register shift)
skills/ai-writing-suite/_shared/knowledge/tone.md:43:- `anti-vibe` (`host-profile`: the user's actual voice)
skills/ai-writing-suite/_shared/knowledge/tone.md:44:- `stop-slop` (no-hype rules)
skills/ai-writing-suite/evals/fixtures/rubric.md:1:# LLM-Judge Rubric — comms-polish before/after
skills/ai-writing-suite/evals/fixtures/rubric.md:2:
skills/ai-writing-suite/evals/fixtures/rubric.md:3:This is the scoring contract for the **judgment** half of the eval. The
skills/ai-writing-suite/evals/fixtures/rubric.md:4:mechanical detector (`evals/detector/`) catches vocabulary and density tells; it
skills/ai-writing-suite/evals/fixtures/rubric.md:5:cannot tell whether a rewrite *preserved meaning* or *invented a number*. That
skills/ai-writing-suite/evals/fixtures/rubric.md:6:is what this rubric is for: a model reads the `before`, the `after`, and the
skills/ai-writing-suite/evals/fixtures/rubric.md:7:expected outcome, and scores the rewrite on the dimensions below.
skills/ai-writing-suite/evals/fixtures/rubric.md:8:
skills/ai-writing-suite/evals/fixtures/rubric.md:9:> **Why both halves exist.** The detector is the cheap, deterministic regression
skills/ai-writing-suite/evals/fixtures/rubric.md:10:> gate (runs every commit, no API key). The LLM judge is the quality gate (runs
skills/ai-writing-suite/evals/fixtures/rubric.md:11:> on demand, needs a model). A rewrite can pass the detector — score drops to 0 —
skills/ai-writing-suite/evals/fixtures/rubric.md:12:> while *failing* the judge by deleting a fact or fabricating evidence. Neither
skills/ai-writing-suite/evals/fixtures/rubric.md:13:> half alone is sufficient.
skills/ai-writing-suite/evals/fixtures/rubric.md:14:
skills/ai-writing-suite/evals/fixtures/rubric.md:15:## Inputs the judge receives
skills/ai-writing-suite/evals/fixtures/rubric.md:16:
skills/ai-writing-suite/evals/fixtures/rubric.md:17:- `before` — the AI-shaped draft.
skills/ai-writing-suite/evals/fixtures/rubric.md:18:- `after` — the candidate human rewrite (this is what's being scored).
skills/ai-writing-suite/evals/fixtures/rubric.md:19:- `genre` — tweet / linkedin / readme / memo (sets length + tone expectations).
skills/ai-writing-suite/evals/fixtures/rubric.md:20:- `rubric_focus` — the dimensions that matter most for this fixture.
skills/ai-writing-suite/evals/fixtures/rubric.md:21:- `subtle_tell` (when present) — what the AI tell actually is, so the judge
skills/ai-writing-suite/evals/fixtures/rubric.md:22:  knows what a good rewrite had to remove.
skills/ai-writing-suite/evals/fixtures/rubric.md:23:
skills/ai-writing-suite/evals/fixtures/rubric.md:24:## Dimensions (score each PASS / FAIL, with a one-line reason)
skills/ai-writing-suite/evals/fixtures/rubric.md:25:
skills/ai-writing-suite/evals/fixtures/rubric.md:26:| Dimension | PASS when | FAIL when |
skills/ai-writing-suite/evals/fixtures/rubric.md:27:| --- | --- | --- |
skills/ai-writing-suite/evals/fixtures/rubric.md:28:| `meaning_preserved` | Every claim, fact, number, and name in `before` survives in `after` (unless the fixture asks to add specifics). | A claim was dropped or its meaning changed. |
skills/ai-writing-suite/evals/fixtures/rubric.md:29:| `tells_removed` | The AI tells named in `subtle_tell` (or the obvious vocabulary tells) are gone. | A flagged tell still reads as AI. |
skills/ai-writing-suite/evals/fixtures/rubric.md:30:| `no_fabrication` | Any new specifics in `after` are plausible *placeholders the author would fill*, not invented facts presented as real. **This is the highest-stakes dimension.** | `after` invents a number, source, or quote that `before` did not contain and presents it as fact. |
skills/ai-writing-suite/evals/fixtures/rubric.md:31:| `voice_kept` | `after` reads like a competent human in this genre, not generic corporate rewrite. | `after` traded one robotic register for another. |
skills/ai-writing-suite/evals/fixtures/rubric.md:32:| `specificity_added` | Where `before` was vague, `after` is concrete (only scored when in `rubric_focus`). | `after` is still vague / empty calories. |
skills/ai-writing-suite/evals/fixtures/rubric.md:33:| `genre_fit` | Length and tone fit the genre (tweet ≤ 280 chars, readme is scannable, memo leads with the decision). | Wrong shape for the channel. |
skills/ai-writing-suite/evals/fixtures/rubric.md:34:
skills/ai-writing-suite/evals/fixtures/rubric.md:35:Structural-tell dimensions appear in `rubric_focus` by name for fixtures that
skills/ai-writing-suite/evals/fixtures/rubric.md:36:target them: `negative_parallelism_removed`, `rule_of_three_removed`,
skills/ai-writing-suite/evals/fixtures/rubric.md:37:`engagement_hook_removed`, `false_concession_removed`, `hedge_stack_removed`,
skills/ai-writing-suite/evals/fixtures/rubric.md:38:`vague_attribution_removed`, `filler_removed`.
skills/ai-writing-suite/evals/fixtures/rubric.md:39:
skills/ai-writing-suite/evals/fixtures/rubric.md:40:## Verdict aggregation
skills/ai-writing-suite/evals/fixtures/rubric.md:41:
skills/ai-writing-suite/evals/fixtures/rubric.md:42:- **PASS overall** = all `rubric_focus` dimensions PASS **and** `no_fabrication`
skills/ai-writing-suite/evals/fixtures/rubric.md:43:  PASS (no_fabrication is always required, even when not listed in focus).
skills/ai-writing-suite/evals/fixtures/rubric.md:44:- **FAIL overall** = any focus dimension FAIL, or any fabrication.
skills/ai-writing-suite/evals/fixtures/rubric.md:45:
skills/ai-writing-suite/evals/fixtures/rubric.md:46:## Judge prompt template (zero-shot, model-agnostic)
skills/ai-writing-suite/evals/fixtures/rubric.md:47:
skills/ai-writing-suite/evals/fixtures/rubric.md:48:```
skills/ai-writing-suite/evals/fixtures/rubric.md:49:You are evaluating a prose rewrite. The "before" is AI-shaped writing; the
skills/ai-writing-suite/evals/fixtures/rubric.md:50:"after" is a human rewrite of it. Judge ONLY the "after".
skills/ai-writing-suite/evals/fixtures/rubric.md:51:
skills/ai-writing-suite/evals/fixtures/rubric.md:52:GENRE: {genre}
skills/ai-writing-suite/evals/fixtures/rubric.md:53:WHAT THE AI TELL WAS: {subtle_tell or "obvious AI vocabulary and formatting"}
skills/ai-writing-suite/evals/fixtures/rubric.md:54:DIMENSIONS TO WEIGH: {rubric_focus}
skills/ai-writing-suite/evals/fixtures/rubric.md:55:
skills/ai-writing-suite/evals/fixtures/rubric.md:56:BEFORE:
skills/ai-writing-suite/evals/fixtures/rubric.md:57:{before}
skills/ai-writing-suite/evals/fixtures/rubric.md:58:
skills/ai-writing-suite/evals/fixtures/rubric.md:59:AFTER:
skills/ai-writing-suite/evals/fixtures/rubric.md:60:{after}
skills/ai-writing-suite/evals/fixtures/rubric.md:61:
skills/ai-writing-suite/evals/fixtures/rubric.md:62:For each dimension, output: <dimension>: PASS|FAIL — <one-line reason>.
skills/ai-writing-suite/evals/fixtures/rubric.md:63:Then output: VERDICT: PASS|FAIL.
skills/ai-writing-suite/evals/fixtures/rubric.md:64:Rule: no_fabrication must PASS or the whole verdict is FAIL, regardless of how
skills/ai-writing-suite/evals/fixtures/rubric.md:65:good the prose reads.
skills/ai-writing-suite/evals/fixtures/rubric.md:66:```
skills/ai-writing-suite/evals/fixtures/rubric.md:67:
skills/ai-writing-suite/evals/fixtures/rubric.md:68:## What the judge must NOT do
skills/ai-writing-suite/evals/fixtures/rubric.md:69:
skills/ai-writing-suite/evals/fixtures/rubric.md:70:- Do not reward fluency that came from inventing facts. A vague-but-honest
skills/ai-writing-suite/evals/fixtures/rubric.md:71:  rewrite beats a specific-but-fabricated one.
skills/ai-writing-suite/evals/fixtures/rubric.md:72:- Do not penalize the `after` for being shorter — concision is the goal.
skills/ai-writing-suite/evals/fixtures/rubric.md:73:- Do not re-flag tells the fixture did not ask about (scope to `rubric_focus`).
skills/ai-writing-suite/_shared/host-profile-template.md:1:<!--
skills/ai-writing-suite/_shared/host-profile-template.md:2:================================================================================
skills/ai-writing-suite/_shared/host-profile-template.md:3:  host-profile-template.md  —  BLANK VOICE FORM
skills/ai-writing-suite/_shared/host-profile-template.md:4:================================================================================
skills/ai-writing-suite/_shared/host-profile-template.md:5:
skills/ai-writing-suite/_shared/host-profile-template.md:6:  WHAT THIS IS
skills/ai-writing-suite/_shared/host-profile-template.md:7:  ------------
skills/ai-writing-suite/_shared/host-profile-template.md:8:  The reusable blank form that `voice-onboard` fills in, one field at a time,
skills/ai-writing-suite/_shared/host-profile-template.md:9:  from your interview answers + writing samples. When complete, its contents
skills/ai-writing-suite/_shared/host-profile-template.md:10:  are written out to `voice-profile.md` (the contract file `comms-polish`
skills/ai-writing-suite/_shared/host-profile-template.md:11:  reads).
skills/ai-writing-suite/_shared/host-profile-template.md:12:
skills/ai-writing-suite/_shared/host-profile-template.md:13:  HOW TO USE
skills/ai-writing-suite/_shared/host-profile-template.md:14:  ----------
skills/ai-writing-suite/_shared/host-profile-template.md:15:  Copy this file. Fill each field from the user's samples. Keep the SAME H2
skills/ai-writing-suite/_shared/host-profile-template.md:16:  headers as `voice-profile.md` — that file is the contract, this is its blank
skills/ai-writing-suite/_shared/host-profile-template.md:17:  twin. Renaming headers here breaks the hand-off.
skills/ai-writing-suite/_shared/host-profile-template.md:18:
skills/ai-writing-suite/_shared/host-profile-template.md:19:  THE ONE RULE
skills/ai-writing-suite/_shared/host-profile-template.md:20:  ------------
skills/ai-writing-suite/_shared/host-profile-template.md:21:  Every field needs sample evidence. No evidence -> write "Unknown — not enough
skills/ai-writing-suite/_shared/host-profile-template.md:22:  signal in samples". Do NOT invent a trait to fill a blank. A guessed profile
skills/ai-writing-suite/_shared/host-profile-template.md:23:  is worse than an empty one, because the reader skill will trust it.
skills/ai-writing-suite/_shared/host-profile-template.md:24:
skills/ai-writing-suite/_shared/host-profile-template.md:25:  CONFIDENCE
skills/ai-writing-suite/_shared/host-profile-template.md:26:  ----------
skills/ai-writing-suite/_shared/host-profile-template.md:27:  A trait counts only if it shows up 3+ times. One occurrence is noise, not a
skills/ai-writing-suite/_shared/host-profile-template.md:28:  habit. With <5 samples, mark Confidence = Low and fill conservatively.
skills/ai-writing-suite/_shared/host-profile-template.md:29:================================================================================
skills/ai-writing-suite/_shared/host-profile-template.md:30:-->
skills/ai-writing-suite/_shared/host-profile-template.md:31:
skills/ai-writing-suite/_shared/host-profile-template.md:32:# Host Profile — [author name]
skills/ai-writing-suite/_shared/host-profile-template.md:33:
skills/ai-writing-suite/_shared/host-profile-template.md:34:## Meta
skills/ai-writing-suite/_shared/host-profile-template.md:35:
skills/ai-writing-suite/_shared/host-profile-template.md:36:- **Author:** [name / id]
skills/ai-writing-suite/_shared/host-profile-template.md:37:- **Extracted:** [YYYY-MM-DD]
skills/ai-writing-suite/_shared/host-profile-template.md:38:- **Sample count:** [N]
skills/ai-writing-suite/_shared/host-profile-template.md:39:- **Sample sources:** [blog / LinkedIn / X / internal memos / other]
skills/ai-writing-suite/_shared/host-profile-template.md:40:- **Sample time span:** [earliest — latest]
skills/ai-writing-suite/_shared/host-profile-template.md:41:- **Confidence:** [Low (N<5) / Medium (5-10) / High (10+)]
skills/ai-writing-suite/_shared/host-profile-template.md:42:
skills/ai-writing-suite/_shared/host-profile-template.md:43:## Tone
skills/ai-writing-suite/_shared/host-profile-template.md:44:
skills/ai-writing-suite/_shared/host-profile-template.md:45:- [overall register in 1-2 sentences: e.g. direct / warm / dry / formal]
skills/ai-writing-suite/_shared/host-profile-template.md:46:
skills/ai-writing-suite/_shared/host-profile-template.md:47:> Evidence: [paste 1 sentence that shows the tone]
skills/ai-writing-suite/_shared/host-profile-template.md:48:
skills/ai-writing-suite/_shared/host-profile-template.md:49:## Sentence Length
skills/ai-writing-suite/_shared/host-profile-template.md:50:
skills/ai-writing-suite/_shared/host-profile-template.md:51:- **Average words/sentence:** [number]
skills/ai-writing-suite/_shared/host-profile-template.md:52:- **Short sentences (<10 words) share:** [%]
skills/ai-writing-suite/_shared/host-profile-template.md:53:- **Long sentences (>30 words) share:** [%]
skills/ai-writing-suite/_shared/host-profile-template.md:54:- **Rhythm habit:** [e.g. "short hook, then long qualifier"; or "Unknown"]
skills/ai-writing-suite/_shared/host-profile-template.md:55:
skills/ai-writing-suite/_shared/host-profile-template.md:56:> Evidence: [paste 1-2 sentences]
skills/ai-writing-suite/_shared/host-profile-template.md:57:
skills/ai-writing-suite/_shared/host-profile-template.md:58:## Vocabulary
skills/ai-writing-suite/_shared/host-profile-template.md:59:
skills/ai-writing-suite/_shared/host-profile-template.md:60:- **First person:** ["I" / "we" / subject-less / depends]
skills/ai-writing-suite/_shared/host-profile-template.md:61:- **Signature words:** [3-8 distinctive words, after stripping generic ones]
skills/ai-writing-suite/_shared/host-profile-template.md:62:- **Stock phrases / tics:** [list, or "none obvious"]
skills/ai-writing-suite/_shared/host-profile-template.md:63:- **Domain / in-group terms:** [3-5]
skills/ai-writing-suite/_shared/host-profile-template.md:64:
skills/ai-writing-suite/_shared/host-profile-template.md:65:## Vocabulary Do
skills/ai-writing-suite/_shared/host-profile-template.md:66:
skills/ai-writing-suite/_shared/host-profile-template.md:67:- [words / constructions the author actively reaches for]
skills/ai-writing-suite/_shared/host-profile-template.md:68:
skills/ai-writing-suite/_shared/host-profile-template.md:69:## Vocabulary Don't
skills/ai-writing-suite/_shared/host-profile-template.md:70:
skills/ai-writing-suite/_shared/host-profile-template.md:71:<!-- STRONGEST signal. Common words the author NEVER uses. -->
skills/ai-writing-suite/_shared/host-profile-template.md:72:- [forbidden words: e.g. "delve", "leverage", "unlock", hype punctuation]
skills/ai-writing-suite/_shared/host-profile-template.md:73:
skills/ai-writing-suite/_shared/host-profile-template.md:74:## Signature Moves
skills/ai-writing-suite/_shared/host-profile-template.md:75:
skills/ai-writing-suite/_shared/host-profile-template.md:76:- [characteristic ways they build a point: e.g. "not X but Y" reframes, leads
skills/ai-writing-suite/_shared/host-profile-template.md:77:  with a number, ends on a consequence]
skills/ai-writing-suite/_shared/host-profile-template.md:78:
skills/ai-writing-suite/_shared/host-profile-template.md:79:## Punctuation & Formatting
skills/ai-writing-suite/_shared/host-profile-template.md:80:
skills/ai-writing-suite/_shared/host-profile-template.md:81:- **Period vs comma:** [period-heavy / comma-heavy / balanced]
skills/ai-writing-suite/_shared/host-profile-template.md:82:- **Em-dash density:** [often / occasional / never]
skills/ai-writing-suite/_shared/host-profile-template.md:83:- **Ellipsis / exclamation:** [density]
skills/ai-writing-suite/_shared/host-profile-template.md:84:- **Lists:** [uses bullets? numbered steps?]
skills/ai-writing-suite/_shared/host-profile-template.md:85:- **Emoji:** [yes / no / which ones / position]
skills/ai-writing-suite/_shared/host-profile-template.md:86:
skills/ai-writing-suite/_shared/host-profile-template.md:87:## Openings & Closings
skills/ai-writing-suite/_shared/host-profile-template.md:88:
skills/ai-writing-suite/_shared/host-profile-template.md:89:- **Opening habit:** [scene / claim / question / number / contrarian / other]
skills/ai-writing-suite/_shared/host-profile-template.md:90:- **Closing habit:** [hook / consequence / open question / trails off / other]
skills/ai-writing-suite/_shared/host-profile-template.md:91:
skills/ai-writing-suite/_shared/host-profile-template.md:92:> Evidence (open): "[paste original opening]"
skills/ai-writing-suite/_shared/host-profile-template.md:93:> Evidence (close): "[paste original closing]"
skills/ai-writing-suite/_shared/host-profile-template.md:94:
skills/ai-writing-suite/_shared/host-profile-template.md:95:## Uncertainty Style
skills/ai-writing-suite/_shared/host-profile-template.md:96:
skills/ai-writing-suite/_shared/host-profile-template.md:97:- [quantified ("70% sure") / blunt ("I don't know") / hedged ("perhaps") / avoids]
skills/ai-writing-suite/_shared/host-profile-template.md:98:
skills/ai-writing-suite/_shared/host-profile-template.md:99:> Evidence: [paste 1 sentence]
skills/ai-writing-suite/_shared/host-profile-template.md:100:
skills/ai-writing-suite/_shared/host-profile-template.md:101:## Things To Avoid
skills/ai-writing-suite/_shared/host-profile-template.md:102:
skills/ai-writing-suite/_shared/host-profile-template.md:103:- [author-specific anti-patterns beyond the forbidden word list: registers,
skills/ai-writing-suite/_shared/host-profile-template.md:104:  structures, moves that read as "not them"]
skills/ai-writing-suite/_shared/host-profile-template.md:105:
skills/ai-writing-suite/_shared/host-profile-template.md:106:## Scope & Calibration
skills/ai-writing-suite/_shared/host-profile-template.md:107:
skills/ai-writing-suite/_shared/host-profile-template.md:108:- **Applies to:** [genres these samples cover]
skills/ai-writing-suite/_shared/host-profile-template.md:109:- **Re-calibrate for:** [genres not covered — flag so the reader doesn't misapply]
skills/ai-writing-suite/_shared/host-profile-template.md:110:
skills/ai-writing-suite/_shared/host-profile-template.md:111:## Changelog
skills/ai-writing-suite/_shared/host-profile-template.md:112:
skills/ai-writing-suite/_shared/host-profile-template.md:113:- [YYYY-MM-DD] First created from N samples.
skills/ai-writing-suite/_shared/host-profile-template.md:114:- [YYYY-MM-DD] [added/removed trait X — reason: user said "X felt off"]
skills/ai-writing-suite/_shared/host-profile-template.md:115:
skills/ai-writing-suite/_shared/host-profile-template.md:116:<!--
skills/ai-writing-suite/_shared/host-profile-template.md:117:  ATTRIBUTION
skills/ai-writing-suite/_shared/host-profile-template.md:118:  -----------
skills/ai-writing-suite/_shared/host-profile-template.md:119:  Adapted from weijt606/anti-vibe-writing host-profile-template.md (MIT):
skills/ai-writing-suite/_shared/host-profile-template.md:120:  ported from Chinese to English and aligned to the suite's voice-profile.md
skills/ai-writing-suite/_shared/host-profile-template.md:121:  field contract. Do's/Don'ts framing borrowed from
skills/ai-writing-suite/_shared/host-profile-template.md:122:  donghuixin/AI-Vibe-Writing-Skills 1_style_extractor.md (MIT). Full copyright
skills/ai-writing-suite/_shared/host-profile-template.md:123:  lines in the suite NOTICE.md. Bilingual (Chinese) path = v2 per design D-scope.
skills/ai-writing-suite/_shared/host-profile-template.md:124:-->
skills/ai-writing-suite/_shared/knowledge/structure.md:1:# Structure — lead with the point, then support it
skills/ai-writing-suite/_shared/knowledge/structure.md:2:
skills/ai-writing-suite/_shared/knowledge/structure.md:3:> **Generic best-practice entry.** Distilled from the four MIT reference repos
skills/ai-writing-suite/_shared/knowledge/structure.md:4:> (see `Sources`). Open-source KB; company forks swap via the same slot
skills/ai-writing-suite/_shared/knowledge/structure.md:5:> (`README.md`).
skills/ai-writing-suite/_shared/knowledge/structure.md:6:
skills/ai-writing-suite/_shared/knowledge/structure.md:7:## Principle
skills/ai-writing-suite/_shared/knowledge/structure.md:8:
skills/ai-writing-suite/_shared/knowledge/structure.md:9:Structure is the order in which ideas arrive. Most professional writing should be
skills/ai-writing-suite/_shared/knowledge/structure.md:10:**top-down**: state the conclusion first, then the reasons, then the detail. A
skills/ai-writing-suite/_shared/knowledge/structure.md:11:reader who stops after the first paragraph should still have the answer.
skills/ai-writing-suite/_shared/knowledge/structure.md:12:
skills/ai-writing-suite/_shared/knowledge/structure.md:13:## Moves
skills/ai-writing-suite/_shared/knowledge/structure.md:14:
skills/ai-writing-suite/_shared/knowledge/structure.md:15:- **BLUF — bottom line up front.** Open with the decision, result, or ask. Don't
skills/ai-writing-suite/_shared/knowledge/structure.md:16:  make the reader earn the point by reading to the end.
skills/ai-writing-suite/_shared/knowledge/structure.md:17:- **One idea per paragraph.** A paragraph that changes topic mid-way should be
skills/ai-writing-suite/_shared/knowledge/structure.md:18:  two paragraphs.
skills/ai-writing-suite/_shared/knowledge/structure.md:19:- **Use the natural number of points.** Don't force everything into a "rule of
skills/ai-writing-suite/_shared/knowledge/structure.md:20:  three." Sometimes the answer is one reason; sometimes four. Forced triads read
skills/ai-writing-suite/_shared/knowledge/structure.md:21:  as machine-generated.
skills/ai-writing-suite/_shared/knowledge/structure.md:22:- **Headings describe content, not ceremony.** "Migration steps" beats
skills/ai-writing-suite/_shared/knowledge/structure.md:23:  "Challenges and Legacy" or "The Road Ahead" — stock headings signal filler.
skills/ai-writing-suite/_shared/knowledge/structure.md:24:- **Match shape to channel.** A tweet is one hook, no headers. A memo is BLUF +
skills/ai-writing-suite/_shared/knowledge/structure.md:25:  sections. A README is task-ordered. Don't pour memo structure into a tweet.
skills/ai-writing-suite/_shared/knowledge/structure.md:26:
skills/ai-writing-suite/_shared/knowledge/structure.md:27:## Before / After
skills/ai-writing-suite/_shared/knowledge/structure.md:28:
skills/ai-writing-suite/_shared/knowledge/structure.md:29:- **Before:** In this document we will explore several considerations. First, we
skills/ai-writing-suite/_shared/knowledge/structure.md:30:  provide background. [...three paragraphs...] Therefore, we recommend Option B.
skills/ai-writing-suite/_shared/knowledge/structure.md:31:- **After:** Recommendation: ship Option B. It is 2x cheaper and reuses the
skills/ai-writing-suite/_shared/knowledge/structure.md:32:  existing pipeline. Background and the two rejected options follow.
skills/ai-writing-suite/_shared/knowledge/structure.md:33:
skills/ai-writing-suite/_shared/knowledge/structure.md:34:## When this matters most
skills/ai-writing-suite/_shared/knowledge/structure.md:35:
skills/ai-writing-suite/_shared/knowledge/structure.md:36:Decision memos, proposals, exec updates. The reader's time budget is short and
skills/ai-writing-suite/_shared/knowledge/structure.md:37:front-loaded — spend the first sentence on the answer.
skills/ai-writing-suite/_shared/knowledge/structure.md:38:
skills/ai-writing-suite/_shared/knowledge/structure.md:39:## Sources
skills/ai-writing-suite/_shared/knowledge/structure.md:40:
skills/ai-writing-suite/_shared/knowledge/structure.md:41:- `nature` (`nature-writing` section-moves: argument-first drafting)
skills/ai-writing-suite/_shared/knowledge/structure.md:42:- `blader` / `aboudjem` (rule-of-three, formulaic-challenges, over-structure tells)
skills/ai-writing-suite/_shared/knowledge/structure.md:43:- `anti-vibe` (scenario-presets: shape per channel)
skills/ai-writing-suite/_shared/self-improvement.md:1:<!--
skills/ai-writing-suite/_shared/self-improvement.md:2:================================================================================
skills/ai-writing-suite/_shared/self-improvement.md:3:  self-improvement.md  —  HUMAN-GATED SELF-IMPROVEMENT PROTOCOL (Layer 2)
skills/ai-writing-suite/_shared/self-improvement.md:4:================================================================================
skills/ai-writing-suite/_shared/self-improvement.md:5:
skills/ai-writing-suite/_shared/self-improvement.md:6:  WHAT THIS IS
skills/ai-writing-suite/_shared/self-improvement.md:7:  ------------
skills/ai-writing-suite/_shared/self-improvement.md:8:  The suite-wide lifecycle hook that lets the skills get *better over time*
skills/ai-writing-suite/_shared/self-improvement.md:9:  WITHOUT silently rewriting themselves. It is referenced (not copied) by every
skills/ai-writing-suite/_shared/self-improvement.md:10:  sub-skill that opts in — in v1 that is `comms-polish` and `voice-onboard`.
skills/ai-writing-suite/_shared/self-improvement.md:11:
skills/ai-writing-suite/_shared/self-improvement.md:12:  THE ONE RULE (read this before anything else)
skills/ai-writing-suite/_shared/self-improvement.md:13:  ---------------------------------------------
skills/ai-writing-suite/_shared/self-improvement.md:14:  This hook may only ever do TWO things autonomously:
skills/ai-writing-suite/_shared/self-improvement.md:15:    1. READ side files at the start of a session (voice-profile + learned-rules).
skills/ai-writing-suite/_shared/self-improvement.md:16:    2. PROPOSE candidate rules at the end of a session.
skills/ai-writing-suite/_shared/self-improvement.md:17:  It MUST NOT write anything until the user explicitly approves. Approved rules
skills/ai-writing-suite/_shared/self-improvement.md:18:  go to ONE place: `learned-rules.md` (append-only). Core SKILL.md logic is NEVER
skills/ai-writing-suite/_shared/self-improvement.md:19:  auto-edited. This is the anti-drift guarantee — see plan §6 (D6) and risk R3.
skills/ai-writing-suite/_shared/self-improvement.md:20:
skills/ai-writing-suite/_shared/self-improvement.md:21:  WHY (product-owner framing)
skills/ai-writing-suite/_shared/self-improvement.md:22:  ---------------------------
skills/ai-writing-suite/_shared/self-improvement.md:23:  Treat learned rules like a feature flag rollout, not a model that retrains
skills/ai-writing-suite/_shared/self-improvement.md:24:  itself on its own outputs. An ungated self-improving system feeds on its own
skills/ai-writing-suite/_shared/self-improvement.md:25:  predictions and drifts — the writing equivalent of a recommender that keeps
skills/ai-writing-suite/_shared/self-improvement.md:26:  recommending what it already recommended. The human gate is the holdout check:
skills/ai-writing-suite/_shared/self-improvement.md:27:  no rule ships to the "production" rule set until a person signs off, and (in
skills/ai-writing-suite/_shared/self-improvement.md:28:  Layer 3) until an eval measures it.
skills/ai-writing-suite/_shared/self-improvement.md:29:================================================================================
skills/ai-writing-suite/_shared/self-improvement.md:30:-->
skills/ai-writing-suite/_shared/self-improvement.md:31:
skills/ai-writing-suite/_shared/self-improvement.md:32:# Self-Improvement Protocol (human-gated, append-only)
skills/ai-writing-suite/_shared/self-improvement.md:33:
skills/ai-writing-suite/_shared/self-improvement.md:34:This is the shared spec for the suite's self-improvement hook. Sub-skills point
skills/ai-writing-suite/_shared/self-improvement.md:35:here instead of restating it, so the gate behaves identically everywhere.
skills/ai-writing-suite/_shared/self-improvement.md:36:
skills/ai-writing-suite/_shared/self-improvement.md:37:## The contract in one line
skills/ai-writing-suite/_shared/self-improvement.md:38:
skills/ai-writing-suite/_shared/self-improvement.md:39:Read learned rules on start. Propose new ones on end. Append only what the
skills/ai-writing-suite/_shared/self-improvement.md:40:user explicitly approves. Never auto-edit core skill logic.
skills/ai-writing-suite/_shared/self-improvement.md:41:
skills/ai-writing-suite/_shared/self-improvement.md:42:## Lifecycle
skills/ai-writing-suite/_shared/self-improvement.md:43:
skills/ai-writing-suite/_shared/self-improvement.md:44:### ON START — read the side files (no writes)
skills/ai-writing-suite/_shared/self-improvement.md:45:
skills/ai-writing-suite/_shared/self-improvement.md:46:Before doing the sub-skill's actual work, read these two files if they exist:
skills/ai-writing-suite/_shared/self-improvement.md:47:
skills/ai-writing-suite/_shared/self-improvement.md:48:1. `_shared/voice-profile.md` — the learned voice (owned by `voice-onboard`).
skills/ai-writing-suite/_shared/self-improvement.md:49:2. `_shared/learned-rules.md` — approved, human-gated improvements (this file's
skills/ai-writing-suite/_shared/self-improvement.md:50:   sibling). Apply any rule whose `status: active` and whose scope matches the
skills/ai-writing-suite/_shared/self-improvement.md:51:   current task (e.g. a rule scoped to `comms-polish` is ignored by
skills/ai-writing-suite/_shared/self-improvement.md:52:   `voice-onboard`).
skills/ai-writing-suite/_shared/self-improvement.md:53:
skills/ai-writing-suite/_shared/self-improvement.md:54:Degrade gracefully: if either file is missing, do not error and do not block.
skills/ai-writing-suite/_shared/self-improvement.md:55:Note briefly that it was absent and continue with defaults. These are bias
skills/ai-writing-suite/_shared/self-improvement.md:56:signals, never hard dependencies (same posture as comms-polish voice matching).
skills/ai-writing-suite/_shared/self-improvement.md:57:
skills/ai-writing-suite/_shared/self-improvement.md:58:### ON END — propose candidate rule(s), then STOP
skills/ai-writing-suite/_shared/self-improvement.md:59:
skills/ai-writing-suite/_shared/self-improvement.md:60:After completing the session's work, look back at what happened and ask: *did a
skills/ai-writing-suite/_shared/self-improvement.md:61:repeatable correction surface that the catalog / profile / checklist does not
skills/ai-writing-suite/_shared/self-improvement.md:62:already cover?* Good candidates come from:
skills/ai-writing-suite/_shared/self-improvement.md:63:
skills/ai-writing-suite/_shared/self-improvement.md:64:- A correction the user made that would recur ("I always cut that opener").
skills/ai-writing-suite/_shared/self-improvement.md:65:- A pattern the existing catalog missed or over-flagged.
skills/ai-writing-suite/_shared/self-improvement.md:66:- A voice-extraction judgment the user overrode.
skills/ai-writing-suite/_shared/self-improvement.md:67:
skills/ai-writing-suite/_shared/self-improvement.md:68:If nothing repeatable surfaced, say so and propose nothing. Do not manufacture a
skills/ai-writing-suite/_shared/self-improvement.md:69:rule to look productive — a noisy rule log is worse than a short one.
skills/ai-writing-suite/_shared/self-improvement.md:70:
skills/ai-writing-suite/_shared/self-improvement.md:71:If a candidate exists, **present it to the user** in the proposed-rule shape
skills/ai-writing-suite/_shared/self-improvement.md:72:(see `learned-rules.md` for the field schema) with:
skills/ai-writing-suite/_shared/self-improvement.md:73:
skills/ai-writing-suite/_shared/self-improvement.md:74:- the proposed rule text,
skills/ai-writing-suite/_shared/self-improvement.md:75:- a one-line rationale grounded in *this* session (cite what happened),
skills/ai-writing-suite/_shared/self-improvement.md:76:- the scope it would apply to (`comms-polish`, `voice-onboard`, or `all`),
skills/ai-writing-suite/_shared/self-improvement.md:77:- a note that in Layer 3 this rule will be eval-measured before it counts as
skills/ai-writing-suite/_shared/self-improvement.md:78:  trusted (do not build or run that eval here — just reference it).
skills/ai-writing-suite/_shared/self-improvement.md:79:
skills/ai-writing-suite/_shared/self-improvement.md:80:Then **stop and wait.** This is the gate.
skills/ai-writing-suite/_shared/self-improvement.md:81:
skills/ai-writing-suite/_shared/self-improvement.md:82:### ON APPROVAL — append, nothing else
skills/ai-writing-suite/_shared/self-improvement.md:83:
skills/ai-writing-suite/_shared/self-improvement.md:84:Only on an explicit "yes" / "approve" / "add it" from the user:
skills/ai-writing-suite/_shared/self-improvement.md:85:
skills/ai-writing-suite/_shared/self-improvement.md:86:- Append ONE entry to `_shared/learned-rules.md` using the documented format
skills/ai-writing-suite/_shared/self-improvement.md:87:  (id, rule, rationale, scope, date, status, source).
skills/ai-writing-suite/_shared/self-improvement.md:88:- Set `status: proposed` until Layer 3's eval has measured it; the user may say
skills/ai-writing-suite/_shared/self-improvement.md:89:  "make it active" to promote a rule they trust without waiting.
skills/ai-writing-suite/_shared/self-improvement.md:90:- Stamp the date and a short source-session note so the log stays auditable.
skills/ai-writing-suite/_shared/self-improvement.md:91:- Do NOT touch any SKILL.md, the pattern catalog, or the voice profile schema.
skills/ai-writing-suite/_shared/self-improvement.md:92:  Approved rules live ONLY in `learned-rules.md`.
skills/ai-writing-suite/_shared/self-improvement.md:93:
skills/ai-writing-suite/_shared/self-improvement.md:94:If the user says no, or edits the wording, follow their version exactly. Never
skills/ai-writing-suite/_shared/self-improvement.md:95:append a rule they did not approve. Never append more than they approved.
skills/ai-writing-suite/_shared/self-improvement.md:96:
skills/ai-writing-suite/_shared/self-improvement.md:97:## What this hook must NEVER do
skills/ai-writing-suite/_shared/self-improvement.md:98:
skills/ai-writing-suite/_shared/self-improvement.md:99:- Auto-edit core logic (any `SKILL.md`, `_shared/patterns/`, the voice-profile
skills/ai-writing-suite/_shared/self-improvement.md:100:  schema headers). Out of bounds, always.
skills/ai-writing-suite/_shared/self-improvement.md:101:- Append a rule without explicit approval.
skills/ai-writing-suite/_shared/self-improvement.md:102:- Silently overwrite or rewrite existing learned rules — the log is append-only.
skills/ai-writing-suite/_shared/self-improvement.md:103:  Superseding a rule = append a new entry that references the old id and set the
skills/ai-writing-suite/_shared/self-improvement.md:104:  old one's `status: retired` (a status edit on its own line, not a rewrite of
skills/ai-writing-suite/_shared/self-improvement.md:105:  its rule text).
skills/ai-writing-suite/_shared/self-improvement.md:106:
skills/ai-writing-suite/_shared/self-improvement.md:107:## Degradation on RovoDev (and other constrained hosts) — R2
skills/ai-writing-suite/_shared/self-improvement.md:108:
skills/ai-writing-suite/_shared/self-improvement.md:109:RovoDev has no skill auto-triggering and a reduced toolset (Read/Write/Edit/
skills/ai-writing-suite/_shared/self-improvement.md:110:Bash/Grep, no Skill tool). This protocol is built to survive that:
skills/ai-writing-suite/_shared/self-improvement.md:111:
skills/ai-writing-suite/_shared/self-improvement.md:112:- **No auto-trigger needed.** The hook is plain instructions inside a SKILL.md,
skills/ai-writing-suite/_shared/self-improvement.md:113:  not an event listener. ON START / ON END run whenever the sub-skill runs,
skills/ai-writing-suite/_shared/self-improvement.md:114:  however the sub-skill was invoked (explicit invocation on RovoDev).
skills/ai-writing-suite/_shared/self-improvement.md:115:- **File-read only on start.** Reading `voice-profile.md` + `learned-rules.md`
skills/ai-writing-suite/_shared/self-improvement.md:116:  uses Read/Grep — available everywhere. No MCP, no special tooling.
skills/ai-writing-suite/_shared/self-improvement.md:117:- **Append uses Edit/Write.** Adding one entry to `learned-rules.md` needs only
skills/ai-writing-suite/_shared/self-improvement.md:118:  Edit (or Write) — both present on RovoDev.
skills/ai-writing-suite/_shared/self-improvement.md:119:- **The gate is conversational, not tool-based.** "Propose → user says yes →
skills/ai-writing-suite/_shared/self-improvement.md:120:  append" works in any chat loop and needs no Skill/Task/Agent machinery.
skills/ai-writing-suite/_shared/self-improvement.md:121:- If even file writes are unavailable, degrade to: print the proposed rule entry
skills/ai-writing-suite/_shared/self-improvement.md:122:  and ask the user to paste it into `learned-rules.md` themselves. The gate and
skills/ai-writing-suite/_shared/self-improvement.md:123:  the append-only discipline still hold.
skills/ai-writing-suite/evals/fixtures/fixtures.json:1:{
skills/ai-writing-suite/evals/fixtures/fixtures.json:2:  "_doc": "Before/after LLM-judge fixtures across 4 genres (tweet/linkedin/readme/memo). Each fixture: an AI-shaped `before`, a good human `after`, and what we expect. `before_band_min`/`before_band_max`/`after_band_max` are detector score-band expectations (mechanical, deterministic regression guards bracketing the observed score). `rubric_focus` lists which rubric dimensions the LLM judge should weigh. Difficulty is calibrated so a NAIVE baseline (flag-if-detector-score >= baseline_threshold) misses ~30-40% of the `before` items: the `subtle` ones are AI-written but score LOW because they avoid vocabulary tells and lean on structural/rhythm tells a flat threshold underweights. See README calibration section.",
skills/ai-writing-suite/evals/fixtures/fixtures.json:3:  "baseline_threshold": 14,
skills/ai-writing-suite/evals/fixtures/fixtures.json:4:  "fixtures": [
skills/ai-writing-suite/evals/fixtures/fixtures.json:5:    {
skills/ai-writing-suite/evals/fixtures/fixtures.json:6:      "id": "tweet-01-obvious",
skills/ai-writing-suite/evals/fixtures/fixtures.json:7:      "genre": "tweet",
skills/ai-writing-suite/evals/fixtures/fixtures.json:8:      "difficulty": "obvious",
skills/ai-writing-suite/evals/fixtures/fixtures.json:9:      "before": "In today's ever-evolving landscape, we're thrilled to delve into a game-changing paradigm. This seamless, robust solution will revolutionize how you work. The future looks bright! 🚀 #innovation #growth #tech #startup #ai #future #buildinpublic",
skills/ai-writing-suite/evals/fixtures/fixtures.json:10:      "after": "Shipped the new import flow today. Cut setup from 11 steps to 3. Early users went from 40% drop-off to 12%.",
skills/ai-writing-suite/evals/fixtures/fixtures.json:11:      "before_band_min": 45,
skills/ai-writing-suite/evals/fixtures/fixtures.json:12:      "after_band_max": 20,
skills/ai-writing-suite/evals/fixtures/fixtures.json:13:      "rubric_focus": [
skills/ai-writing-suite/evals/fixtures/fixtures.json:14:        "meaning_preserved",
skills/ai-writing-suite/evals/fixtures/fixtures.json:15:        "tells_removed",
skills/ai-writing-suite/evals/fixtures/fixtures.json:16:        "voice_kept",
skills/ai-writing-suite/evals/fixtures/fixtures.json:17:        "no_fabrication"
skills/ai-writing-suite/evals/fixtures/fixtures.json:18:      ],
skills/ai-writing-suite/evals/fixtures/fixtures.json:19:      "expect_baseline": "catch"
skills/ai-writing-suite/evals/fixtures/fixtures.json:20:    },
skills/ai-writing-suite/evals/fixtures/fixtures.json:21:    {
skills/ai-writing-suite/evals/fixtures/fixtures.json:22:      "id": "tweet-02-subtle",
skills/ai-writing-suite/evals/fixtures/fixtures.json:23:      "genre": "tweet",
skills/ai-writing-suite/evals/fixtures/fixtures.json:24:      "difficulty": "subtle",
skills/ai-writing-suite/evals/fixtures/fixtures.json:25:      "before": "Spent the week thinking about retrieval. Keyword search is underrated. Vector search is overhyped. Most teams reach for embeddings when an index would do. Worth sitting with that.",
skills/ai-writing-suite/evals/fixtures/fixtures.json:26:      "after": "Spent the week on retrieval. Keyword search beat our embedding setup on the eval — cheaper, and recall was 4 points higher. We were reaching for vectors out of habit.",
skills/ai-writing-suite/evals/fixtures/fixtures.json:27:      "before_band_max": 20,
skills/ai-writing-suite/evals/fixtures/fixtures.json:28:      "after_band_max": 20,
skills/ai-writing-suite/evals/fixtures/fixtures.json:29:      "rubric_focus": [
skills/ai-writing-suite/evals/fixtures/fixtures.json:30:        "specificity_added",
skills/ai-writing-suite/evals/fixtures/fixtures.json:31:        "negative_parallelism_removed",
skills/ai-writing-suite/evals/fixtures/fixtures.json:32:        "no_fabrication"
skills/ai-writing-suite/evals/fixtures/fixtures.json:33:      ],
skills/ai-writing-suite/evals/fixtures/fixtures.json:34:      "expect_baseline": "miss",
skills/ai-writing-suite/evals/fixtures/fixtures.json:35:      "subtle_tell": "negative parallelism (X is underrated / Y is overhyped), vague 'worth sitting with that' closer, zero specifics — all AI structural tells that carry NO vocabulary words, so a flat detector threshold scores it low and misses it."
skills/ai-writing-suite/evals/fixtures/fixtures.json:36:    },
skills/ai-writing-suite/evals/fixtures/fixtures.json:37:    {
skills/ai-writing-suite/evals/fixtures/fixtures.json:38:      "id": "linkedin-01-obvious",
skills/ai-writing-suite/evals/fixtures/fixtures.json:39:      "genre": "linkedin",
skills/ai-writing-suite/evals/fixtures/fixtures.json:40:      "difficulty": "obvious",
skills/ai-writing-suite/evals/fixtures/fixtures.json:41:      "before": "I recently had the pleasure of attending a pivotal conference. It was truly a transformative experience that underscored the importance of fostering meaningful connections. Moreover, the keynote was a testament to the power of innovation. As we navigate this dynamic ecosystem, let's embrace the journey. What's next? Only time will tell.",
skills/ai-writing-suite/evals/fixtures/fixtures.json:42:      "after": "Went to the data conf last week. One talk stuck with me: a team at Stripe cut their feature pipeline from 6 hours to 40 minutes by dropping a caching layer nobody had questioned in two years. Sometimes the win is deleting code.",
skills/ai-writing-suite/evals/fixtures/fixtures.json:43:      "before_band_min": 28,
skills/ai-writing-suite/evals/fixtures/fixtures.json:44:      "after_band_max": 20,
skills/ai-writing-suite/evals/fixtures/fixtures.json:45:      "rubric_focus": [
skills/ai-writing-suite/evals/fixtures/fixtures.json:46:        "meaning_preserved",
skills/ai-writing-suite/evals/fixtures/fixtures.json:47:        "tells_removed",
skills/ai-writing-suite/evals/fixtures/fixtures.json:48:        "specificity_added",
skills/ai-writing-suite/evals/fixtures/fixtures.json:49:        "no_fabrication"
skills/ai-writing-suite/evals/fixtures/fixtures.json:50:      ],
skills/ai-writing-suite/evals/fixtures/fixtures.json:51:      "expect_baseline": "catch"
skills/ai-writing-suite/evals/fixtures/fixtures.json:52:    },
skills/ai-writing-suite/evals/fixtures/fixtures.json:53:    {
skills/ai-writing-suite/evals/fixtures/fixtures.json:54:      "id": "linkedin-02-subtle",
skills/ai-writing-suite/evals/fixtures/fixtures.json:55:      "genre": "linkedin",
skills/ai-writing-suite/evals/fixtures/fixtures.json:56:      "difficulty": "subtle",
skills/ai-writing-suite/evals/fixtures/fixtures.json:57:      "before": "Three things I learned shipping our first ML model.\n\nFirst, data quality matters more than model choice.\n\nSecond, stakeholders care about latency, not accuracy.\n\nThird, the simplest baseline is often hard to beat.\n\nWhat would you add?",
skills/ai-writing-suite/evals/fixtures/fixtures.json:58:      "after": "We shipped our first ranking model last month and I was wrong about almost everything going in. I thought the model would be the hard part. It wasn't — a week of cleaning label noise moved offline NDCG more than any architecture change. And the thing the PM actually cared about was p99 latency, which I'd barely measured.",
skills/ai-writing-suite/evals/fixtures/fixtures.json:59:      "before_band_max": 20,
skills/ai-writing-suite/evals/fixtures/fixtures.json:60:      "after_band_max": 20,
skills/ai-writing-suite/evals/fixtures/fixtures.json:61:      "rubric_focus": [
skills/ai-writing-suite/evals/fixtures/fixtures.json:62:        "rule_of_three_removed",
skills/ai-writing-suite/evals/fixtures/fixtures.json:63:        "specificity_added",
skills/ai-writing-suite/evals/fixtures/fixtures.json:64:        "engagement_hook_removed",
skills/ai-writing-suite/evals/fixtures/fixtures.json:65:        "no_fabrication"
skills/ai-writing-suite/evals/fixtures/fixtures.json:66:      ],
skills/ai-writing-suite/evals/fixtures/fixtures.json:67:      "expect_baseline": "miss",
skills/ai-writing-suite/evals/fixtures/fixtures.json:68:      "subtle_tell": "rule-of-three list scaffolding + 'What would you add?' engagement-bait closer. Reads clean to a vocabulary detector (no tier-1 words) so a flat threshold misses it; an LLM judge keyed to STRUCTURE catches it."
skills/ai-writing-suite/evals/fixtures/fixtures.json:69:    },
skills/ai-writing-suite/evals/fixtures/fixtures.json:70:    {
skills/ai-writing-suite/evals/fixtures/fixtures.json:71:      "id": "readme-01-obvious",
skills/ai-writing-suite/evals/fixtures/fixtures.json:72:      "genre": "readme",
skills/ai-writing-suite/evals/fixtures/fixtures.json:73:      "difficulty": "obvious",
skills/ai-writing-suite/evals/fixtures/fixtures.json:74:      "before": "## Overview\n\nThis comprehensive, cutting-edge library leverages a robust architecture to seamlessly streamline your workflow. It empowers developers to harness the full potential of modern tooling. Whether you're a beginner or an expert, this powerful solution has you covered.",
skills/ai-writing-suite/evals/fixtures/fixtures.json:75:      "after": "## What this does\n\nParses CSV files up to 2GB without loading them into memory. Streams rows, so it works on machines with 512MB of RAM. No dependencies outside the standard library.",
skills/ai-writing-suite/evals/fixtures/fixtures.json:76:      "before_band_min": 20,
skills/ai-writing-suite/evals/fixtures/fixtures.json:77:      "after_band_max": 20,
skills/ai-writing-suite/evals/fixtures/fixtures.json:78:      "rubric_focus": [
skills/ai-writing-suite/evals/fixtures/fixtures.json:79:        "meaning_preserved",
skills/ai-writing-suite/evals/fixtures/fixtures.json:80:        "tells_removed",
skills/ai-writing-suite/evals/fixtures/fixtures.json:81:        "specificity_added"
skills/ai-writing-suite/evals/fixtures/fixtures.json:82:      ],
skills/ai-writing-suite/evals/fixtures/fixtures.json:83:      "expect_baseline": "catch"
skills/ai-writing-suite/evals/fixtures/fixtures.json:84:    },
skills/ai-writing-suite/evals/fixtures/fixtures.json:85:    {
skills/ai-writing-suite/evals/fixtures/fixtures.json:86:      "id": "readme-02-subtle",
skills/ai-writing-suite/evals/fixtures/fixtures.json:87:      "genre": "readme",
skills/ai-writing-suite/evals/fixtures/fixtures.json:88:      "difficulty": "subtle",
skills/ai-writing-suite/evals/fixtures/fixtures.json:89:      "before": "## Installation\n\nTo get started, simply install the package. Once installed, you can begin using it right away. The setup process is designed to be straightforward and intuitive, ensuring a smooth onboarding experience for users of all skill levels.",
skills/ai-writing-suite/evals/fixtures/fixtures.json:90:      "after": "## Installation\n\n```\npip install fastcsv\n```\n\nPython 3.9+. No other dependencies.",
skills/ai-writing-suite/evals/fixtures/fixtures.json:91:      "before_band_max": 20,
skills/ai-writing-suite/evals/fixtures/fixtures.json:92:      "after_band_max": 20,
skills/ai-writing-suite/evals/fixtures/fixtures.json:93:      "rubric_focus": [
skills/ai-writing-suite/evals/fixtures/fixtures.json:94:        "filler_removed",
skills/ai-writing-suite/evals/fixtures/fixtures.json:95:        "specificity_added",
skills/ai-writing-suite/evals/fixtures/fixtures.json:96:        "meaning_preserved"
skills/ai-writing-suite/evals/fixtures/fixtures.json:97:      ],
skills/ai-writing-suite/evals/fixtures/fixtures.json:98:      "expect_baseline": "miss",
skills/ai-writing-suite/evals/fixtures/fixtures.json:99:      "subtle_tell": "all filler, zero content ('simply', 'right away', 'smooth onboarding experience') but no flagged vocabulary — it's empty calories that a word-list detector rates clean. An LLM judge measuring information density catches it."
skills/ai-writing-suite/evals/fixtures/fixtures.json:100:    },
skills/ai-writing-suite/evals/fixtures/fixtures.json:101:    {
skills/ai-writing-suite/evals/fixtures/fixtures.json:102:      "id": "memo-01-obvious",
skills/ai-writing-suite/evals/fixtures/fixtures.json:103:      "genre": "memo",
skills/ai-writing-suite/evals/fixtures/fixtures.json:104:      "difficulty": "obvious",
skills/ai-writing-suite/evals/fixtures/fixtures.json:105:      "before": "It is important to note that, as we move forward, we must delve into the intricacies of our strategy. Experts believe that fostering a culture of innovation is paramount. Furthermore, this pivotal initiative will undoubtedly elevate our position. Let's break this down step by step to ensure a holistic approach.",
skills/ai-writing-suite/evals/fixtures/fixtures.json:106:      "after": "We're behind on Q3 targets by 14%. Two causes: the API migration slipped three weeks, and we lost two engineers. Proposed fix: pause the redesign, put everyone on migration, revisit the redesign in October.",
skills/ai-writing-suite/evals/fixtures/fixtures.json:107:      "before_band_min": 36,
skills/ai-writing-suite/evals/fixtures/fixtures.json:108:      "after_band_max": 20,
skills/ai-writing-suite/evals/fixtures/fixtures.json:109:      "rubric_focus": [
skills/ai-writing-suite/evals/fixtures/fixtures.json:110:        "meaning_preserved",
skills/ai-writing-suite/evals/fixtures/fixtures.json:111:        "tells_removed",
skills/ai-writing-suite/evals/fixtures/fixtures.json:112:        "vague_attribution_removed",
skills/ai-writing-suite/evals/fixtures/fixtures.json:113:        "specificity_added"
skills/ai-writing-suite/evals/fixtures/fixtures.json:114:      ],
skills/ai-writing-suite/evals/fixtures/fixtures.json:115:      "expect_baseline": "catch"
skills/ai-writing-suite/evals/fixtures/fixtures.json:116:    },
skills/ai-writing-suite/evals/fixtures/fixtures.json:117:    {
skills/ai-writing-suite/evals/fixtures/fixtures.json:118:      "id": "memo-02-subtle",
skills/ai-writing-suite/evals/fixtures/fixtures.json:119:      "genre": "memo",
skills/ai-writing-suite/evals/fixtures/fixtures.json:120:      "difficulty": "subtle",
skills/ai-writing-suite/evals/fixtures/fixtures.json:121:      "before": "While our current approach has served us well, there is room for improvement. It is important to note that research suggests engagement is trending in a positive direction. That said, we should remain mindful of potential headwinds, and a measured strategy could potentially position us well. Ultimately, this balanced approach will help us capture emerging opportunities going forward.",
skills/ai-writing-suite/evals/fixtures/fixtures.json:122:      "after": "Sign-ups are up 9% since the March redesign, but week-2 retention dropped from 31% to 24%. We're acquiring people the product doesn't keep. Before we spend more on acquisition, I want a week to dig into the retention cliff.",
skills/ai-writing-suite/evals/fixtures/fixtures.json:123:      "before_band_min": 12,
skills/ai-writing-suite/evals/fixtures/fixtures.json:124:      "before_band_max": 25,
skills/ai-writing-suite/evals/fixtures/fixtures.json:125:      "after_band_max": 20,
skills/ai-writing-suite/evals/fixtures/fixtures.json:126:      "rubric_focus": [
skills/ai-writing-suite/evals/fixtures/fixtures.json:127:        "false_concession_removed",
skills/ai-writing-suite/evals/fixtures/fixtures.json:128:        "hedge_stack_removed",
skills/ai-writing-suite/evals/fixtures/fixtures.json:129:        "specificity_added",
skills/ai-writing-suite/evals/fixtures/fixtures.json:130:        "no_fabrication"
skills/ai-writing-suite/evals/fixtures/fixtures.json:131:      ],
skills/ai-writing-suite/evals/fixtures/fixtures.json:132:      "expect_baseline": "catch",
skills/ai-writing-suite/evals/fixtures/fixtures.json:133:      "subtle_tell": "false concession ('served us well, but...'), hedge-stacking ('could potentially position us'), vague-attribution ('research suggests') with NO numbers. This is the BORDERLINE fixture: it scores ~15, just above the naive threshold, so the mechanical detector catches it but only barely — an LLM judge is still needed to confirm the rewrite added real specifics rather than just swapping words."
skills/ai-writing-suite/evals/fixtures/fixtures.json:134:    }
skills/ai-writing-suite/evals/fixtures/fixtures.json:135:  ]
skills/ai-writing-suite/evals/fixtures/fixtures.json:136:}
skills/ai-writing-suite/skills/comms-qa/SKILL.md:1:---
skills/ai-writing-suite/skills/comms-qa/SKILL.md:2:name: comms-qa
skills/ai-writing-suite/skills/comms-qa/SKILL.md:3:description: Answer questions from the knowledge base via a markdown mini-RAG over the pluggable KB. Not yet built - coming in v2.
skills/ai-writing-suite/skills/comms-qa/SKILL.md:4:---
skills/ai-writing-suite/skills/comms-qa/SKILL.md:5:
skills/ai-writing-suite/skills/comms-qa/SKILL.md:6:# comms-qa (placeholder)
skills/ai-writing-suite/skills/comms-qa/SKILL.md:7:
skills/ai-writing-suite/skills/comms-qa/SKILL.md:8:This sub-skill will answer questions from the knowledge base under
skills/ai-writing-suite/skills/comms-qa/SKILL.md:9:`_shared/knowledge/` -- a zero-dependency mini-RAG that navigates a markdown KB
skills/ai-writing-suite/skills/comms-qa/SKILL.md:10:through its `INDEX.md` and returns the relevant passage. In the open-source build
skills/ai-writing-suite/skills/comms-qa/SKILL.md:11:the KB is generic best practices; a company fork drops its own playbook into the
skills/ai-writing-suite/skills/comms-qa/SKILL.md:12:same slot. The KB slot is already seeded in this build (5 generic entries +
skills/ai-writing-suite/skills/comms-qa/SKILL.md:13:`INDEX.md` + a verified retrieval smoke path); the full question-answering
skills/ai-writing-suite/skills/comms-qa/SKILL.md:14:sub-skill that wraps it is **coming in v2.**
skills/ai-writing-suite/_shared/patterns/lexical-tells.md:1:# Lexical Tells (word-level)
skills/ai-writing-suite/_shared/patterns/lexical-tells.md:2:
skills/ai-writing-suite/_shared/patterns/lexical-tells.md:3:Word- and phrase-level habits. These are the easiest to spot and the easiest to
skills/ai-writing-suite/_shared/patterns/lexical-tells.md:4:over-correct, so flag in clusters, not in isolation: one "however" is nothing; a
skills/ai-writing-suite/_shared/patterns/lexical-tells.md:5:paragraph of delve + leverage + robust + tapestry is a confession.
skills/ai-writing-suite/_shared/patterns/lexical-tells.md:6:
skills/ai-writing-suite/_shared/patterns/lexical-tells.md:7:---
skills/ai-writing-suite/_shared/patterns/lexical-tells.md:8:
skills/ai-writing-suite/_shared/patterns/lexical-tells.md:9:### L1 — AI vocabulary words (tiered)
skills/ai-writing-suite/_shared/patterns/lexical-tells.md:10:
skills/ai-writing-suite/_shared/patterns/lexical-tells.md:11:- **Tell:** A small set of words appears 5-20x more often in post-2023 model
skills/ai-writing-suite/_shared/patterns/lexical-tells.md:12:  output than in human prose, and tends to cluster.
skills/ai-writing-suite/_shared/patterns/lexical-tells.md:13:- **Fix:** Replace with the plain word. Flag by tier, not on sight, to cut
skills/ai-writing-suite/_shared/patterns/lexical-tells.md:14:  false positives on second-language and technical writing.
skills/ai-writing-suite/_shared/patterns/lexical-tells.md:15:- **Sources:** avoid-ai (tiered table), blader (P7), aboudjem (§7), stop-slop.
skills/ai-writing-suite/_shared/patterns/lexical-tells.md:16:
skills/ai-writing-suite/_shared/patterns/lexical-tells.md:17:**Tier 1 — replace on sight** (appears ~5-20x more in AI text):
skills/ai-writing-suite/_shared/patterns/lexical-tells.md:18:delve / delve into, landscape (metaphor), tapestry, realm, paradigm, embark,
skills/ai-writing-suite/_shared/patterns/lexical-tells.md:19:beacon, testament to, robust, comprehensive, cutting-edge, leverage (verb),
skills/ai-writing-suite/_shared/patterns/lexical-tells.md:20:pivotal, underscores, meticulous, seamless, game-changer, utilize, nestled,
skills/ai-writing-suite/_shared/patterns/lexical-tells.md:21:vibrant, thriving, showcasing, deep dive / dive into, unpack, bustling,
skills/ai-writing-suite/_shared/patterns/lexical-tells.md:22:intricate / intricacies, ever-evolving, enduring, daunting, holistic,
skills/ai-writing-suite/_shared/patterns/lexical-tells.md:23:actionable, impactful, learnings, thought leader, best practices, at its core,
skills/ai-writing-suite/_shared/patterns/lexical-tells.md:24:synergy, interplay, in order to, due to the fact that, serves as, features
skills/ai-writing-suite/_shared/patterns/lexical-tells.md:25:(verb), boasts, commence, ascertain, endeavor, embrace (metaphor).
skills/ai-writing-suite/_shared/patterns/lexical-tells.md:26:
skills/ai-writing-suite/_shared/patterns/lexical-tells.md:27:**Tier 2 — flag when 2+ appear in one paragraph** (fine alone, suspect together):
skills/ai-writing-suite/_shared/patterns/lexical-tells.md:28:harness, navigate / navigating, foster, elevate, unleash, streamline, empower,
skills/ai-writing-suite/_shared/patterns/lexical-tells.md:29:bolster, spearhead, resonate, revolutionize, facilitate, underpin, nuanced,
skills/ai-writing-suite/_shared/patterns/lexical-tells.md:30:crucial, multifaceted, ecosystem (metaphor), myriad, plethora, encompass,
skills/ai-writing-suite/_shared/patterns/lexical-tells.md:31:catalyze, reimagine, galvanize, augment, cultivate, illuminate, elucidate,
skills/ai-writing-suite/_shared/patterns/lexical-tells.md:32:juxtapose, transformative, cornerstone, paramount, poised, burgeoning, nascent,
skills/ai-writing-suite/_shared/patterns/lexical-tells.md:33:quintessential, overarching, underpinning.
skills/ai-writing-suite/_shared/patterns/lexical-tells.md:34:
skills/ai-writing-suite/_shared/patterns/lexical-tells.md:35:**Tier 3 — flag only at high density** (normal words AI just overuses):
skills/ai-writing-suite/_shared/patterns/lexical-tells.md:36:significant(ly), innovative / innovation, effective(ly), dynamic, scalable,
skills/ai-writing-suite/_shared/patterns/lexical-tells.md:37:compelling, unprecedented, exceptional, remarkable, sophisticated, instrumental,
skills/ai-writing-suite/_shared/patterns/lexical-tells.md:38:world-class / state-of-the-art / best-in-class.
skills/ai-writing-suite/_shared/patterns/lexical-tells.md:39:
skills/ai-writing-suite/_shared/patterns/lexical-tells.md:40:> The tier idea comes from avoid-ai (adapted from brandonwise/humanizer vocab
skills/ai-writing-suite/_shared/patterns/lexical-tells.md:41:> research). Tiering is what keeps this rule from flattening legitimate prose.
skills/ai-writing-suite/_shared/patterns/lexical-tells.md:42:
skills/ai-writing-suite/_shared/patterns/lexical-tells.md:43:---
skills/ai-writing-suite/_shared/patterns/lexical-tells.md:44:
skills/ai-writing-suite/_shared/patterns/lexical-tells.md:45:### L2 — Copula avoidance
skills/ai-writing-suite/_shared/patterns/lexical-tells.md:46:
skills/ai-writing-suite/_shared/patterns/lexical-tells.md:47:- **Tell:** The model dodges plain "is" / "are" / "has" with fancier verbs to
skills/ai-writing-suite/_shared/patterns/lexical-tells.md:48:  sound sophisticated: serves as, stands as, marks, represents, boasts,
skills/ai-writing-suite/_shared/patterns/lexical-tells.md:49:  features, offers, presents.
skills/ai-writing-suite/_shared/patterns/lexical-tells.md:50:- **Fix:** Use the copula. "Gallery 825 *is* the exhibition space," not "Gallery
skills/ai-writing-suite/_shared/patterns/lexical-tells.md:51:  825 *serves as* the exhibition space." Only keep the fancier verb if it adds
skills/ai-writing-suite/_shared/patterns/lexical-tells.md:52:  real meaning.
skills/ai-writing-suite/_shared/patterns/lexical-tells.md:53:- **Sources:** blader (P8), aboudjem (§8), avoid-ai, anti-vibe.
skills/ai-writing-suite/_shared/patterns/lexical-tells.md:54:
skills/ai-writing-suite/_shared/patterns/lexical-tells.md:55:---
skills/ai-writing-suite/_shared/patterns/lexical-tells.md:56:
skills/ai-writing-suite/_shared/patterns/lexical-tells.md:57:### L3 — Synonym / noun-phrase cycling (elegant variation)
skills/ai-writing-suite/_shared/patterns/lexical-tells.md:58:
skills/ai-writing-suite/_shared/patterns/lexical-tells.md:59:- **Tell:** Repetition-penalty training makes models rename the same thing to
skills/ai-writing-suite/_shared/patterns/lexical-tells.md:60:  avoid repeating a word: "the protagonist… the main character… the central
skills/ai-writing-suite/_shared/patterns/lexical-tells.md:61:  figure… the hero," or whole noun phrases: "the artist… the non-conformist
skills/ai-writing-suite/_shared/patterns/lexical-tells.md:62:  painter… the visionary creator."
skills/ai-writing-suite/_shared/patterns/lexical-tells.md:63:- **Fix:** Pick the clearest term and repeat it. Humans repeat words; repetition
skills/ai-writing-suite/_shared/patterns/lexical-tells.md:64:  reads as precision, not poverty.
skills/ai-writing-suite/_shared/patterns/lexical-tells.md:65:- **Sources:** blader (P11 word-level + P31 noun-phrase), aboudjem (§11),
skills/ai-writing-suite/_shared/patterns/lexical-tells.md:66:  avoid-ai, anti-vibe.
skills/ai-writing-suite/_shared/patterns/lexical-tells.md:67:
skills/ai-writing-suite/_shared/patterns/lexical-tells.md:68:> blader split this into two ids (word-level P11 vs noun-phrase P31). Merged
skills/ai-writing-suite/_shared/patterns/lexical-tells.md:69:> here because the fix is identical; the distinction is noted for lineage only.
skills/ai-writing-suite/_shared/patterns/lexical-tells.md:70:
skills/ai-writing-suite/_shared/patterns/lexical-tells.md:71:---
skills/ai-writing-suite/_shared/patterns/lexical-tells.md:72:
skills/ai-writing-suite/_shared/patterns/lexical-tells.md:73:### L4 — False ranges
skills/ai-writing-suite/_shared/patterns/lexical-tells.md:74:
skills/ai-writing-suite/_shared/patterns/lexical-tells.md:75:- **Tell:** "From X to Y" where X and Y are not on a real spectrum, faking
skills/ai-writing-suite/_shared/patterns/lexical-tells.md:76:  breadth: "from the Big Bang to dark matter," "from onboarding to billing."
skills/ai-writing-suite/_shared/patterns/lexical-tells.md:77:- **Fix:** List the actual items, or pick the one that matters. Don't fake a
skills/ai-writing-suite/_shared/patterns/lexical-tells.md:78:  range.
skills/ai-writing-suite/_shared/patterns/lexical-tells.md:79:- **Sources:** blader (P12), aboudjem (§12), avoid-ai, anti-vibe.
skills/ai-writing-suite/_shared/patterns/lexical-tells.md:80:
skills/ai-writing-suite/_shared/patterns/lexical-tells.md:81:---
skills/ai-writing-suite/_shared/patterns/lexical-tells.md:82:
skills/ai-writing-suite/_shared/patterns/lexical-tells.md:83:### L5 — Hyphenated-pair overuse
skills/ai-writing-suite/_shared/patterns/lexical-tells.md:84:
skills/ai-writing-suite/_shared/patterns/lexical-tells.md:85:- **Tell:** Two problems. (a) Density: stacking compound modifiers on one noun
skills/ai-writing-suite/_shared/patterns/lexical-tells.md:86:  ("a high-quality, well-architected, future-proof solution"). (b) The
skills/ai-writing-suite/_shared/patterns/lexical-tells.md:87:  attributive/predicate error: a compound is hyphenated *before* the noun ("a
skills/ai-writing-suite/_shared/patterns/lexical-tells.md:88:  high-quality report") but not *after* a linking verb ("the report is high
skills/ai-writing-suite/_shared/patterns/lexical-tells.md:89:  quality"). Models frequently hyphenate the predicate form.
skills/ai-writing-suite/_shared/patterns/lexical-tells.md:90:- **Fix:** Cut to the modifier that matters; drop the hyphen in predicate
skills/ai-writing-suite/_shared/patterns/lexical-tells.md:91:  position.
skills/ai-writing-suite/_shared/patterns/lexical-tells.md:92:- **Sources:** aboudjem (§26), avoid-ai (adapted from blader P26).
skills/ai-writing-suite/_shared/patterns/lexical-tells.md:93:
skills/ai-writing-suite/_shared/patterns/lexical-tells.md:94:---
skills/ai-writing-suite/_shared/patterns/lexical-tells.md:95:
skills/ai-writing-suite/_shared/patterns/lexical-tells.md:96:### L6 — Hollow / "real-actual" intensifiers
skills/ai-writing-suite/_shared/patterns/lexical-tells.md:97:
skills/ai-writing-suite/_shared/patterns/lexical-tells.md:98:- **Tell:** Empty intensifiers padding a claim: genuine, real, truly, quite
skills/ai-writing-suite/_shared/patterns/lexical-tells.md:99:  frankly, to be honest. Plus the noun-modifier form where real / actual /
skills/ai-writing-suite/_shared/patterns/lexical-tells.md:100:  genuine / true latches onto an abstract noun to imply the rest of the field is
skills/ai-writing-suite/_shared/patterns/lexical-tells.md:101:  fake without saying what makes this one real ("real on-chain tokenomics,"
skills/ai-writing-suite/_shared/patterns/lexical-tells.md:102:  "genuine utility").
skills/ai-writing-suite/_shared/patterns/lexical-tells.md:103:- **Fix:** Cut the intensifier and state the specific claim. **Carve-out:** keep
skills/ai-writing-suite/_shared/patterns/lexical-tells.md:104:  it when the sentence names the contrast ("actual revenue from customers, not
skills/ai-writing-suite/_shared/patterns/lexical-tells.md:105:  grants") — that is honest contrastive writing, not a tell.
skills/ai-writing-suite/_shared/patterns/lexical-tells.md:106:- **Sources:** avoid-ai (hollow intensifiers + real/actual inflation), stop-slop.
skills/ai-writing-suite/evals/detector/test_detector.py:1:"""Unit tests for the mechanical detector. Run: python3 -m unittest discover.
skills/ai-writing-suite/evals/detector/test_detector.py:2:
skills/ai-writing-suite/evals/detector/test_detector.py:3:Mirrors the coverage of the original avoid-ai `patterns.test.js`:
skills/ai-writing-suite/evals/detector/test_detector.py:4:  - AI-heavy text scores high (pattern coverage didn't regress)
skills/ai-writing-suite/evals/detector/test_detector.py:5:  - plain human prose scores low (no false-positive drift)
skills/ai-writing-suite/evals/detector/test_detector.py:6:  - length gates fire (empty / too-short / too-long)
skills/ai-writing-suite/evals/detector/test_detector.py:7:  - individual category detectors hit their canonical example
skills/ai-writing-suite/evals/detector/test_detector.py:8:  - the trinary classifier is FN-biased (human prose never reads AI_ONLY)
skills/ai-writing-suite/evals/detector/test_detector.py:9:"""
skills/ai-writing-suite/evals/detector/test_detector.py:10:
skills/ai-writing-suite/evals/detector/test_detector.py:11:import unittest
skills/ai-writing-suite/evals/detector/test_detector.py:12:
skills/ai-writing-suite/evals/detector/test_detector.py:13:from detector.detector import analyze
skills/ai-writing-suite/evals/detector/test_detector.py:14:
skills/ai-writing-suite/evals/detector/test_detector.py:15:
skills/ai-writing-suite/evals/detector/test_detector.py:16:class LengthGates(unittest.TestCase):
skills/ai-writing-suite/evals/detector/test_detector.py:17:    def test_empty(self):
skills/ai-writing-suite/evals/detector/test_detector.py:18:        r = analyze("")
skills/ai-writing-suite/evals/detector/test_detector.py:19:        self.assertEqual(r["label"], "Empty")
skills/ai-writing-suite/evals/detector/test_detector.py:20:        self.assertEqual(r["issues"], [])
skills/ai-writing-suite/evals/detector/test_detector.py:21:
skills/ai-writing-suite/evals/detector/test_detector.py:22:    def test_too_short(self):
skills/ai-writing-suite/evals/detector/test_detector.py:23:        r = analyze("Short unscorable text snippet.")
skills/ai-writing-suite/evals/detector/test_detector.py:24:        self.assertTrue(r["tooShort"])
skills/ai-writing-suite/evals/detector/test_detector.py:25:        self.assertEqual(r["label"], "Too short")
skills/ai-writing-suite/evals/detector/test_detector.py:26:
skills/ai-writing-suite/evals/detector/test_detector.py:27:    def test_too_long(self):
skills/ai-writing-suite/evals/detector/test_detector.py:28:        r = analyze("word " * 10001)
skills/ai-writing-suite/evals/detector/test_detector.py:29:        self.assertTrue(r["tooLong"])
skills/ai-writing-suite/evals/detector/test_detector.py:30:        self.assertEqual(r["label"], "Text too long")
skills/ai-writing-suite/evals/detector/test_detector.py:31:
skills/ai-writing-suite/evals/detector/test_detector.py:32:
skills/ai-writing-suite/evals/detector/test_detector.py:33:class ScoreBands(unittest.TestCase):
skills/ai-writing-suite/evals/detector/test_detector.py:34:    def test_ai_heavy_scores_high(self):
skills/ai-writing-suite/evals/detector/test_detector.py:35:        text = (
skills/ai-writing-suite/evals/detector/test_detector.py:36:            "In today's ever-evolving landscape, we delve into the intricate "
skills/ai-writing-suite/evals/detector/test_detector.py:37:            "tapestry of innovation. This seamless, robust paradigm showcases a "
skills/ai-writing-suite/evals/detector/test_detector.py:38:            "comprehensive framework. Moreover, it truly is a game-changer. "
skills/ai-writing-suite/evals/detector/test_detector.py:39:            "Furthermore, this pivotal moment underscores how we navigate the "
skills/ai-writing-suite/evals/detector/test_detector.py:40:            "complexities of modern AI."
skills/ai-writing-suite/evals/detector/test_detector.py:41:        )
skills/ai-writing-suite/evals/detector/test_detector.py:42:        r = analyze(text)
skills/ai-writing-suite/evals/detector/test_detector.py:43:        self.assertGreaterEqual(r["score"], 60, f"got {r['score']}")
skills/ai-writing-suite/evals/detector/test_detector.py:44:        self.assertIn(r["label"], ("Strong AI signals", "Heavy AI patterns"))
skills/ai-writing-suite/evals/detector/test_detector.py:45:
skills/ai-writing-suite/evals/detector/test_detector.py:46:    def test_plain_human_prose_stays_low(self):
skills/ai-writing-suite/evals/detector/test_detector.py:47:        text = (
skills/ai-writing-suite/evals/detector/test_detector.py:48:            "The build broke again this morning. Rolled back the auth refactor "
skills/ai-writing-suite/evals/detector/test_detector.py:49:            "and tests pass now. Still need to figure out why the token refresh "
skills/ai-writing-suite/evals/detector/test_detector.py:50:            "path hits a 401 for users on Safari but not Firefox, probably a "
skills/ai-writing-suite/evals/detector/test_detector.py:51:            "cookie scope issue but I want to confirm before shipping a fix."
skills/ai-writing-suite/evals/detector/test_detector.py:52:        )
skills/ai-writing-suite/evals/detector/test_detector.py:53:        r = analyze(text)
skills/ai-writing-suite/evals/detector/test_detector.py:54:        self.assertLessEqual(r["score"], 20, f"got {r['score']}")
skills/ai-writing-suite/evals/detector/test_detector.py:55:
skills/ai-writing-suite/evals/detector/test_detector.py:56:
skills/ai-writing-suite/evals/detector/test_detector.py:57:class CategoryDetectors(unittest.TestCase):
skills/ai-writing-suite/evals/detector/test_detector.py:58:    """Each AI-tell category fires on its canonical example."""
skills/ai-writing-suite/evals/detector/test_detector.py:59:
skills/ai-writing-suite/evals/detector/test_detector.py:60:    def _types(self, text, mode="general"):
skills/ai-writing-suite/evals/detector/test_detector.py:61:        return {i["type"] for i in analyze(text, mode)["issues"]}
skills/ai-writing-suite/evals/detector/test_detector.py:62:
skills/ai-writing-suite/evals/detector/test_detector.py:63:    def test_cutoff_disclaimer(self):
skills/ai-writing-suite/evals/detector/test_detector.py:64:        text = ("As an AI language model, I cannot give a definitive take here. "
skills/ai-writing-suite/evals/detector/test_detector.py:65:                "As of my last update I do not have access to real-time data on "
skills/ai-writing-suite/evals/detector/test_detector.py:66:                "the topic you raised in this short message to me today.")
skills/ai-writing-suite/evals/detector/test_detector.py:67:        self.assertIn("cutoff-disclaimer", self._types(text))
skills/ai-writing-suite/evals/detector/test_detector.py:68:
skills/ai-writing-suite/evals/detector/test_detector.py:69:    def test_chatbot_artifact(self):
skills/ai-writing-suite/evals/detector/test_detector.py:70:        text = ("Great question! I hope this helps you understand the topic. "
skills/ai-writing-suite/evals/detector/test_detector.py:71:                "Feel free to reach out if you have any other questions today.")
skills/ai-writing-suite/evals/detector/test_detector.py:72:        self.assertIn("chatbot", self._types(text))
skills/ai-writing-suite/evals/detector/test_detector.py:73:
skills/ai-writing-suite/evals/detector/test_detector.py:74:    def test_vague_attribution(self):
skills/ai-writing-suite/evals/detector/test_detector.py:75:        text = ("Experts believe the change is good and studies show it works. "
skills/ai-writing-suite/evals/detector/test_detector.py:76:                "Research indicates the trend will continue for several years.")
skills/ai-writing-suite/evals/detector/test_detector.py:77:        self.assertIn("vague-attribution", self._types(text))
skills/ai-writing-suite/evals/detector/test_detector.py:78:
skills/ai-writing-suite/evals/detector/test_detector.py:79:    def test_placeholder_fingerprint(self):
skills/ai-writing-suite/evals/detector/test_detector.py:80:        text = ("Dear [Recipient Name], thank you for your message regarding "
skills/ai-writing-suite/evals/detector/test_detector.py:81:                "the project. Please review the attached document at your "
skills/ai-writing-suite/evals/detector/test_detector.py:82:                "earliest convenience and reply. Best, [Your Name]")
skills/ai-writing-suite/evals/detector/test_detector.py:83:        self.assertIn("ai-placeholder", self._types(text))
skills/ai-writing-suite/evals/detector/test_detector.py:84:
skills/ai-writing-suite/evals/detector/test_detector.py:85:    def test_citation_markup_leak(self):
skills/ai-writing-suite/evals/detector/test_detector.py:86:        text = ("The result is well documented citeturn0search0 and confirmed "
skills/ai-writing-suite/evals/detector/test_detector.py:87:                "by several independent sources that looked into this matter "
skills/ai-writing-suite/evals/detector/test_detector.py:88:                "carefully over the past year of public reporting.")
skills/ai-writing-suite/evals/detector/test_detector.py:89:        self.assertIn("ai-citation-markup", self._types(text))
skills/ai-writing-suite/evals/detector/test_detector.py:90:
skills/ai-writing-suite/evals/detector/test_detector.py:91:    def test_hashtag_stuffing(self):
skills/ai-writing-suite/evals/detector/test_detector.py:92:        text = ("Big launch today, so proud of the team and the work we did. "
skills/ai-writing-suite/evals/detector/test_detector.py:93:                "#startup #growth #innovation #tech #founder #buildinpublic #ai")
skills/ai-writing-suite/evals/detector/test_detector.py:94:        self.assertIn("hashtag-stuff", self._types(text))
skills/ai-writing-suite/evals/detector/test_detector.py:95:
skills/ai-writing-suite/evals/detector/test_detector.py:96:    def test_title_case_header_general_mode(self):
skills/ai-writing-suite/evals/detector/test_detector.py:97:        text = ("Strategic Negotiations And Key Partnerships\n\n"
skills/ai-writing-suite/evals/detector/test_detector.py:98:                "We worked hard this quarter to close several deals with new "
skills/ai-writing-suite/evals/detector/test_detector.py:99:                "customers and partners across the region and beyond as planned.")
skills/ai-writing-suite/evals/detector/test_detector.py:100:        self.assertIn("title-case-header", self._types(text, "general"))
skills/ai-writing-suite/evals/detector/test_detector.py:101:
skills/ai-writing-suite/evals/detector/test_detector.py:102:    def test_title_case_header_skipped_in_technical_mode(self):
skills/ai-writing-suite/evals/detector/test_detector.py:103:        text = ("Strategic Negotiations And Key Partnerships\n\n"
skills/ai-writing-suite/evals/detector/test_detector.py:104:                "We worked hard this quarter to close several deals with new "
skills/ai-writing-suite/evals/detector/test_detector.py:105:                "customers and partners across the region and beyond as planned.")
skills/ai-writing-suite/evals/detector/test_detector.py:106:        self.assertNotIn("title-case-header", self._types(text, "technical"))
skills/ai-writing-suite/evals/detector/test_detector.py:107:
skills/ai-writing-suite/evals/detector/test_detector.py:108:    def test_tier2_cluster_requires_two(self):
skills/ai-writing-suite/evals/detector/test_detector.py:109:        # One tier-2 word alone should not flag; two in a paragraph should.
skills/ai-writing-suite/evals/detector/test_detector.py:110:        one = ("We harness the data to make a decision about the next release "
skills/ai-writing-suite/evals/detector/test_detector.py:111:               "and ship it to customers before the end of this current month.")
skills/ai-writing-suite/evals/detector/test_detector.py:112:        two = ("We harness the data and foster a culture that helps the team "
skills/ai-writing-suite/evals/detector/test_detector.py:113:               "ship faster to customers before the end of this current month.")
skills/ai-writing-suite/evals/detector/test_detector.py:114:        self.assertNotIn("tier2", self._types(one))
skills/ai-writing-suite/evals/detector/test_detector.py:115:        self.assertIn("tier2", self._types(two))
skills/ai-writing-suite/evals/detector/test_detector.py:116:
skills/ai-writing-suite/evals/detector/test_detector.py:117:
skills/ai-writing-suite/evals/detector/test_detector.py:118:class TrinaryClassifier(unittest.TestCase):
skills/ai-writing-suite/evals/detector/test_detector.py:119:    def test_human_prose_never_ai_only(self):
skills/ai-writing-suite/evals/detector/test_detector.py:120:        text = ("The build broke again this morning. Rolled back the auth "
skills/ai-writing-suite/evals/detector/test_detector.py:121:                "refactor and tests pass now. Still need to figure out the 401.")
skills/ai-writing-suite/evals/detector/test_detector.py:122:        r = analyze(text)
skills/ai-writing-suite/evals/detector/test_detector.py:123:        self.assertNotEqual(r["classification"], "AI_ONLY")
skills/ai-writing-suite/evals/detector/test_detector.py:124:
skills/ai-writing-suite/evals/detector/test_detector.py:125:    def test_cutoff_disclaimer_forces_ai_only(self):
skills/ai-writing-suite/evals/detector/test_detector.py:126:        text = ("As an AI language model, I cannot provide legal advice, but I "
skills/ai-writing-suite/evals/detector/test_detector.py:127:                "can offer some general thoughts on the question you have asked "
skills/ai-writing-suite/evals/detector/test_detector.py:128:                "me here today in this fairly short message you sent over.")
skills/ai-writing-suite/evals/detector/test_detector.py:129:        r = analyze(text)
skills/ai-writing-suite/evals/detector/test_detector.py:130:        self.assertEqual(r["classification"], "AI_ONLY")
skills/ai-writing-suite/evals/detector/test_detector.py:131:        self.assertEqual(r["confidence"], "high")
skills/ai-writing-suite/evals/detector/test_detector.py:132:
skills/ai-writing-suite/evals/detector/test_detector.py:133:
skills/ai-writing-suite/evals/detector/test_detector.py:134:class ScoringMath(unittest.TestCase):
skills/ai-writing-suite/evals/detector/test_detector.py:135:    def test_dedup_counts_distinct_signals(self):
skills/ai-writing-suite/evals/detector/test_detector.py:136:        # Same phrase three times should produce ONE deduped issue, not three.
skills/ai-writing-suite/evals/detector/test_detector.py:137:        text = ("Moreover, the plan works. Moreover, the plan works. Moreover, "
skills/ai-writing-suite/evals/detector/test_detector.py:138:                "the plan works well and the team is happy with it overall now.")
skills/ai-writing-suite/evals/detector/test_detector.py:139:        r = analyze(text)
skills/ai-writing-suite/evals/detector/test_detector.py:140:        transitions = [i for i in r["issues"] if i["type"] == "transition"]
skills/ai-writing-suite/evals/detector/test_detector.py:141:        self.assertEqual(len(transitions), 1)
skills/ai-writing-suite/evals/detector/test_detector.py:142:
skills/ai-writing-suite/evals/detector/test_detector.py:143:
skills/ai-writing-suite/evals/detector/test_detector.py:144:if __name__ == "__main__":
skills/ai-writing-suite/evals/detector/test_detector.py:145:    unittest.main()
skills/ai-writing-suite/evals/fixtures/__init__.py:1:"""LLM-judge before/after fixtures + the harness that runs them.
skills/ai-writing-suite/evals/fixtures/__init__.py:2:
skills/ai-writing-suite/evals/fixtures/__init__.py:3:Two halves (see rubric.md for WHY both):
skills/ai-writing-suite/evals/fixtures/__init__.py:4:  - DETERMINISTIC: run the mechanical detector on every before/after, assert the
skills/ai-writing-suite/evals/fixtures/__init__.py:5:    scores land in the expected bands, and report the naive-baseline miss rate
skills/ai-writing-suite/evals/fixtures/__init__.py:6:    (the calibration check). Needs no model — runs in CI.
skills/ai-writing-suite/evals/fixtures/__init__.py:7:  - LLM-JUDGE: score each `after` against rubric.md with a model. Runs only when
skills/ai-writing-suite/evals/fixtures/__init__.py:8:    a model is wired in; otherwise the harness clearly marks those checks
skills/ai-writing-suite/evals/fixtures/__init__.py:9:    SKIPPED rather than passing them silently.
skills/ai-writing-suite/evals/fixtures/__init__.py:10:"""
skills/ai-writing-suite/_shared/patterns/rhythm-stylometric.md:1:# Rhythm & Stylometric Tells
skills/ai-writing-suite/_shared/patterns/rhythm-stylometric.md:2:
skills/ai-writing-suite/_shared/patterns/rhythm-stylometric.md:3:Whole-document patterns in how the text flows, not individual words or phrases.
skills/ai-writing-suite/_shared/patterns/rhythm-stylometric.md:4:Structure is the #1 detection signal: classifiers weight rhythm and uniformity
skills/ai-writing-suite/_shared/patterns/rhythm-stylometric.md:5:above vocabulary. Fix every flagged word but leave the rhythm metronomic and the
skills/ai-writing-suite/_shared/patterns/rhythm-stylometric.md:6:text still reads as AI.
skills/ai-writing-suite/_shared/patterns/rhythm-stylometric.md:7:
skills/ai-writing-suite/_shared/patterns/rhythm-stylometric.md:8:Important counterweight: over-applying these rules pushes human writing *toward*
skills/ai-writing-suite/_shared/patterns/rhythm-stylometric.md:9:the AI profile. Natural disfluency, idiosyncratic word choice, and uneven pacing
skills/ai-writing-suite/_shared/patterns/rhythm-stylometric.md:10:are what keep text out of the "AI-generated" bucket. Don't sand away all
skills/ai-writing-suite/_shared/patterns/rhythm-stylometric.md:11:personality chasing clean prose.
skills/ai-writing-suite/_shared/patterns/rhythm-stylometric.md:12:
skills/ai-writing-suite/_shared/patterns/rhythm-stylometric.md:13:---
skills/ai-writing-suite/_shared/patterns/rhythm-stylometric.md:14:
skills/ai-writing-suite/_shared/patterns/rhythm-stylometric.md:15:### R1 — Sentence-length uniformity (low burstiness)
skills/ai-writing-suite/_shared/patterns/rhythm-stylometric.md:16:
skills/ai-writing-suite/_shared/patterns/rhythm-stylometric.md:17:- **Tell:** Detectors measure "burstiness" — sentence-length variance. Human
skills/ai-writing-suite/_shared/patterns/rhythm-stylometric.md:18:  writing has high burstiness; AI has low. If most sentences run 15-25 words with
skills/ai-writing-suite/_shared/patterns/rhythm-stylometric.md:19:  no short punches and no long flowing thoughts, it reads robotic.
skills/ai-writing-suite/_shared/patterns/rhythm-stylometric.md:20:- **Fix:** Mix short (3-8 words), medium (12-20), and long (25-40) in every
skills/ai-writing-suite/_shared/patterns/rhythm-stylometric.md:21:  paragraph. Never 3+ consecutive sentences of similar length. Fragments work.
skills/ai-writing-suite/_shared/patterns/rhythm-stylometric.md:22:  Questions break monotony. Let one sentence run long when the thought needs room.
skills/ai-writing-suite/_shared/patterns/rhythm-stylometric.md:23:- **Sources:** blader (P30 + burstiness principle), avoid-ai (rhythm and
skills/ai-writing-suite/_shared/patterns/rhythm-stylometric.md:24:  uniformity), stop-slop (vary rhythm), aboudjem (variety in sentence length).
skills/ai-writing-suite/_shared/patterns/rhythm-stylometric.md:25:
skills/ai-writing-suite/_shared/patterns/rhythm-stylometric.md:26:---
skills/ai-writing-suite/_shared/patterns/rhythm-stylometric.md:27:
skills/ai-writing-suite/_shared/patterns/rhythm-stylometric.md:28:### R2 — Paragraph-length uniformity
skills/ai-writing-suite/_shared/patterns/rhythm-stylometric.md:29:
skills/ai-writing-suite/_shared/patterns/rhythm-stylometric.md:30:- **Tell:** Every paragraph 3-5 sentences and roughly the same size.
skills/ai-writing-suite/_shared/patterns/rhythm-stylometric.md:31:- **Fix:** Vary deliberately. Some paragraphs one sentence. Some longer.
skills/ai-writing-suite/_shared/patterns/rhythm-stylometric.md:32:- **Sources:** avoid-ai (paragraph length uniformity), anti-vibe.
skills/ai-writing-suite/_shared/patterns/rhythm-stylometric.md:33:
skills/ai-writing-suite/_shared/patterns/rhythm-stylometric.md:34:---
skills/ai-writing-suite/_shared/patterns/rhythm-stylometric.md:35:
skills/ai-writing-suite/_shared/patterns/rhythm-stylometric.md:36:### R3 — Low vocabulary diversity (low TTR)
skills/ai-writing-suite/_shared/patterns/rhythm-stylometric.md:37:
skills/ai-writing-suite/_shared/patterns/rhythm-stylometric.md:38:- **Tell:** Type-token ratio (distinct word types / total tokens) is a classical
skills/ai-writing-suite/_shared/patterns/rhythm-stylometric.md:39:  stylometric signal readable by eye. Human prose at 200+ words usually lands
skills/ai-writing-suite/_shared/patterns/rhythm-stylometric.md:40:  ~0.50-0.65; AI trends flatter, sometimes under 0.40 when locked on a small
skills/ai-writing-suite/_shared/patterns/rhythm-stylometric.md:41:  vocabulary loop.
skills/ai-writing-suite/_shared/patterns/rhythm-stylometric.md:42:- **Fix:** Don't thesaurus the text. Broaden the *what*: name specific things,
skills/ai-writing-suite/_shared/patterns/rhythm-stylometric.md:43:  cite specific cases, replace a re-used abstract noun with the concrete instance.
skills/ai-writing-suite/_shared/patterns/rhythm-stylometric.md:44:  **Calibration:** low TTR is not proof — narrow topics, technical reference, and
skills/ai-writing-suite/_shared/patterns/rhythm-stylometric.md:45:  second-language writing legitimately compress vocabulary.
skills/ai-writing-suite/_shared/patterns/rhythm-stylometric.md:46:- **Sources:** avoid-ai (vocabulary diversity / stylometric).
skills/ai-writing-suite/_shared/patterns/rhythm-stylometric.md:47:
skills/ai-writing-suite/_shared/patterns/rhythm-stylometric.md:48:---
skills/ai-writing-suite/_shared/patterns/rhythm-stylometric.md:49:
skills/ai-writing-suite/_shared/patterns/rhythm-stylometric.md:50:### R4 — Low perplexity (predictable word choice)
skills/ai-writing-suite/_shared/patterns/rhythm-stylometric.md:51:
skills/ai-writing-suite/_shared/patterns/rhythm-stylometric.md:52:- **Tell:** Detectors also measure "perplexity" — how predictable each word is. AI
skills/ai-writing-suite/_shared/patterns/rhythm-stylometric.md:53:  text is low-perplexity (it picks the most statistically likely next word); human
skills/ai-writing-suite/_shared/patterns/rhythm-stylometric.md:54:  text is higher (more surprising choices).
skills/ai-writing-suite/_shared/patterns/rhythm-stylometric.md:55:- **Fix:** Choose the second or third word that comes to mind, not the first. Use
skills/ai-writing-suite/_shared/patterns/rhythm-stylometric.md:56:  audience-appropriate jargon or slang. Make unexpected analogies from real
skills/ai-writing-suite/_shared/patterns/rhythm-stylometric.md:57:  experience. (Don't force it — surprise that reads as random is its own tell.)
skills/ai-writing-suite/_shared/patterns/rhythm-stylometric.md:58:- **Sources:** blader (perplexity principle).
skills/ai-writing-suite/_shared/patterns/rhythm-stylometric.md:59:
skills/ai-writing-suite/_shared/patterns/rhythm-stylometric.md:60:---
skills/ai-writing-suite/_shared/patterns/rhythm-stylometric.md:61:
skills/ai-writing-suite/_shared/patterns/rhythm-stylometric.md:62:### R5 — Missing first-person / no stance
skills/ai-writing-suite/_shared/patterns/rhythm-stylometric.md:63:
skills/ai-writing-suite/_shared/patterns/rhythm-stylometric.md:64:- **Tell:** Relentlessly neutral where the genre expects a voice. No "I think," no
skills/ai-writing-suite/_shared/patterns/rhythm-stylometric.md:65:  stated preference, no reaction. The absence is itself a tell in opinion / blog /
skills/ai-writing-suite/_shared/patterns/rhythm-stylometric.md:66:  founder writing.
skills/ai-writing-suite/_shared/patterns/rhythm-stylometric.md:67:- **Fix:** Where appropriate, have opinions and state them. **Carve-out:** for
skills/ai-writing-suite/_shared/patterns/rhythm-stylometric.md:68:  encyclopedic, technical, legal, or reference text, neutral and plain *is* the
skills/ai-writing-suite/_shared/patterns/rhythm-stylometric.md:69:  correct human voice — don't inject opinions there.
skills/ai-writing-suite/_shared/patterns/rhythm-stylometric.md:70:- **Sources:** avoid-ai (missing first-person), aboudjem (personality and soul),
skills/ai-writing-suite/_shared/patterns/rhythm-stylometric.md:71:  stop-slop (put the reader in the room).
skills/ai-writing-suite/_shared/patterns/rhythm-stylometric.md:72:
skills/ai-writing-suite/_shared/patterns/rhythm-stylometric.md:73:---
skills/ai-writing-suite/_shared/patterns/rhythm-stylometric.md:74:
skills/ai-writing-suite/_shared/patterns/rhythm-stylometric.md:75:## What NOT to flag (false-positive guardrails)
skills/ai-writing-suite/_shared/patterns/rhythm-stylometric.md:76:
skills/ai-writing-suite/_shared/patterns/rhythm-stylometric.md:77:A clean human writer can hit many patterns above with no AI involvement. Before
skills/ai-writing-suite/_shared/patterns/rhythm-stylometric.md:78:rewriting, sanity-check you aren't gutting legitimate prose. None of these are
skills/ai-writing-suite/_shared/patterns/rhythm-stylometric.md:79:reliable AI indicators on their own:
skills/ai-writing-suite/_shared/patterns/rhythm-stylometric.md:80:
skills/ai-writing-suite/_shared/patterns/rhythm-stylometric.md:81:- Perfect grammar and consistent style. Polish ≠ AI; many writers are edited.
skills/ai-writing-suite/_shared/patterns/rhythm-stylometric.md:82:- Mixed casual/formal register. Often signals a technical field, a young writer,
skills/ai-writing-suite/_shared/patterns/rhythm-stylometric.md:83:  or neurodivergent prose habits.
skills/ai-writing-suite/_shared/patterns/rhythm-stylometric.md:84:- "Bland" or "robotic" prose. AI has *specific* tells; generic dryness is just
skills/ai-writing-suite/_shared/patterns/rhythm-stylometric.md:85:  dry writing.
skills/ai-writing-suite/_shared/patterns/rhythm-stylometric.md:86:- Formal/academic vocabulary. AI overuses *specific* fancy words, not all of them.
skills/ai-writing-suite/_shared/patterns/rhythm-stylometric.md:87:- A lone em dash, lone curly quotes, a single "however," letter-style salutations.
skills/ai-writing-suite/_shared/patterns/rhythm-stylometric.md:88:- Unsourced claims. Most of the web is unsourced.
skills/ai-writing-suite/_shared/patterns/rhythm-stylometric.md:89:
skills/ai-writing-suite/_shared/patterns/rhythm-stylometric.md:90:**Look for clusters, not isolated tells.** A single em dash is nothing; em dashes
skills/ai-writing-suite/_shared/patterns/rhythm-stylometric.md:91:plus rule-of-three plus "vibrant tapestry" plus a "Conclusion" section is a
skills/ai-writing-suite/_shared/patterns/rhythm-stylometric.md:92:confession.
skills/ai-writing-suite/_shared/patterns/rhythm-stylometric.md:93:
skills/ai-writing-suite/_shared/patterns/rhythm-stylometric.md:94:> Detector false-positive rates exceed 60% on non-native English writers (Liang
skills/ai-writing-suite/_shared/patterns/rhythm-stylometric.md:95:> et al., Stanford, *Patterns* 2023) and 70%+ on open-source detectors (Jabarian
skills/ai-writing-suite/_shared/patterns/rhythm-stylometric.md:96:> & Imas, BFI 2025). These are signals, not proof — never the sole basis for a
skills/ai-writing-suite/_shared/patterns/rhythm-stylometric.md:97:> consequential decision.
skills/ai-writing-suite/_shared/patterns/rhythm-stylometric.md:98:>
skills/ai-writing-suite/_shared/patterns/rhythm-stylometric.md:99:> Sources for this section: aboudjem (detection guidance), avoid-ai (what this
skills/ai-writing-suite/_shared/patterns/rhythm-stylometric.md:100:> skill is and isn't).
skills/ai-writing-suite/skills/comms-polish/SKILL.md:1:---
skills/ai-writing-suite/skills/comms-polish/SKILL.md:2:name: comms-polish
skills/ai-writing-suite/skills/comms-polish/SKILL.md:3:description: Polish prose that sounds AI-written while preserving meaning, facts, and author voice. Modes - detect, review, rewrite, edit - plus a 0-100 AI-tell score on demand. Use for docs, emails, posts, reports, and user-facing copy; do not use for code cleanup.
skills/ai-writing-suite/skills/comms-polish/SKILL.md:4:---
skills/ai-writing-suite/skills/comms-polish/SKILL.md:5:
skills/ai-writing-suite/skills/comms-polish/SKILL.md:6:# comms-polish
skills/ai-writing-suite/skills/comms-polish/SKILL.md:7:
skills/ai-writing-suite/skills/comms-polish/SKILL.md:8:Remove AI-shaped prose without turning the text into generic rewriting.
skills/ai-writing-suite/skills/comms-polish/SKILL.md:9:
skills/ai-writing-suite/skills/comms-polish/SKILL.md:10:The job is narrow: preserve meaning, remove slop, keep the author's voice.
skills/ai-writing-suite/skills/comms-polish/SKILL.md:11:
skills/ai-writing-suite/skills/comms-polish/SKILL.md:12:This is the suite's polish capability (formerly the standalone humanizer). It
skills/ai-writing-suite/skills/comms-polish/SKILL.md:13:does not carry its own pattern list — it reads the consolidated catalog under
skills/ai-writing-suite/skills/comms-polish/SKILL.md:14:`../../_shared/patterns/`, which is the single source of truth for AI tells.
skills/ai-writing-suite/skills/comms-polish/SKILL.md:15:
skills/ai-writing-suite/skills/comms-polish/SKILL.md:16:Three enrichments sit alongside the catalog:
skills/ai-writing-suite/skills/comms-polish/SKILL.md:17:
skills/ai-writing-suite/skills/comms-polish/SKILL.md:18:- `references/scenario-presets.md` — per-genre weighting (tweet / LinkedIn /
skills/ai-writing-suite/skills/comms-polish/SKILL.md:19:  README / memo): which tells matter most here, target tone/length, what to leave
skills/ai-writing-suite/skills/comms-polish/SKILL.md:20:  alone.
skills/ai-writing-suite/skills/comms-polish/SKILL.md:21:- `references/final-pass-checklist.md` — the pre-ship sweep run before returning
skills/ai-writing-suite/skills/comms-polish/SKILL.md:22:  any rewrite.
skills/ai-writing-suite/skills/comms-polish/SKILL.md:23:- `../../_shared/voice-profile.md` — the user's learned voice, read when present
skills/ai-writing-suite/skills/comms-polish/SKILL.md:24:  so rewrites bias toward how *they* write (see Voice Matching).
skills/ai-writing-suite/skills/comms-polish/SKILL.md:25:
skills/ai-writing-suite/skills/comms-polish/SKILL.md:26:## Pattern catalog
skills/ai-writing-suite/skills/comms-polish/SKILL.md:27:
skills/ai-writing-suite/skills/comms-polish/SKILL.md:28:Before scanning or rewriting, load the consolidated catalog. Read the index first
skills/ai-writing-suite/skills/comms-polish/SKILL.md:29:to see what's where, then the category files relevant to the draft:
skills/ai-writing-suite/skills/comms-polish/SKILL.md:30:
skills/ai-writing-suite/skills/comms-polish/SKILL.md:31:- `../../_shared/patterns/00-index.md` — index + how to read entries
skills/ai-writing-suite/skills/comms-polish/SKILL.md:32:- `lexical-tells.md` — AI vocabulary (tiered), copula avoidance, synonym cycling, false ranges, hyphen pairs, hollow intensifiers
skills/ai-writing-suite/skills/comms-polish/SKILL.md:33:- `significance-attribution.md` — significance/novelty inflation, vague attribution, name-dropping, promotional language, superficial -ing, speculative gap-filling, consultant-speak
skills/ai-writing-suite/skills/comms-polish/SKILL.md:34:- `structural-tells.md` — rule of three, negative parallelism, formulaic challenges, over-structure, inline-header lists, reshuffle immunity, treadmill effect
skills/ai-writing-suite/skills/comms-polish/SKILL.md:35:- `hedging-filler.md` — filler, stacked hedging, generic/future-narrative closers, confidence-calibration phrases, signposting
skills/ai-writing-suite/skills/comms-polish/SKILL.md:36:- `punctuation-formatting.md` — em dashes, bold overuse, emoji headers, curly quotes, title case, hashtag stuffing, placeholders, citation/UTM fingerprints
skills/ai-writing-suite/skills/comms-polish/SKILL.md:37:- `communication-artifacts.md` — chatbot tics, sycophancy, acknowledgment loops, cutoff disclaimers, reasoning-chain leaks, engagement hooks, emotional flatline
skills/ai-writing-suite/skills/comms-polish/SKILL.md:38:- `rhythm-stylometric.md` — sentence/paragraph uniformity (burstiness), low TTR, perplexity, register shift, **and the what-NOT-to-flag guardrails**
skills/ai-writing-suite/skills/comms-polish/SKILL.md:39:
skills/ai-writing-suite/skills/comms-polish/SKILL.md:40:Always apply the guardrails in `rhythm-stylometric.md`: look for clusters, not
skills/ai-writing-suite/skills/comms-polish/SKILL.md:41:isolated tells. These are signals, not proof.
skills/ai-writing-suite/skills/comms-polish/SKILL.md:42:
skills/ai-writing-suite/skills/comms-polish/SKILL.md:43:The catalog is the rule source. The local references decide *how* to apply it:
skills/ai-writing-suite/skills/comms-polish/SKILL.md:44:
skills/ai-writing-suite/skills/comms-polish/SKILL.md:45:- `references/scenario-presets.md` — weights catalog categories per genre.
skills/ai-writing-suite/skills/comms-polish/SKILL.md:46:- `references/final-pass-checklist.md` — the pre-ship sweep.
skills/ai-writing-suite/skills/comms-polish/SKILL.md:47:
skills/ai-writing-suite/skills/comms-polish/SKILL.md:48:## Boundary
skills/ai-writing-suite/skills/comms-polish/SKILL.md:49:
skills/ai-writing-suite/skills/comms-polish/SKILL.md:50:This skill edits prose, not code.
skills/ai-writing-suite/skills/comms-polish/SKILL.md:51:
skills/ai-writing-suite/skills/comms-polish/SKILL.md:52:- Use for: README prose, docs, emails, reports, posts, launch notes, UX copy, and narrative summaries.
skills/ai-writing-suite/skills/comms-polish/SKILL.md:53:- Do not use for: source-code cleanup, architecture simplification, test rewriting, or changing program behavior.
skills/ai-writing-suite/skills/comms-polish/SKILL.md:54:- Preserve: facts, citations, numbers, file paths, commands, API names, quoted text, and claims unless the user explicitly asks to change them.
skills/ai-writing-suite/skills/comms-polish/SKILL.md:55:- Flag unsupported claims instead of inventing evidence.
skills/ai-writing-suite/skills/comms-polish/SKILL.md:56:
skills/ai-writing-suite/skills/comms-polish/SKILL.md:57:## Modes
skills/ai-writing-suite/skills/comms-polish/SKILL.md:58:
skills/ai-writing-suite/skills/comms-polish/SKILL.md:59:Pick the mode from the user's request. If unclear, use `rewrite`.
skills/ai-writing-suite/skills/comms-polish/SKILL.md:60:
skills/ai-writing-suite/skills/comms-polish/SKILL.md:61:| Mode | Use When | Output |
skills/ai-writing-suite/skills/comms-polish/SKILL.md:62:| --- | --- | --- |
skills/ai-writing-suite/skills/comms-polish/SKILL.md:63:| `detect` | The user wants to know what sounds AI-written. | Findings and examples, no rewrite. |
skills/ai-writing-suite/skills/comms-polish/SKILL.md:64:| `review` | The user wants prioritized writing feedback. | Findings first, with examples. |
skills/ai-writing-suite/skills/comms-polish/SKILL.md:65:| `rewrite` | The user pasted text and wants a polished version. | Polished text only unless notes are requested. |
skills/ai-writing-suite/skills/comms-polish/SKILL.md:66:| `edit` | The user asks to modify a file. | Targeted file edits plus verification. |
skills/ai-writing-suite/skills/comms-polish/SKILL.md:67:
skills/ai-writing-suite/skills/comms-polish/SKILL.md:68:## Voice Matching
skills/ai-writing-suite/skills/comms-polish/SKILL.md:69:
skills/ai-writing-suite/skills/comms-polish/SKILL.md:70:Voice has three sources, in priority order:
skills/ai-writing-suite/skills/comms-polish/SKILL.md:71:
skills/ai-writing-suite/skills/comms-polish/SKILL.md:72:1. **A learned voice profile** at `../../_shared/voice-profile.md` (canonical path:
skills/ai-writing-suite/skills/comms-polish/SKILL.md:73:   `_shared/voice-profile.md`). This is produced by the `voice-onboard` sub-skill.
skills/ai-writing-suite/skills/comms-polish/SKILL.md:74:   **Before any rewrite, check whether this file exists and read it if it does.**
skills/ai-writing-suite/skills/comms-polish/SKILL.md:75:   It is loose coupling: comms-polish does not create or own that file — it reads
skills/ai-writing-suite/skills/comms-polish/SKILL.md:76:   whatever fields are present and biases edits toward them. Sections to use when
skills/ai-writing-suite/skills/comms-polish/SKILL.md:77:   present: Tone, Sentence Length, Vocabulary Do / Vocabulary Don't, Signature
skills/ai-writing-suite/skills/comms-polish/SKILL.md:78:   Moves, Punctuation & Formatting, Openings & Closings, Uncertainty Style, Things
skills/ai-writing-suite/skills/comms-polish/SKILL.md:79:   To Avoid, and Scope & Calibration (which says where the profile applies). Read
skills/ai-writing-suite/skills/comms-polish/SKILL.md:80:   what's there; ignore what isn't — never fail on a missing section.
skills/ai-writing-suite/skills/comms-polish/SKILL.md:81:2. **A writing sample the user pastes** in this request — match it directly.
skills/ai-writing-suite/skills/comms-polish/SKILL.md:82:3. **Inferred voice** from the draft itself, when neither of the above exists.
skills/ai-writing-suite/skills/comms-polish/SKILL.md:83:
skills/ai-writing-suite/skills/comms-polish/SKILL.md:84:**Graceful degradation:** if `_shared/voice-profile.md` is absent, do not error
skills/ai-writing-suite/skills/comms-polish/SKILL.md:85:and do not block. Note briefly that no profile was found, then polish normally
skills/ai-writing-suite/skills/comms-polish/SKILL.md:86:using a pasted sample or inferred voice. The profile is a bias signal, never a
skills/ai-writing-suite/skills/comms-polish/SKILL.md:87:hard dependency. A hard genre constraint (e.g. a tweet's 280-char limit) still
skills/ai-writing-suite/skills/comms-polish/SKILL.md:88:wins over a profile preference.
skills/ai-writing-suite/skills/comms-polish/SKILL.md:89:
skills/ai-writing-suite/skills/comms-polish/SKILL.md:90:When a profile or sample exists, match:
skills/ai-writing-suite/skills/comms-polish/SKILL.md:91:
skills/ai-writing-suite/skills/comms-polish/SKILL.md:92:- sentence length and rhythm
skills/ai-writing-suite/skills/comms-polish/SKILL.md:93:- plainness or formality
skills/ai-writing-suite/skills/comms-polish/SKILL.md:94:- punctuation habits
skills/ai-writing-suite/skills/comms-polish/SKILL.md:95:- paragraph shape
skills/ai-writing-suite/skills/comms-polish/SKILL.md:96:- tolerance for humor, warmth, bluntness, or personality
skills/ai-writing-suite/skills/comms-polish/SKILL.md:97:- preferred terms and phrases
skills/ai-writing-suite/skills/comms-polish/SKILL.md:98:
skills/ai-writing-suite/skills/comms-polish/SKILL.md:99:When neither exists, use the lightest voice that fits the context:
skills/ai-writing-suite/skills/comms-polish/SKILL.md:100:
skills/ai-writing-suite/skills/comms-polish/SKILL.md:101:- `technical`: precise, compact, no hype
skills/ai-writing-suite/skills/comms-polish/SKILL.md:102:- `professional`: clear, measured, low-drama
skills/ai-writing-suite/skills/comms-polish/SKILL.md:103:- `warm`: supportive and direct
skills/ai-writing-suite/skills/comms-polish/SKILL.md:104:- `casual`: conversational, with contractions
skills/ai-writing-suite/skills/comms-polish/SKILL.md:105:- `blunt`: shortest viable version
skills/ai-writing-suite/skills/comms-polish/SKILL.md:106:
skills/ai-writing-suite/skills/comms-polish/SKILL.md:107:## Rewrite Workflow
skills/ai-writing-suite/skills/comms-polish/SKILL.md:108:
skills/ai-writing-suite/skills/comms-polish/SKILL.md:109:1. Identify the audience, purpose, and required structure.
skills/ai-writing-suite/skills/comms-polish/SKILL.md:110:2. **Pick the genre preset.** Match the draft to a preset in
skills/ai-writing-suite/skills/comms-polish/SKILL.md:111:   `references/scenario-presets.md` (tweet / LinkedIn / README / memo). It tells
skills/ai-writing-suite/skills/comms-polish/SKILL.md:112:   you which catalog categories to weight harder and what to leave alone in this
skills/ai-writing-suite/skills/comms-polish/SKILL.md:113:   genre. If no preset fits, scan the catalog evenly.
skills/ai-writing-suite/skills/comms-polish/SKILL.md:114:3. **Load the voice profile if present.** Check for `../../_shared/voice-profile.md`
skills/ai-writing-suite/skills/comms-polish/SKILL.md:115:   and read it if it exists; otherwise use a pasted sample or inferred voice
skills/ai-writing-suite/skills/comms-polish/SKILL.md:116:   (see Voice Matching). Degrade gracefully when absent.
skills/ai-writing-suite/skills/comms-polish/SKILL.md:117:4. Mark the factual anchors that must survive unchanged.
skills/ai-writing-suite/skills/comms-polish/SKILL.md:118:5. Scan against the pattern catalog, weighted by the preset, and remove the tells
skills/ai-writing-suite/skills/comms-polish/SKILL.md:119:   you find:
skills/ai-writing-suite/skills/comms-polish/SKILL.md:120:   - throat-clearing and filler
skills/ai-writing-suite/skills/comms-polish/SKILL.md:121:   - inflated significance
skills/ai-writing-suite/skills/comms-polish/SKILL.md:122:   - vague attribution
skills/ai-writing-suite/skills/comms-polish/SKILL.md:123:   - promotional adjectives
skills/ai-writing-suite/skills/comms-polish/SKILL.md:124:   - forced three-item lists
skills/ai-writing-suite/skills/comms-polish/SKILL.md:125:   - "not X but Y" theatrics
skills/ai-writing-suite/skills/comms-polish/SKILL.md:126:   - uniform sentence length
skills/ai-writing-suite/skills/comms-polish/SKILL.md:127:   - chatbot artifacts
skills/ai-writing-suite/skills/comms-polish/SKILL.md:128:6. Replace vague abstractions with concrete actors, actions, examples, or consequences.
skills/ai-writing-suite/skills/comms-polish/SKILL.md:129:7. Vary rhythm without adding fake personality. Bias word choice and cadence
skills/ai-writing-suite/skills/comms-polish/SKILL.md:130:   toward the voice profile when one was loaded.
skills/ai-writing-suite/skills/comms-polish/SKILL.md:131:8. **Run `references/final-pass-checklist.md`** before returning anything.
skills/ai-writing-suite/skills/comms-polish/SKILL.md:132:9. Return the requested output and mention any claim that still needs evidence.
skills/ai-writing-suite/skills/comms-polish/SKILL.md:133:
skills/ai-writing-suite/skills/comms-polish/SKILL.md:134:## Safety Rules
skills/ai-writing-suite/skills/comms-polish/SKILL.md:135:
skills/ai-writing-suite/skills/comms-polish/SKILL.md:136:- Do not change the author's position to make the prose smoother.
skills/ai-writing-suite/skills/comms-polish/SKILL.md:137:- Do not add examples, numbers, citations, or claims that were not present.
skills/ai-writing-suite/skills/comms-polish/SKILL.md:138:- Do not remove caveats that carry real uncertainty.
skills/ai-writing-suite/skills/comms-polish/SKILL.md:139:- Do not polish away legal, medical, financial, or safety warnings.
skills/ai-writing-suite/skills/comms-polish/SKILL.md:140:- Do not rewrite quoted text unless the user asks.
skills/ai-writing-suite/skills/comms-polish/SKILL.md:141:
skills/ai-writing-suite/skills/comms-polish/SKILL.md:142:## Before And After Examples
skills/ai-writing-suite/skills/comms-polish/SKILL.md:143:
skills/ai-writing-suite/skills/comms-polish/SKILL.md:144:### Technical docs
skills/ai-writing-suite/skills/comms-polish/SKILL.md:145:
skills/ai-writing-suite/skills/comms-polish/SKILL.md:146:Before:
skills/ai-writing-suite/skills/comms-polish/SKILL.md:147:
skills/ai-writing-suite/skills/comms-polish/SKILL.md:148:```text
skills/ai-writing-suite/skills/comms-polish/SKILL.md:149:This robust workflow enables teams to seamlessly leverage contextual insights, ensuring a more effective and streamlined development experience.
skills/ai-writing-suite/skills/comms-polish/SKILL.md:150:```
skills/ai-writing-suite/skills/comms-polish/SKILL.md:151:
skills/ai-writing-suite/skills/comms-polish/SKILL.md:152:After:
skills/ai-writing-suite/skills/comms-polish/SKILL.md:153:
skills/ai-writing-suite/skills/comms-polish/SKILL.md:154:```text
skills/ai-writing-suite/skills/comms-polish/SKILL.md:155:This workflow gives teams the context they need before they start editing.
skills/ai-writing-suite/skills/comms-polish/SKILL.md:156:```
skills/ai-writing-suite/skills/comms-polish/SKILL.md:157:
skills/ai-writing-suite/skills/comms-polish/SKILL.md:158:### Status update
skills/ai-writing-suite/skills/comms-polish/SKILL.md:159:
skills/ai-writing-suite/skills/comms-polish/SKILL.md:160:Before:
skills/ai-writing-suite/skills/comms-polish/SKILL.md:161:
skills/ai-writing-suite/skills/comms-polish/SKILL.md:162:```text
skills/ai-writing-suite/skills/comms-polish/SKILL.md:163:It is important to note that the migration represents a pivotal step toward improving reliability, scalability, and operational efficiency.
skills/ai-writing-suite/skills/comms-polish/SKILL.md:164:```
skills/ai-writing-suite/skills/comms-polish/SKILL.md:165:
skills/ai-writing-suite/skills/comms-polish/SKILL.md:166:After:
skills/ai-writing-suite/skills/comms-polish/SKILL.md:167:
skills/ai-writing-suite/skills/comms-polish/SKILL.md:168:```text
skills/ai-writing-suite/skills/comms-polish/SKILL.md:169:The migration removes the retry job that caused last week's duplicate sends.
skills/ai-writing-suite/skills/comms-polish/SKILL.md:170:```
skills/ai-writing-suite/skills/comms-polish/SKILL.md:171:
skills/ai-writing-suite/skills/comms-polish/SKILL.md:172:### Personal note
skills/ai-writing-suite/skills/comms-polish/SKILL.md:173:
skills/ai-writing-suite/skills/comms-polish/SKILL.md:174:Before:
skills/ai-writing-suite/skills/comms-polish/SKILL.md:175:
skills/ai-writing-suite/skills/comms-polish/SKILL.md:176:```text
skills/ai-writing-suite/skills/comms-polish/SKILL.md:177:I wanted to take a moment to express my sincere appreciation for your invaluable support throughout this journey.
skills/ai-writing-suite/skills/comms-polish/SKILL.md:178:```
skills/ai-writing-suite/skills/comms-polish/SKILL.md:179:
skills/ai-writing-suite/skills/comms-polish/SKILL.md:180:After:
skills/ai-writing-suite/skills/comms-polish/SKILL.md:181:
skills/ai-writing-suite/skills/comms-polish/SKILL.md:182:```text
skills/ai-writing-suite/skills/comms-polish/SKILL.md:183:Thank you for sticking with me through this. It helped more than you probably know.
skills/ai-writing-suite/skills/comms-polish/SKILL.md:184:```
skills/ai-writing-suite/skills/comms-polish/SKILL.md:185:
skills/ai-writing-suite/skills/comms-polish/SKILL.md:186:## Scoring
skills/ai-writing-suite/skills/comms-polish/SKILL.md:187:
skills/ai-writing-suite/skills/comms-polish/SKILL.md:188:When the user asks for a score, estimate AI-writing density on a 0-100 scale
skills/ai-writing-suite/skills/comms-polish/SKILL.md:189:(lower is more human). Do not claim detector certainty.
skills/ai-writing-suite/skills/comms-polish/SKILL.md:190:
skills/ai-writing-suite/skills/comms-polish/SKILL.md:191:| Score | Verdict | Meaning |
skills/ai-writing-suite/skills/comms-polish/SKILL.md:192:| --- | --- | --- |
skills/ai-writing-suite/skills/comms-polish/SKILL.md:193:| 0-20 | Pristine | Reads like a specific human wrote it. |
skills/ai-writing-suite/skills/comms-polish/SKILL.md:194:| 21-40 | Mostly human | One or two minor tells, easy to clean. |
skills/ai-writing-suite/skills/comms-polish/SKILL.md:195:| 41-60 | Mixed | Half-AI half-human; partial editing likely. |
skills/ai-writing-suite/skills/comms-polish/SKILL.md:196:| 61-80 | AI-leaning | Multiple structural tells; detectors will probably catch it. |
skills/ai-writing-suite/skills/comms-polish/SKILL.md:197:| 81-100 | Pure AI smell | Wholesale chatbot output with no editing. |
skills/ai-writing-suite/skills/comms-polish/SKILL.md:198:
skills/ai-writing-suite/skills/comms-polish/SKILL.md:199:Weight structural tells (rhythm uniformity, reshuffle immunity, treadmill effect)
skills/ai-writing-suite/skills/comms-polish/SKILL.md:200:above vocabulary hits — structure is the harder signal to mask.
skills/ai-writing-suite/skills/comms-polish/SKILL.md:201:
skills/ai-writing-suite/skills/comms-polish/SKILL.md:202:## File Edits
skills/ai-writing-suite/skills/comms-polish/SKILL.md:203:
skills/ai-writing-suite/skills/comms-polish/SKILL.md:204:For `edit` mode:
skills/ai-writing-suite/skills/comms-polish/SKILL.md:205:
skills/ai-writing-suite/skills/comms-polish/SKILL.md:206:1. Read the file first.
skills/ai-writing-suite/skills/comms-polish/SKILL.md:207:2. Preserve frontmatter, headings, tables, links, code blocks, commands, and citations.
skills/ai-writing-suite/skills/comms-polish/SKILL.md:208:3. Make targeted prose edits only; leave already-human passages untouched.
skills/ai-writing-suite/skills/comms-polish/SKILL.md:209:4. Re-read the file and confirm the flagged patterns are resolved.
skills/ai-writing-suite/skills/comms-polish/SKILL.md:210:5. Run `git diff --check` or the repo's docs lint command when available.
skills/ai-writing-suite/skills/comms-polish/SKILL.md:211:
skills/ai-writing-suite/skills/comms-polish/SKILL.md:212:## Self-improvement (human-gated)
skills/ai-writing-suite/skills/comms-polish/SKILL.md:213:
skills/ai-writing-suite/skills/comms-polish/SKILL.md:214:This skill participates in the suite's human-gated self-improvement loop. The
skills/ai-writing-suite/skills/comms-polish/SKILL.md:215:full protocol is in `../../_shared/self-improvement.md`; follow it, do not restate
skills/ai-writing-suite/skills/comms-polish/SKILL.md:216:it. In short:
skills/ai-writing-suite/skills/comms-polish/SKILL.md:217:
skills/ai-writing-suite/skills/comms-polish/SKILL.md:218:- **On start:** read `../../_shared/learned-rules.md` (alongside the voice profile)
skills/ai-writing-suite/skills/comms-polish/SKILL.md:219:  and apply any entry whose `status: active` and whose scope is `comms-polish` or
skills/ai-writing-suite/skills/comms-polish/SKILL.md:220:  `all`. Degrade gracefully if the file is absent.
skills/ai-writing-suite/skills/comms-polish/SKILL.md:221:- **On end:** if a repeatable polish correction surfaced this session, **propose**
skills/ai-writing-suite/skills/comms-polish/SKILL.md:222:  one candidate rule (rule + session-grounded rationale + scope) and **wait for
skills/ai-writing-suite/skills/comms-polish/SKILL.md:223:  explicit approval** before appending it to `learned-rules.md`. Propose nothing
skills/ai-writing-suite/skills/comms-polish/SKILL.md:224:  if nothing repeatable surfaced.
skills/ai-writing-suite/skills/comms-polish/SKILL.md:225:- **Never** auto-edit this SKILL.md or the pattern catalog — approved rules live
skills/ai-writing-suite/skills/comms-polish/SKILL.md:226:  only in `learned-rules.md` (append-only). Each rule is eval-measured in Layer 3
skills/ai-writing-suite/skills/comms-polish/SKILL.md:227:  before it is trusted.
skills/ai-writing-suite/skills/comms-polish/SKILL.md:228:
skills/ai-writing-suite/skills/comms-polish/SKILL.md:229:## Output
skills/ai-writing-suite/skills/comms-polish/SKILL.md:230:
skills/ai-writing-suite/skills/comms-polish/SKILL.md:231:- For `rewrite`: return the polished text only unless the user asks for notes.
skills/ai-writing-suite/skills/comms-polish/SKILL.md:232:- For `detect` or `review`: lead with findings and examples, grouped by severity.
skills/ai-writing-suite/skills/comms-polish/SKILL.md:233:- For `edit`: summarize changed files, what improved, verification, and any preserved uncertainty.
skills/ai-writing-suite/skills/comms-draft/SKILL.md:1:---
skills/ai-writing-suite/skills/comms-draft/SKILL.md:2:name: comms-draft
skills/ai-writing-suite/skills/comms-draft/SKILL.md:3:description: Draft a new page guided by the knowledge base / playbook. Not yet built - coming in v2.
skills/ai-writing-suite/skills/comms-draft/SKILL.md:4:---
skills/ai-writing-suite/skills/comms-draft/SKILL.md:5:
skills/ai-writing-suite/skills/comms-draft/SKILL.md:6:# comms-draft (placeholder)
skills/ai-writing-suite/skills/comms-draft/SKILL.md:7:
skills/ai-writing-suite/skills/comms-draft/SKILL.md:8:This sub-skill will draft a new page guided by the knowledge base under
skills/ai-writing-suite/skills/comms-draft/SKILL.md:9:`_shared/knowledge/` -- using the playbook's structure, terminology, and best
skills/ai-writing-suite/skills/comms-draft/SKILL.md:10:practices to scaffold a first draft, which `comms-polish` can then finish.
skills/ai-writing-suite/skills/comms-draft/SKILL.md:11:**Coming in v2.** Depends on the KB seed and `comms-qa` retrieval, which are
skills/ai-writing-suite/skills/comms-draft/SKILL.md:12:later layers.
skills/ai-writing-suite/evals/detector/patterns.py:1:"""Pattern tables + regexes — the executable expression of `_shared/patterns/`.
skills/ai-writing-suite/evals/detector/patterns.py:2:
skills/ai-writing-suite/evals/detector/patterns.py:3:WHY a separate data module: keeping the rule *data* apart from the scan *logic*
skills/ai-writing-suite/evals/detector/patterns.py:4:(detector.py) mirrors how the skill keeps the catalog (`_shared/patterns/`)
skills/ai-writing-suite/evals/detector/patterns.py:5:apart from the polish prose. When a tell moves in/out of the catalog, only this
skills/ai-writing-suite/evals/detector/patterns.py:6:file changes. Each block names the catalog category it enforces.
skills/ai-writing-suite/evals/detector/patterns.py:7:
skills/ai-writing-suite/evals/detector/patterns.py:8:Ported directly from `avoid-ai-writing/detector/patterns.js` (MIT). Regex
skills/ai-writing-suite/evals/detector/patterns.py:9:syntax translated JS -> Python `re`; behaviour kept identical. `re.I` = case
skills/ai-writing-suite/evals/detector/patterns.py:10:insensitive, `re.M` = multiline (`^`/`$` per line).
skills/ai-writing-suite/evals/detector/patterns.py:11:"""
skills/ai-writing-suite/evals/detector/patterns.py:12:
skills/ai-writing-suite/evals/detector/patterns.py:13:import re
skills/ai-writing-suite/evals/detector/patterns.py:14:
skills/ai-writing-suite/evals/detector/patterns.py:15:# --- Tier 1: AI vocabulary, replace on sight (catalog L1) -----------------
skills/ai-writing-suite/evals/detector/patterns.py:16:# Single words. Value = the plain-word suggestion the skill would offer.
skills/ai-writing-suite/evals/detector/patterns.py:17:TIER1 = {
skills/ai-writing-suite/evals/detector/patterns.py:18:    "delve": "explore, dig into, look at",
skills/ai-writing-suite/evals/detector/patterns.py:19:    "tapestry": "describe the actual complexity",
skills/ai-writing-suite/evals/detector/patterns.py:20:    "paradigm": "model, approach, framework",
skills/ai-writing-suite/evals/detector/patterns.py:21:    "embark": "start, begin",
skills/ai-writing-suite/evals/detector/patterns.py:22:    "beacon": "rewrite entirely",
skills/ai-writing-suite/evals/detector/patterns.py:23:    "robust": "strong, reliable, solid",
skills/ai-writing-suite/evals/detector/patterns.py:24:    "comprehensive": "thorough, complete, full",
skills/ai-writing-suite/evals/detector/patterns.py:25:    "cutting-edge": "latest, newest, advanced",
skills/ai-writing-suite/evals/detector/patterns.py:26:    "pivotal": "important, key, critical",
skills/ai-writing-suite/evals/detector/patterns.py:27:    "underscores": "highlights, shows",
skills/ai-writing-suite/evals/detector/patterns.py:28:    "meticulous": "careful, detailed, precise",
skills/ai-writing-suite/evals/detector/patterns.py:29:    "meticulously": "carefully, precisely",
skills/ai-writing-suite/evals/detector/patterns.py:30:    "seamless": "smooth, easy, without friction",
skills/ai-writing-suite/evals/detector/patterns.py:31:    "seamlessly": "smoothly, easily",
skills/ai-writing-suite/evals/detector/patterns.py:32:    "game-changer": "describe what changed",
skills/ai-writing-suite/evals/detector/patterns.py:33:    "game-changing": "describe what changed",
skills/ai-writing-suite/evals/detector/patterns.py:34:    "utilize": "use",
skills/ai-writing-suite/evals/detector/patterns.py:35:    "nestled": "is located, sits",
skills/ai-writing-suite/evals/detector/patterns.py:36:    "vibrant": "describe what makes it active",
skills/ai-writing-suite/evals/detector/patterns.py:37:    "thriving": "growing, active",
skills/ai-writing-suite/evals/detector/patterns.py:38:    "showcasing": "showing, demonstrating",
skills/ai-writing-suite/evals/detector/patterns.py:39:    "bustling": "busy, active",
skills/ai-writing-suite/evals/detector/patterns.py:40:    "intricate": "complex, detailed",
skills/ai-writing-suite/evals/detector/patterns.py:41:    "intricacies": "complexities, details",
skills/ai-writing-suite/evals/detector/patterns.py:42:    "ever-evolving": "changing, growing",
skills/ai-writing-suite/evals/detector/patterns.py:43:    "enduring": "lasting, long-running",
skills/ai-writing-suite/evals/detector/patterns.py:44:    "daunting": "hard, difficult",
skills/ai-writing-suite/evals/detector/patterns.py:45:    "holistic": "complete, full, whole",
skills/ai-writing-suite/evals/detector/patterns.py:46:    "holistically": "completely, fully",
skills/ai-writing-suite/evals/detector/patterns.py:47:    "actionable": "practical, useful, concrete",
skills/ai-writing-suite/evals/detector/patterns.py:48:    "impactful": "effective, significant",
skills/ai-writing-suite/evals/detector/patterns.py:49:    "learnings": "lessons, findings, takeaways",
skills/ai-writing-suite/evals/detector/patterns.py:50:    "synergy": "describe the combined effect",
skills/ai-writing-suite/evals/detector/patterns.py:51:    "synergies": "describe the combined effect",
skills/ai-writing-suite/evals/detector/patterns.py:52:    "interplay": "relationship, connection",
skills/ai-writing-suite/evals/detector/patterns.py:53:    "commence": "start, begin",
skills/ai-writing-suite/evals/detector/patterns.py:54:    "ascertain": "find out, determine",
skills/ai-writing-suite/evals/detector/patterns.py:55:    "endeavor": "effort, attempt, try",
skills/ai-writing-suite/evals/detector/patterns.py:56:    "symphony": "describe the coordination",
skills/ai-writing-suite/evals/detector/patterns.py:57:    "embrace": "adopt, accept, use",
skills/ai-writing-suite/evals/detector/patterns.py:58:}
skills/ai-writing-suite/evals/detector/patterns.py:59:
skills/ai-writing-suite/evals/detector/patterns.py:60:# Multi-word Tier 1 phrases. (pattern, suggestion).
skills/ai-writing-suite/evals/detector/patterns.py:61:TIER1_PHRASES = [
skills/ai-writing-suite/evals/detector/patterns.py:62:    (re.compile(r"\bdelve\s+into\b", re.I), "explore, dig into"),
skills/ai-writing-suite/evals/detector/patterns.py:63:    (re.compile(r"\blandscape\b", re.I), "field, space, industry"),
skills/ai-writing-suite/evals/detector/patterns.py:64:    (re.compile(r"\brealm\b", re.I), "area, field, domain"),
skills/ai-writing-suite/evals/detector/patterns.py:65:    (re.compile(r"\btestament\s+to\b", re.I), "shows, proves"),
skills/ai-writing-suite/evals/detector/patterns.py:66:    (re.compile(r"\bleverage\b", re.I), "use"),
skills/ai-writing-suite/evals/detector/patterns.py:67:    (re.compile(r"\bwatershed\s+moment\b", re.I), "turning point, shift"),
skills/ai-writing-suite/evals/detector/patterns.py:68:    (re.compile(r"\bdeep\s+dive\b", re.I), "look at, examine"),
skills/ai-writing-suite/evals/detector/patterns.py:69:    (re.compile(r"\bdive\s+into\b", re.I), "look at, examine"),
skills/ai-writing-suite/evals/detector/patterns.py:70:    (re.compile(r"\bunpack(?:ing)?\b", re.I), "explain, break down"),
skills/ai-writing-suite/evals/detector/patterns.py:71:    (re.compile(r"\bthought\s+leader(?:ship)?\b", re.I), "expert, authority"),
skills/ai-writing-suite/evals/detector/patterns.py:72:    (re.compile(r"\bbest\s+practices\b", re.I), "what works, proven methods"),
skills/ai-writing-suite/evals/detector/patterns.py:73:    (re.compile(r"\bat\s+its\s+core\b", re.I), "cut, just state it"),
skills/ai-writing-suite/evals/detector/patterns.py:74:    (re.compile(r"\bin\s+order\s+to\b", re.I), "to"),
skills/ai-writing-suite/evals/detector/patterns.py:75:    (re.compile(r"\bdue\s+to\s+the\s+fact\s+that\b", re.I), "because"),
skills/ai-writing-suite/evals/detector/patterns.py:76:    (re.compile(r"\bserves\s+as\b", re.I), "is"),
skills/ai-writing-suite/evals/detector/patterns.py:77:    (re.compile(r"\bboasts\b", re.I), "has"),
skills/ai-writing-suite/evals/detector/patterns.py:78:]
skills/ai-writing-suite/evals/detector/patterns.py:79:
skills/ai-writing-suite/evals/detector/patterns.py:80:# --- Tier 2: flag in clusters of 2+ per paragraph (catalog L1 tier 2) -----
skills/ai-writing-suite/evals/detector/patterns.py:81:TIER2 = {
skills/ai-writing-suite/evals/detector/patterns.py:82:    "harness": "use, take advantage of",
skills/ai-writing-suite/evals/detector/patterns.py:83:    "navigate": "work through, handle",
skills/ai-writing-suite/evals/detector/patterns.py:84:    "navigating": "working through, handling",
skills/ai-writing-suite/evals/detector/patterns.py:85:    "foster": "encourage, support, build",
skills/ai-writing-suite/evals/detector/patterns.py:86:    "elevate": "improve, raise, strengthen",
skills/ai-writing-suite/evals/detector/patterns.py:87:    "unleash": "release, enable, unlock",
skills/ai-writing-suite/evals/detector/patterns.py:88:    "streamline": "simplify, speed up",
skills/ai-writing-suite/evals/detector/patterns.py:89:    "empower": "enable, let, allow",
skills/ai-writing-suite/evals/detector/patterns.py:90:    "bolster": "support, strengthen",
skills/ai-writing-suite/evals/detector/patterns.py:91:    "spearhead": "lead, drive, run",
skills/ai-writing-suite/evals/detector/patterns.py:92:    "resonate": "connect with, appeal to",
skills/ai-writing-suite/evals/detector/patterns.py:93:    "resonates": "connects with, appeals to",
skills/ai-writing-suite/evals/detector/patterns.py:94:    "revolutionize": "change, transform",
skills/ai-writing-suite/evals/detector/patterns.py:95:    "facilitate": "enable, help, allow",
skills/ai-writing-suite/evals/detector/patterns.py:96:    "facilitates": "enables, helps, allows",
skills/ai-writing-suite/evals/detector/patterns.py:97:    "underpin": "support, form the basis of",
skills/ai-writing-suite/evals/detector/patterns.py:98:    "nuanced": "specific, subtle, detailed",
skills/ai-writing-suite/evals/detector/patterns.py:99:    "crucial": "important, key, necessary",
skills/ai-writing-suite/evals/detector/patterns.py:100:    "multifaceted": "describe the actual facets",
skills/ai-writing-suite/evals/detector/patterns.py:101:    "ecosystem": "system, community, network",
skills/ai-writing-suite/evals/detector/patterns.py:102:    "myriad": "many, numerous",
skills/ai-writing-suite/evals/detector/patterns.py:103:    "plethora": "many, a lot of",
skills/ai-writing-suite/evals/detector/patterns.py:104:    "encompass": "include, cover, span",
skills/ai-writing-suite/evals/detector/patterns.py:105:    "catalyze": "start, trigger, accelerate",
skills/ai-writing-suite/evals/detector/patterns.py:106:    "reimagine": "rethink, redesign, rebuild",
skills/ai-writing-suite/evals/detector/patterns.py:107:    "galvanize": "motivate, rally, push",
skills/ai-writing-suite/evals/detector/patterns.py:108:    "augment": "add to, expand, supplement",
skills/ai-writing-suite/evals/detector/patterns.py:109:    "cultivate": "build, develop, grow",
skills/ai-writing-suite/evals/detector/patterns.py:110:    "illuminate": "clarify, explain, show",
skills/ai-writing-suite/evals/detector/patterns.py:111:    "elucidate": "explain, clarify",
skills/ai-writing-suite/evals/detector/patterns.py:112:    "transformative": "describe what changed",
skills/ai-writing-suite/evals/detector/patterns.py:113:    "transformation": "describe what changed",
skills/ai-writing-suite/evals/detector/patterns.py:114:    "cornerstone": "foundation, basis, key part",
skills/ai-writing-suite/evals/detector/patterns.py:115:    "paramount": "most important, top priority",
skills/ai-writing-suite/evals/detector/patterns.py:116:    "poised": "ready, set, about to",
skills/ai-writing-suite/evals/detector/patterns.py:117:    "burgeoning": "growing, emerging",
skills/ai-writing-suite/evals/detector/patterns.py:118:    "nascent": "new, early-stage",
skills/ai-writing-suite/evals/detector/patterns.py:119:    "quintessential": "typical, classic, defining",
skills/ai-writing-suite/evals/detector/patterns.py:120:    "overarching": "main, central, broad",
skills/ai-writing-suite/evals/detector/patterns.py:121:    "underpinning": "basis, foundation",
skills/ai-writing-suite/evals/detector/patterns.py:122:}
skills/ai-writing-suite/evals/detector/patterns.py:123:
skills/ai-writing-suite/evals/detector/patterns.py:124:# --- Tier 3: flag only at high density (catalog L1 tier 3) -----------------
skills/ai-writing-suite/evals/detector/patterns.py:125:TIER3 = [
skills/ai-writing-suite/evals/detector/patterns.py:126:    "significant", "significantly", "innovative", "innovation",
skills/ai-writing-suite/evals/detector/patterns.py:127:    "effective", "effectively", "dynamic", "scalable",
skills/ai-writing-suite/evals/detector/patterns.py:128:    "compelling", "unprecedented", "exceptional", "remarkable",
skills/ai-writing-suite/evals/detector/patterns.py:129:    "sophisticated", "instrumental",
skills/ai-writing-suite/evals/detector/patterns.py:130:    "world-class", "state-of-the-art", "best-in-class",
skills/ai-writing-suite/evals/detector/patterns.py:131:]
skills/ai-writing-suite/evals/detector/patterns.py:132:# Lookup tolerant of hyphen-stripped forms ("state-of-the-art" / "stateoftheart").
skills/ai-writing-suite/evals/detector/patterns.py:133:TIER3_LOOKUP = {}
skills/ai-writing-suite/evals/detector/patterns.py:134:for _w in TIER3:
skills/ai-writing-suite/evals/detector/patterns.py:135:    TIER3_LOOKUP[_w] = _w
skills/ai-writing-suite/evals/detector/patterns.py:136:    _dashless = _w.replace("-", "")
skills/ai-writing-suite/evals/detector/patterns.py:137:    if _dashless != _w:
skills/ai-writing-suite/evals/detector/patterns.py:138:        TIER3_LOOKUP[_dashless] = _w
skills/ai-writing-suite/evals/detector/patterns.py:139:
skills/ai-writing-suite/evals/detector/patterns.py:140:# Multi-word Tier 3 boilerplate (significance-attribution / consultant-speak).
skills/ai-writing-suite/evals/detector/patterns.py:141:TIER3_PHRASES = [
skills/ai-writing-suite/evals/detector/patterns.py:142:    re.compile(r"\bemerging\s+(?:sector|space|category|industry)\b", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:143:    re.compile(r"\bthe\s+integration\s+of\b", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:144:    re.compile(r"\bthe\s+intersection\s+of\b", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:145:    re.compile(r"\bcommunity-?driven\b", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:146:    re.compile(r"\blong-?term\s+sustainability\b", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:147:    re.compile(r"\buser\s+engagement\b", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:148:    re.compile(r"\bdesigned\s+for\s+long-?term\b", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:149:]
skills/ai-writing-suite/evals/detector/patterns.py:150:
skills/ai-writing-suite/evals/detector/patterns.py:151:# --- Phrase-list categories -----------------------------------------------
skills/ai-writing-suite/evals/detector/patterns.py:152:# Each maps to a catalog category; see CATEGORIES.md for the SKILL <-> type map.
skills/ai-writing-suite/evals/detector/patterns.py:153:TRANSITIONS = [  # hedging-filler: signposting
skills/ai-writing-suite/evals/detector/patterns.py:154:    re.compile(r"\bmoreover\b", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:155:    re.compile(r"\bfurthermore\b", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:156:    re.compile(r"\badditionally\b", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:157:    re.compile(r"\bin\s+today'?s\b", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:158:    re.compile(r"\bin\s+an\s+era\s+where\b", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:159:    re.compile(r"\bit'?s\s+worth\s+noting\s+that\b", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:160:    re.compile(r"\bnotably\b", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:161:    re.compile(r"\bin\s+conclusion\b", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:162:    re.compile(r"\bin\s+summary\b", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:163:    re.compile(r"\bwhen\s+it\s+comes\s+to\b", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:164:    re.compile(r"\bat\s+the\s+end\s+of\s+the\s+day\b", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:165:    re.compile(r"\bthat\s+(?:being\s+)?said\b", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:166:]
skills/ai-writing-suite/evals/detector/patterns.py:167:
skills/ai-writing-suite/evals/detector/patterns.py:168:CHATBOT_ARTIFACTS = [  # communication-artifacts: chatbot tics
skills/ai-writing-suite/evals/detector/patterns.py:169:    re.compile(r"\bi\s+hope\s+this\s+helps\b", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:170:    re.compile(r"\bcertainly!\b", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:171:    re.compile(r"\babsolutely!\b", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:172:    re.compile(r"\bgreat\s+question!\b", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:173:    re.compile(r"\bfeel\s+free\s+to\s+reach\s+out\b", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:174:    re.compile(r"\blet\s+me\s+know\s+if\s+you\s+need\s+anything\b", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:175:    re.compile(r"\bin\s+this\s+article,?\s+we\s+will\s+explore\b", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:176:    re.compile(r"\blet'?s\s+dive\s+in!?\b", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:177:]
skills/ai-writing-suite/evals/detector/patterns.py:178:
skills/ai-writing-suite/evals/detector/patterns.py:179:SYCOPHANTIC = [  # communication-artifacts: sycophancy
skills/ai-writing-suite/evals/detector/patterns.py:180:    re.compile(r"\byou'?re\s+absolutely\s+right\b", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:181:    re.compile(r"\bthat'?s\s+a\s+really\s+insightful\b", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:182:    re.compile(r"\bthat'?s\s+a\s+great\s+question\b", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:183:    re.compile(r"\bexcellent\s+question\b", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:184:]
skills/ai-writing-suite/evals/detector/patterns.py:185:
skills/ai-writing-suite/evals/detector/patterns.py:186:FILLERS = [  # hedging-filler: filler phrases
skills/ai-writing-suite/evals/detector/patterns.py:187:    re.compile(r"\bit\s+is\s+important\s+to\s+note\s+that\b", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:188:    re.compile(r"\bin\s+terms\s+of\b", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:189:    re.compile(r"\bthe\s+reality\s+is\s+that\b", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:190:    re.compile(r"\bit'?s\s+important\s+to\s+note\s+that\b", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:191:]
skills/ai-writing-suite/evals/detector/patterns.py:192:
skills/ai-writing-suite/evals/detector/patterns.py:193:GENERIC_CONCLUSIONS = [  # hedging-filler: generic conclusions
skills/ai-writing-suite/evals/detector/patterns.py:194:    re.compile(r"\bthe\s+future\s+looks\s+bright\b", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:195:    re.compile(r"\bonly\s+time\s+will\s+tell\b", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:196:    re.compile(r"\bone\s+thing\s+is\s+certain\b", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:197:    re.compile(r"\bas\s+we\s+move\s+forward\b", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:198:]
skills/ai-writing-suite/evals/detector/patterns.py:199:
skills/ai-writing-suite/evals/detector/patterns.py:200:LETS_PATTERNS = [  # hedging-filler: "let's" openers
skills/ai-writing-suite/evals/detector/patterns.py:201:    re.compile(r"\blet'?s\s+explore\b", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:202:    re.compile(r"\blet'?s\s+take\s+a\s+look\b", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:203:    re.compile(r"\blet'?s\s+break\s+this\s+down\b", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:204:    re.compile(r"\blet'?s\s+examine\b", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:205:    re.compile(r"\blet'?s\s+(?:consider|discuss|delve|unpack|walk\s+through)\b", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:206:]
skills/ai-writing-suite/evals/detector/patterns.py:207:
skills/ai-writing-suite/evals/detector/patterns.py:208:REASONING_ARTIFACTS = [  # communication-artifacts: reasoning-chain leaks
skills/ai-writing-suite/evals/detector/patterns.py:209:    re.compile(r"\blet\s+me\s+think\s+step\s+by\s+step\b", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:210:    re.compile(r"\bbreaking\s+this\s+down\b", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:211:    re.compile(r"\bto\s+approach\s+this\s+systematically\b", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:212:    re.compile(r"\bhere'?s\s+my\s+thought\s+process\b", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:213:    re.compile(r"\bfirst,?\s+let'?s\s+consider\b", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:214:    re.compile(r"\bworking\s+through\s+this\s+logically\b", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:215:]
skills/ai-writing-suite/evals/detector/patterns.py:216:
skills/ai-writing-suite/evals/detector/patterns.py:217:ACKNOWLEDGMENT_LOOPS = [  # communication-artifacts: acknowledgment loops
skills/ai-writing-suite/evals/detector/patterns.py:218:    re.compile(r"\byou'?re\s+asking\s+about\b", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:219:    re.compile(r"\bthe\s+question\s+of\s+whether\b", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:220:    re.compile(r"\bto\s+answer\s+your\s+question\b", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:221:]
skills/ai-writing-suite/evals/detector/patterns.py:222:
skills/ai-writing-suite/evals/detector/patterns.py:223:SIGNIFICANCE_INFLATION = [  # significance-attribution: significance inflation
skills/ai-writing-suite/evals/detector/patterns.py:224:    re.compile(r"\bmarking\s+a\s+(?:pivotal|significant|important)\s+moment\b", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:225:    re.compile(r"\ba\s+watershed\s+moment\s+for\b", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:226:    re.compile(r"\bin\s+the\s+evolution\s+of\b", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:227:    re.compile(r"\ba\s+(?:pivotal|defining)\s+moment\s+in\b", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:228:]
skills/ai-writing-suite/evals/detector/patterns.py:229:
skills/ai-writing-suite/evals/detector/patterns.py:230:VAGUE_ATTRIBUTIONS = [  # significance-attribution: vague attribution
skills/ai-writing-suite/evals/detector/patterns.py:231:    re.compile(r"\bexperts\s+(?:believe|say|suggest|agree)\b", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:232:    re.compile(r"\bstudies\s+(?:show|suggest|indicate)\b", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:233:    re.compile(r"\bresearch\s+(?:shows|suggests|indicates)\b", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:234:    re.compile(r"\bindustry\s+leaders\s+(?:agree|believe|say)\b", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:235:]
skills/ai-writing-suite/evals/detector/patterns.py:236:
skills/ai-writing-suite/evals/detector/patterns.py:237:HOLLOW_INTENSIFIERS = [  # lexical-tells: hollow intensifiers
skills/ai-writing-suite/evals/detector/patterns.py:238:    re.compile(r"\bgenuine(?:ly)?\b", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:239:    re.compile(r"\btruly\b", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:240:    re.compile(r"\bquite\s+frankly\b", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:241:    re.compile(r"\bto\s+be\s+honest\b", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:242:    re.compile(r"\blet'?s\s+be\s+clear\b", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:243:]
skills/ai-writing-suite/evals/detector/patterns.py:244:
skills/ai-writing-suite/evals/detector/patterns.py:245:EMOTIONAL_FLATLINE = [  # communication-artifacts: emotional flatline
skills/ai-writing-suite/evals/detector/patterns.py:246:    re.compile(r"\bwhat\s+surprised\s+me\s+most\b", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:247:    re.compile(r"\bi\s+was\s+fascinated\s+to\b", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:248:    re.compile(r"\bwhat\s+struck\s+me\s+was\b", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:249:    re.compile(r"\bi\s+was\s+excited\s+to\s+learn\b", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:250:    re.compile(r"\bthe\s+most\s+interesting\s+(?:part|thing|aspect|piece)\b", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:251:    re.compile(r"^\s*interesting\s+(?:part|thing|aspect|piece)(?:\s+of\s+(?:the\s+)?\w+)?\s*:", re.I | re.M),
skills/ai-writing-suite/evals/detector/patterns.py:252:]
skills/ai-writing-suite/evals/detector/patterns.py:253:
skills/ai-writing-suite/evals/detector/patterns.py:254:NOVELTY_INFLATION = [  # significance-attribution: novelty inflation
skills/ai-writing-suite/evals/detector/patterns.py:255:    re.compile(r"\bthe\s+failure\s+mode\s+nobody'?s?\s+naming\b", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:256:    re.compile(r"\ba\s+problem\s+nobody\s+talks\s+about\b", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:257:    re.compile(r"\bthe\s+insight\s+everyone'?s?\s+missing\b", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:258:    re.compile(r"\bwhat\s+nobody\s+tells\s+you\b", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:259:]
skills/ai-writing-suite/evals/detector/patterns.py:260:
skills/ai-writing-suite/evals/detector/patterns.py:261:CUTOFF_DISCLAIMERS = [  # communication-artifacts: cutoff disclaimers
skills/ai-writing-suite/evals/detector/patterns.py:262:    re.compile(r"\bas\s+of\s+my\s+last\s+update\b", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:263:    re.compile(r"\bas\s+of\s+my\s+(?:knowledge\s+)?(?:cut-?off|last\s+training)\b", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:264:    re.compile(r"\bi\s+don'?t\s+have\s+access\s+to\s+real-?time\s+(?:data|information)\b", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:265:    re.compile(r"\bas\s+an?\s+(?:ai|artificial\s+intelligence|large\s+language|ai\s+language)\s+(?:language\s+)?model\b", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:266:    re.compile(r"\bi\s+(?:am|'m)\s+an?\s+(?:ai|artificial\s+intelligence|large\s+language)\s+(?:assistant|model)?\b", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:267:    re.compile(r"\bmy\s+training\s+data\s+(?:only\s+)?(?:goes\s+up\s+to|extends\s+to|ends\s+(?:in|at))\b", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:268:]
skills/ai-writing-suite/evals/detector/patterns.py:269:
skills/ai-writing-suite/evals/detector/patterns.py:270:# AI-tool fingerprints (punctuation-formatting: placeholders / citation / UTM).
skills/ai-writing-suite/evals/detector/patterns.py:271:AI_PLACEHOLDERS = [
skills/ai-writing-suite/evals/detector/patterns.py:272:    re.compile(r"\[(?:Your|Insert|Add|Enter|Describe|Specify|Choose|Pick)[^\]\n]{1,80}\]", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:273:    re.compile(r"\[(?:Recipient|Sender|Topic|Subject|Salutation|Closing|Position|Department|Project Name|Company Name|Date)(?:\s+[^\]\n]{0,60})?\]", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:274:    re.compile(r"\[(?:INSERT|FILL\s+IN|ADD|TODO|TBD|PLACEHOLDER)[^\]\n]{0,80}\]"),
skills/ai-writing-suite/evals/detector/patterns.py:275:    re.compile(r"<!--\s*(?:add|fill\s+in|insert|todo|placeholder)[^>]{0,120}-->", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:276:]
skills/ai-writing-suite/evals/detector/patterns.py:277:AI_CITATION_MARKUP = [
skills/ai-writing-suite/evals/detector/patterns.py:278:    re.compile(r"\bcite(?:turn|news|search|navigation)\d+(?:search|turn|news|navigation)\d+", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:279:    re.compile(r"contentReference\s*\[oaicite:[^\]]+\]\s*\{[^}]*\}", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:280:    re.compile(r"\boai_citation\b", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:281:    re.compile(r"\bgrok_card\b", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:282:]
skills/ai-writing-suite/evals/detector/patterns.py:283:AI_UTM_SOURCE = [
skills/ai-writing-suite/evals/detector/patterns.py:284:    re.compile(r"[?&]utm_source=(?:chatgpt|openai|copilot|claude|grok|gemini|perplexity)(?:\.com|\.ai)?\b", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:285:    re.compile(r"[?&]referrer=(?:chatgpt|copilot|grok|claude|gemini|perplexity)\.(?:com|ai)\b", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:286:]
skills/ai-writing-suite/evals/detector/patterns.py:287:
skills/ai-writing-suite/evals/detector/patterns.py:288:TEMPLATE_PHRASES = [  # structural-tells: template phrases
skills/ai-writing-suite/evals/detector/patterns.py:289:    re.compile(r"\ba\s+\w+\s+step\s+(?:towards?|forward\s+for)\b", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:290:    re.compile(r"\bwhether\s+you'?re\s+\w+\s+or\s+\w+", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:291:    re.compile(r"\bi\s+recently\s+had\s+the\s+pleasure\s+of\b", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:292:]
skills/ai-writing-suite/evals/detector/patterns.py:293:
skills/ai-writing-suite/evals/detector/patterns.py:294:FALSE_CONCESSION = [  # structural-tells: false concession
skills/ai-writing-suite/evals/detector/patterns.py:295:    re.compile(r"\bwhile\s+\w+\s+is\s+impressive\b", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:296:    re.compile(r"\balthough\s+\w+\s+has\s+made\s+strides\b", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:297:    re.compile(r"\bdespite\s+\w+\s+challenges?\b", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:298:]
skills/ai-writing-suite/evals/detector/patterns.py:299:
skills/ai-writing-suite/evals/detector/patterns.py:300:RHETORICAL_QUESTIONS = [  # structural-tells: rhetorical question openers
skills/ai-writing-suite/evals/detector/patterns.py:301:    re.compile(r"\bbut\s+what\s+does\s+this\s+mean\s+for\b", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:302:    re.compile(r"\bso\s+why\s+should\s+you\s+care\b", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:303:    re.compile(r"\bwhat'?s\s+next\?", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:304:]
skills/ai-writing-suite/evals/detector/patterns.py:305:
skills/ai-writing-suite/evals/detector/patterns.py:306:HEDGE_STACK = [  # hedging-filler: stacked hedging
skills/ai-writing-suite/evals/detector/patterns.py:307:    re.compile(r"\b(?:could|may|might)\s+(?:\w+\s+){0,2}(?:potentially|eventually|ultimately|possibly|conceivably)\b", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:308:    re.compile(r"\b(?:potentially|eventually|ultimately)\s+(?:could|may|might)\b", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:309:]
skills/ai-writing-suite/evals/detector/patterns.py:310:
skills/ai-writing-suite/evals/detector/patterns.py:311:FUTURE_NARRATIVE = [  # hedging-filler: future-narrative closers
skills/ai-writing-suite/evals/detector/patterns.py:312:    re.compile(r"\b(?:may|could|will|is\s+(?:poised|set)\s+to)\s+become\s+(?:one\s+of\s+)?(?:the\s+)?(?:most\s+)?\w+\s+(?:narratives?|stories|developments?|trends?|movements?|chapters?|themes?|forces?)\b", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:313:    re.compile(r"\bone\s+of\s+the\s+most\s+important\s+(?:narratives?|stories|trends?|themes?)\s+of\s+the\s+(?:next|coming)\s+\w+\b", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:314:]
skills/ai-writing-suite/evals/detector/patterns.py:315:
skills/ai-writing-suite/evals/detector/patterns.py:316:REAL_ACTUAL_INFLATION = [  # significance-attribution: real/actual inflation
skills/ai-writing-suite/evals/detector/patterns.py:317:    re.compile(r"\b(?:real|actual|genuine|true)\s+(?:on-?chain\s+)?(?:tokenomics|economics|utility|adoption|sustainability|impact|revenue|fundamentals|demand|value|innovation|traction)\b", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:318:]
skills/ai-writing-suite/evals/detector/patterns.py:319:
skills/ai-writing-suite/evals/detector/patterns.py:320:FORMULAIC_OPENERS = [  # structural-tells: formulaic challenges / essay openers
skills/ai-writing-suite/evals/detector/patterns.py:321:    re.compile(r"\bin\s+the\s+(?:rapidly\s+|ever-?\s*)?(?:evolving|changing|expanding|growing|shifting)\s+(?:world|landscape|realm|space|field|domain|era)\s+of\b", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:322:    re.compile(r"\bin\s+(?:an?|the)\s+(?:digital\s+)?age\s+(?:where|of)\b", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:323:    re.compile(r"\bhas\s+emerged\s+as\s+(?:a|the|one\s+of)\s+(?:leading|key|major|critical|essential|fundamental|pivotal|prominent|dominant|important)\s+\w+", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:324:    re.compile(r"\bhas\s+become\s+increasingly\s+(?:important|critical|popular|relevant|prominent|essential)\b", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:325:]
skills/ai-writing-suite/evals/detector/patterns.py:326:
skills/ai-writing-suite/evals/detector/patterns.py:327:# Title-case section header (punctuation-formatting). Gated off in 'technical'.
skills/ai-writing-suite/evals/detector/patterns.py:328:TITLE_CASE_HEADER = re.compile(
skills/ai-writing-suite/evals/detector/patterns.py:329:    r"^([A-Z][a-z]+(?:\s+(?:[A-Z][a-z]+|and|or|of|the|in|for|to|a|an))+\s+[A-Z][a-z]+)\s*$",
skills/ai-writing-suite/evals/detector/patterns.py:330:    re.M,
skills/ai-writing-suite/evals/detector/patterns.py:331:)
skills/ai-writing-suite/evals/detector/patterns.py:332:
skills/ai-writing-suite/evals/detector/patterns.py:333:CONFIDENCE_CALIBRATION = [  # hedging-filler: confidence-calibration phrases
skills/ai-writing-suite/evals/detector/patterns.py:334:    re.compile(r"\binterestingly\b", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:335:    re.compile(r"\bsurprisingly\b", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:336:    re.compile(r"\bimportantly\b", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:337:    re.compile(r"\bcertainly\b", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:338:    re.compile(r"\bundoubtedly\b", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:339:    re.compile(r"\bwithout\s+a\s+doubt\b", re.I),
skills/ai-writing-suite/evals/detector/patterns.py:340:]
skills/ai-writing-suite/evals/detector/patterns.py:341:
skills/ai-writing-suite/evals/detector/patterns.py:342:# --- Per-category score weights (ported from JS ISSUE_WEIGHTS) -------------
skills/ai-writing-suite/evals/detector/patterns.py:343:# Non-flat on purpose: a cutoff disclaimer (LLM self-ID) is far stronger
skills/ai-writing-suite/evals/detector/patterns.py:344:# evidence than one vague attribution. Structural/cluster signals weigh high
skills/ai-writing-suite/evals/detector/patterns.py:345:# because they would otherwise be washed out by the length divisor on short
skills/ai-writing-suite/evals/detector/patterns.py:346:# social posts.
skills/ai-writing-suite/evals/detector/patterns.py:347:ISSUE_WEIGHTS = {
skills/ai-writing-suite/evals/detector/patterns.py:348:    "tier1": 5, "tier2": 3, "tier3": 2, "transition": 2,
skills/ai-writing-suite/evals/detector/patterns.py:349:    "chatbot": 8, "sycophantic": 8, "filler": 2, "generic-conclusion": 3,
skills/ai-writing-suite/evals/detector/patterns.py:350:    "lets-construction": 2, "reasoning-artifact": 6, "acknowledgment-loop": 3,
skills/ai-writing-suite/evals/detector/patterns.py:351:    "significance-inflation": 4, "vague-attribution": 5, "hollow-intensifier": 2,
skills/ai-writing-suite/evals/detector/patterns.py:352:    "emotional-flatline": 2, "novelty-inflation": 3, "cutoff-disclaimer": 10,
skills/ai-writing-suite/evals/detector/patterns.py:353:    "template-phrase": 3, "false-concession": 2, "rhetorical-question": 2,
skills/ai-writing-suite/evals/detector/patterns.py:354:    "confidence-calibration": 2, "em-dash": 4, "uniformity": 5, "formatting": 3,
skills/ai-writing-suite/evals/detector/patterns.py:355:    "tier3-phrase": 3, "tier3-phrase-cluster": 12, "hashtag-stuff": 12,
skills/ai-writing-suite/evals/detector/patterns.py:356:    "bullet-np-list": 10, "hedge-stack": 6, "future-narrative": 12,
skills/ai-writing-suite/evals/detector/patterns.py:357:    "real-actual-inflation": 5, "formulaic-opener": 8, "title-case-header": 4,
skills/ai-writing-suite/evals/detector/patterns.py:358:    "low-ttr": 3, "ai-placeholder": 10, "ai-citation-markup": 15,
skills/ai-writing-suite/evals/detector/patterns.py:359:    "ai-utm-source": 12,
skills/ai-writing-suite/evals/detector/patterns.py:360:}
skills/ai-writing-suite/evals/smoke_test.py:1:#!/usr/bin/env python3
skills/ai-writing-suite/evals/smoke_test.py:2:"""Automate the KB ingestion+retrieval smoke test (design D12).
skills/ai-writing-suite/evals/smoke_test.py:3:
skills/ai-writing-suite/evals/smoke_test.py:4:WHY this exists: the product promise is "a company drops in a markdown page,
skills/ai-writing-suite/evals/smoke_test.py:5:not builds a retrieval engine." That holds only if ONE end-to-end chain works:
skills/ai-writing-suite/evals/smoke_test.py:6:query -> scan INDEX.md keywords/summary -> open the right entry -> quote the
skills/ai-writing-suite/evals/smoke_test.py:7:right passage. This script proves that chain deterministically, with zero deps
skills/ai-writing-suite/evals/smoke_test.py:8:and no embeddings (design D5 — retrieval is pure markdown navigation).
skills/ai-writing-suite/evals/smoke_test.py:9:
skills/ai-writing-suite/evals/smoke_test.py:10:It parses the TEST CASE blocks in `_shared/knowledge/SMOKE-TEST.md`, replicates
skills/ai-writing-suite/evals/smoke_test.py:11:the INDEX.md retrieval protocol in code, and asserts (a) the retrieved entry
skills/ai-writing-suite/evals/smoke_test.py:12:filename equals the expected entry and (b) the expected passage exists in that
skills/ai-writing-suite/evals/smoke_test.py:13:entry file.
skills/ai-writing-suite/evals/smoke_test.py:14:
skills/ai-writing-suite/evals/smoke_test.py:15:Run:  python3 smoke_test.py     (exit 0 = all cases pass)
skills/ai-writing-suite/evals/smoke_test.py:16:"""
skills/ai-writing-suite/evals/smoke_test.py:17:
skills/ai-writing-suite/evals/smoke_test.py:18:import os
skills/ai-writing-suite/evals/smoke_test.py:19:import re
skills/ai-writing-suite/evals/smoke_test.py:20:import sys
skills/ai-writing-suite/evals/smoke_test.py:21:
skills/ai-writing-suite/evals/smoke_test.py:22:HERE = os.path.dirname(os.path.abspath(__file__))
skills/ai-writing-suite/evals/smoke_test.py:23:KB = os.path.normpath(os.path.join(HERE, "..", "_shared", "knowledge"))
skills/ai-writing-suite/evals/smoke_test.py:24:INDEX_PATH = os.path.join(KB, "INDEX.md")
skills/ai-writing-suite/evals/smoke_test.py:25:SMOKE_PATH = os.path.join(KB, "SMOKE-TEST.md")
skills/ai-writing-suite/evals/smoke_test.py:26:
skills/ai-writing-suite/evals/smoke_test.py:27:# Stop words excluded from query<->keyword overlap. WHY: function words appear
skills/ai-writing-suite/evals/smoke_test.py:28:# in every entry's summary, so counting them would let any query "match"
skills/ai-writing-suite/evals/smoke_test.py:29:# everything. This is the deterministic stand-in for what the agent does when
skills/ai-writing-suite/evals/smoke_test.py:30:# it "scans for term overlap" under the INDEX retrieval protocol.
skills/ai-writing-suite/evals/smoke_test.py:31:#
skills/ai-writing-suite/evals/smoke_test.py:32:# Keep this list to TRUE function words only. We deliberately do NOT strip
skills/ai-writing-suite/evals/smoke_test.py:33:# content words like "too", "much", "fix", or "writing" — those carry the
skills/ai-writing-suite/evals/smoke_test.py:34:# retrieval signal (e.g. "too long" / "say too much" map to clarity's verbose/
skills/ai-writing-suite/evals/smoke_test.py:35:# wordy keywords). Over-stripping content words is how a keyword index loses
skills/ai-writing-suite/evals/smoke_test.py:36:# recall, which is the exact failure mode the SMOKE-TEST calibration note warns
skills/ai-writing-suite/evals/smoke_test.py:37:# about.
skills/ai-writing-suite/evals/smoke_test.py:38:STOPWORDS = {
skills/ai-writing-suite/evals/smoke_test.py:39:    "the", "a", "an", "and", "or", "but", "to", "of", "in", "on", "at", "for",
skills/ai-writing-suite/evals/smoke_test.py:40:    "with", "is", "are", "was", "were", "be", "been", "it", "its", "this",
skills/ai-writing-suite/evals/smoke_test.py:41:    "that", "these", "those", "i", "you", "we", "they", "my", "your", "our",
skills/ai-writing-suite/evals/smoke_test.py:42:    "me", "do", "does", "did", "i'm", "im", "even", "all", "am", "so", "if",
skills/ai-writing-suite/evals/smoke_test.py:43:    "as", "by", "from", "about", "into", "out", "up", "down",
skills/ai-writing-suite/evals/smoke_test.py:44:    # Near-function words and ubiquitous tokens with no retrieval signal.
skills/ai-writing-suite/evals/smoke_test.py:45:    # "like"/"no" are the disambiguation LURES the SMOKE-TEST note calls out
skills/ai-writing-suite/evals/smoke_test.py:46:    # (they pull toward tone via "sounds like AI"/"no sycophancy"); "one"
skills/ai-writing-suite/evals/smoke_test.py:47:    # appears in 3+ entries so it discriminates nothing. Dropping them is
skills/ai-writing-suite/evals/smoke_test.py:48:    # query normalization, not KB editing — the INDEX stays untouched.
skills/ai-writing-suite/evals/smoke_test.py:49:    "like", "no", "one",
skills/ai-writing-suite/evals/smoke_test.py:50:}
skills/ai-writing-suite/evals/smoke_test.py:51:
skills/ai-writing-suite/evals/smoke_test.py:52:
skills/ai-writing-suite/evals/smoke_test.py:53:def tokens(text):
skills/ai-writing-suite/evals/smoke_test.py:54:    return [t for t in re.findall(r"[a-z']+", text.lower()) if t not in STOPWORDS]
skills/ai-writing-suite/evals/smoke_test.py:55:
skills/ai-writing-suite/evals/smoke_test.py:56:
skills/ai-writing-suite/evals/smoke_test.py:57:# ── Parse INDEX.md entries table ──────────────────────────────────────────
skills/ai-writing-suite/evals/smoke_test.py:58:def load_index():
skills/ai-writing-suite/evals/smoke_test.py:59:    """Return [{file, summary, keywords, summary_kw}] from the Entries table.
skills/ai-writing-suite/evals/smoke_test.py:60:
skills/ai-writing-suite/evals/smoke_test.py:61:    `keywords` = the Keywords/aliases column only. `summary_kw` = the Summary
skills/ai-writing-suite/evals/smoke_test.py:62:    column tokens. We keep them separate so retrieve() can implement the
skills/ai-writing-suite/evals/smoke_test.py:63:    documented two-step protocol: keyword overlap first, summary-intent overlap
skills/ai-writing-suite/evals/smoke_test.py:64:    as the tie-breaker.
skills/ai-writing-suite/evals/smoke_test.py:65:    """
skills/ai-writing-suite/evals/smoke_test.py:66:    with open(INDEX_PATH, encoding="utf-8") as fh:
skills/ai-writing-suite/evals/smoke_test.py:67:        lines = fh.readlines()
skills/ai-writing-suite/evals/smoke_test.py:68:    entries = []
skills/ai-writing-suite/evals/smoke_test.py:69:    in_table = False
skills/ai-writing-suite/evals/smoke_test.py:70:    for line in lines:
skills/ai-writing-suite/evals/smoke_test.py:71:        # Entry rows look like: | `clarity.md` | summary... | kw, kw, ... |
skills/ai-writing-suite/evals/smoke_test.py:72:        m = re.match(r"\|\s*`([^`]+\.md)`\s*\|(.+?)\|(.+?)\|\s*$", line)
skills/ai-writing-suite/evals/smoke_test.py:73:        if m:
skills/ai-writing-suite/evals/smoke_test.py:74:            in_table = True
skills/ai-writing-suite/evals/smoke_test.py:75:            fname, summary, kws = m.group(1), m.group(2), m.group(3)
skills/ai-writing-suite/evals/smoke_test.py:76:            entries.append({"file": fname.strip(),
skills/ai-writing-suite/evals/smoke_test.py:77:                            "summary": summary.strip(),
skills/ai-writing-suite/evals/smoke_test.py:78:                            "keywords": set(tokens(kws)),
skills/ai-writing-suite/evals/smoke_test.py:79:                            "summary_kw": set(tokens(summary))})
skills/ai-writing-suite/evals/smoke_test.py:80:        elif in_table and line.strip() == "":
skills/ai-writing-suite/evals/smoke_test.py:81:            break
skills/ai-writing-suite/evals/smoke_test.py:82:    return entries
skills/ai-writing-suite/evals/smoke_test.py:83:
skills/ai-writing-suite/evals/smoke_test.py:84:
skills/ai-writing-suite/evals/smoke_test.py:85:def retrieve(query, entries):
skills/ai-writing-suite/evals/smoke_test.py:86:    """Replicate the INDEX retrieval protocol (two steps, in order):
skills/ai-writing-suite/evals/smoke_test.py:87:      1. Scan the Keywords/aliases column for term overlap.
skills/ai-writing-suite/evals/smoke_test.py:88:      2. Use Summary-column (intent) overlap to break keyword ties.
skills/ai-writing-suite/evals/smoke_test.py:89:    Pick the single best entry; remaining ties -> first (stable table order).
skills/ai-writing-suite/evals/smoke_test.py:90:
skills/ai-writing-suite/evals/smoke_test.py:91:    WHY two-tier: the protocol text in INDEX.md says "scan Keywords, THEN the
skills/ai-writing-suite/evals/smoke_test.py:92:    Summary for intent overlap." A flat union of both lets a near-neighbor win
skills/ai-writing-suite/evals/smoke_test.py:93:    on shared keywords; tiering on intent is what makes the disambiguation case
skills/ai-writing-suite/evals/smoke_test.py:94:    (audience vs tone) resolve correctly without editing the KB."""
skills/ai-writing-suite/evals/smoke_test.py:95:    q = set(tokens(query))
skills/ai-writing-suite/evals/smoke_test.py:96:    # Sort key: (total term overlap, summary-intent overlap). Higher = better.
skills/ai-writing-suite/evals/smoke_test.py:97:    #   - primary: overlap across BOTH columns (the protocol's "term overlap")
skills/ai-writing-suite/evals/smoke_test.py:98:    #   - secondary: summary-only overlap, used to break ties on intent
skills/ai-writing-suite/evals/smoke_test.py:99:    # First entry wins a full tie (> not >=, table order preserved).
skills/ai-writing-suite/evals/smoke_test.py:100:    best, best_score = None, (-1, -1)
skills/ai-writing-suite/evals/smoke_test.py:101:    for e in entries:
skills/ai-writing-suite/evals/smoke_test.py:102:        all_terms = e["keywords"] | e["summary_kw"]
skills/ai-writing-suite/evals/smoke_test.py:103:        score = (len(q & all_terms), len(q & e["summary_kw"]))
skills/ai-writing-suite/evals/smoke_test.py:104:        if score > best_score:
skills/ai-writing-suite/evals/smoke_test.py:105:            best, best_score = e, score
skills/ai-writing-suite/evals/smoke_test.py:106:    # Overlap guard (review m2): a query with ZERO term overlap must NOT resolve
skills/ai-writing-suite/evals/smoke_test.py:107:    # to the first table row by stable-order fallback — that would let an empty
skills/ai-writing-suite/evals/smoke_test.py:108:    # or garbage query vacuously satisfy a case. Zero overlap = no match.
skills/ai-writing-suite/evals/smoke_test.py:109:    if best_score[0] == 0:
skills/ai-writing-suite/evals/smoke_test.py:110:        return None, best_score
skills/ai-writing-suite/evals/smoke_test.py:111:    return (best["file"] if best else None), best_score
skills/ai-writing-suite/evals/smoke_test.py:112:
skills/ai-writing-suite/evals/smoke_test.py:113:
skills/ai-writing-suite/evals/smoke_test.py:114:# ── Parse SMOKE-TEST.md TEST CASE blocks ──────────────────────────────────
skills/ai-writing-suite/evals/smoke_test.py:115:def load_cases():
skills/ai-writing-suite/evals/smoke_test.py:116:    """Extract (query, expected_entry, expected_passage) from the smoke doc.
skills/ai-writing-suite/evals/smoke_test.py:117:
skills/ai-writing-suite/evals/smoke_test.py:118:    The doc has two case shapes: the labelled 'TEST CASE' block and the
skills/ai-writing-suite/evals/smoke_test.py:119:    'second case' block. Both carry a Query blockquote, an 'Expected entry'
skills/ai-writing-suite/evals/smoke_test.py:120:    line, and an 'Expected passage' blockquote. We parse on those anchors
skills/ai-writing-suite/evals/smoke_test.py:121:    rather than on heading text so a reworded heading doesn't silently drop
skills/ai-writing-suite/evals/smoke_test.py:122:    a case.
skills/ai-writing-suite/evals/smoke_test.py:123:    """
skills/ai-writing-suite/evals/smoke_test.py:124:    with open(SMOKE_PATH, encoding="utf-8") as fh:
skills/ai-writing-suite/evals/smoke_test.py:125:        text = fh.read()
skills/ai-writing-suite/evals/smoke_test.py:126:
skills/ai-writing-suite/evals/smoke_test.py:127:    cases = []
skills/ai-writing-suite/evals/smoke_test.py:128:    # Find every "Expected entry" anchor; walk backward for the query and
skills/ai-writing-suite/evals/smoke_test.py:129:    # forward for the passage around each one.
skills/ai-writing-suite/evals/smoke_test.py:130:    for m in re.finditer(r"\*\*Expected entry(?:\s+retrieved)?:\*\*\s*`([^`]+)`", text):
skills/ai-writing-suite/evals/smoke_test.py:131:        entry = m.group(1).strip()
skills/ai-writing-suite/evals/smoke_test.py:132:        before = text[:m.start()]
skills/ai-writing-suite/evals/smoke_test.py:133:        after = text[m.start():]
skills/ai-writing-suite/evals/smoke_test.py:134:
skills/ai-writing-suite/evals/smoke_test.py:135:        # Query = the last "Query" blockquote before this anchor.
skills/ai-writing-suite/evals/smoke_test.py:136:        q_matches = list(re.finditer(
skills/ai-writing-suite/evals/smoke_test.py:137:            r"\*\*Query[^*]*:\*\*\s*\n>\s*\"?(.+?)\"?\s*\n", before, re.S))
skills/ai-writing-suite/evals/smoke_test.py:138:        query = q_matches[-1].group(1).strip() if q_matches else None
skills/ai-writing-suite/evals/smoke_test.py:139:
skills/ai-writing-suite/evals/smoke_test.py:140:        # Passage = the first "Expected passage" blockquote after this anchor.
skills/ai-writing-suite/evals/smoke_test.py:141:        p_match = re.search(
skills/ai-writing-suite/evals/smoke_test.py:142:            r"\*\*Expected passage[^*]*:\*\*\s*\n((?:>\s?.*\n?)+)", after)
skills/ai-writing-suite/evals/smoke_test.py:143:        passage = None
skills/ai-writing-suite/evals/smoke_test.py:144:        if p_match:
skills/ai-writing-suite/evals/smoke_test.py:145:            # Strip leading "> " from each quoted line, join, collapse spaces.
skills/ai-writing-suite/evals/smoke_test.py:146:            raw = p_match.group(1)
skills/ai-writing-suite/evals/smoke_test.py:147:            passage = " ".join(
skills/ai-writing-suite/evals/smoke_test.py:148:                re.sub(r"^>\s?", "", ln).strip()
skills/ai-writing-suite/evals/smoke_test.py:149:                for ln in raw.splitlines() if ln.strip())
skills/ai-writing-suite/evals/smoke_test.py:150:            passage = re.sub(r"\s+", " ", passage).strip()
skills/ai-writing-suite/evals/smoke_test.py:151:
skills/ai-writing-suite/evals/smoke_test.py:152:        if query and entry and passage:
skills/ai-writing-suite/evals/smoke_test.py:153:            cases.append({"query": query, "entry": entry, "passage": passage})
skills/ai-writing-suite/evals/smoke_test.py:154:    return cases
skills/ai-writing-suite/evals/smoke_test.py:155:
skills/ai-writing-suite/evals/smoke_test.py:156:
skills/ai-writing-suite/evals/smoke_test.py:157:def normalize(s):
skills/ai-writing-suite/evals/smoke_test.py:158:    """Collapse whitespace + drop markdown bold so passage containment is
skills/ai-writing-suite/evals/smoke_test.py:159:    robust to formatting differences between SMOKE-TEST and the entry file."""
skills/ai-writing-suite/evals/smoke_test.py:160:    s = s.replace("**", "")
skills/ai-writing-suite/evals/smoke_test.py:161:    return re.sub(r"\s+", " ", s).strip().lower()
skills/ai-writing-suite/evals/smoke_test.py:162:
skills/ai-writing-suite/evals/smoke_test.py:163:
skills/ai-writing-suite/evals/smoke_test.py:164:def run():
skills/ai-writing-suite/evals/smoke_test.py:165:    entries = load_index()
skills/ai-writing-suite/evals/smoke_test.py:166:    cases = load_cases()
skills/ai-writing-suite/evals/smoke_test.py:167:    if not cases:
skills/ai-writing-suite/evals/smoke_test.py:168:        print("FAIL: no TEST CASE blocks parsed from SMOKE-TEST.md", file=sys.stderr)
skills/ai-writing-suite/evals/smoke_test.py:169:        return 1
skills/ai-writing-suite/evals/smoke_test.py:170:    if not entries:
skills/ai-writing-suite/evals/smoke_test.py:171:        print("FAIL: no entries parsed from INDEX.md", file=sys.stderr)
skills/ai-writing-suite/evals/smoke_test.py:172:        return 1
skills/ai-writing-suite/evals/smoke_test.py:173:
skills/ai-writing-suite/evals/smoke_test.py:174:    failures = 0
skills/ai-writing-suite/evals/smoke_test.py:175:    print(f"KB smoke test — {len(cases)} case(s), {len(entries)} index entries\n")
skills/ai-writing-suite/evals/smoke_test.py:176:    for i, c in enumerate(cases, 1):
skills/ai-writing-suite/evals/smoke_test.py:177:        got, overlap = retrieve(c["query"], entries)
skills/ai-writing-suite/evals/smoke_test.py:178:        entry_ok = (got == c["entry"])
skills/ai-writing-suite/evals/smoke_test.py:179:
skills/ai-writing-suite/evals/smoke_test.py:180:        # Passage check: the expected passage must appear in the retrieved file.
skills/ai-writing-suite/evals/smoke_test.py:181:        passage_ok = False
skills/ai-writing-suite/evals/smoke_test.py:182:        entry_path = os.path.join(KB, got) if got else None
skills/ai-writing-suite/evals/smoke_test.py:183:        if entry_path and os.path.exists(entry_path):
skills/ai-writing-suite/evals/smoke_test.py:184:            with open(entry_path, encoding="utf-8") as fh:
skills/ai-writing-suite/evals/smoke_test.py:185:                body = normalize(fh.read())
skills/ai-writing-suite/evals/smoke_test.py:186:            # Match on the first sentence of the expected passage so trailing
skills/ai-writing-suite/evals/smoke_test.py:187:            # editorial parentheticals in the smoke doc don't break the assert.
skills/ai-writing-suite/evals/smoke_test.py:188:            needle = normalize(c["passage"].split(".")[0])
skills/ai-writing-suite/evals/smoke_test.py:189:            passage_ok = needle in body
skills/ai-writing-suite/evals/smoke_test.py:190:
skills/ai-writing-suite/evals/smoke_test.py:191:        ok = entry_ok and passage_ok
skills/ai-writing-suite/evals/smoke_test.py:192:        if not ok:
skills/ai-writing-suite/evals/smoke_test.py:193:            failures += 1
skills/ai-writing-suite/evals/smoke_test.py:194:        mark = "PASS" if ok else "FAIL"
skills/ai-writing-suite/evals/smoke_test.py:195:        print(f"[{mark}] Case {i}: query -> {got} "
skills/ai-writing-suite/evals/smoke_test.py:196:              f"(expected {c['entry']}, overlap={overlap})")
skills/ai-writing-suite/evals/smoke_test.py:197:        if not entry_ok:
skills/ai-writing-suite/evals/smoke_test.py:198:            print(f"       entry mismatch: got {got}, expected {c['entry']}")
skills/ai-writing-suite/evals/smoke_test.py:199:        if entry_ok and not passage_ok:
skills/ai-writing-suite/evals/smoke_test.py:200:            print(f"       passage not found in {got}: "
skills/ai-writing-suite/evals/smoke_test.py:201:                  f"\"{c['passage'][:60]}...\"")
skills/ai-writing-suite/evals/smoke_test.py:202:
skills/ai-writing-suite/evals/smoke_test.py:203:    print()
skills/ai-writing-suite/evals/smoke_test.py:204:    if failures:
skills/ai-writing-suite/evals/smoke_test.py:205:        print(f"{failures}/{len(cases)} case(s) FAILED")
skills/ai-writing-suite/evals/smoke_test.py:206:        return 1
skills/ai-writing-suite/evals/smoke_test.py:207:    print(f"All {len(cases)} case(s) passed.")
skills/ai-writing-suite/evals/smoke_test.py:208:    return 0
skills/ai-writing-suite/evals/smoke_test.py:209:
skills/ai-writing-suite/evals/smoke_test.py:210:
skills/ai-writing-suite/evals/smoke_test.py:211:if __name__ == "__main__":
skills/ai-writing-suite/evals/smoke_test.py:212:    sys.exit(run())
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:1:# Significance & Attribution Tells
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:2:
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:3:The model inflates importance and fakes sourcing. These are credibility killers:
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:4:they make confident claims the text can't back up, so they are the highest
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:5:priority to fix in any professional or factual document.
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:6:
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:7:---
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:8:
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:9:### S1 — Significance inflation
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:10:
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:11:- **Tell:** Puffing routine facts into history-making ones: "marking a pivotal
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:12:  moment in the evolution of…," "a watershed moment for the industry," "stands as
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:13:  a testament to," "underscores the importance of," "represents a shift."
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:14:- **Fix:** State what happened and let the reader judge significance. If the
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:15:  sentence still works after deleting the inflation clause, delete it.
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:16:- **Before:** established in 1989, marking a pivotal moment in the evolution of
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:17:  regional statistics.
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:18:- **After:** established in 1989 to collect regional statistics.
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:19:- **Sources:** blader (P1), aboudjem (§1), avoid-ai, anti-vibe.
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:20:
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:21:---
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:22:
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:23:### S2 — Symbolic gloss / meaning-telling
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:24:
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:25:- **Tell:** Narrating the *meaning* of a mundane fact instead of trusting the
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:26:  fact: "this represents a broader shift," "the decision symbolizes a commitment
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:27:  to excellence," "speaks to a larger trend." Distinct from S1's "pivotal /
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:28:  testament" framing — this is the interpretive layer telling readers what to
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:29:  feel.
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:30:- **Fix:** Cut the meaning sentence. State the fact; if the significance is real,
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:31:  show it with a concrete consequence.
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:32:- **Before:** The closed factory represents the decline of American manufacturing
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:33:  and speaks to broader anxieties about post-industrial identity.
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:34:- **After:** The factory closed in 2009. Three hundred jobs. The town's high
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:35:  school dropped football the next year.
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:36:- **Sources:** blader (P40), avoid-ai (folded into superficial -ing), aboudjem.
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:37:
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:38:---
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:39:
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:40:### S3 — Novelty inflation
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:41:
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:42:- **Tell:** Treating an established concept as if the subject invented it: "he
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:43:  coined the term," "a failure mode nobody talks about," "the insight everyone's
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:44:  missing." Factually risky (the idea often already has a Wikipedia page) and
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:45:  reads as promotional.
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:46:- **Fix:** Describe what the person *did with* the concept, not that they
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:47:  discovered it. When unsure whether something is novel, assume it isn't.
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:48:- **Sources:** avoid-ai (novelty inflation).
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:49:
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:50:---
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:51:
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:52:### S4 — Vague attribution / weasel words
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:53:
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:54:- **Tell:** Phantom authorities give opinions weight: "Experts believe,"
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:55:  "Studies show," "Research suggests," "Industry leaders agree," "several
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:56:  sources" — with no named source.
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:57:- **Fix:** Name the specific expert, paper, or report, or drop the claim. One
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:58:  sourced reference beats four vague ones.
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:59:- **Before:** Experts believe it plays a crucial role in the regional ecosystem.
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:60:- **After:** A 2019 Chinese Academy of Sciences survey found 12 endemic fish
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:61:  species.
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:62:- **Sources:** blader (P5), aboudjem (§5), avoid-ai, anti-vibe.
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:63:
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:64:---
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:65:
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:66:### S5 — Notability name-dropping / source-listing as content
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:67:
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:68:- **Tell:** Proving importance by listing coverage instead of saying what the
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:69:  coverage reported: "cited in NYT, BBC, FT, and The Hindu," "maintains an active
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:70:  social media presence."
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:71:- **Fix:** Pick one source and say what it reported. Or cut the list.
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:72:- **Before:** Her insights have been featured in Wired, Refinery29, and other
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:73:  prominent outlets.
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:74:- **After:** Wired profiled her 2024 research on algorithmic bias in hiring
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:75:  software.
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:76:- **Sources:** blader (P2 + P37), aboudjem (§2), avoid-ai.
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:77:
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:78:---
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:79:
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:80:### S6 — Promotional / advertisement language
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:81:
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:82:- **Tell:** Tourism-brochure prose: "nestled within the breathtaking foothills,"
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:83:  "a vibrant hub of innovation," "a thriving ecosystem," "rich cultural
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:84:  heritage," "must-visit," "world-class."
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:85:- **Fix:** Plain description. "is a town in the Gonder region," "has 12
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:86:  startups." If you wouldn't say it in conversation, cut it.
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:87:- **Sources:** blader (P4), aboudjem (§4), avoid-ai, anti-vibe (consultant tone).
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:88:
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:89:---
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:90:
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:91:### S7 — Superficial -ing analyses
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:92:
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:93:- **Tell:** Present-participle phrases tacked on to fake depth: "…symbolizing the
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:94:  region's commitment to progress, reflecting decades of investment, and
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:95:  showcasing a new era." The written equivalent of nodding while saying nothing.
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:96:- **Fix:** Delete the -ing clause. If it carried real information, promote it to
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:97:  its own sentence with a specific source.
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:98:- **Sources:** blader (P3), aboudjem (§3), avoid-ai.
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:99:
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:100:---
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:101:
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:102:### S8 — Speculative gap-filling
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:103:
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:104:- **Tell:** When the model lacks a fact, it fills the gap with hedged
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:105:  speculation dressed as background: "maintains a relatively low public profile,"
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:106:  "is believed to have," "likely began his career in," "appears to have
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:107:  studied." Worse than an honest cutoff disclaimer because the reader can't tell
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:108:  what's known from what's invented.
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:109:- **Fix:** Cut the speculation or replace it with a sourced fact. Say what isn't
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:110:  known rather than guessing.
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:111:- **Sources:** aboudjem (§21 second half), avoid-ai (adapted from blader P21).
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:112:
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:113:---
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:114:
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:115:### S9 — Consultant-speak / business jargon
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:116:
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:117:- **Tell:** Polished-but-evasive language that signals work without carrying it:
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:118:  best-in-class, value-add, key learnings, actionable insights, holistic
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:119:  approach, strategic lever, future-proof, synergy. (Chinese equivalents: 赋能 /
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:120:  打通 / 闭环 / 抓手 / 链路.)
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:121:- **Fix:** If the draft makes a claim, say the claim plainly. Replace the
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:122:  abstraction with what actually happened, exists, or should be done.
skills/ai-writing-suite/_shared/patterns/significance-attribution.md:123:- **Sources:** anti-vibe (consultant tone + Chinese buzzwords), avoid-ai.
skills/ai-writing-suite/evals/detector/__init__.py:1:"""Mechanical AI-tell detector — Python port of the avoid-ai JS engine.
skills/ai-writing-suite/evals/detector/__init__.py:2:
skills/ai-writing-suite/evals/detector/__init__.py:3:WHY this exists (design D10b): the LLM-judge fixtures catch *quality*
skills/ai-writing-suite/evals/detector/__init__.py:4:regressions, but they need a model and cost money. A deterministic, stdlib-only
skills/ai-writing-suite/evals/detector/__init__.py:5:detector is the cheap regression gate: it runs in CI on every change, keys off
skills/ai-writing-suite/evals/detector/__init__.py:6:the same AI-tell categories the `comms-polish` skill reads from
skills/ai-writing-suite/evals/detector/__init__.py:7:`_shared/patterns/`, and never needs an API key.
skills/ai-writing-suite/evals/detector/__init__.py:8:
skills/ai-writing-suite/evals/detector/__init__.py:9:This package is a faithful-but-pragmatic port of the regex-detectable subset of
skills/ai-writing-suite/evals/detector/__init__.py:10:`avoid-ai-writing/detector/patterns.js`. Stylometric signals that need no model
skills/ai-writing-suite/evals/detector/__init__.py:11:(uniformity, em-dash rate, hashtag stuffing, bullet-NP lists) are included
skills/ai-writing-suite/evals/detector/__init__.py:12:because they are pure math; the trinary GPTZero-shaped classifier is included
skills/ai-writing-suite/evals/detector/__init__.py:13:because the fixtures lean on its score bands.
skills/ai-writing-suite/evals/detector/__init__.py:14:"""
skills/ai-writing-suite/evals/detector/__init__.py:15:
skills/ai-writing-suite/evals/detector/__init__.py:16:from .detector import analyze, get_label  # noqa: F401
skills/ai-writing-suite/skills/comms-polish/references/final-pass-checklist.md:1:# Final-Pass Checklist
skills/ai-writing-suite/skills/comms-polish/references/final-pass-checklist.md:2:
skills/ai-writing-suite/skills/comms-polish/references/final-pass-checklist.md:3:Run this before returning any rewritten or edited copy. It's the last gate — the
skills/ai-writing-suite/skills/comms-polish/references/final-pass-checklist.md:4:quick read-through that catches the tell you reintroduced while fixing another one.
skills/ai-writing-suite/skills/comms-polish/references/final-pass-checklist.md:5:
skills/ai-writing-suite/skills/comms-polish/references/final-pass-checklist.md:6:Adapted from `weijt606/anti-vibe-writing` (`final-pass-checklist.md`, MIT); the
skills/ai-writing-suite/skills/comms-polish/references/final-pass-checklist.md:7:optional scoring pass is adapted from the `stop-slop` rubric (MIT).
skills/ai-writing-suite/skills/comms-polish/references/final-pass-checklist.md:8:
skills/ai-writing-suite/skills/comms-polish/references/final-pass-checklist.md:9:## The checklist
skills/ai-writing-suite/skills/comms-polish/references/final-pass-checklist.md:10:
skills/ai-writing-suite/skills/comms-polish/references/final-pass-checklist.md:11:- The opening reaches the point quickly — no runway.
skills/ai-writing-suite/skills/comms-polish/references/final-pass-checklist.md:12:- The main point appears early.
skills/ai-writing-suite/skills/comms-polish/references/final-pass-checklist.md:13:- The wording is concrete enough that a reader can picture the thing described.
skills/ai-writing-suite/skills/comms-polish/references/final-pass-checklist.md:14:- No template phrases or startup jargon ("leverage", "seamless", "robust",
skills/ai-writing-suite/skills/comms-polish/references/final-pass-checklist.md:15:  "circle back").
skills/ai-writing-suite/skills/comms-polish/references/final-pass-checklist.md:16:- Headings and bullets remain only where they help the reader.
skills/ai-writing-suite/skills/comms-polish/references/final-pass-checklist.md:17:- Emoji, icons, and decorative markdown are gone — unless the genre preset allows
skills/ai-writing-suite/skills/comms-polish/references/final-pass-checklist.md:18:  them and the author's voice uses them.
skills/ai-writing-suite/skills/comms-polish/references/final-pass-checklist.md:19:- Stock sections (Overview, Key Features, Conclusion) are gone unless they earn
skills/ai-writing-suite/skills/comms-polish/references/final-pass-checklist.md:20:  their keep.
skills/ai-writing-suite/skills/comms-polish/references/final-pass-checklist.md:21:- Repetition is gone.
skills/ai-writing-suite/skills/comms-polish/references/final-pass-checklist.md:22:- The tone has a point of view instead of manufactured balance.
skills/ai-writing-suite/skills/comms-polish/references/final-pass-checklist.md:23:- Warmth comes from specificity and cadence, not filler friendliness.
skills/ai-writing-suite/skills/comms-polish/references/final-pass-checklist.md:24:- The prose sounds written, not assembled.
skills/ai-writing-suite/skills/comms-polish/references/final-pass-checklist.md:25:- **Facts, numbers, technical claims, code, commands, and quotes are unchanged.**
skills/ai-writing-suite/skills/comms-polish/references/final-pass-checklist.md:26:- Necessary nuance is carried in the sentence, not bolted on as a hedge.
skills/ai-writing-suite/skills/comms-polish/references/final-pass-checklist.md:27:- The result is shorter or sharper, not just different.
skills/ai-writing-suite/skills/comms-polish/references/final-pass-checklist.md:28:
skills/ai-writing-suite/skills/comms-polish/references/final-pass-checklist.md:29:## Genre + voice cross-checks
skills/ai-writing-suite/skills/comms-polish/references/final-pass-checklist.md:30:
skills/ai-writing-suite/skills/comms-polish/references/final-pass-checklist.md:31:Two checks that depend on the layer above this skill:
skills/ai-writing-suite/skills/comms-polish/references/final-pass-checklist.md:32:
skills/ai-writing-suite/skills/comms-polish/references/final-pass-checklist.md:33:- **Genre fit:** re-read against the matching `scenario-presets.md` preset. Did the
skills/ai-writing-suite/skills/comms-polish/references/final-pass-checklist.md:34:  rewrite respect that genre's *leave alone* list? (Don't strip a README's real
skills/ai-writing-suite/skills/comms-polish/references/final-pass-checklist.md:35:  lists; don't add a heading to a tweet.)
skills/ai-writing-suite/skills/comms-polish/references/final-pass-checklist.md:36:- **Voice fit:** if `_shared/voice-profile.md` was loaded, does the rewrite still
skills/ai-writing-suite/skills/comms-polish/references/final-pass-checklist.md:37:  sound like that author — sentence rhythm, punctuation habits, preferred terms?
skills/ai-writing-suite/skills/comms-polish/references/final-pass-checklist.md:38:  If no profile existed, did you keep the original's own voice rather than
skills/ai-writing-suite/skills/comms-polish/references/final-pass-checklist.md:39:  flattening it to generic-clean?
skills/ai-writing-suite/skills/comms-polish/references/final-pass-checklist.md:40:
skills/ai-writing-suite/skills/comms-polish/references/final-pass-checklist.md:41:## Optional scoring pass
skills/ai-writing-suite/skills/comms-polish/references/final-pass-checklist.md:42:
skills/ai-writing-suite/skills/comms-polish/references/final-pass-checklist.md:43:For a borderline draft, score five dimensions (1–10 each) before returning.
skills/ai-writing-suite/skills/comms-polish/references/final-pass-checklist.md:44:Adapted from the `stop-slop` rubric.
skills/ai-writing-suite/skills/comms-polish/references/final-pass-checklist.md:45:
skills/ai-writing-suite/skills/comms-polish/references/final-pass-checklist.md:46:- **Directness** — states things; doesn't announce it's about to state them.
skills/ai-writing-suite/skills/comms-polish/references/final-pass-checklist.md:47:- **Rhythm** — sentence lengths vary; no monotone march of equal clauses.
skills/ai-writing-suite/skills/comms-polish/references/final-pass-checklist.md:48:- **Trust** — respects the reader's intelligence; no over-explaining the obvious.
skills/ai-writing-suite/skills/comms-polish/references/final-pass-checklist.md:49:- **Authenticity** — reads like a person chose the words, not a system.
skills/ai-writing-suite/skills/comms-polish/references/final-pass-checklist.md:50:- **Density** — every sentence earns its place; no filler.
skills/ai-writing-suite/skills/comms-polish/references/final-pass-checklist.md:51:
skills/ai-writing-suite/skills/comms-polish/references/final-pass-checklist.md:52:Below 35 / 50 means it still reads generated — make another pass.
skills/ai-writing-suite/skills/comms-polish/references/final-pass-checklist.md:53:
skills/ai-writing-suite/skills/comms-polish/references/final-pass-checklist.md:54:> This is a *qualitative* gate, separate from the 0–100 AI-tell score in
skills/ai-writing-suite/skills/comms-polish/references/final-pass-checklist.md:55:> `SKILL.md`. The 0–100 score reports density to the user; this checklist is the
skills/ai-writing-suite/skills/comms-polish/references/final-pass-checklist.md:56:> editor's own pre-ship sweep.
skills/ai-writing-suite/evals/detector/detector.py:1:"""analyze() — scan text for AI tells, score it, classify it.
skills/ai-writing-suite/evals/detector/detector.py:2:
skills/ai-writing-suite/evals/detector/detector.py:3:Port of `avoid-ai-writing/detector/patterns.js > analyzeText`. Same scoring
skills/ai-writing-suite/evals/detector/detector.py:4:model: collect raw issues -> dedup by (type, text) -> sum category weights ->
skills/ai-writing-suite/evals/detector/detector.py:5:normalize by log2(words/50) so longer texts don't accumulate unboundedly.
skills/ai-writing-suite/evals/detector/detector.py:6:
skills/ai-writing-suite/evals/detector/detector.py:7:Return shape (dict):
skills/ai-writing-suite/evals/detector/detector.py:8:  score        : int 0-100
skills/ai-writing-suite/evals/detector/detector.py:9:  label        : human-readable band ("Clean" .. "Heavy AI patterns")
skills/ai-writing-suite/evals/detector/detector.py:10:  issues       : list of {type, text, severity, suggestion}
skills/ai-writing-suite/evals/detector/detector.py:11:  stats        : {wordCount, contextMode, tier counts, ...}
skills/ai-writing-suite/evals/detector/detector.py:12:  classification: HUMAN_ONLY | MIXED | AI_ONLY  (GPTZero-shaped, FN-biased)
skills/ai-writing-suite/evals/detector/detector.py:13:  confidence   : low | medium | high
skills/ai-writing-suite/evals/detector/detector.py:14:
skills/ai-writing-suite/evals/detector/detector.py:15:WHY FN-biased: a false "this is AI" on real human writing destroys trust worse
skills/ai-writing-suite/evals/detector/detector.py:16:than a missed AI passage. Ambiguity routes to MIXED, never AI_ONLY.
skills/ai-writing-suite/evals/detector/detector.py:17:
skills/ai-writing-suite/evals/detector/detector.py:18:LIMITATION (review m4): word counting assumes whitespace-delimited scripts
skills/ai-writing-suite/evals/detector/detector.py:19:(`\S+`). CJK / non-space-delimited text (Chinese, Japanese) collapses to a tiny
skills/ai-writing-suite/evals/detector/detector.py:20:word count and returns UNSCORED ("Too short") rather than a real score. That is
skills/ai-writing-suite/evals/detector/detector.py:21:NOT a clean-text signal — it means "unsupported script." Bilingual/CJK scoring
skills/ai-writing-suite/evals/detector/detector.py:22:is v2 (see voice-onboard + scenario-presets, which scope bilingual to v2).
skills/ai-writing-suite/evals/detector/detector.py:23:"""
skills/ai-writing-suite/evals/detector/detector.py:24:
skills/ai-writing-suite/evals/detector/detector.py:25:import math
skills/ai-writing-suite/evals/detector/detector.py:26:import re
skills/ai-writing-suite/evals/detector/detector.py:27:
skills/ai-writing-suite/evals/detector/detector.py:28:from . import patterns as P
skills/ai-writing-suite/evals/detector/detector.py:29:
skills/ai-writing-suite/evals/detector/detector.py:30:MAX_WORDS = 10000  # bail above this rather than regex-scanning a pasted novel
skills/ai-writing-suite/evals/detector/detector.py:31:
skills/ai-writing-suite/evals/detector/detector.py:32:_WORD_RE = re.compile(r"\S+")
skills/ai-writing-suite/evals/detector/detector.py:33:_TOKEN_RE = re.compile(r"[\w'-]+")
skills/ai-writing-suite/evals/detector/detector.py:34:
skills/ai-writing-suite/evals/detector/detector.py:35:
skills/ai-writing-suite/evals/detector/detector.py:36:def _tokenize(text):
skills/ai-writing-suite/evals/detector/detector.py:37:    return _TOKEN_RE.findall(text.lower())
skills/ai-writing-suite/evals/detector/detector.py:38:
skills/ai-writing-suite/evals/detector/detector.py:39:
skills/ai-writing-suite/evals/detector/detector.py:40:def _count_words(text):
skills/ai-writing-suite/evals/detector/detector.py:41:    return len(_WORD_RE.findall(text))
skills/ai-writing-suite/evals/detector/detector.py:42:
skills/ai-writing-suite/evals/detector/detector.py:43:
skills/ai-writing-suite/evals/detector/detector.py:44:def _paragraphs(text):
skills/ai-writing-suite/evals/detector/detector.py:45:    return [p for p in re.split(r"\n\s*\n", text) if p.strip()]
skills/ai-writing-suite/evals/detector/detector.py:46:
skills/ai-writing-suite/evals/detector/detector.py:47:
skills/ai-writing-suite/evals/detector/detector.py:48:def _sentences(text):
skills/ai-writing-suite/evals/detector/detector.py:49:    return [s for s in re.split(r"[.!?]+", text) if len(s.strip()) > 5]
skills/ai-writing-suite/evals/detector/detector.py:50:
skills/ai-writing-suite/evals/detector/detector.py:51:
skills/ai-writing-suite/evals/detector/detector.py:52:def _match(text, regexes, category, severity):
skills/ai-writing-suite/evals/detector/detector.py:53:    """Run a list of compiled regexes, return one issue per match."""
skills/ai-writing-suite/evals/detector/detector.py:54:    out = []
skills/ai-writing-suite/evals/detector/detector.py:55:    for rx in regexes:
skills/ai-writing-suite/evals/detector/detector.py:56:        for m in rx.finditer(text):
skills/ai-writing-suite/evals/detector/detector.py:57:            out.append({"type": category, "text": m.group(0),
skills/ai-writing-suite/evals/detector/detector.py:58:                        "severity": severity, "suggestion": None})
skills/ai-writing-suite/evals/detector/detector.py:59:    return out
skills/ai-writing-suite/evals/detector/detector.py:60:
skills/ai-writing-suite/evals/detector/detector.py:61:
skills/ai-writing-suite/evals/detector/detector.py:62:def get_label(score):
skills/ai-writing-suite/evals/detector/detector.py:63:    if score == 0:
skills/ai-writing-suite/evals/detector/detector.py:64:        return "Clean"
skills/ai-writing-suite/evals/detector/detector.py:65:    if score <= 15:
skills/ai-writing-suite/evals/detector/detector.py:66:        return "Minimal AI signals"
skills/ai-writing-suite/evals/detector/detector.py:67:    if score <= 35:
skills/ai-writing-suite/evals/detector/detector.py:68:        return "Some AI patterns"
skills/ai-writing-suite/evals/detector/detector.py:69:    if score <= 60:
skills/ai-writing-suite/evals/detector/detector.py:70:        return "Moderate AI signals"
skills/ai-writing-suite/evals/detector/detector.py:71:    if score <= 80:
skills/ai-writing-suite/evals/detector/detector.py:72:        return "Strong AI signals"
skills/ai-writing-suite/evals/detector/detector.py:73:    return "Heavy AI patterns"
skills/ai-writing-suite/evals/detector/detector.py:74:
skills/ai-writing-suite/evals/detector/detector.py:75:
skills/ai-writing-suite/evals/detector/detector.py:76:def _dedup(issues):
skills/ai-writing-suite/evals/detector/detector.py:77:    """Dedup by (type, lowercased text) so repeated hits count once.
skills/ai-writing-suite/evals/detector/detector.py:78:
skills/ai-writing-suite/evals/detector/detector.py:79:    Mirrors the JS: the score reflects the *distinct* signals a user sees, not
skills/ai-writing-suite/evals/detector/detector.py:80:    raw match count — otherwise one repeated phrase inflates the number.
skills/ai-writing-suite/evals/detector/detector.py:81:    """
skills/ai-writing-suite/evals/detector/detector.py:82:    seen = set()
skills/ai-writing-suite/evals/detector/detector.py:83:    out = []
skills/ai-writing-suite/evals/detector/detector.py:84:    for it in issues:
skills/ai-writing-suite/evals/detector/detector.py:85:        key = (it["type"], (it["text"] or "").lower())
skills/ai-writing-suite/evals/detector/detector.py:86:        if key in seen:
skills/ai-writing-suite/evals/detector/detector.py:87:            continue
skills/ai-writing-suite/evals/detector/detector.py:88:        seen.add(key)
skills/ai-writing-suite/evals/detector/detector.py:89:        out.append(it)
skills/ai-writing-suite/evals/detector/detector.py:90:    return out
skills/ai-writing-suite/evals/detector/detector.py:91:
skills/ai-writing-suite/evals/detector/detector.py:92:
skills/ai-writing-suite/evals/detector/detector.py:93:def analyze(text, context_mode="general"):
skills/ai-writing-suite/evals/detector/detector.py:94:    if not text or not text.strip():
skills/ai-writing-suite/evals/detector/detector.py:95:        return _unscored("Empty", 0)
skills/ai-writing-suite/evals/detector/detector.py:96:
skills/ai-writing-suite/evals/detector/detector.py:97:    word_count = _count_words(text)
skills/ai-writing-suite/evals/detector/detector.py:98:    if word_count < 10:
skills/ai-writing-suite/evals/detector/detector.py:99:        return _unscored("Too short", word_count)
skills/ai-writing-suite/evals/detector/detector.py:100:    if word_count > MAX_WORDS:
skills/ai-writing-suite/evals/detector/detector.py:101:        return _unscored("Text too long", word_count)
skills/ai-writing-suite/evals/detector/detector.py:102:
skills/ai-writing-suite/evals/detector/detector.py:103:    valid_modes = {"general", "technical", "marketing", "personal"}
skills/ai-writing-suite/evals/detector/detector.py:104:    if context_mode not in valid_modes:
skills/ai-writing-suite/evals/detector/detector.py:105:        context_mode = "general"
skills/ai-writing-suite/evals/detector/detector.py:106:
skills/ai-writing-suite/evals/detector/detector.py:107:    tokens = _tokenize(text)
skills/ai-writing-suite/evals/detector/detector.py:108:    paragraphs = _paragraphs(text)
skills/ai-writing-suite/evals/detector/detector.py:109:    sentences = _sentences(text)
skills/ai-writing-suite/evals/detector/detector.py:110:    issues = []
skills/ai-writing-suite/evals/detector/detector.py:111:
skills/ai-writing-suite/evals/detector/detector.py:112:    # 1. Tier 1 single words (one issue per distinct word).
skills/ai-writing-suite/evals/detector/detector.py:113:    tier1_found = set()
skills/ai-writing-suite/evals/detector/detector.py:114:    for tok in tokens:
skills/ai-writing-suite/evals/detector/detector.py:115:        if tok in P.TIER1 and tok not in tier1_found:
skills/ai-writing-suite/evals/detector/detector.py:116:            tier1_found.add(tok)
skills/ai-writing-suite/evals/detector/detector.py:117:            issues.append({"type": "tier1", "text": tok, "severity": "high",
skills/ai-writing-suite/evals/detector/detector.py:118:                           "suggestion": P.TIER1[tok]})
skills/ai-writing-suite/evals/detector/detector.py:119:    # Tier 1 multi-word phrases.
skills/ai-writing-suite/evals/detector/detector.py:120:    for rx, sugg in P.TIER1_PHRASES:
skills/ai-writing-suite/evals/detector/detector.py:121:        for m in rx.finditer(text):
skills/ai-writing-suite/evals/detector/detector.py:122:            low = m.group(0).lower()
skills/ai-writing-suite/evals/detector/detector.py:123:            if low in tier1_found:
skills/ai-writing-suite/evals/detector/detector.py:124:                continue
skills/ai-writing-suite/evals/detector/detector.py:125:            tier1_found.add(low)
skills/ai-writing-suite/evals/detector/detector.py:126:            issues.append({"type": "tier1", "text": m.group(0),
skills/ai-writing-suite/evals/detector/detector.py:127:                           "severity": "high", "suggestion": sugg})
skills/ai-writing-suite/evals/detector/detector.py:128:
skills/ai-writing-suite/evals/detector/detector.py:129:    # 2. Tier 2 clusters — only flag when 2+ distinct hits in one paragraph.
skills/ai-writing-suite/evals/detector/detector.py:130:    tier2_clusters = 0
skills/ai-writing-suite/evals/detector/detector.py:131:    for para in paragraphs:
skills/ai-writing-suite/evals/detector/detector.py:132:        found = []
skills/ai-writing-suite/evals/detector/detector.py:133:        for tok in _tokenize(para):
skills/ai-writing-suite/evals/detector/detector.py:134:            if tok in P.TIER2 and tok not in found:
skills/ai-writing-suite/evals/detector/detector.py:135:                found.append(tok)
skills/ai-writing-suite/evals/detector/detector.py:136:        if len(found) >= 2:
skills/ai-writing-suite/evals/detector/detector.py:137:            tier2_clusters += 1
skills/ai-writing-suite/evals/detector/detector.py:138:            for w in found:
skills/ai-writing-suite/evals/detector/detector.py:139:                issues.append({"type": "tier2", "text": w, "severity": "medium",
skills/ai-writing-suite/evals/detector/detector.py:140:                               "suggestion": P.TIER2[w]})
skills/ai-writing-suite/evals/detector/detector.py:141:
skills/ai-writing-suite/evals/detector/detector.py:142:    # 3. Tier 3 density — flag at 3% of words, floor of 3 occurrences.
skills/ai-writing-suite/evals/detector/detector.py:143:    tier3_counts = {}
skills/ai-writing-suite/evals/detector/detector.py:144:    for tok in tokens:
skills/ai-writing-suite/evals/detector/detector.py:145:        canon = P.TIER3_LOOKUP.get(tok)
skills/ai-writing-suite/evals/detector/detector.py:146:        if canon:
skills/ai-writing-suite/evals/detector/detector.py:147:            tier3_counts[canon] = tier3_counts.get(canon, 0) + 1
skills/ai-writing-suite/evals/detector/detector.py:148:    density_threshold = max(3, math.floor(word_count * 0.03))
skills/ai-writing-suite/evals/detector/detector.py:149:    for word, count in tier3_counts.items():
skills/ai-writing-suite/evals/detector/detector.py:150:        if count >= density_threshold:
skills/ai-writing-suite/evals/detector/detector.py:151:            issues.append({"type": "tier3", "text": f'"{word}" x{count}',
skills/ai-writing-suite/evals/detector/detector.py:152:                           "severity": "low",
skills/ai-writing-suite/evals/detector/detector.py:153:                           "suggestion": f"Overused ({count} times in {word_count} words)"})
skills/ai-writing-suite/evals/detector/detector.py:154:
skills/ai-writing-suite/evals/detector/detector.py:155:    # 4. Phrase-list categories.
skills/ai-writing-suite/evals/detector/detector.py:156:    issues += _match(text, P.TRANSITIONS, "transition", "medium")
skills/ai-writing-suite/evals/detector/detector.py:157:    issues += _match(text, P.CHATBOT_ARTIFACTS, "chatbot", "critical")
skills/ai-writing-suite/evals/detector/detector.py:158:    issues += _match(text, P.SYCOPHANTIC, "sycophantic", "critical")
skills/ai-writing-suite/evals/detector/detector.py:159:    issues += _match(text, P.FILLERS, "filler", "medium")
skills/ai-writing-suite/evals/detector/detector.py:160:    issues += _match(text, P.GENERIC_CONCLUSIONS, "generic-conclusion", "medium")
skills/ai-writing-suite/evals/detector/detector.py:161:    issues += _match(text, P.LETS_PATTERNS, "lets-construction", "medium")
skills/ai-writing-suite/evals/detector/detector.py:162:    issues += _match(text, P.REASONING_ARTIFACTS, "reasoning-artifact", "critical")
skills/ai-writing-suite/evals/detector/detector.py:163:    issues += _match(text, P.ACKNOWLEDGMENT_LOOPS, "acknowledgment-loop", "medium")
skills/ai-writing-suite/evals/detector/detector.py:164:    issues += _match(text, P.SIGNIFICANCE_INFLATION, "significance-inflation", "high")
skills/ai-writing-suite/evals/detector/detector.py:165:    issues += _match(text, P.VAGUE_ATTRIBUTIONS, "vague-attribution", "critical")
skills/ai-writing-suite/evals/detector/detector.py:166:    issues += _match(text, P.HOLLOW_INTENSIFIERS, "hollow-intensifier", "medium")
skills/ai-writing-suite/evals/detector/detector.py:167:    issues += _match(text, P.EMOTIONAL_FLATLINE, "emotional-flatline", "low")
skills/ai-writing-suite/evals/detector/detector.py:168:    issues += _match(text, P.NOVELTY_INFLATION, "novelty-inflation", "medium")
skills/ai-writing-suite/evals/detector/detector.py:169:    issues += _match(text, P.CUTOFF_DISCLAIMERS, "cutoff-disclaimer", "critical")
skills/ai-writing-suite/evals/detector/detector.py:170:    issues += _match(text, P.AI_PLACEHOLDERS, "ai-placeholder", "critical")
skills/ai-writing-suite/evals/detector/detector.py:171:    issues += _match(text, P.AI_CITATION_MARKUP, "ai-citation-markup", "critical")
skills/ai-writing-suite/evals/detector/detector.py:172:    issues += _match(text, P.AI_UTM_SOURCE, "ai-utm-source", "critical")
skills/ai-writing-suite/evals/detector/detector.py:173:    issues += _match(text, P.TEMPLATE_PHRASES, "template-phrase", "high")
skills/ai-writing-suite/evals/detector/detector.py:174:    issues += _match(text, P.FALSE_CONCESSION, "false-concession", "medium")
skills/ai-writing-suite/evals/detector/detector.py:175:    issues += _match(text, P.RHETORICAL_QUESTIONS, "rhetorical-question", "medium")
skills/ai-writing-suite/evals/detector/detector.py:176:    issues += _match(text, P.HEDGE_STACK, "hedge-stack", "high")
skills/ai-writing-suite/evals/detector/detector.py:177:    issues += _match(text, P.FUTURE_NARRATIVE, "future-narrative", "high")
skills/ai-writing-suite/evals/detector/detector.py:178:    issues += _match(text, P.REAL_ACTUAL_INFLATION, "real-actual-inflation", "medium")
skills/ai-writing-suite/evals/detector/detector.py:179:    issues += _match(text, P.FORMULAIC_OPENERS, "formulaic-opener", "high")
skills/ai-writing-suite/evals/detector/detector.py:180:
skills/ai-writing-suite/evals/detector/detector.py:181:    # Title-case headers — skip in technical mode (API docs use Title Case).
skills/ai-writing-suite/evals/detector/detector.py:182:    if context_mode != "technical":
skills/ai-writing-suite/evals/detector/detector.py:183:        for m in P.TITLE_CASE_HEADER.finditer(text):
skills/ai-writing-suite/evals/detector/detector.py:184:            txt = m.group(0)
skills/ai-writing-suite/evals/detector/detector.py:185:            toks = txt.split()
skills/ai-writing-suite/evals/detector/detector.py:186:            # Keep only the AI mid-sentence shape (has "And"/"Of"/etc.), drop
skills/ai-writing-suite/evals/detector/detector.py:187:            # plain headline-style proper-noun titles.
skills/ai-writing-suite/evals/detector/detector.py:188:            if len(toks) >= 4 and re.search(r"\b(?:And|Or|Of|The|In|For|To|A|An)\b", txt):
skills/ai-writing-suite/evals/detector/detector.py:189:                issues.append({"type": "title-case-header", "text": txt,
skills/ai-writing-suite/evals/detector/detector.py:190:                               "severity": "medium", "suggestion": None})
skills/ai-writing-suite/evals/detector/detector.py:191:
skills/ai-writing-suite/evals/detector/detector.py:192:    # Confidence calibration — only when it stacks (3+ raw hits).
skills/ai-writing-suite/evals/detector/detector.py:193:    conf = _match(text, P.CONFIDENCE_CALIBRATION, "confidence-calibration", "low")
skills/ai-writing-suite/evals/detector/detector.py:194:    if len(conf) >= 3:
skills/ai-writing-suite/evals/detector/detector.py:195:        issues += conf
skills/ai-writing-suite/evals/detector/detector.py:196:
skills/ai-writing-suite/evals/detector/detector.py:197:    # Tier 3 multi-word phrases: per-phrase repetition + cross-phrase cluster.
skills/ai-writing-suite/evals/detector/detector.py:198:    distinct_phrases_hit = 0
skills/ai-writing-suite/evals/detector/detector.py:199:    for rx in P.TIER3_PHRASES:
skills/ai-writing-suite/evals/detector/detector.py:200:        spans = rx.findall(text)
skills/ai-writing-suite/evals/detector/detector.py:201:        matches = list(rx.finditer(text))
skills/ai-writing-suite/evals/detector/detector.py:202:        if not matches:
skills/ai-writing-suite/evals/detector/detector.py:203:            continue
skills/ai-writing-suite/evals/detector/detector.py:204:        distinct_phrases_hit += 1
skills/ai-writing-suite/evals/detector/detector.py:205:        if len(matches) >= 2:
skills/ai-writing-suite/evals/detector/detector.py:206:            issues.append({"type": "tier3-phrase",
skills/ai-writing-suite/evals/detector/detector.py:207:                           "text": f'"{matches[0].group(0).lower()}" x{len(matches)}',
skills/ai-writing-suite/evals/detector/detector.py:208:                           "severity": "medium", "suggestion": None})
skills/ai-writing-suite/evals/detector/detector.py:209:    if distinct_phrases_hit >= 3:
skills/ai-writing-suite/evals/detector/detector.py:210:        issues.append({"type": "tier3-phrase-cluster",
skills/ai-writing-suite/evals/detector/detector.py:211:                       "text": f"{distinct_phrases_hit} distinct boilerplate phrases",
skills/ai-writing-suite/evals/detector/detector.py:212:                       "severity": "high", "suggestion": None})
skills/ai-writing-suite/evals/detector/detector.py:213:
skills/ai-writing-suite/evals/detector/detector.py:214:    # Hashtag stuffing — 6+ tags reads as bot output.
skills/ai-writing-suite/evals/detector/detector.py:215:    hashtags = re.findall(r"(?:^|\W)#\w[\w-]*", text)
skills/ai-writing-suite/evals/detector/detector.py:216:    if len(hashtags) >= 6:
skills/ai-writing-suite/evals/detector/detector.py:217:        issues.append({"type": "hashtag-stuff", "text": f"{len(hashtags)} hashtags",
skills/ai-writing-suite/evals/detector/detector.py:218:                       "severity": "medium", "suggestion": None})
skills/ai-writing-suite/evals/detector/detector.py:219:
skills/ai-writing-suite/evals/detector/detector.py:220:    # Bullet list of bare noun phrases (5+ short verbless items).
skills/ai-writing-suite/evals/detector/detector.py:221:    _detect_bullet_np(text, issues)
skills/ai-writing-suite/evals/detector/detector.py:222:
skills/ai-writing-suite/evals/detector/detector.py:223:    # Em-dash overuse — rate normalized per 1000 words.
skills/ai-writing-suite/evals/detector/detector.py:224:    em_dash_count = len(re.findall(r"—|(?<=\s)--(?=\s|$)", text))
skills/ai-writing-suite/evals/detector/detector.py:225:    if word_count and em_dash_count / (word_count / 1000.0) > 1:
skills/ai-writing-suite/evals/detector/detector.py:226:        issues.append({"type": "em-dash",
skills/ai-writing-suite/evals/detector/detector.py:227:                       "text": f"{em_dash_count} em dashes in {word_count} words",
skills/ai-writing-suite/evals/detector/detector.py:228:                       "severity": "medium", "suggestion": None})
skills/ai-writing-suite/evals/detector/detector.py:229:
skills/ai-writing-suite/evals/detector/detector.py:230:    # Sentence-length uniformity (burstiness — catalog rhythm-stylometric).
skills/ai-writing-suite/evals/detector/detector.py:231:    if len(sentences) >= 5:
skills/ai-writing-suite/evals/detector/detector.py:232:        lengths = [_count_words(s) for s in sentences]
skills/ai-writing-suite/evals/detector/detector.py:233:        avg = sum(lengths) / len(lengths)
skills/ai-writing-suite/evals/detector/detector.py:234:        var = sum((l - avg) ** 2 for l in lengths) / len(lengths)
skills/ai-writing-suite/evals/detector/detector.py:235:        cv = (math.sqrt(var) / avg) if avg > 0 else 0
skills/ai-writing-suite/evals/detector/detector.py:236:        if cv < 0.25 and avg > 10:
skills/ai-writing-suite/evals/detector/detector.py:237:            issues.append({"type": "uniformity",
skills/ai-writing-suite/evals/detector/detector.py:238:                           "text": f"Sentence lengths cluster around {round(avg)} words",
skills/ai-writing-suite/evals/detector/detector.py:239:                           "severity": "medium", "suggestion": None})
skills/ai-writing-suite/evals/detector/detector.py:240:
skills/ai-writing-suite/evals/detector/detector.py:241:    # Type-token ratio (low vocabulary diversity) — conservative, 200+ tokens.
skills/ai-writing-suite/evals/detector/detector.py:242:    if len(tokens) >= 200:
skills/ai-writing-suite/evals/detector/detector.py:243:        ttr = len(set(tokens)) / len(tokens)
skills/ai-writing-suite/evals/detector/detector.py:244:        if ttr < 0.4:
skills/ai-writing-suite/evals/detector/detector.py:245:            issues.append({"type": "low-ttr",
skills/ai-writing-suite/evals/detector/detector.py:246:                           "text": f"Vocabulary diversity {ttr*100:.1f}%",
skills/ai-writing-suite/evals/detector/detector.py:247:                           "severity": "low", "suggestion": None})
skills/ai-writing-suite/evals/detector/detector.py:248:
skills/ai-writing-suite/evals/detector/detector.py:249:    # Bold overuse.
skills/ai-writing-suite/evals/detector/detector.py:250:    bold = re.findall(r"\*\*[^*]+\*\*", text)
skills/ai-writing-suite/evals/detector/detector.py:251:    if len(bold) > 3:
skills/ai-writing-suite/evals/detector/detector.py:252:        issues.append({"type": "formatting", "text": f"{len(bold)} bold phrases",
skills/ai-writing-suite/evals/detector/detector.py:253:                       "severity": "medium", "suggestion": None})
skills/ai-writing-suite/evals/detector/detector.py:254:
skills/ai-writing-suite/evals/detector/detector.py:255:    # --- Score from the deduped list ---
skills/ai-writing-suite/evals/detector/detector.py:256:    deduped = _dedup(issues)
skills/ai-writing-suite/evals/detector/detector.py:257:    raw_score = sum(P.ISSUE_WEIGHTS.get(it["type"], 2) for it in deduped)
skills/ai-writing-suite/evals/detector/detector.py:258:    length_factor = max(1.0, math.log2(word_count / 50.0))
skills/ai-writing-suite/evals/detector/detector.py:259:    score = min(100, round(raw_score / length_factor))
skills/ai-writing-suite/evals/detector/detector.py:260:    label = get_label(score)
skills/ai-writing-suite/evals/detector/detector.py:261:
skills/ai-writing-suite/evals/detector/detector.py:262:    tier1_count = sum(1 for i in deduped if i["type"] == "tier1")
skills/ai-writing-suite/evals/detector/detector.py:263:    tier2_count = sum(1 for i in deduped if i["type"] == "tier2")
skills/ai-writing-suite/evals/detector/detector.py:264:    tier3_count = sum(1 for i in deduped if i["type"] == "tier3")
skills/ai-writing-suite/evals/detector/detector.py:265:
skills/ai-writing-suite/evals/detector/detector.py:266:    classification, confidence = _classify(
skills/ai-writing-suite/evals/detector/detector.py:267:        score, deduped, word_count, tier1_count, tier2_clusters)
skills/ai-writing-suite/evals/detector/detector.py:268:
skills/ai-writing-suite/evals/detector/detector.py:269:    return {
skills/ai-writing-suite/evals/detector/detector.py:270:        "score": score,
skills/ai-writing-suite/evals/detector/detector.py:271:        "label": label,
skills/ai-writing-suite/evals/detector/detector.py:272:        "issues": deduped,
skills/ai-writing-suite/evals/detector/detector.py:273:        "stats": {
skills/ai-writing-suite/evals/detector/detector.py:274:            "wordCount": word_count,
skills/ai-writing-suite/evals/detector/detector.py:275:            "contextMode": context_mode,
skills/ai-writing-suite/evals/detector/detector.py:276:            "tier1Count": tier1_count,
skills/ai-writing-suite/evals/detector/detector.py:277:            "tier2Count": tier2_count,
skills/ai-writing-suite/evals/detector/detector.py:278:            "tier2Clusters": tier2_clusters,
skills/ai-writing-suite/evals/detector/detector.py:279:            "tier3Count": tier3_count,
skills/ai-writing-suite/evals/detector/detector.py:280:            "patternCount": len(deduped) - tier1_count - tier2_count - tier3_count,
skills/ai-writing-suite/evals/detector/detector.py:281:        },
skills/ai-writing-suite/evals/detector/detector.py:282:        "classification": classification,
skills/ai-writing-suite/evals/detector/detector.py:283:        "confidence": confidence,
skills/ai-writing-suite/evals/detector/detector.py:284:    }
skills/ai-writing-suite/evals/detector/detector.py:285:
skills/ai-writing-suite/evals/detector/detector.py:286:
skills/ai-writing-suite/evals/detector/detector.py:287:def _detect_bullet_np(text, issues):
skills/ai-writing-suite/evals/detector/detector.py:288:    """Flag 5+ consecutive short (<=6 word) verbless bullet items."""
skills/ai-writing-suite/evals/detector/detector.py:289:    lines = re.split(r"\r?\n", text)
skills/ai-writing-suite/evals/detector/detector.py:290:    bullet_re = re.compile(r"^\s*(?:\*|-|•|\+)\s+(.+)$")
skills/ai-writing-suite/evals/detector/detector.py:291:    verb_re = re.compile(
skills/ai-writing-suite/evals/detector/detector.py:292:        r"\b(?:is|are|was|were|has|have|had|will|would|should|must|do|does|"
skills/ai-writing-suite/evals/detector/detector.py:293:        r"did|can|could|may|might|am|been|being)\b", re.I)
skills/ai-writing-suite/evals/detector/detector.py:294:    fence_re = re.compile(r"^\s*(?:```|~~~)")
skills/ai-writing-suite/evals/detector/detector.py:295:    run = []
skills/ai-writing-suite/evals/detector/detector.py:296:    blank = 0
skills/ai-writing-suite/evals/detector/detector.py:297:    in_fence = False
skills/ai-writing-suite/evals/detector/detector.py:298:
skills/ai-writing-suite/evals/detector/detector.py:299:    def flush():
skills/ai-writing-suite/evals/detector/detector.py:300:        nonlocal run, blank
skills/ai-writing-suite/evals/detector/detector.py:301:        if len(run) >= 5:
skills/ai-writing-suite/evals/detector/detector.py:302:            bare = [it for it in run
skills/ai-writing-suite/evals/detector/detector.py:303:                    if 0 < len(it.split()) <= 6 and not verb_re.search(it)]
skills/ai-writing-suite/evals/detector/detector.py:304:            if len(bare) >= 5 and len(bare) / len(run) >= 0.75:
skills/ai-writing-suite/evals/detector/detector.py:305:                issues.append({"type": "bullet-np-list",
skills/ai-writing-suite/evals/detector/detector.py:306:                               "text": f"{len(run)}-item bullet list of bare noun phrases",
skills/ai-writing-suite/evals/detector/detector.py:307:                               "severity": "high", "suggestion": None})
skills/ai-writing-suite/evals/detector/detector.py:308:        run = []
skills/ai-writing-suite/evals/detector/detector.py:309:        blank = 0
skills/ai-writing-suite/evals/detector/detector.py:310:
skills/ai-writing-suite/evals/detector/detector.py:311:    for line in lines:
skills/ai-writing-suite/evals/detector/detector.py:312:        if fence_re.match(line):
skills/ai-writing-suite/evals/detector/detector.py:313:            flush()
skills/ai-writing-suite/evals/detector/detector.py:314:            in_fence = not in_fence
skills/ai-writing-suite/evals/detector/detector.py:315:            continue
skills/ai-writing-suite/evals/detector/detector.py:316:        if in_fence:
skills/ai-writing-suite/evals/detector/detector.py:317:            continue
skills/ai-writing-suite/evals/detector/detector.py:318:        m = bullet_re.match(line)
skills/ai-writing-suite/evals/detector/detector.py:319:        if m:
skills/ai-writing-suite/evals/detector/detector.py:320:            run.append(m.group(1).strip())
skills/ai-writing-suite/evals/detector/detector.py:321:            blank = 0
skills/ai-writing-suite/evals/detector/detector.py:322:        elif line.strip() == "":
skills/ai-writing-suite/evals/detector/detector.py:323:            blank += 1
skills/ai-writing-suite/evals/detector/detector.py:324:            if blank >= 2:
skills/ai-writing-suite/evals/detector/detector.py:325:                flush()
skills/ai-writing-suite/evals/detector/detector.py:326:        else:
skills/ai-writing-suite/evals/detector/detector.py:327:            flush()
skills/ai-writing-suite/evals/detector/detector.py:328:    flush()
skills/ai-writing-suite/evals/detector/detector.py:329:
skills/ai-writing-suite/evals/detector/detector.py:330:
skills/ai-writing-suite/evals/detector/detector.py:331:def _classify(score, issues, word_count, tier1_count, tier2_clusters):
skills/ai-writing-suite/evals/detector/detector.py:332:    """GPTZero-shaped trinary classification + confidence. FN-biased."""
skills/ai-writing-suite/evals/detector/detector.py:333:    types = {i["type"] for i in issues}
skills/ai-writing-suite/evals/detector/detector.py:334:    has_cutoff = "cutoff-disclaimer" in types
skills/ai-writing-suite/evals/detector/detector.py:335:    has_reasoning = "reasoning-artifact" in types
skills/ai-writing-suite/evals/detector/detector.py:336:    has_chatbot = "chatbot" in types
skills/ai-writing-suite/evals/detector/detector.py:337:    has_transition = "transition" in types
skills/ai-writing-suite/evals/detector/detector.py:338:    dense_ai_vocab = (word_count >= 150 and tier1_count >= 5
skills/ai-writing-suite/evals/detector/detector.py:339:                      and tier2_clusters >= 2 and has_transition)
skills/ai-writing-suite/evals/detector/detector.py:340:    strong = ((1 if has_cutoff else 0)
skills/ai-writing-suite/evals/detector/detector.py:341:              + (1 if (has_reasoning and has_chatbot) else 0)
skills/ai-writing-suite/evals/detector/detector.py:342:              + (1 if dense_ai_vocab else 0))
skills/ai-writing-suite/evals/detector/detector.py:343:
skills/ai-writing-suite/evals/detector/detector.py:344:    if score < 15 and strong == 0:
skills/ai-writing-suite/evals/detector/detector.py:345:        classification = "HUMAN_ONLY"
skills/ai-writing-suite/evals/detector/detector.py:346:    elif strong >= 1 or score >= 70:
skills/ai-writing-suite/evals/detector/detector.py:347:        classification = "AI_ONLY"
skills/ai-writing-suite/evals/detector/detector.py:348:    else:
skills/ai-writing-suite/evals/detector/detector.py:349:        classification = "MIXED"
skills/ai-writing-suite/evals/detector/detector.py:350:
skills/ai-writing-suite/evals/detector/detector.py:351:    if strong >= 2 or has_cutoff or (score < 8 and word_count >= 100):
skills/ai-writing-suite/evals/detector/detector.py:352:        confidence = "high"
skills/ai-writing-suite/evals/detector/detector.py:353:    elif strong >= 1 or score < 20:
skills/ai-writing-suite/evals/detector/detector.py:354:        confidence = "medium"
skills/ai-writing-suite/evals/detector/detector.py:355:    else:
skills/ai-writing-suite/evals/detector/detector.py:356:        confidence = "low"
skills/ai-writing-suite/evals/detector/detector.py:357:    return classification, confidence
skills/ai-writing-suite/evals/detector/detector.py:358:
skills/ai-writing-suite/evals/detector/detector.py:359:
skills/ai-writing-suite/evals/detector/detector.py:360:def _unscored(label, word_count):
skills/ai-writing-suite/evals/detector/detector.py:361:    return {
skills/ai-writing-suite/evals/detector/detector.py:362:        "score": 0, "label": label, "issues": [],
skills/ai-writing-suite/evals/detector/detector.py:363:        "stats": {"wordCount": word_count}, "classification": "UNSCORED",
skills/ai-writing-suite/evals/detector/detector.py:364:        "confidence": "low",
skills/ai-writing-suite/evals/detector/detector.py:365:        "tooShort": label in ("Empty", "Too short"),
skills/ai-writing-suite/evals/detector/detector.py:366:        "tooLong": label == "Text too long",
skills/ai-writing-suite/evals/detector/detector.py:367:    }
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:1:---
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:2:name: voice-onboard
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:3:description: Interview an author and distill their historical writing into a reusable voice profile that comms-polish reads for voice matching. Ingests local files or pasted samples, extracts a 10-dimension style fingerprint with sample evidence, and writes _shared/voice-profile.md. Use when the user says "learn my voice", "match how I write", or before a series of posts that must stay on-voice.
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:4:---
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:5:
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:6:# voice-onboard
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:7:
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:8:Learn how *you* write, so the rest of the suite stops sounding like a clean
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:9:generic robot and starts sounding like you.
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:10:
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:11:The job is narrow: read your real writing, distill a **voice profile**, and write
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:12:it to a file the polish skill reads on every run. This skill does NOT draft or
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:13:rewrite anything — it only listens and profiles.
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:14:
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:15:## The mental model (for a product-owner learner)
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:16:
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:17:Think of it like building a feature table for a ranking model:
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:18:
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:19:- Your **writing samples** = raw training data.
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:20:- The **10 style dimensions** below = the feature schema.
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:21:- **`_shared/voice-profile.md`** = the published feature table.
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:22:- **`comms-polish`** = the model that reads that table at serving time.
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:23:
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:24:If the table is empty or guessed, the model falls back to a generic baseline.
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:25:So the whole point of this skill is: produce an honest, evidence-backed table.
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:26:
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:27:## What you read and write
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:28:
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:29:- **Reads (your samples):** local markdown/text files you point to, or text you
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:30:  paste inline. (A Confluence-page link as a voice source is **v2** — note it to
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:31:  the user, do not attempt to fetch it. No programmatic ingestion in v1.)
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:32:- **Fills in:** `../../_shared/host-profile-template.md` (the blank form).
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:33:- **Writes:** `../../_shared/voice-profile.md` (the contract file). The field
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:34:  names there are stable — keep every `## H2` header, because `comms-polish`
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:35:  reads by header. Renaming a header silently breaks voice matching.
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:36:
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:37:## How to run it (walk the user through, keep them in control)
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:38:
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:39:This is a guided, human-gated flow. Do one step, show the result, wait. Never
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:40:batch the whole thing and dump a finished profile — the user is the owner of
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:41:their own voice and must confirm each judgment.
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:42:
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:43:### Step 1 — Gather samples
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:44:
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:45:Ask the user for samples. State plainly what makes a good sample:
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:46:
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:47:- **3 minimum, 5-10 ideal.** Fewer than 3 → tell them confidence will be Low and
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:48:  the profile will be conservative. Don't force-extract from thin data.
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:49:- **Same genre as the target.** Learning their LinkedIn voice → ask for LinkedIn
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:50:  posts, not academic papers. Mixed genres → offer to extract two profiles
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:51:  rather than averaging them into a blur.
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:52:- **Their own words, not AI-polished.** A draft Claude already cleaned teaches
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:53:  the clean robot's voice, not theirs.
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:54:- **Recent (last ~6 months).** Voice drifts; recent samples track current style.
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:55:
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:56:How they can hand samples over:
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:57:
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:58:- Point to local files ("read everything in `~/writing/`") — you read them.
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:59:- Paste text inline, separated by `---`.
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:60:
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:61:Confirm what you received before extracting: "Got 6 samples — 4 blog posts,
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:62:2 memos. That's Medium confidence. Want me to extract now, or add more first?"
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:63:
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:64:### Step 2 — Extract the style fingerprint
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:65:
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:66:Profile each of the 10 dimensions below. **Every claim needs evidence from the
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:67:samples.** No evidence → write "Unknown — not enough signal", never invent.
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:68:
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:69:A trait counts only if it appears **3+ times**. One occurrence is noise. This is
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:70:the single most common extraction mistake — learning an accident as a habit.
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:71:
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:72:The 10 dimensions (these map 1:1 to the `voice-profile.md` headers):
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:73:
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:74:1. **Tone** — overall register (direct / warm / dry / formal).
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:75:2. **Sentence Length** — average words/sentence, short vs long share, rhythm habit.
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:76:3. **Vocabulary** — first-person usage, signature words, tics, domain terms.
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:77:4. **Vocabulary Do** — constructions they actively reach for.
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:78:5. **Vocabulary Don't** — common words they NEVER use. *Strongest signal* — a
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:79:   word someone never writes ("delve", "leverage") is more diagnostic than one
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:80:   they use often. Mine the absences.
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:81:6. **Signature Moves** — how they characteristically build a point ("not X but Y",
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:82:   lead with a number, end on a consequence).
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:83:7. **Punctuation & Formatting** — period vs comma balance, em-dash/ellipsis/
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:84:   exclamation density, list and emoji habits.
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:85:8. **Openings & Closings** — how they start and end (scene / claim / number;
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:86:   hook / consequence / trails off).
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:87:9. **Uncertainty Style** — how they signal doubt (quantified / blunt / hedged).
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:88:10. **Things To Avoid** — author-specific anti-patterns (marketing register,
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:89:    false balance, over-explaining to experts).
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:90:
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:91:Two extraction principles to repeat to yourself:
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:92:
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:93:- **Strip content, keep style.** They wrote about search ranking → that's the
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:94:  topic, not the voice. Look at rhythm, word choice, structure — not subject.
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:95:- **Don't average across genres.** Same person writes a tweet and a report
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:96:  differently. Mixed samples → split, don't flatten.
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:97:
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:98:### Step 3 — Fill the template, then show a draft
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:99:
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:100:Fill `host-profile-template.md` field by field with evidence. Then show the user
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:101:the draft profile and name the 3 most distinctive features you found, e.g.:
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:102:
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:103:> "Draft profile ready. The three loudest signals: (1) period-heavy short
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:104:> declaratives, (2) leads every post with a number, (3) never uses hype words
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:105:> like 'unlock' or 'amazing'. Does this sound like you? Anything off?"
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:106:
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:107:### Step 4 — Confirm, then write the contract file
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:108:
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:109:Only after the user confirms, write the profile to
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:110:`../../_shared/voice-profile.md`, preserving every `## H2` header. If a profile
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:111:already exists, show what changed before overwriting — don't silently replace
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:112:their previous one.
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:113:
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:114:Tell the user where it landed and that `comms-polish` will now read it
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:115:automatically.
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:116:
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:117:### Step 5 — Leave a calibration loop open
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:118:
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:119:A profile is a living file, not a one-shot. Tell the user:
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:120:
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:121:- "After a few polish runs, if something feels 'not me', come back and we'll
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:122:  adjust the profile."
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:123:- Note the sample date in the changelog so stale profiles are visible later.
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:124:- If their style drifts, new samples should *replace* old ones, not mix in.
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:125:
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:126:## Safety & boundaries
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:127:
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:128:- **Never invent voice.** Thin samples → say "I could only extract X and Y
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:129:  confidently; the rest is blank." Honest gaps beat confident fiction.
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:130:- **Profile is not a permanent contract.** Prompt re-calibration periodically.
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:131:- **Stay in your lane.** This skill profiles; it does not rewrite. Rewriting is
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:132:  `comms-polish`. (And note: this suite is separate from the personal
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:133:  writing-vault "never ghostwrite" pipeline — see the project plan, R1.)
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:134:- **Self-improvement is human-gated (suite-wide).** See "Self-improvement" below;
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:135:  never auto-edit this SKILL.md.
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:136:
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:137:## Self-improvement (human-gated)
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:138:
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:139:This skill participates in the suite's human-gated self-improvement loop. The
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:140:full protocol is in `../../_shared/self-improvement.md`; follow it, do not restate
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:141:it. In short:
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:142:
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:143:- **On start:** read `../../_shared/learned-rules.md` and apply any entry whose
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:144:  `status: active` and whose scope is `voice-onboard` or `all` (e.g. an approved
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:145:  extraction-judgment rule). Degrade gracefully if the file is absent.
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:146:- **On end:** if a repeatable extraction correction surfaced this session (a voice
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:147:  judgment the user overrode that would recur), **propose** one candidate rule
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:148:  (rule + session-grounded rationale + scope) and **wait for explicit approval**
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:149:  before appending it to `learned-rules.md`. Propose nothing if nothing repeatable
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:150:  surfaced.
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:151:- **Never** auto-edit this SKILL.md — approved rules live only in
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:152:  `learned-rules.md` (append-only). Each rule is eval-measured in Layer 3 before
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:153:  it is trusted.
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:154:
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:155:## Deferred to v2 (note, don't build)
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:156:
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:157:- Confluence-page link as a voice source (fetch/ingest).
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:158:- Bilingual (Chinese) extraction path.
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:159:- Any programmatic/scripted sample ingestion.
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:160:
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:161:<!--
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:162:  ATTRIBUTION
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:163:  -----------
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:164:  Flow + 10-dimension taxonomy adapted from weijt606/anti-vibe-writing
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:165:  (references/learning-mode.md, assets/style-extraction-prompt.md, MIT), ported
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:166:  from Chinese to English. Do's/Don'ts "Style DNA" framing from
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:167:  donghuixin/AI-Vibe-Writing-Skills (1_style_extractor.md, MIT). Full copyright
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:168:  lines in the suite NOTICE.md.
skills/ai-writing-suite/skills/voice-onboard/SKILL.md:169:-->
skills/ai-writing-suite/evals/fixtures/test_fixtures.py:1:"""Unit tests for the fixtures harness. Run: python3 -m unittest discover.
skills/ai-writing-suite/evals/fixtures/test_fixtures.py:2:
skills/ai-writing-suite/evals/fixtures/test_fixtures.py:3:These tests assert the fixture SUITE is well-formed and stays calibrated:
skills/ai-writing-suite/evals/fixtures/test_fixtures.py:4:  - every fixture has the required fields
skills/ai-writing-suite/evals/fixtures/test_fixtures.py:5:  - detector scores land in the declared bands (so a fixture can't silently rot)
skills/ai-writing-suite/evals/fixtures/test_fixtures.py:6:  - the naive-baseline miss rate stays in the 30-40% calibration band
skills/ai-writing-suite/evals/fixtures/test_fixtures.py:7:  - the LLM-judge prompt builds for every fixture (the SKIP path is sound)
skills/ai-writing-suite/evals/fixtures/test_fixtures.py:8:"""
skills/ai-writing-suite/evals/fixtures/test_fixtures.py:9:
skills/ai-writing-suite/evals/fixtures/test_fixtures.py:10:import unittest
skills/ai-writing-suite/evals/fixtures/test_fixtures.py:11:
skills/ai-writing-suite/evals/fixtures/test_fixtures.py:12:from detector.detector import analyze
skills/ai-writing-suite/evals/fixtures/test_fixtures.py:13:from fixtures.run_fixtures import (
skills/ai-writing-suite/evals/fixtures/test_fixtures.py:14:    load_fixtures, build_judge_prompt, _extract_judge_template)
skills/ai-writing-suite/evals/fixtures/test_fixtures.py:15:
skills/ai-writing-suite/evals/fixtures/test_fixtures.py:16:REQUIRED = {"id", "genre", "difficulty", "before", "after",
skills/ai-writing-suite/evals/fixtures/test_fixtures.py:17:            "rubric_focus", "expect_baseline"}
skills/ai-writing-suite/evals/fixtures/test_fixtures.py:18:
skills/ai-writing-suite/evals/fixtures/test_fixtures.py:19:
skills/ai-writing-suite/evals/fixtures/test_fixtures.py:20:class FixtureShape(unittest.TestCase):
skills/ai-writing-suite/evals/fixtures/test_fixtures.py:21:    def test_all_fixtures_have_required_fields(self):
skills/ai-writing-suite/evals/fixtures/test_fixtures.py:22:        for f in load_fixtures()["fixtures"]:
skills/ai-writing-suite/evals/fixtures/test_fixtures.py:23:            missing = REQUIRED - set(f)
skills/ai-writing-suite/evals/fixtures/test_fixtures.py:24:            self.assertFalse(missing, f"{f.get('id')} missing {missing}")
skills/ai-writing-suite/evals/fixtures/test_fixtures.py:25:
skills/ai-writing-suite/evals/fixtures/test_fixtures.py:26:    def test_four_genres_present(self):
skills/ai-writing-suite/evals/fixtures/test_fixtures.py:27:        genres = {f["genre"] for f in load_fixtures()["fixtures"]}
skills/ai-writing-suite/evals/fixtures/test_fixtures.py:28:        self.assertEqual(genres, {"tweet", "linkedin", "readme", "memo"})
skills/ai-writing-suite/evals/fixtures/test_fixtures.py:29:
skills/ai-writing-suite/evals/fixtures/test_fixtures.py:30:
skills/ai-writing-suite/evals/fixtures/test_fixtures.py:31:class ScoreBands(unittest.TestCase):
skills/ai-writing-suite/evals/fixtures/test_fixtures.py:32:    def test_before_after_scores_in_band(self):
skills/ai-writing-suite/evals/fixtures/test_fixtures.py:33:        for f in load_fixtures()["fixtures"]:
skills/ai-writing-suite/evals/fixtures/test_fixtures.py:34:            before = analyze(f["before"])["score"]
skills/ai-writing-suite/evals/fixtures/test_fixtures.py:35:            after = analyze(f["after"])["score"]
skills/ai-writing-suite/evals/fixtures/test_fixtures.py:36:            if "before_band_min" in f:
skills/ai-writing-suite/evals/fixtures/test_fixtures.py:37:                self.assertGreaterEqual(before, f["before_band_min"],
skills/ai-writing-suite/evals/fixtures/test_fixtures.py:38:                                        f"{f['id']} before={before}")
skills/ai-writing-suite/evals/fixtures/test_fixtures.py:39:            if "before_band_max" in f:
skills/ai-writing-suite/evals/fixtures/test_fixtures.py:40:                self.assertLessEqual(before, f["before_band_max"],
skills/ai-writing-suite/evals/fixtures/test_fixtures.py:41:                                     f"{f['id']} before={before}")
skills/ai-writing-suite/evals/fixtures/test_fixtures.py:42:            self.assertLessEqual(after, f["after_band_max"],
skills/ai-writing-suite/evals/fixtures/test_fixtures.py:43:                                 f"{f['id']} after={after}")
skills/ai-writing-suite/evals/fixtures/test_fixtures.py:44:
skills/ai-writing-suite/evals/fixtures/test_fixtures.py:45:
skills/ai-writing-suite/evals/fixtures/test_fixtures.py:46:class Calibration(unittest.TestCase):
skills/ai-writing-suite/evals/fixtures/test_fixtures.py:47:    def test_naive_baseline_misses_30_to_40_percent(self):
skills/ai-writing-suite/evals/fixtures/test_fixtures.py:48:        data = load_fixtures()
skills/ai-writing-suite/evals/fixtures/test_fixtures.py:49:        thr = data["baseline_threshold"]
skills/ai-writing-suite/evals/fixtures/test_fixtures.py:50:        miss = sum(1 for f in data["fixtures"]
skills/ai-writing-suite/evals/fixtures/test_fixtures.py:51:                   if analyze(f["before"])["score"] < thr)
skills/ai-writing-suite/evals/fixtures/test_fixtures.py:52:        total = len(data["fixtures"])
skills/ai-writing-suite/evals/fixtures/test_fixtures.py:53:        pct = 100 * miss / total
skills/ai-writing-suite/evals/fixtures/test_fixtures.py:54:        self.assertTrue(30 <= pct <= 40,
skills/ai-writing-suite/evals/fixtures/test_fixtures.py:55:                        f"miss rate {pct:.0f}% outside 30-40% target")
skills/ai-writing-suite/evals/fixtures/test_fixtures.py:56:
skills/ai-writing-suite/evals/fixtures/test_fixtures.py:57:    def test_expect_baseline_matches_actual(self):
skills/ai-writing-suite/evals/fixtures/test_fixtures.py:58:        # The declared expect_baseline must match what the detector actually does.
skills/ai-writing-suite/evals/fixtures/test_fixtures.py:59:        data = load_fixtures()
skills/ai-writing-suite/evals/fixtures/test_fixtures.py:60:        thr = data["baseline_threshold"]
skills/ai-writing-suite/evals/fixtures/test_fixtures.py:61:        for f in data["fixtures"]:
skills/ai-writing-suite/evals/fixtures/test_fixtures.py:62:            caught = analyze(f["before"])["score"] >= thr
skills/ai-writing-suite/evals/fixtures/test_fixtures.py:63:            expected = "catch" if caught else "miss"
skills/ai-writing-suite/evals/fixtures/test_fixtures.py:64:            self.assertEqual(f["expect_baseline"], expected,
skills/ai-writing-suite/evals/fixtures/test_fixtures.py:65:                             f"{f['id']}: declared {f['expect_baseline']} "
skills/ai-writing-suite/evals/fixtures/test_fixtures.py:66:                             f"but detector would {expected}")
skills/ai-writing-suite/evals/fixtures/test_fixtures.py:67:
skills/ai-writing-suite/evals/fixtures/test_fixtures.py:68:
skills/ai-writing-suite/evals/fixtures/test_fixtures.py:69:class JudgePrompt(unittest.TestCase):
skills/ai-writing-suite/evals/fixtures/test_fixtures.py:70:    def test_prompt_builds_for_every_fixture(self):
skills/ai-writing-suite/evals/fixtures/test_fixtures.py:71:        template = _extract_judge_template()
skills/ai-writing-suite/evals/fixtures/test_fixtures.py:72:        self.assertIn("{before}", template)  # template has the slots
skills/ai-writing-suite/evals/fixtures/test_fixtures.py:73:        for f in load_fixtures()["fixtures"]:
skills/ai-writing-suite/evals/fixtures/test_fixtures.py:74:            prompt = build_judge_prompt(f, template)
skills/ai-writing-suite/evals/fixtures/test_fixtures.py:75:            # All slots filled — no stray placeholders left.
skills/ai-writing-suite/evals/fixtures/test_fixtures.py:76:            for slot in ("{before}", "{after}", "{genre}", "{rubric_focus}"):
skills/ai-writing-suite/evals/fixtures/test_fixtures.py:77:                self.assertNotIn(slot, prompt, f"{f['id']} left {slot} unfilled")
skills/ai-writing-suite/evals/fixtures/test_fixtures.py:78:            self.assertIn(f["before"], prompt)
skills/ai-writing-suite/evals/fixtures/test_fixtures.py:79:            self.assertIn(f["after"], prompt)
skills/ai-writing-suite/evals/fixtures/test_fixtures.py:80:
skills/ai-writing-suite/evals/fixtures/test_fixtures.py:81:
skills/ai-writing-suite/evals/fixtures/test_fixtures.py:82:if __name__ == "__main__":
skills/ai-writing-suite/evals/fixtures/test_fixtures.py:83:    unittest.main()
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:1:# Scenario Presets
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:2:
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:3:Different writing scenarios carry different hard constraints — length, structure,
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:4:whether emoji belong, the scale of reader attention. This file pins down those
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:5:constraints for the four genres comms-polish targets in v1: **tweet / X, LinkedIn,
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:6:README, memo**.
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:7:
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:8:> Why presets exist: the AI-tell catalog under `../../../_shared/patterns/` says
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:9:> *what* reads as machine-written. A preset says *which of those tells matter most
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:10:> here* and *what to leave alone*, so a README isn't edited like a tweet. Presets
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:11:> shape **form**; a voice profile (when one exists) shapes **voice**. They stack
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:12:> when they don't conflict; when they do, voice loses to a hard form constraint
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:13:> (a tweet's 280-char limit beats a profile's love of long sentences).
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:14:
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:15:Adapted from `weijt606/anti-vibe-writing` (`scenario-presets.md`, MIT). The
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:16:original ships five Chinese-platform scenarios; this is the English subset mapped
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:17:to the v1 genres. Bilingual presets are a v2 item (design §5, deferred list).
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:18:
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:19:## How to use a preset
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:20:
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:21:1. Detect the genre from the request (or ask if ambiguous).
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:22:2. Load the matching preset below.
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:23:3. **Weight** the named catalog categories harder during the scan — those are the
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:24:   tells that hurt most in this genre.
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:25:4. Respect the **leave alone** list — these are not tells *here*, even if the
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:26:   catalog flags them in general.
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:27:5. Hold the target tone/length as the rewrite goal.
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:28:
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:29:Each preset names catalog categories by their file id (e.g. `structural-tells`,
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:30:`punctuation-formatting`) so the weighting stays traceable to the single source of
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:31:truth instead of re-listing patterns inline.
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:32:
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:33:---
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:34:
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:35:## 1. Tweet / X
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:36:
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:37:**Form constraints:**
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:38:- One tweet ≤ 280 characters. A thread: every tweet stands alone; tweet #1 must
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:39:  read on its own.
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:40:- No heading levels. No markdown lists (the platform won't render them).
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:41:- Links and @mentions used sparingly.
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:42:
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:43:**Weight these tells harder** (from the catalog):
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:44:- `hedging-filler` — "let's", "today I want to share", "first, some context"
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:45:  openers. The first line must hook; drop the runway.
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:46:- `structural-tells` — rule-of-three and "not X but Y" theatrics read as
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:47:  performance, not a person.
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:48:- `significance-attribution` — "many / some / a lot": replace with the actual
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:49:  number.
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:50:
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:51:**Target tone/length:** punchy, one idea per tweet, leave a reason to read the
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:52:next line. Inversion, fragments, and an incomplete sentence are fine here.
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:53:
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:54:**Leave alone:**
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:55:- Sentence fragments and missing connectives — they're native to the genre, not a
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:56:  tell.
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:57:- Casual punctuation and lowercase, *only* if the author's voice already does
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:58:  this. Never touch numbers, names, or links.
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:59:
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:60:**Endings that work:** a sharp question, a concrete next step, one quotable line,
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:61:or just stop on the fact. Never "more in the next tweet" — the next tweet starts
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:62:itself.
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:63:
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:64:---
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:65:
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:66:## 2. LinkedIn
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:67:
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:68:**Form constraints:**
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:69:- Short-to-medium. The first 1–2 lines show before the "see more" fold — they
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:70:  carry the whole post.
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:71:- Line breaks between short paragraphs; long blocks die on a phone screen.
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:72:- Hashtags by platform habit (a few, at the end), not stuffed inline.
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:73:
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:74:**Weight these tells harder:**
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:75:- `communication-artifacts` — engagement hooks ("Agree? 👇"), sycophancy, and
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:76:  the LinkedIn-broetry "one sentence per line for fake gravity" pattern.
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:77:- `punctuation-formatting` — emoji-as-bullets, decorative section markers, hashtag
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:78:  stuffing.
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:79:- `significance-attribution` — promotional adjectives and self-congratulation
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:80:  ("thrilled", "humbled", "game-changer").
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:81:
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:82:**Target tone/length:** professional but human; a point of view, not balanced
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:83:neutrality. Specific story or claim up front, payoff the reader can take away.
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:84:
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:85:**Leave alone:**
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:86:- A genuine first-person opinion or a real anecdote — these are the point.
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:87:- A single emoji *if* it's the author's habit and earns its place.
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:88:
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:89:**Endings that work:** a concrete takeaway, a real question (not bait), or a
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:90:specific next step. Drop "What do you think? Let me know in the comments."
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:91:
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:92:---
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:93:
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:94:## 3. README
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:95:
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:96:**Form constraints:**
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:97:- Headings, lists, code blocks, and tables are allowed and often required.
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:98:- Code, commands, file paths, flags, and version numbers are sacred — never
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:99:  reworded.
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:100:- Length follows the project; a quickstart is short, a reference is long.
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:101:
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:102:**Weight these tells harder:**
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:103:- `structural-tells` — stock sections (Overview, Key Features, Conclusion) that
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:104:  exist to fill a template; over-structure; inline-header lists that should be
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:105:  prose.
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:106:- `significance-attribution` — "powerful", "seamless", "robust", "enterprise-grade"
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:107:  promotional adjectives; significance inflation about what the tool "enables".
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:108:- `lexical-tells` — "leverage", "utilize", "facilitate" where a plain verb works.
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:109:
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:110:**Target tone/length:** show, don't sell. Lead with what it does and how to run
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:111:it. Each heading must carry information, not decorate.
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:112:
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:113:**Leave alone:**
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:114:- Real lists, tables, and code blocks — structure is *correct* here, not a tell.
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:115:- Necessary headings — a README *should* be navigable.
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:116:- Technical terms — define on first use only if the reader isn't assumed to be a
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:117:  peer.
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:118:
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:119:**Endings that work:** stop after the last real instruction. No "Conclusion"
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:120:section restating the intro.
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:121:
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:122:---
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:123:
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:124:## 4. Memo / Internal Doc
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:125:
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:126:**Form constraints:**
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:127:- Tight structure; layered headings are fine.
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:128:- Long sentences and long paragraphs are allowed when they stay precise.
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:129:- Data and citations must be checkable (links, doc refs, ticket numbers).
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:130:- No emoji. Jargon allowed, defined on first use unless the audience is named as
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:131:  expert.
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:132:
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:133:**Weight these tells harder:**
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:134:- `hedging-filler` — stacked hedging that hides the actual uncertainty ("perhaps",
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:135:  "to some extent", "it could be argued"); signposting; non-conclusions like
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:136:  "it depends" or "consider all factors".
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:137:- `significance-attribution` — vague attribution ("studies show", "experts
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:138:  agree") with no source; consultant-speak.
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:139:- `structural-tells` — rule-of-three; data dropped into a table with no reading.
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:140:
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:141:**Target tone/length:** state the conclusion. Quantify uncertainty instead of
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:142:hiding it. Use explicit branches ("if X, then Y; else Z"). Write the tradeoff:
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:143:what was chosen, what was dropped, and why.
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:144:
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:145:**Leave alone:**
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:146:- A real caveat that carries genuine uncertainty — keep it, just make it specific.
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:147:- Long precise sentences — length isn't a tell when every word is load-bearing.
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:148:- Legal, security, financial, or safety warnings — never polished away.
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:149:
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:150:**Endings that work:** a clear recommendation or decision, not a balanced summary
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:151:that refuses to judge.
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:152:
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:153:---
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:154:
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:155:## Cross-scenario invariants
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:156:
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:157:No matter the genre, these never change (these are the bottom line, not preset
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:158:preferences):
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:159:
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:160:- Don't invent facts.
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:161:- Don't strengthen the author's position for them.
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:162:- Keep caveats that carry real uncertainty.
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:163:- Numbers, names, and quotes are immutable unless the user asks.
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:164:- Drop empty buzzwords ("leverage", "synergy", "circle back", "move the needle").
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:165:
skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:166:Scenarios change which tells you weight. The anti-AI floor stays fixed.
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:1:#!/usr/bin/env python3
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:2:"""Run the before/after fixtures. Deterministic half always; LLM half on demand.
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:3:
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:4:Run from `evals/`:
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:5:    python3 -m fixtures.run_fixtures            # deterministic + calibration
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:6:    python3 -m fixtures.run_fixtures --judge    # also emit LLM-judge prompts
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:7:
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:8:WHY a model is NOT required: the deterministic half (detector score bands +
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:9:naive-baseline miss rate) is the part that gates CI. The LLM half needs a model;
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:10:when none is wired in we print the judge prompts and mark them SKIPPED so a
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:11:reader can see exactly what *would* run, instead of a green check that proved
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:12:nothing. There is intentionally no API call here — this repo ships zero deps and
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:13:no key. A host integration calls `build_judge_prompt()` and sends it to whatever
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:14:model the surface provides.
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:15:"""
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:16:
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:17:import argparse
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:18:import json
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:19:import os
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:20:import sys
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:21:
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:22:# Allow running both as a module (-m fixtures.run_fixtures) and as a script.
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:23:sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:24:from detector.detector import analyze  # noqa: E402
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:25:
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:26:HERE = os.path.dirname(os.path.abspath(__file__))
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:27:FIXTURES_PATH = os.path.join(HERE, "fixtures.json")
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:28:RUBRIC_PATH = os.path.join(HERE, "rubric.md")
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:29:
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:30:
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:31:def load_fixtures():
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:32:    with open(FIXTURES_PATH, encoding="utf-8") as fh:
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:33:        return json.load(fh)
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:34:
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:35:
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:36:def _in_band(score, lo=None, hi=None):
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:37:    if lo is not None and score < lo:
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:38:        return False
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:39:    if hi is not None and score > hi:
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:40:        return False
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:41:    return True
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:42:
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:43:
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:44:def run_deterministic(data):
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:45:    """Assert detector scores land in the declared bands. Returns (passes, fails)."""
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:46:    threshold = data["baseline_threshold"]
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:47:    passes = fails = 0
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:48:    miss = total = 0
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:49:
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:50:    print("=== Deterministic check (detector score bands) ===\n")
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:51:    for f in data["fixtures"]:
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:52:        before = analyze(f["before"])["score"]
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:53:        after = analyze(f["after"])["score"]
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:54:
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:55:        ok = True
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:56:        reasons = []
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:57:        if not _in_band(before, f.get("before_band_min"), f.get("before_band_max")):
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:58:            ok = False
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:59:            reasons.append(
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:60:                f"before={before} outside "
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:61:                f"[{f.get('before_band_min', '-')}, {f.get('before_band_max', '-')}]")
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:62:        if not _in_band(after, hi=f.get("after_band_max")):
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:63:            ok = False
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:64:            reasons.append(f"after={after} > {f.get('after_band_max')}")
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:65:
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:66:        if ok:
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:67:            passes += 1
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:68:        else:
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:69:            fails += 1
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:70:
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:71:        # Naive-baseline accounting: a flat threshold flags `before` as AI iff
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:72:        # score >= threshold. A "miss" is an AI draft that scores below it.
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:73:        total += 1
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:74:        caught = before >= threshold
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:75:        if not caught:
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:76:            miss += 1
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:77:
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:78:        mark = "PASS" if ok else "FAIL"
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:79:        print(f"[{mark}] {f['id']:22} before={before:3} after={after:3} "
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:80:              f"baseline={'CATCH' if caught else 'MISS '}")
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:81:        for r in reasons:
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:82:            print(f"        {r}")
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:83:
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:84:    miss_pct = 100 * miss / total if total else 0
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:85:    print(f"\nNaive-baseline miss rate: {miss}/{total} = {miss_pct:.0f}% "
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:86:          f"(threshold={threshold}; calibration target 30-40%)")
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:87:    calib_ok = 30 <= miss_pct <= 40
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:88:    print(f"Calibration in target band: {'YES' if calib_ok else 'NO'}")
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:89:    if not calib_ok:
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:90:        fails += 1  # treat out-of-band calibration as a suite failure
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:91:    return passes, fails
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:92:
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:93:
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:94:def build_judge_prompt(fixture, rubric_template):
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:95:    """Fill the rubric.md judge template for one fixture."""
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:96:    return (rubric_template
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:97:            .replace("{genre}", fixture["genre"])
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:98:            .replace("{subtle_tell}", fixture.get("subtle_tell",
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:99:                     "obvious AI vocabulary and formatting"))
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:100:            .replace("{rubric_focus}", ", ".join(fixture["rubric_focus"]))
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:101:            .replace("{before}", fixture["before"])
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:102:            .replace("{after}", fixture["after"]))
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:103:
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:104:
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:105:def _extract_judge_template():
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:106:    """Pull the fenced judge-prompt template out of rubric.md."""
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:107:    with open(RUBRIC_PATH, encoding="utf-8") as fh:
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:108:        text = fh.read()
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:109:    start = text.find("```", text.find("Judge prompt template"))
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:110:    end = text.find("```", start + 3)
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:111:    return text[start + 3:end].strip()
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:112:
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:113:
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:114:def run_judge(data):
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:115:    """Emit the filled judge prompts and mark them SKIPPED (no model wired in).
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:116:
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:117:    A host integration would replace the `verdict = None` line with a real model
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:118:    call and aggregate per rubric.md. We never fabricate a verdict offline."""
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:119:    template = _extract_judge_template()
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:120:    print("\n=== LLM-judge check ===")
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:121:    print("No model is configured in this offline harness — emitting the prompts "
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:122:          "that WOULD be sent, marked SKIPPED.\n")
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:123:    for f in data["fixtures"]:
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:124:        prompt = build_judge_prompt(f, template)
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:125:        verdict = None  # offline: never invent a verdict
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:126:        print(f"[SKIP] {f['id']} (focus: {', '.join(f['rubric_focus'])})")
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:127:        # Show the first 2 lines of the filled prompt as proof it built.
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:128:        head = "\n".join(prompt.splitlines()[:2])
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:129:        print(f"        prompt[0:2]: {head[:90]}...")
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:130:    print("\nLLM-judge: 0 scored, all SKIPPED (wire a model to run).")
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:131:
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:132:
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:133:def main(argv=None):
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:134:    argv = argv if argv is not None else sys.argv[1:]
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:135:    ap = argparse.ArgumentParser(description="Run before/after eval fixtures.")
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:136:    ap.add_argument("--judge", action="store_true",
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:137:                    help="also emit LLM-judge prompts (skipped offline)")
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:138:    args = ap.parse_args(argv)
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:139:
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:140:    data = load_fixtures()
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:141:    passes, fails = run_deterministic(data)
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:142:    if args.judge:
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:143:        run_judge(data)
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:144:
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:145:    print(f"\nDeterministic: {passes} passed, {fails} failed.")
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:146:    return 1 if fails else 0
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:147:
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:148:
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:149:if __name__ == "__main__":
skills/ai-writing-suite/evals/fixtures/run_fixtures.py:150:    sys.exit(main())

hook: PostToolUse Completed
hook: PostToolUse Completed
hook: PostToolUse Completed
2026-06-07T21:01:11.445194Z ERROR codex_core::tools::router: error=write_stdin failed: stdin is closed for this session; rerun exec_command with tty=true to keep stdin open
hook: PreToolUse
hook: PreToolUse
hook: PreToolUse
hook: PreToolUse Completed
hook: PreToolUse Completed
hook: PreToolUse Completed
exec
/bin/zsh -lc "rg -n '\"source\"\\s*:\\s*\\{|\"path\"\\s*:' /Users/surahli/.codex /Users/surahli/.agents -g 'marketplace.json' -g 'plugin.json' 2>/dev/null | sed -n '1,240p'" in /Users/surahli/Documents/ai-writing-suite
exec
/bin/zsh -lc "git ls-files -z | xargs -0 rg -n 'packaging/|sync\\.sh|See "'`packaging/`|'"\\.cursor/rules|--sparse' --glob '"'!docs/design-ai-writing-suite-v1-2026-06-06.md'"' --glob '"'!docs/code-review-v1-2026-06-06.md'"'" in /Users/surahli/Documents/ai-writing-suite
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
docs/code-review-v1-2026-06-06.md:23:stdlib-only confirmed (no package.json/requirements/pyproject) → D5 holds. `sync.sh` idempotent;
docs/code-review-v1-2026-06-06.md:40:generic 5-entry KB; full comms-qa retrieval is v2." Re-run `sync.sh`.
docs/code-review-v1-2026-06-06.md:67:- **n1** `evals/` excluded from packaged targets (CI-only) — document why in `packaging/README.md`.
docs/code-review-v1-2026-06-06.md:80:- Honest scaffolding (v2 stubs labeled; P31-P43 corruption disclosed; sync.sh single-source rule).
skills/ai-writing-suite/CHANGELOG.md:23:  directory. (Corrects the earlier plan that targeted `.cursor/rules/*.mdc`, the wrong
skills/ai-writing-suite/CHANGELOG.md:29:- **Generate-and-sync packaging** (`packaging/` + `sync.sh`) — obsolete now that every
skills/ai-writing-suite/CHANGELOG.md:42:- **Directory structure** — standardized layout with `skills/`, `_shared/` (knowledge, patterns, voice profiles), and `packaging/` for multi-surface distribution.
skills/ai-writing-suite/CHANGELOG.md:89:- **Sync tooling scaffold** (`packaging/sync.sh`) — single source of truth distributed to four surfaces (Claude, Codex, Cursor, RovoDev).
docs/packaging.md:8:> This replaces the earlier generate-and-sync approach (`packaging/` + `sync.sh`), which was
docs/packaging.md:27:- **Cursor:** copy `skills/ai-writing-suite/` into `~/.cursor/skills/ai-writing-suite/` (or a project's `.cursor/skills/`). Cursor reads Anthropic-format `SKILL.md` Agent Skills natively; no manifest needed. (Not `.cursor/rules/*.mdc` — that is passive context injection, the wrong primitive for callable skills.)
README.md:53:Codex resolves the plugin from the same source tree — no `--sparse` needed; the Codex
docs/design-ai-writing-suite-v1-2026-06-06.md:59:| **conorbronsdon/avoid-ai-writing** | Programmatic JS detector + tests + CI, CATEGORIES taxonomy, multi-surface packaging (Claude plugin + Cursor `.mdc`) + `sync-plugin-skill.sh` | Detector (v2), packaging/sync scaffold, Cursor target |
docs/design-ai-writing-suite-v1-2026-06-06.md:88:├── packaging/
docs/design-ai-writing-suite-v1-2026-06-06.md:89:│   ├── sync.sh                        # single source → 4 targets
docs/design-ai-writing-suite-v1-2026-06-06.md:149:- **R4 — 4-surface sync drift.** Single source of truth + `sync.sh` (avoid-ai pattern).
docs/design-ai-writing-suite-v1-2026-06-06.md:185:- 4 MIT repos → detectors, scenario presets, voice templates, packaging/sync scaffolds.
skills/ai-writing-suite/README.md:161:See `packaging/` for surface-specific installation instructions (coming in v2).

hook: PostToolUse
exec
/bin/zsh -lc "find /Users/surahli/.codex/plugins/cache /Users/surahli/.codex/plugins /Users/surahli/.agents/plugins -path '*/marketplace.json' -maxdepth 8 -type f 2>/dev/null | sort | sed -n '1,120p'" in /Users/surahli/Documents/ai-writing-suite
hook: PostToolUse
 succeeded in 193ms:
hook: PostToolUse
 succeeded in 260ms:
/Users/surahli/.codex/plugins/cache/sisyphuslabs/.agents/plugins/marketplace.json
/Users/surahli/.codex/plugins/cache/sisyphuslabs/.agents/plugins/marketplace.json

hook: PostToolUse Completed
hook: PostToolUse Completed
hook: PostToolUse Completed
hook: PreToolUse
hook: PreToolUse Completed
exec
/bin/zsh -lc "nl -ba /Users/surahli/.codex/plugins/cache/sisyphuslabs/.agents/plugins/marketplace.json | sed -n '1,200p'" in /Users/surahli/Documents/ai-writing-suite
 succeeded in 0ms:
     1	{
     2		"name": "sisyphuslabs",
     3		"plugins": [
     4			{
     5				"name": "omo",
     6				"source": {
     7					"source": "local",
     8					"path": "./omo/0.1.0"
     9				}
    10			}
    11		]
    12	}

hook: PostToolUse
hook: PostToolUse Completed
codex
For the Codex path question, I found a local installed marketplace using the same shape: a root marketplace under `.agents/plugins/marketplace.json` points to `./omo/0.1.0`, sibling to `.agents/`, not under `plugins/`. That supports repo-root-relative semantics rather than “must be under `plugins/`.”
hook: PreToolUse
hook: PreToolUse Completed
collab: Wait
hook: PostToolUse
hook: PostToolUse Completed
2026-06-07T21:02:52.468391Z ERROR codex_core::tools::router: error=an agent cannot close itself; return your result and let the parent close you if needed
hook: PreToolUse
hook: PreToolUse
hook: PreToolUse
hook: PreToolUse Completed
hook: PreToolUse Completed
hook: PreToolUse Completed
exec
/bin/zsh -lc "codex plugin marketplace --help | sed -n '1,220p'" in /Users/surahli/Documents/ai-writing-suite
exec
/bin/zsh -lc "codex plugin --help | sed -n '1,220p'" in /Users/surahli/Documents/ai-writing-suite
exec
/bin/zsh -lc "codex plugin add --help | sed -n '1,180p'" in /Users/surahli/Documents/ai-writing-suite
 succeeded in 1683ms:
WARNING: proceeding, even though we could not update PATH: Operation not permitted (os error 1)
Add, list, upgrade, or remove configured plugin marketplaces

Usage: codex plugin marketplace [OPTIONS] <COMMAND>

Commands:
  add      Add a local or Git marketplace to the configured marketplace sources
  list     List plugin marketplaces Codex is currently considering and their roots
  upgrade  Refresh configured Git marketplace snapshots
  remove   Remove a configured marketplace source by name
  help     Print this message or the help of the given subcommand(s)

Options:
  -c, --config <key=value>
          Override a configuration value that would otherwise be loaded from `~/.codex/config.toml`.
          Use a dotted path (`foo.bar.baz`) to override nested values. The `value` portion is parsed
          as TOML. If it fails to parse as TOML, the raw string is used as a literal.
          
          Examples: - `-c model="o3"` - `-c 'sandbox_permissions=["disk-full-read-access"]'` - `-c
          shell_environment_policy.inherit=all`

      --enable <FEATURE>
          Enable a feature (repeatable). Equivalent to `-c features.<name>=true`

      --disable <FEATURE>
          Disable a feature (repeatable). Equivalent to `-c features.<name>=false`

  -h, --help
          Print help (see a summary with '-h')

 succeeded in 1683ms:
WARNING: proceeding, even though we could not update PATH: Operation not permitted (os error 1)
Manage Codex plugins

Usage: codex plugin [OPTIONS] <COMMAND>

Commands:
  add          Install a plugin from a configured marketplace snapshot
  list         List plugins available from configured marketplace snapshots
  marketplace  Add, list, upgrade, or remove configured plugin marketplaces
  remove       Remove an installed plugin from local config and cache
  help         Print this message or the help of the given subcommand(s)

Options:
  -c, --config <key=value>
          Override a configuration value that would otherwise be loaded from `~/.codex/config.toml`.
          Use a dotted path (`foo.bar.baz`) to override nested values. The `value` portion is parsed
          as TOML. If it fails to parse as TOML, the raw string is used as a literal.
          
          Examples: - `-c model="o3"` - `-c 'sandbox_permissions=["disk-full-read-access"]'` - `-c
          shell_environment_policy.inherit=all`

      --enable <FEATURE>
          Enable a feature (repeatable). Equivalent to `-c features.<name>=true`

      --disable <FEATURE>
          Disable a feature (repeatable). Equivalent to `-c features.<name>=false`

  -h, --help
          Print help (see a summary with '-h')

 succeeded in 1683ms:
WARNING: proceeding, even though we could not update PATH: Operation not permitted (os error 1)
Install a plugin from a configured marketplace snapshot.

Pass either `PLUGIN@MARKETPLACE` or pass `PLUGIN` with `--marketplace MARKETPLACE`.

Usage: codex plugin add [OPTIONS] <PLUGIN[@MARKETPLACE]>

Arguments:
  <PLUGIN[@MARKETPLACE]>
          Plugin selector to install: either PLUGIN@MARKETPLACE or PLUGIN with --marketplace

Options:
  -c, --config <key=value>
          Override a configuration value that would otherwise be loaded from `~/.codex/config.toml`.
          Use a dotted path (`foo.bar.baz`) to override nested values. The `value` portion is parsed
          as TOML. If it fails to parse as TOML, the raw string is used as a literal.
          
          Examples: - `-c model="o3"` - `-c 'sandbox_permissions=["disk-full-read-access"]'` - `-c
          shell_environment_policy.inherit=all`

  -m, --marketplace <MARKETPLACE>
          Configured marketplace name to use when PLUGIN does not include @MARKETPLACE

      --enable <FEATURE>
          Enable a feature (repeatable). Equivalent to `-c features.<name>=true`

      --disable <FEATURE>
          Disable a feature (repeatable). Equivalent to `-c features.<name>=false`

  -h, --help
          Print help (see a summary with '-h')

Examples:
  codex plugin add sample@debug
  codex plugin add sample --marketplace debug

codex
I’m checking the installed Codex CLI help for the documented update command because a wrong maintenance command would be a concrete docs bug rather than a packaging theory.
hook: PostToolUse
hook: PostToolUse Completed
hook: PostToolUse
hook: PostToolUse Completed
hook: PostToolUse
hook: PostToolUse Completed
codex
The Codex CLI confirms the documented `plugin marketplace upgrade` subcommand exists, so I’m not going to flag that line. The remaining review hinges on stale published README text and whether manual two-manifest versioning is acceptable risk.
hook: PreToolUse
hook: PreToolUse Completed
collab: Wait
hook: PostToolUse
hook: PostToolUse Completed
codex
The architecture lane came back with no blocker. It agrees the model is strong, but flags the in-source README as stale and asks for a required remote Codex smoke gate after push.
hook: PreToolUse
hook: PreToolUse Completed
collab: Wait
hook: PostToolUse
hook: PostToolUse Completed
codex
## BLOCKER (must fix before merge)

None. The source-pointing revision is clean at the merge-blocker level: tracked `packaging/` and `sync.sh` are gone, the repo-root Claude/Codex manifests point at `skills/ai-writing-suite/`, and I did not find a functional double-discovery or missing-body failure in the final tracked state.

## CONCERN (should address)

1. `skills/ai-writing-suite/README.md:137` still documents the old direct-copy install path for Claude/Codex, and `skills/ai-writing-suite/README.md:161` points users to deleted `packaging/`. This needs to change because this README now ships inside the installed source tree, so consumers can land on instructions that contradict the new marketplace layout. Fix: replace that install section with the root marketplace commands from `README.md:36-54`, the Cursor copy path from `README.md:56-67`, and a pointer to `docs/packaging.md`.

2. `CLAUDE.md:24-25` still says Cursor/RovoDev are v2 and “SKILL.md synced to each; do not hand-edit generated packages.” That is now active repo guidance pointing future agents back toward the deleted generate/sync model. Fix: update it to say Claude and Codex install through root marketplace manifests, Cursor copies `skills/ai-writing-suite/`, and there is no generated package body.

3. Hard question: what is the authoritative release version now? `docs/packaging.md:31-32` says bump source `SKILL.md` version if present plus both plugin manifests, but `skills/ai-writing-suite/SKILL.md:1-4` has no version while `skills/ai-writing-suite/.claude-plugin/plugin.json:4` and `skills/ai-writing-suite/.codex-plugin/plugin.json:3` do. Fix: either add `version: 1.0.0` to `SKILL.md` and document parity, or explicitly make the two `plugin.json` files authoritative and add a tiny release check that compares them.

## SUGGESTION (nice to have)

1. Hard question: is remote Codex path resolution a release gate or just a local smoke? `.agents/plugins/marketplace.json:9-11` points to `./skills/ai-writing-suite`; this looks defensible, and I found the same local marketplace shape in an installed Codex plugin cache using a sibling path outside `.agents/plugins`. Still, the only remaining risk is fresh remote resolution after push. Fix: keep `docs/packaging.md:43-44` as a required release gate and record one fresh remote `codex plugin marketplace add surahli123/ai-writing-suite` smoke before tagging.

2. Historical docs still mention `packaging/` / `sync.sh` (`docs/design-ai-writing-suite-v1-2026-06-06.md`, `docs/code-review-v1-2026-06-06.md`). I would not block on these because they are dated design/review records and `docs/packaging.md:8-9` supersedes them. Fix: add a short “superseded by `docs/packaging.md`” note at the top if readers treat those files as operational.

3. Shipping `.claude-plugin`, `.codex-plugin`, and `evals/` inside the source tree is acceptable for v1. The host manifests are namespaced, `evals/` is useful verification material, and this avoids reintroducing a duplicate package body; revisit only if install payload size becomes a real complaint.


hook: Stop
hook: Stop
hook: Stop Completed
hook: Stop Completed
tokens used
115,664
## BLOCKER (must fix before merge)

None. The source-pointing revision is clean at the merge-blocker level: tracked `packaging/` and `sync.sh` are gone, the repo-root Claude/Codex manifests point at `skills/ai-writing-suite/`, and I did not find a functional double-discovery or missing-body failure in the final tracked state.

## CONCERN (should address)

1. `skills/ai-writing-suite/README.md:137` still documents the old direct-copy install path for Claude/Codex, and `skills/ai-writing-suite/README.md:161` points users to deleted `packaging/`. This needs to change because this README now ships inside the installed source tree, so consumers can land on instructions that contradict the new marketplace layout. Fix: replace that install section with the root marketplace commands from `README.md:36-54`, the Cursor copy path from `README.md:56-67`, and a pointer to `docs/packaging.md`.

2. `CLAUDE.md:24-25` still says Cursor/RovoDev are v2 and “SKILL.md synced to each; do not hand-edit generated packages.” That is now active repo guidance pointing future agents back toward the deleted generate/sync model. Fix: update it to say Claude and Codex install through root marketplace manifests, Cursor copies `skills/ai-writing-suite/`, and there is no generated package body.

3. Hard question: what is the authoritative release version now? `docs/packaging.md:31-32` says bump source `SKILL.md` version if present plus both plugin manifests, but `skills/ai-writing-suite/SKILL.md:1-4` has no version while `skills/ai-writing-suite/.claude-plugin/plugin.json:4` and `skills/ai-writing-suite/.codex-plugin/plugin.json:3` do. Fix: either add `version: 1.0.0` to `SKILL.md` and document parity, or explicitly make the two `plugin.json` files authoritative and add a tiny release check that compares them.

## SUGGESTION (nice to have)

1. Hard question: is remote Codex path resolution a release gate or just a local smoke? `.agents/plugins/marketplace.json:9-11` points to `./skills/ai-writing-suite`; this looks defensible, and I found the same local marketplace shape in an installed Codex plugin cache using a sibling path outside `.agents/plugins`. Still, the only remaining risk is fresh remote resolution after push. Fix: keep `docs/packaging.md:43-44` as a required release gate and record one fresh remote `codex plugin marketplace add surahli123/ai-writing-suite` smoke before tagging.

2. Historical docs still mention `packaging/` / `sync.sh` (`docs/design-ai-writing-suite-v1-2026-06-06.md`, `docs/code-review-v1-2026-06-06.md`). I would not block on these because they are dated design/review records and `docs/packaging.md:8-9` supersedes them. Fix: add a short “superseded by `docs/packaging.md`” note at the top if readers treat those files as operational.

3. Shipping `.claude-plugin`, `.codex-plugin`, and `evals/` inside the source tree is acceptable for v1. The host manifests are namespaced, `evals/` is useful verification material, and this avoids reintroducing a duplicate package body; revisit only if install payload size becomes a real complaint.


