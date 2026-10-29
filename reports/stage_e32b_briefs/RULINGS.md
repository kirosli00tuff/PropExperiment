# Stage E.32b lead rulings and open choices (consolidated by the lead, session 3, 2026-10-29 ~04:10 PDT)

Every ruling was made after the spec hash (09ebe697...) unless marked "pre-hash". Full text and times are in
reports/stage_e32b_STATE.md. "Variant" names the score run's patch set (work/score/lead_variants.json) or the spec 5
declared variant that tests it; a ruling with a variant is kept in the return only if it changes the top 5.

## Open choices (sessions 1-2)
- OC-1 N = 838 (the prompt's SCOPE line "N stays 538" is a V51 carry-over; V53 item 2, V56 item 1).
- OC-2 Universe = E.28's 47 codes; ES, MES and the other owned roots not added.
- OC-3 Databento MBO availability and prices: one DataAccess worker (V37 shared source), not each reader.
- OC-4 Primary E is E.28's model (T 20, sigma_T = sigma_1); E_dir60 a declared variant.
- OC-5 Slippage 0.5 tick a round trip (assumption); variants slip0, slip1. OC-6 sigma_h = SD (RMS move); variant mad.
- OC-7 E.28's L1 >= 2.00 and no-zero gates not used; variant L1min2.
- OC-8 Satellite double penalty (leader's D2 facts and the D4 Sat deduction); variants D2_own, sat1.
- OC-9 D2 d by OpenAlex count terciles. OC-10 Own-broker venue (IBKR) in R2/R3 only.
- OC-11, OC-15 Planned context wipes at ~300k tokens (sessions 1 and 2). OC-12 DossierWriter worker writes R2;
  CombinationScorer a separate fresh worker; the lead writes R4. OC-13 Program's own earlier measurements (RETURN
  files) admitted as file-path sources, labelled with their windows.

## Rulings (sessions 1-2)
- LR-F3 VolCoder's choices where spec 2 is silent (overnight pairs join consecutive regular trade dates;
  median_close = median of each day's last main-session close; OC1 codes take the sibling's close; missing calendars
  take the sibling's session). No variant (no scored effect beyond R_d/J and D2 c, both per A0).
- LR-S Spread qualification (median; mean/time-weighted/hourly means all < 1.5 ticks -> median exactly 1; one-tick
  >50% statements for the tick in force; else S = 1 (u)); touch only as a sourced median. Variant: RL-SMEAN (S_mean).
- LR-D0 21-day month scaling of quotes. LR-D1 k ratio r = 0.9195 (ES proxy); variant RL-KZM (r = 3.06).
  LR-D2 p per spec text (only pre-2024-03 seals count); variant RL-PBRIEF. LR-D3 registrations are reads only for
  windows their searches ran on.
- HoldingCoder's 12 spec-7 readings accepted (work/F5/README.md). ScoreCoder readings 1-5 accepted (Sat (i) ">= 5x"
  literal; D6 leader for Sat (i)/(ii) only; D2 c provisional where notional unknown; unknown 50K listing or BC
  acceptance excludes; unknown Rel deduction 0; r3 pool Q4 and G from the worst member; R4 over all venues and over
  prop venues). EconSetup flags: cost per attempt = market case; one sigma_60 cap per pair; m* in sigma_60 units;
  T = 0 curves left out.

## Rulings (session 3)
- LR-SC ScoreCoder readings 6-14 accepted (score README); 12 adds: crude and natgas one asset class "energy".
- LR-E1 Econ pass 1 on every computable listed pair (the scorer needs them), 8 workers.
- LR-B1 Blind brief names-free (briefs/brief_blind.md).
- LR-F5-IBKR Own-broker band B = {h : G <= 1.10 min G} (no DLL or flat-by-close condition); c_f with 2 x all-in.
- LR-Q6d Own-broker sigma_day = sigma_cc x tick value; margin vs USD 6,000 (u).
- LR-R1 V38 closes the 528 trials' tested configurations on the 17 roots; its umbrella sentence (with V45 item 4) is
  an evidence finding (R1-19), not a ban; closed configurations closed at every venue; E.33c families closed on ZM,
  family overlap elsewhere.
