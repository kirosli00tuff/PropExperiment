"""Stage E vehicle rule: per-contract risk, size, risk ratio and the vehicle choice (Task 9).

Frozen rule: docs/STAGE_E_DESIGN.md D2 (with D3, D6, D8, D9.5, D9.11, U7), as the Stage E.2a
lead read it before any research-window bar existed: reports/stage_e2a_vehicle_rule_readings.md
(R1 to R12, sha256 8c3c29dd6531782b6b98d75192071977b8caebd37c48de6cab0afd1642d6b458). Every
function here implements one reading exactly and is pure given its inputs; the I/O runner is
``screening.vehicles_run``. Lead rulings applied (reports/stage_e2a_STATE.md): L-1 (D6's O
values stand), L-2 (an early-settlement day is not an early close), L-4 revised and L-7 (an
unscheduled outage or halt is not a calendar entry; R3's as-of reading handles a missing bar),
L-8 (roll blackouts from the group calendar, as BarsCoder recorded them), L-9 (MBT's window ends
2026-06-18), L-10 (O_X and C_X are clock times on the trade date's own calendar day, and both R3
bars must lie there).

Arithmetic is exact: prices become integer ticks of the contract IN THE VENDOR'S PRICE UNITS
(Databento quotes ZC, ZW, ZS, ZL, HE and LE in cents, so their vendor tick is 100 x the E.0 USD
tick_size; lead's late note, 02:00 PDT), dollars are ticks x tick_value_usd as a Decimal, and
r_c, R*/r_c, q_c and rho_c are Fractions, so round-half-up at .5 and the band edges 0.5 and 2.0
are decided without floating-point error.
"""

from __future__ import annotations

import math
import re
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from datetime import date, time, timedelta
from decimal import Decimal
from fractions import Fraction

import numpy as np

from data.cme_calendar import Holiday, HolidayKind
from data.session import ct_ns

NS_PER_MIN = 60 * 1_000_000_000

# D2 / R6: MES at 2 micros, D.1e's E|m_1| = 144.27 ticks x $1.25 x 2.
R_STAR_USD = Fraction(Decimal("360.68"))
RHO_MAX = Fraction(2)  # R9: candidate iff rho_c <= 2.0 (inclusive)
RHO_MIN_PREFERRED = Fraction(1, 2)  # R9: preferred iff rho_c >= 0.5 (inclusive)
EPS_BAR_USD = Fraction(85)  # D3 / R12

# D2's research window (trade dates, both inclusive); L-9: MBT ends 2026-06-18.
RESEARCH_FIRST = date(2025, 4, 1)
RESEARCH_LAST = date(2026, 6, 19)
LAST_TRADE_DATE: dict[str, date] = {"MBT": date(2026, 6, 18)}

# R1: design D6's session table (CT), O and C per group or metals sub-group, used as written.
D6_SESSIONS: dict[str, tuple[time, time]] = {
    "equity": (time(8, 30), time(15, 0)),
    "rates": (time(7, 20), time(14, 0)),
    "fx": (time(7, 20), time(14, 0)),
    "energy": (time(8, 0), time(13, 30)),
    "gold": (time(7, 20), time(12, 30)),
    "silver": (time(7, 20), time(12, 25)),
    "copper": (time(7, 10), time(12, 0)),
    "grains": (time(8, 30), time(13, 15)),
    "livestock": (time(8, 30), time(13, 0)),
    "crypto": (time(8, 30), time(15, 0)),
}
METALS_SUBGROUP: dict[str, str] = {"GC": "gold", "MGC": "gold", "SI": "silver", "SIL": "silver",
                                   "HG": "copper", "MHG": "copper"}


@dataclass(frozen=True)
class Exposure:
    """One traded exposure of design D1's table: its admissible contracts with their 2026
    January-August ADV (the most active contract's ADV is the table's 'most active' column)."""

    name: str
    cluster: str
    contracts: tuple[tuple[str, int], ...]

    @property
    def products(self) -> tuple[str, ...]:
        return tuple(p for p, _ in self.contracts)

    def adv(self, product: str) -> int:
        return dict(self.contracts)[product]


