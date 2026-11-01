"""Deterministic + judge aggregation for the lift eval.

usage: python3 -I score.py <lift_dir> <detector_evals_dir>
reads  <lift>/items.json, <lift>/result.json (workflow result: arms + judges + perms)
writes <lift>/scores.json and prints markdown tables.
"""
import difflib
import json
import math
import os
import re
import sys
from collections import defaultdict

lift, evals_dir = sys.argv[1], sys.argv[2]
sys.path.insert(0, evals_dir)
from detector.detector import analyze  # noqa: E402

items = {i["id"]: i for i in json.load(open(os.path.join(lift, "items.json"), encoding="utf-8"))["items"]}
res = json.load(open(os.path.join(lift, "result.json"), encoding="utf-8"))
ARMS = res["arm_names"]

NUM = re.compile(r"(?<![\w.])[-+]?\$?\d[\d,]*(?:\.\d+)?(?:%|pp|k|ms|x)?")
HEDGES = ["may", "might", "could", "likely", "possibly", "suggest", "appears", "not yet", "preliminary",
          "not significant", "not ruled out", "cannot separate", "not confirmed", "hypothesis", "as far as we know",
          "still being assessed", "may not generalize", "investigating", "don't know", "not sure"]
SCOPE = ["only", "about", "roughly", "approximately", "~", "most", "never", "all", "some", "first", "up to", "at least"]


def nums(t):
    return {re.sub(r"[,$]", "", m.group(0)).lstrip("+") for m in NUM.finditer(t)}


def has(t, w):
    if w == "~":
        return "~" in t
    return re.search(r"(?<![a-z])" + re.escape(w) + r"(?![a-z])", t.lower()) is not None


def edit_ratio(a, b):
    aw, bw = a.split(), b.split()
    return 1 - difflib.SequenceMatcher(None, aw, bw).ratio()


def wilson(k, n, z=1.96):
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    r = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - r) / d, (c + r) / d)


det = defaultdict(lambda: defaultdict(list))
per_item = defaultdict(dict)
for arm in ARMS:
    outs = {o["id"]: o for o in res["arms"][arm]["items"]}
    for iid, it in items.items():
        o = outs.get(iid)
        if not o:
            per_item[iid][arm] = {"missing": True}
            continue
        src, out = it["source_text"], o["output"]
        ref = src + "\n" + (it.get("notes") or "")
        s_src, s_out = analyze(src), analyze(out)
        lost_nums = sorted(nums(src) - nums(out))
        new_nums = sorted(nums(out) - nums(ref))
        lost_hedges = [h for h in HEDGES if has(src, h) and not has(out, h)]
        lost_scope = [w for w in SCOPE if has(src, w) and not has(out, w)]
        mp = it.get("must_preserve") or []
        mp_lost = [m for m in mp if m not in out]
        row = {"det_before": s_src["score"], "det_after": s_out["score"], "lost_nums": lost_nums, "new_nums": new_nums,
               "lost_hedges": lost_hedges, "lost_scope": lost_scope, "must_preserve_lost": mp_lost,
               "edit_ratio": round(edit_ratio(src, out), 3), "len_ratio": round(len(out.split()) / max(1, len(src.split())), 2)}
        per_item[iid][arm] = row
        det[arm][it["subset"]].append(row)

# judges: un-permute
J = defaultdict(lambda: defaultdict(lambda: {"send": 0, "n": 0, "changes": 0, "change_types": defaultdict(int),
                                               "rank_sum": 0.0, "best": 0, "unsupported": 0}))
judge_rows = []
for jr in res["judges"]:
    if not jr:
        continue
    for e in jr["items"]:
        iid = e["id"]
        perm = res["perms"][jr["perm_key"]][iid]  # label -> arm
        sub = items[iid]["subset"]
        ranks = e.get("reads_human_rank", [])
        for c in e["candidates"]:
            arm = perm.get(c["label"])
            if not arm:
                continue
            for key in (sub, "ALL"):
                a = J[arm][key]
                a["n"] += 1
                a["send"] += 1 if c["would_send"] else 0
                a["changes"] += len(c.get("meaning_changes", []))
                for mc in c.get("meaning_changes", []):
                    a["change_types"][mc.get("type", "other")] += 1
                a["unsupported"] += len(c.get("unsupported_claims_kept", []) or [])
                if c["label"] in ranks:
                    a["rank_sum"] += ranks.index(c["label"]) + 1
                if e.get("best") == c["label"]:
                    a["best"] += 1
            judge_rows.append({"judge": jr["perm_key"] + ":" + jr["chunk"], "item": iid, "arm": arm, **c})

SUBS = ["fresh-ds", "pr67-factbridge", "fixtures", "human-control", "ALL"]
out = {"per_item": per_item, "judge_rows": judge_rows}
print("## Judge results (2 orderings x items; would_send rate with Wilson 95% CI, mean meaning changes, mean reads-human rank 1=best)\n")
print("| arm | subset | n | would send | 95% CI | meaning changes / cand | unsupported kept / cand | mean rank | picked best |")
print("|---|---|---|---|---|---|---|---|---|")
summary = {}
for arm in ARMS:
    for sub in SUBS:
        a = J[arm][sub]
        if not a["n"]:
            continue
        lo, hi = wilson(a["send"], a["n"])
        summary.setdefault(arm, {})[sub] = {k: (dict(v) if isinstance(v, defaultdict) else v) for k, v in a.items()}
        print(f"| {arm} | {sub} | {a['n']} | {a['send']/a['n']:.0%} | {lo:.0%}-{hi:.0%} | {a['changes']/a['n']:.2f} | "
              f"{a['unsupported']/a['n']:.2f} | {a['rank_sum']/a['n']:.2f} | {a['best']} |")
print("\n## Meaning-change types (ALL)\n")
types = sorted({t for arm in ARMS for t in J[arm]["ALL"]["change_types"]})
print("| arm | " + " | ".join(types) + " |")
print("|---|" + "---|" * len(types))
for arm in ARMS:
    print(f"| {arm} | " + " | ".join(str(J[arm]["ALL"]["change_types"].get(t, 0)) for t in types) + " |")

print("\n## Deterministic checks (per subset: totals over items)\n")
print("| arm | subset | items | detector before->after (mean) | numbers lost | new numbers | hedges lost | scope words lost | must_preserve lost | mean edit ratio | mean len ratio |")
print("|---|---|---|---|---|---|---|---|---|---|---|")
for arm in ARMS:
    for sub in SUBS[:-1]:
        rows = det[arm][sub]
        if not rows:
            continue
        n = len(rows)
        print(f"| {arm} | {sub} | {n} | {sum(r['det_before'] for r in rows)/n:.1f} -> {sum(r['det_after'] for r in rows)/n:.1f} | "
              f"{sum(len(r['lost_nums']) for r in rows)} | {sum(len(r['new_nums']) for r in rows)} | "
              f"{sum(len(r['lost_hedges']) for r in rows)} | {sum(len(r['lost_scope']) for r in rows)} | "
              f"{sum(len(r['must_preserve_lost']) for r in rows)} | {sum(r['edit_ratio'] for r in rows)/n:.2f} | "
              f"{sum(r['len_ratio'] for r in rows)/n:.2f} |")
out["judge_summary"] = summary
json.dump(out, open(os.path.join(lift, "scores.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
