# Stage E.33b: compiled coder readings (draft for the lead's decisions; PipelineReview SF1)

Compiler: ReadingsCompiler-OpusXHigh (Opus 5.5, xhigh), 2026-10-28, started 09:13 PDT. Brief:
reports/stage_e33b_briefs/brief_ReadingsCompiler_b.md. This file is a DRAFT for the lead. It decides nothing:
every "PROPOSED" line is a proposal, and reports/stage_e33_protocol_readings.md (the file P0.2 freezes) is the
lead's to write. No code was edited; code was read only where a readings file states a choice that another file
contradicts (labB.py:256-260, lab33.py:610-615, feat33.py:843-845, featB.py:128-129).

## Sources (sha256, first 12 hex, at 09:25 PDT)

Readings (under reports/stage_e33_briefs/work/): FeatureCoder_readings.md 507ac1f27149 (FC), implB/FeatureCoder2_readings.md
ed4fc0e9bed6 (FC2), LabelCoder_readings.md 3a5e2e95ef4b (LC), implB/LabelCoder2_readings.md d89ee6328720 (LC2),
SearchCoder_readings.md fe35d6343d42 (SC), ProofCoder_readings.md 726140546e54 (PC), StatsCostCoder_readings.md
e14c281947f7 (SCC), DataCoder_readings.md dabd71c32aaa (DC), TestCoder_readings.md cb419831cdf6 (TC). No other
*_readings.md exists under work/ (find, 09:14). Reviews (under reports/stage_e33_briefs/review/): PipelineReview.md
8a2b5f6e0fe3, SearchReview.md fd4bdeb7f530, ProofReview.md 326e1ccfe790, MathReview.md 4805d47c1e2e, and the
E.33b phase-1 review PipelineReview_b.md 24ba370a6ad1 (09:23; its views were added at 09:38). Agreement:
work/B3_agreement.md c1a68fc756cf (runs full_r1, feat_r2_partial, lab_r3, full_r2). Rulings already in the readings
file: reports/stage_e33_protocol_readings.md (RF; R-L1..R-L9, R-B3-*; read at 09:23 and 09:37, sha256 067aca889e13).
Protocol: reports/stage_e32_discovery_protocol.md (sha256 c4ffb9d79af4...). User decision V52:
docs/DECISIONS.md:1078-1095. FC changed during the compile (09:30, sha256 e7008d17b708: an "E.33b note" FC:43-75 on
the FD7 fix, the FD6 test and N11's order_log; no new reading ID); FC2 unchanged at 09:37. Both are being edited by
the running fix workers (STATE b3, b4); re-check their hashes before the freeze. FC line numbers below are valid for
both versions (the note was appended after line 42).

Citations are file:line. "B3" = B3_agreement.md run full_r2 (07:02 PDT) unless another run is named. full_r2: labels
0 cells in all 19 columns on every date; sigma 0; features 57 of 59 columns 0 cells, F3_11 5,385 cells (FD6), F3_9
10 cells (FD7). "0 cells" below means that column family agreed on every row of the 20 dates, which says nothing
about a latent case the 20 dates did not contain.

## Flag rule (how NEEDS LEAD is set)

An entry is flagged NEEDS LEAD when (i) a reviewer's view differs from the choice; (ii) Coder-A and Coder-B differ in
the stated choice or in the code (ruled or not, triggered or latent); (iii) the choice is not the literal text where
the text is explicit, or it is neither the literal nor the more conservative of the readings considered; or (iv) the
source itself leaves the decision to the lead ("the lead decides", "should be decided"). A flagged entry still
carries a proposed lean. Items already ruled in RF are listed with their ruling and are not re-proposed.

## NEEDS LEAD (10)

1. L01 TB-SPAN vs LB-2: A checks rule 5's row part on [t, max(t + L + h, tau + L)], B on [t, t + h + 2L]; the
   reviews and T-6 treat them as one reading; 0 cells on 20 dates (latent).
2. F06 FA-6 / B-OFI-1 (ruled R-B3-FD3a/c): MathReview SF-1 (written before the ruling) read A's computed junction
   term as the protocol's; the ruling chose (d); PipelineReview agrees with (d). Confirm only.
3. L11, L12, L13 (R-B3-D5, D3, D4): latent A != B left in Coder-B's label code (LB-8 skips TB instead of stopping;
   LB-13 does not mark F_TOB/F_MBP bad; pre-R records give invalid updates): ruled for A, no B fix ordered; 0
   triggering records or dates. Confirm no B fix is needed.
4. K01 C0 Lucid fee basis (0.560 or 0.920): P6.4's condition cannot be resolved from the A2 note; reports only.
5. K04 C3 limit-order window measured at the exchange, (t + L, t + L + W], against E.31's +50 ms; the coder asks for
   a decision; reports only.
6. K14 R5 AFML reproductions taken from secondary sources: whether they meet the prompt's "to the stated digits".
7. P12 PC-COUNT: the proof summary's counting rule for seeds with a failed configuration is stricter than P4.2's
   literal count; verdict-relevant; 0 failed fits in the 37 seed rows so far.
8. P14 PR-N6: whether a summary-only rewrite after an edit of run_proofs33.py triggers R-L3's rerun rule.
9. T07 T-8: LT3's "exceeds" read as P6.1's "covers" (21 >= 21); a pass judgment on a declared test.
10. F14 FA-14 vs B-RP-1: A takes F4.6's Hi/Lo over the as-of states (the last update at each ts_recv), B over every
    update including earlier same-ts_recv ones (dayB.py:351-375); the reviews treat them as one reading; 0 cells on
    20 dates (latent).

Entry count: 152 entries (F 34, L 23, S 21, P 26, K 14, D 21, T 13); see the coverage table at the end.
Ruled or decided entries (no new decision, listed with their ruling): F06, F11, F23, F26, F27 (R part), F30, L02, L11,
L12, L13 (D4), L14, L21, S10, S11, P03, P09, T12, T13. Proposed "agree" without a flag: the rest.

---------------------------------------------------------------------------------------------------------------

## F. Features (Coder-A FA-*, FC; Coder-B B-*, FC2)

### F01. FA-1 = B-OPEN-1 (junction of the open-time axis at the 07:45-08:30 pause)
- Src: FC:11; FC2:10-24.
- Text (P0.3): "Sample points inside a window are the minute marks t - j minutes, j = 1..k, on that open-time axis."
- Readings: the axis point shared by 07:45 and 08:30 is the instant 08:30:00 (pre-open book) or 07:45:00.
- Code: 07:45:00 on both sides (A's "(B)", B's "(a)"); marks ..., 07:44, 07:45, 08:31, ...; likewise 13:20 for the
  13:20/19:00 junction and the halt time on an early close.
- A/B: same. MathReview's own mapping gives the same marks (MathReview.md:46-48). B3 0 cells on every window feature.
- Reviews: PipelineReview.md:197-198 agree ("the alternative samples a book the protocol says to skip"), log.
- Data: the as-of book at 08:30:00 is invalid on 328 of 328 dates for ZM and ZS, 327 for ZL (FC2:14-16); under the
  08:30 reading F1.2 is invalid on rows 0-115 of every date and C.11 is 0 for the first 116 minutes (FC2:16-19).
- PROPOSED: agree. P0.3 skips the pause; 07:45 never samples a state formed in it, and P1.3's "windows that reach
  back across 08:30" then exist.

### F02. FA-2 (D-1 of the overnight session)
- Src: FC:12. B: no entry.
- Text (P0.3): "Overnight session: 19:00 on D-1 to 07:45 on D."
- Readings: D-1 = the calendar day before D, or the previous trade date.
- Code: calendar day (Monday's overnight starts Sunday 19:00), as measure31.day_bounds.
- A/B: B states nothing; B3 0 cells.
- Reviews: PipelineReview.md:199 agree, "no value depends on it".
- Data: none; the longest window reaches 06:40 on D (FC:12).
- PROPOSED: agree. Matches the trade-date window [D-1 16:00, D 16:00) of 0.3.

### F03. FA-3 (composites from the unclipped quantities, clipped last)
- Src: FC:13. B: no entry (featB clips each row as its last step, featB.py:4, 408).
- Text (P4 G4): "clipped to [-5, 5] after their own normalisation (38)"; F1.4 "dzC5 = zC30(t) - zC30(t - 5 min)",
  F1.6 "zC30 x vrel15".
- Readings: composites built from the clipped component columns, or from the unclipped named quantities then clipped.
- Code: unclipped zC30, gC, GAP, DB, rOpen; each listed feature clipped as its last step (feat33.py:1146).
- A/B: B's file is silent; B3 0 cells on F1.4, F1.6, F1.8, F4.8, F4.12, F4.13 (the readings differ only when a
  component exceeds 5 in absolute value, which the 20 dates may not contain).
- Reviews: PipelineReview.md:200-201 agree, "the text names the quantities", log.
- Data: none stated.
- PROPOSED: agree. The definitions name quantities, not feature columns; clipping is each feature's last step.

### F04. FA-4 = B-MBP-BAD (bad marking on the ZS and ZL MBP-1 books)
- Src: FC:14; FC2:55-59.
- Text (P0.3): mid "defined only when both sides exist, bid_1 < ask_1 and the book is not marked bad
  (F_MAYBE_BAD_BOOK)".
- Readings: per record; per batch (event); persistent until the next R (MBP-1 has one R per file series).
- Code: an MBP-1 book update is bad if any record of its batch carries the flag; ZM (MBO) keeps E.31's rule, bad until
  the next R. B adds: a side is missing when its price is UNDEF_PRICE or INT64_MIN; a defined price with size 0 counts
  as present.
- A/B: same rule; B3 0 cells.
- Reviews: PipelineReview.md:202 agree, "0 open-time flags measured".
- Data: 482 ZS and 392 ZL flagged front records over all 816 dates, none in open time (FC:14), so no window or mark
  depends on the choice. The more restrictive alternative (bad until the next R) would void weeks of ZS/ZL.
- PROPOSED: agree. Never uses the flagged event; no open-time state is affected.

### F05. FA-5 = B-MISS-1 (every sample point of a window must be defined)
- Src: FC:15; FC2:139-142.
- Text (P4 F1.1): "mean_30 and sd_30 over C(t - j min), j = 1..30, inside the segment"; F4.10 "SD of the 15 one-minute
  mid changes ending at t".
- Readings: use only the defined sample points; require all of them.
- Code: all required (and C(t), M(t)); otherwise invalid (G3). B lists F1.1, F1.2, F1.4, F2.1-F2.7, F4.1-F4.5, F4.10,
  F4.11, F4.12, and F1 points outside D's segment.
- A/B: same; B3 0 cells.
- Reviews: PipelineReview.md:203 agree, "conservative", log.
- Data: none stated beyond FC2:202-212 counts (F1.3 546, F1.7/F1.8 1,638, F3.7 73 invalid rows of 5,460).
- PROPOSED: agree. No imputation and no shortened window.

### F06. FA-6 = B-OFI-1 (OFI terms) -- SUPERSEDED by R-B3-FD3a, FD3b, FD3c (RF:67-83)
- Src: FC:16; FC2:100-112. Also B-WIN-1's sentence "An OFI term e_n of the first update after 08:30 is taken against
  the last update before it" (FC2:28-29), superseded by FD3a.
- Text (P4 F2.8): "summed over the MBP-1 updates in the window, e_n = 1{Pb_n >= Pb_{n-1}} qb_n - ..."; P0.3 "OFI sums
  (F2.8-F2.11, F3.1-F3.4) step through book updates".
- Readings (B3 FD3, B3_agreement.md:112): A computed every two-sided not-bad term and invalidated a window holding a
  non-computable term; B set non-valid-book terms to 0. Ruling: (a) the term of the first update after a skipped
  interval is in no window's sum (d); (b) a term whose state lacks a side or is bad makes the window invalid (A);
  (c) crossed or locked two-sided states use the literal e_n (A).
- Code: both sides implement the ruling (FC:16; FC2:100-112). B3 feat_r2_partial and full_r2: 0 cells on F2.8-F2.11,
  F3.1-F3.4.
- Reviews: PipelineReview.md:187-194 and 204 agree with the ruling. MathReview.md:147-159 (SF-1, written 02:19-02:40,
  before the 02:47 ruling) judged A's reading (compute the junction term when both states are two-sided) to match
  the protocol and B's 0 to be an imputation; it did not consider (d). B3_agreement.md:112 named "a term whose
  predecessor lies in skipped time ... is not computable, and a window holding one is invalid" as most conservative.
- Data: before the ruling, F2_9, F2_11, F3_2, F3_3 differed on almost every row (B3 full_r1).
- PROPOSED: ruled. Flag: NEEDS LEAD (i), confirm only: (d) differs from MathReview SF-1's preferred reading and from
  B3's "most conservative" reading (window invalid) for the junction term; RF:67-75 gives the reason for (d).

### F07. FA-7 = B-OFI-2 (a missing level m in the level-m OFI, F3.4)
- Src: FC:17; FC2:114-117.
- Text (P4 F3.4): "OFI^(m) is the level-m OFI (Xu, Gould and Howison 2018: the e_n of F2.8 on level-m prices and
  quantities)".
- Readings: a missing level as quantity 0 at an undefined price; or the term not computable.
- Code: not computable when either update has fewer than m (A: 5) levels on either side; IOFI5 invalid for windows
  holding that update.
- A/B: same (A states "fewer than 5", B "fewer than m"; F3.4 sums m = 1..5, so both invalidate the window); B3 0 cells
  on F3_4.
- Reviews: PipelineReview.md:205-206 agree, "B-OFI-2 reads 'lacks a side' at level m the same way".
- Data: none stated.
- PROPOSED: agree. The level-m price is undefined, so e_n cannot be evaluated; FD3 (b) forbids an imputed term.

### F08. FA-8 = B-DBAR-1 (Dbar_m reference of F3.4)
- Src: FC:18; FC2:155-156.
- Text (P4 F3.4): "Dbar_m = the trailing 20-date reference mean of (qb_m + qa_m)/2".
- Readings: which marks enter; a missing level.
- Code: marks where the ZM book has a valid mid; a missing level counts 0 depth.
- A/B: same; B3 0 cells.
- Reviews: PipelineReview.md:205-206 agree.
- Data: none stated.
- PROPOSED: agree. An invalid book has no depth to average; a missing level displays 0.

### F09. FA-9 = B-SEAS-1 (seasoned depth, F3.7-F3.8)
- Src: FC:19; FC2:61-68.
- Text (P4 F3): "the displayed quantity at a price level counting only orders whose last add or modify (by ts_recv) is
  at least 1.000 s before t."
- Readings: (a) levels of the full displayed book or of a seasoned-only book; (b) whether a size-decreasing M resets
  the time.
- Code: full displayed book's levels (m = 1 the touch), quantity over orders with last A or M ts_recv <= t - 1.000 s;
  every M resets; a C (partial cancel) does not; snapshot adds carry the snapshot ts_recv (B); invalid when the ZM mid
  at t is undefined or the denominator is 0.
- A/B: same; B3 0 cells on F3_7, F3_8.
- Reviews: PipelineReview.md:207 agree, "literal".
- Data: F3.7 invalid on 73 rows of the 20 dates (both seasoned touch quantities 0; FC2:207).
- PROPOSED: agree. Literal "at a price level" and "last ... modify".

### F10. FA-10 = B-SW-1 (sweep sets, F3.10)
- Src: FC:20; FC2:84-91.
- Text (P4 F3.10): "a buy sweep is a set of trade records sharing one ts_event that leaves the best ask level's
  displayed quantity at 0 (sell sweep: the best bid)".
