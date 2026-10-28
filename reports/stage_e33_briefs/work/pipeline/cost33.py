"""Stage E.33 cost and fill model (StatsCostCoder; prompt B6, protocol P0.3, P3.2-P3.3, P6.4, V50).

ZM's per-firm net ticks per round trip:
- fees: each firm's round-trip fee in USD from E.28's A2 firm files (reports/stage_e28_briefs/
  A2_firm_<firm>.json, products.ZM), converted at the ZM tick (0.10 USD/short ton = 10 USD), cross-checked
  against E.28's A3_firm_products.json (fee_rt_ticks) and A3_econ.json (pairs F_rt_ticks), and against the
  protocol's P6.4 list and P0.3's f (`fee_report`);
- (i) market round trip, P3.3 executable prices with the P3.2 fallback (`market_round_trip`);
- (ii) trade-through limit entry, P6.4 (ii): the order rests at the touch at t + L and fills only when an A or B
  trade prints strictly through its price within min(60 s, h/5); market exit as in (i); (ii-b) converts to a
  market order at the timeout (`limit_entry_through`);
- per-fill accounting that overlaps E.31 (V50; reports/stage_e31_briefs/work/pilot/measure31_core.py and
  stats31): the entry leg's per-fill net s (mid(t_f + h) - price) - fee / 2 (`entry_leg_net`).

Units: prices are integer ticks (ZM 0.10 USD/short ton), times are int64 ns on the ts_recv clock (P0.3; a
record is known at u iff ts_recv <= u). Nets are ticks per contract after the firm's round-trip fee.
The module reads no market data: callers pass book-update and trade arrays (synthetic in the tests; on real
data only after the test list is hashed, P6.4). Readings are marked `# READING C<n>` and logged in
reports/stage_e33_briefs/work/StatsCostCoder_readings.md.
"""
from __future__ import annotations

import json
import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[4]
E28 = REPO / "reports" / "stage_e28_briefs"

NS = 1_000_000_000
MIN_NS = 60 * NS
L_NS = 1 * NS  # L = 1.000 s, the selection latency (P0.3)
L_FAST_NS = 300_000_000  # L = 0.300 s, reported for the test list only (P0.3, P6.4 (i))
LIMIT_WINDOW_CAP_NS = 60 * NS  # P6.4 (ii): min(60 s, h/5)
ZM_TICK_USD = 10.0  # 0.10 USD/short ton x 100 short tons (P0.3; E.28 A3_econ candidates.ZM.v_source)
NO_PX = int(np.iinfo(np.int64).min)  # an empty side in the touch arrays (same sentinel as lab33)

LONG, SHORT = 1, -1
AGGRESSOR_SIDES = (ord("A"), ord("B"))  # side N (implied or opening) trades never fill (E.31 convention)

# s_flags bits, the same values as INTERFACE.md 4.2 / lab33
FLAG_ENTRY_FALLBACK = 1
FLAG_EXIT_FALLBACK = 2
FLAG_EXIT_LIMIT = 4
FLAG_EXIT_LAST_TOUCH = 8
FLAG_ENTRY_NOT_MADE = 16
FLAG_LIMIT_NOT_PLACED = 64  # (ii): no touch on the order's side (or a bad book) at t + L
FLAG_CONVERTED = 128  # (ii-b): the unfilled limit order became a market order at the timeout

FIRMS = ("topstep", "lucid", "bulenox", "mffu", "tradeify")
# P6.4: "Topstep 0.528, Lucid 0.560 (0.920 if the 5.60 USD is not all-in), Bulenox 0.572, MFFU 0.612,
# Tradeify 0.920"
PROTOCOL_FEE_TICKS = {"topstep": 0.528, "lucid": 0.560, "bulenox": 0.572, "mffu": 0.612, "tradeify": 0.920}
LUCID_NOT_ALL_IN_TICKS = 0.920
P03_FEE_TICKS = 0.528  # P0.3 f (Topstep, 5.28 USD)
# The ZM round-trip fee field in each E.28 A2 file (products.ZM.<field>.value, USD per round trip)
E28_FEE_FIELD = {"topstep": "fee_rt", "lucid": "commission_round_trip", "bulenox": "commission_round_trip",
                 "mffu": "rt", "tradeify": "fee_rt"}
