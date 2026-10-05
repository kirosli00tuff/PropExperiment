"""Stage E.14 (harness v10): test C2, GEX-conditioned late-session momentum in S&P futures.

    uv run python -m screening.stage_e14_c2 --store-sha256 <sha> --gex <csv> --gex-sha256 <sha> \
        --gex-lag 1 --harness-sha256 <sha> --freeze-sha256 <sha> --out <json>
    uv run python -m screening.stage_e14_c2 count --gex <csv> --gex-sha256 <sha> --gex-lag 1

Exactly the rule of reports/stage_e13_prereg_gexmom.md sections 3-5 (frozen as
reports/stage_e14_prereg_C2.md), with no free parameter; GEX_LAG is fixed by the freeze and given
on the command line (1 or 2).
- Eligible date d, every weekday 2011-05-03..2019-04-30, tested in this order (the first failing
  condition is the date's exclusion reason, every date counted): not an unsourced calendar date;
  a trade date of the hist equity calendar; not an early-halt or late-open date; not an ES roll
  blackout date (the splice date and the two group trade dates before it); its prior trade date
  exists in the store's window and neither it nor any weekday between it and d is unsourced; a
  GEX row (GEX_LAG 1: the row of the latest CSV date strictly before d; 2: the row before that);
  the four bars present (b_s = the one-minute bar starting at s CT): b_14:29, b_14:30, b_15:00 on
  d and b_14:59 on the prior trade date, each labelled with its own trade date and none flagged
  in_scheduled_closure (a bar inside a scheduled closure counts as absent).
- R_rod = close(b_14:29 on d) / close(b_14:59 on the prior trade date) - 1; side +1 if R_rod > 0,
  -1 if R_rod < 0, no trade if R_rod = 0. g = side x (open(b_15:00) - open(b_14:30)) / 0.25, in
  MES ticks. T1 = the trades on eligible dates with GEX < 0 (strictly); T2 = every trade.
- c = 0.976 + 0.5191 + 0.5428 = 2.0379 ticks (commission 1.22 / 1.25; s_b(14:30), s_b(15:00):
  reports/stage_e2a_costs.md, MES check rows 14:30 and 15:00); bar = 1.5 x c. Per test: n, mean,
  sd (ddof 1), t = mean / (sd / sqrt(n)), one-sided p = Student t survival at t with n - 1 df.
  A test passes iff mean >= bar AND p <= 0.025 AND n >= 30. The hypothesis passes iff T1 passes
  AND mean_T1 > mean_T2; "T2 passes alone" (T2 passes, T1 does not) is reported, not a pass.

Run once. Preconditions, each refused with nothing written (the evaluation has not run, no bar or
GEX value is read): the harness preflight; neither the marker reports/stage_e14_c2_RUN_ONCE.json
nor --out exists; GEX_LAG is 1 or 2; the freeze file hashes to --freeze-sha256; the trial
registry holds C2-T1 and C2-T2 registered together under that freeze sha256; the store, the GEX
CSV and the hist equity calendar exist and hash to their pinned values (bytes hashed, not read as
data). Then the marker is written, BEFORE any bar or GEX value is read, and from there every stop
(a store refusal, a malformed GEX file, any error) gives the verdict STOPPED with the reason. The
output JSON holds the verdict, every statistic, eligible counts and exclusions by reason, trade
counts with the long/short split, and the hashes of every input; never a price.
"""

from __future__ import annotations

import argparse
import bisect
import csv
import hashlib
import io
import json
import math
import sys
from collections import Counter
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import numpy as np

from data.config import HIST_ROOT, REPO_ROOT
from data.group_session import previous_trade_date
from data.hist_calendar import (
    HIST_CALENDAR_DIR,
    HistGroupCalendar,
    hist_calendar_path,
    load_hist_group_calendar,
)
from data.session import ct_ns
from data.stage_e_bars import LegFrame
from screening import harness_freeze, trial_registry

