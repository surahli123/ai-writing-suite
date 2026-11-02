"""Adversarial re-analysis of the skill-lift eval. stdlib only.

usage: python3 -I analyze.py <lift_dir> <runs_dir> <items.json>
  lift_dir: holds result.json (v0)
  runs_dir: holds step0..step3/{perms.json,judges.json,extra_items.json,arms.json,arms_k2.json}
"""
import difflib
import json
import math
import os
import re
import sys
from collections import Counter, defaultdict
from itertools import combinations

lift, runs_dir, items_path = sys.argv[1], sys.argv[2], sys.argv[3]
ITEMS = {i["id"]: i for i in json.load(open(items_path, encoding="utf-8"))["items"]}
FROZEN = list(ITEMS)
HC = [i for i in FROZEN if ITEMS[i]["subset"] == "human-control"]


def norm(t):
    return re.sub(r"\s+", " ", (t or "")).strip()


def edit_ratio(a, b):
    return 1 - difflib.SequenceMatcher(None, a.split(), b.split()).ratio()


def binom_two_sided(k, n):
    """exact two-sided sign test p-value for k successes of n (p=0.5)"""
    if n == 0:
        return float("nan")
    lo = min(k, n - k)
    p = sum(math.comb(n, i) for i in range(0, lo + 1)) / 2 ** n
    return min(1.0, 2 * p)


def kappa(pairs):
    """Cohen's kappa for list of (a,b) booleans"""
    n = len(pairs)
    if n == 0:
        return float("nan")
    po = sum(1 for a, b in pairs if a == b) / n
    pa = sum(1 for a, _ in pairs if a) / n
    pb = sum(1 for _, b in pairs if b) / n
    pe = pa * pb + (1 - pa) * (1 - pb)
    return (po - pe) / (1 - pe) if pe < 1 else float("nan")


# ---------------------------------------------------------------- load runs
RUNS = {}  # run -> {"outputs": arm->id->{output,notes}, "rows": [...], "arms": [...], "extra": {...}}


def add_rows(run, perms, judges, outputs, arms, extra_items):
    rows = []
    for j in judges:
        if not j:
            continue
        for e in j["items"]:
            perm = perms[j["perm_key"]].get(e["id"])
            if not perm:
                continue
            labels = sorted(perm)
            ranks = e.get("reads_human_rank") or []
            for c in e["candidates"]:
                arm = perm.get(c["label"])
                if not arm:
                    continue
                rows.append({
                    "run": run, "judge": j["perm_key"] + (":" + j["chunk"] if "chunk" in j else ""),
                    "perm": j["perm_key"], "item": e["id"], "label": c["label"],
                    "pos": labels.index(c["label"]), "k": len(labels), "arm": arm,
                    "ws": bool(c["would_send"]), "mc": len(c.get("meaning_changes") or []),
                    "mc_types": [m.get("type", "other") for m in (c.get("meaning_changes") or [])],
                    "over": bool(c.get("over_edited")), "best": e.get("best") == c["label"],
                    "rank": (ranks.index(c["label"]) + 1) if c["label"] in ranks else None,
                    "comment": c.get("comment", ""),
                })
    RUNS[run] = {"outputs": outputs, "rows": rows, "arms": arms, "extra": extra_items}


v0 = json.load(open(os.path.join(lift, "result.json"), encoding="utf-8"))
v0_out = {a: {o["id"]: o for o in v0["arms"][a]["items"]} for a in v0["arm_names"]}
# alias v0 arm names to the step-run names so identical text lines up
v0_out["main"] = v0_out["suite-main"]
add_rows("v0", v0["perms"], v0["judges"], v0_out, v0["arm_names"], {})
for r in RUNS["v0"]["rows"]:
    if r["arm"] == "suite-main":
        r["arm"] = "main"

