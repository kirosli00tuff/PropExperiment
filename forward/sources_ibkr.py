"""Daily prices of E22-F1's 12 micros from IBKR through IB Gateway (Stage E.24, IBKRCoder).

A :class:`IBKRSettlementSource` implements forward.sources.SettlementSource for the frozen
runner (forward.runner.PaperRunner): ``settlements(t)`` returns ``{instrument: {contract_id:
price}}`` for each instrument's reference contract under forward/rolls_f1.json and, from the
previous contract's roll date through its anchor date, that previous contract too (the runner
needs both legs on a switch date, and keeps needing the held leg while a roll is deferred).

Field delivered: the CLOSE of IB's TRADES daily bar, converted to the runner's quote units
(cents / 100 for MZC, MZS, MZL). Per reports/stage_e24_briefs/facts/ibkr_facts.md I6 that close
is the LAST TRADED PRICE and only "can be" the settlement; it is labelled close_last_trade in the
provenance log and the CSV header. This module decides nothing about E22-F1 (brief item 6).

Rules (each one exists because a false Missing counts as a 0 in E22-F1's evaluation):
- Trade dates are CME trade dates: the date of the session that ends at the settlement. The
  ThinkPad's local date never decides anything; ``now`` must be timezone-aware.
- A bar for date t is used only after the cutoff (t at CUTOFF_CT, America/Chicago); before it
  the day is not ready (DayNotReady, no record).
- A contract with no bar for t counts as affirmatively missing only when a later FINAL bar
  exists for it, its last trade date is before t, or a later final bar exists on the same
  exchange (the t session is over). A later bar is final once its own cutoff has passed (S2,
  wave 3): the open session's partial bar, dated t+1 from 17:00 CT, confirms nothing.
  Otherwise DayNotReady. Connection failures, timeouts, pacing violations and empty or partial
  answers raise SourceUnavailable. Missing(reason) is returned only when no contract at all has
  a price for t and every absence is affirmative.
- A contract that does not resolve to exactly one IB contract is an error, never a guess.

The warm-up assembly (:func:`assemble_rows`, :func:`fetch_warmup_prices`, :func:`write_warmup`)
builds the JSONL of HistoryRow objects that forward.history.load_warmup reads, and
:func:`export_csv` writes forward.sources' CSV format so the frozen runner CLI (--csv) can run
unchanged on IBKR-sourced data.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import UTC, date, datetime, time, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from forward import rolls as R
from forward.history import HistoryRow, back_adjusted_series, load_warmup
from forward.ibkr_gateway import (
    ContractResolutionError,
    ConventionError,
    DayNotReady,
    EmptyResponse,
    GatewaySession,
    IBKRError,
    NoHistoricalData,
    RequestTimedOut,
    SourceUnavailable,
    Vendor,
)
from forward.sources import CSV_HEADER, CsvSettlementSource, DaySettlements, Missing

# --- declared conventions (pending alignment with the facts files; see the report) ----------
CME_TZ = ZoneInfo("America/Chicago")
# Cutoff: a declared choice (18:00 CT = the 16:00 CT session end + 2 h for the data delay and
# late bar updates). I6 says the TRADES close "can be" the settlement only hours later or on
# Saturday, so the cutoff cannot make it a settlement; it only keeps partial bars out.
CUTOFF_CT = time(18, 0)
WHAT_TO_SHOW = "TRADES"  # I6: the TRADES daily close is the LAST TRADED PRICE, not the settlement
FIELD_LABEL = "close_last_trade"  # the label written to provenance and the CSV header (I6)
USE_RTH = False  # whole electronic session; I6/implication 4: dated by the session's closing day
BAR_SIZE = "1 day"
EXPIRED_DEPTH_DAYS = 730  # I5: expired futures' history is kept 2 years after expiry
WARMUP_FIRST = date(2024, 3, 1)  # V42: the warm-up read starts here
WARMUP_DIFFS = 256  # config_f1.json warmup_diffs: flat until 256 daily differences
DURATION_MARGIN_DAYS = 5
MAX_DAY_DURATION = 365
# N7 (wave 3): IB quotes the micro grains in cents (I7 [unverified]). A close below these floors
# (cents; a dollar quote would be about 4, 10 and 0.45) means the convention broke: stop.
MIN_IB_CLOSE_CENTS = {"MZC": 100.0, "MZS": 300.0, "MZL": 10.0}
# S1 (wave 3): a warm-up whose reference is stuck on an old contract (an open roll) while its
# last priced date is more than this many weekdays before the warm-up's last day is refused.
OPEN_ROLL_STALE_WEEKDAYS = 3
# S3 (wave 3): gap groups for the driver's exchange-gap guard. The group is the IB exchange,
# except the CBOT grains, which keep their own session (and holidays) apart from the CBOT
# financials (review N8), so a grains-only gap is caught as well.
GAP_GROUP_OVERRIDES = {"MZC": "CBOT grains", "MZS": "CBOT grains", "MZL": "CBOT grains"}


@dataclass(frozen=True)
class IBSpec:
    """How one runner instrument maps to an IB futures contract.

    USD per 1.0 of IB price = ib_multiplier / price_magnifier; the runner's price is the IB
    price / price_divisor, so the runner multiplier (config_f1.json) must equal
    ib_multiplier / price_magnifier * price_divisor.
    """

    instrument: str
    symbol: str
    exchange: str
    currency: str
    ib_multiplier: float
    price_magnifier: int = 1
    price_divisor: int = 1
    trading_class: str | None = None
    fact: str = "pending reports/stage_e24_briefs/facts/ibkr_facts.md"

    def runner_multiplier(self) -> float:
        return self.ib_multiplier / self.price_magnifier * self.price_divisor


def gap_group(instrument: str, exchange: str) -> str:
    return GAP_GROUP_OVERRIDES.get(instrument, exchange)


IB_SPECS: Mapping[str, IBSpec] = {
    # exchange, IB symbol and trading class: ibkr_facts.md I7 (IBKR US futures margin table).
    # Multipliers and price magnifiers are NOT on any IBKR page fetched (I7 [unverified]): they
    # are derived from config_f1.json and checked against reqContractDetails at runtime.
    "MNQ": IBSpec("MNQ", "MNQ", "CME", "USD", 2.0, trading_class="MNQ", fact="I7"),
    "M2K": IBSpec("M2K", "M2K", "CME", "USD", 5.0, trading_class="M2K", fact="I7"),
    "M6E": IBSpec("M6E", "M6E", "CME", "USD", 12500.0, trading_class="M6E", fact="I7"),
    "MGC": IBSpec("MGC", "MGC", "COMEX", "USD", 10.0, trading_class="MGC", fact="I7"),
    "MCL": IBSpec("MCL", "MCL", "NYMEX", "USD", 100.0, trading_class="MCL", fact="I7"),
    # I7 quirk: Micro Henry Hub is IB symbol MHNG, trading class MNG.
    "MNG": IBSpec("MNG", "MHNG", "NYMEX", "USD", 1000.0, trading_class="MNG", fact="I7"),
    "2YY": IBSpec("2YY", "2YY", "CBOT", "USD", 1000.0, trading_class="2YY", fact="I7"),
    "10Y": IBSpec("10Y", "10Y", "CBOT", "USD", 1000.0, trading_class="10Y", fact="I7"),
    "30Y": IBSpec("30Y", "30Y", "CBOT", "USD", 1000.0, trading_class="30Y", fact="I7"),
    "MZC": IBSpec("MZC", "MZC", "CBOT", "USD", 500.0, 100, 100, trading_class="MZC", fact="I7"),
    "MZS": IBSpec("MZS", "MZS", "CBOT", "USD", 500.0, 100, 100, trading_class="MZS", fact="I7"),
    "MZL": IBSpec("MZL", "MZL", "CBOT", "USD", 6000.0, 100, 100, trading_class="MZL", fact="I7"),
}


class ContractNotFound(ContractResolutionError):
    """No IB contract matched (zero results)."""


def check_specs(specs: Mapping[str, IBSpec], config_multipliers: Mapping[str, float]) -> None:
    """Refuse a spec whose implied runner multiplier differs from config_f1.json's."""
    for inst, mult in config_multipliers.items():
        spec = specs.get(inst)
        if spec is None:
            raise ContractResolutionError(f"{inst}: no IB spec declared")
        if not math.isclose(spec.runner_multiplier(), float(mult), rel_tol=1e-12):
            raise ContractResolutionError(
                f"{inst}: IB spec implies multiplier {spec.runner_multiplier()} but "
                f"config_f1.json says {mult}"
            )


