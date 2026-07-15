"""Capability descriptors — one module per v1 regression check.

Each module here is a self-registering descriptor: it exports SPEC (uniform
metadata) and run(context) (executes the check). `core.discover_capabilities()`
finds them by scanning this package, so adding a capability is adding a file and
never touches a shared step list. Ordering is deterministic (see core.runner) and
contract-independent: no capability depends on another's state.

The run() bodies move the OLD run_all.sh invocations verbatim (same module,
same args, same cwd=evals/); what each check executes is unchanged.
"""
