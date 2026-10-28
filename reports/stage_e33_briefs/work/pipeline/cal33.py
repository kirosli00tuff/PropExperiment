"""E.33 calendar API (brief_DataCoder deliverable 4). Names are fixed: functions may be added,
never renamed. Dates may be passed as datetime.date or "YYYY-MM-DD"; dates come back as
datetime.date. Times are int64 UTC ns. Prices stay Databento fixed-point int64 (1e-9 units).

- trade_dates(), burn_in(), oof_dates(): the 816 regular grains trade dates 2020-12-01..2024-02-29,
  the first 20, the other 796 (P1.4).
- day_bounds(D): (start_ns, end_ns) of [D-1 16:00 CT, D 16:00 CT) (P0.3).
- ct_ns(D, "HH:MM:SS"): CT wall time on D to UTC ns, DST-aware (zoneinfo, fold 0).
- fronts(D): {"ZM", "ZS", "ZL": instrument_id} of ZM.v.0, ZS.v.0, ZL.v.0 on UTC date D from the
  discovery manifests' symbology (measure31.merge_mappings, instrument_on).
- excluded(D): (bool, reasons) of P1.4 (ZM roll date, the trade date after it, early close or
  holiday, scheduled late open).
- segment_id(D): P4 G2 segments (maximal runs of trade dates with the three fronts unchanged).
- releases(D): the P3.6 rule 3 release instants R of D (11:00:00 CT), sorted, unique.
- limits(D): (HL, LL) of the ZM front's last definition with ts_recv <= 08:30:00 CT on D, or None.
- expiry_trade_dates(D): trade dates T with D < T <= the CT date of the ZM front's expiration
  (READING CAL-1).
- monday_or_after_closure(D) (C.10), jja(D) (C.15), tick(root) (P0.3).
- previous_trade_dates(D, n): the up to n trade dates of the 816 before D (look-backs).

CLI: cal33.py summary | releases  (counts; the release table).
"""

# ruff: noqa: I001 - data33/guard33 set sys.path before the E.31 and repo imports
from __future__ import annotations

import csv
import re
import sys
from collections import Counter
from datetime import date, datetime, time, timedelta
from functools import lru_cache
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import data33 as d33  # noqa: E402
import guard33 as g  # noqa: E402
import measure31 as m31  # noqa: E402
import mbo_book31 as mb  # noqa: E402
from data.session import ct_ns as _ct_ns  # noqa: E402

CT = ZoneInfo("America/Chicago")
N_TRADE_DATES, N_BURN_IN, N_OOF = 816, 20, 796
FRONT_SYMBOLS = {"ZM": ("Z1", "ZM.v.0"), "ZS": ("Z2", "ZS.v.0"), "ZL": ("Z3", "ZL.v.0")}
UNDEF_PRICE = mb.UNDEF_PRICE
UNDEF_TIMESTAMP = 2**64 - 1
LIMIT_ASOF = "08:30:00"
RELEASE_CT = "11:00:00"
REASON_ROLL, REASON_AFTER_ROLL = m31.REASON_ROLL, m31.REASON_AFTER_ROLL
REASON_HOLIDAY, REASON_LATE_OPEN = m31.REASON_HOLIDAY, m31.REASON_LATE_OPEN
REASON_NO_MAPPING = m31.REASON_NO_MAPPING

RELEASE_FILES = (g.RESEARCH31 / "usda_releases_ext.csv", g.RESEARCH31 / "usda_releases.csv")
RELEASE_COLUMNS = ["date", "time_et", "report", "source_url", "evidence"]
RELEASE_EXPECTED = {
    "USDA WASDE": 39, "NASS Crop Production": 39, "NASS Crop Production Annual": 4,
    "NASS Grain Stocks": 13, "NASS Prospective Plantings": 3, "NASS Acreage": 3,
    "NOPA Monthly Crush (not USDA)": 37}
NOPA = "NOPA Monthly Crush (not USDA)"
NOPA_RULE = "NOPA rule date"
NOPA_RULE_MONTHS = ("2022-11", "2022-12")
_ISO = re.compile(r"\d{4}-\d{2}-\d{2}")


def _d(day: date | str) -> date:
    return g._as_date(day)


