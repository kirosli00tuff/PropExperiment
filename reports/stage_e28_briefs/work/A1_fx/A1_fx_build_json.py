"""Build reports/stage_e28_briefs/A1_fx.json from the facts in A1_fx.md (A1_fx worker, Stage E.28)."""
import json
OUT = '/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e28_briefs/A1_fx.json'
P = 'reports/stage_e28_briefs/pages/A1_fx/'

def F(value, unit=None, window=None, source_file=None, quote=None, note=None):
    return {"value": value, "unit": unit, "window": window,
            "source_file": (P + source_file) if source_file and not source_file.startswith('reports/') else source_file,
            "quote": quote, "note": note}

# ---------- family-wide facts ----------
HOURS_Q = {
 '6E': ("cme_old_specs_euro-fx.html.txt", "Sunday - Friday 5:00 p.m. - 4:00 p.m. (6:00 p.m. - 5:00 p.m. ET) with a 60-minute break each day beginning at 4:00 p.m. (5:00 p.m. ET)", "Wayback 2021-01-21"),
 'M6E': ("cme_old_specs_e-micro-euro.html.txt", "Sunday - Friday 5:00 p.m. - 4:00 p.m. CT with a 60-minute break each day beginning at 4:00 p.m. CT", "Wayback 2021-04-20"),
 '6A': ("cme_old_specs_australian-dollar.html.txt", "Sunday – Friday 5:00 p.m. – 4:00 p.m. CT (with a 60-minute break each day beginning at 4:00 p.m.CT)", "Wayback 2020-12-02"),
 'M6A': ("cme_old_specs_e-micro-australian-dollar.html.txt", "Monday – Friday: 5:00 p.m. – 4:00 p.m. CT the next day, except on Friday – closes at 4:00 p.m. and reopens Sunday at 5:00 p.m. CT.", "Wayback 2021-04-21"),
}
LIMITS = F("no daily price limit; CME Rule 589 dynamic price fluctuation limits (2-minute halt when trades/bids/offers pass a rolling 60-minute band)",
           None, "6E/6A from trade date 2021-07-12; all CME FX futures from 2022-05-02",
           "cftc_cme_ptc041222_fx_dcb.txt",
           "Upon the effective date, dynamic price fluctuation limits shall apply to all CME FX futures contracts.",
           "Mechanism quote in cftc_cme_ptc062121_fx_dcb.txt l.159-163. Percentage variants are in a Table 'provided under separate cover' (not obtained). Whether micros are 'associated products' of 6E/6A is not stated in the fetched text [unverified].")
LIMIT_HITS = F(None, "days per year", "2019-2024", None, None,
               "Searched: CME Rule 589 filings, CME DCB FAQ and price-limits pages (Wayback 404/timeout). No published count of FX dynamic-halt days found. No daily limit exists to be hit.")
WEEKEND = F("no 7-day underlying documented; OTC spot FX also closes at the weekend", None, None,
            "cme_old_specs_euro-fx.html.txt", "Sunday - Friday 5:00 p.m. - 4:00 p.m.",
            "Spot weekly hours (about Sunday 5 p.m. to Friday 5 p.m. New York) known only from broker/forum pages (pointers, WebSearch-15) [unverified]. No crypto-style weekend trading of the underlying.")
SPOT = F("spot (EBS/Reuters OTC) led price discovery in 2006-era studies; one later study (search snippet) says futures dominate", None, "1996, 2006 (Rosenberg-Traub); 2000s (Cabrera et al.)",
         "rosenberg_traub_frbny_sr262.txt",
         "In particular, we find in our more recent sample that the spot market has the dominant information share.",
         "Cabrera, Wang, Yang (JFM 2009, abstract): 'the spot market is found to consistently lead the price discovery process'. CME 2024: CME has 'over 98% of global volume in EUR/USD futures' (cme_2024_fx_liquidity_speaks_volumes.html.txt l.44). FX Link spread connects OTC spot and futures. BIS 2011: HFT arbitrage 'across the spot and futures prices of the same currency pair'.")
RES_ABSENT = ("No study found testing OFI, queue imbalance, trade-sign predictability or net passive market-making profitability on 6E, M6E, 6A, M6A or E7 "
              "(20 WebSearch calls, 11 OpenAlex queries; arXiv API 503).")

