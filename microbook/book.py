"""The historical book (lead_spec_B.md S3-S6): per-instrument series from the cache, the FDM and
IDM estimates, and the daily simulation of one capital level and rounding method.

Timing (S3.7): instrument i decides on each of its mark dates t from data through settle(t); the
target fills at i's next mark (settle(t+1)). On the union grid G of all mark dates, pos[t, i] is
the position after the fills at t: pos[t] = target[t - 1] where i has a mark at t, else pos[t - 1].
The P&L booked at mark t is pos[t - 1] x multiplier x dP(t) (the move from the previous mark,
held by the position filled there); the fill at t pays |pos[t] - pos[t - 1]| x the per-side cost of
its side; a roll inside (previous mark, t] pays |pos[t - 1]| x the roll legs' costs (two fills per
contract). A grid date without a mark of i carries its position and target (no fill, no order).
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from forward import core
from microbook.universe import Micro, per_side_extension_cents

METHODS = ("unrounded", "simple", "greedy")


# ------------------------------------------------------------------ one instrument ----
@dataclass
class Instrument:
    micro: Micro
    frame: pd.DataFrame  # indexed by mark date


def prepare(micro: Micro, cache: pd.DataFrame, cfg: Mapping) -> tuple[Instrument, dict]:
    """Study units, signal series, vol, $ vol, live flag, speed forecasts, costs (cents)."""
    f = cache.set_index("date").sort_index()
    out = pd.DataFrame(index=f.index)
    notes: dict = {}
    if micro.yield_proxy:
        dy = pd.Series(core.yield_proxy_diffs(f["dp"].to_numpy(), f["price"].to_numpy(),
                                              micro.duration), index=f.index)
        out["d"] = dy  # bp
        out["ret"] = dy  # correlation input: yield changes (bp)
    else:
        out["d"] = f["dp"]
        out["ret"] = f["dp"] / f["price"]  # C-PORT get_daily_percentage_returns: dP / P(current)
    out["price"] = f["price"]
    out["contract"] = f["contract"]
    notes["undefined moves (failed intervals, P&L 0)"] = int(f["dp"].iloc[1:].isna().sum())
    out["sig"] = out["d"].fillna(0.0).cumsum()
    d_def = out["d"].dropna()
    vol = core.vol_from_config(d_def, cfg).reindex(out.index).ffill()
    out["vol"] = vol
    out["V"] = core.annual_dollar_vol(vol, micro.multiplier)
    n_def = out["d"].notna().cumsum()
    out["live"] = (n_def >= cfg["warmup_diffs"]["value"]) & (out["V"] > 0) & out["V"].notna()
    e = cfg["ewmac"]
    speeds = [tuple(x) for x in e["speeds"]["value"]]
    scal = [e["scalars"]["value"][f"{a}/{b}"] for a, b in speeds]
    sp = core.speed_forecasts(out["sig"], vol, speeds, scal, cfg["forecast_cap"]["value"])
    for c in sp.columns:
        out[f"fc_{c}"] = sp[c]
    # costs per contract per side, cents (S6)
    if micro.cost_basis == "frozen":
        out["cost_buy"] = f["cost_buy_c"]
        out["cost_sell"] = f["cost_sell_c"]
        out["slip_buy"] = f["cost_buy_c"] - f["comm_side_c"]
        out["slip_sell"] = f["cost_sell_c"] - f["comm_side_c"]
        out["roll_long"] = f["roll_long_c"]
        out["roll_short"] = f["roll_short_c"]
        comm2 = 2.0 * f["n_rolls"] * f["comm_side_c"]
        out["roll_slip_long"] = f["roll_long_c"] - comm2
        out["roll_slip_short"] = f["roll_short_c"] - comm2
    else:
        side = per_side_extension_cents(micro)
        slip = 100.0 * micro.tick_value
        out["cost_buy"] = out["cost_sell"] = side
        out["slip_buy"] = out["slip_sell"] = slip
        out["roll_long"] = out["roll_short"] = 2.0 * f["n_rolls"] * side
        out["roll_slip_long"] = out["roll_slip_short"] = 2.0 * f["n_rolls"] * slip
    out["n_rolls"] = f["n_rolls"]
    return Instrument(micro, out), notes


def speed_columns(cfg: Mapping) -> list[str]:
    return [f"fc_{a}/{b}" for a, b in cfg["ewmac"]["speeds"]["value"]]


def add_combined(inst: Instrument, cfg: Mapping, fdm: float) -> None:
    sp = inst.frame[speed_columns(cfg)]
    sp.columns = [c[3:] for c in sp.columns]
    inst.frame["F"] = core.combine_forecasts(sp, fdm, cfg["forecast_cap"]["value"])


# ------------------------------------------------------------------ FDM / IDM ----
def estimate_fdm(insts: Sequence[Instrument], cfg: Mapping) -> tuple[float, np.ndarray, int]:
    """S3.3: weekly (W-FRI last) scaled capped forecasts on live dates, stacked over instruments,
    Pearson 4 x 4, floored at 0, FDM = min(1 / sqrt(w' H w), 2.5)."""
    cols = speed_columns(cfg)
    stacks = []
    for ins in insts:
        f = ins.frame.loc[ins.frame["live"], cols]
        stacks.append(f.resample("W-FRI").last().dropna())
    pooled = pd.concat(stacks, ignore_index=True)
    corr = pooled.corr().to_numpy()
    w = np.asarray(cfg["fdm"]["weights"]["value"], dtype=float)
    fdm = core.div_multiplier(corr, w, dm_max=cfg["fdm"]["dm_max"]["value"])
    return fdm, corr, len(pooled)


def subsystem_returns(ins: Instrument) -> pd.Series:
    """Daily $ return of the instrument's subsystem per $1 of annual risk: position F / 10 / V
    (decided at mark t, held from the next mark), times multiplier x dP."""
    f = ins.frame
    s = (f["F"] / 10.0 / f["V"]).where(f["live"], 0.0).fillna(0.0)
    held = s.shift(2).fillna(0.0)  # decided at t-2, filled at t-1, earns the move to t
    return held * ins.micro.multiplier * f["d"].fillna(0.0)


def estimate_idm(insts: Sequence[Instrument], cfg: Mapping) -> tuple[float, np.ndarray, list[str]]:
    """S3.5: weekly (W-FRI sum) subsystem returns, pairwise Pearson over weeks where both are
    live, floored at 0; IDM = min(1 / sqrt(w' H w), 2.5) with w = 1/n."""
    cols = {}
    for ins in insts:
        r = subsystem_returns(ins)
        live_w = ins.frame["live"].resample("W-FRI").max().astype(bool)
        wk = r.resample("W-FRI").sum()
        cols[ins.micro.code] = wk.where(live_w)
    df = pd.DataFrame(cols)
    corr = np.array(df.corr(min_periods=52).fillna(0.0).to_numpy(), dtype=float, copy=True)
    np.fill_diagonal(corr, 1.0)
    n = len(insts)
    idm = core.div_multiplier(corr, np.full(n, 1.0 / n), dm_max=cfg["idm"]["dm_max"]["value"])
    return idm, corr, list(cols)


# ------------------------------------------------------------------ the grid ----
@dataclass
class Grid:
    dates: pd.DatetimeIndex
    codes: list[str]
    mult: np.ndarray
    has_mark: np.ndarray  # T x n bool
    live: np.ndarray  # T x n bool (carried from the last mark)
    F: np.ndarray
    V: np.ndarray
    d: np.ndarray  # move booked at the mark (study units), 0 where none/undefined
    cost: dict[str, np.ndarray]  # name -> T x n (cents)
    n_rolls: np.ndarray
    ret_cum: np.ndarray  # cumulated correlation returns (NaN before the first mark)
    ret_days: np.ndarray  # ordinal day of each grid date
    extra: dict = field(default_factory=dict)


def build_grid(insts: Sequence[Instrument]) -> Grid:
    dates = pd.DatetimeIndex(sorted(set().union(*[set(i.frame.index) for i in insts])))
    codes = [i.micro.code for i in insts]
    T, n = len(dates), len(insts)

    def col(name: str, fill, how: str = "mark") -> np.ndarray:
        out = np.empty((T, n), dtype=float)
        for k, ins in enumerate(insts):
            s = ins.frame[name].astype(float).reindex(dates)
            if how == "ffill":
                s = s.ffill()
            out[:, k] = s.fillna(fill).to_numpy()
        return out

    has = np.zeros((T, n), dtype=bool)
    for k, ins in enumerate(insts):
        has[:, k] = dates.isin(ins.frame.index)
    live = col("live", 0.0, "ffill").astype(bool)
    cost = {c: col(c, 0.0) for c in ("cost_buy", "cost_sell", "slip_buy", "slip_sell",
                                     "roll_long", "roll_short", "roll_slip_long",
                                     "roll_slip_short")}
    ret_cum = np.full((T, n), np.nan)
    for k, ins in enumerate(insts):
        r = ins.frame["ret"].fillna(0.0).cumsum().reindex(dates).ffill()
        ret_cum[:, k] = r.to_numpy()
    return Grid(dates, codes, np.array([i.micro.multiplier for i in insts]), has, live,
                col("F", 0.0, "ffill"), col("V", np.nan, "ffill"), col("d", 0.0),
                cost, col("n_rolls", 0.0), ret_cum,
                np.array([d.toordinal() for d in dates.date], dtype=np.int64))


def correlations(grid: Grid, cfg: Mapping) -> np.ndarray:
    """The greedy's instrument-return correlation at every grid date (data through that date)."""
    c = cfg["greedy"]["correlation"]
    step = int(c["return_days"]["value"])
    n_steps = int(round(c["years"]["value"] * 365.25 / step))
    out = np.empty((len(grid.dates), len(grid.codes), len(grid.codes)))
    for t in range(len(grid.dates)):
        r = core.sampled_returns(grid.ret_cum[: t + 1], grid.ret_days[: t + 1],
                                 int(grid.ret_days[t]), step, n_steps)
        out[t] = core.correlation_from_config(r, cfg)
    return out


# ------------------------------------------------------------------ one book ----
@dataclass
class BookRun:
    method: str
    capital: float
    targets: np.ndarray  # T x n
    pos: np.ndarray  # T x n (after the fills at t)
    nstar: np.ndarray  # T x n unrounded optimum at decision dates (NaN elsewhere)
    counters: dict


def idm_series(grid: Grid, idm_corr: np.ndarray, dm_max: float) -> np.ndarray:
    cache: dict = {}
    out = np.zeros(len(grid.dates))
    for t in range(len(grid.dates)):
        key = grid.live[t].tobytes()
        if key not in cache:
            cache[key] = core.idm_for_live(idm_corr, grid.live[t], dm_max)
        out[t] = cache[key]
    return out


def simulate(grid: Grid, cfg: Mapping, method: str, capital: float, idm_t: np.ndarray,
             corr_t: np.ndarray | None = None) -> BookRun:
    T, n = grid.has_mark.shape
    tau = cfg["vol_target"]["value"]
    n_live = grid.live.sum(axis=1)
    w = np.where(n_live > 0, 1.0 / np.maximum(n_live, 1), 0.0)
    decide = grid.has_mark & grid.live
    with np.errstate(invalid="ignore", divide="ignore"):
        nstar_all = core.unrounded_position(grid.F, capital, tau, idm_t[:, None], w[:, None],
                                            grid.V)
        avg_all = core.average_position(capital, tau, idm_t[:, None], w[:, None], grid.V)
    nstar = np.where(decide, nstar_all, np.nan)
    targets = np.zeros((T, n))
    counters = {"greedy inside buffer": 0, "greedy no trade (integer optimum = current)": 0,
                "greedy no trade (x <= buffer)": 0, "greedy no trade (trades round to 0)": 0,
                "greedy traded": 0, "greedy all-zero integer result": 0, "decision dates": 0}
    g_cfg = cfg["greedy"]
    shadow, te_buf = g_cfg["shadow_cost"]["value"], g_cfg["te_buffer"]["value"]
    buf = cfg["simple_rounding"]["buffer_size"]["value"]
    prev = np.zeros(n)
    for t in range(T):
        cur = prev.copy()
        cur[grid.has_mark[t] & ~grid.live[t]] = 0.0  # not live: no position
        idx = np.flatnonzero(decide[t])
        if len(idx):
            counters["decision dates"] += 1
            if method == "unrounded":
                cur[idx] = nstar_all[t, idx]
            elif method == "simple":
                cur[idx] = core.buffered_round(nstar_all[t, idx], avg_all[t, idx], prev[idx], buf)
            elif method == "greedy":
                cov = core.covariance(corr_t[t][np.ix_(idx, idx)], grid.V[t, idx])
                cpc = 0.5 * (grid.cost["cost_buy"][t, idx] + grid.cost["cost_sell"][t, idx]) / 100.0
                res = core.dynamic_optimise(nstar_all[t, idx], prev[idx], cov, cpc, capital,
                                            shadow_cost=shadow, te_buffer=te_buf)
                cur[idx] = res.positions
                counters[f"greedy {res.stage}"] += 1
                counters["greedy all-zero integer result"] += int(res.greedy_all_zero)
            else:
                raise ValueError(method)
        targets[t] = cur
        prev = cur
    pos = np.zeros((T, n))
    for t in range(1, T):
        pos[t] = np.where(grid.has_mark[t], targets[t - 1], pos[t - 1])
    return BookRun(method, capital, targets, pos, nstar, counters)


def pnl(grid: Grid, run: BookRun, *, slip_mult: float = 1.0) -> dict[str, np.ndarray]:
    """Per-date per-instrument gross P&L, trade costs and roll costs ($), at slippage x
    ``slip_mult`` (1 = base, 2 = the S6 stress case)."""
    held = np.vstack([np.zeros((1, run.pos.shape[1])), run.pos[:-1]])
    gross = np.where(grid.has_mark, held * grid.mult[None, :] * grid.d, 0.0)
    trade = run.pos - held
    c = grid.cost
    extra = slip_mult - 1.0
    buy = c["cost_buy"] + extra * c["slip_buy"]
    sell = c["cost_sell"] + extra * c["slip_sell"]
    tcost = np.where(trade > 0, trade * buy, -trade * sell) / 100.0
    rl = c["roll_long"] + extra * c["roll_slip_long"]
    rs = c["roll_short"] + extra * c["roll_slip_short"]
    rcost = np.where(held > 0, held * rl, -held * rs) / 100.0
    rcost = np.where(grid.has_mark, rcost, 0.0)
    return {"gross": gross, "trade_cost": tcost, "roll_cost": rcost, "trade": trade,
            "held": held}


__all__ = ["BookRun", "Grid", "Instrument", "METHODS", "add_combined", "build_grid",
           "correlations", "estimate_fdm", "estimate_idm", "idm_series", "pnl", "prepare",
           "simulate", "speed_columns", "subsystem_returns"]
