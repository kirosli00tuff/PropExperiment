# Stage E.6 Task 1b: K7 (MBT) dated-input release check

Agent ReleaseChecker-OpusMed (opus, medium). Run 2026-09-27 21:30-21:50 PDT. Machine-readable rows: reports/stage_e6_release_check.json. Evidence pages saved raw under reports/stage_e6_briefs/pages/ (sha256, fetch URL and UTC fetch time per page in the JSON). No bar or parquet file opened; no bar loader called.

Web use: 2 WebSearch calls (URL discovery only, no fact taken from a search summary). No budget or cost notice from WebSearch. Wayback CDX and page fetches by curl. No Scrapling or Firecrawl needed. A PostToolUse hook printed "COST CRITICAL: session total ~$98.31" notices (informational); web searching had already ended.

## A. EC-MBTX: MBT last trading days, research window

CME rule text (verbatim, pdftotext check passed for all six quotes):

- R1 CME Rulebook Chapter 348 Micro Bitcoin Futures, 34802.F (Wayback 2021-06-18): "Trading in expiring futures shall terminate at 4 p.m. London time on the last Friday of the contract month. If that day is not a business day in both the UK and the US, trading shall terminate on the preceding day that is a business day for both the UK and the US. Trading shall terminate at 4 p.m. London time on the Last Trade Date." (reports/stage_e6_briefs/pages/cme_rulebook_ch348_20210618142330.pdf, sha256 a927b0e56524c53c..., via https://web.archive.org/web/20210618142330id_/https://www.cmegroup.com/content/dam/cmegroup/rulebook/CME/III/300/348.pdf)
- R2 CME Rulebook Chapter 348 Micro Bitcoin Futures, 34802.F (Wayback 2026-01-09; same text in captures 2023-12-03, 2024-02-18): "Trading in expiring futures shall terminate at 4 p.m. London time on the last Friday of the contract month if that day is a business day in either the UK or the US. If that day is not a business day in both the UK and the US, trading shall terminate on the preceding day that is a business day in either the UK or the US." (reports/stage_e6_briefs/pages/cme_rulebook_ch348_20260109172553.pdf, sha256 c737466581e754be..., via https://web.archive.org/web/20260109172553id_/https://www.cmegroup.com/content/dam/cmegroup/rulebook/CME/III/300/348.pdf)
- R3 CME Rulebook Chapter 348, 34803.A Final Settlement Price (Wayback 2026-01-09): "For a futures contract for a given delivery month, the Final Settlement Price shall be the BRR published at 4 p.m. London time on the Last Trade Date (Rule 34802.F.)." (reports/stage_e6_briefs/pages/cme_rulebook_ch348_20260109172553.pdf, sha256 c737466581e754be..., via https://web.archive.org/web/20260109172553id_/https://www.cmegroup.com/content/dam/cmegroup/rulebook/CME/III/300/348.pdf)
- R4 CME Rulebook Chapter 348, 34801 (Wayback 2026-01-09): BRR defined: "Each futures contract shall be valued at 0.10 bitcoin as defined by the CME CF Bitcoin Reference Rate (“BRR”)." (reports/stage_e6_briefs/pages/cme_rulebook_ch348_20260109172553.pdf, sha256 c737466581e754be..., via https://web.archive.org/web/20260109172553id_/https://www.cmegroup.com/content/dam/cmegroup/rulebook/CME/III/300/348.pdf)
- R5 CME Rulebook Chapter 350 Bitcoin Futures, 35002.F (Wayback 2021-09-22): old wording: "Trading in expiring futures shall terminate at 4pm London time on the last Friday of the contract month. If that day is not a business day in both the UK and the US, trading shall terminate on the preceding day that is a business day for both the UK and the US." (reports/stage_e6_briefs/pages/cme_rulebook_ch350_20210922.pdf, sha256 568e9849d1481833..., via https://web.archive.org/web/20210922062530id_/https://www.cmegroup.com/content/dam/cmegroup/rulebook/CME/IV/350/350.pdf)
- R6 CME Rulebook Chapter 350 Bitcoin Futures, 35002.F (Wayback 2021-10-26; identical in 2024-07-01): "Trading in expiring futures shall terminate at 4 p.m. London time on the last Friday of the contract month if that day is a business day in either the UK or the US. If that day is not a business day in both the UK and the US, trading shall terminate on the preceding day that is a business day in either the UK or the US." (reports/stage_e6_briefs/pages/cme_rulebook_ch350_20211026.pdf, sha256 0609fe1ec0622a88..., via https://web.archive.org/web/20211026123841id_/https://www.cmegroup.com/content/dam/cmegroup/rulebook/CME/IV/350/350.pdf)

The rule wording changed: ch. 350 (BTC) reads "business day in both ... for both" on 2021-09-22 and "business day in either the UK or the US" on 2021-10-26; ch. 348 (MBT) reads "both" on 2021-06-18 and "either" on 2023-12-03, 2024-02-18 and 2026-01-09 (no ch. 348 capture between 2021-06 and 2023-12). The catalog rule (P-K7-033-c, from the 2021 MBT FAQ) is the old "both" wording.

Final settlement: R3 (BRR at 4 p.m. London on the Last Trade Date) and R4 (BRR = CME CF Bitcoin Reference Rate).

Dates: CME product calendar service for BTC (product 8478), Wayback captures 2023-12-07 and 2024-09-29 (the latest capture found; CDX prefix search of CmeWS/mvc/ProductCalendar from 2024 found no later BTC or MBT capture; MBT product 9024 has none). BTC and MBT carry the same termination rule and BRR settlement. T_exp = 16:00 Europe/London in America/Chicago (zoneinfo), on the verdict date.

| Month | Rule date | Wkday | CME last trade (captures) | Verdict | T_exp CT |
|---|---|---|---|---|---|
| 2025-04 | 2025-04-25 | Fri | none | unverifiable | 10:00 (2025-04-25) |
| 2025-05 | 2025-05-30 | Fri | none | unverifiable | 10:00 (2025-05-30) |
| 2025-06 | 2025-06-27 | Fri | BTCM25 27 Jun 2025 (20231207); BTCM25 27 Jun 2025 (20240929) | keep | 10:00 (2025-06-27) |
| 2025-07 | 2025-07-25 | Fri | none | unverifiable | 10:00 (2025-07-25) |
| 2025-08 | 2025-08-29 | Fri | none | unverifiable | 10:00 (2025-08-29) |
| 2025-09 | 2025-09-26 | Fri | BTCU25 26 Sep 2025 (20240929) | keep | 10:00 (2025-09-26) |
| 2025-10 | 2025-10-31 | Fri | none | unverifiable | 11:00 (2025-10-31) |
| 2025-11 | 2025-11-28 | Fri | none | unverifiable | 10:00 (2025-11-28) |
| 2025-12 | 2025-12-24 | Wed | BTCZ25 24 Dec 2025 (20231207); BTCZ25 26 Dec 2025 (20240929) | drop | 10:00 (2025-12-26) |
| 2026-01 | 2026-01-30 | Fri | none | unverifiable | 10:00 (2026-01-30) |
| 2026-02 | 2026-02-27 | Fri | none | unverifiable | 10:00 (2026-02-27) |
| 2026-03 | 2026-03-27 | Fri | BTCH26 27 Mar 2026 (20240929) | keep | 11:00 (2026-03-27) |
| 2026-04 | 2026-04-24 | Fri | none | unverifiable | 10:00 (2026-04-24) |
| 2026-05 | 2026-05-29 | Fri | none | unverifiable | 10:00 (2026-05-29) |
| 2026-06 | 2026-06-26 | Fri | none | unverifiable (after window, record only) | 10:00 (2026-06-26) |

Research window (14 months 2025-04..2026-05): keep 3, drop 1, unverifiable 10.

- 2025-12 drop: CME 2024-09-29 capture: `"contractMonth":"Dec 2025","productCode":"BTCZ25","firstTrade":"02 Jan 2024","lastTrade":"26 Dec 2025"` (btc_productcalendar_8478_20240929143552.json). The earlier 2023-12-07 capture shows `"lastTrade":"24 Dec 2025"`. The 26 Dec date matches the "either" wording (26 Dec 2025 is a US business day) and E.2a's bar check (expiring contract stops 09:59 CT Fri 12-26, reports/stage_e2a_calendar_bar_checks.md line 672). T_exp on 2025-12-26: 10:00 CT.
- 10 months unverifiable: no CME calendar capture lists them. For each, the rule date is the last Friday and is a business day in both countries, so the "both" and "either" wordings give the same date (rule_rows in the JSON).
- T_exp is 11:00 CT on 2025-10-31 and 2026-03-27, and 10:00 CT on every other date, as expected.

Recorded only (outside the research window): across all CME captures (53 contract-month points, 2021-05..2026-06), the old "both" rule and CME disagree twice: 2021-12 (CME 31 Dec 2021 in the 2021-05-06 capture; the catalog rule gives 2021-12-30, because 31 Dec 2021 is the OPM-observed New Year holiday) and 2025-12 (above). The 2021-12 point bears on the catalog's confirmation-window list. That is the lead's call.

## B. Sunday-evening opens (K7-montrend-01)

Mondays 2025-04-07..2026-06-15: 63. Checked with data.group_session.load_group_calendar('crypto').is_trade_date and rules.sessions.flatten_time_ct('MBT', d). Mondays that fail either check: 5.

| Monday | is_trade_date | flatten_ct | BOOKED_FORWARD | CME trade date |
|---|---|---|---|---|
| 2025-05-26 | False | 11:30 | Memorial Day | 2025-05-27 |
| 2025-09-01 | False | 11:30 | Labor Day | 2025-09-02 |
| 2026-01-19 | False | 11:45 | Martin Luther King Jr. Day | 2026-01-20 |
| 2026-02-16 | False | 11:45 | Presidents Day | 2026-02-17 |
| 2026-05-25 | False | 11:45 | Memorial Day | 2026-05-26 |

Every failing Monday is a BOOKED_FORWARD US holiday. All 58 other Mondays are trade dates with flatten 15:08. Mondays 2026-06-01, 06-08 and 06-15 fall in the 24/7 regime, with no Sunday 17:00 open. They pass both checks.

Citations (from reports/stage_e2a_calendar_sources_crypto.json, no new fetch):
- cme_crypto_24_7_launch (status): "Beginning Friday, May 29 at 4:00 p.m. CT , CME Group Cryptocurrency futures and options will trade continuously on CME Globex with at least a two-hour weekly maintenance period over the weekend." (https://www.cmegroup.com/media-room/press-releases/2026/2/19/cme_group_to_launch247cryptocurrencyfuturesandoptionstradingonma.html, via https://web.archive.org/web/20260219141120id_/https://www.cmegroup.com/media-room/press-releases/2026/2/19/cme_group_to_launch247cryptocurrencyfuturesandoptionstradingonma.html, sha256 e3190d96cf4a2cce...)
- cme_crypto_24_7_launch (time): "CME Group, the world's leading derivatives marketplace, today announced it launched 24/7 trading for Cryptocurrency futures and options. The expanded trading hours, which went live on Friday, May 29, mark a significant milestone" (https://www.cmegroup.com/media-room/press-releases/2026/6/01/cme_group_announceslaunchof247cryptocurrencyfuturesandoptionstra.html, via https://web.archive.org/web/20260602010915id_/https://www.cmegroup.com/media-room/press-releases/2026/6/01/cme_group_announceslaunchof247cryptocurrencyfuturesandoptionstra.html, sha256 f03c03399b564fe1...)
- cme_crypto_hours_5day (Sunday 17:00 CT open): "Trading Hours Sunday - Friday 6:00 p.m. - 5:00 p.m. (5:00 p.m. - 4:00 p.m/ CT) with a 60-minute break each day beginning at 5:00 p.m. (4:00 p.m. CT)" (https://www.cmegroup.com/trading/equity-index/us-index/bitcoin_contract_specifications.html, via https://web.archive.org/web/20190603151021id_/https://www.cmegroup.com/trading/equity-index/us-index/bitcoin_contract_specifications.html, sha256 b1e2766cd25e1283...)
- cme_crypto_hours_5day (MBT FAQ): "CME Globex: Sunday - Friday 6:00 p.m. - 5:00 p.m. ET (5:00 p.m. - 4:00 p.m. CT) with a 60-minute break each day beginning at 5:00 p.m. ET (4:00 p.m. CT)" (https://www.cmegroup.com/education/articles-and-reports/micro-bitcoin-futures-frequently-asked-questions.html, via https://web.archive.org/web/20210330123221id_/https://www.cmegroup.com/education/articles-and-reports/micro-bitcoin-futures-frequently-asked-questions.html, sha256 93a5b74aedccaa70...)

## C. E.2a L-9 guard (code and tests only)

- data/stage_e_bars.py (15-28, 104-134): Every row is booked to its CME trade date by the crypto group calendar; the whole leg is refused (HoldoutRowRefused) if any row books to a trade date >= 2026-06-22 (holdout-1) or outside the research store range 2025-04-01..2026-06-19; the check runs on the whole file before any row is returned. Docstring: "This is how MBT's 1,617 bars of 2026-06-18 16:02 CT .. 2026-06-20, which CME books to trade date 2026-06-22 (ruling L-9), are refused even when the file labels them otherwise".
- data/trade_date_guard.py (19-31, 142-170): refuse_holdout_bookings refuses any minute booked to a holdout-1 trade date (>= data.splits.HOLDOUT_START, 2026-06-22) on every purchase path (ruling L-9).
- screening/stage_e_runner.py (27-31, 73-81, 423-455): Bars per leg come only from data.stage_e_bars.load_research_leg / load_confirmation_leg; the window is member_window(frames, store).
- screening/stage_e_align.py (11-19, 45-46, 74-77): Rule UR-1: UNSEEN_ROLL_DATES = (2026-06-18, 2026-06-19) are removed from every research window (excluded["unseen_roll_UR-1"]).
- screening/stage_e_rules.py (505-509): _opening_refusal: a bar whose trade date is not a window date gets Refusal("engine_not_a_window_date"), so no opening on 2026-06-18.
- screening/stage_e_engine.py (618-653, 683-685): run_engine steps through every minute of the loaded frames (iter_minutes over the full leg frame), not only window dates. The 2026-06-18 trade-date bars (Wed 06-17 ~16:00/17:00 CT to Thu 06-18 16:00 CT) are therefore present in the frame and passed to the member at each step (Run.step calls self.ask_member(ts, bars) at line 653 for every stepped minute; ask_member itself not traced further); openings on that date are refused by the rules. For the lead: whether "reaches a member" covers bars seen but not tradable.
- reports/stage_e2a_bars.json (products.MBT): last_trade_date "2026-06-18"; window_trade_dates ["2025-04-01","2026-06-19"]; drops.trade_date_after_window {"2026-06-22": 1617}, span first_ct "2026-06-18 Thu 16:02", last_ct "2026-06-20 Sat 18:59", booked_from ["2026-06-19"], label "booked to 2026-06-22 (holdout-1 trade date): dropped"; parquet rows 407393 (raw 409010).

Tests (run 21:42-21:43 PDT): `uv run pytest -q tests/test_e2b_trade_date_guard.py` 20 passed; `uv run pytest -q tests/test_stage_e_loader.py` 19 passed; `uv run pytest -q tests/test_stage_e_alignment.py` 10 passed.

Result: No MBT bar booked to a trade date >= 2026-06-19 can reach a member: none are in the file (1,617 dropped at build, all booked to 2026-06-22) and any such row would refuse the whole leg. Bars booked to trade date 2026-06-18 are loaded and stepped through the engine but 2026-06-18 is not a window date (UR-1), so no position can be opened on it. Open point for the lead: the brief says "on or after 2026-06-18". Trade date 2026-06-18 bars are in the loaded frame and stepped, but no position can open on them.

## D. Holiday inputs of the EC-MBTX rule, 2021-01..2026-06

England and Wales (strategy/members/k3/_calendar.py EW_BANK_HOLIDAYS): the code covers 2019-04-19..2026-05-25 (63 dates, 2019-04..2026-06). It has 48 dates in 2021-01..2026-06. Compared with gov.uk bank-holidays.json (fetched 2026-09-28T04:40:30Z, sha256 538b3482c28b85ec...): code-not-gov.uk [], gov.uk-not-code []. The code matches exactly. Source record: reports/stage_e4c_release_check.json line 3942-3943: data/vendor/release_pages/e4b/govuk_bank-holidays.json from https://www.gov.uk/bank-holidays.json; line 4063: "EC-EW: gov.uk JSON covers years 2019..2028; 63 E&W holidays in 2019-04-01..2026-06-30".

EW: 2021-01-01, 2021-04-02, 2021-04-05, 2021-05-03, 2021-05-31, 2021-08-30, 2021-12-27, 2021-12-28, 2022-01-03, 2022-04-15, 2022-04-18, 2022-05-02, 2022-06-02, 2022-06-03, 2022-08-29, 2022-09-19, 2022-12-26, 2022-12-27, 2023-01-02, 2023-04-07, 2023-04-10, 2023-05-01, 2023-05-08, 2023-05-29, 2023-08-28, 2023-12-25, 2023-12-26, 2024-01-01, 2024-03-29, 2024-04-01, 2024-05-06, 2024-05-27, 2024-08-26, 2024-12-25, 2024-12-26, 2025-01-01, 2025-04-18, 2025-04-21, 2025-05-05, 2025-05-26, 2025-08-25, 2025-12-25, 2025-12-26, 2026-01-01, 2026-04-03, 2026-04-06, 2026-05-04, 2026-05-25

US federal holidays, observed dates (OPM federal-holidays page, fetched 2026-09-28T04:40:42Z, sha256 6c3eb6744941eaf0...), OPM tables 2021-2026:
US: 2021-01-01, 2021-01-18, 2021-01-20*, 2021-02-15*, 2021-05-31, 2021-06-18, 2021-07-05, 2021-09-06, 2021-10-11, 2021-11-11, 2021-11-25, 2021-12-24, 2021-12-31*, 2022-01-17, 2022-02-21*, 2022-05-30, 2022-06-20*, 2022-07-04, 2022-09-05, 2022-10-10, 2022-11-11, 2022-11-24, 2022-12-26*, 2023-01-02*, 2023-01-16, 2023-02-20*, 2023-05-29, 2023-06-19, 2023-07-04, 2023-09-04, 2023-10-09, 2023-11-10*, 2023-11-23, 2023-12-25, 2024-01-01, 2024-01-15, 2024-02-19*, 2024-05-27, 2024-06-19, 2024-07-04, 2024-09-02, 2024-10-14, 2024-11-11, 2024-11-28, 2024-12-25, 2025-01-01, 2025-01-20, 2025-02-17*, 2025-05-26, 2025-06-19, 2025-07-04, 2025-09-01, 2025-10-13, 2025-11-11, 2025-11-27, 2025-12-25, 2026-01-01, 2026-01-19, 2026-02-16*, 2026-05-25, 2026-06-19, 2026-07-03*, 2026-09-07, 2026-10-12, 2026-11-11, 2026-11-26, 2026-12-25  (* = OPM observed-day marker)
- OPM 2022 table lists Friday, December 31, 2021 * (New Year's Day 2022 observed); it is in the list under 2021-12-31.
- OPM lists Inauguration Day 2021-01-20 (DC-area employees only); excluded from the rule's US holiday set. 2025-01-20 Inauguration Day coincides with MLK Day (deduplicated).

Good Friday 2021-2026 (data/cme_calendar.py HOLIDAYS): 2021-04-02, 2022-04-15, 2023-04-07, 2024-03-29, 2025-04-18, 2026-04-03

Using these lists, the catalog's "both" rule reproduces the catalog exactly: research 14 dates match True; confirmation 34 dates 2021-05-28..2024-02-23, including 2021-12-30 (True) and 2022-03-25 (True). The "either" wording differs only in 2021-12 (31st) and 2025-12 (26th).

## E. Splice and roll blackout, record only

Splice trade dates: reports/stage_e2a_bars.json products.MBT.rolls.splice_trade_dates (from data/vendor/databento/rolls/MBT_v_0_2025-04-01_2026-06-21_symbology.json; metadata, no bars). The blackout is the splice trade date plus the 2 crypto trade dates before it (crypto calendar).

| Rule date | Next splice | Blackout dates | In blackout |
|---|---|---|---|
| 2025-04-25 | 2025-04-28 | 2025-04-24, 2025-04-25, 2025-04-28 | True |
| 2025-05-30 | 2025-06-02 | 2025-05-29, 2025-05-30, 2025-06-02 | True |
| 2025-06-27 | 2025-06-30 | 2025-06-26, 2025-06-27, 2025-06-30 | True |
| 2025-07-25 | 2025-07-28 | 2025-07-24, 2025-07-25, 2025-07-28 | True |
| 2025-08-29 | 2025-09-02 | 2025-08-28, 2025-08-29, 2025-09-02 | True |
| 2025-09-26 | 2025-09-29 | 2025-09-25, 2025-09-26, 2025-09-29 | True |
| 2025-10-31 | 2025-11-03 | 2025-10-30, 2025-10-31, 2025-11-03 | True |
| 2025-11-28 | 2025-12-01 | 2025-11-26, 2025-11-28, 2025-12-01 | True |
| 2025-12-24 | 2025-12-29 | 2025-12-24, 2025-12-26, 2025-12-29 | True |
| 2026-01-30 | 2026-02-02 | 2026-01-29, 2026-01-30, 2026-02-02 | True |
| 2026-02-27 | 2026-03-02 | 2026-02-26, 2026-02-27, 2026-03-02 | True |
| 2026-03-27 | 2026-03-30 | 2026-03-26, 2026-03-27, 2026-03-30 | True |
| 2026-04-24 | 2026-04-27 | 2026-04-23, 2026-04-24, 2026-04-27 | True |
| 2026-05-29 | 2026-06-01 | 2026-05-28, 2026-05-29, 2026-06-01 | True |
| 2025-12-26 (CME date) | 2025-12-29 | 2025-12-24, 2025-12-26, 2025-12-29 | True |

Survivors (expiry date outside the blackout): research window 0 of 14. 2021-05-03..2024-02-29: not computable: reports/stage_e0_symbology.json holds only "intervals": 62 for MBT.v.0, no dates; no MBT roll file for 2019-2024 on disk. The 2026-06-26 date has no later splice in the research symbology.

## Not finished or not verifiable

- A: 10 of 14 research-window months have no CME calendar source (no Wayback capture of the BTC or MBT calendar service after 2024-09-29). They stay unverifiable.
- A: the date of the MBT (ch. 348) wording change lies between the 2021-06-18 and 2023-12-03 captures. The BTC (ch. 350) change lies between 2021-09-22 and 2021-10-26.
- E: the confirmation-window splice dates could not be computed. reports/stage_e0_symbology.json has counts only, and no 2019-2024 MBT roll metadata is on disk.
- C: the member-visibility question for trade date 2026-06-18 is left to the lead.
