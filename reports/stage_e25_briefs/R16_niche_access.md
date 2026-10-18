# R16 niche-market access (Stage E.25, SourceReader-NicheAccess-OpusHigh)

Written 2026-10-18, 01:58 to 02:00 PDT and 06:12 to about 06:30 PDT (a usage limit cut the run from about 02:00 to 06:12 PDT).
Scope: (b) prop firms by plan for non-CME and niche markets, (c) tick-data sources and published prices, (d) BC retail broker access and cost inputs.
The run was short, so the tables below are partial. Section 10 lists the gaps.

## 1. Answer (at most 250 words)

(b) Only **Phidias** lists Eurex contracts in a rules page that could be fetched and saved. Its "Eurex (DXFEED & TRADOVATE)" list has FDXS, FSXE, FDAX, FDXM, FESX, FSTX, FGBL, FGBM, FGBS, FGBX and FVS, and the same page gives per-side commissions (FDXS 0.55 EUR, FDAX 2.02 EUR, FGBL 1.04 EUR). Phidias bans full automation: "Only semi-automated software is permitted". Its Terms of Use s.3.1.9 product list still names CME products only, so the rules page and the terms disagree.
Topstep's permitted list is CME Group only. Its one Japan exposure is CME's Nikkei contract NKD, tradable from 17:00 CT, so Asian hours fall inside its trading day.
For Apex and Tradeify, Eurex access comes only from search summaries (Apex: FDXS only, Tradovate only, per one review site; Tradeify: "full DAX ladder", per the same site), graded [secondary-only]. Both firms' terms forbid automated fetches.
No firm was found for ICE Europe, OSE, SGX, HKEX, INE or SHFE. That is a search gap, not proof that none exists.

(c) Databento's public dataset pages give these start dates: Eurex XEUR.EOBI from 2025-03-10; ICE Europe Commodities IFEU.IMPACT, ICE Futures US IFUS.IMPACT and ICE Endex from 2018-12-23; ICE Europe Financials IFLL.IMPACT from 2024-12-10. Osaka Exchange and Tokyo Commodity Exchange appear as venues with no dataset id, and no HKEX, SGX, INE or SHFE futures dataset is listed. The CME plans are Standard at $199 a month, Plus at a $1,750 license fee a month, and Unlimited at $4,500 a month. The per-venue prices for Eurex and ICE are rendered by JavaScript and were not readable.

(d) IBKR's published per-contract fee examples (all-in per side, tiered at no more than 1,000 contracts a month): FDAX 2.16 EUR, FDXM 0.75 EUR, FDXS 0.38 EUR; OSE N225 410 JPY. Fixed-rate round trips: Eurex 4.00 EUR, N225 mini 80 JPY, HSI 60 HKD, MHI 34 HKD, SGX Nikkei mini 100 JPY, ICE USD contracts 4.80 USD.

## 2. Candidate hypotheses

None. This reader's objective is access and cost tables. Whether these markets are inefficient is R15's question.

## 3. Evidence table

### 3b. Prop firms by plan: non-CME and niche markets

