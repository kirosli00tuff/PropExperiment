"""IDEAS helper: builds briefs/R2_idea_families.json from sourced facts (no scores, no outcomes).

Every evidence row cites an F2 item id (reports/stage_e32b_briefs/F2_<family>.json), a shared-file id (SB-n), an R1 id
or an on-disk saved page. Quotes are copied from those files. Run: python3 IDEAS_build.py
"""
import json
import os
import subprocess

BRIEFS = "/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e32b_briefs"
OUT = os.path.join(BRIEFS, "R2_idea_families.json")
BALT = "reports/stage_e13_briefs/pages/InfoSource/baltussen_etal_2021_jfe.md"


def ev(src, ids, product, horizon, period, oos, net, finding, sign, verified, venue, quote=None, file=None):
    """One evidence row. sign: positive | null | negative | mixed | volatility_only | absorbed_fast | structure."""
    return {"source": src, "item_ids": ids, "product": product, "horizon": horizon, "period": period,
            "in_or_out_of_sample": oos, "net_of_costs": net, "finding": finding, "sign": sign,
            "verified": verified, "venue_type": venue, "quote": quote, "file": file}


def now_pdt():
    return subprocess.run(["date", "+%Y-%m-%d %H:%M PDT"], capture_output=True, text=True,
                          env={"TZ": "America/Vancouver"}).stdout.strip()


HEADER = {
    "worker": "IdeaFamilies-OpusHigh",
    "stage": "E.32b",
    "spec_sha256": "09ebe6970fcf027009152fa81a414360a015d535b095138cdf65cf1a4eb58635",
    "started_pdt": "2026-10-28 23:10 PDT",
    "websearch_calls": 0,
    "pages_fetched": 0,
    "scope": ("Directional idea families for a one-contract retail system, market orders, holds 5 minutes to the session "
              "close (overnight holds reported apart), on the 47 codes of spec section 0 (NQ excluded, V49). Facts only: "
              "no family is ranked or scored and no product is picked."),
    "sources_read": [
        "reports/stage_e32b_briefs/F2_{crude,natgas,metals,grains,rates,equity,fx,crypto}.md and their JSON T3/T4/T6/T7 items",
        "reports/stage_e32b_briefs/F2_shared_baltussen.json (SB-1..SB-30); F2_shared_cftc_automation.json not used (T2a only)",
        "reports/stage_e32b_briefs/R1_closed_lines.json/.md incl. 'Ambiguous: for lead'",
        "reports/stage_e13_briefs/pages/InfoSource/baltussen_etal_2021_jfe.md (Table 5, mechanism lines 84-90)",
        "reports/stage_e32_methods_brief.md: Front, verdict table, R4 sections 2, 7, 8; M1 sections 0-1 (line ranges)",
        "reports/stage_e28_briefs/C3_lead_draft.md; C2_*.md bottom-line sections scanned (methods only, no 5-minute-plus directional evidence)",
        "reports/stage_e31_inputs/planner_research_notes.md; reports/stage_e32_inputs/planner_research_soy_complex.md (pointers)",
        "docs/DECISIONS.md lines 880-922 (V45 items 3-4); reports/stage_e25_briefs/DF3_treasury_drifts.md (grep)",
        "reports/stage_e20_briefs/shared/barbon_beckmeyer_buraschi_moerke_letf.pdf.txt (abstract lines 27-36)",
    ],
    "cross_family_facts": [
        {"fact": "V38 as amended by V45 item 4: no published post-2015 intraday effect on the 17 E.20 roots exceeds 1.5 x the D8 round trip, except three working-paper effects (pre-refunding ZN, pre-FOMC ZN, ES 3rd-Friday), none with a significant post-2015 estimate.",
         "quote": "no published post-2015 intraday effect on the 17 roots exceeds 1.5 x the D8 round trip, except three working-paper effects whose samples run past 2015, none with a significant post-2015 estimate",
         "file": "docs/DECISIONS.md:910-916 (via R1-19)"},
        {"fact": "E.25: information is priced within 1 to 5 seconds on ES, NQ, ZN and CL (absorption well under 5 minutes for news-driven price moves on these underlyings).",
         "quote": "information is priced within one to five seconds on ES, NQ, ZN and CL",
         "file": "reports/stage_e28_briefs/C3_lead_draft.md:70-71 citing E.25_RETURN.md:330"},
        {"fact": "E.28/E.32: on 1-minute bars every statistically robust directional pattern was worth about 0.1 tick a trade against a 2.1-tick round turn (MES); a published effect sized gross in history fell below the round trip at retail cost in recent data.",
         "quote": "every statistically robust directional pattern is worth about 0.1 tick per trade, against a 2.1-tick round-turn cost",
         "file": "reports/stage_e28_briefs/C3_lead_draft.md:19-20 citing progress.md:902"},
        {"fact": "E.32 methods front: no commodity-futures study shows positive out-of-sample directional predictability net of costs at 1-240 minutes; event families and once-a-day families fail on power over 39 months.",
         "quote": "No commodity-futures study shows positive out-of-sample directional predictability net of costs at 1-240 minutes",
         "file": "reports/stage_e32_methods_brief.md:15-16"},
    ],
    "families": [],
}

FAMILIES = []