# --- time rule -------------------------------------------------------------------------------
def utc_now() -> datetime:
    return datetime.now(UTC)


def _aware(now: datetime) -> datetime:
    if now.tzinfo is None or now.utcoffset() is None:
        raise ConventionError("naive datetime refused: the local time zone never sets a trade date")
    return now


def cutoff_utc(trade_date: date) -> datetime:
    return datetime.combine(trade_date, CUTOFF_CT, tzinfo=CME_TZ).astimezone(UTC)


def is_ready(trade_date: date, now: datetime) -> bool:
    return _aware(now) >= cutoff_utc(trade_date)


def chicago_date(now: datetime) -> date:
    return _aware(now).astimezone(CME_TZ).date()


def latest_ready_trade_date(now: datetime) -> date:
    """The latest weekday whose cutoff has passed at ``now``."""
    day = chicago_date(now)
    while day.weekday() >= 5 or not is_ready(day, now):
        day -= timedelta(days=1)
    return day


def ib_end_of_day(day: date) -> str:
    """'YYYYMMDD-hh:mm:ss' (the API's UTC format, facts I6) for 23:59:59 Chicago time on ``day``.

    Never pass a bare date to ib_async: util.formatIBDatetime reads it in the local time zone,
    and a string without a zone is read in the TWS login time zone (facts I9).
    """
    eod = datetime.combine(day, time(23, 59, 59), tzinfo=CME_TZ).astimezone(UTC)
    return eod.strftime("%Y%m%d-%H:%M:%S")


