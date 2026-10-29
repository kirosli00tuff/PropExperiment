"""FactTable (Stage E.32b, C1): the per-code readings of lead ruling LR-S and the other table-level choices, kept as
data so build_f4.py stays mechanical. Each entry names the F2 item(s) it rests on. Nothing here is a score.

LR-S (verbatim in brief_wave_c.md): a spread figure qualifies if it covers the main session, the US day session or the
whole day and is (i) a median, (ii) a mean / time-weighted mean / set of hourly means all below 1.5 ticks, or (iii) a
sourced statement that the spread sits at one tick more than half the time, for the tick size in force in the F3
window. Touch counts only as a sourced median. No sibling transfer.
"""

# ---------------------------------------------------------------- spread S (primary)
# code -> (clause, item ids, note). A qualifying figure gives S = 1 tick (the median of whole-tick spreads with
# mean < 1.5, or the stated modal tick). Codes absent here: "none: S = 1 (u)".
SPREAD_QUALIFYING = {
    "CL": ("(ii)", ["CRUDE-48"], "hourly AVERAGE spreads over the US day session 09:00-14:30 ET, Q1 2023, most active "
                                "month: 1.27-1.29 ticks, all < 1.5 (CME whitepaper, full text)"),
    "NG": ("(ii)", ["NATGAS-1"], "program-measured time-weighted MEAN quoted spread, day session 08:00-13:30 CT, 5 dates "
                                "2025-05..2026-04: 1.25 ticks < 1.5 (E.2a)"),
    "QG": ("(ii)", ["NATGAS-2"], "program-measured time-weighted MEAN quoted spread, day session: 1.22 ticks < 1.5 (E.2a)"),
    "GC": ("(ii)", ["METALS-49", "METALS-1"], "hourly AVERAGE spreads over ET 08:00-13:00 (US day hours), Q1 2023: "
                                             "1.31-1.35 ticks, all < 1.5; also (iii) METALS-1 'one tick during almost "
                                             "all trading hours' (2017-Q1 2018, tick 0.10 unchanged)"),
    "HG": ("(ii)", ["METALS-50"], "hourly AVERAGE spreads over ET 08:00-13:00 (US day hours), Q1 2023: 1.38-1.45 ticks, "
                                 "all < 1.5 (all-hours average 1.55 is above 1.5; the US-day set is used)"),
    "SI": ("(iii)", ["METALS-2"], "'one tick wide most of the hours' (2017-Q1 2018); SI tick 0.005 is the tick in force "
                                 "in the F3 window"),
    "ZC": ("(ii)", ["GRAINS-1"], "MEAN quoted spread, day session (BBO), 2008-01..2010-01: 1.26 ticks < 1.5; tick 0.25 c "
                                "unchanged"),
    "ZS": ("(ii)", ["GRAINS-3", "GRAINS-33"], "MEAN of daily volume-weighted spreads, day session H1 2019: 1.118 ticks; "
                                             "whole-day average about 2020: 1.04 ticks; both < 1.5"),
    "ZF": ("(iii)", ["RATES-1"], "spread at the minimum increment > 99% of each trading day, RTH 2018; ZF tick unchanged"),
    "ZN": ("(iii)", ["RATES-1", "RATES-4"], "> 99% of each 2018 RTH day at the minimum increment; 94% of observations "
                                           "at one tick in March 2020; ZN tick unchanged"),
    "ZB": ("(iii)", ["RATES-1"], "> 99% of each trading day at the minimum increment, RTH 2018; ZB tick unchanged"),
    "6E": ("(ii)", ["FX-1"], "whole-day time-weighted AVERAGE top-of-book spread about 0.6 pip = 1.2 ticks, June 2021, "
                            "< 1.5"),
    "6A": ("(i)", ["FX-3"], "whole-day MEDIAN top-of-book spread 0.5 pip = 1 tick, December 2020, after the 2020-11-23 "
                           "tick change (tick in force in the F3 window)"),
}

