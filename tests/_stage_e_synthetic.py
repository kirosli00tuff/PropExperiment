"""Synthetic bars and members for the Stage E runner tests (no real data is read here)."""

from __future__ import annotations

import json
from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import UTC, date, datetime, time, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

from strategy.interface import AccountView, Bar, limit_intent, market_intent

CT = ZoneInfo("America/Chicago")
NS = 1_000_000_000


def ts_ns(day: date, hh: int, mm: int, offset_days: int = 0) -> int:
    local = datetime.combine(day + timedelta(days=offset_days), time(hh, mm), tzinfo=CT)
    return int(local.astimezone(UTC).timestamp()) * NS


def mes_frame(days: Sequence[date], seed: int, *, start: tuple[int, int] = (8, 30),
              end: tuple[int, int] = (15, 15), drift_ticks: float = 0.0, vol_ticks: float = 2.0,
              gap_prob: float = 0.0, base_ticks: int = 20000) -> pd.DataFrame:
    """MES-shaped bars on the 0.25 grid, one session per day from ``start`` to ``end`` CT, with the
    MES flag columns (flatten 15:10, no new positions 15:08)."""
    rng = np.random.default_rng(seed)
    rows = []
    price = base_ticks
    for day in days:
        t0 = datetime.combine(day, time(*start), tzinfo=CT)
        n = (end[0] * 60 + end[1]) - (start[0] * 60 + start[1])
        gap = 0
        for k in range(n):
            if gap_prob and rng.random() < gap_prob:
                gap += 1
                price += int(round(rng.normal(drift_ticks, vol_ticks)))
                continue
            o = price
            c = o + int(round(rng.normal(drift_ticks, vol_ticks)))
            hi = max(o, c) + int(rng.integers(0, 3))
            lo = min(o, c) - int(rng.integers(0, 3))
            local = t0 + timedelta(minutes=k)
            minute = local.hour * 60 + local.minute
            rows.append({
                "ts_event": int(local.astimezone(UTC).timestamp()) * NS,
                "open": o * 0.25, "high": hi * 0.25, "low": lo * 0.25, "close": c * 0.25,
                "volume": int(rng.integers(1, 500)), "instrument_id": 4242,
                "raw_symbol": "MESZ5", "trade_date": day.isoformat(),
                "in_flatten_window": minute >= 15 * 60 + 10,
                "in_no_new_positions_window": minute >= 15 * 60 + 8,
                "early_halt_ct": "", "in_scheduled_closure": False, "is_roll_session": False,
                "gap_before_minutes": gap, "vendor_degraded_day": False,
            })
            gap = 0
            price = c
    return pd.DataFrame(rows)


@dataclass
class RandomMesStrategy:
    """Random market and limit orders of 1 to ``max_qty`` micros; deterministic per seed."""

    seed: int
    max_qty: int = 5
    p_order: float = 0.05
    p_limit: float = 0.3
    name: str = "random_mes"
    _rng: np.random.Generator = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._rng = np.random.default_rng(self.seed)

    def on_bar(self, bar: Bar, account: AccountView) -> tuple:
        rng = self._rng
        if rng.random() >= self.p_order:
            return ()
        pos = account.position_micros
        if pos and rng.random() < 0.5:
            side = "sell" if pos > 0 else "buy"
            qty = int(rng.integers(1, abs(pos) + 1))
        else:
            side = "buy" if rng.random() < 0.5 else "sell"
            qty = int(rng.integers(1, self.max_qty + 1))
        if rng.random() < self.p_limit:
            off = int(rng.integers(1, 6)) * 0.25
            price = bar.close - off if side == "buy" else bar.close + off
            return (limit_intent(bar, side, qty, price, int(rng.integers(1, 30))),)
        out = [market_intent(bar, side, qty)]
        if rng.random() < 0.05:
            out.append(market_intent(bar, "hold", 1))  # a construction refusal
        return tuple(out)


def write_parquet(frame: pd.DataFrame, path: Path, meta: dict) -> None:
    import pyarrow as pa
    import pyarrow.parquet as pq

    table = pa.Table.from_pandas(frame, preserve_index=False)
    existing = table.schema.metadata or {}
    table = table.replace_schema_metadata(
        {**existing, b"propexperiment": json.dumps(meta).encode("utf-8")})
    path.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(table, path)


