"""RATES_build_shared.py: builds F2_shared_cftc_automation.json (Stage E.32b, family shared_cftc).

Quotes are pulled from the saved pdftotext files by pattern so they stay verbatim (whitespace collapsed).
Run: python3 -I RATES_build_shared.py
"""
import csv
import json
import re
import subprocess
from pathlib import Path

ROOT = Path("/home/kiros-li/Documents/GitHub/PropExperiment")
PAGES = ROOT / "reports/stage_e32b_briefs/pages/RATES"
E28 = ROOT / "reports/stage_e28_briefs/pages/A1_rates"
OUT = ROOT / "reports/stage_e32b_briefs/F2_shared_cftc_automation.json"


def pdt_now():
    return subprocess.run(["bash", "-c", "TZ=America/Vancouver date +%Y-%m-%dT%H:%M%Z"],
                          capture_output=True, text=True).stdout.strip()


def load_log(path):
    rows = {}
    with open(path) as fh:
        for r in csv.reader(fh, delimiter="\t"):
            if len(r) >= 6 and r[0] != "url":
                rows[r[5]] = {"url": r[0], "fetched_utc": r[1], "sha256": r[4]}
    return rows


LOG = load_log(PAGES / "log.tsv")
LOG28 = load_log(E28 / "log.tsv")


def src(fname, e28=False):
    log = LOG28 if e28 else LOG
    base = E28 if e28 else PAGES
    meta = log[fname]
    return {"file": str((base / (fname + ".txt")).relative_to(ROOT)) if fname.endswith(".pdf")
            else str((base / fname).relative_to(ROOT)),
            "field": None, "url": meta["url"], "fetched_utc": meta["fetched_utc"], "sha256": meta["sha256"]}


def q(fname, pattern, e28=False, n=1):
    base = E28 if e28 else PAGES
    txt = (base / (fname + ".txt")).read_text(errors="replace").splitlines()
    rx = re.compile(pattern)
    for i, line in enumerate(txt):
        if rx.search(line):
            chunk = " ".join(txt[i:i + n])
            return re.sub(r"\s+", " ", chunk).strip()
    raise SystemExit(f"pattern not found: {pattern} in {fname}")


HR15 = "cftc_oce_automatedtrading_2015.pdf"
HR17 = "cftc_oce_automatedtrading_update_2017.pdf"
HR19 = "cftc_ats_update2_2018.pdf"
CO22 = "cftc_hft_market_quality_2022.pdf"
FH17 = "cftc_oce_futureslandscape.pdf"
SL15 = "cftc_oce_speedlatency.pdf"
DMO19 = "cftc_dmo_mib_automated_orders_2019.pdf"
BTC21 = "cftc_who_trades_btc_2021.pdf"

ATS_DEF = ("ATS = order flagged automated under CME FIX Tag 1028 ('generated and/or routed without human "
           "intervention'); broader than HFT: includes manual traders using automated spreaders or third-party "
           "order management (Haynes-Roberts 2015 p.3). Share = percent of traded volume (contracts).")

items = []


def add(codes, topic, field, value, scope, window, detail, quote, source, verified="full_text",
        negative=False):
    items.append({"id": f"CFTC-{len(items) + 1}", "codes": codes, "topic": topic, "field": field,
                  "value": value, "scope": scope, "window": window, "detail": detail, "quote": quote,
                  "source": source, "verified": verified, "pointer": False, "negative": negative})


W19 = "2016-11-01..2018-10-31 (red); prior 2014-11-01..2016-10-31 (black)"
W17 = "2014-11-01..2016-10-31 (red); prior 2012-11-12..2014-10-31 (black)"

