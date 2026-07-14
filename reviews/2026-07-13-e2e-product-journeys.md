# E2E Product Review (B2) — first-run & fork journeys

Reviewer: Fable 5 subagent (independent context, read-only; took over after Codex timed out twice on this slice). Date: 2026-07-13. VERDICT: JOURNEYS FIX-FIRST
Scope: README newcomer path; fork journey against feat/kb-ingestion-tooling @ 45968bd (steps executed in scratch, not inferred); upgrade story.

---

## Summary

The engine under review is better than its paperwork. The KB tools (branch HEAD 45968bd) are genuinely well-built — the validator's file:line FAIL loop carried a simulated non-engineer to PASS in 3 iterations — but the fork journey has one silent product-level failure the validator cannot see (generic-KB shadowing), one falsified doc claim (re-run idempotency), and zero discoverability. The README's capability story contradicts itself between root and suite, and **no upgrade path for forks exists in any shipped doc**. Verdict: FIX-FIRST.

All claims below are from code I read and commands I ran in scratch space (branch tree materialized via `git archive`); transcripts abbreviated at bottom. Paths are repo-relative; worktree root `/Users/surahli/Documents/ai-writing-suite/.claude/worktrees/agent-ac2df9a7cc46f5c3a`.

---

## Area 1 — README as a newcomer

**1.1 CONCERN — Root README understates what's shipped, contradicting the suite README.** `README.md:27` says "`comms-qa` (KB Q&A) and `comms-draft` are v2 stubs"; `README.md:16-17` label them "(v2)"; `README.md:84` says "* = v2 stub". But the current tree ships both as working skills: `skills/ai-writing-suite/README.md:19-20` says v1.1, `skills/ai-writing-suite/CHANGELOG.md:72,82` says "the placeholder is now a working ... sub-skill", and `skills/comms-qa/SKILL.md` is a full implementation. A newcomer's first confusion is "which README is lying?" Fix: rewrite the root Status paragraph and layout comment to v1.1 reality.

**1.2 CONCERN — Version/tag drift undermines both the newcomer and the upgrade story.** `.claude-plugin/plugin.json:4` still `1.0.0`; only `v1.0.0` tags exist (`git tag`), while CHANGELOG's `[Unreleased]` carries the v1.1 features. Matches plan item #26 (`docs/improvement-plan-deslop-landscape-2026-07-11.md:130`). Fix: cut v1.1.0 (both plugin.json files + tag) — it is also the prerequisite for any fork pinning (Area 3).

**1.3 Branch-only features: no overclaim found.** Root and suite READMEs mention none of: audit contract, narrative-shape, stylometric fingerprint, KB tools. Clean — the failure is the mirror image (Area 2.1: the KB tools are invisible even where they should be announced).

**1.4 Eval claims vs the honest-wording rule: compliant, with two nits.** The word "behavioral" appears nowhere in shipped README/CHANGELOG (grep clean; it lives only on the unmerged behavioral-evals branch). I ran the newcomer verify path: `bash evals/run_all.sh` → "Naive-baseline miss rate: 3/8 = 38% ... ALL CHECKS PASSED" — so the 30-40% calibration claim at `skills/ai-writing-suite/README.md:223` is substantiated by output, not just asserted. Nits: (a) `README.md:223` "LLM-judged scoring" omits that the judge is opt-in and never gates CI (`evals/README.md` says it honestly — "SKIPPED unless AIWS_JUDGE_* is set"); one clause fixes it. (b) Internal contradiction: `skills/ai-writing-suite/README.md:127` says approve-then-eval-test, `:225` says "eval-tested before you approve it". Pick one.

**1.5 SUGGESTION — No true 10-minute quickstart at root.** `README.md:38-67` has install commands (three hosts — commands themselves NOT VERIFIED here; running them would modify host config) but no paste-and-go first prompt; the first "try this" lives at `skills/ai-writing-suite/README.md:185-200`. Add one example + expected shape of output to the root README.

---

## Area 2 — Fork journey (branch `feat/kb-ingestion-tooling` @ 45968bd)

**2.1 BLOCKER — The onboarding funnel has no entrance.** `git grep kb-onboarding|kb_ingest|kb_validate` across the branch's `README.md`, suite README, CHANGELOG, and `_shared/knowledge/README.md` returns nothing — the branch adds only the 4 files (`git diff main feat/kb-ingestion-tooling --stat`). A fork owner reading any README never learns the tools or the doc exist; Cursor/RovoDev copies (`cp -R .../skills/ai-writing-suite`) exclude `docs/` entirely. Fix: a "Forking: bring your playbook" section in the root README + a pointer in `_shared/knowledge/README.md` + a CHANGELOG entry, in the same PR as the merge.

