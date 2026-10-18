# Stage E.25 synthesis (lead): S1-S3, execution triage, re-dig — v3 (after the S4 review; v2 of 11:30 kept as synthesis_v2_prereview.md)

Written by the lead against docs/prompts/STAGE_E.25.md and the user's six addenda. Inputs (all under
reports/stage_e25_briefs/): complete readers R1 (rerun), R2, R5 (rerun), R6, R8, R9, R10, R11, R12, R13, R14, R15,
R16, R17, R18; second readers DF1, DF2, DF3; re-digs RD3, RD4, RD5, RD6, RD7, RD8; NM1 and NM2 (merged 11:30);
partial files cut by the first usage limit at about 01:58 PDT and cited as cut: R3, R4, R7, RD1, RD2. Arithmetic:
s2_power.py, output s2_power.out (published sizes, then post-2015 sensitivity). Hurdle (V31, V38): published gross
per trade > 1.5 x the D8 round trip (RT). Ratio = gross / RT; the hurdle is ratio > 1.5.

## S1. Candidate table (one row per distinct hypothesis)

Quality: PR peer-reviewed, WP working paper, TH thesis, V vendor, LR live record, P pointer. RW = research window
2025-04-01..2026-06-19 (299 equity trade dates). Prop = Topstep unless stated: flat before 15:10 CT; DLL;
trailing max loss $2,000/$3,000/$4,500 (50K/100K/150K); Tier 1 news window 5 min either side of CPI, NFP, FOMC
decision and press conference (R9: minis blocked, index and metals micros capped, pending orders not filled);
automation via API, no HFT.

