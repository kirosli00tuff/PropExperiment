"""The design study (lead_spec_B.md S5): estimates, books per capital level and method, the
statistics and the report. Books are saved under reports/stage_e22_microbook/books/ with a
fingerprint (rerun skips them); the instrument-return correlations likewise.
"""

from __future__ import annotations

import hashlib
import json
import math
from collections.abc import Mapping, Sequence
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

from forward import core
from microbook import book as B
from microbook import stats as S
from microbook.config_build import SCALARS_BOOK, build_config, build_tables, extension_cost_row
from microbook.universe import (
    DURATION_NOTE,
    MICROS,
    NOT_MODELLED,
    SENSITIVITY,
    YIELD_CODES,
    Micro,
)

SENTENCE = ("These figures re-use data E.21 already read (2010-07..2024-02); they are a design study "
            "and not evidence of edge.")
CAPITALS_MAIN = (10_000, 25_000, 50_000)
CAPITALS_SWEEP = (10_000, 15_000, 25_000, 35_000, 50_000, 75_000, 100_000, 250_000)
SENS_CAPITAL = 25_000
CONFIG_PATH = Path("forward/config_f1.json")


def now_local() -> str:
    return datetime.now(ZoneInfo("America/Vancouver")).isoformat(timespec="seconds")


def fingerprint(obj: Any) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, default=str).encode()).hexdigest()[:16]


# ------------------------------------------------------------------ inputs ----
def load_instruments(cache_dir: Path, micros: Sequence[Micro], cfg: Mapping
                     ) -> tuple[list[B.Instrument], dict]:
    insts, notes = [], {}
    for m in micros:
        frame = pd.read_parquet(cache_dir / f"{m.root}.parquet")
        meta = json.loads((cache_dir / f"{m.root}.json").read_text(encoding="utf-8"))
        ins, n = B.prepare(m, frame, cfg)
        insts.append(ins)
        notes[m.code] = {"root": m.root, "cache_counters": meta["counters"], **n}
    return insts, notes


def cost_rows(insts: Sequence[B.Instrument]) -> dict[str, dict]:
    """The forward per-side cost table: frozen micros at their latest mark's settlement bucket
    (base, mean of the two sides); the others by the S6 extension."""
    out = {}
    for ins in insts:
        m = ins.micro
        if m.cost_basis == "frozen":
            last = ins.frame.iloc[-1]
            usd = 0.5 * (float(last["cost_buy"]) + float(last["cost_sell"])) / 100.0
            out[m.code] = {"per_side_usd": usd, "source": (
                f"frozen D8 (base_rules.costs.vehicle_cost, reports/stage_e2a_costs.json) at the "
                f"settlement bucket of {ins.frame.index[-1].date()}, base case, mean of buy and sell")}
        else:
            out[m.code] = extension_cost_row(m)
    return out


# ------------------------------------------------------------------ estimates ----
def estimate_all(insts: list[B.Instrument], cfg: Mapping, fdm: float | None = None
                 ) -> dict[str, Any]:
    est: dict[str, Any] = {}
    if fdm is None:
        fdm, fcorr, weeks = B.estimate_fdm(insts, cfg)
        est.update({"fdm": fdm, "fdm_corr": fcorr.tolist(), "fdm_weeks_pooled": weeks})
    else:
        est["fdm"] = fdm
    for ins in insts:
        B.add_combined(ins, cfg, est["fdm"])
    idm, icorr, codes = B.estimate_idm(insts, cfg)
    est.update({"idm": idm, "idm_corr": icorr.tolist(), "idm_codes": codes})
    return est


def forecast_means(insts: Sequence[B.Instrument], cfg: Mapping) -> dict[str, Any]:
    cols = B.speed_columns(cfg)
    live = pd.concat([i.frame.loc[i.frame["live"], cols + ["F"]] for i in insts])
    pooled = {c[3:]: float(live[c].abs().mean()) for c in cols}
    pooled["combined"] = float(live["F"].abs().mean())
    per = {i.micro.code: float(i.frame.loc[i.frame["live"], "F"].abs().mean()) for i in insts}
    return {"pooled_mean_abs": pooled, "per_instrument_mean_abs_combined": per,
            "target": 10.0}


