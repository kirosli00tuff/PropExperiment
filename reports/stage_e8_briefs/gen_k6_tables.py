"""One-off generator of the K6 literal tables (Stage E.8 Task 2, MemberCoder-B).

Not imported by any member. Run from the repository root:

    uv run python reports/stage_e8_briefs/gen_k6_tables.py

Sources (reports/stage_e8_member_specs.md S0.8, S0.11, K6-L-06, K6-L-07, K6-L-10, K6-L-11 and the
section 10 rulings R-1b-1, R-1b-2; K1-L-10, K3-L-11, K4-L-01 and K4-L-13 adopted):
- EC-CAL, the D10 grain and livestock calendars: data.group_session.load_group_calendar("grains"
  / "livestock") (data/calendars/grains.py, livestock.py, data/calendars/__init__.py), their
  is_trade_date, early_halt_ct and scheduled_late_opens, over 2019-05-01..2026-06-19;
- the engine's F: rules.sessions.flatten_time_ct(root, d) for ZC, ZW, ZS, ZM, ZL (grains) and HE,
  LE (livestock), asserted equal across the roots of a group on every trade date;
- the frozen release calendar reports/stage_e2b_release_calendar.json (sha256 asserted as the
  spec header states it): every row with release "WASDE";
- rules.price_limits: LIMITS (HE and LE HARD_DAILY periods) and SETTLEMENT_WINDOW_CT["livestock"];
- Task 1b's check reports/stage_e8_release_check.json (the verdicts behind R-1b-1 and R-1b-2).

Tables written:
- strategy/members/k6/_calendar.py: GRAIN_TRADE_DATES, LIVESTOCK_TRADE_DATES, GRAIN_FULL_SESSIONS,
  LIVESTOCK_FULL_SESSIONS (each as the trade dates less a literal list of the dates the S0.8 test
  removes, with the reason), LIVESTOCK_EARLY_HALT_CT and previous_trade_date;
- strategy/members/k6/_wasde.py: WASDE_DATES, DROPPED_WASDE (empty, R-1b-1), is_wasde_date;
- strategy/members/k6/_limits.py: LIMIT_PERIODS, SETTLEMENT_WINDOW_LIVESTOCK, DROPPED_LIMIT_DATES.

The research-window facts the spec header and section 10 state are asserted before anything is
written. tests/test_k6_members_tables.py recomputes every table from the sources by independent
code and asserts that each module is exactly this script's output.
"""

from __future__ import annotations

import hashlib
import json
import sys
import textwrap
from datetime import date, datetime, time
from pathlib import Path
from zoneinfo import ZoneInfo

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from data.group_session import load_group_calendar, trade_dates_between  # noqa: E402
from rules import price_limits as pl  # noqa: E402
from rules import sessions  # noqa: E402
from rules.products import product  # noqa: E402

OUT_CALENDAR = "strategy/members/k6/_calendar.py"
OUT_WASDE = "strategy/members/k6/_wasde.py"
OUT_LIMITS = "strategy/members/k6/_limits.py"
SESSIONS_FILE = "rules/sessions.py"
PRICE_LIMITS_FILE = "rules/price_limits.py"
RELEASE_CALENDAR = "reports/stage_e2b_release_calendar.json"
RELEASE_CALENDAR_SHA256 = "839f2437bedbeb7b3423d7058a9955a0d4ccd1aebc4b01c62be624ab11d7bcb8"
RELEASE_CHECK = "reports/stage_e8_release_check.json"
GROUP_ROOTS: dict[str, tuple[str, ...]] = {  # S0.1 / S0.11: every root of the group
    "grains": ("ZC", "ZW", "ZS", "ZM", "ZL"), "livestock": ("HE", "LE")}
REGULAR_F = {"grains": time(13, 18), "livestock": time(13, 3)}  # D6 rows (D lines 400-401)
CAL_FIRST, CAL_LAST = date(2019, 5, 1), date(2026, 6, 19)  # S0.8 / S0.11 (K4-L-13)
RESEARCH_FIRST, RESEARCH_LAST = date(2025, 4, 1), date(2026, 6, 19)
CT = ZoneInfo("America/Chicago")
# Spec header, EC-CAL (checked 00:15 PDT): the research-window full closures of both groups, the
# early halts, and the grain scheduled late opens (livestock has none).
SPEC_RESEARCH_CLOSURES = (
    "2025-04-18", "2025-05-26", "2025-06-19", "2025-07-04", "2025-09-01", "2025-11-27",
    "2025-12-25", "2026-01-01", "2026-01-19", "2026-02-16", "2026-04-03", "2026-05-25",
    "2026-06-19")