def duration_for(start: date, end: date) -> str:
    days = max(DURATION_MARGIN_DAYS, (end - start).days + 1 + DURATION_MARGIN_DAYS)
    if days <= MAX_DAY_DURATION:
        return f"{days} D"
    return f"{math.ceil(days / 365)} Y"


# --- contract cycle helpers ------------------------------------------------------------------
def _shift_contract(spec: R.InstrumentRoll, cid: str, step: int) -> str:
    year, month = R.parse_contract(spec, cid)
    i = spec.months.index(month) + step
    year += i // len(spec.months)
    return R.contract_id(spec, year, spec.months[i % len(spec.months)])


def previous_contract(spec: R.InstrumentRoll, cid: str) -> str:
    return _shift_contract(spec, cid, -1)


def next_contract(spec: R.InstrumentRoll, cid: str) -> str:
    return _shift_contract(spec, cid, 1)


def contracts_for_day(spec: R.InstrumentRoll, day: date) -> tuple[str, ...]:
    """The reference contract on ``day`` and, from the previous one's roll date through its
    anchor date, the previous contract too (sorted ids)."""
    active = R.active_contract(spec, day)
    prev = previous_contract(spec, active)
    if R.roll_date(spec, *R.parse_contract(spec, prev)) <= day <= R.expiry_guard(spec, prev):
        return tuple(sorted((prev, active)))
    return (active,)


def warmup_windows(spec: R.InstrumentRoll, first: date, last: date) -> list[tuple[str, date, date]]:
    """(contract, first day needed, last day needed) for each contract that is the reference,
    or the roll partner of it, somewhere in [first, last]."""
    cid, out = R.active_contract(spec, first), []
    final = R.active_contract(spec, last)
    while True:
        start = max(first, R.roll_date(spec, *R.parse_contract(spec, previous_contract(spec, cid))))
        end = min(last, R.expiry_guard(spec, cid))
        out.append((cid, start, end))
        if cid == final:
            return out
        cid = next_contract(spec, cid)


# --- contract resolution ---------------------------------------------------------------------
@dataclass(frozen=True)
class ResolvedContract:
    instrument: str
    contract_id: str
    contract: Any = field(repr=False)
    con_id: int
    local_symbol: str
    exchange: str
    last_trade_date: date
    price_divisor: int