# ---------- product groups, Update #2 (2019), Table 1 and Table 2 ----------
GROUPS_T1 = [
    (["MCL", "QM", "CL", "MNG", "QG", "NG"], r"^\s*Energy\s+275\s+236", "Energy", 66.5, 57.5),
    (["MGC", "GC", "SIL", "SI", "MHG", "HG"], r"^\s*Metals\s+17\s+17", "Metals", 67.6, 54.1),
    (["MZC", "MZS", "MZW", "MZL", "MZM", "XC", "XK", "XW", "ZC", "ZS", "ZW", "ZL", "ZM"],
     r"^\s*Agriculture\s+32\s+31", "Agriculture", 55.5, 48.5),
    (["2YY", "5YY", "10Y", "30Y", "ZT", "ZF", "ZN", "ZB"], r"^\s*Interest Rate\s+12\s+13", "Interest Rate", 71.2, 66.8),
    (["M2K", "RTY", "MYM", "YM", "MNQ", "NQ"], r"^\s*Equities\s+25\s+23", "Equities", 73.7, 71.6),
    (["M6E", "6E", "M6A", "6A"], r"^\s*FX\s+48\s+49", "FX", 84.4, 82.7),
]
for codes, pat, name, v_new, v_old in GROUPS_T1:
    add(codes, "T2a", "auto_share_pct", v_new, "product_group", W19,
        f"CME product group '{name}', ATS share of group volume {v_new}% in 2016-18 ({v_old}% in 2014-16). "
        f"Columns: products (2 periods), Non-Electronic %, ATS %, Manual % (each with share of full market in "
        f"parentheses). {ATS_DEF}",
        q(HR19, pat), src(HR19))

GROUPS_T2 = [
    (["MCL", "QM", "CL"], r"Energy - Crude Oil\s+21\s+22", "Energy - Crude Oil", 70.4, 63.0),
    (["MNG", "QG", "NG"], r"Energy - Natural Gas\s+40\s+36", "Energy - Natural Gas", 65.7, 56.8),
    (["MGC", "GC", "SIL", "SI"], r"Metals - Precious\s+8\s+8", "Metals - Precious", 67.1, 53.5),
    (["MHG", "HG"], r"Metals - Base\s+4\s+4", "Metals - Base", 70.0, 56.9),
    (["MZC", "MZS", "MZW", "MZL", "MZM", "XC", "XK", "XW", "ZC", "ZS", "ZW", "ZL", "ZM"],
     r"Agriculture - Grain and Oilseed\s+13\s+12", "Agriculture - Grain and Oilseed", 55.2, 49.0),
    (["ZT", "ZF", "ZN", "ZB", "2YY", "5YY", "10Y", "30Y"], r"Interest Rate - US Treasury\s+5\s+6",
     "Interest Rate - US Treasury", 73.1, 68.4),
    (["M2K", "RTY", "MYM", "YM", "MNQ", "NQ"], r"Equities - US Index\s+12\s+10", "Equities - US Index", 73.7, 71.5),
    (["6E", "6A", "M6E", "M6A"], r"FX - G10\s+24\s+25", "FX - G10", 85.4, 83.7),
    (["M6E", "M6A"], r"FX - E Micros\s+8\s+7", "FX - E Micros", 70.9, 69.3),
]
for codes, pat, name, v_new, v_old in GROUPS_T2:
    extra = ""
    if "2YY" in codes:
        extra = (" The micro yield futures (2YY 5YY 10Y 30Y) listed only from 2021-08-16, after this window; "
                 "the subgroup figure describes the Treasury futures group they belong to, not those contracts.")
    if name == "FX - E Micros":
        extra = (" 'E Micros' is CME's E-micro FX subgroup in 2014-18 (contracts then listed under that name); "
                 "whether today's M6E/M6A are the same contracts is not established by this source.")
    add(codes, "T2a", "auto_share_pct", v_new, "product_group", W19,
        f"CME subgroup '{name}', ATS share {v_new}% of subgroup volume in 2016-18 ({v_old}% in 2014-16).{extra} "
        f"{ATS_DEF}",
        q(HR19, pat), src(HR19))

