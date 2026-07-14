# Design — Q10 Multi-Genre Voice-Profile Contract (2026-07-13)
Status: DRAFT — owner review gate, do not build

Implements decisions Q10 (`build-multi`) and the Q8 rider from `docs/decisions-2026-07-13.md:16,18`, closing review finding 4 (`reviews/2026-07-13-e2e-product-prose.md:37-42`): the producer offers two profiles for mixed genres (`voice-onboard/SKILL.md:60,105`) but only `_shared/voice-profile.md` exists and both consumers hardcode that single path (`comms-polish/SKILL.md:82`, `comms-draft/SKILL.md:44`).

## 1. Storage — per-genre files, legacy file as fallback
New profiles live at `_shared/voice-profiles/<profile-id>.md`, one file per genre. The **filename is the contract**: it encodes the genre, so a directory listing alone answers "which genres do I have" without reading any file body.

Back-compat (must not break legacy installs): the existing shipped `_shared/voice-profile.md` is **not renamed** (renaming a shipped file would trip packaging validators and break installed forks). It stays as the shipped sample and as a legacy single-profile fallback. Consumers check `_shared/voice-profiles/` first; if that directory is absent or empty, they fall back to the legacy single file exactly as today.
*Alt rejected:* one file with per-genre H2 sections — cheaper lookup but forces every consumer to parse the whole file and re-introduces the "average across genres" risk the producer explicitly forbids (`stylometry.py:15-23`).

## 2. Profile IDs
`profile-id = <genre-slug>`, pattern `[a-z0-9-]+` (e.g. `blog.md`, `linkedin.md`, `formal-report.md`). Genre set is **free-form**, not a fixed enum — genres are open-ended (tweet, memo, README) and a closed list would reject valid ones. Collision rule: re-onboarding an existing genre overwrites that one file, showing the changed-diff first (the current Step-4 behavior, `voice-onboard/SKILL.md:165-167`).
*Alt rejected:* fixed enum — simpler validation, but wrong for an open genre space.

## 3. Default-selection (deterministic precedence)
A consumer resolves a profile in this order, first match wins:
1. **Explicit user request** — user named a genre/profile ("use my LinkedIn voice") → load that id; if missing, say so and drop to rule 4.
2. **Genre/preset match** — the run already selects a scenario preset (`comms-draft/SKILL.md:49`); match the profile id to that genre.
3. **Single-profile fallback** — exactly one profile exists → use it.
4. **Offer-then-degrade (Q8, `decisions:16`)** — zero matches: offer `voice-onboard` once, then degrade to inferred voice with a one-line output note. Multiple profiles but none match the genre: degrade to inferred, note which genres *do* exist so the user can redirect. Never block.

## 4. Consumer lookup (cheap — one listing)
Both consumers run: (a) list `_shared/voice-profiles/*.md` — one directory read, no body parsing; (b) apply the §3 precedence against the filename slugs; (c) read the **full body of the one selected file only**. If the directory is absent/empty, fall back to legacy `_shared/voice-profile.md`. Added consumer prose is ~4 lines each — the lookup rule replaces the current hardcoded-path sentence rather than adding to it (context-bloat constraint).

## 5. Producer contract (voice-onboard)
- Writes one file per genre to `_shared/voice-profiles/<genre>.md`, preserving every `## H2` header (`voice-onboard/SKILL.md:44,165`).
- **Split, don't flatten:** mixed samples → N separate files, one per genre; the existing prohibition on pooling (`SKILL.md:105,129-133`) becomes "one file per genre" instead of "two blocks in one file".
- Adds a `Genre:` field to the Meta block so a file self-declares its genre (redundant with the filename, but survives a manual rename).
- The **Measured Fingerprint** lives inside each genre's file as a single `### <genre>` block (`stylometry.py --genre` already runs per genre, `voice-onboard/SKILL.md:115-133`) — no more multi-genre stacking in one file.

## 6. Q8 rider interaction
The post-edit voice-capture updates the **profile used for that run** (the one §3 resolved). If the run was **degraded/inferred** (no profile matched), the capture offer instead **creates a new profile of that run's genre** — the edit delta seeds a genre file that did not exist. This is the strongest-voice-signal intent of the rider (`decisions:16`) made unambiguous about *which* file it touches.

## 7. Non-goals + open questions
**Non-goals:** cross-genre inheritance/merging; auto-detecting a text's genre without a preset or user hint; migrating the legacy single file (it stays as fallback until re-onboarded).
**Open questions for owner (max 3):**
1. When rule 1 names a genre with no profile, **offer to create it** (voice-onboard handoff) or silently degrade?
2. Is `Genre:` in Meta worth the redundancy with the filename, or is the filename the sole source of truth?
3. Multiple-match-none case (§3): **ask** the user interactively, or **degrade + note** without asking?