TEST, TEST_IDS = "C2", ("C2-T1", "C2-T2")
ROOT, PLAN, GROUP = "ES", "es2011", "equity"
WINDOW = (date(2011, 5, 3), date(2019, 4, 30))
STORE_FIRST_TRADE_DATE = date(2011, 5, 2)
B_SIGNAL, B_ENTRY, B_EXIT, B_PRIOR = time(14, 29), time(14, 30), time(15, 0), time(14, 59)
MES_TICK = 0.25
COMMISSION_TICKS = 0.976  # $1.22 / $1.25 (reports/stage_e2a_costs.md, MES check)
SPREAD_1430_TICKS = 0.5191  # s_b(14:30), MES check row 14:30
SPREAD_1500_TICKS = 0.5428  # s_b(15:00), MES check row 15:00
# The decimal values the freeze states; the float sum and product differ by one ulp only.
COST_TICKS = 2.0379  # = 0.976 + 0.5191 + 0.5428
PASS_BAR_TICKS = 3.05685  # = 1.5 x 2.0379
if abs(COST_TICKS - (COMMISSION_TICKS + SPREAD_1430_TICKS + SPREAD_1500_TICKS)) > 1e-12 \
        or abs(PASS_BAR_TICKS - 1.5 * COST_TICKS) > 1e-12:
    raise RuntimeError("C2's cost and pass bar must be 0.976 + 0.5191 + 0.5428 and 1.5 x c")
ALPHA = 0.025  # Bonferroni 0.05 / 2, one-sided
MIN_TRADES = 30
GEX_LAGS = (1, 2)
GEX_COLUMNS = ("date", "gex")  # the only columns read; price and dix are never parsed
GEX_HEADER = ("date", "price", "dix", "gex")
MARKER_PATH = REPO_ROOT / "reports" / "stage_e14_c2_RUN_ONCE.json"
FREEZE_PATH = REPO_ROOT / "reports" / "stage_e14_prereg_C2.md"
SCHEMA = "stage_e14_c2_result/1"
LOCAL_TZ = ZoneInfo("America/Vancouver")
CODE_FILES = ("screening/stage_e14_c2.py", "data/hist_bars.py", "data/hist_calendar.py")
REASONS = ("unsourced", "not_a_trade_date", "early_halt", "late_open", "roll_blackout",
           "no_prior_trade_date", "prior_trade_date_unsourced", "no_gex_row", "missing_bar",
           "bar_in_scheduled_closure")
PASS, FAIL, STOPPED = "PASS", "FAIL", "STOPPED"
RC_REFUSED = 2


class C2Refused(RuntimeError):
    """A precondition failed: nothing was written and the evaluation has not run."""


class C2Stop(RuntimeError):
    """A stop after the marker: the verdict is STOPPED with this reason."""


def _now() -> str:
    return datetime.now(LOCAL_TZ).isoformat(timespec="seconds")


def _sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _rel(path: Path) -> str:
    resolved = Path(path).resolve()
    return str(resolved.relative_to(REPO_ROOT)) if resolved.is_relative_to(REPO_ROOT) \
        else str(resolved)


# ------------------------------------------------------------------ GEX ----
@dataclass(frozen=True)
class GexSeries:
    """The CSV's dates and GEX values only (price and dix are never parsed)."""

    dates: tuple[date, ...]
    gex: tuple[float, ...]
    path: str
    sha256: str
    header: tuple[str, ...]

    def record(self) -> dict[str, Any]:  # no value, only the file's identity and its span
        return {"path": self.path, "sha256": self.sha256, "rows": len(self.dates),
                "header": list(self.header), "first_date": str(self.dates[0]),
                "last_date": str(self.dates[-1])}


def parse_gex(raw: bytes, path: Path) -> GexSeries:
    """Validate and parse the GEX CSV (columns date, price, dix, gex). Raises ValueError."""
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig")))
    header = tuple(h.strip() for h in (reader.fieldnames or ()))
    if not set(GEX_HEADER) <= set(header):
        raise ValueError(f"GEX CSV header {list(header)} lacks one of {list(GEX_HEADER)}")
    rows: list[tuple[date, float]] = []
    for i, row in enumerate(reader, start=2):
        clean = {k.strip(): (v or "").strip() for k, v in row.items() if k is not None}
        try:
            day = date.fromisoformat(clean["date"])
            value = float(clean["gex"])
        except (ValueError, KeyError) as exc:
            raise ValueError(f"GEX CSV line {i}: date or gex unreadable ({exc})") from exc
        if len(clean["date"]) != 10 or not math.isfinite(value):
            raise ValueError(f"GEX CSV line {i}: date not YYYY-MM-DD or gex not finite")
        rows.append((day, value))
    if not rows:
        raise ValueError("GEX CSV has no rows")
    rows.sort(key=lambda r: r[0])
    dates = tuple(r[0] for r in rows)
    if len(set(dates)) != len(dates):
        raise ValueError("GEX CSV repeats a date")
    return GexSeries(dates, tuple(r[1] for r in rows), _rel(path),
                     hashlib.sha256(raw).hexdigest(), header)