# ------------------------------------------------------------------ dates ----
@lru_cache(maxsize=1)
def _calendar() -> m31.GroupCalendar:
    return m31.grains()


@lru_cache(maxsize=1)
def _trade_dates() -> tuple[date, ...]:
    months = sorted({sf.month for sf in d33.source_files()["Z1"]})
    days = tuple(m31.month_trade_dates(_calendar(), months))
    if len(days) != N_TRADE_DATES or days[0] != g.DISC_FIRST or days[-1] != g.DISC_LAST:
        raise RuntimeError(f"expected {N_TRADE_DATES} trade dates 2020-12-01..2024-02-29, "
                           f"found {len(days)} ({days[0]}..{days[-1]})")
    return days


@lru_cache(maxsize=1)
def _index() -> dict[date, int]:
    return {d: i for i, d in enumerate(_trade_dates())}


def trade_dates() -> list[date]:
    """The 816 regular grains trade dates 2020-12-01..2024-02-29 (P1.4)."""
    return list(_trade_dates())


def burn_in() -> list[date]:
    """The first 20 trade dates (features only; no rows, trades or daily values)."""
    return list(_trade_dates()[:N_BURN_IN])


def oof_dates() -> list[date]:
    """The 796 OOF dates (trade dates after the burn-in)."""
    out = list(_trade_dates()[N_BURN_IN:])
    if len(out) != N_OOF:
        raise RuntimeError(f"expected {N_OOF} OOF dates, found {len(out)}")
    return out


def is_trade_date(day: date | str) -> bool:
    return _d(day) in _index()


def _pos(day: date | str) -> int:
    d = _d(day)
    if d not in _index():
        raise ValueError(f"{d} is not one of the 816 trade dates")
    return _index()[d]


def previous_trade_dates(day: date | str, n: int) -> list[date]:
    """The up to n trade dates of the 816 before D, oldest first (fewer near the start)."""
    i = _pos(day)
    return list(_trade_dates()[max(0, i - n):i])


def day_bounds(day: date | str) -> tuple[int, int]:
    """Trade date D's ts_recv window [D-1 16:00 CT, D 16:00 CT) in UTC ns."""
    return d33.window(_d(day))


def ct_ns(day: date | str, hhmmss: str) -> int:
    """CT wall time "HH:MM:SS" (or "HH:MM") on calendar date D as UTC ns (DST-aware)."""
    parts = [int(x) for x in hhmmss.split(":")]
    if len(parts) == 2:
        parts.append(0)
    return _ct_ns(_d(day), time(*parts))


# ------------------------------------------------------------------ fronts and segments ----
@lru_cache(maxsize=1)
def _mappings() -> dict[str, m31.Mappings]:
    files = g.discovery_manifest()["files"]
    out = {}
    for root, (series, symbol) in FRONT_SYMBOLS.items():
        headers = [f["header"] for f in files if f["series"] == series]
        out[root] = {symbol: m31.merge_mappings(headers).get(symbol, [])}
    return out


def _front_on(root: str, day: date) -> int | None:
    series, symbol = FRONT_SYMBOLS[root]
    return m31.instrument_on(_mappings()[root], symbol, day)


@lru_cache(maxsize=1)
def _fronts_table() -> dict[date, dict[str, int]]:
    out = {}
    for day in _trade_dates():
        f = {root: _front_on(root, day) for root in FRONT_SYMBOLS}
        if any(v is None for v in f.values()):
            raise RuntimeError(f"no front mapping on {day}: {f}")
        out[day] = f
    return out


def fronts(day: date | str) -> dict[str, int]:
    """{"ZM", "ZS", "ZL": instrument_id} of ZM.v.0, ZS.v.0, ZL.v.0 on UTC date D (P0.3)."""
    return dict(_fronts_table()[_d(day)]) if _d(day) in _index() else _raise_not_trade(day)


def _raise_not_trade(day: date | str) -> dict[str, int]:
    raise ValueError(f"{_d(day)} is not one of the 816 trade dates")


@lru_cache(maxsize=1)
def _segments() -> dict[date, int]:
    out, seg, prev = {}, 0, None
    for day in _trade_dates():
        cur = _fronts_table()[day]
        if prev is not None and cur != prev:
            seg += 1
        out[day] = seg
        prev = cur
    return out