FEE_TOL = 1e-9


# ------------------------------------------------------------------------------------------- fees --
@dataclass(frozen=True)
class FirmFee:
    firm: str
    fee_rt_usd: float
    fee_rt_ticks: float  # fee_rt_usd / ZM_TICK_USD
    source: str  # file:field of the USD figure
    quote: str
    note: str
    a3_products_ticks: float | None  # A3_firm_products.json pairs[firm, ZM].fee_rt_ticks
    a3_econ_ticks: float | None  # A3_econ.json pairs[firm, ZM].F_rt_ticks
    protocol_ticks: float  # P6.4

    @property
    def per_fill_ticks(self) -> float:
        """Half the round trip: the fee of one fill (E.31 stats31_core FEE_PER_FILL_TICKS convention)."""
        return self.fee_rt_ticks / 2.0


def _a3_pairs(path: Path, value_of) -> dict[str, float | None]:
    data = json.loads(path.read_text())
    out: dict[str, float | None] = {}
    for p in data["pairs"]:
        if p.get("code") == "ZM":
            out[p["firm"]] = value_of(p)
    return out


def load_firm_fees(e28: Path = E28) -> tuple[FirmFee, ...]:
    """Each firm's ZM fee per round trip from E.28's A2 files, with the A3 cross-checks and P6.4."""
    prod = _a3_pairs(e28 / "A3_firm_products.json", lambda p: (p.get("fee_rt_ticks") or {}).get("value"))
    econ = _a3_pairs(e28 / "A3_econ.json", lambda p: p.get("F_rt_ticks"))
    rows = []
    for firm in FIRMS:
        a2 = json.loads((e28 / f"A2_firm_{firm}.json").read_text())
        rec = a2["products"]["ZM"][E28_FEE_FIELD[firm]]
        usd = float(rec["value"])
        if not math.isfinite(usd) or usd <= 0:
            raise ValueError(f"{firm}: ZM round-trip fee {usd!r} is not a positive number")
        rows.append(FirmFee(firm, usd, usd / ZM_TICK_USD,
                            f"reports/stage_e28_briefs/A2_firm_{firm}.json:products.ZM.{E28_FEE_FIELD[firm]}",
                            str(rec.get("quote", "")), str(rec.get("note", "")), prod.get(firm), econ.get(firm),
                            PROTOCOL_FEE_TICKS[firm]))
    return tuple(rows)


def fee_report(fees: Sequence[FirmFee]) -> dict:
    """Differences between E.28's files, the protocol's P6.4 list and P0.3's f (empty lists = agreement)."""
    diffs = []
    for f in fees:
        if abs(f.fee_rt_ticks - f.protocol_ticks) > FEE_TOL:
            diffs.append(f"{f.firm}: E.28 A2 {f.fee_rt_ticks:.6f} ticks vs P6.4 {f.protocol_ticks:.3f}")
        for name, v in (("A3_firm_products", f.a3_products_ticks), ("A3_econ", f.a3_econ_ticks)):
            if v is None or abs(v - f.fee_rt_ticks) > FEE_TOL:
                diffs.append(f"{f.firm}: E.28 {name} {v!r} vs A2 {f.fee_rt_ticks:.6f}")
    topstep = next(f for f in fees if f.firm == "topstep")
    f_diff = [] if abs(topstep.fee_rt_ticks - P03_FEE_TICKS) <= FEE_TOL else [
        f"P0.3 f {P03_FEE_TICKS} vs Topstep {topstep.fee_rt_ticks:.6f}"]
    return {"fees_ticks": {f.firm: round(f.fee_rt_ticks, 6) for f in fees},
            "lucid_not_all_in_ticks": LUCID_NOT_ALL_IN_TICKS,
            "differences": diffs, "p03_difference": f_diff}


