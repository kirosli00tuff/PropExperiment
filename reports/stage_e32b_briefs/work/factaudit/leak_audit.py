"""FactAuditor (E.32b C1v): independent leak check of the masked sheets.

Greps F4_masked_contracts.json and F4_masked_firms.json (as text) for every code, product name, firm name, plan
name, platform name, URL and path marker, reader item id, E.28 label, and a list of residual identifiers (listing
dates, filing numbers, legal names, cities, vendor names). Prints counts per pattern with up to 2 short contexts.
Read-only; writes nothing.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

B = Path("/home/kiros-li/Documents/GitHub/PropExperiment")
BR = B / "reports/stage_e32b_briefs"
E28 = B / "reports/stage_e28_briefs"

CODES = ["MCL", "QM", "CL", "MNG", "QG", "NG", "MGC", "GC", "SIL", "SI", "MHG", "HG", "M6E", "6E", "M6A", "6A", "MET",
         "ETH", "MBT", "BTC", "M2K", "RTY", "MYM", "YM", "MNQ", "NQ", "2YY", "5YY", "10Y", "30Y", "ZT", "ZF", "ZN",
         "ZB", "MZC", "MZS", "MZW", "MZL", "MZM", "XC", "XK", "XW", "ZC", "ZS", "ZW", "ZL", "ZM"]
OTHER_CODES = ["ES", "MES", "NKD", "PL", "PA", "UB", "TN", "HO", "RB", "E7", "6C", "6B", "6J", "GF", "LE", "HE", "4GC",
               "SGC", "SGU", "QQQ", "SPY", "IWM", "DIA"]
FIRMS = ["Topstep", "TopstepX", "Topstepfunded", "Patak", "Lucid", "LucidPro", "LucidFlex", "LucidDaily", "Tradeify",
         "My Funded Futures", "MyFundedFutures", "MFFU", "Bulenox"]
PLANS = ["Trading Combine", "Express Funded", "XFA", "LFA", "Live Funded Account", "Standard Path", "Consistency Path",
         "Growth", "Advanced", "Select", "Lightning", "Straight to Sim", "Starter", "Expert", "Rapid", "Builder",
         "Qualification Account", "Master Account", "Pro Sim", "Pro Eval", "Flex", "Direct", "Daily Trading", "red folder"]
PLATFORMS = ["ProjectX", "Tradovate", "Rithmic", "NinjaTrader", "CQG", "TradingView", "MotiveWave", "Quantower",
             "Tradesea", "Sierra Chart", "Jigsaw", "Bookmap", "ATAS", "R|Trader", "MultiCharts", "dxFeed", "Volumetrica",
             "WealthCharts", "DeepChart", "Trader Composite", "R|API", "Gateway API"]
PRODUCT_WORDS = ["Micro WTI", "E-mini Crude", "Light Sweet Crude", "Henry Hub", "E-mini Natural Gas", "Micro Henry Hub",
                 "Micro Gold", "E-micro Gold", "1,000 oz", "1000 oz", "Micro Silver", "Micro Copper", "E-micro",
                 "Micro EUR", "Micro AUD", "Euro FX", "Australian dollar", "AUD/USD", "EUR/USD", "Micro Ether",
                 "Micro Bitcoin", "Bitcoin Futures", "Ether Futures", "Russell 2000", "E-mini Dow", "Micro E-mini Dow",
                 "Dow Jones", "Nasdaq-100", "Nasdaq", "E-mini Nasdaq", "Micro E-mini", "2-Year", "5-Year", "10-Year",
                 "30-Year", "Yield Futures", "Treasury Note", "Treasury Bond", "T-Note", "T-Bond", "Ultra", "Mini-Sized",
                 "Micro Corn", "Micro Soybean", "Micro Wheat", "Soybean Oil", "Soybean Meal", "Chicago SRW", "WTI",
                 "Brent", "MMBtu", "troy", "barrel", "bushel", "crush", "crack spread", "Globex", "NYMEX", "COMEX",
                 "CBOT", "CME", "ICE", "EIA", "USDA", "WASDE", "Cushing"]
URLPATH = [r"https?://", r"\bwww\.", r"\.com\b", r"reports/", r"\.json\b", r"\.md\b", r"\.html?\b", r"\.txt\b",
           r"\.pdf\b", r"pages/", r"web\.archive", r"wayback"]
ITEM_IDS = [r"\b(?:CRUDE|NATGAS|METALS|GRAINS|RATES|EQUITY|FX|CRYPTO|CFTC|SB|FIRMS?|DATA|ATTN|NONPROP|R1|R2)-\d+\b"]
E28_LABELS = [r"\bC\d\d\b", r"\bF\d\d\b", r"\bP\d\d\b", r"\bX\d\d\b"]
RESIDUAL = [r"\b(?:NYMEX|COMEX|CBOT|CME)\s?\d\d-\d{3}\b", r"\bSR\s?\d\d-\d{3}\b", r"rules\d{8,}", r"\b\d:\d\d-cv-\d+",
            r"McCrudden", r"Patak", r"WorkMarket", r"\bADP\b", r"Chicago", r"Illinois", r"Delaware", r"Dubai",
            r"Austin", r"Florida", r"Texas", r"Toronto", r"London", r"2021-07-12", r"2019-05-06", r"2021-12-06",
            r"2021-05-03", r"2022-05-02", r"2023-11-06", r"2025-02-24", r"2021-08-16", r"2010-10-04", r"2017-12-18",
            r"2021-02-08", r"2003-04-07", r"\$172\b", r"\$135\b", r"\$125\b", r"90/10", r"Tier 1", r"Tier-1",
            r"volatility cap", r"\$0\.25\b", r"\$5 multiplier", r"\$50 multiplier", r"100 oz", r"5,000 oz",
            r"1,000 barrels", r"10,000 MMBtu", r"125,000", r"100,000", r"5,000 bushels", r"60,000", r"100 short tons",
            r"\$0\.10\b", r"0\.01 per", r"Cushing", r"Henry Hub", r"BrokerTec", r"Special Opening Quotation",
            r"\bBRR\b", r"ETHUSD", r"\bSOQ\b", r"\bACE\b", r"NFA", r"CFTC", r"\$1,200\b", r"\$1,250\b", r"\$2,500\b",
            r"50,100", r"52,100", r"\b16:45\b", r"\b16:10\b", r"\b15:10\b", r"\b15:59\b", r"Option 1", r"Option 2"]


def contexts(text: str, pat: re.Pattern, n: int = 2, w: int = 45) -> list[str]:
    out = []
    for m in pat.finditer(text):
        s = max(0, m.start() - w); e = min(len(text), m.end() + w)
        out.append(text[s:e].replace("\n", " "))
        if len(out) >= n:
            break
    return out


def run(group: str, pats: list[str], text: str, flags=0, show=True) -> int:
    total = 0
    for p in pats:
        rx = re.compile(p, flags)
        c = len(rx.findall(text))
        if c:
            total += c
            if show:
                print(f"  [{group}] {p!r}: {c} hit(s)")
                for ctx in contexts(text, rx):
                    print(f"      ...{ctx}...")
    return total


FIRMS_SUB = FIRMS + ["MyFunded", "Funded Futures", "Topstep", "Lucid", "Tradeify", "Bulenox", "MFFU"]
PLANS_SUB = PLANS + ["Combine", "Builder", "Growth", "Rapid", "Qualification Account", "Master Account", "Sim Funded",
                     "Pro Sim", "LucidLive", "Live Funded", "Trading Combine", "Express", "Straight"]


def main() -> int:
    substring = "--substring" in sys.argv  # names matched as substrings, any case, no word boundaries
    for name in ("F4_masked_contracts.json", "F4_masked_firms.json"):
        text = (BR / name).read_text(encoding="utf-8")
        print(f"== {name}: {len(text)} chars" + (" [substring mode]" if substring else ""))
        t = 0
        t += run("code", [rf"\b{re.escape(c)}\b" for c in CODES], text)
        t += run("other_code", [rf"\b{re.escape(c)}\b" for c in OTHER_CODES], text)
        if substring:
            t += run("firm", [re.escape(f) for f in FIRMS_SUB], text, re.I)
            t += run("plan", [re.escape(p) for p in PLANS_SUB], text, re.I)
            t += run("platform", [re.escape(p) for p in PLATFORMS], text, re.I)
        else:
            t += run("firm", [re.escape(f) for f in FIRMS], text, re.I)
            t += run("plan", [rf"\b{re.escape(p)}\b" for p in PLANS], text)
            t += run("platform", [rf"\b{re.escape(p)}\b" for p in PLATFORMS], text, re.I)
        t += run("url_path", URLPATH, text, re.I)
        t += run("item_id", ITEM_IDS, text)
        t += run("e28_label", E28_LABELS, text)
        print(f"  -> hard-leak total (codes, other codes, firms, plans, platforms, URLs/paths, item ids, E.28 labels): {t}")
        print("  -- product and asset words (asset/size class words allowed by the lead's ruling; full product names are not):")
        run("product_word", [re.escape(p) for p in PRODUCT_WORDS], text, re.I)
        print("  -- residual identifiers (reported for the lead's judgment):")
        run("residual", RESIDUAL, text, re.I)
    # labels: fresh and consistent
    key = json.loads((BR / "F4_mask_key.json").read_text())
    e28key = json.loads((E28 / "A3_mask_key.json").read_text())
    e28_labels = set()
    for sec in ("contracts", "firms", "platforms", "other_products"):
        e28_labels |= set(e28key.get(sec, {}).keys())
    new_labels = set(key["contracts"]) | set(key["firms"]) | set(key["platforms"])
    print("== labels: new", len(new_labels), "E.28", len(e28_labels), "overlap", sorted(new_labels & e28_labels))
    mc = json.loads((BR / "F4_masked_contracts.json").read_text())
    mf = json.loads((BR / "F4_masked_firms.json").read_text())
    print("   contract labels in sheet == key:", set(mc["contracts"]) == set(key["contracts"]),
          "| firm labels == key:", set(mf["firms"]) == set(key["firms"]),
          "| pair labels == key:", set(mf["pairs"]) == set(key["pairs"]))
    print("   contracts mapped:", len(set(key["contracts"].values())), "firms:", len(set(key["firms"].values())),
          "pairs:", len(set(key["pairs"].values())))
    return 0


if __name__ == "__main__":
    sys.exit(main())
