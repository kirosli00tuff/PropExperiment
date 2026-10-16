# Stage E.22 Part B: daily settlement data sources for the micro book (options memo)

Written by DataSourceReader (Opus 5.5) on 2026-10-16, with pages fetched 08:00-08:16 UTC
(01:00-01:16 PDT). Scope: lead_spec_B.md S1 (12 modelled micros plus 9 listed but not modelled)
and S7 (the paper runner's pluggable daily settlement source). This memo lists options only. **It makes
no recommendation**; the lead writes that.

Rules followed: no login, no account, no API key, no purchase, no market data download (only
vendor pricing, docs, terms and contract-listing metadata pages were fetched). No Databento API
call and no key use. cmegroup.com, and CME's client wiki on cmegroupclientsite.atlassian.net,
were **never fetched**; CME items in section D come from search-result snippets only and are
marked [unverified]. Every quote below is verbatim from a saved raw page (grep of the page or of
its `.txt` rendering). Fetch IDs (N0xx = this stage, F0xx = Stage E.13, reused with E.13's original fetch
time) map to URL, UTC time, saved file and sha256 in the fetch log at the end. WebSearch use: 14
searches, no budget notice. Search-result summaries were used only to find URLs and are never
quoted as evidence, except in section D, where they are labelled.

Instruments: MNQ, M2K, MGC, MCL, MNG, M6E, 2YY, 10Y, 30Y, MZC, MZS, MZL (modelled); SIL, MHG,
M6A, M6B, MCD, MJY, MZW, MZM, MES (listed, not modelled). All are CME Group (CME, CBOT, NYMEX,
COMEX) contracts. Whether each micro's daily settlement price equals its full-size parent's
settlement price is **not established on any fetched page [unverified]**. The memo treats the
micro's own settlement as the target and records full-size coverage separately.

---

## A. Databento GLBX.MDP3 (statistics schema settlement, or ohlcv-1d)

**A fresh quote through the Databento API is needed before any purchase. None was obtained
tonight** (no API call, no key use). The repo ledger `ledger/databento_spend.jsonl` was read
only, never modified: 36,402 lines (27,716 quote, 4,339 commit, 4,335 settle, 12 refused). Its
schemas are ohlcv-1m, mbp-1, tbbo, mbo and mbp-10 only. **No `statistics` or `ohlcv-1d` quote
has ever been logged.** For scale only: every ohlcv-1m quote in the ledger works out to USD 65.19 per 10^9 billable
bytes (24,866 quotes, 2026-09-17..2026-10-10). That rate is for a different schema and is not a
statistics-schema price. The last ledger row (2026-10-10T08:26:22Z) shows shared_cumulative_usd
353.455228.

**What it delivers**
- Settlement is in the `statistics` schema, not in OHLCV. N011 (statistics docs): "**Statistics**
  provides official summary statistics of each instrument that's published by the venue." /
  "This generally includes properties like daily volume, open interest, preliminary and final
  settlement prices, and official open, high, and low prices." / "| Settlement price | `3` | ✓ |
  | ✓ | ✓ | The settlement price of an instrument. Flags will indicate whether the price is final
  or preliminary and actual or theoretical. |"
- `ohlcv-1d` is not settlement. N012 (OHLCV docs): "Our `ohlcv-1d` schema is based on UTC dates."
  / "`ohlcv-1d` is based entirely on prices and volumes from the electronic trading session and
  will be consistent with prices and volumes observed from aggregating our `trades` data.
  However, this may differ from official settlement prices and volumes published by the venue".
- Timing and flags. N022 (GLBX.MDP3 venue docs): "Settlement price statistics will first publish
  shortly after the settlement window for an instrument." / "The CME does not publish settlement
  prices on their MDP feed for instruments without open interest or volume." / "The initial
  messages indicate preliminary values, and the final message for the trading session date
  indicates the final value." / "The final message is always the most accurate and the one you
  should use, when available." / stat_flags "| `1 << 0` | 1 | Whether the settlement price is
  final, as opposed to preliminary. |". N013: "Depending on the dataset, statistics can be
  published at various times, so you may need to look at the next UTC date for a given
  statistic."
- History and coverage. N022: "Databento provides full coverage of all futures and options on
  futures beginning in June 2010." (So the micros are covered from their own listing dates. No
  per-symbol check was made tonight, because that needs an API call.) N010 (pricing): "16+ years
  of available history" / "All futures, options, spreads" / "650,000+ symbols".
- Delivery: N010: "Python, C++, and Rust client libraries" / "CSV, JSON, and Databento Binary
  Encoding". N016: "For historical data, all delivery methods (like HTTP and FTP) incur no
  additional charge."