| Firm / plan | Non-CME products listed | Asian-hours CME (NKD etc.) | Flat time | Automation | BC / Canada | Source, grade |
|---|---|---|---|---|---|---|
| Phidias, all plans (Fundamental, Premium, E2L) | Eurex: "Eurex (DXFEED & TRADOVATE) Micro-DAX (FDXS) Micro-EURO STOXX 50 (FSXE) DAX (FDAX) Mini-DAX (FDXM) EURO STOXX 50 (FESX) STOXX Europe 50 (FSTX) Euro-Bund (FGBL) Euro-Bobl (FGBM) Euro-Schatz (FGBS) Euro-Buxl (FGBX) VSTOXX (FVS)". Commissions: "EUREX (dxFeed) Instrument Commission FDXS 0.55€ / side FSXE 0.51€ / side FDAX 2.02€ / side FDXM 1.01€ / side FESX 1.17€ / side FSTX 1.15€ / side FGBL 1.04€ / side ... FVS 0.974€ / side". On NinjaTrader: "FDAX $2.79 / side FDXM $1.59 / side FESX $1.71 / side FXXP $1.50 / side". The terms list conflicts: Terms of Use s.3.1.9 "LIST OF AUTHORIZED PRODUCTS" names CME products only plus "*If the User wants a specific product that is not available, do not hesitate to contact the team". Eurex depth data: "EUREX (Level 1 + Level 2) = 22€/ 25$" | NKD listed (terms s.3.1.9). Fundamental hours: "Regarding CME Globex: Sunday to Friday from 11:00 PM to 9:59 PM (UTC)" | Fundamental and E2L flat at end of trading day; Premium "can remain open overnight and over-week" | "The use of robots, fully automated trading algorithms, or any other form of automated trading is not permitted. Only semi-automated software is permitted, provided the trader actively monitors and manually adjusts" | not restricted (E.13, via R9) | phidiaspropfirm.com/rules (R9 copy pages/R9/phidias_rules.txt, fetched 2026-10-18T08:47:00Z, sha256 bb9ccc4e6cea...); /tou (pages/R9/terms_phidias.txt, 3f82270c07cd...). firm-page |
| Topstep, Combine and XFA | none: "Every tradeable CME Group product". Its list covers CME, CBOT, NYMEX and COMEX only | "Nikkei NKD (NKD)" permitted; "Sunday open 5:00 PM CT ... Weekday reopen 5:00 PM CT", so the Asian session is inside the trading day | "All positions must be closed by 3:10 PM CT every weekday" | API allowed, no VPS, no HFT (R9 E06; E.19) | Canadians eligible (R9 E08) | help.topstep.com/en/articles/8284206 (pages/R9/ts_8284206.txt, 2026-10-18T08:46:18Z, 7c8b7b32120b...). firm-page |
| Apex (2026 product line) | Eurex reported as FDXS only, through Tradovate only, with a paid Eurex Level 2 add-on of about $23 a month | not read | 15:59 CT (E.13 via R9) | banned; "each order manual" (R9 E44) [secondary-only] | E.13 | WebSearch summary of damnpropfirms.com (May 2026, a pointer) and a pipback.com fee table listing "FDAX 1.46 ... FDXM 0.46 ... FESX 0.59" per side on Tradovate. pointer [secondary-only]. Apex terms forbid automated access or were unreadable (terms_log), so no fetch |
| Tradeify | Eurex listed: "full DAX ladder" (review site); contract list not seen | not read | 15:45 CT (E.13) | own algorithm only (R9 E42) [secondary-only] | E.13 | WebSearch summary of damnpropfirms.com. pointer [secondary-only]. Tradeify terms forbid robots (terms_log) |
| TPT, MFFU, Lucid, Alpha, FundedNext, Bulenox, Earn2Trade, TradeDay, ETF, The Trading Pit, Leeloo | not checked in this run | not checked | see R9_prop_rules.md table, lines 135-155 | see R9 | see R9 | not done (section 10) |

### 3c. Tick-data sources and published prices

| Venue | Source | Coverage start | Price (published) | Quote, location | Grade, path |
|---|---|---|---|---|---|
| Eurex (FDAX, FESX, FGBL, ...) | Databento XEUR.EOBI | 2025-03-10 | per GB, usage-based; per-venue plan price not readable (JavaScript) | `"temporalCoverage":"2025-03-10/.."`; "Real-time data is included with any Eurex subscription. Historical data is available for usage-based rates or with any Eurex subscription." (dataset page JSON-LD) | vendor; pages/R16/db_xeur.html (b33de68a0e78d54a) |
| ICE Europe Commodities (Brent, gasoil) | Databento IFEU.IMPACT | 2018-12-23 | usage-based; real-time only on Plus or Unlimited | `"temporalCoverage":"2018-12-23/.."`; "Real-time data is included with a Plus or Unlimited subscription for ICE Europe Commodities." | vendor; pages/R16/db_ifeu.html (b2c91094bc776e22) |
| ICE Futures US | Databento IFUS.IMPACT | 2018-12-23 | usage-based | `"temporalCoverage":"2018-12-23/.."` | vendor; pages/R16/db_ifus.html (8234cb0b2a1ed524) |
| ICE Europe Financials | Databento IFLL.IMPACT | 2024-12-10 | not read | venues page entry `("ICE Europe Financials","IFLL.IMPACT","2024-12-10")` | vendor; pages/R16/databento_venues.html (23074b6320c9eaed) |
| OSE, TOCOM | Databento | no dataset | n/a | venues entry `("Osaka Exchange", dataset_id null, available_from "2023-07-07")`; the same holds for "Tokyo Commodity Exchange". The page has no "coming soon" string, so the user's "OSE coming soon" note is neither confirmed nor refuted | vendor; same file |
| HKEX (HKFE), SGX, INE, SHFE | Databento | no futures dataset listed | n/a | "Singapore Exchange" and the "Hong Kong" entries appear only in the equities venue list | vendor; same file |
| CME (reference) | Databento GLBX | "16+ years" | "Standard ... $199 per month"; "Plus ... $1,750 license fees per month Annual contract required"; "Unlimited ... $4,500 license fees per month"; Standard history: "16+ years of L0 history 1 year of L1 history 1 month of L2 and L3 history" | pricing page, CME tab | vendor; R2 copy pages/R2/databento_pricing.md |
| Exchange data shops (Eurex/Deutsche Boerse, JPX, HKEX), ICE Data, CQG, INE/SHFE vendors | not fetched | | | | section 10 |

