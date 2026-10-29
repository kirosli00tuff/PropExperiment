# ProtocolReview: adversarial review of reports/stage_e34_zl_protocol.md (DRAFT v0.1, P0-P11)

Reviewer: ProtocolReviewer-FableXHigh (worker-xhigh, model fable, claude-fable-5-1). Written 2026-10-29 14:13-14:30 PDT
(`TZ=America/Vancouver date`). Scratch: reports/stage_e34_briefs/work/ProtocolReviewer-FableXHigh/ (recompute_p7.py,
recompute_p7.out, ref_zl_rerun.json, ref_zl_rerun.out).

Method. The whole protocol (576 lines) read by section. Every "as E.32 Pn.m (lines a-b)" range read in
reports/stage_e32_discovery_protocol.md (sha256 verified c4ffb9d7...; the E.33c v0.3 diff read whole). Part M sources
read by section: M1 2.2-2.3, 4.2-4.4, 5, 7; M2 (a), (b), (d), (e), (f); M3 a.4, c.4, d.2-d.3, e.2, (g); M4 equations,
(a), (b), (c), (d)-(g); L whole; X sections 1-6; DF34 sections 1-8; P10_compute_ref.md whole; E.32b recs 4.5 (532-657)
and 6 (1012-1026); DECISIONS V43 (788-806) and V51 (1056-1075); E.32b holding scope 913-951; E.32 test seal section 2
(the sealed-file table, lines 50-66) and the sealed manifest's file names (names only, no data). E.33 pipeline code
grepped only where the protocol relies on it (guard33 check_date/check_records/dry_check, data33 _check_window and
load_mbp1, lab33 constants and bad-book handling, cost33 side-N readings, cal33 previous_trade_dates/_exclusions/
limits, feat33 stream_mbp1 READING FA-4) and the E.33 readings F04 (FA-4) and D20 (G6-1).

Boundaries kept: no market-data file opened; no price, return, feature, label or model output computed; no ZL
statistic of an earlier stage copied; no E.33/E.33b/E.33c outcome file opened (ref_v03.json, read by the rerun of
ref_zl.py, holds wall times only); no web, no keys, no .env, no git change. The two scripts rerun (recompute_p7.py,
written here; ref_zl.py) open no data: ref_zl.py's only read is `ref_v03.json` (grep: `open(`, `read_`, `dbn`,
`npy`, `databento`: no hit beyond the json read), recompute_p7.py imports p7_final, p7_thresholds (program
calendars) and funnel.multiple_comparisons only. Both ran at nice 10.

## Verdict: GO WITH FIXES

Two BLOCKING items, both fixable in the text before the freeze; the first needs a lead decision (and probably a user
decision on a small sealed-window purchase) because it changes P9.1, P11 and, under one of its remedies, T_test and
every P7.2 number. Twelve SHOULD FIX items, fourteen NOTEs. Every threshold, cap, multiplier and compute number the
protocol quotes reproduces with the frozen functions (table at the end). No leak into features or labels was found;
one disclosed mixed-clock residual (rule B) is discussed under N7. No choice steered by a ZL or E.33 outcome was
found, with one sourcing weakness (S9) that should be removed so that the question cannot arise.

Counts: BLOCKING 2, SHOULD FIX 12, NOTE 14.

---

## BLOCKING

### B1. P9.1 / P11: the test window's ZM one-minute bars are not owned before 2019-05 (lines 461-462, 571; also RULES shared facts)

Problem. P9.1 says the test's F09 inputs are "the ZL, ZS and ZM ohlcv-1m bars inside the sealed soy files (owned;
docs/soy_test/SOY_TEST_MANIFEST.json)", and P11's row "test, F09 | ohlcv-1m | ZL, ZS, ZM | 2017-05-01..2020-11-30 |
owned inside the sealed soy files | 0". The seal document contradicts this for ZM.

Evidence. reports/stage_e32_test_seal.md section 2, the "Sealed files" table (lines 57-62):
"| raw ohlcv-1m monthly chunks | ZS | 44 | 2017-04 to 2020-11 |", "| raw ohlcv-1m monthly chunks | ZL | 44 | 2017-04
to 2020-11 |", "| raw ohlcv-1m monthly chunks | ZM | 19 | 2019-05 to 2020-11 (no earlier ZM file is owned) |",
"| step 2 bar store | ZM, ZS, ZL | 3 | trade dates 2019-05-06 to 2024-02-29 |", "| ext2010h bar store | ZS, ZL | 2 |
trade dates 2010-07-01 to 2019-04-30 |". The sealed manifest's 114 file names carry ZM_v_0 only under
processed_step2 and the 2019-05+ raw chunks. E.32b recs 4.5(c) (line 644) listed "ZL: 44 raw ohlcv-1m monthly chunks
2017-04..2020-11" and said nothing about ZM; the BRIEFS shared fact "test bars for ZL, ZS, ZM are owned inside the
sealed files" generalised it. No ZM data of any schema is owned for trade dates 2017-05-22..2019-05-03 (the E.32
P1.1 ZM MBO starts 2020-12; E.32 P9 planned to buy ZM MBO for the test).