# code -> why the figures found do not qualify (reported; S = 1 (u)).
SPREAD_NOT_QUALIFYING = {
    "MNG": (["NATGAS-3"], "time-weighted MEAN 2.414 ticks >= 1.5"),
    "ZT": (["RATES-1"], "2018 statement predates the 2019 ZT tick change (LR-S names this case)"),
    "10Y": (["RATES-5"], "AVERAGE 1.67 ticks >= 1.5 (RTH 2024)"),
    "BTC": (["CRYPTO-1", "CRYPTO-2"], "AVERAGE spreads 13.64 (Jan 2026) and 4.72 (Apr 2023) ticks, session not stated"),
    "ZW": (["GRAINS-2"], "only a MEAN pooled over corn, wheat and soybeans (1.1 ticks, 2015-16): a figure computed "
                         "partly on other codes, sessions as pooled; not a wheat figure (for_lead)"),
    "ZL": (["GRAINS-35", "GRAINS-51"], "snippet only (US hours 2.06 ticks, 2022), and >= 1.5"),
    "ZM": (["GRAINS-50", "GRAINS-51"], "no spread figure (E.31 markouts; snippet ranking only)"),
    "MCL": (["CRUDE-1", "CRUDE-48"], "figures are CL's (no sibling transfer)"),
    "QM": (["CRUDE-1", "CRUDE-48"], "figures are CL's (no sibling transfer)"),
    "MGC": (["METALS-1", "METALS-49"], "figures are GC's (no sibling transfer)"),
    "SIL": (["METALS-2"], "figure is SI's (no sibling transfer)"),
    "MHG": (["METALS-50"], "figure is HG's (no sibling transfer)"),
    "M6E": (["FX-5", "FX-6"], "no published figure; forum pointer only"),
    "M6A": (["FX-5"], "no published figure"),
    "MNQ": (["EQUITY-1", "EQUITY-2"], "abstract with no figure; snippet pointer"),
    "NQ": (["EQUITY-1", "EQUITY-2"], "abstract with no figure; snippet pointer"),
    "MET": (["CRYPTO-3", "CRYPTO-4"], "none sourced; forum pointer only"),
    "ETH": (["CRYPTO-3", "CRYPTO-4"], "none sourced; forum pointer only"),
    "MBT": (["CRYPTO-1", "CRYPTO-2", "CRYPTO-3"], "figures are BTC's (no sibling transfer)"),
}

# ---------------------------------------------------------------- touch (primary: sourced medians only)
TOUCH_QUALIFYING = {
    "NG": (5, ["NATGAS-4"], "median displayed size at best bid/ask, day session, 5 dates 2025-26 (E.2a): bid 5, ask 5"),
    "QG": (10, ["NATGAS-5"], "median displayed size, day session (E.2a): bid 10, ask 10"),
    "MNG": (3, ["NATGAS-6"], "median displayed size, day session (E.2a): bid 3, ask 3 (13:00-13:30 CT bid 2)"),
    "GC": (4.62, ["METALS-3"], "level-1 MEDIAN displayed volume 4.62 contracts, 2010, 06:30-13:30 exchange time as "
                              "printed (Richards, Peters and Dunsmuir, Quantitative Finance 2015); a US day window "
                              "(for_lead: old window, and it sets touch < 5)"),
    "SI": (6.56, ["METALS-4"], "level-1 MEDIAN displayed volume 6.56 contracts, 2010, 08:30-13:00 (same paper)"),
}
TOUCH_NOT_QUALIFYING = {
    "CL": (["CRUDE-2", "CRUDE-49", "CRUDE-50"], "CRUDE-2 is a median (7, 2012-13) but its session is not stated; "
                                                "CRUDE-49/-50 are averages"),
    "HG": (["METALS-52"], "averages only"),
    "ZC": (["GRAINS-5"], "means only"), "ZW": (["GRAINS-6"], "means only"),
    "ZS": (["GRAINS-7", "GRAINS-34"], "means only"),
    "ZT": (["RATES-2"], "averages only (2018)"), "ZF": (["RATES-2"], "averages only (2018)"),
    "ZN": (["RATES-2"], "averages only (2018)"), "ZB": (["RATES-2"], "averages only (2018)"),
    "6E": (["FX-2"], "average, in USD (reader arithmetic to contracts)"),
    "6A": (["FX-4"], "average, in USD (reader arithmetic to contracts)"),
}