- How soon after the close the historical API serves a day's final settlement is **not stated on
  any fetched page [unverified]**. The CME non-professional policy (N019) treats data older than 8
  hours as historical (quote under Licence).

**Cost**
- N010: "Pay as you go with usage-based pricing ($/GB), or choose a subscription plan for
  unlimited access." Usage-based plan: "Pay as you go for historical data. Lowest cost to get
  started." / "No subscription required" / "Historical data only". No $/GB figure is printed. The
  page has an estimator ("Estimated - GB ... <$0.01" for an empty selection).
- N010 Standard plan: "$199" / "per month" / "Monthly subscription" / "Live data" / "No license
  fees" / "16+ years of L0 history". The comparison table includes "| L0 Statistics |  | 16+ years
  | 16+ years | 16+ years |" (Usage-based column blank) and "| Personal use |  | Up to 2 devices
  License fees included |  |  |".
- N016: "All new users receive $125 in free credits upon signup." / "These credits are shared
  across your team and expire after 6 months."
- CME live licence through Databento. N018: "| [CME](...) | Personal | Included with Standard plan
  (up to 2 devices) |" and "| Commercial | $973/exchange $2,170 distribution + $35.40/personal
  user or $119.80/commercial user |". N018 also says license fees "refer to any monthly charges
  imposed by venues for the internal and external use (display, non-display, and distribution) of
  live market data". On that wording, historical (usage-based) data carries no venue licence fee,
  but no fetched page says so outright [unverified].

**Licence and terms (private individual, paper trading, automated use)**
- N020 (User Agreement, "Effective: January 31, 2024"): "Customer agrees to limit all use of
  Third-Party Data by itself and its Authorized Users to internal Customer purposes and not to
  engage in any Redistribution of Third-Party Data".
- N019 (CME non-professional policy, "Effective: April 8, 2025"): "Real-time CME data may not be
  used on behalf or to the benefit of any other individual, employer, trading group, or
  organization." / "After 8 hours, the data is considered historical and no longer subject to
  these restrictions." / "However, distributing any CME data via an API, whether real-time or
  historical, requires an Information License Agreement (ILA) to be in place." Conditions for
  live non-pro data include: "**5. Do you have an active futures trading account with a
  broker?**" / "**6. Are you using third-party software that can execute trades through your
  broker?**" / "Real-time CME data may only be used with software that can route orders and
  execute trades through your broker." / "CME imposes a two-device limit for non-professional
  subscribers."
- N018, on automated (non-display) use: "Non-display use | ... This includes algorithmic trading
  (e.g., automated order or quote generation), internal analytics, or other non-public backend
  applications. Note that some venues don't automatically consider API use as a non-display use
  case. **Internal** use for a **commercial** application. Some venues support **personal**
  non-display use." Whether a paper runner's automated read of historical settlements is
  "non-display" under CME's terms is **not settled by any fetched page [unverified]**.

## B. Broker paper and sim accounts

### B1. Interactive Brokers (paper account)

**What it delivers**
- The paper account has no market data of its own. N025 (IBKR KB 1719): "The paper user, by
  design, does not have a set of market data subscription on its own but can be configured in one
  of the following ways:" / "1. The paper user can be set to share2 the live market data
  subscriptions of the real user:" / "if the real and paper trading sessions are running
  simultaneously, they must reside on the same device in order for the paper to receive live
  market data." / "2. The paper user can be set NOT to share2 the live market data subscriptions
  of the real user: ... the paper user will receive delayed data, as available." / "While this
  approach will result in additional fees for any paid market data" (second real user).
- Delay. N023 (market data pricing): the delayed-data table lists "CBOT | 10 minutes | CBOT
  Real-Time", "CME | 10 minutes | CME Real-Time", "COMEX | 10 minutes | COMEX Real-Time", "NYMEX |
  10 minutes | NYMEX Real-Time"; also "IBKR clients receive free delayed market data on other
  products where available."
- API. N028 (IBKR Campus lesson): "Requesting Historical Data follows a similar pattern to the
  live market data requests. The one caveat to this is that market data cannot be retrieved if
  you do not have a valid market data subscription." / "Exchanges consider API functionality to
  be considered off-platform, and as a result, typically have a cost affiliated with them." /
  "In order for clients to subscribe to market data, users must have a funded IBKR account for at
  least $500 USD in most instances." / "Market Data is affiliated on a per-user basis." /
  "app.reqMarketDataType ... 1,2,3,4 or Live, Frozen, Delayed, or Delayed Frozen". N026 (TWS API
  doc): endDateTime "Must be left as an empty string when requesting continuous futures contracts".
- **Settlement vs close.** No fetched IBKR page says that a daily bar's close, or any tick field,
  is the exchange settlement price **[unverified]**. N027 (the IBKR "Unavailable Historical Data"
  page) returned HTTP 404, so the expired-futures history limit is unverified on a fetched page.

