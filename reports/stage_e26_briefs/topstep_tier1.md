# Stage E.26 Task 4: Topstep Tier 1 news window, today's help-center text

Worker: TopstepRulesReader-OpusMed. Source: help.topstep.com only, via curl (no WebFetch or Scrapling fallback needed). Requests were spaced 3 s apart; the E.19 robots check gives Crawl-delay 1. Saved under `reports/stage_e26_briefs/pages/topstep/`. The text extractions (`ts_<id>.txt`) come from `_scripts/extract.py`, an HTML parser that strips script and style. Line numbers below refer to those .txt files.

## Fetch log

| Page id | Final URL (after redirects) | UTC fetch | PDT fetch | HTTP | sha256 raw .html | dateModified (JSON-LD) | Page marker | .txt lines |
|---|---|---|---|---|---|---|---|---|
| 13613539 | https://help.topstep.com/en/articles/13613539-risk-adjustments-high-risk-high-volatility | 2026-10-21T09:20:34Z | 2026-10-21 02:20:34 PDT | 200 | 085db4d216ded09f5ea46b4d3338cf7219de9155a325731680f4636dc4825aa7 | 2026-10-20T19:42:21Z | "Updated today" | 332 |
| 8284211 | https://help.topstep.com/en/articles/8284211-economic-releases | 2026-10-21T09:20:38Z | 2026-10-21 02:20:38 PDT | 200 | 0318517fa9fd7f2f714e206b615eed1c8f7275fffffc2e6cd3dc99d1bd17337a | 2026-10-15T17:51:06Z | "Updated this week" | 70 |
| 10305426 | https://help.topstep.com/en/articles/10305426-prohibited-trading-strategies-at-topstep | 2026-10-21T09:20:41Z | 2026-10-21 02:20:41 PDT | 200 | d0d9be575dba76796584e4ef80c310a934320df0f10d8143db26b333f051cba7 | 2026-06-10T14:02:45Z | "June 10, 2026" ("Updated over 4 months ago") | 68 |

.txt sha256 values: ts_13613539.txt e6c2b078747208f2...; ts_8284211.txt 6840ca06d9f3dee1...; ts_10305426.txt 324de221f38cac74...

## Quotes

All quotes in items 1 to 5 come from page 13613539 (dateModified 2026-10-20T19:42:21Z), section "Tier 1 News Events Restrictions" (HTML anchor `h_bb7f1d281e`), .txt lines 171-332, unless another location is given.

### 1. Accounts covered

- Section lead sentence (L172): "Ahead of Tier 1 News Events (for example, CPI, FOMC, NFP, PPI), Topstep temporarily restricts new opening positions on equity index products and metals in SIM to protect Traders from extreme volatility."
- Two tables follow. The first is headed "Trading Combines & Challenges" (L199). Its rows are "$1.5K, $3K, and $6K Challenges", "$3K Challenge Undead", "$3K Challenge Slasher", "25K", "50K", "100K", "150K", "250K" and "$50K Static". The second is headed "Express Funded Accounts" (L250), introduced by: "Express Funded Accounts (XFAs) have margin that scales with balance. This is called the Scaling Plan. See details on your Maximum Position Size when accounting for both Tier 1 News Event restrictions, and the Scaling Plan." (L251)
- The Tier 1 section does not mention "Live Funded Account". That string appears only in the earlier "Current Restrictions" header (L45-47: "Trading Combine, Express Funded Account," / "Pro Account" / "Live Funded Account"), which belongs to the volatility-restriction section, not to the Tier 1 section.

### 2. Events and windows (CT)

- L173 (Minis line): "...during the 10-minute window surrounding the release (5 minutes before, 5 minutes after)."
- Table "Tier 1 News Events", columns Event / Announcement (CT) / Window (CT) (L180-197), copied cell by cell:

| Event | Announcement (CT) | Window (CT) |
|---|---|---|
| Consumer Price Index (CPI) | 7:30 AM | 7:25 to 7:35 AM |
| FOMC rate decision | 1:00 PM | 12:55 to 1:05 PM |
| FOMC press conference | 1:30 PM | 1:25 to 1:35 PM |
| Non Farm Payroll (NFP/Unemployment Rate) | 7:30 AM | 7:25 to 7:35 AM |
| Producer Price Index (PPI) | 7:30 AM | 7:25 to 7:35 AM |

### 3. Products and caps

