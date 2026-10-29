"""NATGAS reader (Stage E.32b F2): builds F2_natgas.json from the item list below and checks every quote
against its saved source file (whitespace-normalised substring match). Prints counts and mismatches only."""
import hashlib, html, json, re, subprocess, sys
from pathlib import Path

R = Path("/home/kiros-li/Documents/GitHub/PropExperiment")
B = R / "reports/stage_e32b_briefs"
P = "reports/stage_e32b_briefs/pages/NATGAS/"
E28 = "reports/stage_e28_briefs/pages/A1_natgas/"
E20P = "reports/stage_e20_briefs/pages/NG/"
A1 = "reports/stage_e28_briefs/A1_natgas.json"
A1MD = "reports/stage_e28_briefs/A1_natgas.md"
E20MD = "reports/stage_e20_briefs/product_NG.md"
E2A = "reports/stage_e2a_costs.md"
E16 = "reports/stage_e16_settlement.json"

LOG = {}
for line in (B / "pages/NATGAS/log.tsv").read_text().splitlines()[1:]:
    f = line.split("\t")
    if len(f) >= 6 and f[5] not in ("-",) and "http=200" in f[3] or (len(f) >= 6 and f[3].startswith("openalex")):
        LOG[f[5]] = {"url": f[0], "fetched_utc": f[1], "sha256": f[4]}


LOG28 = {}  # E.28 log: url, utc, pdt, method, sha256, file, note
for line in (R / E28 / "log.tsv").read_text(errors="replace").splitlines()[1:]:
    f = line.split("\t")
    if len(f) >= 6 and f[4]:
        LOG28[f[5]] = {"url": f[0], "fetched_utc": f[1], "sha256": f[4]}
LOG20 = {}  # E.20 NG log: utc, status, size, sha256, file, url
for line in (R / E20P / "fetch_log.tsv").read_text(errors="replace").splitlines():
    f = line.split("\t")
    if len(f) >= 6 and f[1] == "200":
        LOG20[f[4]] = {"url": f[5], "fetched_utc": f[0], "sha256": f[3]}


def lookup(table, name):
    for cand in (name, re.sub(r"\.txt$", "", name), re.sub(r"\.txt$", ".pdf", name), re.sub(r"\.pdf\.txt$", ".pdf", name)):
        if cand in table:
            return table[cand], cand
    return None, None


def src(file, field=None):
    name = file.split("/")[-1]
    s = {"file": file, "field": field, "url": None, "fetched_utc": None, "sha256": None}
    for prefix, table in ((P, LOG), (E28, LOG28), (E20P, LOG20)):
        if file.startswith(prefix):
            rec, cand = lookup(table, name)
            if rec:
                s.update(rec)
                if cand != name:
                    s["sha256_of"] = cand
    return s


def I(codes, topic, field, value, scope, window, detail, quote, source, verified, pointer=False, negative=False,
      check_file=None):
    return dict(codes=codes, topic=topic, field=field, value=value, scope=scope, window=window, detail=detail,
                quote=quote, source=source, verified=verified, pointer=pointer, negative=negative,
                _check=check_file)