# ---------------------------------------------------------------- S_mean variant (LR-S declared variant)
SMEAN_SPREAD = {
    "MNG": {"value": 2.414, "item": "NATGAS-3", "window": "5 dates 2025-05-14..2026-04-15, day session 08:00-13:30 CT",
            "kind": "time-weighted mean quoted spread (program measurement, E.2a)"},
    "BTC": {"value": 4.72, "item": "CRYPTO-2", "window": "2023-04-17..2023-04-21 (front BTCJ3), session not stated",
            "kind": "average bid-ask spread, 23.60 index points / 5.00 tick (nearest window to the F3 window; the "
                    "2026-01 figure 13.64 ticks, CRYPTO-1, is farther)"},
    "10Y": {"value": 1.67, "item": "RATES-5", "window": "2024 (H1 per E.28), RTH 07:00-16:00 CT",
            "kind": "average top-of-book spread 0.167 bp / 0.1 bp tick"},
}
SMEAN_UNCHANGED_SPREAD_REASON = {
    "ZW": "only a mean pooled over three grains (GRAINS-2), not a ZW figure (for_lead)",
    "ZT": "no ZT mean spread found (RATES-1 is a statement under the pre-2019 tick; RATES-6 is a large-order cost)",
    "ZL": "snippet only (GRAINS-35)",
}
SMEAN_TOUCH = {
    "CL": {"value": 8, "item": "CRUDE-49", "window": "Q1 2023, most active month, US day-session hours",
           "kind": "average top-of-book quantity (hourly averages 7.59-9.12 lots); nearest window (CRUDE-50: 25, 2018)"},
    "HG": {"value": 5.35, "item": "METALS-52", "window": "Q1 2023, most active month, all hours",
           "kind": "average best bid/ask quantity (lots); US-hours hourly averages 6.42-7.07"},
    "ZC": {"value": 375.27, "item": "GRAINS-5", "window": "2015-11-23..2016-03-31, nearby",
           "kind": "mean contracts at the best level per side (bid 377.69, ask 375.27; the smaller side)"},
    "ZW": {"value": 43.92, "item": "GRAINS-6", "window": "2015-11-23..2016-03-31, nearby",
           "kind": "mean contracts at the best level per side (bid 45.26, ask 43.92; the smaller side)"},
    "ZS": {"value": 26.32, "item": "GRAINS-34", "window": "about Jan-Nov 2020, whole day",
           "kind": "average volume at best bid and offer (side convention not stated); nearest window"},
    "ZT": {"value": 99471, "item": "RATES-2", "window": "2018, RTH, front month (pre-2019 ZT tick)",
           "kind": "average book size at best bid/offer"},
    "ZF": {"value": 1319, "item": "RATES-2", "window": "2018, RTH", "kind": "average book size at best bid/offer"},
    "ZN": {"value": 2507, "item": "RATES-2", "window": "2018, RTH", "kind": "average book size at best bid/offer"},
    "ZB": {"value": 377, "item": "RATES-2", "window": "2018, RTH", "kind": "average book size at best bid/offer"},
    "6E": {"value": 23, "item": "FX-2", "window": "June 2021, whole day",
           "kind": "average top-of-book size about USD 3.5m = about 23 contracts (reader arithmetic; 28 if EUR)"},
    "6A": {"value": 15, "item": "FX-4", "window": "three days after 2020-11-23, whole day",
           "kind": "average top-of-book size about USD 1.5m = 15 to 20 contracts (reader arithmetic; lower bound)"},
}

# ---------------------------------------------------------------- settlement off a sibling (Sat ii)
SETTLES_OFF = {
    "MCL": ("CL", ["CRUDE-9"]), "QM": ("CL", ["CRUDE-10"]),
    "QG": ("NG", ["NATGAS-35"]), "MNG": ("NG", ["NATGAS-36"]),
    "MHG": ("HG", ["METALS-8", "METALS-9"]),
    "MZC": ("ZC", ["GRAINS-8"]), "MZS": ("ZS", ["GRAINS-8"]), "MZW": ("ZW", ["GRAINS-8"]),
    "MZL": ("ZL", ["GRAINS-8"]), "MZM": ("ZM", ["GRAINS-8"]),
}
SETTLES_NOT = {  # (basis, item): physically delivered or index/benchmark-settled (brief list)
    "XC": "physical delivery (daily/final settlement derived from ZC)", "XK": "physical delivery",
    "XW": "physical delivery", "MGC": "physical delivery via ACE", "SIL": "physical delivery via ACE",
    "M6E": "physical delivery", "M6A": "physical delivery", "MBT": "final to the CME CF BRR index",
    "MET": "final to the CME CF ETHUSD_RR index", "M2K": "final to the index SOQ", "MYM": "final to the index SOQ",
    "MNQ": "final to the index SOQ", "2YY": "cash to the BrokerTec 15:00 ET benchmark",
    "5YY": "cash to the BrokerTec 15:00 ET benchmark", "10Y": "cash to the BrokerTec 15:00 ET benchmark",
    "30Y": "cash to the BrokerTec 15:00 ET benchmark",
}