# ---------------------------------------------------------------- R2-F01
FAMILIES.append({
    "id": "R2-F01",
    "name": "Market intraday momentum into the close (rest-of-day or first half-hour return predicts the last half-hour)",
    "mechanism": {
        "whose_flow": "Gamma hedgers: option market makers short gamma and leveraged-ETF rebalancing trade in the direction of the day's move before the close (Baltussen et al. 2021); late-informed traders (Gao et al. 2018).",
        "why_predictable": "The hedge size is set mechanically by the day's return and is executed near the close, a known time.",
        "why_retail_edge_could_exist": "The flow is non-informational and large against a one-lot; the open issue is size per trade against cost (R1-14: NQ T1 gross 1.25 ticks against 4.08 cost).",
        "quote": "Hedging short gamma exposure requires trading in the direction of price movements, thereby creating price momentum.",
        "file": BALT + ":84-85",
    },
    "codes": {
        "positive_on_product_or_full_size_sibling": ["MNQ (via NQ, SB-9)", "M2K", "RTY (SB-10)", "MYM", "YM (SB-8)", "ZT (SB-12)", "ZF (SB-13)", "ZN (SB-14)", "ZB (SB-15)", "MGC", "GC (SB-17, R2_OOS 0.08%)", "SIL", "SI (SB-19)", "MNG", "QG", "NG (SB-21)", "M6A", "6A (SB-27, full sample only)"],
        "null_or_negative_on_product": ["CL/QM/MCL (SB-20)", "HG/MHG (SB-18)", "ZL/MZL (SB-22)", "ZC/XC/MZC (SB-23, in sample only)", "ZM/MZM (SB-24)", "ZS/XK/MZS (SB-25)", "ZW/XW/MZW (SB-26)", "6E/M6E (SB-28)"],
        "untested_in_source": ["2YY 5YY 10Y 30Y (yield futures not in the sample)", "BTC MBT ETH MET (no crypto futures; spot only, CRYPTO-17)"],
        "excluded": ["NQ (V49): its rows SB-9/SB-30 are evidence for MNQ only"],
    },
    "horizons": {"intraday": "30 minutes: entry at close-30, exit at the class close (equity cash close; FX pit close 14:00 CT, FX-47; GC 12:00-12:30 CT, METALS-27; NG 14:00-14:30 ET, NATGAS-41; bonds 13:30-14:00 CT, RATES-37)",
                 "overnight": "SB-7: the effect reverts over the next days (R1-18 tested the H6 reversal at 5 and 20 days: closed)."},
    "evidence": [
        ev("Baltussen, Da, Lammers, Martens 2021 JFE 142(1), Table 5 Panel B", ["SB-1", "SB-2", "SB-3", "SB-5"], "asset-class pools (17 equity, 16 bond, 21 commodity, 8 currency futures)", "30 min", "2000-2020 subsample", "in sample (pooled)", "no",
           "beta_ROD x100 (t), R2%: equity 3.98 (6.65) 2.34; bonds 1.53 (3.61) 0.47; commodity 1.04 (2.86) 0.12; currency 0.33 (1.45) 0.04", "positive (equity, bonds, commodity); null (currency)", "full_text", "peer-reviewed",
           "| Equity | 4.97*** (6.06) | 1.67 | 4.83*** (6.02) | 2.42*** (3.82) | 8.89*** (4.11) | 2.73 | 3.98*** (6.65) | 2.34 |", BALT + ":1666-1669"),
        ev("Baltussen et al. 2021, Appendix B product rows", ["SB-8", "SB-9", "SB-10", "SB-12", "SB-13", "SB-14", "SB-15", "SB-17", "SB-19", "SB-21", "SB-27"], "YM, NQ, ER(Russell), TU, FV, TY, US, GC, SV, NG, AD", "30 min", "product start to 2020-05", "in sample + recursive OOS R2 (Clark-West)", "no",
           "R2_OOS: NQ 3.76%, Russell 3.15%, YM 2.18%, ZF 0.93%, NG 0.92%, ZN 0.86%, ZT 0.70%, ZB 0.22%, SI 1.01%, 6A 0.17%, GC 0.08%; all significant", "positive", "full_text", "peer-reviewed", None, "F2_shared_baltussen.json"),
        ev("Baltussen et al. 2021, Appendix B product rows", ["SB-18", "SB-20", "SB-22", "SB-23", "SB-24", "SB-25", "SB-26", "SB-28", "SB-16"], "HG, CL, BO, CN, SM, SY, WC, EC, UB", "30 min", "to 2020-05", "OOS", "no",
           "R2_OOS negative or nil: CL -1.04%, HG -0.25%, UB -3.40%, grains and EC about -0.01 to -0.07%", "null/negative", "full_text", "peer-reviewed", None, "F2_shared_baltussen.json"),
        ev("Baltussen et al. 2021, costs", ["SB-6"], "all", "30 min", "1974-2020", "-", "not net, one sentence on ES", "no cost-adjusted table; ES positive net Sharpe at a one-tick cost (ES not a candidate)", "unknown net", "full_text", "peer-reviewed",
           "Note that we do not consider transaction costs.", "F2_shared_baltussen.json SB-6"),
        ev("Gao, Han, Li, Zhou 2018 JFE (via E.20)", ["EQUITY-36", "EQUITY-37", "EQUITY-20"], "SPY, IWM (other venue, same underlying for RTY/M2K)", "30 min (15:30-16:00 ET)", "1993-2013 (IWM 2000-2013)", "in sample + OOS timing", "SPY net of spread 2005-2013: 6.52%/yr vs 7.96% gross",
           "first-half-hour sign predicts last half-hour; IWM OOS R2 2.43%; FOMC days stronger (20.04%/yr vs 6.24%)", "positive", "reused (E.20 full text)", "peer-reviewed", None, "F2_equity.json"),
        ev("Li, Sakkas, Urquhart 2022 J. Financial Markets", ["EQUITY-38"], "S&P 500 cash (not tradable)", "30 min", "2005-10..2017-12", "in sample", "gross", "6.567%/yr, Sharpe 1.115", "positive", "reused", "peer-reviewed", None, "F2_equity.json"),
        ev("Shen, Urquhart, Wang 2022 Financial Review", ["CRYPTO-17"], "bitcoin spot, 5 exchanges", "last 30 min", "2013-2020", "OOS R2 1.09-1.61%", "breakeven 3/7/10 bp; not profitable at a 25 bp fee", "positive gross", "positive gross / negative at retail spot fee", "full_text", "peer-reviewed",
           "the first half-hour positively predicts the last half-hour return", "F2_crypto.json"),
        ev("Wen et al. 2023 (USO)", ["CRUDE-19"], "USO ETF (crude, other venue)", "last half-hour", "2006-2019", "in sample", "gross", "EIA-day third half-hour predicts last half-hour; other days first half-hour", "positive in sample (product row CL null in Baltussen)", "reused", "peer-reviewed",
           "days with EIA announcements, we can generate an even higher average return of 4.14% per annum", "F2_crude.json"),
        ev("Jin, Kearney, Li, Yang 2020 JFM; DCE study", ["METALS-33", "GRAINS-25", "NATGAS-45"], "SHFE copper; DCE soybean and meal; Chinese commodities", "first -> last half-hour", "2002-2013", "in sample", "gross", "positive slopes (DCE meal 0.052, R2 0.90%)", "positive (other venue)", "full_text", "peer-reviewed", None, "F2_grains.json / F2_metals.json"),
        ev("Adams, Dim, Eraker, Fontaine, Ornthanalai, Vilkov draft 2026", ["EQUITY-39"], "ES (cousin)", "60 min", "2018-01..2024-12", "in sample", "gross", "momentum turns to reversal when dealer net gamma is high: Q4-Q1 -1.777 bp (t -3.93)", "negative (regime/decay)", "reused (full text)", "working paper", None, "F2_equity.json"),
        ev("firmtape blog (dev.to)", ["EQUITY-40"], "SPX", "ROD -> LH", "2022-04..2026-08", "-", "gross", "slope +0.006 (t 0.6), flat every year; conditional on short-gamma closes +0.055 (t 3.1)", "null (pointer)", "reused", "pointer (blog)", None, "F2_equity.json"),
        ev("Rosa 2022 JFM", ["EQUITY-41", "RATES-48"], "index futures per snippet [unverified]", "overnight -> last half-hour", "unknown", "OOS", "-", "predictability disappears out of sample", "negative", "abstract", "peer-reviewed", None, "F2_equity.json"),
        ev("Majorin 2025 Aalto MSc thesis", ["EQUITY-46", "RATES-41", "FX-42"], "20 equity, bond, FX futures", "30 min", "2008-01..2024-10", "-", "net", "patterns persist but mostly not feasible after costs, especially bond and currency futures", "negative net", "abstract", "thesis", None, "F2_rates.json"),
        ev("Program E.20 H6 (R1-14)", ["R1-14"], "NQ at MNQ cost", "30 min (entry 14:30 CT)", "2020-06..2024-02", "registered test r004-E20H6", "net", "T1 gross 1.25 ticks vs 4.08 cost, t -0.53; closed (V38)", "negative net", "reused (program record)", "program", None, "R1_closed_lines.json"),
        ev("Program E.16 H1/H4 (R1-13)", ["R1-13"], "pooled 27 roots incl. YM RTY ZT ZF ZN ZB 6E 6A CL NG GC", "settlement-window intraday; next-day reversal", "2010-07..2024-02 (17 roots); 2019-05..2024-02 (10)", "registered r002-E16", "net", "H1 gross about a quarter of its D8 cost; closed V31", "negative net", "reused", "program", None, "R1_closed_lines.json"),
        ev("E.32 methods brief R4 table", [], "CBOT soybean meal", "first half-hour -> last half-hour", "1982-2020", "OOS", "-", "slope -0.95 (t -1.58), OOS R2 < 0", "null", "reused (E.32)", "peer-reviewed (Baltussen)", "CBOT SM first-half-hour -> last half-hour slope -0.95 (t -1.58), OOS R2 < 0 (Baltussen)", "reports/stage_e32_methods_brief.md:3225"),
    ],
    "absorption_under_5min": "Not applicable as such: the effect is a 30-minute flow pattern. Contrary evidence is decay and regime change (EQUITY-39, -40, -41), not fast absorption.",
    "data_needs": {"schema": "1-minute OHLCV or trades for the signal at close-30 and for exits; MBP-1 or trades for spread and slippage at the close; optional option-gamma (GEX) or leveraged-ETF AUM for conditioning (R1-14 T3 used GEX rows 2020-05-29..2024-02-28)",
                   "history": "one trade a day per product: about 252 trades a year; E.32 front: once-a-day families fail on power over 39 months",
                   "calendars": "per-class close times; half-days; daily settlement windows (equity 15:00 CT since 2020-10-26, EQUITY-48)",
                   "windows_already_read_per_R1": "NQ 2020-06..2024-02 (R1-14); 27 roots 2010-2024 (R1-13); research window 2025-04..2026-06 CP1 ports (R1-03..R1-09)"},
    "r1_overlap": [
        {"id": "R1-14", "how": "same family, NQ (excluded) at MNQ cost, 30 min, T1-T3 incl. GEX conditioning; closed V38"},
        {"id": "R1-13", "how": "E16-H1 settlement-window intraday momentum pooled over 27 roots (incl. YM, RTY, ZT, ZF, ZN, ZB, 6E, 6A, CL, NG, GC) and H4 next-day reversal; closed V31"},
        {"id": "R1-03..R1-09", "how": "CP1 open-to-first-half-hour momentum port tested on every K cluster (MNQ M2K MYM; rates; FX; MCL NG; MGC MHG; grains; MBT); Tier B, closed V40"},
        {"id": "R1-15", "how": "ML search with r_ROD features and decision time F_X - 60 on 17 roots; closed V38"},
        {"id": "R1-18", "how": "H6 reversal direction at 5 and 20 days on NQ; closed V41"},
        {"id": "R1-23", "how": "C2 GEX late-session momentum stopped at its power rule (V27); a stop, not a test (R1 ambiguity)"},
        {"id": "R1-19", "how": "V38/V45 census covers the 17 E.20 roots; ambiguity: V38 says 'on Topstep'"},
    ],
    "open_questions": [
        "No per-product estimate after 2020-05 on any CME candidate; post-2018 equity evidence is regime-dependent (EQUITY-39) or a pointer (EQUITY-40).",
        "No cost-adjusted per-product result; the only net statements are ES (one sentence) and SPY net of spread 2005-2013.",
        "Micro codes, yield futures and mini grains were not in the sample; their price path is the full-size sibling's (settlement-derived), costs differ.",
        "Whether a variant that differs from H6/E16-H1 (other products, conditioning) counts as a 'close variant' under R1 is for the lead and scorer.",
    ],
})