# Design D1's table after U1 and U2: 31 traded exposures, 45 admissible contracts.
EXPOSURES: tuple[Exposure, ...] = (
    Exposure("Nasdaq-100", "K1", (("MNQ", 2_363_465), ("NQ", 593_595))),
    Exposure("Russell 2000", "K1", (("RTY", 209_871), ("M2K", 115_832))),
    Exposure("Dow", "K1", (("MYM", 152_686), ("YM", 108_142))),
    Exposure("2-year", "K2", (("ZT", 1_325_938),)),
    Exposure("5-year", "K2", (("ZF", 1_941_530),)),
    Exposure("10-year", "K2", (("ZN", 2_589_058),)),
    Exposure("Ultra 10-year", "K2", (("TN", 819_357),)),
    Exposure("Bond", "K2", (("ZB", 609_604),)),
    Exposure("Ultra bond", "K2", (("UB", 505_131),)),
    Exposure("EUR", "K3", (("6E", 216_466), ("M6E", 24_552), ("E7", 4_018))),
    Exposure("AUD", "K3", (("6A", 119_206), ("M6A", 7_765))),
    Exposure("GBP", "K3", (("6B", 103_657), ("M6B", 4_290))),
    Exposure("CAD", "K3", (("6C", 81_946),)),
    Exposure("JPY", "K3", (("6J", 180_897),)),
    Exposure("CHF", "K3", (("6S", 30_520),)),
    Exposure("NZD", "K3", (("6N", 40_801),)),
    Exposure("WTI crude", "K4", (("CL", 1_079_857), ("MCL", 252_100), ("QM", 9_446))),
    Exposure("Henry Hub gas", "K4", (("NG", 521_792), ("MNG", 14_942), ("QG", 4_060))),
    Exposure("RBOB", "K4", (("RB", 206_850),)),
    Exposure("ULSD", "K4", (("HO", 187_479),)),
    Exposure("gold", "K5", (("MGC", 429_702), ("GC", 212_764))),
    Exposure("silver", "K5", (("SIL", 134_882), ("SI", 83_587))),
    Exposure("copper", "K5", (("HG", 77_679), ("MHG", 21_803))),
    Exposure("corn", "K6", (("ZC", 505_663),)),
    Exposure("wheat", "K6", (("ZW", 180_405),)),
    Exposure("soybeans", "K6", (("ZS", 302_997),)),
    Exposure("soybean meal", "K6", (("ZM", 181_637),)),
    Exposure("soybean oil", "K6", (("ZL", 232_819),)),
    Exposure("lean hogs", "K6", (("HE", 67_267),)),
    Exposure("live cattle", "K6", (("LE", 68_652),)),
    Exposure("bitcoin", "K7", (("MBT", 69_615),)),
)
EXPOSURE_OF_PRODUCT: dict[str, Exposure] = {p: x for x in EXPOSURES for p in x.products}

# R7 (U7): starred micros whose restriction is unresolved are never candidates.
NON_CANDIDATES_BY_DECISION = frozenset({"M6E", "M6A"})
# R9 (D9.11): for silver and copper, SIL (MHG) is the vehicle whenever it is a candidate.
PREFERRED_MICRO = {"silver": "SIL", "copper": "MHG"}

# Late note (02:00 PDT): Databento quotes these in cents; vendor tick = 100 x E.0 tick_size.
VENDOR_PRICE_FACTOR: dict[str, int] = {p: 100 for p in ("ZC", "ZW", "ZS", "ZL", "HE", "LE")}

