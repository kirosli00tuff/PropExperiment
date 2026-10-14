### 3.1 Literature check (Step 1; before any bar)

Each F4 rule was checked against its primary source. The quotes are in the reader reports:
reports/stage_e21_briefs/spec_trend.md, spec_tom.md and spec_post2010.md. The rulings are in
lead_spec section A.

| Item | Primary source | Result | Freeze |
|---|---|---|---|
| T1 signal, hold, 40%/sigma, equal-weight average | MOP 2012, pp.231-236 | MATCH | as F4 |
| T1/T2 lookback across rolls | MOP p.231 (compounds the held contract's daily returns) | MATCH. h2.chained_return splits at every recorded splice; the reader's "MISMATCH risk" was rejected (A1) | lead_spec 1 |
| Volatility: 261, EWMA-mean demeaning, returns strictly before d | MOP eq. 1, p.233 | Prompt SILENT; the paper's terms adopted | lead_spec 2 |
| Warm-up, floor, cap | MOP: none | SILENT; 60 returns [LEAD]; no floor and no cap | A3, A4 |
| T2: 1/3/12 lookbacks, equal weights, monthly | HOP 2017, p.3 | MATCH | as F4 |
| T2 book scaled to a 10% ex-ante volatility (3-year covariance) | HOP 2017, p.3 and endnote 7 | MISMATCH, NOT adopted; declared deviation (A6) | T2 as F4 |
| T3 window: days -1, +1, +2, +3, close to close | McConnell-Xu (WP Table 1); Lakonishok-Smidt via McConnell-Xu | MATCH | day -2 = the month's second-to-last trade date |
| T3 parenthetical "(two trade dates before the month's last)" | as above | MISMATCH: it describes day -3; corrected (A8) | lead_spec 5 |
| T3 day numbering | the papers count NYSE trading days | MISMATCH, found in the calendar-only counts: the futures calendar books US holidays as trade dates; T3 renumbered on NYSE days (A12) | lead_spec 5, A12 |
| T3 volatility scaling | the papers do not scale | the prompt's choice, kept | lead_spec 5 |

Published post-2010 comparison (not part of any verdict):

| Source | Period | Universe | Gross / net | Sharpe | Where |
|---|---|---|---|---|---|
| AQR TSMOM factor (MOP update; computed by SpecReaderPost2010 from AQR's file) | 2010-07..2024-02 (164 months) | AQR's MOP universe | gross (no costs or fees) | 0.389 (t 1.44) | spec_post2010.md P1 |
| Same | 2010-01..2026-05 | same | gross | 0.402 (t 1.63) | P2 |
| SG Trend Index (computed from AQR's fund workbook) | 2010-07..2024-02 | about 10 largest trend CTAs | net of fees and costs | 0.352 (t 1.30) | P4 |
| SG Trend Index (E.13) | 2010-2025 | same | net | 0.24 | P5; stage_e13_trend_carry.md |
| HOP 2017 Exhibit 2: 12-month signal | 2010-2016 | 67 markets | gross | 0.73 | spec_trend.md (read from an exhibit image by eye; not checked by a second reader) |
| HOP 2017 Exhibit 1: the 1/3/12 blend | 2010-2016 | 67 markets | net of costs and 2/20 fees | 0.41 | same caveat |
| Turn of the month, McConnell-Xu | 1987-2005 (after Lakonishok-Smidt) | US cash indexes | gross | 0.15%/day vs -0.00% on other days (t 3.78); weaker in the second half (t 2.00) | spec_tom.md |
| Turn of the month after 2008 | 2010-2018 (Plastun et al., DJIA) and others | cash indexes | gross | mostly decayed (DJIA 0.03%/day on TOM days vs 0.05% on other days) | spec_tom.md |
| Turn of the month in index futures after 2010 | none found | - | - | no peer-reviewed study | spec_post2010.md section 3 |

E.21's T1 (0.50 net) and T2 (0.44 net) sit at or a little above these post-2010 records, after D8
costs, on 17 roots. T3 (0.15) agrees with the decay literature.

### 3.2 PropEd Capital's sourced rules (PropEdReader-OpusHigh)

PropEd's terms (last updated 2026-10-06) forbid "scraping without permission", while robots.txt
allows `/`. The reader therefore made plain one-page fetches only, about 4 s apart, and listed every
saved PropEd page in DO_NOT_COMMIT.txt (kept local, not committed).

**Automation is unresolved.** Terms section 8 says "Copy trading and automated strategies may be used
only where supported and permitted". The FAQ marks "EAs / Bots / Automated" with a red not-allowed
icon. Terms section 5 says the FAQs do not override the plan agreement or the Nexus dashboard, and
neither is public. No public page grants automation for any plan.

**Other rules:**
- Overnight holds are allowed.
- Weekend holds need a paid add-on.
- Listed micros: MES, MNQ, M2K, MGC and MCL. M6E and the micro yield futures are not listed.
- Canada is not on the restricted-countries list.

Ten written questions for PropEd are drafted in reports/stage_e21_proped_rules.md for the user to
send. Nothing was sent.

### 3.3 Per-test results (generated from reports/stage_e21_runs/ by reports/stage_e21_briefs/ret_tables.py)