# ---------------------------------------------------------------- R2-F02
FAMILIES.append({
    "id": "R2-F02",
    "name": "Energy inventory release drift or reversal (EIA WPSR for crude, EIA WNGSR for natural gas, API)",
    "mechanism": {
        "whose_flow": "Report digestion by traders after a scheduled inventory surprise; possible overreaction by liquidity demanders followed by correction.",
        "why_predictable": "Fixed release time (WPSR Wednesday 10:30 ET, CRUDE-13; WNGSR Thursday 10:30 ET, NATGAS-24; API Tuesday 16:30 ET, CRUDE-15).",
        "why_retail_edge_could_exist": "Only if the post-release path keeps moving or reverses on a scale of 15 minutes to hours; the first minutes belong to fast traders (NATGAS-27: within 50 ms).",
    },
    "codes": {"crude": ["CL", "QM", "MCL"], "natgas": ["NG", "QG", "MNG"]},
    "horizons": {"intraday": "post-release 5 min to the close; pre-release 85-90 min (NG, needs analyst forecasts)", "overnight": "API release Tuesday 16:30 ET falls after the day session (CRUDE-15); WNGSR storage surprises partly reverse the next week (NATGAS-30, weekly)."},
    "evidence": [
        ev("Luo and Kang (5-minute data)", ["CRUDE-51"], "CL", "10:35-11:00 and 11:00-15:00 ET", "about 2003-2010", "in sample", "-", "inventory shock has no power for returns after the release", "null", "full_text (Firecrawl directQuote extraction)", "paper",
           "we find that the inventory shock has no power to explain the return in the subsequent period after announcement (10:35AM to 11:00AM Wednesday) as well as in the remaining period (11:00AM to 3:00PM Wednesday)", "F2_crude.json"),
        ev("BoC SWP 2020-8", ["CRUDE-14"], "CL", "5, 15, 30 min windows", "2003-2017", "in sample", "-", "estimates at 5, 15 and 30 minutes very close: absorbed within the window", "absorbed_fast", "full_text", "central-bank WP",
           "the point estimates for the shorter and longer window sizes are very close to the benchmark results.", "F2_crude.json"),
        ev("Geman and Li", ["CRUDE-30", "CRUDE-31"], "CL", "about 25 min, then reversal; EIA-day 10:20-10:25 follow strategy", "not stated", "-", "not stated", "effects last about 25 minutes, then revert quickly", "mixed", "abstract", "paper",
           "responds to inventory shock very quickly, with the effects lasting for about twenty-five minutes", "F2_crude.json"),
        ev("Rousse and Sevi", ["CRUDE-52"], "CL", "hours (half reversed after 4 h)", "2007-2014", "in sample", "gross", "over-reaction on positive surprises, partly corrected in the hours after", "reversal (positive for a fade)", "full_text", "paper",
           "days with positive surprises are characterized by a large average price drop of about 0.5% – traders take short positions as inventories are larger than expected – which is partly corrected in the hours following the news release.", "F2_crude.json"),
        ev("Wen et al. 2023 (USO)", ["CRUDE-20"], "USO ETF", "to the end of the day", "2006-2019", "in sample", "gross", "slow adjustment completed at the end of the trading day; declining; absent 2014-2016", "positive in sample, decaying", "full_text", "peer-reviewed",
           "we show that the adjustment process is rather slow and is only completed at the end of the trading day.", "F2_crude.json"),
        ev("Ye and Karali 2015 poster", ["CRUDE-28"], "CL", "15 min", "2013-2014", "in sample", "-", "EIA effect about twice API's", "volatility/level response", "poster", "poster", None, "F2_crude.json"),
        ev("Halova, Kurov, Kucher 2014 JFM", ["NATGAS-25"], "NG", "(-5,+10) min; longer windows similar", "2003-07..2012-06", "in sample", "-", "response within the event window; longer windows add nothing", "absorbed_fast", "full_text", "peer-reviewed", "The results with longer event windows are similar.", "F2_natgas.json"),
        ev("Linn et al. 2017 EIA slides", ["NATGAS-26", "NATGAS-22"], "NG (also gasoline, distillate)", "5-7 min vs 100 min", "2003-2017", "in sample", "-", "5-7 minute response similar to the level at 100 minutes; NG responds to the crude inventory surprise (-0.112)", "absorbed_fast", "full_text", "agency slides", None, "F2_natgas.json"),
        ev("Brigida and Pratt 2019", ["NATGAS-27"], "NG", "first 50 ms", "n/a", "-", "-", "report incorporated within 50 ms; no pre-release informed trading", "absorbed_fast", "abstract", "paper", None, "F2_natgas.json"),
        ev("Farhangdoost and Etienne 2020", ["NATGAS-31"], "NG", "15 min", "n/a", "-", "-", "15-minute impact diminished over time", "decay", "full_text", "conference paper", None, "F2_natgas.json"),
        ev("Prokopczuk, Wese Simen, Wichmann 2021 Energy J.", ["NATGAS-39", "NATGAS-29"], "NG", "(-90,+30) min around WNGSR", "2003-03..2018-12", "in sample", "gross and net", "after 2011 raw 2.91%/yr (p 0.558), net -0.90%", "negative net after 2011", "reused (E.20 full text)", "peer-reviewed",
           "In the more recent period, this has declined to only 3% and a Sharpe ratio of 0.5, which do not withstand transaction and funding costs.", "F2_natgas.json"),
        ev("Gu and Kurov 2018 JFM", ["NATGAS-40"], "NG", "85-90 min before WNGSR, exit 5 min before", "2008-07..2016-01", "in sample", "not stated", "Sharpe 0.84 (1.26 when the predictor is large); needs analyst forecasts", "positive (pre-release)", "reused (full text)", "peer-reviewed",
           "a simple trading strategy that consists of buying (selling) a futures contract 90 minutes before the release time if the predictor is negative (positive), and closing the position 5 minutes ahead of the announcement", "F2_natgas.json"),
        ev("Ederington et al. 2019", ["NATGAS-30"], "NG", "daily, weekly", "n/a", "in sample", "-", "analyst forecasts priced before release; surprises partly reverse next week", "reversal (weekly)", "full_text (exec summary)", "paper", None, "F2_natgas.json"),
        ev("Program K4 screen and E.5 confirmation (R1-06)", ["R1-06"], "MCL (CL bars), NG", "NG storage pre-release, API/EIA pre/post, overreaction fade", "screen 2025-04..2026-06; confirmation NG 2019-05..2024-02, MCL 2021-07..2024-02", "screen + confirmation", "net", "K4-ngpre-01 fails Holm; closed V40", "negative", "reused", "program", None, "R1_closed_lines.json"),
    ],
    "absorption_under_5min": "Strong for NG (NATGAS-25, -26, -27) and for CL at 5-30 minutes (CRUDE-14, CRUDE-51); E.25: CL information priced within 1-5 seconds. Exceptions: hours-scale reversal after positive surprises (CRUDE-52, 2007-2014) and USO slow adjustment (CRUDE-20, in sample, absent 2014-2016).",
    "data_needs": {"schema": "1-minute bars or trades around 10:30 ET; MBP-1 for spread at the release; surprise needs consensus forecasts (not free; Gu-Kurov used analyst forecasts) or EIA/API figures",
                   "history": "about 52 events a year per report", "calendars": "EIA WPSR and WNGSR release dates incl. holiday shifts; API dates"},
    "r1_overlap": [{"id": "R1-06", "how": "K4 tested NG storage pre-release, API/EIA pre/post and overreaction fade on MCL and NG; closed V40"},
                   {"id": "R1-23", "how": "V39 closed 'commodity event drift as a standalone stage' as a direction (crude, metals, natgas); at most an overlay on trend"},
                   {"id": "R1-11/R1-12", "how": "NG h60 near miss (not event-timed) closed V32"}],
    "open_questions": ["No post-2014 CME study shows a post-release mean drift of 5 minutes or more for CL or NG.", "Whether the CRUDE-52 hours-scale reversal survives after 2014 is unknown.", "MFFU makes EIA Tier 1 for energy on some plans (planner pointer, secondary): firm news windows belong to FirmRules."],
})

# ---------------------------------------------------------------- R2-F03
R4 = "reports/stage_e32_methods_brief.md"
FAMILIES.append({
    "id": "R2-F03",
    "name": "USDA and industry report drift or reversal in grains and oilseeds (WASDE, Crop Production, Grain Stocks, Acreage, NOPA crush)",
    "mechanism": {
        "whose_flow": "Report digestion by commercial and speculative traders; slow incorporation of a large surprise (big events) or overshoot and correction (small events).",
        "why_predictable": "Releases at 12:00 ET (11:00 CT) inside the day session since 2013 (GRAINS-22); NOPA monthly at noon ET (E.32 R4, times before 2026 [unverified]).",
        "why_retail_edge_could_exist": "If the 10-60 minute path after the first minutes keeps a sign that is known at entry; no paper reports that entry-time conditional (E.32 R4 section 2).",
    },
    "codes": {"corn": ["ZC", "XC", "MZC"], "soybeans": ["ZS", "XK", "MZS"], "wheat": ["ZW", "XW", "MZW"], "meal_oil": ["ZM", "MZM", "ZL", "MZL"]},
    "horizons": {"intraday": "entry 5-15 min after 11:00 CT, exit at 30-60 min or at the 13:15-13:20 CT close", "overnight": "Crop Progress Mondays 16:00 ET and Export Sales Thursdays 08:30 ET land outside the day session (GRAINS-22); Crop Progress moves close-to-open variability (GRAINS-40, volatility)."},
    "evidence": [
        ev("Anderson, McKenzie, Noyes 2024 NCCC-134 WP", ["GRAINS-18"], "ZC, ZS nearby", "10 min, 30 min, to the day close", "2010-2021, 122 WASDE reports", "in sample", "-", "not significant at 10 min, significant at 30 min; soybean reaction grows to the close; corn mostly done by 30 min", "positive (drift, soybeans)", "full_text", "working paper",
           "We do not find a significant market reaction within the first ten minutes after the report release time. However, we do find significant and directionally appropriate price reactions after 30 minutes.", "F2_grains.json"),
        ev("Huang 2022 dissertation ch. 3 (via E.32 R4)", [], "corn nearby", "1-60 min after release", "2012-06..2019-08, 104 real-time events", "in sample", "-", "about 75% of the 60-min move by 10 min, 90-100% by 35-45 min; direction-known drift after minute 10: big events +0.65%, small events overshoot (-0.10% after 40 min); the conditioning on the 60-minute sign is not tradable", "mixed (conditional, not tradable as stated)", "full_text (E.32)", "dissertation",
           "Notice that during small events the price initially moves in the opposite direction of the final price.", R4 + ":2797, 2852-2876; reports/stage_e32_briefs/pages/R4_events/R4_ideals_usda_release_policy_2022.txt"),
        ev("Joseph and Garcia 2016", ["GRAINS-21"], "ZS", "15-s returns; spike 5-6 min; variance to 30-60 min", "2010-06..2014-05", "in sample", "-", "no systematic under- or overreaction", "null (direction); volatility_only", "full_text", "paper",
           "Return correlations provide little evidence to support systematic under- or overreaction in prices regardless of when the report is rel", "F2_grains.json"),
        ev("Lehecka, Wang, Garcia 2014", ["GRAINS-19", "GRAINS-37"], "ZC", "about 10 min", "2009-07..2012-05", "in sample", "-", "reactions persist about ten minutes; no systematic under- or overreaction", "absorbed_fast / null", "abstract", "peer-reviewed", None, "F2_grains.json"),
        ev("Adjemian and Irwin 2018", ["GRAINS-20"], "grain futures", "few minutes", "2009-2014", "-", "-", "volatility spike dissipates within a few trading minutes", "volatility_only", "abstract", "peer-reviewed", None, "F2_grains.json"),
        ev("Jump clustering", ["GRAINS-23"], "ZC", "2 min", "2008-2015", "-", "-", "jumps cluster within 2 minutes of the release", "absorbed_fast", "reused", "paper", None, "F2_grains.json"),
        ev("farmdoc single episode", ["GRAINS-52"], "ZC, ZS new crop", "day", "2025-09-12", "-", "-", "bearish WASDE, negative first reaction, closed higher (reversal)", "pointer", "full_text", "pointer (extension commentary)", None, "F2_grains.json"),
        ev("EPA RFS / NOPA news", ["GRAINS-48"], "ZL, ZM", "day", "2014-2025 news", "-", "-", "RFS announcements move ZL sharply (limit moves); NOPA moves ZM/ZL modestly; no intraday study", "pointer", "snippet", "pointer (news)", None, "F2_grains.json"),
        ev("E.32 R4 per-event table", [], "ZM, ZS, ZL", "-", "39-month window", "-", "-", "NOPA: no intraday study in any source read; about 49 major USDA days and 39 NOPA days in 39 months; post-USDA dropped as an E.33 family for power", "gap", "reused (E.32)", "methods brief", None, R4 + ":3214-3250"),
    ],
    "absorption_under_5min": "Lehecka et al. (about 10 min, abstract), Adjemian-Irwin (few minutes, volatility), jumps within 2 min (GRAINS-23), Huang: 40% of the hour's move in minute 1. Against it: GRAINS-18 (soybeans keep moving to the close, 2010-2021) and Huang's direction-known big-event drift to about 40-49 min.",
    "data_needs": {"schema": "1-minute bars or trades 11:00-13:20 CT; MBP-1 for the spread just after releases; limit-day flags", "history": "WASDE 12/yr, NOPA 12/yr, Grain Stocks 4/yr, Acreage and Prospective Plantings 1/yr each (stacked days)", "calendars": "USDA release calendar (real-time era since 2012-2013); NOPA dates and times (pre-2026 times unverified per E.32 R4)"},
    "r1_overlap": [{"id": "R1-08", "how": "K6 WASDE pre/post windows on ZC ZS ZL ZM ZW (screen, Tier B, no confirmation); closed V40"},
                   {"id": "R1-21", "how": "E.33 on ZM excluded release windows and dropped post-USDA as a family for power (E.32 verdict table); ZM 5-60 min closed V56"},
                   {"id": "R1-23", "how": "V39 'commodity event drift as a standalone stage' closed; R1 lists its products as crude, metals, natgas (grains not named)"}],
    "open_questions": ["Is there an entry-time signal (sign and size of the first 5-15 minutes) that keeps the GRAINS-18 / Huang drift? Not reported anywhere read.", "NOPA crush days: no study at all.", "Firm news windows for USDA releases: none listed for Topstep per the planner pointer; FirmRules owns this."],
})

