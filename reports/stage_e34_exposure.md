# Stage E.34 Part 0.2: exposure audit of ZL's discovery dates 2020-12-01..2024-02-29

Worker ExposureAuditor-OpusHigh (claude-opus-5-5, effort high). Written 2026-10-29, 12:27-12:30 PDT
(`TZ=America/Vancouver date`). Tools: Read, Bash. No web. No market-data file was opened or decoded. The only data-area
reads were directory listings of file names (the ZL MBP-1 raw folder, E.33's ZL split folder, the soy ohlcv-1m
folders). Under rule 3, no numeric result of a statistic computed on ZL data is copied here. Outcomes are given as a
verdict word and a file:line.

Inputs read (by line range): reports/stage_e34_briefs/X_extract_records.md (21 rows) and X_extract_code.md (64 code
rows, 14 feature ids); reports/stage_e32_discovery_protocol.md 146-177 (P1.5) and 367-465 (P4);
reports/stage_e32_test_seal.md 104-154; reports/stage_e32_briefs/X1_exposure.md 209-326 (Table C);
docs/DECISIONS.md 1029-1055 (V50); reports/stage_e32b_recommendations.md 384-398, 442-463, 589-633;
reports/stage_e34_briefs/seal/part01_seal_check.md. For verification: E.31_RETURN.md 18-28, 196-204, 310-314,
326-330; E.33c_RETURN.md 111-130, 185-211; E.33_RETURN.md 134-137; E.22_RETURN.md 373-402; E.12_RETURN.md 543;
X1_exposure.md 129-131, 170-200; E.17_RETURN.md 14-22; E.20_RETURN.md 29, 341-342; E.21_RETURN.md 8-10;
F3_vol.md 16-19; stage_e23_briefs/inventory/K6.md 12-29; ledger/trial_registrations.jsonl line 10 (first 300
characters); the E.33 pipeline code build_features33.py 115-175, cal33.py 70-130, data33.py 60-190, guard33.py 1-40,
195-345, split33.py 18-50; a grep of lab33.py and build_labels33.py for ZL (no hits).

## 1. Inventory: every earlier read of ZL data on or touching the discovery dates

"Audit" column: V = checked against the cited source and confirmed; C = corrected here (the correction is stated); X =
taken from the extraction and X1/X1_verify, not re-read here. Rows that only touch dates outside the discovery span
(E.8 2025-04 onward, E.16 calendar only, E.23 W_ext membership, E.24 no read, E.32 sealing) are in
X_extract_records.md Table 2 and are not repeated.

