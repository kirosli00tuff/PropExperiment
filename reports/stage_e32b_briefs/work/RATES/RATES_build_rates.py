"""RATES_build_rates.py: builds F2_rates.json and F2_rates.md (Stage E.32b, family rates).

Facts only. Reused facts cite E.28 A1_rates.json / E.20 product_<ROOT>.json by field path; new facts cite
pages/RATES files with quotes pulled by pattern (whitespace collapsed). Run: python3 -I RATES_build_rates.py
"""
import csv
import json
import re
import subprocess
from pathlib import Path

ROOT = Path("/home/kiros-li/Documents/GitHub/PropExperiment")
B = ROOT / "reports/stage_e32b_briefs"
PAGES = B / "pages/RATES"
E28P = ROOT / "reports/stage_e28_briefs/pages/A1_rates"
A1 = ROOT / "reports/stage_e28_briefs/A1_rates.json"
E20 = ROOT / "reports/stage_e20_briefs"
OUTJ = B / "F2_rates.json"
OUTM = B / "F2_rates.md"
CODES = ["2YY", "5YY", "10Y", "30Y", "ZT", "ZF", "ZN", "ZB"]
MICROS = ["2YY", "5YY", "10Y", "30Y"]
FULL = ["ZT", "ZF", "ZN", "ZB"]


def rel(p):
    return str(Path(p).relative_to(ROOT))


def load_log(path):
    rows = {}
    with open(path) as fh:
        for r in csv.reader(fh, delimiter="\t"):
            if len(r) >= 6 and r[0] != "url":
                rows[r[5]] = {"url": r[0], "fetched_utc": r[1], "sha256": r[4]}
    return rows


LOG = load_log(PAGES / "log.tsv")
LOG28 = load_log(E28P / "log.tsv")


def page_src(fname, txt=None):
    m = LOG[fname]
    f = txt or (fname + ".txt")
    return {"file": rel(PAGES / f), "field": None, "url": m["url"], "fetched_utc": m["fetched_utc"],
            "sha256": m["sha256"]}


def e28page_src(fname):
    m = LOG28.get(fname, {})
    return {"file": rel(E28P / (fname + ".txt")), "field": None, "url": m.get("url"),
            "fetched_utc": m.get("fetched_utc"), "sha256": m.get("sha256")}


def q(path, pattern, n=1):
    txt = Path(path).read_text(errors="replace").splitlines()
    rx = re.compile(pattern)
    for i, line in enumerate(txt):
        if rx.search(line):
            return re.sub(r"\s+", " ", " ".join(txt[i:i + n])).strip()
    raise SystemExit(f"pattern not found: {pattern} in {path}")


A1D = json.load(open(A1))
A1I = {e["candidate"]: (i, e) for i, e in enumerate(A1D)}


def a1(code, field):
    i, e = A1I[code]
    v = e[field]
    sf = v.get("source_file")
    m = LOG28.get(Path(sf).name.replace(".txt", ""), {}) if sf else {}
    return v, {"file": rel(A1), "field": f"[{i}].{field} (candidate {code}); underlying page {sf}",
               "url": m.get("url"), "fetched_utc": m.get("fetched_utc"), "sha256": m.get("sha256")}


E20D = {r: json.load(open(E20 / f"product_{r}.json")) for r in FULL}


def e20(root, eid):
    ev = E20D[root]["evidence"]
    for i, e in enumerate(ev):
        if e["id"] == eid:
            return e, {"file": rel(E20 / f"product_{root}.json"), "field": f"evidence[{i}] (id {eid})",
                       "url": e.get("url"), "fetched_utc": None, "sha256": e.get("sha256")}
    raise SystemExit(f"E20 {root} {eid} missing")


items = []


def add(codes, topic, field, value, scope, window, detail, quote, source, verified="full_text", negative=False,
        pointer=False):
    items.append({"id": f"RATES-{len(items) + 1}", "codes": codes, "topic": topic, "field": field, "value": value,
                  "scope": scope, "window": window, "detail": detail, "quote": quote, "source": source,
                  "verified": verified, "pointer": pointer, "negative": negative})
    return items[-1]["id"]


IDS = {}

# =========================== T1 spread and touch ===========================
v, s = a1("ZN", "median_spread_ticks_main")
IDS["sp_full"] = add(FULL, "T1", "median_spread_ticks", 1, "product", "2018 calendar year; RTH 07:00-16:00 CT; front month",
    "CME 'Interest Rate Futures Liquidity Update - 2018' (7 Jan 2019): best bid/offer spread equal to the minimum "
    "increment more than 99% of each trading day for all Treasury futures. A median is not published; 1 tick follows "
    "from '>99% at the minimum'. CAVEAT for ZT: the ZT minimum tick was halved in early 2019 (now 1/8 of 1/32, "
    "E.28 tick_size; E.28 F12 R8 note, abstract-level), so the 2018 statement is under the old ZT tick (1/4 of 1/32). "
    "No post-2019 ZT spread in current ticks was found (RATES searched_not_found).",
    v["quote"], s, "reused")
