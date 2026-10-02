"""One-off generator of the K8 literal tables (Stage E.9 Task 2, MemberCoder-A).

Not imported by any member. Run from the repository root:

    uv run python reports/stage_e9_briefs/gen_k8_tables.py

Sources (reports/stage_e9_member_specs.md S0.8, S0.10, S0.11, K8-L-03, K8-L-04, K8-L-08, K8-L-14
and the section 7 rulings R-1b-1, R-1b-3; K1-L-10, K3-L-11, K7-L-02 and K4-L-13 adopted):
- EC-CAL, the D10 group calendars: data.group_session.load_group_calendar(group) for "equity",
  "crypto", "metals", "energy" and "fx" (data/calendars/*.py, data/cme_calendar.py for equity),
  their is_trade_date, is_full_closure, booked_forward and early_halt_ct, over
  2019-05-01..2026-06-19;
- the engine's F: rules.sessions.flatten_time_ct(root, d) for the K8 roots of each group (equity
  MES and MNQ, crypto MBT, metals MGC, energy MCL, fx 6C), asserted equal across the roots of a
  group on every trade date;
- the frozen release calendar reports/stage_e2b_release_calendar.json (sha256 asserted as the spec
  header states it): every row dated 2019-05-01..2026-06-19 whose "products" include MGC, 6C or
  MNQ, with no correction (ruling R-1b-1).

Tables written:
- strategy/members/k8/_calendar.py: EQUITY_, CRYPTO_, METALS_, ENERGY_ and FX_FULL_SESSIONS
  (each the weekdays of the range less a literal list of the weekdays that are not full sessions,
  with the reason), FLIGHT_DATES, OILCAD_DATES, WKNDBTC_DATES and previous_dates;
- strategy/members/k8/_releases.py: GUARD_INSTANTS (from a literal row table) and in_guard.

The research-window facts the spec header and section 7 state are asserted before anything is
written. tests/test_k8_members_tables.py recomputes every table from the sources by independent
code and asserts that each module is exactly this script's output.
"""

from __future__ import annotations

import hashlib
import json
import sys
import textwrap
from collections import Counter
from datetime import date, datetime, time, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from data.group_session import load_group_calendar  # noqa: E402
from rules import sessions  # noqa: E402
from rules.products import product  # noqa: E402

OUT_CALENDAR = "strategy/members/k8/_calendar.py"
OUT_RELEASES = "strategy/members/k8/_releases.py"
SESSIONS_FILE = "rules/sessions.py"
RELEASE_CALENDAR = "reports/stage_e2b_release_calendar.json"
RELEASE_CALENDAR_SHA256 = "839f2437bedbeb7b3423d7058a9955a0d4ccd1aebc4b01c62be624ab11d7bcb8"
# S0.11 / K8-L-03: the K8 roots of each group, in the order the tables are written
GROUP_ROOTS: dict[str, tuple[str, ...]] = {
    "equity": ("MES", "MNQ"), "crypto": ("MBT",), "metals": ("MGC",), "energy": ("MCL",),
    "fx": ("6C",)}
TABLE_NAMES = {"equity": "EQUITY", "crypto": "CRYPTO", "metals": "METALS", "energy": "ENERGY",
               "fx": "FX"}
