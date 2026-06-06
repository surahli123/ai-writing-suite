# Clarity — say one thing per sentence, plainly

> **Generic best-practice entry.** Distilled from the four MIT reference repos
> (see `Sources` below + `NOTICE.md`). This is the open-source KB. A company fork
> replaces or augments these entries with its own playbook via the same slot —
> see `README.md`.

## Principle

A reader should grasp each sentence on the first pass. Clarity is not
dumbing-down; it is removing everything between the reader and the point. When a
sentence carries two ideas, split it. When a word can be cut without losing
meaning, cut it.

## Moves

- **One idea per sentence.** If you find an "and" joining two full claims, make
  two sentences.
- **Concrete over abstract.** "We cut p95 latency from 800ms to 120ms" beats "We
  significantly improved performance." Numbers, names, dates — not "robust,"
  "significant," "various."
- **Subject-verb-object, early.** Put the actor and the action at the front. Long
  windups ("In order to be able to...") bury the verb.
- **Cut filler.** Delete "it's worth noting that," "in today's fast-paced world,"
  "at the end of the day." They add length, not meaning.
- **Prefer the short word.** "Use" not "utilize." "Help" not "facilitate."

## Before / After

- **Before:** It is worth noting that, in order to facilitate improved outcomes,
  the team undertook various optimizations across the system.
- **After:** The team cut three slow queries. p95 latency dropped from 800ms to
  120ms.

## When this matters most

Technical memos, status updates, PR descriptions — anywhere a busy reader skims.
Clarity is the first thing to check and the cheapest to fix.

## Sources

- `nature` (`nature-polishing` style-guardrails: concrete claims, cut hedging)
- `anti-vibe` (consultant-speak removal, "数据放具体数字")
- `stop-slop` (plain-word rules)
- `avoid-ai` (vague-attribution / vocabulary tiers)
