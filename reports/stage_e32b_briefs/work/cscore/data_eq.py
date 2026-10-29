"""Q1-Q3 ratings for the single-product equity dossiers (YM, MYM, MNQ, RTY).

CombinationScorer-OpusXHigh, Stage E.32b step 3b. Source read: briefs/R2_dossiers_for_rating.md only.
Each dossier: ids with band and shortest member, then (value, reason) for Q1, Q2, Q3; optional per-id overrides.
"""


def id_range(first, last, band, shortest):
    lo, hi = int(first[1:]), int(last[1:])
    return [(f"C{n:03d}", band, shortest) for n in range(lo, hi + 1)]


# ---------------------------------------------------------------- shared reasons
F01_Q1_YM = ("Identified non-informational hedging flow into the close (short-gamma and leveraged-ETF rebalancing, "
             "mechanism quote); the YM row F01.E02 runs to 2020-05, mostly pre-2015, and post-2015 evidence is cousin, "
             "conditional or flat (F01.E10, F01.E11, F01.E14), so 3 not 4.")
F01_Q2_YM = ("F01.E02 (full text): peer-reviewed recursive out-of-sample R2 2.18% on the YM row at 30 min, but gross "
             "(F01.E04: no costs considered), so 3 not 4; pooled program test incl. YM net negative (F01.E15).")
F01_Q3_YM = ("Close variant, not a re-test: R1-13 E16-H1 settlement-window momentum was closed pooled over 27 roots incl. "
             "YM; R1-03 K1-cp1-01 (MYM traded, YM path) is a first-half-hour momentum port whose decision time the "
             "dossier does not state; the documented C-30-to-close configuration was run singly only on NQ (R1-14).")

F04_Q1 = ("Plausible slow-digestion story without an identified participant; the only drift evidence at the band is a "
          "weak joint test on ES 2008-2014 (F04.E03), while F04.E01 puts most permanent change within minutes and "
          "F04.E08 (abstract) within 1 s.")
F04_Q2 = ("Best evidence is peer-reviewed in sample on a cousin (F04.E03, ES, full text) plus a regulator paper on ES "
          "and ZN (F04.E01); nothing on this underlying: other-product evidence.")

F05_Q1 = ("Slow policy-path repricing is documented only in cash Treasuries (F05.E01, about 3 h, to 2024) and as "
          "FOMC-day close momentum on SPY 1993-2013 (F05.E02); no post-statement drift on equity-index futures at the "
          "band; F05.E06 is the pre-FOMC drift, gone after 2015.")
F05_Q2 = ("Peer-reviewed in sample on another venue (F05.E02, SPY) and a central-bank working paper on another asset "
          "class (F05.E01); nothing on this underlying.")
F05_Q3 = ("Family overlap only: R1-04 K2 post-FOMC (rates), R1-07 K5-fomc-01 (MGC, confirmation null) and R1-01 MES "
          "family E; no FOMC configuration closed on this underlying.")

F08_Q1_15 = ("Identified carry-over of prior-US-close imbalances into the European open on the ES cousin (F08.E03, "
             "1998-2020, gross Sharpe 1.1, -0.5 after spreads), documented at 60 min outside the 15-30 band and outside "
             "the main session; the cash-open handoff has only F01.E05 (SPY, to 2013).")
F08_Q1_30 = ("Identified carry-over of prior-US-close imbalances into the European open on the ES cousin (F08.E03, "
             "1998-2020, gross Sharpe 1.1, -0.5 after spreads), documented at 60 min, inside the band but outside the "
             "main session; the cash-open handoff has only F01.E05 (SPY, to 2013).")
F08_Q2 = ("Peer-reviewed in sample on a cousin (F08.E03, ES, full text; negative after spreads) and other-venue SPY "
          "(F01.E05); nothing on this underlying.")

F10_Q1_15 = ("Plausible participant story (worked orders, refill) but forward order-flow predictability decays to "
             "insignificance by 5-30 min (F10.E01, NYSE 1996) and lasts seconds in F10.E02 (abstract); the only 10-60 min "
             "support is gamma-conditioned reversal on ES (F10.E06, working paper).")