- LR-R2a Combinations = top-15 pairs x applicable families + IBKR x the top-15 codes + pools. LR-R2b band = the
  pair's F5 B, h_c its lowest-G member. LR-R2c crude and natgas members asset_class "energy".
- FactTable items: FT-1 o/p booleans (o_owned_36m true when o = 0; p_all_read true when p = 1); FT-2 touch has no
  window rule (GC 4.62 from 2010 counts; variant RL-TRECENT); FT-3, FT-5, FT-7 (E.28's OC-A3-8 OCO kept), FT-9
  accepted; FT-11 noted (2YY 5YY 30Y ADV 0 and Lucid SIL RR-05 below commission: gate failures, no effect).
- LR-DLL No DLL on the modelled plan (Topstep, Bulenox): the MLL is used (spec 4 D convention; the scripts agree).
- Audit decisions: B1 (Lucid plan names), S2 (IIP lines), S3 (sizes, ticks) patched without relabelling; B2
  (MFFU name) and plan words patched by the lead; S4 left as ruled (RR-05 text; SIL fails the gate).
- LR-S1e HG primary S = 1 stays (value unchanged); the sourced -> u correction is an erratum with no score effect
  (F4 frozen; F4_corrections.json); under S_mean HG S = 1.55 (whole-day average).
- Blind ratings: the rater's primary values are used throughout (no lead override; each flagged value is consistent
  with the scale text and unknown rules); its alternatives run as reported sensitivities RS-D6SPAN, RS-D6THRESH,
  RS-D6CRYPTO, RS-D2BIIP, RS-MFFUR, RS-CRYPTOR, RS-ATOP2, RS-A3P, RS-ATRAD1, RS-RELTOP0, RS-RELTRAD1.
- LR-ATT The score run reads work/F5run/F2_attention_listcodes.json (format-only copy: codes as lists).
- Process: rater 1 (cut by the usage limit after 47 contracts; possible exposure to the B1 leak) superseded by a
  fresh rater 2 on the patched sheets; rater 1's contract ratings reported as inter-rater agreement only (302/329).

## Rulings (session 3, after the score run; 05:25-07:08 PDT)
- RL-KZM changes the top-5 order only and is kept in the return (spec 5). Sensitivities RS-MNQD6, RS-OWNONLY, RS-EQS2
  added after the RankingWriter showed MNQ is not a satellite (NQ/MNQ notional ratio 3.86 < 5); YM is in every top 5
  of the 28 variants and first in 23.
- Scope file: k(h) falls about as sqrt(h) (no flattening point); bands set by G (entry cap and power); news windows are
  not band conditions; soft DLLs treated as hard; E_dir60 mu* = 0 (topstep YM, RTY) is a model property, not an edge;
  the 0.5-tick slippage is in F5's c_f, not in E (spec 4 vs 7); "hours" not supported; ZL's S may be understated.
- Ranking file: QM's exclusion by the satellite double penalty is the intended OC-8 reading; "next products after ZM"
  read by underlying; no ZL S = 2.06 variant (cannot reach the top 5; econ busy).
- LR-Q6p Q6's daily payout threshold is the lowest over the firm's payout paths: Topstep 0 (Consistency Path), the
  Standard Path's $150 a sensitivity (ts150_v2); Tradeify 150; Lucid, MFFU, Bulenox 0.
- CombinationScorer flags: ZL F01 Q3 0 stands; MNQ F12 and F12 pools Q3 1 only if R1-14 H6 T3 is excluded; V39's
  commodity event drift closure not read as covering USDA/NOPA drift on the soy complex (V51's ZM protocol considered
  post-USDA families); other rater values stand.
