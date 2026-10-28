"""E.33 implementation B: the exclusion calendar of the labels (P1.4, P3.6 rules 3 and 5), the
trade-date lists, the ZM fronts and the ZM tick. Written independently of pipeline A's cal33.

Sources (all reads through guard33): the program grains calendar (P1.2 b), the E.31 Z1 month
markers' symbology mappings (the manifests' symbology, 0.3), data33.definitions() (Z4), and the
two release calendars of P3.6 rule 3 (reference data, sha256-pinned by the protocol).
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import re
import sys
from collections import Counter
from datetime import date, time, timedelta
from functools import lru_cache
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
PIPELINE = HERE.parent / "pipeline"
for _p in (str(PIPELINE), str(HERE)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import guard33 as g  # noqa: E402  (adds REPO and the E.31 pilot folder to sys.path)
import measure31 as m31  # noqa: E402
from labB import ct_ns  # noqa: E402

from data.group_session import trade_dates_between  # noqa: E402

UNIVERSE = (date(2020, 12, 1), date(2024, 2, 29))
N_UNIVERSE, N_BURN_IN, N_OOF = 816, 20, 796
B3_SEED, B3_N = 20261028, 20
FRONT_SYMBOL = "ZM.v.0"
LIMIT_ASOF = time(8, 30)  # P3.6 rule 5: last definition with ts_recv <= 08:30 CT on D
RELEASE_CT = time(11, 0)  # R = 11:00:00 CT (12:00 ET)
RESEARCH = g.REPO / "reports" / "stage_e31_briefs" / "research"
RELEASE_FILES = {  # P3.6 rule 3, sha256 as printed in the protocol
    "usda_releases_ext.csv":
        "55df3b14f4565f607294e313c0b8fc26f3652df1d4de02a732861b47ba9feb88",
    "usda_releases.csv":
        "0743c0e27ac963d2d47a691a8b644f10208cb64b8f629a09ac788d829ad45119",
}
RELEASE_REPORTS = ("USDA WASDE", "NASS Crop Production", "NASS Crop Production Annual",
                   "NASS Grain Stocks", "NASS Prospective Plantings", "NASS Acreage",
                   "NOPA Monthly Crush (not USDA)")
NOPA = "NOPA Monthly Crush (not USDA)"
EXPECTED_RELEASE_COUNTS = {"USDA WASDE": 39, "NASS Crop Production": 39,
                           "NASS Crop Production Annual": 4, "NASS Grain Stocks": 13,
                           "NASS Prospective Plantings": 3, "NASS Acreage": 3, NOPA: 37,
                           "NOPA rule dates": 2}
EXPECTED_NOPA_GAPS = ("2022-11", "2022-12")
_ISO = re.compile(r"^\d{4}-\d{2}-\d{2}$")


# ------------------------------------------------------------------ dates ----
@lru_cache(maxsize=1)
def calendar():  # noqa: ANN201 - data.group_session.GroupCalendar
    return m31.grains()


@lru_cache(maxsize=1)
def trade_dates() -> tuple[date, ...]:
    """P1.4: the 816 regular grains trade dates 2020-12-01..2024-02-29."""
    days = tuple(trade_dates_between(calendar(), *UNIVERSE))
    if len(days) != N_UNIVERSE:
        raise AssertionError(f"expected {N_UNIVERSE} trade dates, found {len(days)}")
    return days


def burn_in_dates() -> tuple[date, ...]:
    return trade_dates()[:N_BURN_IN]


def oof_dates() -> tuple[date, ...]:
    out = tuple(sorted(trade_dates()[N_BURN_IN:]))
    if len(out) != N_OOF:
        raise AssertionError("OOF list length")
    return out


def b3_dates() -> list[date]:
    """reports/stage_e33_STATE.md 14:45 B3 dates rule, applied to this module's OOF list."""
    oof = np.array(oof_dates(), dtype=object)
    idx = np.random.default_rng(B3_SEED).choice(N_OOF, B3_N, replace=False)
    return sorted(oof[idx].tolist())


def previous_trade_dates(day: date, k: int) -> list[date]:
    """The k grains trade dates before ``day`` (oldest first), within the universe."""
    days = trade_dates()
    pos = days.index(day)
    if pos < k:
        raise ValueError(f"{day}: fewer than {k} trade dates before it in the universe")
    return list(days[pos - k:pos])


# ------------------------------------------------------------------ fronts ----
@lru_cache(maxsize=1)
def zm_mappings() -> m31.Mappings:
    """Symbology of ZM.v.0 / ZM.v.1 from the 39 E.31 Z1 month markers (the request metadata of
    the discovery files; read through guard33)."""
    markers = []
    for path in sorted(g.E31_Z1.glob("*.split.json")):
        markers.append(json.loads(g.check_path(path).read_text(encoding="utf-8")))
    if len(markers) != 39:
        raise AssertionError(f"expected 39 Z1 month markers, found {len(markers)}")
    return m31.merge_mappings(markers)


def zm_front(day: date) -> int | None:
    return m31.instrument_on(zm_mappings(), FRONT_SYMBOL, day)


