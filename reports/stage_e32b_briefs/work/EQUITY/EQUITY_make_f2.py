"""EQUITY helper (Stage E.32b, EquityReader-OpusHigh): build reports/stage_e32b_briefs/F2_equity.json.
Every quote is checked (whitespace-normalised substring) against its source file before writing."""
import csv
import json
import re
import sys

ROOT = "/home/kiros-li/Documents/GitHub/PropExperiment/"
PG = "reports/stage_e32b_briefs/pages/EQUITY/"
E28 = "reports/stage_e28_briefs/pages/A1_equity/"
A1MD = "reports/stage_e28_briefs/A1_equity.md"
EQN = "reports/stage_e20_briefs/shared/equity_class_notes.md"
SB = "reports/stage_e32b_briefs/F2_shared_baltussen.json"
OUT = ROOT + "reports/stage_e32b_briefs/F2_equity.json"
ALL = ["M2K", "RTY", "MYM", "YM", "MNQ", "NQ"]
MICROS = ["MNQ", "M2K", "MYM"]

LOG = {}
with open(ROOT + PG + "log.tsv") as f:
    for r in csv.DictReader(f, delimiter="\t"):
        LOG[r["file"]] = r
E28LOG = {}
with open(ROOT + E28 + "log.tsv") as f:
    for r in csv.DictReader(f, delimiter="\t"):
        E28LOG[r["file"]] = r


def src_new(fn):
    r = LOG[fn]
    return {"file": PG + fn, "field": None, "url": r["url"], "fetched_utc": r["utc_fetch"], "sha256": r["sha256"]}


def src_e28(fn, field=None):
    r = E28LOG.get(fn.replace(".txt", ".pdf").replace(".html.txt", ".html"), E28LOG.get(fn, {}))
    return {"file": E28 + fn, "field": field, "url": r.get("url"), "fetched_utc": r.get("utc_fetch"),
            "sha256": r.get("sha256"), "note": "reused E.28 page (log reports/stage_e28_briefs/pages/A1_equity/log.tsv)"}


def src_file(path, field=None, note=None):
    d = {"file": path, "field": field, "url": None, "fetched_utc": None, "sha256": None}
    if note:
        d["note"] = note
    return d


items = []


def add(codes, topic, field, value, scope, window, detail, quote, source, verified, quote_file=None,
        pointer=False, negative=False):
    items.append({"id": f"EQUITY-{len(items) + 1}", "codes": codes, "topic": topic, "field": field, "value": value,
                  "scope": scope, "window": window, "detail": detail, "quote": quote, "source": source,
                  "verified": verified, "pointer": pointer, "negative": negative,
                  "_qf": quote_file or source["file"]})


# ---------------- T1 spread and touch ----------------
add(["MNQ", "NQ"], "T1", "median_spread_ticks", None, "leader", "2005 (paper); no later figure",
    "Kurov and Zabotina (2005) J. Futures Markets 25, 79-104: the E-mini Nasdaq-100 minimum tick binds the spread "
    "(implies a modal one-tick spread in that era). Abstract only, reused from E.25 RD8 (not re-fetched). No median "
    "spread in ticks is stated.",
    "the current minimum tick sizes of the E-mini S&P 500 and E-mini Nasdaq-100 futures contracts act as binding "
    "constraints on the bid-ask spreads",
    src_file("reports/stage_e25_briefs/RD8_redig_e20_planning.md", "row E24",
             "E.25 saved pages/RD8/repec_kurov_zabotina.html"), "abstract")
add(["MNQ", "NQ"], "T1", "median_spread_ticks", "1 tick (0.25 pt) US session (claimed)", "product", "undated",
    "Broker education page (brokerchooser.com) via WebSearch snippet only, undated, no source given; also claims "
    "0.50-2.00 points overnight. Not fetched. Pointer only; no fact rests on it.",
    "a bid-ask spread of about 0.25 points during the US session and 0.50 to 2.00 points overnight",
    src_file("WebSearch 2026-10-28 (query: CME Micro E-mini Nasdaq-100 MNQ bid-ask spread top of book)",
             note="search-tool summary of https://brokerchooser.com/education/basics/how-to-trade-nasdaq100-futures-small-account"),
    "snippet", quote_file="-", pointer=True)

# ---------------- T2a automated / HFT share ----------------
add(ALL, "T2a", "auto_share_pct", 34.22, "other", "2010-05-03..2010-05-05 (pre-2012)",
    "E-mini S&P 500 (ES), a cousin in the CME equity index product group, not a candidate: HFT share of volume "
    "34.22% (15 accounts) over May 3-5, 2010, CFTC audit-trail data. Slide deck of Kirilenko, Kyle, Samadi, Tuzun "
    "(CFTC economists; paper later JF 2017). Pre-2012, not the product or its leader. CFTC OCE ATS shares for NQ/YM "
    "are RatesReader's shared source (not repeated here).",
    "High Frequency Traders       34.22%        32.56%           15", src_new("kirilenko_flash_crash_wp.pdf"),
    "full_text", quote_file=PG + "kirilenko_flash_crash_wp.pdf.txt")

