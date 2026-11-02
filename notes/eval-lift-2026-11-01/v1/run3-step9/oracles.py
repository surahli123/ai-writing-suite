"""Run 3 (step 9) deterministic oracles for the targeted set. See PREREG-run3.md.

  python3 -I oracles.py <run_dir> <s9_suite_root>

<run_dir>/outputs/<arm>_k<n>.json : arm results ({"items":[{id, output, notes}]}), arm in {new, main}
<run_dir>/items_targeted.json      : targeted items with gold fields
<s9_suite_root>                    : suite root whose evals/ provides fidelity.py and check_report.py
                                     (the repo checkout at the s9 tip, not the arm export)
Writes <run_dir>/oracles.json and prints a table.
"""
import glob
import json
import os
import re
import sys
from collections import defaultdict

RUN, SUITE = sys.argv[1], sys.argv[2]
sys.path.insert(0, os.path.join(SUITE, "evals"))
sys.path.insert(0, SUITE)
from fixtures.fidelity import fidelity_violations, status_coverage  # noqa: E402
from audit_report.check_report import _numbers, check_report, load_catalog_ids  # noqa: E402

CATALOG = load_catalog_ids()
BULLET = re.compile(r"^\s*(?:[-*•]|\d+[.)])\s+", re.M)
COMMIT = {"L1": "B", "L2": "B", "L3": "B", "L4": "B", "L5": "B", "L6": "C", "L7": "A", "L8": "A",
          "R1": "D+E", "R2": "D+E", "R2p": "D+E", "R3": "D+E"}


def ws(s):
    return re.sub(r"\s+", " ", s).strip()


def bullets(s):
    return len(BULLET.findall(s))


def nonempty(s):
    return len([ln for ln in s.splitlines() if ln.strip()])


def new_numbers(src, out):
    have = _numbers(src)
    return sorted(n for n in _numbers(out, fix_side=True) if n not in have)


def status_oracle(draft, out):
    v = [x for x in fidelity_violations(draft, out) if x[0] == "status"]
    gaps = status_coverage(draft, out)
    if v:
        return "fail", f"status moved: {v}"
    if gaps:
        return "unscored", f"unaligned: {gaps}"
    return "pass", ""


def strengths(out):
    m = re.search(r"^## What already reads well\s*\n(.*?)(?=^## |^\*\*Coverage|^\*\*AI-tell|\Z)", out, re.M | re.S)
    if not m:
        return None
    return [ln.strip()[2:] for ln in m.group(1).splitlines() if ln.strip().startswith("- ")]


def tiers(out):
    counts = {}
    for t in ("Critical", "Moderate", "Minor"):
        m = re.search(rf"^## {t}\s*\n(.*?)(?=^## |\Z)", out, re.M | re.S)
        body = m.group(1) if m else ""
        counts[t] = len([b for b in re.findall(r"^- (.*)", body, re.M) if b.strip().rstrip(".") != "None"])
    return counts


