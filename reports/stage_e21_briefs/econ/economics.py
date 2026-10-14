"""Stage E.21 F8 descriptive economics (not part of any verdict).

Reads only: reports/stage_e21_runs/{T1..T4}_result.json, verdict.json, per_root/<ROOT>.json,
reports/stage_e13_trend_carry.md (C2 values transcribed below, with the row names),
reports/stage_e21_proped_rules.json. Writes reports/stage_e21_economics.json and .md.
Never writes under reports/stage_e21_runs/. Prints summaries only.
"""
import datetime as dt
import json
import math
import os
from pathlib import Path

import numpy as np

os.nice(10)

REPO = Path(__file__).resolve().parents[3]
RUNS = REPO / "reports" / "stage_e21_runs"
OUT_JSON = REPO / "reports" / "stage_e21_economics.json"
OUT_MD = REPO / "reports" / "stage_e21_economics.md"
PROPED = REPO / "reports" / "stage_e21_proped_rules.json"

ROOTS = ["6E", "CL", "GC", "HE", "LE", "NG", "NQ", "RTY", "TN", "UB", "ZB", "ZC", "ZF", "ZL",
         "ZN", "ZS", "ZT"]
TAUS = [0.15, 0.25]
K_LEVELS = [10_000, 25_000, 50_000, 100_000]
W_TARGET = 0.40
S_MAX = {"T1": 17, "T2": 17, "T3": 2}
WINDOW = 21

# E.13 C2 "$ risk / contract / yr" (reports/stage_e13_trend_carry.md lines 214-262), by C2 row code.
C2_RISK = {"MNQ": 9743, "M2K": 2014, "MGC": 9254, "MCL": 2777, "M6E": 787, "6E": 7859,
           "2YY": 745, "5YY": 752, "10YY": 670, "30YY": 587, "MTN": 645, "MWN": 1137,
           "ZT": 3116, "ZF": 3581, "ZN": 5186, "TN": 6453, "ZB": 9703, "UB": 11366,
           "NG": 13183, "ZC": 3817, "ZS": 7914, "ZL": 8971, "HE": 6586, "LE": 14666,
           "MNG": 1318, "MZC": 382, "MZS": 791, "MZL": 897}

# F8 vehicle per root, how one E.12 vehicle contract converts to F8 vehicle contracts (r), and flags.
# r = notional ratio where the contracts share the underlying; for micro yield futures (quoted in
# yield, $10 DV01) r = C2 risk ratio E.12 vehicle / F8 vehicle (no notional ratio exists).
F8 = {
    "NQ": ("MNQ", 1.0, "same as E.12 vehicle", False),
    "RTY": ("M2K", 1.0, "same as E.12 vehicle", False),
    "GC": ("MGC", 1.0, "same as E.12 vehicle", False),
    "CL": ("MCL", 1.0, "same as E.12 vehicle", False),
    "6E": ("M6E", 10.0, "notional ratio EUR 125,000 / EUR 12,500", False),
    "TN": ("MTN", 10.0, "notional ratio $1,000/pt / $100/pt", False),
    "UB": ("MWN", 10.0, "notional ratio $1,000/pt / $100/pt", False),
    "ZT": ("2YY", 3116 / 745, "C2 risk ratio ZT 3,116 / 2YY 745 (yield future: no notional ratio)", False),
    "ZF": ("5YY", 3581 / 752, "C2 risk ratio ZF 3,581 / 5YY 752 (yield future: no notional ratio)", False),
    "ZN": ("10YY", 5186 / 670, "C2 risk ratio ZN 5,186 / 10YY 670 (yield future: no notional ratio)", False),
    "ZB": ("30YY", 9703 / 587, "C2 risk ratio ZB 9,703 / 30YY 587 (yield future: no notional ratio)", False),
    "NG": ("NG", 1.0, "full-size, FLAGGED (brief: no micro in F8's list; C2 lists MNG)", True),
    "ZC": ("ZC", 1.0, "full-size, FLAGGED (brief; C2 lists MZC)", True),
    "ZS": ("ZS", 1.0, "full-size, FLAGGED (brief; C2 lists MZS)", True),
    "ZL": ("ZL", 1.0, "full-size, FLAGGED (brief; C2 lists MZL)", True),
    "HE": ("HE", 1.0, "full-size, FLAGGED (no micro in C2)", True),
    "LE": ("LE", 1.0, "full-size, FLAGGED (no micro in C2)", True),
}
# Supplementary only (not the brief's book): grain/gas micros C2 lists.
F8_SUPP_MICRO = {"NG": "MNG", "ZC": "MZC", "ZS": "MZS", "ZL": "MZL"}

