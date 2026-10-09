"""Fill counts/2%-checks/flags into the livestock calendar using data.hist_calendar's parser (read only)."""
import json, hashlib
from datetime import date, timedelta
from pathlib import Path
from data.hist_calendar import parse_hist_calendar
import data.calendars.livestock as FROZEN

OUT = Path("/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e16_calendars/hist2010_livestock.json")
SCR = Path("/tmp/claude-1000/-home-kiros-li-Documents-GitHub-PropExperiment/4a9d3866-b27d-4996-9f9a-acc98193de69/scratchpad")
d = json.loads(OUT.read_text())
d["counts"] = {}
tmp = SCR / "livestock_copy.json"; tmp.write_text(json.dumps(d, indent=1, ensure_ascii=False) + "\n")
cal = parse_hist_calendar(tmp.read_bytes(), "livestock", tmp)

def wk(a, b):
    return [a + timedelta(n) for n in range((b - a).days + 1) if (a + timedelta(n)).weekday() < 5]

def share(a, b):
    w = wk(a, b)
    trade = [x for x in w if cal.is_trade_date(x) or x in cal.unsourced]
    u = [x for x in w if x in cal.unsourced]
    return {"window": [str(a), str(b)], "weekdays": len(w), "trade_dates_incl_unsourced": len(trade),
            "unsourced": len(u), "share_of_weekdays": round(len(u) / len(w), 5),
            "share_of_trade_dates": round(len(u) / len(trade), 5)}

srcs = d["sources"]
dorman = {k for k, v in srcs.items() if v["kind"] == "broker-hosted CME PDF"}
images = {k for k, v in srcs.items() if v["kind"].startswith("broker page (image")}
def sens(excl, years_lost):
    days = set(cal.unsourced)
    for e in d["entries"]:
        if e["source"] in excl and e["name"] != "Regular Monday open (first session of the week)":
            days.add(date.fromisoformat(e["day"]))
    for f in d["no_entry_findings"]:
        if f["source"] in excl:
            days.add(date.fromisoformat(f["day"]))
    for y in years_lost:
        days |= {x for x in wk(date(y, 1, 1), date(y, 12, 31)) if date(2010, 6, 1) <= x <= date(2019, 5, 31)}
    w = wk(date(2010, 6, 1), date(2019, 5, 31))
    return {"unsourced": len(days & set(w)), "share_of_weekdays": round(len(days & set(w)) / len(w), 5)}

lo, hi = date(2019, 5, 1), date(2019, 5, 31)
fz = {str(k): [v.kind.name, None if v.halt_ct is None else str(v.halt_ct)[:5]] for k, v in FROZEN.HOLIDAYS.items() if lo <= k <= hi}
mn = {str(k): [v.kind.name, None if v.halt_ct is None else str(v.halt_ct)[:5]] for k, v in cal.holidays.items() if lo <= k <= hi}
fs = [s for s in FROZEN.SESSIONS if s.valid_from <= hi and (s.valid_to is None or s.valid_to >= lo)]
ms = [s for s in cal.sessions if s.valid_from <= hi and (s.valid_to is None or s.valid_to >= lo)]
overlap = {"window": [str(lo), str(hi)], "frozen_entries": fz, "my_entries": mn, "entries_equal": fz == mn,
           "frozen_late_opens": len(getattr(FROZEN, "LATE_OPENS", {}) or {}),
           "my_late_opens_in_window": [str(k) for k in cal.scheduled_late_opens if lo <= k <= hi],
           "segments_equal": [s.segments for s in fs] == [s.segments for s in ms],
           "day_session_ct_equal": [s.day_session_ct for s in fs] == [s.day_session_ct for s in ms],
           "frozen_sha256": hashlib.sha256(Path(FROZEN.__file__).read_bytes()).hexdigest()}
