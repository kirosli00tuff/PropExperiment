# E.34 Part M, section L: lead reconciliations of M1-M4 against Part F (lead, Opus 5.5 max, session 2)

Written 2026-10-29 13:55-14:10 PDT. Arithmetic on counts already on disk; no market-data file opened. Inputs:
reports/stage_e34_briefs/M1_F10_ZL.md (M1), M3_labels_ZL.md (M3), M4_power_ZL.md (M4),
reports/stage_e34_data_facts.md (DF34), reports/stage_e34_exposure.md (X).

## L.a M1's message rate and the minimum aggregation horizon, redone with DF34

Source check. M1's per-date counts (records median 188,737, F_LAST book events 168,917, T records 19,195, quietest
date 6,998 T on 2021-04-05) are cited from E.32's data facts (M1 lines 32-33, 242-249: "DF 238-262"), recorded counts,
not a decode. M1's only script (work/MathReaderM1-OpusHigh/scripts/m1_examples.py) contains no file-open or data-read
call (grep for open(, read_, dbn, parquet, DBNStore, from_file, glob, Path(: no hit). RULES rule 2 holds.

DF34's counts agree with M1's to within the date-set and median-rule difference: records median 188,782 against
188,737; T median 19,206 against 19,195 (DF34 section 3 table, line 127). F_LAST is set on 142,061,153 of 158,046,466
records (89.9%), so 188,782 x 0.899 = 169,700 book events against M1's 168,917.

The day-session share was M1's only assumption (83%). DF34 measured it (section 3 totals, lines 137-146):
- T records: 12,207,251 of 16,019,898 in 08:30-13:20 CT = 76.2%;
- all records: 111,058,833 of 158,044,028 = 70.3%.
M1's binding count is trades (M1 3.2, last paragraph). At the measured 76.2%, over the 290-minute day session:

| date | T a date | T a minute (x 0.762 / 290) | n in 5 minutes | iid SD of a sign imbalance, 1/sqrt(n) |
|---|---|---|---|---|
| quietest (2021-04-05, E.32 DF) | 6,998 | 18.39 | 91.9 | 0.104 |
| DF34 5th percentile | 12,352 | 32.46 | 162.3 | 0.078 |
| DF34 median | 19,206 | 50.47 | 252.3 | 0.063 |

Book events at the measured 70.3%: 168,917 x 0.703 / 17,400 s = 6.8 a second on the median date (M1's 0.70 row).

Ruling L.a. The minimum aggregation horizon stays 5 minutes and M1's windows stand ({5, 15, 30} for OFI and TI, 5 for
CR, 15 for SW and RF, 60 for lambda). M1's criterion (i) (iid SD at most 0.10) is read at the 5th-percentile date,
where it holds with margin (0.078). The one quietest date (the Monday after Easter 2021) misses it by 0.004. That is
immaterial next to the long-memory SD of 0.24 at 5 minutes (M1 3.2 table), which is why TI enters the models next to
its own trailing scale and never as a fixed threshold. Caveat: the per-date day share is taken at the pooled 816-date
share; DF34 tabulates day-session records per date (median 131,302) but not day-session T per date.

## L.b Entry caps and the form of K2

M3 d.2: under the frozen grid G_h(D) = {08:35, ..., 13:12 - h} CT and E.32 P3.8's re-entry rule (next decision at the
first grid minute at or after the exit fill), n_max(h) = floor((277 - h) / (h + 1)) + 1:
h 15: floor(262 / 16) + 1 = 17; h 30: floor(247 / 31) + 1 = 8; h 60: floor(217 / 61) + 1 = 4.
E.32b's n_cap = min(20, floor(290 / h)) = 19, 9, 4 assumed back-to-back holds over the whole 290-minute session.

Test e80 at the protocol caps, e80 = SR80_test x sigma_h / sqrt(n), sigma_h 20.37 / 28.10 / 38.21 (E.32b holding
scope 15):

| N (B) | SR80_test (T_test 870; M4 (g)) | h 15, n 17 | h 30, n 8 | h 60, n 4 |
|---|---|---|---|---|
| 838 (0) | 0.1936 | 0.96 | 1.92 | 3.70 |
| 1038 (200) | 0.1957 | 0.97 | 1.94 | 3.74 |

Ruling L.b.
1. The caps used in the protocol's power statements, P7 tables and P10 reports are 17 / 8 / 4, the maxima the frozen
   grid allows. E.32b's 19 / 9 / 4 are superseded for ZL. The 20-entry hard cap of E.32 P3.8 stays as written (it
   never binds at h >= 15).
