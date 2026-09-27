"""MemberAuditor-K3 (Stage E.4 Part 3, Task 3, item 5): recompute every K3 literal table from its
sources in the auditor's own code and diff it against strategy/members/k3/_calendar.py, _clocks.py
and _mehedge_signal.py. Read-only; prints counts and differences only.

Sources: EC-CAL FX (data.group_session.load_group_calendar("fx")), rules.sessions.flatten_time_ct,
the gov.uk bank-holiday JSON and the CAO holiday CSV saved by the release checkers, the ECB
working-hours captures (TARGET), the saved Nikkei files, and zoneinfo for the clocks.
Run: PYTHONPATH=. uv run python reports/stage_e4_briefs/audit_k3/recompute_tables.py
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from datetime import date, datetime, time, timedelta
from decimal import Decimal, getcontext
from pathlib import Path
from zoneinfo import ZoneInfo

from data.group_session import load_group_calendar, trade_dates_between
from rules import sessions
from strategy.members.k3 import _calendar as C
from strategy.members.k3 import _clocks as K
from strategy.members.k3 import _mehedge_signal as M

REPO = Path(__file__).resolve().parents[3]
CT = ZoneInfo("America/Chicago")
ROOTS = ("6E", "6A", "6B", "6C", "6J", "6S", "6N")
FIRST, LAST = date(2019, 5, 1), date(2026, 6, 19)  # EC-CAL coverage
TK_FIRST, TK_LAST = date(2019, 4, 1), date(2026, 6, 19)
RESEARCH = (date(2025, 4, 1), date(2026, 6, 19))
CHECK = REPO / "reports" / "stage_e4c_release_check.json"
GOVUK = REPO / "data" / "vendor" / "release_pages" / "e4b" / "govuk_bank-holidays.json"
CAO = REPO / "data" / "vendor" / "release_pages" / "e4c" / "cao_syukujitsu.csv"
E4C = REPO / "data" / "vendor" / "release_pages" / "e4c"
IDX = REPO / "data" / "vendor" / "index_history"

findings: list[str] = []


def diff(name: str, mine, theirs) -> None:
    mine, theirs = list(mine), list(theirs)
    same = mine == theirs
    print(f"{name}: mine {len(mine)} rows, table {len(theirs)} rows, equal={same}")
    if not same:
        sm, st = set(mine), set(theirs)
        print(f"  only mine: {sorted(sm - st)[:20]}")
        print(f"  only table: {sorted(st - sm)[:20]}")
        if sm == st:
            print("  (same set, different order)")
        findings.append(f"{name} differs")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def weekdays(a: date, b: date):
    d = a
    while d <= b:
        if d.weekday() < 5:
            yield d
        d += timedelta(days=1)


def easter(year: int) -> date:  # Anonymous Gregorian algorithm
    a = year % 19
    b, c = divmod(year, 100)
    d, e = divmod(b, 4)
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = divmod(c, 4)
    ll = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * ll) // 451
    month, day = divmod(h + ll - 7 * m + 114, 31)
    return date(year, month, day + 1)


# ------------------------------------------------------------------ 1. FX_FULL_SESSIONS
cal = load_group_calendar("fx")
trade_dates = trade_dates_between(cal, FIRST, LAST)
print(f"EC-CAL fx trade dates in coverage: {len(trade_dates)}; coverage {cal.coverage}")
halted = [d for d in trade_dates if cal.early_halt_ct(d) is not None]
print(f"  early-halt trade dates: {len(halted)}")
full: list[str] = []
early_f: list[str] = []
f_by_root_disagree = []
for d in trade_dates:
    if cal.early_halt_ct(d) is not None:
        continue
    fs = {r: sessions.flatten_time_ct(r, d) for r in ROOTS}
    if len(set(fs.values())) != 1:
        f_by_root_disagree.append((d, fs))
    if all(f == time(15, 8) for f in fs.values()):
        full.append(d.isoformat())
    else:
        early_f.append(d.isoformat())
print(f"  F differs across K3 roots on: {f_by_root_disagree}")
diff("FX_FULL_SESSIONS", full, C.FX_FULL_SESSIONS)
diff("FX_EARLY_F_DATES", early_f, C.FX_EARLY_F_DATES)
print(f"  early-F dates: {early_f}")
research_full = [d for d in full if RESEARCH[0].isoformat() <= d <= RESEARCH[1].isoformat()]
research_td = [d for d in trade_dates if RESEARCH[0] <= d <= RESEARCH[1]]
print(f"  research window: trade dates {len(research_td)}, full sessions {len(research_full)}, "
      f"halts {[d.isoformat() for d in research_td if cal.early_halt_ct(d)]}, "
      f"early-F {[d for d in early_f if d >= '2025-04-01']}")
# the literal (bar-label) reading of C4 would keep the early-F dates:
print(f"  literal-C4 (halt label only) sessions: {len(full) + len(early_f)}")

# ------------------------------------------------------------------ 2. MONTH_ENDS
me_rows = []
by_month: dict[tuple[int, int], date] = {}
for d in trade_dates:
    by_month[(d.year, d.month)] = d  # ascending, so the last wins
for (y, m), d in sorted(by_month.items()):
    last_day = (date(y + (m == 12), m % 12 + 1, 1) - timedelta(days=1))
    if FIRST <= last_day <= LAST:
        me_rows.append((f"{y:04d}-{m:02d}", d.isoformat()))
diff("MONTH_ENDS", me_rows, C.MONTH_ENDS)
print(f"  months whose last day is outside coverage (not listed): "
      f"{[k for k, d in sorted(by_month.items()) if not (FIRST <= (date(k[0] + (k[1] == 12), k[1] % 12 + 1, 1) - timedelta(days=1)) <= LAST)]}")
halted_me = [(m, d) for m, d in me_rows if cal.early_halt_ct(date.fromisoformat(d))]
print(f"  halted month-ends: {halted_me}")

# ------------------------------------------------------------------ 3. EW_BANK_HOLIDAYS
gov = json.loads(GOVUK.read_text(encoding="utf-8"))
ew = sorted(e["date"] for e in gov["england-and-wales"]["events"]
            if "2019-04-01" <= e["date"] <= "2026-06-30")
print(f"  gov.uk file sha256 {sha(GOVUK)[:16]}; E&W events in file: "
      f"{len(gov['england-and-wales']['events'])}")
diff("EW_BANK_HOLIDAYS", ew, C.EW_BANK_HOLIDAYS)
print(f"  E&W weekday holidays in the research window: "
      f"{[d for d in ew if '2025-04-01' <= d <= '2026-06-19']}")

# ------------------------------------------------------------------ 4. TGT_CLOSING_DAYS
tgt = []
for y in range(2019, 2027):
    e = easter(y)
    tgt += [date(y, 1, 1), e - timedelta(days=2), e + timedelta(days=1), date(y, 5, 1),
            date(y, 12, 25), date(y, 12, 26)]
tgt_s = sorted(d.isoformat() for d in tgt)
diff("TGT_CLOSING_DAYS (six-day rule 2019-2026)", tgt_s, C.TGT_CLOSING_DAYS)
# spot check against the saved ECB pages: the starred rows of the 2025 and 2026 captures
for cap, year in (("wb_20241230111431_ecb_working_hours.html", 2025),
                  ("wb_20251218035041_ecb_working_hours.html", 2026),
                  ("ecb_working_hours_live.html", 2026)):
    html = (E4C / cap).read_text(encoding="utf-8", errors="replace")
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"\s+", " ", text)
    stars = re.findall(r"([A-Z][A-Za-z' ]+?)\* (\d{1,2} [A-Z][a-z]+ %d)" % year, text)
    stars = [datetime.strptime(dm, "%d %B %Y").date().isoformat() for _, dm in stars]
    print(f"  {cap}: starred {year} rows found: {stars}")
    print(f"    table {year}: {[d for d in C.TGT_CLOSING_DAYS if d.startswith(str(year))]}")

# ------------------------------------------------------------------ 5. Tokyo tables
raw = CAO.read_bytes()
txt = raw.decode("shift_jis")
jp_hol = set()
for line in txt.splitlines()[1:]:
    ds = line.split(",")[0].strip()
    if not ds:
        continue
    y, m, d = (int(x) for x in ds.split("/"))
    jp_hol.add(date(y, m, d))
print(f"  CAO CSV sha256 {sha(CAO)[:16]}: {len(jp_hol)} holidays total; "
      f"{len([h for h in jp_hol if 2019 <= h.year <= 2026])} in 2019-2026")


def tokyo_bday(d: date) -> bool:
    return (d.weekday() < 5 and d not in jp_hol and not (d.month == 12 and d.day == 31)
            and not (d.month == 1 and d.day <= 3))


tk = [d for d in weekdays(TK_FIRST, TK_LAST) if tokyo_bday(d)]
diff("TOKYO_BUSINESS_DAYS", [d.isoformat() for d in tk], C.TOKYO_BUSINESS_DAYS)
last_of_month: dict[tuple[int, int], date] = {}
for d in tk:
    last_of_month[(d.year, d.month)] = d
# the last Tokyo business day of a month is only known inside the range if the month is complete
tk_me = {d for (y, m), d in last_of_month.items()
         if (date(y + (m == 12), m % 12 + 1, 1) - timedelta(days=1)) <= TK_LAST}
gotobi = [d for d in tk if d.day in (5, 10, 15, 20, 25, 30)]
ev = sorted(set(gotobi) | tk_me)
diff("GOTOBI_OR_TOKYO_MONTH_END", [d.isoformat() for d in ev], C.GOTOBI_OR_TOKYO_MONTH_END)
print(f"  gotobi {len(gotobi)}, Tokyo month-ends in range {len(tk_me)}, union {len(ev)}")
# year-end: the MURC TTM files (the check's evidence) if readable
try:
    import pandas as pd
    for y in (2019, 2020, 2024, 2025, 2026):
        xls = E4C / "murc" / f"murc_{y}.xls"
        df = pd.read_excel(xls, header=None)
        # find rows whose first cell is a date and print the late-Dec / early-Jan ones
        found = []
        for _, row in df.iterrows():
            v = row.iloc[0]
            dt = None
            if isinstance(v, (datetime, pd.Timestamp)):
                dt = v.date()
            elif isinstance(v, str) and re.match(r"\d{4}/\d{1,2}/\d{1,2}", v):
                dt = datetime.strptime(v.split()[0], "%Y/%m/%d").date()
            if dt and ((dt.month == 12 and dt.day >= 28) or (dt.month == 1 and dt.day <= 6)):
                found.append(dt.isoformat())
        print(f"  MURC {y} (sha {sha(xls)[:8]}): year-end rows with a TTM line: {found}")
except Exception as exc:  # noqa: BLE001
    print(f"  MURC xls not readable here: {type(exc).__name__}: {exc}")

# ------------------------------------------------------------------ 6. Clocks
LON, BER, TKY = ZoneInfo("Europe/London"), ZoneInfo("Europe/Berlin"), ZoneInfo("Asia/Tokyo")


def ct_of(d: date, hh: int, mm: int, zone: ZoneInfo) -> datetime:
    return datetime.combine(d, time(hh, mm), tzinfo=zone).astimezone(CT)


t_l = [(d.isoformat(), ct_of(d, 16, 0, LON).strftime("%H:%M")) for d in weekdays(TK_FIRST, TK_LAST)]
t_e = [(d.isoformat(), ct_of(d, 14, 15, BER).strftime("%H:%M")) for d in weekdays(TK_FIRST, TK_LAST)]
bad_day = [(d, x) for d, x in ((d, ct_of(d, 16, 0, LON)) for d in weekdays(TK_FIRST, TK_LAST))
           if x.date() != d]
print(f"  T_L instants not on CT date d: {bad_day[:3]}")
diff("T_L", t_l, K.T_L)
diff("T_E", t_e, K.T_E)
t_t = []
t_t_bad = []
for d in tk:
    x = ct_of(d, 9, 55, TKY)
    if x.date() != d - timedelta(days=1):
        t_t_bad.append((d, x))
    t_t.append((d.isoformat(), x.strftime("%H:%M")))
print(f"  T_T instants not on CT date d-1: {t_t_bad[:3]}")
diff("T_T", t_t, K.T_T)
kat = {"T_L": {"2025-03-10": "11:00", "2025-03-31": "10:00", "2025-10-27": "11:00",
               "2025-11-03": "10:00", "2021-11-01": "11:00", "2021-11-02": "11:00",
               "2021-11-03": "11:00", "2021-11-04": "11:00", "2021-11-05": "11:00"},
       "T_E": {"2025-03-10": "08:15", "2025-04-01": "07:15"},
       "T_T": {"2025-11-04": "18:55", "2025-01-10": "18:55", "2025-03-10": "19:55",
               "2025-07-10": "19:55"}}
tables = {"T_L": dict(K.T_L), "T_E": dict(K.T_E), "T_T": dict(K.T_T)}
for name, cases in kat.items():
    res = {d: (tables[name].get(d), exp) for d, exp in cases.items()}
    ok = all(a == b for a, b in res.values())
    print(f"  C9 known-answer {name}: all pass={ok} {'' if ok else res}")
# C9's 11:00 ranges
c9 = ["2019-03-11..2019-03-29", "2019-10-28..2019-11-01", "2020-03-09..2020-03-27",
      "2020-10-26..2020-10-30", "2021-03-15..2021-03-26", "2021-11-01..2021-11-05",
      "2022-03-14..2022-03-25", "2022-10-31..2022-11-04", "2023-03-13..2023-03-24",
      "2023-10-30..2023-11-03", "2024-03-11..2024-03-29", "2024-10-28..2024-11-01",
      "2025-03-10..2025-03-28", "2025-10-27..2025-10-31", "2026-03-09..2026-03-27"]
c9_days = set()
for r in c9:
    a, b = (date.fromisoformat(x) for x in r.split(".."))
    c9_days |= {d.isoformat() for d in weekdays(max(a, TK_FIRST), min(b, TK_LAST))}
at11 = {d for d, t in K.T_L if t == "11:00"}
at0815 = {d for d, t in K.T_E if t == "08:15"}
print(f"  T_L 11:00 days == C9 list: {at11 == c9_days} ({len(at11)}); T_E 08:15 days == same: "
      f"{at0815 == at11}")

# ------------------------------------------------------------------ 7. mehedge R_eq
check = json.loads(CHECK.read_text(encoding="utf-8"))
print(f"  release check sha256 {sha(CHECK)} == pinned {sha(CHECK) == M.MEHEDGE_RELEASE_CHECK_SHA256}")
for rel, s in M.MEHEDGE_SOURCE_SHA256:
    p = REPO / rel
    ok = sha(p) == s
    in_check = check["index"]["N225"]["sha256"].get(rel) == s
    print(f"  {rel}: sha matches table {ok}, matches check {in_check}")
manifest = [json.loads(l) for l in (IDX / "manifest.jsonl").read_text().splitlines() if l.strip()]
served = {m["file"]: m for m in manifest if m.get("http") == "200"}
for rel, s in M.MEHEDGE_SOURCE_SHA256:
    name = Path(rel).name
    m = served.get(name)
    print(f"    manifest {name}: served={m['url_served'][:90] if m else None} sha_ok="
          f"{m['sha256'] == s if m else None} bytes={m['bytes'] if m else None}")


NIKKEI_ROW = re.compile(r'^"(\d{4})/(\d{2})/(\d{2})","(\d+\.\d+)"')


def parse_nikkei(path: Path) -> dict[date, Decimal]:
    """Nikkei Inc. daily file: header 'Date of Data,Close,Open,High,Low'; the first number
    after the date is the official close."""
    out = {}
    header = path.read_text(encoding="latin-1").splitlines()[0].strip()
    assert header.startswith("Date of Data,Close"), (path, header)
    for line in path.read_text(encoding="latin-1").splitlines():
        m = NIKKEI_ROW.match(line)
        if m:
            y, mo, d, close = m.groups()
            out[date(int(y), int(mo), int(d))] = Decimal(close)
    return out


closes: dict[date, Decimal] = {}
conflicts = []
for rel, _ in M.MEHEDGE_SOURCE_SHA256:
    part = parse_nikkei(REPO / rel)
    print(f"    {Path(rel).name}: {len(part)} closes {min(part)}..{max(part)}")
    for d, v in part.items():
        if d in closes and closes[d] != v:
            conflicts.append((d, closes[d], v))
        closes.setdefault(d, v)
print(f"  overlap conflicts: {len(conflicts)}")
win = {d for d in closes if TK_FIRST <= d <= TK_LAST}
tkset = set(tk)
print(f"  closes in window {len(win)}; == Tokyo business days: {win == tkset}; "
      f"missing {sorted(tkset - win)[:5]}; extra {sorted(win - tkset)[:5]}")
getcontext().prec = 34
mine_rows = []
audit = []
for month, me_s in me_rows:
    me = date.fromisoformat(me_s)
    y, m = (int(x) for x in month.split("-"))
    py, pm = (y, m - 1) if m > 1 else (y - 1, 12)
    pa_candidates = [d for d in closes if d < me]
    pa = max(pa_candidates)
    pb = max(d for d in closes if (d.year, d.month) == (py, pm))
    assert pa < me and pb < date(y, m, 1)
    r = float((closes[pa] / closes[pb]).ln())
    mine_rows.append((month, me_s, r))
    audit.append((month, pa, pb))
table = list(M.MEHEDGE_R_EQ_6J)
print(f"MEHEDGE_R_EQ_6J: mine {len(mine_rows)} rows, table {len(table)} rows")
exact = sum(1 for a, b in zip(mine_rows, table) if a == b)
close_enough = sum(1 for a, b in zip(mine_rows, table)
                   if a[:2] == b[:2] and b[2] is not None and math.isclose(a[2], b[2], rel_tol=1e-12, abs_tol=1e-15))
print(f"  exact float equality on {exact}/{len(table)}; equal within 1e-12 on {close_enough}")
print(f"  months mismatched: {[(a, b) for a, b in zip(mine_rows, table) if a[:2] != b[:2]]}")
signs_zero = [r for r in table if r[2] is None or r[2] == 0]
print(f"  None or zero rows: {signs_zero}")
# P_a always the Tokyo business day just before ME? (the 'second-last trading day' case)
gap = [(mo, pa, me) for (mo, pa, pb), (_, me, _) in zip(audit, mine_rows)
       if (date.fromisoformat(me) - pa).days > 3]
print(f"  months where P_a is more than 3 days before ME: {gap}")
# does the CLOSES audit table (if present) agree with my P_a / P_b dates?
if hasattr(M, "MEHEDGE_CLOSES_6J"):
    theirs = {r[0]: (r[1], r[4]) for r in M.MEHEDGE_CLOSES_6J}
    mism = [(mo, pa.isoformat(), pb.isoformat(), theirs.get(mo)) for mo, pa, pb in audit
            if theirs.get(mo) != (pa.isoformat(), pb.isoformat())]
    print(f"  P_a/P_b dates vs MEHEDGE_CLOSES_6J: mismatches {mism[:5]} (of {len(audit)})")
# sample rows for the report
for mo in ("2025-04", "2025-10", "2026-03", "2026-05"):
    row = next(r for r in mine_rows if r[0] == mo)
    a = next(x for x in audit if x[0] == mo)
    print(f"  {mo}: ME {row[1]} P_a {a[1]} {closes[a[1]]} P_b {a[2]} {closes[a[2]]} R_eq {row[2]:+.6f}")

# ------------------------------------------------------------------ 8. SX5E drop evidence
stoxx_files = [IDX / "stoxx_h_3msx5e.txt"] + sorted((IDX / "stoxx_wayback").glob("*.txt"))
sx_dates = set()
for p in stoxx_files:
    for line in p.read_text(encoding="latin-1").splitlines():
        m = re.match(r"(\d{2})\.(\d{2})\.(\d{4})", line.strip())
        if m:
            sx_dates.add(date(int(m.group(3)), int(m.group(2)), int(m.group(1))))
tgt_set = {date.fromisoformat(d) for d in C.TGT_CLOSING_DAYS}
sx_expected = [d for d in weekdays(TK_FIRST, TK_LAST) if d not in tgt_set]
missing_all = [d for d in sx_expected if d not in sx_dates]
missing_res = [d for d in missing_all if RESEARCH[0] <= d <= RESEARCH[1]]
print(f"SX5E: {len(stoxx_files)} saved files, {len(sx_dates)} distinct dates; window dates "
      f"{len([d for d in sx_dates if TK_FIRST <= d <= TK_LAST])}; missing vs weekdays-TGT: "
      f"{len(missing_all)} (research window {len(missing_res)})")
me_res = [date.fromisoformat(d) for _, d in me_rows if RESEARCH[0] <= date.fromisoformat(d)]
sx_me_ok = [(me.isoformat(), max((d for d in sx_dates if d < me), default=None)) for me in me_res]
print(f"  research month-ends with the last SX5E close before ME: {sx_me_ok}")

# ------------------------------------------------------------------ 9. event-set sizes
full_set = set(C.FX_FULL_SESSIONS)
ewset = set(C.EW_BANK_HOLIDAYS)
ldnrev = [d for _, d in C.MONTH_ENDS if d in full_set and d not in ewset]
ldnmom = [d for d in C.FX_FULL_SESSIONS if d not in ewset]
ecbfix = [d for d in C.FX_FULL_SESSIONS if d not in set(C.TGT_CLOSING_DAYS)]
tkypre = [d for d in C.GOTOBI_OR_TOKYO_MONTH_END if d in full_set]
tkypost = [d for d in C.TOKYO_BUSINESS_DAYS if d in full_set]
mehedge = [d for mo, d in C.MONTH_ENDS if d in full_set and d not in ewset
           and next((r for r in table if r[0] == mo), (None, None, None))[2] not in (None, 0)]


def rw(xs):
    return len([d for d in xs if "2025-04-01" <= d <= "2026-06-19"])


print("event sets (all / research):", {"ldnrev": (len(ldnrev), rw(ldnrev)),
                                       "ldnmom": (len(ldnmom), rw(ldnmom)),
                                       "ecbfix": (len(ecbfix), rw(ecbfix)),
                                       "tkypre": (len(tkypre), rw(tkypre)),
                                       "tkypost": (len(tkypost), rw(tkypost)),
                                       "mehedge": (len(mehedge), rw(mehedge))})
print("  ldnrev research dates:", [d for d in ldnrev if d >= "2025-04-01"])
print("  month-ends dropped (halt or E&W):", [(mo, d) for mo, d in C.MONTH_ENDS
                                              if d not in full_set or d in ewset])
# every event date has its clock row
for name, ev_dates, tbl in (("ldnrev/T_L", ldnrev, dict(K.T_L)), ("ldnmom/T_L", ldnmom, dict(K.T_L)),
                            ("ecbfix/T_E", ecbfix, dict(K.T_E)), ("tkypre/T_T", tkypre, dict(K.T_T)),
                            ("tkypost/T_T", tkypost, dict(K.T_T))):
    print(f"  {name}: event dates without a clock row: {[d for d in ev_dates if d not in tbl]}")
print("FINDINGS:", findings or "none: every table recomputed equal")
