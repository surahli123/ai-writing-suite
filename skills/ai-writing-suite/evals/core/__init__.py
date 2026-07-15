"""Capability-runner core: discovery protocol + result type.

WHY this exists (see reviews/2026-07-13-architecture-improve-review.md item 1):
the old run_all.sh hand-maintained an ORDINAL step list (== [1/7] .. [7/7] ==).
Three in-flight branches each renumbered those steps -> merge-hostile. This
package replaces the central list with DISCOVERY: each capability is a small
descriptor module under `capabilities/`, and the runner finds them at runtime.
Adding a capability = adding a file; nothing renumbers.

A capability descriptor module exposes:
  - SPEC: {id, name, kind, needs_model, depends_on}  (uniform interface)
  - run(context) -> EvalResult                       (executes the check)

The `context` gives descriptors one thing: `context.run(cmd)`, which shells out
to the SAME command the ordinal step ran, inheriting stdout/stderr so any
load-bearing output (calibration line, catalog line) passes through byte-for-byte.
"""

from .result import EvalResult
from .runner import Context, discover_capabilities, order_capabilities

__all__ = ["EvalResult", "Context", "discover_capabilities", "order_capabilities"]
