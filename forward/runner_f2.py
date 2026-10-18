"""E22-F2 paper book: one call per NYSE session, in order (F2BookCoder, Stage E.24).

Spec: reports/stage_e24_prereg_F2.md sections 4-6 (with the lead's rulings of 2026-10-18). Step
order mirrors forward/runner.py (E22-F1); nothing futures-specific is imported. For session t:

1. reads t's bars (``forward.etf_bars``); with a source that offers ``fetch_day`` (as
   forward.sources_alpaca does) it also queries ``corporate_actions(start, end, symbols)`` over
   each symbol's whole span (prev, t], prev the symbol's last recorded session, and computes
   r = k x (rawclose(t) + D) / rawclose(prev) - 1 from the RECORDED close (B1; the source's own
   previous close is only checked: prev_close_mismatch:SYM above 1e-6 relative); an instrument
   whose raw close moves by more than ln 1.5 with no split in (prev, t] is treated as having no
   bar (suspect_split:SYM) for at most 10 sessions (S6); ``SourceUnavailable`` propagates and NO
   record is written;
2. checks the date: no weekend, after the last record, every weekday in the gap declared closed by
   the operator (stored in this record's ``declared_closed``);
3. books late corporate actions passed in by the caller (section 6: an action whose ex_date falls
   in an already-recorded session, published only after that record), with q_ex the shares held
   into the ex_date session: a distribution books q_ex x k x amount (k the session's split
   ratios, recorded and late; S2); a split adds (k - 1) x q_ex shares
   and books their value at the ETF's last recorded raw close; a BIL action of either kind books
   -L_ex x dr_c, dr_c the corrected minus the recorded BIL return of the ex_date session (Q21);
   other types of a held ETF are flagged only; each symbol|type|ex_date|amount (B2) is booked at
   most once and never when the source already counted it in a recorded r (each record stores the
   actions
   counted in its r with type, ex_date and amount or ratio, Q23; a corrected return applies
   section 6's formula to all of a session's actions, recorded and late); then applies the
   section 5 share update to each held ETF with a bar on t:
   q(t) = q(t-1) x k x (rawclose(t) + D) / rawclose(t) (splits and distributions; a source
   without ``fetch_day``: q(t-1) x rawclose(prev) x (1 + r(t)) / rawclose(t) with its own r);
4. fills the pending orders at t's raw close (an order expires if its ETF has no bar on t); a sign
   change is filled as two legs (close the old side, open the new one);
5. costs of t's fills: half spread per share (forward/tables_f2.json); SEC fee rate x proceeds on
   sells (short sales included); FINRA TAF per share sold; CAT fee per share on every fill; each
   fee type summed over the session's fills and rounded up to the next 0.01 USD; commission 0;
6. the five P&L terms of section 5 with N_i = q_i x rawclose_i(prev) held into t and d = calendar
   days from the last earlier record that is not a missing day: excess, shorts, leverage, costs,
   late_ca; net_pnl = their sum;
7. new targets from ``forward.strategy_f2.decide`` with the history through t (each booked late
   action's ex-session return corrected from all that session's actions, recorded and late, for
   the rule only) and the shares held
   after the fills; orders = targets - held for ETFs with a bar on t.

Missing data (section 6): an ETF without a bar on t gets no fill (its order expires), no new order,
keeps its shares; its N x r accrues when its data returns (r spans the gap) while -N x r_c is
charged each session BIL has a bar; flagged. After 10 consecutive sessions without a bar that are
not missing days it is closed at its last recorded close as a fill with costs (leg ``delist``) and
dropped for the rest of the test (S7); after 10 such sessions without a BIL bar, SGOV (read every
session) is the cash benchmark from then on, flagged cash_benchmark:SGOV.
BIL without a bar: the r_c parts of the cash terms are not charged on t and accrue when BIL returns
(its r spans the gap); flagged. A day with no bar for any of the 11 ETFs (whatever BIL delivers) is
a missing day: P&L 0, every pending order expires, nothing is ordered, late actions are deferred,
flagged ``missing_day``; it counts as 0 in the evaluation series, and its accruals are charged in
the next record.

Every record stores the operative data feed (a runtime input; the config holds both feeds and is
not edited for the fallback); the book refuses a feed change after the first record. State is
rebuilt from the ledger and the warm-up on every call. Re-running a recorded date recomputes it
from the records before it and returns the stored record when identical; a mismatch raises
LedgerConflictError. Nothing is ever written twice for a date.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import numbers
import sys
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field, replace
from datetime import date, timedelta
from pathlib import Path
from typing import Any

from forward import strategy_f2
from forward.etf_bars import (
    CsvEtfSource,
    EtfBar,
    EtfBarSource,
    EtfDayRow,
    Missing,
    etf_history_sha256,
    load_etf_warmup,
    normalize_etf_day,
)
from forward.ledger import Ledger, canonical_json, strip_hashes

SCHEMA = "E22-F2-ledger/1"
TEST_ID = "E22-F2"
HERE = Path(__file__).resolve().parent
DEFAULT_CONFIG = HERE / "config_f2.json"
DEFAULT_TABLES = HERE / "tables_f2.json"
TargetFn = Callable[..., Any]


class RunnerError(Exception):
    """A refused call (bad date, gap, config mismatch, bad target)."""


class LedgerConflictError(RunnerError):
    """A re-run of a recorded date produced a different record."""


def _finite(x: Any) -> bool:
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)


def _f(x: float) -> float:
    """float with -0.0 normalised to 0.0 (canonical JSON stability)."""
    return float(x) + 0.0


# ------------------------------------------------------------------ configuration ----
@dataclass(frozen=True)
class BookConfig:
    """forward/config_f2.json and forward/tables_f2.json, validated."""

    config: Mapping[str, Any]
    tables: Mapping[str, Any]

    def __post_init__(self) -> None:
        if self.config.get("schema") != "stage_e24_f2_config/1":
            raise RunnerError("config schema must be stage_e24_f2_config/1")
        syms = self.symbols
        if len(set(syms)) != len(syms) or self.cash_symbol in syms:
            raise RunnerError("instruments_order must be unique and must not hold the cash symbol")
        hs = self.tables.get("half_spread_usd", {})
        if set(hs) != set(syms):
            raise RunnerError("tables half_spread_usd must cover exactly the instruments")
        for s in syms:
            if not (_finite(hs[s]) and hs[s] >= 0):
                raise RunnerError(f"{s}: half spread must be finite and >= 0")
        for v in (self.capital, self.cap_usd):
            if not (_finite(v) and v > 0):
                raise RunnerError("capital and leverage cap must be finite and > 0")
        for v in (
            self.sec_rate,
            self.taf_per_share,
            self.cat_per_share,
            self.borrow_b,
            self.margin_s,
            self.commission,
            self.share_tolerance,
        ):
            if not (_finite(v) and v >= 0):
                raise RunnerError("cost and financing constants must be finite and >= 0")
        strategy_f2.increment_steps(self.config)
        rep = self.cash_replacement
        if rep is not None and rep in self.universe:
            raise RunnerError("the replacement cash symbol must not be an instrument or the cash")
        if not (self.prev_close_rel >= 0 and self.suspect_ratio > 1):
            raise RunnerError("prev_close_mismatch_rel must be >= 0 and the suspect ratio > 1")
        for v in (self.suspect_max, self.delisting_sessions, self.cash_replacement_after):
            if v < 1:
                raise RunnerError("session counts of the data rules must be >= 1")

    @property
    def symbols(self) -> tuple[str, ...]:
        return tuple(self.config["instruments_order"])

    @property
    def cash_symbol(self) -> str:
        return str(self.config["cash_symbol"]["value"])

    @property
    def universe(self) -> tuple[str, ...]:
        return (*self.symbols, self.cash_symbol)

    @property
    def cash_replacement(self) -> str | None:
        """SGOV (section 6, delisting bullet), or None when the config declares none."""
        rep = self.config["cash_symbol"].get("replacement")
        return None if not rep else str(rep["value"])

    @property
    def cash_replacement_after(self) -> int:
        rep = self.config["cash_symbol"].get("replacement")
        return int(rep["after_sessions"]) if rep else 1

    @property
    def read_universe(self) -> tuple[str, ...]:
        """The symbols read every session: the instruments, the cash symbol and its replacement
        (read from the first record so that its recorded close exists at a switch)."""
        rep = self.cash_replacement
        return self.universe if rep is None else (*self.universe, rep)

    def _rule(self, key: str) -> float:
        return float(self.config["data_rules"][key]["value"])

    prev_close_rel = property(lambda self: self._rule("prev_close_mismatch_rel"))
    suspect_ratio = property(lambda self: self._rule("suspect_split_move_ratio"))
    suspect_max = property(lambda self: int(self._rule("suspect_split_max_sessions")))
    delisting_sessions = property(lambda self: int(self._rule("delisting_sessions")))

    def _v(self, *keys: str) -> float:
        node: Any = self.config
        for k in keys:
            node = node[k]
        return float(node["value"])

    capital = property(lambda self: self._v("capital_usd"))
    cap_usd = property(lambda self: self._v("leverage_cap_usd"))
    sec_rate = property(lambda self: self._v("costs", "sec_fee_rate"))
    taf_per_share = property(lambda self: self._v("costs", "finra_taf_per_share"))
    cat_per_share = property(lambda self: self._v("costs", "cat_fee_per_share"))
    commission = property(lambda self: self._v("costs", "commission_usd"))
    borrow_b = property(lambda self: self._v("financing", "borrow_fee_b"))
    margin_s = property(lambda self: self._v("financing", "margin_spread_s"))
    day_count = property(lambda self: self._v("financing", "day_count"))
    share_tolerance = property(lambda self: self._v("numerics", "share_update_tolerance"))
    cent_guard = property(lambda self: int(self._v("numerics", "fee_cent_rounding_guard")))

    @property
    def primary_feed(self) -> str:
        return str(self.config["data_feed"]["value"])

    @property
    def feeds(self) -> tuple[str, ...]:
        """The registered feeds: the primary and its fallback (section 6)."""
        fb = self.config["data_feed"].get("fallback")
        return (self.primary_feed,) if not fb else (self.primary_feed, str(fb))

    def half_spread(self, symbol: str) -> float:
        return float(self.tables["half_spread_usd"][symbol])

    def fingerprint(self) -> str:
        """sha256 of the schema, the whole config and the whole tables (canonical JSON)."""
        body = {"schema": SCHEMA, "config": self.config, "tables": self.tables}
        return hashlib.sha256(canonical_json(body).encode("ascii")).hexdigest()


def load_book_config(
    config_path: Path | str = DEFAULT_CONFIG, tables_path: Path | str = DEFAULT_TABLES
) -> BookConfig:
    with open(config_path, encoding="utf-8") as fh:
        config = json.load(fh)
    with open(tables_path, encoding="utf-8") as fh:
        tables = json.load(fh)
    return BookConfig(config, tables)


# ------------------------------------------------------------------ state ----
@dataclass(frozen=True)
class BookState:
    last_date: date | None
    positions: Mapping[str, float]  # shares held after the last record's fills
    targets: Mapping[str, float]  # the last record's targets
    orders: Mapping[str, float]  # pending: targets - positions, for the next session's close
    accrual_base: date | None = None  # the last record that is not a missing day (section 5 d)
    dropped: frozenset[str] = frozenset()  # delisted instruments (section 6), never re-entered
    cash_symbol: str | None = None  # the cash benchmark in effect (BIL, or SGOV after a switch)


def initial_state(config: BookConfig) -> BookState:
    zero = {s: 0.0 for s in config.symbols}
    return BookState(None, zero, dict(zero), {}, None, frozenset(), config.cash_symbol)


def state_from_record(record: Mapping[str, Any]) -> BookState:
    base = record.get("accrual_base")
    return BookState(
        date.fromisoformat(record["date"]),
        {s: float(q) for s, q in record["positions"].items()},
        {s: float(q) for s, q in record["targets"].items()},
        {s: float(q) for s, q in record["orders"].items()},
        date.fromisoformat(base) if base else None,
        frozenset(record.get("dropped", ())),
        record.get("cash", {}).get("symbol"),
    )


def row_from_record(record: Mapping[str, Any]) -> EtfDayRow | None:
    """The record's bars as a history row (None for a missing day)."""
    if not record.get("bars"):
        return None
    day = date.fromisoformat(record["date"])
    return EtfDayRow(day, {s: EtfBar.from_json(b) for s, b in record["bars"].items()})