**Cost (non-professional, USD per month)**
- N023: "| CME Real-Time (L1)  14 | United States | USD 1.55 | N/A |", with identical rows for
  "CBOT Real-Time (L1)", "COMEX Real-Time (L1)" and "NYMEX Real-Time (L1)" (USD 1.55 each). Footnote
  14 (raw HTML id d-fourteen): "Fee is waived if commissions generated are greater than USD 20.00".
- Bundle alternative, N023: "US Securities Snapshot and Futures Value Bundle ... USD 10.00 Base
  Waived for Activity + USD 0.01 per Snapshot" and the waiver table "| US Securities Snapshot and
  Futures Value Bundle | USD 10.00 | USD 30.00 |" (fee, commissions waiver). Footnotes: "Includes
  top of book quotes for CBOT, CME, COMEX, and NYMEX" / "Access to US Futures data requires
  clients to have US Futures Trading Permissions." / "Accounts must generate at least USD 30 in
  commissions per month per each user subscribed."
- The same CME L1 USD 1.55 row was on IBKR Canada's page in E.13 (F003, 2026-10-03T21:55:27Z;
  E.13 report B-07).
- Four exchanges at L1 (CME, CBOT, NYMEX, COMEX) at USD 1.55 each make USD 6.20 a month, or USD
  74.40 a year, before waivers. This is arithmetic from the quoted rows. That the 12 micros need
  exactly these four exchange subscriptions follows from their listing exchanges in
  ibkr_margins.json; it is not a quoted IBKR statement.

**Licence and terms**: market data rules are as above (per-user subscriptions, off-platform API use
"typically" costs). IBKR's own market-data terms page was not fetched (E.13 found the .ca terms of use
URL returned 404, F005). Margins: see `reports/stage_e22_briefs/ibkr_margins.json`.

### B2. AMP Futures (live data through CQG, Rithmic or TT; E.13 page reused)

F034 (fetched 2026-10-03T22:01:54Z in E.13, "Prices effective June 1, 2026", non-pro): "CME
Bundle - ALL CME Markets (Level 1) Top of Book | $15.00 | $15.00 | -" (CQG | Rithmic | TT);
"CME/Globex (Level 1) Top of Book | $5.00 | $5.00 | -", and the same $5.00 for CBOT/Globex,
NYMEX/Globex and COMEX/Globex L1; "Monthly Fees Listed Above are for Non-Professional Trader
Status." Eligibility (E.13 B-18, Wayback 2025-09-11): "Only 3 provinces in Canada are allowed:
Alberta, Ontario and Quebec. Additionally, British Columbia accounts may be allowed at the
discretion of a senior manager." Settlement delivery through these platforms' APIs and their
paper or sim terms were **not researched tonight [unverified]**.

### B3. NinjaTrader simulator (E.13 page reused)

F042 (fetched 2026-10-03T22:03:08Z in E.13): "Sharpen your skills in our free futures trading
simulation, which comes with live market data for the first 14 days. No minimum funding*
required to get started." Data after day 14, settlement fields, automated export terms and
exchange fees for the simulator are **not established [unverified]**.

## C. Licensed end-of-day vendors

### C1. Norgate Data (Futures package)
- Settlement: N029: "Unless otherwise specified, the Close price in the data is the official
  settlement price (and not the last-traded price)." / "Historical data extends back to around
  1980 or to the first day of trading in a market (with a few exceptions)." / "Norgate Data
  covers around 100 Futures markets drawn from 11 worldwide exchanges (or exchange groups). The
  coverage is selective rather than exhaustive." Continuous series: "unadjusted and
  back-adjusted. Back-adjustment is calculated arithmetically."
