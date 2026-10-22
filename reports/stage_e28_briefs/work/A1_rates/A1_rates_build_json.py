"""Build A1_rates.json (one object per candidate) from facts gathered in A1_rates.md.

Every field is {"value","unit","window","source_file","quote","note"}. Unknowns have value None and say what was
searched. Run: python3 -I work/A1_rates/A1_rates_build_json.py (from reports/stage_e28_briefs).
"""
import json

P = "reports/stage_e28_briefs/pages/A1_rates/"
TFF = json.load(open("work/A1_rates/A1_rates_tff_summary.json"))


def F(value=None, unit=None, window=None, source_file=None, quote=None, note=None):
    return {"value": value, "unit": unit, "window": window, "source_file": source_file, "quote": quote, "note": note}


# ---------- shared facts ----------
MICRO_FILING = P + "cftc_ptc072921cbotdcm001.pdf.txt"
ADV_AUG23 = P + "cme_Web_ADV_Report_CBOT_20230924143322.pdf.txt"
ADV_NOV23 = P + "cme_Web_ADV_Report_CMEG_20231218025648.pdf.txt"
ADV_SEP26 = P + "cme_Web_ADV_Report_CMEG_20261011043127.pdf.txt"
OI_MAR24 = P + "cme_Web_OI_Report_CBOT_20240416143839.pdf.txt"
OI_OCT25 = P + "cme_Web_OI_Report_CBOT_20251112073031.pdf.txt"
SPFL = P + "cme_special_price_fluctuation_limits.xlsx"
MM23 = P + "cftc_rules0706233776.pdf.txt"
MM26 = P + "cftc_rules0708269230.pdf.txt"
AUCT = P + "ust_tentative_auction_schedule.pdf.txt"
HR17 = P + "cftc_oce_automatedtrading_update_2017.pdf.txt"
JSR = P + "jsr_oct15_2014.pdf.txt"
LIQ18 = P + "cme_ir_futures_liquidity_update_2018.html.txt"
SER8542 = P + "cme_SER-8542.pdf.txt"

LIMIT_HITS_UNKNOWN = F(None, "days per year", "2019-2024", None, None,
                       "No CME notice, regulator report or press item reporting a Rule 589 halt in this product in "
                       "2019-2024 was found (one WebSearch on Treasury futures halts and dynamic circuit breakers; "
                       "SER-8542 read). Gap, not a finding of zero. See A1_rates.md F8.")
WEEKEND = F(None, None, None, None, None,
            "Underlying is the US Treasury yield/price; no source fetched states that cash Treasuries trade while "
            "CME Globex is closed (Fri 4:00 p.m. CT to Sun 5:00 p.m. CT). Not crypto spot. Not verified from a "
            "primary source either way, so recorded as unknown (expected no, but unsourced).")
OVERNIGHT_SPREAD = F(None, "ticks", None, None, None,
                     "No published overnight (ETH) spread found for this product; CME 2023 rates review shows ETH/ATH "
                     "ADV only as charts. Searched CME liquidity reports (2018 update, 2023 review), FEDS 2025-038, "
                     "JSR 2015.")
VPM = F(None, "contracts per minute", None, None, None,
        "Not published for this product in any source found; A0 owns 1-minute bars for ZT..ZB (volume per minute "
        "is derivable there), none for the micro yields.")
RETAIL_TREAS = F(None, "% of volume", None, None, None,
                 "No CME or regulator retail-share figure found (searched CME press releases and rates reviews, "
                 "CBOT filings, CFTC OCE papers). Proxy: Haynes-Roberts small manual traders share (see "
                 "hft_automated_share note) and TFF nonreportable share of OI.")
HEDGER_TFF = F(None, "% of OI", None, None, None,
               "CFTC TFF (the report for rates) has no commercial-hedger category: categories are dealer, asset "
               "manager, leveraged funds, other reportables, nonreportables. See tff_category_shares.")


def releases(tenor):
    return F(0.23, "auctions of the matching Treasury tenor per week (about 1 per month)",
             "Treasury tentative schedule Aug 2026 - Jan 2027", AUCT,
             tenor,
             "Each nominal coupon tenor is auctioned once a month (6 auctions per tenor in the 6-month schedule). "
             "Whether auctions count as product-specific releases or as the shared US macro calendar is for the "
             "scorer. Other tenors' auctions (2,3,5,7,10,20,30-year) total about 7 per month across the curve; bills "
             "several per week. No other product-specific scheduled release found.")


def tff(code):
    rows = {}
    for w in ("2022-11..2023-10", "latest"):
        rows[w] = TFF.get(f"{code}|{w}")
    return rows


def nonrep(code, market_name):
    t = tff(code)
    a, b = t["2022-11..2023-10"], t["latest"]
    return F({"2022-11..2023-10": {"long": a["nonrept_pct_long"], "short": a["nonrept_pct_short"]},
              "latest_52w": {"long": b["nonrept_pct_long"], "short": b["nonrept_pct_short"]}},
             "% of open interest (mean of weekly values)",
             f"{a['first']}..{a['last']} ({a['n_reports']} reports); {b['first']}..{b['last']} ({b['n_reports']} reports)",
             P + "cftc_tff_rates_2022-11_2023-10.json; " + P + "cftc_tff_rates_latest.json",
             market_name,
             "Computed by work/A1_rates/A1_rates_tff.py as the mean of pct_of_oi_nonrept_long_all / _short_all "
             "(CFTC TFF futures-only, Socrata gpe5-46if). Share of OI, not of volume.")


