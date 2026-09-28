"""One-off generator of the K1 literal tables (Stage E.7 Task 2, MemberCoder-B).

Not imported by any member. Run from the repository root:

    uv run python reports/stage_e7_briefs/gen_k1_tables.py

Sources (reports/stage_e7_member_specs.md S0.8, S0.11, K1-L-02, K1-L-10; K3-L-11, K4-L-01,
K4-L-13 adopted):
- EC-CAL, the D10 equity calendar: data.group_session.load_group_calendar("equity")
  (data/cme_calendar.py HOLIDAYS, data/calendars/equity.py SESSIONS, data/calendars/__init__.py),
  its is_trade_date and early_halt_ct, over 2019-05-01..2026-06-19;
- the engine's F: rules.sessions.flatten_time_ct(root, d) for MNQ, M2K and MYM (rules/sessions.py
  also holds the Topstep holiday rows that can move F), asserted equal for the three roots on
  every trade date;
- the Cboe VXN daily file saved by Task 1b, data/vendor/index_history/vxn/VXN_History.csv
  (columns DATE as MM/DD/YYYY, OPEN, HIGH, LOW, CLOSE; sha256 asserted as spec section 9 states
  it), every row dated 2019-04-30..2026-06-19, less the rows lead rulings R-1b-2 and R-1b-3 drop.

Tables written:
- strategy/members/k1/_calendar.py: EQUITY_TRADE_DATES (every EC-CAL equity trade date of the
  range) and EQUITY_FULL_SESSIONS (no early halt AND the regular engine F 15:08 CT), with the
  sources' sha256 and a comment naming every date where the early-halt test and the F test
  disagree.
- strategy/members/k1/_vxn.py: VXN_CLOSE, (ISO calendar date, the CLOSE field exactly as the file
  writes it) for every row of the range, oldest first, less DROPPED_VXN (spec section 9, lead
  01:12 PDT: 2021-04-02 and 2021-12-24 by R-1b-3, 2024-02-01 by R-1b-2), with the file's sha256.
  The research-window dates without V are asserted equal to R-1b-5's list.

The research-window facts the spec header states (non-trade dates, early-F dates) are asserted
before anything is written. tests/test_k1_members_tables.py recomputes every table from the
sources by independent code and asserts that each module is exactly this script's output.
"""

from __future__ import annotations

import hashlib
import re
import sys
import textwrap
from datetime import date, time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from data.group_session import load_group_calendar, trade_dates_between  # noqa: E402
from rules import sessions  # noqa: E402
from rules.products import product  # noqa: E402

OUT_CALENDAR = "strategy/members/k1/_calendar.py"
OUT_VXN = "strategy/members/k1/_vxn.py"
SESSIONS_FILE = "rules/sessions.py"
VXN_FILE = "data/vendor/index_history/vxn/VXN_History.csv"
GROUP = "equity"
ROOTS = ("MNQ", "M2K", "MYM")  # S0.1: the cluster's three vehicles
REGULAR_F = time(15, 8)  # D6 equity row (D line 391); rules.sessions.REGULAR_FLATTEN_CT["equity"]
CAL_FIRST, CAL_LAST = date(2019, 5, 1), date(2026, 6, 19)  # S0.8 / S0.11 (K4-L-13)
VXN_FIRST, VXN_LAST = date(2019, 4, 30), date(2026, 6, 19)  # S0.11 (K4-L-01)
# Spec section 9 (lead, 01:12 PDT, after Task 1b): the saved file and the dropped rows.
VXN_SHA256 = "f1b00135c4922ea756cd22cfeaa1d483700a6aed580f8da562f61574b5e1cdcc"
VXN_ROWS_IN_RANGE = 1797  # R-1b-1: rows of the file dated 2019-04-30..2026-06-19
DROPPED_VXN: dict[str, str] = {
    "2021-04-02": "R-1b-3: NYSE closed (Good Friday); the row repeats the prior close",
    "2021-12-24": "R-1b-3: NYSE closed (Christmas observed); the row repeats the prior close",
    "2024-02-01": "R-1b-2: CLOSE revised by Cboe (11.20 in the 2024-04-19 Wayback copy, 17.33 now)",
}
# R-1b-5: research-window trade dates d whose EC-CAL trade date d-1 has no VXN row
R_1B_5_NO_V = ("2025-05-27", "2025-06-20", "2025-07-07", "2025-09-02", "2025-11-28",
               "2026-01-20", "2026-02-17", "2026-04-06", "2026-05-26")