class ContractResolver:
    """instrument + contract id (MNQZ26) -> exactly one IB futures contract, cached."""

    def __init__(
        self,
        session: GatewaySession,
        vendor: Vendor,
        rolls: Mapping[str, R.InstrumentRoll],
        *,
        specs: Mapping[str, IBSpec] = IB_SPECS,
        config_multipliers: Mapping[str, float] | None = None,
    ):
        if config_multipliers is not None:
            check_specs(specs, config_multipliers)
        self.session, self.vendor, self.rolls, self.specs = session, vendor, rolls, specs
        self._cache: dict[tuple[str, str], ResolvedContract] = {}
        self._by_con_id: dict[int, ResolvedContract] = {}

    def query(self, instrument: str, contract_id: str) -> Any:
        spec = self._spec(instrument)
        year, month = R.parse_contract(self.rolls[instrument], contract_id)
        extra = {"tradingClass": spec.trading_class} if spec.trading_class else {}
        return self.vendor.future(
            symbol=spec.symbol,
            lastTradeDateOrContractMonth=f"{year:04d}{month:02d}",
            exchange=spec.exchange,
            currency=spec.currency,
            includeExpired=True,
            **extra,
        )

    def _spec(self, instrument: str) -> IBSpec:
        if instrument not in self.specs or instrument not in self.rolls:
            raise ContractResolutionError(f"{instrument}: not in the IB specs or the roll file")
        return self.specs[instrument]

    def resolve(self, instrument: str, contract_id: str) -> ResolvedContract:
        key = (instrument, contract_id)
        if key not in self._cache:
            details = self.session.contract_details(
                f"reqContractDetails {contract_id}", self.query(instrument, contract_id)
            )
            rc = self._check(instrument, contract_id, details)
            self._cache[key] = rc
            self._by_con_id[rc.con_id] = rc
        return self._cache[key]

    def _check(self, instrument: str, cid: str, details: Sequence[Any]) -> ResolvedContract:
        if not details:
            raise ContractNotFound(f"{instrument} {cid}: no IB contract matched")
        if len(details) > 1:
            seen = sorted(
                f"{getattr(d.contract, 'localSymbol', '?')}/"
                f"{getattr(d.contract, 'multiplier', '?')}"
                for d in details
            )
            raise ContractResolutionError(
                f"{instrument} {cid}: ambiguous, {len(details)} matches {seen}"
            )
        return _validated(self._spec(instrument), self.rolls[instrument], cid, details[0])

    def identify(self, contract: Any) -> ResolvedContract | None:
        """The resolved contract behind an IB position's contract (by conId), or None."""
        return self._by_con_id.get(int(getattr(contract, "conId", 0) or 0))

    def known(self) -> list[ResolvedContract]:
        return list(self._cache.values())


def _validated(spec: IBSpec, roll: R.InstrumentRoll, cid: str, d: Any) -> ResolvedContract:
    c = d.contract
    year, month = R.parse_contract(roll, cid)
    where = f"{spec.instrument} {cid}"
    checks = {
        "secType": (getattr(c, "secType", None), "FUT"),
        "symbol": (getattr(c, "symbol", None), spec.symbol),
        "currency": (getattr(c, "currency", None), spec.currency),
        "exchange": (getattr(c, "exchange", None), spec.exchange),
        "contractMonth": (getattr(d, "contractMonth", None), f"{year:04d}{month:02d}"),
        "priceMagnifier": (int(getattr(d, "priceMagnifier", 0) or 1), spec.price_magnifier),
    }
    bad = {k: got for k, (got, want) in checks.items() if got != want}
    try:
        multiplier = float(getattr(c, "multiplier", "") or "nan")
    except ValueError:
        multiplier = float("nan")
    if not math.isclose(multiplier, spec.ib_multiplier, rel_tol=1e-12):
        bad["multiplier"] = getattr(c, "multiplier", None)
    con_id = int(getattr(c, "conId", 0) or 0)
    if con_id <= 0:
        bad["conId"] = con_id
    if bad:
        raise ContractResolutionError(f"{where}: IB fields differ from the declared spec: {bad}")
    raw = str(getattr(c, "lastTradeDateOrContractMonth", ""))[:8]
    try:
        last_trade = datetime.strptime(raw, "%Y%m%d").date()
    except ValueError:
        raise ContractResolutionError(f"{where}: no last trade date in {raw!r}") from None
    return ResolvedContract(
        spec.instrument,
        cid,
        c,
        con_id,
        str(getattr(c, "localSymbol", "")),
        spec.exchange,
        last_trade,
        spec.price_divisor,
    )


# --- bars ------------------------------------------------------------------------------------
def to_runner_price(close: Any, divisor: int) -> float:
    value = float(close)
    if not math.isfinite(value):
        raise ConventionError(f"bar close {close!r} is not finite")
    if divisor == 1:
        return value
    return float(Decimal(repr(value)) / Decimal(divisor))


def bar_prices(bars: Iterable[Any], rc: ResolvedContract) -> dict[date, tuple[float, float]]:
    """{trade date: (IB close, runner price)} after the convention checks."""
    out: dict[date, tuple[float, float]] = {}
    for bar in bars:
        day = bar.date
        if isinstance(day, datetime) or not isinstance(day, date):
            raise ConventionError(f"{rc.contract_id}: daily bar date {day!r} is not a date")
        if day.weekday() >= 5:
            raise ConventionError(f"{rc.contract_id}: daily bar dated on a weekend ({day})")
        if day in out:
            raise ConventionError(f"{rc.contract_id}: two daily bars dated {day}")
        floor = MIN_IB_CLOSE_CENTS.get(rc.instrument)
        if floor is not None and not float(bar.close) >= floor:
            raise ConventionError(
                f"{rc.contract_id}: close {bar.close!r} on {day} is below {floor:g}; IB quotes "
                "the micro grains in cents (I7), so this is not a cents price"
            )
        out[day] = (float(bar.close), to_runner_price(bar.close, rc.price_divisor))
    return dict(sorted(out.items()))