2. K2 is stated in the rate- and horizon-matched, measured form that M4 (d) offers (E.33's measured e80):
   for a configuration c, e80_test(c) = SR80_test(N_reg, T_test) x SD(X_D,c) / nbar_c, with X_D,c its daily net P&L in
   ticks and nbar_c its mean trades a date, both over its out-of-fold discovery dates. K2 stops the run before the
   sealed read if no Tier A finalist has out-of-fold mean net per trade >= e80_test(c). Because mean(X_D) / nbar >=
   SR80 x SD(X_D) / nbar is the same inequality as SR_d >= SR80_test, and G4 already requires SR_d - se >= b_test
   (binding 0.2007 at N 838, above SR80_test 0.1936), K2 cannot bind for a Tier A finalist while T_test stays 870. It
   binds when the test window shrinks (for example dates lost to P1.2's drop rule or to a short purchase), because
   SR80_test rises as T_test falls. K2 is computed at the realised T_test immediately before the sealed read. The fixed
   figures (0.96 / 1.92 / 3.70 at N 838; 1.8 ticks at E.32b's cap 9) are reported beside it for continuity, not used.

## L.c The latest 30-minute entry

12:42 CT (10:42 PT), from the frozen grid: decision minutes 08:35 .. 13:12 - h CT, every label span ends by 13:13 CT,
before the 13:14-13:15 CT settlement window (M3 d.3, d.6; E.32 0.3 line 68; lab33 LAST_GRID_OFFSET 277). E.32b's
12:50 CT (10:50 PT, BRIEFS shared facts) was a planning figure against the 13:20 close and is superseded for the
protocol. Latest entries: 12:57 / 12:42 / 12:12 CT at h 15 / 30 / 60. Topstep's flat-by time (15:10 CT) never binds,
because ZL's day session ends at 13:20 CT.

## L.d A lower bound on ts_event (X section 6 residual)

DF34 (lines 104-112): ts_recv is non-decreasing within every file; ts_event > ts_recv on 230,475 records (0.146%);
ts_recv - ts_event > 1 s on 354; > 1 day on 7; F_SNAPSHOT and F_BAD_TS_RECV each on 848 records (identical counts).

Ruling L.d (goes into P1.2 as a drop-and-count rule; ts_recv stays the only clock, E.33 P0.3):
1. Drop every record flagged F_SNAPSHOT or F_BAD_TS_RECV (E.33's G6 exclusion; all MDP 2 records carry F_BAD_TS_RECV).
2. Drop every record whose ts_event lies before the first instant of its window's first trade date (discovery:
   2020-11-30T22:00:00Z; test: 2017-05-21T21:00:00Z, the start of trade date 2017-05-22, 16:00 CDT) or whose
   ts_recv - ts_event exceeds 86,400 s.
3. Count the drops by rule and window and report them in the run's data report. Dropping uses ts_event only; no
   feature or label reads it.
The rule closes the residual that guard33's check_records leaves open (no lower bound on ts_event): no record time-
stamped by the exchange inside the sealed window can enter a discovery feature.

## L.e The test span (M1 4.3 against M4 (a))

Trade dates 2017-05-22..2020-11-30 on ZL MBP-1, 890 dates, T_test 870 after the 20-date burn-in, the same span as E.32
P9 for ZM. M4's MBP-1 option from 2017-05-01 (905 dates, T_test 885) is not used: before 2017-05-21 the data are MDP 2,
"The `ts_recv` field on all MDP 2 data is set to the same value as `ts_event`" and "all records on MDP 2 data have the
`F_BAD_TS_RECV` flag set" (M1 4.3, from the saved Databento GLBX page), so the ts_recv clock and L.d rule 1 cannot be
applied the same way. The 15 trade dates 2017-05-01..2017-05-19 stay sealed and untested. Every threshold and power
figure uses T_test 870 (M4's MBO rows).

## L.f (session 3, 15:26 PDT): lead rulings after MathReview and ProtocolReview
- L.f.1 (MathReview S1): L.b's "the 20-entry hard cap of E.32 P3.8 stays as written (it never binds at h >= 15)" holds
  for FH15, FH30 and FH60 only (maxima 17, 8, 4). For TB15 and TB30 the trade count per date is realised (a barrier
  exit frees the account early) and the cap can bind; L.b's e80 table is for the FH labels. Protocol 0.5, P3.8, P7.2.
- L.f.2 (MathReview S2, ProtocolReview B2): one bad-book reading for features, labels, exclusions and fills: E.33
  reading FA-4 (feat33.stream_mbp1): an MBP-1 update is bad iff any record of its batch carries F_MAYBE_BAD_BOOK; the
  mark belongs to that update only (the code clears it at each F_LAST record). M3's F_LAST-record form (M3 c.4, (g)
  P3.0) is superseded. Labels come from ZL MBP-1 in both windows (M1 4.4, L.e), so M3 c.4's parity options reduce to
  (a) without an MBO purchase; parity by identical code. Book updates are F_LAST records of any action (F and R
  included), as E.33's code. Protocol 0.3, P3.2, P4 F10 header.
- L.f.3 (MathReview N13): K2 can bind for a configuration that passed G4 only if SR80_test at the realised T_test
  exceeds 0.2028, roughly T_test below 810 at N 1038 (870 x (0.1957/0.2028)^2). Protocol P10.2.
- L.f.4 (ProtocolReview B1): the test window's ZM ohlcv-1m bars are owned only for 2019-05..2020-11
  (reports/stage_e32_test_seal.md section 2). The data plan adds ZM.v.0 ohlcv-1m 2017-05-01..2019-04-30, bought with
  the test MBP-1 (estimate about USD 1.46: 24 x the median USD 0.0608 of 73 settled ZM ohlcv-1m months in the spend
  ledger). The BRIEFS RULES fact "test bars for ZL, ZS, ZM are owned" was wrong for ZM and is corrected there.
  Protocol P9.1, P9.2, P11.
- L.f.5 (MathReview N5): the overlap of the ts_recv - ts_event tail (DF34: 354 records above 1 s, 7 above a day) with
  the F_SNAPSHOT and F_BAD_TS_RECV flags is left to the run stage's drop report (each record counted under every rule
  it meets and once in the total); no protocol number depends on it, and E.34 makes no new count.
