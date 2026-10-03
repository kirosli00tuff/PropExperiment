"""Stage E.12 Task 5: the phase-1 subset by V2.1's rule as applied by lead rule P-4 (frozen in the
design before the quote). Lead-run, read-only except its output.

    python reports/stage_e12_briefs/rank_phase1.py --quotes <root=usd JSON> --out reports/stage_e12_ranking.json

Inputs (frozen files): reports/stage_e0_liquidity.json (the vehicle's YTD 2026 Jan-Aug ADV, the
adv_alternates entry with that period), reports/stage_e10_research/cost_wall.json (c = rt_wall_ticks
x tick_value_usd), reports/stage_e12_cme_margins.json (maintenance_usd, role "vehicle") or, when the
lead switches the whole ranking, reports/stage_e2a_epsilon.json's E|m_1| (--proxy em1, never mixed).
Headroom per account is read from the spend gates at run time (acct-2 at the v8 cap).
"""
from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
UNIVERSE = {  # vehicle -> (cluster, price path): ml_route_v2.constants.UNIVERSE (V2.1)
    "MNQ": ("K1", "NQ"), "M2K": ("K1", "RTY"), "MYM": ("K1", "YM"),
    "ZT": ("K2", "ZT"), "ZF": ("K2", "ZF"), "ZN": ("K2", "ZN"), "TN": ("K2", "TN"),
    "ZB": ("K2", "ZB"), "UB": ("K2", "UB"),
    "6E": ("K3", "6E"), "6A": ("K3", "6A"), "6B": ("K3", "6B"), "6C": ("K3", "6C"),
    "6J": ("K3", "6J"), "6S": ("K3", "6S"), "6N": ("K3", "6N"),
    "MCL": ("K4", "CL"), "NG": ("K4", "NG"), "MGC": ("K5", "GC"), "MHG": ("K5", "HG"),
    "ZC": ("K6", "ZC"), "ZW": ("K6", "ZW"), "ZS": ("K6", "ZS"), "ZM": ("K6", "ZM"),
    "ZL": ("K6", "ZL"), "HE": ("K6", "HE"), "LE": ("K6", "LE"), "MBT": ("K7", "MBT"),
}
OWNED_PATHS = {"NG": "the owned E.5 step 2 store is NG's price path (design V2.1)"}
MARGIN = 0.03  # each pick's quote must fit its account's remaining headroom with a 3% margin


def adv_ytd_2026(liq: dict) -> dict[str, float]:
    out = {}
    for p in liq["products"]:
        alts = [a for a in p.get("adv_alternates", []) if str(a.get("period", "")).startswith("YTD 2026")]
        if alts:
            out[p["symbol"]] = float(alts[0]["value"])
    return out


def proxies(kind: str) -> dict[str, float]:
    if kind == "margin":
        rows = json.loads((ROOT / "reports/stage_e12_cme_margins.json").read_text())["rows"]
        return {r["symbol"]: float(r["maintenance_usd"]) for r in rows
                if r.get("role") == "vehicle" and r.get("maintenance_usd") is not None}
    if kind == "em1":  # the frozen E|m_1| (E.2a), in dollars per contract of the vehicle
        eps = json.loads((ROOT / "reports/stage_e2a_epsilon.json").read_text())["exposures"]
        wall = {r["vehicle"]: r for r in json.loads(
            (ROOT / "reports/stage_e10_research/cost_wall.json").read_text())["rows"]}
        out = {}
        for e in eps:
            ticks = float(e["e_abs_move_ticks"]["1"])
            ctx = wall[e["vehicle"]]["E_abs_m1_ticks_context"]
            if abs(round(ticks, 2) - ctx) > 0.011:  # cost wall carries it rounded to 0.01
                raise SystemExit(f"{e['vehicle']}: E|m_1| {ticks} != cost wall context {ctx}")
            out[e["vehicle"]] = ticks * float(e["tick_value_usd"])
        return out
    raise SystemExit(f"unknown proxy {kind!r}")


def headroom() -> dict[str, float]:
    import sys
    sys.path.insert(0, str(ROOT))
    from data.spend_gate import SpendGate
    out = {}
    for a in ("acct-1", "acct-2"):
        g = SpendGate("e12-rank-readonly", account=a)
        out[a] = g.account_cap_usd - g.account_spent_usd()
    return out


