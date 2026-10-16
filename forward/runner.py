"""E22-F1 paper runner: one call per trade date, in order (ForwardRunnerCoder, E.22).

For trade date t the runner:
1. reads t's settlements from the source;
2. fills the orders pending from the previous processed date at t's settlement (paper fills in
   the reference contract; cost = |contracts| x the instrument's cost per contract per side);
3. rolls positions whose reference contract is due to roll (close and open at t's settlements,
   two fills per contract, costs as in 2); a flat instrument's reference switches without fills;
4. marks to market: gross P&L_i = q_i(t-1) x (p_i(t) - mark_i(t-1)) x multiplier_i, USD; fills
   and rolls happen at t's settlement and so add no gross P&L on t; net = gross - costs;
5. calls the target function with the history through t and the positions after 2-3;
6. records the new orders (target positions) for the next processed date's settlement.

Missing data: an instrument whose reference contract has no settlement on t gets no fill (its
pending order expires, flagged), no new order, keeps its position marked at the last price, and
the day is flagged. A missing whole day is a no-trade day: every pending order expires, nothing
is filled or ordered, P&L is 0, the record is flagged ``missing_day``. Orders are valid for the
next processed date only. Integer contracts only.

State is rebuilt from the ledger on every call. Re-running a date already in the ledger
recomputes it from the previous record and returns the stored record unchanged when it matches;
a mismatch raises LedgerConflictError. Nothing is ever written twice for a date.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib
import json
import math
import numbers
import sys
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path
from typing import Any

from forward import rolls as R
from forward.history import (
    HistoryRow,
    check_ascending,
    history_fingerprint,
    load_warmup,
    row_from_record,
)
from forward.ledger import Ledger, canonical_json, strip_hashes
from forward.sources import (
    CsvSettlementSource,
    DaySettlements,
    Missing,
    SettlementSource,
    normalize_day,
)

SCHEMA = "E22-F1-ledger/1"
TargetFn = Callable[[tuple[HistoryRow, ...], dict[str, int], Mapping[str, Any]], Mapping[str, Any]]


class RunnerError(Exception):
    """A refused runner call (bad date, gap, config mismatch, bad target)."""


class LedgerConflictError(RunnerError):
    """A re-run of a recorded date produced a different record."""


@dataclass(frozen=True)
class Position:
    contract: str | None = None
    qty: int = 0
    mark: float | None = None
    mark_date: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "contract": self.contract,
            "qty": self.qty,
            "mark": self.mark,
            "mark_date": self.mark_date,
        }


@dataclass(frozen=True)
class RunnerState:
    last_date: date | None
    positions: Mapping[str, Position]
    pending: Mapping[str, int]


@dataclass(frozen=True)
class RunnerConfig:
    """Frozen inputs: per-instrument multipliers (USD per 1.0 of quoted price per contract) and
    costs (USD per contract per side), the roll specs, and the strategy config passed through."""

    multipliers: Mapping[str, float]
    cost_per_side: Mapping[str, float]
    rolls: Mapping[str, R.InstrumentRoll]
    strategy_config: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        names = set(self.multipliers)
        if not names or set(self.cost_per_side) != names:
            raise RunnerError("multipliers and cost_per_side must cover the same instruments")
        if not names <= set(self.rolls):
            raise RunnerError(f"no roll spec for {sorted(names - set(self.rolls))}")
        for name in names:
            m, c = self.multipliers[name], self.cost_per_side[name]
            if not (_finite(m) and m > 0 and _finite(c) and c >= 0):
                raise RunnerError(f"{name}: multiplier must be > 0 and cost >= 0, both finite")

    @property
    def instruments(self) -> tuple[str, ...]:
        return tuple(sorted(self.multipliers))

    def fingerprint(self, warmup_sha256: str) -> str:
        body = {
            "schema": SCHEMA,
            "multipliers": {k: float(v) for k, v in self.multipliers.items()},
            "cost_per_side": {k: float(v) for k, v in self.cost_per_side.items()},
            "rolls": R.rolls_fingerprint({k: self.rolls[k] for k in self.instruments}),
            "strategy_config": canonical_json(self.strategy_config),
            "warmup_sha256": warmup_sha256,
        }
        return hashlib.sha256(canonical_json(body).encode("ascii")).hexdigest()


def _finite(x: Any) -> bool:
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)


def initial_state(config: RunnerConfig) -> RunnerState:
    return RunnerState(None, {i: Position() for i in config.instruments}, {})


def state_from_record(record: Mapping[str, Any]) -> RunnerState:
    positions = {
        i: Position(p["contract"], int(p["qty"]), p["mark"], p["mark_date"])
        for i, p in record["positions"].items()
    }
    return RunnerState(
        date.fromisoformat(record["date"]),
        positions,
        {i: int(q) for i, q in record["orders"].items()},
    )


def _resolve_default_target() -> TargetFn:
    """forward.strategy.target_positions, looked up at call time (never at import)."""
    return importlib.import_module("forward.strategy").target_positions


@dataclass
class _Day:
    """Mutable accumulator for one trade date's per-instrument results."""

    positions: dict[str, Position]
    fills: list[dict[str, Any]] = field(default_factory=list)
    rolls: list[dict[str, Any]] = field(default_factory=list)
    expired: dict[str, int] = field(default_factory=dict)
    pnl: dict[str, dict[str, float]] = field(default_factory=dict)
    flags: list[str] = field(default_factory=list)
    with_data: set[str] = field(default_factory=set)


