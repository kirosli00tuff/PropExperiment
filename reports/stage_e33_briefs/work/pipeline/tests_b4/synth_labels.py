"""Run Coder-A's (pipeline/lab33.py) and Coder-B's (implB/labB*.py) label code on one synthetic ZM MBO stream and
return both INTERFACE 4.2 tables. Synthetic data only. Both get the same day context (releases, limits, exclusion,
sigma_ZM); A takes limits in fixed point, B in ticks (each module's own convention); both replay the records with
ts_recv < 13:20:00 CT, as their builders do."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from datetime import date, time
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
PIPE = HERE.parent
IMPLB = PIPE.parent / "implB"
for p in (str(PIPE), str(IMPLB), str(HERE)):
    if p not in sys.path:
        sys.path.insert(0, p)

import lab33  # noqa: E402
import labB  # noqa: E402
import labB_book  # noqa: E402

from synth_streams import TICK_FP, ct_ns  # noqa: E402

LABELS = ("F05", "F15", "F30", "F60", "T15", "T30")


@dataclass(frozen=True)
class SynthCtx:
    day: date
    iid: int
    releases_ns: tuple[int, ...] = ()
    limits_ticks: tuple[int, int] | None = None
    excluded: bool = False
    sigma_ticks: float | None = 3.15


def _cut(arr: np.ndarray, day: date) -> np.ndarray:
    stop = ct_ns(day, 13, 20)
    return arr[arr["ts_recv"] < stop]


def run_a(arr: np.ndarray, ctx: SynthCtx, labels: tuple[str, ...] = LABELS) -> dict[str, pd.DataFrame]:
    tick = TICK_FP["ZM"]
    rec = _cut(arr, ctx.day)
    hist = lab33.replay(rec, ctx.iid, tick, end_ns=ct_ns(ctx.day, 13, 20) - 1)
    lim = None if ctx.limits_ticks is None else (ctx.limits_ticks[0] * tick, ctx.limits_ticks[1] * tick)
    day = lab33.DayInputs(
        date=ctx.day.isoformat(), t0_ns=ct_ns(ctx.day, 8, 35), close_ns=ct_ns(ctx.day, 13, 13),
        session_end_ns=ct_ns(ctx.day, 13, 20), releases=tuple(ctx.releases_ns), limits=lim, tick=tick,
        excluded=ctx.excluded, sigma_zm=ctx.sigma_ticks)
    out = {}
    for lab in labels:
        cols, _excl = lab33.compute_label(hist, day, lab)
        out[lab] = pd.DataFrame({k: cols[k] for k in cols})
    return out


def run_b(arr: np.ndarray, ctx: SynthCtx, labels: tuple[str, ...] = LABELS) -> dict[str, pd.DataFrame]:
    rec = _cut(arr, ctx.day)
    upd, _counts = labB_book.front_updates(rec, ctx.iid, TICK_FP["ZM"])
    c = labB.DayContext(day=ctx.day, excluded=ctx.excluded, releases_ns=tuple(ctx.releases_ns),
                        limits=ctx.limits_ticks, sigma_ticks=ctx.sigma_ticks)
    out = {}
    for lab in labels:
        cols, _excl = labB.label_table(upd, c, lab, burn_in=False)
        out[lab] = pd.DataFrame({k: cols[k] for k in cols})
    return out


def _unused_time() -> time:  # keeps the datetime.time import explicit for readers of ct_ns
    return time(8, 35)