def last_seen(history: Sequence[EtfDayRow]) -> dict[str, tuple[float, date]]:
    """{symbol: (last raw close, its session date)} over the history."""
    out: dict[str, tuple[float, date]] = {}
    for row in history:
        for s, bar in row.bars.items():
            out[s] = (bar.close, row.date)
    return out


# ------------------------------------------------------------------ dates ----
def check_date(state: BookState, trade_date: date, declared_closed: Sequence[date]) -> list[str]:
    """forward/runner.py's rule: refuse weekends, backwards dates and undeclared weekday gaps;
    return the declared closed dates (weekdays strictly inside the gap), sorted."""
    if trade_date.weekday() >= 5:
        raise RunnerError(f"{trade_date} is a weekend day, not a session")
    closed = sorted(set(declared_closed))
    if state.last_date is None:
        if closed:
            raise RunnerError("declared_closed is meaningless before the first record")
        return []
    if trade_date <= state.last_date:
        raise RunnerError(f"{trade_date} is not after the last ledger date {state.last_date}")
    gap = [
        state.last_date + timedelta(days=k) for k in range(1, (trade_date - state.last_date).days)
    ]
    weekdays = [d for d in gap if d.weekday() < 5]
    if any(d not in weekdays for d in closed):
        raise RunnerError("declared_closed dates must be weekdays strictly inside the gap")
    undeclared = [d.isoformat() for d in weekdays if d not in closed]
    if undeclared:
        raise RunnerError(
            f"weekday(s) {undeclared} between {state.last_date} and {trade_date} have no record; "
            "run them (missing data is recorded) or declare them exchange-closed"
        )
    return [d.isoformat() for d in closed]


# ------------------------------------------------------------------ costs ----
def ceil_cent(total: float, guard: int = 6) -> float:
    """Round a non-negative fee total up to the next 0.01 USD (noise below 10^-guard cent is
    ignored)."""
    if total <= 0:
        return 0.0
    return math.ceil(round(total * 100.0, guard)) / 100.0


def fill_legs(q_before: float, q_after: float) -> list[tuple[str, float]]:
    """Section 4 step 4: a sign change is reached by closing the old side and opening the new
    one."""
    if q_after == q_before:
        return []
    if (q_before > 0 > q_after) or (q_before < 0 < q_after):
        return [("close", _f(-q_before)), ("open", _f(q_after))]
    return [("trade", _f(q_after - q_before))]


def leg_record(symbol: str, leg: str, shares: float, price: float, cfg: BookConfig) -> dict:
    qty = abs(shares)
    sale = shares < 0
    notional = qty * price
    return {
        "symbol": symbol,
        "leg": leg,
        "shares": _f(shares),
        "price": price,
        "notional_usd": notional,
        "half_spread_usd": qty * cfg.half_spread(symbol),
        "sec_fee_usd": cfg.sec_rate * notional if sale else 0.0,
        "taf_usd": cfg.taf_per_share * qty if sale else 0.0,
        "cat_fee_usd": cfg.cat_per_share * qty,
    }