def load_gex(path: Path, expected_sha256: str) -> GexSeries:
    raw = Path(path).read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != expected_sha256:
        raise ValueError(f"GEX CSV {Path(path).name}: sha256 {digest[:12]}... is not the "
                         f"expected {expected_sha256[:12]}...")
    return parse_gex(raw, path)


def gex_index(series: GexSeries, day: date, lag: int) -> int | None:
    """GEX_LAG 1: the row of the latest CSV date strictly before ``day``; 2: the row before it."""
    if lag not in GEX_LAGS:
        raise ValueError(f"GEX_LAG {lag!r} is not one of {GEX_LAGS}")
    i = bisect.bisect_left(series.dates, day) - 1 - (lag - 1)
    return i if i >= 0 else None


# ------------------------------------------------------------------ eligibility ----
def window_weekdays(first: date = WINDOW[0], last: date = WINDOW[1]) -> list[date]:
    days = (first + timedelta(days=n) for n in range((last - first).days + 1))
    return [d for d in days if d.weekday() < 5]


def calendar_reason(day: date, cal: HistGroupCalendar, blackout: frozenset[date]
                    ) -> tuple[str | None, date | None]:
    """(the first failing calendar condition, None) or (None, the prior trade date)."""
    if day in cal.unsourced:
        return "unsourced", None
    if not cal.is_trade_date(day):
        return "not_a_trade_date", None
    if cal.early_halt_ct(day) is not None:
        return "early_halt", None
    if day in cal.scheduled_late_opens or day in cal.late_opens:
        return "late_open", None
    if day in blackout:
        return "roll_blackout", None
    prior = previous_trade_date(cal, day)
    if prior is None or prior < STORE_FIRST_TRADE_DATE:
        return "no_prior_trade_date", None
    between = (prior + timedelta(days=n) for n in range((day - prior).days))
    if any(d in cal.unsourced for d in between if d.weekday() < 5):
        return "prior_trade_date_unsourced", None
    return None, prior


def count_gex_negative(calendar: HistGroupCalendar, gex: GexSeries, lag: int) -> dict[str, Any]:
    """The power check's count (calendar and GEX only, no bar): window weekdays passing the
    calendar conditions with a GEX row, and how many of those have GEX < 0. The roll blackout
    and the bar conditions are not applied (they need the store). Counts only."""
    excluded: Counter[str] = Counter()
    eligible = negative = 0
    days = window_weekdays()
    trade_dates = [d for d in days if calendar.is_trade_date(d)]
    unsourced = [d for d in days if d in calendar.unsourced]
    for day in days:
        reason, _ = calendar_reason(day, calendar, frozenset())
        idx = None if reason else gex_index(gex, day, lag)
        if reason is None and idx is None:
            reason = "no_gex_row"
        if reason:
            excluded[reason] += 1
            continue
        eligible += 1
        negative += gex.gex[idx] < 0
    return {"window": [str(WINDOW[0]), str(WINDOW[1])], "gex_lag": lag,
            "weekdays": len(days), "calendar_and_gex_eligible": eligible,
            "gex_negative": negative, "excluded_by_reason": dict(excluded),
            # for the freeze's 2% stop on unsourced dates (the lead's check, before the buy)
            "window_unsourced_weekdays": len(unsourced),
            "window_calendar_trade_dates": len(trade_dates),
            "window_unsourced_share_of_weekdays": len(unsourced) / len(days),
            "not_applied": ["roll_blackout", "missing_bar", "bar_in_scheduled_closure"],
            "calendar": calendar.record(), "gex": gex.record()}


