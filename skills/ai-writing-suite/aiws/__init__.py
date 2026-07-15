"""aiws — the AI Writing Suite product package.

Reusable, host-agnostic logic lives here (not in `evals/`, which owns test
scaffolding, fixtures, and calibration; not in `tools/`, which owns thin CLI
entrypoints). `evals/` and `tools/` both import from `aiws`; `aiws` imports
from neither — see `aiws.kb` for the first module extracted under this rule
(architecture review 2026-07-13, item 5).
"""