- Cost: N029: "6 months = USD 148.50" / "12 months = USD 270".
- Coverage (N043 contract table; header "Market | First Contract | History Start Date | Symbol |
  Session"; 104 futures rows parsed):
  - Micros listed: "Micro E-mini Nasdaq 100 | Jun 2019 | 6 May 2019 | MNQ | All Sessions
    Combined", "Micro E-mini Russell 2000 | Jun 2019 | 6 May 2019 | M2K | ...", "Micro E-mini S&P
    500 | Jun 2019 | 6 May 2019 | MES | ...".
  - Not listed: MGC, MCL, MNG, M6E, 2YY, 10Y, 30Y, MZC, MZS, MZL, SIL, MHG, M6A, M6B, MCD, MJY,
    MZW, MZM.
  - Full-size parents listed: NQ, RTY, GC, CL, NG, 6E, ZT, ZN, ZB, ZC, ZS, ZL, SI, HG.
- Delivery and latency: N045: "In default mode, NDU runs "in the background" to deliver updates
  automatically as soon as new data becomes available." / "| Futures | Final Edition | 8.40 pm New
  York time" / scheduling through "NDU.Trigger.exe". Whether the updater runs on Linux is **not
  established [unverified]**; the trigger is a Windows .exe.
- Licence: N044: "No commercial use - the data can only be licensed for personal use by
  individuals" / "Fixed subscription length - subscriptions are for a set period and not subject
  to cancellation in the event that the service is no longer required." / "A fully-functional
  3-week free trial with 2 years of history is available". The End User Licensing Agreement itself
  was not fetched [unverified].

### C2. CSI Data (Unfair Advantage)
- Cost (N040, rendered page script): the Monthly branch sets "SRateColTitle ... "Monthly access
  rate"" and "SILVERRate_1 ... "$47.50"". The Yearly branch sets "Yearly access rate" and
  SILVERRate_1 "$398.00". Row 1 is "North American Futures", whose static row (N039) shows
  "$60.00" in the "One time licensing fee" column. Package text: "This category includes active
  futures and cash markets in the U.S. and Canada ... with a daily cumulative maximum of 49
  markets processed through your UA portfolio." / "Inactive futures not included." History: "For
  monthly subscriptions: Access to 5 years of historical data ... For yearly subscriptions: Access
  to 10 years of historical data". Trial: "$20 Trial ... any 5 US Futures within the CME ... 18
  months of history included for 21 day access."
- Coverage (N042, CSI factsheet table for CME Group, contract metadata only): all 21 micros are
  listed and marked active with end date 2026-10-15. Examples: "200334 | ... | MNQ | MNQ | MNQ |
  CME | Micro E-mini Nasdaq 100 Index | ... | 2019-05-06 | 2026-10-15", "200601 | ... | 2YY | CBT
  | 2-Year Yield | ... | 2021-08-16", "200673 | ... | MNG | NYMEX | Micro Henry Hub Natural Gas |
  ... | 2023-11-03", "200837 | ... | MZB | MZB | MZS | CBT | Micro Soybean |" (CSI symbol MZB,
  exchange symbol MZS), "100869 | ... | SIL | COMEX | 1000 oz Silver | ... | 2013-06-17".
- Settlement: N038: "We provide Regular Trading Hours(RTH), Electronic Trading Hours(ETH), and
  Combined Futures pricing" / "ETH pricing can be included with Combined Futures pricing, and RTH
  settlements can be included with ETH pricing." Whether the default daily close field for these
  micros is the official settlement is **not stated on a fetched page [unverified]**. N037: "We
  provide only End of Day data." Latency: N039 notes "When early access is used (before 6:30
  p.m.), charting is limited to 250 series." The time zone is not given.
- Licence: N036: "All data and software licensed to you are provided for your personal and
  private use." / "Before you use the software under a license, you must assign that license to
  one device." / "(c) Commercial Accounts – FTP transmissions, multi-users, network, creating
  derivative(s), publication, website presentation, redistribution or resell is not allowed under
  this agreement." Automated reading of exported files by the user's own program is not addressed
  explicitly [unverified]. Delivery is through the UA desktop software with export ("Export to most
  charting and trading software", N039); its OS support was not checked [unverified].

### C3. Barchart OnDemand (cmdty)
- N048 (getHistory doc): "Historical data is available as tick, minute bars or end-of-day data."
  Field definition: "close" / "The last traded price for the period." There is a session code
  field: ""G" is electronic session and "R" is pit session."
- No price is published on the fetched pages. N049 lists APIs and "Contact" links only; no
  individual or free tier price is shown. Licence terms were not fetched. Barchart returned HTTP
  202 bot-challenge pages to curl (N046, N047); Scrapling `extract fetch` rendered them.
- Settlement availability through getHistory is **not established**: the doc defines close as last
  trade [unverified for futures daily].

### C4. Nasdaq Data Link
- **Not established.** The product pages tried (N050 SCF, N051 CHRIS) render only a JavaScript
  shell under Scrapling. The docs page from a search hit returned 404 (N052). A search summary
  mentioned a premium table "MarketWorks Futures Settlement CME" with metadata dated March 2017.
  That is **[unverified, search snippet only]**, and whether it is still sold is unknown.

### C5. Massive (formerly Polygon.io) futures (found in this search)
- Settlement: N055 (REST futures aggregates doc): "`results[].settlement_price` | number | The
  price the contract settled at for this session. Included for session, week, month, quarter, and
  year candles". "A futures session opens the evening before the date it settles on, so a session
  bar's window_start is the day before its session_end_date." / "**Plan Access:** Included in all
  Futures plans". Recency: "| Futures Basic | 8-hour historical |", "| Futures Starter | 10-minute
  delayed |", "| Futures Developer | 10-minute delayed |", "| Futures Advanced | Real-time |".
- Cost (N053): "Futures Basic" "$0/month", "5 API Calls / Minute", "2 Years Historical Data",
  "CME, CBOT, NYMEX, COMEX", "Individual use"; "Futures Starter" "$29/monthBilled monthly",
  "Unlimited API Calls", "2 Years Historical Data"; "Futures Developer" "$79/monthBilled monthly",
  "5 Years Historical Data"; "Futures Advanced" "$199/monthBilled monthly", "7+ Years Historical
  Data", "Individual useNon-pros only"; "Save 20% with the annual plan". Every tier lists "All
  Futures Tickers". Per-symbol coverage of each micro was **not checked [unverified]**.
- Licence: N057 ("Last Updated: July 18, 2025"): the licence is "solely for your own personal,
  non-commercial, and non-business purposes." N056: "The Massive for Individuals Terms of Service
  apply to your personal, individual, and non-business use of any service or product labeled for
  "Individual Use"." CME exchange-fee terms for Massive individual plans were **not found on a
  fetched page [unverified]**.

## D. The exchange itself (CME DataMine, settlement files): search snippets only, all [unverified]

cmegroup.com and cmegroupclientsite.atlassian.net were not fetched. The following comes from
WebSearch result summaries of those pages (2026-10-16, about 08:15 UTC). It is not verbatim page
text and is **[unverified]**:
- Daily settlement files exist for all CME Group exchanges. The free files are "available for the
  current day only", and each day's files overwrite the prior day's. Historical end-of-day data
  "can be purchased from the CME DataMine page on cmegroup.com" [unverified].
- An End of Market Summary subscription "can vary from $105/per month, $105/per month per DCM,
  or $2,100/per month depending on the End of Market Summary dataset chosen"; "if for internal use
  only, then only the DataMine fee applies" [unverified; this comes from a CME FAQ about an FTP
  access change].