def session_costs(fills: Sequence[Mapping[str, Any]], cfg: BookConfig) -> dict[str, float]:
    """Half spreads (unrounded) plus each regulatory fee type summed over the session's fills and
    rounded up to the next cent (prereg section 5); commission per fill leg (0)."""
    spread = math.fsum(f["half_spread_usd"] for f in fills)
    guard = cfg.cent_guard
    sec = ceil_cent(math.fsum(f["sec_fee_usd"] for f in fills), guard)
    taf = ceil_cent(math.fsum(f["taf_usd"] for f in fills), guard)
    cat = ceil_cent(math.fsum(f["cat_fee_usd"] for f in fills), guard)
    commission = cfg.commission * len(fills)
    return {
        "half_spread": spread,
        "sec_fee": sec,
        "finra_taf": taf,
        "cat_fee": cat,
        "commission": commission,
        "total": math.fsum([spread, sec, taf, cat, commission]),
    }


# ------------------------------------------------------------------ late corporate actions ----
def _ca_types(cfg: BookConfig) -> tuple[frozenset[str], frozenset[str]]:
    """(distribution types, split types) from config late_corporate_actions."""
    block = cfg.config["late_corporate_actions"]
    return frozenset(block["distribution_types"]), frozenset(block["split_types"])


def _ca_key(a: Mapping[str, Any]) -> str:
    """Section 6 (B2): symbol, type, ex_date and the amount or ratio; two actions with the same
    symbol, type and ex_date but different amounts are two actions."""
    return f"{a['symbol']}|{a['type']}|{a['ex_date']}|{float(a['amount_or_ratio'])!r}"


def _is_split(a: Mapping[str, Any]) -> bool:
    return "split" in str(a["type"])


def _action_item(a: Mapping[str, Any], what: str) -> dict[str, Any]:
    """One corporate action as {symbol, type, ex_date, amount_or_ratio}, validated."""
    if set(a) != {"symbol", "type", "ex_date", "amount_or_ratio"}:
        raise RunnerError(f"{what} must have symbol, type, ex_date, amount_or_ratio: {a!r}")
    ex = date.fromisoformat(str(a["ex_date"])).isoformat()
    v = a["amount_or_ratio"]
    if isinstance(v, bool) or not _finite(v):
        raise RunnerError(f"{what} amount_or_ratio must be finite: {a!r}")
    item = {
        "symbol": str(a["symbol"]),
        "type": str(a["type"]),
        "ex_date": ex,
        "amount_or_ratio": float(v),
    }
    if _is_split(item) and not item["amount_or_ratio"] > 0:
        raise RunnerError(f"split ratio must be > 0: {a!r}")
    return item


def normalize_late_actions(actions: Sequence[Mapping[str, Any]] | None) -> list[dict[str, Any]]:
    """[{symbol, type, ex_date, amount_or_ratio}] validated, sorted, one per key (the key holds
    every field, so a repeated key is the same action offered twice)."""
    out: dict[str, dict[str, Any]] = {}
    for a in actions or ():
        item = _action_item(a, "late action")
        out[_ca_key(item)] = item
    return [out[k] for k in sorted(out)]


def normalize_applied(
    applied: Mapping[str, Sequence[Mapping[str, Any]]] | None,
) -> dict[str, list[dict[str, Any]]] | None:
    """Q23: the corporate actions counted inside each symbol's r when the session is recorded,
    {symbol: [{symbol, type, ex_date, amount_or_ratio}]}, validated and sorted. Every action is
    kept (two cash dividends on one ex_date are both counted in r). None: the source does not
    report them (no ``fetch_day``)."""
    if applied is None:
        return None
    out: dict[str, list[dict[str, Any]]] = {}
    for s, acts in sorted(applied.items()):
        items = [_action_item(a, f"applied action of {s}") for a in acts]
        if any(i["symbol"] != s for i in items):
            raise RunnerError(f"applied actions filed under {s} name another symbol: {items!r}")
        out[str(s)] = sorted(items, key=lambda i: (_ca_key(i), i["amount_or_ratio"]))
    return out


def _k_d(actions: Sequence[Mapping[str, Any]]) -> tuple[float, float]:
    """(k, D) of section 6: the product of the split ratios and the sum of the per-share amounts."""
    k, dist = 1.0, 0.0
    for a in actions:
        if _is_split(a):
            k *= float(a["amount_or_ratio"])
        else:
            dist += float(a["amount_or_ratio"])
    return k, dist


def session_return(
    close: float,
    ret: float,
    prev_close: float,
    recorded: Sequence[Mapping[str, Any]] | None,
    late: Sequence[Mapping[str, Any]],
) -> float:
    """Section 6's corrected return of one (symbol, session) from ALL its actions:
    k x (rawclose(t) + D) / rawclose(prev) - 1 with k and D over the actions stored in the record
    (``recorded``, Q23) and the booked ``late`` ones. ``recorded`` None (a source without
    ``fetch_day`` stored no actions): the recorded r is taken to contain no split, so
    1 + r = (1 + r_recorded) x k + k x D / rawclose(prev) with k and D of the late actions."""
    k, dist = _k_d(late)
    if recorded is None:
        return (1.0 + ret) * k + k * dist / prev_close - 1.0
    k0, d0 = _k_d(recorded)
    return k0 * k * (close + d0 + dist) / prev_close - 1.0


def seen_keys(records: Sequence[Mapping[str, Any]]) -> set[str]:
    """Keys of late actions already handled (booked, or flagged as an unbooked type)."""
    return {e["key"] for r in records for e in r.get("late_ca", [])}


def applied_keys(records: Sequence[Mapping[str, Any]]) -> set[str]:
    """Keys of corporate actions the source applied inside a recorded r (ca_applied)."""
    return {
        _ca_key(a) for r in records for acts in (r.get("ca_applied") or {}).values() for a in acts
    }


def _recorded_actions(record: Mapping[str, Any], symbol: str) -> list[Mapping[str, Any]] | None:
    """The actions the record stored as counted in ``symbol``'s r (None: none were stored)."""
    applied = record.get("ca_applied")
    return None if applied is None else list(applied.get(symbol, ()))


def _booked_late(entries: Sequence[Mapping[str, Any]], symbol: str, session: str) -> list:
    return [
        e for e in entries if e.get("booked") and e["symbol"] == symbol and e["session"] == session
    ]


def _ex_session(records: Sequence[Mapping[str, Any]], symbol: str, ex: str) -> Mapping | None:
    """The recorded session whose bar for ``symbol`` spans ``ex``: prev_date < ex <= date."""
    for r in records:
        bar = r.get("bars", {}).get(symbol)
        if bar is not None and (bar["prev_date"] or "") < ex <= r["date"]:
            return r
    return None


def _last_close(records: Sequence[Mapping[str, Any]], symbol: str) -> float | None:
    for r in reversed(records):
        if symbol in r.get("bars", {}):
            return float(r["bars"][symbol]["close"])
    return None


def _prev_close(rows: Sequence[EtfDayRow], symbol: str, session: str) -> float | None:
    """The symbol's close on its last stored session before ``session`` (warm-up included)."""
    out = None
    for row in rows:
        if row.date.isoformat() >= session:
            break
        if symbol in row.bars:
            out = row.bars[symbol].close
    return out


