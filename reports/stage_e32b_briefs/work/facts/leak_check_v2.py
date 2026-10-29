"""Leak check v2 (after F4_audit.md B1): substring-based. Firm names, distinctive plan names, platform names and
product names are searched as case-insensitive SUBSTRINGS (no word boundaries); generic plan words (Pro, Flex, Direct,
Daily, Growth, Select, Core, Rapid, Builder, Master, Momentum, Combine, Qualification, Option 1/2) as capitalised tokens
in the firm sheet; codes as tokens; plus units and size patterns. Every hit is printed with its context and the
justification rule it falls under; a hit no rule covers is UNJUSTIFIED (exit 1).

Usage: leak_check_v2.py [out.txt]"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import mask_vocab as V  # noqa: E402

B = HERE.parents[1]
E28 = B.parent / "stage_e28_briefs"
CODES = ["MCL", "QM", "CL", "MNG", "QG", "NG", "MGC", "GC", "SIL", "SI", "MHG", "HG", "M6E", "6E", "M6A", "6A", "MET",
         "ETH", "MBT", "BTC", "M2K", "RTY", "MYM", "YM", "MNQ", "NQ", "2YY", "5YY", "10Y", "30Y", "ZT", "ZF", "ZN", "ZB",
         "MZC", "MZS", "MZW", "MZL", "MZM", "XC", "XK", "XW", "ZC", "ZS", "ZW", "ZL", "ZM"]
DISTINCT_PLANS = ["LucidPro", "LucidFlex", "LucidDirect", "LucidLive", "LucidBLACK", "LucidDaily", "LucidMaxx",
                  "Trading Combine", "Express Funded", "Live Funded Account", "XFA", "LFA", "Back2Funded",
                  "Standard Path", "Consistency Path", "Qualification Account", "Master Account", "Fast Track",
                  "Rapid Sim Funded", "Pro Sim Funded", "Daily Trading"]
GENERIC_PLANS = ["Pro", "Flex", "Direct", "Daily", "Growth", "Select", "Core", "Rapid", "Builder", "Master",
                 "Momentum", "Combine", "Qualification", "Lightning", "Maxx", "BLACK"]
UNITS = {
    "barrels/bbl": r"\b(?:bbl|barrels?)\b", "ounces/oz": r"\b(?:oz|ounces?)\b", "bushels": r"\bbushels?\b",
    "currency notional": r"\b(?:EUR|AUD|USD)\s?\d[\d,.]*(?:\s?(?:m|million|bn|k))?\b|\$\s?\d[\d,.]*\s?(?:m|million)\b",
    "tick with a number": r"\d[\d./]*\s*(?:index points?\s)?ticks?\b|\bticks?\s(?:size\s)?(?:of\s|=\s|is\s)?\$?\d[\d./]*",
    "multiplier": r"multiplier",
}


def patterns(sheet: str):
    p = []
    for f, names in V.FIRM_NAMES.items():
        for n in set(names + [f]):
            p.append(("firm", n, re.compile(re.escape(n), re.I)))
    for n in DISTINCT_PLANS:
        p.append(("plan", n, re.compile(re.escape(n), re.I)))
    if sheet == "firms":
        for n in GENERIC_PLANS:
            p.append(("plan-token", n, re.compile(r"(?<![A-Za-z])" + re.escape(n) + r"(?![A-Za-z])")))
    plat = set(V.PLATFORMS) | set(json.loads((E28 / "A3_mask_key.json").read_text())["platforms"].values())
    for n in sorted(plat):
        p.append(("platform", n, re.compile(re.escape(n), re.I)))
    for n in V.PRODUCT_NAMES:
        p.append(("product", n, re.compile(re.escape(n), re.I)))
    for c in CODES:
        p.append(("code", c, re.compile(r"(?<![A-Za-z0-9_])" + re.escape(c) + r"(?:[FGHJKMNQUVXZ]\d{1,2})?(?![A-Za-z0-9_])")))
    for lp in V.LITIGATION_LEAK:
        p.append(("litigation", lp, re.compile(lp, re.I)))
    for lit in ("http", "www", ".com", "reports/", ".json", ".md"):
        p.append(("literal", lit, re.compile(re.escape(lit), re.I)))
    key = json.loads((E28 / "A3_mask_key.json").read_text())
    for grp in ("contracts", "firms", "platforms", "other_products"):
        for lab in key[grp]:
            p.append(("E28 label", lab, re.compile(r"(?<![A-Za-z0-9])" + re.escape(lab) + r"(?![0-9])")))
    for k, r in UNITS.items():
        p.append(("unit", k, re.compile(r, re.I)))
    return p


# Justification rules: (kind, name, regex on the hit's context window) -> reason. Each was written after reading the
# hit list (see the output file); a hit that matches no rule is unjustified.
RULES = [
    ("unit", "tick with a number", r"Sharpe at \d tick|half[- ]spread|spread (?:of|at|cost|=)|cost[s]? |round trip|"
     r"max(?:imum)? spread|slippage|ticks? (?:wide|spread)|spread[s]? (?:is|was|were|of)|bid-ask|quoted spread|"
     r"\d ticks? (?:away|from|beyond|above|below|through|deep|behind)|tick cut|minimum tick|one tick",
     "a cost, quoting or spread statement in ticks, not the contract's tick size"),
    ("unit", "currency notional", r"TOB|top[- ]of[- ]book|book size|million at|\$\d[\d,.]*\s?million|USD \d[\d,.]*(?:m|bn)",
     "a book-size or volume statement in USD (liquidity), not a contract size"),
    ("unit", "currency notional", r"(?:EUR|AUD|USD)\s?\d{4}\b|EUR/USD|AUD/USD",
     "a currency pair or a year next to a currency word, not an amount"),
    ("unit", "multiplier", r"[Mm]ultiplier\]|\[multiplier\]", "the masked placeholder itself"),
    ("unit", "ounces/oz", r"troy ounce|per ounce|\$/oz|USD/oz|/oz", "a price unit of the asset class (gold quoted per ounce), not a contract size"),
    ("unit", "bushels", r"per bushel|cents?/bu|c/bu|/bushel", "a price unit of the asset class, not a contract size"),
    ("unit", "barrels/bbl", r"per barrel|\$/bbl|/bbl|USD/bbl|barrels? (?:per day|a day)|million barrels",
     "a price unit or an inventory quantity of the asset class, not a contract size"),
    ("plan", "Daily Trading", r"daily trading(?: volume|/)", "lowercase generic phrase (daily trading volume), "
     "not a plan name"),
    ("platform", "Rithmic", r"(?i)algorithmic", "substring of 'algorithmic', not the platform"),
    ("unit", "currency notional", r"incentive pool|USD \d[\d,]* monthly", "a program's incentive money, not a contract size"),
    ("unit", "currency notional", r"/USD \d+-minute", "a currency pair followed by a bar length, not an amount"),
    ("unit", "tick with a number", r"tick a trade|1/2 tick|adverse selection",
     "a per-trade cost or adverse-selection figure in ticks, not the contract's tick size"),
    ("plan-token", "Daily", r"Daily Loss Limit", "the generic limit name used by every firm, not a plan name"),
    ("plan-token", "Momentum", r"momentum", "finance term (price momentum), not a plan name"),
    ("plan-token", "Core", r"Core (?:Metal|PCE|CPI|inflation)", "a product group or macro series name, not a plan"),
    ("plan-token", "Direct", r"Direct (?:market|access|debit|deposit)", "generic phrase, not a plan name"),
    ("platform", "ATAS", r"(?i)d?atas", "substring of an ordinary word (data set)"),
]


def strings(x, path=""):
    if isinstance(x, dict):
        for k, v in x.items():
            yield from strings(v, f"{path}/{k}")
    elif isinstance(x, list):
        for i, v in enumerate(x):
            yield from strings(v, f"{path}/{i}")
    elif x is not None:
        yield path, str(x)


def main() -> int:
    out = []
    unjust = 0
    totals = {}
    for sheet, name in (("contracts", "F4_masked_contracts.json"), ("firms", "F4_masked_firms.json")):
        doc = json.loads((B / name).read_text())
        texts = [(p, t) for p, t in strings(doc) if not p.startswith("/format")]
        pats = patterns(sheet)
        n_sheet = 0
        for kind, nm, rx in pats:
            for path, t in texts:
                for m in rx.finditer(t):
                    ctx = t[max(0, m.start() - 60):m.end() + 60].replace("\n", " ")
                    why = next((r[3] for r in RULES if r[0] == kind and r[1] == nm and re.search(r[2], ctx)), None)
                    n_sheet += 1
                    totals[(sheet, kind, nm, why is not None)] = totals.get((sheet, kind, nm, why is not None), 0) + 1
                    if why is None:
                        unjust += 1
                    out.append(f"{sheet}\t{kind}\t{nm}\t{'JUSTIFIED: ' + why if why else 'UNJUSTIFIED'}\t{path}\t{ctx}")
        out.append(f"# {sheet}: {len(pats)} patterns, {n_sheet} hits")
    summ = ["# summary (sheet, kind, pattern, justified): count"] + [
        f"# {k}: {v}" for k, v in sorted(totals.items())] + [f"# UNJUSTIFIED HITS: {unjust}"]
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "leak_v2_out.txt"
    dest.write_text("\n".join(summ + out) + "\n")
    print("\n".join(summ))
    return 1 if unjust else 0


if __name__ == "__main__":
    raise SystemExit(main())