| # | Hypothesis (readers) | Best evidence (quality) | Instrument, horizon | Published gross -> micro ticks (conversion) | RT ticks | Ratio | Data; owned; cost | RW testable | Prop | Overlap with the 538 (named) | Lead rank |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Noise-area intraday momentum (R10-C1, DF1) | Zarattini, Aziz, Barbon 2024, v2025-09 (WP): SPY 2007-05..2024-04, $0.09/share net at $247 = 3.64 bp net, about 4.0 bp gross (if the paper's 7,668 "trades" are fills, per round trip about 8 bp: DF1; replications run 0.8-0.9 round trips a day); daily t 5.34 over 2,620 traded days (about 61% of the 17-year sample); futures table S&P SR 1.32, Nasdaq 1.23 (cost unstated). Post-publication (DF1): no independent S&P test is distinguishable from zero and the most recent are negative (Brusco ES -0.61 bp/trade, P; VigorTas ES t -1.21, P; Paz OOS SR 0.39, t 0.54; Delgado SR -0.46 for 2025-09..2026-08 [secondary-only]); VigorTas NQ at MNQ cost about 41 MNQ ticks/trade, t 1.37 (P: code checkable, data not shared) | MNQ (MES ref.), 09:00-15:00 CT | 4.0 bp at NQ 24,000 = 9.6 pts = 38.4 MNQ ticks (NQ 21,000-25,000: 33.6-40.0); at ES 6,000 = 9.6 MES ticks | 4.119 MNQ; 2.03 MES | 9.32 (8.16-9.71); 4.73 | 1-min bars; owned; $0 | yes, but NOT blind: third-party results already cover 2025-2026 (DF1) | intraday; worst drawdown at 1 MNQ $3.4k [secondary-only, Chuk abstract] to $4.25k (VigorTas, P) exceeds the 50K and 100K trailing max loss | never tested; V34 dropped it as "unsized" (the basis is weakened: R10, DF1); nearest K1-vwap-01 (C1's trailing stop uses VWAP), K1-cp2-01, B-H1/RT1-RT4, E20H6-T1 | 1 |
| 2 | 3rd-Friday spike, reversal leg: short MNQ/MES at the 08:30 CT open of the monthly a.m.-settlement Friday (RD4, R12, DF2) | Baltussen, Terstegge, Whelan (WP; January 2024 AFA copy read by DF2; the August 2026 version, sample to 2023, drops the futures table): ES Table II -12.89 bp, t -2.40, sd 80.45 bp, 2003-2021 (verified, DF2); 2015-23 17.6 bp, 2022-23 14.8 bp (digitized, not significant per subperiod); about 70% of the reversal in 08:30-09:00 CT, complete by about 10:30 CT; carried by quarterly expiries (-37 bp vs -6 bp off-quarter, SOQ basis) | MNQ/MES, 08:30 -> 10:30 or close | 12.89 bp x 6,000 / 10,000 / 0.25 = 30.9 MES ticks; NQ (DF2 figure) -12.5 bp in 30 min | 2.03 MES | 15.24 | 1-min bars + expiry calendar; owned; $0 | yes: 15 monthly expiries in the RW, 5 quarterly; 2025-04-17 and 2026-06-18 are Thursday expiries (DF2) | compatible | nearest: A-H4 rth leg (MES 08:30-15:00 every day) and D-H4 (overnight-gap fade at the first bar, 30 min), both unconditional; E-H3 (MES quarterly witching short 14:30-15:00) differs: open window, monthly | 2 |
| 3 | 3rd-Friday spike, run-up leg: long 17:00 CT Thursday -> 08:30 CT Friday (RD4, R12, DF2) | same paper: Thu close -> Fri open +14.30 bp, t 3.54, sd 60.53; none accrues 15:00-17:00 CT (-0.6 bp), +12.75 bp from 17:00 CT (DF2); decayed: 26.2 bp (2003-14), 4.2 (2015-23), 1.6 (2022-23) | MNQ/MES, inside one Topstep day | 14.30 bp -> 34.3 MES ticks (full sample); 4.2 bp -> 10.1; 1.6 bp -> 3.8 | 2.03 | 16.91 (published table, upper bound for a 17:00 CT entry); 15.07 (17:00 CT leg, digitized); 4.97 (2015-23); 1.89 (2022-23) | as row 2 | yes, n 15 (10 if quarterly dates are blacked out) | compatible | nearest: A-H4 eth leg (MES session-open hold about 15.5 h, the same 17:00 CT -> 08:30 CT window, every day, unconditional); E-H1, A-H1 differ in calendar and window | 4 (decayed) |
| 4 | Pre-refunding-announcement Treasury gain: long ZN over the NY session of the trading day before the quarterly refunding announcement (RD2, DF3) | Wang, Zhao 2025 OSF draft (WP): 10-year CASH +12.62 bp, t 3.32, N 129 (verified); 9.40 bp (SE 4.03) with day-of-week and month-end fixed effects; intraday result only as a figure; "present almost exclusively when an FOMC announcement occurs within the preceding five days" (DF3) | ZN, one session | 12.62 x 0.69 (futures/cash) x 111 / 10,000 x 64 = 6.19 ZN ticks; FE 9.40 -> 4.61 | 1.168 | 5.30; FE 3.94 | ZN bars owned; dates public | partial: 5 events, 3 FOMC-conditional (TRAs 2025-11-03, 2026-02-02, 2026-05-04); NOT blind on 2 of the 3 (K2-monthend-01's recorded research-window ZN trades cover the pre-TRA days 2025-10-31 and 2026-01-30) | compatible; 1 ZN = $15.625/tick | nearest K2-monthend-01 (long ZN on month-end dates N-1 and N, 07:20-15:04 CT; WZ's own month-end fixed effect cuts 12.63 to 9.40 bp, so part of the effect is month-end); K2 auction members and E16-H3 use auction dates | 5 |
| 5 | Pre-FOMC Treasury drift: long ZN 18:00 CT day -2 -> 11:00 CT day -1 (RD2, DF3) | Pan, Peng 2026 SAIF draft (WP): 10-year FUTURES +7.26 bp, t 2.82, 2004-01..2025-06 (verified); December 2025 draft 6.9 bp, t 2.24; window read off the authors' figure (Tokyo open to London close) | ZN, 17 h inside one Topstep day | 7.26 x 111 / 10,000 x 64 = 5.16 ZN ticks | 1.168 (D8 book data: same RT at 18:00-18:30 CT, a third of the depth, DF3) | 4.42 | owned | yes, n 10 | compatible | K2-fomcpost-01, K5-fomc-01, E-H1 differ in asset or window | 3 |
| 6 | FOMC pre-announcement reversal, 12:50-14:50 CT (R6-C3, RD6) | Baglioni-Ribeiro thesis (TH): 23.34 bp per event net of spread, 71 events 2011-2020; nothing after 2020-01; zero citers in OpenCitations (RD6; can be an index gap) | MES/MNQ | 23.34 bp (net of spread, used as gross: conservative) -> about 56 MES ticks | 2.03 | about 27 | owned; FOMC dates owned | yes, n 10 | crosses the 13:00 CT statement: Tier 1 window blocks or caps entries 12:55-13:05 CT and pending orders do not fill | E-H1, E-H2, K9-anncday-01 draft differ in window | 6 (thesis grade) |
| 7 | FOMC press-conference fade or continuation (R5-C1, R6-C1) | Narain-Sangani IJCB 2026 (PR): sign reversed across regimes (continuation 2011-2020, reversal after COVID, n about 16) | MES/MNQ, 13:36-15:00 CT | not a per-trade figure (R6 derives about 260 MNQ ticks from a slope) | - | - | owned | yes, n 10 | Tier 1 window moves entry to 13:36 CT | E-H2, K2-fomcpost-01 | not shortlisted (sign unstable, unsized) |
| 8 | Gamma-proxy (5-day RSI) overlay on row 1 (R2-C2) | Beat the Market section 4.5 (WP), in-sample beta -3.25 | MNQ | overlay, no per-trade figure | - | - | owned | yes | as row 1 | as row 1 | not shortlisted (adds a fitted parameter) |
| 9 | First-half-hour momentum on high-volatility or volume days (R12-C3, R4) | Gao, Han, Li, Zhou JFE 2018 (PR): 5.85 bp, t 3.80, SPY 1993-2013, full-sample terciles | MES/MNQ, 14:30-15:00 CT | 14.0 MES ticks | 2.03 | 6.90 | owned | yes | compatible | duplicates K1-cp1-01, E20H6-T1/T2 (FAIL) | not shortlisted (duplicate) |
| 10 | FOMC-day first-30-min momentum into the last 30 min (R12-C4) | R12 source (WP) | MES | 19.1 MES ticks (reader) | 2.03 | 9.41 | owned | partial | compatible | K1-cp1-01, E-H1/E-H2 | not shortlisted (duplicate family) |
| 11 | Conditional overnight drift (buy the dip), 01:30-03:30 ET (R13-C1, R15) | Boyarchenko, Larsen, Whelan RFS 2023 (PR) | MES | about 11.7 MES ticks (reader) | 2.03 | 5.76 | signed close volume not owned | partial | compatible | A-H1 (FAIL) | excluded: authors (2026) "averaged close to zero since 2021" |
| 12 | 5-minute ORB, 10R target (R10-C3) | Zarattini, Aziz 2023 (WP), in-sample, zero slippage | MNQ | at least 23.8 MNQ ticks (derived bound) | 4.119 | at least 5.8 | owned | yes | compatible | duplicates B-H1, RT1-RT4, H1/H3/H4, K1-cp2-01; Mesfin 2026 walk-forward T 0.88 | not shortlisted |
| 13 | ATR-band breakout (R10-C2) | Concretum note 2026 (V) | MES/MNQ | unsized | - | - | owned | yes | compatible | D-H3, B-H4 | not shortlisted |
| 14 | Fixed-percent ORB on crude (R10-C4) | Holmberg et al. FRL 2013 (PR), 1991-2011 | MCL | 13 MCL ticks | 3.167 | 4.10 | owned | yes | compatible | K4-cp2-01 | not shortlisted ("not robust to time") |
| 15 | API-to-EIA crude predictability (RD3-C2) | Alturki-Kurov JFM 2022 (PR), 2011-2019 | MCL | 4.5 MCL ticks | 3.167 | 1.42 | owned | yes | compatible | re-parameterizes K4-apipre-01 (FAIL) | not shortlisted (below hurdle) |
| 16 | Rates-to-gold after FOMC (RD3-C1) | reader's own construction | MGC | upper bound 10.5 MGC ticks at $1,800/oz (14.0 at RD3's higher price level) | 4.086 | 2.57-3.43 (bound) | owned | yes | Tier 1 caps metals micros | K5-fomc-01 | not shortlisted (not a published rule) |
| 17 | GMM regime entries on MNQ (R12-C5/C6, RD1-C1) | Mesfin arXiv 2026 (WP, one unreviewed author, 53+ combinations) | MNQ | 24.4-55.3 MNQ ticks | 4.119 | 5.9-13.4 | owned | yes | compatible | A-H1, C-H1, D-H1/D-H3 | not shortlisted (specification search) |
| 18 | 0DTE-era gamma-conditioned reversal (R1-C1) | Adams et al. 2026 (WP): 1-2 bp, 10 min-2 h, top net-gamma quartile | ES | 2.4-4.8 MES ticks | 2.03 | 1.2-2.4 | Cboe intraday Open-Close: $1,000 per data-month at 10-min (R2), not owned | no | compatible | C2, E20H6-T3 | not shortlisted (authors: not feasible; net gamma unobservable) |
| 19 | SpotGamma Put Wall breach (R2-C1) | vendor (V), +14 bp 1-day, no n | ES | overnight hold | - | - | not owned | no | not Topstep (overnight) | - | not shortlisted |
| 20 | Liquidity-sweep reversal; value-area 80% rule (R11-C1/C2) | communities (P); Osler 2002 points to continuation | MES/MNQ | unsized | - | - | owned | yes | compatible | B-H2, G5.RTH, H5; F6_1, D-H4 | not shortlisted |
| 21 | Minute-scale order-flow imbalance (R3-C1/C2) | CKS 2014, CCZ 2023 (PR); ES OFI shocks die within 1 s | MES/MNQ | no per-trade gross at 1-30 min | - | - | MBP-10 not owned | partial | HFT ban at the working horizon | D.1g C6 | not shortlisted |
| 22 | Signed market-maker SPX position change (RD5-C1) | Egebjerg-Kokholm (WP) [secondary-only] | ES | unsized | - | - | paid | no | compatible | E20H6-T3, C2 | not shortlisted |
| 23 | GEFS forecast revisions traded intraday on NG (RD6-C1) | pointer; no intraday gross published | MNG | unsized | - | - | free (AWS from 2017) | partial | compatible | C1/C1b | not shortlisted (fails V31 gate) |
| 24 | DAX / Nikkei first-half-hour momentum (R15-C1/C2) | Li, Sakkas, Urquhart JFM 2022 (PR), 2005-2017 | FDXS / OSE | 3.9 Micro-DAX ticks; 1.4 OSE ticks | not D8 (IBKR FDXS 0.38 EUR/side fees, spread unverified, R16) | - | not owned (Databento Eurex only from 2025-03-10) | no | Phidias lists Eurex (semi-automated); Topstep CME only | same mechanism as K1-cp1-01/E20H6 | not shortlisted |
| 25 | Expiry-day pinning (R17-C2) | Golez, Jackwerth 2012 (PR), to 2009 | ES | aggregate 11 bp | - | - | owned | yes | compatible | E-H3 | not shortlisted |
| 26 | Large-tick fast trend (RD7-C1) | Kurth et al. 2026 (WP) | rates/ags, multi-day | unsized | - | - | owned | - | not Topstep | E21-T1/T2, E22-F1 | not shortlisted |
| 27 | Collective2 "ares" MNQ intraday (R7) | C2 page (LR, C2 labels it hypothetical; rules private) | MNQ | about 37.6 ticks/contract (crude) | 4.119 | - | - | - | - | K1-cp2-01/K1-vwap-01/E20H6 family | existence only |