for s in sorted(os.listdir(runs_dir)):
    pj = os.path.join(runs_dir, s, "perms.json")
    jj = os.path.join(runs_dir, s, "judges.json")
    if not (os.path.exists(pj) and os.path.exists(jj)):
        continue
    P = json.load(open(pj, encoding="utf-8"))
    J = json.load(open(jj, encoding="utf-8"))["judges"]
    extra = {}
    ep = os.path.join(runs_dir, s, "extra_items.json")
    if os.path.exists(ep):
        extra = {i["id"]: i for i in json.load(open(ep, encoding="utf-8"))["items"]}
    add_rows(s, P["perms"], J, P["outputs"], P["arm_names"], extra)

STEPS = [r for r in RUNS if r != "v0"]
ALL_ITEMS = dict(ITEMS)
for r in STEPS:
    ALL_ITEMS.update(RUNS[r]["extra"])


def src(iid):
    return ALL_ITEMS[iid]["source_text"]


def agg(run, arm, ids):
    rows = [r for r in RUNS[run]["rows"] if r["arm"] == arm and r["item"] in ids]
    return {"ws": sum(r["ws"] for r in rows), "n": len(rows), "mc": sum(r["mc"] for r in rows),
            "over": sum(r["over"] for r in rows)}


def per_item(run, arm, key="ws"):
    d = defaultdict(int)
    for r in RUNS[run]["rows"]:
        if r["arm"] == arm:
            d[r["item"]] += int(r[key])
    return d


print("=" * 78)
print("0. SANITY: identical cached text for bare/main across runs?")
for arm in ("bare", "main"):
    base = RUNS["v0"]["outputs"][arm]
    for s in STEPS:
        o = RUNS[s]["outputs"][arm]
        same = sum(1 for i in FROZEN if norm(o[i]["output"]) == norm(base[i]["output"]) and norm(o[i].get("notes")) == norm(base[i].get("notes")))
        print(f"  {arm:5s} v0 vs {s}: {same}/{len(FROZEN)} frozen items byte-identical (output+notes)")

print("\n" + "=" * 78)
print("A. TEST-RETEST ON IDENTICAL TEXT: bare and main totals per run (frozen 24 items, 2 judges each)")
print(f"{'run':8s} | {'bare ws/48':>10s} {'bare mc':>8s} {'bare HC/10':>10s} {'bare over':>9s} | {'main ws/48':>10s} {'main mc':>8s} {'main HC/10':>10s} {'main over':>9s}")
series = defaultdict(list)
for run in ["v0"] + STEPS:
    b, m = agg(run, "bare", FROZEN), agg(run, "main", FROZEN)
    bh, mh = agg(run, "bare", HC), agg(run, "main", HC)
    print(f"{run:8s} | {b['ws']:>10d} {b['mc']:>8d} {bh['ws']:>10d} {b['over']:>9d} | {m['ws']:>10d} {m['mc']:>8d} {mh['ws']:>10d} {m['over']:>9d}")
    for k, v in (("bare_ws", b["ws"]), ("bare_mc", b["mc"]), ("bare_hc", bh["ws"]), ("main_ws", m["ws"]), ("main_mc", m["mc"]), ("main_hc", mh["ws"])):
        series[k].append(v)
for k, v in series.items():
    mu = sum(v) / len(v)
    sd = (sum((x - mu) ** 2 for x in v) / (len(v) - 1)) ** 0.5
    print(f"  {k:8s}: range {min(v)}-{max(v)}  mean {mu:.1f}  sd {sd:.2f}   (steps only: {v[1:]})")
print("  Note: v0 judged these texts among 6 candidates (and read the request from a file); steps judged among 3 with request inline.")

print("\nA2. Per-item would-send (sum of 2 orderings) for the SAME main/bare text across runs; cells that are not constant:")
for arm in ("bare", "main"):
    mats = {run: per_item(run, arm) for run in ["v0"] + STEPS}
    flip_items = []
    for i in FROZEN:
        vals = [mats[run][i] for run in ["v0"] + STEPS]
        if len(set(vals)) > 1:
            flip_items.append((i, vals))
    print(f"  {arm}: {len(flip_items)}/24 items change would-send sum across the 5 runs:")
    for i, vals in flip_items:
        print(f"     {i:38s} v0,s0,s1,s2,s3 = {vals}")