**2.2 CONCERN — The idempotency promise is false on the collision path (executed, not inferred).** `docs/kb-onboarding.md:83-84` (branch): "Re-running with the same export is safe: identical input produces identical output." My run: a page titled "Tone" collided with the shipped generic `tone.md` → correctly written as `tone-2.md`; re-running the same export minted **`tone-3.md`**. Root cause: `kb_ingest.py:539-541` checks provenance only at the original slug path (`dest_initial` = `tone.md`, whose provenance is None), never at previously auto-renamed `-N` siblings — so every re-ingest of a colliding page appends another `tone-N.md`. Step 5 explicitly sends users back to Step 1 (`kb-onboarding.md:198`), so re-ingestion is the designed loop. Fix: before renaming, scan existing `stem-N.md` files for a provenance match to `src_name`; correct the doc sentence either way.

**2.3 CONCERN — Generic-KB coexistence silently hijacks retrieval, and PASS doesn't catch it.** The doc never says whether to delete or keep the 5 shipped generic entries; ingest merges into them. Measured after reaching validator PASS: query "how should our team sound when writing to execs?" retrieves generic `tone.md`, not the company's tone page — `comms-qa` will present OSS boilerplate as "the playbook", the exact failure `kb-onboarding.md:10-11` warns about. The validator structurally cannot see this: check 9 (`kb_validate.py:189-245`) tests each entry's *own* keywords only, so a richer generic entry shadows real user phrasings invisibly. Fix: a Step-0 decision in the doc ("replace or augment the generic KB — most forks should delete `audience/clarity/structure/tone/revision.md` + their rows"), and ideally a validator WARN when a kb_ingest-produced entry is beaten by a non-provenance entry on its title words. Also soften `kb_validate.py:295` "KB is ready for first use" — it is necessary, not sufficient.

**2.4 CONCERN — Ingest silently destroys the shipped INDEX.md header.** First run replaced the shipped index's "Categories" and "Provenance" sections and its 4-step protocol with kb_ingest's own 3-step `INDEX_HEADER` (`kb_ingest.py:414-438`; only table rows survive via `parse_existing_index_rows`). `kb-onboarding.md:75` "It never overwrites an entry you have already edited" reads to a non-engineer as covering INDEX.md prose; it doesn't. Also incoherent with "the retrieval protocol itself is frozen" (`kb_ingest.py:19-20`) — the tool overwrites the canonical protocol text with a divergent copy. Fix: preserve non-table INDEX content, or state the limitation in doc + run report.

**2.5 SUGGESTION — First-error ergonomics.** Most likely first error (running from repo root, where `git clone` leaves you): raw interpreter output `can't open file '.../skills/tools/kb_ingest.py': [Errno 2] No such file or directory` — no doc coverage; the doc shows FAIL examples for validate but nothing for ingest errors, `python` vs `python3` (`command not found: python` on macOS), or Windows (`py -3`). A 5-row troubleshooting table fixes this. Note: `kb-onboarding.md:216` "run the same on Claude, Codex, Cursor, and RovoDev" — hosts, not OSes; Windows is unaddressed.

**2.6 SUGGESTION — Dual bookkeeping is the most error-prone human step.** `kb-onboarding.md:129` requires editing Keywords in *both* the `kb-entry-meta` block and the INDEX row. Editing only the file fails check 7 with a message ("INDEX Keywords ... missing word(s)") that doesn't say which side to fix. One sentence in the TODO table ("add the word to the INDEX row") closes it.

**2.7 What's genuinely good (state it so it survives the merge debate):** validator messages are excellent (file:line, tie/shadow detection at `kb_validate.py:237-241`, dead-INDEX-row detection when I deleted `tone-3.md`); the Step3↔4 loop converges; exit codes correct; collision safety and hand-edited-row preservation behaved exactly as documented; a careful non-engineer *can* reach PASS. The doc's promised output strings match the code (`kb_validate.py:295` vs `kb-onboarding.md:179`).

---

## Area 3 — Upgrade story (fork takes v1.2.0 later)

**3.1 BLOCKER — No documented path exists. Plainly: nothing.** Searched all shipped docs (root README, suite README, `docs/packaging.md`, CHANGELOG, branch `kb-onboarding.md`, `_shared/knowledge/INDEX.md`) for merge/pin/rebase/upstream guidance. The only hits — `docs/packaging.md:37-38` — cover plugin-*consumer* refresh (`claude plugin update`, tag `--ref` pinning) and are maintainer-facing. The fork's structural problem is worse than a missing paragraph: **the fuel lives inside the engine tree.** `_shared/knowledge/` — and one shared file, `INDEX.md` — is simultaneously fork-owned (playbook rows) and upstream-owned (generic entries, header prose, protocol text). Every upstream release touching the generic KB guarantees merge conflicts in the fork's most important file, and kb_ingest's header rewrite (2.4) maximizes the diff. The onboarding doc's promise — "you add data, not engineering" (`kb-onboarding.md:6`, echoing repo CLAUDE.md) — holds for day 1 and breaks at the first upgrade, which is a git merge with guaranteed conflicts.

