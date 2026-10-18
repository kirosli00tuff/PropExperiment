# Stage E.25 R0a: index of every mechanism tested (cumulative N = 538)

Extraction only, no evaluation. Written 2026-10-18 01:3x-01:5x PDT (`date`: Sun Oct 18 01:34 PDT 2026 at start). All clock times CT unless stated. Outcome labels are copied as recorded (inventory `tier`, STAGES.md, stage RETURN files, registry). "Tier B" means screened on the research window, not confirmed. Sources: reports/stage_e23_briefs/inventory/{K1..K8,CDE,H6}.md/.json; docs/STAGES.md lines 1-200; `uv run python -m screening.trial_registry status`; reports/E.12_RETURN.md; reports/E.20_RETURN.md; reports/stage_e20_search/configs.csv; reports/E.21_RETURN.md; reports/E.22_RETURN.md; reports/E.23_RETURN.md; reports/stage_e16_prereg_H1..H5.md; reports/E.14_RETURN.md; reports/E.18_RETURN.md.

## 0. N reconciliation (sums to 538, no gap)

| Block | Trials | Cumulative | Source |
|---|---|---|---|
| D.1 (23 hypotheses, 5 families) | 23 | 23 | STAGES.md Stage D.1; CDE.md rows 1-15, 17-24 |
| D.1b C-H4 (Family F admitted zero) | 1 | 24 | STAGES.md D.1b "cumulative N = 24" |
| D.1d re-tests RT1-RT7 (28-statistic sweep admitted zero) | 7 | 31 | STAGES.md D.1d "cumulative N = 31" |
| D.1f frozen list: 21 event statistics (F/G) + 6 Family H | 27 | 58 | STAGES.md D.1f "N = 58"; CDE.md header (58 rows = 31 + 21 + 6) |
| E.3 K2 rates | 44 | 102 | STAGES.md E.3 "N = 102" |
| E.4a K4 energy | 12 | 114 | STAGES.md E.4a "N = 114" |
| E.4b K5 metals (11 coded; cp1 MHG, cp2 MHG never screened; pmfix screened then excluded, counts) | 9 | 123 | STAGES.md E.4b; K5.md Notes ("E.4b added 9 screened K5 trials") |
| E.4c K3 FX (30 coded, 3 excluded on coverage) | 27 | 150 | STAGES.md E.4c "N = 150" |
| E.6 K7 bitcoin | 6 | 156 | STAGES.md E.6 |
| E.7 K1 equity index | 11 | 167 | STAGES.md E.7 |
| E.8 K6 grains/livestock | 27 | 194 | STAGES.md E.8 |
| E.9 K8 cross-market | 4 | 198 | STAGES.md E.9 |
| E.12 Gate 0 (192 family A + 81 family B) | 273 | 471 | E.12_RETURN.md line 28 "198 + 273 = 471" |
| r001-C1 (C1-T1, C1-T2) | 2 | 473 | registry: N 471 -> 473 at 2026-10-09T19:29:06 |
| r002-E16 (E16-H1..H5) | 5 | 478 | registry: 473 -> 478 at 2026-10-10T00:30:15 |
| r003-C1b (C1b-T1, C1b-T2) | 2 | 480 | registry: 478 -> 480 at 2026-10-10T12:17:48 |
| r004-E20H6 (E20H6-T1..T3) | 3 | 483 | registry: 480 -> 483 at 2026-10-11T15:36:20 |
| r005-E20S (E20S-01..45) | 45 | 528 | registry: 483 -> 528 at 2026-10-11T17:43:59 |
| r006-E21 (E21-T1..T4) | 4 | 532 | registry: 528 -> 532 at 2026-10-14T04:12:12 |
| r007-E22 (E22-F1) | 1 | 533 | registry: 532 -> 533 at 2026-10-16T02:12:01 |
| r008-E23 (5 trigger-holds) | 5 | 538 | registry: 533 -> 538 at 2026-10-17T03:33:45 |

Check: 31 + 27 = 58; 58 + 44 + 12 + 9 + 27 + 6 + 11 + 27 + 4 = 198; 198 + 273 = 471; 471 + 2 + 5 + 2 + 3 + 45 + 4 + 1 + 5 = 538. Unreconciled detail: the registry header prints "N = 538 (9 lines)" but lists 8 registered entries r001-r008 (the extra line is not shown). The registry covers N 471 -> 538 only; N <= 471 comes from STAGES.md and the stage RETURN files (E.12_RETURN.md: "no machine-readable N ledger exists" before E.12).

Cluster totals from the inventories: K1 11, K2 44, K3 30 coded (27 counted), K4 12, K5 11 coded (9 counted), K6 27, K7 6, K8 4 = 145 coded, 140 counted (matches the E.3-E.9 rows above).

Not in N (see section 17): K9-anncday-01 draft, C2 (stopped), ML-route v1 members, K1-predrift-01, K2 X-01..X-09, K6 catalog exclusions.

## 1. D.1 / D.1b / D.1d / D.1f: MES families (31 trials + 27 frozen-list statistics = 58)

