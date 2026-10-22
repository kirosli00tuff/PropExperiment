# A1_crypto: Layer 1 fact sheets for MET, ETH, MBT, BTC (Stage E.28 Part A)

Worker: A1_crypto (Opus 5.5), 2026-10-21 05:13-05:43 PDT. WebSearch calls used: 23 of 40. Facts only; no scoring. Every quote is verbatim from a
file saved under reports/stage_e28_briefs/pages/A1_crypto/ (log: pages/A1_crypto/log.tsv with URL, UTC and PDT
fetch time, method, sha256). Text files ending .txt are pdftotext/HTML-to-text renderings of the saved raw file of the
same stem. Helper scripts and derived outputs are in work/A1_crypto/.

Fetch situation (logged): cmegroup.com answers 403 to this machine (known); the Wayback Machine returned 429 and then
"Temporarily Offline" for part of the session; three of four Wayback captures of CME spec pages were shells with
JavaScript-loaded spec values (no tick or unit text); the Firecrawl connector returned "Insufficient credits"
(account out of credits). Contract terms were therefore taken from CME's own self-certification filings as posted on
cftc.gov (CME Submissions 21-005, 21-155, 21-477, 21-486, 19-015), plus a Wayback raw capture of CME Submission 17-417,, which carry the contract terms tables and rulebook
chapter text.

## F. Family-wide facts (CME cryptocurrency futures)

### F1. Trading hours (all four)

