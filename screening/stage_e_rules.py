"""The Stage E rule set of the generalized engine (Stage E.2b Task 1; design D8, D9, D11.5).

``StageERules`` plugs into screening.stage_e_engine.run_engine. Every value comes from a frozen
file or a module constant (screening.stage_e_frozen, rules/): the caller passes only the legs'
frozen inputs, the member's window dates, the union of its legs' roll blackouts and the frozen
release calendar, all built by screening.stage_e_runner.

The structural refusals, in ``STAGE_E_REFUSAL_ORDER`` (the first that applies is recorded):
- engine_not_an_intent / strategy_construction_refusal / engine_malformed_intent: what the member
  returned is not a well-formed LegIntent;
- engine_intent_timestamp_mismatch: not stamped with this minute's decision time;
- engine_not_a_traded_leg: an order on a signal leg;
- engine_leg_missing_bar: the traded leg has no bar at this minute, or (opening exposure) any leg
  the member reads has none (D11.5: a member whose leg has no bar at a decision time does not
  trade; exits of an open position stay allowed, reading RR-1);
- engine_scheduled_closure: the bar lies in a scheduled closure;
- engine_flatten_window: rules/sessions.py says flat at the decision time (R-F1, R-F4: F is the
  earliest of the regular F, the CME early close minus 15 minutes and Topstep's schedule), or the
  bar's own flatten flag is set (the union of the two, reading RR-2);
- engine_no_new_positions: opening exposure where the session allows no new position;
- engine_not_a_window_date / engine_roll_blackout / engine_skipped_for_day: opening exposure on a
  date outside the member's window, on a roll-blackout date of any leg (D4 union), or on a date
  whose entry was skipped (D9.3 ruling 01:52, D9.12);
- engine_malformed_passive: a limit price off the leg's vendor tick grid or marketable against
  the decision bar's close;
- engine_second_leg_position: opening one traded leg while another holds or awaits exposure (one
  position at a time; the catalog has no two-leg position, K8 rule 5);
- member_product_cap_exceeded / member_lot_equivalent_cap_exceeded (rules/constraints.py, D9.5,
  D9.11);
- engine_entry_cap: the 21st entry of the product on its trade date (D9.3a);
- engine_min_hold: an exit or flip less than 2 full minutes after the position's last opening
  fill (D9.3b);
- engine_price_limit_reference_unavailable / price_limit_zone_no_entry: D9.7 on a hard-limit
  product (grains, livestock, equity): no prior-settlement proxy, or the price at or beyond a stop
  level. DCB-only products have no lock limit (ruling L-13), so D9.7 does not apply to them.
Then the gate: account_not_active, position_limit_exceeded (the XFA Scaling Plan in
lot-equivalents, which the 1-lot member cap keeps from ever binding).

At the fill (``admit_fill``):
- D9.5a fill guard: a strategy order whose fill would land in [release, release + 2 min) of a
  release concerning the leg waits for the first bar at or after release + 2 min. Forced flattens
  and D9.7 exits are exempt (conduct outranks fidelity, the 01:52 ruling's reasoning; RR-3).
- D9.12: an opening fill in [CPI - 5 min, CPI + 5 min] on NQ, RTY, YM, GC, SI, HG is skipped for
  the day; on MNQ, M2K, MYM, MGC, SIL, MHG one above 3 contracts is skipped for the day.
- D9.3 ruling 01:52: an opening fill whose forced exit (F, the grain pause) would come less than
  2 full minutes later is skipped for the day.
- R-08: an exit that must trade against a limit lock (hard-limit products) waits for a bar that
  trades through; a lock still holding when the session ends is refused by name
  (EngineRefusedCase "locked_exit_through_session_end"), a question for the user.
Costs: D8 per side, the event-window cost for any fill in [release, release + 30 min) and for
every D9.7 exit (T12-4 reading, screening.stage_e_frozen); a limit fill pays commission only.
"""

from __future__ import annotations

import functools
import json
from collections.abc import Iterator, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import UTC, date, datetime, time
from decimal import Decimal
from pathlib import Path
from types import MappingProxyType
from typing import Any

import numpy as np
import pandas as pd