REGULAR_F = time(15, 8)  # D6 rows of all five groups (D lines 391-402)
CAL_FIRST, CAL_LAST = date(2019, 5, 1), date(2026, 6, 19)  # S0.11 / K8-L-14 (K4-L-13)
RESEARCH_FIRST, RESEARCH_LAST = date(2025, 4, 1), date(2026, 6, 19)
CT = ZoneInfo("America/Chicago")
SATURDAY, MONDAY = 5, 0
FRIDAY_BEFORE_MONDAY_DAYS = 3
# Section 7 (lead's count 22:32 PDT, the S0.8 definition): research-window full sessions
SPEC_RESEARCH_FULL = {"equity": 303, "crypto": 304, "metals": 304, "energy": 304, "fx": 304}
SPEC_RESEARCH_MEMBER = {"FLIGHT_DATES": 303, "OILCAD_DATES": 304, "WKNDBTC_DATES": 303}
SPEC_RESEARCH_WKNDBTC_MONDAYS = 54  # Mondays d with d and d - 3 both in WKNDBTC_DATES
# R-1b-3: a late open or delayed start is not an early close
CRYPTO_DELAYED_START_FULL = date(2026, 6, 1)
# Spec header (lead count 22:20 PDT; Task 1b A1): research-window rows per traded root
GUARD_ROOTS = ("MGC", "6C", "MNQ")
SPEC_RESEARCH_ROWS: dict[str, dict[tuple[str, str], int]] = {
    "MGC": {("NFP", "08:30"): 14, ("CPI", "08:30"): 14, ("G17", "09:15"): 14,
            ("FOMC", "14:00"): 10},
    "6C": {("WPSR", "10:30"): 56, ("WPSR", "12:00"): 7, ("WPSR", "17:00"): 1, ("NFP", "08:30"): 14,
           ("FOMC", "14:00"): 10},
    "MNQ": {("ISM_SERVICES", "10:00"): 15, ("NFP", "08:30"): 14, ("CPI", "08:30"): 14,
            ("FOMC", "14:00"): 10},
}
SPEC_TZ = "America/New_York"
# R-1b-1: the two WPSR rows E.4 dropped stay in GUARD_INSTANTS["6C"]
R1B1_KEPT_ROWS = ("WPSR-2025-12-29", "WPSR-2026-05-28")
GUARD_SECONDS = 120  # D9.5a: [R, R + 2 min)
DATES_PER_LINE = 6
COMMENT_WIDTH = 96


# ------------------------------------------------------------------------ helpers ----
def sha256_of(rel: str) -> str:
    return hashlib.sha256((REPO_ROOT / rel).read_bytes()).hexdigest()


def in_research(d: date) -> bool:
    return RESEARCH_FIRST <= d <= RESEARCH_LAST


def weekdays(first: date, last: date) -> list[date]:
    days = (first + timedelta(days=n) for n in range((last - first).days + 1))
    return [d for d in days if d.weekday() < SATURDAY]


def wrap_comment(paragraphs: list[str]) -> str:
    return "\n".join("# " + line for text in paragraphs
                     for line in textwrap.wrap(text, COMMENT_WIDTH))


def render_pairs(name: str, pairs: list[tuple[str, str]], comment: str) -> str:
    body = "\n".join(f'    ("{a}", "{b}"),' for a, b in pairs)
    return (f"# {comment} ({len(pairs)} rows)\n"
            f"{name}: tuple[tuple[str, str], ...] = (\n{body}\n)")


def render_sources(name: str, pairs: list[tuple[str, str]]) -> str:
    body = "\n".join(f'    ("{p}",\n     "{s}"),' for p, s in pairs)
    return f"{name}: tuple[tuple[str, str], ...] = (\n{body}\n)"


def quoted(names: tuple[str, ...]) -> str:
    inner = ", ".join(f'"{n}"' for n in names)
    return f"({inner},)" if len(names) == 1 else f"({inner})"


def hm(t: time | None) -> str:
    return "none" if t is None else f"{t:%H:%M}"


# ----------------------------------------------------------------- the calendars ----
def group_table(group: str) -> dict:
    """The group's full sessions, the weekdays of the range that are not (date, reason), the
    dates where the early-halt test and the F test disagree, and the calendar module paths."""
    cal = load_group_calendar(group)
    roots = GROUP_ROOTS[group]
    assert cal.covers(CAL_FIRST), (group, cal.coverage)
    assert all(product(r).group == group for r in roots), group
    assert sessions.REGULAR_FLATTEN_CT[group] == REGULAR_F, group
    full: list[date] = []
    not_full: list[tuple[str, str]] = []
    disagree: list[str] = []
    for d in weekdays(CAL_FIRST, CAL_LAST):
        if not cal.is_trade_date(d):
            if cal.is_full_closure(d):
                reason = "not a trade date: full closure"
            else:
                target = cal.booked_forward[d]  # the only other non-trade weekday
                reason = f"not a trade date: booked forward to {target.isoformat()}"
            not_full.append((d.isoformat(), reason))
            continue
        flats = {r: sessions.flatten_time_ct(r, d) for r in roots}
        assert len(set(flats.values())) == 1, (group, d, flats)  # S0.11: the roots agree
        f = flats[roots[0]]
        halt = cal.early_halt_ct(d)
        no_halt, regular_f = halt is None, f == REGULAR_F
        if no_halt and regular_f:
            full.append(d)
        else:
            not_full.append((d.isoformat(), f"early halt {hm(halt)}; F {hm(f)}"))
        if no_halt != regular_f:
            disagree.append(f"{d.isoformat()} (early halt {hm(halt)}, F {hm(f)})")
    research = sum(1 for d in full if in_research(d))
    assert research == SPEC_RESEARCH_FULL[group], (group, research)
    return {"full": full, "not_full": not_full, "disagree": disagree,
            "paths": sorted(cal.module_sha256())}


