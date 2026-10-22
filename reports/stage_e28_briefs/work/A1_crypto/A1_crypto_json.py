import json
P='pages/A1_crypto/'
def F(value,unit=None,window=None,src=None,quote=None,note=None):
    return {"value":value,"unit":unit,"window":window,"source_file":(P+src if src and not src.startswith('work/') else src),"quote":quote,"note":note}
UNK=lambda searched,unit=None,window=None: F(None,unit,window,None,None,"unknown; searched: "+searched)
HOURS=F("Sun-Fri 17:00-16:00 CT, 60-minute daily break from 16:00 CT; closed Fri 16:00 CT to Sun 17:00 CT (until 24/7 from 2026-05-29)",None,"2021 filings; 24/7 from 2026-05-29","cftc_ptc112921cmedcm002.txt","Sunday - Friday 5:00 p.m. - 4:00 p.m. Central Time (CT) (6:00 p.m. - 5:00 p.m. Eastern Time (ET) with a 60-minute break each day beginning at 4:00 p.m. CT (5:00 p.m. ET)","Same hours in the ETH filing cftc_ptc012621cmedcm001.txt line 101; 24/7 change: mm_cme_247_launch.html.txt")
LIM=F("10% dynamic variant over rolling 60-minute look-back, 2-minute halt; no hard daily limit from 2023-01-06 (30% hard limit removed)",None,"from trade date 2023-01-06","cftc_ptc123022cmedcm002.txt","The Contracts will continue to be subject to Dynamic Price Fluctuation Limits with a 10% dynamic variant pursuant to Rule 589.D. (“Dynamic Price Fluctuation Limits”).","Same filing: 'to remove the existing price limit of 30% ... effective on trade date Friday, January 6, 2023'. 2019-03-10..2023-01-05: dynamic halts plus 30% hard limit (cftc_ptc022119cmedcm001.txt).")
HITS=F(None,"days per year","2019-2024",None,None,"unknown; no CME or regulator list of crypto halt days found. News pointer only (not evidence): ptr_forklog_cme_halt_2020.html.txt reports a BTC halt at the 2020-12-28 open after a ~12% gap. Searched: WebSearch for CME bitcoin futures halts 2020-2022; CME filings.")
REL=F(0,"scheduled product-specific high-impact releases per week","2019-2026",None,None,"none found in CME filings, FAQ or product pages read; CME CF reference rates are daily fixings, not news. Absence, not a sourced statement.")
WKND=F(True,None,"2017-12-18..2026-05-28 (incl. pilot window 2023-11..2024-02)","cftc_ptc042621cmedcm001.txt","on its website at 4:00 p.m. London time 365 days per year","BRR published every day while Globex closed weekends (F1). 24/7 Globex trading began 2026-05-29 (mm_cme_247_launch.html; datePublished 2026-06-01). 17-417 lines 134-135: reference price 'may be adjusted to incorporate BRR changes on non-trading days'.")
JUMP=UNK("OpenAlex for bitcoin jump studies; only a spot study (Scaillet et al. 2018, Mt. Gox 2011-2013: 124 jump days of 888, lit_scaillet2018_btc_jumps.txt) found; no CME-product study; days with |r|>4 SD not computed (A0 owns bar data)","days per year with |r| > 4 daily SD","2019-2024")
BASIS=UNK("BIS WP 1087 (fetch returned HTML, not PDF); CME filings give settlement mechanics only","basis to spot")
SPREAD=UNK("CME Bitcoin futures liquidity report page (values load by script), CME Liquidity Tool (login), Quantitative Brokers 2021-06a (gated), WebSearch x2","ticks","main and overnight session")
DEPTH=UNK("same as spread","contracts at best bid/ask")
QV=UNK("same as spread","contracts per minute / minutes")
HFT=UNK("CFTC OCE automated-trading series 2015, 2017, 2019 and 2019 staff report: no crypto product tabulated (latest sample ends 2018-10-31); WebSearch for CFTC crypto automated share","share of volume")
RETAIL=lambda note: F(None,"share of volume",None,None,None,"no number found; searched CME releases, FIA, CFTC research, WebSearch. Qualitative: "+note)
def tff(w1,w2):
    return {"W1":w1,"W2":w2}