from data.config import REPO_ROOT
from data.group_session import load_group_calendar, previous_trade_date
from rules import price_limits as pl
from rules import sessions
from rules import xfa_rules as xr
from rules.constraints import check_cpi_opening, check_member_size, lot_equivalents_tenths
from rules.products import PRICE_SCALE, product
from rules.xfa_rules import AccountState, Phase, Refusal, Status
from screening.stage_e_engine import (
    EVENT_WINDOW_NS,
    FILL_GUARD_NS,
    MAX_ENTRIES_PER_DAY,
    MIN_HOLD_NS,
    NS_PER_MINUTE,
    EngineInvariantError,
    EngineRefusedCase,
    _Normalized,
    _Order,
    _Run,
)
from screening.stage_e_frozen import LegInputs, sha256_file, slippage_cents
from sim.fill_model import FillCost
from strategy.interface import NS_PER_BAR, NS_PER_S, Bar
from strategy.stage_e.interface import LegIntent, MemberAccountView, MinuteView

if pl.DCB_READING_DEFAULT is not pl.DcbReading.NO_LOCK_LIMIT:  # ruling L-13 is what is encoded
    raise ImportError("rules.price_limits DCB reading changed from NO_LOCK_LIMIT; the engine's "
                      "D9.7 scope (hard-limit products only) would no longer match it")

RELEASE_CALENDAR_PATH = "reports/stage_e2b_release_calendar.json"
RELEASE_CALENDAR_SCHEMA = "stage_e_release_calendar/1"
STAGE_E_REFUSAL_ORDER = (
    "engine_not_an_intent", "strategy_construction_refusal", "engine_malformed_intent",
    "engine_intent_timestamp_mismatch", "engine_not_a_traded_leg", "engine_leg_missing_bar",
    "engine_scheduled_closure", "engine_flatten_window", "engine_no_new_positions",
    "engine_not_a_window_date", "engine_roll_blackout", "engine_skipped_for_day",
    "engine_malformed_passive", "engine_second_leg_position", "member_product_cap_exceeded",
    "member_lot_equivalent_cap_exceeded", "engine_entry_cap", "engine_min_hold",
    "engine_price_limit_reference_unavailable", "price_limit_zone_no_entry",
    "account_not_active", "position_limit_exceeded",
)


class ReleaseCalendarMissing(RuntimeError):
    """The frozen release calendar (D8 event window, D9.5a, D9.12) does not exist or is invalid."""


# ------------------------------------------------------------ release calendar ----
@dataclass(frozen=True)
class ReleaseCalendar:
    """Scheduled major releases that concern each product (D8: Topstep's release table F6.4 plus
    the releases the product's catalog members name) and the CPI instants (D9.12)."""

    by_root: Mapping[str, tuple[int, ...]]  # root -> sorted release instants, UTC ns
    cpi: tuple[datetime, ...]
    first: date
    last: date
    sha256: str
    source: str

    def _latest_at_or_before(self, root: str, ts_ns: int) -> int | None:
        arr = self.by_root.get(root, ())
        i = int(np.searchsorted(np.asarray(arr, dtype=np.int64), ts_ns, side="right")) - 1
        return None if i < 0 else int(arr[i])

    def in_event_window(self, root: str, ts_ns: int) -> bool:
        r = self._latest_at_or_before(root, ts_ns)
        return r is not None and ts_ns < r + EVENT_WINDOW_NS

    def in_fill_guard(self, root: str, ts_ns: int) -> bool:
        r = self._latest_at_or_before(root, ts_ns)
        return r is not None and ts_ns < r + FILL_GUARD_NS

    def covers(self, days: Sequence[date]) -> bool:
        return all(self.first <= d <= self.last for d in days)


def _instant_ns(text: str) -> int:
    dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        raise ReleaseCalendarMissing(f"release instant {text!r} is not timezone-aware")
    return int(dt.timestamp()) * NS_PER_S + dt.microsecond * 1000


