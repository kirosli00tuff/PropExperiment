"""Release tables for the trigger extraction (lead_spec section 6; TriggerCoder brief item 3).

A frozen Stage E member that trades on scheduled releases reads a table generated from the frozen
release calendar reports/stage_e2b_release_calendar.json, which starts on 2019-05-01. For W_ext
(2011-07..2019-04) the same table is rebuilt from the program's sourced 2010-2019 rows, never from
the web, keeping only the rows that match the member's frozen definition:

- FOMC statement dates (K2-fomcpost-01, K2-predrift-01, K5-fomc-01; E.3-L-15): the FOMC rows
  whose instant is 13:00 America/Chicago on the row's date. Source before 2019-05-01:
  reports/stage_e14_cal_releases.json (FOMC rows 2010-06..2019-05). Statements at 12:30 ET or
  14:15 ET (2010-2012) are not trigger dates; they are counted by their CT clock time.
- Treasury auctions (K2-aucpre-01, K2-aucpost-01; L-14): every TREASURY_AUCTION row of tenor 2Y,
  5Y, 10Y or 30Y as (date, tenor, T_a), T_a = the row's instant in America/Chicago "HH:MM".
  Source before 2019-05-01: reports/stage_e16_calendars/ec_auc_2010_2019.json, built in the
  frozen file's row format (same keys, tenor from original_security_term, E.0's C9 filter).
  K2's DROPPED_AUCTIONS is empty, so nothing is dropped.

The same filters applied to the frozen calendar reproduce the frozen member tables exactly
(tests/test_trigger_hold_events_tables.py), which is the check that the filter is the member's.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from data.config import REPO_ROOT

CT = ZoneInfo("America/Chicago")
FROZEN_CALENDAR_PATH = Path("reports/stage_e2b_release_calendar.json")
HIST_RELEASES_PATH = Path("reports/stage_e14_cal_releases.json")  # FOMC, NGS, WPSR 2010-2019
HIST_AUCTIONS_PATH = Path("reports/stage_e16_calendars/ec_auc_2010_2019.json")
FROZEN_FIRST = date(2019, 5, 1)  # the frozen calendar's first date; hist rows stop before it
FOMC_RELEASE = "FOMC"
AUCTION_RELEASE = "TREASURY_AUCTION"
FOMC_STATEMENT_CT = "13:00"  # E.3-L-15: the frozen tables keep the FOMC rows at 13:00 CT
AUCTION_TENORS = ("2Y", "5Y", "10Y", "30Y")  # K2 _releases: TREASURY_AUCTIONS tenors


class TableError(RuntimeError):
    """A release table input is missing or malformed (refused, never repaired)."""


@dataclass(frozen=True)
class SourcedRows:
    path: str
    sha256: str
    rows: tuple[Mapping[str, Any], ...]


@dataclass(frozen=True)
class Table:
    """A member table rebuilt from sourced rows, with what the definition left out."""

    kind: str  # "fomc_statement_dates" | "treasury_auctions"
    rows: tuple  # the member's own format: dates as "YYYY-MM-DD", or (date, tenor, "HH:MM")
    counts: Mapping[str, int]
    sources: Mapping[str, Mapping[str, str]]  # role -> {path, sha256}


def read_rows(path: Path, root: Path = REPO_ROOT) -> SourcedRows:
    full = Path(root) / path
    if not full.is_file():
        raise TableError(f"{path} does not exist")
    raw = full.read_bytes()
    body = json.loads(raw)
    rows = body.get("releases") if isinstance(body, dict) else None
    if not isinstance(rows, list):
        raise TableError(f"{path}: no 'releases' rows")
    return SourcedRows(str(path), hashlib.sha256(raw).hexdigest(), tuple(rows))


def ct_clock(instant_utc: str) -> tuple[date, str]:
    """(CT calendar date, CT "HH:MM") of a UTC instant text."""
    dt = datetime.fromisoformat(str(instant_utc).replace("Z", "+00:00"))
    if dt.tzinfo is None:
        raise TableError(f"instant {instant_utc!r} is not timezone-aware")
    local = dt.astimezone(UTC).astimezone(CT)
    return local.date(), f"{local.hour:02d}:{local.minute:02d}"


def _in_range(row: Mapping[str, Any], first: date | None, last: date | None) -> bool:
    day = date.fromisoformat(str(row["date"]))
    return (first is None or day >= first) and (last is None or day <= last)


def fomc_statement_dates(rows: Iterable[Mapping[str, Any]], first: date | None = None,
                         last: date | None = None) -> tuple[tuple[str, ...], dict[str, int]]:
    """The FOMC rows whose instant is 13:00 CT on the row's own date (E.3-L-15)."""
    kept: list[str] = []
    counts: Counter[str] = Counter()
    for row in rows:
        if row.get("release") != FOMC_RELEASE or not _in_range(row, first, last):
            continue
        counts["fomc_rows"] += 1
        if not row.get("instant_utc"):
            counts["excluded:no_instant"] += 1
            continue
        local_day, clock = ct_clock(row["instant_utc"])
        if clock != FOMC_STATEMENT_CT or local_day.isoformat() != str(row["date"]):
            counts[f"excluded:statement_not_at_13:00_CT ({clock} CT)"] += 1
            continue
        kept.append(str(row["date"]))
    if len(set(kept)) != len(kept):
        raise TableError("two FOMC rows at 13:00 CT on one date")
    counts["kept"] = len(kept)
    return tuple(sorted(kept)), dict(counts)


