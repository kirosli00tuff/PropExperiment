"""DeltaReviewer: recompute the v2 primary ranking from its inputs' criterion scores with the
frozen formulas (spec lines 53, 97-101, 106, 134, 175), and check RR-01's all-UNKNOWN claim."""
import json
from pathlib import Path

B = Path(__file__).resolve().parents[2]
W1 = dict(C1=.25, C2=.20, C3=.15, C4=.15, C5=.10, C6=.15)
W2 = dict(E=.40, D=.10, R=.10, A=.15, F=.10, P=.05, Rel=.10)


def s(x, c):
    return 4 * max(0.0, 1 - x / c)


for name in ("A3_ranking_table.json", "A3_ranking_table_v1.json"):
    p = json.loads((B / name).read_text())["variants"]["primary"]
    lay, rows = p["layer1"], p["ranked"]
    out, bad, nonnum = [], 0, 0
    for r in rows:
        l1 = lay[r["code"]]
        L1 = sum(w * l1[k] for k, w in W1.items())
        try:
            E = .6 * s(r["mu_star_lim"], 2) + .15 * s(r["mu_star_mkt"], 3) + .25 * s(r["mu10K"], 3)
        except TypeError:  # non-numeric mu (recorded as such): stored E used, counted
            E, nonnum = r["E"], nonnum + 1
        L2 = sum(w * (E if k == "E" else r[k]) for k, w in W2.items())
        S = .5 * L1 + .5 * L2
        gate = L1 >= 2.0 and min(l1[k] for k in W1) > 0
        bad += abs(S - r["S"]) > 1e-6 or abs(L1 - r["L1"]) > 1e-6 or abs(E - r["E"]) > 1e-3
        out.append((S, r["firm"], r["code"], L1, gate))
    gated = sorted([o for o in out if o[4]], key=lambda o: -o[0])
    print(name, "rows", len(rows), "mismatches vs stored S/L1/E:", bad, "non-numeric mu rows:", nonnum,
          "stored order == recomputed:", [(o[1], o[2]) for o in gated] ==
          [(r["firm"], r["code"]) for r in rows if (r["firm"], r["code"]) in
           {(o[1], o[2]) for o in gated}])
    for k, o in enumerate(gated[:10], 1):
        print(f"  {k:2d} {o[1]:9s} {o[2]:4s} S={o[0]:.4f} L1={o[3]:.2f}")
    below = sorted({o[2] for o in out if not o[4]})
    print("  below gate in ranked list:", below)

m = json.loads((B / "A3_masked_contracts.json").read_text())["contracts"]
allunk = []
for c in m:
    ev = c["C1b_evidence"]
    ev = ev if isinstance(ev, list) else []
    vals = [str(e.get("value", e.get("finding", ""))).upper() for e in ev if isinstance(e, dict)]
    if vals and all("UNKNOWN" in v for v in vals):
        allunk.append(c["label"])
print("C1b all-UNKNOWN labels:", allunk, "of", len(m))
print("mask C40 ->", json.loads((B / "A3_mask_key.json").read_text()).get("contracts", {}).get("C40"))
