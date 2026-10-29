"""E.32b F5 core: the holding-time formulas of spec section 7, pure functions on plain inputs (no file access).

Spec: reports/stage_e32b_ranking_spec.md section 7 (frozen). Interpretations of clauses the spec leaves open are
marked "INTERPRETATION" below and listed in README.md for the lead.
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass

INTRADAY_H = (1, 2, 5, 15, 30, 60, 120, 240)
OVERNIGHT_KEYS = ("cc", "on")
ROW_ORDER = tuple(str(h) for h in INTRADAY_H) + ("OC",)          # the section 7 rows, in order
BAND_CANDIDATES = ("5", "15", "30", "60", "120", "240", "OC")    # B's candidate set, in order
SLIPPAGE_RT = 0.5            # c_RT = S + 0.5 (spec 3 D1, 7)
S_UNKNOWN = 1.0              # S = 1 (u) where none is sourced (spec 1)
ENTRY_CAP = 20               # the program's entry cap (spec 9.2)
DAYS_PER_YEAR = 252          # spec 9.2
NORMAL_FACTOR = 1.596        # p = 0.5 + g / (1.596 sigma_h): 2 E|Z| = 2 sqrt(2/pi) (spec 7)
BAND_G_FACTOR = 1.10         # G(h) <= 1.10 min G
BAND_DLL_MIN = 2.0           # DLL_f / (sigma_h v) >= 2
REL_TOL = 1e-12              # boundary tolerance: a value equal to a band boundary up to float error is inside
SR80_KEYS = ("disc_G3", "disc_G3G4", "test")
TZ_OFFSET_FROM_PT = {        # minutes to subtract from a local clock time to get Pacific time (US zones share DST)
    "PT": 0, "PST": 0, "PDT": 0, "AMERICA/VANCOUVER": 0, "AMERICA/LOS_ANGELES": 0,
    "MT": 60, "MST": 60, "MDT": 60, "AMERICA/DENVER": 60,
    "CT": 120, "CST": 120, "CDT": 120, "AMERICA/CHICAGO": 120,
    "ET": 180, "EST": 180, "EDT": 180, "AMERICA/NEW_YORK": 180,
}


class InputError(ValueError):
    """An input violates SCHEMA.md."""


# ---------------------------------------------------------------- small helpers

def le_tol(x: float, limit: float) -> bool:
    return x <= limit + REL_TOL * max(1.0, abs(limit))


def ge_tol(x: float, limit: float) -> bool:
    return x >= limit - REL_TOL * max(1.0, abs(limit))


def hhmm_to_min(text: str) -> int:
    m = re.fullmatch(r"\s*(\d{1,2}):(\d{2})\s*", str(text))
    if not m or int(m.group(1)) > 23 or int(m.group(2)) > 59:
        raise InputError(f"not an HH:MM time: {text!r}")
    return int(m.group(1)) * 60 + int(m.group(2))


def min_to_hhmm(minutes: int | None) -> str | None:
    if minutes is None:
        return None
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


@dataclass(frozen=True)
class FlatByClose:
    status: str          # "time" | "none" (the firm has no flat-by-close rule) | "unknown"
    pt_min: int | None   # minutes after midnight, Pacific time
    raw: object


def _clock_with_tz(text: str) -> int:
    m = re.fullmatch(r"\s*(\d{1,2}):(\d{2})\s*(?:([AaPp][Mm])\s+)?([A-Za-z_/]+)\s*", text)
    if not m:
        raise InputError(f"flat_by_close {text!r}: expected 'HH:MM TZ' or 'H:MM AM/PM TZ' (TZ such as CT, ET, PT)")
    hour, minute, ampm, tz = int(m.group(1)), int(m.group(2)), m.group(3), m.group(4).upper()
    if ampm:
        if not 1 <= hour <= 12:
            raise InputError(f"flat_by_close {text!r}: bad 12-hour clock")
        hour = hour % 12 + (12 if ampm.upper() == "PM" else 0)
    if hour > 23 or minute > 59:
        raise InputError(f"flat_by_close {text!r}: bad time")
    if tz not in TZ_OFFSET_FROM_PT:
        raise InputError(f"flat_by_close {text!r}: unknown time zone {tz}")
    return (hour * 60 + minute - TZ_OFFSET_FROM_PT[tz]) % (24 * 60)


def parse_flat_by_close(raw) -> FlatByClose:
    """Accepted forms (SCHEMA.md): null / {"unknown": true} -> unknown; "none", false or {"none": true} -> no rule;
    "15:10 CT", "3:10 PM CT"; {"time": "15:10", "tz": "CT"}; {"pt": "13:10"}; any of these under {"value": ...}."""
    node = raw
    if isinstance(node, dict) and "value" in node and not ({"time", "tz", "pt"} & node.keys()):
        if node.get("unknown") is True:
            return FlatByClose("unknown", None, raw)
        node = node["value"]
    if node is None or (isinstance(node, dict) and node.get("unknown") is True):
        return FlatByClose("unknown", None, raw)
    if node is False or (isinstance(node, str) and node.strip().lower() in ("none", "no rule")) or (
            isinstance(node, dict) and node.get("none") is True):
        return FlatByClose("none", None, raw)
    if isinstance(node, str):
        return FlatByClose("time", _clock_with_tz(node), raw)
    if isinstance(node, dict) and "pt" in node:
        return FlatByClose("time", hhmm_to_min(node["pt"]), raw)
    if isinstance(node, dict) and "time" in node and "tz" in node:
        return FlatByClose("time", _clock_with_tz(f"{node['time']} {node['tz']}"), raw)
    raise InputError(f"flat_by_close: unrecognised form {raw!r}")


# ---------------------------------------------------------------- per-horizon formulas

def c_rt(spread_ticks: float | None) -> tuple[float, bool]:
    """c_RT = S + 0.5; S = 1 (u) when not sourced. Returns (c_RT, S_unknown)."""
    if spread_ticks is None:
        return S_UNKNOWN + SLIPPAGE_RT, True
    if spread_ticks < 0:
        raise InputError(f"spread S must be >= 0, got {spread_ticks}")
    return spread_ticks + SLIPPAGE_RT, False


def c_firm(c_rt_ticks: float, fee_rt_usd: float, tick_value_usd: float) -> float:
    """c_f = c_RT + F_rt,f / v."""
    if tick_value_usd is None or tick_value_usd <= 0:
        raise InputError(f"tick value must be > 0, got {tick_value_usd}")
    if fee_rt_usd is None or fee_rt_usd < 0:
        raise InputError(f"round-trip fee must be >= 0, got {fee_rt_usd}")
    return c_rt_ticks + fee_rt_usd / tick_value_usd


def n_max(row_key: str, l_main: int | None) -> int | None:
    """n_max(h) = floor(L_main / h); OC and the overnight holds: 1 a day."""
    if row_key == "OC" or row_key in OVERNIGHT_KEYS:
        return 1
    if l_main is None:
        return None
    return l_main // int(row_key)


def n_cap(nmax: int | None) -> int | None:
    return None if nmax is None else min(ENTRY_CAP, nmax)


def hit_rate(g: float, m: float | None, sigma: float | None) -> tuple[float | None, float | None]:
    """(p empirical = 0.5 + g / (2 m_h), p normal = 0.5 + g / (1.596 sigma_h)); values above 1 are kept as is."""
    p_emp = None if not m else 0.5 + g / (2 * m)
    p_norm = None if not sigma else 0.5 + g / (NORMAL_FACTOR * sigma)
    return p_emp, p_norm


def _div(a, b):
    return None if a is None or not b else a / b


def horizon_row(row_key: str, stats: dict | None, l_main: int | None, cost: float, cost_rt: float,
                sr80: dict) -> dict:
    """All firm-independent section 7 quantities at one horizon for a cost basis `cost` (c_RT or c_f)."""
    stats = stats or {}
    sigma = stats.get("sigma")
    m = stats.get("m")
    if sigma is not None and sigma <= 0:
        sigma = None  # a non-positive sigma is treated as unknown
    nm = n_max(row_key, l_main)
    nc = n_cap(nm)
    usable = sigma is not None and nc is not None and nc > 0
    p_be = hit_rate(cost, m, sigma)
    p_1 = hit_rate(cost + 1, m, sigma)
    row = {
        "sigma": sigma, "m": m, "n_pairs": stats.get("n"),
        "k_RT": _div(cost_rt, sigma), "k": _div(cost, sigma),
        "g_be": cost, "g_1": cost + 1,
        "p_be_emp": p_be[0], "p_be_norm": p_be[1], "p_1_emp": p_1[0], "p_1_norm": p_1[1],
        "n_max": nm, "n_cap": nc, "trades_per_year": None if nc is None else nc * DAYS_PER_YEAR,
    }
    for key in SR80_KEYS:
        e80 = sr80[key] * sigma / math.sqrt(nc) if usable else None
        row[f"e80_{key}"] = e80
        row[f"gross_detect_{key}"] = None if e80 is None else cost + e80
    row["G_cost_term"] = cost / sigma if usable else None
    row["G_power_term"] = sr80["test"] / math.sqrt(nc) if usable else None
    row["G"] = row["G_cost_term"] + row["G_power_term"] if usable else None
    return row


def horizon_rows(f3_root: dict, cost: float, cost_rt: float, sr80: dict) -> tuple[dict, dict]:
    """(rows for 1..240 and OC, overnight rows cc and on)."""
    l_main = f3_root.get("L_main")
    h_stats = f3_root.get("h") or {}
    rows = {key: horizon_row(key, h_stats.get(key), l_main, cost, cost_rt, sr80) for key in ROW_ORDER[:-1]}
    rows["OC"] = horizon_row("OC", f3_root.get("OC"), l_main, cost, cost_rt, sr80)
    on = f3_root.get("overnight") or {}
    overnight = {key: horizon_row(key, on.get(key), l_main, cost, cost_rt, sr80) for key in OVERNIGHT_KEYS}
    return rows, overnight


# ---------------------------------------------------------------- prop rules by horizon

def latest_start(row_key: str, main_start: int, main_end: int, flat: FlatByClose) -> tuple[int | None, bool | None]:
    """(latest start in PT minutes, fits) for an h-minute hold inside the main session and before flat-by-close.

    INTERPRETATION: the hold must end by min(main-session end, flat-by-close); it fits if that latest start is not
    before the main-session start. OC runs from the main-session start to its end, so it fits iff flat-by-close is not
    before the main-session end. Unknown flat-by-close: computed against the main-session end, fits = None (u)."""
    end = main_end if flat.status != "time" else min(main_end, flat.pt_min)
    if row_key == "OC":
        fits = True if flat.status == "none" else (None if flat.status == "unknown" else flat.pt_min >= main_end)
        return main_start, fits
    start = end - int(row_key)
    if flat.status == "unknown":
        return start, (None if start >= main_start else False)
    return start, start >= main_start


def _limit_ratios(row: dict, dll: float | None, mll: float | None, tick_value: float) -> dict:
    sv = None if row["sigma"] is None else row["sigma"] * tick_value
    return {"dll_ratio": _div(dll, sv), "mll_ratio": _div(mll, sv)}


def with_prop_columns(rows: dict, overnight: dict, dll: float | None, mll: float | None, tick_value: float,
                      main_start: int | None, main_end: int | None, flat: FlatByClose,
                      overnight_allowed: bool | None) -> tuple[dict, dict]:
    """New firm rows with DLL_f / (sigma_h v), MLL_f / (sigma_h v), the latest start and the flat-by-close fit."""
    out_rows = {}
    for key, row in rows.items():
        if main_start is None or main_end is None:
            start, fits = None, None
        else:
            start, fits = latest_start(key, main_start, main_end, flat)
        out_rows[key] = {**row, **_limit_ratios(row, dll, mll, tick_value),
                         "latest_start_pt": min_to_hhmm(start) if start is not None and start >= 0 else None,
                         "fits_flat_by_close": fits}
    out_on = {key: {**row, **_limit_ratios(row, dll, mll, tick_value), "latest_start_pt": None,
                    "fits_flat_by_close": None, "overnight_allowed": overnight_allowed}
              for key, row in overnight.items()}
    return out_rows, out_on


# ---------------------------------------------------------------- band and verdict

def g_minimum(rows: dict, overnight: dict) -> tuple[float | None, list[str]]:
    """min G over every row with a G (1..240, OC, cc, on) and the keys attaining it (ties within REL_TOL).

    INTERPRETATION: one minimum over all rows, used both for the band's 1.10 min G and for the verdict's
    'minimum of G lies at ...' (which names 1-2 minutes, OC and overnight, so those rows are in the set)."""
    allg = {k: r["G"] for k, r in list(rows.items()) + list(overnight.items()) if r.get("G") is not None}
    if not allg:
        return None, []
    gmin = min(allg.values())
    order = list(ROW_ORDER) + list(OVERNIGHT_KEYS)
    return gmin, [k for k in order if k in allg and le_tol(allg[k], gmin)]


def _band_test(row: dict, gmin: float | None) -> tuple[list[str], list[str]]:
    """(reasons h is excluded, conditions that are unknown) for one candidate row."""
    why, unknown = [], []
    if row.get("G") is None or gmin is None:
        why.append("G unknown (sigma or n_cap unknown or zero)")
    elif not le_tol(row["G"], BAND_G_FACTOR * gmin):
        why.append(f"G/minG = {row['G'] / gmin:.4f} > {BAND_G_FACTOR:.2f}")
    if row.get("dll_ratio") is None:
        unknown.append("DLL_f / (sigma_h v) unknown")
    elif not ge_tol(row["dll_ratio"], BAND_DLL_MIN):
        why.append(f"DLL_f / (sigma_h v) = {row['dll_ratio']:.3f} < {BAND_DLL_MIN:g}")
    if row.get("fits_flat_by_close") is None:
        unknown.append("flat-by-close fit unknown")
    elif row["fits_flat_by_close"] is False:
        why.append("hold does not fit before flat-by-close")
    return why, unknown


def band(rows: dict, gmin: float | None) -> tuple[dict, dict]:
    """(B, new rows with G_over_min and in_band) for B = {h in 5..240, OC : G(h) <= 1.10 min G,
    DLL_f / (sigma_h v) >= 2, the hold fits before flat-by-close}.

    INTERPRETATION: an unknown DLL ratio or an unknown flat-by-close fit does not exclude h; it is marked (u)."""
    members, excluded, unknown, out_rows = [], {}, {}, {}
    for key, row in rows.items():
        ratio = row["G"] / gmin if row.get("G") is not None and gmin else None
        out_rows[key] = {**row, "G_over_min": ratio, "in_band": False}
    for key in BAND_CANDIDATES:
        why, u = _band_test(rows[key], gmin)
        if why:
            excluded[key] = why
            continue
        members.append(key)
        out_rows[key] = {**out_rows[key], "in_band": True}
        if u:
            unknown[key] = u
    idx = [BAND_CANDIDATES.index(k) for k in members]
    contiguous = bool(idx) and idx == list(range(idx[0], idx[-1] + 1))
    result = {"members": members, "shortest": members[0] if members else None,
              "longest": members[-1] if members else None, "contiguous": contiguous,
              "excluded": excluded, "unknown_conditions": unknown}
    return result, out_rows


def band_context(rows: dict) -> dict:
    """Facts for the band's reason: the k curve's successive ratios and where the power term overtakes cost."""
    order = list(ROW_ORDER)
    steps = {}
    for a, b in zip(order, order[1:], strict=False):
        ka, kb = rows[a].get("k"), rows[b].get("k")
        steps[f"{a}->{b}"] = None if ka is None or kb is None or ka == 0 else kb / ka
    power_from = next((k for k in order if rows[k].get("G_power_term") is not None
                       and rows[k]["G_power_term"] >= rows[k]["G_cost_term"]), None)
    return {"k_step_ratios": steps, "power_term_exceeds_cost_from": power_from}


def verdict(members: list[str], argmin: list[str]) -> dict:
    """The user's prior per pair (spec 7).

    fails: B empty, or min G at 1 or 2 minutes, or min G only at OC or overnight (these take precedence);
    partly: B contains OC (INTERPRETATION: also when OC is B's only member);
    holds: B non-empty and inside 5..240 minutes."""
    fails = []
    if not members:
        fails.append("B is empty")
    if set(argmin) & {"1", "2"}:
        fails.append(f"min G lies at {'/'.join(k for k in argmin if k in ('1', '2'))} minute(s)")
    if argmin and set(argmin) <= {"OC", *OVERNIGHT_KEYS}:
        fails.append(f"min G lies only at {'/'.join(argmin)}")
    if not argmin:
        fails.append("no G computable")
    if fails:
        return {"value": "fails", "reason": "; ".join(fails)}
    if "OC" in members:
        only = members == ["OC"]
        return {"value": "partly", "reason": "B contains only OC" if only else "B contains OC besides intraday holds"}
    return {"value": "holds", "reason": f"B = {', '.join(members)} minutes, inside 5 to 240"}