# ---------------------------------------------------------------- R2-F04
FAMILIES.append({
    "id": "R2-F04",
    "name": "US macro release drift (08:30 ET NFP, CPI, PPI, GDP; 09:15 IP; 10:00 ET ISM) across rates, equity, metals, FX, crypto",
    "mechanism": {
        "whose_flow": "Repricing of rate and growth expectations after a surprise; slower cross-asset digestion (copper, silver lags).",
        "why_predictable": "Pre-announced calendar (EQUITY-16).",
        "why_retail_edge_could_exist": "Only in the slower components: ES continuing adjustment 10-30 min (EQUITY-17) and the metals' delayed response (METALS-23); the jump itself is absorbed within seconds to a minute (RATES-19, -20; FX-22).",
    },
    "codes": {"rates": ["ZT", "ZF", "ZN", "ZB", "2YY", "5YY", "10Y", "30Y"], "equity": ["MNQ", "M2K", "RTY", "MYM", "YM"], "metals": ["GC", "MGC", "SI", "SIL", "HG", "MHG"], "fx": ["6E", "M6E", "6A", "M6A"], "crypto": ["BTC", "MBT", "ETH", "MET"], "energy": ["CL", "QM", "MCL", "NG", "QG", "MNG"]},
    "horizons": {"intraday": "entry 5-10 min after the release, exit 30-60 min", "overnight": "none"},
    "evidence": [
        ev("Haynes and Roberts 2015 CFTC OCE", ["RATES-19"], "ZN (and ES)", "minutes or seconds", "2012-11..2015-09", "in sample", "-", "majority of permanent price changes within minutes or seconds after NFP", "absorbed_fast", "full_text", "regulator paper",
           "price discovery usually happens very quickly, with the majority of permanent price changes restricted to the minutes,", "F2_rates.json"),
        ev("Balduzzi, Elton, Green 2001 (secondary via CFTC)", ["RATES-20"], "cash Treasuries", "first minute", "early 1990s", "-", "-", "price adjustment within the first minute", "absorbed_fast", "full_text (secondary)", "peer-reviewed", None, "F2_rates.json"),
        ev("Kurov, Sancetta, Strasser, Wolfe 2015/2019 JFQA", ["EQUITY-17", "EQUITY-18", "RATES-22"], "ES (cousin), ZN", "t+10 to t+30 min; pre-release 30 min", "2008-01..2014-03", "in sample", "-", "some evidence of continuing adjustment 10-30 min after; pre-release drift in 7 of 18 releases (needs the surprise sign)", "positive (weak), pre-release not tradable ex ante", "full_text", "peer-reviewed",
           "a joint test of significance of price moves in the [t + 10min, t + 30min] window for all 30 announcements shows some evidence of continuing adjustment.", "F2_equity.json"),
        ev("Elder, Miao, Ramchander 2012 JBF", ["METALS-23", "METALS-24"], "GC, SI, HG", "5-min to 1 h", "2002-2008", "in sample", "-", "gold and silver mostly in 08:30-08:35; copper delayed; about 30-min delay after 09:15 releases; dissipates in under an hour; volatility decays within about 10 min", "positive (delayed response) / absorbed within 1 h", "reused (full text)", "peer-reviewed",
           "copper exhibits a somewhat delayed response to the 8:30 announcement. For the 9:15 announcements, there is about a 30-minute dela", "F2_metals.json"),
        ev("Chaboud et al. IFDP 823; ABDV", ["FX-21", "FX-22"], "EUR/USD (EBS spot), FX", "minutes", "1992-1998; 1999-2004", "in sample", "-", "conditional mean jump, completed within a few minutes", "absorbed_fast", "full_text", "central-bank WP / peer-reviewed",
           "the surprise component of the announcement produces a movement in the conditional mean that is generally completed within a few minutes, and that is effectively a jump.", "F2_fx.json"),
        ev("Benigno and Rosa NY Fed SR 1052", ["CRYPTO-27"], "bitcoin", "-5 to +25 and +55 min", "2017-2022", "in sample", "-", "bitcoin orthogonal to monetary and macro news", "null", "full_text", "central-bank WP",
           "The key result is that, unlike other U.S. asset classes, Bitcoin is orthogonal to monetary and macroeconomic news.", "F2_crypto.json"),
        ev("Kroner, Mohammed, Vega 2026", ["CRYPTO-29"], "crypto", "near-instantaneous; vol 30 min", "n/a", "-", "-", "reactions near-instantaneous; volatility, volume, spreads elevated up to 30 min", "absorbed_fast (snippet)", "snippet", "pointer", None, "F2_crypto.json"),
        ev("Takahashi 2025 arXiv", ["EQUITY-19"], "ES order flow", "1 s", "n/a", "-", "-", "macro-news shocks dissipate within one second", "absorbed_fast", "abstract", "preprint", None, "F2_equity.json"),
        ev("Boucher, Gagnon, Power 2025 Energy J.", ["NATGAS-32"], "NG", "unknown", "n/a", "-", "-", "26 US macro releases move NG (price drift, volatility, spreads)", "unknown horizon", "abstract", "peer-reviewed", None, "F2_natgas.json"),
        ev("Payroll jumps in crude", ["CRUDE-38"], "CL", "jumps", "2005-2010", "-", "-", "payrolls followed by jumps in over 30% of releases", "volatility_only", "reused", "paper", None, "F2_crude.json"),
    ],
    "absorption_under_5min": "Strongest of all families: rates (RATES-19, -20), FX (FX-21, -22), ES order flow (EQUITY-19), crypto (CRYPTO-27, -29), E.25 (1-5 seconds on ES, NQ, ZN, CL). Slower pieces: ES 10-30 min (weak joint test), copper and silver delays (2002-2008).",
    "data_needs": {"schema": "1-minute bars or trades around 07:30, 08:15, 09:00 CT; consensus forecasts for surprises (vendor data, not owned per sources read)", "history": "about 12 per release type a year; NFP, CPI, PPI each monthly", "calendars": "E.20 shared/macro_calendars.md (EQUITY-16)"},
    "r1_overlap": [{"id": "R1-01", "how": "MES family E scheduled-macro and calendar (MES outside the universe; equity cousin)"},
                   {"id": "R1-04", "how": "K2 ISM pre-drift on rates; closed V40"},
                   {"id": "R1-19", "how": "E.20 census of 17 roots incl. macro-release effects"}],
    "open_questions": ["No post-2015 study shows a mean drift of 5 minutes or more after US macro releases in Treasury, FX or crypto futures (searched, not found: F2_rates, F2_fx, F2_crypto).", "Firm news windows (Topstep Tier 1: CPI, NFP, PPI, FOMC; equity minis and GC SI HG blocked, MGC capped per planner pointer) may gate the core trade: FirmRules owns this."],
})

# ---------------------------------------------------------------- R2-F05
FAMILIES.append({
    "id": "R2-F05",
    "name": "FOMC statement and post-statement drift (hours)",
    "mechanism": {
        "whose_flow": "Slow repricing of the policy path after the 14:00 ET statement and press conference; portfolio rebalancing over the afternoon.",
        "why_predictable": "Eight scheduled meetings a year (FX-26 for frequency of ECB/RBA; FOMC 8/yr).",
        "why_retail_edge_could_exist": "SR 1188 finds an unconditional, persistent yield decline for about 3 hours after the statement, a horizon a one-lot can reach.",
    },
    "codes": {"rates": ["ZT", "ZF", "ZN", "ZB", "2YY", "5YY", "10Y", "30Y"], "equity": ["MNQ", "M2K", "RTY", "MYM", "YM"], "metals": ["GC", "MGC"], "fx": ["6E", "M6E", "6A", "M6A"]},
    "horizons": {"intraday": "14:00 ET to the 16:00 CT close (rates); 75+ min to the equity close (EQUITY-20)", "overnight": "post-FOMC drift over days in long bond futures (RATES-26, abstract); FX 12-24 h partial reversal (FX-25)"},
    "evidence": [
        ev("Fleming, Liu, Nguyen NY Fed SR 1188 (2026)", ["RATES-23"], "Treasury yields (cash)", "3 h after statement", "1997..2024-07", "in sample", "gross", "significant, persistent yield decline after FOMC; null before FOMC and around payrolls", "positive (unconditional drift)", "reused (E.20 full text)", "central-bank WP",
           "In the three hours prior to each announcement, yield changes are not systematically different from zero. Following employment report releases, yield changes remain largely insignificant. FOMC announcements are followed by a significant and persistent decline", "F2_rates.json"),
        ev("Gao et al. 2018 Table 8", ["EQUITY-20"], "SPY", "last half-hour on FOMC days", "1993-2013", "in sample", "gross", "intraday momentum 20.04%/yr on FOMC days vs 6.24%", "positive", "reused", "peer-reviewed", None, "F2_equity.json"),
        ev("Awartani et al. 2024 IRFA", ["METALS-25"], "GC", "5 and 10 min after the shock", "2007-2020", "in sample", "-", "adjustment at 10 min threefold that at 5 min", "positive (slower than 5 min)", "reused", "peer-reviewed", "However, the adjustment 10 minutes after the shock is significantly threefold higher than after 5 minutes.", "F2_metals.json"),
        ev("FOMC FX dissertation", ["FX-25"], "currencies", "12 h windows", "1999-2015", "in sample", "gross", "appreciation before and partial reversal 12-24 h after", "mixed (hours, overnight)", "full_text", "dissertation", None, "F2_fx.json"),
        ev("Indriawan, Jiao, Tse 2021 JBF", ["RATES-26"], "long bond futures", "up to 15 days", "post-GFC", "-", "-", "post-FOMC drift over days", "positive (multi-day)", "abstract", "peer-reviewed", None, "F2_rates.json"),
        ev("Lucca-Moench; Kurov-Wolfe-Gilbert 2021", ["EQUITY-21", "RATES-25"], "SPX; Treasuries", "24 h before", "1994-2011; to 2019", "in sample", "-", "pre-FOMC equity drift disappeared after 2015; none in Treasuries", "negative", "reused / abstract", "peer-reviewed", None, "F2_equity.json; F2_rates.json"),
        ev("Benigno and Rosa", ["CRYPTO-27"], "bitcoin", "-5 to +55 min", "2017-2022", "in sample", "-", "orthogonal to monetary news", "null", "full_text", "central-bank WP", None, "F2_crypto.json"),
        ev("Program K2/K5 (R1-04, R1-07)", ["R1-04", "R1-07"], "ZT ZF ZN ZB; MGC", "post-FOMC windows", "screen 2025-04..2026-06; K5-fomc-01 MGC confirmation 2019-05..2024-02", "screen + confirmation", "net", "K5-fomc-01 null; K2 fomcpost Tier B, no confirmation", "negative / untested", "reused", "program", None, "R1_closed_lines.json"),
    ],
    "absorption_under_5min": "Statement jump fast (E.25 for ZN); gold continues 5-10 min (METALS-25); rates drift persists about 3 h (RATES-23).",
    "data_needs": {"schema": "1-minute bars or trades 13:00-16:00 CT on statement days", "history": "8 events a year: about 26 in 39 months, so power is low (V45 notes 3-15 events give power 0.11-0.22 for the drifts it names)", "calendars": "FOMC statement dates and times (14:15 ET before 2013, EQUITY-16)"},
    "r1_overlap": [{"id": "R1-04", "how": "K2 post-FOMC member on rates (Tier B, no confirmation); closed V40"},
                   {"id": "R1-07", "how": "K5-fomc-01 MGC, E.22 confirmation null"},
                   {"id": "R1-19", "how": "V45 exception: pre-FOMC ZN drift (pre-statement, see R2-F06)"}],
    "open_questions": ["Is SR 1188's 3-hour decline present in ZN/ZF futures after 2015 and net of costs? Not found.", "FOMC is a Topstep Tier 1 event (planner pointer): whether rates are outside its window (pointer says 'energies, rates, FX unaffected') is FirmRules' fact."],
})