## S2. Shortlist

Four hypotheses clear the hurdle on published numbers and duplicate no prior trial (S4 checked rows 1-5 against
the index): C1 (row 1), C2 (row 2), C5 (row 5), C4 (row 4); C3 (row 3) is kept as C2's second leg but its
post-2015 size is near the hurdle. The designs register five trials (C1, C2, C3, C4, C5). Power is at the
PUBLISHED size on the research window (s2_power.out v2), one-sided 5% and the first Holm step for k = 5
(alpha 0.01); the sensitivity column uses the verified post-2015 or later-draft sizes. C1's dispersion is per
traded day (about 183 expected traded days in the window). C2/C3 events: the 15 monthly expiries (two shifted to
Thursday), 10 if the roll blackout removes the 5 quarterly dates.

| S2 | Hypothesis | Ratio | n on RW | E[t] | Power 5% | Power Holm-5 | Post-2015 / later-draft sensitivity |
|---|---|---|---|---|---|---|---|
| C1 | Noise-area momentum, MNQ (MES ref.) | 9.32 at NQ 24,000 (MES 4.73 at ES 6,000) | about 183 traded days of 299 | 1.26 (1.11) | 0.35 (0.30) | 0.14 (0.11) | no independent S&P test after publication distinguishable from zero, the latest negative; NQ pointer +41 ticks, t 1.37 |
| C2 | 3rd-Friday reversal leg | 15.24 | 10-15 | 0.47-0.58 | 0.12-0.14 | 0.03-0.04 | 14.8 bp (2022-23, digitized), n 15: 0.17; off-quarter only -6 bp SOQ basis |
| C3 | 3rd-Friday run-up leg from 17:00 CT | 15.07 (17:00 CT leg, digitized); 16.91 published upper bound | 10-15 | 0.62-0.76 (0.70-0.86) | 0.15-0.19 (0.17-0.22) | 0.04-0.06 (0.05-0.07) | 4.2 bp: 0.08; 1.6 bp: 0.06 |
| C4 | Pre-refunding ZN, as designed (FOMC-conditional) | 5.30 (conditional cell 23.65 bp: 9.93) | 3 | 0.41 (0.85) | 0.11 (0.21) | 0.03 (0.07) | FE 9.40 bp: 0.08; unconditional n 5: 0.13 |
| C5 | Pre-FOMC ZN drift | 4.42 | 10 | 0.53 (sd inferred, N about 171) | 0.13 | 0.04 | 6.9 bp, t 2.24 draft: 0.11 |