- DataMine pricing "varies based upon data type and duration of the data request"; "All sales are
  final" [unverified].
- CME holiday notices (snippet): no settlement prices derived or disseminated on 2026-11-26 or
  New Year's Day 2027 [unverified]. This matters for the runner's calendar.
- CME product pages show settlements free to view in a browser, but automated reading is outside
  this project's boundary, and CME's terms for it were not checked [unverified].

---

## Comparison table (facts as quoted above; no ranking)

"Cost per year for this use" means the published price for daily EOD coverage of the 12 modelled
micros by one private user. Arithmetic is shown; anything not published is marked.

| Source | Cost per year for this use | Settlement price | Micros covered (of 21) | Automated download allowed | Main caveat |
|---|---|---|---|---|---|
| Databento GLBX.MDP3, usage-based historical, `statistics` | Unknown: $/GB not published, fresh API quote required (not obtained); $125 signup credits expire after 6 months | Yes (stat_type 3, final/preliminary flag) | All CME Group futures since June 2010 (per-symbol not checked) | API is the delivery method; internal use only, no redistribution; "personal non-display" status for CME not settled | No statistics quote ever logged; same-day availability of final settlement through historical not stated |
| Databento Standard plan | USD 199 x 12 = 2,388 | Yes (L0 Statistics, 16+ years; live) | Same | API; CME personal licence included, up to 2 devices; live non-pro use requires a funded broker account and order-capable software | Live-licence conditions (questions 5 and 6) |
| IBKR paper (shares live subscriptions) | CME+CBOT+NYMEX+COMEX L1 at USD 1.55 each = 74.40, each waived above USD 20 commissions a month; or Futures Value Bundle USD 10/mo = 120 (waived at USD 30) | Not established [unverified] | All 21 have IBKR margin rows (ibkr_margins.json) | TWS API historical needs a valid subscription; account must be funded (USD 500 "in most instances") | Paper and live sessions on different devices lose live data; settlement field unverified |
| AMP Futures (CQG/Rithmic) | CME bundle L1 USD 15 x 12 = 180, or 4 x USD 5 x 12 = 240 (non-pro) | Not researched [unverified] | Not checked | Not researched | BC accounts only at a senior manager's discretion (E.13) |
| NinjaTrader simulator | Free with live data for first 14 days; after that unknown | Not researched [unverified] | Not checked | Not researched | Data after day 14 unknown |
| Norgate Data Futures | USD 270 (12 months) | Yes ("Close ... is the official settlement price") | 3 (MNQ, M2K, MES); all 12 full-size parents covered | Updater runs automatically or scheduled; personal use by individuals only | Most micros absent; updater is a Windows .exe (Linux unverified) |
| CSI Data UA, North American Futures (Silver) | USD 398 yearly + USD 60 one-time licence = 458 in year 1 (monthly USD 47.50) | Partly: "RTH settlements can be included with ETH pricing"; default close unverified | 21 of 21 listed active | Personal and private use, one device; desktop software export | Settlement field semantics unverified; 49-market daily cap |
| Barchart OnDemand getHistory | Not published (contact sales) | Doc defines close as "last traded price" | Not checked | API product; terms not fetched | No price; settlement unverified |
| Nasdaq Data Link | Not established | Not established | Not established | Not established | Pages JS-only or 404; futures EOD offer unverified |
| Massive futures | Basic USD 0 (8-hour historical, 2 years, 5 calls/min); Starter USD 29 x 12 = 348 (annual plan advertised as 20% off) | Yes (`settlement_price` on session candles) | "All Futures Tickers" (per-symbol unverified) | REST API; personal, non-commercial, non-business use | Exchange-fee terms not found; short history on low tiers |
| CME DataMine / settlement files | [unverified] e.g. "$105/per month" per dataset (snippet) | Yes (exchange settlement files) [unverified] | [unverified] | cmegroup.com off-limits to this project's automation | Everything unverified; free files current-day only |

