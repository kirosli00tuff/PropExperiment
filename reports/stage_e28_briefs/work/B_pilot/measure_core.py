"""Spec section 3 on one reduced trade date: placements, the fill rules, touches and markouts.

Frozen spec: reports/stage_e28_pilot_spec.md (contract QM, sha256 8937740338e81103...), sections
2 and 3, with the SpecReviewer fixes RS-03 to RS-06 and RS-13 (reports/stage_e28_briefs/R_spec.md).
The code is contract-generic: tick size comes from --tick (QM: 0.025), fees from --fee-side.

Placements (spec 3): at every grid time g of a session piece, one buy and one sell of size 1
for each placement type: T at the touch (buy at the best bid, sell at the best ask) and I one
tick inside (buy at bid + 1, sell at ask - 1, only when the spread is at least 2 ticks). The
order joins at j = g + 50 ms using the book state at j (price, and Q_ahead = the displayed
size at its price for T, 0 for I). A join state that is missing, crossed, locked or has an
empty side takes no placement (counted). Virtual orders never touch the book. Each order is
flagged ``stale`` when the best price on its side at g differs from that at j, or no book
state exists at g (RS-06; reported per cell).

Life: the order rests over the open window (j, c) with c = min(j + 60 s + 50 ms, the end of
its session piece) (RS-13: under the spec grid the clip never binds). The cancel is decided at
j + 60 s and takes effect 50 ms later, and fills inside that latency count. A trade stamped
exactly at j is part of the join state and does not count; one stamped exactly at c finds the
order already cancelled.

Trades with no aggressor (side N: implied-involved or opening trades) never add to V(t) and
never trigger a fill under any rule (frozen spec section 2 and 3, RS-03, RS-04).

Fill rules (``RULES``), each giving the first qualifying event inside the life, with its
trigger ("queue", "through", "at" or "quote") and the trigger trade's aggressor side (A or B):
- ``spec`` (section 3, conservative): V(t) = cumulative size of trades printed at exactly the
  order's price with the aggressor on the other side (sell-aggressor 'A' for a buy, buy-
  aggressor 'B' for a sell); fill at the first trade with V >= Q_ahead + 1 ("queue"), or at the
  first trade with a defined aggressor (A or B) printed strictly through the price
  ("through"), whichever is first. A quote that reaches the price without a trade is never a
  fill; cancellations ahead never reduce Q_ahead.
- ``trade_through_only``: the first A/B trade strictly through the price.
- ``trade_at_or_through``: the first A/B trade at or through the price.
- ``touch``: the first A/B trade at or through the price, or the first opposite best quote at
  or through it ("quote"), whichever is first.
The fill price is always the limit price; the fill time is that event's timestamp.

Touch (spec 4's touch rate, as worded there): the order's price is reached inside its life by a
trade (at or through, any aggressor, N included) or by the opposite best quote (ask <= price for
a buy, bid >= price for a sell; any defined quote, crossed or locked states included).

Markouts (spec 3): markout_h = s * (mid(t_f + h) - p) in ticks, s = +1 buy / -1 sell, h = 1,
10, 60 s. Headline: mid from the last book state at or before t_f + h, dropped (counted by
reason) as "session_end" when t_f + h is at or after the end of the fill's session piece,
"invalid_book" when any book state active over [t_f, t_f + h] is crossed, locked or has an
empty side, "no_book" when no state precedes t_f. No-drop variant (RS-05, beside the headline):
mid from the last VALID state at or before t_f + h, dropped only when no valid state is active
at any moment after t_f up to t_f + h ("no_valid_book") or as "session_end" (which the spec grid
never reaches).
"""
# ruff: noqa: I001 - pilot_common is imported first on purpose (sys.path)

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

import pilot_common as pc
from pilot_stream import ASK_UNDEF, BID_UNDEF, SIDE_ASK, SIDE_BID, DayBook

RULE_SPEC = "spec"
RULE_THROUGH = "trade_through_only"
RULE_AT_OR_THROUGH = "trade_at_or_through"
RULE_TOUCH = "touch"
RULES = (RULE_SPEC, RULE_THROUGH, RULE_AT_OR_THROUGH, RULE_TOUCH)
SIM_RULE_CHOICES = (RULE_THROUGH, RULE_TOUCH, RULE_SPEC, RULE_AT_OR_THROUGH)
TYPES = ("T", "I")
SIDES = (1, -1)  # +1 buy, -1 sell
DROP_SESSION_END, DROP_INVALID, DROP_NO_BOOK = "session_end", "invalid_book", "no_book"
DROP_NO_VALID = "no_valid_book"
TRIG_QUEUE, TRIG_THROUGH, TRIG_AT, TRIG_QUOTE = "queue", "through", "at", "quote"
NONE = -1  # "no event" in integer time columns


