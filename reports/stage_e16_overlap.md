# Stage E.16 Task 2: overlap audit of H1 to H5 against the program's tested members

Worker: OverlapAudit-OpusHigh (worker-high, opus). Written 2026-10-09 from 00:24 PDT (`date`).
Read-only on the repo; no market-data byte read (only file names, manifests, member docstrings,
catalogs, result JSON summaries and reports); no web; no other file written.
This file recommends. The lead rules (drop identical, keep related with the relation in the freeze).

Definitions audited against: docs/prompts/STAGE_E.16.md "THE FIVE HYPOTHESES" and
reports/stage_e16_briefs/lead_spec.md section 4.

## 0. Choices made where the brief left room (for the lead's Open choices)

- O-1 "Identical" means: same signal (same price inputs, same reference points, same sign rule), same
  clock window (decision, entry and exit minutes, or for a multi-day rule the same day set and hold),
  and same products. The data window is reported in every row but is NOT a condition of identity: a
  member that matched on signal, clock window and products would be called identical even if it ran on
  another data window (the conservative reading). No member reaches that point, so the reading changes
  no recommendation.
- O-2 Products: a micro and its full-size contract on the same market count as the same product
  (MNQ = NQ, M2K = RTY, MYM = YM, MCL = CL, MGC = GC, MHG = HG). ES and MES are a different product from
  every H product (they are not among E.12's 27 price paths), even though NQ, YM and RTY track them
  closely; the correlation is stated as a relation, not an identity.
- O-3 "Tested member" means a rule whose P&L or test statistic was actually computed on market data
  (a screen, a confirmation read, a Gate 0 test, a D.1/D.1b/D.1d/D.1f trial or statistic). Rules that
  were drafted or excluded but never computed (E.0's X-03 K2-auc5d-01 and X-04 K2-eom2d-01, E.13/E.14's
  C2, C1 which is frozen but not run, ML v1 members, K9-anncday-01) are reported as relations, never as
  grounds for a drop.
- O-4 Settlement minutes: the comparison of clock windows uses D6's session table
  (docs/STAGE_E_DESIGN.md D6: equity 15:00, rates 14:00, FX 14:00, energy 13:30, gold 12:30, copper
  12:00, grains 13:15, livestock 13:00 CT), which every Stage E port encodes as C and which equals the
  lead's prior for S_p. Task 1 owns S_p. Where Task 1's table differs from D6's C on some dates (for
  example an earlier settlement minute in 2010-2012), the H1/H4 clock windows on those dates differ from
  the ports' windows, which only widens the difference reported here.

## 1. Inventory: what the program has tested, and on which bars

Sources: docs/STAGES.md; progress.md; reports/stage_d1_accounting.json; reports/stage_d1f_confirmation_list.md
and stage_d1f_run_tables.md; reports/stage_e0_catalog.md (assembled K1-K8, with E.1 and review rulings);
reports/stage_e10_catalog_K9.md; reports/stage_e3_k2_screen, stage_e4_k4_screen, stage_e4b_k5_screen,
stage_e4c_k3_screen, stage_e6_k7_screen, stage_e7_k1_screen, stage_e8_k6_screen, stage_e9_k8_screen
(the *_research_cluster.json tier tables); reports/stage_e5_k4_confirmation and E.5_RETURN.md;
docs/STAGE_E_ML_V2_DESIGN.md, reports/stage_e12_phase1_bars.json, stage_e12_gate0.json/.md,
E.12_RETURN.md; reports/stage_e13_* and stage_e14_prereg_C1.md, stage_e14_c1_model.md,
stage_e14_c2_result.md; ledger/trial_registrations.jsonl; docs/DECISIONS.md V24, V28, V29.

| Program read | Products | Bars read (data window) | Clock coverage | H-relevant content |
|---|---|---|---|---|
| Stage D.1, D.1a, D.1b (EDA), D.1d | MES only | research 2025-04-01..2026-05-13 | full sessions | A-H2 close window, E-H3, E-H4, D-H4, F3.2, F3.3, F4.2, Family H |
| Stage D.1f confirmation (58 Tier A + 43 Tier B) | MES only | 2020-02-03..2024-02-29 | full sessions | same members; every class C1-C5, C7 null |
| Stage E screens E.3, E.4a, E.4b, E.4c, E.6, E.7, E.8, E.9 (145 trials) | K1-K8 vehicles (MNQ, M2K, MYM; ZT, ZF, ZN, TN, ZB, UB; 6E, 6A, 6B, 6C, 6J, 6S, 6N; MCL, NG; MGC, MHG; ZC, ZW, ZS, ZM, ZL, HE, LE; MBT; MGC with MES; 6C with MCL; MNQ with MBT) | research 2025-04-01..2026-06-19 only | each member's own window | every CP1, CP2, CP3 port and every cluster member |
| Stage E.5 K4 confirmation (12 trials, null) | MCL (micro step-2 store), NG | MCL 2021-07-12..2024-02-29 (586 days); NG 2019-05-06..2024-02-29 (1,070 days) | each K4 member's window | K4-cp1-01 (13:00-13:29 CT), K4-cp3-01 (08:01-13:29), K4-eiamom-01, K4-ovr-01 |
| Stage E.12 Gate 0 (273 tests, FAIL) | all 27 H products plus MBT (E.12 price paths; MES refused) | 2019-05-06..2024-02-29 (S_X: ZF from 2020-10-01, ZT from 2021-10-01, MBT 2024-01-02) | decision times t1-t3 from O_X+30, targets h60, h120 and F (flatten F_X 15:08; grains 13:18; livestock 13:03) with features from bars closed by t | 64 signals incl. cp1_ret, cp3_clv, k2_auction_mto/msince, k2_monthend_msince, g04_ret_day, g05_gap, g08_prev_ret, g16_month_end; family B ridge per product-horizon |
| Stage E.14 C1 M1 fit (no new bars) | E.12 panel (all 81 pairs) | the E.12 panel, 2019-05..2024-02 | as Gate 0 | re-fit of Gate 0's ridge; q reproduced |
| Stage E.14 C2 (stopped) | ES / MES | none: only a COUNT of GEX < 0 days; no price read | - | the H1 signal on ES; never run |
| C1 (frozen, not run; E.17 runs it before H1-H5) | NG traded; NQ, ZN, 6E, GC, ZC as G17 feature legs | 2010-06-07..2019-04-30 | NG decisions 08:30, 10:30, 13:00 CT, h60 and F; legs' 60-minute returns ending at t | reads NG in H1's NG window; GC's 12:00-12:59 and ZC's 12:00-12:59 minutes as inputs |
| ledger/trial_registrations.jsonl | - | - | - | one line, the baseline (N = 471); nothing registered since |

