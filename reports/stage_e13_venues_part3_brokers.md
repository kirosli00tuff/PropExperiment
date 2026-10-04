# Stage E.13 Task 1, part 3: personal futures accounts for a British Columbia resident

Worker: BrokerVenues-OpusHigh. Research only. No login, no account, no quote request, no contact with
any broker. Every page cited below is saved under `reports/stage_e13_briefs/pages/BrokerVenues/`
(fetch ids F001 to F096 in `fetch_log.md`; all fetched 2026-10-03). Quotes are verbatim, grepped from
the saved files. Where a figure is my arithmetic from published components it is marked "computed".
A fact without a broker-side source is marked UNSOURCED.

Bottom line: on the broker's own pages, only Interactive Brokers Canada Inc. (IBKR Canada) shows all
four things this project needs together: a Canadian (CIRO) dealer serving Canadian residents, US CME
Group futures including the micros, an order-entry API, and published overnight margins and costs.
Wealthsimple now offers futures to Canadians but shows no API. The US FCMs either exclude BC (NinjaTrader,
Tradovate), allow BC only case by case (AMP), or give no BC statement of their own (Ironbeam,
EdgeClear, TradeStation, GFF). A BCSC exemption pattern (below) is the likely reason for this. The
bank-owned brokers, Questrade and Qtrade offer no futures.

## 0. Regulatory point that decides eligibility in BC

- BC Securities Act s. 34(a) needs dealer registration to trade exchange contracts (futures) with BC
  residents. Foreign dealers that are not registered in BC get exemptions under s. 48 that cover only
  "eligible derivatives parties" (sophisticated investors). For individuals, the definition requires
  financial assets of at least $5,000,000 [B-15], [B-16], [B-17]. Quote [B-15]
  (2024 BCSECCOM 523, RBC Capital Markets, LLC, December 20, 2024): "granting relief from the
  requirement in section 34(a) of the Act for the Filer to be registered as a dealer in connection
  with trades in contracts or instruments, including futures contracts and options ... with the
  Jurisdiction's residents that fall within the definition of "eligible derivatives party"". The
  headnote reads: "the person will only trade exchange contracts with sophisticated investors." Para (o)
  of the definition reads: "an individual that beneficially owns financial assets ... of at least $5 000 000".
  The same template appears in 2025 BCSECCOM 346 (StoneX Financial Ltd., July 31, 2025) [B-16] and
  2025 BCSECCOM 141 (Duneland Commodities Inc. dba DLC Risk Management, April 3, 2025) [B-17].
- My reading, not a legal opinion: a retail BC resident should use a BC-registered dealer, in practice
  a CIRO investment dealer. IBKR Canada says: "Interactive Brokers Canada Inc. is a member of the
  Canadian Investment Regulatory Organization (CIRO)" [B-02], [B-10]. Wealthsimple places itself among
  "Canadian investment dealers regulated by CIRO that offer futures trading" [B-41]. Jitneytrade Inc.
  "is registered as an Investment Dealer with the Canadian Investment Regulatory Organization (CIRO) and
  the Canadian Security Administrators in most provinces and territories" [B-52]. US FCMs that accept
  BC residents "at the discretion of a senior manager" [B-18] or as "Non-Solicited Self-Directed"
  clients [B-29] are relying on a basis their pages do not explain. Treat them as UNCLEAR.
- Registered accounts are out. At IBKR Canada the RRSP and TFSA lists of qualified investments contain
  no futures, and the RRSP section says "Margin trading is not permitted in a RRSP/SRRSP" [B-11].
  Wealthsimple: "Futures are not permitted in Tax-Free Savings Accounts (TFSAs) or Registered Retirement
  Savings Plans (RRSPs). You must use a non-registered account." [B-42]

## 1. Broker summary table

Commission column: per contract per side for MES at the lowest-volume tier, including exchange and
regulatory fees where the broker publishes them.