# ------------------------------------------------------------------ books ----
def cached_corr(grid: B.Grid, cfg: Mapping, out_dir: Path, tag: str) -> np.ndarray:
    fp = fingerprint({"codes": grid.codes, "n": len(grid.dates), "first": str(grid.dates[0]),
                      "last": str(grid.dates[-1]), "corr": cfg["greedy"]["correlation"],
                      "ret": float(np.nansum(grid.ret_cum[-1]))})
    path = out_dir / "books" / f"corr_{tag}_{fp}.npy"
    if path.is_file():
        return np.load(path)
    corr = B.correlations(grid, cfg)
    path.parent.mkdir(parents=True, exist_ok=True)
    np.save(path, corr)
    return corr


def cached_run(grid: B.Grid, cfg: Mapping, method: str, capital: float, idm_t: np.ndarray,
               corr_t: np.ndarray | None, out_dir: Path, tag: str) -> B.BookRun:
    fp = fingerprint({"cfg": {k: cfg[k] for k in ("ewmac", "forecast_cap", "vol", "vol_target",
                                                  "simple_rounding", "greedy", "warmup_diffs")},
                      "codes": grid.codes, "F": float(np.nansum(grid.F)),
                      "V": float(np.nansum(grid.V)), "idm": float(idm_t.sum()),
                      "n": len(grid.dates), "method": method, "capital": capital})
    path = out_dir / "books" / f"{tag}_{method}_{int(capital)}_{fp}.npz"
    if path.is_file():
        z = np.load(path, allow_pickle=False)
        return B.BookRun(method, capital, z["targets"], z["pos"], z["nstar"],
                         json.loads(str(z["counters"])))
    run = B.simulate(grid, cfg, method, capital, idm_t, corr_t)
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(path, targets=run.targets, pos=run.pos, nstar=run.nstar,
                        counters=json.dumps(run.counters))
    return run


def span_start(grid: B.Grid, ref: B.BookRun) -> int:
    nz = np.flatnonzero(np.any(ref.pos != 0, axis=1))
    return int(nz[0]) if len(nz) else 0


def summarize(grid: B.Grid, run: B.BookRun, start: int, ref_net: np.ndarray | None,
              margins: Mapping[str, float] | None, *, boot: bool) -> dict[str, Any]:
    cap = run.capital
    base = B.pnl(grid, run)
    stress = B.pnl(grid, run, slip_mult=2.0)
    sl = slice(start, None)
    dates = grid.dates[sl]
    gross = base["gross"][sl].sum(axis=1)
    cost = (base["trade_cost"] + base["roll_cost"])[sl].sum(axis=1)
    cost_st = (stress["trade_cost"] + stress["roll_cost"])[sl].sum(axis=1)
    net, net_st = gross - cost, gross - cost_st
    years = (dates[-1] - dates[0]).days / 365.25
    am, asd = S.annual(net)
    trades = np.abs(base["trade"][sl]).sum()
    roll_fills = (np.abs(base["held"][sl]) * 2.0 * grid.n_rolls[sl]).sum()
    dd = S.max_drawdown(net, dates)
    pos = run.pos[sl]
    live = grid.live[sl]
    zero = (pos == 0) & live
    with np.errstate(invalid="ignore"):
        zero_share = float(np.nanmean(zero.sum(axis=1) / np.where(live.sum(axis=1) > 0,
                                                                 live.sum(axis=1), np.nan)))
    out: dict[str, Any] = {
        "method": run.method, "capital": cap, "first": str(dates[0].date()),
        "last": str(dates[-1].date()), "days": int(len(dates)), "years": years,
        "annual_mean_usd": am, "annual_sd_usd": asd, "annual_mean_pct": 100 * am / cap,
        "annual_sd_pct": 100 * asd / cap, "sharpe_gross": S.sharpe(gross),
        "sharpe_net": S.sharpe(net), "sharpe_net_stress_2x_slip": S.sharpe(net_st),
        "corr_net_with_unrounded": (None if ref_net is None else
                                    float(np.corrcoef(net, ref_net)[0, 1])),
        "trade_contracts_per_year": float(trades / years),
        "roll_fills_per_year": float(roll_fills / years),
        "round_turns_per_year": float((trades + roll_fills) / 2.0 / years),
        "cost_usd_per_year": float(cost.sum() / years),
        "cost_usd_per_year_stress": float(cost_st.sum() / years),
        "cost_pct_capital": float(100 * cost.sum() / years / cap),
        "cost_sharpe_units": (None if S.sharpe(gross) is None or S.sharpe(net) is None
                              else S.sharpe(gross) - S.sharpe(net)),
        "max_dd_usd": dd["max_dd"], "max_dd_pct": 100 * dd["max_dd"] / cap,
        "max_dd_peak": dd["peak_date"], "max_dd_trough": dd["trough_date"],
        "zero_share_mean": zero_share,
        "pct_days_at_zero": {c: float(100 * zero[:, k].sum() / max(live[:, k].sum(), 1))
                             for k, c in enumerate(grid.codes)},
        "mean_abs_contracts": {c: float(np.abs(pos[live[:, k], k]).mean()) if live[:, k].any()
                               else None for k, c in enumerate(grid.codes)},
        "net_usd_per_year_by_instrument": {
            c: float(((base["gross"] - base["trade_cost"] - base["roll_cost"])[sl, k]).sum()
                     / years) for k, c in enumerate(grid.codes)},
        "counters": run.counters,
        "_net": net,
    }
    if boot:
        mdd = S.block_bootstrap_mdd(net)
        bs = S.bootstrap_summary(mdd)
        out["boot_1y_mdd_usd"] = bs
        out["boot_1y_mdd_pct"] = {k: 100 * val / cap for k, val in bs.items()}
    if margins is not None:
        rate = np.array([margins.get(c, np.nan) for c in grid.codes])
        known = ~np.isnan(rate)
        m = (np.abs(pos[:, known]) * rate[known][None, :]).sum(axis=1)
        out["margin"] = {"mean_usd": float(m.mean()), "p95_usd": float(np.percentile(m, 95)),
                         "max_usd": float(m.max()), "mean_pct": float(100 * m.mean() / cap),
                         "p95_pct": float(100 * np.percentile(m, 95) / cap),
                         "max_pct": float(100 * m.max() / cap),
                         "not_sourced": [c for c, k in zip(grid.codes, known) if not k]}
    else:
        out["margin"] = "margin not sourced"
    return out


