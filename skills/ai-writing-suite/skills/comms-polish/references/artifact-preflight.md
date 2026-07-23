# Artifact Preflight

Use this preflight before editing copy that appears in a rendered component or
page.

## Trace visible copy to its durable source

For each copy region, record the rendered location and classify its current
source:

- **static** — copy lives directly in a checked-in page or content file;
- **template** — a template expands the copy into the rendered output;
- **generated** — a generator produces the visible file;
- **JS-rendered** — client or server JavaScript supplies the visible string;
- **sidecar** — copy comes from adjacent data such as JSON, YAML, or a CMS export;
- **deploy copy** — the visible text exists only in a built or deployed artifact.

Identify the durable upstream file or system before editing. Do not patch a
generated file, build output, or deploy copy when an upstream source controls
it.

## Classify visibility

Mark each copy region as:

- **visible-now** — shown without interaction;
- **user-expandable** — available through a deliberate user action;
- **permanently-hidden** — present in source but not reachable in the rendered
  experience;
- **generated-only** — present only after generation or at runtime.

Do not count permanently hidden or unreachable copy toward the visible
experience. Treat user-expandable copy as available but not equivalent to
visible-now copy.

## Work hotspot first

When the user names a component or page hotspot:

1. Inspect that hotspot in the rendered output.
2. Trace its visible copy to the durable source.
3. Edit the durable source, not a downstream copy.
4. Re-render or reload and verify the same hotspot again.

Rendered verification through a browser or screenshots is
**RUNTIME-ADVISORY — never a CI gate.** Use it when the runtime is available;
keep it out of `evals/run_all.sh` and every deterministic gating path.

## Build the must-keep inventory

Before editing, list the exact facts and surfaces that must survive:

- facts, numbers, dates, names, links, commands, labels, and technical claims;
- required headings, calls to action, navigation labels, and legal copy;
- visibility requirements for each item;
- any hard density or length budget from
  `references/artifact-density-budget.md`.

Turn that inventory into acceptance criteria. The edit is not complete unless
every literal or requirement is present in the durable source and appears in
the required visibility class after rendering.

## Add artifact evidence to the edit summary

In addition to the normal `edit` summary, report:

- the rendered hotspot and its durable source;
- the source and visibility classifications;
- the must-keep inventory and whether each item survived;
- the applied density or length budget, if any;
- the re-verification performed, or why runtime verification was unavailable.

## Stop conditions

Stop and report the blocker when:

- the durable source cannot be identified;
- the only editable surface is generated output or deploy copy;
- sources disagree and ownership cannot be resolved safely;
- a must-keep item cannot fit without changing meaning or violating a hard
  surface constraint;
- the requested edit requires inventing facts, labels, or product behavior;
- re-rendering reveals a mismatch that cannot be traced safely.

Unavailable browser or screenshot tooling is not itself a CI failure. Report
the runtime-advisory verification gap and complete every source-level check that
remains possible.
