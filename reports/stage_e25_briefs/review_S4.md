# Stage E.25 S4 review: ShortlistReviewer-FableXHigh

Reviewed: reports/stage_e25_briefs/synthesis.md (v2, 11:30 PDT, NM2 merged 11:33), against the reader files it
cites, reports/stage_e2a_costs.md (D8), sim/costs.py + sim/slippage_calibration.json (MES), s2_power.py/.out,
r0_mechanism_index.md, NM1_nearmiss_table.json, NM2_exec_triage.md, and the E.23 inventory file list. Research
only: no market data, no web fetch, no agents, nothing outside reports/stage_e25_briefs/. Review written 11:40-12:05
PDT 2026-10-18 (`TZ=America/Vancouver date`). Calendar counts (3rd Fridays, FOMC statements, TRA Mondays) were
re-derived by weekday arithmetic from the DF2/DF3 lists, not from any owned calendar module.

## Verdict

**BLOCK** until findings 1 and 2 are corrected (two BLOCKING items, both power figures in the S2 table; neither
changes shortlist membership, rank, or the S2/S3 conclusion that the research window cannot confirm any
candidate). READY WITH FIXES once findings 1-12 are applied. No shortlisted candidate duplicates a prior trial.

Counts: BLOCKING 2, SHOULD FIX 10, NOTE 10.

## Recomputed ratio and power for every S2 row (lead's figure | mine)

Method as the lead's (net = gross - RT; E[t] = net/sd x sqrt(n); one-sided 5% z 1.645; Holm first step k=4 z
2.241, both re-derived by bisection of Phi), with the inputs re-read from the reader files. Conversions: 1 bp =
2.40 MES ticks at ES 6,000; ZN cash->futures x0.69 (RD2 l.8: "E.20 assumption ... not sourced"), ZN price 111,
tick 1/64.

| S2 | Ratio lead \| mine | n lead \| mine | E[t] lead \| mine | Power 5% lead \| mine | Holm-4 lead \| mine | Note |
|---|---|---|---|---|---|---|
| C1 MNQ | 9.32 \| 9.32 (NQ 24,000; 8.16 at 21,000) | 299 \| ~183 traded days | 1.61 \| 1.26 | 0.49 \| 0.35 | 0.26 \| 0.16 | finding 1 |
| C1 MES | 4.73 \| 4.73 | 299 \| ~183 | 1.42 \| 1.11 | 0.41 \| 0.30 | 0.21 \| 0.13 | finding 1 |
| C2 (12.89 bp) | 15.24 \| 15.24 | 13-15 \| 13-15 | 0.54-0.67 \| 0.54-0.58 | 0.13-0.17 \| 0.13-0.14 | 0.04-0.06 \| 0.04-0.05 | finding 2; n 9: 0.45 / 0.12 / 0.04 |
| C2 sens. 14.8 bp n15 | 17.50 \| 17.50 | 15 \| 15 | 0.67 \| 0.67 | 0.17 \| 0.17 | 0.06 \| 0.06 | matches |
| C3 (14.30 bp) | 16.91 \| 16.91 (upper bound) | 13-15 \| 13 | 0.80 \| 0.80 (n15: 0.86) | 0.20 \| 0.20 (0.22) | 0.07 \| 0.07 (0.08) | finding 4: tradable 17:00 CT leg 12.75 bp -> 15.07, 0.71-0.76, 0.17-0.19, 0.06-0.07 |
| C3 sens. 4.2 / 1.6 bp | 4.97 / 1.89 \| same | 15 | 0.21 / 0.05 \| same | 0.08 / 0.06 \| same | 0.02 / 0.01 \| same | matches |
| C4 (12.62 bp, n5) | 5.30 \| 5.30 | 5 (3 cond.) \| 5 | 0.53 \| 0.53 | 0.13 \| 0.13 | 0.04 \| 0.04 | matches the row; does not match the design (finding 3) |
| C4 as designed (n3) | - \| 5.30 at 12.62 bp; 9.93 at the paper's FOMC-Earlier 23.65 bp | - \| 3 | - \| 0.41; 0.85 | - \| 0.11; 0.21 | - \| 0.03; 0.08 | finding 3 |
| C4 sens. FE 9.40 n3 | 3.94 \| 3.94 | 3 | 0.27 \| 0.27 | 0.08 \| 0.08 | 0.02 \| 0.02 | matches |
| C5 (7.26 bp) | 4.42 \| 4.42 | 10 \| 10 | 0.53 \| 0.53 | 0.13 \| 0.13 | 0.04 \| 0.04 | matches; sd inferred (N ~171), see NOTE 14 |
| C5 sens. 6.9 bp | 4.20 \| 4.20 | 10 | 0.41 \| 0.41 | 0.11 \| 0.11 | 0.03 \| 0.03 | matches |