- Readings: when "leaves ... at 0" is judged; aggressor side required; grouping.
- Code: a set = the front's T records sharing one ts_event (a maximal run); touch prices taken just before the first T;
  checked at each F_LAST inside the run; counted once per side at the first update where that level shows 0; time =
  that update's ts_recv; no aggressor condition.
- A/B: same; B3 0 cells on F3_10 (after FD1/FD2).
- Reviews: PipelineReview.md:208-209 agree, "causal".
- Data: 0 batches mix ts_events on 3 dates (FC:20).
- PROPOSED: agree. Causal (G1), checked only at event ends; the text sets no side condition.

### F11. FA-11 = B-FILL-1 + B-REM-1 (touch removals, F3.9) -- A's first coding SUPERSEDED by R-B3-FD5 (RF:91-93) and R-B3-FD7 (RF:118-125)
- Src: FC:21; FC2:70-82.
- Text (P4 F3.9): "contracts removed from the price level that was the best ask (Ca) or best bid (Cb) just before the
  record, by cancels, size-reducing modifies (the reduction) and modifies to another price (the full size) ...; fills
  are not removals (ProtocolReview DO-16)".
- Readings: whether unconsumed fill lots carry across batches (FD5); whether fill lots of an order not yet in the book
  count (FD7). Classification on the record-level book just before the record; time = the record's ts_recv; a modify
  to another price, side or size <= 0 removes the full size (both).
- Code: FD5 (clear at every F_LAST) on both sides. FD7: ruled for B (attribute fill lots by order id within the batch);
  fix in Coder-A running (STATE b3, 09:13).
- A/B: full_r2 F3_9 10 cells on 2022-09-01 (FD7); full_r3 pending.
- Reviews: PipelineReview.md:210 agree (follows FD5); B3_agreement.md:42-48 (FD7 favours B). PipelineReview_b.md:132-144 agree with FD7 (b); Coder-A applied it at 09:19 (feat33 b216f11ee2df, FC:45-49).
- Data: 17,115 of 17,115 C/M after an F of the same order lay in the same batch on 2022-02-15 (FC2:72-74); 1,472
  iceberg-style refreshes on 2021-01-19 (FC:21); FD7 2 events, 10 cells.
- PROPOSED: ruled; confirm in full_r3.

### F12. FA-12 = B-LAM-1 ("intervals that contain trades", F3.12)
- Src: FC:22; FC2:127-131.
- Text (P4 F3.12): "over those of the 60 one-minute intervals ending at t that contain trades".
- Readings: any T record; aggressor-signed T records only.
- Code: any ZM front T record (sides A, B, N); signed volume B - S uses sides B and A.
- A/B: same; B3 0 cells on F3_12 (after FD1/FD2).
- Reviews: PipelineReview.md:211-212 agree.
- Data: none stated.
- PROPOSED: agree. Literal "trades".

### F13. FA-13 = B-LAM-2 (intervals with an undefined mid change; minimum count; reference median)
- Src: FC:23; FC2:127-131.
- Text (P4 F3.12): "invalid with fewer than 30 such intervals (ProtocolReview DO-13)".
- Readings: an interval with trades but an undefined end mid counts toward 30 or not.
- Code: excluded and not counted. B also states: rank < 2 (all x equal) invalid; reference median over valid slopes,
  invalid if 0 or none. A's file is silent on these two, but its code does the same (feat33.py:678-680 slope NaN
  without regressor variation; feat33.py:937-940 a 0 or undefined median gives an invalid ratio).
- A/B: same main choice; B3 0 cells on F3_12.
- Reviews: PipelineReview.md:211-212 agree.
- Data: none stated.
- PROPOSED: agree. An undefined dM cannot enter the fit; fewer usable intervals makes the feature invalid sooner.

### F14. FA-14 = B-RP-1 (Hi and Lo of F4.6)
- Src: FC:24; FC2:133-135.
- Text (P4 F4.6): "Hi and Lo the max and min of M_ZM over [08:30, t] on D".
- Readings: all book updates; the as-of function M(u).
- Code: A: the state as of 08:30:00 and each update in (08:30, t] that is the last update at its ts_recv
  (feat33.py:474, `nxt[j] > t`). B: the valid mid as of 08:30:00 and EVERY valid book update with ts_recv in
  (08:30, t], including earlier updates that share a ts_recv with a later one (dayB.py:351-375, running max/min over
  all updates).
- A/B: DIFFER (latent). An intermediate update that shares its ts_recv with a later update is never the state "as of"
  any instant; B lets it set Hi or Lo, A does not. B3 0 cells on F4_6 on the 20 dates (the case did not set a new
  high or low there). Several updates per ts_recv are common (LC2:13-14; MathReview.md:173-175 N-4 on records).
- Reviews: PipelineReview.md:213 agree with FA-14 = B-RP-1 "as-of function", treating the two as one reading.
- Data: none measured.
- PROPOSED: needs the lead; lean A (P4 F4.6 "M_ZM over [08:30, t]" with 0.3's "'as of u' means the last book update
  with ts_recv <= u" is the as-of function; B's extra states are transient). Then Coder-B changes one condition.
  Flag: NEEDS LEAD (ii).

### F15. FA-15 = B-SIG-1 (sigma_X(D))
- Src: FC:25; FC2:147-151.
- Text (P0.3): "the SD of 1-minute mid changes of X over all 1-minute intervals inside 08:35-13:13 of the 20 trade
  dates before D (burn-in dates included as history), with valid mids at both ends, chained across rolls".
- Readings: fewer than 20 dates.
- Code: null unless all 20 dates exist; population SD of all pooled valid changes; sigma <= 0 (A: all changes 0)
  makes C.6 and every feature divided by it invalid.
- A/B: same; B3 sigma_ZM, ZS, ZL equal on 20 of 20 dates; MathReview.md:42-43 hand value equals both.
- Reviews: PipelineReview.md:214-215 agree, log.
- Data: OOF dates always have 20 previous dates.
- PROPOSED: agree. A short history gives no sigma rather than a different one.

### F16. FA-16 = B-REF-1 + B-OFI-REF (trailing 20-date references)
- Src: FC:26; FC2:153-156, 119-121.
- Text (P0.3): "its mean (or median where stated) over the minute marks 08:35-13:13 of the 20 trade dates before D".
- Readings: marks where the statistic is undefined.
- Code: pooled over the defined marks; undefined if none; numpy median. B: undefined with fewer than 20 dates; Obar
  over marks whose OFI window is computable (FD3 (b)); Obar_S/L undefined if ZS or ZL had no front on any of the 20.
- A/B: same; B3 0 cells.
- Reviews: PipelineReview.md:214-215 agree, log.
- Data: none stated.
- PROPOSED: agree. Undefined values carry no scale information.

### F17. FA-17 = B-F13-DATES (which dates F1.3 fits on)
- Src: FC:27; FC2:171-177.
- Text (P4 F1.3): "1-minute samples (08:35-13:13, minutes clear of P3.6 rule 3) of the 10 trade dates before D inside
  the current segment; at least 3 such dates or invalid".
- Readings: (i) dates in the segment among the 10 before D that contribute a sample; (ii) the 10 most recent
  in-segment dates, reaching further back.
- Code: (i), at least 3; a sample needs all three mids valid at a release-clear mark.
- A/B: same; B3 0 cells on F1_3.
- Reviews: PipelineReview.md:216-218 agree; "(ii) ... would reach further back and is less conservative", log.
- Data: F1.3 invalid on 546 rows of the 20 dates (2022-12-13 has 1 segment date, 2023-02-16 has 0; FC2:205).
- PROPOSED: agree. A date with no usable sample contributes nothing; (i) never reaches outside the 10 dates.

### F18. FA-18 = B-F13-REL (release window for an instant, F1.3)
- Src: FC:28; FC2:171-177.
- Text (P3.6 rule 3): "no span intersects [R - 2 min, R + 30 min]".
- Readings: closed or half-open window for an instant.
- Code: mark u excluded iff R - 2 min <= u <= R + 30 min for a release R of that date (closed).
- A/B: same; B3 0 cells on F1_3. MathReview.md:44-45 (NOPA 2022-09-15 removes 33 marks under the closed window).
- Reviews: PipelineReview.md:216-218 agree, log.
- Data: see MathReview.md:44-45.
- PROPOSED: agree. The closed interval removes the most minutes.

### F19. FA-19 (rank-deficient F1.3 fit)
- Src: FC:29; FC2:171-177 (same rule, plus "residual SD 0 is invalid").
- Text (P0.3): "an OLS fit is numpy.linalg.lstsq on centred regressors with an intercept, and its residual SD is
  sqrt(SSR / n)".
- Readings: use lstsq's minimum-norm answer, or invalid when rank < 3.
- Code: invalid when rank < 3 (feat33.py:843-845; featB.py:128-129). B also invalid when the residual SD is 0 (A's file
  silent; the division e(t)/sd_e is then a G3 zero denominator on both sides).
- A/B: same; B3 0 cells.
- Reviews: PipelineReview.md:219 agree.
- Data: none stated.
- PROPOSED: agree. Coefficients are not identified.

### F20. FA-20 = B-GAP-1 (dates for sd_gap and D's own gap across a front change)
- Src: FC:30; FC2:179-185.
- Text (P4 F4.7): "sd_gap = the SD of the same quantity over the 20 trade dates before D on which the ZM front was the
  same at both times (at least 10, or invalid)"; G2 for F1.7.
- Readings: (a) qualifying dates among the 20 before D; (b) the 20 most recent qualifying dates; and D's own GAP when
  D's front differs from the previous date's.
- Code: (a); D's own GAP invalid across a front change; F1.7: D' and its previous date in D's segment.
- A/B: same; B3 0 cells on F1_7, F4_7.
- Reviews: PipelineReview.md:220-221 agree, log.
- Data: F1.7 and F1.8 invalid on 1,638 rows (6 of the 20 dates; FC2:205-209), so C.11 is 0 on those dates.
- PROPOSED: agree. (a) matches "(at least 10, or invalid)" without reaching back; a cross-contract gap is a spread.

### F21. FA-21 (F4.11 undefined B(e), ties, and the units of t - e*)
- Src: FC:31. B: covered by B-MISS-1 (FC2:139-142) for F4.11, F4.12.
- Text (P4 F4.11): "B* the B(e) with the largest |B(e)| (latest e on ties)"; F4.12 "exp(-(t - e*)/5 min)".
- Readings: undefined B(e); exact or tolerant ties; t - e* in wall or open-time minutes.
- Code: invalid if any of the 14 B(e) is undefined; exact float ties, latest e; t - e* in open-time minutes.
- A/B: B's file silent on ties and units; B3 0 cells on F4_11, F4_12.
- Reviews: PipelineReview.md:222 agree.
- Data: none stated. (Near 08:35 the wall and axis readings of t - e* differ by 45 minutes; e is defined as t - j
  min on the axis, so t - e* = j* min is the literal value.)
- PROPOSED: agree. FA-5's rule, and e's own definition on the axis.

### F22. FA-22 = B-VOL-1 (contracts traded)
- Src: FC:32; FC2:123-125.
- Text (P4 C.5): "V_ZM(15) = ZM contracts traded in the 15-minute window ending at t"; F1.5 "(ZM trades from MBO, ZS
  and ZL trades from MBP-1 trade records)".
- Readings: include side-N trades; count MBP-1 F records.
- Code: all T records (A, B, N) of the front; MBP-1 F records not counted; TI and lam60's signed volume use B and A.
  A: trades before the ZM book's first R count.
- A/B: same; B3 0 cells on C_5, F1_5.
- Reviews: PipelineReview.md:223 agree, "literal", log.
- Data: none stated.
- PROPOSED: agree. Side-N trades are real trades; MBP-1 F records are undocumented (data facts 3.2).

### F23. FA-23 = B-REFILL-1 (refills, F3.11) -- SUPERSEDED by R-B3-FD4 (RF:84-89) and R-B3-FD6 (RF:108-116)
- Src: FC:33; FC2:93-98.
- Text (P4 F3.11): "a refill is an add at the same price and side within 100 ms (ts_recv) after that price level,
  while it was the touch, reached 0 displayed quantity through trades".
- Readings: FD4 (window at the F3.10 sweep update (A) or at the record whose fill reduction empties the current touch
  (B)): ruled (b). FD6 (a record whose reduction is partly fill and partly voluntary): ruled (a), A's `rest == 0`.
- Code: A implements both; B's FD6 fix running (STATE b4, 09:13).
- A/B: full_r2 F3_11 5,385 cells (FD6); full_r3 pending.
- Reviews: PipelineReview.md:224 agree (FD4); PipelineReview SF3 (lines 92-109) on FD6. PipelineReview_b.md:119-131 agree with FD6 (a); Coder-A pinned it by a test (FC:51-52).
- Data: about 1 refill a day differs under FD6 (2021-01-19: 4,013 vs 4,014), moving rbar_15 on every date
  (B3_agreement.md:34-41).
- PROPOSED: ruled; confirm in full_r3.

### F24. FA-24 = B-C34 (C.3 and C.4 on an invalid ZM book)
- Src: FC:34; FC2:144-145.
- Text (P4 C.3): "min(s_ZM(t), 5) in ticks"; C.4 "log(1 + qb_1 + qa_1) of ZM at t"; G3 "empty book side".
- Readings: values when the ZM book at t is crossed, locked, bad or one-sided.
- Code: invalid (0) unless the ZM mid at t is defined; C has no flag.
- A/B: same; B3 0 cells.
- Reviews: PipelineReview.md:225 agree.
- Data: none on rows: rows need a valid M_ZM(t) (P3.7) and entries need M_ZM(t) (R-B3-D2), so C.3/C.4 differ from
  the literal value only off the rows.
- PROPOSED: agree. A crossed book has no spread; no row is affected.

### F25. FA-25 = B-F49 (rOpen at 08:35)
- Src: FC:35; FC2:190-191.
- Text (P4 F4.9): "rOpen = (M_ZM(t) - M_ZM(08:35:00))/(sigma_ZM(D) sqrt(max(1, minutes from 08:35 to t))); 0 at 08:35".
- Readings: always 0 (valid) at 08:35, or 0 with the usual validity.
- Code: 0 at 08:35 when M_ZM(08:35) and sigma_ZM(D) are defined, else invalid.
- A/B: same; B3 0 cells.
- Reviews: PipelineReview.md:226 agree.
- Data: none (rows need M_ZM(t); sigma defined on OOF dates).
- PROPOSED: agree. Same validity on every row.

### F26. FA-26 = B-LT1-1 = T-5 = T-15 (LT1 cutoff mechanics and history dates) -- RULED by R-L9 (RF:132-138)
- Src: FC:36; FC2:193-200; TC:13, 39.
- Text (P4.1 LT1): "recompute every feature from ALL input streams (ZM MBO, ZS and ZL MBP-1, and the definitions)
  truncated at ts_recv <= t".
- Readings: (a) history from production pass 1; (b) re-stream D and its 21 history dates; (c) (a) with a (b) subset.
  A's C.7 uses only the front's last definition with ts_recv <= 08:30:00 CT on D, so a cutoff before 08:30 on D is
  refused (A).
- Code: A defaults to (b) (--prior recompute); B reuses history raws only when their window ends at or before the
  cutoff (asserted); B's 10-28 fix keys the truncated raw cache by code_sha12.
