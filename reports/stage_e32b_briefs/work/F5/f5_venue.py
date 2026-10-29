"""E.32b F5: the own-broker venue (IBKR, spec 8.2-8.3) rows, pure functions on plain inputs (no file access).

Added by F5Runner (Opus 5.5, xhigh), 2026-10-29, under the lead's rulings in briefs/brief_wave_c.md section C5a:
- LR-F5-IBKR: c_f = c_RT + F_rt / v with F_rt = 2 x the all-in fee per side; an own account has no DLL, MLL or
  flat-by-close, so B = {h in {5, 15, 30, 60, 120, 240, OC} : G(h) <= 1.10 min G} (no DLL or flat-by-close
  condition; intraday holds end by the main session's end); overnight rows report the overnight margin.
- LR-Q6d: spec 8.3's own-broker Q6 inputs per code: one contract's initial margin (intraday and overnight) against
  the capital ceiling (USD 6,000 (u) when docs/DECISIONS.md records none), and sigma_day = sigma_cc (F3 overnight
  close-to-close) x tick value against 2% of that ceiling, with sigma_OC x tick value beside. Inputs only: Q6 itself
  is scored by r3_score.py.
The formulas per horizon are f5_core's (horizon_rows, g_minimum, band_context, verdict); min G is the same single
minimum over 1..240, OC, cc and on as for the firm pairs (README interpretation 4).
"""
from __future__ import annotations

import f5_core as core
from f5_core import InputError

VENUE_KEY = "ibkr"
CEILING_DEFAULT_USD = 6000.0     # spec 8.3: USD 6,000, marked u, when docs/DECISIONS.md records no ceiling
SIGMA_DAY_SHARE = 0.02           # spec 8.3: sigma_day at one contract against 2% of the ceiling
FEE_TOL = 1e-9
BAND_RULE = "G(h) <= 1.10 min G only (LR-F5-IBKR: own account, no DLL, MLL or flat-by-close condition)"
MARGIN_KEYS = ("margin_intraday_initial_usd", "margin_overnight_initial_usd", "margin_overnight_maintenance_usd")


def _num(x, what: str):
    """A non-negative number, or None for null / {"unknown": true}; bools and text are refused."""
    if isinstance(x, dict):
        x = None if x.get("unknown") is True else x.get("value")
    if x is None:
        return None
    if isinstance(x, bool) or not isinstance(x, (int, float)):
        raise InputError(f"{what}: not a number: {x!r}")
    if x < 0:
        raise InputError(f"{what}: must be >= 0, got {x}")
    return float(x)


def check_limits(doc: dict) -> None:
    """LR-F5-IBKR assumes an own account without DLL, MLL or flat-by-close; a file stating one is refused."""
    stated = {k: doc.get(k) for k in ("dll", "mll", "flat_by_close") if doc.get(k) is not None}
    if stated:
        raise InputError(f"venue file states {stated}; LR-F5-IBKR's band assumes no DLL, MLL or flat-by-close")


def capital_ceiling(doc: dict) -> tuple[float, bool]:
    """(ceiling USD, unknown flag): the venue file's capital_ceiling_usd, else USD 6,000 (u) (spec 8.3)."""
    c = _num(doc.get("capital_ceiling_usd"), "venue capital_ceiling_usd")
    if c is None:
        return CEILING_DEFAULT_USD, True
    if c <= 0:
        raise InputError(f"venue capital_ceiling_usd must be > 0, got {c}")
    return c, False


def overnight_allowed(doc: dict) -> bool | None:
    v = doc.get("overnight_holds_allowed")
    return v if isinstance(v, bool) else None


def venue_fee(code: str, entry: dict) -> tuple[float, float] | None:
    """(all-in fee per side, F_rt = 2 x per side) in USD, or None when the per-side fee is not published.
    A stated fee_rt_usd that differs from 2 x per side is refused (an inconsistent venue file)."""
    per_side = _num(entry.get("fee_per_side_usd"), f"venue {code} fee_per_side_usd")
    if per_side is None:
        return None
    fee_rt = 2.0 * per_side
    stated = _num(entry.get("fee_rt_usd"), f"venue {code} fee_rt_usd")
    if stated is not None and abs(stated - fee_rt) > FEE_TOL * max(1.0, fee_rt):
        raise InputError(f"venue {code}: fee_rt_usd {stated} != 2 x fee_per_side_usd {per_side}")
    return per_side, fee_rt


def margins(code: str, entry: dict) -> dict:
    return {k: _num(entry.get(k), f"venue {code} {k}") for k in MARGIN_KEYS}


def band_g_only(rows: dict, gmin: float | None) -> tuple[dict, dict]:
    """(B, new rows with G_over_min and in_band) for B = {h in 5..240, OC : G(h) <= 1.10 min G} (LR-F5-IBKR).
    Boundaries inclusive within f5_core.REL_TOL, as for the firm pairs."""
    members, excluded, out_rows = [], {}, {}
    for key, row in rows.items():
        ratio = row["G"] / gmin if row.get("G") is not None and gmin else None
        out_rows[key] = {**row, "G_over_min": ratio, "in_band": False}
    for key in core.BAND_CANDIDATES:
        row = rows[key]
        if row.get("G") is None or gmin is None:
            excluded[key] = ["G unknown (sigma or n_cap unknown or zero)"]
        elif not core.le_tol(row["G"], core.BAND_G_FACTOR * gmin):
            excluded[key] = [f"G/minG = {row['G'] / gmin:.4f} > {core.BAND_G_FACTOR:.2f}"]
        else:
            members.append(key)
            out_rows[key] = {**out_rows[key], "in_band": True}
    idx = [core.BAND_CANDIDATES.index(k) for k in members]
    contiguous = bool(idx) and idx == list(range(idx[0], idx[-1] + 1))
    return ({"members": members, "shortest": members[0] if members else None,
             "longest": members[-1] if members else None, "contiguous": contiguous, "excluded": excluded,
             "rule": BAND_RULE}, out_rows)