With five registered trials (finding 5) the Holm first step is z 2.326: C1 MNQ 0.24 (lead's E[t]) / 0.14
(corrected), C1 MES 0.18 / 0.11; event rows 0.03-0.07.

Cost table: every D8 round trip in brief_shared.md section 2 matches reports/stage_e2a_costs.md l.16-56 (MNQ
4.119, M2K 3.954, MYM 3.983, MCL 3.167, MGC 4.086, MHG 3.701, MNG 5.350, M6E 1.922, NQ 3.110, ZN 1.168, CL
1.728, GC 4.351; 6S 2.650 and NG 1.672 used in the Group A text also match). MES 2.03 reproduced from sim/costs.py
($1.22 = 0.976 ticks) plus 2 x 0.5251 (slippage_calibration.json close window) = 2.026; the 08:30 bucket gives
2.07. Hurdle ticks (1.5 x RT) in the brief table re-multiplied and correct.

## Findings

### BLOCKING

**1. C1 power is computed on 299 days but the published dispersion is per traded day; the S2 figures are overstated.**
Location: S2 table C1 row (0.49 / 0.41; Holm 0.26 / 0.21), S2 text "The best power is C1's 0.49", C1 design
"at the published size about 250 trading days give power near 0.5", S1 row 1 "daily t 5.34 over 2,620 trading
days". What is wrong: DF1 l.47 records the paper's column as "the number of traded days" ("Unconditional 2620 12
5.34"; "Table 6 calls the column 'the number of traded days'") over a sample "May 2007 to April 2024" (DF1
l.38), about 4,280 trading days. So the strategy traded on about 61% of days and the per-day SR 0.1043 is per
traded day; the paper's 1.8 trades/day is per calendar day (7,668 / 4,280 = 1.79; 7,668 / 2,620 = 2.93 per traded
day). s2_power.py applies SR 0.1043 to all 299 research-window days. Recomputed on the expected ~183 traded days
(or, equivalently, calendar-day SR sqrt(0.612) x 0.1043 = 0.0815 over 299 days): MNQ E[t] 1.26, power 0.35, Holm
0.16; MES E[t] 1.11, power 0.30, Holm 0.13. The forward-test sentence: 250 trading days give power about 0.31
(MNQ) / 0.27 (MES), not "near 0.5". Correct text for S1 row 1: "daily t 5.34 over 2,620 traded days (about 61%
of the 17-year sample)". Decision unchanged: C1 stays first and underpowered; the forward-record design stands.
Evidence: DF1_noise_area.md l.38, l.47, l.96-99; s2_power.py l.14, l.32-37.

