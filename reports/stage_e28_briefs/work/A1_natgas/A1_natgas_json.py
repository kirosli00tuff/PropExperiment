"""A1_natgas: write reports/stage_e28_briefs/A1_natgas.json (one object per candidate, every field as
{value, unit, window, source_file, quote, note}). Facts are transcribed from A1_natgas.md; nothing is scored."""
import json
import sys

P = "reports/stage_e28_briefs/pages/A1_natgas/"
OUT = sys.argv[1]


def f(value, unit=None, window=None, src=None, quote=None, note=None):
    if src is not None and not src.startswith("reports/"):
        src = P + src
    return {"value": value, "unit": unit, "window": window, "source_file": src, "quote": quote, "note": note}


def u(searched, note=None):
    return f(None, note=("UNKNOWN. Searched: " + searched + (" " + note if note else "")))


EIA = f(1, "scheduled product-specific high-impact releases per week", "current", "eia_wngsr_schedule.html.txt",
        "The standard release time and day of the week will be at 10:30 a.m. eastern time on Thursdays with the following exceptions.",
        "EIA Weekly Natural Gas Storage Report; 10:30 ET = 07:30 PT, inside the main session. Impact: Linn and Zhu 2004 "
        "(linn_zhu_2004_JFM_ou.txt lines 47-49): 'the weekly gas storage report announcement was responsible for considerable "
        "volatility at the time of its release and that volatility up to 30 minutes following the announcement was also higher "
        "than normal.' No second weekly gas-specific release found.")
HOURS = f("Sun-Fri 17:00-16:00 CT, 60-minute daily halt from 16:00 CT (Sun-Fri 15:00-14:00 America/Vancouver)", None,
          "current", "cme_faq_MNG.html.txt",
          "CME Globex: Sunday – Friday: 5:00 p.m. to 4:00 p.m. Central Time (CT) Monday – Friday: 60-minute daily trading halt beginning at 4:00 p.m. CT",
          "One TRADING SCHEDULE row shared by MNG, QG and NG in the FAQ comparison table.")
WEEKEND = f(False, "underlying trades while Globex is closed (crypto-style)", "current", "cme_faq_MNG.html.txt",
            "Sunday – Friday, 6:00 p.m. – 5:00 p.m. ET, with a trading halt from 5:00 p.m. ET – 6:00 p.m. ET.",
            "Globex closed Fri 16:00 CT to Sun 17:00 CT. No listed Henry Hub instrument trading through the weekend was found "
            "(reader's note, not sourced). Weekend news still gaps the Sunday open: Borovkova and Mahakena 2015 abstract "
            "(vu_borovkova_mahakena_landing.html.txt line 28): 'the arrival of news in non-trading periods causes overnight returns'.")
LIMIT_DAYS = u("CME and CFTC filings (SER-8569, NYMEX 2018 emergency action, 2020 DCB 15% filing); no per-day list of DCB "
               "triggers or limit hits 2019-2024 in any saved source.",
               "2018 filing: limits widened 'in light of recent natural gas price movements'; 2020 filing: increase 'intended to "
               "reduce market interruptions'. These show limits were reached before 2020 but give no day count.")
DCB = f("dynamic circuit breakers (NYMEX Rule 589), no hard daily limit; 15% since trade date 2020-04-06 (7% before); "
        "2-minute monitoring period then a 2-minute halt", None, "2020-04-06..current", "cme_SER8569.txt",
        "Effective Sunday, April 5, 2020 for trade date Monday, April 6, 2020 ... NYMEX is increasing the dynamic circuit breakers for the energy contracts from 7% to 15%.",
        "Rule 589 text in cftc_ptc032320_nymex_dcb15.txt lines 164-205.")