def _late_cash_dr(
    rec: Mapping[str, Any],
    symbol: str,
    action: Mapping[str, Any],
    booked_before: Sequence[Mapping[str, Any]],
    rows: Sequence[EtfDayRow],
) -> float:
    """Q21 dr_c of one late BIL action: the session's corrected return with this action minus
    the one without it (the recorded r when no late action of that session was booked before)."""
    session = rec["date"]
    bar = rec["bars"][symbol]
    if bar.get("ret") is None:
        raise RunnerError(f"{symbol}: the {session} record has no return to correct")
    prev = _prev_close(rows, symbol, session)
    if prev is None:
        raise RunnerError(f"{symbol}: no close before {session} for the late action")
    close, ret = float(bar["close"]), float(bar["ret"])
    recorded = _recorded_actions(rec, symbol)
    before = _booked_late(booked_before, symbol, session)
    r_before = session_return(close, ret, prev, recorded, before) if before else ret
    return session_return(close, ret, prev, recorded, [*before, action]) - r_before


def _batch_splits(
    actions: Sequence[Mapping[str, Any]],
    records: Sequence[Mapping[str, Any]],
    split_types: frozenset[str],
    handled: set[str],
) -> dict[tuple[str, str], list[Mapping[str, Any]]]:
    """The late splits of this batch that will be booked, by (symbol, ex session date)."""
    out: dict[tuple[str, str], list[Mapping[str, Any]]] = {}
    for a in actions:
        if a["type"] not in split_types or _ca_key(a) in handled:
            continue
        rec = _ex_session(records, a["symbol"], a["ex_date"])
        if rec is not None:
            out.setdefault((a["symbol"], rec["date"]), []).append(a)
    return out


def _session_split_k(
    rec: Mapping[str, Any],
    symbol: str,
    booked_before: Sequence[Mapping[str, Any]],
    batch_splits: Mapping[tuple[str, str], Sequence[Mapping[str, Any]]],
) -> float:
    """S2: the product of the split ratios of ``symbol``'s ex session ``rec``: those counted in
    its recorded r, the late ones booked in earlier records and the late ones of this batch."""
    splits: dict[str, Mapping[str, Any]] = {}
    for a in _recorded_actions(rec, symbol) or ():
        splits[_ca_key(a)] = a
    for e in _booked_late(booked_before, symbol, rec["date"]):
        splits[_ca_key(e)] = e
    for a in batch_splits.get((symbol, rec["date"]), ()):
        splits[_ca_key(a)] = a
    return _k_d([a for a in splits.values() if _is_split(a)])[0]


def late_corporate_actions(
    actions: Sequence[Mapping[str, Any]],
    records: Sequence[Mapping[str, Any]],
    cfg: BookConfig,
    rows: Sequence[EtfDayRow] = (),
) -> tuple[list[dict[str, Any]], dict[str, float], list[str], dict[str, int]]:
    """Section 6 late corporate actions against the records before t (``rows``: the stored
    history, for BIL's previous close). With q_ex the shares held into the ex_date session:
    a distribution books q_ex x k x amount as P&L, k the product of that session's split ratios
    (recorded, booked late before, and late in this batch; S2); a split adds (k - 1) x q_ex
    shares and books their
    value at the ETF's last recorded raw close as P&L; a BIL action of either kind books
    -L_ex x dr_c (Q21: L_ex the long notional held into BIL's ex_date session, dr_c the corrected
    minus the recorded BIL return of that session, the corrected one from ALL its actions by
    ``session_return``; when several late BIL actions share a session, each books only its
    increment over the actions booked before it, so their dr_c sum to corrected minus recorded).
    The cash branch applies to the session's cash benchmark (BIL, or SGOV after a switch).
    Flagged only: any other type of an ETF held into its ex_date session. Skipped without a flag:
    keys (symbol|type|ex_date|amount, B2) already handled in the ledger, keys the source applied
    inside a recorded r, actions whose ex_date is in no recorded session, actions of a cash
    symbol not in effect in that session. Returns (entries, extra shares per symbol, flags,
    skip counts); each entry's pnl_usd enters the fifth P&L term."""
    distribution_types, split_types = _ca_types(cfg)
    done, in_ret = seen_keys(records), applied_keys(records)
    earlier = [e for r in records for e in r.get("late_ca", [])]
    entries, extra, flags = [], {}, []
    skipped = {
        "already_handled": 0,
        "inside_recorded_return": 0,
        "not_in_a_recorded_session": 0,
        "not_held": 0,
    }
    for a in actions:
        if a["symbol"] not in cfg.read_universe:
            raise RunnerError(f"late action for a symbol outside the universe: {a!r}")
    batch_splits = _batch_splits(actions, records, split_types, done | in_ret)
    for a in actions:
        key, s = _ca_key(a), a["symbol"]
        if key in done:
            skipped["already_handled"] += 1
            continue
        if key in in_ret:
            skipped["inside_recorded_return"] += 1
            continue
        rec = _ex_session(records, s, a["ex_date"])
        if rec is None:
            skipped["not_in_a_recorded_session"] += 1
            continue
        is_cash = s == rec.get("cash", {}).get("symbol", cfg.cash_symbol)
        if not is_cash and s not in cfg.symbols:  # a cash symbol not in effect that session
            skipped["not_held"] += 1
            continue
        held = 0.0 if is_cash else float(rec["pnl_by_symbol"][s]["shares_held_into"])
        entry: dict[str, Any] = {
            "key": key,
            **a,
            "session": rec["date"],
            "shares_held_into": held,
            "extra_shares": 0.0,
            "value_price": None,
            "long_notional_ex_usd": None,
            "dr_c": None,
            "k": None,
            "pnl_usd": 0.0,
            "booked": False,
        }
        if is_cash and a["type"] in distribution_types | split_types:
            long_ex = (
                0.0
                if rec.get("missing_day")
                else float(rec["exposure"].get("long_notional_held_into_usd", 0.0))
            )
            dr_c = _late_cash_dr(rec, s, a, [*earlier, *entries], rows)
            entry.update(
                long_notional_ex_usd=long_ex, dr_c=dr_c, pnl_usd=_f(-long_ex * dr_c), booked=True
            )
            flags.append(f"late_ca:{s}")
        elif a["type"] in distribution_types:
            # S2: q_ex x k x amount, k the session's split ratios (recorded and late)
            k = _session_split_k(rec, s, [*earlier, *entries], batch_splits)
            entry.update(k=k, pnl_usd=_f(held * k * a["amount_or_ratio"]), booked=True)
            flags.append(f"late_ca:{s}")
        elif a["type"] in split_types:
            more = _f(held * (a["amount_or_ratio"] - 1.0))
            price = _last_close(records, s)
            entry.update(
                extra_shares=more,
                value_price=price,
                booked=True,
                pnl_usd=_f(more * price) if price is not None and more else 0.0,
            )
            if more:
                extra[s] = extra.get(s, 0.0) + more
            flags.append(f"late_ca:{s}")
        elif held != 0:
            flags.append(f"late_ca_unbooked:{s}:{a['type']}")
        else:
            skipped["not_held"] += 1
            continue
        entries.append(entry)
    return entries, extra, flags, skipped


def corrected_rows(
    rows: Sequence[EtfDayRow],
    entries: Sequence[Mapping[str, Any]],
    records: Sequence[Mapping[str, Any]] = (),
) -> tuple[EtfDayRow, ...]:
    """Section 6: for the signal series, the ex_date session's return of each booked late split
    or distribution is the corrected one, from ALL the session's actions (Q23): those the
    session's record stored as counted in its r (``records``' ca_applied) and the booked late
    ``entries`` of that (symbol, session), by ``session_return``. Recorded days are unchanged:
    this returns new rows for the rule only."""
    fixes: dict[tuple[str, str], list[Mapping[str, Any]]] = {}
    for e in entries:
        if e.get("booked") and e.get("session"):
            fixes.setdefault((e["symbol"], e["session"]), []).append(e)
    if not fixes:
        return tuple(rows)
    by_date = {r["date"]: r for r in records}
    out, last = [], {}
    for row in rows:
        bars, changed, day = dict(row.bars), False, row.date.isoformat()
        for s, bar in row.bars.items():
            late = fixes.get((s, day))
            if late is not None and bar.ret is not None and s in last:
                rec = by_date.get(day)
                recorded = None if rec is None else _recorded_actions(rec, s)
                r = session_return(bar.close, bar.ret, last[s], recorded, late)
                bars[s] = EtfBar(bar.close, r, bar.prev_date)
                changed = True
            last[s] = bar.close
        out.append(EtfDayRow(row.date, bars) if changed else row)
    return tuple(out)