PROPED_LISTED = {"MNQ", "M2K", "MGC", "MCL", "NG", "ZC", "ZS", "ZL", "ZT", "ZF", "ZN", "ZB", "6E"}
FULL_SIZE_F8 = {"NG", "ZC", "ZS", "ZL", "HE", "LE"}  # count 10 micro-equivalents each


def rnd(x):
    return float(np.sign(x) * np.floor(np.abs(x) + 0.5))


def load(p):
    with open(p) as f:
        return json.load(f)


def series_of(test):
    d = load(RUNS / f"{test}_result.json")
    s = d["series"]["base"]
    return [r[0] for r in s], np.array([r[1] for r in s], dtype=float), d["stats"]["base"]


def root_book(pr, test):
    """Per root: fills sorted by ts, per-contract daily $ dict."""
    fills = sorted(pr["fills"].get(test, []), key=lambda f: f["ts"])
    return fills, pr["per_contract_daily_dollars"]


def reconstruct(per_root, test, dates, scale=None):
    """Fractional (scale None, capital units) or integer (F8 contracts at capital scale) book.

    Returns daily total, gross-by-root holdings per date (contracts), fill costs per date,
    per-root median base per-contract cost (F8 units, $), diagnostics.
    """
    idx = {d: i for i, d in enumerate(dates)}
    n = len(dates)
    total = np.zeros(n)
    gross = np.zeros(n)
    costs = np.zeros(n)
    held_by_root = {}
    med_cost = {}
    diag = {"null_pnl_while_held": 0, "fills_off_series": 0}
    for root, pr in per_root.items():
        fills, pc = root_book(pr, test)
        if not fills:
            continue
        r = F8[root][1]
        # state changes from non-roll fills, applied from the next date on
        changes = []  # (date, held value in output units)
        c_cur = 0.0
        frac_cur = 0.0
        cost_day = {}
        cpc_list = []
        for f in fills:
            cpc = f["cost_per_contract_cents"]["base"] / 100.0 / r  # $ per F8 contract
            cpc_list.append(cpc)
            if f["kind"] in ("roll_out", "roll_in"):
                if scale is None:
                    c = abs(f["trade"]) * f["cost_per_contract_cents"]["base"] / 100.0
                    c_ref = f["cost"]["base"]
                    if abs(c - c_ref) > 1e-9 + 1e-6 * abs(c_ref):
                        diag.setdefault("cost_mismatch", 0)
                        diag["cost_mismatch"] += 1
                    cost_day[f["date"]] = cost_day.get(f["date"], 0.0) + c_ref
                else:
                    cost_day[f["date"]] = cost_day.get(f["date"], 0.0) + abs(c_cur) * cpc
                continue
            frac_cur = f["held_after"]
            if scale is None:
                cost_day[f["date"]] = cost_day.get(f["date"], 0.0) + f["cost"]["base"]
                changes.append((f["date"], frac_cur))
            else:
                c_new = rnd(scale * r * frac_cur)
                cost_day[f["date"]] = cost_day.get(f["date"], 0.0) + abs(c_new - c_cur) * cpc
                c_cur = c_new
                changes.append((f["date"], c_cur))
        med_cost[root] = float(np.median(cpc_list))
        held = np.zeros(n)
        j = 0
        cur = 0.0
        for i, d in enumerate(dates):
            while j < len(changes) and changes[j][0] < d:
                cur = changes[j][1]
                j += 1
            held[i] = cur
        pnl_unit = np.zeros(n)
        for i, d in enumerate(dates):
            v = pc.get(d)
            if v is None:
                if held[i] != 0 and d in pc:
                    diag["null_pnl_while_held"] += 1
                continue
            pnl_unit[i] = v if scale is None else v / r
        g = held * pnl_unit
        cst = np.zeros(n)
        for d, c in cost_day.items():
            if d in idx:
                cst[idx[d]] += c
            else:
                diag["fills_off_series"] += 1
        gross += g
        costs += cst
        total += g - cst
        held_by_root[root] = held
    return total, gross, costs, held_by_root, med_cost, diag


def five_day_sd(x):
    m = len(x) // 5
    s = x[: m * 5].reshape(m, 5).sum(axis=1)
    return float(np.std(s, ddof=1)), m


def weekend_follow(dates):
    out = np.zeros(len(dates), dtype=bool)
    for i in range(1, len(dates)):
        p = dt.date.fromisoformat(dates[i - 1])
        d = dt.date.fromisoformat(dates[i])
        k = p + dt.timedelta(days=1)
        while k < d:
            if k.weekday() == 5:
                out[i] = True
                break
            k += dt.timedelta(days=1)
    return out


