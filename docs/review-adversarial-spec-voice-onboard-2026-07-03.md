# Adversarial Spec Review — voice-onboard B+C (result)

- **Date:** 2026-07-03
- **Reviewed:** `docs/design-voice-onboard-exemplars-hardrules-2026-07-03.md`
- **Method:** Workflow-orchestrated OMC panel — 4 adversarial lenses (1× `oh-my-claudecode:architect`
  + 3× `oh-my-claudecode:critic`, all Opus), each grounded in the real repo files (not just the spec).
  Every raised finding then passed through an independent **refute** agent (default-to-false). 25 agents,
  0 errors, ~1.85M tokens.
- **Raw result:** 21 findings raised, **0 survived refutation.**

## Verdict

**SOUND — no BLOCKER or CONCERN survives.** The spec is internally consistent and consistent with the
repo it will modify. No must-fix defect before "go".

**Why the 0-survivor result is trustworthy (not a rubber stamp):**
- Reviewers raised 21 *substantive* findings with specific `file:line` citations — they engaged, they
  didn't wave it through.
- Refutations are specific, not hand-wavy; several even corrected the *reviewers'* own miscitations
  (e.g. the "Not X, but Y" line is voice-profile `L96`, not `L92`).
- The findings died on concrete grounds (misread of an LLM-instruction as code, a scenario the spec
  already forecloses, a behavior already shipped in v1.1), not on reviewer laziness.

**Scope limit (important):** this pass verified the spec's *internal soundness* and its *consistency with
repo reality*. It did **not** — and could not — verify runtime behavior. Whether exemplars+rules actually
improve voice-match is the **quality question the spec deliberately defers** (§6.2, blocked on 16-24 real
drafts / P3). "Sound spec" ≠ "feature works". That gap is disclosed, not hidden.

## Residuals worth folding in (SUGGESTION-level, surfaced by the refutations)

None of these block "go", but the refuters themselves flagged them as cheap improvements.

| # | Residual | Origin finding (lens) | Recommendation |
|---|---|---|---|
| **R1** | Spec §6.1 says "existing **65**-test suite"; a reviewer ran `pytest --collect-only` → **78**. Stale factual claim. | eval-rigor | **Apply now** — change to 78 / "the existing stdlib suite". |
| **R2** | Spec invents a `None yet` degrade sentinel, but the repo already ships an in-band empty-marker convention: `Unknown — not enough signal`. Inconsistent. | contract | **Apply now** — align to the existing `Unknown` convention + add one clause "a `None yet`/`Unknown` body is treated as absent". |
| **R3** | §5.1's example rule "*Never open with a rhetorical contrast*" would negate the shipped **Sam** profile's Signature Move "*Not X, but Y*" — the spec's own example contradicts its own sample. | contract | **Apply now** — swap for a Sam-consistent example (e.g. "*Never use hype words like 'unlock'/'amazing'*", which is in Sam's `Vocabulary Don't`). |
| **R4** | No explicit "no same-genre exemplar → skip the few-shot, note it, never cross-genre substitute" line. **3 independent reviewers tripped on this** → real readers will too. | contract + scope + guardrail | **Apply now** — add one degradation line at §5.4/§5.5. |
| **R5** | Anti-copy has no mechanical check. A **copy-rate / longest-shared-span overlap** fixture is seedable with *synthetic* same-genre inputs — it does **not** need the 16-24 real drafts, so it partially un-blocks the anti-copy guarantee from P3. | eval-rigor + guardrail | **Add to §6.2** as a 3rd quality-fixture dimension (synthetic-seedable, runnable before real drafts). |
| **R6** | §6.1's header-presence test should name `voice-profile.md` (the file consumers read) as its target and note the option to extend the existing `REQUIRED_HEADERS` guard. | eval-rigor + scope | **Note for writing-plans** (byte-exact, deferred by design). |
| **R7** | §2's philosophy sentence invites the "C is half-baked without F" misread; C actually distills from **presence + absence + human judgment**, not pure absence-mining. | scope | **Optional wording tighten** in §2. |
| **R8** | Consumers read the profile "when present" with no check for the *unreplaced* sample; a user who forgets to run voice-onboard gets Sam's voice. **Pre-existing** (the 10 descriptive dims already leak Sam), not introduced by B+C. | guardrail | **Optional pre-existing hardening** — tell consumers to detect the "STATUS: example only" marker and warn. Out of scope for B+C. |