# ------------------------------------------------------------------ evaluation ----
@dataclass(frozen=True)
class Trade:
    day: date
    side: int
    g: float
    gex_negative: bool


class BarIndex:
    """Row lookup by ts_event (the bar's start) without a per-row Python dict."""

    def __init__(self, leg: LegFrame) -> None:
        ts = leg.frame["ts_event"].to_numpy().astype(np.int64)
        self.order = np.argsort(ts, kind="stable")
        self.ts = ts[self.order]
        if len(self.ts) > 1 and (np.diff(self.ts) <= 0).any():
            raise C2Stop("the store holds duplicate bar timestamps")

    def get(self, ts_ns: int) -> int | None:
        i = int(np.searchsorted(self.ts, ts_ns))
        return int(self.order[i]) if i < len(self.ts) and self.ts[i] == ts_ns else None


def _bars_for(day: date, prior: date, leg: LegFrame, rows: BarIndex
              ) -> tuple[str | None, str | None, dict[str, int]]:
    """(reason, which bar, the four rows by name) for the rule's bars."""
    frame = leg.frame
    wanted = {"b_14:29": (day, B_SIGNAL), "b_14:30": (day, B_ENTRY), "b_15:00": (day, B_EXIT),
              "b_14:59_prior": (prior, B_PRIOR)}
    found: dict[str, int] = {}
    for name, (on, at) in wanted.items():
        i = rows.get(ct_ns(on, at))
        if i is None or str(frame["trade_date"].iat[i]) != on.isoformat():
            return "missing_bar", name, found
        if bool(frame["in_scheduled_closure"].iat[i]):
            return "bar_in_scheduled_closure", name, found
        found[name] = i
    return None, None, found


def evaluate(leg: LegFrame, cal: HistGroupCalendar, gex: GexSeries, lag: int
             ) -> tuple[list[Trade], dict[str, Any]]:
    """The rule over every window weekday: the trades and the eligibility counts."""
    if leg.root != ROOT or cal.group != GROUP:
        raise C2Stop(f"C2 reads ES on the equity calendar, not {leg.root} on {cal.group}")
    rows = BarIndex(leg)
    excluded: Counter[str] = Counter()
    missing_by_bar: Counter[str] = Counter()
    trades: list[Trade] = []
    eligible = ties = eligible_negative = not_prior_row = 0
    frame = leg.frame
    for day in window_weekdays():
        reason, prior = calendar_reason(day, cal, leg.roll_blackout)
        idx = None if reason else gex_index(gex, day, lag)
        if reason is None and idx is None:
            reason = "no_gex_row"
        found: dict[str, int] = {}
        if reason is None:
            assert prior is not None
            reason, which, found = _bars_for(day, prior, leg, rows)
            if which is not None:
                missing_by_bar[f"{reason}:{which}"] += 1
        if reason is not None:
            excluded[reason] += 1
            continue
        assert idx is not None and prior is not None
        eligible += 1
        negative = gex.gex[idx] < 0
        eligible_negative += negative
        not_prior_row += lag == 1 and gex.dates[idx] != prior
        close_prior = float(frame["close"].iat[found["b_14:59_prior"]])
        close_now = float(frame["close"].iat[found["b_14:29"]])
        r_rod = close_now / close_prior - 1.0
        side = 1 if r_rod > 0 else -1 if r_rod < 0 else 0
        if side == 0:
            ties += 1
            continue
        move = float(frame["open"].iat[found["b_15:00"]]) - float(frame["open"].iat[
            found["b_14:30"]])
        trades.append(Trade(day, side, side * move / MES_TICK, negative))
    counts = {"weekdays_considered": len(window_weekdays()), "eligible_dates": eligible,
              "eligible_dates_gex_negative": eligible_negative,
              "excluded_by_reason": {r: excluded.get(r, 0) for r in REASONS},
              "excluded_bars_by_name": dict(sorted(missing_by_bar.items())),
              "ties_no_trade": ties,
              "gex_row_date_not_prior_trade_date": not_prior_row if lag == 1 else None}
    return trades, counts


