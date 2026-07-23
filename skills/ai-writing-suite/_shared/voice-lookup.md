# Voice Lookup Protocol

This is the single lookup protocol for consumer skills that match a user's
learned voice. `comms-polish` and `comms-draft` reference this file; they do not
copy its selection, fallback, banner, or offer rules.

Resolve mutable profile paths through `_shared/state-location.md`.

## Source order

Use these voice sources in order:

1. A learned per-genre profile under resolved `<state>/voice-profiles/`.
2. A writing sample the user pasted in the current request.
3. The lightest voice inferred from the draft or brief and its context.

The first available source wins. A profile is a bias signal, never a hard
dependency, and a genre's hard form constraints still take precedence.

## Learned-profile lookup

Look up source 1 cheaply:

1. **List** `<state>/voice-profiles/*.md` with one directory read. Inspect
   filenames only; do not parse every body.
2. **Select one file**, first match wins:
   1. **Explicit user request.** If the user names a genre, select that genre's
      file. If it is absent, treat the lookup as no match.
   2. **Normalized-exact preset/genre match.** Normalize the run's genre and
      each filename slug the same way: lowercase and replace spaces with
      hyphens. Match by string equality only. Do not use fuzzy, prefix, or alias
      matching (`formal-report` is not `report`).
   3. **Single-profile fallback.** If exactly one profile file exists, use it.
   4. **No match.** Continue to the next voice source.
3. **Read** the full body of the one selected file only.
4. If the directory is absent or empty, try the legacy
   `_shared/voice-profile.md` path.

**Any file carrying the `> SAMPLE PROFILE.` banner counts as NO profile,
whether it sits in `<state>/voice-profiles/` or the legacy
`_shared/voice-profile.md` path.** Continue to the next voice source exactly as
if that file were absent.

For a valid profile, use every present field that carries voice guidance. The
canonical ordered header list lives at the top of `_shared/voice-profile.md`;
reference it rather than restating a subset. Ignore missing fields without
failing.

## Graceful degradation and Q8 offer budget

When source 1 yields no valid match, do not error or block. Use a pasted sample
when available; otherwise infer the lightest voice that fits the context.

If the user explicitly requested their own voice, offer `voice-onboard` once to
create the named or needed genre profile. If profiles exist but none match,
name the available genres so the user can redirect. The offer never blocks the
deliverable: if it is declined or unanswered, continue with the next voice
source and use the consumer skill's required degraded-voice note.

Otherwise, degrade silently: do not ask a question or mention the missing
profile.

The `voice-onboard` offer budget is **at most one offer per session,
suite-wide**. An offer already made by `comms-polish`, `comms-draft`, or the
router spends it. Check the conversation before offering. An offer is
offer-only: never auto-run `voice-onboard` and never hold the deliverable for
it.