Instrument MES for all rows (no W_ext data). D.1/D.1b/D.1d screened on train window 2025-04-01..2026-05-13; D.1f ran the frozen 58-test list once on the extension (2020-02-03..2024-02-29). Side inputs: none beyond own bars unless stated. Outcome for every row in this section: D.1 screen fail (STAGES: "none cleared the robust power-gate verdict"); D.1f "composite fail; Holm reject False; no member passed confirmation (Holm rejects none of 58)"; classes C1-C5 and C7 null under NULL_CRITERIA.md; C6 (passive execution, C-H4) not run, closed by scope decision (D.1g), "no C6 null statement exists". All 58 are on the frozen D.1f list recorded as "D.1f Tier A" in CDE.md.

| id | mechanism | decision CT / hold | side inputs | class |
|---|---|---|---|---|
| A-H1 | european-open overnight drift: every trade date at 02:00 ET window | 01:00, about 60 min | none | C1 |
| A-H2 buy / sell | rth close window: every trade date 15:30 ET, buy and sell as two trials | 14:30 to 15:00 | none | C1 |
| A-H3 | weekend effect: Monday and Friday trade dates, RTH hold | 08:30 to 15:00 | none | C1 |
| A-H4 eth / rth | session-open hold, eth leg (about 15.5 h) and rth leg (08:30-15:00), two trials | session open; 08:30 | none | C1 |
| B-H1 hold 5 / hold 75 | opening-range breakout: first close beyond 08:30-08:45 range by 4 ticks; 5 or 75 min hold, two trials | variable from 08:45 | none | C2 |
| B-H2 | prior-day stop cascade: first RTH close through prior session high/low by 4 ticks | variable from 08:30, <= 15 min | none | C2 |
| B-H3 breakout / fade | breakout of 08:30-09:00 range by 4 ticks, follow and fade legs, two trials | variable from 09:00, 30 min | none | C2 |
| B-H4 | narrow-range breakout: OR15 width <= 40th pct of last 20, then close-through 4 ticks | variable from 08:45, 30 min | none | C2 |
| C-H1 | magnitude-conditioned reversal: trailing 5-min return magnitude rank in [0.20, 0.60] of last 120 | any bar, 5 min | none | C3 |
| C-H2 | post-spike exhaustion fade: bar with volume z > 3.0 or range ratio > 3.0 vs trailing 60 | any spike bar, 2 min | none | C3 |
| C-H3 | close-location-value reversal: bar with abs CLV >= 0.80 and range > 1.5x trailing mean | any bar, 3 min | none | C3 |
| C-H4 | passive-fill reversal: C-H1 signal entered with resting limit 1 tick off close, TTL 5 bars (D.1b) | any bar, 5 bars | none | C6, not run (D.1g closed) |
| D-H1 | trailing-vol regime gate: bottom tercile of last 60 EWMA vol snapshots | bar 60 of trade date (about 18:00 CT prior evening), 30 min | none | C4 |
| D-H2 | inverse-vol sizing: size 1-5 micros by inverse EWMA vol | bar 60, 30 min | none | C4 |
| D-H3 | range-compression gate: trailing 20-bar range below 20th pct of last 250, close beyond prior 20-bar high/low | any bar, 15 min | none | C4 |
| D-H4 | overnight gap fade: abs gap rank in [0.20, 0.80] of last 60 | first bar of trade date, 30 min | none | C4 |
| E-H1 | scheduled macro drift: FOMC / CPI / NFP release dates, overnight-through-day hold | first bar (about 17:00 CT prior evening), 14.5-20 h | release table | C5 |
| E-H2 | post-release momentum: release minute (CPI/NFP 08:30 ET, FOMC 14:00 ET) with 5-min reaction range > 2.0x baseline | end of 5-min reaction window, 10 min | release table | C5 |
| E-H3 | quarterly witching short: 3rd Friday of Mar/Jun/Sep/Dec | 14:30 to 15:00 | calendar | C5 |
| E-H4 | turn-of-month long: last trading day of month and first 3 of next | trade-date open, about 22 h | calendar | C5 |
| RT1-RT4 (D.1d) | B-H1 / B-H3 re-run on 5-min bars (OR 08:30-09:00, +/-4 ticks); hold 1 bar, 15 bars; breakout leg; fade leg | variable from 09:00 | none | C2 |
| RT5 (D.1d) | C-H2 spike fade on 5-min bars | any 5-min bar, 1 bar | none | C3 |
| RT6, RT7 (D.1d) | D-H1 / D-H2 with daily-observation EWMA vol V_d | bar 60, 30 min | none | C4 |
| F6_1 overnight_range_position | position of 08:30 open in ETH high-low range predicts 08:30-09:30 return (Family F) | 08:30, 60 min | none | C2 |
| F4_1 rth_open_crossing | bar 09:00-14:29 crossing the 08:30 open; 15-min refractory | crossing bar, 15 min | none | C2 |
| F4_4 round_number_multiples_of_100 | approach of a multiple of 100 index points, any session | approach bar, 15 min | none | C2 |
| G2.RTH.30, G2.ETH.30, G2.ETH.5 (Family G) | slot closing beyond max high / min low of earlier slots in segment | slot completion, next slot | none | C2 |
| G5.RTH.15, G5.RTH.30 | first RTH slot closing beyond the ETH high or low; up to 2 per day | slot completion, next slot | none | C2 |
| G3.RTH.15 | first RTH 15-min slot closing beyond the 08:30-08:45 opening range | slot completion, to about 15:00 | none | C2 |
| F3_2 bucket pairs 01_02, 02_03, 04_05, 05_06, 06_07, 07_08, 08_09, 10_11, 12_13 (9 trials) | 30-min bucket return predicts next bucket return (e.g. bucket 07 11:30-12:00 -> bucket 08 12:00-12:30) | close of bucket, 30 min | none | C3 |
| F3_3 opening_30min_to_close_momentum; F3_3 overnight_to_close_momentum | 08:30-09:00 return (or first bar to 09:00) predicts 14:30-15:00 return | 09:00 signal, 14:30 to 15:00 | none | C3 |
| G1.RTH.5 | RTH 5-min slot with abs body / trailing same-slot mean abs body >= Q80 | slot completion, next slot | none | C3 |
| H1 NR4 / H2 NR7 / H3 inside-day ORB | previous-day range pattern (NR4, NR7, inside day), then first OR30 close-through (Family H) | from 09:00, to 14:58 | none | C7 |
| H4 / H5 | bottom-tercile prior range breakout / top-tercile prior range opening-range fade (OR30) | from 09:00, to 14:58 | none | C7 |
| H6 | prior-close location follow-through: CLV of d-1 >= 0.8 buy, <= 0.2 sell | 08:30 bar, fill 08:31 to 14:58 | none | C7 |