def _finite(x: float | None) -> float | None:
    return None if x is None or not math.isfinite(x) else float(x)


def stats_of(g: Sequence[float]) -> dict[str, Any]:
    """n, mean, sd (ddof 1), t = mean / (sd / sqrt(n)), one-sided p (Student t, n - 1 df), and
    the pass criteria (mean >= bar, p <= 0.025, n >= 30)."""
    from scipy.stats import t as student_t  # scipy ships with the pinned lightgbm

    values = np.asarray(g, dtype=np.float64)
    n = int(values.size)
    mean = float(values.mean()) if n else math.nan
    sd = float(values.std(ddof=1)) if n > 1 else math.nan
    if n > 1 and sd > 0:
        t = mean / (sd / math.sqrt(n))
    elif n > 1 and sd == 0:
        t = math.copysign(math.inf, mean) if mean != 0 else math.nan
    else:
        t = math.nan
    p = float(student_t.sf(t, n - 1)) if n > 1 and not math.isnan(t) else math.nan
    criteria = {"mean_at_least_bar": bool(n > 0 and mean >= PASS_BAR_TICKS),
                "p_at_most_alpha": bool(p <= ALPHA), "n_at_least_30": n >= MIN_TRADES}
    return {"n": n, "mean": _finite(mean), "sd": _finite(sd), "t": _finite(t),
            "t_text": None if math.isfinite(t) else str(t), "p": _finite(p),
            "criteria": criteria, "passes": all(criteria.values())}


def passes(mean: float, p: float, n: int) -> bool:
    """Section 5's per-test bar, as stats_of applies it."""
    return bool(mean >= PASS_BAR_TICKS and p <= ALPHA and n >= MIN_TRADES)


def _test_block(trades: Sequence[Trade]) -> dict[str, Any]:
    out = stats_of([t.g for t in trades])
    out["long"] = sum(t.side == 1 for t in trades)
    out["short"] = sum(t.side == -1 for t in trades)
    return out


def verdict_of(t1: dict[str, Any], t2: dict[str, Any]) -> dict[str, Any]:
    exceeds = t1["mean"] is not None and t2["mean"] is not None and t1["mean"] > t2["mean"]
    passed = bool(t1["passes"] and exceeds)
    alone = bool(t2["passes"] and not t1["passes"])
    if passed:
        reading = ("PASS: T1 passes and its mean g exceeds T2's (GEX < 0 conditioning adds "
                   "information)")
    elif alone:
        reading = ("FAIL: T2 passes alone: unconditional late-session momentum in 2011-2019; no "
                   "evidence that GEX adds information (not a pass for C2)")
    elif t1["passes"]:
        reading = "FAIL: T1 passes but its mean g does not exceed T2's"
    else:
        reading = "FAIL: T1 does not pass"
    return {"verdict": PASS if passed else FAIL, "t1_passes": bool(t1["passes"]),
            "t2_passes": bool(t2["passes"]), "t1_mean_exceeds_t2_mean": exceeds,
            "t2_passes_alone": alone, "reading": reading}


def trades_sha256(trades: Sequence[Trade]) -> str:
    """A fingerprint of the trade list (date, side, g, GEX < 0) for an independent check."""
    text = "\n".join(f"{t.day},{t.side},{t.g!r},{int(t.gex_negative)}" for t in trades)
    return hashlib.sha256(text.encode()).hexdigest()


def rule_record(lag: int) -> dict[str, Any]:
    return {"window": [str(WINDOW[0]), str(WINDOW[1])], "root": ROOT, "plan": PLAN,
            "bars_ct": {"signal": "close(b_14:29 on d) / close(b_14:59 on the prior trade "
                                  "date) - 1", "entry": "open(b_14:30)", "exit": "open(b_15:00)"},
            "g": "side x (open(b_15:00) - open(b_14:30)) / 0.25, MES ticks",
            "t1": "trades on eligible dates with GEX < 0", "t2": "trades on every eligible date",
            "gex_lag": lag, "cost_ticks": {"commission": COMMISSION_TICKS,
                                           "s_b_14_30": SPREAD_1430_TICKS,
                                           "s_b_15_00": SPREAD_1500_TICKS, "c": COST_TICKS},
            "pass_bar_ticks": PASS_BAR_TICKS, "alpha_one_sided": ALPHA, "min_trades": MIN_TRADES,
            "exclusion_order": list(REASONS)}