# ---------------- T2b market-maker programs ----------------
add(MICROS, "T2b", "mm_program", "Micro E-mini Futures Market Maker Program", "product",
    "2019-05-06 to 2022-01-31, extended to 2022-04-30 (CME/CBOT Submission 22-047, effective 2022-02-01)",
    "Outright Micro E-mini futures (MES, MNQ, M2K, MYM) on Globex; up to 10 participants; hours 8:00-15:15 CT and "
    "17:00-08:00 CT. In force in 2021 and early 2022 (the 22-047 filing modifies a live program). Overstrike "
    "convention: the filing says deletions are overstruck; the program being modified effective 2022-02-01 with "
    "'January 31, 2022 April 30, 2022' means the old end 2022-01-31 was extended to 2022-04-30. Status after "
    "2022-04-30 not found.",
    "Product Scope Micro E-mini Standard and Poor’s 500 Stock Price Index Futures (“MES”), Micro E-mini Nasdaq-100 "
    "Index Futures (“MNQ”), Micro E-mini Russell 2000 Index Futures (“M2K”), and Micro E-mini Dow Jones Industrial "
    "Average Index Futures (“MYM”) that are traded on the CME Globex Platform (“Products”).",
    src_new("cftc_rule011222cmedcm004.pdf"), "full_text", quote_file=PG + "cftc_rule011222cmedcm004.pdf.txt")
add(MICROS, "T2b", "mm_program", "Micro E-mini Futures Market Maker Program: term", "product", "2019-05-06..2022-04-30",
    "Program term line of CME 22-047 (see previous item).",
    "Start date is May 6, 2019. End date is January 31, 2022 April 30, 2022.",
    src_new("cftc_rule011222cmedcm004.pdf"), "full_text", quote_file=PG + "cftc_rule011222cmedcm004.pdf.txt")
add(["NQ", "MNQ", "YM", "MYM"], "T2b", "mm_program",
    "CME/CBOT E-mini Equity Index Futures Market Maker Program (ES, NQ, EMD, YM)", "leader",
    "2013-04-01 to 2021-01-31 (2019 filing; end date read by the overstrike convention)",
    "Reused from E.28 (A1_equity.md NQ sheet; JSON [1].market_maker_program). The 2019 filing (effective "
    "2019-02-01) reads 'End date is January 31, 2019 January 31, 2021'; by the same convention as CME 22-047 the new "
    "end is 2021-01-31, so the program was in force in January 2021 unless ended early. No later filing for this "
    "outright program found (3 WebSearches, 2026-10-28). For MNQ/MYM this is the leader's program.",
    "\"Product Scope E-mini S&P 500 Futures (\"ES\"), E-mini Nasdaq-100 Futures (\"NQ\"),",
    src_file(A1MD, "[1].market_maker_program (A1_equity.json)",
             "E.28 page cftc_rule012819_emini_eq_mm_program.txt"), "reused")
add(["RTY", "M2K"], "T2b", "mm_program", "E-mini Russell 2000 Futures Market Maker Program", "leader",
    "2017-07-10 to 2018-03-31 (overstrike reading); status 2021-2026 not found",
    "Reused from E.28 F5. No 2020-2026 filing for an RTY outright program found (WebSearch 2026-10-28). For RTY "
    "itself (2021-2026): not found. M2K is covered by the Micro program above.",
    "E-mini Russell 2000 Futures Market Maker Program (RTY): cftc_rule053017_RTY_mm_program.txt",
    src_file(A1MD, "F5", "E.28 page cftc_rule053017_RTY_mm_program.txt"), "reused")
add(["NQ", "MNQ", "RTY", "M2K"], "T2b", "mm_program",
    "E-mini TACO Futures Market Maker Program (TACO on ES, NQ, RTY: ESQ, NQQ, RTQ)", "leader",
    "2018-07-16 to 2026-01-31 (CME 24-509, effective 2025-02-01)",
    "Covers Trade-at-Cash-Open (TACO) contracts on NQ and RTY, not the outright NQ/RTY futures; the lead decides "
    "whether it counts. Not YM.",
    "TACO on E-mini S&P 500 Futures (“ESQ”), E-mini Nasdaq-100 Futures (“NQQ”), and E-mini Russell 2000 Futures "
    "(“RTQ”) that are traded on the CME Globex Platform (“Products”).",
    src_new("cftc_rules1202249986.pdf"), "full_text", quote_file=PG + "cftc_rules1202249986.pdf.txt")
add(ALL, "T2b", "mm_program", "E-mini Equity Index Futures BTIC Market Maker Program (NQT, RLT, YMT, ...)", "leader",
    "2015-11-16 to 2026-01-31 (CME/CBOT 24-576, effective 2025-02-01)",
    "Covers BTIC (basis trade at index close) contracts on NQ, RTY and YM, not the outright futures. Hours RTH "
    "8:30-15:00 CT.",
    "BTIC on E-mini Standard and Poor's 500 Stock Price Index® Futures (“EST”), BTIC on E-mini NASDAQ "
    "100 Index® Futures (“NQT”), BTIC on E-mini Russell 1000 Index Futures (“R1T”), BTIC on E-mini Russell "
    "2000 Index Futures (“RLT”), BTIC CBOT E-mini Dow Jones Industrial AverageSM Index Futures ($5 "
    "Multiplier) (“YMT”)",
    src_new("cftc_rules12202412493.pdf"), "full_text", quote_file=PG + "cftc_rules12202412493.pdf.txt")
add(ALL, "T2b", "mm_program", "E-mini Equity Index Futures TMAC Market Maker Program (NQX, RTX, YMX)", "leader",
    "2023-07-31 to 2025-01-31 (CME 23-541, effective 2024-02-01)",
    "Covers Trade-at-Marker-at-Close (TMAC) contracts on NQ, RTY and YM, not the outright futures.",
    "TMAC on E-mini S&P 500 Index Futures (“ESX”), TMAC on E-mini Nasdaq 100 Index Futures (“NQX”), "
    "TMAC on E-mini Russell 2000 Index Futures (“RTX”), and TMAC on CBOT E-mini Dow Jones Industrial "
    "Average Index Futures ($5 Multiplier) (“YMX”) that are traded on Globex (“Products”).",
    src_new("cftc_rules1221239990.pdf"), "full_text", quote_file=PG + "cftc_rules1221239990.pdf.txt")
