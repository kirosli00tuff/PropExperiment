"""Stage E.16 Task 3b(a): livestock hist calendar 2010-06-01..2019-05-31 (schema e14_hist_calendar/1).

Every text quote is extracted by regex from the saved page text and so is verbatim (whitespace
normalized). Image sources carry a transcription made by reading the saved image.
"""
import csv
import hashlib
import json
import re
import sys
from datetime import date, timedelta
from pathlib import Path

REPO = Path("/home/kiros-li/Documents/GitHub/PropExperiment")
PAGES = REPO / "reports/stage_e16_briefs/pages/livestock"
OUT = REPO / "reports/stage_e16_calendars/hist2010_livestock.json"
FIRST, LAST = date(2010, 6, 1), date(2019, 5, 31)
ERA2_START, ERA3_START = date(2014, 10, 27), date(2016, 2, 29)
PRODUCTS = ["HE", "LE"]

# ------------------------------------------------------------------ fetch logs -> sources
LOGS = {}
for log in PAGES.rglob("*fetch_rows.tsv"):
    for row in csv.reader(log.open(), delimiter="\t"):
        if len(row) >= 5:
            name, url, t, code, sha = row[:5]
            LOGS[(log.parent / name).resolve()] = (url, t, code, sha)

SOURCES, TEXT = {}, {}


def norm(s):
    s = s.replace("­", "").replace("·", " ").replace("•", " ").replace("‐", "-")
    s = re.sub("[-]", " ", s)
    return re.sub(r"\s+", " ", s)


def src(sid, rel, title, grade, kind, text_rel=None, capture=None, terms=""):
    path = (PAGES / rel).resolve()
    if not path.is_file():
        sys.exit(f"missing source file {rel}")
    url, fetched, code, sha_log = LOGS.get(path, (None, None, None, None))
    sha = hashlib.sha256(path.read_bytes()).hexdigest()
    if sha_log and sha_log != sha:
        sys.exit(f"sha mismatch {rel}")
    if url is None:
        sys.exit(f"no fetch-log row for {rel}")
    SOURCES[sid] = {"url": url, "capture": capture, "fetched_utc": fetched,
                    "saved_file": str(path.relative_to(REPO)), "sha256": sha, "title": title,
                    "grade": grade, "kind": kind, "terms": terms}
    if text_rel:
        TEXT[sid] = norm((PAGES / text_rel).read_text(encoding="utf8", errors="replace"))


def q(sid, *pats):
    """Verbatim quote(s) from a text source; several patterns joined with ' [...] '."""
    out = []
    for p in pats:
        m = re.search(p, TEXT[sid], re.I)
        if not m:
            sys.exit(f"quote not found: {sid} /{p}/")
        out.append(m.group(0).strip())
    return " [...] ".join(out)


T_CFTC = "cftc.gov web policy: public domain (E.14 terms_checks.md row); plain curl of single filings"
T_DORMAN = ("dormantrading.com: robots.txt 'User-agent: * Disallow:' (allows all); no terms-of-use "
            "page found (footer links: Risk Disclosure, Privacy Policy, Barchart data disclaimer); "
            "no automated-access prohibition found")
T_CANNON = ("cannontrading.com: robots.txt User-agent * disallows only listed paths (not "
            "/tools/support-resistance-levels/ or /community/newsletter/); no terms-of-use page "
            "found (footer: Risk Disclosure); no automated-access prohibition found")
T_NYSE = "web.archive.org capture (archive.org terms checked in E.14 terms_checks.md)"
T_FIA = ("fia.org Website Terms and Conditions read (saved other/fia_website-terms-and-"
         "conditions.html): personal non-commercial copies permitted; no automated-access clause")
T_AMP = "ampfutures.com robots.txt allows *; no terms-of-use page found (only Privacy statement)"

CME_HOSTED = "a CME Group schedule document re-hosted by a broker (Dorman Trading)"

# filings (CME self-certifications hosted by the CFTC)
src("f14_408", "ptc102314cmedcm034.pdf", "CME Submission No. 14-408 (filed 2014-10-09): reduction of "
    "CME Globex trading hours for livestock futures, effective Monday 2014-10-27", "cme",
    "CME filing on cftc.gov", "ptc102314cmedcm034.txt", terms=T_CFTC)
src("f16_064", "ptc021116cmedcm001.pdf", "CME Submission No. 16-064 (filed 2016-02-10): amended "
    "livestock trading hours effective Monday 2016-02-29", "cme", "CME filing on cftc.gov",
    "ptc021116cmedcm001.txt", terms=T_CFTC)
src("f15_opt", "ptc060315cmedcm001.pdf", "CME submission (filed 2015-06-03): livestock options "
    "floor hours effective 2015-07-06; states the current CME Globex livestock hours",
    "cme", "CME filing on cftc.gov", "ptc060315cmedcm001.txt", terms=T_CFTC)
src("f08_159", "rul101708cme001.pdf", "CME Submission #08-159: Friday Globex close for livestock "
    "1:30 p.m. -> 1:55 p.m. effective 2008-10-24", "cme", "CME filing on cftc.gov",
    "rul101708cme001.txt", terms=T_CFTC)
src("nadex14", "rul040914nadex001.pdf", "Nadex notice of emergency action (CFTC-hosted), "
    "2014-04-08 CME Globex corn halt", "secondary", "exchange filing on cftc.gov",
    "rul040914nadex001.txt", terms=T_CFTC)
src("lean", "lean_market-hours-database.json", "QuantConnect LEAN market-hours-database.json "
    "(vendor dataset, Apache-2.0); entries Future-cme-LE / Future-cme-HE", "unverified",
    "vendor dataset (cross-check only, never evidence)", terms="GitHub public repo, Apache-2.0")

DOR = [  # (sid, file stem, title)
    ("floor2010", "2010floorholidaycard", "CME Group Chicago Trading Floor Holiday Schedule for 2010 (dated 11/16/2010)"),
    ("floor2011", "2011floorholidaycard", "CME Group Chicago Trading Floor Holiday Schedule for 2011 (dated 11/30/2010)"),
    ("floor2012", "2012floorholidaycard", "CME Group Chicago Trading Floor Holiday Schedule for 2012"),
    ("d10_jul4", "2010-4th-of-july", "CME Globex Fourth of July 2010 schedule"),
    ("d10_labor", "2010-labor-day", "CME Globex Labor Day 2010 schedule"),
    ("d10_columbus", "2010-columbus-day", "CME Globex Columbus Day 2010 schedule"),
    ("d10_veterans", "2010-veterans-day", "CME Globex Veterans Day 2010 schedule"),
    ("d10_thanks", "2010-thanksgiving", "CME Globex Thanksgiving 2010 schedule"),
    ("d11_mlk", "2011-martin-luther-king", "CME Globex MLK 2011 schedule"),
    ("d11_pres", "2011-presidents-day", "CME Globex Presidents Day 2011 schedule"),
    ("d11_gf", "2011-good-friday", "CME Globex Good Friday 2011 schedule"),
    ("d11_mem", "2011-memorial-day", "CME Globex Memorial Day 2011 schedule"),
    ("d11_jul4", "2011-4th-of-july", "CME Globex Fourth of July 2011 schedule"),
    ("d11_labor", "2011-labor-day", "CME Globex Labor Day 2011 schedule"),
    ("d11_columbus", "2011-columbus-day", "CME Globex Columbus Day 2011 schedule"),
    ("d11_veterans", "2011-veterans-day", "CME Globex Veterans Day 2011 schedule"),
    ("d11_thanks", "2011-thanksgiving", "CME Globex Thanksgiving 2011 schedule"),
    ("d11_xmas", "2011-christmas", "CME Globex Christmas 2011 schedule"),
    ("d12_ny", "2012-new-years", "CME Globex New Year's 2012 schedule"),
    ("d12_mlk", "2012-martin-luther-king", "CME Globex MLK 2012 schedule"),
    ("d12_pres", "2012-presidents-day", "CME Globex Presidents Day 2012 schedule"),
    ("d12_gf", "2012-good-friday", "CME Globex Good Friday 2012 schedule"),
    ("d12_mem", "2012-memorial-day", "CME Globex Memorial Day 2012 schedule"),
    ("d12_jul4", "2012-4th-of-july", "CME Globex Fourth of July 2012 schedule (last updated 6/18/2012)"),
    ("d12_labor", "2012-labor-day", "CME Globex Labor Day 2012 schedule"),
    ("d12_columbus", "2012-columbus-day", "CME Globex Columbus Day 2012 schedule"),
    ("d12_veterans", "2012-veterans-day", "CME Globex Veterans Day 2012 schedule"),
    ("d12_thanks", "2012-thanksgiving", "CME Globex Thanksgiving 2012 schedule"),
    ("d13_ny", "2013-new-years", "CME Globex New Year's 2013 schedule"),
    ("d13_pres", "2013-presidents-day", "CME Globex Presidents Day 2013 schedule"),
    ("d13_mem", "2013-memorial-day", "CME Globex Memorial Day 2013 schedule"),
    ("d13_labor", "2013-labor-day", "CME Globex Labor Day 2013 schedule"),
    ("d13_veterans", "2013-veterans-day", "CME Globex Veterans Day 2013 schedule"),
    ("d13_thanks", "2013-thanksgiving", "CME Globex Thanksgiving 2013 schedule"),
    ("d13_xmas", "2013-christmas", "CME Globex Christmas 2013 schedule"),
    ("d14_gf", "2014-good-friday-holiday-schedule", "CME Globex Good Friday 2014 schedule"),
    ("d14_mem", "2014-memorial-day-holiday-schedule", "CME Globex Memorial Day 2014 schedule"),
]
for sid, stem, title in DOR:
    src(sid, f"dorman/{stem}.pdf", title + " [" + CME_HOSTED + "]", "secondary",
        "broker-hosted CME PDF", f"dorman/{stem}.txt", terms=T_DORMAN)