def tffcats(code, market_name):
    t = tff(code)
    keep = ["dealer", "asset_mgr", "lev_money", "other_rept", "nonrept"]
    v = {}
    for w, r in t.items():
        v[w] = {k: {"long": r[k + "_pct_long"], "short": r[k + "_pct_short"]} for k in keep}
        v[w]["mean_oi"] = r["mean_oi"]
        v[w]["mean_traders_tot"] = r["mean_traders_tot"]
        v[w]["n_reports"] = r["n_reports"]
    return F(v, "% of open interest (mean of weekly values)", "2022-11..2023-10 and 2025-10..2026-10",
             P + "cftc_tff_rates_2022-11_2023-10.json; " + P + "cftc_tff_rates_latest.json", market_name,
             "CFTC Traders in Financial Futures, futures only; summary in work/A1_rates/A1_rates_tff_summary.json")


def adv_row(label, aug23, nov23, sep26):
    return aug23, nov23, sep26, label


# ---------- Treasury futures ----------
TREAS = {
    "ZT": dict(
        name="Short-Term U.S. Treasury Note Futures (2-Year)", ch="21", rb=P + "cbot_rulebook_II_21.pdf.txt",
        name_q="Short-Term U.S. Treasury Note Futures (2-Year)",
        tick=0.00390625, tick_unit="points of par (1/8 of 1/32)", tickv=7.8125,
        tick_q="The minimum price fluctuation shall be one-eighth of one thirty-second of one point (equal to $7.8125 per contract), including intermonth spreads.",
        size_q="The unit of trading shall be U.S. Treasury notes having a face value at maturity of two hundred thousand dollars ($200,000) or multiples thereof.",
        size=200000, cap="Wayback capture 2026-04-22 of CBOT rulebook II/21.pdf",
        dyn="0.75 of 1 point", tff_code="ZT", tff_name="UST 2Y NOTE - CHICAGO BOARD OF TRADE",
        adv_label="2-YR NOTE", adv=(797491, 882991.9, 675122.09, 1464550, 1317555, 1250894), oi=(2373250, 4606433),
        adv_q_aug="2-YR NOTE 1,087,650 856,268.83 27.0% 552,402.7 96.9% 797,491 718,838 10.9%",
        adv_q_nov="2-YR NOTE 1,464,550 882,991.9 65.9% 675,122.09 116.9% 825,021 702,369 17.5%",
        adv_q_sep="2-YR NOTE 1,250,894 748,591.24 67.1% 1,908,757.29 -34.5% 1,317,555 1,063,259 23.9%",
        oi_q="2-YR NOTE 3,756,330 2,373,250 58.3% 3,695,788 1.6% (Mar 2024 report); 2-YR NOTE 4,606,433 4,503,100 2.3% 4,610,882 -0.1% (Oct 2025 report)",
        depth=99471, depth3=131254, depth_q="2-Yr Note (ZT) 3,854 38,852 99,471 156% 13,760 74,152 131,254 77%",
        algo=("partial pro-rata (CME 'K' configurable / split FIFO-pro-rata family); exact current parameters not found",
              P + "cftc_two_year_analysis_2019.pdf.txt",
              "The 2Y Treasury contract is traded using a partial pro-rata matching algorithm.",
              "Databento 2025-08-01 (databento_cme_matching_algorithms.html.txt) lists 'Configurable' with 'Popular CME products: ZT, ZQ, ZC, ZS, ZW outrights'. CME 2008 notice: K algorithm 'was only applied to the 2-Year U.S. Treasury Note futures'. GCC Product Resources page (authoritative per CBOT Rule 580) is on blocked cmegroup.com."),
        hft=("ZT not tabulated by product in Haynes-Roberts (only the top 3 by volume per group: 10 Yr, 5 Yr). Group 'Interest Rate - US Treasury' ATS share 64.0% (2012-14) and 68.4% (2014-16) of volume.",),
        auction_q="2-Year NOTE Thursday, August 20, 2026 Tuesday, August 25, 2026 Monday, August 31, 2026",
        research="R1 (COUSIN, NEG), R2 (COUSIN, NEG), R3 (COUSIN, NULL), R4 (SAME, NULL: matching-algorithm mechanics), R7 (SAME, POS weekly), R8 (SAME, NULL mechanism; abstract only), R9 (SAME/COUSIN, POS, abstract only), R14 (CLASS theory for pro-rata)",
    ),
    "ZF": dict(
        name="Medium-Term U.S. Treasury Note Futures (5-Year)", ch="20", rb=P + "cbot_rulebook_II_20.pdf.txt",
        name_q="Medium-Term U.S. Treasury Note Futures (5-Year)",
        tick=0.0078125, tick_unit="points of par (1/4 of 1/32)", tickv=7.8125,
        tick_q="The minimum price fluctuation shall be one-quarter of one thirty-second of one point (equal to $7.8125 per contract), including intermonth spreads.",
        size_q="The unit of trading shall be U.S. Treasury notes having a face value at maturity of one hundred thousand dollars ($100,000) or multiples thereof.",
        size=100000, cap="Wayback capture 2024-03-01 of CBOT rulebook II/20.pdf",
        dyn="1.50 points", tff_code="ZF", tff_name="UST 5Y NOTE - CHICAGO BOARD OF TRADE",
        adv_label="5-YR NOTE", adv=(1542263, 1659547.95, 1335160.5, 2740659, 1938361, 1913161), oi=(4415991, 6990134),
        adv_q_aug="5-YR NOTE 2,132,110 1,519,169.87 40.3% 1,130,591.35 88.6% 1,542,263 1,372,161 12.4%",
        adv_q_nov="5-YR NOTE 2,740,659 1,659,547.95 65.1% 1,335,160.5 105.3% 1,593,595 1,348,169 18.2%",
        adv_q_sep="5-YR NOTE 1,913,161 1,302,551.29 46.9% 2,392,004.81 -20.0% 1,938,361 1,859,680 4.2%",
        oi_q="5-YR NOTE 5,983,841 4,415,991 35.5% 5,822,423 2.8% (Mar 2024 report); 5-YR NOTE 6,990,134 6,195,313 12.8% 6,642,163 5.2% (Oct 2025 report)",
        depth=1319, depth3=6632, depth_q="5-Yr Note (ZF) 596 866 1,319 52% 3,172 4,465 6,632 49%",
        algo=("FIFO (outrights)", P + "cftc_two_year_analysis_2019.pdf.txt",
              "For a few days in May of 2015, the 2Y Treasury contract unexpectedly defaulted to a pure FIFO algorithm, matching the other Treasury contracts’ algorithms",
              "Databento 2025-08-01: FIFO 'Popular products: ES, NQ, ZN, ZF, ZB, CL outrights'. Calendar spreads 20% FIFO / 80% pro-rata since 2014-10-06 (CBOT 14-348)."),
        hft=("Haynes-Roberts 2017 Table 3: '5 Yr Note 360 378 50.5 53.2 32.8 34.0 8.6 7.4' (total volume mm; ATS-ATS %; ATS-MAN %; MAN-MAN %; 2012-14 then 2014-16). Table 5: small manual traders 18.7% then 18.0% of volume.",),
        auction_q="5-Year NOTE Thursday, August 20, 2026 Wednesday, August 26, 2026 Monday, August 31, 2026",
        research="R1 (COUSIN, NEG), R2 (COUSIN, NEG), R3 (COUSIN, NULL), R5 (SAME, NULL descriptive), R7 (SAME, POS weekly), R9 (SAME/COUSIN, POS, abstract only), R12 (SAME, NULL descriptive)",
    ),
    "ZN": dict(
        name="U.S. Treasury Note Futures (6 1/2 to 7 3/4-Year), the 10-Year T-Note futures", ch="19", rb=P + "cbot_rulebook_II_19.pdf.txt",
        name_q="U.S. Treasury Note Futures (6½ to 7¾-Year)",
        tick=0.015625, tick_unit="points of par (1/2 of 1/32)", tickv=15.625,
        tick_q="The minimum price fluctuation shall be one-half of one thirty-second of one point (equal to $15.625 per contract), except for intermonth spreads for which the minimum price fluctuation shall be one-quarter of one thirty-second of one point (equal to $7.8125 per contract).",
        size_q="The unit of trading shall be U.S. Treasury Notes having a face value at maturity of one hundred thousand dollars ($100,000) or multiples thereof.",
        size=100000, cap="Wayback capture 2023-12-06 of CBOT rulebook II/19.pdf",
        dyn="2.00 points", tff_code="ZN", tff_name="UST 10Y NOTE - CHICAGO BOARD OF TRADE",
        adv_label="10-YR NOTE", adv=(1971131, 2174701.33, 1961964.73, 3007906, 2595499, 2646717), oi=(4248005, 5511626),
        adv_q_aug="10-YR NOTE 2,429,196 1,892,104.74 28.4% 1,493,233.1 62.7% 1,971,131 1,917,259 2.8%",
        adv_q_nov="10-YR NOTE 3,007,906 2,174,701.33 38.3% 1,961,964.73 53.3% 2,026,975 1,898,452 6.8%",
        adv_q_sep="10-YR NOTE 2,646,717 1,754,399.24 50.9% 3,108,874.86 -14.9% 2,595,499 2,341,136 10.9%",
        oi_q="10-YR NOTE 4,350,564 4,248,005 2.4% 4,304,156 1.1% (Mar 2024 report); 10-YR NOTE 5,511,626 4,566,438 20.7% 5,462,258 0.9% (Oct 2025 report)",
        depth=2507, depth3=12322, depth_q="10-Yr Note (ZN) 1,166 1,649 2,507 52% 6,360 8,324 12,322 48%",
        algo=("FIFO (outrights)", P + "cftc_two_year_analysis_2019.pdf.txt",
              "For a few days in May of 2015, the 2Y Treasury contract unexpectedly defaulted to a pure FIFO algorithm, matching the other Treasury contracts’ algorithms",
              "Databento 2025-08-01: FIFO 'Popular products: ES, NQ, ZN, ZF, ZB, CL outrights'. Calendar spreads 20% FIFO / 80% pro-rata (CBOT 14-348 conformed 2-,3-,5-year spreads 'to the 10-Year U.S. Treasury Note calendar spread allocation mix')."),
        hft=("Haynes-Roberts 2017 Table 3: '10 Yr Note 643 661 42.6 48.0 41.1 39.7 11.9 8.7' (ATS-ATS 42.6% then 48.0%; MAN-MAN 11.9% then 8.7%). Table 5: small manual traders 27.4% then 23.7%. JSR 2015: PTFs 68.4% of 10-year futures volume in the Oct 15 2014 event window and >50% generally. FEDS 2025-038: PTFs 70% of liquidity-providing volume; ~72% of passive orders in 2021.",),
        auction_q="10-Year NOTE Wednesday, August 05, 2026 Wednesday, August 12, 2026 Monday, August 17, 2026",
        research="R1 (SAME, NEG: passive fills adversely selected, ~1/2 tick), R2 (SAME, NEG: 199 of 224 fills adverse), R3 (SAME, NULL), R5 (SAME, NULL), R6 (SAME, NULL), R7 (SAME, POS weekly), R9 (SAME/COUSIN, POS, abstract only)",
    ),
    "ZB": dict(
        name="U.S. Treasury Bond Futures", ch="18", rb=P + "cbot_rulebook_II_18.pdf.txt",
        name_q="U.S. Treasury Bond Futures",
        tick=0.03125, tick_unit="points of par (1/32)", tickv=31.25,
        tick_q="The minimum price fluctuation shall be one thirty-second of one point (equal to $31.25 per contract), except for intermonth spreads for which the minimum price fluctuation shall be one-quarter of one thirty-second of one point (equal to $7.8125 per contract).",
        size_q="The unit of trading shall be U.S. Treasury Bonds having a face value at maturity of one hundred thousand dollars ($100,000) or multiples thereof.",
        size=100000, cap="Wayback capture 2023-12-26 of CBOT rulebook II/18.pdf",
        dyn="4.50 points", tff_code="ZB", tff_name="UST BOND - CHICAGO BOARD OF TRADE",
        adv_label="30-YR BOND", adv=(405796, 452782.14, 554315, 679777, 609587, 609453), oi=(1191819, 1920369),
        adv_q_aug="30-YR BOND 546,547 411,020.7 33.0% 332,159.5 64.5% 405,796 407,748 -0.5%",
        adv_q_nov="30-YR BOND 679,777 452,782.14 50.1% 554,315 22.6% 447,255 399,034 12.1%",
        adv_q_sep="30-YR BOND 609,453 437,362.05 39.3% 851,806.33 -28.5% 609,587 557,495 9.3%",
        oi_q="30-YR BOND 1,514,046 1,191,819 27.0% 1,498,762 1.0% (Mar 2024 report); 30-YR BOND 1,920,369 1,871,856 2.6% 1,844,283 4.1% (Oct 2025 report)",
        depth=377, depth3=1898, depth_q="Bond (ZB) 154 253 377 49% 843 1,309 1,898 45%",
        algo=("FIFO (outrights)", P + "cftc_two_year_analysis_2019.pdf.txt",
              "For a few days in May of 2015, the 2Y Treasury contract unexpectedly defaulted to a pure FIFO algorithm, matching the other Treasury contracts’ algorithms",
              "Databento 2025-08-01: FIFO 'Popular products: ES, NQ, ZN, ZF, ZB, CL outrights'. The CFTC 2019 study used the 30-year bond contract as its FIFO control."),
        hft=("ZB not tabulated by product in Haynes-Roberts (top 3 per group only). Group ATS share 64.0% then 68.4%. JSR 2015: PTFs >50% of futures volume across maturities.",),
        auction_q="30-Year BOND Wednesday, August 05, 2026 Thursday, August 13, 2026 Monday, August 17, 2026",
        research="R1 (COUSIN, NEG), R2 (COUSIN, NEG), R3 (COUSIN, NULL), R4 (control contract in a ZT study), R7 (SAME, POS weekly), R9 (SAME/COUSIN, POS, abstract only)",
    ),
}

