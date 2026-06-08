# Packaging & Publishing (maintainer note)

**Model: one source tree, read directly by every host.** There is no build/generate step.
The single source of truth is `skills/ai-writing-suite/`. Each host gets a tiny manifest that
*points at* that tree (or, for Cursor, copies it). Nothing is duplicated or generated, so there
is no sync-drift surface.

> This replaces the earlier generate-and-sync approach (`packaging/` + `sync.sh`), which was
> removed: its generated bodies were gitignored, which is what made v1 uninstallable.

## The four manifests

| File | Host | Role |
|---|---|---|
| `/.claude-plugin/marketplace.json` | Claude | Marketplace catalog; `plugins[].source = "./skills/ai-writing-suite"` |
| `/skills/ai-writing-suite/.claude-plugin/plugin.json` | Claude | Plugin identity (name, version, metadata) |
| `/.agents/plugins/marketplace.json` | Codex | Marketplace catalog; `plugins[].source = {source:"local", path:"./skills/ai-writing-suite"}` |
| `/skills/ai-writing-suite/.codex-plugin/plugin.json` | Codex | Plugin identity (+ `"skills": "./skills/"`, `interface{}`) |

Both root marketplaces point at the **same** source tree. Claude auto-discovers the sub-skills
under `skills/ai-writing-suite/skills/`; the root `SKILL.md` is a documentation router.

## Install (end users)

- **Claude:** `claude plugin marketplace add surahli123/ai-writing-suite` → `claude plugin install ai-writing-suite@ai-writing-suite`
- **Codex:** `codex plugin marketplace add surahli123/ai-writing-suite` → `codex plugin add ai-writing-suite@ai-writing-suite`
- **Cursor:** copy `skills/ai-writing-suite/` into `~/.cursor/skills/ai-writing-suite/` (or a project's `.cursor/skills/`). Cursor reads Anthropic-format `SKILL.md` Agent Skills natively; no manifest needed. (Not `.cursor/rules/*.mdc` — that is passive context injection, the wrong primitive for callable skills.)
- **RovoDev (experimental):** manual folder copy + **explicit** invocation (RovoDev does not auto-trigger). See "RovoDev — experimental manual install" below. On-device verification is required before relying on it; the nested sub-skill layout may need a flat repackage on builds that do not crawl nested skill dirs.

## Versioning / updates

The two `plugin.json` files (`.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`) are the
**authoritative version** (currently `1.0.0`). `SKILL.md` carries no version field, so there is one
version source per host and nothing to keep in lockstep with the body.

1. On a release, bump `"version"` in **both** `plugin.json` files together (keep them in parity).
2. Commit + push. Consumers refresh via `claude plugin update` / `codex plugin marketplace upgrade`.
3. (Optional) cut a git tag (`claude plugin tag` for Claude; a git tag for Codex `--ref` pinning)
   **after** verifying a real-remote install.

## Verify before publishing

- `claude plugin validate .` and `claude plugin validate skills/ai-writing-suite` (both must pass).
- Local install smoke per host (add the local path as a marketplace, install, confirm the skill
  loads, then remove — restore your config). For Cursor, validate the `SKILL.md` frontmatter `name:`
  matches each folder.
- **Local green ≠ remote-installable.** After pushing, run a real-remote smoke
  (`marketplace add surahli123/ai-writing-suite`) before tagging a release.

## Engine vs fuel

`_shared/patterns/` is the *engine* (de-AI rules) and must survive a KB swap. `_shared/knowledge/`
is the *fuel* — the generic OSS KB; a company fork drops its real playbook into the same slot
(never committed to this public repo).

## RovoDev — experimental manual install (pending on-device verification)

RovoDev is not yet a first-class target. There is no marketplace manifest for it; install is a
manual folder copy, the same primitive as Cursor. Two RovoDev facts shape this:

- **It does not auto-trigger skills** by description — you invoke explicitly (name the skill in
  your prompt). The router's "RovoDev — explicit intent routing" section is written for this.
- **It may not discover *nested* sub-skills.** RovoDev documents flat per-skill discovery
  (`skills/<name>/SKILL.md`); our sub-skills live one level deeper, under
  `skills/ai-writing-suite/skills/<name>/`. So it likely registers only the top-level router. The
  router is patched to be self-sufficient (it tells the agent to read the chosen sub-skill file on
  demand), which makes the nested layout work *if* the agent follows that step.

### Steps

1. Get the repo on the machine: `git clone https://github.com/surahli123/ai-writing-suite`
   (or copy the folder if cloning is blocked by corp policy).
2. Copy the suite into RovoDev's skills discovery directory (confirm the real path via `/skills`;
   common candidates are `~/.rovodev/skills/`, `~/.agents/skills/`, or a project `.rovodev/skills/`):

   ```
   cp -R ai-writing-suite/skills/ai-writing-suite ~/.rovodev/skills/ai-writing-suite
   ```

   The directory name **must** equal the frontmatter `name:` → `ai-writing-suite`.
3. Start a fresh RovoDev session, run `/skills`, and confirm `ai-writing-suite` is registered.
   (Expect only the router to appear, not the four sub-skills.)
4. Invoke explicitly, e.g.:

   > Use the ai-writing-suite skill. Rewrite this so it sounds less AI-generated; keep the facts
   > and my voice. Mode: rewrite. [paste draft]

### "Done" on RovoDev (verify, per the project's verify rule)

- `ai-writing-suite` shows up in `/skills`.
- An explicit `comms-polish` invocation produces a real **before/after** rewrite on a sample
  draft (loads + behavioural evidence, not "no error thrown").
- If the agent reads only the router and stops, prompt it to read
  `skills/ai-writing-suite/skills/comms-polish/SKILL.md` and its `_shared/patterns/` references,
  then re-run. Needing that by hand means the router self-sufficiency step is being skipped.

## Deferred (v2)

A flat RovoDev repackage (each sub-skill as its own top-level `skills/<name>/` dir with the needed
`_shared/` assets copied alongside) — **only** if on-device testing shows the self-sufficient
router is unreliable and RovoDev does not crawl the nested tree. Keep it RovoDev-specific; do not
disturb the nested Claude/Cursor layout that already works.