SPEC_RESEARCH_HALTS = {"grains": {"2025-11-28": "12:05", "2025-12-24": "12:05"},
                       "livestock": {"2025-11-28": "12:05", "2025-12-24": "12:15"}}
SPEC_RESEARCH_LATE_OPENS = {"grains": ("2025-11-28", "2025-12-26", "2026-01-02"),
                            "livestock": ()}
# Spec header and R-1b-1: the 14 research-window WASDE rows, each 12:00 America/New_York.
SPEC_RESEARCH_WASDE = (
    "2025-04-10", "2025-05-12", "2025-06-12", "2025-07-11", "2025-08-12", "2025-09-12",
    "2025-11-14", "2025-12-09", "2026-01-12", "2026-02-10", "2026-03-10", "2026-04-09",
    "2026-05-12", "2026-06-11")
WASDE_TIME_LOCAL, WASDE_TZ = "12:00", "America/New_York"
# S0.11: the initial limits of the research window in vendor ticks.
LIMIT_ROOTS = ("HE", "LE")
SPEC_LIMIT_TICKS = {("HE", "0.0400"): 160, ("HE", "0.0475"): 190, ("LE", "0.0650"): 260,
                    ("LE", "0.0725"): 290}
# R-1b-2 (spec section 10): LE trade dates 2026-06-01..2026-06-18 dropped for the member.
LE_DROP_FIRST, LE_DROP_LAST = date(2026, 6, 1), date(2026, 6, 18)
LE_DROP_COUNT = 14
LE_DROP_REASON = (
    "R-1b-2: CME SER-9736 (May 14, 2026) sets a new initial Live Cattle limit of $0.0850 "
    "effective trade date 2026-06-01; the frozen table (bracketed 2026-05-19..2026-06-19) "
    "holds $0.0725")
SATURDAY = 5
DATES_PER_LINE = 6
COMMENT_WIDTH = 96


# ------------------------------------------------------------------------ helpers ----
def sha256_of(rel: str) -> str:
    return hashlib.sha256((REPO_ROOT / rel).read_bytes()).hexdigest()


def in_research(iso: str) -> bool:
    return RESEARCH_FIRST.isoformat() <= iso <= RESEARCH_LAST.isoformat()


def wrap_comment(paragraphs: list[str]) -> str:
    return "\n".join("# " + line for text in paragraphs
                     for line in textwrap.wrap(text, COMMENT_WIDTH))


def render_isos(name: str, days: list[str], comment: str) -> str:
    lines = [f"# {comment} ({len(days)} dates)", f"{name}: tuple[str, ...] = ("]
    for i in range(0, len(days), DATES_PER_LINE):
        lines.append("    " + " ".join(f'"{d}",' for d in days[i:i + DATES_PER_LINE]))
    lines.append(")")
    return "\n".join(lines)


def render_pairs(name: str, pairs: list[tuple[str, str]], comment: str) -> str:
    body = "\n".join(f'    ("{a}", "{b}"),' for a, b in pairs)
    return (f"# {comment} ({len(pairs)} rows)\n"
            f"{name}: tuple[tuple[str, str], ...] = (\n{body}\n)")


def render_sources(name: str, pairs: list[tuple[str, str]]) -> str:
    body = "\n".join(f'    ("{p}",\n     "{s}"),' for p, s in pairs)
    return f"{name}: tuple[tuple[str, str], ...] = (\n{body}\n)"


def quoted(names: tuple[str, ...]) -> str:
    return "(" + ", ".join(f'"{n}"' for n in names) + ")"


def date_literal(d: date) -> str:
    return f"date({d.year}, {d.month}, {d.day})"


def weekdays(first: date, last: date) -> list[date]:
    return [date.fromordinal(n) for n in range(first.toordinal(), last.toordinal() + 1)
            if date.fromordinal(n).weekday() < SATURDAY]