- A/B: different mechanics, identical by construction (FC2:196-197).
- Reviews: PipelineReview.md:227-228 agree, "the lead's choice should be logged"; PipelineReview N1 (lines 113-119). PipelineReview_b.md:183-188 (build_cutoff refuses a cutoff before 08:30 on D; prior recompute or production).
- Data: none.
- PROPOSED: ruled: (b) on all 200 draws, (a) reported beside it (R-L9).

### F27. FA-27 = B-BOOKBAD (E.31 book driver for the ZM features)
- Src: FC:37; FC2:50-53.
- Text (P0.3): "Book: ZM from MBO (mbo_book31.Book, full displayed depth)".
- Readings: which E.31 driver rules apply; an R record carrying F_MAYBE_BAD_BOOK.
- Code: records before the first R ignored; F_MAYBE_BAD_BOOK, F_TOB, F_MBP mark the book bad until the next R; A and M
  with side N skipped; R record with the flag: clear, then mark bad (R-B3-D1). B's feature replay marked before the
  clear: ruled R-B3-N10 (RF:127-130), fix in Coder-B running (STATE b4).
- A/B: same after N10; 0 R records carry the flag on 816 dates (tests_b3/count_d1.py).
- Reviews: PipelineReview.md:229 agree, "with D1"; PipelineReview N10 (lines 166-175). PipelineReview_b.md:145-150 agree with N10.
- Data: 5,417 flagged records on 58 dates, all before the date's first R (B3_agreement.md:81-86).
- PROPOSED: agree (the R-record part is ruled by D1 and N10).

### F28. FA-28 (files in code_sha12)
- Src: FC:38. B: own sha (FC2:222-225, no deviation).
- Text (INTERFACE 4.1, not the protocol): "<code_sha12> = first 12 hex of the sha256 of the concatenated feature code
  files".
- Readings: which files.
- Code: feat33.py, build_features33.py, mbo_book31.py; data33/cal33/guard33 listed with their sha256 in manifest.json.
- A/B: n/a.
- Reviews: PipelineReview.md:230 agree, "see SF2 for the rest of the freeze list".
- Data: none (file layout; P0.2 "Details that cannot affect an outcome ... are E.33's").
- PROPOSED: agree; the freeze list (SF2, FreezeCoder) covers the dependencies.

### F29. FA-29 (exact integer crush)
- Src: FC:39. B: no entry (float route within G7).
- Text (P4 F1): "C(u) = 11 M_ZL(u) + 2.2 M_ZM(u) - M_ZS(u)".
- Readings: float in natural units, or exact integers.
- Code: C2 = 11 raw2_ZL + 2.2 raw2_ZM - raw2_ZS in 1e-9 units, C = C2 / 2e9 cents/bu.
- A/B: same formula; B3 0 cells on F1 (MathReview.md:55: F1.1 A 2.3e-13 relative from the hand value).
- Reviews: PipelineReview.md:231 agree.
- Data: none.
- PROPOSED: agree. Same formula without float error.

### F30. FA-30 = B-EARLY-1 + B-LATE-1 (actual session per date) -- A's first coding SUPERSEDED by R-B3-FD1/FD2 (RF:60-65)
- Src: FC:40; FC2:33-44.
- Text (P0.3): "the last k minutes of time during which X was open, ending at t (the 07:45-08:30 pause and the
  13:20-19:00 close are skipped; overnight minutes count)".
- Readings: the regular schedule on every date (A first) or the actual session (B). Ruled: actual session.
- Code: both: early halt cuts the day session at 12:05 and a closed t maps to the last open mark; on scheduled late
  opens the window reaches into the previous trade date's day session; F1 samples there need D's segment (G2).
- A/B: same; B3 feat_r2_partial and full_r2 0 cells on C_5, F2, F3.10, F3.12, F1 and 2021-07-06's rows.
- Reviews: PipelineReview.md:187-194, 232 agree; MathReview.md:161-166 (N-1) named the difference.
- Data: 9 dates (FC:40): 2020-12-24; 2021-11-26, 2022-11-25, 2023-11-24; 2021-07-06, 2022-07-05, 2023-07-05,
  2023-12-26, 2024-01-02.
- PROPOSED: ruled.

### F31. FA-31 (instant states as of the wall minute; windows on the mapped axis)
- Src: FC:41. B: B-EARLY-1 (FC2:33-38: "M(t) itself is as of the wall time t ... sigma use the wall-clock marks").
- Text (P0.3): sigma_X "over all 1-minute intervals inside 08:35-13:13 ... with valid mids at both ends"; F1.7 "C(08:35:00
  on D) - C(13:15:00 on the previous trade date)".
- Readings: with FD1/FD2, an instant state at a closed minute read at the mapped mark (the halt) or as of the wall
  minute.
