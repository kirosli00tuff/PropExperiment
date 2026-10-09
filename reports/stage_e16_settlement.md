# Stage E.16 Task 1: daily settlement minute S_p and day-session open O_p, 2010-06-07..2024-02-29

Worker: SettlementSource-OpusHigh (worker-high, opus). Written 2026-10-09, 00:16-00:39 PDT (times from `date`).
Machine-readable table: `reports/stage_e16_settlement.json` (schema `stage_e16_settlement/1`).
Pages and log: `reports/stage_e16_briefs/pages/settlement/` and its `fetch_log.jsonl`.
No market data was read. No Databento call was made, and no cmegroup.com page or archive of one was fetched or used.

## Method

- **Sources.** Every primary source is a CME, CBOT, NYMEX or COMEX rule self-certification hosted on cftc.gov. I checked the terms first (`cftc_webpolicy.html`: "Government information at the CFTC website is in the public domain"; robots `Content-Signal: search=yes,ai-train=no,use=reference`, `Allow: /`). I fetched each filing with plain curl, saved it raw (PDF), converted it with `pdftotext -layout`, and read it by grep.
- **Secondary source.** One secondary source, Baltussen, Da, Lammers and Martens (2021, JFE), was reused from E.13's disk copy. Its terms were checked in E.13 (EUR portal: personal use only).
- **Verified quotes.** Every quote in the JSON is verbatim from the saved text with whitespace collapsed. The build script checked that each passage is present in its file (0 failures) and that each file's sha256 matches the fetch log.
- **Search.** I ran about 25 WebSearch queries, mostly `site:cftc.gov`. No budget or over-limit notice appeared.
- **O_p and C.** These come from the frozen calendars, read in code only (`SessionSpec.day_session_ct` and the hist2010 `sessions[].day_session_ct`). hist2010 covers dates up to 2019-04-30 and `data/calendars/<group>.py` covers 2019-05-01 on. Both files cover May 2019. lead_spec switches to .py from 2019-05-06, and either split gives the same O. For LE and HE in 2010-2019, I sourced O_p myself and marked it `task3b-pending`.
- **Fields added to the schema (my choices):**
  - `basis` on each period:
    - `direct`: a source dated in, or bracketing, the period states the value.
    - `inferred`: the value is carried from the nearest dated source, with no change found.
    - `direct-secondary`: only a secondary source states the value.
  - `window_ct: null` where no saved source states the window length.
  - `minute_ct: null` for periods before a product's listing.
  - `first_business_day_of_week_minute_ct` for one livestock O_p period.
- **Grade.** A period's `grade` is the class of its best supporting source. Where that support is indirect, `basis` says so. The lead rules on inferred spans.
- **Convention.** S_p is the CT minute at which the settlement window ENDS (lead_spec section 0). ET windows are converted at a fixed ET = CT + 1 h. Both exchanges observe the same DST, so the conversion holds all year.

## Per-product table

Read "sources" against the source list below. Calendar C is the frozen calendar's `day_session_ct` close.