def release_calendar_from_dict(raw: dict, sha256: str, source: str) -> ReleaseCalendar:
    if raw.get("schema") != RELEASE_CALENDAR_SCHEMA:
        raise ReleaseCalendarMissing(f"{source}: schema {raw.get('schema')!r} is not "
                                     f"{RELEASE_CALENDAR_SCHEMA!r}")
    by_root: dict[str, list[int]] = {}
    cpi: list[datetime] = []
    for entry in raw["releases"]:
        ns = _instant_ns(entry["instant_utc"])
        if ns % NS_PER_MINUTE:
            raise ReleaseCalendarMissing(f"{source}: {entry.get('id')} is not on a minute")
        for root in entry["products"]:
            product(root)  # an unknown root raises
            by_root.setdefault(root, []).append(ns)
        if entry.get("cpi", False):
            cpi.append(datetime.fromtimestamp(ns / NS_PER_S, tz=UTC))
    cov = raw["coverage"]
    return ReleaseCalendar(
        MappingProxyType({r: tuple(sorted(set(v))) for r, v in by_root.items()}),
        tuple(sorted(cpi)), date.fromisoformat(cov["first"]), date.fromisoformat(cov["last"]),
        sha256, source)


def load_release_calendar(root: Path = REPO_ROOT) -> ReleaseCalendar:
    """The frozen release calendar of the repository; refused by name when absent."""
    path = Path(root) / RELEASE_CALENDAR_PATH
    if not path.is_file():
        raise ReleaseCalendarMissing(
            f"{RELEASE_CALENDAR_PATH} does not exist: D8's event-window cost, D9.5a's fill guard "
            "and D9.12's CPI window cannot be applied without it (question for the lead: who "
            "builds and freezes it)")
    return release_calendar_from_dict(json.loads(path.read_text(encoding="utf-8")),
                                      sha256_file(path), RELEASE_CALENDAR_PATH)


# ------------------------------------------------------------------- bars ----
def product_bar_iterator(root: str) -> Any:
    """A frame -> Bar iterator that checks every row on the product's vendor tick grid (the MES
    construct_bar checks the 0.25 grid only)."""
    tick_fixed = product(root).vendor_tick_fixed

    def iterate(frame: pd.DataFrame) -> Iterator[Bar]:
        prices = {c: frame[c].to_numpy(dtype="float64") for c in ("open", "high", "low", "close")}
        for c, arr in prices.items():
            fixed = np.rint(arr * PRICE_SCALE).astype(np.int64)
            off = (fixed % tick_fixed != 0) | (np.abs(fixed / PRICE_SCALE - arr) > 1e-6)
            if off.any():
                i = int(np.flatnonzero(off)[0])
                raise EngineInvariantError(f"{root} row {i}: {c} {arr[i]} is off the vendor tick "
                                           f"grid ({tick_fixed} x 1e-9)")
        ts = frame["ts_event"].to_numpy(dtype="int64")
        if (ts % NS_PER_BAR).any():
            raise EngineInvariantError(f"{root}: a bar timestamp is not on a minute")
        o, h, lo, c = prices["open"], prices["high"], prices["low"], prices["close"]
        bad = (lo > np.minimum(o, c)) | (h < np.maximum(o, c)) | (lo > h)
        if bad.any():
            raise EngineInvariantError(f"{root} row {int(np.flatnonzero(bad)[0])}: OHLC "
                                       "inconsistent")
        vol = frame["volume"].to_numpy()
        if (vol < 0).any():
            raise EngineInvariantError(f"{root}: negative volume")
        cols = {k: frame[k].to_numpy() for k in (
            "instrument_id", "raw_symbol", "trade_date", "in_flatten_window",
            "in_no_new_positions_window", "early_halt_ct", "in_scheduled_closure",
            "is_roll_session", "gap_before_minutes", "vendor_degraded_day")}
        day_cache: dict[str, date] = {}
        for i in range(len(frame)):
            label = str(cols["trade_date"][i])
            day = day_cache.get(label)
            if day is None:
                day = day_cache[label] = date.fromisoformat(label)
            halt = str(cols["early_halt_ct"][i])
            yield Bar(int(ts[i]), float(o[i]), float(h[i]), float(lo[i]), float(c[i]),
                      int(vol[i]), int(cols["instrument_id"][i]), str(cols["raw_symbol"][i]), day,
                      bool(cols["in_flatten_window"][i]),
                      bool(cols["in_no_new_positions_window"][i]),
                      time.fromisoformat(halt) if halt else None,
                      bool(cols["in_scheduled_closure"][i]), bool(cols["is_roll_session"][i]),
                      int(cols["gap_before_minutes"][i]), bool(cols["vendor_degraded_day"][i]))

    return iterate


