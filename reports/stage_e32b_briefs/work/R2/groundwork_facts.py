"""groundwork_facts.py: the DossierWriter's curated phase-1 facts (Stage E.32b, step 3b).

Each entry points to its source: R2 evidence rows by id (FNN.ENN = family FNN, evidence row NN in the order of
briefs/R2_idea_families.json), R1 lines by id (briefs/R1_closed_lines.json), F2 items by id. build_groundwork.py
copies the rows, quotes and closing sentences verbatim from those files, so the text below only selects and
relates them. Facts only: no rating (Q1-Q3 belong to the CombinationScorer) and no outcome of any strategy.
"""
from __future__ import annotations

FAMILIES = ("F01", "F02", "F03", "F04", "F05", "F06", "F07", "F08", "F09", "F10", "F11", "F12")

UNDERLYINGS = {
    "DOW": {"name": "Dow Jones Industrial Average", "codes": ["YM", "MYM"], "leader": "YM", "asset_class": "equity",
            "note": "MYM is YM's micro (1/10 size); MYM's F3 statistics are YM's (OC-1 transfer); MYM settles daily "
                    "from YM (EQUITY-22, -23). The two are one underlying and never pool members together."},
    "NASDAQ": {"name": "Nasdaq-100", "codes": ["MNQ"], "leader": "NQ (excluded, V49)", "asset_class": "equity",
               "note": "MNQ is NQ's satellite: MNQ's F3 statistics are NQ's (OC-1), MNQ settles from NQ's 30-s VWAP "
                       "(EQUITY-22, -23, -24). NQ is excluded as a candidate (V49); NQ-based closed lines bind MNQ "
                       "because the price path is the same (lead's instruction for this run)."},
    "RUSSELL": {"name": "Russell 2000", "codes": ["RTY"], "leader": "RTY", "asset_class": "equity",
                "note": "M2K (micro sibling) is a survivor but not a top-15 code: no M2K combination (LR-R2a)."},
    "SOYOIL": {"name": "Soybean oil (CBOT)", "codes": ["ZL"], "leader": "ZL", "asset_class": "grains",
               "note": "MZL (micro sibling) is a survivor but not a top-15 code: no MZL combination (LR-R2a). ZL is "
                       "a leg of the soybean crush with ZS and ZM (GRAINS-15, -16, -38)."},
}

# Family kind: how K_year is counted (spec 8.2). "daily": one trade a trade date at a fixed clock (252 events a
# year, 1 trade per event); "event": events a year x trades per event; "continuous": n_cap(h_c) x 252.
FAMILY_KIND = {"F01": "daily", "F03": "event", "F04": "event", "F05": "event", "F08": "daily",
               "F09": "continuous", "F10": "continuous", "F11": "continuous", "F12": "event"}

EQUITY_UNDS = ("DOW", "NASDAQ", "RUSSELL")

# ------------------------------------------------------------------------------------------- applicability
# (applies, deciding fact, sources). The deciding fact is the structural precondition the brief names: an event
# family needs the scheduled event, a cross-market family a documented relationship, an order-book family order-book
# data; pattern families (F01, F08, F11) need the session clock the pattern is defined on.
_EQ_NOT = {
    "F02": "R2-F02 lists crude and natgas codes only (WPSR, WNGSR, API inventory releases); no equity-index "
           "inventory release exists (EQUITY-16: no product-specific scheduled release for equity index futures).",
    "F03": "R2-F03 lists grain and oilseed codes only (USDA, NOPA reports).",
    "F06": "R2-F06 lists rates and natgas codes only (pre-FOMC ZN, pre-refunding ZN, Treasury auctions, pre-WNGSR). "
           "The pre-FOMC equity drift is recorded under F05 as evidence against (F05.E06: 'essentially disappeared "
           "after 2015', EQUITY-21).",
    "F07": "R2-F07 lists FX, rates and metals codes only (FX fixes, month-end dollar and Treasury demand, LBMA). "
           "The equity turn of the month is a multi-day line (R1-16 T3), outside the 5-240 minute scope.",
}
APPLIES = {}
for _u in EQUITY_UNDS:
    for _f, _why in _EQ_NOT.items():
        APPLIES[(_u, _f)] = (False, _why, [])
    APPLIES[(_u, "F01")] = (True, "Baltussen et al. 2021 define the effect on the cash-session close (EQUITY-49) and "
                            "report a product row for this underlying (SB-8 YM, SB-9 NQ, SB-10 Russell).",
                            ["EQUITY-49", "SB-8", "SB-9", "SB-10"])
    APPLIES[(_u, "F04")] = (True, "Scheduled US macro releases: NFP, CPI, PPI, GDP 08:30 ET; ISM 10:00 ET (EQUITY-16).",
                            ["EQUITY-16"])
    APPLIES[(_u, "F05")] = (True, "Scheduled FOMC statements 14:00 ET, eight a year (EQUITY-16; R2-F05).",
                            ["EQUITY-16", "EQUITY-20"])
    APPLIES[(_u, "F08")] = (True, "Fixed session clocks: Globex Sun-Fri 18:00-17:00 ET, cash session 09:30-16:00 ET "
                            "(EQUITY-47, EQUITY-49); European open 02:00-03:00 ET documented on the ES cousin "
                            "(EQUITY-50).", ["EQUITY-47", "EQUITY-49", "EQUITY-50"])
    APPLIES[(_u, "F10")] = (True, "Order-book data exist for purchase: Databento GLBX.MDP3 MBO from 2017-05-21, MBP-10 "
                            "before (F2_data_access databento_dataset); the code's MBO start is in the data plan.",
                            ["F2_data_access:databento_dataset"])
    APPLIES[(_u, "F11")] = (True, "R2-F11 applies to any code (own price path on 1-minute bars).", [])
    APPLIES[(_u, "F12")] = (True, "Monthly option expiries (3rd Friday) on the index; R2-F12 lists the equity codes "
                            "(12 monthly expiries a year, 4 quarterly).", [])
APPLIES[("DOW", "F09")] = (False, "EQUITY-14: 'No sourced intraday lead-lag or cointegration study for Dow futures (YM) "
                           "against ES/NQ found ... Mechanical only: MYM-YM pair.' A mechanical mini/micro pair is "
                           "arbitrage-tight (F09.E10).", ["EQUITY-14", "EQUITY-12"])