def segment_id(day: date | str) -> int:
    """P4 G2: segment number (0-based) of D; a new segment starts at any ZM, ZS or ZL front
    change from the previous trade date of the 816."""
    return _segments()[_d(day)] if _d(day) in _index() else _raise_not_trade(day)


# ------------------------------------------------------------------ exclusions ----
def _prev_cal_trade_date(day: date) -> date:
    cal, prev = _calendar(), day - timedelta(days=1)
    while not (cal.covers(prev) and cal.is_trade_date(prev)):
        prev -= timedelta(days=1)
    return prev


@lru_cache(maxsize=1)
def _exclusions() -> dict[date, tuple[str, ...]]:
    """Every reason of P1.4 per trade date, by the rule. Roll: the ZM.v.0 instrument on D differs
    from the one on the previous grains trade date (measure31.roll_reasons); after roll: the
    trade date after a roll date. Calendar: measure31.calendar_reason (holiday or early close,
    scheduled late open)."""
    cal, days = _calendar(), _trade_dates()
    zm_maps = _mappings()["ZM"]
    reasons: dict[date, set[str]] = {d: set() for d in days}
    for i, day in enumerate(days):
        iid = _front_on("ZM", day)
        before = _front_on("ZM", _prev_cal_trade_date(day))
        if iid is None or before is None:
            reasons[day].add(REASON_NO_MAPPING)
        elif iid != before:
            reasons[day].add(REASON_ROLL)
            if i + 1 < len(days):
                reasons[days[i + 1]].add(REASON_AFTER_ROLL)
        why = m31.calendar_reason(cal, day)
        if why:
            reasons[day].add(why)
    # cross-check against measure31.roll_reasons (it keeps one reason per date)
    theirs = m31.roll_reasons(zm_maps, "ZM.v.0", list(days), cal)
    ours = {d for d, r in reasons.items() if r & {REASON_ROLL, REASON_AFTER_ROLL,
                                                   REASON_NO_MAPPING}}
    theirs_in = {d for d in theirs if d in reasons}
    if ours != theirs_in:
        raise RuntimeError(f"roll exclusions differ from measure31.roll_reasons: "
                           f"{sorted(ours ^ theirs_in)}")
    return {d: tuple(sorted(r)) for d, r in reasons.items()}


def excluded(day: date | str) -> tuple[bool, tuple[str, ...]]:
    """(True, reasons) if D is excluded from trading by P1.4, else (False, ())."""
    d = _d(day)
    if d not in _index():
        raise ValueError(f"{d} is not one of the 816 trade dates")
    r = _exclusions()[d]
    return bool(r), r


def exclusion_counts(dates: list[date] | None = None) -> dict[str, int]:
    """Counts by reason (a date counts under each of its reasons) and the distinct dates."""
    days = list(_trade_dates()) if dates is None else [_d(x) for x in dates]
    c: Counter[str] = Counter()
    for d in days:
        for r in _exclusions()[d]:
            c[r] += 1
    c["excluded_dates"] = sum(1 for d in days if _exclusions()[d])
    return dict(sorted(c.items()))


# ------------------------------------------------------------------ releases ----
def parse_release_lines(lines: list[str], where: str = "") -> list[tuple[date, str, int]]:
    """P3.6 rule 3 parse rule: skip lines starting with "#"; columns date, time_et, report,
    source_url, evidence; skip rows whose date is not a valid YYYY-MM-DD; keep rows with time_et
    "12:00" and report exactly one of the seven names (any evidence grade); R = 11:00:00 CT."""
    reader = csv.DictReader([ln for ln in lines if not ln.startswith("#")])
    if reader.fieldnames != RELEASE_COLUMNS:
        raise RuntimeError(f"{where}: columns {reader.fieldnames} != {RELEASE_COLUMNS}")
    rows = []
    for row in reader:
        raw = row["date"] or ""
        if not _ISO.fullmatch(raw):
            continue
        try:
            day = date.fromisoformat(raw)
        except ValueError:
            continue
        if row["time_et"] != "12:00" or row["report"] not in RELEASE_EXPECTED:
            continue
        rows.append((day, row["report"], ct_ns(day, RELEASE_CT)))
    return rows