def tf(code,mean_oi,med_oi,d,a,l,o,n,nr,tr,window):
    return F({"cftc_code":code,"mean_OI":mean_oi,"median_OI":med_oi,"dealer":d,"asset_mgr":a,"lev_money":l,"other_rept":o,"nonreportable":n,"nonreportable_range":nr,"mean_traders":tr},"percent of OI (long+short+2*spread)/(2*OI); OI in contracts",window,"work/A1_crypto/A1_crypto_cot_out.txt",None,"computed by work/A1_crypto/A1_crypto_cot.py from CFTC TFF futures-only annual files (pages/A1_crypto/cftc_fut_fin_txt_YYYY.zip). TFF has no commercial-hedger category. Exchange reportable level is 1 contract (F4).")
W1='2022-11-01..2023-10-31 (53 weekly reports)'; W2='2025-10-21..2026-10-13 (52 weekly reports)'
STUD_BTC=[
 {"study":"Aleti and Mizrach 2021, J. Futures Markets 41(2), Bitcoin spot and futures market microstructure","relation":"same product (BTC)","result":"null for order-book predictability (descriptive; CME leads price discovery)","source_file":P+"oa_aleti_mizrach2021.json.abstract.txt","quote":"Spot market median trade sizes are under $1,300 but exceed $18,000 on the CME. Bid‐ask spreads average 0.0298%.","note":"abstract only"},
 {"study":"Akyildirim, Cepni, Corbet, Uddin 2021, Ann. Oper. Res., Forecasting mid-price movement of Bitcoin futures using machine learning","relation":"same product (BTC)","result":"positive (minute-bar mid-price direction ~54% logistic; gross of costs; no order-book inputs)","source_file":P+"lit_akyildirim2021_midprice_btcfut.xml.txt","quote":"the average success rate for both in the sample and out-sample periods is almost always 54% for three different hold-outs","note":"full text, CME BTC 2020-01-02..2020-09-10"},
]
STUD_CLASS=[
 {"study":"Fang et al. 2021, European J. Finance, Ascertaining price formation in cryptocurrency markets with machine learning","relation":"asset class only (spot)","result":"positive (tick-ahead mid-price direction, 78% claimed)","source_file":P+"oa_fang2021_crypto_ml.json.abstract.txt","quote":"achieving a consistent 78% accuracy on the prediction of the mid-price movement on live exchange rate of Bitcoins vs. US dollars","note":"abstract only"},
 {"study":"Scaillet, Treccani, Trevisan 2018, J. Fin. Econometrics, High-Frequency Jump Analysis of the Bitcoin Market","relation":"asset class only (Mt. Gox spot 2011-2013)","result":"positive (OFI predicts jumps)","source_file":P+"lit_scaillet2018_btc_jumps.txt","quote":"The order flow imbalance and the preponderance of aggressive traders, as well as a widening of the bid-ask spread predict them.","note":"full text"},
 {"study":"Cestari et al. 2023, arXiv 2312.16190, Hawkes-based cryptocurrency forecasting via LOB data","relation":"asset class only (USDT/USD spot)","result":"positive (abstract; cost treatment not stated)","source_file":P+"oa_hawkes_crypto_lob_2023.json.abstract.txt","quote":"our strategy surpasses benchmark models in both prediction accuracy and cumulative profit when implemented in a trading environment","note":"abstract only"},
 {"study":"The Quarter-Hour Effect, arXiv 2607.09426 v2 (2026)","relation":"asset class only (Binance perpetuals)","result":"mixed (quarter-hour order imbalance predicts 4-12h returns; much weaker at finer clock-time frequencies)","source_file":P+"lit_arxiv2607.09426_quarter_hour.txt","quote":"opening order imbalance predicts returns over four to twelve hours, with much weaker effects at finer clock-time frequencies","note":"full text saved; abstract lines read"},
 {"study":"Rajendran and Singaravelu 2026, Int. Rev. Econ. Finance, Order-flow toxicity in cryptocurrency perpetual futures","relation":"asset class only (Bybit perpetuals)","result":"positive for adverse-selection detection (not a P&L result)","source_file":P+"oa_ofi_toxicity_perp_2026.json.abstract.txt","quote":"interpret TailScore as a practically relevant adverse-selection risk-ranking signal, not a direct measure of private information or a realised trading strategy","note":"abstract only"},
]
def studies(code):
    if code in ('BTC','MBT'):
        s=[dict(x) for x in STUD_BTC]
        if code=='MBT':
            for x in s: x['relation']='same underlying, full-size version (BTC)'
            s.append({"study":"Pati 2022, Finance Research Letters, Informativeness of CME Micro Bitcoin Futures in Pricing of Bitcoin: Intraday Evidence","relation":"same product (MBT)","result":"unknown (price discovery; title only)","source_file":P+"oa_pati2022_mbt.json","quote":None,"note":"no abstract in OpenAlex [unverified]"})
    else:
        s=[dict(x) for x in STUD_BTC]
        for x in s: x['relation']='close cousin on CME Globex (BTC: same asset class, different underlying)'
    return F(s+STUD_CLASS,None,None,None,None,"No study found testing OFI, queue imbalance, trade-sign predictability or passive-MM profitability on CME BTC, MBT, ETH or MET, and none reporting such patterns absent. Searches: OpenAlex 7 queries, WebSearch 3, arXiv API (timed out).")
