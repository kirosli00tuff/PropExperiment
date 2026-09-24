# Stage E.0 liquidity census (rerun): contract specs, ADV, OI

Run by LiquidityCensus2-OpusHigh, 2026-09-23 21:00 PDT. Supersedes `reports/stage_e0_liquidity_sonnet_failed.{md,json}`. Machine-readable copy: `reports/stage_e0_liquidity.json` (each figure with URL, fetch time and the verbatim row or sentence it was copied from).

Figures are copied from public pages. No ranking and no judgement of which products are liquid enough.

## Method and coverage

- **Route.** cmegroup.com blocks this machine's IP (curl returned CME's IP-block JSON, HTTP 403). Pages were fetched through Firecrawl (its own servers), then through Wayback captures fetched with local curl after Firecrawl's plan credits ran out at about 20:52 PDT. No Databento, no price or bar data recorded.

- **Tick specs (50/50).** From each product's CME contract-spec page, 'Minimum Price Fluctuation' row, outright tick. Some pages came from Firecrawl's cache (cachedAt 2026-09-22 20:19 UTC to 2026-09-24 01:49 UTC).

- **ADV (50/50).** Primary source: CME's monthly ADV reports, August 2026 edition, futures rows (all venues). Columns available for every product: ADV Aug 2026, Aug 2025, Jul 2026, YTD 2026 (Jan-Aug), YTD 2025 (Jan-Aug). NYMEX/COMEX products are matched by commodity code; CME/CBOT products by product name (the group report has no code column).

- **Full-year 2025 ADV (11/50).** CME's December 2025 ADV report (which would give full-year 2025 for every product) could not be retrieved: not in Wayback (CDX has 2025 captures only up to 2025-11-14), and `ftp/webmthly/2025/202512.zip` is IP-blocked to curl and returned HTTP 400 via Firecrawl. The 2025 annual press release (2026-01-05) gives full-year 2025 futures ADV for 11 of the 50 products (ZT, ZF, MNQ, HO, ZC, ZS, ZL, MGC, SIL, MBT, MET), rounded as published. Following the brief's order, the ADV column uses those 11 figures and **YTD 2026 (Jan-Aug)** for the other 39; the YTD 2026 column is filled for all 50 as a single common period.

- **OI (50/50).** CME daily Volume & Open Interest asset-class pages, trade date Tuesday 22 Sep 2026 (Final), futures row, 'Overall Combined Total' open interest (all contract months).

- **Listing dates.** 17 of the 20 micro/E-mini/E-micro products have a date with a quote; 3 not found (E7, QM, QG). Dates marked 'planned' come from pre-launch announcements.


## K1

| Sym | Exch | Name | Contract unit | Outright tick = USD | Listed | ADV (period) | ADV YTD 2026 Jan-Aug | ADV Aug 2026 | OI 2026-09-22 |
|---|---|---|---|---|---|---|---|---|---|
| NQ | CME | E-mini Nasdaq-100 Futures | $20 x Nasdaq-100 Index | 0.25 = $5 | 1999-06-21 | 593,595 (YTD26) | 593,595 | 510,604 | 286,321 |
| RTY | CME | E-mini Russell 2000 Index Futures | $50 x Russell 2000 Index | 0.10 = $5 | 2017-07-10 planned | 209,871 (YTD26) | 209,871 | 133,463 | 415,047 |
| YM | CBOT | E-mini Dow Jones Industrial Average Index Futures | $5 x Dow Jones Industrial Average index | 1.00 = $5 | 2002-04 (month only) | 108,142 (YTD26) | 108,142 | 61,873 | 88,087 |
| NKD | CME | Nikkei (USD) Futures | 5 USD x Nikkei Stock Average | 5.00 = $25 | n/a | 7,969 (YTD26) | 7,969 | 5,437 | 6,959 |
| ES | CME | E-mini S&P 500 Futures | $50 x S&P 500 Index | 0.25 = $12.5 | 1997-09-09 | 1,615,122 (YTD26) | 1,615,122 | 1,229,199 | 1,890,653 |
| MNQ | CME | Micro E-mini Nasdaq-100 Index Futures | $2 x Nasdaq-100 Index | 0.25 = $0.5 | 2019-05-06 | 1,600,000 (FY2025) | 2,363,465 | 2,383,284 | 119,984 |
| M2K | CME | Micro E-mini Russell 2000 Index Futures | $5 x Russell 2000 Index | 0.10 = $0.5 | 2019-05-06 | 115,832 (YTD26) | 115,832 | 68,235 | 33,875 |
| MYM | CBOT | Micro E-mini Dow Jones Industrial Average Index Futures | $0.50 x DJIA Index | 1.0 = $0.5 | 2019-05-06 | 152,686 (YTD26) | 152,686 | 101,135 | 19,934 |

