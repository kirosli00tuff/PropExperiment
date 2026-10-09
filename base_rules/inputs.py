"""Loaders for the stage's non-bar inputs: Task 1's settlement table, the EC-AUC auction rows, the
release rows of the cost rule, and U2's window starts from E.12's quote record.

Every loader refuses (``InputError``) rather than guesses: a settlement table whose periods do
not tile 2010-06-07..2024-02-29 exactly, an unknown grade, a malformed minute, an auction row of
another release or an unknown tenor, a duplicate row id. Nothing here reads market data.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import date, time, timedelta
from pathlib import Path
from typing import Any

from base_rules import constants as K


class InputError(RuntimeError):
    """An input file is missing or malformed; nothing is computed from it."""


def sha256_file(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_json(path: Path) -> tuple[Any, str]:
    path = Path(path)
    if not path.is_file():
        raise InputError(f"{path} does not exist")
    raw = path.read_bytes()
    try:
        return json.loads(raw), hashlib.sha256(raw).hexdigest()
    except json.JSONDecodeError as exc:
        raise InputError(f"{path.name}: not JSON ({exc})") from exc


def _day(text: Any, where: str) -> date:
    try:
        return date.fromisoformat(str(text))
    except ValueError as exc:
        raise InputError(f"{where}: {text!r} is not a date") from exc


def _minute(text: Any, where: str) -> int | None:
    if text is None:  # not listed in the period (e.g. TN before 2016-01-11): no minute
        return None
    try:
        t = time.fromisoformat(str(text))
    except ValueError as exc:
        raise InputError(f"{where}: {text!r} is not HH:MM") from exc
    if t.second or t.microsecond:
        raise InputError(f"{where}: {text!r} is not on a minute")
    return t.hour * 60 + t.minute


# ------------------------------------------------------------------ settlement table ----
@dataclass(frozen=True)
class Period:
    first: date
    last: date
    minute: int | None  # CT minute of day; None: the product is not listed then
    grade: str
    lead_grade: str | None = None  # settle periods: the lead's grade, the one H1/H4 use
    first_of_week_minute: int | None = None  # day_open: O_p on the ISO week's first trade date


def _periods(rows: Any, key: str, where: str, first: date, last: date) -> tuple[Period, ...]:
    if not isinstance(rows, list) or not rows:
        raise InputError(f"{where}: {key} must be a non-empty list")
    out = []
    for i, row in enumerate(rows):
        here = f"{where} {key}[{i}]"
        if not isinstance(row, dict):
            raise InputError(f"{here}: not an object")
        grade = row.get("grade", "unsourced" if key != "day_open" else "calendar")
        lead = row.get("lead_grade")
        if key != "day_open":
            if grade not in K.SETTLEMENT_GRADES:
                raise InputError(f"{here}: grade {grade!r} is not one of {K.SETTLEMENT_GRADES}")
            if lead not in K.LEAD_GRADES:
                raise InputError(f"{here}: lead_grade {lead!r} is not one of {K.LEAD_GRADES}")
        out.append(Period(_day(row.get("from"), here), _day(row.get("to"), here),
                          _minute(row.get("minute_ct"), here), str(grade),
                          None if lead is None else str(lead),
                          _minute(row.get("first_business_day_of_week_minute_ct"), here)))
    out.sort(key=lambda p: p.first)
    if out[0].first != first or out[-1].last != last:
        raise InputError(f"{where} {key}: periods span {out[0].first}..{out[-1].last}, not "
                         f"{first}..{last}")
    for a, b in zip(out, out[1:], strict=False):
        if a.last < a.first or b.first != a.last + timedelta(days=1):
            raise InputError(f"{where} {key}: periods {a.first}..{a.last} and {b.first}.. leave a "
                             "gap or overlap (they must tile the window)")
    if out[-1].last < out[-1].first:
        raise InputError(f"{where} {key}: an empty period")
    return tuple(out)


def _lookup(periods: tuple[Period, ...], day: date) -> Period:
    for p in periods:
        if p.first <= day <= p.last:
            return p
    raise InputError(f"no period covers {day}")


@dataclass(frozen=True)
class SettlementTable:
    """S_p and O_p per product and trade date (lead_spec section 0)."""

    settle: Mapping[str, tuple[Period, ...]]
    day_open: Mapping[str, tuple[Period, ...]]
    sha256: str
    source: str
    provisional: bool = False

    def settle_at(self, product: str, day: date) -> Period:
        return _lookup(self.settle[product], day)

    def settle_minute(self, product: str, day: date) -> int | None:
        return self.settle_at(product, day).minute

    def listed(self, product: str, day: date) -> bool:
        """An S_p exists on ``day`` (null minute_ct: not listed, no unit of any test)."""
        return self.settle_at(product, day).minute is not None

    def sourced(self, product: str, day: date) -> bool:
        """The H1/H4 bar: the period's LEAD grade is secondary or better (never "grade")."""
        at = self.settle_at(product, day)
        return at.minute is not None and at.lead_grade in K.SETTLEMENT_GRADES_OK

    def open_minute(self, product: str, day: date, first_of_week: bool = False) -> int | None:
        """O_p; ``first_of_week``: ``day`` is the first trade date of its ISO week on the
        product's group calendar (the period's first-business-day minute applies then)."""
        at = _lookup(self.day_open[product], day)
        if first_of_week and at.first_of_week_minute is not None:
            return at.first_of_week_minute
        return at.minute