add(ALL, "T2b", "mm_program", "E-nano Equity Index Futures Market Maker Program (NES, NNQ, N2K, NDOW)", "sibling",
    "2026-08-24 to 2027-03-31 (CME/CBOT 26-377)",
    "Covers new E-nano contracts on the same underlyings (Nasdaq-100, Russell 2000, DJIA), not any candidate code. "
    "Also a T3 fact: E-nano siblings exist from 2026-08 (size not read here).",
    "E-nano Standard and Poor's 500 Stock Price Index Futures (“NES”), E-nano Nasdaq-100 Index Futures "
    "(“NNQ”), E-nano Russell 2000 Index Futures (“N2K”), and E-nano Dow Jones Industrial Average Index "
    "Futures (“NDOW”)",
    src_new("cftc_rules08072614627.pdf"), "full_text", quote_file=PG + "cftc_rules08072614627.pdf.txt")

# ---------------- T3 structural relationships ----------------
add(ALL, "T3", "relationship", "micro/mini pairs MNQ-NQ, M2K-RTY, MYM-YM (10:1, mechanical)", "sibling",
    "since 2019-05-06",
    "Type: mechanical (mini/micro on the same index). Rule 589 'Associated' for price limits; Rule 855 offsets 10 "
    "micros per mini; same final SOQ; micro daily settlement taken from the E-mini's VWAP (see T5). No intraday "
    "lead-lag study found beyond Fassas (2021, abstract only, see T5).",
    "Micro E-mini NASDAQ-100 Index Futures ... MNQ Associated NQ",
    src_file(A1MD, "F1", "E.28 page cftc_ptc041519_micro_emini_launch.txt"), "reused")
add(["MNQ", "NQ", "RTY", "M2K"], "T3", "relationship", "NQ leads ES and Russell 2000 futures at 60-min chart extrema",
    "leader", "60-min bars 2004-09..2014-05-15 (Russell on ICE then)",
    "Maier-Paape and Platen (2015) arXiv 1504.06235 (preprint, technical-analysis method, local extrema of 60-min "
    "charts, directional statistics; no trading test, no costs). Table 2 (time of extrema), asterisk = leading "
    "market, lag column in minutes: E-mini Nasdaq leads E-mini S&P by about 8.7-12.3 min; Nasdaq leads Russell 2000 "
    "(ICE) by about 8.0-11.3 min; Russell leads E-mini S&P by about 4.7-5.0 min. Type: cross-asset lead-lag at "
    "minute-plus horizons, horizons of chart swings (not a return-predictability regression).",
    "CME MINI NSDQ∗       CME MINI S&P             0.035 ± 0.005    0.013 ± 0.002    12.253 ± 1.746",
    src_new("arxiv_1504.06235.pdf"), "full_text", quote_file=PG + "arxiv_1504.06235.pdf.txt")
add(["MYM", "YM"], "T3", "relationship", None, "underlying", "-",
    "No sourced intraday lead-lag or cointegration study for Dow futures (YM) against ES/NQ found (searched with the "
    "NQ/RTY queries). Mechanical only: MYM-YM pair (above).", None, src_file("-"), "reused", quote_file="-",
    negative=False)
add(ALL, "T3", "relationship", "quarterly calendar spreads (Mar, Jun, Sep, Dec)", "product", "current",
    "Type: calendar (mechanical). NQ lists quarterly contracts for 5 consecutive quarters (old spec page, Wayback). "
    "No intraday calendar-spread mean-reversion study found.",
    "Quarterly contracts (Mar, Jun, Sep, Dec) listed for 5 consecutive quarters",
    src_e28("cme_old_specs_e-mini-nasdaq-100.html.txt"), "reused",
    quote_file=E28 + "cme_old_specs_e-mini-nasdaq-100.html.txt")

# ---------------- T4 scheduled events ----------------
add(ALL, "T4", "event", "NFP, CPI, PPI, GDP 08:30 ET; ISM 10:00 ET; FOMC statement 14:00 ET (14:15 before 2013)",
    "futures_broad", "2010-2024 calendars",
    "Shared US macro calendar (no product-specific weekly release for equity index futures: E.28 F9). Reused from "
    "E.20 shared/macro_calendars.md section 3.",
    "| FOMC statement (14:00; 14:15 or 12:30-12:35 before 2013) |",
    src_file("reports/stage_e20_briefs/shared/macro_calendars.md", "section 3"), "reused")
add(ALL, "T4", "event", "continuing adjustment 10-30 min after macro releases; pre-release drift 30 min before",
    "other", "2008-01..2014-03, second-by-second",
    "Kurov, Sancetta, Strasser, Wolfe (2015 draft; published JFQA 2019) on E-mini S&P 500 (cousin) and 10-year note "
    "futures, 30 US announcements. 7 of 18 market-moving announcements show pre-announcement drift starting about 30 "
    "min before release (about half of the total move; 64% mean for ES in Table 5). Post-release: 'some evidence of "
    "continuing adjustment' in [t+10min, t+30min] (joint test, all 30 announcements). Absorption: mostly within "
    "minutes per earlier literature, with some drift to 30 min. Not on NQ/RTY/YM.",
    "a joint test of significance of price moves in the [t + 10min, t + 30min] window for all 30 announcements shows "
    "some evidence of continuing adjustment.",
    src_new("kssw2015_preannouncement_stern.pdf"), "full_text",
    quote_file=PG + "kssw2015_preannouncement_stern.pdf.txt")