def research(code):
    same = code in ('6E', 'M6E')
    rows = []
    rows.append(F("Haynes and Roberts (CFTC OCE 2015, 2017, 2019): ATS shares and passive resting times", None, "2012-11..2018-10",
                  "cftc_ats_update2_2019.txt", "Euro 12.4 14.0 0.9 0.8 5.1 4.4 0.4 0.3 2.7 2.5 0.3 0.2 10.6 10.2 1.8 1.5 4.9 4.7 1.6 1.3 9.1 9.9",
                  "relation: " + ("same product (6E row)" if code == '6E' else "same underlying micro/full or group-level" ) + "; result: not a predictability test (documents fast automated liquidity provision)"))
    rows.append(F("Chen (An-Sing) et al., EFMA 2009: trade imbalance and weekly Euro FX futures returns", None, "1999-12-17..2005-03-04",
                  "efma2009_0102_euro_fx_trade_imbalance.txt",
                  "we find weekly returns in Euro FX futures exhibit significant reversals following periods of extreme (negative) trade imbalances",
                  "relation: " + ("same product" if code == '6E' else "full-size version (6E)" if code == 'M6E' else "close cousin (CME FX futures)") + "; result: positive at weekly horizon only (not short-horizon); conference paper"))
    rows.append(F("Kao and Fung (IREF 2012): volume, trade imbalance and intraday volatility, euro FX and yen futures on GLOBEX", None, None,
                  "ideas_kao_fung_2012.html.txt", "the net effect of trading imbalance is negative, supporting the asymmetrical information hypothesis",
                  "relation: " + ("same product" if code == '6E' else "full-size version" if code == 'M6E' else "close cousin") + "; result: not a return-predictability test; abstract only"))
    rows.append(F("Cabrera, Wang, Yang (JFM 2009): price discovery Globex regular vs E-mini vs EBS (euro, yen)", None, None,
                  "openalex_10.1002_fut.20352_abstract.txt", "the spot market is found to consistently lead the price discovery process for both currencies",
                  "relation: " + ("same product" if code == '6E' else "full-size version" if code == 'M6E' else "close cousin") + "; result: price discovery, not predictability; abstract only"))
    rows.append(F("Martinez and Tse (FRL 2019): CME tick-size reductions in peso, yen and euro futures", None, None,
                  "ideas_martinez_tse_2019_tick_fx_futures.html.txt", "We find significant evidence of increased market quality for the Mexican peso contracts, but less significant evidence for the other two contracts.",
                  "relation: " + ("same product" if code == '6E' else "full-size version" if code == 'M6E' else "close cousin") + "; result: market quality, not predictability; abstract only"))
    rows.append(F("Andersen, Bondarenko, Gousgounis, Onur (J. Econometrics 2026): FX futures trading invariance, tick data, spread and depth around tick cuts", None, None,
                  "kellogg_fx_futures_invariance.html.txt", "the remaining components of the TI hypothesis adjust to maintain the equilibrium by shifts in the trading intensity and market depth",
                  "relation: CME FX futures (currencies not named in abstract); result: not a predictability test; abstract only"))
    rows.append(F("Chaboud et al. (IFDP 980 / JF 2014): algorithmic trading on EBS spot", None, "2006-2007",
                  "chaboud_etal_ifdp980_rise_of_machines.txt", "algorithmic trades tend to be correlated",
                  "relation: asset class only (spot); result: not a predictability test"))
    if code in ('6A', 'M6A'):
        rows.append(F("Rentzler, Tandon, Yu (JFM 2006): intraday reversals after large moves, seven CME currency futures 1988-2003", None, "1988-2003",
                      "ideas_rentzler_2006_jfm.html.txt", "Significant intraday price‐reversal patterns are observed in five of the seven currency futures contracts",
                      "relation: includes the AUD future? not stated in abstract [unverified]; result: daily-move reversals, not order-book; abstract only"))
    rows.append(F(None, None, None, None, None, "Absent: " + RES_ABSENT))
    return rows

ATS_EMICRO = F({"ATS_pct": 70.9, "manual_pct": 29.1}, "% of volume", "2016-11..2018-10", "cftc_ats_update2_2019.txt",
               "FX - E Micros 8 7 0.0 (0.0) 0.0 (0.0) 69.3 (0.1) 70.9 (0.1) 30.7 (0.1) 29.1 (0.1)",
               "E-micro FX subgroup (8 products in the early period, 7 late; members not listed); no per-product figure for M6E/M6A. Earlier: 66.3% ATS 2012-14, 69.3% 2014-16.")