# ---------- named products, Update #2 (2019) Table 3 (ATS and MAN columns given directly) ----------
PRODUCTS = [
    (["MCL", "QM", "CL"], r"Energy - Crude Oil\s+Crude Oil\s+454", "Crude Oil", 69.4, 60.4),
    (["MNG", "QG", "NG"], r"Natural Gas \(Henry Hub\)\s+175\s+219", "Natural Gas (Henry Hub)", 69.9, 63.3),
    (["MGC", "GC"], r"Metals - Precious\s+Gold\s+162", "Gold", 67.6, 65.0),
    (["SIL", "SI"], r"Metals - Precious\s+Silver\s+31", "Silver", 67.1, 54.1),
    (["MHG", "HG"], r"Metals - Base\s+Copper\s+97", "Copper", 70.2, 53.2),
    (["MZC", "XC", "ZC"], r"Grain and Oilseed\s+Corn\s+168", "Corn", 52.5, 45.7),
    (["MZS", "XK", "ZS"], r"Grain and Oilseed\s+Soybean\s+115", "Soybean", 53.3, 47.9),
    (["MZW", "XW", "ZW"], r"Grain and Oilseed\s+Wheat\s+62", "Wheat", 62.2, 53.1),
    (["ZN"], r"US Treasury\s+10 Yr Note\s+661", "10 Yr Note", 72.7, 67.9),
    (["ZF"], r"US Treasury\s+5 Yr Note\s+378", "5 Yr Note", 74.0, 70.2),
    (["MNQ", "NQ"], r"E-mini NASDAQ 100\s+134\s+176", "E-mini NASDAQ 100", 74.0, 77.1),
    (["MYM", "YM"], r"E-mini Dow \(\$5\)\s+82", "E-mini Dow ($5)", 81.2, 80.2),
    (["M6E", "6E"], r"FX - G10\s+Euro\s+115", "Euro", 82.0, 80.3),
]
for codes, pat, name, v_new, v_old in PRODUCTS:
    sib = "" if len(codes) == 1 else (f" Figure is for the full-size product {codes[-1]}; it applies to "
                                      f"{', '.join(codes[:-1])} only as the leader's figure (siblings not tabulated).")
    add(codes, "T2a", "auto_share_pct", v_new, "product" if len(codes) == 1 else "leader", W19,
        f"Product '{name}': ATS share {v_new}% of product volume 2016-18 ({v_old}% 2014-16). Row columns: total "
        f"volume (mm, 2 periods), ATS %, MAN %, ATS-ATS %, ATS-MAN %, MAN-MAN % (each 2 periods).{sib} {ATS_DEF}",
        q(HR19, pat), src(HR19))

# ZT and ZB not in Table 3 (top three per group; only 10 Yr and 5 Yr listed)
add(["ZT", "ZB"], "T2a", "auto_share_pct", None, "product", W19,
    "ZT (2-Year Note) and ZB (Bond) are not tabulated by product in Haynes-Roberts 2015, 2017 or 2019: Table 3 "
    "lists only the top products by volume per group, and for Interest Rate - US Treasury only 10 Yr Note and "
    "5 Yr Note appear. Use the subgroup figure (Interest Rate - US Treasury).",
    q(HR19, r"top three products by volume in each product group"), src(HR19))

# older product rows (2012-14 and 2014-16), 2017 update Table 5: small+large ATS
OLDER = [
    (["ZN"], r"^\s*10 Yr Note\s+47,773", "10 Yr Note", "20.5+42.7=63.2 (2012-14); 21.3+46.5=67.8 (2014-16)"),
    (["ZF"], r"^\s*5 Yr Note\s+22,399", "5 Yr Note", "20.0+47.0=67.0 (2012-14); 22.3+47.9=70.2 (2014-16)"),
    (["MCL", "QM", "CL"], r"^\s*Crude Oil\s+65,410", "Crude Oil", "18.4+34.6=53.0 (2012-14); 18.3+42.1=60.4 (2014-16)"),
    (["MNG", "QG", "NG"], r"^\s*Natural Gas \(Henry Hub\)\s+35,181", "Natural Gas", "15.1+38.5=53.6; 17.8+45.6=63.4"),
    (["MGC", "GC"], r"^\s*Gold\s+52,675", "Gold", "19.0+26.9=45.9; 19.4+33.7=53.1"),
    (["SIL", "SI"], r"^\s*Silver\s+23,934", "Silver", "17.0+29.3=46.3; 18.1+35.9=54.0"),
    (["MZC", "XC", "ZC"], r"^\s*Corn\s+76,290", "Corn", "18.7+18.6=37.3; 20.8+24.9=45.7"),
    (["MZS", "XK", "ZS"], r"^\s*Soybean\s+59,739", "Soybean", "19.2+17.2=36.4; 22.1+25.8=47.9"),
    (["MNQ", "NQ"], r"^\s*E-mini NASDAQ 100\s+52,793", "E-mini NASDAQ 100", "17.4+58.2=75.6; 16.8+60.3=77.1"),
    (["M6E", "6E"], r"^\s*Euro\s+45,064", "Euro", "14.9+64.1=79.0; 15.7+64.6=80.3"),
]
for codes, pat, name, derived in OLDER:
    add(codes, "T2a", "auto_share_pct_older", derived, "product" if len(codes) == 1 else "leader", W17,
        f"Older figures for '{name}', 2017 update Table 5 (volume shares by trader group; small ATS + large ATS = "
        f"product ATS share, derived by the reader as the sum of two columns). Row columns: N small (2 periods), "
        f"small ATS %, small MAN %, N large, large ATS %, large MAN % (2 periods each). {ATS_DEF}",
        q(HR17, pat, e28=True), src(HR17, e28=True))