Consequence. Every F09 feature uses M(u) (L1.1-L1.6, L1.8, L2.4-L2.9 through M and b_M, L1.7 through V_ZM). On
about 495 of the 870 test dates (2017-05-22..2019-05-03) ZM would be "stale" under 0.3, every F09 feature invalid
(G3), C.11 = C.12 = 0 and the F09 columns 0: the frozen S_crush, S_prop and S_pool models would be scored on
degenerate inputs for 57% of the window. That is not the like-for-like test P9 promises, and it is not the
"owned, USD 0" input P11 declares. If instead the F09 sets' test were restricted to 2019-05-06..2020-11-30
(about 375 OOF dates), SR80_test at that T_test lies far above G4 (recompute_p7.out: SR80_test already exceeds G4
0.2028 at T_test 800), so K2 would stop every F09 finalist before the read and the three F09 sets could never be
tested as designed.

Replacement text (the lead chooses the remedy; this is the one that keeps the design):
- P9.1 line 461-462: "ZL.v.0 MBP-1 and ZL definitions for trade dates 2017-05-22..2020-11-30, requested from
  2017-05-21 (L.e); the ZL and ZS ohlcv-1m bars inside the sealed soy files (owned: 44 raw monthly chunks each,
  2017-04..2020-11, reports/stage_e32_test_seal.md section 2); the ZM ohlcv-1m bars for 2019-05..2020-11 inside the
  sealed files (19 raw monthly chunks) and, for 2017-05-01..2019-04-30, ZM.v.0 ohlcv-1m bought with the test data
  (not owned: 'no earlier ZM file is owned', seal section 2), requested from 2017-05-01 so that the burn-in and the
  20-date references are complete. Without the ZM bars the F09 sets have no test; if they cannot be bought the run
  stage stops before the read and reports."
- P11: replace the "test, F09" row with two rows: "test, F09 | ohlcv-1m | ZL, ZS (2017-04..2020-11), ZM
  (2019-05..2020-11) | owned inside the sealed soy files | 0" and "test, F09 | ohlcv-1m | ZM.v.0 | 2017-05-01..
  2019-04-30 | not owned; bought with the test MBP-1 under the seal guard | not priced (quote with the MBP-1)".
- P9.2 first bullet: add "and ZM.v.0 ohlcv-1m 2017-05-01..2019-04-30" to the quote list.
- Also correct the RULES shared fact in the lead's own records (not a protocol edit).

### B2. 0.3 line 64 against P4 line 357: two different bad-book rules for the same MBP-1 book

Problem. 0.3: "Bad-book reading for MBP-1 (M3 g, P3.0): an update is bad iff its F_LAST record carries
F_MAYBE_BAD_BOOK." P4 F10 header: "a batch containing F_MAYBE_BAD_BOOK marks the book bad". These differ when the
flag sits on a non-F_LAST record of a batch. M_ZL's validity (0.3), the labels (P3.3-P3.4), the P3.6 rule 5 row rule
and every F10 "good" state depend on which one holds. A frozen protocol cannot carry both; a run-stage reading would
be a hidden degree of freedom inside the label definition.

Evidence. M3 (g) P3.0 (line 445-446) states the F_LAST-record form; M1 section 7 (line 455-456) states the batch form;
E.33's frozen code and reading use the batch form: feat33.py stream_mbp1 docstring "READING FA-4: the update is
marked bad if any record of its batch (since the previous F_LAST record) carries F_MAYBE_BAD_BOOK";
reports/stage_e33_protocol_readings.md F04: "Readings: per record; per batch (event); persistent until the next R
... Code: an MBP-1 book update is bad if any record of its batch carries the flag ... Data: 482 ZS and 392 ZL
flagged front records over all 816 dates, none in open time". So the choice moves nothing measured on the
discovery dates (a count, not an outcome), but the test window is unknown and P1.1 reuses E.33's split with E.33's
stream code, which implements the batch rule.

Replacement text, 0.3 line 63-64: "A book update is the state after a record carrying F_LAST, timed at that record's
ts_recv. Bad-book reading for MBP-1 (E.33 reading FA-4, feat33.stream_mbp1): an update is bad iff any record of its
batch (the records after the previous F_LAST record up to and including its own F_LAST record) carries
F_MAYBE_BAD_BOOK." Delete the F_LAST-only sentence; P4 line 357 then agrees.

---

## SHOULD FIX

### S1. P7.1 line 419 against P10.3 lines 545-546: two run orders

