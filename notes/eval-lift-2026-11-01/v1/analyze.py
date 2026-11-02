"""v1 analysis per PREREG.md. stdlib only; run with python3 -I.

  analyze.py <run_dir> <items_heldout.json>

<run_dir>/judges/*.json : judge workflow results ({"judges":[{key, kind, model, items}]})
<run_dir>/keys/*.key.json : packet keys written by prep.py (abs: <arm>_k<n>.key.json; pair: pair_k<n>.key.json)
Writes <run_dir>/report.md and verdict.json.
"""
import glob
import json
import math
import os
import random
import sys
from collections import defaultdict

SEED = 20261101
B = 10000
SEVERE = {"number_change", "added_claim", "dropped_fact", "strengthened_certainty", "weakened_certainty", "scope_change"}


def load(p):
    return json.load(open(p, encoding="utf-8"))


def boot_ci(diffs, lo=0.05, hi=0.95):
    rng = random.Random(SEED)
    n = len(diffs)
    means = sorted(sum(diffs[rng.randrange(n)] for _ in range(n)) / n for _ in range(B))
    return sum(diffs) / n, means[int(lo * B)], means[int(hi * B) - 1]


def sign_p(wins, losses):
    n = wins + losses
    if n == 0:
        return 1.0
    return sum(math.comb(n, i) for i in range(wins + 1)) / 2 ** n  # P(X <= wins) for new's wins