APPLIES[("NASDAQ", "F09")] = (False, "EQUITY-13: NQ (MNQ's underlying) LEADS ES by about 9-12 min and Russell by about "
                              "8-11 min; no source documents the Nasdaq-100 following another market at minutes, so "
                              "no documented relationship predicts MNQ. MNQ-NQ is a mechanical 10:1 pair (EQUITY-12).",
                              ["EQUITY-13", "EQUITY-12"])
APPLIES[("RUSSELL", "F09")] = (True, "EQUITY-13: NQ leads Russell 2000 futures by about 8-11 min at 60-min chart "
                               "extrema (preprint, 2004-2014, no trading test); RTY is the follower.", ["EQUITY-13"])

APPLIES[("SOYOIL", "F01")] = (True, "Soybean oil (BO) is in Baltussen et al.'s 62-futures sample with its own product "
                              "row (SB-22); the row is null or negative out of sample (F01.E03).", ["SB-22"])
APPLIES[("SOYOIL", "F02")] = (False, "R2-F02 lists crude and natgas codes only; the soybean-oil link to energy policy "
                              "is a daily pointer (EPA RFS announcements, GRAINS-48), not an inventory release.",
                              ["GRAINS-48"])
APPLIES[("SOYOIL", "F03")] = (True, "USDA reports (WASDE, Crop Production, Grain Stocks, Acreage, Prospective "
                              "Plantings) at 11:00 CT inside the day session (GRAINS-22); NOPA monthly crush at noon "
                              "ET = 11:00 CT (E.32 methods brief section 8.1; pre-2026 times unverified).",
                              ["GRAINS-22", "GRAINS-48"])
APPLIES[("SOYOIL", "F04")] = (False, "R2-F04 lists rates, equity, metals, FX, crypto and energy codes; no grain code "
                              "and no sourced macro-release effect on ZL.", [])
APPLIES[("SOYOIL", "F05")] = (False, "R2-F05 lists rates, equity, gold and FX codes; no sourced FOMC effect on ZL.", [])
APPLIES[("SOYOIL", "F06")] = (False, "R2-F06 lists rates and natgas codes only.", [])
APPLIES[("SOYOIL", "F07")] = (False, "R2-F07 lists FX, rates and metals codes only.", [])
APPLIES[("SOYOIL", "F08")] = (True, "Fixed session clocks: Globex 19:00-07:45 CT, pause 07:45-08:30 CT, day 08:30-13:20 "
                              "CT (GRAINS-14, GRAINS-29); R2-F08 lists the grain codes.", ["GRAINS-14", "GRAINS-29"])
APPLIES[("SOYOIL", "F09")] = (True, "Soybean crush: ZS vs ZM and ZL cointegrated intraday on 180 of 243 day sessions "
                              "(2015, 1-minute; GRAINS-15, -16), no fixed leader (GRAINS-38).",
                              ["GRAINS-15", "GRAINS-16", "GRAINS-38"])
APPLIES[("SOYOIL", "F10")] = (True, "Order-book data exist: ZL MBP-1 2020-12..2024-02 owned (E.31 purchase); MBO "
                              "buyable from 2017-05-21 (F2_data_access).", ["F2_data_access:ZL"])
APPLIES[("SOYOIL", "F11")] = (True, "R2-F11 applies to any code.", [])
APPLIES[("SOYOIL", "F12")] = (False, "R2-F12 lists equity and crypto codes only; no sourced option-hedging or expiry "
                              "study on grains or oilseeds.", [])

# ------------------------------------------------------------------------------------------- evidence rows
# (row id, relation of the row's product to this underlying)
_F01_EQ = {
    "DOW": [("F01.E01", "asset-class pool (17 equity index futures, incl. YM)"),
            ("F01.E02", "this underlying: YM product row (SB-8)"),
            ("F01.E04", "all products (cost statement)"),
            ("F01.E05", "other venue, other index (SPY; IWM)"),
            ("F01.E06", "cash index, other index (S&P 500)"),
            ("F01.E10", "cousin (ES)"),
            ("F01.E11", "cash S&P 500 (pointer)"),
            ("F01.E12", "index futures (abstract; DJIA per snippet only, EQUITY-41)"),
            ("F01.E13", "equity, bond and FX futures pool (abstract)"),
            ("F01.E14", "other product (NQ at MNQ cost; program test)"),
            ("F01.E15", "pooled program test incl. YM")],
    "NASDAQ": [("F01.E01", "asset-class pool (17 equity index futures, incl. NQ)"),
               ("F01.E02", "this underlying: NQ product row (SB-9); MNQ is NQ's satellite"),
               ("F01.E04", "all products (cost statement)"),
               ("F01.E05", "other venue, other index (SPY; IWM)"),
               ("F01.E06", "cash index, other index (S&P 500)"),
               ("F01.E10", "cousin (ES)"),
               ("F01.E11", "cash S&P 500 (pointer)"),
               ("F01.E12", "index futures (abstract)"),
               ("F01.E13", "equity, bond and FX futures pool (abstract)"),
               ("F01.E14", "this underlying: NQ price path at MNQ cost (program test)"),
               ("F01.E15", "pooled program test incl. NQ")],
    "RUSSELL": [("F01.E01", "asset-class pool (17 equity index futures, incl. Russell)"),
                ("F01.E02", "this underlying: Russell product row (SB-10; ICE then CME)"),
                ("F01.E04", "all products (cost statement)"),
                ("F01.E05", "other venue, same index (IWM OOS R2 2.43%)"),
                ("F01.E06", "cash index, other index (S&P 500)"),
                ("F01.E10", "cousin (ES)"),
                ("F01.E11", "cash S&P 500 (pointer)"),
                ("F01.E12", "index futures (abstract)"),
                ("F01.E13", "equity, bond and FX futures pool (abstract)"),
                ("F01.E14", "other product (NQ at MNQ cost; program test)"),
                ("F01.E15", "pooled program test incl. RTY")],
}
EVIDENCE = {}
for _u in EQUITY_UNDS:
    EVIDENCE[(_u, "F01")] = _F01_EQ[_u]
    EVIDENCE[(_u, "F04")] = [("F04.E03", "cousin (ES), 30 announcements, full text"),
                             ("F04.E01", "cousin (ES) and ZN, after NFP"),
                             ("F04.E08", "cousin (ES order flow, abstract)")]
    EVIDENCE[(_u, "F05")] = [("F05.E02", "other venue (SPY), FOMC release days"),
                             ("F05.E06", "cash S&P 500 and Treasuries: pre-FOMC drift (before the statement)"),
                             ("F05.E01", "other asset class (cash Treasury yields)")]
    EVIDENCE[(_u, "F08")] = [("F08.E03", "cousin (ES), European open 02:00-03:00 ET"),
                             ("F01.E05", "other venue (SPY): first half-hour predicts the last half-hour (listed "
                                         "under F01; the open-to-close handoff)")]
    EVIDENCE[(_u, "F10")] = [("F10.E01", "other asset class (NYSE stocks)"),
                             ("F10.E02", "equities (abstract)"),
                             ("F10.E06", "cousin (ES): net gamma conditions order-flow reversals"),
                             ("F10.E07", "other product (ZM), program test"),
                             ("F10.E08", "excluded sub-5-minute items (NQ among them)")]
    EVIDENCE[(_u, "F12")] = [("F12.E01", "cousin (ES; V45 exception, untested)"),
                             ("F12.E02", "other venue (US stocks and ETFs)"),
                             ("F12.E03", "cousin (ES)")]