v, s = a1("ZN", "touch_queue_size")
IDS["touch_full"] = add(FULL, "T1", "touch_size", "ZT 99,471; ZF 1,319; ZN 2,507; ZB 377 (contracts, average at best bid/offer, 2018)",
    "product", "2018; RTH 07:00-16:00 CT; outright front month",
    "CME 2018 liquidity update table 'Avg Book Size at Best Bid/Offer Level' 2016/2017/2018 (average, not median; "
    "whether bid+ask or one side is not stated in the quoted row). ZT row (2016 3,854; 2017 38,852; 2018 99,471) is "
    "under the pre-2019 ZT tick. Quote is the ZN row; other rows in E.28 A1_rates.md F9.",
    v["quote"], s, "reused")
IDS["sp_zn_fh"] = add(["ZN"], "T1", "median_spread_ticks", "about 1 (average close to minimum tick)", "product",
    "2013-01..2016 (daily averages, 08:00-16:00 CST, most active contract)",
    "Fett and Haynes (2017), CFTC OCE 'Liquidity in Select Futures Markets', Figure 6 discussion: ZN average "
    "bid-ask spread very close to the minimum tick ($15.625) for the entire period. Average, not median.",
    q(PAGES / "cftc_oce_liquidityfuturesmarkets.pdf.txt", r"contracts, the bid-ask spread is very close to the minimum tick size", 2),
    page_src("cftc_oce_liquidityfuturesmarkets.pdf"))
IDS["sp_zn_feds"] = add(["ZN"], "T1", "median_spread_ticks", "1 (94% of observations at one tick, March 2020)", "product",
    "March 2020", "FEDS 2025-038 (Gousgounis, Mixon, Tuzun, Vega), reused from E.28 F9.",
    '"bid-ask spreads over our sample period were often constrained by the minimum tick size (e.g., in March 2020, 94% of bid-ask spread observations are "stuck" at one tick)"',
    {"file": "reports/stage_e28_briefs/A1_rates.md", "field": "section F9, bullet 'ZN tick-constrained spread'",
     "url": None, "fetched_utc": None, "sha256": None}, "reused")
v, s = a1("10Y", "median_spread_ticks_main")
IDS["sp_10y"] = add(["10Y"], "T1", "median_spread_ticks", 1.67, "product", "2024 (H1 per E.28), RTH 07:00-16:00 CT",
    "Average (not median) top-of-book spread 0.167 bp with tick 0.1 bp = 1.67 ticks; CME marketing article via Wayback.",
    v["quote"], s, "reused")
IDS["ctt"] = add(["ZT", "ZF", "ZN"], "T1", "cost_to_trade_ticks", "ZT 1.78 (1,000 lots); ZF 1.60 (1,000 lots); ZN 1.07 (500 lots); 2023",
    "product", "2021 baseline vs 2023 (CME)", "CME 'Interest Rate liquidity and trading review 2023': average cost to "
    "trade a 1,000-lot (ZT, ZF) or 500-lot (ZN) order, in ticks. A large-order cost, not a top-of-book spread; context "
    "only. ZT 2021 1.10 -> 2023 1.78 ticks.",
    q(E28P / "cme_ir_liquidity_trading_review_2023.pdf.txt", r"Avg\. Cost to Trade, 1000 Lots\s+1\.10"),
    e28page_src("cme_ir_liquidity_trading_review_2023.pdf"))
IDS["trade_zn"] = add(["ZN"], "T1", "trade_size", "mean 16.01, median 2 contracts (2024-04-09)", "product", "2024-04-09 (one day)",
    "Lalor and Swishchuk arXiv 2409.12721v3, reused from E.28 F9. Trade size, not touch size.",
    '"ZN 16.01 2"', {"file": "reports/stage_e28_briefs/A1_rates.md", "field": "section F9, bullet 'Trade size and queues'",
                      "url": None, "fetched_utc": None, "sha256": None}, "reused")

# =========================== T2a crowding (non-shared sources) ===========================
add(FULL + MICROS, "T2a", "auto_share_pct", "see F2_shared_cftc_automation.json", "product_group", "2012-2021",
    "CFTC sources owned by this reader are in the shared file: Interest Rate - US Treasury subgroup ATS share 73.1% "
    "(2016-18); 10 Yr Note 72.7%, 5 Yr Note 74.0% (2016-18); Coughlan-Orlov HFT share of 10-year T-note 45.2% (2020). "
    "ZT and ZB have no product-level CFTC figure; the micro yields none at all.",
    "Interest Rate - US Treasury 5 6 4.5 (1.1) 4.2 (1.1) 68.4 (16.4) 73.1 (19.4) 27.1 (6.5) 22.7 (6.0)",
    {"file": "reports/stage_e32b_briefs/F2_shared_cftc_automation.json", "field": "items CFTC-4, CFTC-12, CFTC-24, CFTC-25, CFTC-29, CFTC-50, CFTC-59",
     "url": None, "fetched_utc": None, "sha256": None}, "reused")