Row count: 35 table rows covering 58 statistics (A-H2, A-H4, B-H1, B-H3 hold two trials each; F3_2 nine; F3_3 two). D.1 24 + RT 7 = 31; F/G 21 (F6_1, F4_1, F4_4, G2 x3, G5 x2, G3, F3_2 x9, F3_3 x2, G1); H 6.

## 2. K1 equity index (E.7, 11 trials, all "Tier B"; MNQ/M2K/MYM; W_ext price path NQ, RTY, none for MYM)

| id | mechanism | instruments | decision CT / hold | side inputs | outcome |
|---|---|---|---|---|---|
| K1-cp1-01 | sign of 08:59 close vs trade date's first bar (17:00 CT d-1) open; momentum | MNQ, M2K, MYM | signal 08:59, fill 14:30, exit 14:59 | none | Tier B (3 trials) |
| K1-cp2-01 | first close beyond 08:30-08:45 opening range by 4 ticks; momentum | MNQ, M2K, MYM | variable from 08:45 (latest 14:59), 75 bars or F | vendor tick size (label "tick history not source-verified") | Tier B (3) |
| K1-cp3-01 | prior day CLV >= 0.8 buy / <= 0.2 sell | MNQ, M2K, MYM | 08:30, fill 08:31, exit 14:59 | none | Tier B (3) |
| K1-vxnband-01 | VXN prior close < 20 or >= 30 and bar close breaching C_prev x (1 +/- V/1600); fade, first breach | MNQ | variable 08:30-14:29, 30 min | VXN daily close (Cboe VXN_History.csv) | Tier B |
| K1-vwap-01 | sign of bar close vs session VWAP from 08:30; stop-and-reverse, <= 20 entries/day | MNQ | every bar 08:30-14:57, reverse on signal, final 14:58 | none | Tier B |

Rows 5, trials 11. Excluded (0 trials): K1-ml-01, K1-predrift-01.

## 3. K2 rates (E.3, 44 trials, all Tier B; ZT, ZF, ZN, TN, ZB, UB)

| id | mechanism | instruments | decision CT / hold | side inputs | outcome |
|---|---|---|---|---|---|
| K2-cp1-01 | sign of 07:49 close vs first bar (17:00 CT d-1) open; momentum | ZT ZF ZN TN ZB UB | 13:29, fill 13:30, exit 13:59 | none | Tier B (6) |
| K2-cp2-01 | first close beyond 07:20-07:35 opening range by 4 ticks | 6 roots | variable 07:35-13:59, 75 min | none | Tier B (6) |
| K2-cp3-01 | prior day CLV >= 0.8 buy / <= 0.2 sell | 6 roots | 07:20 to 13:59 | none | Tier B (6) |
| K2-aucpre-01 | tenor-matched Treasury auction date: SELL 181 min before auction time T_a, exit T_a - 1 | 6 roots | T_a - 181 (08:59 or 07:29), 179 min | Treasury auction calendar | Tier B (6) |
| K2-aucpost-01 | same auction dates: BUY at T_a + 4, exit T_a + 184 | 6 roots | T_a + 4 (12:04 or 10:34), 180 min | Treasury auction calendar | Tier B (6) |
| K2-fomcpost-01 | scheduled FOMC statement date at 13:00 CT: BUY 13:29, exit 15:04 | 6 roots | 13:29, 95 min | FOMC statement dates | Tier B (6) |
| K2-predrift-01 | ISM Services release (09:00 CT): sign of 08:49 close vs 08:30 open; momentum | ZN, ZB | 08:49, exit 09:04 (15 min) | ISM Services release dates | Tier B (2) |
| K2-monthend-01 | trade dates N-1 and N of each month: unconditional BUY | 6 roots | 07:20 to 15:04 | month-end calendar | Tier B (6) |

Rows 8, trials 44. Excluded (0 trials): K2-ml-01, X-01 K2-scalp-01, X-02 K2-hftbook-01, X-03 K2-auc5d-01, X-04 K2-eom2d-01, X-05 K2-basis-01, X-06 K2-aucother-01, X-07 K2-btc-01, X-08 K2-surprise-01, X-09 K2-rollspread-01.

## 4. K3 FX (E.4c, 30 coded, 27 counted; 6E, 6A, 6B, 6C, 6J, 6S, 6N)

