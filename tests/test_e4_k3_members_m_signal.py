"""Stage E.4 Part 3, K3-mehedge-01's signal table (MemberCoder-A): the pin of
strategy/members/k3/_mehedge_signal.py against the saved Nikkei files
(reports/stage_e4c_member_specs.md section 6 and section 11; K3-L-07; catalog
reports/stage_e0_catalog_K3.md lines 590-597).

The table is recomputed here by code independent of the generator
(reports/stage_e4_briefs/gen_k3_mehedge.py): the saved files are parsed with a regular expression,
their sha256s checked against reports/stage_e4c_release_check.json, the overlaps checked to agree,
ME(m) taken from EC-CAL FX and the Tokyo business days from the release check's EC-JP holidays.
The generator's own missing-close branch is exercised by loading it from its path. No bar data is
read.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import re
from datetime import date, timedelta
from decimal import Context, Decimal
from functools import cache
from pathlib import Path
from types import ModuleType

import pytest

from data.group_session import load_group_calendar, trade_dates_between
from screening.stage_e_freeze import check_member_source
from strategy.members.k3 import _mehedge_signal as sig

REPO = Path(__file__).resolve().parents[1]
CHECK = REPO / "reports" / "stage_e4c_release_check.json"
GENERATOR = REPO / "reports" / "stage_e4_briefs" / "gen_k3_mehedge.py"
ROW = re.compile(r'^"(\d{4})/(\d{2})/(\d{2})","(\d+\.\d+)"')
LN = Context(prec=34)


@cache
def release_check() -> dict:
    return json.loads(CHECK.read_text(encoding="utf-8"))


@cache
def saved_closes() -> dict[date, tuple[Decimal, frozenset[str]]]:
    """Every saved close with the set of files holding it; overlapping files must agree."""
    n225 = release_check()["index"]["N225"]
    out: dict[date, tuple[Decimal, frozenset[str]]] = {}
    for rel in n225["saved_path"]:
        raw = (REPO / rel).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == n225["sha256"][rel], rel
        for line in raw.decode("latin-1").splitlines():
            match = ROW.match(line)
            if match is None:
                continue
            y, m, d, close = match.groups()
            day, value = date(int(y), int(m), int(d)), Decimal(close)
            if day in out:
                assert out[day][0] == value, (day, rel)
                out[day] = (value, out[day][1] | {Path(rel).name})
            else:
                out[day] = (value, frozenset({Path(rel).name}))
    return out


@cache
def business_days() -> tuple[date, ...]:
    holidays = {date.fromisoformat(h["date"]) for h in release_check()["ec_jp_holidays"]}
    day, out = date(2019, 1, 1), []
    while day <= date(2026, 12, 31):
        closed = (day.month, day.day) in {(12, 31), (1, 1), (1, 2), (1, 3)}
        if day.weekday() < 5 and day not in holidays and not closed:
            out.append(day)
        day += timedelta(days=1)
    return tuple(out)


@cache
def month_ends() -> tuple[tuple[str, date], ...]:
    cal = load_group_calendar("fx")
    first, last = cal.coverage
    last_of: dict[tuple[int, int], date] = {}
    for day in trade_dates_between(cal, first, last):
        last_of[(day.year, day.month)] = max(day, last_of.get((day.year, day.month), day))
    out = []
    for (y, m), me in sorted(last_of.items()):
        month_last = date(y + m // 12, m % 12 + 1, 1) - timedelta(days=1)
        if date(y, m, 1) >= first and month_last <= last:
            out.append((f"{y:04d}-{m:02d}", me))
    return tuple(out)


def recompute(closes: dict[date, Decimal], month: str, me: date) -> float | None:
    y, m = (int(x) for x in month.split("-"))
    prev = (y, m - 1) if m > 1 else (y - 1, 12)
    pa_day = [b for b in business_days() if b < me][-1]
    pb_day = [b for b in business_days() if (b.year, b.month) == prev][-1]
    if pa_day not in closes or pb_day not in closes:
        return None
    return float((closes[pa_day] / closes[pb_day]).ln(LN))


def plain_closes() -> dict[date, Decimal]:
    return {d: v for d, (v, _) in saved_closes().items()}


def generator() -> ModuleType:
    spec = importlib.util.spec_from_file_location("gen_k3_mehedge", GENERATOR)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# ------------------------------------------------------------------------------ pins ----
def test_the_signal_module_passes_the_freeze_static_check() -> None:
    rel = "strategy/members/k3/_mehedge_signal.py"
    assert check_member_source(rel, (REPO / rel).read_text(encoding="utf-8"), "K3") == []


def test_the_saved_files_are_the_release_checks_files() -> None:
    n225 = release_check()["index"]["N225"]
    assert n225["obtained"] is True and n225["overlap_conflicts"] == []
    assert dict(sig.MEHEDGE_SOURCE_SHA256) == n225["sha256"]
    assert hashlib.sha256(CHECK.read_bytes()).hexdigest() == sig.MEHEDGE_RELEASE_CHECK_SHA256
    for rel, sha in sig.MEHEDGE_SOURCE_SHA256:
        assert hashlib.sha256((REPO / rel).read_bytes()).hexdigest() == sha


def test_the_saved_closes_are_exactly_the_tokyo_business_days_of_the_check_window() -> None:
    window = {d for d in saved_closes() if date(2019, 4, 1) <= d <= date(2026, 6, 19)}
    expected = {b for b in business_days() if date(2019, 4, 1) <= b <= date(2026, 6, 19)}
    assert window == expected and len(window) == 1761  # the release check's n


def test_the_months_are_ec_cal_fx_month_ends_inside_the_coverage() -> None:
    rows = sig.MEHEDGE_R_EQ_6J
    assert [(m, date.fromisoformat(me)) for m, me, _ in rows] == list(month_ends())
    assert (len(rows), rows[0][0], rows[-1][0]) == (85, "2019-05", "2026-05")
    in_check = [(r["month"], r["me_date"]) for r in release_check()["month_ends"]
                if r["in_ec_cal_coverage"]]
    assert [(m, me) for m, me, _ in rows] == in_check


def test_the_table_is_recomputed_from_the_saved_files() -> None:
    closes = plain_closes()
    for month, me, r_eq in sig.MEHEDGE_R_EQ_6J:
        assert recompute(closes, month, date.fromisoformat(me)) == r_eq, month
    assert all(r is not None and r != 0 for _, _, r in sig.MEHEDGE_R_EQ_6J)  # 0 None, 0 zero


def test_the_closes_used_are_listed_with_a_file_that_holds_them() -> None:
    closes = saved_closes()
    assert [row[0] for row in sig.MEHEDGE_CLOSES_6J] == [m for m, _, _ in sig.MEHEDGE_R_EQ_6J]
    for (month, pa_day, pa, pa_file, pb_day, pb, pb_file), (_, _, r_eq) in zip(
            sig.MEHEDGE_CLOSES_6J, sig.MEHEDGE_R_EQ_6J, strict=True):
        for day, value, name in ((pa_day, pa, pa_file), (pb_day, pb, pb_file)):
            held, files = closes[date.fromisoformat(day)]
            assert held == Decimal(value) and name in files, (month, day)
        assert float((Decimal(pa) / Decimal(pb)).ln(LN)) == r_eq


def test_no_close_on_or_after_the_month_end_enters_the_table() -> None:
    """P_a is on a Tokyo date strictly before ME(m)'s calendar date (the Tokyo close of ME's own
    date label is excluded, C line 594) and P_b in month m-1; replacing every close dated on or
    after ME(m) by garbage leaves each month's value unchanged."""
    closes = plain_closes()
    for (month, me, r_eq), audit in zip(sig.MEHEDGE_R_EQ_6J, sig.MEHEDGE_CLOSES_6J, strict=True):
        me_day = date.fromisoformat(me)
        pa_day, pb_day = date.fromisoformat(audit[1]), date.fromisoformat(audit[4])
        assert pa_day < me_day and pb_day < date(me_day.year, me_day.month, 1)
        assert pa_day == max(d for d in closes if d < me_day)  # the last close before ME
        assert (pb_day.year * 12 + pb_day.month) == me_day.year * 12 + me_day.month - 1
        poisoned = {d: (v if d < me_day else v * 3 + 1) for d, v in closes.items()}
        assert recompute(poisoned, month, me_day) == r_eq, month