# ----------------------------------------------------------------- the calendars ----
def group_tables(group: str) -> dict:
    """The group's trade dates, the dates the S0.8 test removes (date, reason), the dates where
    the early-halt test and the F test disagree, the early halts and the calendar module paths."""
    cal = load_group_calendar(group)
    roots = GROUP_ROOTS[group]
    assert cal.covers(CAL_FIRST) and cal.covers(CAL_LAST), cal.coverage
    assert all(product(r).group == group for r in roots)
    assert sessions.REGULAR_FLATTEN_CT[group] == REGULAR_F[group]
    trade: list[str] = []
    removed: list[tuple[str, str]] = []
    disagree: list[str] = []
    halts: list[tuple[str, str]] = []
    for d in trade_dates_between(cal, CAL_FIRST, CAL_LAST):
        flats = {r: sessions.flatten_time_ct(r, d) for r in roots}
        assert len(set(flats.values())) == 1, (group, d, flats)  # S0.11: one F per group
        f = flats[roots[0]]
        halt = cal.early_halt_ct(d)
        trade.append(d.isoformat())
        no_halt, regular_f = halt is None, f == REGULAR_F[group]
        halt_text = "none" if halt is None else f"{halt:%H:%M}"
        f_text = "none (no trading on CT date d)" if f is None else f"{f:%H:%M}"
        if halt is not None:
            halts.append((d.isoformat(), f"{halt:%H:%M}"))
        if not (no_halt and regular_f):
            removed.append((d.isoformat(), f"early halt {halt_text}; F {f_text}"))
        if no_halt != regular_f:
            disagree.append(f"{d.isoformat()} (early halt {halt_text}, F {f_text})")
    research_closed = [d.isoformat() for d in weekdays(RESEARCH_FIRST, RESEARCH_LAST)
                       if not cal.is_trade_date(d)]
    assert tuple(research_closed) == SPEC_RESEARCH_CLOSURES, (group, research_closed)
    research_halts = {d: h for d, h in halts if in_research(d)}
    assert research_halts == SPEC_RESEARCH_HALTS[group], (group, research_halts)
    late = sorted(d.isoformat() for d in cal.scheduled_late_opens if in_research(d.isoformat()))
    assert tuple(late) == SPEC_RESEARCH_LATE_OPENS[group], (group, late)
    return {"trade": trade, "removed": removed, "disagree": disagree, "halts": halts,
            "paths": sorted(cal.module_sha256()), "late_research": late}


CALENDAR_DOC = '''"""K6 calendar tables (literal; reports/stage_e8_member_specs.md S0.8,
S0.11, K6-L-04, K6-L-06, K6-L-09, K6-L-10; K1-L-10, K3-L-11 and K4-L-13 adopted).

GENERATED by reports/stage_e8_briefs/gen_k6_tables.py. Do not edit by hand:
tests/test_k6_members_tables.py recomputes every table from its sources and asserts this file is
the generator's output. Members read these tables; only the ISO text is turned into dates here.

- GRAIN_TRADE_DATES, LIVESTOCK_TRADE_DATES: every EC-CAL trade date of the group
  (data.group_session.load_group_calendar("grains" / "livestock").is_trade_date: a weekday that is
  not a FULL_CLOSURE of data/calendars/grains.py or livestock.py) of 2019-05-01..2026-06-19,
  sorted. An early-halt date is a trade date. crushgap's d-1 and limitcont's d-1, d-2, d-3 are
  the entries immediately before d (K6-L-04, K6-L-09).
- GRAIN_FULL_SESSIONS, LIVESTOCK_FULL_SESSIONS (S0.8, K6-L-10): the trade dates with no early halt
  (early_halt_ct None) AND the regular engine F on CT date d (rules.sessions.flatten_time_ct:
  13:18 CT for ZC, ZW, ZS, ZM and ZL; 13:03 CT for HE and LE; equal for every root of the group
  on every date). Written as the trade dates less *_NOT_FULL, the literal list of the dates the
  test removes, each with its early halt and F. A grain late open (no evening session) is not
  an early close.
- LIVESTOCK_EARLY_HALT_CT: the livestock early-halt time of every early-halt trade date of the
  range, for K6-limitcont-01's settlement window (K6-L-06).
- previous_trade_date(dates, d): the latest element of the sorted ``dates`` before d, or None.
"""'''