**The research window cannot confirm any of them.** The best power is C1's 0.35 at its published size, and DF1
shows that no independent S&P test after publication is distinguishable from zero and that third-party tests
already cover the research window, so a C1 read of it would not be blind. Every event candidate has power of
0.11-0.22 at its published size (0.06-0.17 at the post-2015 or fixed-effects sizes).

Draft test designs (one paragraph each; every parameter is the published one; nothing is chosen from data):

- **C1 noise-area momentum (MNQ).** The rule exactly as published (14-day mean absolute move from the open by
  minute; bands from max/min(open, prior close); checks on the :00 and :30 bars from 09:00 CT; long above the
  upper band, short below the lower; trailing stop at the band or VWAP; flat 15:00 CT), 1 MNQ, market orders at
  D8 cost, roll blackout set, through `screening.screen_candidate`; one registered trial. Because the research
  window is no longer blind for this rule (DF1), the clean read is FORWARD: a frozen paper record from the
  registration date (as E22-F1), with the bar net mean per day t >= 1.645 one-sided after a fixed number of days
  set from the published Sharpe before the first day (at the published size 250 trading days give power about
  0.31 on MNQ and 0.27 on MES; power 0.8 needs about 1,165 trading days on MNQ (4.6 years) and about 1,490 on MES; at the post-publication S&P evidence,
  near zero). The worst drawdown at 1 MNQ ($3.4k [secondary-only] to $4.25k [P], DF1) rules out the 50K and
  100K accounts; only 150K ($4,500) fits, barely.