# ------------------------------------------------------------------ recorded returns ----
@dataclass
class _Bars:
    """The session's bars as the book uses them (section 6) and what the source delivered."""

    bars: dict[str, EtfBar]  # the book's bars: r from the recorded previous close (B1)
    source: dict[str, Any]  # the source's bars as delivered (to_json), for the record
    kd: dict[str, tuple[float, float]]  # (k, D) of each r computed by the book
    applied: dict[str, list[dict[str, Any]]] | None  # the actions counted in each r
    checks: dict[str, dict[str, float]]  # prev_close_check: recorded and source previous close
    suspect: dict[str, int]  # suspect_split: sessions so far without a split covering the move
    flags: list[str]


def _suspect_count(records: Sequence[Mapping[str, Any]], symbol: str, since: date) -> int:
    """Records after ``since`` (the symbol's last recorded close) in which it was suspect."""
    after = since.isoformat()
    return sum(1 for r in records if r["date"] > after and symbol in (r.get("suspect_split") or {}))


def _source_prev_close(bar: EtfBar, actions: Sequence[Mapping[str, Any]]) -> float:
    """The source's own previous close implied by its bar and the actions inside its r:
    k x (rawclose(t) + D) / (1 + r)."""
    k, dist = _k_d(actions)
    return k * (bar.close + dist) / (1.0 + float(bar.ret))


def recorded_bars(
    found: Mapping[str, EtfBar],
    marks: Mapping[str, tuple[float, date]],
    applied: Mapping[str, Sequence[Mapping[str, Any]]] | None,
    source_applied: Mapping[str, Sequence[Mapping[str, Any]]] | None,
    records: Sequence[Mapping[str, Any]],
    cfg: BookConfig,
    dropped: frozenset[str],
) -> _Bars:
    """Section 6 on the source's bars. ``applied``: the actions with ex_date in (prev, t] for each
    symbol (the source's corporate actions over the whole span; None for a source without
    ``fetch_day``, whose own r is then used unchanged). With prev the symbol's last recorded
    session and rawclose(prev) the recorded close (``marks``), never the source's copy:
    r = k x (rawclose(t) + D) / rawclose(prev) - 1 (B1); the source's own previous close is checked
    against the recorded one when the source's previous session is the recorded one, and a
    relative difference above prev_close_mismatch_rel is flagged prev_close_mismatch:SYM.
    Suspect split (S6): an instrument whose raw close moves by more than the ratio either way
    with no split in (prev, t] is treated as having no bar on t (suspect_split:SYM) for at most
    suspect_split_max_sessions sessions, then accepted (suspect_split_accepted:SYM). Dropped
    (delisted) instruments are ignored."""
    out = _Bars({}, {s: b.to_json() for s, b in found.items()}, {}, None, {}, {}, [])
    if applied is not None:
        out.applied = {}
    for s, sb in found.items():
        if s in dropped:
            continue
        mark = marks.get(s)
        if applied is None:
            out.bars[s] = sb
            continue
        if mark is None:  # no recorded close yet: no return on t
            out.bars[s] = EtfBar(sb.close)
            continue
        acts = list(applied.get(s, ()))
        if sb.prev_date != mark[1]:
            out.flags.append(f"prev_date_mismatch:{s}")
        moved = abs(math.log(sb.close / mark[0])) > math.log(cfg.suspect_ratio)
        if s in cfg.symbols and moved and not any(_is_split(a) for a in acts):
            n = _suspect_count(records, s, mark[1])
            if n < cfg.suspect_max:
                out.suspect[s] = n + 1
                continue
            out.flags.append(f"suspect_split_accepted:{s}")
        k, dist = _k_d(acts)
        out.bars[s] = EtfBar(sb.close, k * (sb.close + dist) / mark[0] - 1.0, mark[1])
        out.kd[s] = (k, dist)
        if acts:
            out.applied[s] = acts
        if sb.ret is not None and sb.prev_date == mark[1]:
            src_prev = _source_prev_close(sb, (source_applied or {}).get(s, ()))
            out.checks[s] = {"recorded": mark[0], "source": src_prev}
            if abs(src_prev - mark[0]) > cfg.prev_close_rel * mark[0]:
                out.flags.append(f"prev_close_mismatch:{s}")
    return out


def _no_bar_streak(records: Sequence[Mapping[str, Any]], symbol: str) -> int:
    """S7: consecutive earlier records that are not missing days in which ``symbol`` had no bar
    (flag missing:SYM); missing days neither count nor break the run."""
    flag, n = f"missing:{symbol}", 0
    for r in reversed(records):
        if r.get("missing_day"):
            continue
        if flag not in r.get("flags", ()):
            break
        n += 1
    return n


def _without(rows: Sequence[EtfDayRow], dropped: frozenset[str]) -> tuple[EtfDayRow, ...]:
    """The history without the dropped instruments (S7: weights and IDM over the rest)."""
    if not dropped:
        return tuple(rows)
    out = []
    for row in rows:
        bars = {s: b for s, b in row.bars.items() if s not in dropped}
        if len(bars) == len(row.bars):
            out.append(row)
        elif bars:
            out.append(EtfDayRow(row.date, bars))
    return tuple(out)


# ------------------------------------------------------------------ one session ----
@dataclass
class _Day:
    """Mutable accumulator for one session."""

    before_fills: dict[str, float] = field(default_factory=dict)
    after_fills: dict[str, float] = field(default_factory=dict)
    share_update: dict[str, float] = field(default_factory=dict)
    fills: list[dict[str, Any]] = field(default_factory=list)
    expired: dict[str, float] = field(default_factory=dict)
    by_symbol: dict[str, dict[str, Any]] = field(default_factory=dict)
    flags: list[str] = field(default_factory=list)
    with_bar: list[str] = field(default_factory=list)


def _symbol_day(
    s: str,
    bar: EtfBar | None,
    state: BookState,
    mark: tuple[float, date] | None,
    cfg: BookConfig,
    day: _Day,
    kd: tuple[float, float] | None = None,
    no_bar_flag: str = "missing",
) -> None:
    """Steps 3-4 and the per-symbol P&L inputs for one ETF. ``kd``: the (k, D) of the book's r
    (section 5 share update k x (rawclose(t) + D) / rawclose(t)); None for a source without
    ``fetch_day`` (rawclose(prev) x (1 + r) / rawclose(t) with the source's r)."""
    q = float(state.positions.get(s, 0.0))
    if q != 0 and mark is None:
        raise RunnerError(f"{s}: holds {q} shares but has no previous close")
    notional = q * mark[0] if q != 0 else 0.0
    entry: dict[str, Any] = {
        "shares_held_into": _f(q),
        "notional_held_into": _f(notional),
        "ret": None,
        "etf_pnl": 0.0,
    }
    day.by_symbol[s] = entry
    if bar is None:
        day.flags.append(f"{no_bar_flag}:{s}")
        if s in state.orders:
            day.expired[s] = state.orders[s]
            day.flags.append(f"order_expired:{s}")
        day.before_fills[s] = day.after_fills[s] = _f(q)
        return
    day.with_bar.append(s)
    if mark is not None and bar.prev_date != mark[1]:
        day.flags.append(f"prev_date_mismatch:{s}")
    q1 = q
    if q != 0:
        if bar.ret is None:
            raise RunnerError(f"{s}: holds {q} shares but its bar has no total return")
        if kd is not None:
            factor = kd[0] * (bar.close + kd[1]) / bar.close
        else:
            factor = mark[0] * (1.0 + bar.ret) / bar.close
        if abs(factor - 1.0) <= cfg.share_tolerance:
            factor = 1.0
        q1 = _f(q * factor)
        day.share_update[s] = factor
        entry["ret"] = bar.ret
        entry["etf_pnl"] = notional * bar.ret
    day.before_fills[s] = q1
    if s not in state.orders:
        day.after_fills[s] = q1
        return
    # the pending order was target - q; q may have changed by the share update since
    new = _f(float(state.targets[s]) + (q1 - q))
    for leg, shares in fill_legs(q1, new):
        day.fills.append(leg_record(s, leg, shares, bar.close, cfg))
    day.after_fills[s] = new


