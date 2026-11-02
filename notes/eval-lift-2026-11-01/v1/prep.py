"""Prepare v1 judge packets (see PREREG.md). stdlib only; run with python3 -I.

  prep.py arms-view  <items.json> <out.json>
      -> {"items":[{id, request}]} for the arm agents
  prep.py abs  <items.json> <outputs.json> <arm_key> <fixtures_dir> <out_prefix>
      -> <out_prefix>.txt   absolute packet: request + one candidate per item, NOTES HIDDEN,
                            10 sentinels interleaved under disguised ids
         <out_prefix>.key.json  {disguised_id: {"kind": "item"|"sentinel", "id":..., "expect": "good"|"bad"}}
  prep.py pair <items.json> <new_outputs.json> <main_outputs.json> <out_prefix>
      -> <out_prefix>_AB.txt / _BA.txt (new first / main first), notes hidden, + <out_prefix>.key.json

<items.json> is {"items":[{id, request, ...}]}. <outputs.json> is an arm result {"items":[{id, output, notes}]}.
"""
import json
import os
import sys

SENTINEL_GOOD = ["restraint-01-clean-human-en", "fidelity-01-ds-readout-en", "fidelity-02-scope-en",
                 "overstep-07-evidence-answered-en"]
SENTINEL_BAD = ["fail-fidelity-units-en", "fail-fidelity-significance-en", "fail-fidelity-hope-to-fact-en",
                "fail-restraint-overedit-en", "fail-stance-dropped-en", "fail-fabricated-number-en"]


def load(p):
    return json.load(open(p, encoding="utf-8"))


def sentinels(fixtures_dir):
    good = {f["id"]: f for f in load(os.path.join(fixtures_dir, "fixtures.json"))["fixtures"]}
    bad = {f["id"]: f for f in load(os.path.join(fixtures_dir, "fixtures_fail.json"))["fixtures"]}
    out = []
    for sid in SENTINEL_GOOD:
        f = good[sid]
        out.append((sid, "good", f["before"], f["after"]))
    for sid in SENTINEL_BAD:
        f = bad[sid]
        out.append((sid, "bad", f["before"], f["after"]))
    return out


def block(did, request, candidates):
    lines = [f"### Item {did}", "AUTHOR'S REQUEST:", request, ""]
    for lab, text in candidates:
        lines.append(f"--- Candidate {lab} ---\n{text}\n")
    return "\n".join(lines)


def cmd_arms_view(items_p, out_p):
    items = load(items_p)["items"]
    json.dump({"items": [{"id": i["id"], "request": i["request"]} for i in items]},
              open(out_p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"{len(items)} items")


def cmd_abs(items_p, outputs_p, arm_key, fixtures_dir, prefix):
    items = load(items_p)["items"]
    outs = {o["id"]: o for o in load(outputs_p)["items"]}
    sents = sentinels(fixtures_dir)
    rows = [("item", i["id"], i["request"], outs.get(i["id"], {}).get("output", "(no output)"), None) for i in items]
    # Interleave sentinels at fixed, spread positions (deterministic: every ~3rd slot).
    for n, (sid, exp, before, after) in enumerate(sents):
        pos = min(len(rows), 2 + n * (len(rows) + len(sents)) // len(sents))
        rows.insert(pos, ("sentinel", sid, f"Polish this so it doesn't read AI-generated:\n\n{before}", after, exp))
    key, blocks = {}, []
    for n, (kind, rid, req, cand, exp) in enumerate(rows):
        did = f"q{n + 1:02d}"
        key[did] = {"kind": kind, "id": rid, "expect": exp, "arm": arm_key}
        blocks.append(block(did, req, [("A", cand)]))
    open(prefix + ".txt", "w", encoding="utf-8").write("\n\n".join(blocks))
    json.dump(key, open(prefix + ".key.json", "w", encoding="utf-8"), indent=1)
    print(f"{prefix}: {len(rows)} blocks ({len(sents)} sentinels)")


def cmd_pair(items_p, new_p, main_p, prefix):
    items = load(items_p)["items"]
    new = {o["id"]: o for o in load(new_p)["items"]}
    main = {o["id"]: o for o in load(main_p)["items"]}
    key = {}
    for order in ("AB", "BA"):
        blocks = []
        for n, it in enumerate(items):
            did = f"p{n + 1:02d}"
            a, b = new.get(it["id"], {}).get("output", "(no output)"), main.get(it["id"], {}).get("output", "(no output)")
            cands = [("A", a), ("B", b)] if order == "AB" else [("A", b), ("B", a)]
            blocks.append(block(did, it["request"], cands))
            key.setdefault(did, {"id": it["id"]})[order] = {"A": "new", "B": "main"} if order == "AB" else {"A": "main", "B": "new"}
        open(f"{prefix}_{order}.txt", "w", encoding="utf-8").write("\n\n".join(blocks))
    json.dump(key, open(prefix + ".key.json", "w", encoding="utf-8"), indent=1)
    print(f"{prefix}: {len(items)} pairs x 2 orders")


if __name__ == "__main__":
    cmd, args = sys.argv[1], sys.argv[2:]
    {"arms-view": cmd_arms_view, "abs": cmd_abs, "pair": cmd_pair}[cmd](*args)