# ---------------------------------------------------------------- R2-F06
FAMILIES.append({
    "id": "R2-F06",
    "name": "Pre-scheduled-event drift and supply pressure (pre-FOMC ZN, pre-refunding ZN, Treasury auction cycle, pre-WNGSR)",
    "mechanism": {
        "whose_flow": "Dealers absorbing new Treasury supply (auction concession and post-auction reversal); risk premium before uncertainty resolves; informed or forecast-based positioning before inventory reports.",
        "why_predictable": "Auction, refunding and FOMC calendars are published in advance.",
        "why_retail_edge_could_exist": "Hours-scale price pressure that a one-lot can hold; samples are small (3-15 events in a research window per V45).",
    },
    "codes": {"rates": ["ZT", "ZF", "ZN", "ZB", "2YY", "5YY", "10Y", "30Y"], "natgas": ["NG", "QG", "MNG"]},
    "horizons": {"intraday": "auction: hours before the 13:00 ET auction and after; pre-refunding 06:30-16:00 CT (DF3-C4); pre-WNGSR 85-90 min", "overnight": "pre-FOMC ZN window 18:00 CT on the Monday evening to 11:00 CT Tuesday (DF3-C5), inside one Topstep trading day per E.25 DF3"},
    "evidence": [
        ev("Pan and Peng 2026 (V45 exception)", ["R1-19"], "10-year note futures", "19:00 ET day -2 to 12:00 ET day -1", "2004-01..2025-06", "in sample, no post-2015 split", "gross", "+7.26 bp, t 2.82; rest of day -1 gives back -2.05 bp (t -1.76)", "positive (pre-2015 dominated)", "full_text (E.25 DF3)", "working paper",
           "The average cumulative return on U.S. Treasury futures begins to rise at 19:00 ET on day -2, coinciding with the start of the Tokyo market, and peaks at 12:00 ET on day -1", "reports/stage_e25_briefs/DF3_treasury_drifts.md:74"),
        ev("Wang and Zhao 2025 (V45 exception)", ["R1-19"], "10-year cash Treasury", "trading day before the Monday 15:00 ET refunding release", "1991Q4-2023, N 129", "in sample", "gross", "+12.62 bp/day (t 3.32); post-2002 15.48 (t 3.27); 9.40 bp with calendar controls; no futures, no post-2015 split", "positive (daily, cash)", "full_text (E.25 DF3)", "working paper",
           "Full 129 0.66 [0.86] 8.25∗∗∗ [3.62] 12.62∗∗∗ [3.32]", "reports/stage_e25_briefs/DF3_treasury_drifts.md:65"),
        ev("Fleming, Liu, Nguyen SR 1188", ["RATES-24"], "on-the-run cash 2Y-30Y", "180-min windows around 13:00 ET auctions", "1991-2024", "in sample", "gross", "pre-auction price pressure and post-auction reversal; own-tenor pressure roughly halved in 2015-2024", "positive, decaying", "reused", "central-bank WP",
           "Pre-auction Return (bps) −0.733∗∗∗ −1.134∗∗∗ −2.523∗∗∗ −1.204 −3.822∗∗∗ −12.075∗∗∗", "F2_rates.json"),
        ev("Robeco quant chart 2025", ["RATES-43"], "ZN", "auction day (window unstated)", "1983-2024", "-", "gross", "ZN declines ahead of the 10-year auction", "positive (practitioner)", "full_text", "practitioner", None, "F2_rates.json"),
        ev("Gu and Kurov 2018", ["NATGAS-40"], "NG", "85-90 min before WNGSR", "2008-2016", "in sample", "not stated", "Sharpe 0.84 with analyst forecasts", "positive", "reused", "peer-reviewed", None, "F2_natgas.json"),
        ev("Kurov et al. pre-announcement drift", ["RATES-22", "EQUITY-18"], "ZN, ES", "30 min before release", "2008-2014", "in sample", "-", "drift in the direction of the surprise: not tradable without the surprise sign", "not tradable ex ante", "reused / full_text", "peer-reviewed", None, "F2_rates.json"),
        ev("Lucca-Moench", ["RATES-25"], "Treasuries", "24 h pre-FOMC", "1994-2011", "in sample", "-", "no pre-FOMC drift in Treasuries (contrast with Pan-Peng futures window)", "negative", "reused", "peer-reviewed", None, "F2_rates.json"),
    ],
    "absorption_under_5min": "Not applicable (pre-event and hours-scale supply effects); auction effect has decayed (halved 2015-2024).",
    "data_needs": {"schema": "1-minute bars or trades on ZT ZF ZN ZB across the overnight and day sessions", "history": "auctions about 0.23 a week per tenor (RATES-27); refunding 4/yr; FOMC 8/yr; WNGSR 52/yr", "calendars": "Treasury auction and refunding calendars (treasury.gov), FOMC dates, analyst forecasts for WNGSR"},
    "r1_overlap": [{"id": "R1-04", "how": "K2 pre/post Treasury-auction windows and ISM pre-drift (screen, Tier B); closed V40"},
                   {"id": "R1-13", "how": "E16-H3 Treasury auction cycle (holds overnight per V28); closed V31"},
                   {"id": "R1-19", "how": "V45 lists the pre-refunding and pre-FOMC ZN drifts as exceptions with power 0.11-0.22; whether closed or open is for the lead (R1 ambiguity)"},
                   {"id": "R1-06", "how": "K4-ngpre-01 NG storage pre-release failed Holm (E.5)"}],
    "open_questions": ["No post-2015 subsample for either V45 ZN drift; the micro yields (2YY..30Y) are cash-settled to BrokerTec (RATES-32) and untested.", "Power at 4-8 events a year is the binding issue (V45)."],
})

# ---------------------------------------------------------------- R2-F07
FAMILIES.append({
    "id": "R2-F07",
    "name": "Benchmark fixes and month-end rebalancing flows (FX fixes, month-end dollar and Treasury demand, LBMA metals auctions)",
    "mechanism": {
        "whose_flow": "Asset managers and corporates trading at benchmark fixes (WMR 16:00 London, ECB, Tokyo) and rebalancing hedges at month-end; index-duration extension in Treasuries at month-end.",
        "why_predictable": "Fixed clock times and calendar dates; month-to-date equity returns set the hedge rebalancing sign (Melvin-Prins).",
        "why_retail_edge_could_exist": "Flows are non-informational and dated; Krohn et al. report CME futures post-London +0.64 bp (t 2.20), but liquidity demanders lose after costs.",
    },
    "codes": {"fx": ["6E", "M6E", "6A", "M6A"], "rates": ["ZT", "ZF", "ZN", "ZB"], "metals": ["GC", "MGC", "SI", "SIL"]},
    "horizons": {"intraday": "1-60 min around fixes (Evans 1, 5, 15 min; Melvin-Prins 60 min before); hours around London fix (Krohn)", "overnight": "Treasury month-end returns are close-to-close over 1-5 days (RATES-44)"},
    "evidence": [
        ev("Krohn, Mueller, Whelan 2024 JF", ["FX-38"], "spot; CME futures dollar portfolio", "hours around fixes", "1999-2019 (CME from 2006)", "in sample", "gross; liquidity demanders negative after costs", "EUR post-London +2.73 bp/day; AUD pre-Tokyo -2.84, post-London +1.93; CME futures post-London +0.64 (t 2.20)", "positive gross / negative net for demanders", "reused (E.20 full text)", "peer-reviewed",
           "the unconditional return patterns cannot easily be arbitraged in the client market as transaction cost adjusted returns are significantly", "F2_fx.json"),
        ev("Evans 2018 JBF", ["FX-39"], "spot, 21 pairs", "1, 5, 15 min after the month-end fix", "2004-2013", "post-2010 out of sample", "net of half spread", "15 min: EUR/USD 3.965%/yr, AUD/USD 9.187%/yr; average across currencies 3.25%", "positive net (spot)", "reused (full text)", "peer-reviewed",
           "Returns are inclusive of trading costs [...] average return across the currencies of 3.25 percent.", "F2_fx.json"),
        ev("Melvin and Prins 2015 JFM", ["FX-40"], "spot, 10 currencies", "60 min before month-end fix", "2004-2012", "in sample", "gross", "month-to-date equity return predicts the currency's move", "positive", "reused (full text)", "peer-reviewed", None, "F2_fx.json"),
        ev("Fix V-shapes", ["FX-50", "FX-51"], "USD", "around Tokyo 9:55 JST, ECB 14:15/14:00 CET, WMR 16:00", "n/a", "-", "-", "V-shaped USD moves at fixes; WMR window widened to 5 min on 2015-02-15", "structure", "full_text", "paper", None, "F2_fx.json"),
        ev("Hartley and Schwarz 2019", ["RATES-44"], "Treasury futures", "last t days of the month, close-to-close", "1990-2018", "in sample", "gross", "predictable end-of-month returns (daily horizon)", "positive (multi-day)", "full_text", "working paper", None, "F2_rates.json"),
        ev("LBMA gold auction post-2015", ["METALS-35"], "gold", "minutes", "post-2015", "-", "-", "no significant leakage before the fix; price discovery finishes within minutes", "absorbed_fast", "full_text", "paper", None, "F2_metals.json"),
        ev("PM-fix drop / hat shape (CBS thesis)", ["METALS-28", "METALS-36"], "gold", "around 15:00 London; 24 h", "2007-2011 significant only", "-", "-", "pattern significant only 2007-2011", "negative (decayed)", "full_text", "thesis", None, "F2_metals.json"),
        ev("Caminschi 2014 UWA WP", ["METALS-43", "METALS-44"], "COMEX silver futures", "about 10 min either side of the noon fix", "2000-2013", "in sample", "-", "10-12 bp downward bias around the London silver fixing; the fixing was replaced by an auction in 2014", "positive pre-2014, mechanism removed", "full_text", "working paper (do not cite)", None, "F2_metals.json"),
        ev("Program K3 screen and E.22 (R1-05)", ["R1-05"], "6E 6A and 5 other FX", "London-fix reversal and momentum, ECB fix, Tokyo fix pre/post, month-end hedge", "screen 2025-04..2026-06; ldnrev 6E 2019-05..2024-02", "screen + confirmation", "net", "K3-ldnrev-01 6E confirmation null; others Tier B", "negative", "reused", "program", None, "R1_closed_lines.json"),
    ],
    "absorption_under_5min": "LBMA gold post-2015 (METALS-35); WMR window widened to 5 min in 2015 (structure). Evans finds effects at 1-15 min after the fix.",
    "data_needs": {"schema": "1-minute bars or trades around 10:00 CT (16:00 London), 07:15 CT (ECB), Tokyo 9:55 JST (overnight in CT); month-end flags; month-to-date equity return", "history": "12 month-ends a year; daily fixes", "calendars": "WMR, ECB, Tokyo fix times with DST shifts; LBMA auction times (10:30, 15:00 London)"},
    "r1_overlap": [{"id": "R1-05", "how": "K3 London-fix reversal/momentum, ECB fix, Tokyo fix pre/post, month-end hedge on 6E 6A (and other FX); ldnrev null at E.22; closed V40"},
                   {"id": "R1-07", "how": "K5 LBMA AM/PM auction windows on MGC (pmfix excluded from the count); closed V40"},
                   {"id": "R1-04, R1-13, R1-18", "how": "K2-monthend-01 long ZF/ZN/ZB (screen; at 5 days closed V41); E16-H2 month-end NQ vs ZN closed V31"}],
    "open_questions": ["Evans' month-end fix effect is on spot with a half-spread cost; no CME futures test net of a futures round trip found.", "Tokyo fix lands in the overnight Globex session (FX liquidity at that hour: DataAccess/T1 owners)."],
})