def member_dates(tables: dict[str, dict]) -> dict[str, list[date]]:
    sets = {g: set(t["full"]) for g, t in tables.items()}
    out = {"FLIGHT_DATES": sorted(sets["equity"] & sets["metals"]),
           "OILCAD_DATES": sorted(sets["energy"] & sets["fx"]),
           "WKNDBTC_DATES": sorted(sets["equity"] & sets["crypto"])}
    for name, days in out.items():
        research = sum(1 for d in days if in_research(d))
        assert research == SPEC_RESEARCH_MEMBER[name], (name, research)
    wk = set(out["WKNDBTC_DATES"])
    mondays = [d for d in wk if in_research(d) and d.weekday() == MONDAY
               and d - timedelta(days=FRIDAY_BEFORE_MONDAY_DAYS) in wk]
    assert len(mondays) == SPEC_RESEARCH_WKNDBTC_MONDAYS, len(mondays)
    assert CRYPTO_DELAYED_START_FULL in sets["crypto"], "R-1b-3"
    assert date(2025, 11, 28) not in out["FLIGHT_DATES"]  # an early halt (the brief's example)
    return out


CALENDAR_DOC = '''"""K8 calendar tables (literal; reports/stage_e9_member_specs.md S0.8,
S0.11, K8-L-03, K8-L-04, K8-L-14 and section 7 ruling R-1b-3; K1-L-10, K3-L-11, K7-L-02 and
K4-L-13 adopted).

GENERATED by reports/stage_e9_briefs/gen_k8_tables.py. Do not edit by hand:
tests/test_k8_members_tables.py recomputes every table from its sources and asserts this file is
the generator's output. Members read these tables; only the literal lists are turned into dates
here, at import.

- EQUITY_FULL_SESSIONS, CRYPTO_FULL_SESSIONS, METALS_FULL_SESSIONS, ENERGY_FULL_SESSIONS,
  FX_FULL_SESSIONS (S0.8, K8-L-03): the group's EC-CAL trade dates of 2019-05-01..2026-06-19
  (data.group_session.load_group_calendar(group).is_trade_date: a weekday that is not a full
  closure and not a booked-forward day) with no early halt (early_halt_ct None) AND the regular
  engine F of 15:08 CT on CT date d (rules.sessions.flatten_time_ct(root, d), equal for every K8
  root of the group on every date: equity MES and MNQ, crypto MBT, metals MGC, energy MCL, fx
  6C). Written as the weekdays of TABLE_RANGE less <GROUP>_NOT_FULL, the literal list of the
  weekdays the test removes, each with its reason. A late open or delayed start is not an early
  close (R-1b-3: 2026-06-01 is a crypto full session).
- FLIGHT_DATES = EQUITY & METALS, OILCAD_DATES = ENERGY & FX, WKNDBTC_DATES = EQUITY & CRYPTO:
  sorted tuples (S0.11).
- previous_dates(dates, d, k): the k most recent elements of the sorted ``dates`` strictly
  before d, oldest first (fewer at the table's start; K8-L-04's reference dates).
"""'''