@dataclass(frozen=True)
class Observation:
    rc: ResolvedContract
    bar: tuple[float, float] | None  # (IB close, runner price) on the trade date
    later: date | None  # the latest FINAL bar date after the trade date, if any
    expired: bool  # last trade date before the trade date


class IBKRSettlementSource:
    """forward.sources.SettlementSource over IB daily bars (see the module docstring)."""

    def __init__(
        self,
        session: GatewaySession,
        resolver: ContractResolver,
        rolls: Mapping[str, R.InstrumentRoll],
        *,
        instruments: Iterable[str] | None = None,
        now: Callable[[], datetime] = utc_now,
        provenance_path: Path | str | None = None,
    ):
        self.session, self.resolver, self.rolls = session, resolver, rolls
        self.instruments = tuple(sorted(instruments if instruments is not None else rolls))
        self._now = now
        self.provenance_path = Path(provenance_path) if provenance_path else None
        self._memo: dict[date, DaySettlements | Missing] = {}
        self.logs: dict[date, list[dict[str, Any]]] = {}  # decide()'s log per answered date

    def settlements(self, trade_date: date) -> DaySettlements | Missing:
        if trade_date in self._memo:
            return _copy_answer(self._memo[trade_date])
        now = self._now()
        if trade_date.weekday() >= 5:
            raise ConventionError(f"{trade_date} is a weekend day, not a CME trade date")
        if not is_ready(trade_date, now):
            raise DayNotReady(
                f"{trade_date}: before the cutoff {cutoff_utc(trade_date).isoformat()} "
                f"({CUTOFF_CT.isoformat()} America/Chicago)"
            )
        obs = {
            (inst, cid): self._observe(inst, cid, trade_date, now)
            for inst in self.instruments
            for cid in contracts_for_day(self.rolls[inst], trade_date)
        }
        answer, log = decide(trade_date, obs)
        self._write_provenance(log, now)
        self._memo[trade_date] = answer
        self.logs[trade_date] = log
        return _copy_answer(answer)

    def exchange_gaps(self, trade_date: date) -> dict[str, list[str]]:
        """Gap groups whose every contract is affirmed missing on an answered date while
        another group is priced (S3, wave 3): {group: [instrument:contract, ...]}."""
        return exchange_gaps(self.logs.get(trade_date, []))

    def _observe(self, inst: str, cid: str, trade_date: date, now: datetime) -> Observation:
        today = chicago_date(now)
        rc = self.resolver.resolve(inst, cid)
        if rc.last_trade_date < trade_date:
            return Observation(rc, None, None, True)
        live = rc.last_trade_date >= today
        end_day = today if live else rc.last_trade_date
        try:
            bars = self.session.daily_bars(
                f"reqHistoricalData {cid} for {trade_date}",
                rc.contract,
                end="" if live else ib_end_of_day(end_day),
                duration=duration_for(trade_date, end_day),
                what_to_show=WHAT_TO_SHOW,
                use_rth=USE_RTH,
            )
        except NoHistoricalData:
            bars = []
        prices = bar_prices(bars, rc)
        # S2 (wave 3): only a bar whose own session is final confirms that t is over
        later = max((d for d in prices if d > trade_date and is_ready(d, now)), default=None)
        return Observation(rc, prices.get(trade_date), later, False)

    def _write_provenance(self, log: list[dict[str, Any]], now: datetime) -> None:
        if self.provenance_path is None:
            return
        stamp = now.astimezone(UTC).isoformat()
        lines = "".join(
            json.dumps({**entry, "fetched_utc": stamp}, sort_keys=True) + "\n" for entry in log
        )
        self.provenance_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.provenance_path, "a", encoding="utf-8") as fh:
            fh.write(lines)
            fh.flush()
            os.fsync(fh.fileno())


def _copy_answer(answer: DaySettlements | Missing) -> DaySettlements | Missing:
    if isinstance(answer, Missing):
        return answer
    return {inst: dict(q) for inst, q in answer.items()}