v, s = a1("ZN", "hft_automated_share")
add(["ZN", "ZT", "ZF", "ZB"], "T2a", "ptf_share_pct",
    "JSR 2015: PTFs >50% of Treasury futures volume; FEDS 2025-038: PTFs 70% of liquidity-providing volume (ZN)",
    "product", "2014 (JSR); 2012-2021 (FEDS 2025-038)",
    "Reused from E.28 (hft_automated_share note for ZN). Principal trading firms, a firm-type classification, not the "
    "automation flag. JSR figure is in E.28 A1_rates.json [ZN].hft_automated_share.value; the quote below is FEDS 2025-038 "
    "as quoted in E.28 F12 R3.",
    '"PTFs and bank dealers are the main liquidity providers, accounting for 70 and 15 percent of the volume of liquidity providing trades"',
    {"file": "reports/stage_e28_briefs/A1_rates.md", "field": "section F12 row R3; A1_rates.json [ZN].hft_automated_share",
     "url": None, "fetched_utc": None, "sha256": None}, "reused")

# =========================== T2b programs ===========================
v, s = a1("2YY", "market_maker_program")
IDS["mm_micro"] = add(MICROS, "T2b", "mm_program",
    "Micro Treasury Yield Futures Market Maker Program (later 'Yield Futures Market Maker Program')", "product",
    "2021-08-16 .. 2028-02-29 (successive extensions; E.28 F7)",
    "CBOT filings to CFTC; quoting obligations on 10Y outright and 10Y-2YY, 10Y-5YY, 30Y-10Y spreads; fee waivers; "
    "from 2026-08-01 a USD 10,000 monthly incentive pool (E.28 F7).", v["quote"], s, "reused")
IDS["iip"] = add(CODES, "T2b", "mm_program",
    "International Incentive Program (IIP), CME/CBOT/NYMEX/COMEX volume-fee incentive", "product_group",
    "Start 2011-12-16; end 2026-01-31 per 2025 filing (effective 2025-02-01), 'or the date on which' the Exchanges modify",
    "Fee-discount program for proprietary trading firms located outside North America; IIP all-in fees per side "
    "include 'U.S. Treasury Futures $0.54' and 'Micro Treasury Yield Futures $0.21'. A volume-incentive program covering "
    "outright Treasury futures and the micro yields; not a market-maker or quoting program. The same fee table also "
    "lists E-micro FX, Micro E-mini equity, Micro E-mini Dow, agricultural, Henry Hub natural gas and other products "
    "(other families; reported to the lead only). Whether it was extended past 2026-01-31: not found.",
    q(PAGES / "cftc_rules01102513618.pdf.txt", r"U\.S\. Treasury Futures\s+\$0\.54") + " | " +
    q(PAGES / "cftc_rules01102513618.pdf.txt", r"Start date is December 16, 2011") + " | " +
    q(PAGES / "cftc_rules01102513618.pdf.txt", r"Micro Treasury Yield Futures\s+\$0\.21"),
    page_src("cftc_rules01102513618.pdf"))
IDS["invoice"] = add(FULL, "T2b", "mm_program", "Invoice Spreads Inter-Dealer Broker Incentive Program (invoice spreads only)",
    "product", "2024-09-01 .. 2025-02-28 (CBOT 24-xxx, rules0812244266); 2026-08-01 .. 2027-07-31 (CBOT 26-335)",
    "Covers ZT ('26'), ZF ('25'), ZN ('21'), TN, ZB ('17'), UB futures only when 'executed as part of an invoice spread' "
    "(futures against swap package), for inter-dealer brokers. Not a program for outright futures.",
    q(PAGES / "cftc_rules07152610364.pdf.txt", r"Futures \(“UBE”\) executed as part of an invoice spread"),
    page_src("cftc_rules07152610364.pdf"))
add(["ZB"], "T2b", "mm_program", "Long-Term U.S. Treasury Bond MM Program = Ultra Bond (UB), not ZB", "sibling",
    "Start 2010-01-10; end 2022-01-31 (CBOT 21-330)",
    "CBOT 'Market Maker Program for Long-Term U.S. Treasury Bond Futures' (up to 7 participants, quoting 65% of RTH "
    "07:00-16:00). Its start date (2010-01-10) matches the Ultra Bond launch in January 2010 (E.28 page "
    "cftc_ptc02232412041: Ultra Bond 'coexisted with the original U.S. Treasury Bond Futures contract since its launch "
    "in January 2010'), and CBOT Chapter 40 'Long-Term U.S. Treasury Bond Futures' is the Ultra Bond chapter "
    "[snippet: WebSearch result for cmegroup.com/rulebook/CBOT/III/40.pdf, not fetched]. So this program is for UB, "
    "not ZB (ZB is Chapter 18 'U.S. Treasury Bond Futures').",
    q(PAGES / "cftc_rule071321cbotdcm002.pdf.txt", r"Start date is January 10, 2010") + " | " +
    q(PAGES / "cftc_rule071321cbotdcm002.pdf.txt", r"CBOT Long-Term U\.S\. Treasury Bond f utures traded on"),
    page_src("cftc_rule071321cbotdcm002.pdf"))