def fee_variants(fees: Sequence[FirmFee]) -> dict[str, float]:
    """The per-firm round-trip fees P6.4 evaluates, in ticks, plus the Lucid not-all-in alternative."""
    out = {f.firm: f.fee_rt_ticks for f in fees}
    out["lucid_not_all_in"] = LUCID_NOT_ALL_IN_TICKS
    return out


# -------------------------------------------------------------------------------------- the touch --
@dataclass(frozen=True)
class Touch:
    """ZM top of book after each book update (P0.3): ts_recv times, bid_1 and ask_1 in ticks (NO_PX = empty
    side) and the F_MAYBE_BAD_BOOK state. "As of u" = the last update with t <= u."""

    t: np.ndarray
    bid: np.ndarray
    ask: np.ndarray
    bad: np.ndarray

    @classmethod
    def of(cls, t, bid, ask, bad=None) -> Touch:
        t = np.asarray(t, dtype=np.int64)
        bid = np.asarray(bid, dtype=np.int64)
        ask = np.asarray(ask, dtype=np.int64)
        bad = np.zeros(len(t), dtype=bool) if bad is None else np.asarray(bad, dtype=bool)
        if not (len(t) == len(bid) == len(ask) == len(bad)):
            raise ValueError("touch arrays differ in length")
        if len(t) > 1 and np.any(np.diff(t) < 0):
            raise ValueError("touch times must be non-decreasing (ts_recv order)")
        return cls(t, bid, ask, bad)

    def asof(self, u: int) -> int:
        return int(np.searchsorted(self.t, u, side="right")) - 1

    def side_ok(self, k: int, side_px: np.ndarray) -> bool:
        return k >= 0 and not bool(self.bad[k]) and int(side_px[k]) != NO_PX

    def mid_ok(self, k: int) -> bool:
        """P0.3: both sides exist, bid_1 < ask_1, the book is not marked bad."""
        return (self.side_ok(k, self.bid) and self.side_ok(k, self.ask)
                and int(self.bid[k]) < int(self.ask[k]))

    def mid(self, u: int) -> float:
        k = self.asof(u)
        return (int(self.bid[k]) + int(self.ask[k])) / 2.0 if self.mid_ok(k) else math.nan


@dataclass(frozen=True)
class Fill:
    price: int  # ticks
    t: int  # ns: the as-of time, or the fallback update's time
    fallback: bool


def _side_px(touch: Touch, buy: bool) -> np.ndarray:
    return touch.ask if buy else touch.bid


def market_fill(touch: Touch, u: int, buy: bool, deadline: int) -> Fill | None:
    """A market order arriving at u fills at ask_1 (buy) or bid_1 (sell) as of u (P3.2, one contract, no depth
    walk). Fallback: if that side is empty or the book is bad at u, the first later update with t < deadline
    (strictly before, as lab33) at which the side exists and the book is not bad. None when there is none."""
    px = _side_px(touch, buy)
    k = touch.asof(u)
    if touch.side_ok(k, px):
        return Fill(int(px[k]), u, False)
    j = max(k + 1, 0)
    while j < len(touch.t) and int(touch.t[j]) < deadline:
        if touch.side_ok(j, px):
            return Fill(int(px[j]), int(touch.t[j]), True)
        j += 1
    return None


def _last_valid_touch(touch: Touch, u: int, buy: bool) -> int | None:
    px = _side_px(touch, buy)
    k = touch.asof(u)
    while k >= 0:
        if touch.side_ok(k, px):
            return int(px[k])
        k -= 1
    return None