@lru_cache(maxsize=1)
def release_table() -> tuple[tuple[date, str, int], ...]:
    """(date, report, R_ns) of every P3.6 rule-3 release row plus the NOPA rule dates, sorted.
    Asserts the protocol's counts; raises on any other count."""
    rows: list[tuple[date, str, int]] = []
    for path in RELEASE_FILES:
        g.check_reference(path)
        with path.open(encoding="utf-8", newline="") as fh:
            rows.extend(parse_release_lines(list(fh), str(path)))
    counts = Counter(r for _, r, _ in rows)
    if dict(counts) != RELEASE_EXPECTED:
        raise RuntimeError(f"P3.6 release counts {dict(counts)} != expected {RELEASE_EXPECTED}")
    months = sorted({sf.month for sf in d33.source_files()["Z1"]})
    with_nopa = {f"{d:%Y-%m}" for d, r, _ in rows if r == NOPA}
    missing = tuple(m for m in months if m not in with_nopa)
    if missing != NOPA_RULE_MONTHS:
        raise RuntimeError(f"months without a NOPA row {missing} != {NOPA_RULE_MONTHS}")
    cal = _calendar()
    for m in missing:
        day = date.fromisoformat(f"{m}-15")
        while not (cal.covers(day) and cal.is_trade_date(day)):
            day += timedelta(days=1)
        rows.append((day, NOPA_RULE, ct_ns(day, RELEASE_CT)))
    if sum(1 for _, r, _ in rows if r == NOPA_RULE) != 2:
        raise RuntimeError("expected 2 NOPA rule dates")
    return tuple(sorted(rows))


@lru_cache(maxsize=1)
def _releases_by_date() -> dict[date, tuple[int, ...]]:
    out: dict[date, set[int]] = {}
    for day, _, r in release_table():
        out.setdefault(day, set()).add(r)
    return {d: tuple(sorted(v)) for d, v in out.items()}


def releases(day: date | str) -> list[int]:
    """Sorted unique release instants R (UTC ns, 11:00:00 CT) of P3.6 rule 3 on D."""
    return list(_releases_by_date().get(_d(day), ()))


# ------------------------------------------------------------------ definitions ----
@lru_cache(maxsize=1)
def _defs_by_instrument() -> dict[int, np.ndarray]:
    arr = d33.definitions(outright_only=True)
    order = np.argsort(arr["instrument_id"], kind="stable")  # keeps ts_recv order per id
    s = arr[order]
    ids, starts = np.unique(s["instrument_id"], return_index=True)
    bounds = list(starts) + [len(s)]
    return {int(i): s[bounds[k]:bounds[k + 1]] for k, i in enumerate(ids)}


def front_definition(day: date | str, root: str = "ZM", asof: str = LIMIT_ASOF) -> np.void | None:
    """The root front's last definition record with ts_recv <= asof CT on D (as-of over all Z4
    files in ts_recv order, state carried across files and dates), or None."""
    d = _d(day)
    iid = fronts(d)[root]
    recs = _defs_by_instrument().get(iid)
    if recs is None or len(recs) == 0:
        return None
    k = int(np.searchsorted(recs["ts_recv"], np.int64(ct_ns(d, asof)), side="right")) - 1
    return recs[k] if k >= 0 else None


def limits(day: date | str) -> tuple[int, int] | None:
    """(HL, LL) of the ZM front's last definition with ts_recv <= 08:30:00 CT on D (P3.6 rule 5),
    int64 1e-9 USD/short ton; None if there is no such record or either field is UNDEF_PRICE
    (2^63 - 1) or 0 (the limit-proximity part is then skipped for D)."""
    return limits_of(front_definition(day))


def limits_of(rec: np.void | None) -> tuple[int, int] | None:
    """(HL, LL) of one definition record, None if absent or either is UNDEF_PRICE or 0."""
    if rec is None:
        return None
    hl, ll = int(rec["high_limit_price"]), int(rec["low_limit_price"])
    if hl in (UNDEF_PRICE, 0) or ll in (UNDEF_PRICE, 0):
        return None
    return hl, ll


def limits_none_dates(dates: list[date] | None = None) -> list[date]:
    days = list(_trade_dates()) if dates is None else [_d(x) for x in dates]
    return [d for d in days if limits(d) is None]