# ---------------------------------------------------------------- R2-F08
FAMILIES.append({
    "id": "R2-F08",
    "name": "Regional session and overnight-to-day handoffs (local-hours currency effect, European open, day-session reopen after a pause, settlement-window reversal, day versus night returns)",
    "mechanism": {
        "whose_flow": "Local-hours hedging and order imbalances carried over from the prior close (Boyarchenko et al.: 2:00-3:00 ET returns linked to prior US-close imbalances); overnight news priced at the reopen.",
        "why_predictable": "Fixed session clocks (Globex pauses: grains 07:45-08:30 CT, GRAINS-14; daily 16:00-17:00 CT halts).",
        "why_retail_edge_could_exist": "Hours-scale holds around a known clock; most documented versions are gross or negative after spreads.",
    },
    "codes": {"fx": ["6E", "M6E", "6A", "M6A"], "equity": ["MNQ", "M2K", "RTY", "MYM", "YM"], "metals": ["GC", "MGC"], "crude": ["CL", "QM", "MCL"], "grains": ["ZC", "ZS", "ZW", "ZM", "ZL", "minis", "micros"], "crypto": ["BTC", "MBT", "ETH", "MET"], "rates": ["ZT", "ZF", "ZN", "ZB"]},
    "horizons": {"intraday": "session blocks of hours (local trading hours); first half-hour after the day reopen", "overnight": "European-open drift 02:00-03:00 ET (EQUITY-50), gold overnight vs day (METALS-31), INE night -> day (CRUDE-41), crypto weekend gap (CRYPTO-41, pointer; Globex crypto 24/7 from 2026-05-29, CRYPTO-38)"},
    "evidence": [
        ev("Breedon and Ranaldo 2013 JMCB", ["FX-37", "FX-49"], "EBS spot EUR/USD, AUD/USD", "session (hours)", "1997-2007", "in sample", "net of EBS bid/ask", "a currency falls in its own local hours; EUR/USD Sharpe 1.3 and 0.9 net; AUD/USD net negative (-0.51, -0.50)", "positive net (EUR), negative net (AUD)", "full_text", "peer-reviewed",
           "the notable exception is EUR/USD where the significant intraday pattern combined with narrow spreads in this cross means that this basic strategy has been profitable on average with Sharpe Ratios of 1.3 and 0.9", "F2_fx.json"),
        ev("Jiang 2018 WP", ["FX-45"], "currencies", "US vs foreign hours", "n/a", "-", "-", "European currencies gain in US hours", "unverified", "snippet", "working paper", None, "F2_fx.json"),
        ev("Boyarchenko, Larsen, Whelan NY Fed SR 917 / RFS 2023", ["EQUITY-50", "EQUITY-51"], "ES (cousin)", "02:00-03:00 ET (overnight hold)", "1998-2020", "in sample", "net of bid-ask", "+3.7%/yr gross, Sharpe 1.1 gross, -0.5 after spreads (1:30-3:30: 1.3 gross, 0.3 net)", "negative net", "full_text", "peer-reviewed", None, "F2_equity.json"),
        ev("COMEX gold day vs overnight", ["METALS-31"], "GC front", "day vs overnight", "1985-2012", "in sample", "claimed 'even with transaction costs'", "day returns negative, overnight positive", "positive (pre-2013)", "abstract", "paper",
           "Overnight returns are significantly positive while day returns are significantly negative in the COMEX gold front futures contract", "F2_metals.json"),
        ev("INE SC night -> day", ["CRUDE-41"], "INE crude (other venue)", "night return -> day", "n/a", "in and out of sample", "-", "night return predicts a day reversal", "positive (other venue)", "abstract", "paper", None, "F2_crude.json"),
        ev("Wen et al. 2023 / Wen-Gong-Ma-Xu 2021 (USO)", ["CRUDE-19", "CRUDE-43"], "USO", "first half-hour after the overnight break -> close", "2006-2019", "in sample (2021: in and out)", "gross", "first half-hour predicts the last half-hour", "positive (other venue)", "reused / snippet", "peer-reviewed", None, "F2_crude.json"),
        ev("DCE vs US overnight", ["GRAINS-42"], "DCE soybean, corn", "overnight -> day", "before/after DCE night trading (~2019)", "-", "-", "overreaction to US overnight returns stopped working after night trading", "negative (arbitraged)", "abstract", "paper", None, "F2_grains.json"),
        ev("Onur and Reiffen (CFTC)", ["GRAINS-17"], "ZC", "pre-close to settlement, reversed at next open", "2012-03..06", "in sample", "-", "settlement-window reversals declined after the 2012 rule change", "negative (decayed)", "full_text", "regulator paper", None, "F2_grains.json"),
        ev("E.32 R4 table: Sunday open and SM overnight", [], "ZM", "overnight + first half-hour -> last half-hour", "1982-2020", "OOS", "-", "CBOT SM overnight + first half-hour: no prediction (Baltussen); planner family 4 (08:30 reopen gap) untested", "null", "reused (E.32)", "peer-reviewed", None, R4 + ":3224"),
        ev("Shen, Urquhart, Wang 2022", ["CRYPTO-39"], "bitcoin spot", "US-morning open to 17:00 EST break", "2013-2020", "OOS", "not profitable at 25 bp", "first half-hour predicts last half-hour", "positive gross", "full_text", "peer-reviewed", None, "F2_crypto.json"),
        ev("CME crypto gap", ["CRYPTO-41"], "BTC, MBT", "weekend gap", "n/a", "-", "-", "no academic study; fill-rate claims from trader posts only; gap removed by 24/7 trading from 2026-05-29", "pointer, negative", "pointer", "pointer", None, "F2_crypto.json"),
        ev("Fleming-Remolona-type session study", ["RATES-51"], "cash Treasuries", "Tokyo -> London -> NY", "1994", "in sample", "-", "overseas changes are unbiased predictors of NY overnight changes", "structure", "full_text", "paper", None, "F2_rates.json"),
        ev("Volatility-only session facts", ["CRUDE-29", "CRUDE-48", "NATGAS-50", "GRAINS-36"], "CL, NG, ZC ZS", "open/close", "various", "-", "-", "jumps cluster at former pit open/close; U-shaped volatility; spreads widest next to the pause", "volatility_only", "full_text", "papers", None, "F2_crude/natgas/grains.json"),
    ],
    "absorption_under_5min": "Not the issue here; the evidence that exists is either gross, pre-2013, other-venue, or negative after spreads (EQUITY-51) or arbitraged after a venue change (GRAINS-42, GRAINS-17).",
    "data_needs": {"schema": "1-minute bars or trades through the overnight session (ETH) and the reopen; MBP-1 for overnight spreads", "history": "daily (one trade a day per product)", "calendars": "session clocks per product incl. DST; Globex pauses; crypto session change 2026-05-29"},
    "r1_overlap": [{"id": "R1-01", "how": "MES families A (calendar/clock windows) and D (gaps) incl. overnight/European-open drift (MES A-H1, A-H3, E-H4 per R1 family lookup)"},
                   {"id": "R1-03..R1-09", "how": "CP3 prior-day close-location continuation or reversal on every K cluster"},
                   {"id": "R1-13", "how": "E16-H4 next-day reversal of the settlement-window move; closed V31"},
                   {"id": "R1-10", "how": "K8-wkndbtc-01 weekend bitcoin to NQ (inconclusive by design)"},
                   {"id": "R1-05", "how": "K3 Tokyo fix pre/post (overnight handoff for FX)"}],
    "open_questions": ["No post-2010 futures test of the local-hours currency effect on 6E/6A net of a futures round trip.", "Grains 08:30 CT reopen after the 07:45-08:30 pause: untested (planner family 4), and Export Sales lands at 07:30 CT just before the pause (GRAINS-22)."],
})