out=[]
# MET
out.append({"candidate":"MET",
 "product_name":F("Micro Ether Futures",None,None,"cftc_ptc112921cmedcm002.txt","Contract Title Micro Ether Futures","CME rulebook chapter 347"),
 "code":F("MET",None,None,"cftc_ptc112921cmedcm002.txt","Commodity Code CME Globex/CME ClearPort: MET",None),
 "contract_size":F(0.1,"ether",None,"cftc_ptc112921cmedcm002.txt","The unit of trading shall be 0.10 ether.",None),
 "tick_size":F(0.50,"USD per ether (index points)","outright","cftc_ptc112921cmedcm002.txt","The minimum price increment shall be 0.50 index points, equal to $0.05 per contract",None),
 "tick_value":F(0.05,"USD per contract","outright","cftc_ptc112921cmedcm002.txt","Outright: 0.50 index points = $0.05 per contract",None),
 "launch_trade_date":F("2021-12-06",None,None,"cftc_ptc112921cmedcm002.txt","effective on Sunday, December 5, 2021, for trade date Monday, December 6, 2021",None),
 "globex_60_dates_in_pilot_window":F(True,None,"2023-11-01..2024-02-29","cftc_ptc112921cmedcm002.txt","for trade date Monday, December 6, 2021","launched before 2023-11 and continuously listed (TFF weekly reports in W1 and W2; Oct 2023 ADV 10.4K; MM program active to 2025-01-31). No market data read."),
 "matching_algorithm":F("FIFO",None,"outright","cftc_ptc112921cmedcm002.txt","CME Globex F: First In First Out (FIFO) Matching Algorithm","also cme_met_faq_2021.html.txt"),
 "trading_hours":HOURS,"price_limits":LIM,"limit_hit_days_2019_2024":HITS,
 "adv_latest":F({"2025_calendar":144000,"2025_09":182000,"2025_Q3":209000,"2025_10":222000},"contracts per day","calendar 2025 and single months 2025","srp_cme_2025_crypto_adv.html.txt","Micro Ether futures led the growth with an ADV of 144,000 contracts","2025 calendar figure is secondary (SRP citing CME 5 Jan 2026); monthly from prn_cme_q3_2025_mondovisione.html.txt and prn_cme_oct_2025_mondovisione.html.txt. Latest 12 months (Oct 2025..Sep 2026) not found."),
 "adv_2022_11_2023_10":F({"2023_10":10400},"contracts per day","Oct 2023 only","cme_crypto_review_2023-10.html.txt","October ADV was 10.4K (+150% vs. Sep), and OI averaged 19.3K (+59% vs. Sep).","12-month figure not found; A0 owns bar-based ADV."),
 "open_interest":F({"W1_mean_TFF":18082,"W2_mean_TFF":109408,"W2_median_TFF":62865,"2023_10_avg_CME":19300},"contracts",W1+"; "+W2,"work/A1_crypto/A1_crypto_cot_out.txt",None,"TFF computed; CME Oct 2023 from cme_crypto_review_2023-10.html.txt"),
 "tff_positions":tff(tf("146022",18082,16492,10.6,5.1,38.3,42.6,3.3,"1.7-5.7",93.5,W1),tf("146022",109408,62865,3.1,5.3,67.6,21.8,2.2,"0.7-4.3",268.2,W2)),
 "reportable_level":F(1,"contracts",None,"cftc_ptc112921cmedcm002.txt","The reportable level shall be 1 Micro Ether futures (MET) contract.",None),
 "retail_share":RETAIL("CME 2021 launch release targets 'institutions to sophisticated, active, individual traders' (prn_cme_met_launch_2021_mondovisione.html.txt)."),
 "commercial_hedger_share":F(None,None,None,None,None,"TFF has no commercial-hedger category; see tff_positions (Dealer/Intermediary is the sell side)"),
 "market_maker_program":F("Micro Ether Futures Market Maker Program 2021-12-06..2025-01-31 (covers pilot window); Micro Cryptocurrency Futures MM Program from 2025-02-01 to 2027-01-31",None,None,"cftc_rules0715243344.txt","Start date is December 6, 2021. End date is July 31, 2024 January 31, 2025.","later program: cftc_rules07162610502.txt"),
 "hft_automated_share":HFT,"median_spread_ticks":SPREAD,"depth_best_level":DEPTH,"queue_size_and_volume_per_minute":QV,
 "scheduled_releases_per_week":REL,"weekend_gap_exposure":WKND,"jump_frequency":JUMP,"basis_to_spot":BASIS,
 "microstructure_studies":studies('MET')})
