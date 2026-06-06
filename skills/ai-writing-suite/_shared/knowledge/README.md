# Knowledge base (pluggable slot)

This directory is the **fuel** slot. It is intentionally empty in this build.

The suite is the engine; the knowledge base is the fuel. The open-source build
will ship a generic best-practices KB here (a wiki-style set of markdown topic
entries plus an `INDEX.md` for navigation). A company fork drops its own writing
playbook into this same slot via a Confluence page or markdown files. The
playbook never enters the public repo.

- **KB seed (generic entries + `INDEX.md`):** Layer 2.
- **Retrieval over the KB (`comms-qa` mini-RAG):** v2.

Until then this slot holds only this README and a `.gitkeep`, so the directory
exists and the "drop in a page" promise has a concrete home.