P7.1: "4 sets (S_crush, S_prop, S_book, S_pool) x 5 labels ... x 10 model settings = 200 configurations, run in that
nested order." P10.3: "its cut unit is a whole set in the order S_pool, S_crush, S_book, S_prop" (E.32 P5 line 613
ran S5 first so that a cut leaves whole sets). The order matters only when a feasibility cut fires, but then it
decides which sets P8 sees. Replacement, P7.1: "... = 200 configurations. Run order: sets S_pool, S_crush, S_book,
S_prop (P10.3); inside a set FH15, FH30, FH60, TB15, TB30; inside a label the P5 grid order (6 LOGIT, then 4 LGBM)."

### S2. 0.4 (lines 78-84): the mirror rule lacks the count and name substitutions the inherited E.32 text needs

A literal reading of the "as E.32" sections keeps E.32's numbers. Found: P4.1 LT7 (E.32 line 485) "S5 x {FH15,
TB30}"; P4.2 (505-534) "300-configuration", "the 59 S5 feature columns", "N 838", "300 x P(Z > 5.66)", "F3
feature"; P6.3 (638) "over the 300 OOF series"; P6.5 (668-670) "the five blocks C, F1, F2, F3, F4" and "59 x 6 =
354 fits"; P10 cut rule (845-847) "216 x the mean ... LOGIT ... + 144 x ... LGBM" (a ZL set has 180 LOGIT and 120
LGBM folds: 5 labels x 6 x 6 and 5 x 4 x 6); P10 (844) "(S5, S1, S3, S2, S4)"; P4.2's planted-proof reference
"0.91 ... 0.914" (at N 1038 the select-and-pass product at s = 0.25 is 0.898 and selection alone 0.905,
recompute_p7.out). Replacement, add to 0.4: "Counts and names: 300 -> 200; S5 -> S_pool, S1 -> S_crush, S2 ->
S_prop, S3 -> S_book, S4 -> (none); 59 -> 43 features; N 838 -> N_reg (1038); z 5.66 -> 5.72; the five MDA blocks C,
F1, F2, F3, F4 -> the four blocks C, F09c, F09p, F10; SFI 59 x 6 = 354 -> 43 x 6 = 258; a set's fold counts 216 LOGIT
/ 144 LGBM -> 180 / 120; E.32's run order S5, S1, S3, S2, S4 -> S_pool, S_crush, S_book, S_prop; 0.91 / 0.914 ->
0.90 / 0.905. The synthetic proofs (P4.2) run at the thresholds of N 1038."

### S3. Line 15 and P10.4 line 549: reports/stage_e34_zl_methods.md does not exist

The sources list names "reports/stage_e34_zl_methods.md (M1 F10 on ZL, M2 F09 into ZL, M3 labels, M4 power, L the
lead's reconciliations)" and P10.4 hashes it. On disk Part M is five files: reports/stage_e34_briefs/M1_F10_ZL.md,
M2_F09_ZL.md, M3_labels_ZL.md, M4_power_ZL.md, L_lead_reconciliations.md (`wc -l` 513, 640, 488, 335, 97; the
methods file: "No such file or directory"). Either assemble the file before the freeze or replace both mentions
with the five paths (P10.4 already lists L separately).

### S4. P1.2 line 122: "Dropping reads ts_event; nothing else does" is contradicted by P4 G6 (313-314) and LT8 (379-380)

G6: "the run stage reports, per month, the distribution of ts_recv - ts_event for the ZL MBP-1 feed"; LT8: "the
share of grid minutes at which the last T record inside the rule-B bar, by ts_event, has ts_recv > t". Both read
ts_event. Replacement, line 122: "Dropping reads ts_event; no feature, label, exclusion or fill reads it. The G6
clock report and the LT8 count read it for reports only (counts, no outcome)." L.d rule 3 says the same ("no
feature or label reads it").

### S5. P1.2 record drops (120-123): records of a non-front instrument_id are not dropped anywhere in the text

DF34 section 5: "83 of the 158,044,028 records (0.00005%) carry another id than the mapped front, on 14 dates".
E.33's stream keeps only the front (feat33.py:563, DF34 line 272-273), but the run stage's new MBP-1 BookHistory for
labels (DF34 section 7, lab33 row) has no such rule in the protocol. Replacement, add drop rule "(3) records whose
instrument_id is not D's ZL front (0.3), counted (DF34 section 5: 83 records on 14 dates)".

### S6. P4 F10.7 (line 363): no invalidity rule for a zero denominator

QI1s = (qb~ - qa~)/(qb~ + qa~) is 0/0 when both touch prices improved inside the last second. E.32 F3.7 says
"invalid if the denominator is 0"; M1 2.3(b) (line 162-163) says "invalid (0, G3) if the denominator is 0"; M1
section 7's table and the protocol's table dropped it, and F10.8's "invalid marks skipped" presupposes it.
Replacement, F10.7 "Window / parameters" cell: "seasoning 1.000 s; invalid if qb~ + qa~ = 0".

### S7. P2 F10 (217-220) and P4 F10 (370-371): the window changes against E.32 F3 are not listed where they are made