add(ALL, "T4", "event", "pre-announcement drift (ES), 7 of 18 releases", "other", "2008-01..2014-03",
    "Same paper, abstract. Direction-correct drift before release; equity-cousin evidence.",
    "For these announcements, prices begin to drift in the “correct” direction about 30 minutes before the "
    "announcement time. The pre-announcement drift accounts on average for about half of the total price adjustment.",
    src_new("kssw2015_preannouncement_stern.pdf"), "full_text",
    quote_file=PG + "kssw2015_preannouncement_stern.pdf.txt")
add(ALL, "T4", "event", "macro-news shocks dissipate within one second (ES order flow)", "other", "see E.28 R5",
    "Takahashi (2025) arXiv 2508.06788, abstract only (reused E.28 F11 R5). Absorption within seconds; order-flow "
    "impact, not a 5-min drift.",
    "Impulse responses indicate that shocks dissipate almost entirely within a second.",
    src_file(A1MD, "F11 R5"), "abstract")
add(ALL, "T4", "event", "FOMC-day intraday momentum stronger (SPY): 20.04%/yr vs 6.24%/yr", "other_venue",
    "SPY 1993-02..2013-12",
    "Gao, Han, Li, Zhou (JFE 2018; WP 2015 text) Table 8: on FOMC release days (2:15 pm schedule) the first-half-hour "
    "sign predicts the last half hour more strongly; the last half hour (15:30-16:00) follows the 14:15 statement by "
    "75+ min. Gross. Reused from E.20 shared/equity_class_notes.md S1 (full text read there).",
    "\"Non-Release FOMC 6.24***\n  6.20 1.01\" and \"Release FOMC 20.04** 5.84 3.43\"",
    src_file(EQN, "S1"), "reused")
add(ALL, "T4", "event", "pre-FOMC drift (SPX, 24 h before statement) and its disappearance after 2015", "underlying",
    "1994-09..2011-03; extended to 2019-12",
    "Lucca and Moench (NY Fed SR 512 / JF 2015, full text in E.20): about 49 bp in the 24 h before scheduled FOMC "
    "announcements, mostly the morning of the announcement; flat after 14:15. Kurov, Wolfe, Gilbert (FRL 2021, "
    "abstract only): 'essentially disappeared after 2015'. Pre-release, not post-release drift. Reused E.20 S6, S7.",
    "the pre-FOMC drift essentially\n  disappeared after 2015",
    src_file(EQN, "S7"), "reused", negative=True)

# ---------------- T5 settlement and price discovery ----------------
add(MICROS, "T5", "settlement_basis",
    "financial; final = Special Opening Quotation (SOQ) of the index, same SOQ as the E-mini", "product",
    "since listing 2019-05-06",
    "CME 19-140 launch filing, contract terms (chapters 353/361/363 CME; MYM CBOT). Final settlement is the index "
    "SOQ, not a sibling's settlement price.",
    "Delivery is by cash settlement by reference to the Final Settlement Price, equal to the Special Opening "
    "Quotation of the Index based on the opening prices of the Index component stocks on the Last Day of Trading.",
    src_e28("cftc_ptc041519_micro_emini_launch.txt"), "reused",
    quote_file=E28 + "cftc_ptc041519_micro_emini_launch.txt")
add(MICROS, "T5", "settlement_basis", "daily settlement = 30-s VWAP of the E-mini counterpart", "sibling",
    "CME FAQ, Wayback 2024 copy (time window shown is the pre-2020-10-26 one)",
    "Micro daily settlement prices are taken from the E-mini counterpart's Globex VWAP (relevant to D4 Sat (ii): "
    "daily marks off a sibling, while the final settlement is the index SOQ). The FAQ's 4:14:30-4:15:00 pm ET "
    "window predates the 2020-10-26 move of equity settlement to 15:00 CT (E.16 R-S6); the current window was not "
    "verified.",
    "Daily settlement for Micro E-mini futures are based on the 30-second volume-weighted average price (VWAP) of "
    "CME Globex trades between 4:14:30 p.m. and 4:15:00 p.m. ET of their E-mini counterpart.",
    src_e28("cme_micro_emini_faq.html.txt"), "reused", quote_file=E28 + "cme_micro_emini_faq.html.txt")
add(MICROS, "T5", "settlement_basis", "final SOQ identical to the E-mini's", "sibling", "CME FAQ (Wayback 2024)",
    "Same FAQ.",
    "The Micro E-mini will have the same SOQ value as the corresponding E-mini contract on final settlement day.",
    src_e28("cme_micro_emini_faq.html.txt"), "reused", quote_file=E28 + "cme_micro_emini_faq.html.txt")
add(["RTY"], "T5", "settlement_basis", "financial; final = SOQ of the Russell 2000", "product", "since 2017-07-10",
    "CME 17-110 RTY listing filing.",
    "Delivery is by cash settlement by reference to Final Settlement Price, equal to Special Opening Quotation of",
    src_e28("cftc_ptc041317_cme003_RTY_listing.txt"), "reused",
    quote_file=E28 + "cftc_ptc041317_cme003_RTY_listing.txt")
