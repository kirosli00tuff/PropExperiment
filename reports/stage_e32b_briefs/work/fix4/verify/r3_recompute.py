"""FixVerifier (F4) item 3: recompute Q4-Q7, C, the order, the R4 and the best own-broker for the primary and the five
sensitivity outputs from the spec 8.3 text (my own implementation, not r3_score.py), and compare with each r3 output.
Reads only the combinations JSON inputs and the r3 outputs."""
import hashlib
import json
import math
from fractions import Fraction as Fr
from pathlib import Path

B = Path(__file__).resolve().parents[3]
RUNS = {
    "primary": ("R2_combinations.json", "r3_out.json"),
    "q3only": ("work/R2/R2_combinations_q3only.json", "work/R2/r3_out_q3only.json"),
    "nozlw": ("work/R2/R2_combinations_nozlw.json", "work/R2/r3_out_nozlw.json"),
    "ts150_v2": ("work/R2/R2_combinations_ts150_v2.json", "work/R2/r3_out_ts150_v2.json"),
    "q3bleg": ("work/R2/R2_combinations_q3bleg.json", "work/R2/r3_out_q3bleg.json"),
    "v1": ("work/R2/R2_combinations_v1.json", "work/R2/r3_out_v1.json"),
}
W = {"Q1": Fr("0.20"), "Q2": Fr("0.10"), "Q3": Fr("0.10"), "Q4": Fr("0.15"), "Q5": Fr("0.15"), "Q6": Fr("0.15"),
     "Q7": Fr("0.15")}
T_TEST = 870


def fr(x):
    return Fr(x) if x is not None else None


def q4(c_f, sig):
    x = fr(c_f) / fr(sig)
    for lim, s in ((Fr("0.025"), 4), (Fr("0.05"), 3), (Fr("0.10"), 2), (Fr("0.20"), 1)):
        if x <= lim:
            return s, x
    return 0, x


def q5(sr80, k):
    q2 = fr(sr80) ** 2 * T_TEST / fr(k)   # q = SR80 sqrt(870)/sqrt(K); compare q^2 exactly
    for lim, s in ((Fr("0.05"), 4), (Fr("0.10"), 3), (Fr("0.20"), 2), (Fr("0.40"), 1)):
        if q2 <= lim * lim:
            return s, math.sqrt(float(q2))
    return 0, math.sqrt(float(q2))


def q6_prop(m):
    sv = fr(m["sigma_hc_ticks"]) * fr(m["tick_value_usd"])
    dll = m.get("dll_usd")
    if dll == "none":
        dll = m.get("mll_usd")   # spec 4's D convention: no DLL -> the MLL binds (r3 does the same; noted)
    d = 0
    if dll is None:
        d += 2
    else:
        ratio = fr(dll) / sv
        d += 2 if ratio < Fr("1.5") else (1 if ratio < 3 else 0)
    thr, n = m.get("payout_threshold_usd"), m.get("n_per_day")
    if thr is None or n is None:
        d += 1
    else:
        d += 1 if fr(thr) ** 2 > fr(n) * sv * sv else 0
    ev = m.get("news_stop_events_per_week")
    d += 1 if (ev is None or fr(ev) >= 2) else 0
    return max(0, 4 - d)


def q6_own(m, ceiling):
    d = 0
    mg = m.get("initial_margin_usd")
    d += 2 if (mg is None or fr(mg) > ceiling) else 0
    sd = m.get("sigma_day_ticks")
    d += 1 if (sd is None or fr(sd) * fr(m["tick_value_usd"]) > Fr("0.02") * ceiling) else 0
    return max(0, 4 - d)


def q7(data):
    disc, alld, months = data.get("discovery_cost_usd"), data.get("all_data_cost_usd"), data.get("clean_test_window_months")
    d = (1 if (disc is None or fr(disc) > 50) else 0) + (1 if (alld is None or fr(alld) > 200) else 0)
    d += 2 if months is None else (0 if fr(months) >= 36 else (1 if fr(months) >= 24 else 2))
    return max(0, 4 - d)


def ncap(h_c, l_main):
    return 1 if h_c == "OC" else min(20, int(math.floor(l_main / int(h_c))))


def rating(c, k):
    r = c.get(k)
    if not isinstance(r, dict) or r.get("value") is None or r.get("unknown") is True:
        return None
    return Fr(r["value"])