| id | mechanism | instruments | decision CT / hold | side inputs | outcome |
|---|---|---|---|---|---|
| K3-cp1-01 | sign of 07:49 close vs Globex-open 17:00 CT d-1 bar open; momentum | 6E 6A 6B 6C 6J (6S, 6N) | 13:29, exit 13:59 | none | Tier B (5); 6S, 6N not run (excluded on coverage) |
| K3-cp2-01 | first close beyond 07:20-07:35 opening range by 4 ticks | 6E 6A 6B 6C 6J 6S (6N) | variable 07:35-13:59, 75 min | none | Tier B (6); 6N not run |
| K3-cp3-01 | prior day CLV >= 0.8 buy / <= 0.2 sell | 6E 6A 6B 6C 6J 6S 6N | 07:20 to 13:59 | none | Tier B (7) |
| K3-ldnrev-01 | month-end: 10-min pre-London-fix move M; fade (BUY if M < 0) | 6E, 6J, 6S | T_L + 4 = 10:04, exit T_L + 20 | month-end table, E&W bank holidays, London fix clock | Tier A on 6E; Tier B on 6J, 6S; E.22 confirmation 6E: NULL |
| K3-ldnmom-01 | S = close(T_L - 13) - open(T_L - 15); momentum into London fix | 6E, 6J | T_L - 13 = 09:47, exit T_L + 5 | London fix clock, bank holidays | Tier B (2) |
| K3-mehedge-01 | month-end: minus sign of Nikkei month return R_eq | 6J | T_L - 61 = 08:59, exit T_L - 3 | literal Nikkei month-end table | Tier B (EUR leg not traded) |
| K3-ecbfix-01 | every FX full session not a TARGET closing day: SELL 01:00 CT to T_E, then BUY T_E + 1 to 15:05 | 6E | leg 1 00:59, leg 2 T_E = 07:15 | TARGET closing days, ECB fix clock (14:15 Berlin) | Tier B |
| K3-tkypre-01 | gotobi day / last Tokyo business day of month: SELL from 17:29 d-1 to T_T | 6J | 17:29 CT d-1 | Tokyo gotobi / business-day calendar, Tokyo fix clock (09:55 JST) | Tier B |
| K3-tkypost-01 | Tokyo business day: BUY from T_T to 01:00 CT | 6J | T_T d-1 = 18:55 CST / 19:55 CDT | Tokyo business-day calendar | Tier B |

Rows 9, trials 30 (27 counted). Excluded (0 trials): K3-mehedge-01 on 6E (EUR; never declared).

## 5. K4 energy (E.4a, 12 trials; MCL, NG)

| id | mechanism | instruments | decision CT / hold | side inputs | outcome |
|---|---|---|---|---|---|
| K4-cp1-01 | sign of 08:29 close vs 17:00 CT Globex-open bar; momentum | MCL, NG | 12:59, 13:00 to 13:29 | none | Tier B (2) |
| K4-cp2-01 | first close beyond 08:00-08:15 opening range by 4 ticks | MCL, NG | variable 08:15-13:29, 75 bars | none | Tier B (2) |
| K4-cp3-01 | prior day CLV >= 0.8 buy / <= 0.2 sell | MCL, NG | 08:00 to 13:29 | none | Tier B (2) |
| K4-ngpre-01 | every EIA weekly NG storage release: SELL 90 min before, exit 30 min after | NG | T - 91 (07:59 or 09:29), T - 90 to T + 30 | EIA NGS storage release table | Tier A (NG); E.5 confirmation: NULL (fails Holm) |
| K4-apipre-01 | WPSR Wednesdays: sign of API-report move R_API (Tuesday 15:24/15:39 closes); momentum into 09:30 | MCL | 07:29, 07:30 to 09:29 | WPSR release table, API report times, federal Monday holidays | Tier B |
| K4-eiafade-01 | WPSR release with 14-min post-release move abs M >= 0.005; fade | MCL | T_W + 14 (09:44-12:14), exit 13:29 | WPSR release table | Tier B |
| K4-eiamom-01 | WPSR Wednesday: sign of r3 (09:29 and 09:59 closes); momentum | MCL | 14:29, 14:30 to 14:59 | WPSR release table, NYSE early closes | Tier B |
| K4-ovr-01 | trailing return at t in {09:00..13:00} at or beyond P10/P90 of 20 prior days; fade | MCL, NG | t-1 (08:59..12:59), 60 min | none | Tier B (2) |

Rows 8, trials 12.

## 6. K5 metals (E.4b, 11 coded, 9 counted; MGC, MHG)