PREVIOUS_DATES = '''def previous_dates(dates: Sequence[date], d: date, k: int) -> tuple[date, ...]:
    """The ``k`` most recent elements of ``dates`` (sorted ascending) strictly before ``d``,
    oldest first; fewer when the table holds fewer, none when ``k`` <= 0."""
    lo, hi = 0, len(dates)
    while lo < hi:
        mid = (lo + hi) // 2
        if dates[mid] < d:
            lo = mid + 1
        else:
            hi = mid
    return tuple(dates[max(0, lo - k):lo])  # k <= 0: an empty slice'''

FULL_FROM = '''def _weekdays(first: date, last: date) -> tuple[date, ...]:
    days = (first + timedelta(days=n) for n in range((last - first).days + 1))
    return tuple(d for d in days if d.weekday() < _SATURDAY)


_RANGE_WEEKDAYS: tuple[date, ...] = _weekdays(date.fromisoformat(TABLE_RANGE[0]),
                                              date.fromisoformat(TABLE_RANGE[1]))


def _full_sessions(not_full: tuple[tuple[str, str], ...]) -> frozenset[date]:
    removed = frozenset(date.fromisoformat(s) for s, _ in not_full)
    return frozenset(d for d in _RANGE_WEEKDAYS if d not in removed)
'''


def calendar_module(tables: dict[str, dict]) -> str:
    paths = sorted({p for t in tables.values() for p in t["paths"]})
    sources = [(p, sha256_of(p)) for p in paths] + [(SESSIONS_FILE, sha256_of(SESSIONS_FILE))]
    dates = member_dates(tables)
    notes = []
    for group, tab in tables.items():
        listed = ", ".join(tab["disagree"])
        removed_research = [s for s, _ in tab["not_full"] if in_research(date.fromisoformat(s))]
        notes.append(
            f"{group} ({', '.join(GROUP_ROOTS[group])}): {len(tab['full'])} full sessions; "
            f"{len(tab['not_full'])} weekdays removed; dates where the early-halt test and the F "
            "test disagree: " + (f"{listed}." if listed else "none.")
            + f" Research window 2025-04-01..2026-06-19: {sum(map(in_research, tab['full']))} "
            f"full sessions; weekdays removed: {', '.join(removed_research)}.")
    notes.append("Research-window member dates (section 7): "
                 + ", ".join(f"{n} {sum(map(in_research, d))}" for n, d in dates.items())
                 + f"; Mondays d with d and d - 3 both in WKNDBTC_DATES: "
                 f"{SPEC_RESEARCH_WKNDBTC_MONDAYS}.")
    notes.append("EC-CAL's own coverage may be wider than the tables' range; the tables stop at "
                 "the spec's 2019-05-01..2026-06-19 (K8-L-14, K4-L-13).")
    blocks = [CALENDAR_DOC,
              "from __future__ import annotations\n\n"
              "from collections.abc import Sequence\nfrom datetime import date, timedelta",
              "# sha256 of each source file when the tables were generated\n"
              + render_sources("SOURCE_SHA256", sources),
              f'TABLE_RANGE = ("{CAL_FIRST.isoformat()}", "{CAL_LAST.isoformat()}")\n'
              f'REGULAR_F_CT = "{REGULAR_F:%H:%M}"\n'
              "# the K8 roots whose engine F was checked equal on every date of the group\n"
              "GROUP_ROOTS: tuple[tuple[str, tuple[str, ...]], ...] = (\n"
              + "\n".join(f'    ("{g}", {quoted(r)}),' for g, r in GROUP_ROOTS.items())
              + "\n)\n_SATURDAY = 5",
              wrap_comment(notes)]
    for group, tab in tables.items():
        name = TABLE_NAMES[group]
        blocks.append(render_pairs(f"{name}_NOT_FULL", tab["not_full"],
                                   f"{group} weekdays that are not full sessions: (ISO date, "
                                   "reason)"))
    blocks.append(FULL_FROM)
    blocks.append("\n".join(
        f"{TABLE_NAMES[g]}_FULL_SESSIONS: frozenset[date] = _full_sessions({TABLE_NAMES[g]}"
        "_NOT_FULL)" for g in tables))
    blocks.append(
        "FLIGHT_DATES: tuple[date, ...] = tuple(sorted(EQUITY_FULL_SESSIONS & "
        "METALS_FULL_SESSIONS))\n"
        "OILCAD_DATES: tuple[date, ...] = tuple(sorted(ENERGY_FULL_SESSIONS & FX_FULL_SESSIONS))\n"
        "WKNDBTC_DATES: tuple[date, ...] = tuple(sorted(EQUITY_FULL_SESSIONS & "
        "CRYPTO_FULL_SESSIONS))")
    blocks.append("\n" + PREVIOUS_DATES + "\n")
    blocks.append(
        '__all__ = [\n    "CRYPTO_FULL_SESSIONS", "CRYPTO_NOT_FULL", "ENERGY_FULL_SESSIONS",\n'
        '    "ENERGY_NOT_FULL", "EQUITY_FULL_SESSIONS", "EQUITY_NOT_FULL", "FLIGHT_DATES",\n'
        '    "FX_FULL_SESSIONS", "FX_NOT_FULL", "GROUP_ROOTS", "METALS_FULL_SESSIONS",\n'
        '    "METALS_NOT_FULL", "OILCAD_DATES", "REGULAR_F_CT", "SOURCE_SHA256", "TABLE_RANGE",\n'
        '    "WKNDBTC_DATES", "previous_dates",\n]')
    return "\n\n".join(blocks) + "\n"