EVIDENCE[("DOW", "F11")] = [("F11.E01", "futures pool (16-24 futures; equity-index membership not recorded)"),
                            ("F11.E09", "other venue (SPY), noise-area momentum"),
                            ("F11.E10", "other underlying (MNQ 5-min, NQ 15-min), preprints")]
EVIDENCE[("NASDAQ", "F11")] = [("F11.E01", "futures pool (16-24 futures; equity-index membership not recorded)"),
                               ("F11.E09", "other venue (SPY), noise-area momentum"),
                               ("F11.E10", "this underlying (MNQ 5-min; NQ 15-min), preprints")]
EVIDENCE[("RUSSELL", "F11")] = [("F11.E01", "futures pool (16-24 futures; equity-index membership not recorded)"),
                                ("F11.E09", "other venue (SPY), noise-area momentum"),
                                ("F11.E10", "other underlying (MNQ 5-min, NQ 15-min), preprints")]
EVIDENCE[("RUSSELL", "F09")] = [("F09.E06", "this underlying (Russell 2000 futures, ICE then) as the follower of NQ"),
                                ("F09.E10", "mechanical pairs (M2K-RTY): arbitrage-tight, no directional edge")]
EVIDENCE[("SOYOIL", "F01")] = [("F01.E01", "asset-class pool (21 commodity futures, incl. BO)"),
                               ("F01.E03", "this product: BO (soybean oil) product row (SB-22), null or negative"),
                               ("F01.E04", "all products (cost statement)"),
                               ("F01.E09", "other venue (DCE soybean and meal; Chinese commodities)"),
                               ("F01.E16", "cousin (CBOT soybean meal)"),
                               ("F01.E15", "pooled program test incl. ZL")]
EVIDENCE[("SOYOIL", "F03")] = [("F03.E01", "cousins (ZS, ZC nearby), WASDE"),
                               ("F03.E02", "cousin (corn nearby)"),
                               ("F03.E03", "cousin (ZS)"),
                               ("F03.E04", "cousin (ZC)"),
                               ("F03.E05", "grain futures (abstract)"),
                               ("F03.E06", "cousin (ZC)"),
                               ("F03.E07", "cousins (ZC, ZS new crop), pointer"),
                               ("F03.E08", "this product (ZL) and ZM, pointer (news)"),
                               ("F03.E09", "this product and the crush siblings (ZM, ZS, ZL)")]
EVIDENCE[("SOYOIL", "F08")] = [("F08.E07", "other venue (DCE soybean, corn)"),
                               ("F08.E08", "cousin (ZC)"),
                               ("F08.E09", "cousin (ZM): overnight plus first half-hour; 08:30 reopen untested"),
                               ("F08.E13", "cousins (CL, NG, ZC, ZS), volatility only")]
EVIDENCE[("SOYOIL", "F09")] = [("F09.E01", "this product as a crush leg (ZS, ZM, ZL)"),
                               ("F09.E02", "this product as an input leg; traded ZM (program test)"),
                               ("F09.E03", "soy complex (abstract)")]
EVIDENCE[("SOYOIL", "F10")] = [("F10.E01", "other asset class (NYSE stocks)"),
                               ("F10.E02", "equities (abstract)"),
                               ("F10.E03", "cousin (ZC), drift-burst reversal"),
                               ("F10.E04", "grain futures (corn, wheat, soybeans; abstract, horizon unknown)"),
                               ("F10.E07", "crush sibling ZM traded, ZL MBP-1 an input (program test)")]
EVIDENCE[("SOYOIL", "F11")] = [("F11.E01", "futures pool (16-24 futures incl. crude and the 10-year)"),
                               ("F11.E05", "other venue (Chinese commodity futures)")]

# ------------------------------------------------------------------------------------------- R1 overlaps
# (line id, relation of the line to this underlying, the configuration it tested, reading under LR-R1)
_CLOSED = "closed configuration (LR-R1: a closed configuration stays closed at every venue, the own broker included)"
_FAM_OTHER = "family closed on another product (family overlap under LR-R1)"
_E33C = "E.33c family closed on ZM; on this product family overlap (LR-R1)"
_UMB = "evidence finding (R1-19), not a ban on new families (LR-R1)"
_STOP = "a stop before any test, not a test (R1 ambiguity list)"
_EXEC = "execution line: passive spread capture closed (V50); limit orders stay allowed as execution of a signal"
_MULTI = "multi-day line, outside the 5-240 minute scope"