# small manual traders (retail proxy, not retail)
add(["ZN"], "T2c", "small_manual_share_pct", 19.8, "product", W19,
    "Not a retail share. Haynes-Roberts Update #2 Table 5: 'small volume trader' (account under 0.5% of daily "
    "volume) using manual entry = 19.8% of 10 Yr Note volume 2016-18 (23.7% 2014-16). Proxy only.",
    q(HR19, r"^\s*10 Yr Note\s+50,232"), src(HR19))
add(["ZF"], "T2c", "small_manual_share_pct", 14.8, "product", W19,
    "Not a retail share. Small manual traders 14.8% of 5 Yr Note volume 2016-18 (18.0% 2014-16). Proxy only.",
    q(HR19, r"^\s*5 Yr Note\s+24,741"), src(HR19))

# Large-trader non-directional share at 5 min (Table 8) for Treasuries
add(["ZN"], "T2a", "large_ats_nondirectional_5min_pct", 61.7, "product", W19,
    "Table 8: large automated traders' volume that is non-directional (netted) within 5 minutes = 61.7% of their "
    "volume 2016-18 (61.8% 2014-16); full day 88.4%. Columns: Full Day ATS MAN, 1 Min ATS MAN, 3 Min, 5 Min (2 periods "
    "each). Describes intermediation, not a volume share.",
    q(HR19, r"^\s*10 Yr Note\s+86\.5\s+88\.4"), src(HR19))
add(["ZF"], "T2a", "large_ats_nondirectional_5min_pct", 47.8, "product", W19,
    "Table 8: 5-minute non-directional share of large ATS volume 47.8% (2016-18), 49.7% (2014-16).",
    q(HR19, r"^\s*5 Yr Note\s+79\.8\s+80\.6"), src(HR19))

# ---------- Coughlan and Orlov 2022 (CFTC OCE), behavioral HFT share ----------
CO_ROWS = [
    (["MZC", "XC", "ZC"], r"Agriculture\s+Corn\s+8\.0%", "Corn", 23.9),
    (["MZS", "XK", "ZS"], r"Agriculture\s+Soybeans\s+13\.1%", "Soybeans", 36.0),
    (["MZW", "XW", "ZW"], r"Agriculture\s+Wheat\s+12\.5%", "Wheat", 26.6),
    (["M6E", "6E"], r"Currencies\s+Euro FX\s+57\.0%", "Euro FX", 46.2),
    (["MNG", "QG", "NG"], r"Energy\s+Natural gas\s+12\.9%", "Natural gas", 31.7),
    (["MCL", "QM", "CL"], r"Energy\s+WTI crude oil\s+29\.1%", "WTI crude oil", 53.9),
    (["ZN"], r"Financials\s+10-year T-note\s+35\.8%", "10-year T-note", 45.2),
    (["MGC", "GC"], r"Metals\s+Gold\s+20\.6%", "Gold", 48.1),
]
for codes, pat, name, v2020 in CO_ROWS:
    add(codes, "T2a", "hft_share_pct", v2020, "product" if len(codes) == 1 else "leader",
        "2012..2021 (columns: 2012, 2020, percent change, average over 2012-2021)",
        f"Coughlan and Orlov (2022, CFTC OCE working paper, 'High-Frequency Trading and Market Quality: Evidence from "
        f"Account-Level Futures Data'), Table 1, '{name}': HFT share of total volume {v2020}% in 2020. HFT defined by "
        f"behaviour (Brogaard et al. 2019): account trades >0.25% of annual volume, end-of-day inventory <20% of its "
        f"volume, never holds >30% of daily volume intraday. Narrower than ATS. Most recent product-level CFTC "
        f"figure found.",
        q(CO22, pat), src(CO22))
add(["ES-not-in-universe"], "T2a", "hft_share_pct", 49.7, "other_venue", "2012..2021",
    "E-mini S&P 500 (not a candidate; context for the equity group): HFT share 49.7% in 2020 (31.8% in 2012).",
    q(CO22, r"Financials\s+E-mini S&P500"), src(CO22))