# ----------------------------------------------------------------- the releases ----
def load_json(rel: str) -> dict:
    return json.loads((REPO_ROOT / rel).read_text(encoding="utf-8"))


def instant_seconds(text: str) -> int:
    dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
    assert dt.tzinfo is not None and dt.microsecond == 0 and dt.second == 0, text
    return int(dt.timestamp())


def guard_rows() -> list[tuple[int, str, tuple[str, ...], str, str, date]]:
    """(UTC epoch seconds, row id, the guard roots among its products, CT clock, release, date) of
    every calendar row dated 2019-05-01..2026-06-19 whose products include MGC, 6C or MNQ, oldest
    first."""
    assert sha256_of(RELEASE_CALENDAR) == RELEASE_CALENDAR_SHA256, "not the frozen calendar"
    rows = []
    research: dict[str, Counter] = {r: Counter() for r in GUARD_ROOTS}
    for r in load_json(RELEASE_CALENDAR)["releases"]:
        roots = tuple(x for x in GUARD_ROOTS if x in r["products"])
        if not roots:
            continue
        day = date.fromisoformat(r["date"])
        if not CAL_FIRST <= day <= CAL_LAST:
            continue
        seconds = instant_seconds(r["instant_utc"])
        local = datetime.fromtimestamp(seconds, tz=CT)
        assert local.date() == day, r["id"]  # the row's date is its CT date
        rows.append((seconds, r["id"], roots, f"{local:%H:%M}", r["release"], day))
        if in_research(day):
            assert r["tz"] == SPEC_TZ, r["id"]
            for x in roots:
                research[x][(r["release"], r["time_local"])] += 1
    for x in GUARD_ROOTS:
        assert dict(research[x]) == SPEC_RESEARCH_ROWS[x], (x, dict(research[x]))
    ids = {row[1] for row in rows}
    assert set(R1B1_KEPT_ROWS) <= ids, "R-1b-1"
    rows.sort()
    return rows


RELEASES_DOC = '''"""K8 release-guard table (literal; reports/stage_e9_member_specs.md S0.10,
S0.11, K8-L-08, K8-L-14 and section 7 ruling R-1b-1; K3-L-01 and K4-L-01 adopted).

GENERATED by reports/stage_e9_briefs/gen_k8_tables.py from the frozen release calendar
reports/stage_e2b_release_calendar.json (RELEASE_CALENDAR_SHA256 below). Do not edit by hand:
tests/test_k8_members_tables.py recomputes the table from the calendar and asserts this file is
the generator's output.

- GUARD_ROWS: (UTC epoch seconds, row id, the guard roots among the row's "products") for every
  calendar row dated 2019-05-01..2026-06-19 whose "products" include MGC, 6C or MNQ, oldest
  first; the trailing comment is the instant's America/Chicago clock. The table spans both
  windows; Task 1b checked the research-window rows (K8-L-14). No correction (R-1b-1): the two
  WPSR rows E.4 dropped from K4's event members (WPSR-2025-12-29, WPSR-2026-05-28) stay in, as
  they stay in the engine's D9.5a set.
- GUARD_INSTANTS: root -> the sorted distinct instants (UTC epoch seconds) of the rows that name
  the root, for "MGC", "6C" and "MNQ": the engine's D9.5a set for the traded root (K8-L-08).
- in_guard(root, t_ns): True iff R <= t_ns / 1e9 < R + 120 for some R of GUARD_INSTANTS[root]
  (integer arithmetic on nanoseconds): C6's skip test on an entry's fill minute (S0.10).
"""'''

