# Audience — write for the specific reader, not "everyone"

> **Generic best-practice entry.** Distilled from the four MIT reference repos
> (see `Sources`). Open-source KB; company forks swap via the same slot
> (`README.md`).

## Principle

Every piece has one primary reader with a job to do. Naming that reader — their
role, what they already know, what decision they need to make — settles most
style questions automatically. Writing for "everyone" produces text that lands
with no one.

## Moves

- **State the reader and their job before drafting.** "An on-call engineer who
  needs to decide whether to roll back." That sentence fixes tone, length, and
  jargon level.
- **Calibrate jargon to shared knowledge.** Define a term once if the reader
  might not know it; never define terms the reader uses daily (it reads as
  condescending or AI-padded).
- **Lead with what the reader cares about,** not what you find interesting. An
  exec wants the decision; an engineer wants the repro steps.
- **Cut the throat-clearing.** "In today's fast-paced world" and "as we all
  know" address no one. Address the actual reader directly.

## Before / After

- **Before:** This guide is designed to help users of all skill levels
  understand the fundamentals of our deployment process.
- **After:** If you're on-call and a deploy is failing, run `./rollback.sh`. The
  rest of this page explains what it does.

## When this matters most

Cross-functional writing — when an engineer writes for a PM, or a DS writes for
leadership. Mismatched audience is the most common reason good content fails to
land.

## Sources

- `anti-vibe` (`host-profile` + scenario-presets: reader-shaped voice)
- `ai-vibe` (`style-extractor` / reviewer prompts: audience modeling)
- `nature` (`nature-writing`: audience-aware framing per journal)

## Related entries

- `structure.md` — once you've named the reader, their role decides the order and channel: exec gets the decision first, engineer gets the repro steps.
- `tone.md` — naming the reader settles most register questions automatically; the right formality is the reader's, not the writer's.
