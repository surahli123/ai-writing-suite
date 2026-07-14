# Adversarial review (Codex gpt-5.6-sol xhigh) — prose mega-fix branch, 2026-07-13

Run B scope: comms-polish SKILL + scenario-presets + comms-qa + voice-onboard + voice-profile.md.
Run A scope (router + comms-draft): first attempt timed out (600s), retry pending — appended below when done.
Full-scope single run timed out at 600s (third data point for the one-subsystem rule; even one subsystem needed splitting).

## Run B verbatim output

BLOCKER

- `skills/ai-writing-suite/skills/comms-polish/SKILL.md:197` — All three worked examples violate the zero-new-facts probe:
  - Technical, line 200: adds “before they start editing”; neither the timing nor editing exists in the before-text.
  - Status, line 214: strengthens “a step toward improving” into the direct claim “improves.”
  - Personal, line 233: adds magnitude and presumed knowledge: “It helped more than you probably know.”
  These contradict lines 64, 165–170, and 182.

- `skills/ai-writing-suite/skills/comms-polish/SKILL.md:89` — Q8’s no-profile path is effectively unreachable at HEAD. The skill treats file existence as a learned profile, while `skills/ai-writing-suite/_shared/voice-profile.md:57` declares the always-present file an example containing fictional Sam. An agent will load Sam instead of offering onboarding or degrading to inferred voice.

- `skills/ai-writing-suite/skills/comms-polish/SKILL.md:112` — Q8 has conflicting execution semantics:
  - “Which?” invites a blocking turn, while line 114 says never block.
  - Lines 112 and 121 each establish their own once-per-session offer, permitting two offers.
  - Lines 119–125 require a post-run offer, while lines 281–286 permit only the degraded-voice note as a voice-related rewrite addition.
  - Line 103 requires a no-profile note generally, but lines 282–286 permit it only for explicit “my voice” requests.

- `skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:63` — The fabrication boundary remains open. “Sharp question,” “concrete next step,” “takeaway,” and “specific next step” at lines 63 and 92 can add new substance. Lines 144–146 can similarly invent branches, decisions, or tradeoffs. “Don’t invent facts” does not prevent adding non-factual but substantive material.

- `skills/ai-writing-suite/_shared/voice-profile.md:29` — The claimed canonical-header discipline is not implemented. It says consumers do not restate subsets, but `comms-polish/SKILL.md:93` immediately restates one and omits `Measured Fingerprint`, despite that section containing direct voice guidance. An agent can reasonably ignore the quantitative fingerprint.

CONCERN

- `skills/ai-writing-suite/skills/voice-onboard/SKILL.md:58` — “One genre per run” conflicts with the line 79 example, which invites extraction from four blog posts plus two memos. The shipped sample profile also spans multiple genres at `voice-profile.md:72` and `:161` while measuring only blog.

- `skills/ai-writing-suite/_shared/voice-profile.md:18` — It and `voice-onboard/SKILL.md:12` claim `comms-polish` reads the profile “every run,” but `comms-polish/SKILL.md:89` only requires it before rewrites.

- `skills/ai-writing-suite/_shared/voice-profile.md:122` — The sample treats “Not X, but Y” as an authentic signature move, while `comms-polish/SKILL.md:162` and `scenario-presets.md:47` tell agents to remove that construction as theatrics without a clear voice-precedence test.

- `skills/ai-writing-suite/skills/comms-qa/SKILL.md:89` — Q9 is otherwise consistent across frontmatter, body, and output. The remaining ambiguity is line 93’s “state the gap and stop”: for a multipart strict-mode question, it could mean stop that subpart or abort the entire invocation.

- `skills/ai-writing-suite/skills/voice-onboard/SKILL.md:73` — The claim that `comms-draft` offers manual-edit routing cannot be verified within the explicitly permitted five-file scope. I did not inspect `comms-draft`.

SUGGESTION

- `skills/ai-writing-suite/skills/comms-polish/SKILL.md:89` — Define an explicit valid-profile predicate that treats the shipped sample marker as “no profile.”

- `skills/ai-writing-suite/skills/comms-polish/SKILL.md:108` — Define one shared offer budget, whether an offer pauses execution, and where the post-run/manual-edit offer appears relative to rewrite output.

- `skills/ai-writing-suite/skills/comms-polish/references/scenario-presets.md:63` — Add “only when already supported by the source” to every ending, branch, takeaway, recommendation, and next-step instruction.

Hard questions:

1. Is Q8’s “offer once” one global session-level offer across pre-run, post-run, and manual-edit triggers, or one offer per trigger?
2. Should the pre-run “Which?” pause for an answer, or should polishing proceed immediately with inferred voice?
3. Must the shipped Sam profile be treated as absent until overwritten, and what exact marker determines that?
4. In strict KB-only multipart requests, does “stop” end only the uncovered part or the whole response?

Independent role-typed review lanes were unavailable on this App surface; approval would therefore be gated even without the blockers above.

VERDICT: REVISE

VERIFIED_AGAINST: fix/prose-mega-fix @ 11d87e9
## Run A (router + comms-draft): CIRCUIT BREAKER — 3 consecutive 600s timeouts

Attempts: full-scope (all 7 files), narrow (2 files + trace probes), tight (2 files,
3 questions, 400-word cap). All exit 124; `-o` file never written. Run B (5 files,
fact-check-style probes) completed in ~4 min — failure class is probe TYPE, not scope:
behavior-trace simulation probes do not converge at xhigh on this model. No 4th attempt
per circuit-breaker protocol; owner to choose: accept gap (router+draft covered by
in-context code-reviewer + orchestrator line review, both clean on Q7 axes) or re-run
with different probe style/effort.

## Orchestrator disk-arbitration of Run B (re-grepped against HEAD 11d87e9)

- B1 worked-examples fabricate: CONFIRMED all three (technical adds "before they start
  editing"; migration strengthens "step toward improving"→"improves" — modality = claim
  change; personal adds "It helped more than you probably know" — magnitude + presumed
  reader mind, itself an overstepping tell).
- B2 shipped Sam sample defeats Q8: CONFIRMED — `> SAMPLE PROFILE.` banner present at
  voice-profile.md:64; polish's existence-check loads Sam on fresh installs; Q8
  no-profile path unreachable. Highest-impact finding of the session.
- B3 Q8 semantics conflicts: CONFIRMED (dual offer budgets; "Which?" blocking ambiguity;
  post-run offer vs text-only output; two inconsistent note rules).
- B4 presets endings license substance-adding: CONFIRMED (pre-existing, same class
  as remediation 1.8).
- B5 canonical-list discipline self-violated: CONFIRMED (polish + draft restate
  10-header subset, omit Measured Fingerprint).
- C1 one-genre-per-run vs 4-blogs+2-memos example: CONFIRMED (introduced this branch).
- C2 "every run" drift: CONFIRMED, cheap fix. C4 strict-mode multipart "stop": CONFIRMED
  ambiguity. C5 voice-onboard overclaims comms-draft offer: CONFIRMED (= code-reviewer
  MAJOR; fix = narrow claim to comms-polish per Q8 letter).
- C3 (Sam's "Not X, but Y" signature move vs catalog theatrics-removal, voice-precedence
  test): REAL but product-policy — deferred to owner, NOT fixed this branch.

Fix batch F1–F10 dispatched to executor 2026-07-13 (round 2); code-reviewer verdict
APPROVE-WITH-FIXES (MAJOR = C5-equivalent, MINOR = migration-example triple, folded
into F2/F8).

VERIFIED_AGAINST: fix/prose-mega-fix @ 11d87e9