- L173: "Minis (ES, RTY, YM, NQ, NKD, GC, SI, HG, PL): No new opening transactions permitted during the 10-minute window surrounding the release (5 minutes before, 5 minutes after)."
- L174: "Micros (MES, M2K, MYM, MNQ, MGC): Opening transactions limited to 1, 3, 6, 9, and 15 contracts for the $25K, $50K, $100K, $150K, and $250K account sizes, respectively, during the window (see table below)"
- L175: "MHG and SIL: Opening transactions limited to 1, 2, 5, 7, 12 contracts for the $25K, $50K, $100K, $150K, and $250K account sizes, respectively, during the window (see table below)"
- L176: "Other products (energies, rates, FX, etc.) are unaffected."
- Combine/Challenge table (L199-249). Columns: Account / Margin / Max micros / Equity Minis / Effect during window.

| Account | Margin | Max micros | Equity Minis | Effect during window |
|---|---|---|---|---|
| $1.5K, $3K, and $6K Challenges | $3,000 | 0 | Blocked | No Trading available |
| $3K Challenge Undead | $50,000 | 3 | Blocked | Capped at 3 micros |
| $3K Challenge Slasher | $20,000 | 1 | Blocked | Capped at 1 micro |
| 25K | $20,000 | 1 | Blocked | Capped at 1 micro |
| 50K | $50,000 | 3 | Blocked | Capped at 3 micros |
| 100K | $100,000 | 6 | Blocked | Capped at 6 micros |
| 150K | $150,000 | 9 | Blocked | Capped at 9 micros |
| 250K | $250,000 | 15 | Blocked | Capped at 15 micros |
| $50K Static | $40,000 | 2 | Blocked | Capped at 2 micros |

- XFA table (L252-301). Columns: Account / Balance / Margin / Minis/Micros / SIL & MHG.

| Account | Balance | Margin | Minis/Micros | SIL & MHG |
|---|---|---|---|---|
| $50K XFA | Below $1500 | $20,000 | 0/1 | 0/1 |
| $50K XFA | $1500-$2000 | $30,000 | 0/1 | 0/1 |
| $50K XFA | Above $2000 | $50,000 | 0/3 | 0/2 |
| $100K XFA | Below $1500 | $30,000 | 0/1 | 0/1 |
| $100K XFA | $1500-$2000 | $40,000 | 0/2 | 0/2 |
| $100K XFA | $2,000-3,000 | $50,000 | 0/3 | 0/2 |
| $100K XFA | Above $3,000 | $100,000 | 0/6 | 0/5 |
| $150K XFA | Below $1500 | $30,000 | 0/1 | 0/1 |
| $150K XFA | $1500-$2000 | $40,000 | 0/2 | 0/2 |
| $150K XFA | $2,000-3,000 | $50,000 | 0/3 | 0/2 |
| $150K XFA | $3,000-$4,500 | $100,000 | 0/6 | 0/5 |
| $150K XFA | Above $4,500 | $150,000 | 0/9 | 0/7 |

- Challenge-specific Tier 1 lines in the volatility section, same page: L78 "In the $3K Challenge, you cannot trade MHG, MET, MBT, or SIL. Trading during Tier 1 News Events is also restricted to 0. Additionally, MGC and MCL is limited to 6 micros." L85 (Undead): "During Tier 1 News Events, MES, MNQ, MYM, M2K, M6A, M6B, M6E, MNG, MCL, MGC, MBT, MET, MHG, and SIL are limited to 3 lots." L86 (Slasher): same list "are limited to 1 lot." L79 and L80 say the $1.5K and $6K Challenges are also "restricted to 0".

### 4. Existing positions, pending orders, brackets

- L177: "Existing Positions: Traders holding existing positions in equity index products and metals prior to 5 minutes before the news event may keep them open and manage them through the Tier 1 News Events window. TopstepX™ automatically enforces these limits, so no manual adjustment is required for existing trades."
- L178: "Pending orders: Pending orders are not open positions. They will not fill during the 10-minute window, and new pending orders intended to execute during this timeframe cannot be placed. TP/SL brackets that are reducing/closing positions will be accepted during the window."
- L179: "How you'll be alerted: we'll email you and you'll see a banner at the top of the platform, so you're always prepared."
- The page has no wording that requires flattening before the window.

### 5. Consequence of a violation

- The only enforcement wording is L177: "TopstepX™ automatically enforces these limits, so no manual adjustment is required for existing trades." and L178: "new pending orders intended to execute during this timeframe cannot be placed".
- A grep of pages 13613539 and 8284211 for enforce, violation, breach, reject, suspen and terminat finds only L177. Neither page states a rule-breach or account consequence for the Tier 1 window. Page 10305426 lists P06 as prohibited (item 7) and says "These aren't gray areas — they're hard stops." (L29). Its rejection and removal wording ("We retain the right to reject profit claims if abuse is suspected.", L46) sits in the SIM-fills section, not under P06.

### 6. Economic Releases article (8284211, dateModified 2026-10-15T17:51:06Z)