def check_date(state: RunnerState, trade_date: date, declared_closed: Sequence[date]) -> list[str]:
    """Refuse weekends, backwards dates and undeclared weekday gaps; return the closed dates."""
    if trade_date.weekday() >= 5:
        raise RunnerError(f"{trade_date} is a weekend day, not a trade date")
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
            f"weekday(s) {undeclared} between {state.last_date} and {trade_date} have "
            "no record; run them (missing data is recorded) or declare them closed"
        )
    return [d.isoformat() for d in closed]


def _roll(
    inst: str,
    spec: R.InstrumentRoll,
    ref: str,
    qty: int,
    quotes: Mapping[str, float],
    trade_date: date,
    cps: float,
    day: _Day,
) -> tuple[str, float]:
    """Step 3 for one instrument: returns the reference contract and its price after the roll."""
    target = R.active_contract(spec, trade_date)
    if target == ref:
        return ref, quotes[ref]
    if not R.is_roll_due(spec, ref, trade_date):
        day.flags.append(f"contract_ahead:{inst}")
        return ref, quotes[ref]
    if target not in quotes:
        day.flags.append(f"roll_deferred:{inst}")
        if trade_date >= R.expiry_guard(spec, ref):
            day.flags.append(f"roll_overdue:{inst}")
        return ref, quotes[ref]
    cost = 2 * abs(qty) * cps
    day.rolls.append(
        {
            "instrument": inst,
            "from_contract": ref,
            "to_contract": target,
            "qty": qty,
            "close_price": quotes[ref],
            "open_price": quotes[target],
            "cost": cost,
        }
    )
    day.pnl[inst]["cost"] += cost
    return target, quotes[target]


def _instrument_day(
    inst: str,
    pos: Position,
    pending: int | None,
    quotes: Mapping[str, float],
    config: RunnerConfig,
    trade_date: date,
    day: _Day,
) -> None:
    """Steps 2-4 for one instrument."""
    spec, cps = config.rolls[inst], float(config.cost_per_side[inst])
    ref = pos.contract or R.active_contract(spec, trade_date)
    day.pnl[inst] = {"gross": 0.0, "cost": 0.0}
    if ref not in quotes:
        day.flags.append(f"missing:{inst}")
        if pending is not None:
            day.expired[inst] = pending
            day.flags.append(f"order_expired:{inst}")
        day.positions[inst] = pos
        return
    day.with_data.add(inst)
    price, qty = quotes[ref], pos.qty
    if qty != 0:
        day.pnl[inst]["gross"] = qty * (price - float(pos.mark)) * float(config.multipliers[inst])
    if pending is not None and pending != qty:
        delta = pending - qty
        cost = abs(delta) * cps
        day.fills.append(
            {"instrument": inst, "contract": ref, "qty": delta, "price": price, "cost": cost}
        )
        day.pnl[inst]["cost"] += cost
        qty = pending
    contract, mark = _roll(inst, spec, ref, qty, quotes, trade_date, cps, day)
    day.positions[inst] = Position(contract, qty, mark, trade_date.isoformat())