YIELDS = {
    "2YY": dict(tenor="2-Year", ch="80", adv=(320, 428.71, 175.91, 213, 0, 0), oi=(461, 20), tff=None,
                adv_q_nov="2Y YIELD 213 428.71 -50.3% 175.91 21.2% 292 386 -24.2%",
                adv_q_aug="2Y YIELD 237 254.78 -6.8% 227.6 4.3% 320 363 -11.9%",
                adv_q_sep="2Y YIELD 0 8 -97.6% 0 - 0 36 -99.5%",
                oi_q="2Y YIELD 518 461 12.4% 525 -1.3% (Mar 2024 report); 2Y YIELD 20 714 -97.2% 40 -50.0% (Oct 2025 report)",
                auction_q="2-Year NOTE Thursday, August 20, 2026 Tuesday, August 25, 2026 Monday, August 31, 2026",
                cousin="ZT", mm="quoting obligations only via the 10Y-2YY inter-commodity spread; fee waivers for 2YY Globex volume on meeting Tier 1 10Y-2YY obligations"),
    "5YY": dict(tenor="5-Year", ch="81", adv=(6, 24.76, 0.45, 0, 0, 0), oi=(0, 0), tff=None,
                adv_q_nov="5Y YIELD 0 24.76 -100.0% 0.45 -100.0% 4 97 -95.7%",
                adv_q_aug="5Y YIELD 0 14.13 -98.2% 0.25 4.4% 6 124 -95.5%",
                adv_q_sep="5Y YIELD 0 1.95 -97.6% 0 - 0 0 -94.5%",
                oi_q="5Y YIELD 0 0 - 0 - (Mar 2024 report); 5Y YIELD 0 0 - 41 -100.0% (Oct 2025 report)",
                auction_q="5-Year NOTE Thursday, August 20, 2026 Wednesday, August 26, 2026 Monday, August 31, 2026",
                cousin="ZF", mm="quoting obligations only via the 10Y-5YY inter-commodity spread; fee waivers for 5YY Globex volume on meeting Tier 1 10Y-5YY obligations"),
    "10Y": dict(tenor="10-Year", ch="82", adv=(4230, 2481.62, 9071, 7282, 1277, 1398), oi=(2921, 3454), tff="10Y",
                adv_q_nov="10Y YIELD 7,282 2,481.62 193.4% 9,071 -19.7% 5,163 4,702 9.8%",
                adv_q_aug="10Y YIELD 6,172 4,119.7 49.8% 4,021.85 53.5% 4,230 4,714 -10.3%",
                adv_q_sep="10Y YIELD 1,398 2,084.95 -32.9% 632.38 121.1% 1,277 3,287 -61.1%",
                oi_q="10Y YIELD 2,050 2,921 -29.8% 6,511 -68.5% (Mar 2024 report); 10Y YIELD 3,454 5,008 -31.0% 2,671 29.3% (Oct 2025 report)",
                auction_q="10-Year NOTE Wednesday, August 05, 2026 Wednesday, August 12, 2026 Monday, August 17, 2026",
                cousin="ZN", mm="direct outright quoting tiers (Tier 1/2/3 RTH, ETH) plus 10Y legs of all three inter-commodity spreads; fee waivers; from Aug 2026 a $10,000 monthly incentive pool"),
    "30Y": dict(tenor="30-Year", ch="83", adv=(47, 201.1, 103.5, 48, 0, 2), oi=(178, 9), tff=None,
                adv_q_nov="30Y YIELD 48 201.1 -76.2% 103.5 -53.8% 53 461 -88.4%",
                adv_q_aug="30Y YIELD 53 299.61 -82.3% 27.5 93.0% 47 489 -90.5%",
                adv_q_sep="30Y YIELD 2 0.38 374.9% 1 81.0% 0 0 188.5%",
                oi_q="30Y YIELD 22 178 -87.6% 29 -24.1% (Mar 2024 report); 30Y YIELD 9 3 200.0% 8 12.5% (Oct 2025 report)",
                auction_q="30-Year BOND Wednesday, August 05, 2026 Thursday, August 13, 2026 Monday, August 17, 2026",
                cousin="ZB", mm="quoting obligations only via the 30Y-10Y inter-commodity spread"),
}