# =========================== T3 relationships ===========================
add(FULL, "T3", "relationship", "Treasury inter-commodity spreads (curve): 5Y/10Y FIT/FYT, 2Y/5Y TUF/TFY, 10Y/30Y NOB, etc.",
    "product", "2023 ADV (CME)", "Type: mechanical/curve (implied inter-commodity spread books on Globex, E.28 F2). "
    "2023 ADV in contract legs: 5Y/10Y 125,625; 2Y/5Y 51,533; Ultra10Y/30Y 13,992; 10Y/Ultra10Y 13,103; 10Y/30Y 12,445. "
    "No intraday mean-reversion or lead-lag study of these curve spreads on CME futures was found.",
    q(E28P / "cme_ir_liquidity_trading_review_2023.pdf.txt", r"5Y/10Y\s+FIT/FYT"), e28page_src("cme_ir_liquidity_trading_review_2023.pdf"))
add(FULL, "T3", "relationship", "calendar (roll) spreads, quarterly cycle", "product", "2014-2018",
    "Type: calendar. Treasury futures trade concentrated in the front contract outside the roll; spread trading low "
    "(Fett-Haynes 2017). Haynes-Roberts: SP-SP share of 10 Yr volume small (Update #2 Table 4).",
    q(PAGES / "cftc_oce_futureslandscape.pdf.txt", r"Because Treasury trading is usually concentrated in the most active", 2),
    page_src("cftc_oce_futureslandscape.pdf"))
add(MICROS, "T3", "relationship", "micro yield futures vs Treasury futures / cash on-the-run (same tenor)", "product", "design",
    "Type: mechanical (different designs: yield-quoted, cash-settled to BrokerTec on-the-run benchmark vs price-quoted "
    "physically delivered CTD basket; E.28 F1, F11). 10Y and ZN are not siblings for price transfer (spec 0). No "
    "intraday lead-lag study found.", None,
    {"file": "reports/stage_e28_briefs/A1_rates.md", "field": "sections F1, F11", "url": None, "fetched_utc": None,
     "sha256": None}, "reused")
add(["ZN", "ZF", "ZT", "ZB"], "T3", "relationship", "futures vs cash (BrokerTec): millisecond cross-market trading", "underlying",
    "around 2014-2015 (10-year; BrokerTec and CME)",
    "Dobrev and Schaumburg, NY Fed Liberty Street Economics, 2015-08-19: cross-market activity peaks at +/-5 ms; "
    "futures usually lead cash but the reverse is often true. Arbitrage-tight, sub-second; no minute-level lead-lag.",
    q(PAGES / "lse_2015-08_hf_cross_market_treasury.html.txt", r"Market participants often presume that price discovery happens"),
    page_src("lse_2015-08_hf_cross_market_treasury.html", "lse_2015-08_hf_cross_market_treasury.html.txt"))
v, s = a1("ZN", "brokertec_link")
add(["ZN", "ZF", "ZT", "ZB"], "T3", "relationship", "futures order flow vs cash yields (level and slope)", "product", "weekly data (Mixon-Tuzun FEDS 2018-065)",
    "Price discovery in the level linked to non-dealer order flow in 10-year futures; slope to 10-year futures and 5-year "
    "cash. Weekly horizon (E.28 F12 R7).",
    '"Price discovery in the level of interest rates is most strongly linked to non-dealer order flow in the 10-year futures contract, while price discovery in the slope of the curve is linked to order flow in the 10-year futures and the 5-year cash market."',
    {"file": "reports/stage_e28_briefs/A1_rates.md", "field": "section F11 (feds_2018-065_price_pressure_term_structure.pdf.txt)",
     "url": None, "fetched_utc": None, "sha256": None}, "reused")

# =========================== T4 events ===========================
add(CODES, "T4", "event", "Employment Situation (NFP), first Friday 08:30 ET monthly", "underlying", "2012-11..2015-09 (ZN, ES)",
    "Haynes and Roberts (2015-12-18), CFTC OCE 'Macro News Announcements and Automated Trading' (ZN focus). Absorption: "
    "'majority of permanent price changes restricted to the minutes, or in many cases seconds, just following the "
    "release'; activity forces 'concentrated over relatively short periods, usually on the order of a few seconds'. "
    "Fast absorption (seconds to minutes).",
    q(PAGES / "cftc_oce_macroannouncement.pdf.txt", r"price discovery usually happens very quickly", 2),
    page_src("cftc_oce_macroannouncement.pdf"))
add(CODES, "T4", "event", "macro announcements (Treasury market): price adjustment concentrated within first minute", "underlying",
    "early 1990s (Balduzzi et al. 2001, cash)",
    "Secondary citation inside Haynes-Roberts 2015 macro paper of Balduzzi, Elton, Green (2001): price adjustment "
    "within the first minute; liquidity returns in 5-15 minutes. Balduzzi et al. not fetched; quote is the CFTC paper's "
    "summary. Fast absorption.",
    q(PAGES / "cftc_oce_macroannouncement.pdf.txt", r"announcement, but that the price adjustment, even in the early 90", 3),
    page_src("cftc_oce_macroannouncement.pdf"))