R1_OVERLAP = {
    ("DOW", "F01"): [
        ("R1-13", "pooled incl. YM (fallback window 2019-05-06..2024-02-29)",
         "E16-H1 settlement-window intraday momentum and H4 next-day reversal, pooled over 27 roots", _CLOSED),
        ("R1-03", "MYM traded, YM price path",
         "K1-cp1-01 open-to-first-half-hour momentum port (signal bar 08:59 CT; R1's horizons field: \"intraday "
         "holds, flat by the exchange-set F (15:08 CT equity/rates)\"); research window 2025-04-01..2026-06-12", _CLOSED),
        ("R1-14", "other product (NQ)", "H6 rest-of-day to last-half-hour momentum, entry 14:30 CT, 2020-06..2024-02",
         _FAM_OTHER),
        ("R1-11", "MYM tested", "ML route v2 Gate 0 at h60, h120, hF on 1-minute bar features", _CLOSED),
        ("R1-23", "not product-specific", "C2 GEX late-session momentum stopped at its power rule", _STOP)],
    ("DOW", "F04"): [
        ("R1-01", "cousin (MES; outside the 47-code universe)", "MES family E scheduled-macro and calendar windows",
         _FAM_OTHER),
        ("R1-04", "other product (rates)", "K2 ISM pre-drift window", _FAM_OTHER)],
    ("DOW", "F05"): [
        ("R1-04", "other product (rates)", "K2 post-FOMC member (Tier B, no confirmation)", _FAM_OTHER),
        ("R1-07", "other product (MGC)", "K5-fomc-01, E.22 confirmation null", _FAM_OTHER),
        ("R1-01", "cousin (MES)", "MES family E scheduled-macro and calendar windows", _FAM_OTHER)],
    ("DOW", "F08"): [
        ("R1-03", "MYM traded, YM price path",
         "K1-cp3-01 prior-day close-location (entry intent on the 08:30 CT bar; exit by the exchange-set flat F per R1)", _CLOSED),
        ("R1-13", "pooled incl. YM", "E16-H4 next-day reversal of the settlement-window move", _CLOSED),
        ("R1-01", "cousin (MES)", "families A (calendar and clock windows) and D (gaps), incl. overnight and "
         "European-open drift (MES A-H1, A-H3, E-H4)", _FAM_OTHER)],
    ("DOW", "F10"): [
        ("R1-21", "other product (ZM)", "S3 ZM order flow and book state at 5-60 min", _E33C),
        ("R1-20", "execution line (ZM measured)", "passive spread capture at the touch, one lot", _EXEC),
        ("R1-11", "MYM tested", "ML on 1-minute bar features (no book data)", _CLOSED)],
    ("DOW", "F11"): [
        ("R1-03", "MYM traded, YM price path",
         "K1-cp2-01 opening-range breakout (first qualifying bar in [08:45, 15:00) CT; exit by the exchange-set flat F per R1)", _CLOSED),
        ("R1-01", "cousin (MES)", "families B (opening range, breakout), C (reversal, fade), G (price-path "
         "statistics), H (NR4/NR7 ORB)", _FAM_OTHER),
        ("R1-11", "MYM tested", "Gate 0 ML over 64 bar features at h60, h120, hF", _CLOSED),
        ("R1-21", "other product (ZM)", "S4 ZM own price path at 5-60 min", _E33C)],
    ("DOW", "F12"): [
        ("R1-14", "other product (NQ)", "H6 T3: momentum into the close conditioned on negative prior-day GEX",
         _FAM_OTHER),
        ("R1-23", "not product-specific", "C2 GEX late-session momentum stopped at its power rule", _STOP),
        ("R1-19", "cousin (ES; outside the universe)", "V45 lists the ES 3rd-Friday reversal as an exception "
         "(never tested)", _UMB)],
    ("NASDAQ", "F01"): [
        ("R1-14", "same underlying: NQ price path traded at MNQ cost",
         "H6 T1 always, T2 |r_ROD| above its 60-date median, T3 negative prior-day GEX; entry at C-30 (14:30 CT) "
         "to the close; 2020-06-01..2024-02-29", _CLOSED),
        ("R1-13", "pooled incl. NQ (2010-07..2024-02)", "E16-H1 settlement-window momentum and H4 reversal", _CLOSED),
        ("R1-03", "MNQ traded", "K1-cp1-01 open-to-first-half-hour momentum port; exit by the exchange-set flat F per R1", _CLOSED),
        ("R1-15", "same underlying (NQ searched)", "E20S ML, 45 configurations, r_ROD features, extra decision time "
         "t4 = F_X - 60 min, h60/h120/hF", _CLOSED),
        ("R1-18", "same underlying (NQ)", "H6 reversal direction at 5 and 20 days", _MULTI),
        ("R1-11", "MNQ tested", "Gate 0 ML at h60, h120, hF", _CLOSED),
        ("R1-23", "not product-specific", "C2 GEX late-session momentum stopped at its power rule", _STOP)],
    ("NASDAQ", "F04"): [
        ("R1-01", "cousin (MES)", "MES family E scheduled-macro and calendar windows", _FAM_OTHER),
        ("R1-19", "same underlying (NQ in the 17-root census)", "E.20 Part A census of published intraday effects, "
         "macro-release effects included", _UMB)],
    ("NASDAQ", "F05"): [
        ("R1-04", "other product (rates)", "K2 post-FOMC member (Tier B, no confirmation)", _FAM_OTHER),
        ("R1-07", "other product (MGC)", "K5-fomc-01, E.22 confirmation null", _FAM_OTHER),
        ("R1-01", "cousin (MES)", "MES family E scheduled-macro and calendar windows", _FAM_OTHER)],
    ("NASDAQ", "F08"): [
        ("R1-03", "MNQ traded", "K1-cp3-01 prior-day close-location (08:30 CT entry; exit by the exchange-set flat F per R1)", _CLOSED),
        ("R1-13", "pooled incl. NQ", "E16-H4 next-day reversal of the settlement-window move", _CLOSED),
        ("R1-10", "MNQ traded", "K8-wkndbtc-01 weekend bitcoin move to NQ/MNQ (inconclusive by design, not run in "
         "confirmation)", _CLOSED),
        ("R1-01", "cousin (MES)", "families A (clock windows) and D (gaps), incl. European-open drift", _FAM_OTHER)],
    ("NASDAQ", "F10"): [
        ("R1-21", "other product (ZM)", "S3 ZM order flow and book state at 5-60 min", _E33C),
        ("R1-22", "same underlying (NQ dropped)", "NQ dropped for the passive limit-order direction (V49)",
         "product decision for the passive direction; V49's scope for directional use not stated (R1 ambiguity)"),
        ("R1-20", "execution line (ZM measured)", "passive spread capture at the touch, one lot", _EXEC),
        ("R1-11", "MNQ tested", "ML on 1-minute bar features (no book data)", _CLOSED)],
    ("NASDAQ", "F11"): [
        ("R1-03", "MNQ traded", "K1-cp2-01 opening-range breakout, K1-vxnband-01 VXN band fade, K1-vwap-01 VWAP "
         "stop-and-reverse; exit by the exchange-set flat F per R1", _CLOSED),
        ("R1-01", "cousin (MES)", "families B, C, G, H (breakout, reversal and fade, price-path statistics, ORB)",
         _FAM_OTHER),
        ("R1-11", "MNQ tested", "Gate 0 ML over 64 bar features at h60, h120, hF", _CLOSED),
        ("R1-15", "same underlying (NQ searched)", "E20S ML, 36 bar features, h60/h120/hF", _CLOSED),
        ("R1-19", "this product", "the E.25 shortlist named noise-area intraday momentum on MNQ; never tested; V45 "
         "item 3 dropped it on post-publication evidence", _UMB),
        ("R1-21", "other product (ZM)", "S4 ZM own price path at 5-60 min", _E33C)],
    ("NASDAQ", "F12"): [
        ("R1-14", "same underlying: NQ price path at MNQ cost", "H6 T3: momentum into the close conditioned on "
         "negative prior-day GEX (134 trades)", _CLOSED),
        ("R1-23", "not product-specific", "C2 GEX late-session momentum stopped at its power rule", _STOP),
        ("R1-19", "cousin (ES)", "V45 lists the ES 3rd-Friday reversal as an exception (never tested)", _UMB)],
    ("RUSSELL", "F01"): [
        ("R1-13", "pooled incl. RTY (2017-06..2024-02)", "E16-H1 settlement-window momentum and H4 reversal", _CLOSED),
        ("R1-03", "M2K traded, RTY price path", "K1-cp1-01 open-to-first-half-hour momentum port; exit by the exchange-set flat F per R1",
         _CLOSED),
        ("R1-15", "this product (RTY searched)", "E20S ML, r_ROD features, h60/h120/hF", _CLOSED),
        ("R1-14", "other product (NQ)", "H6 rest-of-day to last-half-hour momentum, entry 14:30 CT", _FAM_OTHER),
        ("R1-11", "M2K tested", "Gate 0 ML at h60, h120, hF", _CLOSED),
        ("R1-23", "not product-specific", "C2 GEX late-session momentum stopped at its power rule", _STOP)],
    ("RUSSELL", "F04"): [
        ("R1-01", "cousin (MES)", "MES family E scheduled-macro and calendar windows", _FAM_OTHER),
        ("R1-19", "this product (RTY in the 17-root census)", "E.20 Part A census, macro-release effects included",
         _UMB)],
    ("RUSSELL", "F05"): [
        ("R1-04", "other product (rates)", "K2 post-FOMC member (Tier B, no confirmation)", _FAM_OTHER),
        ("R1-07", "other product (MGC)", "K5-fomc-01, E.22 confirmation null", _FAM_OTHER),
        ("R1-01", "cousin (MES)", "MES family E scheduled-macro and calendar windows", _FAM_OTHER)],
    ("RUSSELL", "F08"): [
        ("R1-03", "M2K traded, RTY price path", "K1-cp3-01 prior-day close-location (08:30 CT entry; exit by the exchange-set flat F per R1)",
         _CLOSED),
        ("R1-13", "pooled incl. RTY", "E16-H4 next-day reversal of the settlement-window move", _CLOSED),
        ("R1-01", "cousin (MES)", "families A (clock windows) and D (gaps), incl. European-open drift", _FAM_OTHER)],
    ("RUSSELL", "F09"): [
        ("R1-10", "other products (MGC with MES leg, 6C with MCL leg, MNQ with MBT leg)", "K8 cross-market screen: "
         "equity flight into gold, oil/CAD, weekend bitcoin to NQ", _FAM_OTHER),
        ("R1-13", "other products (NQ vs ZN)", "E16-H2 month-end NQ vs ZN pair", _FAM_OTHER),
        ("R1-21", "other product (ZM)", "S1 crush residual and S2 cross-asset propagation from ZS and ZL", _E33C)],
    ("RUSSELL", "F10"): [
        ("R1-21", "other product (ZM)", "S3 ZM order flow and book state at 5-60 min", _E33C),
        ("R1-20", "execution line (ZM measured)", "passive spread capture at the touch, one lot", _EXEC),
        ("R1-11", "M2K tested", "ML on 1-minute bar features (no book data)", _CLOSED)],
    ("RUSSELL", "F11"): [
        ("R1-03", "M2K traded, RTY price path", "K1-cp2-01 opening-range breakout; exit by the exchange-set flat F per R1", _CLOSED),
        ("R1-01", "cousin (MES)", "families B, C, G, H", _FAM_OTHER),
        ("R1-11", "M2K tested", "Gate 0 ML over 64 bar features at h60, h120, hF", _CLOSED),
        ("R1-15", "this product (RTY searched)", "E20S ML, 36 bar features, h60/h120/hF", _CLOSED),
        ("R1-21", "other product (ZM)", "S4 ZM own price path at 5-60 min", _E33C)],
    ("RUSSELL", "F12"): [
        ("R1-14", "other product (NQ)", "H6 T3: momentum conditioned on negative prior-day GEX", _FAM_OTHER),
        ("R1-23", "not product-specific", "C2 GEX late-session momentum stopped at its power rule", _STOP),
        ("R1-19", "cousin (ES)", "V45 lists the ES 3rd-Friday reversal as an exception (never tested)", _UMB)],
    ("SOYOIL", "F01"): [
        ("R1-08", "this product (ZL among 7 roots)", "K6-cp1-01 momentum port (decision 12:44 CT; exit by the "
         "exchange-set flat F per R1's horizons field); research window 2025-04-01..2026-06-19", _CLOSED),
        ("R1-13", "pooled incl. ZL (2010-07..2024-02)", "E16-H1 settlement-window momentum and H4 reversal", _CLOSED),
        ("R1-15", "this product (ZL searched)", "E20S ML, r_ROD features, h60/h120/hF", _CLOSED),
        ("R1-14", "other product (NQ)", "H6 rest-of-day to last-half-hour momentum", _FAM_OTHER),
        ("R1-11", "this product (ZL tested)", "Gate 0 ML at h60, h120, hF", _CLOSED)],
    ("SOYOIL", "F03"): [
        ("R1-08", "other products (ZC, ZS)", "K6-wasdepre-01 (ZC, ZS; decision 10:29 CT) and K6-wasdepost-01 (ZC; "
         "decision 11:14 CT); exit by the exchange-set flat F per R1", _FAM_OTHER),
        ("R1-21", "crush sibling (ZM)", "E.33 excluded release windows on ZM; post-USDA dropped as an E.33 family for "
         "power (E.32 verdict table)", _E33C),
        ("R1-23", "direction-level", "V39 closed 'commodity event drift as a standalone stage'; R1 lists its products "
         "as crude, metals, natgas (grains not named)",
         "direction closed by the user without a trial; grains not named (R1 ambiguity)")],
    ("SOYOIL", "F08"): [
        ("R1-08", "this product (ZL among 7 roots)", "K6-cp3-01 prior-day close-location (decision 08:30 CT, the day "
         "reopen; exit by the exchange-set flat F per R1)", _CLOSED),
        ("R1-13", "pooled incl. ZL", "E16-H4 next-day reversal of the settlement-window move", _CLOSED),
        ("R1-01", "cousin family on MES", "families A (clock windows) and D (gaps)", _FAM_OTHER)],
    ("SOYOIL", "F09"): [
        ("R1-21", "this product as an input leg; ZM traded", "S1 crush residual and S2 cross-asset propagation from ZS "
         "and ZL into ZM, 5-60 min, 2020-12-30..2024-02-29", _E33C),
        ("R1-08", "crush siblings (ZS traded, ZM bars as the signal leg)", "K6-crushgap-01", _FAM_OTHER),
        ("R1-20", "this product's MBP-1 read as conditioning data", "E.31 read ZL MBP-1 2020-12..2024-02 (V50 item 4: "
         "not a clean holdout for order-flow tests)", _EXEC)],
    ("SOYOIL", "F10"): [
        ("R1-21", "this product's MBP-1 an input; ZM traded", "S3 ZM order flow and book state at 5-60 min", _E33C),
        ("R1-20", "this product (ZL follow-up closed by decision, skipped)", "passive spread capture at the touch",
         _EXEC),
        ("R1-11", "this product (ZL tested)", "ML on 1-minute bar features (no book data)", _CLOSED)],
    ("SOYOIL", "F11"): [
        ("R1-08", "this product (ZL among 7 roots)", "K6-cp2-01 opening-range breakout (variable 08:45..13:14 CT; exit by the "
         "exchange-set flat F per R1)", _CLOSED),
        ("R1-11", "this product (ZL tested)", "Gate 0 ML over 64 bar features at h60, h120, hF", _CLOSED),
        ("R1-15", "this product (ZL searched)", "E20S ML, 36 bar features, h60/h120/hF", _CLOSED),
        ("R1-21", "crush sibling (ZM)", "S4 ZM own price path at 5-60 min", _E33C),
        ("R1-01", "cousin family on MES", "families B, C, G, H", _FAM_OTHER)],
}