---

## Not finished or not verified

- No Databento quote for `statistics` or `ohlcv-1d` (by design tonight). There is no published $/GB
  for these schemas, and the lag before a day's final settlement reaches the historical API is
  unknown.
- IBKR: no fetched page ties any API field to the exchange settlement price. The expired-futures
  history page returned 404. IBKR's market-data subscriber terms were not fetched.
- AMP and NinjaTrader: sim or paper data terms and settlement delivery were not researched beyond
  E.13's pages.
- Norgate EULA text and Linux support; CSI settlement semantics and automation terms; Barchart
  pricing and terms; Nasdaq Data Link offer; Massive per-symbol micro coverage and CME exchange-fee
  pass-through.
- Whether each micro's settlement equals its full-size parent's settlement: not established.
- Section D is snippet-only by rule.
- Saved pages that are not evidence: N003 to N006 and N007 to N009 (JS shells, superseded by
  N010 to N012), N015 (Databento /terms 404), N024 (KB redirect shell, superseded by N025), N027,
  N030, N033 and N052 (404), N046 and N047 (202 bot challenge, superseded by N048 and N049), N031
  (connection refused, no file; retried as N043), N050 and N051 (JS shells).

## Fetch log

Saved under `reports/stage_e22_briefs/datasrc_pages/`, with the machine log in `fetch_log.tsv`
and private scripts in `_scripts/`. `.txt` files are text renderings made by
`_scripts/totext.py`; the sha256 is of the raw saved file.

