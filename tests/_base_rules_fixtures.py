"""Synthetic fixtures of the base_rules tests (Stage E.16 Task 3): no market data anywhere.

- hand-built hist calendars in data.hist_calendar's schema (parsed by the frozen parser);
- settlement tables in Task 1's schema;
- ProductBars built directly from (day, CT minute, open, close, contract) rows;
- stores written in the real ext2010 / step 2 layout by the frozen read-only parquet writer.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable, Mapping, Sequence
from datetime import date, time
from pathlib import Path

import numpy as np
import pandas as pd

from base_rules import constants as K
from base_rules import hist_plan as HP
from base_rules.auctions import Auction
from base_rules.calendars import GroupCalendars
from base_rules.context import empty_release_rules, make_context
from base_rules.inputs import settlement_from_dict
from base_rules.store import ProductBars, Splice, step2_name
from data.group_session import load_group_calendar
from data.hist_calendar import parse_hist_calendar
from data.session import ct_ns
from rules.products import PRICE_SCALE, product

SM = {"equity": (15 * 60, 8 * 60 + 30), "rates": (14 * 60, 7 * 60 + 20),
      "fx": (14 * 60, 7 * 60 + 20), "energy": (13 * 60 + 30, 8 * 60),
      "metals": (12 * 60 + 30, 7 * 60 + 20), "grains": (13 * 60 + 15, 8 * 60 + 30),
      "livestock": (13 * 60, 8 * 60 + 30)}


def ns(day: date, minute: int) -> int:
    return ct_ns(day, time(minute // 60, minute % 60))


def hm(minute: int) -> str:
    return f"{minute // 60:02d}:{minute % 60:02d}"


# ------------------------------------------------------------------ calendars ----
def hist_payload(group: str, *, entries: Sequence[dict] = (), unsourced: Sequence[date] = (),
                 segments: Sequence[dict] | None = None,
                 day_session: Mapping[str, tuple[str, str]] | None = None) -> dict:
    """A minimal valid e14_hist_calendar/1 file: one session spec, every year covered."""
    from data.calendars import GROUP_OF_PRODUCT

    products = [p for p, g in GROUP_OF_PRODUCT.items() if g == group]
    s, o = SM[group]
    day_session = day_session or {p: (hm(o), hm(s + 5)) for p in products}
    segments = segments or [{"start_offset_days": -1, "start_ct": "17:00",
                             "end_offset_days": 0, "end_ct": "16:00"}]
    return {
        "schema": "e14_hist_calendar/1", "group": group, "products": products,
        "cme_row_labels": ["synthetic"],
        "coverage": {"first": "2010-06-01", "last": "2019-05-31"},
        "sessions": [{"valid_from": "2010-06-01", "valid_to": "2019-05-31",
                      "segments": list(segments),
                      "day_session_ct": {k: list(v) for k, v in day_session.items()},
                      "evidence": "cme", "source": "synthetic", "note": ""}],
        "entries": list(entries), "no_entry_findings": [],
        "year_coverage": [{"year": y, "documents": [], "complete_exception_list": True,
                           "evidence": "cme"} for y in range(2010, 2020)],
        "unsourced": [{"day": str(d), "reason": "synthetic"} for d in unsourced],
        "sources": {}, "counts": {},
    }


def closure(day: date, name: str = "closed") -> dict:
    return {"day": str(day), "name": name, "kind": "full_closure", "halt_ct": None,
            "open_ct": None, "evidence": "cme", "time_evidence": "n/a", "source": "s",
            "status_quote": "q", "time_quote": None, "note": ""}


def early_halt(day: date, halt: str = "12:00") -> dict:
    return {"day": str(day), "name": "early close", "kind": "early_halt", "halt_ct": halt,
            "open_ct": None, "evidence": "cme", "time_evidence": "cme", "source": "s",
            "status_quote": "q", "time_quote": "t", "note": ""}


def group_calendars(group: str, payload: dict | None = None) -> GroupCalendars:
    raw = json.dumps(payload or hist_payload(group)).encode()
    hist = parse_hist_calendar(raw, group, Path(f"/synthetic/{group}.json"))
    return GroupCalendars(group, hist, load_group_calendar(group))


def calendars(groups: Iterable[str], payloads: Mapping[str, dict] | None = None
              ) -> dict[str, GroupCalendars]:
    return {g: group_calendars(g, (payloads or {}).get(g)) for g in groups}


# ------------------------------------------------------------------ settlement ----
def settlement_payload(overrides: Mapping[str, Sequence[dict]] | None = None,
                       opens: Mapping[str, Sequence[dict]] | None = None) -> dict:
    products = {}
    for p in K.PRODUCTS:
        s, o = SM[K.GROUP_OF[p]]
        settle = (overrides or {}).get(p) or [
            {"from": str(K.PROMPT_FIRST), "to": str(K.WINDOW_LAST), "minute_ct": hm(s),
             "grade": "primary", "lead_grade": "primary"}]
        day_open = (opens or {}).get(p) or [
            {"from": str(K.PROMPT_FIRST), "to": str(K.WINDOW_LAST), "minute_ct": hm(o),
             "grade": "primary"}]
        products[p] = {"group": K.GROUP_OF[p], "settle": list(settle), "day_open": list(day_open)}
    return {"schema": K.SETTLEMENT_SCHEMA, "window": [str(K.PROMPT_FIRST), str(K.WINDOW_LAST)],
            "products": products}


def settlement(**kw):
    raw = settlement_payload(**kw)
    return settlement_from_dict(raw, "0" * 64, "synthetic")


# ------------------------------------------------------------------ bars ----
def make_bars(root: str, rows: Sequence[tuple], splices: Sequence[tuple[int, date]] = (),
              blackout: Iterable[date] = (), extra: Mapping[tuple, dict] | None = None
              ) -> ProductBars:
    """rows: (trade date, CT minute, open ticks, close ticks, contract[, usable]); ``extra``:
    (trade date, minute) -> {"high", "low", "volume", "no_new"} (defaults: max and min of open
    and close, volume 1, not in the no-new-positions window)."""
    rows = sorted(rows, key=lambda r: ns(r[0], r[1]))
    symbols = sorted({r[4] for r in rows})
    code = {s: i for i, s in enumerate(symbols)}
    ex = [(extra or {}).get((r[0], r[1]), {}) for r in rows]
    return ProductBars(
        root=root, ts=np.array([ns(r[0], r[1]) for r in rows], dtype=np.int64),
        open_t=np.array([r[2] for r in rows], dtype=np.int64),
        close_t=np.array([r[3] for r in rows], dtype=np.int64),
        sym=np.array([code[r[4]] for r in rows], dtype=np.int32), symbols=tuple(symbols),
        usable=np.array([r[5] if len(r) > 5 else True for r in rows], dtype=bool),
        td=np.array([r[0].toordinal() for r in rows], dtype=np.int64),
        splices=tuple(Splice(t, d) for t, d in splices), blackout=frozenset(blackout),
        records=(),
        high_t=np.array([e.get("high", max(r[2], r[3])) for r, e in zip(rows, ex, strict=True)],
                        dtype=np.int64),
        low_t=np.array([e.get("low", min(r[2], r[3])) for r, e in zip(rows, ex, strict=True)],
                       dtype=np.int64),
        volume=np.array([e.get("volume", 1) for e in ex], dtype=np.int64),
        no_new=np.array([e.get("no_new", False) for e in ex], dtype=bool))


def context(cals: Mapping[str, GroupCalendars], bars: Mapping[str, ProductBars], *,
            st=None, starts: Mapping[str, date] | None = None,
            auctions: Sequence[Auction] = (), releases=None):
    return make_context(cals, st or settlement(), {**K.WINDOW_START, **(starts or {})},
                        lambda p: bars[p], tuple(auctions), releases or empty_release_rules())


def trade_dates(cal: GroupCalendars, first: date, last: date) -> list[date]:
    return [d for d in cal.trade_dates() if first <= d <= last]


# ------------------------------------------------------------------ worlds ----
def intraday_world(root: str, dates: Sequence[date], *, h1_edge: float, h4_edge: float,
                   noise: float, seed: int, symbol: str = "C1", base: int = 100000
                   ) -> ProductBars:
    """Bars at O+1, S-31, S-30, S-1, S on each date (module docstring of base_rules.intraday):
    the H1 window move is sign(x) * h1_edge + noise, x the move from PS(d-1) to S-31; the H4
    move from O+1 to S-31 is -sign(prior window move) * h4_edge + noise."""
    s, o = SM[K.GROUP_OF[root]]
    rng = np.random.default_rng(seed)
    rows, ps, w_prev = [], base, 0
    for d in dates:
        a = int(rng.integers(-30, 31))
        o1 = ps + a
        r = int(round(-np.sign(w_prev) * h4_edge + rng.normal(0, noise)))
        o31 = o1 + r  # H4's exit price (the open of bar S-31)
        c31 = o31 + int(rng.integers(-3, 4))
        x = c31 - ps
        w = int(round(np.sign(x) * h1_edge + rng.normal(0, noise)))
        s_open = c31 + w
        rows += [(d, o + 1, o1, o1, symbol), (d, s - 31, o31, c31, symbol),
                 (d, s - 30, c31, c31, symbol), (d, s - 1, s_open, s_open, symbol),
                 (d, s, s_open, s_open, symbol)]
        ps, w_prev = s_open, w
    return make_bars(root, rows)


def level_rows(root: str, levels: Mapping[date, int], minutes: Sequence[int], symbol="C1"
               ) -> list[tuple]:
    return [(d, m, lv, lv, symbol) for d, lv in levels.items() for m in minutes]


# ------------------------------------------------------------------ stores ----
def store_frame(root: str, cal_rows: Sequence[tuple[int, str, str, int]]) -> pd.DataFrame:
    """BAR_COLUMNS rows: (ts_ns, trade date label, raw symbol, close ticks)."""
    tick = product(root).vendor_tick_fixed / PRICE_SCALE
    px = np.array([r[3] for r in cal_rows], dtype=float) * tick
    return pd.DataFrame({
        "ts_event": np.array([r[0] for r in cal_rows], dtype=np.int64),
        "open": px, "high": px, "low": px, "close": px,
        "volume": np.ones(len(cal_rows), dtype=np.int64),
        "instrument_id": np.ones(len(cal_rows), dtype=np.int64),
        "raw_symbol": [r[2] for r in cal_rows], "trade_date": [r[1] for r in cal_rows],
        "in_flatten_window": False, "in_no_new_positions_window": False, "early_halt_ct": "",
        "in_scheduled_closure": False, "is_roll_session": False, "gap_before_minutes": 0,
        "vendor_degraded_day": False})


def write_store(base: Path, root: str, era: str, frame: pd.DataFrame, meta: dict,
                plan: str | None = None, first: date = K.PROMPT_FIRST) -> tuple[Path, str]:
    """The real layouts: <base>/<plan>/<ROOT>/..._<first>_2019-04-30_<plan>.parquet (hist) and
    <base>/step2/<ROOT>/..._step2.parquet."""
    from data.build_mes_bars import _write_read_only_parquet

    out = (Path(base) / str(plan) / root / HP.expected_name(root, str(plan), first, K.HIST_LAST)
           if era == "ext2010" else Path(base) / "step2" / root / step2_name(root))
    _write_read_only_parquet(frame, out, meta)
    return out, hashlib.sha256(out.read_bytes()).hexdigest()


def store_rows(root: str, cal, days: Sequence[date], minutes: Sequence[int],
               symbol_at, price_at) -> list[tuple[int, str, str, int]]:
    """Rows on ``days`` at CT ``minutes``, booked by the frozen booking (data.stage_e_bars)."""
    from data.stage_e_bars import book_trade_dates

    ts = np.array([ns(d, m) for d in days for m in minutes], dtype=np.int64)
    booked = book_trade_dates(cal, ts)
    return [(int(t), str(b), symbol_at(int(t)), price_at(int(t))) for t, b in zip(ts, booked,
                                                                                    strict=True)]



__all__ = [n for n in dir() if not n.startswith("_")]