P2 says "8 of E.32's 12 F3 features carry over to MBP-1 unchanged". M1 2.2 (lines 126-134) says otherwise: OFI
"carry over, windows changed to k 5, 15, 30"; TI "carry over, k 5, 15, 30" (E.32 had 5, 15); SW "carry over, window
15" (E.32 F3.10 is SW5; reason M1 2.3 d: "the window is 15 minutes because sweeps are rarer than trades"); QI3
replaced by QIbar5 (M1 2.3 b). Firewall rule 4 (line 163-164) requires each change "listed at its feature with its
reason". None of these comes from an outcome (M1's reasons are message-rate counts and MBP-1's content), but the
protocol must say so itself. Replacement: P2 line 217-218 "8 of E.32's 12 F3 features carry over to MBP-1 with
their definitions unchanged (windows changed as listed in P4)"; P4 line 370-371 add: "Windows changed against
E.32 F3, with reasons: OFI k = 1, 5, 15 -> 5, 15, 30 and TI k = 5, 15 -> 5, 15, 30 (L.a: minimum aggregation horizon 5
minutes from ZL's trade rate; 30 added to span band B's h_c); SW window 5 -> 15 minutes (M1 2.3 d: sweeps are rarer
than trades); QI3 -> QIbar5, a 5-minute mean of the MBP-1 proxy (M1 2.3 b)."

### S8. P4 F10 header (line 357) and P1.2: F and R records' status as book updates is ambiguous

"Book updates are F_LAST records; F and R records enter no count". DF34: 165,388 F records and 1 R record in the ZL
files, F_LAST on 142.1M records; whether an F record carrying F_LAST closes a batch and defines a top-of-book state
is not said (its bid/ask fields are populated like any MBP-1 record). Replacement: "Book updates are F_LAST
records of any action, including F and R; F and R records are neither trades nor removals and enter no T, C or M
count."

### S9. P2 F09c (lines 197, 203-204) and F09p (208-213): the design changes cite M2 (e), which reasons from E.33's negative

The origin split (L1.5-L1.6) and the k = 30 look-back are the two additions against E.32's F1/F2. Their independent
grounds exist in M2 (a).1-2 and (d).4 (the biofuel-origin regime: Avileis and Swanson; Janzen and Wang's collapsed
oil coefficient) and M2 (b).1 (holds of 15-60 minutes). But P2 cites "M2 bottom line 1, (a), (d), (e)" and M2 (e).3
says "F09 on ZL should not be a mirror of E.33's S1 and S2 with the leg swapped ... Otherwise it inherits E.33's
failure mode unchanged", which is a design argument from the E.33 outcome, and firewall rule 5 (line 165-167)
forbids adding a feature "by reference to E.33's ... results". The features are sign-free (a share and a look-back)
and cannot encode E.33's direction, so this is a sourcing fault, not an outcome-steered choice; but it should be
closed. Replacement, P2 F09c: cite "(M2 bottom line 1, (a), (d); (e) for the prior only)" and add "Sources of the
two additions: the origin split from M2 (a).1-2 and (d).4 (regime evidence, literature); the regression-weight gap
from M2 (b).2 (Janzen and Wang). Neither cites an E.31 or E.33 result." P2 F09p: add the reason for k = 30: "k = 30
matches band B's h_c (M2 b.1), the same reason as F10's OFI_30."

### S10. Lines 5-8 and 237-241: the V43 reading (OC-5) is a user-level decision and is not in the user-decision list

The header lists E.32b-D2, E.32b-D3 and E.32-D2 as the decisions before registration. OC-5 (every set is one
order-book program under V43, so S_crush and S_prop run as ML) is a reading of the user's rule V43 ("for order-book
and limit-order strategies ... V28 stands unchanged for every other line", DECISIONS 788-806). M2 (f) "Model rule"
(lines 528-535) says under a literal V43 the bar-built F09 sets "must run as rules" and that the ML form "is
admissible only if the lead rules ... as E.33's precedent did". The precedent is V51 item 1 ("ML is a core tool,
under V43") for a program whose every set carried ZM's own MBO book. The ruling is defensible (labels, fills and
C.3-C.4 come from ZL's book) but it is the user's rule to read. Replacement, line 8: add "- OC-5: that S_crush and
S_prop, built from bar leaders and ZL's book context and traded against ZL's book, run as ML under V43 (option A);
otherwise option B (12 rules under V28 for F09 beside ML for F10, E.32b recs 4.5(b)) is registered instead, and
P7 is recomputed at N_before + 62."

### S11. P7.1 (417-423): the registration mechanics of E.32 P7.1 (lines 685-701) are dropped without replacement

