"""E22-F2 positions (reports/stage_e24_prereg_F2.md, sections 2, 4 and 6 as revised 2026-10-18).

    forward.strategy_f2.target_shares(history, prev_shares, config) -> {symbol: float}

The rule is E22-F1's, reused through E22-F1's frozen code: ``forward.strategy.instrument_state``
(per-instrument forecast, annual dollar volatility and live flag, with spec multiplier 1 and
yield_quoted false) and ``forward.core`` (idm_for_live, unrounded_position, average_position,
round_half_away). Only the position steps of prereg section 4 are new:

1. unrounded targets n_i (shares) and average positions a_i (forecast +10);
2. leverage cap: with C the gross notional of the carried positions (ETFs without a close on t,
   valued at their last close) and G = sum |n_i| x close_i(t) over the instruments that get a new
   target, if C + G > B every such n_i and a_i is multiplied by max(0, B - C) / G (C held fixed);
3. Carver's buffer around the capped n_i (trade to the edge, buffer_size x a_i), no rounding;
4. granularity: non-negative targets rounded half away from zero to the fractional increment,
   negative targets rounded toward zero to whole shares;
5. second cap check: if the gross exposure of the result at close(t), C included, exceeds B,
   every position that got a new target, long or short, is multiplied by max(0, B - C) / (its
   gross), then longs are rounded toward zero to the fractional increment and shorts toward zero
   to whole shares, so the gross never exceeds B unless C alone exceeds it (then every new target
   is 0 and the carried positions are left as they are);
6. an instrument with no close on t keeps its shares (no new target); a live instrument whose close
   arrives gets a target; a non-live instrument with a close on t gets 0.

``history``: either a sequence of ``forward.etf_bars.EtfDayRow`` (or ``(date, {symbol: EtfBar})``
pairs), oldest first, ending with the decision date t (warm-up rows, then one row per ledger
session); or ``{symbol: DataFrame}`` with columns ``adj_price`` and ``price`` indexed by session
date. For rows, each symbol's signal frame is built by ``signal_frame``: ``price`` = the raw close,
``adj_price`` = the back-adjusted total-return close of prereg section 6 (equal to the raw close on
the symbol's latest session, divided going back by (1 + r(u)) for each later session u).

``prev_shares``: shares held after t's fills (a missing symbol counts as 0).
``config``: forward/config_f2.json as loaded by json (``load_config``).
Pure: no I/O except ``load_config``.
"""

from __future__ import annotations

import json
import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from forward import core
from forward.etf_bars import EtfBar, EtfDayRow
from forward.strategy import instrument_state

DEFAULT_CONFIG = Path(__file__).resolve().parent / "config_f2.json"


def load_config(path: Path | str = DEFAULT_CONFIG) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


# ------------------------------------------------------------------ signal series (section 6) ----
def back_adjusted(closes: Sequence[float], rets: Sequence[float | None]) -> list[float]:
    """Section 6: the latest value is the raw close; going back, divide by (1 + r(u)) for each
    later session u. ``rets[k]`` is the total return from session k-1 to k (``rets[0]`` unused)."""
    n = len(closes)
    if n != len(rets):
        raise ValueError("closes and rets must have the same length")
    if n == 0:
        return []
    adj = [0.0] * n
    adj[-1] = float(closes[-1])
    for k in range(n - 2, -1, -1):
        r = rets[k + 1]
        if r is None:
            raise ValueError(f"session {k + 1} has no total return; the series cannot be rebuilt")
        adj[k] = adj[k + 1] / (1.0 + float(r))
    return adj


def _as_row(row: Any) -> EtfDayRow:
    if isinstance(row, EtfDayRow):
        return row
    if isinstance(row, tuple) and len(row) == 2:
        return EtfDayRow(row[0], row[1])
    raise TypeError(f"history rows must be EtfDayRow or (date, bars), got {type(row).__name__}")


