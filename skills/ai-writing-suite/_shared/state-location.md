# User State Location

This file is the single resolver for mutable, per-user AI Writing Suite state.
Skills reference this file; they do not copy or redefine its rules.

## Resolver

Resolve `<state>` once per run:

1. If `$AIWS_STATE_DIR` is set, use its value.
2. Otherwise, use `~/.aiws/`.

The live state paths are:

- voice profiles: `<state>/voice-profiles/<genre>.md`
- learned rules: `<state>/learned-rules.md`

Create the resolved state directory or `voice-profiles/` child when a gated write
needs it. Reads degrade gracefully when a resolved file or directory is absent.

## Packaging invariant

The shipped package must contain no real voice profiles and no real learned-rule
entry whose status is `active` or `proposed`. Shipped sample profiles, blank
templates, and the retired `LR-000` schema example are immutable package assets,
not live user state.