def decide(
    trade_date: date, obs: Mapping[tuple[str, str], Observation]
) -> tuple[DaySettlements | Missing, list[dict[str, Any]]]:
    """Turn observations into the runner's answer; raise DayNotReady on any open absence."""
    exchanges_moved_on = {o.rc.exchange for o in obs.values() if o.later is not None}
    prices: DaySettlements = {}
    log, pending = [], []
    for (inst, cid), o in sorted(obs.items()):
        entry = _log_entry(trade_date, o)
        if o.bar is not None:
            prices.setdefault(inst, {})[cid] = o.bar[1]
            entry.update(status="price", bar_close_ib=o.bar[0], price=o.bar[1])
        elif o.later is not None:
            entry.update(status="affirmed_missing", reason=f"later bar {o.later} exists")
        elif o.expired:
            entry.update(status="affirmed_missing", reason="last trade date before the date")
        elif o.rc.exchange in exchanges_moved_on:
            entry.update(status="affirmed_missing", reason=f"later bar on {o.rc.exchange}")
        else:
            pending.append(f"{inst}:{cid}")
            continue
        log.append(entry)
    if pending:
        raise DayNotReady(
            f"{trade_date}: no bar yet for {pending} and no later bar confirms the session is over"
        )
    if not prices:
        return Missing(
            f"IBKR has no daily bar for {trade_date} for any contract while the "
            "session is confirmed over (exchange closed? declare it closed)"
        ), log
    return {i: dict(sorted(q.items())) for i, q in sorted(prices.items())}, log


def exchange_gaps(log: Sequence[Mapping[str, Any]]) -> dict[str, list[str]]:
    """From decide()'s log: the gap groups (gap_group) in which every contract is affirmed
    missing while at least one other group has a price. Empty when nothing is priced (that
    is a whole-day Missing) or when every group has a price."""
    groups: dict[str, list[Mapping[str, Any]]] = {}
    for entry in log:
        groups.setdefault(gap_group(entry["instrument"], entry["exchange"]), []).append(entry)
    priced = {g for g, es in groups.items() if any(e["status"] == "price" for e in es)}
    if not priced:
        return {}
    return {
        g: sorted(f"{e['instrument']}:{e['contract_id']}" for e in es)
        for g, es in sorted(groups.items())
        if g not in priced and all(e["status"] == "affirmed_missing" for e in es)
    }


def _log_entry(trade_date: date, o: Observation) -> dict[str, Any]:
    return {
        "trade_date": trade_date.isoformat(),
        "bar_date": trade_date.isoformat() if o.bar is not None else None,
        "instrument": o.rc.instrument,
        "contract_id": o.rc.contract_id,
        "con_id": o.rc.con_id,
        "local_symbol": o.rc.local_symbol,
        "exchange": o.rc.exchange,
        "field": FIELD_LABEL,
        "what_to_show": WHAT_TO_SHOW,
        "use_rth": USE_RTH,
        "bar_size": BAR_SIZE,
        "price_divisor": o.rc.price_divisor,
    }


# --- warm-up assembly ------------------------------------------------------------------------
PriceMap = Mapping[str, Mapping[str, Mapping[date, float]]]  # instrument -> contract -> day


def assemble_rows(
    prices: PriceMap, rolls: Mapping[str, R.InstrumentRoll], first: date, last: date
) -> tuple[HistoryRow, ...]:
    """HistoryRows over [first, last] with each day's reference after that day's rolls.

    The reference follows rolls_f1.json's rule exactly as the runner applies it: an
    instrument's first reference is the declared contract on its first priced day; a due roll
    executes on the first day on or after the roll date where both contracts have a price, and
    that row carries both prices (so back_adjusted_series can shift at the switch).
    """
    days = sorted({d for q in prices.values() for s in q.values() for d in s if first <= d <= last})
    ref: dict[str, str] = {}
    rows = []
    for day in days:
        row_prices: dict[str, dict[str, float]] = {}
        for inst in sorted(prices):
            quotes = _day_quotes(prices[inst], rolls[inst], ref, inst, day)
            if quotes:
                row_prices[inst] = quotes
        rows.append(HistoryRow(day, row_prices, dict(ref)))
    return tuple(rows)


def _day_quotes(
    by_contract: Mapping[str, Mapping[date, float]],
    spec: R.InstrumentRoll,
    ref: dict[str, str],
    inst: str,
    day: date,
) -> dict[str, float]:
    available = {cid: s[day] for cid, s in by_contract.items() if day in s}
    target = R.active_contract(spec, day)
    current = ref.get(inst)
    if current is None:
        if target not in available:
            return {}
        ref[inst] = target
        return {target: available[target]}
    quotes = {current: available[current]} if current in available else {}
    if target != current and R.is_roll_due(spec, current, day) and target in available:
        quotes[target] = available[target]
        if current in quotes:
            ref[inst] = target
    return quotes