def common_tail(obj, code, family_research, releases_q):
    obj["limit_hit_days_2019_2024"] = LIMIT_HITS_UNKNOWN
    obj["weekend_gap_exposure"] = WEEKEND
    obj["median_spread_ticks_overnight"] = OVERNIGHT_SPREAD
    obj["volume_per_minute"] = VPM
    obj["scheduled_releases_per_week"] = releases(releases_q)
    obj["microstructure_research"] = F(family_research, None, None, "reports/stage_e28_briefs/A1_rates.md (section F12)",
                                       None, "Study IDs refer to the F12 table, which carries each study's file, quote, relation and result.")
    return obj


def treasury(code, d):
    o = {"candidate": code, "family": "rates"}
    o["product_name"] = F(d["name"], None, None, d["rb"], d["name_q"], f"CBOT rulebook chapter {d['ch']}; {d['cap']}" + ("; the Rule 589 table (capture 2024-10-01) titles it 'U.S. Treasury Note Futures (6½ to 8-Year)' and SER-7193 (2014) 'Long-Term U.S. Treasury Note Futures (6 ½ to 10-Year)': the deliverable window has changed over time" if code == "ZN" else ""))
    o["product_code"] = F(code, None, None, P + "cme_SER-7193.html.txt", None,
                          "SER-7193 product table lists the Globex code next to the product title (ZT, ZF, ZN, ZB).")
    o["tick_size"] = F(d["tick"], d["tick_unit"], None, d["rb"], d["tick_q"], d["cap"])
    o["tick_value"] = F(d["tickv"], "USD per contract", None, d["rb"], d["tick_q"], None)
    o["contract_size"] = F(d["size"], "USD face value", None, d["rb"], d["size_q"], None)
    o["settlement"] = F("physical delivery of eligible Treasury securities; March-June-September-December expiries", None, None,
                        d["rb"], None, "Rulebook chapter delivery rules; quarterly cycle per CBOT 2015 TN filing ('Nearest 3 months in the March-June-September-December quarterly cycle', cftc_ptc122315cbotdcm001.pdf.txt) for the cousin TN; not quoted for this product.")
    if code == "ZB":
        o["launch_date"] = F(1977, "year", None, P + "cme_understanding_treasury_futures.pdf.txt",
                             "Treasury Bond futures were introduced on the Chicago || Board of Trade in 1977.", "Two-column layout: the sentence spans two lines with a chart label between them.")
    else:
        o["launch_date"] = F(None, None, None, P + "cme_understanding_treasury_futures.pdf.txt",
                             None,
                             "Exact launch year not found in fetched files; listed and traded since at least 2014 (CBOT 14-348 algorithm filing names it) and through 2023-2026 (CME ADV reports).")
    o["globex_60_dates_in_2023-11..2024-02"] = F(True, None, "2023-11-01..2024-02-29", ADV_NOV23, d["adv_q_nov"],
                                                  "Launch long before 2023-11 and continuous listing; November 2023 ADV in the millions (published aggregate; no market data read).")
    a, s, q, n = d["algo"]
    o["match_algorithm"] = F(a, None, None, s, q, n)
    o["trading_hours"] = F("Sunday 5:00 p.m. - Friday 4:00 p.m. CT, daily maintenance 4:00-5:00 p.m. CT", None, None,
                           P + "cftc_ptc1005237330.pdf.txt",
                           "CME Globex: Sunday 5:00 p.m. - Friday - 4:00 p.m. CT with a daily maintenance period from 4:00 p.m. - 5:00 p.m. CT",
                           "Quote is from the 2023 CBOT filing for Monday weekly options on these futures; futures spec page blocked. Cousin Micro Ultra futures filing gives the same schedule (cftc_ptc02232412041.pdf.txt).")
    o["price_limits"] = F({"daily_limit": None, "dynamic_variant": d["dyn"], "halt": "2-minute halt when traded/bid/offered through the dynamic limit in a rolling 60-minute look-back"},
                          None, "Rule 589 table Wayback capture 2024-10-01", SPFL,
                          f"{d['name_q'].replace('U.S.', 'US') if code != 'ZN' else 'U.S. Treasury Note Futures (6½ to 8-Year)'} | {d['ch']} | {code} | Primary | Primary | {d['dyn']}",
                          "Sheet 'Interest Rates', column 'Dynamically Calculated Variant - All Hours'. Dynamic limits in force since trade date 2020-07-27 (SER-8542). No fixed daily limit value found.")
    a23, n22, o23, n23, y26, s26 = d["adv"]
    o["adv_published_latest"] = F({"YTD_Jan-Sep_2026": y26, "Sep_2026": s26}, "contracts per day, all expiries",
                                  "Jan-Sep 2026", ADV_SEP26, d["adv_q_sep"], "CME Group Exchange ADV Report - Monthly, September 2026 (Wayback capture 2026-10-11).")
    o["adv_2022_11_2023_10"] = F({"YTD_Jan-Aug_2023": a23, "Nov_2022": n22, "Oct_2023": o23}, "contracts per day, all expiries",
                                 "2022-11..2023-10 (pieces published; no 12-month average printed)", ADV_AUG23 + "; " + ADV_NOV23,
                                 d["adv_q_aug"] + " || " + d["adv_q_nov"],
                                 "Aug 2023 report columns: AUG 2023, AUG 2022, %, JUL 2023, %, YTD 2023, YTD 2022, %. Nov 2023 report columns: NOV 2023, NOV 2022, %, OCT 2023, %, YTD 2023, YTD 2022, %. Owned-bar ADV for the standard window is A0's.")
    o["open_interest"] = F({"Mar_2023": d["oi"][0], "Oct_2025": d["oi"][1]}, "contracts, month-end", "Mar 2023; Oct 2025",
                           OI_MAR24 + "; " + OI_OCT25, d["oi_q"], None)
    o["retail_share"] = RETAIL_TREAS
    o["commercial_hedger_share"] = HEDGER_TFF
    o["tff_category_shares"] = tffcats(d["tff_code"], d["tff_name"])
    o["nonreportable_share"] = nonrep(d["tff_code"], d["tff_name"])
    o["market_maker_program"] = F(False, None, None, None, None,
                                  "No market-maker or incentive program for this outright found (CFTC rule filings searched by two WebSearch queries; programs found were for the micro yields and the Micro Ultra contracts). Not a full scan of CBOT incentive filings.")
    o["hft_automated_share"] = F(d["hft"][0], "% of volume", "2012-11..2016-10 (Haynes-Roberts); 2014 (JSR); 2012-2021 (FEDS 2025-038)",
                                 HR17 + "; " + JSR + "; " + P + "feds_2025-038_tsy_futures_liquidity_march2020.pdf.txt",
                                 "Interest Rate - US Treasury 5 5 5.9 (1.5) 4.5 (1.1) 64.0 (16.6) 68.4 (16.4) 30.2 (7.8) 27.1 (6.5)",
                                 "ATS = automated trading system (not only HFT). Quote is Table 2 (Non-Electronic %, ATS %, Manual %; two periods).")
    o["median_spread_ticks_main"] = F(1, "ticks (best bid/offer spread equals the minimum tick > 99% of the day)", "2018, RTH 7:00-16:00 CT",
                                      LIQ18, "For all Treasury futures products, for example, best bid/offered price spreads matched corresponding contract minimum price increments throughout more than 99% of each trading day.",
                                      "Median not published; value inferred from '>99% of each trading day at the minimum increment'. ZN also: FEDS 2025-038 '94% of bid-ask spread observations are \"stuck\" at one tick' (March 2020). ZT's tick was halved in early 2019 (abstract-only, R8), after which no ZT spread figure was found.")
    o["depth_best_level"] = F({"best_level": d["depth"], "best_3_levels": d["depth3"]}, "contracts (average book size, front month outright)",
                              "2018, RTH 7:00 a.m.-4:00 p.m. CT", LIQ18, d["depth_q"],
                              "Columns: best level 2016, 2017, 2018, % growth; best 3 levels 2016, 2017, 2018, % growth. Not split by side; definition per CME. No later figure found." + (" ZT figure predates the early-2019 tick halving." if code == "ZT" else ""))
    o["touch_queue_size"] = F(d["depth"], "contracts", "2018 RTH", LIQ18, d["depth_q"],
                              "Same as depth_best_level (average displayed size at the best level); no separate queue statistic published. ZN trade size: arXiv 2409.12721 'ZN 16.01 2' (mean, median contracts, 2024-04-09)." if code == "ZN" else "Same as depth_best_level; no separate queue statistic published.")
    o["brokertec_link"] = F("Cash Treasuries trade on BrokerTec (CME Group; on CME Globex since 2021-02-01); futures and cash share price discovery; deliverable basket links futures to cash notes/bonds",
                            None, None, MICRO_FILING + "; " + P + "feds_2018-065_price_pressure_term_structure.pdf.txt",
                            "On February 1, 2021, BrokerTec cash Treasuries transitioned to CME Globex.",
                            "See A1_rates.md F11.")
    o["jump_frequency"] = F(None, "days per year with |daily return| > 4 SD", "2019-2024", "reports/stage_e28_briefs/A0_contract_stats.md", None,
                            "Owned-bar counts are A0's (A0_contract_stats.md lines 148-155); not computed here. No published count found.")
    return common_tail(o, code, d["research"], d["auction_q"])