def signal_frame(dates: Sequence[date], bars: Sequence[EtfBar]) -> pd.DataFrame:
    """DataFrame(adj_price, price) for one symbol's bars in date order (section 6)."""
    closes = [b.close for b in bars]
    adj = back_adjusted(closes, [b.ret for b in bars])
    idx = pd.DatetimeIndex(pd.to_datetime(list(dates)))
    return pd.DataFrame({"adj_price": adj, "price": closes}, index=idx)


def frames_from_history(history: Any, symbols: Sequence[str]) -> dict[str, pd.DataFrame]:
    """{symbol: DataFrame(adj_price, price)} from either history format (module docstring)."""
    if isinstance(history, Mapping):
        return {s: history[s] for s in symbols if s in history and len(history[s])}
    rows = [_as_row(r) for r in history]
    for a, b in zip(rows, rows[1:], strict=False):
        if b.date <= a.date:
            raise ValueError(f"history rows must be strictly ascending: {a.date} then {b.date}")
    out = {}
    for s in symbols:
        dates = [r.date for r in rows if s in r.bars]
        if dates:
            out[s] = signal_frame(dates, [r.bars[s] for r in rows if s in r.bars])
    return out


# ------------------------------------------------------------------ position steps (section 4) ----
def increment_steps(config: Mapping) -> int:
    """1 / fractional increment, which must be a whole number (0.001 -> 1000)."""
    inc = float(config["fractional_increment_shares"]["value"])
    if not (math.isfinite(inc) and 0 < inc <= 1):
        raise ValueError(f"fractional increment must be in (0, 1], got {inc!r}")
    steps = round(1.0 / inc)
    if abs(steps * inc - 1.0) > 1e-12:
        raise ValueError(f"1 / fractional increment must be a whole number, got {1.0 / inc!r}")
    return int(steps)


def granular(x: float, steps: int) -> float:
    """Step 4: x >= 0 rounded half away from zero to 1 / steps shares; x < 0 rounded toward zero
    to whole shares."""
    x = float(x)
    if x >= 0:
        return float(core.round_half_away(x * steps)) / steps + 0.0
    return float(math.trunc(x)) + 0.0


def floor_long(x: float, steps: int) -> float:
    """Step 5: a scaled long rounded toward zero to 1 / steps shares (never above x)."""
    return float(math.floor(float(x) * steps)) / steps + 0.0 if x > 0 else 0.0


def toward_zero(x: float, steps: int) -> float:
    """Step 5: a scaled long rounded toward zero to 1 / steps shares, a scaled short toward zero
    to whole shares."""
    return floor_long(x, steps) if x > 0 else float(math.trunc(float(x))) + 0.0


def _trim_to_cap(
    targets: dict[str, float],
    close: Mapping[str, float],
    longs: Sequence[str],
    cap_usd: float,
    steps: int,
) -> int:
    """Floating-point guard for step 5's 'the gross never exceeds B': while the computed gross
    is above B, take one increment off the largest long (by value). Returns the number of trims
    (0 unless float rounding of the sums left the gross a hair above B)."""
    trims = 0
    while _gross(targets, close) > cap_usd:
        live = [s for s in longs if targets[s] > 0]
        if not live:
            break
        s = max(live, key=lambda x: (targets[x] * close[x], x))
        targets[s] = max(0.0, (round(targets[s] * steps) - 1) / steps) + 0.0
        trims += 1
    return trims


def buffered(n: float, a: float, q: float, buffer_size: float) -> float:
    """Step 3: q if n - bs x a <= q <= n + bs x a, else the nearer edge (no rounding)."""
    lower, upper = n - buffer_size * a, n + buffer_size * a
    if q < lower:
        return lower
    if q > upper:
        return upper
    return q


@dataclass(frozen=True)
class StepsResult:
    targets: dict[str, float]
    unrounded_gross_usd: float
    cap_scale: float
    cap_bound: bool
    n_capped: dict[str, float]
    a_capped: dict[str, float]
    buffered: dict[str, float]
    second_check: dict[str, Any]
    target_gross_usd: float
    carried_gross_usd: float = 0.0