def _pnl(day: _Day, r_c: float | None, d: int, cfg: BookConfig) -> dict[str, float]:
    """Section 5's four terms (USD)."""
    notional = [e["notional_held_into"] for e in day.by_symbol.values()]
    etf = math.fsum(e["etf_pnl"] for e in day.by_symbol.values())
    rc = 0.0 if r_c is None else r_c
    excess = etf - rc * math.fsum(notional)
    short_notional = math.fsum(-n for n in notional if n < 0)
    accrual = d / cfg.day_count
    shorts = -short_notional * (rc + cfg.borrow_b * accrual)
    long_notional = math.fsum(n for n in notional if n > 0)
    leverage = -max(0.0, long_notional - cfg.capital) * cfg.margin_s * accrual
    return {
        "excess": _f(excess),
        "shorts": _f(shorts),
        "leverage": _f(leverage),
        "long_notional_held_into": long_notional,
        "short_notional_held_into": short_notional,
    }


def _validate_targets(out: Any, cfg: BookConfig) -> dict[str, float]:
    if not isinstance(out, Mapping):
        raise RunnerError(f"target function must return a mapping, got {type(out).__name__}")
    unknown = sorted(set(out) - set(cfg.symbols))
    if unknown:
        raise RunnerError(f"target function returned unknown symbols {unknown}")
    targets = {}
    for s in cfg.symbols:
        if s not in out:
            raise RunnerError(f"target function omitted {s}")
        v = out[s]
        if isinstance(v, bool) or not isinstance(v, numbers.Real) or not math.isfinite(v):
            raise RunnerError(f"{s}: target {v!r} is not a finite number of shares")
        targets[s] = _f(v)
    return targets


def _default_target(
    history: Any, held: Mapping[str, float], config: Mapping[str, Any], *, decision_date: date
) -> strategy_f2.Decision:
    return strategy_f2.decide(history, held, config, decision_date=decision_date)


