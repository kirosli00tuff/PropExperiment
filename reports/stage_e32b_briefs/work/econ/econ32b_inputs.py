"""E.32b economics: job lists from (a) F3_vol.json + F4_facts_unmasked.json (wave C) and (b) E.28's A3_inputs.json
(the regression). A job is one pair on one curve (per-trade law) with the market costs evaluated on it.

Field names follow the shared data contract in reports/stage_e32b_briefs/brief_wave_b.md (and ScoreCoder's
work/score/SCHEMA.md where it adds detail):
  F3 roots[CODE]: status, tick_size, L_main, h["1"|"30"|"60"|"120"|"240"].sigma (ticks of the code's own tick)
  F4 codes[CODE]: excluded, tick_size, tick_value_usd, spread_S {value, sourced, item}
  F4 pairs["firm|CODE"]: listed_50k, fee_rt_usd, fee_kind
  F4 firms[firm]: dll_50k, mll_50k (checked against E.28's firm models; the model itself is E.28's)
Spec section 4: c_mkt = F_rt / v + S_rt, S_rt = the sourced S (1 tick where none is sourced); primary T = 20,
sigma_T = sigma_1; spread1 S = 1 for every code; E_dir60 T = min(20, floor(L_main / 60)), sigma_T = sigma_60;
E_dir at h = 30, 120, 240 (given pairs only) T = min(20, floor(L_main / h)), sigma_T = sigma_h. Grid cap
max(4, ceil(0.30 sigma_60)) ticks for every curve of the pair. NQ is excluded (V49).
"""

from __future__ import annotations

import math
from typing import Any

from econ32b_core import grid_cap_k, trades_per_day

EXCLUDED_CODES = {"NQ": "excluded (V49)"}
EDIR_H = (30, 120, 240)
DIR60 = 60
S_DEFAULT = 1.0
REGRESS_K_MAX = 500  # regression grid cap 5.00 ticks: every E.28 limit-case mu10K <= 4 maps to a market one <= 5
TICK_REL_TOL = 1e-9


def _num(x: Any) -> float | None:
    """A finite number, or None. A {"value": x, ...} record is read through its value."""
    if isinstance(x, dict):
        x = x.get("value")
    if isinstance(x, bool) or x is None:
        return None
    if isinstance(x, (int, float)) and math.isfinite(x):
        return float(x)
    return None


def _sigma(root: dict[str, Any], h: int) -> float | None:
    rec = (root.get("h") or {}).get(str(h)) or {}
    s = _num(rec.get("sigma"))
    return s if s is not None and s > 0 else None


def spread_rt(code_rec: dict[str, Any]) -> tuple[float, str]:
    """S_rt in ticks: the sourced S, else 1 tick (status "u")."""
    sp = code_rec.get("spread_S") or {}
    val = _num(sp.get("value"))
    if sp.get("sourced") is True and val is not None and val > 0:
        return val, "sourced"
    return S_DEFAULT, "u"


def _case(name: str, fee: float, v: float, s: float) -> dict[str, Any]:
    return {"name": name, "f_rt_usd": fee, "v_usd": v, "s_rt_ticks": s}


def _job(key: str, curve: str, h: int, t_rt: int, sigma_t: float, sigma60: float | None, k_max: int,
         cases: list[dict[str, Any]], firm: str | None = None) -> dict[str, Any]:
    """`key` is the pair key as F4 writes it (kept in the output); `firm` the E.28 model's firm name."""
    firm_raw, code = key.split("|")
    firm = firm or firm_raw
    return {"pair": key, "firm": firm, "code": code, "curve": curve, "h": h, "T": t_rt, "sigma_T": sigma_t,
            "v_usd": cases[0]["v_usd"], "sigma60": sigma60, "k_max": k_max, "cases": cases}