CAN = [  # (sid, slug, title)
    ("c11_jul4", "futures-trading-levels-independence-day-weekend-trading-schedule", "Cannon Trading: Independence Day 2011 schedule (post 2011-06-29)"),
    ("c11_labor", "labor-day-2011-holiday-futures-trading-hours", "Cannon Trading: Labor Day 2011 (post 2011-09-02)"),
    ("c11_thanks", "thanksgiving-2011-futures-trading-hours-and-holiday-trading-schedule", "Cannon Trading: Thanksgiving 2011 (post 2011-11-19)"),
    ("c12_mlk", "martin-luther-king-jr-day-trading-schedule", "Cannon Trading: MLK 2012 (post 2012-01-13)"),
    ("c12_pres", "presidents-day-futures-trading-hours-and-holiday-trading-schedule", "Cannon Trading: Presidents Day 2012 (post 2012-02-17)"),
    ("c12_gf", "good-friday-holiday-trading-schedule", "Cannon Trading: Good Friday 2012 (post 2012-04-04)"),
    ("c12_jul4", "independence-day-trading-schedule-for-4th-of-july-2012", "Cannon Trading: Independence Day 2012 (post 2012-06-29)"),
    ("c12_sandy1", "trading-levels-and-reports-for-10-30-2012", "Cannon Trading: daily post 2012-10-29 (Hurricane Sandy)"),
    ("c12_sandy2", "trading-levels-and-reports-for-october-31-2012", "Cannon Trading: daily post 2012-10-30 (Hurricane Sandy)"),
    ("c13_gf", "good-friday-futures-trading-schedule", "Cannon Trading: Good Friday 2013 (post 2013-03-27)"),
    ("c13_mem", "memorial-day-futures-trading-schedule", "Cannon Trading: Memorial Day 2013 (post 2013-05-22)"),
    ("c13_jul4", "fourth-of-july-futures-trading-schedule", "Cannon Trading: Fourth of July 2013 (post 2013-07-01)"),
    ("c13_thanks", "thanksgiving-holiday-futures-trading-schedule-2013", "Cannon Trading: Thanksgiving 2013 (post 2013-11-22)"),
    ("c13_xmas", "christmas-holiday-futures-trading-schedule-2013", "Cannon Trading: Christmas 2013 (post 2013-12-19)"),
    ("c14_ny", "new-years-2014", "Cannon Trading: New Years 2014 (post 2013-12-27)"),
    ("c14_pres", "presidents-day-2014-futures-trading-holiday-schedule", "Cannon Trading: Presidents Day 2014 (post 2014-02-14)"),
    ("c14_jul4", "independence-day-july-4th-2014-futures-trading-holiday-hours-cme-globex-ice-exchanges", "Cannon Trading: Independence Day 2014 (post 2014-06-26)"),
    ("c15_presd", "futures-levels-economic-reports-2-13-2015", "Cannon Trading: daily post 2015-02-12 with the Presidents Day 2015 summary 'From the CME Globex Control Center'"),
    ("c15_mlk", "martin-luther-king-day-futures-trading-schedule-2015", "Cannon Trading: MLK 2015 (post 2015-01-15)"),
    ("c15_pres", "presidents-day-holiday-day-futures-trading-schedule-2015", "Cannon Trading: Presidents Day 2015 (post 2015-02-12)"),
    ("c15_gf", "good-friday-holiday-futures-trading-schedule-2015", "Cannon Trading: Good Friday 2015 (post 2015-03-31)"),
    ("c15_mem", "memorial-day-holiday-globex-ice-futures-holiday-schedule-2015", "Cannon Trading: Memorial Day 2015 (post 2015-05-20)"),
    ("c15_jul4", "fourth-july-holiday-globex-ice-futures-holiday-schedule-2015", "Cannon Trading: Fourth of July 2015 (post 2015-06-30)"),
    ("c15_labor", "labor-day-holiday-globex-ice-futures-trading-schedule-2015", "Cannon Trading: Labor Day 2015 (post 2015-09-03)"),
    ("c15_thanks", "globex-ice-futures-thanksgiving-holiday-schedule-2015", "Cannon Trading: Thanksgiving 2015 (post 2015-11-19)"),
    ("c15_xmas", "christmas-holiday-globex-ice-futures-holiday-schedule-2015", "Cannon Trading: Christmas 2015 (post 2015-12-18)"),
    ("c16_ny", "new-years-2016-globex-ice-futures-holiday-schedule-2015-2016", "Cannon Trading: New Years 2016 (post 2015-12-30)"),
    ("c16_mlk", "martin-luther-king-globex-ice-futures-holiday-schedule-2016", "Cannon Trading: MLK 2016 (post 2016-01-13)"),
    ("c16_pres", "globex-ice-presidents-day-holiday-schedule-2016", "Cannon Trading: Presidents Day 2016 (post 2016-02-10)"),
    ("c16_mem", "globex-ice-memorial-day-holiday-trading-schedule-2016", "Cannon Trading: Memorial Day 2016 (post 2016-05-25)"),
    ("c16_jul4", "globex-ice-independence-day-holiday-trading-schedule-2016", "Cannon Trading: Independence Day 2016 (post 2016-06-30)"),
    ("c16_labor", "globex-ice-labor-day-holiday-schedule-2016", "Cannon Trading: Labor Day 2016 (post 2016-08-31)"),
    ("c16_thanks", "globex-ice-thanksgiving-holiday-schedule-2016", "Cannon Trading: Thanksgiving 2016 (post 2016-11-18)"),
    ("c16_xmas", "christmas-holiday-schedule-december-2016-cme-globex-ice-exchanges", "Cannon Trading: Christmas 2016 (post 2016-12-16)"),
    ("c17_ny", "new-years-2017-day-holiday-schedule-cme-globex-ice-exchanges", "Cannon Trading: New Years 2017 (post 2016-12-28)"),
]
for sid, slug, title in CAN:
    src(sid, f"cannon/{slug}.html", title, "secondary", "broker page (text)", f"cannon/{slug}.txt",
        terms=T_CANNON)
src("c14_mlk", "cannon/2014-cme-group-MLK-schedule.pdf", "CME Globex MLK 2014 schedule table "
    "[CME schedule re-hosted by Cannon Trading, /community/newsletter/]", "secondary",
    "broker-hosted CME PDF", "cannon/2014-cme-group-MLK-schedule.txt", terms=T_CANNON)

IMG = {  # sid: (file, post slug, title)
    "i16_gf": ("gf2016.png", "Good Friday 2016 schedule table (Cannon post 2016-03-22)"),
    "i17_mlk": ("mlk2017.png", "MLK 2017 schedule table (Cannon post 2017-01-12)"),
    "i17_pres": ("pres2017.png", "Presidents Day 2017 schedule table (Cannon post 2017-02-16)"),
    "i17_gf": ("gf2017.jpg", "Good Friday 2017 schedule table (Cannon post 2017-04-12)"),
    "i17_mem": ("mem2017.jpg", "Memorial Day 2017 schedule table (Cannon post 2017-05-24)"),
    "i17_jul4": ("jul2017.jpg", "Independence Day 2017 schedule table (Cannon posts 2017-06-28/29)"),
    "i17_labor": ("lab2017.png", "Labor Day 2017 schedule table (Cannon post 2017-08-30)"),
    "i17_thanks": ("thx2017.png", "Thanksgiving 2017 schedule table (Cannon post 2017-11-17)"),
    "i17_xmas": ("xmas2017.png", "Christmas 2017 schedule table (Cannon post 2017-12-18)"),
    "i18_ny": ("ny2018a.png", "New Years 2018 schedule table (Cannon post 2017-12-28)"),
    "i18_mlk": ("mlk2018.jpg", "MLK 2018 schedule table (Cannon post 2018-01-11)"),
    "i18_pres": ("pres2018.jpg", "Presidents Day 2018 schedule table (Cannon post 2018-02-15)"),
    "i18_gf": ("gf2018.jpg", "Good Friday 2018 schedule table (Cannon post 2018-03-27)"),
    "i18_mem": ("mem2018.png", "Memorial Day 2018 schedule table (Cannon post 2018-05-23)"),
    "i18_jul4": ("jul2018.jpg", "Independence Day 2018 schedule table (Cannon post 2018-06-27)"),
    "i18_labor": ("lab2018.png", "Labor Day 2018 schedule table (Cannon post 2018-08-29)"),
    "i18_thanks": ("thx2018.png", "Thanksgiving 2018 schedule table (Cannon post 2018-11-16)"),
    "i18_xmas": ("xmas2018.png", "Christmas 2018 table (Cannon post 2018-12-18)"),
    "i19_ny": ("ny2019.gif", "New Years 2019 schedule table (Cannon post 2018-12-28)"),
    "i19_mlk": ("mlk2019.png", "MLK 2019 schedule table (Cannon post 2019-01-16)"),
    "i19_pres": ("pres2019.png", "Presidents Day 2019 schedule table (Cannon post 2019-02-13)"),
    "i19_gf": ("gf2019.gif", "Good Friday 2019 schedule table, low-resolution GIF (Cannon post 2019-04-11)"),
    "i19_mem": ("mem2019.png", "Memorial Day 2019 schedule table (Cannon post 2019-05-21)"),
}
for sid, (fn, title) in IMG.items():
    src(sid, f"cannon/img/{fn}", "Cannon Trading image: " + title, "secondary",
        "broker page (image; transcribed by reading)", terms=T_CANNON)

for sid, ts, title in [("nyse15", "20150106155052", "NYSE holidays 2015-2016"),
                       ("nyse16", "20160108005018", "NYSE holidays 2015-2016"),
                       ("nyse17", "20170102054744", "NYSE holidays 2016-2017"),
                       ("nyse18", "20180101202300", "NYSE holidays 2017-2019"),
                       ("nyse19", "20190107231452", "NYSE holidays 2019-2021")]:
    src(sid, f"nyse/wb{ts}_nyse_hours-calendars.html", "Wayback capture of nyse.com/markets/"
        "hours-calendars: " + title, "secondary", "exchange holiday list (NYSE), universe check",
        f"nyse/wb{ts}_nyse_hours-calendars.txt", capture=ts, terms=T_NYSE)
src("fia18", "other/www.fia.org_fia_articles_market-information-national-day-mourning-wednesday-"
    "december-5-2018.html", "FIA market information: National Day of Mourning 2018-12-05",
    "secondary", "industry association notice", "other/www.fia.org_fia_articles_market-information-"
    "national-day-mourning-wednesday-december-5-2018.txt", terms=T_FIA)