| Broker | BC residents (US futures) | Minimum | API (futures orders) | Multi-day holds | Micros listed | Commission (micro, per side, all-in) | Market data cost | Notes |
|---|---|---|---|---|---|---|---|---|
| IBKR Canada (Interactive Brokers Canada Inc.) | Yes: CIRO dealer for Canadian residents; US futures permission listed; separate margin schedule "For residents of Canada trading futures and FOPs" [B-06], [B-10], [B-12] | Account minimum USD 0.00 [B-08]; stock margin needs $2,000 equity [B-13]; futures-specific minimum UNSOURCED | TWS API, Web API (REST), FIX. TWS API and REST over the Internet: "USD 0.00 per month minimum commission". FIX: USD 1,500/month minimum [B-08], [B-09], [B-14] | Yes. Overnight margins published; intraday rates revert "back to the full overnight margin requirement" each day [B-06] | All in item 4 except where noted: MES, MNQ, M2K, MYM, MCL, MGC, SIL, MHG, MBT, MET, M6E, M6A, M6B, MCD, MJY, MSF, 2YY, 5YY, 10Y, 30Y, MHNG (class MNG), MZC, MZS, MZW, MZL, MZM [B-01], [B-06] | MES USD 0.61 (computed: 0.25 IBKR + 0.35 exchange + 0.01 regulatory) [B-01], [B-02] | "US Securities Snapshot and Futures Value Bundle" USD 10.00/month non-pro, waived at USD 30 commissions; covers CBOT, CME, COMEX, NYMEX top of book. Or CME Real-Time (L1) USD 1.55/month non-pro per exchange [B-07] | PERMITTED. Inactivity fee USD 0.00 [B-08] |
| Wealthsimple | Probably yes (national CIRO dealer, futures launched for Canadians), but no page I could retrieve names BC or the provinces; the help article was 403 and no Wayback capture exists. UNSOURCED for BC specifically [B-41] | Margin account required ("Futures trading is only offered in margin accounts": search snippet only, help page 403, so UNSOURCED); no minimum found | No API found on its futures pages. Terms forbid scraping, reverse engineering and circumventing rate limits [B-43] | UNSOURCED (page says "Margin — returned when position closes", trading "nearly 24/7") [B-41] | "micro, mini, and standard contract sizes"; examples S&P 500, gold, oil; full list is on the help page (403). Per-symbol: UNSOURCED [B-41] | MES USD 1.37 (computed: "$1 USD per contract" + "$0.35 and $0.02 ... for the micro S&P 500") [B-41] | "$0 real-time market data — no subscription required" [B-41] | HUMAN-IN-THE-LOOP ONLY (no API). Margins are shown only in the app |
| AMP Futures (AMP Global Clearing, US FCM) | Only at discretion: "Only 3 provinces in Canada are allowed: Alberta, Ontario and Quebec. Additionally, British Columbia accounts may be allowed at the discretion of a senior manager." [B-18] (Wayback 2025-09-11) | "$100" (2019 news) [B-23]; current figure UNSOURCED | Rithmic R \| API (C++/.NET): $100/month plus $25 user ID, plus $0.10 per contract routing; also TT API, CQG [B-22] | Yes: "Maintenance Margin ... is the amount required to carry a contract past the daily close" [B-20] | MES, MNQ, M2K, MYM, MCL, MGC, SIL, MHG, M6E, M6A, M6B, MCD, MJY, MSF, 2YY, 5YY, 10Y, 30Y, MNG, MZC, MZS, MZW on margin page; MBT, MET not on margin page [B-20] | Current: not published (quote form) [B-24]. 2019 example: "Total per Side $0.42" [B-23] (stale; CME fees rose since) | CME Bundle L1 $15/month, CME/Globex L1 $5/month non-pro ("Prices effective June 1, 2026") [B-21] | UNCLEAR (BC acceptance discretionary; see BCSC point) |
| NinjaTrader Brokerage | No: "Canadian law restricts NinjaTrader from opening accounts for residents of Canada that are outside of the province of Ontario. This includes all other provinces: ... British Columbia ..." [B-25] (Apr 16, 2025) | n/a | NinjaTrader API licence: "access and use the API solely for the purpose of connecting Your order entry and/or trading program(s)" [B-27]; "Build, test, and deploy automated trading strategies" [B-28] | n/a | n/a | n/a | n/a | NOT PERMITTED. BC users may run the NinjaTrader platform with a third-party broker [B-25] |
| Tradovate | No: same restriction; "If you are in Canada, but outside of Ontario, you are still able to use Tradovate in Simulated Mode." [B-26] (Nov 19, 2024) | n/a | API exists (NinjaTrader group API [B-27]); irrelevant for BC | n/a | n/a | n/a | n/a | NOT PERMITTED |
| Optimus Futures (introducing broker) | Claimed via clearing firms: "We accept all Non-Solicited Self-Directed Canadian futures traders when you Open an Optimus Futures account that is cleared through Phillip Capital and Ironbeam." [B-29]. 2019 forum post: "If you are currently living in BC, Canada, we can accept you as a client with Ironbeam." [B-31] | UNSOURCED | UNSOURCED on fetched pages (offers Optimus Flow, CQG, Rithmic per [B-31]) | UNSOURCED | UNSOURCED | UNSOURCED | UNSOURCED | UNCLEAR ("Non-Solicited" basis; BCSC exemption pattern) |
| Ironbeam (US FCM) | Not stated for BC on Ironbeam's own pages: "To confirm whether your country is supported, please send a message to [email protected]" [B-32], [B-33] | "Ironbeam has no account minimum." [B-33] | Ironbeam API (REST): "Send orders to the exchange directly from your API connection"; fee UNSOURCED [B-35] | Yes: overnight margins published [B-34] | MES, MNQ, M2K, MYM, MCL, MGC, SIL, MHG, MBT, MET, M6A, M6B, M6E, MCD, MJY, MSF, 2YY, 5YY, 10Y, 30Y, MNG [B-34] | UNSOURCED: pricing page is password-protected [B-36] | UNSOURCED | UNCLEAR |
| EdgeClear (US IB) | No statement on edgeclear.com; only third-party claims (not used). UNSOURCED [B-37] | UNSOURCED (commission calculator is JavaScript) | "Automated Trading Solutions ... EdgeQX Automation"; Rithmic [B-37] | UNSOURCED | UNSOURCED | UNSOURCED | UNSOURCED | UNCLEAR |
| TradeStation (US) | No Canada statement on tradestation.com; international clients need paper applications [B-38]. A third-party claim that Canadians cannot trade futures there was not verified on a TradeStation page. UNSOURCED | UNSOURCED | "Multi-asset brokerage API: equities, futures, and options ... from a single API key"; REST and FIX [B-39] | UNSOURCED | UNSOURCED | UNSOURCED | UNSOURCED | UNCLEAR (leans NOT PERMITTED; unverified) |
| GFF Brokers (US IB) | Not stated: "Country-specific options depend on the clearing firm's regulatory coverage - reach out" [B-51] | UNSOURCED | UNSOURCED | UNSOURCED | UNSOURCED | UNSOURCED | UNSOURCED | UNCLEAR (NinjaTrader names GFF and IBKR as the Canadian options but does not give provinces; forum source only) |
| Jitneytrade Inc. (Montreal, CIRO) | CIRO investment dealer "in most provinces and territories" [B-52]; BC and US futures UNSOURCED: jitneytrade.com did not resolve (DNS failure, F092/F094) | UNSOURCED | UNSOURCED | UNSOURCED | UNSOURCED | UNSOURCED | UNSOURCED | UNCLEAR (site unreachable) |
| Questrade | No futures. Product list: "More than just Stocks & ETFs. Trade options, precious metals, and IPOs" [B-40]; offers CFDs instead [B-53] | n/a | n/a | n/a | n/a | n/a | n/a | NOT PERMITTED (no futures product) |
| TD Direct Investing | No futures. Commission schedule covers equities, options, gold/silver, fixed income and mutual funds, with no futures section [B-46]. Active Trader shows "CME Futures (15 Min Delayed)" as a data package only [B-45] | n/a | n/a | n/a | n/a | n/a | n/a | NOT PERMITTED (no futures product) |
| RBC Direct Investing | No: account approval text says "The Customer may NOT ... nor buy or sell futures." [B-44] | n/a | n/a | n/a | n/a | n/a | n/a | NOT PERMITTED |
| BMO InvestorLine | No: "BMO InvestorLine Inc. is not registered to trade in futures." [B-47] | n/a | n/a | n/a | n/a | n/a | n/a | NOT PERMITTED |
| CIBC Investor's Edge | No futures in "Investment choices" (Stocks, ETFs, Options, CDRs, Mutual Funds, GICs, Fixed Income, Precious Metals, IPOs, Structured Notes) [B-48] | n/a | n/a | n/a | n/a | n/a | n/a | NOT PERMITTED (no futures product; list-based) |
| National Bank Direct Brokerage | No futures; "Futures contracts" are on its list of products that cannot be transferred in [B-49] | n/a | n/a | n/a | n/a | n/a | n/a | NOT PERMITTED (indirect evidence) |
| Qtrade Direct Investing | No futures: "access to a wide array of stocks, ETFs, mutual funds, bonds, options and more" [B-50] | n/a | n/a | n/a | n/a | n/a | n/a | NOT PERMITTED (list-based) |