print("\nA3. Per-judgment stability: for each (item, arm in bare/main) there are 10 verdicts of identical text (5 runs x 2 orderings)")
for arm in ("bare", "main"):
    unanimous = split = 0
    for i in FROZEN:
        vs = [r["ws"] for run in ["v0"] + STEPS for r in RUNS[run]["rows"] if r["arm"] == arm and r["item"] == i]
        if len(set(vs)) == 1:
            unanimous += 1
        else:
            split += 1
    print(f"  {arm}: unanimous on {unanimous}/24 items, split verdicts on {split}/24")
print("  meaning_changes count for identical text, per (item,arm): min..max over 10 verdicts where max>0")
for arm in ("bare", "main"):
    out = []
    for i in FROZEN:
        vs = [r["mc"] for run in ["v0"] + STEPS for r in RUNS[run]["rows"] if r["arm"] == arm and r["item"] == i]
        if max(vs) > 0:
            out.append(f"{i.split('-')[0]}-{i.split('-')[1]}:{min(vs)}..{max(vs)}(zeros={vs.count(0)}/10)")
    print(f"  {arm}: " + "; ".join(out))

print("\n" + "=" * 78)
print("B. WITHIN-RUN AGREEMENT BETWEEN THE TWO ORDERINGS (p1 vs p2)")
for run in ["v0"] + STEPS:
    rows = RUNS[run]["rows"]
    by = defaultdict(dict)
    for r in rows:
        by[(r["item"], r["arm"])][r["perm"]] = r
    pairs = [(d["p1"]["ws"], d["p2"]["ws"]) for d in by.values() if "p1" in d and "p2" in d]
    mcp = [(d["p1"]["mc"], d["p2"]["mc"]) for d in by.values() if "p1" in d and "p2" in d]
    bestp = [(d["p1"]["best"], d["p2"]["best"]) for d in by.values() if "p1" in d and "p2" in d]
    overp = [(d["p1"]["over"], d["p2"]["over"]) for d in by.values() if "p1" in d and "p2" in d]
    agree = sum(1 for a, b in pairs if a == b)
    base_rate = sum(a for a, _ in pairs) / len(pairs)
    mc_exact = sum(1 for a, b in mcp if a == b) / len(mcp)
    mc_any = kappa([(a > 0, b > 0) for a, b in mcp])
    n_items = len({k[0] for k in by})
    best_agree = sum(1 for a, b in bestp if a and b)
    print(f"  {run:6s}: would_send agree {agree}/{len(pairs)} ({agree/len(pairs):.0%}), base rate sent={base_rate:.0%}, kappa={kappa(pairs):.2f} | "
          f"meaning_changes exact-count agree {mc_exact:.0%}, kappa(any change)={mc_any:.2f} | over_edited kappa={kappa(overp):.2f} | best agree {best_agree}/{n_items}")

print("\n" + "=" * 78)
print("C. HEADLINE REPLICATION: suite-main vs bare, paired item sign tests, recomputed in every run (identical text)")
print("   (v0 README: would-send 3/2 p=1.0; meaning changes fewer on 8, more on 1, p=0.04)")
for run in ["v0"] + STEPS:
    for key in ("mc", "ws"):
        b, m = per_item(run, "bare", key), per_item(run, "main", key)
        if key == "mc":
            better = sum(1 for i in FROZEN if m[i] < b[i]); worse = sum(1 for i in FROZEN if m[i] > b[i])
        else:
            better = sum(1 for i in FROZEN if m[i] > b[i]); worse = sum(1 for i in FROZEN if m[i] < b[i])
        p = binom_two_sided(better, better + worse)
        print(f"  {run:6s} {key}: main better on {better}, worse on {worse}, ties {24-better-worse}  -> sign test p={p:.3f}")