c = dict(cal.counts)
c.pop("file_counts", None)
c["two_pct_check"] = {
    "coverage": share(date(2010, 6, 1), date(2019, 5, 31)),
    "e14_window": share(date(2010, 6, 7), date(2019, 4, 30)),
    "LE_window_U2": share(date(2010, 7, 1), date(2019, 4, 30)),
    "HE_window_U2": share(date(2017, 7, 3), date(2019, 4, 30)),
    "rule": "at most 2% of window weekdays unsourced (brief_calendars.md (a))",
    "sensitivity_if_broker_hosted_CME_PDFs_rejected": sens(dorman, [2010, 2011, 2012]),
    "sensitivity_if_image_transcriptions_rejected": sens(images, []),
}
c["overlap_2019_05_vs_frozen_livestock_py"] = overlap
d["counts"] = c
d["flags_for_lead"] = [
    "Grading: broker/vendor copies of CME schedules graded 'secondary' (precedent: data/calendars/livestock.py grades an AMP Futures image of a CME schedule 'secondary'); CME self-certifications fetched from cftc.gov graded 'cme'. Dorman Trading re-hosts CME's own holiday PDFs: if the lead treats these as 'mirrors' of cmegroup.com (brief_common.md), see counts.two_pct_check.sensitivity_if_broker_hosted_CME_PDFs_rejected.",
    "Year coverage 2013 and 2014 rests on the holiday set the other years' full-year lists show (no 2013/2014 full-year list found outside CME's site); 2015-2019 on NYSE lists (Wayback), 2010-2012 on CME floor holiday cards (broker-hosted).",
    "2016-2019 holiday statuses come from schedule images on cannontrading.com read visually (no OCR tool installed); see sensitivity_if_image_transcriptions_rejected.",
    "Thursday-before-Good-Friday 13:55 closes (2012, 2013, 2014, 2015) and 2015-12-31 13:55 are recorded as early_halt because CME's schedules call them 'Early Close', although 13:55 is after the 13:00 settlement; lead spec section 2 then excludes them as action dates.",
    "2012-07-03: the Globex schedule (updated 6/18/2012) says regular close for livestock, the 2012 floor card (late 2011) says commodities close at 12:00 on the floor; recorded as a regular Globex day (no_entry_finding); the settlement minute that day may have followed the floor.",
    "2012-12-24 and 2010-12-31: early-close status from floor cards; Globex halt minute 12:15 (2012, inferred) and 12:00 (2010, unverified).",
    "2017-01-17: Cannon's MLK 2017 table shows a 09:05 Tuesday livestock open, against the 08:30 open in force; kept as a late open with time unverified.",
    "Eras 1-2 (to 2016-02-26): Mondays open 09:05 (295 late_open entries incl. post-holiday ones); Friday Globex close 13:55 and era-1 evening segments are not representable in SessionSpec (notes_for_e17).",
    "day_session_ct: era 1 (09:05, 13:00), era 2 (08:00, 13:00), era 3 (08:30, 13:00). Era 2's 08:00 is the Globex open; the futures pit opened 09:05 until 2015-07-02. H4's O_p in era 2 is a lead call.",
]
d["notes_for_e17"] = [
    "data.hist_calendar.parse_hist_calendar(raw, 'livestock', path) accepts this file as is (verified 2026-10-09 on a scratch copy; nothing written under data/). load_hist_group_calendar('livestock') refuses because HIST_GROUPS = ('equity','rates','fx','energy','metals','grains') is hardcoded and hist_calendar_path checks it: E.17 must add 'livestock' to HIST_GROUPS and copy this file to data/calendars/hist2010/livestock.json (the products check uses data.calendars.GROUP_OF_PRODUCT, which already maps HE and LE to 'livestock').",
    "Weekday-dependent sessions before 2016-02-29 (Monday 09:05 opens, Friday 13:55 closes) are not expressible in SessionSpec: Mondays are late_open entries; Friday closes are not entries (an early_halt would exclude every Friday under lead spec section 2). Bar checks must allow no bars 13:55-16:00 CT on Fridays in eras 1-2 and must not expect Sunday-evening bars in era 1.",
    "Era 1 post-holiday evening segments: where a schedule says livestock reopened at 1700 CT the evening before (2010 and early-2011 Monday holidays, Thanksgiving 2010-2012) the regular segment applies; where it says 0905 the day carries a late_open entry.",
    "late_open entries are not exclusions under lead spec section 2 (only early halts, halts and unsourced dates are); E.17 should take max(O_p, open_ct) for H4's entry minute.",
]
OUT.write_text(json.dumps(d, indent=1, ensure_ascii=False) + "\n")
tmp.write_text(OUT.read_text())
cal2 = parse_hist_calendar(tmp.read_bytes(), "livestock", tmp)
print("reparse ok; sha256", hashlib.sha256(OUT.read_bytes()).hexdigest())
print(json.dumps(c["two_pct_check"]))
print(json.dumps(overlap))
