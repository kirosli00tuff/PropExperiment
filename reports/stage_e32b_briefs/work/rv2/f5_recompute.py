"""RV2 independent F5 band and verdict recomputation (spec 7 and LR-F5-IBKR) from F3_vol.json, F4 fees, SR80.json.
Compares with F5_holding.json for the given pair keys. Pairs: c_f = S + 0.5 + fee_rt/v; B = {h in 5..OC: G <= 1.10 minG,
DLL(or MLL)/(sigma_h v) >= 2, hold fits before flat-by-close}; own broker: G rule only. min G over 1,2,5..240,OC,cc,on."""
import json, math, sys
f3 = json.load(open("F3_vol.json"))["roots"]; f4 = json.load(open("F4_facts_unmasked.json")); f5 = json.load(open("F5_holding.json"))
ib = json.load(open("F4_venue_ibkr.json")); sr = json.load(open("work/F5/SR80.json"))["SR80"]["test"]
H = ["1", "2", "5", "15", "30", "60", "120", "240", "OC"]; CAND = ["5", "15", "30", "60", "120", "240", "OC"]
def ncap(h, L): return 1 if h == "OC" else min(20, L // int(h))
def minutes(t): hh, mm = t.split(":"); return int(hh) * 60 + int(mm)
for key in sys.argv[1:]:
    firm, code = key.split("|"); r3 = f3[code]; L = r3["L_main"]; v = f4["codes"][code]["tick_value_usd"]
    own = firm == "ibkr"
    if own:
        fee = ib["codes"][code]["fee_rt_usd"]; S = 1.0 if f4["codes"][code]["spread_S"]["value"] is None else f4["codes"][code]["spread_S"]["value"]
        lim = None; flat_ok = lambda h: True
    else:
        p = f4["pairs"][key]; fm = f4["firms"][firm]; fee = p["fee_rt_usd"]
        S = f4["codes"][code]["spread_S"]["value"]; S = 1.0 if S is None else S
        lim = fm["mll_50k"] if fm["dll_50k"] == "none" else fm["dll_50k"]
        fbc = fm["flat_by_close"]; fbc_pt = minutes(fbc["time"]) - (120 if fbc["tz"] == "CT" else 0)
        ms, me = (minutes(t) for t in r3["main_session_pt"]); end = min(me, fbc_pt)
        flat_ok = lambda h: (fbc_pt >= me) if h == "OC" else (ms + int(h) <= end)
    c_f = S + 0.5 + fee / v
    sig = {h: (r3["h"][h]["sigma"] if h != "OC" else r3["OC"]["sigma"]) for h in H}
    G = {h: c_f / sig[h] + sr / math.sqrt(ncap(h, L)) for h in H}
    for k in ("cc", "on"): G[k] = c_f / r3["overnight"][k]["sigma"] + sr
    gmin = min(G.values()); argmin = [h for h in G if abs(G[h] - gmin) <= 1e-12 * gmin]
    B = []
    for h in CAND:
        ok = G[h] <= 1.10 * gmin * (1 + 1e-12)
        if not own: ok = ok and lim / (sig[h] * v) >= 2 * (1 - 1e-12) and flat_ok(h)
        if ok: B.append(h)
    if not B or set(argmin) & {"1", "2"} or set(argmin) <= {"OC", "cc", "on"}: verdict = "fails"
    elif "OC" in B: verdict = "partly"
    else: verdict = "holds"
    row = f5["pairs"].get(key) or f5["own_broker"]["rows"].get(key)
    print(f"== {key}: c_f {c_f:.4f} (file {row['c_f']}) | minG {gmin:.6f} at {argmin} (file {row['G_min']:.6f} at {row['G_argmin']}) | B {B} (file {row['band']['members']}) | verdict {verdict} (file {row['verdict']['value']})")
    print("   G by h:", {h: round(G[h], 4) for h in G})