@dataclass(frozen=True)
class MeasureParams:
    latency_ns: int = pc.LATENCY_NS
    life_ns: int = pc.LIFE_NS
    horizons_s: tuple[int, ...] = pc.HORIZONS_S
    rules: tuple[str, ...] = (RULE_SPEC,)

    @property
    def life_end_offset_ns(self) -> int:
        return self.life_ns + self.latency_ns


def _first(idx: np.ndarray) -> int | None:
    return int(idx[0]) if len(idx) else None


def _earliest(*candidates: int | None) -> int | None:
    found = [c for c in candidates if c is not None]
    return min(found) if found else None


def defined_aggressor(side: np.ndarray) -> np.ndarray:
    """A or B: side N (no aggressor) never triggers a fill (RS-04)."""
    return (side == SIDE_ASK) | (side == SIDE_BID)


def spec_fill(px: np.ndarray, sz: np.ndarray, side: np.ndarray, price: int, q_ahead: int,
              s: int) -> tuple[int, str] | None:
    """(index into the life-window trades, trigger) of the spec rule's fill, or None."""
    other = SIDE_ASK if s > 0 else SIDE_BID
    at = (px == price) & (side == other)
    vol = np.cumsum(np.where(at, sz, 0))
    queue = _first(np.flatnonzero(at & (vol >= q_ahead + 1)))
    through = through_index(px, side, price, s)
    first = _earliest(queue, through)
    if first is None:
        return None
    return first, TRIG_QUEUE if first == queue else TRIG_THROUGH


def spec_fill_index(px: np.ndarray, sz: np.ndarray, side: np.ndarray, price: int, q_ahead: int,
                    s: int) -> int | None:
    """Index into the life-window trades of the spec rule's fill, or None."""
    got = spec_fill(px, sz, side, price, q_ahead, s)
    return None if got is None else got[0]


def through_index(px: np.ndarray, side: np.ndarray, price: int, s: int) -> int | None:
    """First trade with a defined aggressor strictly through ``price``."""
    beyond = px < price if s > 0 else px > price
    return _first(np.flatnonzero(beyond & defined_aggressor(side)))


def at_or_through_index(px: np.ndarray, side: np.ndarray | None, price: int,
                        s: int) -> int | None:
    """First trade at or through ``price``; with ``side`` given, A/B aggressors only."""
    reach = px <= price if s > 0 else px >= price
    if side is not None:
        reach = reach & defined_aggressor(side)
    return _first(np.flatnonzero(reach))


def quote_touch_time(book: DayBook, lo: int, hi: int, price: int, s: int) -> int | None:
    """First book change in (lo, hi) whose opposite best quote is at or through ``price``."""
    a = int(np.searchsorted(book.chg_ts, lo, side="right"))
    b = int(np.searchsorted(book.chg_ts, hi, side="left"))
    if a >= b:
        return None
    if s > 0:
        opp = book.chg_ask[a:b]
        hit = np.flatnonzero((opp != ASK_UNDEF) & (opp <= price))
    else:
        opp = book.chg_bid[a:b]
        hit = np.flatnonzero((opp != BID_UNDEF) & (opp >= price))
    return int(book.chg_ts[a + hit[0]]) if len(hit) else None


def _mid(book: DayBook, k: int) -> float:
    return (int(book.chg_bid[k]) + int(book.chg_ask[k])) / 2.0


def markouts(book: DayBook, t_f: int, price: int, s: int, piece_hi: int,
             horizons_s: tuple[int, ...]) -> list[tuple[float | None, str | None]]:
    """Headline: (markout in ticks, None) or (None, drop reason) for each horizon."""
    k_f = book.state_index(t_f)
    out: list[tuple[float | None, str | None]] = []
    for h in horizons_s:
        t_h = t_f + h * pc.NS
        if t_h >= piece_hi:
            out.append((None, DROP_SESSION_END))
            continue
        if k_f < 0:
            out.append((None, DROP_NO_BOOK))
            continue
        k_h = book.state_index(t_h)
        if int(book.chg_invalid_cum[k_h + 1] - book.chg_invalid_cum[k_f]) > 0:
            out.append((None, DROP_INVALID))
            continue
        out.append((s * (_mid(book, k_h) - price), None))
    return out