- LR-Q3a (replaces the 06:21 reading that K1-cp1-01 "held to the flat", which rested on R1-03's line-level text): F01
  on YM, MYM and RTY re-tests closed configurations (E16-H1, a pooled test including YM: F01's rest-of-day rule at
  h 30; K1-cp1-01: 14:30-14:59 CT on MYM and M2K, strategy/members/k1/cp1.py:58-60): Q3 = 0 for 13 combinations.
- LR-V31 V31 read literally ("no rerun or variant on these windows, no purchase of the 10 fallback roots"): YM and MYM
  have no buyable clean test window (clean_test_window_months = 0, 98 combinations); the narrow reading is sensitivity
  q3only and user decision D1.
- LR-ZLW V56 item 1 ("stays sealed for a future hypothesis family"): ZL keeps its sealed window; F09 and F10 share its
  single read (user decision D2); sensitivity nozlw.
- R4 lead text corrected at 07:07 after the RecsDrafter's fact check (work/R4/fix_lead_text.py, 14 passages).

## Rulings (session 3 end and session 4)
- LR-Q3b (07:19:57, RV2 B1): RTY F09 (C112-C116) and ZL F09 (C138-C139) get Q3 = 1: E.12 Gate 0 (R1-11) and E.20's
  search (R1-15) held G17 cross-market lead features (60-minute returns of the other clusters' lead prices; never the
  product's own cluster) on M2K/RTY and ZL at h60-hF, a neighbouring horizon of both bands (spec 8.3 Q3 = 1, the reading
  the rater used for ZL F01 and F11). The leg-level reading (the dossier's leaders, NQ for RTY and ZS/ZM for ZL, were
  never live features there: Q3 2) is the sensitivity (= the earlier primary). Applied in patch_v31_q3_lead.py for every
  mode; r3 rerun (all four). Primary R4: C140 ZL F10 2.75, C138 ZL F09 2.65, C072 MNQ F08 2.55, C021 YM F08 2.55, C147 EQ3
  F08 2.55 (all Topstep); RTY F09 out (2.50); own-broker C141 ZL F10 ibkr 2.60.
- LR-Q3b detail (session 4, from R1Fixer's code check): the live G17 leads were ZN, 6E, CL, GC, ZC on RTY/M2K and NQ,
  ZN, 6E, CL, GC on ZL; E.12 also had g17_mbt (MBT, live only from 2024-01-02, two months of its window; g17_mes
  excluded by rule P-1a). The Q3 reason strings in R2_combinations.json list the six main leads; no effect on the ruling.
- LR-OF (08:58): recommendations:485 / draft:207 split under LR-Q3b: R1-11 and R1-15 are the same family for ZL F09 at
  a neighbouring horizon, other families for ZL F10 (no order-book features in either library).
- LR-RV1S1 (session 4): RV1 S1 fixed in the scorer (tie-break reads the market-case cost, as ruled in session 2),
  not by amending the ruling; score rerun 08:51:03, no score, gate or rank change.

## Open choices (sessions 3-4; numbering continues OC-1..OC-15, OC-14 = lead rulings after the hash carry variants)
- OC-16 Planned context wipe after session 3 (READY FOR WIPE 07:25; session 4 resumed 08:40:31).
- OC-17 LR-Q3b's leg-level reading reproducible as sensitivity q3bleg (work/R2/r3_out_q3bleg.json = session-3 list).
- OC-18 RV1 S1 fixed in the scorer, not by amending the ruling (LR-RV1S1).
- OC-19 ZL F09 P(edge) 0.07 -> 0.05 for the G17 null on ZL; ZL program prior stays about 4%.
- OC-20 EQ3 F08 pool prior under 1% (about 1.5% at most with V31 narrowed and 2024-03+ approved); K_eff 1,305 at the
  spec's rho 0.5 is likely optimistic.
- OC-21 R2_dossiers_for_rating.md kept as rated; corrections as errata (R2_dossiers.md, R2_Q_ratings.md) and in the R1
  file; LR-OF.
- OC-22 Base rate shown both ways: 4% over 23 lines, 1/19 over the 17 with a registered outcome (RV2 N5).
- OC-23 The return quotes git status --short by line count and this stage's lines (full listing in checks_*.txt).
- OC-24 Pauses shown apart from work time: usage limit 01:56-03:10, session-4 wipe gap 07:28:40-08:40:31; the lead's
  wait while econ pass 1 ran (04:09-05:24) is stage compute and counted.
- OC-25 The commit leaves the raw fetched pages untracked (briefs/pages/, 584 files, 135 MB; three raw HTML pages under
  work/CRYPTO and work/GRAINS), as E.28 and E.32 did; the reader logs with URL, fetch time and sha256 are committed.