@dataclass(frozen=True)
class RoundTrip:
    made: bool
    net: float  # ticks after the fee; NaN when not made
    gross: float  # ticks before the fee
    entry_px: int | None
    exit_px: int | None
    entry_ns: int
    exit_ns: int
    flags: int


NOT_MADE = RoundTrip(False, math.nan, math.nan, None, None, -1, -1, FLAG_ENTRY_NOT_MADE)


def _exit(touch: Touch, side: int, exit_decision: int, latency: int, session_end: int,
          limit_px: Mapping[int, int] | None) -> tuple[int, int, int]:
    """Market exit decided at exit_decision, arriving at exit_decision + L, with the P3.2 fallback: the first
    later valid update before session_end, else the front's limit price on the blocking side (the low limit for
    a long's exit, the high limit for a short's exit) when D has limits, else the last valid touch on that side.
    Returns (price, time, flags)."""
    buy = side == SHORT
    u = exit_decision + latency
    f = market_fill(touch, u, buy, session_end)  # "before 13:20:00": t < session_end (as lab33)
    if f is not None:
        return f.price, f.t, FLAG_EXIT_FALLBACK if f.fallback else 0
    # a marked exit has no fill update; its time is session_end (lab33 READING EXIT-MARK-TIME)
    if limit_px is not None:
        return int(limit_px[side]), session_end, FLAG_EXIT_FALLBACK | FLAG_EXIT_LIMIT
    last = _last_valid_touch(touch, u, buy)
    if last is None:
        raise ValueError("an exit with no valid touch at any time before it (internal error)")
    return last, session_end, FLAG_EXIT_FALLBACK | FLAG_EXIT_LAST_TOUCH


def _net(side: int, entry_px: int, exit_px: int, fee: float) -> tuple[float, float]:
    gross = float(exit_px - entry_px) if side == LONG else float(entry_px - exit_px)
    return gross - fee, gross


def market_round_trip(touch: Touch, t: int, exit_decision: int, side: int, fee: float, *,
                      latency: int = L_NS, entry_deadline: int | None = None, session_end: int,
                      limit_px: Mapping[int, int] | None = None) -> RoundTrip:
    """P6.4 (i) / P3.3: market entry decided at t (fills as of t + L), market exit decided at exit_decision
    (fills as of exit_decision + L). FH: exit_decision = t + h min gives N_long = bid_1(t + h + L) -
    ask_1(t + L) - f. entry_deadline (default exit_decision, lab33's FH planned exit) bounds the entry fallback.
    limit_px = {LONG: low limit, SHORT: high limit} in ticks, or None when D has no limits."""
    _check_side(side)
    deadline = exit_decision if entry_deadline is None else entry_deadline
    ent = market_fill(touch, t + latency, side == LONG, deadline)
    if ent is None:
        return NOT_MADE
    flags = FLAG_ENTRY_FALLBACK if ent.fallback else 0
    xpx, xt, xflags = _exit(touch, side, exit_decision, latency, session_end, limit_px)
    net, gross = _net(side, ent.price, xpx, fee)
    return RoundTrip(True, net, gross, ent.price, xpx, ent.t, xt, flags | xflags)


# ------------------------------------------------------------------------- trade-through limit entry --
@dataclass(frozen=True)
class Trades:
    """ZM trade prints: ts_recv, price in ticks, aggressor side code (ord 'A', 'B' or 'N')."""

    t: np.ndarray
    px: np.ndarray
    side: np.ndarray

    @classmethod
    def of(cls, t, px, side) -> Trades:
        t = np.asarray(t, dtype=np.int64)
        px = np.asarray(px, dtype=np.int64)
        side = np.asarray([ord(s) if isinstance(s, str) else int(s) for s in side], dtype=np.int64)
        if not (len(t) == len(px) == len(side)):
            raise ValueError("trade arrays differ in length")
        if len(t) > 1 and np.any(np.diff(t) < 0):
            raise ValueError("trade times must be non-decreasing (ts_recv order)")
        return cls(t, px, side)