RESEARCH = [
    {"study": "Haynes and Roberts 2015; 2019 Update #2 (CFTC OCE)", "relation": "same product (NG)", "result": "descriptive (automation shares); not a predictability test", "source_file": P + "cftc_ats_update2_2019.txt", "evidence": "full text"},
    {"study": "Betancourt, Rodriguez and Boyd, arXiv 1710.01415 (JRSS-C 2019), NYMEX NG 2005-2008", "relation": "same product", "result": "positive for predicting future trader-to-trader transactions; not a price or order-book signal", "source_file": P + "arxiv_1710.01415_betancourt_NG_networks.txt", "evidence": "full text"},
    {"study": "Masteika and Vaitonis 2015, LNBIP, HFT calendar-spread statistical arbitrage on NYMEX NG", "relation": "same product", "result": "positive ('Statistical arbitrage and HFT has given positive results'); inter-contract spread rule, cost treatment unknown", "source_file": P + "openalex_masteika_vaitonis_2015.json", "evidence": "abstract only [unverified]"},
    {"study": "Linn and Zhu 2004, J. Futures Markets, storage report and intraday volatility", "relation": "same product (pit era, 1999-2002)", "result": "volatility event effect; not directional, not order-book", "source_file": P + "linn_zhu_2004_JFM_ou.txt", "evidence": "full text"},
    {"study": "Prokopczuk, Wese Simen and Wichmann 2021, Energy Journal, announcement-day returns", "relation": "same product (front month)", "result": "positive directional event drift after costs (abstract); not order-book", "source_file": P + "openalex_prokopczuk_2021_EJ.json", "evidence": "abstract only [unverified]"},
    {"study": "Borovkova and Mahakena 2015, Quantitative Finance, news, volatility and jumps", "relation": "same product", "result": "news Granger-causes jumps; not order-book", "source_file": P + "vu_borovkova_mahakena_landing.html.txt", "evidence": "publisher abstract [unverified beyond abstract]"},
    {"study": "Chevallier and Sevi 2012, Energy Economics (WP), volume-volatility, NYMEX NG and CL", "relation": "same product", "result": "contemporaneous volume-volatility relation; not predictive", "source_file": P + "economix_chevallier_sevi_2011_vol_volume.txt", "evidence": "full text"},
    {"study": "Pinto-Gutierrez 2012, SSRN 2139767, LOB information content in 'the electronic energy market'", "relation": "unknown market", "result": "unknown", "source_file": P + "openalex_pinto_gutierrez_2012.json", "evidence": "title only [unverified]"},
    {"study": "Benato, MSc thesis Padova, LOB information content, EEX Germany Baseload power futures", "relation": "asset class only (energy, not CME)", "result": "positive in-sample, small ('even if it appears to be little'); no costs", "source_file": P + "unipd_benato_lob_energy_thesis.txt", "evidence": "full text"},
    {"study": "CL studies collected by A1_crude (Raman-Robe-Yadav EMMs; Rousse-Sevi pre-EIA order flow; Roberts 2018 depth; Lalor-Swishchuk adverse selection)", "relation": "close cousin (CME Globex energy)", "result": "pre-release buyer-initiated order flow before EIA (informed trading); no CL OFI or queue-imbalance price-prediction study found", "source_file": "reports/stage_e28_briefs/A1_crude.md", "evidence": "cited from A1_crude, lines 101-178"},
    {"study": "ES OFI studies collected by C2_OFI", "relation": "futures broadly (CME Globex equity index)", "result": "positive: 'both price and flow impacts are significant at the one-second horizon'", "source_file": "reports/stage_e28_briefs/C2_OFI.md", "evidence": "cited from C2_OFI line 1032"},
    {"study": "Program-internal E.12 Gate 0 and E.18 C1b replication (not published)", "relation": "same product (NG 1-minute bars)", "result": "null: 'The best pair (NG h60, t 2.51) is not evidence after Holm'; replication 'C1b FAIL (E.18)'", "source_file": "reports/stage_e28_briefs/C1_inventory.md", "evidence": "program records, lines 91 and 213"},
]
RESEARCH_NOTE = ("No study of order-flow imbalance, queue imbalance, trade-sign predictability or passive market-making "
                 "profitability on NG, QG or MNG was found, and no study showing such patterns absent. Searches: 11 OpenAlex "
                 "queries, 2 arXiv API queries, 4 WebSearch queries (see A1_natgas.md F14).")
FAMILY_NOTE = "Family facts: A1_natgas.md section F; this object repeats them per candidate."