**3.2 Proposed minimal honest doc — `docs/forking.md` (~1 page):**
1. **Fork model:** git-fork the repo; install from *your* fork's marketplace path; pin to an upstream tag, never track `main`. (Prereq: cut v1.1.0 — only `v1.0.0` tags exist today.)
2. **Upgrade recipe:** `git fetch upstream && git merge v1.2.0`; expect conflicts confined to `_shared/knowledge/` if you replaced the generic KB — resolve with `git checkout --ours -- _shared/knowledge/` when your playbook fully replaced it; then re-run `kb_validate.py` + the Step-5 smoke before shipping.
3. **What upstream guarantees stable across minor releases** (needs owner sign-off, but the code already half-promises it): the INDEX.md row schema + retrieval protocol and the `kb-entry-meta` header — both declared "FROZEN" at `kb_ingest.py:19-20` and in the INDEX header; promote that from docstring folklore to a documented contract. `_shared/` filenames/paths (`voice-profile.md`, `learned-rules.md`) likewise. **Explicitly NOT stable:** pattern/tell IDs in `_shared/patterns/` — no stability promise exists anywhere today, so the doc should say "may change between minors" rather than invent one.
4. **What the fork must never edit** (engine: `skills/*/SKILL.md`, `evals/`, `_shared/patterns/`) so merges stay trivial.
5. Flag as v2 option: move fuel out of the engine directory (fork-gitignored KB dir + pointer), which deletes the conflict surface permanently.

---

## Transcript A — newcomer (abbreviated)

Read `README.md` → engine-vs-fuel framing lands well → Status (`:24-27`): comms-qa/draft are "v2 stubs" → install commands copied (not executed; NOT VERIFIED) → opened `skills/ai-writing-suite/README.md:19-20`: comms-qa/draft are v1.1, shipped. **FIRST FAILURE: `README.md:27` vs `skills/ai-writing-suite/README.md:19-20` — the two READMEs disagree about what I just installed; no error message, just lost trust.** Recovery path exists (CHANGELOG settles it) but nothing points there. Verify path `bash evals/run_all.sh` → "ALL CHECKS PASSED", calibration 38% in band — worked first try.

## Transcript B — fork data-person (abbreviated)

Exported 3 pages (1 Confluence HTML incl. space-in-filename — handled fine, 2 md) → `cd skills/ai-writing-suite` → ingest → clear report, 5 TODOs → page titled "Tone" collided with generic `tone.md` → `tone-2.md`. Re-ran after adding a page (doc's Step-5→Step-1 loop): **FIRST FAILURE: `tone-3.md` minted — same source, third file; doc's `kb-onboarding.md:83` says this can't happen; the doc's only advice is the duplicate-TODO row, which doesn't explain why the duplicate keeps coming back.** Validate → FAIL 3/9 with precise file:line → deleted `tone-3.md` → validator caught the dead INDEX row → renamed per doc (4 coordinated edits across 3 files + INDEX) → dual-bookkeeping keyword edits → **PASS after 3 validate runs (~35 min equivalent).** Post-PASS probe: "how should our team sound when writing to execs?" → retrieves generic `tone.md`, not the company page — the wrong-playbook failure, invisible to the PASS gate.

## Hard questions

1. **Should a fork keep the generic KB at all?** If the real answer is "replace it," why does ingest merge into it by default and the doc never mention deletion? Answering this decides fix 2.3 — and it's a product decision, not an engineering one.
2. **Who owns upgrades?** The doc promises "data, not engineering," but taking v1.2.0 is a git merge with guaranteed INDEX.md conflicts. Either name the engineer in the fork loop honestly, or move the fuel out of the engine tree. Which is the bet?
3. **Which retrieval-protocol text is canonical?** INDEX.md says the protocol is frozen; kb_ingest overwrites it with its own divergent 3-step copy on every first ingest. If it's frozen, the tool must not rewrite it.

Risk lines: install commands for Claude/Codex marketplaces are unverified here (register c); my fork simulation used a 3-page export — very large Confluence space exports (nested dirs, `index.html`, attachments) go beyond `_discover_inputs`'s flat, top-level-only scan (`kb_ingest.py:464-476`) and were not exercised.

JOURNEYS: FIX-FIRST