# ETH
out.append({"candidate":"ETH",
 "product_name":F("Ether Futures",None,None,"cftc_ptc012621cmedcm001.txt","Initial Listing of the Ether Futures Contract","CME rulebook chapter 349 (Submission 21-005)"),
 "code":F("ETH",None,None,"cftc_ptc123022cmedcm002.txt","Ether Futures ETH 349",None),
 "contract_size":F(50,"ether",None,"cftc_ptc012621cmedcm001.txt","The unit of trading shall be 50 ether.",None),
 "tick_size":F(0.50,"USD per ether (index points)","outright, from trade date 2021-12-06 (0.25 before)","cftc_ptc111621cmedcm001.txt","to increase the minimum price fluctuation limit from 0.25 Index points ($12.50 per contract) to 0.50 Index points ($25.00 per contract)",None),
 "tick_value":F(25.00,"USD per contract","outright, from 2021-12-06","cftc_ptc111621cmedcm001.txt","0.50 Index points ($25.00 per contract)",None),
 "launch_trade_date":F("2021-02-08",None,None,"cftc_ptc012621cmedcm001.txt","effective on Sunday, February 7, 2021, for trade date Monday, February 8, 2021",None),
 "globex_60_dates_in_pilot_window":F(True,None,"2023-11-01..2024-02-29","cftc_ptc012621cmedcm001.txt","for trade date Monday, February 8, 2021","launched before 2023-11, continuously listed (TFF weekly in W1 and W2; Oct 2023 ADV 5.5K). No market data read."),
 "matching_algorithm":F("FIFO",None,"outright","cftc_ptc012621cmedcm001.txt","CME Globex Matching F: First In First Out (FIFO) Algorithm",None),
 "trading_hours":HOURS,"price_limits":LIM,"limit_hit_days_2019_2024":HITS,
 "adv_latest":F({"2025_10":24000,"2026_04":19000},"contracts per day","single months","cme_pr_2026-05-04_april_adv.html.txt","Ether futures ADV increased 33% to 19,000 contracts","Oct 2025 from prn_cme_oct_2025_mondovisione.html.txt. Q3 2025 'Record Ether futures ADV of 236,000 contracts' (prn_cme_q3_2025_mondovisione.html.txt) likely aggregates Micro Ether [unverified]. Latest 12 months not found."),
 "adv_2022_11_2023_10":F({"2023_10":5500},"contracts per day","Oct 2023 only","cme_crypto_review_2023-10.html.txt","Ether futures October ADV was 5.5K (+40% vs. Sep), and OI averaged 4.7K.","12-month figure not found."),
 "open_interest":F({"W1_mean_TFF":4405,"W2_mean_TFF":32232,"2023_10_avg_CME":4700},"contracts",W1+"; "+W2,"work/A1_crypto/A1_crypto_cot_out.txt",None,None),
 "tff_positions":tff(tf("146021",4405,4433,8.1,10.7,51.2,15.5,14.6,"9.5-20.9",64.8,W1),tf("146021",32232,31377,52.7,10.3,33.2,1.4,2.5,"1.7-6.7",94.3,W2)),
 "reportable_level":F(1,"contracts",None,"cftc_ptc012621cmedcm001.txt","The reportable level shall be 1 contract.",None),
 "retail_share":RETAIL("CME (2021) on ETH: growth in liquidity 'especially among institutional traders' (prn_cme_met_launch_2021_mondovisione.html.txt)."),
 "commercial_hedger_share":F(None,None,None,None,None,"TFF has no commercial-hedger category; see tff_positions"),
 "market_maker_program":F("Ether Futures MM Program 2021-02-08..2021-08-31 (as filed); ETH in Cryptocurrency Futures MM Program scope in the 2026 filing (program start 2018-03-05); scope during pilot window unverified",None,None,"cftc_rules07162610506.txt","Bitcoin Futures (“BTC”), Ether Futures (“ETH”), SOL Futures (“SOL”), and XRP Futures (“XRP”) that are traded on Globex","2021 program: cftc_rule012821cmedcm004.txt 'Start date is February 8, 2021. End date is August 31, 2021.'"),
 "hft_automated_share":HFT,"median_spread_ticks":SPREAD,"depth_best_level":DEPTH,"queue_size_and_volume_per_minute":QV,
 "scheduled_releases_per_week":REL,"weekend_gap_exposure":WKND,"jump_frequency":JUMP,"basis_to_spot":BASIS,
 "microstructure_studies":studies('ETH')})