src("amp18", "other/www.ampfutures.com_news_us-national-day-of-mourning-on-5th-december-2018-"
    "amended-trading-hours.html", "AMP Futures: trading hours for the National Day of Mourning "
    "2018-12-05", "secondary", "broker page (text)", "other/www.ampfutures.com_news_us-national-"
    "day-of-mourning-on-5th-december-2018-amended-trading-hours.txt", terms=T_AMP)

# ------------------------------------------------------------------ entries
ENTRIES, FIND, UNSOURCED = [], [], []


def ent(day, name, kind, sid, quote, ev="secondary", tev=None, halt=None, opn=None, tq=None,
        note=""):
    if tev is None:
        tev = "n/a" if kind == "full_closure" else "secondary"
    ENTRIES.append({"day": day, "name": name, "kind": kind, "halt_ct": halt, "open_ct": opn,
                    "evidence": ev, "time_evidence": tev, "source": sid, "status_quote": quote,
                    "time_quote": tq, "note": note})


def find(day, name, finding, sid, quote, ev="secondary"):
    FIND.append({"day": day, "name": name, "finding": finding, "evidence": ev, "source": sid,
                 "quote": quote})


def uns(day, reason):
    UNSOURCED.append({"day": day, "reason": reason})


IMGQ = "[transcribed from image] "
C, H, L = "full_closure", "early_halt", "late_open"
MON_HOL = "Monday holiday: livestock closed until its Tuesday open"

# ---- 2010 (from 2010-06-01)
ent("2010-07-05", "Independence Day (observed)", C, "d10_jul4",
    q("d10_jul4", r"Dairy, Crude Palm Oil, Livestock, GSCI, Lumber and Weather products will remain closed until 1700 CT on Monday"),
    note="Globex livestock reopened 17:00 CT Monday for trade date Tuesday (regular evening segment)")
find("2010-07-02", "Friday before Independence Day", "regular close", "d10_jul4",
     q("d10_jul4", r"Regular Close . Per each product schedule for trade date Friday July 2 (?:for: )?Livestock"))
ent("2010-09-06", "Labor Day", C, "d10_labor",
    q("d10_labor", r"Dairy, Crude Palm Oil, Livestock, GSCI, Lumber and Weather products will remain closed until 1700 CT on Monday"))
find("2010-10-11", "Columbus Day", "regular session (Monday open per product schedule)", "d10_columbus",
     q("d10_columbus", r"Exceptions: Livestock, Domestic Dairy, TRAKRS and ETFs will remain closed until their regularly scheduled open on Monday"))
find("2010-11-11", "Veterans Day", "regular session", "d10_veterans",
     q("d10_veterans", r"Thursday, Nov 11 Regular Close . Per each product schedule for trade date Thursday, Nov 11"))
ent("2010-11-25", "Thanksgiving Day", C, "d10_thanks",
    q("d10_thanks", r"Livestock, GSCI, Crude Palm Oil and Weather will remain closed until their open at 1700 CT on Thursday Nov 25"))
ent("2010-11-26", "Day after Thanksgiving", H, "d10_thanks",
    q("d10_thanks", r"1200 CT . Early CME Globex close for CME Agricultural Futures"), halt="12:00",
    tq=q("d10_thanks", r"1200 CT . Early CME Globex close for CME Agricultural Futures, CBOT Grain Futures & Options"),
    note="time stated for 'CME Agricultural Futures' (livestock are CME agricultural futures); floor card 2010 also 12:00 for commodities")
find("2010-12-23", "Thursday before Christmas (observed Friday)", "floor: commodities regular (only FX and interest rates close early)",
     "floor2010", q("floor2010", r"Thursday, December 23, 2010 Christmas Day Friday, December 24, 2010 Foreign Exchange & Interest Rates close at 12:00 p.m."))
ent("2010-12-24", "Christmas Day (observed)", C, "floor2010",
    q("floor2010", r"DATE ON WHICH CME GROUP TRADING FLOORS"), note=(
        "floor card lists Friday, December 24, 2010 as the Christmas Day date on which CME Group "
        "trading floors are closed (" + q("floor2010", r"Christmas Day Friday, December 24, 2010") +
        "); Globex livestock statement for 2010-12-24 not found outside CME's site; status rests "
        "on the floor closure (livestock settled from the pit in 2010)"))
ent("2010-12-31", "Friday before New Year's Day 2011 (Saturday)", H, "floor2011",
    q("floor2011", r"Friday, December 31, 2010 Foreign Exchange, Interest Rates, Commodities, Weather &.{0,40}?Real Estate close at 12:00 p\.m\."),
    halt="12:00", tev="unverified",
    tq=q("floor2011", r"Commodities, Weather &.{0,40}?Real Estate close at 12:00 p\.m\."),
    note=("12:00 is the floor time for commodities (floor card dated 11/30/2010); the Globex "
          "livestock halt minute is not established outside CME's site (the LEAN vendor table has "
          "12:15); 12:00 kept as the earlier, conservative cut"))

# ---- 2011
ent("2011-01-17", "Martin Luther King Jr. Day", C, "d11_mlk",
    q("d11_mlk", r"Dairy, Crude Palm Oil, Livestock, GSCI, Lumber and Weather products will remain closed until 1700 CT on Monday"))
ent("2011-02-21", "Presidents' Day", C, "d11_pres",
    q("d11_pres", r"Dairy, Crude Palm Oil, Livestock, GSC, Lumber and Weather products will remain closed until 1700 CT on Monday"))
find("2011-04-21", "Thursday before Good Friday", "regular close", "d11_gf",
     q("d11_gf", r"Thursday, Apr 21 Regular Close . Per each product schedule for trade date Thursday, Apr 21 (?:for: )?Livestock"))
ent("2011-04-22", "Good Friday", C, "d11_gf", q("d11_gf", r"Friday, Apr 22 CME Globex is closed"))
ent("2011-05-30", "Memorial Day", C, "d11_mem",
    q("d11_mem", r"Dairy, Crude Palm Oil, Livestock, GSCI, Lumber, and Weather products will remain closed until 1700 CT on Monday"))
ent("2011-07-04", "Independence Day", C, "d11_jul4",
    q("d11_jul4", r"Livestock will remain closed until its scheduled opening 0905 CT on Tuesday"))
ent("2011-07-05", "Tuesday after Independence Day", L, "d11_jul4",
    q("d11_jul4", r"Livestock will remain closed until its scheduled opening 0905 CT on Tuesday"), opn="09:05",
    tq=q("d11_jul4", r"scheduled opening 0905 CT on Tuesday"),
    note="Cannon's text post (c11_jul4) lists livestock among products closed Monday; agrees")
ent("2011-09-05", "Labor Day", C, "d11_labor",
    q("d11_labor", r"Livestock will remain closed until its scheduled opening 0905 CT on Tuesday"))
ent("2011-09-06", "Tuesday after Labor Day", L, "d11_labor",
    q("d11_labor", r"Livestock will remain closed until its scheduled opening 0905 CT on Tuesday"), opn="09:05",
    tq=q("d11_labor", r"scheduled opening 0905 CT on Tuesday"),
    note=("DISAGREEMENT: Cannon's text post c11_labor lists livestock under '5:00 pm Open' on Monday "
          "(" + q("c11_labor", r"5:00 pm Open: Equity, Interest Rate, Foreign Exchange, Dairy, Crude Palm Oil, Livestock") +
          "); the CME schedule (Dorman copy) is product-specific and is followed"))
find("2011-10-10", "Columbus Day", "regular session", "d11_columbus",
     q("d11_columbus", r"Exceptions: Dairy, Crude Palm Oil, Livestock, Lumber, & TRAKR.s will remain closed until their regularly scheduled open on Monday"))
find("2011-11-11", "Veterans Day", "regular session", "d11_veterans",
     q("d11_veterans", r"Friday, Nov 11 Regular CME Globex Close . Per each product schedule for trade date Friday, Nov 11"))
ent("2011-11-24", "Thanksgiving Day", C, "d11_thanks",
    q("d11_thanks", r"Livestock, GSCI, Lumber, Crude Palm Oil and Weather will remain closed until their open at 1700 CT on Thursday Nov 24"))
ent("2011-11-25", "Day after Thanksgiving", H, "d11_thanks",
    q("d11_thanks", r"1200 CT . Early CME Globex close for CME Agricultural Futures"), halt="12:00",
    tq=q("d11_thanks", r"1200 CT . Early CME Globex close for CME Agricultural Futures"),
    note=("Cannon c11_thanks agrees (" + q("c11_thanks", r"12:00 pm Close: Agricultural, CBOT Grain futures & options") +
          "); the LEAN vendor table's 12:15 is not supported"))
find("2011-12-23", "Friday before Christmas (observed Monday)", "regular close", "d11_xmas",
     q("d11_xmas", r"Friday, Dec 23 Regular Close[^.]{0,80}?CME Commodity"))
ent("2011-12-26", "Christmas Day (observed)", C, "d11_xmas",
    q("d11_xmas", r"Monday, Dec 26 Christmas Day Observed . Globex closed"),
    note="schedule-wide closure line; livestock reopens Tuesday 09:05 (next entry)")
ent("2011-12-27", "Tuesday after Christmas (observed)", L, "d11_xmas",
    q("d11_xmas", r"0905 CT Livestock Futures & Options"), opn="09:05",
    tq=q("d11_xmas", r"0905 CT Livestock Futures & Options"))
find("2011-12-30", "Friday before New Year's Day (observed Monday)", "regular close", "d12_ny",
     q("d12_ny", r"Regular Close . Per each product schedule for trade date Friday, Dec 30 (?:for: )?Livestock"))

# ---- 2012
ent("2012-01-02", "New Year's Day (observed)", C, "d12_ny", q("d12_ny", r"Monday, Jan 2 New Years Observed . Globex closed"))
ent("2012-01-03", "Tuesday after New Year's Day (observed)", L, "d12_ny",
    q("d12_ny", r"0905 CT Livestock Futures & Options"), opn="09:05", tq=q("d12_ny", r"0905 CT Livestock Futures & Options"))
