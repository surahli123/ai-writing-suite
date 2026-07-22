# Calibration Measurement Policy

Policy version: v1 (2026-07-21)

## The n=8 knife-edge

With the inclusive 30–40% calibration band and eight targeted fixtures, only
3/8 (37.5%) is in band. Both 2/8 (25%) and 4/8 (50%) fail. The implementation
context is documented in `calibration.py:5-12`, and the invariant is pinned by
`test_calibration.py:19-27`.

## Decision

The band stays at 30–40% inclusive. Expand the fixture set toward n≥13 only when
the owner's real enterprise-draft corpus lands. There must be no silent band
widening and no silent fixture edits. The detector remains a regression signal,
not a KPI.

## Change procedure

Any future band or fixture-set-size change must bump this note's policy version
and update `test_calibration.py` in the same commit.