add(["NQ", "YM"], "T5", "settlement_basis", "financially settled (index SOQ, by analogy with the micro chapters)",
    "product", "old spec pages, Wayback 2020-12..2021-01",
    "The old NQ and YM spec pages say 'Financially Settled'; the SOQ wording for NQ/YM chapters 359/27 was not "
    "fetched (micro and RTY chapters state SOQ).",
    "Settlement Method\nFinancially Settled",
    src_e28("cme_old_specs_e-mini-nasdaq-100.html.txt"), "reused",
    quote_file=E28 + "cme_old_specs_e-mini-nasdaq-100.html.txt")
add(["MNQ", "NQ"], "T5", "info_share", "E-mini NQ > 80% of Nasdaq-100 price discovery (vs QQQ ETF and floor ND)",
    "leader", "1-s resolution, 2000-03-01..2000-05-31",
    "Hasbrouck (2003, J. Finance 58(6)) working-paper version FIN-00-046 (NYU). Information shares: the E-mini "
    "dominates; QQQ and the regular contract roughly equal. Pre-2010; MNQ did not exist.",
    "As with the S&P 500, the E-mini contract dominates, providing over 80% of the price discovery.",
    src_new("hasbrouck_2000_fin00046.pdf"), "full_text", quote_file=PG + "hasbrouck_2000_fin00046.pdf.txt")
add(MICROS, "T5", "info_share", "micros contribute approximately equal shares with the E-minis (first 3 months)",
    "sibling", "three months after 2019-05-06 (intraday)",
    "Fassas (2021) J. Derivatives, doi 10.3905/jod.2021.1.131; abstract only (reused E.28 F9; full text not found "
    "again 2026-10-28: Thessaly repository has no file). Shares not given in the abstract.",
    "contribute approximately equal amounts to the information transmission process with the established E-Mini\n"
    "  index futures.",
    src_file(A1MD, "F9"), "abstract")

# ---------------- T6 intraday directional evidence ----------------
SBD = json.load(open(ROOT + SB))
SBI = {it["id"]: it for it in SBD["items"]}
for sid, codes, note in [("SB-9", ["MNQ", "NQ"], "NQ futures"), ("SB-10", ["M2K", "RTY"], "Russell 2000 futures (ER)"),
                         ("SB-8", ["MYM", "YM"], "Dow futures"), ("SB-30", ["MNQ", "NQ"], "Nasdaq-100 cash index"),
                         ("SB-29", ["MYM", "YM"], "DJIA cash index"), ("SB-1", ALL, "equity asset class pooled")]:
    it = SBI[sid]
    add(codes, "T6", "directional_study", it["value"], it["scope"], it["window"],
        f"Baltussen, Da, Lammers, Martens (2021) JFE, {note}: last-30-min return predicted by prev-close-to-close-30 "
        f"return; horizon 30 min; in sample with recursive OOS R2; gross of costs; data ends 2020-05. Peer-reviewed. "
        f"Full item in {SB} {sid}.",
        it["quote"], {"file": SB, "field": f"items[{sid}]", "url": it["source"]["url"],
                      "fetched_utc": it["source"]["fetched_utc"], "sha256": it["source"]["sha256"]},
        "reused", quote_file=it["source"]["file"])
add(ALL, "T6", "directional_study", "not net of costs; ES positive net Sharpe at 1 tick (one sentence)",
    "futures_broad", "1974-2020", "Baltussen et al. costs statement; see " + SB + " SB-6.",
    SBI["SB-6"]["quote"].split(" ... ")[0],
    {"file": SB, "field": "items[SB-6]", "url": SBI["SB-6"]["source"]["url"], "fetched_utc": None,
     "sha256": SBI["SB-6"]["source"]["sha256"]}, "reused", quote_file=SBI["SB-6"]["source"]["file"])
add(ALL, "T6", "directional_study", "first-half-hour sign -> last half hour, SPY: 6.67%/yr, SR 1.08 gross",
    "other_venue", "1993-02..2013-12",
    "Gao, Han, Li, Zhou, JFE 129 (2018) (WP Dec 2015 text read in E.20). Horizon 30 min (15:30-16:00 ET). In sample "
    "plus out-of-sample timing table. Net of spread 2005-2013: 6.52%/yr vs 7.96% gross (Table 10). SPY is another "
    "venue on the S&P 500, a cousin underlying. Reused E.20 S1.",
    "the average return of the timing strategy\n  using the sign of the first half-hour return is 6.67% per annum",
    src_file(EQN, "S1"), "reused")
add(["M2K", "RTY"], "T6", "directional_study", "IWM (Russell 2000 ETF): first half hour -> LH, OOS R2 2.43%, 11.72%/yr",
    "other_venue", "2000-05-26..2013-12-31",
    "Gao et al. Table 12 (mean-variance form, gross). Russell 2000 ETF: same underlying, other venue. Reused E.20 S1.",
    "\"IWM 11.72*** 7.70 2.51 2.43\n  11.72\"", src_file(EQN, "S1"), "reused")
add(ALL, "T6", "directional_study", "first half hour -> last half hour, S&P 500 cash: 6.567%/yr, Sharpe 1.115",
    "other", "2005-10..2017-12",
    "Li, Sakkas, Urquhart (J. Financial Markets 57, 2022), 16 developed cash indices; US = .SPX; gross; cash index "
    "not tradable. Reused E.20 S5.",
    "\"US ITSM 6.567 5.892 0.086 3.099 1.115\"", src_file(EQN, "S5"), "reused")