ent("2012-01-16", "Martin Luther King Jr. Day", C, "d12_mlk",
    q("d12_mlk", r"Livestock will remain closed until its scheduled opening 0905 CT on Tuesday"),
    note="Cannon c12_mlk agrees: " + q("c12_mlk", r"Closed: Dairy, Crude Palm Oil, GSCI, Weather, CBOT/KCBT/MGEX Grains, Ethanol, Dow UBS ER, Lumber and Livestock products"))
ent("2012-01-17", "Tuesday after MLK Day", L, "d12_mlk",
    q("d12_mlk", r"Livestock will remain closed until its scheduled opening 0905 CT on Tuesday"), opn="09:05",
    tq=q("d12_mlk", r"scheduled opening 0905 CT on Tuesday"))
ent("2012-02-20", "Presidents' Day", C, "d12_pres",
    q("d12_pres", r"Livestock will remain closed until its scheduled opening 0905 CT on Tuesday"),
    note="Cannon c12_pres agrees")
ent("2012-02-21", "Tuesday after Presidents' Day", L, "d12_pres",
    q("d12_pres", r"Livestock will remain closed until its scheduled opening 0905 CT on Tuesday"), opn="09:05",
    tq=q("d12_pres", r"scheduled opening 0905 CT on Tuesday"))
ent("2012-04-05", "Thursday before Good Friday", H, "d12_gf",
    q("d12_gf", r"1355 CT . Early Close for Lumber, Dairy and Livestock"), halt="13:55",
    tq=q("d12_gf", r"1355 CT . Early Close for Lumber, Dairy and Livestock"),
    note="13:55 is after the 13:00 settlement; CME calls it an early close (the regular Thursday Globex close was 16:00). Cannon c12_gf agrees: " + q("c12_gf", r"1:55 pm Close: Lumber, Dairy and Livestock products"))
ent("2012-04-06", "Good Friday", C, "d12_gf", q("d12_gf", r"Friday, Apr 6 CME Globex is closed"))
ent("2012-05-28", "Memorial Day", C, "d12_mem",
    q("d12_mem", r"Livestock will remain closed until its scheduled opening 0905 CT on Tuesday"))
ent("2012-05-29", "Tuesday after Memorial Day", L, "d12_mem",
    q("d12_mem", r"Livestock will remain closed until its scheduled opening 0905 CT on Tuesday"), opn="09:05",
    tq=q("d12_mem", r"scheduled opening 0905 CT on Tuesday"))
find("2012-07-03", "Day before Independence Day", "Globex regular close", "d12_jul4",
     q("d12_jul4", r"Regular Close . Per each product schedule for trade date Tuesday, July 3 (?:for: )?Livestock"))
ent("2012-07-04", "Independence Day", C, "d12_jul4",
    q("d12_jul4", r"Livestock will remain closed until its scheduled opening 0905 CT on Thursday"),
    note="Cannon c12_jul4 agrees")
ent("2012-07-05", "Thursday after Independence Day", L, "d12_jul4",
    q("d12_jul4", r"Livestock will remain closed until its scheduled opening 0905 CT on Thursday"), opn="09:05",
    tq=q("d12_jul4", r"scheduled opening 0905 CT on Thursday"))
ent("2012-09-03", "Labor Day", C, "d12_labor",
    q("d12_labor", r"Livestock will remain closed until its scheduled opening 0905 CT on Tuesday"))
ent("2012-09-04", "Tuesday after Labor Day", L, "d12_labor",
    q("d12_labor", r"Livestock will remain closed until its scheduled opening 0905 CT on Tuesday"), opn="09:05",
    tq=q("d12_labor", r"scheduled opening 0905 CT on Tuesday"))
find("2012-10-08", "Columbus Day", "regular session", "d12_columbus",
     q("d12_columbus", r"Exceptions: Livestock & Lumber will remain closed until their regularly scheduled open on Monday"))
find("2012-10-29", "Hurricane Sandy (day 1)", "regular session (closures limited to equity index and interest rate products)",
     "c12_sandy1", q("c12_sandy1", r"Hurricane Sandy shut down the NYSE and in return CME and ICE shut down trading on stock index futures earlier this morning and then shut down interest rates earlier than normal\."))
find("2012-10-30", "Hurricane Sandy (day 2)", "regular session", "c12_sandy1",
     q("c12_sandy1", r"As of this moment, CME plans on having NORMAL trading for tonight and tomorrow.s session\."))
find("2012-11-12", "Veterans Day (observed)", "regular session", "d12_veterans",
     q("d12_veterans", r"Agricultural, GSCI , Dow Jones UBS ER, Weather, Real Estate, and Eurozone HICP Sunday, Nov 11 Regular CME Globex Open . Per each product schedule for trade date Monday, Nov 12 Monday, Nov 12 Regular Trading Hours . Per each product schedule for trade date Monday, Nov 12"))
ent("2012-11-22", "Thanksgiving Day", C, "d12_thanks",
    q("d12_thanks", r"Livestock, GSCI, Lumber, Crude Palm Oil and Weather will remain closed until their open at 1700 CT on Thursday Nov 22"))
ent("2012-11-23", "Day after Thanksgiving", H, "d12_thanks",
    q("d12_thanks", r"1215 CT . Early CME Globex close for CME Livestock Futures & Options"), halt="12:15",
    tq=q("d12_thanks", r"1215 CT . Early CME Globex close for CME Livestock Futures & Options"),
    note="floor card 2012 gives 12:00 for commodities on the floor; the Globex livestock close is 12:15")
ent("2012-12-24", "Christmas Eve", H, "floor2012",
    q("floor2012", r"Monday, December 24, 2012 Foreign Exchange, Interest Rates, Commodities, GSCI,"),
    halt="12:15", tev="inferred",
    tq=q("floor2012", r"Christmas Day Weather & Real Estate close at 12:00 p.m."),
    note=("status from the 2012 floor card (commodities close early); the Globex minute 12:15 is "
          "inferred from the 2012 Thanksgiving Globex schedule, where the floor card's 12:00 "
          "commodity close went with a 12:15 Globex livestock close (d12_thanks); the floor time "
          "is 12:00"))
ent("2012-12-25", "Christmas Day", C, "floor2012", q("floor2012", r"Christmas Day Weather & Real Estate close at 12:00 p.m. \(CME commodity Tuesday, December 25, 2012"),
    note="floor card: Tuesday, December 25, 2012 is the date on which the Chicago trading floor is closed")
find("2012-12-31", "New Year's Eve", "Globex regular close", "d13_ny",
     q("d13_ny", r"Monday, Dec 31 Regular Close[^.]{0,90}?Livestock"))

# ---- 2013
ent("2013-01-01", "New Year's Day", C, "d13_ny", q("d13_ny", r"Tuesday, Jan 1 New Years Observed . Globex closed"))
ent("2013-01-02", "Wednesday after New Year's Day", L, "d13_ny",
    q("d13_ny", r"0905 CT Livestock Futures & Options"), opn="09:05", tq=q("d13_ny", r"0905 CT Livestock Futures & Options"))
uns("2013-01-21", "Martin Luther King Jr. Day 2013: closure expected (exchange holiday every year) but no saved non-CME source states the livestock status (CME's 2013 MLK file is not hosted by Dorman or Cannon; Cannon's posts of 2013-01-17/18 carry no schedule)")
uns("2013-01-22", "Tuesday after MLK Day 2013: whether livestock opened 09:05 Tuesday or 17:00 Monday is unsourced (every 2012-2014 Monday-holiday schedule found says 09:05 Tuesday)")
ent("2013-02-18", "Presidents' Day", C, "d13_pres",
    q("d13_pres", r"Livestock will remain closed until its scheduled opening 0905 CT on Tuesday"))
ent("2013-02-19", "Tuesday after Presidents' Day", L, "d13_pres",
    q("d13_pres", r"Livestock will remain closed until its scheduled opening 0905 CT on Tuesday"), opn="09:05",
    tq=q("d13_pres", r"scheduled opening 0905 CT on Tuesday"))
ent("2013-03-28", "Thursday before Good Friday", H, "c13_gf",
    q("c13_gf", r"Thursday, March 28: 1:55 Central Time . Early Close for Lumber & Livestock"), halt="13:55",
    tq=q("c13_gf", r"1:55 Central Time . Early Close for Lumber & Livestock"), note="13:55 is after the 13:00 settlement")
ent("2013-03-29", "Good Friday", C, "c13_gf", q("c13_gf", r"Friday, March 29: CME Globex is closed"))
ent("2013-05-27", "Memorial Day", C, "d13_mem",
    q("d13_mem", r"Livestock will remain closed until its scheduled opening 0905 CT on Tuesday"), note="Cannon c13_mem agrees")
ent("2013-05-28", "Tuesday after Memorial Day", L, "d13_mem",
    q("d13_mem", r"Livestock will remain closed until its scheduled opening 0905 CT on Tuesday"), opn="09:05",
    tq=q("d13_mem", r"scheduled opening 0905 CT on Tuesday"))
ent("2013-07-03", "Day before Independence Day", H, "c13_jul4",
    q("c13_jul4", r"12:15 P\.M\. CT . Early close for Livestock Futures & Options"), halt="12:15",
    tq=q("c13_jul4", r"12:15 P\.M\. CT . Early close for Livestock Futures & Options"))
ent("2013-07-04", "Independence Day", C, "c13_jul4",
    q("c13_jul4", r"Livestock will remain closed until its scheduled opening 9:05 A\.M\. CT on Friday"))
ent("2013-07-05", "Friday after Independence Day", L, "c13_jul4",
    q("c13_jul4", r"Livestock will remain closed until its scheduled opening 9:05 A\.M\. CT on Friday"), opn="09:05",
    tq=q("c13_jul4", r"scheduled opening 9:05 A\.M\. CT on Friday"))
ent("2013-09-02", "Labor Day", C, "d13_labor",
    q("d13_labor", r"Livestock will remain closed until its scheduled opening 0905 CT on Tuesday"))
ent("2013-09-03", "Tuesday after Labor Day", L, "d13_labor",
    q("d13_labor", r"Livestock will remain closed until its scheduled opening 0905 CT on Tuesday"), opn="09:05",
    tq=q("d13_labor", r"scheduled opening 0905 CT on Tuesday"))