- **C2/C3 3rd-Friday spike (MNQ).** Monthly a.m.-settlement Fridays from the Cboe calendar (holiday rule: the
  expiry moves to Thursday, 2025-04-17 and 2026-06-18); C3 long 1 MNQ from the 17:00 CT reopen the evening before
  to the 08:30 CT open; C2 short from the 08:30 open to the paper's close (the "complete by about 10:30" remark is
  descriptive and not used to pick an exit). Two trials. Event rule: the 15 monthly expiries in the window, the
  two Thursday-shifted ones included; quarterly expiries carry most of the reversal, and whether the program's roll
  blackout removes the 5 quarterly dates (n 10) must be checked against docs/SCREENING.md before registration (DF2
  did not check the roll splice). The NQ size is from a figure only. 10-15 events give power 0.12-0.19 at the
  published sizes (C3 at the tradable 17:00 CT leg); the owned NQ path's post-sample events (2022-01..2024-02, W_cf, about 26 monthly dates, kept by V41
  "for a hypothesis with a stronger prior") would add power only to about 0.25. Two SEC-approved rule changes in
  the window (GTH trading of expiring a.m. SPX options from 2025-06-10; a.m.-settled SPX dailies from 2026-06-12,
  DF2) could change the mechanism inside the test window.
- **C4 pre-refunding ZN.** Long 1 ZN over the paper's intraday window (07:30-17:00 ET quotes; flat by 15:05 CT)
  on the trading day before each quarterly refunding announcement, only when an FOMC statement fell within the
  preceding five days (the paper's own condition, DF3; the cell labels for the window are as DF3 reads Table 11);
  one trial; 3 eligible events in the research window: power 0.11 at the unconditional 12.62 bp, 0.21 at the
  conditional cell's 23.65 bp (full-sample sd; the cell's sd is not published). Two of the three pre-TRA days
  (2025-10-31, 2026-01-30) are month-end dates whose ZN research-window trades K2-monthend-01 already recorded, so
  a research-window read is not blind on them. The figures are cash-Treasury returns; the futures size is a 0.69
  conversion that E.20 assumed and nobody sourced.