def no_weekend_series(gross, costs, held_by_root, med_cost, dates):
    wf = weekend_follow(dates)
    extra = np.zeros(len(dates))
    for root, h in held_by_root.items():
        extra += wf * 2.0 * np.abs(h) * med_cost[root]
    g = np.where(wf, 0.0, gross)
    return g - costs - extra, int(wf.sum()), float(extra.sum())


def window_breach(pnl, dd, dll=None):
    n = len(pnl)
    nw = n - WINDOW + 1
    tr = st = dl = 0
    worst_tr = []
    for s in range(nw):
        e = np.concatenate([[0.0], np.cumsum(pnl[s: s + WINDOW])])
        peak = np.maximum.accumulate(e)
        tdd = float(np.max(peak - e))
        sdd = float(max(0.0, -np.min(e)))
        worst_tr.append(tdd)
        daily = dll is not None and bool(np.any(pnl[s: s + WINDOW] < -dll))
        tr += (tdd >= dd) or daily
        st += (sdd >= dd) or daily
        dl += daily
    return {"windows": nw, "trailing_share": tr / nw, "static_share": st / nw,
            "dll_only_share": (dl / nw) if dll is not None else None,
            "median_worst_trailing_dd": float(np.median(worst_tr))}


def num(x):
    return x if isinstance(x, (int, float)) and not isinstance(x, bool) else None


def personal(test, sigma_b, binding_risk_roots):
    out = {}
    roots = binding_risk_roots
    risks = {r: C2_RISK[F8[r][0]] for r in roots}
    imax = max(risks, key=risks.get)
    S = S_MAX[test]
    for tau in TAUS:
        k = tau / sigma_b
        kmin = risks[imax] * S / (k * W_TARGET)
        per = {}
        for r in roots:
            row = {"vehicle": F8[r][0], "risk": risks[r],
                   "at_Kmin": k * kmin * W_TARGET / S / risks[r]}
            for K in K_LEVELS:
                row[f"at_{K}"] = k * K * W_TARGET / S / risks[r]
            per[r] = row
        zeros = {K: sorted(r for r in roots if rnd(per[r][f"at_{K}"]) == 0) for K in K_LEVELS}
        out[f"tau_{int(tau*100)}"] = {"k": k, "K_min": kmin, "binding": imax,
                                      "per_root": per, "round_to_zero": zeros}
    # supplementary: grain/gas micros from C2
    risks2 = dict(risks)
    for r, m in F8_SUPP_MICRO.items():
        if r in risks2:
            risks2[r] = C2_RISK[m]
    i2 = max(risks2, key=risks2.get)
    out["supp_with_grain_gas_micros"] = {
        f"tau_{int(t*100)}": {"K_min": risks2[i2] * S / ((t / sigma_b) * W_TARGET),
                              "binding": i2} for t in TAUS}
    out["scale_A"] = risks[imax] * S / W_TARGET
    return out