MNG = {
    "candidate": "MNG", "family": "natural gas (Henry Hub)", "family_note": FAMILY_NOTE,
    "product_name": f("Micro Henry Hub Natural Gas futures", None, "current", "cme_faq_MNG.html.txt", "PRODUCT CODE MNG QG MNO MN1; MN2; MN3; MN4; MN5 NG", "NYMEX rulebook chapter 440"),
    "code": f("MNG", None, "current", "cftc_ptc0926237029_MNG_launch.txt", "Micro Natural Gas Futures (MNG)", None),
    "contract_size": f(1000, "MMBtu", "current", "nymex_rulebook_ch440_MNG.txt", "The contract quantity shall be 1,000 MMBtu.", "1/10 of NG; financially settled"),
    "tick_size": f(0.001, "USD per MMBtu", "current", "nymex_rulebook_ch440_MNG.txt", "The minimum price fluctuation shall be $0.001 per MMBtu.", None),
    "tick_value": f(1.00, "USD per contract", "current", "cftc_ptc0926237029_MNG_launch.txt", "Value per Tick $1.00", None),
    "launch_date": f("2023-11-06", "trade date", None, "cme_faq_MNG.html.txt", "Starting trade date November 06, 2023, Micro Henry Hub Natural Gas futures and options will be available for trading on CME Globex", "50,000 contracts traded by 2023-11-08 (cme_pr_20231108_MNG_50k.html.txt line 48)."),
    "pilot_window_globex_60_dates": f(None, "boolean", "2023-11-01..2024-02-29", "cme_faq_MNG.html.txt", "Starting trade date November 06, 2023", "Launched after 2023-11-01, so the launch-before-2023-11 shortcut does not apply. 79 weekday trade dates 2023-11-06..2024-02-29 (reader's calendar count, 5 holidays removed); continuous trading on each not verified; no market data read. Needs a definition/statistics check by the lead."),
    "matching_algorithm": f("FIFO", None, "current", "cftc_ptc0926237029_MNG_launch.txt", "CME Globex F-FIFO Matching Algorithm", "FAQ Q10 (cme_faq_MNG.html.txt line 149): 'Micro Henry Hub futures and options use a FIFO (first in, first out) algorithm, identical to their standard-sized counterparts.'"),
    "trading_hours": HOURS,
    "price_limits": f(DCB["value"], None, DCB["window"], "nymex_rulebook_ch440_MNG.txt", "the contract shall be subject to special price fluctuation limits as set forth in Rule 589", "FAQ Q11: 'Micro Henry Hub futures have dynamic price fluctuation limits (circuit breakers) just like their standard-sized counterparts.' MNG's row in the Rule 589 table is an image in the filing."),
    "limit_hit_days_2019_2024": LIMIT_DAYS,
    "adv_latest": f(14609, "contracts per day", "October 2025", "cme_ADV_report_NYMEX_COMEX_202511snap.txt", "NATURAL GAS PHY MNG 14,609 7,631.78 91.4% 13,095.76 11.6% 13,781 5,178.97 166.1%", "Exchange total, all venues. YTD Jan-Oct 2025 13,781; YTD Jan-Oct 2024 5,178.97 (overlaps pilot months Jan-Feb 2024; aggregate published figure). No MNG row in the Sep 2026 group report."),
    "adv_ytd_2025": f(13781, "contracts per day", "2025-01..2025-10", "cme_ADV_report_NYMEX_COMEX_202511snap.txt", "NATURAL GAS PHY MNG 14,609 7,631.78 91.4% 13,095.76 11.6% 13,781 5,178.97 166.1%", None),
    "adv_2022_11_2023_10": f(None, "contracts per day", "2022-11..2023-10", None, None, "Not applicable: MNG not listed before 2023-11-06."),
    "open_interest_latest": f(4890, "contracts", "end of May 2024", "cme_OI_report_NYMEX_COMEX_202406snap.txt", "NATURAL GAS PHY MNG 4,890 0 - 4,896 -0.1%", "Latest NYMEX OI report on Wayback."),
    "retail_share": u("one WebSearch for CME retail share of natural gas futures; CME investor pages blocked from this IP.", "Launch release (cme_pr_20230927_MNG_launch.html.txt line 50), IBKR: micros 'continue to be a popular way for our active trader clients to manage their exposure with less upfront commitment.'"),
    "commercial_hedger_share_cot": u("CFTC disaggregated futures-only files 2022-2023 (pre-2023-11 rows only): no MNG market; later reports not read under the pilot-window rule."),
    "nonreportable_share_cot": u("same as commercial_hedger_share_cot"),
    "market_maker_or_incentive_programs": f("none found", None, "launch filing 2023-09", "cftc_ptc0926237029_MNG_launch.txt", "CME Globex $0.30 $0.60", "Launch filing has no incentive or market-maker program; fee exhibit: Globex $0.30 member / $0.60 non-member per side, facilitation fee $0.06. One WebSearch on cftc.gov filings found only NG and look-alike programs. Not exhaustive (CME rule-filing pages blocked)."),
    "hft_automated_share": u("CFTC Haynes and Roberts 2015, 2017, 2019 tables: NG only, all before MNG existed."),
    "spread_median_ticks_by_session": u("CME Liquidity Insights (NG only), CME Liquidity Tool (login, blocked), OpenAlex and WebSearch for spread studies."),
    "depth_best_level": u("same as spread; no MNG source."),
    "touch_queue_size": u("same as spread."),
    "volume_per_minute": u("owned by A0; no owned MNG bars before 2023-11 (A0_contract_stats.md line 212)."),
    "scheduled_releases_per_week": EIA,
    "weekend_gap_exposure": WEEKEND,
    "jump_frequency": f(None, "days per year with |return| > 4 SD", "2019-2024", "reports/stage_e28_briefs/A0_contract_stats.md", None, "Owned by A0; no owned MNG bars before 2023-11."),
    "expiry_roll": f("monthly; last trade 1 business day before NG's expiration; 24 serial months listed", None, "current", "cme_faq_MNG.html.txt", "Trading terminates one (1) business day prior to the expiration of the corresponding contract month of the Henry Hub Natural Gas Futures contract (NG).", "FAQ Q4: 'There are 24 serial contract months listed'. Fungible with QG for clearing (FAQ Q12)."),
    "microstructure_research": f(RESEARCH, None, None, None, None, RESEARCH_NOTE + " For MNG all NG studies are 'its full-size version'."),
}

