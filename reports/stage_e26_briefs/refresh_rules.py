"""Stage E.26 Task 4: refresh reports/stage_e19_rules.json for Topstep's Tier 1 news window.

Evidence: reports/stage_e26_briefs/topstep_tier1.md (TopstepRulesReader-OpusMed, pages fetched
2026-10-21 02:20:34-02:20:41 PDT, saved under reports/stage_e26_briefs/pages/topstep/) and E.25's
R9 reader (reports/stage_e25_briefs/R9_prop_rules.md, rows E01-E07). Builds a new document (the
loaded one is not mutated), validates it with prop_econ.rules.validate_rules, and writes it in the
file's own serialization (indent 1, UTF-8, no trailing newline). Schema unchanged (e19-rules-1):
the window goes in new leaves, each with exactly one rule, which the validator accepts as extras.
Usage: PYTHONPATH=. uv run python reports/stage_e26_briefs/refresh_rules.py [--check]
"""
from __future__ import annotations

import copy
import hashlib
import json
import sys
from pathlib import Path

from prop_econ.rules import validate_rules

REPO = Path(__file__).resolve().parents[2]
RULES = REPO / "reports" / "stage_e19_rules.json"
PAGES = "reports/stage_e26_briefs/pages/topstep"
EVIDENCE = "reports/stage_e26_briefs/topstep_tier1.md"
REFRESH_PDT = "2026-10-21T02:20:34-07:00"


def source(url: str, title: str, utc: str, pdt: str, page: str, modified: str) -> dict:
    path = REPO / PAGES / f"ts_{page}.html"
    return {"url": url, "title": title, "fetched_utc": utc, "fetched_pdt": pdt, "file": f"{PAGES}/ts_{page}.html",
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "page_updated": f"dateModified {modified}",
            "method": "curl", "http_status": "200"}


SOURCES = {
    "S42": source("https://help.topstep.com/en/articles/13613539-risk-adjustments-high-risk-high-volatility",
                  "Risk Adjustments (High Risk / High Volatility): Tier 1 News Events Restrictions",
                  "2026-10-21 09:20:34Z", "2026-10-21 02:20:34 PDT", "13613539", "2026-10-20T19:42:21Z"),
    "S43": source("https://help.topstep.com/en/articles/8284211-economic-releases", "Economic Releases",
                  "2026-10-21 09:20:38Z", "2026-10-21 02:20:38 PDT", "8284211", "2026-10-15T17:51:06Z"),
    "S44": source("https://help.topstep.com/en/articles/10305426-prohibited-trading-strategies-at-topstep",
                  "Prohibited Trading Strategies at Topstep",
                  "2026-10-21 09:20:41Z", "2026-10-21 02:20:41 PDT", "10305426", "2026-06-10T14:02:45Z"),
}

Q_MINIS = ("Minis (ES, RTY, YM, NQ, NKD, GC, SI, HG, PL): No new opening transactions permitted during the 10-minute "
           "window surrounding the release (5 minutes before, 5 minutes after).")
Q_MICROS = ("Micros (MES, M2K, MYM, MNQ, MGC): Opening transactions limited to 1, 3, 6, 9, and 15 contracts for the "
            "$25K, $50K, $100K, $150K, and $250K account sizes, respectively, during the window (see table below)")
Q_MHG = ("MHG and SIL: Opening transactions limited to 1, 2, 5, 7, 12 contracts for the $25K, $50K, $100K, $150K, "
         "and $250K account sizes, respectively, during the window (see table below)")
Q_OTHER = "Other products (energies, rates, FX, etc.) are unaffected."
Q_EXISTING = ("Existing Positions: Traders holding existing positions in equity index products and metals prior to 5 "
              "minutes before the news event may keep them open and manage them through the Tier 1 News Events "
              "window. TopstepX™ automatically enforces these limits, so no manual adjustment is required for "
              "existing trades.")
Q_PENDING = ("Pending orders: Pending orders are not open positions. They will not fill during the 10-minute window, "
             "and new pending orders intended to execute during this timeframe cannot be placed. TP/SL brackets that "
             "are reducing/closing positions will be accepted during the window.")