ATS_6E = F({"ATS_pct": 82.0, "manual_pct": 17.2, "ATS_ATS_pct": 69.4, "MAN_MAN_pct": 4.6}, "% of volume", "2016-11..2018-10", "cftc_ats_update2_2019.txt",
           "Euro 115 125 80.3 82.0 19.1 17.2 66.3 69.4 28.0 25.1 5.1 4.6", "Table 3 (early/late pairs). 2012-14 ATS-ATS 64.5%.")
ATS_G10 = F({"ATS_pct": 85.4, "manual_pct": 13.8}, "% of volume", "2016-11..2018-10", "cftc_ats_update2_2019.txt",
            "FX - G10 24 25 0.7 (0.0) 0.8 (0.0) 83.7 (5.1) 85.4 (4.8) 15.6 (1.0) 13.8 (0.8)", "G10 subgroup; no per-product 6A figure.")
MM_MICRO = F("FX Micros Market Maker Program (M6A, M6E and other micros): continuous two-sided quoting at maximum spreads and minimum sizes; no limit on participants",
             None, "2021-08-01..2025-08-31 (extended 2023 and 2024)", "cftc_cme_rules0901235937_fx_mm_2023.txt",
             "Participants must quote continuous two-sided markets in the Products at maximum bid/ask spreads and minimum quote sizes during a certain percentage of time-in-market.",
             "Product scope quote: 'Micro AUD/USD Futures (“M6A”) ... Micro EUR/USD Futures (“M6E”)'. Term: 'End date is September 30, 2023 March 31, 2024' (2023 filing), extended to 'August 31, 2025' (cftc_cme_rules0808244211_fx_mm_2024.txt). Predecessor programs since 2008 (cftc_cme_rule091719_fx_mm_2019.txt).")
MM_FULL = F(None, None, None, "cftc_cme_rule091719_fx_mm_2019.txt",
            "EUR/AUD, EUR/CAD, EUR/CHF, EUR/GBP, EUR/JPY, GBP/JPY, AUD/JPY, BRL/USD, RUB/USD,",
            "No market-maker or incentive program for the full-size contract found. The 2019 FX Futures MM Program lists crosses, EM pairs and E-micros only. Searched CFTC filings (WebSearch-5, -6). Bank fee programs (Asia-Pacific Incentive Program) exist but are not product-specific [snippet only].")

def tff(code):
    if code == '6E':
        return (F({"Dealer_Intermediary": 34.7, "Asset_Manager_Institutional": 40.3, "Leveraged_Funds": 11.9, "Other_Reportables": 3.9, "Nonreportable": 9.2},
                  "% of OI (long+short+2*spread)/(2*OI)", "53 weekly reports 2022-11-01..2023-10-31", "cftc_fut_fin_txt_2022.zip; cftc_fut_fin_txt_2023.zip",
                  "EURO FX - CHICAGO MERCANTILE EXCHANGE (099741)", "Computed by reports/stage_e28_briefs/work/A1_fx/A1_fx_cot.py (output A1_fx_cot_out.txt). TFF has no commercial-hedger category."),
                F(9.2, "% of OI", "2022-11-01..2023-10-31", "cftc_fut_fin_txt_2023.zip", "EURO FX - CHICAGO MERCANTILE EXCHANGE (099741)", "range 8.5-10.3; small-trader proxy"),
                F(745734, "contracts (mean weekly OI, futures only)", "2022-11-01..2023-10-31", "cftc_fut_fin_txt_2023.zip", "EURO FX - CHICAGO MERCANTILE EXCHANGE (099741)", "CFTC TFF; whether micro positions are aggregated is not stated [unverified]"))
    if code == '6A':
        return (F({"Dealer_Intermediary": 21.0, "Asset_Manager_Institutional": 42.9, "Leveraged_Funds": 20.9, "Other_Reportables": 0.9, "Nonreportable": 14.3},
                  "% of OI (long+short+2*spread)/(2*OI)", "53 weekly reports 2022-11-01..2023-10-31", "cftc_fut_fin_txt_2022.zip; cftc_fut_fin_txt_2023.zip",
                  "AUSTRALIAN DOLLAR - CHICAGO MERCANTILE EXCHANGE (232741)", "Computed by work/A1_fx/A1_fx_cot.py. TFF has no commercial-hedger category."),
                F(14.3, "% of OI", "2022-11-01..2023-10-31", "cftc_fut_fin_txt_2023.zip", "AUSTRALIAN DOLLAR - CHICAGO MERCANTILE EXCHANGE (232741)", "range 11.3-17.9; small-trader proxy"),
                F(167984, "contracts (mean weekly OI, futures only)", "2022-11-01..2023-10-31", "cftc_fut_fin_txt_2023.zip", "AUSTRALIAN DOLLAR - CHICAGO MERCANTILE EXCHANGE (232741)", "CFTC TFF"))
    nf = "Not a separate market in the 2022 or 2023 TFF files (script listed all EURO/AUSTRAL/MICRO market names; no micro FX market)."
    return (F(None, "% of OI", "2022-11-01..2023-10-31", "cftc_fut_fin_txt_2023.zip", None, nf),
            F(None, "% of OI", "2022-11-01..2023-10-31", "cftc_fut_fin_txt_2023.zip", None, nf),
            F(None, "contracts", None, None, None, "No OI source found (not in TFF; CME ADV report has no OI; CME OI pages script-rendered)."))