# Other closed lines on the product that are not one of its applicable families (product overlap context).
PRODUCT_OTHER_LINES = {
    "DOW": [("R1-11", "Gate 0 ML (MYM tested)"), ("R1-13", "E16 H1-H5 (YM pooled)")],
    "NASDAQ": [("R1-16", "E21 multi-day trend and turn of month on NQ (multi-day)"),
               ("R1-18", "E23 H6 reversal at 5 and 20 days on NQ (multi-day)"),
               ("R1-12", "C1/C1b: NQ as a feature leg of an NG model"),
               ("R1-22", "NQ dropped (V49)"), ("R1-19", "NQ in the 17-root census")],
    "RUSSELL": [("R1-16", "E21 multi-day trend and turn of month on RTY (multi-day)"),
                ("R1-19", "RTY in the 17-root census")],
    "SOYOIL": [("R1-16", "E21 multi-day trend on ZL (multi-day)"), ("R1-19", "ZL in the 17-root census"),
               ("R1-20", "passive spread capture: ZL follow-up closed by decision (V50)")],
}

# ------------------------------------------------------------------------------------------- timing and events
# Per (underlying, family): documented horizon, timing in PT against the main session, events a year (event and
# daily families), the events' source, trades per event (1 unless the family defines more).
_EQ_MAIN = "main session 06:30-13:00 PT (cash 09:30-16:00 ET, EQUITY-47/-49)"
F04_COUNTS = {"NFP": 57, "CPI": 58, "PPI": 58, "GDP first and last": 38, "ISM services": 57,
              "ISM manufacturing": 58}