The ZL P7.1 is stated in full, so E.32's text no longer applies: no registry ID pattern, no single register call
before any real-outcome fit, no freeze-file field list (set, label, h, model, hyperparameters, pipeline sha256,
protocol sha256, readings sha256), no require_registered re-check after a restart, no rule that N is
current_n() immediately after the registration (the ZL text has this last one). These are verification hooks, not
outcomes, but P9.3 and P10.1 rely on them. Replacement, add to P7.1: "Registration mechanics as E.32 P7.1 (lines
685-701) with 'E33' read as the run stage's test name, 300 as 200, and the ID pattern <test>-<set><label><grid>, set
C (S_crush), P (S_prop), B (S_book), L (S_pool); label F15, F30, F60, T15, T30; grid as E.32 P7.1."

### S12. P1.5 lines 182-185: the own-price disclosure should say how much of rL_k the model can reconstruct

"ZL's own price enters only inside declared relative-value or scale quantities ... A fitted model can recombine
those quantities" is honest but understates it: within S_prop and S_pool, gR_k = [b_S dS_k + b_M dM_k - dO_k]/(0.01
sigma_ZL sqrt k) with rS_k and rM_k present, so -dO_k/(0.01 sigma_ZL sqrt k) = gR_k - b_S (0.25 sigma_ZS/0.01
sigma_ZL) rS_k - b_M (0.10 sigma_ZM/0.01 sigma_ZL) rM_k: ZL's own scaled k-minute return is an exact linear
function of three features with coefficients that change by date. A LOGIT model recovers it approximately, a tree
model partially. E3 therefore excludes the stand-alone feature, not the information. Replacement, line 183-184:
"A fitted model can recombine those quantities: in S_prop and S_pool, ZL's own scaled k-minute return is a linear
function of gR_k, rS_k and rM_k with date-varying coefficients, so E3 removes the stand-alone feature and its
direct test history, not the information; the disclosure above stands ..."

---

## NOTE

### N1. Line 312: "E.32 P4 G5-G7 (lines 388-395)" cites the wrong range
G5 starts at E.32 line 383 ("G5 Model standardisation"); 388-395 begins inside G6. Replace with "(lines 383-394)".

### N2. P1.4 line 145: the flip example's dates
"ZLN1 and ZLK1 alternating 2021-04-04..04-10" is M1's phrasing; DF34 section 5's table has the changes on
2021-04-05, 04-07, 04-08, 04-09 and 04-12 (5 changes), plus the ZLQ1/ZLQ2 one-day excursions (4): 9 in all, as
the protocol says. Replace the example with "2021-04-05..04-12".

### N3. P4 F10.12 (line 368): a zero or negative trailing median
lam60 is divided by "the trailing 20-date reference median of the same slope". A median of 0 is not covered
(E.32 F3.12 has the same gap). Add "invalid if the reference median is 0". A negative median flips the sign of a
normalised slope; state whether the normaliser is the median or its absolute value (the conservative reading:
abs, so the sign of lam60 is the sign of the slope).

### N4. P4 leader inputs (lines 327-329): L1.7's bars are counted on clock minutes, not the open-time axis
"the 15 bars stamped t - 15 min .. t - 1 min" at 08:35-08:49 would reach into the 07:45-08:30 pause (no bars),
while C.5's V_ZL(15) uses the open-time window of 0.3. Say "the bars at the 15 minute marks of the window of 15
minutes ending at t (0.3, open-time axis), stamped mark - 1 min". Same for V_X(k) wherever bars are summed.

### N5. 0.3 lines 72-74: sigma_ZS and sigma_ZM from bar closes need the "both ends have a bar" reading
E.32 0.3 defines sigma over 1-minute intervals "with valid mids at both ends". For bars: "over the 1-minute
intervals inside 08:35-13:13 whose two end marks both have a usable bar under rule B; intervals with a missing bar
are skipped, not filled". Bars exist only in traded minutes (DF34 section 4), so this matters for ZM on quiet dates.

### N6. P6.4 (402-406): the Topstep prop-account simulator of E.32 P6.4 (lines 659-661) is dropped silently
The ZL P6.4 is restated in full, so E.32's last bullet (the E.19 simulator under the firm's 50K rules: daily-loss
and trailing-drawdown breach probabilities, dates to first payout) no longer applies, yet P10.3 keeps "the prop
simulator" in the cut order it inherits from E.32 P10 (857). E.32b's prop-fit row (MLL USD 2,000 against 3.95
days of 9 trades) suggests keeping it for Tier A. Say either "P6.4 also runs E.32's Tier A prop simulator under
Topstep's 50K rules" or "not run" and remove it from the cut order.

### N7. 0.3 lines 67-71 (rule B): the disclosed mixed-clock residual is acceptable; keep LT8 a count
The bar stamped t - 1 min is complete by exchange time at t; its last trade's ts_recv can exceed t by the capture
latency, so a feature at t can use a record not yet "known" on the ts_recv clock. The fill is at t + L = t + 1 s,
and DF34 measures ts_recv - ts_event > 1 s on 354 of 158,046,466 ZL records, so no information the fill could not
have had enters; and LT1 cannot test this (it truncates bars at rule B, not at ts_recv). The protocol says all
this. Two cautions: (i) the latency of the ZS and ZM bar feeds is not measured (bars carry no ts_recv) and LT8's
count is for ZL only, as stated; (ii) LT8's count must stay a report, never a trigger to move rule B after the fact
(that would be a reading made after an outcome). Add to LT8: "The count changes no rule."