def _validate_targets(out: Any, universe: Sequence[str], with_data: set[str]) -> dict[str, int]:
    if not isinstance(out, Mapping):
        raise RunnerError(f"target function must return a mapping, got {type(out).__name__}")
    unknown = sorted(set(out) - set(universe))
    if unknown:
        raise RunnerError(f"target function returned unknown instruments {unknown}")
    omitted = sorted(with_data - set(out))
    if omitted:
        raise RunnerError(f"target function omitted instruments with data: {omitted}")
    targets = {}
    for inst in sorted(with_data):
        value = out[inst]
        if isinstance(value, bool) or not isinstance(value, numbers.Integral):
            raise RunnerError(f"{inst}: target {value!r} is not an integer number of contracts")
        targets[inst] = int(value)
    return targets


def _payload(
    trade_date: date,
    fingerprint: str,
    closed: list[str],
    prices: DaySettlements,
    day: _Day,
    orders: dict[str, int],
    missing_day: bool,
) -> dict[str, Any]:
    fill_cost = sum(f["cost"] for f in day.fills)
    roll_cost = sum(r["cost"] for r in day.rolls)
    gross = sum(v["gross"] for v in day.pnl.values())
    return {
        "schema": SCHEMA,
        "date": trade_date.isoformat(),
        "config_sha256": fingerprint,
        "declared_closed": closed,
        "missing_day": missing_day,
        "prices": prices,
        "fills": day.fills,
        "rolls": day.rolls,
        "expired_orders": day.expired,
        "costs": {"fills": fill_cost, "rolls": roll_cost, "total": fill_cost + roll_cost},
        "pnl_by_instrument": day.pnl,
        "gross_pnl": gross,
        "net_pnl": gross - (fill_cost + roll_cost),
        "positions": {i: p.as_dict() for i, p in sorted(day.positions.items())},
        "orders": orders,
        "flags": sorted(set(day.flags)),
    }


def step(
    state: RunnerState,
    trade_date: date,
    raw_day: Any,
    history_before: Sequence[HistoryRow],
    config: RunnerConfig,
    target_fn: TargetFn,
    fingerprint: str,
    declared_closed: Sequence[date] = (),
) -> dict[str, Any]:
    """Compute one trade date's ledger payload (no hashes) from the state before it. Pure."""
    closed = check_date(state, trade_date, declared_closed)
    found = normalize_day(raw_day, f"settlements {trade_date}")
    day = _Day(positions=dict(state.positions))
    if isinstance(found, Missing):
        day.expired = dict(state.pending)
        day.flags = ["missing_day", *(f"order_expired:{i}" for i in state.pending)]
        day.pnl = {i: {"gross": 0.0, "cost": 0.0} for i in config.instruments}
        return _payload(trade_date, fingerprint, closed, {}, day, {}, True)
    unknown = sorted(set(found) - set(config.instruments))
    if unknown:
        raise RunnerError(f"settlements for instruments outside the universe: {unknown}")
    for inst in config.instruments:
        _instrument_day(
            inst,
            state.positions.get(inst, Position()),
            state.pending.get(inst),
            found.get(inst, {}),
            config,
            trade_date,
            day,
        )
    orders: dict[str, int] = {}
    if day.with_data:
        row = HistoryRow(
            trade_date, found, {i: p.contract for i, p in day.positions.items() if p.contract}
        )
        held = {i: p.qty for i, p in sorted(day.positions.items())}
        out = target_fn((*history_before, row), dict(held), copy.deepcopy(config.strategy_config))
        targets = _validate_targets(out, config.instruments, day.with_data)
        orders = {i: t for i, t in targets.items() if t != held[i]}
    return _payload(trade_date, fingerprint, closed, found, day, orders, False)