def step(
    state: BookState,
    trade_date: date,
    raw_day: Any,
    history_before: Sequence[EtfDayRow],
    cfg: BookConfig,
    *,
    fingerprint: str,
    warmup_sha256: str,
    declared_closed: Sequence[date] = (),
    target_fn: TargetFn | None = None,
    late_actions: Sequence[Mapping[str, Any]] = (),
    records_before: Sequence[Mapping[str, Any]] = (),
    ca_applied: Mapping[str, Sequence[Mapping[str, Any]]] | None = None,
    ca_other: Mapping[str, Sequence[str]] | None = None,
    feed: str | None = None,
    source_applied: Mapping[str, Sequence[Mapping[str, Any]]] | None = None,
) -> dict[str, Any]:
    """One session's ledger payload (no hashes) from the state before it. Pure. ``late_actions``
    (normalised) are booked against ``records_before`` (section 6 late corporate actions);
    ``feed`` is the operative data feed, stored in the record (section 6). ``ca_applied``: each
    symbol's corporate actions with ex_date in (prev, t], prev its last recorded session
    ({symbol: [{symbol, type, ex_date, amount_or_ratio}]}: the source's corporate actions over the
    whole span, B1); the ones counted in an r are stored in the record (Q23), a missing day's
    included; None for a source without ``fetch_day`` (its own r is used). ``source_applied``:
    the actions inside the source's own r, used only to check its previous close (B1)."""
    closed = check_date(state, trade_date, declared_closed)
    applied = normalize_applied(ca_applied)
    src_applied = normalize_applied(source_applied)
    other = None if ca_other is None else {s: sorted(v) for s, v in sorted(ca_other.items())}
    raw = normalize_etf_day(raw_day, trade_date, f"bars {trade_date}")
    source_found = {} if isinstance(raw, Missing) else raw
    unknown = sorted(set(source_found) - set(cfg.read_universe))
    if unknown:
        raise RunnerError(f"bars for symbols outside the universe: {unknown}")
    # section 5: d from the last earlier record that is not a missing day
    d = (trade_date - state.accrual_base).days if state.accrual_base is not None else 0
    dropped = state.dropped
    cash_sym = state.cash_symbol or cfg.cash_symbol
    marks = last_seen(history_before)
    rb = recorded_bars(source_found, marks, applied, src_applied, records_before, cfg, dropped)
    found = rb.bars
    base = {
        "schema": SCHEMA,
        "test_id": TEST_ID,
        "date": trade_date.isoformat(),
        "config_sha256": fingerprint,
        "warmup_sha256": warmup_sha256,
        "feed": feed if feed is not None else cfg.primary_feed,
        "declared_closed": closed,
    }
    data = {
        "source_bars": rb.source,
        "prev_close_check": rb.checks,
        "suspect_split": rb.suspect,
    }
    held_in = {s: _f(state.positions.get(s, 0.0)) for s in cfg.symbols}
    if not any(s in found for s in cfg.symbols):  # section 6: no bar for any of the 11 ETFs
        reason = str(raw.reason) if isinstance(raw, Missing) else "no bar for any of the 11 ETFs"
        flags = [
            "missing_day",
            *(f"order_expired:{s}" for s in sorted(state.orders)),
            *(f"late_ca_deferred:{a['symbol']}" for a in late_actions),
            *rb.flags,
            *(f"suspect_split:{s}" for s in rb.suspect),
        ]
        zero_costs = {
            "half_spread": 0.0,
            "sec_fee": 0.0,
            "finra_taf": 0.0,
            "cat_fee": 0.0,
            "commission": 0.0,
            "total": 0.0,
        }
        return {
            **base,
            "missing_day": True,
            "missing_reason": reason,
            "accrual_days": 0,
            "accrual_base": None if state.accrual_base is None else state.accrual_base.isoformat(),
            "bars": {s: b.to_json() for s, b in found.items()},
            **data,
            "cash": {"symbol": cash_sym, "r_c": None},
            "positions_before_fills": held_in,
            "share_update": {},
            "fills": [],
            "expired_orders": dict(sorted(state.orders.items())),
            "costs": zero_costs,
            "pnl": {"excess": 0.0, "shorts": 0.0, "leverage": 0.0, "costs": 0.0, "late_ca": 0.0},
            "late_ca_input": list(late_actions),
            "late_ca": [],
            "late_ca_skipped": {},
            "ca_applied": rb.applied,
            "ca_other": other,
            "net_pnl": 0.0,
            "pnl_by_symbol": {},
            "positions": held_in,
            "targets": dict(held_in),
            "orders": {},
            "signals": {},
            "exposure": {"cap_usd": cfg.cap_usd, "cap_bound": False, "decision": False},
            "dropped": sorted(dropped),
            "flags": sorted(set(flags)),
        }
    entries, extra, late_flags, late_skipped = late_corporate_actions(
        late_actions, records_before, cfg, history_before
    )
    if extra:
        pos, tgt = dict(state.positions), dict(state.targets)
        for s, more in extra.items():
            if s in dropped:  # the position was closed at the last recorded close (S7)
                late_flags.append(f"late_ca_dropped:{s}")
                continue
            pos[s] = _f(pos.get(s, 0.0) + more)
            tgt[s] = _f(tgt.get(s, 0.0) + more)
        state = replace(state, positions=pos, targets=tgt)
    day = _Day()
    day.flags.extend([*late_flags, *rb.flags])
    delist = []
    for s in cfg.symbols:
        if s in dropped:
            q = _f(state.positions.get(s, 0.0))
            day.by_symbol[s] = {
                "shares_held_into": q,
                "notional_held_into": 0.0,
                "ret": None,
                "etf_pnl": 0.0,
            }
            day.before_fills[s] = day.after_fills[s] = q
            continue
        kd = rb.kd.get(s) if applied is not None else None
        flag = "suspect_split" if s in rb.suspect else "missing"
        _symbol_day(s, found.get(s), state, marks.get(s), cfg, day, kd, flag)
        streak = _no_bar_streak(records_before, s) + 1
        if s not in source_found and streak >= cfg.delisting_sessions:
            delist.append(s)
    for s in delist:  # S7: closed at the last recorded close as a fill with costs, dropped
        q = day.after_fills[s]
        if q != 0:
            day.fills.append(leg_record(s, "delist", _f(-q), marks[s][0], cfg))
            day.after_fills[s] = 0.0
        day.flags.append(f"delisted:{s}")
    dropped_now = dropped | frozenset(delist)
    for s, notes in sorted((ca_other or {}).items()):
        if notes and s in day.by_symbol and day.by_symbol[s]["shares_held_into"] != 0:
            day.flags.append(f"ca_other:{s}")
    rep = cfg.cash_replacement
    if (
        cash_sym == cfg.cash_symbol
        and rep is not None
        and cash_sym not in found
        and _no_bar_streak(records_before, cash_sym) + 1 >= cfg.cash_replacement_after
    ):  # S7: BIL without a bar in 10 consecutive sessions that are not missing days
        day.flags.append(f"missing:{cash_sym}")
        cash_sym = rep
    if cash_sym != cfg.cash_symbol:
        day.flags.append(f"cash_benchmark:{cash_sym}")
    cash_bar = found.get(cash_sym)
    r_c = cash_bar.ret if cash_bar is not None else None
    if cash_bar is None:
        day.flags.append(f"missing:{cash_sym}")
    elif cash_bar.ret is None:
        day.flags.append(f"no_return:{cash_sym}")
    elif cash_sym in marks and cash_bar.prev_date != marks[cash_sym][1]:
        day.flags.append(f"prev_date_mismatch:{cash_sym}")
    costs = session_costs(day.fills, cfg)
    terms = _pnl(day, r_c, d, cfg)
    pnl = {
        "excess": terms["excess"],
        "shorts": terms["shorts"],
        "leverage": terms["leverage"],
        "costs": _f(-costs["total"]),
        "late_ca": _f(math.fsum(e["pnl_usd"] for e in entries)),
    }
    held = dict(day.after_fills)
    targets, signals, exposure = dict(held), {}, {"decision": False}
    if day.with_bar:
        row = EtfDayRow(trade_date, found)
        fn = target_fn if target_fn is not None else _default_target
        booked = [e for r in records_before for e in r.get("late_ca", [])] + entries
        rows = corrected_rows((*history_before, row), booked, records_before)
        out = fn(
            _without(rows, dropped_now),
            dict(held),
            copy.deepcopy(dict(cfg.config)),
            decision_date=trade_date,
        )
        if isinstance(out, strategy_f2.Decision):
            signals, exposure = out.signals, {**out.exposure, "decision": True}
            out = out.targets
        else:
            exposure = {"decision": True}
        proposed = _validate_targets(out, cfg)
        for s in day.with_bar:
            targets[s] = proposed[s]
    orders = {s: _f(targets[s] - held[s]) for s in day.with_bar if targets[s] != held[s]}
    held_gross = math.fsum(
        abs(q) * (found[s].close if s in found else marks[s][0]) for s, q in held.items() if q != 0
    )
    exposure = {
        "cap_usd": cfg.cap_usd,
        "cap_bound": bool(exposure.get("cap_bound", False)),
        **exposure,
        "held_gross_usd": held_gross,
        "long_notional_held_into_usd": terms["long_notional_held_into"],
        "short_notional_held_into_usd": terms["short_notional_held_into"],
    }
    return {
        **base,
        "missing_day": False,
        "accrual_days": d,
        "accrual_base": trade_date.isoformat(),
        "bars": {s: b.to_json() for s, b in found.items()},
        **data,
        "cash": {"symbol": cash_sym, "r_c": r_c},
        "positions_before_fills": dict(day.before_fills),
        "share_update": dict(sorted(day.share_update.items())),
        "fills": day.fills,
        "expired_orders": dict(sorted(day.expired.items())),
        "costs": costs,
        "pnl": pnl,
        "net_pnl": _f(math.fsum(pnl.values())),
        "pnl_by_symbol": day.by_symbol,
        "late_ca_input": list(late_actions),
        "late_ca": entries,
        "late_ca_skipped": late_skipped,
        "ca_applied": rb.applied,
        "ca_other": other,
        "positions": held,
        "targets": targets,
        "orders": orders,
        "signals": signals,
        "exposure": exposure,
        "dropped": sorted(dropped_now),
        "flags": sorted(set(day.flags)),
    }


# ------------------------------------------------------------------ the book ----
def _applied_item(a: Any) -> dict[str, Any]:
    """A forward.sources_alpaca CorporateAction counted in r as a stored action (Q23)."""
    value = a.ratio if "split" in str(a.kind) else a.amount
    return {
        "symbol": str(a.symbol),
        "type": str(a.kind),
        "ex_date": a.ex_date.isoformat(),
        "amount_or_ratio": value,  # validated by normalize_applied (None is refused)
    }


def read_day(source: EtfBarSource, trade_date: date) -> tuple[Any, dict | None, dict | None]:
    """The day's bars, plus (when the source offers ``fetch_day``, as forward.sources_alpaca does)
    the corporate actions applied inside each r ({symbol: [{symbol, type, ex_date,
    amount_or_ratio}]}, Q23: a split's ratio, a distribution's per-share amount) and the other
    corporate action notes ({symbol: [text]}). Other sources: (bars, None, None)."""
    fetch = getattr(source, "fetch_day", None)
    if not callable(fetch):
        return source.bars(trade_date), None, None
    got = fetch(trade_date)
    applied = {
        str(s): [_applied_item(a) for a in acts if a.ex_date is not None]
        for s, acts in dict(getattr(got, "applied", {}) or {}).items()
    }
    other = {
        str(s): [str(x) for x in notes]
        for s, notes in dict(getattr(got, "flags", {}) or {}).items()
        if notes
    }
    return got.answer(), applied, other


