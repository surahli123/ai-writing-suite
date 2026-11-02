# comms-draft (archived 2026-11-02)

`comms-draft` wrote a full first draft from a brief plus the playbook. It has been
replaced by [`comms-shape`](../../skills/ai-writing-suite/skills/comms-shape/SKILL.md),
which agrees on the reader, the thesis, and an outline with the author before
filling anything in, and also pressure-tests drafts and handles polish-plus-add
requests. Owner ruling R4 in `docs/decisions-2026-11-01.md`; plan in
`docs/plan-step9-and-comms-shape-2026-11-02.md`.

The skill file is kept as `SKILL.archived.md` for history. It is outside the
packaged tree and renamed so no host discovers it as a skill. Asking for
`comms-draft` by name routes to `comms-shape`, and learned rules scoped
`comms-draft` still apply to comms-shape's fill step and mixed mode.