# ---------------------------------------------------------------- pauses (PT), from the readers' T7 items
PAUSE_SETS = {
    "grains": [{"start_pt": "05:45", "end_pt": "06:30", "days": "Mon-Fri",
                "what": "pause 07:45-08:30 CT between the overnight and day segments; no orders accepted",
                "item": "GRAINS-14"},
               {"start_pt": "11:20", "end_pt": "17:00", "days": "Mon-Fri",
                "what": "day session closes 13:20 CT; Globex reopens 19:00 CT", "item": "GRAINS-14"}],
    "cme_ct_break": [{"start_pt": "14:00", "end_pt": "15:00", "days": "Sun-Fri",
                      "what": "daily 60-minute break 16:00-17:00 CT", "item": None}],
    "yields_break": [{"start_pt": "14:00", "end_pt": "15:00", "days": "Mon-Thu",
                      "what": "daily maintenance 16:00-17:00 CT", "item": "RATES-50"}],
    "crypto_break": [{"start_pt": "14:00", "end_pt": "15:00", "days": "Sun-Fri",
                      "what": "daily 60-minute break 16:00-17:00 CT (to 2026-05-28; 24/7 with shortened maintenance "
                              "from 2026-05-29, CRYPTO-38)", "item": "CRYPTO-37"}],
}
PAUSE_ITEM_BY_FAMILY = {"crude": "CRUDE-17", "natgas": "NATGAS-47", "metals": "METALS-14", "fx": "FX-47",
                        "equity": "EQUITY-47", "rates": "RATES-49"}

# ---------------------------------------------------------------- cross-family program items
# The International Incentive Program fee table (RATES-11; pages/RATES/cftc_rules01102513618.pdf.txt lines 136-224)
# names these product lines; each code below falls under a named line. Not named: MCL, MNG, MHG, the crypto codes and
# the micro grains.
IIP_CODES = {
    "6E": "Full Size Foreign Exchange - Futures", "6A": "Full Size Foreign Exchange - Futures",
    "M6E": "E-micro Foreign Exchange Contracts", "M6A": "E-micro Foreign Exchange Contracts",
    "NQ": "E-mini Equity Index - Futures", "RTY": "E-mini Equity Index - Futures",
    "MNQ": "Micro E-Mini Equity Index - Futures", "M2K": "Micro E-Mini Equity Index - Futures",
    "MYM": "Micro E-Mini Dow Futures", "YM": "E-mini Dow/DJ U.S. Real Estate (CBOT; read as the E-mini Dow line)",
    "ZC": "Full Size Agricultural Futures Contracts", "ZS": "Full Size Agricultural Futures Contracts",
    "ZW": "Full Size Agricultural Futures Contracts", "ZL": "Full Size Agricultural Futures Contracts",
    "ZM": "Full Size Agricultural Futures Contracts", "XC": "Mini Agricultural Contracts",
    "XK": "Mini Agricultural Contracts", "XW": "Mini Agricultural Contracts",
    "2YY": "Micro Treasury Yield Futures", "5YY": "Micro Treasury Yield Futures",
    "10Y": "Micro Treasury Yield Futures", "30Y": "Micro Treasury Yield Futures",
    "ZT": "U.S. Treasury Futures", "ZF": "U.S. Treasury Futures", "ZN": "U.S. Treasury Futures",
    "ZB": "U.S. Treasury Futures", "NG": "Henry Hub Natural Gas Futures (NG)",
    "CL": "Light Sweet Crude Oil (WTI) Futures (CL)", "QM": "E-mini Crude Oil Futures (QM)",
    "QG": "E-mini Natural Gas Futures (QG)", "GC": "Core Metal (GC, SI, HG)", "SI": "Core Metal (GC, SI, HG)",
    "HG": "Core Metal (GC, SI, HG)", "MGC": "E-micro Gold (MGC)", "SIL": "1,000 oz. Silver (SIL)",
}

# Lead-ruling-free P inputs: E.28's P items (A3_firm_products.json firms.*.P_items, E.28 OC-A3-8), which FirmRules
# found unchanged. native_api = not no_documented_api; oco_api = not no_api_oco_bracket.
VPS = {"topstep": "prohibited", "lucid": "unknown", "tradeify": "prohibited", "mffu": "unknown", "bulenox": "unknown"}
RATE = {"topstep": 3.33, "lucid": "unknown", "tradeify": "unknown", "mffu": "unknown", "bulenox": "unknown"}
# The firm models' DLL (E.28 A3_models): Topstep's DLL is optional (not chosen in the modelled Standard Path), Bulenox
# Option 1 has none. "none" = no daily loss limit (SCHEMA.md section 2).
DLL_NONE = {"topstep": "optional (USD 1,000 only if added at purchase; not a rule violation); the modelled Standard "
                       "Path plan has none (E.28 firm model dll None)",
            "bulenox": "Option 1 (the modelled plan) has none; Option 2 has USD 1,100 soft"}
