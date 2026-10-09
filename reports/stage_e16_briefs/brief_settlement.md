# Task 1 brief: SettlementSource-OpusHigh (worker-high, opus). Read brief_common.md first.

Objective: for each of the 27 products below, the daily settlement minute S_p in CT (the minute at which the
daily settlement window ENDS; lead_spec.md section 0) for every trade date 2010-06-07..2024-02-29, every change in
that period with its effective date, each period graded and cited; and the day-session open O_p per period.

Products (group): equity NQ, YM, RTY; rates ZT, ZF, ZN, TN, ZB, UB; FX 6E, 6A, 6B, 6C, 6J, 6S, 6N; energy CL, NG;
metals GC, HG; grains ZC, ZW, ZS, ZM, ZL; livestock LE, HE.
The lead's prior, TO BE VERIFIED, NEVER USED UNVERIFIED: equity index 15:00; Treasuries 14:00; FX 14:00; energy
13:30; gold 12:30; copper 12:00; grains 13:15; livestock 13:00. Investigate, without presuming the answer, the known
candidate changes in 2010-2024: whether the equity index daily settlement was at 15:15 CT in some early years and
when it moved; grains (the 2012-2015 trading-hours changes, and whether the settlement minute moved); livestock
(trading-hours changes, e.g. the day-session open); gold and copper settlement windows; energy (CL, NG); Treasuries
and FX (13:59-14:00 CT windows); TN and UB from listing.

O_p: tabulate the day-session open per product and period from the FROZEN group calendars, which are the authority:
data/calendars/<group>.py (SESSIONS, SessionSpec.day_session_ct, valid_from/valid_to; 2019 on) and
data/calendars/hist2010/<group>.json (2010-2019; six groups: energy, equity, rates, fx, metals, grains). Livestock
2010-2019 is being built in parallel by another worker (Task 3b): for LE and HE 2010-2019 source O_p yourself and mark
it "cross-check against Task 3b". Where a source of yours disagrees with a frozen calendar's day_session_ct, report
the disagreement; do not override the calendar. Also report the day-session close C from the calendars beside S_p.

Sources (web allowed; brief_common.md terms rules): CME's site and its archives are forbidden. Candidate permitted
sources: cftc.gov (CME's rule self-certification and submission filings hosted by the CFTC often state settlement
procedure changes and effective dates; E.13 saved CFTC's web policy and robots.txt under
reports/stage_e13_briefs/pages/InfoSource/; read them first), the Federal Register, published papers (for example
Baltussen, Da, Lammers and Martens 2021 JFE, on disk as reports/stage_e13_briefs/pages/InfoSource/baltussen_etal_2021_jfe.md),
broker or data-vendor contract specification pages whose terms allow automated access, exchange rulebook passages
quoted by a permitted source. Pages under reports/stage_e1[2-4]_briefs/pages/ that are NOT cmegroup.com copies may be
reused if their terms were checked (say which).
Grades per period and per change date: "primary" (exchange rule text, exchange notice or regulatory filing quoted
verbatim from a permitted host), "secondary" (peer-reviewed paper, government or data-vendor documentation, broker
contract page that states the time), "weak" (forum, undated or unattributed page), "unsourced". A period's grade is
its best supporting source. Every citation carries a verbatim quote from the saved page, or is marked [unverified].

Outputs:
1. reports/stage_e16_settlement.json, schema "stage_e16_settlement/1":
   {"schema": "stage_e16_settlement/1", "generated_pdt": "...", "window": ["2010-06-07", "2024-02-29"],
    "products": {"NQ": {"group": "equity",
        "settle": [{"from": "YYYY-MM-DD", "to": "YYYY-MM-DD", "minute_ct": "HH:MM", "window_ct": "HH:MM:SS-HH:MM:SS",
                    "grade": "primary|secondary|weak|unsourced", "source_ids": ["S1"], "note": "..."}],
        "day_open": [{"from": ..., "to": ..., "minute_ct": "HH:MM", "grade": ..., "source_ids": [...],
                      "calendar": "data/calendars/... or hist2010/... or task3b-pending"}],
        "day_close_calendar": [{"from": ..., "to": ..., "minute_ct": "HH:MM", "calendar": "..."}],
        "change_dates": [{"date": "YYYY-MM-DD", "what": "...", "grade": ..., "source_ids": [...]}]}, ...},
    "sources": {"S1": {"url": "...", "file": "reports/stage_e16_briefs/pages/settlement/...", "fetched_utc": "...",
                "sha256": "...", "grade": "...", "terms_checked": "file or note", "quote": "verbatim passage"}}}
   The settle and day_open periods of every product tile 2010-06-07..2024-02-29 exactly (contiguous, no gap, no
   overlap). Where a change date is known only to the month or not at all, write the uncertain span as its own period
   graded by what you have and explain in "note"; the lead rules on it.
2. reports/stage_e16_settlement.md: method, the per-product table (product, period, S_p, window, grade, sources,
   O_p, calendar C), the change list, disagreements with the frozen calendars, what stayed unsourced, the fetch log
   summary. Page files under reports/stage_e16_briefs/pages/settlement/ and the log
   reports/stage_e16_briefs/pages/settlement/fetch_log.jsonl.
Boundaries: no market data, no Databento, no code edits; write only the outputs above. Other workers own the overlap
audit, the calendars (livestock, EC-AUC) and base_rules/.