def position_steps(
    symbols: Sequence[str],
    n: Mapping[str, float],
    a: Mapping[str, float],
    prev: Mapping[str, float],
    close: Mapping[str, float],
    zero: set[str] | frozenset[str],
    *,
    cap_usd: float,
    buffer_size: float,
    steps: int,
) -> StepsResult:
    """Section 4 steps 2-6 on given unrounded targets ``n`` and average positions ``a`` (the
    instruments that get a new target: live, with a close on t). ``zero``: instruments with a close
    on t that are not live (target 0). Every other instrument keeps ``prev`` (carried; its gross
    at ``close`` is C). ``close``: close(t) for instruments with a close on t, the last close for
    the others (used for the gross only)."""
    syms = list(symbols)
    new = [s for s in syms if s in n]
    if set(new) & set(zero):
        raise ValueError("an instrument cannot both get a target and be set to zero")
    targets = {s: float(prev.get(s, 0.0)) + 0.0 for s in syms}
    for s in zero:
        targets[s] = 0.0
    carried = _gross({s: targets[s] for s in syms if s not in n and s not in zero}, close)
    room = max(0.0, cap_usd - carried)
    g = math.fsum(abs(n[s]) * close[s] for s in new)
    bound = carried + g > cap_usd
    scale = (room / g if g > 0 else 0.0) if bound else 1.0
    n_c = {s: n[s] * scale for s in new}
    a_c = {s: a[s] * scale for s in new}
    buf = {s: buffered(n_c[s], a_c[s], float(prev.get(s, 0.0)), buffer_size) for s in new}
    for s in new:
        targets[s] = granular(buf[s], steps)
    gross = _gross(targets, close)
    second: dict[str, Any] = {
        "gross_before_usd": gross,
        "carried_gross_usd": carried,
        "applied": False,
        "factor": None,
    }
    if gross > cap_usd:
        movers = [s for s in new if targets[s] != 0]
        g_new = math.fsum(abs(targets[s]) * close[s] for s in movers)
        if g_new > 0:
            for s in movers:
                targets[s] = toward_zero(targets[s] * room / g_new, steps)
            longs = [s for s in movers if targets[s] > 0]
            second = {
                **second,
                "applied": True,
                "factor": room / g_new,
                "scaled": sorted(movers),
                "float_trims": _trim_to_cap(targets, close, longs, cap_usd, steps),
            }
        else:  # nothing that got a new target holds a position: C alone exceeds B
            second = {**second, "nothing_to_scale": True}
    return StepsResult(
        targets=targets,
        unrounded_gross_usd=g,
        cap_scale=scale,
        cap_bound=bound,
        n_capped=n_c,
        a_capped=a_c,
        buffered=buf,
        second_check=second,
        target_gross_usd=_gross(targets, close),
        carried_gross_usd=carried,
    )


def _gross(targets: Mapping[str, float], close: Mapping[str, float]) -> float:
    vals = []
    for s, q in targets.items():
        if q == 0:
            continue
        if s not in close:
            raise ValueError(f"{s}: holds {q} shares but has no close to value them")
        vals.append(abs(q) * close[s])
    return math.fsum(vals)


# ------------------------------------------------------------------ the decision ----
@dataclass(frozen=True)
class Decision:
    """Targets for every instrument plus what the ledger records about how they were made."""

    targets: dict[str, float]
    decision_date: str | None
    signals: dict[str, dict[str, Any]] = field(default_factory=dict)
    exposure: dict[str, Any] = field(default_factory=dict)


def _finite_or_none(x: Any) -> float | None:
    try:
        v = float(x)
    except (TypeError, ValueError):
        return None
    return v if math.isfinite(v) else None


def _spec(config: Mapping, s: str) -> dict:
    spec = dict(config["instruments"][s])
    if float(spec["multiplier"]) != 1.0 or spec.get("yield_quoted"):
        raise ValueError(f"{s}: E22-F2 instruments have multiplier 1 and are not yield quoted")
    return spec