RESEARCH_FIRST, RESEARCH_LAST = date(2025, 4, 1), date(2026, 6, 19)
# Spec header (checked 00:57 PDT): research-window weekdays that are not equity trade dates, and
# the trade dates with an early engine F.
SPEC_RESEARCH_NON_TRADE = ("2025-04-18", "2025-12-25", "2026-01-01")
SPEC_RESEARCH_EARLY_F = (
    "2025-05-26", "2025-06-19", "2025-07-03", "2025-07-04", "2025-09-01", "2025-11-27",
    "2025-11-28", "2025-12-24", "2026-01-19", "2026-02-16", "2026-04-03", "2026-05-25",
    "2026-06-19")
VXN_HEADER = "DATE,OPEN,HIGH,LOW,CLOSE"
DECIMAL = r"(\d+\.\d+)"
VXN_ROW = re.compile(rf"^(\d{{2}})/(\d{{2}})/(\d{{4}}),{DECIMAL},{DECIMAL},{DECIMAL},{DECIMAL}$")
SATURDAY = 5
DATES_PER_LINE = 5
PAIRS_PER_LINE = 3
COMMENT_WIDTH = 96


# ------------------------------------------------------------------------ helpers ----
def sha256_of(rel: str) -> str:
    return hashlib.sha256((REPO_ROOT / rel).read_bytes()).hexdigest()


def in_research(iso: str) -> bool:
    return RESEARCH_FIRST.isoformat() <= iso <= RESEARCH_LAST.isoformat()


def wrap_comment(paragraphs: list[str]) -> str:
    return "\n".join("# " + line for text in paragraphs
                     for line in textwrap.wrap(text, COMMENT_WIDTH))


def render_dates(name: str, days: list[str], comment: str) -> str:
    lines = [f"# {comment} ({len(days)} dates)", f"{name}: tuple[str, ...] = ("]
    for i in range(0, len(days), DATES_PER_LINE):
        lines.append("    " + " ".join(f'"{d}",' for d in days[i:i + DATES_PER_LINE]))
    lines.append(")")
    return "\n".join(lines)


def render_pairs(name: str, rows: list[tuple[str, str]], comment: str) -> str:
    lines = [f"# {comment} ({len(rows)} rows)", f"{name}: tuple[tuple[str, str], ...] = ("]
    for i in range(0, len(rows), PAIRS_PER_LINE):
        lines.append("    " + " ".join(f'("{a}", "{b}"),' for a, b in rows[i:i + PAIRS_PER_LINE]))
    lines.append(")")
    return "\n".join(lines)


def render_reasons(name: str, pairs: list[tuple[str, str]]) -> str:
    body = "\n".join(f'    ("{d}",\n     "{r}"),' for d, r in pairs)
    return f"{name}: tuple[tuple[str, str], ...] = (\n{body}\n)"


def render_sources(name: str, pairs: list[tuple[str, str]]) -> str:
    body = "\n".join(f'    ("{p}",\n     "{s}"),' for p, s in pairs)
    return f"{name}: tuple[tuple[str, str], ...] = (\n{body}\n)"


# ----------------------------------------------------------------- the calendar ----
def equity_tables() -> tuple[list[str], list[str], list[tuple[str, str, str]], list[str]]:
    """(EQUITY_TRADE_DATES, EQUITY_FULL_SESSIONS, the dates where the two tests disagree as
    (date, early halt, F), the calendar module paths)."""
    cal = load_group_calendar(GROUP)
    assert cal.covers(CAL_FIRST) and cal.covers(CAL_LAST), cal.coverage
    assert all(product(r).group == GROUP for r in ROOTS)
    assert sessions.REGULAR_FLATTEN_CT[GROUP] == REGULAR_F
    trade: list[str] = []
    full: list[str] = []
    disagree: list[tuple[str, str, str]] = []
    for d in trade_dates_between(cal, CAL_FIRST, CAL_LAST):
        flats = {r: sessions.flatten_time_ct(r, d) for r in ROOTS}
        assert len(set(flats.values())) == 1, (d, flats)  # S0.11: one F for the three roots
        f = flats[ROOTS[0]]
        assert f is not None, d  # an EC-CAL trade date always has an F
        halt = cal.early_halt_ct(d)
        trade.append(d.isoformat())
        no_halt, regular_f = halt is None, f == REGULAR_F
        if no_halt and regular_f:
            full.append(d.isoformat())
        if no_halt != regular_f:
            disagree.append((d.isoformat(), "none" if halt is None else f"{halt:%H:%M}",
                             f"{f:%H:%M}"))
    early_f = [d.isoformat() for d in trade_dates_between(cal, RESEARCH_FIRST, RESEARCH_LAST)
               if sessions.flatten_time_ct(ROOTS[0], d) != REGULAR_F]
    assert tuple(early_f) == SPEC_RESEARCH_EARLY_F, early_f
    non_trade = [d for d in _weekdays(RESEARCH_FIRST, RESEARCH_LAST) if not cal.is_trade_date(d)]
    assert tuple(d.isoformat() for d in non_trade) == SPEC_RESEARCH_NON_TRADE, non_trade
    paths = sorted(cal.module_sha256())
    return trade, full, disagree, paths