## K2

| Sym | Exch | Name | Contract unit | Outright tick = USD | Listed | ADV (period) | ADV YTD 2026 Jan-Aug | ADV Aug 2026 | OI 2026-09-22 |
|---|---|---|---|---|---|---|---|---|---|
| ZT | CBOT | 2-Year T-Note Futures | Face value at maturity of $200,000 | 1/8 of 1/32 (0.00390625) = $7.8125 | n/a | 1,000,000 (FY2025) | 1,325,938 | 1,908,757 | 4,539,374 |
| ZF | CBOT | 5-Year T-Note Futures | Face value at maturity of $100,000 | 1/4 of 1/32 (0.0078125) = $7.8125 | n/a | 1,800,000 (FY2025) | 1,941,530 | 2,392,005 | 6,599,737 |
| ZN | CBOT | 10-Year T-Note Futures | Face value at maturity of $100,000 | 1/2 of 1/32 (0.015625) = $15.625 | n/a | 2,589,058 (YTD26) | 2,589,058 | 3,108,875 | 5,407,726 |
| TN | CBOT | Ultra 10-Year U.S. Treasury Note Futures | Face value at maturity of $100,000 | 1/2 of 1/32 (0.015625) = $15.625 | n/a | 819,357 (YTD26) | 819,357 | 1,144,786 | 2,587,440 |
| ZB | CBOT | U.S. Treasury Bond Futures | Face value at maturity of $100,000 | 1/32 (0.03125) = $31.25 | n/a | 609,604 (YTD26) | 609,604 | 851,806 | 1,887,864 |
| UB | CBOT | Ultra U.S. Treasury Bond Futures | Face value at maturity of $100,000 | 1/32 (0.03125) = $31.25 | n/a | 505,131 (YTD26) | 505,131 | 791,427 | 2,476,197 |

## K3

| Sym | Exch | Name | Contract unit | Outright tick = USD | Listed | ADV (period) | ADV YTD 2026 Jan-Aug | ADV Aug 2026 | OI 2026-09-22 |
|---|---|---|---|---|---|---|---|---|---|
| 6E | CME | Euro FX Futures | 125,000 Euro | 0.00005 = $6.25 | n/a | 216,466 (YTD26) | 216,466 | 138,686 | 821,689 |
| 6J | CME | Japanese Yen Futures | 12,500,000 Japanese yen | 0.0000005 = $6.25 | n/a | 180,897 (YTD26) | 180,897 | 167,109 | 378,701 |
| 6B | CME | British Pound Futures | 62,500 British pounds | 0.0001 = $6.25 | n/a | 103,657 (YTD26) | 103,657 | 64,463 | 244,925 |
| 6A | CME | Australian Dollar Futures | 100,000 Australian dollars | 0.00005 = $5 | n/a | 119,206 (YTD26) | 119,206 | 72,461 | 306,488 |
| 6C | CME | Canadian Dollar Futures | 100,000 Canadian dollars | 0.00005 = $5 | n/a | 81,946 (YTD26) | 81,946 | 66,489 | 311,085 |
| 6S | CME | Swiss Franc Futures | 125,000 Swiss francs | 0.00005 = $6.25 | n/a | 30,520 (YTD26) | 30,520 | 24,049 | 133,495 |
| 6M | CME | Mexican Peso Futures | 500,000 Mexican pesos | 0.00001 = $5 | n/a | 69,001 (YTD26) | 69,001 | 44,517 | 266,061 |
| 6N | CME | New Zealand Dollar Futures | 100,000 New Zealand dollars | 0.00005 = $5 | n/a | 40,801 (YTD26) | 40,801 | 31,862 | 101,377 |
| E7 | CME | E-mini Euro FX Futures | 62,500 euro | 0.0001 = $6.25 | not found | 4,018 (YTD26) | 4,018 | 2,004 | 10,759 |
| M6E | CME | Micro EUR/USD Futures | 12,500 euros | 0.0001 = $1.25 | 2009-03-23 planned | 24,552 (YTD26) | 24,552 | 12,815 | 16,425 |
| M6A | CME | Micro AUD/USD Futures | 10,000 Australlian Dollars | 0.0001 = $1 | 2009-03-23 planned | 7,765 (YTD26) | 7,765 | 3,352 | 2,927 |
| M6B | CME | Micro GBP/USD Futures | 6,250 British pounds | 0.0001 = $0.625 | 2009-03-23 planned | 4,290 (YTD26) | 4,290 | 1,855 | 2,513 |