class PaperRunner:
    """The daily paper runner over one ledger file. Stateless between calls."""

    def __init__(
        self,
        ledger_path: Path | str,
        source: SettlementSource,
        config: RunnerConfig,
        *,
        target_fn: TargetFn | None = None,
        warmup: Sequence[HistoryRow] = (),
    ):
        self.ledger = Ledger(ledger_path)
        self.source = source
        self.config = config
        self._target_fn = target_fn
        self.warmup = tuple(warmup)
        check_ascending(self.warmup)
        self.fingerprint = config.fingerprint(history_fingerprint(self.warmup))

    def _target(self) -> TargetFn:
        return self._target_fn if self._target_fn is not None else _resolve_default_target()

    def _load(self) -> list[dict[str, Any]]:
        records = self.ledger.records()
        bad = [r["date"] for r in records if r.get("config_sha256") != self.fingerprint]
        if bad:
            raise RunnerError(
                f"ledger records {bad[:3]} were made under another configuration "
                "(multipliers, costs, rolls, strategy config or warm-up)"
            )
        return records

    def state(self) -> RunnerState:
        records = self._load()
        return state_from_record(records[-1]) if records else initial_state(self.config)

    def _compute(
        self, records: list[dict[str, Any]], trade_date: date, declared_closed: Sequence[date]
    ) -> dict[str, Any]:
        if self.warmup and self.warmup[-1].date >= trade_date:
            raise RunnerError(f"{trade_date} is not after the last warm-up row")
        state = state_from_record(records[-1]) if records else initial_state(self.config)
        history = (*self.warmup, *(row_from_record(r) for r in records))
        return step(
            state,
            trade_date,
            self.source.settlements(trade_date),
            history,
            self.config,
            self._target(),
            self.fingerprint,
            declared_closed,
        )

    def run_date(self, trade_date: date, *, declared_closed: Sequence[date] = ()) -> dict[str, Any]:
        """Process ``trade_date``; returns the stored ledger record."""
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
            return self.ledger.append(self._compute(records, trade_date, declared_closed))
        stored = records[index]
        closed = declared_closed or [date.fromisoformat(d) for d in stored["declared_closed"]]
        again = self._compute(records[:index], trade_date, closed)
        if canonical_json(again) != canonical_json(strip_hashes(stored)):
            diff = sorted(
                k for k in again if canonical_json(again[k]) != canonical_json(stored.get(k))
            )
            raise LedgerConflictError(f"re-run of {trade_date} differs from the ledger in {diff}")
        return stored

    def run_dates(self, dates: Sequence[date]) -> list[dict[str, Any]]:
        return [self.run_date(d) for d in dates]


def load_tables(path: Path | str) -> tuple[dict[str, float], dict[str, float]]:
    """{"multipliers": {inst: usd_per_point}, "cost_per_side": {inst: usd}} from a JSON file."""
    with open(path, encoding="utf-8") as fh:
        raw = json.load(fh)
    return (
        {k: float(v) for k, v in raw["multipliers"].items()},
        {k: float(v) for k, v in raw["cost_per_side"].items()},
    )


def _main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="python -m forward.runner", description=__doc__.split("\n")[0]
    )
    ap.add_argument("--ledger", required=True)
    ap.add_argument("--csv", required=True, help="settlement CSV (forward.sources format)")
    ap.add_argument("--tables", required=True, help="JSON with multipliers and cost_per_side")
    ap.add_argument("--config", required=True, help="strategy config JSON (config_f1.json)")
    ap.add_argument("--rolls", default=str(R.DEFAULT_ROLLS_PATH))
    ap.add_argument("--warmup", help="JSONL of HistoryRow objects")
    ap.add_argument("--date", required=True, help="trade date YYYY-MM-DD")
    ap.add_argument("--closed", nargs="*", default=[], help="declared exchange-closed weekdays")
    args = ap.parse_args(argv)
    multipliers, costs = load_tables(args.tables)
    with open(args.config, encoding="utf-8") as fh:
        strategy_config = json.load(fh)
    config = RunnerConfig(multipliers, costs, R.load_rolls(args.rolls), strategy_config)
    runner = PaperRunner(
        args.ledger,
        CsvSettlementSource(args.csv, config.instruments),
        config,
        warmup=load_warmup(args.warmup) if args.warmup else (),
    )
    record = runner.run_date(
        date.fromisoformat(args.date), declared_closed=[date.fromisoformat(d) for d in args.closed]
    )
    print(
        f"{record['date']} net_pnl={record['net_pnl']:.2f} fills={len(record['fills'])} "
        f"rolls={len(record['rolls'])} flags={len(record['flags'])} "
        f"sha={record['record_sha256'][:12]}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(_main())