def settlement_from_dict(raw: Any, sha256: str, source: str,
                         products: Iterable[str] = K.PRODUCTS) -> SettlementTable:
    if not isinstance(raw, dict) or raw.get("schema") != K.SETTLEMENT_SCHEMA:
        raise InputError(f"{source}: schema is not {K.SETTLEMENT_SCHEMA!r}")
    first, last = K.PROMPT_FIRST, K.WINDOW_LAST
    window = raw.get("window")
    if window != [str(first), str(last)]:
        raise InputError(f"{source}: window {window!r} is not [{first}, {last}]")
    table = raw.get("products")
    if not isinstance(table, dict):
        raise InputError(f"{source}: products must be an object")
    missing = [p for p in products if p not in table]
    if missing:
        raise InputError(f"{source}: no settlement rows for {missing}")
    settle, opens = {}, {}
    for p in products:
        where = f"{source} {p}"
        entry = table[p]
        if not isinstance(entry, dict) or entry.get("group") != K.GROUP_OF[p]:
            raise InputError(f"{where}: group is not {K.GROUP_OF[p]!r}")
        settle[p] = _periods(entry.get("settle"), "settle", where, first, last)
        opens[p] = _periods(entry.get("day_open"), "day_open", where, first, last)
    return SettlementTable(settle, opens, sha256, source)


def load_settlement(path: Path = K.SETTLEMENT_PATH) -> SettlementTable:
    raw, digest = read_json(K.repo_path(path))
    return settlement_from_dict(raw, digest, str(path))


def prior_settlement(day_open: Mapping[str, Mapping[date, int]] | None = None) -> SettlementTable:
    """PROVISIONAL: the lead's prior minutes (prompt) graded "secondary", O_p from ``day_open``
    (product -> {valid_from: minute}, the frozen calendars). Calendar-only counts only."""
    settle, opens = {}, {}
    for p in K.PRODUCTS:
        key = K.SUBGROUP.get(p, K.GROUP_OF[p])
        t = K.PRIOR_SETTLE_CT[key]
        settle[p] = (Period(K.PROMPT_FIRST, K.WINDOW_LAST, t.hour * 60 + t.minute, "secondary",
                            "secondary"),)
        rows = sorted((day_open or {}).get(p, {date(2010, 6, 1): 8 * 60 + 30}).items())
        periods = []
        for i, (start, minute) in enumerate(rows):
            end = rows[i + 1][0] - timedelta(days=1) if i + 1 < len(rows) else K.WINDOW_LAST
            periods.append(Period(max(start, K.PROMPT_FIRST), end, minute, "calendar"))
        opens[p] = tuple(x for x in periods if x.first <= x.last)
    return SettlementTable(settle, opens, "0" * 64, "provisional: lead prior", provisional=True)


# ------------------------------------------------------------------ window starts (U2) ----
def windows_from_dict(raw: Any, source: str) -> dict[str, date]:
    """reports/stage_e16_windows.json: product -> the date the window starts ON OR AFTER (the
    first trade date on or after it opens the window); every product, end 2024-02-29."""
    if not isinstance(raw, dict) or raw.get("schema") != K.WINDOWS_SCHEMA:
        raise InputError(f"{source}: schema is not {K.WINDOWS_SCHEMA!r}")
    if raw.get("fallback_window") != [str(K.FALLBACK_FIRST), str(K.WINDOW_LAST)]:
        raise InputError(f"{source}: fallback window is not {K.FALLBACK_FIRST}..{K.WINDOW_LAST}")
    out = {}
    for p in K.PRODUCTS:
        row = (raw.get("products") or {}).get(p)
        if not isinstance(row, dict) or row.get("window_end") != str(K.WINDOW_LAST):
            raise InputError(f"{source}: no window ending {K.WINDOW_LAST} for {p}")
        start = _day(row.get("window_start_on_or_after"), f"{source} {p}")
        if not K.PROMPT_FIRST.replace(day=1) <= start <= K.FALLBACK_FIRST:
            raise InputError(f"{source}: {p} starts {start}, outside 2010-06..2019-05-06")
        out[p] = max(start, K.PROMPT_FIRST)
    return out


def load_windows(path: Path = K.WINDOWS_PATH) -> dict[str, date]:
    raw, _ = read_json(K.repo_path(path))
    return windows_from_dict(raw, str(path))


def window_starts_from_quotes(path: Path = Path(K.QUOTE_RECORD),
                              trade_dates: Mapping[str, Iterable[date]] | None = None
                              ) -> dict[str, date]:
    """U2: the first trade date of the first priced month after each product's last unpriced
    gap before 2019-05 (``trade_dates``: product -> its calendar's trade dates; without them
    the month's first weekday is returned)."""
    raw, _ = read_json(K.repo_path(path))
    per = raw["sets"][K.QUOTE_SET]["per_contract"]
    out = {}
    for p in K.PRODUCTS:
        failed = [str(f).split("..")[0][:7] for f in per[p]["failed"]]
        failed = [m for m in failed if m < "2019-05"]
        month = date(2010, 1, 1) if not failed else date.fromisoformat(max(failed) + "-01")
        if failed:
            month = (month.replace(day=28) + timedelta(days=4)).replace(day=1)
        month = max(month, K.PROMPT_FIRST.replace(day=1))
        days = sorted(d for d in (trade_dates or {}).get(p, ()) if
                      (d.year, d.month) == (month.year, month.month)) if trade_dates else []
        if days:
            out[p] = days[0]
        else:
            d = month
            while d.weekday() >= 5:
                d += timedelta(days=1)
            out[p] = d
        out[p] = max(out[p], K.PROMPT_FIRST)
    return out


__all__ = ["InputError", "Period", "SettlementTable", "load_settlement", "load_windows",
           "prior_settlement", "read_json", "settlement_from_dict", "sha256_file",
           "window_starts_from_quotes", "windows_from_dict"]