- MET filing (cftc_ptc112921cmedcm002.txt, CME Submission No. 21-477, lines 107-111): "Sunday - Friday 5:00 p.m. -
  4:00 p.m. Central Time (CT) (6:00 p.m. - 5:00 p.m. Eastern Time (ET) with a 60-minute break each day beginning at
  4:00 p.m. CT (5:00 p.m. ET)".
- ETH filing (cftc_ptc012621cmedcm001.txt, CME Submission No. 21-005, line 101): "Trading and Clearing Hours Sunday -
  Friday 5:00 p.m. - 4:00 p.m. CT (6:00 p.m. - 5:00 p.m. ET) with a 60-".
- So Globex is closed from Friday 16:00 CT to Sunday 17:00 CT, while crypto spot trades continuously (see F6).

### F2. Matching algorithm (all four: FIFO)

- MET (cftc_ptc112921cmedcm002.txt lines 167-169): "CME Globex F: First In First Out (FIFO) Matching Algorithm".
- ETH (cftc_ptc012621cmedcm001.txt lines 165-166): "CME Globex Matching F: First In First Out (FIFO) Algorithm".
  Restated unchanged in the Dec 2021 tick amendment (cftc_ptc111621cmedcm001.txt line 167-169).
- MBT (cftc_ptc042621cmedcm001.txt lines 138-139): "CME Globex Matching F: First In, First Out (FIFO) Algorithm".
- BTC (cme_rulefiling_17-417.txt, CME Submission 17-417, Wayback raw capture, lines 186-188): "CME Globex F: First
  In First Out (FIFO) Matching Algorithm".

### F3. Price limits and circuit breakers (Rule 589)

- 2017 launch design (BTC only; cme_rulefiling_17-417.txt lines 134-141): "a daily price limit at 20% above or below
  a reference price ... Given the volatility of bitcoin, special price fluctuation limits at 7% above or below and 13%
  above or below the reference price will be implemented. In the event the market hits the 7% or 13% limit, a cooling
  off period of 2 minutes will begin. If the market is still at limit at the completion of the cooling off period,
  trading will be temporarily halted for 2 minutes and will reopen at the expanded limit."
- 2019 change (cftc_ptc022119cmedcm001.txt, CME Submission No. 19-015, effective "Sunday, March 10, 2019"): lines
  75-82: "The amendments to CME Rule 589. adopt new section - (“Dynamic Price Fluctuation Limits”) to introduce
  dynamic price fluctuation limit functionality as a type of special price fluctuation limit. ... During the
  trading day, the dynamic variant will be utilized in continuously rolling 60-minute look-back periods to establish
  dynamic upper and lower price fluctuation ... dynamic price fluctuation limits will trigger a two (2) minute
  trading halt." Line 99: "The daily hard price limit will remain in place and will be expanded from 20% to 30%."
- ETH at launch (cftc_ptc012621cmedcm001.txt, Rule 589 table, lines 744-749): "10% of Dynamically Calculated
  Reference Price ... Ether Futures 349 ETH Primary Primary ... Daily Price Limit Table".
- MBT (cftc_ptc042621cmedcm001.txt line 683): "Micro Bitcoin Futures 348 MBT Associated BTC 10% of Dynamically
  Calculated Reference Price".
- MET (cftc_ptc112921cmedcm002.txt lines 786-790): "Micro Ether 10% of Dynamically Calculated Reference Price 347 MET
  Associated ETH Futures Daily Price Limit Table".
- January 2023 (cftc_ptc123022cmedcm002.txt, CME Submission No. 22-566, lines 70-73 and 117-123): amendments "in
  connection with all CME cryptocurrency futures contracts (and their associated products) to remove the existing
  price limit of 30% ... effective on trade date Friday, January 6, 2023"; "The Contracts will continue to be subject
  to Dynamic Price Fluctuation Limits with a 10% dynamic variant pursuant to Rule 589.D. ... Posted trades, bids or
  offers through the dynamic price fluctuation limits will trigger a two (2) minute trading halt." Table 1 lists
  BTC (350), MBT (348), ETH (349), MET (347). So from 2023-01-06 there is no hard daily limit, only 2-minute halts
  on a 10% move inside a rolling 60-minute window. Before that (2019-03-10..2023-01-05): dynamic halts plus a 30%
  hard limit (BTC), and per the launch filings a 10% dynamic variant for ETH, MBT and MET.
- Limit or halt hits 2019-2024: no CME or regulator list of crypto halt days was found. The only item is a news
  report (pointer only, not evidence): ptr_forklog_cme_halt_2020.html.txt: "The CME Bitcoin futures market opened on
  December 28 with the largest gap on record. After opening nearly 12% above Thursday’s close, trading of Bitcoin
  futures on the Chicago exchange was temporarily halted amid heightened volatility." Count of hit days per year:
  unknown.

### F4. Reportable level (relevant to reading the COT nonreportable share)

- MBT (cftc_ptc042621cmedcm001.txt line 135): "The reportable level shall be 1 Micro Bitcoin Futures (MBT)
  Contracts."
- ETH (cftc_ptc012621cmedcm001.txt lines 158-159): "The reportable level shall be 1 contract."
- MET (cftc_ptc112921cmedcm002.txt line 156): "The reportable level shall be 1 Micro Ether futures (MET) contract."
- These are exchange reportable levels. The CFTC COT files below nonetheless show nonzero nonreportable shares;
  how CFTC reporting thresholds for these markets relate to the exchange level was not established [unverified].

### F5. Positions by trader type: CFTC Traders in Financial Futures (TFF), futures only

Files: cftc_fut_fin_txt_2022.zip, _2023.zip, _2025.zip, _2026.zip (CFTC historical compressed TFF, futures only).
Script work/A1_crypto/A1_crypto_cot.py, output work/A1_crypto/A1_crypto_cot_out.txt. Share = (long + short + 2 x
spread) / (2 x open interest) per category; the five categories sum to 100%. Windows: W1 = 53 weekly reports
2022-11-01..2023-10-31; W2 = latest 52 reports 2025-10-21..2026-10-13. The pilot window 2023-11..2024-02 was not
read. TFF has no commercial-hedger category (crypto is a TFF market); Dealer/Intermediary is the sell side.

| CFTC market (code) | Window | Mean OI | Median OI | Dealer | Asset Mgr | Lev Money | Other Rept | Nonreportable (range) | Mean traders |
|---|---|---|---|---|---|---|---|---|---|
| BITCOIN - CME (133741) = BTC | W1 | 15,356 | 15,385 | 13.7% | 28.5% | 42.6% | 8.2% | 7.0% (5.3-8.5) | 108.5 |
| ETHER CASH SETTLED - CME (146021) = ETH | W1 | 4,405 | 4,433 | 8.1% | 10.7% | 51.2% | 15.5% | 14.6% (9.5-20.9) | 64.8 |
| MICRO BITCOIN - CME (133742) = MBT | W1 | 10,822 | 9,440 | 11.1% | 5.2% | 44.9% | 18.9% | 19.9% (9.2-31.8) | 91.6 |
| MICRO ETHER - CME (146022) = MET | W1 | 18,082 | 16,492 | 10.6% | 5.1% | 38.3% | 42.6% | 3.3% (1.7-5.7) | 93.5 |
| BTC (133741) | W2 | 22,539 | 22,192 | 24.3% | 19.5% | 47.1% | 4.2% | 4.9% (3.9-6.4) | 124.1 |
| ETH (146021) | W2 | 32,232 | 31,377 | 52.7% | 10.3% | 33.2% | 1.4% | 2.5% (1.7-6.7) | 94.3 |
| MBT (133742) | W2 | 29,353 | 28,631 | 10.8% | 3.9% | 52.5% | 16.9% | 15.9% (10.0-23.5) | 213.5 |
| MET (146022) | W2 | 109,408 | 62,865 | 3.1% | 5.3% | 67.6% | 21.8% | 2.2% (0.7-4.3) | 268.2 |

Open interest in contracts (MBT and MET are 1/50 and 1/500 of BTC and ETH by underlying amount; see the per-product
sheets). MET W2 OI ranges 36,131-490,147, so the mean is driven by a few weeks.

### F6. Spot linkage, weekend gap, 24/7 trading, basis

- Final settlement to a spot reference rate: ETH (cftc_ptc012621cmedcm001.txt, 34903.A): "the Final Settlement Price
  shall be the ETHUSD_RR published at 4 p.m. London time on the Last Trade Date". MBT (cftc_ptc042621cmedcm001.txt
  line 123): trading "terminates at 4:00 p.m. London time on the last Friday of the contract month"; the BRR (line
  215) is published "on its website at 4:00 p.m. London time 365 days per year"; line 231: "Currently, there are
  five (5) constituent exchanges: Bitstamp, Coinbase, Gemini, itBit and Kraken".