QG = {
    "candidate": "QG", "family": "natural gas (Henry Hub)", "family_note": FAMILY_NOTE,
    "product_name": f("E-mini Henry Hub Natural Gas futures (CME report label 'MINY NATURAL GAS')", None, "current", "nymex_rulebook_ch402_QG.txt", "The contract quantity shall be 2,500 MMBtu", "NYMEX rulebook chapter 402"),
    "code": f("QG", None, "current", "cme_ja_QG.html.txt", "CME Globex: QG 清算: QG", None),
    "contract_size": f(2500, "MMBtu", "current", "nymex_rulebook_ch402_QG.txt", "The contract quantity shall be 2,500 MMBtu", "1/4 of NG; financially settled. The 2002 launch contract was 4,000 MMBtu."),
    "tick_size": f(0.005, "USD per MMBtu", "current", "nymex_rulebook_ch402_QG.txt", "$0.005 per MMBtu ($12.50 per Contract)", "5 times NG's tick in price."),
    "tick_value": f(12.50, "USD per contract", "current", "nymex_rulebook_ch402_QG.txt", "$0.005 per MMBtu ($12.50 per Contract)", None),
    "launch_date": f("2002-06-17", "first Globex trade date (as e-miNY natural gas)", None, "reports/stage_e28_briefs/pages/A1_crude/mondovisione_2002_eminy_begin_june17.html.txt", "e-miNY crude oil and natural gas contracts will begin trading on CME's GLOBEXâ electronic trading platform on June 17.", "Announcement dated 30/05/2002 (saved by A1_crude). Contract size later changed from 4,000 to 2,500 MMBtu at a date not found."),
    "pilot_window_globex_60_dates": f(True, "boolean", "2023-11-01..2024-02-29", "cme_chadv23_372_NG_QG_spread.txt", "there is no change to the outright futures trade tick which remains at 0.005", "Launch before 2023-11 and continuous listing; the NG:QG spread listed from trade date 2024-01-22 requires a listed QG outright. Activity on each date not verified (no market data read)."),
    "matching_algorithm": u("CME client wiki matching page, Databento CME matching blog, NYMEX 2018 algorithm filing, one WebSearch; QG Wayback spec page 404."),
    "trading_hours": f(HOURS["value"], None, "current", "cme_ja_QG.html.txt", "日曜日―金曜日：6:00 p.m. - 5:00 p.m. (5:00 p.m. - 4:00 p.m. シカゴ時間/CT) ただし、5:00 p.m. (4:00 p.m. CT) から60分間は取引休止", "CME Japanese-language QG page (line 121)."),
    "price_limits": f(DCB["value"] + "; QG is 'Associated' with NG", None, DCB["window"], "cme_SER8569.txt", "E-mini Natural Gas Futures 402 QG Associated NG", None),
    "limit_hit_days_2019_2024": LIMIT_DAYS,
    "adv_latest": f(2961, "contracts per day", "September 2026", "cme_ADV_report_CMEG_202610snap.txt", "MINY NATURAL GAS 2,961 2,877.29 2.9% 2,299.62 28.8% 3,937 4,618 -14.7%", "YTD Jan-Sep 2026 3,937; YTD Jan-Sep 2025 4,618. Oct 2025 3,565 and YTD Jan-Oct 2025 4,502 (cme_ADV_report_NYMEX_COMEX_202511snap.txt line 230)."),
    "adv_ytd_2026": f(3937, "contracts per day", "2026-01..2026-09", "cme_ADV_report_CMEG_202610snap.txt", "MINY NATURAL GAS 2,961 2,877.29 2.9% 2,299.62 28.8% 3,937 4,618 -14.7%", None),
    "adv_2022_11_2023_10": f(11317, "contracts per day", "2023-01..2023-08 (closest published window found)", "cme_ADV_report_CMEG_202309snap.txt", "MINY NATURAL GAS 8,340 16,712.52 -50.1% 7,409.95 12.6% 11,317 15,732 -28.1%", "Aug 2023 8,340; YTD Jan-Aug 2022 15,732. No report covering exactly 2022-11..2023-10 found."),
    "open_interest_latest": f(10448, "contracts", "end of May 2024", "cme_OI_report_NYMEX_COMEX_202406snap.txt", "MINY NATURAL GAS QG 10,448 14,136 -26.1% 13,881 -24.7%", "End Aug 2023: 9,044 (cme_OI_report_NYMEX_COMEX_202310snap.txt line 23)."),
    "retail_share": u("one WebSearch for CME retail share of natural gas futures."),
    "commercial_hedger_share_cot": u("CFTC disaggregated futures-only 2022-2023: no QG market; code 03565B (2,500 MMBtu) matches NN Henry Hub Swap by open interest (417,298 vs QG 9,044 in Aug 2023)."),
    "nonreportable_share_cot": u("same as commercial_hedger_share_cot"),
    "market_maker_or_incentive_programs": u("one WebSearch on cftc.gov NYMEX filings; found only NG (deferred spreads and strips) and Henry Hub look-alike programs."),
    "hft_automated_share": u("CFTC Haynes and Roberts tables list 'Natural Gas (Henry Hub)' only; whether QG is pooled is not stated."),
    "spread_median_ticks_by_session": u("CME Liquidity Insights (NG only), CME Liquidity Tool (login, blocked), OpenAlex and WebSearch."),
    "depth_best_level": u("same as spread."),
    "touch_queue_size": u("same as spread."),
    "volume_per_minute": u("owned by A0; no owned QG bars before 2023-11 (A0_contract_stats.md line 212)."),
    "book_links": f("NG:QG 1:4 intercommodity spread on Globex from trade date 2024-01-22, spread tick 0.00025", None, "2024-01-22..", "cme_chadv23_372_NG_QG_spread.txt", "NG:QG 1:4 0.00025", "Whether implied prices from the spread are disseminated into the QG outright book is not stated."),
    "scheduled_releases_per_week": EIA,
    "weekend_gap_exposure": WEEKEND,
    "jump_frequency": f(None, "days per year with |return| > 4 SD", "2019-2024", "reports/stage_e28_briefs/A0_contract_stats.md", None, "Owned by A0; no owned QG bars before 2023-11."),
    "expiry_roll": f("monthly; last trade the business day before NG's last trading day", None, "current", "cme_faq_MNG.html.txt", "Trading shall cease on the business day immediately preceding the last day of trading in the current delivery month of the Henry Hub Natural Gas Futures contract (NG).", "Fungible with MNG for clearing (FAQ Q12)."),
    "microstructure_research": f(RESEARCH, None, None, None, None, RESEARCH_NOTE + " For QG all NG studies are 'its full-size version'."),
}

