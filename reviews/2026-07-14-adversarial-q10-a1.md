# Adversarial review (Codex gpt-5.6-sol xhigh) — Q10 + A1 stacked branches, 2026-07-14

Scope: git diff fix/prose-mega-fix...fix/a1-followups (fact-check probes only — the
behavior-trace probe style that timed out 3x on 07-13 was avoided; run completed in ~7 min).
code-reviewer (isolated worktree) ran in parallel: APPROVE-WITH-FIXES, 1 MINOR (explicit Genre: clause).

## Codex verbatim output

## Findings

### BLOCKER — OQ3 is directly contradicted by both consumers

Approved spec: “profiles exist but none match” must “degrade + note” and “Do not ask interactively” ([spec](/Users/surahli/Documents/ai-writing-suite/docs/design-q10-voice-profile-contract-2026-07-13.md:17)).

But:

- `comms-polish`: “no match → make the Q8 offer once” ([comms-polish](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/skills/comms-polish/SKILL.md:99)), then explicitly asks “Which?” when profiles exist but none match ([line 135](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/skills/comms-polish/SKILL.md:135)).
- `comms-draft`: “no match → Q8 offer once” ([comms-draft](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/skills/comms-draft/SKILL.md:61)); its Q8 clause includes “profiles exist but none match” and asks “which?” ([line 132](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/skills/comms-draft/SKILL.md:132)).

“The question never blocks” does not satisfy “Do not ask interactively.” Both consumers conflate OQ1’s explicitly named missing genre with OQ3’s preset mismatch.

### BLOCKER — the ONE shared offer budget is not actually cross-file

OQ1 requires one budget shared between `comms-polish` and `comms-draft` ([spec](/Users/surahli/Documents/ai-writing-suite/docs/design-q10-voice-profile-contract-2026-07-13.md:9)).

- `comms-polish` defines sharing only among “the two triggers below” inside that file ([lines 130–154](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/skills/comms-polish/SKILL.md:130)).
- `comms-draft` independently says “Offer at most once per session” ([line 139](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/skills/comms-draft/SKILL.md:139)).

Nothing says a `comms-draft` offer spends `comms-polish`’s budget. As written, a session can receive one offer from each.

### BLOCKER — producer destination claims drift across files

The active producer says real profiles are written only to `_shared/voice-profiles/<genre-slug>.md`, and legacy `_shared/voice-profile.md` is left alone ([voice-onboard](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/skills/voice-onboard/SKILL.md:47), [line 195](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/skills/voice-onboard/SKILL.md:195)).

Contradictory claims remain:

- Template: completed contents “are written out to `voice-profile.md`” ([host-profile-template](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/_shared/host-profile-template.md:8)).
- Sample schema: it is “meant to be OVERWRITTEN per user” and `voice-onboard` “fills this in” ([voice-profile](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/_shared/voice-profile.md:8)).
- Banner copy: “Your real profile overwrites all of it” ([line 70](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/_shared/voice-profile.md:70)).

This is exactly the file-A-claims-file-B behavior drift class.

### CONCERN — banner predicate differs between consumers

- `comms-polish` ends with the general rule: “A profile is valid only with the banner absent” ([line 104](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/skills/comms-polish/SKILL.md:104)).
- `comms-draft` applies the banner gate only to the legacy fallback ([line 62](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/skills/comms-draft/SKILL.md:62)).
- Yet `voice-onboard` claims both consumers reject “any file carrying that banner” ([line 202](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/skills/voice-onboard/SKILL.md:202)).

Thus `comms-draft` does not explicitly reject a banner-bearing file inside `voice-profiles/`.

### CONCERN — confidence contract overlaps at N=10

Both the template and producer define `Medium = 5-10` and `High = 10+` ([template](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/_shared/host-profile-template.md:42), [voice-onboard](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/skills/voice-onboard/SKILL.md:69)). Ten samples satisfy both.

### SUGGESTION — approved spec retains stale references

The behavioral clauses are recoverable, but several cited `voice-onboard` line numbers no longer point to the behavior described ([spec](/Users/surahli/Documents/ai-writing-suite/docs/design-q10-voice-profile-contract-2026-07-13.md:48)). Section 7 also remains labeled “open questions” after approval.

## Probe 1 — consumer lookup side by side

| Contract point | `comms-polish` | `comms-draft` | Result |
|---|---|---|---|
| Listing | “List `_shared/voice-profiles/*.md` — one directory read, filenames only, no body parsing.” | “list `_shared/voice-profiles/*.md` (one directory read, filenames only)” | Same |
| Precedence | Explicit request → normalized exact preset → single profile → no match | Same four steps | Same |
| Normalization | “lowercase, spaces→hyphens… string equality, no fuzzy/prefix/alias” | “lowercase, spaces→hyphens, string equality; no fuzzy/prefix/alias” | Same |
| Fallback | Absent/empty directory → legacy file | Same | Same |
| Banner | General validity sentence after legacy rule | Explicit only for legacy fallback | Different |
| OQ3 note | Says the “degraded note” lists existing genres | Says “say which genres” but Output guarantees only that no profile was used | Weaker in draft |