F04_WINDOW = ("2019-05-06", "2024-02-29")      # E.20 frozen calendar / EC-K9 counts (macro_calendars.md section 3)
F04_SOURCE = ("reports/stage_e20_briefs/shared/macro_calendars.md section 3 (via EQUITY-16): counts in "
              "2019-05-06..2024-02-29: NFP 57, CPI 58, PPI 58, GDP first and last 38, ISM services 57, ISM "
              "manufacturing 58")
TOPSTEP_T1_COUNTS = {"NFP": 57, "CPI": 58, "PPI": 58, "FOMC": 37}   # same calendar file, same window

TIMING = {}
for _u in EQUITY_UNDS:
    TIMING[(_u, "F01")] = {
        "documented_horizon": "30 min: entry at close-30, exit at the cash close (Baltussen et al.; EQUITY-49)",
        "horizon_minutes": [30],
        "timing_pt": "entry 12:30 PT (14:30 CT), exit 13:00 PT (15:00 CT cash close); " + _EQ_MAIN,
        "inside_main_session": True, "events_per_year": 252, "events_source": "one trade a trade date (spec 9.2: "
        "252 trade dates a year)", "trades_per_event": 1}
    TIMING[(_u, "F04")] = {
        "documented_horizon": "entry 5-10 min after the release, exit 30-60 min (R2-F04); ES continuing adjustment "
                              "t+10 to t+30 min (EQUITY-17)",
        "horizon_minutes": [20, 30, 60],
        "timing_pt": "08:30 ET releases (NFP, CPI, PPI, GDP) = 05:30 PT, BEFORE the main session (Globex pre-open); "
                     "10:00 ET releases (ISM) = 07:00 PT, inside; 09:15 ET (IP) = 06:15 PT, before (not counted: no "
                     "calendar file); " + _EQ_MAIN,
        "inside_main_session": "partly (ISM only)", "events_per_year": None, "events_source": F04_SOURCE,
        "trades_per_event": 1}
    TIMING[(_u, "F05")] = {
        "documented_horizon": "after the 14:00 ET statement to the close: FOMC-day last half-hour (15:30-16:00 ET), "
                              "75+ min after the statement (EQUITY-20); Treasury yields about 3 h (RATES-23)",
        "horizon_minutes": [30, 120],
        "timing_pt": "statement 11:00 PT (14:00 ET), press conference 11:30 PT; last half-hour 12:30-13:00 PT; "
                     + _EQ_MAIN,
        "inside_main_session": True, "events_per_year": 8, "events_source": "eight scheduled FOMC meetings a year "
        "(R2-F05 mechanism; frozen calendar 37 statements in 2019-05-06..2024-02-29, macro_calendars.md section 3)",
        "trades_per_event": 1}
    TIMING[(_u, "F08")] = {
        "documented_horizon": "European open 02:00-03:00 ET, 60 min (EQUITY-50); the cash-open first half-hour as "
                              "the predictor of the close (F01.E05)",
        "horizon_minutes": [30, 60],
        "timing_pt": "European open 23:00-00:00 PT (prior evening, Globex, outside the main session); cash open "
                     "06:30 PT; " + _EQ_MAIN,
        "inside_main_session": "partly", "events_per_year": 252, "events_source": "one trade a trade date",
        "trades_per_event": 1}
    TIMING[(_u, "F10")] = {
        "documented_horizon": "5-30 min forward (R2-F10); forward predictability insignificant by 5-30 min "
                              "(F10.E01)", "horizon_minutes": [5, 15, 30],
        "timing_pt": "any time in the main session; " + _EQ_MAIN, "inside_main_session": True,
        "events_per_year": None, "events_source": "continuous: n_cap(h_c) a day", "trades_per_event": None}
    TIMING[(_u, "F11")] = {
        "documented_horizon": "reversion 2-16 min; weak trend at 1 h or more (F11.E01)", "horizon_minutes": [5, 15, 60],
        "timing_pt": "any time in the main session; " + _EQ_MAIN, "inside_main_session": True,
        "events_per_year": None, "events_source": "continuous: n_cap(h_c) a day", "trades_per_event": None}
    TIMING[(_u, "F12")] = {
        "documented_horizon": "expiry day into the close; 10-60 min conditioned on gamma (R2-F12)",
        "horizon_minutes": [10, 30, 60],
        "timing_pt": "3rd Friday of each month, into the 13:00 PT close; " + _EQ_MAIN, "inside_main_session": True,
        "events_per_year": 12, "events_source": "12 monthly expiries a year, 4 quarterly (R2-F12 data needs)",
        "trades_per_event": 1}