**2. C2 row of the S2 table mixes the 14.8 bp sensitivity figures into the published-size range.**
Location: S2 table C2 row "n on RW 13-15 | E[t] 0.54-0.67 | Power 5% 0.13-0.17 | Holm-4 0.04-0.06". What is
wrong: the table header says power is "at the PUBLISHED size"; 0.67 / 0.17 / 0.06 are the s2_power.out
"C2s reversal 14.8bp n15" row (DF2 2022-23 digitized subperiod), already shown in the sensitivity column. At the
published 12.89 bp (sd 80.45 bp) with n 15: E[t] 0.58, power 0.14, Holm 0.05. Correct row: n 13-15, E[t]
0.54-0.58, power 0.13-0.14, Holm 0.04-0.05 (n 9, the roll-blackout case in s2_power.py l.41-43: 0.45 / 0.12 /
0.04). The event count is also stated three ways in the stage's files: 9-13 (synthesis v1 as quoted by NM2
section 5b, "9-13 per synthesis"), 13-15 (S2 table), 15 (S1 row 2, C2/C3 design, NM2 5b). State one rule
(which of the 15 dates the roll blackout and the two Thursday shifts remove) and derive n from it. Decision
unchanged. Evidence: s2_power.out l.3-4, l.9; DF2 l.103-106 (15 dates, 5 quarterly, 2 Thursday); NM2 l.416
(section 5b table).

### SHOULD FIX

**3. C4 S2 row does not describe the C4 design.** Location: S2 table C4 row (n 5, 12.62 bp, power 0.13) versus
the C4 design paragraph ("only when an FOMC statement fell within the preceding five days ... 3 eligible events").
What is wrong: the design conditions on the paper's Table 11 cell, whose published size is "FOMC Earlier 23.65
(SE 6.15)" (DF3 l.69, l.98), not the unconditional 12.62 bp. For the design as written: at 12.62 bp, n 3: E[t]
0.41, power 0.11, Holm 0.03; at the conditional 23.65 bp (full-sample sd 43.15 bp, the cell's sd is not
published), n 3: ratio 9.93, E[t] 0.85, power 0.21, Holm 0.08. The sensitivity cell "FE 9.40 bp, n 3: 0.08"
mixes the fixed-effects size (which is unconditional) with the conditional n. Give the row the design's own
numbers and label the cell sd as the full-sample one. Evidence: DF3 l.64-69, l.98-99, l.126-128.

**4. C3 ratio and power are an upper bound, unlabelled in S2.** Location: S2 table C3 row (16.91; 0.80 / 0.20 /
0.07). What is wrong: s2_power.py l.44-46 labels the 14.30 bp leg "upper bound: published leg starts at the RTH
close"; the S2 table drops the label. The tradable leg from the 17:00 CT reopen is +12.75 bp on the 2026 figure
(DF2 l.33, digitized): ratio 15.07, E[t] 0.71 (n 13) to 0.76 (n 15), power 0.17-0.19, Holm 0.06-0.07. Either
figure clears the hurdle; the row should say which it uses and that the 17:00 CT figure is digitized. Evidence:
DF2 l.18, l.33; s2_power.py l.44-46.