| ID | URL | UTC fetched | Method | File | sha256 | Status |
|---|---|---|---|---|---|---|
| N001 | https://www.interactivebrokers.com/en/trading/margin-futures-fops.php?hm=us&ex=us&rgt=0&rsk=1&pm=0&rst=101004100808 | 2026-10-16T08:00:23Z | curl | ibkr_margin_fut_us.html | b686db282e829dff9a05ece6468f201816be9a49f3d3415b88d517efa2831398 | 200 |
| N002 | https://www.interactivebrokers.ca/en/trading/margin-futures-fops.php?hm=ca&ex=us&rgt=0&rsk=1&pm=0&rst=101004100808 | 2026-10-16T08:00:40Z | curl | ibkrca_margin_fut_ca_us.html | 0695ec9eb21005c21ab7725e23a2329eb864ae6133e4f05c7cf74270d3669007 | 200 |
| N010 | https://databento.com/pricing | 2026-10-16T08:02:24Z | scrapling fetch (network-idle) | databento_pricing_scr2.md | 235b54c38bf81be0e24ddbcf9174e450909822d0c0eb5de45d4aec340ef3a23b | ok |
| N011 | https://databento.com/docs/schemas-and-data-formats/statistics | 2026-10-16T08:03:34Z | scrapling fetch | databento_docs_statistics_scr2.md | 2a33dfe707dc8cb4a24f3ed10c2ab50d827b45d14f5416eeb036482bf9a83035 | ok |
| N012 | https://databento.com/docs/schemas-and-data-formats/ohlcv | 2026-10-16T08:04:07Z | scrapling fetch | databento_docs_ohlcv_scr2.md | fa1928701e73d04d35d2eb744f60a365dc348b45462b636496222de7820ff37a | ok |
| N013 | https://databento.com/docs/examples/futures/retrieving-oi-and-settlement-prices | 2026-10-16T08:04:19Z | scrapling fetch | databento_ex_settlement_scr.md | 1c3b9fb81cc6b4880dc1f241ead6c479ac86b4bef0e75d63be303d0b8a55d6af | ok |
| N014 | https://databento.com/docs/examples/futures/statistics-schedule | 2026-10-16T08:04:32Z | scrapling fetch | databento_ex_statsched_scr.md | 68d5ab7e3041b29aa6793cbe7cdadb5a582800d1b0a61025b0fc480f7b1427d4 | ok (no times stated) |
| N016 | https://databento.com/docs/faqs/usage-pricing-and-data-credits | 2026-10-16T08:04:56Z | scrapling fetch | databento_faq_pricing_scr.md | 1571bc16753dc9b0419775186e8eeede9759de914d9899648713ce536c2d6852 | ok |
| N017 | https://databento.com/legal | 2026-10-16T08:05:38Z | scrapling fetch | databento_legal_scr.md | b0cf9d6be1eb2e383637cef653ca20b325bd236ba7c3d9d15db1a08e262d2e0c | ok (index) |
| N018 | https://databento.com/docs/portal/live-data | 2026-10-16T08:05:49Z | scrapling fetch | databento_docs_livedata_scr.md | 7cad1dd58cfde943a2fd6dd42bd79992e80202c2d32149e87cebf4c1b7966266 | ok |
| N019 | https://databento.com/legal/exchange-data-policy/cme-non-professional | 2026-10-16T08:06:13Z | scrapling fetch | databento_legal_cme_nonpro_scr.md | 67045c8340cbd70eea0538896e612e76df05220dd576b32ca669023dcf2eda6d | ok |
| N020 | https://databento.com/legal/databento-user-agreement | 2026-10-16T08:06:24Z | scrapling fetch | databento_user_agreement_scr.md | 60b61128a6c073e74d2b890adf210869057ddb4b86f830917f8997a2466d63fa | ok |
| N021 | https://databento.com/docs/examples/basics-historical/historical-introduction | 2026-10-16T08:06:59Z | scrapling fetch | databento_ex_hist_intro_scr.md | 8e0efbcb33f2e4b2bcedb2c41e8595489ce4b30d4e3558923f375b47dace94f6 | ok (not quoted) |
| N022 | https://databento.com/docs/venues-and-datasets/glbx-mdp3 | 2026-10-16T08:07:11Z | scrapling fetch | databento_venue_glbx_scr.md | cad93c23b2515c8220f1f533f512b2ae6a87cd346900b6f1aa47c455488d989f | ok |
| N023 | https://www.interactivebrokers.com/en/pricing/market-data-pricing.php | 2026-10-16T08:07:30Z | curl | ibkr_market_data_pricing.html | 09e09d88dca537501ab339f0ed19809953fa2ec00c898f91a6b586db519dd500 | 200 |
| N025 | https://ibkb.interactivebrokers.com/article/1719 | 2026-10-16T08:08:43Z | scrapling fetch | ibkb_1719_paper_market_data_scr.md | 2c1de3a36f8a3510c24e694f6ea3d77150827e946ab5819ec0cea3d37b8b69c0 | ok |
| N026 | https://www.interactivebrokers.com/docs/tws-api/sync-doc/historical-market-data.md | 2026-10-16T08:09:08Z | curl | ibkr_twsapi_historical_market_data.md | 46e49523e1753295d089ddeffb6db67a12403df4740d580f6ab5cd8248ccc36d | 200 |
| N027 | https://www.interactivebrokers.com/docs/tws-api/doc/market-data-historical/historical-data-limitations/unavailable-historical-data | 2026-10-16T08:09:22Z | curl | ibkr_twsapi_unavailable_hist.html | 86cef2079e7eb90cf45a8cc23918b1dd96fb1e529c8387f5c12c4d0849516b00 | 404 |
| N028 | https://ibkrcampus.eu/trading-lessons/python-receiving-market-data/ | 2026-10-16T08:09:26Z | curl | ibkrcampus_python_receiving_market_data.html | 9effe1034e313c98365ebdbf7efef1ac01f01cb44369da3bb80054e5ff13bb43 | 200 |
| N029 | https://norgatedata.com/futurespackage.php | 2026-10-16T08:09:47Z | curl | norgate_futurespackage.html | 406eb9e36dda8c00172ee500cf361e451a6b45fa479798abd26e8f5f74e38459 | 200 |
| N036 | https://www.csidata.com/?page_id=824 | 2026-10-16T08:10:14Z | curl | csi_license.html | baafc975b2dadcffa707660658f6c051f2782c958a38b41edb012f5fafeb5b44 | 200 |
| N037 | https://www.csidata.com/?page_id=450 | 2026-10-16T08:10:14Z | curl | csi_coverage_faq.html | f5f6f6f4684c24a6e37b6acfa4143f7c1ec21db4d61aed531fbac48a574efadf | 200 |
| N038 | https://www.csidata.com/?page_id=14 | 2026-10-16T08:10:15Z | curl | csi_ua_features.html | 4a2a19c4775285bd5e30e9319a93ae74dedd1d423a2df012d3e5de982462c2c4 | 200 |
| N039 | https://apps.csidata.com/OrderUA | 2026-10-16T08:10:24Z | curl | csi_orderua.html | e38fcd029a533a683d356c327ba17e1b9c3ec6ed8ec8424223468a83d36d3ee4 | 200 |
| N040 | https://apps.csidata.com/OrderUA | 2026-10-16T08:10:49Z | scrapling fetch | csi_orderua_scr.html | 562f007e3d96af16d5d672237c6ddea0219a4bc9975ed01886d2749302de8d54 | ok |
| N042 | https://apps.csidata.com/factsheets.php?type=commodity&exchangeid=CMEGROUP&format=htmltable | 2026-10-16T08:11:34Z | curl | csi_factsheet_cmegroup.html | c989ae6a88368bb46d0feceb9882ea388527ccd3e77b6bae746a4fd2f1c7f7ed | 200 (contract metadata) |
| N043 | https://norgatedata.com/data-content-tables.php | 2026-10-16T08:11:54Z | curl | norgate_data_content_tables.html | a814cf204bd15e1cefb6fdac3f26ac90039e48e367debb1e2418bc5ae2895873 | 200 |
| N044 | https://norgatedata.com/subscribe/subscribe.php | 2026-10-16T08:12:16Z | curl | norgate_subscribe.html | 1ef4a13645fc204c763ce04323bfbe61e31f2e01d374edfb7b8589e1d49aec27 | 200 |
| N045 | https://norgatedata.com/ndu-usage.php | 2026-10-16T08:12:31Z | curl | norgate_ndu_usage.html | 06910e80a189a2a226c7cbb00696ebba9d9cfb22eb45451213f9ff4cfba68fbb | 200 |
| N048 | https://www.barchart.com/ondemand/api/getHistory | 2026-10-16T08:12:50Z | scrapling fetch | barchart_ondemand_gethistory_scr.md | 17692de7498eeaa6c83a5b2c7367e8025809993998b63f5ba48ef89beb45ad02 | ok |
| N049 | https://www.barchart.com/ondemand/free-market-data-api | 2026-10-16T08:13:06Z | scrapling fetch | barchart_ondemand_free_scr.md | cb67d5344913ef73a2861998d6aac1472a1382ebd1addde5c718ca6c23db2207 | ok |
| N053 | https://massive.com/pricing?product=futures | 2026-10-16T08:14:56Z | curl | massive_pricing_futures.html | 46d4c942e6b4b85e7ba90fc948c071d8105f347931a7eb20212860bf7d64ffcb | 200 |
| N055 | https://massive.com/docs/rest/futures/aggregates.md | 2026-10-16T08:15:10Z | curl | massive_docs_futures_aggregates.md | d7f852a3e2574672d90f98a50f48da582dbcadb14700122e050af661c0c6980e | 200 |
| N056 | https://massive.com/terms | 2026-10-16T08:15:20Z | curl | massive_terms.html | aa04bf90c4461f22d55149432d8b13f0979d0624e1b1534eeead8c22fb8a1c97 | 200 |
| N057 | https://massive.com/legal/individuals-terms-of-service | 2026-10-16T08:15:27Z | curl | massive_individual_tos.html | 6eb51671703add6ec0ee8016c20d53b3dd2c6056a417218a0ae190d84e671e4d | 200 |
| F003 (E.13) | https://www.interactivebrokers.ca/en/pricing/market-data-pricing.php | 2026-10-03T21:55:27Z | curl | ../../stage_e13_briefs/pages/BrokerVenues/ibkrca_market_data.html | 4538c16d2557c3a1d0f29737dc280b82167694d988a031b858dad47f85bb7ec1 | 200 |
| F034 (E.13) | https://www.ampfutures.com/trading-info/exchange-data-fees | 2026-10-03T22:01:54Z | curl | ../../stage_e13_briefs/pages/BrokerVenues/amp_exchange_data_fees.html | b294e2cc8a7ea8b8c1d8658bdbbeba26bf5ed8de85e14ce8982b9d5a9060c74d | 200 |
| F042 (E.13) | https://ninjatrader.com/ | 2026-10-03T22:03:08Z | curl | ../../stage_e13_briefs/pages/BrokerVenues/nt_home.html | 675cae55628caa6da672997f96a5659786a774a7d73a61eb99d73106840f91e0 | 200 |

The non-evidence or navigation-only fetches (N003 to N009, N015, N024, N030, N031, N033 to N035, N041, N046, N047,
N050 to N052, N054) are logged with hashes in `fetch_log.tsv`.