# pooled: 10 judgments per item
print("  Pooled over all 5 runs (10 verdicts per item):")
for key in ("mc", "ws"):
    b = defaultdict(int); m = defaultdict(int)
    for run in ["v0"] + STEPS:
        for i, v in per_item(run, "bare", key).items(): b[i] += v
        for i, v in per_item(run, "main", key).items(): m[i] += v
    if key == "mc":
        better = sum(1 for i in FROZEN if m[i] < b[i]); worse = sum(1 for i in FROZEN if m[i] > b[i])
    else:
        better = sum(1 for i in FROZEN if m[i] > b[i]); worse = sum(1 for i in FROZEN if m[i] < b[i])
    print(f"    {key}: main better {better}, worse {worse}, p={binom_two_sided(better, better+worse):.3f}; items: " +
          ", ".join(f"{i}({m[i]}v{b[i]})" for i in FROZEN if m[i] != b[i]))

print("\n" + "=" * 78)
print("D. POSITION / LABEL EFFECTS (pooled over runs; p1 and p2 are mirror orders so arms are balanced over positions)")
for grp, runs in (("v0 (k=6)", ["v0"]), ("steps (k=3)", STEPS)):
    rows = [r for run in runs for r in RUNS[run]["rows"]]
    k = rows[0]["k"]
    print(f"  {grp}:")
    print("    pos | n | would_send | best picked (expected 1/k) | mean reads-human rank | mean meaning changes")
    for pos in range(k):
        rr = [r for r in rows if r["pos"] == pos]
        ranks = [r["rank"] for r in rr if r["rank"]]
        print(f"    {chr(65+pos)}   | {len(rr):3d} | {sum(r['ws'] for r in rr)/len(rr):.0%}      | {sum(r['best'] for r in rr)/len(rr):.0%} (exp {1/k:.0%})          | {sum(ranks)/len(ranks):.2f}                | {sum(r['mc'] for r in rr)/len(rr):.2f}")
    # best-at-first-position binomial test
    n_items = len({(r['run'], r['judge'], r['item']) for r in rows})
    firsts = sum(1 for r in rows if r["pos"] == 0 and r["best"])
    # two-sided binomial vs 1/k
    def binom_p_ge(kk, n, p):
        return sum(math.comb(n, i) * p**i * (1-p)**(n-i) for i in range(kk, n+1))
    print(f"    best at position A: {firsts}/{n_items} judged items; P(X>={firsts} | p=1/{k}) = {binom_p_ge(firsts, n_items, 1/k):.3f}")
    lasts = sum(1 for r in rows if r["pos"] == k-1 and r["best"])
    print(f"    best at last position: {lasts}/{n_items}; P(X<={lasts}) = {1-binom_p_ge(lasts+1, n_items, 1/k):.3f}")

print("\n" + "=" * 78)
print("E. IS 'RETURN THE TEXT UNCHANGED' REWARDED? (normalized-whitespace identity; near = edit ratio < 0.03)")
def classify(run, arm, iid):
    o = RUNS[run]["outputs"][arm].get(iid)
    if not o:
        return None
    a, b = norm(src(iid)), norm(o["output"])
    if a == b:
        return "unchanged"
    return "near" if edit_ratio(a, b) < 0.03 else "changed"
tot = defaultdict(lambda: defaultdict(lambda: {"n": 0, "ws": 0, "mc": 0, "over": 0}))
by_arm_v0 = defaultdict(Counter)
for run in ["v0"] + STEPS:
    for r in RUNS[run]["rows"]:
        c = classify(run, r["arm"], r["item"])
        sub = ALL_ITEMS[r["item"]]["subset"] if r["item"] in ALL_ITEMS else "extra"
        for s in (sub, "ALL"):
            t = tot[s][c]; t["n"] += 1; t["ws"] += r["ws"]; t["mc"] += r["mc"]; t["over"] += r["over"]
for run in ["v0"]:
    for arm in RUNS[run]["arms"]:
        a2 = "main" if arm == "suite-main" else arm
        for i in FROZEN:
            by_arm_v0[arm][classify(run, a2, i)] += 1
print("  v0: how many of 24 outputs each arm returned unchanged / near-unchanged:")
for arm, c in by_arm_v0.items():
    print(f"    {arm:14s} unchanged={c['unchanged']:2d} near={c['near']:2d} changed={c['changed']:2d}")