- **C5 pre-FOMC ZN.** Long 1 ZN from 18:00 CT two days before each scheduled FOMC statement to 11:00 CT the day
  before; one trial; 10 events; power 0.13 (the per-event sd is DF3's inference from N about 171, not
  published). The window was read off the authors' average-return figure, and the t-statistic moved from 2.24 to
  2.82 between drafts: both are selection warnings.

### Execution triage (user addenda 4 and 5): Group A, Group B, one calibration slice

Sources: NM1_nearmiss_table.json (378 rows; 192 positive recorded gross; 119 cover fees) and NM2_exec_triage.md/.json
(ExecTriage-OpusXHigh: 119 rows classified from the 54 distinct rule texts: 52 momentum or breakout, 38 ML-sign,
21 time-based, 8 fade entries; every exit time-based; 17 rows fail mainly on cost under the lead's rule, 11 of
them momentum and 6 Gate 0 ML, none a fade). The lead's rule, fixed before ranking (Open choice 19): Group A needs
(i) an entry against the move, (ii) gross > fee ticks, (iii) RT - gross below the realistic passive saving,
(iv) failure mainly on cost, read as gross t >= 1.0 with net < 0. Realistic passive saving per side under
TopstepX's trade-through fills (NM2's arithmetic from the D8 half-spread and the published adverse-fill shares, not
a published figure): MNQ +0.36 to +0.68 ticks, MES -0.57 to +0.06, MGC +0.39 to +1.17 (no gold source), MCL -0.21
to +0.45, 6E-class -0.52 to +0.26, ZN-class -0.78 to 0.00; touch fills would save 0.2-2.2 ticks but TopstepX does
not give them. Evidence: Lalor-Swishchuk find 65.8-88.8% of passive fills adverse on ES, NQ, CL and ZN in the TT
simulator, which fills only on trade-through (R18); DeLise: a resting ZN fill is followed by a -0.45 tick mid move
(RD8); non-HFT ES market makers lose $0.97 per contract at 1 minute (Baron-Brogaard-Kirilenko, R17). Missed-fill
cost is not quantified in any source.

**Group A: empty (NM2 confirms).** No earlier rule meets all four conditions. Nearest, each failing (iv):
K3-ldnrev-01 6S confirmation (gross 1.91 vs RT 2.65, gross t 0.58, n 55); K4-ovr-01 NG confirmation (0.72 vs
1.67, t 0.42, n 1,091; also fails (iii)); F3_3 opening-30-min to close (MES, 1.20 vs 2.03, gross t about 0.75 by
NM2's approximation; a fade of the 08:30-09:00 move set by the statistic's sign; also fails (iii)). The fades with
gross t >= 1 either already covered their RT and failed on non-cost grounds (K3-ldnrev-01 6E/6J research, n 12-13,
null at confirmation) or sit below the fee line (C-H1, C-H3, G2.ETH, NM2). Momentum near-misses with high gross t
(K2-cp1-01 ZF/ZN, K3-cp1-01 6E/6B) are excluded by addendum 5.

**Group B: one candidate, B1** (R17-C1): C2's mechanism with a resting sell limit at the 08:30 CT open price of
the monthly a.m.-settlement Friday, filled only on trade-through, cancelled if unfilled by a cutoff (the lead's
design parameter, not a published one: it must be fixed in a pre-registration before any data is read; NM2 5b),
covered at the paper's close. Published mechanism: the derivative payoff bias. Since about 70% of the reversal happens in the
first 30 minutes (DF2), a limit that waits for a trade-through above the open fills mainly on days the spike keeps
rising, which is the adverse-selection case R18 measures; the price saving is under 1% of the published move
(NM2). Not testable on owned 1-minute bars. Not proposed: generic slow market making (negative, R17), expiry pinning (unsized, pre-2010),
USO/GSCI roll (multi-day), OBI fades (die within 1 s; HFT ban).