add(ALL, "T6", "directional_study", "ES hourly momentum turns to reversal when dealer net gamma is high (2018-2024)",
    "other", "2018-01..2024-12, 10-min marks, 9:30-16:00 ET",
    "Adams, Dim, Eraker, Fontaine, Ornthanalai, Vilkov (draft 2026-07-15), E-mini S&P. 60-min momentum return by "
    "net-gamma quartile: Q1 +0.633 bp, Q4 -1.144 bp, Q4-Q1 -1.777 bp (t -3.93); unconditional decay/regime evidence "
    "after 2018; gross; needs option-position data. Unpublished draft, full text read in E.20 (S3).",
    "negative momentum returns (or positive reversal returns) of around\n  1-2 bps across the investment horizons for "
    "the higher level of net gamma.", src_file(EQN, "S3"), "reused", negative=True)
add(ALL, "T6", "directional_study", "SPX ROD -> LH slope +0.006 (t 0.6), flat every year 2022-2026", "other",
    "2022-04-14..2026-08-20, 1,085 sessions",
    "firmtape blog on dev.to (unreviewed practitioner post): pointer only. Conditional on short-gamma closes slope "
    "+0.055 (t 3.1). Reused E.20 S4.",
    "\"Flat overall, flat in every single year,\n  signs alternating.\"", src_file(EQN, "S4"), "reused",
    pointer=True, negative=True)
add(["MNQ", "NQ", "MYM", "YM"], "T6", "directional_study",
    "overnight return -> last half hour: predictability disappears out of sample", "leader",
    "[unverified snippet: S&P 500, Nasdaq 100, DJIA futures, 1997-09..2020-12]",
    "Rosa, J. Futures Markets 42(12) 2022, peer-reviewed; abstract only (full text closed; E.20 shared/"
    "rosa_2022_notes.md). Threshold strategy beats always-on; no numbers. Product list from search snippets only.",
    "The predictability disappears in the\n> out‐of‐sample period.",
    src_file("reports/stage_e20_briefs/shared/rosa_2022_notes.md", "Abstract"), "abstract", negative=True)
add(ALL, "T6", "directional_study", "noise-area intraday momentum SPY: 6.2%/yr net unlevered, Sharpe 0.61",
    "other_venue", "2007-2024",
    "Zarattini, Aziz, Barbon WP 2025 (practitioner co-authors), SPY, net of $0.0035/share commission; intraday "
    "holds; no per-trade bp. Reused E.20 S10.",
    "\"Momentum Opp.Band 100% 178% 6.2% 10.9% 0.61 54%\"", src_file(EQN, "S10"), "reused")
add(["MNQ", "NQ"], "T6", "directional_study", "14 OHLCV signal families on MNQ 5-min: none passes; most below friction",
    "product", "947 days 2021-2025; OOS years 2023-2025",
    "Mesfin (2026) arXiv 2605.04004 (single-author preprint, unreviewed), walk-forward OOS, net of 2.0 MNQ points "
    "friction. No ROD->LH test. Full text saved by E.20 (pages/NQ/arxiv_2605.04004.txt lines 19-27).",
    "Eleven signal families fail because their maximum gross return before\nfriction is 0.07 to 1.50 points per trade, "
    "below the 2.0-point MNQ friction floor.",
    src_file("reports/stage_e20_briefs/pages/NQ/arxiv_2605.04004.txt", "lines 19-27"), "reused", negative=True)
add(["MNQ", "NQ"], "T6", "directional_study",
    "ICT AMD signal on NQ 15-min: no directional information beyond the daily trend regime", "product",
    "2022-01-01..2026-07-01, 15-min Databento bars, 484 signal days",
    "Taylor (2026) arXiv 2610.35887 (single-author preprint, unreviewed). In sample, chi-square with BH correction; "
    "daily accuracy, no entry/exit, costs only in a 6-trade secondary table. Trend regime = daily 20-EMA with a 0.5% "
    "band (whether same-day close is used was not established: possible look-ahead). Null for the signal itself.",
    "AMD model, no directional information beyond the daily trend regime was observed:",
    src_new("arxiv_2610.35887v1.pdf"), "full_text", quote_file=PG + "arxiv_2610.35887v1.pdf.txt", negative=True)
add(["MNQ", "NQ"], "T6", "directional_study", "excluded: horizon under 5 minutes (OFI, queue depletion, +/-3-tick race)",
    "product", "20 RTH sessions",
    "excluded: <5 min. Rodas (2026) SSRN, abstract only (E.28 F11 R1): OFI and depletion carry no direction on NQ.",
    "Neither feature departs measurably from the unconditional base rate",
    src_file(A1MD, "F11 R1"), "abstract", negative=True)
add(ALL, "T6", "directional_study", "persistence 2008-2024 in 20 futures; mostly not cost-feasible", "futures_broad",
    "2008-01..2024-10",
    "Aalto master's thesis (metadata/abstract only; E.20 shared/aalto_thesis_notes.md; quoted in product_NQ.md E8). "
    "No figures.",
    "most intraday momentum and reversal trading strategies may not be feasible after transactions costs, especially in "
    "bond and currency futures",
    src_file("reports/stage_e20_briefs/product_NQ.md", "section 1 row E8"), "abstract")

# ---------------- T7 session structure ----------------
add(ALL, "T7", "session", "Globex Sun-Fri 18:00-17:00 ET, daily 17:00-18:00 ET break; 16:15-16:30 ET halt removed "
    "from 2021-06-28", "product", "since 2021-06-28",
    "Reused E.28 F3 (CME 20-244 halt removal; old spec pages). Main session = cash 09:30-16:00 ET.",
    "Effective \"Sunday, June 27,\n  2021 for trade date Monday, June 28, 2021.\"", src_file(A1MD, "F3"), "reused")