print("  Judged outcomes by class (all runs pooled, all arms):")
print("    subset            class      n   would_send  mean mc  over_edited")
for s in ["fresh-ds", "human-control", "fixtures", "pr67-factbridge", "ALL"]:
    for c in ("unchanged", "near", "changed"):
        t = tot[s][c]
        if t["n"]:
            print(f"    {s:17s} {c:9s} {t['n']:4d}   {t['ws']/t['n']:.0%}        {t['mc']/t['n']:.2f}     {t['over']/t['n']:.0%}")
print("  Judge comments on unchanged outputs that still said would_send=false:")
for run in ["v0"] + STEPS:
    for r in RUNS[run]["rows"]:
        if classify(run, r["arm"], r["item"]) == "unchanged" and not r["ws"]:
            print(f"    [{run} {r['judge']}] {r['item']} {r['arm']}: {r['comment'][:140]}")

print("\n" + "=" * 78)
print("F. DO THE ASSISTANTS' NOTES LEAK THE ARM? (judges see notes as '[Message to author: ...]')")
print("  v0 note rate and length by arm:")
for arm in v0["arm_names"]:
    outs = v0_out[arm]
    withn = [o for o in outs.values() if norm(o.get("notes"))]
    L = [len(norm(o["notes"]).split()) for o in withn]
    print(f"    {arm:14s} notes on {len(withn):2d}/24, mean words {sum(L)/max(1,len(L)):.0f}, max {max(L) if L else 0}")
print("  Step runs: note rate for bare/main (cached) and new:")
for s in STEPS:
    parts = []
    for arm in RUNS[s]["arms"]:
        outs = RUNS[s]["outputs"][arm]
        withn = sum(1 for i in FROZEN if norm(outs.get(i, {}).get("notes")))
        parts.append(f"{arm}={withn}/24")
    print(f"    {s}: " + ", ".join(parts))
# would_send conditional on notes presence, within subset, pooled
print("  would_send | notes present vs absent (pooled, by subset):")
cond = defaultdict(lambda: defaultdict(lambda: [0, 0]))
for run in ["v0"] + STEPS:
    for r in RUNS[run]["rows"]:
        o = RUNS[run]["outputs"][r["arm"]].get(r["item"])
        has = bool(norm(o.get("notes"))) if o else False
        sub = ALL_ITEMS[r["item"]]["subset"]
        for s in (sub, "ALL"):
            cond[s][has][0] += 1; cond[s][has][1] += r["ws"]
for s in ["fresh-ds", "human-control", "fixtures", "pr67-factbridge", "ALL"]:
    a, b = cond[s][True], cond[s][False]
    print(f"    {s:17s} notes: {b[1]}/{b[0]} sent without ({b[1]/max(1,b[0]):.0%}), {a[1]}/{a[0]} sent with ({a[1]/max(1,a[0]):.0%})")
# leak vocabulary: suite-specific words appearing in notes/outputs seen by judges
LEAK = ["skill", "catalog", "fidelity", "voice profile", "preset", "tell", "false-positive", "false positive", "guardrail", "protocol",
        "named failure", "edit restraint", "unchanged", "term of art", "terms of art", "source packet", "authoriz", "notes:", "Notes:"]
print("  Suite-jargon tokens in notes shown to judges (count of candidates whose notes contain the token), per arm (v0 + steps new):")
arms_to_check = [(("v0", a), a) for a in v0["arm_names"]] + [((s, "new"), f"{s}:new") for s in STEPS]
for key, name in arms_to_check:
    run, arm = key
    outs = RUNS[run]["outputs"][arm]
    hits = Counter()
    for i, o in outs.items():
        n = (o.get("notes") or "").lower()
        for w in LEAK:
            if w.lower() in n:
                hits[w.lower()] += 1
    top = ", ".join(f"{w}:{c}" for w, c in hits.most_common(6))
    print(f"    {name:14s} {top}")
# simple leave-one-out nearest-centroid classifier: arm from notes, v0 (6 arms, 24 items)
def tokens(t):
    return re.findall(r"[a-z']+", (t or "").lower())