def run_set(insts: list[B.Instrument], cfg: Mapping, idm_corr: np.ndarray, capitals: Sequence[int],
            out_dir: Path, tag: str, margins: Mapping[str, float] | None, *,
            boot_caps: Sequence[int] = (), corr_t: np.ndarray | None = None
            ) -> tuple[dict, B.Grid]:
    grid = B.build_grid(insts)
    if corr_t is None:
        corr_t = cached_corr(grid, cfg, out_dir, tag)
    idm_t = B.idm_series(grid, np.asarray(idm_corr), cfg["idm"]["dm_max"]["value"])
    res: dict = {}
    for cap in capitals:
        runs = {m: cached_run(grid, cfg, m, cap, idm_t, corr_t if m == "greedy" else None,
                              out_dir, tag) for m in B.METHODS}
        start = span_start(grid, runs["unrounded"])
        ref = summarize(grid, runs["unrounded"], start, None, margins, boot=cap in boot_caps)
        rows = {"unrounded": ref}
        for m in ("simple", "greedy"):
            rows[m] = summarize(grid, runs[m], start, ref["_net"], margins, boot=cap in boot_caps)
        for m, r in rows.items():
            r["sharpe_net_loss_vs_unrounded"] = (None if r["sharpe_net"] is None else
                                                 ref["sharpe_net"] - r["sharpe_net"])
        ref["corr_net_with_unrounded"] = 1.0
        res[cap] = rows
        print(f"{now_local()} {tag} ${cap:,}: " + ", ".join(
            f"{m} SR {r['sharpe_net']:.2f}" for m, r in rows.items()), flush=True)
    res["_idm_mean"] = float(idm_t[span_start(grid, cached_run(grid, cfg, 'unrounded', capitals[0],
                                                                idm_t, None, out_dir, tag)):].mean())
    return res, grid


def greedy_te_diagnostic(grid: B.Grid, cfg: Mapping, out_dir: Path, capitals: Sequence[int],
                         every: int = 7) -> dict:
    """Diagnostic (not a S5 table): on every ``every``-th decision date after the series start,
    the greedy integer solution from zero with shadow cost 0 against the unrounded optimum, its
    tracking error versus that of rounding each position half away from zero, same covariance."""
    corr_t = cached_corr(grid, cfg, out_dir, "main")
    idm_t = B.idm_series(grid, np.asarray(cfg["idm"]["correlation"]), cfg["idm"]["dm_max"]["value"])
    out = {}
    for cap in capitals:
        ref = cached_run(grid, cfg, "unrounded", cap, idm_t, None, out_dir, "main")
        worse, ratios = 0, []
        for t in range(span_start(grid, ref), len(grid.dates), every):
            idx = np.flatnonzero(grid.has_mark[t] & grid.live[t])
            if not len(idx):
                continue
            opt = ref.targets[t, idx]
            cov = core.covariance(corr_t[t][np.ix_(idx, idx)], grid.V[t, idx])
            g = core.greedy_integer(opt, np.zeros(len(idx)), cov, np.zeros(len(idx)), cap, 0.0)
            te_g = core.tracking_error(g.positions - opt, cov, cap)
            te_r = core.tracking_error(core.round_half_away(opt) - opt, cov, cap)
            worse += int(te_g > te_r + 1e-12)
            if te_r > 0:
                ratios.append(te_g / te_r)
        out[cap] = {"dates": len(ratios), "share_greedy_te_above_rounding": worse / max(len(ratios), 1),
                    "median_ratio": float(np.median(ratios)), "p90_ratio": float(np.percentile(ratios, 90))}
    return out