- Code: instant states (sigma's mids, Dbar's depths, F1.3's samples, the 08:35 and 13:15 levels) as of the wall
  minute; only windows and their sample points use the mapped mark.
- A/B: same; B3 sigma and F3.4's Dbar equal; F1.7 0 cells.
- Reviews: PipelineReview.md:233-234 agree ("keeps sigma and Dbar free of 68 copies of a halt state"), log;
  PipelineReview N9 (lines 158-165): the production label build must read sigma from the frozen store's _day.
- Data: after the 12:05 halt every wall-minute state to 13:13 is not a valid book (68 of 68 minutes on 2020-12-24 and
  2022-11-25; FC:41), so these minutes leave sigma and Dbar.
- PROPOSED: agree. The definitions name clock instants; the ruling addresses windows.

### F32. FA-32 = B-EARLYIDX (clock positions of the decision time)
- Src: FC:42; FC2:46.
- Text (P4 C.1): "tod = (t - 08:35)/(13:13 - 08:35) in minutes"; C.9 "C.8 x 1{t >= 11:30}"; F4.13 "LATE = rOpen x
  1{t >= 12:15}".
- Readings: wall minutes or mapped open minutes for a closed t.
- Code: wall minute index i (t = 08:35 + i min); C.9 is i >= 175, F4.13 i >= 220.
- A/B: same; B3 0 cells.
- Reviews: PipelineReview.md:235-236 agree, "differs only on excluded dates", log.
- Data: none (differs only after an early halt, on excluded dates).
- PROPOSED: agree. Clock positions, not windows.

### F33. B-WIN-1 (what a window sum covers)
- Src: FC2:26-31; A's equivalent inside FA-1 (FC:11: "sums records in (mark p-k, mark p] that lie in open time").
- Text (P0.3): "the 07:45-08:30 pause and the 13:20-19:00 close are skipped".
- Readings: records with ts_recv in the wall interval (wall(t - k), t] including the pause; or open time only.
- Code: open time only on both sides (volume, OFI, removals, sweeps, refills, trade counts). B-WIN-1's OFI sentence
  is superseded by FD3a (F06).
- A/B: same; B3 0 cells.
- Reviews: PipelineReview.md:236 agree.
- Data: identical except records stamped exactly 07:45:00.000 or 08:30:00.000 (FC:11).
- PROPOSED: agree. No closed-time record enters a window.

### F34. B-F15 (vrel15 validity, F1.5)
- Src: FC2:187-188. A: no entry.
- Text (P4 F1.5): "vrel15 = V_ZM(15)/(V_ZM(15) + V_ZS(15) + V_ZL(15))".
- Readings: (implicit) a front unknown; the segment check.
- Code (B): invalid when any of the three fronts is unknown or the denominator is 0; no segment check (G2 binds only
  the crush and its residual).
- A/B: A's file silent; B3 0 cells on F1_5.
- Reviews: PipelineReview.md:236 agree.
- Data: none stated.
- PROPOSED: agree. G3 zero denominator; G2 names only F1's level quantities.

(B-C7 = CAL-1, B-C10 = CAL-6, B-SEG-1 = CAL-7: section D.)

---------------------------------------------------------------------------------------------------------------

## L. Labels (Coder-A LabelCoder IDs, LC; Coder-B LB-*, LC2)

### L01. TB-SPAN vs LB-2 (span that rule 5's row part checks for a TB row)
- Src: LC:10; LC2:19-29.
- Text (P3.6): "A label span is [t, t + L + h min] (FH) or [t, tau + L] (TB)." ... "a trade may be entered at t only
  if the possible span [t, t + L + h min] meets them" ... "A row is kept only if its whole possible span lies inside
  D's day session on one ZM front and meets every rule"; rule 5 "(row rule) no span with a book update at which the ZM
  book lacks a bid or an ask or is marked bad".
- Readings (A's labels): (a) realised [t, tau + L]; (b) possible [t, t + L + h]; (c) their union
  [t, max(t + L + h, tau + L)]; (d) the whole possible TB span [t, t + 2L + h].
- Code: A chose (c) (lab33.py:612-615, `max(poss_end, span_end)`), and rules 1-3 on [t, t + L + h]. B chose (d) for
  the row rules (labB.py:256-260 `possible_span_end` = t + h + 2L for TB; LC2:24-27 calls it "(c)"); entry rules on
  [t, t + L + h].
- A/B: DIFFER (latent). B also removes a TB row with a one-sided or bad update in (max(t + L + h, tau + L),
  t + h + 2L] (at most L = 1 s). Rules 2-3 give identical results on the minute grid (both coders; PipelineReview N6).
  B3 0 cells on T15/T30 row_ok; MathReview.md:176-177 (N-5): A's union and the possible span agree on 263 rows of D1.
- Reviews: PipelineReview.md:70 (SF1 list "TB-SPAN = LB-2") and 237 (agree with "TB-SPAN (c)"), and PipelineReview
  N6 (lines 140-145) treat the two as one reading; TC:14 (T-6) builds LT2 on "max(t + L + h, realised end) (both
  coders' union reading)". No reviewer noted B's wider end.
- Data: 0 rows removed by the extra part on the 20 dates (LC2:29).
- PROPOSED: needs the lead. A's (c) is the union of the two spans the text names; B's (d) reads "whole possible span"
  as every span a TB label can have and is the superset (stricter). Lean (d), the more conservative where the text
  does not settle it (P0.2); then lab33's check end and LT2's TB span (T-6) change; under (c) labB changes.
  Flag: NEEDS LEAD (ii).

### L02. R5-CROSSED = LB-3 (entry at a crossed or locked book at t) -- SUPERSEDED by R-B3-D2 (RF:98-100)
- Src: LC:11, 49-53; LC2:31-41.
- Text (P3.6): "a trade may be entered at t only if ... the ZM book at t has both sides and is not marked bad";
  P3.7 rows need "a valid M_ZM(t)".
- Readings: (a) entry needs both sides and not bad (limit test skipped or failed on a crossed book); (b) entry needs
  M_ZM(t) defined. Ruled (b) (B's).
- Code: both require M_ZM(t) for entry_ok on every date (A changed, lab33 ff0181fc391c).
- A/B: same; lab_r3 0 cells.
- Reviews: PipelineReview.md:187-194 agree.
- Data: 0 minutes on the 20 dates; cannot arise on real data (limits on all 816 dates).
- PROPOSED: ruled. (B's INTERFACE difference LC2:31-41 is the ruled rule.)

### L03. LOCKED-LITERAL = LB-17 (which updates in the span, and crossed or locked updates)
- Src: LC:12; LC2:161-167.
- Text (P3.6 rule 5): "no span with a book update at which the ZM book lacks a bid or an ask or is marked bad".
- Readings: (a) literal; (b) also remove spans with a crossed or locked quote.
- Code: (a) on both; B: updates with ts_recv in the closed [t, span end]; the state as of t is covered by the
  M_ZM(t) rule.
- A/B: same choice (span end differs: L01); B3 0 cells.
- Reviews: PipelineReview.md:237-241 agree ("LOCKED-LITERAL is the literal text"; lab33 asserts P3.3's "both cannot
  be positive", lab33.py:598-599, which only an entry on a crossed book could break, and D2 forbids that).
- Data: 0 on the 20 dates.
- PROPOSED: agree. "Locked" in the heading is the limit-lock the text already covers.

### L04. TB-M0 = LB-7 (TB row when M_ZM(t + L) is undefined)
- Src: LC:13; LC2:69-74.
- Text (P3.4): "m0 = M_ZM(t + L)".
- Readings: (a) no row; (b) the last defined mid.
- Code: (a); counted (A `tb_m0`, or `r5_locked_span` when a bad update exists; B `label_undef`); the entry minute
  stays and the simulation marks it TB-not-made (flag 32, P3.2).
- A/B: same; B3 0 cells.
- Reviews: PipelineReview.md:237 agree.
- Data: 0 on the 20 dates.
- PROPOSED: agree. No label without its anchor; mirrors P3.2's TB rule.

### L05. ENTRY-WINDOW = LB-4 (planned exit time of an entry not made)
- Src: LC:14; LC2:43-52.
- Text (P3.2): "an entry with no such update before its planned exit time is not made (counted)"; P3.8 "FH at t + h,
  TB at tau".
- Readings: FH t + h or t + h + L; TB t + L + h or that plus L; strict or not.
- Code: FH t + h, TB t + L + h, strictly before.
- A/B: same; B3 0 cells.
- Reviews: PipelineReview.md:237 agree; PipelineReview N5 (lines 136-139) "Conservative (fewer fallback entries); B
  agrees (LB-4); log it".
- Data: no entry fallback fired on the 20 dates (LC2:52).
- PROPOSED: agree. Fewer partial-hold trades.

### L06. ENTRY-FLAGS = LB-10 (flag bits 1 and 2)
- Src: LC:15; LC2:88-96.
- Text (INTERFACE 4.2, not the protocol): "1 entry fallback fired, 2 exit fallback fired, 4 exit marked at the limit
  price, 8 exit marked at the last valid touch, 16 entry not made ..., 32 TB entry not made".
- Readings: bits 1/2 whenever the fallback rule was invoked, or only when a fallback fill happened.
- Code: invoked (1|16 for an entry not made; 2|4 or 2|8 for a marked exit; 32 or 1|32 for TB).
- A/B: same; B3 0 cells on flags.
- Reviews: PipelineReview.md:237 agree.
- Data: flags 0 on the 20 dates (LC:59).
- PROPOSED: agree. Flags only, no label effect.

### L07. EXIT-MARK-TIME = LB-11 (time of a marked exit)
- Src: LC:16; LC2:98-102.
- Text (P3.2): "an exit with none before 13:20:00 is marked at the front's limit price on the side that blocked it".
- Readings: s_exit_ns = 13:20:00 CT, -1, or the planned exit time.
- Code: 13:20:00 CT; a fallback exit fill must come strictly before 13:20:00 (B).
- A/B: same; B3 0 cells.
- Reviews: PipelineReview.md:237 agree.
- Data: none on the 20 dates.
- PROPOSED: agree. The position cannot close earlier; no later trade follows on D.

### L08. FILL-TIME = LB-5 (time of a normal fill)
- Src: LC:17; LC2:54-61.
- Text (P3.2): "A market buy decided at time u fills at ask_1 of the ZM book as of u + L"; P4.1 LT7 "the production
  fill time (t + L, or the fallback fill update of P3.2)".
- Readings: u + L, or the ts_recv of the as-of update.
- Code: u + L without a fallback; the fallback update's ts_recv otherwise.
- A/B: same; B3 0 cells.
- Reviews: PipelineReview.md:237-238 agree.
- Data: none.
- PROPOSED: agree. LT7's own wording; never earlier than the as-of update.

### L09. TB-TIE = LB-9 (opposite barriers at the same ts_recv)
- Src: LC:18; LC2:82-86.
- Text (P3.4): "tau = min(tau_up, tau_dn, t + L + h min) ... y^TB(t) = +1 if tau = tau_up".
- Readings: (a) first barrier-hitting update in record order; (b) by time, +1 first.
- Code: (a); B counts same-ts_recv ties (`tb_same_time_ties`).
- A/B: same; B3 0 cells.
- Reviews: PipelineReview.md:238 agree.
- Data: 0 ties on the 20 dates.
- PROPOSED: agree. "the first ZM book update" is an order statement.

### L10. TB-EXACT (exact barrier comparison)
- Src: LC:19. B: no entry.
- Text (P3.4): "M_ZM(u) >= m0 + b(t)".
- Readings: float m0 + b, or the exact form.
- Code (A): (S_u - S_0) >= 2b in float64 with S = bid_1 + ask_1 integer ticks.
- A/B: B's file silent; B3 0 cells on T15/T30.
- Reviews: PipelineReview.md:238 agree.
- Data: none.
- PROPOSED: agree. Equals the real-number comparison.

### L11. TB-SIGMA vs LB-8 (TB when sigma_ZM(D) is undefined) -- RULED R-B3-D5 (RF:102-106)
- Src: LC:20, 54; LC2:76-80; TC:22-26.
- Text (P3.4): "half-width b(t) = kappa x sigma_ZM(D) x sqrt(h) ticks"; "For b(t) > 0 ...".
- Readings: A stops the label build (LabelError); B removes TB entries and rows on D (`tb_sigma`, counted).
- Code: ruled for A; B's labB unchanged (no B fix was ordered).
- A/B: DIFFER (latent). SearchCoder S5 also stops on a missing sigma (consistent with A).
- Reviews: PipelineReview.md:187-194 agree (D3-D5); PipelineReview.md:238 "TB-SIGMA (stop)".
- Data: does not arise: sigma is defined on every OOF date (FC:25); defined on all 20 B3 dates (LC2:79).
- PROPOSED: ruled. Flag: NEEDS LEAD (ii), confirm only that B's latent difference may stay (B's label code is a
  comparison implementation; no real date can trigger it).

### L12. BOOK-BAD-FLAGS vs LB-13 (F_TOB / F_MBP on MBO records) -- RULED R-B3-D3 (RF:102-106)
- Src: LC:22; LC2:117-121; FC2:50-53 (B's features do mark).
- Text (P0.3): "the book is not marked bad (F_MAYBE_BAD_BOOK)".
- Readings: only F_MAYBE_BAD_BOOK; also F_TOB/F_MBP as E.31.
- Code: A's labels and both feature builders mark the book bad (E.31); B's labels do not (counted).
- A/B: DIFFER (latent) in the label code; ruled for A; no B fix ordered.
- Reviews: PipelineReview.md:187-194 agree (D3). PipelineReview_b.md:111-115 (N14): "Record it in the readings file beside D3 (SF1) so the test stage does not read B's label replay as the ruled rule."
- Data: 0 such records in Z1 (data facts 1.5; B3_agreement.md:92-93).
- PROPOSED: ruled. Flag: NEEDS LEAD (ii), confirm only (as L11).

### L13. BOOK-UPDATE = LB-1 (which records make a book update) and D4 (records before the first R)
- Src: LC:23; LC2:9-17; B3_agreement.md:94-98.
- Text (P0.3): "the book state after a record that carries F_LAST (the end of one event batch) ... A book update's time
  is the ts_recv of its F_LAST record".
- Readings: every F_LAST record (T, F, N included) or only F_LAST records that changed the book; several updates per
  ts_recv; records before the first R.
- Code: every F_LAST record, every update kept in record order; "as of u" the last one; first-touch and the rule 5
  row check visit each. Before the first R: A emits no update, B emits an invalid one (D4).
- A/B: same rule; D4 differs in the update count only (2021-01-19: A 401,300, B 401,355 F_LAST records; 58 before the
  start on both); ruled "no effect" (RF:102-106).
- Reviews: PipelineReview.md:238-239 agree.
- Data: no as-of state in 08:35-13:20 can differ (both books start at the evening snapshot).
- PROPOSED: agree (literal; FixVerifier R-W2-6). Flag: NEEDS LEAD (ii), confirm only for D4 (as L11).

### L14. LB-12 (book driver for the labels) and A's D1 change -- R record part RULED R-B3-D1 (RF:95-96)
- Src: LC2:104-115; LC:45-48.
- Text (P0.3): "Book: ZM from MBO (mbo_book31.Book, full displayed depth)"; mbo_book31: "F_MAYBE_BAD_BOOK marks the
  book bad until the next R" (as quoted LC2:106-107).
- Readings: records before the first R; an R carrying the flag (clear then mark, or mark then clear); A/M with side N;
  T/F/N.
- Code: both: records before the first R not applied; flag on an R record: clear, then mark bad (A changed, lab33
  ff0181fc391c); A/M side N skipped and counted; T, F, N change nothing.
- A/B: same after D1; lab_r3 0 cells.
- Reviews: PipelineReview.md:187-194 agree (D1).
- Data: 1,752 records before the first R on the 20 dates (LC2:109-110); 0 R records carry the flag on 816 dates.
- PROPOSED: ruled (D1); the rest agree.

### L15. W-SUM = LB-18 (sample weights)
- Src: LC:21; LC2:169-178.
- Text (P3.7): "c_m = the number of rows of the same label type and date whose span intersects m by more than one
  second ... u_i = the mean of 1/c_m over the intervals m that span_i intersects by more than one second".
- Readings: np.mean, sequential sum or fsum; strict or not; which rows count.
- Code: math.fsum(1/c_m)/n; overlap > 1 s strict; intervals the clock minutes; only row_ok rows enter c_m (B; A's file
  says rows).
- A/B: same; B3 w within 1e-12 relative on every row.
- Reviews: PipelineReview.md:238 agree ("W-SUM (fsum)").
- Data: none (weights only).
- PROPOSED: agree. Order-free and correctly rounded; strict "more than one second" is the text.

### L16. REPLAY-END (labels replay to 13:20)
- Src: LC:24. B: LC2:98-102 (a fallback exit fill strictly before 13:20:00).
- Text (P3.2): "an exit with none before 13:20:00 is marked".
- Readings: replay to 16:00 or to 13:20.
- Code (A): records with ts_recv < 13:20:00 CT (data33.load_zm cutoff 13:20:00 - 1 ns).
- A/B: same effect; B3 0 cells.
- Reviews: PipelineReview.md:239 agree.
- Data: none.
- PROPOSED: agree. No label or fill looks at or after 13:20:00.

### L17. GRID-R1R2 (rules 1-2 on the grid)
- Src: LC:25.
- Text (P3.6): "1. Open: no span starts before 08:35:00 ... 2. Close: every span ends by 13:13:00".
- Readings: none (implemented and counted).
- Code: never fire on G_h(D) (t >= 08:35; t + L + h <= 13:12:01; TB tau + L <= 13:12:02).
- A/B: same; B3 0 cells.
- Reviews: PipelineReview.md:239 agree.
- Data: 0 removals.
- PROPOSED: agree.

### L18. LIMIT-ORDER (malformed limit pair)
- Src: LC:26.
- Text (P3.6 rule 5): "If no such record exists, or either limit field of it is UNDEF_PRICE (mbo_book31.UNDEF_PRICE,
  2^63 - 1) or 0, the limit-proximity part is skipped for D and the date is counted".
- Readings: none; a guard.
- Code (A): DayInputs raises if HL <= LL or if UNDEF/0 limits are passed instead of None.
- A/B: n/a; B asserts limit fields are tick multiples (LC2:184).
- Reviews: PipelineReview.md:239 agree.
- Data: none (limits present on all 816 dates).
- PROPOSED: agree. A malformed pair stops rather than mis-excluding.

### L19. MIDMOVE-EXCL (mid_move on excluded dates; reported-only column)
- Src: LC:27.
- Text (P6.2, reported only): "the hit rate of the realised sign of the mid move over [t + L, t + L + h] given the
  chosen side"; lead follow-up 2026-10-27 as quoted LC:27.
- Readings: (a) NaN on P1.4-excluded dates; (b) filled on every grid minute of every date.
- Code (A): (b); book replayed on excluded dates; flags stay false there.
- A/B: B's labels have no mid_move column (MathReview.md:171-172 N-3); not compared (B3_agreement.md:17-18).
- Reviews: PipelineReview.md:239 agree.
- Data: none for labels; P8 never uses it.
- PROPOSED: agree. Reported-only; the lead's own follow-up text.

### L20. LB-6 (release window edges for label spans)
- Src: LC2:63-67. A: same rule in lab33 (LC:10 notes the edges are whole minutes).
- Text (P3.6 rule 3): "no span intersects [R - 2 min, R + 30 min]".
- Readings: closed or half-open edges.
- Code: closed at both ends; with h = 5 the excluded starts are 10:53 to 11:30 (38 minutes).
- A/B: same; B3 0 cells; MathReview.md:33 checked the F05 flags at 10:52, 10:53, 11:29, 11:30, 11:31 on 2023-08-11.
- Reviews: PipelineReview N6 (lines 140-145) "R - 2 min, R + 30 min, 08:35 and 13:13 are minute marks".
- Data: as stated.
- PROPOSED: agree. More minutes removed at the edges.

### L21. LB-15 and LabelCoder's finding (stale weekly limit bands in rule 5) -- DECIDED by the user, V52.2
- Src: LC2:133-144; LC:29-38.
- Text (P3.6 rule 5): "HL and LL are the high and low limit prices of the front's last definition record with ts_recv
  <= 08:30:00 CT on D".
- Readings: none (implemented literally; a data finding).
- Code: literal on both sides.
- A/B: same; B3 0 cells.
- Reviews: PipelineReview N3 (lines 125-130): "record this in the readings file as a data note (not a reading)";
  MathReview.md:34-35 (D4 = 2021-04-01 hand check).
- Data: the definitions' limit fields change only on Sundays; on the 20 dates r5_limit removes 497 F05 minutes
  (2021-07-09 all 273, 2021-04-01 82, 2022-06-03 142); 2021-07-01 loses all 263 F15 minutes (LC:31-36).
- User decision (docs/DECISIONS.md:1083-1086): "price-limit rule 5 is kept for discovery as written. E.33b counts the
  affected dates and minutes on all 796 dates."
- PROPOSED: agree; carry as a data note with the 796-date count (STATE b14).

### L22. LB-16 (sigma_ZM(D) source and replay details in B's labels)
- Src: LC2:146-159.
- Text (P0.3): sigma_X(D) as in F15.
- Readings: read sigma from B's features _day or compute it.
- Code (B): own sigma (folder absent at 15:07 PDT); 279 marks, 278 intervals; each history date's own front; replay
  keeps ts_recv <= 13:13:00 inclusive (a first build at 13:13:00 - 1 ns was discarded). A's labels read sigma from A's
  features _day (B3_agreement.md:22-23).
- A/B: same values; B3 sigma_ZM equal A feature = B feature = B label on 20 dates.
- Reviews: PipelineReview N9 (lines 158-165): the production label build must point --features-sha at the frozen
  store's _day.
- Data: none.
- PROPOSED: agree.

### L23. LB-19 (limit-proximity arithmetic)
- Src: LC2:180-184. A: lab33.py:387-393 (PipelineReview N4).
- Text (P3.6 rule 5): "M_ZM(t) >= HL - 0.02 c or M_ZM(t) <= LL + 0.02 c, where ... c = (HL + LL)/2".
- Readings: exact integer or float.
- Code: B 50 (bid + ask) >= 99 HL - LL and <= 101 LL + HL; A 100 (bid + ask) >= 198 HL - 2 LL and <= 202 LL + 2 HL.
- A/B: same algebra; B3 0 cells.
- Reviews: PipelineReview N4 (lines 132-134) re-derived A's inequalities: correct.
- Data: none (differs from float only at an exact tie).
- PROPOSED: agree.

---------------------------------------------------------------------------------------------------------------

## S. Search engine (SearchCoder S1-S21, SC; single implementation, so no A/B comparison)

### S01. S1 (a class with no training row)
- Src: SC:11-17.
- Text (P3.5): "mu_long_k = the weighted mean of N_long over training rows with y = k"; P5 "A configuration with any
  fold whose fit raises an error, or yields probabilities that are not finite, is failed".
- Readings: (a) the fit raises, configuration failed; (b) mu_k = 0; (c) drop the class.
- Code: (a): FitError (also for an LGBM inner block without a class); fold<k>.FAILED.
- Reviews: PipelineReview.md:242 agree; SearchReview.md:204-206 "consistent with the classes_ check".
- Data: should never fire at about 170,000 rows.
- PROPOSED: agree. No invented magnitude enters EV.

### S02. S2 ("SD 0" in standardisation)
- Src: SC:19-22.
- Text (P4 G5): "a training SD of 0 makes the feature 0 in that fold".
- Readings: computed SD exactly 0 only; or exact constant (max == min) as well.
- Code: SD 0 when the training column is exactly constant or its computed SD is 0; the feature is 0 in training and
  evaluation rows.
- Reviews: PipelineReview.md:242 agree; SearchReview.md:187-193 confirms the rule in code.
- Data: constant columns (for example the proofs' C_11-C_14) are zeroed rather than amplified.
- PROPOSED: agree. A float SD of 1e-17 for a constant would blow noise up to +-1.

### S03. S3 (an entry not made and the 20-entry cap)
- Src: SC:24-30.
- Text (P3.2): "an entry with no such update before its planned exit time is not made (counted)"; P3.8 "When flat at t
  ..., and fewer than 20 entries have been made on D, apply P3.5."
- Readings: (a) flat, next minute decides, not counted; (b) wait for the planned exit; (c) count the attempt.
- Code: (a); not-made attempts to not_made.parquet.
- Reviews: PipelineReview.md:242 agree; PipelineReview N2 (lines 121-123) "Literal ... A stricter reading (count
  attempts) would be equally defensible"; SearchReview.md:145-150 (N6) literal and causal; (a) and (b) coincide.
- Data: flags 0 on the 20 B3 dates, so negligible.
- PROPOSED: agree. Literal "entries ... made"; no future value enters.

### S04. S4 (exit fill time drives the next decision)
- Src: SC:32-34.
- Text (P3.8): "the next decision is the first grid minute at or after the exit fill time".
- Readings: none (listed for visibility).
- Code: the first grid minute with t_ns >= s_exit_ns.
- Reviews: PipelineReview.md:242 agree; SearchReview.md:207-214 (searchsorted left).
- Data: none.
- PROPOSED: agree.

### S05. S5 (sigma_ZM(D) missing for the terciles)
- Src: SC:36-39.
- Text (P8 G5 d): "the 796 OOF dates sorted by sigma_ZM(D) ascending (ties by date), ranks 1-265, 266-530 and 531-796".
- Readings: stop, or define terciles another way.
- Code: an OOF date without a finite positive sigma_zm stops the load (ValueError).
- Reviews: PipelineReview.md:243 agree ("missing sigma stops").
- Data: none (sigma defined on every OOF date).
- PROPOSED: agree. A data fault is for the lead, not a silent gate failure.

### S06. S6 (P6.2's quarters)
- Src: SC:41-44.
- Text (P6.2): "per-fold, per-quarter and per-month sums"; P8 G5 (a) "(Dec-Feb, Mar-May, Jun-Aug, Sep-Nov; the first
  without the burn-in dates)".
- Readings: calendar quarters or G5 (a)'s seasonal quarters.
- Code: G5 (a)'s, keyed by the start month ("2020-12" = Dec 2020-Feb 2021).
- Reviews: PipelineReview.md:243 agree; SearchReview.md:216-221 (13 quarters on the OOF dates).
- Data: none (reported statistics).
- PROPOSED: agree. One quarter definition for P6.2 and G5.

### S07. S7 (reported-only rho and top decile)
- Src: SC:46-54.
- Text (P6.2): "the Pearson correlation rho over all OOF rows between the chosen side's EV and the realised net of that
  side; ... the mean realised net in the top decile of max(EV_long, EV_short)".
- Readings: rows, chosen side, ties, decile size.
- Code: row_ok rows with their fold's prediction; side with the larger EV ignoring the 0 threshold (exact ties
  dropped); net n_long/n_short; top ceil(n/10) rows by max EV, ties by (date, i); also rho over trades taken.
- Reviews: PipelineReview.md:243 agree.
- Data: none (never used by P8).
- PROPOSED: agree.

### S08. S8 (mid-sign hit rate)
- Src: SC:56-68.
- Text (P6.2): "the hit rate of the realised sign of the mid move over [t + L, t + L + h] given the chosen side".
- Readings: population; NaN and zero moves.
- Code: trades taken; hit = mid_move has the side's sign; NaN and exact 0 left out and reported (n_used + n_nan +
  n_zero = trades); None when no trade is usable; a column on some dates only stops the load.
- Reviews: PipelineReview.md:243 agree.
- Data: none (reported only).
- PROPOSED: agree.

### S09. S9 (code-version folders)
- Src: SC:70-73.
- Text (INTERFACE 4.1, not the protocol): tables keyed by <code_sha12>.
- Readings: which folder to load.
- Code: the only 12-hex folder, or the one given; refuses with two or more; fold DONE records both shas.
- Reviews: PipelineReview.md:243 agree ("never guess between code versions").
- Data: none.
- PROPOSED: agree.

### S10. S10 (real root and the probe) -- probe part SUPERSEDED by R-L1 (RF:15-22)
- Src: SC:75-84.
- Text (P5, as quoted SC:76-77): "before the first real-outcome fit, E.33 times ... fold 6 (the largest training set,
  664 dates) of the two slowest grid points".