uns("2013-10-14", "Columbus Day 2013: livestock traded normally on Columbus Day in 2010-2012 (floor cards, schedules), but no saved source states 2013")
find("2013-11-11", "Veterans Day", "regular session", "d13_veterans",
     q("d13_veterans", r"Products listed on Globex are unaffected and will run on a normal schedule"))
ent("2013-11-28", "Thanksgiving Day", C, "d13_thanks",
    q("d13_thanks", r"Livestock will remain closed until 0905 CT on Friday, Nov 29"))
ent("2013-11-29", "Day after Thanksgiving", H, "d13_thanks",
    q("d13_thanks", r"1215 CT . Early close for Livestock Futures & Options"), halt="12:15",
    tq=q("d13_thanks", r"1215 CT . Early close for Livestock Futures & Options"), note="Cannon c13_thanks agrees")
ent("2013-11-29", "Day after Thanksgiving (late open)", L, "d13_thanks",
    q("d13_thanks", r"Livestock will remain closed until 0905 CT on Friday, Nov 29"), opn="09:05",
    tq=q("d13_thanks", r"0905 CT on Friday, Nov 29"))
ent("2013-12-24", "Christmas Eve", H, "d13_xmas",
    q("d13_xmas", r"1215 CT . Early close for Livestock Futures & Options"), halt="12:15",
    tq=q("d13_xmas", r"1215 CT . Early close for Livestock Futures & Options"), note="Cannon c13_xmas agrees")
ent("2013-12-25", "Christmas Day", C, "d13_xmas", q("d13_xmas", r"Wednesday, Dec 25 Christmas Day Observed . Globex closed"))
ent("2013-12-26", "Thursday after Christmas", L, "d13_xmas",
    q("d13_xmas", r"0905 CT Livestock Futures & Options"), opn="09:05", tq=q("d13_xmas", r"0905 CT Livestock Futures & Options"))
find("2013-12-31", "New Year's Eve", "regular close", "c14_ny",
     q("c14_ny", r"Other CME Group Products Regular close per each product schedule"))

# ---- 2014
ent("2014-01-01", "New Year's Day", C, "c14_ny",
    q("c14_ny", r"New Year.s Day Observed . Globex closed"),
    note="the closure line is printed for CBOT/KCBT grain and agricultural products; livestock's next open is Thursday 09:05 (next entry)")
ent("2014-01-02", "Thursday after New Year's Day", L, "c14_ny",
    q("c14_ny", r"9:05 Central Time Livestock Futures & Options"), opn="09:05",
    tq=q("c14_ny", r"9:05 Central Time Livestock Futures & Options"))
find("2014-01-17", "Friday before MLK Day", "regular Friday close 13:55", "c14_mlk",
     q("c14_mlk", r"Livestock 13:55 16:00 9:05"))
ent("2014-01-20", "Martin Luther King Jr. Day", C, "c14_mlk", q("c14_mlk", r"Livestock 13:55 16:00 9:05"),
    note="table row: regular Friday close 13:55, then the Tuesday 09:05 open; no Monday session")
ent("2014-01-21", "Tuesday after MLK Day", L, "c14_mlk", q("c14_mlk", r"Livestock 13:55 16:00 9:05"),
    opn="09:05", tq=q("c14_mlk", r"Livestock 13:55 16:00 9:05"))
ent("2014-02-17", "Presidents' Day", C, "c14_pres",
    q("c14_pres", r"Friday, Feb 14 Regular close . Per each product schedule (?:for: )?Livestock"),
    note="Livestock: Friday regular close, next open Tuesday 09:05 (" + q("c14_pres", r"9:05 CT . Livestock markets open") + ")")
ent("2014-02-18", "Tuesday after Presidents' Day", L, "c14_pres", q("c14_pres", r"9:05 CT . Livestock markets open"),
    opn="09:05", tq=q("c14_pres", r"9:05 CT . Livestock markets open"))
ent("2014-04-08", "CME Globex agricultural outage (intraday)", H, "nadex14",
    q("nadex14", r"On April 8, 2014, the CME Group halted trading on the Globex Futures and Options of Corn \(ZC\) at 1:38:33pm ET, due to technical issues\."),
    ev="unverified", tev="unverified", halt="12:38", tq=q("nadex14", r"1:38:33pm ET"),
    note=("Reports (Reuters/Bloomberg via search results; Farm Media copies not fetchable under "
          "their terms) say the outage hit CME agricultural products incl. cattle and hogs from about "
          "12:38 CT, with livestock restarting on Globex about 14:30 CT while the pits traded on; "
          "the saved CFTC-hosted Nadex filing states the corn halt only. Recorded as an early halt "
          "at 12:38 CT (conservative; the session resumed later) with status unverified, so the date "
          "is unsourced and excluded"))
ent("2014-04-17", "Thursday before Good Friday", H, "d14_gf",
    q("d14_gf", r"Livestock, Dairy & Lumber Products Thursday, April 17 1355 CT / 1455 ET / 1855 UTC . Early Close"),
    halt="13:55", tq=q("d14_gf", r"1355 CT / 1455 ET / 1855 UTC . Early Close"), note="13:55 is after the 13:00 settlement")
ent("2014-04-18", "Good Friday", C, "d14_gf", q("d14_gf", r"Livestock, Dairy & Lumber Products Thursday, April 17 1355 CT / 1455 ET / 1855 UTC . Early Close Friday, April; 18 CME Globex is closed"))
find("2014-05-23", "Friday before Memorial Day", "regular close", "d14_mem",
     q("d14_mem", r"Friday, May 23 Regular close . Per each product schedule (?:for: )?Livestock"))
ent("2014-05-26", "Memorial Day", C, "d14_mem", q("d14_mem", r"905 CT / 1005 ET / 1405 UTC . Livestock markets open"),
    note="Livestock: Friday regular close, next open Tuesday 09:05; no Monday session")
ent("2014-05-27", "Tuesday after Memorial Day", L, "d14_mem", q("d14_mem", r"905 CT / 1005 ET / 1405 UTC . Livestock markets open"),
    opn="09:05", tq=q("d14_mem", r"905 CT / 1005 ET / 1405 UTC . Livestock markets open"))
ent("2014-07-03", "Day before Independence Day", H, "c14_jul4",
    q("c14_jul4", r"1215 CT / 1315 ET / 1715 UTC . Early close for Livestock Futures & Options"), halt="12:15",
    tq=q("c14_jul4", r"1215 CT / 1315 ET / 1715 UTC . Early close for Livestock Futures & Options"))
ent("2014-07-04", "Independence Day", C, "c14_jul4", q("c14_jul4", r"Early close for Livestock Futures & Options Friday, July 4 All products closed"))
uns("2014-08-25", "Monday after the 2014-08-24 Sunday-evening CME Globex outage (start of trading delayed for all markets, per search results); livestock's Monday 09:05 open is not confirmed by a saved source")
uns("2014-09-01", "Labor Day 2014: closure expected but no saved source (Cannon's 2014-08-28 post carried the schedule as an image that is no longer retrievable)")
uns("2014-09-02", "Tuesday after Labor Day 2014: open time (09:05 expected) unsourced")
uns("2014-10-13", "Columbus Day 2014: no saved source")
uns("2014-11-11", "Veterans Day 2014: no saved source")
uns("2014-11-27", "Thanksgiving 2014: closure expected but no saved non-CME source")
uns("2014-11-28", "Day after Thanksgiving 2014: early close (12:15 expected) and open time unsourced")
uns("2014-12-24", "Christmas Eve 2014: early close expected; the one news report found (Reuters via a Farm Media site) cannot be used under that site's terms")
uns("2014-12-25", "Christmas Day 2014: closure expected but no saved source")
uns("2014-12-26", "Friday after Christmas 2014: open time unsourced")
uns("2014-12-31", "New Year's Eve 2014: status unsourced")

# ---- 2015
uns("2015-01-01", "New Year's Day 2015: closure expected but no saved source")
uns("2015-01-02", "Friday after New Year's Day 2015: open time unsourced")
find("2015-01-16", "Friday before MLK Day", "regular close", "c15_mlk",
     q("c15_mlk", r"Friday, Jan 16 Regular close . Per each product schedule (?:for: )?Livestock"))
ent("2015-01-19", "Martin Luther King Jr. Day", C, "c15_mlk", q("c15_mlk", r"905 CT / 1005 ET / 1505 UTC . Livestock markets open"),
    note="Livestock: Friday regular close, next open Tuesday 09:05; no Monday session")
ent("2015-01-20", "Tuesday after MLK Day", L, "c15_mlk", q("c15_mlk", r"905 CT / 1005 ET / 1505 UTC . Livestock markets open"),
    opn="09:05", tq=q("c15_mlk", r"905 CT / 1005 ET / 1505 UTC . Livestock markets open"),
    note="f15_opt: 'The opening at 9:05 a.m. CT on the first business day of the week (usually Monday but Monday holidays will change this to Tuesday)'")
find("2015-02-13", "Friday before Presidents' Day", "regular close", "c15_pres",
     q("c15_pres", r"Friday, Feb 13 Regular close . Per each product schedule (?:for: )?Livestock"))
ent("2015-02-16", "Presidents' Day", C, "c15_presd", q("c15_presd", r"Sunday . normal open for all, EXCEPT grains & Livestock = stay closed"),
    note="Tuesday 09:05 open: " + q("c15_pres", r"905 CT / 1005 ET / 1505 UTC . Livestock markets open"))
ent("2015-02-17", "Tuesday after Presidents' Day", L, "c15_pres", q("c15_pres", r"905 CT / 1005 ET / 1505 UTC . Livestock markets open"),
    opn="09:05", tq=q("c15_pres", r"905 CT / 1005 ET / 1505 UTC . Livestock markets open"))
ent("2015-04-02", "Thursday before Good Friday", H, "c15_gf",
    q("c15_gf", r"Livestock, Dairy & Lumber Products Thursday, April 2 1355 CT / 1455 ET / 1855 UTC . Early Close"),
    halt="13:55", tq=q("c15_gf", r"1355 CT / 1455 ET / 1855 UTC . Early Close"), note="13:55 is after the 13:00 settlement")