print("  Leave-one-out bag-of-words nearest-centroid: predict arm from NOTES text alone (v0, 6 arms, chance=17%):")
docs = [(arm, tokens(v0_out[arm][i].get("notes"))) for arm in v0["arm_names"] for i in FROZEN]
docs_ne = [(a, t) for a, t in docs if t]
def loo_acc(docs):
    correct = 0
    for idx, (a, t) in enumerate(docs):
        cents = defaultdict(Counter)
        for jdx, (a2, t2) in enumerate(docs):
            if jdx != idx:
                cents[a2].update(set(t2))
        q = set(t)
        best, bs = None, -1
        for a2, c in cents.items():
            nd = sum(1 for _, a3 in docs if a3 == a2) - (1 if a2 == a else 0)
            s = sum(c[w] / max(1, nd) for w in q) / max(1, len(q))
            if s > bs:
                bs, best = s, a2
        correct += best == a
    return correct / len(docs)
print(f"    accuracy on candidates with non-empty notes: {loo_acc(docs_ne):.0%} (n={len(docs_ne)})")
print(f"    accuracy on all 144 (empty notes -> most-likely-empty arm): {loo_acc([(a, t if t else ['<empty>']) for a, t in docs]):.0%}")
print("  Same on OUTPUT text (would the text itself identify the arm?):")
docs_o = [(arm, tokens(v0_out[arm][i]["output"])) for arm in v0["arm_names"] for i in FROZEN]
print(f"    accuracy: {loo_acc(docs_o):.0%} (n=144, chance 17%)  [outputs share the source so this is a hard test]")

print("\n" + "=" * 78)
print("G. HOW MANY ITEMS DISCRIMINATE? (per run, frozen items where arms differ in would-send sum / in mc sum)")
for run in ["v0"] + STEPS:
    arms = ["bare", "oneliner", "main", "suite-pr67", "cursor-unslop", "clay-unslop"] if run == "v0" else RUNS[run]["arms"]
    ws = {a: per_item(run, a, "ws") for a in arms}
    mc = {a: per_item(run, a, "mc") for a in arms}
    d_ws = [i for i in FROZEN if len({ws[a][i] for a in arms}) > 1]
    d_mc = [i for i in FROZEN if len({mc[a][i] for a in arms}) > 1]
    core = ["bare", "main"] if run == "v0" else ["bare", "main", "new"]
    d_core = [i for i in FROZEN if len({ws[a][i] for a in core}) > 1]
    print(f"  {run:6s}: ws differs on {len(d_ws)}/24 items (among {len(arms)} arms); mc differs on {len(d_mc)}/24; "
          f"ws differs among {core} on {len(d_core)}: {d_core}")
    sat = [i for i in FROZEN if all(ws[a][i] == 2 for a in core)]
    print(f"          all-core-arms-at-ceiling (2/2 sent) items: {len(sat)}/24")
# which items ever discriminate main vs new in any step
print("  Items whose would-send differs between `main` and `new` in each step (the whole gate signal):")
for s in STEPS:
    wm, wn = per_item(s, "main"), per_item(s, "new")
    mm, mn = per_item(s, "main", "mc"), per_item(s, "new", "mc")
    print(f"    {s}: ws  " + ", ".join(f"{i}({wm[i]}->{wn[i]})" for i in FROZEN if wm[i] != wn[i]))
    print(f"    {s}: mc  " + ", ".join(f"{i}({mm[i]}->{mn[i]})" for i in FROZEN if mm[i] != mn[i]))