| # | stage | what was computed | ZL data and dates | labels on ZL, or ZL as an input | what of the outcome was published | source | audit |
|---|---|---|---|---|---|---|---|
| 1 | E.0 | quote metadata only (record counts) | ohlcv-1m metadata, 2019-05-01..2026-06-21; no price read | none | metadata row | stage_e0_quotes.md:73 | X |
| 2 | E.12 Gate 0 (471 baseline) | family B: per-root ML ridge pairs on ZL, horizons h60, h120, hF; family A: pooled tests including ZL rows; G17 cross-market 60-minute lead returns on ZL (NQ, ZN, 6E, CL, GC); c/sigma admissibility filter | ZL step 2 bars, trade dates 2019-05-06..2024-02-29 (all discovery dates, and the sealed window's 2019-05-06..2020-11-30) | ZL label (family B, gate0B_ZL_h60/h120/hF); ZL rows in pooled family A | per-pair statistics for the three ZL rows and FAIL (X1_exposure.md:129-131; E.12_RETURN.md:543); G17 lead set per recs L11 (stage_e32b_recommendations.md:442-449) | as cited | V |
| 3 | E.14 / E.18 | M1 ridge per horizon (h60, hF) fitted once on the E.12 panel, ZL rows included | E.12 panel, 2019-05-06..2024-02-29 | ZL as training rows (ZL-labelled rows inside a pooled fit); tested on other products | C1 stopped at C10 (no statistic); C1b FAIL | stage_e32_test_seal.md:124 | X |
| 4 | E.17 (r002-E16) | H1 settlement-window momentum (S_p-30 to S_p), H4 intraday reversal of the prior day's H1 move, H5 combination; pooled over 27 price paths incl. ZL | ZL ext2010h 2010-07..2019-04 and step 2 2019-05-06..2024-02-29 (all discovery dates; the whole sealed window) | ZL price path pooled (a 30-minute ZL forward move at the settlement window, inside a pooled label) | pooled test rows and FAIL (E.17_RETURN.md:14-22) | as cited | V |
| 5 | E.20 (r005-E20S) | 45-configuration ML search (ridge, LightGBM depth 2) on 36 late-session bar features, nested CPCV, with G17 leads | ZL step 2, 2019-05..2024-02 (all discovery dates; sealed window's 2019-05-06..2020-11-30) | ZL label rows in pooled fits at h60, h120, hF | FAIL for all 45; ZL "never traded" out of sample (E.20_RETURN.md:29, 341-342); per-vehicle results not recorded | as cited | V |
| 6 | E.21 (r006-E21) | 12-month TSMOM and a trend blend, per-root contributions | ZL ext2010h and step 2, 2010-07..2024-02 | ZL label (multi-day, outside band B) | FAIL; per-root ZL rows recorded (X1_exposure.md B5) | E.21_RETURN.md:8-16, 385, 412 | X |
| 7 | E.22 Part A | K6 confirmation: K6-cp1-01 ZL (fill 12:45, exit about 13:14, about 29 minutes), K6-cp2-01 ZL (opening-range breakout, 75-bar hold), K6-cp3-01 ZL (prior-close location, 08:31 to 13:14); K6-crushgap-01 ZS (overnight crush-margin gap, ZM and ZL legs) | ZL step 2, 2019-05-06..2024-02-29 (all discovery dates; sealed window's 2019-05-06..2020-11-30) | ZL label (cp1, cp2, cp3); ZL as an input leg (crushgap, ZS traded) | full member rows, tier B, status null (E.22_RETURN.md:373, 380, 387, 390); K6 "no cluster statement" (398-402) | K6.md:12, 19, 26, 29 | V |
| 8 | E.22 Part B | micro trend book design (weekly correlations, returns, costs, MZL) | ZL ext2010h and step 2, 2010-07..2024-02 | ZL returns (multi-day design) | design study; E22-F1 registered, never evaluated | stage_e22_microbook.md:25-26 | X |
| 9 | E.25 NM1 | derived gross per trade and gross t from the E.22 ZL trip files and the E.12 ZL rows | E.22 trips 2019-05-06..2024-02-29 | ZL label (derived from row 7) | descriptive ZL rows (NM1_nearmiss_table.md:109, 180-181) | as cited | X |
| 10 | E.28 A0 | big-move-day counts per calendar year | ZL ohlcv-1m raw files ending on or before 2023-11-01 | none (volatility and calendar) | descriptive counts | A0_contract_stats.md:12-14, 202 | X |
| 11 | E.31 pilot | ZM passive markouts (1, 10, 60 s) split by the ZL mid move over the prior 1 s and 10 s and by the joint ZS+ZL move; ZL tick check; per-trade-date record counts and tail checks of the Z3 files (canary, verify) | ZL MBP-1 front (Z3), 2020-12..2024-02, 816 dates | ZM label; ZL only as a conditioning split (stats31.py:334-343; measure31_core.py:686-688, 900-914) | the ZL split buckets with means and intervals (stats31.md 1071-1554; X1 Table C2); the return states no ZS, ZL, imbalance or USDA bucket is positive (E.31_RETURN.md:200-201) | E.31_RETURN.md:18-28, 196-204; code rows 1-25 | V |
| 12 | E.31 follow-up (V49) | ZL trade-through measurement: planned, not run | n/a | n/a | "ZL follow-up (skipped)" (V50 item 1; E.31_RETURN.md:312-313, 329-330) | DECISIONS.md:1031-1038 | V |
| 13 | E.32b F3 and F5 | day-session sigma_h of ZL at h1, h5, h15, h30, h60; holding band B = 15, 30, 60 and e80 from it | ZL ohlcv-1m, 2022-11-01..2023-10-31 through BarGuard | none (volatility) | the ZL sigma row (F3_vol.md:163) and band B (F5_holding.md:905); the sigma values are in this stage's shared RULES and every E.34 worker has read them | F3_vol.md:16-19; f3_vol.py:40, 57 | V |
| 14 | E.32b ranking | C138 (ZL F09) and C140 (ZL F10) ranked and recommended; Q3 ruling on G17 (LR-Q3b, LR-OF) | inputs from rows 2, 5, 7 and 13; no separate ZL read | n/a | ranking (E.32b_RETURN.md:21-25, 186-200) | recs 442-463 | V |
| 15 | E.33 search (r009-E33, 300 ids) | 5 sets x 6 ZM labels x 10 settings. ZL enters S1 (F1 crush: C = 11 ZL + 2.2 ZM - ZS; zR regression of ZM on ZS and ZL; ZL volume in vrel15), S2 (F2.4-F2.6 ZL returns, F2.7 d5, F2.10-F2.11 ZL level-1 OFI) and S5 (all). S3 and S4 carry C.11 and C.12, the F1/F2 validity flags, which depend on ZL validity. Reference statistics: sigma_ZL, trailing mean of abs OFI_ZL | ZL MBP-1 split, 816 dates; search on 796 OOF dates 2020-12-30..2024-02-29 | ZM labels F05, F15, F30, F60, T15, T30; ZL as an input only (lab33.py and build_labels33.py: no ZL reference) | Tier A empty; gate funnel, G1-passer counts by set and label, the 10 best configurations by SR_d with identifiers, largest DSR with its configuration id, a "no statement" null per set, "clean negative" (E.33c_RETURN.md:111-130, 185-211) | ledger line 10; feat33.py rows 39-53 of the code extract | C: the extraction (EX-18) names S2 and S5 only. S1 also reads ZL through the crush, and S3 and S4 carry ZL-dependent validity flags (P4 counts: "S1 23" = C + F1, stage_e32_discovery_protocol.md:464; E.33c_RETURN.md:201) |
| 16 | E.33 / E.33b checks | split counts against raw counts; B3 agreement of sigma_ZL and other features on 20 dates; G6 ts_recv - ts_event per month for ZL | ZL MBP-1, 2020-12..2024-02 | none (data checks) | agreement statements; split counts (E.33_RETURN.md:136) | E.33b_RETURN.md:66-67; g6_33.py:42-66 | V (E.33_RETURN.md:136) |
| 17 | E.33 guard dry check | refusal of a sealed ZL path and of a test-window date | none read | n/a | refusal | E.33_RETURN.md:76-81 | X |
| 18 | acquisition | purchase and quote events | ZL ohlcv-1m 2010-07..2026-06; ZL MBP-1 from 2020-11-30T22:00Z; definitions to 2024-02-29 | n/a | ledger counts | spend_zl_summary.txt (Haiku folder) | X |
| 19 | E.34 (this stage) | no computation. The lead read E.33c_RETURN.md sections 1-3.8 while orienting: aggregate ZM outcomes, per-set gate counts (including the ZL-input sets S1, S2, S5) and the top-10 configuration list. This auditor read, as its brief required, X1 Table C (the E.31 ZL-conditioned ZM markout buckets with their values), the E.22 K6 ZL member rows, the three E.12 gate0B_ZL rows, the E.17 test table and E.33c 3.4 and 3.7. The two Haiku extractors read program reports and code. Every E.34 worker has the E.32b ZL sigma_h figures in the RULES | no market data | ZL labels seen: E.22 cp1-cp3 rows, E.12 gate0B_ZL rows (as published) | nothing new published; no value copied here | this file; BRIEFS.md RULES | n/a |

Rows 2, 3, 4, 5, 6, 7, 8 and 9 also touch the sealed test window, on one-minute bars only. The seal document records
this (stage_e32_test_seal.md:117-131): "No order-book data (MBO, MBP, trades) for the window was ever bought or read".
For ZL, the sealed window's bars carried ZL-labelled outcomes for the row 2, 4, 5, 6 and 7 mechanisms.

Extraction errors and gaps found: (a) the S1 omission in row 15 (corrected above). (b) The records extraction has no
row for E.31's Z3 data checks or E.33's G6 timing probe; they are merged into rows 11 and 16 from the code extraction
(rows 21-24, 36). (c) The code extraction left note N2 open; it is settled in section 6. Every other row checked (V)
agreed with its source. I found no row whose cited line failed to support it.

## 2. Verdict per proposed feature group and label

The definitions are E.32b's draft (recs 4.5(b), lines 589-633) applied to E.32's P4 text (lines 367-465). The draft
mirrors E.32's ZM features with ZL as the traded leg: F10 = F3 on ZL's own book; F09 = F1 and F2 mirrored, with ZS
and ZM as leaders and possibly CL; context C; labels F15, F30, F60, T15 and T30 on ZL. The scale is the brief's:
none / indirect (ZL only an input to another product's label, or volatility and calendar statistics) / direct (an
outcome with a ZL label, or a ZL book statistic conditioned on a candidate feature).

### F10, order-book state on ZL's own book (E.32 F3.1-F3.12 mirrored)

| item | verdict | basis |
|---|---|---|
| OFI_ZL_k, k = 1, 5 (F3.1, F3.2 mirror) | indirect | E.33 F2.10 and F2.11 computed ZL best-level OFI from MBP-1, with the same Cont-Kukanov-Stoikov e_n and a 20-date reference, as inputs to ZM labels in S2 and S5 (feat33.py:1050-1051). From ZL MBO at level 1 it is essentially the same series. Its ZM-label outcome is published only at set level (row 15) |
| OFI_ZL_15 (F3.3 mirror) | none | E.33 used k = 1 and 5 only for ZL (P4 line 434) |
| IOFI5, levels 1-5 | none | no ZL depth beyond level 1 was ever owned or read |
| TI_5, TI_15, ZL aggressor imbalance | none | E.33 used unsigned ZL trade volume only (F1.5; feat33.py:592) |
| QI1, QI3 on seasoned ZL depth | none | E.31's queue-imbalance split and E.33's F3.7-F3.8 were on ZM's book. No ZL imbalance was ever computed. These are the nearest analogues on another product (cross-product, not ZL exposure) |
| CR5, SW5, RF15 | none | they need ZL MBO, which was never owned |
| lam60 on ZL | none | not computed for ZL |
| any ZL book statistic conditioned on a feature | none | E.31's conditioning used ZL mid moves to split ZM fills, never ZL book state against a ZL outcome |

### F09, crush residual mirrored with ZL traded (E.32 F1.1-F1.8)

| item | verdict | basis |
|---|---|---|
| zC30, zC120, dzC5, zC30 x vrel | indirect, close | the crush C and its z-scores are the same series whichever leg is traded. E.33 computed exactly these (F1.1, F1.2, F1.4, F1.6) against ZM labels in S1 and S5, with set-level outcomes published (row 15). A residual that reverts must revert through some leg, so a ZM-side null bears on the ZL side. This is still not a ZL outcome |
| zR (regression residual) | indirect | the E.33 regression is ZM on ZS and ZL. The mirror, ZL on ZS and ZM, is a different fitted residual |
| vrel15 (ZL share of soy volume) | indirect | E.33 F1.5 used ZL volume in the denominator of ZM's share |
| gC(D), gC decay (F1.7, F1.8) | indirect | computed in E.33 against ZM labels. K6-crushgap-01 traded the overnight crush gap in ZS with a ZL leg on bars, 2019-05-06..2024-02-29, null (row 7) |

### F09, propagation mirrored into ZL (E.32 F2.1-F2.11)

| item | verdict | basis |
|---|---|---|
| rS_k, ZS returns as leader (k = 1, 5, 15) | none (for ZL) | computed in E.33 against ZM labels only. E.31 split ZM fills by ZS seconds-scale moves. Neither involves ZL |
| rM_k, ZM returns as leader | none (for ZL) | ZM's own returns were ZM-label features (E.33 F4.1-F4.3) |
| d5 mirror, implied-oil move minus ZL's 5-minute move | indirect, same series | E.33 F2.7 equals -dC_5/2.2 scaled by sigma_ZM (P4 line 432). The ZL mirror is -dC_5/11 in ZL ticks scaled by sigma_ZL, the same crush change up to a positive per-date scale. It was computed against ZM labels |
| OFI_S_k, OFI_M_k (leaders' OFI) | none (for ZL) | ZM-label features only (E.33 F2.8-F2.9, F3.1-F3.2) |
| rL_k, ZL's own returns (only if kept; a strict mirror drops them) | direct | ZL own-price-path outcomes on these dates: E.22 cp1 and cp2 momentum on ZL, and E.12 and E.20 bar signals with ZL labels at h60-hF. E.33 also used rL_k against ZM labels (indirect) |
| CL as a leader (the draft's "possibly CL") | direct | E.12 family B (ZL label, h60, h120, hF) and E.20 (ZL rows) held G17, the 60-minute log return of CL (with NQ, ZN, 6E, GC), as live features on ZL, 2019-05-06..2024-02-29, both FAIL (recs 442-449). Pooled ML, not a CL-specific test |

### Context block C on ZL (E.32 C.1-C.15 with ZL substituted)

| item | verdict | basis |
|---|---|---|
| C.1, C.2 time of day | indirect (calendar) | E.22 cp1 (12:45) and cp3 (08:30) were ZL outcomes at fixed clock times. Time of day as a feature was never tested on ZL |
| C.3, C.4 ZL spread and touch depth | none | never computed. E.32b assumes S = 1.0 tick (marked u) |
| C.5 ZL volume against its 20-date same-minute mean | indirect | ZL volume counts only (E.33 F1.5) |
| C.6 log sigma_ZL | indirect (volatility) | E.32b F3 (row 13); E.33 sigma_zl references |
| C.7 ZL front expiry | indirect (calendar) | ZL front identity sets E.33's segments (cal33.py:181-190) |
| C.8, C.9 release flags | none (for ZL) | E.31's USDA split was on ZM fills, and E.22's WASDE pre-drift was on ZS |
| C.10 Monday or after a closure; C.15 June-August | none | not computed on ZL |
| C.11-C.14 validity flags | indirect | E.33's F1 and F2 flags depend on ZL validity |

### Labels on ZL

| label | verdict | basis |
|---|---|---|
| F15 | indirect | ZL sigma_15 (E.32b F3). No 15-minute ZL outcome was found in any stage |
| F30 | direct, under other features | E.22 K6-cp1-01 ZL (about 29-minute hold, 12:45 entry) and E.17 H1 (S_p-30 to S_p, pooled with ZL) on these dates. Both are fixed clock windows at bar resolution, null and FAIL |
| F60 | direct, under other features | E.12 gate0B_ZL_h60 (ZL ridge), E.20 h60 (ZL rows), E.22 cp2 (75-bar hold) |
| T15, T30 | indirect | no triple-barrier label on ZL in any stage. E.33's T15 and T30 were on ZM. ZL sigma only |

Summary: no proposed F10 or F09 feature has ever been put against a ZL-labelled outcome, with two exceptions: ZL's own
returns (direct, if kept) and CL as a leader (direct, through G17 at h60-hF). The closest exposure is indirect. E.33
computed the crush z-scores and the crush-change d5 as ZM-label features, and those series are identical (up to
scale) to the F09 mirror's. The labels F30 and F60 on ZL were looked at directly, but only under bar mechanisms
unrelated to F09 and F10 (momentum into the close, breakout, open location, settlement window, pooled bar ML).

## 3. Firewall rules for the ZL protocol's P1.5 (concrete and checkable)

These are drafted for the lead's declaration. Each rule says how a reviewer checks it.

1. Data allowlist (guard). The run stage's guard is a copy of guard33 with its allowlist changed. It allows only:
   the 39 Z3 ZL MBP-1 files of manifest 09396842 (`range=2020-11-30T220000Z_...` through
   `range=2024-01-31T220000Z_2024-02-29T220000Z`); the Z2, Z1 and Z4 discovery files of the same manifest; the ohlcv-1m
   files `range=2020-12-01_2021-01-01` through `range=2024-02-01_2024-03-01` of ZL_v_0, ZS_v_0, ZM_v_0 (39 each), and
   of CL if CL is declared; any ZL MBO discovery purchase, by its own manifest; the P3.6 release calendars
   (sha256-pinned); and the run stage's own derived tree. It keeps every guard33 refusal: data/sealed/ and the
   sealed originals; trade dates 2017-05-01..2020-11-30 and on or after 2024-03-01; record ts_recv before
   2020-11-30T22:00:00Z; derived_unsealed_files.tsv; reports/stage_e31_briefs/work/pilot/runs/. Check: a dry-check
   with at least the four guard33 probes, plus one probe of a ZL ohlcv-1m name in 2020-11 and one of a derived/e33
   results folder. All must be refused.
2. Reuse of E.33 derived data. The run stage may read E.33's ZL and ZS split arrays (derived/e33/split/ZL and ZS:
   816 files, 2020-12-01..2024-02-29 by name) as data, after checking DONE counts. It may not open E.33's labels,
   search, statistics or selection outputs (search33.py stats.json, P8_select33.json, D_stats.md and .json). It
   builds its own features. Check: the guard's allowlist names derived/e33/split only, not derived/e33 whole.
3. Results that may not be consulted by any run-stage worker or the lead while declaring: E.31's stats31.md and .json
   and X1's Table C and its appendix; E.33, E.33b and E.33c results (sections 3.4-3.8 of E.33c_RETURN.md and the
   files they cite); the E.22 K6 ZL trip files and member rows; E.25 NM1 ZL rows; the E.12 gate0B_ZL rows; the E.20
   search outputs; the E.17 units files; E.21 per_root/ZL.json. Check: each run-stage brief carries this list. The
   guard refuses the data-area ones. The lead's earlier reading of E.33c 1-3.8 is disclosed in the declaration
   (row 19), and nothing in the declaration may cite it.
4. Definitions fixed from text. Every feature is E.32 P4's text (lines 367-465) passed through a written
   substitution table, hashed before any outcome: traded leg ZM to ZL; legs ZL to ZM; tick 0.10 USD/ton to 0.01
   cents/lb; sigma_ZM to sigma_ZL; C unchanged; F2's other-leg returns become rS_k and rM_k. No look-back, threshold,
   sign, clip or weight differs from E.32's text unless units or data force it (for example ZL MBP-1 against MBO for
   F10). Each such change is listed with its reason. Option B's rule thresholds (abs z >= 1.5, 2.0) and leader
   choices cite recs lines 618-619 and a literature source, never an E.33 or E.31 result. Check: a reviewer diffs the
   table against P4. Any item whose only stated source is an outcome file fails the review.
5. Grid not trimmed by outcome. Labels are E.33's six minus F05, and the sole reason is band B (cost and sigma,
   E.32b F5; sign-free). The 10 model settings are E.33's, unchanged. The sets are the full mirror. No set, label,
   setting or feature is added, dropped, ordered or weighted by reference to E.33's per-set or per-label gate counts,
   its top-10 list or E.31's splits. Check: every grid element carries a source tag (P4 line, recs line or
   literature quote).