def session_columns(rows: dict, main_start: int | None, main_end: int | None) -> dict:
    """Latest start of an h-minute hold that ends by the main session's end, and whether it fits in the session."""
    none_rule = core.FlatByClose("none", None, "own account: none")
    out = {}
    for key, row in rows.items():
        if main_start is None or main_end is None:
            start, fits = None, None
        else:
            start, fits = core.latest_start(key, main_start, main_end, none_rule)
        out[key] = {**row, "latest_start_pt": core.min_to_hhmm(start) if start is not None and start >= 0 else None,
                    "fits_main_session": fits}
    return out


def q6_inputs(f3_root: dict, v: float, mg: dict, ceiling: float, ceiling_u: bool) -> dict:
    """LR-Q6d: spec 8.3's own-broker Q6 inputs for one code (inputs and comparisons only, no Q6 score)."""
    sig_cc = ((f3_root.get("overnight") or {}).get("cc") or {}).get("sigma")
    sig_oc = (f3_root.get("OC") or {}).get("sigma")
    limit = SIGMA_DAY_SHARE * ceiling

    def exceeds(x, lim):
        return None if x is None else x > lim

    day_usd = None if sig_cc is None else sig_cc * v
    return {"capital_ceiling_usd": ceiling, "capital_ceiling_u": ceiling_u,
            "margin_intraday_initial_usd": mg["margin_intraday_initial_usd"],
            "margin_overnight_initial_usd": mg["margin_overnight_initial_usd"],
            "margin_intraday_exceeds_ceiling": exceeds(mg["margin_intraday_initial_usd"], ceiling),
            "margin_overnight_exceeds_ceiling": exceeds(mg["margin_overnight_initial_usd"], ceiling),
            "sigma_day_basis": "sigma_cc (F3 overnight close-to-close, ticks) x tick value (LR-Q6d)",
            "sigma_cc_ticks": sig_cc, "sigma_day_usd": day_usd, "sigma_day_limit_usd": limit,
            "sigma_day_limit_rule": f"{SIGMA_DAY_SHARE:.0%} of the capital ceiling",
            "sigma_day_exceeds_limit": exceeds(day_usd, limit),
            "sigma_OC_ticks": sig_oc, "sigma_OC_usd": None if sig_oc is None else sig_oc * v}


def venue_block(code: str, f3_root: dict, v: float, crt: float, s_unknown: bool, entry: dict, fee: tuple,
                sr80: dict, main_start: int | None, main_end: int | None, ceiling: float, ceiling_u: bool,
                allowed: bool | None, overnight_fee) -> dict:
    """The own-broker row set "ibkr|<CODE>" (cost basis c_f with the venue's fee)."""
    per_side, fee_rt = fee
    cf = core.c_firm(crt, fee_rt, v)
    mg = margins(code, entry)
    rows0, on0 = core.horizon_rows(f3_root, cf, crt, sr80)
    rows1 = session_columns(rows0, main_start, main_end)
    on1 = {k: {**r, "latest_start_pt": None, "fits_main_session": None, "overnight_allowed": allowed,
               "margin_overnight_initial_usd": mg["margin_overnight_initial_usd"],
               "margin_overnight_maintenance_usd": mg["margin_overnight_maintenance_usd"]}
           for k, r in on0.items()}
    gmin, argmin = core.g_minimum(rows1, on1)
    b, rows2 = band_g_only(rows1, gmin)
    u = ["S: no sourced spread -> 1 tick (u)"] if s_unknown else []
    if ceiling_u:
        u.append(f"capital ceiling: none recorded -> USD {ceiling:,.0f} (u)")
    u += [f"{k} unknown (u)" for k, x in mg.items() if x is None]
    if allowed is None:
        u.append("overnight allowed: unknown (u)")
    late = [k for k in b["members"] if rows2[k].get("fits_main_session") is False]
    if late:
        u.append(f"band members {late}: the hold does not fit inside the main session (flag for the lead)")
    return {"venue": VENUE_KEY, "code": code, "tick_value_usd": v,
            "fee_per_side_usd": per_side, "fee_rt_usd": fee_rt,
            "fee_rule": "F_rt = 2 x all-in fee per side (LR-F5-IBKR)", "fee_status": entry.get("fee_status"),
            "fee_rt_usd_stated": entry.get("fee_rt_usd"), "fee_ticks": fee_rt / v,
            "S": crt - core.SLIPPAGE_RT, "S_unknown": s_unknown, "c_RT": crt, "c_f": cf, "cost_basis": "c_f",
            "DLL_f": None, "MLL_f": None, "flat_by_close": "none (own account)",
            "limits": "own account: no DLL, MLL or flat-by-close (LR-F5-IBKR)",
            "main_session_pt": f3_root.get("main_session_pt"), "overnight_allowed": allowed,
            "overnight_position_fee": overnight_fee, **mg,
            "rows": rows2, "overnight_rows": on1, "G_min": gmin, "G_argmin": argmin,
            "band": {**b, **core.band_context(rows2)}, "verdict": core.verdict(b["members"], argmin),
            "Q6_inputs": q6_inputs(f3_root, v, mg, ceiling, ceiling_u), "u": u}