ent("2015-04-03", "Good Friday", C, "c15_gf", q("c15_gf", r"Early Close Friday, April 3 CME Globex is closed"))
find("2015-05-22", "Friday before Memorial Day", "regular close", "c15_mem",
     q("c15_mem", r"Friday, May 22 Regular close . Per each product schedule (?:for: )?Livestock"))
ent("2015-05-25", "Memorial Day", C, "c15_mem", q("c15_mem", r"0905 CT / 1005 ET / 1405 UTC . Livestock markets open"),
    note="Livestock: Friday regular close, next open Tuesday 09:05; no Monday session")
ent("2015-05-26", "Tuesday after Memorial Day", L, "c15_mem", q("c15_mem", r"0905 CT / 1005 ET / 1405 UTC . Livestock markets open"),
    opn="09:05", tq=q("c15_mem", r"0905 CT / 1005 ET / 1405 UTC . Livestock markets open"))
ent("2015-07-02", "Day before Independence Day (observed)", H, "c15_jul4",
    q("c15_jul4", r"1215 CT / 1315 ET / 1715 UTC . Early close for Livestock Futures & Options"), halt="12:15",
    tq=q("c15_jul4", r"1215 CT / 1315 ET / 1715 UTC . Early close for Livestock Futures & Options"))
ent("2015-07-03", "Independence Day (observed)", C, "c15_jul4", q("c15_jul4", r"Early close for Livestock Futures & Options Friday, July 3 All products closed"))
find("2015-09-04", "Friday before Labor Day", "regular close", "c15_labor",
     q("c15_labor", r"Friday, Sep 4 Regular Close . Per each product schedule (?:for: )?Livestock"))
ent("2015-09-07", "Labor Day", C, "c15_labor", q("c15_labor", r"905 CT / 1005 ET / 1405 UTC . Livestock markets open"),
    note="Livestock: Friday regular close, next open Tuesday 09:05; no Monday session")
ent("2015-09-08", "Tuesday after Labor Day", L, "c15_labor", q("c15_labor", r"905 CT / 1005 ET / 1405 UTC . Livestock markets open"),
    opn="09:05", tq=q("c15_labor", r"905 CT / 1005 ET / 1405 UTC . Livestock markets open"))
uns("2015-10-12", "Columbus Day 2015: no saved source")
uns("2015-11-11", "Veterans Day 2015: no saved source")
find("2015-11-25", "Wednesday before Thanksgiving", "regular close", "c15_thanks",
     q("c15_thanks", r"Wednesday, Nov 25 Regular close . Per each product schedule (?:for: )?Livestock"))
ent("2015-11-26", "Thanksgiving Day", C, "c15_thanks",
    q("c15_thanks", r"Wednesday, Nov 25 Regular close . Per each product schedule (?:for: )?Livestock Dairy Lumber Friday, Nov 27"),
    note="livestock block runs from the Wednesday close to the Friday 08:00 open; no Thursday session")
ent("2015-11-27", "Day after Thanksgiving", H, "c15_thanks",
    q("c15_thanks", r"1215 CT / 1315 ET / 1815 UTC . Early close for Livestock Futures & Options"), halt="12:15",
    tq=q("c15_thanks", r"1215 CT / 1315 ET / 1815 UTC . Early close for Livestock Futures & Options"),
    note="opens at the regular era-2 08:00 (" + q("c15_thanks", r"800 CT / 900 ET / 1400 UTC . Livestock markets open") + ")")
ent("2015-12-24", "Christmas Eve", H, "c15_xmas",
    q("c15_xmas", r"1215 CT / 1315 ET / 1815 UTC . Early close for Livestock Futures & Options"), halt="12:15",
    tq=q("c15_xmas", r"1215 CT / 1315 ET / 1815 UTC . Early close for Livestock Futures & Options"))
ent("2015-12-25", "Christmas Day", C, "c15_xmas", q("c15_xmas", r"Friday, Dec 25 Christmas Day Observed . Globex closed"))
ent("2015-12-31", "New Year's Eve (Thursday)", H, "c16_ny",
    q("c16_ny", r"Livestock, Dairy & Lumber Products Thursday, Dec 31 1355 CT / 1455 ET / 1955 UTC . Early Close"),
    halt="13:55", tq=q("c16_ny", r"1355 CT / 1455 ET / 1955 UTC . Early Close"), note="13:55 is after the 13:00 settlement")

# ---- 2016
ent("2016-01-01", "New Year's Day", C, "c16_ny", q("c16_ny", r"Friday, Jan 1 New Years Observed . Globex closed"))
find("2016-01-15", "Friday before MLK Day", "regular close", "c16_mlk",
     q("c16_mlk", r"Friday, Jan 15 Regular close . Per each product schedule (?:for: )?Livestock"))
ent("2016-01-18", "Martin Luther King Jr. Day", C, "c16_mlk", q("c16_mlk", r"905 CT / 1005 ET / 1505 UTC . Livestock markets open"),
    note="Livestock: Friday regular close, next open Tuesday 09:05; no Monday session")
ent("2016-01-19", "Tuesday after MLK Day", L, "c16_mlk", q("c16_mlk", r"905 CT / 1005 ET / 1505 UTC . Livestock markets open"),
    opn="09:05", tq=q("c16_mlk", r"905 CT / 1005 ET / 1505 UTC . Livestock markets open"))
ent("2016-02-15", "Presidents' Day", C, "c16_pres", q("c16_pres", r"Livestock 13:55 Closed Closed 9:05"),
    note="table row: Friday 13:55 regular close, Monday closed (two columns), Tuesday 09:05 open")
ent("2016-02-16", "Tuesday after Presidents' Day", L, "c16_pres", q("c16_pres", r"Livestock 13:55 Closed Closed 9:05"),
    opn="09:05", tq=q("c16_pres", r"Livestock 13:55 Closed Closed 9:05"))
find("2016-03-24", "Thursday before Good Friday", "regular close 13:05", "i16_gf",
     IMGQ + "row 'Livestock': Thursday, March 24 'Regular Close' 13:05")
ent("2016-03-25", "Good Friday", C, "i16_gf", IMGQ + "Friday, March 25: 'Globex Closed' across all rows; Livestock next 'Pre-opening' 6:00 and 'Open' 8:30 on Monday, March 28")
find("2016-05-27", "Friday before Memorial Day", "regular close", "c16_mem",
     q("c16_mem", r"Friday, May 27 Regular close . Per each product schedule (?:for: )?Livestock"))
ent("2016-05-30", "Memorial Day", C, "c16_mem", q("c16_mem", r"0830 CT / 0930 ET / 1330 UTC . Livestock markets open"),
    note="Livestock: Friday regular close, next open Tuesday 08:30 (regular); no Monday session")
ent("2016-07-04", "Independence Day", C, "c16_jul4", q("c16_jul4", r"830 CT / 930 ET / 1330 UTC . Livestock markets open"),
    note="Livestock block: Friday July 1 regular close, Tuesday July 5 08:30 open; no Monday session")
find("2016-07-01", "Friday before Independence Day", "regular close", "c16_jul4",
     q("c16_jul4", r"Livestock, Dairy & Lumber Products Friday, July 1 Regular Close . Per each product schedule for:"))
find("2016-09-02", "Friday before Labor Day", "regular close", "c16_labor",
     q("c16_labor", r"Friday, Sep 2 Regular Close . Per each product schedule (?:for: )?Livestock"))
ent("2016-09-05", "Labor Day", C, "c16_labor", q("c16_labor", r"830 CT / 930 ET / 1330 UTC . Livestock markets open"),
    note="Livestock: Friday regular close, next open Tuesday 08:30; no Monday session")
uns("2016-10-10", "Columbus Day 2016: no saved source")
uns("2016-11-11", "Veterans Day 2016: no saved source")
find("2016-11-23", "Wednesday before Thanksgiving", "regular close", "c16_thanks",
     q("c16_thanks", r"Wednesday, Nov 23 Regular close . Per each product schedule (?:for: )?Livestock"))
ent("2016-11-24", "Thanksgiving Day", C, "c16_thanks",
    q("c16_thanks", r"Wednesday, Nov 23 Regular close . Per each product schedule (?:for: )?Livestock Dairy Lumber Friday, Nov 25"),
    note="livestock block runs from the Wednesday close to the Friday 08:30 open; no Thursday session")
ent("2016-11-25", "Day after Thanksgiving", H, "c16_thanks",
    q("c16_thanks", r"1215 CT / 1315 ET / 1815 UTC . Early close for Livestock Futures & Options"), halt="12:15",
    tq=q("c16_thanks", r"1215 CT / 1315 ET / 1815 UTC . Early close for Livestock Futures & Options"))
ent("2016-12-23", "Friday before Christmas (observed Monday)", H, "c16_xmas",
    q("c16_xmas", r"1215 CT / 1315 ET / 1815 UTC . Early close for Livestock Futures & Options"), halt="12:15",
    tq=q("c16_xmas", r"1215 CT / 1315 ET / 1815 UTC . Early close for Livestock Futures & Options"),
    note="the LEAN vendor table has 12:05 for this date; the schedule text says 12:15")
ent("2016-12-26", "Christmas Day (observed)", C, "c16_xmas", q("c16_xmas", r"Monday, Dec 26 Christmas Day Observed . Globex closed"))
find("2016-12-30", "Friday before New Year's Day (observed Monday)", "regular close", "c17_ny",
     q("c17_ny", r"Livestock, Dairy & Lumber Products Friday, Dec 30 Regular Close . Per each Product"))

# ---- 2017 (images unless noted)
ent("2017-01-02", "New Year's Day (observed)", C, "c17_ny", q("c17_ny", r"Monday, Jan 2 New Years Observed . Globex closed"))
ent("2017-01-16", "Martin Luther King Jr. Day", C, "i17_mlk", IMGQ + "row 'Livestock': Fri Jan 13 '*ALL* REGULAR Closes' 13:05; no Sunday/Monday entries; Tues Jan 17 'Pre-opening' 6:00, 'OPEN' 9:05")
ent("2017-01-17", "Tuesday after MLK Day", L, "i17_mlk", IMGQ + "row 'Livestock': Tues., Jan. 17 'OPEN' 9:05",
    opn="09:05", tev="unverified", tq=IMGQ + "Tues., Jan. 17 OPEN 9:05",
    note=("CONFLICT: 09:05 contradicts the 08:30 Mon-Fri open in force since 2016-02-29 (f16_064) and "
          "every other 2016-2019 schedule found (Tuesday 08:30); possibly a stale template value. "
          "Kept as a late open with time unverified (conservative: nothing before 09:05 counts)"))