add(["MZC", "MZS", "MZW", "MZL", "MZM", "XC", "XK", "XW", "ZC", "ZS", "ZW", "ZL", "ZM", "MCL", "QM", "CL", "MNG",
     "QG", "NG", "MGC", "GC", "SIL", "SI", "MHG", "HG", "ZT", "ZF", "ZN", "ZB", "2YY", "5YY", "10Y", "30Y", "M2K",
     "RTY", "MYM", "YM", "MNQ", "NQ", "M6E", "6E", "M6A", "6A"],
    "T2a", "hft_definition", "HFT classification", "futures_broad", "2012..2021",
    "Definition used by Coughlan-Orlov 2022 for the hft_share_pct items.",
    q(CO22, r"Accounts are classi.ed as HFTs if they trade more than", n=3), src(CO22))

# ---------- Fett and Haynes 2017: PTF share of all futures volume ----------
add(["ALL"], "T2a", "ptf_share_pct", 51, "futures_broad", "analyzed period of Fett-Haynes 2017 (CME futures, to 2016)",
    "Principal trading firms (by firm-type classification, not automation flag) = 51% of all CME futures volume; "
    "52% in June 2016 (Table 3). Not product-specific.",
    q(FH17, r"basis, PTFs accounted for 51 percent of all volume"), src(FH17))

# ---------- Fishe, Haynes, Onur 2015: proprietary share of order messages, Treasuries ----------
add(["ZT", "ZF", "ZN", "ZB"], "T2a", "proprietary_order_message_share_pct",
    "2Y 55.5, 5Y 57.1, 10Y 57.8, 30Y 58.7 (of all order messages); order submissions 85.1, 92.6, 90.3, 92.4",
    "product", "2014-10-06..2014-10-17 (order book data)",
    "Speed and Latency in Treasury and e-Mini Futures Part 1 (CFTC OCE, Dec 2015) Table 2: share of order messages "
    "from proprietary accounts. A message share, not a volume share and not an automation flag. Table 1 also counts "
    "unique automated vs manual accounts (2Y 797 vs 709; 5Y 1,887 vs 1,466; 10Y 2,705 vs 4,052; 30Y 1,857 vs 3,267).",
    q(SL15, r"^\s*Proprietary\s+59\.6%"), src(SL15))
add(["ZT", "ZF", "ZN", "ZB"], "T2a", "automated_accounts_count", "2Y 797; 5Y 1,887; 10Y 2,705; 30Y 1,857 automated accounts",
    "product", "2014-10-06..2014-10-17", "Account counts, Table 1 (row 'Automated'; columns E-mini, 2Y, 5Y, 10Y, 30Y).",
    q(SL15, r"^\s*Automated\s+4,380"), src(SL15))

# ---------- CFTC DMO Market Intelligence Branch 2019: automated share of transactions by group ----------
DMO_Q = q(DMO19, r"Overall, across all the", n=4)
DMO_GROUPS = [
    (["M6E", "6E", "M6A", "6A"], "Currencies", "about 91 (2018)"),
    (["M2K", "RTY", "MYM", "YM", "MNQ", "NQ"], "Equities", "about 79 (2018)"),
    (["ZT", "ZF", "ZN", "ZB", "2YY", "5YY", "10Y", "30Y"], "Financials (10-YR Note, 30-YR Bond, Eurodollar, Fed Funds)",
     "about 87 (2018)"),
    (["MCL", "QM", "CL", "MNG", "QG", "NG"], "Energies", "about 79 (2018)"),
    (["MGC", "GC", "SIL", "SI", "MHG", "HG"], "Metals", "about 82 (2018)"),
    (["MZC", "MZW", "XC", "XW", "ZC", "ZW"], "Grains", "about 71 (2018)"),
    (["MZS", "MZL", "MZM", "XK", "ZS", "ZL", "ZM"], "Oilseeds (soybeans, meal, oil)", "about 71 (2018)"),
]
for codes, gname, val in DMO_GROUPS:
    add(codes, "T2a", "auto_share_of_transactions_pct", val, "product_group", "2013..2018 (annual)",
        f"CFTC Division of Market Oversight, Market Intelligence Branch staff report 'Impact of Automated Orders in "
        f"Futures Markets' (March 2019), Exhibit 2 (chart; value read from the chart by the reader, +/- about 1 point; "
        f"chart saved as reports/stage_e32b_briefs/work/RATES/RATES_dmo_exh2-000.png): DMO group '{gname}', share of "
        f"automated (ATS) orders among transactions, counted by number of transactions regardless of contracts. "
        f"Groups built from the most active contracts (30 in total).",
        DMO_Q, src(DMO19))