@lru_cache(maxsize=1)
def exclusions() -> dict[date, tuple[str, ...]]:
    """P1.4 (i) roll date and the trade date after (measure31.roll_reasons; READING LB-14: its
    'roll_status_unknown' and 'no_symbol_mapping' reasons exclude too) and (ii) early-close and
    scheduled late-open dates (measure31.calendar_reason), over the 816 dates."""
    cal = calendar()
    days = list(trade_dates())
    rolls = m31.roll_reasons(zm_mappings(), FRONT_SYMBOL, days, cal)
    out: dict[date, tuple[str, ...]] = {}
    for d in days:
        reasons = []
        if d in rolls:
            reasons.append(rolls[d])
        cr = m31.calendar_reason(cal, d)
        if cr:
            reasons.append(cr)
        if reasons:
            out[d] = tuple(reasons)
    return out


# ------------------------------------------------------------------ releases ----
def _read_release_file(name: str) -> str:
    path = g.check_reference(RESEARCH / name)
    raw = path.read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    if sha != RELEASE_FILES[name]:
        raise AssertionError(f"{name}: sha256 {sha} differs from the protocol's")
    return raw.decode("utf-8")


@lru_cache(maxsize=1)
def releases() -> tuple[dict[date, tuple[int, ...]], dict[str, int]]:
    """P3.6 rule 3 parse rule; returns {D: R instants (UTC ns)} and the asserted counts."""
    counts: Counter[str] = Counter()
    days_by_report: dict[str, set[date]] = {}
    for name in RELEASE_FILES:
        text = _read_release_file(name)
        body = "\n".join(line for line in text.splitlines() if not line.startswith("#"))
        for row in csv.reader(io.StringIO(body)):
            if len(row) < 3:
                continue
            day_s, time_et, report = row[0].strip(), row[1].strip(), row[2].strip()
            if not _ISO.match(day_s):
                continue
            try:
                day = date.fromisoformat(day_s)
            except ValueError:
                continue
            if time_et != "12:00" or report not in RELEASE_REPORTS:
                continue
            counts[report] += 1
            days_by_report.setdefault(report, set()).add(day)
    nopa_months = {f"{d:%Y-%m}" for d in days_by_report.get(NOPA, set())}
    months = sorted({f"{d:%Y-%m}" for d in trade_dates()})
    gaps = [m for m in months if m not in nopa_months]
    if tuple(gaps) != EXPECTED_NOPA_GAPS:
        raise AssertionError(f"NOPA months without a valid row: {gaps}")
    cal = calendar()
    rule_days = []
    for m in gaps:
        d = date.fromisoformat(f"{m}-15")
        while not cal.is_trade_date(d):
            d += timedelta(days=1)
        rule_days.append(d)
    counts["NOPA rule dates"] = len(rule_days)
    found = {k: int(counts.get(k, 0)) for k in EXPECTED_RELEASE_COUNTS}
    if found != EXPECTED_RELEASE_COUNTS or set(counts) - set(EXPECTED_RELEASE_COUNTS):
        raise AssertionError(f"release counts {dict(counts)} differ from P3.6 rule 3")
    out: dict[date, set[int]] = {}
    for days in days_by_report.values():
        for d in days:
            out.setdefault(d, set()).add(ct_ns(d, RELEASE_CT))
    for d in rule_days:
        out.setdefault(d, set()).add(ct_ns(d, RELEASE_CT))
    found["nopa_rule_dates"] = [d.isoformat() for d in rule_days]  # type: ignore[assignment]
    return {d: tuple(sorted(v)) for d, v in out.items()}, found


# ------------------------------------------------------------------ definitions ----
@lru_cache(maxsize=1)
def _outright_defs() -> np.ndarray:
    import data33  # noqa: PLC0415 - the loader needs its cache; imported on first use
    return data33.definitions(outright_only=True)


@lru_cache(maxsize=1)
def zm_tick() -> int:
    """ZM tick in 1e-9 price units, measure31.checked_tick over the outright definitions."""
    defs = m31.definition_rows(_outright_defs())
    tick = m31.checked_tick(defs, "ZM")
    if tick != 100_000_000:
        raise AssertionError(f"ZM tick {tick} differs from 0.10 USD/short ton")
    return int(tick)


def limit_prices(day: date, iid: int, cutoff_ns: int | None = None
                 ) -> tuple[tuple[int, int] | None, str]:
    """P3.6 rule 5: (HL, LL) in ticks of the front's last definition record with
    ts_recv <= 08:30 CT on D (records in ts_recv order across files and dates). Returns None
    with the reason for the skip case. ``cutoff_ns`` truncates the definitions (LT1).
    READING LB-15: implemented literally; the Z4 limit fields change weekly (Sundays) only."""
    arr = _outright_defs()
    asof_ns = ct_ns(day, LIMIT_ASOF)
    if cutoff_ns is not None:
        asof_ns = min(asof_ns, int(cutoff_ns))
    ts = arr["ts_recv"].astype(np.int64)
    if len(ts) > 1 and bool(np.any(np.diff(ts) < 0)):
        raise AssertionError("definitions not in ts_recv order")
    upto = int(np.searchsorted(ts, asof_ns, side="right"))
    mine = np.flatnonzero(arr["instrument_id"][:upto] == np.uint32(iid))
    if not len(mine):
        return None, "no_definition_record"
    rec = arr[int(mine[-1])]
    hl, ll = int(rec["high_limit_price"]), int(rec["low_limit_price"])
    undef = int(np.iinfo(np.int64).max)
    if hl in (undef, 0) or ll in (undef, 0):
        return None, "undefined_limit_field"
    tick = zm_tick()
    if hl % tick or ll % tick:
        raise AssertionError(f"{day}: limit prices are not tick multiples")
    return (hl // tick, ll // tick), ""
