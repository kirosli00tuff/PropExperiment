"""One-off generator of strategy/members/k3/_mehedge_signal.py (Stage E.4 Part 3, MemberCoder-A).

Not imported by the member code. Run from the repository root:

    uv run python reports/stage_e4_briefs/gen_k3_mehedge.py

It writes K3-mehedge-01's literal monthly signal table for 6J (reports/stage_e4c_member_specs.md
section 6, S0.11, K3-L-07; catalog reports/stage_e0_catalog_K3.md lines 590-597):

    R_eq(m) = ln(P_a / P_b)
    P_a = the Nikkei 225's last official close on a Tokyo date strictly before ME(m)'s calendar date
    P_b = its last official close in calendar month m-1
    None when either close is missing.

Inputs:
- the four saved Nikkei Inc. daily files listed in reports/stage_e4c_release_check.json key
  index.N225 (saved_path, sha256), each checked against its sha256 before it is read. Where the
  files overlap, every date's close must be equal in all files holding it (checked); the close is
  labelled with the newest capture holding it (live 2026-09-27, then the Wayback captures of
  2024-04-01, 2023-05-23, 2020-09-19).
- EC-JP, the Tokyo business days (weekday, not a Cabinet Office holiday from the release check's
  ec_jp_holidays, not 31 Dec-3 Jan; K3-L-08). A close is "missing" when the Tokyo business day that
  holds P_a (the last one before ME(m)) or P_b (the last one of month m-1) has no close in the
  files. The files' dates over 2019-04-01..2026-06-19 are checked to equal EC-JP's business days.
- ME(m), the last EC-CAL FX trade date of calendar month m, halted or not, for the months whose
  whole calendar month lies inside EC-CAL's coverage 2019-05-01..2026-06-19 (K4-L-13, specs
  section 11): 2019-05..2026-05. Cross-checked against the release check's month_ends.

tests/test_e4_k3_members_m_signal.py recomputes the table from the saved files and asserts
equality with the written module (the pin).
"""

from __future__ import annotations

import csv
import hashlib
import json
import sys
from datetime import date, timedelta
from decimal import Context, Decimal
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from data.group_session import load_group_calendar, trade_dates_between  # noqa: E402

RELEASE_CHECK = "reports/stage_e4c_release_check.json"
OUT = REPO_ROOT / "strategy" / "members" / "k3" / "_mehedge_signal.py"
# newest capture first: the label a close carries when several files hold its date
PRECEDENCE = (
    "data/vendor/index_history/nikkei_stock_average_daily_en.csv",
    "data/vendor/index_history/nikkei_wayback/wb_20240401064221_nikkei_daily_en.csv",
    "data/vendor/index_history/nikkei_wayback/wb_20230523124334_nikkei_daily_en.csv",
    "data/vendor/index_history/nikkei_wayback/wb_20200919105418_nikkei_daily_en.csv",
)
CHECK_FIRST, CHECK_LAST = date(2019, 4, 1), date(2026, 6, 19)
LN_CONTEXT = Context(prec=34)


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_nikkei(path: Path) -> dict[date, Decimal]:
    """Nikkei Inc.'s daily CSV: a header, quoted rows "YYYY/MM/DD","close",... and a copyright
    footer row; only the date and the Close column are read. The footer's apostrophe is one
    non-ASCII byte (0x81), so the file is decoded as latin-1; every data row is ASCII."""
    out: dict[date, Decimal] = {}
    with path.open(encoding="latin-1", newline="") as fh:
        rows = list(csv.reader(fh))
    assert rows[0][:2] == ["Date of Data", "Close"], (path, rows[0])
    for row in rows[1:]:
        if len(row) < 2 or row[0].count("/") != 2:
            continue  # the copyright footer
        y, m, d = (int(x) for x in row[0].split("/"))
        day = date(y, m, d)
        assert day not in out, (path, day)
        out[day] = Decimal(row[1])
    return out


def merged_closes(check: dict) -> tuple[dict[date, Decimal], dict[date, str]]:
    """Every date's close and the saved file it is labelled with; overlaps must agree."""
    n225 = check["index"]["N225"]
    assert sorted(n225["saved_path"]) == sorted(PRECEDENCE)
    closes: dict[date, Decimal] = {}
    label: dict[date, str] = {}
    for rel in PRECEDENCE:
        path = REPO_ROOT / rel
        assert sha256_of(path) == n225["sha256"][rel], rel
        for day, close in parse_nikkei(path).items():
            if day in closes:
                assert closes[day] == close, (day, rel, label[day])  # overlaps agree
                continue
            closes[day], label[day] = close, rel
    return closes, label


def tokyo_business_days(check: dict) -> list[date]:
    holidays = {date.fromisoformat(h["date"]) for h in check["ec_jp_holidays"]}
    first, last = date(2019, 1, 1), date(2026, 12, 31)
    out, day = [], first
    while day <= last:
        year_end = (day.month, day.day) in ((12, 31), (1, 1), (1, 2), (1, 3))
        if day.weekday() < 5 and day not in holidays and not year_end:
            out.append(day)
        day += timedelta(days=1)
    return out