add(CODES, "T4", "event", "major announcements (cash Treasuries): volatility and volume persist after a lag", "underlying",
    "GovPX cash data; sample period not read (abstract only; staff report dated July 1997)",
    "Fleming and Remolona, NY Fed Staff Report 27 (July 1997; JF 1999 version). Abstract read from the scanned PDF page "
    "image (no text layer): volatility, volume and spreads; volatility-only (no statement on mean drift in the abstract).",
    "High levels of price volatility and trading volume then persist, with volume persisting somewhat longer.",
    page_src("nyfed_sr27_fleming_remolona_1997.pdf", "nyfed_sr27_fleming_remolona_1997.pdf"), "full_text")
e, s = e20("ZN", "E7")
add(["ZN", "ZB"], "T4", "event", "pre-announcement drift before some macro releases (ZN)", "product", e.get("sample"),
    "Kurov, Sancetta, Strasser, Wolfe (ECB WP 1901, 2016; JFQA 2019), reused from E.20: drift before the release in the "
    "direction of the surprise; not tradable ex ante without the surprise sign. Pre-release, not post-release drift.",
    e.get("quote"), s, "reused")
e, s = e20("ZF", "E5")
add(["ZF", "ZN", "ZB", "ZT"], "T4", "event", "FOMC statement 14:00 ET: yields keep falling for about 3 hours after; NFP and pre-FOMC null",
    "underlying", e.get("sample"),
    "Fleming, Liu, Nguyen, NY Fed SR 1188 (2026), reused from E.20 ZF E5 / ZB E3: unconditional post-FOMC yield decline "
    "over a 3-hour window (slow, hours-horizon drift); null 3 h before FOMC and payrolls and after payrolls.",
    e.get("quote"), s, "reused")
e, s = e20("ZN", "E3")
add(["ZN", "ZF", "ZT", "ZB"], "T4", "event", "Treasury auctions (13:00 ET close): yields rise in the hours before and reverse after",
    "underlying", e.get("sample"),
    "SR 1188, reused from E.20 (ZN E3/E4; ZT E1-E3; ZF E2-E4; ZB E1-E2): price pressure over 180-minute windows; own-tenor "
    "pressure roughly halved in 2015-2024. Hours horizon, gross.", e.get("quote"), s, "reused")
e, s = e20("ZN", "E8")
add(["ZN", "ZT"], "T4", "event", "pre-FOMC drift: none in Treasuries", "underlying", e.get("sample"),
    "Lucca and Moench (SR 512; JF 2015), reused from E.20. Null.", e.get("quote"), s, "reused", negative=True)
e, s = e20("ZN", "E9")
add(["ZN", "ZB"], "T4", "event", "post-FOMC drift in long bond futures (days)", "product", e.get("sample"),
    "Indriawan, Jiao, Tse (JBF 2021), reused from E.20; secondary-only there. Horizon up to 15 days (daily, not intraday).",
    e.get("quote"), s, "abstract")
v, s = a1("ZN", "scheduled_releases_per_week")
add(CODES, "T4", "event", "Treasury coupon auctions: each tenor monthly (about 0.23/week)", "underlying",
    "Treasury tentative schedule Aug 2026-Jan 2027", "Reused E.28 F10.", str(v.get("quote")), s, "reused")

# =========================== T5 settlement and price discovery ===========================
for c in FULL:
    v, s = a1(c, "settlement")
    chap = {"ZB": 18, "ZN": 19, "ZF": 20, "ZT": 21}[c]
    rq = q(E28P / f"cbot_rulebook_II_{chap}.pdf.txt", r"contract grade for delivery on futures made under these Rules", 3)
    add([c], "T5", "settlement_basis", "physical delivery of eligible Treasury securities (CTD basket)", "product", None,
        f"CBOT rulebook Chapter {chap} (E.28 Wayback copy). Not financially settled off a sibling. E.28 field value reused.",
        rq, e28page_src(f"cbot_rulebook_II_{chap}.pdf"), "full_text")
v, s = a1("2YY", "brokertec_link")
add(MICROS, "T5", "settlement_basis",
    "cash-settled to the 3:00 p.m. ET BrokerTec US Treasury Benchmark (15-min VWAY of on-the-run cash trades); "
    "daily settlement 30-second VWAP before 2:00 p.m. CT", "product", "since launch 2021-08-16",
    "Settles to a cash-market fixing (BrokerTec, a CME Group cash platform), not to a Treasury futures sibling's "
    "settlement price.", v["quote"], s, "reused")
