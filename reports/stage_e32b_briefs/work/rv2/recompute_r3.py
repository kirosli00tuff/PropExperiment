"""RV2 independent recomputation of Q4-Q7, C, the ordering and R4 from a combinations file (spec 8.3), compared with
an r3_out file. Written from the spec text, not from r3_score.py's helpers. Usage: recompute_r3.py <combos> <r3_out>"""
import json, math, sys
from fractions import Fraction as F
combos = json.load(open(sys.argv[1])); out = json.load(open(sys.argv[2]))
sr80 = F(str(combos["sr80_test"]["value"]))
ceiling = F(6000)
W = {"Q1": F("0.20"), "Q2": F("0.10"), "Q3": F("0.10"), "Q4": F("0.15"), "Q5": F("0.15"), "Q6": F("0.15"), "Q7": F("0.15")}
def fr(x): return None if x is None else F(str(x))
def band(x, steps):
    for lim, s in steps:
        if x <= lim: return s
    return 0
def ncap(h, L): return 1 if h == "OC" else min(20, L // int(h))
rows = {}
for c in combos["combinations"]:
    ms = c["members"]; own = c["venue"] == "ibkr"; h = str(c["h_c"])
    q = {k: fr(c[k]["value"]) for k in ("Q1", "Q2", "Q3")}
    # Q4: worst member (lowest score; among equal scores the larger x)
    xs = [fr(m["c_f_ticks"]) / fr(m["sigma_hc_ticks"]) for m in ms]
    q4s = [band(x, ((F("0.025"), 4), (F("0.05"), 3), (F("0.10"), 2), (F("0.20"), 1))) for x in xs]
    q["Q4"] = F(min(q4s))
    # Q5
    if len(ms) == 1: K = fr(ms[0]["K_test"])
    else:
        cls = [m["asset_class"] for m in ms]; pairs = [(i, j) for i in range(len(ms)) for j in range(i + 1, len(ms))]
        rho = sum(F("0.5") if cls[i] == cls[j] else F("0.3") for i, j in pairs) / len(pairs)
        K = sum(fr(m["K_test"]) for m in ms) / (1 + (len(ms) - 1) * rho)
    qq = sr80 * sr80 * 870 / K
    q["Q5"] = F(band(qq, ((F("0.05") ** 2, 4), (F("0.10") ** 2, 3), (F("0.20") ** 2, 2), (F("0.40") ** 2, 1))))
    # Q6
    q6s = []
    for m in ms:
        sv = fr(m["sigma_hc_ticks"]) * fr(m["tick_value_usd"])
        if own:
            d = (2 if fr(m["initial_margin_usd"]) > ceiling else 0) + (1 if fr(m["sigma_day_ticks"]) * fr(m["tick_value_usd"]) > F("0.02") * ceiling else 0)
        else:
            dll = fr(m["mll_usd"]) if m["dll_usd"] == "none" else fr(m["dll_usd"])
            r = dll / sv
            d = (2 if r < F("1.5") else 1 if r < 3 else 0)
            d += 1 if fr(m["payout_threshold_usd"]) > (fr(m["n_per_day"])) ** F(1) * 0 + sv * F(str(math.sqrt(float(m["n_per_day"])))) else 0
            d += 1 if fr(m["news_stop_events_per_week"]) >= 2 else 0
        q6s.append(max(0, 4 - d))
    q["Q6"] = F(min(q6s))
    dd = c["data"]; d7 = (1 if fr(dd["discovery_cost_usd"]) > 50 else 0) + (1 if fr(dd["all_data_cost_usd"]) > 200 else 0)
    mo = fr(dd["clean_test_window_months"]); d7 += 0 if mo >= 36 else 1 if mo >= 24 else 2
    q["Q7"] = F(max(0, 4 - d7))
    C = sum(W[k] * q[k] for k in W)
    Cr = F(math.floor(C * 100 + F(1, 2)), 100)
    gate = any(m.get("gate", {}).get(k) for m in ms for k in ("news_window_covers_event_trade", "overnight_needed_but_prohibited", "holds_past_flat_by_close")) or q["Q3"] == 0
    G = max(float(fr(m["c_f_ticks"]) / fr(m["sigma_hc_ticks"])) + float(sr80) / math.sqrt(ncap(h, int(m["L_main"]))) for m in ms)
    name = c["product"] or c["pool"]["name"]
    rows[c["id"]] = dict(q=q, C=C, Cr=Cr, gate=gate, G=G, name=name, venue=c["venue"], fam=c["family"], K=K)
# compare
mism = []
by = {r["id"]: r for r in out["combinations"]}
for cid, r in rows.items():
    o = by[cid]
    for k in ("Q4", "Q5", "Q6", "Q7"):
        if F(str(o[k])) != r["q"][k]: mism.append((cid, k, o[k], str(r["q"][k])))
    if F(str(o["C"])) != r["C"]: mism.append((cid, "C", o["C"], float(r["C"])))
    if F(str(o["C_rounded"])) != r["Cr"]: mism.append((cid, "Cr", o["C_rounded"], float(r["Cr"])))
    if (o["status"] != "eligible") != r["gate"]: mism.append((cid, "gate", o["status"], r["gate"]))
    if abs(o["G_hc"] - r["G"]) > 1e-9: mism.append((cid, "G", o["G_hc"], r["G"]))
    if abs(float(F(str(o["K_used"]))) - float(r["K"])) > 1e-6: mism.append((cid, "K", o["K_used"], float(r["K"])))
print("combos", len(rows), "mismatches", len(mism)); [print("  ", m) for m in mism[:40]]
# ordering
elig = [cid for cid, r in rows.items() if not r["gate"]]
key = lambda cid: (-rows[cid]["Cr"], -rows[cid]["q"]["Q1"], rows[cid]["G"], rows[cid]["name"], rows[cid]["venue"], rows[cid]["fam"])
mine = sorted(elig, key=key); theirs = [r["id"] for r in out["combinations"] if r["status"] == "eligible"]
print("eligible", len(mine), "order identical:", mine == theirs)
if mine != theirs:
    for i, (a, b) in enumerate(zip(mine, theirs)):
        if a != b: print("  first diff at rank", i + 1, a, b); break
# R4
picks, seen = [], set()
for cid in mine:
    k = (rows[cid]["name"], rows[cid]["fam"])
    if k in seen: continue
    seen.add(k); picks.append((cid, rows[cid]["name"], rows[cid]["fam"][:20], rows[cid]["venue"], float(rows[cid]["Cr"])))
    if len(picks) == 5: break
print("my R4:", picks); print("their R4:", [(p["id"], p["C_rounded"]) for p in out["R4"]["candidates"]])
own = [cid for cid in mine if rows[cid]["venue"] == "ibkr"]
print("my best own:", own[0] if own else None, "theirs:", out["best_own_broker"]["id"])
print("n >= 2.00 among my R4:", sum(1 for p in picks if p[4] >= 2))