def main():
    per_root = {r: load(RUNS / "per_root" / f"{r}.json") for r in ROOTS}
    verdict = load(RUNS / "verdict.json")
    proped = load(PROPED)
    res = {"schema": "stage_e21_economics/1", "descriptive_only": True,
           "verdicts_unchanged": {t: verdict["tests"][t]["pass"] for t in verdict["tests"]},
           "tests": {}}
    plans = proped["plans"] + [dict(p, _comparison=True) for p in proped["comparison"]]
    for test in ["T1", "T2", "T3"]:
        dates, x, st = series_of(test)
        sigma_b = float(np.std(x, ddof=1) * math.sqrt(252))
        roots = [r for r in ROOTS if per_root[r]["fills"].get(test)]
        smax_seen = max((h.get("S_M") or h.get("S_u") or 0) for r in roots
                        for h in per_root[r]["holdings"][test])
        # fractional reconstruction check
        tot_f, _, _, _, _, diag_f = reconstruct(per_root, test, dates)
        recon_err = float(np.max(np.abs(tot_f - x)))
        pers = personal(test, sigma_b, roots)
        A = pers["scale_A"]
        tot_i, gross_i, cost_i, held_i, medc, diag_i = reconstruct(per_root, test, dates, scale=A)
        sd1 = float(np.std(tot_i, ddof=1))
        sd5, n5 = five_day_sd(tot_i)
        f = x * sd1 / float(np.std(x, ddof=1))
        te = float(np.std(tot_i - f, ddof=1))
        corr = float(np.corrcoef(tot_i, x)[0, 1])
        # contract counts
        held_any = np.array([held_i[r] for r in held_i])
        nz_rows = {r: {"max_abs": float(np.max(np.abs(held_i[r]))),
                       "share_days_nonzero_given_root_signal": None,
                       "rebal_targets_rounding_to_zero": None} for r in held_i}
        for r in held_i:
            tg = [h["target"] for h in per_root[r]["holdings"][test]
                  if h.get("target") not in (None, 0.0)]
            z = sum(1 for t in tg if rnd(A * F8[r][1] * t) == 0)
            nz_rows[r]["rebal_targets_rounding_to_zero"] = f"{z}/{len(tg)}"
        microeq = sum(np.abs(held_i[r]) * (10 if F8[r][0] in FULL_SIZE_F8 else 1) for r in held_i)
        nw_pnl, n_wk, wk_cost = no_weekend_series(gross_i, cost_i, held_i, medc, dates)
        book = {"scale_A_capital_dollars_at_unit_leverage": A, "n_dates": len(dates),
                "daily_mean": float(np.mean(tot_i)), "daily_sd": sd1,
                "five_day_sd": sd5, "five_day_blocks": n5,
                "annual_mean": float(np.mean(tot_i) * 252), "annual_sd": sd1 * math.sqrt(252),
                "gross_total": float(gross_i.sum()), "cost_total": float(cost_i.sum()),
                "tracking_error_daily_sd": te, "tracking_error_annual": te * math.sqrt(252),
                "corr_with_fractional": corr,
                "fractional_scaled_daily_sd": float(np.std(x * A, ddof=1)),
                "max_micro_equivalent": float(np.max(microeq)),
                "per_root": nz_rows, "diag": diag_i,
                "no_weekend": {"daily_sd": float(np.std(nw_pnl, ddof=1)),
                               "five_day_sd": five_day_sd(nw_pnl)[0],
                               "annual_mean": float(np.mean(nw_pnl) * 252),
                               "dates_after_weekend_zeroed": n_wk,
                               "extra_weekend_fill_costs_total": wk_cost}}
        prop = []
        for p in plans:
            dd = num(p.get("drawdown_usd"))
            dll = num(p.get("daily_loss_limit_usd"))
            maxc = p.get("max_contracts")
            maxmicro = None
            if isinstance(maxc, str) and "micro" in maxc:
                try:
                    maxmicro = int(maxc.split("/")[-1].strip().split()[0])
                except ValueError:
                    maxmicro = None
            not_listed = sorted({F8[r][0] for r in held_i if F8[r][0] not in PROPED_LISTED}) \
                if not p.get("_comparison") else "UNSOURCED (Phidias instrument list not collected)"
            row = {"name": p["name"], "comparison": bool(p.get("_comparison")),
                   "drawdown_type": p.get("drawdown_type"), "drawdown_usd": p.get("drawdown_usd"),
                   "daily_loss_limit_usd": p.get("daily_loss_limit_usd"),
                   "max_contracts": maxc, "max_micro_equiv": maxmicro,
                   "book_max_micro_equiv": float(np.max(microeq)),
                   "share_days_over_max": (float(np.mean(microeq > maxmicro))
                                           if maxmicro else None),
                   "instruments_not_listed": not_listed,
                   "overnight": p.get("overnight_allowed"),
                   "weekend": p.get("weekend_allowed"),
                   "weekend_addon_price_usd": p.get("weekend_addon_price_usd"),
                   "automation": "UNCONFIRMED" if not p.get("_comparison")
                   else "semi-automated only (Phidias)",
                   "daily_sd_over_dd": sd1 / dd if dd else None,
                   "five_day_sd_over_dd": sd5 / dd if dd else None}
            if dd:
                row["with_weekend"] = window_breach(tot_i, dd, dll)
                row["without_weekend"] = window_breach(nw_pnl, dd, dll)
                mbest = 0
                for m in range(1, 200):
                    t_m = reconstruct(per_root, test, dates, scale=A * m)[0]
                    if np.std(t_m, ddof=1) <= 0.10 * dd:
                        mbest = m
                    else:
                        break
                if mbest:
                    t_m, g_m, c_m, h_m, mc_m, _ = reconstruct(per_root, test, dates, scale=A * mbest)
                    nw_m = no_weekend_series(g_m, c_m, h_m, mc_m, dates)[0]
                    row["ten_pct_scale"] = {"multiple": mbest,
                                            "with_weekend": window_breach(t_m, dd, dll),
                                            "without_weekend": window_breach(nw_m, dd, dll)}
                else:
                    row["ten_pct_scale"] = "none"
            prop.append(row)
        res["tests"][test] = {"sigma_b": sigma_b, "S_max_used": S_MAX[test],
                              "S_max_in_holdings": smax_seen, "roots": roots,
                              "fractional_recon_max_abs_err": recon_err,
                              "fractional_recon_diag": diag_f,
                              "personal": pers, "integer_book": book, "proped": prop}
        print(test, f"sigma_b={sigma_b:.4f} Smax_seen={smax_seen} recon_err={recon_err:.2e}",
              f"A={A:,.0f} sd1={sd1:,.0f} sd5={sd5:,.0f} TE={te:,.0f} corr={corr:.3f}",
              f"maxmicro={np.max(microeq):.0f} diag={diag_i} fdiag={diag_f}")
    d4, x4, _ = series_of("T4")
    big = np.abs(x4) > 10
    top = np.argsort(-np.abs(x4))[:3]
    res["tests"]["T4"] = {"note": "combination in risk units; no contract book",
                          "realized_vol_annual_risk_units": float(np.std(x4, ddof=1) * math.sqrt(252)),
                          "n_dates": len(d4),
                          "max_abs_daily": float(np.max(np.abs(x4))),
                          "p99_abs_daily": float(np.percentile(np.abs(x4), 99)),
                          "n_days_abs_over_10": int(big.sum()),
                          "largest_days": [[d4[i], float(x4[i])] for i in top],
                          "realized_vol_excl_abs_over_10": float(np.std(x4[~big], ddof=1) * math.sqrt(252))}
    with open(OUT_JSON, "w") as fo:
        json.dump(res, fo, indent=1, default=str)
    print("T4 realized vol", res["tests"]["T4"]["realized_vol_annual_risk_units"])
    OUT_MD.write_text(render(res))
    print("wrote", OUT_JSON, OUT_MD)