# ------------------------------------------------------------ Stage E products ----
def product_frame(root: str, days: Sequence[date], seed: int, *, start: tuple[int, int] = (7, 0),
                  end: tuple[int, int] = (15, 20), base_ticks: int = 10000,
                  vol_ticks: float = 2.0, drift_ticks: float = 0.0, instrument_id: int = 777,
                  skip: set[int] | None = None, path_ticks: dict | None = None) -> pd.DataFrame:
    """Bars of ``root`` on its vendor tick grid, one CT day segment per trade date, flags from
    rules/sessions.py (both Stage E flag columns start where the session must be flat).
    ``path_ticks``: {(day, minute_of_day_ct): (o, h, l, c)} overrides in ticks."""
    from rules import sessions
    from rules.products import product

    tick_fixed = product(root).vendor_tick_fixed
    rng = np.random.default_rng(seed)
    rows = []
    price = base_ticks
    for day in days:
        t0 = datetime.combine(day, time(*start), tzinfo=CT)
        n = (end[0] * 60 + end[1]) - (start[0] * 60 + start[1])
        for k in range(n):
            local = t0 + timedelta(minutes=k)
            minute = local.hour * 60 + local.minute
            o = price
            c = o + int(round(rng.normal(drift_ticks, vol_ticks)))
            hi, lo = max(o, c) + int(rng.integers(0, 2)), min(o, c) - int(rng.integers(0, 2))
            if path_ticks and (day, minute) in path_ticks:
                o, hi, lo, c = path_ticks[(day, minute)]
            price = c
            if skip and minute in skip:
                continue
            state = sessions.session_state(root, local.astimezone(UTC))
            to_price = lambda t: t * tick_fixed / 1e9  # noqa: E731
            rows.append({
                "ts_event": int(local.astimezone(UTC).timestamp()) * NS,
                "open": to_price(o), "high": to_price(hi), "low": to_price(lo),
                "close": to_price(c), "volume": int(rng.integers(1, 50)),
                "instrument_id": instrument_id, "raw_symbol": f"{root}U5",
                "trade_date": day.isoformat(),
                "in_flatten_window": bool(state.must_be_flat),
                "in_no_new_positions_window": bool(not state.can_open),
                "early_halt_ct": "", "in_scheduled_closure": False, "is_roll_session": False,
                "gap_before_minutes": 0, "vendor_degraded_day": False,
            })
    return pd.DataFrame(rows)


def minute_ct(bar_or_ns: object) -> tuple[int, int]:
    ns = bar_or_ns if isinstance(bar_or_ns, int) else bar_or_ns.ts_event_ns  # type: ignore[attr-defined]
    local = datetime.fromtimestamp(ns / NS, tz=UTC).astimezone(CT)
    return local.hour, local.minute


MEMBER_SOURCE = '''"""A synthetic Stage E member for the runner tests."""
from dataclasses import dataclass, field
from datetime import UTC, datetime, time
from zoneinfo import ZoneInfo

from strategy.stage_e.interface import TradingInterval, leg_market_intent

CT = ZoneInfo("America/Chicago")
ROOT = "ZN"
ENTRY, EXIT, EARLY = {entry}, {exit}, {early}


@dataclass
class Member:
    name: str = "synthetic"
    trading_windows: dict = field(default_factory=lambda: {{ROOT: (TradingInterval(time(9, 0),
                                                                                  time(10, 0)),)}})

    def on_minute(self, view, account):
        bar = view.bar(ROOT)
        if bar is None:
            return ()
        t = datetime.fromtimestamp(bar.ts_event_ns / 1e9, tz=UTC).astimezone(CT)
        hm = (t.hour, t.minute)
        pos = account.position(ROOT)
        if hm == ENTRY and not pos:
            return (leg_market_intent(view, ROOT, "buy", 1),)
        if pos and (hm == EXIT or (EARLY and hm == (ENTRY[0], ENTRY[1] + 1))):
            return (leg_market_intent(view, ROOT, "sell", pos),)
        return ()


def make_member():
    return Member()


def other_factory():
    return Member()
'''


def install_member_package(tmp: Path, monkeypatch, cluster: str = "k1", name: str = "synth",
                           entry=(9, 10), exit_=(9, 40), early=False) -> str:
    """Write strategy/members/<cluster>/<name>.py under ``tmp`` and make it importable as
    strategy.members.<cluster>.<name>. Returns the dotted module name."""
    import importlib
    import sys

    import strategy

    base = tmp / "strategy" / "members" / cluster
    base.mkdir(parents=True, exist_ok=True)
    (tmp / "strategy" / "members" / "__init__.py").write_text("", encoding="utf-8")
    (base / "__init__.py").write_text("", encoding="utf-8")
    (base / f"{name}.py").write_text(
        MEMBER_SOURCE.format(entry=entry, exit=exit_, early=early), encoding="utf-8")
    # prepended: the repository's own (empty, frozen) strategy/members must not shadow the copy
    monkeypatch.setattr(strategy, "__path__", [str(tmp / "strategy"), *strategy.__path__])
    for mod in [m for m in sys.modules if m.startswith("strategy.members")]:
        monkeypatch.delitem(sys.modules, mod)
    importlib.invalidate_caches()
    return f"strategy.members.{cluster}.{name}"