def calendar_module(grains: dict, livestock: dict) -> str:
    paths = sorted(set(grains["paths"]) | set(livestock["paths"]))
    sources = [(p, sha256_of(p)) for p in paths] + [(SESSIONS_FILE, sha256_of(SESSIONS_FILE))]
    notes = []
    for name, tab in (("Grain", grains), ("Livestock", livestock)):
        listed = ", ".join(tab["disagree"])
        notes.append(f"{name}: dates where the early-halt test and the F test disagree: "
                     + (f"{listed}." if listed else "none; they remove the same trade dates."))
        research = [d for d, _ in tab["removed"] if in_research(d)]
        notes.append(f"{name}: trade dates the S0.8 test removes: {len(tab['removed'])} of "
                     f"{len(tab['trade'])}; in the research window 2025-04-01..2026-06-19: "
                     f"{', '.join(research) or 'none'}.")
    notes.append("Grain scheduled late opens in the research window (no evening session; not an "
                 "early close, so they stay full sessions when F is regular): "
                 f"{', '.join(grains['late_research'])}. Livestock has none.")
    notes.append("EC-CAL's own coverage is wider than the tables' range; the tables stop at the "
                 "spec's 2019-05-01..2026-06-19 (K4-L-13).")
    halts_body = "\n".join(f'    ("{d}", "{h}"),' for d, h in livestock["halts"])
    func = '''def previous_trade_date(dates: Sequence[date], d: date) -> date | None:
    """The latest element of ``dates`` (sorted ascending) before ``d``; None if there is none."""
    lo, hi = 0, len(dates)
    while lo < hi:
        mid = (lo + hi) // 2
        if dates[mid] < d:
            lo = mid + 1
        else:
            hi = mid
    return dates[lo - 1] if lo > 0 else None'''
    text = "\n\n".join([
        CALENDAR_DOC,
        "from __future__ import annotations\n\n"
        "from collections.abc import Sequence\nfrom datetime import date, time",
        "# sha256 of each source file when the tables were generated\n"
        + render_sources("SOURCE_SHA256", sources),
        f'TABLE_RANGE = ("{CAL_FIRST.isoformat()}", "{CAL_LAST.isoformat()}")\n'
        "# the roots whose engine F was checked equal on every date of the group\n"
        f"GRAIN_F_ROOTS = {quoted(GROUP_ROOTS['grains'])}\n"
        f"LIVESTOCK_F_ROOTS = {quoted(GROUP_ROOTS['livestock'])}\n"
        f'GRAIN_REGULAR_F_CT = "{REGULAR_F["grains"]:%H:%M}"\n'
        f'LIVESTOCK_REGULAR_F_CT = "{REGULAR_F["livestock"]:%H:%M}"',
        wrap_comment(notes),
        render_isos("_GRAIN_TRADE_ISO", grains["trade"], "ISO grain trade dates, oldest first"),
        render_pairs("GRAIN_NOT_FULL", grains["removed"],
                     "grain trade dates that are not full sessions: (ISO date, reason)"),
        render_isos("_LIVESTOCK_TRADE_ISO", livestock["trade"],
                    "ISO livestock trade dates, oldest first"),
        render_pairs("LIVESTOCK_NOT_FULL", livestock["removed"],
                     "livestock trade dates that are not full sessions: (ISO date, reason)"),
        f"# livestock early halts: (ISO trade date, halt CT) ({len(livestock['halts'])} rows)\n"
        f"_LIVESTOCK_HALT_ISO: tuple[tuple[str, str], ...] = (\n{halts_body}\n)",
        "GRAIN_TRADE_DATES: tuple[date, ...] = tuple(date.fromisoformat(s) for s in "
        "_GRAIN_TRADE_ISO)\n"
        "LIVESTOCK_TRADE_DATES: tuple[date, ...] = tuple(date.fromisoformat(s)\n"
        "                                               for s in _LIVESTOCK_TRADE_ISO)\n"
        "GRAIN_FULL_SESSIONS: frozenset[date] = frozenset(GRAIN_TRADE_DATES) - frozenset(\n"
        "    date.fromisoformat(s) for s, _ in GRAIN_NOT_FULL)\n"
        "LIVESTOCK_FULL_SESSIONS: frozenset[date] = frozenset(LIVESTOCK_TRADE_DATES) - frozenset(\n"
        "    date.fromisoformat(s) for s, _ in LIVESTOCK_NOT_FULL)\n"
        "LIVESTOCK_EARLY_HALT_CT: dict[date, time] = {\n"
        "    date.fromisoformat(d): time.fromisoformat(t) for d, t in _LIVESTOCK_HALT_ISO}",
        "\n" + func + "\n",
        '__all__ = [\n    "GRAIN_FULL_SESSIONS", "GRAIN_NOT_FULL", "GRAIN_TRADE_DATES",\n'
        '    "LIVESTOCK_EARLY_HALT_CT", "LIVESTOCK_FULL_SESSIONS", "LIVESTOCK_NOT_FULL",\n'
        '    "LIVESTOCK_TRADE_DATES", "previous_trade_date",\n]',
    ]) + "\n"
    return text