Databento's catalogue states, through the pricing page product filter: "CME CFE EEX Eurex ICE Europe Commodities ICE Europe Financials ICE Endex ICE Futures US". Databento terms (terms_log, R2): allowed for named public pages one at a time. No quote was requested and no API call was made.

### 3d. Retail access for a BC resident: IBKR published per-contract fees

Source: https://www.interactivebrokers.ca/en/pricing/commissions-futures-europe.php. The page also carries Asia-Pacific tables. Fetched 2026-10-18T13:14:15Z, sha256 e7e8e25ced08595d..., pages/R16/ibkr_ca_fut_comm.html and .txt. robots.txt has "User-agent: *" and no pricing disallow (pages/R16/ibkr_robots.txt). The IBKR terms of use were not read (section 10). Grade: firm-page (broker).

| Contract | IBKR all-in per side, tiered (no more than 1,000 contracts a month) | Fixed round trip | Verbatim |
|---|---|---|---|
| FDAX | EUR 2.16 | EUR 4.00 (all Eurex Germany) | "1 DAX Futures Contract = IBKR Execution Fee EUR 0.90 + Exchange Fee EUR 1.25 + Clearing Fee EUR 0.00 + Regulatory Fee EUR 0.01 = EUR 2.16"; "Fixed: 1 Roundturn = EUR 4.00" |
| FDXM | EUR 0.75 | EUR 4.00 | "1 Mini DAX Futures Contract = IBKR Execution Fee EUR 0.50 + Exchange Fee EUR 0.24 + Clearing Fee EUR 0.00 + Regulatory Fee EUR 0.01 = EUR 0.75" |
| FDXS | EUR 0.38 | EUR 4.00 | "1 Micro DAX Futures Contract = IBKR Execution Fee EUR 0.25 + Exchange Fee EUR 0.12 + Clearing Fee EUR 0.00 + Regulatory Fee EUR 0.01 = EUR 0.38" |
| FESX, FGBL | execution fee EUR 0.90 at no more than 1,000 contracts a month, plus exchange fees not listed in the examples | EUR 4.00 | "Germany Futures ... ≤ 1,000 EUR 0.90 /contract EUR 2.00 /contract" (tiered and fixed per side) |
| OSE N225 (large) | JPY 410 | JPY 800 | "1 N225 Futures Contract = IBKR Execution Fee JPY 280 + Exchange Fee JPY 110 + Clearing Fee JPY 20 + Regulatory Fee JPY 0.00 = JPY 410. If held overnight, additional JPY 10 per contract."; "N225: 1 Roundturn = JPY 800 N225 Mini: 1 Roundturn = JPY 80 MNTPX: 1 Roundturn = JPY 100 MJ: 1 Roundturn = JPY 170" |
| HKFE HSI and MHI | tiered "≤ 1,000 HKD 8.50 /contract" execution, plus exchange fee | HSI HKD 60.00, MHI HKD 34.00 | "Fixed: HSI: 1 Roundturn = HKD 60.00 MHI: 1 Roundturn = HKD 34.00" |
| SGX Nikkei mini (SGXNKM), SEY, SSG | "≤ 1,000 SGD 2.25 /contract" tiered execution | SGXNKM JPY 100; SEY JPY 600; SSG SGD 8.00 | "SSG: 1 Roundturn = SGD 8.00 SEY: 1 Roundturn = JPY 600 SGXNKM: 1 Roundturn = JPY 100" |
| ICE Europe USD contracts (Brent) | not given as an example | USD 4.80 | "Intercontinental Exchange (USD Denominated Contracts): 1 Roundturn = USD 4.80" |
| INE, SHFE | not on the page as read | n/a | the page has CNH-denominated columns for HK and SGX only; nothing was found for INE or SHFE |