| id | mechanism | instruments | decision CT / hold | side inputs | outcome |
|---|---|---|---|---|---|
| K5-cp1-01 | sign of 07:49 (MHG 07:39) close vs 17:00 CT open bar; momentum | MGC, MHG | MGC entry 11:59 (MHG 11:29) to 12:29 | metals calendar | MGC Tier B; MHG n/a (never screened; coverage) |
| K5-cp2-01 | first close beyond opening range [07:20, 07:35) (MHG 07:10) by 4 ticks | MGC, MHG | variable 07:35-12:29, 75 bars | metals calendar | MGC Tier B; MHG n/a (never screened) |
| K5-cp3-01 | prior day CLV >= 0.8 buy / <= 0.2 sell | MGC, MHG | 07:20 to 12:29 | metals calendar | Tier B (2) |
| K5-preauc-01 | LBMA gold AM auction day: unconditional SELL 30 min before 10:30 London | MGC | T-31 (03:59 or 04:59), T-30 to T-1 | LBMA gold AM auction dates | Tier B |
| K5-pmfix-01 | LBMA gold PM auction day: sign of close(T_P+1) - close(T_P-1); momentum | MGC | T_P + 1 (09:01 or 10:01), 10 min | LBMA gold PM auction dates | n/a (screened, then excluded on the mean-hold floor; counts in N) |
| K5-fomc-01 | FOMC statement date 13:00: sign of close(13:04) - close(12:59); momentum | MGC | 13:04, fill 13:05, exit 13:15 | FOMC statement dates | Tier A; E.22 confirmation (GC bars, U8): NULL |
| K5-ovr-01 | trailing 60-min return at t in {08:20..12:20} at or beyond P10/P90 of 20 days; fade | MGC, MHG | t-1, 60 min | none | Tier B (2) |

Rows 7, trials 11 (9 counted).

## 7. K6 grains, oilseeds, livestock (E.8, 27 trials; ZC, ZW, ZS, ZM, ZL, HE, LE)

| id | mechanism | instruments | decision CT / hold | side inputs | outcome |
|---|---|---|---|---|---|
| K6-cp1-01 | sign of 08:59 close vs first bar of trade date; momentum | ZC ZW ZS ZM ZL HE LE | 12:44, to 13:14 (livestock 12:58) | none | Tier B (7) |
| K6-cp2-01 | first close beyond 08:30-08:45 opening range by 4 ticks | 7 roots | variable 08:45-13:14, 75 min | none | Tier B (7) |
| K6-cp3-01 | prior day CLV >= 0.8 buy / <= 0.2 sell | 7 roots | 08:30 to close | none | Tier B (7) |
| K6-crushgap-01 | soybean crush gap G = GPM_open - GPM_close(d-1) <= -0.02 or >= +0.02 (GPM = 0.022 ZM + 11 ZL - ZS); trade ZS | ZS (signal legs ZM, ZL) | 08:30 to 13:14 | ZM and ZL bars | Tier B |
| K6-limitcont-01 | prior day settlement proxy moved exactly +/- initial limit L ticks; momentum | HE, LE | 08:44 to 12:59 | HE/LE daily price limits, settlement-proxy window | Tier A on HE; Tier B on LE; E.22 confirmation HE: NULL BY INACTIVITY (10 trips < 30); LE 0 trips |
| K6-wasdepre-01 | WASDE date: sign of close(10:29) - open(08:30); momentum | ZC, ZS | 10:29, 10:30 to 11:15 | WASDE release dates (12:00 ET) | Tier B (2) |
| K6-wasdepost-01 | WASDE date: sign of close(11:14) - close(10:59); momentum | ZC | 11:14 to 13:14 | WASDE release dates | Tier B |

Rows 7, trials 27 (7+7+7+1+2+2+1). Excluded (0 trials): K6-ml-01, K6-ovr-01, K6 catalog list (K6-crush3-01, K6-crushavg-01, K6-surprise-01, K6-stocksrev-01, K6-relmin-01, K6-cpfade-01, K6-lvrpt-01, ...).

## 8. K7 bitcoin (E.6, 6 trials; MBT; all six "Tier B" per STAGES.md E.6; the inventory tier field reads None)

| id | mechanism | instruments | decision CT / hold | side inputs | outcome |
|---|---|---|---|---|---|
| K7-cp1-01 | sign of 08:59 close vs first bar (17:00 CT d-1) open; momentum | MBT | signal 08:59, fill 14:30, exit 14:59 | none | Tier B |
| K7-cp2-01 | first close beyond 08:30-08:45 opening range by 4 ticks | MBT | variable 08:45-14:59, 75 bars | none | Tier B |
| K7-cp3-01 | prior day CLV >= 0.8 buy / <= 0.2 sell | MBT | 08:30, fill 08:31 to 14:59 | none | Tier B |
| K7-expiry-01 | MBT last trading day: long only, 300 min before expiry | MBT | 04:59 or 05:59 to T_exp - 1 | MBTX last-trading-day table | not traded (every research expiry day in a roll blackout) |
| K7-rev2h-01 | two 2-hour block returns (08:30-10:29, 10:30-12:29); fade | MBT | 10:29 and 12:29, final 14:30 | none | Tier B |
| K7-montrend-01 | Monday: 20 hourly decisions Sunday 18:00 to Monday 13:00 on prior hour's sign; momentum | MBT | hourly, final Monday 14:00 | none | Tier B |

Rows 6, trials 6.

## 9. K8 cross-market (E.9, 4 trials)

| id | mechanism | instruments | decision CT / hold | side inputs | outcome |
|---|---|---|---|---|---|
| K8-flight-01 H30 | first 5-min MES block return at or below the 0.5% quantile of prior 20 dates and < 0; always long MGC, hold 30 min | MGC with MES signal | every 5 min 08:35-14:55, exit min(T_e + 29, 15:04) | MES 1-min bars, GC price path | Tier B |
| K8-flight-01 HEOD | same trigger, hold to 15:04 | MGC with MES signal | same | MES bars, GC price path | Tier A; E.22 confirmation: NULL |
| K8-oilcad-01 | 5-min MCL block return abs(r / s(d)) >= 2.0; trade 6C by sign of c1 vs c6 | 6C with MCL signal | every 5 min 08:05-13:25 | MCL bars | Tier B |
| K8-wkndbtc-01 | Monday: weekend MBT move G = P_Sunday 17:59 / P_Friday 14:59 - 1; trade MNQ in sign of G | MNQ with MBT signal | Sunday 18:00 CT to Monday 14:59 | MBT bars, NQ price path | Tier A; E.22: INCONCLUSIVE BY DESIGN (not run) |

