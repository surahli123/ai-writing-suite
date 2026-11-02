"""Deep-dive on the items that drive gate flips. usage: python3 -I items_deep.py <lift_dir> <runs_dir> <items.json>"""
import difflib, json, math, os, re, sys
from collections import defaultdict

lift, runs_dir, items_path = sys.argv[1], sys.argv[2], sys.argv[3]
ITEMS = {i["id"]: i for i in json.load(open(items_path, encoding="utf-8"))["items"]}
FROZEN = list(ITEMS)
norm = lambda t: re.sub(r"\s+", " ", (t or "")).strip()
v0 = json.load(open(os.path.join(lift, "result.json"), encoding="utf-8"))
RUNS = {}
for s in ["step0", "step1", "step2", "step3"]:
    P = json.load(open(os.path.join(runs_dir, s, "perms.json")))
    J = json.load(open(os.path.join(runs_dir, s, "judges.json")))["judges"]
    RUNS[s] = (P, J)


def verdicts(s, iid, arm):
    P, J = RUNS[s]
    out = []
    for j in J:
        perm = P["perms"][j["perm_key"]][iid]
        inv = {v: k for k, v in perm.items()}
        for e in j["items"]:
            if e["id"] == iid:
                for c in e["candidates"]:
                    if c["label"] == inv[arm]:
                        out.append((j["perm_key"], c["would_send"], len(c.get("meaning_changes") or []),
                                    [m["type"] + ": " + m["detail"][:110] for m in (c.get("meaning_changes") or [])], c.get("comment", "")[:200]))
    return out


def v0_verdicts(iid, arm):
    out = []
    for j in v0["judges"]:
        perm = v0["perms"][j["perm_key"]][iid]
        inv = {v: k for k, v in perm.items()}
        for e in j["items"]:
            if e["id"] == iid:
                for c in e["candidates"]:
                    if c["label"] == inv[arm]:
                        out.append((j["perm_key"], c["would_send"], len(c.get("meaning_changes") or []),
                                    [m["type"] + ": " + m["detail"][:110] for m in (c.get("meaning_changes") or [])], c.get("comment", "")[:200]))
    return out


def show(s, iid, arms=("main", "new")):
    P, _ = RUNS[s]
    print(f"\n######## {s} / {iid}  (subset {ITEMS[iid]['subset']})")
    print("SOURCE:", norm(ITEMS[iid]["source_text"])[:600])
    for arm in arms:
        o = P["outputs"][arm][iid]
        print(f"\n--- {arm} OUTPUT (edit ratio {1-difflib.SequenceMatcher(None, ITEMS[iid]['source_text'].split(), o['output'].split()).ratio():.2f}):")
        print(norm(o["output"])[:700])
        print(f"--- {arm} NOTES: {norm(o.get('notes'))[:400]}")
        for pk, ws, mc, det, com in verdicts(s, iid, arm):
            print(f"   [{pk}] would_send={ws} mc={mc} {det} | {com}")


show("step0", "memo-02-subtle")
show("step0", "narrshape-04-absent-ambiguity-en")
show("step1", "tweet-01-obvious")
show("step2", "fp-esl-03-memo", arms=("bare", "main", "new"))
show("step3", "memo-01-obvious")

print("\n\n######## overstep-05-payoff-en: main's output is the suite's own gold rewrite; judges reject it every time")
o = RUNS["step0"][0]["outputs"]["main"]["overstep-05-payoff-en"]
print("SOURCE:", norm(ITEMS["overstep-05-payoff-en"]["source_text"]))
print("MAIN  :", norm(o["output"]))
print("GOLD  :", norm(ITEMS["overstep-05-payoff-en"].get("reference_after", "")))
for s in RUNS:
    for pk, ws, mc, det, com in verdicts(s, "overstep-05-payoff-en", "main"):
        print(f"   [{s} {pk}] would_send={ws} mc={mc} {det} | {com[:150]}")

print("\n\n######## linkedin-01-obvious: main scored 0/2 in v0 (6 candidates) but 2,2,1,2 in steps (3 candidates). Same text.")
print("MAIN  :", norm(o := RUNS["step0"][0]["outputs"]["main"]["linkedin-01-obvious"] and RUNS["step0"][0]["outputs"]["main"]["linkedin-01-obvious"]["output"])[:500])
for pk, ws, mc, det, com in v0_verdicts("linkedin-01-obvious", "suite-main"):
    print(f"   [v0 {pk}] would_send={ws} mc={mc} {det} | {com[:160]}")
