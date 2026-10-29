"""Q1-Q3 ratings for the ZL dossiers and the EQ3 / EQ3m pools.

CombinationScorer-OpusXHigh, Stage E.32b step 3b. Source read: briefs/R2_dossiers_for_rating.md only.
Pool rule: each of Q1, Q2, Q3 takes the weakest member (a pooled test assumes the mechanism on every member, and a
pool that contains a re-test re-tests). EQ3 members are YM|Fxx, MNQ|Fxx, RTY|Fxx; EQ3m members MYM|Fxx, MNQ|Fxx, RTY|Fxx.
"""

from data_eq import id_range

DOSSIERS_ZL = [
    {"dossier": "ZL|F01", "ids": id_range("C132", "C133", "15, 30, 60", 15),
     "Q1": (0, "Contradicted by full text on this product: Baltussen's BO row is null or negative out of sample "
               "(F01.E03) and the CBOT meal cousin's slope is negative with OOS R2 < 0 (F01.E16); the gamma and LETF "
               "story has no documented soybean-oil counterpart; only DCE 2002-2013 (F01.E09) and the in-sample "
               "commodity pool (F01.E01, R2 0.12%) are positive."),
     "Q2": (0, "Negative evidence on this product: F01.E03 (full text, peer-reviewed) OOS R2 negative or nil for BO; "
               "pooled program test incl. ZL net negative (F01.E15); the 0 rests on full-text rows."),
     "Q3": (0, "Re-tests R1-08 K6-cp1-01 (momentum port on ZL, decision 12:44 CT, about 30 min before the flat, closed "
               "V40) at the band's 30-min member; the 60-min member sits on R1-15 E20S r_ROD ML on ZL at t4 = F-60 / "
               "h60; R1-13 E16-H1 pooled incl. ZL.")},
    {"dossier": "ZL|F03", "ids": id_range("C134", "C135", "15, 30, 60", 15),
     "Q1": (3, "Report digestion with documented drift on cousins: soybean reaction significant at 30 min and growing "
               "to the close 2010-2021 (F03.E01), big-event drift after minute 10 in corn (F03.E02); against it F03.E03 "
               "(no systematic under- or overreaction) and F03.E04/F03.E05 (abstracts); nothing intraday on ZL "
               "(F03.E08 snippet, F03.E09)."),
     "Q2": (2, "Working paper and dissertation in sample on cousins (F03.E01 ZS/ZC, F03.E02 corn, full text) and a paper "
               "on ZS that finds no systematic drift (F03.E03); ZL itself only a news snippet (F03.E08): other-product "
               "evidence."),
     "Q3": (2, "Family overlap only: R1-08 K6-wasdepre-01 and K6-wasdepost-01 closed on ZC and ZS, R1-21 post-USDA "
               "dropped on ZM; R1-23 V39 'commodity event drift' names crude, metals and natgas, not grains (ambiguity "
               "flagged).")},
    {"dossier": "ZL|F08", "ids": id_range("C136", "C137", "15, 30, 60", 15),
     "Q1": (1, "Clock pattern without a grain-specific participant flow (the imbalance story is Boyarchenko's for "
               "equities); cousin evidence is null or decayed: ZM overnight plus first half-hour no prediction OOS "
               "(F08.E09), ZC settlement reversals declined after the 2012 rule change (F08.E08), DCE effect stopped "
               "(F08.E07, abstract); F08.E13 is volatility only."),
     "Q2": (0, "No evidence on ZL; the cousin full-text and reused rows are negative or volatility-only (F08.E08, "
               "F08.E09, F08.E13), so the 0 does not rest on the abstract row F08.E07."),
     "Q3": (1, "Close variant: R1-08 K6-cp3-01 prior-day close-location on ZL decides at the 08:30 CT reopen and holds "
               "to the flat; a 15-60 min hold at the same reopen is a shorter-hold variant; R1-13 E16-H4 pooled incl. "
               "ZL; R1-01 MES family overlap.")},
    {"dossier": "ZL|F09", "ids": id_range("C138", "C139", "15, 30, 60", 15),
     "Q1": (2, "Identified economic anchor (crush margin) but no evidence at the horizon: cointegration on 180 of 243 "
               "days in 2015 with no half-life or trading test (F09.E01); the crush-residual and propagation test on ZM "
               "finds nothing net (F09.E02); spillovers within 30 s (F09.E03, abstract)."),
     "Q2": (2, "Peer-reviewed in sample on this product but of cointegration only, with no horizon or trading test "
               "(F09.E01, full text), so below 3; sibling-leg program test net negative (F09.E02)."),
     "Q3": (2, "Family overlap: R1-21 S1 crush residual and S2 propagation closed on ZM with ZL as an input leg (LR-R1: "
               "family overlap on other products); R1-08 K6-crushgap-01 on ZS; trading ZL on the same residual is the "
               "mirror leg (1 if read as a close variant).")},
    {"dossier": "ZL|F10", "ids": id_range("C140", "C141", "15, 30, 60", 15),
     "Q1": (2, "Plausible participant story but forward predictability decays by 5-30 min (F10.E01); grain evidence is "
               "a drift-burst reversal with look-ahead (F10.E03, ZC) and an abstract with unknown horizon (F10.E04); "
               "the ZM order-flow and book test with ZL MBP-1 input fails net (F10.E07)."),
     "Q2": (2, "Cousin peer-reviewed in sample (F10.E03, ZC, full text via E.32, look-ahead to remove) and other-asset "
               "evidence (F10.E01); sibling program test net negative (F10.E07); nothing on ZL."),
     "Q3": (2, "Family overlap: R1-21 S3 order flow and book state closed on ZM with ZL MBP-1 as an input; R1-20 ZL "
               "passive follow-up skipped (execution line); R1-11 ZL bar-feature ML (other family); V50 item 4: ZL "
               "MBP-1 2020-12..2024-02 is not a clean holdout.")},
    {"dossier": "ZL|F11", "ids": id_range("C142", "C143", "15, 30, 60", 15),
     "Q1": (1, "Generic price-path pattern; F11.E01 (pool incl. crude) reversion 2-16 min and weak trend >= 1 h, OOS "
               "R2 under 1 bp; Chinese commodity intraday momentum and reversal do not cover costs (F11.E05, abstract); "
               "no commodity study positive OOS net at 1-240 min (E.32 front)."),
     "Q2": (2, "Peer-reviewed OOS gross on a cross-asset futures pool (F11.E01, full text); F11.E05 abstract negative; "
               "nothing on ZL."),
     "Q3": (1, "Close variant: R1-11 ZL Gate 0 (64 bar features) and R1-15 ZL E20S (36 bar features) at h60, a band "
               "member, and R1-08 K6-cp2-01 ORB on ZL are closed; an own-price-path rule is narrower than the closed ML "
               "searches.")},
]