ALL = ["MNG", "QG", "NG"]
items = [
    # ---------------- T1 spread and touch (program measurement, E.2a) ----------------
    I(["NG"], "T1", "mean_spread_ticks", 1.25, "product",
      "5 trade dates (all Wednesdays) 2025-05-14, 2025-08-13, 2025-11-12, 2026-02-11, 2026-04-15; day session 08:00-13:30 CT",
      "Program measurement (Stage E.2a cost model, Databento mbp-1 front contract). TIME-WEIGHTED MEAN quoted spread, "
      "NOT a median: 2 x the mean of the 11 day-session 30-minute buckets' mean half-spread s_b (0.6250 ticks; bucket "
      "range 0.6044-0.6321, i.e. full spread 1.21-1.26 ticks). All 46 buckets incl. overnight: mean full spread 1.449, "
      "max 1.986 ticks (17:00-17:30 CT reopen). E.2a limitation: all five dates are EIA crude (WPSR) Wednesdays; five dates "
      "only. A median spread is not reported by E.2a. Computed by work/NATGAS/NATGAS_e2a_spread.py from "
      "reports/stage_e2a_costs.json products.NG.buckets[].half_spread_ticks.",
      "| 08:00-08:30 | D | 5/5 |  | 0.6235 | 0.6235 | 5 | 5 | 0.000 / 0.000 | 0.6235 / 0.6235 | 1.6690 | 16.690 |",
      src(E2A, "### NG (energy) table; JSON products.NG.buckets[*].half_spread_ticks"), "reused"),
    I(["QG"], "T1", "mean_spread_ticks", 1.22, "product", "same 5 dates; day session 08:00-13:30 CT",
      "Program measurement (E.2a). Time-weighted mean quoted spread, not a median: 2 x mean day-bucket half-spread "
      "0.6099 ticks (range 0.5865-0.6308). QG tick is $0.005/MMBtu (5 NG ticks in price). All-bucket mean full spread "
      "1.257, max 1.547 ticks.",
      "| 08:00-08:30 | D | 5/5 |  | 0.6132 | 0.6132 | 9 | 10 | 0.000 / 0.000 | 0.6132 / 0.6132 | 1.3879 | 17.349 |",
      src(E2A, "### QG (energy) table; JSON products.QG.buckets[*].half_spread_ticks"), "reused"),
    I(["MNG"], "T1", "mean_spread_ticks", 2.414, "product", "same 5 dates; day session 08:00-13:30 CT",
      "Program measurement (E.2a). Time-weighted mean quoted spread, not a median: 2 x mean day-bucket half-spread "
      "1.2072 ticks (range 1.1613-1.2576). MNG tick $0.001/MMBtu = $1. All-bucket mean full spread 2.673, max 5.106 ticks.",
      "| 08:00-08:30 | D | 5/5 |  | 1.1720 | 1.1720 | 3 | 3 | 0.500 / 0.500 | 1.6720 / 1.6720 | 5.2640 | 5.264 |",
      src(E2A, "### MNG (energy) table; JSON products.MNG.buckets[*].half_spread_ticks"), "reused"),
    I(["NG"], "T1", "touch_size", 5, "product", "same 5 dates; day session 08:00-13:30 CT",
      "Program measurement (E.2a). Median displayed size at the best bid / ask per 30-min bucket (rule R4: lower "
      "time-weighted median, pooled over the 5 dates). Day buckets: bid 4-6 (median 5), ask 5 in all 11. Overnight "
      "buckets 3-4.",
      "R4 median: the lower time-weighted median, the smallest size m whose cumulative time share is at least one half, "
      "pooled over the five dates' valid-book time in the bucket.",
      src(E2A, "## Readings of the rule R4; ### NG table columns 'Med. bid', 'Med. ask'"), "reused"),
    I(["QG"], "T1", "touch_size", 10, "product", "same 5 dates; day session",
      "Program measurement (E.2a), as NG: day buckets bid 9-10 (median 10), ask 9-11 (median 10).",
      "| 10:00-10:30 | D | 5/5 |  | 0.6244 | 0.6244 | 10 | 11 | 0.000 / 0.000 | 0.6244 / 0.6244 | 1.4105 | 17.631 |",
      src(E2A, "### QG table 'Med. bid', 'Med. ask'"), "reused"),
    I(["MNG"], "T1", "touch_size", 3, "product", "same 5 dates; day session",
      "Program measurement (E.2a), as NG: day buckets bid 2-3 (median 3), ask 3 in all 11 (13:00-13:30 CT bid 2). E.2a "
      "notes a non-zero depth term for MNG at q_c 6 in 46 of 46 buckets.",
      "| 13:00-13:30 | D | 5/5 |  | 1.2576 | 1.2576 | 2 | 3 | 0.500 / 0.667 | 1.7576 / 1.9243 | 5.6019 | 5.602 |",
      src(E2A, "### MNG table 'Med. bid', 'Med. ask'"), "reused"),
    I(["NG"], "T1", "mean_spread_ticks", "< 1.5 (non-US hours, average)", "product", "Q2 2020",
      "CME marketing article (E.28 reuse): average, not median; non-US hours 5 p.m.-7 a.m. CT; no US-hours number.",
      "Throughout Q2, US spreads remained fairly steady. Though non-US spreads were slightly elevated, they remained below 1.5 ticks on average.",
      src(E28 + "cme_liqinsights_henryhub_2020.html.txt", "A1_natgas.json [2].spread_median_ticks_by_session"), "reused",
      check_file=E28 + "cme_liqinsights_henryhub_2020.html.txt"),
    # ---------------- T2a automation ----------------
    I(["NG", "QG", "MNG"], "T2a", "auto_share_pct", 69.9, "product", "2016-11-01..2018-10-31 (63.3 in 2014-11..2016-10)",
      "CFTC Haynes and Roberts (2019 Update #2), NG row, ATS share of volume. Reused from E.28 only as a cross-reference: "
      "the CFTC automation series is the shared source owned by RatesReader (F2_shared_cftc_automation.json); use that file. "
      "Applies to QG and MNG only as their leader's figure (no QG/MNG breakdown exists).",
      "Energy - Natural Gas Natural Gas (Henry Hub) 175 219 63.3 69.9",
      src(E28 + "cftc_ats_update2_2019.txt", "A1_natgas.json [2].hft_automated_share"), "reused",
      check_file=E28 + "cftc_ats_update2_2019.txt"),
    I(["NG"], "T2a", "auto_share_pct", "about 2/3 (HFT, generic claim, unsourced in abstract)", "other", "not stated",
      "Driaunys, Masteika, Sakalauskas, Vaitonis (2014), Transformations in Business & Economics 13(3): the abstract "
      "asserts HFT's share of overall volume in general, not for NG; no source or window given. Weak; listed for completeness.",
      "HFT already generates nearly 2/3 of the overall trading volume",
      src(P + "tbe_33_driaunys.html"), "abstract", check_file=P + "tbe_33_driaunys.html"),
    # ---------------- T2b programs ----------------
    I(["NG", "QG", "MNG"], "T2b", "mm_program",
      "NYMEX Financial Natural Gas Market Maker Program: HH and NG on CME Globex", "product",
      "2017-01-01 .. 2026-07-31, extended to 2027-07-31 (NYMEX Submission 26-350, filed 2026-07-14, effective 2026-08-01)",
      "Scope covers Henry Hub Natural Gas Futures (NG) on Globex (the text does not limit NG to spreads or strips, unlike "
      "the Physical HH program). Hours 7:00AM-3:00PM CT. Obligation: two-sided quotes at predetermined average bid/ask "
      "spreads and minimum sizes for a share of time-in-market. NEW vs E.28 (F1 change). Applies to QG and MNG as their "
      "leader's program.",
      "Natural Gas (Henry Hub) Last-day Financial Futures (“HH”) and Henry Hub Natural Gas Futures (“NG”) that are traded "
      "on the CME Globex Platform (“Products”).",
      src(P + "cftc_rules07142610098.pdf.txt"), "full_text", check_file=P + "cftc_rules07142610098.pdf.txt"),
    I(["NG", "QG", "MNG"], "T2b", "mm_program", "NYMEX Financial NG MM Program term", "product",
      "start 2017-01-01; end 2026-07-31 -> 2027-07-31",
      "Program term line (old end date overstruck, new underlined in the filing).",
      "Start date is January 1, 2017. End date is July 31, 2026 July 31, 2027",
      src(P + "cftc_rules07142610098.pdf.txt"), "full_text", check_file=P + "cftc_rules07142610098.pdf.txt"),
    I(["NG", "QG", "MNG"], "T2b", "mm_program", "Henry Hub Strips Liquidity Provider Program: HH and NG on Globex",
      "product", "2019-10-01 .. 2023-07-31, extended to 2024-07-31 (NYMEX Submission 23-316, filed 2023-07-17)",
      "Named for strips; the product scope text lists NG traded on Globex. NEW vs E.28.",
      "Start date is October 1, 2019. End date is July 31, 2023 July 31, 2024.",
      src(P + "cftc_rules0717234171_HH_strips_LPP.pdf.txt"), "full_text",
      check_file=P + "cftc_rules0717234171_HH_strips_LPP.pdf.txt"),
    I(["NG", "QG", "MNG"], "T2b", "mm_program",
      "Physical Henry Hub (NG) Market Maker Program: deferred NG spreads and strips on Globex", "product",
      "2017-07-01 .. 2024-07-31 (Submissions 21-282, 23-312)",
      "Reused from E.28 F7: scope is deferred spreads and strips, not the front outright.",
      "The purpose of this Program is to build electronic liquidity in deferred Henry Hub spreads, strips, and strip spreads.",
      src(E28 + "cftc_rules071223_NG_MM_program.txt", "A1_natgas.json [2].market_maker_or_incentive_programs"), "reused",
      check_file=None),
    I(["MNG"], "T2b", "mm_program", "NYMEX Micro Natural Gas Futures Market Development Program (volume incentive, MNG on Globex)",
      "product", "2023-11-06 .. 2024-01-31 (NYMEX Submission 23-420, filed 2023-09-26)",
      "Volume-threshold incentive; participants must be proprietary trading firms. NEW vs E.28 (E.28 found none in the "
      "launch filing): F1 change. Later extensions not searched beyond one query (none found).",
      "Micro Henry Hub Natural Gas Futures (“MNG”) that are traded on the CME Globex Platform (“Product”).",
      src(P + "cftc_rules0926237041_MNG_MDP.pdf.txt"), "full_text", check_file=P + "cftc_rules0926237041_MNG_MDP.pdf.txt"),
    I(["MNG"], "T2b", "mm_program", "MNG MDP term and participant class", "product", "2023-11-06 .. 2024-01-31",
      "Term and eligibility lines.",
      "Participants must be classified as a proprietary trading firm.",
      src(P + "cftc_rules0926237041_MNG_MDP.pdf.txt"), "full_text", check_file=P + "cftc_rules0926237041_MNG_MDP.pdf.txt"),
    # ---------------- T2c retail ----------------
    I(["NG"], "T2c", "retail_share", None, "product", "2022-11..2023-10 (COT proxy)",
      "No published retail share found (E.28 and this pass). Proxy only (E.28 F6): COT nonreportable 4.7% of NG open "
      "interest (mean of long 5.9 and short 3.5). QG and MNG: no COT row.",
      "Nonreportable (small-trader proxy) share for NG: 4.7% of OI",
      src(A1MD, "F6; A1_natgas.json [2].nonreportable_share_cot"), "reused", check_file=A1MD),
    # ---------------- T3 relationships ----------------
    I(["NG", "QG"], "T3", "relationship", "NG:QG 1:4 intercommodity spread on Globex", "product",
      "listed from trade date 2024-01-22 (CME Clearing Advisory 23-372)",
      "Mechanical (mini/full pair, same underlying, QG cash-settled off NG). Spread tick 0.00025. No intraday study of the "
      "pair found. Reused from E.28 F1.",
      "NG:QG 1:4 0.00025",
      src(E28 + "cme_chadv23_372_NG_QG_spread.txt", "A1_natgas.md F1"), "reused",
      check_file=E28 + "cme_chadv23_372_NG_QG_spread.txt"),
    I(["MNG", "QG"], "T3", "relationship", "MNG fungible (clearing) with QG and the penultimate financial contracts",
      "product", "current (FAQ, Wayback 2025)",
      "Mechanical; separate Globex books. Reused from E.28 F12.",
      "Micro Henry Hub Natural Gas futures are fungible with E-mini Henry Hub Natural Gas futures",
      src(E28 + "cme_faq_MNG.html.txt", "A1_natgas.md F12"), "reused", check_file=E28 + "cme_faq_MNG.html.txt"),
    I(["NG"], "T3", "relationship", "NG calendar spreads and strips (Globex spread books with MM programs)", "product",
      "2017-2024 programs",
      "Calendar type; documented only as listed spread/strip books with quoting programs (T2b items). No study of "
      "intraday mean reversion in NG calendar spreads found with full text; the HFT stat-arb papers below are abstract-only.",
      "The purpose of this Program is to build electronic liquidity in deferred Henry Hub spreads, strips, and strip spreads.",
      src(A1MD, "F7"), "reused", check_file=A1MD),
    I(["NG"], "T3", "relationship", "NG calendar/inter-contract pairs: HFT statistical arbitrage", "product",
      "data period not stated in abstract",
      "Driaunys, Masteika, Sakalauskas, Vaitonis (2014) TBE 13(3) 'An algorithm-based statistical arbitrage high frequency "
      "trading system to forecast prices of natural gas futures'; NYMEX HF data; claims outperformance; horizon (HFT) and "
      "costs not stated in the abstract. Same group: Masteika and Vaitonis (2015) LNBIP (E.28 F14, abstract only). "
      "Horizon likely under 5 minutes (HFT); not verified.",
      "In this report we apply high frequency data from NYMEX exchange to test a trading system based on statistical "
      "arbitrage in one of the most liquid futures market, i.e. natural gas futures.",
      src(P + "tbe_33_driaunys.html"), "abstract", check_file=P + "tbe_33_driaunys.html"),
    I(["NG"], "T3", "relationship", "NG <-> CL (crude) bidirectional causality in VOLATILITY around inventory releases",
      "underlying", "2003-06-13 start, 380 weeks, 10-minute intervals (to about 2010)",
      "Rosenman and Wolfe [Halova] (2014), Energy Economics (author copy 'Forthcoming'). Economic cross-asset pair; "
      "VOLATILITY-ONLY (no return lead-lag). Gas-inventory news moves oil volatility more than the reverse.",
      "We find that the effect of gas inventory announcements on oil price volatility is more than twice as strong as the "
      "effect of oil inventory announcements on gas price volatility.",
      src(P + "halova_bidirectional_oil_gas.pdf.txt"), "full_text", check_file=P + "halova_bidirectional_oil_gas.pdf.txt"),
    I(["NG"], "T3", "relationship", "NG returns respond to petroleum inventory surprises (cross-product, 15-min window)",
      "underlying", "2003-07-16..2017-06-30",
      "Linn, Ederington, Fernando, Guernsey (2017), EIA workshop slides: in the (-5,+10) minute window NG's response to "
      "the oil-inventory surprise is -0.112***, to its own surprise -1.005***. Economic cross-asset link at the release, "
      "minutes horizon; no lead-lag beyond the window shown.",
      "Natural Gas -0.112*** -0.105*** -0.107*** -1.005***",
      src(P + "eia_linn_2017_presentation.pdf.txt"), "full_text", check_file=P + "eia_linn_2017_presentation.pdf.txt"),
    I(["NG"], "T3", "relationship", "HH -> TTF one-directional Granger causality (daily)", "other_venue",
      "2019-2024, daily front-month futures (NYMEX NG=F and TTF)",
      "Jimenez-Preciado, Venegas-Martinez, Garcia-Perez, Gases 6(3) 30 (MDPI). Economic cross-market pair, DAILY horizon "
      "only; HH-TTF cointegration held in 2019 and broke down from 2020.",
      "Granger causality tests point to a one-directional transmission from Henry Hub to Europe.",
      src(P + "mdpi_gases_06_00030.pdf.txt"), "full_text", check_file=P + "mdpi_gases_06_00030.pdf.txt"),
    # ---------------- T4 events ----------------
    I(ALL, "T4", "event", "EIA Weekly Natural Gas Storage Report (WNGSR), Thursdays 10:30 ET", "underlying", "weekly; holiday weeks move",
      "Reused from E.28 F11. 10:30 ET = 09:30 CT = 07:30 PT, inside the day session.",
      "The standard release time and day of the week will be at 10:30 a.m. eastern time on Thursdays with the following "
      "exceptions.",
      src(E28 + "eia_wngsr_schedule.html.txt", "A1_natgas.json [*].scheduled_releases_per_week"), "reused",
      check_file=E28 + "eia_wngsr_schedule.html.txt"),
    I(ALL, "T4", "event", "WNGSR absorption: price effect complete within the (-5,+10) min window; longer windows similar",
      "underlying", "2003-07-16..2012-06-27",
      "Halova, Kurov, Kucher (2014) JFM 34(10), author copy. Event window 10:25-10:40 ET; footnote 12 says longer windows "
      "give similar results, i.e. no further mean movement documented beyond +10 minutes. Absorbed within about 10 "
      "minutes (no drift claim). OLS understates impact (ITC about 4x OLS for NG).",
      "The results with longer event windows are similar.",
      src(P + "halova_kurov_kucher_2014_noisy.pdf.txt"), "full_text",
      check_file=P + "halova_kurov_kucher_2014_noisy.pdf.txt"),
    I(ALL, "T4", "event", "WNGSR absorption: 5-7 minute response similar to the level at 100 minutes", "underlying",
      "2003-07-16..2017-06-30",
      "Linn, Ederington, Fernando, Guernsey (2017) EIA workshop slides (academic authors, practitioner venue). Slide "
      "'Immediate Response: Oil' says the 5-7 minute response is similar to the level at 100 minutes, and the same holds for "
      "natural gas: absorbed within minutes, no drift to 100 minutes.",
      "5 to 7 minute response relative to level at 100 minutes Similar for Gasoline, Distillate and Natural Gas",
      src(P + "eia_linn_2017_presentation.pdf.txt"), "full_text", check_file=P + "eia_linn_2017_presentation.pdf.txt"),
    I(ALL, "T4", "event", "WNGSR absorption by HFT within 50 ms; no pre-release informed trading", "underlying",
      "millisecond FIX/FAST NG data; period not in abstract",
      "Brigida and Pratt (2019) Studies in Economics and Finance 36(4) 547-566. Absorption in milliseconds; abstract only.",
      "The authors find those who trade within the first 50 ms accurately incorporate the information contained in the "
      "storage report into prices, and earn the majority of profits.",
      src(P + "ideas_brigida_pratt_2018.html"), "abstract", check_file=P + "ideas_brigida_pratt_2018.html"),
    I(ALL, "T4", "event", "WNGSR: volatility elevated up to 30 min after release (VOLATILITY-ONLY)", "underlying",
      "1999-01..2002 (pit era)", "Linn and Zhu (2004) JFM 24(3), reused from E.28 F11.",
      "volatility up to 30 minutes following the announcement was also higher than normal",
      src(E28 + "linn_zhu_2004_JFM_ou.txt", "A1_natgas.md F11"), "reused", check_file=None),
    I(ALL, "T4", "event", "WNGSR announcement-day drift: (-90,+30) min return half pre-, half post-release; died after 2011",
      "underlying", "2003-03..2018-12, 699 announcements, 5-min TRTH; post-2011 subsample",
      "Prokopczuk, Wese Simen, Wichmann (2021) Energy Journal 42(2); full text read by E.20 (accepted version, "
      "pages/NG/prokopczuk_wesesimen_wichmann_2021_ej_accepted.pdf). Mean (-90,+30) return -0.37%: pre (-90,-5) -0.18%, "
      "post (-5,+30) -0.19%. The post part includes the release jump; it is an unconditional negative mean on announcement "
      "days, not a surprise-signed slow adjustment. After 2011: not significant (see T6 item).",
      "Panel B: \"(-90, -5) ... -0.18 ... (-5, 30) -0.19 ... 49.4% 50.6%\"",
      src(E20MD, "section 1 E3 verbatim quotes"), "reused", check_file=E20MD),
    I(ALL, "T4", "event", "Pre-release information: analyst forecasts impounded before release; surprises partly reversed next week",
      "underlying", "not stated in the executive summary (daily data)",
      "Ederington, Lin, Linn, Yang (2019) Energy Journal 40(5), IAEE executive summary (full text of the summary; verifies "
      "E.20's E6 [secondary-only] quote). Daily/weekly horizon, not intraday.",
      "Storage flows higher or lower than analysts had expected one week tend to be partially reversed the following week",
      src(P + "iaee_ederington_2019_execsum.pdf.txt"), "full_text", check_file=P + "iaee_ederington_2019_execsum.pdf.txt"),
    I(ALL, "T4", "event", "WNGSR impact (15-min window) diminished over time", "underlying",
      "856-863 weekly observations (period not stated in saved text)",
      "Farhangdoost and Etienne (2020), AAEA meeting paper (Wayback copy). Impact measured 10:25-10:40 ET only; no "
      "absorption horizon tested.",
      "Overall, EIA's inventory report still contains valuable information for the natural gas market; however, the impact "
      "of EIA inventory reports have diminished over time.",
      src(P + "agecon_farhangdoost_etienne_2020.pdf.txt"), "full_text",
      check_file=P + "agecon_farhangdoost_etienne_2020.pdf.txt"),
    I(ALL, "T4", "event", "26 US macro announcements move NG futures (price drift, volatility, spreads)", "underlying",
      "not in abstract",
      "Boucher, Gagnon, Power (2025) Energy Journal, 'Speculative Trading in Energy Markets: Evidence from Macroeconomic "
      "Surprises'. Abstract only (OpenAlex); 'price drift' horizon unknown. Macro releases (not NG-specific).",
      "We study the impact of twenty-six macroeconomic announcement releases on energy commodities (crude oil, natural gas) "
      "as our baseline case",
      src(P + "openalex_ng_abstracts_1.json"), "abstract", check_file=None),
    I(ALL, "T4", "event", "Weather-model runs (GFS, European) as recurring information flow", "underlying", "trade press 2024-2025",
      "POINTER only: NGI / Energy Intelligence market commentary seen in a WebSearch summary; no study. E.20 E8 lists an "
      "unretrieved 2022 Princeton senior thesis on intraday NG moves on 00 and 18 UTC runs.",
      "December Nymex gas futures declined 11.1¢ Wednesday to $4.232 per million Btu as updated weather forecasts suggested "
      "less space heating demand for gas in mid-November.",
      src("WebSearch summary 2026-10-28 (energyintel.com result); page not saved"), "snippet", pointer=True),
    # ---------------- T5 settlement and price discovery ----------------
    I(["NG"], "T5", "settlement_basis", "physical delivery at Henry Hub", "product", "current rulebook ch. 220",
      "Reused from E.28 F1.",
      "The provisions of these rules shall apply to all natural gas bought or sold for future delivery on the",
      src(E28 + "nymex_rulebook_ch220_NG.txt"), "reused", check_file=E28 + "nymex_rulebook_ch220_NG.txt"),
    I(["QG"], "T5", "settlement_basis", "financial, off NG's final settlement price (sibling settlement)", "product",
      "current rulebook ch. 402 (Wayback 2025)",
      "Floating Price = NG final settlement price for the contract month on QG's last trading day (one business day "
      "before NG's last trade).",
      "The Floating Price for each contract month will be equal to the Henry Hub Natural Gas Futures contract final "
      "settlement price for the corresponding contract month on the last trading day for the E-mini Natural Gas Futures "
      "contract month.",
      src(E28 + "nymex_rulebook_ch402_QG.txt"), "reused", check_file=E28 + "nymex_rulebook_ch402_QG.txt"),
    I(["MNG"], "T5", "settlement_basis", "financial, off NG's final settlement price (sibling settlement)", "product",
      "current rulebook ch. 440 (Wayback 2025)", "Floating Price = NG final settlement price.",
      "The Floating Price for each contract month is equal to the Henry Hub Natural Gas Futures contract (commodity code: "
      "NG; Rulebook Chapter 220) final settlement price for the corresponding contract month on the last trading day for "
      "that contract month.",
      src(E28 + "nymex_rulebook_ch440_MNG.txt"), "reused", check_file=E28 + "nymex_rulebook_ch440_MNG.txt"),
    I(["NG"], "T5", "info_share", "NYMEX NG led on 63% of contract days vs ICE look-alike 20% (price leadership)", "other_venue",
      "2006", "CFTC 2009 Federal Register notice (E9-13871) quoting the Oct 2007 ECM Study. A day-count of price "
      "leadership, not a Hasbrouck information share. NYMEX vs ICE, not NG vs QG/MNG.",
      "In 2006, the ICE's natural gas contract exhibited price leadership on 20 percent of the contract days; the NYMEX's "
      "physically-delivered natural gas contract, on the other hand, exhibited price leadership on 63 percent of the "
      "contract days.",
      src(P + "cftc_fr_e9-13871_ice_hh_spdc.html"), "full_text", check_file=P + "cftc_fr_e9-13871_ice_hh_spdc.html"),
    I(["NG"], "T5", "info_share", "NG futures lead the spot market (price discovery in futures; spot reacts the next day)",
      "underlying", "2002-08..2011-08, daily",
      "Chiou-Wei, Linn, Zhu (2013 working paper, IMF seminar copy via Wayback). Daily horizon; no share number.",
      "We also present direct evidence of price discovery occurring in the futures market for natural gas with that "
      "information then flowing to the spot market.",
      src(P + "imf_2012_chiouwei_linn_zhu_wp.pdf.txt"), "full_text",
      check_file=P + "imf_2012_chiouwei_linn_zhu_wp.pdf.txt"),
    # ---------------- T6 directional ----------------
    I(ALL, "T6", "directional_study", "WNGSR storage-day short (-90,+30): significant 2003-2011, not after 2011; net negative after 2011",
      "product", "2003-03..2018-12 (699 events); post-2011 subsample",
      "Prokopczuk, Wese Simen, Wichmann (2021) Energy Journal 42(2), peer-reviewed; product NG front month; horizon 120 min "
      "around the Thursday release; in sample; gross and net of costs reported. Full sample raw 17.86%/yr (p 0.000), "
      "net 12.21%; after 2011 raw 2.91%/yr (p 0.558), net -0.90%. NEGATIVE after 2011 (gone after costs). Full text read "
      "by E.20 (reuse).",
      "In the more recent period, this has declined to only 3% and a Sharpe ratio of 0.5, which do not withstand "
      "transaction and funding costs.",
      src(E20MD, "section 1 E2 quote; E.20 file pages/NG/prokopczuk_wesesimen_wichmann_2021_ej_accepted.pdf"), "reused",
      negative=True, check_file=E20P + "prokopczuk_wesesimen_wichmann_2021_ej_accepted.pdf.txt"),
    I(ALL, "T6", "directional_study", "Pre-WNGSR drift traded on an analyst-forecast predictor, Sharpe 0.84 (1.26 large predictor)",
      "product", "2008-07..2016-01, 334 announcements",
      "Gu and Kurov (2018) JFM 38(9), read in Gu's WVU dissertation (E.20 reuse). NG; hold 85 min (entry -90, exit -5 min); "
      "needs analyst forecasts (Bloomberg individual forecasts); costs not stated in E.20's reading; in sample (E.20 "
      "reports a 24-month moving average positive to 2016-01, no out-of-sample test noted).",
      "a simple trading strategy that consists of buying (selling) a futures contract 90 minutes before the release time "
      "if the predictor is negative (positive), and closing the position 5 minutes ahead of the announcement would have "
      "earned an annualized Sharpe ratio of 0.84.",
      src(E20MD, "section 1 E4 quote; E.20 file pages/NG/gu_2016_wvu_dissertation_firecrawl.md"), "reused",
      check_file=E20MD),
    I(ALL, "T6", "directional_study", "NG rest-of-day -> last half-hour (14:00-14:30 ET) momentum: beta 3.02 (t 6.15), R2OOS 0.92%",
      "product", "1993-01-06..2020-05-01, 6,824 days, 1-min",
      "Baltussen et al. (2021) JFE 'Hedging demand and market intraday momentum', Table B3 NG row. Shared source owned "
      "by EquityReader (F2_shared_baltussen.json); here cited only as E.20's reuse. Peer-reviewed; product NG; 30-min hold; "
      "out-of-sample R2 positive; gross (no costs). Data mostly pre-2010 plus post-2010 years; post-2020 decay per E.20 "
      "shared baltussen_notes.md (not read here).",
      "| NG | 3.89***(5.49) | 0.68 | 0.61***(5.21) | 3.74***(5.21) | 1.80***(2.58) | 9.20***(3.44) | 1.34 | 0.94*** | "
      "3.02***(6.15) | 1.04 | 0.92*** |",
      src(E20MD, "section 1 E5 quote"), "reused", check_file=E20MD),
    I(ALL, "T6", "directional_study", "Market intraday momentum 'everywhere' (>60 futures incl. commodities)", "futures_broad",
      "about 45 years to 2019", "Lammers (2019) Erasmus MSc thesis (thesis; precursor of the Baltussen et al. JFE paper). "
      "ROD -> last 30 min; in sample and economic significance claimed in the abstract; no per-product detail; abstract only.",
      "The return during the last 30 minutes before the market close is positively predicted by the return during the "
      "rest of the day",
      src(P + "eur_thesis_51180.html"), "abstract", check_file=P + "eur_thesis_51180.html"),
    I(["NG"], "T6", "directional_study", "Statistical arbitrage HFT on NG futures outperforms", "product", "not in abstract",
      "Driaunys et al. (2014) TBE 13(3) and Masteika and Vaitonis (2015) LNBIP: practitioner-grade journal / proceedings; "
      "abstract only; horizon (HFT), costs and sample not given. excluded (probable): horizon likely under 5 minutes; "
      "kept for completeness.",
      "The overall results suggest that statistical arbitrage in HFT environment significantly outperforms traditional "
      "trading strategies",
      src(P + "tbe_33_driaunys.html"), "abstract", check_file=P + "tbe_33_driaunys.html"),
    I(["NG"], "T6", "directional_study", "excluded: spread-crossing prediction (order-book HFT), Kamali 2016 OU dissertation",
      "product", "not in abstract",
      "Kamali (2016) dissertation, University of Oklahoma: SVM predicts occurrence and amplitude of spread crossings from "
      "reconstructed top-of-book data. excluded: order-book horizon (spread crossings), horizon not stated; abstract only.",
      "Predictive modeling techniques based on multi-class support vector machines are used to predict the occurrence and "
      "the amplitude of spread crossings.",
      src(P + "openalex_ng_abstracts_1.json"), "abstract", check_file=None),
    I(["NG"], "T6", "directional_study", "Intraday TSMOM first-to-last half-hour in Chinese commodity futures (not NG)",
      "asset_class", "Chinese copper, steel, soybean, soybean meal",
      "Jin, Kearney, Li, Yang (2020) JFM 40(4); commodity class on another venue (not energy, not CME); abstract only.",
      "Our results indicate that the first half‐hour return positively predicts the last half‐hour return across all four "
      "futures.",
      src(P + "ideas_jfm_v40i4p632.html"), "abstract", check_file=P + "ideas_jfm_v40i4p632.html"),
    I(["NG"], "T6", "directional_study", "Program-internal: E.12 Gate 0 NG h60 not evidence after Holm; C1b backward replication failed",
      "product", "program records (bar features)",
      "Program's own records as cited by E.28 F14; not published; bar features, not a published study. Negative for the "
      "program's library on NG.",
      "The best pair (NG h60, t 2.51) is not evidence after Holm",
      src(A1MD, "F14 table, program-internal row"), "reused", negative=True, check_file=A1MD),
    # ---------------- T7 session ----------------
    I(ALL, "T7", "session_handoff", "Globex Sun-Fri 17:00-16:00 CT, 60-min halt 16:00-17:00 CT", "product", "current",
      "Reused from E.28 F2 (MNG FAQ and filing). Main session per program calendars 08:00-13:30 CT (E.2a D6 day session).",
      "CME Globex: Sunday – Friday: 5:00 p.m. to 4:00 p.m. Central Time (CT)",
      src(E28 + "cme_faq_MNG.html.txt", "A1_natgas.md F2"), "reused", check_file=E28 + "cme_faq_MNG.html.txt"),
    I(["NG", "QG", "MNG"], "T7", "session_handoff", "Settlement window 14:28:00-14:30:00 ET (13:28-13:30 CT), Globex, first six NG months",
      "product", "unchanged 2015-07-06 .. (amended procedure 2019-09-04)",
      "E.16 source S14 (NYMEX Submission 19-198 via cftc.gov). QG/MNG settle daily off their own procedures (not read); "
      "their final settlement is NG's. No study of returns in or around this window found (searched-not-found).",
      "The first six contract months in NYMEX Natural Gas futures (NG) are settled by CME Group staff based on trading "
      "activity on CME Globex between 14:28:00 and 14:30:00 Eastern Time (ET), the settlement period.",
      src(E16, "sources.S14.quote"), "reused", check_file=E16),
    I(ALL, "T7", "session_handoff", "Last half-hour before the NG day close (14:00-14:30 ET) predicted by rest-of-day return",
      "product", "1993-2020", "Same as the Baltussen T6 item: the documented handoff effect into the settlement window "
      "(NG day 9:00-14:30 ET in the paper's Table 1). Shared source; cite F2_shared_baltussen.json.",
      "Natural gas futures NYMEX | NG | 9:00 - 14:30",
      src(E20MD, "section 1 E5 Table 1 quote"), "reused", check_file=E20MD),
    I(ALL, "T7", "session_handoff", "U-shaped intraday volatility, high at the open (VOLATILITY-ONLY, pit era)", "product",
      "1999-2002", "Linn and Zhu (2004) JFM; open-outcry hours; volatility only, no mean effect.",
      "A general U-shaped pattern in the volatilities (ignoring the 2:00–2:05 PM interval) is present across all three "
      "subperiods",
      src(E28 + "linn_zhu_2004_JFM_ou.txt"), "reused", check_file=E28 + "linn_zhu_2004_JFM_ou.txt"),
    I(ALL, "T7", "session_handoff", "News in non-trading periods causes overnight returns (overnight gap)", "product",
      "not stated", "Borovkova and Mahakena (2015) Quantitative Finance 15(7); abstract only (E.28 F11 reuse).",
      "the arrival of news in non-trading periods causes overnight returns",
      src(E28 + "vu_borovkova_mahakena_landing.html.txt", "A1_natgas.md F11"), "abstract",
      check_file=E28 + "vu_borovkova_mahakena_landing.html.txt"),
    # ---------------- F1 changes ----------------
    I(["MNG"], "F1", "changed_fact", "MM/incentive: MNG Market Development Program 2023-11-06..2024-01-31", "product",
      "old value: 'none found' (A1_natgas.json [0].market_maker_or_incentive_programs)",
      "New source: NYMEX Submission 23-420 (see T2b items).",
      "Start date is November 6, 2023. End date is January 31, 2024.",
      src(P + "cftc_rules0926237041_MNG_MDP.pdf.txt"), "full_text", check_file=P + "cftc_rules0926237041_MNG_MDP.pdf.txt"),
    I(["NG"], "F1", "changed_fact", "MM/incentive: Financial NG MM Program covering NG on Globex 2017-01-01..2027-07-31; "
      "HH Strips LPP 2019-10-01..2024-07-31", "product",
      "old value: 'Physical Henry Hub (NG) Market Maker Program for deferred spreads and strips on Globex, "
      "2017-07-01..2024-07-31' (A1_natgas.json [2].market_maker_or_incentive_programs)",
      "Additions, not a replacement: the Physical HH program stands.",
      "End date is July 31, 2026 July 31, 2027",
      src(P + "cftc_rules07142610098.pdf.txt"), "full_text", check_file=P + "cftc_rules07142610098.pdf.txt"),
    I(ALL, "F1", "changed_fact", "spread and touch: program-measured (E.2a) NG 1.25 / QG 1.22 / MNG 2.41 ticks mean; touch 5 / 10 / 3",
      "product", "old values: A1_natgas.json [*].spread_median_ticks_by_session and touch_queue_size = u (NG: '< 1.5 ticks "
      "average in non-US hours (Q2 2020)')",
      "E.2a existed before E.28 but was not cited there; the values are means (spread) and medians (touch).",
      "Sample: mbp-1, the five trade dates 2025-05-14, 2025-08-13, 2025-11-12, 2026-02-11, 2026-04-15",
      src(E2A, "header"), "reused", check_file=E2A),
    I(["NG"], "T3", "relationship", "S&P 500 vs NG (and CL, ethanol) intraday return/volatility linkages vary by aggregation",
      "asset_class", "2010-01..2013-12, 1-minute data aggregated",
      "Caporin, Chang, McAleer (2016) Tinbergen Institute DP 2016-006/III (working paper). Cross-asset pair (equity index vs "
      "NG); mean and variance spillovers and DCCs; the abstract states only that relationships vary with trading range, "
      "overnight vs daily effects and frequency; no NG-specific lead-lag result extracted. Weak.",
      "the relationships between the stock market and alternative energy financial derivatives, specifically futures prices "
      "and returns, can and do vary according to the trading range, whether daily or overnight effects are considered, and "
      "the temporal aggregation and time frequencies that are used.",
      src(P + "tinbergen_16006.pdf.txt"), "full_text", check_file=P + "tinbergen_16006.pdf.txt"),
    I(["NG"], "T3", "relationship", "NG April/May calendar spread is the highest-volume NG calendar spread", "product",
      "December 2016 contract lifetime (CFTC OCE staff paper, Kane, undated in saved text)",
      "Calendar type; the paper explains the April/May spread economically (end of the storage withdrawal season). "
      "Daily liquidity measure only; no intraday mean reversion or lead-lag.",
      "The largest trading volume calendar spread transaction in NG is the April/May spread in the same year.",
      src(P + "cftc_oce_priceimpact.pdf.txt"), "full_text", check_file=P + "cftc_oce_priceimpact.pdf.txt"),
]