Q_EVENTS = ("Consumer Price Index (CPI) | 7:30 AM | 7:25 to 7:35 AM ; FOMC rate decision | 1:00 PM | 12:55 to 1:05 PM ; "
            "FOMC press conference | 1:30 PM | 1:25 to 1:35 PM ; Non Farm Payroll (NFP/Unemployment Rate) | 7:30 AM | "
            "7:25 to 7:35 AM ; Producer Price Index (PPI) | 7:30 AM | 7:25 to 7:35 AM")
N_SECTION = "S42 section 'Tier 1 News Events Restrictions' (anchor h_bb7f1d281e); quotes verbatim in " + EVIDENCE

WINDOW = {
    "minutes_before": (5, Q_MINIS, "ADDED E.26. The window is 10 minutes, 5 before and 5 after the release."),
    "minutes_after": (5, Q_MINIS, "ADDED E.26."),
    "minis_new_opens_blocked": (True, Q_MINIS, "ADDED E.26. Combine and XFA tables: 'Equity Minis: Blocked' / "
                                "'Minis/Micros 0/...' in every row."),
    "mini_products": ("ES, RTY, YM, NQ, NKD, GC, SI, HG, PL", Q_MINIS, "ADDED E.26."),
    "micro_products_capped": ("MES, M2K, MYM, MNQ, MGC; MHG and SIL on their own caps", Q_MICROS,
                              "ADDED E.26. Per-size caps: sizes.<size>.combine.tier1_news_* and "
                              "sizes.<size>.xfa.tier1_news_micro_caps_by_balance."),
    "other_products_unaffected": (True, Q_OTHER, "ADDED E.26. Energies, rates and FX trade normally in the window."),
    "existing_positions_may_be_held": (True, Q_EXISTING, "ADDED E.26. Flattening before the window is not required."),
    "pending_orders_fill_in_window": (False, Q_PENDING, "ADDED E.26. Closing TP/SL brackets are accepted."),
    "closing_brackets_accepted": (True, Q_PENDING, "ADDED E.26."),
    "events_ct": ("CPI 07:30 (07:25-07:35); FOMC rate decision 13:00 (12:55-13:05); FOMC press conference 13:30 "
                  "(13:25-13:35); NFP 07:30 (07:25-07:35); PPI 07:30 (07:25-07:35)", Q_EVENTS,
                  "ADDED E.26. Table 'Tier 1 News Events' (CT), cells joined by ' | ', rows by ' ; '. PPI was added "
                  "on 2026-10-20 (S42 dateModified), after E.25's copy of 2026-10-16."),
    "enforcement": ("platform: TopstepX refuses restricted opening orders", Q_EXISTING,
                    "ADDED E.26. Neither S42 nor S43 states a rule-breach or account consequence for the window "
                    "(worker grep for enforce, violation, breach, reject, suspen, terminat)."),
}
XFA_ROWS = {  # S42 table 'Express Funded Accounts' (Balance | Margin | Minis/Micros | SIL & MHG)
    "50K": "Below $1500 | $20,000 | 0/1 | 0/1 ; $1500-$2000 | $30,000 | 0/1 | 0/1 ; Above $2000 | $50,000 | 0/3 | 0/2",
    "100K": ("Below $1500 | $30,000 | 0/1 | 0/1 ; $1500-$2000 | $40,000 | 0/2 | 0/2 ; $2,000-3,000 | $50,000 | 0/3 | "
             "0/2 ; Above $3,000 | $100,000 | 0/6 | 0/5"),
    "150K": ("Below $1500 | $30,000 | 0/1 | 0/1 ; $1500-$2000 | $40,000 | 0/2 | 0/2 ; $2,000-3,000 | $50,000 | 0/3 | "
             "0/2 ; $3,000-$4,500 | $100,000 | 0/6 | 0/5 ; Above $4,500 | $150,000 | 0/9 | 0/7"),
}
COMBINE_CAPS = {"50K": (3, 2), "100K": (6, 5), "150K": (9, 7)}  # micros (L174), MHG/SIL (L175)


