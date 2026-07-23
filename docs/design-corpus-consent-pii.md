# Design — Corpus Consent, PII, and Impersonation Handling (E4)

Date: 2026-07-22
Status: DESIGN ONLY — the `voice-onboard` hook is a future one-line change

## Problem and boundary

`voice-onboard` reads real writing and distills durable voice guidance, but its
current sample-gathering flow does not establish authority to use the corpus,
minimize personal information, or refuse an unconsented named-third-party voice
profile. The profile can also preserve verbatim anchors, which creates a second
place where sensitive sample text could survive after extraction.

The safe default is to decide authority before reading, minimize the corpus
before analysis, persist derived voice rather than raw text, and refuse
unconsented impersonation. This design does not add automated identity
verification and does not claim that regexes can recognize every form of PII.

## Pre-ingestion consent gate

Before opening a local path or accepting pasted samples, `voice-onboard` asks the
user to choose one authority state:

| State | Required confirmation | Result |
| --- | --- | --- |
| `self-authored` | "I wrote these samples and permit their use to create my voice profile." | Continue |
| `authorized` | "The author authorized this specific profiling use, and I am permitted to provide the samples." | Continue with the author and scope recorded |
| `unknown` or `denied` | Authority cannot be affirmed, is disputed, or is refused | Do not ingest or profile |

The confirmation names the intended use: local analysis to create a reusable
voice profile. Permission to read a public post is not automatically permission
to build an impersonation profile from it. A license that permits redistribution
also does not establish the subject's consent to identity imitation.

The gate occurs before file reading. It records the authority state, confirmation
date, confirmer, allowed profile genre/register scope, and any retention or
sharing restriction in the session receipt and the profile's `Meta` body. It
does not store a legal document or claim independent verification.

Mixed-author corpora are split before ingestion. Only samples covered by the
confirmation proceed. Forwarded messages, quoted replies, comments by other
people, and AI-polished passages are excluded unless separately authorized and
clearly attributed.

If the user cannot determine who wrote a passage, the safe branch is exclusion,
not probabilistic assignment.

## PII minimization

The skill warns the user not to provide credentials, authentication material,
government identifiers, financial account data, medical details, private
addresses, personal phone numbers, or unrelated third-party information.

After authority is established, ingestion follows four stages:

1. **Inventory.** List sample files and declared authors without quoting their
   bodies. The user confirms the intended subset.
2. **Screen.** Detect obvious high-risk strings with stdlib patterns where
   possible and review contextual identifiers with the user. Deterministic
   patterns are an aid, not a completeness claim.
3. **Minimize.** Exclude irrelevant passages and replace non-style-bearing
   identifiers with typed placeholders such as `[PERSON]`, `[EMAIL]`,
   `[PHONE]`, `[ADDRESS]`, `[ACCOUNT]`, or `[SECRET]`. Preserve punctuation and
   sentence shape when those are needed for stylometry.
4. **Confirm.** Show a bounded list of removals and replacements, not the
   sensitive values, and obtain approval before extraction.

Credentials, secrets, government identifiers, financial account data, and
unnecessary health information are never analyzed. A sample that cannot be
usefully de-identified is excluded.

Raw samples are ephemeral inputs. `voice-onboard` writes derived traits,
aggregate measurements, confidence, and provenance labels to the profile; it
does not copy the corpus into the profile or repository. Temporary copies are
removed at session end according to the user's retention instruction.

`Verbatim Anchors` receive a separate check because exact quotations can restore
PII that was removed elsewhere. Each anchor must be necessary, free of sensitive
or unrelated third-party data, traceable to an authorized sample, and explicitly
approved for persistence. Otherwise the profile uses a redacted anchor or
records `Unknown — no persistable anchor`.

Logs and error output use sample IDs and paths, not sample bodies or matched
sensitive values.

## Impersonation refusal

The deterministic rule is:

```text
named third-party subject + no subject-authorized profiling consent = refuse
```

This includes public figures, coworkers, customers, family members, and
deceased or historical figures when the request is to create a reusable profile
that imitates the named identity. Public availability of the writing does not
waive the rule.

On refusal, the skill does not read the offered corpus and does not create a
profile. It may offer a non-identifying alternative: describe broad,
genre-appropriate qualities requested by the user (for example, concise,
evidence-led, or conversational) without naming the person, extracting their
signature moves, or using their verbatim anchors.

Authorized organizational or editorial work can continue only when the
confirmation covers the named author, the profiling purpose, and the intended
users. The resulting profile records the authorization scope and must not be
reused outside it.

Authorship, identity, and authorization cannot always be resolved
deterministically. Names can be pseudonyms, samples can contain multiple voices,
and a requester can assert consent that the tool cannot verify. In any ambiguous
case the skill pauses before ingestion and requires a human owner to choose one
of three outcomes: provide adequate authorization, remove the ambiguous
samples/identity, or abandon profiling. The model does not guess, and an
uncertain classifier score cannot override the human gate.

## Failure and recovery behavior

- Missing consent fails closed before corpus access.
- Detected high-risk data is redacted or the sample is excluded; it is not
  printed as an explanation.
- Revoked permission stops future use. The user is shown which local profile
  and temporary corpus locations are in scope for deletion; deletion itself
  remains an explicit owner action.
- If a completed profile is found to contain unapproved PII or third-party
  anchors, consumers treat it as unavailable until the owner removes or
  re-approves the affected material.
- Consent applies to the declared corpus and purpose, not all future samples.
  Re-onboarding new sources re-runs the gate.

## Follow-up hook (not built here)

A later lane may add exactly this one-line bullet under
`voice-onboard/SKILL.md`'s `## Safety & boundaries` section:

```markdown
- **Consent, PII, and impersonation gate.** Before reading samples, confirm the author permits this profiling use, minimize or redact PII, and refuse profiling a named third party without their consent.
```

That future lane must also update the guided Step 1 flow and tests so the line is
an enforced protocol rather than a disconnected warning. This design lane does
not edit any `SKILL.md`.

## Acceptance criteria

- No sample body is read until the user records `self-authored` or scoped
  `authorized` permission for voice profiling.
- `unknown`, denied, disputed, or ambiguous authority fails closed and produces
  no profile from the affected samples.
- A named-third-party profiling request without subject-authorized consent is
  refused even when the writing is public.
- Mixed-author samples are separated, and quoted or forwarded third-party text
  is excluded unless independently authorized.
- High-risk data is excluded; other non-style-bearing PII is minimized with
  typed placeholders before extraction.
- Raw corpus text and sensitive matched values do not enter profiles,
  repository files, logs, or error output.
- Every persisted verbatim anchor has authorized provenance and separate
  persistence approval; otherwise it is redacted or omitted.
- Ambiguous identity or consent routes to the documented human-gated decision,
  never to model inference.
- The future hook attaches under `## Safety & boundaries`; this lane changes no
  `SKILL.md`.

**Falsifiable next step:** Run a table-driven dry review of 12 intake scenarios:
three self-authored, three authorized organizational, three named-third-party
without consent, and three containing high-risk PII. The protocol fails if any
unconsented third-party case reaches extraction, any high-risk literal reaches a
profile or log, or any authorized clean case is refused solely because the
deterministic screen cannot prove identity.
