#!/usr/bin/env bash
# run_all.sh — run every v1 regression check in one shot, fail-fast.
#
# Stdlib-only: no pip installs, no external deps. Works from any cwd (resolves
# its own directory). Used both by humans pre-commit and by CI (.github/workflows/ci.yml).
#
# Checks, in order (any nonzero aborts the run):
#   1. unit tests      — detector logic + fixture/judge/false-positive/draft suites
#   2. KB smoke        — end-to-end ingestion/retrieval over the seed KB (3 cases)
#   3. fixtures        — deterministic detector bands + 30-40% baseline calibration assert
#   4. false positives — clean human-style prose must NOT flag (+ planted-positive control)
#   5. comms-draft     — behavioral cases: good vs bad pre-authored draft artifacts must
#                        be told apart (per-case planted positive; see draft_cases.json)
#   6. voice extraction — voice-onboard: engineered corpus (habit 4x / noise 2x / absence 0x,
#                        mixed genres) + good vs bad profile artifacts must be told apart

set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")"   # the evals/ directory

echo "== [1/7] unit tests =="
python3 -m unittest discover -p 'test_*.py'

echo "== [2/7] KB smoke =="
python3 smoke_test.py

echo "== [3/7] fixtures (deterministic + calibration) =="
python3 -m fixtures.run_fixtures

echo "== [4/7] false positives =="
python3 -m fixtures.run_false_positives

echo "== [5/7] comms-draft behavioral cases =="
python3 -m fixtures.run_draft_cases

echo "== [6/7] voice-onboard extraction =="
python3 -m fixtures.run_voice_extraction

echo "== [7/7] audit-report output contract =="
python3 -m audit_report.run_report_contract

echo
echo "ALL CHECKS PASSED"
