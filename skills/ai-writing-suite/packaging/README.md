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
        claude/            ← Claude target (generated content + manual manifests)
        codex/             ← Codex marketplace (manual manifests; generated
                             content under plugins/ai-writing-suite/)
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

For each target the script copies generated content into a per-target
**content root**:

- Claude content root → `packaging/claude/` (content sits at the marketplace root).
- Codex content root → `packaging/codex/plugins/ai-writing-suite/` (content sits
  inside the plugin; `packaging/codex/` itself is the *marketplace* root, not the
  plugin — see §Codex layout).

Into that content root the script:

1. **Wipes** the previously-generated `skills/` and `_shared/` dirs so deletions
   in the source propagate cleanly.
2. **Copies** top-level files (`SKILL.md`, `NOTICE.md`, `LICENSE`, `README.md`,
   `CHANGELOG.md`) from source → content root.
3. **Copies** `skills/` and `_shared/` trees recursively from source → content root.
4. **Version-checks** the target's plugin manifest (`plugin.json`) against the
   `version:` field in the source `SKILL.md` frontmatter and warns if they
   disagree.

The manifest files/dirs are **not** wiped — they are maintained manually
(see §Manifest files below):

- Claude: `packaging/claude/.claude-plugin/`.
- Codex: `packaging/codex/.agents/plugins/marketplace.json` (marketplace manifest)
  and `packaging/codex/plugins/ai-writing-suite/.codex-plugin/plugin.json` (plugin
  manifest). The wipe only touches `plugins/ai-writing-suite/{skills,_shared}`, so
  both manifests survive every sync.

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

`packaging/codex/` is a **marketplace** that contains one **plugin**. The
marketplace manifest lives at the root; the plugin (manifest + all generated
content) lives under `plugins/ai-writing-suite/`.

```
codex/                                       # marketplace root
├── .agents/plugins/marketplace.json         # marketplace manifest (maintained manually)
└── plugins/ai-writing-suite/                # the plugin
    ├── .codex-plugin/plugin.json            # plugin manifest (maintained manually)
    ├── SKILL.md                             # generated — router
    ├── skills/                              # generated — sub-skills
    │   ├── comms-polish/
    │   ├── voice-onboard/
    │   ├── comms-qa/          (stub, v2)
    │   └── comms-draft/       (stub, v2)
    ├── _shared/                             # generated — patterns, KB, voice-profile
    ├── NOTICE.md                            # generated
    ├── LICENSE                              # generated
    ├── README.md                            # generated
    └── CHANGELOG.md                         # generated
```

**Manifest status (Codex): CONFORMANT — restructured 2026-06-06.**
The `codex` CLI (codex-cli 0.137.0) uses a **marketplace** model:
`codex plugin marketplace add <local|owner/repo|git-url>` → `codex plugin add <plugin>`.
The earlier bare-`.codex-plugin/plugin.json`-at-root layout was rejected with:

    Error: invalid marketplace file .../packaging/codex: marketplace root does not
    contain a supported manifest

The layout above is the verified-conformant shape, matching a working marketplace
(`~/.codex/.tmp/marketplaces/claude-plugin-codex`) and the `nature-skills` repo:

    <marketplace-root>/
    ├── .agents/plugins/marketplace.json   # MARKETPLACE manifest (REQUIRED)
    └── plugins/<plugin-name>/
        ├── .codex-plugin/plugin.json      # plugin manifest
        ├── skills/  _shared/  ...         # plugin content
        └── SKILL.md  NOTICE.md  ...

Two manifests are maintained by hand (sync.sh never touches them):

- `codex/.agents/plugins/marketplace.json` — marketplace manifest. Shape:
  `{ "name", "interface": {"displayName"}, "plugins": [ { "name",
  "source": {"source":"local","path":"./plugins/ai-writing-suite"},
  "policy": {"installation":"AVAILABLE","authentication":"ON_INSTALL"},
  "category" } ] }`.
- `codex/plugins/ai-writing-suite/.codex-plugin/plugin.json` — plugin manifest.
  Same identity fields as Claude, but it **keeps** `"skills": "./skills/"` (Codex
  uses it; Claude does not) and adds an `interface` block (`displayName`,
  `shortDescription`, `longDescription`, `developerName`, `category`,
  `capabilities`).

Generated content (`SKILL.md`, `skills/`, `_shared/`, `NOTICE.md`, `LICENSE`,
`README.md`, `CHANGELOG.md`) lands under `plugins/ai-writing-suite/` via sync.sh.
Add to a local marketplace with:
`codex plugin marketplace add ./skills/ai-writing-suite/packaging/codex`.

---

## Manifest files (maintained manually)

These files live in the manifest dirs and are NOT overwritten by sync:

| File | Purpose | Edit when |
|---|---|---|
| `claude/.claude-plugin/plugin.json` | Claude plugin identity | version bump, metadata change |
| `claude/.claude-plugin/marketplace.json` | Claude marketplace listing | name/description/category change |
| `codex/.agents/plugins/marketplace.json` | Codex marketplace listing | name/category/plugin-path change |
| `codex/plugins/ai-writing-suite/.codex-plugin/plugin.json` | Codex plugin identity | version bump, metadata change |

When bumping the skill version:
1. Update `version:` in source `SKILL.md` frontmatter.
2. Update `"version"` in the two `plugin.json` files above (the marketplace
   manifests carry no version field).
3. Run `bash packaging/sync.sh` — it will confirm version parity.

---

## Deferred targets (v2)

Cursor (`.cursor/rules/` + `.mdc` file) and RovoDev packaging are deferred to
v2 per owner decision (2026-06-06). When added, they follow the same pattern:
sync.sh gains a new `sync_target` call; the new target dir gets a manually-
maintained manifest; generated content is never hand-edited.