# R5. D9.5 lot caps (D9.6 weights: minis 1, micros 0.1, SIL 0.2, MBT 1) at 1 lot-equivalent.
# Topstep names no weight for QM, QG or E7 (reports/stage_e0_topstep_facts.md F12.4): they are
# not micros, so they count as minis, as D9.11's "QM ... at most 1 (point 5 binds first)" reads.
MICROS = frozenset({"MNQ", "M2K", "MYM", "M6E", "M6A", "M6B", "MCL", "MNG", "MGC", "MHG"})
LOT_CAP_SPECIAL = {"SIL": 5, "MBT": 1}
# R5. D9.11's 50K volatility figures for the contracts R5 applies them to (Topstep F12.1c).
# D9.11 also quotes SI = 0 and HG = 0; neither D9.11's own "Encoded:" sentence nor R5 lists SI
# or HG among the contracts D9.11 caps (D9.11 handles them by D2's SIL/MHG preference), so they
# keep D9.5's 1 here: question Q-1 to the lead (it cannot change a vehicle choice, see the md).
VOL_CAP_50K = {"SIL": 2, "MHG": 2, "MCL": 30, "MGC": 30,
               "CL": 3, "QM": 3, "RB": 3, "HO": 3, "GC": 3}
VOL_CAP_50K_ZERO_NOT_APPLIED = {"SI": 0, "HG": 0}

GRID_TOLERANCE_TICKS = 1e-6
MIN_OFF_GRID_SHARE_COARSER = 0.10  # at 2x and 10x the vendor tick (tick-too-fine guard)


class VehicleRuleError(ValueError):
    """An input cannot be read under R1-R12 as written; nothing is guessed."""


# ------------------------------------------------------------------ R1 / ticks ----
def session_of(product: str, group: str) -> tuple[str, time, time]:
    """R1: (D6 key, O_X, C_X) of a product in its group."""
    key = METALS_SUBGROUP.get(product, group) if group == "metals" else group
    if key not in D6_SESSIONS:
        raise VehicleRuleError(f"{product}: no D6 session for group {group!r}")
    opening, closing = D6_SESSIONS[key]
    return key, opening, closing


_LEADING_DECIMAL = re.compile(r"^\s*(\d+(?:\.\d+)?)\s*(?:\(.*\))?\s*$")
_FRACTION_THEN_DECIMAL = re.compile(
    r"^\s*(\d+)/(\d+)(?:\s+of\s+(\d+)/(\d+))?\s*\((\d+(?:\.\d+)?)\)\s*$")


def parse_tick_size(text: str) -> Decimal:
    """E.0's tick_size string -> Decimal in E.0's units. A plain decimal first ("0.0025 (USD per
    bushel; ...)", "0.10"), or a rates fraction with its decimal in parentheses ("1/2 of 1/32
    (0.015625)"), whose fraction must equal the decimal."""
    m = _LEADING_DECIMAL.match(text)
    if m:
        return Decimal(m.group(1))
    m = _FRACTION_THEN_DECIMAL.match(text)
    if m:
        a, b, c, d, dec = m.groups()
        frac = Fraction(int(a), int(b)) * (Fraction(int(c), int(d)) if c else 1)
        value = Decimal(dec)
        if Fraction(value) != frac:
            raise VehicleRuleError(f"tick_size {text!r}: fraction {frac} != decimal {value}")
        return value
    raise VehicleRuleError(f"tick_size {text!r} is not a decimal or a rates fraction")


def vendor_tick(product: str, e0_tick_size: Decimal) -> Decimal:
    """The tick in the vendor's price units (late note)."""
    return e0_tick_size * VENDOR_PRICE_FACTOR.get(product, 1)


def off_grid_count(prices: np.ndarray, tick: Decimal) -> int:
    """How many prices are not integer multiples of ``tick`` (NaN prices are refused)."""
    prices = np.asarray(prices, dtype=np.float64)
    if np.isnan(prices).any():
        raise VehicleRuleError("NaN price")
    x = prices / float(tick)
    return int((np.abs(x - np.rint(x)) > GRID_TOLERANCE_TICKS).sum())