### N8. P3.8 / P7.2 (lines 292-294, 433): the caps 17 / 8 / 4 are FH maxima; TB trades can reach the 20-entry cap
A TB15 trade freeing the account at tau + L can re-enter sooner (M3 d.2: "n_max^T depends on the realised tau
(bounded by 20)"). P7.2's row label "test e80 at the grid caps 17 / 8 / 4 (h 15 / 30 / 60)" should say "FH caps";
for TB configurations the fixed figure is a floor on n and the measured K2 form governs, as P10.2 already says.

### N9. P1.5 line 159: "adopted as written" is not exact
The protocol restates X's rules with changes: rule 2 (X allows the ZS split; the protocol does not use it), rule 6
(X: look-backs under 1 minute; protocol: under 5 minutes), rule 7 (X: "F3.7 and F3.8 ... on seasoned depth";
protocol: "F10.7 and F10.8 are continuous"). All three are tighter or equal. Say "adopted, restated below (rules
2, 6 and 7 tightened)".

### N10. P4 G7 (line 312): "E.33's two implementations (its B3)" is inherited; say whether the run stage builds two
E.32 G7 fixes the agreement tolerance for two independent implementations of features and labels (E.33 B3, A/B).
The ZL protocol inherits the tolerance but never says the run stage must write two implementations. It was E.33's
strongest leak check and it costs a second coder. State it (and P10.3's compute reference does not include it).

### N11. P4 G2/G3: the share of OOF dates on which the F09 families are invalid by construction should be reported
L1.3 needs at least 3 dates of the current segment, and a segment breaks at any front change of ZL, ZS or ZM (25 ZL
changes in 39 months, DF34 section 5; ZS and ZM add their own). On the first 3 dates of every segment L1.3 and
L2.7-L2.9 are invalid, so C.11 = C.12 = 0 and the F09 columns are 0 on a sizeable share of dates. Not a defect (E.32
F1.3 did the same); P4.1 LT11 or the data report should count it, and the P10.5 null report should show it beside
the F09 sets' results.

### N12. P1.1 line 102: the bar files are hashed "into its freeze list" but no expected sha256 list exists yet
The 156 MBP-1/definition files have a verified manifest; the 117 bar files have none in E.34's outputs (DF34
section 2 gives record counts and metadata only). The run stage's first hashing becomes the reference; fine, but say
"hashed once, before any read, and the list is part of the pipeline freeze".

### N13. P3.6 rule 3 (274-277) and P9.2 (474-477): NOPA's 11:00 CT release time in 2017-2020 is assumed
The seven report types and the 11:00 CT (12:00 ET) window are carried from E.32 for both windows. Whether NOPA's
monthly crush release was at 11:00 CT throughout 2017-2020 is not verified anywhere on disk that I read
([unverified]); the calendar builder of P9.2 should record the release time per month from the saved pages, and
the protocol should say the window follows the recorded time, 11:00 CT where none is recorded.

### N14. P10.3 (536-546): the reference is reproduced; three stated caveats stand
ref_zl.py rerun at nice 10 writes JSON identical to ref_zl.json (diff: none; script sha256 57de4f8b..., json
6041900a...). The rescaling formula gives R = 1,200 + 2,372.6 + 38.53 x 114 = 7,965.0 s. P10_compute_ref.md's own
caveats (kappa is a pure guess; the build factor is unverifiable; no independent arithmetic check before this one)
are consistent with the protocol's "guess range". The protocol's "which covers the all-high case" holds: 23,895 >
22,651.

---

## The "as E.32 Pn.m (lines a-b)" references, each read and judged after the 0.4 substitutions