| Product | Period | S_p (CT) | Window (CT) | Grade / basis | Sources | O_p (CT) [calendar] | Calendar C |
|---|---|---|---|---|---|---|---|
| NQ, YM | 2010-06-07..2012-11-18 | 15:15 | 15:14:30-15:15:00 (length unverified pre-2018) | primary / inferred | S02, S40 | 08:30 [hist2010/equity] | 15:00 (disagrees) |
| NQ, YM | 2012-11-19..2020-10-25 | 15:15 | 15:14:30-15:15:00 | primary / direct | S02, S03, S01, S40 | 08:30 [hist2010 to 2019-04-30, equity.py after] | 15:00 (disagrees) |
| NQ, YM | 2020-10-26..2024-02-29 | 15:00 | 14:59:30-15:00:00 | primary / direct | S01 | 08:30 [equity.py] | 15:00 |
| RTY | 2010-06-07..2017-07-09 | none (not listed on CME) | - | primary / direct | S04 | none | (calendar 15:00) |
| RTY | 2017-07-10..2020-10-25 | 15:15 | 15:14:30-15:15:00 | primary / direct | S04, S03, S01 | 08:30 | 15:00 (disagrees) |
| RTY | 2020-10-26..2024-02-29 | 15:00 | 14:59:30-15:00:00 | primary / direct | S01 | 08:30 | 15:00 |
| ZT, ZF, ZN, ZB, UB | 2010-06-07..2014-02-24 | 14:00 | 13:59:30-14:00:00 | primary / inferred | S05, S08, S09 | 07:20 [hist2010/rates] | 14:00 |
| ZT, ZF, ZN, ZB, UB | 2014-02-25..2024-02-29 | 14:00 | 13:59:30-14:00:00 | primary / direct (forward of 2020-05 inferred) | S05, S06, S07, S40 | 07:20 [rates.py from 2019-05-01] | 14:00 |
| TN | 2010-06-07..2016-01-10 | none (not listed) | - | primary / direct | S07 | none | (calendar 14:00) |
| TN | 2016-01-11..2024-02-29 | 14:00 | 13:59:30-14:00:00 | primary / direct | S05, S06, S07, S40 | 07:20 | 14:00 |
| 6E, 6A, 6B, 6C, 6J, 6S | 2010-06-07..2024-02-29 | 14:00 | 13:59:30-14:00:00 | primary / inferred (2008 primary, 2020 secondary bracket) | S10, S40 | 07:20 [hist2010/fx, fx.py] (secondary) | 14:00 |
| 6N | 2010-06-07..2024-02-29 | 14:00 | 13:59:30-14:00:00 (assumed = majors) | secondary / direct-secondary | S40, S10 | 07:20 (secondary) | 14:00 |
| CL, NG | 2010-06-07..2015-07-05 | 13:30 | 13:28:00-13:30:00 | primary / inferred | S11, S15 | 08:00 [hist2010/energy] (secondary) | 13:30 |
| CL | 2015-07-06..2024-02-29 | 13:30 | 13:28:00-13:30:00 | primary / direct to 2018-10, inferred after | S11, S12, S13 | 08:00 [energy.py from 2019-05-01] | 13:30 |
| NG | 2015-07-06..2024-02-29 | 13:30 | 13:28:00-13:30:00 | primary / direct to 2019-09, inferred after | S11, S14 | 08:00 | 13:30 |
| GC | 2010-06-07..2024-02-29 | 12:30 | 12:29:00-12:30:00 | primary / direct (bracketed 2010-02..2023-08) | S16, S17, S18, S19 | 07:20 [hist2010/metals, metals.py] (secondary) | 12:30 |
| HG | 2010-06-07..2017-09-25 | 12:00 | 11:59:00-12:00:00 | primary / inferred (7 years back from 2017) | S17, S40 | 07:10 (secondary) | 12:00 |
| HG | 2017-09-26..2024-02-29 | 12:00 | 11:59:00-12:00:00 | primary / direct | S17, S18, S19 | 07:10 | 12:00 |
| ZC, ZW, ZS, ZM, ZL | 2010-06-07..2012-06-24 | 13:15 | not stated | primary / direct (2012), earlier inferred | S22, S20, S21 | 09:30 [hist2010/grains] | 13:15 to 2012-05-20, then 14:00 (disagrees 2012-05-21..06-24) |
| grains | 2012-06-25..2013-04-07 | **14:00** | not stated | primary / direct | S22, S24 | 09:30 (07:20 floor open on USDA report days from 2012-06-12) | 14:00 |
| grains | 2013-04-08..2015-07-05 | 13:15 | not stated (1:14-1:15 per S25 in 2015) | primary / direct | S24, S25 | 08:30 | 13:15 |
| grains | 2015-07-06..2024-02-29 | 13:15 | 13:14:00-13:15:00 | primary / direct (2015), inferred after | S25, S40 | 08:30 [hist2010 to 2019-04-30, grains.py after] | 13:20 hist2010 (disagrees) / 13:15 grains.py |
| LE, HE | 2010-06-07..2014-12-14 | 13:00 | not stated | primary / **inferred (weakest)** | S27, S28 | 09:05 (task3b-pending) | task3b-pending |
| LE, HE | 2014-12-15..2024-02-29 | 13:00 | 12:59:30-13:00:00 | primary / direct to 2018-10, inferred after | S27, S33, S29, S30, S31 | 2014-10-27..2016-02-28: 08:00 (09:05 first business day of week); 2016-02-29 on: 08:30 (task3b-pending to 2019-04-30, then livestock.py) | livestock.py 13:00 from 2019-05-01 |

