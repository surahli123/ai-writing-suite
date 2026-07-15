"""EvalResult — the single value a capability's run(context) returns."""

from dataclasses import dataclass


@dataclass(frozen=True)
class EvalResult:
    """Outcome of running one capability.

    ok=False aborts the whole run (fail-fast, matching the old `set -e` shell).
    returncode carries the child process exit code so the wrapper can propagate
    the exact nonzero status CI asserts on.
    """

    ok: bool
    returncode: int = 0