IBKR market-data subscriptions per month. Source: https://www.interactivebrokers.ca/en/pricing/market-data-pricing.php, fetched 2026-10-18T13:17:07Z, sha256 fadfb0efbfc232ee..., pages/R16/ibkr_mktdata.html and .txt. The two fee columns are read as (non-professional, professional) from the page's table layout; the header row was not captured in the text extract, so that column order is an inference:

| Feed | Fees as printed | Verbatim |
|---|---|---|
| Eurex Core L1 / L2 | L1 waived; L2 EUR 13.00 / EUR 67.50 | "Eurex Core (L1) 3 Germany Fee Waived N/A Eurex Core (L2) 4 Germany EUR 13.00 EUR 67.50" |
| ICE Futures Europe Commodities (IPE, Brent) | USD 155.00 / USD 155.00 | "ICE Futures E.U. - Commodities (IPE) (L1, L2) 5 United Kingdom USD 155.00 USD 155.00" |
| ICE Futures Europe Financials | USD 132.00 / USD 132.00 | "ICE Futures E.U. – Financials (LIFFE) (L1, L2) 5 United Kingdom USD 132.00 USD 132.00" |
| Osaka Exchange L1 / L2 | JPY 200 / 1500 (L1); JPY 400 / 2200 (L2) | "Osaka Exchange (L1) 1 Japan JPY 200.00 JPY 1500.00 Osaka Exchange (L2) 1 Japan JPY 400.00 JPY 2200.00" |
| HKFE derivatives L1 / L2 | L1 waived; L2 HKD 100 | "Hong Kong Derivatives (Fut & Opt) (L1) 11 Hong Kong Fee Waived Fee Waived Hong Kong Derivatives (Fut & Opt) (L2) 11 Hong Kong HKD 100.00 HKD 100.00" |
| SGX derivatives L1 | SGD 2.00 | "Singapore Exchange (SGX) – Derivatives (L1) Singapore SGD 2.00 SGD 2.00" |
| Delayed data (free) | Eurex 15 min; IPE 10 min; OSE 20 min; SGX 10 min; HKFE 15 min | "Eurex EUREX 15 minutes ... ICE Futures Europe (Commodities) IPE 10 minutes ... Osaka Securities Exchange OSE.JPN 20 minutes ... SGX Derivatives SGX 10 minutes" |

Cost-estimate inputs (an ESTIMATE, not D8; tick sizes and values are [unverified] because no exchange spec page was fetched): FDXS commission at IBKR is 2 x 0.38 = EUR 0.76 per round trip. At Phidias it is 2 x 0.55 = EUR 1.10. Adding slippage needs a tick value and a spread. The commonly cited FDXS spec of 1 index point = EUR 1 [unverified] would make the commission alone about 0.76 index points, against FDAX near 24,000 [unverified price]. No exchange or vendor published a typical bid-ask spread in ticks in what this run read, so the slippage term is missing.

## 4. Negative evidence

- Topstep: no non-CME product; "No Forex".
- Phidias Terms of Use s.3.1.9 omits Eurex even though the rules page lists it. A firm's own documents disagree, so confirm with the firm before relying on Eurex at Phidias.
- Databento has no dataset for OSE, TOCOM, HKFE, SGX, INE or SHFE futures, and Eurex history starts only in 2025-03. That is about 19 months to 2026-10, and it overlaps the research window 2025-04..2026-06.
- Apex Eurex: sources conflict (FDXS only, versus FDAX/FDXM/FESX in a fee table). No primary source.