print("\n" + "=" * 78)
print("H. LENGTH / EDIT-SIZE vs VERDICT (within-item: does the judge send the shorter / less-edited candidate?)")
for grp, runs in (("v0", ["v0"]), ("steps", STEPS)):
    rows = [r for run in runs for r in RUNS[run]["rows"]]
    pairs_len = []; pairs_edit = []
    byitem = defaultdict(list)
    for r in rows:
        o = RUNS[r["run"]]["outputs"][r["arm"]].get(r["item"])
        if not o: continue
        s = src(r["item"])
        r["_len"] = len(o["output"].split()) / max(1, len(s.split()))
        r["_edit"] = edit_ratio(norm(s), norm(o["output"]))
        byitem[(r["run"], r["judge"], r["item"])].append(r)
    # within-judge-item: compare each sent vs each not-sent candidate
    len_short_wins = len_cmp = edit_small_wins = edit_cmp = 0
    for k, rr in byitem.items():
        sent = [r for r in rr if r["ws"]]; not_sent = [r for r in rr if not r["ws"]]
        for a in sent:
            for b in not_sent:
                if a["_edit"] != b["_edit"]:
                    edit_cmp += 1; edit_small_wins += a["_edit"] < b["_edit"]
                if abs(a["_len"] - b["_len"]) > 0.02:
                    len_cmp += 1; len_short_wins += a["_len"] < b["_len"]
    print(f"  {grp}: among (sent, not-sent) pairs within the same judge+item, the SENT one was the less-edited {edit_small_wins}/{edit_cmp} "
          f"({edit_small_wins/max(1,edit_cmp):.0%}) and the shorter {len_short_wins}/{len_cmp} ({len_short_wins/max(1,len_cmp):.0%})")
    # sent rate by edit ratio bin, fixtures only (where editing is needed)
    bins = [(0, 0.03), (0.03, 0.2), (0.2, 0.4), (0.4, 0.6), (0.6, 1.01)]
    for sub in ("fixtures", "fresh-ds", "human-control"):
        parts = []
        for lo, hi in bins:
            rr = [r for r in rows if ALL_ITEMS[r["item"]]["subset"] == sub and lo <= r.get("_edit", -1) < hi]
            if rr:
                parts.append(f"[{lo:.2f},{hi:.2f}) n={len(rr)} sent={sum(r['ws'] for r in rr)/len(rr):.0%}")
        print(f"     {sub:14s} would_send by edit-ratio bin: " + " | ".join(parts))

print("\n" + "=" * 78)
print("I. GATE UNDER THE NULL: apply the step gate's judged checks to `main` text judged in run i as if it were `new`,")
print("   against `main` and `bare` judged in run j (identical text both sides). A fair gate passes ~100% here.")
checks_pass = Counter(); n_pairs = 0; full_pass = 0
detail = []
for i_run in STEPS:
    for j_run in STEPS:
        if i_run == j_run: continue
        n_pairs += 1
        new = {"ws": agg(i_run, "main", FROZEN)["ws"], "mc": agg(i_run, "main", FROZEN)["mc"], "hc": agg(i_run, "main", HC)["ws"]}
        ok_all = True
        for base in ("main", "bare"):
            b = {"ws": agg(j_run, base, FROZEN)["ws"], "mc": agg(j_run, base, FROZEN)["mc"], "hc": agg(j_run, base, HC)["ws"]}
            for key, cmp in (("ws", lambda n, b: n >= b), ("mc", lambda n, b: n <= b), ("hc", lambda n, b: n >= b)):
                ok = cmp(new[key], b[key]); checks_pass[(base, key)] += ok; ok_all &= ok
        full_pass += ok_all
        detail.append((i_run, j_run, ok_all))
print(f"  main-as-new vs main+bare baselines: full gate passes {full_pass}/{n_pairs} run-pairs")
for (base, key), c in sorted(checks_pass.items()):
    print(f"    check vs {base} {key}: pass {c}/{n_pairs}")
print("  per pair: " + ", ".join(f"{a}->{b}:{'PASS' if ok else 'FAIL'}" for a, b, ok in detail))
# same-run variant: the gate as actually run compares new (fresh) to main judged in the same packet. Null proxy:
# use the two orderings as two 'runs': main judged by p1 vs main judged by p2 within the same run.
print("  Within-run proxy (p1 verdicts on main as 'new' vs p2 verdicts on main as baseline, and vice versa):")
for s in STEPS:
    for a, b in (("p1", "p2"), ("p2", "p1")):
        def A(arm, perm, ids):
            rr = [r for r in RUNS[s]["rows"] if r["arm"] == arm and r["perm"] == perm and r["item"] in ids]
            return sum(r["ws"] for r in rr), sum(r["mc"] for r in rr), sum(r["ws"] for r in rr if r["item"] in HC)
        nw, nm, nh = A("main", a, FROZEN); bw, bm, bh = A("main", b, FROZEN)
        ok = nw >= bw and nm <= bm and nh >= bh
        print(f"    {s} {a} vs {b}: ws {nw} vs {bw}, mc {nm} vs {bm}, hc {nh} vs {bh} -> {'PASS' if ok else 'FAIL'}")

