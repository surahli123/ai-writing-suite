---
name: voice-onboard
description: Interview an author and distill their historical writing into a reusable voice profile that comms-polish reads for voice matching. Ingests local files or pasted samples, extracts a 10-dimension style fingerprint with sample evidence, and writes _shared/voice-profile.md. Use when the user says "learn my voice", "match how I write", or before a series of posts that must stay on-voice. Not for rewriting or polishing text - that is comms-polish; this skill only profiles.
---

# voice-onboard

Learn how *you* write, so the rest of the suite stops sounding like a clean
generic robot and starts sounding like you.

The job is narrow: read your real writing, distill a **voice profile**, and write
it to a file `comms-polish` reads before any rewrite (and `comms-draft` before
drafting). This skill does NOT draft or rewrite anything — it only listens and
profiles.

## Locating shared assets (suite root)

All `_shared/...` paths in this file are **suite-root-relative**. The suite root is the
installed directory that directly contains `_shared/` and the suite's router `SKILL.md`
(e.g. `.../ai-writing-suite/`). Do not resolve these paths against your session's working
directory. To find the root: start from this SKILL.md's own location and walk up until a
directory contains `_shared/`. If you cannot find it, say so and ask for the suite's
install path — do not guess or silently skip the shared assets.

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
- **Fills in:** `_shared/host-profile-template.md` (the blank form).
- **Writes:** `_shared/voice-profile.md` (the contract file). The field
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
  posts, not academic papers. **One genre per run.** The current build stores a
  single `_shared/voice-profile.md`, so if the samples span genres, pick the one
  target genre for this run rather than averaging them into a blur — don't promise
  a second stored profile the build can't hold. (Storing a separate profile per
  genre, with IDs and selection, is a designed follow-up, not yet available; note
  it to the user rather than acting on it.)
- **Their own words, not AI-polished.** A draft Claude already cleaned teaches
  the clean robot's voice, not theirs.
- **Recent (last ~6 months).** Voice drifts; recent samples track current style.

How they can hand samples over:

- Point to local files ("read everything in `~/writing/`") — you read them.
- Paste text inline, separated by `---`.
- **Their own edits to something the suite returned.** If the user hand-corrected
  a `comms-polish` output, the delta between what was returned and what they
  changed is the strongest voice signal available — treat the corrected version as
  a high-value sample (`comms-polish` offers to route those edits here).

Confirm what you received before extracting: "Got 6 blog posts — that's Medium
confidence for your blog voice. Extract now, or add more first?" If the samples
span genres, say so and ask which ONE to profile this run: "These are 4 blog posts
and 2 memos — different voices. Which should I profile this run? (One genre per
run; the other can be a separate run.)"

### Step 2 — Extract the style fingerprint

Profile each of the 10 dimensions below. **Every claim needs evidence from the
samples.** No evidence → write "Unknown — not enough signal", never invent.

A trait counts only if it appears **3+ times**. One occurrence is noise. This is
the single most common extraction mistake — learning an accident as a habit.

The 10 qualitative dimensions below are the extraction schema; they populate ten
of the profile's headers. The profile's **full** header set — including Meta,
Scope & Calibration, Measured Fingerprint, and Changelog — is the **canonical
ordered list at the top of `_shared/voice-profile.md`**. Reference that list and
keep every header exactly; do not restate a divergent subset. The 10 dimensions:

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
  differently. Mixed samples → pick the target genre for this run and profile
  that one; do not pool them into a single blurred profile. (Storing a distinct
  profile per genre is the designed follow-up above — today one genre is profiled
  and stored per run.)

#### The measurement pass (quantitative half — run alongside the 10 dimensions)

The 10 dimensions above are qualitative adjectives about the voice. Run the
deterministic stylometry pass to add the **measured** half: numbers a reader
skill (and the eval) can verify against the samples instead of trusting prose.
This is the differentiator — competitors derive voice from corpus statistics,
not adjectives.

Run the shipped module (stdlib-only, loads on every host) once **per genre**:

```
python3 <suite-root>/_shared/stylometry.py --genre <genre> <sample-file> [...]
```