# ---------------------------------------------------------------- the rules ----
@functools.cache
def _calendar(group: str) -> Any:
    return load_group_calendar(group)


@dataclass
class _Settlement:
    """Per traded hard-limit leg: prior-settlement proxies, collected as bars stream."""

    root: str
    proxies: dict[date, Any] = field(default_factory=dict)
    day: date | None = None
    window: tuple[datetime, datetime] | None = None
    prints: list = field(default_factory=list)

    def finalize(self) -> None:
        if self.day is None or self.window is None:
            return
        proxy = pl.settlement_proxy(self.prints, *self.window)
        if proxy is not None:
            self.proxies[self.day] = proxy.value

    def add(self, bar: Bar) -> None:
        if bar.trade_date != self.day:
            self.finalize()
            self.day = bar.trade_date
            self.window = pl.settlement_window_utc(self.root, bar.trade_date)
            self.prints = []
        assert self.window is not None
        start = bar.open_ts_utc
        if start >= self.window[1]:
            return
        pr = pl.BarPrint(start, Decimal(repr(bar.close)), bar.volume)
        if start < self.window[0].replace(second=0, microsecond=0):
            # before the window only the latest print matters (the proxy's fallback, R-P2)
            self.prints = [p for p in self.prints if p.start >= self.window[0]
                           .replace(second=0, microsecond=0)] + [pr]
        else:
            self.prints.append(pr)


