"""reports/stage_e22_microbook.md from the study's result dict (all descriptive, no p-value)."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from microbook.universe import MICROS, NOT_MODELLED, SENSITIVITY

METHOD_NAMES = {"unrounded": "unrounded (reference)", "simple": "simple (rounded + buffered)",
                "greedy": "greedy (Nov 2021, shrink 0.5)"}


def f(x: Any, nd: int = 2) -> str:
    if x is None:
        return "n/a"
    if isinstance(x, str):
        return x
    if isinstance(x, (int,)) and not isinstance(x, bool):
        return f"{x:,}"
    return f"{x:,.{nd}f}"


def table(head: Sequence[str], rows: Sequence[Sequence[Any]]) -> list[str]:
    out = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    out += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return out + [""]


def _rows_by_cap(res: Mapping) -> list[tuple[str, Mapping]]:
    out = []
    for cap in ("10000", "25000", "50000"):
        for m in ("unrounded", "simple", "greedy"):
            out.append((f"${int(cap):,} {METHOD_NAMES[m]}", res["main"][cap][m]))
        if cap == "25000":
            for m in ("unrounded", "simple", "greedy"):
                out.append((f"$25,000 WITHOUT yield proxies, {METHOD_NAMES[m]}",
                            res["sensitivities_25k"]["without_yield_proxies"]["rows"][m]))
    return out


def _flatten(cfg: Mapping, prefix: str = "") -> list[tuple[str, Any, str]]:
    out = []
    for k, val in cfg.items():
        key = f"{prefix}{k}"
        if isinstance(val, Mapping) and "value" in val and "source" in val:
            out.append((key, val["value"], val["source"]))
        elif isinstance(val, Mapping) and k not in ("instruments",):
            out += _flatten(val, key + ".")
    return out


def write_report(res: Mapping, cfg: Mapping, path: Path) -> None:
    L: list[str] = ["# Stage E.22 Part B: the micro trend book, design study (B2-B3)", "",
                    f"**{res['sentence']}** No p-value is computed anywhere in this study.", "",
                    "Lead rulings applied (2026-10-16): S8 B-R1..B-R5; R-B6 the main greedy uses the 0.5 "
                    "correlation shrink (the November 2021 post states shrinking without a value; B-R5 takes "
                    "the code's 0.5), the no-shrink greedy is a sensitivity row; R-B7 E22-F1 rounds with the "
                    "SIMPLE method (rounded and buffered): forward/config_f1.json rounding_method = simple, the "
                    "greedy stays in forward/core.py as the study's comparison method, not used by E22-F1.", "",
                    f"Run {res['started_local']} .. {res['finished_local']} (microbook.run study). "
                    "Spec: reports/stage_e22_briefs/lead_spec_B.md (S1-S8). Code: microbook/, forward/core.py. "
                    "Machine-readable: reports/stage_e22_microbook.json. Constants: forward/config_f1.json.", ""]
    # S1 universe
    L += ["## 1. Universe (S1)", "", res["sentence"], ""]
    rows = []
    for m in MICROS:
        ins = next(r for r in res["instruments"] if r["micro"] == m.code)
        rows.append([m.code, m.exposure, ins["path"], f"{m.multiplier:g} {ins['multiplier_units']}",
                     f"{m.tick:g} / ${m.tick_value:.2f}", m.cost_basis, f"{ins['data_first']}..{ins['last']}",
                     "modelled"])
    for c, why in NOT_MODELLED.items():
        rows.append([c, "", "", "", "", "", "", f"not modelled: {why}"])
    for m in SENSITIVITY:
        rows.append([m.code, m.exposure, m.root, f"{m.multiplier:g}", f"{m.tick:g} / ${m.tick_value:.4g}",
                     m.cost_basis, "", "sensitivity only ($25K, in place of 10Y/30Y)"])
    L += table(["Micro", "Exposure", "Owned path", "Multiplier", "Tick", "Costs", "Data", "Status"], rows)
    L += ["Specs: E.13 T-28 (AMP contract specifications; quotes per row in forward/config_f1.json and "
          "microbook/universe.py). Costs 'frozen' = base_rules' D8 vehicle tables (settlement bucket, base); "
          "'extension' = FLAGGED S6 D8 extension (commission per side + 1 tick per side). Yield-micro and "
          "micro-grain commissions are UNSOURCED (declared $1.92 RT, the largest frozen micro figure). "
          "Yield-proxy durations ZT 1.9, ZN 6.5, ZB 15.0 are a declared approximation, UNSOURCED.", ""]
    # constants
    L += ["## 2. Constants (S3, S4, S8)", ""]
    L += table(["Constant", "Value", "Source"],
               [[k, (f(v, 6) if isinstance(v, float) else str(v))[:120], s] for k, v, s in _flatten(cfg)
                if k not in ("fdm.correlation", "idm.correlation")])
    est = res["estimates"]
    fm = res["forecast_means"]
    L += ["## 3. Estimates (frozen for E22-F1)", "",
          f"- FDM = {est['fdm']:.4f} (pooled weekly forecast correlation, {est['fdm_weeks_pooled']:,} "
          "instrument-weeks, floored at 0, cap 2.5).",
          f"- IDM (12 instruments) = {est['idm']:.4f}; mean IDM over the series span with the live sub-matrix "
          f"= {res['idm_mean_over_span_live_submatrix']:.4f}.",
          "- FDM correlation (8/32, 16/64, 32/128, 64/256): "
          + "; ".join("[" + ", ".join(f"{x:.2f}" for x in r) + "]" for r in est["fdm_corr"]), ""]
    L += table(["Speed", "Mean |scaled capped forecast| (pooled, live days)", "Target"],
               [[k, f(v), "10"] for k, v in fm["pooled_mean_abs"].items()])
    L += ["IDM correlation (weekly subsystem returns, before flooring):", ""]
    codes = est["idm_codes"]
    L += table([""] + codes, [[c] + [f"{x:.2f}" for x in r] for c, r in zip(codes, est["idm_corr"])])
    # main table
    L += ["## 4. Returns by capital and method (S5)", "", res["sentence"], "",
          "Daily net $ P&L series from the first fill of the unrounded book "
          f"({res['main']['25000']['unrounded']['first']}) to {res['main']['25000']['unrounded']['last']}; "
          "annualised x252 (mean) and x sqrt(252) (sd, Sharpe). Fixed capital, no compounding. "
          "Stress = 2 x slippage (S6).", ""]
    L += table(["Book", "Mean $/yr", "Sd $/yr", "Mean %", "Sd % (target 20)", "SR gross", "SR net",
                "SR net stress", "Net SR loss vs unrounded", "Corr with unrounded"],
               [[n, f(r["annual_mean_usd"], 0), f(r["annual_sd_usd"], 0), f(r["annual_mean_pct"], 1),
                 f(r["annual_sd_pct"], 1), f(r["sharpe_gross"]), f(r["sharpe_net"]),
                 f(r["sharpe_net_stress_2x_slip"]), f(r["sharpe_net_loss_vs_unrounded"]),
                 f(r["corr_net_with_unrounded"])] for n, r in _rows_by_cap(res)])
    L += ["## 5. Turnover and costs (S5, S6)", "", res["sentence"], ""]
    L += table(["Book", "Contracts traded/yr", "Roll fills/yr", "Round turns/yr", "Cost $/yr",
                "Cost % of capital", "Cost (SR units)", "Cost $/yr stress"],
               [[n, f(r["trade_contracts_per_year"], 0), f(r["roll_fills_per_year"], 0),
                 f(r["round_turns_per_year"], 0), f(r["cost_usd_per_year"], 0),
                 f(r["cost_pct_capital"], 2), f(r["cost_sharpe_units"], 3),
                 f(r["cost_usd_per_year_stress"], 0)] for n, r in _rows_by_cap(res)])
    L += ["## 6. Drawdowns (S5)", "", res["sentence"], "",
          "Bootstrap: circular blocks of 21 days, 10,000 resamples of 252 days, seed 20261016 (a fresh "
          "generator per series); expected = mean, worst = 95th percentile, also the 99th.", ""]
    L += table(["Book", "Realized max DD $", "% of capital", "Peak .. trough", "Exp. 1y max DD $",
                "p95 $", "p99 $", "Exp. %", "p95 %", "p99 %"],
               [[n, f(r["max_dd_usd"], 0), f(r["max_dd_pct"], 1), f"{r['max_dd_peak']} .. {r['max_dd_trough']}",
                 f(r.get("boot_1y_mdd_usd", {}).get("expected"), 0), f(r.get("boot_1y_mdd_usd", {}).get("p95"), 0),
                 f(r.get("boot_1y_mdd_usd", {}).get("p99"), 0), f(r.get("boot_1y_mdd_pct", {}).get("expected"), 1),
                 f(r.get("boot_1y_mdd_pct", {}).get("p95"), 1), f(r.get("boot_1y_mdd_pct", {}).get("p99"), 1)]
                for n, r in _rows_by_cap(res)])
    L += ["## 7. Instruments at zero and margin (S5)", "", res["sentence"], "",
          f"Margin: {res['margins_source']} (IBKR overnight initial per contract, as fetched in 2026, "
          "applied to every date: a present-day rate on historical positions; since sizing gives more "
          "contracts when prices are lower, the early years' margin is biased upward, notably for MNQ and MGC). "
          "The unrounded book's margin uses fractional contracts.", ""]
    mrows = []
    for n, r in _rows_by_cap(res):
        mg = r["margin"]
        if isinstance(mg, str):
            mrows.append([n, f(r["zero_share_mean"]), mg, "", "", "", ""])
        else:
            mrows.append([n, f(r["zero_share_mean"]), f(mg["mean_usd"], 0), f(mg["p95_usd"], 0),
                          f(mg["max_usd"], 0), f"{mg['mean_pct']:.1f} / {mg['p95_pct']:.1f} / {mg['max_pct']:.1f}",
                          ", ".join(mg["not_sourced"]) or "none"])
    L += table(["Book", "Mean share of live instruments at 0", "Margin mean $", "p95 $", "max $",
                "% of capital (mean/p95/max)", "Margin not sourced"], mrows)
    # sweep
    L += ["## 8. Capital sweep: Sharpe loss against unrounded (S5)", "", res["sentence"], ""]
    srows = []
    for cap in sorted(res["main"], key=lambda x: int(x)):
        rr = res["main"][cap]
        srows.append([f"${int(cap):,}", f(rr["unrounded"]["sharpe_net"]), f(rr["simple"]["sharpe_net"]),
                      f(rr["greedy"]["sharpe_net"]), f(rr["simple"]["sharpe_net_loss_vs_unrounded"]),
                      f(rr["greedy"]["sharpe_net_loss_vs_unrounded"]), f(rr["simple"]["zero_share_mean"]),
                      f(rr["greedy"]["zero_share_mean"])])
    L += table(["Capital", "SR net unrounded", "SR net simple", "SR net greedy", "Loss simple",
                "Loss greedy", "Zero share simple", "Zero share greedy"], srows)
    # per instrument
    L += ["## 9. Per instrument (S5)", "", res["sentence"], "",
          "Cost per round turn: mean over live days of buy + sell per-side cost (base). In Sharpe units: "
          "cost per round turn / median annual $ vol per contract; Carver's 0.01 SR test reported, not applied "
          "(E.13 T-18). Minimum capital: Carver's formula 4 contracts x $ vol / (tau x IDM x weight) (E.13 "
          "Part B, T-25), with ours (tau 0.20, the study IDM, w = 1/12) and with his report's assumptions "
          "(25%, IDM 2.5, w 0.04), at the median $ vol.", ""]
    L += table(["Micro", "Path", "Live from", "Multiplier", "Cost/RT $", "Cost/RT SR", "0.01 test",
                "Median $ vol/contract", "Min capital (ours)", "Min capital (his assumptions)", "Mean |F|"],
               [[r["micro"], r["path"], r["live_first"], f"{r['multiplier']:g}", f(r["cost_rt_usd"]),
                 f(r["cost_rt_sharpe_units"], 4), r["carver_0_01_test"], f(r["dollar_vol_median"], 0),
                 f(r["carver_min_capital_ours"], 0), f(r["carver_min_capital_his_assumptions"], 0),
                 f(r["mean_abs_forecast"])] for r in res["instruments"]])
    head = ["Micro"] + [f"${int(c) // 1000}K {m}" for c in ("10000", "25000", "50000")
                        for m in ("simple", "greedy")]
    zrows = []
    for m in MICROS:
        zrows.append([m.code] + [f(res["main"][c][meth]["pct_days_at_zero"].get(m.code), 1)
                                 for c in ("10000", "25000", "50000") for meth in ("simple", "greedy")])
    L += ["Per instrument: % of live days held at zero (unrounded: never zero by construction).", ""]
    L += table(head, zrows)
    crow = []
    for m in MICROS:
        crow.append([m.code] + [f(res["main"][c][meth]["net_usd_per_year_by_instrument"].get(m.code), 0)
                                for c in ("10000", "25000", "50000") for meth in ("unrounded", "simple", "greedy")])
    L += ["Per instrument: net $ per year.", ""]
    L += table(["Micro"] + [f"${int(c) // 1000}K {m}" for c in ("10000", "25000", "50000")
                            for m in ("unrounded", "simple", "greedy")], crow)
    # sensitivities
    sens = res["sensitivities_25k"]
    L += ["## 10. Sensitivities at $25,000 (S5)", "", res["sentence"], ""]
    srows = []
    for key, label in (("without_yield_proxies", "without the yield proxies (9 instruments)"),
                       ("book_scalars_fdm_idm_held", "book forecast scalars 5.3/3.75/2.65/1.87 (FDM, IDM held)"),
                       ("mtn_mwn_for_10y_30y", "MTN/MWN on TN/UB in place of 10Y/30Y")):
        if key not in sens:
            srows.append([label, "not run", "", "", "", ""])
            continue
        rr = sens[key]["rows"]
        for m in ("unrounded", "simple", "greedy"):
            r = rr[m]
            srows.append([label, m, f(r["sharpe_net"]), f(r["annual_sd_pct"], 1),
                          f(r["sharpe_net_loss_vs_unrounded"]), f(r["cost_usd_per_year"], 0)])
    if "greedy_no_shrink" in sens:
        for cap, rr in sorted(sens["greedy_no_shrink"]["rows_by_capital"].items(), key=lambda x: int(x[0])):
            r = rr["greedy"]
            srows.append([f"greedy WITHOUT the 0.5 correlation shrink at ${int(cap):,}", "greedy",
                          f(r["sharpe_net"]), f(r["annual_sd_pct"], 1), f(r["sharpe_net_loss_vs_unrounded"]),
                          f(r["cost_usd_per_year"], 0)])
    L += table(["Sensitivity", "Method", "SR net", "Sd %", "Loss vs unrounded", "Cost $/yr"], srows)
    L += ["Shrink: lead ruling R-B6 (P-NOV21 .txt:153 states shrinking the correlation matrix without a "
          "value; B-R5 takes the code's 0.5): the main greedy rows use the 0.5 shrink; the rows above show "
          "the greedy without it.", ""]
    diag = res.get("greedy_te_diagnostic")
    if diag:
        L += ["## 10b. Diagnostic: the greedy's tracking error against plain rounding", "",
              "Every 7th decision date: the greedy integer solution from zero with shadow cost 0 (no buffer) "
              "versus rounding each unrounded position half away from zero, tracking error to the unrounded "
              "optimum under the same covariance. The greedy steps one contract at a time in the sign of each "
              "optimum and cannot step back, so with highly correlated instruments (10Y/30Y about 0.9) it can "
              "overshoot one and leave the other short.", ""]
        L += table(["Capital", "Dates", "Share greedy TE > rounding TE", "Median TE ratio greedy/rounding",
                    "p90 ratio"],
                   [[f"${int(c):,}", d["dates"], f(d["share_greedy_te_above_rounding"]), f(d["median_ratio"]),
                     f(d["p90_ratio"])] for c, d in sorted(diag.items(), key=lambda x: int(x[0]))])
    # greedy counters
    L += ["## 11. Optimiser and data counters", ""]
    grow = []
    for cap in sorted(res["main"], key=lambda x: int(x)):
        c = res["main"][cap]["greedy"]["counters"]
        grow.append([f"${int(cap):,}"] + [c.get(k, 0) for k in (
            "decision dates", "greedy inside buffer", "greedy no trade (integer optimum = current)",
            "greedy no trade (x <= buffer)", "greedy no trade (trades round to 0)", "greedy traded",
            "greedy all-zero integer result")])
    L += ["Greedy steps per decision date (main greedy, 0.5 correlation shrink). Step 3's x (tracking "
          "error of the current against the integer-optimised positions) and the buffer b = 0.0125 are both "
          "annualised tracking-error standard deviations as a fraction of capital (weights = contracts x "
          "multiplier x price / capital, covariance of annualised percentage returns; pinned by "
          "tests/test_forward_core_rounding.py). An adjustment of 0 almost always means x = 0: at small capital "
          "one contract is several % of tracking error, so step 1 rarely holds, and the shadow-cost penalty "
          "(250 x per-side cost / capital per contract traded) makes the current positions the greedy's best "
          "integer portfolio on most days.", ""]
    L += table(["Capital", "Decision dates", "Inside buffer (step 1)", "x = 0: integer optimum = current",
                "0 < x <= b", "Trades round to 0", "Traded", "All-zero integer result"], grow)
    drows = []
    for code, n in res["data_notes"].items():
        cc = n["cache_counters"]
        drows.append([code, n["root"], cc.get("marks"), cc.get("rolls"),
                      cc.get("listed window dates without a mark (dropped)"),
                      cc.get("splices removed by merging (no bar between)"),
                      cc.get("store boundary interval chained"),
                      n.get("undefined moves (failed intervals, P&L 0)")])
    L += table(["Micro", "Path", "Marks", "Rolls", "Listed dates without a mark (dropped)",
                "Splices removed (no bar between)", "Store boundary chained", "Undefined moves"], drows)
    L += [f"Series grid: {res['grid_days']:,} dates ({res['grid_days_per_year']:.1f} per calendar year; "
          "the union of the 12 paths' mark dates).", "", res["sentence"], ""]
    path.write_text("\n".join(L) + "\n", encoding="utf-8")


__all__ = ["write_report"]