TIMING[("RUSSELL", "F09")] = {
    "documented_horizon": "NQ leads Russell by about 8-11 min at 60-min chart extrema (EQUITY-13); no trading test",
    "horizon_minutes": [10, 60], "timing_pt": "any time in the main session; " + _EQ_MAIN,
    "inside_main_session": True, "events_per_year": None, "events_source": "continuous: n_cap(h_c) a day",
    "trades_per_event": None}
_ZL_MAIN = "main session 06:30-11:20 PT (day 08:30-13:20 CT, GRAINS-14); pause 07:45-08:30 CT = 05:45-06:30 PT"
TIMING[("SOYOIL", "F01")] = {
    "documented_horizon": "30 min: entry at close-30, exit at the class close (Baltussen et al.)",
    "horizon_minutes": [30],
    "timing_pt": "entry 10:50 PT (12:50 CT), exit 11:20 PT (13:20 CT day close); " + _ZL_MAIN,
    "inside_main_session": True, "events_per_year": 252, "events_source": "one trade a trade date",
    "trades_per_event": 1}
TIMING[("SOYOIL", "F03")] = {
    "documented_horizon": "entry 5-15 min after 11:00 CT, exit at 30-60 min or at the 13:20 CT close (R2-F03); "
                          "soybeans: not significant at 10 min, significant at 30, growing to the close (GRAINS-18)",
    "horizon_minutes": [30, 60, 140],
    "timing_pt": "release 09:00 PT (11:00 CT; NOPA noon ET = 11:00 CT); 140 min before the 11:20 PT close; "
                 + _ZL_MAIN,
    "inside_main_session": True, "events_per_year": 27,
    "events_source": "15 major 11:00 CT USDA days a year (E.32 R4_events.md line 235, cited in the E.32 methods "
                     "brief lines 8201 and 8304) + 12 NOPA releases a year (monthly; methods brief section 8.2: 39 "
                     "in 39 months); overlapping days not netted, holiday shifts not counted",
    "trades_per_event": 1}
TIMING[("SOYOIL", "F08")] = {
    "documented_horizon": "first half-hour after the 08:30 CT reopen (planner family 4, untested; F08.E09); "
                          "overnight-to-day blocks of hours", "horizon_minutes": [30],
    "timing_pt": "reopen 06:30 PT (08:30 CT) after the 05:45-06:30 PT pause; Export Sales 07:30 CT = 05:30 PT lands "
                 "before the pause (GRAINS-22); " + _ZL_MAIN,
    "inside_main_session": True, "events_per_year": 252, "events_source": "one trade a trade date",
    "trades_per_event": 1}
TIMING[("SOYOIL", "F09")] = {
    "documented_horizon": "15-240 min for crush residual reversion (planner family 1); no published half-life "
                          "(GRAINS-15)", "horizon_minutes": [15, 240],
    "timing_pt": "any time in the day session; " + _ZL_MAIN, "inside_main_session": True,
    "events_per_year": None, "events_source": "continuous: n_cap(h_c) a day", "trades_per_event": None}
TIMING[("SOYOIL", "F10")] = dict(TIMING[("DOW", "F10")], timing_pt="any time in the day session; " + _ZL_MAIN)
TIMING[("SOYOIL", "F11")] = dict(TIMING[("DOW", "F11")], timing_pt="any time in the day session; " + _ZL_MAIN)