## K4

| Sym | Exch | Name | Contract unit | Outright tick = USD | Listed | ADV (period) | ADV YTD 2026 Jan-Aug | ADV Aug 2026 | OI 2026-09-22 |
|---|---|---|---|---|---|---|---|---|---|
| CL | NYMEX | Crude Oil (WTI) Futures | 1,000 barrels | 0.01 = $10 | n/a | 1,079,857 (YTD26) | 1,079,857 | 742,600 | 1,841,811 |
| NG | NYMEX | Henry Hub Natural Gas Futures | 10,000 MMBtu | 0.001 = $10 | n/a | 521,792 (YTD26) | 521,792 | 458,873 | 1,837,146 |
| RB | NYMEX | RBOB Gasoline Futures | 42,000 gallons | 0.0001 = $4.2 | n/a | 206,850 (YTD26) | 206,850 | 179,392 | 361,099 |
| HO | NYMEX | NY Harbor ULSD Futures | 42,000 gallons | 0.0001 = $4.2 | n/a | 197,000 (FY2025) | 187,479 | 139,223 | 274,811 |
| MCL | NYMEX | Micro WTI Crude Oil Futures | 100 barrels | 0.01 = $1 | 2021-07-12 planned | 252,100 (YTD26) | 252,100 | 151,689 | 37,994 |
| QM | NYMEX | E-mini Crude Oil Futures | 500 barrels | 0.025 = $12.5 | not found | 9,446 (YTD26) | 9,446 | 4,046 | 2,244 |
| QG | NYMEX | E-mini Natural Gas Futures | 2,500 MMBtu | 0.005 = $12.5 | not found | 4,060 (YTD26) | 4,060 | 2,300 | 10,070 |
| MNG | NYMEX | Micro Henry Hub Natural Gas Futures | 1,000 MMBtu | 0.001 = $1 | 2023-11-06 | 14,942 (YTD26) | 14,942 | 6,807 | 7,665 |

## K5

| Sym | Exch | Name | Contract unit | Outright tick = USD | Listed | ADV (period) | ADV YTD 2026 Jan-Aug | ADV Aug 2026 | OI 2026-09-22 |
|---|---|---|---|---|---|---|---|---|---|
| GC | COMEX | Gold Futures | 100 troy ounces | 0.10 = $10 | n/a | 212,764 (YTD26) | 212,764 | 197,734 | 412,800 |
| SI | COMEX | Silver Futures | 5,000 troy ounces | 0.005 = $25 | n/a | 83,587 (YTD26) | 83,587 | 72,820 | 106,474 |
| HG | COMEX | Copper Futures | 25,000 pounds | 0.0005 = $12.5 | n/a | 77,679 (YTD26) | 77,679 | 86,037 | 301,657 |
| PL | NYMEX | Platinum Futures | 50 troy ounces | 0.10 = $5 | n/a | 22,360 (YTD26) | 22,360 | 19,082 | 65,373 |
| MGC | COMEX | Micro Gold Futures | 10 troy ounces | 0.10 = $1 | 2010-10-04 | 325,000 (FY2025) | 429,702 | 344,587 | 98,428 |
| SIL | COMEX | Micro Silver Futures (1,000 oz) | 1,000 troy ounces | 0.005 = $5 | 2013-06-15 (year inferred) | 48,000 (FY2025) | 134,882 | 63,140 | 17,295 |
| MHG | COMEX | Micro Copper Futures | 2500 pounds | 0.0005 = $1.25 | 2022-05-02 planned | 21,803 (YTD26) | 21,803 | 13,125 | 9,961 |

## K6