ADV = {  # (YTD2023 Jan-Aug, YTD2022, YTD2026 Jan-Sep, YTD2025, row quote 2023, row quote 2026)
 '6E': (223555, 227222, 227726, 237823, "EURO FX 181,181 218,188.48 -17.0% 198,201.7 -8.6% 223,555 227,222 -1.6%", "EURO FX 317,270 278,609.05 13.9% 138,686.19 128.8% 227,726 237,823 -4.2%"),
 'M6E': (30128, 35780, 23742, 36978, "MICRO EUR/USD 26,200 36,258.87 -27.7% 28,910.4 -9.4% 30,128 35,780 -15.8%", "MICRO EUR/USD 17,296 32,474.48 -46.7% 12,815.29 35.0% 23,742 36,978 -35.8%"),
 '6A': (93860, 97935, 120862, 101374, "AUSTRALIAN DOLLAR 83,581 87,592.17 -4.6% 90,273.3 -7.4% 93,860 97,935 -4.2%", "AUSTRALIAN DOLLAR 134,033 109,197.9 22.7% 72,461.38 85.0% 120,862 101,374 19.2%"),
 'M6A': (13103, 12441, 7384, 11030, "MICRO AUD/USD 13,000 10,498.61 23.8% 13,824.35 -6.0% 13,103 12,441 5.3%", "MICRO AUD/USD 4,356 6,307.62 -30.9% 3,351.76 30.0% 7,384 11,030 -33.1%"),
}
A0REF = {'6E': "| 6E | yes | 0.00005 | 6.25 | 3.56 | 3.58 | 0.19 | 153.0 | 176,291 | 118 (195.2) | 50 (104.9) | 0.42 | 257 (2) |",
         '6A': "| 6A | yes | 0.00005 | 5.00 | 3.09 | 3.12 | 0.21 | 138.0 | 82,950 | 46 (83.0) | 30 (52.1) | 0.38 | 257 (2) |"}