ent("2017-02-20", "Presidents' Day", C, "i17_pres", IMGQ + "row 'Livestock': Fri Feb 17 13:05 regular close; no Sun/Mon entries; Tues Feb 21 Pre-opening 6:00, Open 8:30")
ent("2017-04-14", "Good Friday", C, "i17_gf", IMGQ + "row 'Livestock': Thurs Apr 13 'REGULAR Close' 13:05; Friday Apr 14 'Globex CLOSED'; Mon Apr 17 6:00 / 8:30")
find("2017-04-13", "Thursday before Good Friday", "regular close 13:05", "i17_gf", IMGQ + "row 'Livestock': Thursday April 13 'REGULAR Close' 13:05")
ent("2017-05-29", "Memorial Day", C, "i17_mem", IMGQ + "row 'Livestock': Friday May 26 'REGULAR Fri. Close' 13:05 ('EARLY Close = NONE'); no Sun/Mon entries; Tues May 30 6:00 / 8:30")
ent("2017-07-03", "Day before Independence Day", H, "i17_jul4", IMGQ + "row 'Livestock': Monday July 3 'EARLY CLOSE' 12:15",
    halt="12:15", tq=IMGQ + "EARLY CLOSE 12:15")
ent("2017-07-04", "Independence Day", C, "i17_jul4", IMGQ + "row 'Livestock': 'Markets Closed' (July 3 evening and July 4); Wed July 5 6:00 / 8:30")
ent("2017-09-04", "Labor Day", C, "i17_labor", IMGQ + "row 'Livestock': Friday Sept 1 'REGULAR Fri. Close' 13:05; no Sun/Mon entries; Tues Sept 5 6:00 / 8:30")
uns("2017-10-09", "Columbus Day 2017: no saved source")
uns("2017-11-10", "Veterans Day 2017 (observed Friday): no saved source")
ent("2017-11-23", "Thanksgiving Day", C, "i17_thanks", IMGQ + "row 'Livestock': 'Closed for Thanksgiving' (Wed Nov 22 open, Thu Nov 23 halt and open); Friday Nov 24 open 'Regular per Product'")
ent("2017-11-24", "Day after Thanksgiving", H, "i17_thanks", IMGQ + "row 'Livestock': Friday November 24 CLOSE 'Early @ 1215 CT / 1815 UTC'",
    halt="12:15", tq=IMGQ + "Early @ 1215 CT / 1815 UTC")
ent("2017-12-22", "Friday before Christmas (observed Monday)", H, "i17_xmas", IMGQ + "row 'Livestock': Friday, Dec 22 CLOSE 'Early @1215 CT / 1815 UTC'",
    halt="12:15", tq=IMGQ + "Early @1215 CT / 1815 UTC")
ent("2017-12-25", "Christmas Day", C, "i17_xmas", IMGQ + "row 'Livestock': Monday, Dec 25 'Closed for Christmas'; Tuesday Dec 26 'Pre-open 6:00CT ... Open 8:30 CT'")
find("2017-12-29", "Friday before New Year's Day (observed Monday)", "regular close 13:05", "i18_ny", IMGQ + "row 'Livestock': Fri., Dec. 29 'ALL REG. closes' 13:05")

# ---- 2018
ent("2018-01-01", "New Year's Day", C, "i18_ny", IMGQ + "row 'Livestock': Mon., Jan. 1 'Globex CLOSED'; Tuesday Jan. 2 6:00 / 8:30, close 13:05")
ent("2018-01-15", "Martin Luther King Jr. Day", C, "i18_mlk", IMGQ + "row 'Livestock': Fri Jan 12 '*ALL* REGULAR Closes' 13:05; no Sun/Mon entries; Tues Jan 16 6:00 / 8:30")
ent("2018-02-19", "Presidents' Day", C, "i18_pres", IMGQ + "row 'Livestock': Fri Feb 16 13:05; no Sun/Mon entries; Tues Feb 20 6:00 / 8:30")
find("2018-03-29", "Thursday before Good Friday", "regular close 13:05", "i18_gf", IMGQ + "row 'Livestock': Thursday, March 29 'REGULAR Close' 13:05")
ent("2018-03-30", "Good Friday", C, "i18_gf", IMGQ + "row 'Livestock': Friday, March 30 'Globex CLOSED'; Mon Apr 2 6:00 / 8:30")
ent("2018-05-28", "Memorial Day", C, "i18_mem", IMGQ + "row 'Livestock': Friday May 25 'REGULAR Fri. Close' 13:05 ('EARLY Close = NONE'); no Sun/Mon entries; Tues May 29 6:00 / 8:30")
ent("2018-07-03", "Day before Independence Day", H, "i18_jul4", IMGQ + "row 'Livestock': Tuesday July 3 CLOSE 'Early @ 1215 CT / 1715 UTC'",
    halt="12:15", tq=IMGQ + "Early @ 1215 CT / 1715 UTC")
ent("2018-07-04", "Independence Day", C, "i18_jul4", IMGQ + "row 'Livestock': 'Markets Closed' (Tuesday July 3 open, Wednesday July 4 halt); open 'Thursday @ 0830 / 1330 UTC'")
ent("2018-09-03", "Labor Day", C, "i18_labor", IMGQ + "row 'Livestock': Friday Aug 31 13:05; no Sunday/Monday entries; Tues Sept 4 Pre-opening 6:00, Open 8:30")
uns("2018-10-08", "Columbus Day 2018: no saved source")
uns("2018-11-12", "Veterans Day 2018 (observed Monday): no saved source")
ent("2018-11-22", "Thanksgiving Day", C, "i18_thanks", IMGQ + "row 'Livestock': Wed. Nov. 21 'REGULAR Close = ALL' 13:05; no Thursday entries; Fri. Nov. 23 Pre-opening 6:00, Open 8:30, 'EARLY CLOSE = ALL' 12:15")
ent("2018-11-23", "Day after Thanksgiving", H, "i18_thanks", IMGQ + "row 'Livestock': Fri., Nov. 23 'EARLY CLOSE = ALL' 12:15",
    halt="12:15", tq=IMGQ + "EARLY CLOSE = ALL 12:15")
find("2018-12-05", "National Day of Mourning (President G. H. W. Bush)", "regular session (closures limited to US equity index and fixed income)",
     "fia18", q("fia18", r"US equity index and fixed income futures and options markets will also be closed for trading during US business hours\. All other US futures markets will open as usual\."))
ent("2018-12-24", "Christmas Eve", H, "i18_xmas", IMGQ + "CME Group row 'Livestock': Monday, December 24th Close 12:15",
    halt="12:15", tq=IMGQ + "Livestock 12:15")
ent("2018-12-25", "Christmas Day", C, "i18_xmas", IMGQ + "CME Group row 'Livestock': Tuesday, December 25th 'Closed'; Open '8:30 (Wed. Morning)'")
find("2018-12-31", "New Year's Eve", "regular close 13:05", "i19_ny", IMGQ + "row 'Livestock': Mon., Dec. 31 'ALL REGULAR closes' 13:05")

# ---- 2019
ent("2019-01-01", "New Year's Day", C, "i19_ny", IMGQ + "row 'Livestock': Tues., Jan. 1 'Globex CLOSED'; Wednesday Jan. 2 6:00 / 8:30, close 13:05")
ent("2019-01-21", "Martin Luther King Jr. Day", C, "i19_mlk", IMGQ + "row 'Livestock': Fri Jan 18 '*ALL* REGULAR Closes' 13:05; no Sun/Mon entries; Tues Jan 22 6:00 / 8:30")
ent("2019-02-18", "Presidents' Day", C, "i19_pres", IMGQ + "row 'Livestock': Fri Feb 15 13:05; no Sun/Mon entries; Tues Feb 19 6:00 / 8:30")
find("2019-04-18", "Thursday before Good Friday", "regular close", "i19_gf", IMGQ + "row 'Livestock': Thursday, April 18 CLOSE 'Regular per Product' (low-resolution GIF)")
ent("2019-04-19", "Good Friday", C, "i19_gf", IMGQ + "row 'Livestock': Friday, April 19 'Closed for Good Friday'; open 'Monday @ 0830' (low-resolution GIF)")
ent("2019-05-27", "Memorial Day", C, "i19_mem", IMGQ + "row 'Livestock': Friday May 24 'REGULAR Fri. Close' 13:05 ('EARLY Close = NONE'); no Sun/Mon entries; Tues May 28 6:00 / 8:30")

# ------------------------------------------------------------------ regular Monday 09:05 opens
MON_Q1 = q("f14_408", r"Monday 9:05 a\.m\. Central Time/CT-Opening")
MON_Q2 = q("f16_064", r"Mon: 9:05 am . 4:00 pm")
closed = {e["day"] for e in ENTRIES if e["kind"] == C}
late = {e["day"] for e in ENTRIES if e["kind"] == L}
uns_days = {u["day"] for u in UNSOURCED}
d = FIRST
n_mon = 0
while d < ERA3_START:
    if d.weekday() == 0 and str(d) not in closed and str(d) not in late and str(d) not in uns_days:
        era1 = d < ERA2_START
        ENTRIES.append({
            "day": str(d), "name": "Regular Monday open (first session of the week)", "kind": L,
            "halt_ct": None, "open_ct": "09:05",
            "evidence": "secondary" if era1 else "cme",
            "time_evidence": "inferred" if era1 else "cme",
            "source": "f14_408" if era1 else "f16_064",
            "status_quote": MON_Q1 if era1 else MON_Q2,
            "time_quote": MON_Q1 if era1 else MON_Q2,
            "note": ("generated by rule: livestock had no Sunday-evening session; the week's first "
                     "session opened Monday 09:05 CT. " + ("Era 1 (to 2014-10-24): the rule is CME's "
                     "'current' hours in Submission 14-408 (Oct 2014); the 2010-2013 broker-hosted "
                     "CME schedules show livestock staying closed through the Sunday 17:00 Globex "
                     "open 'until their regularly scheduled open on Monday' (e.g. d10_columbus, "
                     "d11_gf), so status secondary and time inferred" if era1 else
                     "Era 2: Submission 14-408 hours as of 2014-10-27 and 16-064 'current' hours"))})
        n_mon += 1
    d += timedelta(days=1)