**Shared calibration slice and test data spec (no quote requested, nothing bought).** Databento GLBX.MDP3 schemas
`trades` and `mbp-1` (`mbo` only if queue position matters, which C6 makes moot at Topstep): (a) calibration
2019-05..2024-02-29 only (ending before the March 2024 embargo and holdout-2), MNQ and MES: the monthly expiry
Fridays 2022-01..2024-02 (about 26, post-sample for the paper) and the evening before each, plus 20 second-Friday
(non-expiry) control dates 2019-05..2024-02 (NM2), for the trade-through fill probability and the 1-60-minute
markout of a limit at the open; no rule outcome computed; (b) test: `trades` + `mbp-1` for MNQ on the
15 expiry Fridays in the research window (and Thursday 17:00 CT to Friday 08:30 CT for C3); one registered trial
per rule-execution pair. Published prices on file: TBBO 5 days NQ $3.58, MNQ $8.62 (E.0 log, cited by R4); OPRA
$199/month (R2). A logged quote and the user's approval come first.

## Re-dig findings (user addendum 1): earlier verdicts the deeper reading supports, weakens or overturns

| Verdict or closure | Reader | Effect | Basis (quoted in the reader file) |
|---|---|---|---|
| E20H6 T1-T3 FAIL | RD1, RD5, R1 | supports | Baltussen's equity coefficient decays in-paper; Rosa's out-of-sample disappearance; Mesfin's MNQ families gross 0.07-1.50 NQ points; Adams et al.: market-maker net gamma positive in 88% of intervals, about 0.7 bp, "not a feasible trading strategy" |
| E20H6 as a replica | RD1 | weakens (not the FAIL) | H6 exits 1-2 minutes before the close (14:58 bar, fill about 14:59 CT), inside the last ten minutes where the Aalto thesis places most of the effect |
| E.14 C2 stop | RD5 | supports | SqueezeMetrics GEX matches Baltussen's NGE ("virtually identical results"); most negative-gamma days predate 2011 |
| K1 Tier B; K2 auction cycle; E16-H3 | RD1, RD2 | supports | Lou-Yan-Zhang short holds unprofitable after costs; SR 1188: "do[es] not persist at the same magnitude" |
| K2-predrift-01; V34's drop of pre-announcement drift | RD8 | supports | Kurov et al.'s sizes are sign-adjusted by the unknown surprise; no ex-ante rule; sample ends 2014-03 |
| V34's drop of closing-auction distortions | RD8 | supports | index-level deviation 0.93 bp (2.2 MES ticks), reverting after 16:00 ET |
| V34's reason for dropping noise-area momentum ("unsized") | R10, DF1 | weakens the "unsized" basis (not a result) | the authors' FAQ sizes it; post-publication S&P tests are not distinguishable from zero |
| K3-ldnrev-01, K3-ecbfix-01 nulls | RD4 | supports | Krohn-Mueller-Whelan: futures reversal 0.64 bp, "turn negative once transaction costs are taken into account"; FCA: reversals "disappear from 2015 onwards" |
| K6-limitcont-01 | RD4 | supports | continuation happens in the opening gap (Janardanan-Qiao-Rouwenhorst), before the 08:45 CT entry |
| K4-ngpre-01, K4-eia*, K5-fomc-01, PM fix, C1/C1b | RD3, RD6 | supports | Gu-Kurov-Stan JFM 2026: NG -0.092% from 90 to 5 min before storage (2.8 MNG ticks vs hurdle 8.03); post-2014 decay; HFTs take the first 50 ms |
| K4-apipre-01 | RD3 | weakens slightly | Alturki-Kurov JFM 2022: 4.5 MCL ticks, below the 4.75 hurdle, only in low liquidity |
| E.13 ranking (C1 > C2 > C3) | RD6 | supports | no source argues for reordering; GEFS archive from 2017 and ECMWF CC-BY since 2025-10-01 weaken two cost facts behind weather (C4), which still ranks fourth |
| V38 sentence "no published post-2015 intraday effect on the 17 roots exceeds 1.5 x the D8 round trip" | RD2, DF3, RD4, DF2 | weakens (as far as the evidence goes) | two working papers whose samples run past 2015 report pre-refunding (cash) and pre-FOMC (futures) drifts above the hurdle, but neither publishes a post-2015 estimate (DF3: "WEAKENS only as far as the cash evidence goes"); the only post-2015 estimates (ES 3rd-Friday reversal 14.8-17.6 bp, digitized) are not significant alone |
| V38/V39 trend closure for prop accounts | RD7 | supports | Lou-Polk-Skouras: equity-index TSMOM earns its alpha overnight (1.40%/month, t 3.24); intraday -0.10%, t -0.24 |
| E21 T1-T4 FAIL | RD7 | supports | Hurst-Ooi-Pedersen 2010-2016 gross Sharpe 1-month 0.06, 12-month 0.73; Baltas-Kosowski daily 2.63 -> 0.37 |
| E22-F1 design | RD7 | weakens (small-tick contracts) | Kurth et al.: fast trend collapsed on small-tick contracts (MNQ, M2K, M6E), held on large-tick ones |
| V39 commodity event drift closure | R5, RD3 | supports | Brandt-Gao: geopolitical news enters oil "at once without follow-on momentum" |
| E.19 rule R040 (news flatten not required) | R9 | overturns (the rule changed) | Topstep Tier 1 window (2026-10-10..16) |