| protocol line | reference | E.32 lines read | holds for ZL after 0.4? | remark |
|---|---|---|---|---|
| 48 | 0.2 (28-45) | 28-44 | yes | "E.33" -> "the run stage" stated; readings file named |
| 55, 72-73 | 0.3 (46-81) | 46-81 | yes, with the ZL protocol's own 0.3 overriding book, bars, ticks, fee | N5 for sigma from bars |
| 217 | F3 (209-222) | 209-222 | yes (evidence text only) | the "Overlap" sentence names ZM; X section 2 replaces it |
| 227 | C (236-240) | 236-240 | yes | |
| 253 | P3.2 (262-276) | 262-275 | yes | ZM -> ZL; "E.33 reports the counts" -> the run stage |
| 263 | P3.4 (285-297) | 285-296 | yes | f 0.528 -> 0.880 stated |
| 268 | P3.5 (298-308) | 298-307 | yes | |
| 271 | P3.6 (309-345) | 309-344 | yes, with the six readings | rule 3's counts are for the discovery dates only (stated) |
| 288 | P3.7 (346-355) | 346-354 | yes | |
| 292 | P3.8 (356-366) | 356-365 | yes | "screening/stage_e_runner.py 31-39" cap carries over |
| 312 | P4 G5-G7 (388-395) | 383-394 | yes; range mis-cited (N1); A/B implementations unstated (N10) | |
| 318 | C (396-411) | 396-411 | yes; C.14 removed, 14 features | |
| 374 | P4.1 LT1-LT7 (466-504) | 466-503 | yes except names: "S5", "E33A", "reports/stage_e33_finalists.md", "ZM MBO" in LT1 (restated), "300 configurations" in LT7's re-run clause | S2 |
| 391 | P4.2 (505-534) | 505-533 | needs S2's substitutions (S5, 59, 300, N 838, 5.66, 0.91/0.914) | S2 |
| 395 | P5 (535-577) | 535-576 | yes; "ZM sign" in the monotone-constraint sentence is cosmetic | |
| 397 | P5 compute (578-615) | 578-614 | replaced by P10.3 (correct); its run order survives only via P10.3 | S1 |
| 400 | P6 (616-682) | 616-681 | P6.1-P6.3 yes ("300" in P6.3, S2); P6.4 and P6.5 restated | N6; MDA blocks and SFI counts, S2 |
| 413 | P8 line 744 | 744 | yes (FDR "a report, never a gate") | |
| 441 | P8 (740-787) | 740-786 | yes with the stated values; "300" twice (lines 771, 773) -> 200 | S2 |
| 474 | P9 (799-806) | 800-806 | yes | the sources list (OCE, NASS, NOPA PDFs) is in E.32's text, not restated: fine by reference |
| 480 | P9 (807-815) | 807-817 | yes | |
| 512 | P10 (832-838) | 832-839 | yes | |
| 546 | P10 (839-858) | 840-858 | needs "216/144 -> 180/120", "S5, S1, S3, S2, S4 -> S_pool, S_crush, S_book, S_prop"; "the prop simulator" in the cut order (N6) | S2 |
| 556 | P10 (859-865) | 860-865 | yes with 200 | |
| 33 | DECISIONS 788-806 (V43) | 788-806 | yes | S10 on whose reading it is |

