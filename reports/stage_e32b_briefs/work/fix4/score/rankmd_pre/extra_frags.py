"""Extra fragments for the ranking file (lead follow-up, 05:4x PDT):
sec7u.md  products by underlying, best code first, micros under their leaders (primary ranks);
sec7q.md  QM (and QG, MGC) ranks under declared variant sat1, derived from the primary pair scores.

sat1 changes only the D4 Sat deduction (2 -> 1), so each listed, sigma-known pair's S moves by
0.5 x 0.15 x (new D4 - old D4) and pairs whose new D4 > 0 rank; ordering uses spec 5 (S at 2 dp half-up,
then m*, L1, cost per attempt, code, firm). The derivation is checked against the score run's sat1 output
(n_ranked, top 5, MNQ ranks) and refuses to write if they differ.
"""
import json
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

B = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / "out"
SC = json.loads((B / "score32b_out.json").read_text())
F4 = json.loads((B / "F4_facts_unmasked.json").read_text())
PRI = SC["primary"]
L1 = PRI["layer1"]
FIRM = {"bulenox": "Bulenox", "lucid": "Lucid", "mffu": "MFFU", "topstep": "Topstep", "tradeify": "Tradeify"}


def r2(x: float) -> float:
    return float(Decimal(str(x)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def sat1_ranks() -> list:
    rows = []
    for p in PRI["pairs"]:
        g = p["gate_reasons"]
        if p["status"] == "excluded (V49)" or any("not listed" in x or "sigma_60 unknown" in x for x in g):
            continue
        r = L1[p["code"]]
        dp = r["D4_parts"]
        d4n = max(0, 4 - dp["L"] - dp["J"] - dp["Sat"])
        if d4n == 0:
            continue
        dS = 0.5 * 0.15 * (d4n - r["D4"])
        S = p["S"] + dS
        m = p["m_star"] if isinstance(p["m_star"], float) else float("inf")
        rows.append((-r2(S), m, -(p["L1"] + 0.15 * (d4n - r["D4"])), p["cost_per_attempt"], p["code"], p["firm"], S))
    rows.sort()
    return rows


def main() -> None:
    rows = sat1_ranks()
    v = SC["variants"]["sat1"]
    top = [(x[5], x[4]) for x in rows[:5]]
    mnq = {x[5]: i + 1 for i, x in enumerate(rows) if x[4] == "MNQ"}
    if len(rows) != v["n_ranked"] or top != [(t["firm"], t["code"]) for t in v["top5"]] or mnq != v["MNQ_ranks"]:
        raise SystemExit("sat1 derivation does not match the score run")
    lines = ["| code | sat1 ranks (firm rank S) |", "|---|---|"]
    for c in ("QM", "QG", "MGC"):
        cells = [f"{FIRM[x[5]]} {i + 1} ({x[6]:.3f})" for i, x in enumerate(rows) if x[4] == c]
        lines.append(f"| {c} | {'; '.join(cells) or 'not ranked'} |")
    (OUT / "sec7q.md").write_text("\n".join(lines) + "\n")

    ranked = [p for p in PRI["pairs"] if p["status"] == "ranked"]
    best = {}
    for p in ranked:
        if p["code"] not in best or p["rank"] < best[p["code"]][0]:
            best[p["code"]] = (p["rank"], p["firm"])
    und = {}
    for c, (rk, fm) in best.items():
        und.setdefault(F4["codes"][c]["underlying"], []).append((rk, c, fm))
    order = sorted(und.items(), key=lambda kv: min(kv[1])[0])
    lines = ["| order | underlying | codes by best rank (code: best rank, firm) |", "|---|---|---|"]
    for i, (u, cs) in enumerate(order, 1):
        cs.sort()
        lines.append(f"| {i} | {u} | " + "; ".join(f"{c}: {rk} ({FIRM[fm]})" for rk, c, fm in cs) + " |")
    (OUT / "sec7u.md").write_text("\n".join(lines) + "\n")
    print("ok", len(rows), [u for u, _ in order])


if __name__ == "__main__":
    main()