print("\n" + "=" * 78)
print("J. GENERATION VARIANCE OF `new` (step0/step1 have a second fresh generation arms_k2.json, not yet judged)")
for s in ("step0", "step1"):
    p = os.path.join(runs_dir, s, "arms_k2.json")
    if not os.path.exists(p): continue
    k2 = {o["id"]: o for o in json.load(open(p, encoding="utf-8"))["arms"]["new"]["items"]}
    k1 = RUNS[s]["outputs"]["new"]
    ident = 0; ers = []; lens = []
    notes_same = 0
    for i in FROZEN:
        a, b = norm(k1[i]["output"]), norm(k2[i]["output"])
        ident += a == b
        ers.append(edit_ratio(a, b))
        notes_same += norm(k1[i].get("notes")) == norm(k2[i].get("notes"))
    e_src1 = [edit_ratio(norm(src(i)), norm(k1[i]["output"])) for i in FROZEN]
    e_src2 = [edit_ratio(norm(src(i)), norm(k2[i]["output"])) for i in FROZEN]
    unchanged1 = sum(1 for i in FROZEN if norm(src(i)) == norm(k1[i]["output"]))
    unchanged2 = sum(1 for i in FROZEN if norm(src(i)) == norm(k2[i]["output"]))
    big = [(i, round(e, 2)) for i, e in zip(FROZEN, ers) if e > 0.3]
    print(f"  {s}: new vs new2 identical on {ident}/24 frozen items; mean word-edit distance between the two generations {sum(ers)/24:.2f} "
          f"(vs mean distance from source {sum(e_src1)/24:.2f} / {sum(e_src2)/24:.2f}); unchanged-from-source {unchanged1} vs {unchanged2}; notes identical {notes_same}/24")
    print(f"      items where the two generations differ by >0.30: {big}")
    # deterministic gate metrics for k2
    HEDGES = ["may", "might", "could", "likely", "possibly", "suggest", "appears", "not yet", "preliminary", "not significant", "not ruled out", "cannot separate", "not confirmed", "hypothesis", "as far as we know", "still being assessed", "may not generalize", "investigating", "don't know", "not sure"]
    def has(t, w): return re.search(r"(?<![a-z])" + re.escape(w) + r"(?![a-z])", t.lower()) is not None
    hl = lambda outs: sum(1 for i in FROZEN for h in HEDGES if has(src(i), h) and not has(outs[i]["output"], h))
    print(f"      hedges_lost (frozen): new={hl(k1)} new2={hl(k2)}")

print("\n" + "=" * 78)
print("K. META: meaning_changes type mix (how much of the 'fidelity' signal is the catch-all 'other'?)")
for run in ["v0"] + STEPS:
    c = Counter();
    for r in RUNS[run]["rows"]:
        if r["item"] in FROZEN:
            c.update(r["mc_types"])
    tot_ = sum(c.values())
    print(f"  {run:6s}: total {tot_:3d}; " + ", ".join(f"{k}={v}({v/max(1,tot_):.0%})" for k, v in c.most_common()))

print("\n" + "=" * 78)
print("L. EXTRA ITEMS: did they discriminate? (per step, would-send sums and mc for bare_extra/main_extra/new)")
for s in STEPS:
    ex = list(RUNS[s]["extra"])
    for arm in RUNS[s]["arms"]:
        w, m = per_item(s, arm), per_item(s, arm, "mc")
        print(f"  {s} {arm:5s}: " + ", ".join(f"{i}: ws={w[i]} mc={m[i]}" for i in ex))