# ----------------------------------------------------------------------- WASDE ----
def load_json(rel: str) -> dict:
    return json.loads((REPO_ROOT / rel).read_text(encoding="utf-8"))


def wasde_rows() -> tuple[list[str], list[str]]:
    """(the CT dates of the calendar's WASDE rows at 12:00 America/New_York in the range, the
    rows at another time, which are left out and listed: E.3-L-15)."""
    assert sha256_of(RELEASE_CALENDAR) == RELEASE_CALENDAR_SHA256, "not the frozen calendar"
    kept: list[str] = []
    other: list[str] = []
    for r in load_json(RELEASE_CALENDAR)["releases"]:
        if r["release"] != "WASDE":
            continue
        local = datetime.fromisoformat(r["instant_utc"].replace("Z", "+00:00")).astimezone(CT)
        day = local.date()
        if not CAL_FIRST <= day <= CAL_LAST:
            continue
        assert day.isoformat() == r["date"], r["id"]
        if r["time_local"] == WASDE_TIME_LOCAL and r["tz"] == WASDE_TZ:
            kept.append(day.isoformat())
        else:
            other.append(f"{r['id']} ({r['time_local']} {r['tz']})")
    assert kept == sorted(set(kept)), "WASDE rows unsorted or doubled"
    research = tuple(d for d in kept if in_research(d))
    assert research == SPEC_RESEARCH_WASDE, research
    check = load_json(RELEASE_CHECK)["A"]
    verdicts = {r["date"]: r["verdict"] for r in check["rows"]}
    assert tuple(sorted(verdicts)) == SPEC_RESEARCH_WASDE and set(verdicts.values()) == {"keep"}
    assert "2025-10-09" not in kept and "2025-11-10" not in kept and "2025-11-14" in kept
    return kept, other


WASDE_DOC = '''"""K6 EC-WASDE table (literal; reports/stage_e8_member_specs.md S0.11,
K6-L-11, section 10 ruling R-1b-1; E.3-L-15 and K4-L-01 adopted).

GENERATED by reports/stage_e8_briefs/gen_k6_tables.py from the frozen release calendar
reports/stage_e2b_release_calendar.json (sha256 below). Do not edit by hand:
tests/test_k6_members_tables.py recomputes the table from the calendar and asserts this file is
the generator's output.

WASDE_DATES: the CT dates (the row's instant_utc in America/Chicago) of every calendar row with
release "WASDE" at local time 12:00 America/New_York dated 2019-05-01..2026-06-19, less
DROPPED_WASDE. A row at another time would be left out, not re-timed, and listed (E.3-L-15).
The table spans both windows; Task 1b checked the 14 research-window rows (K4-L-01). The members
read the date only: T = 11:00 CT is fixed (C lines 72-74). is_wasde_date reads both tables at
call time.
"""'''