The lead's prior (equity 15:00; Treasuries 14:00; FX 14:00; energy 13:30; gold 12:30; copper 12:00; grains 13:15; livestock 13:00) holds except in three places:

- **Equity:** 15:15 until 2020-10-23.
- **Grains:** 14:00 from 2012-06-25 to 2013-04-05.
- **Not listed:** RTY before 2017-07-10 and TN before 2016-01-11.

## Change list (2010-2024; S = settlement minute, O = day open)

| Date (trade date) | Products | What | Grade | Sources |
|---|---|---|---|---|
| 2012-05-21 | grains | Globex extended to 17:00-14:00 CT. Settlement stayed at 13:15 CT (open-auction close). | primary | S20, S21, S22 |
| 2012-06-12 | grains | Floor opens 07:20 CT on major USDA crop-report mornings (not in the calendar) | primary | S23 |
| **2012-06-25** | grains | **S 13:15 -> 14:00**; floor close 14:00 | primary (date = S22's stated intent; S24 confirms the move happened) | S22, S24 |
| 2012-11-19 | NQ, YM | Trading day extended to 16:15. Settlement "remain unchanged at 3:15 p.m. CT". | primary | S02 |
| **2013-04-08** | grains | **S 14:00 -> 13:15**; **O 09:30 -> 08:30** | primary | S24 |
| 2014-02-25 | Treasuries | Settlement document corrected; no change in how settlements are determined | primary | S05 |
| 2014-10-27 | LE, HE | Globex halts 16:00 and restarts 08:00 Tue-Fri; Monday open 09:05 (**O change**) | primary | S26 |
| 2014-12-15 | LE, HE | Settlement = pit+Globex VWAP 12:59:30-13:00:00 (was pit-based; minute 13:00 kept) | primary | S27 |
| 2015-07-06 | CL, NG | Globex-only settlement; window 14:28-14:30 ET unchanged | primary | S11 |
| 2015-07-06 | grains | Globex close 13:15 -> 13:20; settlement window 13:14-13:15 unchanged | primary | S25 |
| 2015-07-06 | LE, HE | Settlement on CME Globex only (pit closed); window 12:59:30-13:00:00 unchanged | primary | S33 |
| 2015-07-06 | LE, HE | Options floor opens 08:00 on business days 2-5 of the week | primary | S28 |
| 2016-01-11 | TN | First trade date | primary | S07 |
| **2016-02-29** | LE, HE | Globex Mon-Fri 08:30-13:05 (**O 08:00 -> 08:30**); settlement period unchanged | primary | S30 |
| 2017-07-10 | RTY | First CME trade date | primary | S04 |
| 2017-10-23 | GC, HG | Procedures standardised; windows unchanged | primary | S17 |
| 2017-11-06, 2018-10-01 | CL | Procedures amended; window unchanged | primary | S12, S13 |
| 2018-02-09 | NQ, YM, RTY | Procedures standardised; time listed 15:15:00 CT | primary | S03 |
| 2018-10-01 | LE, HE | Documents amended; window unchanged | primary | S31 |
| 2019-09-04 | NG | Procedure amended; window unchanged | primary | S14 |
| **2020-10-26** | NQ, YM, RTY | **S 15:15 -> 15:00** (14:59:30-15:00:00) | primary | S01 |
| 2023-08-30 | GC, HG | Documents amended; windows unchanged | primary | S18, S19 |

I found no 2010-2024 settlement-minute change for Treasuries, FX, CL, NG, GC or HG. The calendar regime changes the hist2010 files already record (equity 2012-11-19 and 2015-09-21; rates 2011-10-03; energy and metals 2015-09-21) affect the Globex segments only, not S or O.

## Disagreements with the frozen calendars (reported, not overridden)

1. **Equity C vs S_p.** hist2010/equity.json and equity.py carry C = 15:00 for 2010-06-07..2020-10-25, but the settlement period ended at 15:15 CT then (S02, S03, S01). E.2a recorded the same discrepancy for 2019-2020. From 2020-10-26 C = S_p = 15:00.
2. **Grains C vs S_p, 2012-05-21..2012-06-24.** hist2010/grains.json has C = 14:00 from 2012-05-21 (Globex and open-outcry close). Settlement stayed at 13:15 until 2012-06-22 (S22: "During the week of May 21, settlement prices ... were determined at the close of the open auction trading period at 1:15 p.m."). From 2012-06-25 to 2013-04-05, C = S_p = 14:00.
3. **Grains C, 2015-07-06..2019-04-30.** hist2010/grains.json has C = 13:20 (the Globex close), but the settlement window stayed 13:14-13:15 (S25). grains.py has C = 13:15 from 2019-05-01, so the two frozen grain calendars also disagree with each other over the May 2019 overlap.
4. **Grains O on USDA report days, 2012-06-12..2013-04-05.** The floor opened 07:20, not 09:30 (S23). The calendar has 09:30 on every day. This is noted only.
5. **O_p.** No source of mine contradicts any calendar O. Corroboration:
   - Rates 07:20 (S08, S09, S07).
   - Grains 09:30 and 08:30 with the 2013-04-08 switch (S20, S21, S24).
   - Energy 08:00, gold 07:20 and copper 07:10 (S40 only, secondary). This includes hist2010/energy's O for 2015-09-21..2019-05-31, which that calendar marks UNVERIFIED.
   - Equity 08:30 and FX 07:20 rest on S40 (secondary) and design D6.
6. **Listing dates vs lead_spec U2.** These are for the lead to rule on.
   - **RTY:** the U2 window starts 2017-06-01, but RTY's first CME trade date is 2017-07-10 (S04).
   - **TN:** the U2 window starts 2016-01-04, and U2 says TN was priced 2010-01..2012-05. TN's first trade date is 2016-01-11 (S07), so any "TN" data before 2016-01-11 is not the Ultra 10-Year.

## Livestock O_p for Task 3b to cross-check

| Period | O_p (CT) | Basis |
|---|---|---|
| 2010-06-07..2014-10-26 | 09:05 | S26 "Monday 9:05 a.m. Central Time/CT-Opening"; S28 floor 9:05-13:02 Mon-Fri as of 2015-06. Globex otherwise ran nearly continuously Mon-Thu, so the day open is the pit open. 2010-2014 is not stated directly. |
| 2014-10-27..2016-02-28 | 08:00, but 09:05 on the first business day of the week | S26 (restart 08:00 CT Tue-Fri), S28, S30. **Lead choice needed:** the futures pit kept 09:05 until the 2015-07 pit closure. |
| 2016-02-29..2019-04-30 | 08:30 | S30 |
| 2019-05-01..2024-02-29 | 08:30 | livestock.py |

My sourced livestock day closes, for Task 3b to compare: the pit closed at 13:00 until the 2014-2015 changes, the options floor at 13:02, and Globex closed 13:05 from 2016-02-29 (S30). Settlement is 13:00 throughout.

## What stayed weak or unsourced

- **LE, HE 2010-06-07..2014-12-14.** No saved source states the settlement minute or window. 13:00 is inferred from S27's pit-VWAP rule, which ends at 13:00.
  - Search snippets of 2014 Reuters reprints say livestock settlements were "based solely on pit closing prices at 1 p.m. CT" [unverified]. Those hosts (Glacier Farm Media sites: grainews.ca and others) forbid robots and spiders in their terms, so I did not fetch them; their terms page is saved.
  - farmdoc daily (Univ. of Illinois) refused connections (curl rc 7, also via Scrapling).
- **HG 2010-06-07..2017-09-25.** The copper window is carried back from the 2017 "current" document (S17 Appendix A). No 2010-2016 copper settlement text was found on cftc.gov.
- **6N, all years.** No primary source. S40 (secondary, sample to May 2020) covers U.S.-listed currency futures including the NZ dollar. S10 (2008) lists only the six majors.
- **FX majors.** The only primary source is S10, dated 2008 (before the window). Inside the window, support rests on S40 and the absence of any change found.
- **Settlement windows not stated in any saved source:**
  - grains before 2015-07-06;
  - livestock before 2014-12-15;
  - equity before 2018. The 15:14:30-15:15:00 window is taken from S01's struck text.
- **Forward spans with no restating source** (inferred, no change found): equity after 2020-10; Treasuries after 2016 (S40 to 2020-05); CL after 2018-10; NG after 2019-09; livestock after 2018-10; grains after 2015.
- **CME client wiki not used.** The CME client wiki (cmegroupclientsite.atlassian.net, "Daily Settlement Time Details") was cited by the E.2a/E.14 calendars. It is CME content, so I did not fetch or use it.

## Sources (all cftc.gov unless noted; full quotes, URLs, sha256 and fetch times in the JSON)

S01 CME/CBOT 20-018 (equity 15:15 -> 15:00, trade date 2020-10-26) · S02 CBOT/CME 12-356 (settlement unchanged at 3:15, 2012-11-19) · S03 CME/CBOT 18-008 (table: NQ, RTY, YM 15:15:00 CT, 2018-02-09) · S04 CME 17-110 (RTY listing, trade date 2017-07-10) · S05 CBOT 14-046 and S06 CME/CBOT 14-075 (Treasury window 13:59:30-14:00:00, 2014) · S07 CBOT 15-572 (TN listing 2016-01-11; settlement at 2:00 p.m. CT) · S08 CBOT 09-177 (UB open outcry 07:20-14:00) · S09 CBOT 10-382R (Treasury options floor 7:20-2:00) · S10 CME 08-96 (FX 30-second closing range ending 2:00 PM CT, 2008) · S11 NYMEX 15-213 (energy 14:28-14:30 ET, Globex-only from 2015-07-06) · S12 NYMEX 17-384 · S13 NYMEX 18-389 (CL) · S14 NYMEX 19-198 (NG) · S15 NYMEX 08.16 (TAS by 2:30 p.m. NY) · S16 COMEX 10-053 (gold 1:29-1:30 p.m. ET from 2010-02-26) · S17 COMEX 17-358 (GC 13:29-13:30 ET, HG 12:59-13:00 ET; current and amended) · S18/S19 NYMEX/COMEX 23-170 (2023-08-30) · S20 CBOT 12-134 · S21 CBOT 12-145 · S22 CBOT 12-188 (grain settlement 1:15 -> 2:00, 2012-06-25) · S23 CBOT 12-157 · S24 CBOT 13-092 (grain settlement 2:00 -> 1:15, 2013-04-08) · S25 CBOT 15-204 (1:14-1:15 settlement window, close 1:20) · S26 CME 14-408 · S27 CME 14-430 · S28 CME 15-164 · S29 CME 15-539 · S30 CME 16-064 · S31 CME 18-342 · S33 CME 15-211 (livestock Globex-only settlement from 2015-07-06) · S40 Baltussen et al. 2021 JFE (secondary; E.13 disk copy).

## Fetch log summary

`fetch_log.jsonl` has 64 entries (58 HTTP 200).

- **Transient failures:** 4 curl failures (code 000) on cftc.gov robots and two PDFs, all retried successfully.
- **Not found:** thecattlesite terms page (404); that site was not used.
- **Connection refused:** farmdoc daily, by curl and by Scrapling get; not used.
- **Saved but not cited:** a few saved filings turned out to be irrelevant (CBOT 10-240 OTR yield futures, 15-549 and 18-096 fed funds, 23-447 and 24-146 non-Treasury, 16-574 London gold, 12-279, 14-231, 15-067, 10-284, 08-159, the UB options 10-132 and 10-133, 16-186 other equity products, 10-382R used for floor hours only).
- **Size:** about 18 MB of pages.
- **Licensing:** the filings are CME-authored documents hosted by the CFTC. The lead may want them listed in a DO_NOT_COMMIT note, as E.13 did.

Build script, kept outside the repo: `/tmp/claude-1000/-home-kiros-li-Documents-GitHub-PropExperiment/4a9d3866-b27d-4996-9f9a-acc98193de69/scratchpad/build_settlement.py`. It verifies every quote, the sha256 values and exact tiling (0 errors).
