"""Discovery + execution for capability descriptors.

`discover_capabilities()` scans the sibling `capabilities/` package for modules
that export a SPEC dict and a run() callable. No central list is read; a module
appearing in that directory IS its registration.

`order_capabilities()` gives a deterministic run order: a stable topological sort
honoring each SPEC's `depends_on`, ties broken by id. Order does not affect any
contract (each step's load-bearing output comes from its own child process), but
determinism keeps the discovery-ordered `[n/N]` headers reproducible.
"""

import importlib
import os
import pkgutil
import subprocess
import sys
from dataclasses import dataclass
from typing import Callable, List

from .result import EvalResult

# evals/ is the import root (run_all.sh cd's here); core/ and capabilities/ are
# packages beneath it. EVALS_DIR is where child processes run so that invocations
# like `python3 -m fixtures.run_fixtures` resolve exactly as they did in the shell.
EVALS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@dataclass(frozen=True)
class Capability:
    """A discovered descriptor: its SPEC fields plus its run() callable."""

    id: str
    name: str
    kind: str
    needs_model: bool
    depends_on: tuple
    run: Callable[["Context"], EvalResult]


class Context:
    """The single service a descriptor's run() gets: shell out to a command,
    inheriting this process's stdout/stderr so child output passes through
    byte-for-byte (calibration line, catalog line, per-check output)."""

    def __init__(self, cwd: str = EVALS_DIR):
        self.cwd = cwd

    def run(self, cmd: List[str]) -> EvalResult:
        sys.stdout.flush()
        sys.stderr.flush()
        proc = subprocess.run(cmd, cwd=self.cwd)
        return EvalResult(ok=proc.returncode == 0, returncode=proc.returncode)


def discover_capabilities() -> List[Capability]:
    """Import every descriptor module under capabilities/ and collect its SPEC."""
    from . import __name__ as core_pkg  # e.g. "core" (run root) or "evals.core"

    caps_pkg_name = core_pkg.rsplit(".", 1)[0] + ".capabilities" if "." in core_pkg else "capabilities"
    caps_pkg = importlib.import_module(caps_pkg_name)

    found: List[Capability] = []
    for mod_info in pkgutil.iter_modules(caps_pkg.__path__):
        if mod_info.name.startswith("_") or mod_info.name.startswith("test_"):
            continue
        module = importlib.import_module(f"{caps_pkg_name}.{mod_info.name}")
        spec = getattr(module, "SPEC", None)
        run_fn = getattr(module, "run", None)
        if spec is None or run_fn is None:
            # capabilities/ holds only descriptors + __init__.py by convention (see
            # package docstring); a module missing SPEC/run here is a defect, not
            # an optional file to skip past. Fail loudly so a broken descriptor
            # can never silently vanish from the run the way ordinal renumbering
            # used to drop steps.
            raise RuntimeError(
                f"capability module {caps_pkg_name}.{mod_info.name!r} is missing "
                f"SPEC and/or run() — every module under capabilities/ must be a "
                f"valid descriptor (see capabilities/__init__.py)"
            )
        found.append(
            Capability(
                id=spec["id"],
                name=spec["name"],
                kind=spec.get("kind", "batch"),
                needs_model=spec.get("needs_model", False),
                depends_on=tuple(spec.get("depends_on", ())),
                run=run_fn,
            )
        )
    return found


def order_capabilities(caps: List[Capability]) -> List[Capability]:
    """Stable topological sort by depends_on; ties broken by id.

    F3 (2026-07-15 review round): kept the cycle guard as-is — six real SPECs now
    carry depends_on=["unit_tests"], so `visit`'s traversal/seen-tracking is live
    code exercised on every run, not unused machinery; the 2-line cycle check
    riding on that same path is cheap insurance against a future typo'd
    self/mutual dependency, not standalone gold-plating.
    """
    by_id = {c.id: c for c in caps}
    ordered: List[Capability] = []
    placed = set()

    def visit(cap: Capability, seen: frozenset):
        if cap.id in placed:
            return
        if cap.id in seen:
            raise ValueError(f"dependency cycle at capability {cap.id!r}")
        for dep in sorted(cap.depends_on):
            if dep in by_id:
                visit(by_id[dep], seen | {cap.id})
        placed.add(cap.id)
        ordered.append(cap)

    for cap in sorted(caps, key=lambda c: c.id):
        visit(cap, frozenset())
    return ordered