- Readings: a probe on the real root (real outcomes) or on a production-size synthetic table.
- Code: the runner refuses the real root without --registered and trial_registry.require_registered per prefix;
  --expected-n 796 on the real root; --probe writes timing only.
- Reviews: PipelineReview.md:243 agree; SearchReview N1 (lines 111-121) on the exact-path refusal and the log
  written before refusing (code note, not a reading).
- Data: none.
- PROPOSED: ruled (R-L1 (b): the probe runs on seed9000's synthetic table); the refusal rules agree.

### S11. S11 (early-stopping metric) -- RULED R-L7 (RF:140-142)
- Src: SC:86-97.
- Text (P5): "up to 500 iterations with early stopping after 50 rounds without improvement in the weighted
  multi_logloss of the inner validation block".
- Readings: LightGBM's float32 built-in metric or a float64 numpy feval with LightGBM's own callback.
- Code: the float64 feval; kept iteration = min(best, built).
- Reviews: SearchReview.md:165-169 (N9) "I accept S11"; PipelineReview.md:180-185 agree with R-L7.
- Data: 1.6e-10 relative; same stopping iteration (SearchReview probe 1).
- PROPOSED: ruled.

### S12. S12 (guard calls in the engine)
- Src: SC:99-105.
- Text (INTERFACE 2.2, as quoted SC:99): "Every real-data read goes through guard33 (P1.2)."
- Readings: per file or per folder.
- Code: check_path on the features, labels and _day folders once per load, check_date on every date, check_path on any
  symlink; synthetic roots outside derived/e33 skip the guard; the engine refuses dates outside 2020-12-01..2024-02-29.
- Reviews: PipelineReview.md:244 agree.
- Data: a 796-date load 6.3 s instead of 53 s.
- PROPOSED: agree. A folder check refuses a folder holding an unsealed file.

### S13. S13 (interruptions and failed fits; revised for SearchReview SF2-SF4)
- Src: SC:107-135.
- Text (P5): "A fold interrupted before it writes its result ... is not failed: it is rerun once from the DONE markers
  with identical settings ...; a second interruption of the same fold fails the configuration. Every out-of-memory
  kill counts toward P10's two-failure stop".
- Readings: what fails a fit; what is an interruption; a dead worker.
- Code: an attempt record before the tables load; 2 attempts without DONE or FAILED = FAILED; only fit errors (FitError,
  sklearn ValueError/ArithmeticError/LinAlgError, LightGBMError except bad_alloc, non-finite probabilities) fail a
  configuration; every other error propagates (rc 5) with the attempt charged; MemoryError/bad_alloc = OOM (rc 4); a
  dead worker loses only its own fold.
- Reviews: PipelineReview.md:244 agree ("revised for SF2-SF4"); SearchReview SF2-SF4 (lines 61-108);
  PipelineReview N7 (lines 146-151): a non-numerical sklearn ValueError would count as a failed fit; cannot arise with
  the fixed grid.
- Data: none so far.
- PROPOSED: agree. Charging an attempt for a code-bug stop is stricter than P5's list of interruptions, never looser.

### S14. S14 (collector window)
- Src: SC:137-139.
- Text (CLAUDE.md, not the protocol): heavy runs stay out of 15:30-16:00 PT on weekdays.
- Readings: none.
- Code: no new fold submitted in that window; --no-window-pause disables it.
- Reviews: PipelineReview.md:244 agree.
- Data: none (cannot affect an outcome).
- PROPOSED: agree.

### S15. S15 (label validation: stop, never repair)
- Src: SC:141-147.
- Text (P3.3): "Both cannot be positive"; P3.7 rows and weights (validation of the label table).
- Readings: none.
- Code: stops on y outside {-1, 0, 1}, non-finite nets or w <= 0 on rows, y != 0 off rows, FH class/net disagreement,
  impossible fill times, t_ns or grid mismatches, non-finite features.
- Reviews: PipelineReview.md:244 agree.
- Data: none.
- PROPOSED: agree.

### S16. S16 (model-file sha and threads)
- Src: SC:149-153.
- Text (P8): "the 6 fold models of each with sha256".
- Readings: file sha (depends on --lgbm-threads through the parameters block) or a thread-free tree sha.
- Code: both: the file sha and trees_sha256 (the model string before "parameters:").
- Reviews: PipelineReview.md:244 agree.
- Data: none.
- PROPOSED: agree.

### S17. S17 (bit-for-bit predictions)
- Src: SC:155-159.
- Text (lead addendum, not the protocol): OOF probabilities from the stored model.
- Readings: sklearn's predict_proba or a fixed-order reimplementation on the reloaded JSON model.
- Code: fixed-order logits and softmax on the reloaded model (no BLAS).
- Reviews: PipelineReview.md:244 agree; SearchReview probe 2: equals sklearn to 2.2e-16 (LOGIT), 2.8e-16 (LGBM).
- Data: none.
- PROPOSED: agree.

### S18. S18 (inner validation counts training dates, excluded dates included)
- Src: SC:161-163.
- Text (P5): "the latest 15% of the fold's training dates by date (rounded up to whole dates)".
- Readings: count training dates (excluded dates included) or dates with rows.
- Code: ceil(15 n / 100) of the training dates: 97, 97, 97, 97, 97, 100 for folds 1-6; no embargo between inner-train
  and inner-validation.
- Reviews: PipelineReview.md:244-245 agree ("literal 'training dates'"); SearchReview.md:161-163 (N8): literal,
  "flagged only so the lead rules on S18 explicitly".
- Data: none stated.
- PROPOSED: agree (literal; the explicit ruling SearchReview N8 asks for is this entry).

### S19. S19 (LightGBM parameters P5 does not list)
- Src: SC:165-171.
- Text (P5): the listed LightGBM 4.7.0 parameters; "of y on the booster's three raw scores".
- Readings: none; defaults for unlisted parameters.
- Code: LightGBM 4.7.0 defaults (min_sum_hessian_in_leaf 1e-3, min_data_in_bin 3, feature_pre_filter true,
  bin_construct_sample_cnt 200000, verbosity -1); calibrator on the three raw scores, unscaled; sklearn 1.9.1
  multinomial (lbfgs, l1_ratio 0, C 1e4).
- Reviews: PipelineReview.md:245 agree; SearchReview.md:194-203 every listed parameter present.
- Data: none.
- PROPOSED: agree.

### S20. S20 (trade nets in X_D)
- Src: SC:173-174.
- Text (P3.8): "Daily value X_D = the sum of the net P&L of the trades entered on D".
- Readings: none.
- Code: sums the label table's s_net of trades entered, fallback fills included; row-level rho (S7) uses n_long/n_short,
  the trade-level rho s_net.
- Reviews: PipelineReview.md:245 agree.
- Data: none.
- PROPOSED: agree.

### S21. S21 (code and table versions in markers; SearchReview SF1)
- Src: SC:176-195.
- Text (P4.2): "each run exactly once per pipeline hash ... after a logged code fix (0.2) all 40 are rerun"; P4.1 LT7
  "any fit the fix touches, is re-run".
- Readings: how a marker is tied to the code and the tables.
- Code: pipeline_sha over search33, run_search33 and their transitive pipeline/ imports, and tables_fingerprint, in
  every marker; any marker without the running pipeline_sha makes the run refuse (rc 6); nothing is deleted or redone
  automatically.
- Reviews: PipelineReview.md:245 agree; SearchReview SF1 (lines 38-60).
- Data: none.
- PROPOSED: agree. Refusal, not silent redo; every run before and after a fix stays on disk.

---------------------------------------------------------------------------------------------------------------

## P. Selection rule and synthetic proofs (ProofCoder Q*, P-*, PC; ProofReview PR; single implementation)

### P01. Q1 (G1 comparisons)
- Src: PC:33-36.
- Text (P8 G1): "at least 1.0 trade per OOF date on average (at least 796 trades) and a trade on at least 50% of the
  OOF dates".
- Readings: none (integer comparisons).
- Code: count >= 1.0 x T and dates_with_trade >= 0.5 x T (398 of 796 passes, 397 fails; tested).
- Reviews: ProofReview.md:159 agree; PipelineReview.md:246 agree.
- Data: none.
- PROPOSED: agree.

### P02. Q2 (mean net per trade, G2)
- Src: PC:26-31.
- Text (P8 G2): "mean net per trade >= 0.50 tick".
- Readings: sum of the trades' nets / count; sum of X_D / count.
- Code: math.fsum(X_D) / trade count; daily.parquet cross-checked against stats.json.
- Reviews: ProofReview.md:159-160 agree; PipelineReview.md:246.
- Data: the two differ by float rounding only (1e-15).
- PROPOSED: agree.

### P03. Q3 (Tier B start point) -- RULED R-L8 (RF:144-146)
- Src: PC:10-24.
- Text (P8): "continue the Tier A walk over all 300 configurations ordered by the same key, gates ignored, taking the
  next two whose OOF daily series has correlation <= 0.70 with every configuration already taken".
- Readings: continue from where the Tier A walk stopped; restart from the top.
- Code: continue (default); both computed and written to tier_b_detail.
- Reviews: ProofReview.md:142-157 agree, with two details to state in the reading: (i) with Tier A full, gate-failed
  configurations between the first and third members are never examined for Tier B; (ii) with one member, Tier B
  comes from below the lowest-ranked passer. PipelineReview.md:180-185 agree with R-L8.
- Data: outcome-relevant when Tier A is non-empty.
- PROPOSED: ruled; the lead may add ProofReview's details (i)-(ii) to R-L8.

### P04. Q4 (G4 with an undefined standard error)
- Src: PC:38-43.
- Text (P8 G4): "se(SR_d) = sqrt((1 - g3 SR_d + (g4 - 1)/4 SR_d^2)/(T_disc - 1))".
- Readings: (a) a non-positive radicand fails G4; (b) clamp as p7_final.se_sharpe (max(1e-12, .)).
- Code: (a).
- Reviews: ProofReview.md:160-161 agree ("G3 fails too and the pass set is unaffected").
- Data: none.
- PROPOSED: agree. An undefined se cannot show power.

### P05. Q5 (G5 (c) undefined t)
- Src: PC:45-48.
- Text (P8 G5 c): "for each of the 39 months, the daily t of the series without that month ... >= 2.5".
- Readings: none; an undefined t.
- Code: a month whose removal leaves SD 0 fails (c).
- Reviews: ProofReview.md:161-162 agree.
- Data: only constant series reach it.
- PROPOSED: agree.

### P06. Q6 (undefined correlation in a walk)
- Src: PC:50-53.
- Text (P8 Tier A): "take a configuration if its OOF daily series has Pearson correlation <= 0.70 with every
  configuration already taken".
- Readings: none; an undefined correlation.
- Code: never qualifies in the walk; the Tier B fill reports None (see P13).
- Reviews: ProofReview.md:162 agree.
- Data: cannot arise in Tier A (G3 needs SD > 0).
- PROPOSED: agree.

### P07. Q7 (one-sided p-values for the BH and Holm reports)
- Src: PC:55-59.
- Text: E.33 prompt "FDR (and Holm, for reference);" (docs/prompts/STAGE_E.33.md:175); the brief as quoted PC:56 "BH
  FDR and Holm on one-sided p-values from the daily t (state the reading)".
- Readings: normal or Student-t reference; configurations without t.
- Code: p = 1 - Phi(t) from t_stat(); no t -> p = 1, counted in m; BH q = 0.05; Holm step-down at 0.05.
- Reviews: ProofReview.md:162-163 "reports only; fine"; StatsCostCoder reproduced BH 4 and Holm 3 on the 15
  published p-values through select33 (SCC:26).
- Data: none (reports, never gates).
- PROPOSED: agree.

### P08. Q8 (discovery PBO set)
- Src: PC:61-64.
- Text (P6.3): "CSCV PBO over the 300 OOF series with the program's function (screening.stage_e_verdict.pbo: 8 blocks
  of n_days // 8 dates)".
- Readings: which configurations enter.
- Code: every configuration with a series (constants included); failed ones left out, count reported.
- Reviews: ProofReview.md:163 agree with P6.3.
- Data: none (report).
- PROPOSED: agree.

### P09. Q9 ("best configuration" in the proof summary) -- RULED R-L8 (RF:144-146)
- Src: PC:66-73.
- Text (P4.2): "E.33 reports the realised OOF Sharpe of the best planted configuration per seed beside the oracle."
- Readings: the top of P8's order over all, or over non-constant series.
- Code: the first in P8's total order over configurations with a non-constant series, gates ignored; None if none.
- Reviews: ProofReview.md:163-164 agree.
- Data: report only (changed 02:37 after a no-trade configuration showed as "best").
- PROPOSED: ruled.

### P10. Q10 (SD of the 400 null daily Sharpes)
- Src: PC:75-79.
- Text (P4.2): "the SD of the 400 null daily Sharpes (20 configurations x 20 seeds, each centred on its configuration's
  mean) against 1/sqrt(796) = 0.0354".
- Readings: how constant series count.
- Code: population SD of the 400 centred values, a constant series as Sharpe 0; also over non-constant series only.
- Reviews: ProofReview.md:164-165 agree "with N2's df remark" (ProofReview.md:78-82: the reference for the centred SD is
  sqrt(19/20) x 0.0354 = 0.0345; applied, PC:204-205).
