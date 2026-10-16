"""E22-F1's strategy entry point for the paper runner (lead_spec_B.md S7):

    forward.strategy.target_positions(history, prev_positions, config) -> {instrument: int}

``history``, either
- the paper runner's format (forward/README.md "Strategy interface"): a sequence of
  forward.history.HistoryRow, oldest first, ending with the decision date t (warm-up rows, then
  one row per ledger date); each instrument's frame comes from forward.history.instrument_frame
  (column "adjusted": the additive back-adjustment at each reference switch, for signals;
  "price": the held contract's own settlement, for the record); or
- {code: pandas.DataFrame} indexed by settlement date (ascending, unique) with columns
  "adj_price" (back-adjusted settlement series) and "price" (held contract's settlement).
Either way it holds ONLY data through t; for the yield micros (2YY, 10Y, 30Y) prices are yields in
percent (lead ruling (2)).
``prev_positions``: {code: int}, the contracts held after day t's fills and rolls (the runner's
"held"; equal to the previous targets once they have filled); a missing code counts as 0.
``config``: forward/config_f1.json as loaded by json (load_config below).

Returns integer target positions for every code of config["instruments_order"], to be filled at
each instrument's next settlement (S3.7). The decision date t is the latest date in ``history``.
An instrument without a settlement on t keeps its previous position (no new order; prereg section
6). An instrument is live once it has config["warmup_diffs"] daily differences; one that is not
live has target 0. Rounding: config["rounding_method"] ("greedy": the November 2021 dynamic
optimisation; "simple": rounded and buffered). Pure: no I/O except load_config.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path

import numpy as np
import pandas as pd

from forward import core
from forward.history import HistoryRow, instrument_frame

DEFAULT_CONFIG = Path(__file__).resolve().parent / "config_f1.json"


def load_config(path: Path | str = DEFAULT_CONFIG) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _series(df: pd.DataFrame, col: str) -> pd.Series:
    s = df[col].astype(float)
    s.index = pd.DatetimeIndex(pd.to_datetime(df.index))
    return s.sort_index()


def frames_from_history(history, codes: list[str]) -> dict[str, pd.DataFrame]:
    """{code: DataFrame(adj_price, price)} from either history format (module docstring)."""
    if isinstance(history, Mapping):
        return {c: history[c] for c in codes if c in history}
    rows = tuple(history)
    if rows and not all(isinstance(r, HistoryRow) for r in rows):
        raise TypeError("history must be a mapping of frames or a sequence of HistoryRow")
    out = {}
    for c in codes:
        f = instrument_frame(rows, c)
        if len(f):
            out[c] = f.rename(columns={"adjusted": "adj_price"})
    return out


def instrument_state(df: pd.DataFrame, spec: Mapping, config: Mapping) -> dict:
    """Latest combined forecast, annual $ vol per contract, live flag and correlation returns."""
    adj = _series(df, "adj_price")
    price = _series(df, "price")
    if adj.index.has_duplicates:
        raise ValueError("history dates must be unique")
    d = adj.diff()
    vol = core.vol_from_config(d.dropna(), config).reindex(adj.index).ffill()
    _, fc = core.forecasts_from_config(adj, vol, config)
    v_last = float(core.annual_dollar_vol(vol.iloc[-1], spec["multiplier"])) if len(vol) else float("nan")
    n_diff = int(d.notna().sum())
    live = bool(n_diff >= config["warmup_diffs"]["value"] and np.isfinite(v_last) and v_last > 0)
    ret = d if spec.get("yield_quoted") else d / price  # C-PORT get_daily_percentage_returns
    return {"last": adj.index[-1], "F": float(fc.iloc[-1]) if len(fc) else float("nan"),
            "V": v_last, "live": live, "ret": ret.fillna(0.0)}


def correlation_at(states: Mapping[str, dict], codes: list[str], decision: pd.Timestamp,
                   config: Mapping) -> np.ndarray:
    """The greedy's instrument-return correlation at the decision date (config greedy.correlation)."""
    c = config["greedy"]["correlation"]
    step = int(c["return_days"]["value"])
    n_steps = int(round(c["years"]["value"] * 365.25 / step))
    days = sorted({d for code in codes for d in states[code]["ret"].index})
    idx = pd.DatetimeIndex(days)
    cum = np.full((len(idx), len(codes)), np.nan)
    for k, code in enumerate(codes):
        cum[:, k] = states[code]["ret"].cumsum().reindex(idx).ffill().to_numpy()
    ordinals = np.array([d.toordinal() for d in idx.date], dtype=np.int64)
    r = core.sampled_returns(cum, ordinals, decision.toordinal(), step, n_steps)
    return core.correlation_from_config(r, config)


def target_positions(history: Mapping[str, pd.DataFrame], prev_positions: Mapping[str, int],
                     config: Mapping) -> dict[str, int]:
    codes = list(config["instruments_order"])
    specs = config["instruments"]
    prev = np.array([float(prev_positions.get(c, 0)) for c in codes])
    states = {}
    for c, df in frames_from_history(history, codes).items():
        if df is not None and len(df):
            states[c] = instrument_state(df, specs[c], config)
    if not states:
        return {c: int(p) for c, p in zip(codes, prev)}
    decision = max(s["last"] for s in states.values())
    live = np.array([c in states and states[c]["live"] for c in codes])
    today = np.array([c in states and states[c]["last"] == decision for c in codes])
    order = list(config["idm"]["instruments"])
    if order != codes:
        raise ValueError("config idm.instruments must equal instruments_order")
    idm = core.idm_for_live(np.asarray(config["idm"]["correlation"]), live,
                            config["idm"]["dm_max"]["value"])
    n_live = int(live.sum())
    w = 1.0 / n_live if n_live else 0.0
    cap_usd = float(config["capital_usd"]["value"])
    tau = float(config["vol_target"]["value"])
    out = prev.copy()
    out[today & ~live] = 0.0
    idx = np.flatnonzero(today & live)
    if len(idx):
        F = np.array([states[codes[i]]["F"] for i in idx])
        V = np.array([states[codes[i]]["V"] for i in idx])
        nstar = core.unrounded_position(F, cap_usd, tau, idm, w, V)
        method = config["rounding_method"]["value"]
        if method == "greedy":
            sel = [codes[i] for i in idx]
            corr = correlation_at(states, sel, decision, config)
            cost = np.array([float(specs[c]["cost_per_side_usd"]) for c in sel])
            g = config["greedy"]
            res = core.dynamic_optimise(nstar, prev[idx], core.covariance(corr, V), cost, cap_usd,
                                        shadow_cost=g["shadow_cost"]["value"],
                                        te_buffer=g["te_buffer"]["value"])
            out[idx] = res.positions
        elif method == "simple":
            avg = core.average_position(cap_usd, tau, idm, w, V)
            out[idx] = core.buffered_round(nstar, avg, prev[idx],
                                           config["simple_rounding"]["buffer_size"]["value"])
        else:
            raise ValueError(f"rounding method {method!r} gives no integer positions")
    return {c: int(round(p)) for c, p in zip(codes, out)}


__all__ = ["DEFAULT_CONFIG", "correlation_at", "frames_from_history", "instrument_state", "load_config",
           "target_positions"]