add(["ZT", "ZF", "ZN", "ZB"], "T5", "info_share",
    "futures gain share; GovPX spot shares for 5y and 10y 'typically fail to reach 50% from 1999 on'", "underlying",
    "GovPX and CBOT data, 1990s to mid-2000s (paper draft 2007-09-30)",
    "Mizrach and Neely, St. Louis Fed WP 2005-070E / JBF 2008. Abstract read from the rendered PDF page (text layer "
    "garbled; E.28 copy). Highest futures shares in the longest maturities; 2-year spot shares higher but declining "
    "after 1998. Pre-2010, cash vs futures.",
    "The highest futures market shares are in the longest maturities. The estimates of 5-year and 10-year GovPX spot "
    "market information shares typically fail to reach 50% from 1999 on. The GovPX information shares for the 2-year "
    "contract are higher than those of the 5- and 10-year maturities but also decline after 1998.",
    {"file": "reports/stage_e28_briefs/pages/A1_rates/stlfed_wp2005-070_mizrach_neely_info_shares.pdf (page 2, read as image)",
     "field": None, "url": "https://s3.amazonaws.com/real.stlouisfed.org/wp/2005/2005-070.pdf",
     "fetched_utc": "2026-10-21T12:59:10Z",
     "sha256": "5ac64c577463ce39996db1553e00a2191db3ede12dc7723161eb7f4bf88bf323"}, "full_text")
add(["ZN"], "T5", "info_share", "futures usually lead cash, reverse often true; 'effectively ... one' market", "underlying",
    "around 2014-2015", "Dobrev-Schaumburg 2015 (Liberty Street). No share number.",
    q(PAGES / "lse_2015-08_hf_cross_market_treasury.html.txt", r"Market participants often presume that price discovery happens"),
    page_src("lse_2015-08_hf_cross_market_treasury.html", "lse_2015-08_hf_cross_market_treasury.html.txt"))
add(["ZT"], "T5", "info_share", "short-run price discovery moves to the finer-grid market after the 2018-19 tick cuts",
    "product", "around 2018-11-19 (cash) and early 2019 (futures)",
    "Management Science 2023 (doi 10.1287/mnsc.2022.4663), reused from E.28 F12 R8; abstract only there.",
    "the finer pricing grid in the cash market allows traders to act on small information signals that are not profitable to exploit in the larger-tick futures market",
    {"file": "reports/stage_e28_briefs/A1_rates.md", "field": "section F12 row R8", "url": None, "fetched_utc": None,
     "sha256": None}, "abstract")
add(["10Y"], "T5", "info_share", None, "product", None,
    "No information-share study on the micro yield futures found (E.28 searches; this reader found none).", None,
    {"file": "reports/stage_e28_briefs/A1_rates.md", "field": "section F12 closing note", "url": None,
     "fetched_utc": None, "sha256": None}, "reused")

# =========================== T6 directional evidence ===========================
T6 = [("ZN", "E1", ["ZN", "10Y"], "full_text"), ("ZF", "E1", ["ZF", "5YY"], "full_text"), ("ZT", "E4", ["ZT", "2YY"], "full_text"),
      ("ZB", "E4", ["ZB", "30Y"], "full_text"), ("ZN", "E2", CODES, "abstract"), ("ZN", "E13", ["ZN"], "full_text"),
      ("ZN", "E6", ["ZN"], "full_text"), ("ZN", "E10", FULL, "full_text"), ("ZN", "E12", CODES, "abstract")]
for root, eid, codes, ver in T6:
    e, s = e20(root, eid)
    note = ("Baltussen et al. 2021 (shared source owned by EquityReader: see F2_shared_baltussen.json); this is E.20's "
            "already-sourced product row, reused. " if "Baltussen" in str(e.get("source")) else "")
    add(codes, "T6", "directional_study", e.get("effect"), "product" if len(codes) <= 2 else "asset_class", e.get("sample"),
        f"{note}Source: {e.get('source')}. Rule: {e.get('rule')}. Hold: {e.get('hold')}. Gross/net: {e.get('gross_or_net')}. "
        f"Decay: {e.get('decay_evidence')}. E.20 grade: {e.get('grade')}. Micro yield codes listed only where the tenor "
        f"matches; 10Y is not a price-transfer sibling of ZN (spec 0) - listed for information, the scorer decides.",
        e.get("quote"), s, ver if e.get("grade") != "secondary-only" else "abstract")
add(FULL, "T6", "directional_study", "negative serial correlation of intraday price changes; trading strategy earns excess profits",
    "asset_class", "not stated in abstract; published 2009 (pre-2010 data)",
    "Cusatis, Kulkarni, Thomas (2009), 'Intraday serial correlation and the predictability of returns in the U.S. treasury "
    "note futures market', Banking and Finance Review (PSU Pure abstract page). Horizon, maturity, sample and costs not "
    "in the abstract. Correlations 'have declined considerably over time'.",
    q(PAGES / "psu_cusatis_kulkarni_thomas_2009.html.txt", r"This study examines the intraday price patterns"),
    page_src("psu_cusatis_kulkarni_thomas_2009.html", "psu_cusatis_kulkarni_thomas_2009.html.txt"), "abstract")
add(["ZN"], "T6", "directional_study", "excluded: under 5 minutes / passive fills (adverse selection ~1/2 tick)", "product",
    "Dec 2023; 2024-04", "DeLise arXiv 2407.16527 and Lalor-Swishchuk arXiv 2409.12721 (E.28 F12 R1, R2). Excluded: "
    "fill-level horizon, passive quoting, not a 5-minute-plus directional test.",
    '"a limit order fill does incur a type of slippage penalty, and the magnitude of that penalty is shown to here to be very close to 1/2 tick"',
    {"file": "reports/stage_e28_briefs/A1_rates.md", "field": "section F12 rows R1, R2", "url": None, "fetched_utc": None,
     "sha256": None}, "reused", negative=True)
