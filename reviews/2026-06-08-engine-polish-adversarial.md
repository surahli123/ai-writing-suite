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
session id: 019ea60c-ee2e-7042-a439-3413ab59a76d
--------
user
You are an adversarial code reviewer. SINGLE-PASS, DIRECT. CRITICAL: do NOT invoke any code-review skill, do NOT spawn/delegate to sub-agents — a prior run exhausted its budget that way. Read the files yourself and OUTPUT FINDINGS + VERDICT NOW.

CONTEXT: "Engine-polish" — 5 small instruction/catalog edits to the SHIPPED skill body of the AI Writing Suite (consumer-facing on Claude/Codex/Cursor), distilled from 4 external writing skills. Read the diff at /tmp/engine-polish.diff, then the actual files:
- skills/ai-writing-suite/skills/comms-polish/SKILL.md (edit #1 re-scan step 8.5; #2 frontmatter negative routing)
- skills/ai-writing-suite/skills/voice-onboard/SKILL.md, comms-draft/SKILL.md, comms-qa/SKILL.md (#2 frontmatter routing)
- skills/ai-writing-suite/_shared/patterns/lexical-tells.md (#3 replace-on-sight table mirroring detector/patterns.py TIER1)
- skills/ai-writing-suite/_shared/self-improvement.md (#4 human-gated GRADUATION step)
- skills/ai-writing-suite/skills/comms-polish/references/final-pass-checklist.md (#5 layered gate)
- skills/ai-writing-suite/evals/test_catalog_sync.py (new dev sync-test for #3 drift)
- cross-ref: skills/ai-writing-suite/evals/detector/patterns.py (the TIER1 source dict)

Check and report only REAL defects (file:line + concrete fix):
1. #1: the Rewrite Workflow steps are correctly renumbered after inserting step 8.5 (no duplicate/skipped numbers; the new step is coherent and not contradictory with the existing final-pass-checklist step).
2. #2: every edited frontmatter `description:` is still valid YAML on one line, name+description present, and the negative-routing claims are accurate (e.g. comms-polish really does hand voice work to voice-onboard).
3. #3: the lexical-tells.md table covers EVERY key in patterns.py TIER1 (no missing/renamed word), the swaps match patterns.py, and the provenance note is correct. Does the sync-test actually enforce this (path resolution correct, import works under `unittest discover` from evals/, assertion meaningful not vacuous)?
4. #4: the GRADUATION step does NOT weaken the "never auto-edit the catalog" guarantee — confirm it is human/maintainer-only and the hook gains no autonomous catalog-write power. Any wording a model could misread as license to auto-fold?
5. #5: the layered checklist kept ALL original 13 items (none dropped/altered in meaning), the L1 facts-floor is the original facts-unchanged item, and the added L4 acceptance question is consistent.
6. Any consumer-facing risk: do these change behavior in a way that could harm existing installs, or are they additive/clarifying?
7. CI: these don't touch evals/run_all.sh or ci.yml execution; confirm the new sync-test is stdlib-only and key-free.

OUTPUT NOW:
- Findings, each [BLOCKER]/[CONCERN]/[SUGGESTION] with file:line, problem, concrete fix.
- One-line verdict: SAFE-TO-COMMIT / COMMIT-WITH-FIXES / NEEDS-REWORK.
- End: VERIFIED_AGAINST: feat/engine-polish-distill @ <HEAD-sha> @ <timestamp>

2026-06-08T07:05:27.282439Z ERROR rmcp::transport::worker: worker quit with fatal: Transport channel closed, when AuthRequired(AuthRequiredError { www_authenticate_header: "Bearer realm=\"OAuth\", resource_metadata=\"https://mcp.cloudflare.com/.well-known/oauth-protected-resource/mcp\", error=\"invalid_token\"" })
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
I’ll do this as a single-pass manual review only: diff first, then the listed files and sync test, with the stop condition being concrete findings plus the requested verdict/HEAD/timestamp.
hook: PreToolUse
hook: PreToolUse
hook: PreToolUse
hook: PreToolUse Completed
hook: PreToolUse Completed
hook: PreToolUse Completed
exec
/bin/zsh -lc "sed -n '1,260p' /tmp/engine-polish.diff" in /Users/surahli/Documents/ai-writing-suite
 succeeded in 0ms:
diff --git a/skills/ai-writing-suite/_shared/patterns/lexical-tells.md b/skills/ai-writing-suite/_shared/patterns/lexical-tells.md
index ef1137b..469b71c 100644
--- a/skills/ai-writing-suite/_shared/patterns/lexical-tells.md
+++ b/skills/ai-writing-suite/_shared/patterns/lexical-tells.md
@@ -37,6 +37,60 @@ significant(ly), innovative / innovation, effective(ly), dynamic, scalable,
 compelling, unprecedented, exceptional, remarkable, sophisticated, instrumental,
 world-class / state-of-the-art / best-in-class.
 
+**Replace-on-sight table (Tier 1 → plain swap).** Deterministic suggestions, not guesses —
+reach for these instead of inventing a substitution. This table mirrors
+`evals/detector/patterns.py` `TIER1`; a dev sync-test (`evals/test_catalog_sync.py`) fails
+if the two drift (regenerate from `patterns.py` in v2).
+
+| AI word | Plain swap |
+| --- | --- |
+| delve | explore, dig into, look at |
+| tapestry | describe the actual complexity |
+| paradigm | model, approach, framework |
+| embark | start, begin |
+| beacon | rewrite entirely |
+| robust | strong, reliable, solid |
+| comprehensive | thorough, complete, full |
+| cutting-edge | latest, newest, advanced |
+| pivotal | important, key, critical |
+| underscores | highlights, shows |
+| meticulous | careful, detailed, precise |
+| meticulously | carefully, precisely |
+| seamless | smooth, easy, without friction |
+| seamlessly | smoothly, easily |
+| game-changer | describe what changed |
+| game-changing | describe what changed |
+| utilize | use |
+| nestled | is located, sits |
+| vibrant | describe what makes it active |
+| thriving | growing, active |
+| showcasing | showing, demonstrating |
+| bustling | busy, active |
+| intricate | complex, detailed |
+| intricacies | complexities, details |
+| ever-evolving | changing, growing |
+| enduring | lasting, long-running |
+| daunting | hard, difficult |
+| holistic | complete, full, whole |
+| holistically | completely, fully |
+| actionable | practical, useful, concrete |
+| impactful | effective, significant |
+| learnings | lessons, findings, takeaways |
+| synergy | describe the combined effect |
+| synergies | describe the combined effect |
+| interplay | relationship, connection |
+| commence | start, begin |
+| ascertain | find out, determine |
+| endeavor | effort, attempt, try |
+| symphony | describe the coordination |
+| embrace | adopt, accept, use |
+
+Common Tier-1 phrases: `delve into` → explore / dig into · `landscape` → field / space ·
+`realm` → area / field · `testament to` → shows / proves · `leverage` → use · `deep dive`
+/ `dive into` → look at / examine · `unpack` → explain / break down · `best practices` →
+what works · `in order to` → to · `due to the fact that` → because · `serves as` → is ·
+`boasts` → has.
+
 > The tier idea comes from avoid-ai (adapted from brandonwise/humanizer vocab
 > research). Tiering is what keeps this rule from flattening legitimate prose.
 
diff --git a/skills/ai-writing-suite/_shared/self-improvement.md b/skills/ai-writing-suite/_shared/self-improvement.md
index 08f49e2..e0bd8f7 100644
--- a/skills/ai-writing-suite/_shared/self-improvement.md
+++ b/skills/ai-writing-suite/_shared/self-improvement.md
@@ -94,6 +94,24 @@ Only on an explicit "yes" / "approve" / "add it" from the user:
 If the user says no, or edits the wording, follow their version exactly. Never
 append a rule they did not approve. Never append more than they approved.
 
+### GRADUATION — fold stable rules into the catalog (human-gated, maintainer-run)
+
+`learned-rules.md` is append-only, so its on-start read cost grows with every approved
+rule. Graduation keeps the log small WITHOUT weakening the anti-drift gate:
+
+- **Who:** the maintainer (a human), never this hook autonomously. The hook proposes and
+  appends; it does NOT graduate.
+- **When:** a rule is `status: active`, has proven stable across sessions, and (Layer 3) has
+  passed its eval.
+- **What:** the maintainer folds the rule's substance into the right catalog file
+  (`_shared/patterns/...`) or sub-skill reference by hand — the same way any catalog edit is
+  made — then sets the `learned-rules.md` entry to `status: graduated` (a status edit on its
+  own line, noting where it landed). The rule now lives in the catalog; the log entry is a
+  tombstone, not an active rule the hook re-applies on start.
+- **Why it's safe:** the "never auto-edit the catalog" rule (below) is untouched. Graduation
+  is a deliberate human edit, identical in trust to writing the catalog in the first place.
+  The hook gains no new power — it still only reads on start and proposes on end.
+
 ## What this hook must NEVER do
 
 - Auto-edit core logic (any `SKILL.md`, `_shared/patterns/`, the voice-profile
diff --git a/skills/ai-writing-suite/evals/test_catalog_sync.py b/skills/ai-writing-suite/evals/test_catalog_sync.py
new file mode 100644
index 0000000..8f252af
--- /dev/null
+++ b/skills/ai-writing-suite/evals/test_catalog_sync.py
@@ -0,0 +1,40 @@
+"""Catalog/detector sync test (engine-polish #3 drift guard).
+
+The polish catalog `_shared/patterns/lexical-tells.md` ships a "replace-on-sight"
+table that mirrors the detector's `TIER1` swap dict in `detector/patterns.py`.
+Two copies of the same data drift silently — so this test fails CI if any
+`TIER1` word is missing from the catalog table. Prose provenance notes don't
+catch drift; this does. (v2: generate the table from patterns.py and delete this.)
+
+Stdlib-only, no network. Runs under `run_all.sh` via `unittest discover`.
+"""
+
+import os
+import re
+import unittest
+
+from detector.patterns import TIER1
+
+# This file lives at <skill-root>/evals/test_catalog_sync.py, so the catalog is
+# two levels up: evals/ -> <skill-root> -> _shared/patterns/lexical-tells.md.
+CATALOG = os.path.join(
+    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
+    "_shared", "patterns", "lexical-tells.md")
+
+
+class CatalogSync(unittest.TestCase):
+    def test_catalog_exists(self):
+        self.assertTrue(os.path.exists(CATALOG), f"catalog missing: {CATALOG}")
+
+    def test_every_tier1_word_is_in_the_catalog_table(self):
+        with open(CATALOG, encoding="utf-8") as fh:
+            text = fh.read().lower()
+        missing = [w for w in TIER1 if w.lower() not in text]
+        self.assertEqual(
+            missing, [],
+            f"lexical-tells.md is missing TIER1 swap words {missing} — the "
+            f"catalog table drifted from detector/patterns.py TIER1. Re-sync them.")
+
+
+if __name__ == "__main__":
+    unittest.main()
diff --git a/skills/ai-writing-suite/skills/comms-draft/SKILL.md b/skills/ai-writing-suite/skills/comms-draft/SKILL.md
index 10ee60e..8a8d99c 100644
--- a/skills/ai-writing-suite/skills/comms-draft/SKILL.md
+++ b/skills/ai-writing-suite/skills/comms-draft/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: comms-draft
-description: Draft a new page guided by the knowledge base / playbook. Not yet built - coming in v2.
+description: Draft a new page guided by the knowledge base / playbook. Not yet built - coming in v2. For polishing existing text use comms-polish; for KB Q&A use comms-qa.
 ---
 
 # comms-draft (placeholder)
diff --git a/skills/ai-writing-suite/skills/comms-polish/SKILL.md b/skills/ai-writing-suite/skills/comms-polish/SKILL.md
index bc0d710..7cf4b31 100644
--- a/skills/ai-writing-suite/skills/comms-polish/SKILL.md
+++ b/skills/ai-writing-suite/skills/comms-polish/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: comms-polish
-description: Polish prose that sounds AI-written while preserving meaning, facts, and author voice. Modes - detect, review, rewrite, edit - plus a 0-100 AI-tell score on demand. Use for docs, emails, posts, reports, and user-facing copy; do not use for code cleanup.
+description: Polish prose that sounds AI-written while preserving meaning, facts, and author voice. Modes - detect, review, rewrite, edit - plus a 0-100 AI-tell score on demand. Use for docs, emails, posts, reports, and user-facing copy. Not for code cleanup, and not for learning or extracting an author's voice - that is voice-onboard.
 ---
 
 # comms-polish
@@ -128,8 +128,11 @@ When neither exists, use the lightest voice that fits the context:
 6. Replace vague abstractions with concrete actors, actions, examples, or consequences.
 7. Vary rhythm without adding fake personality. Bias word choice and cadence
    toward the voice profile when one was loaded.
-8. **Run `references/final-pass-checklist.md`** before returning anything.
-9. Return the requested output and mention any claim that still needs evidence.
+8. **Re-scan your rewrite against the pattern catalog** (repeat step 5 on the *output*).
+   Rewriting reintroduces tells — fixing one often plants another. Treat the rewrite as a
+   fresh draft, scan it, and remove any tell you find before the final pass.
+9. **Run `references/final-pass-checklist.md`** before returning anything.
+10. Return the requested output and mention any claim that still needs evidence.
 
 ## Safety Rules
 
diff --git a/skills/ai-writing-suite/skills/comms-polish/references/final-pass-checklist.md b/skills/ai-writing-suite/skills/comms-polish/references/final-pass-checklist.md
index 34012c1..f2f4064 100644
--- a/skills/ai-writing-suite/skills/comms-polish/references/final-pass-checklist.md
+++ b/skills/ai-writing-suite/skills/comms-polish/references/final-pass-checklist.md
@@ -6,7 +6,14 @@ quick read-through that catches the tell you reintroduced while fixing another o
 Adapted from `weijt606/anti-vibe-writing` (`final-pass-checklist.md`, MIT); the
 optional scoring pass is adapted from the `stop-slop` rubric (MIT).
 
-## The checklist
+## The checklist (layered — clear each layer in order)
+
+**L1 — Mechanical floor (non-negotiable).** A single failure here blocks the return, no
+matter how good the prose reads. This layer is never traded off against style.
+
+- **Facts, numbers, technical claims, code, commands, and quotes are unchanged.**
+
+**L2 — Slop removal (style).**
 
 - The opening reaches the point quickly — no runway.
 - The main point appears early.
@@ -22,10 +29,14 @@ optional scoring pass is adapted from the `stop-slop` rubric (MIT).
 - The tone has a point of view instead of manufactured balance.
 - Warmth comes from specificity and cadence, not filler friendliness.
 - The prose sounds written, not assembled.
-- **Facts, numbers, technical claims, code, commands, and quotes are unchanged.**
 - Necessary nuance is carried in the sentence, not bolted on as a hedge.
 - The result is shorter or sharper, not just different.
 
+**L3 — Genre + voice fit.** Run the cross-checks in the next section.
+
+**L4 — Acceptance (one honest question).** *Would a specific, informed human have written
+this?* If no, make another pass before returning.
+
 ## Genre + voice cross-checks
 
 Two checks that depend on the layer above this skill:
diff --git a/skills/ai-writing-suite/skills/comms-qa/SKILL.md b/skills/ai-writing-suite/skills/comms-qa/SKILL.md
index dc05073..3cf475c 100644
--- a/skills/ai-writing-suite/skills/comms-qa/SKILL.md
+++ b/skills/ai-writing-suite/skills/comms-qa/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: comms-qa
-description: Answer questions from the knowledge base via a markdown mini-RAG over the pluggable KB. Not yet built - coming in v2.
+description: Answer questions from the knowledge base via a markdown mini-RAG over the pluggable KB. Not yet built - coming in v2. For polishing existing text use comms-polish; for drafting a new page use comms-draft.
 ---
 
 # comms-qa (placeholder)
diff --git a/skills/ai-writing-suite/skills/voice-onboard/SKILL.md b/skills/ai-writing-suite/skills/voice-onboard/SKILL.md
index b89a19c..1b11e54 100644
--- a/skills/ai-writing-suite/skills/voice-onboard/SKILL.md
+++ b/skills/ai-writing-suite/skills/voice-onboard/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: voice-onboard
-description: Interview an author and distill their historical writing into a reusable voice profile that comms-polish reads for voice matching. Ingests local files or pasted samples, extracts a 10-dimension style fingerprint with sample evidence, and writes _shared/voice-profile.md. Use when the user says "learn my voice", "match how I write", or before a series of posts that must stay on-voice.
+description: Interview an author and distill their historical writing into a reusable voice profile that comms-polish reads for voice matching. Ingests local files or pasted samples, extracts a 10-dimension style fingerprint with sample evidence, and writes _shared/voice-profile.md. Use when the user says "learn my voice", "match how I write", or before a series of posts that must stay on-voice. Not for rewriting or polishing text - that is comms-polish; this skill only profiles.
 ---
 
 # voice-onboard

hook: PostToolUse
exec
/bin/zsh -lc 'git status --short' in /Users/surahli/Documents/ai-writing-suite
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
 M skills/ai-writing-suite/_shared/patterns/lexical-tells.md
 M skills/ai-writing-suite/_shared/self-improvement.md
 A skills/ai-writing-suite/evals/test_catalog_sync.py
 M skills/ai-writing-suite/skills/comms-draft/SKILL.md
 M skills/ai-writing-suite/skills/comms-polish/SKILL.md
 M skills/ai-writing-suite/skills/comms-polish/references/final-pass-checklist.md
 M skills/ai-writing-suite/skills/comms-qa/SKILL.md
 M skills/ai-writing-suite/skills/voice-onboard/SKILL.md
?? docs/handover-2026-06-02-personal-productivity-skills-next.md
?? docs/handover-2026-06-06-ai-writing-suite-v1.md
?? docs/handover-2026-06-06-v1-shipped.md
?? docs/handover-2026-06-07-publish-and-ci.md
?? docs/plan-engine-polish-distill-2026-06-07.html
?? docs/plan-engine-polish-distill-2026-06-07.md
?? docs/plan-phase2-quality-eval-2026-06-07.md
?? docs/plan-publish-cleanup-test-2026-06-07.md
?? docs/proposal-distill-writing-skills-2026-06-07.md
?? docs/session-closeout-2026-06-02-ai-writing-humanizer.md
?? docs/test-plan-v1-2026-06-07.md
?? reviews/

hook: PostToolUse
exec
/bin/zsh -lc "git rev-parse --abbrev-ref HEAD && git rev-parse HEAD && date '+%Y-%m-%dT%H:%M:%S%z'" in /Users/surahli/Documents/ai-writing-suite
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
feat/engine-polish-distill
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
0a4de7fc14def87d92f298c74b3c4601a1fd2355
2026-06-08T00:05:41-0700

hook: PostToolUse
hook: PostToolUse Completed
hook: PostToolUse Completed
hook: PostToolUse Completed
codex
The diff is limited to the requested files, and the branch/HEAD is `feat/engine-polish-distill` at `0a4de7f...`; I’m checking actual line-numbered contents now so findings cite the working tree, not only the patch.
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
exec
/bin/zsh -lc "nl -ba skills/ai-writing-suite/evals/detector/patterns.py | sed -n '1,220p'; nl -ba skills/ai-writing-suite/evals/test_catalog_sync.py | sed -n '1,120p'" in /Users/surahli/Documents/ai-writing-suite
 succeeded in 0ms:
     1	"""Pattern tables + regexes — the executable expression of `_shared/patterns/`.
     2	
     3	WHY a separate data module: keeping the rule *data* apart from the scan *logic*
     4	(detector.py) mirrors how the skill keeps the catalog (`_shared/patterns/`)
     5	apart from the polish prose. When a tell moves in/out of the catalog, only this
     6	file changes. Each block names the catalog category it enforces.
     7	
     8	Ported directly from `avoid-ai-writing/detector/patterns.js` (MIT). Regex
     9	syntax translated JS -> Python `re`; behaviour kept identical. `re.I` = case
    10	insensitive, `re.M` = multiline (`^`/`$` per line).
    11	"""
    12	
    13	import re
    14	
    15	# --- Tier 1: AI vocabulary, replace on sight (catalog L1) -----------------
    16	# Single words. Value = the plain-word suggestion the skill would offer.
    17	TIER1 = {
    18	    "delve": "explore, dig into, look at",
    19	    "tapestry": "describe the actual complexity",
    20	    "paradigm": "model, approach, framework",
    21	    "embark": "start, begin",
    22	    "beacon": "rewrite entirely",
    23	    "robust": "strong, reliable, solid",
    24	    "comprehensive": "thorough, complete, full",
    25	    "cutting-edge": "latest, newest, advanced",
    26	    "pivotal": "important, key, critical",
    27	    "underscores": "highlights, shows",
    28	    "meticulous": "careful, detailed, precise",
    29	    "meticulously": "carefully, precisely",
    30	    "seamless": "smooth, easy, without friction",
    31	    "seamlessly": "smoothly, easily",
    32	    "game-changer": "describe what changed",
    33	    "game-changing": "describe what changed",
    34	    "utilize": "use",
    35	    "nestled": "is located, sits",
    36	    "vibrant": "describe what makes it active",
    37	    "thriving": "growing, active",
    38	    "showcasing": "showing, demonstrating",
    39	    "bustling": "busy, active",
    40	    "intricate": "complex, detailed",
    41	    "intricacies": "complexities, details",
    42	    "ever-evolving": "changing, growing",
    43	    "enduring": "lasting, long-running",
    44	    "daunting": "hard, difficult",
    45	    "holistic": "complete, full, whole",
    46	    "holistically": "completely, fully",
    47	    "actionable": "practical, useful, concrete",
    48	    "impactful": "effective, significant",
    49	    "learnings": "lessons, findings, takeaways",
    50	    "synergy": "describe the combined effect",
    51	    "synergies": "describe the combined effect",
    52	    "interplay": "relationship, connection",
    53	    "commence": "start, begin",
    54	    "ascertain": "find out, determine",
    55	    "endeavor": "effort, attempt, try",
    56	    "symphony": "describe the coordination",
    57	    "embrace": "adopt, accept, use",
    58	}
    59	
    60	# Multi-word Tier 1 phrases. (pattern, suggestion).
    61	TIER1_PHRASES = [
    62	    (re.compile(r"\bdelve\s+into\b", re.I), "explore, dig into"),
    63	    (re.compile(r"\blandscape\b", re.I), "field, space, industry"),
    64	    (re.compile(r"\brealm\b", re.I), "area, field, domain"),
    65	    (re.compile(r"\btestament\s+to\b", re.I), "shows, proves"),
    66	    (re.compile(r"\bleverage\b", re.I), "use"),
    67	    (re.compile(r"\bwatershed\s+moment\b", re.I), "turning point, shift"),
    68	    (re.compile(r"\bdeep\s+dive\b", re.I), "look at, examine"),
    69	    (re.compile(r"\bdive\s+into\b", re.I), "look at, examine"),
    70	    (re.compile(r"\bunpack(?:ing)?\b", re.I), "explain, break down"),
    71	    (re.compile(r"\bthought\s+leader(?:ship)?\b", re.I), "expert, authority"),
    72	    (re.compile(r"\bbest\s+practices\b", re.I), "what works, proven methods"),
    73	    (re.compile(r"\bat\s+its\s+core\b", re.I), "cut, just state it"),
    74	    (re.compile(r"\bin\s+order\s+to\b", re.I), "to"),
    75	    (re.compile(r"\bdue\s+to\s+the\s+fact\s+that\b", re.I), "because"),
    76	    (re.compile(r"\bserves\s+as\b", re.I), "is"),
    77	    (re.compile(r"\bboasts\b", re.I), "has"),
    78	]
    79	
    80	# --- Tier 2: flag in clusters of 2+ per paragraph (catalog L1 tier 2) -----
    81	TIER2 = {
    82	    "harness": "use, take advantage of",
    83	    "navigate": "work through, handle",
    84	    "navigating": "working through, handling",
    85	    "foster": "encourage, support, build",
    86	    "elevate": "improve, raise, strengthen",
    87	    "unleash": "release, enable, unlock",
    88	    "streamline": "simplify, speed up",
    89	    "empower": "enable, let, allow",
    90	    "bolster": "support, strengthen",
    91	    "spearhead": "lead, drive, run",
    92	    "resonate": "connect with, appeal to",
    93	    "resonates": "connects with, appeals to",
    94	    "revolutionize": "change, transform",
    95	    "facilitate": "enable, help, allow",
    96	    "facilitates": "enables, helps, allows",
    97	    "underpin": "support, form the basis of",
    98	    "nuanced": "specific, subtle, detailed",
    99	    "crucial": "important, key, necessary",
   100	    "multifaceted": "describe the actual facets",
   101	    "ecosystem": "system, community, network",
   102	    "myriad": "many, numerous",
   103	    "plethora": "many, a lot of",
   104	    "encompass": "include, cover, span",
   105	    "catalyze": "start, trigger, accelerate",
   106	    "reimagine": "rethink, redesign, rebuild",
   107	    "galvanize": "motivate, rally, push",
   108	    "augment": "add to, expand, supplement",
   109	    "cultivate": "build, develop, grow",
   110	    "illuminate": "clarify, explain, show",
   111	    "elucidate": "explain, clarify",
   112	    "transformative": "describe what changed",
   113	    "transformation": "describe what changed",
   114	    "cornerstone": "foundation, basis, key part",
   115	    "paramount": "most important, top priority",
   116	    "poised": "ready, set, about to",
   117	    "burgeoning": "growing, emerging",
   118	    "nascent": "new, early-stage",
   119	    "quintessential": "typical, classic, defining",
   120	    "overarching": "main, central, broad",
   121	    "underpinning": "basis, foundation",
   122	}
   123	
   124	# --- Tier 3: flag only at high density (catalog L1 tier 3) -----------------
   125	TIER3 = [
   126	    "significant", "significantly", "innovative", "innovation",
   127	    "effective", "effectively", "dynamic", "scalable",
   128	    "compelling", "unprecedented", "exceptional", "remarkable",
   129	    "sophisticated", "instrumental",
   130	    "world-class", "state-of-the-art", "best-in-class",
   131	]
   132	# Lookup tolerant of hyphen-stripped forms ("state-of-the-art" / "stateoftheart").
   133	TIER3_LOOKUP = {}
   134	for _w in TIER3:
   135	    TIER3_LOOKUP[_w] = _w
   136	    _dashless = _w.replace("-", "")
   137	    if _dashless != _w:
   138	        TIER3_LOOKUP[_dashless] = _w
   139	
   140	# Multi-word Tier 3 boilerplate (significance-attribution / consultant-speak).
   141	TIER3_PHRASES = [
   142	    re.compile(r"\bemerging\s+(?:sector|space|category|industry)\b", re.I),
   143	    re.compile(r"\bthe\s+integration\s+of\b", re.I),
   144	    re.compile(r"\bthe\s+intersection\s+of\b", re.I),
   145	    re.compile(r"\bcommunity-?driven\b", re.I),
   146	    re.compile(r"\blong-?term\s+sustainability\b", re.I),
   147	    re.compile(r"\buser\s+engagement\b", re.I),
   148	    re.compile(r"\bdesigned\s+for\s+long-?term\b", re.I),
   149	]
   150	
   151	# --- Phrase-list categories -----------------------------------------------
   152	# Each maps to a catalog category; see CATEGORIES.md for the SKILL <-> type map.
   153	TRANSITIONS = [  # hedging-filler: signposting
   154	    re.compile(r"\bmoreover\b", re.I),
   155	    re.compile(r"\bfurthermore\b", re.I),
   156	    re.compile(r"\badditionally\b", re.I),
   157	    re.compile(r"\bin\s+today'?s\b", re.I),
   158	    re.compile(r"\bin\s+an\s+era\s+where\b", re.I),
   159	    re.compile(r"\bit'?s\s+worth\s+noting\s+that\b", re.I),
   160	    re.compile(r"\bnotably\b", re.I),
   161	    re.compile(r"\bin\s+conclusion\b", re.I),
   162	    re.compile(r"\bin\s+summary\b", re.I),
   163	    re.compile(r"\bwhen\s+it\s+comes\s+to\b", re.I),
   164	    re.compile(r"\bat\s+the\s+end\s+of\s+the\s+day\b", re.I),
   165	    re.compile(r"\bthat\s+(?:being\s+)?said\b", re.I),
   166	]
   167	
   168	CHATBOT_ARTIFACTS = [  # communication-artifacts: chatbot tics
   169	    re.compile(r"\bi\s+hope\s+this\s+helps\b", re.I),
   170	    re.compile(r"\bcertainly!\b", re.I),
   171	    re.compile(r"\babsolutely!\b", re.I),
   172	    re.compile(r"\bgreat\s+question!\b", re.I),
   173	    re.compile(r"\bfeel\s+free\s+to\s+reach\s+out\b", re.I),
   174	    re.compile(r"\blet\s+me\s+know\s+if\s+you\s+need\s+anything\b", re.I),
   175	    re.compile(r"\bin\s+this\s+article,?\s+we\s+will\s+explore\b", re.I),
   176	    re.compile(r"\blet'?s\s+dive\s+in!?\b", re.I),
   177	]
   178	
   179	SYCOPHANTIC = [  # communication-artifacts: sycophancy
   180	    re.compile(r"\byou'?re\s+absolutely\s+right\b", re.I),
   181	    re.compile(r"\bthat'?s\s+a\s+really\s+insightful\b", re.I),
   182	    re.compile(r"\bthat'?s\s+a\s+great\s+question\b", re.I),
   183	    re.compile(r"\bexcellent\s+question\b", re.I),
   184	]
   185	
   186	FILLERS = [  # hedging-filler: filler phrases
   187	    re.compile(r"\bit\s+is\s+important\s+to\s+note\s+that\b", re.I),
   188	    re.compile(r"\bin\s+terms\s+of\b", re.I),
   189	    re.compile(r"\bthe\s+reality\s+is\s+that\b", re.I),
   190	    re.compile(r"\bit'?s\s+important\s+to\s+note\s+that\b", re.I),
   191	]
   192	
   193	GENERIC_CONCLUSIONS = [  # hedging-filler: generic conclusions
   194	    re.compile(r"\bthe\s+future\s+looks\s+bright\b", re.I),
   195	    re.compile(r"\bonly\s+time\s+will\s+tell\b", re.I),
   196	    re.compile(r"\bone\s+thing\s+is\s+certain\b", re.I),
   197	    re.compile(r"\bas\s+we\s+move\s+forward\b", re.I),
   198	]
   199	
   200	LETS_PATTERNS = [  # hedging-filler: "let's" openers
   201	    re.compile(r"\blet'?s\s+explore\b", re.I),
   202	    re.compile(r"\blet'?s\s+take\s+a\s+look\b", re.I),
   203	    re.compile(r"\blet'?s\s+break\s+this\s+down\b", re.I),
   204	    re.compile(r"\blet'?s\s+examine\b", re.I),
   205	    re.compile(r"\blet'?s\s+(?:consider|discuss|delve|unpack|walk\s+through)\b", re.I),
   206	]
   207	
   208	REASONING_ARTIFACTS = [  # communication-artifacts: reasoning-chain leaks
   209	    re.compile(r"\blet\s+me\s+think\s+step\s+by\s+step\b", re.I),
   210	    re.compile(r"\bbreaking\s+this\s+down\b", re.I),
   211	    re.compile(r"\bto\s+approach\s+this\s+systematically\b", re.I),
   212	    re.compile(r"\bhere'?s\s+my\s+thought\s+process\b", re.I),
   213	    re.compile(r"\bfirst,?\s+let'?s\s+consider\b", re.I),
   214	    re.compile(r"\bworking\s+through\s+this\s+logically\b", re.I),
   215	]
   216	
   217	ACKNOWLEDGMENT_LOOPS = [  # communication-artifacts: acknowledgment loops
   218	    re.compile(r"\byou'?re\s+asking\s+about\b", re.I),
   219	    re.compile(r"\bthe\s+question\s+of\s+whether\b", re.I),
   220	    re.compile(r"\bto\s+answer\s+your\s+question\b", re.I),
     1	"""Catalog/detector sync test (engine-polish #3 drift guard).
     2	
     3	The polish catalog `_shared/patterns/lexical-tells.md` ships a "replace-on-sight"
     4	table that mirrors the detector's `TIER1` swap dict in `detector/patterns.py`.
     5	Two copies of the same data drift silently — so this test fails CI if any
     6	`TIER1` word is missing from the catalog table. Prose provenance notes don't
     7	catch drift; this does. (v2: generate the table from patterns.py and delete this.)
     8	
     9	Stdlib-only, no network. Runs under `run_all.sh` via `unittest discover`.
    10	"""
    11	
    12	import os
    13	import re
    14	import unittest
    15	
    16	from detector.patterns import TIER1
    17	
    18	# This file lives at <skill-root>/evals/test_catalog_sync.py, so the catalog is
    19	# two levels up: evals/ -> <skill-root> -> _shared/patterns/lexical-tells.md.
    20	CATALOG = os.path.join(
    21	    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    22	    "_shared", "patterns", "lexical-tells.md")
    23	
    24	
    25	class CatalogSync(unittest.TestCase):
    26	    def test_catalog_exists(self):
    27	        self.assertTrue(os.path.exists(CATALOG), f"catalog missing: {CATALOG}")
    28	
    29	    def test_every_tier1_word_is_in_the_catalog_table(self):
    30	        with open(CATALOG, encoding="utf-8") as fh:
    31	            text = fh.read().lower()
    32	        missing = [w for w in TIER1 if w.lower() not in text]
    33	        self.assertEqual(
    34	            missing, [],
    35	            f"lexical-tells.md is missing TIER1 swap words {missing} — the "
    36	            f"catalog table drifted from detector/patterns.py TIER1. Re-sync them.")
    37	
    38	
    39	if __name__ == "__main__":
    40	    unittest.main()

hook: PostToolUse
exec
/bin/zsh -lc "nl -ba skills/ai-writing-suite/_shared/patterns/lexical-tells.md | sed -n '1,140p'" in /Users/surahli/Documents/ai-writing-suite
 succeeded in 0ms:
     1	# Lexical Tells (word-level)
     2	
     3	Word- and phrase-level habits. These are the easiest to spot and the easiest to
     4	over-correct, so flag in clusters, not in isolation: one "however" is nothing; a
     5	paragraph of delve + leverage + robust + tapestry is a confession.
     6	
     7	---
     8	
     9	### L1 — AI vocabulary words (tiered)
    10	
    11	- **Tell:** A small set of words appears 5-20x more often in post-2023 model
    12	  output than in human prose, and tends to cluster.
    13	- **Fix:** Replace with the plain word. Flag by tier, not on sight, to cut
    14	  false positives on second-language and technical writing.
    15	- **Sources:** avoid-ai (tiered table), blader (P7), aboudjem (§7), stop-slop.
    16	
    17	**Tier 1 — replace on sight** (appears ~5-20x more in AI text):
    18	delve / delve into, landscape (metaphor), tapestry, realm, paradigm, embark,
    19	beacon, testament to, robust, comprehensive, cutting-edge, leverage (verb),
    20	pivotal, underscores, meticulous, seamless, game-changer, utilize, nestled,
    21	vibrant, thriving, showcasing, deep dive / dive into, unpack, bustling,
    22	intricate / intricacies, ever-evolving, enduring, daunting, holistic,
    23	actionable, impactful, learnings, thought leader, best practices, at its core,
    24	synergy, interplay, in order to, due to the fact that, serves as, features
    25	(verb), boasts, commence, ascertain, endeavor, embrace (metaphor).
    26	
    27	**Tier 2 — flag when 2+ appear in one paragraph** (fine alone, suspect together):
    28	harness, navigate / navigating, foster, elevate, unleash, streamline, empower,
    29	bolster, spearhead, resonate, revolutionize, facilitate, underpin, nuanced,
    30	crucial, multifaceted, ecosystem (metaphor), myriad, plethora, encompass,
    31	catalyze, reimagine, galvanize, augment, cultivate, illuminate, elucidate,
    32	juxtapose, transformative, cornerstone, paramount, poised, burgeoning, nascent,
    33	quintessential, overarching, underpinning.
    34	
    35	**Tier 3 — flag only at high density** (normal words AI just overuses):
    36	significant(ly), innovative / innovation, effective(ly), dynamic, scalable,
    37	compelling, unprecedented, exceptional, remarkable, sophisticated, instrumental,
    38	world-class / state-of-the-art / best-in-class.
    39	
    40	**Replace-on-sight table (Tier 1 → plain swap).** Deterministic suggestions, not guesses —
    41	reach for these instead of inventing a substitution. This table mirrors
    42	`evals/detector/patterns.py` `TIER1`; a dev sync-test (`evals/test_catalog_sync.py`) fails
    43	if the two drift (regenerate from `patterns.py` in v2).
    44	
    45	| AI word | Plain swap |
    46	| --- | --- |
    47	| delve | explore, dig into, look at |
    48	| tapestry | describe the actual complexity |
    49	| paradigm | model, approach, framework |
    50	| embark | start, begin |
    51	| beacon | rewrite entirely |
    52	| robust | strong, reliable, solid |
    53	| comprehensive | thorough, complete, full |
    54	| cutting-edge | latest, newest, advanced |
    55	| pivotal | important, key, critical |
    56	| underscores | highlights, shows |
    57	| meticulous | careful, detailed, precise |
    58	| meticulously | carefully, precisely |
    59	| seamless | smooth, easy, without friction |
    60	| seamlessly | smoothly, easily |
    61	| game-changer | describe what changed |
    62	| game-changing | describe what changed |
    63	| utilize | use |
    64	| nestled | is located, sits |
    65	| vibrant | describe what makes it active |
    66	| thriving | growing, active |
    67	| showcasing | showing, demonstrating |
    68	| bustling | busy, active |
    69	| intricate | complex, detailed |
    70	| intricacies | complexities, details |
    71	| ever-evolving | changing, growing |
    72	| enduring | lasting, long-running |
    73	| daunting | hard, difficult |
    74	| holistic | complete, full, whole |
    75	| holistically | completely, fully |
    76	| actionable | practical, useful, concrete |
    77	| impactful | effective, significant |
    78	| learnings | lessons, findings, takeaways |
    79	| synergy | describe the combined effect |
    80	| synergies | describe the combined effect |
    81	| interplay | relationship, connection |
    82	| commence | start, begin |
    83	| ascertain | find out, determine |
    84	| endeavor | effort, attempt, try |
    85	| symphony | describe the coordination |
    86	| embrace | adopt, accept, use |
    87	
    88	Common Tier-1 phrases: `delve into` → explore / dig into · `landscape` → field / space ·
    89	`realm` → area / field · `testament to` → shows / proves · `leverage` → use · `deep dive`
    90	/ `dive into` → look at / examine · `unpack` → explain / break down · `best practices` →
    91	what works · `in order to` → to · `due to the fact that` → because · `serves as` → is ·
    92	`boasts` → has.
    93	
    94	> The tier idea comes from avoid-ai (adapted from brandonwise/humanizer vocab
    95	> research). Tiering is what keeps this rule from flattening legitimate prose.
    96	
    97	---
    98	
    99	### L2 — Copula avoidance
   100	
   101	- **Tell:** The model dodges plain "is" / "are" / "has" with fancier verbs to
   102	  sound sophisticated: serves as, stands as, marks, represents, boasts,
   103	  features, offers, presents.
   104	- **Fix:** Use the copula. "Gallery 825 *is* the exhibition space," not "Gallery
   105	  825 *serves as* the exhibition space." Only keep the fancier verb if it adds
   106	  real meaning.
   107	- **Sources:** blader (P8), aboudjem (§8), avoid-ai, anti-vibe.
   108	
   109	---
   110	
   111	### L3 — Synonym / noun-phrase cycling (elegant variation)
   112	
   113	- **Tell:** Repetition-penalty training makes models rename the same thing to
   114	  avoid repeating a word: "the protagonist… the main character… the central
   115	  figure… the hero," or whole noun phrases: "the artist… the non-conformist
   116	  painter… the visionary creator."
   117	- **Fix:** Pick the clearest term and repeat it. Humans repeat words; repetition
   118	  reads as precision, not poverty.
   119	- **Sources:** blader (P11 word-level + P31 noun-phrase), aboudjem (§11),
   120	  avoid-ai, anti-vibe.
   121	
   122	> blader split this into two ids (word-level P11 vs noun-phrase P31). Merged
   123	> here because the fix is identical; the distinction is noted for lineage only.
   124	
   125	---
   126	
   127	### L4 — False ranges
   128	
   129	- **Tell:** "From X to Y" where X and Y are not on a real spectrum, faking
   130	  breadth: "from the Big Bang to dark matter," "from onboarding to billing."
   131	- **Fix:** List the actual items, or pick the one that matters. Don't fake a
   132	  range.
   133	- **Sources:** blader (P12), aboudjem (§12), avoid-ai, anti-vibe.
   134	
   135	---
   136	
   137	### L5 — Hyphenated-pair overuse
   138	
   139	- **Tell:** Two problems. (a) Density: stacking compound modifiers on one noun
   140	  ("a high-quality, well-architected, future-proof solution"). (b) The

hook: PostToolUse
exec
/bin/zsh -lc "nl -ba skills/ai-writing-suite/skills/comms-polish/SKILL.md | sed -n '1,175p'" in /Users/surahli/Documents/ai-writing-suite
exec
/bin/zsh -lc "nl -ba skills/ai-writing-suite/skills/voice-onboard/SKILL.md | sed -n '1,80p'; nl -ba skills/ai-writing-suite/skills/comms-draft/SKILL.md | sed -n '1,80p'; nl -ba skills/ai-writing-suite/skills/comms-qa/SKILL.md | sed -n '1,80p'" in /Users/surahli/Documents/ai-writing-suite
 succeeded in 0ms:
     1	---
     2	name: comms-polish
     3	description: Polish prose that sounds AI-written while preserving meaning, facts, and author voice. Modes - detect, review, rewrite, edit - plus a 0-100 AI-tell score on demand. Use for docs, emails, posts, reports, and user-facing copy. Not for code cleanup, and not for learning or extracting an author's voice - that is voice-onboard.
     4	---
     5	
     6	# comms-polish
     7	
     8	Remove AI-shaped prose without turning the text into generic rewriting.
     9	
    10	The job is narrow: preserve meaning, remove slop, keep the author's voice.
    11	
    12	This is the suite's polish capability (formerly the standalone humanizer). It
    13	does not carry its own pattern list — it reads the consolidated catalog under
    14	`../../_shared/patterns/`, which is the single source of truth for AI tells.
    15	
    16	Three enrichments sit alongside the catalog:
    17	
    18	- `references/scenario-presets.md` — per-genre weighting (tweet / LinkedIn /
    19	  README / memo): which tells matter most here, target tone/length, what to leave
    20	  alone.
    21	- `references/final-pass-checklist.md` — the pre-ship sweep run before returning
    22	  any rewrite.
    23	- `../../_shared/voice-profile.md` — the user's learned voice, read when present
    24	  so rewrites bias toward how *they* write (see Voice Matching).
    25	
    26	## Pattern catalog
    27	
    28	Before scanning or rewriting, load the consolidated catalog. Read the index first
    29	to see what's where, then the category files relevant to the draft:
    30	
    31	- `../../_shared/patterns/00-index.md` — index + how to read entries
    32	- `lexical-tells.md` — AI vocabulary (tiered), copula avoidance, synonym cycling, false ranges, hyphen pairs, hollow intensifiers
    33	- `significance-attribution.md` — significance/novelty inflation, vague attribution, name-dropping, promotional language, superficial -ing, speculative gap-filling, consultant-speak
    34	- `structural-tells.md` — rule of three, negative parallelism, formulaic challenges, over-structure, inline-header lists, reshuffle immunity, treadmill effect
    35	- `hedging-filler.md` — filler, stacked hedging, generic/future-narrative closers, confidence-calibration phrases, signposting
    36	- `punctuation-formatting.md` — em dashes, bold overuse, emoji headers, curly quotes, title case, hashtag stuffing, placeholders, citation/UTM fingerprints
    37	- `communication-artifacts.md` — chatbot tics, sycophancy, acknowledgment loops, cutoff disclaimers, reasoning-chain leaks, engagement hooks, emotional flatline
    38	- `rhythm-stylometric.md` — sentence/paragraph uniformity (burstiness), low TTR, perplexity, register shift, **and the what-NOT-to-flag guardrails**
    39	
    40	Always apply the guardrails in `rhythm-stylometric.md`: look for clusters, not
    41	isolated tells. These are signals, not proof.
    42	
    43	The catalog is the rule source. The local references decide *how* to apply it:
    44	
    45	- `references/scenario-presets.md` — weights catalog categories per genre.
    46	- `references/final-pass-checklist.md` — the pre-ship sweep.
    47	
    48	## Boundary
    49	
    50	This skill edits prose, not code.
    51	
    52	- Use for: README prose, docs, emails, reports, posts, launch notes, UX copy, and narrative summaries.
    53	- Do not use for: source-code cleanup, architecture simplification, test rewriting, or changing program behavior.
    54	- Preserve: facts, citations, numbers, file paths, commands, API names, quoted text, and claims unless the user explicitly asks to change them.
    55	- Flag unsupported claims instead of inventing evidence.
    56	
    57	## Modes
    58	
    59	Pick the mode from the user's request. If unclear, use `rewrite`.
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
    96	- tolerance for humor, warmth, bluntness, or personality
    97	- preferred terms and phrases
    98	
    99	When neither exists, use the lightest voice that fits the context:
   100	
   101	- `technical`: precise, compact, no hype
   102	- `professional`: clear, measured, low-drama
   103	- `warm`: supportive and direct
   104	- `casual`: conversational, with contractions
   105	- `blunt`: shortest viable version
   106	
   107	## Rewrite Workflow
   108	
   109	1. Identify the audience, purpose, and required structure.
   110	2. **Pick the genre preset.** Match the draft to a preset in
   111	   `references/scenario-presets.md` (tweet / LinkedIn / README / memo). It tells
   112	   you which catalog categories to weight harder and what to leave alone in this
   113	   genre. If no preset fits, scan the catalog evenly.
   114	3. **Load the voice profile if present.** Check for `../../_shared/voice-profile.md`
   115	   and read it if it exists; otherwise use a pasted sample or inferred voice
   116	   (see Voice Matching). Degrade gracefully when absent.
   117	4. Mark the factual anchors that must survive unchanged.
   118	5. Scan against the pattern catalog, weighted by the preset, and remove the tells
   119	   you find:
   120	   - throat-clearing and filler
   121	   - inflated significance
   122	   - vague attribution
   123	   - promotional adjectives
   124	   - forced three-item lists
   125	   - "not X but Y" theatrics
   126	   - uniform sentence length
   127	   - chatbot artifacts
   128	6. Replace vague abstractions with concrete actors, actions, examples, or consequences.
   129	7. Vary rhythm without adding fake personality. Bias word choice and cadence
   130	   toward the voice profile when one was loaded.
   131	8. **Re-scan your rewrite against the pattern catalog** (repeat step 5 on the *output*).
   132	   Rewriting reintroduces tells — fixing one often plants another. Treat the rewrite as a
   133	   fresh draft, scan it, and remove any tell you find before the final pass.
   134	9. **Run `references/final-pass-checklist.md`** before returning anything.
   135	10. Return the requested output and mention any claim that still needs evidence.
   136	
   137	## Safety Rules
   138	
   139	- Do not change the author's position to make the prose smoother.
   140	- Do not add examples, numbers, citations, or claims that were not present.
   141	- Do not remove caveats that carry real uncertainty.
   142	- Do not polish away legal, medical, financial, or safety warnings.
   143	- Do not rewrite quoted text unless the user asks.
   144	
   145	## Before And After Examples
   146	
   147	### Technical docs
   148	
   149	Before:
   150	
   151	```text
   152	This robust workflow enables teams to seamlessly leverage contextual insights, ensuring a more effective and streamlined development experience.
   153	```
   154	
   155	After:
   156	
   157	```text
   158	This workflow gives teams the context they need before they start editing.
   159	```
   160	
   161	### Status update
   162	
   163	Before:
   164	
   165	```text
   166	It is important to note that the migration represents a pivotal step toward improving reliability, scalability, and operational efficiency.
   167	```
   168	
   169	After:
   170	
   171	```text
   172	The migration removes the retry job that caused last week's duplicate sends.
   173	```
   174	
   175	### Personal note

 succeeded in 0ms:
     1	---
     2	name: voice-onboard
     3	description: Interview an author and distill their historical writing into a reusable voice profile that comms-polish reads for voice matching. Ingests local files or pasted samples, extracts a 10-dimension style fingerprint with sample evidence, and writes _shared/voice-profile.md. Use when the user says "learn my voice", "match how I write", or before a series of posts that must stay on-voice. Not for rewriting or polishing text - that is comms-polish; this skill only profiles.
     4	---
     5	
     6	# voice-onboard
     7	
     8	Learn how *you* write, so the rest of the suite stops sounding like a clean
     9	generic robot and starts sounding like you.
    10	
    11	The job is narrow: read your real writing, distill a **voice profile**, and write
    12	it to a file the polish skill reads on every run. This skill does NOT draft or
    13	rewrite anything — it only listens and profiles.
    14	
    15	## The mental model (for a product-owner learner)
    16	
    17	Think of it like building a feature table for a ranking model:
    18	
    19	- Your **writing samples** = raw training data.
    20	- The **10 style dimensions** below = the feature schema.
    21	- **`_shared/voice-profile.md`** = the published feature table.
    22	- **`comms-polish`** = the model that reads that table at serving time.
    23	
    24	If the table is empty or guessed, the model falls back to a generic baseline.
    25	So the whole point of this skill is: produce an honest, evidence-backed table.
    26	
    27	## What you read and write
    28	
    29	- **Reads (your samples):** local markdown/text files you point to, or text you
    30	  paste inline. (A Confluence-page link as a voice source is **v2** — note it to
    31	  the user, do not attempt to fetch it. No programmatic ingestion in v1.)
    32	- **Fills in:** `../../_shared/host-profile-template.md` (the blank form).
    33	- **Writes:** `../../_shared/voice-profile.md` (the contract file). The field
    34	  names there are stable — keep every `## H2` header, because `comms-polish`
    35	  reads by header. Renaming a header silently breaks voice matching.
    36	
    37	## How to run it (walk the user through, keep them in control)
    38	
    39	This is a guided, human-gated flow. Do one step, show the result, wait. Never
    40	batch the whole thing and dump a finished profile — the user is the owner of
    41	their own voice and must confirm each judgment.
    42	
    43	### Step 1 — Gather samples
    44	
    45	Ask the user for samples. State plainly what makes a good sample:
    46	
    47	- **3 minimum, 5-10 ideal.** Fewer than 3 → tell them confidence will be Low and
    48	  the profile will be conservative. Don't force-extract from thin data.
    49	- **Same genre as the target.** Learning their LinkedIn voice → ask for LinkedIn
    50	  posts, not academic papers. Mixed genres → offer to extract two profiles
    51	  rather than averaging them into a blur.
    52	- **Their own words, not AI-polished.** A draft Claude already cleaned teaches
    53	  the clean robot's voice, not theirs.
    54	- **Recent (last ~6 months).** Voice drifts; recent samples track current style.
    55	
    56	How they can hand samples over:
    57	
    58	- Point to local files ("read everything in `~/writing/`") — you read them.
    59	- Paste text inline, separated by `---`.
    60	
    61	Confirm what you received before extracting: "Got 6 samples — 4 blog posts,
    62	2 memos. That's Medium confidence. Want me to extract now, or add more first?"
    63	
    64	### Step 2 — Extract the style fingerprint
    65	
    66	Profile each of the 10 dimensions below. **Every claim needs evidence from the
    67	samples.** No evidence → write "Unknown — not enough signal", never invent.
    68	
    69	A trait counts only if it appears **3+ times**. One occurrence is noise. This is
    70	the single most common extraction mistake — learning an accident as a habit.
    71	
    72	The 10 dimensions (these map 1:1 to the `voice-profile.md` headers):
    73	
    74	1. **Tone** — overall register (direct / warm / dry / formal).
    75	2. **Sentence Length** — average words/sentence, short vs long share, rhythm habit.
    76	3. **Vocabulary** — first-person usage, signature words, tics, domain terms.
    77	4. **Vocabulary Do** — constructions they actively reach for.
    78	5. **Vocabulary Don't** — common words they NEVER use. *Strongest signal* — a
    79	   word someone never writes ("delve", "leverage") is more diagnostic than one
    80	   they use often. Mine the absences.
     1	---
     2	name: comms-draft
     3	description: Draft a new page guided by the knowledge base / playbook. Not yet built - coming in v2. For polishing existing text use comms-polish; for KB Q&A use comms-qa.
     4	---
     5	
     6	# comms-draft (placeholder)
     7	
     8	This sub-skill will draft a new page guided by the knowledge base under
     9	`_shared/knowledge/` -- using the playbook's structure, terminology, and best
    10	practices to scaffold a first draft, which `comms-polish` can then finish.
    11	**Coming in v2.** Depends on the KB seed and `comms-qa` retrieval, which are
    12	later layers.
     1	---
     2	name: comms-qa
     3	description: Answer questions from the knowledge base via a markdown mini-RAG over the pluggable KB. Not yet built - coming in v2. For polishing existing text use comms-polish; for drafting a new page use comms-draft.
     4	---
     5	
     6	# comms-qa (placeholder)
     7	
     8	This sub-skill will answer questions from the knowledge base under
     9	`_shared/knowledge/` -- a zero-dependency mini-RAG that navigates a markdown KB
    10	through its `INDEX.md` and returns the relevant passage. In the open-source build
    11	the KB is generic best practices; a company fork drops its own playbook into the
    12	same slot. The KB slot is already seeded in this build (5 generic entries +
    13	`INDEX.md` + a verified retrieval smoke path); the full question-answering
    14	sub-skill that wraps it is **coming in v2.**

hook: PostToolUse
hook: PostToolUse
exec
/bin/zsh -lc "nl -ba skills/ai-writing-suite/_shared/self-improvement.md | sed -n '1,155p'; nl -ba skills/ai-writing-suite/skills/comms-polish/references/final-pass-checklist.md | sed -n '1,120p'" in /Users/surahli/Documents/ai-writing-suite
 succeeded in 0ms:
     1	<!--
     2	================================================================================
     3	  self-improvement.md  —  HUMAN-GATED SELF-IMPROVEMENT PROTOCOL (Layer 2)
     4	================================================================================
     5	
     6	  WHAT THIS IS
     7	  ------------
     8	  The suite-wide lifecycle hook that lets the skills get *better over time*
     9	  WITHOUT silently rewriting themselves. It is referenced (not copied) by every
    10	  sub-skill that opts in — in v1 that is `comms-polish` and `voice-onboard`.
    11	
    12	  THE ONE RULE (read this before anything else)
    13	  ---------------------------------------------
    14	  This hook may only ever do TWO things autonomously:
    15	    1. READ side files at the start of a session (voice-profile + learned-rules).
    16	    2. PROPOSE candidate rules at the end of a session.
    17	  It MUST NOT write anything until the user explicitly approves. Approved rules
    18	  go to ONE place: `learned-rules.md` (append-only). Core SKILL.md logic is NEVER
    19	  auto-edited. This is the anti-drift guarantee — see plan §6 (D6) and risk R3.
    20	
    21	  WHY (product-owner framing)
    22	  ---------------------------
    23	  Treat learned rules like a feature flag rollout, not a model that retrains
    24	  itself on its own outputs. An ungated self-improving system feeds on its own
    25	  predictions and drifts — the writing equivalent of a recommender that keeps
    26	  recommending what it already recommended. The human gate is the holdout check:
    27	  no rule ships to the "production" rule set until a person signs off, and (in
    28	  Layer 3) until an eval measures it.
    29	================================================================================
    30	-->
    31	
    32	# Self-Improvement Protocol (human-gated, append-only)
    33	
    34	This is the shared spec for the suite's self-improvement hook. Sub-skills point
    35	here instead of restating it, so the gate behaves identically everywhere.
    36	
    37	## The contract in one line
    38	
    39	Read learned rules on start. Propose new ones on end. Append only what the
    40	user explicitly approves. Never auto-edit core skill logic.
    41	
    42	## Lifecycle
    43	
    44	### ON START — read the side files (no writes)
    45	
    46	Before doing the sub-skill's actual work, read these two files if they exist:
    47	
    48	1. `_shared/voice-profile.md` — the learned voice (owned by `voice-onboard`).
    49	2. `_shared/learned-rules.md` — approved, human-gated improvements (this file's
    50	   sibling). Apply any rule whose `status: active` and whose scope matches the
    51	   current task (e.g. a rule scoped to `comms-polish` is ignored by
    52	   `voice-onboard`).
    53	
    54	Degrade gracefully: if either file is missing, do not error and do not block.
    55	Note briefly that it was absent and continue with defaults. These are bias
    56	signals, never hard dependencies (same posture as comms-polish voice matching).
    57	
    58	### ON END — propose candidate rule(s), then STOP
    59	
    60	After completing the session's work, look back at what happened and ask: *did a
    61	repeatable correction surface that the catalog / profile / checklist does not
    62	already cover?* Good candidates come from:
    63	
    64	- A correction the user made that would recur ("I always cut that opener").
    65	- A pattern the existing catalog missed or over-flagged.
    66	- A voice-extraction judgment the user overrode.
    67	
    68	If nothing repeatable surfaced, say so and propose nothing. Do not manufacture a
    69	rule to look productive — a noisy rule log is worse than a short one.
    70	
    71	If a candidate exists, **present it to the user** in the proposed-rule shape
    72	(see `learned-rules.md` for the field schema) with:
    73	
    74	- the proposed rule text,
    75	- a one-line rationale grounded in *this* session (cite what happened),
    76	- the scope it would apply to (`comms-polish`, `voice-onboard`, or `all`),
    77	- a note that in Layer 3 this rule will be eval-measured before it counts as
    78	  trusted (do not build or run that eval here — just reference it).
    79	
    80	Then **stop and wait.** This is the gate.
    81	
    82	### ON APPROVAL — append, nothing else
    83	
    84	Only on an explicit "yes" / "approve" / "add it" from the user:
    85	
    86	- Append ONE entry to `_shared/learned-rules.md` using the documented format
    87	  (id, rule, rationale, scope, date, status, source).
    88	- Set `status: proposed` until Layer 3's eval has measured it; the user may say
    89	  "make it active" to promote a rule they trust without waiting.
    90	- Stamp the date and a short source-session note so the log stays auditable.
    91	- Do NOT touch any SKILL.md, the pattern catalog, or the voice profile schema.
    92	  Approved rules live ONLY in `learned-rules.md`.
    93	
    94	If the user says no, or edits the wording, follow their version exactly. Never
    95	append a rule they did not approve. Never append more than they approved.
    96	
    97	### GRADUATION — fold stable rules into the catalog (human-gated, maintainer-run)
    98	
    99	`learned-rules.md` is append-only, so its on-start read cost grows with every approved
   100	rule. Graduation keeps the log small WITHOUT weakening the anti-drift gate:
   101	
   102	- **Who:** the maintainer (a human), never this hook autonomously. The hook proposes and
   103	  appends; it does NOT graduate.
   104	- **When:** a rule is `status: active`, has proven stable across sessions, and (Layer 3) has
   105	  passed its eval.
   106	- **What:** the maintainer folds the rule's substance into the right catalog file
   107	  (`_shared/patterns/...`) or sub-skill reference by hand — the same way any catalog edit is
   108	  made — then sets the `learned-rules.md` entry to `status: graduated` (a status edit on its
   109	  own line, noting where it landed). The rule now lives in the catalog; the log entry is a
   110	  tombstone, not an active rule the hook re-applies on start.
   111	- **Why it's safe:** the "never auto-edit the catalog" rule (below) is untouched. Graduation
   112	  is a deliberate human edit, identical in trust to writing the catalog in the first place.
   113	  The hook gains no new power — it still only reads on start and proposes on end.
   114	
   115	## What this hook must NEVER do
   116	
   117	- Auto-edit core logic (any `SKILL.md`, `_shared/patterns/`, the voice-profile
   118	  schema headers). Out of bounds, always.
   119	- Append a rule without explicit approval.
   120	- Silently overwrite or rewrite existing learned rules — the log is append-only.
   121	  Superseding a rule = append a new entry that references the old id and set the
   122	  old one's `status: retired` (a status edit on its own line, not a rewrite of
   123	  its rule text).
   124	
   125	## Degradation on RovoDev (and other constrained hosts) — R2
   126	
   127	RovoDev has no skill auto-triggering and a reduced toolset (Read/Write/Edit/
   128	Bash/Grep, no Skill tool). This protocol is built to survive that:
   129	
   130	- **No auto-trigger needed.** The hook is plain instructions inside a SKILL.md,
   131	  not an event listener. ON START / ON END run whenever the sub-skill runs,
   132	  however the sub-skill was invoked (explicit invocation on RovoDev).
   133	- **File-read only on start.** Reading `voice-profile.md` + `learned-rules.md`
   134	  uses Read/Grep — available everywhere. No MCP, no special tooling.
   135	- **Append uses Edit/Write.** Adding one entry to `learned-rules.md` needs only
   136	  Edit (or Write) — both present on RovoDev.
   137	- **The gate is conversational, not tool-based.** "Propose → user says yes →
   138	  append" works in any chat loop and needs no Skill/Task/Agent machinery.
   139	- If even file writes are unavailable, degrade to: print the proposed rule entry
   140	  and ask the user to paste it into `learned-rules.md` themselves. The gate and
   141	  the append-only discipline still hold.
     1	# Final-Pass Checklist
     2	
     3	Run this before returning any rewritten or edited copy. It's the last gate — the
     4	quick read-through that catches the tell you reintroduced while fixing another one.
     5	
     6	Adapted from `weijt606/anti-vibe-writing` (`final-pass-checklist.md`, MIT); the
     7	optional scoring pass is adapted from the `stop-slop` rubric (MIT).
     8	
     9	## The checklist (layered — clear each layer in order)
    10	
    11	**L1 — Mechanical floor (non-negotiable).** A single failure here blocks the return, no
    12	matter how good the prose reads. This layer is never traded off against style.
    13	
    14	- **Facts, numbers, technical claims, code, commands, and quotes are unchanged.**
    15	
    16	**L2 — Slop removal (style).**
    17	
    18	- The opening reaches the point quickly — no runway.
    19	- The main point appears early.
    20	- The wording is concrete enough that a reader can picture the thing described.
    21	- No template phrases or startup jargon ("leverage", "seamless", "robust",
    22	  "circle back").
    23	- Headings and bullets remain only where they help the reader.
    24	- Emoji, icons, and decorative markdown are gone — unless the genre preset allows
    25	  them and the author's voice uses them.
    26	- Stock sections (Overview, Key Features, Conclusion) are gone unless they earn
    27	  their keep.
    28	- Repetition is gone.
    29	- The tone has a point of view instead of manufactured balance.
    30	- Warmth comes from specificity and cadence, not filler friendliness.
    31	- The prose sounds written, not assembled.
    32	- Necessary nuance is carried in the sentence, not bolted on as a hedge.
    33	- The result is shorter or sharper, not just different.
    34	
    35	**L3 — Genre + voice fit.** Run the cross-checks in the next section.
    36	
    37	**L4 — Acceptance (one honest question).** *Would a specific, informed human have written
    38	this?* If no, make another pass before returning.
    39	
    40	## Genre + voice cross-checks
    41	
    42	Two checks that depend on the layer above this skill:
    43	
    44	- **Genre fit:** re-read against the matching `scenario-presets.md` preset. Did the
    45	  rewrite respect that genre's *leave alone* list? (Don't strip a README's real
    46	  lists; don't add a heading to a tweet.)
    47	- **Voice fit:** if `_shared/voice-profile.md` was loaded, does the rewrite still
    48	  sound like that author — sentence rhythm, punctuation habits, preferred terms?
    49	  If no profile existed, did you keep the original's own voice rather than
    50	  flattening it to generic-clean?
    51	
    52	## Optional scoring pass
    53	
    54	For a borderline draft, score five dimensions (1–10 each) before returning.
    55	Adapted from the `stop-slop` rubric.
    56	
    57	- **Directness** — states things; doesn't announce it's about to state them.
    58	- **Rhythm** — sentence lengths vary; no monotone march of equal clauses.
    59	- **Trust** — respects the reader's intelligence; no over-explaining the obvious.
    60	- **Authenticity** — reads like a person chose the words, not a system.
    61	- **Density** — every sentence earns its place; no filler.
    62	
    63	Below 35 / 50 means it still reads generated — make another pass.
    64	
    65	> This is a *qualitative* gate, separate from the 0–100 AI-tell score in
    66	> `SKILL.md`. The 0–100 score reports density to the user; this checklist is the
    67	> editor's own pre-ship sweep.

hook: PostToolUse
hook: PostToolUse Completed
hook: PostToolUse Completed
hook: PostToolUse Completed
hook: PostToolUse Completed
hook: PostToolUse Completed
codex
The only material risk I see so far is around the new sync test’s strength, not the shipped prose instructions; I’m checking original checklist and actually executing the stdlib tests/YAML parse before finalizing the verdict.
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
hook: PostToolUse
hook: PostToolUse
exec
/bin/zsh -lc "git show HEAD:skills/ai-writing-suite/skills/comms-polish/references/final-pass-checklist.md | nl -ba | sed -n '1,90p'" in /Users/surahli/Documents/ai-writing-suite
exec
/bin/zsh -lc "git show HEAD:skills/ai-writing-suite/skills/comms-polish/SKILL.md | nl -ba | sed -n '105,145p'" in /Users/surahli/Documents/ai-writing-suite
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
     1	# Final-Pass Checklist
     2	
     3	Run this before returning any rewritten or edited copy. It's the last gate — the
     4	quick read-through that catches the tell you reintroduced while fixing another one.
     5	
     6	Adapted from `weijt606/anti-vibe-writing` (`final-pass-checklist.md`, MIT); the
     7	optional scoring pass is adapted from the `stop-slop` rubric (MIT).
     8	
     9	## The checklist
    10	
    11	- The opening reaches the point quickly — no runway.
    12	- The main point appears early.
    13	- The wording is concrete enough that a reader can picture the thing described.
    14	- No template phrases or startup jargon ("leverage", "seamless", "robust",
    15	  "circle back").
    16	- Headings and bullets remain only where they help the reader.
    17	- Emoji, icons, and decorative markdown are gone — unless the genre preset allows
    18	  them and the author's voice uses them.
    19	- Stock sections (Overview, Key Features, Conclusion) are gone unless they earn
    20	  their keep.
    21	- Repetition is gone.
    22	- The tone has a point of view instead of manufactured balance.
    23	- Warmth comes from specificity and cadence, not filler friendliness.
    24	- The prose sounds written, not assembled.
    25	- **Facts, numbers, technical claims, code, commands, and quotes are unchanged.**
    26	- Necessary nuance is carried in the sentence, not bolted on as a hedge.
    27	- The result is shorter or sharper, not just different.
    28	
    29	## Genre + voice cross-checks
    30	
    31	Two checks that depend on the layer above this skill:
    32	
    33	- **Genre fit:** re-read against the matching `scenario-presets.md` preset. Did the
    34	  rewrite respect that genre's *leave alone* list? (Don't strip a README's real
    35	  lists; don't add a heading to a tweet.)
    36	- **Voice fit:** if `_shared/voice-profile.md` was loaded, does the rewrite still
    37	  sound like that author — sentence rhythm, punctuation habits, preferred terms?
    38	  If no profile existed, did you keep the original's own voice rather than
    39	  flattening it to generic-clean?
    40	
    41	## Optional scoring pass
    42	
    43	For a borderline draft, score five dimensions (1–10 each) before returning.
    44	Adapted from the `stop-slop` rubric.
    45	
    46	- **Directness** — states things; doesn't announce it's about to state them.
    47	- **Rhythm** — sentence lengths vary; no monotone march of equal clauses.
    48	- **Trust** — respects the reader's intelligence; no over-explaining the obvious.
    49	- **Authenticity** — reads like a person chose the words, not a system.
    50	- **Density** — every sentence earns its place; no filler.
    51	
    52	Below 35 / 50 means it still reads generated — make another pass.
    53	
    54	> This is a *qualitative* gate, separate from the 0–100 AI-tell score in
    55	> `SKILL.md`. The 0–100 score reports density to the user; this checklist is the
    56	> editor's own pre-ship sweep.

 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
   105	- `blunt`: shortest viable version
   106	
   107	## Rewrite Workflow
   108	
   109	1. Identify the audience, purpose, and required structure.
   110	2. **Pick the genre preset.** Match the draft to a preset in
   111	   `references/scenario-presets.md` (tweet / LinkedIn / README / memo). It tells
   112	   you which catalog categories to weight harder and what to leave alone in this
   113	   genre. If no preset fits, scan the catalog evenly.
   114	3. **Load the voice profile if present.** Check for `../../_shared/voice-profile.md`
   115	   and read it if it exists; otherwise use a pasted sample or inferred voice
   116	   (see Voice Matching). Degrade gracefully when absent.
   117	4. Mark the factual anchors that must survive unchanged.
   118	5. Scan against the pattern catalog, weighted by the preset, and remove the tells
   119	   you find:
   120	   - throat-clearing and filler
   121	   - inflated significance
   122	   - vague attribution
   123	   - promotional adjectives
   124	   - forced three-item lists
   125	   - "not X but Y" theatrics
   126	   - uniform sentence length
   127	   - chatbot artifacts
   128	6. Replace vague abstractions with concrete actors, actions, examples, or consequences.
   129	7. Vary rhythm without adding fake personality. Bias word choice and cadence
   130	   toward the voice profile when one was loaded.
   131	8. **Run `references/final-pass-checklist.md`** before returning anything.
   132	9. Return the requested output and mention any claim that still needs evidence.
   133	
   134	## Safety Rules
   135	
   136	- Do not change the author's position to make the prose smoother.
   137	- Do not add examples, numbers, citations, or claims that were not present.
   138	- Do not remove caveats that carry real uncertainty.
   139	- Do not polish away legal, medical, financial, or safety warnings.
   140	- Do not rewrite quoted text unless the user asks.
   141	
   142	## Before And After Examples
   143	
   144	### Technical docs
   145	

hook: PostToolUse
hook: PostToolUse
exec
/bin/zsh -lc 'cd skills/ai-writing-suite/evals && PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -v' in /Users/surahli/Documents/ai-writing-suite
hook: PostToolUse Completed
hook: PostToolUse Completed
hook: PostToolUse Completed
hook: PostToolUse Completed
hook: PostToolUse
 succeeded in 220ms:
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
test_run_all_and_ci_never_invoke_the_judge (fixtures.test_fixtures.CIClean.test_run_all_and_ci_never_invoke_the_judge) ... ok
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
test_incomplete_reps_discarded_complete_rep_decides (fixtures.test_fixtures.JudgeParsing.test_incomplete_reps_discarded_complete_rep_decides) ... ok
test_majority_vote_across_reps (fixtures.test_fixtures.JudgeParsing.test_majority_vote_across_reps) ... ok
test_majority_vote_tie_resolves_fail (fixtures.test_fixtures.JudgeParsing.test_majority_vote_tie_resolves_fail) ... ok
test_missing_required_dim_returns_none (fixtures.test_fixtures.JudgeParsing.test_missing_required_dim_returns_none) ... ok
test_no_fabrication_fail_forces_overall_fail (fixtures.test_fixtures.JudgeParsing.test_no_fabrication_fail_forces_overall_fail) ... ok
test_parse_excludes_self_reported_verdict_line (fixtures.test_fixtures.JudgeParsing.test_parse_excludes_self_reported_verdict_line) ... ok
test_parser_tolerates_markdown_formatting (fixtures.test_fixtures.JudgeParsing.test_parser_tolerates_markdown_formatting) ... ok
test_required_dim_missing_from_all_reps_returns_none (fixtures.test_fixtures.JudgeParsing.test_required_dim_missing_from_all_reps_returns_none) ... ok
test_unparseable_returns_none (fixtures.test_fixtures.JudgeParsing.test_unparseable_returns_none) ... ok
test_prompt_builds_for_every_fixture (fixtures.test_fixtures.JudgePrompt.test_prompt_builds_for_every_fixture) ... ok
test_every_prompt_requests_no_fabrication (fixtures.test_fixtures.JudgePromptAlwaysScoresNoFabrication.test_every_prompt_requests_no_fabrication) ... ok
test_before_after_scores_in_band (fixtures.test_fixtures.ScoreBands.test_before_after_scores_in_band) ... ok
test_catalog_exists (test_catalog_sync.CatalogSync.test_catalog_exists) ... ok
test_every_tier1_word_is_in_the_catalog_table (test_catalog_sync.CatalogSync.test_every_tier1_word_is_in_the_catalog_table) ... ok
test_all_consumer_headers_present (test_voice_contract.VoiceProfileContract.test_all_consumer_headers_present) ... ok
test_template_exists (test_voice_contract.VoiceProfileContract.test_template_exists) ... ok

----------------------------------------------------------------------
Ran 49 tests in 0.095s

OK

hook: PostToolUse Completed
codex
`unittest discover` from `skills/ai-writing-suite/evals` passes 49 tests, including the new catalog sync test. The remaining question is whether that test proves all intended drift conditions or only a subset.
hook: PreToolUse
hook: PreToolUse
hook: PreToolUse
hook: PreToolUse Completed
hook: PreToolUse Completed
hook: PreToolUse Completed
exec
/bin/zsh -lc "sed -n '1,160p' skills/ai-writing-suite/evals/run_all.sh; sed -n '1,200p' .github/workflows/ci.yml" in /Users/surahli/Documents/ai-writing-suite
 succeeded in 0ms:
#!/usr/bin/env bash
# run_all.sh — run every v1 regression check in one shot, fail-fast.
#
# Stdlib-only: no pip installs, no external deps. Works from any cwd (resolves
# its own directory). Used both by humans pre-commit and by CI (.github/workflows/ci.yml).
#
# Checks, in order (any nonzero aborts the run):
#   1. unit tests   — detector logic + fixture well-formedness (~23 tests)
#   2. KB smoke     — end-to-end ingestion/retrieval over the seed KB (3 cases)
#   3. fixtures     — deterministic detector bands + 30-40% baseline calibration assert

set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")"   # the evals/ directory

echo "== [1/3] unit tests =="
python3 -m unittest discover -p 'test_*.py'

echo "== [2/3] KB smoke =="
python3 smoke_test.py

echo "== [3/3] fixtures (deterministic + calibration) =="
python3 -m fixtures.run_fixtures

echo
echo "ALL CHECKS PASSED"
name: CI

on:
  push:
    branches: [main]
  pull_request:

jobs:
  checks:
    name: regression checks (stdlib-only)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Run all v1 checks
        run: bash skills/ai-writing-suite/evals/run_all.sh

hook: PostToolUse
exec
/bin/zsh -lc "python3 -c \"from pathlib import Path; files=['skills/ai-writing-suite/skills/comms-polish/SKILL.md','skills/ai-writing-suite/skills/voice-onboard/SKILL.md','skills/ai-writing-suite/skills/comms-draft/SKILL.md','skills/ai-writing-suite/skills/comms-qa/SKILL.md'];
for f in files:
 text=Path(f).read_text(); block=text.split('---',2)[1]; lines=[line for line in block.splitlines() if line.strip()]; print(f, any(line.startswith('name: ') for line in lines), [line for line in lines if line.startswith('description: ')])\"" in /Users/surahli/Documents/ai-writing-suite
 succeeded in 0ms:
skills/ai-writing-suite/skills/comms-polish/SKILL.md True ["description: Polish prose that sounds AI-written while preserving meaning, facts, and author voice. Modes - detect, review, rewrite, edit - plus a 0-100 AI-tell score on demand. Use for docs, emails, posts, reports, and user-facing copy. Not for code cleanup, and not for learning or extracting an author's voice - that is voice-onboard."]
skills/ai-writing-suite/skills/voice-onboard/SKILL.md True ['description: Interview an author and distill their historical writing into a reusable voice profile that comms-polish reads for voice matching. Ingests local files or pasted samples, extracts a 10-dimension style fingerprint with sample evidence, and writes _shared/voice-profile.md. Use when the user says "learn my voice", "match how I write", or before a series of posts that must stay on-voice. Not for rewriting or polishing text - that is comms-polish; this skill only profiles.']
skills/ai-writing-suite/skills/comms-draft/SKILL.md True ['description: Draft a new page guided by the knowledge base / playbook. Not yet built - coming in v2. For polishing existing text use comms-polish; for KB Q&A use comms-qa.']
skills/ai-writing-suite/skills/comms-qa/SKILL.md True ['description: Answer questions from the knowledge base via a markdown mini-RAG over the pluggable KB. Not yet built - coming in v2. For polishing existing text use comms-polish; for drafting a new page use comms-draft.']

hook: PostToolUse
exec
/bin/zsh -lc "python3 -c \"from pathlib import Path; import sys; sys.path.insert(0, str(Path('skills/ai-writing-suite/evals').resolve())); from detector.patterns import TIER1, TIER1_PHRASES; text=Path('skills/ai-writing-suite/_shared/patterns/lexical-tells.md').read_text().lower(); print('tier1_keys',len(TIER1),'missing_keys',[k for k in TIER1 if k.lower() not in text]); print('missing_values',[(k,v) for k,v in TIER1.items() if v.lower() not in text]); print('phrase_suggestions_missing',[(p.pattern,s) for p,s in TIER1_PHRASES if s.lower() not in text])\"" in /Users/surahli/Documents/ai-writing-suite
 succeeded in 0ms:
tier1_keys 40 missing_keys []
missing_values []
phrase_suggestions_missing [('\\blandscape\\b', 'field, space, industry'), ('\\brealm\\b', 'area, field, domain'), ('\\btestament\\s+to\\b', 'shows, proves'), ('\\bwatershed\\s+moment\\b', 'turning point, shift'), ('\\bdeep\\s+dive\\b', 'look at, examine'), ('\\bdive\\s+into\\b', 'look at, examine'), ('\\bunpack(?:ing)?\\b', 'explain, break down'), ('\\bthought\\s+leader(?:ship)?\\b', 'expert, authority'), ('\\bbest\\s+practices\\b', 'what works, proven methods'), ('\\bat\\s+its\\s+core\\b', 'cut, just state it')]

hook: PostToolUse
hook: PostToolUse Completed
hook: PostToolUse Completed
hook: PostToolUse Completed
codex
The review gate is effectively closed: shipped instructions look additive/clarifying, while the new sync test has a real false-negative gap against the stated drift-guard purpose.
hook: PreToolUse
hook: PreToolUse Completed
exec
/bin/zsh -lc "ruby -rpsych -e 'ARGV.each{|f| s=File.read(f); b=s.split(\"---\",3)[1]; y=Psych.safe_load(b); puts \"#{f}: #{y.key?(\"name\") && y.key?(\"description\") && y[\"description\"].is_a?(String) && "'!y["description"].include?("'"\\n\")}\" }' skills/ai-writing-suite/skills/comms-polish/SKILL.md skills/ai-writing-suite/skills/voice-onboard/SKILL.md skills/ai-writing-suite/skills/comms-draft/SKILL.md skills/ai-writing-suite/skills/comms-qa/SKILL.md" in /Users/surahli/Documents/ai-writing-suite
 succeeded in 0ms:
skills/ai-writing-suite/skills/comms-polish/SKILL.md: true
skills/ai-writing-suite/skills/voice-onboard/SKILL.md: true
skills/ai-writing-suite/skills/comms-draft/SKILL.md: true
skills/ai-writing-suite/skills/comms-qa/SKILL.md: true

hook: PostToolUse
hook: PostToolUse Completed
codex
**Findings**

[CONCERN] `skills/ai-writing-suite/evals/test_catalog_sync.py:29`  
The sync test only checks whether each `TIER1` key appears anywhere in `lexical-tells.md`. That can pass if the replace-on-sight table is missing a row, has the wrong swap, or the word appears elsewhere in prose. Concrete fix: parse the markdown table rows into `{word: swap}` and assert exact equality with `TIER1` keys and values.

No blocker findings in the shipped skill text. Verified: rewrite steps are sequential `1-10`; frontmatter parses as YAML with one-line `description`; `TIER1` table manually matches all 40 dict keys and swaps; graduation remains human/maintainer-only; final checklist preserves the original 13 items with facts moved to L1; `run_all.sh`/CI are unchanged; `python3 -m unittest discover -v` from `evals/` passes 49 tests.

VERDICT: COMMIT-WITH-FIXES

VERIFIED_AGAINST: feat/engine-polish-distill @ 0a4de7fc14def87d92f298c74b3c4601a1fd2355 @ 2026-06-08T00:05:41-0700
hook: Stop
hook: Stop
hook: Stop Completed
hook: Stop Completed
tokens used
66,129
**Findings**

[CONCERN] `skills/ai-writing-suite/evals/test_catalog_sync.py:29`  
The sync test only checks whether each `TIER1` key appears anywhere in `lexical-tells.md`. That can pass if the replace-on-sight table is missing a row, has the wrong swap, or the word appears elsewhere in prose. Concrete fix: parse the markdown table rows into `{word: swap}` and assert exact equality with `TIER1` keys and values.

No blocker findings in the shipped skill text. Verified: rewrite steps are sequential `1-10`; frontmatter parses as YAML with one-line `description`; `TIER1` table manually matches all 40 dict keys and swaps; graduation remains human/maintainer-only; final checklist preserves the original 13 items with facts moved to L1; `run_all.sh`/CI are unchanged; `python3 -m unittest discover -v` from `evals/` passes 49 tests.

VERDICT: COMMIT-WITH-FIXES

VERIFIED_AGAINST: feat/engine-polish-distill @ 0a4de7fc14def87d92f298c74b3c4601a1fd2355 @ 2026-06-08T00:05:41-0700