def rule(rid: str, path: str, value, quote: str, note: str) -> dict:
    return {"id": rid, "path": path, "value": value, "status": "SOURCED", "readings": [value], "source": "S42",
            "quote": quote, "note": f"{note} {N_SECTION}."}


def refreshed(doc: dict) -> dict:
    new = copy.deepcopy(doc)
    if any(s in new["sources"] for s in SOURCES) or "tier1_news_window" in new["global"]:
        raise SystemExit("already refreshed")
    new["sources"] = {**new["sources"], **SOURCES}
    new["global"]["tier1_news_window"] = {k: v[0] for k, v in WINDOW.items()}
    rules = list(new["rules"])
    for i, r in enumerate(rules):
        if r["id"] == "R040":
            assert r["path"] == "global.news_flatten_required" and r["value"] is False
            rules[i] = {**r, "source": "S42", "quote": Q_EXISTING,
                        "note": ("REFRESHED E.26 (2026-10-21). Value unchanged: flattening is still not required. "
                                 "The E.19 quote (S22: 'Topstep doesn't require you to flatten positions during "
                                 "economic releases — in SIM or Funded Accounts.') is gone from the Economic Releases "
                                 "article (S43, dateModified 2026-10-15T17:51:06Z), which now reads 'Topstep restricts "
                                 "trading for a short period during Tier 1 News Events.' New opening positions in "
                                 "equity index products and metals are restricted inside the Tier 1 window: "
                                 "global.tier1_news_window.*. E.25 R9 rows E01-E04. P06 unchanged (S44, "
                                 "dateModified 2026-06-10T14:02:45Z).")}
    first = n = int(rules[-1]["id"][1:])
    for key, (value, quote, note) in WINDOW.items():
        n += 1
        rules.append(rule(f"R{n:03d}", f"global.tier1_news_window.{key}", value, quote, note))
    for size, (micros, mhg) in COMBINE_CAPS.items():
        new["sizes"][size]["combine"]["tier1_news_micro_open_cap"] = micros
        new["sizes"][size]["combine"]["tier1_news_mhg_sil_open_cap"] = mhg
        new["sizes"][size]["xfa"]["tier1_news_micro_caps_by_balance"] = XFA_ROWS[size]
        n += 1
        rules.append(rule(f"R{n:03d}", f"sizes.{size}.combine.tier1_news_micro_open_cap", micros, Q_MICROS,
                          f"ADDED E.26. Combine table row '{size}': 'Capped at {micros} micros'."))
        n += 1
        rules.append(rule(f"R{n:03d}", f"sizes.{size}.combine.tier1_news_mhg_sil_open_cap", mhg, Q_MHG,
                          "ADDED E.26."))
        n += 1
        rules.append(rule(f"R{n:03d}", f"sizes.{size}.xfa.tier1_news_micro_caps_by_balance", XFA_ROWS[size],
                          "Express Funded Accounts (XFAs) have margin that scales with balance.",
                          "ADDED E.26. XFA table rows for this size, cells joined by ' | ' (Balance | Margin | "
                          "Minis/Micros | SIL & MHG), rows by ' ; '; balance is the XFA balance (start 0)."))
    new["rules"] = rules
    new["refreshes"] = [{"stage": "E.26", "pdt": REFRESH_PDT, "what": "Topstep Tier 1 news window (E.25 return "
                         "section 7 item 6; E.25 R9 rows E01-E07)", "sources_added": sorted(SOURCES),
                         "rules_changed": ["R040"], "rules_added": f"R{first + 1:03d}-R{n:03d}", "evidence": EVIDENCE}]
    return new


def main(argv: list[str]) -> int:
    raw = RULES.read_bytes()
    doc = json.loads(raw)
    new = refreshed(doc)
    extras = validate_rules(new)
    out = json.dumps(new, indent=1, ensure_ascii=False).encode()
    print("valid; extras", len(extras), "rules", len(doc["rules"]), "->", len(new["rules"]),
          "sha256 before", hashlib.sha256(raw).hexdigest()[:16], "after", hashlib.sha256(out).hexdigest()[:16])
    if "--check" not in argv:
        RULES.write_bytes(out)
        print("written", RULES.relative_to(REPO))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
