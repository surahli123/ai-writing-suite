# Outline template

Use this shape for the step-3 outline. Keep it short: an outline that runs longer
than a third of the finished document is a draft in disguise.

```
Reader: <who> — Decision or action wanted: <what they should do>
Thesis: <the one sentence the author chose>

Acceptance criteria
- style: <register and voice for this reader>
- format: <genre and its hard constraints>
- length: <target range>
- content integration: <facts and KB slots that must appear>
- depth: <overview or detail, and why>

Talking points
- <point> — author (notes ¶2)
- <point> — author (answer, turn 3)
- <point> — proposed (needs the author's approval and a source)
- <slot the genre needs> — [NEEDS: what is missing]

Shape: <where the stakes peak; what stays open, if the material leaves it open>
Sources used: <KB entries the slots came from>
```

## Provenance tags

| Tag | Meaning | Allowed in the finished document? |
| --- | --- | --- |
| author | The author's notes, draft, or an answer in this conversation | Yes |
| proposed | The skill suggested it | Only after the author approves **and** a source exists; otherwise `[NEEDS: evidence]` |
| `[NEEDS: …]` | The material does not hold it | Stays as a visible gap |

## Genre slots

Take the slot list from the matching KB entry (`_shared/knowledge/INDEX.md`). For
example:

- **Experiment readout:** the verdict first; for each effect, the baseline, unit
  of change, interval, n, and window; which null result it is (no detectable
  effect, underpowered, or not run).
- **Decision memo:** the call, the options rejected, the trade-off, and what would
  change the decision.
- **Status update:** the call or headline, the ask, and owned, dated items.
- **Incident note:** facts, hypotheses, and unknowns kept apart; a timeline in one
  timezone; owned action items.

A company fork's playbook entries replace these generic slots through the same KB.

## Parallel sets

When the document is, or contains, a set of items of one kind (status items,
result cards, titles), decide in the outline:

- the item frame (for example: status label, then what, then owner);
- the closed status vocabulary (for example: Shipped, In progress, Blocked, Next);
- the slots every comparable item carries.

Then every item is filled the same way. See comms-polish's scenario presets,
"Parallel items".