def month_ends(check: dict) -> list[tuple[str, date]]:
    """(YYYY-MM, ME(m)) for the months wholly inside EC-CAL FX's coverage."""
    cal = load_group_calendar("fx")
    first, last = cal.coverage
    by_month: dict[str, date] = {}
    for day in trade_dates_between(cal, first, last):
        by_month[f"{day:%Y-%m}"] = day  # ascending: the last one wins
    out = []
    for month, me in sorted(by_month.items()):
        month_first = date(me.year, me.month, 1)
        next_first = date(me.year + me.month // 12, me.month % 12 + 1, 1)
        if month_first >= first and next_first - timedelta(days=1) <= last:
            out.append((month, me))
    expected = [(r["month"], date.fromisoformat(r["me_date"])) for r in check["month_ends"]
                if r["in_ec_cal_coverage"]]
    assert out == expected, "ME(m) differs from the release check's month_ends"
    return out


def r_eq_row(month: str, me: date, closes: dict[date, Decimal], bdays: list[date]
             ) -> tuple[float | None, date, date]:
    """R_eq for month m (None when a close is missing), with the P_a and P_b dates."""
    y, m = (int(x) for x in month.split("-"))
    prev_y, prev_m = (y, m - 1) if m > 1 else (y - 1, 12)
    pa_day = max(b for b in bdays if b < me)
    pb_day = max(b for b in bdays if (b.year, b.month) == (prev_y, prev_m))
    if pa_day not in closes or pb_day not in closes:
        return None, pa_day, pb_day
    return float((closes[pa_day] / closes[pb_day]).ln(LN_CONTEXT)), pa_day, pb_day


def build() -> tuple[list[tuple], list[tuple], dict[str, str], str]:
    check_path = REPO_ROOT / RELEASE_CHECK
    check = json.loads(check_path.read_text(encoding="utf-8"))
    closes, label = merged_closes(check)
    bdays = tokyo_business_days(check)
    window = {d for d in closes if CHECK_FIRST <= d <= CHECK_LAST}
    assert window == {b for b in bdays if CHECK_FIRST <= b <= CHECK_LAST}, "files vs EC-JP"
    rows, audit = [], []
    for month, me in month_ends(check):
        r, pa_day, pb_day = r_eq_row(month, me, closes, bdays)
        assert pa_day < me and pb_day < date(me.year, me.month, 1)  # no close on or after ME
        rows.append((month, me.isoformat(), r))
        audit.append((month, pa_day.isoformat(), str(closes.get(pa_day, "")),
                      Path(label.get(pa_day, "")).name, pb_day.isoformat(),
                      str(closes.get(pb_day, "")), Path(label.get(pb_day, "")).name))
    shas = check["index"]["N225"]["sha256"]
    return rows, audit, {rel: shas[rel] for rel in PRECEDENCE}, sha256_of(check_path)


HEADER = f'''"""K3-mehedge-01's monthly signal for 6J (literal table; S0.11, K3-L-07).

GENERATED by reports/stage_e4_briefs/gen_k3_mehedge.py from the saved Nikkei Inc.
daily files of {RELEASE_CHECK} key index.N225 (sha256s below).
Do not edit by hand: tests/test_e4_k3_members_m_signal.py recomputes the table from the
saved files and asserts equality.

R_eq(m) = ln(P_a / P_b): P_a the Nikkei 225's last official close on a Tokyo date
strictly before ME(m)'s calendar date, P_b its last official close in calendar month m-1
(catalog reports/stage_e0_catalog_K3.md lines 590-597). None when a close is missing (the
Tokyo business day holding it, EC-JP, has no close in the files). ME(m) = the last EC-CAL
FX trade date of month m, halted or not, for the months inside EC-CAL's coverage
(2019-05..2026-05). Where the saved files overlap, each close is equal in every file
holding it (checked by the generator); MEHEDGE_CLOSES_6J names the newest capture holding
each close used. The 6E trial (EURO STOXX 50) is not traded: its free history was not
obtained (specs section 11), so there is no 6E table.
"""'''


def render(rows: list[tuple], audit: list[tuple], shas: dict[str, str], check_sha: str) -> str:
    n_none = sum(1 for r in rows if r[2] is None)
    lines = [
        *HEADER.splitlines(),
        "",
        "from __future__ import annotations",
        "",
        "MEHEDGE_SOURCE = (",
        '    "Nikkei Inc. nikkei_stock_average_daily_en.csv (live 2026-09-27 and Wayback "',
        '    "captures 20240401064221, 20230523124334, 20200919105418); EC-JP business days; "',
        '    "EC-CAL FX month-ends"',
        ")",
        "# sha256 of each saved file when the table was generated (equal to the release check's)",
        "MEHEDGE_SOURCE_SHA256: tuple[tuple[str, str], ...] = (",
    ]
    lines += [f'    ("{rel}",\n     "{sha}"),' for rel, sha in shas.items()]
    lines += [
        ")",
        f'MEHEDGE_RELEASE_CHECK_SHA256 = "{check_sha}"',
        "",
        f"# (month, ME(m), R_eq for 6J or None), oldest first ({len(rows)} months, {n_none} None)",
        "MEHEDGE_R_EQ_6J: tuple[tuple[str, str, float | None], ...] = (",
    ]
    lines += [f'    ("{m}", "{me}", {r!r}),' for m, me, r in rows]
    lines += [
        ")",
        "",
        "# the closes used: (month, P_a date, P_a close, P_a file, P_b date, P_b close, P_b file)",
        "MEHEDGE_CLOSES_6J: tuple[tuple[str, str, str, str, str, str, str], ...] = (",
    ]
    lines += ["    (" + ", ".join(f'"{x}"' for x in row[:4]) + ",\n     "
              + ", ".join(f'"{x}"' for x in row[4:]) + ")," for row in audit]
    lines += [")", ""]
    return "\n".join(lines)


def main() -> None:
    rows, audit, shas, check_sha = build()
    OUT.write_text(render(rows, audit, shas, check_sha), encoding="utf-8")
    n_none = sum(1 for r in rows if r[2] is None)
    print(f"wrote {OUT.relative_to(REPO_ROOT)}: {len(rows)} months {rows[0][0]}..{rows[-1][0]}, "
          f"{n_none} None, {sum(1 for r in rows if r[2] == 0)} zero")


if __name__ == "__main__":
    main()