def pool_ids(first_num, step, count, band, shortest):
    return [(f"C{first_num + k * step:03d}", band, shortest) for k in range(count)]


DOSSIERS_POOLS = [
    # ------------------------------------------------------------------ EQ3 (YM, MNQ, RTY), band 15, 30
    {"dossier": "EQ3|F01", "ids": pool_ids(144, 7, 4, "15, 30", 15),
     "Q1": (3, "Weakest member 3: all three underlyings have the identified hedging flow with product rows dominated "
               "by pre-2015 data (F01.E02: YM 2.18%, NQ 3.76%, Russell 3.15% OOS R2) and only cousin, conditional or "
               "flat post-2015 evidence (F01.E10, F01.E11, F01.E14)."),
     "Q2": (3, "Weakest member 3: peer-reviewed recursive OOS product rows for all three, gross (F01.E02, F01.E04; full "
               "text); asset-class pool in sample (F01.E01)."),
     "Q3": (0, "Re-tests R1-14 through the MNQ member (E.20 H6 on the NQ path, C-30 to the close, closed V38); the YM "
               "and RTY members are close variants of R1-13 E16-H1 (pooled).")},
    {"dossier": "EQ3|F04", "ids": pool_ids(145, 7, 4, "15, 30", 15),
     "Q1": (2, "Weakest member 2 (all three as YM|F04): only a weak ES joint test at t+10..t+30 (F04.E03); fast "
               "absorption (F04.E01, F04.E08 abstract)."),
     "Q2": (2, "Weakest member 2: cousin peer-reviewed in sample (F04.E03) and regulator paper (F04.E01); nothing on any "
               "member."),
     "Q3": (2, "Weakest member 2: family overlap only (R1-01 MES family E, R1-04 K2 ISM pre-drift; R1-19 evidence "
               "finding).")},
    {"dossier": "EQ3|F05", "ids": pool_ids(146, 7, 4, "15, 30", 15),
     "Q1": (2, "Weakest member 2: post-statement drift documented only in cash Treasuries (F05.E01) and SPY FOMC-day "
               "close momentum (F05.E02); F05.E06 is the pre-FOMC drift."),
     "Q2": (2, "Weakest member 2: other-venue and other-asset-class evidence (F05.E02, F05.E01)."),
     "Q3": (2, "Weakest member 2: family overlap only (R1-04, R1-07, R1-01).")},
    {"dossier": "EQ3|F08", "ids": pool_ids(147, 7, 4, "15, 30", 15),
     "Q1": (3, "Weakest member 3: identified imbalance carry-over at the European open on the ES cousin (F08.E03), "
               "60 min outside the band; cash-open handoff only F01.E05."),
     "Q2": (2, "Weakest member 2: cousin peer-reviewed in sample, negative after spreads (F08.E03) and SPY (F01.E05)."),
     "Q3": (1, "Weakest member 1: R1-03 K1-cp3-01 closed on MYM, MNQ and M2K and R1-13 E16-H4 pooled incl. YM, NQ and "
               "RTY; 15-30 min holds of these handoff signals are close variants.")},
    {"dossier": "EQ3|F10", "ids": pool_ids(148, 7, 4, "15, 30", 15),
     "Q1": (2, "Weakest member 2: plausible order-flow story, decay to insignificance by 5-30 min (F10.E01); "
               "gamma-conditioned ES reversal only (F10.E06)."),
     "Q2": (2, "Weakest member 2: cousin working paper (F10.E06) and other-asset evidence (F10.E01); ZM program test "
               "negative (F10.E07)."),
     "Q3": (2, "Weakest member 2: family overlap only (R1-21 S3 on ZM; R1-22 passive-direction drop of NQ, directional "
               "scope unstated).")},
    {"dossier": "EQ3|F11", "ids": pool_ids(149, 7, 4, "15, 30", 15),
     "Q1": (1, "Weakest member 1: generic price-path pattern, OOS R2 under 1 bp (F11.E01); F11.E09 dropped; F11.E10 "
               "fails on MNQ and NQ."),
     "Q2": (0, "Weakest member 0: MNQ's own-underlying evidence is negative OOS net (F11.E10, reused / full text); YM and "
               "RTY have only the cross-asset pool (F11.E01)."),
     "Q3": (1, "Weakest member 1: bar-feature ML at h60 closed on MYM, MNQ, NQ, RTY and M2K (R1-11, R1-15) and K1 "
               "price-path rules (R1-03); neighbouring horizon.")},
    {"dossier": "EQ3|F12", "ids": pool_ids(150, 7, 4, "15, 30", 15),
     "Q1": (3, "Weakest member 3: identified dealer-hedging flow at fixed dates, evidence on the ES cousin (F12.E01, "
               "F12.E03) and stocks/ETFs (F12.E02)."),
     "Q2": (2, "Weakest member 2: cousin and other-venue working papers in sample (F12.E01, F12.E02, F12.E03)."),
     "Q3": (1, "Weakest member 1 (MNQ): R1-14 H6 T3 GEX-conditioned close momentum on the NQ path is closed at 30 min; "
               "YM and RTY members are family overlap only.")},
    # ------------------------------------------------------------------ EQ3m (MYM, MNQ, RTY), band 30
    {"dossier": "EQ3m|F01", "ids": pool_ids(172, 7, 2, "30", 30),
     "Q1": (3, "Weakest member 3: identified hedging flow; product rows mostly pre-2015 (F01.E02); post-2015 evidence "
               "cousin, conditional or flat (F01.E10, F01.E11, F01.E14); band = documented 30 min."),
     "Q2": (3, "Weakest member 3: peer-reviewed recursive OOS rows for the Dow, NQ and Russell at 30 min, gross "
               "(F01.E02, F01.E04; full text)."),
     "Q3": (0, "Re-tests R1-14 through the MNQ member: the 30-min band is E.20 H6 T1 on the NQ path (C-30 to close, "
               "closed V38); MYM and RTY members are close variants of R1-13 E16-H1.")},
    {"dossier": "EQ3m|F04", "ids": pool_ids(173, 7, 2, "30", 30),
     "Q1": (2, "Weakest member 2: weak ES joint test ending at t+30 (F04.E03); fast absorption (F04.E01, F04.E08)."),
     "Q2": (2, "Weakest member 2: cousin peer-reviewed in sample (F04.E03) and regulator paper (F04.E01)."),
     "Q3": (2, "Weakest member 2: family overlap only (R1-01, R1-04; R1-19 evidence finding).")},
    {"dossier": "EQ3m|F05", "ids": pool_ids(174, 7, 2, "30", 30),
     "Q1": (2, "Weakest member 2: drift documented only in cash Treasuries (F05.E01) and SPY FOMC-day close momentum "
               "(F05.E02)."),
     "Q2": (2, "Weakest member 2: other-venue and other-asset-class evidence (F05.E02, F05.E01)."),
     "Q3": (2, "Weakest member 2: family overlap only (R1-04, R1-07, R1-01).")},
    {"dossier": "EQ3m|F08", "ids": pool_ids(175, 7, 2, "30", 30),
     "Q1": (3, "Weakest member 3: identified European-open imbalance carry-over on the ES cousin at 60 min (F08.E03); "
               "cash-open handoff only F01.E05."),
     "Q2": (2, "Weakest member 2: cousin peer-reviewed in sample, negative after spreads (F08.E03) and SPY (F01.E05)."),
     "Q3": (1, "Weakest member 1: R1-03 K1-cp3-01 closed on MYM, MNQ and M2K, R1-13 E16-H4 pooled; a 30-min hold of "
               "these signals is a close variant.")},
    {"dossier": "EQ3m|F10", "ids": pool_ids(176, 7, 2, "30", 30),
     "Q1": (2, "Weakest member 2: the 30-min band sits at the end of the documented decay (F10.E01); only "
               "gamma-conditioned ES reversal reaches 60 min (F10.E06)."),
     "Q2": (2, "Weakest member 2: cousin working paper (F10.E06) and other-asset evidence (F10.E01); ZM test negative "
               "(F10.E07)."),
     "Q3": (2, "Weakest member 2: family overlap only (R1-21 S3 on ZM; R1-22 directional scope unstated).")},
    {"dossier": "EQ3m|F11", "ids": pool_ids(177, 7, 2, "30", 30),
     "Q1": (1, "Weakest member 1: generic price-path pattern, OOS R2 under 1 bp (F11.E01); F11.E10 fails on MNQ and NQ."),
     "Q2": (0, "Weakest member 0: MNQ's own-underlying evidence is negative OOS net (F11.E10, reused / full text)."),
     "Q3": (1, "Weakest member 1: bar-feature ML at h60 closed on MYM, MNQ, NQ, RTY, M2K (R1-11, R1-15) and K1 "
               "price-path rules (R1-03); neighbouring horizon.")},
    {"dossier": "EQ3m|F12", "ids": pool_ids(178, 7, 2, "30", 30),
     "Q1": (3, "Weakest member 3: identified dealer-hedging flow at fixed dates; ES cousin and stocks/ETFs evidence "
               "(F12.E01, F12.E02, F12.E03)."),
     "Q2": (2, "Weakest member 2: cousin and other-venue working papers in sample (F12.E01, F12.E02, F12.E03)."),
     "Q3": (1, "Weakest member 1 (MNQ): R1-14 H6 T3 GEX-conditioned close momentum on the NQ path closed at 30 min, "
               "the band itself; MYM and RTY family overlap only.")},
]