def wasde_module() -> str:
    kept, other = wasde_rows()
    check_sha = sha256_of(RELEASE_CHECK)
    notes = wrap_comment([
        "WASDE rows of the range at a time other than 12:00 America/New_York (left out): "
        f"{', '.join(other) or 'none'}.",
        f"Research-window rows (2025-04-01..2026-06-19): {len(SPEC_RESEARCH_WASDE)}, each "
        "verdict keep in Task 1b's check. The cancelled October 2025 WASDE (scheduled "
        "2025-10-09) has no row; the November 2025 WASDE moved from 2025-11-10 to 2025-11-14 by "
        "the NASS notice of 2025-10-31 and is kept (R-1b-1).",
    ])
    body = "\n".join(["# R-1b-1 (spec section 10, lead 00:32 PDT): all 14 research-window rows "
                      "kept; no row is",
                      "# dropped. ISO date -> reason for any dropped row.",
                      "DROPPED_WASDE: dict[date, str] = {}"])
    func = '''def is_wasde_date(d: date) -> bool:
    """d is an EC-WASDE date after C9a's drop rule (both tables read at call time)."""
    return d in WASDE_DATES and d not in DROPPED_WASDE'''
    text = "\n\n".join([
        WASDE_DOC,
        "from __future__ import annotations\n\nfrom datetime import date",
        "# sha256 of the sources when the table was generated\n"
        + render_sources("SOURCE_SHA256", [(RELEASE_CALENDAR, RELEASE_CALENDAR_SHA256),
                                           (RELEASE_CHECK, check_sha)]),
        f'WASDE_RANGE = ("{CAL_FIRST.isoformat()}", "{CAL_LAST.isoformat()}")\n'
        f'WASDE_RELEASE_TIME = ("{WASDE_TIME_LOCAL}", "{WASDE_TZ}")',
        notes,
        body,
        render_isos("_WASDE_ISO", kept, "ISO CT dates of the 12:00 ET WASDE rows, oldest first"),
        "WASDE_DATES: frozenset[date] = frozenset(\n"
        "    date.fromisoformat(s) for s in _WASDE_ISO) - frozenset(DROPPED_WASDE)",
        "\n" + func + "\n",
        '__all__ = ["DROPPED_WASDE", "WASDE_DATES", "is_wasde_date"]',
    ]) + "\n"
    return text


# ---------------------------------------------------------------------- limits ----
def limit_rows(root: str) -> list[tuple[date, date, str, str]]:
    """(first date, last date, amount as LIMITS writes it, status) of every HARD_DAILY period of
    the root intersecting the range."""
    rows = []
    p_root = product(root)
    for p in pl.LIMITS[root]:
        assert p.kind is pl.LimitKind.HARD_DAILY, (root, p)
        if p.end < CAL_FIRST or p.start > CAL_LAST:
            continue
        assert p.status in ("sourced", "bracketed", "carried"), (root, p)
        assert p.amount is not None
        ticks = p.amount * p_root.vendor_price_factor / p_root.vendor_tick
        assert ticks == int(ticks), (root, p.amount)  # S0.11: an integer number of vendor ticks
        spec = SPEC_LIMIT_TICKS.get((root, str(p.amount)))
        assert spec is None or spec == int(ticks), (root, p.amount, ticks)
        rows.append((p.start, p.end, str(p.amount), p.status))
    assert rows[0][0] <= CAL_FIRST and rows[-1][1] >= CAL_LAST, root
    for (_, end, _, _), (start, _, _, _) in zip(rows, rows[1:], strict=False):
        assert start.toordinal() == end.toordinal() + 1, (root, end, start)  # contiguous
    return rows


def dropped_le() -> list[date]:
    cal = load_group_calendar("livestock")
    days = trade_dates_between(cal, LE_DROP_FIRST, LE_DROP_LAST)
    assert len(days) == LE_DROP_COUNT, days
    b1 = load_json(RELEASE_CHECK)["B"]["B1_summary"]
    assert b1["differing_roots"] == ["LE"]
    assert b1["differing_dates"] == [d.isoformat() for d in days]
    for d in days:
        p = pl.limit_period("LE", d)
        assert (str(p.amount), p.status) == ("0.0725", "bracketed"), d
    return days


