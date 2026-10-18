# NM2 Execution triage (Stage E.25, research only; user addenda 4 and 5)

Worker: ExecTriage-OpusXHigh (NM2). Written 2026-10-18 11:16-12:0x PDT, from recorded results only.
The earlier NM2 run left nothing on disk (pages/NM2/ was empty).

Inputs read: NM1_nearmiss_table.json/.md (378 rows; read with `python3 -I`, printing only the needed
fields), R18_queue_fill.md, R17_maker_native.md, R3_orderflow.md, R4_volume_tradeside.md, R16_niche_access.md
(Databento lines), docs/DECISIONS.md (C6 closure, lines 30-45), synthesis.md (the lead's draft, lines 40-66),
reports/stage_e2a_costs.md (D8 definitions and the MES/MNQ bucket table), reports/stage_e0_quotes.md (the
per-product mbp-1/tbbo rows that R4 cites). No market data, no purchase, no quote request, no web fetch.
Machine-readable table: NM2_exec_triage.json (119 rows, with the passive-saving arithmetic and the Group A
clause flags per row). Scripts: scratchpad nm2/dump.py, num.py, build.py (not in the repo).

Units: ticks of the row's vehicle per contract per round trip (RT), as in NM1. Shortfall = D8 RT - gross
(NM1's field). "s" = D8 one-side slippage = half the D8 slip (time-weighted mean half-spread plus depth
term, stage_e2a_costs.md R5). The lead's Group A rule is applied as written in synthesis.md line 62 and
the brief: (A1) entry against the move; (A2) gross > fee ticks; (A3) RT - gross < realistic passive
saving; (A4) failure mainly cost = gross t >= 1.0 with net < 0. NM2 does not change the rule.

## 1. Positive-gross intraday rows whose gross covers fees (119 rows)

Selection: NM1 rows with `gross_covers_fees` true (gross > D8 fee ticks). All NM1 rows are intraday or
single-session (NM1 already excluded the multi-day trials E21-T1..T4, E22-F1, E23-MEZ*/H6NQ*, E16-H2,
E16-H3). Three rows hold across the 17:00 CT reopen inside one trade date (A-H4 ETH leg; E-H1;
K3-tkypost/tkypre on the Tokyo clock); they are flat before the 15:10 CT flatten of their trade date.

Classes are read from the verbatim entry and exit text (dump of the 54 distinct rule texts), not from
side_kind alone. Every exit in the 119 rows is time-based: a market intent at a fixed clock or a fixed
hold (75 bars, 60/120 min, to the flatten), with the engine's flatten and D9.7 price-limit exit as
backstops; no row has a stop or target ("No stop, no target" is explicit in H1/H3/H4). The "limit"
that NM1's order_type_in_text lists for K6-limitcont and E20H6-T1..T3 is the D9.7 price-limit exit, not a
limit order.

Counts: entry class breakout/momentum 52, ML model sign 38 (37 gate0B training-window rows + C1b-T1),
time-based 21, fade/mean reversion 8. Failure class under the lead's A4 rule: mainly cost 17 (11
momentum, 6 gate0B ML), non-cost 101, undetermined 1 (E16-H1: no D8 cost basis in NM1).

Notes on the columns: "gross t ~" marks a gross t that NM1 does not carry and NM2 approximated as
net t x gross / net (D.1/D.1f-era rows, whose net t is a daily-series t; approximate, not recorded).
For gate0B rows NM1's gross t is the recorded per-date t_B; nine of them are negative with a positive
gross mean, as recorded (not reconciled here). Net for gate0B rows = gross - D8 RT (NM1 has no net).
K6 rows: NM1's entry text is empty; the class comes from the shared cp1/cp2/cp3 template (K1-K5).

