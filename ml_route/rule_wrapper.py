"""A distilled route rule as a Strategy the engine runs (M5, M7.7).

INTERFACE (for CanaryCoder and the Stage E runner; stable):

    spec = rule_spec_from_json(rule_json)            # verifies rule_json["rule_sha256"]
    strat = DistilledRuleStrategy(spec, product, cost, times, blackout, releases, cpi,
                                  lead=LeadSpec(...) for a non-lead leg, None for the lead leg,
                                  quantity_micros=1)
    strat.observe_lead(lead_bar)   # every bar of the cluster's F16 lead, in any order, any time
    intents = strat.on_bar(bar, account)             # strategy.interface.Strategy protocol
    strat.decisions                                  # audit trail: one Decision per decision time

- ``spec``: a RuleSpec (conditions on F1-F17 with float64 cut points, the sign, the horizon).
- ``product`` (ml_route.inputs.ProductSpec) and ``cost`` (the vehicle's VehicleCost): the leg.
- ``times``: {trade date: DayTimes} for the leg (ml_route.inputs.day_times; frozen sessions).
- ``blackout``: the leg's roll-blackout trade dates; ``releases`` / ``cpi``: int64 UTC ns.

Timing, identical to the training rows (M4): the decision at t acts on the bar OPENING at t
(the engine calls ``on_bar`` for it at t + 1 minute), reads only bars that CLOSED at or before t
(every earlier bar, never the current one), and its market intent fills at the open of the bar at
t + 1 minute. The exit intent is emitted on the bar whose decision time is the exit time
(t + h, or F_X), so it fills at the open of the bar at the exit time; the engine's forced flatten
at F covers the rest. A decision is skipped while the leg's position (or a pending order) is open
(M4's one-open-position rule) and when any feature is missing (ML-A05). Features are computed by
the training pipeline's own code (ml_route.features / ml_route.rows) on the history this object
has seen, restricted to the current date's decision grid, and checked by M7.1's validator.

Cross-product (F16): ``observe_lead`` appends lead bars to a separate history. At decision time t
the lead history is FILTERED to bars that closed at or before t before anything reads it, so a
lead bar handed over early (or a planted future lead bar) cannot change a decision.

Cost of the simple design: each decision rebuilds the features from the whole history
(quadratic in the number of bars); fine for canaries and a few hundred dates, to be revisited if
E.ML-test's runtime needs it.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date

import numpy as np

from ml_route.constants import (
    CLUSTER_OF,
    F17_MEDIAN_DATES,
    HORIZON_MINUTES,
    HORIZONS,
    LEAD_OF_CLUSTER,
    SIGMA_LOOKBACK_DATES,
)
from ml_route.features import Bars, Daily, LeadContext, build_daily
from ml_route.inputs import DayTimes, ProductSpec, VehicleCost
from ml_route.ledger import canonical, sha256_bytes
from ml_route.rows import build_rows, validate_availability
from ml_route.surrogate import condition_mask

NS_MIN = 60_000_000_000
# F17 at a date needs sigma on the 120 dates ending there, the first of which needs 20 complete
# dates before it: no date at position < 139 of the leg's history can have every feature.
FIRST_F17_POSITION = SIGMA_LOOKBACK_DATES + F17_MEDIAN_DATES - 1


class RuleIntegrityError(ValueError):
    """The rule JSON does not hash to its recorded rule_sha256."""


@dataclass(frozen=True)
class RuleSpec:
    conditions: tuple[tuple[str, str, float], ...]
    sign: int
    horizon: str
    rule_sha256: str


def rule_spec_from_json(rule: Mapping) -> RuleSpec:
    body = {k: v for k, v in rule.items() if k != "rule_sha256"}
    if sha256_bytes(canonical(body)) != rule.get("rule_sha256"):
        raise RuleIntegrityError("the rule JSON was changed after it was hashed")
    if rule["horizon"] not in HORIZONS or rule["sign"] not in (1, -1):
        raise ValueError(f"bad rule: horizon {rule['horizon']!r}, sign {rule['sign']!r}")
    conds = tuple((c["feature"], c["op"], float(c["cut"])) for c in rule["conditions"])
    return RuleSpec(conds, int(rule["sign"]), rule["horizon"], rule["rule_sha256"])


@dataclass(frozen=True)
class LeadSpec:
    root: str
    per_unit: float  # the lead's vehicle ticks per vendor price unit
    product: ProductSpec
    times: Mapping[date, DayTimes]


@dataclass(frozen=True)
class Decision:
    t_ns: int
    features_complete: bool
    fired: bool
    acted: bool  # an intent was emitted (fired, flat and nothing pending)
    trade_date: date | None = None  # the decision bar's trade date


_EPOCH_ORDINAL = date(1970, 1, 1).toordinal()
_FIELDS = ("ts", "o", "h", "lo", "c", "v", "inst", "day")


class _History:
    """Append-only bar history in growing numpy arrays (amortized doubling)."""

    def __init__(self) -> None:
        self.n = 0
        self._a = {f: np.empty(1024, dtype=np.int64 if f in ("ts", "inst", "day") else np.float64)
                   for f in _FIELDS}
        self.dates: list[date] = []  # distinct trade dates, in arrival order

    def add(self, bar) -> None:  # noqa: ANN001 - strategy.interface.Bar
        if not self.dates or self.dates[-1] != bar.trade_date:
            self.dates.append(bar.trade_date)
        if self.n == len(self._a["ts"]):
            self._a = {f: np.concatenate([a, np.empty_like(a)]) for f, a in self._a.items()}
        i = self.n
        a = self._a
        a["ts"][i], a["o"][i], a["h"][i] = int(bar.ts_event_ns), float(bar.open), float(bar.high)
        a["lo"][i], a["c"][i], a["v"][i] = float(bar.low), float(bar.close), float(bar.volume)
        a["inst"][i] = int(bar.instrument_id)
        a["day"][i] = bar.trade_date.toordinal() - _EPOCH_ORDINAL
        self.n += 1

    def bars(self, root: str, closed_by_ns: int | None = None) -> Bars:
        a = {f: arr[:self.n] for f, arr in self._a.items()}
        ts = a["ts"]
        order = (np.arange(self.n) if self.n < 2 or np.all(np.diff(ts) > 0)
                 else np.argsort(ts, kind="stable"))
        keep = order if closed_by_ns is None else order[ts[order] + NS_MIN <= closed_by_ns]
        return Bars(root, ts[keep], a["o"][keep], a["h"][keep], a["lo"][keep], a["c"][keep],
                    a["v"][keep], a["inst"][keep], a["day"][keep].astype("datetime64[D]"))


class DistilledRuleStrategy:
    """One leg of a distilled route rule (see the module docstring for the interface)."""

    def __init__(self, spec: RuleSpec, product: ProductSpec, cost: VehicleCost,
                 times: Mapping[date, DayTimes], blackout: frozenset[date],
                 releases: np.ndarray, cpi: np.ndarray, lead: LeadSpec | None = None,
                 quantity_micros: int = 1) -> None:
        if product.vehicle is None:
            raise ValueError(f"{product.root} has no vehicle; a route rule cannot trade it")
        self.name = f"route_rule_{spec.rule_sha256[:12]}_{product.root}"
        self.spec = spec
        self.product = product
        self.cost = cost
        self.times = dict(times)
        self.blackout = frozenset(blackout)
        self.releases = np.asarray(releases, dtype=np.int64)
        self.cpi = np.asarray(cpi, dtype=np.int64)
        self.lead = lead
        self.qty = quantity_micros
        self.decisions: list[Decision] = []
        self._own = _History()
        self._lead = _History()
        self._exit_ts: int | None = None
        self._daily: Daily | None = None
        self._daily_key: date | None = None
        self._lead_daily: Daily | None = None
        self._lead_key: tuple | None = None
        lead_root = LEAD_OF_CLUSTER[CLUSTER_OF[product.root]]
        if lead is None and lead_root != product.root:
            raise ValueError(f"{product.root}: F16 reads the cluster lead {lead_root}; pass it")
        if lead is not None and lead.root != lead_root:
            raise ValueError(f"{product.root}: the F16 lead is {lead_root}, not {lead.root}")

    def observe_lead(self, bar) -> None:  # noqa: ANN001 - strategy.interface.Bar
        self._lead.add(bar)

    def _features(self, t_ns: int, day: date) -> np.ndarray | None:
        seen = self._own.dates
        pos_guess = len(seen) - 1 if seen and seen[-1] == day else len(seen)
        if pos_guess < FIRST_F17_POSITION:
            return None  # exact: F17 needs 120 sigmas, each 20 complete dates, so it is missing
        bars = self._own.bars(self.product.root)
        if self._daily_key != day:  # once per trade date: Daily reads earlier dates only
            times = {d: self.times[d] for d in np.unique(bars.trade_date).astype(object).tolist()}
            self._daily = build_daily(bars, self.product, times)
            self._daily_key = day
        daily = self._daily
        pos = daily.pos_of(np.datetime64(day))
        if pos < FIRST_F17_POSITION:
            return None
        lead_ctx = self._lead_context(t_ns, bars)
        table = build_rows(bars, daily, self.product, self.cost, self.blackout, self.releases,
                           self.cpi, lead_ctx, only_date_pos=pos)
        hit = np.flatnonzero(table.t_ns == t_ns)
        if hit.size == 0:
            return None
        validate_availability(table)
        return table.X[hit[0]]

    def _lead_context(self, t_ns: int, own: Bars) -> LeadContext | None:
        if self.lead is None:  # the leg is its cluster's lead: F16 reads its own bars
            return LeadContext(self.product.root, own, self._daily,
                               self.product.vehicle_ticks_per_vendor_unit)
        bars = self._lead.bars(self.lead.root, closed_by_ns=t_ns)  # the look-ahead filter
        if len(bars.ts) == 0:
            return None
        # The lead's Daily for a date reads earlier dates and that date's first bars only; it is
        # reused within the date while the filtered history keeps the same date layout.
        key = (bars.trade_date[-1], len(np.unique(bars.trade_date)),
               int(np.searchsorted(bars.trade_date, bars.trade_date[-1])))
        if self._lead_key != key:
            times = {d: self.lead.times[d]
                     for d in np.unique(bars.trade_date).astype(object).tolist()}
            self._lead_daily = build_daily(bars, self.lead.product, times)
            self._lead_key = key
        return LeadContext(self.lead.root, bars, self._lead_daily, self.lead.per_unit)

    def _is_decision_time(self, bar) -> bool:  # noqa: ANN001
        dt = self.times.get(bar.trade_date)
        if dt is None:
            return False
        offset = bar.ts_event_ns - dt.open_ns
        return (offset > 0 and offset % (30 * NS_MIN) == 0 and bar.ts_event_ns < dt.close_ns)

    def _exit_time(self, t_ns: int, day: date) -> int:
        mins = HORIZON_MINUTES[self.spec.horizon]
        return self.times[day].flatten_ns if mins is None else t_ns + mins * NS_MIN

    def on_bar(self, bar, account) -> tuple:  # noqa: ANN001 - interface.Bar, AccountView
        from strategy.interface import market_intent

        out: tuple = ()
        busy = account.position_micros != 0 or account.pending_signed_micros != 0
        if account.position_micros != 0 and account.pending_signed_micros == 0 \
                and self._exit_ts is not None and bar.ts_event_ns + NS_MIN >= self._exit_ts:
            side = "sell" if account.position_micros > 0 else "buy"
            out = (market_intent(bar, side, abs(account.position_micros)),)
        elif account.position_micros == 0 and account.pending_signed_micros == 0:
            self._exit_ts = None
        if self._is_decision_time(bar):
            x = self._features(bar.ts_event_ns, bar.trade_date)
            complete = x is not None and bool(np.isfinite(x).all())
            fired = complete and bool(condition_mask(x[None, :], self.spec.conditions)[0])
            acted = fired and not busy and not out
            if acted:
                side = "buy" if self.spec.sign > 0 else "sell"
                out = (market_intent(bar, side, self.qty),)
                self._exit_ts = self._exit_time(bar.ts_event_ns, bar.trade_date)
            self.decisions.append(Decision(bar.ts_event_ns, complete, fired, acted,
                                           bar.trade_date))
        self._own.add(bar)  # the current bar joins the history only after the decision
        return out