def _weekdays(first: date, last: date) -> list[date]:
    return [date.fromordinal(n) for n in range(first.toordinal(), last.toordinal() + 1)
            if date.fromordinal(n).weekday() < SATURDAY]


CALENDAR_DOC = '''"""K1 calendar tables (literal; reports/stage_e7_member_specs.md S0.8, S0.11,
K1-L-02, K1-L-10; K3-L-11 and K4-L-13 adopted).

GENERATED by reports/stage_e7_briefs/gen_k1_tables.py. Do not edit by hand:
tests/test_k1_members_tables.py recomputes every table from its sources and asserts this file is
the generator's output. Members read these tuples; nothing here is computed at run time.

- EQUITY_TRADE_DATES: every EC-CAL equity trade date (data.group_session.load_group_calendar(
  "equity").is_trade_date: data/cme_calendar.py HOLIDAYS with data/calendars/equity.py SESSIONS)
  of 2019-05-01..2026-06-19, oldest first. An exchange holiday on which CME's equity session
  trades to an early halt is a trade date. K1-vxnband-01's "trade date d-1" is the entry
  immediately before d (K1-L-02).
- EQUITY_FULL_SESSIONS (S0.8, K1-L-10): the EQUITY_TRADE_DATES with no early halt
  (early_halt_ct None) AND the regular engine F of 15:08 CT on CT date d
  (rules.sessions.flatten_time_ct(root, d), equal for MNQ, M2K and MYM on every date).
  K1-vxnband-01 and K1-vwap-01 enter only on these dates.
"""'''


def calendar_module(trade: list[str], full: list[str], disagree: list[tuple[str, str, str]],
                    paths: list[str]) -> str:
    sources = [(p, sha256_of(p)) for p in paths] + [(SESSIONS_FILE, sha256_of(SESSIONS_FILE))]
    removed = [d for d in trade if d not in set(full)]
    listed = ", ".join(f"{d} (early halt {h}, F {f})" for d, h, f in disagree)
    notes = wrap_comment([
        "Dates where the early-halt test and the F test disagree: "
        + (f"{listed}; on every other trade date they agree." if disagree
           else "none; they keep or remove the same trade dates."),
        f"Trade dates the two tests remove: {len(removed)} of {len(trade)}; in the research "
        f"window 2025-04-01..2026-06-19: {', '.join(d for d in removed if in_research(d))}.",
        "EC-CAL's own coverage (data/cme_calendar.py CALENDAR_COVERAGE, 2019-01-01..2026-12-31) "
        "is wider than the tables' range; the tables stop at the spec's 2019-05-01..2026-06-19.",
    ])
    text = "\n\n".join([
        CALENDAR_DOC, "from __future__ import annotations",
        "# sha256 of each source file when the tables were generated\n"
        + render_sources("SOURCE_SHA256", sources),
        f'TABLE_RANGE = ("{CAL_FIRST.isoformat()}", "{CAL_LAST.isoformat()}")\n'
        f"F_ROOTS = ({', '.join(chr(34) + r + chr(34) for r in ROOTS)})"
        "  # the roots whose engine F was checked equal on every date\n"
        f'REGULAR_F_CT = "{REGULAR_F:%H:%M}"',
        notes,
        render_dates("EQUITY_TRADE_DATES", trade, "ISO trade dates, oldest first"),
        render_dates("EQUITY_FULL_SESSIONS", full,
                     "ISO trade dates without early halt and with F 15:08 CT, oldest first"),
    ]) + "\n"
    return text


# ---------------------------------------------------------------------- VXN ----
def vxn_rows() -> list[tuple[str, str]]:
    """(ISO date, CLOSE string) of every file row dated VXN_FIRST..VXN_LAST, oldest first, before
    the drops."""
    raw = (REPO_ROOT / VXN_FILE).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == VXN_SHA256, "the VXN file is not section 9's"
    lines = raw.decode("ascii").splitlines()
    assert lines[0] == VXN_HEADER, lines[0]
    rows: list[tuple[str, str]] = []
    for line in lines[1:]:
        match = VXN_ROW.match(line)
        assert match is not None, "a VXN row does not have the DATE,OPEN,HIGH,LOW,CLOSE shape"
        month, day, year, _o, _h, _l, close = match.groups()
        d = date(int(year), int(month), int(day))
        if VXN_FIRST <= d <= VXN_LAST:
            rows.append((d.isoformat(), close))
    days = [d for d, _ in rows]
    assert days == sorted(days) and len(set(days)) == len(days), "VXN rows unsorted or doubled"
    assert days[0] == VXN_FIRST.isoformat(), days[0]
    assert len(rows) == VXN_ROWS_IN_RANGE, len(rows)
    return rows