add(ALL, "T7", "session", "daily settlement 15:00 CT (16:00 ET) from 2020-10-26; 15:15 CT before", "product",
    "2020-10-26 onward",
    "Reused E.16 lead ruling R-S6 (CME/CBOT 20-018). The settlement now coincides with the cash close.",
    "Equity settlement at 15:15 CT until 2020-10-23 (CME/CBOT 20-018, effective trade date 2020-10-26: 15:00)",
    src_file("reports/stage_e16_rulings.md", "R-S6"), "reused")
add(ALL, "T7", "session_handoff", "cash close: last half hour (15:30-16:00 ET) predicted by the rest of day",
    "underlying", "to 2020-05",
    "Baltussen et al. (see T6 items) define the day by the cash session 09:30-16:00 ET; the handoff effect is the "
    "last 30 min before the cash close (and the first 30 min after the cash open as predictor). Horizon 30 min. "
    "Post-2018 evidence weaker (Adams et al., SPX retest).",
    "we select the observations of the S&P E-Mini between 09:30 and 16:00, as these are the trading hours of the "
    "S&P 500.",
    {"file": "reports/stage_e13_briefs/pages/InfoSource/baltussen_etal_2021_jfe.md", "field": None,
     "url": SBI["SB-1"]["source"]["url"], "fetched_utc": SBI["SB-1"]["source"]["fetched_utc"],
     "sha256": SBI["SB-1"]["source"]["sha256"]}, "full_text")
add(ALL, "T7", "session_handoff", "European open 02:00-03:00 ET: ES +3.7%/yr ('overnight drift'); net of spread SR -0.5",
    "other", "1998-01-05..2020-12-31, ES front month, mid quotes",
    "Boyarchenko, Larsen, Whelan, NY Fed SR 917 (rev. 2022; RFS 2023). E-mini S&P (cousin) only. Positive 2:00-3:00 "
    "ET return linked to prior US-close order imbalances; selloffs followed by overnight reversals. Gross SR 1.1; "
    "after bid-ask spreads -0.5 (1:30-3:30: 1.3 gross, 0.3 net). Horizon 60 min. Negative net-of-cost result for a "
    "directional market-order trade on ES.",
    "the largest positive returns are between\n2:00 and 3:00 - the opening of European markets in U.S. Eastern Time "
    "terms (ET) - averaging\n3.7% on an annualized basis (1.48 basis points per day).",
    src_new("nyfed_sr917_overnight_drift.pdf"), "full_text", quote_file=PG + "nyfed_sr917_overnight_drift.pdf.txt")
add(ALL, "T7", "session_handoff", "2:00-3:00 long: SR 1.1 gross, -0.5 after bid-ask spreads", "other",
    "1998-2020", "Same paper, cost statement (also a T6 negative-after-costs item for the ES cousin).",
    "a trading strategy that goes long the S&P 500 futures between 2:00 and 3:00 earns\na Sharpe ratio of 1.1 and "
    "accounting for bid-ask spreads this reduces to −0.5.",
    src_new("nyfed_sr917_overnight_drift.pdf"), "full_text", quote_file=PG + "nyfed_sr917_overnight_drift.pdf.txt",
    negative=True)
add(MICROS, "T7", "session", "20-24% of Micro E-mini equity volume outside US hours", "product", "2023-2024",
    "Reused E.28 F9 (CME press release 2023-03-17; CME OpenMarkets 2024). Not split by product.",
    "\"20% of volume occurs outside of U.S. trading hours\"", src_file(A1MD, "F9"), "reused")

# ---------------- F1 changed facts ----------------
add(["RTY", "M2K"], "F1", "changed_fact", "RTY 217,000 and M2K 85,000 contracts/day (2025 to Oct)", "product",
    "2025, as at October 2025 (page dated 2025-11-18)",
    "Newer published ADV from the index provider (FTSE Russell/LSEG insight page), to be shown beside E.28's ADV "
    "(A0 v_0 / A1_equity.json [2].adv_latest_published and [3].adv_latest_published), not substituted. Promotional "
    "source; all-expiry volume presumably.",
    "E-mini Russell 2000 Index Futures (RTY) have averaged 217,000 traded contracts per day, while Micro E-mini "
    "Russell 2000 Index Futures (M2K) have averaged 85,000 contracts per",
    src_new("lseg_ftse_russell_cme_2025.html"), "full_text", quote_file=PG + "lseg_ftse_russell_cme_2025.html.txt")
add(MICROS, "F1", "changed_fact", "Micro E-mini Futures MM Program ran to at least 2022-01-31 (extended to 2022-04-30)",
    "product", "2022",
    "Old value (E.28 F5 and A1_equity.json [0].market_maker_program): 'Whether the program ran in 2022-2024 was NOT "
    "found'; end date read as 2021-01-31. New: CME 22-047 (see T2b items).",
    "Start date is May 6, 2019. End date is January 31, 2022 April 30, 2022.",
    src_new("cftc_rule011222cmedcm004.pdf"), "full_text", quote_file=PG + "cftc_rule011222cmedcm004.pdf.txt")


# ---------------- verify quotes ----------------
def norm(s):
    s = s.replace("&amp;", "&").replace("‐", "-").replace("‑", "-")
    s = re.sub(r"\s+", " ", s)
    return s.strip()


