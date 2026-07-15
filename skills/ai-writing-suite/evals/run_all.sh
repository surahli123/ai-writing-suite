#!/usr/bin/env bash
# run_all.sh — run every v1 regression check in one shot, fail-fast.
#
# Stdlib-only: no pip installs, no external deps. Works from any cwd (resolves
# its own directory). Used both by humans pre-commit and by CI (.github/workflows/ci.yml).
#
# Thin compatibility wrapper: the checks are no longer a hardcoded numbered list
# here. Each capability is a self-registering descriptor under evals/capabilities/,
# and run.py DISCOVERS and runs them (fail-fast). Adding a check = adding a file;
# nothing in this script renumbers. See core/ + capabilities/ and
# reviews/2026-07-13-architecture-improve-review.md item 1.

set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")"   # the evals/ directory

exec python3 run.py "$@"
