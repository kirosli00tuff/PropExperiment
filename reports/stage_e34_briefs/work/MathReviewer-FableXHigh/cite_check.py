"""Citation spot-check: for each (label, file, cited line(s), needle) find lines containing the needle
and report whether a hit lies within +-3 lines of the cited line. Reads only text files already on disk."""
import sys
from pathlib import Path

R = Path("/home/kiros-li/Documents/GitHub/PropExperiment")
B = R / "reports/stage_e34_briefs"
M1P = B / "work/MathReaderM1-OpusHigh/pages"
M2P = B / "work/MathReaderM2-OpusHigh/pages"
M3P = B / "work/MathReaderM3-OpusHigh/pages"
BRIEF = R / "reports/stage_e32_methods_brief.md"
PROTO = R / "reports/stage_e32_discovery_protocol.md"
RECS = R / "reports/stage_e32b_recommendations.md"
HOLD = R / "reports/stage_e32b_holding_scope.md"
E32PAGES = R / "reports/stage_e32_briefs/pages/R3a_crush"

CHECKS = [
    # M1 Databento pages
    ("M1 DB-mbp1 L6", M1P / "schemas_mbp-1.md", 6, "provides every order book event that updates the top price level"),
    ("M1 DB-mbp1 L21", M1P / "schemas_mbp-1.md", 21, "sell aggressor in a trade"),
    ("M1 DB-mbo L6", M1P / "schemas_mbo.md", 6, "keyed by its order ID"),
    ("M1 DB-schema L77", M1P / "schemas_whats-a-schema.md", 77, "are simply derived from MBO data"),
    ("M1 DB-schema L79", M1P / "schemas_whats-a-schema.md", 79, "losslessly on the client side"),
    ("M1 DB-glbx L42", M1P / "datasets_glbx-mdp3.md", 42, "such as MBP-1 and Trades"),
    ("M1 DB-glbx L57", M1P / "datasets_glbx-mdp3.md", 57, "normalized into one"),
    ("M1 DB-glbx L62", M1P / "datasets_glbx-mdp3.md", 62, "modify the orders"),
    ("M1 DB-glbx L70-71", M1P / "datasets_glbx-mdp3.md", 70, "normalized with side set to"),
    ("M1 DB-glbx L104", M1P / "datasets_glbx-mdp3.md", 104, "normal for order books to be locked or crossed"),
    ("M1 DB-glbx L113", M1P / "datasets_glbx-mdp3.md", 113, "publishing the merged top-of-book"),
    ("M1 DB-glbx L299", M1P / "datasets_glbx-mdp3.md", 299, "set to the same value as"),
    ("M1 DB-glbx L301", M1P / "datasets_glbx-mdp3.md", 301, "F_BAD_TS_RECV"),
    ("M1 DB-glbx L315", M1P / "datasets_glbx-mdp3.md", 315, "highest granularity schema available for MDP 2 data is MBP-10"),
    # M1 E.32 brief
    ("M1 brief L3821 CRS", BRIEF, 3821, "In no more than thirty minutes, order imbalances lose their predictive ability"),
    ("M1 brief L3810 CKS R2", BRIEF, 3810, "with an average R2 of 65%"),
    ("M1 brief L3812 CKS acf", BRIEF, 3812, "autocorrelations at a timescale of 10 seconds are small and quickly vanish"),
    ("M1 brief L3814 XGH", BRIEF, 3814, "linear relationship between MLOFI and the contemporaneous change in mid-price"),
    ("M1 brief L3905 Lillo-Farmer", BRIEF, 3905, "decays roughly as"),
    ("M1 brief L3911 Patzelt", BRIEF, 3911, "extreme order flow imbalance is not associated with large returns"),
    ("M1 brief L4350 Volkenand", BRIEF, 4350, "For some contracts, returns can be predicted using lagged order imbalance"),
    ("M1 brief L4351 Jin", BRIEF, 4351, "diminishes over longer measure and price change frequency horizons"),
    ("M1 brief L3663 ZM 0.0120", BRIEF, 3663, "0.0120"),
    ("M1 recs L595-596 V50", RECS, 595, "not a clean holdout"),
    # M2
    ("M2 brief L1500 Janzen", BRIEF, 1500, "a previously stable relationship among soybean crush components has broken down"),
    ("M2 brief L4693 Huth", BRIEF, 4693, "a naive strategy based on market orders cannot make any profit of this effect"),
    ("M2 brief L5071 Boero", BRIEF, 5071, "If they are zero then that particular error correction term does not enter that equation"),
    ("M2 brief L1802-1804 Avileis", BRIEF, 1803, "biofuel-induced price increase in soybean oil leads to"),
    ("M2 brief L1795-1797 Adrangi", BRIEF, 1796, "bear the burden of convergence"),
    ("M2 brief L1798 Liu-Sono", BRIEF, 1798, "one-way information flow from the soymeal and soyoil markets"),
    ("M2 farmdoc 2013 L51", M2P / "farmdoc_fdd180913_biodiesel_prices.pdf.txt", 51, "7.55 pounds of soybean oil per gallon"),
    ("M2 farmdoc 2013 L89-94", M2P / "farmdoc_fdd180913_biodiesel_prices.pdf.txt", 92, "priced biodiesel based on the cost of soybean oil"),
    ("M2 farmdoc 2023 L165-167", M2P / "farmdoc_fdd111323_biodiesel_squeeze.pdf.txt", 166, "lagged in the second half of 2021"),
    ("M2 farmdoc 2023 L78-80", M2P / "farmdoc_fdd111323_biodiesel_squeeze.pdf.txt", 79, "7.50 and 7.55 pounds per gallon"),
    ("M2 Kristoufek L38-39", M2P / "kristoufek_2012_timefreq_biofuels.pdf.txt", 38, "even at high frequencies"),
    ("M2 Kristoufek L80-81", M2P / "kristoufek_2012_timefreq_biofuels.pdf.txt", 80, "transmitted into rapeseed oil prices"),
    ("M2 Zhou L822/880", E32PAGES / "zhou_jcm2023_wur.pdf.txt", 822, "the more soybean will Granger cause soyoil"),
    ("M2 Zhou L881-882", E32PAGES / "zhou_jcm2023_wur.pdf.txt", 881, "even more significantly Granger cause"),
    ("M2 Rechner L278", E32PAGES / "rechner_poitras_1993.pdf.txt", 278, "-0.035"),
    ("M2 Rechner L356", E32PAGES / "rechner_poitras_1993.pdf.txt", 356, "-0.08935"),
    ("M2 seal L117-119", R / "reports/stage_e32_test_seal.md", 118, "for the window was ever bought or read"),
    ("M2 recs L644 test F09", RECS, 644, "F09"),
    ("M2 recs L540", RECS, 540, "slower participant set prices with a delay"),
    # M3
    ("M3 EIA schedule", M3P / "eia_wpsr_schedule.txt", None, "standard release time and day of the week will be at 10:30"),
    ("M3 FBN 4.50 limit", M3P / "fbn_22778_epa_dec2022.txt", None, "4.50"),
    ("M3 Fastmarkets limit down", M3P / "fastmarkets_vegoil_slump_jun2023.txt", None, "limit down during the overnight session"),
    ("M3 Avileis by 3pm L395", E32PAGES / "aveleis_swanson_nccc134_2025.pdf.txt", 395, "by 3pm"),
    ("M3 brief L1965", BRIEF, 1965, "No intraday timing is reported"),
    ("M3 brief L2324-2325 limits", BRIEF, 2324, "removed on the business day prior to first notice day"),
    ("M3 brief L8814 Topstep limit", BRIEF, 8814, "Price Limit%"),
    ("M3 brief L5494-5496 TB", BRIEF, 5495, "realism of the exit, not prediction"),
    ("M3 brief L5429 B-13", BRIEF, 5429, "B-13"),
    ("M3 proto L285 dead zone", PROTO, 285, "The dead zone is the spread plus costs, not a tuned threshold"),
    ("M3 proto L363 re-entry", PROTO, 363, "first grid minute at or after the exit fill time"),
    ("M3 hold L921 G/minG", HOLD, 921, "1.6135"),
    ("M3 hold L929-931 p_be", HOLD, 930, "0.573"),
    ("M3 hold L943-945 latest PT", HOLD, 944, "10:50"),
    ("M3 recs L614 five labels", RECS, 614, "T30"),
    ("M3 DECISIONS L1038-1041 V50 TT", R / "docs/DECISIONS.md", 1039, "trade-through rule unless a firm documents otherwise"),
    ("M3 DECISIONS L1031-1037 V49", R / "docs/DECISIONS.md", 1034, "V49"),
    # M4
    ("M4 proto L777 sealed untested", PROTO, 777, "stay sealed and untested"),
    ("M4 proto L787 K=9", PROTO, 787, "9"),
    ("M4 proto L724 0.164882", PROTO, 724, "0.164882"),
    ("M4 proto L716-718 Holm z", PROTO, 717, "2.902"),
    ("M4 proto L727-729 1.60x", PROTO, 728, "1.60 x"),
    ("M4 recs L512 N838 row", RECS, 512, "0.2007"),
    ("M4 recs L518 N938", RECS, 518, "0.2018"),
    ("M4 recs L520 N1038", RECS, 520, "0.2028"),
    ("M4 recs L521 N1138", RECS, 521, "0.2037"),
    ("M4 recs L506 V52", RECS, 506, "V52"),
    ("M4 recs L551-552 K2", RECS, 551, "1.8 ticks"),
    ("M4 recs L487 D2 open", RECS, 487, "stays open until a test is registered"),
    ("M4 hold L944-946 e80", HOLD, 945, "1.81"),
    ("M4 hold L915 c_f", HOLD, 915, "2.38"),
    ("M4 E33c L194-195 s80", R / "reports/E.33c_RETURN.md", 194, "0.2309"),
    ("M4 E33c L18 embargo", R / "reports/E.33c_RETURN.md", 18, "21-date embargo"),
    ("M4 E32_RETURN L436-440 D2", R / "reports/E.32_RETURN.md", 438, "D2"),
    ("M4 brief L7417 unverified", BRIEF, 7417, "unverified"),
    ("M4 DECISIONS L788-806 V43", R / "docs/DECISIONS.md", 790, "order-book"),
]


def main() -> None:
    ok = 0
    for label, path, line, needle in CHECKS:
        if not path.exists():
            print(f"MISSING-FILE | {label} | {path.name}")
            continue
        lines = path.read_text(errors="replace").splitlines()
        hits = [i + 1 for i, s in enumerate(lines) if needle in s]
        near = [h for h in hits if line is None or abs(h - line) <= 3]
        status = "OK" if near else ("FOUND-ELSEWHERE" if hits else "NOT-FOUND")
        if status == "OK":
            ok += 1
        print(f"{status} | {label} | cited {line} | hits {hits[:6]}")
    print(f"--- {ok}/{len(CHECKS)} OK")


if __name__ == "__main__":
    main()
