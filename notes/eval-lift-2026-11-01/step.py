"""Per-step regression gate for the skill-lift eval (pre-registered in README.md, "Step gate").

Three arms per item: `bare` and `main` (cached v0 outputs on the 24 frozen items; freshly
generated for any step-specific extra items) and `new` (the step's candidate skill, fresh).

  python3 -I step.py prep    --run RUN [--extra RUN/extra_items.json]
  python3 -I step.py packets --run RUN --v0 result.json --arms RUN/arms.json [--arms RUN/arms_k2.json]
  python3 -I step.py score   --run RUN --evals EVALS_DIR

prep    writes RUN/items_new.json (frozen + extra, arm view) and RUN/items_extra.json.
packets writes RUN/packet_p1.txt, RUN/packet_p2.txt and RUN/perms.json (labels -> arms).
score   reads RUN/judges.json, writes RUN/report.md and RUN/gate.json, prints the report.
With two --arms files (a K=2 re-run), `new` outputs from both runs are judged as `new` and `new2`
and the gate uses their mean.
"""
import argparse
import difflib
import json
import math
import os
import re
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
FROZEN = os.path.join(HERE, "items.json")
LABELS = "ABCDEF"

NUM = re.compile(r"(?<![\w.])[-+]?\$?\d[\d,]*(?:\.\d+)?(?:%|pp|k|ms|x)?")
HEDGES = ["may", "might", "could", "likely", "possibly", "suggest", "appears", "not yet", "preliminary",
          "not significant", "not ruled out", "cannot separate", "not confirmed", "hypothesis", "as far as we know",
          "still being assessed", "may not generalize", "investigating", "don't know", "not sure"]


def load_items(run):
    items = json.load(open(FROZEN, encoding="utf-8"))["items"]
    for i in items:
        i["frozen"] = True
    extra_p = os.path.join(run, "extra_items.json")
    if os.path.exists(extra_p):
        for i in json.load(open(extra_p, encoding="utf-8"))["items"]:
            i["frozen"] = False
            items.append(i)
    return items