def tick_scale_check(prices: np.ndarray, tick: Decimal) -> dict:
    """Every price on the ``tick`` grid, and the grid not coarser: at least 10% of prices off
    the 2x and the 10x grid (a tick too fine by 2, 10 or 100 leaves none off)."""
    n = int(np.asarray(prices).size)
    off1, off2, off10 = (off_grid_count(prices, tick * k) for k in (1, 2, 10))
    passed = (n > 0 and off1 == 0 and off2 >= MIN_OFF_GRID_SHARE_COARSER * n
              and off10 >= MIN_OFF_GRID_SHARE_COARSER * n)
    return {"tick": str(tick), "prices_checked": n, "off_grid_1x": off1, "off_grid_2x": off2,
            "off_grid_10x": off10, "passed": bool(passed)}


def to_ticks(prices: np.ndarray, tick: Decimal) -> np.ndarray:
    """Prices -> integer ticks; any price off the grid raises."""
    x = np.asarray(prices, dtype=np.float64) / float(tick)
    out = np.rint(x)
    if x.size and np.abs(x - out).max() > GRID_TOLERANCE_TICKS:
        raise VehicleRuleError(f"price off the {tick} grid")
    return out.astype(np.int64)


# ------------------------------------------------------------------ R5 / R6 ----
@dataclass(frozen=True)
class CapDecision:
    cap: int
    source: str  # "D9.5" or "D9.11"
    lot_cap_d9_5: int
    vol_cap_50k_d9_11: int | None
    note: str


def lot_cap_d9_5(product: str) -> int:
    if product in LOT_CAP_SPECIAL:
        return LOT_CAP_SPECIAL[product]
    return 10 if product in MICROS else 1


def cap_for(product: str) -> CapDecision:
    """R5: cap_c = min(D9.5 lot cap, D9.11 50K volatility cap)."""
    lot = lot_cap_d9_5(product)
    vol = VOL_CAP_50K.get(product)
    if vol is not None and vol < lot:
        return CapDecision(vol, "D9.11", lot, vol, f"D9.11 50K figure {vol} < D9.5 {lot}")
    if product in VOL_CAP_50K_ZERO_NOT_APPLIED:
        return CapDecision(lot, "D9.5", lot, None,
                           "D9.11 quotes a 50K figure of 0; R5 and D9.11's encoding do not "
                           "apply it (D2's SIL/MHG preference instead): question Q-1")
    note = (f"D9.11 50K figure {vol} >= D9.5 {lot}: the lot cap binds" if vol is not None
            else "no D9.11 figure")
    return CapDecision(lot, "D9.5", lot, vol, note)


def round_half_up(x: Fraction) -> int:
    """R6: floor(x + 0.5)."""
    return math.floor(Fraction(x) + Fraction(1, 2))


def size_contract(r_c_usd: Fraction, cap: int, r_star: Fraction = R_STAR_USD
                  ) -> tuple[int, Fraction]:
    """R6: q_c = min(cap_c, max(1, round(R*/r_c))) with round-half-up; rho_c = q_c r_c / R*."""
    if r_c_usd <= 0:
        raise VehicleRuleError(f"r_c must be positive, got {r_c_usd}")
    if cap < 1:
        raise VehicleRuleError(f"cap must be >= 1, got {cap}")
    q_c = min(cap, max(1, round_half_up(Fraction(r_star) / Fraction(r_c_usd))))
    return q_c, q_c * Fraction(r_c_usd) / Fraction(r_star)


# ------------------------------------------------------------------ R2 / R3 / R4 ----
CAUSES = ("roll_blackout", "vendor_degraded", "closure_or_early_close_at_or_before_C",
          "no_bar_in_window")


def calendar_exclusion(holiday: Holiday | None, close_ct: time) -> str | None:
    """R2: a full closure, or an early halt or early close at or before C_X (L-2: early
    settlement is not an early close; it is not in HOLIDAYS)."""
    if holiday is None:
        return None
    if holiday.kind is HolidayKind.FULL_CLOSURE:
        return "full_closure"
    if holiday.kind is HolidayKind.EARLY_HALT:
        if holiday.halt_ct is None:
            raise VehicleRuleError(f"{holiday.day}: early halt without a time")
        return "early_halt_at_or_before_C" if holiday.halt_ct <= close_ct else None
    raise VehicleRuleError(f"{holiday.day}: unknown holiday kind {holiday.kind!r}")