@dataclass(frozen=True)
class WarmupNote:
    instrument: str
    contract_id: str
    note: str


def fetch_warmup_prices(
    session: GatewaySession,
    resolver: ContractResolver,
    rolls: Mapping[str, R.InstrumentRoll],
    first: date,
    last: date,
    *,
    today: date,
    instruments: Iterable[str] | None = None,
    expired_depth_days: int = EXPIRED_DEPTH_DAYS,
) -> tuple[dict[str, dict[str, dict[date, float]]], list[WarmupNote]]:
    """Each needed contract's runner prices over its window, plus notes on absent history.

    A contract older than ``expired_depth_days`` (facts I5: 2 years) that IB does not know,
    answers with no data, or answers empty or not within the request timeout, is noted and
    skipped (fewer prior settlements). Inside the depth, a not-found contract is accepted only
    BEFORE the instrument's first resolved contract (the product was listed later, e.g. the
    micro grains); a not-found contract after it raises, a "no data" answer raises (S1, wave
    3), an instrument with no resolved contract at all raises (a wrong symbol mapping), and so
    does any connection failure or timeout. No partial window is ever used (B1, wave 3).

    The depth is measured from the contract's anchor date in rolls_f1.json (R.expiry_guard), not
    from IB's last trade date (N6): a few business days lenient for MCL, up to about four weeks
    conservative for MGC and the grains.
    """
    out: dict[str, dict[str, dict[date, float]]] = {}
    notes: list[WarmupNote] = []
    for inst in sorted(instruments if instruments is not None else rolls):
        spec = rolls[inst]
        out[inst] = {}
        found = False
        for cid, start, end in warmup_windows(spec, first, last):
            old = R.expiry_guard(spec, cid) < today - timedelta(days=expired_depth_days)
            got = _fetch_contract(session, resolver, inst, cid, start, end, old or not found, notes)
            found = found or (inst, cid) in {
                (r.instrument, r.contract_id) for r in resolver.known()
            }
            if got:
                out[inst][cid] = got
        if not found:
            raise ContractNotFound(f"{inst}: no contract of the warm-up window resolved at IB")
    return out, notes


def _fetch_contract(
    session: GatewaySession,
    resolver: ContractResolver,
    inst: str,
    cid: str,
    start: date,
    end: date,
    old: bool,
    notes: list[WarmupNote],
) -> dict[date, float]:
    try:
        rc = resolver.resolve(inst, cid)
    except ContractNotFound:
        if not old:
            raise
        notes.append(
            WarmupNote(inst, cid, "not found at IB (beyond the 2-year depth, or listed later)")
        )
        return {}
    stop = min(end, rc.last_trade_date)
    if stop < start:
        notes.append(WarmupNote(inst, cid, f"last trade date {rc.last_trade_date} before {start}"))
        return {}
    try:
        bars = session.daily_bars(
            f"warm-up reqHistoricalData {cid}",
            rc.contract,
            end=ib_end_of_day(stop),
            duration=duration_for(start, stop),
            what_to_show=WHAT_TO_SHOW,
            use_rth=USE_RTH,
        )
    except NoHistoricalData:
        if not old:  # S1 (wave 3): inside the depth a no-data answer is a gap, never a skip
            raise
        notes.append(WarmupNote(inst, cid, "server: no data for the window"))
        return {}
    except SourceUnavailable as exc:
        if not (old and isinstance(exc.__cause__, (EmptyResponse, RequestTimedOut))):
            raise
        notes.append(
            WarmupNote(
                inst, cid, "empty or timed-out answers (beyond the depth, or before listing)"
            )
        )
        return {}
    return {d: p for d, (_, p) in bar_prices(bars, rc).items() if start <= d <= stop}