def cmd_prep(a):
    os.makedirs(a.run, exist_ok=True)
    if a.extra and os.path.abspath(a.extra) != os.path.abspath(os.path.join(a.run, "extra_items.json")):
        json.dump(json.load(open(a.extra, encoding="utf-8")), open(os.path.join(a.run, "extra_items.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    items = load_items(a.run)
    view = lambda xs: {"items": [{"id": i["id"], "request": i["request"]} for i in xs]}
    json.dump(view(items), open(os.path.join(a.run, "items_new.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    extra = [i for i in items if not i["frozen"]]
    if extra:
        json.dump(view(extra), open(os.path.join(a.run, "items_extra.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"{len(items)} items ({len(extra)} extra)")


def cmd_packets(a):
    items = load_items(a.run)
    v0 = json.load(open(a.v0, encoding="utf-8"))["arms"]
    outs = {"bare": {o["id"]: o for o in v0["bare"]["items"]}, "main": {o["id"]: o for o in v0["suite-main"]["items"]}}
    for k, path in enumerate(a.arms):
        arms = json.load(open(path, encoding="utf-8"))["arms"]
        outs["new" if k == 0 else f"new{k + 1}"] = {o["id"]: o for o in arms["new"]["items"]}
        if k == 0:
            for base, key in (("bare", "bare_extra"), ("main", "main_extra")):
                for o in arms.get(key, {}).get("items", []):
                    outs[base][o["id"]] = o
    arm_names = list(outs)
    perms = {"p1": {}, "p2": {}}
    texts = {"p1": [], "p2": []}
    for idx, it in enumerate(items):
        order = [arm_names[(j + idx) % len(arm_names)] for j in range(len(arm_names))]
        for pk, seq in (("p1", order), ("p2", order[::-1])):
            perms[pk][it["id"]] = {LABELS[j]: arm for j, arm in enumerate(seq)}
            block = [f"### Item {it['id']}", "AUTHOR'S REQUEST:", it["request"], ""]
            for j, arm in enumerate(seq):
                o = outs[arm].get(it["id"])
                text = o["output"] if o else "(no output)"
                note = f"\n[Message to author: {o['notes'].strip()}]" if o and o.get("notes", "").strip() else ""
                block.append(f"--- Candidate {LABELS[j]} ---\n{text}{note}\n")
            texts[pk].append("\n".join(block))
    for pk in texts:
        open(os.path.join(a.run, f"packet_{pk}.txt"), "w", encoding="utf-8").write("\n\n".join(texts[pk]))
    json.dump({"arm_names": arm_names, "perms": perms, "outputs": outs}, open(os.path.join(a.run, "perms.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("arms:", arm_names, "| items:", len(items))


def nums(t):
    return {re.sub(r"[,$]", "", m.group(0)).lstrip("+") for m in NUM.finditer(t)}


def has(t, w):
    return re.search(r"(?<![a-z])" + re.escape(w) + r"(?![a-z])", t.lower()) is not None


def wilson(k, n, z=1.96):
    if not n:
        return (float("nan"), float("nan"))
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    r = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - r) / d, (c + r) / d)


def cmd_score(a):
    sys.path.insert(0, a.evals)
    from detector.detector import analyze  # noqa: E402

    items = {i["id"]: i for i in load_items(a.run)}
    P = json.load(open(os.path.join(a.run, "perms.json"), encoding="utf-8"))
    judges = [j for j in json.load(open(os.path.join(a.run, "judges.json"), encoding="utf-8"))["judges"] if j]
    arms = P["arm_names"]
    # judge metrics per arm per item (summed over orderings)
    ws = defaultdict(lambda: defaultdict(int))
    mc = defaultdict(lambda: defaultdict(int))
    unsup = defaultdict(lambda: defaultdict(int))
    over = defaultdict(lambda: defaultdict(int))
    for j in judges:
        for e in j["items"]:
            perm = P["perms"][j["perm_key"]].get(e["id"])
            if not perm:
                continue
            for c in e["candidates"]:
                arm = perm.get(c["label"])
                if not arm:
                    continue
                ws[arm][e["id"]] += 1 if c["would_send"] else 0
                mc[arm][e["id"]] += len(c.get("meaning_changes", []))
                unsup[arm][e["id"]] += len(c.get("unsupported_claims_kept") or [])
                over[arm][e["id"]] += 1 if c.get("over_edited") else 0
    det = defaultdict(lambda: defaultdict(int))
    for arm in arms:
        for iid, o in P["outputs"][arm].items():
            if iid not in items:
                continue
            src, out = items[iid]["source_text"], o["output"]
            ref = src + "\n" + (items[iid].get("notes") or "")
            det[arm]["numbers_lost"] += len(nums(src) - nums(out))
            det[arm]["numbers_added"] += len(nums(out) - nums(ref))
            det[arm]["hedges_lost"] += sum(1 for h in HEDGES if has(src, h) and not has(out, h))
            det[arm]["edit_ratio_x100"] += round(100 * (1 - difflib.SequenceMatcher(None, src.split(), out.split()).ratio()))

    def agg(arm, ids):
        return {"would_send": sum(ws[arm][i] for i in ids), "n": 2 * len(ids),
                "meaning_changes": sum(mc[arm][i] for i in ids), "unsupported_kept": sum(unsup[arm][i] for i in ids),
                "over_edited": sum(over[arm][i] for i in ids)}

    frozen = [i for i in items if items[i]["frozen"]]
    extra = [i for i in items if not items[i]["frozen"]]
    hc = [i for i in frozen if items[i]["subset"] == "human-control"]
    news = [x for x in arms if x.startswith("new")]

    def mean_new(key, ids):
        vals = [agg(x, ids)[key] for x in news]
        return sum(vals) / len(vals)

    def mean_det(key):
        return sum(det[x][key] for x in news) / len(news)

    gate = {"checks": [], "pass": True}
    for base in ("main", "bare"):
        for label, new_v, base_v, ok in (
            ("would_send (frozen)", mean_new("would_send", frozen), agg(base, frozen)["would_send"], lambda n, b: n >= b),
            ("meaning_changes (frozen)", mean_new("meaning_changes", frozen), agg(base, frozen)["meaning_changes"], lambda n, b: n <= b),
            ("would_send (human controls)", mean_new("would_send", hc), agg(base, hc)["would_send"], lambda n, b: n >= b),
            ("numbers_lost", mean_det("numbers_lost"), det[base]["numbers_lost"], lambda n, b: n <= b),
            ("numbers_added", mean_det("numbers_added"), det[base]["numbers_added"], lambda n, b: n <= b),
            ("hedges_lost", mean_det("hedges_lost"), det[base]["hedges_lost"], lambda n, b: n <= b),
        ):
            passed = ok(new_v, base_v)
            gate["checks"].append({"vs": base, "metric": label, "new": new_v, "baseline": base_v, "pass": passed})
            gate["pass"] = gate["pass"] and passed

    lines = [f"# Step gate report: `{os.path.basename(os.path.normpath(a.run))}`", "",
             f"Arms: {', '.join(arms)}. Judges: {len(judges)} orderings. Frozen items: {len(frozen)}; extra items: {len(extra)}.", "",
             f"**GATE: {'PASS' if gate['pass'] else 'FAIL'}** (new must be no worse than `main` and `bare` on every check; mean over {len(news)} new run(s))", "",
             "| vs | check | new | baseline | ok |", "|---|---|---|---|---|"]
    for c in gate["checks"]:
        lines.append(f"| {c['vs']} | {c['metric']} | {c['new']:g} | {c['baseline']:g} | {'yes' if c['pass'] else '**NO**'} |")
    lines += ["", "## Judge metrics by subset", "",
              "| arm | subset | would send | 95% CI | meaning changes | unsupported kept | over-edited |", "|---|---|---|---|---|---|---|"]
    subsets = sorted({items[i]["subset"] for i in items})
    for arm in arms:
        for sub in subsets + ["FROZEN-ALL"]:
            ids = frozen if sub == "FROZEN-ALL" else [i for i in items if items[i]["subset"] == sub]
            if not ids:
                continue
            g = agg(arm, ids)
            if not g["n"]:
                continue
            lo, hi = wilson(g["would_send"], g["n"])
            lines.append(f"| {arm} | {sub} | {g['would_send']}/{g['n']} | {lo:.0%}-{hi:.0%} | {g['meaning_changes']} | {g['unsupported_kept']} | {g['over_edited']} |")
    lines += ["", "## Deterministic checks (all items)", "", "| arm | numbers lost | numbers added | hedges lost | mean edit ratio |", "|---|---|---|---|---|"]
    for arm in arms:
        n = max(1, len(P["outputs"][arm]))
        lines.append(f"| {arm} | {det[arm]['numbers_lost']} | {det[arm]['numbers_added']} | {det[arm]['hedges_lost']} | {det[arm]['edit_ratio_x100'] / 100 / n:.2f} |")
    lines += ["", "## Per-item would-send (sum of 2 orderings)", "", "| item | " + " | ".join(arms) + " |", "|---|" + "---|" * len(arms)]
    for i in items:
        lines.append(f"| {i} | " + " | ".join(str(ws[x][i]) for x in arms) + " |")
    report = "\n".join(lines) + "\n"
    open(os.path.join(a.run, "report.md"), "w", encoding="utf-8").write(report)
    json.dump(gate, open(os.path.join(a.run, "gate.json"), "w", encoding="utf-8"), indent=1)
    print(report)


ap = argparse.ArgumentParser()
sub = ap.add_subparsers(dest="cmd", required=True)
p = sub.add_parser("prep"); p.add_argument("--run", required=True); p.add_argument("--extra")
p = sub.add_parser("packets"); p.add_argument("--run", required=True); p.add_argument("--v0", required=True); p.add_argument("--arms", action="append", required=True)
p = sub.add_parser("score"); p.add_argument("--run", required=True); p.add_argument("--evals", required=True)
a = ap.parse_args()
{"prep": cmd_prep, "packets": cmd_packets, "score": cmd_score}[a.cmd](a)
