"""A3 input table: per-candidate magnitudes and per-(firm, candidate) fees, limits and plan facts.

Pure extraction from the stage's fact files, with the lead's open choices applied exactly:
- OC-1: sigma_1m and R_d in ticks for a candidate without owned window data come from an owned sibling on the
  SAME underlying price: x_ticks(cand) = x_ticks(sibling) * tick(sibling) / tick(cand), only where the price
  units match; volume statistics never transfer. SIL, SI, MET, ETH and the micro yields stay unknown (no A1 reader
  sourced a value).
- OC-2: ADV for owned roots is A0's v_0 median daily volume (front contract); otherwise A1's published figures
  (all fields kept, with windows and sources); both are reported where both exist. ADV is not used by the economic
  model; it is passed through for the fact table.
- S_rt (spec section 3): the sourced median main-session spread in ticks, 1 if unknown. A sourced mean is not a
  median; it is kept as S_rt_mean_sourced for a sensitivity only.
No market data is read: A0 is the stage's own statistics file.
Usage: uv run python reports/stage_e28_briefs/work/A3_econ/A3_inputs.py  (writes A3_inputs.json beside it)
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[4]
BRIEFS = REPO / "reports" / "stage_e28_briefs"
OUT = Path(__file__).resolve().parent / "A3_inputs.json"
FAMILIES = ("crude", "natgas", "metals", "fx", "crypto", "equity", "rates", "grains")
FIRMS = ("topstep", "lucid", "tradeify", "mffu", "bulenox")
FEE_KEY = {"topstep": "fee_rt", "lucid": "commission_round_trip", "tradeify": "fee_rt", "mffu": "rt",
           "bulenox": "commission_round_trip"}
# OC-1 siblings (lead decision): candidate -> owned sibling on the same underlying price
SIBLING = {"MNQ": "NQ", "M2K": "RTY", "MYM": "YM", "MNG": "NG", "QG": "NG", "QM": "CL", "M6E": "6E",
           "M6A": "6A", "BTC": "MBT", "XC": "ZC", "XK": "ZS", "XW": "ZW", "MZC": "ZC", "MZS": "ZS",
           "MZW": "ZW", "MZL": "ZL", "MZM": "ZM"}
# price-unit strings judged equal by hand (A1 wording differs, same quoted price)
UNIT_SAME = {("USD per bitcoin", "USD per bitcoin (index points)")}
MICROS = {"MCL", "MNG", "MGC", "SIL", "MHG", "M6E", "M6A", "MET", "MBT", "M2K", "MYM", "MNQ", "MZC",
          "MZS", "MZW", "MZL", "MZM", "2YY", "5YY", "10Y", "30Y"}
# S_rt classification of the A1 spread entries (main session); every sourced number is 1 tick or a mean
SPREAD_MEDIAN_ONE = {  # a statement that the touch spread is one tick most of the time / most volume
    "CL": "volume-weighted statement: majority of volume at the minimum tick (2012-13)",
    "GC": "one tick during almost all trading hours (2017-Q1 2018, all hours)",
    "SI": "one tick most of the hours (2017-Q1 2018)",
    "ZT": "minimum increment > 99% of each trading day (2018 RTH)",
    "ZF": "minimum increment > 99% of each trading day (2018 RTH)",
    "ZN": "minimum increment > 99% of each trading day (2018 RTH)",
    "ZB": "minimum increment > 99% of each trading day (2018 RTH)",
}


def _val(x: Any) -> Any:
    return x.get("value") if isinstance(x, dict) else x


def _src(x: Any) -> dict[str, Any] | None:
    if not isinstance(x, dict):
        return None
    return {k: x.get(k) for k in ("value", "unit", "window", "source_file", "quote", "note") if k in x}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_a0() -> dict[str, dict[str, Any]]:
    doc = json.loads((BRIEFS / "A0_contract_stats.json").read_text())
    return {r["root"]: r for r in doc["roots"]}


def load_a1() -> dict[str, dict[str, Any]]:
    out = {}
    for fam in FAMILIES:
        for rec in json.loads((BRIEFS / f"A1_{fam}.json").read_text()):
            code = _val(rec.get("candidate")) or _val(rec.get("code"))
            out[str(code)] = {"family": fam, **rec}
    return out


def _unit(rec: dict[str, Any]) -> str:
    return str((rec.get("tick_size") or {}).get("unit") or "").strip()


def units_match(a: str, b: str) -> bool:
    return a == b or (a, b) in UNIT_SAME or (b, a) in UNIT_SAME


def magnitudes(code: str, a0: dict, a1: dict) -> dict[str, Any]:
    """sigma_1m and R_d in ticks with their provenance (owned, OC-1 sibling, or unknown)."""
    own = a0.get(code)
    if own is not None and own.get("sigma_1m_ticks") is not None:
        return {"sigma_1m_ticks": own["sigma_1m_ticks"], "R_d_ticks": own["R_d_median_ticks"],
                "magnitude_source": f"owned A0 window {own['window_first_trade_date']}.."
                f"{own['window_last_trade_date']} ({own['n_trade_dates']} trade dates)"}
    sib = SIBLING.get(code)
    if sib is None:
        return {"sigma_1m_ticks": None, "R_d_ticks": None,
                "magnitude_source": "unknown: no owned window data and no OC-1 sibling"}
    s0, sa, ca = a0.get(sib), a1.get(sib), a1.get(code)
    if s0 is None or s0.get("sigma_1m_ticks") is None or sa is None or ca is None:
        return {"sigma_1m_ticks": None, "R_d_ticks": None,
                "magnitude_source": f"unknown: sibling {sib} has no owned window data"}
    if not units_match(_unit(sa), _unit(ca)):
        return {"sigma_1m_ticks": None, "R_d_ticks": None,
                "magnitude_source": f"unknown: price units differ ({_unit(sa)!r} vs {_unit(ca)!r})"}
    ratio = float(_val(sa["tick_size"])) / float(_val(ca["tick_size"]))
    return {"sigma_1m_ticks": s0["sigma_1m_ticks"] * ratio, "R_d_ticks": s0["R_d_median_ticks"] * ratio,
            "magnitude_source": f"OC-1 sibling {sib}: x_ticks({sib}) x tick({sib}) / tick({code}) = "
            f"x {ratio:g} (A1 ticks {_val(sa['tick_size'])} / {_val(ca['tick_size'])} {_unit(ca)})",
            "sibling": sib, "tick_ratio": ratio}


def spread(code: str, rec: dict[str, Any]) -> dict[str, Any]:
    entries = {k: _src(rec[k]) for k in ("median_spread_ticks_main", "median_spread_ticks",
                                          "spread_median_ticks_by_session") if rec.get(k)}
    sourced = [e for e in entries.values() if e and e.get("value") is not None]
    if code in SPREAD_MEDIAN_ONE:
        return {"S_rt_ticks": 1.0, "S_rt_status": "sourced", "S_rt_note": SPREAD_MEDIAN_ONE[code],
                "S_rt_mean_sourced": None, "S_rt_entries": entries}
    mean = None
    for e in sourced:
        try:
            mean = float(e["value"])
        except (TypeError, ValueError):
            continue
    note = ("default 1 (u): no sourced median" if mean is None else
            f"default 1 (u): the sourced figure {mean:g} is a mean/average, not a median")
    return {"S_rt_ticks": 1.0, "S_rt_status": "u", "S_rt_note": note, "S_rt_mean_sourced": mean,
            "S_rt_entries": entries}


def adv(code: str, a0: dict, rec: dict[str, Any]) -> dict[str, Any]:
    own = a0.get(code)
    owned = None
    if own is not None and own.get("ADV_median_contracts_v0_front") is not None:
        owned = {"value": own["ADV_median_contracts_v0_front"], "source": "A0 v_0 front median, window"}
    pub = {k: _src(v) for k, v in rec.items() if k.startswith("adv") and isinstance(v, dict)
           and v.get("value") is not None}
    return {"ADV_owned_v0": owned, "ADV_published_A1": pub}


def candidate_table(a0: dict, a1: dict) -> dict[str, dict[str, Any]]:
    out = {}
    for code, rec in a1.items():
        v = float(_val(rec["tick_value"]))
        a0v = a0.get(code, {}).get("tick_value_usd")
        row = {"code": code, "family": rec["family"], "tick_size": _val(rec["tick_size"]),
               "tick_unit": _unit(rec), "v_usd": v, "v_source": _src(rec["tick_value"]),
               "v_matches_A0": None if a0v is None else abs(float(a0v) - v) < 1e-9,
               "micro": code in MICROS}
        row.update(magnitudes(code, a0, a1))
        row.update(spread(code, rec))
        row.update(adv(code, a0, rec))
        g60 = next((rec[k] for k in rec if k.startswith(("globex_60", "pilot_window_globex",
                                                         "traded_60"))), None)
        row["globex_60_dates_pilot"] = _src(g60)
        out[code] = row
    return out


def firm_products(firm: str) -> dict[str, dict[str, Any]]:
    doc = json.loads((BRIEFS / f"A2_firm_{firm}.json").read_text())
    out = {}
    for code, p in doc["products"].items():
        allowed = _src(p.get("allowed")) or {}
        fee = _src(p.get(FEE_KEY[firm])) or {}
        note = str(allowed.get("note") or "")
        restricted = (allowed.get("value") is False and fee.get("value") is not None
                      and "restricted" in note)
        out[code] = {"allowed": allowed.get("value") is True, "restricted_now": restricted,
                     "allowed_src": allowed, "F_rt_usd": fee.get("value"), "fee_src": fee}
    return out


def position_limit(firm: str, code: str) -> tuple[int | None, str]:
    """Contracts of this product allowed at the 50K plan (evaluation stage) and the rule text."""
    micro = code in MICROS
    if firm == "topstep":
        vol = {"CL": 3, "QM": 3, "MCL": 30, "GC": 3, "MGC": 30, "SI": 0, "SIL": 2, "HG": 0, "MHG": 2}
        base = 50 if micro else 5
        if code in ("MBT", "MET"):
            base = 5
        if code == "SIL":
            base = 25
        n = min(base, vol.get(code, base))
        txt = ("Combine 5 minis / 50 micros (10:1); XFA 2/3/5 lots by balance (<1,500 / 1,500-2,000 / >2,000)"
               + (f"; volatility cap {vol[code]}" if code in vol else "")
               + ("; MBT/MET capped at mini-equivalent lots" if code in ("MBT", "MET") else "")
               + ("; SIL counts as 2 micros" if code == "SIL" else ""))
        return n, txt
    if firm in ("lucid", "tradeify"):
        return (40 if micro else 4), "4 minis or 40 micros (10:1)"
    if firm == "mffu":
        if code == "MBT":
            return 4, "4 minis / 40 micros; MBT treated as a mini"
        if code in ("MGC", "SIL", "MHG"):
            return 5, "4 minis / 40 micros; micro metals capped at 5 at 50K (since 2026-04-17)"
        return (40 if micro else 4), "4 minis / 40 micros (10:1)"
    if firm == "bulenox":
        return (70 if micro else 7), "Option 1: 7 minis or 70 micros (1:10), no scaling"
    raise ValueError(firm)


def pair_table(cands: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    prods = {f: firm_products(f) for f in FIRMS}
    pairs = []
    for firm in FIRMS:
        for code, p in sorted(prods[firm].items()):
            if not (p["allowed"] or p["restricted_now"]):
                continue
            flags = []
            fee, fee_status = p["F_rt_usd"], "sourced"
            others = [prods[f][code]["F_rt_usd"] for f in FIRMS if f != firm
                      and prods[f].get(code, {}).get("F_rt_usd") is not None]
            if fee is None:
                fee, fee_status = (max(others) if others else None), "u"
                flags.append("fee_unknown_highest_other_firm_used")
            if p["restricted_now"]:
                flags.append("restricted_now: listed with a fee but 'currently restricted'")
            if firm == "lucid":
                flags.append("fee: commission per side x 2; exchange/NFA inclusion not stated")
            if firm == "topstep":
                flags.append("fee conflict: LFA-costs page says $3.70/lot simulated fee in the Combine")
            npos, ptxt = position_limit(firm, code)
            if npos == 0:
                flags.append("position_limit_0: product listed but 0 contracts at 50K now")
            c = cands.get(code)
            pairs.append({"firm": firm, "code": code, "F_rt_usd": fee, "F_rt_status": fee_status,
                          "fee_src": p["fee_src"], "F_rt_alt_usd": max(others) if others else None,
                          "position_limit": npos, "position_limit_text": ptxt,
                          "v_usd": None if c is None else c["v_usd"], "flags": flags})
    return pairs


def main() -> int:
    a0, a1 = load_a0(), load_a1()
    cands = candidate_table(a0, a1)
    pairs = pair_table(cands)
    inputs = {f"A2_firm_{f}.json": sha256(BRIEFS / f"A2_firm_{f}.json") for f in FIRMS}
    inputs.update({f"A1_{f}.json": sha256(BRIEFS / f"A1_{f}.json") for f in FAMILIES})
    inputs["A0_contract_stats.json"] = sha256(BRIEFS / "A0_contract_stats.json")
    doc = {"generated_by": str(Path(__file__).relative_to(REPO)), "inputs_sha256": inputs,
           "candidates": cands, "pairs": pairs}
    OUT.write_text(json.dumps(doc, indent=1))
    known = sum(1 for c in cands.values() if c["sigma_1m_ticks"] is not None)
    print(f"candidates {len(cands)} (sigma known {known}); pairs {len(pairs)}")
    for firm in FIRMS:
        fp = [p for p in pairs if p["firm"] == firm]
        print(firm, len(fp), " ".join(p["code"] for p in fp))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