**Recommended action:** fold **R1-R4** into both spec versions now (pure doc-accuracy/consistency polish),
add **R5** to §6.2 (a genuine, cheap de-risk of the one guardrail with no mechanical check), note R6-R7
for the writing-plans stage, and file R8 as a separate pre-existing hardening ticket. Then the spec is
"go"-ready.

## Audit trail — all 21 findings (raised → dropped)

Every finding was raised at CONCERN or SUGGESTION (no BLOCKER was even raised) and refuted. Condensed:

**contract-correctness (architect):**
1. Same-genre exemplar has no shared genre vocabulary → *LLM semantic match, not a code join; open vocab is intentional; silent-skip is designed degradation.* Residual → R4.
2. Precedence leaves Hard-Rule-vs-dimension undefined; example contradicts Sam → *the "rhetorical contrast" string is a format demo, not an extracted rule; real generic-tell-vs-signature-move tension is resolved by §5.6.* Residual → R3.
3. `None yet` sentinel present-but-empty, untested → *identical class to the shipped `Unknown` marker; consumers are LLMs, not parsers.* Residual → R2.
4. "10 dims map 1:1 to headers" goes stale; template insert point unspecified → *already 13 headers today; contract read by name not position; byte-exact deferred.*

**scope-yagni-owner-fit (critic):**
5. C half-baked without F → *C sources from Don't + Things-To-Avoid + Signature-Moves (presence too), human-gated; not pure absence-mining.* Residual → R7.
6. Test scope undersold (must modify `test_voice_contract.py`) → *§6.1 already mandates the tripwire; can be an add-only new test.* Residual → R6.
7. Exemplar genre-tag not pinned to preset vocab → *the two vocabularies are orthogonal by design; pinning them would backfire.* Residual → R4.
8. 2×2 wiring vs two high-value cells → *`价值最高` is a fit-ranking not a scope boundary; cross-cells are mechanically native + near-zero cost; owner approved X1.*
9. "Small cut" undersells a 6-file contract evolution → *§1 states the producer→consumer change up front; §5/§7/§8 disclose the full surface.*

**eval-verification-rigor (critic):**
10. Structural tests can only verify text (anti-copy/advisory untestable) → *§6.1 explicitly labels them "text present"/"wired"; §6.2 is the deferred behavioral tier — disclosed, not hidden.*
11. Cheap proxies lumped into P3 → *the proxies need a live model run (not stdlib); one-fictional-profile run is the broken ruler the owner forbids.* Residual → R5.
12. 1.2.0 "acceptance" gate undefined → *owner sign-off is the gate (doc is owner-gated throughout); changelog line is descriptive-wiring, not a quality claim.*
13. Structural test targets wrong file; `REQUIRED_HEADERS` not updated → *§6.1 bullet 1 already guards `voice-profile.md` (the file consumers read).* Residual → R6.
14. Stale "65-test suite" → *verified 78; but non-load-bearing parenthetical.* Residual → R1.

**guardrail-failuremodes (critic):**
15. Anti-copy = instruction with zero verification → *same class as "no fabrication" (the suite's hardest rule, also instruction+deferred-judge); §6.1 doesn't overclaim.* Residual → R5.
16. "Advisory" collapses to gating in the autonomous loop → *advisory = don't-block + yield-to-facts (real distinction); it's the shipped comms-polish loop; Hard Rules are less aggressive than other profile fields; the flatten scenario is foreclosed by §5.1+§5.6+author-confirm.*
17. Fictional-Sam exemplars leak into real output → *anti-copy guardrail at both points; worst harm is contingent on Finding-15; style-bias toward Sam already exists via the 10 dims (pre-existing).* Residual → R8.
18. Genre-match under-specified, no fallback → *"same-genre" appears 3× in the spec; cross-genre substitution is foreclosed, not invited.* Residual → R4.
19. No staleness/expiry for hard rules → *re-onboard re-runs Step 2 (re-derive) + Step 4 (overwrite-with-diff); no merge path exists; advisory contains any stale rule.*
20. "Why gold" has no validation → *it's a one-line hint, not the anchor (the verbatim sample is); validated by the human gate; per-sample not statistical by design.*
21. §5.6 cites `LR-000`, a retired "do not apply" example → *"do not apply" = runtime, not citation; LR-000 is the only entry illustrating the principle; source self-labels so it can't durably mislead.*
