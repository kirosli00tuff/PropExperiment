# Stage E.14 Task 3: the GEX file (test C2)

Lead: Opus 5.5 xhigh, 2026-10-05 00:38-01:50 PDT (the stop ruled at 01:34). Prompt: docs/prompts/STAGE_E.14.md, Task 3. Draft:
reports/stage_e13_prereg_gexmom.md sections 2, 7 and 9. Evidence: reports/stage_e14_briefs/pages/gex/ (pages,
fetch log, Wayback captures) and reports/stage_e14_briefs/gex/ (the CSV, its headers, the fetch record). The CSV and
the Wayback copies of it are listed in DO_NOT_COMMIT.txt and stay on disk, uncommitted.

## Result: C2 STOPS on its power rule, before its freeze and registration

The count of eligible dates with GEX < 0 in 2011-05-03..2019-04-30, under the timing rule and the Task 2 equity
calendar, is **135** (of 1,987 calendar-eligible dates; share 0.068). Under 200, so the minimum-power stop of the
draft's section 7 fires: "if fewer than 200 eligible GEX < 0 dates exist, power is below about 0.5 even at a
per-trade Sharpe of 0.14. The stage then stops before the purchase and reports, and the user decides."

The stop does not depend on the calendar: over every weekday d in the window, at most **146** have a negative
lag-1 GEX row, whatever the CME calendar says (computed from the CSV's dates alone; a row can serve only the
weekdays up to the next CSV date). So no calendar correction can bring the count to 200.

Consequences (prompt Task 3 and Task 4): C2 is not frozen, not registered (N stays 471 for it), and nothing is
bought; E14_SESSION_CAP_USD stays 0.00 in harness v10. The fresh ES quote was already taken ($10.109048, 96 of 96
chunks, $0.00 ledger lines; reports/stage_e14_quotes_es2011.json) and is reported in reports/stage_e14_purchase.md.

## 1. Terms (read before the fetch)

| Page | Fetched (UTC) | sha256 | Finding |
|---|---|---|---|
| https://squeezemetrics.com/monitor/terms | 2026-10-05T07:38:50Z | 695c1bbd930b8930777190e1fc966b26f35fa12dcb798ed99977c0cd132c169d | "As a user of the Platform, you agree not to: ... systematically retrieve data or other content from the Platform to create or compile, directly or indirectly, a collection, compilation, database, or directory without written permission from us; ... creating user accounts by automated means or under false pretenses" |
| https://squeezemetrics.com/robots.txt | 2026-10-05T07:38:51Z | d465172175d35d493fb1633e237700022bd849fa123164790b168b8318acb090 | HTTP 404: no robots rules |
| https://squeezemetrics.com/monitor/dix | 2026-10-05T07:38:51Z | f8fc33b0d6b88dc815660bf6864c98e6b970ca98842b929b0b89193945701526 | the free DIX page; "Gamma Exposure (GEX) is a dollar-denominated measure of option market-makers' hedging obligations." |
| https://squeezemetrics.com/monitor/static/js/dix.js | 2026-10-05T07:39:18Z | 145e00f742bdc4bfce351c2d047e0ffb4ed25349b230b4f91d95e3f57046de9e | the page's download button: `window.location = '/monitor/static/DIX.csv';` and the chart loads `d3.csv('/monitor/static/DIX.csv?_t=' ...)` for every visitor |

Lead ruling: the terms bar systematic retrieval to compile a database without permission, not the single download
of a file the free page offers through its own button. One download, for one registered test, kept uncommitted and
not redistributed, is not forbidden. C2 was therefore not stopped by its terms rule.

What was actually done (Fable F-V1): the CSV was fetched once with curl carrying browser-like headers
(`-A "Mozilla/5.0 ..."`, the CLAUDE.md fetch order), not by clicking the page's button; eight further copies came
from the Wayback Machine (archive.org's own retrieval, not a retrieval from the Platform). The terms' "automated
means" clause concerns account creation. Neither act is one the quoted terms forbid; the ruling's conclusion
stands. The Wayback copies of the CSV are also outside the prompt's source list (open choices 16; FreezeReviewer
F-08).

## 2. The file (fetched once)

- URL https://squeezemetrics.com/monitor/static/DIX.csv, fetched 2026-10-05T07:43:01Z (curl, browser headers),
  HTTP 200, `Last-Modified: Fri, 02 Oct 2026 21:57:14 GMT`.
- sha256 **51bef9ea5ee13af2f72b14f4198de57eeb865a36c1d3e244a3f64b3603e9ce62**, 222,563 bytes, 3,879 data rows,
  header `date,price,dix,gex`, first row 2011-05-02, last row 2026-10-02. Stored at
  reports/stage_e14_briefs/gex/DIX.csv (mode 0444, uncommitted).
- The same bytes as the Wayback capture of 2026-10-02 23:28:47 UTC (sha256 equal).