def treasury_auctions(rows: Iterable[Mapping[str, Any]], first: date | None = None,
                      last: date | None = None
                      ) -> tuple[tuple[tuple[str, str, str], ...], dict[str, int]]:
    """(date, tenor, T_a CT) for every TREASURY_AUCTION row of tenor 2Y/5Y/10Y/30Y (L-14)."""
    kept: list[tuple[str, str, str]] = []
    counts: Counter[str] = Counter()
    for row in rows:
        if row.get("release") != AUCTION_RELEASE or not _in_range(row, first, last):
            continue
        counts["auction_rows"] += 1
        tenor = str(row.get("id", "")).rsplit("-", 1)[-1]
        if tenor not in AUCTION_TENORS:
            counts[f"excluded:tenor_{tenor}"] += 1
            continue
        if not row.get("instant_utc"):
            counts["excluded:no_instant"] += 1
            continue
        local_day, clock = ct_clock(row["instant_utc"])
        if local_day.isoformat() != str(row["date"]):
            counts["excluded:instant_not_on_row_date"] += 1
            continue
        kept.append((str(row["date"]), tenor, clock))
        counts[f"kept:{tenor}"] += 1
    return tuple(sorted(kept)), dict(counts)


def hist_fomc_table(first: date | None, last: date, root: Path = REPO_ROOT) -> Table:
    """FOMC 13:00 CT dates from the E.14 rows dated ``first``..``last``, before 2019-05-01."""
    src = read_rows(HIST_RELEASES_PATH, root)
    end = min(last, date.fromordinal(FROZEN_FIRST.toordinal() - 1))
    dates, counts = fomc_statement_dates(src.rows, first, end)
    return Table("fomc_statement_dates", dates, counts,
                 {"release_hist": {"path": src.path, "sha256": src.sha256}})


def hist_auction_table(first: date | None, last: date, root: Path = REPO_ROOT) -> Table:
    """Tenor-matched Treasury auctions from the E.16 rows dated ``first``..``last``, before
    2019-05-01."""
    src = read_rows(HIST_AUCTIONS_PATH, root)
    end = min(last, date.fromordinal(FROZEN_FIRST.toordinal() - 1))
    rows, counts = treasury_auctions(src.rows, first, end)
    return Table("treasury_auctions", rows, counts,
                 {"ecauc_hist": {"path": src.path, "sha256": src.sha256}})


TABLE_BUILDERS = {"fomc_statement_dates": hist_fomc_table,
                  "treasury_auctions": hist_auction_table}