def limit_window_ns(h_min: int) -> int:
    """P6.4 (ii): min(60 s, h/5); 60 s for every protocol horizon (h >= 5 min)."""
    if h_min <= 0:
        raise ValueError(f"horizon {h_min!r} must be positive")
    return min(LIMIT_WINDOW_CAP_NS, h_min * MIN_NS // 5)


def through_fill(trades: Trades, price: int, side: int, start: int, end: int) -> int | None:
    """Time of the first A or B trade with start < t <= end strictly through the order's price (below a buy,
    above a sell), or None. READING C1: a trade stamped at the placement time is not a fill (E.31: a timer at T
    sees every record stamped <= T before the order joins); READING C2: side-N trades never fill (E.31)."""
    _check_side(side)
    lo = int(np.searchsorted(trades.t, start, side="right"))
    hi = int(np.searchsorted(trades.t, end, side="right"))
    if hi <= lo:
        return None
    px = trades.px[lo:hi]
    hit = (px < price) if side == LONG else (px > price)
    hit &= np.isin(trades.side[lo:hi], AGGRESSOR_SIDES)
    idx = np.flatnonzero(hit)
    return int(trades.t[lo + idx[0]]) if len(idx) else None


@dataclass(frozen=True)
class LimitOutcome:
    placed: bool
    filled: bool
    limit_px: int | None
    fill_ns: int  # -1 if not filled
    net: float  # (ii): ticks after the fee if filled, else NaN
    exit_px: int | None
    exit_ns: int
    flags: int
    market: RoundTrip  # the same signal at market (P6.4 (i)): N_mkt for the opportunity cost
    converted: RoundTrip | None  # (ii-b): the conversion at the timeout (None if filled)

    @property
    def net_iib(self) -> float:
        """(ii-b): the filled limit trade's net, else the converted market trade's net."""
        if self.filled:
            return self.net
        return self.converted.net if self.converted is not None and self.converted.made else math.nan


def limit_entry_through(touch: Touch, trades: Trades, t: int, exit_decision: int, side: int, fee: float,
                        h_min: int, *, latency: int = L_NS, session_end: int,
                        limit_px: Mapping[int, int] | None = None) -> LimitOutcome:
    """P6.4 (ii) for one signal (decision t, side, exit decision as in the selection simulation).

    At t + L the order rests at the touch (bid_1 as of t + L for a long, ask_1 for a short) and fills at its
    own price at the first A/B trade strictly through it inside (t + L, c + L], c = min(t + W, exit_decision)
    the bot's cancel/convert decision (W = min(60 s, h/5); READING C3: the order rests W at the exchange and the
    cancel or conversion takes the same latency L). Exit: market as in (i), at the selection variant's exit
    decision (READING C6: variants differ only in execution, P6.4). (ii-b): unfilled at c, the order converts to
    a market entry filling as of c + L (with the P3.2 fallback), exit as in (i). READING C4: an exit decision
    before the timeout ends the window at it (c = exit_decision); (ii) then has no trade and (ii-b) converts at
    c, a round trip of zero length (net -spread - fee; the conservative choice). READING C5: no touch on the
    order's side (or a bad book) at t + L -> the order is not placed (unfilled; (ii-b) still converts at c)."""
    _check_side(side)
    mkt = market_round_trip(touch, t, exit_decision, side, fee, latency=latency, session_end=session_end,
                            limit_px=limit_px)
    u0 = t + latency
    c = min(t + limit_window_ns(h_min), exit_decision)
    k = touch.asof(u0)
    own = touch.bid if side == LONG else touch.ask
    placed = touch.side_ok(k, own)
    price = int(own[k]) if placed else None
    fill_t = through_fill(trades, price, side, u0, c + latency) if placed else None
    if fill_t is not None:
        xpx, xt, xflags = _exit(touch, side, exit_decision, latency, session_end, limit_px)
        net, _ = _net(side, price, xpx, fee)
        return LimitOutcome(True, True, price, fill_t, net, xpx, xt, xflags, mkt, None)
    conv = market_round_trip(touch, c, exit_decision, side, fee, latency=latency, session_end=session_end,
                             limit_px=limit_px)
    conv = RoundTrip(conv.made, conv.net, conv.gross, conv.entry_px, conv.exit_px, conv.entry_ns, conv.exit_ns,
                     conv.flags | FLAG_CONVERTED)
    flags = 0 if placed else FLAG_LIMIT_NOT_PLACED
    return LimitOutcome(placed, False, price, -1, math.nan, None, -1, flags, mkt, conv)


# ------------------------------------------------------------------------- per-fill accounting (E.31) --
def entry_leg_net(touch: Touch, side: int, price: int, fill_ns: int, horizon_ns: int, fee_rt: float) -> float:
    """E.31's per-fill net of a passive fill: s (mid(t_f + h) - price) - fee_rt / 2 in ticks (E.31: E_h =
    markout_h + c_half, N_h = E_h - fee per fill, stats31_core FEE_PER_FILL_TICKS = RT / 2). NaN when the mid
    as of t_f + h is undefined. E.31's headline markout also drops a fill whose book was invalid at any update
    in [t_f, t_f + h]; callers that need that rule apply it (READING C7)."""
    _check_side(side)
    m = touch.mid(fill_ns + horizon_ns)
    return side * (m - price) - fee_rt / 2.0 if math.isfinite(m) else math.nan


def exit_leg_net(touch: Touch, side: int, exit_px: int, exit_ns: int, fee_rt: float) -> float:
    """The exit fill's per-fill net against the mid at its own time: s (exit_px - mid(exit)) - fee_rt / 2."""
    _check_side(side)
    m = touch.mid(exit_ns)
    return side * (exit_px - m) - fee_rt / 2.0 if math.isfinite(m) else math.nan


# -------------------------------------------------------------------------------- per-firm summaries --
def firm_nets(gross: float, fees: Mapping[str, float]) -> dict[str, float]:
    """A round trip's net per firm: gross ticks minus each firm's round-trip fee."""
    return {firm: gross - fee for firm, fee in fees.items()}


def limit_summary(outcomes: Sequence[LimitOutcome]) -> dict:
    """P6.4 (ii) report fields over one signal set: p_fill, E[N | fill], E[N_mkt | no fill], the opportunity
    cost (1 - p_fill) E[N_mkt | no fill], and (ii-b)'s mean net. Means over made trades; counts included."""
    placed_or_not = list(outcomes)
    n = len(placed_or_not)
    if n == 0:
        raise ValueError("no signals")
    fills = [o for o in placed_or_not if o.filled]
    nofill_mkt = [o.market.net for o in placed_or_not if not o.filled and o.market.made]
    iib = [o.net_iib for o in placed_or_not if math.isfinite(o.net_iib)]
    p_fill = len(fills) / n
    e_fill = float(np.mean([o.net for o in fills])) if fills else math.nan
    e_mkt_nofill = float(np.mean(nofill_mkt)) if nofill_mkt else math.nan
    return {"n_signals": n, "n_fills": len(fills), "n_not_placed": sum(not o.placed for o in placed_or_not),
            "p_fill": p_fill, "mean_net_fill": e_fill, "mean_net_mkt_nofill": e_mkt_nofill,
            "opportunity_cost": (1.0 - p_fill) * e_mkt_nofill if nofill_mkt else math.nan,
            "n_iib": len(iib), "mean_net_iib": float(np.mean(iib)) if iib else math.nan}


def _check_side(side: int) -> None:
    if side not in (LONG, SHORT):
        raise ValueError(f"side {side!r} must be +1 (long) or -1 (short)")


if __name__ == "__main__":  # prints the fee check only; reads no market data
    print(json.dumps(fee_report(load_firm_fees()), indent=1))