F10_Q1_30 = ("Plausible participant story but the shortest member 30 lies at the end of the documented decay to "
             "insignificance (F10.E01, NYSE 1996; F10.E02 seconds, abstract); only gamma-conditioned reversal on ES "
             "reaches 60 min (F10.E06, working paper).")
F10_Q2 = ("Cousin working paper in sample, gross (F10.E06, ES) and other-asset-class peer-reviewed evidence that decays "
          "(F10.E01); ZM program test net negative (F10.E07); nothing on this underlying.")

F11_Q1 = ("Generic price-path autocorrelation with no identified flow or clock; F11.E01 documents reversion at 2-16 min "
          "and weak trend at >= 1 h with OOS R2 under 1 bp; F11.E09 dropped post-publication; F11.E10 OHLCV families "
          "fail OOS net on MNQ and NQ.")
F11_Q2 = ("Peer-reviewed OOS on a cross-asset futures pool, gross and tiny, equity membership unrecorded (F11.E01, full "
          "text); SPY practitioner WP dropped (F11.E09); cousin preprints negative (F11.E10); nothing on this "
          "underlying.")

F12_Q1 = ("Identified non-informational flow at fixed dates (dealer delta and gamma hedging, LETF rebalancing); evidence "
          "on the ES cousin (F12.E01 3rd-Friday reversal 2003-2021, 2015-23 not significant alone; F12.E03 high-gamma "
          "reversal 2018-24) and stocks/ETFs (F12.E02), not on this underlying.")
F12_Q2 = ("Working papers in sample and gross on a cousin (F12.E01, F12.E03, ES) and another venue (F12.E02, stocks and "
          "ETFs, full text); nothing on this underlying.")
F12_Q3_FAM = ("Family overlap only: R1-14 H6 T3 GEX-conditioned close momentum closed on NQ; R1-23 C2 is a stop before "
              "any test and R1-19 an evidence finding (LR-R1).")