| Sym | Exch | Name | Contract unit | Outright tick = USD | Listed | ADV (period) | ADV YTD 2026 Jan-Aug | ADV Aug 2026 | OI 2026-09-22 |
|---|---|---|---|---|---|---|---|---|---|
| ZC | CBOT | Corn Futures | 5,000 bushels | 0.0025 (USD per bushel; quoted in cents: 1/4 cent) = $12.5 | n/a | 437,000 (FY2025) | 505,663 | 602,349 | 1,854,505 |
| ZW | CBOT | Chicago SRW Wheat Futures | 5,000 bushels (~ 136 metric tons) | 0.0025 (USD per bushel; quoted in cents: 1/4 cent) = $12.5 | n/a | 180,405 (YTD26) | 180,405 | 217,204 | 483,279 |
| ZS | CBOT | Soybean Futures | 5,000 bushels (~136 metric tons) | 0.0025 (USD per bushel; quoted in cents: 1/4 cent) = $12.5 | n/a | 293,000 (FY2025) | 302,997 | 266,856 | 1,114,328 |
| ZM | CBOT | Soybean Meal Futures | 100 short tons (~ 91 metric tons) | 0.10 = $10 | n/a | 181,637 (YTD26) | 181,637 | 166,698 | 657,637 |
| ZL | CBOT | Soybean Oil Futures | 60,000 pounds | 0.0001 (USD per pound; quoted in cents: 0.01 cent) = $6 | n/a | 182,000 (FY2025) | 232,819 | 218,667 | 605,458 |
| HE | CME | Lean Hog Futures | 40,000 pounds | 0.00025 (USD per pound) = $10 | n/a | 67,267 (YTD26) | 67,267 | 53,450 | 287,713 |
| LE | CME | Live Cattle Futures | 40,000 pounds (~18 metric tons) | 0.00025 (USD per pound) = $10 | n/a | 68,652 (YTD26) | 68,652 | 62,172 | 284,889 |

## K7

| Sym | Exch | Name | Contract unit | Outright tick = USD | Listed | ADV (period) | ADV YTD 2026 Jan-Aug | ADV Aug 2026 | OI 2026-09-22 |
|---|---|---|---|---|---|---|---|---|---|
| MBT | CME | Micro Bitcoin Futures | 0.10 bitcoin, as defined by the CME CF Bitcoin Reference Rate (BRR) | 5.00 (USD per bitcoin) = $0.5 | 2021-05-03 | 75,000 (FY2025) | 69,615 | 65,250 | 35,597 |
| MET | CME | Micro Ether Futures | 0.1 ether | 0.50 (USD per ether) = $0.05 | 2021-12-06 | 144,000 (FY2025) | 61,082 | 37,505 | 65,122 |

FY2025 = CME 2025 annual press release (futures, rounded as published). YTD26 = CME ADV report Aug 2026 edition, 'ADV Y.T.D 2026'. Tick values are for the outright; calendar-spread and TAS/BTIC ticks are in `tick_quote` in the JSON.


## Notes per figure that need care

- **Name-matched ADV rows (CME/CBOT).** LE uses row 'CATTLE' (feeder cattle is a separate row); HE 'HOGS'; ZW 'CHI WHEAT' (a separate 'WHEAT' row has ADV about 100); YM 'E-mini ($5) Dow'; MYM 'MICRO MINI $5 DOW'; NKD 'NIKKEI 225 ($) STOCK'; M6E/M6A/M6B 'MICRO EUR/USD' / 'MICRO AUD/USD' / 'MICRO GBP/USD'; E7 'E-MINI EURO FX'.

- **Group report aggregates micro and full-size energy under one name.** In the group report 'CRUDE OIL PHY' is 894,288 in Aug 2026 = CL 742,600 + MCL 151,689 (NYMEX/COMEX report, by code); the CL and MCL figures here come from the coded report, not the aggregate.

- **NG 2025.** The annual release gives Henry Hub 'futures and options' 904,000 (combined), kept as an alternate only; the NG ADV used is YTD 2026 futures.

- **ZT tick.** CME page: '1/8 of 1/32 of one point (0.00390625) = $7.8125' on $200,000 face (this settles the conflict flagged in the failed run).

- **6A tick.** CME page: '0.00005 per AUD increment = $5.00' (the failed run had 0.0001 / $10).

- **SIL listing date** (2013-06-15) has an inferred year: the CME article is undated; 2013 is inferred from its own text. Treat as unverified.

- **YM listing** is month-only (April 2002) from a CBOT release on a secondary host (Mondo Visione).