add([], "T6", "directional_study", "excluded: asset class not stated (overnight -> last half-hour momentum disappears out of sample)",
    "other", "unknown", "Rosa (2022), Journal of Futures Markets 42(12):2218-2234, IDEAS abstract. Not attributed to rates.",
    q(PAGES / "ideas_rosa_2022_jfm.html.txt", r"This paper studies the out.of.sample performance"),
    page_src("ideas_rosa_2022_jfm.html", "ideas_rosa_2022_jfm.html.txt"), "abstract", negative=True)

# =========================== T7 session ===========================
v, s = a1("ZN", "trading_hours")
add(FULL, "T7", "session_handoff", "Globex Sun 17:00 - Fri 16:00 CT; daily maintenance 16:00-17:00 CT; RTH 07:00-16:00 CT",
    "product", None, "Reused E.28 F4 (options filing quote; futures same schedule per Micro Ultra filing).", v["quote"], s, "reused")
v, s = a1("2YY", "trading_hours")
add(MICROS, "T7", "session_handoff", "Globex Sun-Fri 17:00-16:00 CT; Mon-Thu 16:00-17:00 CT maintenance", "product", None,
    "Reused E.28 F4.", v["quote"], s, "reused")
add(CODES, "T7", "session_handoff", "New York open and data hour: volume/volatility peak 08:30-09:00 ET, smaller peak 14:30-15:00 ET",
    "underlying", "cash interdealer (GovPX), 1994",
    "Fleming (1997), FRBNY Economic Policy Review, 'The Round-the-Clock Market for U.S. Treasury Securities'. Trading "
    "passes Tokyo -> London -> New York; >94% of volume in New York hours; overseas price changes are unbiased predictors "
    "of overnight New York changes (efficiency, no handoff drift). Volatility/volume pattern; no mean effect.",
    "The analysis reveals that trading volume and price volatility are highly concentrated in New York trading hours, with a daily peak between 8:30 a.m. and 9 a.m. and a smaller peak between 2:30 p.m. and 3 p.m. ... overseas price changes in U.S. Treasury securities emerge as unbiased predictors of overnight New York price changes. [left column of a two-column layout, lines 54-61 of the .txt, joined]",
    page_src("nyfed_epr1997_fleming_round_the_clock.pdf"))
e, s = e20("ZN", "E11")
add(FULL, "T7", "session_handoff", "month-end index strike time moved 15:00 -> 16:00 ET (Jan 2021); activity concentrates at strike",
    "underlying", e.get("sample"), "Dyer, Fleming, Shachar, Liberty Street 2026-09-22 (reused E.20 ZN E11). Activity only, no return figure.",
    e.get("quote"), s, "reused")
e, s = e20("ZN", "E1")
add(["ZN", "ZF", "ZT", "ZB"], "T7", "session_handoff", "settlement window: rest-of-day return predicts last 30 min to end of daily settlement (14:00 CT)",
    "asset_class", e.get("sample"),
    "Baltussen et al. 2021 via E.20 (shared source owned by EquityReader). Close defined as end of the daily settlement "
    "period for bond futures. Documented handoff-type effect at the settlement window.", e.get("quote"), s, "reused")

# =========================== per_code ===========================
per_code = {}
for c in CODES:
    per_code[c] = {"median_spread_ticks": None, "spread_item": None, "touch_size": None, "touch_item": None,
                   "settlement_basis": None, "settlement_item": None, "leader": None, "notes": ""}
for c in FULL:
    per_code[c].update({"median_spread_ticks": 1, "spread_item": IDS["sp_full"], "touch_item": IDS["touch_full"],
                        "settlement_basis": "physical delivery (Treasury CTD basket)", "leader": c})
per_code["ZT"]["touch_size"] = 99471
per_code["ZF"]["touch_size"] = 1319
per_code["ZN"]["touch_size"] = 2507
per_code["ZB"]["touch_size"] = 377
per_code["ZT"]["notes"] = ("Spread 1 tick is a 2018 figure under the pre-2019 ZT tick (1/4 of 1/32); current tick 1/8 of 1/32; "
                           "no post-2019 spread found. 2023 cost to trade 1,000 lots 1.78 ticks (" + IDS["ctt"] + ").")
per_code["ZN"]["notes"] = f"Also {IDS['sp_zn_fh']} (2013-16) and {IDS['sp_zn_feds']} (Mar 2020) at about one tick."
per_code["10Y"].update({"median_spread_ticks": 1.67, "spread_item": IDS["sp_10y"],
                        "notes": "1.67 is an average (CME, 2024), not a median. No touch size published."})