6. Minute look-backs only: no lead-lag feature from ZS, ZM or CL into ZL with a look-back under 1 minute (E.31's
   ZL splits used 1 s and 10 s). Check: the smallest look-back in the table is 1 minute.
7. Queue imbalance enters as E.32's continuous F3.7 and F3.8 definitions on seasoned depth. No bucket edge from
   E.31 (+-0.2, +-0.6) appears anywhere. Check: grep the declaration and code for those edges.
8. Selection is mechanical (a copy of E.33's P8 with G2 re-set in ZL ticks). Discovery selects and the one sealed
   read confirms (V43). No person or model chooses among configurations after outcomes.
9. Loader rule (from section 6): previous-date loads come only from the run stage's own 816-date list, so the first
   date has no previous date. Each loaded date passes check_request, and records pass check_records. Check: a unit
   test that asks for the previous trade date of 2020-12-01 and expects a refusal or no date.
10. Disclosure: the declaration carries this file's section 1 (or a pointer to it with its sha256) and states that
    E.34 computed nothing on ZL.

## 4. Choices excluded because of exposure

These are proposals for the lead's ruling. The protocol's content is the lead's decision.

| # | excluded choice | reason |
|---|---|---|
| E1 | Sub-minute lead-lag features from ZS or ZM into ZL (look-backs of 1 s or 10 s) | E.31's ZL and ZS+ZL splits were at exactly these lags (row 11). The E.32b draft and E.32's firewall already set minute look-backs only |
| E2 | Queue-imbalance thresholds or buckets taken from E.31 | E.31's buckets on ZM fills are known. Rule 7 keeps QI continuous |
| E3 | A ZL own-price-path set (F4 mirror: momentum, breakout, open location, gap, late-session terms) and ZL's own returns rL_k as features | ZL-labelled outcomes for these mechanisms exist on the discovery dates and on the sealed window's 2019-05-06..2020-11-30 bars (rows 2, 5, 7). The test window is not clean for them. They are not in E.32b's draft; listed so they are not added |
| E4 | 60-minute cross-market lead returns (CL, NQ, ZN, 6E, GC) as ZL features, above all at F60 | this repeats G17 in E.12 and E.20 on ZL at h60-hF, with known FAIL outcomes and test-window dates read. If CL is kept as a leader, it enters only through the F2 mirror at k = 1, 5, 15 minutes, justified by literature (rule 4) |
| E5 | A once-a-day overnight crush-gap rule | it repeats K6-crushgap-01 (null; ZL leg). gC and gC decay stay as continuous features inside the F1 mirror, as E.32 kept them for ZM |
| E6 | Pruning or ranking sets, labels or model settings by E.33's results (for example dropping the crush set, or favouring T30) | outcome-steered (rule 5). The lead has read E.33c 3.4-3.8 |

Not excluded, with reasons: (a) labels F30 and F60. Their direct exposure was under unrelated bar mechanisms at
fixed clock windows, and band B is set by cost and volatility, sign-free. Dropping them would itself be a choice
steered by those outcomes. (b) The F1 and F2 mirrors (indirect only). Their definitions were frozen in E.32's text
before E.33 read any outcome, and no ZL-side outcome exists. (c) F10 (none, except level-1 OFI, which is indirect).
(d) Context C (indirect or none). (e) Using E.32b's ZL sigma_h for band B and e80: it is a volatility statistic,
disclosed in row 13.

## 5. Verdict

ZL's discovery dates are not virgin, but this program's features were never tested against a ZL outcome. Every
earlier ZL-labelled outcome on these dates was a one-minute-bar mechanism unrelated to F09 and F10, all null or FAIL:
the K6 ZL members, E.12 Gate 0 family B, E.17's pooled settlement window, E.20's pooled search and E.21's trend. The
order-book reads (E.31, E.33) used ZL MBP-1 only as an input to ZM labels or as a split of ZM fills. No ZL book
feature other than level-1 OFI was ever computed, and ZL MBO was never owned.

The strongest exposure is indirect. E.33 searched the crush z-scores and the crush-change d5 against ZM labels, and
those series are identical, up to scale, to the F09 mirror's. E.33's clean negative on its crush and propagation sets
therefore bears on F09's prior. The firewall must keep that result from setting any sign, threshold or grid choice.

Two items carry direct exposure: ZL's own returns and 60-minute cross-market (G17) leads, CL included. I propose
excluding them in their exposed forms (E3, E4). V50 item 4's warning concerns the ZM order-flow reads and does not
transfer to ZL's own book: no ZL order-flow signal was ever measured.

Under rules 1-10, the run stage can fix every definition from E.32's frozen text and E.32b's draft. The sealed
2017-05..2020-11 read has never selected any configuration of this program. Its bar data was read for ZL outcomes
under the excluded mechanisms only, so the one-shot test stays clean for F09 and F10 as defined.

## 6. Settled: can build_features33.py:156 load a record from trade date 2020-11-30 or earlier?

No. The code path has four independent locks:
1. Previous-date source. `day_axis` (build_features33.py:124-138) takes `prev` from
   `cal33.previous_trade_dates(day, 1)`. That function slices the 816-date list `_trade_dates()[max(0, i - n):i]`
   (cal33.py:125-128), and the list is required to start at `g.DISC_FIRST` = 2020-12-01 (cal33.py:81-87; guard33.py:72).
   For 2020-12-01 (index 0) the slice is empty and `day_axis` raises "no overnight session and no previous trade
   date": nothing is loaded. In practice 2020-12-01, a Tuesday, has an overnight interval, so `prev` is None. Every
   other date's previous date is a member of the list, so it is 2020-12-01 or later.
2. Request guard. `data33.load_mbp1` calls `g.check_request(path, day, day)` (data33.py:175). That calls
   `check_date` (guard33.py:269-282), which refuses 2017-05-01..2020-11-30 and anything before 2020-12-01.
3. Record guard. `g.check_records` (data33.py:183; guard33.py:325-339) refuses any record with ts_recv before
   2020-11-30T22:00:00Z. `_check_window` (data33.py:107-110, called at 185) refuses records outside D's
   [D-1 16:00 CT, D 16:00 CT) window.
4. File spans. The first raw Z3 file is `range=2020-11-30T220000Z_2020-12-31T220000Z`. 2020-11-30 is in CST, so
   22:00Z is 16:00 CT, which ends trade date 2020-11-30. That file holds no record of trade date 2020-11-30 by the
   ts_recv convention. E.33's ZL split folder holds 816 `.npy` names from 2020-12-01.npy to 2024-02-29.npy (directory
   listing only), and split33 assigns records only to those 816 windows (split33.py:42-47, 88-92).

Residual, stated and not resolved here: check_records sets no lower bound on ts_event (guard33.py:326-328, by design
for MBO snapshots). A first-hour 2020-12-01 record could carry a ts_event just before 22:00Z, and the top-of-book
fields of the first records describe the book left from 2020-11-30's close. Both are outside the window by the
seal's UTC ts_recv rule. Both fall in the 20-date burn-in, which has no rows or labels. Whether any such ts_event
exists is a count question for DataFacts, not answered here.