- **RTY listing** 2017-07-10 is the current CME listing (a return to CME), from the pre-launch announcement.


## Not found

- E7: listing date: WebSearch summaries say 1999; the cited pages (mdpi.com 2227-9091/9/6/111, marketswiki) were not read (MDPI 403 to curl and WebFetch); Firecrawl credits exhausted
- QM: listing date: WebSearch summary says NYMEX introduced E-mini crude and natural gas in mid-June 2002 (ScienceDirect S1044028305000402); page returned 403 to curl and WebFetch, not read
- QG: listing date: same as QM: 'mid-June 2002' seen only in a search summary; source page not read (403)
- 2025 full-year per-product ADV not found for 39 products: NQ, RTY, YM, NKD, ES, M2K, MYM, ZN, TN, ZB, UB, 6E, 6J, 6B, 6A, 6C, 6S, 6M, 6N, E7, M6E, M6A, M6B, CL, NG, RB, MCL, QM, QG, MNG, GC, SI, HG, PL, MHG, ZW, ZM, HE, LE. Tried: CME Dec-2025 ADV report (live URL now shows Aug 2026; Wayback CDX has no Dec-2025 capture), ftp/webmthly/2025/202512.zip (403 curl, 400 Firecrawl), Wayback CDX for cmegroup.com/ftp/webmthly/*, 2025 annual press release (names only 11 of the 50). investor.cmegroup.com/monthly-volume (WebFetch timeout, Firecrawl failed, curl 403). FIA statistics not tried (Firecrawl credits exhausted).

## Sources

- https://www.cmegroup.com/daily_bulletin/monthly_volume/Web_ADV_Report_CMEG.pdf (fetched 2026-09-23 20:34 PDT): CME Group Exchange ADV Report - Monthly, August 2026 (all exchanges; ADV Aug-26, Aug-25, Jul-26, YTD-26, YTD-25 by product name)
- https://www.cmegroup.com/daily_bulletin/monthly_volume/Web_ADV_Report_NYMEX_COMEX.pdf (fetched 2026-09-23 20:39 PDT): NYMEX/COMEX Exchange ADV Report - Monthly, August 2026 (same columns, with commodity codes)
- https://www.cmegroup.com/daily_bulletin/monthly_volume/Web_ADV_Report_CBOT.pdf (fetched 2026-09-23 20:39 PDT): CBOT Exchange ADV Report, August 2026; read to cross-check CBOT rows (e.g. 10-YR NOTE 3,108,875 / YTD 2,589,058 match the group report)
- https://www.cmegroup.com/daily_bulletin/monthly_volume/Web_ADV_Report_CME.pdf (fetched 2026-09-23 20:39 PDT): CME Exchange ADV Report, August 2026; PDF columns mis-parsed on page 1, NOT used for figures
- https://www.prnewswire.com/news-releases/cme-group-reports-record-annual-adv-of-28-1-million-contracts-in-2025--up-6-year-over-year-302652344.html (fetched 2026-09-23 20:53 PDT): CME Group press release 'Record Annual ADV of 28.1 Million Contracts in 2025' dated Jan 05, 2026 07:30 ET (PR Newswire copy; raw HTML read with curl; cmegroup.com copy blocked)
- https://www.cmegroup.com/market-data/browse-data/energy-volume.html (fetched 2026-09-23 20:32 PDT): CME daily Volume & Open Interest, asset class 'energy', trade date 22 Sep 2026 (Final)
- https://www.cmegroup.com/market-data/browse-data/equity-volume.html (fetched 2026-09-23 20:40 PDT): CME daily Volume & Open Interest, asset class 'equity', trade date 22 Sep 2026 (Final)
- https://www.cmegroup.com/market-data/browse-data/interest-rate-volume.html (fetched 2026-09-23 20:40 PDT): CME daily Volume & Open Interest, asset class 'rates', trade date 22 Sep 2026 (Final)
- https://www.cmegroup.com/market-data/browse-data/fx-volume.html (fetched 2026-09-23 20:40 PDT): CME daily Volume & Open Interest, asset class 'fx', trade date 22 Sep 2026 (Final)
- https://www.cmegroup.com/market-data/browse-data/metals-volume.html (fetched 2026-09-23 20:41 PDT): CME daily Volume & Open Interest, asset class 'metals', trade date 22 Sep 2026 (Final)
- https://www.cmegroup.com/market-data/browse-data/agriculture-commodities-volume.html (fetched 2026-09-23 20:41 PDT): CME daily Volume & Open Interest, asset class 'ag', trade date 22 Sep 2026 (Final)
- https://www.cmegroup.com/markets/<asset>/<...>/<product>.contractSpecs.html (50 pages, one per product; URL per product in tick_source_url) (fetched 2026-09-23 20:32-20:51 PDT): CME contract-spec pages via Firecrawl (tables only); several served from Firecrawl's cache, cachedAt between 2026-09-22 20:19 UTC and 2026-09-24 01:49 UTC
- https://www.cmegroup.com/ftp/webmthly/2025/ (fetched 2026-09-23 20:35 PDT): CME monthly volume archive directory; lists 202512.zip (not retrievable)
- https://www.cmegroup.com/openmarkets/equity-index/2024/The-Growth-of-Tech-and-25-Years-of-Nasdaq-Futures.html | archive: https://web.archive.org/web/20260513032841/https://www.cmegroup.com/openmarkets/equity-index/2024/The-Growth-of-Tech-and-25-Years-of-Nasdaq-Futures.html (fetched 2026-09-23 20:56 PDT): listing/launch date for NQ
- https://www.cmegroup.com/media-room/press-releases/2017/4/12/russell_2000_indexfuturesandoptionstoreturntocmegroupjuly10.html | archive: https://web.archive.org/web/20250818112751/https://www.cmegroup.com/media-room/press-releases/2017/4/12/russell_2000_indexfuturesandoptionstoreturntocmegroupjuly10.html (fetched 2026-09-23 20:55 PDT): listing/launch date for RTY
- https://mondovisione.com/media-and-resources/news/cbot-minisized-dow-shatters-previous-volume-record-2011124/ (fetched 2026-09-23 20:56 PDT): listing/launch date for YM
- https://www.cmegroup.com/company/product-anniversaries.html | archive: https://web.archive.org/web/20260613123321/https://www.cmegroup.com/company/product-anniversaries.html (fetched 2026-09-23 20:56 PDT): listing/launch date for ES
- https://www.cmegroup.com/media-room/press-releases/2019/5/06/cme_group_announceslaunchofnewmicroe-miniequityindexfutures.html (fetched 2026-09-23 20:51 PDT): listing/launch date for MNQ, M2K, MYM
- https://www.cftc.gov/sites/default/files/stellent/groups/public/@rulesandproducts/documents/ifdocs/rul021909cme002.pdf (fetched 2026-09-23 20:55 PDT): listing/launch date for M6E, M6A, M6B
- https://www.cmegroup.com/media-room/press-releases/2021/5/17/cme_group_to_launchmicrowtifuturesonjuly12.html (fetched 2026-09-23 20:51 PDT): listing/launch date for MCL
- https://www.cmegroup.com/media-room/press-releases/2023/11/08/micro_henry_hub_futuressurpass50000contractstraded.html | archive: https://web.archive.org/web/20241212021947/https://www.cmegroup.com/media-room/press-releases/2023/11/08/micro_henry_hub_futuressurpass50000contractstraded.html (fetched 2026-09-23 20:54 PDT): listing/launch date for MNG
- https://www.cmegroup.com/media-room/press-releases/2010/9/09/cme_group_announceslaunchofe-microgoldcontracts.html (fetched 2026-09-23 20:52 PDT): listing/launch date for MGC
- https://www.cmegroup.com/trading/metals/files/cme-micro-silver-article.pdf | archive: https://web.archive.org/web/20211021072236/https://www.cmegroup.com/trading/metals/files/cme-micro-silver-article.pdf (fetched 2026-09-23 20:55 PDT): listing/launch date for SIL
- https://www.cmegroup.com/media-room/press-releases/2022/4/05/cme_group_to_launchmicrocopperfuturesonmay2.html (fetched 2026-09-23 20:52 PDT): listing/launch date for MHG
- https://www.cmegroup.com/media-room/press-releases/2021/5/03/cme_group_announceslaunchofmicrobitcoinfutures.html (fetched 2026-09-23 20:52 PDT): listing/launch date for MBT
- https://www.cmegroup.com/media-room/press-releases/2021/12/06/cme_group_announceslaunchofmicroetherfutures.html (fetched 2026-09-23 20:52 PDT): listing/launch date for MET