bad = []
for it in items:
    qf, q = it.pop("_qf"), it["quote"]
    if qf in ("-",) or q is None or it["verified"] == "snippet":
        continue
    text = norm(open(ROOT + qf, errors="ignore").read())
    if norm(q) not in text:
        bad.append((it["id"], qf, q[:70]))
if bad:
    for b in bad:
        print("QUOTE MISS", b)
    sys.exit(1)

doc = {
    "family": "equity", "worker": "EquityReader-OpusHigh", "codes": ["M2K", "RTY", "MYM", "YM", "MNQ"],
    "leader_facts_for": ["NQ (excluded V49; leader of MNQ)"],
    "started_pdt": "2026-10-28 22:48", "finished_pdt": sys.argv[1] if len(sys.argv) > 1 else None,
    "websearch_calls": int(sys.argv[2]) if len(sys.argv) > 2 else None, "fulltext_reads_t6": 3,
    "notices": [],
    "items": items,
    "searched_not_found": [
        {"codes": ALL, "topic": "T1", "queries": [
            "E-mini Nasdaq-100 futures median bid-ask spread ticks one tick percentage of time Russell 2000 Dow futures liquidity",
            "CME Micro E-mini Nasdaq-100 MNQ bid-ask spread top of book quantity liquidity report average contracts",
            "Russell 2000 futures migration ICE to CME 2017 bid-ask spread depth liquidity study"],
         "note": "No sourced median main-session spread or touch size for any of the six (E.28 F10 also found none; "
                 "the CME RTY liquidity report holds data only in an interactive chart). Spec rule S = 1 (u) applies."},
        {"codes": ALL, "topic": "T2a", "queries": [
            "high-frequency OR automated share of volume equity index futures CME E-mini Nasdaq Russell 2000 percent study 2020-2023"],
         "note": "No post-2012 non-CFTC HFT/automated share for NQ, RTY, YM or micros. CFTC OCE series is "
                 "RatesReader's shared source (E.28 F6 has NQ/YM ATS figures 2012-2018)."},
        {"codes": ["NQ", "YM", "RTY"], "topic": "T2b", "queries": [
            "cftc.gov CME E-mini Equity Index Futures Market Maker Program 2021 OR 2022 OR 2023 extension",
            "E-mini Equity Index Futures Market Maker Program modifications January 31, 2022 OR 2021 cftc.gov",
            "cftc.gov CME E-mini Russell 2000 futures Market Maker Program OR Incentive Program 2020-2022"],
         "note": "No outright-futures program filing for NQ, YM or RTY after 2019 found. Programs for TACO, BTIC and "
                 "TMAC contracts on them exist (items). Absence not established."},
        {"codes": ALL, "topic": "T2c", "queries": [
            "retail percent of Micro E-mini equity index futures volume CME 2024-2026"],
         "note": "No retail share of volume; CME says retail participation drove micro growth (qualitative). "
                 "E.28 F13 found none either."},
        {"codes": ALL, "topic": "T3", "queries": [
            "lead-lag relationship E-mini S&P 500 and E-mini Nasdaq-100 OR Russell 2000 futures intraday minutes cointegration",
            "arXiv API: lead-lag AND (E-mini OR index futures)"],
         "note": "Only the 60-min extrema study (item). No minute-level cointegration/lead-lag return study for "
                 "NQ/RTY/YM vs ES found."},
        {"codes": ALL, "topic": "T6", "queries": [
            "intraday momentum last half-hour Nasdaq-100 OR Russell 2000 OR Dow index futures out-of-sample 2021-2024",
            "arXiv API: all:\"intraday momentum\"", "arXiv API: Nasdaq-100/Russell 2000/Dow futures"],
         "note": "No peer-reviewed post-2020 test on NQ, RTY or YM. ACFR conference paper (Zhou) blocked 403 "
                 "(curl and WebFetch); Yu-Rentzler-Wolf 2005 (NQ) not read (pre-2010, E.20 404)."},
    ],
    "per_code": {},
    "gaps": [
        "T1 spread and touch unknown for all six.",
        "T2b: outright NQ/YM program after 2021-01, RTY program after 2018, Micro program after 2022-04: not found.",
        "T5: Fassas (2021) micro information shares: abstract only; current micro daily-settlement window not verified.",
        "T6: no full-text post-2020 directional study on RTY/M2K or YM/MYM; Rosa (2022) full text closed.",
        "KSSW 2017 Skidmore copy 404 (used the 2015 Stern draft instead).",
    ],
}
for c in ["M2K", "RTY", "MYM", "YM", "MNQ", "NQ"]:
    leader = {"M2K": "RTY", "MYM": "YM", "MNQ": "NQ"}.get(c, c)
    settle = ("financial, final = index SOQ (same SOQ as the E-mini); daily settlement = E-mini counterpart's VWAP"
              if c in MICROS else "financial, final = index SOQ")
    sid = {"M2K": "EQUITY-22,EQUITY-23", "MYM": "EQUITY-22,EQUITY-23", "MNQ": "EQUITY-22,EQUITY-23",
           "RTY": "EQUITY-25", "NQ": "EQUITY-26", "YM": "EQUITY-26"}[c]
    doc["per_code"][c] = {"median_spread_ticks": None, "spread_item": None, "touch_size": None, "touch_item": None,
                          "settlement_basis": settle, "settlement_item": sid, "leader": leader,
                          "notes": "NQ excluded (V49): leader facts only" if c == "NQ" else ""}
json.dump(doc, open(OUT, "w"), indent=1, ensure_ascii=False)
print(OUT, len(items), "items; quotes OK")