or import `compute_per_genre({genre: [samples]})` if the samples are in memory.
It prints, per genre: sentence-length mean AND variance/burstiness (variance is
the rhythm signal, not the mean), punctuation density per 1k words, testable-
number density per 100 words, AI-register word hits (0 is the strong signal),
function-word deltas vs a generic baseline, and a char 3-gram profile.

Rules the skill must honor — in what it computes AND what it is allowed to claim:

- **Per genre, never pooled.** Run the module once per genre and store one
  block per genre. Do NOT concatenate two genres into one run — pooling a tweet
  and a report produces a mean/variance that describes neither (the module's
  `--demo` proves this). This is the same "don't average across genres" rule,
  now enforced numerically.
- **3+ samples.** With fewer than 3 samples the module marks every number
  indicative-only; say so out loud and do not call any figure a habit.
- **CJK / non-whitespace scripts.** The module emits NO numbers for
  predominantly-CJK samples (whitespace word-counting collapses on them) and
  returns an UNSUPPORTED marker instead. Surface that marker verbatim; never
  hand-fill numbers it refused to compute. Bilingual/CJK stylometry is v2.
- **Every number carries provenance.** When you write a figure, it carries the
  genre, the sample count, and a confidence note. A number with no provenance is
  worse than no number.

### Step 3 — Fill the template, then show a draft

Fill `host-profile-template.md` field by field with evidence — both the 10
qualitative dimensions AND the **Measured Fingerprint** section (one `### <genre>`
block per genre, straight from the measurement pass). Then show the user the
draft profile and name the 3 most distinctive features, backed by the measured
numbers so "distinctive" is checkable, not vibes, e.g.:

> "Draft profile ready. The three loudest signals: (1) short, bursty rhythm —
> mean 8.4 words/sentence but variance 41 (blog, N=6), so short punches next to
> long qualifiers; (2) high testable-number density, 4.2 figures per 100 words;
> (3) zero AI-register words across 55 checked. Every number here is recomputed
> from your samples. Does this sound like you? Anything off?"

Keep the flow human-gated: show the numbers, let the user confirm or correct;
never write the profile before they approve (Step 4). If a genre came back
UNSUPPORTED (CJK), say so plainly rather than inventing numbers.

### Step 4 — Confirm, then write the contract file

Only after the user confirms, write the profile to
`_shared/voice-profile.md`, preserving every `## H2` header. If a profile
already exists, show what changed before overwriting — don't silently replace
their previous one.

**A real profile must NOT carry the `> SAMPLE PROFILE.` banner** the shipped
example uses. Overwrite that banner and Sam's example content entirely — consumers
(`comms-polish`, `comms-draft`) detect the un-replaced sample by that banner and
treat it as *no profile*, so leaving the banner in place would make your real
profile invisible. A real profile is defined by the banner's absence.

Tell the user where it landed and that `comms-polish` will now read it
automatically (before any rewrite).

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
  writing-vault "never ghostwrite" pipeline — this suite may draft and rewrite.)
- **Self-improvement is human-gated (suite-wide).** See "Self-improvement" below;
  never auto-edit this SKILL.md.

## Self-improvement (human-gated)

This skill participates in the suite's human-gated self-improvement loop. The
full protocol is in `_shared/self-improvement.md`; follow it, do not restate
it. In short:

- **On start:** read `_shared/learned-rules.md` and apply any entry whose
  `status: active` and whose scope is `voice-onboard` or `all` (e.g. an approved
  extraction-judgment rule). Degrade gracefully if the file is absent.
- **On end:** if a repeatable extraction correction surfaced this session (a voice
  judgment the user overrode that would recur), **propose** one candidate rule
  (rule + session-grounded rationale + scope) and **wait for explicit approval**
  before appending it to `learned-rules.md`. Propose nothing if nothing repeatable
  surfaced.
- **Never** auto-edit this SKILL.md — approved rules live only in
  `learned-rules.md` (append-only). Each rule is eval-measured in Layer 3 before
  it is trusted.

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