Stage E confirmation reads other than E.5's: none. K5 stopped before its list (E.5); the Tier A
members of K3 (K3-ldnrev-01 6E), K6 (K6-limitcont-01 HE) and K8 (K8-flight-01 HEOD, K8-wkndbtc-01)
never reached a confirmation read (docs/STAGES.md: "Stage E.3b onward ... (planned)"). ML route v1
(E.2a) was frozen and superseded, never trained on market data. K9-anncday-01 was drafted (E.10),
never frozen or screened; it entered Gate 0 only as the flag k9_anncday.

## 2. H1: settlement-window intraday momentum, pooled (27 products)

H1: signal s = sign(close of bar S_p-31 on d minus PS(p, d-1) = close of bar S_p-1 on d-1); entry at
the open of bar S_p-30, exit at the open of bar S_p; pooled daily equal-risk mean; 2010-06..2024-02.

| Member | Cluster / family | Signal (what it reads) | Decision time and hold | Products | Data window screened or confirmed | Result | Similarity | Reason (one line) |
|---|---|---|---|---|---|---|---|---|
| K1-cp1-01 | K1, port CP1 (D.1 F3.3(a)) | sign(close 08:59 - open of the 17:00 CT first bar of d) | entry 14:30 open, exit 14:59 open | MNQ, M2K, MYM (= NQ, RTY, YM) | research 2025-04..2026-06 | Tier B (t +0.33, -0.98, -1.82) | related | same entry minute and products, exit 1 min earlier; signal is overnight + first half hour, not prior settlement to S-31 |
| K2-cp1-01 | K2, CP1 | sign(close 07:49 - open 17:00 CT first bar) | 13:30 open to 13:59 open | ZT, ZF, ZN, TN, ZB, UB | research | Tier B, all negative (t -1.12 to -5.34) | related | same window on all six rates products (all six are H products); different signal span |
| K3-cp1-01 | K3, CP1 | sign(close 07:49 - open 17:00 CT first bar) | 13:30 to 13:59 | 6E, 6A, 6B, 6C, 6J (6S, 6N excluded on coverage) | research | Tier B (t +0.32 to -5.53) | related | same window; different signal span; 6S and 6N never screened here |
| K4-cp1-01 | K4, CP1 | sign(close 08:29 - open 17:00 CT first bar) | 13:00 to 13:29 | MCL (= CL), NG | research; CONFIRMATION MCL 2021-07-12..2024-02-29, NG 2019-05-06..2024-02-29 | research Tier B (t +0.35, -1.01); confirmation null (theta_hat MCL -6.93, NG -1.43 net ticks/ct/day) | related | the only rule ever confirmed in H1's exact clock window on H1 products' 2019-2024 bars; signal differs |
| K5-cp1-01 | K5, CP1 | sign(close O+29 - open 17:00 CT first bar) | MGC 12:00 to 12:29; MHG 11:30 to 11:59 | MGC (= GC); MHG excluded (coverage) | research | MGC Tier B (t -0.13); MHG not run | related | same window on gold; copper's window never screened by any member |
| K6-cp1-01 | K6, CP1 | sign(close 08:59 - open of the first bar, 19:00 CT evening session) | grains 12:45 to 13:14; livestock 12:30 to 12:59 | ZC, ZW, ZS, ZM, ZL, HE, LE | research | Tier B, all negative (t -1.24 to -6.01) | related | same window; different signal span |
| K7-cp1-01 | K7, CP1 | as CP1 | 14:30 to 14:59 | MBT | research | Tier B (t -1.79) | unrelated | MBT is not an H product |
| Gate 0 cp1_ret (family A) | E.12 ML v2 | CP1's signal as a z-scored feature at t1, t2, t3 | forward h60, h120, F from t1-t3 (holds that span or include S-30..S on most groups) | all 27 (+MBT) pooled | 2019-05-06..2024-02-29 | t -0.03 / +0.26 / +0.29; not rejected | related | CP1 signal against intraday forward returns, not the S-30..S window alone |
| Gate 0 g04_ret_day (family A) | E.12 generic G4 | return since the trade date's first bar (17:00 CT open) to t | forward h60, h120, F from t1-t3; at t3 (equity 13:00, rates/FX/gold 12:50, energy 13:00, grains 11:00) the h120/F targets contain S-30..S | all 27 pooled | 2019-05..2024-02 | t +0.62 / +0.35 / +0.03; not rejected | related | closest computed analogue of the rest-of-day signal; reference is the Globex open, not prior settlement, and the target is not the last 30 minutes |
| C2 (E.13 draft, E.14 Task 7) | E.13 ranking C2 | R_rod = close(14:29 bar)/close(14:59 bar of d-1) - 1; T1 only GEX < 0, T2 every date | entry 14:30 open, exit 15:00 open | ES path, MES vehicle | 2011-05-03..2019-04-30 (planned) | STOPPED at its power rule before freeze; no price read; not registered | related (identical rule, different product, never tested) | C2's T2 is H1's rule exactly, on ES; H1 runs it on 27 products that exclude ES |
| F3_3 (a) overnight_to_close, (b) opening_30min_to_close | Stage D.1b Family F / D.1f class C3 | (a) first bar to 09:00, (b) 08:30-09:00, each against 14:30-15:00 | 14:30 to 15:00 | MES | EDA 2025-04..2026-05; confirmation 2020-02-03..2024-02-29 (reversal-signed, s = -1) | C3 null | related | CP1's MES parent; product MES; signal span differs |
| F3_2_bucket12_bucket13 | D.1b F3.2 / D.1f C3 | 14:00-14:30 return | 14:30 to 15:00 | MES | EDA; confirmation 2020-02..2024-02 | C3 null | related (weak) | adjacent-bucket form (GHLZ's 12th half hour); MES |
| A-H2 rth close window (buy), (sell) | Stage D.1 family A, class C1 | none (unconditional clock) | 14:30 to 15:00 | MES | research; confirmation 2020-02..2024-02 | C1 null | related (window only) | same window, no signal; MES |
| E-H3 quarterly witching short | D.1 family E, C5 | witching Friday only, short | last 30 min of RTH | MES | research; confirmation | C5 null by inactivity | unrelated | calendar short, MES |
| K4-eiamom-01 | K4 (X7) | WPSR-day 09:30-10:00 CT return | 14:30 to 15:00 CT (after CL's 13:30 settlement) | MCL | research; confirmation MCL 2021-07..2024-02 | Tier B; null (theta -0.09) | related (weak) | half-hour momentum into a late window, but not S-30..S and only WPSR days |
| K2-aucpost-01, K2-fomcpost-01 | K2 (X5, X6) | none (event day, BUY) | aucpost 12:05-15:05 (13:00 ET closes); fomcpost 13:30-15:05 | ZT, ZF, ZN, TN, ZB, UB | research | Tier B | unrelated | unconditional event-day longs that happen to span 13:30-14:00 on a few days a year |
| K6-wasdepost-01 | K6 (X8) | ZC 10:59-11:14 WASDE move | 11:15 to 13:14 | ZC | research | Tier B (t -0.75) | unrelated | WASDE-keyed; spans ZC's window on 12 days a year |
| K4-ovr-01, K5-ovr-01, K6-ovr-01 (excluded) | X10 hourly reversal | fade an extreme 60-minute move | 59-minute holds inside the day session | MCL, NG; MGC, MHG; grains | research; K4 confirmation | Tier B; K4 null | unrelated | reversal of the last hour, conditioned on an extreme; opposite family |
| C1 (frozen, not run) | E.13/E.14 C1 | Gate 0 ridge r_hat | NG t3 13:00 with h60 and F | NG | 2010-06..2019-04 (E.17, before H1) | not run | unrelated (signal); data reuse | will read NG's 13:00-13:30 bars of 2010-2019 before H1 runs |

Settled near match (lead's question): CP1 against H1. The trade window is the same to the minute at
entry (S-30 = C-30 open) and one minute longer at exit (H1 exits at the S_p open, CP1 at the C-1 open);
products overlap on 24 of 27 markets in the research screens (6S, 6N and HG never had a CP1 screen).
The signals differ in span: CP1 reads [17:00 CT Globex open of d, O+30) (19:00 for grains);
H1 reads [S_p of d-1, S_p-30 of d), which contains CP1's span plus d-1's post-settlement minutes and
the whole O+30..S-31 day segment. That is Baltussen, Da, Lammers and Martens' rest-of-day form; CP1 is
the Gao-Han-Li-Zhou first-half-hour form (D6 row CP1; U8 kept CP1 "in the (a) form only"). The program
itself records that "The rest-of-day form (open to 14:30) and its gamma conditioning were not screened"
(reports/stage_e13_info_sources.md line 263). No program computation used a prior-settlement reference
for a last-30-minute trade. The two signals share their overnight component, so their signs are
positively correlated (degree not computed: no data read). Not identical.

Classification history to disclose: E.10's K9 exclusion list put "any 'early-session return predicts the
later session' rule, conditioned or not" under X1 (CP1), and the E.10 reader logged Baltussen et al.
(K9O-018) as "X1" (reports/stage_e10_design_target.md line 152; stage_e10_research_overnight.md
line 655). That was a mechanism-level exclusion rule for K9, stricter than E.16's identity rule; under
it H1 would have been excluded as X1. Under E.16's rule it is related.

**Recommendation H1: KEEP (related).** Closest member: K#-cp1-01 (CP1 on K1-K6), and K4-cp1-01 for the
2019-2024 confirmation read; closest untested rule: C2's T2.

Recommended relation text for H1's freeze:
> H1 trades the same clock window as the program's CP1 port (entry at the open of the bar at S_p-30;
> CP1 exits one minute earlier, at the C-1 open, with C equal to D6's settlement minute) on 24 of
> H1's 27 markets, but with a different signal: the sign of the rest-of-day return from the prior
> date's settlement price to the close of bar S_p-31 (Baltussen, Da, Lammers and Martens), where CP1
> uses the overnight plus first-half-hour return (Gao, Han, Li and Zhou). The signals share their
> overnight component and are positively correlated. CP1 was Tier B on every cluster's research
> window (2025-04..2026-06; negative on rates, FX ex-6E, grains and livestock) and null on its only
> confirmation read (K4: NG 2019-05..2024-02, MCL 2021-07..2024-02). The rest-of-day form was never
> computed by the program; E.14's C2 drafted it on ES (T2 is H1's rule on ES) and stopped before any
> price was read. E.10 classed this form under the CP1 mechanism (X1) for K9; E.16 tests it as a
> separate signal and counts it in N. Gate 0 (2019-05..2024-02) tested CP1's signal and the
> since-the-open return (g04) as pooled features against intraday horizons that contain this window;
> neither was rejected.

## 3. H2: month-end NQ/ZN rebalancing pair (multi-day, IBKR)

H2: on the fifth-last joint trading day d5 at 15:00 CT, MTD_NQ vs MTD_ZN (from the prior month's last
settlement); short the outperformer, long the other; both legs held to their settlement minutes on the
month's last day dL; per-month pair P&L, volatility matched.

| Member | Cluster / family | Signal | Decision time and hold | Products | Data window | Result | Similarity | Reason |
|---|---|---|---|---|---|---|---|---|
| K2-monthend-01 | K2 (X12), port of D.1 family E | none: calendar (last two trade dates N-1, N) | BUY 07:21 to 15:05 CT on N-1 and on N, each intraday | ZT, ZF, ZN, TN, ZB, UB | research 2025-04..2026-06 | Tier B (ZN t -0.48; all six t -1.42 to +0.04) | related | ZN month-end demand (Hartley and Schwarz; Dyer, Fleming and Shachar) inside H2's hold, but unconditional long, intraday, one leg, no equity leg |
| X-04 K2-eom2d-01 | E.0 K2 excluded (flat by F) | none: long from the close two days before month-end to the last day's close | two-night hold | rates | never computed | excluded at E.0 | related (untested) | the multi-day bond month-end trade; no equity leg, no relative signal |
| Gate 0 k2_monthend_msince | E.12 member flag | minutes since K2-monthend's event | intraday h60/h120/F | all 27 pooled | 2019-05..2024-02 | t -0.44 / -1.72 / -1.33; not rejected | related (weak) | month-end clock flag, intraday |
| Gate 0 g16_month_end | E.12 generic G16 | flag: last two trade dates of the month | intraday h60/h120/F | all 27 pooled | 2019-05..2024-02 | t +0.66 / +0.87 / +0.90; not rejected | related (weak) | month-end clock, intraday, unsigned by performance |
| K3-mehedge-01 | K3 (X12), with an external index | month-to-date local equity return (Nikkei; EURO STOXX not traded) | the hour before the month-end London 4 p.m. fix | 6J | research | Tier B (t -1.57) | related (mechanism) | rebalancing sized by month-to-date equity performance (Melvin and Prins), but FX, intraday, one leg |
| K3-ldnrev-01 | K3 (X9/X12) | 10-minute pre-fix move | after the month-end London fix | 6E (Tier A t 1.42), 6J, 6S | research | Tier A on 6E never confirmed | unrelated | fix-flow reversal on FX |
| E-H4 turn-of-month long | D.1 family E, C5 | none: last day of month plus first 3 days | intraday long each day | MES | research; confirmation 2020-02..2024-02 | C5 null | related (weak) | equity month-end flow, unconditional, intraday, MES |
| K9-anncday-01 | E.10 draft (never screened) | macro-announcement trade dates (about half at the turn of the month) | long the announcement trade date | MNQ, M2K, MYM | none (Gate 0 flag only) | not screened | unrelated | release-keyed, not month-end-keyed (E.10's X12 ruling) |
| Gate 0 g17_nq, g17_zn | E.12 generic G17 | 60-minute returns of NQ and ZN as cross-product features | intraday | all 27 pooled | 2019-05..2024-02 | not rejected | unrelated | no month-to-date return, no pair |

Settled near match (lead's question): K2's month-end slices against H2. K2-monthend-01 takes the
day-session slices of days N-1 and N with an unconditional long in each rates contract; H2 holds a
pair from d5's 15:00 CT to dL's settlement (five trading days, overnight), sizes NQ against ZN, and
signs both legs by relative month-to-date performance. K2-monthend's ZN slices lie inside H2's ZN
holding period on months where H2 is long ZN; on months where H2 is short ZN they are the opposite
position. No program member traded NQ around month-end, held anything across a month-end night, or
read a month-to-date return of NQ or ZN. Not identical.

**Recommendation H2: KEEP (related).** Closest member: K2-monthend-01 (ZN); closest untested rule: X-04.

Recommended relation text for H2's freeze:
> H2's bond leg overlaps K2-monthend-01, which bought ZN (and ZT, ZF, TN, ZB, UB) in the day sessions
> of the last two trade dates of each month (07:21-15:05 CT, unconditional; Tier B on the research
> window 2025-04..2026-06, ZN t -0.48). H2 differs in four ways: it holds overnight from the
> fifth-last joint trading day to the last day's settlement, it has an NQ leg, its direction comes from
> the NQ-versus-ZN month-to-date return (Harvey, Mazzoleni and Melone's rebalancing flow), and the two
> legs are volatility matched. E.0 excluded the multi-day bond month-end hold (X-04 K2-eom2d-01) for
> the flatten and never tested it. K3-mehedge-01 (Tier B) used month-to-date equity returns to sign a
> month-end FX trade; MES's turn-of-month long (E-H4) was null on 2020-02..2024-02. Gate 0 tested only
> intraday month-end flags (g16_month_end, k2_monthend_msince) on 2019-05..2024-02; neither was
> rejected. No program test read a month-to-date NQ or ZN return or held a position across days.

## 4. H3: Treasury auction cycle (multi-day, IBKR)

H3: per 2-, 5-, 10-, 30-year auction (ZT, ZF, ZN, ZB; E.0's EC-AUC filter): short at S_T on t-3, cover
and go long at S_T on t, exit at S_T on t+5; per-auction P&L; same-tenor overlaps keep the earlier.

| Member | Cluster / family | Signal | Decision time and hold | Products | Data window | Result | Similarity | Reason |
|---|---|---|---|---|---|---|---|---|
| K2-aucpre-01 | K2 (X5) | none: auction day (EC-AUC, same filter and tenor map; also TN 10-year, UB 30-year) | SELL from T_a-180 to T_a-1 (T_a = competitive close - 1 h CT; 09:00-11:59 for 13:00 ET closes) on the auction day | ZT, ZF, ZN, TN, ZB, UB | research | Tier B (t -1.36 to +0.48) | related | same events, same short-before sign, but 179 minutes on the auction day, not settlement t-3 to t |
| K2-aucpost-01 | K2 (X5) | none: auction day | BUY T_a+5 to T_a+185 (12:05-15:05 CT) | same six | research | Tier B (ZN t -2.02) | related | same events, same long-after sign, intraday only, not t to t+5 |
| X-03 K2-auc5d-01 | E.0 K2 excluded (flat by F) | none: auctions | short 5 days before, long 5 days after (Lou, Yan and Zhang, K2-001) | rates | never computed | excluded at E.0 | related (untested) | the multi-day form of H3's own source; H3's pre-window is 3 days, not 5 |
| Gate 0 k2_auction_mto, k2_auction_msince | E.12 member flags (auction pre and post; also 7- and 20-year as clock inputs) | minutes to / since the auction | intraday h60/h120/F | all 27 pooled | 2019-05..2024-02 | mto t +0.06 / -1.86 / -1.63; msince t +0.50 / +1.48 / +1.38; not rejected | related (weak) | auction clock as an intraday feature; no multi-day hold |
| K5-preauc-01 | K5 (X9) | LBMA auction schedule | short into LBMA auctions | MGC | research | Tier B | unrelated | metals auctions, not Treasury |
| K9 "Treasury announcement-day premium" | E.10 K9 excluded | Treasury announcement dates | daily | rates | never computed | excluded (round 2 item 15) | unrelated | announcement premium, not the auction cycle |

Settled near match: K2's intraday auction slices against H3. K2-aucpre and K2-aucpost trade the same
EC-AUC events with the same tenor match and the same V shape (short before, long after), but each only
within the auction day, three hours on each side of the close. H3 holds from settlement three trading
days before to settlement five trading days after, overnight, and reverses at the auction day's
settlement (14:00 CT), not at the competitive close (12:00 CT). The literal multi-day form of the same
paper was excluded at E.0 (X-03) and never computed. Not identical.

**Recommendation H3: KEEP (related).** Closest members: K2-aucpre-01 and K2-aucpost-01; closest untested
rule: X-03 K2-auc5d-01.

Recommended relation text for H3's freeze:
> H3 trades the same Treasury auctions, filtered as E.0 (Note or Bond, not floating, not inflation-
> indexed, announced before the auction date), and the same short-before / long-after shape as
> K2-aucpre-01 and K2-aucpost-01, which held only the 180 minutes before and after the auction close on
> the auction day (also on TN and UB) and were Tier B on the research window 2025-04..2026-06. H3 holds
> across days: short from the settlement minute three trading days before to the auction day's
> settlement minute, then long to the settlement minute five trading days after. Its source, Lou, Yan
> and Zhang (E.0 log K2-001), was logged at E.0 as supporting evidence; its literal five-day form was
> excluded at E.0 for the flatten (X-03) and never tested. Gate 0 tested only intraday auction-clock
> flags (k2_auction_mto, k2_auction_msince) on 2019-05..2024-02; neither was rejected.

## 5. H4: next-day reversal of the settlement-window move

H4: m = open(bar S_p on d-1) - open(bar S_p-30 on d-1); trade -sign(m) from the open of bar O_p+1 on d to
the open of bar S_p-31 on d; pooled daily equal-risk mean.

| Member | Cluster / family | Signal | Decision time and hold | Products | Data window | Result | Similarity | Reason |
|---|---|---|---|---|---|---|---|---|
| K#-cp3-01 (K1, K2, K3, K4, K5, K6) | port CP3 (MES Family H6, C7) | CLV of d-1's [O, C) day bar: >= 0.8 buy, <= 0.2 sell (continuation) | decision on the O bar, fill at the O+1 open; exit at the C-1 open | MNQ, M2K, MYM; ZT, ZF, ZN, TN, ZB, UB; 6E, 6A, 6B, 6C, 6J, 6S, 6N; MCL, NG; MGC, MHG; ZC, ZW, ZS, ZM, ZL, HE, LE | research; CONFIRMATION K4-cp3-01 MCL 2021-07..2024-02, NG 2019-05..2024-02 | all Tier B; K4 null (theta MCL -1.79, NG -5.41) | related | identical entry fill (O+1 open) on all 27 markets; exit 30 min later (C-1 vs S-31); signal is the prior day's close location (continuation), not the prior day's last-30-minute move (reversal) |
| Gate 0 cp3_clv | E.12 port feature | CP3's CLV | intraday h60/h120/F from t1-t3 | all 27 pooled | 2019-05..2024-02 | t -1.95 / -1.93 / -1.61 (negative IC: reversal-leaning); not rejected | related | prior-day close location against next-day intraday returns; seen before H4 was named |
| Gate 0 g08_prev_ret | E.12 generic G8 | prior complete day's return over sigma | intraday h60/h120/F | all 27 pooled | 2019-05..2024-02 | t -1.57 / -2.08 / -0.94 (negative: reversal-leaning); not rejected | related | prior-day move faded next day, full-day span, not the 30-minute window |
| Gate 0 g05_gap | E.12 generic G5 | day-session open minus prior close at C_X | intraday | all 27 pooled | 2019-05..2024-02 | not rejected (not tabulated here) | unrelated | overnight gap, not d-1's last 30 minutes |
| Family H6 prior close location; H1-H5 range-conditioned breakouts | D.1f Family H (C7) | prior daily bar (CLV; range state) | H6: decided on the 08:30 bar, filled at 08:31, exit 14:58 decision | MES | confirmation 2020-02..2024-02 | C7 null | related (weak) | CP3's MES parent |
| D-H4 overnight gap fade | D.1 family D (C4) | overnight gap size / direction | RTH fade | MES | research; confirmation | C4 null (net -1.21) | related (weak) | fade at the next open, but of the gap, not d-1's late move; MES |
| F4.2 prior RTH close crossing | D.1b F4 | crossing of the prior 14:59 close | 15-minute forward | MES | EDA; Tier B in D.1f | null | unrelated | level-crossing event |
| B-H2 prior-day stop cascade | D.1 family B (C2) | break of the prior session's high/low | short hold | MES | research; confirmation | C2 null | unrelated | breakout of prior range |
| K6-limitcont-01 | K6 (X11) | prior-day limit close direction | 08:45 to C-1, continuation | HE (Tier A, 1 trade), LE (0 trades) | research | Tier A HE never confirmed | related (weak) | next-day trade after an extreme prior-day close, opposite sign (continuation), limit days only |
| K6-crushgap-01 | K6 (X10) | overnight change in the soybean crush margin | 08:31 to 13:14, fade | ZS | research | Tier B (t -2.71) | unrelated | overnight spread gap |
| K8-wkndbtc-01 | K8 (X14) | weekend MBT move | Sunday 18:00 to Monday 14:59 | MNQ | research | Tier A (t 1.07), never confirmed | unrelated | cross-market signal |
| K9 excluded: "long equity after a large prior-day shock", "continue the prior day in calm states" | E.10 | prior-day move | next session | equity | never computed | excluded | related (untested) | prior-day move to next day; X3-adjacent per E.10 |
| K9O-018 Baltussen et al. (E.10 log) | literature only | "reverts over the next days" (P-K9O-018-b) | - | - | - | logged, not tested | basis | the logged evidence for H4's sign |

Settled near match (lead's question): members that trade the day-session open after a prior-day move.
CP3 on every exposure enters at exactly H4's fill (the O+1 open), on the same 27 markets, and holds
until the C-1 open (H4 stops at S-31, 30 minutes earlier, so it never overlaps H1). CP3 signs the trade
by where d-1 closed in its day range (buy high, sell low: continuation), and trades only CLV extremes;
H4 signs it against d-1's last-30-minute move, every day with m != 0. A strong late rally on d-1 tends to
put the close near the high, so CP3 would buy where H4 sells: the signals are negatively related, not
equal. No program member traded against d-1's settlement-window move. Not identical.

Disclosure for H4's freeze (seen results): Gate 0's family A, run on 2019-05..2024-02 bars of all 27
products before H4 was named, showed reversal-leaning pooled ICs for the two prior-day features, cp3_clv
(t -1.95, -1.93, -1.61) and g08_prev_ret (t -1.57, -2.08, -0.94), none rejected; and K4-cp3-01 NG's
confirmation was negative (theta -5.41 net ticks/day, UCB95 -1.70). These are in H4's direction and on
the overlapping 2019-2024 segment.

**Recommendation H4: KEEP (related).** Closest member: K#-cp3-01 (CP3, same entry fill, same markets).

Recommended relation text for H4's freeze:
> H4 enters at the same fill as the program's CP3 port (the open of the bar after the day-session
> open) on the same markets, and exits 30 minutes earlier (the S_p-31 open against CP3's C-1 open). Its
> signal differs: H4 trades against the sign of d-1's settlement-window move (S_p-30 to S_p, H1's
> window), every day the move is non-zero; CP3 trades with d-1's close location in its day range, only
> at CLV >= 0.8 or <= 0.2. The signals are negatively related. CP3 was Tier B on every cluster's research
> window and null on its K4 confirmation (NG 2019-05..2024-02, MCL 2021-07..2024-02). Before H4 was
> named, Gate 0 (2019-05..2024-02, all 27 products) showed reversal-leaning, unrejected pooled ICs for
> CP3's CLV (t -1.95 / -1.93 / -1.61) and the prior day's return (t -1.57 / -2.08 / -0.94), and K4-cp3-01
> NG's confirmation was negative; these are disclosed as seen results on the overlapping segment. The
> sign rests on Baltussen et al.'s "reverts over the next days" (logged at E.10 as K9O-018). No program
> member conditioned on the prior day's last-30-minute move.

## 6. H5: equal-risk combination of H1 to H4

| Member | Family | What it combines | Hold | Products | Data window | Result | Similarity | Reason |
|---|---|---|---|---|---|---|---|---|
| Gate 0 family B (gate0B_<p>_<h>) | E.12 ML v2 | ridge (lambda 0.1) over 64 signals incl. cp1_ret, cp3_clv, g08_prev_ret, g16_month_end, k2_monthend_msince, k2_auction flags; top-20% confident trades | intraday h60/h120/F | 27 products x 3 horizons (81 tests) | 2019-05..2024-02 | FAIL: no pair rejected; pooled mean gross -0.72 ticks vs cost 2.26 | related (weak) | a combination of signals (features) per product, not of strategy P&L series; intraday only |
| ML v2 portfolio (V2.6-V2.8) | E.11/E.12 design | model portfolio with risk sizing | intraday | all | never run (v2 stopped at Gate 0) | not run | unrelated (untested) | never computed |
| K#-ml-01 (ML route v1) | E.0/E.2a | ML member per cluster | intraday | per cluster | never run (excluded U6; superseded) | not run | unrelated (untested) | never computed |
| D-H2 inverse-vol sizing; RT7 | D.1 family D (C4) | one strategy sized by trailing volatility | intraday | MES | research; confirmation | C4 null | unrelated | sizing rule, not a combination |
| C3 trend + carry (E.13) | E.13 research | published index series | multi-day | none (no program data) | none | research only | unrelated | no program test |

No program member combined several base rules' P&L series. **Recommendation H5: KEEP.** It has no
identical member; its relations are those of H1 to H4.

Recommended relation text for H5's freeze:
> H5 combines the daily net P&L series of H1 to H4 at equal trailing-60-date risk; it inherits each
> component's relations (sections of H1 to H4). No program member combined base-rule P&L series. The
> nearest computation is Gate 0's family B (E.12, 2019-05..2024-02), a ridge combination of 64
> intraday features per product-horizon (including the CP1, CP3, prior-day-return, month-end and
> auction features), which failed with no pair rejected; ML route v2's portfolio and ML route v1 were
> never run.

## 7. Data reuse: program reads of H products' 2019-05..2024-02 bars in H's windows

All H tests' 2019-05-06..2024-02-29 segment comes from the E.12 phase-1 stores, the same bytes Gate 0
read. V24 (docs/DECISIONS.md) states: "The phase-1 stores stay on disk; any reuse needs a new
pre-registration that counts N = 471" and, for E.13, "Re-running Gate 0, relaxing its bar, or re-mining
the 2019-2024 stores is ruled out"; V28 and V29 then direct H1-H5 onto data already owned with the
2019-05 fallback. The freeze should cite these and the reads below.

| H | Program reads of H's products in H's window, 2019-05..2024-02 | Also later (2010-2019) |
|---|---|---|
| H1 | (1) E.12 Gate 0, all 27 products (ZF from 2020-10-01, ZT from 2021-10-01 by D4's S_X): every decision row's features read bars closed by t1-t3, and its h60/h120/F targets read forward bars to as late as F_X; the bars S_p-31, S_p-30 and S_p and d-1's S_p-1 lie inside what Gate 0 read for every group (S_p <= F_X; for grains and livestock S_p = 13:15 / 13:00 against F_X 13:18 / 13:03). Tests touching the signal family: cp1_ret, g04_ret_day (not rejected). (2) E.5 K4 confirmation: K4-cp1-01 traded exactly 13:00-13:29 CT on NG 2019-05-06..2024-02-29 and on MCL (micro store of the CL market) 2021-07-12..2024-02-29, null. Every other K4 member's run read the same stores. (3) E.14's M1 fit re-read Gate 0's panel (features and targets), no new bars. (4) D.1f read MES's 14:30-15:00 (not an H product). | C1 (E.17, run before H1-H5): NG 2010-06..2019-04 including 13:00-14:00 (t3 h60) and to F; G17 legs' 60-minute returns ending at the decision times read GC's 12:00-12:59 (contains GC's H1 window 12:00-12:30) and ZC's 12:00-12:59 (contains 12:45-12:59 of ZC's window); NQ, ZN, 6E are read only before their H1 windows (decisions <= 13:00 CT). |
| H2 | Gate 0 read NQ and ZN 2019-05..2024-02 day sessions including NQ's 15:00 and ZN's 14:00 settlement bars (t3 targets: NQ 13:00 + h120 = 15:00, F 15:08; ZN 12:50 + h120 = 14:50) and every month-end day; tests on month-end flags only (g16_month_end, k2_monthend_msince), intraday. No multi-day hold and no month-to-date return was ever computed. MNQ and ZN research screens (2025-04..2026-06) lie outside H2's window. | C1 reads NQ and ZN 2010-2019 as G17 legs, 60-minute returns ending at 08:30, 10:30, 13:00 CT; not their settlement bars, no month-to-date returns. |
| H3 | Gate 0 read ZT (from 2021-10-01), ZF (from 2020-10-01), ZN and ZB 2019-05..2024-02 day sessions including the 14:00 settlement bar (t3 12:50 + h120 = 14:50; F 15:08) on every date of every H3 window; tests on auction flags only, intraday. No multi-day auction hold computed. | C1 reads ZN 2010-2019 as a G17 leg (60-minute returns ending at <= 13:00 CT); not the 14:00 settlement bar. |
| H4 | Gate 0 read all 27 products' d-1 S_p-30..S_p bars and d's O_p+1..S_p-31 bars, 2019-05..2024-02 (as for H1); tests on cp3_clv and g08_prev_ret leaned to reversal (section 5), not rejected. E.5 read NG 2019-05..2024-02 and MCL 2021-07..2024-02 in CP3's window 08:01-13:29 (K4-cp3-01, null; NG negative) and in 13:00-13:29 (d-1 side). | C1 reads NG 2010-2019 day sessions from 08:30 (t1) onward, i.e. H4's NG window and its d-1 reference window; GC and ZC 60-minute legs as above. |
| H5 | The union of H1 to H4's reads. | The union. |

Research-window screens (2025-04..2026-06) never touch any H test window (H ends 2024-02-29), but their
results for CP1 (H1's window), CP3 (H4's fill), K2-monthend and K2-aucpre/aucpost are known and are part
of the relation texts above.

## 8. Summary of recommendations

| H | Recommendation | Closest tested member | What differs |
|---|---|---|---|
| H1 | keep (related) | K#-cp1-01 (CP1, K1-K6; confirmed only in K4) | signal span: prior settlement to S-31 vs Globex open to O+29; exit 1 minute later; untested twin C2 on ES |
| H2 | keep (related) | K2-monthend-01 (ZN) | pair with NQ, signed by relative MTD return, multi-day from d5 to dL; untested X-04 |
| H3 | keep (related) | K2-aucpre-01 / K2-aucpost-01 | settlement t-3 to t to t+5, overnight; untested X-03 is the source's 5-day form |
| H4 | keep (related) | K#-cp3-01 (CP3, same entry fill) | reversal of d-1's last-30-minute move vs continuation of d-1's CLV; exit 30 min earlier; Gate 0 seen results lean its way |
| H5 | keep | none (Gate 0 family B nearest) | combination of strategy P&L series, not of features |

None of H1 to H5 is identical to a tested member under O-1 to O-3, so no drop is recommended and the
Holm family stays at five unless the lead rules otherwise.

## 9. Points outside this task, flagged for the lead (not decided here)

- E.12's D4 start rule set S_X = 2020-10-01 for ZF and 2021-10-01 for ZT (E.12_RETURN.md line 536;
  reports/stage_e12_phase1_bars.json first_trade_date), although their store files are named
  2019-05-06. lead_spec section 2 takes "the E.12 stores begin 2019-05-06" for every product; whether
  H1, H3 and H4 read ZF before 2020-10 and ZT before 2021-10 (dates D4 refused for Gate 0) is a window
  rule the freeze should state. Similarly E.5's MCL confirmation started 2021-07-12 (MCL micro store),
  which does not bind H (H reads the CL path).
- V24's wording ("re-mining the 2019-2024 stores is ruled out" for E.13; "any reuse needs a new
  pre-registration that counts N = 471") should be quoted in the freeze beside V28/V29's instruction to
  use data already owned.
- H1's relation to C2: if C2 is ever revived, its T2 on ES would be H1's rule on a product correlated
  with NQ/YM/RTY; that later registration would need to cite H1's result.