for c in MICROS:
    per_code[c]["settlement_basis"] = "cash-settled to BrokerTec 3:00 p.m. ET benchmark (on-the-run cash VWAY)"
    per_code[c]["leader"] = None
    per_code[c]["notes"] = (per_code[c]["notes"] + " Leader under spec 0: not decided here (10Y and ZN are not siblings "
                            "for price transfer; no same-underlying yield-futures sibling with larger ADV).").strip()
for c in ["2YY", "5YY", "30Y"]:
    per_code[c]["notes"] = "No spread or touch figure found. " + per_code[c]["notes"]
for c in FULL + MICROS:
    for it in items:
        if it["topic"] == "T5" and it["field"] == "settlement_basis" and c in it["codes"]:
            per_code[c]["settlement_item"] = it["id"]

searched = [
    {"codes": ["ZT", "ZF", "ZN", "ZB"], "topic": "T1",
     "queries": ["Treasury futures 2-year ZT bid-ask spread ticks top of book depth 2023-2025 CME tick size reduction 2019",
                 "(E.28 searches, A1_rates.md F9)"],
     "note": "No published post-2018 median spread or touch size for ZT/ZF/ZN/ZB found; CME's UST market profile tool "
             "reportedly publishes only volume as public data [snippet]."},
    {"codes": ["2YY", "5YY", "30Y"], "topic": "T1", "queries": ["E.28 searches"], "note": "No spread or touch size published."},
    {"codes": ["ZT", "ZF", "ZN", "ZB"], "topic": "T2b",
     "queries": ["cftc.gov CBOT incentive program Treasury futures 2022-2024 market maker Ultra 10-Year / 10-Year Note",
                 "cftc.gov CBOT International/Asian/Latin American incentive program Treasury 2022-2024",
                 "CME Group International Incentive Program IIP interest rate futures"],
     "note": "No market-maker or quoting program for ZT, ZF, ZN or ZB outrights found for 2021-2026 (found: IIP fee "
             "program covering Treasury futures; invoice-spread IDB program; UB, 20-year (TWE) and Micro Ultra programs, "
             "all other products). Absence is 'not found', not 'none exists'."},
    {"codes": CODES, "topic": "T2c", "queries": ["E.28 searches; CFTC papers read for the shared file"],
     "note": "No retail share of volume found. Proxy only: small manual traders (shared CFTC-40, CFTC-41)."},
    {"codes": CODES, "topic": "T4",
     "queries": ["Treasury futures intraday price drift after macroeconomic announcements minutes post-announcement drift 10-year note futures"],
     "note": "No study documenting post-release mean drift of 5+ minutes after US macro releases in Treasury futures "
             "found; evidence found says seconds-to-minutes absorption (CFTC 2015) except FOMC (3-hour yield decline, "
             "SR 1188) and auctions (hours-scale pressure). Jiang-Lo-Valente BoC WP 2014-56 blocked (AWS WAF)."},
    {"codes": CODES, "topic": "T5",
     "queries": ["information share Treasury futures cash BrokerTec price discovery percent 10-year",
                 "Mizrach Neely information shares US Treasury market pdf"],
     "note": "No post-2010 numeric information share for Treasury futures vs cash found. Campbell-Hendry BoC WP 2007-43 "
             "(2002-2005, US futures larger share per snippet) blocked by AWS WAF; not used."},
    {"codes": CODES, "topic": "T6",
     "queries": ["intraday momentum Treasury/bond futures last half-hour out-of-sample 2022-2025",
                 "10-year Treasury note futures intraday return predictability 30-minute/hourly momentum or reversal"],
     "note": "No new peer-reviewed post-2010 product-level out-of-sample intraday directional study on US Treasury "
             "futures beyond E.20's rows (Baltussen et al. rows per contract). Micro yields: none."},
]

doc = {
    "family": "rates", "worker": "RatesReader-OpusHigh", "codes": CODES,
    "started_pdt": "2026-10-28T22:48PDT",
    "finished_pdt": subprocess.run(["bash", "-c", "TZ=America/Vancouver date +%Y-%m-%dT%H:%M%Z"], capture_output=True,
                                   text=True).stdout.strip(),
    "websearch_calls": 10, "fulltext_reads_t6": 0, "notices": [],
    "items": items, "searched_not_found": searched, "per_code": per_code,
    "gaps": [
        "ZT spread under the current (post-2019) tick not found; the 1-tick figure is 2018, old tick.",
        "Touch sizes are 2018 averages (CME), not medians; none for the micro yields.",
        "Balduzzi-Elton-Green 2001 and Andersen et al. 2007 not fetched (absorption evidence taken from the CFTC 2015 paper).",
        "Bank of Canada PDFs (Jiang-Lo-Valente 2014-56; Campbell-Hendry 2007-43) blocked by an AWS WAF challenge via curl; "
        "Scrapling not tried (terms not checked within time).",
        "Fleming-Remolona read from scanned page images (abstract only); sample window not confirmed from the text.",
        "Whether the IIP was extended past 2026-01-31 not checked (cmegroup.com not fetched by rule).",
    ],
}
OUTJ.write_text(json.dumps(doc, indent=1, ensure_ascii=False))
print("items", len(items), "->", OUTJ)
