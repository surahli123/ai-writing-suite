#!/usr/bin/env bash
# run_all.sh — run every v1 regression check in one shot, fail-fast.
#
# Stdlib-only: no pip installs, no external deps. Works from any cwd (resolves
# its own directory). Used both by humans pre-commit and by CI (.github/workflows/ci.yml).
#
# Checks, in order (any nonzero aborts the run):
#   1. unit tests      — detector logic + fixture well-formedness (~23 tests)
#   2. KB smoke        — end-to-end ingestion/retrieval over the seed KB (3 cases)
#   3. fixtures        — deterministic detector bands + 30-40% baseline calibration assert
#   4. false positives — clean human-style prose must NOT flag (+ planted-positive control)

set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")"   # the evals/ directory

echo "== [1/4] unit tests =="
python3 -m unittest discover -p 'test_*.py'

echo "== [2/4] KB smoke =="
python3 smoke_test.py

echo "== [3/4] fixtures (deterministic + calibration) =="
python3 -m fixtures.run_fixtures

echo "== [4/4] false positives =="
python3 -m fixtures.run_false_positives

echo
echo "ALL CHECKS PASSED"