def result_of(trades: Sequence[Trade], counts: dict[str, Any]) -> dict[str, Any]:
    t1 = _test_block([t for t in trades if t.gex_negative])
    t2 = _test_block(trades)
    return {**verdict_of(t1, t2), "stop_reason": None, "tests": {"C2-T1": t1, "C2-T2": t2},
            "eligibility": counts, "trades_sha256": trades_sha256(trades)}


# ------------------------------------------------------------------ the run ----
@dataclass(frozen=True)
class RunInputs:
    store_sha256: str
    gex_path: Path
    gex_sha256: str
    gex_lag: int
    harness_sha256: str
    freeze_sha256: str
    out: Path
    freeze_path: Path = FREEZE_PATH
    marker_path: Path = MARKER_PATH
    registry_path: Path = trial_registry.REGISTRY_PATH
    hist_root: Path = HIST_ROOT
    calendar_base: Path = HIST_CALENDAR_DIR


def _check_file(path: Path, expected: str, what: str) -> str:
    if not Path(path).is_file():
        raise C2Refused(f"{what} {path} does not exist")
    got = _sha256(path)
    if got != expected:
        raise C2Refused(f"{what} {Path(path).name}: sha256 {got[:12]}... is not the expected "
                        f"{expected[:12]}...")
    return got


def preconditions(inp: RunInputs, preflight: Callable[[str], str]) -> dict[str, Any]:
    """Every check before the marker. Raises C2Refused; returns the input records."""
    from data.hist_store import hist_parquet_path

    harness = preflight(inp.harness_sha256)
    if inp.marker_path.exists() or inp.out.exists():
        raise C2Refused(f"C2 runs once: {inp.marker_path.name if inp.marker_path.exists() else
                                         inp.out.name} exists")
    if inp.gex_lag not in GEX_LAGS:
        raise C2Refused(f"GEX_LAG {inp.gex_lag!r} is not one of {GEX_LAGS}")
    _check_file(inp.freeze_path, inp.freeze_sha256, "freeze")
    try:
        entry = trial_registry.require_registered(TEST_IDS, test=TEST,
                                                  freeze_sha256=inp.freeze_sha256,
                                                  path=inp.registry_path)
    except trial_registry.TrialRegistryError as exc:
        raise C2Refused(str(exc)) from exc
    store = hist_parquet_path(ROOT, PLAN, inp.hist_root)
    _check_file(store, inp.store_sha256, "store")
    _check_file(inp.gex_path, inp.gex_sha256, "GEX CSV")
    calendar = hist_calendar_path(GROUP, inp.calendar_base)
    if not calendar.is_file():
        raise C2Refused(f"hist equity calendar {calendar} does not exist")
    try:  # a calendar file only (no bar, no GEX value): a malformed one is refused here
        load_hist_group_calendar(GROUP, base=inp.calendar_base)
    except (ValueError, RuntimeError) as exc:
        raise C2Refused(f"hist equity calendar refused: {exc}") from exc
    return {"harness_sha256": harness,
            "freeze": {"path": _rel(inp.freeze_path), "sha256": inp.freeze_sha256},
            "registry": {"path": _rel(inp.registry_path), "entry_id": entry["entry_id"],
                         "n_before": entry["n_before"], "n_after": entry["n_after"]},
            "store": {"path": _rel(store), "sha256": inp.store_sha256},
            "gex_expected_sha256": inp.gex_sha256,
            "calendar_sha256_before_marker": _sha256(calendar),
            "code": {p: _sha256(REPO_ROOT / p) for p in CODE_FILES if (REPO_ROOT / p).is_file()}}


