"""Rules applied and flags for the lead (R2_Q_ratings.md)."""

RULES = [
    "Q3 = 0 (re-test) when a band member repeats a closed single-product configuration of the same family on this "
    "price path at the same horizon (MNQ F01 = R1-14 H6 T1; ZL F01 = R1-08 K6-cp1-01). Q3 = 1 (close variant) for a "
    "pooled closed test that contains the product (R1-13 E16-H1/H4), an ML search whose bar features span the family at "
    "a band or neighbouring horizon (R1-11, R1-15), a shorter hold of a closed signal (K1/K6-cp3-01), or a same-family "
    "closed line at a neighbouring horizon. Q3 = 2 when the family was closed only on another product (incl. R1-21 on "
    "ZM, per LR-R1). Venue never reopens a closed configuration (LR-R1), so ids in one dossier share Q3.",
    "Same underlying counts as this product: MYM = YM (OC-1), MNQ = NQ price path (lead's instruction in the "
    "dossiers), M2K = RTY.",
    "Q2 policy: product-specific negative evidence gives 0 even when pool evidence is positive (ZL F01, MNQ F11, ZL F08 "
    "with none on ZL and cousins decayed); positive gross product evidence with a failed net program test stays 3 "
    "(F01 equities: F01.E02 against F01.E14/F01.E15), since costs are Q4-Q7's question.",
    "Pools (EQ3, EQ3m) take the weakest member on Q1, Q2 and Q3: a pooled test assumes the mechanism on every member, "
    "and a pool that contains a re-test re-tests.",
    "Evidence rule: every Q2 of 0 or 3 rests on full-text or reused rows (no 4 given), so no value is marked "
    "unverified. Within each dossier all ids share the shortest member, so Q1 never differs by id.",
]

FLAGS = [
    "Q3 = 0, 13 ids: C057-C061 (MNQ|F01) re-test R1-14 (E.20 H6, NQ path at MNQ cost, C-30 to close, V38); C132-C133 "
    "(ZL|F01) re-test R1-08 K6-cp1-01 (ZL momentum port, decision 12:44 CT, V40); C144, C151, C158, C165 (EQ3|F01) and "
    "C172, C179 (EQ3m|F01) re-test R1-14 through the MNQ member.",
    "Boundary 1 vs 0, YM/MYM/RTY F01 (C001-C006, C043-C044, C092-C096): the dossier gives K1-cp1-01 only a 'signal bar "
    "08:59 CT'; K6-cp1-01's 12:44 CT decision (30 min before the 13:14 CT flat) suggests the CP1 port trades the last "
    "30 min before F; if so, the 30-min member re-tests K1-cp1-01 on MYM / M2K and these become 0. R1-13 H1 (V31: 'no "
    "rerun or variant on these windows') also bears on them.",
    "Boundary 0 vs 1, ZL F01 (C132-C133): rated a re-test of K6-cp1-01 (same product, family and 30-min horizon); if "
    "the lead treats a different momentum signal (first half-hour vs rest of day) as a variant, 1. Q1 = Q2 = 0 there "
    "either way.",
    "Boundary 1 vs 0, MYM F11 (C053-C054) and ZL F11 (C142-C143): R1-11 and R1-15 ML searches tested these products at "
    "h60 (and h120) over bar features; rated close variants; a reading that the ML spanned the rule's information "
    "gives 0.",
    "Boundary 1 vs 0, MNQ F12 (C087-C091) and the EQ3/EQ3m F12 pools: 1 holds only if the F12 search stays on the "
    "expiry calendar (or the high-gamma reversal side); negative-GEX momentum into the close on all days at 30 min is "
    "R1-14 H6 T3.",
    "Boundary 2 vs 1, ZL F09 (C138-C139) and ZL F10 (C140-C141): ZL data were inputs to the closed R1-21 S1/S2/S3 "
    "configurations on ZM; rated 2 per LR-R1 (family overlap on other products); a mirror-leg reading gives 1. ZL F10: "
    "V50 item 4, ZL MBP-1 2020-12..2024-02 is not a clean holdout for order-flow tests.",
    "Ambiguity, ZL F03 (C134-C135): V39 closed 'commodity event drift as a standalone stage' and R1-23 lists only crude, "
    "metals and natgas; rated 2 on the reading that grain report drift is not covered; if V39 covers it, 0.",
    "Ambiguity, MNQ F10 (C077-C081) and the F10 pools: R1-22 (V49 NQ drop) is stated for the passive direction; its "
    "scope for directional book-state use on the NQ path is unstated; rated 2 on R1-21 family overlap.",
    "Q1 boundary 2 vs 3, every F04 and F05 id: F04's drift evidence is a weak joint test on ES before 2015 (F04.E03) "
    "against fast absorption (F04.E01); F05's drift is documented only in cash Treasuries (F05.E01) and as SPY FOMC-day "
    "close momentum (F05.E02); reading either as 'identified mechanism, evidence on a cousin' gives 3.",
    "Q1 boundaries elsewhere: F11 rated 1 (generic story; 2 on a literal reading of 'participant story'); MNQ F11 near 0 "
    "(F11.E10 is a net-of-cost failure at 5-15 min on this underlying, not a full-text contradiction at 15-30); ZL F08 "
    "rated 1 (no grain participant flow; cousin evidence null or decayed).",
    "Q2 boundary ZL F09: F09.E01 is peer-reviewed in sample on this product but documents cointegration only (no "
    "half-life or trading test); rated 2, not 3.",
    "Pools: EQ3/EQ3m F01 are gated and F11 get Q2 = 0 only through the MNQ member; whether to re-form a pool without MNQ "
    "is the lead's call, not the rater's.",
    "Unclear or conflicting facts: F01.E14 ('T1 gross 1.25 ticks vs 4.08 cost, t -0.53') does not say whether t is "
    "gross or net; equity F08 evidence (F08.E03) is at the European open, 23:00-00:00 PT outside the main session, so a "
    "cash-open F08 test has no direct evidence; F04's 08:30 ET releases fall before the main session; the "
    "documented-horizon column differs for the same evidence between YM|F04 ([60]) and MYM|F04 ([20]) and between "
    "EQ3|F11 ([5, 60]) and EQ3m|F11 ([5, 15, 60]) (extraction inconsistency, no effect on the ratings).",
]