def norm_firm(name: str, model_firms: set[str]) -> str:
    """The E.28 model's firm name for an F4 firm name (case and surrounding spaces ignored)."""
    f = name.strip().lower()
    if f not in model_firms:
        raise ValueError(f"firm {name!r} has no E.28 firm model (models: {sorted(model_firms)})")
    return f


def _check_tick(code: str, root: dict[str, Any], crec: dict[str, Any]) -> None:
    a, b = _num(root.get("tick_size")), _num(crec.get("tick_size"))
    if a is not None and b is not None and abs(a - b) > TICK_REL_TOL * max(abs(a), abs(b)):
        raise ValueError(f"{code}: F3 tick_size {a} != F4 tick_size {b}; F3 statistics are in F3's ticks")


def _pair_inputs(key: str, pr: dict[str, Any], f3: dict[str, Any], f4: dict[str, Any]
                 ) -> tuple[dict[str, Any] | None, str | None]:
    """The pair's inputs, or (None, reason not computed)."""
    code = key.split("|")[1]
    if code in EXCLUDED_CODES:
        return None, EXCLUDED_CODES[code]
    if pr.get("listed_50k") is not True:
        return None, "not listed for the 50K plan"
    crec = (f4.get("codes") or {}).get(code)
    if crec is None:
        return None, "code missing from F4 codes"
    if crec.get("excluded"):
        return None, "code excluded in F4"
    root = (f3.get("roots") or {}).get(code)
    if root is None or root.get("status") == "unknown":
        return None, "sigma unknown (Layer 1 gate)"
    _check_tick(code, root, crec)
    sig = {h: _sigma(root, h) for h in (1, DIR60, *EDIR_H)}
    if sig[1] is None or sig[DIR60] is None:
        return None, "sigma_1 or sigma_60 unknown (Layer 1 gate)"
    fee, v = _num(pr.get("fee_rt_usd")), _num(crec.get("tick_value_usd"))
    if fee is None:
        return None, "fee unknown"
    if v is None or v <= 0:
        return None, "tick value unknown"
    s, s_status = spread_rt(crec)
    return {"code": code, "fee": fee, "v": v, "S": s, "S_status": s_status, "sig": sig,
            "L_main": _num(root.get("L_main")), "status": root.get("status"),
            "fee_kind": pr.get("fee_kind"), "spread_item": (crec.get("spread_S") or {}).get("item")}, None


def _dir_job(key: str, p: dict[str, Any], h: int, k_max: int, name: str) -> tuple[dict[str, Any] | None, str]:
    if p["L_main"] is None:
        return None, f"{name}: L_main unknown"
    if p["sig"][h] is None:
        return None, f"{name}: sigma_{h} unknown"
    t_rt = trades_per_day(p["L_main"], h)
    if t_rt < 1:
        return None, f"{name}: T = 0 (L_main {p['L_main']} < h {h})"
    return _job(key, f"dir{h}", h, t_rt, p["sig"][h], p["sig"][DIR60], k_max,
                [_case(name, p["fee"], p["v"], p["S"])], firm=p.get("firm")), ""


