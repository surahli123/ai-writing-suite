---
name: voice-onboard
description: Interview an author and distill their historical writing into a reusable voice profile that comms-polish reads for voice matching. Ingests local files or pasted samples, extracts a 10-dimension style fingerprint with sample evidence, and writes _shared/voice-profile.md. Use when the user says "learn my voice", "match how I write", or before a series of posts that must stay on-voice.
---

# voice-onboard

Learn how *you* write, so the rest of the suite stops sounding like a clean
generic robot and starts sounding like you.

The job is narrow: read your real writing, distill a **voice profile**, and write
it to a file the polish skill reads on every run. This skill does NOT draft or
rewrite anything — it only listens and profiles.

## The mental model (for a product-owner learner)

Think of it like building a feature table for a ranking model:

- Your **writing samples** = raw training data.
- The **10 style dimensions** below = the feature schema.
- **`_shared/voice-profile.md`** = the published feature table.
- **`comms-polish`** = the model that reads that table at serving time.

If the table is empty or guessed, the model falls back to a generic baseline.
So the whole point of this skill is: produce an honest, evidence-backed table.

## What you read and write

- **Reads (your samples):** local markdown/text files you point to, or text you
  paste inline. (A Confluence-page link as a voice source is **v2** — note it to
  the user, do not attempt to fetch it. No programmatic ingestion in v1.)
- **Fills in:** `../../_shared/host-profile-template.md` (the blank form).
- **Writes:** `../../_shared/voice-profile.md` (the contract file). The field
  names there are stable — keep every `## H2` header, because `comms-polish`
  reads by header. Renaming a header silently breaks voice matching.

## How to run it (walk the user through, keep them in control)

This is a guided, human-gated flow. Do one step, show the result, wait. Never
batch the whole thing and dump a finished profile — the user is the owner of
their own voice and must confirm each judgment.

### Step 1 — Gather samples

Ask the user for samples. State plainly what makes a good sample:

- **3 minimum, 5-10 ideal.** Fewer than 3 → tell them confidence will be Low and
  the profile will be conservative. Don't force-extract from thin data.
- **Same genre as the target.** Learning their LinkedIn voice → ask for LinkedIn
  posts, not academic papers. Mixed genres → offer to extract two profiles
  rather than averaging them into a blur.
- **Their own words, not AI-polished.** A draft Claude already cleaned teaches
  the clean robot's voice, not theirs.
- **Recent (last ~6 months).** Voice drifts; recent samples track current style.

How they can hand samples over:

- Point to local files ("read everything in `~/writing/`") — you read them.
- Paste text inline, separated by `---`.

Confirm what you received before extracting: "Got 6 samples — 4 blog posts,
2 memos. That's Medium confidence. Want me to extract now, or add more first?"

### Step 2 — Extract the style fingerprint

Profile each of the 10 dimensions below. **Every claim needs evidence from the
samples.** No evidence → write "Unknown — not enough signal", never invent.

A trait counts only if it appears **3+ times**. One occurrence is noise. This is
the single most common extraction mistake — learning an accident as a habit.

The 10 dimensions (these map 1:1 to the `voice-profile.md` headers):

1. **Tone** — overall register (direct / warm / dry / formal).
2. **Sentence Length** — average words/sentence, short vs long share, rhythm habit.
3. **Vocabulary** — first-person usage, signature words, tics, domain terms.
4. **Vocabulary Do** — constructions they actively reach for.
5. **Vocabulary Don't** — common words they NEVER use. *Strongest signal* — a
   word someone never writes ("delve", "leverage") is more diagnostic than one
   they use often. Mine the absences.
6. **Signature Moves** — how they characteristically build a point ("not X but Y",
   lead with a number, end on a consequence).
7. **Punctuation & Formatting** — period vs comma balance, em-dash/ellipsis/
   exclamation density, list and emoji habits.
8. **Openings & Closings** — how they start and end (scene / claim / number;
   hook / consequence / trails off).
9. **Uncertainty Style** — how they signal doubt (quantified / blunt / hedged).
10. **Things To Avoid** — author-specific anti-patterns (marketing register,
    false balance, over-explaining to experts).

Two extraction principles to repeat to yourself:

- **Strip content, keep style.** They wrote about search ranking → that's the
  topic, not the voice. Look at rhythm, word choice, structure — not subject.
- **Don't average across genres.** Same person writes a tweet and a report
  differently. Mixed samples → split, don't flatten.

### Step 3 — Fill the template, then show a draft

Fill `host-profile-template.md` field by field with evidence. Then show the user
the draft profile and name the 3 most distinctive features you found, e.g.:

> "Draft profile ready. The three loudest signals: (1) period-heavy short
> declaratives, (2) leads every post with a number, (3) never uses hype words
> like 'unlock' or 'amazing'. Does this sound like you? Anything off?"

### Step 4 — Confirm, then write the contract file

Only after the user confirms, write the profile to
`../../_shared/voice-profile.md`, preserving every `## H2` header. If a profile
already exists, show what changed before overwriting — don't silently replace
their previous one.

Tell the user where it landed and that `comms-polish` will now read it
automatically.

### Step 5 — Leave a calibration loop open

A profile is a living file, not a one-shot. Tell the user:

- "After a few polish runs, if something feels 'not me', come back and we'll
  adjust the profile."
- Note the sample date in the changelog so stale profiles are visible later.
- If their style drifts, new samples should *replace* old ones, not mix in.

## Safety & boundaries

- **Never invent voice.** Thin samples → say "I could only extract X and Y
  confidently; the rest is blank." Honest gaps beat confident fiction.
- **Profile is not a permanent contract.** Prompt re-calibration periodically.
- **Stay in your lane.** This skill profiles; it does not rewrite. Rewriting is
  `comms-polish`. (And note: this suite is separate from the personal
  writing-vault "never ghostwrite" pipeline — see the project plan, R1.)
- **Self-improvement is human-gated (suite-wide).** If you spot a candidate
  extraction-rule improvement during a session, *propose* it for the suite's
  `learned-rules.md` and let the user approve — never auto-edit this SKILL.md.
  (The `learned-rules.md` log itself is wired in a later layer.)

## Deferred to v2 (note, don't build)

- Confluence-page link as a voice source (fetch/ingest).
- Bilingual (Chinese) extraction path.
- Any programmatic/scripted sample ingestion.

<!--
  ATTRIBUTION
  -----------
  Flow + 10-dimension taxonomy adapted from weijt606/anti-vibe-writing
  (references/learning-mode.md, assets/style-extraction-prompt.md, MIT), ported
  from Chinese to English. Do's/Don'ts "Style DNA" framing from
  donghuixin/AI-Vibe-Writing-Skills (1_style_extractor.md, MIT). Full copyright
  lines in the suite NOTICE.md.
-->
