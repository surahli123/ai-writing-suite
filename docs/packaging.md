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

## Deferred (v2)

RovoDev packaging. It will follow the same source-pointing model (explicit intent routing via the
suite router, since RovoDev does not auto-trigger skills).