def expiry_trade_dates(day: date | str) -> int | None:
    """READING CAL-1: the number of grains trade dates T with D < T <= E, E = the CT calendar
    date of the expiration of the ZM front of D per its last definition with ts_recv <= 08:30:00
    CT on D (0 on the expiration date itself). None if no definition or expiration is undefined.
    C.7 = min(this, 60) / 60."""
    d = _d(day)
    rec = front_definition(d)
    if rec is None or int(rec["expiration"]) in (UNDEF_TIMESTAMP, 0):
        return None
    exp = datetime.fromtimestamp(int(rec["expiration"]) / g.NS, CT).date()
    cal, n, cur = _calendar(), 0, d + timedelta(days=1)
    while cur <= exp:
        if not cal.covers(cur):
            raise RuntimeError(f"grains calendar does not cover {cur}")
        n += int(cal.is_trade_date(cur))
        cur += timedelta(days=1)
    return n


# ------------------------------------------------------------------ calendar flags ----
def monday_or_after_closure(day: date | str) -> bool:
    """C.10: D is a Monday, or a calendar day strictly between the previous grains trade date
    and D is a full closure."""
    d = _d(day)
    if d.weekday() == 0:
        return True
    cal, prev = _calendar(), _prev_cal_trade_date(d)
    cur = prev + timedelta(days=1)
    while cur < d:
        if cal.is_full_closure(cur):
            return True
        cur += timedelta(days=1)
    return False


def jja(day: date | str) -> bool:
    """C.15: D falls in June, July or August."""
    return _d(day).month in (6, 7, 8)


@lru_cache(maxsize=3)
def tick(root: str) -> int:
    """P0.3 tick of root in 1e-9 price units from the Z4 min_price_increment, after
    measure31.checked_tick (E.31's lead ruling: ZS and ZL quotes are US cents, so the USD check
    accepts cents). ZM 100_000_000 (0.10 USD/short ton), ZS 250_000_000 (0.25 c/bu),
    ZL 10_000_000 (0.01 c/lb)."""
    if root not in FRONT_SYMBOLS:
        raise ValueError(f"root must be ZM, ZS or ZL, not {root!r}")
    defs = m31.definition_rows(d33.definitions(outright_only=True))
    return int(m31.checked_tick(defs, root))


# ------------------------------------------------------------------ CLI ----
def summary() -> dict:
    days, oof = trade_dates(), oof_dates()
    table = release_table()
    none_all = limits_none_dates()
    exp = [expiry_trade_dates(d) for d in days]
    return {
        "trade_dates": len(days), "burn_in": len(burn_in()), "oof": len(oof),
        "first_oof": oof[0].isoformat(),
        "exclusions_816": exclusion_counts(), "exclusions_oof": exclusion_counts(oof),
        "segments": segment_id(days[-1]) + 1,
        "release_counts": dict(sorted(Counter(r for _, r, _ in table).items())),
        "nopa_rule_dates": [d.isoformat() for d, r, _ in table if r == NOPA_RULE],
        "release_dates": len(_releases_by_date()),
        "release_dates_not_trade_dates": sorted(
            d.isoformat() for d in _releases_by_date() if d not in _index()),
        "release_trade_dates_oof": sum(1 for d in oof if releases(d)),
        "limits_none_816": len(none_all),
        "limits_none_oof": sum(1 for d in none_all if d in set(oof)),
        "limits_none_dates": [d.isoformat() for d in none_all],
        "expiry_none": sum(1 for e in exp if e is None),
        "expiry_min_max": [min(e for e in exp if e is not None),
                           max(e for e in exp if e is not None)],
        "monday_or_after_closure_816": sum(monday_or_after_closure(d) for d in days),
        "jja_816": sum(jja(d) for d in days),
        "ticks": {r: tick(r) for r in FRONT_SYMBOLS},
    }


def main(argv: list[str] | None = None) -> int:
    import json

    args = sys.argv[1:] if argv is None else argv
    if args == ["summary"]:
        print(json.dumps(summary(), indent=1))
        return 0
    if args == ["releases"]:
        table = release_table()
        for report, n in sorted(Counter(r for _, r, _ in table).items()):
            print(f"{report}: {n}")
        for day, report, r in table:
            print(f"{day.isoformat()}\t{report}\t{r}")
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
