---
name: comms-qa
description: Answer questions from the knowledge base via a markdown mini-RAG over the pluggable KB. Not yet built - coming in v2. For polishing existing text use comms-polish; for drafting a new page use comms-draft.
---

# comms-qa (placeholder)

This sub-skill will answer questions from the knowledge base under
`_shared/knowledge/` -- a zero-dependency mini-RAG that navigates a markdown KB
through its `INDEX.md` and returns the relevant passage. In the open-source build
the KB is generic best practices; a company fork drops its own playbook into the
same slot. The KB slot is already seeded in this build (5 generic entries +
`INDEX.md` + a verified retrieval smoke path); the full question-answering
sub-skill that wraps it is **coming in v2.**