def instrument_rows(insts: Sequence[B.Instrument], cfg: Mapping, idm: float) -> list[dict]:
    rows = []
    n = len(insts)
    tau = cfg["vol_target"]["value"]
    for ins in insts:
        f = ins.frame
        lv = f.loc[f["live"]]
        v_med = float(lv["V"].median())
        rt = float(((lv["cost_buy"] + lv["cost_sell"]) / 100.0).mean())
        m = ins.micro
        rows.append({
            "micro": m.code, "path": m.root + (f" (yield proxy, D {m.duration}, {DURATION_NOTE})"
                                               if m.yield_proxy else ""),
            "data_first": str(f.index[0].date()), "live_first": str(lv.index[0].date()),
            "last": str(f.index[-1].date()), "multiplier": m.multiplier,
            "multiplier_units": "USD per bp" if m.yield_proxy else "USD per price unit",
            "spec_source": m.spec_source, "cost_basis": m.cost_basis,
            "cost_rt_usd": rt, "dollar_vol_median": v_med,
            "cost_rt_sharpe_units": rt / v_med, "carver_0_01_test": "pass" if rt / v_med <= 0.01 else "fail",
            "carver_min_capital_ours": 4.0 * v_med / (tau * idm * (1.0 / n)),
            "carver_min_capital_his_assumptions": 4.0 * v_med / (0.25 * 2.5 * 0.04),
            "mean_abs_forecast": float(lv["F"].abs().mean()),
        })
    return rows


# ------------------------------------------------------------------ the study ----
def load_margins(path: Path) -> dict[str, float] | None:
    if not path.is_file():
        return None
    d = json.loads(path.read_text(encoding="utf-8"))
    return {k: float(r["initial"]) for k, r in d.get("rates", {}).items()
            if isinstance(r, dict) and r.get("initial") is not None}