# ----------------------------------------------------------------------------------------------
# Markdown rendering (same numbers as the JSON)
# ----------------------------------------------------------------------------------------------
def _f(x, nd=0):
    if x is None:
        return "-"
    if isinstance(x, str):
        return x
    return f"{x:,.{nd}f}"


def _pct(x):
    return "-" if x is None else f"{100 * x:.1f}%"


def _short(s, n=60):
    s = str(s)
    return s if len(s) <= n else s[: n - 3] + "..."


ASSUMPTIONS = [
    "F8 is descriptive only; no verdict changes (verdict.json pass flags are copied into the JSON).",
    "sigma_b = sd (ddof 1) of the run's base-case daily series x sqrt(252), in capital units "
    "(flat days included as zeros, as the run's series has them).",
    "Per-contract annual dollar risk sigma$_i = E.13 C2 '$ risk / contract / yr' (2026-10-02 "
    "prices and Carver T-22 vols; micro yields from T-30). These are today's levels, not the "
    "2010-2024 levels at which the run's targets were set, so the integer book's actual contract "
    "counts differ from the K_min arithmetic (e.g. ZT/2YY: low 2010-2020 rate vol gives large "
    "historical targets).",
    "S = 17 (T1, T2) and 2 (T3), the tests' maximum divisors (confirmed as the maxima of S_M and "
    "S_u in the holdings rows).",
    "Root to F8 vehicle mapping: NQ->MNQ, RTY->M2K, GC->MGC, CL->MCL (these are already the E.12 "
    "vehicles), 6E->M6E, TN->MTN, UB->MWN (notional ratio 10), ZT->2YY, ZF->5YY, ZN->10YY, "
    "ZB->30YY (micro Treasury YIELD futures, $10 DV01; converted by the C2 risk ratio because no "
    "notional ratio exists; FLAG: yield futures move with the on-the-run yield, not the "
    "cheapest-to-deliver price, and the economic direction is inverted, a long note being a short "
    "yield position). NG, ZC, ZS, ZL, HE, LE are full-size, FLAGGED (brief's list; C2 does list "
    "MNG, MZC, MZS, MZL, shown only as a supplementary K_min line; HE and LE have no micro in C2).",
    "K_min(tau) = max_i sigma$_i x S / (k x 0.40), k = tau / sigma_b; per-root contracts at K are "
    "k x K x 0.40 / S / sigma$_i at full signal (|s| = 1); 'rounds to zero' uses round-half-up.",
    "Integer book: capital scale A = max_i sigma$_i x S / 0.40 dollars at unit leverage (= k x "
    "K_min for both tau). Contracts c(i,M) = round_half_up(A x r_i x target(i,M)) in F8 "
    "vehicles, r_i = F8 contracts per E.12 vehicle contract. Per-F8-contract daily P&L = the "
    "run's per_contract_daily_dollars / r_i.",
    "Holding timing: a fill on date d (at MK(d)) changes the holding from date d+1 on; the P&L of "
    "date d belongs to the previous holding. This reproduces the run's base series exactly in "
    "capital units (max abs error reported per test), so the timing and cost reading match the run.",
    "Costs: rebalance/entry/exit fills pay |delta c| x the fill's base cost per contract; each roll "
    "leg pays |c| x that leg's base cost per contract. Cost per F8 contract = the run's E.12 "
    "per-contract cost / r_i (FLAG: proportional scaling; real micro costs per unit of notional "
    "are higher, so micro-converted roots' costs are understated).",
    "No-weekend variant: on each series date whose previous series date lies before a Saturday, the "
    "gross P&L is set to zero; that date's own fill costs are kept; per root 2 x |c held| x the "
    "root's median base per-contract cost (all of its fills in the test, F8 units) is charged on "
    "that date.",
    "Breach windows: every run of 21 consecutive series dates (step 1). Equity starts at 0 at the "
    "window start; trailing = max drop from the running EOD peak (peak includes the start), "
    "static = max drop below the start; breach if the drop >= the drawdown amount, or (where a "
    "daily loss limit is sourced, One Plan only) any day's loss > the limit. Both measures are "
    "shown for every plan; the plan's own type is in the drawdown column (Standard and Instant "
    "say EOD without saying whether it trails; TrueRisk is CONFLICT static vs EOD).",
    "Max contracts: micro-equivalents with 1 mini = 10 micros (PropEd Q31); full-size F8 vehicles "
    "(NG, ZC, ZS, ZL, HE, LE) count as 10, every micro (including 2YY..30YY, MTN, MWN, M6E) as 1. "
    "'share over' = share of series dates whose held micro-equivalent exceeds the plan's micro cap.",
    "10% scale: integer multiples m of A; the largest m with book daily dollar sd <= 10% of the "
    "drawdown. Every root holds >= 1 contract at full signal for m >= 1 by construction (C2 "
    "basis); 'none' when m = 1 already exceeds 10%.",
    "Tracking error: sd of (integer book - fractional book scaled to the integer book's daily "
    "dollar sd); the fractional book is the run's base series.",
    "Automation is UNCONFIRMED for every PropEd plan (lead ruling A11); Phidias is semi-automated "
    "only. No fee or payout model.",
]