@dataclass(frozen=True)
class StageERules:
    """The Stage E constraint set for one member (built by screening.stage_e_runner)."""

    legs: Mapping[str, LegInputs]
    window_dates: frozenset[date]
    blackout: frozenset[date]  # the union of every leg's roll blackout (D4)
    releases: ReleaseCalendar
    restart_on_terminal: bool = True
    mask_hindsight_fields: bool = True
    phase: Phase = Phase.XFA

    skip_closure_bars = True  # OC-T: no fill or MLL mark ever uses a scheduled-closure print

    # -- units --------------------------------------------------------------
    def new_account(self) -> AccountState:
        return xr.new_xfa_account()

    def bar_iterator(self, root: str) -> Any:
        return product_bar_iterator(root)

    def tick_value(self, root: str) -> Any:
        return self.legs[root].tick_value_cents

    def price_ticks(self, root: str, price: float) -> int:
        tick_fixed = self.legs[root].product.vendor_tick_fixed
        fixed = round(price * PRICE_SCALE)
        if fixed % tick_fixed or abs(fixed / PRICE_SCALE - price) > 1e-6:
            raise EngineInvariantError(f"{root}: price {price} is off the vendor tick grid")
        return fixed // tick_fixed

    def ticks_price(self, root: str, ticks: int) -> float:
        return ticks * self.legs[root].product.vendor_tick_fixed / PRICE_SCALE

    def _traded(self, root: str) -> bool:
        return self.legs[root].costs is not None

    # -- per-minute observation (the D9.7 settlement proxies) -----------------
    def _settlements(self, run: _Run) -> dict[str, _Settlement]:
        store = run.__dict__.setdefault("_stage_e_settlements", {})
        if not store:
            for root in run.traded:
                if root in pl.HARD_LIMIT_PRODUCTS:
                    store[root] = _Settlement(root)
        return store

    def observe(self, run: _Run, ts: int, bars: Mapping[str, Bar]) -> None:
        for root, s in self._settlements(run).items():
            bar = bars.get(root)
            if bar is not None:
                s.add(bar)

    def prior_settlement(self, run: _Run, root: str, day: date) -> Any:
        s = self._settlements(run).get(root)
        if s is None:
            return None
        prev = previous_trade_date(_calendar(product(root).group), day)
        return None if prev is None else s.proxies.get(prev)

    # -- costs --------------------------------------------------------------
    def _market_cost(self, root: str, bar_open_utc: datetime, ts_ns: int, qty: int, side: str,
                     force_event: bool) -> tuple[FillCost, bool]:
        leg = self.legs[root]
        assert leg.costs is not None
        event = force_event or self.releases.in_event_window(root, ts_ns)
        slip = leg.costs.side_slippage_ticks(bar_open_utc, side, event)
        return FillCost(qty, qty * leg.costs.commission_side_cents,
                        slippage_cents(qty, slip, leg.tick_value_cents), slip,
                        "event" if event else "mean"), event

    def fill_cost(self, run: _Run, order: _Order, bar: Bar, qty: int, side: str, reason: str
                  ) -> tuple[FillCost, bool]:
        leg = self.legs[order.root]
        assert leg.costs is not None
        if order.is_passive:
            return FillCost(qty, qty * leg.costs.commission_side_cents, 0, 0.0, "passive"), False
        return self._market_cost(order.root, bar.open_ts_utc, bar.ts_event_ns, qty, side,
                                 reason == "price_limit_exit")

    def close_cost(self, run: _Run, root: str, bar: Bar, qty: int, side: str
                   ) -> tuple[FillCost, bool]:
        return self._market_cost(root, bar.open_ts_utc, bar.ts_event_ns, qty, side, False)

    # -- fill admission -----------------------------------------------------
    def _locked(self, run: _Run, order: _Order, bar: Bar) -> bool:
        root = order.root
        if root not in pl.HARD_LIMIT_PRODUCTS:
            return False
        s = self.prior_settlement(run, root, bar.trade_date)
        if s is None:
            return False  # no reference: a lock cannot be shown (reading RR-4)
        band = pl.limit_band(root, bar.trade_date, bar.open_ts_utc, s)
        up, down = pl.limit_prices(band, s)
        hi, lo = Decimal(repr(bar.high)), Decimal(repr(bar.low))
        if order.signed_qty < 0:
            return down is not None and hi <= down
        return up is not None and lo >= up

    def admit_fill(self, run: _Run, order: _Order, bar: Bar) -> str:
        root = order.root
        before = run.position[root].qty
        reducing = xr.is_reducing(before, order.signed_qty)
        if order.reason == "strategy" and self.releases.in_fill_guard(root, bar.ts_event_ns):
            run.count("fill_guard_deferral")
            return "defer"
        exits = before != 0 and (reducing or (before > 0) != (order.signed_qty > 0))
        if exits and self._locked(run, order, bar):
            run.count("locked_exit_deferral")
            return "defer_locked"
        if order.reason != "strategy" or reducing:
            return "fill"
        after = before + order.signed_qty
        flips = before != 0 and (after > 0) != (before > 0)
        opening = abs(after) if flips else abs(order.signed_qty)
        refusal = check_cpi_opening(root, bar.open_ts_utc, opening, self.releases.cpi)
        if refusal is not None:
            run.skipped_today.add(root)
            return f"cpi_skip:{refusal.reason}"
        for probe in (bar.ts_event_ns, bar.ts_event_ns + NS_PER_MINUTE):
            state = sessions.session_state(root, datetime.fromtimestamp(probe / NS_PER_S, tz=UTC))
            if state.must_be_flat:
                run.skipped_today.add(root)
                return "entry_skipped_min_hold_before_flatten"
        return "fill"

    def before_session_change(self, run: _Run) -> None:
        locked = sorted({o.root for o in run.pending if o.locked_waits})
        if locked:
            raise EngineRefusedCase(f"locked_exit_through_session_end: {locked} exit still locked "
                                    f"at the end of {run.trade_date}")

    def passive_no_new(self, run: _Run, root: str, bar: Bar) -> bool:
        if bar.in_no_new_positions_window:
            return True
        return not sessions.session_state(root, bar.open_ts_utc).can_open

    # -- forced exits -------------------------------------------------------
    def forced_reasons(self, run: _Run, root: str, bar: Bar) -> tuple[str, ...]:
        exposure = run.exposure(root)
        if not exposure:
            return ()
        if bar.in_flatten_window or sessions.required_flatten(root, exposure,
                                                              bar.decision_ts_utc) is not None:
            return ("forced_flatten",)
        if root in pl.HARD_LIMIT_PRODUCTS and run.position[root].qty:
            s = self.prior_settlement(run, root, bar.trade_date)
            if s is not None and pl.required_price_limit_exit(
                    root, bar.trade_date, bar.decision_ts_utc, run.position[root].qty, s,
                    Decimal(repr(bar.close))) is not None:
                return ("price_limit_exit",)
        return ()

    # -- the member ---------------------------------------------------------
    def account_view(self, run: _Run) -> MemberAccountView:
        avg = {}
        for r, pos in run.position.items():
            q = pos.qty
            avg[r] = None if q == 0 else self.ticks_price(r, 1) * pos.basis_ticks / q
        return MemberAccountView(
            phase=run.state.phase, status=run.state.status, trade_date=run.trade_date,
            balance_cents=run.state.balance_cents, mll_floor_cents=run.state.mll_floor_cents,
            positions=MappingProxyType({r: p.qty for r, p in run.position.items()}),
            pending=MappingProxyType({r: run.pending_signed(r) for r in run.traded}),
            avg_entry_price=MappingProxyType(avg),
            entries_today=MappingProxyType(dict(run.entries_today)))

    def call_member(self, run: _Run, ts: int, bars: Mapping[str, Bar]) -> Sequence[Any]:
        view = MinuteView(ts, MappingProxyType({r: run.visible(bars.get(r)) for r in run.read}))
        return run.member.on_minute(view, self.account_view(run))

    def received_repr(self, item: Any, norm: _Normalized | None) -> str:
        return repr(item)

    def normalize(self, run: _Run, item: Any, ts: int, bars: Mapping[str, Bar]
                  ) -> tuple[_Normalized | None, Refusal | None]:
        if isinstance(item, Refusal):
            return None, Refusal("strategy_construction_refusal",
                                 f"{item.reason}: {item.arithmetic}")
        if not isinstance(item, LegIntent):
            return None, Refusal("engine_not_an_intent", f"member returned {type(item).__name__}")
        if item.side not in xr.SIDES or item.root not in run.read:
            return None, Refusal("engine_malformed_intent",
                                 f"root {item.root!r} / side {item.side!r} is not a leg order")
        if isinstance(item.quantity, bool) or not isinstance(item.quantity, int) or \
                item.quantity <= 0:
            return None, Refusal("engine_malformed_intent",
                                 f"quantity {item.quantity!r} is not a positive integer")
        if item.limit_price is not None and (
                isinstance(item.ttl_bars, bool) or not isinstance(item.ttl_bars, int)
                or item.ttl_bars <= 0):
            return None, Refusal("engine_malformed_intent", f"ttl {item.ttl_bars!r} is invalid")
        return _Normalized(item.root, item.signed_quantity, item.ts_utc, item.limit_price,
                           item.ttl_bars, None), None

    def _opens(self, run: _Run, norm: _Normalized) -> bool:
        return not xr.is_reducing(run.exposure(norm.root), norm.signed_qty)

    def structural_refusal(self, run: _Run, norm: _Normalized, ts: int,
                           bars: Mapping[str, Bar]) -> Refusal | None:
        decision = datetime.fromtimestamp((ts + NS_PER_BAR) / NS_PER_S, tz=UTC)
        root = norm.root
        if norm.ts_utc != decision:
            return Refusal("engine_intent_timestamp_mismatch",
                           f"intent ts {norm.ts_utc.isoformat()} != decision "
                           f"{decision.isoformat()}")
        if root not in run.traded:
            return Refusal("engine_not_a_traded_leg", f"{root} is a signal leg")
        opens = self._opens(run, norm)
        bar = bars.get(root)
        missing = [r for r in run.read if r not in bars]
        if bar is None or (opens and missing):
            return Refusal("engine_leg_missing_bar",
                           f"no bar at {datetime.fromtimestamp(ts / NS_PER_S, tz=UTC).isoformat()}"
                           f" for {missing or [root]}")
        if bar.in_scheduled_closure:
            return Refusal("engine_scheduled_closure", f"{root} bar {ts} is in a closure")
        state = sessions.session_state(root, decision)
        if bar.in_flatten_window or state.must_be_flat:
            return Refusal("engine_flatten_window", f"{root} at {decision.isoformat()}: "
                           f"{state.reason if state.must_be_flat else 'bar flatten flag'}")
        if opens and (bar.in_no_new_positions_window or not state.can_open):
            return Refusal("engine_no_new_positions", f"{root}: {state.reason}")
        if opens:
            refusal = self._opening_refusal(run, norm, bar, decision)
            if refusal is not None:
                return refusal
        return self._exit_refusal(run, norm, ts + NS_PER_BAR)

    def _opening_refusal(self, run: _Run, norm: _Normalized, bar: Bar,
                         decision: datetime) -> Refusal | None:
        root, day = norm.root, bar.trade_date
        if day not in self.window_dates:
            return Refusal("engine_not_a_window_date", f"{day} is not a window date")
        if day in self.blackout:
            return Refusal("engine_roll_blackout", f"{day} is a roll-blackout date of a leg")
        if root in run.skipped_today:
            return Refusal("engine_skipped_for_day", f"{root}: an entry was skipped on {day}")
        if norm.limit_price is not None:
            try:
                self.price_ticks(root, norm.limit_price)
            except EngineInvariantError as exc:
                return Refusal("engine_malformed_passive", str(exc))
            marketable = (norm.limit_price >= bar.close if norm.signed_qty > 0
                          else norm.limit_price <= bar.close)
            if marketable:
                return Refusal("engine_malformed_passive",
                               f"limit {norm.limit_price} is marketable against close {bar.close}")
        others = [r for r in run.traded if r != root and run.exposure(r)]
        if others:
            return Refusal("engine_second_leg_position", f"{others} already hold exposure")
        after = {r: run.exposure(r) for r in run.traded}
        after[root] += norm.signed_qty
        cap = check_member_size(after)
        if cap is not None:
            return cap
        pending_open = sum(1 for o in run.pending if o.root == root and o.reason == "strategy"
                           and not xr.is_reducing(run.position[root].qty, o.signed_qty))
        if run.entries_today.get(root, 0) + pending_open >= MAX_ENTRIES_PER_DAY:
            return Refusal("engine_entry_cap", f"{root}: {MAX_ENTRIES_PER_DAY} entries already "
                           f"on {day}")
        if root in pl.HARD_LIMIT_PRODUCTS:
            s = self.prior_settlement(run, root, day)
            if s is None:
                return Refusal("engine_price_limit_reference_unavailable",
                               f"{root}: no prior-settlement proxy for {day}")
            refusal = pl.check_price_limit_entry(root, day, decision, s, Decimal(repr(bar.close)))
            if refusal is not None:
                return refusal
        return None

    def _exit_refusal(self, run: _Run, norm: _Normalized, decision_ns: int) -> Refusal | None:
        pos = run.position[norm.root].qty
        if pos == 0 or (pos > 0) == (norm.signed_qty > 0):
            return None
        last = run.last_open_fill_ns.get(norm.root)
        if last is not None and decision_ns < last + MIN_HOLD_NS:
            return Refusal("engine_min_hold", f"{norm.root}: exit decided "
                           f"{(decision_ns - last) // NS_PER_S} s after the opening fill")
        return None

    def gate(self, run: _Run, norm: _Normalized, ts: int, bars: Mapping[str, Bar]
             ) -> Refusal | None:
        if run.state.status is not Status.ACTIVE:
            return Refusal("account_not_active", f"status {run.state.status.value}")
        if not self._opens(run, norm):
            return None
        after = {r: run.exposure(r) for r in run.traded}
        after[norm.root] += norm.signed_qty
        tenths = lot_equivalents_tenths(after)
        limit = xr.max_position_micros(run.state.phase, run.state.session_start_balance_cents)
        if tenths > limit:  # max_position_micros is minis x 10: tenths of a lot
            return Refusal("position_limit_exceeded", f"{tenths / 10:.1f} lots > {limit / 10}")
        return None


__all__ = [
    "RELEASE_CALENDAR_PATH", "RELEASE_CALENDAR_SCHEMA", "STAGE_E_REFUSAL_ORDER",
    "ReleaseCalendar", "ReleaseCalendarMissing", "StageERules", "load_release_calendar",
    "product_bar_iterator", "release_calendar_from_dict",
]