- Spot trades while Globex is closed: the BTC launch filing ties the limit reference price to spot moves on closed
  days (cme_rulefiling_17-417.txt lines 134-135): the reference price "generally will be set at the most recent
  daily settlement price but may be adjusted to incorporate BRR changes on non-trading days".
- Weekend gap example (news pointer only, not evidence): ptr_forklog_cme_halt_2020.html.txt, Dec 28 2020 open
  "nearly 12% above Thursday’s close" with a temporary halt.
- 24/7 trading began after the pilot window: mm_cme_247_launch.html.txt (MarketsMedia repost of the CME release):
  "CME Group ... announced it launched 24/7 trading for Cryptocurrency futures and options. The expanded trading
  hours, which went live on Friday, May 29, mark a significant milestone"; "Over its inaugural weekend, more than
  7,200 Cryptocurrency futures and options contracts were traded (~$50 million in notional) ... Volume was supported
  by a healthy ecosystem of retail and institutional firms." Year: the raw page metadata (mm_cme_247_launch.html) carries "datePublished":"2026-06-01T21:16:39+00:00", so the launch was Friday 2026-05-29. For 2023-11..2024-02 and for all of 2019-2024 the weekend gap applied.
- Basis to spot (size, sign, behaviour): no sourced number. Tried: BIS WP 1087 (Schmeling, Schrimpf, Todorov,
  "Crypto carry") at bis.org/publ/work1087.pdf returned an HTML page, not the PDF. Unknown.