def norm(s):
    s = html.unescape(s)
    s = re.sub(r"<[^>]+>", " ", s)
    s = s.replace(" ", " ")
    return re.sub(r"\s+", " ", s).strip()


bad = []
cache = {}
for n, it in enumerate(items, 1):
    it["id"] = f"NATGAS-{n}"
    cf = it.pop("_check")
    if cf and it["quote"]:
        if cf not in cache:
            cache[cf] = norm((R / cf).read_text(errors="replace"))
        q = norm(it["quote"]).replace('\\"', '"')
        if q not in cache[cf] and q.replace('"', "") not in cache[cf]:
            bad.append((it["id"], cf, it["quote"][:80]))

out = {
    "family": "natgas", "worker": "NatgasReader-OpusHigh", "codes": ["MNG", "QG", "NG"],
    "started_pdt": "2026-10-28 22:48 PDT", "finished_pdt": sys.argv[1] if len(sys.argv) > 1 else None,
    "websearch_calls": int(sys.argv[2]) if len(sys.argv) > 2 else None, "fulltext_reads_t6": 0,
    "notices": [],
    "items": [{k: it[k] for k in ["id", "codes", "topic", "field", "value", "scope", "window", "detail", "quote",
                                  "source", "verified", "pointer", "negative"]} for it in items],
}
extra = json.loads((B / "work/NATGAS/NATGAS_extra.json").read_text())
out.update(extra)
(B / "F2_natgas.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
print("items", len(items), "quote mismatches", len(bad))
for b in bad:
    print("  MISMATCH", b)