# ---------------------------------------------------------------- R2-F09
FAMILIES.append({
    "id": "R2-F09",
    "name": "Cross-market lead-lag and relative-value reversion (crush, calendars, mini/micro-full pairs, equity-index lead-lag, gold-silver, AUD-commodities, BTC-ETH)",
    "mechanism": {
        "whose_flow": "Hedgers and spread traders anchoring an economic relation (crush margin); information arriving first in the deeper market and propagating.",
        "why_predictable": "Cointegrated legs revert; a leader's move precedes a laggard's.",
        "why_retail_edge_could_exist": "Only where the lag or the reversion lasts minutes to hours: seconds-scale lead-lag cannot pay at retail latency (E.32 verdict table, M2 b).",
    },
    "codes": {"soy_crush": ["ZS", "ZM", "ZL", "XK", "MZS", "MZM", "MZL"], "corn_calendar": ["ZC", "XC", "MZC"], "equity": ["MNQ", "M2K", "RTY", "MYM", "YM"], "metals": ["GC", "MGC", "SI", "SIL"], "fx_commodity": ["6A", "M6A"], "crypto": ["BTC", "MBT", "ETH", "MET"], "energy": ["CL", "QM", "MCL", "NG", "QG", "MNG"]},
    "horizons": {"intraday": "15-240 min for crush residual reversion (planner family 1); 5-11 min for NQ->ES/RTY extrema; 1 min for silver->gold", "overnight": "crush cointegration mostly breaks down overnight (52 of 243 days)"},
    "evidence": [
        ev("Zhou, Bagnarosa, Gohin, Pennings, Debie (J. Commodity Markets 2023)", ["GRAINS-15", "GRAINS-16", "GRAINS-38"], "ZS, ZM, ZL", "1-minute sampling, daily VECM", "2015, 243 days", "in sample", "-", "day-session crush cointegrated on 180 of 243 days, overnight on 52; no fixed leader; no half-life or trading test", "structure (positive)", "full_text", "peer-reviewed",
           "A high level of cointegration is indeed observed during session 2 trading hours, which fades away during session 1.", "F2_grains.json"),
        ev("Program E.33c ZM search S1/S2 (R1-21)", ["R1-21", "GRAINS-49"], "ZM with ZS/ZL inputs", "5, 15, 30, 60 min; TB 15/30", "796 OOF dates 2020-12..2024-02", "registered r009-E33", "net", "crush residual and ZS/ZL propagation: no configuration passes; best loses 1.098 ticks a trade", "negative", "reused", "program", None, "R1_closed_lines.json"),
        ev("de Boer et al. 2022 JFM", ["GRAINS-24"], "soy complex", "30 s", "2015", "-", "-", "liquidity spillovers mainly within 30 s; negative at longer horizons", "absorbed_fast", "abstract", "peer-reviewed", None, "F2_grains.json"),
        ev("Corn nearby/deferred calendar", ["GRAINS-46"], "ZC", "intraday (daily estimation)", "2008-2015", "in sample", "-", "intraday cointegration on about 70% of days; nearby price-discovery share 52% vs first deferred", "structure", "full_text", "working paper", None, "F2_grains.json"),
        ev("Corn-soy-wheat weekly", ["GRAINS-47"], "ZC ZS ZW", "weekly", "n/a", "in sample", "-", "cointegrated weekly; trading rules significant risk-adjusted returns", "positive (weekly, outside band)", "full_text", "working paper 2012", None, "F2_grains.json"),
        ev("Maier-Paape and Platen 2015 arXiv", ["EQUITY-13"], "NQ, ES, Russell", "60-min chart extrema", "2004-09..2014-05", "in sample", "none", "NQ leads ES by about 9-12 min and Russell by 8-11 min; Russell leads ES by about 5 min", "positive (no trading test)", "full_text", "preprint", None, "F2_equity.json"),
        ev("Silver leads gold (master's thesis)", ["METALS-37"], "CME gold, silver", "1 min", "2007-2012", "in sample", "-", "silver leads gold at 1-minute frequency", "positive (sub-5-min lag)", "full_text", "thesis", None, "F2_metals.json"),
        ev("AUD vs gold, copper, oil (CIRANO WP)", ["FX-19", "FX-20"], "AUD/USD spot; futures daily", "5-min and daily", "2000-2009; 1992-2009", "in sample", "-", "Granger causality both ways, stronger at short horizons, commodity -> currency dominant; daily futures: none", "mixed", "full_text", "working paper", None, "F2_fx.json"),
        ev("BTC-ETH", ["CRYPTO-35", "CRYPTO-24"], "Coinbase 1-min", "short", "2022-2025", "-", "-", "BTC leads ETH only in high-volatility regimes", "mixed", "abstract", "peer-reviewed / abstract", None, "F2_crypto.json"),
        ev("Mechanical pairs", ["EQUITY-12", "GRAINS-45", "GRAINS-27", "METALS-38", "CRYPTO-32", "FX-14"], "micro/mini vs full", "-", "-", "-", "-", "micros and minis settle from the full-size settlement or share the underlying: arbitrage-tight", "structure (no directional edge)", "full_text / reused", "exchange documents", None, "F2 files"),
        ev("Arbitrage-tight cross-venue links", ["CRUDE-33", "RATES-17", "FX-17"], "CL-Brent; ZN-BrokerTec; 6E-FX Link", "seconds / ms", "various", "-", "-", "WTI leads; oil futures reflect news within minutes; futures-cash millisecond links", "absorbed_fast", "full_text", "papers", None, "F2 files"),
        ev("Crack and Brent-WTI spreads", ["CRUDE-34"], "CL (HO, Brent legs outside universe)", "daily and monthly", "1984-2005", "in sample", "-", "spreads mean-revert, legs cointegrated; no intraday crack study found", "positive (daily, outside band)", "full_text", "paper", None, "F2_crude.json"),
        ev("NG-CL", ["NATGAS-21"], "NG, CL", "10 min", "2003-2006", "in sample", "-", "volatility-only bidirectional causality", "volatility_only", "full_text", "paper", None, "F2_natgas.json"),
        ev("Gold after extreme S&P moves", ["METALS-32"], "gold", "after extreme negative 5-min S&P 500 moves", "n/a", "-", "-", "gold rises after extreme negative 5-minute S&P moves", "positive", "abstract", "paper", None, "F2_metals.json"),
    ],
    "absorption_under_5min": "Cross-venue and mechanical links are seconds or milliseconds (CRUDE-33, RATES-17, GRAINS-24); silver->gold at 1 minute (METALS-37). Minute-to-hour structure exists only for the crush (cointegration, no half-life) and the NQ/Russell extrema lags (preprint).",
    "data_needs": {"schema": "synchronised 1-minute bars or MBP-1 on all legs; for the crush ZS, ZM, ZL (owned ZM MBO and ZS/ZL MBP-1 for 2020-12..2024-02 were read by E.31/E.33)", "history": "continuous: n_cap trades a day", "calendars": "roll calendars for each leg; limit days for the soy complex"},
    "r1_overlap": [{"id": "R1-21", "how": "crush residual (S1) and ZS/ZL propagation (S2) on ZM at 5-60 min: closed V56; 2017-05..2020-11 ZM window sealed (V51)"},
                   {"id": "R1-08", "how": "K6-crushgap-01 ZS with ZM bars as the signal leg; closed V40"},
                   {"id": "R1-10", "how": "K8 equity flight into gold (MGC with MES leg), oil/CAD (6C with MCL leg), weekend BTC to NQ; closed V40"},
                   {"id": "R1-13", "how": "E16-H2 month-end NQ vs ZN pair; closed V31"},
                   {"id": "R1-20", "how": "E.31 read 2020-12..2024-02 ZM/ZS/ZL dates for markouts: not a clean holdout for order-flow tests (V50 item 4)"}],
    "open_questions": ["Crush residual reversion with ZS or ZL (not ZM) as the traded leg: not tested by the program; no published intraday half-life.", "No minute-level study of calendar-spread reversion for CL, NG or Treasuries; Treasury curve spreads (FIT/FYT, TUF, NOB, RATES-14) have no intraday study."],
})

# ---------------------------------------------------------------- R2-F10
FAMILIES.append({
    "id": "R2-F10",
    "name": "Order-book state and order flow at 5 minutes and longer (lagged order imbalance, book state, drift-burst aftermath)",
    "mechanism": {
        "whose_flow": "Large orders worked over time (sign persistence) and liquidity shocks followed by refill.",
        "why_predictable": "Imbalance and sign persistence are autocorrelated.",
        "why_retail_edge_could_exist": "Weak: forward predictability decays to insignificance by 5-30 minutes and sign persistence is offset by asymmetric liquidity (E.32 M1).",
    },
    "codes": {"all": "any code; published grain evidence for ZC ZS ZW (abstract); program evidence for ZM"},
    "horizons": {"intraday": "5-30 min forward", "overnight": "none"},
    "evidence": [
        ev("Chordia, Roll, Subrahmanyam 2005 (via E.32 M1)", [], "NYSE stocks", "5-60 min forward", "1996 and later", "in sample", "-", "forward R2 3.32% at 5 min, 0.53% at 30 min (1996); imbalance coefficient loses significance by 30 min", "decay to null", "full_text (E.32 M1)", "peer-reviewed",
           "the forward part decays to statistical insignificance by 5 to 30 minutes in the best-documented case (Chordia, Roll and Subrahmanyam 2005, NYSE)", R4 + ":3638-3640"),
        ev("Kolm, Turiel, Westray 2023", [], "equities", "about two price changes", "n/a", "-", "-", "deep order-flow forecasts effective for about two average price changes (about 12 s in ZM)", "absorbed_fast", "abstract", "peer-reviewed", None, R4 + ":3640-3641"),
        ev("Christensen, Oomen, Renò (via E.32 M1)", [], "ZC", "after drift bursts", "n/a, 97 events", "in sample", "-", "post-drift-burst reversal b = -0.20, R2 41.5%; event time set at a local extremum of the test statistic (look-ahead to remove)", "positive with look-ahead caveat", "full_text (E.32 M1)", "peer-reviewed", None, R4 + ":3643-3647"),
        ev("Volkenand et al. 2018", ["GRAINS-41"], "corn, wheat, soybeans, cattle, hogs", "unknown (full text 403)", "March 2008, March 2016", "-", "-", "lagged order imbalance predicts returns for some contracts", "positive (horizon unknown)", "abstract", "paper", None, "F2_grains.json"),
        ev("Pre-EIA order imbalance", ["CRUDE-16"], "CL", "pre-release", "n/a", "-", "-", "pre-EIA imbalance conditional on the ex-post surprise", "not tradable ex ante", "reused", "paper", None, "F2_crude.json"),
        ev("Adams et al. draft 2026", ["EQUITY-39"], "ES", "10-60 min", "2018-2024", "in sample", "gross", "net gamma predicts stronger order-flow reversals", "conditioner", "reused (full text)", "working paper", None, "F2_equity.json"),
        ev("Program E.33c S3 (R1-21)", ["R1-21"], "ZM order flow and book state (MBO)", "5-60 min", "2020-12..2024-02", "registered", "net", "no configuration passes; all G1 configurations lose over 1.0 tick a trade", "negative", "reused", "program", None, "R1_closed_lines.json"),
        ev("Excluded sub-5-minute items", ["EQUITY-45", "CRUDE-21", "RATES-47", "NATGAS-44"], "NQ, CL, ZN, NG", "<5 min / passive", "-", "-", "-", "excluded by the T6 rule (sub-5-minute or passive-fill)", "excluded", "abstract/reused", "-", None, "F2 files"),
    ],
    "absorption_under_5min": "Central: E.32 M1 (contemporaneous far stronger than forward), Kolm et al. (seconds), E.25 (1-5 seconds on ES, NQ, ZN, CL).",
    "data_needs": {"schema": "MBO or MBP-10 (book state), trades; 1 s to 1 min features", "history": "continuous", "calendars": "release and roll exclusions"},
    "r1_overlap": [{"id": "R1-21", "how": "ZM order flow and book state (S3) at 5-60 min closed V56; V56 item 2: 'Order-book direction is not closed for other products.'"},
                   {"id": "R1-20", "how": "passive spread capture closed V50; limit orders stay allowed as execution"},
                   {"id": "R1-11", "how": "ML on 1-minute bars (no book data)"}],
    "open_questions": ["No CME-product study of forward order-flow predictability at 5 minutes or more found outside ZM's own null.", "Drift-burst reversal after removing the look-ahead: untested."],
})

