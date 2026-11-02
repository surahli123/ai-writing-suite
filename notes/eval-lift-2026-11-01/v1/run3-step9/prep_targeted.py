"""Build the run-3 targeted judge packets (report-only questions; PREREG-run3.md).

  python3 -I prep_targeted.py <run_dir>

One packet per arm (new = s9, main = s8) holding all 3 runs, block ids disguised and
interleaved. Gold fields are shown to the judge. Notes are shown for L6 only.
Writes <run_dir>/keys/targeted_<arm>.key.json and <run_dir>/targeted_<arm>.txt.
"""
import hashlib
import json
import os
import sys

RUN = sys.argv[1]
items = json.load(open(os.path.join(RUN, "items_targeted.json"), encoding="utf-8"))["items"]
QUESTIONS = {
    "L2": "scans_better (did the rewrite make the list easier to scan than the original?) and template_forced (n/a).",
    "L3": "scans_better (are the subject lines easier to tell apart at a glance than the originals?).",
    "L4": "template_forced (were the decision, risk and ask bullets forced into one grammatical template?) and scans_better.",
    "L6": "conflicts_reported = how many GOLD conflicts the output or notes tell the author about; conflicts_false = how many reported issues are not real; invented = did the output add any number, sample size or interval that was not in the original?",
    "L7": "made_specific = were the vague bullets rewritten as specific claims using only facts from the original paragraph (yes / partial / no); invented = did it add any fact not in the original?",
    "L8": "same_unified = is the same-metric pair now called by one name; distinct_kept = are the two distinct terms still distinct and both present?",
    "R1": "tone_praise = does the review praise tone, effort, topic or general structure (anything not quoted from the draft)?",
    "R2": "tone_praise as in R1; praise_outside = does it praise any passage other than the gold concrete sentence?",
    "R2p": "tone_praise as in R1; praise_outside as in R2.",
    "R3": "r3_count = how many of the five evidence-free contrasts the review counts as the pattern (0-5); evidence_counted = does it count the evidence-backed sentence as a problem?",
}


def gold(it):
    keys = ("gold_statuses", "gold_conflicts", "concrete_sentence", "same_pair", "distinct_pair",
            "contrast_sentences", "evidence_sentence")
    return {k: it[k] for k in keys if it.get(k)}


for arm in ("new", "main"):
    rows = []
    for k in (1, 2, 3):
        outs = {o["id"]: o for o in json.load(open(os.path.join(RUN, "outputs", f"{arm}_k{k}.json"), encoding="utf-8"))["items"]}
        for it in items:
            if it["category"] not in QUESTIONS:
                continue
            o = outs.get(it["id"], {})
            rows.append((hashlib.sha1(f"{arm}{k}{it['id']}".encode()).hexdigest(), k, it, o))
    rows.sort()
    key, blocks = {}, []
    for n, (_, k, it, o) in enumerate(rows):
        did = f"b{n + 1:02d}"
        key[did] = {"item": it["id"], "category": it["category"], "k": k, "arm": arm}
        parts = [f"### Block {did} (category {it['category']})", "AUTHOR'S REQUEST:", it["request"], "",
                 "GOLD (what is true about the original):", json.dumps(gold(it), ensure_ascii=False), "",
                 "--- Assistant output ---", o.get("output", "(no output)")]
        if it["category"] == "L6":
            parts += ["", "--- Assistant notes to the author ---", o.get("notes", "") or "(none)"]
        parts += ["", "QUESTIONS: " + QUESTIONS[it["category"]]]
        blocks.append("\n".join(parts))
    os.makedirs(os.path.join(RUN, "keys"), exist_ok=True)
    json.dump(key, open(os.path.join(RUN, "keys", f"targeted_{arm}.key.json"), "w", encoding="utf-8"), indent=1)
    open(os.path.join(RUN, f"targeted_{arm}.txt"), "w", encoding="utf-8").write("\n\n".join(blocks))
    print(arm, len(blocks), "blocks")