@dataclass(frozen=True)
class RiskMeasure:
    """R2-R4 for one contract. Moves per date stay internal (no price series is reported)."""

    trade_dates: tuple[date, ...]
    excluded: dict[str, tuple[date, ...]]  # cause -> dates (roll/degraded/calendar may overlap)
    used: tuple[date, ...]
    open_bar_missing: tuple[date, ...]  # used dates whose bar at exactly O_X was missing
    close_bar_missing: tuple[date, ...]  # used dates whose bar at exactly C_X - 1 min was missing
    other_trade_date_bars_in_window: int  # bars in [O_X, C_X) of D's calendar day, not of D
    sum_abs_ticks: int
    tick_value_usd: Decimal

    @property
    def exact_bar_missing(self) -> tuple[date, ...]:
        return tuple(sorted(set(self.open_bar_missing) | set(self.close_bar_missing)))

    @property
    def r_c_usd(self) -> Fraction:
        if not self.used:
            raise VehicleRuleError("no date left to measure r_c on")
        return Fraction(self.tick_value_usd) * Fraction(self.sum_abs_ticks, len(self.used))


def _as_day_array(trade_dates: Iterable) -> np.ndarray:
    return np.asarray(list(trade_dates) if not isinstance(trade_dates, np.ndarray)
                      else trade_dates).astype("datetime64[D]")


def measure_risk(ts_ns: np.ndarray, bar_trade_dates: np.ndarray, opens: np.ndarray,
                 closes: np.ndarray, instrument_ids: np.ndarray, *, open_ct: time,
                 close_ct: time, holidays: Mapping[date, Holiday],
                 roll_blackout: Iterable[date], degraded: Iterable[date], tick: Decimal,
                 tick_value_usd: Decimal, first: date = RESEARCH_FIRST,
                 last: date = RESEARCH_LAST) -> RiskMeasure:
    """R2-R4 on one contract's bars (time-ordered, one row per one-minute bar; ``ts_ns`` is the
    bar open in UTC ns, ``bar_trade_dates`` its trade date). The trade dates are the bars' own
    trade dates in [first, last] (R2: the research parquet's dates)."""
    ts = np.asarray(ts_ns, dtype=np.int64)
    if len(ts) > 1 and not (np.diff(ts) > 0).all():
        raise VehicleRuleError("bars must be strictly increasing in time")
    days_arr = _as_day_array(bar_trade_dates)
    days = sorted({d.astype(object) for d in np.unique(days_arr)})
    outside = [d for d in days if not first <= d <= last]
    if outside:
        raise VehicleRuleError(f"trade dates outside {first}..{last}: {outside[:3]}")
    blackout, bad = set(roll_blackout), set(degraded)
    excluded: dict[str, list[date]] = {c: [] for c in CAUSES}
    for d in days:
        if d in blackout:
            excluded["roll_blackout"].append(d)
        if d in bad:
            excluded["vendor_degraded"].append(d)
        if calendar_exclusion(holidays.get(d), close_ct) is not None:
            excluded["closure_or_early_close_at_or_before_C"].append(d)
    dropped = {d for c in CAUSES for d in excluded[c]}
    used: list[date] = []
    open_missing: list[date] = []
    close_missing: list[date] = []
    foreign = 0
    total = 0
    for d in days:
        if d in dropped:
            continue
        lo, hi = ct_ns(d, open_ct), ct_ns(d, close_ct)  # L-10: D's own calendar day
        i0, i1 = np.searchsorted(ts, lo, "left"), np.searchsorted(ts, hi, "left")
        mine = np.flatnonzero(days_arr[i0:i1] == np.datetime64(d, "D")) + i0
        foreign += (i1 - i0) - len(mine)
        if len(mine) == 0:
            excluded["no_bar_in_window"].append(d)
            continue
        first_i, last_i = int(mine[0]), int(mine[-1])
        if instrument_ids[first_i] != instrument_ids[last_i]:
            raise VehicleRuleError(f"{d}: the O_X and C_X bars belong to different instruments")
        o_tick, c_tick = to_ticks(np.array([opens[first_i], closes[last_i]]), tick)
        total += abs(int(c_tick) - int(o_tick))
        used.append(d)
        if ts[first_i] != lo:
            open_missing.append(d)
        if ts[last_i] != hi - NS_PER_MIN:
            close_missing.append(d)
    return RiskMeasure(tuple(days), {c: tuple(v) for c, v in excluded.items()}, tuple(used),
                       tuple(open_missing), tuple(close_missing), int(foreign), total,
                       Decimal(tick_value_usd))


