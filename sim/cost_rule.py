"""The D8 rule arithmetic on calibrated book histograms (Stage E.2a Task 8). Pure functions.

Input: one contract's raw calibration (``sim.calibrate_costs``: per trade date, per 30-minute CT
bucket, exact nanosecond histograms of the quoted spread in ticks and of the bid and ask top
sizes over valid books). Output: the frozen per-bucket costs. Exact rational arithmetic
(``fractions.Fraction``) throughout; floats appear only in the written table.

The rule (docs/STAGE_E_DESIGN.md D8, frozen), with the readings this module makes (each one is
also listed in READINGS and in the report):
- s_b = the time-weighted mean of the quoted half-spread (ask - bid) / 2 in ticks during bucket
  b, pooled over the valid-book time of the five dates.
- depth term, per side: when the time-weighted median top-of-book size on the side a market
  order hits (the ask for a buy, the bid for a sell) is below q_c, add (q_c - size) / q_c ticks.
- one-side slippage at bucket b = s_b + that side's depth term.
- fallback: a bucket quoted on fewer than 3 of the 5 dates takes, per side, the largest one-side
  slippage of the product's buckets quoted on at least 3 dates (neither its own half-spread nor
  its own sizes are used).
- event window: per side, the largest one-side slippage over all of the product's buckets.
- round turn at bucket b, in ticks: commission / tick value + buy side + sell side (a long's
  entry and exit or a short's, both in bucket b; the two orders are the same sum).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import time
from decimal import Decimal
from fractions import Fraction

from sim.cost_inputs import MIN_DATES_WITH_QUOTES, SAMPLE_DATES

SIDES = ("buy", "sell")
SIDE_BOOK = {"buy": "ask", "sell": "bid"}  # the side of the book a market order hits

READINGS: tuple[str, ...] = (
    "R1 time axis: Databento ts_recv; each mbp-1 record's top of book lasts until the next "
    "record's ts_recv (exact event-time weighting, not D.1's 1-second sampling).",
    "R2 'time-weighted mean over the five dates': pooled over the valid-book time of all five "
    "dates in the bucket (a date with less valid time weighs less); the equal-weight-per-date "
    "alternative is computed beside it as a sensitivity figure and is not used.",
    "R3 'quotes on a date': the bucket has any positive valid-book time (two-sided, ask > bid) "
    "on that date after the closure and grace exclusions; a standing book carried in from "
    "before the bucket counts.",
    "R4 median: the lower time-weighted median, the smallest size m whose cumulative time share "
    "is at least one half, pooled over the five dates' valid-book time in the bucket.",
    "R5 depth term per side: buy orders hit the ask, sell orders the bid; one-side slippage is "
    "s_b plus that side's depth term; the table's round turn at bucket b is commission/tick "
    "value + (s_b + depth_ask) + (s_b + depth_bid).",
    "R6 fallback: 'the product's other buckets' are those quoted on >= 3 dates; the fallback "
    "replaces the whole one-side slippage per side (half-spread and depth), taking the largest "
    "such value per side. A fallback bucket's own thin data are reported, not used.",
    "R7 event window: per side, the largest final one-side slippage over all the product's "
    "buckets (fallback buckets equal a qualified maximum, so they never raise it).",
    "R8 buckets: 30-minute CT clock buckets of the group's trading segments on each sample date; "
    "a partial half-hour at a segment edge is its own bucket keyed by its CT start (grains "
    "07:30-07:45 and 13:00-13:20, livestock 13:00-13:05); the 1-second reopen grace after every "
    "closure (as sim/calibrate_slippage.py) is excluded from the first bucket of a segment.",
    "R9 headline: the unweighted mean, min and max of the round turn over the buckets that "
    "overlap design D6's day session [O, C) for the product (a bucket straddling O, such as "
    "07:00-07:30 for a 07:20 open, is included).",
    "R10 the depth term is evaluated at the contract's q_c from Task 9 "
    "(reports/stage_e2a_vehicle_sizes.json); a member trading fewer than q_c contracts still "
    "pays the q_c depth term per contract (the rule states one table at q_c).",
)


class UncalibratableError(ValueError):
    """No bucket of the contract is quoted on at least 3 of the 5 dates: D8 has no fallback."""


@dataclass(frozen=True)
class BucketStats:
    key: str
    start_min: int
    end_min: int
    dates_present: int  # sample dates on which the bucket is open time
    dates_with_quotes: int
    valid_ns: int
    spread_tick_ns: int  # sum over valid time of spread ticks x ns (pooled)
    half_spread: Fraction | None  # pooled time-weighted mean half-spread, ticks
    half_spread_equal_dates: Fraction | None  # R2's alternative (sensitivity only)
    per_date: dict[str, dict[str, int]]
    median_size: dict[str, int | None]  # book side ("bid", "ask") -> lower weighted median
    dropped_ns: dict[str, int]
    dropped_records: dict[str, int]
    unknown_ns: int

    @property
    def qualified(self) -> bool:
        return self.dates_with_quotes >= MIN_DATES_WITH_QUOTES


def weighted_lower_median(hist: dict[int, int]) -> int | None:
    total = sum(hist.values())
    if total <= 0:
        return None
    cum = 0
    for value in sorted(hist):
        cum += hist[value]
        if 2 * cum >= total:
            return value
    raise AssertionError("unreachable")


def _merge(hists: list[dict[str, int]]) -> dict[int, int]:
    out: dict[int, int] = {}
    for hist in hists:
        for value, ns in hist.items():
            out[int(value)] = out.get(int(value), 0) + int(ns)
    return out


def bucket_order(start_min: int) -> int:
    """Trade-date order: the 17:00 CT evening first."""
    return (start_min - 17 * 60) % 1440


def aggregate(raw_dates: dict[str, dict]) -> list[BucketStats]:
    """Per-bucket pooled statistics from one contract's raw per-date calibration."""
    if sorted(raw_dates) != sorted(d.isoformat() for d in SAMPLE_DATES):
        raise ValueError(f"raw dates {sorted(raw_dates)} are not the five sample dates")
    spans: dict[str, tuple[int, int]] = {}
    for day in raw_dates.values():
        for key, b in day["buckets"].items():
            span = (int(b["start_min"]), int(b["end_min"]))
            if spans.setdefault(key, span) != span:
                raise ValueError(f"bucket {key} spans {spans[key]} and {span} on different dates")
    out: list[BucketStats] = []
    for key, (start_min, end_min) in sorted(spans.items(), key=lambda kv: bucket_order(kv[1][0])):
        days = {d: v["buckets"][key] for d, v in sorted(raw_dates.items()) if key in v["buckets"]}
        per_date: dict[str, dict[str, int]] = {}
        for d, b in days.items():
            hist = {int(s): int(ns) for s, ns in b["spread_ticks_ns"].items()}
            per_date[d] = {"valid_ns": int(b["class_ns"]["valid"]),
                           "spread_tick_ns": sum(s * ns for s, ns in hist.items())}
            if per_date[d]["valid_ns"] != sum(hist.values()):
                raise ValueError(f"{key} {d}: spread histogram != valid time")
        valid_ns = sum(v["valid_ns"] for v in per_date.values())
        tick_ns = sum(v["spread_tick_ns"] for v in per_date.values())
        quoted = [v for v in per_date.values() if v["valid_ns"] > 0]
        out.append(BucketStats(
            key=key, start_min=start_min, end_min=end_min, dates_present=len(days),
            dates_with_quotes=len(quoted), valid_ns=valid_ns, spread_tick_ns=tick_ns,
            half_spread=Fraction(tick_ns, 2 * valid_ns) if valid_ns else None,
            half_spread_equal_dates=(sum(Fraction(v["spread_tick_ns"], 2 * v["valid_ns"])
                                         for v in quoted) / len(quoted)) if quoted else None,
            per_date=per_date,
            median_size={side: weighted_lower_median(_merge([b[f"{side}_size_ns"]
                                                             for b in days.values()]))
                         for side in ("bid", "ask")},
            dropped_ns={c: sum(int(b["class_ns"][c]) for b in days.values())
                        for c in ("empty", "locked", "crossed")},
            dropped_records={c: sum(int(b["class_records"][c]) for b in days.values())
                             for c in ("empty", "locked", "crossed")},
            unknown_ns=sum(int(b["unknown_ns"]) for b in days.values()),
        ))
    return out