### IBKR Canada detail (every field of the brief)

1. BC residents: IBKR Canada is the Canadian entity. Its margin pages carry a residence selector, and the
   US-futures page for "hm=ca" says "For residents of Canada trading futures and FOPs: You are subjected to
   margin requirements." [B-06]. Its trading-permissions page lists "Futures ... United States" [B-10].
   CIRO member [B-02]. No page names BC specifically; nothing excludes any province. Account types:
   Individual, Joint, Trust, RRSP/SRRSP, TFSA, FHSA. "Margin | Cash, Reg T and Portfolio Margin are
   available." [B-12]. Futures go in a non-registered account [B-11].
2. Minimums: "Account Minimums | USD 0.00", "Inactivity Fees | USD 0.00" [B-08]. Stock margin: "All
   stocks bought or sold on margin require a minimum of $2,000 in equity" [B-13]. Portfolio Margin needs
   "at least $100,000" (F012). A futures-specific minimum equity was not found: UNSOURCED. Futures
   commissions and margins are charged "in the currency of the traded product" [B-01], so US futures run
   in USD.
3. API: "Web API ... RESTful API + Websockets", "TWS API ... develop applications in C++, C#, Java, Python",
   "Programmatically place orders including advanced order types" [B-09]. The TWS API documentation shows
   futures contracts defined with `SecType = "FUT"` [B-14]. Cost: "Gateway (Internet) | Trader Workstation
   and TWS API | REST API | ... USD 0.00 per month minimum commission"; FIX CTCI "USD 1,500.00 per month
   minimum commission for the first FIX session" [B-08]. API-specific restrictions in the client
   agreement: UNSOURCED (the agreements page is JavaScript-rendered, F017). Overnight and multi-day holds:
   overnight initial and maintenance margins are published per contract, and "Each day at 'Intraday End
   Time' the futures contract will revert back to the full overnight margin requirement until the
   'Intraday Start Time' the next day." [B-06]
4. Micros: listed in the commission schedule's micro group: "E-micro Futures and Futures Options (MES,
   MNQ, M2K, VOLQ, MYM, 2YY, 5YY, 10Y, 30Y, MCL, MRB, MGC, MWN, MTN, SIL, VXM, MHNG, MHO, MNK, MNI, MZC,
   MZS, MZW, MZL, MZM, ...)". MBT and MET are in their own groups. Micro FX: "E-Micro FX Futures" [B-01].
   Margin rows exist for all of them plus NG, ZN, ZF, ZT [B-06]. Micro Henry Hub: product MHNG, trading
   class MNG [B-06]. Micro grains: MZC, MZS, MZW, MZL, MZM [B-06].