# ------------------------------------------------------------------ R8 ----
@dataclass(frozen=True)
class BucketSides:
    """One D8 cost bucket at size q_c: CT minutes [start_min, end_min) and the per-side cost in
    ticks (s_b plus that side's depth term at q_c)."""

    start_min: int
    end_min: int
    buy_ticks: float
    sell_ticks: float


def one_side_slippage_ticks(buckets: Sequence[BucketSides], open_min: int, close_min: int
                            ) -> Fraction:
    """R8: the minute-weighted mean over [O_X, C_X) of s_b plus the mean of the two sides'
    depth terms, i.e. of (buy + sell) / 2 per bucket. The buckets must tile [O_X, C_X)."""
    if not 0 <= open_min < close_min <= 24 * 60:
        raise VehicleRuleError(f"window [{open_min}, {close_min}) is empty")
    covered = np.zeros(close_min - open_min, dtype=np.int64)
    total = Fraction(0)
    for b in buckets:
        lo, hi = max(b.start_min, open_min), min(b.end_min, close_min)
        if hi <= lo:
            continue
        covered[lo - open_min:hi - open_min] += 1
        total += (hi - lo) * (Fraction(b.buy_ticks) + Fraction(b.sell_ticks)) / 2
    if (covered != 1).any():
        gaps = int((covered == 0).sum())
        raise VehicleRuleError(f"cost buckets do not tile the day session: {gaps} minutes "
                               f"uncovered, {int((covered > 1).sum())} covered twice")
    return total / (close_min - open_min)


def cost_per_dollar_of_risk(commission_rt_usd: Fraction, one_side_slippage_usd: Fraction,
                            r_c_usd: Fraction) -> Fraction:
    """R8: (commission_c + 2 x one-side slippage_c) / r_c (q_c cancels)."""
    if r_c_usd <= 0:
        raise VehicleRuleError("r_c must be positive")
    return (Fraction(commission_rt_usd) + 2 * Fraction(one_side_slippage_usd)) / Fraction(r_c_usd)


# ------------------------------------------------------------------ R9 - R12 ----
@dataclass(frozen=True)
class VehicleFacts:
    product: str
    q_c: int
    cap_c: int
    rho_c: Fraction
    cost_per_dollar: Fraction  # R8
    adv: int  # D1's 2026 January-August ADV


@dataclass(frozen=True)
class Choice:
    exposure: str
    status: str  # "chosen" | "undersized" | "no candidate: not traded in Stage E" | "question"
    vehicle: str | None
    candidates: tuple[str, ...]
    preferred: tuple[str, ...]
    excluded_by_r7: tuple[str, ...]
    deciding: str  # the comparison that decides, in words