def depth_ticks(median_size: int | None, q_c: int | None) -> Fraction:
    """(q_c - size) / q_c when the median top size is below q_c, else 0 (q_c None: pending)."""
    if q_c is None:
        return Fraction(0)
    if isinstance(q_c, bool) or not isinstance(q_c, int) or q_c < 1:
        raise ValueError(f"q_c {q_c!r} is not a positive integer")
    if median_size is None:
        raise ValueError("no median size for a qualified bucket")
    return Fraction(q_c - median_size, q_c) if median_size < q_c else Fraction(0)


@dataclass(frozen=True)
class BucketCost:
    stats: BucketStats
    fallback: bool
    depth: dict[str, Fraction | None]  # side -> own depth term (None for a fallback bucket)
    side_ticks: dict[str, Fraction]  # final one-side slippage per side
    round_turn_ticks: Fraction


@dataclass(frozen=True)
class ProductRule:
    commission_rt_usd: Decimal
    tick_value_usd: Decimal
    q_c: int | None

    @property
    def commission_ticks(self) -> Fraction:
        return Fraction(self.commission_rt_usd) / Fraction(self.tick_value_usd)


def apply_rule(stats: list[BucketStats], rule: ProductRule
               ) -> tuple[list[BucketCost], dict[str, Fraction]]:
    """Final per-bucket costs and the event-window one-side slippage per side."""
    qualified = [b for b in stats if b.qualified]
    if not qualified:
        raise UncalibratableError("no bucket is quoted on at least 3 of the 5 dates")
    own: dict[str, dict[str, Fraction]] = {}
    depth: dict[str, dict[str, Fraction]] = {}
    for b in qualified:
        if b.half_spread is None:
            raise ValueError(f"qualified bucket {b.key} has no valid time")
        depth[b.key] = {s: depth_ticks(b.median_size[SIDE_BOOK[s]], rule.q_c) for s in SIDES}
        own[b.key] = {s: b.half_spread + depth[b.key][s] for s in SIDES}
    fallback = {s: max(v[s] for v in own.values()) for s in SIDES}
    out: list[BucketCost] = []
    for b in stats:
        sides = own.get(b.key, fallback)
        out.append(BucketCost(
            stats=b, fallback=not b.qualified,
            depth=depth.get(b.key, {s: None for s in SIDES}), side_ticks=dict(sides),
            round_turn_ticks=rule.commission_ticks + sides["buy"] + sides["sell"]))
    event = {s: max(c.side_ticks[s] for c in out) for s in SIDES}
    return out, event


def day_session_buckets(costs: list[BucketCost], open_ct: time, close_ct: time
                        ) -> list[BucketCost]:
    """R9: the buckets overlapping [O, C) of design D6."""
    o_min = open_ct.hour * 60 + open_ct.minute
    c_min = close_ct.hour * 60 + close_ct.minute
    return [c for c in costs if c.stats.start_min < c_min and c.stats.end_min > o_min
            and c.stats.start_min < 17 * 60]


def headline(costs: list[BucketCost], rule: ProductRule, open_ct: time, close_ct: time) -> dict:
    day = day_session_buckets(costs, open_ct, close_ct)
    if not day:
        raise ValueError("no bucket overlaps the day session")
    ticks = [c.round_turn_ticks for c in day]
    usd = [t * Fraction(rule.tick_value_usd) for t in ticks]
    return {"n_buckets": len(day), "first": day[0].stats.key, "last": day[-1].stats.key,
            "fallback_buckets": [c.stats.key for c in day if c.fallback],
            "round_turn_ticks": {"mean": sum(ticks) / len(ticks), "min": min(ticks),
                                 "max": max(ticks)},
            "round_turn_usd": {"mean": sum(usd) / len(usd), "min": min(usd), "max": max(usd)}}