# MBT
out.append({"candidate":"MBT",
 "product_name":F("Micro Bitcoin Futures",None,None,"cftc_ptc042621cmedcm001.txt","Micro Bitcoin Futures MBT CME 348","CME rulebook chapter 348 (Submission 21-155)"),
 "code":F("MBT",None,None,"cftc_ptc123022cmedcm002.txt","Micro Bitcoin Futures MBT 348",None),
 "contract_size":F(0.1,"bitcoin",None,"cftc_ptc042621cmedcm001.txt","The unit of trading shall be 0.10 bitcoin.",None),
 "tick_size":F(5.00,"USD per bitcoin (index points)","outright","cftc_ptc042621cmedcm001.txt","The minimum price increment shall be 5.00 index points, equal to $0.50 per contract",None),
 "tick_value":F(0.50,"USD per contract","outright","cftc_ptc042621cmedcm001.txt","Outright: 5.00 index points = $0.50 per contract",None),
 "launch_trade_date":F("2021-05-03",None,None,"cftc_ptc042621cmedcm001.txt","CME ClearPort effective on Sunday, May 2, 2021, for trade date Monday, May 3, 2021",None),
 "globex_60_dates_in_pilot_window":F(True,None,"2023-11-01..2024-02-29","cftc_ptc042621cmedcm001.txt","for trade date Monday, May 3, 2021","launched before 2023-11, continuously listed (TFF weekly W1 and W2; Oct 2023 ADV 11.5K). No market data read."),
 "matching_algorithm":F("FIFO",None,"outright","cftc_ptc042621cmedcm001.txt","CME Globex Matching F: First In, First Out (FIFO) Algorithm",None),
 "trading_hours":HOURS,"price_limits":LIM,"limit_hit_days_2019_2024":HITS,
 "adv_latest":F({"2025_calendar":75000,"2025_09":62000,"2025_10":80000},"contracts per day","calendar 2025 and single months","srp_cme_2025_crypto_adv.html.txt","while Micro Bitcoin futures reached 75,000","2025 calendar figure secondary; monthly from prn_cme_q3_2025_mondovisione.html.txt and prn_cme_oct_2025_mondovisione.html.txt. Latest 12 months not found."),
 "adv_2022_11_2023_10":F({"2023_10":11500},"contracts per day","Oct 2023 only","cme_crypto_review_2023-10.html.txt","Micro Bitcoin futures October ADV was 11.5K (+96% MoM), while OI averaged 9.2K (+6% MoM).","12-month figure not found."),
 "open_interest":F({"W1_mean_TFF":10822,"W1_median_TFF":9440,"W2_mean_TFF":29353,"2023_10_avg_CME":9200},"contracts",W1+"; "+W2,"work/A1_crypto/A1_crypto_cot_out.txt",None,None),
 "tff_positions":tff(tf("133742",10822,9440,11.1,5.2,44.9,18.9,19.9,"9.2-31.8",91.6,W1),tf("133742",29353,28631,10.8,3.9,52.5,16.9,15.9,"10.0-23.5",213.5,W2)),
 "reportable_level":F(1,"contracts",None,"cftc_ptc042621cmedcm001.txt","The reportable level shall be 1 Micro Bitcoin Futures (MBT) Contracts.",None),
 "retail_share":RETAIL("FIA MarketVoice 2021 frames MBT as serving rising retail interest (fia_mv_micro_bitcoin_retail_2021.html.txt); Ferko et al. 2023: MBT trader composition differs from BTC (repec_ferko2023.html.txt)."),
 "commercial_hedger_share":F(None,None,None,None,None,"TFF has no commercial-hedger category; see tff_positions"),
 "market_maker_program":F("Micro Bitcoin Futures MM Program from 2021-05-03 (to 2021-10-31 as filed; 2024 modifications per filings-index search summary, unverified); Bitcoin Friday Futures MM Program incl. MBT 2024-09-30..2025-07-31; Micro Cryptocurrency Futures MM Program from 2025-02-01",None,None,"cftc_rule041921cmedcm004.txt","participants must meet certain volume thresholds and quote two-sided markets in the Product at predetermined average bid/ask spreads and minimum quote sizes.","also cftc_rules01092513460.txt, cftc_rules07162610502.txt; coverage during 2023-11..2024-02 not verified from a fetched filing"),
 "hft_automated_share":HFT,"median_spread_ticks":SPREAD,"depth_best_level":DEPTH,"queue_size_and_volume_per_minute":QV,
 "scheduled_releases_per_week":REL,"weekend_gap_exposure":WKND,"jump_frequency":JUMP,"basis_to_spot":BASIS,
 "microstructure_studies":studies('MBT')})