Rows 4, trials 4. E.22 cluster statement: K8 NULL.

## 10. E.12 Gate 0, ML route v2 (273 tests; E.12_RETURN.md, stage_e12_gate0_list.json)

| id | mechanism | instruments | decision CT / hold | side inputs | outcome |
|---|---|---|---|---|---|
| gate0A_* (192 tests) | each of 64 covered signals x h60, h120, hF, two-sided date-clustered mean of z x y_norm; signals are the K1-K9 member variables (cp1_ret, cp2_range, cp2_brk, cp3_clv, k1_vwap_dist, k1_vxn_regime, k1_vxn_band, k2_auction_mto/msince, k2_fomc_mto, k2_monthend_msince, k2_predrift_move, k3_ldnmom_trend, k3_ldnrev_move, k3_mehedge_req, k3_ecbfix_*, k3_tky*, k4_*, k5_*, k6_*, k7_*, k8_oilcad_*, k8_wkndbtc_move, k9_anncday) plus g01-g17 (ret30, ret60, ret120, ret_day, gap, rv60, range, prev_ret, vol_state, logvol30, t_index, dow, min_to_rel, min_since_rel, rel_day, month_end, g17_nq/zn/6e/cl/gc/zc/mbt) | vehicles with owned legs (g17_mes, k8_flight_ret, k8_flight_tail uncovered: MES refused) | three decision times per product per day: t1 = O_X + 30, t2, t3 (rates/FX 07:50, 10:20, 12:50; equity/crypto 09:00, 11:00, 13:00; energy 08:30, 10:30, 13:00; grains and livestock 09:00, 10:00, 11:00); horizons h60, h120, hF (forced flatten) | member tables: VXN (k1_vxn_*), release calendars, auctions, FOMC, EIA, WASDE | FAIL (smallest family A p 0.015, g07_range hF, t -2.43; no Holm rejection) |
| gate0B_* (81 tests) | per admissible (vehicle, horizon) pair; rule: cost_multiple 1.5, t_min 3, alpha 0.05, top_fraction 0.2, min_trades 30, ridge_lambda 0.1 | 27 vehicles x 3 horizons (MNQ MGC NG 6E ZL UB MBT MCL ZS TN ZF ZB ZN ZT ZC MYM M2K LE MHG 6S HE 6J 6A 6B 6N ZM ZW 6C; 28 listed, MES refused) | same | same | FAIL; best NG h60 mean gross 5.57 ticks vs cost 1.71 (3.25x), t_B 2.51, p 0.0062, Holm rank 1 of 273 not rejected; eight pairs clear 1.5c (6J hF, HE hF, NG h60/h120/hF, UB h60, ZS hF, ZT hF) |

Rows 2, tests 273 (192 + 81). Gate 0 FAIL; v2 stops.

## 11. E.13 / E.14 C2 (stopped, not a trial, not in N)

| id | mechanism | instruments | decision CT / hold | side inputs | outcome |
|---|---|---|---|---|---|
| C2 | dealer-gamma-conditioned S&P late-session momentum, GEX < 0 at lag 1 | S&P (draft) | late session | SqueezeMetrics GEX daily | stopped at minimum-power rule (135 eligible GEX < 0 dates, floor 200), before freeze, registration, purchase |

## 12. E.16 H1-H5 base-rule batch (r002-E16, 5 trials, 27 price paths 2010-07..2024-02; all FAIL)

| id | mechanism | instruments | decision CT / hold | side inputs | outcome |
|---|---|---|---|---|---|
| E16-H1 | settlement-window intraday momentum: sign of price at S_p - 30 vs prior eligible date's settlement-minute price, pooled | NQ YM RTY ZT ZF ZN TN ZB UB 6E 6A 6B 6C 6J 6S 6N CL NG GC HG ZC ZW ZS ZM ZL LE HE | close of bar S_p - 31 (equity 14:29), S_p - 30 to S_p, 30 min | none | FAIL (Holm no, DSR about 0; Fable-verified) |
| E16-H2 | month-end rebalancing pair: fifth-last trading day, short NQ / long ZN if NQ outperformed ZN month-to-date (else reverse); exit last trading day settlement | NQ (vehicle MNQ) and ZN | settlement minute, multi-day | none | FAIL |
| E16-H3 | Treasury auction cycle: short tenor contract 3 trading days before auction, cover at auction date, long to 5 days after | ZT ZF ZN ZB (2Y, 5Y, 10Y, 30Y) | settlement minute, multi-day | EC-AUC FiscalData auction calendar | FAIL |
| E16-H4 | next-day reversal of the settlement-window move (CP3 port) | 27 roots | O_p + 1 to S_p - 31 | none | FAIL (Holm no, DSR about 0) |
| E16-H5 | equal-risk daily combination of H1-H4 net daily P&L, each scaled by trailing 60-date std | combination | daily | none | FAIL |

Rows 5, trials 5.