def _write_new(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as fh:  # never over an existing file
        fh.write(json.dumps(payload, indent=1, default=str) + "\n")


def _evaluate_inputs(inp: RunInputs, records: dict[str, Any]) -> dict[str, Any]:
    from data.hist_bars import load_hist_leg

    cal = load_hist_group_calendar(GROUP, base=inp.calendar_base,
                                   expected_sha256=records["calendar_sha256_before_marker"])
    gex = load_gex(inp.gex_path, inp.gex_sha256)
    leg = load_hist_leg(ROOT, PLAN, expected_sha256=inp.store_sha256, hist_root=inp.hist_root,
                        calendar=cal)
    trades, counts = evaluate(leg, cal, gex, inp.gex_lag)
    result = result_of(trades, counts)
    records.update({"calendar": cal.record(), "gex": gex.record()})
    return result


def run(inp: RunInputs, *, preflight: Callable[[str], str] | None = None,
        log: Callable[[str], None] = print) -> dict[str, Any]:
    """The one evaluation. C2Refused before the marker; afterwards always a written result."""
    preflight = preflight or harness_freeze.preflight
    records = preconditions(inp, preflight)
    started = _now()
    _write_new(inp.marker_path, {"schema": "stage_e14_c2_run_once/1", "test": TEST,
                                 "started_local": started, "out": _rel(inp.out),
                                 "gex_lag": inp.gex_lag, "inputs": records})
    log(f"C2 marker written at {started}; the evaluation runs once from here")
    try:
        result = _evaluate_inputs(inp, records)
    except Exception as exc:  # noqa: BLE001 — every stop after the marker is the verdict
        result = {"verdict": STOPPED, "stop_reason": f"{type(exc).__name__}: {exc}"}
    payload = {"schema": SCHEMA, "test": TEST, "test_ids": list(TEST_IDS), **result,
               "rule": rule_record(inp.gex_lag), "inputs": records,
               "started_local": started, "finished_local": _now()}
    _write_new(inp.out, payload)
    log(f"C2 verdict {payload['verdict']}" + (f" ({payload['stop_reason']})"
                                              if payload.get("stop_reason") else ""))
    return payload


# ------------------------------------------------------------------ CLI ----
def _run_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m screening.stage_e14_c2")
    parser.add_argument("--store-sha256", required=True)
    parser.add_argument("--gex", required=True)
    parser.add_argument("--gex-sha256", required=True)
    parser.add_argument("--gex-lag", type=int, required=True, choices=GEX_LAGS)
    parser.add_argument("--harness-sha256", required=True)
    parser.add_argument("--freeze-sha256", required=True)
    parser.add_argument("--freeze", default=str(FREEZE_PATH))
    parser.add_argument("--out", required=True)
    return parser


def _count_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m screening.stage_e14_c2 count")
    parser.add_argument("--gex", required=True)
    parser.add_argument("--gex-sha256", required=True)
    parser.add_argument("--gex-lag", type=int, required=True, choices=GEX_LAGS)
    return parser


def main(argv: list[str] | None = None, *, preflight: Callable[[str], str] | None = None,
         calendar_base: Path = HIST_CALENDAR_DIR) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv[:1] == ["count"]:
        args = _count_parser().parse_args(argv[1:])
        try:
            counts = count_gex_negative(load_hist_group_calendar(GROUP, base=calendar_base),
                                        load_gex(Path(args.gex), args.gex_sha256), args.gex_lag)
        except (ValueError, OSError, RuntimeError) as exc:
            print(f"REFUSED ({type(exc).__name__}): {exc}", file=sys.stderr)
            return RC_REFUSED
        print(json.dumps({k: v for k, v in counts.items() if k not in ("calendar", "gex")}))
        return 0
    args = _run_parser().parse_args(argv[1:] if argv[:1] == ["run"] else argv)
    inp = RunInputs(args.store_sha256, Path(args.gex), args.gex_sha256, args.gex_lag,
                    args.harness_sha256, args.freeze_sha256, Path(args.out),
                    freeze_path=Path(args.freeze), calendar_base=calendar_base)
    try:
        payload = run(inp, preflight=preflight)
    except (C2Refused, harness_freeze.HarnessFreezeError, OSError) as exc:
        print(f"REFUSED, nothing written, the evaluation has not run ({type(exc).__name__}): "
              f"{exc}", file=sys.stderr)
        return RC_REFUSED
    return 0 if payload["verdict"] in (PASS, FAIL) else 1


if __name__ == "__main__":
    sys.exit(main())