- L50-51: "Trading During the News" / "Topstep restricts trading for a short period during Tier 1 News Events. learn more here." The link points to `https://help.topstep.com/en/articles/13613539-risk-adjustments-high-risk-high-volatility#h_bb7f1d281e`.
- Same page: "Slippage is common during these events. Orders can execute at a worse price than expected. That's not a bug — that's the market."
- The E.19 sentence "Topstep doesn't require you to flatten positions during economic releases — in SIM or Funded Accounts." is **absent**. A grep for "flatten" in ts_8284211.txt returns 0 matches. E.25 had already recorded this removal (E04).

### 7. P06 (10305426, dateModified 2026-06-10T14:02:45Z, page shows "June 10, 2026")

- L43-44: "Trading Maximum Position Size into Major News Events" / "Purposefully trading your full Maximum Position Size directly into a scheduled major news event."

## Diff vs E.25 copies

Method: a diff of the whitespace-normalized text against `reports/stage_e25_briefs/pages/R9/ts_<id>.txt`, ignoring Intercom boilerplate. Spacing-only differences come from the two extractors and are not listed.

| Page | E.25 dateModified | Today dateModified | Status |
|---|---|---|---|
| 13613539 | 2026-10-16T17:11:31Z | 2026-10-20T19:42:21Z | **changed** |
| 8284211 | 2026-10-15T17:51:06Z | 2026-10-15T17:51:06Z | unchanged (only spacing and the title line differ) |
| 10305426 | 2026-06-10T14:02:45Z | 2026-06-10T14:02:45Z | unchanged (only spacing and the title line differ) |

Changes in 13613539, Tier 1 section:

- Lead sentence. E.25: "Ahead of Tier 1 News Events (for example, CPI, FOMC, NFP), Topstep temporarily restricts..." Today: "Ahead of Tier 1 News Events (for example, CPI, FOMC, NFP, PPI), Topstep temporarily restricts..." (PPI added)
- Events table. E.25 row label "CPI"; today "Consumer Price Index (CPI)". **New row**: "Producer Price Index (PPI)" | "7:30 AM" | "7:25 to 7:35 AM".
- Existing Positions. E.25: "Traders holding existing positions in energies and metals prior to 5 minutes before..." Today: "Traders holding existing positions in equity index products and metals prior to 5 minutes before..."
- Unchanged: the Minis list and 10-minute window, the Micros caps 1/3/6/9/15, the MHG/SIL caps 1/2/5/7/12, "Other products ... unaffected", the Pending orders and TP/SL text, and the Combine and XFA tables (no row differences found).

Changes in 13613539 outside the Tier 1 section (volatility restrictions, for the lead's information):

- "Micro Silver (SIL) = 2/4/6" became "Micro Silver (SIL) = 2/5/7", and "Micro Copper (MHG) = 2/4/6" became "Micro Copper (MHG) = 2/5/7".
- "$25K Static Trading Combine ... max contract size of 1 mini/10 micros." became "... 1 mini/12 micros."
- "$250K Trading Combine ... 15 minis/150 micros. For SIL/MHG, 10 minis/100 micros." became "... 15 minis/156 micros. For SIL/MHG, 12 micros."
- Scaling examples: "$2,000 balance = 3 contracts minis / 31 micros" became "$2,000 balance = 3 minis / 31 micros". "Below $1500 balance = 1 contract" became "Below $1500 balance = 1 mini / 18 micros". "...on the 2/4/6 plan" became "...on the 2/5/7 plan". "$2,000 balance = 3 micros" became "$2,000 balance = 2 micros". There are also plural/singular fixes ("1 micros" became "1 micro", "7 micro" became "7 micros").
- Related-articles list: "Trading Combine® Parameters" was replaced by "What is the Maximum Loss Limit?".

E.25 evidence rows E01-E07 (R9_prop_rules.md L57-65):

- E01: the micros and minis wording is still verbatim. The quoted lead sentence now reads "(for example, CPI, FOMC, NFP, PPI)", so E01's quote is outdated by one token.
- E02: the window times are unchanged. The CPI label has been expanded, and a PPI row has been **added** with window 7:25 to 7:35 AM CT.
- E03: unchanged.
- E04: unchanged. The removed sentence is still absent and dateModified is the same.
- E05, E06: not in this brief's pages (8284206 and 11187768 were not fetched).
- E07: unchanged (dateModified 2026-06-10).

## Not done or not verified

- E05 and E06 pages (8284206, 11187768) were not refetched because they are outside the brief.
- I did not check whether TopstepX enforcement behaves as the help text describes. That needs the platform, which this brief forbids.
- The Tier 1 section does not name Live Funded Accounts either way. Item 1 records that silence, not a conclusion.
