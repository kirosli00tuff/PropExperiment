"""Stage B-C ETA probe: time the thin backtest loop on one month of MES bars.

    uv run python -m sim.eta_probe

Month: April 2025, the EARLIEST month on disk — chosen so the probe never
touches data that could later fall inside the sealed holdout. The probe reads
no returns and computes no statistic on prices; it only times iteration.

Also times one rules-engine account-day (record P&L, real-time MLL check,
close the day, payout eligibility), because that step — not bar iteration —
is what the Stage B Monte Carlo repeats hundreds of millions of times.
"""

from __future__ import annotations

import json
import time
from collections.abc import Callable, Iterator, Sequence
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta

import numpy as np
import pandas as pd
import pyarrow.dataset as pads

from rules import xfa_rules as xr
from rules.xfa_rules import OrderIntent

# The probe's loop, moved here verbatim when sim/engine.py grew into the full engine
# (iter_probe_bars -> sim.engine.iter_bars, run_probe_loop -> sim.engine.run_backtest).
NS_PER_S = 1_000_000_000
NS_PER_MIN = 60 * NS_PER_S


@dataclass(frozen=True, slots=True)
class ProbeBar:
    ts_event_ns: int  # bar OPEN on Databento's receive clock
    open: float
    high: float
    low: float
    close: float
    volume: int
    trade_date: str
    in_flatten_window: bool
    in_no_new_positions_window: bool
    in_scheduled_closure: bool

    @property
    def decision_ts_utc(self) -> datetime:
        """The bar is only complete — and so only knowable — at its close."""
        return datetime.fromtimestamp((self.ts_event_ns + NS_PER_MIN) / NS_PER_S, tz=UTC)


def iter_probe_bars(frame: pd.DataFrame) -> Iterator[ProbeBar]:
    cols = {c: frame[c].to_numpy() for c in frame.columns}
    ts = cols["ts_event"].astype(np.int64)
    if len(ts) > 1 and not (np.diff(ts) > 0).all():
        raise ValueError("bars are not strictly increasing in time")
    for i in range(len(ts)):
        yield ProbeBar(
            int(ts[i]), float(cols["open"][i]), float(cols["high"][i]), float(cols["low"][i]),
            float(cols["close"][i]), int(cols["volume"][i]), str(cols["trade_date"][i]),
            bool(cols["in_flatten_window"][i]), bool(cols["in_no_new_positions_window"][i]),
            bool(cols["in_scheduled_closure"][i]),
        )


def run_probe_loop(
    bars: Iterator[ProbeBar], on_bar: Callable[[ProbeBar], Sequence[OrderIntent]]
) -> list[tuple[int, OrderIntent]]:
    """Replay bars in order; collect (bar ts, intent) pairs. Nothing else."""
    collected: list[tuple[int, OrderIntent]] = []
    last_ts = -1
    for bar in bars:
        if bar.ts_event_ns <= last_ts:
            raise ValueError("out-of-order bar")
        last_ts = bar.ts_event_ns
        collected.extend((bar.ts_event_ns, intent) for intent in on_bar(bar))
    return collected


# The probe ran on the full series on 2026-09-17, before the holdout was sealed; April 2025
# is in the research slice, so the research file reproduces it.
PARQUET = "data/processed/MES/ohlcv-1m_MES_v_0_2025-04-01_2026-06-19_research.parquet"
MONTH_START = datetime(2025, 4, 1, tzinfo=UTC)
MONTH_END = datetime(2025, 5, 1, tzinfo=UTC)
COLUMNS = ["ts_event", "open", "high", "low", "close", "volume", "trade_date",
           "in_flatten_window", "in_no_new_positions_window", "in_scheduled_closure"]


def _ns(dt: datetime) -> int:
    return int(dt.timestamp()) * 1_000_000_000


def probe_loop(repeats: int = 5) -> dict:
    t0 = time.perf_counter()
    ds = pads.dataset(PARQUET)
    field = pads.field("ts_event")
    frame = ds.to_table(columns=COLUMNS,
                        filter=(field >= _ns(MONTH_START)) & (field < _ns(MONTH_END))).to_pandas()
    load_s = time.perf_counter() - t0

    counter = {"n": 0}

    def stub(bar):  # noqa: ANN001, ANN202 — probe stub, not a strategy: emits every 97th bar
        counter["n"] += 1
        if counter["n"] % 97:
            return ()
        built = xr.construct_intent(symbol="MES", side="buy", quantity_micros=1,
                                    ts_utc=bar.decision_ts_utc)
        return (built,)

    timings = []
    intents = 0
    for _ in range(repeats):
        counter["n"] = 0
        t = time.perf_counter()
        out = run_probe_loop(iter_probe_bars(frame), stub)
        timings.append(time.perf_counter() - t)
        intents = len(out)
    best = min(timings)
    return {"month": "2025-04", "bars": len(frame), "load_s": round(load_s, 4),
            "loop_s_best_of": repeats, "loop_s": round(best, 4),
            "bars_per_s": round(len(frame) / best), "intents_collected": intents}


def probe_account_day(days: int = 252, repeats: int = 200) -> dict:
    """One simulated account-year of pure rules-engine day steps."""
    d0 = date(2025, 4, 1)
    t = time.perf_counter()
    for r in range(repeats):
        state = xr.new_xfa_account()
        for i in range(days):
            pnl = 3_000 if (i + r) % 3 else -2_500
            state = xr.apply_realtime_mll(state, -4_000)
            state = xr.record_realized_pnl(state, pnl)
            state = xr.close_trading_day(state, d0 + timedelta(days=i), 1)
            xr.check_payout_request(state, xr.PayoutPath.STANDARD, 12_500)
    elapsed = time.perf_counter() - t
    steps = days * repeats
    return {"account_days": steps, "seconds": round(elapsed, 4),
            "us_per_account_day": round(1e6 * elapsed / steps, 2)}


def main() -> None:
    result = {"generated_utc": datetime.now(UTC).isoformat(),
              "loop": probe_loop(), "rules_account_day": probe_account_day()}
    print(json.dumps(result, indent=1))


if __name__ == "__main__":
    main()
