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

**Manifest status (Claude): VERIFIED 2026-06-06** against
`code.claude.com/docs/en/plugins-reference.md` + `/plugin-marketplaces.md`.
`.claude-plugin/plugin.json` — only `name` is required; `description`, `version`,
`author` (object `{name, email?, url?}`), `homepage`, `repository`, `license`,
`keywords` are valid optionals. The earlier `"skills": "./skills/"` field was
**removed** — Claude auto-discovers the `skills/` directory, so that field was
redundant (the `skills` field is only for *custom* paths in addition to the
default). `.claude-plugin/marketplace.json` is correct as-is (`name` + `owner` +
`plugins[]` required; `source` must start with `./`; `$schema` is editor-only,
ignored at load). Validate before publishing with: `claude plugin validate .`

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

**Manifest status (Codex): VERIFIED 2026-06-06 — current layout is NON-CONFORMANT.**
The `codex` CLI (codex-cli 0.137.0) uses a **marketplace** model:
`codex plugin marketplace add <local|owner/repo|git-url>` → `codex plugin add <plugin>`.
A live test (`codex plugin marketplace add ./packaging/codex`) was **rejected**:

    Error: invalid marketplace file .../packaging/codex: marketplace root does not
    contain a supported manifest

Ground truth, from a working marketplace (`~/.codex/.tmp/marketplaces/claude-plugin-codex`)
and the `nature-skills` repo, the required structure is:

    <marketplace-root>/
    ├── .agents/plugins/marketplace.json   # MARKETPLACE manifest (REQUIRED)
    └── plugins/<plugin-name>/
        ├── .codex-plugin/plugin.json      # plugin manifest
        ├── skills/  _shared/  ...         # plugin content
        └── SKILL.md  NOTICE.md  ...

`.agents/plugins/marketplace.json` shape (from nature-skills):

    { "name": "<marketplace>", "interface": {"displayName": "..."},
      "plugins": [ { "name": "<plugin>",
                     "source": {"source": "local", "path": "./plugins/<plugin>"},
                     "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
                     "category": "..." } ] }

Our current `packaging/codex/` (bare `.codex-plugin/plugin.json` at root, content
alongside) does NOT match — it lacks `.agents/plugins/marketplace.json` and the
`plugins/<name>/` nesting. **TODO before Codex publish:** either (a) restructure
the codex target to the layout above, or (b) use a Claude→Codex bridge (there is a
`claude-plugin-codex` marketplace that converts Claude plugins to Codex — our Claude
plugin already validates, so the bridge may be the lower-effort path). The plugin.json
itself (`name`/`description`/`version`/...) is fine; only the *packaging shape* is wrong.

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
