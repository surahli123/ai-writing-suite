# Onboarding your playbook into the knowledge base

**Who this is for:** the person on a company fork who owns the writing playbook —
a data / comms / ops person, **not** an engineer. You will export pages, run two
scripts, and fix whatever they flag. No code to write, no retrieval engine to
build. That is the whole point: **you add data, not engineering.**

**What you get at the end:** a `_shared/knowledge/` folder holding your playbook
as the knowledge base the `comms-qa` skill answers from. Until it passes the
validator, treat the KB as *not ready* — a broken KB makes the assistant answer
from the wrong page or refuse to answer at all.

All commands below are run from the suite folder:

```
cd skills/ai-writing-suite
```

---

## The five steps at a glance

```
[1] EXPORT      [2] INGEST         [3] REVIEW        [4] VALIDATE      [5] SMOKE
Confluence/  →  kb_ingest.py    →  fix the TODOs  →  kb_validate.py →  ask a real
Notion/Docs     shapes pages       the tool left     must say PASS     question
to a folder     into KB entries    for you                             (comms-qa)
```

You will bounce between **[3] Review** and **[4] Validate** until the validator
says `PASS`. That loop is normal and expected.

---

## Step 1 — Export your pages to a folder

Put every page you want in the KB into one folder (e.g. `export/`). Two formats
work, and you can mix them in the same folder:

- **Confluence → "Export to HTML".** On a page or space, use *… → Export → HTML*
  (or *Space settings → Export → HTML*). You get one `.html` file per page. This
  is the format any Confluence user can produce **without admin rights or an API
  token**, which is why the tool targets it.
- **Markdown export** (`.md`). Notion (*Export → Markdown*), Google Docs (via a
  Markdown download/add-on), or any plain markdown files.

**One page = one topic.** Keep pages small and focused ("Tone", "Exec updates",
"Structuring a memo") rather than one giant page. Retrieval picks *one* entry per
question, so a sprawling page answers nothing cleanly.

---

## Step 2 — Ingest: shape the export into KB entries

```
python3 tools/kb_ingest.py export --out _shared/knowledge
```

This reads every page in `export/` and, for each one, writes a KB entry into
`_shared/knowledge/`: a `# Title`, your page text, a **Keywords** and **Summary**
line (pulled from the page's own words), and a `## Related entries` footer linking
adjacent topics. It also updates `INDEX.md`, the one file the assistant reads to
find the right entry.

**What it will and will not do for you:**

- It **extracts** keywords and a summary from your page's title and headings — it
  never makes up facts or synonyms.
- It **proposes** links between related pages (based on shared words) and prints
  each proposal in the report so you can confirm it.
- Where it genuinely cannot tell (a page with no title, an empty page, two pages
  with the same title, too few keywords), it writes a **`TODO:` marker** into the
  file and lists it at the end. It never guesses silently.

It **never overwrites** an entry you have already edited. To regenerate anyway:

```
python3 tools/kb_ingest.py export --out _shared/knowledge --force
```

Re-running with the same export is safe: identical input produces identical
output.

### What the report looks like

```
=== kb_ingest report ===
Wrote 3 entr(y/ies): tone.md, exec-updates.md, structure.md

PROPOSED related links (confirm these — not auto-trusted):
  - tone.md <-> structure.md (shared-keyword overlap; confirm)

TODO — resolve before first use (kb_validate.py will fail on these):
  - exec-updates.md: only 2 keyword(s) extracted (need >=3) — add aliases
```

---

## Step 3 — Review the TODOs

Open each entry the report mentioned and fix its `TODO:` markers. Common ones:

| TODO you'll see | What to do |
| --- | --- |
| `TODO: add a title` | The source had no heading. Add a `# Title` line. |
| `TODO: add keywords/aliases` or "only N keyword(s)" | Add the words a colleague would actually type to find this page (synonyms, the "how do I…" phrasing). Edit the `Keywords:` line in the `<!-- kb-entry-meta -->` block **and** the Keywords column in `INDEX.md`. |
| `TODO: add a one-line summary` | Write one plain sentence describing the page; put it in `Summary:` and the INDEX Summary column. |
| `TODO: source page had no body content` | The page was empty. Add the real text, or delete the entry and its INDEX row. |
| `TODO: duplicate topic` | Two pages had the same title. Merge them into one entry, or rename one. |
| `TODO: add >=2 bidirectional links` | List at least two related entries in the footer, and add a matching link back in each of those entries. |

**Deleting `TODO` text is not enough — fix the underlying gap.** The validator
checks the *content*, not just the absence of the word.

---

## Step 4 — Validate: the go/no-go gate

```
python3 tools/kb_validate.py _shared/knowledge
```

This runs seven checks and prints a `PASS`/`FAIL` line for each, with the exact
`file:line` of every problem. It must say **PASS** before you ship. The checks:

1. **INDEX ↔ files line up** — every INDEX row has a file and vice versa.
2. **Related-entries valid** — each entry has ≥2 links, none broken.
3. **Links go both ways** — if A links B, B links A.
4. **Keywords present** — no empty Keywords cell.
5. **Summary present** — no empty/placeholder Summary.
6. **No TODO markers left** — every gap from Step 3 is resolved.
7. **Retrieval smoke** — each entry's own keywords actually find that entry (if
   not, its keywords are too weak or clash with a neighbour — make them more
   specific).

### A FAIL looks like this

```
[FAIL] No TODO markers left
       - _shared/knowledge/exec-updates.md:2 Keywords: TODO: add retrieval keywords/aliases
[FAIL] Retrieval smoke (own keywords -> own entry)
       - _shared/knowledge/tone.md:0 own keywords retrieve 'structure.md' not 'tone.md'
```

Fix each line, re-run, repeat until you see:

```
PASS — KB is ready for first use (7 checks).
```

If check 7 keeps failing for two entries, their keywords overlap too much. Give
each the distinct terms a user would use for *that* topic specifically.

---

## Step 5 — Smoke-test with a real question

Ask the assistant (the `comms-qa` skill) a question your playbook should answer,
e.g. *"How should I open a status update for an exec?"* A good answer:

- comes back with guidance **from your playbook's own words**, and
- **cites the entry file** it came from (e.g. `Sources: exec-updates.md`).

If it cites the wrong entry, strengthen that topic's keywords (Step 3) and
re-validate. If it says the KB does not cover the question and it should, you are
missing an entry — export that page and start again at Step 1.

You can also add your own cases to `_shared/knowledge/SMOKE-TEST.md` (query →
expected entry → expected passage) so future KB edits are checked automatically.

---

## Quick reference

```
cd skills/ai-writing-suite
python3 tools/kb_ingest.py export --out _shared/knowledge     # shape pages
#   ...review and fix TODO markers...
python3 tools/kb_validate.py _shared/knowledge                # must print PASS
#   ...ask comms-qa a real question, confirm the citation...
```

Both scripts are pure Python standard library — nothing to install, and they run
the same on Claude, Codex, Cursor, and RovoDev.