# ---------------------------------------------------------------- R2-F11
FAMILIES.append({
    "id": "R2-F11",
    "name": "Own-price-path intraday trend and reversal (hour-scale trend, short reversion, overreaction fades, breakout and noise-area momentum)",
    "mechanism": {
        "whose_flow": "Trend followers and stop cascades (trend); liquidity-provider inventory correction (reversion).",
        "why_predictable": "Price-path autocorrelation by horizon (reversion 2-16 min, weak trend at 1 h or more).",
        "why_retail_edge_could_exist": "Generic and crowded; the published sizes are tiny (out-of-sample R2 under 1 bp).",
    },
    "codes": {"all": "any; published pooled futures evidence covers crude and the 10-year (Safari-Schmidhuber)"},
    "horizons": {"intraday": "reversion 2-16 min; trend 1 h to the close", "overnight": "multi-day trend closed (R1-16)"},
    "evidence": [
        ev("Safari and Schmidhuber 2025 Physica A", ["CRUDE-40", "RATES-42"], "16-24 futures incl. crude and the 10-year", "minutes to hours", "2010-2023", "OOS", "gross", "reversion at 2-16 min, weak trend persistence at 1 h or more; OOS R2 0.55 bp and 0.020 bp", "positive but tiny", "full_text", "peer-reviewed",
           "weak trends tend to persist (b > 0), while strong trends tend to revert (c < 0).", "F2_crude.json"),
        ev("Cusatis, Kulkarni, Thomas 2009", ["RATES-46"], "T-note futures", "intraday", "pre-2010", "-", "-", "negative serial correlation that declined considerably over time", "decay", "abstract", "paper", None, "F2_rates.json"),
        ev("Rentzler et al. 2006 JFM", ["FX-44"], "7 CME currency futures", "intraday reversal", "1988-2003", "in sample", "-", "reversals in 5 of 7", "positive (pre-2003)", "abstract", "peer-reviewed", None, "F2_fx.json"),
        ev("Overreaction contrarian", ["METALS-30", "CRUDE-22"], "GC SI HG; futures in Covid", "intraday", "2019-2020", "in sample", "-", "overreactions and reversals; turning points defined ex post", "positive with look-ahead", "abstract/full_text", "papers", None, "F2_metals.json"),
        ev("Chinese commodities", ["CRUDE-44"], "Chinese commodity futures", "intraday", "n/a", "-", "net", "intraday momentum and reversal do not cover costs", "negative", "abstract", "paper", None, "F2_crude.json"),
        ev("ICE Brent efficiency", ["CRUDE-54"], "Brent", "<10 min vs longer", "n/a", "-", "none", "inefficient under 10 min, more efficient at lower frequencies", "absorbed by 10 min", "full_text", "paper", None, "F2_crude.json"),
        ev("Akyildirim, Cepni, Corbet, Uddin 2021", ["CRYPTO-20"], "CME BTC futures", "5-60 min", "2020-01..2020-09", "OOS", "gross", "ML accuracy about 54% (51-57%)", "positive gross (short sample)", "full_text", "peer-reviewed", None, "F2_crypto.json"),
        ev("Crypto spot studies", ["CRYPTO-18", "CRYPTO-21", "CRYPTO-22", "CRYPTO-26"], "spot crypto", "intraday to 6 h", "2014-2022", "mixed", "assumed fee in one", "Bouri et al. Sharpe 0.74 at 0.03% fee; predictability up to 6 h (abstract); mostly unpredictable (abstract)", "mixed", "full_text/abstract", "peer-reviewed", None, "F2_crypto.json"),
        ev("Zarattini, Aziz, Barbon WP (noise-area momentum)", ["EQUITY-42"], "SPY", "intraday", "2007-2024", "in sample", "net of commission", "6.2%/yr net, Sharpe 0.61; V45 item 3: dropped on post-publication evidence (no independent S&P test distinguishable from zero)", "positive pre-publication / negative after", "reused", "practitioner WP", None, "F2_equity.json; docs/DECISIONS.md:898-909"),
        ev("Mesfin 2026; Taylor 2026", ["EQUITY-43", "EQUITY-44"], "MNQ 5-min; NQ 15-min", "5-15 min", "2021-2025; 2022-2026", "walk-forward OOS; in sample", "net of 2 MNQ points", "none of 14 OHLCV families passes; AMD signal has no direction beyond the daily trend regime", "negative", "reused / full_text", "preprints", None, "F2_equity.json"),
    ],
    "absorption_under_5min": "Short reversion is at 2-16 min and tiny (CRUDE-40); Brent inefficiency vanishes past 10 min (CRUDE-54).",
    "data_needs": {"schema": "1-minute bars", "history": "continuous", "calendars": "release and roll exclusions"},
    "r1_overlap": [{"id": "R1-01", "how": "MES families B (opening range, breakout), C (reversal, fade), G (price-path statistics), H (NR4/NR7 ORB): 58 tests, null"},
                   {"id": "R1-03..R1-09", "how": "CP2 opening-range breakout port and overreaction fades (K1 VXN band, K4-ovr, K5-ovr), K7 2-hour reversal on MBT"},
                   {"id": "R1-11, R1-15", "how": "ML over 64 and 36 bar features at h60/h120/hF on 27 and 17 roots"},
                   {"id": "R1-21", "how": "ZM own price path (S4) at 5-60 min closed V56"},
                   {"id": "R1-19", "how": "E.25 shortlist named noise-area MNQ, never tested; V45 item 3 drop stands on post-publication evidence"}],
    "open_questions": ["Every generic price-path family has been screened by the program on 1-minute bars; a new one would be a close variant unless the product or mechanism differs (scorer's call)."],
})

# ---------------------------------------------------------------- R2-F12
FAMILIES.append({
    "id": "R2-F12",
    "name": "Expiry and option-hedging days (equity 3rd-Friday reversal, dealer-gamma conditioning, crypto option expiry)",
    "mechanism": {
        "whose_flow": "Option market makers' delta hedging around expiry and their aggregate gamma; leveraged ETF rebalancing.",
        "why_predictable": "Expiry calendars are fixed; dealer gamma is estimable from open interest (GEX).",
        "why_retail_edge_could_exist": "Non-informational flow at a known date; events are few (monthly).",
    },
    "codes": {"equity": ["MNQ", "M2K", "RTY", "MYM", "YM"], "crypto": ["BTC", "MBT", "ETH", "MET"]},
    "horizons": {"intraday": "expiry day into the close; 10-60 min conditioned on gamma", "overnight": "post-expiry reversal (days)"},
    "evidence": [
        ev("Baltussen, Terstegge, Whelan (V45 exception)", ["R1-19"], "ES (cousin; not a candidate)", "3rd-Friday", "2003-2021", "in sample", "gross", "-12.89 bp (t -2.40); 2015-23 not significant alone", "positive pre-2015, null after", "reused (E.25)", "working paper", None, "docs/DECISIONS.md:917-920"),
        ev("Barbon, Beckmeyer, Buraschi, Moerke (via E.20)", [], "US stocks/ETFs", "end of day", "n/a", "in sample", "gross", "large negative (positive) gamma imbalance gives end-of-day momentum (reversal); leveraged-ETF effect economically larger; effects revert", "positive (mechanism)", "full_text", "working paper",
           "We find that a large and negative (positive) aggregated gamma imbalance, relative to the average dollar volume, gives rise to an economically and statistically significant end-of-day momentum (reversal).", "reports/stage_e20_briefs/shared/barbon_beckmeyer_buraschi_moerke_letf.pdf.txt:31-34"),
        ev("Adams et al. draft 2026", ["EQUITY-39"], "ES", "60 min", "2018-2024", "in sample", "gross", "momentum reverses in the high net-gamma quartile", "conditioner", "reused", "working paper", None, "F2_equity.json"),
        ev("Weiss, Gaudiosi, Zhou, Webb 2026 FRL", ["CRYPTO-23"], "spot and Deribit perps", "around option expiry", "n/a", "-", "-", "reversal around Deribit expiry", "positive (other venue)", "abstract", "peer-reviewed", None, "F2_crypto.json"),
    ],
    "absorption_under_5min": "Not applicable (calendar flow).",
    "data_needs": {"schema": "1-minute bars; option open interest by strike for GEX (vendor data; R1-14 used GEX rows 2020-05-29..2024-02-28)", "history": "12 monthly expiries a year (4 quarterly)", "calendars": "equity and crypto option expiry calendars"},
    "r1_overlap": [{"id": "R1-14", "how": "H6 T3: momentum conditioned on negative prior-day GEX on NQ; closed V38"},
                   {"id": "R1-23", "how": "C2 GEX late-session momentum stopped at its power rule (135 eligible dates, floor 200)"},
                   {"id": "R1-09", "how": "K7-expiry-01 on MBT not traded (every research expiry in a roll blackout)"},
                   {"id": "R1-19", "how": "V45 lists the ES 3rd-Friday reversal as an exception; ES is outside the universe"}],
    "open_questions": ["The 3rd-Friday reversal is published for ES only; no evidence on NQ, RTY or YM codes.", "GEX data source and cost: not established here (DataAccess)."],
})

SEARCHED_NOT_FOUND = [
    {"topic": "post-2015 CME product study, out of sample and net of costs, at 5 min to the session", "note": "None found for any family on any of the 47 codes in the F2 files (each family reader's searched_not_found lists the queries)."},
    {"topic": "intraday crack-spread, Treasury curve-spread and NG/CL calendar-spread reversion", "note": "F2_crude, F2_rates, F2_natgas: not found."},
    {"topic": "settlement-window directional effects (CL, NG, metals, FX, crypto)", "note": "F2 readers found settlement windows as structure only."},
    {"topic": "NOPA, Export Sales, EPA RFS intraday event studies", "note": "F2_grains and E.32 R4: none."},
    {"topic": "copper and China data; OPEC intraday", "note": "F2_metals, F2_crude: none."},
]
GAPS = [
    "No page was fetched and no WebSearch used: every fact reuses on-disk F2, R1, E.20, E.25, E.32 sources; levels are as those files recorded them.",
    "Huang 2022 and Christensen-Oomen-Reno, Chordia-Roll-Subrahmanyam numbers are taken from E.32 methods brief text (its readers' full-text reads), not re-read here.",
    "Per-family event counts for the scorer's K_year are calendar facts from the F2 items; holiday shifts not counted.",
    "Overlap 'how' notes are R1 extraction facts; whether a combination re-tests a closed line is the CombinationScorer's and the lead's judgment.",
]
NOTICES = []