Other cited lines checked: E.32b recs 4.5 (532-657) and 6 (1012-1026) match what P10.2 and P11 take from them;
E.32b holding scope 913-951 matches 0.5 and the fee; M3 (g) matches P3 except the bad-book sentence (B2) and
"FOMC [12:58, 13:13] on decision dates if adopted" (the protocol rules it out, OC-8: fine); M2 (f) tables match P4's
F09c and F09p tables word for word (checked cell by cell), with the one declared change (L1.7's ZL volume from bars)
stated at line 328-329; M1 section 7's table matches P4's F10 table word for word; M4 (g) row B 200 matches P7.2.

---

## Recomputation table (recompute_p7.py with p7_final.se_sharpe / g4_threshold, p7_thresholds.required_sharpe / trade_dates, funnel.multiple_comparisons.expected_max_sharpe / deflated_sharpe_ratio; ref_zl.py rerun)

| item | protocol line | quoted | recomputed | match |
|---|---|---|---|---|
| T_disc, T_test | 140, 463 | 796, 870 | trade_dates: 816 - 20 = 796; 890 - 20 = 870 | yes |
| e(N) at 1038 | (M4) | 3.2657 | 3.2657 | yes |
| SR0 discovery at N 1038 | (not quoted; RULES 0.1137 at 838) | - | 0.1158 (0.1137 at 838) | - |
| G3 daily Sharpe (DSR 0.95, V 1/795) | 428 | 0.1746 | 0.1746 (t 4.93; DSR 0.9500 at it) | yes |
| G3 at skew -0.5, kurtosis 6 | - | - | 0.1778 | - |
| b_test unrounded | 429 | 0.166967 | 0.166967 (t 4.92; = DSR 0.95 at V 1/869; t-bar 0.1017 does not bind) | yes |
| G4 = binding | 430 | 0.2028 | 0.2028 (t 5.72) | yes |
| SR80_test | 431 | 0.1957 | 0.1957 | yes |
| SR80 discovery at binding | 432 | 0.2330 | 0.2330 | yes |
| test e80 at caps 17/8/4 | 433, 527 | 0.97 / 1.94 / 3.74 | 0.967 / 1.944 / 3.739 | yes |
| test e80 h30 at n 1/2/4 | 434 | 5.50 / 3.89 / 2.75 | 5.500 / 3.889 / 2.750 | yes |
| E.32b's "1.8" (h30, cap 9) at N 1038 | 527 | 1.8 | 1.833 (1.814 at N 838) | yes |
| discovery e80 (G3+G4) at caps 17/8/4, N 1038 | (RULES: 1.08/2.16/4.41 at 19/9/4, N 838) | - | 1.151 / 2.314 / 4.451 | - |
| daily t bar at the test | 435 | 3.0 (SR 0.1017) | 3/sqrt(870) = 0.1017 | yes |
| K2 cannot bind at T_test 870 | 526 | 0.2028 > 0.1957 | binding / SR80_test = 1.036; SR80_test exceeds G4 once T_test < about 820 (0.2042 at 800, 0.1980 at 850) | yes |
| P9.4 multipliers at N 1038 | 490-491 | 1.633 (one null), 1.539 (two) | 1.6329, 1.5395 | yes |
| P9.4 table (M4 simulation) | 495-498 | 0.000/0.845; 0.000/0.995; 0.699/0.993; 0.725/0.857 | copied from M4 (f) rows (as coded all three; amended DSR and t): identical | yes (copy check; simulation not rerun) |
| Holm K = 9 z, m = 1/2/3 | 484 | "z at most 2.90" | 2.539 / 2.773 / 2.902 | yes |
| n_max FH | 89, 294 | 17 / 8 / 4 | floor((277 - h)/(h + 1)) + 1 = 17 / 8 / 4 | yes |
| latest entries | 294 | 12:57 / 12:42 / 12:12 CT | grid index 262 / 247 / 217 -> 12:57 / 12:42 / 12:12 | yes |
| grid minutes a date | 288-289 | 263, 248, 218 | 278 - h = 263 / 248 / 218 | yes |
| feature counts | 317, 332, 344, 356, 539 | C 14, F09c 8, F09p 9, F10 12; sets 22/23/26/43 | C.1-C.13 + C.15 = 14; L1.1-L1.8 = 8; L2.1-L2.9 = 9; F10.1-F10.12 = 12; 22/23/26/43; clipped 22 + unclipped 21 = 43 | yes |
| budget, N_reg, fold fits | 418-420, 539 | 200, 1038, 1,200 | 4 x 5 x 10 = 200; 838 + 200; 200 x 6 = 1,200 | yes |
| R_ZL central, range, stop | 540-541 | 7,965; 3,022-22,651; 23,895 | rerun JSON identical; formula 1,200 + 2,372.6 + 38.53 x 114 = 7,965.0; 3 x 7,965 = 23,895 > 22,651 | yes |
| share of T records outside the day session | 134 | 23.8% (3,812,647 of 16,019,898) | 0.2380 | yes |
| ts_recv - ts_event > 1 s | 69 | 354 of 158,046,466 | DF34 line 107-108: 354 | yes |
| ZL front changes, flips | 144-145 | 25, 9 | DF34 section 5: 25 rows; 5 + 4 = 9 | yes (dates in the example: N2) |
| fee, c_f | 76, 88 | 0.880; 2.38 | 5.28/6.00 = 0.8800; 1.0 + 0.5 + 0.88 = 2.38 | yes |
| cost per sigma_30 ZL vs ZM | 199 | 0.085 vs 0.092 | 2.38/28.10 = 0.0847; 1.59/17.25 = 0.0922 | yes |
| break-even share s_L*, D = 1, m = 1 / 2 | 198 | 52% / 35% | 2.38 x 0.11/0.5 = 0.5236; /0.75 = 0.3491 | yes |
| test MBP-1 estimate; route B minus A | 470, 569, 574 | USD 23.36; 17.60 | 0.5432 x 43 = 23.36; 40.96 - 23.36 = 17.60 | yes |
| 117 bar files | 102 | 117 | 39 x 3 | yes |
| select-and-pass at s 0.25 (E.32 P4.2's 0.91 / 0.914) | via 391 | 0.91 / 0.914 (E.32, N 838) | 0.898 / 0.905 at N 1038 (0.908 / 0.914 at 838) | needs S2's restatement |
| analytic null rate over 200 at the binding t | via 391 | "far below 0.05" | 200 x P(Z > 5.72) = 1.1e-6; at G3 8.4e-5 | yes |

Everything quoted reproduces to the printed digits. The one number the protocol quotes that I could not rerun is the
P9.4 simulation table (M4's 4,000-replication draw); I checked it as a copy against M4 (f).

## Not finished or not verified

- The P9.4 simulation was not rerun (a copy check only; the MathReviewer owns Part M).
- NOPA's historical release time (N13) and the F-record semantics in MBP-1 (S8) are [unverified] here; no web.
- I did not read E.33's lab33 label code beyond grep; the claim that a ZL MBP-1 BookHistory is a new module rests on
  DF34 section 7's reading of it.
- The ZS.v.0 and ZM.v.0 bar files' instrument_id behaviour on roll dates (one id per trade date?) is stated by DF34
  for ZL only ("0 trade dates with two ids in the bar files"); G2's segment rule assumes it for all three roots.
- review/MathReview.md was not present when I wrote this and was not relied on.