Core selection order and OQ4 match. Banner scope and OQ3 output wording differ.

## Probe 2 — producer contract

The operational producer contract itself matches the intended storage interface:

- Directory and slug: `_shared/voice-profiles/<genre>.md`, `[a-z0-9-]+`, lowercase and spaces→hyphens ([voice-onboard](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/skills/voice-onboard/SKILL.md:47)).
- `Genre:` is in `## Meta` in the copied template, with filename authoritative ([template](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/_shared/host-profile-template.md:34)).
- Real profiles never carry the sample banner ([voice-onboard](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/skills/voice-onboard/SKILL.md:202)).
- Consumers select using filenames, not `Genre:` bodies.

However, the stale template/sample descriptions above contradict where the producer writes.

## Probe 4 — headers

PASS. Both files contain the same 14 H2 headers, in the same order:

`Meta`, `Tone`, `Sentence Length`, `Vocabulary`, `Vocabulary Do`, `Vocabulary Don't`, `Signature Moves`, `Punctuation & Formatting`, `Openings & Closings`, `Uncertainty Style`, `Things To Avoid`, `Scope & Calibration`, `Measured Fingerprint`, `Changelog`.

`Genre:` was added to `Meta` in both files.

## Probe 5 — A1 findings 8/9/11/12/13

- **8:** “Two inputs are REQUIRED… brief and suite root… voice profile, KB match, and genre preset [are optional]” ([comms-draft](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/skills/comms-draft/SKILL.md:32)). No excess change.
- **9:** Two sanctioned rewrite additions: degraded-voice line plus a narrowly limited `Notes:` block for evidence flags ([comms-polish](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/skills/comms-polish/SKILL.md:327)). No excess change.
- **11:** Concrete scope names and Layer-3 language appear in all four children: [draft](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/skills/comms-draft/SKILL.md:276), [polish](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/skills/comms-polish/SKILL.md:317), [QA](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/skills/comms-qa/SKILL.md:155), [onboard](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/skills/voice-onboard/SKILL.md:244). No excess change.
- **12:** Adds explicit thresholds, template-copy-not-edit, and profile-local changelog destination ([voice-onboard](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/skills/voice-onboard/SKILL.md:69), [line 176](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/skills/voice-onboard/SKILL.md:176), [line 218](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/skills/voice-onboard/SKILL.md:218)). No excess change, but the requested N=10 overlap remains ambiguous.
- **13:** Adds conditional, non-deliverable `Sources used:` provenance ([comms-draft](/Users/surahli/Documents/ai-writing-suite/skills/ai-writing-suite/skills/comms-draft/SKILL.md:296)). No excess change.

The later attribution relocation is separate from findings 8/9/11/12/13, not hidden expansion inside their fix commit.

## Hard questions

1. Why do both consumers ask “Which?” in the exact OQ3 case where the approved spec says “Do not ask interactively”?
2. What written clause prevents `comms-draft` from spending one offer and `comms-polish` from later spending its separately defined offer?
3. Is legacy `_shared/voice-profile.md` immutable sample/fallback, or a file that `voice-onboard` still overwrites? The current contracts assert both.

VERDICT: REVISE  
VERIFIED_AGAINST: fix/a1-followups @ 6063589
## Orchestrator disk-arbitration (against fix/a1-followups @ 6063589)

- B1 (OQ3 vs Which?): PARTIALLY CONFIRMED — draft's offer IS conditioned on explicit
  my-voice (Q8-sanctioned), so no owner-intent violation; but polish rule-4's
  unconditioned 'make the Q8 offer' shorthand + the spec's missing carve-out are real
  ambiguity. Fix = disambiguate both consumers + spec OQ3 bullet (G1), not remove offers.
- B2 (budget not cross-file): CONFIRMED verbatim (draft:139 standalone once-per-session;
  polish budget scoped to its own two triggers). Fix G2 = suite-wide budget sentence both files.
- B3 (producer destination drift): CONFIRMED — template:8, sample:8-10, banner:70 all
  still claim voice-profile.md is the write target. Fix G3.
- C1 (banner scope): CONFIRMED — draft gates only the legacy path. Fix G4.
- C2 (N=10 overlap): CONFIRMED — Medium 5-10 vs High 10+. Fix G5 (Medium 5-9).
- SUGGESTION (spec stale refs/§7 label): accepted as G7. code-reviewer MINOR = G6.

Fix batch G1-G7 dispatched to executor 2026-07-14.
VERIFIED_AGAINST: fix/a1-followups @ 6063589
