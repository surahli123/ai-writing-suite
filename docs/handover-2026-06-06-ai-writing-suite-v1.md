# Handover — AI Writing Suite v1 (plan + rename)

Date: 2026-06-06
Project: personal-productivity-skills (`~/Documents/Codex/2026-06-01/personal-productivity-skills`)
Branch: `rename-ai-writing-suite` (PR #4 open → main)

## Last session summary

Took the user's `ai-writing-humanizer` skill and, through `/grill-me` + `/plan-eng-review`
+ `/plan-ceo-review`, designed its evolution into a full **AI writing-assistant suite**
(the OSS version of a company DS writing skillset driven by a proprietary DS Comms
Playbook via a pluggable KB). Plan written and reviewed. Renamed the skill package
`ai-writing-humanizer` → `ai-writing-suite` and opened PR #4. No suite code built yet —
this was planning + rename only.

## Current state

- **Plan**: `docs/design-ai-writing-suite-v1-2026-06-06.md` — full decision log D1–D12,
  v1 scope (9 items), risks R1–R6, eng+ceo GSTACK review report (both CLEARED).
- **Rename**: committed (760a2ee), pushed, **PR #4 open** →
  https://github.com/surahli123/personal-productivity-skills/pull/4 (NOT merged yet).
- **No suite implementation exists.** The renamed `skills/ai-writing-suite/` still
  contains only the original humanizer (polish) content.
- Reference repos cloned at `/tmp/grill-refs/` (anti-vibe-writing, avoid-ai-writing,
  AI-Vibe-Writing-Skills, nature-skills) — all MIT. May be gone after reboot; re-clone if needed.

## Key decisions (see design doc for full table)

- **Suite** = router (thin, RovoDev-only routing) + comms-qa + comms-draft + comms-polish
  + voice-onboard; self-improvement = human-gated cross-cutting hook.
- **Engine vs fuel**: OSS bundles generic KB; company forks and drops the real playbook
  into `_shared/knowledge/` via a **Confluence page** (data, not engineering).
- **RAG** = pure markdown + INDEX.md, zero-dep, portable across Claude/Codex/Cursor/RovoDev
  (NOT OMC wiki MCP tools — those break off-Claude). "Wiki-style" = convention only.
- **Eval (D10)**: fixtures (LLM-judge, baseline fails 30-40%) + ported avoid-ai JS detector
  + Autorefine-style (Three Gulfs / error-analysis / mutation) self-improvement loop.
- **v1 (D12)**: must prove ONE end-to-end ingestion+retrieval smoke path so the company
  step is truly "drop in a Confluence page".
- Absorb all 4 MIT repos with NOTICE attribution; nature-skills → only writing+polishing.

## Next steps (priority order)

1. **Merge PR #4** (rename) once reviewed.
2. Start the v1 build: `git checkout main && pull`, cut `feat/ai-writing-suite-v1`.
3. Build per design doc §5: suite skeleton + router → consolidate pattern catalog into
   `_shared/patterns/` (fix corrupted blader ref) → comms-polish enrichment →
   voice-onboard → generic KB seed + INDEX → ingestion+retrieval smoke path → eval harness
   → human-gated self-improvement hook → NOTICE/CHANGELOG/README → Claude+Codex packaging.
4. Read the Autorefine skill before building the eval/self-improvement loop.

## Gotchas / constraints

- Plan-only discipline: user is product owner, wants plan→approve→build in visible stages.
- Do NOT rename the GitHub repo; umbrella repo keeps `agent-goal-contracts`.
- Keep this suite SEPARATE from the personal writing-vault (`/distill`, `/voicecheck`) —
  the "AI scaffolds never ghostwrites" philosophy applies there, not here (R1).
- Installed copy `~/.codex/skills/ai-writing-humanizer/` still has the OLD name + 3 rich
  refs (stop-slop, blader [corrupted], aboudjem). Re-point/rename after PR #4 merges.

## Relevant files

- `docs/design-ai-writing-suite-v1-2026-06-06.md` (the plan — read first)
- `skills/ai-writing-suite/SKILL.md` (current = humanizer content)
- `/tmp/grill-refs/` (4 reference repos)