NG = {
    "candidate": "NG", "family": "natural gas (Henry Hub)", "family_note": FAMILY_NOTE,
    "product_name": f("Henry Hub Natural Gas futures (CME report label 'NATURAL GAS PHY')", None, "current", "nymex_rulebook_ch220_NG.txt", "The unit of trading shall be 10,000 MMBtu.", "NYMEX rulebook chapter 220; physically delivered."),
    "code": f("NG", None, "current", "cme_SER8569.txt", "Henry Hub Natural Gas Futures 220 NG Primary Primary", None),
    "contract_size": f(10000, "MMBtu", "current", "nymex_rulebook_ch220_NG.txt", "The unit of trading shall be 10,000 MMBtu.", None),
    "tick_size": f(0.001, "USD per MMBtu", "current", "nymex_rulebook_ch220_NG.txt", "The minimum fluctuation shall be $0.001 (one tenth of one cent) per MMBtu.", "Inter-commodity spreads on Globex may trade in $0.00025."),
    "tick_value": f(10.00, "USD per contract", "current", "cme_faq_MNG.html.txt", "DOLLAR VALUE OF ONE TICK $1 per contract $12.50 per contract ... $10 per contract", None),
    "launch_date": f("Globex electronic trading from 2006-09-05; listed since 1990 [unverified]", None, None, "arxiv_1710.01415_betancourt_NG_networks.txt", "September 5, 2006, when electronic trading was introduced in this market.", "The 1990 listing date is not in a saved source."),
    "pilot_window_globex_60_dates": f(True, "boolean", "2023-11-01..2024-02-29", "reports/stage_e28_briefs/A0_contract_stats.md", None, "Launch before 2023-11 with continuous listing; owned NG bars from 2010-06-06 (A0 line 188)."),
    "matching_algorithm": f("FIFO", None, "current", "cme_faq_MNG.html.txt", "Micro Henry Hub futures and options use a FIFO (first in, first out) algorithm, identical to their standard-sized counterparts.", "Inferred from the MNG FAQ: NG is MNG's standard-sized counterpart. No NG-specific source read."),
    "trading_hours": HOURS,
    "price_limits": f(DCB["value"] + "; NG is the 'Primary' product", None, DCB["window"], "cme_SER8569.txt", "Henry Hub Natural Gas Futures 220 NG Primary Primary", "2018-11-14 GCC emergency action widened limits from 30 to 50 cents 'in light of recent natural gas price movements' (cftc_ptc111618_nymex_emergency.txt)."),
    "limit_hit_days_2019_2024": LIMIT_DAYS,
    "adv_latest": f(569681, "contracts per day", "September 2026", "cme_ADV_report_CMEG_202610snap.txt", "NATURAL GAS PHY 569,681 475,742.71 19.7% 465,679.71 22.3% 540,414 545,684 -1.0%", "Exchange total, all venues. YTD Jan-Sep 2026 540,414. Oct 2025 557,219 and YTD Jan-Oct 2025 534,766 (cme_ADV_report_NYMEX_COMEX_202511snap.txt line 231). Q4 2025 655,000; Dec 2025 708,000 (mm_cme_2025_annual_adv.html.txt lines 93, 116)."),
    "adv_ytd_2026": f(540414, "contracts per day", "2026-01..2026-09", "cme_ADV_report_CMEG_202610snap.txt", "NATURAL GAS PHY 569,681 475,742.71 19.7% 465,679.71 22.3% 540,414 545,684 -1.0%", None),
    "adv_2022_11_2023_10": f(400923, "contracts per day", "2023-01..2023-08 (closest published window found)", "cme_ADV_report_CMEG_202309snap.txt", "NATURAL GAS PHY 376,529 253,432.35 48.6% 323,929 16.2% 400,923 353,594 13.4%", "Oct 2023: 'approximately 421,000 contracts' (cme_pr_20231108_MNG_50k.html.txt line 50). Owned-bar ADV for 2022-11..2023-10 is A0's (A0_contract_stats.md line 105); not reconciled with CME totals."),
    "open_interest_latest": f(1495281, "contracts", "end of May 2024", "cme_OI_report_NYMEX_COMEX_202406snap.txt", "NATURAL GAS PHY NG 1,495,281 1,371,662 9.0% 1,559,471 -4.1%", "End Aug 2023 1,148,827 (cme_OI_report_NYMEX_COMEX_202310snap.txt line 24). A WebSearch snippet reported a record 1,807,497 on 2026-09-01 [unverified, snippet only]."),
    "open_interest_2022_11_2023_10": f(1189842, "contracts (mean of weekly COT OI)", "2022-11-01..2023-10-31 (53 reports)", "cftc_fut_disagg_txt_2023.zip", None, "Computed by work/A1_natgas/A1_natgas_cot.py from the CFTC disaggregated futures-only files (CFTC code 023651); median 1,186,140."),
    "retail_share": u("one WebSearch for CME retail share.", "Proxy: CFTC small traders (<0.5% of daily volume, not retail) 17.0% automated + 19.1% manual = about 36% of NG volume, 2016-11..2018-10 (cftc_ats_update2_2019.txt line 507: 'Natural Gas (Henry Hub) 35,136 31,291 17.8 17.0 21.7 19.1 565 459 45.6 52.9 11.4 7.8')."),
    "commercial_hedger_share_cot": f(17.6, "% of open interest (producer/merchant, mean of long 14.0 and short 21.3)", "2022-11-01..2023-10-31", "cftc_fut_disagg_txt_2023.zip", None, "Computed (A1_natgas_cot.py). With swap dealers (long 26.4, short 10.5): about 36%. Managed money long 41.0, short 44.4."),
    "nonreportable_share_cot": f(4.7, "% of open interest (mean of long 5.9 and short 3.5)", "2022-11-01..2023-10-31", "cftc_fut_disagg_txt_2023.zip", None, "Computed (A1_natgas_cot.py); small-trader proxy."),
    "market_maker_or_incentive_programs": f("Physical Henry Hub (NG) Market Maker Program for deferred spreads and strips on Globex, 2017-07-01..2024-07-31", None, "2017-07-01..2024-07-31", "cftc_rules071223_NG_MM_program.txt", "The purpose of this Program is to build electronic liquidity in deferred Henry Hub spreads, strips, and strip spreads.", "Obligations: 'quote two-sided markets in the applicable Products, at predetermined average bid/ask spreads and minimum quote sizes during a certain percentage of time-in-market.' Scope is not the front-month outright. Status after 2024-07-31 not found."),
    "hft_automated_share": f(69.9, "% of volume entered by automated trading systems", "2016-11-01..2018-10-31", "cftc_ats_update2_2019.txt", "Energy - Natural Gas Natural Gas (Henry Hub) 175 219 63.3 69.9 33.1 26.9 42.5 50.9 41.6 38.0 12.3 7.9", "63.3% in 2014-11..2016-10. ATS-ATS 50.9%. Large automated traders 52.9% of volume; 76.5% of large ATS volume non-directional over the full day, 34.6% within 1 minute (Table 8, line 585). Passive fills: 'over 90 percent of passive executed corn orders remained in the book longer than one second, as are 85 percent of natural gas futures' (2015 paper, line 596)."),
    "spread_median_ticks_by_session": f("< 1.5 ticks average in non-US hours (Q2 2020); US-hours value not given; medians not found", "ticks", "2020 Q2", "cme_liqinsights_henryhub_2020.html.txt", "Throughout Q2, US spreads remained fairly steady. Though non-US spreads were slightly elevated, they remained below 1.5 ticks on average.", "CME article dated 15 Sep 2020; non-US hours '5 p.m. – 7 a.m. CT'. Average, not median."),
    "depth_best_level": u("CME Liquidity Tool (login, blocked), CFTC ATS papers (no depth tables), OpenAlex/WebSearch for NG depth studies."),
    "touch_queue_size": u("same as depth_best_level."),
    "volume_per_minute": f(None, "contracts per minute", "2022-11..2023-10", "reports/stage_e28_briefs/A0_contract_stats.md", None, "Owned by A0 (line 105: main-session median 99, mean 150.0; overnight median 7, mean 27.7). Not computed here."),
    "scheduled_releases_per_week": EIA,
    "weekend_gap_exposure": WEEKEND,
    "jump_frequency": f(None, "days per year with |return| > 4 SD", "2019-2024", "reports/stage_e28_briefs/A0_contract_stats.md", None, "Owned by A0 (line 142, e.g. '2018: 3/246, 2019: 1/246, 2020: 1/245, 2021: 0/246, 2022: 0/246, 2023: 0/205')."),
    "expiry_roll": f("monthly; last trade the 3rd last business day of the month before delivery; physical delivery", None, "current", "cme_faq_MNG.html.txt", "Trading terminates on the 3rd last business day of the month prior to the contract month.", "Rolls: 'During a futures roll, order-to-execution times increase, with spread quotes on average sitting in the book for a longer period' (cftc_haynes_roberts_2015_automated_trading.txt lines 632-634)."),
    "microstructure_research": f(RESEARCH, None, None, None, None, RESEARCH_NOTE),
}

json.dump([MNG, QG, NG], open(OUT, "w"), ensure_ascii=False, indent=1)
print("wrote", OUT, "candidates", 3, "fields", [len(x) for x in (MNG, QG, NG)])