def strip(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {str(k): strip(v) for k, v in obj.items() if not str(k).startswith("_")}
    if isinstance(obj, (list, tuple)):
        return [strip(v) for v in obj]
    if isinstance(obj, (np.floating, np.integer)):
        return obj.item()
    return obj


def run_study(*, out_dir: Path, cache_dir: Path, report_md: Path, report_json: Path,
              margins_json: Path, with_sensitivity: bool = True,
              config_path: Path | None = None) -> dict:
    from base_rules import constants as BK

    t0 = now_local()
    margins = load_margins(margins_json)
    cfg0 = build_config(fdm=1.0, fdm_corr=None, idm=None, idm_corr=None, idm_codes=None,
                        cost_rows={m.code: {"per_side_usd": None, "source": ""} for m in MICROS})
    insts, notes = load_instruments(cache_dir, MICROS, cfg0)
    est = estimate_all(insts, cfg0)
    rows_cost = cost_rows(insts)
    cfg = build_config(fdm=est["fdm"], fdm_corr=est["fdm_corr"], idm=est["idm"],
                       idm_corr=est["idm_corr"], idm_codes=est["idm_codes"], cost_rows=rows_cost,
                       study_note=("FDM and IDM estimated by microbook.run study on the 12 study paths "
                                   "2010-07..2024-02 (yield micros on the ZT/ZN/ZB yield proxy); " + SENTENCE))
    cfg_path = config_path or BK.repo_path(CONFIG_PATH)
    cfg_path.write_text(json.dumps(cfg, indent=1) + "\n", encoding="utf-8")
    cfg_path.with_name("tables_f1.json").write_text(json.dumps(build_tables(cfg), indent=1) + "\n",
                                                     encoding="utf-8")
    fmeans = forecast_means(insts, cfg)
    print(f"{now_local()} FDM {est['fdm']:.4f} IDM {est['idm']:.4f}", flush=True)
    caps = sorted(set(CAPITALS_MAIN) | set(CAPITALS_SWEEP))
    main, grid = run_set(insts, cfg, np.asarray(est["idm_corr"]), caps, out_dir, "main", margins,
                         boot_caps=CAPITALS_MAIN)
    result: dict[str, Any] = {
        "schema": "stage_e22_microbook/1", "sentence": SENTENCE, "started_local": t0,
        "estimates": {k: est[k] for k in ("fdm", "fdm_corr", "fdm_weeks_pooled", "idm", "idm_corr",
                                          "idm_codes")},
        "idm_mean_over_span_live_submatrix": main.pop("_idm_mean"),
        "forecast_means": fmeans, "main": main,
        "instruments": instrument_rows(insts, cfg, est["idm"]),
        "data_notes": notes, "grid_days": len(grid.dates),
        "grid_days_per_year": len(grid.dates) / ((grid.dates[-1] - grid.dates[0]).days / 365.25),
        "margins_source": str(margins_json) if margins is not None else "margin not sourced",
    }
    sens: dict[str, Any] = {}
    # without the three yield proxies (every table shows it at $25K)
    keep = [i for i in insts if i.micro.code not in YIELD_CODES]
    idx = [est["idm_codes"].index(i.micro.code) for i in keep]
    sub = np.asarray(est["idm_corr"])[np.ix_(idx, idx)]
    nr, _ = run_set(keep, cfg, sub, [SENS_CAPITAL], out_dir, "noyield", margins,
                    boot_caps=[SENS_CAPITAL])
    sens["without_yield_proxies"] = {"idm_full": core.div_multiplier(sub, np.full(len(idx), 1 / len(idx))),
                                     "rows": nr[SENS_CAPITAL]}
    cfg_s = json.loads(json.dumps(cfg))
    cfg_s["greedy"]["correlation"]["shrinkage"]["value"] = None
    shr, _ = run_set(insts, cfg_s, np.asarray(est["idm_corr"]), list(CAPITALS_MAIN), out_dir,
                     "noshrink", margins)
    shr.pop("_idm_mean", None)
    sens["greedy_no_shrink"] = {"rows_by_capital": shr, "note": (
        "greedy WITHOUT the 0.5 correlation shrink (the main greedy rows use it, lead ruling R-B6)")}
    result["greedy_te_diagnostic"] = greedy_te_diagnostic(grid, cfg, out_dir, CAPITALS_SWEEP)
    if with_sensitivity:
        cfg_b = json.loads(json.dumps(cfg))
        cfg_b["ewmac"]["scalars"]["value"] = dict(SCALARS_BOOK)
        ib, _ = load_instruments(cache_dir, MICROS, cfg_b)
        for ins in ib:
            B.add_combined(ins, cfg_b, est["fdm"])
        br, _ = run_set(ib, cfg_b, np.asarray(est["idm_corr"]), [SENS_CAPITAL], out_dir,
                        "bookscalars", margins)
        sens["book_scalars_fdm_idm_held"] = {"forecast_means": forecast_means(ib, cfg_b),
                                             "rows": br[SENS_CAPITAL]}
        swap = [m for m in MICROS if m.code not in ("10Y", "30Y")] + list(SENSITIVITY)
        isw, nsw = load_instruments(cache_dir, swap, cfg)
        est_sw = estimate_all(isw, cfg, fdm=est["fdm"])
        sr, _ = run_set(isw, cfg, np.asarray(est_sw["idm_corr"]), [SENS_CAPITAL], out_dir,
                        "mtnmwn", margins)
        sens["mtn_mwn_for_10y_30y"] = {"idm": est_sw["idm"], "rows": sr[SENS_CAPITAL],
                                       "instruments": instrument_rows(isw[-2:], cfg, est_sw["idm"]),
                                       "data_notes": {k: nsw[k] for k in ("MTN", "MWN")}}
    result["sensitivities_25k"] = sens
    result["config_path"] = str(cfg_path)
    result["finished_local"] = now_local()
    clean = strip(result)
    report_json.write_text(json.dumps(clean, indent=1, default=str) + "\n", encoding="utf-8")
    from microbook.report import write_report

    write_report(clean, cfg, report_md)
    return clean


__all__ = ["CAPITALS_MAIN", "CAPITALS_SWEEP", "SENTENCE", "run_study"]