def test_spot_rows_by_hand() -> None:
    table = {m: (me, r) for m, me, r in sig.MEHEDGE_R_EQ_6J}
    audit = {row[0]: row for row in sig.MEHEDGE_CLOSES_6J}
    # 2025-11 (ME 11-28, the halted month-end): P_a 11-27 50167.10, P_b 10-31 52411.34
    assert audit["2025-11"][1:3] == ("2025-11-27", "50167.10")
    assert audit["2025-11"][4:6] == ("2025-10-31", "52411.34")
    assert table["2025-11"][1] < 0  # the Nikkei fell: R_eq < 0
    # 2019-05: P_b is 2019-04-26, the last Tokyo day before the 2019 Golden Week closure
    assert audit["2019-05"][4] == "2019-04-26"
    # P_b of 2026-01 and 2020-01 are FRED's spot-checked closes (release check)
    fred = {r["date"]: r["fred"] for r in release_check()["index"]["N225"]["fred_spot_check"]}
    assert Decimal(audit["2026-01"][5]) == Decimal(str(fred["2025-12-30"]))
    assert Decimal(audit["2020-01"][5]) == Decimal(str(fred["2019-12-30"]))


def test_there_is_no_6e_table() -> None:
    names = [n for n in dir(sig) if not n.startswith("_")]
    assert not any("6E" in n or "SX5E" in n or "STOXX" in n for n in names)


# ----------------------------------------------- the generator's missing-close branch ----
@pytest.mark.parametrize("drop", ["pa", "pb", "both"])
def test_a_missing_close_gives_none_in_the_generator_and_here(drop: str) -> None:
    gen = generator()
    closes = plain_closes()
    month, me = "2025-09", date(2025, 9, 30)
    r_full, pa_day, pb_day = gen.r_eq_row(month, me, closes, list(business_days()))
    assert r_full == dict((m, r) for m, _, r in sig.MEHEDGE_R_EQ_6J)[month]
    gone = {"pa": {pa_day}, "pb": {pb_day}, "both": {pa_day, pb_day}}[drop]
    holed = {d: v for d, v in closes.items() if d not in gone}
    r_gen, pa2, pb2 = gen.r_eq_row(month, me, holed, list(business_days()))
    assert r_gen is None and (pa2, pb2) == (pa_day, pb_day)  # never an earlier close instead
    assert recompute(holed, month, me) is None


def test_the_generator_rebuilds_the_written_table() -> None:
    rows, audit, shas, check_sha = generator().build()
    assert tuple(rows) == sig.MEHEDGE_R_EQ_6J
    assert tuple(audit) == sig.MEHEDGE_CLOSES_6J
    assert tuple(shas.items()) == sig.MEHEDGE_SOURCE_SHA256
    assert check_sha == sig.MEHEDGE_RELEASE_CHECK_SHA256