5. Commissions, lowest tier (≤1,000 contracts/month; the Fixed and Tiered rates match at this tier):
   micro group USD 0.25, E-micro FX USD 0.15, MBT USD 0.85, MET USD 0.20, other USD futures USD 0.85
   [B-01]. Exchange-fee recovery (non-member, Tier I): MES/MNQ/M2K USD 0.35 [B-02]; MYM USD 0.35, micro
   yields USD 0.30, micro ags USD 0.50, ZN USD 0.80, ZF and ZT USD 0.65 [B-03]; MCL USD 0.50, MHNG USD
   0.60, NG USD 1.60 [B-04]; MGC USD 0.70, MHG USD 0.70 [B-05]; E-micro FX USD 0.24, MBT USD 1.15, MET
   USD 0.10 [B-02]. Regulatory (NFA): USD 0.01 [B-02]. Clearing fee USD 0.00 in IBKR's worked example
   ("1 ES Futures Contract = IBKR Execution Fee USD 0.85 + Exchange Fee USD 1.38 + Clearing Fee USD 0.00
   + Regulatory Fee USD 0.00 = USD 2.24") [B-01]. All-in per side (computed): MES, MNQ, M2K, MYM 0.61;
   2YY to 30Y 0.56; MCL 0.76; MZC/MZS/MZW 0.76; MHNG 0.86; MGC 0.96; MHG 0.96; micro FX 0.40; MBT 2.01;
   MET 0.31; ZN 1.66; ZF 1.51; ZT 1.51; NG 2.46. SIL's exchange fee is not on the COMEX fee page
   (UNSOURCED). Market data: as in the table [B-07]. Footnote: "Access to US Futures data requires
   clients to have US Futures Trading Permissions." [B-07]
6. Margins: section 2 below. The page shows no date.
7. Inactivity: USD 0.00 [B-08]. Market-data bundle fee waived at USD 30 commissions per month [B-07].

## 2. Margin table

IBKR Canada, page "US Futures and FOPs Margin Requirements" for residents of Canada (F010, no date shown,
fetched 2026-10-03). USD per contract. IBKR also publishes a separate "Short Overnight" pair, shown last.
"Intraday" means IBKR's intraday initial/maintenance; N/A means no reduced intraday rate.

| Contract | Broker | Initial (overnight) | Maintenance (overnight) | Intraday (initial / maint) | Short overnight (initial / maint) | Page date | Source key |
|---|---|---|---|---|---|---|---|
| MES | IBKR Canada | 3,704.55 | 2,608.90 | 2,593.185 / 1,826.23 | 2,869.79 / 2,608.90 | no date shown | B-06 |
| MNQ | IBKR Canada | 7,359.31 | 4,322.20 | 5,151.52 / 3,025.54 | 5,560.10 / 4,321.97 | no date shown | B-06 |
| M2K | IBKR Canada | 1,383.08 | 1,090.50 | 968.153 / 763.35 | 1,253.50 / 1,090.00 | no date shown | B-06 |
| MYM | IBKR Canada | 1,807.535 | 1,521.01 | 1,265.27 / 1,064.71 | 1,749.16 / 1,521.01 | no date shown | B-06 |
| MCL | IBKR Canada | 1,901.78 | 1,521.42 | N/A | 2,178.78 / 1,521.42 | no date shown | B-06 |
| MGC | IBKR Canada | 3,788.37 | 3,294.23 | N/A | 4,108.37 / 3,294.23 | no date shown | B-06 |
| SIL (row: underlying SI, class SIL) | IBKR Canada | 11,201.51 | 9,740.44 | N/A | 12,945.00 / 9,740.44 | no date shown | B-06 |
| MHG | IBKR Canada | 2,484.25 | 1,634.50 | N/A | 2,419.25 / 1,634.50 | no date shown | B-06 |
| MBT | IBKR Canada | 3,116.11 | 2,601.09 | N/A | 2,991.25 / 2,601.09 | no date shown | B-06 |
| MET | IBKR Canada | 126.448 | 109.955 | N/A | 158.11 / 137.444 | no date shown | B-06 |
| M6E | IBKR Canada | 435.02 | 350.017 | N/A | 402.52 / 350.017 | no date shown | B-06 |
| M6A | IBKR Canada | 277.31 | 215.052 | N/A | 247.31 / 215.052 | no date shown | B-06 |
| M6B | IBKR Canada | 258.874 | 201.738 | N/A | 231.999 / 201.738 | no date shown | B-06 |
| MCD | IBKR Canada | 136.283 | 118.507 | N/A | 145.783 / 118.507 | no date shown | B-06 |
| MJY | IBKR Canada | 340.775 | 280.022 | N/A | 322.025 / 280.022 | no date shown | B-06 |
| MSF | IBKR Canada | 586.285 | 473.40 | N/A | 544.41 / 473.40 | no date shown | B-06 |
| 2YY | IBKR Canada | 918.619 | 798.80 | N/A | 918.619 / 798.80 | no date shown | B-06 |
| 5YY | IBKR Canada | 825.075 | 717.456 | N/A | 825.075 / 717.456 | no date shown | B-06 |
| 10Y | IBKR Canada | 685.804 | 577.968 | N/A | 664.804 / 577.968 | no date shown | B-06 |
| 30Y | IBKR Canada | 728.613 | 624.881 | N/A | 718.613 / 624.881 | no date shown | B-06 |
| Micro Henry Hub (MHNG, class MNG) | IBKR Canada | 661.992 | 553.037 | N/A | 635.993 / 553.037 | no date shown | B-06 |
| MZC | IBKR Canada | 206.028 | 179.155 | N/A | 232.278 / 179.155 | no date shown | B-06 |
| MZS | IBKR Canada | 443.93 | 386.026 | N/A | 466.43 / 386.026 | no date shown | B-06 |
| MZW | IBKR Canada | 352.215 | 305.187 | N/A | 350.965 / 305.187 | no date shown | B-06 |
| MZL | IBKR Canada | 547.965 | 410.75 | N/A | 472.362 / 410.75 | no date shown | B-06 |
| MZM | IBKR Canada | 363.208 | 315.833 | N/A | 400.209 / 315.833 | no date shown | B-06 |
| NG | IBKR Canada | 6,619.92 | 5,530.36 | N/A | 6,359.92 / 5,530.36 | no date shown | B-06 |
| ZN | IBKR Canada | 2,156.27 | 1,875.02 | N/A | 2,280.99 / 1,875.02 | no date shown | B-06 |
| ZF | IBKR Canada | 1,437.50 | 1,250.00 | N/A | 1,554.43 / 1,250.00 | no date shown | B-06 |
| ZT | IBKR Canada | 1,380.04 | 1,200.04 | N/A | 1,458.25 / 1,200.04 | no date shown | B-06 |

Second brokers. These are public pages of brokers that are UNCLEAR for BC, so read them as reference
only. AMP shows one overnight figure, headed "*Maintenance", with the note "The CFTC, CME, and NFA
classify all retail traders as a "Heightened Risk Profile," mandating a 10% higher exchange margin
requirement than the rates published on the CME website." [B-20]. AMP's column is therefore the amount
needed to hold overnight, and no separate initial figure is published. Ironbeam shows "Overnight Margin"
and "Day Margin"; overnight values "fluctuate daily" [B-34]. Neither page shows a date. Some Ironbeam
values (MCL 416, MET 110) are far below IBKR's and AMP's and may be stale.

| Contract | AMP "*Maintenance" (overnight) / Day | Ironbeam Overnight / Day |
|---|---|---|
| MES | 2,881.00 / 40.00 | 2,307 / 50 |
| MNQ | 4,762.00 / 100.00 | 3,542 / 100 |
| M2K | 1,237.00 / 50.00 | 996 / 50 |
| MYM | 1,698.00 / 50.00 | 1,505 / 50 |
| MCL | 948.00 / 237.00 | 416 / 200 |
| MGC | 2,426.00 / 606.50 | 2,640 / 100 |
| SIL | 7,129.00 / 7,129.00 | 7,150 / 400 |
| MHG | 1,320.00 / 330.00 | 1,100 / 50 |
| MBT | not on page | 2,387 / 50 |
| MET | not on page | 110 / 50 |
| M6E | 231.00 / 57.75 | 297 / 50 |
| M6A | 193.00 / 48.25 | 209 / 40 |
| M6B | 187.00 / 46.75 | 220 / 50 |
| MCD | 88.00 / 22.00 | 110 / 50 |
| MJY | 308.00 / 308.00 | 308 / 50 |
| MSF | 396.00 / 396.00 | 495 / 50 |
| 2YY | 363.00 / 90.75 | 363 / 50 |
| 5YY | 352.00 / 88.00 | 341 / 50 |
| 10Y | 352.00 / 88.00 | 330 / 50 |
| 30Y | 297.00 / 74.25 | 297 / 50 |
| Micro Henry Hub (MNG) | 326.00 / 326.00 | 452 / 50 |
| MZC / MZW / MZS | 116.00 / 34.80; 226.00 / 67.80; 253.00 / 75.90 | not on page |
| NG | 3,234.00 / 3,234.00 | 4,494 / 1000 |
| ZN | 2,062.00 / 515.50 | 2,063 / 200 |
| ZF | 1,375.00 / 343.75 | 1,430 / 150 |
| ZT | 1,320.00 / 330.00 | 1,320 / 75 |

(AMP source B-20; Ironbeam source B-34. AMP's page prints "$187 .00" for M6B and "$2,062 .00" for ZN with
a stray space; the values are transcribed without it.)

## 3. Classification per broker

- IBKR Canada: PERMITTED. CIRO dealer for Canadian residents with US futures permission [B-02], [B-06],
  [B-10]; API with futures order entry and no API minimum commission over the Internet [B-08], [B-09],
  [B-14]; overnight margins published [B-06]. Open point: API terms in the client agreement are
  UNSOURCED.
- Wealthsimple: HUMAN-IN-THE-LOOP ONLY. Futures are offered [B-41] but no API was found, and the terms
  forbid scraping, reverse engineering and circumventing "rate limits" [B-43]. BC eligibility for
  futures specifically is UNSOURCED.
- AMP Futures: UNCLEAR. BC accepted only "at the discretion of a senior manager" [B-18]; BCSC exemption
  pattern [B-15] to [B-17].
- NinjaTrader Brokerage: NOT PERMITTED [B-25].
- Tradovate: NOT PERMITTED [B-26].
- Optimus Futures: UNCLEAR [B-29], [B-31] (Non-Solicited basis; BC statement from 2019).
- Ironbeam: UNCLEAR [B-32], [B-33].
- EdgeClear: UNCLEAR (no broker-side statement) [B-37].
- TradeStation: UNCLEAR (no broker-side statement) [B-38].
- GFF Brokers: UNCLEAR [B-51].
- Jitneytrade: UNCLEAR (site unreachable; CIRO dealer per [B-52]).
- Questrade: NOT PERMITTED (no futures) [B-40].
- TD Direct Investing: NOT PERMITTED (no futures) [B-45], [B-46].
- RBC Direct Investing: NOT PERMITTED [B-44].
- BMO InvestorLine: NOT PERMITTED [B-47].
- CIBC Investor's Edge: NOT PERMITTED (no futures in product list) [B-48].
- National Bank Direct Brokerage: NOT PERMITTED (indirect) [B-49].
- Qtrade: NOT PERMITTED (no futures in product list) [B-50].

## 4. Source list

All fetched 2026-10-03 (UTC). Files are in `reports/stage_e13_briefs/pages/BrokerVenues/`; the fetch id
links each source to its sha256 in `fetch_log.md`.

| key | URL | fetch id / file | page date | page type | verbatim quote |
|---|---|---|---|---|---|
| B-01 | https://www.interactivebrokers.ca/en/pricing/commissions-futures.php | F001 ibkrca_commissions_futures.html | no date shown | broker pricing | "Spot-Quoted Futures, E-Nano Futures, E-micro Futures and Futures Options (MES, MNQ, M2K, VOLQ, MYM, 2YY, 5YY, 10Y, 30Y, MCL, MRB, MGC, MWN, MTN, SIL, VXM, MHNG, ...) ... ≤ 1,000 \| USD 0.25 /contract"; "All fees are charged in the currency of the traded product." |
| B-02 | https://www.interactivebrokers.ca/en/accounts/fees/CME.php | F006 ibkrca_fees_CME.html | no date shown | broker fee schedule | "Micro E-Mini Futures Products MES, MNQ, M2K, VOLQ \| USD \| 0.35"; "E-micro Forex Futures M6A, M6B, M6E, ... MCD, MJY, MSF ... \| USD \| 0.24"; "Non-Members & IIP \| All Products \| USD \| 0.01"; "Interactive Brokers Canada Inc. is a member of the Canadian Investment Regulatory Organization (CIRO)" |
| B-03 | https://www.interactivebrokers.ca/en/accounts/fees/CBOT.php | F007 ibkrca_fees_CBOT.html | no date shown | broker fee schedule | "Micro E-Mini Futures \| MYM \| USD 0.35"; "Micro Treasury Futures \| 2YY, 5YY, 10Y, 30Y, MWN, MTN \| USD 0.30"; "U.S. Treasury Futures \| ZN, TN \| USD 0.80"; "ZF \| USD 0.65"; "ZT \| USD 0.65"; "Micro Ags-Electronic Futures \| MZC,MZS,MZW,MZL,MZM \| USD 0.50" (first column = Tier I Non-Members) |
| B-04 | https://www.interactivebrokers.ca/en/accounts/fees/NYMEX.php | F008 ibkrca_fees_NYMEX.html | no date shown | broker fee schedule | "MCL \| USD 0.50"; "MHNG \| USD 0.60"; "NG \| USD 1.60" (Tier I column) |
| B-05 | https://www.interactivebrokers.ca/en/accounts/fees/COMEX.php | F009 ibkrca_fees_COMEX.html | no date shown | broker fee schedule | "MGC \| USD 0.70 \| USD 0.20"; "MHG \| USD 0.70 \| USD 0.30" (Non-Member, Member) |
| B-06 | https://www.interactivebrokers.ca/en/trading/margin-futures-fops.php?hm=ca&ex=us&rgt=0&rsk=1&pm=0&rst=101004100808 | F010 ibkrca_margin_fut_ca_us.html | no date shown | broker margin page | "For residents of Canada trading futures and FOPs: You are subjected to margin requirements."; "CME \| MES \| MICRO E-MINI S&P 500 STOCK PRICE INDEX \| MES \| 2593.185 \| 1826.23 \| 3704.55 \| 2608.90 \| USD"; "Each day at 'Intraday End Time' the futures contract will revert back to the full overnight margin requirement" |
| B-07 | https://www.interactivebrokers.ca/en/pricing/market-data-pricing.php | F003 ibkrca_market_data.html | no date shown | broker pricing | "US Securities Snapshot and Futures Value Bundle \| USD 10.00 \| USD 30.00" (fee, commission waiver); "Includes top of book quotes for CBOT, CME, COMEX, and NYMEX"; "CME Real-Time (L1) ... non-pro USD 1.55" |
| B-08 | https://www.interactivebrokers.ca/en/index.php?f=4969 | F004 ibkrca_minimums.html | no date shown | broker fees page | "Account Minimums \| USD 0.00 \| Inactivity Fees \| USD 0.00"; "Gateway (Internet) \| Trader Workstation and TWS API \| REST API \| FIX CTCI \| USD 0.00 per month minimum commission \| USD 0.00 per month minimum commission \| USD 1,500.00 per month minimum commission for the first FIX session" |
| B-09 | https://www.interactivebrokers.ca/en/trading/ib-api.php | F013 ibkrca_ib_api.html | no date shown | broker product page | "Automate algorithmic trading strategies, advanced programmatic investing or trading systems."; "Programmatically place orders including advanced order types and algos" |
| B-10 | https://www.interactivebrokers.ca/en/accounts/trading-and-market-data.php | F015 ibkrca_trading_and_market_data.html | no date shown | broker permissions page | permissions table "Futures ... Canada ... United States"; "Interactive Brokers Canada Inc. is a member of the Canadian Investment Regulatory Organization (CIRO)" |
| B-11 | https://www.interactivebrokers.ca/en/accounts/rsp_tfsa_information.php | F014 ibkrca_rsp_tfsa.html | no date shown | broker account rules | "Margin trading is not permitted in a RRSP/SRRSP."; TFSA "No margin trading." (qualified-investment lists contain no futures) |
| B-12 | https://www.interactivebrokers.ca/en/accounts/account-guide.php | F095 ibkrca_account_guide.html | no date shown | broker account guide | "Margin \| Cash, Reg T and Portfolio Margin are available." |
| B-13 | https://www.interactivebrokers.ca/html/retailAccount/stockMarginReq.html | F011 ibkrca_stockMarginReq.html | no date shown | broker margin rule | "All stocks bought or sold on margin require a minimum of $2,000 in equity." |
| B-14 | https://interactivebrokers.github.io/tws-api/basic_contracts.html | F019 ibkr_twsapi_basic_contracts.html | no date shown | API docs | "A regular futures contract is commonly defined using an expiry and the symbol field"; `contract.SecType = "FUT"` |
| B-15 | https://www.bcsc.bc.ca/documents/view/S0SES1SFS1S0S6S3S6S4S7S5S7S2S7SBS6S4S7SAS7S7S6SDS7S4S7SBS6SES6S0S7S2S0S1 | F021 bcsc_doc1.pdf | December 20, 2024 | regulator decision (2024 BCSECCOM 523, RBC Capital Markets, LLC) | "Exemption from s. 34(a) requirement to be registered as a dealer to trade exchange contracts ... the person will only trade exchange contracts with sophisticated investors."; "(o) an individual that beneficially owns financial assets ... of at least $5 000 000" |
| B-16 | https://www.bcsc.bc.ca/documents/view/S0SES1SFS1S0S6S3S6S4S7S5S7S2S7SBS6S4S7SAS7S7S6SDS7S4S7SBS6SES6S0S7SAS0S1 | F022 bcsc_doc2.pdf | July 31, 2025 | regulator decision (2025 BCSECCOM 346, StoneX Financial Ltd.) | "the person will only trade exchange contracts with sophisticated investors." |
| B-17 | https://www.bcsc.bc.ca/documents/view/S0SES1SFS1S0S6S3S6S4S7S5S7S2S7SBS6S4S7SAS7S7S6SDS7S4S7SBS6SES6S0S7S4S0S1 | F023 bcsc_doc3.pdf | April 3, 2025 | regulator decision (2025 BCSECCOM 141, Duneland Commodities Inc.) | same headnote as B-15 |
| B-18 | https://web.archive.org/web/20250911092608/https://faq.ampfutures.com/hc/en-us/articles/10797726829463-Restricted-Countries-List | F031 amp_restricted_countries_wb20250911.html | Wayback capture 2025-09-11 | broker help centre (archived) | "Only 3 provinces in Canada are allowed: Alberta, Ontario and Quebec. Additionally, British Columbia accounts may be allowed at the discretion of a senior manager." |
| B-19 | https://web.archive.org/web/20250812000009/https://faq.ampfutures.com/hc/en-us/articles/33480677897623-Can-I-open-an-AMP-account-if-I-live-outside-the-United-States | F032 amp_outside_us_wb20250812.html | Wayback capture 2025-08-12 | broker help centre (archived) | "Yes, you can open an AMP account even if you live outside the United States, but there are a few important points to know:" |
| B-20 | https://www.ampfutures.com/trading-info/margins | F027 amp_margins.html | no date shown | broker margin page | "Maintenance Margin is set by the exchange. This is the amount required to carry a contract past the daily close."; "Micro E-mini S&P 500 \| MES \| MES \| CME \| $2,881.00 \| $40.00" |
| B-21 | https://www.ampfutures.com/trading-info/exchange-data-fees | F034 amp_exchange_data_fees.html | "Prices effective June 1, 2026" | broker fees | "CME Bundle - ALL CME Markets (Level 1) Top of Book \| $15.00"; "CME/Globex (Level 1) Top of Book \| $5.00" |
| B-22 | https://www.ampfutures.com/trading-platform/rithmic-r-api | F038 amp_rithmic_api.html | no date shown | broker platform page | "The total FLAT monthly technology cost to use the Rithmic API is $125 ($100 API fee + $25 User/Trader ID)."; "For LIVE trading, a Rithmic trade routing fee of $0.10 per contract filled will also apply." |
| B-23 | https://www.ampfutures.com/news/cme-e-micro-indices-launched-ready-for-live-trading | F037 amp_news_micro_launch.html | 2019 (launch "May 5, 2019") | broker news | "Total per Side $0.42"; "AMP Account Minimum to get started is only $100." |
| B-24 | https://www.ampfutures.com/why-amp/commission-quote-match | F028 amp_commissions.html | no date shown | broker pricing | "We will MATCH or BEAT any Written Commission Quote!*" (no rate table) |
| B-25 | https://vendor-support.ninjatrader.com/s/article/How-Can-I-Open-a-NinjaTrader-Account-in-Canada?language=en_US | F047 nt_canada_scrapling.md | Apr 16, 2025 | broker help article | "Canadian law restricts NinjaTrader from opening accounts for residents of Canada that are outside of the province of Ontario. This includes all other provinces: Quebec, Alberta, Manitoba, British Columbia, ..." |
| B-26 | https://vendor-support.ninjatrader.com/s/article/Opening-a-Tradovate-Account-in-Canada?language=en_US | F048 tradovate_canada_scrapling.md | Nov 19, 2024 | broker help article | "Canadian residents living in the province of Ontario are able to open an account with Tradovate."; "If you are in Canada, but outside of Ontario, you are still able to use Tradovate in Simulated Mode." |
| B-27 | https://partner.ninjatrader.com/connect/resources/legal/ninja-trader-api-license-agreement | F045 nt_api_license.html | no date shown | API licence | "access and use the API solely for the purpose of connecting Your order entry and/or trading program(s) software to Ninj[aTrader]" |
| B-28 | https://developer.ninjatrader.com/ | F046 nt_developer.html | no date shown | developer page | "Build, test, and deploy automated trading strategies" |
| B-29 | https://support.optimusfutures.com/do-you-allow-canadian-futures-traders-to-open-accounts | F051 optimus_canadian.html | no date shown (copyright 2025) | broker help article | "We accept all Non-Solicited Self-Directed Canadian futures traders when you Open an Optimus Futures account that is cleared through Phillip Capital and Ironbeam." |
| B-30 | https://support.optimusfutures.com/international-futures-trading | F049 optimus_international.html | no date shown | broker help article | "Yes, Optimus Futures allows and supports foreign clients trading futures from outside the United States. We currently have account holders residing in many different countries, including: Canada" |
| B-31 | https://community.optimusfutures.com/t/futures-broker-for-british-columbia-residents/3157 | F050 optimus_community_bc.html | posts 2019-11-19 to 2020-03-20 | broker staff forum post | "If you are currently living in BC, Canada, we can accept you as a client with Ironbeam." |
| B-32 | https://www.ironbeam.com/?p=4310 | F053 ironbeam_p4310.html | no date shown | broker FAQ | "Yes, we open accounts for people located outside the United States and accept accounts from many countries. To confirm whether your country is supported, please send a message to [email protected]" |
| B-33 | https://www.ironbeam.com/how-to-open-a-futures-trading-account/ | F052 ironbeam_open_account.html | no date shown | broker page | "Ironbeam has no account minimum."; "If you are outside the United States and want to confirm your country of residence is eligible, reach out to [email protected] before applying." |
| B-34 | https://www.ironbeam.com/margins | F054 ironbeam_margins.html | no date shown | broker margin page | "Exchange/overnight margins fluctuate daily"; "Micro E-Mini S&P 500 \| MES \| $50 \| $2,307" |
| B-35 | https://www.ironbeam.com/api/ | F055 ironbeam_api.html | no date shown | broker API page | "Easy Integration via REST"; "Send orders to the exchange directly from your API connection" |
| B-36 | https://www.ironbeam.com/pricing/ | F056 ironbeam_pricing.html | no date shown | broker pricing | "This content is password-protected." |
| B-37 | https://edgeclear.com/technology/ (also /legal-notices/, home) | F064, F063, F059 | no date shown | broker pages | "Automated Trading Solutions"; "Unlock the potential of algorithmic trading and embrace the power of automation with EdgeQX." (no Canada statement on any fetched page) |
| B-38 | https://www.tradestation.com/faqs/ | F065 tradestation_faqs.html | no date shown | broker FAQ | "For international clients, a valid passport and address verification dated within the last 60 days are required." |
| B-39 | https://www.tradestation.com/platforms-and-tools/trading-api/ | F067 tradestation_api.html | no date shown | broker API page | "Multi-asset brokerage API: equities, futures, and options with self-clearing and direct-market-access services – all from a single API key" |
| B-40 | https://invest.questrade.com/self-directed-investing | F089 questrade_self_directed.html | no date shown | broker product page | "More than just Stocks & ETFs. Trade options, precious metals, and IPOs on one powerful platform." |
| B-41 | https://www.wealthsimple.com/en-ca/trade/futures | F074 wealthsimple_trade_futures.html (DO_NOT_COMMIT) | no date shown (cites "as of June 12, 2026") | broker product page | "It's $1 USD per contract, with $0 platform fees and $0 market data fees, plus applicable exchange and regulatory fees. These additional exchange and regulatory fees (for example, $0.35 and $0.02, respectively, for the micro S&P 500)"; "Trade everything from global indices to commodities in micro, mini, and standard contract sizes."; "Wealthsimple supports market, limit, and stop-loss orders for futures contracts." |
| B-42 | https://www.wealthsimple.com/en-ca/learn/how-to-trade-futures | F072 wealthsimple_learn_futures.html (DO_NOT_COMMIT) | Updated September 15, 2026 | broker education | "Futures are not permitted in Tax-Free Savings Accounts (TFSAs) or Registered Retirement Savings Plans (RRSPs). You must use a non-registered account." |
| B-43 | https://www.wealthsimple.com/en-ca/legal/terms | F073 wealthsimple_terms.html (DO_NOT_COMMIT) | "Effective immediately for new clients and September 27, 2026 for existing clients" | broker terms | "copy, scrape, crawl, or data-mine the Platform or Content in any form or by any method;"; "reverse engineer, decompile, or disassemble the Platform"; "disable, circumvent, or defeat any security features ... including without limitation, any rate limits" |
| B-44 | https://www.rbcdirectinvesting.com/pdf/corpoptionsE.pdf | F077 rbcdi_risk_disclosure_futures_options.pdf | (c) 2024 | broker agreement form | "30. ACCOUNT APPROVAL ... The Customer may NOT write uncovered options or covered put options; engage in spreads combinations or straddles; write options against convertible securities; nor buy or sell futures." |
| B-45 | https://www.td.com/ca/en/investing/direct-investing/trading/active-trader | F079 td_active_trader.html | no date shown | broker page | "Futures \| CME Futures (15 Min Delayed)" (market-data package row) |
| B-46 | https://www.td.com/ca/document/PDF/forms/521778.pdf | F081 td_commission_schedule.pdf | no date shown | broker commission schedule | contents: "Canadian Equities ... U.S. Equities ... Canadian and U.S. Options ... Gold and Silver ... Fixed Income Investments ... Mutual Funds" (no futures entry) |
| B-47 | https://www.bmoinvestorline.com/selfDirected/pdfs/AuthorizedTradingAgent.pdf | F083 bmo_il_authorized_trading_agent.pdf | no date shown | broker form | "BMO InvestorLine Inc. is not registered to trade in futures." |
| B-48 | https://www.investorsedge.cibc.com/en/pricing.html | F085 cibc_ie_pricing.html | rates "Effective September 17, 2026" | broker pricing | "Investment choices \| Stocks \| Exchanged Traded Funds (ETFs) \| Options \| Canadian Depositary Receipts (CDRs) \| Mutual Funds \| Guaranteed Investment Certificates (GICs) \| Fixed Income \| Precious Metals \| Initial Public Offerings (IPOs) \| Structured Notes" |
| B-49 | https://nbdb.ca/help/transactions/transfers/products-transferred.html | F086 nbdb_products_not_transferred.html | (c) 2026 | broker help | "Private investments \| Futures contracts \| Some Guaranteed Investment Certificates (GICs)" (list of products that cannot be transferred to NBDB) |
| B-50 | https://www.qtrade.ca/en/investor/trading/investment-choices.html | F088 qtrade_investment_choices.html | no date shown | broker product page | "Qtrade makes it easy to build a well-diversified portfolio, with access to a wide array of stocks, ETFs, mutual funds, bonds, options and more." |
| B-51 | https://www.gffbrokers.com/resources/faqs | F091 gff_faqs.html | no date shown | broker FAQ | "Country-specific options depend on the clearing firm's regulatory coverage - reach out and our team will match you with the right firm for your jurisdiction." |
| B-52 | https://www.m-x.ca/f_circulaires_en/057-26_en.pdf | F093 mx_circular_057-26_jitneytrade.pdf | May 4, 2026 | exchange circular | "Jitneytrade Inc. is registered as an Investment Dealer with the Canadian Investment Regulatory Organization (CIRO) and the Canadian Security Administrators in most provinces and territories." |
| B-53 | https://www.questrade.com/pricing/self-directed-commissions-plans-fees/forex-cfd | F068 questrade_cfd.html | no date shown | broker pricing | Questrade's FX and CFD pricing page (CFDs, not exchange futures). Supporting only |

## 5. Gaps and failures

- IBKR Canada: (a) no IBKR page names British Columbia. Eligibility rests on IBKR Canada being the CIRO
  entity for Canadian residents with a Canada-resident margin schedule. (b) No futures-specific minimum
  equity was found. (c) The client agreement and any API automation clauses were not retrieved because
  the agreements page is JavaScript-rendered (F017). (d) The margin page shows no date. (e) The SIL
  exchange fee is not on the COMEX fee page. (f) The numbering of market-data footnote 14 is ambiguous
  (an empty list item), so the CME L1 USD 1.55 waiver rule is not stated here.
- Wealthsimple: the help-centre futures article (contract list, eligibility, margins) returned 403 to
  curl and WebFetch. Its terms forbid scraping, so Scrapling was not used; no Wayback capture exists. BC
  eligibility, the contract list, multi-day holds and margins are UNSOURCED. All wealthsimple.com files
  are listed in DO_NOT_COMMIT.txt.
- AMP: the live help centre returns 403; Wayback captures from 2025 were used (their dates are the page
  dates). No terms of use were found for ampfutures.com, and Scrapling was not used there. Current
  commission rates are not published (quote form only). The micro all-in figure is from 2019 and stale.
- NinjaTrader/Tradovate articles: curl returned a JavaScript shell and WebFetch returned "CSS Error".
  Before using Scrapling I looked for website terms of use (ninjatrader.com /terms-of-use/, /legal/,
  /terms/ and similar all 404; the disclosures page lists none; vendor-support robots.txt "Allow: /").
  None were found, so `scrapling extract fetch` was used (F047, F048), as recorded in the log.
- Ironbeam: the pricing page is password-protected, so commissions are UNSOURCED. BC is not confirmed on
  Ironbeam's own pages.
- EdgeClear, TradeStation, GFF: no broker-side statement on Canadian or BC eligibility was found.
  Third-party snippets (forums, review sites) were not used as sources.
- Jitneytrade: jitneytrade.com did not resolve (curl http 000, WebFetch ENOTFOUND).
- bmo.com refused curl (http 000), so the BMO FAQ page was not saved. The BMO InvestorLine PDF form was
  used instead.
- Absence evidence: CIBC, Qtrade, Questrade and TD are classed from product lists or commission
  schedules that omit futures, not from an explicit "no futures" statement. RBC and BMO have explicit
  statements. NBDB's evidence is indirect (futures cannot be transferred in).
- Not covered: Disnat (Desjardins), Canaccord Direct, Friedberg Direct (FX/CFD dealer) and any other
  CIRO dealer not named in the brief.
- Counts: 81 evidence files saved (plus .txt extracts), 28 of 100 WebSearch calls, 0 Firecrawl calls,
  2 Scrapling fetches, 4 WebFetch attempts (all failed). Failed fetches: 15 rows marked FAILED in the
  log (403s, 404s, DNS, WebFetch shells). Error pages were deleted and their log rows annotated.