- Data: none (report).
- PROPOSED: agree.

### P11. Q11 (funnel of failed configurations)
- Src: PC:81-83.
- Text (P8): "A failed configuration (P5) fails G1"; "the count passing each gate alone and in order G1..G5".
- Readings: none; gates alone for a failed configuration.
- Code: fails every gate alone (no gate can be evaluated).
- Reviews: ProofReview.md:165 agree.
- Data: none.
- PROPOSED: agree.

### P12. PC-COUNT (compiler's ID; ProofCoder's counting rule for seeds with a failed configuration)
- Src: PC:192-197 ("Changes after ProofReview", SF1); B5_proofs.md:11.
- Text (P4.2): "The proof fails if Tier A is non-empty in 2 or more of the 20 null searches"; "The proof passes if at
  least one S5 configuration at FH15 or TB30 enters Tier A in at least 14 of the 20 planted seeds".
- Readings: the literal count (Tier A non-empty only); or a seed with any failed configuration is never clean (null:
  counts against the proof; planted: does not count toward the pass).
- Code: the stricter rule, with both raw counts printed.
- Reviews: ProofReview.md:41-56 (SF1) asked for visibility of failed configurations and, optionally, a criterion line
  "Tier A non-empty: n; seeds with any failed configuration: m"; it did not ask for the counting rule.
- Data: 0 failed fits in each of the 37 seed rows in B5_proofs.md (mtime 09:17 PDT; 4 seeds running, STATE b1).
- PROPOSED: needs the lead; lean agree (a failed fit can only make the null look cleaner, and an incomplete search
  never raises the planted count). Flag: NEEDS LEAD (iii): departs from P4.2's literal count; verdict-relevant.

### P13. PR-N5 (compiler's ID; Tier B fill accepts a constant series)
- Src: ProofReview.md:99-101; PC:208-209 (N5 not applied).
- Text (P8): "A configuration with no OOF series (failed, P5) or a constant OOF series (no trade) is skipped. If fewer
  than two qualify, Tier B is filled by the highest-ranked remaining configurations with a defined series".
- Readings: "defined" = has a series (constant included); or non-constant.
- Code: constant series accepted in the fill; correlation reported as None.
- Reviews: ProofReview.md:99-101 "this is literal ... If the lead reads 'defined' as 'non-constant' the fill
  condition is one `or r["constant"]`. No outcome effect in the proofs."
- Data: none in the proofs.
- PROPOSED: agree. Literal; the skip sentence governs the walk and the fill sentence says only "defined".

### P14. PR-N6 (compiler's ID; summary-only rewrite after an edit of run_proofs33.py)
- Src: ProofReview.md:103-110; PC:206 (N6 applied: the summary prints the writing file's sha256).
- Text (P4.2): "each run exactly once per pipeline hash (4,800 fits); after a logged code fix (0.2) all 40 are rerun
  with the same seeds"; RF:29-37 (R-L3).
- Readings: a summary-printer edit of run_proofs33.py is an executed-file change (R-L3: rerun all 40) or a report-only
  change (`--summary-only`).
- Code: --summary-only skips check_manifest; the summary prints the sha256 of the run_proofs33.py that wrote it beside
  the manifest's.
- Reviews: ProofReview.md:108-110 "the lead decides whether a summary-printer edit triggers the rerun rule or is
  logged as a report-only change".
- Data: none so far.
- PROPOSED: needs the lead; lean: report-only when the edit touches only summary text and the seed results are
  byte-identical, stated with both hashes. Flag: NEEDS LEAD (iv).

### P15. P-L (latency at minute resolution in the generator)
- Src: PC:87-92.
- Text (P4.2): "run from synthetic minute rows on the real decision grid G_h(D)"; P3.2 "as of u + L".
- Readings: design choice.
- Code: three sample points per minute (t, t + L, t + 2L); 1/60 of a minute's variance and drift per L step.
- Reviews: ProofReview.md:166-168 "design choices of the synthetic world, none departs from P4.2".
- Data: synthetic only.
- PROPOSED: agree.

### P16. P-TB (barrier monitoring in the generator)
- Src: PC:94-98.
- Text (P3.4): "tau_up = the first ZM book update u in (t + L, t + L + h min] with M_ZM(u) >= m0 + b(t)".
- Readings: design choice.
- Code: discrete monitoring once a minute at the B points; exact integer comparison as lab33.
- Reviews: ProofReview.md:93-97 (N4) "fine for a proof, and consistent with P3.4 at minute resolution";
  ProofReview.md:166.
- Data: synthetic T30 class shares about 0.29 / 0.42 / 0.29.
- PROPOSED: agree.

### P17. P-SPREAD (touch and spread)
- Src: PC:100-103.
- Text (P4.2): "mids, touch prices, labels and the 59 S5 feature columns generated to match the data facts' rates".
- Readings: design choice.
- Code: 2-tick touches with probability 0.10, i.i.d. per sample point.
- Reviews: ProofReview.md:166; ProofReview.md:111-116 (N7) streams separate.
- Data: synthetic only.
- PROPOSED: agree.

### P18. P-VOL (volatility)
- Src: PC:105-110.
- Text (P4.2): as P17.
- Readings: design choice.
- Code: log sigma_D AR(1) (0.90, SD 0.20), mean set so E[sigma_D^2] + 1/6 = 3.15^2; sigma_ZM(D) per P0.3 on the
  synthetic mids; null on the 20 burn-in dates.
- Reviews: ProofReview.md:166.
- Data: realised mean sigma 3.10-3.14 across draws.
- PROPOSED: agree.

### P19. P-PLANT (the plant)
- Src: PC:112-118.
- Text (P4.2): "Planted: one F3 feature carries a signal whose size is set so that the oracle strategy ... has a daily
  Sharpe of 0.35 net".
- Readings: design choice.
- Code: F3_4 (IOFI5) Gaussian AR(1), phi = exp(-1/5); drift beta x F3_4(t_j); null beta 0, planted 0.367.
- Reviews: ProofReview.md:72-76 (N1): F4 and F2_7 carry derived signal; the only source is F3_4; say so in the summary
  (applied, PC:204).
- Data: synthetic only.
- PROPOSED: agree.

### P20. P-ORACLE (oracle and calibration)
- Src: PC:120-134.
- Text (P4.2): "the oracle strategy (the P3.5 rule applied with the generator's true class probabilities, with the P3.8
  costs and the dead zone) has a daily Sharpe of 0.35 net under the selection variant at FH15".
- Readings: design choice (closed-form class probabilities; expected over draws).
- Code: closed-form p_+1, p_-1 given F3_4(t_i) and sigma_D; class means P3.7-weighted over the seed's rows; beta 0.367
  by bisection on 60 draws (mean SR 0.3498, se 0.0048); check on 60 fresh draws 0.3486.
- Reviews: ProofReview.md:166-168 matches P4.2's text; ProofReview.md:83-92 (N3): the oracle is an anchor, not a
  ceiling; MathReview.md:167-170 (N-2): the per-seed power 0.8 is an assumption.
- Data: synthetic only.
- PROPOSED: agree.

### P21. P-NULL (exactness of the null)
- Src: PC:136-140.
- Text (P4.2): "Null: no feature carries signal."
- Readings: design choice.
- Code: beta = 0; residual discretisation of order 1/sigma^2, well under 0.01 tick; logged, not removed.
- Reviews: ProofReview.md:166; ProofReview.md:111-116 (N7) null probe.
- Data: synthetic only.
- PROPOSED: agree.

### P22. P-RULES (exclusions on the synthetic book)
- Src: PC:142-146.
- Text (P4.2): "the P3.6 exclusion calendar".
- Readings: design choice.
- Code: rules 1-4 from the real calendar; rules 5-6 cannot arise (both sides always, no limits, no ZS/ZL book); row_ok =
  entry_ok; mid_move NaN on excluded dates.
- Reviews: ProofReview.md:166.
- Data: synthetic only.
- PROPOSED: agree.

### P23. P-FEATURES (non-plant features)
- Src: PC:148-154.
- Text (P4.2): "the 59 S5 feature columns generated to match the data facts' rates".
- Readings: design choice.
- Code: clock and calendar C features; noise with feature-like persistence for F1, F2 (except F2_7), F3 (except F3_4);
  F4 per P4 on the synthetic mids; G4 clipping on the 38 columns.
- Reviews: ProofReview.md:166.
- Data: synthetic only.
- PROPOSED: agree.

### P24. P-C7 (C_7 proxy in the generator)
- Src: PC:150-151.
- Text (P4 C.7): "min(trade dates from D to the expiration of the ZM front, from its last definition record with
  ts_recv <= 08:30:00 CT on D, 60)/60".
- Readings: design choice (definitions not read).
- Code: trade dates to the next ZM roll + 10, capped at 60, / 60.
- Reviews: ProofReview.md:166 (P-* agree).
- Data: synthetic only.
- PROPOSED: agree.

### P25. P-FLAGS (C_11-C_14 constant 1 in the generator)
- Src: PC:151-152.
- Text (P4 C.11-C.14): "validity flags v1-v4 of F1-F4 (G3)".
- Readings: design choice.
- Code: all 1 (constant columns, zeroed by the engine for LOGIT, S2).
- Reviews: ProofReview.md:169 "harmless".
- Data: synthetic only.
- PROPOSED: agree.

### P26. P-SEED9000 (probe table)
- Src: PC:156-158.
- Text (P5 probe; R-L1).
- Readings: design choice.
- Code: seed 9000 as a null seed at full size under DERIVED/proofs/seed9000/.
- Reviews: ProofReview.md:166; R-L1 (RF:15-22) uses it.
- Data: synthetic only.
- PROPOSED: agree.

---------------------------------------------------------------------------------------------------------------

## K. Cost model and published reproductions (StatsCostCoder C0-C8, R1-R5, SCC; single implementation)

P6.4 runs after the test list is hashed, on Tier A and Tier B only; "they select nothing" (P6.4 heading).

### K01. C0 (fees; Lucid's basis)
- Src: SCC:71-86.
- Text (P6.4): "Topstep 0.528, Lucid 0.560 (0.920 if the 5.60 USD is not all-in), Bulenox 0.572, MFFU 0.612, Tradeify
  0.920".
- Readings: Lucid 0.560 or 0.920.
- Code: reports 0.560 as the firm's figure and 0.920 as `lucid_not_all_in`; all fees agree with E.28 A2/A3 and P6.4 to
  1e-9; f = 0.528 = Topstep.
- Reviews: PipelineReview.md:247-251 (C1-C7 only; C0 not reviewed).
- Data: the A2 note says "inclusion of exchange/NFA fees not stated" (SCC:82), so P6.4's condition cannot be resolved.
- PROPOSED: needs the lead; lean: report both, label 0.920 as the conservative figure (P6.4 names it), choose none
  for any verdict (reports only). Flag: NEEDS LEAD (iv).

### K02. C1 (a print stamped at the placement time is not a fill)
- Src: SCC:88-92.
- Text (P6.4 ii): "at t + L the order rests at the touch (bid_1 for a long, ask_1 for a short); it fills only when a
  trade prints strictly through its price (below a buy, above a sell) within min(60 s, h/5)".
- Readings: window open or closed at t + L.
- Code: open at t + L (as E.31: a record at T is seen before the order joins).
- Reviews: PipelineReview.md:247 agree.
- Data: none (reports).
- PROPOSED: agree. Never counts a print the order could not meet.

### K03. C2 (side-N trades never fill)
- Src: SCC:94-97.
- Text (P6.4 ii): as K02 ("a trade prints strictly through").
- Readings: include or exclude side-N prints.
- Code: excluded (E.31 measure31_core: "Side-N trades ... are never match events").
- Reviews: PipelineReview.md:247 agree.
- Data: none (reports).
- PROPOSED: agree. Fewer fills; E.31 agreement under V50.

### K04. C3 (the window and the conversion time)
- Src: SCC:99-110.
- Text (P6.4 ii): "within min(60 s, h/5)"; "(ii-b), conversion to a market order at the timeout".
- Readings: W at the exchange, window (t + L, t + L + W], cancel/convert decided at t + W and reaching the exchange at
  t + L + W; E.31's (j, j + 60 s + 50 ms) (cancel latency added on top); a window measured from t.
- Code: the first; W = 60 s for every horizon; (ii-b) fills at the touch as of t + L + W.
- Reviews: PipelineReview.md:247-248 agree ("W at the exchange, cancel/convert with latency L").
- Data: under E.31's convention the window would be 61 s; "a longer window raises p_fill" (SCC:109-110).
- PROPOSED: needs the lead; lean agree (the literal 60 s from the resting time, and the shorter window). The coder
  wrote "This should be decided". Flag: NEEDS LEAD (iv).

### K05. C4 (an exit decision before the timeout)
- Src: SCC:112-119.
- Text (P6.4 ii): as K04.
- Readings: the window ends at the exit decision; (ii-b) converts at c (zero-length round trip, net -spread - fee), or
  cancels without trading.
- Code: c = min(t + W, exit decision); (ii): no trade; (ii-b): converts at c.
- Reviews: PipelineReview.md:248-251 agree, "C4 is the conservative choice".
- Data: none (reports).
- PROPOSED: agree. Charges the signal's cost.

### K06. C5 (no touch on the order's side at t + L)
- Src: SCC:121-123.
- Text (P6.4 ii): "at t + L the order rests at the touch".
- Readings: not placed (unfilled); placed at the first later valid update.
- Code: not placed (flag 64), unfilled in p_fill; (ii-b) still converts at c.
- Reviews: PipelineReview.md:248-249 agree.
- Data: rare (P3.6 entry rules need a valid book at t).
- PROPOSED: agree.

### K07. C6 (exit of the limit variants)
- Src: SCC:125-128.
- Text (P6.4): "Every variant is evaluated on one common signal set: the decision times and sides that the selection
  variant's simulation (P3.8) produced, so variants differ only in execution".
- Readings: the selection variant's exit decision, or exits recomputed from the limit fill.
- Code: the caller's exit decision (FH t + h; TB the selection simulation's tau); P3.2's TB rule applied by the
  caller.
- Reviews: PipelineReview.md:250-251 agree, "C6 is P6.4's text".
- Data: none (reports).
- PROPOSED: agree.

### K08. C7 (entry-leg net and E.31's invalid-state drop)
- Src: SCC:130-132.
- Text (E.33 prompt B6, STAGE_E.33.md:124): "it must match E.31's per-fill accounting where the two overlap."
- Readings: apply E.31's headline-markout drop of fills with an invalid state over [t_f, t_f + h] or not.
- Code: not applied; N_h = s (mid(t_f + h) - price) - fee/2.
- Reviews: PipelineReview.md:247-251 agree (C7).
- Data: agreement tests keep books valid (agree to 1e-9).
- PROPOSED: agree. E.31's drop is a markout filter, not a fill rule.

### K09. C8 (E.31's clock; information)
- Src: SCC:134-136.
- Text (P0.3): "All ordering, look-backs, "as of" lookups, label starts and label ends use ts_recv, never ts_event".
- Readings: none.
- Code: E.33 uses ts_recv; E.31's engine runs on the running maximum of ts_event; agreement tests feed explicit times.
- Reviews: not reviewed.
- Data: none.
- PROPOSED: agree (information).