# BTC
out.append({"candidate":"BTC",
 "product_name":F("Bitcoin Futures",None,None,"cme_rulefiling_17-417.txt","self-certifying the initial listing of the Bitcoin Futures Contract","CME rulebook chapter 350"),
 "code":F("BTC",None,None,"cftc_ptc123022cmedcm002.txt","Bitcoin Futures BTC 350",None),
 "contract_size":F(5,"bitcoin",None,"cftc_ptc022119cmedcm001.txt","The unit of trading shall be 5 bitcoin.","chapter 350 text inside CME Submission 19-015"),
 "tick_size":F(5.00,"USD per bitcoin","outright","cftc_ptc022119cmedcm001.txt","The minimum price increment shall be $5.00, equal to $25.00 per contract",None),
 "tick_value":F(25.00,"USD per contract","outright","cftc_ptc022119cmedcm001.txt","equal to $25.00 per contract",None),
 "launch_trade_date":F("2017-12-18",None,None,"cme_rulefiling_17-417.txt","effective on Sunday, December 17, 2017, for trade date of Monday, December 18, 2017.","Wayback raw capture of the CME filing"),
 "globex_60_dates_in_pilot_window":F(True,None,"2023-11-01..2024-02-29","cme_rulefiling_17-417.txt","for trade date of Monday, December 18, 2017.","launched before 2023-11, continuously listed (TFF weekly W1 and W2; Oct 2023 ADV 13K). No market data read."),
 "matching_algorithm":F("FIFO",None,"outright","cme_rulefiling_17-417.txt","CME Globex F: First In First Out (FIFO) Matching Algorithm",None),
 "trading_hours":HOURS,"price_limits":LIM,"limit_hit_days_2019_2024":HITS,
 "adv_latest":UNK("CME 2025-2026 monthly releases (Mondo Visione reposts, Wayback); no BTC per-product ADV after Oct 2023 found","contracts per day","latest 12 months"),
 "adv_2022_11_2023_10":F({"2023_10":13000},"contracts per day","Oct 2023 only","cme_crypto_review_2023-10.html.txt","The October ADV for Bitcoin futures was 13K (+35% MoM), while OI averaged a record 17K (+10% MoM).","12-month figure not found; 2021 YTD to Mar 17: 13,934 (cftc_ptc042621cmedcm001.txt)"),
 "open_interest":F({"W1_mean_TFF":15356,"W2_mean_TFF":22539,"2023_10_avg_CME":17000,"record_2023_10_25":20369},"contracts",W1+"; "+W2,"work/A1_crypto/A1_crypto_cot_out.txt",None,"record from cme_crypto_review_2023-10.html.txt"),
 "tff_positions":tff(tf("133741",15356,15385,13.7,28.5,42.6,8.2,7.0,"5.3-8.5",108.5,W1),tf("133741",22539,22192,24.3,19.5,47.1,4.2,4.9,"3.9-6.4",124.1,W2)),
 "reportable_level":F(None,"contracts",None,None,None,"BTC reportable level not in fetched text (MBT, ETH, MET are 1 contract)"),
 "retail_share":RETAIL("2021 filing: 'The number of unique accounts that have traded the Bitcoin Futures contract since launch is above 7,700'; 77-110 large open interest holders (cftc_ptc042621cmedcm001.txt)."),
 "commercial_hedger_share":F(None,None,None,None,None,"TFF has no commercial-hedger category; see tff_positions"),
 "market_maker_program":F("Cryptocurrency Futures Market Maker Program from 2018-03-05 (extended to 2027-01-31; BTC in 2026 scope); 2021: 'A significant number of market makers support the Bitcoin Futures contract.'",None,None,"cftc_rules07162610506.txt","Start date is March 5, 2018. End date is July 31, 2026 January 31, 2027","quote on market makers: cftc_ptc042621cmedcm001.txt"),
 "hft_automated_share":HFT,"median_spread_ticks":SPREAD,"depth_best_level":DEPTH,"queue_size_and_volume_per_minute":QV,
 "scheduled_releases_per_week":REL,"weekend_gap_exposure":WKND,"jump_frequency":JUMP,"basis_to_spot":BASIS,
 "microstructure_studies":studies('BTC')})
json.dump(out,open('/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e28_briefs/A1_crypto.json','w'),indent=1,ensure_ascii=False)
print(len(out),[o['candidate'] for o in out],len(out[0]))