## 5. Data and cost

The program owns no Eurex, ICE or Asian data (brief s.4). A Eurex test on Databento history would cover only 2025-03-10 onward. ICE Europe history runs from 2018-12-23. Per-GB prices for XEUR and IFEU were not readable. No quote was requested.

## 6. Prop compatibility

Eurex at a prop firm currently means Phidias (semi-automated only; Premium allows overnight). Apex and Tradeify are reported only through secondary sources and both restrict automation. Topstep's API-allowed venue cannot trade Eurex. Its Asian-hours exposure is limited to CME products, NKD among them, inside 17:00-15:10 CT.

## 7. Overlap with tested mechanisms

Not applicable (no candidates).

## 8. Re-dig verdicts

Not applicable.

## 9. Fetch log

| url | UTC | sha256 (first 16) | path | status | tool |
|---|---|---|---|---|---|
| https://databento.com/venues | 2026-10-18T13:12:49Z | 23074b6320c9eaed | pages/R16/databento_venues.html | ok | curl |
| https://databento.com/pricing | 2026-10-18T13:12:55Z | 9470ffac83729821 | pages/R16/databento_pricing.html | ok (JS shell; R2's copy used) | curl |
| https://databento.com/docs/venues-and-datasets | 2026-10-18T13:13:35Z | ea3c0d4de144020a | pages/R16/db_docs_venues.html | ok (JS shell, no content) | curl |
| https://databento.com/datasets/XEUR.EOBI | 2026-10-18T13:13:42Z | b33de68a0e78d54a | pages/R16/db_xeur.html | ok | curl |
| https://databento.com/datasets/IFEU.IMPACT | 2026-10-18T13:13:49Z | b2c91094bc776e22 | pages/R16/db_ifeu.html | ok | curl |
| https://databento.com/datasets/IFUS.IMPACT | 2026-10-18T13:14:51Z | 8234cb0b2a1ed524 | pages/R16/db_ifus.html | ok | curl |
| https://www.interactivebrokers.ca/robots.txt | 2026-10-18T13:14:10Z | b69c27ba2b18a7ed | pages/R16/ibkr_robots.txt | ok | curl |
| https://www.interactivebrokers.ca/en/pricing/commissions-futures-europe.php | 2026-10-18T13:14:15Z | e7e8e25ced08595d | pages/R16/ibkr_ca_fut_comm.html | ok | curl |
| https://www.interactivebrokers.ca/en/pricing/market-data-pricing.php | 2026-10-18T13:17:07Z | fadfb0efbfc232ee | pages/R16/ibkr_mktdata.html | ok | curl |

Terms: databento.com, cited from the terms_log line (R2): "allowed for named public pages one at a time". interactivebrokers.ca: robots only; terms not read. Prop pages: R9's copies reused, with no new prop-domain requests. WebSearch: 2 calls, "Apex Trader Funding Eurex FDAX FESX allowed products Rithmic" and "Tradeify Eurex products FDAX allowed tradable instruments". No budget notices. OpenAlex and Firecrawl were not used (lead: OpenAlex budget exhausted, no Firecrawl credits).

## 10. Unfinished and unverified

- Plan-by-plan Eurex, ICE and Asian product lists for TPT, MFFU, Lucid, Alpha, FundedNext, Bulenox, Earn2Trade, TradeDay, ETF, The Trading Pit and Leeloo: not checked. Apex and Tradeify: secondary-only.
- Prop firms for ICE Europe, OSE, SGX, HKEX, INE and SHFE: not searched beyond the two queries above.
- Databento per-GB and per-venue subscription prices for Eurex and ICE (JavaScript-rendered); whether OSE or HKEX is "coming soon".
- INE/SHFE vendors (ICE Data Services, CQG), exchange data shops (Deutsche Boerse, JPX Data Cloud, HKEX), and their prices and terms.
- IBKR Canada: confirm the fee column order (non-professional vs professional) on the market-data page; margins; terms-of-use page; exchange fees for FESX and FGBL; other BC brokers.
- Contract specs (tick size and value for FDAX, FDXM, FDXS, FESX, FGBL, N225, HSI and Brent) and published typical spreads: [unverified]; no exchange page fetched.