DOSSIERS_EQ = [
    # ------------------------------------------------------------------ YM
    {"dossier": "YM|F01", "ids": id_range("C001", "C006", "15, 30", 15),
     "Q1": (3, F01_Q1_YM), "Q2": (3, F01_Q2_YM), "Q3": (1, F01_Q3_YM)},
    {"dossier": "YM|F04", "ids": id_range("C007", "C012", "15, 30", 15),
     "Q1": (2, F04_Q1), "Q2": (2, F04_Q2),
     "Q3": (2, "Family overlap only: R1-01 MES family E scheduled-macro windows (cousin) and R1-04 K2 ISM pre-drift "
               "(rates); no macro-release configuration closed on YM or MYM.")},
    {"dossier": "YM|F05", "ids": id_range("C013", "C018", "15, 30", 15),
     "Q1": (2, F05_Q1), "Q2": (2, F05_Q2), "Q3": (2, F05_Q3)},
    {"dossier": "YM|F08", "ids": id_range("C019", "C024", "15, 30", 15),
     "Q1": (3, F08_Q1_15), "Q2": (2, F08_Q2),
     "Q3": (1, "Same family and underlying: R1-03 K1-cp3-01 prior-day close-location (MYM traded, 08:30 CT entry to "
               "flat) and R1-13 E16-H4 next-day reversal (pooled incl. YM, intraday) are closed; a 15-30 min hold of the "
               "same handoff signals is a close variant; R1-01 MES family overlap.")},
    {"dossier": "YM|F10", "ids": id_range("C025", "C030", "15, 30", 15),
     "Q1": (2, F10_Q1_15), "Q2": (2, F10_Q2),
     "Q3": (2, "Family overlap only: R1-21 S3 order flow and book state closed on ZM; R1-11 MYM Gate 0 used bar "
               "features without book data (other family); R1-20 is an execution line.")},
    {"dossier": "YM|F11", "ids": id_range("C031", "C036", "15, 30", 15),
     "Q1": (1, F11_Q1), "Q2": (2, F11_Q2),
     "Q3": (1, "Same family and underlying at a neighbouring horizon: R1-11 MYM Gate 0 ML over 64 bar features at h60 "
               "and R1-03 K1-cp2-01 ORB (MYM traded) are closed; R1-01 MES and R1-21 ZM family overlap.")},
    {"dossier": "YM|F12", "ids": id_range("C037", "C042", "15, 30", 15),
     "Q1": (3, F12_Q1), "Q2": (2, F12_Q2), "Q3": (2, F12_Q3_FAM)},
    # ------------------------------------------------------------------ MYM
    {"dossier": "MYM|F01", "ids": [("C043", "30, 60", 30), ("C044", "30, 60, 120", 30)],
     "Q1": (3, "As YM|F01 (same underlying): identified hedging flow into the close; YM row F01.E02 mostly pre-2015, "
               "post-2015 evidence cousin, conditional or flat (F01.E10, F01.E11, F01.E14); shortest member 30 = the "
               "documented horizon."),
     "Q2": (3, "As YM|F01: F01.E02 (full text) peer-reviewed recursive OOS on the YM row at 30 min, a band member, "
               "gross (F01.E04), so 3 not 4."),
     "Q3": (1, "Close variant: R1-13 E16-H1 pooled incl. YM; R1-03 K1-cp1-01 on MYM itself (first-half-hour momentum "
               "port, decision time not stated); R1-11 MYM Gate 0 at h60/h120 used generic bar features (other "
               "family); no single-product run of the documented configuration.")},
    {"dossier": "MYM|F04", "ids": [("C045", "30, 60", 30), ("C046", "30, 60, 120", 30)],
     "Q1": (2, "As YM|F04; the shortest member 30 sits at the end of the weak t+10..t+30 ES window (F04.E03); fast "
               "absorption per F04.E01 and F04.E08 (abstract)."),
     "Q2": (2, F04_Q2),
     "Q3": (2, "Family overlap only: R1-01 MES family E (cousin) and R1-04 K2 ISM pre-drift (rates); no macro-release "
               "configuration closed on MYM or YM.")},
    {"dossier": "MYM|F05", "ids": [("C047", "30, 60", 30), ("C048", "30, 60, 120", 30)],
     "Q1": (2, F05_Q1), "Q2": (2, F05_Q2), "Q3": (2, F05_Q3)},
    {"dossier": "MYM|F08", "ids": [("C049", "30, 60", 30), ("C050", "30, 60, 120", 30)],
     "Q1": (3, F08_Q1_30), "Q2": (2, F08_Q2),
     "Q3": (1, "Same family and product: R1-03 K1-cp3-01 prior-day close-location on MYM (08:30 CT entry to flat) and "
               "R1-13 E16-H4 (pooled incl. YM) are closed; a 30-120 min hold of the same signal is a shorter-hold close "
               "variant; R1-01 MES family overlap.")},
    {"dossier": "MYM|F10", "ids": [("C051", "30, 60", 30), ("C052", "30, 60, 120", 30)],
     "Q1": (2, F10_Q1_30), "Q2": (2, F10_Q2),
     "Q3": (2, "Family overlap only: R1-21 S3 closed on ZM; R1-11 MYM Gate 0 at h60/h120 used bar features without "
               "book data (other family); R1-20 is an execution line.")},
    {"dossier": "MYM|F11", "ids": [("C053", "30, 60", 30), ("C054", "30, 60, 120", 30)],
     "Q1": (1, "As YM|F11: generic pattern with no identified flow or clock; the 30-120 band is nearer F11.E01's weak "
               ">= 1 h trend but OOS R2 is under 1 bp; F11.E10 cousin OOS fails net."),
     "Q2": (2, F11_Q2),
     "Q3": (1, "Close variant: R1-11 MYM Gate 0 ML over 64 bar features tested this product at h60, a band member, "
               "with a superset feature space; R1-03 K1-cp2-01 ORB on MYM; an own-price-path rule is narrower than the "
               "closed ML configuration."),
     "override": {"C054": {"Q3": (1, "Close variant: R1-11 MYM Gate 0 ML over 64 bar features tested this product at "
                                     "h60 and h120, both band members, with a superset feature space; R1-03 K1-cp2-01 "
                                     "ORB on MYM; an own-price-path rule is narrower than the closed ML configuration.")}}},
    {"dossier": "MYM|F12", "ids": [("C055", "30, 60", 30), ("C056", "30, 60, 120", 30)],
     "Q1": (3, F12_Q1), "Q2": (2, F12_Q2), "Q3": (2, F12_Q3_FAM)},
    # ------------------------------------------------------------------ MNQ
    {"dossier": "MNQ|F01", "ids": id_range("C057", "C061", "15, 30", 15),
     "Q1": (3, "Identified hedging flow into the close (mechanism quote); NQ row OOS R2 3.76% to 2020-05 (F01.E02); "
               "the post-2015 test on the NQ path shows gross 1.25 ticks only (F01.E14) and cousin evidence is "
               "conditional or flat (F01.E10, F01.E11)."),
     "Q2": (3, "F01.E02 (full text): peer-reviewed recursive OOS on the NQ row (MNQ's price path) at 30 min, gross "
               "(F01.E04), so 3 not 4; the registered net test on this path is negative (F01.E14)."),
     "Q3": (0, "Re-tests R1-14 (E.20 H6 rest-of-day to last-half-hour momentum on the NQ price path at MNQ cost, entry "
               "14:30 CT to the close, 2020-06..2024-02, closed V38): the 30-min member is H6 T1; R1-03 K1-cp1-01 on "
               "MNQ and R1-15 r_ROD ML on NQ are also closed.")},
    {"dossier": "MNQ|F04", "ids": id_range("C062", "C066", "15, 30", 15),
     "Q1": (2, F04_Q1), "Q2": (2, F04_Q2),
     "Q3": (2, "Family overlap only: R1-01 MES family E (cousin); R1-19 lists NQ in the census as an evidence finding, "
               "not a ban (LR-R1).")},
    {"dossier": "MNQ|F05", "ids": id_range("C067", "C071", "15, 30", 15),
     "Q1": (2, F05_Q1), "Q2": (2, F05_Q2), "Q3": (2, F05_Q3)},
    {"dossier": "MNQ|F08", "ids": id_range("C072", "C076", "15, 30", 15),
     "Q1": (3, F08_Q1_15), "Q2": (2, F08_Q2),
     "Q3": (1, "Same family and underlying: R1-03 K1-cp3-01 prior-day close-location (MNQ traded, 08:30 CT to flat), "
               "R1-13 E16-H4 (pooled incl. NQ) and R1-10 K8-wkndbtc-01 (MNQ) are closed; a 15-30 min hold of these "
               "handoff signals is a close variant; R1-01 MES family overlap.")},
    {"dossier": "MNQ|F10", "ids": id_range("C077", "C081", "15, 30", 15),
     "Q1": (2, F10_Q1_15), "Q2": (2, F10_Q2),
     "Q3": (2, "Family overlap only: R1-21 S3 closed on ZM; R1-11 MNQ Gate 0 used bar features without book data; "
               "R1-22 drops NQ for the passive direction with directional scope unstated; R1-20 is an execution line.")},
    {"dossier": "MNQ|F11", "ids": id_range("C082", "C086", "15, 30", 15),
     "Q1": (1, "Generic price-path pattern with no identified flow or clock (F11.E01 OOS R2 under 1 bp at 2-16 min and "
               ">= 1 h); on this underlying F11.E10 finds no OHLCV family passing OOS net on MNQ 5-min and no direction "
               "on NQ 15-min; near 0, but not a full-text contradiction at 15-30 min."),
     "Q2": (0, "Negative evidence on this underlying: F11.E10 (reused / full text) walk-forward OOS net on MNQ 5-min "
               "(none of 14 families passes) and NQ 15-min; the only support is the cross-asset pool at other horizons "
               "(F11.E01); the 0 rests on full-text and reused rows, not abstracts."),
     "Q3": (1, "Same family and underlying at a neighbouring horizon: R1-11 MNQ Gate 0 (64 bar features) and R1-15 NQ "
               "E20S (36 bar features) at h60, and R1-03 K1 ORB, VXN band fade and VWAP stop-and-reverse on MNQ are "
               "closed; R1-19 noise-area momentum is an evidence finding.")},
    {"dossier": "MNQ|F12", "ids": id_range("C087", "C091", "15, 30", 15),
     "Q1": (3, F12_Q1), "Q2": (2, F12_Q2),
     "Q3": (1, "Close variant: R1-14 H6 T3 (GEX-conditioned momentum into the close on the NQ path, 134 trades) is "
               "closed at the band's 30 min; the 3rd-Friday restriction and the high-gamma reversal side are untested, "
               "but negative-GEX close momentum on all days would re-test R1-14.")},
    # ------------------------------------------------------------------ RTY
    {"dossier": "RTY|F01", "ids": id_range("C092", "C096", "15, 30", 15),
     "Q1": (3, "Identified hedging flow into the close (mechanism quote); Russell row OOS R2 3.15% to 2020-05 (F01.E02) "
               "and IWM OOS R2 2.43% 2000-2013 (F01.E05); post-2015 evidence is cousin, conditional or flat (F01.E10, "
               "F01.E11, F01.E14)."),
     "Q2": (3, "F01.E02 (full text): peer-reviewed recursive OOS on the Russell row at 30 min, gross (F01.E04), so 3 "
               "not 4; same-index ETF OOS (F01.E05); pooled program test incl. RTY net negative (F01.E15)."),
     "Q3": (1, "Close variant: R1-13 E16-H1 pooled incl. RTY, R1-15 E20S r_ROD ML on RTY at t4 = F-60 / h60 "
               "(neighbouring horizon) and R1-03 K1-cp1-01 on M2K (RTY path, decision time not stated) are closed; the "
               "documented C-30 configuration was never run singly on RTY.")},
    {"dossier": "RTY|F04", "ids": id_range("C097", "C101", "15, 30", 15),
     "Q1": (2, F04_Q1), "Q2": (2, F04_Q2),
     "Q3": (2, "Family overlap only: R1-01 MES family E (cousin); R1-19 lists RTY in the census as an evidence finding, "
               "not a ban (LR-R1).")},
    {"dossier": "RTY|F05", "ids": id_range("C102", "C106", "15, 30", 15),
     "Q1": (2, F05_Q1), "Q2": (2, F05_Q2), "Q3": (2, F05_Q3)},
    {"dossier": "RTY|F08", "ids": id_range("C107", "C111", "15, 30", 15),
     "Q1": (3, F08_Q1_15), "Q2": (2, F08_Q2),
     "Q3": (1, "Same family and underlying: R1-03 K1-cp3-01 prior-day close-location (M2K traded, RTY path, 08:30 CT "
               "to flat) and R1-13 E16-H4 (pooled incl. RTY) are closed; a 15-30 min hold of the same signals is a close "
               "variant; R1-01 MES family overlap.")},
    {"dossier": "RTY|F09", "ids": id_range("C112", "C116", "15, 30", 15),
     "Q1": (2, "Plausible slow diffusion from the deeper market; the only evidence is a preprint on 60-min chart extrema "
               "2004-2014 with no trading test (F09.E06: NQ leads Russell by 8-11 min); E.25 prices information within "
               "seconds on NQ; M2K-RTY is arbitrage-tight (F09.E10)."),
     "Q2": (2, "Preprint in sample on this underlying (F09.E06, Russell futures on ICE, full text), not peer-reviewed "
               "and not a trading test, so below 3: other-venue evidence."),
     "Q3": (2, "Family overlap only: R1-10 K8 cross-market (MGC, 6C, MNQ legs), R1-13 E16-H2 NQ vs ZN pair and R1-21 "
               "S1/S2 on ZM; no cross-market configuration closed on RTY or M2K.")},
    {"dossier": "RTY|F10", "ids": id_range("C117", "C121", "15, 30", 15),
     "Q1": (2, F10_Q1_15), "Q2": (2, F10_Q2),
     "Q3": (2, "Family overlap only: R1-21 S3 closed on ZM; R1-11 M2K Gate 0 used bar features without book data "
               "(other family); R1-20 is an execution line.")},
    {"dossier": "RTY|F11", "ids": id_range("C122", "C126", "15, 30", 15),
     "Q1": (1, F11_Q1), "Q2": (2, F11_Q2),
     "Q3": (1, "Same family and product at a neighbouring horizon: R1-15 E20S on RTY (36 bar features) and R1-11 M2K "
               "Gate 0 at h60, and R1-03 K1-cp2-01 ORB (M2K) are closed; R1-01 MES and R1-21 ZM family overlap.")},
    {"dossier": "RTY|F12", "ids": id_range("C127", "C131", "15, 30", 15),
     "Q1": (3, F12_Q1), "Q2": (2, F12_Q2), "Q3": (2, F12_Q3_FAM)},
]