IN_GUARD = '''def in_guard(root: str, t_ns: int) -> bool:
    """True iff ``t_ns`` (UTC ns) lies in [R, R + 120 s) for an instant R of ``root``."""
    instants = GUARD_INSTANTS[root]
    lo, hi = 0, len(instants)
    while lo < hi:  # lo: the number of instants R with R <= t
        mid = (lo + hi) // 2
        if instants[mid] * NS_PER_S <= t_ns:
            lo = mid + 1
        else:
            hi = mid
    return lo > 0 and t_ns < (instants[lo - 1] + GUARD_SECONDS) * NS_PER_S'''


def releases_module() -> str:
    rows = guard_rows()
    counts = []
    for x in GUARD_ROOTS:
        mine = [r for r in rows if x in r[2]]
        by_release = Counter(row[4] for row in mine)
        research = sum(1 for row in mine if in_research(row[5]))
        counts.append(f"{x}: {len(mine)} rows ("
                      + ", ".join(f"{k} {v}" for k, v in sorted(by_release.items()))
                      + f"); research window 2025-04-01..2026-06-19: {research}.")
    body = "\n".join(f'    ({s}, "{i}", {quoted(roots)}),  # {clock} CT'
                     for s, i, roots, clock, _, _ in rows)
    blocks = [RELEASES_DOC,
              "from __future__ import annotations",
              f'RELEASE_CALENDAR = "{RELEASE_CALENDAR}"\n'
              f'RELEASE_CALENDAR_SHA256 = "{RELEASE_CALENDAR_SHA256}"\n'
              f'TABLE_RANGE = ("{CAL_FIRST.isoformat()}", "{CAL_LAST.isoformat()}")\n'
              f"GUARD_ROOTS = {quoted(GUARD_ROOTS)}\n"
              f"GUARD_SECONDS = {GUARD_SECONDS}  # D9.5a: [R, R + 2 min)\n"
              "NS_PER_S = 1_000_000_000",
              wrap_comment(counts),
              f"# (UTC epoch seconds, row id, guard roots) ({len(rows)} rows)\n"
              f"GUARD_ROWS: tuple[tuple[int, str, tuple[str, ...]], ...] = (\n{body}\n)",
              "GUARD_INSTANTS: dict[str, tuple[int, ...]] = {\n"
              "    root: tuple(sorted({s for s, _, roots in GUARD_ROWS if root in roots}))\n"
              "    for root in GUARD_ROOTS\n}",
              "\n" + IN_GUARD + "\n",
              '__all__ = [\n    "GUARD_INSTANTS", "GUARD_ROOTS", "GUARD_ROWS", "GUARD_SECONDS",'
              ' "NS_PER_S",\n    "RELEASE_CALENDAR", "RELEASE_CALENDAR_SHA256", "TABLE_RANGE",'
              ' "in_guard",\n]']
    return "\n\n".join(blocks) + "\n"


def build() -> dict[str, str]:
    """{repository path: module text} of every generated module."""
    tables = {g: group_table(g) for g in GROUP_ROOTS}
    return {OUT_CALENDAR: calendar_module(tables), OUT_RELEASES: releases_module()}


def main() -> None:
    for rel, text in build().items():
        (REPO_ROOT / rel).write_text(text, encoding="utf-8")
        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
        print(f"wrote {rel}: {text.count(chr(10))} lines, sha256 {digest[:12]}")


if __name__ == "__main__":
    main()