## 13. C1 / C1b: backward NG replication (E.13 draft, E.14 freeze, E.17, E.18)

| id | mechanism | instruments | decision CT / hold | side inputs | outcome |
|---|---|---|---|---|---|
| C1-T1, C1-T2 (r001-C1) | backward NG replication: E.12's NG h60 / hF rows rebuilt (q reproduced exactly), model M1 fitted, evaluated on NG 2010-2019; T1 h60, T2 hF | NG | ML decision times, h60 / hF | CME, EIA and Fed calendars 2010-2019 | STOPPED at guard C10 (E.17; g17_mbt n/a by design in 2010-2019, a freeze contradiction; Fable-verified; not rerun) |
| C1b-T1, C1b-T2 (r003-C1b) | C1 re-registered with C10's one fix (g17_mbt and g17_cl exempt), evaluated once on E.17 stores | NG | h60, hF | same | FAIL (T1 NG h60 mean 0.585 ticks vs bar 2.562, t_B -0.83; T2 NG hF -0.113 vs 2.649, t_B -0.41; Fable-verified) |

Rows 2, trials 4.

## 14. E20H6 and E20S (r004, r005)

| id | mechanism | instruments | decision CT / hold | side inputs | outcome |
|---|---|---|---|---|---|
| E20H6-T1 | rest-of-day to last-half-hour momentum (r_ROD): sign of rest-of-day return, every eligible date | NQ price path at MNQ cost | 14:30 (C-30), exit C-2 (14:58) | none | FAIL (893 trades; gross 1.25 ticks vs 4.08 round trip, t_B -0.53) |
| E20H6-T2 | same, only when abs r_ROD above the median of the 60 prior eligible dates | NQ at MNQ cost | 14:30 to 14:58 | none | FAIL (446 trades; t_B -0.95) |
| E20H6-T3 | same, only when previous day's GEX row negative | NQ at MNQ cost | 14:30 to 14:58 | SqueezeMetrics GEX daily CSV | FAIL (134 trades; t_B -0.38) |
| E20S-01..45 | ML-route net pipeline, 2019-05..2024-02, nested CPCV; 45 configurations: ridge lambda {0.01, 0.1, 1} x k {1.5, 2, 3} x h {60, 120, F} (27) and lgbm depth {2, 3} x k {1.5, 2, 3} x h {60, 120, F} (18); 36 features (34 kept from the 67-signal library + rod_ret, rod_absratio) | 17 roots (NG NQ ZN 6E GC ZC ZT ZF ZB UB TN CL ZL ZS RTY HE LE) | decision times t1-t3 plus t4 = F_X - 60 (14:08 equity/rates/FX/energy/gold, 12:18 grains, 12:03 livestock); h60, h120, hF | k1_vxn_* features dropped (no 2010-2019 VXN) | search screen FAIL (median-path t -1.33, PBO 0.60, net Sharpe -0.83; all 45 negative out of sample; best E20S-13 ridge_l0.1_k2_h60 -0.33); no backward test |

Rows 4, trials 48 (3 + 45).

## 15. E.21 multi-day round (r006-E21, 4 trials, 17 roots, 2010-2024; all FAIL, Holm 0.025)

| id | mechanism | instruments | decision / hold | side inputs | outcome |
|---|---|---|---|---|---|
| E21-T1 | TSMOM-12 (Moskowitz-Ooi-Pedersen 2012): 12-month time-series momentum, monthly rebalance | 17 roots | monthly, multi-day | none | FAIL (net Sharpe 0.50 [-0.06, 1.05], t 1.78, p 0.042) |
| E21-T2 | 1/3/12-month trend blend (Hurst-Ooi-Pedersen 2017), equal weights, monthly | 17 roots | monthly, multi-day | none | FAIL (0.44, t 1.56, p 0.064) |
| E21-T3 | equity turn of the month (NYSE day numbering) | NQ, RTY | multi-day around month end | NYSE trading-day calendar | FAIL (0.15, t 0.53) |
| E21-T4 | equal-risk combined book of T2, T3 and E16-H2 component series (trailing 60-date std scaling) | combined | daily | none | FAIL (0.12, t 0.43) |

Rows 4, trials 4.

## 16. E.22 and E.23

| id | mechanism | instruments | decision / hold | side inputs | outcome |
|---|---|---|---|---|---|
| E22-F1 (r007-E22) | micro trend book: Carver EWMAC 8/32, 16/64, 32/128, 64/256, 20% vol target, equal weights, simple rounding, $25K, forward paper test 36 months | 12 micros on E.21 owned paths | daily, next-settlement fills | daily settlement source (pending user approval) | registered; forward test, no verdict (PASS iff one-sided p <= 0.05 and net Sharpe >= 0.3); clock starts after the source is approved |
| E23-MEZFh5, E23-MEZNh5, E23-MEZBh5 (r008-E23) | K2-monthend-01 held 5 trading days: long ZF / ZN / ZB, entered at trigger day's settlement; alpha over the root's E.21 T1/T2 | ZF, ZN, ZB | settlement, 5 days | none | all NULL (discovery 2011-07-27..2019-04-30: alpha t 0.55 / 0.38 / 0.10; confirmation inconclusive by design, power 0.18) |
| E23-H6NQh5, E23-H6NQh20 (r008-E23) | E20H6-T1 reversal held 5 and 20 days | NQ | settlement, 5 / 20 days | none | NULL (alpha t -1.61 / -0.71) |