### K10. R1 (DSR example units)
- Src: SCC:34-37.
- Text (E.33 prompt B5 iii, STAGE_E.33.md:116-118): "The CV, deflated Sharpe, FDR and PBO code reproduces published
  worked examples (Lopez de Prado, Bailey and Lopez de Prado, Benjamini and Hochberg) to the stated digits."
- Readings: none (the paper prints the expressions).
- Code: daily values (SR 2.5/sqrt(250), V 0.5/250, T 1250); reproduced to the 4 printed decimals.
- Reviews: not in any review's readings section.
- Data: none.
- PROPOSED: agree.

### K11. R2 (Holm in the BH example)
- Src: SCC:39-41.
- Text: as K10.
- Readings: none.
- Code: Holm 3 "implied by the published counts" (Bonferroni 3, Hochberg 3); not a printed number.
- Reviews: none.
- Data: none.
- PROPOSED: agree (labelled as implied).

### K12. R3 (PBO at the median rank)
- Src: SCC:43-55.
- Text: as K10.
- Readings: Definition 2.2 ("rbar_n < N/2") or Section 3.1 (lambda <= 0).
- Code: the program (funnel, pinned) counts lambda <= 0 as overfit, the higher PBO; logit magnitudes differ, sign
  identical without ties.
- Reviews: none.
- Data: none (PBO is a report, P6.3).
- PROPOSED: agree. The conservative side; funnel/ not edited.

### K13. R4 (S = 16 misprint)
- Src: SCC:57-59.
- Text: as K10.
- Readings: none.
- Code: the paper prints 12,780; Eq. 2.3 and the program give C(16, 8) = 12,870; "NOT REPRODUCED: a misprint".
- Reviews: none.
- Data: none.
- PROPOSED: agree (record as a misprint, rendered page StatsCost/pbo2017_p11_eq2_3_combinations.png).

### K14. R5 (AFML from secondary sources)
- Src: SCC:61-67.
- Text: as K10 ("to the stated digits").
- Readings: whether a secondary restatement (mlfinpy docs for ch. 4; the author's 2018 JPM paper and 2017 slides for
  ch. 7, construction only) counts.
- Code: ch. 4 digits match the restatement to atol 2e-16; ch. 7 construction reproduced (no numeric example exists).
- Reviews: none. The coder: "The lead decides whether this counts as 'the stated digits' for AFML."
- Data: none.
- PROPOSED: needs the lead; lean: record as "reproduced against the author's restatements; the book itself not seen
  (paid)". Flag: NEEDS LEAD (iv).

---------------------------------------------------------------------------------------------------------------

## D. Data layer and calendar (DataCoder DG-*, DATA-*, CAL-*, G6-*, DC; B's calendar readings B-C7, B-C10, B-SEG-1, LB-14)

All 21 DataCoder readings were accepted by the lead in reports/E.33_RETURN.md section 6 item 12 (line 268-269);
they are not yet entries of RF.

### D01. DG-1 (record-level date bounds of the guard)
- Src: DC:9-18.
- Text (P1.2): "any ZM, ZS or ZL data dated 2017-05-01..2020-11-30 (seal manifest docs/soy_test/SOY_TEST_MANIFEST.json);
  anything dated on or after 2024-03-01".
- Readings: (a) ts_recv only; (b) ts_recv and ts_event on both sides.
- Code: ts_recv in [2020-11-30T22:00Z, 2024-03-01T00:00Z) (the seal manifest's window_utc ends at 2020-11-30T22:00Z);
  ts_event < 2024-03-01T00:00Z; no ts_event lower bound.
- Reviews: PipelineReview.md:252-253 agree ("the guard dry check refuses 4 of 4 classes").
- Data: admits the 1,157 Z1 snapshot records whose ts_event precedes 2020-12-01 (resting orders' original entry
  times; their ts_recv is the owned capture time); refusing them would delete resting orders from the first book.
- PROPOSED: agree (accepted, E.33_RETURN item 12). The seal is defined on the same ts_recv window, so no sealed
  instant is admitted.

### D02. DG-2 (dates outside the discovery span)
- Src: DC:20-24.
- Text (P1.2): "anything dated on or after 2024-03-01"; P1.4 "Universe: the 816 regular grains trade dates
  2020-12-01..2024-02-29".
- Readings: (a) allow other dates before 2017-05-01; (b) refuse every date outside 2020-12-01..2024-02-29.
- Code: (b).
- Reviews: PipelineReview.md:252 agree.
- Data: none (no allowed file holds such a date).
- PROPOSED: agree. Closes every path to other data.

### D03. DG-3 (allowlist)
- Src: DC:26-32.
- Text (P1.2): "Market data E.33 may read: (a) the 156 files; (b) the program calendars ...; (c) the release calendar
  of P3.6; (d) E.31's code ... as a library"; "any other root's market data" refused.
- Readings: which derived stores count.
- Code: strict allowlist: the 156 files, E.31's derived/e31/Z1, the E.33 DERIVED tree, the four manifest copies, the
  two release CSVs (sha256 pinned); E.31's Z2 and Z3 stores refused.
- Reviews: PipelineReview.md:252 agree.
- Data: none.
- PROPOSED: agree.

### D04. DG-4 (dates read from names)
- Src: DC:34-40.
- Text (brief as quoted DC:34): "by any date span readable from a file name".
- Readings: which name tokens count.
- Code: every path component of both spellings: Databento range stamps as UTC instants (end exclusive); <date>_<date>
  inclusive; single YYYY-MM-DD tokens; YYYY-MM tokens as whole months.
- Reviews: PipelineReview.md:252 agree.
- Data: the first discovery file (range=2020-11-30T220000Z_...) passes (start = the seal window's end).
- PROPOSED: agree. A folder or month token naming a sealed date is refused.

### D05. DG-5 (derived_unsealed_files.tsv)
- Src: DC:42-44.
- Text (P1.2): "any file listed in reports/stage_e32_briefs/seal/derived_unsealed_files.tsv".
- Readings: the listed path only, or also folders holding one.
- Code: either spelling refused, and any folder holding a listed file.
- Reviews: PipelineReview.md:252 agree.
- Data: none.
- PROPOSED: agree.

### D06. DATA-1 (ts_recv ordering)
- Src: DC:48-54.
- Text (P4.1 LT4): "with records that have ts_recv < ts_event (0.14-0.16%, F 1.4) kept in ts_recv order".
- Readings: none; how to handle disorder.
- Code: every loader counts decreases and returns a stable ts_recv sort if any, logged in data33.ORDER_LOG.
- Reviews: PipelineReview.md:252 agree. PipelineReview_b.md:77-89 (N11): A's builders did not record ORDER_LOG; applied 09:25 (build_features33 pass1 DONE and build_labels33 results carry `order_log`, FC:63-75; new code_sha12 2b30cb0e953b and 4fd0bb31d210). Count 0 on real data.
- Data: 0 ts_recv decreases in Z1, Z2, Z3, Z4 (whole series checked).
- PROPOSED: agree.

### D07. DATA-2 (month-file boundaries in the ZS/ZL split)
- Src: DC:56-62.
- Text (P0.3): "Trade date D: E.31's convention (measure31.day_bounds), the ts_recv window [D-1 16:00, D 16:00)".
- Readings: keep only the file month's trade dates (E.31 split_file) or take boundary records from both files.
- Code: both files.
- Reviews: PipelineReview.md:252 agree.
- Data: no ZS/ZL date drew records from two files; E.31's ZM store equals an independent raw count on all 816 dates.
- PROPOSED: agree.

### D08. DATA-3 (records outside trade-date windows)
- Src: DC:64-65.
- Text (P0.3): as D07.
- Readings: none.
- Code: counted, not stored.
- Reviews: PipelineReview.md:252 agree.
- Data: ZS 1,373, ZL 2,438 records (weekend and full-closure windows).
- PROPOSED: agree.

### D09. DATA-4 (field types)
- Src: DC:67-69.
- Text: none (storage; P0.2 "Details that cannot affect an outcome ... are E.33's").
- Readings: none.
- Code: action/side uint8 ASCII; ts int64; prices int64 1e-9 units.
- Reviews: PipelineReview.md:252 agree.
- Data: none.
- PROPOSED: agree.

### D10. DATA-5 (definitions)
- Src: DC:71-75.
- Text (brief as quoted DC:71): "all Z4 definition records in ts_recv order"; P0.3 "Tick sizes are read from the
  definitions".
- Readings: all records or outrights only.
- Code: all 1,810,372 by default; outright_only gives 70,131 ZM/ZS/ZL outright-future records (148 ids).
- Reviews: PipelineReview.md:252 agree.
- Data: as stated.
- PROPOSED: agree.

### D11. DATA-6 (loader integrity checks)
- Src: DC:77-79.
- Text: none (integrity; supports P1.2 and P0.3's trade-date window).
- Readings: none.
- Code: refuse a record-count mismatch with the marker or a ts_recv outside D's window; E.31 month marker sha256
  checked against the discovery manifest.
- Reviews: PipelineReview.md:252 agree.
- Data: none.
- PROPOSED: agree.

### D12. CAL-1 = B-C7 (days to expiry, C.7)
- Src: DC:83-89; FC2:158-161.
- Text (P4 C.7): "min(trade dates from D to the expiration of the ZM front, from its last definition record with
  ts_recv <= 08:30:00 CT on D, 60)/60".
- Readings: count T with (a) D < T <= E; (b) D <= T <= E; (c) D <= T < E.
- Code: (a) on both (0 on the expiration date). B: invalid when no definition with ts_recv <= 08:30 CT on D (and <= the
  cutoff) or the expiration is undefined; A: never undefined on the 816 dates.
- A/B: same; B3 0 cells on C_7.
- Reviews: PipelineReview.md:236 agree ("B-C7 = CAL-1 ((a) D < T <= E)").
- Data: range 10..122 over the 816 dates; the choice shifts C.7 by at most 1/60.
- PROPOSED: agree. None of the readings leaks; (a) is the usual count.

### D13. CAL-2 = LB-14 (exclusion reasons)
- Src: DC:91-96; LC2:123-131.
- Text (P1.4): "(i) a ZM roll date (the ZM front on D differs from the front on the previous trade date) and the trade
  date after it (measure31.roll_reasons); (ii) early-close and scheduled late-open dates (measure31.calendar_reason)".
- Readings: which reasons exclude (B: 'roll_status_unknown' and 'no_symbol_mapping' too); counting.
- Code: every reason excludes; counts per reason and distinct; equal to measure31.roll_reasons' set.
- A/B: same; B3 0 cells on entry_ok/row_ok.
- Reviews: PipelineReview.md:252 agree.
- Data: 52 excluded of 816 (23 roll_day, 21 after_roll_day, 5 scheduled_late_open, 4 cme_holiday_or_early_close; one
  date has two reasons), 49 OOF; no unknown or no-mapping reasons (LC2:126-130).
- PROPOSED: agree. Removes more dates.

### D14. CAL-3 (roll test on 2020-12-01)
- Src: DC:98-102.
- Text (P1.4): as D13.
- Readings: use 2020-11-30's ZM.v.0 mapping from the first file's symbology header.
- Code: yes (metadata of an allowed file).
- Reviews: PipelineReview.md:252 agree.
- Data: no roll on 2020-12-01 (a burn-in date).
- PROPOSED: agree.

### D15. CAL-4 (releases)
- Src: DC:104-108.
- Text (P3.6 rule 3): "A calendar month with no valid NOPA row (exactly 2022-11 and 2022-12 in these files) gets its rule
  date: the 15th, or the next trade date if the 15th is not one, at 11:00 CT."
- Readings: unique instants; NOPA rule months; name matching.
- Code: unique instants; NOPA rule months computed and asserted (2022-11-15, 2022-12-15); exact report and time_et
  matching.
- Reviews: PipelineReview.md:252 agree.
- Data: one kept row on a non-trade date (2022-04-15, Good Friday) touches no session.
- PROPOSED: agree.

### D16. CAL-5 (limits as of 08:30)
- Src: DC:110-114.
- Text (P3.6 rule 5): "a single as-of pass over the Z4 files in ts_recv order, state carried across files and dates".
- Readings: a literal single pass or a per-instrument filter of the ordered concatenation; ts_recv ties.
- Code: the ordered concatenation filtered to the front (identical to the single pass); ties to the later record in
  file order.
- Reviews: PipelineReview.md:252 agree.
- Data: None on 0 of 816 dates. (The stale-band finding is L21.)
- PROPOSED: agree.

### D17. CAL-6 = B-C10 (Monday or first date after a full closure, C.10)
- Src: DC:116-117; FC2:163-165.
- Text (P4 C.10): "1 if D is a Monday or the first trade date after a full closure, else 0".
- Readings: what "after a full closure" means.
- Code: a weekday full closure lies strictly between the previous grains trade date and D (both).
- A/B: same; B3 0 cells on C_10.
- Reviews: PipelineReview.md:236 agree.
- Data: 173 of 816.
- PROPOSED: agree.

### D18. CAL-7 = B-SEG-1 (segments, G2)
- Src: DC:119-121; FC2:167-169.
- Text (P4 G2): "a segment is a maximal run of trade dates on which the three fronts (ZM, ZS, ZL) are unchanged".
- Readings: numbering; a front change during a non-trading gap; an unknown front.
- Code: from 0 at 2020-12-01 over the 816 dates; a change in a gap starts the segment on the next trade date; B: a date
  with an unknown front starts its own segment.
- A/B: same; 54 segments on both.
- Reviews: PipelineReview.md:236 agree.
- Data: 54 segments.
- PROPOSED: agree.

### D19. CAL-8 (ct_ns at an ambiguous wall time)
- Src: DC:123-124.
- Text (P0.3): "Times are America/Chicago (CT)."
- Readings: fold at the fall-back hour.
- Code: zoneinfo fold 0; no protocol session time falls in that hour.
- Reviews: PipelineReview.md:252 agree.
- Data: none.
- PROPOSED: agree.

### D20. G6-1 (records used in the G6 report)
- Src: DC:128-130.
- Text (P4 G6): "E.33 also reports, per month, the distribution of ts_recv - ts_event for ZM, ZS and ZL side by side; a
  difference in medians above 100 ms in any month is reported as a data finding".
- Readings: all records, or without F_SNAPSHOT / F_BAD_TS_RECV.
- Code: without them (their ts_recv is the snapshot time or flagged inaccurate).
- Reviews: PipelineReview.md:252 agree.
- Data: none (report; "no rule changes because of it").
- PROPOSED: agree.

### D21. G6-2 (the ZM column)
- Src: DC:132-134.
- Text (P4 G6): as D20.
- Readings: all Z1 records or the front only.
- Code: every Z1 record, with a front-only median beside it; a month flagged if either version differs by > 100 ms.
- Reviews: PipelineReview.md:252 agree.
- Data: none (report).
- PROPOSED: agree.

---------------------------------------------------------------------------------------------------------------

## T. Agreement and leakage tests (TestCoder T-1..T-15, TC; T-5 and T-15 are in F26)

### T01. T-1 (G7 feature tolerance)
- Src: TC:9.
- Text (P4 G7): "features equal within 1e-9 relative (1e-12 absolute near 0)".
- Readings: (a) |a - b| <= max(1e-9 max(|a|, |b|), 1e-12); (b) relative to |b| only; (c) an absolute floor below a
  threshold.
- Code: (a); NaN == NaN counted equal but counted separately; equal infinities equal.
- Reviews: PipelineReview.md:254 agree.
- Data: NaN cells 0 on both sides (B3).
- PROPOSED: agree. Symmetric in A and B.

### T02. T-2 (label tolerance)
- Src: TC:10.
- Text (P4 G7): "labels and classes exactly equal (prices are integer ticks)"; the brief "weights: within 1e-12
  relative" (as quoted TC:10).
- Readings: nets exact or within rounding.
- Code: y, entry_ok, row_ok, flags, made, fill times, span ends, n_long, n_short, per-side nets exact; w within 1e-12.
- Reviews: PipelineReview.md:254 agree.
- Data: 0 cells.
- PROPOSED: agree. Exact is the stricter test.

### T03. T-3 (row join)
- Src: TC:11.
- Text: none (not stated).
- Readings: join on i, or by position.
- Code: on i; a row on one side only is a `__row__` mismatch.
- Reviews: PipelineReview.md:254 agree.
- Data: none.
- PROPOSED: agree.

### T04. T-4 (LT1 draw)
- Src: TC:12.
- Text (P4.1 LT1): "for 200 decision times drawn with seed 20261027 across the OOF dates".
- Readings: (a) uniform over the 796 x 273 (date, i) grid; (b) 200 dates then a minute; (c) excluding excluded dates.
- Code: (a): idx = default_rng(20261027).choice(217308, 200, replace=False); excluded dates included; written to
  LT1_draw.json before any rebuild.
- Reviews: PipelineReview.md:254 agree.
- Data: none.
- PROPOSED: agree. Each decision time equally likely; features exist on every date.

### T05. T-6 (LT2 rows checked)
- Src: TC:14.
- Text (P4.1 LT2): "for every row the span lies in [08:35, 13:13] on D, on one ZM front, clear of P3.6; no feature
  window reaches past t. Violations must be 0."
- Readings: (a) row_ok rows only; (b) also entry_ok minutes (possible span).
- Code: (a), with the TB span max(t + L + h, realised end), each implementation checked with the other's book.
- Reviews: PipelineReview.md:254 agree.
- Data: LT2_r3: 46,886 rows, 0 violations (B3_agreement.md:62).
- PROPOSED: agree on (a); the TB span follows L01's decision (T-6 calls max(t + L + h, realised end) "both coders'
  union reading", which is A's (c), not B's (d)). Flag: tied to L01.

### T06. T-7 (LT2 feature part)
- Src: TC:15.
- Text (P4.1 LT2): "no feature window reaches past t".
- Readings: (a) a static window-end check; (b) t_ns equals the decision time, with LT1 testing that no record after t
  enters.
- Code: (b); LT5 shows the window-end check on the canary.
- Reviews: PipelineReview.md:254 agree.
- Data: none.
- PROPOSED: agree. The builders expose no per-feature window ends; LT1 is the behavioural test.

### T07. T-8 (LT3 embargo "exceeds")
- Src: TC:16.
- Text (P4.1 LT3): "the embargo (21 dates) exceeds every label's span and every feature look-back"; P6.1 "21 covers the
  longest feature look-back: F1.7's and F4.7's 20-date SDs reach the 13:15 mid of the 21st date back".
- Readings: "exceeds" strictly (> 21) or covers (>= 21).
- Code: covers.
- Reviews: PipelineReview.md:254-255 agree, "P6.1's own arithmetic".
- Data: the first training date after an embargo (block end + 22) reaches back to block end + 1, an embargo date; no
  evaluation date. Strict "exceeds" would fail the protocol's own fold design (reported in B4_leakage.md, TC:16).
- PROPOSED: needs the lead; lean agree (P6.1 states the intent; no training feature touches an evaluation date).
  Flag: NEEDS LEAD (iii): the chosen reading is not LT3's literal word; a pass judgment on a declared test.

### T08. T-9 (LT5 shift direction)
- Src: TC:17.
- Text (P4.1 LT5): "a deliberately leaked feature (the label shifted by one step)".
- Readings: y(t - 1 min) or y(t + 1 min).
- Code: y(t - 1 min).
- Reviews: PipelineReview.md:254-255 agree ("T-9's shift direction is the subtle one").
- Data: none (canary).
- PROPOSED: agree. The harder case to catch.

### T09. T-10 (LT7 decision)
- Src: TC:18.
- Text (P4.1 LT7): "the entry decision (side or no trade) recomputed from all streams truncated at t equals the
  production decision".
- Readings: the EV rule only, or gated by the entry rules at t.
- Code: gated by entry_ok (production: the label table's; recomputed: lab33's rules on truncated records); account
  assumed flat at t.
- Reviews: PipelineReview.md:254 agree.
- Data: none yet (LT7 at scale pending, STATE b5).
- PROPOSED: agree. P3.8 decides only where the entry rules hold.

### T10. T-11 (LT7 fill)
- Src: TC:19.
- Text (P4.1 LT7): "the entry fill recomputed from streams truncated at the production fill time (t + L, or the
  fallback fill update of P3.2) equals the production fill".
- Readings: the decided side only, or both sides.
- Code: both counted; the decided side is the test; for an entry not made the cutoff is the planned exit minus 1 ns.
- Reviews: PipelineReview.md:254 agree.
- Data: none yet.
- PROPOSED: agree.

### T11. T-12 (synthetic sessions, P4.2 first bullet)
- Src: TC:20.
- Text (P4.2): "a record-level synthetic MBO and MBP-1 stream for 30 trade dates (tick sizes, spreads, volatility and
  event rates of the data facts)".