def main(run, items_p):
    items = {i["id"]: i for i in load(items_p)["items"]}
    keys = {os.path.basename(p)[:-9]: load(p) for p in glob.glob(os.path.join(run, "keys", "*.key.json"))}
    judges = [j for p in sorted(glob.glob(os.path.join(run, "judges", "*.json"))) for j in load(p)["judges"] if j]
    S = defaultdict(lambda: defaultdict(list))   # arm -> item -> [0/1 per run]
    W = defaultdict(lambda: defaultdict(list))
    sent = {}
    pair = defaultdict(lambda: defaultdict(dict))  # k -> item -> {order: winner_arm|'tie'}
    models = set()
    for j in judges:
        models.add(j.get("model"))
        key = keys[j["key"]] if j["kind"] == "abs" else keys[j["key"].rsplit("_", 1)[0]]
        if j["kind"] == "abs":
            correct = total = 0
            rows = []
            for e in j["items"]:
                k = key.get(e["id"])
                if not k:
                    continue
                sev = any(c.get("type") in SEVERE for c in e.get("severe_changes", []))
                if k["kind"] == "sentinel":
                    total += 1
                    ok = (not sev and e["would_send"]) if k["expect"] == "good" else (sev or not e["would_send"])
                    correct += ok
                else:
                    rows.append((k["arm"], k["id"], sev, e["would_send"]))
            sent[j["key"]] = (correct, total)
            if total and correct / total < 0.8:
                continue  # PREREG: discard packets below 8/10 sentinel accuracy
            for arm, iid, sev, ws in rows:
                S[arm][iid].append(1 if sev else 0)
                W[arm][iid].append(1 if ws else 0)
        else:
            order = j["key"].rsplit("_", 1)[1]
            kk = j["key"].rsplit("_", 1)[0]
            for e in j["items"]:
                kd = key.get(e["id"])
                if not kd:
                    continue
                winner = "tie" if e["preferred"] == "tie" else kd[order][e["preferred"]]
                pair[kk][kd["id"]][order] = winner
    ho = sorted(items)
    mean = lambda xs: sum(xs) / len(xs)
    lines = ["# v1 report (pre-registered rules in PREREG.md)", "",
             f"Judge model(s): {sorted(m for m in models if m)}. Items: {len(ho)} held-out.", "",
             "## Sentinel accuracy per absolute packet (keep if >= 8/10)", ""]
    for k, (c, t) in sorted(sent.items()):
        lines.append(f"- {k}: {c}/{t}{'' if t and c / t >= 0.8 else '  **DISCARDED**'}")
    verdict = {"checks": []}

    def compare(a, b, metric, M, better_low):
        common = [i for i in ho if M[a].get(i) and M[b].get(i)]
        d = [mean(M[a][i]) - mean(M[b][i]) for i in common]
        if not d:
            return None
        m, lo, hi = boot_ci(d)
        if better_low:
            v = "WORSE" if lo > 0 else ("NOT WORSE" if hi <= 0.10 else "INCONCLUSIVE")
        else:
            v = "WORSE" if hi < 0 else ("NOT WORSE" if lo >= -0.10 else "INCONCLUSIVE")
        verdict["checks"].append({"vs": b, "metric": metric, "mean_diff": m, "ci90": [lo, hi], "n": len(d), "verdict": v})
        return f"| {a} − {b} | {metric} | {len(d)} | {m:+.3f} | [{lo:+.3f}, {hi:+.3f}] | **{v}** |"

    lines += ["", "## Paired item-level differences (bootstrap 90% CI)", "",
              "| contrast | metric | items | mean Δ | 90% CI | verdict |", "|---|---|---|---|---|---|"]
    for b in ("main", "bare"):
        for metric, M, low in (("S severe-change rate (lower better)", S, True), ("W would-send (higher better)", W, False)):
            r = compare("new", b, metric, M, low)
            if r:
                lines.append(r)
    lines += ["", "## Arm means", "", "| arm | S | W | items |", "|---|---|---|---|"]
    for arm in ("new", "main", "bare"):
        its = [i for i in ho if S[arm].get(i)]
        if its:
            lines.append(f"| {arm} | {mean([mean(S[arm][i]) for i in its]):.3f} | {mean([mean(W[arm][i]) for i in its]):.3f} | {len(its)} |")
    # Pairwise
    net = defaultdict(int)
    ties = 0
    for kk, per in pair.items():
        for iid, orders in per.items():
            if len(orders) == 2 and orders["AB"] == orders["BA"] and orders["AB"] != "tie":
                net[iid] += 1 if orders["AB"] == "new" else -1
            else:
                ties += 1
    wins = sum(1 for v in net.values() if v > 0)
    losses = sum(1 for v in net.values() if v < 0)
    p = sign_p(wins, losses)
    pv = "WORSE" if p < 0.10 and losses > wins else "NOT WORSE"
    verdict["checks"].append({"vs": "main", "metric": "pairwise", "new_items": wins, "main_items": losses, "p_main_better": p, "verdict": pv})
    lines += ["", "## Pairwise new vs main (a side wins only if both orders agree)", "",
              f"Item-level net: new preferred on {wins} items, main on {losses}; non-decisive pairs: {ties}. "
              f"One-sided p(main better) = {p:.3f} → **{pv}**"]
    # Floor
    floor_ids = [i for i in ho if items[i].get("category") in ("clean_human", "terse_status")]
    if floor_ids and all(S["new"].get(i) for i in floor_ids):
        fs = mean([mean(S["new"][i]) for i in floor_ids])
        fw = mean([mean(W["new"][i]) for i in floor_ids])
        ok = fw >= 0.85 and fs <= 0.10
        verdict["checks"].append({"metric": "floor", "W": fw, "S": fs, "verdict": "PASS" if ok else "FAIL"})
        lines += ["", f"## Floor (clean_human + terse_status, {len(floor_ids)} items)", "",
                  f"new: W = {fw:.2f} (need ≥ 0.85), S = {fs:.2f} (need ≤ 0.10) → **{'PASS' if ok else 'FAIL'}**"]
    lines += ["", "## By category (mean S / W)", "", "| category | arm | S | W |", "|---|---|---|---|"]
    cats = sorted({items[i].get("category", "?") for i in ho})
    for c in cats:
        ids = [i for i in ho if items[i].get("category") == c]
        for arm in ("new", "main", "bare"):
            its = [i for i in ids if S[arm].get(i)]
            if its:
                lines.append(f"| {c} | {arm} | {mean([mean(S[arm][i]) for i in its]):.2f} | {mean([mean(W[arm][i]) for i in its]):.2f} |")
    worse = [c for c in verdict["checks"] if c["verdict"] in ("WORSE", "FAIL")]
    have = {c["metric"] for c in verdict["checks"] if "mean_diff" in c or c["metric"] == "floor"}
    if len(have) < 3 or not pair:
        worse.append({"metric": "missing data (need S, W, floor and pairwise)", "vs": "", "verdict": "FAIL"})
    verdict["ship"] = not worse
    if not worse:
        rule = "OPEN PRs (no WORSE / FAIL)"
    elif any(c["metric"].startswith("missing data") for c in worse):
        rule = "NO DECISION: missing data (need S, W, floor and pairwise)"
    else:
        rule = "BISECT (" + ", ".join(c["metric"] + " vs " + c.get("vs", "") for c in worse) + ")"
    lines += ["", f"## Ship rule: {rule}"]
    open(os.path.join(run, "report.md"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
    json.dump(verdict, open(os.path.join(run, "verdict.json"), "w", encoding="utf-8"), indent=1)
    print("\n".join(lines))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