def warmup_summary(
    rows: Sequence[HistoryRow],
    rolls: Mapping[str, R.InstrumentRoll],
    instruments: Iterable[str],
    *,
    warmup_diffs: int = WARMUP_DIFFS,
) -> dict[str, dict[str, Any]]:
    """Per instrument: priced rows, first and last date, contracts, an open roll at the end, and
    whether it is live at the start (at least ``warmup_diffs`` daily differences, E22-F1 sec. 7)."""
    out = {}
    for inst in sorted(instruments):
        priced = [r for r in rows if r.price(inst) is not None]
        refs = sorted({r.reference[inst] for r in priced})
        last_ref = rows[-1].reference.get(inst) if rows else None
        due = R.active_contract(rolls[inst], rows[-1].date) if rows else None
        out[inst] = {
            "rows": len(priced),
            "first_date": priced[0].date.isoformat() if priced else None,
            "last_date": priced[-1].date.isoformat() if priced else None,
            "contracts": refs,
            "last_reference": last_ref,
            "open_roll": bool(last_ref and due and last_ref != due),
            "back_adjusted_points": len(back_adjusted_series(rows, inst)),
            "live_at_start": len(priced) - 1 >= warmup_diffs,
        }
    return out


def stale_open_rolls(
    summary: Mapping[str, Mapping[str, Any]],
    last: date,
    *,
    tolerance_weekdays: int = OPEN_ROLL_STALE_WEEKDAYS,
) -> list[str]:
    """Instruments whose reference is stuck on an old contract at the end of the warm-up (an
    open roll) while their last priced date is more than ``tolerance_weekdays`` weekdays before
    ``last`` (S1, wave 3). A roll deferred at the very end keeps a recent last date."""
    out = []
    for inst, s in sorted(summary.items()):
        if not s.get("open_roll"):
            continue
        last_priced = date.fromisoformat(s["last_date"]) if s.get("last_date") else None
        lag = _weekdays_between(last_priced, last) if last_priced else None
        if lag is None or lag > tolerance_weekdays:
            out.append(inst)
    return out


def _weekdays_between(a: date, b: date) -> int:
    """Weekdays d with a < d <= b."""
    return sum(1 for k in range(1, (b - a).days + 1) if (a + timedelta(days=k)).weekday() < 5)


def write_warmup(rows: Sequence[HistoryRow], path: Path | str) -> str:
    """Write the JSONL (refusing to overwrite), verify the round trip, write <path>.sha256."""
    path = Path(path)
    if path.exists():
        raise FileExistsError(f"{path} exists; a warm-up file is never overwritten")
    path.parent.mkdir(parents=True, exist_ok=True)
    body = "".join(
        json.dumps(r.to_json(), sort_keys=True, separators=(",", ":")) + "\n" for r in rows
    )
    with open(path, "x", encoding="utf-8") as fh:
        fh.write(body)
    if load_warmup(path) != tuple(rows):
        raise IBKRError(f"{path}: load_warmup round trip differs from the assembled rows")
    digest = hashlib.sha256(body.encode("utf-8")).hexdigest()
    Path(f"{path}.sha256").write_text(f"{digest}  {path.name}\n", encoding="ascii")
    return digest


# --- CSV export (forward.sources format) -----------------------------------------------------
def rows_to_days(rows: Iterable[HistoryRow]) -> dict[date, DaySettlements]:
    return {r.date: {i: dict(q) for i, q in r.prices.items()} for r in rows if r.prices}


def export_csv(days: Mapping[date, DaySettlements | Missing], path: Path | str) -> int:
    """Append days to a forward.sources CSV (created with its header when absent).

    A Missing day writes no rows (the CSV source reads it as missing). A day already in the file
    must match it exactly (then nothing is written); a difference raises. Prices are written with
    repr(), so the CSV source reads back the identical floats. Returns the rows written.
    """
    path = Path(path)
    existing = CsvSettlementSource(path).load() if path.exists() else {}
    new_lines = []
    for day in sorted(days):
        answer = days[day]
        if isinstance(answer, Missing) or not answer:
            continue
        if day in existing:
            if existing[day] != answer:
                raise IBKRError(f"{path}: {day} already has different rows")
            continue
        new_lines += [
            f"{day.isoformat()},{inst},{cid},{price!r}"
            for inst, quotes in sorted(answer.items())
            for cid, price in sorted(quotes.items())
        ]
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        head = (
            f"# IBKR daily bars (forward.sources_ibkr), field {FIELD_LABEL} "
            f"(I6: NOT the settlement): {WHAT_TO_SHOW} {BAR_SIZE} bars, useRTH={USE_RTH}\n"
            + ",".join(CSV_HEADER)
            + "\n"
        )
        path.write_text(head, encoding="utf-8")
    if new_lines:
        with open(path, "a", encoding="utf-8") as fh:
            fh.write("\n".join(new_lines) + "\n")
    CsvSettlementSource(path).load()  # full re-validation of the file
    return len(new_lines)
