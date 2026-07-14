# Adversarial Review — Synthesis (commit 8c612d8)

VERIFIED_AGAINST: `feat/make-v1-installable-3hosts` @ `8c612d8` @ 2026-06-07
Reviewer: Codex `gpt-5.5`, read-only, independent context. Raw log: `reviews/2026-06-07-make-v1-installable.md`.

**Caveat:** the Codex run hit the 10-min cap before emitting its formal BLOCKER/CONCERN/SUGGESTION
block, and the two sub-agent "lanes" it tried to spawn failed on an unrelated MCP/OAuth transport
error. Findings below are extracted from its **grounded reasoning trace** — each backed by a command
it actually ran against HEAD — plus my own disk-arbitration (cross-review protocol Step 3/5).

## Verdict: no BLOCKER. 1 CONCERN (conscious-accept), 1 SUGGESTION.

### BLOCKER — none
- Codex found no path/resolution bug. Confirmed the Claude marketplace `source: "./skills/ai-writing-suite"`
  is valid and (web-checked Claude docs) a relative plugin dir is an accepted source.
- `diff --exclude` **works** on this macOS diff build — Codex explicitly declined to overstate it as a
  portability blocker after testing it live.
- Codex never produced a SHA/symbol mis-attribution (protocol Step 5: clean).

### CONCERN — Claude ships a nested duplicate of the suite
- **What:** Claude's plugin = the whole `skills/ai-writing-suite/` tree. We committed the Codex body at
  `skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/`, so Claude consumers receive a
  **full second copy of the suite (~33 files)** nested inside the plugin's `packaging/` dir.
- **Not functionally breaking (verified):** my Claude install smoke discovered **exactly 4 skills, not 8** —
  Claude's discovery is shallow, so the nested copy is inert. Install works; ~361 tok always-on.
- **But:** it is bloat + an unprofessional self-nested artifact shipped to Claude users, on top of the
  `evals/` + `packaging/` bloat already accepted under the Option-A "ship the source tree" choice.
- **Disk-arbitration:** `git ls-files skills/ai-writing-suite/packaging/codex/plugins/ai-writing-suite/skills`
  confirms the copied sub-skills exist under the Claude-plugin tree. Concern is real at the repo level.
- **Options:** (a) **accept for v1** + a v2 follow-up to de-nest `packaging/` out of the published plugin
  dir; (b) restructure now (relocate Codex packaging to repo root, change the Codex `--sparse` path,
  re-smoke). **Rec: (a)** — functional, within the accepted Option-A tradeoff, keeps v1 moving.

### SUGGESTION — trailing whitespace in NOTICE.md
- `git diff --check main..HEAD` exits 2 on trailing whitespace in NOTICE.md. These are **intentional
  markdown hard-breaks** (two trailing spaces) in the pre-existing source `NOTICE.md`, now surfaced
  because the generated copy was committed. Low priority. Rec: leave (intentional) or convert to `\`
  breaks later; note for any future CI whitespace lint.

## Hard questions Codex pressed (my answers)
1. **"Installable first version but a stale-update trap?"** — Updates aren't automatic: a consumer
   re-runs `claude plugin update` / `marketplace update`. v1 is `1.0.0`; the packaging README documents
   the bump path (SKILL.md frontmatter + the two `plugin.json` + re-sync). No silent-stale risk for v1.
2. **"Does Claude double-discover the nested copy?"** — Empirically **NO** (smoke = 4 skills). Verified.

## Net
Mergeable. The one CONCERN is a conscious-accept decision for the owner (de-nest now vs v2 follow-up).
