# Design — Q10 Multi-Genre Voice-Profile Contract (2026-07-13)
Status: APPROVED 2026-07-14 — amendments below

## Decisions (owner, 2026-07-14) — resolve the §7 open questions

The three §7 open questions plus one matching-semantics ruling, answered by the
product owner. These override any conflicting text in §1–§6 above.

- **OQ1 (§7.1 — named genre, no profile):** OFFER voice-onboard creation for that
  genre. The offer shares the single per-session Q8 offer budget (`comms-polish`
  Voice Matching / `comms-draft` step 2). Declined or unanswered → degrade to
  inferred voice and note it. Never block.
- **OQ2 (§7.2 — `Genre:` in Meta):** KEEP a `Genre:` field in each profile's Meta
  block (a self-description that survives a manual rename). But the **filename is
  the sole source of truth on conflict** — lookup reads filenames only and never
  parses `Genre:` to decide selection. `Genre:` is documentation, not the key.
- **OQ3 (§7.3 — multiple profiles, none match):** never block; degrade to inferred
  voice and let the output note list the genres that DO exist so the user can
  redirect. Do not ask interactively. Note: the Q8/OQ1 voice-onboard offer (on
  explicit my-voice requests only) is sanctioned and is never a which-profile
  question; OQ3 forbids interactive profile-picking, not the Q8 offer.
- **OQ4 (preset↔profile matching semantics):** NORMALIZED EXACT match — lowercase,
  spaces→hyphens, then string equality. No fuzzy/prefix/alias matching
  (`formal-report` ≠ `report`; `formal-report` ≠ `formal`). A miss falls through
  the §3 precedence to offer-then-degrade, it does not silently pick a near-name.

Implements decisions Q10 (`build-multi`) and the Q8 rider from `docs/decisions-2026-07-13.md:16,18`, closing review finding 4 (`reviews/2026-07-13-e2e-product-prose.md:37-42`). This describes the pre-Q10 state now fixed: the producer offered profiles for mixed genres (`voice-onboard/SKILL.md`, "Gather samples" / "Split, don't flatten") but only `_shared/voice-profile.md` existed and both consumers hardcoded that single path (`comms-polish/SKILL.md` Voice Matching, `comms-draft/SKILL.md` Inputs). The Decisions section above and §1–§6 below record the built contract.

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

## 7. Non-goals + resolved questions
**Non-goals:** cross-genre inheritance/merging; auto-detecting a text's genre without a preset or user hint; migrating the legacy single file (it stays as fallback until re-onboarded).
**Resolved questions** (answered by the owner — see the Decisions section at the top of this doc for the binding rulings):
1. Rule-1 names a genre with no profile → **OFFER to create it** (OQ1).
2. `Genre:` in Meta is kept, but the **filename is the sole source of truth** on conflict (OQ2).
3. Multiple-match-none case (§3) → **degrade + note** which genres exist; never ask interactively (OQ3).