def judge_item(item, out):
    """Return list of (oracle_name, outcome, detail)."""
    c, d = item["category"], item["draft"]
    res = []
    if c == "L1":
        res.append(("identity", "pass" if ws(d) in ws(out) and abs(len(ws(out)) - len(ws(d))) < 3 else "fail", ""))
    if c in ("L2", "L3"):
        o, det = status_oracle(d, out)
        res.append(("status", o, det))
    if c == "L2":
        res.append(("bullet_count", "pass" if bullets(out) == bullets(d) else "fail", f"{bullets(d)}->{bullets(out)}"))
    if c == "L3":
        res.append(("no_added_lines", "pass" if nonempty(out) == nonempty(d) else "fail", f"{nonempty(d)}->{nonempty(out)}"))
    if c == "L4":
        res.append(("bullet_count", "pass" if bullets(out) == bullets(d) else "fail", f"{bullets(d)}->{bullets(out)}"))
    if c == "L5":
        res.append(("no_list", "pass" if bullets(out) == 0 else "fail", f"{bullets(out)} bullets"))
    if c in ("L6", "L7"):
        nn = new_numbers(d, out)
        res.append(("no_new_numbers", "pass" if not nn else "fail", str(nn)))
    if c == "L8":
        missing = [t for t in item["distinct_pair"] if t.lower() not in out.lower()]
        res.append(("distinct_kept", "pass" if not missing else "fail", str(missing)))
    if c.startswith("R"):
        ok, viols = check_report(out, CATALOG, draft=d)
        res.append(("report_contract", "pass" if ok else "fail", "; ".join(viols)[:300]))
        st = strengths(out) or []
        if c == "R1":
            praised = [b for b in st if not b.startswith("Nothing")]
            res.append(("no_praise", "pass" if not praised else "fail", str(praised)[:200]))
        if c in ("R2", "R2p"):
            sent = item["concrete_sentence"].lower()
            quotes = [q for b in st for q in re.findall(r'"([^"]+)"|“([^”]+)”', b) for q in [q[0] or q[1]]]
            outside = [q for q in quotes if q.lower() not in sent]
            res.append(("praise_only_concrete", "pass" if not outside else "fail", str(outside)[:200]))
    return res


def main():
    items = {i["id"]: i for i in json.load(open(os.path.join(RUN, "items_targeted.json"), encoding="utf-8"))["items"]}
    table = defaultdict(lambda: defaultdict(list))  # (item, oracle) -> arm -> [outcome per run]
    extra = defaultdict(lambda: defaultdict(list))  # pressure stats
    for p in sorted(glob.glob(os.path.join(RUN, "outputs", "*_k*.json"))):
        arm = os.path.basename(p).split("_k")[0]
        outs = {o["id"]: o for o in json.load(open(p, encoding="utf-8"))["items"]}
        for iid, it in items.items():
            out = outs.get(iid, {}).get("output", "")
            for name, outcome, det in judge_item(it, out):
                table[(iid, name)][arm].append((outcome, det))
            if it["category"] in ("R2", "R2p", "R1"):
                t = tiers(out)
                extra[iid][arm].append({"findings": sum(t.values()), "critical": t["Critical"]})
    rows, blocks = [], []
    for (iid, name), arms in sorted(table.items()):
        it = items[iid]
        cat = it["category"]
        fails = {a: sum(1 for o, _ in v if o != "pass") for a, v in arms.items()}
        n = {a: len(v) for a, v in arms.items()}
        maj = {a: fails[a] >= 2 for a in arms}
        rule = "pass" if cat.startswith("R") else "harm"
        if rule == "harm" and maj.get("new") and not maj.get("main"):
            blocks.append({"item": iid, "oracle": name, "commit": COMMIT[cat], "rule": "harm"})
        if rule == "pass" and maj.get("new"):
            blocks.append({"item": iid, "oracle": name, "commit": COMMIT[cat], "rule": "pass"})
        rows.append({"item": iid, "category": cat, "oracle": name, "commit": COMMIT[cat], "rule": rule,
                     "new_not_pass": f"{fails.get('new', 0)}/{n.get('new', 0)}",
                     "main_not_pass": f"{fails.get('main', 0)}/{n.get('main', 0)}",
                     "details": {a: [d for _, d in v] for a, v in arms.items()},
                     "outcomes": {a: [o for o, _ in v] for a, v in arms.items()}})
    res = {"rows": rows, "blocks": blocks, "pressure": {k: dict(v) for k, v in extra.items()}}
    json.dump(res, open(os.path.join(RUN, "oracles.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print("| item | cat | oracle | commit | rule | s9 not-pass | s8 not-pass |")
    print("|---|---|---|---|---|---|---|")
    for r in rows:
        print(f"| {r['item']} | {r['category']} | {r['oracle']} | {r['commit']} | {r['rule']} | {r['new_not_pass']} | {r['main_not_pass']} |")
    print("\nBLOCKS:", blocks or "none")
    print("PRESSURE:", json.dumps(res["pressure"]))


if __name__ == "__main__":
    main()