def decide(
    history: Any,
    prev_shares: Mapping[str, float],
    config: Mapping,
    *,
    decision_date: date | None = None,
) -> Decision:
    """Section 4 steps 1-6 at the decision date (default: the latest date in ``history``)."""
    symbols = list(config["instruments_order"])
    if list(config["idm"]["instruments"]) != symbols:
        raise ValueError("config idm.instruments must equal instruments_order")
    prev = {s: float(prev_shares.get(s, 0.0)) + 0.0 for s in symbols}
    states, last_close = {}, {}
    for s, df in frames_from_history(history, symbols).items():
        states[s] = instrument_state(df, _spec(config, s), config)
        last_close[s] = float(df["price"].iloc[-1]) if "price" in df else float("nan")
    if not states:
        return Decision(dict(prev), None)
    t = (
        pd.Timestamp(decision_date)
        if decision_date is not None
        else max(st["last"] for st in states.values())
    )
    if any(st["last"] > t for st in states.values()):
        raise ValueError(f"history holds data after the decision date {t.date()}")
    live = np.array([s in states and states[s]["live"] for s in symbols])
    today = {s for s in symbols if s in states and states[s]["last"] == t}
    idm = core.idm_for_live(
        np.asarray(config["idm"]["correlation"], dtype=float),
        live,
        config["idm"]["dm_max"]["value"],
    )
    n_live = int(live.sum())
    w = 1.0 / n_live if n_live else 0.0
    cap_usd = float(config["capital_usd"]["value"])
    tau = float(config["vol_target"]["value"])
    new = [s for s, lv in zip(symbols, live, strict=True) if lv and s in today]
    n_map, a_map = {}, {}
    for s in new:
        F, V = states[s]["F"], states[s]["V"]
        n_map[s] = float(core.unrounded_position(F, cap_usd, tau, idm, w, V))
        a_map[s] = float(core.average_position(cap_usd, tau, idm, w, V))
    zero = {s for s, lv in zip(symbols, live, strict=True) if not lv and s in today}
    res = position_steps(
        symbols,
        n_map,
        a_map,
        prev,
        last_close,
        zero,
        cap_usd=float(config["leverage_cap_usd"]["value"]),
        buffer_size=float(config["simple_rounding"]["buffer_size"]["value"]),
        steps=increment_steps(config),
    )
    signals = {
        s: {
            "F": _finite_or_none(st["F"]),
            "V": _finite_or_none(st["V"]),
            "live": bool(st["live"]),
            "close_on_t": s in today,
            "last_date": st["last"].date().isoformat(),
            "n_unrounded": n_map.get(s),
            "a": a_map.get(s),
            "n_capped": res.n_capped.get(s),
            "a_capped": res.a_capped.get(s),
            "buffered": res.buffered.get(s),
        }
        for s, st in sorted(states.items())
    }
    exposure = {
        "idm": idm,
        "n_live": n_live,
        "weight": w,
        "cap_usd": float(config["leverage_cap_usd"]["value"]),
        "unrounded_gross_usd": res.unrounded_gross_usd,
        "cap_scale": res.cap_scale,
        "cap_bound": res.cap_bound,
        "carried_gross_usd": res.carried_gross_usd,
        "second_check": res.second_check,
        "target_gross_usd": res.target_gross_usd,
    }
    return Decision(res.targets, t.date().isoformat(), signals, exposure)


def target_shares(
    history: Any,
    prev_shares: Mapping[str, float],
    config: Mapping,
    *,
    decision_date: date | None = None,
) -> dict[str, float]:
    """Target shares for every symbol of config["instruments_order"] (module docstring)."""
    return decide(history, prev_shares, config, decision_date=decision_date).targets


__all__ = [
    "DEFAULT_CONFIG",
    "Decision",
    "StepsResult",
    "back_adjusted",
    "buffered",
    "floor_long",
    "decide",
    "frames_from_history",
    "granular",
    "increment_steps",
    "load_config",
    "position_steps",
    "signal_frame",
    "target_shares",
    "toward_zero",
]