for s in RUNS:
    for pk, ws, mc, det, com in verdicts(s, "linkedin-01-obvious", "main"):
        print(f"   [{s} {pk}] would_send={ws} mc={mc} {det} | {com[:160]}")

print("\n\n######## fp-esl-03-memo (human control): bare 0/10 sent. What did bare do?")
print("SOURCE:", norm(ITEMS["fp-esl-03-memo"]["source_text"]))
print("BARE  :", norm(RUNS["step0"][0]["outputs"]["bare"]["fp-esl-03-memo"]["output"]))
for pk, ws, mc, det, com in v0_verdicts("fp-esl-03-memo", "bare"):
    print(f"   [v0 {pk}] would_send={ws} mc={mc} {det} | {com[:160]}")

print("\n\n######## ds-07-nullresult: bare 0/10 sent, mc=1 every time. What did bare do?")
src = ITEMS["ds-07-nullresult"]["source_text"]; out = RUNS["step0"][0]["outputs"]["bare"]["ds-07-nullresult"]["output"]
sm = difflib.SequenceMatcher(None, src.split(), out.split())
for tag, i1, i2, j1, j2 in sm.get_opcodes():
    if tag != "equal":
        print(f"   {tag}: '{' '.join(src.split()[i1:i2])}' -> '{' '.join(out.split()[j1:j2])}'")
for pk, ws, mc, det, com in v0_verdicts("ds-07-nullresult", "bare"):
    print(f"   [v0 {pk}] would_send={ws} mc={mc} {det} | {com[:160]}")

print("\n\n######## Deterministic hedges_lost: which items/words produce bare=5, main=2?")
HEDGES = ["may", "might", "could", "likely", "possibly", "suggest", "appears", "not yet", "preliminary", "not significant", "not ruled out", "cannot separate", "not confirmed", "hypothesis", "as far as we know", "still being assessed", "may not generalize", "investigating", "don't know", "not sure"]
has = lambda t, w: re.search(r"(?<![a-z])" + re.escape(w) + r"(?![a-z])", t.lower()) is not None
for arm in ("bare", "main", "new"):
    for s in ["step0"]:
        P, _ = RUNS[s]
        for iid in FROZEN:
            srcs = ITEMS[iid]["source_text"]; o = P["outputs"][arm][iid]["output"]
            lost = [h for h in HEDGES if has(srcs, h) and not has(o, h)]
            if lost:
                # show context of the hedge in source
                ctx = [re.search(r"[^.]*\b" + re.escape(h) + r"\b[^.]*", srcs, re.I).group(0).strip()[:90] for h in lost]
                print(f"   {arm:4s} {iid}: lost {lost} | src: {ctx}")

print("\n\n######## `new` unchanged-from-source counts per step (frozen 24) and share of its would-send that comes from unchanged items")
for s in RUNS:
    P, J = RUNS[s]
    unchanged = [i for i in FROZEN if norm(P["outputs"]["new"][i]["output"]) == norm(ITEMS[i]["source_text"])]
    ws_unch = sum(1 for i in unchanged for v in verdicts(s, i, "new") if v[1])
    ws_all = sum(1 for i in FROZEN for v in verdicts(s, i, "new") if v[1])
    m_unch = [i for i in FROZEN if norm(P["outputs"]["main"][i]["output"]) == norm(ITEMS[i]["source_text"])]
    print(f"   {s}: new unchanged on {len(unchanged)}/24 (main: {len(m_unch)}); would-send from unchanged items {ws_unch}/{ws_all}; by subset: "
          + ", ".join(f"{sub}={sum(1 for i in unchanged if ITEMS[i]['subset']==sub)}" for sub in ["fresh-ds", "human-control", "fixtures", "pr67-factbridge"]))

print("\n\n######## exact binomial for position effects")
def p_ge(k, n, p): return sum(math.comb(n, i) * p**i * (1-p)**(n-i) for i in range(k, n+1))
print(f"   v0: best at position B 18/48, P(X>=18|p=1/6) = {p_ge(18, 48, 1/6):.4f}")
print(f"   steps: best at position A 98/222, P(X>=98|p=1/3) = {p_ge(98, 222, 1/3):.5f}")