| # | id | window | veh | n | gross | gross t | RT = fee + slip | shortfall | entry class (read) | exit class | failure class | reason |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | K2-aucpost-01 ZT | research | ZT | 13 | 2.462 | 1.77 | 1.301 = 0.297 + 1.004 | -1.160 | time-based (BUY unconditional at T_a+5 after a Treasury auction) | time-based (fixed clock, no stop or target) | non-cost | net 1.15 >= 0 (shortfall < 0): failed on t or n, not on cost |
| 2 | K2-aucpre-01 TN | research | TN | 15 | 3.133 | 0.62 | 1.174 = 0.168 + 1.006 | -1.959 | time-based (SELL unconditional at T_a-180 before a Treasury auction) | time-based (fixed clock, no stop or target) | non-cost | net 1.96 >= 0 (shortfall < 0): failed on t or n, not on cost |
| 3 | K2-aucpre-01 UB | research | UB | 15 | 2.800 | 0.78 | 1.098 = 0.093 + 1.005 | -1.702 | time-based (SELL unconditional at T_a-180 before a Treasury auction) | time-based (fixed clock, no stop or target) | non-cost | net 1.70 >= 0 (shortfall < 0): failed on t or n, not on cost |
| 4 | K2-aucpre-01 ZB | research | ZB | 15 | 1.867 | 0.63 | 1.089 = 0.088 + 1.001 | -0.777 | time-based (SELL unconditional at T_a-180 before a Treasury auction) | time-based (fixed clock, no stop or target) | non-cost | net 0.78 >= 0 (shortfall < 0): failed on t or n, not on cost |
| 5 | K2-aucpre-01 ZN | research | ZN | 15 | 1.933 | 0.55 | 1.168 = 0.168 + 1.000 | -0.765 | time-based (SELL unconditional at T_a-180 before a Treasury auction) | time-based (fixed clock, no stop or target) | non-cost | net 0.76 >= 0 (shortfall < 0): failed on t or n, not on cost |
| 6 | K2-cp1-01 TN | research | TN | 270 | 0.189 | 0.71 | 1.174 = 0.168 + 1.006 | 0.985 | breakout/momentum (side = sign of the Globex-open-to-07:49 move (continuation)) | time-based (fixed clock, no stop or target) | non-cost | gross t 0.71 < 1: gross not distinguished from zero; cost not the main failure |
| 7 | K2-cp1-01 ZB | research | ZB | 272 | 0.136 | 0.77 | 1.089 = 0.088 + 1.001 | 0.953 | breakout/momentum (side = sign of the Globex-open-to-07:49 move (continuation)) | time-based (fixed clock, no stop or target) | non-cost | gross t 0.77 < 1: gross not distinguished from zero; cost not the main failure |
| 8 | K2-cp1-01 ZF | research | ZF | 275 | 0.956 | 3.14 | 1.298 = 0.297 + 1.001 | 0.342 | breakout/momentum (side = sign of the Globex-open-to-07:49 move (continuation)) | time-based (fixed clock, no stop or target) | mainly cost | gross t 3.14 >= 1 and net -0.34 < 0: cost (shortfall 0.34 ticks) binds |
| 9 | K2-cp1-01 ZN | research | ZN | 276 | 0.656 | 3.26 | 1.168 = 0.168 + 1.000 | 0.512 | breakout/momentum (side = sign of the Globex-open-to-07:49 move (continuation)) | time-based (fixed clock, no stop or target) | mainly cost | gross t 3.26 >= 1 and net -0.51 < 0: cost (shortfall 0.51 ticks) binds |
| 10 | K2-cp1-01 ZT | research | ZT | 264 | 0.640 | 2.26 | 1.301 = 0.297 + 1.004 | 0.661 | breakout/momentum (side = sign of the Globex-open-to-07:49 move (continuation)) | time-based (fixed clock, no stop or target) | mainly cost | gross t 2.26 >= 1 and net -0.66 < 0: cost (shortfall 0.66 ticks) binds |
| 11 | K2-cp2-01 TN | research | TN | 286 | 0.343 | 0.53 | 1.174 = 0.168 + 1.006 | 0.832 | breakout/momentum (opening-range (07:20-07:35) breakout) | time-based (75 bars after the fill) | non-cost | gross t 0.53 < 1: gross not distinguished from zero; cost not the main failure |
| 12 | K2-cp2-01 UB | research | UB | 291 | 0.588 | 1.05 | 1.098 = 0.093 + 1.005 | 0.511 | breakout/momentum (opening-range (07:20-07:35) breakout) | time-based (75 bars after the fill) | mainly cost | gross t 1.05 >= 1 and net -0.51 < 0: cost (shortfall 0.51 ticks) binds |
| 13 | K2-cp2-01 ZB | research | ZB | 285 | 0.453 | 0.96 | 1.089 = 0.088 + 1.001 | 0.637 | breakout/momentum (opening-range (07:20-07:35) breakout) | time-based (75 bars after the fill) | non-cost | gross t 0.96 < 1: gross not distinguished from zero; cost not the main failure |
| 14 | K2-cp2-01 ZF | research | ZF | 283 | 1.074 | 1.64 | 1.298 = 0.297 + 1.001 | 0.224 | breakout/momentum (opening-range (07:20-07:35) breakout) | time-based (75 bars after the fill) | mainly cost | gross t 1.64 >= 1 and net -0.22 < 0: cost (shortfall 0.22 ticks) binds |
| 15 | K2-cp2-01 ZT | research | ZT | 265 | 0.498 | 0.84 | 1.301 = 0.297 + 1.004 | 0.803 | breakout/momentum (opening-range (07:20-07:35) breakout) | time-based (75 bars after the fill) | non-cost | gross t 0.84 < 1: gross not distinguished from zero; cost not the main failure |
| 16 | K2-cp3-01 ZT | research | ZT | 121 | 0.364 | 0.17 | 1.301 = 0.297 + 1.004 | 0.938 | breakout/momentum (prior-day close-location continuation (CLV top/bottom 20%)) | time-based (fixed clock, no stop or target) | non-cost | gross t 0.17 < 1: gross not distinguished from zero; cost not the main failure |
| 17 | K2-monthend-01 ZF | research | ZF | 18 | 0.778 | 0.18 | 1.298 = 0.297 + 1.001 | 0.520 | time-based (BUY unconditional on month-end N-1 and N) | time-based (fixed clock, no stop or target) | non-cost | gross t 0.18 < 1: gross not distinguished from zero; cost not the main failure |
| 18 | K2-monthend-01 ZT | research | ZT | 18 | 1.444 | 0.42 | 1.301 = 0.297 + 1.004 | -0.143 | time-based (BUY unconditional on month-end N-1 and N) | time-based (fixed clock, no stop or target) | non-cost | net 0.15 >= 0 (shortfall < 0): failed on t or n, not on cost |
| 19 | K2-predrift-01 ZN | research | ZN | 12 | 0.417 | 0.23 | 1.168 = 0.168 + 1.000 | 0.751 | breakout/momentum (sign of the 08:30-08:49 pre-ISM drift) | time-based (fixed clock, no stop or target) | non-cost | gross t 0.23 < 1: gross not distinguished from zero; cost not the main failure |
| 20 | K4-cp1-01 MCL | research | MCL | 258 | 4.016 | 1.66 | 3.167 = 1.720 + 1.447 | -0.849 | breakout/momentum (side = sign of the Globex-open-to-08:29 move) | time-based (fixed clock, no stop or target) | non-cost | net 0.84 >= 0 (shortfall < 0): failed on t or n, not on cost |
| 21 | K4-eiafade-01 MCL | research | MCL | 12 | 9.583 | 0.34 | 3.167 = 1.720 + 1.447 | -6.416 | fade/mean reversion (BUY if the 15-min post-WPSR move <= -0.5%, SELL if >= +0.5%) | time-based (fixed clock, no stop or target) | non-cost | net 6.08 >= 0 (shortfall < 0): failed on t or n, not on cost |
| 22 | K4-ngpre-01 NG | research | NG | 50 | 19.040 | 2.02 | 1.672 = 0.422 + 1.250 | -17.368 | time-based (SELL unconditional at T-90 before the NGS release) | time-based (fixed clock, no stop or target) | non-cost | net 17.37 >= 0 (shortfall < 0): failed on t or n, not on cost |
| 23 | K5-cp1-01 MGC | research | MGC | 284 | 3.493 | 0.73 | 4.086 = 1.920 + 2.166 | 0.593 | breakout/momentum (side = sign of the Globex-open-to-07:49 move) | time-based (fixed clock, no stop or target) | non-cost | gross t 0.73 < 1: gross not distinguished from zero; cost not the main failure |
| 24 | K5-cp2-01 MGC | research | MGC | 295 | 14.820 | 1.27 | 4.086 = 1.920 + 2.166 | -10.734 | breakout/momentum (opening-range breakout (4-tick buffer)) | time-based (75 bars after the fill) | non-cost | net 10.56 >= 0 (shortfall < 0): failed on t or n, not on cost |
| 25 | K5-cp3-01 MGC | research | MGC | 101 | 29.000 | 0.92 | 4.086 = 1.920 + 2.166 | -24.914 | breakout/momentum (prior-day close-location continuation) | time-based (fixed clock, no stop or target) | non-cost | net 24.81 >= 0 (shortfall < 0): failed on t or n, not on cost |
| 26 | K5-cp3-01 MHG | research | MHG | 126 | 11.437 | 1.04 | 3.701 = 1.536 + 2.165 | -7.736 | breakout/momentum (prior-day close-location continuation) | time-based (fixed clock, no stop or target) | non-cost | net 7.60 >= 0 (shortfall < 0): failed on t or n, not on cost |
| 27 | K5-fomc-01 MGC | research | MGC | 8 | 92.250 | 2.40 | 4.086 = 1.920 + 2.166 | -88.164 | breakout/momentum (sign of the 12:59-13:04 FOMC move) | time-based (fixed clock, no stop or target) | non-cost | net 86.65 >= 0 (shortfall < 0): failed on t or n, not on cost |
| 28 | K5-preauc-01 MGC | research | MGC | 280 | 5.496 | 1.43 | 4.086 = 1.920 + 2.166 | -1.410 | time-based (SELL unconditional 30 min before the London gold AM auction) | time-based (fixed clock, no stop or target) | non-cost | net 1.38 >= 0 (shortfall < 0): failed on t or n, not on cost |
| 29 | K3-cp1-01 6E | research | 6E | 284 | 2.292 | 2.13 | 1.935 = 0.675 + 1.259 | -0.358 | breakout/momentum (side = sign of the Globex-open-to-07:49 move) | time-based (fixed clock, no stop or target) | non-cost | net 0.35 >= 0 (shortfall < 0): failed on t or n, not on cost |
| 30 | K3-cp1-01 6J | research | 6J | 275 | 0.924 | 1.41 | 1.890 = 0.675 + 1.215 | 0.966 | breakout/momentum (side = sign of the Globex-open-to-07:49 move) | time-based (fixed clock, no stop or target) | mainly cost | gross t 1.41 >= 1 and net -0.95 < 0: cost (shortfall 0.97 ticks) binds |
| 31 | K3-ldnmom-01 6E | research | 6E | 254 | 1.055 | 0.97 | 1.935 = 0.675 + 1.259 | 0.879 | breakout/momentum (sign of the 3-bar trend into the London 16:00 fix) | time-based (fixed clock, no stop or target) | non-cost | gross t 0.97 < 1: gross not distinguished from zero; cost not the main failure |
| 32 | K3-ldnrev-01 6E | research | 6E | 12 | 9.000 | 1.89 | 1.935 = 0.675 + 1.259 | -7.065 | fade/mean reversion (BUY if the 10-min pre-fix move < 0, SELL if > 0 ('contrarian'), entry T_L+5) | time-based (fixed clock, no stop or target) | non-cost | net 7.08 >= 0 (shortfall < 0): failed on t or n, not on cost |
| 33 | K3-ldnrev-01 6J | research | 6J | 13 | 3.769 | 1.51 | 1.890 = 0.675 + 1.215 | -1.879 | fade/mean reversion (BUY if the 10-min pre-fix move < 0, SELL if > 0 ('contrarian'), entry T_L+5) | time-based (fixed clock, no stop or target) | non-cost | net 1.89 >= 0 (shortfall < 0): failed on t or n, not on cost |
| 34 | K3-ldnrev-01 6S | research | 6S | 13 | 3.846 | 0.56 | 2.650 = 0.675 + 1.975 | -1.196 | fade/mean reversion (BUY if the 10-min pre-fix move < 0, SELL if > 0 ('contrarian'), entry T_L+5) | time-based (fixed clock, no stop or target) | non-cost | net 1.24 >= 0 (shortfall < 0): failed on t or n, not on cost |
| 35 | K7-montrend-01 MBT | research | MBT | 466 | 6.534 | 1.09 | 8.846 = 5.640 + 3.206 | 2.312 | breakout/momentum (Monday trend rule on the weekend/Monday move) | time-based (fixed clock, no stop or target) | mainly cost | gross t 1.09 >= 1 and net -2.69 < 0: cost (shortfall 2.31 ticks) binds |
| 36 | K1-cp1-01 MNQ | research | MNQ | 284 | 8.789 | 0.62 | 4.119 = 2.440 + 1.679 | -4.670 | breakout/momentum (side = sign of the Globex-open-to-08:59 move) | time-based (fixed clock, no stop or target) | non-cost | net 4.71 >= 0 (shortfall < 0): failed on t or n, not on cost |
| 37 | K1-cp2-01 M2K | research | M2K | 297 | 6.902 | 0.88 | 3.954 = 2.440 + 1.514 | -2.948 | breakout/momentum (opening-range (08:30-08:45) breakout) | time-based (75 bars after the fill) | non-cost | net 2.87 >= 0 (shortfall < 0): failed on t or n, not on cost |
| 38 | K1-cp3-01 MNQ | research | MNQ | 118 | 30.373 | 0.33 | 4.119 = 2.440 + 1.679 | -26.254 | breakout/momentum (prior-day close-location continuation) | time-based (fixed clock, no stop or target) | non-cost | net 26.12 >= 0 (shortfall < 0): failed on t or n, not on cost |
| 39 | K6-cp1-01 ZL | research | ZL | 271 | 0.989 | 1.01 | 2.174 = 0.880 + 1.294 | 1.185 | breakout/momentum (cp1 template (sign of the open-to-O+29 move); entry text empty in NM1) | time-based (fixed clock, no stop or target) | mainly cost | gross t 1.01 >= 1 and net -1.20 < 0: cost (shortfall 1.18 ticks) binds |
| 40 | K6-cp2-01 ZL | research | ZL | 276 | 1.612 | 0.74 | 2.174 = 0.880 + 1.294 | 0.561 | breakout/momentum (cp2 template (opening-range breakout); entry text empty in NM1) | time-based (75 bars after the fill) | non-cost | gross t 0.74 < 1: gross not distinguished from zero; cost not the main failure |
| 41 | K6-cp3-01 LE | research | LE | 112 | 6.054 | 0.94 | 2.393 = 0.522 + 1.871 | -3.660 | breakout/momentum (cp3 template (prior-day CLV continuation); entry text empty in NM1) | time-based (fixed clock, no stop or target) | non-cost | net 3.64 >= 0 (shortfall < 0): failed on t or n, not on cost |
| 42 | K6-cp3-01 ZM | research | ZM | 119 | 2.731 | 1.22 | 1.608 = 0.528 + 1.080 | -1.123 | breakout/momentum (cp3 template (prior-day CLV continuation); entry text empty in NM1) | time-based (fixed clock, no stop or target) | non-cost | net 1.10 >= 0 (shortfall < 0): failed on t or n, not on cost |
| 43 | K6-cp3-01 ZW | research | ZW | 131 | 1.321 | 0.65 | 1.479 = 0.422 + 1.057 | 0.159 | breakout/momentum (cp3 template (prior-day CLV continuation); entry text empty in NM1) | time-based (fixed clock, no stop or target) | non-cost | gross t 0.65 < 1: gross not distinguished from zero; cost not the main failure |
| 44 | K6-limitcont-01 HE | research | HE | 1 | 53.000 | - | 1.860 = 0.522 + 1.338 | -51.140 | breakout/momentum (continuation after limit moves (settlement-proxy rule)) | time-based (fixed clock, no stop or target) | non-cost | net 51.03 >= 0 (shortfall < 0): failed on t or n, not on cost (n = 1) |
| 45 | K8-flight-01 H30 MGC | research | MGC | 55 | 25.818 | 1.16 | 4.086 = 1.920 + 2.166 | -21.732 | time-based (fixed side long MGC after a negative extreme MES move (cross-asset trigger, not a fade of MGC)) | time-based (fixed clock, no stop or target) | non-cost | net 21.74 >= 0 (shortfall < 0): failed on t or n, not on cost |
| 46 | K8-flight-01 HEOD MGC | research | MGC | 55 | 58.436 | 1.51 | 4.086 = 1.920 + 2.166 | -54.350 | time-based (fixed side long MGC after a negative extreme MES move (cross-asset trigger, not a fade of MGC)) | time-based (fixed clock, no stop or target) | non-cost | net 54.35 >= 0 (shortfall < 0): failed on t or n, not on cost |
| 47 | K8-wkndbtc-01 MNQ | research | MNQ | 39 | 190.154 | 1.10 | 4.119 = 2.440 + 1.679 | -186.035 | breakout/momentum (sign of the weekend MBT move, traded in MNQ) | time-based (fixed clock, no stop or target) | non-cost | net 185.74 >= 0 (shortfall < 0): failed on t or n, not on cost |
| 48 | K4-cp2-01 NG | confirmation | NG | 1061 | 3.226 | 1.40 | 1.672 = 0.422 + 1.250 | -1.554 | breakout/momentum (opening-range breakout) | time-based (75 bars after the fill) | non-cost | net 1.45 >= 0 (shortfall < 0): failed on t or n, not on cost |
| 49 | K4-eiamom-01 MCL | confirmation | MCL | 100 | 2.620 | 1.30 | 3.167 = 1.720 + 1.447 | 0.547 | breakout/momentum (sign of the 30-min post-WPSR move) | time-based (fixed clock, no stop or target) | mainly cost | gross t 1.30 >= 1 and net -0.52 < 0: cost (shortfall 0.55 ticks) binds |
| 50 | K4-ngpre-01 NG | confirmation | NG | 198 | 1.268 | 0.20 | 1.672 = 0.422 + 1.250 | 0.404 | time-based (SELL unconditional at T-90 before the NGS release) | time-based (fixed clock, no stop or target) | non-cost | gross t 0.20 < 1: gross not distinguished from zero; cost not the main failure |
| 51 | K4-ovr-01 NG | confirmation | NG | 1091 | 0.718 | 0.42 | 1.672 = 0.422 + 1.250 | 0.954 | fade/mean reversion (BUY if the 60-min return <= P10, SELL if >= P90 of 20-day reference) | time-based (fixed clock, no stop or target) | non-cost | gross t 0.42 < 1: gross not distinguished from zero; cost not the main failure |
| 52 | K3-cp1-01 6B | confirmation | 6B | 1107 | 1.431 | 4.14 | 1.916 = 0.675 + 1.241 | 0.485 | breakout/momentum (side = sign of the Globex-open-to-07:49 move) | time-based (fixed clock, no stop or target) | mainly cost | gross t 4.14 >= 1 and net -0.40 < 0: cost (shortfall 0.49 ticks) binds |
| 53 | K3-cp1-01 6E | confirmation | 6E | 1134 | 1.475 | 3.03 | 1.935 = 0.675 + 1.259 | 0.459 | breakout/momentum (side = sign of the Globex-open-to-07:49 move) | time-based (fixed clock, no stop or target) | mainly cost | gross t 3.03 >= 1 and net -0.47 < 0: cost (shortfall 0.46 ticks) binds |
| 54 | K3-cp3-01 6B | confirmation | 6B | 548 | 2.463 | 1.11 | 1.916 = 0.675 + 1.241 | -0.547 | breakout/momentum (prior-day close-location continuation) | time-based (fixed clock, no stop or target) | non-cost | net 0.57 >= 0 (shortfall < 0): failed on t or n, not on cost |
| 55 | K3-cp3-01 6E | confirmation | 6E | 513 | 2.466 | 0.81 | 1.935 = 0.675 + 1.259 | -0.531 | breakout/momentum (prior-day close-location continuation) | time-based (fixed clock, no stop or target) | non-cost | net 0.52 >= 0 (shortfall < 0): failed on t or n, not on cost |
| 56 | K3-cp3-01 6J | confirmation | 6J | 543 | 1.448 | 0.57 | 1.890 = 0.675 + 1.215 | 0.442 | breakout/momentum (prior-day close-location continuation) | time-based (fixed clock, no stop or target) | non-cost | gross t 0.57 < 1: gross not distinguished from zero; cost not the main failure |
| 57 | K3-cp3-01 6S | confirmation | 6S | 497 | 1.207 | 0.36 | 2.650 = 0.675 + 1.975 | 1.443 | breakout/momentum (prior-day close-location continuation) | time-based (fixed clock, no stop or target) | non-cost | gross t 0.36 < 1: gross not distinguished from zero; cost not the main failure |
| 58 | K3-ecbfix-01 6E | confirmation | 6E | 2301 | 1.348 | 0.94 | 1.935 = 0.675 + 1.259 | 0.587 | time-based (SELL 01:00 to the ECB fix, then leg 2 (fixed sides)) | time-based (fixed clock, no stop or target) | non-cost | gross t 0.94 < 1: gross not distinguished from zero; cost not the main failure |
| 59 | K3-ldnrev-01 6S | confirmation | 6S | 55 | 1.909 | 0.58 | 2.650 = 0.675 + 1.975 | 0.741 | fade/mean reversion (BUY if the 10-min pre-fix move < 0, SELL if > 0 ('contrarian'), entry T_L+5) | time-based (fixed clock, no stop or target) | non-cost | gross t 0.58 < 1: gross not distinguished from zero; cost not the main failure |
| 60 | K3-tkypost-01 6J | confirmation | 6J | 1091 | 0.777 | 0.68 | 1.890 = 0.675 + 1.215 | 1.113 | time-based (BUY 6J unconditional after the Tokyo fix) | time-based (fixed clock, no stop or target) | non-cost | gross t 0.68 < 1: gross not distinguished from zero; cost not the main failure |
| 61 | K3-tkypre-01 6J | confirmation | 6J | 224 | 5.745 | 2.85 | 1.890 = 0.675 + 1.215 | -3.856 | time-based (Gotobi/Tokyo month-end fixed side before the Tokyo fix) | time-based (fixed clock, no stop or target) | non-cost | net 3.87 >= 0 (shortfall < 0): failed on t or n, not on cost |
| 62 | K6-cp2-01 HE | confirmation | HE | 906 | 0.662 | 0.68 | 1.860 = 0.522 + 1.338 | 1.198 | breakout/momentum (cp2 template (opening-range breakout); entry text empty in NM1) | time-based (75 bars after the fill) | non-cost | gross t 0.68 < 1: gross not distinguished from zero; cost not the main failure |
| 63 | K6-cp2-01 ZW | confirmation | ZW | 1070 | 0.600 | 0.82 | 1.479 = 0.422 + 1.057 | 0.879 | breakout/momentum (cp2 template (opening-range breakout); entry text empty in NM1) | time-based (75 bars after the fill) | non-cost | gross t 0.82 < 1: gross not distinguished from zero; cost not the main failure |
| 64 | K6-limitcont-01 HE | confirmation | HE | 10 | 7.400 | 0.31 | 1.860 = 0.522 + 1.338 | -5.540 | breakout/momentum (continuation after limit moves (settlement-proxy rule)) | time-based (fixed clock, no stop or target) | non-cost | net 5.46 >= 0 (shortfall < 0): failed on t or n, not on cost |
| 65 | K8-flight-01 H30 MGC | confirmation | MGC | 231 | 3.160 | 0.94 | 4.086 = 1.920 + 2.166 | 0.926 | time-based (fixed side long MGC after a negative extreme MES move (cross-asset trigger, not a fade of MGC)) | time-based (fixed clock, no stop or target) | non-cost | gross t 0.94 < 1: gross not distinguished from zero; cost not the main failure |
| 66 | K8-flight-01 HEOD MGC | confirmation | MGC | 231 | 2.840 | 0.45 | 4.086 = 1.920 + 2.166 | 1.246 | time-based (fixed side long MGC after a negative extreme MES move (cross-asset trigger, not a fade of MGC)) | time-based (fixed clock, no stop or target) | non-cost | gross t 0.45 < 1: gross not distinguished from zero; cost not the main failure |
| 67 | A-H2 rth close window (sell) | confirmation(extension) | MES | 972 | 1.255 | 0.74 ~ | 2.034 = 0.976 + 1.058 | 0.779 | time-based (SELL unconditional 15:30-16:00 ET) | time-based (fixed clock, no stop or target) | non-cost | gross t 0.74 < 1: gross not distinguished from zero; cost not the main failure |
| 68 | A-H4 eth leg | confirmation(extension) | MES | 1007 | 3.236 | 0.96 ~ | 2.034 = 0.976 + 1.058 | -1.202 | time-based (BUY unconditional at the ETH open to 09:30 ET) | time-based (fixed clock, no stop or target) | non-cost | net 1.13 >= 0 (shortfall < 0): failed on t or n, not on cost |
| 69 | A-H4 rth leg | confirmation(extension) | MES | 1005 | 4.976 | 1.08 ~ | 2.034 = 0.976 + 1.058 | -2.942 | time-based (BUY unconditional 09:30-16:00 ET) | time-based (fixed clock, no stop or target) | non-cost | net 2.91 >= 0 (shortfall < 0): failed on t or n, not on cost |
| 70 | E-H1 scheduled macro drift | confirmation(extension) | MES | 112 | 13.009 | 1.35 ~ | 2.034 = 0.976 + 1.058 | -10.975 | time-based (BUY unconditional from the session start to the release) | time-based (fixed clock, no stop or target) | non-cost | net 10.85 >= 0 (shortfall < 0): failed on t or n, not on cost |
| 71 | H1 NR4 opening-range breakout | confirmation(extension) | MES | 266 | 5.098 | 0.65 ~ | 2.034 = 0.976 + 1.058 | -3.064 | breakout/momentum (NR4-day opening-range breakout) | time-based (fixed clock, no stop or target) | non-cost | net 0.48 >= 0 (shortfall < 0): failed on t or n, not on cost |
| 72 | H3 inside-day opening-range breakout | confirmation(extension) | MES | 80 | 14.600 | 0.93 ~ | 2.034 = 0.976 + 1.058 | -12.566 | breakout/momentum (inside-day opening-range breakout) | time-based (fixed clock, no stop or target) | non-cost | net 5.23 >= 0 (shortfall < 0): failed on t or n, not on cost |
| 73 | H4 bottom-tercile prior range, breakout | confirmation(extension) | MES | 336 | 10.679 | 1.74 ~ | 2.034 = 0.976 + 1.058 | -8.645 | breakout/momentum (low-range-day opening-range breakout) | time-based (fixed clock, no stop or target) | non-cost | net 3.27 >= 0 (shortfall < 0): failed on t or n, not on cost |
| 74 | F6_1_overnight_range_position | confirmation(extension) | MES | 992 | 2.308 | 1.08 ~ | 2.034 = 0.976 + 1.058 | -0.275 | breakout/momentum (BUY when the 08:30 open is in the upper half of the ETH range (continuation)) | time-based (09:30 CT (08:30-09:30 return)) | non-cost | net 0.20 >= 0 (shortfall < 0): failed on t or n, not on cost |
| 75 | F3_3_opening_30min_to_close_momentum | confirmation(extension) | MES | 960 | 1.204 | 0.75 ~ | 2.034 = 0.976 + 1.058 | 0.830 | fade/mean reversion (statistic, s = -1: 14:30-15:00 trade AGAINST the 08:30-09:00 move (side from the sign of the statistic)) | time-based (15:00 CT (end of the 14:30-15:00 window)) | non-cost | gross t 0.75 < 1: gross not distinguished from zero; cost not the main failure |
| 76 | F3_3_overnight_to_close_momentum | confirmation(extension) | MES | 963 | 3.157 | 1.91 ~ | 2.034 = 0.976 + 1.058 | -1.123 | fade/mean reversion (statistic, s = -1: 14:30-15:00 trade AGAINST the open-to-09:00 move) | time-based (15:00 CT) | non-cost | net 1.05 >= 0 (shortfall < 0): failed on t or n, not on cost |
| 77 | F3_2_bucket12_bucket13 | confirmation(extension) | MES | 963 | 1.468 | 0.89 ~ | 2.034 = 0.976 + 1.058 | 0.566 | breakout/momentum (statistic, s = +1: bucket 13 in the direction of bucket 12) | time-based (end of bucket 13) | non-cost | gross t 0.89 < 1: gross not distinguished from zero; cost not the main failure |
| 78 | gate0B_6A_hF | ML training window | 6A | 479 | 1.451 | -0.20 | 2.191 = 0.844 + 1.347 | 0.740 | other: ML model sign (none of the three) (ridge model sign, top 20% |z|) | time-based (horizon to the flatten time) | non-cost | gross t -0.20 < 1: gross not distinguished from zero; cost not the main failure; ML training-window (in-sample) row |
| 79 | gate0B_6C_h60 | ML training window | 6C | 532 | 1.165 | 0.56 | 2.026 = 0.844 + 1.182 | 0.861 | other: ML model sign (none of the three) (ridge model sign, top 20% |z|) | time-based (60-min horizon) | non-cost | gross t 0.56 < 1: gross not distinguished from zero; cost not the main failure; ML training-window (in-sample) row |
| 80 | gate0B_6J_hF | ML training window | 6J | 490 | 3.494 | 1.40 | 1.890 = 0.675 + 1.215 | -1.604 | other: ML model sign (none of the three) (ridge model sign, top 20% |z|) | time-based (horizon to the flatten time) | non-cost | net 1.60 >= 0 (shortfall < 0): failed on t or n, not on cost; ML training-window (in-sample) row |
| 81 | gate0B_6N_hF | ML training window | 6N | 170 | 2.465 | 0.07 | 2.252 = 0.844 + 1.408 | -0.213 | other: ML model sign (none of the three) (ridge model sign, top 20% |z|) | time-based (horizon to the flatten time) | non-cost | net 0.21 >= 0 (shortfall < 0): failed on t or n, not on cost; ML training-window (in-sample) row |
| 82 | gate0B_HE_h120 | ML training window | HE | 477 | 2.220 | 0.60 | 1.860 = 0.522 + 1.338 | -0.360 | other: ML model sign (none of the three) (ridge model sign, top 20% |z|) | time-based (120-min horizon) | non-cost | net 0.36 >= 0 (shortfall < 0): failed on t or n, not on cost; ML training-window (in-sample) row |
| 83 | gate0B_HE_hF | ML training window | HE | 478 | 2.793 | 0.49 | 1.860 = 0.522 + 1.338 | -0.933 | other: ML model sign (none of the three) (ridge model sign, top 20% |z|) | time-based (horizon to the flatten time) | non-cost | net 0.93 >= 0 (shortfall < 0): failed on t or n, not on cost; ML training-window (in-sample) row |
| 84 | gate0B_LE_h120 | ML training window | LE | 520 | 1.727 | 1.07 | 2.393 = 0.522 + 1.871 | 0.666 | other: ML model sign (none of the three) (ridge model sign, top 20% |z|) | time-based (120-min horizon) | mainly cost | gross t 1.07 >= 1 and net -0.67 < 0: cost (shortfall 0.67 ticks) binds; ML training-window (in-sample) row |
| 85 | gate0B_LE_hF | ML training window | LE | 522 | 1.079 | -0.11 | 2.393 = 0.522 + 1.871 | 1.315 | other: ML model sign (none of the three) (ridge model sign, top 20% |z|) | time-based (horizon to the flatten time) | non-cost | gross t -0.11 < 1: gross not distinguished from zero; cost not the main failure; ML training-window (in-sample) row |
| 86 | gate0B_MGC_h60 | ML training window | MGC | 581 | 2.014 | -0.41 | 4.086 = 1.920 + 2.166 | 2.072 | other: ML model sign (none of the three) (ridge model sign, top 20% |z|) | time-based (60-min horizon) | non-cost | gross t -0.41 < 1: gross not distinguished from zero; cost not the main failure; ML training-window (in-sample) row |
| 87 | gate0B_MYM_h60 | ML training window | MYM | 587 | 3.549 | -0.60 | 3.982 = 2.440 + 1.542 | 0.434 | other: ML model sign (none of the three) (ridge model sign, top 20% |z|) | time-based (60-min horizon) | non-cost | gross t -0.60 < 1: gross not distinguished from zero; cost not the main failure; ML training-window (in-sample) row |
| 88 | gate0B_NG_h120 | ML training window | NG | 518 | 2.925 | 0.69 | 1.672 = 0.422 + 1.250 | -1.253 | other: ML model sign (none of the three) (ridge model sign, top 20% |z|) | time-based (120-min horizon) | non-cost | net 1.25 >= 0 (shortfall < 0): failed on t or n, not on cost; ML training-window (in-sample) row |
| 89 | gate0B_NG_h60 | ML training window | NG | 518 | 5.569 | 2.51 | 1.672 = 0.422 + 1.250 | -3.897 | other: ML model sign (none of the three) (ridge model sign, top 20% |z|) | time-based (60-min horizon) | non-cost | net 3.90 >= 0 (shortfall < 0): failed on t or n, not on cost; ML training-window (in-sample) row |
| 90 | gate0B_NG_hF | ML training window | NG | 494 | 13.921 | 2.33 | 1.672 = 0.422 + 1.250 | -12.249 | other: ML model sign (none of the three) (ridge model sign, top 20% |z|) | time-based (horizon to the flatten time) | non-cost | net 12.25 >= 0 (shortfall < 0): failed on t or n, not on cost; ML training-window (in-sample) row |
| 91 | gate0B_TN_h60 | ML training window | TN | 464 | 1.108 | 0.94 | 1.174 = 0.168 + 1.006 | 0.066 | other: ML model sign (none of the three) (ridge model sign, top 20% |z|) | time-based (60-min horizon) | non-cost | gross t 0.94 < 1: gross not distinguished from zero; cost not the main failure; ML training-window (in-sample) row |
| 92 | gate0B_TN_hF | ML training window | TN | 442 | 1.507 | 0.72 | 1.174 = 0.168 + 1.006 | -0.333 | other: ML model sign (none of the three) (ridge model sign, top 20% |z|) | time-based (horizon to the flatten time) | non-cost | net 0.33 >= 0 (shortfall < 0): failed on t or n, not on cost; ML training-window (in-sample) row |
| 93 | gate0B_UB_h60 | ML training window | UB | 501 | 1.928 | 0.65 | 1.098 = 0.093 + 1.005 | -0.830 | other: ML model sign (none of the three) (ridge model sign, top 20% |z|) | time-based (60-min horizon) | non-cost | net 0.83 >= 0 (shortfall < 0): failed on t or n, not on cost; ML training-window (in-sample) row |
| 94 | gate0B_ZB_h60 | ML training window | ZB | 458 | 0.886 | 0.36 | 1.089 = 0.088 + 1.001 | 0.203 | other: ML model sign (none of the three) (ridge model sign, top 20% |z|) | time-based (60-min horizon) | non-cost | gross t 0.36 < 1: gross not distinguished from zero; cost not the main failure; ML training-window (in-sample) row |
| 95 | gate0B_ZB_hF | ML training window | ZB | 444 | 0.644 | 0.29 | 1.089 = 0.088 + 1.001 | 0.445 | other: ML model sign (none of the three) (ridge model sign, top 20% |z|) | time-based (horizon to the flatten time) | non-cost | gross t 0.29 < 1: gross not distinguished from zero; cost not the main failure; ML training-window (in-sample) row |
| 96 | gate0B_ZC_h120 | ML training window | ZC | 558 | 0.751 | 0.46 | 1.425 = 0.422 + 1.003 | 0.674 | other: ML model sign (none of the three) (ridge model sign, top 20% |z|) | time-based (120-min horizon) | non-cost | gross t 0.46 < 1: gross not distinguished from zero; cost not the main failure; ML training-window (in-sample) row |
| 97 | gate0B_ZC_h60 | ML training window | ZC | 558 | 1.138 | 1.39 | 1.425 = 0.422 + 1.003 | 0.287 | other: ML model sign (none of the three) (ridge model sign, top 20% |z|) | time-based (60-min horizon) | mainly cost | gross t 1.39 >= 1 and net -0.29 < 0: cost (shortfall 0.29 ticks) binds; ML training-window (in-sample) row |
| 98 | gate0B_ZC_hF | ML training window | ZC | 558 | 0.649 | 0.62 | 1.425 = 0.422 + 1.003 | 0.777 | other: ML model sign (none of the three) (ridge model sign, top 20% |z|) | time-based (horizon to the flatten time) | non-cost | gross t 0.62 < 1: gross not distinguished from zero; cost not the main failure; ML training-window (in-sample) row |
| 99 | gate0B_ZF_h120 | ML training window | ZF | 379 | 1.113 | 1.23 | 1.298 = 0.297 + 1.001 | 0.184 | other: ML model sign (none of the three) (ridge model sign, top 20% |z|) | time-based (120-min horizon) | mainly cost | gross t 1.23 >= 1 and net -0.18 < 0: cost (shortfall 0.18 ticks) binds; ML training-window (in-sample) row |
| 100 | gate0B_ZF_hF | ML training window | ZF | 374 | 0.963 | 1.18 | 1.298 = 0.297 + 1.001 | 0.335 | other: ML model sign (none of the three) (ridge model sign, top 20% |z|) | time-based (horizon to the flatten time) | mainly cost | gross t 1.18 >= 1 and net -0.34 < 0: cost (shortfall 0.34 ticks) binds; ML training-window (in-sample) row |
| 101 | gate0B_ZL_h120 | ML training window | ZL | 556 | 1.169 | -1.14 | 2.174 = 0.880 + 1.294 | 1.004 | other: ML model sign (none of the three) (ridge model sign, top 20% |z|) | time-based (120-min horizon) | non-cost | gross t -1.14 < 1: gross not distinguished from zero; cost not the main failure; ML training-window (in-sample) row |
| 102 | gate0B_ZM_h120 | ML training window | ZM | 545 | 0.897 | -0.16 | 1.608 = 0.528 + 1.080 | 0.711 | other: ML model sign (none of the three) (ridge model sign, top 20% |z|) | time-based (120-min horizon) | non-cost | gross t -0.16 < 1: gross not distinguished from zero; cost not the main failure; ML training-window (in-sample) row |
| 103 | gate0B_ZM_hF | ML training window | ZM | 546 | 0.844 | 0.21 | 1.608 = 0.528 + 1.080 | 0.764 | other: ML model sign (none of the three) (ridge model sign, top 20% |z|) | time-based (horizon to the flatten time) | non-cost | gross t 0.21 < 1: gross not distinguished from zero; cost not the main failure; ML training-window (in-sample) row |
| 104 | gate0B_ZN_h120 | ML training window | ZN | 577 | 0.260 | -0.21 | 1.168 = 0.168 + 1.000 | 0.908 | other: ML model sign (none of the three) (ridge model sign, top 20% |z|) | time-based (120-min horizon) | non-cost | gross t -0.21 < 1: gross not distinguished from zero; cost not the main failure; ML training-window (in-sample) row |
| 105 | gate0B_ZN_h60 | ML training window | ZN | 578 | 0.894 | 0.85 | 1.168 = 0.168 + 1.000 | 0.273 | other: ML model sign (none of the three) (ridge model sign, top 20% |z|) | time-based (60-min horizon) | non-cost | gross t 0.85 < 1: gross not distinguished from zero; cost not the main failure; ML training-window (in-sample) row |
| 106 | gate0B_ZN_hF | ML training window | ZN | 571 | 1.038 | 1.42 | 1.168 = 0.168 + 1.000 | 0.129 | other: ML model sign (none of the three) (ridge model sign, top 20% |z|) | time-based (horizon to the flatten time) | mainly cost | gross t 1.42 >= 1 and net -0.13 < 0: cost (shortfall 0.13 ticks) binds; ML training-window (in-sample) row |
| 107 | gate0B_ZS_h120 | ML training window | ZS | 570 | 0.560 | -0.72 | 1.469 = 0.422 + 1.046 | 0.909 | other: ML model sign (none of the three) (ridge model sign, top 20% |z|) | time-based (120-min horizon) | non-cost | gross t -0.72 < 1: gross not distinguished from zero; cost not the main failure; ML training-window (in-sample) row |
| 108 | gate0B_ZS_h60 | ML training window | ZS | 570 | 1.500 | 0.00 | 1.469 = 0.422 + 1.046 | -0.031 | other: ML model sign (none of the three) (ridge model sign, top 20% |z|) | time-based (60-min horizon) | non-cost | net 0.03 >= 0 (shortfall < 0): failed on t or n, not on cost; ML training-window (in-sample) row |
| 109 | gate0B_ZS_hF | ML training window | ZS | 569 | 2.668 | 0.61 | 1.469 = 0.422 + 1.046 | -1.199 | other: ML model sign (none of the three) (ridge model sign, top 20% |z|) | time-based (horizon to the flatten time) | non-cost | net 1.20 >= 0 (shortfall < 0): failed on t or n, not on cost; ML training-window (in-sample) row |
| 110 | gate0B_ZT_h120 | ML training window | ZT | 230 | 0.574 | 0.03 | 1.301 = 0.297 + 1.004 | 0.727 | other: ML model sign (none of the three) (ridge model sign, top 20% |z|) | time-based (120-min horizon) | non-cost | gross t 0.03 < 1: gross not distinguished from zero; cost not the main failure; ML training-window (in-sample) row |
| 111 | gate0B_ZT_h60 | ML training window | ZT | 230 | 1.126 | 1.00 | 1.301 = 0.297 + 1.004 | 0.175 | other: ML model sign (none of the three) (ridge model sign, top 20% |z|) | time-based (60-min horizon) | mainly cost | gross t 1.00 >= 1 and net -0.18 < 0: cost (shortfall 0.18 ticks) binds; ML training-window (in-sample) row |
| 112 | gate0B_ZT_hF | ML training window | ZT | 221 | 1.977 | 0.96 | 1.301 = 0.297 + 1.004 | -0.676 | other: ML model sign (none of the three) (ridge model sign, top 20% |z|) | time-based (horizon to the flatten time) | non-cost | net 0.68 >= 0 (shortfall < 0): failed on t or n, not on cost; ML training-window (in-sample) row |
| 113 | gate0B_ZW_h60 | ML training window | ZW | 543 | 0.459 | -0.58 | 1.479 = 0.422 + 1.057 | 1.021 | other: ML model sign (none of the three) (ridge model sign, top 20% |z|) | time-based (60-min horizon) | non-cost | gross t -0.58 < 1: gross not distinguished from zero; cost not the main failure; ML training-window (in-sample) row |
| 114 | gate0B_ZW_hF | ML training window | ZW | 543 | 0.807 | -0.71 | 1.479 = 0.422 + 1.057 | 0.673 | other: ML model sign (none of the three) (ridge model sign, top 20% |z|) | time-based (horizon to the flatten time) | non-cost | gross t -0.71 < 1: gross not distinguished from zero; cost not the main failure; ML training-window (in-sample) row |
| 115 | E20H6-T1 overlap | overlap | MNQ (NQ price path at MNQ co | 254 | 17.472 | 1.52 | 4.119 = 2.440 + 1.679 | -13.354 | breakout/momentum (rest-of-day return sign into the last 30 min (Baltussen form)) | time-based (fixed clock, no stop or target) | non-cost | net 13.39 >= 0 (shortfall < 0): failed on t or n, not on cost |
| 116 | E20H6-T2 overlap | overlap | MNQ (NQ price path at MNQ co | 104 | 21.885 | 0.83 | 4.119 = 2.440 + 1.679 | -17.766 | breakout/momentum (same, |r_ROD| above the 60-day median) | time-based (fixed clock, no stop or target) | non-cost | net 17.80 >= 0 (shortfall < 0): failed on t or n, not on cost |
| 117 | E20H6-T3 overlap | overlap | MNQ (NQ price path at MNQ co | 39 | 75.974 | 1.26 | 4.119 = 2.440 + 1.679 | -71.856 | breakout/momentum (same, previous-day GEX negative) | time-based (fixed clock, no stop or target) | non-cost | net 71.89 >= 0 (shortfall < 0): failed on t or n, not on cost |
| 118 | C1b-T1 (NG h60) | W_ext (2010-07..2019-04  | NG | 814 | 0.585 | -0.83 | 1.672 = 0.422 + 1.250 | 1.087 | other: ML model sign (none of the three) (ridge model sign (NG h60)) | time-based (60-min horizon) | non-cost | gross t -0.83 < 1: gross not distinguished from zero; cost not the main failure; ML training-window (in-sample) row |
| 119 | E16-H1 | W_ext | 27 full-size roots pooled (p | 55070 | 5.731 | - | - | - | breakout/momentum (sign of the move into S_p-30 (settlement-window momentum)) | time-based (fixed clock, no stop or target) | undetermined | no D8 cost basis or gross t in NM1 (pooled full-size price paths) |

## 2. Realistic passive saving per vehicle class (touch fills vs TopstepX trade-through fills)

Definition. Passive saving = the cut in RT cost against D8's market-order cost when a leg is entered or
exited with a resting limit at the own-side touch instead of a market order, after adverse selection,
before missed-fill cost. Per side, a market order costs s against the decision-time mid (D8).

Arithmetic (NM2's, not a published number; inputs sourced):
- Touch fill, no adverse selection (the naive backtest): the limit fills at mid - s, so it saves 2s a
  side. This is an upper bound no source supports.
- Touch or queue fill with adverse selection: Lalor and Swishchuk (arXiv:2409.12721v3, Table 2, via
  R18) count the share p of passive 1-lot fills followed by an adverse next price change on CME, in the
  TT simulator (queue position plus traded-through volume, one day each, 2024-04-23..25):
  "ES Jun24 941 767" (p = 0.815), "NQ Jun24 1929 1269" (0.658), "CL Jun24 625 518" (0.829),
  "ZN Jun24 224 199" (0.888). If the next change is one tick either way, the expected markout after a
  fill is (2p - 1) ticks: ES 0.63, NQ 0.32, CL 0.66, ZN 0.78. Saving a side = 2s - (2p - 1).
- TopstepX trade-through fill (DECISIONS C6: "the market has to trade through your price - not just
  touch it"): a buy at L fills only after a print at L - 1 tick, so at the fill the mid is about
  L - 1 + s. The fill is then about 1 - s ticks under water against the mid. Saving a side at most
  2s - 1 (no selection beyond the trade-through tick). Adding the same (2p - 1) next-change markout
  gives 2s - 1 - (2p - 1). R18 section 5 reaches the same sign for a one-tick MES/MNQ book ("at or
  below zero per side").
- Missed fills are not costed. A resting limit that never trades through is either skipped (the
  skipped trades are the ones where price left at once, which for a positive-gross rule are the better
  trades) or chased with a market order (pays s, and the move). Either way every figure below is an
  upper bound on the realistic saving.
- RT: a rule whose exit is a fixed clock can rest only its entry, unless it rests the exit some
  minutes early with a market fallback. Entry-only RT saving = 1 x the per-side figure; both legs =
  2 x the per-side figure.

Cross-check on ES from a second source (R17, Baron-Brogaard-Kirilenko 2014, CFTC audit trail, Table 7
Panel B): non-HFT market makers (aggressiveness < 20%, flat end of day: the retail-maker profile)
"Non-HFT MM ... -$0.97" per contract at one-minute marks, i.e. -0.08 ES ticks ($12.50). With the
half-spread already inside that figure, a slow maker's passive fill is worth about -0.08 tick against
mid, against -0.5 for a market order. That is about +0.42 tick a side under real exchange (queue)
fills, matching the MES touch-with-selection figure of 0.43 below (NM2's arithmetic; it assumes a
zero one-minute markout for an uninformed market order).

Per side, ticks of the vehicle (s from D8, the NM1 d8 fields; per-class L-S p where published):

| class (vehicle) | D8 s a side | L-S p used | touch, no selection (2s) | touch with L-S selection | TopstepX trade-through, upper (2s - 1) | TopstepX with L-S selection | realistic range a side, TopstepX | realistic range a side, touch |
|---|---|---|---|---|---|---|---|---|
| MNQ | 0.839 (08:30 bucket 0.969) | NQ 0.658 | 1.68 | 1.36 | 0.68 | 0.36 | 0.36 to 0.68 | 1.36 to 1.68 |
| MES | 0.529 (08:30 bucket 0.547) | ES 0.815 | 1.06 | 0.43 (BBK check 0.42) | 0.06 | -0.57 | -0.57 to 0.06 | 0.43 to 1.06 |
| MGC | 1.083 | none for gold: 0.658-0.888 | 2.17 | 1.39 to 1.85 | 1.17 | 0.39 to 0.85 | 0.39 to 1.17 | 1.39 to 2.17 |
| MCL | 0.724 | CL 0.829 | 1.45 | 0.79 | 0.45 | -0.21 | -0.21 to 0.45 | 0.79 to 1.45 |
| 6E-class FX: 6E | 0.630 | none for FX: 0.658-0.888 | 1.26 | 0.48 to 0.94 | 0.26 | -0.52 to -0.06 | -0.52 to 0.26 | 0.48 to 1.26 |
| 6S / 6J / 6B | 0.988 / 0.607 / 0.620 | same | 1.98 / 1.21 / 1.24 | 1.20-1.66 / 0.44-0.90 / 0.47-0.93 | 0.98 / 0.21 / 0.24 | 0.20-0.66 / -0.56 to -0.10 / -0.54 to -0.08 | as left | as left |
| ZN-class rates (ZN; ZT, ZF, TN, ZB, UB within 0.003) | 0.500 | ZN 0.888 | 1.00 | 0.22 | 0.00 | -0.78 | -0.78 to 0.00 | 0.22 to 1.00 |
| NG (for K4-ovr-01) | 0.625 | none: 0.658-0.888 | 1.25 | 0.47 to 0.93 | 0.25 | -0.53 to -0.07 | -0.53 to 0.25 | 0.47 to 1.25 |

Reading the table:
- Touch fills are not available on TopstepX (C6), and an edge from SIM queue position is prohibited
  (C6 reason 2). Use the TopstepX columns for anything the program would trade.
- One-tick books (MES, ZN-class rates, and 6E for most of the day) save nothing under trade-through,
  and lose once the next-change selection is counted. This is R18's conclusion, and it is consistent
  with D.1f's C-H4 (MES resting-limit reversal, trade-through): UCB95 -177.18 net ticks per micro per
  day over 90,418 round trips (DECISIONS C6).
- Wide-book micros (MNQ, MGC, 6S) show a positive TopstepX upper bound only because D8's mean s is
  above half a tick: the book is often more than one tick wide. This rests on a mean, and for MGC, 6S
  and NG on no CME adverse-selection number at all. It is a hypothesis for the calibration slice
  (section 5), not a usable figure.
- Sources' limits: L-S is one day per contract, simulator queue fills (more generous than
  trade-through) and author-chosen quote spacing, with no tick markout published (R18 section 10).
  BBK is ES, August 2010, pre-micro. Nothing found measures MGC, MCL, FX or NG passive fills.

## 3. Group A: the lead's "empty" is CONFIRMED

No row of the 378 meets all four clauses. Only eight of the 119 fee-covering rows have a fade entry
(A1). Five of those have net >= 0, so cost is not their failure (A4 fails). The other three fail A4
(gross t < 1), and two of them fail A3 as well. A fade row with gross t >= 1 and net < 0 exists only
below the fee line (A2 fails); passive execution cannot recover commission.

Nearest rows, arithmetic (per-side savings from section 2; "both legs" = 2 x per side):

| row (window, n) | A1 entry | A2 gross > fee | shortfall RT - gross | TopstepX saving available: entry only / both legs | A3 | gross t | net | A4 | verdict |
|---|---|---|---|---|---|---|---|---|---|
| K3-ldnrev-01 6S (confirmation 2019-05..2024-02, n 55) | fade: "BUY if M < 0, SELL if M > 0 (contrarian ...)", M = 10-min pre-London-fix move, entry T_L+5, exit T_L+20 | yes: 1.909 > 0.675 | 2.650 - 1.909 = 0.741 | 0.20..0.98 / 0.40..1.95 | open: passes only toward the no-selection bound (0.98 entry only); fails entry-only with L-S selection (max 0.66) | 0.584 | -0.693 | no (t < 1) | not Group A: the gross itself is not distinct from zero |
| K4-ovr-01 NG (confirmation, n 1,091) | fade: "r(t) <= P10 buys, r(t) >= P90 sells" (60-min return vs a 20-day reference) | yes: 0.718 > 0.422 | 1.672 - 0.718 = 0.954 | -0.53..0.25 / -1.05..0.50 | no: 0.954 > 0.50 even at the upper bound; passes only with touch fills (2.50 both legs) | 0.417 | -0.993 | no | not Group A: fails A3 and A4 |
| F3_3_opening_30min (confirmation-extension 2020-02..2024-02, MES, n 960; a statistic, not a trial) | fade: s = -1, so the 14:30-15:00 trade goes against the 08:30-09:00 move; the side comes from the sign of the statistic (F / C3, -6.3358, -1) | yes: 1.204 > 0.976 | 2.034 - 1.204 = 0.830 | -0.57..0.06 / -1.14..0.12 | no under TopstepX; under touch fills both legs 0.86..2.12 would pass | about 0.75 (approx., net t -0.565 x 1.204 / -0.906) | -0.906 | no | not Group A. The lead's "side unclear" resolves: the side is a fade of the opening half-hour, chosen by the statistic's sign |
| K3-ldnrev-01 6E / 6J / 6S (research, n 12 / 13 / 13) | fade (same rule) | yes | -7.07 / -1.88 / -1.20 (net > 0) | n/a | n/a | 1.89 / 1.51 / 0.56 | +7.08 / +1.89 / +1.24 | no (net > 0) | not cost-limited; the confirmation-window gross is -0.40 (6E) and -1.08 (6J), so the sign does not carry |
| K4-eiafade-01 MCL (research, n 12) | fade (BUY if the 15-min post-WPSR move <= -0.5%, SELL if >= +0.5%) | yes: 9.58 > 1.72 | -6.42 | n/a | n/a | 0.342 | +6.08 | no (net > 0) | not cost-limited; confirmation gross -25.51 (n 55, t -1.96) |
| F3_3_overnight_to_close (confirmation-extension, MES, n 963; statistic) | fade (s = -1 against the open-to-09:00 move) | yes: 3.157 > 0.976 | -1.123 | n/a | n/a | about 1.91 (approx.) | +1.047 | no (net > 0) | not cost-limited (net t 0.634) |

Fade rows that pass A4 but fail A2 (below the fee line, all MES, D.1f confirmation-extension; gross t
approximated as above):

| row | n | gross | fee | gross t (approx.) | net |
|---|---|---|---|---|---|
| C-H1 magnitude-conditioned reversal | 149,035 | 0.125 | 0.976 | about 3.69 | -1.954 |
| C-H3 close-location-value reversal | 47,582 | 0.104 | 0.976 | about 1.97 | -1.980 |
| G2.ETH.5 (fade, s = -1) | 9,584 | 0.253 | 0.976 | about 2.15 | -1.857 |
| G2.ETH.30 (fade, s = -1) | 4,412 | 0.606 | 0.976 | about 1.83 | -1.504 |
| B-H3 fade leg | 991 | 0.571 | 0.976 | about 0.42 (fails A4 too) | -1.499 |

These carry a real but tiny reversal (0.1-0.6 MES ticks a trade), below commission alone. C-H4
(the passive-fill version of the same family) is the program's record of what resting limits do to
it: gross -1.092, net -2.178 a trade (NM1 row C-H4, n 90,418).

Rows that pass A2-A4 but fail A1 (momentum or ML entries whose failure is mainly cost). This is shown
for the lead only, because the rule excludes these rows: a momentum entry rested at the touch fills on
pullbacks, that is when the move is failing, so its selection is expected to be worse than a fade's.
That expectation is unmeasured.

| row (window) | entry | shortfall | TopstepX both legs: upper / with L-S | touch both legs with L-S |
|---|---|---|---|---|
| K2-cp1-01 ZF / ZN / ZT (research) | momentum | 0.342 / 0.512 / 0.661 | 0.00 / -1.55 | 0.45 |
| K2-cp2-01 UB / ZF (research) | ORB | 0.511 / 0.224 | 0.01 / -1.54 | 0.45 |
| K3-cp1-01 6J (research) | momentum | 0.966 | 0.43 / -1.12..-0.20 | 0.88..1.80 |
| K3-cp1-01 6B (confirmation) | momentum | 0.485 | 0.48 / -1.07..-0.15 | 0.93..1.85 |
| K3-cp1-01 6E (confirmation) | momentum | 0.459 | 0.52 / -1.03..-0.11 | 0.97..1.89 |
| K4-eiamom-01 MCL (confirmation) | momentum | 0.547 | 0.89 / -0.42 | 1.58 |
| K6-cp1-01 ZL (research) | momentum | 1.185 | 0.59 / -0.96..-0.04 | 1.04..1.96 |
| K7-montrend-01 MBT (research) | momentum | 2.312 | 4.41 / 2.86..3.78 | 4.86..5.78 |
| gate0B_LE_h120 (ML training window) | ML sign | 0.666 | 1.74 / 0.19..1.11 | 2.19..3.11 |
| gate0B_ZC_h60, ZF_h120, ZF_hF, ZN_hF, ZT_h60 (ML training window) | ML sign | 0.29 / 0.18 / 0.34 / 0.13 / 0.18 | about 0.00 / about -1.55 | about 0.45 |

Two rows have a shortfall below even the selection-adjusted TopstepX figure: K7-montrend-01 MBT
(wide MBT book, s = 1.60 a side; no CME adverse-selection number for crypto futures) and, in part,
gate0B_LE_h120 (an in-sample ML row). Both fail A1. NM2 proposes neither: selection is the lead's
call.

## 4. Group B: maker-native candidates with a published mechanism

### B1: the reversal leg of the 3rd-Friday spike, entered with a resting sell limit at the 08:30 CT open (R17-C1 = the lead's C2 mechanism)

- Mechanism (Baltussen, Terstegge and Whelan 2024, via RD4/R17; R17 did not refetch it): on monthly
  a.m.-settlement Fridays the active ES contract rises "+14.30 bp" into the SOQ open and reverses
  "-12.89 bp" by noon ET (t -2.40, sd 80.45, 2003-2021). R17 converts this at ES 6,000 to 7.73 ES points,
  or 30.9 MES ticks, marked close to noon, not at a limit fill. The MNQ size is not published: the same
  bp on NQ at 21,000 would be about 108 MNQ ticks, but that is NM2's assumption, not a published figure.
- Price saving at stake: MNQ 08:30 bucket s = 0.969 a side (D8 bucket table), so the TopstepX range is
  0.62 to 0.94 ticks for the entry. MES 08:30 bucket s = 0.547 gives -0.54 to 0.09. Either is under
  1% of the published move (MNQ about 0.9%, MES about 0.3%). The execution cannot be why B1 beats or loses to the
  market-order C2. Its effect works through which days fill.
- How trade-through fills hurt: the sell limit fills only if price prints at least one tick above it
  after 08:30. That selects the days the spike continues, an adverse selection inside the event (R17:
  "selects the days the spike continues"). It skips the days the price turns straight from the
  opening print, which are the days that carry the published reversal. The fill rate is below 1, so B1
  has fewer events than C2's 9-13 on the research window. C2's power is already 0.12-0.13 at 5% and
  0.04 at Holm-4 (s2_power.out via synthesis.md), so B1's power is lower still.
- How trade-through fills could help: only if the spike peaks after the 08:30 print, that is, if the
  path routinely overshoots by a tick or more before reverting. A limit above the open then sells
  nearer the top on most event days, and the trade-through requirement costs little. This is a claim
  about the intra-event path that no source in R17/RD4 publishes (their marks are the open and noon). It
  is an empirical question for the registered test, not something the calibration slice may answer
  (section 5).
- Execution variants (each its own registered trial if the lead keeps it): B1a, skip the day if
  unfilled by a fixed time. B1b, market-order fallback at a fixed time; this mixes C2 and B1 and
  inherits C2's cost on unfilled days. A single resting sell for 2 lots that closes C3's long and opens
  C2's short has opposite selection on its two legs. For the C3 exit leg, a fill needs further
  strength, which is favourable. An unfilled day leaves the long open into the reversal, so it needs
  a market fallback.

### R17-C2: expiry-day pinning in ES serial-option months (Golez and Jackwerth 2012, JFE)

- Mechanism (peer-reviewed; R17 quotes): futures "pulled toward the at the money strike price on days
  when serial options on the S&P 500 futures expire (pinning) ... driven by the interplay of market
  makers' rebalancing of delta hedges"; "a shift of at least 11.00 bps from Thursday PM to expiration
  Friday PM ... $59 million shifts solely within the last 30 min".
- Execution: resting limits that fade moves away from the nearest 5-point strike, 14:30-15:05 CT.
  Under trade-through, a fade limit placed away from the strike fills only when price pushes one more
  tick away from the strike, which selects the moments the pin is failing (hurts). It helps only if the
  pull is strong enough that a one-tick overshoot is routine noise. No per-trade gross is published, and
  11 bp is an aggregate shift in the distribution, not a trade P&L. The sample (1992-2009) predates
  weekly and 0DTE options. Open interest by strike is not owned. There are about 8 events a year.
  Weak: at most a low-priority candidate, and the lead decides whether to keep it.

### Considered and excluded (no maker-native candidate survives)

- R17-C3, providing liquidity to the commodity-ETF/GSCI roll (Bessembinder et al. 2016): multi-day
  holds, which are prop-incompatible on Topstep (flat by 15:10 CT). The intraday imbalance "is almost
  entirely reversed within one minute", which is HFT scale. Liquidity providers increased on roll days
  and spreads narrowed (t -4.11), so the rent was competed away.
- R18: zero candidates. It supports C6: "The naive strategy ... is in fact highly unprofitable"
  (Albers et al. 2025, Binance, not CME), and back-of-queue fills mark out at -0.775 bp after one
  second.
- R3: no maker-native candidate. Queue imbalance (Gould and Bonart 2016) predicts the next mid move,
  but using it to place and cancel limits needs sub-second reaction: "the added value of exploiting
  liquidity imbalance is eroded by latency" (Lehalle and Mounjid 2017). CME latency in Dixon 2018 is
  100 us to 1 ms. That is HFT scale, banned by the prop HFT clauses (R9/R18 quotes), and it would
  monetise SIM queue position, which C6 prohibits. R3-C1 and R3-C2 are taker signals.
- R4: no maker-native candidate. Aggressor-side and volume features (R4-C1..C4) are taker signals,
  and the volume-conditioned momentum (Gao et al.) enters at 14:30 by market order.
- General negative (R17, BBK): "the average Aggressive HFT firm earns a daily profit of $74,000 ...
  Passive firms earn ... $12,600", which is "a stronger profit motive for liquidity taking than
  liquidity providing"; small traders lose $3.67 a contract (-0.29 ES ticks).

## 5. Shared calibration slice and test data spec (Databento GLBX.MDP3; nothing requested or bought)

Principle (brief): a small calibration slice used for fill and adverse-selection modelling only, with no
rule tested on it. The test runs on the research window 2025-04-01..2026-06-19. Each rule-execution
pair is a new registered trial, and N carries forward.

### 5a. Calibration slice (fill model only)

- Window constraint: NM2 narrows the brief's "2019-2024" to 2019-05-01..2024-02-29. March 2024 is the
  embargo and holdout-2 is 2024-04-01..2025-03-31 (docs/STAGE_E_DESIGN.md line 254;
  docs/STAGE_E_ML_DESIGN.md line 51: "Never used by the route: March 2024 (embargo) and holdout-2").
  This applies an invariant. It is not a design choice.
- Dates (a fixed rule, so nothing is selected by outcome): the 2nd Friday of every third month,
  2019-05-10, 2019-08-09, 2019-11-08, then February, May, August and November of 2020-2023, then
  2024-02-09. That is 20 dates. A date that is an exchange holiday, an early halt or a roll-blackout
  date is dropped, not replaced. These months avoid the quarterly roll weeks. The 3rd Fridays, the
  event days of B1/C2/C3, are kept out of the slice. B1's fill rate on event days would preview the
  rule's outcome, because a fill happens if and only if price rose at least a tick above the limit.
  The lead may decide otherwise.
- Contracts: the front (most-active) outright of MNQ and MES. These cover B1, the C1 reference
  execution and the MES row of section 2. Group A is empty, so no other root is needed. Optional, only
  if the lead keeps a non-equity execution pair: MGC (07:20-12:30), MCL and NG (08:00-13:30), 6E and 6S
  (07:20-14:00, which includes the London fix at 10:00/11:00 CT), ZN (07:20-14:00).
- Schemas: `trades` (each print with its aggressor side; R4 quotes the DBN field: "the side that
  initiates the trade. Can be Ask for a sell aggressor ..., Bid for a buy aggressor ..., or None") to
  detect trade-through and touch prints, and `mbp-1` (the BBO and its sizes at every top-of-book
  change) for the limit price, the spread, top size and mid markouts. `mbo`: not needed. A TopstepX
  trade-through fill depends only on the print sequence beyond the limit, not on queue position. A
  queue-position (exchange-real) counterfactual would need `mbo`, but C6 bars monetising it on
  TopstepX. If the lead wants it for another venue, the program's D.1e quote is MES mbo RTH $0.7836 a
  day (R3/R18; a quote, not a price list).
- Clock: MNQ/MES 07:30-15:10 CT (the 08:30 open, C1's :00/:30 checks from 09:00, the 14:30-15:00
  window, flat by 15:00).
- What is measured (no signal is computed): at each fixed clock (08:30:00, and every :00 and :30 from
  09:00 to 14:30), a virtual 1-lot buy and a virtual 1-lot sell at the own-side touch from mbp-1. For
  each: (i) the trade-through fill time (first print strictly beyond the limit), within 1, 5, 15, 30
  and 60 min; (ii) the touch fill time (first print at the limit), for comparison; (iii) the markout
  against the fill price at +1 s, +1 min, +5 min and +30 min (mbp-1 mid); (iv) for unfilled orders, the
  mid move over the same horizons, which is the missed-fill cost; (v) the spread and top size at
  placement. Output per vehicle: fill probability and conditional markout under both fill models, i.e.
  section 2's saving with confidence intervals, replacing the L-S and BBK proxies.
- Cost, from figures already in the reader files (E.0 log: 5 sample days in each product's session
  window, quotes from the free metadata endpoint, cited by R4 for ES/NQ/MNQ): mbp-1 MNQ $13.46,
  NQ $5.92, ES $5.44; tbbo MNQ $8.62, NQ $3.58, ES $4.41 (R4: "`trades` is smaller than `tbbo`"). Linear
  scaling, which is not a quote: MNQ about $2.69 a day for mbp-1 and at most about $1.72 a day for
  trades, so 20 dates come to about $54 + at most $34. MES has no row in the E.0 table, and no reader
  file gives an MES mbp-1 price. ES is not a valid proxy (MNQ costs 2.3 times NQ). Same E.0 table, for
  the optional roots (5 days, mbp-1 / tbbo): ZN $1.31 / $0.87, 6E $0.86 / $0.42, 6S $0.20 / $0.12,
  MCL $0.64 / $0.49, NG $0.25 / $0.42, MGC $2.29 / $2.25.
- Published Databento prices (R3's excerpt of databento.com/pricing, fetched 2026-10-18; R16 the
  same): Standard "$199 per month" with "1 year of L1 history" and "1 month of L2 and L3 history",
  "Pay as you go for more history"; Plus "$1,750 license fees per month"; Unlimited "$4,500 license
  fees per month"; "$125 in free credits", example "CME Globex MDP 3.0 / 1 product(ES) / MBO 14
  months / MBP-1 12 months / TBBO 15 months / Trades 16 months"; usage-based "$/GB by the data's
  uncompressed size", with no CME $/GB printed. R4 reads L1 as MBP-1, TBBO and Trades. Standard's
  "1 year of L1 history" reaches back only about 12 months from the purchase date, so the 2019-2024
  slice and the 2025-04..2025-10 part of the research window would be pay-as-you-go or credit.
- Spend gate (CLAUDE.md): a logged quote first, and explicit approval in a stage prompt. None in E.25.

### 5b. Test data on the research window (2025-04-01..2026-06-19)

| trial (rule x execution) | status | contracts | dates | schemas | clock CT | scaled cost (not a quote) |
|---|---|---|---|---|---|---|
| C2, 3rd-Friday reversal, market orders | lead's shortlist (S2) | MNQ (MES reference) | monthly a.m.-settlement 3rd Fridays: 15 in the window (2025-04-18 .. 2026-06-19); the lead's list after the roll-blackout and holiday exclusions governs (9-13 per synthesis) | none beyond owned 1-min bars and D8 | 08:30-15:00 | $0 |
| B1a, same rule, resting sell limit at the 08:30 open, trade-through fills, skip if unfilled by a fixed time | new trial if kept (+1 to N) | MNQ, MES | the same dates | trades + mbp-1 | 07:30-15:10 | MNQ about 15 x ($2.69 + $1.72) = about $66 at most; MES not priced |
| B1b, as B1a with a market fallback at a fixed time | new trial if kept (+1 to N) | same | same | same | same | included above |
| R17-C2, pinning fade with resting limits | only if the lead registers it (+1 to N); weak (section 4) | MES (ES 5-pt strike grid, computable) | serial (non-quarterly) ES-option expiry Fridays in the window, about 10 | trades + mbp-1 | 14:00-15:10 | MES not priced |

- Fills in every test use the TopstepX trade-through rule (C6). Touch fills are reported beside them,
  never in the verdict.
- No rule is fitted on 5a. 5a supplies only the fill-probability and markout model, which is frozen
  before the test.

## 6. Unfinished or unverified

- The saving arithmetic in section 2 is NM2's, not published. It assumes a one-tick next price change
  and uses D8's mean s for books that are often wider than one tick. L-S covers ES/NQ/CL/ZN on one day
  each, with simulator queue fills. MGC, FX and NG have no CME adverse-selection number. Missed-fill
  cost is not quantified anywhere, so every saving is an upper bound.
- The BBK cross-check assumes a zero one-minute markout for an uninformed market order. The BBK
  non-HFT MM class includes up to 20% aggressive trades.
- Gross t for the D.1/D.1f-era rows is approximated (net t x gross / net on a daily-series t). It is
  not recorded. The signs of the gate0B gross t values are as NM1 recorded them and are not reconciled.
- K6 entry texts are empty in NM1, so their classes come from the family template.
- The MNQ size of the 3rd-Friday reversal is NM2's same-bp assumption. Only ES bp are published (via
  RD4; R17 did not refetch).
- No MES mbp-1 or trades price was found in R3/R4/R16/R18 or in the E.0 table. No CME $/GB rate is
  published.
- No web fetch was made (none was needed). No market data or purchase. REGISTRATION.md, live/ and
  ops/ were untouched, and nothing was committed.