def yieldfut(code, d):
    o = {"candidate": code, "family": "rates"}
    o["product_name"] = F(f"Micro {d['tenor']} Yield Futures (titled '{d['tenor']} Yield Futures' since 2024-02-05)", None, None, MICRO_FILING,
                          f"Micro {d['tenor']} Yield Futures {code} {d['ch']}",
                          "Title change: CBOT 24-116 (cftc_rules02132411742.pdf.txt) 'Effective Monday, February 5, 2024, the Exchange implemented administrative amendments to the contract title of all Micro Yield futures contracts'.")
    o["product_code"] = F(code, None, None, MICRO_FILING, "CME Globex: 2YY, 5YY, 10Y, 30Y", None)
    o["tick_size"] = F(0.001, "index points of yield (0.1 basis point)", None, MICRO_FILING,
                       "shall be 0.001 Index points, equal to $1.00 per contract, or $1000 per Index point", "Rulebook text in the filing, Rule 80102.C-83102.C; spec table: 'All delivery months: 0.001 Index points (1/10th basis point per annum) =' $1.00.")
    o["tick_value"] = F(1.00, "USD per contract", None, MICRO_FILING, "Tick Size $1.00 (1/10th of 1 bp)", None)
    o["contract_size"] = F("$1,000 x index points ($10 DV01)", None, None, MICRO_FILING, "CONTRACT UNIT $1,000 x Index points ($10 DV01)", None)
    o["settlement"] = F("cash-settled to the BrokerTec US Treasury benchmark (3:00 p.m. ET VWAY) of the on-the-run issue; 2 nearest monthly contracts; terminates last business day of the month",
                        None, None, MICRO_FILING, "Cash-Settled to BrokerTec benchmark",
                        "'The Contracts settle to the most recently auctioned On-the-Run CUSIP at each tenor, which updates monthly and the expectation is that the front contract month will dominate trading'.")
    o["launch_date"] = F("2021-08-16", "trade date", None, MICRO_FILING,
                         "effective on Sunday, August 15, 2021, for trade date Monday, August 16, 2021", None)
    a23, n22, o23, n23, y26, s26 = d["adv"]
    if code == "5YY":
        g = F(None, None, "2023-11-01..2024-02-29", ADV_NOV23, d["adv_q_nov"],
              "Launched 2021-08-16 and listed continuously (brief: launch before 2023-11 and continuous listing suffice), but published ADV was 0 in Nov 2023 and 0.45 in Oct 2023, and OI 0 in Feb-Mar 2024 ('5Y YIELD 0 0 - 0 -'); trading on >= 60 dates in the window is doubtful. Daily trade-date counts not read (market data rule).")
    elif code == "30Y":
        g = F(None, None, "2023-11-01..2024-02-29", ADV_NOV23, d["adv_q_nov"],
              "Launched 2021-08-16 and listed continuously, but published ADV only 48 in Nov 2023 and OI 29 (Feb 2024) / 22 (Mar 2024); whether trades occurred on >= 60 dates is not established from published aggregates.")
    elif code == "2YY":
        g = F(True, None, "2023-11-01..2024-02-29", ADV_NOV23, d["adv_q_nov"],
              "Launch 2021-08-16 and continuous listing (the brief's sufficient condition). ADV 213 in Nov 2023 and OI ~500 (Feb-Mar 2024) are low; per-date trade counts not read.")
    else:
        g = F(True, None, "2023-11-01..2024-02-29", ADV_NOV23, d["adv_q_nov"],
              "Launch 2021-08-16 and continuous listing; ADV 7,282 in Nov 2023.")
    o["globex_60_dates_in_2023-11..2024-02"] = g
    o["match_algorithm"] = F("FIFO", None, None, MICRO_FILING, "F - FIFO", "Exhibit 2 table cell labelled 'CME GLOBEX MATCHING ALGORITHM' (label split over three lines in the text layer).")
    o["trading_hours"] = F("Sunday-Friday 6:00 p.m. - 5:00 p.m. ET (5:00 p.m. - 4:00 p.m. CT); Mon-Thu 5:00-6:00 p.m. ET maintenance", None, None,
                           MICRO_FILING, "Sunday - Friday 6:00 - 5:00 p.m. ET (5:00 - 4:00 p.m. CT).", "Exhibit 2, row CME Globex; next cell: 'Monday - Thursday 5:00 - 6:00 p.m. ET (4:00 - 5:00 p.m. CT) daily maintenance period'.")
    o["price_limits"] = F({"daily_limit": None, "dynamic_variant": "20 basis points", "halt": "2-minute halt (Rule 589.D)"}, None,
                          "Rule 589 table Wayback capture 2024-10-01; listing filing 2021", SPFL,
                          f"{d['tenor']} Yield Futures | {d['ch']} | {code} | Primary | Primary | 20 basis points",
                          "Same 20 bp variant in the 2021 listing filing Appendix D. 20 bp = 200 ticks of 0.1 bp.")
    o["adv_published_latest"] = F({"YTD_Jan-Sep_2026": y26, "Sep_2026": s26}, "contracts per day", "Jan-Sep 2026", ADV_SEP26, d["adv_q_sep"],
                                  "Row label in report '" + d["adv_q_sep"].split(" ")[0] + " YIELD'.")
    o["adv_2022_11_2023_10"] = F({"YTD_Jan-Aug_2023": a23, "Nov_2022": n22, "Oct_2023": o23}, "contracts per day",
                                 "2022-11..2023-10 (pieces published)", ADV_AUG23 + "; " + ADV_NOV23,
                                 d["adv_q_aug"] + " || " + d["adv_q_nov"], "No owned bars (A0 line 211).")
    o["open_interest"] = F({"Mar_2023": d["oi"][0], "Oct_2025": d["oi"][1]}, "contracts, month-end", "Mar 2023; Oct 2025",
                           OI_MAR24 + "; " + OI_OCT25, d["oi_q"], None)
    o["retail_share"] = F(None, "% of volume", None, P + "mondovisione_cme_micro_yield_launch_2021-06-09.html.txt",
                          "These innovative, micro-sized contracts will provide market participants – from institutions to sophisticated, active, individual traders – exposure to the yield of on-the-run",
                          "No retail percentage published in any file found (CME launch, 30k and 1M-contract releases, CBOT filings). CME targets individual traders among others; it does not describe the product as predominantly retail.")
    o["commercial_hedger_share"] = HEDGER_TFF
    if d["tff"]:
        o["tff_category_shares"] = tffcats("10Y", "MICRO 10 YEAR YIELD - CHICAGO BOARD OF TRADE")
        o["nonreportable_share"] = nonrep("10Y", "MICRO 10 YEAR YIELD - CHICAGO BOARD OF TRADE")
        o["nonreportable_share"]["note"] += " Published only in weeks that met CFTC reporting criteria (32 of 53 weeks in 2022-11..2023-10; 34 weeks in the latest window)."
    else:
        miss = F(None, "% of open interest", "2022-11..2026-10", P + "cftc_tff_04_market_list.json; " + P + "cftc_tff_rates_market_list.json", None,
                 "No CFTC TFF rows for this contract since 2022-11 (below reporting thresholds); the only micro yield in TFF is 'MICRO 10 YEAR YIELD' (04360Y).")
        o["tff_category_shares"] = miss
        o["nonreportable_share"] = miss
    o["market_maker_program"] = F(True, None, "2021-08-16 .. 2028-02-29 (successive extensions)", MM23 + "; " + MM26,
                                  "Micro 2-Year Yield Futures (“2YY”), Micro 5-Year Yield Futures (“5YY”), Micro 10-Year Yield Futures (“10Y”), and Micro 30-Year Yield Futures (“30Y”) traded on Globex (“Products”).",
                                  "Micro Treasury Yield Futures Market Maker Program / Yield Futures Market Maker Program; in force through the pilot window. For " + code + ": " + d["mm"] + ". See A1_rates.md F7.")
    o["hft_automated_share"] = F(None, "% of volume", None, None, None,
                                 "No automated or HFT share published for the micro yields (Haynes-Roberts and JSR predate them). Market makers present by program (F7).")
    if code == "10Y":
        o["median_spread_ticks_main"] = F(1.67, "ticks (average, not median; 0.167 bp / 0.1 bp tick)", "2024 (H1), RTH 7:00 a.m.-4:00 p.m. CT",
                                          P + "cme_article_2023_yield_futures_macro_events.html.txt",
                                          "In 2024, the average bid-ask spread at the top of book (TOB) has been 0.167 bps during RTH (regular trading hours: generally 7:00 a.m. – 4:00 p.m. CT), while the minimum tick size is 0.1 bps.",
                                          "CME marketing article (Wayback copy). Average daily range 'All other Days 8.17' bps in the same table.")
    else:
        o["median_spread_ticks_main"] = F(None, "ticks", None, None, None,
                                          "No published spread found (searched CME articles, MM program filings, one WebSearch on micro yield spreads). MM program obligations bound quoted widths only for participants meeting them, and for this tenor only via spreads against 10Y.")
    o["depth_best_level"] = F(None, "contracts", None, MM23, None,
                              "No published depth figure. MM program minimum sizes (10Y outright Tier 1: 10 contracts; Tier 2: 150; ETH: 5) are program terms, not measured depth.")
    o["touch_queue_size"] = F(None, "contracts", None, None, None, "Not published.")
    o["brokertec_link"] = F("Final settlement to the BrokerTec US Treasury Benchmark (15-minute VWAY of on-the-run cash trades before 3:00 p.m. ET); daily settlement 30-second VWAP before 2:00 p.m. CT",
                            None, None, MICRO_FILING,
                            "The final settlement value, applied on the last business day of the month, will be determined by the 3:00 p.m. ET BrokerTec US Treasury Benchmark1, or latest available fixing.",
                            "Price is yield, so it moves opposite to " + d["cousin"] + " futures prices. See F11.")
    o["jump_frequency"] = F(None, "days per year with |daily return| > 4 SD", "2019-2024", None, None,
                            "No owned bars (A0) and no published count found; product launched 2021-08-16, so 2019-2021 do not exist for it. The full-size cousin's counts are in A0.")
    research = ("No study on this product found. Evidence on the full-size cousin " + d["cousin"] +
                " (FAM relation, different design): see F12 R1-R3, R7-R9. CLASS: R10, R11.")
    return common_tail(o, code, research, d["auction_q"])


out = [treasury(c, d) for c, d in TREAS.items()] + [yieldfut(c, d) for c, d in YIELDS.items()]
order = ["2YY", "5YY", "10Y", "30Y", "ZT", "ZF", "ZN", "ZB"]
out.sort(key=lambda o: order.index(o["candidate"]))
json.dump(out, open("A1_rates.json", "w"), indent=1, ensure_ascii=False)
print(len(out), [o["candidate"] for o in out], len(out[0]))
