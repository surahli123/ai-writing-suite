# Packaging — AI Writing Suite

## Single Source of Truth

All skill logic lives under `skills/ai-writing-suite/` (one level up from this
directory). Everything inside `packaging/claude/` and `packaging/codex/` is
**generated** by `sync.sh`. Do not hand-edit generated packages.

```
skills/ai-writing-suite/   ← SOURCE (edit here)
    SKILL.md
    skills/
    _shared/
    NOTICE.md  LICENSE  README.md  CHANGELOG.md
    packaging/
        sync.sh            ← assembler
        claude/            ← GENERATED (Claude target)
        codex/             ← GENERATED (Codex target)
```

> **WARNING: Do NOT hand-edit files inside `packaging/claude/` or
> `packaging/codex/`. Those directories are wiped and regenerated every time
> `sync.sh` runs. Any manual edits will be silently lost. Edit the source and
> re-run sync instead.**
>
> This rule implements design decision R4 ("avoid 4-surface sync drift") from
> `docs/design-ai-writing-suite-v1-2026-06-06.md`.

---

## How sync works

```
bash packaging/sync.sh            # from repo root or from packaging/
bash packaging/sync.sh --dry-run  # preview what would be copied, nothing written
```

For each target (`claude`, `codex`) the script:

1. **Wipes** the previously-generated `skills/` and `_shared/` dirs inside the
   target so deletions in the source propagate cleanly.
2. **Copies** top-level files (`SKILL.md`, `NOTICE.md`, `LICENSE`, `README.md`,
   `CHANGELOG.md`) from source → target.
3. **Copies** `skills/` and `_shared/` trees recursively from source → target.
4. **Version-checks** the target's plugin manifest (`plugin.json`) against the
   `version:` field in the source `SKILL.md` frontmatter and warns if they
   disagree.

The manifest directories (`.claude-plugin/`, `.codex-plugin/`) are **not**
wiped — they contain the host-specific manifests that are maintained manually
(see §Manifest files below).

Idempotent: running sync.sh twice produces the same result.
No external dependencies: pure bash + cp + mkdir + python3 (stdlib only, for
JSON version check).

---

## Target layouts

### Claude (`packaging/claude/`)

```
claude/
├── .claude-plugin/
│   ├── plugin.json        # Claude plugin manifest (maintained manually)
│   └── marketplace.json   # Claude marketplace listing (maintained manually)
├── SKILL.md               # generated — router
├── skills/                # generated — sub-skills
│   ├── comms-polish/
│   ├── voice-onboard/
│   ├── comms-qa/          (stub, v2)
│   └── comms-draft/       (stub, v2)
├── _shared/               # generated — patterns, KB, voice-profile
├── NOTICE.md              # generated
├── LICENSE                # generated
├── README.md              # generated
└── CHANGELOG.md           # generated
```

**Manifest assumption (Claude):** The `.claude-plugin/plugin.json` format
follows the `avoid-ai-writing` and `nature-skills` conventions: flat JSON with
`name`, `description`, `version`, `author`, `homepage`, `repository`,
`license`, `keywords`, and `skills` (path to skills dir). The
`.claude-plugin/marketplace.json` uses the
`https://json.schemastore.org/claude-code-marketplace.json` schema with a
`plugins[]` array listing source paths. **Confirm with Claude Code plugin
documentation before publishing** — this format may change.

### Codex (`packaging/codex/`)

```
codex/
├── .codex-plugin/
│   └── plugin.json        # Codex plugin manifest (maintained manually)
├── SKILL.md               # generated — router
├── skills/                # generated — sub-skills
│   ├── comms-polish/
│   ├── voice-onboard/
│   ├── comms-qa/          (stub, v2)
│   └── comms-draft/       (stub, v2)
├── _shared/               # generated — patterns, KB, voice-profile
├── NOTICE.md              # generated
├── LICENSE                # generated
├── README.md              # generated
└── CHANGELOG.md           # generated
```

**Manifest assumption (Codex):** The `.codex-plugin/plugin.json` format mirrors
the `.claude-plugin/plugin.json` structure (same fields), following the
`nature-skills` Codex plugin convention. **Confirm with OpenAI Codex / codex
CLI plugin documentation before publishing** — the Codex plugin spec is not
publicly stable as of the writing date (2026-06-06). The `skills` field points
to `./skills/` as the sub-skill directory.

---

## Manifest files (maintained manually)

These files live in the manifest dirs and are NOT overwritten by sync:

| File | Purpose | Edit when |
|---|---|---|
| `claude/.claude-plugin/plugin.json` | Claude plugin identity | version bump, metadata change |
| `claude/.claude-plugin/marketplace.json` | Claude marketplace listing | name/description/category change |
| `codex/.codex-plugin/plugin.json` | Codex plugin identity | version bump, metadata change |

When bumping the skill version:
1. Update `version:` in source `SKILL.md` frontmatter.
2. Update `"version"` in all three manifest files above.
3. Run `bash packaging/sync.sh` — it will confirm version parity.

---

## Deferred targets (v2)

Cursor (`.cursor/rules/` + `.mdc` file) and RovoDev packaging are deferred to
v2 per owner decision (2026-06-06). When added, they follow the same pattern:
sync.sh gains a new `sync_target` call; the new target dir gets a manually-
maintained manifest; generated content is never hand-edited.
