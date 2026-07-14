# Unified remediation plan — E2E product reviews (2026-07-13)

Synthesizes four review slices (A1 prose / A2 assets / B1 packaging / B2 journeys — all
FIX-FIRST; full critiques under `reviews/2026-07-13-e2e-product-*.md`) into three buckets.
Orchestrator-owned; updated as items close.

## Bucket 1 — objective defects, fix without waiting (status-tracked)

| # | Finding (source) | Where | Status |
| --- | --- | --- | --- |
| 1.1 | comms-draft frontmatter invalid strict YAML → skill undiscoverable on fresh install (B1) | PR #15 @ 8ce298f + class regression test | **FIXED, pushed, CI green** |
| 1.2 | kb collision re-ingest mints tone-3.md — idempotency promise false (B2, executed) | lane-kb-ingestion round 2 | dispatched |
| 1.3 | kb_ingest destroys shipped INDEX header incl. frozen protocol text (B2, executed) | lane-kb-ingestion round 2 | dispatched |
| 1.4 | Onboarding funnel entrances (kb-onboarding front pointer + \_shared/knowledge/README) (B2) | lane-kb-ingestion round 2 | dispatched |
| 1.5 | Troubleshooting table + dual-bookkeeping hint + "ready for first use" softening (B2) | lane-kb-ingestion round 2 | dispatched |
| 1.6 | Register-shift contradiction C11 vs rhythm guardrail + index misplacement (A2 BLOCKER) | needs a prose fix lane | queued |
| 1.7 | Self-improvement lifecycle: `graduated` illegal status; scope schema excludes comms-draft/qa; README order contradicts protocol (A2 BLOCKERs) | needs a prose fix lane | queued |
| 1.8 | comms-polish worked example fabricates facts its own rules forbid; scenario-presets "actual number" drift (A1 BLOCKER) | needs a prose fix lane | queued |
| 1.9 | Router refuses to route when directly invoked (A1 BLOCKER) — add an executable classify-and-load step | needs a prose fix lane | queued |
| 1.10 | Router "read every referenced file" defeats selective loading (A1) | same lane as 1.9 | queued |
| 1.11 | Voice-profile header schema drift producer vs consumers (A1) — one canonical list | same lane | queued |
| 1.12 | Stale router status prose ("later"/"until then" for shipped skills) (A1) | same lane | queued |
| 1.13 | Dead refs: voice "project plan R1", scenario-presets "design §5"; catalog paths not fully qualified (A1) | same lane | queued |
| 1.14 | Marketplace descriptions still say "v2" for shipped skills (B1) | release-hygiene lane | queued |
| 1.15 | LICENSE copyright says "AI Writing Humanizer contributors"; NOTICE points to nonexistent root LICENSE (B1) | release-hygiene lane | queued |
| 1.16 | CI never validates the plugin body — add manifest checks + `claude plugin validate` equivalents where runnable key-free (B1 BLOCKER) | release-hygiene lane | queued |
| 1.17 | .gitignore the runtime worktrees (`.claude/worktrees/`) — accidental `git add .` trap (B1) | release-hygiene lane | queued |
| 1.18 | Root README vs suite README contradict on comms-qa/draft status (B2) | release-hygiene lane | queued |
| 1.19 | SMOKE-TEST stale "two cases" + Case-1 wrong-reason rationale (A2) | assets fix lane | queued |
| 1.20 | 00-index: real links, counts, fix dead `notes/` pointer, drop "deduplicated" overclaim until true (A2) | assets fix lane | queued |

## Bucket 2 — closes automatically at integration (verify, don't build)

| # | Item | Closes when |
| --- | --- | --- |
| 2.1 | Measured Fingerprint missing from template/example/writer-contract (A2 BLOCKER 5) | feat/stylometric-fingerprint merges (template:109, voice-profile:138, SKILL step 2 all updated there) |
| 2.2 | "1.1.0 presented as released while public main is 1.0.0" (B1) | owner merges PR #15 + tags v1.1.0 |
| 2.3 | CHANGELOG missing the draft/voice eval lanes (B1) | behavioral-evals branch merge adds its own entries |
| 2.4 | KB tools invisible + no CHANGELOG entry (B2 part) | kb branch merge PR carries README/CHANGELOG entries (root README part is 1.18) |

## Bucket 3 — owner decisions (blocked on you; do not implement until answered)

Collected across all reviews. The first six are already in the decision artifact
(claude.ai/code/artifact/26f490e8-…); the rest below should be answered in the same pass.

**Product-definition (A1 hard questions):**
- P1 Mixed edit-plus-add: does comms-draft return the fully revised document (existing text
  as immutable source), or only the new section + mandatory comms-polish invocation?
  (The current seam clause routes mixed requests to a skill that says it never edits
  existing text — 1.9's fix needs this answer.)
- P2 "In my voice" with no profile: acceptable generic-voice fallback, or a mandatory
  voice-onboard gate?
- P3 comms-qa: strictly KB-only, or is the separately-labeled "Outside the playbook"
  section part of the product? (Frontmatter and body currently disagree.)
- P4 Multi-genre voice profiles: v1 capability (then define storage/selection contract)
  or explicitly one-genre-per-run in v1?

**Fork/product strategy (B2 hard questions):**
- P5 Should a fork REPLACE the generic KB by default? (Decides the shadowing fix and the
  Step-0 doc guidance.)
- P6 Who owns fork upgrades — accept "an engineer is in the loop at upgrade time," or
  invest in moving fuel out of the engine tree (v2)? docs/forking.md draft is sketched in
  the B2 review §3.2 either way.
- P7 Which retrieval-protocol text is canonical (INDEX.md's frozen 4-step) — confirming
  1.3's fix direction.

**Trust/claims (B1):**
- P8 nature-skills attribution: record the absorbed MIT-era commit (needs archaeology in
  the June extraction history) — or re-derive those two files and drop the dependency?
- P9 "RovoDev supported" claim: narrow to registration+comms-polish (verified 2026-06-08)
  or schedule the 4-skill re-verification (#27) before the next release?

**Catalog philosophy (A2 hard question):**
- P10 Is the catalog optimizing prose quality or detecting AI provenance? (C11-class
  entries currently convert weak provenance signals into mandatory style edits; the answer
  drives which entries get validity conditions in 1.6's follow-up.)

## Sequencing note

Prose fixes (1.6–1.13) touch files that three open lanes also touch (comms-draft SKILL:
narrative lane; comms-polish SKILL: audit lane; voice-onboard SKILL: stylometry lane).
To avoid a fourth concurrent editor on the same files, the prose lane starts AFTER those
three lanes merge — or works stacked on the integration branch, whichever the owner's
merge order makes true. Release-hygiene items (1.14–1.18) are main-tree and independent.