def jobs_from_facts(f3: dict[str, Any], f4: dict[str, Any], model_firms: set[str],
                    edir_pairs: list[str] | None = None, only: list[str] | None = None
                    ) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]], dict[str, str]]:
    """(jobs, per-pair input records, not computed {pair: reason}) from F3 and F4."""
    jobs: list[dict[str, Any]] = []
    meta: dict[str, dict[str, Any]] = {}
    skipped: dict[str, str] = {}
    def norm_key(k: str) -> str:
        f, c = k.split("|")
        return f"{f.strip().lower()}|{c}"

    edir = {norm_key(k) for k in (edir_pairs or [])}
    only_n = None if only is None else {norm_key(k) for k in only}
    for key, pr in sorted((f4.get("pairs") or {}).items()):  # F4's key is kept in the output
        firm = norm_firm(key.split("|")[0], model_firms)
        if only_n is not None and norm_key(key) not in only_n:
            continue
        p, why = _pair_inputs(key, pr, f3, f4)
        if p is None:
            skipped[key] = why or "not computed"
            continue
        p = {**p, "firm": firm}
        k_max = grid_cap_k(p["sig"][DIR60])
        meta[key] = {"S_rt_ticks": p["S"], "S_rt_status": p["S_status"], "spread_item": p["spread_item"],
                     "F_rt_usd": p["fee"], "fee_kind": p["fee_kind"], "v_usd": p["v"], "L_main": p["L_main"],
                     "f3_status": p["status"], "sigma_1": p["sig"][1], "sigma60": p["sig"][DIR60],
                     "grid_cap": k_max / 100, "notes": []}
        prim = [_case("primary", p["fee"], p["v"], p["S"]), _case("spread1", p["fee"], p["v"], S_DEFAULT)]
        jobs.append(_job(key, "primary", 1, 20, p["sig"][1], p["sig"][DIR60], k_max, prim, firm=firm))
        want_edir = norm_key(key) in edir
        variants = [(DIR60, "E_dir60")] + ([(h, f"E_dir{h}") for h in EDIR_H] if want_edir else [])
        for h, name in variants:
            j, note = _dir_job(key, p, h, k_max, name)
            if j is None:
                meta[key]["notes"].append(f"not computed: {note}")
            else:
                jobs.append(j)
    computed = {norm_key(k) for k in meta}
    for k in sorted(edir - computed):
        skipped.setdefault(k, "E_dir requested for a pair that is not computed")
    return jobs, meta, skipped


def firm_check(f4: dict[str, Any], limits: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """F4 dll_50k / mll_50k against E.28's firm models. A difference is a lead decision (update the model or
    accept it); an unknown F4 value is reported as unverifiable."""
    rows, mismatches = {}, []
    for raw, rec in sorted((f4.get("firms") or {}).items()):
        f = raw.strip().lower()
        if f not in limits:
            rows[f] = {"status": "no E.28 model"}
            continue
        row = {"plan": limits[f]["plan"]}
        for fk, mk in (("mll_50k", "mll_usd"), ("dll_50k", "dll_usd")):
            raw_v = rec.get(fk)
            fv, mv = _num(raw_v), limits[f][mk]
            if (raw_v is None or (isinstance(raw_v, dict) and raw_v.get("value") is None)) and mv is None:
                st = "match (none)"
            elif fv is None:
                st = "unverifiable (F4 value not a number)"
            elif mv is None or abs(fv - mv) > 0.005:
                st = "MISMATCH"
                mismatches.append(f"{f} {fk}: F4 {rec.get(fk)!r} vs model {mv!r}")
            else:
                st = "match"
            row[fk] = {"f4": rec.get(fk), "model": mv, "status": st}
        rows[f] = row
    return {"rows": rows, "mismatches": mismatches}


def jobs_from_e28(inputs: dict[str, Any], k_max: int = REGRESS_K_MAX
                  ) -> tuple[list[dict[str, Any]], dict[str, str]]:
    """Regression jobs: E.28's own inputs, S = 1 (E.28's S_rt for every candidate), T = 20, sigma_1m."""
    jobs, skipped = [], {}
    for p in inputs["pairs"]:
        key = f"{p['firm']}|{p['code']}"
        cand = inputs["candidates"][p["code"]]
        sig, fee, v = cand["sigma_1m_ticks"], p["F_rt_usd"], cand["v_usd"]
        if sig is None or fee is None:
            skipped[key] = "not computed in E.28 (sigma_1m unknown)" if sig is None else "fee unknown"
            continue
        if cand["S_rt_ticks"] != S_DEFAULT:
            raise ValueError(f"{key}: E.28 S_rt {cand['S_rt_ticks']} != 1")
        jobs.append(_job(key, "regress", 1, 20, sig, None, k_max, [_case("regress", fee, v, S_DEFAULT)]))
    return jobs, skipped