## Prop landscape and outcome data (R8, R9, R16)

- No firm found allows both full automation and overnight holds (R9). Automation-friendly firms all flatten daily:
  Topstep (API), FundedNext (terms 2.2.6, 2026-09-25: "automated trading bots ... is allowed"), DayTraders.com,
  MFFU, Lucid, Tradeify, Bulenox (Apex, Lucid, Tradeify and Bulenox facts rest on search summaries [secondary-only],
  R9). Overnight plans allow semi-automation at most (Phidias Premium; The5ers Futures
  Swing, no algorithmic trading; ETF Diamond Hands by written authorization). No firm names British Columbia.
- Non-CME venues (R16): Phidias's rules page lists Eurex (semi-automated only; its terms list CME only); Apex and
  Tradeify Eurex access only from search summaries; no firm found for ICE Europe, OSE, SGX, HKEX, INE or SHFE.
  Databento: Eurex from 2025-03-10; ICE Europe Commodities and ICE US from 2018-12-23; no OSE, HKFE, SGX, INE or
  SHFE futures dataset.
- Outcome data (R8, firm pages unless stated): Topstep 2025: 16.8% of Combines passed, 51.8% of individuals ever
  funded, 33.3% of funded individuals paid at least once (2024: 12.4%, 46.6%, 28.3%); FPFX Tech cross-firm (vendor):
  14% pass, 45% of passers paid, 7% of all participants; FTMO payouts about 35-55% of revenue (pointer).

## S3. Closing assessment

The evidence says an intraday futures edge that survives retail costs and prop rules is possible on paper but not
demonstrable with what the program owns, and the one frequent candidate weakened as soon as others tested it.
(1) The effects with large published sizes are rare events: the 3rd-Friday spike, the refunding and pre-FOMC
Treasury drifts and the FOMC-day reversal come 3 to 15 times in the research window, so power is 0.11-0.22 at
the published sizes and 0.06-0.17 at the post-2015 sizes, and two of them shrank after 2015 or between drafts.
(2) The one frequent candidate, noise-area momentum, had the right size in-sample (power 0.35 on the window at
that size), but no independent S&P test after publication is distinguishable from zero and the latest are
negative, the only positive Nasdaq test is a pointer with t 1.37, third-party results already cover the research
window, and its drawdown at one MNQ exceeds the 50K and 100K trailing limits. (3) Order-flow and headline
information is priced within one to five seconds on ES, NQ, ZN and CL (Takahashi; Chordia et al.; Brandt-Gao;
CEA: "very close to zero" after five minutes), below retail latency and inside the HFT ban. (4) Passive execution
does not rescue the near misses: under TopstepX trade-through fills most passive fills are adverse (R18), the
realistic saving per side is at most about 0.7 MNQ ticks and near or below zero for MES, ZN and FX (NM2), slow
market making in ES loses money (R17), and Group A is empty. (5) The base rates are poor and the terms keep
tightening: Topstep's own 2025 funnel pays about a third of funded individuals; fewer than 1% of Taiwan day
traders and about 3% of persistent Brazilian mini-index day traders profit (R11); no audited multi-year intraday
futures record was found (R7); Topstep added a Tier 1 news window this month (R9); no firm allows automation with
overnight holds. The honest odds that any intraday edge is reachable at retail costs and prop rules are low.
The only clean test left is forward: a frozen paper record of C1 on MNQ, with the expectation that it fails.