# ------------------------------------------------------------------------------------------- data
# Schema per family; extras that are not Databento GLBX futures data are listed with unknown cost.
SCHEMA = {"F01": "ohlcv-1m", "F03": "ohlcv-1m", "F04": "ohlcv-1m", "F05": "ohlcv-1m", "F08": "ohlcv-1m",
          "F09": "ohlcv-1m (all legs, synchronised)", "F10": "mbo", "F11": "ohlcv-1m", "F12": "ohlcv-1m"}
EXTRAS = {
    "F03": ["dated USDA and NOPA release calendars (NOPA pre-2026 release times unverified, E.32 methods brief 8.1)"],
    "F04": ["release calendar (E.20 frozen calendar covers 2019-05..2024-02 only; no 2010-2019 file for NFP, CPI, "
            "PPI, GDP, ISM: macro_calendars.md section 3); consensus forecasts only for a surprise-signed variant "
            "(vendor data, not owned, cost unknown)"],
    "F05": ["FOMC statement dates and times (calendar files 2010-2024 exist: macro_calendars.md section 3)"],
    "F09": ["leader leg bars: NQ ohlcv-1m for RTY (owned 2010-06..2024-02)", "crush legs: ZS and ZM bars for ZL"],
    "F10": ["MBP-10 is the highest granularity before 2017-05-21 (F2_data_access databento_dataset)"],
    "F12": ["option open interest by strike for a gamma-conditioned variant (GEX; vendor data, cost unknown; R1-14 "
            "used GEX rows 2020-05-29..2024-02-28); the 3rd-Friday variant needs bars and the expiry calendar only"],
}
# Book data source per code for F10: the product's own book unless noted.
BOOK_SOURCE = {"YM": "YM", "MYM": "YM", "MNQ": "MNQ", "RTY": "RTY", "ZL": "ZL"}
BOOK_SOURCE_NOTE = {"MYM": "MYM's F10 signal is priced on YM's book (the full-size leader of the same underlying; "
                           "MYM's own MBO starts 2019-05-06 and its own k is USD 9.65/month); an assumption",
                    "MNQ": "priced on MNQ's own MBO; NQ's book (census k USD 22.88/month) would be cheaper but NQ is "
                           "excluded (V49: 'NQ is not used as a pilot or comparison contract')"}

# ------------------------------------------------------------------------------------------- pools
POOLS = [
    {"name": "EQ3", "members": ["YM", "MNQ", "RTY"],
     "mechanism": "one index-level mechanism on three distinct underlyings (Dow, Nasdaq-100, Russell 2000): the same "
                  "cash close (F01), release times (F04, F05), session clocks (F08), expiry calendar (F12), and the "
                  "generic book (F10) and price-path (F11) families"},
    {"name": "EQ3m", "members": ["MYM", "MNQ", "RTY"],
     "mechanism": "as EQ3 with the micro Dow (MYM) in place of YM; YM and MYM are one underlying and never pool "
                  "together (pooling one price path twice would overstate K_eff)"},
]
POOLS_NOT_BUILT = [
    {"candidate": "YM + MYM", "reason": "one underlying (MYM settles from YM): not a pool"},
    {"candidate": "EQ3 or EQ3m at bulenox (YM, RTY) and lucid (YM, MNQ)", "reason": "a pool at a venue needs every "
     "member there with an F5 band; bulenox|MNQ, lucid|RTY (and every non-mffu MYM pair) are not top-15 pairs, so "
     "F5 has no band for them (LR-R2a, LR-R2b). Two-member sub-pools were not built (a pool is its member set)."},
    {"candidate": "ZL with the equity codes", "reason": "different asset class; the families ZL shares with them "
     "(F01, F08, F10, F11) are generic, and F01 is null on ZL (F01.E03)"},
    {"candidate": "ZL with ZS and ZM (soy crush, F09)", "reason": "ZS and ZM are not top-15 codes (LR-R2a: pools only "
     "among the top-15 codes)"},
    {"candidate": "F09 equity pool", "reason": "F09 applies only to RTY among the equity codes (EQUITY-13, -14)"},
]
E29_MEASURED = ("E.29 section 3.2 measured daily-return correlations only for CL-ZM, CL-GC, CL-NQ, ZM-GC, ZM-NQ, GC-NQ "
                "(2022-11-01..2023-10-31): none pairs two pool members, so r3_score uses its rule (0.5 within an "
                "asset class). E.29 also says the P&L correlation of direction-neutral one-minute trading follows "
                "shared volatility days (range correlations up to 0.40) more than price direction.")

# ------------------------------------------------------------------------------------------- cross-family facts
CROSS_FACTS = [
    "LR-R1: V38 closes the tested configurations of the 528 bar-based trials (R1-01..R1-18) on the 17 roots; its "
    "umbrella sentence with V45 item 4 is an evidence finding (R1-19), not a ban on new families. A closed "
    "configuration stays closed at every venue, the own broker included. The ZM 5-60 minute families of E.33c (V56) "
    "are closed on ZM and are family overlap on other products. NQ is excluded (V49); passive spread capture is "
    "closed (V50).",
    "Retail size (one contract, tens of milliseconds to a second, no co-location): information is priced within 1 to 5 "
    "seconds on ES, NQ, ZN and CL (E.25, C3 draft:70-71), so only effects that last minutes or longer are reachable; "
    "a one-lot moves no price.",
    "E.32 front: no commodity-futures study shows positive out-of-sample predictability net of costs at 1-240 "
    "minutes; event and once-a-day families fail on power over 39 months (E.32 methods brief:15-16).",
    "E.28 C3: on 1-minute bars the robust MES patterns were worth about 0.1 tick against a 2.1-tick round turn.",
    "E.33c (cost and trade-count facts only): minimum detectable edges 1.5 to 4.4 ticks a trade at the trade rates "
    "seen; the 61 G1 configurations lost more than 1.0 tick a trade after costs; at every firm's fee the median "
    "configuration loses 2.2 to 2.6 ticks a trade (ZM, 796 dates).",
    "E.31 (measured): a resting one-lot limit at the ZM touch under the trade-through rule has a gross 10 s markout "
    "of -0.970 ticks per fill [-0.988, -0.950] (model c, front month, DAY session); models (a) K-algorithm -0.287 and "
    "(b) FIFO -0.252 decide nothing.",
    "E.29 section 1 and 3.4: a one-lot micro rarely clears the USD 150 winning-day payout threshold (MGC); "
    "correlation barely mattered in the basket model.",
]