def _cheapest(pool: Sequence[VehicleFacts], label: str = "contract in the set"
              ) -> tuple[VehicleFacts, str]:
    """Lowest R8 cost; an exact tie goes to the higher ADV (R9)."""
    best_cost = min(f.cost_per_dollar for f in pool)
    tied = [f for f in pool if f.cost_per_dollar == best_cost]
    if len(pool) == 1:
        return pool[0], (f"the only {label}: {pool[0].product} (cost per dollar of "
                         f"risk {float(best_cost):.8f})")
    if len(tied) == 1:
        others = ", ".join(f"{f.product} {float(f.cost_per_dollar):.8f}" for f in pool
                           if f is not tied[0])
        return tied[0], (f"lowest cost per dollar of risk: {tied[0].product} "
                         f"{float(best_cost):.8f} < {others}")
    top = max(f.adv for f in tied)
    winners = [f for f in tied if f.adv == top]
    if len(winners) != 1:
        raise VehicleRuleError(f"tie on cost and ADV: {[f.product for f in winners]}")
    return winners[0], (f"cost tie at {float(best_cost):.6f} between "
                        f"{', '.join(f.product for f in tied)}; higher ADV {winners[0].product} "
                        f"{top:,}")


def choose_vehicle(exposure: str, facts: Sequence[VehicleFacts],
                   apply_preference: bool = True) -> Choice:
    """R7, R9, R10, R11 for one exposure's admissible contracts. ``apply_preference=False``
    runs R9 without D9.11's SIL/MHG sentence, only to show whether that sentence binds."""
    r7 = tuple(f.product for f in facts if f.product in NON_CANDIDATES_BY_DECISION)
    cands = [f for f in facts if f.product not in NON_CANDIDATES_BY_DECISION
             and f.rho_c <= RHO_MAX]
    names = tuple(f.product for f in cands)
    preferred = [f for f in cands if f.rho_c >= RHO_MIN_PREFERRED]
    pref_names = tuple(f.product for f in preferred)
    if not cands:
        return Choice(exposure, "no candidate: not traded in Stage E", None, (), (), r7,
                      "no admissible contract has rho_c <= 2.0 after R7")
    micro = PREFERRED_MICRO.get(exposure) if apply_preference else None
    by_name = {f.product: f for f in cands}
    if micro in by_name:
        f = by_name[micro]
        if f.rho_c >= RHO_MIN_PREFERRED:
            return Choice(exposure, "chosen", micro, names, pref_names, r7,
                          f"R9 (D9.11): {micro} is a candidate (rho {float(f.rho_c):.4f}), "
                          "so it is the vehicle")
        if preferred:
            return Choice(exposure, "question", None, names, pref_names, r7,
                          f"{micro} is a candidate below 0.5 while {pref_names} are preferred: "
                          "R9's preference and R10 do not settle this; the lead rules")
        return Choice(exposure, "undersized", micro, names, pref_names, r7,
                      f"R9 (D9.11) and R10: {micro} is a candidate and no candidate has "
                      "rho_c >= 0.5; traded at the cap")
    if preferred:
        best, why = _cheapest(preferred, "preferred candidate")
        return Choice(exposure, "chosen", best.product, names, pref_names, r7, why)
    best, why = _cheapest(cands, "candidate")
    if best.q_c != best.cap_c:
        raise VehicleRuleError(f"{best.product}: rho < 0.5 below the cap is impossible")
    return Choice(exposure, "undersized", best.product, names, pref_names, r7,
                  "R10: no candidate has rho_c >= 0.5; " + why)


def translated_epsilon_ticks(q_c: int, tick_value_usd: Decimal) -> int:
    """R12 (D3): floor($85.00 / (q_c x tick_value_c)) net ticks per contract per day."""
    if q_c < 1:
        raise VehicleRuleError("q_c must be >= 1")
    return math.floor(EPS_BAR_USD / (q_c * Fraction(Decimal(tick_value_usd))))


def blackout_dates(splices: Iterable[date], is_trade_date, sessions_before: int = 2
                   ) -> frozenset[date]:
    """The splice trade date and the ``sessions_before`` trade dates before it (a check on
    BarsCoder's recorded lists; L-8 makes the recorded list govern)."""
    out: set[date] = set()
    for splice in splices:
        out.add(splice)
        day, found = splice, 0
        while found < sessions_before:
            day -= timedelta(days=1)
            if is_trade_date(day):
                out.add(day)
                found += 1
    return frozenset(out)