def markouts_nodrop(book: DayBook, t_f: int, price: int, s: int, piece_hi: int,
                    horizons_s: tuple[int, ...]) -> list[tuple[float | None, str | None]]:
    """RS-05 variant: the last VALID state at or before t_f + h, if that state is active at
    some moment after t_f (its index is at least the state active at t_f)."""
    k_f = book.state_index(t_f)
    out: list[tuple[float | None, str | None]] = []
    for h in horizons_s:
        t_h = t_f + h * pc.NS
        if t_h >= piece_hi:
            out.append((None, DROP_SESSION_END))
            continue
        k_h = book.state_index(t_h)
        pos = int(np.searchsorted(book.valid_idx, k_h, side="right")) - 1
        k_v = int(book.valid_idx[pos]) if pos >= 0 else -1
        if k_f < 0 or k_v < k_f:
            out.append((None, DROP_NO_VALID))
            continue
        out.append((s * (_mid(book, k_v) - price), None))
    return out


def _new_columns(params: MeasureParams) -> dict[str, Any]:
    cols: dict[str, Any] = {k: [] for k in ("grid_index", "g_ns", "j_ns", "life_end_ns",
                                            "session", "piece_hi", "type", "side", "price",
                                            "q_ahead", "touch_ns", "stale")}
    cols["rules"] = {r: {"fill_ns": [], "trigger": [], "trigger_side": [],
                         **{f"{p}{h}": [] for h in params.horizons_s
                            for p in ("m", "drop", "n", "ndrop")}} for r in params.rules}
    return cols


def _order_prices(book: DayBook, k: int, kind: str, s: int) -> tuple[int, int] | str:
    """(price, Q_ahead) of a type-``kind`` order on side ``s`` at join index k, or a skip
    reason."""
    if not book.j_has[k]:
        return "no_book_state_at_join"
    if not book.j_valid[k]:
        return "invalid_book_at_join"
    bid, ask = int(book.j_bid[k]), int(book.j_ask[k])
    if kind == "T":
        return (bid, int(book.j_bsz[k])) if s > 0 else (ask, int(book.j_asz[k]))
    if ask - bid < 2:
        return "spread_lt_2_ticks"
    return (bid + 1, 0) if s > 0 else (ask - 1, 0)


def is_stale(book: DayBook, k: int, s: int) -> bool | None:
    """RS-06: the best price on the order's side at g differs from that at j (no state at g
    counts as differing). None when the book carries no g states."""
    if len(book.g_has) == 0:
        return None
    if not book.g_has[k]:
        return True
    if s > 0:
        return int(book.g_bid[k]) != int(book.j_bid[k])
    return int(book.g_ask[k]) != int(book.j_ask[k])


Fill = tuple[int, str, str | None]  # (time, trigger, aggressor side of the trigger trade)


def _trade_fill(book: DayBook, a: int, idx: int | None, trigger: str | None = None,
                price: int | None = None) -> Fill | None:
    if idx is None:
        return None
    k = a + idx
    trig = trigger or (TRIG_AT if int(book.tr_px[k]) == price else TRIG_THROUGH)
    return int(book.tr_ts[k]), trig, chr(int(book.tr_side[k]))


def rule_fill(rule: str, book: DayBook, a: int, b: int, price: int, q_ahead: int, s: int,
              quote_touch: int | None) -> Fill | None:
    px, sz, side = book.tr_px[a:b], book.tr_sz[a:b], book.tr_side[a:b]
    if rule == RULE_SPEC:
        got = spec_fill(px, sz, side, price, q_ahead, s)
        return None if got is None else _trade_fill(book, a, got[0], got[1])
    if rule == RULE_THROUGH:
        return _trade_fill(book, a, through_index(px, side, price, s), TRIG_THROUGH)
    if rule == RULE_AT_OR_THROUGH:
        return _trade_fill(book, a, at_or_through_index(px, side, price, s), price=price)
    if rule == RULE_TOUCH:
        trade = _trade_fill(book, a, at_or_through_index(px, side, price, s), price=price)
        if quote_touch is not None and (trade is None or quote_touch < trade[0]):
            return quote_touch, TRIG_QUOTE, None
        return trade
    raise ValueError(f"unknown fill rule {rule!r}")


def rule_fill_time(rule: str, book: DayBook, a: int, b: int, price: int, q_ahead: int, s: int,
                   quote_touch: int | None) -> int | None:
    got = rule_fill(rule, book, a, b, price, q_ahead, s, quote_touch)
    return None if got is None else got[0]