# ---------- crypto: not covered ----------
searched = [
    {"codes": ["MET", "ETH", "MBT", "BTC"], "topic": "T2a",
     "queries": ["CFTC OCE research papers listing pages 0-3 (saved)", "Haynes-Roberts 2015/2017/2019 tables",
                 "CFTC Ferko-Moin-Onur-Penick 2021 'Who Trades Bitcoin Futures and Why?' grep automat|HFT|algorithm"],
     "note": "No CFTC automated-trading or HFT share for CME bitcoin or ether futures found. Haynes-Roberts windows end "
             "2018-10 and have no crypto group; Coughlan-Orlov 2022 covers nine non-crypto contracts; the 2021 BTC paper "
             "classifies traders as concentrated/diversified/hybrid by holdings, with no automation flag."},
    {"codes": ["2YY", "5YY", "10Y", "30Y"], "topic": "T2a",
     "queries": ["CFTC OCE listings", "Haynes-Roberts updates"],
     "note": "No CFTC automation share for the micro yield futures (listed 2021-08-16, after every CFTC window found)."},
    {"codes": ["M6A", "6A", "M2K", "RTY", "ZT", "ZB", "SIL", "SI", "MHG", "HG", "ZL", "ZM", "MZL", "MZM"],
     "topic": "T2a", "queries": ["Coughlan-Orlov 2022 Table 1", "Haynes-Roberts Table 3"],
     "note": "No product-level CFTC figure: AUD/USD, Russell 2000, 2-Year, Bond, soybean oil and meal are not in the "
             "named-product tables (Copper, Silver have Haynes-Roberts rows but no Coughlan-Orlov row). Group figures apply."},
    {"codes": ["ALL"], "topic": "T2a", "queries": ["WebSearch: CFTC OCE automated trading futures by product 2019-2022 Haynes"],
     "note": "No CFTC Haynes-Roberts-style update after Update #2 (window to 2018-10-31, published 2019-03-26) found."},
]

doc = {
    "family": "shared_cftc", "worker": "RatesReader-OpusHigh",
    "codes": ["MCL", "QM", "CL", "MNG", "QG", "NG", "MGC", "GC", "SIL", "SI", "MHG", "HG", "MZC", "MZS", "MZW", "MZL",
              "MZM", "XC", "XK", "XW", "ZC", "ZS", "ZW", "ZL", "ZM", "2YY", "5YY", "10Y", "30Y", "ZT", "ZF", "ZN", "ZB",
              "M2K", "RTY", "MYM", "YM", "MNQ", "NQ", "M6E", "6E", "M6A", "6A", "MET", "ETH", "MBT", "BTC"],
    "started_pdt": "2026-10-28T22:48PDT", "finished_pdt": pdt_now(),
    "websearch_calls": 2, "fulltext_reads_t6": 0, "notices": [],
    "sources_read": [
        "Haynes & Roberts (2015) Automated Trading in Futures Markets, CFTC OCE (E.28 copy)",
        "Haynes & Roberts (2017) Automated Trading in Futures Markets - Update (E.28 copy)",
        "Haynes & Roberts (2019-03-26) Automated Trading in Futures Markets - Update #2, window 2012-2018",
        "Coughlan & Orlov (2022-07-29) High-Frequency Trading and Market Quality, CFTC OCE",
        "Fett & Haynes (2017) The Futures Trading Landscape, CFTC OCE",
        "Fishe, Haynes & Onur (2015) Speed and Latency in Treasury and e-Mini Futures Part 1, CFTC OCE",
        "CFTC DMO MIB (2019) Impact of Automated Orders in Futures Markets",
        "Ferko, Moin, Onur & Penick (2021) Who Trades Bitcoin Futures and Why?, CFTC OCE"],
    "items": items, "searched_not_found": searched, "per_code": {},
    "gaps": ["DMO 2019 Exhibit 2 values are read from a chart (approximate).",
             "No CFTC series after 2022 on automation by product found within budget."],
}
OUT.write_text(json.dumps(doc, indent=1, ensure_ascii=False))
print("items", len(items), "->", OUT)