def render(res):
    L = ["# Stage E.21 F8: descriptive economics (not part of any verdict)", "",
         "Produced by reports/stage_e21_briefs/econ/economics.py from the run's files "
         "(reports/stage_e21_runs/, read only), E.13 C2 (reports/stage_e13_trend_carry.md) and "
         "reports/stage_e21_proped_rules.json. Numbers: reports/stage_e21_economics.json. "
         "Verdicts are unchanged: " + ", ".join(f"{t} pass={v}" for t, v in
                                                 res["verdicts_unchanged"].items()) + ".", ""]
    L += ["## 1. Personal account: capital to hold every root at >= 1 contract at full signal", ""]
    for t in ["T1", "T2", "T3"]:
        T = res["tests"][t]
        P = T["personal"]
        L += [f"### {t} (sigma_b = {_pct(T['sigma_b'])}, S = {T['S_max_used']}, roots = "
              f"{len(T['roots'])}; fractional reconstruction max abs error "
              f"{T['fractional_recon_max_abs_err']:.1e})", ""]
        L += ["| tau | k = tau/sigma_b | K_min | binding root | roots rounding to 0 at $10K / $25K / "
              "$50K / $100K |", "|---|---|---|---|---|"]
        for tau in ["tau_15", "tau_25"]:
            x = P[tau]
            z = " / ".join(str(len(x["round_to_zero"][str(K)] if str(K) in x["round_to_zero"]
                                   else x["round_to_zero"][K])) for K in K_LEVELS)
            L.append(f"| {tau[4:]}% | {x['k']:.3f} | ${_f(x['K_min'])} | {x['binding']} "
                     f"({P[tau]['per_root'][x['binding']]['vehicle']}) | {z} |")
        sp = P["supp_with_grain_gas_micros"]
        L += ["", f"Supplementary (not the brief's book): with MNG/MZC/MZS/MZL for NG/ZC/ZS/ZL, "
              f"K_min = ${_f(sp['tau_15']['K_min'])} (15%) and ${_f(sp['tau_25']['K_min'])} (25%), "
              f"binding {sp['tau_15']['binding']}.", ""]
        L += ["| root | F8 vehicle | sigma$/yr | 15%: at K_min | $10K | $25K | $50K | $100K | "
              "25%: at K_min | $10K | $25K | $50K | $100K |", "|" + "---|" * 13]
        for r in T["roots"]:
            a = P["tau_15"]["per_root"][r]
            b = P["tau_25"]["per_root"][r]
            flag = " (FLAG full-size)" if F8[r][3] else ""
            cells = [f"{a['at_Kmin']:.2f}"] + [f"{a[f'at_{K}']:.2f}" for K in K_LEVELS] + \
                    [f"{b['at_Kmin']:.2f}"] + [f"{b[f'at_{K}']:.2f}" for K in K_LEVELS]
            L.append(f"| {r} | {a['vehicle']}{flag} | {_f(a['risk'])} | " + " | ".join(cells) + " |")
        L += ["", "Roots rounding to zero contracts (round-half-up of the fractional count above):", ""]
        for tau in ["tau_15", "tau_25"]:
            for K in K_LEVELS:
                zz = P[tau]["round_to_zero"]
                zz = zz.get(str(K), zz.get(K))
                L.append(f"- {tau[4:]}%, ${K:,}: {', '.join(zz) if zz else 'none'}")
        L.append("")
    L += ["### Cross-check against E.13 C3", "",
          "- C3 chooses which instruments to hold: the N lowest-risk instruments whose one contract is "
          "within 1.5x of the target, and floors every held position at 1 contract (max(1, round)). "
          "F8 here must hold the 17 fixed roots of the test (2 for T3), including the high-risk "
          "full-size LE ($14,666), NG ($13,183), ZL, ZS and the micros MNQ ($9,743) and MGC ($9,254), "
          "which C3 never holds even at $100K. So C3 holds 11-23 instruments at $10K-$100K while "
          "here T1/T2 need $323K-$691K before LE reaches one contract.",
          "- Per-instrument risk budget: C3 uses tau x IDM(N)/N with rho 0.125 (e.g. $2,692/yr at "
          "$100K, 25%, N 23); here it is k x K x 0.40 / S with k from the realized book "
          "volatility (T1 at $100K, 25%: 1.503 x 100,000 x 0.40 / 17 = $3,537/yr; T2 $4,544/yr; T3 "
          "$28,523/yr per root with S = 2). The orders of magnitude agree for T1/T2; the gap is the "
          "fixed universe, not the budget.",
          "- C3 is a separate construction (Carver-style, equal weights over cheap instruments); it "
          "is not the tested book, and its $10K-$100K portfolios would not reproduce T1/T2.", ""]
    L += ["## 2. The integer book at its smallest integer size (base case)", "",
          "| test | scale A (capital $ at unit leverage) | dates | daily mean $ | daily sd $ | 5-day sd $ "
          "(blocks) | annual mean $ | annual sd $ | gross $ | costs $ | TE daily $ (annual) | corr with "
          "fractional | max micro-equiv |", "|" + "---|" * 13]
    for t in ["T1", "T2", "T3"]:
        B = res["tests"][t]["integer_book"]
        L.append(f"| {t} | {_f(B['scale_A_capital_dollars_at_unit_leverage'])} | {B['n_dates']} | "
                 f"{_f(B['daily_mean'], 1)} | {_f(B['daily_sd'])} | {_f(B['five_day_sd'])} "
                 f"({B['five_day_blocks']}) | {_f(B['annual_mean'])} | {_f(B['annual_sd'])} | "
                 f"{_f(B['gross_total'])} | {_f(B['cost_total'])} | {_f(B['tracking_error_daily_sd'])} "
                 f"({_f(B['tracking_error_annual'])}) | {B['corr_with_fractional']:.4f} | "
                 f"{_f(B['max_micro_equivalent'])} |")
    L += ["", "No-weekend variant of the same book:", "",
          "| test | daily sd $ | 5-day sd $ | annual mean $ | dates zeroed | extra weekend fill costs $ |",
          "|---|---|---|---|---|---|"]
    for t in ["T1", "T2", "T3"]:
        N = res["tests"][t]["integer_book"]["no_weekend"]
        L.append(f"| {t} | {_f(N['daily_sd'])} | {_f(N['five_day_sd'])} | {_f(N['annual_mean'])} | "
                 f"{N['dates_after_weekend_zeroed']} | {_f(N['extra_weekend_fill_costs_total'])} |")
    L += ["", "Per root, largest |contracts| held (F8 vehicles) and nonzero rebalance targets that round "
          "to zero:", ""]
    for t in ["T1", "T2", "T3"]:
        pr = res["tests"][t]["integer_book"]["per_root"]
        L.append(f"- {t}: " + "; ".join(f"{r} {F8[r][0]} max {int(v['max_abs'])}, zero "
                                         f"{v['rebal_targets_rounding_to_zero']}" for r, v in pr.items()))
    L += ["", "### T4", ""]
    T4 = res["tests"]["T4"]
    L += [f"T4 is a combination in risk units and has no contract book. Realized volatility of its "
          f"base daily series: {T4['realized_vol_annual_risk_units']:.2f} risk units per year "
          f"({T4['n_dates']} dates). Observation for the lead (not interpreted here): the series has "
          f"{T4['n_days_abs_over_10']} days with |value| > 10 (max {T4['max_abs_daily']:.1f}; 99th "
          f"percentile of |value| {T4['p99_abs_daily']:.2f}); largest days "
          + ", ".join(f"{d} {v:.1f}" for d, v in T4["largest_days"])
          + f". Without those days the realized volatility is {T4['realized_vol_excl_abs_over_10']:.2f}.",
          ""]
    L += ["## 3. PropEd plans (automation UNCONFIRMED on every row) and Phidias Premium 50K", "",
          "Instruments: PropEd's list (Q32) has MNQ, M2K, MGC, MCL, NG, ZC, ZS, ZL, ZT, ZF, ZN, ZB "
          "and 6E; it does NOT list M6E, the micro yield futures, MTN, MWN, TN, UB, HE or LE. The "
          "list is not plan-specific. Phidias: instrument list UNSOURCED. Daily loss limit is "
          "UNSOURCED for every PropEd plan except One Plan ($11,250); Phidias has none.", ""]
    for t in ["T1", "T2", "T3"]:
        T = res["tests"][t]
        B = T["integer_book"]
        L += [f"### {t} (daily sd ${_f(B['daily_sd'])}, 5-day sd ${_f(B['five_day_sd'])}, max "
              f"micro-equivalent {_f(B['max_micro_equivalent'])})", "",
              "| plan | DD type | DD $ | DLL $ | max micros | share days over max | not listed | "
              "daily sd / DD | 5-day sd / DD | weekend add-on $ | breach with weekend (trailing / "
              "static) | breach no weekend (trailing / static) | 10% scale: m, with wknd tr/st, no wknd "
              "tr/st |", "|" + "---|" * 13]
        for p in T["proped"]:
            ww = p.get("with_weekend") or {}
            wo = p.get("without_weekend") or {}
            ten = p.get("ten_pct_scale")
            if isinstance(ten, dict):
                ts = (f"m={ten['multiple']}: {_pct(ten['with_weekend']['trailing_share'])} / "
                      f"{_pct(ten['with_weekend']['static_share'])}; "
                      f"{_pct(ten['without_weekend']['trailing_share'])} / "
                      f"{_pct(ten['without_weekend']['static_share'])}")
            else:
                ts = str(ten)
            nl = p["instruments_not_listed"]
            nl = ", ".join(nl) if isinstance(nl, list) else nl
            name = p["name"] + (" (comparison)" if p["comparison"] else "") + \
                (" [automation UNCONFIRMED]" if not p["comparison"] else " [semi-automated only]")
            L.append(f"| {name} | {_short(p['drawdown_type'], 45)} | {_f(p['drawdown_usd'])} | "
                     f"{_short(p['daily_loss_limit_usd'], 12) if p['daily_loss_limit_usd'] is not None else 'none'} | "
                     f"{p['max_micro_equiv']} | {_pct(p['share_days_over_max'])} | {nl or '-'} | "
                     f"{_f(p['daily_sd_over_dd'], 2)} | {_f(p['five_day_sd_over_dd'], 2)} | "
                     f"{_short(p['weekend_addon_price_usd'], 25) if p['weekend_addon_price_usd'] is not None else 'not needed / none listed'} | "
                     f"{_pct(ww.get('trailing_share'))} / {_pct(ww.get('static_share'))} | "
                     f"{_pct(wo.get('trailing_share'))} / {_pct(wo.get('static_share'))} | {ts} |")
        L.append("")
    L += ["Overnight: Standard, Instant and TrueRisk plans 'yes' (FAQ Q21, terms Q02); One Plan and "
          "Nexus X5: general FAQ statement only, plan not named (FLAG). Weekend holds: add-on for "
          "Standard/Instant/TrueRisk (TrueRisk Eval price UNSOURCED, 'available at checkout'); One Plan "
          "and Nexus X5 weekend terms UNSOURCED; Phidias allows weekends (JSON weekend_allowed true).",
          "", "## 4. Assumptions and flags", ""]
    L += [f"{i}. {a}" for i, a in enumerate(ASSUMPTIONS, 1)]
    L += ["", "FLAGS: full-size roots NG, ZC, ZS, ZL, HE, LE; micro-yield conversion by risk ratio "
          "(ZT, ZF, ZN, ZB); proportional micro cost scaling; C2 risk at 2026 levels; automation "
          "UNCONFIRMED (PropEd), semi-automated only (Phidias); PropEd drawdown trailing-or-static "
          "unresolved for Standard/Instant (EOD, trailing not stated) and TrueRisk (CONFLICT); "
          "daily loss limits UNSOURCED except One Plan; PropEd instrument list not plan-specific; "
          "Phidias instrument list and price UNSOURCED.", ""]
    return "\n".join(L)


if __name__ == "__main__":
    main()