- A 2026 working paper on the 24/7 switch exists (oa_247_2026.json: Runa Lee, "What Recedes and What Remains When
  Markets Go 24/7: Evidence from Bitcoin and Ether Futures", SSRN 7546659); OpenAlex holds no abstract and SSRN is
  blocked. Content unknown [unverified].

### F7. Scheduled product-specific high-impact releases

No scheduled crypto-specific release (an analogue of EIA inventories or USDA reports) was found in the CME filings,
FAQ or product pages read. The daily CME CF reference rates (BRR, ETHUSD_RR) are price fixings, not news releases.
Count per week: 0 found (absence, not a sourced statement; the US macro calendar is excluded by the spec).

### F8. Volume (ADV) and open interest, all sources found

| Product | Fact | Value | Window | Source file: quote |
|---|---|---|---|---|
| BTC | ADV | 13K | Oct 2023 | cme_crypto_review_2023-10.html.txt: "The October ADV for Bitcoin futures was 13K (+35% MoM), while OI averaged a record 17K (+10% MoM)." |
| BTC | OI peak | 20,369 | 2023-10-25 | same: "open interest in CME Group Bitcoin futures reached an all-time high of 20,369 contracts (nearly 102,000 equivalent bitcoin or $3.6 billion notional) on October 25" |
| BTC | ADV | 13,934 | 2021 YTD to Mar 17 | cftc_ptc042621cmedcm001.txt: "The Bitcoin futures year-to-date average daily volume as of March 17, 2021 is 13,934 futures contracts per day." |
| MBT | ADV, OI | 11.5K ADV; OI avg 9.2K | Oct 2023 | cme_crypto_review_2023-10.html.txt: "Micro Bitcoin futures October ADV was 11.5K (+96% MoM), while OI averaged 9.2K (+6% MoM)." |
| ETH | ADV, OI | 5.5K ADV; OI avg 4.7K | Oct 2023 | same: "Ether futures October ADV was 5.5K (+40% vs. Sep), and OI averaged 4.7K." |
| MET | ADV, OI | 10.4K ADV; OI avg 19.3K | Oct 2023 | same (Micro Ether section): "October ADV was 10.4K (+150% vs. Sep), and OI averaged 19.3K (+59% vs. Sep)." |
| MET, MBT | ADV | MET 182,000; MBT 62,000 | Sep 2025 | prn_cme_q3_2025_mondovisione.html.txt: "Micro Ether futures ADV increased 472% to 182,000 contracts"; "Micro Bitcoin futures ADV increased 50% to 62,000 contracts" |
| MET | ADV | 209,000 | Q3 2025 | same: "Record Micro Ether futures ADV of 209,000 contracts"; also "Record Ether futures ADV of 236,000 contracts" (whether this line aggregates Micro Ether is not stated; it exceeds MET alone, so it is likely an ether-complex figure [unverified]) |
| MET, MBT, ETH | ADV | MET 222,000; MBT 80,000; ETH 24,000 | Oct 2025 | prn_cme_oct_2025_mondovisione.html.txt: "Micro Ether futures ADV increased 583% to 222,000 contracts"; "Micro Bitcoin futures ADV increased 60% to 80,000 contracts"; "Ether futures ADV increased 357% to 24,000 contracts" |
| MET, MBT | ADV | MET 144,000; MBT 75,000 | calendar 2025 | srp_cme_2025_crypto_adv.html.txt (secondary, citing CME's 5 Jan 2026 statistics): "Micro Ether futures led the growth with an ADV of 144,000 contracts, while Micro Bitcoin futures reached 75,000" |
| ETH | ADV | 19,000 | Apr 2026 | cme_pr_2026-05-04_april_adv.html.txt (Wayback, CME release): "Ether futures ADV increased 33% to 19,000 contracts"; crypto total "Cryptocurrency ADV of 192,000 contracts ($14.8 billion notional)" |

Not found: a per-product 12-month ADV for 2022-11..2023-10 (CME monthly crypto reviews for other months were not in
the Wayback Machine under the same URL pattern: 404 for 2022-11..2023-08; the CDX index timed out), and a per-product
ADV for the latest 12 months (Oct 2025..Sep 2026; no 2026 monthly release other than April 2026 was retrieved; BTC
ADV after Oct 2023 not found). Open interest for both windows is in F5 (CFTC TFF, weekly). A0 owns the 1-minute-bar
volume figures.

### F9. Market-maker and incentive programs (CME filings on cftc.gov)

| Program | Products | Term | Source file: quote |
|---|---|---|---|
| Cryptocurrency Futures Market Maker Program | BTC, ETH, SOL, XRP (2026 scope) | from 2018-03-05, extended to 2027-01-31 | cftc_rules07162610506.txt: "Start date is March 5, 2018. End date is July 31, 2026 January 31, 2027"; "Bitcoin Futures (“BTC”), Ether Futures (“ETH”), SOL Futures (“SOL”), and XRP Futures (“XRP”) that are traded on Globex". Whether ETH was in scope during 2023-11..2024-02 is not shown by this 2026 version [unverified]. |
| Ether Futures Market Maker Program | ETH | 2021-02-08..2021-08-31 (as filed) | cftc_rule012821cmedcm004.txt: "Start date is February 8, 2021. End date is August 31, 2021." |
| Micro Bitcoin Futures Market Maker Program | MBT | 2021-05-03..2021-10-31 (as filed); further modifications listed 2024-01-12 and 2024-07-17 | cftc_rule041921cmedcm004.txt: "Start date is May 3, 2021. End date is October 31, 2021."; "participants must meet certain volume thresholds and quote two-sided markets in the Product at predetermined average bid/ask spreads and minimum quote sizes." The 2024 modification filings are known only from a search-result summary of the CFTC filings index [unverified]. |
| Micro Ether Futures Market Maker Program | MET | 2021-12-06, extended to 2025-01-31 | cftc_rules0715243344.txt: "Start date is December 6, 2021. End date is July 31, 2024 January 31, 2025." (active through the pilot window) |
| Micro Cryptocurrency Futures Market Maker Program | MBT, MET, MSL, MXP | from 2025-02-01, extended to 2027-01-31 | cftc_rules07162610502.txt: "Start date is February 1, 2025. End date is July 31, 2026 January 31, 2027"; "Micro Bitcoin Futures (“MBT”), Micro Ether Futures (“MET”), Micro SOL Futures (“MSL”), and Micro XRP Futures (“MXP”)" |
| Bitcoin Friday Futures Market Maker Program | MBT and BFF | 2024-09-30..2025-07-31 | cftc_rules01092513460.txt: "Micro Bitcoin Futures (“MBT”) and Bitcoin Friday Futures (“BFF”) that are traded on the CME Globex Platform" |
| Ether/Bitcoin Ratio Futures MM Program | ratio futures only | 2023-07-31..2024-01-31 | cftc_rules0714234097.txt: "Start date is July 31, 2023. End date is January 31, 2024." |

Other liquidity-provision statements: cftc_ptc042621cmedcm001.txt (2021): "A significant number of market makers
support the Bitcoin Futures contract." A "Micro Cryptocurrency Futures Market-Wide Fee Discount Program" was
modified in December 2023 per a search-result summary of CME's 2023 rule-filing list [unverified; not fetched].
The MET launch filing (cftc_ptc112921cmedcm002.txt): "It is expected that professional trading companies looking to
arbitrage price differences across other ether exchanges will provide additional liquidity."

### F10. Participants: retail, institutional, automated

- CFTC automated-trading series (Haynes and Roberts 2015; OCE updates 2017 and 2019; staff report "Impact of
  Automated Orders in Futures Markets" 2019): saved as cftc_haynes_roberts_2015, cftc_haynes_roberts_2017_update,
  cftc_ats_update2_2019, cftc_automated_orders_2019. A grep for bitcoin, crypto or ether finds no crypto product in
  any of them (the latest sample ends October 2018; cftc_ats_update2_2019.txt line 30: "2016 to October 31,
  2018"). No HFT or automated share for any crypto future was found. Unknown.
- Ferko, Moin, Onur, Penick (CFTC economists), "Who trades bitcoin futures and why?", Global Finance Journal 55
  (2023), abstract (repec_ferko2023.html.txt): "Using regulatory data with identifiers, we analyze the traders active
  in the Bit- coin futures (BTC) contracts traded on the Chicago Mercantile Exchange (CME). We find two primary trader
  types, those who hold almost exclusively BTC (con- centrated traders) and those who hold BTC to diversify a broader
  futures portfolio (diversified traders). ... Finally, we analyze the micro BTC contract and find that the trader
  composition is different than that of the full-size contract." Full text paywalled; how it differs is unknown.
- Retail statements: MET launch release (prn_cme_met_launch_2021_mondovisione.html.txt): Micro Ether futures are for
  "a range of market participants – from institutions to sophisticated, active, individual traders"; same release
  (Tim McCourt): "we have seen steady growth in liquidity in these contracts, especially among institutional
  traders" (about ETH). FIA MarketVoice 2021 (fia_mv_micro_bitcoin_retail_2021.html.txt): "Derivatives exchanges are
  rolling out smaller-sized versions of existing contracts to appeal to the rising number of retail investors
  interested in trading futures. The launch of micro bitcoin futures by exchange giant CME Group on May 3 is the
  latest proof of this trend"; Interactive Brokers: "about 65% of traded contracts come from outside the US"
  (geography, not a retail share). 24/7 launch (mm_cme_247_launch.html.txt): "Volume was supported by a healthy
  ecosystem of retail and institutional firms." No CME, CFTC or investor-presentation figure for the retail share of
  volume in any of the four products was found. Unknown as a number.
- BTC participant counts (cftc_ptc042621cmedcm001.txt, 2021): "The number of unique accounts that have traded the
  Bitcoin Futures contract since launch is above 7,700 ... As of December 2020, the number of large open interest
  holders of Bitcoin Futures grew to 110 and as of March 16, stands at 77."
- COT position shares: F5.

### F11. Published microstructure and short-horizon predictability evidence (crypto)

| Study | Relation to the four products | Data | Finding relevant to order-book predictability | Result | Evidence level |
|---|---|---|---|---|---|
| Aleti and Mizrach, "Bitcoin spot and futures market microstructure", J. Futures Markets 41(2) 2021 (oa_aleti_mizrach2021.json.abstract.txt) | same product (BTC) plus spot | CME BTC and four spot exchanges | Descriptive: "Spot market median trade sizes are under $1,300 but exceed $18,000 on the CME. Bid‐ask spreads average 0.0298%. ... 2.5% of trades and 15.5% of cancellations on Coinbase take place within 50 ms. ... The CME leads price discovery." No order-book predictability test stated in the abstract. | null for the C6 question (descriptive; no OFI or queue result reported in the abstract) | abstract only [unverified beyond abstract] |
| Akyildirim, Cepni, Corbet, Uddin, "Forecasting mid-price movement of Bitcoin futures using machine learning", Ann. Oper. Res. 2021 (lit_akyildirim2021_midprice_btcfut.xml.txt, PMC full text) | same product (BTC) | CME BTC 1-minute data, 2020-01-02..2020-09-10, 5-60 min horizons | "the average classification accuracy for five out of the six MLAs is consistently above the 50% threshold"; logistic regression "the average success rate for both in the sample and out-sample periods is almost always 54%". Inputs are price-based (no order-book variables); profitability measured as an "Ideal Profit Ratio", gross of costs. | positive (direction, minute bars, gross), not order-book | full text |
| Ferko, Moin, Onur, Penick 2023 (repec_ferko2023.html.txt) | same product (BTC, MBT) | CFTC regulatory data | participant types only | not a predictability study | abstract |
| Pati, "Informativeness of CME Micro Bitcoin Futures in Pricing of Bitcoin: Intraday Evidence", Finance Research Letters 2022 (oa_pati2022_mbt.json) | same product (MBT) | intraday | price discovery (title only; no abstract in OpenAlex) | unknown | title only [unverified] |
| Fang, Chung, Ventre, Basios, Kanthan, "Ascertaining price formation in cryptocurrency markets with machine learning", European J. Finance 2021 (oa_fang2021_crypto_ml.json.abstract.txt) | asset class only (spot exchanges) | tick data, crypto exchanges | "we applied a machine learning approach to predict the direction of the mid-price changes on the upcoming tick ... achieving a consistent 78% accuracy on the prediction of the mid-price movement on live exchange rate of Bitcoins vs. US dollars" | positive (tick-ahead mid-price direction; no cost-netted P&L stated) | abstract only |
| Scaillet, Treccani, Trevisan, "High-Frequency Jump Analysis of the Bitcoin Market", J. Financial Econometrics 2018 (lit_scaillet2018_btc_jumps.txt, arXiv 1704.08175) | asset class only (Mt. Gox spot 2011-2013) | tick data with trader IDs | "Jumps are frequent events and they cluster in time. The order flow imbalance and the preponderance of aggressive traders, as well as a widening of the bid-ask spread predict them." | positive (OFI predicts jumps), old unregulated spot venue | full text |
| Cestari, Barchi, Busetto, Marazzina, Formentin, "Hawkes-based cryptocurrency forecasting via Limit Order Book data", arXiv 2312.16190 (oa_hawkes_crypto_lob_2023.json.abstract.txt) | asset class only (USDT/USD spot) | LOB of a centralized exchange | "our strategy surpasses benchmark models in both prediction accuracy and cumulative profit when implemented in a trading environment" | positive (abstract; cost treatment not stated) | abstract only |
| "The Quarter-Hour Effect: Periodic Algorithmic Trading and Return Predictability in Cryptocurrency Futures", arXiv 2607.09426 v2 (lit_arxiv2607.09426_quarter_hour.txt) | asset class only (Binance perpetuals) | trade data, six perpetual contracts | "Opening returns are predictable out of sample, while opening order imbalance predicts returns over four to twelve hours, with much weaker effects at finer clock-time frequencies." | mixed: positive at quarter-hour boundaries over hours; weak at 1- and 5-minute frequencies | full text (abstract lines read) |
| Rajendran and Singaravelu, "Order-flow toxicity in cryptocurrency perpetual futures", Int. Rev. Econ. Finance 2026 (oa_ofi_toxicity_perp_2026.json.abstract.txt) | asset class only (Bybit perpetuals) | second-level order book and trades | "second-level order-book and trade-flow signals ... can detect order-flow toxicity"; "we ... interpret TailScore as a practically relevant adverse-selection risk-ranking signal, not ... a realised trading strategy." | positive for adverse-selection detection (not a P&L result) | abstract only |
| Pinto, "High-frequency dynamics of Bitcoin futures: An examination of market microstructure", Borsa Istanbul Review 2025 (oa_pinto2025.json.abstract.txt) | asset class only (Binance BTC and ETH perpetuals) | intraday 2020-2024 | MDH vs ITIH volatility-volume fit: "We find evidence favoring the MDH in the crypto futures market." | not a predictability study | abstract only (EconStor full text blocked by a bot check; scrapling get and fetch failed) |

No study was found that tests order-flow imbalance, queue imbalance, trade-sign predictability or passive
market-making profitability on CME Globex crypto futures (BTC, MBT, ETH, MET). Searches: OpenAlex (7 queries),
WebSearch ("order flow imbalance" CME bitcoin futures; Aleti and Mizrach full text), arXiv API (timed out). No paper
reporting that such patterns are absent on these CME products was found either.

### F12. Spreads, depth, queues, volume per minute

No sourced median bid-ask spread in ticks, top-of-book depth, touch queue size or volume per minute for BTC, MBT,
ETH or MET by session. CME's Bitcoin futures liquidity report page (cme_btc_liquidity_report.html.txt) only says
"This report highlights activity in Bitcoin futures, including historical CME Globex and block trade volume, ADV and
open interest, and bid/ask spread." (values load by script; none in the capture). The CME Liquidity Tool that holds
these statistics requires a login (search-result summary). A Quantitative Brokers whitepaper "Intraday Liquidity
Profiles of Bitcoin Futures and Micro Bitcoin Futures" (2021-06a) is gated (qb_2021_06a_btc_mbt_liquidity.html shows
only the research library page). Aleti and Mizrach's abstract gives an average spread of 0.0298% without saying
whether it is for CME or spot [unverified]. All unknown.

### F13. Volatility and jumps

- cftc_ptc042621cmedcm001.txt lines 384-386 (2021): "annualized realized volatility in the Bitcoin Futures contract
  rose to 120% in February 2021 and has averaged about 70% during the past three years. 30-day volatility has reduced
  to approximately 56% as at the beginning of April 2021".
- Jump frequency on the CME products: no study found. Spot only (Scaillet et al., Mt. Gox): 124 jump days in 888 days
  (lit_scaillet2018_btc_jumps.txt table: "Entire sample <0.01 124 888"), June 2011..November 2013.
- Days per year with |daily return| > 4 daily SD, 2019-2024: not computed (owned-bar magnitudes belong to A0; no
  published count found). Unknown.

## Per-product fact sheets

Family-wide facts F1-F13 apply to every product unless a sheet says otherwise. The 60-trade-date check for
2023-11-01..2024-02-29 rests only on launch date plus continuous listing (no market data was read): each product
launched before 2023-11, has CFTC TFF reports in every week of W1 and W2 (F5), CME volume statements for October
2023 (F8), and is a quarterly or monthly listed future traded Sunday-Friday (F1).

### MET: Micro Ether futures (CME, Globex code MET, rulebook chapter 347)

- Contract size: cftc_ptc112921cmedcm002.txt line 652: "The unit of trading shall be 0.10 ether."
- Tick: line 654: "The minimum price increment shall be 0.50 index points, equal to $0.05 per contract"; terms table
  line 133: "Outright: 0.50 index points = $0.05 per contract". (Index points = USD per ether.)
- Launch: lines 69-71: "for trading on the CME Globex electronic trading platform (“CME Globex”) and for submission
  for clearing via CME ClearPort effective on Sunday, December 5, 2021, for trade date Monday, December 6, 2021".
  Before 2023-11: yes.
- Matching: FIFO (F2). Hours: F1. Limits: 10% dynamic variant, 2-minute halts; 30% hard limit removed 2023-01-06 (F3).
  Limit-hit days 2019-2024: unknown.
- ADV: 10.4K (Oct 2023); 144,000 (calendar 2025, secondary); 182,000 (Sep 2025); 209,000 (Q3 2025); 222,000 (Oct
  2025). OI: CFTC TFF mean 18,082 (W1), 109,408 (W2, median 62,865). CME: "OI averaged 19.3K" (Oct 2023). F8, F5.
- Participants (TFF W1): Lev Money 38.3%, Other Reportables 42.6%, Dealer 10.6%, Asset Mgr 5.1%, Nonreportable 3.3%
  (W2: 67.6%, 21.8%, 3.1%, 5.3%, 2.2%). Exchange reportable level 1 contract (F4). Retail share: no number (F10).
- Market maker program: Micro Ether Futures Market Maker Program from 2021-12-06, extended to 2025-01-31 (covers the
  pilot window); Micro Cryptocurrency Futures MM Program from 2025-02-01 (F9).
- HFT or automated share: unknown (F10). Spread, depth, queue, volume per minute: unknown (F12).
- Scheduled product releases: none found (F7). Weekend gap: yes through 2026-05-28 (F6). Jumps: no CME-product study
  (F13). Basis: unknown (F6).
- Microstructure evidence: none on MET or ETH found; CME BTC studies (Aleti and Mizrach; Akyildirim et al.) are on a
  close cousin (same exchange, same asset class, different underlying); spot and perpetual-swap studies are asset
  class only (F11).

### ETH: Ether futures (CME, Globex code ETH, rulebook chapter 349)

- Contract size: cftc_ptc012621cmedcm001.txt line 657: "The unit of trading shall be 50 ether."
- Tick: from trade date 2021-12-06, cftc_ptc111621cmedcm001.txt lines 73-76: "to increase the minimum price
  fluctuation limit from 0.25 Index points ($12.50 per contract) to 0.50 Index points ($25.00 per contract) for
  trading on the CME Globex electronic ... effective Sunday, December 5, 2021 for trade date Monday, December 6,
  2021." So $0.50 per ether, $25.00 per contract.
- Launch: cftc_ptc012621cmedcm001.txt line 70: "for submission for clearing via CME ClearPort effective on Sunday,
  February 7, 2021, for trade date" Monday February 8, 2021 (the next line of the filing; also
  cme_crypto_review_2023-10.html.txt: "CME Group launched Ether futures on February 8, 2021."). Before 2023-11: yes.
- Matching: FIFO (F2). Hours: F1. Limits: 10% dynamic variant (launch table), 30% hard limit removed 2023-01-06 (F3).
- ADV: 5.5K (Oct 2023); 24,000 (Oct 2025); 19,000 (Apr 2026). OI: TFF mean 4,405 (W1), 32,232 (W2); CME "OI averaged
  4.7K" (Oct 2023).
- Participants (TFF W1): Lev Money 51.2%, Other Rept 15.5%, Asset Mgr 10.7%, Dealer 8.1%, Nonreportable 14.6%
  (W2: Dealer 52.7%, Lev Money 33.2%, Asset Mgr 10.3%, Other 1.4%, Nonrept 2.5%). Reportable level 1 contract.
  CME (2021): growth in Ether futures liquidity "especially among institutional traders" (F10).
- Market maker program: Ether Futures MM Program 2021-02-08..2021-08-31 as filed; ETH is in the Cryptocurrency
  Futures MM Program scope in the 2026 filing (program start 2018-03-05); ETH's inclusion during 2023-11..2024-02 is
  not verified (F9).
- HFT, spreads, depth, queues: unknown. Releases: none found. Weekend gap: yes (to 2026-05-28). Jumps, basis: unknown.
- Microstructure evidence: as MET.

### MBT: Micro Bitcoin futures (CME, Globex code MBT, rulebook chapter 348)

- Contract size: cftc_ptc042621cmedcm001.txt line 593: "The unit of trading shall be 0.10 bitcoin."
- Tick: line 595: "The minimum price increment shall be 5.00 index points, equal to $0.50 per contract"; terms table
  line 119: "Outright: 5.00 index points = $0.50 per contract". ($5 per bitcoin.)
- Launch: line 70: "CME ClearPort effective on Sunday, May 2, 2021, for trade date Monday, May 3, 2021". Before
  2023-11: yes.
- Matching: FIFO (F2). Limits: line 683: "Micro Bitcoin Futures 348 MBT Associated BTC 10% of Dynamically Calculated
  Reference Price"; 30% hard limit removed 2023-01-06 (F3).
- ADV: 11.5K (Oct 2023); 62,000 (Sep 2025); 80,000 (Oct 2025); 75,000 (calendar 2025, secondary). OI: TFF mean 10,822
  (W1, median 9,440), 29,353 (W2); CME "OI averaged 9.2K" (Oct 2023).
- Participants (TFF W1): Lev Money 44.9%, Nonreportable 19.9% (range 9.2-31.8%), Other Rept 18.9%, Dealer 11.1%,
  Asset Mgr 5.2% (W2: 52.5%, 15.9%, 16.9%, 10.8%, 3.9%). Highest nonreportable share of the four. Ferko et al.: MBT
  trader composition "is different than that of the full-size contract" (F10). FIA 2021 frames MBT's launch as retail
  demand (F10). Retail share as a number: unknown.
- Market maker program: Micro Bitcoin Futures MM Program from 2021-05-03 (term to 2021-10-31 as filed; 2024
  modifications known only from a filings-index search summary); Bitcoin Friday Futures MM Program incl. MBT
  (2024-09-30..2025-07-31); Micro Cryptocurrency Futures MM Program from 2025-02-01 (F9). MM coverage during
  2023-11..2024-02 is plausible but not verified from a fetched filing.
- HFT, spreads, depth, queues: unknown. Releases: none found. Weekend gap: yes (to 2026-05-28).
- Microstructure evidence: Aleti and Mizrach and Akyildirim et al. study BTC, the full-size version of the same
  underlying (F11); Pati 2022 studies MBT price discovery (title only).

### BTC: Bitcoin futures (CME, Globex code BTC, rulebook chapter 350)

- Contract size: cftc_ptc022119cmedcm001.txt (chapter 350 text in CME Submission 19-015) line 347: "The unit of
  trading shall be 5 bitcoin."
- Tick: line 349: "The minimum price increment shall be $5.00, equal to $25.00 per contract".
- Launch: cme_rulefiling_17-417.txt lines 70-71: "effective on Sunday, December 17, 2017, for trade date of Monday,
  December 18, 2017." Before 2023-11: yes.
- Matching: FIFO (cme_rulefiling_17-417.txt lines 186-188). Limits: 7%/13% special limits and 20% hard limit at
  launch; dynamic 2-minute halts and 30% hard limit from 2019-03-10; 30% limit removed 2023-01-06 (F3). Halt days:
  one news pointer (2020-12-28); count unknown.
- ADV: 13K (Oct 2023); 13,934 (2021 YTD to Mar 17). Latest 12 months: not found. OI: TFF mean 15,356 (W1), 22,539
  (W2); CME record 20,369 on 2023-10-25 and "OI averaged a record 17K" (Oct 2023).
- Participants (TFF W1): Lev Money 42.6%, Asset Mgr 28.5%, Dealer 13.7%, Other 8.2%, Nonreportable 7.0% (W2: 47.1%,
  19.5%, 24.3%, 4.2%, 4.9%). 2021 filing: above 7,700 unique accounts since launch; 77-110 large open interest
  holders (F10).
- Market maker program: Cryptocurrency Futures Market Maker Program, start 2018-03-05, BTC in scope in the 2026
  filing (F9); "A significant number of market makers support the Bitcoin Futures contract" (2021 filing).
- HFT, spreads, depth, queues: unknown (Aleti and Mizrach: CME median trade size above $18,000, abstract).
- Releases: none found. Weekend gap: yes (to 2026-05-28).
- Microstructure evidence (same product): Aleti and Mizrach 2021 (descriptive, CME leads price discovery; abstract
  only); Akyildirim et al. 2021 (minute-bar mid-price direction about 54% for logistic regression, gross, no
  order-book inputs). No order-book predictability or passive-MM study on BTC found (F11).

## Unknowns and failures (summary)

- Not found for any product: retail share of volume (number), HFT or automated share, median spread in ticks, depth
  at the best level, touch queue size, volume per minute, basis size, jump frequency on the CME products, limit-hit
  day counts 2019-2024, per-product ADV for 2022-11..2023-10 and for the latest 12 months (only single months and
  calendar 2025 for MET and MBT).
- Blocked or failed routes: cmegroup.com 403; Wayback 429 and offline periods, CDX timeouts; Firecrawl out of
  credits; arXiv API timeouts; EconStor bot check (scrapling get and fetch failed); SSRN not attempted (known 403);
  ScienceDirect and Wiley bot pages; Barchart and Crowdfund Insider bot pages; BIS WP 1087 returned HTML.
- [unverified] items: MBT MM program modifications in 2024; ETH in the crypto MM program scope during the pilot
  window; the Micro Cryptocurrency Futures Market-Wide Fee Discount Program; the 0.0298% spread's venue; the 2026
  24/7 working paper's content; Pati 2022's content.
