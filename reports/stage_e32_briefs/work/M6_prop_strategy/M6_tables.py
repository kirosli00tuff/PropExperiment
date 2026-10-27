"""M6 (E.32): cost-per-round-trip and probability-threshold tables (arithmetic only, no data)."""
import json, math
from statistics import NormalDist
N = NormalDist()
FEE = {"topstep": 0.528, "lucid": 0.560, "lucid_u": 0.920, "tradeify": 0.920, "mffu": 0.612, "bulenox": 0.572}
ENTRY = {"M": 0.5, "TT": 0.970, "QK": 0.287, "QF": 0.252}   # per-fill cost vs mid 10 s later (E.31 / half spread)
out = {}
for f, fee in FEE.items():
    out[f] = {k: round(ENTRY[k] + 0.5 + fee, 3) for k in ENTRY}            # limit or market entry, market exit
    out[f].update({k + "_both": round(2 * ENTRY[k] + fee, 3) for k in ("TT", "QK", "QF")})
sig1 = 3.15
thr = {}
for f in ("topstep", "lucid", "tradeify", "mffu", "bulenox"):
    c = out[f]["M"]
    thr[f] = {h: round(N.cdf(c / (sig1 * math.sqrt(h))), 4) for h in (5, 15, 60)}
    thr[f]["sig"] = {h: round(sig1 * math.sqrt(h), 3) for h in (5, 15, 60)}
    thr[f]["barrier_b10_pstar"] = round(0.5 + c / 20, 4)
json.dump({"cost": out, "pstar_normal_MM": thr}, open("M6_tables_out.json", "w"), indent=1)
for f in out: print(f, out[f])
for f in thr: print(f, thr[f])
