# Knowledge base (pluggable slot)

This directory is the **fuel** slot. The suite is the engine; the knowledge base
is the fuel.

This OSS build ships a **generic best-practices KB** (markdown topic entries +
`INDEX.md` navigation, distilled from four MIT reference repos). A company fork
drops its own writing playbook into this *same slot* via a Confluence page or
markdown files. The playbook never enters the public repo.

## What's in this slot

| File | Role |
| --- | --- |
| `INDEX.md` | **Retrieval backbone.** Lists every entry with a one-line summary + keywords/aliases so an agent can resolve a natural-language query to the right entry. Pure markdown, zero deps (design decision **D5**). |
| `clarity.md`, `structure.md`, `audience.md`, `tone.md`, `revision.md` | Generic professional-writing best-practice entries. Each is attributed (`Sources` section) and small. |
| `SMOKE-TEST.md` | **Proof the chain works (D12).** One end-to-end ingestion + retrieval test: sample page → INDEX row → query → expected entry + passage. Layer 3 eval automates it. |
| `README.md` | This file. |

## How retrieval works (no engine to build)

Retrieval is an agent reading `INDEX.md`, matching the question against the
keywords/summary, opening the one matching entry, and quoting the passage. There
are **no embeddings, no vector DB, and no host-specific MCP tools** in the core
path — so it runs identically on Claude, Codex, Cursor, and RovoDev (D5). The
OMC `wiki_*` tools are an optional Claude-side accelerator only; they are never
required.

Full `comms-qa` retrieval logic (multi-passage, ranking, citations) is **v2**.
v1 ships the seed + the proven smoke path, nothing heavier.

## Swapping in a company playbook (the company step)

A company fork turns "generic KB" into "DS Comms Playbook" by **adding data, not
building an engine** (decisions D11 + D12). The steps:

1. **Export each Confluence page / playbook section to markdown** and drop the
   file(s) into this directory (replace the generic entries, or add alongside
   them). One page = one `*.md` entry. Keep entries small and topic-scoped.
2. **Add one row per entry to `INDEX.md`** — `entry file | one-line summary |
   keywords/aliases`. That single row IS the ingestion step (see `SMOKE-TEST.md`
   Step 2). No build, no re-index job.
3. **Add company test cases to `SMOKE-TEST.md`** (query → expected entry →
   expected passage) so the eval can verify the company KB resolves correctly.
4. **Do not push the company KB to the public repo.** The playbook is private; it
   lives only in the fork. The engine (everything outside this slot) stays shared.

That's the whole integration. Because the index and entries are plain markdown,
the company never touches retrieval code — they edit a table and drop in pages.