def overlap_check(root: Path = REPO_ROOT) -> dict[str, Any]:
    """Where the sourced 2010-2019 files and the frozen calendar both have rows (2019-05-01 on),
    the same filter must give the same rows: a check of the sourced files, dates only."""
    frozen = read_rows(FROZEN_CALENDAR_PATH, root)
    out: dict[str, Any] = {}
    for kind, path, fn in (("fomc_statement_dates", HIST_RELEASES_PATH, fomc_statement_dates),
                           ("treasury_auctions", HIST_AUCTIONS_PATH, treasury_auctions)):
        hist = read_rows(path, root)
        days = [date.fromisoformat(str(r["date"])) for r in hist.rows]
        last = max(days)
        a, _ = fn(hist.rows, FROZEN_FIRST, last)
        b, _ = fn(frozen.rows, FROZEN_FIRST, last)
        out[kind] = {"range": [FROZEN_FIRST.isoformat(), last.isoformat()], "hist_rows": len(a),
                     "frozen_rows": len(b), "equal": tuple(a) == tuple(b),
                     "only_hist": [list(x) if isinstance(x, tuple) else x
                                   for x in sorted(set(a) - set(b))],
                     "only_frozen": [list(x) if isinstance(x, tuple) else x
                                     for x in sorted(set(b) - set(a))]}
    return out


__all__ = ["AUCTION_TENORS", "FOMC_STATEMENT_CT", "FROZEN_CALENDAR_PATH", "FROZEN_FIRST",
           "hist_month_end_table", "month_end_rows",
           "HIST_AUCTIONS_PATH", "HIST_RELEASES_PATH", "TABLE_BUILDERS", "SourcedRows", "Table",
           "TableError", "ct_clock", "fomc_statement_dates", "hist_auction_table",
           "hist_fomc_table", "overlap_check", "read_rows", "treasury_auctions"]


# ------------------------------------------------------------------ month end (K2 monthend) ----
def month_end_rows(calendar: Any, first: date, last: date) -> tuple[tuple[str, str, str], ...]:
    """reports/stage_e3_briefs/gen_k2_month_end.py month_end_rows()'s rule on ``calendar``:
    (YYYY-MM, N-1, N) for every month whose N (the month's last trade date) lies in first..last
    and is covered; N-1 = the calendar's trade date before N."""
    from datetime import timedelta

    from data.group_session import previous_trade_date, trade_dates_between

    rows = []
    year, month = first.year, first.month
    while date(year, month, 1) <= last:
        start = date(year, month, 1)
        nxt = date(year + (month == 12), month % 12 + 1, 1)
        days = trade_dates_between(calendar, start, nxt - timedelta(days=1))
        if days and calendar.covers(days[-1]) and first <= days[-1] <= last:
            n = days[-1]
            n1 = previous_trade_date(calendar, n)
            if n1 is None or not calendar.covers(n1):
                raise TableError(f"{n}: no covered previous trade date")
            rows.append((f"{year:04d}-{month:02d}", n1.isoformat(), n.isoformat()))
        year, month = nxt.year, nxt.month
    return tuple(rows)


def hist_month_end_table(first: date, last: date) -> Table:
    """N-1 and N on the hist rates calendar (data/calendars/hist2010/rates.json) before
    2019-05-01, months with N in first..last."""
    from base_rules.calendars import load_hist

    cal = load_hist("rates")
    end = min(last, date.fromordinal(FROZEN_FIRST.toordinal() - 1))
    rows = month_end_rows(cal, first, end)
    dates = tuple(sorted({d for _, a, b in rows for d in (a, b)}))
    return Table("month_end_dates", dates, {"months": len(rows), "dates": len(dates)},
                 {"hist_calendar_rates": {"path": str(getattr(cal, "file_path", "")),
                                          "sha256": str(getattr(cal, "file_sha256", ""))}})


TABLE_BUILDERS["month_end_dates"] = hist_month_end_table