**5. Holm step uses k = 4 while the designs register five trials.** Location: S2 preamble ("first Holm step for k =
4"), s2_power.py l.7, l.13. What is wrong: the designs name one trial each for C1, C4, C5 and "Two trials" for
C2/C3 = 5. First Holm step 0.05/5 = 0.01 one-sided, z 2.326: C1 MNQ 0.24 (lead's E[t]) or 0.14 (finding 1), MES
0.18 / 0.11; event rows 0.03-0.07. Either drop C3 from the registered set (then k = 4 holds and C3 is sensitivity
only) or use k = 5.

**6. Overlap cells omit the nearest prior trials named by the second readers; one overlap removes blindness.**
Location: S1 rows 1-4 "Overlap with the 538" and the C4 design. What is wrong, per row:
- Row 3 (C3): omits A-H4 eth leg (D.1: "session-open hold, eth leg (about 15.5 h)", every trade date,
  r0_mechanism_index.md l.46; DF2 section 7 lists it). Same 17:00 CT -> 08:30 CT window, unconditional. Not a
  duplicate (C3 restricts to 15 expiry dates), but it is the nearest, not E-H1/A-H1.
- Row 2 (C2): omits A-H4 rth leg (08:30-15:00, every day) and D-H4 (overnight gap fade at the first bar, 30 min,
  r0 l.58), both unconditional; DF2 section 7 names them. E-H3 alone is listed.
- Row 4 (C4): omits K2-monthend-01 (long ZN among 6 roots, dates N-1 and N, 07:20-15:04 CT, r0 l.104), which
  shares 2025-10-31 and 2026-01-30 with C4's five pre-TRA dates (DF3 section 7), i.e. two of the three
  FOMC-conditional events the design keeps. K2-monthend-01's research-window ZN trades on those dates are
  already recorded (E.3; NM1 rows "K2-monthend-01 ZN research"), so a C4 read of the research window is not
  blind on 2 of 3 events, the same caveat the lead applies to C1. WZ's own EOM fixed effect (12.63 -> 9.40, DF3
  l.66) says part of the pre-TRA effect is month-end. State both in row 4 and in the C4 design.
- Row 1 (C1): omits K1-vwap-01 (DF1 section 7 lists it first: C1's trailing stop uses VWAP). Nearest only.
No shortlisted candidate duplicates a prior trial: I checked rows 1-5 against r0_mechanism_index.md sections 1-16
and the keyword index l.267-286 (rule text, decision time, hold). Evidence: r0_mechanism_index.md l.43-63,
l.85-104, l.212, l.231-233; DF1 l.178-186; DF2 section 7; DF3 section 7.

**7. Evidence-quality labels missing on three row-1 numbers.** Location: S1 row 1 ("Delgado SR -0.46 for
2025-09..2026-08"; "worst drawdown at 1 MNQ $3.4k-4.25k"), C1 design ("$3.4k-4.25k, DF1"). What is wrong: DF1
grades Delgado "working-paper [secondary-only] (abstract via Crossref; SSRN full text blocked)" (l.54) and Chuk,
the source of the $3,406 MDD, "working-paper [secondary-only]" (l.56-57, l.217). Brusco and VigorTas S&P figures
are "pointer (code checkable, data not shared)" (l.58-62), the same grade the row gives only to the NQ figure.
Correct text: "Delgado SR -0.46 [secondary-only]"; "$3.4k [secondary-only, Chuk abstract] to $4.25k (VigorTas,
P)"; mark Brusco/VigorTas ES as P.

**8. "Every independent S&P test at or below zero" contradicts the cited Paz figure.** Location: S1 row 1, S2 C1
sensitivity cell, S3 (2). What is wrong: Paz OOS SR 0.39, t 0.54 is positive and not significant (DF1 l.51:
"not statistically different from zero ($t = 0.54$)"); Delgado's pooled May 2024-Aug 2026 Sharpe is 0.35 (DF1
l.54). Correct text: "no independent S&P test after publication is distinguishable from zero, and the two most
recent (Brusco ES -0.61 bp/trade; VigorTas ES t -1.21; Delgado 2025-09..2026-08 SR -0.46) are negative".

**9. Re-dig row "E20H6 as a replica": wrong text.** Location: re-dig table row 2 ("H6 exits 1-2 minutes before
the last ten minutes"). RD1 l.142: H6 "exits at 14:58 bar, filling about 14:59 CT, so it drops 1-2 of those ten
minutes". Correct text: "H6 exits 1-2 minutes before the close, inside the last ten minutes where the Aalto
thesis places most of the effect".

**10. Re-dig row V38: "post-2015-inclusive WPs" overstates DF3.** Location: re-dig table V38 row. DF3 section 8:
for C4 "WEAKENS only as far as the cash evidence goes. No futures and no post-2015 intraday subsample are
published"; for C5 "no post-2015 split exists". DF2 l.82: "None of the subperiod means is significant on its
own." Correct text: "two working papers whose samples run past 2015 report pre-refunding (cash) and pre-FOMC
(futures) drifts above the hurdle, but neither publishes a post-2015 estimate; the only post-2015 estimates
(ES 3rd-Friday reversal 14.8-17.6 bp, digitized) are not significant alone".

**11. C1 per-trade basis caveat missing (cuts in C1's favour).** Location: S1 row 1, C1 design. DF1 l.96-99,
l.141: the paper's 7,668 trades may be fills ("If the paper counts fills, its 'per trade' figure is half a round
trip, so per-round-trip gross would be about 8 bp, not 4 bp. The paper does not say which"); independent
replications run 0.8-0.9 round trips a day. The ratio could be about 2x; the power figures are SR-based and do
not move. One sentence in row 1.

**12. S3 (1) power range mislabelled.** "power at the published size is 0.06-0.20": at published sizes the
figures are 0.13-0.22 (0.11-0.21 after findings 1-4); 0.06-0.08 are the post-2015 / fixed-effects sizes. Say
"0.06-0.22 across published and post-2015 sizes" or split the two.

### NOTE

**13.** C5 per-event sd is DF3's inference ("assumes N of about 171 and is DF3's inference, not a published
number", DF3 l.226); RD2 l.75 quotes "250 scheduled FOMC announcements" for the daily sample. At N 250 the sd is
28.9 ticks, E[t] 0.44, power 0.11. Mark the sd as inferred in the S2 row.

**14.** Row 16 (RD3-C1) upper bound 10.5 MGC ticks is at $1,800/oz (RD3 l.40); RD3 l.41 gives 14.0 ticks at
$2,400; gold in the research window is higher. Not a published rule, so the "not shortlisted" stands, but the
price level should be stated.

**15.** The MNQ ratio 9.32 uses NQ 24,000; brief section 2 gives 21,000-25,000 (8.16-9.71). State the level in
S2 as in S1.

**16.** Re-dig row "V34 ... 'unsized'": DF1 l.191 grades it "WEAKENS the 'unsized' basis"; "overturns the reason"
is the lead's upgrade (defensible: R10 sized it from the paper's FAQ). Say it is the lead's grade.

**17.** Header: "v2 (11:30 PDT)" and "NM2 (merged 11:33)" in one sentence; the file's mtime is 11:30. Harmless;
re-stamp on the next edit.

**18.** C4 "FOMC within the preceding five days": DF3 l.234 says the Table 11 cell labels for the five window
events are "DF3's mapping, the lead checks"; the paper's exact definition (calendar or trading days; relative to
the Monday or the Friday) is not quoted. The three events (Oct 29 / Jan 28 / Apr 29 statements, 2 days before
the pre-TRA Friday) are safely inside any reading.

**19.** Row 6: the 23.34 bp is "net of spread" (RD6 E16, thesis); using it as the gross is conservative, and
RD6 l.202 warns that "zero citers can be an index gap". Both worth one clause.

**20.** Row 2 label "(WP; AEA 2025)": DF2 reads the January 2024 AFA copy and the August 2026 version ("R&R at
RFS"); the Table II numbers are from the 2024 copy (DF2 l.46). Minor.

**21.** Group B B1 "cancelled if unfilled by 08:45 CT" is the lead's parameter (NM2 5b: "skip if unfilled by a
fixed time"); fine, but it is a choice, not a published rule, and the design paragraph should say so.

**22.** Prop landscape: Lucid's automation and flatten facts rest on a search summary in R9 (E43 "search summary
of support.lucidtrading.com"); Apex and Tradeify Eurex are [secondary-only] (R16 l.11), which the synthesis already
says. Tag Lucid the same way or cite R9's primary row if one exists.

## Checked and found correct (so the lead need not re-verify)

- Hurdle ratios S1 rows 1-5, 9, 10, 11, 12, 14, 15, 16, 17, 18 and the conversions shown (bp x price / 10,000 /
  tick) all reproduce; MES RT 2.03 and the D8 table match (see above).
- Rows 1-5 quotes: DF1 l.9-12, l.44-48, l.51, l.54, l.58-62, l.106, l.164-167; DF2 l.13-26, l.32-33, l.46, l.56,
  l.62, l.68-69, l.103-106; DF3 l.25-41, l.50-51, l.60-78, l.92, l.126-128. 15 expiries (2 Thursday shifts), 5
  quarterly, 10 scheduled FOMC statements, 5 TRA Mondays (3 with a statement 2 days before the pre-TRA Friday)
  re-derived by weekday arithmetic.
- NM1: 378 rows, 192 positive gross, 119 gross_covers_fees (counted from the JSON). NM2: 54 distinct rule
  texts; 52 / 38 / 21 / 8 = 119; 17 mainly-cost (11 momentum, 6 gate0B), none a fade; Group A nearest rows
  (K3-ldnrev-01 6S 1.909 vs 2.650, t 0.584, n 55; K4-ovr-01 NG 0.718 vs 1.672, t 0.417, n 1,091, fails A3 and
  A4; F3_3 1.204 vs 2.034, t about 0.75, fails A3); the 6E/6J research rows net > 0; C-H1/C-H3/G2.ETH below the
  fee line; K2-cp1-01 ZF/ZN and K3-cp1-01 6E/6B momentum with gross t 2.1-4.1. Passive-saving ranges per class
  (MNQ 0.36-0.68, MES -0.57-0.06, MGC 0.39-1.17, MCL -0.21-0.45, 6E -0.52-0.26, ZN -0.78-0.00; touch 0.22-2.17)
  match NM2 l.207-213 (section 2 table); B1 saving "under 1%" matches NM2 (0.9% MNQ, 0.3% MES). Calibration slice
  dates (2019-05-01..2024-02-29; 26 expiry Fridays 2022-01..2024-02; 20 second-Friday controls) and the E.0 TBBO
  prices ($3.58 NQ, $8.62 MNQ) match NM2 section 5.
- Passive evidence: R18 l.22-23 (Lalor-Swishchuk 65.8-88.8% adverse, TT fills on trade-through); R17 l.55
  (BBK non-HFT MM -$0.97 per contract, 1-minute marks); RD8 l.77 (DeLise -0.45 tick).
- Re-dig table: all 18 rows' quotes found in the named files (RD1 l.26-30, l.139-145; RD2 l.16-18, l.76; RD3
  l.13-16, l.138-141; RD4 l.16-21, l.57-58, l.128-134; RD5 l.17-18, l.47; RD6 l.25-27, l.154-156; RD7 l.29-39,
  l.64-75; RD8 l.28-35, l.57-62; R1 l.43, l.60; R5 l.48, l.83; R9 l.25-30; R10 l.195), except the wording in
  findings 9-10 and the grade in NOTE 16.
- S3: Chordia et al. "within a tenth of a second ... fully within five seconds" (R5 l.46), Takahashi ES about one
  second (R4 l.15, l.77), Brandt-Gao "at once without follow-on momentum" (R5 l.48), CEA "very close to zero"
  after the first 5-minute interval on ES and ZN 2021-2023 (R6 l.53-54, l.306); R11 l.28-29 (<1% Taiwan, 97%
  Brazil lost); R7 l.8 (no audited record); R8 l.12-14, l.34, l.48-50 (16.8 / 51.8 / 33.3; 12.4 / 46.6 / 28.3;
  FPFX 14 / 45 / 7; FTMO 35-55%); R9 l.11-18, l.25, l.32, E10 ("Last updated: 25 September 2026"); R16 l.9-14.
- Group A rule matches Open choice 19 (ret_open_choices.md l.96) and addenda 4-5 (l.45-58).

## Re-check (lead's fixes)

Checked 11:48-11:55 PDT: `diff synthesis_v2_prereview.md synthesis.md` (132 diff lines, every hunk read in
full), s2_power.py/.out v2 (every row re-derived independently; all E[t] and power figures match mine to two
decimals, including the new power-0.8 horizons: MNQ (2.4865 / 0.0931)^2 = 713 traded days = 1,165 trading days,
MES 914 traded = about 1,490), ret_decisions.md, ret_summary.md, and the ruling table in ret_verification.md.

**Verdict: READY.** Findings 1-12 are applied correctly; NOTEs 13-18 and 20-22 applied; no new error introduced.

Per finding: (1) S1 row 1 "2,620 traded days (about 61% ...)"; S2 C1 1.26 (1.11), 0.35 (0.30), Holm-5 0.14
(0.11); forward 250 days 0.31 / 0.27: correct. (2) One event rule (15; 10 if quarterly blacked out), C2 0.47-0.58
/ 0.12-0.14 / 0.03-0.04: correct. (3) C4 row as designed, n 3: 0.41 (0.85), 0.11 (0.21), 0.03 (0.07); sensitivity
"FE 9.40: 0.08; unconditional n 5: 0.13": correct. (4) C3 15.07 at 12.75 bp with 16.91 labelled upper bound;
0.62-0.76 (0.70-0.86), 0.15-0.19 (0.17-0.22), 0.04-0.06 (0.05-0.07): correct. (5) k = 5, z 2.326 throughout,
column renamed Holm-5: correct. (6) Row 1 K1-vwap-01; row 2 A-H4 rth leg and D-H4; row 3 A-H4 eth leg; row 4
K2-monthend-01 with the two shared dates, the EOM fixed effect and "NOT blind on 2 of the 3" in the RW-testable
cell and the C4 design: correct. (7) Delgado [secondary-only], Chuk MDD [secondary-only], Brusco/VigorTas ES P:
correct. (8) S1, S2 cell, S3 (2) and decisions 1: "no independent S&P test ... distinguishable from zero":
correct. (9) H6 exit text: correct. (10) V38 row and decision 4: correct, and DF3's own clause quoted. (11) Fills
caveat in row 1 with DF1's 0.8-0.9 round trips a day: correct. (12) S3 (1) 0.11-0.22 / 0.06-0.17: matches
s2_power.out v2 (published: C2 0.12-0.14, C3 0.15-0.22, C4 0.11-0.21, C5 0.13; post-2015/FE: 0.06-0.17).
New text checked against its sources: row 2 "August 2026 version ... drops that futures table" (DF2 l.14-15);
row 16 "14.0 at RD3's higher price level", ratio 2.57-3.43 (RD3 l.40-41); prop landscape "[secondary-only]" for
Apex, Lucid, Tradeify, Bulenox (R9 E42-E45 all graded "[secondary-only]" by R9 itself; Bulenox's terms PDF was
read for the terms check, the current rule comes from a search summary); B1 cut-off stated as the lead's
parameter; decision 2 "W_cf ... lifts C2 only to about 0.25" (12.89 bp, n 15 + 26 = 41: E[t] 0.96, power 0.25).

Remaining items (NOTE only, no fix required):
- R1. NOTE 19's second clause was not taken: row 6 could add RD6 l.202 "zero citers can be an index gap".
- R2. Wording consistency: the re-dig table now grades the V34 "unsized" row "weakens the basis" (DF1's grade),
  while ret_decisions.md item 5 says the reason "was wrong". Both are defensible (the FAQ does size it); pick one
  phrase for the return and the DECISIONS entry.
- R3. The S2 C1 ratio cell shows 9.32 (4.73) without the NQ level; S1 row 1 now carries 8.16-9.71. Optional.
- R4. ret_verification.md l.39 says "Fable's confirmation of the fixes: see the re-check line below"; that line
  is the lead's to add from this section.
