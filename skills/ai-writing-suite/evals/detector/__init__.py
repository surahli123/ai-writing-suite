"""Mechanical AI-tell detector — Python port of the avoid-ai JS engine.

WHY this exists (design D10b): the LLM-judge fixtures catch *quality*
regressions, but they need a model and cost money. A deterministic, stdlib-only
detector is the cheap regression gate: it runs in CI on every change, keys off
the same AI-tell categories the `comms-polish` skill reads from
`_shared/patterns/`, and never needs an API key.

This package is a faithful-but-pragmatic port of the regex-detectable subset of
`avoid-ai-writing/detector/patterns.js`. Stylometric signals that need no model
(uniformity, em-dash rate, hashtag stuffing, bullet-NP lists) are included
because they are pure math; the trinary GPTZero-shaped classifier is included
because the fixtures lean on its score bands.
"""

from .detector import analyze, get_label  # noqa: F401