def rank(quotes: dict[str, float | None], proxy_kind: str, room: dict[str, float]) -> dict:
    liq = json.loads((ROOT / "reports/stage_e0_liquidity.json").read_text())
    wall = {r["vehicle"]: r for r in json.loads(
        (ROOT / "reports/stage_e10_research/cost_wall.json").read_text())["rows"]}
    adv, prox = adv_ytd_2026(liq), proxies(proxy_kind)
    missing = [v for v in UNIVERSE if v not in adv or v not in wall or v not in prox]
    if missing:
        raise SystemExit(f"inputs missing for {missing}: the lead decides before ranking")
    med = statistics.median(adv[v] for v in UNIVERSE)
    rows = []
    for v, (cl, path) in UNIVERSE.items():
        c = wall[v]["rt_wall_ticks"] * wall[v]["tick_value_usd"]
        rows.append({"vehicle": v, "cluster": cl, "path": path, "adv_ytd2026": adv[v],
                     "tier": 1 if adv[v] >= med else 2, "c_usd": round(c, 4),
                     "sigma_proxy_usd": prox[v], "c_over_sigma": c / prox[v],
                     "quote_usd": 0.0 if path in OWNED_PATHS else quotes.get(path)})
    rows.sort(key=lambda r: (r["tier"], r["c_over_sigma"], r["vehicle"]))
    for i, r in enumerate(rows, 1):
        r["rank"] = i
    rem, steps, taken = dict(room), [], set()

    def consider(r: dict, pass_no: int) -> None:
        q = r["quote_usd"]
        if q is None:
            steps.append({**_step(r, pass_no, rem), "action": "skip", "reason": "no complete fresh quote"})
            return
        for acct in ("acct-1", "acct-2"):
            if q * (1 + MARGIN) <= rem[acct] + 1e-9:
                rem[acct] -= q * (1 + MARGIN)  # reserve the 3% margin too (freeze review F-1)
                taken.add(r["vehicle"])
                steps.append({**_step(r, pass_no, rem), "action": "take", "account": acct})
                return
        steps.append({**_step(r, pass_no, rem), "action": "skip",
                      "reason": f"quote x 1.03 = {q * (1 + MARGIN):.4f} fits neither account"})

    best = {}
    for r in rows:
        best.setdefault(r["cluster"], r)
    for r in rows:  # pass 1: the seven cluster-best exposures, in rank order
        if best[r["cluster"]] is r:
            consider(r, 1)
    for r in rows:  # pass 2: every remaining exposure, in rank order
        if r["vehicle"] not in taken and best[r["cluster"]] is not r:
            consider(r, 2)
    subset = [s for s in steps if s["action"] == "take"]
    total = sum(s["quote_usd"] for s in subset)
    return {"rule": "design V2.1 steps 1-5 (lead rule P-4)", "proxy": proxy_kind,
            "adv_median_ytd2026": med, "headroom_start": room, "ranking": rows, "steps": steps,
            "subset": [{"vehicle": s["vehicle"], "path": s["path"], "account": s["account"],
                        "quote_usd": s["quote_usd"]} for s in subset],
            "subset_total_usd": total,
            "per_account_usd": {a: sum(s["quote_usd"] for s in subset if s["account"] == a)
                                for a in ("acct-1", "acct-2")},
            "headroom_end": rem}


def _step(r: dict, pass_no: int, rem: dict) -> dict:
    return {"pass": pass_no, "rank": r["rank"], "vehicle": r["vehicle"], "path": r["path"],
            "cluster": r["cluster"], "quote_usd": r["quote_usd"],
            "headroom_after": {k: round(v, 6) for k, v in rem.items()}}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--quotes", required=True, help="JSON {price path root: training-window quote usd}")
    ap.add_argument("--proxy", default="em1", choices=("margin", "em1"))
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    quotes = {k: (None if v is None else float(v)) for k, v in json.loads(Path(a.quotes).read_text()).items()}
    res = rank(quotes, a.proxy, headroom())
    Path(a.out).write_text(json.dumps(res, indent=1) + "\n")
    print(f"subset {len(res['subset'])}: {[s['vehicle'] for s in res['subset']]} total "
          f"{res['subset_total_usd']:.6f} per account {res['per_account_usd']}")


if __name__ == "__main__":
    main()