# ------------------------------------------------------------------ sessions
SESSIONS = [
    {"valid_from": "2010-06-01", "valid_to": "2014-10-24",
     "segments": [{"start_offset_days": -1, "start_ct": "17:00", "end_offset_days": 0, "end_ct": "16:00"}],
     "day_session_ct": {"HE": ["09:05", "13:00"], "LE": ["09:05", "13:00"]},
     "source": "f14_408", "evidence": "secondary",
     "note": ("Era 1. CME Globex livestock: " + q("f14_408", r"Monday 9:05 a\.m\. Central Time/CT-Opening") + " [...] " + q("f14_408", r"Daily trading halts 4:00 p\.m\. - 5:00 p\.m\. CT\.") + " [...] Trading restarts at 5:00 p.m. CT and continues until 4:00 p.m. CT on Monday-Thursday (left column of the two-column table, read from the PDF; the text layer interleaves the columns)" +
              " ... " + q("f14_408", r"Friday 1:55 p\.m\. CT- Close") + " (Submission 14-408, the hours "
              "'current' in Oct 2014). Friday close 1:55 p.m. since 2008-10-24 (f08_159: " +
              q("f08_159", r"from the current 1:30 p\.m\. close to 1:55 p\.m\.") + "). Graded secondary, "
              "not cme: no CME filing found that dates this structure to 2010-06; the 2010-2013 "
              "broker-hosted CME schedules corroborate it (livestock reopening at 1700 CT the evening "
              "before a trade date, 'remain closed until their regularly scheduled open on Monday', "
              "Friday closes). Not representable in SessionSpec and left to E.17: Monday opens 09:05 "
              "(generated late_open entries), Friday Globex close 13:55 (regular, not an early halt; "
              "no bars 13:55-16:00 on Fridays), and the evening segment before a post-holiday trade "
              "date where a schedule says 0905 (late_open entries). day_session_ct open 09:05 = the "
              "open-outcry/RTH open (floor hours 'Monday-Friday 9:05 a.m. to 1:02 p.m.' for "
              "livestock options in f15_opt); close 13:00 = the end of the livestock settlement "
              "period, the C the frozen data/calendars/livestock.py uses (day_session_ct (08:30, "
              "13:00)); f16_064: 'The daily settlement period and procedures for the Contracts "
              "shall remain unchanged'. Settlement S_p is Task 1's.")},
    {"valid_from": "2014-10-27", "valid_to": "2016-02-26",
     "segments": [{"start_offset_days": 0, "start_ct": "08:00", "end_offset_days": 0, "end_ct": "16:00"}],
     "day_session_ct": {"HE": ["08:00", "13:00"], "LE": ["08:00", "13:00"]},
     "source": "f14_408", "evidence": "cme",
     "note": ("Era 2. " + q("f14_408", r"At 4:00 p\.m\. CT on Monday-Thursday, the markets halt.{0,60}?restart at 8:00 a\.m\. CT on the next morning\.") +
              " Effective " + q("f14_408", r"effective on Monday, October 27, 2014") + ". Confirmed as "
              "'current' on 2016-02-10 by f16_064 (" + q("f16_064", r"Tue . Thu: 8:00 am . 4:00 pm") + "; " +
              q("f16_064", r"Fri: 8:00 am . 1:55 pm") + "). Monday (and a Tuesday after a Monday "
              "holiday) opens 09:05: generated late_open entries; f15_opt: " +
              q("f15_opt", r"The opening at 9:05 a\.m\. CT on the first business day of the week \(usually Monday but Monday holidays will change this to Tuesday\) shall remain unchanged\.") +
              " Friday close 13:55 not representable (left to E.17). day_session_ct open 08:00 = "
              "the Globex daytime open (the session's first minute, as 2019's 08:30); the "
              "open-outcry futures pit (until 2015-07-02) opened 09:05: a judgment call for the "
              "lead (H4's O_p). Close 13:00 as era 1.")},
    {"valid_from": "2016-02-29", "valid_to": None,
     "segments": [{"start_offset_days": 0, "start_ct": "08:30", "end_offset_days": 0, "end_ct": "13:05"}],
     "day_session_ct": {"HE": ["08:30", "13:00"], "LE": ["08:30", "13:00"]},
     "source": "f16_064", "evidence": "cme",
     "note": ("Era 3. " + q("f16_064", r"The amended hours will be effective on Monday, February 29, 2016\.") +
              " CME Globex: " + q("f16_064", r"Mon . Fri: 8:30 am . 1:05 pm") + ". Matches the frozen "
              "data/calendars/livestock.py at 2019-05 (segment 08:30-13:05, day_session_ct (08:30, "
              "13:00)). "
              "No CFTC filing changing livestock hours between 2016-02-29 and 2019-05 was found; every "
              "2016-2019 holiday schedule read shows the 08:30 open and 13:05 regular close (except "
              "the MLK 2017 table's 09:05, recorded as an unverified late open).")},
]

# ------------------------------------------------------------------ year coverage
UNSCHED = {
    2010: "news/notice search (WebSearch) for CME livestock halts and closures 2010: none found; floor cards list every 2010 exchange holiday",
    2011: "WebSearch for 2011 livestock halts: none found",
    2012: "Hurricane Sandy 2012-10-29/30 checked (c12_sandy1/2: closures limited to equity index and interest rates; findings); no other event found",
    2013: "WebSearch: none found",
    2014: "2014-04-08 Globex agricultural outage (entry, unverified -> unsourced); 2014-08-24/25 Sunday-evening Globex outage (listed unsourced); Oct 27 hours change (session row)",
    2015: "WebSearch: none found",
    2016: "Feb 29 hours change (session row); WebSearch: no livestock halt found",
    2017: "WebSearch: none found",
    2018: "2018-12-05 National Day of Mourning checked (fia18, amp18: other futures markets open as usual; finding)",
    2019: "2019-01..05: none found",
}
UNIVERSE = {
    2010: ("floor2010 and floor2011 (CME full-year floor holiday lists, broker-hosted) list every 2010 exchange holiday and early close; per-holiday Globex schedules for each", ["floor2010", "floor2011"]),
    2011: ("floor2011 full-year list; per-holiday schedules for every 2011 holiday", ["floor2011", "floor2012"]),
    2012: ("floor2012 full-year list; per-holiday schedules", ["floor2012"]),
    2013: ("no full-year list found for 2013; the set of exchange holidays is the one every other year's list shows (New Year, MLK, Presidents, Good Friday, Memorial, Independence, Labor, Thanksgiving, Christmas) plus Columbus/Veterans and eves checked; JUDGMENT CALL flagged to the lead", []),
    2014: ("no full-year list found for 2014; same judgment as 2013; several 2014 holidays are listed unsourced", []),
    2015: ("NYSE holiday list for 2015 (nyse15/nyse16 Wayback captures) as the universe; per-holiday schedules", ["nyse15", "nyse16"]),
    2016: ("NYSE holiday lists (nyse16, nyse17)", ["nyse16", "nyse17"]),
    2017: ("NYSE holiday lists (nyse17, nyse18)", ["nyse17", "nyse18"]),
    2018: ("NYSE holiday list (nyse18) plus the 2018-12-05 day of mourning", ["nyse18", "fia18", "amp18"]),
    2019: ("NYSE holiday list (nyse18, nyse19)", ["nyse18", "nyse19"]),
}
YEARS = []
for y in range(2010, 2020):
    docs = sorted({e["source"] for e in ENTRIES if e["day"].startswith(str(y))}
                  | {f["source"] for f in FIND if f["day"].startswith(str(y))} | set(UNIVERSE[y][1]))
    YEARS.append({"year": y, "documents": docs, "complete_exception_list": True,
                  "unscheduled_check": UNSCHED[y], "evidence": "secondary",
                  "note": "holiday universe: " + UNIVERSE[y][0] + "; every candidate date without a "
                          "sourced livestock statement is in 'unsourced'"})

# ------------------------------------------------------------------ write
ENTRIES.sort(key=lambda e: (e["day"], e["kind"]))
FIND.sort(key=lambda f: f["day"])
UNSOURCED.sort(key=lambda u: u["day"])
payload = {
    "schema": "e14_hist_calendar/1",
    "group": "livestock",
    "products": PRODUCTS,
    "cme_row_labels": ["Livestock / CME Agricultural Futures (Other CME Group Products on CME Globex, 2010-2012 schedules)",
                       "Livestock, Dairy & Lumber Products (2013-2016 schedules)",
                       "Grain, Oilseed & Livestock / Livestock (2016-2019 schedule tables)",
                       "Commodities (CME Group Chicago Trading Floor Holiday Schedule 2010-2012)"],
    "coverage": {"first": str(FIRST), "last": str(LAST)},
    "sessions": SESSIONS,
    "entries": ENTRIES,
    "no_entry_findings": FIND,
    "year_coverage": YEARS,
    "unsourced": UNSOURCED,
    "sources": SOURCES,
    "counts": {},
    "built_by": "Stage E.16 Task 3b CalendarBuilder-OpusHigh (scratch build_livestock.py); no CME page live or archived fetched; no market data read",
    "grading": ("E.14 grades. 'cme' = a CME document fetched from cftc.gov (self-certification filings). "
                "'secondary' = a broker- or vendor-hosted copy of a CME schedule (Dorman Trading PDFs, Cannon "
                "Trading text posts and schedule images), an industry notice (FIA) or a NYSE list, following "
                "data/calendars/livestock.py's precedent of grading an AMP Futures image of a CME schedule "
                "'secondary'. 'unverified' = anything else (LEAN vendor table: cross-check only)."),
    "flags_for_lead": [],
}
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(payload, indent=1, ensure_ascii=False) + "\n")
print("entries", len(ENTRIES), "findings", len(FIND), "unsourced", len(UNSOURCED), "mondays", n_mon,
      "sources", len(SOURCES))