Rows 3, trials 6 (E22-F1 1 + E23 5). E.23 inventoried 208 triggers and wrote 11 mechanism memos; K8-flight-01 and K1-vxnband-01 labelled "UNCONFIRMABLE ON OWNED DATA"; Holm smallest p 0.309.

## 17. Not trials (named so readers can recognise them)

- K9-anncday-01 (E.10): macro-announcement-day premium, long MNQ/M2K/MYM, 3 trials; draft only, never screened or frozen; K9-vixback-01 and K9-vixspike-01 withdrawn.
- ML-route v1 members K1-ml-01, K2-ml-01, K6-ml-01 (superseded by the ML route, U6); K1-predrift-01 (excluded at E.0).
- K2 X-01..X-09 (E.0 catalog exclusions, e.g. K2-auc5d-01, K2-eom2d-01 multi-day).
- E.13 research: trend and carry after publication, dealer gamma, GFS revisions (research only, no trials).
- D.1g C6 passive-execution queue model (closed, not run).

## Keywords (mechanism class: ids covered)

- release-minute momentum: E-H2; K5-fomc-01; K2-predrift-01; K6-wasdepre-01; K6-wasdepost-01; K4-eiamom-01; K4-apipre-01; K4-eiafade-01 (fade); K2-fomcpost-01; E-H1
- settlement window: E16-H1; E16-H4; E16-H2; E16-H3; E20H6-T1..T3 (last-half-hour momentum); E23-MEZFh5/MEZNh5/MEZBh5 and E23-H6NQh5/h20 (entered at settlement); K6-limitcont-01 (D9.7 settlement proxy); A-H2; E-H3
- opening range: A-H3/A-H4 (session open); B-H1; B-H3; B-H4; RT1-RT4; G3.RTH.15; H1-H5 (OR30); K1-cp2-01; K2-cp2-01; K3-cp2-01; K4-cp2-01; K5-cp2-01; K6-cp2-01; K7-cp2-01
- close location value (prior-day CLV): K1-cp3-01; K2-cp3-01; K3-cp3-01; K4-cp3-01; K5-cp3-01; K6-cp3-01; K7-cp3-01; H6 (D.1f); C-H3; E16-H4 (CP3 port)
- first-bar sign momentum (cp1): K1-cp1-01; K2-cp1-01; K3-cp1-01; K4-cp1-01; K5-cp1-01; K6-cp1-01; K7-cp1-01; E16-H1 (CP1 port); E20H6-T1..T3 (rest-of-day)
- gamma/GEX: E20H6-T3; C2 (stopped)
- VXN / volatility regime: K1-vxnband-01; D-H1; D-H2; D-H3; RT6; RT7; Gate 0 g06_rv60, g09_vol_state, k1_vxn_regime
- lead-lag / cross-market signal leg: K8-flight-01 (MES -> MGC); K8-oilcad-01 (MCL -> 6C); K8-wkndbtc-01 (MBT -> MNQ); K6-crushgap-01 (ZM, ZL -> ZS); K3-mehedge-01 (Nikkei -> 6J); E16-H2 (NQ vs ZN); Gate 0 g17_* features
- VWAP: K1-vwap-01; Gate 0 k1_vwap_dist
- overnight gap: D-H4; Gate 0 g05_gap; K6-crushgap-01 (open vs prior close); A-H1 (european-open overnight drift); F6_1 (overnight range position); F3_3 overnight_to_close_momentum
- auction: K2-aucpre-01; K2-aucpost-01; E16-H3; K5-preauc-01; K5-pmfix-01 (LBMA gold AM/PM auctions); fix windows K3-ldnrev-01, K3-ldnmom-01, K3-ecbfix-01, K3-tkypre-01, K3-tkypost-01
- month-end: K2-monthend-01; E16-H2; E23-MEZFh5/MEZNh5/MEZBh5; E21-T3 and E-H4 (turn of the month); K3-ldnrev-01; K3-mehedge-01; Gate 0 g16_month_end
- trend multi-day: E21-T1 (TSMOM-12); E21-T2 (1/3/12 blend); E21-T4 (combined); E22-F1 (EWMAC micro book)
- reversal / fade: C-H1; C-H2; C-H3; C-H4 (passive); RT5; B-H3 fade leg; H5; K1-vxnband-01; K3-ldnrev-01; K4-eiafade-01; K4-ovr-01; K5-ovr-01; K7-rev2h-01; E23-H6NQh5/h20
- calendar / day-of-week: A-H3 (weekend effect); E-H3 (quarterly witching short); K3-tkypre-01; K3-tkypost-01; K3-ecbfix-01; K8-wkndbtc-01 (Monday); K7-montrend-01 (Monday); Gate 0 g12_dow
- storage / inventory / crop releases: K4-ngpre-01 (EIA storage); K4-apipre-01; K4-eiafade-01; K4-eiamom-01 (WPSR); K6-wasdepre-01; K6-wasdepost-01 (WASDE)
- limit: K6-limitcont-01
- expiry: K7-expiry-01
- bucket / slot predictors: F3_2 bucket pairs; F3_3; G1.RTH.5; G2.*; G5.*
- sizing / gating: D-H1; D-H2; D-H3; RT6; RT7
- ML pattern search (features x horizons): E.12 Gate 0 (273 tests); E20S-01..45; C1-T1/T2; C1b-T1/T2