- Readings: the regular schedule on every date, or the calendar's sessions.
- Code: labels run: regular schedule on 30 weekdays in 2023-02/04; features run: the real sessions of 30 OOF dates to
  2024-01-10 (early close, late opens), real fronts, releases and definitions, synthetic records.
- Reviews: PipelineReview.md:254 agree.
- Data: B4 synthetic features 8,190 rows, 0 cells (B3_agreement.md:50-55).
- PROPOSED: agree. Exercises the holiday schedules where FD1/FD2 arose.

### T12. T-13 = FD6 -- RULED R-B3-FD6 (RF:108-116); see F23.
- Src: TC:37.
- PROPOSED: ruled (a), Coder-A's `rest == 0`; fix in Coder-B running.

### T13. T-14 = FD7 -- RULED R-B3-FD7 (RF:118-125); see F11.
- Src: TC:38.
- PROPOSED: ruled (b), attribution by order id within the batch; fix in Coder-A running.

---------------------------------------------------------------------------------------------------------------

## Coder readings already answered by a ruling in RF (no new entry needed; listed so nothing is skipped)

| Coder ID | Ruling in RF | Entry here |
|---|---|---|
| SC S10 (probe) | R-L1 (RF:15-22) | S10 |
| SC S11 | R-L7 (RF:140-142) | S11 |
| PC Q3, Q9 | R-L8 (RF:144-146) | P03, P09 |
| FC FA-26, FC2 B-LT1-1, TC T-5, T-15 | R-L9 (RF:132-138) | F26 |
| FC FA-30, FC2 B-EARLY-1, B-LATE-1 | R-B3-FD1/FD2 (RF:60-65) | F30 |
| FC FA-6, FC2 B-OFI-1, B-WIN-1 (OFI sentence) | R-B3-FD3a/b/c (RF:67-83) | F06, F33 |
| FC FA-23, FC2 B-REFILL-1, TC T-13 | R-B3-FD4 (RF:84-89), FD6 (RF:108-116) | F23, T12 |
| FC FA-11, FC2 B-FILL-1, B-REM-1, TC T-14 | R-B3-FD5 (RF:91-93), FD7 (RF:118-125) | F11, T13 |
| FC FA-27, FC2 B-BOOKBAD, LC2 LB-12, LC BOOK-BAD-FLAGS (R part) | R-B3-D1 (RF:95-96), N10 (RF:127-130) | F27, L14 |
| LC R5-CROSSED, LC2 LB-3 | R-B3-D2 (RF:98-100) | L02 |
| LC BOOK-BAD-FLAGS (F_TOB/F_MBP), LC2 LB-13 | R-B3-D3 (RF:102-106) | L12 |
| LC BOOK-UPDATE (pre-R), LC2 LB-1 (pre-R) | R-B3-D4 (RF:102-106) | L13 |
| LC TB-SIGMA, LC2 LB-8 | R-B3-D5 (RF:102-106) | L11 |
| LC2 LB-15, LC finding 2021-07-01 | user V52.2 (docs/DECISIONS.md:1083-1086) | L21 |

Not readings (listed for completeness, no entry): FC2 "What the readings do on the 20 B3 dates" (FC2:202-220) and
"Deviations from INTERFACE.md" (FC2:222-225); LC2 "Differences from INTERFACE.md" (LC2:186-189: no <code_sha12>
level in B's label path, an E.33 layout detail; entry_ok adds M_ZM(t) = L02); SC "sklearn 1.9.1 spelling",
"Additions to INTERFACE 4.3", "Timings" (SC:197-238); PC "Runner" and "Test runs" (PC:160-188), PC SF2 (manifest pins
versions, PC:198-199), PC notes applied N1-N3, N6, N8, N9, N11 (PC:200-207); ProofReview N10 (feasibility, the lead's
call); SCC "B5 (iii) reproduction results" table (SCC:20-30) and "E.31 agreement (B6)" (SCC:138-149); DC "Differences
from INTERFACE.md" (DC:136-139: none); TC's latent D1-D5 list (TC:22-26) = L11-L14 and L02; SearchReview N1-N5, N7,
N10 and PipelineReview N1, N7, N8 (code or sequencing notes, not readings of a protocol line).

---------------------------------------------------------------------------------------------------------------

## Coverage table

| Source file | IDs found | IDs compiled (entry) | SF1-named IDs not found |
|---|---|---|---|
| FeatureCoder_readings.md | FA-1..FA-32 (32) | FA-1..FA-25 F01-F25, FA-26 F26, FA-27..FA-32 F27-F32 (32) | none |
| implB/FeatureCoder2_readings.md | B-OPEN-1, B-WIN-1, B-EARLY-1, B-LATE-1, B-EARLYIDX, B-BOOKBAD, B-MBP-BAD, B-SEAS-1, B-FILL-1, B-REM-1, B-SW-1, B-REFILL-1, B-OFI-1, B-OFI-2, B-OFI-REF, B-VOL-1, B-LAM-1, B-LAM-2, B-RP-1, B-MISS-1, B-C34, B-SIG-1, B-REF-1, B-DBAR-1, B-C7, B-C10, B-SEG-1, B-F13-REL, B-F13-DATES, B-GAP-1, B-F15, B-F49, B-LT1-1 (33) | F01, F33, F30 (x2), F32, F27, F04, F09, F11 (x2), F10, F23, F06, F07, F16 (x2), F22, F12, F13, F14, F05, F24, F15, F16, F08, D12, D17, D18, F18, F17, F20, F34, F25, F26 (33) | none |
| LabelCoder_readings.md | TB-SPAN, R5-CROSSED, LOCKED-LITERAL, TB-M0, ENTRY-WINDOW, ENTRY-FLAGS, EXIT-MARK-TIME, FILL-TIME, TB-TIE, TB-EXACT, TB-SIGMA, W-SUM, BOOK-BAD-FLAGS, BOOK-UPDATE, REPLAY-END, GRID-R1R2, LIMIT-ORDER, MIDMOVE-EXCL (18); finding 2021-07-01; post-B3 D1, D2, D5 | L01, L02, L03, L04, L05, L06, L07, L08, L09, L10, L11, L15, L12 + L14, L13, L16, L17, L18, L19 (18); L21; L14, L02, L11 | none |
| implB/LabelCoder2_readings.md | LB-1..LB-19 (19) | LB-1 L13, LB-2 L01, LB-3 L02, LB-4 L05, LB-5 L08, LB-6 L20, LB-7 L04, LB-8 L11, LB-9 L09, LB-10 L06, LB-11 L07, LB-12 L14, LB-13 L12, LB-14 D13, LB-15 L21, LB-16 L22, LB-17 L03, LB-18 L15, LB-19 L23 (19) | none |
| SearchCoder_readings.md | S1..S21 (21) | S01-S21 (21) | none |
| ProofCoder_readings.md | Q1..Q11 (11); P-L, P-TB, P-SPREAD, P-VOL, P-PLANT, P-ORACLE, P-NULL, P-RULES, P-FEATURES, P-C7, P-FLAGS, P-SEED9000 (12); the SF1 counting rule (no ID) | P01-P11; P15-P26; P12 (PC-COUNT) | none |
| StatsCostCoder_readings.md | C0..C8 (9); R1..R5 (5) | K01-K09; K10-K14 | none |
| DataCoder_readings.md | DG-1..DG-5, DATA-1..DATA-6, CAL-1..CAL-8, G6-1, G6-2 (21) | D01-D21 (21) | none |
| TestCoder_readings.md | T-1..T-15 (15) | T-1..T-4 T01-T04, T-5 F26, T-6..T-12 T05-T11, T-13 T12, T-14 T13, T-15 F26 (15) | none |
| review/ProofReview.md (reviewer-raised readings) | N5, N6 | P13 (PR-N5), P14 (PR-N6) | n/a |
| review/PipelineReview.md, SearchReview.md, MathReview.md, PipelineReview_b.md | views only (cited per entry); PipelineReview_b N11 (D06), N14 (L12), rulings FD6/FD7/N10 (F23, F11, F27); N12, N13 are run notes, not readings | n/a | n/a |

SF1 list (PipelineReview.md:65-73) checked ID by ID: FA-1 F01, FA-3 F03, FA-5 F05, FA-7 F07, FA-9 F09, FA-10 F10,
FA-12/13 F12/F13, FA-14 F14, FA-15 F15, FA-16 F16, FA-17/18 F17/F18, FA-19 F19, FA-20 F20, FA-21 F21, FA-22 F22,
FA-24 F24, FA-25 F25, FA-31 F31, FA-32 F32, B-WIN-1 F33, B-MBP-BAD = FA-4 F04, B-OFI-2 F07; TB-SPAN = LB-2 L01 (the
two are NOT the same reading), LOCKED-LITERAL = LB-17 L03, TB-M0 = LB-7 L04, ENTRY-WINDOW = LB-4 L05, TB-TIE = LB-9
L09, W-SUM = LB-18 L15, REPLAY-END L16; S1 S01, S2 S02, S3 S03, S5 S05, S6 S06, S18 S18, S20 S20; Q1 P01, Q2 P02, Q4
P04, Q5 P05, Q6 P06, Q8 P08, Q10 P10, Q11 P11; C1-C7 K02-K08; CAL-1 = B-C7 D12, CAL-4 D15, CAL-5 D16, CAL-6 = B-C10
D17; T-4 T04, T-5 F26, T-6 T05, T-8 T07, T-9 T08, T-10 T09, T-11 T10. All found. Two SF1 equalities do not hold as
stated: TB-SPAN = LB-2 (L01) and FA-14 = B-RP-1 (F14); both are NEEDS LEAD.

Entry count: F01-F34 (34), L01-L23 (23), S01-S21 (21), P01-P26 (26), K01-K14 (14), D01-D21 (21), T01-T13 (13) = 152.

Not finished or not verified by this compile: (1) the B-side choices where B's readings file is silent (FA-2, FA-3,
FA-21, FA-29, TB-EXACT, REPLAY-END) rest on B3's 0 cells, not on reading B's code; (2) FC and FC2 were being edited
by running fix workers during the compile (hashes above); (3) full_r3 (FD6, FD7, N10 fixes) had not run; (4) the
latent-difference search was by readings text, plus code reads for F14, L01, F13 and F19 only, not a code audit.
