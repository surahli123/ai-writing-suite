---
name: comms-qa
description: Answer questions from the knowledge base via a markdown mini-RAG over the pluggable KB. Not yet built - coming in v2.
---

# comms-qa (placeholder)

This sub-skill will answer questions from the knowledge base under
`_shared/knowledge/` -- a zero-dependency mini-RAG that navigates a markdown KB
through its `INDEX.md` and returns the relevant passage. In the open-source build
the KB is generic best practices; a company fork drops its own playbook into the
same slot. **Coming in v2.** The KB slot exists in this build but is empty
(retrieval is a later layer).