def day_orders(book: DayBook, params: MeasureParams) -> tuple[dict[str, Any], dict[str, int]]:
    """Every placement of the day with its touch, fills under each rule and markouts.
    Returns (columns, skipped counts keyed '<type>|<session>|<buy/sell>|<reason>')."""
    if book.day >= pc.CUTOFF_TRADE_DATE:
        raise pc.PilotRefused(f"trade date {book.day} is on or after {pc.CUTOFF_TRADE_DATE}")
    cols = _new_columns(params)
    skipped: dict[str, int] = {}
    plan = book.plan
    for k in range(len(book.join_ns)):
        piece = plan.pieces[int(plan.grid_piece[k])]
        j = int(book.join_ns[k])
        # cancel effective at j + 60 s + 50 ms, clipped at the session piece end (RS-13)
        c = min(j + params.life_end_offset_ns, piece.hi)
        a = int(np.searchsorted(book.tr_ts, j, side="right"))
        b = int(np.searchsorted(book.tr_ts, c, side="left"))
        for kind in TYPES:
            for s in SIDES:
                got = _order_prices(book, k, kind, s)
                if isinstance(got, str):
                    key = f"{kind}|{piece.label}|{'buy' if s > 0 else 'sell'}|{got}"
                    skipped[key] = skipped.get(key, 0) + 1
                    continue
                price, q_ahead = got
                quote = quote_touch_time(book, j, c, price, s)
                trade_touch = at_or_through_index(book.tr_px[a:b], None, price, s)
                touch = _earliest(None if trade_touch is None else int(book.tr_ts[a + trade_touch]),
                                  quote)
                _append_order(cols, params, book, (k, j, c), piece, kind, s, (price, q_ahead),
                              (touch, quote), (a, b))
    return cols, skipped


def _append_order(cols: dict[str, Any], params: MeasureParams, book: DayBook,
                  when: tuple[int, int, int], piece: pc.Piece, kind: str, s: int,
                  order: tuple[int, int], touches: tuple[int | None, int | None],
                  span: tuple[int, int]) -> None:
    (k, j, c), (price, q_ahead), (touch, quote), (a, b) = when, order, touches, span
    for key, value in (("grid_index", k), ("g_ns", int(book.plan.grid_ns[k])), ("j_ns", j),
                       ("life_end_ns", c), ("session", piece.label), ("piece_hi", piece.hi),
                       ("type", kind), ("side", s), ("price", price), ("q_ahead", q_ahead),
                       ("touch_ns", NONE if touch is None else touch),
                       ("stale", is_stale(book, k, s))):
        cols[key].append(value)
    for rule in params.rules:
        fill = rule_fill(rule, book, a, b, price, q_ahead, s, quote)
        out = cols["rules"][rule]
        out["fill_ns"].append(NONE if fill is None else fill[0])
        out["trigger"].append(None if fill is None else fill[1])
        out["trigger_side"].append(None if fill is None else fill[2])
        blank = [(None, None)] * len(params.horizons_s)
        heads = blank if fill is None else markouts(book, fill[0], price, s, piece.hi,
                                                    params.horizons_s)
        nodrop = blank if fill is None else markouts_nodrop(book, fill[0], price, s, piece.hi,
                                                            params.horizons_s)
        for h, (m, reason), (n, nreason) in zip(params.horizons_s, heads, nodrop, strict=True):
            out[f"m{h}"].append(m)
            out[f"drop{h}"].append(reason)
            out[f"n{h}"].append(n)
            out[f"ndrop{h}"].append(nreason)


def day_summary_counts(book: DayBook) -> dict[str, Any]:
    """The data-check counts of spec section 2 for the day file."""
    return {"counts": dict(book.counts),
            "main_max_gap_s": (None if book.main_max_gap_ns is None
                               else book.main_max_gap_ns / pc.NS),
            "main_records": book.main_records,
            "invalid_book_seconds": {k: v / pc.NS for k, v in book.invalid_ns.items()},
            "instrument_ids_in_records": list(book.instrument_ids),
            "first_ts_event": (None if book.first_ts_event is None
                               else pc.iso_ns(book.first_ts_event)),
            "last_ts_event": None if book.last_ts_event is None else pc.iso_ns(book.last_ts_event),
            "book_changes_kept": int(len(book.chg_ts)), "trades_kept": int(len(book.tr_ts)),
            "placement_grid_times": int(len(book.join_ns))}
