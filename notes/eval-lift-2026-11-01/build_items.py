"""Build the lift-eval item set: fresh DS drafts + PR #67 factbridge + main fixtures + human controls.

usage: python3 -I build_items.py <lift_dir> <drafts.json>
"""
import json
import os
import sys

lift = sys.argv[1]
drafts = {d["id"]: d["draft"] for d in json.load(open(sys.argv[2], encoding="utf-8"))}
briefs = json.load(open(os.path.join(lift, "briefs.json"), encoding="utf-8"))
main_fx = json.load(open(os.path.join(lift, "suite-main/skills/ai-writing-suite/evals/fixtures/fixtures.json"), encoding="utf-8"))["fixtures"]
pr_fx = json.load(open(os.path.join(lift, "suite-pr67/skills/ai-writing-suite/evals/fixtures/fixtures.json"), encoding="utf-8"))["fixtures"]
fps = json.load(open(os.path.join(lift, "suite-main/skills/ai-writing-suite/evals/fixtures/false_positives.json"), encoding="utf-8"))["samples"]

GENRE = {"tweet": "tweet", "linkedin": "LinkedIn post", "readme": "README section", "memo": "internal memo"}
items = []

for b in briefs:
    draft = drafts[b["id"]]
    if b["with_notes"]:
        req = (f"I drafted this {b['format']} for {b['audience']} from my analysis notes. "
               f"Polish it so it doesn't read AI-generated before I send it.\n\n"
               f"MY NOTES:\n{b['notes']}\n\nMY DRAFT:\n{draft}")
    else:
        req = (f"Polish this {b['format']} so it doesn't read AI-generated before I send it "
               f"to {b['audience']}.\n\n{draft}")
    items.append({"id": b["id"], "subset": "fresh-ds", "with_notes": b["with_notes"],
                  "notes": b["notes"], "source_text": draft, "request": req})

pr_by_id = {f["id"]: f for f in pr_fx}
for fid in ["factbridge-01-unsupported-cause-en", "factbridge-02-cooccurrence-en", "factbridge-04-supported-possibility-en"]:
    f = pr_by_id[fid]
    req = (f"Polish this sentence from my memo. My source note says: {f['source_context']}\n\n"
           f"MEMO SENTENCE:\n{f['before']}")
    items.append({"id": fid, "subset": "pr67-factbridge", "with_notes": True, "notes": f["source_context"],
                  "source_text": f["before"], "request": req, "reference_after": f["after"]})

main_by_id = {f["id"]: f for f in main_fx}
for fid in ["tweet-01-obvious", "linkedin-01-obvious", "memo-01-obvious", "memo-02-subtle",
            "overstep-05-payoff-en", "overstep-06-strawman-en", "narrshape-04-absent-ambiguity-en",
            "artifact-01-status-card-en"]:
    f = main_by_id[fid]
    req = f"Polish this {GENRE[f['genre']]} so it doesn't sound AI-written:\n\n{f['before']}"
    items.append({"id": fid, "subset": "fixtures", "with_notes": False, "notes": "",
                  "source_text": f["before"], "request": req, "reference_after": f["after"],
                  "must_preserve": [m for m in f.get("must_preserve", []) if m in f["before"]]})

fp_by_id = {s["id"]: s for s in fps}
for sid in ["fp-terse-04", "fp-pro-linkedin-07", "fp-pro-memo-09", "fp-academic-05", "fp-esl-03-memo"]:
    s = fp_by_id[sid]
    req = f"Polish this {GENRE[s['genre']]} before I send it:\n\n{s['text']}"
    items.append({"id": sid, "subset": "human-control", "with_notes": False, "notes": "",
                  "source_text": s["text"], "request": req})

json.dump({"items": items}, open(os.path.join(lift, "items.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(items), "items;", {k: sum(1 for i in items if i["subset"] == k) for k in ["fresh-ds", "pr67-factbridge", "fixtures", "human-control"]})