def span_actions(
    source: Any,
    raw: Any,
    marks: Mapping[str, tuple[float, date]],
    trade_date: date,
    cfg: BookConfig,
    dropped: frozenset[str] = frozenset(),
) -> tuple[dict[str, list[dict[str, Any]]], dict[str, list[str]]]:
    """B1: each symbol's corporate actions with ex_date in (prev, t], prev its last recorded
    session (``marks``), from the source's ``corporate_actions(start, end, symbols)`` queried over
    the whole span (start = prev + 1 day, end = t; one query per distinct prev). Returns (the
    split and distribution actions as stored items, other-type notes)."""
    fetch = getattr(source, "corporate_actions", None)
    if not callable(fetch):
        raise RunnerError(
            "a source with fetch_day must offer corporate_actions(start, end, symbols) "
            "(section 6: k and D over the whole span (prev, t])"
        )
    distribution_types, split_types = _ca_types(cfg)
    spans: dict[date, list[str]] = {}
    for s in sorted(raw if isinstance(raw, Mapping) else ()):
        if s in marks and s not in dropped:
            spans.setdefault(marks[s][1], []).append(s)
    applied: dict[str, list[dict[str, Any]]] = {}
    other: dict[str, list[str]] = {}
    for prev, syms in sorted(spans.items()):
        got = fetch(prev + timedelta(days=1), trade_date, syms)
        for a in got.booked:
            if a.symbol not in syms or a.ex_date is None or not prev < a.ex_date <= trade_date:
                continue
            if a.kind in distribution_types | split_types:
                applied.setdefault(a.symbol, []).append(_applied_item(a))
            else:
                other.setdefault(a.symbol, []).append(f"{a.kind} ex_date {a.ex_date}")
        for a in got.other:
            if a.symbol in syms and (a.ex_date is None or prev < a.ex_date <= trade_date):
                other.setdefault(a.symbol, []).append(f"{a.kind} ex_date {a.ex_date}")
    return applied, other


class PaperBookF2:
    """The E22-F2 paper book over one ledger file. Stateless between calls."""

    def __init__(
        self,
        ledger_path: Path | str,
        source: EtfBarSource,
        config: BookConfig,
        *,
        warmup: Sequence[EtfDayRow] = (),
        target_fn: TargetFn | None = None,
        feed: str | None = None,
    ):
        self.ledger = Ledger(ledger_path)
        self.source = source
        self.config = config
        self.feed = config.primary_feed if feed is None else str(feed)
        if self.feed not in config.feeds:
            raise RunnerError(f"feed {self.feed!r} is not a registered feed {config.feeds}")
        self.warmup = tuple(warmup)
        self.warmup_sha256 = etf_history_sha256(self.warmup)
        self.fingerprint = config.fingerprint()
        self._target_fn = target_fn

    def _load(self) -> list[dict[str, Any]]:
        records = self.ledger.records()
        for r in records:
            if r.get("schema") != SCHEMA:
                raise RunnerError(f"ledger record {r['date']} is not an {SCHEMA} record")
            if r.get("config_sha256") != self.fingerprint:
                raise RunnerError(f"ledger record {r['date']} was made under another configuration")
            if r.get("warmup_sha256") != self.warmup_sha256:
                raise RunnerError(
                    f"ledger record {r['date']} was made with another warm-up history"
                )
            if r.get("feed") != self.feed:
                raise RunnerError(
                    f"ledger record {r['date']} used feed {r.get('feed')!r}, not {self.feed!r}; "
                    "the feed is fixed before the first record"
                )
        return records

    def state(self) -> BookState:
        records = self._load()
        return state_from_record(records[-1]) if records else initial_state(self.config)

    def history(self, records: Sequence[Mapping[str, Any]]) -> tuple[EtfDayRow, ...]:
        rows = [r for r in (row_from_record(x) for x in records) if r is not None]
        return (*self.warmup, *rows)

    def _compute(
        self,
        records: list[dict[str, Any]],
        trade_date: date,
        declared_closed: Sequence[date],
        late_actions: Sequence[Mapping[str, Any]] = (),
    ) -> dict[str, Any]:
        if self.warmup and self.warmup[-1].date >= trade_date:
            raise RunnerError(f"{trade_date} is not after the last warm-up row")
        state = state_from_record(records[-1]) if records else initial_state(self.config)
        check_date(state, trade_date, declared_closed)  # refuse before reading the source
        raw, source_applied, other = read_day(self.source, trade_date)
        history = self.history(records)
        applied = None
        if source_applied is not None:  # B1: k and D over the recorded span (prev, t]
            applied, span_other = span_actions(
                self.source, raw, last_seen(history), trade_date, self.config, state.dropped
            )
            for s, notes in span_other.items():
                other[s] = sorted({*other.get(s, ()), *notes})
        return step(
            state,
            trade_date,
            raw,
            history,
            self.config,
            fingerprint=self.fingerprint,
            warmup_sha256=self.warmup_sha256,
            declared_closed=declared_closed,
            target_fn=self._target_fn,
            late_actions=normalize_late_actions(late_actions),
            records_before=records,
            ca_applied=applied,
            ca_other=other,
            feed=self.feed,
            source_applied=source_applied,
        )

    def run_date(
        self,
        trade_date: date,
        *,
        declared_closed: Sequence[date] = (),
        late_actions: Sequence[Mapping[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Process ``trade_date``; returns the stored ledger record. ``late_actions``: corporate
        actions published after the record of their ex_date session (section 6); on a re-run of a
        recorded date, None reuses the stored record's input."""
        records = self._load()
        index = next(
            (k for k, r in enumerate(records) if r["date"] == trade_date.isoformat()), None
        )
        if index is None:
            if records and trade_date < date.fromisoformat(records[-1]["date"]):
                raise RunnerError(
                    f"{trade_date} is before the last ledger date and not in the "
                    "ledger; out-of-order dates are refused"
                )
            return self.ledger.append(
                self._compute(records, trade_date, declared_closed, late_actions or ())
            )
        stored = records[index]
        closed = declared_closed or [date.fromisoformat(x) for x in stored["declared_closed"]]
        late = stored.get("late_ca_input", []) if late_actions is None else late_actions
        again = self._compute(records[:index], trade_date, closed, late)
        if canonical_json(again) != canonical_json(strip_hashes(stored)):
            diff = sorted(
                k for k in again if canonical_json(again[k]) != canonical_json(stored.get(k))
            )
            raise LedgerConflictError(f"re-run of {trade_date} differs from the ledger in {diff}")
        return stored

    def run_dates(self, dates: Sequence[date]) -> list[dict[str, Any]]:
        return [self.run_date(d) for d in dates]


def summary_line(record: Mapping[str, Any]) -> str:
    return (
        f"{record['date']} net_pnl={record['net_pnl']:.2f} fills={len(record['fills'])} "
        f"flags={len(record['flags'])} sha={record['record_sha256'][:12]}"
    )


def _main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="python -m forward.runner_f2", description=__doc__.split("\n")[0]
    )
    ap.add_argument("--ledger", required=True)
    ap.add_argument("--csv", required=True, help="ETF bar CSV (forward.etf_bars format)")
    ap.add_argument("--config", default=str(DEFAULT_CONFIG))
    ap.add_argument("--tables", default=str(DEFAULT_TABLES))
    ap.add_argument("--warmup", help="warm-up JSONL (forward.etf_bars format)")
    ap.add_argument("--date", required=True, help="session date YYYY-MM-DD (America/New_York)")
    ap.add_argument("--closed", nargs="*", default=[], help="declared exchange-closed weekdays")
    args = ap.parse_args(argv)
    cfg = load_book_config(args.config, args.tables)
    book = PaperBookF2(
        args.ledger,
        CsvEtfSource(args.csv, cfg.read_universe),
        cfg,
        warmup=load_etf_warmup(args.warmup) if args.warmup else (),
    )
    record = book.run_date(
        date.fromisoformat(args.date), declared_closed=[date.fromisoformat(x) for x in args.closed]
    )
    print(summary_line(record))
    return 0


if __name__ == "__main__":
    sys.exit(_main())


__all__ = [
    "SCHEMA",
    "TEST_ID",
    "BookConfig",
    "BookState",
    "LedgerConflictError",
    "PaperBookF2",
    "RunnerError",
    "ceil_cent",
    "check_date",
    "fill_legs",
    "initial_state",
    "load_book_config",
    "session_costs",
    "state_from_record",
    "step",
    "summary_line",
]