SPEC = {
 '6E': dict(name="Euro FX (EUR/USD) futures", unit=125000, cur="EUR", tick=0.00005, tv=6.25, ch=261,
            sf="cme_rulebook_ch261_6E.txt", sq="minimum price fluctuations shall be in multiples of $.00005 per Euro, equivalent to $6.25 per contract", uq="The unit of trading shall be 125,000 Euro.", sw="rulebook Wayback snapshot 2023-09-28"),
 'M6E': dict(name="Micro EUR/USD futures (E-micro EUR/USD)", unit=12500, cur="EUR", tick=0.0001, tv=1.25, ch=292,
            sf="cme_rulebook_ch292.txt", sq="Minimum price fluctuations shall be in multiples of $.0001 per Euro, equivalent to $1.25 per contract.", uq="The unit of trading shall be 12,500 Euro.", sw="rulebook Wayback snapshot 2025-05-15; same tick on spec page 2021-04-20"),
 '6A': dict(name="Australian dollar (AUD/USD) futures", unit=100000, cur="AUD", tick=0.00005, tv=5.00, ch=255,
            sf="cme_rulebook_ch255_6A.txt", sq="minimum price fluctuations shall be in multiplies of $.00005 per Australian dollar, equivalent to $5.00 per contract", uq="The unit of trading shall be 100,000 Australian dollars.", sw="rulebook Wayback 2023 snapshot; half tick in force since 2020 (Jan 2020 filing still shows $.0001 = $10.00)"),
 'M6A': dict(name="Micro AUD/USD futures (E-micro AUD/USD)", unit=10000, cur="AUD", tick=0.0001, tv=1.00, ch=291,
            sf="cme_rulebook_ch291.txt", sq="Minimum price fluctuations shall be in multiples of $.0001 per Australian dollar, equivalent to $1.00 per contract.", uq="The unit of trading shall be 10,000 Australian dollars.", sw="rulebook Wayback snapshot 2025; same tick on spec page 2021-04-21"),
}