LIMITS_DOC = '''"""K6-limitcont-01's limit tables (literal;
reports/stage_e8_member_specs.md S0.11, section 5, K6-L-06, K6-L-07, K6-L-08 and section 10
rulings R-1b-2, R-1b-3).

GENERATED by reports/stage_e8_briefs/gen_k6_tables.py from rules.price_limits (LIMITS and
SETTLEMENT_WINDOW_CT; rules/price_limits.py sha256 below) and Task 1b's check. Do not edit by
hand: tests/test_k6_members_tables.py recomputes the tables and asserts this file is the
generator's output.

- LIMIT_PERIODS: root -> (first trade date, last trade date, initial daily limit in USD per pound
  as the exact decimal string LIMITS writes) for every HARD_DAILY period of HE and LE intersecting
  2019-05-01..2026-06-19; each period's status (sourced / bracketed / carried) is its comment.
  Only the initial limit is encoded (flag R-L2, K6-L-07). The member converts an amount to vendor
  ticks as amount x vendor_price_factor / vendor_tick, an integer for every period.
- SETTLEMENT_WINDOW_LIVESTOCK: rules.price_limits.SETTLEMENT_WINDOW_CT["livestock"], [start, end)
  CT, the D9.7 proxy window of a regular livestock day (K6-L-06).
- DROPPED_LIMIT_DATES: root -> {trade date: reason}; the member does not trade a d whose event
  test reads L on a dropped date (d-1 or d-2). R-1b-2: the 14 LE trade dates 2026-06-01..06-18.
  HE: none.
"""'''


def limits_module() -> str:
    window = pl.SETTLEMENT_WINDOW_CT["livestock"]
    assert (window.start_ct, window.end_ct) == (time(12, 59, 30), time(13, 0))
    lines = ["LIMIT_PERIODS: dict[str, tuple[tuple[date, date, str], ...]] = {"]
    for root in LIMIT_ROOTS:
        lines.append(f'    "{root}": (')
        for start, end, amount, status in limit_rows(root):
            lines.append(f'        ({date_literal(start)}, {date_literal(end)}, "{amount}"),'
                         f"  # {status}")
        lines.append("    ),")
    lines.append("}")
    drops = "\n".join(f"        {date_literal(d)}: _LE_DROP_REASON," for d in dropped_le())
    text = "\n\n".join([
        LIMITS_DOC,
        "from __future__ import annotations\n\nfrom datetime import date, time",
        "# sha256 of the sources when the tables were generated\n"
        + render_sources("SOURCE_SHA256", [(PRICE_LIMITS_FILE, sha256_of(PRICE_LIMITS_FILE)),
                                           (RELEASE_CHECK, sha256_of(RELEASE_CHECK))]),
        f'LIMIT_RANGE = ("{CAL_FIRST.isoformat()}", "{CAL_LAST.isoformat()}")',
        "\n".join(lines),
        "# rules.price_limits.SETTLEMENT_WINDOW_CT[\"livestock\"]: [start, end) CT\n"
        "SETTLEMENT_WINDOW_LIVESTOCK: tuple[time, time] = (time(12, 59, 30), time(13, 0))",
        "# R-1b-2 (spec section 10, lead 00:32 PDT; Task 1b B1/B2: the period LE 2026-05-19.."
        "2026-06-19\n# verdict drop)\n"
        + "_LE_DROP_REASON = (\n" + "\n".join(
            f'    "{part}"' for part in textwrap.wrap(LE_DROP_REASON, 84, drop_whitespace=False))
        + ")\n"
        "DROPPED_LIMIT_DATES: dict[str, dict[date, str]] = {\n"
        '    "HE": {},  # R-1b-2 / R-1b-3: no dropped HE date\n'
        '    "LE": {\n' + drops + "\n    },\n}",
        '__all__ = ["DROPPED_LIMIT_DATES", "LIMIT_PERIODS", "SETTLEMENT_WINDOW_LIVESTOCK"]',
    ]) + "\n"
    return text


def build() -> dict[str, str]:
    """{repository path: module text} of every generated module."""
    grains, livestock = group_tables("grains"), group_tables("livestock")
    return {OUT_CALENDAR: calendar_module(grains, livestock), OUT_WASDE: wasde_module(),
            OUT_LIMITS: limits_module()}


def main() -> None:
    for rel, text in build().items():
        (REPO_ROOT / rel).write_text(text, encoding="utf-8")
        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
        print(f"wrote {rel}: {text.count(chr(10))} lines, sha256 {digest[:12]}")


if __name__ == "__main__":
    main()