def apply_drops(rows: list[tuple[str, str]]) -> list[tuple[str, str]]:
    """Section 9: every dropped date is a row of the range; it is removed, not replaced."""
    have = {d for d, _ in rows}
    assert set(DROPPED_VXN) <= have, sorted(set(DROPPED_VXN) - have)
    kept = [(d, c) for d, c in rows if d not in DROPPED_VXN]
    assert len(kept) == VXN_ROWS_IN_RANGE - len(DROPPED_VXN)
    return kept


def no_v_dates(trade: list[str], have: set[str], first: str, last: str) -> list[str]:
    """Trade dates d in [first, last] whose EQUITY_TRADE_DATES predecessor has no VXN row."""
    return [d for prev, d in zip(trade, trade[1:], strict=False)
            if first <= d <= last and prev not in have]


VXN_DOC = '''"""K1-vxnband-01's VXN table (literal; reports/stage_e7_member_specs.md S0.11, K1-L-01,
K1-L-02; K4-L-01 adopted).

GENERATED by reports/stage_e7_briefs/gen_k1_tables.py from the Cboe VXN daily file saved by
Task 1b (data/vendor/index_history/vxn/VXN_History.csv, sha256 below). Do not edit by hand:
tests/test_k1_members_tables.py recomputes the table from the saved file and asserts this file is
the generator's output.

VXN_CLOSE: (ISO calendar date, the file's CLOSE field exactly as written), every row dated
2019-04-30..2026-06-19, oldest first, less DROPPED_VXN (spec section 9, lead rulings R-1b-2 and
R-1b-3: removed, not replaced; a trade date whose d-1 is dropped has no V and is not traded).
Rows after 2026-06-19 are not included. The member reads it as a mapping date -> Decimal(CLOSE).
The table spans both windows; Task 1b checked the research-window rows (R-1b-1: kept, not
point-in-time checked).
"""'''


def vxn_module(trade: list[str]) -> str:
    rows = apply_drops(vxn_rows())
    have = {d for d, _ in rows}
    no_row = [d for d in trade if d not in have and in_research(d)]
    not_trade = sorted(d for d in have if d not in set(trade) and d >= CAL_FIRST.isoformat())
    research_no_v = no_v_dates(trade, have, RESEARCH_FIRST.isoformat(),
                               RESEARCH_LAST.isoformat())
    assert tuple(research_no_v) == R_1B_5_NO_V, research_no_v
    all_no_v = no_v_dates(trade, have, trade[1], trade[-1])
    assert {"2021-04-05", "2024-02-02"} <= set(all_no_v)  # section 9: the drops' effect
    notes = wrap_comment([
        "EC-CAL equity trade dates of the research window with no VXN row: "
        f"{', '.join(no_row) or 'none'}. The trade dates after them have no V and are not "
        f"traded (K1-L-02, R-1b-5): {', '.join(research_no_v)}.",
        "VXN rows on a date that is not an EC-CAL equity trade date (never read), after the "
        f"drops: {', '.join(not_trade) or 'none'}.",
        f"Trade dates 2019-05-02..2026-06-19 without V: {len(all_no_v)}.",
    ])
    text = "\n\n".join([
        VXN_DOC, "from __future__ import annotations",
        "# sha256 of the saved file when the table was generated\n"
        + render_sources("VXN_SOURCE_SHA256", [(VXN_FILE, sha256_of(VXN_FILE))]),
        f'VXN_RANGE = ("{VXN_FIRST.isoformat()}", "{VXN_LAST.isoformat()}")',
        "# Spec section 9 (lead, 01:12 PDT): rows of the range removed, not replaced, and why\n"
        + render_reasons("DROPPED_VXN", sorted(DROPPED_VXN.items())),
        notes,
        render_pairs("VXN_CLOSE", rows, "(ISO date, CLOSE), oldest first"),
    ]) + "\n"
    return text


def build() -> dict[str, str]:
    """{repository path: module text} of every generated module."""
    trade, full, disagree, paths = equity_tables()
    out = {OUT_CALENDAR: calendar_module(trade, full, disagree, paths)}
    if (REPO_ROOT / VXN_FILE).is_file():
        out[OUT_VXN] = vxn_module(trade)
    return out


def main() -> None:
    texts = build()
    if OUT_VXN not in texts:
        print(f"{VXN_FILE} is absent: {OUT_VXN} not written")
    for rel, text in texts.items():
        (REPO_ROOT / rel).write_text(text, encoding="utf-8")
        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
        print(f"wrote {rel}: {text.count(chr(10))} lines, sha256 {digest[:12]}")


if __name__ == "__main__":
    main()