def candidate(code):
    s = SPEC[code]; micro = code.startswith('M')
    hf, hq, hw = HOURS_Q[code]
    tffv, nonrep, oi = tff(code)
    a = ADV[code]
    d = {"code": code, "family": "FX", "ROOT": "A1_fx"}
    d["product_name"] = F(s['name'], None, None, s['sf'], None, "CME rulebook chapter %d" % s['ch'])
    d["globex_code"] = F(code, None, None, hf, "CME Globex: %s" % code, None)
    d["tick_size"] = F(s['tick'], "USD per %s" % s['cur'], s['sw'], s['sf'], s['sq'], None)
    d["tick_value"] = F(s['tv'], "USD per contract", s['sw'], s['sf'], s['sq'], None)
    d["contract_size"] = F(s['unit'], s['cur'], s['sw'], s['sf'], s['uq'], None)
    if micro:
        d["launch_date"] = F("2009-03", "month", None, "cme_ser5311.html.txt", "In March 2009, E-micro FX futures were listed for trading.",
                             "Re-specified to physical delivery / IMM terms from the Dec 2010 contract (SER 5311). That EUR/USD and AUD/USD were in the 2009 set is inferred from 'six existing E-micro Forex futures contracts launched in 2009' plus later product lists [partly unverified].")
        d["globex_60_dates_pilot_window"] = F(True, None, "2023-11-01..2024-02-29", "cftc_cme_rules0901235937_fx_mm_2023.txt",
                             "Micro EUR/USD Futures (“M6E”)" if code == 'M6E' else "Micro AUD/USD Futures (“M6A”)",
                             "Inferred: launched 2009, continuously listed, and covered by a CME Globex quoting program whose term ran to 2024-03-31. No owned file covers the window (A0_contract_stats.md l.212). Not a count of trade dates.")
        d["matching_algorithm"] = F(None, None, None, None, None, "No product-level source found (CME client wiki and Databento blog list algorithms, not products; CFTC algorithm filings found cover 6E/6J and 6A/6C only).")
        d["market_maker_program"] = MM_MICRO
        d["ats_share"] = ATS_EMICRO
        d["manual_share_cftc"] = F(29.1, "% of volume (manual)", "2016-11..2018-10", "cftc_ats_update2_2019.txt", ATS_EMICRO['quote'], "E-micro FX subgroup")
        d["retail_share"] = F(None, "% of volume", None, "mv_cme_emicro_launch_2009.html.txt",
                              "Smaller Contract Size And Proportionally Reduced Margins Aimed To Attract Retail Participation",
                              "No numeric share found. CME describes E-micros as retail products (2009 launch release; SER 5311: 'serving a need in the market place for retail customers'; 2010 release: 'provide our retail customers'). CME-wide retail share 27% in 2018 (risknet_cme_exchange_innovation.html.txt l.325).")
    else:
        d["launch_date"] = F(None, None, None, "cme_fxhistory.html.txt", None,
                             "Not found (CME FX history page has no product dates; WebSearch-9). Listed well before 2023-11: CFTC TFF weekly OI 2022-11..2023-10; owned GLBX files from %s (A0_contract_stats.md)." % ('2010-06-06' if code == '6E' else '2019-05-01'))
        d["globex_60_dates_pilot_window"] = F(True, None, "2023-11-01..2024-02-29", "cftc_fut_fin_txt_2023.zip",
                             "EURO FX - CHICAGO MERCANTILE EXCHANGE (099741)" if code == '6E' else "AUSTRALIAN DOLLAR - CHICAGO MERCANTILE EXCHANGE (232741)",
                             "Inferred from continuous listing (weekly TFF OI through 2023-10, CME filings 2019-2022, CME ADV reports 2023 and 2026) and owned pilot-window files by name (A0_contract_stats.md l.162-165). Not a count of trade dates.")
        d["matching_algorithm"] = F("FIFO (CME Algorithm F) for outrights; calendar spreads Algorithm K (split FIFO/pro rata)", None,
                                    "from 2019-08-12" if code == '6E' else "from 2020-01-27",
                                    "cftc_cme_rule071819_fx_spread_algo.txt" if code == '6E' else "cftc_cme_ptc011020_aud_algo.txt",
                                    "6E 6E Outright F F" if code == '6E' else "AUD/USD Futures 6A 6A Outright F F",
                                    "Filing: 'No changes are being made to the CME Globex trading matching algorithm for outright transactions'. No later change notice found (not specifically searched after 2020).")
        d["market_maker_program"] = MM_FULL
        d["ats_share"] = ATS_6E if code == '6E' else ATS_G10
        d["manual_share_cftc"] = F(17.2 if code == '6E' else 13.8, "% of volume (manual)", "2016-11..2018-10", "cftc_ats_update2_2019.txt",
                                   ATS_6E['quote'] if code == '6E' else ATS_G10['quote'], "6E per product" if code == '6E' else "G10 subgroup, no per-product 6A figure")
        d["retail_share"] = F(None, "% of volume", None, None, None, "No numeric or qualitative CME retail statement found for the full-size contract. Small-trader proxy: TFF nonreportable share (field nonreportable_share).")
    d["trading_hours"] = F("Sun-Fri 17:00-16:00 CT, 60-minute daily break from 16:00 CT", "Central Time", hw, hf, hq, None)
    d["listing_cycle"] = F({"6E": "quarterly for 20 quarters plus 3 serial months", "M6E": "2 consecutive quarters", "6A": "first 3 consecutive months and 20 months in the March quarterly cycle", "M6A": "two months in the March quarterly cycle"}[code], None, hw, hf, None, "physically delivered; last trade 9:16 a.m. CT two business days before the third Wednesday")
    d["daily_price_limits"] = LIMITS
    d["limit_hit_days_2019_2024"] = LIMIT_HITS
    d["adv_latest_published"] = F(a[2], "contracts/day (exchange ADV, YTD)", "2026-01..2026-09", "cme_adv_report_snap20261011.txt", a[5], "CME Group Exchange ADV Report, September 2026; YTD 2025 = %d. All venues, not Globex-only." % a[3])
    d["adv_pre_pilot_published"] = F(a[0], "contracts/day (exchange ADV, YTD)", "2023-01..2023-08", "cme_adv_report_snap20230924.txt", a[4], "Closest published figure to 2022-11..2023-10 (not exact). YTD 2022 (Jan-Aug) = %d." % a[1])
    d["adv_owned_2022_11_2023_10"] = F(None, None, "2022-11-01..2023-10-31", "reports/stage_e28_briefs/A0_contract_stats.md", A0REF.get(code), "Owned-bar ADV belongs to A0 (A0 Table 1 row; columns: ..., ADV median (v_0), Vol/min main median (mean), Vol/min overnight median (mean), ...)." + ("" if code in A0REF else " A0 has no owned window for this product."))
    d["open_interest"] = oi
    d["trader_type_shares_tff"] = tffv
    d["commercial_hedger_share"] = F(None, None, None, "cftc_fut_fin_txt_2023.zip", None, "TFF (the CFTC report for FX) has no commercial-hedger category; see trader_type_shares_tff.")
    d["nonreportable_share"] = nonrep
    if code == '6E':
        d["median_spread_ticks"] = F(1.2, "ticks (time-weighted average, not median; 0.6 pips)", "June 2021", "cme_fx_market_profile_usecase.html.txt",
                                     "At the top of the book, outright FX futures have the tightest pricing (white line), at an average of around 0.6 pips.",
                                     "Conversion to ticks is mine (1 pip = 0.0001 = 2 ticks of 0.00005). Average, not median; session not split; 'TOB Spread data is not volume weighted'.")
        d["depth_best_level"] = F(None, "contracts", "June 2021", "cme_fx_market_profile_usecase.html.txt",
                                  "For the top of book, futures order size is low and rising through the trading day, while EBS Market order size is consistently high.",
                                  "No contract count published in the fetched text. CME 2024: '$458M was executed' in one second at peak (cme_2024_fx_liquidity_speaks_volumes.html.txt).")
    else:
        d["median_spread_ticks"] = F(None, "ticks", None, None, None, "No source found." + (" Micro tick (0.0001) = 1 pip = 2 full-size ticks, so the micro spread is at least 1 pip while 6E averaged about 0.6 pips (June 2021)." if micro else ""))
        d["depth_best_level"] = F(None, "contracts", None, None, None, "No source found.")
    d["touch_queue_size"] = F(None, "contracts", None, None, None, "No source found; QV cannot be formed from published data.")
    d["volume_per_minute"] = F(None, "contracts/min", "2022-11-01..2023-10-31", "reports/stage_e28_briefs/A0_contract_stats.md", A0REF.get(code), "Owned magnitudes belong to A0 (A0 Table 1 row; Vol/min main median (mean) is the 10th column)." + ("" if code in A0REF else " None for this product."))
    d["overnight_vs_main_spread"] = F(None, "ratio", None, "cme_fx_market_profile_usecase.html.txt" if code == '6E' else None,
                                      "The top of book (“TOB”) spreads for both EBS Market and CME futures are consistent throughout the trading day" if code == '6E' else None,
                                      "No tabulated session split found." )
    if code in ('6E', 'M6E'):
        d["product_specific_releases_per_week"] = F(0.15, "ECB decisions per week (8 per year)", "2027 calendar (latest page)", "ecb_meeting_calendar.html.txt",
                                                    "Governing Council of the ECB: monetary policy meeting in Frankfurt (Day 2), followed by press conference",
                                                    "Monthly euro-area releases (flash HICP, PMIs, Ifo/ZEW) not sourced; total stays below 2 per week by count [unverified]. 2019-2024 meeting counts not fetched.")
    else:
        d["product_specific_releases_per_week"] = F(0.15, "RBA decisions per week (8 per year)", "2025-2026 schedules", "rba_board_meeting_schedules.html.txt",
                                                    "2–3 February / 16–17 March / 4–5 May / 15–16 June / 10–11 August 2026 / 28–29 September / 2–3 November / 7–8 December",
                                                    "Pre-2024: 11 meetings a year [unverified]. Monthly Australian labour force, CPI and Chinese data not sourced; total below 2 per week by count [unverified].")
    d["weekend_gap_exposure"] = WEEKEND
    d["jump_frequency"] = F({"6E": {"2019": 0, "2020": 1, "2021": 0, "2022": 0, "2023_to_Oct": 0}, "6A": {"2019_from_May": 0, "2020": 2, "2021": 0, "2022": 0, "2023_to_Oct": 0}}[code if not micro else code[1:]], "days with |daily log return| > 4 x that year's daily SD", "2019-2023-10", "reports/stage_e28_briefs/A0_contract_stats.md",
                            {"6E": "2019: 0/254, 2020: 1/255, 2021: 0/255, 2022: 0/254, 2023: 0/213", "6A": "2019: 0/170, 2020: 2/255, 2021: 0/255, 2022: 0/254, 2023: 0/213"}.get(code if not micro else code[1:]),
                            "A0's owned counts" + (" for the full-size contract on the same underlying (no owned micro data)." if micro else ".") + " No published jump-frequency study for 2019-2024 found.")
    d["spot_interaction_price_discovery"] = SPOT
    d["microstructure_research"] = research(code)
    return d

data = [candidate(c) for c in ('M6E', '6E', 'M6A', '6A')]
json.dump(data, open(OUT, 'w'), indent=1, ensure_ascii=False)
print(len(data), 'candidates;', sum(len(d) for d in data), 'fields;', sum(1 for d in data for k, v in d.items() if isinstance(v, dict) and v.get('value') is None), 'null-valued fields')