def score(c, sr80, ceiling, measured):
    members = c["members"]
    kind = "own_broker" if c["venue"] == "ibkr" else "prop"
    name = c["product"] if c.get("product") is not None else c["pool"]["name"]
    h_c = str(c["h_c"])
    qv = {k: rating(c, k) for k in ("Q1", "Q2", "Q3")}
    q4s = [q4(m["c_f_ticks"], m["sigma_hc_ticks"]) for m in members]
    worst = min(q4s, key=lambda t: (t[0], -t[1]))     # pool: the worst member (r3's reading; spec silent)
    qv["Q4"] = Fr(worst[0])
    if c.get("pool") is None:
        k_used, rho = fr(members[0]["K_test"]), None
    else:
        pairs = [(a, b) for i, a in enumerate(members) for b in members[i + 1:]]
        rs = []
        for a, b in pairs:
            key1, key2 = f"{a['code']}|{b['code']}", f"{b['code']}|{a['code']}"
            meas = measured.get(key1) or measured.get(key2)
            if meas:
                rs.append(fr(meas["value"]))
            else:
                rs.append(Fr("0.5") if a["asset_class"] == b["asset_class"] else Fr("0.3"))
        rho = sum(rs) / len(rs)
        k_used = sum(fr(m["K_test"]) for m in members) / (1 + (len(members) - 1) * rho)
    s5, qval = q5(sr80, k_used)
    qv["Q5"] = Fr(s5)
    gates = [k for m in members for k, v in (m.get("gate") or {}).items() if v is True]
    qv["Q6"] = Fr(min((q6_own(m, ceiling) if kind == "own_broker" else q6_prop(m)) for m in members))
    qv["Q7"] = Fr(q7(c.get("data") or {}))
    if qv["Q3"] == 0:
        gates.append("Q3=0")
    unrated = [k for k in ("Q1", "Q2", "Q3") if qv[k] is None]
    C = None if unrated else sum(W[k] * qv[k] for k in W)
    G = max(float(fr(m["c_f_ticks"]) / fr(m["sigma_hc_ticks"])) + float(sr80) / math.sqrt(ncap(h_c, m["L_main"]))
            for m in members)
    return {"id": c["id"], "name": name, "venue": c["venue"], "kind": kind, "family": c["family"], **qv, "C": C,
            "G": G, "K": k_used, "q": qval, "x": worst[1], "status": "excluded" if gates else ("unrated" if unrated else "eligible")}


def run(mode):
    inp, outp = RUNS[mode]
    d = json.loads((B / inp).read_text())
    o = json.loads((B / outp).read_text())
    h_in = hashlib.sha256((B / inp).read_bytes()).hexdigest()
    rec = o["inputs"]["combos"]
    rec_h = rec.get("sha256") if isinstance(rec, dict) else rec
    print(f"\n=== {mode}: {inp} sha256 {h_in[:16]} ; r3 output recorded input {str(rec_h)[:16]} match={str(rec_h) == h_in}")
    sr80 = Fr(d["sr80_test"]["value"]) if isinstance(d["sr80_test"], dict) else Fr(d["sr80_test"])
    ceil_raw = (d.get("own_account_capital_ceiling_usd") or {}).get("value")
    ceiling = Fr(ceil_raw) if ceil_raw else Fr(6000)
    measured = d.get("rho_measured") or {}
    mine = [score(c, sr80, ceiling, measured) for c in d["combinations"]]
    theirs = {r["id"]: r for r in o["combinations"]}
    mism = []
    for r in mine:
        t = theirs[r["id"]]
        for k in ("Q1", "Q2", "Q3", "Q4", "Q5", "Q6", "Q7"):
            if r[k] is not None and Fr(str(t[k])) != r[k]:
                mism.append((r["id"], k, float(r[k]), t[k]))
        if r["C"] is not None and Fr(str(t["C"])) != r["C"]:
            mism.append((r["id"], "C", float(r["C"]), t["C"]))
        if (r["status"] == "excluded") != (t["status"] == "excluded"):
            mism.append((r["id"], "status", r["status"], t["status"]))
    print("combos", len(mine), "; Q/C/status mismatches:", len(mism), mism[:12])
    elig = sorted((r for r in mine if r["status"] == "eligible"),
                  key=lambda r: (-r["C"], -r["Q1"], r["G"], r["name"], r["venue"], r["family"]))
    their_order = [r["id"] for r in sorted((r for r in o["combinations"] if r.get("rank") is not None), key=lambda r: r["rank"])]
    my_order = [r["id"] for r in elig]
    print("eligible", len(my_order), "vs", len(their_order), "; same order:", my_order == their_order)
    if my_order != their_order:
        first = next(i for i, (a, b) in enumerate(zip(my_order, their_order)) if a != b)
        print("  first difference at rank", first + 1, my_order[first:first + 4], their_order[first:first + 4])
    # R4
    picks, seen = [], set()
    for r in elig:
        key = (r["name"], r["family"])
        if key in seen:
            continue
        seen.add(key)
        picks.append(r)
        if len(picks) == 5:
            break
    my_r4 = [(p["id"], p["name"], p["venue"], f"{float(p['C']):.2f}") for p in picks]
    th_r4 = [(p["id"], p["product_or_pool"], p["best_venue"], f"{p['C']:.2f}") for p in o["R4"]["candidates"]]
    print("R4 mine  :", my_r4)
    print("R4 theirs:", th_r4, "equal:", my_r4 == th_r4, "; n_reaching_2 mine",
          sum(1 for p in picks if p["C"] >= 2), "theirs", o["R4"]["n_reaching_2"])
    own = next((r for r in elig if r["kind"] == "own_broker"), None)
    bo = o.get("best_own_broker") or {}
    print("best own-broker mine:", (own["id"], own["name"], f"{float(own['C']):.2f}") if own else None,
          "theirs:", (bo.get("id"), bo.get("name"), bo.get("C")), "rank theirs", bo.get("rank"))
    for cid in ("C138", "C139", "C140", "C141", "C113", "C072", "C021", "C147"):
        r = next((x for x in mine if x["id"] == cid), None)
        if r and r["C"] is not None:
            t = theirs[cid]
            print(f"  {cid} {r['name']} {r['venue']} Q={[int(r[k]) for k in ('Q1','Q2','Q3','Q4','Q5','Q6','Q7')]} "
                  f"C={float(r['C']):.2f} (r3 {t['C']:.2f}, rank {t.get('rank')}) K={float(r['K']):.0f} q={r['q']:.4f} x={float(r['x']):.4f}")


for mode in RUNS:
    run(mode)