## 3. Timing rule: lag 1 (the row dated on the latest CSV date strictly before d)

The draft: use the row of the latest trading day strictly before d, or two days back if SqueezeMetrics documents
that a row dated d-1 can be published after 14:30 CT on d. No SqueezeMetrics page states a publication time. The
facts, from SqueezeMetrics' public CSV page and Wayback captures of it (no other source):
- the server's Last-Modified on the file whose last row is 2026-10-02 is 21:57:14 GMT = 16:57 CT on 2026-10-02;
- the Wayback captures of the CSV at 2020-12-03 23:20:00, 2025-04-29 23:17:57, 2026-09-09 23:39:27, 2026-09-10
  23:45:59, 2026-09-11 23:55:26 and 2026-10-02 23:28:47 UTC (17:20 to 18:55 CT) each already hold that same day's
  row (reports/stage_e14_briefs/pages/gex/wayback/capture_last_dates.txt; only last-row dates were read).
Also (Fable F-V4): the capture of Monday 2022-12-05 14:19 UTC (08:19 CT, before 14:30 CT) already holds the row
dated Friday 2022-12-02. So the row dated d-1 is public by the evening of d-1, before 14:30 CT on d: lag 1. Disclosed limits: the evidence
covers 2020-2026 publication practice; whether the 2011-2019 rows were published in real time is not observable
(they were most likely computed later).

Revision check (hashes only, no value read): the 2,012 rows dated 2011-05-02..2019-04-30 hash identically (all
columns: d3c8bc82111499f0...; date and gex: 0ec46859ebf506d9...) in the captures of 2020-11-29, 2020-12-03,
2022-12-05, 2025-04-29, 2026-09-09, 09-10, 09-11, 10-02 and the fresh file. They were not revised after 2020.

## 4. The count (the one read of GEX values before an evaluation)

Script reports/stage_e14_briefs/gex_count.py (calendar and GEX date and sign only; prints counts only), run at
01:33 PDT on the equity calendar as first written (reports/stage_e14_cal_equity.json sha256 5a93e51f...):

| Count | Value |
|---|---|
| CME equity trade dates in 2011-05-03..2019-04-30 | 2,064 |
| excluded: early halt or late open | 77 |
| excluded: unsourced | 0 |
| excluded: no prior trade date / no GEX row | 0 / 0 |
| calendar-eligible dates | 1,987 |
| calendar-eligible dates with GEX < 0 (lag 1) | **135** (share 0.0679) |
| calendar-free upper bound (any calendar) | 146 |
| GEX < 0 rows among the 2,011 rows dated 2011-05-02..2019-04-29 | 138 (share 0.0686) |

The roll blackout and bar presence (which need the bought data) could only lower the count. Two readings recorded
by the Fable verifier: 44 of the 1,987 eligible dates take a lag-1 row older than the prior CME trade date (that
prior date was a CME trading day with no CSV row, mostly an equity early-halt day); the strictest reading of the
draft's timing sentence drops them and gives 131 (F-V2). One eligible date's lag-1 row has GEX exactly 0, counted
as not negative ("GEX < 0"; F-V5). Every reading stops C2.

Incident (Fable F-V6): the verifier's first look at the CSV (`head -3`) printed the price, DIX and GEX values of the
rows dated 2011-05-02 and 2011-05-03 into its context before its redaction applied. That was after C2's stop; no
evaluation exists for it to bias, and nothing was derived from them. Any future C2-like pre-registration must
disclose it. The draft expected a
share near the paper's 48% for its own NGE measure and warned that "SqueezeMetrics' GEX column is a different
construction, so its share may differ"; its share in this window is about 7%. At 135 trades T1 sits below the
draft's 0.10-share power row (0.10 / 0.28 / 0.55 at a per-trade Sharpe of 0.05 / 0.10 / 0.15, for about 190
trades).

Cross-check (01:50 PDT): v10's own helper, an independent implementation (`python -m screening.stage_e14_c2 count
--gex-lag 1`, on data/calendars/hist2010/equity.json, the same bytes), gives the same figures: 2,086 weekdays,
2,064 trade dates, 1,987 eligible (excluded: 71 early halts, 6 late opens, 22 not trade dates), **135** with
GEX < 0, 0 unsourced (reports/stage_e14_briefs/gex_count_v10helper.out).

Final equity calendar (reports/stage_e14_cal_equity.json, last written 02:26:02, sha256
b12aee433635bc8334adb15d8f06c21255b0cb24889ea123a4d4375fb22657be, the same bytes as
data/calendars/hist2010/equity.json): both implementations rerun at 02:29 PDT give identical figures, **135** of
1,987 (reports/stage_e14_briefs/gex_count_final.out, gex_count_v10helper_final.out). The Fable verifier recomputes
the count independently (Task 8).
