# R2 dossiers (Stage E.32b step 3b, spec 8.2): DossierWriter-OpusXHigh

> **Lead errata (session 3, 2026-10-29 06:47-06:49 PDT; applied in briefs/R2_combinations.json by
> work/R2/patch_v31_q3_lead.py; the dossiers below are unchanged).**
> 1. LR-Q3a. F01 on YM, MYM and RTY re-tests closed configurations, so those combinations are gated (Q3 = 0):
>    E16-H1 (R1-13; V31) applied F01's rest-of-day rule at h 30 to YM over 2019-05-06..2024-02-29 (signal sign(close of
>    bar S-31 minus the prior settlement), entry at S-30, exit at S); K1-cp1-01 (R1-03; frozen rule
>    strategy/members/k1/cp1.py:58-60) traded 14:30-14:59 CT on MYM and M2K. The R1-03 overlap text in the YM, MYM and
>    RTY F01 dossiers ("held to the flat") follows R1-03's line-level horizons field, not the member's code.
> 2. LR-V31. YM is a V31 fallback root ("no rerun or variant on these windows, no purchase of the 10 fallback roots"):
>    no buyable clean test window for YM or MYM (clean_test_window_months = 0 in every combination with a YM or MYM
>    member). E16-H4 (reversal of the prior day's settlement-window move, entry at the open + 1 minute, exit at S-31)
>    is an F08-type rule read on YM over the same window.
> 3. LR-ZLW. ZL keeps its sealed test window (V56 item 1); ZL F09 and F10 share its single read.
>
> **Lead errata (session 4, 2026-10-29 08:53 PDT; R1Fixer-OpusHigh for RV2 B1, S6 and N2; facts verified against the frozen
> code, see work/fix4/r1/r1fix_report.md; only the two R1 catalog rows below are edited, tagged "[corrected s4: see
> errata]").**
> 4. R1-11 and R1-15 cross-market content (RV2 B1/S6). Both ML libraries include G17, the 60-minute log returns of the
>    other clusters' lead prices (NQ, ZN, 6E, CL, GC, ZC; E.12 also MBT, live only from its 2024-01-02 store start;
>    g17_mes was excluded in E.12 by rule P-1a and in E.20 by the leg rule), never applied on the product's own cluster
>    (ml_route_v2/signals/generic.py:22-25, 343, 351-352; c1_replication/c1b.py:53-54). Live on RTY/M2K: ZN, 6E, CL, GC,
>    ZC; live on ZL: NQ, ZN, 6E, CL, GC (ZS and ZM are not G17 leads). E.12 Gate 0 (R1-11) tested them pooled over the
>    27 products including M2K and ZL at h60, h120, hF (reports/stage_e12_gate0.md:158-164, 222-228, 286-292) and as
>    inputs of Family B's pooled ridge; E.20 (R1-15) kept the six in its 36 frozen features on the 17 roots including
>    RTY and ZL (pattern_search/constants.py:59; reports/stage_e20_search_freeze.json feature_names) at h60, h120, hF,
>    2019-05-06..2024-02-29, decision times t1-t3 and t4 = F_X - 60 (14:08 CT equity, 12:18 CT grains). Every dossier
>    line that describes R1-11 or R1-15 only as "64 bar features", "36 bar features", "r_ROD features" or "1-minute bar
>    features" omits this, and the RTY|F09 and ZL|F09 dossiers' R1 overlap lists (lines 1242 and 1571)
>    omit R1-11 and R1-15.
> 5. RTY|F09 Q3. The rater's reason "no cross-market configuration closed on RTY or M2K" (R2_Q_ratings.md, RTY|F09) is
>    wrong: 60-minute leads from five other asset classes (ZN, 6E, CL, GC, ZC) were searched on RTY and M2K at h60-hF
>    (R1-11, R1-15). LR-Q3b (RULINGS.md, session 3 end) sets Q3 = 1 for C112-C116 and C138-C139 (same family and product
>    at a neighbouring horizon, spec 8.3); the leg-level reading (the dossiers' leaders, NQ for RTY and ZS/ZM for ZL,
>    were never live features there: Q3 = 2) is the sensitivity.
> 6. RV2 N2. E.29 section 3.2 measured daily-return correlations only for the CL, ZM, GC and NQ pairs (CL-ZM, CL-GC,
>    CL-NQ, ZM-GC, ZM-NQ, GC-NQ; reports/E.29_RETURN.md:134-148), none of YM-MNQ, YM-RTY or MNQ-RTY (nor MYM-MNQ,
>    MYM-RTY), so the EQ3 and EQ3m pools use the spec's default rho 0.5 within an asset class (spec 8.3;
>    R2_combinations.json rho_measured = {}). It is not that E.29 measured no correlation between the pool members:
>    it did not measure those pairs. (This file has no sentence saying E.29 measured no correlation; line 71, on the
>    basket model, is a different statement and is unchanged.)
> 7. R2_dossiers_for_rating.md is kept exactly as the CombinationScorer rated it.


Written 2026-10-29 05:58:24 PDT by work/R2/write_dossiers.py from work/R2/groundwork.json and work/R2/combos_detail.json (numbers by work/R2/build_combos.py). Spec sha256 09ebe6970fcf0270... Facts and arithmetic only; no outcome. One dossier per product or pool and family, with a venue table by combination id.

## Conventions

- SR80 (daily Sharpe, N 838): discovery G3+G4 0.2309 (binding), G3 alone 0.2025; test 0.1936 (work/F5/SR80.json). T_disc 796, T_test 870.
- Band B and h_c: the pair's F5 band (IBKR: LR-F5-IBKR); h_c = the member of B with the lowest G; a pool's band is the intersection of its members' bands and h_c the member with the lowest worst-member G (LR-R2b).
- c_f = S + 0.5 + F_rt / v (F5). g_be = c_f, g_1 = c_f + 1; p = 0.5 + g / (2 m_hc), normal approximation 0.5 + g / (1.596 sigma_hc).
- K_year: continuous families n_cap(h_c) x 252; daily families (F01, F08) 252; event families events a year x trades per event (1). K_disc = K_year x 796 / 252, K_test = K_year x 870 / 252; n/day = K_year / 252.
- Payout: the firm's daily payout-qualification threshold against sqrt(n/day) sigma_hc v (E.29); Topstep and Tradeify USD 150 a winning day; Lucid, MFFU, Bulenox state no daily threshold (0).
- News events a week: scheduled events whose firm news window overlaps the family's trading times (only Topstep blocks, and only full-size RTY and YM among these codes; frozen-calendar rates {'NFP': 0.2266, 'CPI': 0.2306, 'PPI': 0.2306, 'FOMC': 0.1471}).
- Queue-limit variant (Rithmic routes: Bulenox, Lucid, Tradeify): c_lim replaces each passive leg's half-spread and slippage with E.31's measured trade-through markout 0.970 ticks per fill; reported beside, never scored. Not computed at Topstep (TopstepX trade-through), MFFU (Tradovate) or IBKR.
- Overnight: no firm allows an overnight hold (F4 firms.<firm>.overnight.allowed false); every band is intraday, so no family here needs one. IBKR allows overnight holds (overnight margin shown beside).
- Own broker (IBKR): initial margin = the intraday initial margin (every band is intraday), against USD 6,000 (u); sigma_day = sigma_cc (LR-Q6d).
- Data: discovery 2020-12..2024-02 (39 months), test 43 months; costs are census estimates (F2_data_access k x months for MBO; the E.12 ohlcv-1m quote scaled by months for bars), labelled estimates.

How to read an R1 overlap entry: the relation of the closed line to this product, the configuration it tested, and a 'Reading' that states the line's status under LR-R1 (closed configuration, family closed on another product, evidence finding, stop, execution line). Whether a combination re-tests a closed line or is a close variant (Q3) is the CombinationScorer's judgment, not the Reading's. Evidence-row relations (this product, same underlying, cousin, other venue, pool) are the DossierWriter's extraction.

## Lead rulings and cross-family facts that bear on the ratings

- LR-R1: V38 closes the tested configurations of the 528 bar-based trials (R1-01..R1-18) on the 17 roots; its umbrella sentence with V45 item 4 is an evidence finding (R1-19), not a ban on new families. A closed configuration stays closed at every venue, the own broker included. The ZM 5-60 minute families of E.33c (V56) are closed on ZM and are family overlap on other products. NQ is excluded (V49); passive spread capture is closed (V50).
- Retail size (one contract, tens of milliseconds to a second, no co-location): information is priced within 1 to 5 seconds on ES, NQ, ZN and CL (E.25, C3 draft:70-71), so only effects that last minutes or longer are reachable; a one-lot moves no price.
- E.32 front: no commodity-futures study shows positive out-of-sample predictability net of costs at 1-240 minutes; event and once-a-day families fail on power over 39 months (E.32 methods brief:15-16).

- E.28 C3: on 1-minute bars the robust MES patterns were worth about 0.1 tick against a 2.1-tick round turn.
- E.33c (cost and trade-count facts only): minimum detectable edges 1.5 to 4.4 ticks a trade at the trade rates seen; the 61 G1 configurations lost more than 1.0 tick a trade after costs; at every firm's fee the median configuration loses 2.2 to 2.6 ticks a trade (ZM, 796 dates).
- E.31 (measured): a resting one-lot limit at the ZM touch under the trade-through rule has a gross 10 s markout of -0.970 ticks per fill [-0.988, -0.950] (model c, front month, DAY session); models (a) K-algorithm -0.287 and (b) FIFO -0.252 decide nothing.
- E.29 section 1 and 3.4: a one-lot micro rarely clears the USD 150 winning-day payout threshold (MGC); correlation barely mattered in the basket model.

## Dossier index

| dossier | combinations | product or pool | family |
|---|---|---|---|
| YM|F01 | C001-C006 (6) | YM | F01 intraday momentum into the close |
| YM|F04 | C007-C012 (6) | YM | F04 US macro release drift |
| YM|F05 | C013-C018 (6) | YM | F05 FOMC post-statement drift |
| YM|F08 | C019-C024 (6) | YM | F08 session and overnight-to-day handoff |
| YM|F10 | C025-C030 (6) | YM | F10 order-book state at 5 min and longer |
| YM|F11 | C031-C036 (6) | YM | F11 own-price-path trend and reversal |
| YM|F12 | C037-C042 (6) | YM | F12 expiry and option-hedging days |
| MYM|F01 | C043-C044 (2) | MYM | F01 intraday momentum into the close |
| MYM|F04 | C045-C046 (2) | MYM | F04 US macro release drift |
| MYM|F05 | C047-C048 (2) | MYM | F05 FOMC post-statement drift |
| MYM|F08 | C049-C050 (2) | MYM | F08 session and overnight-to-day handoff |
| MYM|F10 | C051-C052 (2) | MYM | F10 order-book state at 5 min and longer |
| MYM|F11 | C053-C054 (2) | MYM | F11 own-price-path trend and reversal |
| MYM|F12 | C055-C056 (2) | MYM | F12 expiry and option-hedging days |
| MNQ|F01 | C057-C061 (5) | MNQ | F01 intraday momentum into the close |
| MNQ|F04 | C062-C066 (5) | MNQ | F04 US macro release drift |
| MNQ|F05 | C067-C071 (5) | MNQ | F05 FOMC post-statement drift |
| MNQ|F08 | C072-C076 (5) | MNQ | F08 session and overnight-to-day handoff |
| MNQ|F10 | C077-C081 (5) | MNQ | F10 order-book state at 5 min and longer |
| MNQ|F11 | C082-C086 (5) | MNQ | F11 own-price-path trend and reversal |
| MNQ|F12 | C087-C091 (5) | MNQ | F12 expiry and option-hedging days |
| RTY|F01 | C092-C096 (5) | RTY | F01 intraday momentum into the close |
| RTY|F04 | C097-C101 (5) | RTY | F04 US macro release drift |
| RTY|F05 | C102-C106 (5) | RTY | F05 FOMC post-statement drift |
| RTY|F08 | C107-C111 (5) | RTY | F08 session and overnight-to-day handoff |
| RTY|F09 | C112-C116 (5) | RTY | F09 cross-market lead-lag |
| RTY|F10 | C117-C121 (5) | RTY | F10 order-book state at 5 min and longer |
| RTY|F11 | C122-C126 (5) | RTY | F11 own-price-path trend and reversal |
| RTY|F12 | C127-C131 (5) | RTY | F12 expiry and option-hedging days |
| ZL|F01 | C132-C133 (2) | ZL | F01 intraday momentum into the close |
| ZL|F03 | C134-C135 (2) | ZL | F03 USDA and NOPA report drift |
| ZL|F08 | C136-C137 (2) | ZL | F08 session and overnight-to-day handoff |
| ZL|F09 | C138-C139 (2) | ZL | F09 cross-market lead-lag |
| ZL|F10 | C140-C141 (2) | ZL | F10 order-book state at 5 min and longer |
| ZL|F11 | C142-C143 (2) | ZL | F11 own-price-path trend and reversal |
| EQ3|F01 | C144-C165 (4) | EQ3 | F01 intraday momentum into the close |
| EQ3|F04 | C145-C166 (4) | EQ3 | F04 US macro release drift |
| EQ3|F05 | C146-C167 (4) | EQ3 | F05 FOMC post-statement drift |
| EQ3|F08 | C147-C168 (4) | EQ3 | F08 session and overnight-to-day handoff |
| EQ3|F10 | C148-C169 (4) | EQ3 | F10 order-book state at 5 min and longer |
| EQ3|F11 | C149-C170 (4) | EQ3 | F11 own-price-path trend and reversal |
| EQ3|F12 | C150-C171 (4) | EQ3 | F12 expiry and option-hedging days |
| EQ3m|F01 | C172-C179 (2) | EQ3m | F01 intraday momentum into the close |
| EQ3m|F04 | C173-C180 (2) | EQ3m | F04 US macro release drift |
| EQ3m|F05 | C174-C181 (2) | EQ3m | F05 FOMC post-statement drift |
| EQ3m|F08 | C175-C182 (2) | EQ3m | F08 session and overnight-to-day handoff |
| EQ3m|F10 | C176-C183 (2) | EQ3m | F10 order-book state at 5 min and longer |
| EQ3m|F11 | C177-C184 (2) | EQ3m | F11 own-price-path trend and reversal |
| EQ3m|F12 | C178-C185 (2) | EQ3m | F12 expiry and option-hedging days |

## Dossiers

### Dossier YM|F01: product YM, F01 intraday momentum into the close

MYM is YM's micro (1/10 size); MYM's F3 statistics are YM's (OC-1 transfer); MYM settles daily from YM (EQUITY-22, -23). The two are one underlying and never pool members together.

*DOW (Dow Jones Industrial Average)*

- Applies because: Baltussen et al. 2021 define the effect on the cash-session close (EQUITY-49) and report a product row for this underlying (SB-8 YM, SB-9 NQ, SB-10 Russell).
- Participant flow: Gamma hedgers: option market makers short gamma and leveraged-ETF rebalancing trade in the direction of the day's move before the close (Baltussen et al. 2021); late-informed traders (Gao et al. 2018).
- Why predictable: The hedge size is set mechanically by the day's return and is executed near the close, a known time.
- Why an edge could exist at retail size: The flow is non-informational and large against a one-lot; the open issue is size per trade against cost (R1-14: NQ T1 gross 1.25 ticks against 4.08 cost). One contract moves no price; at tens of milliseconds to a second without co-location only effects lasting minutes are reachable (information is priced within 1 to 5 s on ES, NQ, ZN, CL: E.25).
- Mechanism quote: "Hedging short gamma exposure requires trading in the direction of price movements, thereby creating price momentum." (reports/stage_e13_briefs/pages/InfoSource/baltussen_etal_2021_jfe.md:84-85)
- Documented horizon: 30 min: entry at close-30, exit at the cash close (Baltussen et al.; EQUITY-49)
- Timing: entry 12:30 PT (14:30 CT), exit 13:00 PT (15:00 CT cash close); main session 06:30-13:00 PT (cash 09:30-16:00 ET, EQUITY-47/-49)
- Kind: daily; events a year: 252 (one trade a trade date (spec 9.2: 252 trade dates a year)); trades per event: 1
- Absorption under 5 minutes (R2): Not applicable as such: the effect is a 30-minute flow pattern. Contrary evidence is decay and regime change (EQUITY-39, -40, -41), not fast absorption.
- Evidence rows (relation to this product; full rows in the catalog): F01.E01 (asset-class pool (17 equity index futures, incl. YM); full_text); F01.E02 (this underlying: YM product row (SB-8); full_text); F01.E04 (all products (cost statement); full_text); F01.E05 (other venue, other index (SPY; IWM); reused (E.20 full text)); F01.E06 (cash index, other index (S&P 500); reused); F01.E10 (cousin (ES); reused (full text)); F01.E11 (cash S&P 500 (pointer); reused); F01.E12 (index futures (abstract; DJIA per snippet only, EQUITY-41); abstract); F01.E13 (equity, bond and FX futures pool (abstract); abstract); F01.E14 (other product (NQ at MNQ cost; program test); reused (program record)); F01.E15 (pooled program test incl. YM; reused)
- R1 overlap (closing sentences in the R1 catalog):
  - R1-13 (pooled incl. YM (fallback window 2019-05-06..2024-02-29)): E16-H1 settlement-window intraday momentum and H4 next-day reversal, pooled over 27 roots. Reading: closed configuration (LR-R1: a closed configuration stays closed at every venue, the own broker included).
  - R1-03 (MYM traded, YM price path): K1-cp1-01 open-to-first-half-hour momentum port (signal bar 08:59 CT; R1's horizons field: "intraday holds, flat by the exchange-set F (15:08 CT equity/rates)"); research window 2025-04-01..2026-06-12. Reading: closed configuration (LR-R1: a closed configuration stays closed at every venue, the own broker included).
  - R1-14 (other product (NQ)): H6 rest-of-day to last-half-hour momentum, entry 14:30 CT, 2020-06..2024-02. Reading: family closed on another product (family overlap under LR-R1).
  - R1-11 (MYM tested): ML route v2 Gate 0 at h60, h120, hF on 1-minute bar features. Reading: closed configuration (LR-R1: a closed configuration stays closed at every venue, the own broker included).
  - R1-23 (not product-specific): C2 GEX late-session momentum stopped at its power rule. Reading: a stop before any test, not a test (R1 ambiguity list).
- Open questions (R2): No per-product estimate after 2020-05 on any CME candidate; post-2018 equity evidence is regime-dependent (EQUITY-39) or a pointer (EQUITY-40). | No cost-adjusted per-product result; the only net statements are ES (one sentence) and SPY net of spread 2005-2013. | Micro codes, yield futures and mini grains were not in the sample; their price path is the full-size sibling's (settlement-derived), costs differ. | Whether a variant that differs from H6/E16-H1 (other products, conditioning) counts as a 'close variant' under R1 is for the lead and scorer.

Band and horizon: documented horizon inside B (documented [30] min). C001 h_c 30; C002 h_c 30; C003 h_c 30; C004 h_c 30; C005 h_c 30; C006 h_c 30

Cost and power at h_c (ticks of the member's own tick; e80 = SR80 sqrt(T) sigma_hc / sqrt(K)):

| id | venue | band | h_c | member | c_f | sigma_hc | c_f/sigma | p_be emp / norm | p_1 emp / norm | K_year | K_disc | K_test | e80 disc G3+G4 / G3 / test | c_f + e80_test |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C001 | bulenox | 15-30 | 30 | YM | 2.336 | 63.23 | 0.0369 | 0.5257 / 0.5231 | 0.5367 / 0.5331 | 252.0 | 796.0 | 870.0 | 14.60 / 12.80 / 12.24 | 14.58 |
| C002 | tradeify | 15-30 | 30 | YM | 2.652 | 63.23 | 0.0419 | 0.5292 / 0.5263 | 0.5402 / 0.5362 | 252.0 | 796.0 | 870.0 | 14.60 / 12.80 / 12.24 | 14.90 |
| C003 | topstep | 15-30 | 30 | YM | 2.256 | 63.23 | 0.0357 | 0.5248 / 0.5224 | 0.5358 / 0.5323 | 252.0 | 796.0 | 870.0 | 14.60 / 12.80 / 12.24 | 14.50 |
| C004 | mffu | 15-30 | 30 | YM | 2.652 | 63.23 | 0.0419 | 0.5292 / 0.5263 | 0.5402 / 0.5362 | 252.0 | 796.0 | 870.0 | 14.60 / 12.80 / 12.24 | 14.90 |
| C005 | lucid | 15-30 | 30 | YM | 2.652 | 63.23 | 0.0419 | 0.5292 / 0.5263 | 0.5402 / 0.5362 | 252.0 | 796.0 | 870.0 | 14.60 / 12.80 / 12.24 | 14.90 |
| C006 | ibkr | 15-30 | 30 | YM | 2.396 | 63.23 | 0.0379 | 0.5264 / 0.5237 | 0.5374 / 0.5337 | 252.0 | 796.0 | 870.0 | 14.60 / 12.80 / 12.24 | 14.64 |

Prop fit (one contract) and own-broker fit:

| id | venue | member | DLL (USD) / MLL | DLL/(sigma v) | flat-by-close PT, latest start | payout threshold vs sqrt(n/day) sigma v | news events a week | gates | queue-limit c_lim (passive entry / both) | margin, sigma_day |
|---|---|---|---|---|---|---|---|---|---|---|
| C001 | bulenox | YM | none / 2500.0 | 7.91 | 13:59, 12:30 | 0 vs 316.17 (below) | 0.000 | none | 2.556 / 2.776 | - |
| C002 | tradeify | YM | 1250.0 / 2000.0 | 3.95 | 13:45, 12:30 | 150 vs 316.17 (below) | 0.000 | none | 2.872 / 3.092 | - |
| C003 | topstep | YM | none / 2000.0 | 6.33 | 13:10, 12:30 | 150 vs 316.17 (below) | 0.000 | none | - | - |
| C004 | mffu | YM | 1000.0 / 2000.0 | 3.16 | 13:10, 12:30 | 0 vs 316.17 (below) | 0.000 | none | - | - |
| C005 | lucid | YM | 1200.0 / 2000.0 | 3.80 | 13:45, 12:30 | 0 vs 316.17 (below) | 0.000 | none | 2.872 / 3.092 | - |
| C006 | ibkr | YM | none (own account) | - | none, 12:30 | - | 0 | none | not computed | intraday initial USD 12699.91 (overnight 18142.73); sigma_cc 275.49 ticks = USD 1377.45 |

Data needed:

- YM: schema ohlcv-1m (YM price path). Discovery 2020-12-01..2024-02-29 (39 months; bars owned: True); test 2015-10-01..2019-04-30 (43 months; never read, unsealed, not owned: buy); clean test window 106.97 months (never read, unsealed: ['2010-06-06', '2019-05-06']). Cost (estimates): discovery USD 0.00, test USD 4.26, all USD 4.26; basis: estimate: E.12 quote USD 10.50261 for 106 monthly ohlcv-1m chunks 2010-07..2019-04 (reports/stage_e16_windows.json products.YM) = USD 0.0991/month x 43. Quotes to obtain: GLBX.MDP3 ohlcv-1m YM.v.0 2015-10-01..2019-04-30.
- Combination (sums over members; clean window = the shortest member's): discovery USD 0.00, all USD 4.26, clean test window 106.97 months.

### Dossier YM|F04: product YM, F04 US macro release drift

MYM is YM's micro (1/10 size); MYM's F3 statistics are YM's (OC-1 transfer); MYM settles daily from YM (EQUITY-22, -23). The two are one underlying and never pool members together.

*DOW (Dow Jones Industrial Average)*

- Applies because: Scheduled US macro releases: NFP, CPI, PPI, GDP 08:30 ET; ISM 10:00 ET (EQUITY-16).
- Participant flow: Repricing of rate and growth expectations after a surprise; slower cross-asset digestion (copper, silver lags).
- Why predictable: Pre-announced calendar (EQUITY-16).
- Why an edge could exist at retail size: Only in the slower components: ES continuing adjustment 10-30 min (EQUITY-17) and the metals' delayed response (METALS-23); the jump itself is absorbed within seconds to a minute (RATES-19, -20; FX-22). One contract moves no price; at tens of milliseconds to a second without co-location only effects lasting minutes are reachable (information is priced within 1 to 5 s on ES, NQ, ZN, CL: E.25).
- Mechanism quote: none recorded in the R2 file for this family
- Documented horizon: entry 5-10 min after the release, exit 30-60 min (R2-F04); ES continuing adjustment t+10 to t+30 min (EQUITY-17)
- Timing: 08:30 ET releases (NFP, CPI, PPI, GDP) = 05:30 PT, BEFORE the main session (Globex pre-open); 10:00 ET releases (ISM) = 07:00 PT, inside; 09:15 ET (IP) = 06:15 PT, before (not counted: no calendar file); main session 06:30-13:00 PT (cash 09:30-16:00 ET, EQUITY-47/-49)
- Kind: event; events a year: 67.62 (326 releases in 4.821 years = 67.62 a year (reports/stage_e20_briefs/shared/macro_calendars.md section 3 (via EQUITY-16): counts in 2019-05-06..2024-02-29: NFP 57, CPI 58, PPI 58, GDP first and last 38, ISM services 57, ISM manufacturing 58)); trades per event: 1
- Absorption under 5 minutes (R2): Strongest of all families: rates (RATES-19, -20), FX (FX-21, -22), ES order flow (EQUITY-19), crypto (CRYPTO-27, -29), E.25 (1-5 seconds on ES, NQ, ZN, CL). Slower pieces: ES 10-30 min (weak joint test), copper and silver delays (2002-2008).
- Evidence rows (relation to this product; full rows in the catalog): F04.E03 (cousin (ES), 30 announcements, full text; full_text); F04.E01 (cousin (ES) and ZN, after NFP; full_text); F04.E08 (cousin (ES order flow, abstract); abstract)
- R1 overlap (closing sentences in the R1 catalog):
  - R1-01 (cousin (MES; outside the 47-code universe)): MES family E scheduled-macro and calendar windows. Reading: family closed on another product (family overlap under LR-R1).
  - R1-04 (other product (rates)): K2 ISM pre-drift window. Reading: family closed on another product (family overlap under LR-R1).
- Open questions (R2): No post-2015 study shows a mean drift of 5 minutes or more after US macro releases in Treasury, FX or crypto futures (searched, not found: F2_rates, F2_fx, F2_crypto). | Firm news windows (Topstep Tier 1: CPI, NFP, PPI, FOMC; equity minis and GC SI HG blocked, MGC capped per planner pointer) may gate the core trade: FirmRules owns this.

Band and horizon: documented horizon(s) [60] min lie outside B (15-30 min) (documented [20, 30, 60] min). C007 h_c 30; C008 h_c 30; C009 h_c 30; C010 h_c 30; C011 h_c 30; C012 h_c 30

Cost and power at h_c (ticks of the member's own tick; e80 = SR80 sqrt(T) sigma_hc / sqrt(K)):

| id | venue | band | h_c | member | c_f | sigma_hc | c_f/sigma | p_be emp / norm | p_1 emp / norm | K_year | K_disc | K_test | e80 disc G3+G4 / G3 / test | c_f + e80_test |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C007 | bulenox | 15-30 | 30 | YM | 2.336 | 63.23 | 0.0369 | 0.5257 / 0.5231 | 0.5367 / 0.5331 | 67.6 | 213.6 | 233.4 | 28.18 / 24.72 / 23.64 | 25.97 |
| C008 | tradeify | 15-30 | 30 | YM | 2.652 | 63.23 | 0.0419 | 0.5292 / 0.5263 | 0.5402 / 0.5362 | 67.6 | 213.6 | 233.4 | 28.18 / 24.72 / 23.64 | 26.29 |
| C009 | topstep | 15-30 | 30 | YM | 2.256 | 63.23 | 0.0357 | 0.5248 / 0.5224 | 0.5358 / 0.5323 | 67.6 | 213.6 | 233.4 | 28.18 / 24.72 / 23.64 | 25.89 |
| C010 | mffu | 15-30 | 30 | YM | 2.652 | 63.23 | 0.0419 | 0.5292 / 0.5263 | 0.5402 / 0.5362 | 67.6 | 213.6 | 233.4 | 28.18 / 24.72 / 23.64 | 26.29 |
| C011 | lucid | 15-30 | 30 | YM | 2.652 | 63.23 | 0.0419 | 0.5292 / 0.5263 | 0.5402 / 0.5362 | 67.6 | 213.6 | 233.4 | 28.18 / 24.72 / 23.64 | 26.29 |
| C012 | ibkr | 15-30 | 30 | YM | 2.396 | 63.23 | 0.0379 | 0.5264 / 0.5237 | 0.5374 / 0.5337 | 67.6 | 213.6 | 233.4 | 28.18 / 24.72 / 23.64 | 26.03 |

Prop fit (one contract) and own-broker fit:

| id | venue | member | DLL (USD) / MLL | DLL/(sigma v) | flat-by-close PT, latest start | payout threshold vs sqrt(n/day) sigma v | news events a week | gates | queue-limit c_lim (passive entry / both) | margin, sigma_day |
|---|---|---|---|---|---|---|---|---|---|---|
| C007 | bulenox | YM | none / 2500.0 | 7.91 | 13:59, 12:30 | 0 vs 163.77 (below) | 0.000 | none | 2.556 / 2.776 | - |
| C008 | tradeify | YM | 1250.0 / 2000.0 | 3.95 | 13:45, 12:30 | 150 vs 163.77 (below) | 0.000 | none | 2.872 / 3.092 | - |
| C009 | topstep | YM | none / 2000.0 | 6.33 | 13:10, 12:30 | 150 vs 163.77 (below) | 0.688 | none | - | - |
| C010 | mffu | YM | 1000.0 / 2000.0 | 3.16 | 13:10, 12:30 | 0 vs 163.77 (below) | 0.000 | none | - | - |
| C011 | lucid | YM | 1200.0 / 2000.0 | 3.80 | 13:45, 12:30 | 0 vs 163.77 (below) | 0.000 | none | 2.872 / 3.092 | - |
| C012 | ibkr | YM | none (own account) | - | none, 12:30 | - | 0 | none | not computed | intraday initial USD 12699.91 (overnight 18142.73); sigma_cc 275.49 ticks = USD 1377.45 |

Data needed:

- YM: schema ohlcv-1m (YM price path). Discovery 2020-12-01..2024-02-29 (39 months; bars owned: True); test 2015-10-01..2019-04-30 (43 months; never read, unsealed, not owned: buy); clean test window 106.97 months (never read, unsealed: ['2010-06-06', '2019-05-06']). Cost (estimates): discovery USD 0.00, test USD 4.26, all USD 4.26; basis: estimate: E.12 quote USD 10.50261 for 106 monthly ohlcv-1m chunks 2010-07..2019-04 (reports/stage_e16_windows.json products.YM) = USD 0.0991/month x 43. Quotes to obtain: GLBX.MDP3 ohlcv-1m YM.v.0 2015-10-01..2019-04-30. Not priced: release calendar (E.20 frozen calendar covers 2019-05..2024-02 only; no 2010-2019 file for NFP, CPI, PPI, GDP, ISM: macro_calendars.md section 3); consensus forecasts only for a surprise-signed variant (vendor data, not owned, cost unknown).
- Combination (sums over members; clean window = the shortest member's): discovery USD 0.00, all USD 4.26, clean test window 106.97 months.

### Dossier YM|F05: product YM, F05 FOMC post-statement drift

MYM is YM's micro (1/10 size); MYM's F3 statistics are YM's (OC-1 transfer); MYM settles daily from YM (EQUITY-22, -23). The two are one underlying and never pool members together.

*DOW (Dow Jones Industrial Average)*

- Applies because: Scheduled FOMC statements 14:00 ET, eight a year (EQUITY-16; R2-F05).
- Participant flow: Slow repricing of the policy path after the 14:00 ET statement and press conference; portfolio rebalancing over the afternoon.
- Why predictable: Eight scheduled meetings a year (FX-26 for frequency of ECB/RBA; FOMC 8/yr).
- Why an edge could exist at retail size: SR 1188 finds an unconditional, persistent yield decline for about 3 hours after the statement, a horizon a one-lot can reach. One contract moves no price; at tens of milliseconds to a second without co-location only effects lasting minutes are reachable (information is priced within 1 to 5 s on ES, NQ, ZN, CL: E.25).
- Mechanism quote: none recorded in the R2 file for this family
- Documented horizon: after the 14:00 ET statement to the close: FOMC-day last half-hour (15:30-16:00 ET), 75+ min after the statement (EQUITY-20); Treasury yields about 3 h (RATES-23)
- Timing: statement 11:00 PT (14:00 ET), press conference 11:30 PT; last half-hour 12:30-13:00 PT; main session 06:30-13:00 PT (cash 09:30-16:00 ET, EQUITY-47/-49)
- Kind: event; events a year: 8 (eight scheduled FOMC meetings a year (R2-F05 mechanism; frozen calendar 37 statements in 2019-05-06..2024-02-29, macro_calendars.md section 3)); trades per event: 1
- Absorption under 5 minutes (R2): Statement jump fast (E.25 for ZN); gold continues 5-10 min (METALS-25); rates drift persists about 3 h (RATES-23).
- Evidence rows (relation to this product; full rows in the catalog): F05.E02 (other venue (SPY), FOMC release days; reused); F05.E06 (cash S&P 500 and Treasuries: pre-FOMC drift (before the statement); reused / abstract); F05.E01 (other asset class (cash Treasury yields); reused (E.20 full text))
- R1 overlap (closing sentences in the R1 catalog):
  - R1-04 (other product (rates)): K2 post-FOMC member (Tier B, no confirmation). Reading: family closed on another product (family overlap under LR-R1).
  - R1-07 (other product (MGC)): K5-fomc-01, E.22 confirmation null. Reading: family closed on another product (family overlap under LR-R1).
  - R1-01 (cousin (MES)): MES family E scheduled-macro and calendar windows. Reading: family closed on another product (family overlap under LR-R1).
- Open questions (R2): Is SR 1188's 3-hour decline present in ZN/ZF futures after 2015 and net of costs? Not found. | FOMC is a Topstep Tier 1 event (planner pointer): whether rates are outside its window (pointer says 'energies, rates, FX unaffected') is FirmRules' fact.

Band and horizon: documented horizon(s) [120] min lie outside B (15-30 min) (documented [30, 120] min). C013 h_c 30; C014 h_c 30; C015 h_c 30; C016 h_c 30; C017 h_c 30; C018 h_c 30

Cost and power at h_c (ticks of the member's own tick; e80 = SR80 sqrt(T) sigma_hc / sqrt(K)):

| id | venue | band | h_c | member | c_f | sigma_hc | c_f/sigma | p_be emp / norm | p_1 emp / norm | K_year | K_disc | K_test | e80 disc G3+G4 / G3 / test | c_f + e80_test |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C013 | bulenox | 15-30 | 30 | YM | 2.336 | 63.23 | 0.0369 | 0.5257 / 0.5231 | 0.5367 / 0.5331 | 8.0 | 25.3 | 27.6 | 81.93 / 71.86 / 68.72 | 71.05 |
| C014 | tradeify | 15-30 | 30 | YM | 2.652 | 63.23 | 0.0419 | 0.5292 / 0.5263 | 0.5402 / 0.5362 | 8.0 | 25.3 | 27.6 | 81.93 / 71.86 / 68.72 | 71.37 |
| C015 | topstep | 15-30 | 30 | YM | 2.256 | 63.23 | 0.0357 | 0.5248 / 0.5224 | 0.5358 / 0.5323 | 8.0 | 25.3 | 27.6 | 81.93 / 71.86 / 68.72 | 70.97 |
| C016 | mffu | 15-30 | 30 | YM | 2.652 | 63.23 | 0.0419 | 0.5292 / 0.5263 | 0.5402 / 0.5362 | 8.0 | 25.3 | 27.6 | 81.93 / 71.86 / 68.72 | 71.37 |
| C017 | lucid | 15-30 | 30 | YM | 2.652 | 63.23 | 0.0419 | 0.5292 / 0.5263 | 0.5402 / 0.5362 | 8.0 | 25.3 | 27.6 | 81.93 / 71.86 / 68.72 | 71.37 |
| C018 | ibkr | 15-30 | 30 | YM | 2.396 | 63.23 | 0.0379 | 0.5264 / 0.5237 | 0.5374 / 0.5337 | 8.0 | 25.3 | 27.6 | 81.93 / 71.86 / 68.72 | 71.11 |

Prop fit (one contract) and own-broker fit:

| id | venue | member | DLL (USD) / MLL | DLL/(sigma v) | flat-by-close PT, latest start | payout threshold vs sqrt(n/day) sigma v | news events a week | gates | queue-limit c_lim (passive entry / both) | margin, sigma_day |
|---|---|---|---|---|---|---|---|---|---|---|
| C013 | bulenox | YM | none / 2500.0 | 7.91 | 13:59, 12:30 | 0 vs 56.33 (below) | 0.000 | none | 2.556 / 2.776 | - |
| C014 | tradeify | YM | 1250.0 / 2000.0 | 3.95 | 13:45, 12:30 | 150 vs 56.33 (exceeds) | 0.000 | none | 2.872 / 3.092 | - |
| C015 | topstep | YM | none / 2000.0 | 6.33 | 13:10, 12:30 | 150 vs 56.33 (exceeds) | 0.147 | none | - | - |
| C016 | mffu | YM | 1000.0 / 2000.0 | 3.16 | 13:10, 12:30 | 0 vs 56.33 (below) | 0.000 | none | - | - |
| C017 | lucid | YM | 1200.0 / 2000.0 | 3.80 | 13:45, 12:30 | 0 vs 56.33 (below) | 0.000 | none | 2.872 / 3.092 | - |
| C018 | ibkr | YM | none (own account) | - | none, 12:30 | - | 0 | none | not computed | intraday initial USD 12699.91 (overnight 18142.73); sigma_cc 275.49 ticks = USD 1377.45 |

Data needed:

- YM: schema ohlcv-1m (YM price path). Discovery 2020-12-01..2024-02-29 (39 months; bars owned: True); test 2015-10-01..2019-04-30 (43 months; never read, unsealed, not owned: buy); clean test window 106.97 months (never read, unsealed: ['2010-06-06', '2019-05-06']). Cost (estimates): discovery USD 0.00, test USD 4.26, all USD 4.26; basis: estimate: E.12 quote USD 10.50261 for 106 monthly ohlcv-1m chunks 2010-07..2019-04 (reports/stage_e16_windows.json products.YM) = USD 0.0991/month x 43. Quotes to obtain: GLBX.MDP3 ohlcv-1m YM.v.0 2015-10-01..2019-04-30. Not priced: FOMC statement dates and times (calendar files 2010-2024 exist: macro_calendars.md section 3).
- Combination (sums over members; clean window = the shortest member's): discovery USD 0.00, all USD 4.26, clean test window 106.97 months.

### Dossier YM|F08: product YM, F08 session and overnight-to-day handoff

MYM is YM's micro (1/10 size); MYM's F3 statistics are YM's (OC-1 transfer); MYM settles daily from YM (EQUITY-22, -23). The two are one underlying and never pool members together.

*DOW (Dow Jones Industrial Average)*

- Applies because: Fixed session clocks: Globex Sun-Fri 18:00-17:00 ET, cash session 09:30-16:00 ET (EQUITY-47, EQUITY-49); European open 02:00-03:00 ET documented on the ES cousin (EQUITY-50).
- Participant flow: Local-hours hedging and order imbalances carried over from the prior close (Boyarchenko et al.: 2:00-3:00 ET returns linked to prior US-close imbalances); overnight news priced at the reopen.
- Why predictable: Fixed session clocks (Globex pauses: grains 07:45-08:30 CT, GRAINS-14; daily 16:00-17:00 CT halts).
- Why an edge could exist at retail size: Hours-scale holds around a known clock; most documented versions are gross or negative after spreads. One contract moves no price; at tens of milliseconds to a second without co-location only effects lasting minutes are reachable (information is priced within 1 to 5 s on ES, NQ, ZN, CL: E.25).
- Mechanism quote: none recorded in the R2 file for this family
- Documented horizon: European open 02:00-03:00 ET, 60 min (EQUITY-50); the cash-open first half-hour as the predictor of the close (F01.E05)
- Timing: European open 23:00-00:00 PT (prior evening, Globex, outside the main session); cash open 06:30 PT; main session 06:30-13:00 PT (cash 09:30-16:00 ET, EQUITY-47/-49)
- Kind: daily; events a year: 252 (one trade a trade date); trades per event: 1
- Absorption under 5 minutes (R2): Not the issue here; the evidence that exists is either gross, pre-2013, other-venue, or negative after spreads (EQUITY-51) or arbitraged after a venue change (GRAINS-42, GRAINS-17).
- Evidence rows (relation to this product; full rows in the catalog): F08.E03 (cousin (ES), European open 02:00-03:00 ET; full_text); F01.E05 (other venue (SPY): first half-hour predicts the last half-hour (listed under F01; the open-to-close handoff); reused (E.20 full text))
- R1 overlap (closing sentences in the R1 catalog):
  - R1-03 (MYM traded, YM price path): K1-cp3-01 prior-day close-location (entry intent on the 08:30 CT bar; exit by the exchange-set flat F per R1). Reading: closed configuration (LR-R1: a closed configuration stays closed at every venue, the own broker included).
  - R1-13 (pooled incl. YM): E16-H4 next-day reversal of the settlement-window move. Reading: closed configuration (LR-R1: a closed configuration stays closed at every venue, the own broker included).
  - R1-01 (cousin (MES)): families A (calendar and clock windows) and D (gaps), incl. overnight and European-open drift (MES A-H1, A-H3, E-H4). Reading: family closed on another product (family overlap under LR-R1).
- Open questions (R2): No post-2010 futures test of the local-hours currency effect on 6E/6A net of a futures round trip. | Grains 08:30 CT reopen after the 07:45-08:30 pause: untested (planner family 4), and Export Sales lands at 07:30 CT just before the pause (GRAINS-22).

Band and horizon: documented horizon(s) [60] min lie outside B (15-30 min) (documented [30, 60] min). C019 h_c 30; C020 h_c 30; C021 h_c 30; C022 h_c 30; C023 h_c 30; C024 h_c 30

Cost and power at h_c (ticks of the member's own tick; e80 = SR80 sqrt(T) sigma_hc / sqrt(K)):

| id | venue | band | h_c | member | c_f | sigma_hc | c_f/sigma | p_be emp / norm | p_1 emp / norm | K_year | K_disc | K_test | e80 disc G3+G4 / G3 / test | c_f + e80_test |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C019 | bulenox | 15-30 | 30 | YM | 2.336 | 63.23 | 0.0369 | 0.5257 / 0.5231 | 0.5367 / 0.5331 | 252.0 | 796.0 | 870.0 | 14.60 / 12.80 / 12.24 | 14.58 |
| C020 | tradeify | 15-30 | 30 | YM | 2.652 | 63.23 | 0.0419 | 0.5292 / 0.5263 | 0.5402 / 0.5362 | 252.0 | 796.0 | 870.0 | 14.60 / 12.80 / 12.24 | 14.90 |
| C021 | topstep | 15-30 | 30 | YM | 2.256 | 63.23 | 0.0357 | 0.5248 / 0.5224 | 0.5358 / 0.5323 | 252.0 | 796.0 | 870.0 | 14.60 / 12.80 / 12.24 | 14.50 |
| C022 | mffu | 15-30 | 30 | YM | 2.652 | 63.23 | 0.0419 | 0.5292 / 0.5263 | 0.5402 / 0.5362 | 252.0 | 796.0 | 870.0 | 14.60 / 12.80 / 12.24 | 14.90 |
| C023 | lucid | 15-30 | 30 | YM | 2.652 | 63.23 | 0.0419 | 0.5292 / 0.5263 | 0.5402 / 0.5362 | 252.0 | 796.0 | 870.0 | 14.60 / 12.80 / 12.24 | 14.90 |
| C024 | ibkr | 15-30 | 30 | YM | 2.396 | 63.23 | 0.0379 | 0.5264 / 0.5237 | 0.5374 / 0.5337 | 252.0 | 796.0 | 870.0 | 14.60 / 12.80 / 12.24 | 14.64 |

Prop fit (one contract) and own-broker fit:

| id | venue | member | DLL (USD) / MLL | DLL/(sigma v) | flat-by-close PT, latest start | payout threshold vs sqrt(n/day) sigma v | news events a week | gates | queue-limit c_lim (passive entry / both) | margin, sigma_day |
|---|---|---|---|---|---|---|---|---|---|---|
| C019 | bulenox | YM | none / 2500.0 | 7.91 | 13:59, 12:30 | 0 vs 316.17 (below) | 0.000 | none | 2.556 / 2.776 | - |
| C020 | tradeify | YM | 1250.0 / 2000.0 | 3.95 | 13:45, 12:30 | 150 vs 316.17 (below) | 0.000 | none | 2.872 / 3.092 | - |
| C021 | topstep | YM | none / 2000.0 | 6.33 | 13:10, 12:30 | 150 vs 316.17 (below) | 0.000 | none | - | - |
| C022 | mffu | YM | 1000.0 / 2000.0 | 3.16 | 13:10, 12:30 | 0 vs 316.17 (below) | 0.000 | none | - | - |
| C023 | lucid | YM | 1200.0 / 2000.0 | 3.80 | 13:45, 12:30 | 0 vs 316.17 (below) | 0.000 | none | 2.872 / 3.092 | - |
| C024 | ibkr | YM | none (own account) | - | none, 12:30 | - | 0 | none | not computed | intraday initial USD 12699.91 (overnight 18142.73); sigma_cc 275.49 ticks = USD 1377.45 |

Data needed:

- YM: schema ohlcv-1m (YM price path). Discovery 2020-12-01..2024-02-29 (39 months; bars owned: True); test 2015-10-01..2019-04-30 (43 months; never read, unsealed, not owned: buy); clean test window 106.97 months (never read, unsealed: ['2010-06-06', '2019-05-06']). Cost (estimates): discovery USD 0.00, test USD 4.26, all USD 4.26; basis: estimate: E.12 quote USD 10.50261 for 106 monthly ohlcv-1m chunks 2010-07..2019-04 (reports/stage_e16_windows.json products.YM) = USD 0.0991/month x 43. Quotes to obtain: GLBX.MDP3 ohlcv-1m YM.v.0 2015-10-01..2019-04-30.
- Combination (sums over members; clean window = the shortest member's): discovery USD 0.00, all USD 4.26, clean test window 106.97 months.

### Dossier YM|F10: product YM, F10 order-book state at 5 min and longer

MYM is YM's micro (1/10 size); MYM's F3 statistics are YM's (OC-1 transfer); MYM settles daily from YM (EQUITY-22, -23). The two are one underlying and never pool members together.

*DOW (Dow Jones Industrial Average)*

- Applies because: Order-book data exist for purchase: Databento GLBX.MDP3 MBO from 2017-05-21, MBP-10 before (F2_data_access databento_dataset); the code's MBO start is in the data plan.
- Participant flow: Large orders worked over time (sign persistence) and liquidity shocks followed by refill.
- Why predictable: Imbalance and sign persistence are autocorrelated.
- Why an edge could exist at retail size: Weak: forward predictability decays to insignificance by 5-30 minutes and sign persistence is offset by asymmetric liquidity (E.32 M1). One contract moves no price; at tens of milliseconds to a second without co-location only effects lasting minutes are reachable (information is priced within 1 to 5 s on ES, NQ, ZN, CL: E.25).
- Mechanism quote: none recorded in the R2 file for this family
- Documented horizon: 5-30 min forward (R2-F10); forward predictability insignificant by 5-30 min (F10.E01)
- Timing: any time in the main session; main session 06:30-13:00 PT (cash 09:30-16:00 ET, EQUITY-47/-49)
- Kind: continuous; events a year: - (continuous: n_cap(h_c) a day); trades per event: -
- Absorption under 5 minutes (R2): Central: E.32 M1 (contemporaneous far stronger than forward), Kolm et al. (seconds), E.25 (1-5 seconds on ES, NQ, ZN, CL).
- Evidence rows (relation to this product; full rows in the catalog): F10.E01 (other asset class (NYSE stocks); full_text (E.32 M1)); F10.E02 (equities (abstract); abstract); F10.E06 (cousin (ES): net gamma conditions order-flow reversals; reused (full text)); F10.E07 (other product (ZM), program test; reused); F10.E08 (excluded sub-5-minute items (NQ among them); abstract/reused)
- R1 overlap (closing sentences in the R1 catalog):
  - R1-21 (other product (ZM)): S3 ZM order flow and book state at 5-60 min. Reading: E.33c family closed on ZM; on this product family overlap (LR-R1).
  - R1-20 (execution line (ZM measured)): passive spread capture at the touch, one lot. Reading: execution line: passive spread capture closed (V50); limit orders stay allowed as execution of a signal.
  - R1-11 (MYM tested): ML on 1-minute bar features (no book data). Reading: closed configuration (LR-R1: a closed configuration stays closed at every venue, the own broker included).
- Open questions (R2): No CME-product study of forward order-flow predictability at 5 minutes or more found outside ZM's own null. | Drift-burst reversal after removing the look-ahead: untested.

Band and horizon: documented horizon(s) [5] min lie outside B (15-30 min) (documented [5, 15, 30] min). C025 h_c 30; C026 h_c 30; C027 h_c 30; C028 h_c 30; C029 h_c 30; C030 h_c 30

Cost and power at h_c (ticks of the member's own tick; e80 = SR80 sqrt(T) sigma_hc / sqrt(K)):

| id | venue | band | h_c | member | c_f | sigma_hc | c_f/sigma | p_be emp / norm | p_1 emp / norm | K_year | K_disc | K_test | e80 disc G3+G4 / G3 / test | c_f + e80_test |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C025 | bulenox | 15-30 | 30 | YM | 2.336 | 63.23 | 0.0369 | 0.5257 / 0.5231 | 0.5367 / 0.5331 | 3276.0 | 10348.0 | 11310.0 | 4.05 / 3.55 / 3.40 | 5.73 |
| C026 | tradeify | 15-30 | 30 | YM | 2.652 | 63.23 | 0.0419 | 0.5292 / 0.5263 | 0.5402 / 0.5362 | 3276.0 | 10348.0 | 11310.0 | 4.05 / 3.55 / 3.40 | 6.05 |
| C027 | topstep | 15-30 | 30 | YM | 2.256 | 63.23 | 0.0357 | 0.5248 / 0.5224 | 0.5358 / 0.5323 | 3276.0 | 10348.0 | 11310.0 | 4.05 / 3.55 / 3.40 | 5.65 |
| C028 | mffu | 15-30 | 30 | YM | 2.652 | 63.23 | 0.0419 | 0.5292 / 0.5263 | 0.5402 / 0.5362 | 3276.0 | 10348.0 | 11310.0 | 4.05 / 3.55 / 3.40 | 6.05 |
| C029 | lucid | 15-30 | 30 | YM | 2.652 | 63.23 | 0.0419 | 0.5292 / 0.5263 | 0.5402 / 0.5362 | 3276.0 | 10348.0 | 11310.0 | 4.05 / 3.55 / 3.40 | 6.05 |
| C030 | ibkr | 15-30 | 30 | YM | 2.396 | 63.23 | 0.0379 | 0.5264 / 0.5237 | 0.5374 / 0.5337 | 3276.0 | 10348.0 | 11310.0 | 4.05 / 3.55 / 3.40 | 5.79 |

Prop fit (one contract) and own-broker fit:

| id | venue | member | DLL (USD) / MLL | DLL/(sigma v) | flat-by-close PT, latest start | payout threshold vs sqrt(n/day) sigma v | news events a week | gates | queue-limit c_lim (passive entry / both) | margin, sigma_day |
|---|---|---|---|---|---|---|---|---|---|---|
| C025 | bulenox | YM | none / 2500.0 | 7.91 | 13:59, 12:30 | 0 vs 1139.96 (below) | 0.000 | none | 2.556 / 2.776 | - |
| C026 | tradeify | YM | 1250.0 / 2000.0 | 3.95 | 13:45, 12:30 | 150 vs 1139.96 (below) | 0.000 | none | 2.872 / 3.092 | - |
| C027 | topstep | YM | none / 2000.0 | 6.33 | 13:10, 12:30 | 150 vs 1139.96 (below) | 0.835 | none | - | - |
| C028 | mffu | YM | 1000.0 / 2000.0 | 3.16 | 13:10, 12:30 | 0 vs 1139.96 (below) | 0.000 | none | - | - |
| C029 | lucid | YM | 1200.0 / 2000.0 | 3.80 | 13:45, 12:30 | 0 vs 1139.96 (below) | 0.000 | none | 2.872 / 3.092 | - |
| C030 | ibkr | YM | none (own account) | - | none, 12:30 | - | 0 | none | not computed | intraday initial USD 12699.91 (overnight 18142.73); sigma_cc 275.49 ticks = USD 1377.45 |

Data needed:

- YM: schema mbo (YM; MBO from 2017-05-21). Discovery 2020-12-01..2024-02-29 (39 months; bars owned: True); test 2015-10-01..2019-04-30 (43 months; never read, unsealed, not owned: buy); clean test window 106.97 months (never read, unsealed: ['2010-06-06', '2019-05-06']). Cost (estimates): discovery USD 227.57, test USD 250.91, all USD 478.48; basis: census estimate k = USD 5.8351/month (F2_data_access codes.YM.k_usd_month, scaled from mbp-1 (estimate)) x months. Quotes to obtain: GLBX.MDP3 mbo YM.v.0 2020-12-01..2024-02-29; GLBX.MDP3 mbo YM.v.0 2015-10-01..2019-04-30 (MBP-10 before 2017-05-21). Not priced: MBP-10 is the highest granularity before 2017-05-21 (F2_data_access databento_dataset).
- Combination (sums over members; clean window = the shortest member's): discovery USD 227.57, all USD 478.48, clean test window 106.97 months.

### Dossier YM|F11: product YM, F11 own-price-path trend and reversal

MYM is YM's micro (1/10 size); MYM's F3 statistics are YM's (OC-1 transfer); MYM settles daily from YM (EQUITY-22, -23). The two are one underlying and never pool members together.

*DOW (Dow Jones Industrial Average)*

- Applies because: R2-F11 applies to any code (own price path on 1-minute bars).
- Participant flow: Trend followers and stop cascades (trend); liquidity-provider inventory correction (reversion).
- Why predictable: Price-path autocorrelation by horizon (reversion 2-16 min, weak trend at 1 h or more).
- Why an edge could exist at retail size: Generic and crowded; the published sizes are tiny (out-of-sample R2 under 1 bp). One contract moves no price; at tens of milliseconds to a second without co-location only effects lasting minutes are reachable (information is priced within 1 to 5 s on ES, NQ, ZN, CL: E.25).
- Mechanism quote: none recorded in the R2 file for this family
- Documented horizon: reversion 2-16 min; weak trend at 1 h or more (F11.E01)
- Timing: any time in the main session; main session 06:30-13:00 PT (cash 09:30-16:00 ET, EQUITY-47/-49)
- Kind: continuous; events a year: - (continuous: n_cap(h_c) a day); trades per event: -
- Absorption under 5 minutes (R2): Short reversion is at 2-16 min and tiny (CRUDE-40); Brent inefficiency vanishes past 10 min (CRUDE-54).
- Evidence rows (relation to this product; full rows in the catalog): F11.E01 (futures pool (16-24 futures; equity-index membership not recorded); full_text); F11.E09 (other venue (SPY), noise-area momentum; reused); F11.E10 (other underlying (MNQ 5-min, NQ 15-min), preprints; reused / full_text)
- R1 overlap (closing sentences in the R1 catalog):
  - R1-03 (MYM traded, YM price path): K1-cp2-01 opening-range breakout (first qualifying bar in [08:45, 15:00) CT; exit by the exchange-set flat F per R1). Reading: closed configuration (LR-R1: a closed configuration stays closed at every venue, the own broker included).
  - R1-01 (cousin (MES)): families B (opening range, breakout), C (reversal, fade), G (price-path statistics), H (NR4/NR7 ORB). Reading: family closed on another product (family overlap under LR-R1).
  - R1-11 (MYM tested): Gate 0 ML over 64 bar features at h60, h120, hF. Reading: closed configuration (LR-R1: a closed configuration stays closed at every venue, the own broker included).
  - R1-21 (other product (ZM)): S4 ZM own price path at 5-60 min. Reading: E.33c family closed on ZM; on this product family overlap (LR-R1).
- Open questions (R2): Every generic price-path family has been screened by the program on 1-minute bars; a new one would be a close variant unless the product or mechanism differs (scorer's call).

Band and horizon: documented horizon(s) [5, 60] min lie outside B (15-30 min) (documented [5, 15, 60] min). C031 h_c 30 (h_c not a documented horizon); C032 h_c 30 (h_c not a documented horizon); C033 h_c 30 (h_c not a documented horizon); C034 h_c 30 (h_c not a documented horizon); C035 h_c 30 (h_c not a documented horizon); C036 h_c 30 (h_c not a documented horizon)

Cost and power at h_c (ticks of the member's own tick; e80 = SR80 sqrt(T) sigma_hc / sqrt(K)):

| id | venue | band | h_c | member | c_f | sigma_hc | c_f/sigma | p_be emp / norm | p_1 emp / norm | K_year | K_disc | K_test | e80 disc G3+G4 / G3 / test | c_f + e80_test |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C031 | bulenox | 15-30 | 30 | YM | 2.336 | 63.23 | 0.0369 | 0.5257 / 0.5231 | 0.5367 / 0.5331 | 3276.0 | 10348.0 | 11310.0 | 4.05 / 3.55 / 3.40 | 5.73 |
| C032 | tradeify | 15-30 | 30 | YM | 2.652 | 63.23 | 0.0419 | 0.5292 / 0.5263 | 0.5402 / 0.5362 | 3276.0 | 10348.0 | 11310.0 | 4.05 / 3.55 / 3.40 | 6.05 |
| C033 | topstep | 15-30 | 30 | YM | 2.256 | 63.23 | 0.0357 | 0.5248 / 0.5224 | 0.5358 / 0.5323 | 3276.0 | 10348.0 | 11310.0 | 4.05 / 3.55 / 3.40 | 5.65 |
| C034 | mffu | 15-30 | 30 | YM | 2.652 | 63.23 | 0.0419 | 0.5292 / 0.5263 | 0.5402 / 0.5362 | 3276.0 | 10348.0 | 11310.0 | 4.05 / 3.55 / 3.40 | 6.05 |
| C035 | lucid | 15-30 | 30 | YM | 2.652 | 63.23 | 0.0419 | 0.5292 / 0.5263 | 0.5402 / 0.5362 | 3276.0 | 10348.0 | 11310.0 | 4.05 / 3.55 / 3.40 | 6.05 |
| C036 | ibkr | 15-30 | 30 | YM | 2.396 | 63.23 | 0.0379 | 0.5264 / 0.5237 | 0.5374 / 0.5337 | 3276.0 | 10348.0 | 11310.0 | 4.05 / 3.55 / 3.40 | 5.79 |

Prop fit (one contract) and own-broker fit:

| id | venue | member | DLL (USD) / MLL | DLL/(sigma v) | flat-by-close PT, latest start | payout threshold vs sqrt(n/day) sigma v | news events a week | gates | queue-limit c_lim (passive entry / both) | margin, sigma_day |
|---|---|---|---|---|---|---|---|---|---|---|
| C031 | bulenox | YM | none / 2500.0 | 7.91 | 13:59, 12:30 | 0 vs 1139.96 (below) | 0.000 | none | 2.556 / 2.776 | - |
| C032 | tradeify | YM | 1250.0 / 2000.0 | 3.95 | 13:45, 12:30 | 150 vs 1139.96 (below) | 0.000 | none | 2.872 / 3.092 | - |
| C033 | topstep | YM | none / 2000.0 | 6.33 | 13:10, 12:30 | 150 vs 1139.96 (below) | 0.835 | none | - | - |
| C034 | mffu | YM | 1000.0 / 2000.0 | 3.16 | 13:10, 12:30 | 0 vs 1139.96 (below) | 0.000 | none | - | - |
| C035 | lucid | YM | 1200.0 / 2000.0 | 3.80 | 13:45, 12:30 | 0 vs 1139.96 (below) | 0.000 | none | 2.872 / 3.092 | - |
| C036 | ibkr | YM | none (own account) | - | none, 12:30 | - | 0 | none | not computed | intraday initial USD 12699.91 (overnight 18142.73); sigma_cc 275.49 ticks = USD 1377.45 |

Data needed:

- YM: schema ohlcv-1m (YM price path). Discovery 2020-12-01..2024-02-29 (39 months; bars owned: True); test 2015-10-01..2019-04-30 (43 months; never read, unsealed, not owned: buy); clean test window 106.97 months (never read, unsealed: ['2010-06-06', '2019-05-06']). Cost (estimates): discovery USD 0.00, test USD 4.26, all USD 4.26; basis: estimate: E.12 quote USD 10.50261 for 106 monthly ohlcv-1m chunks 2010-07..2019-04 (reports/stage_e16_windows.json products.YM) = USD 0.0991/month x 43. Quotes to obtain: GLBX.MDP3 ohlcv-1m YM.v.0 2015-10-01..2019-04-30.
- Combination (sums over members; clean window = the shortest member's): discovery USD 0.00, all USD 4.26, clean test window 106.97 months.

### Dossier YM|F12: product YM, F12 expiry and option-hedging days

MYM is YM's micro (1/10 size); MYM's F3 statistics are YM's (OC-1 transfer); MYM settles daily from YM (EQUITY-22, -23). The two are one underlying and never pool members together.

*DOW (Dow Jones Industrial Average)*

- Applies because: Monthly option expiries (3rd Friday) on the index; R2-F12 lists the equity codes (12 monthly expiries a year, 4 quarterly).
- Participant flow: Option market makers' delta hedging around expiry and their aggregate gamma; leveraged ETF rebalancing.
- Why predictable: Expiry calendars are fixed; dealer gamma is estimable from open interest (GEX).
- Why an edge could exist at retail size: Non-informational flow at a known date; events are few (monthly). One contract moves no price; at tens of milliseconds to a second without co-location only effects lasting minutes are reachable (information is priced within 1 to 5 s on ES, NQ, ZN, CL: E.25).
- Mechanism quote: none recorded in the R2 file for this family
- Documented horizon: expiry day into the close; 10-60 min conditioned on gamma (R2-F12)
- Timing: 3rd Friday of each month, into the 13:00 PT close; main session 06:30-13:00 PT (cash 09:30-16:00 ET, EQUITY-47/-49)
- Kind: event; events a year: 12 (12 monthly expiries a year, 4 quarterly (R2-F12 data needs)); trades per event: 1
- Absorption under 5 minutes (R2): Not applicable (calendar flow).
- Evidence rows (relation to this product; full rows in the catalog): F12.E01 (cousin (ES; V45 exception, untested); reused (E.25)); F12.E02 (other venue (US stocks and ETFs); full_text); F12.E03 (cousin (ES); reused)
- R1 overlap (closing sentences in the R1 catalog):
  - R1-14 (other product (NQ)): H6 T3: momentum into the close conditioned on negative prior-day GEX. Reading: family closed on another product (family overlap under LR-R1).
  - R1-23 (not product-specific): C2 GEX late-session momentum stopped at its power rule. Reading: a stop before any test, not a test (R1 ambiguity list).
  - R1-19 (cousin (ES; outside the universe)): V45 lists the ES 3rd-Friday reversal as an exception (never tested). Reading: evidence finding (R1-19), not a ban on new families (LR-R1).
- Open questions (R2): The 3rd-Friday reversal is published for ES only; no evidence on NQ, RTY or YM codes. | GEX data source and cost: not established here (DataAccess).

Band and horizon: documented horizon(s) [10, 60] min lie outside B (15-30 min) (documented [10, 30, 60] min). C037 h_c 30; C038 h_c 30; C039 h_c 30; C040 h_c 30; C041 h_c 30; C042 h_c 30

Cost and power at h_c (ticks of the member's own tick; e80 = SR80 sqrt(T) sigma_hc / sqrt(K)):

| id | venue | band | h_c | member | c_f | sigma_hc | c_f/sigma | p_be emp / norm | p_1 emp / norm | K_year | K_disc | K_test | e80 disc G3+G4 / G3 / test | c_f + e80_test |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C037 | bulenox | 15-30 | 30 | YM | 2.336 | 63.23 | 0.0369 | 0.5257 / 0.5231 | 0.5367 / 0.5331 | 12.0 | 37.9 | 41.4 | 66.89 / 58.68 / 56.11 | 58.44 |
| C038 | tradeify | 15-30 | 30 | YM | 2.652 | 63.23 | 0.0419 | 0.5292 / 0.5263 | 0.5402 / 0.5362 | 12.0 | 37.9 | 41.4 | 66.89 / 58.68 / 56.11 | 58.76 |
| C039 | topstep | 15-30 | 30 | YM | 2.256 | 63.23 | 0.0357 | 0.5248 / 0.5224 | 0.5358 / 0.5323 | 12.0 | 37.9 | 41.4 | 66.89 / 58.68 / 56.11 | 58.36 |
| C040 | mffu | 15-30 | 30 | YM | 2.652 | 63.23 | 0.0419 | 0.5292 / 0.5263 | 0.5402 / 0.5362 | 12.0 | 37.9 | 41.4 | 66.89 / 58.68 / 56.11 | 58.76 |
| C041 | lucid | 15-30 | 30 | YM | 2.652 | 63.23 | 0.0419 | 0.5292 / 0.5263 | 0.5402 / 0.5362 | 12.0 | 37.9 | 41.4 | 66.89 / 58.68 / 56.11 | 58.76 |
| C042 | ibkr | 15-30 | 30 | YM | 2.396 | 63.23 | 0.0379 | 0.5264 / 0.5237 | 0.5374 / 0.5337 | 12.0 | 37.9 | 41.4 | 66.89 / 58.68 / 56.11 | 58.50 |

Prop fit (one contract) and own-broker fit:

| id | venue | member | DLL (USD) / MLL | DLL/(sigma v) | flat-by-close PT, latest start | payout threshold vs sqrt(n/day) sigma v | news events a week | gates | queue-limit c_lim (passive entry / both) | margin, sigma_day |
|---|---|---|---|---|---|---|---|---|---|---|
| C037 | bulenox | YM | none / 2500.0 | 7.91 | 13:59, 12:30 | 0 vs 68.99 (below) | 0.000 | none | 2.556 / 2.776 | - |
| C038 | tradeify | YM | 1250.0 / 2000.0 | 3.95 | 13:45, 12:30 | 150 vs 68.99 (exceeds) | 0.000 | none | 2.872 / 3.092 | - |
| C039 | topstep | YM | none / 2000.0 | 6.33 | 13:10, 12:30 | 150 vs 68.99 (exceeds) | 0.000 | none | - | - |
| C040 | mffu | YM | 1000.0 / 2000.0 | 3.16 | 13:10, 12:30 | 0 vs 68.99 (below) | 0.000 | none | - | - |
| C041 | lucid | YM | 1200.0 / 2000.0 | 3.80 | 13:45, 12:30 | 0 vs 68.99 (below) | 0.000 | none | 2.872 / 3.092 | - |
| C042 | ibkr | YM | none (own account) | - | none, 12:30 | - | 0 | none | not computed | intraday initial USD 12699.91 (overnight 18142.73); sigma_cc 275.49 ticks = USD 1377.45 |

Data needed:

- YM: schema ohlcv-1m (YM price path). Discovery 2020-12-01..2024-02-29 (39 months; bars owned: True); test 2015-10-01..2019-04-30 (43 months; never read, unsealed, not owned: buy); clean test window 106.97 months (never read, unsealed: ['2010-06-06', '2019-05-06']). Cost (estimates): discovery USD 0.00, test USD 4.26, all USD 4.26; basis: estimate: E.12 quote USD 10.50261 for 106 monthly ohlcv-1m chunks 2010-07..2019-04 (reports/stage_e16_windows.json products.YM) = USD 0.0991/month x 43. Quotes to obtain: GLBX.MDP3 ohlcv-1m YM.v.0 2015-10-01..2019-04-30. Not priced: option open interest by strike for a gamma-conditioned variant (GEX; vendor data, cost unknown; R1-14 used GEX rows 2020-05-29..2024-02-28); the 3rd-Friday variant needs bars and the expiry calendar only.
- Combination (sums over members; clean window = the shortest member's): discovery USD 0.00, all USD 4.26, clean test window 106.97 months.

### Dossier MYM|F01: product MYM, F01 intraday momentum into the close

MYM is YM's micro (1/10 size); MYM's F3 statistics are YM's (OC-1 transfer); MYM settles daily from YM (EQUITY-22, -23). The two are one underlying and never pool members together.

*DOW (Dow Jones Industrial Average)*: mechanism, participant flow, horizon, evidence rows and R1 overlap exactly as in dossier YM|F01 (same underlying, same family).

Band and horizon: documented horizon inside B (documented [30] min). C043 h_c 30; C044 h_c 60 (h_c not a documented horizon)

Cost and power at h_c (ticks of the member's own tick; e80 = SR80 sqrt(T) sigma_hc / sqrt(K)):

| id | venue | band | h_c | member | c_f | sigma_hc | c_f/sigma | p_be emp / norm | p_1 emp / norm | K_year | K_disc | K_test | e80 disc G3+G4 / G3 / test | c_f + e80_test |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C043 | mffu | 30-60 | 30 | MYM | 5.300 | 63.23 | 0.0838 | 0.5583 / 0.5525 | 0.5694 / 0.5624 | 252.0 | 796.0 | 870.0 | 14.60 / 12.80 / 12.24 | 17.54 |
| C044 | ibkr | 30-120 | 60 | MYM | 6.340 | 88.56 | 0.0716 | 0.5491 / 0.5449 | 0.5569 / 0.5519 | 252.0 | 796.0 | 870.0 | 20.45 / 17.93 / 17.15 | 23.49 |

Prop fit (one contract) and own-broker fit:

| id | venue | member | DLL (USD) / MLL | DLL/(sigma v) | flat-by-close PT, latest start | payout threshold vs sqrt(n/day) sigma v | news events a week | gates | queue-limit c_lim (passive entry / both) | margin, sigma_day |
|---|---|---|---|---|---|---|---|---|---|---|
| C043 | mffu | MYM | 1000.0 / 2000.0 | 31.63 | 13:10, 12:30 | 0 vs 31.62 (below) | 0.000 | none | - | - |
| C044 | ibkr | MYM | none (own account) | - | none, 12:00 | - | 0 | none | not computed | intraday initial USD 1269.99 (overnight 1814.27); sigma_cc 275.49 ticks = USD 137.74 |

Data needed:

- MYM: schema ohlcv-1m (YM price path). Discovery 2020-12-01..2024-02-29 (39 months; bars owned: True); test 2015-10-01..2019-04-30 (43 months; never read, unsealed, not owned: buy); clean test window 106.97 months (never read, unsealed: ['2010-06-06', '2019-05-06']). Cost (estimates): discovery USD 0.00, test USD 4.26, all USD 4.26; basis: estimate: E.12 quote USD 10.50261 for 106 monthly ohlcv-1m chunks 2010-07..2019-04 (reports/stage_e16_windows.json products.YM) = USD 0.0991/month x 43. Quotes to obtain: GLBX.MDP3 ohlcv-1m YM.v.0 2015-10-01..2019-04-30.
- Combination (sums over members; clean window = the shortest member's): discovery USD 0.00, all USD 4.26, clean test window 106.97 months.

### Dossier MYM|F04: product MYM, F04 US macro release drift

MYM is YM's micro (1/10 size); MYM's F3 statistics are YM's (OC-1 transfer); MYM settles daily from YM (EQUITY-22, -23). The two are one underlying and never pool members together.

*DOW (Dow Jones Industrial Average)*: mechanism, participant flow, horizon, evidence rows and R1 overlap exactly as in dossier YM|F04 (same underlying, same family).

Band and horizon: documented horizon(s) [20] min lie outside B (30-60 min) (documented [20, 30, 60] min). C045 h_c 30; C046 h_c 60

Cost and power at h_c (ticks of the member's own tick; e80 = SR80 sqrt(T) sigma_hc / sqrt(K)):

| id | venue | band | h_c | member | c_f | sigma_hc | c_f/sigma | p_be emp / norm | p_1 emp / norm | K_year | K_disc | K_test | e80 disc G3+G4 / G3 / test | c_f + e80_test |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C045 | mffu | 30-60 | 30 | MYM | 5.300 | 63.23 | 0.0838 | 0.5583 / 0.5525 | 0.5694 / 0.5624 | 67.6 | 213.6 | 233.4 | 28.18 / 24.72 / 23.64 | 28.94 |
| C046 | ibkr | 30-120 | 60 | MYM | 6.340 | 88.56 | 0.0716 | 0.5491 / 0.5449 | 0.5569 / 0.5519 | 67.6 | 213.6 | 233.4 | 39.47 / 34.62 / 33.10 | 39.44 |

Prop fit (one contract) and own-broker fit:

| id | venue | member | DLL (USD) / MLL | DLL/(sigma v) | flat-by-close PT, latest start | payout threshold vs sqrt(n/day) sigma v | news events a week | gates | queue-limit c_lim (passive entry / both) | margin, sigma_day |
|---|---|---|---|---|---|---|---|---|---|---|
| C045 | mffu | MYM | 1000.0 / 2000.0 | 31.63 | 13:10, 12:30 | 0 vs 16.38 (below) | 0.000 | none | - | - |
| C046 | ibkr | MYM | none (own account) | - | none, 12:00 | - | 0 | none | not computed | intraday initial USD 1269.99 (overnight 1814.27); sigma_cc 275.49 ticks = USD 137.74 |

Data needed:

- MYM: schema ohlcv-1m (YM price path). Discovery 2020-12-01..2024-02-29 (39 months; bars owned: True); test 2015-10-01..2019-04-30 (43 months; never read, unsealed, not owned: buy); clean test window 106.97 months (never read, unsealed: ['2010-06-06', '2019-05-06']). Cost (estimates): discovery USD 0.00, test USD 4.26, all USD 4.26; basis: estimate: E.12 quote USD 10.50261 for 106 monthly ohlcv-1m chunks 2010-07..2019-04 (reports/stage_e16_windows.json products.YM) = USD 0.0991/month x 43. Quotes to obtain: GLBX.MDP3 ohlcv-1m YM.v.0 2015-10-01..2019-04-30. Not priced: release calendar (E.20 frozen calendar covers 2019-05..2024-02 only; no 2010-2019 file for NFP, CPI, PPI, GDP, ISM: macro_calendars.md section 3); consensus forecasts only for a surprise-signed variant (vendor data, not owned, cost unknown).
- Combination (sums over members; clean window = the shortest member's): discovery USD 0.00, all USD 4.26, clean test window 106.97 months.

### Dossier MYM|F05: product MYM, F05 FOMC post-statement drift

MYM is YM's micro (1/10 size); MYM's F3 statistics are YM's (OC-1 transfer); MYM settles daily from YM (EQUITY-22, -23). The two are one underlying and never pool members together.

*DOW (Dow Jones Industrial Average)*: mechanism, participant flow, horizon, evidence rows and R1 overlap exactly as in dossier YM|F05 (same underlying, same family).

Band and horizon: documented horizon(s) [120] min lie outside B (30-60 min) (documented [30, 120] min). C047 h_c 30; C048 h_c 60 (h_c not a documented horizon)

Cost and power at h_c (ticks of the member's own tick; e80 = SR80 sqrt(T) sigma_hc / sqrt(K)):

| id | venue | band | h_c | member | c_f | sigma_hc | c_f/sigma | p_be emp / norm | p_1 emp / norm | K_year | K_disc | K_test | e80 disc G3+G4 / G3 / test | c_f + e80_test |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C047 | mffu | 30-60 | 30 | MYM | 5.300 | 63.23 | 0.0838 | 0.5583 / 0.5525 | 0.5694 / 0.5624 | 8.0 | 25.3 | 27.6 | 81.93 / 71.86 / 68.72 | 74.02 |
| C048 | ibkr | 30-120 | 60 | MYM | 6.340 | 88.56 | 0.0716 | 0.5491 / 0.5449 | 0.5569 / 0.5519 | 8.0 | 25.3 | 27.6 | 114.75 / 100.65 / 96.24 | 102.58 |

Prop fit (one contract) and own-broker fit:

| id | venue | member | DLL (USD) / MLL | DLL/(sigma v) | flat-by-close PT, latest start | payout threshold vs sqrt(n/day) sigma v | news events a week | gates | queue-limit c_lim (passive entry / both) | margin, sigma_day |
|---|---|---|---|---|---|---|---|---|---|---|
| C047 | mffu | MYM | 1000.0 / 2000.0 | 31.63 | 13:10, 12:30 | 0 vs 5.63 (below) | 0.000 | none | - | - |
| C048 | ibkr | MYM | none (own account) | - | none, 12:00 | - | 0 | none | not computed | intraday initial USD 1269.99 (overnight 1814.27); sigma_cc 275.49 ticks = USD 137.74 |

Data needed:

- MYM: schema ohlcv-1m (YM price path). Discovery 2020-12-01..2024-02-29 (39 months; bars owned: True); test 2015-10-01..2019-04-30 (43 months; never read, unsealed, not owned: buy); clean test window 106.97 months (never read, unsealed: ['2010-06-06', '2019-05-06']). Cost (estimates): discovery USD 0.00, test USD 4.26, all USD 4.26; basis: estimate: E.12 quote USD 10.50261 for 106 monthly ohlcv-1m chunks 2010-07..2019-04 (reports/stage_e16_windows.json products.YM) = USD 0.0991/month x 43. Quotes to obtain: GLBX.MDP3 ohlcv-1m YM.v.0 2015-10-01..2019-04-30. Not priced: FOMC statement dates and times (calendar files 2010-2024 exist: macro_calendars.md section 3).
- Combination (sums over members; clean window = the shortest member's): discovery USD 0.00, all USD 4.26, clean test window 106.97 months.

### Dossier MYM|F08: product MYM, F08 session and overnight-to-day handoff

MYM is YM's micro (1/10 size); MYM's F3 statistics are YM's (OC-1 transfer); MYM settles daily from YM (EQUITY-22, -23). The two are one underlying and never pool members together.

*DOW (Dow Jones Industrial Average)*: mechanism, participant flow, horizon, evidence rows and R1 overlap exactly as in dossier YM|F08 (same underlying, same family).

Band and horizon: documented horizon inside B (documented [30, 60] min). C049 h_c 30; C050 h_c 60

Cost and power at h_c (ticks of the member's own tick; e80 = SR80 sqrt(T) sigma_hc / sqrt(K)):

| id | venue | band | h_c | member | c_f | sigma_hc | c_f/sigma | p_be emp / norm | p_1 emp / norm | K_year | K_disc | K_test | e80 disc G3+G4 / G3 / test | c_f + e80_test |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C049 | mffu | 30-60 | 30 | MYM | 5.300 | 63.23 | 0.0838 | 0.5583 / 0.5525 | 0.5694 / 0.5624 | 252.0 | 796.0 | 870.0 | 14.60 / 12.80 / 12.24 | 17.54 |
| C050 | ibkr | 30-120 | 60 | MYM | 6.340 | 88.56 | 0.0716 | 0.5491 / 0.5449 | 0.5569 / 0.5519 | 252.0 | 796.0 | 870.0 | 20.45 / 17.93 / 17.15 | 23.49 |

Prop fit (one contract) and own-broker fit:

| id | venue | member | DLL (USD) / MLL | DLL/(sigma v) | flat-by-close PT, latest start | payout threshold vs sqrt(n/day) sigma v | news events a week | gates | queue-limit c_lim (passive entry / both) | margin, sigma_day |
|---|---|---|---|---|---|---|---|---|---|---|
| C049 | mffu | MYM | 1000.0 / 2000.0 | 31.63 | 13:10, 12:30 | 0 vs 31.62 (below) | 0.000 | none | - | - |
| C050 | ibkr | MYM | none (own account) | - | none, 12:00 | - | 0 | none | not computed | intraday initial USD 1269.99 (overnight 1814.27); sigma_cc 275.49 ticks = USD 137.74 |

Data needed:

- MYM: schema ohlcv-1m (YM price path). Discovery 2020-12-01..2024-02-29 (39 months; bars owned: True); test 2015-10-01..2019-04-30 (43 months; never read, unsealed, not owned: buy); clean test window 106.97 months (never read, unsealed: ['2010-06-06', '2019-05-06']). Cost (estimates): discovery USD 0.00, test USD 4.26, all USD 4.26; basis: estimate: E.12 quote USD 10.50261 for 106 monthly ohlcv-1m chunks 2010-07..2019-04 (reports/stage_e16_windows.json products.YM) = USD 0.0991/month x 43. Quotes to obtain: GLBX.MDP3 ohlcv-1m YM.v.0 2015-10-01..2019-04-30.
- Combination (sums over members; clean window = the shortest member's): discovery USD 0.00, all USD 4.26, clean test window 106.97 months.

### Dossier MYM|F10: product MYM, F10 order-book state at 5 min and longer

MYM is YM's micro (1/10 size); MYM's F3 statistics are YM's (OC-1 transfer); MYM settles daily from YM (EQUITY-22, -23). The two are one underlying and never pool members together.

*DOW (Dow Jones Industrial Average)*: mechanism, participant flow, horizon, evidence rows and R1 overlap exactly as in dossier YM|F10 (same underlying, same family).

Band and horizon: documented horizon(s) [5, 15] min lie outside B (30-60 min) (documented [5, 15, 30] min). C051 h_c 30; C052 h_c 60 (h_c not a documented horizon)

Cost and power at h_c (ticks of the member's own tick; e80 = SR80 sqrt(T) sigma_hc / sqrt(K)):

| id | venue | band | h_c | member | c_f | sigma_hc | c_f/sigma | p_be emp / norm | p_1 emp / norm | K_year | K_disc | K_test | e80 disc G3+G4 / G3 / test | c_f + e80_test |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C051 | mffu | 30-60 | 30 | MYM | 5.300 | 63.23 | 0.0838 | 0.5583 / 0.5525 | 0.5694 / 0.5624 | 3276.0 | 10348.0 | 11310.0 | 4.05 / 3.55 / 3.40 | 8.70 |
| C052 | ibkr | 30-120 | 60 | MYM | 6.340 | 88.56 | 0.0716 | 0.5491 / 0.5449 | 0.5569 / 0.5519 | 1512.0 | 4776.0 | 5220.0 | 8.35 / 7.32 / 7.00 | 13.34 |

Prop fit (one contract) and own-broker fit:

| id | venue | member | DLL (USD) / MLL | DLL/(sigma v) | flat-by-close PT, latest start | payout threshold vs sqrt(n/day) sigma v | news events a week | gates | queue-limit c_lim (passive entry / both) | margin, sigma_day |
|---|---|---|---|---|---|---|---|---|---|---|
| C051 | mffu | MYM | 1000.0 / 2000.0 | 31.63 | 13:10, 12:30 | 0 vs 114.00 (below) | 0.000 | none | - | - |
| C052 | ibkr | MYM | none (own account) | - | none, 12:00 | - | 0 | none | not computed | intraday initial USD 1269.99 (overnight 1814.27); sigma_cc 275.49 ticks = USD 137.74 |

Data needed:

- MYM: schema mbo (YM; MBO from 2017-05-21). Discovery 2020-12-01..2024-02-29 (39 months; bars owned: True); test 2015-10-01..2019-04-30 (43 months; never read, unsealed, not owned: buy); clean test window 106.97 months (never read, unsealed: ['2010-06-06', '2019-05-06']). Cost (estimates): discovery USD 227.57, test USD 250.91, all USD 478.48; basis: census estimate k = USD 5.8351/month (F2_data_access codes.YM.k_usd_month, scaled from mbp-1 (estimate)) x months; MYM's F10 signal is priced on YM's book (the full-size leader of the same underlying; MYM's own MBO starts 2019-05-06 and its own k is USD 9.65/month); an assumption. Quotes to obtain: GLBX.MDP3 mbo YM.v.0 2020-12-01..2024-02-29; GLBX.MDP3 mbo YM.v.0 2015-10-01..2019-04-30 (MBP-10 before 2017-05-21). Not priced: MBP-10 is the highest granularity before 2017-05-21 (F2_data_access databento_dataset).
- Combination (sums over members; clean window = the shortest member's): discovery USD 227.57, all USD 478.48, clean test window 106.97 months.

### Dossier MYM|F11: product MYM, F11 own-price-path trend and reversal

MYM is YM's micro (1/10 size); MYM's F3 statistics are YM's (OC-1 transfer); MYM settles daily from YM (EQUITY-22, -23). The two are one underlying and never pool members together.

*DOW (Dow Jones Industrial Average)*: mechanism, participant flow, horizon, evidence rows and R1 overlap exactly as in dossier YM|F11 (same underlying, same family).

Band and horizon: documented horizon(s) [5, 15] min lie outside B (30-60 min) (documented [5, 15, 60] min). C053 h_c 30 (h_c not a documented horizon); C054 h_c 60

Cost and power at h_c (ticks of the member's own tick; e80 = SR80 sqrt(T) sigma_hc / sqrt(K)):

| id | venue | band | h_c | member | c_f | sigma_hc | c_f/sigma | p_be emp / norm | p_1 emp / norm | K_year | K_disc | K_test | e80 disc G3+G4 / G3 / test | c_f + e80_test |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C053 | mffu | 30-60 | 30 | MYM | 5.300 | 63.23 | 0.0838 | 0.5583 / 0.5525 | 0.5694 / 0.5624 | 3276.0 | 10348.0 | 11310.0 | 4.05 / 3.55 / 3.40 | 8.70 |
| C054 | ibkr | 30-120 | 60 | MYM | 6.340 | 88.56 | 0.0716 | 0.5491 / 0.5449 | 0.5569 / 0.5519 | 1512.0 | 4776.0 | 5220.0 | 8.35 / 7.32 / 7.00 | 13.34 |

Prop fit (one contract) and own-broker fit:

| id | venue | member | DLL (USD) / MLL | DLL/(sigma v) | flat-by-close PT, latest start | payout threshold vs sqrt(n/day) sigma v | news events a week | gates | queue-limit c_lim (passive entry / both) | margin, sigma_day |
|---|---|---|---|---|---|---|---|---|---|---|
| C053 | mffu | MYM | 1000.0 / 2000.0 | 31.63 | 13:10, 12:30 | 0 vs 114.00 (below) | 0.000 | none | - | - |
| C054 | ibkr | MYM | none (own account) | - | none, 12:00 | - | 0 | none | not computed | intraday initial USD 1269.99 (overnight 1814.27); sigma_cc 275.49 ticks = USD 137.74 |

Data needed:

- MYM: schema ohlcv-1m (YM price path). Discovery 2020-12-01..2024-02-29 (39 months; bars owned: True); test 2015-10-01..2019-04-30 (43 months; never read, unsealed, not owned: buy); clean test window 106.97 months (never read, unsealed: ['2010-06-06', '2019-05-06']). Cost (estimates): discovery USD 0.00, test USD 4.26, all USD 4.26; basis: estimate: E.12 quote USD 10.50261 for 106 monthly ohlcv-1m chunks 2010-07..2019-04 (reports/stage_e16_windows.json products.YM) = USD 0.0991/month x 43. Quotes to obtain: GLBX.MDP3 ohlcv-1m YM.v.0 2015-10-01..2019-04-30.
- Combination (sums over members; clean window = the shortest member's): discovery USD 0.00, all USD 4.26, clean test window 106.97 months.

### Dossier MYM|F12: product MYM, F12 expiry and option-hedging days

MYM is YM's micro (1/10 size); MYM's F3 statistics are YM's (OC-1 transfer); MYM settles daily from YM (EQUITY-22, -23). The two are one underlying and never pool members together.

*DOW (Dow Jones Industrial Average)*: mechanism, participant flow, horizon, evidence rows and R1 overlap exactly as in dossier YM|F12 (same underlying, same family).

Band and horizon: documented horizon(s) [10] min lie outside B (30-60 min) (documented [10, 30, 60] min). C055 h_c 30; C056 h_c 60

Cost and power at h_c (ticks of the member's own tick; e80 = SR80 sqrt(T) sigma_hc / sqrt(K)):

| id | venue | band | h_c | member | c_f | sigma_hc | c_f/sigma | p_be emp / norm | p_1 emp / norm | K_year | K_disc | K_test | e80 disc G3+G4 / G3 / test | c_f + e80_test |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C055 | mffu | 30-60 | 30 | MYM | 5.300 | 63.23 | 0.0838 | 0.5583 / 0.5525 | 0.5694 / 0.5624 | 12.0 | 37.9 | 41.4 | 66.89 / 58.68 / 56.11 | 61.41 |
| C056 | ibkr | 30-120 | 60 | MYM | 6.340 | 88.56 | 0.0716 | 0.5491 / 0.5449 | 0.5569 / 0.5519 | 12.0 | 37.9 | 41.4 | 93.69 / 82.18 / 78.58 | 84.92 |

Prop fit (one contract) and own-broker fit:

| id | venue | member | DLL (USD) / MLL | DLL/(sigma v) | flat-by-close PT, latest start | payout threshold vs sqrt(n/day) sigma v | news events a week | gates | queue-limit c_lim (passive entry / both) | margin, sigma_day |
|---|---|---|---|---|---|---|---|---|---|---|
| C055 | mffu | MYM | 1000.0 / 2000.0 | 31.63 | 13:10, 12:30 | 0 vs 6.90 (below) | 0.000 | none | - | - |
| C056 | ibkr | MYM | none (own account) | - | none, 12:00 | - | 0 | none | not computed | intraday initial USD 1269.99 (overnight 1814.27); sigma_cc 275.49 ticks = USD 137.74 |

Data needed:

- MYM: schema ohlcv-1m (YM price path). Discovery 2020-12-01..2024-02-29 (39 months; bars owned: True); test 2015-10-01..2019-04-30 (43 months; never read, unsealed, not owned: buy); clean test window 106.97 months (never read, unsealed: ['2010-06-06', '2019-05-06']). Cost (estimates): discovery USD 0.00, test USD 4.26, all USD 4.26; basis: estimate: E.12 quote USD 10.50261 for 106 monthly ohlcv-1m chunks 2010-07..2019-04 (reports/stage_e16_windows.json products.YM) = USD 0.0991/month x 43. Quotes to obtain: GLBX.MDP3 ohlcv-1m YM.v.0 2015-10-01..2019-04-30. Not priced: option open interest by strike for a gamma-conditioned variant (GEX; vendor data, cost unknown; R1-14 used GEX rows 2020-05-29..2024-02-28); the 3rd-Friday variant needs bars and the expiry calendar only.
- Combination (sums over members; clean window = the shortest member's): discovery USD 0.00, all USD 4.26, clean test window 106.97 months.

### Dossier MNQ|F01: product MNQ, F01 intraday momentum into the close

MNQ is NQ's satellite: MNQ's F3 statistics are NQ's (OC-1), MNQ settles from NQ's 30-s VWAP (EQUITY-22, -23, -24). NQ is excluded as a candidate (V49); NQ-based closed lines bind MNQ because the price path is the same (lead's instruction for this run).

*NASDAQ (Nasdaq-100)*

- Applies because: Baltussen et al. 2021 define the effect on the cash-session close (EQUITY-49) and report a product row for this underlying (SB-8 YM, SB-9 NQ, SB-10 Russell).
- Participant flow: Gamma hedgers: option market makers short gamma and leveraged-ETF rebalancing trade in the direction of the day's move before the close (Baltussen et al. 2021); late-informed traders (Gao et al. 2018).
- Why predictable: The hedge size is set mechanically by the day's return and is executed near the close, a known time.
- Why an edge could exist at retail size: The flow is non-informational and large against a one-lot; the open issue is size per trade against cost (R1-14: NQ T1 gross 1.25 ticks against 4.08 cost). One contract moves no price; at tens of milliseconds to a second without co-location only effects lasting minutes are reachable (information is priced within 1 to 5 s on ES, NQ, ZN, CL: E.25).
- Mechanism quote: "Hedging short gamma exposure requires trading in the direction of price movements, thereby creating price momentum." (reports/stage_e13_briefs/pages/InfoSource/baltussen_etal_2021_jfe.md:84-85)
- Documented horizon: 30 min: entry at close-30, exit at the cash close (Baltussen et al.; EQUITY-49)
- Timing: entry 12:30 PT (14:30 CT), exit 13:00 PT (15:00 CT cash close); main session 06:30-13:00 PT (cash 09:30-16:00 ET, EQUITY-47/-49)
- Kind: daily; events a year: 252 (one trade a trade date (spec 9.2: 252 trade dates a year)); trades per event: 1
- Absorption under 5 minutes (R2): Not applicable as such: the effect is a 30-minute flow pattern. Contrary evidence is decay and regime change (EQUITY-39, -40, -41), not fast absorption.
- Evidence rows (relation to this product; full rows in the catalog): F01.E01 (asset-class pool (17 equity index futures, incl. NQ); full_text); F01.E02 (this underlying: NQ product row (SB-9); MNQ is NQ's satellite; full_text); F01.E04 (all products (cost statement); full_text); F01.E05 (other venue, other index (SPY; IWM); reused (E.20 full text)); F01.E06 (cash index, other index (S&P 500); reused); F01.E10 (cousin (ES); reused (full text)); F01.E11 (cash S&P 500 (pointer); reused); F01.E12 (index futures (abstract); abstract); F01.E13 (equity, bond and FX futures pool (abstract); abstract); F01.E14 (this underlying: NQ price path at MNQ cost (program test); reused (program record)); F01.E15 (pooled program test incl. NQ; reused)
- R1 overlap (closing sentences in the R1 catalog):
  - R1-14 (same underlying: NQ price path traded at MNQ cost): H6 T1 always, T2 |r_ROD| above its 60-date median, T3 negative prior-day GEX; entry at C-30 (14:30 CT) to the close; 2020-06-01..2024-02-29. Reading: closed configuration (LR-R1: a closed configuration stays closed at every venue, the own broker included).
  - R1-13 (pooled incl. NQ (2010-07..2024-02)): E16-H1 settlement-window momentum and H4 reversal. Reading: closed configuration (LR-R1: a closed configuration stays closed at every venue, the own broker included).
  - R1-03 (MNQ traded): K1-cp1-01 open-to-first-half-hour momentum port; exit by the exchange-set flat F per R1. Reading: closed configuration (LR-R1: a closed configuration stays closed at every venue, the own broker included).
  - R1-15 (same underlying (NQ searched)): E20S ML, 45 configurations, r_ROD features, extra decision time t4 = F_X - 60 min, h60/h120/hF. Reading: closed configuration (LR-R1: a closed configuration stays closed at every venue, the own broker included).
  - R1-18 (same underlying (NQ)): H6 reversal direction at 5 and 20 days. Reading: multi-day line, outside the 5-240 minute scope.
  - R1-11 (MNQ tested): Gate 0 ML at h60, h120, hF. Reading: closed configuration (LR-R1: a closed configuration stays closed at every venue, the own broker included).
  - R1-23 (not product-specific): C2 GEX late-session momentum stopped at its power rule. Reading: a stop before any test, not a test (R1 ambiguity list).
- Open questions (R2): No per-product estimate after 2020-05 on any CME candidate; post-2018 equity evidence is regime-dependent (EQUITY-39) or a pointer (EQUITY-40). | No cost-adjusted per-product result; the only net statements are ES (one sentence) and SPY net of spread 2005-2013. | Micro codes, yield futures and mini grains were not in the sample; their price path is the full-size sibling's (settlement-derived), costs differ. | Whether a variant that differs from H6/E16-H1 (other products, conditioning) counts as a 'close variant' under R1 is for the lead and scorer.

Band and horizon: documented horizon inside B (documented [30] min). C057 h_c 30; C058 h_c 30; C059 h_c 30; C060 h_c 30; C061 h_c 30

Cost and power at h_c (ticks of the member's own tick; e80 = SR80 sqrt(T) sigma_hc / sqrt(K)):

| id | venue | band | h_c | member | c_f | sigma_hc | c_f/sigma | p_be emp / norm | p_1 emp / norm | K_year | K_disc | K_test | e80 disc G3+G4 / G3 / test | c_f + e80_test |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C057 | topstep | 15-30 | 30 | MNQ | 3.940 | 147.10 | 0.0268 | 0.5183 / 0.5168 | 0.5229 / 0.5210 | 252.0 | 796.0 | 870.0 | 33.96 / 29.79 / 28.48 | 32.42 |
| C058 | tradeify | 15-30 | 30 | MNQ | 5.140 | 147.10 | 0.0349 | 0.5238 / 0.5219 | 0.5284 / 0.5262 | 252.0 | 796.0 | 870.0 | 33.96 / 29.79 / 28.48 | 33.62 |
| C059 | mffu | 15-30 | 30 | MNQ | 5.300 | 147.10 | 0.0360 | 0.5246 / 0.5226 | 0.5292 / 0.5268 | 252.0 | 796.0 | 870.0 | 33.96 / 29.79 / 28.48 | 33.78 |
| C060 | lucid | 15-30 | 30 | MNQ | 5.300 | 147.10 | 0.0360 | 0.5246 / 0.5226 | 0.5292 / 0.5268 | 252.0 | 796.0 | 870.0 | 33.96 / 29.79 / 28.48 | 33.78 |
| C061 | ibkr | 15-30 | 30 | MNQ | 6.344 | 147.10 | 0.0431 | 0.5294 / 0.5270 | 0.5340 / 0.5313 | 252.0 | 796.0 | 870.0 | 33.96 / 29.79 / 28.48 | 34.83 |

Prop fit (one contract) and own-broker fit:

| id | venue | member | DLL (USD) / MLL | DLL/(sigma v) | flat-by-close PT, latest start | payout threshold vs sqrt(n/day) sigma v | news events a week | gates | queue-limit c_lim (passive entry / both) | margin, sigma_day |
|---|---|---|---|---|---|---|---|---|---|---|
| C057 | topstep | MNQ | none / 2000.0 | 27.19 | 13:10, 12:30 | 150 vs 73.55 (exceeds) | 0.000 | none | - | - |
| C058 | tradeify | MNQ | 1250.0 / 2000.0 | 16.99 | 13:45, 12:30 | 150 vs 73.55 (exceeds) | 0.000 | none | 5.360 / 5.580 | - |
| C059 | mffu | MNQ | 1000.0 / 2000.0 | 13.60 | 13:10, 12:30 | 0 vs 73.55 (below) | 0.000 | none | - | - |
| C060 | lucid | MNQ | 1200.0 / 2000.0 | 16.32 | 13:45, 12:30 | 0 vs 73.55 (below) | 0.000 | none | 5.520 / 5.740 | - |
| C061 | ibkr | MNQ | none (own account) | - | none, 12:30 | - | 0 | none | not computed | intraday initial USD 4622.90 (overnight 6604.14); sigma_cc 699.90 ticks = USD 349.95 |

Data needed:

- MNQ: schema ohlcv-1m (NQ price path). Discovery 2020-12-01..2024-02-29 (39 months; bars owned: True); test no clean window of 36 months or more before 2024-03: every pre-2024-03 month of the underlying was read (census p_basis) and none is sealed; a test would need 2024-03 onward (not sealed for these codes; outside Q7's pre-2024-03 rule); clean test window 0.82 months (never read, unsealed: ['2010-06-06', '2010-07-01']). Cost (estimates): discovery USD 0.00, test USD 0.00, all USD 0.00; basis: no clean pre-2024-03 test window: nothing to buy before 2024-03. Quotes to obtain: none.
- Combination (sums over members; clean window = the shortest member's): discovery USD 0.00, all USD 0.00, clean test window 0.82 months.

### Dossier MNQ|F04: product MNQ, F04 US macro release drift

MNQ is NQ's satellite: MNQ's F3 statistics are NQ's (OC-1), MNQ settles from NQ's 30-s VWAP (EQUITY-22, -23, -24). NQ is excluded as a candidate (V49); NQ-based closed lines bind MNQ because the price path is the same (lead's instruction for this run).

*NASDAQ (Nasdaq-100)*

- Applies because: Scheduled US macro releases: NFP, CPI, PPI, GDP 08:30 ET; ISM 10:00 ET (EQUITY-16).
- Participant flow: Repricing of rate and growth expectations after a surprise; slower cross-asset digestion (copper, silver lags).
- Why predictable: Pre-announced calendar (EQUITY-16).
- Why an edge could exist at retail size: Only in the slower components: ES continuing adjustment 10-30 min (EQUITY-17) and the metals' delayed response (METALS-23); the jump itself is absorbed within seconds to a minute (RATES-19, -20; FX-22). One contract moves no price; at tens of milliseconds to a second without co-location only effects lasting minutes are reachable (information is priced within 1 to 5 s on ES, NQ, ZN, CL: E.25).
- Mechanism quote: none recorded in the R2 file for this family
- Documented horizon: entry 5-10 min after the release, exit 30-60 min (R2-F04); ES continuing adjustment t+10 to t+30 min (EQUITY-17)
- Timing: 08:30 ET releases (NFP, CPI, PPI, GDP) = 05:30 PT, BEFORE the main session (Globex pre-open); 10:00 ET releases (ISM) = 07:00 PT, inside; 09:15 ET (IP) = 06:15 PT, before (not counted: no calendar file); main session 06:30-13:00 PT (cash 09:30-16:00 ET, EQUITY-47/-49)
- Kind: event; events a year: 67.62 (326 releases in 4.821 years = 67.62 a year (reports/stage_e20_briefs/shared/macro_calendars.md section 3 (via EQUITY-16): counts in 2019-05-06..2024-02-29: NFP 57, CPI 58, PPI 58, GDP first and last 38, ISM services 57, ISM manufacturing 58)); trades per event: 1
- Absorption under 5 minutes (R2): Strongest of all families: rates (RATES-19, -20), FX (FX-21, -22), ES order flow (EQUITY-19), crypto (CRYPTO-27, -29), E.25 (1-5 seconds on ES, NQ, ZN, CL). Slower pieces: ES 10-30 min (weak joint test), copper and silver delays (2002-2008).
- Evidence rows (relation to this product; full rows in the catalog): F04.E03 (cousin (ES), 30 announcements, full text; full_text); F04.E01 (cousin (ES) and ZN, after NFP; full_text); F04.E08 (cousin (ES order flow, abstract); abstract)
- R1 overlap (closing sentences in the R1 catalog):
  - R1-01 (cousin (MES)): MES family E scheduled-macro and calendar windows. Reading: family closed on another product (family overlap under LR-R1).
  - R1-19 (same underlying (NQ in the 17-root census)): E.20 Part A census of published intraday effects, macro-release effects included. Reading: evidence finding (R1-19), not a ban on new families (LR-R1).
- Open questions (R2): No post-2015 study shows a mean drift of 5 minutes or more after US macro releases in Treasury, FX or crypto futures (searched, not found: F2_rates, F2_fx, F2_crypto). | Firm news windows (Topstep Tier 1: CPI, NFP, PPI, FOMC; equity minis and GC SI HG blocked, MGC capped per planner pointer) may gate the core trade: FirmRules owns this.

Band and horizon: documented horizon(s) [60] min lie outside B (15-30 min) (documented [20, 30, 60] min). C062 h_c 30; C063 h_c 30; C064 h_c 30; C065 h_c 30; C066 h_c 30

Cost and power at h_c (ticks of the member's own tick; e80 = SR80 sqrt(T) sigma_hc / sqrt(K)):

| id | venue | band | h_c | member | c_f | sigma_hc | c_f/sigma | p_be emp / norm | p_1 emp / norm | K_year | K_disc | K_test | e80 disc G3+G4 / G3 / test | c_f + e80_test |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C062 | topstep | 15-30 | 30 | MNQ | 3.940 | 147.10 | 0.0268 | 0.5183 / 0.5168 | 0.5229 / 0.5210 | 67.6 | 213.6 | 233.4 | 65.56 / 57.51 / 54.99 | 58.93 |
| C063 | tradeify | 15-30 | 30 | MNQ | 5.140 | 147.10 | 0.0349 | 0.5238 / 0.5219 | 0.5284 / 0.5262 | 67.6 | 213.6 | 233.4 | 65.56 / 57.51 / 54.99 | 60.13 |
| C064 | mffu | 15-30 | 30 | MNQ | 5.300 | 147.10 | 0.0360 | 0.5246 / 0.5226 | 0.5292 / 0.5268 | 67.6 | 213.6 | 233.4 | 65.56 / 57.51 / 54.99 | 60.29 |
| C065 | lucid | 15-30 | 30 | MNQ | 5.300 | 147.10 | 0.0360 | 0.5246 / 0.5226 | 0.5292 / 0.5268 | 67.6 | 213.6 | 233.4 | 65.56 / 57.51 / 54.99 | 60.29 |
| C066 | ibkr | 15-30 | 30 | MNQ | 6.344 | 147.10 | 0.0431 | 0.5294 / 0.5270 | 0.5340 / 0.5313 | 67.6 | 213.6 | 233.4 | 65.56 / 57.51 / 54.99 | 61.33 |

Prop fit (one contract) and own-broker fit:

| id | venue | member | DLL (USD) / MLL | DLL/(sigma v) | flat-by-close PT, latest start | payout threshold vs sqrt(n/day) sigma v | news events a week | gates | queue-limit c_lim (passive entry / both) | margin, sigma_day |
|---|---|---|---|---|---|---|---|---|---|---|
| C062 | topstep | MNQ | none / 2000.0 | 27.19 | 13:10, 12:30 | 150 vs 38.10 (exceeds) | 0.000 | none | - | - |
| C063 | tradeify | MNQ | 1250.0 / 2000.0 | 16.99 | 13:45, 12:30 | 150 vs 38.10 (exceeds) | 0.000 | none | 5.360 / 5.580 | - |
| C064 | mffu | MNQ | 1000.0 / 2000.0 | 13.60 | 13:10, 12:30 | 0 vs 38.10 (below) | 0.000 | none | - | - |
| C065 | lucid | MNQ | 1200.0 / 2000.0 | 16.32 | 13:45, 12:30 | 0 vs 38.10 (below) | 0.000 | none | 5.520 / 5.740 | - |
| C066 | ibkr | MNQ | none (own account) | - | none, 12:30 | - | 0 | none | not computed | intraday initial USD 4622.90 (overnight 6604.14); sigma_cc 699.90 ticks = USD 349.95 |

Data needed:

- MNQ: schema ohlcv-1m (NQ price path). Discovery 2020-12-01..2024-02-29 (39 months; bars owned: True); test no clean window of 36 months or more before 2024-03: every pre-2024-03 month of the underlying was read (census p_basis) and none is sealed; a test would need 2024-03 onward (not sealed for these codes; outside Q7's pre-2024-03 rule); clean test window 0.82 months (never read, unsealed: ['2010-06-06', '2010-07-01']). Cost (estimates): discovery USD 0.00, test USD 0.00, all USD 0.00; basis: no clean pre-2024-03 test window: nothing to buy before 2024-03. Quotes to obtain: none. Not priced: release calendar (E.20 frozen calendar covers 2019-05..2024-02 only; no 2010-2019 file for NFP, CPI, PPI, GDP, ISM: macro_calendars.md section 3); consensus forecasts only for a surprise-signed variant (vendor data, not owned, cost unknown).
- Combination (sums over members; clean window = the shortest member's): discovery USD 0.00, all USD 0.00, clean test window 0.82 months.

### Dossier MNQ|F05: product MNQ, F05 FOMC post-statement drift

MNQ is NQ's satellite: MNQ's F3 statistics are NQ's (OC-1), MNQ settles from NQ's 30-s VWAP (EQUITY-22, -23, -24). NQ is excluded as a candidate (V49); NQ-based closed lines bind MNQ because the price path is the same (lead's instruction for this run).

*NASDAQ (Nasdaq-100)*

- Applies because: Scheduled FOMC statements 14:00 ET, eight a year (EQUITY-16; R2-F05).
- Participant flow: Slow repricing of the policy path after the 14:00 ET statement and press conference; portfolio rebalancing over the afternoon.
- Why predictable: Eight scheduled meetings a year (FX-26 for frequency of ECB/RBA; FOMC 8/yr).
- Why an edge could exist at retail size: SR 1188 finds an unconditional, persistent yield decline for about 3 hours after the statement, a horizon a one-lot can reach. One contract moves no price; at tens of milliseconds to a second without co-location only effects lasting minutes are reachable (information is priced within 1 to 5 s on ES, NQ, ZN, CL: E.25).
- Mechanism quote: none recorded in the R2 file for this family
- Documented horizon: after the 14:00 ET statement to the close: FOMC-day last half-hour (15:30-16:00 ET), 75+ min after the statement (EQUITY-20); Treasury yields about 3 h (RATES-23)
- Timing: statement 11:00 PT (14:00 ET), press conference 11:30 PT; last half-hour 12:30-13:00 PT; main session 06:30-13:00 PT (cash 09:30-16:00 ET, EQUITY-47/-49)
- Kind: event; events a year: 8 (eight scheduled FOMC meetings a year (R2-F05 mechanism; frozen calendar 37 statements in 2019-05-06..2024-02-29, macro_calendars.md section 3)); trades per event: 1
- Absorption under 5 minutes (R2): Statement jump fast (E.25 for ZN); gold continues 5-10 min (METALS-25); rates drift persists about 3 h (RATES-23).
- Evidence rows (relation to this product; full rows in the catalog): F05.E02 (other venue (SPY), FOMC release days; reused); F05.E06 (cash S&P 500 and Treasuries: pre-FOMC drift (before the statement); reused / abstract); F05.E01 (other asset class (cash Treasury yields); reused (E.20 full text))
- R1 overlap (closing sentences in the R1 catalog):
  - R1-04 (other product (rates)): K2 post-FOMC member (Tier B, no confirmation). Reading: family closed on another product (family overlap under LR-R1).
  - R1-07 (other product (MGC)): K5-fomc-01, E.22 confirmation null. Reading: family closed on another product (family overlap under LR-R1).
  - R1-01 (cousin (MES)): MES family E scheduled-macro and calendar windows. Reading: family closed on another product (family overlap under LR-R1).
- Open questions (R2): Is SR 1188's 3-hour decline present in ZN/ZF futures after 2015 and net of costs? Not found. | FOMC is a Topstep Tier 1 event (planner pointer): whether rates are outside its window (pointer says 'energies, rates, FX unaffected') is FirmRules' fact.

Band and horizon: documented horizon(s) [120] min lie outside B (15-30 min) (documented [30, 120] min). C067 h_c 30; C068 h_c 30; C069 h_c 30; C070 h_c 30; C071 h_c 30

Cost and power at h_c (ticks of the member's own tick; e80 = SR80 sqrt(T) sigma_hc / sqrt(K)):

| id | venue | band | h_c | member | c_f | sigma_hc | c_f/sigma | p_be emp / norm | p_1 emp / norm | K_year | K_disc | K_test | e80 disc G3+G4 / G3 / test | c_f + e80_test |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C067 | topstep | 15-30 | 30 | MNQ | 3.940 | 147.10 | 0.0268 | 0.5183 / 0.5168 | 0.5229 / 0.5210 | 8.0 | 25.3 | 27.6 | 190.60 / 167.18 / 159.86 | 163.80 |
| C068 | tradeify | 15-30 | 30 | MNQ | 5.140 | 147.10 | 0.0349 | 0.5238 / 0.5219 | 0.5284 / 0.5262 | 8.0 | 25.3 | 27.6 | 190.60 / 167.18 / 159.86 | 165.00 |
| C069 | mffu | 15-30 | 30 | MNQ | 5.300 | 147.10 | 0.0360 | 0.5246 / 0.5226 | 0.5292 / 0.5268 | 8.0 | 25.3 | 27.6 | 190.60 / 167.18 / 159.86 | 165.16 |
| C070 | lucid | 15-30 | 30 | MNQ | 5.300 | 147.10 | 0.0360 | 0.5246 / 0.5226 | 0.5292 / 0.5268 | 8.0 | 25.3 | 27.6 | 190.60 / 167.18 / 159.86 | 165.16 |
| C071 | ibkr | 15-30 | 30 | MNQ | 6.344 | 147.10 | 0.0431 | 0.5294 / 0.5270 | 0.5340 / 0.5313 | 8.0 | 25.3 | 27.6 | 190.60 / 167.18 / 159.86 | 166.20 |

Prop fit (one contract) and own-broker fit:

| id | venue | member | DLL (USD) / MLL | DLL/(sigma v) | flat-by-close PT, latest start | payout threshold vs sqrt(n/day) sigma v | news events a week | gates | queue-limit c_lim (passive entry / both) | margin, sigma_day |
|---|---|---|---|---|---|---|---|---|---|---|
| C067 | topstep | MNQ | none / 2000.0 | 27.19 | 13:10, 12:30 | 150 vs 13.11 (exceeds) | 0.000 | none | - | - |
| C068 | tradeify | MNQ | 1250.0 / 2000.0 | 16.99 | 13:45, 12:30 | 150 vs 13.11 (exceeds) | 0.000 | none | 5.360 / 5.580 | - |
| C069 | mffu | MNQ | 1000.0 / 2000.0 | 13.60 | 13:10, 12:30 | 0 vs 13.11 (below) | 0.000 | none | - | - |
| C070 | lucid | MNQ | 1200.0 / 2000.0 | 16.32 | 13:45, 12:30 | 0 vs 13.11 (below) | 0.000 | none | 5.520 / 5.740 | - |
| C071 | ibkr | MNQ | none (own account) | - | none, 12:30 | - | 0 | none | not computed | intraday initial USD 4622.90 (overnight 6604.14); sigma_cc 699.90 ticks = USD 349.95 |

Data needed:

- MNQ: schema ohlcv-1m (NQ price path). Discovery 2020-12-01..2024-02-29 (39 months; bars owned: True); test no clean window of 36 months or more before 2024-03: every pre-2024-03 month of the underlying was read (census p_basis) and none is sealed; a test would need 2024-03 onward (not sealed for these codes; outside Q7's pre-2024-03 rule); clean test window 0.82 months (never read, unsealed: ['2010-06-06', '2010-07-01']). Cost (estimates): discovery USD 0.00, test USD 0.00, all USD 0.00; basis: no clean pre-2024-03 test window: nothing to buy before 2024-03. Quotes to obtain: none. Not priced: FOMC statement dates and times (calendar files 2010-2024 exist: macro_calendars.md section 3).
- Combination (sums over members; clean window = the shortest member's): discovery USD 0.00, all USD 0.00, clean test window 0.82 months.

### Dossier MNQ|F08: product MNQ, F08 session and overnight-to-day handoff

MNQ is NQ's satellite: MNQ's F3 statistics are NQ's (OC-1), MNQ settles from NQ's 30-s VWAP (EQUITY-22, -23, -24). NQ is excluded as a candidate (V49); NQ-based closed lines bind MNQ because the price path is the same (lead's instruction for this run).

*NASDAQ (Nasdaq-100)*

- Applies because: Fixed session clocks: Globex Sun-Fri 18:00-17:00 ET, cash session 09:30-16:00 ET (EQUITY-47, EQUITY-49); European open 02:00-03:00 ET documented on the ES cousin (EQUITY-50).
- Participant flow: Local-hours hedging and order imbalances carried over from the prior close (Boyarchenko et al.: 2:00-3:00 ET returns linked to prior US-close imbalances); overnight news priced at the reopen.
- Why predictable: Fixed session clocks (Globex pauses: grains 07:45-08:30 CT, GRAINS-14; daily 16:00-17:00 CT halts).
- Why an edge could exist at retail size: Hours-scale holds around a known clock; most documented versions are gross or negative after spreads. One contract moves no price; at tens of milliseconds to a second without co-location only effects lasting minutes are reachable (information is priced within 1 to 5 s on ES, NQ, ZN, CL: E.25).
- Mechanism quote: none recorded in the R2 file for this family
- Documented horizon: European open 02:00-03:00 ET, 60 min (EQUITY-50); the cash-open first half-hour as the predictor of the close (F01.E05)
- Timing: European open 23:00-00:00 PT (prior evening, Globex, outside the main session); cash open 06:30 PT; main session 06:30-13:00 PT (cash 09:30-16:00 ET, EQUITY-47/-49)
- Kind: daily; events a year: 252 (one trade a trade date); trades per event: 1
- Absorption under 5 minutes (R2): Not the issue here; the evidence that exists is either gross, pre-2013, other-venue, or negative after spreads (EQUITY-51) or arbitraged after a venue change (GRAINS-42, GRAINS-17).
- Evidence rows (relation to this product; full rows in the catalog): F08.E03 (cousin (ES), European open 02:00-03:00 ET; full_text); F01.E05 (other venue (SPY): first half-hour predicts the last half-hour (listed under F01; the open-to-close handoff); reused (E.20 full text))
- R1 overlap (closing sentences in the R1 catalog):
  - R1-03 (MNQ traded): K1-cp3-01 prior-day close-location (08:30 CT entry; exit by the exchange-set flat F per R1). Reading: closed configuration (LR-R1: a closed configuration stays closed at every venue, the own broker included).
  - R1-13 (pooled incl. NQ): E16-H4 next-day reversal of the settlement-window move. Reading: closed configuration (LR-R1: a closed configuration stays closed at every venue, the own broker included).
  - R1-10 (MNQ traded): K8-wkndbtc-01 weekend bitcoin move to NQ/MNQ (inconclusive by design, not run in confirmation). Reading: closed configuration (LR-R1: a closed configuration stays closed at every venue, the own broker included).
  - R1-01 (cousin (MES)): families A (clock windows) and D (gaps), incl. European-open drift. Reading: family closed on another product (family overlap under LR-R1).
- Open questions (R2): No post-2010 futures test of the local-hours currency effect on 6E/6A net of a futures round trip. | Grains 08:30 CT reopen after the 07:45-08:30 pause: untested (planner family 4), and Export Sales lands at 07:30 CT just before the pause (GRAINS-22).

Band and horizon: documented horizon(s) [60] min lie outside B (15-30 min) (documented [30, 60] min). C072 h_c 30; C073 h_c 30; C074 h_c 30; C075 h_c 30; C076 h_c 30

Cost and power at h_c (ticks of the member's own tick; e80 = SR80 sqrt(T) sigma_hc / sqrt(K)):

| id | venue | band | h_c | member | c_f | sigma_hc | c_f/sigma | p_be emp / norm | p_1 emp / norm | K_year | K_disc | K_test | e80 disc G3+G4 / G3 / test | c_f + e80_test |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C072 | topstep | 15-30 | 30 | MNQ | 3.940 | 147.10 | 0.0268 | 0.5183 / 0.5168 | 0.5229 / 0.5210 | 252.0 | 796.0 | 870.0 | 33.96 / 29.79 / 28.48 | 32.42 |
| C073 | tradeify | 15-30 | 30 | MNQ | 5.140 | 147.10 | 0.0349 | 0.5238 / 0.5219 | 0.5284 / 0.5262 | 252.0 | 796.0 | 870.0 | 33.96 / 29.79 / 28.48 | 33.62 |
| C074 | mffu | 15-30 | 30 | MNQ | 5.300 | 147.10 | 0.0360 | 0.5246 / 0.5226 | 0.5292 / 0.5268 | 252.0 | 796.0 | 870.0 | 33.96 / 29.79 / 28.48 | 33.78 |
| C075 | lucid | 15-30 | 30 | MNQ | 5.300 | 147.10 | 0.0360 | 0.5246 / 0.5226 | 0.5292 / 0.5268 | 252.0 | 796.0 | 870.0 | 33.96 / 29.79 / 28.48 | 33.78 |
| C076 | ibkr | 15-30 | 30 | MNQ | 6.344 | 147.10 | 0.0431 | 0.5294 / 0.5270 | 0.5340 / 0.5313 | 252.0 | 796.0 | 870.0 | 33.96 / 29.79 / 28.48 | 34.83 |

Prop fit (one contract) and own-broker fit:

| id | venue | member | DLL (USD) / MLL | DLL/(sigma v) | flat-by-close PT, latest start | payout threshold vs sqrt(n/day) sigma v | news events a week | gates | queue-limit c_lim (passive entry / both) | margin, sigma_day |
|---|---|---|---|---|---|---|---|---|---|---|
| C072 | topstep | MNQ | none / 2000.0 | 27.19 | 13:10, 12:30 | 150 vs 73.55 (exceeds) | 0.000 | none | - | - |
| C073 | tradeify | MNQ | 1250.0 / 2000.0 | 16.99 | 13:45, 12:30 | 150 vs 73.55 (exceeds) | 0.000 | none | 5.360 / 5.580 | - |
| C074 | mffu | MNQ | 1000.0 / 2000.0 | 13.60 | 13:10, 12:30 | 0 vs 73.55 (below) | 0.000 | none | - | - |
| C075 | lucid | MNQ | 1200.0 / 2000.0 | 16.32 | 13:45, 12:30 | 0 vs 73.55 (below) | 0.000 | none | 5.520 / 5.740 | - |
| C076 | ibkr | MNQ | none (own account) | - | none, 12:30 | - | 0 | none | not computed | intraday initial USD 4622.90 (overnight 6604.14); sigma_cc 699.90 ticks = USD 349.95 |

Data needed:

- MNQ: schema ohlcv-1m (NQ price path). Discovery 2020-12-01..2024-02-29 (39 months; bars owned: True); test no clean window of 36 months or more before 2024-03: every pre-2024-03 month of the underlying was read (census p_basis) and none is sealed; a test would need 2024-03 onward (not sealed for these codes; outside Q7's pre-2024-03 rule); clean test window 0.82 months (never read, unsealed: ['2010-06-06', '2010-07-01']). Cost (estimates): discovery USD 0.00, test USD 0.00, all USD 0.00; basis: no clean pre-2024-03 test window: nothing to buy before 2024-03. Quotes to obtain: none.
- Combination (sums over members; clean window = the shortest member's): discovery USD 0.00, all USD 0.00, clean test window 0.82 months.

### Dossier MNQ|F10: product MNQ, F10 order-book state at 5 min and longer

MNQ is NQ's satellite: MNQ's F3 statistics are NQ's (OC-1), MNQ settles from NQ's 30-s VWAP (EQUITY-22, -23, -24). NQ is excluded as a candidate (V49); NQ-based closed lines bind MNQ because the price path is the same (lead's instruction for this run).

*NASDAQ (Nasdaq-100)*

- Applies because: Order-book data exist for purchase: Databento GLBX.MDP3 MBO from 2017-05-21, MBP-10 before (F2_data_access databento_dataset); the code's MBO start is in the data plan.
- Participant flow: Large orders worked over time (sign persistence) and liquidity shocks followed by refill.
- Why predictable: Imbalance and sign persistence are autocorrelated.
- Why an edge could exist at retail size: Weak: forward predictability decays to insignificance by 5-30 minutes and sign persistence is offset by asymmetric liquidity (E.32 M1). One contract moves no price; at tens of milliseconds to a second without co-location only effects lasting minutes are reachable (information is priced within 1 to 5 s on ES, NQ, ZN, CL: E.25).
- Mechanism quote: none recorded in the R2 file for this family
- Documented horizon: 5-30 min forward (R2-F10); forward predictability insignificant by 5-30 min (F10.E01)
- Timing: any time in the main session; main session 06:30-13:00 PT (cash 09:30-16:00 ET, EQUITY-47/-49)
- Kind: continuous; events a year: - (continuous: n_cap(h_c) a day); trades per event: -
- Absorption under 5 minutes (R2): Central: E.32 M1 (contemporaneous far stronger than forward), Kolm et al. (seconds), E.25 (1-5 seconds on ES, NQ, ZN, CL).
- Evidence rows (relation to this product; full rows in the catalog): F10.E01 (other asset class (NYSE stocks); full_text (E.32 M1)); F10.E02 (equities (abstract); abstract); F10.E06 (cousin (ES): net gamma conditions order-flow reversals; reused (full text)); F10.E07 (other product (ZM), program test; reused); F10.E08 (excluded sub-5-minute items (NQ among them); abstract/reused)
- R1 overlap (closing sentences in the R1 catalog):
  - R1-21 (other product (ZM)): S3 ZM order flow and book state at 5-60 min. Reading: E.33c family closed on ZM; on this product family overlap (LR-R1).
  - R1-22 (same underlying (NQ dropped)): NQ dropped for the passive limit-order direction (V49). Reading: product decision for the passive direction; V49's scope for directional use not stated (R1 ambiguity).
  - R1-20 (execution line (ZM measured)): passive spread capture at the touch, one lot. Reading: execution line: passive spread capture closed (V50); limit orders stay allowed as execution of a signal.
  - R1-11 (MNQ tested): ML on 1-minute bar features (no book data). Reading: closed configuration (LR-R1: a closed configuration stays closed at every venue, the own broker included).
- Open questions (R2): No CME-product study of forward order-flow predictability at 5 minutes or more found outside ZM's own null. | Drift-burst reversal after removing the look-ahead: untested.

Band and horizon: documented horizon(s) [5] min lie outside B (15-30 min) (documented [5, 15, 30] min). C077 h_c 30; C078 h_c 30; C079 h_c 30; C080 h_c 30; C081 h_c 30

Cost and power at h_c (ticks of the member's own tick; e80 = SR80 sqrt(T) sigma_hc / sqrt(K)):

| id | venue | band | h_c | member | c_f | sigma_hc | c_f/sigma | p_be emp / norm | p_1 emp / norm | K_year | K_disc | K_test | e80 disc G3+G4 / G3 / test | c_f + e80_test |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C077 | topstep | 15-30 | 30 | MNQ | 3.940 | 147.10 | 0.0268 | 0.5183 / 0.5168 | 0.5229 / 0.5210 | 3276.0 | 10348.0 | 11310.0 | 9.42 / 8.26 / 7.90 | 11.84 |
| C078 | tradeify | 15-30 | 30 | MNQ | 5.140 | 147.10 | 0.0349 | 0.5238 / 0.5219 | 0.5284 / 0.5262 | 3276.0 | 10348.0 | 11310.0 | 9.42 / 8.26 / 7.90 | 13.04 |
| C079 | mffu | 15-30 | 30 | MNQ | 5.300 | 147.10 | 0.0360 | 0.5246 / 0.5226 | 0.5292 / 0.5268 | 3276.0 | 10348.0 | 11310.0 | 9.42 / 8.26 / 7.90 | 13.20 |
| C080 | lucid | 15-30 | 30 | MNQ | 5.300 | 147.10 | 0.0360 | 0.5246 / 0.5226 | 0.5292 / 0.5268 | 3276.0 | 10348.0 | 11310.0 | 9.42 / 8.26 / 7.90 | 13.20 |
| C081 | ibkr | 15-30 | 30 | MNQ | 6.344 | 147.10 | 0.0431 | 0.5294 / 0.5270 | 0.5340 / 0.5313 | 3276.0 | 10348.0 | 11310.0 | 9.42 / 8.26 / 7.90 | 14.24 |

Prop fit (one contract) and own-broker fit:

| id | venue | member | DLL (USD) / MLL | DLL/(sigma v) | flat-by-close PT, latest start | payout threshold vs sqrt(n/day) sigma v | news events a week | gates | queue-limit c_lim (passive entry / both) | margin, sigma_day |
|---|---|---|---|---|---|---|---|---|---|---|
| C077 | topstep | MNQ | none / 2000.0 | 27.19 | 13:10, 12:30 | 150 vs 265.20 (below) | 0.000 | none | - | - |
| C078 | tradeify | MNQ | 1250.0 / 2000.0 | 16.99 | 13:45, 12:30 | 150 vs 265.20 (below) | 0.000 | none | 5.360 / 5.580 | - |
| C079 | mffu | MNQ | 1000.0 / 2000.0 | 13.60 | 13:10, 12:30 | 0 vs 265.20 (below) | 0.000 | none | - | - |
| C080 | lucid | MNQ | 1200.0 / 2000.0 | 16.32 | 13:45, 12:30 | 0 vs 265.20 (below) | 0.000 | none | 5.520 / 5.740 | - |
| C081 | ibkr | MNQ | none (own account) | - | none, 12:30 | - | 0 | none | not computed | intraday initial USD 4622.90 (overnight 6604.14); sigma_cc 699.90 ticks = USD 349.95 |

Data needed:

- MNQ: schema mbo (MNQ; MBO from 2019-05-06). Discovery 2020-12-01..2024-02-29 (39 months; bars owned: True); test no clean window of 36 months or more before 2024-03: every pre-2024-03 month of the underlying was read (census p_basis) and none is sealed; a test would need 2024-03 onward (not sealed for these codes; outside Q7's pre-2024-03 rule); clean test window 0.82 months (never read, unsealed: ['2010-06-06', '2010-07-01']). Cost (estimates): discovery USD 2026.86, test USD 0.00, all USD 2026.86; basis: census estimate k = USD 51.9707/month (F2_data_access codes.MNQ.k_usd_month, scaled from mbp-1 (estimate)) x months; priced on MNQ's own MBO; NQ's book (census k USD 22.88/month) would be cheaper but NQ is excluded (V49: 'NQ is not used as a pilot or comparison contract'). Quotes to obtain: GLBX.MDP3 mbo MNQ.v.0 2020-12-01..2024-02-29. Not priced: MBP-10 is the highest granularity before 2017-05-21 (F2_data_access databento_dataset).
- Combination (sums over members; clean window = the shortest member's): discovery USD 2026.86, all USD 2026.86, clean test window 0.82 months.

### Dossier MNQ|F11: product MNQ, F11 own-price-path trend and reversal

MNQ is NQ's satellite: MNQ's F3 statistics are NQ's (OC-1), MNQ settles from NQ's 30-s VWAP (EQUITY-22, -23, -24). NQ is excluded as a candidate (V49); NQ-based closed lines bind MNQ because the price path is the same (lead's instruction for this run).

*NASDAQ (Nasdaq-100)*

- Applies because: R2-F11 applies to any code (own price path on 1-minute bars).
- Participant flow: Trend followers and stop cascades (trend); liquidity-provider inventory correction (reversion).
- Why predictable: Price-path autocorrelation by horizon (reversion 2-16 min, weak trend at 1 h or more).
- Why an edge could exist at retail size: Generic and crowded; the published sizes are tiny (out-of-sample R2 under 1 bp). One contract moves no price; at tens of milliseconds to a second without co-location only effects lasting minutes are reachable (information is priced within 1 to 5 s on ES, NQ, ZN, CL: E.25).
- Mechanism quote: none recorded in the R2 file for this family
- Documented horizon: reversion 2-16 min; weak trend at 1 h or more (F11.E01)
- Timing: any time in the main session; main session 06:30-13:00 PT (cash 09:30-16:00 ET, EQUITY-47/-49)
- Kind: continuous; events a year: - (continuous: n_cap(h_c) a day); trades per event: -
- Absorption under 5 minutes (R2): Short reversion is at 2-16 min and tiny (CRUDE-40); Brent inefficiency vanishes past 10 min (CRUDE-54).
- Evidence rows (relation to this product; full rows in the catalog): F11.E01 (futures pool (16-24 futures; equity-index membership not recorded); full_text); F11.E09 (other venue (SPY), noise-area momentum; reused); F11.E10 (this underlying (MNQ 5-min; NQ 15-min), preprints; reused / full_text)
- R1 overlap (closing sentences in the R1 catalog):
  - R1-03 (MNQ traded): K1-cp2-01 opening-range breakout, K1-vxnband-01 VXN band fade, K1-vwap-01 VWAP stop-and-reverse; exit by the exchange-set flat F per R1. Reading: closed configuration (LR-R1: a closed configuration stays closed at every venue, the own broker included).
  - R1-01 (cousin (MES)): families B, C, G, H (breakout, reversal and fade, price-path statistics, ORB). Reading: family closed on another product (family overlap under LR-R1).
  - R1-11 (MNQ tested): Gate 0 ML over 64 bar features at h60, h120, hF. Reading: closed configuration (LR-R1: a closed configuration stays closed at every venue, the own broker included).
  - R1-15 (same underlying (NQ searched)): E20S ML, 36 bar features, h60/h120/hF. Reading: closed configuration (LR-R1: a closed configuration stays closed at every venue, the own broker included).
  - R1-19 (this product): the E.25 shortlist named noise-area intraday momentum on MNQ; never tested; V45 item 3 dropped it on post-publication evidence. Reading: evidence finding (R1-19), not a ban on new families (LR-R1).
  - R1-21 (other product (ZM)): S4 ZM own price path at 5-60 min. Reading: E.33c family closed on ZM; on this product family overlap (LR-R1).
- Open questions (R2): Every generic price-path family has been screened by the program on 1-minute bars; a new one would be a close variant unless the product or mechanism differs (scorer's call).

Band and horizon: documented horizon(s) [5, 60] min lie outside B (15-30 min) (documented [5, 15, 60] min). C082 h_c 30 (h_c not a documented horizon); C083 h_c 30 (h_c not a documented horizon); C084 h_c 30 (h_c not a documented horizon); C085 h_c 30 (h_c not a documented horizon); C086 h_c 30 (h_c not a documented horizon)

Cost and power at h_c (ticks of the member's own tick; e80 = SR80 sqrt(T) sigma_hc / sqrt(K)):

| id | venue | band | h_c | member | c_f | sigma_hc | c_f/sigma | p_be emp / norm | p_1 emp / norm | K_year | K_disc | K_test | e80 disc G3+G4 / G3 / test | c_f + e80_test |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C082 | topstep | 15-30 | 30 | MNQ | 3.940 | 147.10 | 0.0268 | 0.5183 / 0.5168 | 0.5229 / 0.5210 | 3276.0 | 10348.0 | 11310.0 | 9.42 / 8.26 / 7.90 | 11.84 |
| C083 | tradeify | 15-30 | 30 | MNQ | 5.140 | 147.10 | 0.0349 | 0.5238 / 0.5219 | 0.5284 / 0.5262 | 3276.0 | 10348.0 | 11310.0 | 9.42 / 8.26 / 7.90 | 13.04 |
| C084 | mffu | 15-30 | 30 | MNQ | 5.300 | 147.10 | 0.0360 | 0.5246 / 0.5226 | 0.5292 / 0.5268 | 3276.0 | 10348.0 | 11310.0 | 9.42 / 8.26 / 7.90 | 13.20 |
| C085 | lucid | 15-30 | 30 | MNQ | 5.300 | 147.10 | 0.0360 | 0.5246 / 0.5226 | 0.5292 / 0.5268 | 3276.0 | 10348.0 | 11310.0 | 9.42 / 8.26 / 7.90 | 13.20 |
| C086 | ibkr | 15-30 | 30 | MNQ | 6.344 | 147.10 | 0.0431 | 0.5294 / 0.5270 | 0.5340 / 0.5313 | 3276.0 | 10348.0 | 11310.0 | 9.42 / 8.26 / 7.90 | 14.24 |

Prop fit (one contract) and own-broker fit:

| id | venue | member | DLL (USD) / MLL | DLL/(sigma v) | flat-by-close PT, latest start | payout threshold vs sqrt(n/day) sigma v | news events a week | gates | queue-limit c_lim (passive entry / both) | margin, sigma_day |
|---|---|---|---|---|---|---|---|---|---|---|
| C082 | topstep | MNQ | none / 2000.0 | 27.19 | 13:10, 12:30 | 150 vs 265.20 (below) | 0.000 | none | - | - |
| C083 | tradeify | MNQ | 1250.0 / 2000.0 | 16.99 | 13:45, 12:30 | 150 vs 265.20 (below) | 0.000 | none | 5.360 / 5.580 | - |
| C084 | mffu | MNQ | 1000.0 / 2000.0 | 13.60 | 13:10, 12:30 | 0 vs 265.20 (below) | 0.000 | none | - | - |
| C085 | lucid | MNQ | 1200.0 / 2000.0 | 16.32 | 13:45, 12:30 | 0 vs 265.20 (below) | 0.000 | none | 5.520 / 5.740 | - |
| C086 | ibkr | MNQ | none (own account) | - | none, 12:30 | - | 0 | none | not computed | intraday initial USD 4622.90 (overnight 6604.14); sigma_cc 699.90 ticks = USD 349.95 |

Data needed:

- MNQ: schema ohlcv-1m (NQ price path). Discovery 2020-12-01..2024-02-29 (39 months; bars owned: True); test no clean window of 36 months or more before 2024-03: every pre-2024-03 month of the underlying was read (census p_basis) and none is sealed; a test would need 2024-03 onward (not sealed for these codes; outside Q7's pre-2024-03 rule); clean test window 0.82 months (never read, unsealed: ['2010-06-06', '2010-07-01']). Cost (estimates): discovery USD 0.00, test USD 0.00, all USD 0.00; basis: no clean pre-2024-03 test window: nothing to buy before 2024-03. Quotes to obtain: none.
- Combination (sums over members; clean window = the shortest member's): discovery USD 0.00, all USD 0.00, clean test window 0.82 months.

### Dossier MNQ|F12: product MNQ, F12 expiry and option-hedging days

MNQ is NQ's satellite: MNQ's F3 statistics are NQ's (OC-1), MNQ settles from NQ's 30-s VWAP (EQUITY-22, -23, -24). NQ is excluded as a candidate (V49); NQ-based closed lines bind MNQ because the price path is the same (lead's instruction for this run).

*NASDAQ (Nasdaq-100)*

- Applies because: Monthly option expiries (3rd Friday) on the index; R2-F12 lists the equity codes (12 monthly expiries a year, 4 quarterly).
- Participant flow: Option market makers' delta hedging around expiry and their aggregate gamma; leveraged ETF rebalancing.
- Why predictable: Expiry calendars are fixed; dealer gamma is estimable from open interest (GEX).
- Why an edge could exist at retail size: Non-informational flow at a known date; events are few (monthly). One contract moves no price; at tens of milliseconds to a second without co-location only effects lasting minutes are reachable (information is priced within 1 to 5 s on ES, NQ, ZN, CL: E.25).
- Mechanism quote: none recorded in the R2 file for this family
- Documented horizon: expiry day into the close; 10-60 min conditioned on gamma (R2-F12)
- Timing: 3rd Friday of each month, into the 13:00 PT close; main session 06:30-13:00 PT (cash 09:30-16:00 ET, EQUITY-47/-49)
- Kind: event; events a year: 12 (12 monthly expiries a year, 4 quarterly (R2-F12 data needs)); trades per event: 1
- Absorption under 5 minutes (R2): Not applicable (calendar flow).
- Evidence rows (relation to this product; full rows in the catalog): F12.E01 (cousin (ES; V45 exception, untested); reused (E.25)); F12.E02 (other venue (US stocks and ETFs); full_text); F12.E03 (cousin (ES); reused)
- R1 overlap (closing sentences in the R1 catalog):
  - R1-14 (same underlying: NQ price path at MNQ cost): H6 T3: momentum into the close conditioned on negative prior-day GEX (134 trades). Reading: closed configuration (LR-R1: a closed configuration stays closed at every venue, the own broker included).
  - R1-23 (not product-specific): C2 GEX late-session momentum stopped at its power rule. Reading: a stop before any test, not a test (R1 ambiguity list).
  - R1-19 (cousin (ES)): V45 lists the ES 3rd-Friday reversal as an exception (never tested). Reading: evidence finding (R1-19), not a ban on new families (LR-R1).
- Open questions (R2): The 3rd-Friday reversal is published for ES only; no evidence on NQ, RTY or YM codes. | GEX data source and cost: not established here (DataAccess).

Band and horizon: documented horizon(s) [10, 60] min lie outside B (15-30 min) (documented [10, 30, 60] min). C087 h_c 30; C088 h_c 30; C089 h_c 30; C090 h_c 30; C091 h_c 30

Cost and power at h_c (ticks of the member's own tick; e80 = SR80 sqrt(T) sigma_hc / sqrt(K)):

| id | venue | band | h_c | member | c_f | sigma_hc | c_f/sigma | p_be emp / norm | p_1 emp / norm | K_year | K_disc | K_test | e80 disc G3+G4 / G3 / test | c_f + e80_test |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C087 | topstep | 15-30 | 30 | MNQ | 3.940 | 147.10 | 0.0268 | 0.5183 / 0.5168 | 0.5229 / 0.5210 | 12.0 | 37.9 | 41.4 | 155.62 / 136.50 / 130.53 | 134.47 |
| C088 | tradeify | 15-30 | 30 | MNQ | 5.140 | 147.10 | 0.0349 | 0.5238 / 0.5219 | 0.5284 / 0.5262 | 12.0 | 37.9 | 41.4 | 155.62 / 136.50 / 130.53 | 135.67 |
| C089 | mffu | 15-30 | 30 | MNQ | 5.300 | 147.10 | 0.0360 | 0.5246 / 0.5226 | 0.5292 / 0.5268 | 12.0 | 37.9 | 41.4 | 155.62 / 136.50 / 130.53 | 135.83 |
| C090 | lucid | 15-30 | 30 | MNQ | 5.300 | 147.10 | 0.0360 | 0.5246 / 0.5226 | 0.5292 / 0.5268 | 12.0 | 37.9 | 41.4 | 155.62 / 136.50 / 130.53 | 135.83 |
| C091 | ibkr | 15-30 | 30 | MNQ | 6.344 | 147.10 | 0.0431 | 0.5294 / 0.5270 | 0.5340 / 0.5313 | 12.0 | 37.9 | 41.4 | 155.62 / 136.50 / 130.53 | 136.87 |

Prop fit (one contract) and own-broker fit:

| id | venue | member | DLL (USD) / MLL | DLL/(sigma v) | flat-by-close PT, latest start | payout threshold vs sqrt(n/day) sigma v | news events a week | gates | queue-limit c_lim (passive entry / both) | margin, sigma_day |
|---|---|---|---|---|---|---|---|---|---|---|
| C087 | topstep | MNQ | none / 2000.0 | 27.19 | 13:10, 12:30 | 150 vs 16.05 (exceeds) | 0.000 | none | - | - |
| C088 | tradeify | MNQ | 1250.0 / 2000.0 | 16.99 | 13:45, 12:30 | 150 vs 16.05 (exceeds) | 0.000 | none | 5.360 / 5.580 | - |
| C089 | mffu | MNQ | 1000.0 / 2000.0 | 13.60 | 13:10, 12:30 | 0 vs 16.05 (below) | 0.000 | none | - | - |
| C090 | lucid | MNQ | 1200.0 / 2000.0 | 16.32 | 13:45, 12:30 | 0 vs 16.05 (below) | 0.000 | none | 5.520 / 5.740 | - |
| C091 | ibkr | MNQ | none (own account) | - | none, 12:30 | - | 0 | none | not computed | intraday initial USD 4622.90 (overnight 6604.14); sigma_cc 699.90 ticks = USD 349.95 |

Data needed:

- MNQ: schema ohlcv-1m (NQ price path). Discovery 2020-12-01..2024-02-29 (39 months; bars owned: True); test no clean window of 36 months or more before 2024-03: every pre-2024-03 month of the underlying was read (census p_basis) and none is sealed; a test would need 2024-03 onward (not sealed for these codes; outside Q7's pre-2024-03 rule); clean test window 0.82 months (never read, unsealed: ['2010-06-06', '2010-07-01']). Cost (estimates): discovery USD 0.00, test USD 0.00, all USD 0.00; basis: no clean pre-2024-03 test window: nothing to buy before 2024-03. Quotes to obtain: none. Not priced: option open interest by strike for a gamma-conditioned variant (GEX; vendor data, cost unknown; R1-14 used GEX rows 2020-05-29..2024-02-28); the 3rd-Friday variant needs bars and the expiry calendar only.
- Combination (sums over members; clean window = the shortest member's): discovery USD 0.00, all USD 0.00, clean test window 0.82 months.

### Dossier RTY|F01: product RTY, F01 intraday momentum into the close

M2K (micro sibling) is a survivor but not a top-15 code: no M2K combination (LR-R2a).

*RUSSELL (Russell 2000)*

- Applies because: Baltussen et al. 2021 define the effect on the cash-session close (EQUITY-49) and report a product row for this underlying (SB-8 YM, SB-9 NQ, SB-10 Russell).
- Participant flow: Gamma hedgers: option market makers short gamma and leveraged-ETF rebalancing trade in the direction of the day's move before the close (Baltussen et al. 2021); late-informed traders (Gao et al. 2018).
- Why predictable: The hedge size is set mechanically by the day's return and is executed near the close, a known time.
- Why an edge could exist at retail size: The flow is non-informational and large against a one-lot; the open issue is size per trade against cost (R1-14: NQ T1 gross 1.25 ticks against 4.08 cost). One contract moves no price; at tens of milliseconds to a second without co-location only effects lasting minutes are reachable (information is priced within 1 to 5 s on ES, NQ, ZN, CL: E.25).
- Mechanism quote: "Hedging short gamma exposure requires trading in the direction of price movements, thereby creating price momentum." (reports/stage_e13_briefs/pages/InfoSource/baltussen_etal_2021_jfe.md:84-85)
- Documented horizon: 30 min: entry at close-30, exit at the cash close (Baltussen et al.; EQUITY-49)
- Timing: entry 12:30 PT (14:30 CT), exit 13:00 PT (15:00 CT cash close); main session 06:30-13:00 PT (cash 09:30-16:00 ET, EQUITY-47/-49)
- Kind: daily; events a year: 252 (one trade a trade date (spec 9.2: 252 trade dates a year)); trades per event: 1
- Absorption under 5 minutes (R2): Not applicable as such: the effect is a 30-minute flow pattern. Contrary evidence is decay and regime change (EQUITY-39, -40, -41), not fast absorption.
- Evidence rows (relation to this product; full rows in the catalog): F01.E01 (asset-class pool (17 equity index futures, incl. Russell); full_text); F01.E02 (this underlying: Russell product row (SB-10; ICE then CME); full_text); F01.E04 (all products (cost statement); full_text); F01.E05 (other venue, same index (IWM OOS R2 2.43%); reused (E.20 full text)); F01.E06 (cash index, other index (S&P 500); reused); F01.E10 (cousin (ES); reused (full text)); F01.E11 (cash S&P 500 (pointer); reused); F01.E12 (index futures (abstract); abstract); F01.E13 (equity, bond and FX futures pool (abstract); abstract); F01.E14 (other product (NQ at MNQ cost; program test); reused (program record)); F01.E15 (pooled program test incl. RTY; reused)
- R1 overlap (closing sentences in the R1 catalog):
  - R1-13 (pooled incl. RTY (2017-06..2024-02)): E16-H1 settlement-window momentum and H4 reversal. Reading: closed configuration (LR-R1: a closed configuration stays closed at every venue, the own broker included).
  - R1-03 (M2K traded, RTY price path): K1-cp1-01 open-to-first-half-hour momentum port; exit by the exchange-set flat F per R1. Reading: closed configuration (LR-R1: a closed configuration stays closed at every venue, the own broker included).
  - R1-15 (this product (RTY searched)): E20S ML, r_ROD features, h60/h120/hF. Reading: closed configuration (LR-R1: a closed configuration stays closed at every venue, the own broker included).
  - R1-14 (other product (NQ)): H6 rest-of-day to last-half-hour momentum, entry 14:30 CT. Reading: family closed on another product (family overlap under LR-R1).
  - R1-11 (M2K tested): Gate 0 ML at h60, h120, hF. Reading: closed configuration (LR-R1: a closed configuration stays closed at every venue, the own broker included).
  - R1-23 (not product-specific): C2 GEX late-session momentum stopped at its power rule. Reading: a stop before any test, not a test (R1 ambiguity list).
- Open questions (R2): No per-product estimate after 2020-05 on any CME candidate; post-2018 equity evidence is regime-dependent (EQUITY-39) or a pointer (EQUITY-40). | No cost-adjusted per-product result; the only net statements are ES (one sentence) and SPY net of spread 2005-2013. | Micro codes, yield futures and mini grains were not in the sample; their price path is the full-size sibling's (settlement-derived), costs differ. | Whether a variant that differs from H6/E16-H1 (other products, conditioning) counts as a 'close variant' under R1 is for the lead and scorer.

Band and horizon: documented horizon inside B (documented [30] min). C092 h_c 30; C093 h_c 30; C094 h_c 30; C095 h_c 30; C096 h_c 30

Cost and power at h_c (ticks of the member's own tick; e80 = SR80 sqrt(T) sigma_hc / sqrt(K)):

| id | venue | band | h_c | member | c_f | sigma_hc | c_f/sigma | p_be emp / norm | p_1 emp / norm | K_year | K_disc | K_test | e80 disc G3+G4 / G3 / test | c_f + e80_test |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C092 | bulenox | 15-30 | 30 | RTY | 2.336 | 51.75 | 0.0451 | 0.5315 / 0.5283 | 0.5450 / 0.5404 | 252.0 | 796.0 | 870.0 | 11.95 / 10.48 / 10.02 | 12.36 |
| C093 | topstep | 15-30 | 30 | RTY | 2.256 | 51.75 | 0.0436 | 0.5304 / 0.5273 | 0.5439 / 0.5394 | 252.0 | 796.0 | 870.0 | 11.95 / 10.48 / 10.02 | 12.28 |
| C094 | tradeify | 15-30 | 30 | RTY | 2.652 | 51.75 | 0.0512 | 0.5357 / 0.5321 | 0.5492 / 0.5442 | 252.0 | 796.0 | 870.0 | 11.95 / 10.48 / 10.02 | 12.67 |
| C095 | mffu | 15-30 | 30 | RTY | 2.436 | 51.75 | 0.0471 | 0.5328 / 0.5295 | 0.5463 / 0.5416 | 252.0 | 796.0 | 870.0 | 11.95 / 10.48 / 10.02 | 12.46 |
| C096 | ibkr | 15-30 | 30 | RTY | 2.396 | 51.75 | 0.0463 | 0.5323 / 0.5290 | 0.5458 / 0.5411 | 252.0 | 796.0 | 870.0 | 11.95 / 10.48 / 10.02 | 12.42 |

Prop fit (one contract) and own-broker fit:

| id | venue | member | DLL (USD) / MLL | DLL/(sigma v) | flat-by-close PT, latest start | payout threshold vs sqrt(n/day) sigma v | news events a week | gates | queue-limit c_lim (passive entry / both) | margin, sigma_day |
|---|---|---|---|---|---|---|---|---|---|---|
| C092 | bulenox | RTY | none / 2500.0 | 9.66 | 13:59, 12:30 | 0 vs 258.76 (below) | 0.000 | none | 2.556 / 2.776 | - |
| C093 | topstep | RTY | none / 2000.0 | 7.73 | 13:10, 12:30 | 150 vs 258.76 (below) | 0.000 | none | - | - |
| C094 | tradeify | RTY | 1250.0 / 2000.0 | 4.83 | 13:45, 12:30 | 150 vs 258.76 (below) | 0.000 | none | 2.872 / 3.092 | - |
| C095 | mffu | RTY | 1000.0 / 2000.0 | 3.86 | 13:10, 12:30 | 0 vs 258.76 (below) | 0.000 | none | - | - |
| C096 | ibkr | RTY | none (own account) | - | none, 12:30 | - | 0 | none | not computed | intraday initial USD 8760.56 (overnight 12515.08); sigma_cc 237.81 ticks = USD 1189.04 |

Data needed:

- RTY: schema ohlcv-1m (RTY price path). Discovery 2020-12-01..2024-02-29 (39 months; bars owned: True); test no clean window of 36 months or more before 2024-03: every pre-2024-03 month of the underlying was read (census p_basis) and none is sealed; a test would need 2024-03 onward (not sealed for these codes; outside Q7's pre-2024-03 rule); clean test window 0.0 months (none: None). Cost (estimates): discovery USD 0.00, test USD 0.00, all USD 0.00; basis: no clean pre-2024-03 test window: nothing to buy before 2024-03. Quotes to obtain: none.
- Combination (sums over members; clean window = the shortest member's): discovery USD 0.00, all USD 0.00, clean test window 0.0 months.

### Dossier RTY|F04: product RTY, F04 US macro release drift

M2K (micro sibling) is a survivor but not a top-15 code: no M2K combination (LR-R2a).

*RUSSELL (Russell 2000)*

- Applies because: Scheduled US macro releases: NFP, CPI, PPI, GDP 08:30 ET; ISM 10:00 ET (EQUITY-16).
- Participant flow: Repricing of rate and growth expectations after a surprise; slower cross-asset digestion (copper, silver lags).
- Why predictable: Pre-announced calendar (EQUITY-16).
- Why an edge could exist at retail size: Only in the slower components: ES continuing adjustment 10-30 min (EQUITY-17) and the metals' delayed response (METALS-23); the jump itself is absorbed within seconds to a minute (RATES-19, -20; FX-22). One contract moves no price; at tens of milliseconds to a second without co-location only effects lasting minutes are reachable (information is priced within 1 to 5 s on ES, NQ, ZN, CL: E.25).
- Mechanism quote: none recorded in the R2 file for this family
- Documented horizon: entry 5-10 min after the release, exit 30-60 min (R2-F04); ES continuing adjustment t+10 to t+30 min (EQUITY-17)
- Timing: 08:30 ET releases (NFP, CPI, PPI, GDP) = 05:30 PT, BEFORE the main session (Globex pre-open); 10:00 ET releases (ISM) = 07:00 PT, inside; 09:15 ET (IP) = 06:15 PT, before (not counted: no calendar file); main session 06:30-13:00 PT (cash 09:30-16:00 ET, EQUITY-47/-49)
- Kind: event; events a year: 67.62 (326 releases in 4.821 years = 67.62 a year (reports/stage_e20_briefs/shared/macro_calendars.md section 3 (via EQUITY-16): counts in 2019-05-06..2024-02-29: NFP 57, CPI 58, PPI 58, GDP first and last 38, ISM services 57, ISM manufacturing 58)); trades per event: 1
- Absorption under 5 minutes (R2): Strongest of all families: rates (RATES-19, -20), FX (FX-21, -22), ES order flow (EQUITY-19), crypto (CRYPTO-27, -29), E.25 (1-5 seconds on ES, NQ, ZN, CL). Slower pieces: ES 10-30 min (weak joint test), copper and silver delays (2002-2008).
- Evidence rows (relation to this product; full rows in the catalog): F04.E03 (cousin (ES), 30 announcements, full text; full_text); F04.E01 (cousin (ES) and ZN, after NFP; full_text); F04.E08 (cousin (ES order flow, abstract); abstract)
- R1 overlap (closing sentences in the R1 catalog):
  - R1-01 (cousin (MES)): MES family E scheduled-macro and calendar windows. Reading: family closed on another product (family overlap under LR-R1).
  - R1-19 (this product (RTY in the 17-root census)): E.20 Part A census, macro-release effects included. Reading: evidence finding (R1-19), not a ban on new families (LR-R1).
- Open questions (R2): No post-2015 study shows a mean drift of 5 minutes or more after US macro releases in Treasury, FX or crypto futures (searched, not found: F2_rates, F2_fx, F2_crypto). | Firm news windows (Topstep Tier 1: CPI, NFP, PPI, FOMC; equity minis and GC SI HG blocked, MGC capped per planner pointer) may gate the core trade: FirmRules owns this.

Band and horizon: documented horizon(s) [60] min lie outside B (15-30 min) (documented [20, 30, 60] min). C097 h_c 30; C098 h_c 30; C099 h_c 30; C100 h_c 30; C101 h_c 30

Cost and power at h_c (ticks of the member's own tick; e80 = SR80 sqrt(T) sigma_hc / sqrt(K)):

| id | venue | band | h_c | member | c_f | sigma_hc | c_f/sigma | p_be emp / norm | p_1 emp / norm | K_year | K_disc | K_test | e80 disc G3+G4 / G3 / test | c_f + e80_test |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C097 | bulenox | 15-30 | 30 | RTY | 2.336 | 51.75 | 0.0451 | 0.5315 / 0.5283 | 0.5450 / 0.5404 | 67.6 | 213.6 | 233.4 | 23.06 / 20.23 / 19.34 | 21.68 |
| C098 | topstep | 15-30 | 30 | RTY | 2.256 | 51.75 | 0.0436 | 0.5304 / 0.5273 | 0.5439 / 0.5394 | 67.6 | 213.6 | 233.4 | 23.06 / 20.23 / 19.34 | 21.60 |
| C099 | tradeify | 15-30 | 30 | RTY | 2.652 | 51.75 | 0.0512 | 0.5357 / 0.5321 | 0.5492 / 0.5442 | 67.6 | 213.6 | 233.4 | 23.06 / 20.23 / 19.34 | 22.00 |
| C100 | mffu | 15-30 | 30 | RTY | 2.436 | 51.75 | 0.0471 | 0.5328 / 0.5295 | 0.5463 / 0.5416 | 67.6 | 213.6 | 233.4 | 23.06 / 20.23 / 19.34 | 21.78 |
| C101 | ibkr | 15-30 | 30 | RTY | 2.396 | 51.75 | 0.0463 | 0.5323 / 0.5290 | 0.5458 / 0.5411 | 67.6 | 213.6 | 233.4 | 23.06 / 20.23 / 19.34 | 21.74 |

Prop fit (one contract) and own-broker fit:

| id | venue | member | DLL (USD) / MLL | DLL/(sigma v) | flat-by-close PT, latest start | payout threshold vs sqrt(n/day) sigma v | news events a week | gates | queue-limit c_lim (passive entry / both) | margin, sigma_day |
|---|---|---|---|---|---|---|---|---|---|---|
| C097 | bulenox | RTY | none / 2500.0 | 9.66 | 13:59, 12:30 | 0 vs 134.03 (below) | 0.000 | none | 2.556 / 2.776 | - |
| C098 | topstep | RTY | none / 2000.0 | 7.73 | 13:10, 12:30 | 150 vs 134.03 (exceeds) | 0.688 | none | - | - |
| C099 | tradeify | RTY | 1250.0 / 2000.0 | 4.83 | 13:45, 12:30 | 150 vs 134.03 (exceeds) | 0.000 | none | 2.872 / 3.092 | - |
| C100 | mffu | RTY | 1000.0 / 2000.0 | 3.86 | 13:10, 12:30 | 0 vs 134.03 (below) | 0.000 | none | - | - |
| C101 | ibkr | RTY | none (own account) | - | none, 12:30 | - | 0 | none | not computed | intraday initial USD 8760.56 (overnight 12515.08); sigma_cc 237.81 ticks = USD 1189.04 |

Data needed:

- RTY: schema ohlcv-1m (RTY price path). Discovery 2020-12-01..2024-02-29 (39 months; bars owned: True); test no clean window of 36 months or more before 2024-03: every pre-2024-03 month of the underlying was read (census p_basis) and none is sealed; a test would need 2024-03 onward (not sealed for these codes; outside Q7's pre-2024-03 rule); clean test window 0.0 months (none: None). Cost (estimates): discovery USD 0.00, test USD 0.00, all USD 0.00; basis: no clean pre-2024-03 test window: nothing to buy before 2024-03. Quotes to obtain: none. Not priced: release calendar (E.20 frozen calendar covers 2019-05..2024-02 only; no 2010-2019 file for NFP, CPI, PPI, GDP, ISM: macro_calendars.md section 3); consensus forecasts only for a surprise-signed variant (vendor data, not owned, cost unknown).
- Combination (sums over members; clean window = the shortest member's): discovery USD 0.00, all USD 0.00, clean test window 0.0 months.

### Dossier RTY|F05: product RTY, F05 FOMC post-statement drift

M2K (micro sibling) is a survivor but not a top-15 code: no M2K combination (LR-R2a).

*RUSSELL (Russell 2000)*

- Applies because: Scheduled FOMC statements 14:00 ET, eight a year (EQUITY-16; R2-F05).
- Participant flow: Slow repricing of the policy path after the 14:00 ET statement and press conference; portfolio rebalancing over the afternoon.
- Why predictable: Eight scheduled meetings a year (FX-26 for frequency of ECB/RBA; FOMC 8/yr).
- Why an edge could exist at retail size: SR 1188 finds an unconditional, persistent yield decline for about 3 hours after the statement, a horizon a one-lot can reach. One contract moves no price; at tens of milliseconds to a second without co-location only effects lasting minutes are reachable (information is priced within 1 to 5 s on ES, NQ, ZN, CL: E.25).
- Mechanism quote: none recorded in the R2 file for this family
- Documented horizon: after the 14:00 ET statement to the close: FOMC-day last half-hour (15:30-16:00 ET), 75+ min after the statement (EQUITY-20); Treasury yields about 3 h (RATES-23)
- Timing: statement 11:00 PT (14:00 ET), press conference 11:30 PT; last half-hour 12:30-13:00 PT; main session 06:30-13:00 PT (cash 09:30-16:00 ET, EQUITY-47/-49)
- Kind: event; events a year: 8 (eight scheduled FOMC meetings a year (R2-F05 mechanism; frozen calendar 37 statements in 2019-05-06..2024-02-29, macro_calendars.md section 3)); trades per event: 1
- Absorption under 5 minutes (R2): Statement jump fast (E.25 for ZN); gold continues 5-10 min (METALS-25); rates drift persists about 3 h (RATES-23).
- Evidence rows (relation to this product; full rows in the catalog): F05.E02 (other venue (SPY), FOMC release days; reused); F05.E06 (cash S&P 500 and Treasuries: pre-FOMC drift (before the statement); reused / abstract); F05.E01 (other asset class (cash Treasury yields); reused (E.20 full text))
- R1 overlap (closing sentences in the R1 catalog):
  - R1-04 (other product (rates)): K2 post-FOMC member (Tier B, no confirmation). Reading: family closed on another product (family overlap under LR-R1).
  - R1-07 (other product (MGC)): K5-fomc-01, E.22 confirmation null. Reading: family closed on another product (family overlap under LR-R1).
  - R1-01 (cousin (MES)): MES family E scheduled-macro and calendar windows. Reading: family closed on another product (family overlap under LR-R1).
- Open questions (R2): Is SR 1188's 3-hour decline present in ZN/ZF futures after 2015 and net of costs? Not found. | FOMC is a Topstep Tier 1 event (planner pointer): whether rates are outside its window (pointer says 'energies, rates, FX unaffected') is FirmRules' fact.

Band and horizon: documented horizon(s) [120] min lie outside B (15-30 min) (documented [30, 120] min). C102 h_c 30; C103 h_c 30; C104 h_c 30; C105 h_c 30; C106 h_c 30

Cost and power at h_c (ticks of the member's own tick; e80 = SR80 sqrt(T) sigma_hc / sqrt(K)):

| id | venue | band | h_c | member | c_f | sigma_hc | c_f/sigma | p_be emp / norm | p_1 emp / norm | K_year | K_disc | K_test | e80 disc G3+G4 / G3 / test | c_f + e80_test |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C102 | bulenox | 15-30 | 30 | RTY | 2.336 | 51.75 | 0.0451 | 0.5315 / 0.5283 | 0.5450 / 0.5404 | 8.0 | 25.3 | 27.6 | 67.05 / 58.81 / 56.24 | 58.58 |
| C103 | topstep | 15-30 | 30 | RTY | 2.256 | 51.75 | 0.0436 | 0.5304 / 0.5273 | 0.5439 / 0.5394 | 8.0 | 25.3 | 27.6 | 67.05 / 58.81 / 56.24 | 58.50 |
| C104 | tradeify | 15-30 | 30 | RTY | 2.652 | 51.75 | 0.0512 | 0.5357 / 0.5321 | 0.5492 / 0.5442 | 8.0 | 25.3 | 27.6 | 67.05 / 58.81 / 56.24 | 58.89 |
| C105 | mffu | 15-30 | 30 | RTY | 2.436 | 51.75 | 0.0471 | 0.5328 / 0.5295 | 0.5463 / 0.5416 | 8.0 | 25.3 | 27.6 | 67.05 / 58.81 / 56.24 | 58.68 |
| C106 | ibkr | 15-30 | 30 | RTY | 2.396 | 51.75 | 0.0463 | 0.5323 / 0.5290 | 0.5458 / 0.5411 | 8.0 | 25.3 | 27.6 | 67.05 / 58.81 / 56.24 | 58.64 |

Prop fit (one contract) and own-broker fit:

| id | venue | member | DLL (USD) / MLL | DLL/(sigma v) | flat-by-close PT, latest start | payout threshold vs sqrt(n/day) sigma v | news events a week | gates | queue-limit c_lim (passive entry / both) | margin, sigma_day |
|---|---|---|---|---|---|---|---|---|---|---|
| C102 | bulenox | RTY | none / 2500.0 | 9.66 | 13:59, 12:30 | 0 vs 46.10 (below) | 0.000 | none | 2.556 / 2.776 | - |
| C103 | topstep | RTY | none / 2000.0 | 7.73 | 13:10, 12:30 | 150 vs 46.10 (exceeds) | 0.147 | none | - | - |
| C104 | tradeify | RTY | 1250.0 / 2000.0 | 4.83 | 13:45, 12:30 | 150 vs 46.10 (exceeds) | 0.000 | none | 2.872 / 3.092 | - |
| C105 | mffu | RTY | 1000.0 / 2000.0 | 3.86 | 13:10, 12:30 | 0 vs 46.10 (below) | 0.000 | none | - | - |
| C106 | ibkr | RTY | none (own account) | - | none, 12:30 | - | 0 | none | not computed | intraday initial USD 8760.56 (overnight 12515.08); sigma_cc 237.81 ticks = USD 1189.04 |

Data needed:

- RTY: schema ohlcv-1m (RTY price path). Discovery 2020-12-01..2024-02-29 (39 months; bars owned: True); test no clean window of 36 months or more before 2024-03: every pre-2024-03 month of the underlying was read (census p_basis) and none is sealed; a test would need 2024-03 onward (not sealed for these codes; outside Q7's pre-2024-03 rule); clean test window 0.0 months (none: None). Cost (estimates): discovery USD 0.00, test USD 0.00, all USD 0.00; basis: no clean pre-2024-03 test window: nothing to buy before 2024-03. Quotes to obtain: none. Not priced: FOMC statement dates and times (calendar files 2010-2024 exist: macro_calendars.md section 3).
- Combination (sums over members; clean window = the shortest member's): discovery USD 0.00, all USD 0.00, clean test window 0.0 months.

### Dossier RTY|F08: product RTY, F08 session and overnight-to-day handoff

M2K (micro sibling) is a survivor but not a top-15 code: no M2K combination (LR-R2a).

*RUSSELL (Russell 2000)*

- Applies because: Fixed session clocks: Globex Sun-Fri 18:00-17:00 ET, cash session 09:30-16:00 ET (EQUITY-47, EQUITY-49); European open 02:00-03:00 ET documented on the ES cousin (EQUITY-50).
- Participant flow: Local-hours hedging and order imbalances carried over from the prior close (Boyarchenko et al.: 2:00-3:00 ET returns linked to prior US-close imbalances); overnight news priced at the reopen.
- Why predictable: Fixed session clocks (Globex pauses: grains 07:45-08:30 CT, GRAINS-14; daily 16:00-17:00 CT halts).
- Why an edge could exist at retail size: Hours-scale holds around a known clock; most documented versions are gross or negative after spreads. One contract moves no price; at tens of milliseconds to a second without co-location only effects lasting minutes are reachable (information is priced within 1 to 5 s on ES, NQ, ZN, CL: E.25).
- Mechanism quote: none recorded in the R2 file for this family
- Documented horizon: European open 02:00-03:00 ET, 60 min (EQUITY-50); the cash-open first half-hour as the predictor of the close (F01.E05)
- Timing: European open 23:00-00:00 PT (prior evening, Globex, outside the main session); cash open 06:30 PT; main session 06:30-13:00 PT (cash 09:30-16:00 ET, EQUITY-47/-49)
- Kind: daily; events a year: 252 (one trade a trade date); trades per event: 1
- Absorption under 5 minutes (R2): Not the issue here; the evidence that exists is either gross, pre-2013, other-venue, or negative after spreads (EQUITY-51) or arbitraged after a venue change (GRAINS-42, GRAINS-17).
- Evidence rows (relation to this product; full rows in the catalog): F08.E03 (cousin (ES), European open 02:00-03:00 ET; full_text); F01.E05 (other venue (SPY): first half-hour predicts the last half-hour (listed under F01; the open-to-close handoff); reused (E.20 full text))
- R1 overlap (closing sentences in the R1 catalog):
  - R1-03 (M2K traded, RTY price path): K1-cp3-01 prior-day close-location (08:30 CT entry; exit by the exchange-set flat F per R1). Reading: closed configuration (LR-R1: a closed configuration stays closed at every venue, the own broker included).
  - R1-13 (pooled incl. RTY): E16-H4 next-day reversal of the settlement-window move. Reading: closed configuration (LR-R1: a closed configuration stays closed at every venue, the own broker included).
  - R1-01 (cousin (MES)): families A (clock windows) and D (gaps), incl. European-open drift. Reading: family closed on another product (family overlap under LR-R1).
- Open questions (R2): No post-2010 futures test of the local-hours currency effect on 6E/6A net of a futures round trip. | Grains 08:30 CT reopen after the 07:45-08:30 pause: untested (planner family 4), and Export Sales lands at 07:30 CT just before the pause (GRAINS-22).

Band and horizon: documented horizon(s) [60] min lie outside B (15-30 min) (documented [30, 60] min). C107 h_c 30; C108 h_c 30; C109 h_c 30; C110 h_c 30; C111 h_c 30

Cost and power at h_c (ticks of the member's own tick; e80 = SR80 sqrt(T) sigma_hc / sqrt(K)):

| id | venue | band | h_c | member | c_f | sigma_hc | c_f/sigma | p_be emp / norm | p_1 emp / norm | K_year | K_disc | K_test | e80 disc G3+G4 / G3 / test | c_f + e80_test |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C107 | bulenox | 15-30 | 30 | RTY | 2.336 | 51.75 | 0.0451 | 0.5315 / 0.5283 | 0.5450 / 0.5404 | 252.0 | 796.0 | 870.0 | 11.95 / 10.48 / 10.02 | 12.36 |
| C108 | topstep | 15-30 | 30 | RTY | 2.256 | 51.75 | 0.0436 | 0.5304 / 0.5273 | 0.5439 / 0.5394 | 252.0 | 796.0 | 870.0 | 11.95 / 10.48 / 10.02 | 12.28 |
| C109 | tradeify | 15-30 | 30 | RTY | 2.652 | 51.75 | 0.0512 | 0.5357 / 0.5321 | 0.5492 / 0.5442 | 252.0 | 796.0 | 870.0 | 11.95 / 10.48 / 10.02 | 12.67 |
| C110 | mffu | 15-30 | 30 | RTY | 2.436 | 51.75 | 0.0471 | 0.5328 / 0.5295 | 0.5463 / 0.5416 | 252.0 | 796.0 | 870.0 | 11.95 / 10.48 / 10.02 | 12.46 |
| C111 | ibkr | 15-30 | 30 | RTY | 2.396 | 51.75 | 0.0463 | 0.5323 / 0.5290 | 0.5458 / 0.5411 | 252.0 | 796.0 | 870.0 | 11.95 / 10.48 / 10.02 | 12.42 |

Prop fit (one contract) and own-broker fit:

| id | venue | member | DLL (USD) / MLL | DLL/(sigma v) | flat-by-close PT, latest start | payout threshold vs sqrt(n/day) sigma v | news events a week | gates | queue-limit c_lim (passive entry / both) | margin, sigma_day |
|---|---|---|---|---|---|---|---|---|---|---|
| C107 | bulenox | RTY | none / 2500.0 | 9.66 | 13:59, 12:30 | 0 vs 258.76 (below) | 0.000 | none | 2.556 / 2.776 | - |
| C108 | topstep | RTY | none / 2000.0 | 7.73 | 13:10, 12:30 | 150 vs 258.76 (below) | 0.000 | none | - | - |
| C109 | tradeify | RTY | 1250.0 / 2000.0 | 4.83 | 13:45, 12:30 | 150 vs 258.76 (below) | 0.000 | none | 2.872 / 3.092 | - |
| C110 | mffu | RTY | 1000.0 / 2000.0 | 3.86 | 13:10, 12:30 | 0 vs 258.76 (below) | 0.000 | none | - | - |
| C111 | ibkr | RTY | none (own account) | - | none, 12:30 | - | 0 | none | not computed | intraday initial USD 8760.56 (overnight 12515.08); sigma_cc 237.81 ticks = USD 1189.04 |

Data needed:

- RTY: schema ohlcv-1m (RTY price path). Discovery 2020-12-01..2024-02-29 (39 months; bars owned: True); test no clean window of 36 months or more before 2024-03: every pre-2024-03 month of the underlying was read (census p_basis) and none is sealed; a test would need 2024-03 onward (not sealed for these codes; outside Q7's pre-2024-03 rule); clean test window 0.0 months (none: None). Cost (estimates): discovery USD 0.00, test USD 0.00, all USD 0.00; basis: no clean pre-2024-03 test window: nothing to buy before 2024-03. Quotes to obtain: none.
- Combination (sums over members; clean window = the shortest member's): discovery USD 0.00, all USD 0.00, clean test window 0.0 months.

### Dossier RTY|F09: product RTY, F09 cross-market lead-lag

M2K (micro sibling) is a survivor but not a top-15 code: no M2K combination (LR-R2a).

*RUSSELL (Russell 2000)*

- Applies because: EQUITY-13: NQ leads Russell 2000 futures by about 8-11 min at 60-min chart extrema (preprint, 2004-2014, no trading test); RTY is the follower.
- Participant flow: Hedgers and spread traders anchoring an economic relation (crush margin); information arriving first in the deeper market and propagating.
- Why predictable: Cointegrated legs revert; a leader's move precedes a laggard's.
- Why an edge could exist at retail size: Only where the lag or the reversion lasts minutes to hours: seconds-scale lead-lag cannot pay at retail latency (E.32 verdict table, M2 b). One contract moves no price; at tens of milliseconds to a second without co-location only effects lasting minutes are reachable (information is priced within 1 to 5 s on ES, NQ, ZN, CL: E.25).
- Mechanism quote: none recorded in the R2 file for this family
- Documented horizon: NQ leads Russell by about 8-11 min at 60-min chart extrema (EQUITY-13); no trading test
- Timing: any time in the main session; main session 06:30-13:00 PT (cash 09:30-16:00 ET, EQUITY-47/-49)
- Kind: continuous; events a year: - (continuous: n_cap(h_c) a day); trades per event: -
- Absorption under 5 minutes (R2): Cross-venue and mechanical links are seconds or milliseconds (CRUDE-33, RATES-17, GRAINS-24); silver->gold at 1 minute (METALS-37). Minute-to-hour structure exists only for the crush (cointegration, no half-life) and the NQ/Russell extrema lags (preprint).
- Evidence rows (relation to this product; full rows in the catalog): F09.E06 (this underlying (Russell 2000 futures, ICE then) as the follower of NQ; full_text); F09.E10 (mechanical pairs (M2K-RTY): arbitrage-tight, no directional edge; full_text / reused)
- R1 overlap (closing sentences in the R1 catalog):
  - R1-10 (other products (MGC with MES leg, 6C with MCL leg, MNQ with MBT leg)): K8 cross-market screen: equity flight into gold, oil/CAD, weekend bitcoin to NQ. Reading: family closed on another product (family overlap under LR-R1).
  - R1-13 (other products (NQ vs ZN)): E16-H2 month-end NQ vs ZN pair. Reading: family closed on another product (family overlap under LR-R1).
  - R1-21 (other product (ZM)): S1 crush residual and S2 cross-asset propagation from ZS and ZL. Reading: E.33c family closed on ZM; on this product family overlap (LR-R1).
- Open questions (R2): Crush residual reversion with ZS or ZL (not ZM) as the traded leg: not tested by the program; no published intraday half-life. | No minute-level study of calendar-spread reversion for CL, NG or Treasuries; Treasury curve spreads (FIT/FYT, TUF, NOB, RATES-14) have no intraday study.

Band and horizon: documented horizon(s) [10, 60] min lie outside B (15-30 min) (documented [10, 60] min). C112 h_c 30 (h_c not a documented horizon); C113 h_c 30 (h_c not a documented horizon); C114 h_c 30 (h_c not a documented horizon); C115 h_c 30 (h_c not a documented horizon); C116 h_c 30 (h_c not a documented horizon)

Cost and power at h_c (ticks of the member's own tick; e80 = SR80 sqrt(T) sigma_hc / sqrt(K)):

| id | venue | band | h_c | member | c_f | sigma_hc | c_f/sigma | p_be emp / norm | p_1 emp / norm | K_year | K_disc | K_test | e80 disc G3+G4 / G3 / test | c_f + e80_test |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C112 | bulenox | 15-30 | 30 | RTY | 2.336 | 51.75 | 0.0451 | 0.5315 / 0.5283 | 0.5450 / 0.5404 | 3276.0 | 10348.0 | 11310.0 | 3.31 / 2.91 / 2.78 | 5.12 |
| C113 | topstep | 15-30 | 30 | RTY | 2.256 | 51.75 | 0.0436 | 0.5304 / 0.5273 | 0.5439 / 0.5394 | 3276.0 | 10348.0 | 11310.0 | 3.31 / 2.91 / 2.78 | 5.04 |
| C114 | tradeify | 15-30 | 30 | RTY | 2.652 | 51.75 | 0.0512 | 0.5357 / 0.5321 | 0.5492 / 0.5442 | 3276.0 | 10348.0 | 11310.0 | 3.31 / 2.91 / 2.78 | 5.43 |
| C115 | mffu | 15-30 | 30 | RTY | 2.436 | 51.75 | 0.0471 | 0.5328 / 0.5295 | 0.5463 / 0.5416 | 3276.0 | 10348.0 | 11310.0 | 3.31 / 2.91 / 2.78 | 5.22 |
| C116 | ibkr | 15-30 | 30 | RTY | 2.396 | 51.75 | 0.0463 | 0.5323 / 0.5290 | 0.5458 / 0.5411 | 3276.0 | 10348.0 | 11310.0 | 3.31 / 2.91 / 2.78 | 5.18 |

Prop fit (one contract) and own-broker fit:

| id | venue | member | DLL (USD) / MLL | DLL/(sigma v) | flat-by-close PT, latest start | payout threshold vs sqrt(n/day) sigma v | news events a week | gates | queue-limit c_lim (passive entry / both) | margin, sigma_day |
|---|---|---|---|---|---|---|---|---|---|---|
| C112 | bulenox | RTY | none / 2500.0 | 9.66 | 13:59, 12:30 | 0 vs 932.96 (below) | 0.000 | none | 2.556 / 2.776 | - |
| C113 | topstep | RTY | none / 2000.0 | 7.73 | 13:10, 12:30 | 150 vs 932.96 (below) | 0.835 | none | - | - |
| C114 | tradeify | RTY | 1250.0 / 2000.0 | 4.83 | 13:45, 12:30 | 150 vs 932.96 (below) | 0.000 | none | 2.872 / 3.092 | - |
| C115 | mffu | RTY | 1000.0 / 2000.0 | 3.86 | 13:10, 12:30 | 0 vs 932.96 (below) | 0.000 | none | - | - |
| C116 | ibkr | RTY | none (own account) | - | none, 12:30 | - | 0 | none | not computed | intraday initial USD 8760.56 (overnight 12515.08); sigma_cc 237.81 ticks = USD 1189.04 |

Data needed:

- RTY: schema ohlcv-1m (RTY price path) + NQ leader bars. Discovery 2020-12-01..2024-02-29 (39 months; bars owned: True); test no clean window of 36 months or more before 2024-03: every pre-2024-03 month of the underlying was read (census p_basis) and none is sealed; a test would need 2024-03 onward (not sealed for these codes; outside Q7's pre-2024-03 rule); clean test window 0.0 months (none: None). Cost (estimates): discovery USD 0.00, test USD 0.00, all USD 0.00; basis: no clean pre-2024-03 test window: nothing to buy before 2024-03; leader leg NQ ohlcv-1m owned 2010-06..2024-02 (read). Quotes to obtain: none. Not priced: leader leg bars: NQ ohlcv-1m for RTY (owned 2010-06..2024-02); crush legs: ZS and ZM bars for ZL.
- Combination (sums over members; clean window = the shortest member's): discovery USD 0.00, all USD 0.00, clean test window 0.0 months.

### Dossier RTY|F10: product RTY, F10 order-book state at 5 min and longer

M2K (micro sibling) is a survivor but not a top-15 code: no M2K combination (LR-R2a).

*RUSSELL (Russell 2000)*

- Applies because: Order-book data exist for purchase: Databento GLBX.MDP3 MBO from 2017-05-21, MBP-10 before (F2_data_access databento_dataset); the code's MBO start is in the data plan.
- Participant flow: Large orders worked over time (sign persistence) and liquidity shocks followed by refill.
- Why predictable: Imbalance and sign persistence are autocorrelated.
- Why an edge could exist at retail size: Weak: forward predictability decays to insignificance by 5-30 minutes and sign persistence is offset by asymmetric liquidity (E.32 M1). One contract moves no price; at tens of milliseconds to a second without co-location only effects lasting minutes are reachable (information is priced within 1 to 5 s on ES, NQ, ZN, CL: E.25).
- Mechanism quote: none recorded in the R2 file for this family
- Documented horizon: 5-30 min forward (R2-F10); forward predictability insignificant by 5-30 min (F10.E01)
- Timing: any time in the main session; main session 06:30-13:00 PT (cash 09:30-16:00 ET, EQUITY-47/-49)
- Kind: continuous; events a year: - (continuous: n_cap(h_c) a day); trades per event: -
- Absorption under 5 minutes (R2): Central: E.32 M1 (contemporaneous far stronger than forward), Kolm et al. (seconds), E.25 (1-5 seconds on ES, NQ, ZN, CL).
- Evidence rows (relation to this product; full rows in the catalog): F10.E01 (other asset class (NYSE stocks); full_text (E.32 M1)); F10.E02 (equities (abstract); abstract); F10.E06 (cousin (ES): net gamma conditions order-flow reversals; reused (full text)); F10.E07 (other product (ZM), program test; reused); F10.E08 (excluded sub-5-minute items (NQ among them); abstract/reused)
- R1 overlap (closing sentences in the R1 catalog):
  - R1-21 (other product (ZM)): S3 ZM order flow and book state at 5-60 min. Reading: E.33c family closed on ZM; on this product family overlap (LR-R1).
  - R1-20 (execution line (ZM measured)): passive spread capture at the touch, one lot. Reading: execution line: passive spread capture closed (V50); limit orders stay allowed as execution of a signal.
  - R1-11 (M2K tested): ML on 1-minute bar features (no book data). Reading: closed configuration (LR-R1: a closed configuration stays closed at every venue, the own broker included).
- Open questions (R2): No CME-product study of forward order-flow predictability at 5 minutes or more found outside ZM's own null. | Drift-burst reversal after removing the look-ahead: untested.

Band and horizon: documented horizon(s) [5] min lie outside B (15-30 min) (documented [5, 15, 30] min). C117 h_c 30; C118 h_c 30; C119 h_c 30; C120 h_c 30; C121 h_c 30

Cost and power at h_c (ticks of the member's own tick; e80 = SR80 sqrt(T) sigma_hc / sqrt(K)):

| id | venue | band | h_c | member | c_f | sigma_hc | c_f/sigma | p_be emp / norm | p_1 emp / norm | K_year | K_disc | K_test | e80 disc G3+G4 / G3 / test | c_f + e80_test |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C117 | bulenox | 15-30 | 30 | RTY | 2.336 | 51.75 | 0.0451 | 0.5315 / 0.5283 | 0.5450 / 0.5404 | 3276.0 | 10348.0 | 11310.0 | 3.31 / 2.91 / 2.78 | 5.12 |
| C118 | topstep | 15-30 | 30 | RTY | 2.256 | 51.75 | 0.0436 | 0.5304 / 0.5273 | 0.5439 / 0.5394 | 3276.0 | 10348.0 | 11310.0 | 3.31 / 2.91 / 2.78 | 5.04 |
| C119 | tradeify | 15-30 | 30 | RTY | 2.652 | 51.75 | 0.0512 | 0.5357 / 0.5321 | 0.5492 / 0.5442 | 3276.0 | 10348.0 | 11310.0 | 3.31 / 2.91 / 2.78 | 5.43 |
| C120 | mffu | 15-30 | 30 | RTY | 2.436 | 51.75 | 0.0471 | 0.5328 / 0.5295 | 0.5463 / 0.5416 | 3276.0 | 10348.0 | 11310.0 | 3.31 / 2.91 / 2.78 | 5.22 |
| C121 | ibkr | 15-30 | 30 | RTY | 2.396 | 51.75 | 0.0463 | 0.5323 / 0.5290 | 0.5458 / 0.5411 | 3276.0 | 10348.0 | 11310.0 | 3.31 / 2.91 / 2.78 | 5.18 |

Prop fit (one contract) and own-broker fit:

| id | venue | member | DLL (USD) / MLL | DLL/(sigma v) | flat-by-close PT, latest start | payout threshold vs sqrt(n/day) sigma v | news events a week | gates | queue-limit c_lim (passive entry / both) | margin, sigma_day |
|---|---|---|---|---|---|---|---|---|---|---|
| C117 | bulenox | RTY | none / 2500.0 | 9.66 | 13:59, 12:30 | 0 vs 932.96 (below) | 0.000 | none | 2.556 / 2.776 | - |
| C118 | topstep | RTY | none / 2000.0 | 7.73 | 13:10, 12:30 | 150 vs 932.96 (below) | 0.835 | none | - | - |
| C119 | tradeify | RTY | 1250.0 / 2000.0 | 4.83 | 13:45, 12:30 | 150 vs 932.96 (below) | 0.000 | none | 2.872 / 3.092 | - |
| C120 | mffu | RTY | 1000.0 / 2000.0 | 3.86 | 13:10, 12:30 | 0 vs 932.96 (below) | 0.000 | none | - | - |
| C121 | ibkr | RTY | none (own account) | - | none, 12:30 | - | 0 | none | not computed | intraday initial USD 8760.56 (overnight 12515.08); sigma_cc 237.81 ticks = USD 1189.04 |

Data needed:

- RTY: schema mbo (RTY; MBO from 2017-07-10). Discovery 2020-12-01..2024-02-29 (39 months; bars owned: True); test no clean window of 36 months or more before 2024-03: every pre-2024-03 month of the underlying was read (census p_basis) and none is sealed; a test would need 2024-03 onward (not sealed for these codes; outside Q7's pre-2024-03 rule); clean test window 0.0 months (none: None). Cost (estimates): discovery USD 280.54, test USD 0.00, all USD 280.54; basis: census estimate k = USD 7.1933/month (F2_data_access codes.RTY.k_usd_month, scaled from mbp-1 (estimate)) x months. Quotes to obtain: GLBX.MDP3 mbo RTY.v.0 2020-12-01..2024-02-29. Not priced: MBP-10 is the highest granularity before 2017-05-21 (F2_data_access databento_dataset).
- Combination (sums over members; clean window = the shortest member's): discovery USD 280.54, all USD 280.54, clean test window 0.0 months.

### Dossier RTY|F11: product RTY, F11 own-price-path trend and reversal

M2K (micro sibling) is a survivor but not a top-15 code: no M2K combination (LR-R2a).

*RUSSELL (Russell 2000)*

- Applies because: R2-F11 applies to any code (own price path on 1-minute bars).
- Participant flow: Trend followers and stop cascades (trend); liquidity-provider inventory correction (reversion).
- Why predictable: Price-path autocorrelation by horizon (reversion 2-16 min, weak trend at 1 h or more).
- Why an edge could exist at retail size: Generic and crowded; the published sizes are tiny (out-of-sample R2 under 1 bp). One contract moves no price; at tens of milliseconds to a second without co-location only effects lasting minutes are reachable (information is priced within 1 to 5 s on ES, NQ, ZN, CL: E.25).
- Mechanism quote: none recorded in the R2 file for this family
- Documented horizon: reversion 2-16 min; weak trend at 1 h or more (F11.E01)
- Timing: any time in the main session; main session 06:30-13:00 PT (cash 09:30-16:00 ET, EQUITY-47/-49)
- Kind: continuous; events a year: - (continuous: n_cap(h_c) a day); trades per event: -
- Absorption under 5 minutes (R2): Short reversion is at 2-16 min and tiny (CRUDE-40); Brent inefficiency vanishes past 10 min (CRUDE-54).
- Evidence rows (relation to this product; full rows in the catalog): F11.E01 (futures pool (16-24 futures; equity-index membership not recorded); full_text); F11.E09 (other venue (SPY), noise-area momentum; reused); F11.E10 (other underlying (MNQ 5-min, NQ 15-min), preprints; reused / full_text)
- R1 overlap (closing sentences in the R1 catalog):
  - R1-03 (M2K traded, RTY price path): K1-cp2-01 opening-range breakout; exit by the exchange-set flat F per R1. Reading: closed configuration (LR-R1: a closed configuration stays closed at every venue, the own broker included).
  - R1-01 (cousin (MES)): families B, C, G, H. Reading: family closed on another product (family overlap under LR-R1).
  - R1-11 (M2K tested): Gate 0 ML over 64 bar features at h60, h120, hF. Reading: closed configuration (LR-R1: a closed configuration stays closed at every venue, the own broker included).
  - R1-15 (this product (RTY searched)): E20S ML, 36 bar features, h60/h120/hF. Reading: closed configuration (LR-R1: a closed configuration stays closed at every venue, the own broker included).
  - R1-21 (other product (ZM)): S4 ZM own price path at 5-60 min. Reading: E.33c family closed on ZM; on this product family overlap (LR-R1).
- Open questions (R2): Every generic price-path family has been screened by the program on 1-minute bars; a new one would be a close variant unless the product or mechanism differs (scorer's call).

Band and horizon: documented horizon(s) [5, 60] min lie outside B (15-30 min) (documented [5, 15, 60] min). C122 h_c 30 (h_c not a documented horizon); C123 h_c 30 (h_c not a documented horizon); C124 h_c 30 (h_c not a documented horizon); C125 h_c 30 (h_c not a documented horizon); C126 h_c 30 (h_c not a documented horizon)

Cost and power at h_c (ticks of the member's own tick; e80 = SR80 sqrt(T) sigma_hc / sqrt(K)):

| id | venue | band | h_c | member | c_f | sigma_hc | c_f/sigma | p_be emp / norm | p_1 emp / norm | K_year | K_disc | K_test | e80 disc G3+G4 / G3 / test | c_f + e80_test |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C122 | bulenox | 15-30 | 30 | RTY | 2.336 | 51.75 | 0.0451 | 0.5315 / 0.5283 | 0.5450 / 0.5404 | 3276.0 | 10348.0 | 11310.0 | 3.31 / 2.91 / 2.78 | 5.12 |
| C123 | topstep | 15-30 | 30 | RTY | 2.256 | 51.75 | 0.0436 | 0.5304 / 0.5273 | 0.5439 / 0.5394 | 3276.0 | 10348.0 | 11310.0 | 3.31 / 2.91 / 2.78 | 5.04 |
| C124 | tradeify | 15-30 | 30 | RTY | 2.652 | 51.75 | 0.0512 | 0.5357 / 0.5321 | 0.5492 / 0.5442 | 3276.0 | 10348.0 | 11310.0 | 3.31 / 2.91 / 2.78 | 5.43 |
| C125 | mffu | 15-30 | 30 | RTY | 2.436 | 51.75 | 0.0471 | 0.5328 / 0.5295 | 0.5463 / 0.5416 | 3276.0 | 10348.0 | 11310.0 | 3.31 / 2.91 / 2.78 | 5.22 |
| C126 | ibkr | 15-30 | 30 | RTY | 2.396 | 51.75 | 0.0463 | 0.5323 / 0.5290 | 0.5458 / 0.5411 | 3276.0 | 10348.0 | 11310.0 | 3.31 / 2.91 / 2.78 | 5.18 |

Prop fit (one contract) and own-broker fit:

| id | venue | member | DLL (USD) / MLL | DLL/(sigma v) | flat-by-close PT, latest start | payout threshold vs sqrt(n/day) sigma v | news events a week | gates | queue-limit c_lim (passive entry / both) | margin, sigma_day |
|---|---|---|---|---|---|---|---|---|---|---|
| C122 | bulenox | RTY | none / 2500.0 | 9.66 | 13:59, 12:30 | 0 vs 932.96 (below) | 0.000 | none | 2.556 / 2.776 | - |
| C123 | topstep | RTY | none / 2000.0 | 7.73 | 13:10, 12:30 | 150 vs 932.96 (below) | 0.835 | none | - | - |
| C124 | tradeify | RTY | 1250.0 / 2000.0 | 4.83 | 13:45, 12:30 | 150 vs 932.96 (below) | 0.000 | none | 2.872 / 3.092 | - |
| C125 | mffu | RTY | 1000.0 / 2000.0 | 3.86 | 13:10, 12:30 | 0 vs 932.96 (below) | 0.000 | none | - | - |
| C126 | ibkr | RTY | none (own account) | - | none, 12:30 | - | 0 | none | not computed | intraday initial USD 8760.56 (overnight 12515.08); sigma_cc 237.81 ticks = USD 1189.04 |

Data needed:

- RTY: schema ohlcv-1m (RTY price path). Discovery 2020-12-01..2024-02-29 (39 months; bars owned: True); test no clean window of 36 months or more before 2024-03: every pre-2024-03 month of the underlying was read (census p_basis) and none is sealed; a test would need 2024-03 onward (not sealed for these codes; outside Q7's pre-2024-03 rule); clean test window 0.0 months (none: None). Cost (estimates): discovery USD 0.00, test USD 0.00, all USD 0.00; basis: no clean pre-2024-03 test window: nothing to buy before 2024-03. Quotes to obtain: none.
- Combination (sums over members; clean window = the shortest member's): discovery USD 0.00, all USD 0.00, clean test window 0.0 months.

### Dossier RTY|F12: product RTY, F12 expiry and option-hedging days

M2K (micro sibling) is a survivor but not a top-15 code: no M2K combination (LR-R2a).

*RUSSELL (Russell 2000)*

- Applies because: Monthly option expiries (3rd Friday) on the index; R2-F12 lists the equity codes (12 monthly expiries a year, 4 quarterly).
- Participant flow: Option market makers' delta hedging around expiry and their aggregate gamma; leveraged ETF rebalancing.
- Why predictable: Expiry calendars are fixed; dealer gamma is estimable from open interest (GEX).
- Why an edge could exist at retail size: Non-informational flow at a known date; events are few (monthly). One contract moves no price; at tens of milliseconds to a second without co-location only effects lasting minutes are reachable (information is priced within 1 to 5 s on ES, NQ, ZN, CL: E.25).
- Mechanism quote: none recorded in the R2 file for this family
- Documented horizon: expiry day into the close; 10-60 min conditioned on gamma (R2-F12)
- Timing: 3rd Friday of each month, into the 13:00 PT close; main session 06:30-13:00 PT (cash 09:30-16:00 ET, EQUITY-47/-49)
- Kind: event; events a year: 12 (12 monthly expiries a year, 4 quarterly (R2-F12 data needs)); trades per event: 1
- Absorption under 5 minutes (R2): Not applicable (calendar flow).
- Evidence rows (relation to this product; full rows in the catalog): F12.E01 (cousin (ES; V45 exception, untested); reused (E.25)); F12.E02 (other venue (US stocks and ETFs); full_text); F12.E03 (cousin (ES); reused)
- R1 overlap (closing sentences in the R1 catalog):
  - R1-14 (other product (NQ)): H6 T3: momentum conditioned on negative prior-day GEX. Reading: family closed on another product (family overlap under LR-R1).
  - R1-23 (not product-specific): C2 GEX late-session momentum stopped at its power rule. Reading: a stop before any test, not a test (R1 ambiguity list).
  - R1-19 (cousin (ES)): V45 lists the ES 3rd-Friday reversal as an exception (never tested). Reading: evidence finding (R1-19), not a ban on new families (LR-R1).
- Open questions (R2): The 3rd-Friday reversal is published for ES only; no evidence on NQ, RTY or YM codes. | GEX data source and cost: not established here (DataAccess).

Band and horizon: documented horizon(s) [10, 60] min lie outside B (15-30 min) (documented [10, 30, 60] min). C127 h_c 30; C128 h_c 30; C129 h_c 30; C130 h_c 30; C131 h_c 30

Cost and power at h_c (ticks of the member's own tick; e80 = SR80 sqrt(T) sigma_hc / sqrt(K)):

| id | venue | band | h_c | member | c_f | sigma_hc | c_f/sigma | p_be emp / norm | p_1 emp / norm | K_year | K_disc | K_test | e80 disc G3+G4 / G3 / test | c_f + e80_test |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C127 | bulenox | 15-30 | 30 | RTY | 2.336 | 51.75 | 0.0451 | 0.5315 / 0.5283 | 0.5450 / 0.5404 | 12.0 | 37.9 | 41.4 | 54.75 / 48.02 / 45.92 | 48.26 |
| C128 | topstep | 15-30 | 30 | RTY | 2.256 | 51.75 | 0.0436 | 0.5304 / 0.5273 | 0.5439 / 0.5394 | 12.0 | 37.9 | 41.4 | 54.75 / 48.02 / 45.92 | 48.18 |
| C129 | tradeify | 15-30 | 30 | RTY | 2.652 | 51.75 | 0.0512 | 0.5357 / 0.5321 | 0.5492 / 0.5442 | 12.0 | 37.9 | 41.4 | 54.75 / 48.02 / 45.92 | 48.57 |
| C130 | mffu | 15-30 | 30 | RTY | 2.436 | 51.75 | 0.0471 | 0.5328 / 0.5295 | 0.5463 / 0.5416 | 12.0 | 37.9 | 41.4 | 54.75 / 48.02 / 45.92 | 48.36 |
| C131 | ibkr | 15-30 | 30 | RTY | 2.396 | 51.75 | 0.0463 | 0.5323 / 0.5290 | 0.5458 / 0.5411 | 12.0 | 37.9 | 41.4 | 54.75 / 48.02 / 45.92 | 48.32 |

Prop fit (one contract) and own-broker fit:

| id | venue | member | DLL (USD) / MLL | DLL/(sigma v) | flat-by-close PT, latest start | payout threshold vs sqrt(n/day) sigma v | news events a week | gates | queue-limit c_lim (passive entry / both) | margin, sigma_day |
|---|---|---|---|---|---|---|---|---|---|---|
| C127 | bulenox | RTY | none / 2500.0 | 9.66 | 13:59, 12:30 | 0 vs 56.47 (below) | 0.000 | none | 2.556 / 2.776 | - |
| C128 | topstep | RTY | none / 2000.0 | 7.73 | 13:10, 12:30 | 150 vs 56.47 (exceeds) | 0.000 | none | - | - |
| C129 | tradeify | RTY | 1250.0 / 2000.0 | 4.83 | 13:45, 12:30 | 150 vs 56.47 (exceeds) | 0.000 | none | 2.872 / 3.092 | - |
| C130 | mffu | RTY | 1000.0 / 2000.0 | 3.86 | 13:10, 12:30 | 0 vs 56.47 (below) | 0.000 | none | - | - |
| C131 | ibkr | RTY | none (own account) | - | none, 12:30 | - | 0 | none | not computed | intraday initial USD 8760.56 (overnight 12515.08); sigma_cc 237.81 ticks = USD 1189.04 |

Data needed:

- RTY: schema ohlcv-1m (RTY price path). Discovery 2020-12-01..2024-02-29 (39 months; bars owned: True); test no clean window of 36 months or more before 2024-03: every pre-2024-03 month of the underlying was read (census p_basis) and none is sealed; a test would need 2024-03 onward (not sealed for these codes; outside Q7's pre-2024-03 rule); clean test window 0.0 months (none: None). Cost (estimates): discovery USD 0.00, test USD 0.00, all USD 0.00; basis: no clean pre-2024-03 test window: nothing to buy before 2024-03. Quotes to obtain: none. Not priced: option open interest by strike for a gamma-conditioned variant (GEX; vendor data, cost unknown; R1-14 used GEX rows 2020-05-29..2024-02-28); the 3rd-Friday variant needs bars and the expiry calendar only.
- Combination (sums over members; clean window = the shortest member's): discovery USD 0.00, all USD 0.00, clean test window 0.0 months.

### Dossier ZL|F01: product ZL, F01 intraday momentum into the close

MZL (micro sibling) is a survivor but not a top-15 code: no MZL combination (LR-R2a). ZL is a leg of the soybean crush with ZS and ZM (GRAINS-15, -16, -38).

*SOYOIL (Soybean oil (CBOT))*

- Applies because: Soybean oil (BO) is in Baltussen et al.'s 62-futures sample with its own product row (SB-22); the row is null or negative out of sample (F01.E03).
- Participant flow: Gamma hedgers: option market makers short gamma and leveraged-ETF rebalancing trade in the direction of the day's move before the close (Baltussen et al. 2021); late-informed traders (Gao et al. 2018).
- Why predictable: The hedge size is set mechanically by the day's return and is executed near the close, a known time.
- Why an edge could exist at retail size: The flow is non-informational and large against a one-lot; the open issue is size per trade against cost (R1-14: NQ T1 gross 1.25 ticks against 4.08 cost). One contract moves no price; at tens of milliseconds to a second without co-location only effects lasting minutes are reachable (information is priced within 1 to 5 s on ES, NQ, ZN, CL: E.25).
- Mechanism quote: "Hedging short gamma exposure requires trading in the direction of price movements, thereby creating price momentum." (reports/stage_e13_briefs/pages/InfoSource/baltussen_etal_2021_jfe.md:84-85)
- Documented horizon: 30 min: entry at close-30, exit at the class close (Baltussen et al.)
- Timing: entry 10:50 PT (12:50 CT), exit 11:20 PT (13:20 CT day close); main session 06:30-11:20 PT (day 08:30-13:20 CT, GRAINS-14); pause 07:45-08:30 CT = 05:45-06:30 PT
- Kind: daily; events a year: 252 (one trade a trade date); trades per event: 1
- Absorption under 5 minutes (R2): Not applicable as such: the effect is a 30-minute flow pattern. Contrary evidence is decay and regime change (EQUITY-39, -40, -41), not fast absorption.
- Evidence rows (relation to this product; full rows in the catalog): F01.E01 (asset-class pool (21 commodity futures, incl. BO); full_text); F01.E03 (this product: BO (soybean oil) product row (SB-22), null or negative; full_text); F01.E04 (all products (cost statement); full_text); F01.E09 (other venue (DCE soybean and meal; Chinese commodities); full_text); F01.E16 (cousin (CBOT soybean meal); reused (E.32)); F01.E15 (pooled program test incl. ZL; reused)
- R1 overlap (closing sentences in the R1 catalog):
  - R1-08 (this product (ZL among 7 roots)): K6-cp1-01 momentum port (decision 12:44 CT; exit by the exchange-set flat F per R1's horizons field); research window 2025-04-01..2026-06-19. Reading: closed configuration (LR-R1: a closed configuration stays closed at every venue, the own broker included).
  - R1-13 (pooled incl. ZL (2010-07..2024-02)): E16-H1 settlement-window momentum and H4 reversal. Reading: closed configuration (LR-R1: a closed configuration stays closed at every venue, the own broker included).
  - R1-15 (this product (ZL searched)): E20S ML, r_ROD features, h60/h120/hF. Reading: closed configuration (LR-R1: a closed configuration stays closed at every venue, the own broker included).
  - R1-14 (other product (NQ)): H6 rest-of-day to last-half-hour momentum. Reading: family closed on another product (family overlap under LR-R1).
  - R1-11 (this product (ZL tested)): Gate 0 ML at h60, h120, hF. Reading: closed configuration (LR-R1: a closed configuration stays closed at every venue, the own broker included).
- Open questions (R2): No per-product estimate after 2020-05 on any CME candidate; post-2018 equity evidence is regime-dependent (EQUITY-39) or a pointer (EQUITY-40). | No cost-adjusted per-product result; the only net statements are ES (one sentence) and SPY net of spread 2005-2013. | Micro codes, yield futures and mini grains were not in the sample; their price path is the full-size sibling's (settlement-derived), costs differ. | Whether a variant that differs from H6/E16-H1 (other products, conditioning) counts as a 'close variant' under R1 is for the lead and scorer.

Band and horizon: documented horizon inside B (documented [30] min). C132 h_c 30; C133 h_c 30

Cost and power at h_c (ticks of the member's own tick; e80 = SR80 sqrt(T) sigma_hc / sqrt(K)):

| id | venue | band | h_c | member | c_f | sigma_hc | c_f/sigma | p_be emp / norm | p_1 emp / norm | K_year | K_disc | K_test | e80 disc G3+G4 / G3 / test | c_f + e80_test |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C132 | topstep | 15-60 | 30 | ZL | 2.380 | 28.10 | 0.0847 | 0.5569 / 0.5531 | 0.5809 / 0.5754 | 252.0 | 796.0 | 870.0 | 6.49 / 5.69 / 5.44 | 7.82 |
| C133 | ibkr | 15-60 | 30 | ZL | 2.503 | 28.10 | 0.0891 | 0.5599 / 0.5558 | 0.5838 / 0.5781 | 252.0 | 796.0 | 870.0 | 6.49 / 5.69 / 5.44 | 7.94 |

Prop fit (one contract) and own-broker fit:

| id | venue | member | DLL (USD) / MLL | DLL/(sigma v) | flat-by-close PT, latest start | payout threshold vs sqrt(n/day) sigma v | news events a week | gates | queue-limit c_lim (passive entry / both) | margin, sigma_day |
|---|---|---|---|---|---|---|---|---|---|---|
| C132 | topstep | ZL | none / 2000.0 | 11.86 | 13:10, 10:50 | 150 vs 168.62 (below) | 0.000 | none | - | - |
| C133 | ibkr | ZL | none (own account) | - | none, 10:50 | - | 0 | none | not computed | intraday initial USD 4661.63 (overnight 4661.63); sigma_cc 116.84 ticks = USD 701.05 |

Data needed:

- ZL: schema ohlcv-1m (ZL price path). Discovery 2020-12-01..2024-02-29 (39 months; bars owned: True); test 2017-05-01..2020-11-30 (43 months; sealed for a future test (V51, every schema)); clean test window 43.04 months (sealed for a future test: ['2017-05-01', '2020-11-30']). Cost (estimates): discovery USD 0.00, test USD 0.00, all USD 0.00; basis: ZL ohlcv-1m for the window is owned inside the sealed files (docs/soy_test/SOY_TEST_MANIFEST.json: 44 raw ohlcv-1m files, 2 stores, 1 cache for ZL); unlock only in a registered test. Quotes to obtain: none.
- Combination (sums over members; clean window = the shortest member's): discovery USD 0.00, all USD 0.00, clean test window 43.04 months.

### Dossier ZL|F03: product ZL, F03 USDA and NOPA report drift

MZL (micro sibling) is a survivor but not a top-15 code: no MZL combination (LR-R2a). ZL is a leg of the soybean crush with ZS and ZM (GRAINS-15, -16, -38).

*SOYOIL (Soybean oil (CBOT))*

- Applies because: USDA reports (WASDE, Crop Production, Grain Stocks, Acreage, Prospective Plantings) at 11:00 CT inside the day session (GRAINS-22); NOPA monthly crush at noon ET = 11:00 CT (E.32 methods brief section 8.1; pre-2026 times unverified).
- Participant flow: Report digestion by commercial and speculative traders; slow incorporation of a large surprise (big events) or overshoot and correction (small events).
- Why predictable: Releases at 12:00 ET (11:00 CT) inside the day session since 2013 (GRAINS-22); NOPA monthly at noon ET (E.32 R4, times before 2026 [unverified]).
- Why an edge could exist at retail size: If the 10-60 minute path after the first minutes keeps a sign that is known at entry; no paper reports that entry-time conditional (E.32 R4 section 2). One contract moves no price; at tens of milliseconds to a second without co-location only effects lasting minutes are reachable (information is priced within 1 to 5 s on ES, NQ, ZN, CL: E.25).
- Mechanism quote: none recorded in the R2 file for this family
- Documented horizon: entry 5-15 min after 11:00 CT, exit at 30-60 min or at the 13:20 CT close (R2-F03); soybeans: not significant at 10 min, significant at 30, growing to the close (GRAINS-18)
- Timing: release 09:00 PT (11:00 CT; NOPA noon ET = 11:00 CT); 140 min before the 11:20 PT close; main session 06:30-11:20 PT (day 08:30-13:20 CT, GRAINS-14); pause 07:45-08:30 CT = 05:45-06:30 PT
- Kind: event; events a year: 27 (15 major 11:00 CT USDA days a year (E.32 R4_events.md line 235, cited in the E.32 methods brief lines 8201 and 8304) + 12 NOPA releases a year (monthly; methods brief section 8.2: 39 in 39 months); overlapping days not netted, holiday shifts not counted); trades per event: 1
- Absorption under 5 minutes (R2): Lehecka et al. (about 10 min, abstract), Adjemian-Irwin (few minutes, volatility), jumps within 2 min (GRAINS-23), Huang: 40% of the hour's move in minute 1. Against it: GRAINS-18 (soybeans keep moving to the close, 2010-2021) and Huang's direction-known big-event drift to about 40-49 min.
- Evidence rows (relation to this product; full rows in the catalog): F03.E01 (cousins (ZS, ZC nearby), WASDE; full_text); F03.E02 (cousin (corn nearby); full_text (E.32)); F03.E03 (cousin (ZS); full_text); F03.E04 (cousin (ZC); abstract); F03.E05 (grain futures (abstract); abstract); F03.E06 (cousin (ZC); reused); F03.E07 (cousins (ZC, ZS new crop), pointer; full_text); F03.E08 (this product (ZL) and ZM, pointer (news); snippet); F03.E09 (this product and the crush siblings (ZM, ZS, ZL); reused (E.32))
- R1 overlap (closing sentences in the R1 catalog):
  - R1-08 (other products (ZC, ZS)): K6-wasdepre-01 (ZC, ZS; decision 10:29 CT) and K6-wasdepost-01 (ZC; decision 11:14 CT); exit by the exchange-set flat F per R1. Reading: family closed on another product (family overlap under LR-R1).
  - R1-21 (crush sibling (ZM)): E.33 excluded release windows on ZM; post-USDA dropped as an E.33 family for power (E.32 verdict table). Reading: E.33c family closed on ZM; on this product family overlap (LR-R1).
  - R1-23 (direction-level): V39 closed 'commodity event drift as a standalone stage'; R1 lists its products as crude, metals, natgas (grains not named). Reading: direction closed by the user without a trial; grains not named (R1 ambiguity).
- Open questions (R2): Is there an entry-time signal (sign and size of the first 5-15 minutes) that keeps the GRAINS-18 / Huang drift? Not reported anywhere read. | NOPA crush days: no study at all. | Firm news windows for USDA releases: none listed for Topstep per the planner pointer; FirmRules owns this.

Band and horizon: documented horizon(s) [140] min lie outside B (15-60 min) (documented [30, 60, 140] min). C134 h_c 30; C135 h_c 30

Cost and power at h_c (ticks of the member's own tick; e80 = SR80 sqrt(T) sigma_hc / sqrt(K)):

| id | venue | band | h_c | member | c_f | sigma_hc | c_f/sigma | p_be emp / norm | p_1 emp / norm | K_year | K_disc | K_test | e80 disc G3+G4 / G3 / test | c_f + e80_test |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C134 | topstep | 15-60 | 30 | ZL | 2.380 | 28.10 | 0.0847 | 0.5569 / 0.5531 | 0.5809 / 0.5754 | 27.0 | 85.3 | 93.2 | 19.82 / 17.38 / 16.62 | 19.00 |
| C135 | ibkr | 15-60 | 30 | ZL | 2.503 | 28.10 | 0.0891 | 0.5599 / 0.5558 | 0.5838 / 0.5781 | 27.0 | 85.3 | 93.2 | 19.82 / 17.38 / 16.62 | 19.13 |

Prop fit (one contract) and own-broker fit:

| id | venue | member | DLL (USD) / MLL | DLL/(sigma v) | flat-by-close PT, latest start | payout threshold vs sqrt(n/day) sigma v | news events a week | gates | queue-limit c_lim (passive entry / both) | margin, sigma_day |
|---|---|---|---|---|---|---|---|---|---|---|
| C134 | topstep | ZL | none / 2000.0 | 11.86 | 13:10, 10:50 | 150 vs 55.19 (exceeds) | 0.000 | none | - | - |
| C135 | ibkr | ZL | none (own account) | - | none, 10:50 | - | 0 | none | not computed | intraday initial USD 4661.63 (overnight 4661.63); sigma_cc 116.84 ticks = USD 701.05 |

Data needed:

- ZL: schema ohlcv-1m (ZL price path). Discovery 2020-12-01..2024-02-29 (39 months; bars owned: True); test 2017-05-01..2020-11-30 (43 months; sealed for a future test (V51, every schema)); clean test window 43.04 months (sealed for a future test: ['2017-05-01', '2020-11-30']). Cost (estimates): discovery USD 0.00, test USD 0.00, all USD 0.00; basis: ZL ohlcv-1m for the window is owned inside the sealed files (docs/soy_test/SOY_TEST_MANIFEST.json: 44 raw ohlcv-1m files, 2 stores, 1 cache for ZL); unlock only in a registered test. Quotes to obtain: none. Not priced: dated USDA and NOPA release calendars (NOPA pre-2026 release times unverified, E.32 methods brief 8.1).
- Combination (sums over members; clean window = the shortest member's): discovery USD 0.00, all USD 0.00, clean test window 43.04 months.

### Dossier ZL|F08: product ZL, F08 session and overnight-to-day handoff

MZL (micro sibling) is a survivor but not a top-15 code: no MZL combination (LR-R2a). ZL is a leg of the soybean crush with ZS and ZM (GRAINS-15, -16, -38).

*SOYOIL (Soybean oil (CBOT))*

- Applies because: Fixed session clocks: Globex 19:00-07:45 CT, pause 07:45-08:30 CT, day 08:30-13:20 CT (GRAINS-14, GRAINS-29); R2-F08 lists the grain codes.
- Participant flow: Local-hours hedging and order imbalances carried over from the prior close (Boyarchenko et al.: 2:00-3:00 ET returns linked to prior US-close imbalances); overnight news priced at the reopen.
- Why predictable: Fixed session clocks (Globex pauses: grains 07:45-08:30 CT, GRAINS-14; daily 16:00-17:00 CT halts).
- Why an edge could exist at retail size: Hours-scale holds around a known clock; most documented versions are gross or negative after spreads. One contract moves no price; at tens of milliseconds to a second without co-location only effects lasting minutes are reachable (information is priced within 1 to 5 s on ES, NQ, ZN, CL: E.25).
- Mechanism quote: none recorded in the R2 file for this family
- Documented horizon: first half-hour after the 08:30 CT reopen (planner family 4, untested; F08.E09); overnight-to-day blocks of hours
- Timing: reopen 06:30 PT (08:30 CT) after the 05:45-06:30 PT pause; Export Sales 07:30 CT = 05:30 PT lands before the pause (GRAINS-22); main session 06:30-11:20 PT (day 08:30-13:20 CT, GRAINS-14); pause 07:45-08:30 CT = 05:45-06:30 PT
- Kind: daily; events a year: 252 (one trade a trade date); trades per event: 1
- Absorption under 5 minutes (R2): Not the issue here; the evidence that exists is either gross, pre-2013, other-venue, or negative after spreads (EQUITY-51) or arbitraged after a venue change (GRAINS-42, GRAINS-17).
- Evidence rows (relation to this product; full rows in the catalog): F08.E07 (other venue (DCE soybean, corn); abstract); F08.E08 (cousin (ZC); full_text); F08.E09 (cousin (ZM): overnight plus first half-hour; 08:30 reopen untested; reused (E.32)); F08.E13 (cousins (CL, NG, ZC, ZS), volatility only; full_text)
- R1 overlap (closing sentences in the R1 catalog):
  - R1-08 (this product (ZL among 7 roots)): K6-cp3-01 prior-day close-location (decision 08:30 CT, the day reopen; exit by the exchange-set flat F per R1). Reading: closed configuration (LR-R1: a closed configuration stays closed at every venue, the own broker included).
  - R1-13 (pooled incl. ZL): E16-H4 next-day reversal of the settlement-window move. Reading: closed configuration (LR-R1: a closed configuration stays closed at every venue, the own broker included).
  - R1-01 (cousin family on MES): families A (clock windows) and D (gaps). Reading: family closed on another product (family overlap under LR-R1).
- Open questions (R2): No post-2010 futures test of the local-hours currency effect on 6E/6A net of a futures round trip. | Grains 08:30 CT reopen after the 07:45-08:30 pause: untested (planner family 4), and Export Sales lands at 07:30 CT just before the pause (GRAINS-22).

Band and horizon: documented horizon inside B (documented [30] min). C136 h_c 30; C137 h_c 30

Cost and power at h_c (ticks of the member's own tick; e80 = SR80 sqrt(T) sigma_hc / sqrt(K)):

| id | venue | band | h_c | member | c_f | sigma_hc | c_f/sigma | p_be emp / norm | p_1 emp / norm | K_year | K_disc | K_test | e80 disc G3+G4 / G3 / test | c_f + e80_test |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C136 | topstep | 15-60 | 30 | ZL | 2.380 | 28.10 | 0.0847 | 0.5569 / 0.5531 | 0.5809 / 0.5754 | 252.0 | 796.0 | 870.0 | 6.49 / 5.69 / 5.44 | 7.82 |
| C137 | ibkr | 15-60 | 30 | ZL | 2.503 | 28.10 | 0.0891 | 0.5599 / 0.5558 | 0.5838 / 0.5781 | 252.0 | 796.0 | 870.0 | 6.49 / 5.69 / 5.44 | 7.94 |

Prop fit (one contract) and own-broker fit:

| id | venue | member | DLL (USD) / MLL | DLL/(sigma v) | flat-by-close PT, latest start | payout threshold vs sqrt(n/day) sigma v | news events a week | gates | queue-limit c_lim (passive entry / both) | margin, sigma_day |
|---|---|---|---|---|---|---|---|---|---|---|
| C136 | topstep | ZL | none / 2000.0 | 11.86 | 13:10, 10:50 | 150 vs 168.62 (below) | 0.000 | none | - | - |
| C137 | ibkr | ZL | none (own account) | - | none, 10:50 | - | 0 | none | not computed | intraday initial USD 4661.63 (overnight 4661.63); sigma_cc 116.84 ticks = USD 701.05 |

Data needed:

- ZL: schema ohlcv-1m (ZL price path). Discovery 2020-12-01..2024-02-29 (39 months; bars owned: True); test 2017-05-01..2020-11-30 (43 months; sealed for a future test (V51, every schema)); clean test window 43.04 months (sealed for a future test: ['2017-05-01', '2020-11-30']). Cost (estimates): discovery USD 0.00, test USD 0.00, all USD 0.00; basis: ZL ohlcv-1m for the window is owned inside the sealed files (docs/soy_test/SOY_TEST_MANIFEST.json: 44 raw ohlcv-1m files, 2 stores, 1 cache for ZL); unlock only in a registered test. Quotes to obtain: none.
- Combination (sums over members; clean window = the shortest member's): discovery USD 0.00, all USD 0.00, clean test window 43.04 months.

### Dossier ZL|F09: product ZL, F09 cross-market lead-lag

MZL (micro sibling) is a survivor but not a top-15 code: no MZL combination (LR-R2a). ZL is a leg of the soybean crush with ZS and ZM (GRAINS-15, -16, -38).

*SOYOIL (Soybean oil (CBOT))*

- Applies because: Soybean crush: ZS vs ZM and ZL cointegrated intraday on 180 of 243 day sessions (2015, 1-minute; GRAINS-15, -16), no fixed leader (GRAINS-38).
- Participant flow: Hedgers and spread traders anchoring an economic relation (crush margin); information arriving first in the deeper market and propagating.
- Why predictable: Cointegrated legs revert; a leader's move precedes a laggard's.
- Why an edge could exist at retail size: Only where the lag or the reversion lasts minutes to hours: seconds-scale lead-lag cannot pay at retail latency (E.32 verdict table, M2 b). One contract moves no price; at tens of milliseconds to a second without co-location only effects lasting minutes are reachable (information is priced within 1 to 5 s on ES, NQ, ZN, CL: E.25).
- Mechanism quote: none recorded in the R2 file for this family
- Documented horizon: 15-240 min for crush residual reversion (planner family 1); no published half-life (GRAINS-15)
- Timing: any time in the day session; main session 06:30-11:20 PT (day 08:30-13:20 CT, GRAINS-14); pause 07:45-08:30 CT = 05:45-06:30 PT
- Kind: continuous; events a year: - (continuous: n_cap(h_c) a day); trades per event: -
- Absorption under 5 minutes (R2): Cross-venue and mechanical links are seconds or milliseconds (CRUDE-33, RATES-17, GRAINS-24); silver->gold at 1 minute (METALS-37). Minute-to-hour structure exists only for the crush (cointegration, no half-life) and the NQ/Russell extrema lags (preprint).
- Evidence rows (relation to this product; full rows in the catalog): F09.E01 (this product as a crush leg (ZS, ZM, ZL); full_text); F09.E02 (this product as an input leg; traded ZM (program test); reused); F09.E03 (soy complex (abstract); abstract)
- R1 overlap (closing sentences in the R1 catalog):
  - R1-21 (this product as an input leg; ZM traded): S1 crush residual and S2 cross-asset propagation from ZS and ZL into ZM, 5-60 min, 2020-12-30..2024-02-29. Reading: E.33c family closed on ZM; on this product family overlap (LR-R1).
  - R1-08 (crush siblings (ZS traded, ZM bars as the signal leg)): K6-crushgap-01. Reading: family closed on another product (family overlap under LR-R1).
  - R1-20 (this product's MBP-1 read as conditioning data): E.31 read ZL MBP-1 2020-12..2024-02 (V50 item 4: not a clean holdout for order-flow tests). Reading: execution line: passive spread capture closed (V50); limit orders stay allowed as execution of a signal.
- Open questions (R2): Crush residual reversion with ZS or ZL (not ZM) as the traded leg: not tested by the program; no published intraday half-life. | No minute-level study of calendar-spread reversion for CL, NG or Treasuries; Treasury curve spreads (FIT/FYT, TUF, NOB, RATES-14) have no intraday study.

Band and horizon: documented horizon(s) [240] min lie outside B (15-60 min) (documented [15, 240] min). C138 h_c 30 (h_c not a documented horizon); C139 h_c 30 (h_c not a documented horizon)

Cost and power at h_c (ticks of the member's own tick; e80 = SR80 sqrt(T) sigma_hc / sqrt(K)):

| id | venue | band | h_c | member | c_f | sigma_hc | c_f/sigma | p_be emp / norm | p_1 emp / norm | K_year | K_disc | K_test | e80 disc G3+G4 / G3 / test | c_f + e80_test |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C138 | topstep | 15-60 | 30 | ZL | 2.380 | 28.10 | 0.0847 | 0.5569 / 0.5531 | 0.5809 / 0.5754 | 2268.0 | 7164.0 | 7830.0 | 2.16 / 1.90 / 1.81 | 4.19 |
| C139 | ibkr | 15-60 | 30 | ZL | 2.503 | 28.10 | 0.0891 | 0.5599 / 0.5558 | 0.5838 / 0.5781 | 2268.0 | 7164.0 | 7830.0 | 2.16 / 1.90 / 1.81 | 4.32 |

Prop fit (one contract) and own-broker fit:

| id | venue | member | DLL (USD) / MLL | DLL/(sigma v) | flat-by-close PT, latest start | payout threshold vs sqrt(n/day) sigma v | news events a week | gates | queue-limit c_lim (passive entry / both) | margin, sigma_day |
|---|---|---|---|---|---|---|---|---|---|---|
| C138 | topstep | ZL | none / 2000.0 | 11.86 | 13:10, 10:50 | 150 vs 505.85 (below) | 0.000 | none | - | - |
| C139 | ibkr | ZL | none (own account) | - | none, 10:50 | - | 0 | none | not computed | intraday initial USD 4661.63 (overnight 4661.63); sigma_cc 116.84 ticks = USD 701.05 |

Data needed:

- ZL: schema ohlcv-1m (ZL price path) + ZS, ZM legs. Discovery 2020-12-01..2024-02-29 (39 months; bars owned: True); test 2017-05-01..2020-11-30 (43 months; sealed for a future test (V51, every schema)); clean test window 43.04 months (sealed for a future test: ['2017-05-01', '2020-11-30']). Cost (estimates): discovery USD 0.00, test USD 0.00, all USD 0.00; basis: ZL ohlcv-1m for the window is owned inside the sealed files (docs/soy_test/SOY_TEST_MANIFEST.json: 44 raw ohlcv-1m files, 2 stores, 1 cache for ZL); unlock only in a registered test; crush legs ZS and ZM ohlcv-1m: discovery owned (2020-12..2024-02), test inside the sealed soy-test files (every schema). Quotes to obtain: none. Not priced: leader leg bars: NQ ohlcv-1m for RTY (owned 2010-06..2024-02); crush legs: ZS and ZM bars for ZL.
- Combination (sums over members; clean window = the shortest member's): discovery USD 0.00, all USD 0.00, clean test window 43.04 months.

### Dossier ZL|F10: product ZL, F10 order-book state at 5 min and longer

MZL (micro sibling) is a survivor but not a top-15 code: no MZL combination (LR-R2a). ZL is a leg of the soybean crush with ZS and ZM (GRAINS-15, -16, -38).

*SOYOIL (Soybean oil (CBOT))*

- Applies because: Order-book data exist: ZL MBP-1 2020-12..2024-02 owned (E.31 purchase); MBO buyable from 2017-05-21 (F2_data_access).
- Participant flow: Large orders worked over time (sign persistence) and liquidity shocks followed by refill.
- Why predictable: Imbalance and sign persistence are autocorrelated.
- Why an edge could exist at retail size: Weak: forward predictability decays to insignificance by 5-30 minutes and sign persistence is offset by asymmetric liquidity (E.32 M1). One contract moves no price; at tens of milliseconds to a second without co-location only effects lasting minutes are reachable (information is priced within 1 to 5 s on ES, NQ, ZN, CL: E.25).
- Mechanism quote: none recorded in the R2 file for this family
- Documented horizon: 5-30 min forward (R2-F10); forward predictability insignificant by 5-30 min (F10.E01)
- Timing: any time in the day session; main session 06:30-11:20 PT (day 08:30-13:20 CT, GRAINS-14); pause 07:45-08:30 CT = 05:45-06:30 PT
- Kind: continuous; events a year: - (continuous: n_cap(h_c) a day); trades per event: -
- Absorption under 5 minutes (R2): Central: E.32 M1 (contemporaneous far stronger than forward), Kolm et al. (seconds), E.25 (1-5 seconds on ES, NQ, ZN, CL).
- Evidence rows (relation to this product; full rows in the catalog): F10.E01 (other asset class (NYSE stocks); full_text (E.32 M1)); F10.E02 (equities (abstract); abstract); F10.E03 (cousin (ZC), drift-burst reversal; full_text (E.32 M1)); F10.E04 (grain futures (corn, wheat, soybeans; abstract, horizon unknown); abstract); F10.E07 (crush sibling ZM traded, ZL MBP-1 an input (program test); reused)
- R1 overlap (closing sentences in the R1 catalog):
  - R1-21 (this product's MBP-1 an input; ZM traded): S3 ZM order flow and book state at 5-60 min. Reading: E.33c family closed on ZM; on this product family overlap (LR-R1).
  - R1-20 (this product (ZL follow-up closed by decision, skipped)): passive spread capture at the touch. Reading: execution line: passive spread capture closed (V50); limit orders stay allowed as execution of a signal.
  - R1-11 (this product (ZL tested)): ML on 1-minute bar features (no book data). Reading: closed configuration (LR-R1: a closed configuration stays closed at every venue, the own broker included).
- Open questions (R2): No CME-product study of forward order-flow predictability at 5 minutes or more found outside ZM's own null. | Drift-burst reversal after removing the look-ahead: untested.

Band and horizon: documented horizon(s) [5] min lie outside B (15-60 min) (documented [5, 15, 30] min). C140 h_c 30; C141 h_c 30

Cost and power at h_c (ticks of the member's own tick; e80 = SR80 sqrt(T) sigma_hc / sqrt(K)):

| id | venue | band | h_c | member | c_f | sigma_hc | c_f/sigma | p_be emp / norm | p_1 emp / norm | K_year | K_disc | K_test | e80 disc G3+G4 / G3 / test | c_f + e80_test |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C140 | topstep | 15-60 | 30 | ZL | 2.380 | 28.10 | 0.0847 | 0.5569 / 0.5531 | 0.5809 / 0.5754 | 2268.0 | 7164.0 | 7830.0 | 2.16 / 1.90 / 1.81 | 4.19 |
| C141 | ibkr | 15-60 | 30 | ZL | 2.503 | 28.10 | 0.0891 | 0.5599 / 0.5558 | 0.5838 / 0.5781 | 2268.0 | 7164.0 | 7830.0 | 2.16 / 1.90 / 1.81 | 4.32 |

Prop fit (one contract) and own-broker fit:

| id | venue | member | DLL (USD) / MLL | DLL/(sigma v) | flat-by-close PT, latest start | payout threshold vs sqrt(n/day) sigma v | news events a week | gates | queue-limit c_lim (passive entry / both) | margin, sigma_day |
|---|---|---|---|---|---|---|---|---|---|---|
| C140 | topstep | ZL | none / 2000.0 | 11.86 | 13:10, 10:50 | 150 vs 505.85 (below) | 0.000 | none | - | - |
| C141 | ibkr | ZL | none (own account) | - | none, 10:50 | - | 0 | none | not computed | intraday initial USD 4661.63 (overnight 4661.63); sigma_cc 116.84 ticks = USD 701.05 |

Data needed:

- ZL: schema mbo (ZL; MBO from 2017-05-21). Discovery 2020-12-01..2024-02-29 (39 months; bars owned: True); test 2017-05-01..2020-11-30 (43 months; sealed for a future test (V51, every schema)); clean test window 43.04 months (sealed for a future test: ['2017-05-01', '2020-11-30']). Cost (estimates): discovery USD 19.48, test USD 21.48, all USD 40.96; basis: census estimate k = USD 0.4995/month (F2_data_access codes.ZL.k_usd_month, scaled from mbp-1 (estimate)) x months. Quotes to obtain: GLBX.MDP3 mbo ZL.v.0 2020-12-01..2024-02-29; GLBX.MDP3 mbo ZL.v.0 2017-05-01..2020-11-30 (MBP-10 before 2017-05-21). Alternative: {'schema': 'mbp-1', 'discovery': 'owned (E.31 purchase, ZL front MBP-1 2020-12..2024-02; read by E.31/E.33: V50 item 4)', 'discovery_cost_usd': 0.0, 'test_cost_usd': 23.36, 'basis': 'census mbp-1 whole-month mean USD 0.5432/month x 43 (estimate)'}. Not priced: MBP-10 is the highest granularity before 2017-05-21 (F2_data_access databento_dataset).
- Combination (sums over members; clean window = the shortest member's): discovery USD 19.48, all USD 40.96, clean test window 43.04 months.

### Dossier ZL|F11: product ZL, F11 own-price-path trend and reversal

MZL (micro sibling) is a survivor but not a top-15 code: no MZL combination (LR-R2a). ZL is a leg of the soybean crush with ZS and ZM (GRAINS-15, -16, -38).

*SOYOIL (Soybean oil (CBOT))*

- Applies because: R2-F11 applies to any code.
- Participant flow: Trend followers and stop cascades (trend); liquidity-provider inventory correction (reversion).
- Why predictable: Price-path autocorrelation by horizon (reversion 2-16 min, weak trend at 1 h or more).
- Why an edge could exist at retail size: Generic and crowded; the published sizes are tiny (out-of-sample R2 under 1 bp). One contract moves no price; at tens of milliseconds to a second without co-location only effects lasting minutes are reachable (information is priced within 1 to 5 s on ES, NQ, ZN, CL: E.25).
- Mechanism quote: none recorded in the R2 file for this family
- Documented horizon: reversion 2-16 min; weak trend at 1 h or more (F11.E01)
- Timing: any time in the day session; main session 06:30-11:20 PT (day 08:30-13:20 CT, GRAINS-14); pause 07:45-08:30 CT = 05:45-06:30 PT
- Kind: continuous; events a year: - (continuous: n_cap(h_c) a day); trades per event: -
- Absorption under 5 minutes (R2): Short reversion is at 2-16 min and tiny (CRUDE-40); Brent inefficiency vanishes past 10 min (CRUDE-54).
- Evidence rows (relation to this product; full rows in the catalog): F11.E01 (futures pool (16-24 futures incl. crude and the 10-year); full_text); F11.E05 (other venue (Chinese commodity futures); abstract)
- R1 overlap (closing sentences in the R1 catalog):
  - R1-08 (this product (ZL among 7 roots)): K6-cp2-01 opening-range breakout (variable 08:45..13:14 CT; exit by the exchange-set flat F per R1). Reading: closed configuration (LR-R1: a closed configuration stays closed at every venue, the own broker included).
  - R1-11 (this product (ZL tested)): Gate 0 ML over 64 bar features at h60, h120, hF. Reading: closed configuration (LR-R1: a closed configuration stays closed at every venue, the own broker included).
  - R1-15 (this product (ZL searched)): E20S ML, 36 bar features, h60/h120/hF. Reading: closed configuration (LR-R1: a closed configuration stays closed at every venue, the own broker included).
  - R1-21 (crush sibling (ZM)): S4 ZM own price path at 5-60 min. Reading: E.33c family closed on ZM; on this product family overlap (LR-R1).
  - R1-01 (cousin family on MES): families B, C, G, H. Reading: family closed on another product (family overlap under LR-R1).
- Open questions (R2): Every generic price-path family has been screened by the program on 1-minute bars; a new one would be a close variant unless the product or mechanism differs (scorer's call).

Band and horizon: documented horizon(s) [5] min lie outside B (15-60 min) (documented [5, 15, 60] min). C142 h_c 30 (h_c not a documented horizon); C143 h_c 30 (h_c not a documented horizon)

Cost and power at h_c (ticks of the member's own tick; e80 = SR80 sqrt(T) sigma_hc / sqrt(K)):

| id | venue | band | h_c | member | c_f | sigma_hc | c_f/sigma | p_be emp / norm | p_1 emp / norm | K_year | K_disc | K_test | e80 disc G3+G4 / G3 / test | c_f + e80_test |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C142 | topstep | 15-60 | 30 | ZL | 2.380 | 28.10 | 0.0847 | 0.5569 / 0.5531 | 0.5809 / 0.5754 | 2268.0 | 7164.0 | 7830.0 | 2.16 / 1.90 / 1.81 | 4.19 |
| C143 | ibkr | 15-60 | 30 | ZL | 2.503 | 28.10 | 0.0891 | 0.5599 / 0.5558 | 0.5838 / 0.5781 | 2268.0 | 7164.0 | 7830.0 | 2.16 / 1.90 / 1.81 | 4.32 |

Prop fit (one contract) and own-broker fit:

| id | venue | member | DLL (USD) / MLL | DLL/(sigma v) | flat-by-close PT, latest start | payout threshold vs sqrt(n/day) sigma v | news events a week | gates | queue-limit c_lim (passive entry / both) | margin, sigma_day |
|---|---|---|---|---|---|---|---|---|---|---|
| C142 | topstep | ZL | none / 2000.0 | 11.86 | 13:10, 10:50 | 150 vs 505.85 (below) | 0.000 | none | - | - |
| C143 | ibkr | ZL | none (own account) | - | none, 10:50 | - | 0 | none | not computed | intraday initial USD 4661.63 (overnight 4661.63); sigma_cc 116.84 ticks = USD 701.05 |

Data needed:

- ZL: schema ohlcv-1m (ZL price path). Discovery 2020-12-01..2024-02-29 (39 months; bars owned: True); test 2017-05-01..2020-11-30 (43 months; sealed for a future test (V51, every schema)); clean test window 43.04 months (sealed for a future test: ['2017-05-01', '2020-11-30']). Cost (estimates): discovery USD 0.00, test USD 0.00, all USD 0.00; basis: ZL ohlcv-1m for the window is owned inside the sealed files (docs/soy_test/SOY_TEST_MANIFEST.json: 44 raw ohlcv-1m files, 2 stores, 1 cache for ZL); unlock only in a registered test. Quotes to obtain: none.
- Combination (sums over members; clean window = the shortest member's): discovery USD 0.00, all USD 0.00, clean test window 43.04 months.

### Dossier EQ3|F01: pool EQ3 ['YM', 'MNQ', 'RTY'], F01 intraday momentum into the close

Pool mechanism: one index-level mechanism on three distinct underlyings (Dow, Nasdaq-100, Russell 2000): the same cash close (F01), release times (F04, F05), session clocks (F08), expiry calendar (F12), and the generic book (F10) and price-path (F11) families.

*DOW (Dow Jones Industrial Average)*: mechanism, participant flow, horizon, evidence rows and R1 overlap exactly as in dossier YM|F01 (same underlying, same family).

*NASDAQ (Nasdaq-100)*: mechanism, participant flow, horizon, evidence rows and R1 overlap exactly as in dossier MNQ|F01 (same underlying, same family).

*RUSSELL (Russell 2000)*: mechanism, participant flow, horizon, evidence rows and R1 overlap exactly as in dossier RTY|F01 (same underlying, same family).

Band and horizon: documented horizon inside B (documented [30] min). C144 h_c 30; C151 h_c 30; C158 h_c 30; C165 h_c 30

Cost and power at h_c (ticks of the member's own tick; e80 = SR80 sqrt(T) sigma_hc / sqrt(K)):

| id | venue | band | h_c | member | c_f | sigma_hc | c_f/sigma | p_be emp / norm | p_1 emp / norm | K_year | K_disc | K_test | e80 disc G3+G4 / G3 / test | c_f + e80_test |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C144 | topstep | 15-30 | 30 | YM | 2.256 | 63.23 | 0.0357 | 0.5248 / 0.5224 | 0.5358 / 0.5323 | 252.0 | 796.0 | 870.0 | 14.60 / 12.80 / 12.24 | 14.50 |
| C144 | topstep | 15-30 | 30 | MNQ | 3.940 | 147.10 | 0.0268 | 0.5183 / 0.5168 | 0.5229 / 0.5210 | 252.0 | 796.0 | 870.0 | 33.96 / 29.79 / 28.48 | 32.42 |
| C144 | topstep | 15-30 | 30 | RTY | 2.256 | 51.75 | 0.0436 | 0.5304 / 0.5273 | 0.5439 / 0.5394 | 252.0 | 796.0 | 870.0 | 11.95 / 10.48 / 10.02 | 12.28 |
| C151 | tradeify | 15-30 | 30 | YM | 2.652 | 63.23 | 0.0419 | 0.5292 / 0.5263 | 0.5402 / 0.5362 | 252.0 | 796.0 | 870.0 | 14.60 / 12.80 / 12.24 | 14.90 |
| C151 | tradeify | 15-30 | 30 | MNQ | 5.140 | 147.10 | 0.0349 | 0.5238 / 0.5219 | 0.5284 / 0.5262 | 252.0 | 796.0 | 870.0 | 33.96 / 29.79 / 28.48 | 33.62 |
| C151 | tradeify | 15-30 | 30 | RTY | 2.652 | 51.75 | 0.0512 | 0.5357 / 0.5321 | 0.5492 / 0.5442 | 252.0 | 796.0 | 870.0 | 11.95 / 10.48 / 10.02 | 12.67 |
| C158 | mffu | 15-30 | 30 | YM | 2.652 | 63.23 | 0.0419 | 0.5292 / 0.5263 | 0.5402 / 0.5362 | 252.0 | 796.0 | 870.0 | 14.60 / 12.80 / 12.24 | 14.90 |
| C158 | mffu | 15-30 | 30 | MNQ | 5.300 | 147.10 | 0.0360 | 0.5246 / 0.5226 | 0.5292 / 0.5268 | 252.0 | 796.0 | 870.0 | 33.96 / 29.79 / 28.48 | 33.78 |
| C158 | mffu | 15-30 | 30 | RTY | 2.436 | 51.75 | 0.0471 | 0.5328 / 0.5295 | 0.5463 / 0.5416 | 252.0 | 796.0 | 870.0 | 11.95 / 10.48 / 10.02 | 12.46 |
| C165 | ibkr | 15-30 | 30 | YM | 2.396 | 63.23 | 0.0379 | 0.5264 / 0.5237 | 0.5374 / 0.5337 | 252.0 | 796.0 | 870.0 | 14.60 / 12.80 / 12.24 | 14.64 |
| C165 | ibkr | 15-30 | 30 | MNQ | 6.344 | 147.10 | 0.0431 | 0.5294 / 0.5270 | 0.5340 / 0.5313 | 252.0 | 796.0 | 870.0 | 33.96 / 29.79 / 28.48 | 34.83 |
| C165 | ibkr | 15-30 | 30 | RTY | 2.396 | 51.75 | 0.0463 | 0.5323 / 0.5290 | 0.5458 / 0.5411 | 252.0 | 796.0 | 870.0 | 11.95 / 10.48 / 10.02 | 12.42 |

Prop fit (one contract) and own-broker fit:

| id | venue | member | DLL (USD) / MLL | DLL/(sigma v) | flat-by-close PT, latest start | payout threshold vs sqrt(n/day) sigma v | news events a week | gates | queue-limit c_lim (passive entry / both) | margin, sigma_day |
|---|---|---|---|---|---|---|---|---|---|---|
| C144 | topstep | YM | none / 2000.0 | 6.33 | 13:10, 12:30 | 150 vs 316.17 (below) | 0.000 | none | - | - |
| C144 | topstep | MNQ | none / 2000.0 | 27.19 | 13:10, 12:30 | 150 vs 73.55 (exceeds) | 0.000 | none | - | - |
| C144 | topstep | RTY | none / 2000.0 | 7.73 | 13:10, 12:30 | 150 vs 258.76 (below) | 0.000 | none | - | - |
| C151 | tradeify | YM | 1250.0 / 2000.0 | 3.95 | 13:45, 12:30 | 150 vs 316.17 (below) | 0.000 | none | 2.872 / 3.092 | - |
| C151 | tradeify | MNQ | 1250.0 / 2000.0 | 16.99 | 13:45, 12:30 | 150 vs 73.55 (exceeds) | 0.000 | none | 5.360 / 5.580 | - |
| C151 | tradeify | RTY | 1250.0 / 2000.0 | 4.83 | 13:45, 12:30 | 150 vs 258.76 (below) | 0.000 | none | 2.872 / 3.092 | - |
| C158 | mffu | YM | 1000.0 / 2000.0 | 3.16 | 13:10, 12:30 | 0 vs 316.17 (below) | 0.000 | none | - | - |
| C158 | mffu | MNQ | 1000.0 / 2000.0 | 13.60 | 13:10, 12:30 | 0 vs 73.55 (below) | 0.000 | none | - | - |
| C158 | mffu | RTY | 1000.0 / 2000.0 | 3.86 | 13:10, 12:30 | 0 vs 258.76 (below) | 0.000 | none | - | - |
| C165 | ibkr | YM | none (own account) | - | none, 12:30 | - | 0 | none | not computed | intraday initial USD 12699.91 (overnight 18142.73); sigma_cc 275.49 ticks = USD 1377.45 |
| C165 | ibkr | MNQ | none (own account) | - | none, 12:30 | - | 0 | none | not computed | intraday initial USD 4622.90 (overnight 6604.14); sigma_cc 699.90 ticks = USD 349.95 |
| C165 | ibkr | RTY | none (own account) | - | none, 12:30 | - | 0 | none | not computed | intraday initial USD 8760.56 (overnight 12515.08); sigma_cc 237.81 ticks = USD 1189.04 |

Data needed:

- YM: schema ohlcv-1m (YM price path). Discovery 2020-12-01..2024-02-29 (39 months; bars owned: True); test 2015-10-01..2019-04-30 (43 months; never read, unsealed, not owned: buy); clean test window 106.97 months (never read, unsealed: ['2010-06-06', '2019-05-06']). Cost (estimates): discovery USD 0.00, test USD 4.26, all USD 4.26; basis: estimate: E.12 quote USD 10.50261 for 106 monthly ohlcv-1m chunks 2010-07..2019-04 (reports/stage_e16_windows.json products.YM) = USD 0.0991/month x 43. Quotes to obtain: GLBX.MDP3 ohlcv-1m YM.v.0 2015-10-01..2019-04-30.
- MNQ: schema ohlcv-1m (NQ price path). Discovery 2020-12-01..2024-02-29 (39 months; bars owned: True); test no clean window of 36 months or more before 2024-03: every pre-2024-03 month of the underlying was read (census p_basis) and none is sealed; a test would need 2024-03 onward (not sealed for these codes; outside Q7's pre-2024-03 rule); clean test window 0.82 months (never read, unsealed: ['2010-06-06', '2010-07-01']). Cost (estimates): discovery USD 0.00, test USD 0.00, all USD 0.00; basis: no clean pre-2024-03 test window: nothing to buy before 2024-03. Quotes to obtain: none.
- RTY: schema ohlcv-1m (RTY price path). Discovery 2020-12-01..2024-02-29 (39 months; bars owned: True); test no clean window of 36 months or more before 2024-03: every pre-2024-03 month of the underlying was read (census p_basis) and none is sealed; a test would need 2024-03 onward (not sealed for these codes; outside Q7's pre-2024-03 rule); clean test window 0.0 months (none: None). Cost (estimates): discovery USD 0.00, test USD 0.00, all USD 0.00; basis: no clean pre-2024-03 test window: nothing to buy before 2024-03. Quotes to obtain: none.
- Combination (sums over members; clean window = the shortest member's): discovery USD 0.00, all USD 4.26, clean test window 0.0 months.

### Dossier EQ3|F04: pool EQ3 ['YM', 'MNQ', 'RTY'], F04 US macro release drift

Pool mechanism: one index-level mechanism on three distinct underlyings (Dow, Nasdaq-100, Russell 2000): the same cash close (F01), release times (F04, F05), session clocks (F08), expiry calendar (F12), and the generic book (F10) and price-path (F11) families.

*DOW (Dow Jones Industrial Average)*: mechanism, participant flow, horizon, evidence rows and R1 overlap exactly as in dossier YM|F04 (same underlying, same family).

*NASDAQ (Nasdaq-100)*: mechanism, participant flow, horizon, evidence rows and R1 overlap exactly as in dossier MNQ|F04 (same underlying, same family).

*RUSSELL (Russell 2000)*: mechanism, participant flow, horizon, evidence rows and R1 overlap exactly as in dossier RTY|F04 (same underlying, same family).

Band and horizon: documented horizon(s) [60] min lie outside B (15-30 min) (documented [20, 30, 60] min). C145 h_c 30; C152 h_c 30; C159 h_c 30; C166 h_c 30

Cost and power at h_c (ticks of the member's own tick; e80 = SR80 sqrt(T) sigma_hc / sqrt(K)):

| id | venue | band | h_c | member | c_f | sigma_hc | c_f/sigma | p_be emp / norm | p_1 emp / norm | K_year | K_disc | K_test | e80 disc G3+G4 / G3 / test | c_f + e80_test |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C145 | topstep | 15-30 | 30 | YM | 2.256 | 63.23 | 0.0357 | 0.5248 / 0.5224 | 0.5358 / 0.5323 | 67.6 | 213.6 | 233.4 | 28.18 / 24.72 / 23.64 | 25.89 |
| C145 | topstep | 15-30 | 30 | MNQ | 3.940 | 147.10 | 0.0268 | 0.5183 / 0.5168 | 0.5229 / 0.5210 | 67.6 | 213.6 | 233.4 | 65.56 / 57.51 / 54.99 | 58.93 |
| C145 | topstep | 15-30 | 30 | RTY | 2.256 | 51.75 | 0.0436 | 0.5304 / 0.5273 | 0.5439 / 0.5394 | 67.6 | 213.6 | 233.4 | 23.06 / 20.23 / 19.34 | 21.60 |
| C152 | tradeify | 15-30 | 30 | YM | 2.652 | 63.23 | 0.0419 | 0.5292 / 0.5263 | 0.5402 / 0.5362 | 67.6 | 213.6 | 233.4 | 28.18 / 24.72 / 23.64 | 26.29 |
| C152 | tradeify | 15-30 | 30 | MNQ | 5.140 | 147.10 | 0.0349 | 0.5238 / 0.5219 | 0.5284 / 0.5262 | 67.6 | 213.6 | 233.4 | 65.56 / 57.51 / 54.99 | 60.13 |
| C152 | tradeify | 15-30 | 30 | RTY | 2.652 | 51.75 | 0.0512 | 0.5357 / 0.5321 | 0.5492 / 0.5442 | 67.6 | 213.6 | 233.4 | 23.06 / 20.23 / 19.34 | 22.00 |
| C159 | mffu | 15-30 | 30 | YM | 2.652 | 63.23 | 0.0419 | 0.5292 / 0.5263 | 0.5402 / 0.5362 | 67.6 | 213.6 | 233.4 | 28.18 / 24.72 / 23.64 | 26.29 |
| C159 | mffu | 15-30 | 30 | MNQ | 5.300 | 147.10 | 0.0360 | 0.5246 / 0.5226 | 0.5292 / 0.5268 | 67.6 | 213.6 | 233.4 | 65.56 / 57.51 / 54.99 | 60.29 |
| C159 | mffu | 15-30 | 30 | RTY | 2.436 | 51.75 | 0.0471 | 0.5328 / 0.5295 | 0.5463 / 0.5416 | 67.6 | 213.6 | 233.4 | 23.06 / 20.23 / 19.34 | 21.78 |
| C166 | ibkr | 15-30 | 30 | YM | 2.396 | 63.23 | 0.0379 | 0.5264 / 0.5237 | 0.5374 / 0.5337 | 67.6 | 213.6 | 233.4 | 28.18 / 24.72 / 23.64 | 26.03 |
| C166 | ibkr | 15-30 | 30 | MNQ | 6.344 | 147.10 | 0.0431 | 0.5294 / 0.5270 | 0.5340 / 0.5313 | 67.6 | 213.6 | 233.4 | 65.56 / 57.51 / 54.99 | 61.33 |
| C166 | ibkr | 15-30 | 30 | RTY | 2.396 | 51.75 | 0.0463 | 0.5323 / 0.5290 | 0.5458 / 0.5411 | 67.6 | 213.6 | 233.4 | 23.06 / 20.23 / 19.34 | 21.74 |

Prop fit (one contract) and own-broker fit:

| id | venue | member | DLL (USD) / MLL | DLL/(sigma v) | flat-by-close PT, latest start | payout threshold vs sqrt(n/day) sigma v | news events a week | gates | queue-limit c_lim (passive entry / both) | margin, sigma_day |
|---|---|---|---|---|---|---|---|---|---|---|
| C145 | topstep | YM | none / 2000.0 | 6.33 | 13:10, 12:30 | 150 vs 163.77 (below) | 0.688 | none | - | - |
| C145 | topstep | MNQ | none / 2000.0 | 27.19 | 13:10, 12:30 | 150 vs 38.10 (exceeds) | 0.000 | none | - | - |
| C145 | topstep | RTY | none / 2000.0 | 7.73 | 13:10, 12:30 | 150 vs 134.03 (exceeds) | 0.688 | none | - | - |
| C152 | tradeify | YM | 1250.0 / 2000.0 | 3.95 | 13:45, 12:30 | 150 vs 163.77 (below) | 0.000 | none | 2.872 / 3.092 | - |
| C152 | tradeify | MNQ | 1250.0 / 2000.0 | 16.99 | 13:45, 12:30 | 150 vs 38.10 (exceeds) | 0.000 | none | 5.360 / 5.580 | - |
| C152 | tradeify | RTY | 1250.0 / 2000.0 | 4.83 | 13:45, 12:30 | 150 vs 134.03 (exceeds) | 0.000 | none | 2.872 / 3.092 | - |
| C159 | mffu | YM | 1000.0 / 2000.0 | 3.16 | 13:10, 12:30 | 0 vs 163.77 (below) | 0.000 | none | - | - |
| C159 | mffu | MNQ | 1000.0 / 2000.0 | 13.60 | 13:10, 12:30 | 0 vs 38.10 (below) | 0.000 | none | - | - |
| C159 | mffu | RTY | 1000.0 / 2000.0 | 3.86 | 13:10, 12:30 | 0 vs 134.03 (below) | 0.000 | none | - | - |
| C166 | ibkr | YM | none (own account) | - | none, 12:30 | - | 0 | none | not computed | intraday initial USD 12699.91 (overnight 18142.73); sigma_cc 275.49 ticks = USD 1377.45 |
| C166 | ibkr | MNQ | none (own account) | - | none, 12:30 | - | 0 | none | not computed | intraday initial USD 4622.90 (overnight 6604.14); sigma_cc 699.90 ticks = USD 349.95 |
| C166 | ibkr | RTY | none (own account) | - | none, 12:30 | - | 0 | none | not computed | intraday initial USD 8760.56 (overnight 12515.08); sigma_cc 237.81 ticks = USD 1189.04 |

Data needed:

- YM: schema ohlcv-1m (YM price path). Discovery 2020-12-01..2024-02-29 (39 months; bars owned: True); test 2015-10-01..2019-04-30 (43 months; never read, unsealed, not owned: buy); clean test window 106.97 months (never read, unsealed: ['2010-06-06', '2019-05-06']). Cost (estimates): discovery USD 0.00, test USD 4.26, all USD 4.26; basis: estimate: E.12 quote USD 10.50261 for 106 monthly ohlcv-1m chunks 2010-07..2019-04 (reports/stage_e16_windows.json products.YM) = USD 0.0991/month x 43. Quotes to obtain: GLBX.MDP3 ohlcv-1m YM.v.0 2015-10-01..2019-04-30. Not priced: release calendar (E.20 frozen calendar covers 2019-05..2024-02 only; no 2010-2019 file for NFP, CPI, PPI, GDP, ISM: macro_calendars.md section 3); consensus forecasts only for a surprise-signed variant (vendor data, not owned, cost unknown).
- MNQ: schema ohlcv-1m (NQ price path). Discovery 2020-12-01..2024-02-29 (39 months; bars owned: True); test no clean window of 36 months or more before 2024-03: every pre-2024-03 month of the underlying was read (census p_basis) and none is sealed; a test would need 2024-03 onward (not sealed for these codes; outside Q7's pre-2024-03 rule); clean test window 0.82 months (never read, unsealed: ['2010-06-06', '2010-07-01']). Cost (estimates): discovery USD 0.00, test USD 0.00, all USD 0.00; basis: no clean pre-2024-03 test window: nothing to buy before 2024-03. Quotes to obtain: none. Not priced: release calendar (E.20 frozen calendar covers 2019-05..2024-02 only; no 2010-2019 file for NFP, CPI, PPI, GDP, ISM: macro_calendars.md section 3); consensus forecasts only for a surprise-signed variant (vendor data, not owned, cost unknown).
- RTY: schema ohlcv-1m (RTY price path). Discovery 2020-12-01..2024-02-29 (39 months; bars owned: True); test no clean window of 36 months or more before 2024-03: every pre-2024-03 month of the underlying was read (census p_basis) and none is sealed; a test would need 2024-03 onward (not sealed for these codes; outside Q7's pre-2024-03 rule); clean test window 0.0 months (none: None). Cost (estimates): discovery USD 0.00, test USD 0.00, all USD 0.00; basis: no clean pre-2024-03 test window: nothing to buy before 2024-03. Quotes to obtain: none. Not priced: release calendar (E.20 frozen calendar covers 2019-05..2024-02 only; no 2010-2019 file for NFP, CPI, PPI, GDP, ISM: macro_calendars.md section 3); consensus forecasts only for a surprise-signed variant (vendor data, not owned, cost unknown).
- Combination (sums over members; clean window = the shortest member's): discovery USD 0.00, all USD 4.26, clean test window 0.0 months.

### Dossier EQ3|F05: pool EQ3 ['YM', 'MNQ', 'RTY'], F05 FOMC post-statement drift

Pool mechanism: one index-level mechanism on three distinct underlyings (Dow, Nasdaq-100, Russell 2000): the same cash close (F01), release times (F04, F05), session clocks (F08), expiry calendar (F12), and the generic book (F10) and price-path (F11) families.

*DOW (Dow Jones Industrial Average)*: mechanism, participant flow, horizon, evidence rows and R1 overlap exactly as in dossier YM|F05 (same underlying, same family).

*NASDAQ (Nasdaq-100)*: mechanism, participant flow, horizon, evidence rows and R1 overlap exactly as in dossier MNQ|F05 (same underlying, same family).

*RUSSELL (Russell 2000)*: mechanism, participant flow, horizon, evidence rows and R1 overlap exactly as in dossier RTY|F05 (same underlying, same family).

Band and horizon: documented horizon(s) [120] min lie outside B (15-30 min) (documented [30, 120] min). C146 h_c 30; C153 h_c 30; C160 h_c 30; C167 h_c 30

Cost and power at h_c (ticks of the member's own tick; e80 = SR80 sqrt(T) sigma_hc / sqrt(K)):

| id | venue | band | h_c | member | c_f | sigma_hc | c_f/sigma | p_be emp / norm | p_1 emp / norm | K_year | K_disc | K_test | e80 disc G3+G4 / G3 / test | c_f + e80_test |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C146 | topstep | 15-30 | 30 | YM | 2.256 | 63.23 | 0.0357 | 0.5248 / 0.5224 | 0.5358 / 0.5323 | 8.0 | 25.3 | 27.6 | 81.93 / 71.86 / 68.72 | 70.97 |
| C146 | topstep | 15-30 | 30 | MNQ | 3.940 | 147.10 | 0.0268 | 0.5183 / 0.5168 | 0.5229 / 0.5210 | 8.0 | 25.3 | 27.6 | 190.60 / 167.18 / 159.86 | 163.80 |
| C146 | topstep | 15-30 | 30 | RTY | 2.256 | 51.75 | 0.0436 | 0.5304 / 0.5273 | 0.5439 / 0.5394 | 8.0 | 25.3 | 27.6 | 67.05 / 58.81 / 56.24 | 58.50 |
| C153 | tradeify | 15-30 | 30 | YM | 2.652 | 63.23 | 0.0419 | 0.5292 / 0.5263 | 0.5402 / 0.5362 | 8.0 | 25.3 | 27.6 | 81.93 / 71.86 / 68.72 | 71.37 |
| C153 | tradeify | 15-30 | 30 | MNQ | 5.140 | 147.10 | 0.0349 | 0.5238 / 0.5219 | 0.5284 / 0.5262 | 8.0 | 25.3 | 27.6 | 190.60 / 167.18 / 159.86 | 165.00 |
| C153 | tradeify | 15-30 | 30 | RTY | 2.652 | 51.75 | 0.0512 | 0.5357 / 0.5321 | 0.5492 / 0.5442 | 8.0 | 25.3 | 27.6 | 67.05 / 58.81 / 56.24 | 58.89 |
| C160 | mffu | 15-30 | 30 | YM | 2.652 | 63.23 | 0.0419 | 0.5292 / 0.5263 | 0.5402 / 0.5362 | 8.0 | 25.3 | 27.6 | 81.93 / 71.86 / 68.72 | 71.37 |
| C160 | mffu | 15-30 | 30 | MNQ | 5.300 | 147.10 | 0.0360 | 0.5246 / 0.5226 | 0.5292 / 0.5268 | 8.0 | 25.3 | 27.6 | 190.60 / 167.18 / 159.86 | 165.16 |
| C160 | mffu | 15-30 | 30 | RTY | 2.436 | 51.75 | 0.0471 | 0.5328 / 0.5295 | 0.5463 / 0.5416 | 8.0 | 25.3 | 27.6 | 67.05 / 58.81 / 56.24 | 58.68 |
| C167 | ibkr | 15-30 | 30 | YM | 2.396 | 63.23 | 0.0379 | 0.5264 / 0.5237 | 0.5374 / 0.5337 | 8.0 | 25.3 | 27.6 | 81.93 / 71.86 / 68.72 | 71.11 |
| C167 | ibkr | 15-30 | 30 | MNQ | 6.344 | 147.10 | 0.0431 | 0.5294 / 0.5270 | 0.5340 / 0.5313 | 8.0 | 25.3 | 27.6 | 190.60 / 167.18 / 159.86 | 166.20 |
| C167 | ibkr | 15-30 | 30 | RTY | 2.396 | 51.75 | 0.0463 | 0.5323 / 0.5290 | 0.5458 / 0.5411 | 8.0 | 25.3 | 27.6 | 67.05 / 58.81 / 56.24 | 58.64 |

Prop fit (one contract) and own-broker fit:

| id | venue | member | DLL (USD) / MLL | DLL/(sigma v) | flat-by-close PT, latest start | payout threshold vs sqrt(n/day) sigma v | news events a week | gates | queue-limit c_lim (passive entry / both) | margin, sigma_day |
|---|---|---|---|---|---|---|---|---|---|---|
| C146 | topstep | YM | none / 2000.0 | 6.33 | 13:10, 12:30 | 150 vs 56.33 (exceeds) | 0.147 | none | - | - |
| C146 | topstep | MNQ | none / 2000.0 | 27.19 | 13:10, 12:30 | 150 vs 13.11 (exceeds) | 0.000 | none | - | - |
| C146 | topstep | RTY | none / 2000.0 | 7.73 | 13:10, 12:30 | 150 vs 46.10 (exceeds) | 0.147 | none | - | - |
| C153 | tradeify | YM | 1250.0 / 2000.0 | 3.95 | 13:45, 12:30 | 150 vs 56.33 (exceeds) | 0.000 | none | 2.872 / 3.092 | - |
| C153 | tradeify | MNQ | 1250.0 / 2000.0 | 16.99 | 13:45, 12:30 | 150 vs 13.11 (exceeds) | 0.000 | none | 5.360 / 5.580 | - |
| C153 | tradeify | RTY | 1250.0 / 2000.0 | 4.83 | 13:45, 12:30 | 150 vs 46.10 (exceeds) | 0.000 | none | 2.872 / 3.092 | - |
| C160 | mffu | YM | 1000.0 / 2000.0 | 3.16 | 13:10, 12:30 | 0 vs 56.33 (below) | 0.000 | none | - | - |
| C160 | mffu | MNQ | 1000.0 / 2000.0 | 13.60 | 13:10, 12:30 | 0 vs 13.11 (below) | 0.000 | none | - | - |
| C160 | mffu | RTY | 1000.0 / 2000.0 | 3.86 | 13:10, 12:30 | 0 vs 46.10 (below) | 0.000 | none | - | - |
| C167 | ibkr | YM | none (own account) | - | none, 12:30 | - | 0 | none | not computed | intraday initial USD 12699.91 (overnight 18142.73); sigma_cc 275.49 ticks = USD 1377.45 |
| C167 | ibkr | MNQ | none (own account) | - | none, 12:30 | - | 0 | none | not computed | intraday initial USD 4622.90 (overnight 6604.14); sigma_cc 699.90 ticks = USD 349.95 |
| C167 | ibkr | RTY | none (own account) | - | none, 12:30 | - | 0 | none | not computed | intraday initial USD 8760.56 (overnight 12515.08); sigma_cc 237.81 ticks = USD 1189.04 |

Data needed:

- YM: schema ohlcv-1m (YM price path). Discovery 2020-12-01..2024-02-29 (39 months; bars owned: True); test 2015-10-01..2019-04-30 (43 months; never read, unsealed, not owned: buy); clean test window 106.97 months (never read, unsealed: ['2010-06-06', '2019-05-06']). Cost (estimates): discovery USD 0.00, test USD 4.26, all USD 4.26; basis: estimate: E.12 quote USD 10.50261 for 106 monthly ohlcv-1m chunks 2010-07..2019-04 (reports/stage_e16_windows.json products.YM) = USD 0.0991/month x 43. Quotes to obtain: GLBX.MDP3 ohlcv-1m YM.v.0 2015-10-01..2019-04-30. Not priced: FOMC statement dates and times (calendar files 2010-2024 exist: macro_calendars.md section 3).
- MNQ: schema ohlcv-1m (NQ price path). Discovery 2020-12-01..2024-02-29 (39 months; bars owned: True); test no clean window of 36 months or more before 2024-03: every pre-2024-03 month of the underlying was read (census p_basis) and none is sealed; a test would need 2024-03 onward (not sealed for these codes; outside Q7's pre-2024-03 rule); clean test window 0.82 months (never read, unsealed: ['2010-06-06', '2010-07-01']). Cost (estimates): discovery USD 0.00, test USD 0.00, all USD 0.00; basis: no clean pre-2024-03 test window: nothing to buy before 2024-03. Quotes to obtain: none. Not priced: FOMC statement dates and times (calendar files 2010-2024 exist: macro_calendars.md section 3).
- RTY: schema ohlcv-1m (RTY price path). Discovery 2020-12-01..2024-02-29 (39 months; bars owned: True); test no clean window of 36 months or more before 2024-03: every pre-2024-03 month of the underlying was read (census p_basis) and none is sealed; a test would need 2024-03 onward (not sealed for these codes; outside Q7's pre-2024-03 rule); clean test window 0.0 months (none: None). Cost (estimates): discovery USD 0.00, test USD 0.00, all USD 0.00; basis: no clean pre-2024-03 test window: nothing to buy before 2024-03. Quotes to obtain: none. Not priced: FOMC statement dates and times (calendar files 2010-2024 exist: macro_calendars.md section 3).
- Combination (sums over members; clean window = the shortest member's): discovery USD 0.00, all USD 4.26, clean test window 0.0 months.

### Dossier EQ3|F08: pool EQ3 ['YM', 'MNQ', 'RTY'], F08 session and overnight-to-day handoff

Pool mechanism: one index-level mechanism on three distinct underlyings (Dow, Nasdaq-100, Russell 2000): the same cash close (F01), release times (F04, F05), session clocks (F08), expiry calendar (F12), and the generic book (F10) and price-path (F11) families.

*DOW (Dow Jones Industrial Average)*: mechanism, participant flow, horizon, evidence rows and R1 overlap exactly as in dossier YM|F08 (same underlying, same family).

*NASDAQ (Nasdaq-100)*: mechanism, participant flow, horizon, evidence rows and R1 overlap exactly as in dossier MNQ|F08 (same underlying, same family).

*RUSSELL (Russell 2000)*: mechanism, participant flow, horizon, evidence rows and R1 overlap exactly as in dossier RTY|F08 (same underlying, same family).

Band and horizon: documented horizon(s) [60] min lie outside B (15-30 min) (documented [30, 60] min). C147 h_c 30; C154 h_c 30; C161 h_c 30; C168 h_c 30

Cost and power at h_c (ticks of the member's own tick; e80 = SR80 sqrt(T) sigma_hc / sqrt(K)):

| id | venue | band | h_c | member | c_f | sigma_hc | c_f/sigma | p_be emp / norm | p_1 emp / norm | K_year | K_disc | K_test | e80 disc G3+G4 / G3 / test | c_f + e80_test |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C147 | topstep | 15-30 | 30 | YM | 2.256 | 63.23 | 0.0357 | 0.5248 / 0.5224 | 0.5358 / 0.5323 | 252.0 | 796.0 | 870.0 | 14.60 / 12.80 / 12.24 | 14.50 |
| C147 | topstep | 15-30 | 30 | MNQ | 3.940 | 147.10 | 0.0268 | 0.5183 / 0.5168 | 0.5229 / 0.5210 | 252.0 | 796.0 | 870.0 | 33.96 / 29.79 / 28.48 | 32.42 |
| C147 | topstep | 15-30 | 30 | RTY | 2.256 | 51.75 | 0.0436 | 0.5304 / 0.5273 | 0.5439 / 0.5394 | 252.0 | 796.0 | 870.0 | 11.95 / 10.48 / 10.02 | 12.28 |
| C154 | tradeify | 15-30 | 30 | YM | 2.652 | 63.23 | 0.0419 | 0.5292 / 0.5263 | 0.5402 / 0.5362 | 252.0 | 796.0 | 870.0 | 14.60 / 12.80 / 12.24 | 14.90 |
| C154 | tradeify | 15-30 | 30 | MNQ | 5.140 | 147.10 | 0.0349 | 0.5238 / 0.5219 | 0.5284 / 0.5262 | 252.0 | 796.0 | 870.0 | 33.96 / 29.79 / 28.48 | 33.62 |
| C154 | tradeify | 15-30 | 30 | RTY | 2.652 | 51.75 | 0.0512 | 0.5357 / 0.5321 | 0.5492 / 0.5442 | 252.0 | 796.0 | 870.0 | 11.95 / 10.48 / 10.02 | 12.67 |
| C161 | mffu | 15-30 | 30 | YM | 2.652 | 63.23 | 0.0419 | 0.5292 / 0.5263 | 0.5402 / 0.5362 | 252.0 | 796.0 | 870.0 | 14.60 / 12.80 / 12.24 | 14.90 |
| C161 | mffu | 15-30 | 30 | MNQ | 5.300 | 147.10 | 0.0360 | 0.5246 / 0.5226 | 0.5292 / 0.5268 | 252.0 | 796.0 | 870.0 | 33.96 / 29.79 / 28.48 | 33.78 |
| C161 | mffu | 15-30 | 30 | RTY | 2.436 | 51.75 | 0.0471 | 0.5328 / 0.5295 | 0.5463 / 0.5416 | 252.0 | 796.0 | 870.0 | 11.95 / 10.48 / 10.02 | 12.46 |
| C168 | ibkr | 15-30 | 30 | YM | 2.396 | 63.23 | 0.0379 | 0.5264 / 0.5237 | 0.5374 / 0.5337 | 252.0 | 796.0 | 870.0 | 14.60 / 12.80 / 12.24 | 14.64 |
| C168 | ibkr | 15-30 | 30 | MNQ | 6.344 | 147.10 | 0.0431 | 0.5294 / 0.5270 | 0.5340 / 0.5313 | 252.0 | 796.0 | 870.0 | 33.96 / 29.79 / 28.48 | 34.83 |
| C168 | ibkr | 15-30 | 30 | RTY | 2.396 | 51.75 | 0.0463 | 0.5323 / 0.5290 | 0.5458 / 0.5411 | 252.0 | 796.0 | 870.0 | 11.95 / 10.48 / 10.02 | 12.42 |

Prop fit (one contract) and own-broker fit:

| id | venue | member | DLL (USD) / MLL | DLL/(sigma v) | flat-by-close PT, latest start | payout threshold vs sqrt(n/day) sigma v | news events a week | gates | queue-limit c_lim (passive entry / both) | margin, sigma_day |
|---|---|---|---|---|---|---|---|---|---|---|
| C147 | topstep | YM | none / 2000.0 | 6.33 | 13:10, 12:30 | 150 vs 316.17 (below) | 0.000 | none | - | - |
| C147 | topstep | MNQ | none / 2000.0 | 27.19 | 13:10, 12:30 | 150 vs 73.55 (exceeds) | 0.000 | none | - | - |
| C147 | topstep | RTY | none / 2000.0 | 7.73 | 13:10, 12:30 | 150 vs 258.76 (below) | 0.000 | none | - | - |
| C154 | tradeify | YM | 1250.0 / 2000.0 | 3.95 | 13:45, 12:30 | 150 vs 316.17 (below) | 0.000 | none | 2.872 / 3.092 | - |
| C154 | tradeify | MNQ | 1250.0 / 2000.0 | 16.99 | 13:45, 12:30 | 150 vs 73.55 (exceeds) | 0.000 | none | 5.360 / 5.580 | - |
| C154 | tradeify | RTY | 1250.0 / 2000.0 | 4.83 | 13:45, 12:30 | 150 vs 258.76 (below) | 0.000 | none | 2.872 / 3.092 | - |
| C161 | mffu | YM | 1000.0 / 2000.0 | 3.16 | 13:10, 12:30 | 0 vs 316.17 (below) | 0.000 | none | - | - |
| C161 | mffu | MNQ | 1000.0 / 2000.0 | 13.60 | 13:10, 12:30 | 0 vs 73.55 (below) | 0.000 | none | - | - |
| C161 | mffu | RTY | 1000.0 / 2000.0 | 3.86 | 13:10, 12:30 | 0 vs 258.76 (below) | 0.000 | none | - | - |
| C168 | ibkr | YM | none (own account) | - | none, 12:30 | - | 0 | none | not computed | intraday initial USD 12699.91 (overnight 18142.73); sigma_cc 275.49 ticks = USD 1377.45 |
| C168 | ibkr | MNQ | none (own account) | - | none, 12:30 | - | 0 | none | not computed | intraday initial USD 4622.90 (overnight 6604.14); sigma_cc 699.90 ticks = USD 349.95 |
| C168 | ibkr | RTY | none (own account) | - | none, 12:30 | - | 0 | none | not computed | intraday initial USD 8760.56 (overnight 12515.08); sigma_cc 237.81 ticks = USD 1189.04 |

Data needed:

- YM: schema ohlcv-1m (YM price path). Discovery 2020-12-01..2024-02-29 (39 months; bars owned: True); test 2015-10-01..2019-04-30 (43 months; never read, unsealed, not owned: buy); clean test window 106.97 months (never read, unsealed: ['2010-06-06', '2019-05-06']). Cost (estimates): discovery USD 0.00, test USD 4.26, all USD 4.26; basis: estimate: E.12 quote USD 10.50261 for 106 monthly ohlcv-1m chunks 2010-07..2019-04 (reports/stage_e16_windows.json products.YM) = USD 0.0991/month x 43. Quotes to obtain: GLBX.MDP3 ohlcv-1m YM.v.0 2015-10-01..2019-04-30.
- MNQ: schema ohlcv-1m (NQ price path). Discovery 2020-12-01..2024-02-29 (39 months; bars owned: True); test no clean window of 36 months or more before 2024-03: every pre-2024-03 month of the underlying was read (census p_basis) and none is sealed; a test would need 2024-03 onward (not sealed for these codes; outside Q7's pre-2024-03 rule); clean test window 0.82 months (never read, unsealed: ['2010-06-06', '2010-07-01']). Cost (estimates): discovery USD 0.00, test USD 0.00, all USD 0.00; basis: no clean pre-2024-03 test window: nothing to buy before 2024-03. Quotes to obtain: none.
- RTY: schema ohlcv-1m (RTY price path). Discovery 2020-12-01..2024-02-29 (39 months; bars owned: True); test no clean window of 36 months or more before 2024-03: every pre-2024-03 month of the underlying was read (census p_basis) and none is sealed; a test would need 2024-03 onward (not sealed for these codes; outside Q7's pre-2024-03 rule); clean test window 0.0 months (none: None). Cost (estimates): discovery USD 0.00, test USD 0.00, all USD 0.00; basis: no clean pre-2024-03 test window: nothing to buy before 2024-03. Quotes to obtain: none.
- Combination (sums over members; clean window = the shortest member's): discovery USD 0.00, all USD 4.26, clean test window 0.0 months.

### Dossier EQ3|F10: pool EQ3 ['YM', 'MNQ', 'RTY'], F10 order-book state at 5 min and longer

Pool mechanism: one index-level mechanism on three distinct underlyings (Dow, Nasdaq-100, Russell 2000): the same cash close (F01), release times (F04, F05), session clocks (F08), expiry calendar (F12), and the generic book (F10) and price-path (F11) families.

*DOW (Dow Jones Industrial Average)*: mechanism, participant flow, horizon, evidence rows and R1 overlap exactly as in dossier YM|F10 (same underlying, same family).

*NASDAQ (Nasdaq-100)*: mechanism, participant flow, horizon, evidence rows and R1 overlap exactly as in dossier MNQ|F10 (same underlying, same family).

*RUSSELL (Russell 2000)*: mechanism, participant flow, horizon, evidence rows and R1 overlap exactly as in dossier RTY|F10 (same underlying, same family).

Band and horizon: documented horizon(s) [5] min lie outside B (15-30 min) (documented [5, 15, 30] min). C148 h_c 30; C155 h_c 30; C162 h_c 30; C169 h_c 30

Cost and power at h_c (ticks of the member's own tick; e80 = SR80 sqrt(T) sigma_hc / sqrt(K)):

| id | venue | band | h_c | member | c_f | sigma_hc | c_f/sigma | p_be emp / norm | p_1 emp / norm | K_year | K_disc | K_test | e80 disc G3+G4 / G3 / test | c_f + e80_test |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C148 | topstep | 15-30 | 30 | YM | 2.256 | 63.23 | 0.0357 | 0.5248 / 0.5224 | 0.5358 / 0.5323 | 3276.0 | 10348.0 | 11310.0 | 4.05 / 3.55 / 3.40 | 5.65 |
| C148 | topstep | 15-30 | 30 | MNQ | 3.940 | 147.10 | 0.0268 | 0.5183 / 0.5168 | 0.5229 / 0.5210 | 3276.0 | 10348.0 | 11310.0 | 9.42 / 8.26 / 7.90 | 11.84 |
| C148 | topstep | 15-30 | 30 | RTY | 2.256 | 51.75 | 0.0436 | 0.5304 / 0.5273 | 0.5439 / 0.5394 | 3276.0 | 10348.0 | 11310.0 | 3.31 / 2.91 / 2.78 | 5.04 |
| C155 | tradeify | 15-30 | 30 | YM | 2.652 | 63.23 | 0.0419 | 0.5292 / 0.5263 | 0.5402 / 0.5362 | 3276.0 | 10348.0 | 11310.0 | 4.05 / 3.55 / 3.40 | 6.05 |
| C155 | tradeify | 15-30 | 30 | MNQ | 5.140 | 147.10 | 0.0349 | 0.5238 / 0.5219 | 0.5284 / 0.5262 | 3276.0 | 10348.0 | 11310.0 | 9.42 / 8.26 / 7.90 | 13.04 |
| C155 | tradeify | 15-30 | 30 | RTY | 2.652 | 51.75 | 0.0512 | 0.5357 / 0.5321 | 0.5492 / 0.5442 | 3276.0 | 10348.0 | 11310.0 | 3.31 / 2.91 / 2.78 | 5.43 |
| C162 | mffu | 15-30 | 30 | YM | 2.652 | 63.23 | 0.0419 | 0.5292 / 0.5263 | 0.5402 / 0.5362 | 3276.0 | 10348.0 | 11310.0 | 4.05 / 3.55 / 3.40 | 6.05 |
| C162 | mffu | 15-30 | 30 | MNQ | 5.300 | 147.10 | 0.0360 | 0.5246 / 0.5226 | 0.5292 / 0.5268 | 3276.0 | 10348.0 | 11310.0 | 9.42 / 8.26 / 7.90 | 13.20 |
| C162 | mffu | 15-30 | 30 | RTY | 2.436 | 51.75 | 0.0471 | 0.5328 / 0.5295 | 0.5463 / 0.5416 | 3276.0 | 10348.0 | 11310.0 | 3.31 / 2.91 / 2.78 | 5.22 |
| C169 | ibkr | 15-30 | 30 | YM | 2.396 | 63.23 | 0.0379 | 0.5264 / 0.5237 | 0.5374 / 0.5337 | 3276.0 | 10348.0 | 11310.0 | 4.05 / 3.55 / 3.40 | 5.79 |
| C169 | ibkr | 15-30 | 30 | MNQ | 6.344 | 147.10 | 0.0431 | 0.5294 / 0.5270 | 0.5340 / 0.5313 | 3276.0 | 10348.0 | 11310.0 | 9.42 / 8.26 / 7.90 | 14.24 |
| C169 | ibkr | 15-30 | 30 | RTY | 2.396 | 51.75 | 0.0463 | 0.5323 / 0.5290 | 0.5458 / 0.5411 | 3276.0 | 10348.0 | 11310.0 | 3.31 / 2.91 / 2.78 | 5.18 |

Prop fit (one contract) and own-broker fit:

| id | venue | member | DLL (USD) / MLL | DLL/(sigma v) | flat-by-close PT, latest start | payout threshold vs sqrt(n/day) sigma v | news events a week | gates | queue-limit c_lim (passive entry / both) | margin, sigma_day |
|---|---|---|---|---|---|---|---|---|---|---|
| C148 | topstep | YM | none / 2000.0 | 6.33 | 13:10, 12:30 | 150 vs 1139.96 (below) | 0.835 | none | - | - |
| C148 | topstep | MNQ | none / 2000.0 | 27.19 | 13:10, 12:30 | 150 vs 265.20 (below) | 0.000 | none | - | - |
| C148 | topstep | RTY | none / 2000.0 | 7.73 | 13:10, 12:30 | 150 vs 932.96 (below) | 0.835 | none | - | - |
| C155 | tradeify | YM | 1250.0 / 2000.0 | 3.95 | 13:45, 12:30 | 150 vs 1139.96 (below) | 0.000 | none | 2.872 / 3.092 | - |
| C155 | tradeify | MNQ | 1250.0 / 2000.0 | 16.99 | 13:45, 12:30 | 150 vs 265.20 (below) | 0.000 | none | 5.360 / 5.580 | - |
| C155 | tradeify | RTY | 1250.0 / 2000.0 | 4.83 | 13:45, 12:30 | 150 vs 932.96 (below) | 0.000 | none | 2.872 / 3.092 | - |
| C162 | mffu | YM | 1000.0 / 2000.0 | 3.16 | 13:10, 12:30 | 0 vs 1139.96 (below) | 0.000 | none | - | - |
| C162 | mffu | MNQ | 1000.0 / 2000.0 | 13.60 | 13:10, 12:30 | 0 vs 265.20 (below) | 0.000 | none | - | - |
| C162 | mffu | RTY | 1000.0 / 2000.0 | 3.86 | 13:10, 12:30 | 0 vs 932.96 (below) | 0.000 | none | - | - |
| C169 | ibkr | YM | none (own account) | - | none, 12:30 | - | 0 | none | not computed | intraday initial USD 12699.91 (overnight 18142.73); sigma_cc 275.49 ticks = USD 1377.45 |
| C169 | ibkr | MNQ | none (own account) | - | none, 12:30 | - | 0 | none | not computed | intraday initial USD 4622.90 (overnight 6604.14); sigma_cc 699.90 ticks = USD 349.95 |
| C169 | ibkr | RTY | none (own account) | - | none, 12:30 | - | 0 | none | not computed | intraday initial USD 8760.56 (overnight 12515.08); sigma_cc 237.81 ticks = USD 1189.04 |

Data needed:

- YM: schema mbo (YM; MBO from 2017-05-21). Discovery 2020-12-01..2024-02-29 (39 months; bars owned: True); test 2015-10-01..2019-04-30 (43 months; never read, unsealed, not owned: buy); clean test window 106.97 months (never read, unsealed: ['2010-06-06', '2019-05-06']). Cost (estimates): discovery USD 227.57, test USD 250.91, all USD 478.48; basis: census estimate k = USD 5.8351/month (F2_data_access codes.YM.k_usd_month, scaled from mbp-1 (estimate)) x months. Quotes to obtain: GLBX.MDP3 mbo YM.v.0 2020-12-01..2024-02-29; GLBX.MDP3 mbo YM.v.0 2015-10-01..2019-04-30 (MBP-10 before 2017-05-21). Not priced: MBP-10 is the highest granularity before 2017-05-21 (F2_data_access databento_dataset).
- MNQ: schema mbo (MNQ; MBO from 2019-05-06). Discovery 2020-12-01..2024-02-29 (39 months; bars owned: True); test no clean window of 36 months or more before 2024-03: every pre-2024-03 month of the underlying was read (census p_basis) and none is sealed; a test would need 2024-03 onward (not sealed for these codes; outside Q7's pre-2024-03 rule); clean test window 0.82 months (never read, unsealed: ['2010-06-06', '2010-07-01']). Cost (estimates): discovery USD 2026.86, test USD 0.00, all USD 2026.86; basis: census estimate k = USD 51.9707/month (F2_data_access codes.MNQ.k_usd_month, scaled from mbp-1 (estimate)) x months; priced on MNQ's own MBO; NQ's book (census k USD 22.88/month) would be cheaper but NQ is excluded (V49: 'NQ is not used as a pilot or comparison contract'). Quotes to obtain: GLBX.MDP3 mbo MNQ.v.0 2020-12-01..2024-02-29. Not priced: MBP-10 is the highest granularity before 2017-05-21 (F2_data_access databento_dataset).
- RTY: schema mbo (RTY; MBO from 2017-07-10). Discovery 2020-12-01..2024-02-29 (39 months; bars owned: True); test no clean window of 36 months or more before 2024-03: every pre-2024-03 month of the underlying was read (census p_basis) and none is sealed; a test would need 2024-03 onward (not sealed for these codes; outside Q7's pre-2024-03 rule); clean test window 0.0 months (none: None). Cost (estimates): discovery USD 280.54, test USD 0.00, all USD 280.54; basis: census estimate k = USD 7.1933/month (F2_data_access codes.RTY.k_usd_month, scaled from mbp-1 (estimate)) x months. Quotes to obtain: GLBX.MDP3 mbo RTY.v.0 2020-12-01..2024-02-29. Not priced: MBP-10 is the highest granularity before 2017-05-21 (F2_data_access databento_dataset).
- Combination (sums over members; clean window = the shortest member's): discovery USD 2534.97, all USD 2785.88, clean test window 0.0 months.

### Dossier EQ3|F11: pool EQ3 ['YM', 'MNQ', 'RTY'], F11 own-price-path trend and reversal

Pool mechanism: one index-level mechanism on three distinct underlyings (Dow, Nasdaq-100, Russell 2000): the same cash close (F01), release times (F04, F05), session clocks (F08), expiry calendar (F12), and the generic book (F10) and price-path (F11) families.

*DOW (Dow Jones Industrial Average)*: mechanism, participant flow, horizon, evidence rows and R1 overlap exactly as in dossier YM|F11 (same underlying, same family).

*NASDAQ (Nasdaq-100)*: mechanism, participant flow, horizon, evidence rows and R1 overlap exactly as in dossier MNQ|F11 (same underlying, same family).

*RUSSELL (Russell 2000)*: mechanism, participant flow, horizon, evidence rows and R1 overlap exactly as in dossier RTY|F11 (same underlying, same family).

Band and horizon: documented horizon(s) [5, 60] min lie outside B (15-30 min) (documented [5, 15, 60] min). C149 h_c 30 (h_c not a documented horizon); C156 h_c 30 (h_c not a documented horizon); C163 h_c 30 (h_c not a documented horizon); C170 h_c 30 (h_c not a documented horizon)

Cost and power at h_c (ticks of the member's own tick; e80 = SR80 sqrt(T) sigma_hc / sqrt(K)):

| id | venue | band | h_c | member | c_f | sigma_hc | c_f/sigma | p_be emp / norm | p_1 emp / norm | K_year | K_disc | K_test | e80 disc G3+G4 / G3 / test | c_f + e80_test |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C149 | topstep | 15-30 | 30 | YM | 2.256 | 63.23 | 0.0357 | 0.5248 / 0.5224 | 0.5358 / 0.5323 | 3276.0 | 10348.0 | 11310.0 | 4.05 / 3.55 / 3.40 | 5.65 |
| C149 | topstep | 15-30 | 30 | MNQ | 3.940 | 147.10 | 0.0268 | 0.5183 / 0.5168 | 0.5229 / 0.5210 | 3276.0 | 10348.0 | 11310.0 | 9.42 / 8.26 / 7.90 | 11.84 |
| C149 | topstep | 15-30 | 30 | RTY | 2.256 | 51.75 | 0.0436 | 0.5304 / 0.5273 | 0.5439 / 0.5394 | 3276.0 | 10348.0 | 11310.0 | 3.31 / 2.91 / 2.78 | 5.04 |
| C156 | tradeify | 15-30 | 30 | YM | 2.652 | 63.23 | 0.0419 | 0.5292 / 0.5263 | 0.5402 / 0.5362 | 3276.0 | 10348.0 | 11310.0 | 4.05 / 3.55 / 3.40 | 6.05 |
| C156 | tradeify | 15-30 | 30 | MNQ | 5.140 | 147.10 | 0.0349 | 0.5238 / 0.5219 | 0.5284 / 0.5262 | 3276.0 | 10348.0 | 11310.0 | 9.42 / 8.26 / 7.90 | 13.04 |
| C156 | tradeify | 15-30 | 30 | RTY | 2.652 | 51.75 | 0.0512 | 0.5357 / 0.5321 | 0.5492 / 0.5442 | 3276.0 | 10348.0 | 11310.0 | 3.31 / 2.91 / 2.78 | 5.43 |
| C163 | mffu | 15-30 | 30 | YM | 2.652 | 63.23 | 0.0419 | 0.5292 / 0.5263 | 0.5402 / 0.5362 | 3276.0 | 10348.0 | 11310.0 | 4.05 / 3.55 / 3.40 | 6.05 |
| C163 | mffu | 15-30 | 30 | MNQ | 5.300 | 147.10 | 0.0360 | 0.5246 / 0.5226 | 0.5292 / 0.5268 | 3276.0 | 10348.0 | 11310.0 | 9.42 / 8.26 / 7.90 | 13.20 |
| C163 | mffu | 15-30 | 30 | RTY | 2.436 | 51.75 | 0.0471 | 0.5328 / 0.5295 | 0.5463 / 0.5416 | 3276.0 | 10348.0 | 11310.0 | 3.31 / 2.91 / 2.78 | 5.22 |
| C170 | ibkr | 15-30 | 30 | YM | 2.396 | 63.23 | 0.0379 | 0.5264 / 0.5237 | 0.5374 / 0.5337 | 3276.0 | 10348.0 | 11310.0 | 4.05 / 3.55 / 3.40 | 5.79 |
| C170 | ibkr | 15-30 | 30 | MNQ | 6.344 | 147.10 | 0.0431 | 0.5294 / 0.5270 | 0.5340 / 0.5313 | 3276.0 | 10348.0 | 11310.0 | 9.42 / 8.26 / 7.90 | 14.24 |
| C170 | ibkr | 15-30 | 30 | RTY | 2.396 | 51.75 | 0.0463 | 0.5323 / 0.5290 | 0.5458 / 0.5411 | 3276.0 | 10348.0 | 11310.0 | 3.31 / 2.91 / 2.78 | 5.18 |

Prop fit (one contract) and own-broker fit:

| id | venue | member | DLL (USD) / MLL | DLL/(sigma v) | flat-by-close PT, latest start | payout threshold vs sqrt(n/day) sigma v | news events a week | gates | queue-limit c_lim (passive entry / both) | margin, sigma_day |
|---|---|---|---|---|---|---|---|---|---|---|
| C149 | topstep | YM | none / 2000.0 | 6.33 | 13:10, 12:30 | 150 vs 1139.96 (below) | 0.835 | none | - | - |
| C149 | topstep | MNQ | none / 2000.0 | 27.19 | 13:10, 12:30 | 150 vs 265.20 (below) | 0.000 | none | - | - |
| C149 | topstep | RTY | none / 2000.0 | 7.73 | 13:10, 12:30 | 150 vs 932.96 (below) | 0.835 | none | - | - |
| C156 | tradeify | YM | 1250.0 / 2000.0 | 3.95 | 13:45, 12:30 | 150 vs 1139.96 (below) | 0.000 | none | 2.872 / 3.092 | - |
| C156 | tradeify | MNQ | 1250.0 / 2000.0 | 16.99 | 13:45, 12:30 | 150 vs 265.20 (below) | 0.000 | none | 5.360 / 5.580 | - |
| C156 | tradeify | RTY | 1250.0 / 2000.0 | 4.83 | 13:45, 12:30 | 150 vs 932.96 (below) | 0.000 | none | 2.872 / 3.092 | - |
| C163 | mffu | YM | 1000.0 / 2000.0 | 3.16 | 13:10, 12:30 | 0 vs 1139.96 (below) | 0.000 | none | - | - |
| C163 | mffu | MNQ | 1000.0 / 2000.0 | 13.60 | 13:10, 12:30 | 0 vs 265.20 (below) | 0.000 | none | - | - |
| C163 | mffu | RTY | 1000.0 / 2000.0 | 3.86 | 13:10, 12:30 | 0 vs 932.96 (below) | 0.000 | none | - | - |
| C170 | ibkr | YM | none (own account) | - | none, 12:30 | - | 0 | none | not computed | intraday initial USD 12699.91 (overnight 18142.73); sigma_cc 275.49 ticks = USD 1377.45 |
| C170 | ibkr | MNQ | none (own account) | - | none, 12:30 | - | 0 | none | not computed | intraday initial USD 4622.90 (overnight 6604.14); sigma_cc 699.90 ticks = USD 349.95 |
| C170 | ibkr | RTY | none (own account) | - | none, 12:30 | - | 0 | none | not computed | intraday initial USD 8760.56 (overnight 12515.08); sigma_cc 237.81 ticks = USD 1189.04 |

Data needed:

- YM: schema ohlcv-1m (YM price path). Discovery 2020-12-01..2024-02-29 (39 months; bars owned: True); test 2015-10-01..2019-04-30 (43 months; never read, unsealed, not owned: buy); clean test window 106.97 months (never read, unsealed: ['2010-06-06', '2019-05-06']). Cost (estimates): discovery USD 0.00, test USD 4.26, all USD 4.26; basis: estimate: E.12 quote USD 10.50261 for 106 monthly ohlcv-1m chunks 2010-07..2019-04 (reports/stage_e16_windows.json products.YM) = USD 0.0991/month x 43. Quotes to obtain: GLBX.MDP3 ohlcv-1m YM.v.0 2015-10-01..2019-04-30.
- MNQ: schema ohlcv-1m (NQ price path). Discovery 2020-12-01..2024-02-29 (39 months; bars owned: True); test no clean window of 36 months or more before 2024-03: every pre-2024-03 month of the underlying was read (census p_basis) and none is sealed; a test would need 2024-03 onward (not sealed for these codes; outside Q7's pre-2024-03 rule); clean test window 0.82 months (never read, unsealed: ['2010-06-06', '2010-07-01']). Cost (estimates): discovery USD 0.00, test USD 0.00, all USD 0.00; basis: no clean pre-2024-03 test window: nothing to buy before 2024-03. Quotes to obtain: none.
- RTY: schema ohlcv-1m (RTY price path). Discovery 2020-12-01..2024-02-29 (39 months; bars owned: True); test no clean window of 36 months or more before 2024-03: every pre-2024-03 month of the underlying was read (census p_basis) and none is sealed; a test would need 2024-03 onward (not sealed for these codes; outside Q7's pre-2024-03 rule); clean test window 0.0 months (none: None). Cost (estimates): discovery USD 0.00, test USD 0.00, all USD 0.00; basis: no clean pre-2024-03 test window: nothing to buy before 2024-03. Quotes to obtain: none.
- Combination (sums over members; clean window = the shortest member's): discovery USD 0.00, all USD 4.26, clean test window 0.0 months.

### Dossier EQ3|F12: pool EQ3 ['YM', 'MNQ', 'RTY'], F12 expiry and option-hedging days

Pool mechanism: one index-level mechanism on three distinct underlyings (Dow, Nasdaq-100, Russell 2000): the same cash close (F01), release times (F04, F05), session clocks (F08), expiry calendar (F12), and the generic book (F10) and price-path (F11) families.

*DOW (Dow Jones Industrial Average)*: mechanism, participant flow, horizon, evidence rows and R1 overlap exactly as in dossier YM|F12 (same underlying, same family).

*NASDAQ (Nasdaq-100)*: mechanism, participant flow, horizon, evidence rows and R1 overlap exactly as in dossier MNQ|F12 (same underlying, same family).

*RUSSELL (Russell 2000)*: mechanism, participant flow, horizon, evidence rows and R1 overlap exactly as in dossier RTY|F12 (same underlying, same family).

Band and horizon: documented horizon(s) [10, 60] min lie outside B (15-30 min) (documented [10, 30, 60] min). C150 h_c 30; C157 h_c 30; C164 h_c 30; C171 h_c 30

Cost and power at h_c (ticks of the member's own tick; e80 = SR80 sqrt(T) sigma_hc / sqrt(K)):

| id | venue | band | h_c | member | c_f | sigma_hc | c_f/sigma | p_be emp / norm | p_1 emp / norm | K_year | K_disc | K_test | e80 disc G3+G4 / G3 / test | c_f + e80_test |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C150 | topstep | 15-30 | 30 | YM | 2.256 | 63.23 | 0.0357 | 0.5248 / 0.5224 | 0.5358 / 0.5323 | 12.0 | 37.9 | 41.4 | 66.89 / 58.68 / 56.11 | 58.36 |
| C150 | topstep | 15-30 | 30 | MNQ | 3.940 | 147.10 | 0.0268 | 0.5183 / 0.5168 | 0.5229 / 0.5210 | 12.0 | 37.9 | 41.4 | 155.62 / 136.50 / 130.53 | 134.47 |
| C150 | topstep | 15-30 | 30 | RTY | 2.256 | 51.75 | 0.0436 | 0.5304 / 0.5273 | 0.5439 / 0.5394 | 12.0 | 37.9 | 41.4 | 54.75 / 48.02 / 45.92 | 48.18 |
| C157 | tradeify | 15-30 | 30 | YM | 2.652 | 63.23 | 0.0419 | 0.5292 / 0.5263 | 0.5402 / 0.5362 | 12.0 | 37.9 | 41.4 | 66.89 / 58.68 / 56.11 | 58.76 |
| C157 | tradeify | 15-30 | 30 | MNQ | 5.140 | 147.10 | 0.0349 | 0.5238 / 0.5219 | 0.5284 / 0.5262 | 12.0 | 37.9 | 41.4 | 155.62 / 136.50 / 130.53 | 135.67 |
| C157 | tradeify | 15-30 | 30 | RTY | 2.652 | 51.75 | 0.0512 | 0.5357 / 0.5321 | 0.5492 / 0.5442 | 12.0 | 37.9 | 41.4 | 54.75 / 48.02 / 45.92 | 48.57 |
| C164 | mffu | 15-30 | 30 | YM | 2.652 | 63.23 | 0.0419 | 0.5292 / 0.5263 | 0.5402 / 0.5362 | 12.0 | 37.9 | 41.4 | 66.89 / 58.68 / 56.11 | 58.76 |
| C164 | mffu | 15-30 | 30 | MNQ | 5.300 | 147.10 | 0.0360 | 0.5246 / 0.5226 | 0.5292 / 0.5268 | 12.0 | 37.9 | 41.4 | 155.62 / 136.50 / 130.53 | 135.83 |
| C164 | mffu | 15-30 | 30 | RTY | 2.436 | 51.75 | 0.0471 | 0.5328 / 0.5295 | 0.5463 / 0.5416 | 12.0 | 37.9 | 41.4 | 54.75 / 48.02 / 45.92 | 48.36 |
| C171 | ibkr | 15-30 | 30 | YM | 2.396 | 63.23 | 0.0379 | 0.5264 / 0.5237 | 0.5374 / 0.5337 | 12.0 | 37.9 | 41.4 | 66.89 / 58.68 / 56.11 | 58.50 |
| C171 | ibkr | 15-30 | 30 | MNQ | 6.344 | 147.10 | 0.0431 | 0.5294 / 0.5270 | 0.5340 / 0.5313 | 12.0 | 37.9 | 41.4 | 155.62 / 136.50 / 130.53 | 136.87 |
| C171 | ibkr | 15-30 | 30 | RTY | 2.396 | 51.75 | 0.0463 | 0.5323 / 0.5290 | 0.5458 / 0.5411 | 12.0 | 37.9 | 41.4 | 54.75 / 48.02 / 45.92 | 48.32 |

Prop fit (one contract) and own-broker fit:

| id | venue | member | DLL (USD) / MLL | DLL/(sigma v) | flat-by-close PT, latest start | payout threshold vs sqrt(n/day) sigma v | news events a week | gates | queue-limit c_lim (passive entry / both) | margin, sigma_day |
|---|---|---|---|---|---|---|---|---|---|---|
| C150 | topstep | YM | none / 2000.0 | 6.33 | 13:10, 12:30 | 150 vs 68.99 (exceeds) | 0.000 | none | - | - |
| C150 | topstep | MNQ | none / 2000.0 | 27.19 | 13:10, 12:30 | 150 vs 16.05 (exceeds) | 0.000 | none | - | - |
| C150 | topstep | RTY | none / 2000.0 | 7.73 | 13:10, 12:30 | 150 vs 56.47 (exceeds) | 0.000 | none | - | - |
| C157 | tradeify | YM | 1250.0 / 2000.0 | 3.95 | 13:45, 12:30 | 150 vs 68.99 (exceeds) | 0.000 | none | 2.872 / 3.092 | - |
| C157 | tradeify | MNQ | 1250.0 / 2000.0 | 16.99 | 13:45, 12:30 | 150 vs 16.05 (exceeds) | 0.000 | none | 5.360 / 5.580 | - |
| C157 | tradeify | RTY | 1250.0 / 2000.0 | 4.83 | 13:45, 12:30 | 150 vs 56.47 (exceeds) | 0.000 | none | 2.872 / 3.092 | - |
| C164 | mffu | YM | 1000.0 / 2000.0 | 3.16 | 13:10, 12:30 | 0 vs 68.99 (below) | 0.000 | none | - | - |
| C164 | mffu | MNQ | 1000.0 / 2000.0 | 13.60 | 13:10, 12:30 | 0 vs 16.05 (below) | 0.000 | none | - | - |
| C164 | mffu | RTY | 1000.0 / 2000.0 | 3.86 | 13:10, 12:30 | 0 vs 56.47 (below) | 0.000 | none | - | - |
| C171 | ibkr | YM | none (own account) | - | none, 12:30 | - | 0 | none | not computed | intraday initial USD 12699.91 (overnight 18142.73); sigma_cc 275.49 ticks = USD 1377.45 |
| C171 | ibkr | MNQ | none (own account) | - | none, 12:30 | - | 0 | none | not computed | intraday initial USD 4622.90 (overnight 6604.14); sigma_cc 699.90 ticks = USD 349.95 |
| C171 | ibkr | RTY | none (own account) | - | none, 12:30 | - | 0 | none | not computed | intraday initial USD 8760.56 (overnight 12515.08); sigma_cc 237.81 ticks = USD 1189.04 |

Data needed:

- YM: schema ohlcv-1m (YM price path). Discovery 2020-12-01..2024-02-29 (39 months; bars owned: True); test 2015-10-01..2019-04-30 (43 months; never read, unsealed, not owned: buy); clean test window 106.97 months (never read, unsealed: ['2010-06-06', '2019-05-06']). Cost (estimates): discovery USD 0.00, test USD 4.26, all USD 4.26; basis: estimate: E.12 quote USD 10.50261 for 106 monthly ohlcv-1m chunks 2010-07..2019-04 (reports/stage_e16_windows.json products.YM) = USD 0.0991/month x 43. Quotes to obtain: GLBX.MDP3 ohlcv-1m YM.v.0 2015-10-01..2019-04-30. Not priced: option open interest by strike for a gamma-conditioned variant (GEX; vendor data, cost unknown; R1-14 used GEX rows 2020-05-29..2024-02-28); the 3rd-Friday variant needs bars and the expiry calendar only.
- MNQ: schema ohlcv-1m (NQ price path). Discovery 2020-12-01..2024-02-29 (39 months; bars owned: True); test no clean window of 36 months or more before 2024-03: every pre-2024-03 month of the underlying was read (census p_basis) and none is sealed; a test would need 2024-03 onward (not sealed for these codes; outside Q7's pre-2024-03 rule); clean test window 0.82 months (never read, unsealed: ['2010-06-06', '2010-07-01']). Cost (estimates): discovery USD 0.00, test USD 0.00, all USD 0.00; basis: no clean pre-2024-03 test window: nothing to buy before 2024-03. Quotes to obtain: none. Not priced: option open interest by strike for a gamma-conditioned variant (GEX; vendor data, cost unknown; R1-14 used GEX rows 2020-05-29..2024-02-28); the 3rd-Friday variant needs bars and the expiry calendar only.
- RTY: schema ohlcv-1m (RTY price path). Discovery 2020-12-01..2024-02-29 (39 months; bars owned: True); test no clean window of 36 months or more before 2024-03: every pre-2024-03 month of the underlying was read (census p_basis) and none is sealed; a test would need 2024-03 onward (not sealed for these codes; outside Q7's pre-2024-03 rule); clean test window 0.0 months (none: None). Cost (estimates): discovery USD 0.00, test USD 0.00, all USD 0.00; basis: no clean pre-2024-03 test window: nothing to buy before 2024-03. Quotes to obtain: none. Not priced: option open interest by strike for a gamma-conditioned variant (GEX; vendor data, cost unknown; R1-14 used GEX rows 2020-05-29..2024-02-28); the 3rd-Friday variant needs bars and the expiry calendar only.
- Combination (sums over members; clean window = the shortest member's): discovery USD 0.00, all USD 4.26, clean test window 0.0 months.

### Dossier EQ3m|F01: pool EQ3m ['MYM', 'MNQ', 'RTY'], F01 intraday momentum into the close

Pool mechanism: as EQ3 with the micro Dow (MYM) in place of YM; YM and MYM are one underlying and never pool together (pooling one price path twice would overstate K_eff).

*DOW (Dow Jones Industrial Average)*: mechanism, participant flow, horizon, evidence rows and R1 overlap exactly as in dossier YM|F01 (same underlying, same family).

*NASDAQ (Nasdaq-100)*: mechanism, participant flow, horizon, evidence rows and R1 overlap exactly as in dossier MNQ|F01 (same underlying, same family).

*RUSSELL (Russell 2000)*: mechanism, participant flow, horizon, evidence rows and R1 overlap exactly as in dossier RTY|F01 (same underlying, same family).

Band and horizon: documented horizon inside B (documented [30] min). C172 h_c 30; C179 h_c 30

Cost and power at h_c (ticks of the member's own tick; e80 = SR80 sqrt(T) sigma_hc / sqrt(K)):

| id | venue | band | h_c | member | c_f | sigma_hc | c_f/sigma | p_be emp / norm | p_1 emp / norm | K_year | K_disc | K_test | e80 disc G3+G4 / G3 / test | c_f + e80_test |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C172 | mffu | 30-30 | 30 | MYM | 5.300 | 63.23 | 0.0838 | 0.5583 / 0.5525 | 0.5694 / 0.5624 | 252.0 | 796.0 | 870.0 | 14.60 / 12.80 / 12.24 | 17.54 |
| C172 | mffu | 30-30 | 30 | MNQ | 5.300 | 147.10 | 0.0360 | 0.5246 / 0.5226 | 0.5292 / 0.5268 | 252.0 | 796.0 | 870.0 | 33.96 / 29.79 / 28.48 | 33.78 |
| C172 | mffu | 30-30 | 30 | RTY | 2.436 | 51.75 | 0.0471 | 0.5328 / 0.5295 | 0.5463 / 0.5416 | 252.0 | 796.0 | 870.0 | 11.95 / 10.48 / 10.02 | 12.46 |
| C179 | ibkr | 30-30 | 30 | MYM | 6.340 | 63.23 | 0.1003 | 0.5698 / 0.5628 | 0.5808 / 0.5727 | 252.0 | 796.0 | 870.0 | 14.60 / 12.80 / 12.24 | 18.58 |
| C179 | ibkr | 30-30 | 30 | MNQ | 6.344 | 147.10 | 0.0431 | 0.5294 / 0.5270 | 0.5340 / 0.5313 | 252.0 | 796.0 | 870.0 | 33.96 / 29.79 / 28.48 | 34.83 |
| C179 | ibkr | 30-30 | 30 | RTY | 2.396 | 51.75 | 0.0463 | 0.5323 / 0.5290 | 0.5458 / 0.5411 | 252.0 | 796.0 | 870.0 | 11.95 / 10.48 / 10.02 | 12.42 |

Prop fit (one contract) and own-broker fit:

| id | venue | member | DLL (USD) / MLL | DLL/(sigma v) | flat-by-close PT, latest start | payout threshold vs sqrt(n/day) sigma v | news events a week | gates | queue-limit c_lim (passive entry / both) | margin, sigma_day |
|---|---|---|---|---|---|---|---|---|---|---|
| C172 | mffu | MYM | 1000.0 / 2000.0 | 31.63 | 13:10, 12:30 | 0 vs 31.62 (below) | 0.000 | none | - | - |
| C172 | mffu | MNQ | 1000.0 / 2000.0 | 13.60 | 13:10, 12:30 | 0 vs 73.55 (below) | 0.000 | none | - | - |
| C172 | mffu | RTY | 1000.0 / 2000.0 | 3.86 | 13:10, 12:30 | 0 vs 258.76 (below) | 0.000 | none | - | - |
| C179 | ibkr | MYM | none (own account) | - | none, 12:30 | - | 0 | none | not computed | intraday initial USD 1269.99 (overnight 1814.27); sigma_cc 275.49 ticks = USD 137.74 |
| C179 | ibkr | MNQ | none (own account) | - | none, 12:30 | - | 0 | none | not computed | intraday initial USD 4622.90 (overnight 6604.14); sigma_cc 699.90 ticks = USD 349.95 |
| C179 | ibkr | RTY | none (own account) | - | none, 12:30 | - | 0 | none | not computed | intraday initial USD 8760.56 (overnight 12515.08); sigma_cc 237.81 ticks = USD 1189.04 |

Data needed:

- MYM: schema ohlcv-1m (YM price path). Discovery 2020-12-01..2024-02-29 (39 months; bars owned: True); test 2015-10-01..2019-04-30 (43 months; never read, unsealed, not owned: buy); clean test window 106.97 months (never read, unsealed: ['2010-06-06', '2019-05-06']). Cost (estimates): discovery USD 0.00, test USD 4.26, all USD 4.26; basis: estimate: E.12 quote USD 10.50261 for 106 monthly ohlcv-1m chunks 2010-07..2019-04 (reports/stage_e16_windows.json products.YM) = USD 0.0991/month x 43. Quotes to obtain: GLBX.MDP3 ohlcv-1m YM.v.0 2015-10-01..2019-04-30.
- MNQ: schema ohlcv-1m (NQ price path). Discovery 2020-12-01..2024-02-29 (39 months; bars owned: True); test no clean window of 36 months or more before 2024-03: every pre-2024-03 month of the underlying was read (census p_basis) and none is sealed; a test would need 2024-03 onward (not sealed for these codes; outside Q7's pre-2024-03 rule); clean test window 0.82 months (never read, unsealed: ['2010-06-06', '2010-07-01']). Cost (estimates): discovery USD 0.00, test USD 0.00, all USD 0.00; basis: no clean pre-2024-03 test window: nothing to buy before 2024-03. Quotes to obtain: none.
- RTY: schema ohlcv-1m (RTY price path). Discovery 2020-12-01..2024-02-29 (39 months; bars owned: True); test no clean window of 36 months or more before 2024-03: every pre-2024-03 month of the underlying was read (census p_basis) and none is sealed; a test would need 2024-03 onward (not sealed for these codes; outside Q7's pre-2024-03 rule); clean test window 0.0 months (none: None). Cost (estimates): discovery USD 0.00, test USD 0.00, all USD 0.00; basis: no clean pre-2024-03 test window: nothing to buy before 2024-03. Quotes to obtain: none.
- Combination (sums over members; clean window = the shortest member's): discovery USD 0.00, all USD 4.26, clean test window 0.0 months.

### Dossier EQ3m|F04: pool EQ3m ['MYM', 'MNQ', 'RTY'], F04 US macro release drift

Pool mechanism: as EQ3 with the micro Dow (MYM) in place of YM; YM and MYM are one underlying and never pool together (pooling one price path twice would overstate K_eff).

*DOW (Dow Jones Industrial Average)*: mechanism, participant flow, horizon, evidence rows and R1 overlap exactly as in dossier YM|F04 (same underlying, same family).

*NASDAQ (Nasdaq-100)*: mechanism, participant flow, horizon, evidence rows and R1 overlap exactly as in dossier MNQ|F04 (same underlying, same family).

*RUSSELL (Russell 2000)*: mechanism, participant flow, horizon, evidence rows and R1 overlap exactly as in dossier RTY|F04 (same underlying, same family).

Band and horizon: documented horizon(s) [20, 60] min lie outside B (30-30 min) (documented [20, 30, 60] min). C173 h_c 30; C180 h_c 30

Cost and power at h_c (ticks of the member's own tick; e80 = SR80 sqrt(T) sigma_hc / sqrt(K)):

| id | venue | band | h_c | member | c_f | sigma_hc | c_f/sigma | p_be emp / norm | p_1 emp / norm | K_year | K_disc | K_test | e80 disc G3+G4 / G3 / test | c_f + e80_test |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C173 | mffu | 30-30 | 30 | MYM | 5.300 | 63.23 | 0.0838 | 0.5583 / 0.5525 | 0.5694 / 0.5624 | 67.6 | 213.6 | 233.4 | 28.18 / 24.72 / 23.64 | 28.94 |
| C173 | mffu | 30-30 | 30 | MNQ | 5.300 | 147.10 | 0.0360 | 0.5246 / 0.5226 | 0.5292 / 0.5268 | 67.6 | 213.6 | 233.4 | 65.56 / 57.51 / 54.99 | 60.29 |
| C173 | mffu | 30-30 | 30 | RTY | 2.436 | 51.75 | 0.0471 | 0.5328 / 0.5295 | 0.5463 / 0.5416 | 67.6 | 213.6 | 233.4 | 23.06 / 20.23 / 19.34 | 21.78 |
| C180 | ibkr | 30-30 | 30 | MYM | 6.340 | 63.23 | 0.1003 | 0.5698 / 0.5628 | 0.5808 / 0.5727 | 67.6 | 213.6 | 233.4 | 28.18 / 24.72 / 23.64 | 29.98 |
| C180 | ibkr | 30-30 | 30 | MNQ | 6.344 | 147.10 | 0.0431 | 0.5294 / 0.5270 | 0.5340 / 0.5313 | 67.6 | 213.6 | 233.4 | 65.56 / 57.51 / 54.99 | 61.33 |
| C180 | ibkr | 30-30 | 30 | RTY | 2.396 | 51.75 | 0.0463 | 0.5323 / 0.5290 | 0.5458 / 0.5411 | 67.6 | 213.6 | 233.4 | 23.06 / 20.23 / 19.34 | 21.74 |

Prop fit (one contract) and own-broker fit:

| id | venue | member | DLL (USD) / MLL | DLL/(sigma v) | flat-by-close PT, latest start | payout threshold vs sqrt(n/day) sigma v | news events a week | gates | queue-limit c_lim (passive entry / both) | margin, sigma_day |
|---|---|---|---|---|---|---|---|---|---|---|
| C173 | mffu | MYM | 1000.0 / 2000.0 | 31.63 | 13:10, 12:30 | 0 vs 16.38 (below) | 0.000 | none | - | - |
| C173 | mffu | MNQ | 1000.0 / 2000.0 | 13.60 | 13:10, 12:30 | 0 vs 38.10 (below) | 0.000 | none | - | - |
| C173 | mffu | RTY | 1000.0 / 2000.0 | 3.86 | 13:10, 12:30 | 0 vs 134.03 (below) | 0.000 | none | - | - |
| C180 | ibkr | MYM | none (own account) | - | none, 12:30 | - | 0 | none | not computed | intraday initial USD 1269.99 (overnight 1814.27); sigma_cc 275.49 ticks = USD 137.74 |
| C180 | ibkr | MNQ | none (own account) | - | none, 12:30 | - | 0 | none | not computed | intraday initial USD 4622.90 (overnight 6604.14); sigma_cc 699.90 ticks = USD 349.95 |
| C180 | ibkr | RTY | none (own account) | - | none, 12:30 | - | 0 | none | not computed | intraday initial USD 8760.56 (overnight 12515.08); sigma_cc 237.81 ticks = USD 1189.04 |

Data needed:

- MYM: schema ohlcv-1m (YM price path). Discovery 2020-12-01..2024-02-29 (39 months; bars owned: True); test 2015-10-01..2019-04-30 (43 months; never read, unsealed, not owned: buy); clean test window 106.97 months (never read, unsealed: ['2010-06-06', '2019-05-06']). Cost (estimates): discovery USD 0.00, test USD 4.26, all USD 4.26; basis: estimate: E.12 quote USD 10.50261 for 106 monthly ohlcv-1m chunks 2010-07..2019-04 (reports/stage_e16_windows.json products.YM) = USD 0.0991/month x 43. Quotes to obtain: GLBX.MDP3 ohlcv-1m YM.v.0 2015-10-01..2019-04-30. Not priced: release calendar (E.20 frozen calendar covers 2019-05..2024-02 only; no 2010-2019 file for NFP, CPI, PPI, GDP, ISM: macro_calendars.md section 3); consensus forecasts only for a surprise-signed variant (vendor data, not owned, cost unknown).
- MNQ: schema ohlcv-1m (NQ price path). Discovery 2020-12-01..2024-02-29 (39 months; bars owned: True); test no clean window of 36 months or more before 2024-03: every pre-2024-03 month of the underlying was read (census p_basis) and none is sealed; a test would need 2024-03 onward (not sealed for these codes; outside Q7's pre-2024-03 rule); clean test window 0.82 months (never read, unsealed: ['2010-06-06', '2010-07-01']). Cost (estimates): discovery USD 0.00, test USD 0.00, all USD 0.00; basis: no clean pre-2024-03 test window: nothing to buy before 2024-03. Quotes to obtain: none. Not priced: release calendar (E.20 frozen calendar covers 2019-05..2024-02 only; no 2010-2019 file for NFP, CPI, PPI, GDP, ISM: macro_calendars.md section 3); consensus forecasts only for a surprise-signed variant (vendor data, not owned, cost unknown).
- RTY: schema ohlcv-1m (RTY price path). Discovery 2020-12-01..2024-02-29 (39 months; bars owned: True); test no clean window of 36 months or more before 2024-03: every pre-2024-03 month of the underlying was read (census p_basis) and none is sealed; a test would need 2024-03 onward (not sealed for these codes; outside Q7's pre-2024-03 rule); clean test window 0.0 months (none: None). Cost (estimates): discovery USD 0.00, test USD 0.00, all USD 0.00; basis: no clean pre-2024-03 test window: nothing to buy before 2024-03. Quotes to obtain: none. Not priced: release calendar (E.20 frozen calendar covers 2019-05..2024-02 only; no 2010-2019 file for NFP, CPI, PPI, GDP, ISM: macro_calendars.md section 3); consensus forecasts only for a surprise-signed variant (vendor data, not owned, cost unknown).
- Combination (sums over members; clean window = the shortest member's): discovery USD 0.00, all USD 4.26, clean test window 0.0 months.

### Dossier EQ3m|F05: pool EQ3m ['MYM', 'MNQ', 'RTY'], F05 FOMC post-statement drift

Pool mechanism: as EQ3 with the micro Dow (MYM) in place of YM; YM and MYM are one underlying and never pool together (pooling one price path twice would overstate K_eff).

*DOW (Dow Jones Industrial Average)*: mechanism, participant flow, horizon, evidence rows and R1 overlap exactly as in dossier YM|F05 (same underlying, same family).

*NASDAQ (Nasdaq-100)*: mechanism, participant flow, horizon, evidence rows and R1 overlap exactly as in dossier MNQ|F05 (same underlying, same family).

*RUSSELL (Russell 2000)*: mechanism, participant flow, horizon, evidence rows and R1 overlap exactly as in dossier RTY|F05 (same underlying, same family).

Band and horizon: documented horizon(s) [120] min lie outside B (30-30 min) (documented [30, 120] min). C174 h_c 30; C181 h_c 30

Cost and power at h_c (ticks of the member's own tick; e80 = SR80 sqrt(T) sigma_hc / sqrt(K)):

| id | venue | band | h_c | member | c_f | sigma_hc | c_f/sigma | p_be emp / norm | p_1 emp / norm | K_year | K_disc | K_test | e80 disc G3+G4 / G3 / test | c_f + e80_test |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C174 | mffu | 30-30 | 30 | MYM | 5.300 | 63.23 | 0.0838 | 0.5583 / 0.5525 | 0.5694 / 0.5624 | 8.0 | 25.3 | 27.6 | 81.93 / 71.86 / 68.72 | 74.02 |
| C174 | mffu | 30-30 | 30 | MNQ | 5.300 | 147.10 | 0.0360 | 0.5246 / 0.5226 | 0.5292 / 0.5268 | 8.0 | 25.3 | 27.6 | 190.60 / 167.18 / 159.86 | 165.16 |
| C174 | mffu | 30-30 | 30 | RTY | 2.436 | 51.75 | 0.0471 | 0.5328 / 0.5295 | 0.5463 / 0.5416 | 8.0 | 25.3 | 27.6 | 67.05 / 58.81 / 56.24 | 58.68 |
| C181 | ibkr | 30-30 | 30 | MYM | 6.340 | 63.23 | 0.1003 | 0.5698 / 0.5628 | 0.5808 / 0.5727 | 8.0 | 25.3 | 27.6 | 81.93 / 71.86 / 68.72 | 75.06 |
| C181 | ibkr | 30-30 | 30 | MNQ | 6.344 | 147.10 | 0.0431 | 0.5294 / 0.5270 | 0.5340 / 0.5313 | 8.0 | 25.3 | 27.6 | 190.60 / 167.18 / 159.86 | 166.20 |
| C181 | ibkr | 30-30 | 30 | RTY | 2.396 | 51.75 | 0.0463 | 0.5323 / 0.5290 | 0.5458 / 0.5411 | 8.0 | 25.3 | 27.6 | 67.05 / 58.81 / 56.24 | 58.64 |

Prop fit (one contract) and own-broker fit:

| id | venue | member | DLL (USD) / MLL | DLL/(sigma v) | flat-by-close PT, latest start | payout threshold vs sqrt(n/day) sigma v | news events a week | gates | queue-limit c_lim (passive entry / both) | margin, sigma_day |
|---|---|---|---|---|---|---|---|---|---|---|
| C174 | mffu | MYM | 1000.0 / 2000.0 | 31.63 | 13:10, 12:30 | 0 vs 5.63 (below) | 0.000 | none | - | - |
| C174 | mffu | MNQ | 1000.0 / 2000.0 | 13.60 | 13:10, 12:30 | 0 vs 13.11 (below) | 0.000 | none | - | - |
| C174 | mffu | RTY | 1000.0 / 2000.0 | 3.86 | 13:10, 12:30 | 0 vs 46.10 (below) | 0.000 | none | - | - |
| C181 | ibkr | MYM | none (own account) | - | none, 12:30 | - | 0 | none | not computed | intraday initial USD 1269.99 (overnight 1814.27); sigma_cc 275.49 ticks = USD 137.74 |
| C181 | ibkr | MNQ | none (own account) | - | none, 12:30 | - | 0 | none | not computed | intraday initial USD 4622.90 (overnight 6604.14); sigma_cc 699.90 ticks = USD 349.95 |
| C181 | ibkr | RTY | none (own account) | - | none, 12:30 | - | 0 | none | not computed | intraday initial USD 8760.56 (overnight 12515.08); sigma_cc 237.81 ticks = USD 1189.04 |

Data needed:

- MYM: schema ohlcv-1m (YM price path). Discovery 2020-12-01..2024-02-29 (39 months; bars owned: True); test 2015-10-01..2019-04-30 (43 months; never read, unsealed, not owned: buy); clean test window 106.97 months (never read, unsealed: ['2010-06-06', '2019-05-06']). Cost (estimates): discovery USD 0.00, test USD 4.26, all USD 4.26; basis: estimate: E.12 quote USD 10.50261 for 106 monthly ohlcv-1m chunks 2010-07..2019-04 (reports/stage_e16_windows.json products.YM) = USD 0.0991/month x 43. Quotes to obtain: GLBX.MDP3 ohlcv-1m YM.v.0 2015-10-01..2019-04-30. Not priced: FOMC statement dates and times (calendar files 2010-2024 exist: macro_calendars.md section 3).
- MNQ: schema ohlcv-1m (NQ price path). Discovery 2020-12-01..2024-02-29 (39 months; bars owned: True); test no clean window of 36 months or more before 2024-03: every pre-2024-03 month of the underlying was read (census p_basis) and none is sealed; a test would need 2024-03 onward (not sealed for these codes; outside Q7's pre-2024-03 rule); clean test window 0.82 months (never read, unsealed: ['2010-06-06', '2010-07-01']). Cost (estimates): discovery USD 0.00, test USD 0.00, all USD 0.00; basis: no clean pre-2024-03 test window: nothing to buy before 2024-03. Quotes to obtain: none. Not priced: FOMC statement dates and times (calendar files 2010-2024 exist: macro_calendars.md section 3).
- RTY: schema ohlcv-1m (RTY price path). Discovery 2020-12-01..2024-02-29 (39 months; bars owned: True); test no clean window of 36 months or more before 2024-03: every pre-2024-03 month of the underlying was read (census p_basis) and none is sealed; a test would need 2024-03 onward (not sealed for these codes; outside Q7's pre-2024-03 rule); clean test window 0.0 months (none: None). Cost (estimates): discovery USD 0.00, test USD 0.00, all USD 0.00; basis: no clean pre-2024-03 test window: nothing to buy before 2024-03. Quotes to obtain: none. Not priced: FOMC statement dates and times (calendar files 2010-2024 exist: macro_calendars.md section 3).
- Combination (sums over members; clean window = the shortest member's): discovery USD 0.00, all USD 4.26, clean test window 0.0 months.

### Dossier EQ3m|F08: pool EQ3m ['MYM', 'MNQ', 'RTY'], F08 session and overnight-to-day handoff

Pool mechanism: as EQ3 with the micro Dow (MYM) in place of YM; YM and MYM are one underlying and never pool together (pooling one price path twice would overstate K_eff).

*DOW (Dow Jones Industrial Average)*: mechanism, participant flow, horizon, evidence rows and R1 overlap exactly as in dossier YM|F08 (same underlying, same family).

*NASDAQ (Nasdaq-100)*: mechanism, participant flow, horizon, evidence rows and R1 overlap exactly as in dossier MNQ|F08 (same underlying, same family).

*RUSSELL (Russell 2000)*: mechanism, participant flow, horizon, evidence rows and R1 overlap exactly as in dossier RTY|F08 (same underlying, same family).

Band and horizon: documented horizon(s) [60] min lie outside B (30-30 min) (documented [30, 60] min). C175 h_c 30; C182 h_c 30

Cost and power at h_c (ticks of the member's own tick; e80 = SR80 sqrt(T) sigma_hc / sqrt(K)):

| id | venue | band | h_c | member | c_f | sigma_hc | c_f/sigma | p_be emp / norm | p_1 emp / norm | K_year | K_disc | K_test | e80 disc G3+G4 / G3 / test | c_f + e80_test |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C175 | mffu | 30-30 | 30 | MYM | 5.300 | 63.23 | 0.0838 | 0.5583 / 0.5525 | 0.5694 / 0.5624 | 252.0 | 796.0 | 870.0 | 14.60 / 12.80 / 12.24 | 17.54 |
| C175 | mffu | 30-30 | 30 | MNQ | 5.300 | 147.10 | 0.0360 | 0.5246 / 0.5226 | 0.5292 / 0.5268 | 252.0 | 796.0 | 870.0 | 33.96 / 29.79 / 28.48 | 33.78 |
| C175 | mffu | 30-30 | 30 | RTY | 2.436 | 51.75 | 0.0471 | 0.5328 / 0.5295 | 0.5463 / 0.5416 | 252.0 | 796.0 | 870.0 | 11.95 / 10.48 / 10.02 | 12.46 |
| C182 | ibkr | 30-30 | 30 | MYM | 6.340 | 63.23 | 0.1003 | 0.5698 / 0.5628 | 0.5808 / 0.5727 | 252.0 | 796.0 | 870.0 | 14.60 / 12.80 / 12.24 | 18.58 |
| C182 | ibkr | 30-30 | 30 | MNQ | 6.344 | 147.10 | 0.0431 | 0.5294 / 0.5270 | 0.5340 / 0.5313 | 252.0 | 796.0 | 870.0 | 33.96 / 29.79 / 28.48 | 34.83 |
| C182 | ibkr | 30-30 | 30 | RTY | 2.396 | 51.75 | 0.0463 | 0.5323 / 0.5290 | 0.5458 / 0.5411 | 252.0 | 796.0 | 870.0 | 11.95 / 10.48 / 10.02 | 12.42 |

Prop fit (one contract) and own-broker fit:

| id | venue | member | DLL (USD) / MLL | DLL/(sigma v) | flat-by-close PT, latest start | payout threshold vs sqrt(n/day) sigma v | news events a week | gates | queue-limit c_lim (passive entry / both) | margin, sigma_day |
|---|---|---|---|---|---|---|---|---|---|---|
| C175 | mffu | MYM | 1000.0 / 2000.0 | 31.63 | 13:10, 12:30 | 0 vs 31.62 (below) | 0.000 | none | - | - |
| C175 | mffu | MNQ | 1000.0 / 2000.0 | 13.60 | 13:10, 12:30 | 0 vs 73.55 (below) | 0.000 | none | - | - |
| C175 | mffu | RTY | 1000.0 / 2000.0 | 3.86 | 13:10, 12:30 | 0 vs 258.76 (below) | 0.000 | none | - | - |
| C182 | ibkr | MYM | none (own account) | - | none, 12:30 | - | 0 | none | not computed | intraday initial USD 1269.99 (overnight 1814.27); sigma_cc 275.49 ticks = USD 137.74 |
| C182 | ibkr | MNQ | none (own account) | - | none, 12:30 | - | 0 | none | not computed | intraday initial USD 4622.90 (overnight 6604.14); sigma_cc 699.90 ticks = USD 349.95 |
| C182 | ibkr | RTY | none (own account) | - | none, 12:30 | - | 0 | none | not computed | intraday initial USD 8760.56 (overnight 12515.08); sigma_cc 237.81 ticks = USD 1189.04 |

Data needed:

- MYM: schema ohlcv-1m (YM price path). Discovery 2020-12-01..2024-02-29 (39 months; bars owned: True); test 2015-10-01..2019-04-30 (43 months; never read, unsealed, not owned: buy); clean test window 106.97 months (never read, unsealed: ['2010-06-06', '2019-05-06']). Cost (estimates): discovery USD 0.00, test USD 4.26, all USD 4.26; basis: estimate: E.12 quote USD 10.50261 for 106 monthly ohlcv-1m chunks 2010-07..2019-04 (reports/stage_e16_windows.json products.YM) = USD 0.0991/month x 43. Quotes to obtain: GLBX.MDP3 ohlcv-1m YM.v.0 2015-10-01..2019-04-30.
- MNQ: schema ohlcv-1m (NQ price path). Discovery 2020-12-01..2024-02-29 (39 months; bars owned: True); test no clean window of 36 months or more before 2024-03: every pre-2024-03 month of the underlying was read (census p_basis) and none is sealed; a test would need 2024-03 onward (not sealed for these codes; outside Q7's pre-2024-03 rule); clean test window 0.82 months (never read, unsealed: ['2010-06-06', '2010-07-01']). Cost (estimates): discovery USD 0.00, test USD 0.00, all USD 0.00; basis: no clean pre-2024-03 test window: nothing to buy before 2024-03. Quotes to obtain: none.
- RTY: schema ohlcv-1m (RTY price path). Discovery 2020-12-01..2024-02-29 (39 months; bars owned: True); test no clean window of 36 months or more before 2024-03: every pre-2024-03 month of the underlying was read (census p_basis) and none is sealed; a test would need 2024-03 onward (not sealed for these codes; outside Q7's pre-2024-03 rule); clean test window 0.0 months (none: None). Cost (estimates): discovery USD 0.00, test USD 0.00, all USD 0.00; basis: no clean pre-2024-03 test window: nothing to buy before 2024-03. Quotes to obtain: none.
- Combination (sums over members; clean window = the shortest member's): discovery USD 0.00, all USD 4.26, clean test window 0.0 months.

### Dossier EQ3m|F10: pool EQ3m ['MYM', 'MNQ', 'RTY'], F10 order-book state at 5 min and longer

Pool mechanism: as EQ3 with the micro Dow (MYM) in place of YM; YM and MYM are one underlying and never pool together (pooling one price path twice would overstate K_eff).

*DOW (Dow Jones Industrial Average)*: mechanism, participant flow, horizon, evidence rows and R1 overlap exactly as in dossier YM|F10 (same underlying, same family).

*NASDAQ (Nasdaq-100)*: mechanism, participant flow, horizon, evidence rows and R1 overlap exactly as in dossier MNQ|F10 (same underlying, same family).

*RUSSELL (Russell 2000)*: mechanism, participant flow, horizon, evidence rows and R1 overlap exactly as in dossier RTY|F10 (same underlying, same family).

Band and horizon: documented horizon(s) [5, 15] min lie outside B (30-30 min) (documented [5, 15, 30] min). C176 h_c 30; C183 h_c 30

Cost and power at h_c (ticks of the member's own tick; e80 = SR80 sqrt(T) sigma_hc / sqrt(K)):

| id | venue | band | h_c | member | c_f | sigma_hc | c_f/sigma | p_be emp / norm | p_1 emp / norm | K_year | K_disc | K_test | e80 disc G3+G4 / G3 / test | c_f + e80_test |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C176 | mffu | 30-30 | 30 | MYM | 5.300 | 63.23 | 0.0838 | 0.5583 / 0.5525 | 0.5694 / 0.5624 | 3276.0 | 10348.0 | 11310.0 | 4.05 / 3.55 / 3.40 | 8.70 |
| C176 | mffu | 30-30 | 30 | MNQ | 5.300 | 147.10 | 0.0360 | 0.5246 / 0.5226 | 0.5292 / 0.5268 | 3276.0 | 10348.0 | 11310.0 | 9.42 / 8.26 / 7.90 | 13.20 |
| C176 | mffu | 30-30 | 30 | RTY | 2.436 | 51.75 | 0.0471 | 0.5328 / 0.5295 | 0.5463 / 0.5416 | 3276.0 | 10348.0 | 11310.0 | 3.31 / 2.91 / 2.78 | 5.22 |
| C183 | ibkr | 30-30 | 30 | MYM | 6.340 | 63.23 | 0.1003 | 0.5698 / 0.5628 | 0.5808 / 0.5727 | 3276.0 | 10348.0 | 11310.0 | 4.05 / 3.55 / 3.40 | 9.74 |
| C183 | ibkr | 30-30 | 30 | MNQ | 6.344 | 147.10 | 0.0431 | 0.5294 / 0.5270 | 0.5340 / 0.5313 | 3276.0 | 10348.0 | 11310.0 | 9.42 / 8.26 / 7.90 | 14.24 |
| C183 | ibkr | 30-30 | 30 | RTY | 2.396 | 51.75 | 0.0463 | 0.5323 / 0.5290 | 0.5458 / 0.5411 | 3276.0 | 10348.0 | 11310.0 | 3.31 / 2.91 / 2.78 | 5.18 |

Prop fit (one contract) and own-broker fit:

| id | venue | member | DLL (USD) / MLL | DLL/(sigma v) | flat-by-close PT, latest start | payout threshold vs sqrt(n/day) sigma v | news events a week | gates | queue-limit c_lim (passive entry / both) | margin, sigma_day |
|---|---|---|---|---|---|---|---|---|---|---|
| C176 | mffu | MYM | 1000.0 / 2000.0 | 31.63 | 13:10, 12:30 | 0 vs 114.00 (below) | 0.000 | none | - | - |
| C176 | mffu | MNQ | 1000.0 / 2000.0 | 13.60 | 13:10, 12:30 | 0 vs 265.20 (below) | 0.000 | none | - | - |
| C176 | mffu | RTY | 1000.0 / 2000.0 | 3.86 | 13:10, 12:30 | 0 vs 932.96 (below) | 0.000 | none | - | - |
| C183 | ibkr | MYM | none (own account) | - | none, 12:30 | - | 0 | none | not computed | intraday initial USD 1269.99 (overnight 1814.27); sigma_cc 275.49 ticks = USD 137.74 |
| C183 | ibkr | MNQ | none (own account) | - | none, 12:30 | - | 0 | none | not computed | intraday initial USD 4622.90 (overnight 6604.14); sigma_cc 699.90 ticks = USD 349.95 |
| C183 | ibkr | RTY | none (own account) | - | none, 12:30 | - | 0 | none | not computed | intraday initial USD 8760.56 (overnight 12515.08); sigma_cc 237.81 ticks = USD 1189.04 |

Data needed:

- MYM: schema mbo (YM; MBO from 2017-05-21). Discovery 2020-12-01..2024-02-29 (39 months; bars owned: True); test 2015-10-01..2019-04-30 (43 months; never read, unsealed, not owned: buy); clean test window 106.97 months (never read, unsealed: ['2010-06-06', '2019-05-06']). Cost (estimates): discovery USD 227.57, test USD 250.91, all USD 478.48; basis: census estimate k = USD 5.8351/month (F2_data_access codes.YM.k_usd_month, scaled from mbp-1 (estimate)) x months; MYM's F10 signal is priced on YM's book (the full-size leader of the same underlying; MYM's own MBO starts 2019-05-06 and its own k is USD 9.65/month); an assumption. Quotes to obtain: GLBX.MDP3 mbo YM.v.0 2020-12-01..2024-02-29; GLBX.MDP3 mbo YM.v.0 2015-10-01..2019-04-30 (MBP-10 before 2017-05-21). Not priced: MBP-10 is the highest granularity before 2017-05-21 (F2_data_access databento_dataset).
- MNQ: schema mbo (MNQ; MBO from 2019-05-06). Discovery 2020-12-01..2024-02-29 (39 months; bars owned: True); test no clean window of 36 months or more before 2024-03: every pre-2024-03 month of the underlying was read (census p_basis) and none is sealed; a test would need 2024-03 onward (not sealed for these codes; outside Q7's pre-2024-03 rule); clean test window 0.82 months (never read, unsealed: ['2010-06-06', '2010-07-01']). Cost (estimates): discovery USD 2026.86, test USD 0.00, all USD 2026.86; basis: census estimate k = USD 51.9707/month (F2_data_access codes.MNQ.k_usd_month, scaled from mbp-1 (estimate)) x months; priced on MNQ's own MBO; NQ's book (census k USD 22.88/month) would be cheaper but NQ is excluded (V49: 'NQ is not used as a pilot or comparison contract'). Quotes to obtain: GLBX.MDP3 mbo MNQ.v.0 2020-12-01..2024-02-29. Not priced: MBP-10 is the highest granularity before 2017-05-21 (F2_data_access databento_dataset).
- RTY: schema mbo (RTY; MBO from 2017-07-10). Discovery 2020-12-01..2024-02-29 (39 months; bars owned: True); test no clean window of 36 months or more before 2024-03: every pre-2024-03 month of the underlying was read (census p_basis) and none is sealed; a test would need 2024-03 onward (not sealed for these codes; outside Q7's pre-2024-03 rule); clean test window 0.0 months (none: None). Cost (estimates): discovery USD 280.54, test USD 0.00, all USD 280.54; basis: census estimate k = USD 7.1933/month (F2_data_access codes.RTY.k_usd_month, scaled from mbp-1 (estimate)) x months. Quotes to obtain: GLBX.MDP3 mbo RTY.v.0 2020-12-01..2024-02-29. Not priced: MBP-10 is the highest granularity before 2017-05-21 (F2_data_access databento_dataset).
- Combination (sums over members; clean window = the shortest member's): discovery USD 2534.97, all USD 2785.88, clean test window 0.0 months.

### Dossier EQ3m|F11: pool EQ3m ['MYM', 'MNQ', 'RTY'], F11 own-price-path trend and reversal

Pool mechanism: as EQ3 with the micro Dow (MYM) in place of YM; YM and MYM are one underlying and never pool together (pooling one price path twice would overstate K_eff).

*DOW (Dow Jones Industrial Average)*: mechanism, participant flow, horizon, evidence rows and R1 overlap exactly as in dossier YM|F11 (same underlying, same family).

*NASDAQ (Nasdaq-100)*: mechanism, participant flow, horizon, evidence rows and R1 overlap exactly as in dossier MNQ|F11 (same underlying, same family).

*RUSSELL (Russell 2000)*: mechanism, participant flow, horizon, evidence rows and R1 overlap exactly as in dossier RTY|F11 (same underlying, same family).

Band and horizon: documented horizon(s) [5, 15, 60] min lie outside B (30-30 min) (documented [5, 15, 60] min). C177 h_c 30 (h_c not a documented horizon); C184 h_c 30 (h_c not a documented horizon)

Cost and power at h_c (ticks of the member's own tick; e80 = SR80 sqrt(T) sigma_hc / sqrt(K)):

| id | venue | band | h_c | member | c_f | sigma_hc | c_f/sigma | p_be emp / norm | p_1 emp / norm | K_year | K_disc | K_test | e80 disc G3+G4 / G3 / test | c_f + e80_test |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C177 | mffu | 30-30 | 30 | MYM | 5.300 | 63.23 | 0.0838 | 0.5583 / 0.5525 | 0.5694 / 0.5624 | 3276.0 | 10348.0 | 11310.0 | 4.05 / 3.55 / 3.40 | 8.70 |
| C177 | mffu | 30-30 | 30 | MNQ | 5.300 | 147.10 | 0.0360 | 0.5246 / 0.5226 | 0.5292 / 0.5268 | 3276.0 | 10348.0 | 11310.0 | 9.42 / 8.26 / 7.90 | 13.20 |
| C177 | mffu | 30-30 | 30 | RTY | 2.436 | 51.75 | 0.0471 | 0.5328 / 0.5295 | 0.5463 / 0.5416 | 3276.0 | 10348.0 | 11310.0 | 3.31 / 2.91 / 2.78 | 5.22 |
| C184 | ibkr | 30-30 | 30 | MYM | 6.340 | 63.23 | 0.1003 | 0.5698 / 0.5628 | 0.5808 / 0.5727 | 3276.0 | 10348.0 | 11310.0 | 4.05 / 3.55 / 3.40 | 9.74 |
| C184 | ibkr | 30-30 | 30 | MNQ | 6.344 | 147.10 | 0.0431 | 0.5294 / 0.5270 | 0.5340 / 0.5313 | 3276.0 | 10348.0 | 11310.0 | 9.42 / 8.26 / 7.90 | 14.24 |
| C184 | ibkr | 30-30 | 30 | RTY | 2.396 | 51.75 | 0.0463 | 0.5323 / 0.5290 | 0.5458 / 0.5411 | 3276.0 | 10348.0 | 11310.0 | 3.31 / 2.91 / 2.78 | 5.18 |

Prop fit (one contract) and own-broker fit:

| id | venue | member | DLL (USD) / MLL | DLL/(sigma v) | flat-by-close PT, latest start | payout threshold vs sqrt(n/day) sigma v | news events a week | gates | queue-limit c_lim (passive entry / both) | margin, sigma_day |
|---|---|---|---|---|---|---|---|---|---|---|
| C177 | mffu | MYM | 1000.0 / 2000.0 | 31.63 | 13:10, 12:30 | 0 vs 114.00 (below) | 0.000 | none | - | - |
| C177 | mffu | MNQ | 1000.0 / 2000.0 | 13.60 | 13:10, 12:30 | 0 vs 265.20 (below) | 0.000 | none | - | - |
| C177 | mffu | RTY | 1000.0 / 2000.0 | 3.86 | 13:10, 12:30 | 0 vs 932.96 (below) | 0.000 | none | - | - |
| C184 | ibkr | MYM | none (own account) | - | none, 12:30 | - | 0 | none | not computed | intraday initial USD 1269.99 (overnight 1814.27); sigma_cc 275.49 ticks = USD 137.74 |
| C184 | ibkr | MNQ | none (own account) | - | none, 12:30 | - | 0 | none | not computed | intraday initial USD 4622.90 (overnight 6604.14); sigma_cc 699.90 ticks = USD 349.95 |
| C184 | ibkr | RTY | none (own account) | - | none, 12:30 | - | 0 | none | not computed | intraday initial USD 8760.56 (overnight 12515.08); sigma_cc 237.81 ticks = USD 1189.04 |

Data needed:

- MYM: schema ohlcv-1m (YM price path). Discovery 2020-12-01..2024-02-29 (39 months; bars owned: True); test 2015-10-01..2019-04-30 (43 months; never read, unsealed, not owned: buy); clean test window 106.97 months (never read, unsealed: ['2010-06-06', '2019-05-06']). Cost (estimates): discovery USD 0.00, test USD 4.26, all USD 4.26; basis: estimate: E.12 quote USD 10.50261 for 106 monthly ohlcv-1m chunks 2010-07..2019-04 (reports/stage_e16_windows.json products.YM) = USD 0.0991/month x 43. Quotes to obtain: GLBX.MDP3 ohlcv-1m YM.v.0 2015-10-01..2019-04-30.
- MNQ: schema ohlcv-1m (NQ price path). Discovery 2020-12-01..2024-02-29 (39 months; bars owned: True); test no clean window of 36 months or more before 2024-03: every pre-2024-03 month of the underlying was read (census p_basis) and none is sealed; a test would need 2024-03 onward (not sealed for these codes; outside Q7's pre-2024-03 rule); clean test window 0.82 months (never read, unsealed: ['2010-06-06', '2010-07-01']). Cost (estimates): discovery USD 0.00, test USD 0.00, all USD 0.00; basis: no clean pre-2024-03 test window: nothing to buy before 2024-03. Quotes to obtain: none.
- RTY: schema ohlcv-1m (RTY price path). Discovery 2020-12-01..2024-02-29 (39 months; bars owned: True); test no clean window of 36 months or more before 2024-03: every pre-2024-03 month of the underlying was read (census p_basis) and none is sealed; a test would need 2024-03 onward (not sealed for these codes; outside Q7's pre-2024-03 rule); clean test window 0.0 months (none: None). Cost (estimates): discovery USD 0.00, test USD 0.00, all USD 0.00; basis: no clean pre-2024-03 test window: nothing to buy before 2024-03. Quotes to obtain: none.
- Combination (sums over members; clean window = the shortest member's): discovery USD 0.00, all USD 4.26, clean test window 0.0 months.

### Dossier EQ3m|F12: pool EQ3m ['MYM', 'MNQ', 'RTY'], F12 expiry and option-hedging days

Pool mechanism: as EQ3 with the micro Dow (MYM) in place of YM; YM and MYM are one underlying and never pool together (pooling one price path twice would overstate K_eff).

*DOW (Dow Jones Industrial Average)*: mechanism, participant flow, horizon, evidence rows and R1 overlap exactly as in dossier YM|F12 (same underlying, same family).

*NASDAQ (Nasdaq-100)*: mechanism, participant flow, horizon, evidence rows and R1 overlap exactly as in dossier MNQ|F12 (same underlying, same family).

*RUSSELL (Russell 2000)*: mechanism, participant flow, horizon, evidence rows and R1 overlap exactly as in dossier RTY|F12 (same underlying, same family).

Band and horizon: documented horizon(s) [10, 60] min lie outside B (30-30 min) (documented [10, 30, 60] min). C178 h_c 30; C185 h_c 30

Cost and power at h_c (ticks of the member's own tick; e80 = SR80 sqrt(T) sigma_hc / sqrt(K)):

| id | venue | band | h_c | member | c_f | sigma_hc | c_f/sigma | p_be emp / norm | p_1 emp / norm | K_year | K_disc | K_test | e80 disc G3+G4 / G3 / test | c_f + e80_test |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C178 | mffu | 30-30 | 30 | MYM | 5.300 | 63.23 | 0.0838 | 0.5583 / 0.5525 | 0.5694 / 0.5624 | 12.0 | 37.9 | 41.4 | 66.89 / 58.68 / 56.11 | 61.41 |
| C178 | mffu | 30-30 | 30 | MNQ | 5.300 | 147.10 | 0.0360 | 0.5246 / 0.5226 | 0.5292 / 0.5268 | 12.0 | 37.9 | 41.4 | 155.62 / 136.50 / 130.53 | 135.83 |
| C178 | mffu | 30-30 | 30 | RTY | 2.436 | 51.75 | 0.0471 | 0.5328 / 0.5295 | 0.5463 / 0.5416 | 12.0 | 37.9 | 41.4 | 54.75 / 48.02 / 45.92 | 48.36 |
| C185 | ibkr | 30-30 | 30 | MYM | 6.340 | 63.23 | 0.1003 | 0.5698 / 0.5628 | 0.5808 / 0.5727 | 12.0 | 37.9 | 41.4 | 66.89 / 58.68 / 56.11 | 62.45 |
| C185 | ibkr | 30-30 | 30 | MNQ | 6.344 | 147.10 | 0.0431 | 0.5294 / 0.5270 | 0.5340 / 0.5313 | 12.0 | 37.9 | 41.4 | 155.62 / 136.50 / 130.53 | 136.87 |
| C185 | ibkr | 30-30 | 30 | RTY | 2.396 | 51.75 | 0.0463 | 0.5323 / 0.5290 | 0.5458 / 0.5411 | 12.0 | 37.9 | 41.4 | 54.75 / 48.02 / 45.92 | 48.32 |

Prop fit (one contract) and own-broker fit:

| id | venue | member | DLL (USD) / MLL | DLL/(sigma v) | flat-by-close PT, latest start | payout threshold vs sqrt(n/day) sigma v | news events a week | gates | queue-limit c_lim (passive entry / both) | margin, sigma_day |
|---|---|---|---|---|---|---|---|---|---|---|
| C178 | mffu | MYM | 1000.0 / 2000.0 | 31.63 | 13:10, 12:30 | 0 vs 6.90 (below) | 0.000 | none | - | - |
| C178 | mffu | MNQ | 1000.0 / 2000.0 | 13.60 | 13:10, 12:30 | 0 vs 16.05 (below) | 0.000 | none | - | - |
| C178 | mffu | RTY | 1000.0 / 2000.0 | 3.86 | 13:10, 12:30 | 0 vs 56.47 (below) | 0.000 | none | - | - |
| C185 | ibkr | MYM | none (own account) | - | none, 12:30 | - | 0 | none | not computed | intraday initial USD 1269.99 (overnight 1814.27); sigma_cc 275.49 ticks = USD 137.74 |
| C185 | ibkr | MNQ | none (own account) | - | none, 12:30 | - | 0 | none | not computed | intraday initial USD 4622.90 (overnight 6604.14); sigma_cc 699.90 ticks = USD 349.95 |
| C185 | ibkr | RTY | none (own account) | - | none, 12:30 | - | 0 | none | not computed | intraday initial USD 8760.56 (overnight 12515.08); sigma_cc 237.81 ticks = USD 1189.04 |

Data needed:

- MYM: schema ohlcv-1m (YM price path). Discovery 2020-12-01..2024-02-29 (39 months; bars owned: True); test 2015-10-01..2019-04-30 (43 months; never read, unsealed, not owned: buy); clean test window 106.97 months (never read, unsealed: ['2010-06-06', '2019-05-06']). Cost (estimates): discovery USD 0.00, test USD 4.26, all USD 4.26; basis: estimate: E.12 quote USD 10.50261 for 106 monthly ohlcv-1m chunks 2010-07..2019-04 (reports/stage_e16_windows.json products.YM) = USD 0.0991/month x 43. Quotes to obtain: GLBX.MDP3 ohlcv-1m YM.v.0 2015-10-01..2019-04-30. Not priced: option open interest by strike for a gamma-conditioned variant (GEX; vendor data, cost unknown; R1-14 used GEX rows 2020-05-29..2024-02-28); the 3rd-Friday variant needs bars and the expiry calendar only.
- MNQ: schema ohlcv-1m (NQ price path). Discovery 2020-12-01..2024-02-29 (39 months; bars owned: True); test no clean window of 36 months or more before 2024-03: every pre-2024-03 month of the underlying was read (census p_basis) and none is sealed; a test would need 2024-03 onward (not sealed for these codes; outside Q7's pre-2024-03 rule); clean test window 0.82 months (never read, unsealed: ['2010-06-06', '2010-07-01']). Cost (estimates): discovery USD 0.00, test USD 0.00, all USD 0.00; basis: no clean pre-2024-03 test window: nothing to buy before 2024-03. Quotes to obtain: none. Not priced: option open interest by strike for a gamma-conditioned variant (GEX; vendor data, cost unknown; R1-14 used GEX rows 2020-05-29..2024-02-28); the 3rd-Friday variant needs bars and the expiry calendar only.
- RTY: schema ohlcv-1m (RTY price path). Discovery 2020-12-01..2024-02-29 (39 months; bars owned: True); test no clean window of 36 months or more before 2024-03: every pre-2024-03 month of the underlying was read (census p_basis) and none is sealed; a test would need 2024-03 onward (not sealed for these codes; outside Q7's pre-2024-03 rule); clean test window 0.0 months (none: None). Cost (estimates): discovery USD 0.00, test USD 0.00, all USD 0.00; basis: no clean pre-2024-03 test window: nothing to buy before 2024-03. Quotes to obtain: none. Not priced: option open interest by strike for a gamma-conditioned variant (GEX; vendor data, cost unknown; R1-14 used GEX rows 2020-05-29..2024-02-28); the 3rd-Friday variant needs bars and the expiry calendar only.
- Combination (sums over members; clean window = the shortest member's): discovery USD 0.00, all USD 4.26, clean test window 0.0 months.

## Evidence row catalog

| row | study | product in study | horizon | data period | sample | net of costs | finding | verified level | venue type |
|---|---|---|---|---|---|---|---|---|---|
| F01.E01 | Baltussen, Da, Lammers, Martens 2021 JFE 142(1), Table 5 Panel B (SB-1, SB-2, SB-3, SB-5) | asset-class pools (17 equity, 16 bond, 21 commodity, 8 currency futures) | 30 min | 2000-2020 subsample | in sample (pooled) | no | beta_ROD x100 (t), R2%: equity 3.98 (6.65) 2.34; bonds 1.53 (3.61) 0.47; commodity 1.04 (2.86) 0.12; currency 0.33 (1.45) 0.04 | full_text | peer-reviewed |
| F01.E02 | Baltussen et al. 2021, Appendix B product rows (SB-8, SB-9, SB-10, SB-12, SB-13, SB-14, SB-15, SB-17, SB-19, SB-21, SB-27) | YM, NQ, ER(Russell), TU, FV, TY, US, GC, SV, NG, AD | 30 min | product start to 2020-05 | in sample + recursive OOS R2 (Clark-West) | no | R2_OOS: NQ 3.76%, Russell 3.15%, YM 2.18%, ZF 0.93%, NG 0.92%, ZN 0.86%, ZT 0.70%, ZB 0.22%, SI 1.01%, 6A 0.17%, GC 0.08%; all significant | full_text | peer-reviewed |
| F01.E03 | Baltussen et al. 2021, Appendix B product rows (SB-18, SB-20, SB-22, SB-23, SB-24, SB-25, SB-26, SB-28, SB-16) | HG, CL, BO, CN, SM, SY, WC, EC, UB | 30 min | to 2020-05 | OOS | no | R2_OOS negative or nil: CL -1.04%, HG -0.25%, UB -3.40%, grains and EC about -0.01 to -0.07% | full_text | peer-reviewed |
| F01.E04 | Baltussen et al. 2021, costs (SB-6) | all | 30 min | 1974-2020 | - | not net, one sentence on ES | no cost-adjusted table; ES positive net Sharpe at a one-tick cost (ES not a candidate) | full_text | peer-reviewed |
| F01.E05 | Gao, Han, Li, Zhou 2018 JFE (via E.20) (EQUITY-36, EQUITY-37, EQUITY-20) | SPY, IWM (other venue, same underlying for RTY/M2K) | 30 min (15:30-16:00 ET) | 1993-2013 (IWM 2000-2013) | in sample + OOS timing | SPY net of spread 2005-2013: 6.52%/yr vs 7.96% gross | first-half-hour sign predicts last half-hour; IWM OOS R2 2.43%; FOMC days stronger (20.04%/yr vs 6.24%) | reused (E.20 full text) | peer-reviewed |
| F01.E06 | Li, Sakkas, Urquhart 2022 J. Financial Markets (EQUITY-38) | S&P 500 cash (not tradable) | 30 min | 2005-10..2017-12 | in sample | gross | 6.567%/yr, Sharpe 1.115 | reused | peer-reviewed |
| F01.E09 | Jin, Kearney, Li, Yang 2020 JFM; DCE study (METALS-33, GRAINS-25, NATGAS-45) | SHFE copper; DCE soybean and meal; Chinese commodities | first -> last half-hour | 2002-2013 | in sample | gross | positive slopes (DCE meal 0.052, R2 0.90%) | full_text | peer-reviewed |
| F01.E10 | Adams, Dim, Eraker, Fontaine, Ornthanalai, Vilkov draft 2026 (EQUITY-39) | ES (cousin) | 60 min | 2018-01..2024-12 | in sample | gross | momentum turns to reversal when dealer net gamma is high: Q4-Q1 -1.777 bp (t -3.93) | reused (full text) | working paper |
| F01.E11 | firmtape blog (dev.to) (EQUITY-40) | SPX | ROD -> LH | 2022-04..2026-08 | - | gross | slope +0.006 (t 0.6), flat every year; conditional on short-gamma closes +0.055 (t 3.1) | reused | pointer (blog) |
| F01.E12 | Rosa 2022 JFM (EQUITY-41, RATES-48) | index futures per snippet [unverified] | overnight -> last half-hour | unknown | OOS | - | predictability disappears out of sample | abstract | peer-reviewed |
| F01.E13 | Majorin 2025 Aalto MSc thesis (EQUITY-46, RATES-41, FX-42) | 20 equity, bond, FX futures | 30 min | 2008-01..2024-10 | - | net | patterns persist but mostly not feasible after costs, especially bond and currency futures | abstract | thesis |
| F01.E14 | Program E.20 H6 (R1-14) (R1-14) | NQ at MNQ cost | 30 min (entry 14:30 CT) | 2020-06..2024-02 | registered test r004-E20H6 | net | T1 gross 1.25 ticks vs 4.08 cost, t -0.53; closed (V38) | reused (program record) | program |
| F01.E15 | Program E.16 H1/H4 (R1-13) (R1-13) | pooled 27 roots incl. YM RTY ZT ZF ZN ZB 6E 6A CL NG GC | settlement-window intraday; next-day reversal | 2010-07..2024-02 (17 roots); 2019-05..2024-02 (10) | registered r002-E16 | net | H1 gross about a quarter of its D8 cost; closed V31 | reused | program |
| F01.E16 | E.32 methods brief R4 table () | CBOT soybean meal | first half-hour -> last half-hour | 1982-2020 | OOS | - | slope -0.95 (t -1.58), OOS R2 < 0 | reused (E.32) | peer-reviewed (Baltussen) |
| F03.E01 | Anderson, McKenzie, Noyes 2024 NCCC-134 WP (GRAINS-18) | ZC, ZS nearby | 10 min, 30 min, to the day close | 2010-2021, 122 WASDE reports | in sample | - | not significant at 10 min, significant at 30 min; soybean reaction grows to the close; corn mostly done by 30 min | full_text | working paper |
| F03.E02 | Huang 2022 dissertation ch. 3 (via E.32 R4) () | corn nearby | 1-60 min after release | 2012-06..2019-08, 104 real-time events | in sample | - | about 75% of the 60-min move by 10 min, 90-100% by 35-45 min; direction-known drift after minute 10: big events +0.65%, small events overshoot (-0.10% after 40 min); the conditioning on the 60-minute sign is not tradable | full_text (E.32) | dissertation |
| F03.E03 | Joseph and Garcia 2016 (GRAINS-21) | ZS | 15-s returns; spike 5-6 min; variance to 30-60 min | 2010-06..2014-05 | in sample | - | no systematic under- or overreaction | full_text | paper |
| F03.E04 | Lehecka, Wang, Garcia 2014 (GRAINS-19, GRAINS-37) | ZC | about 10 min | 2009-07..2012-05 | in sample | - | reactions persist about ten minutes; no systematic under- or overreaction | abstract | peer-reviewed |
| F03.E05 | Adjemian and Irwin 2018 (GRAINS-20) | grain futures | few minutes | 2009-2014 | - | - | volatility spike dissipates within a few trading minutes | abstract | peer-reviewed |
| F03.E06 | Jump clustering (GRAINS-23) | ZC | 2 min | 2008-2015 | - | - | jumps cluster within 2 minutes of the release | reused | paper |
| F03.E07 | farmdoc single episode (GRAINS-52) | ZC, ZS new crop | day | 2025-09-12 | - | - | bearish WASDE, negative first reaction, closed higher (reversal) | full_text | pointer (extension commentary) |
| F03.E08 | EPA RFS / NOPA news (GRAINS-48) | ZL, ZM | day | 2014-2025 news | - | - | RFS announcements move ZL sharply (limit moves); NOPA moves ZM/ZL modestly; no intraday study | snippet | pointer (news) |
| F03.E09 | E.32 R4 per-event table () | ZM, ZS, ZL | - | 39-month window | - | - | NOPA: no intraday study in any source read; about 49 major USDA days and 39 NOPA days in 39 months; post-USDA dropped as an E.33 family for power | reused (E.32) | methods brief |
| F04.E01 | Haynes and Roberts 2015 CFTC OCE (RATES-19) | ZN (and ES) | minutes or seconds | 2012-11..2015-09 | in sample | - | majority of permanent price changes within minutes or seconds after NFP | full_text | regulator paper |
| F04.E03 | Kurov, Sancetta, Strasser, Wolfe 2015/2019 JFQA (EQUITY-17, EQUITY-18, RATES-22) | ES (cousin), ZN | t+10 to t+30 min; pre-release 30 min | 2008-01..2014-03 | in sample | - | some evidence of continuing adjustment 10-30 min after; pre-release drift in 7 of 18 releases (needs the surprise sign) | full_text | peer-reviewed |
| F04.E08 | Takahashi 2025 arXiv (EQUITY-19) | ES order flow | 1 s | n/a | - | - | macro-news shocks dissipate within one second | abstract | preprint |
| F05.E01 | Fleming, Liu, Nguyen NY Fed SR 1188 (2026) (RATES-23) | Treasury yields (cash) | 3 h after statement | 1997..2024-07 | in sample | gross | significant, persistent yield decline after FOMC; null before FOMC and around payrolls | reused (E.20 full text) | central-bank WP |
| F05.E02 | Gao et al. 2018 Table 8 (EQUITY-20) | SPY | last half-hour on FOMC days | 1993-2013 | in sample | gross | intraday momentum 20.04%/yr on FOMC days vs 6.24% | reused | peer-reviewed |
| F05.E06 | Lucca-Moench; Kurov-Wolfe-Gilbert 2021 (EQUITY-21, RATES-25) | SPX; Treasuries | 24 h before | 1994-2011; to 2019 | in sample | - | pre-FOMC equity drift disappeared after 2015; none in Treasuries | reused / abstract | peer-reviewed |
| F08.E03 | Boyarchenko, Larsen, Whelan NY Fed SR 917 / RFS 2023 (EQUITY-50, EQUITY-51) | ES (cousin) | 02:00-03:00 ET (overnight hold) | 1998-2020 | in sample | net of bid-ask | +3.7%/yr gross, Sharpe 1.1 gross, -0.5 after spreads (1:30-3:30: 1.3 gross, 0.3 net) | full_text | peer-reviewed |
| F08.E07 | DCE vs US overnight (GRAINS-42) | DCE soybean, corn | overnight -> day | before/after DCE night trading (~2019) | - | - | overreaction to US overnight returns stopped working after night trading | abstract | paper |
| F08.E08 | Onur and Reiffen (CFTC) (GRAINS-17) | ZC | pre-close to settlement, reversed at next open | 2012-03..06 | in sample | - | settlement-window reversals declined after the 2012 rule change | full_text | regulator paper |
| F08.E09 | E.32 R4 table: Sunday open and SM overnight () | ZM | overnight + first half-hour -> last half-hour | 1982-2020 | OOS | - | CBOT SM overnight + first half-hour: no prediction (Baltussen); planner family 4 (08:30 reopen gap) untested | reused (E.32) | peer-reviewed |
| F08.E13 | Volatility-only session facts (CRUDE-29, CRUDE-48, NATGAS-50, GRAINS-36) | CL, NG, ZC ZS | open/close | various | - | - | jumps cluster at former pit open/close; U-shaped volatility; spreads widest next to the pause | full_text | papers |
| F09.E01 | Zhou, Bagnarosa, Gohin, Pennings, Debie (J. Commodity Markets 2023) (GRAINS-15, GRAINS-16, GRAINS-38) | ZS, ZM, ZL | 1-minute sampling, daily VECM | 2015, 243 days | in sample | - | day-session crush cointegrated on 180 of 243 days, overnight on 52; no fixed leader; no half-life or trading test | full_text | peer-reviewed |
| F09.E02 | Program E.33c ZM search S1/S2 (R1-21) (R1-21, GRAINS-49) | ZM with ZS/ZL inputs | 5, 15, 30, 60 min; TB 15/30 | 796 OOF dates 2020-12..2024-02 | registered r009-E33 | net | crush residual and ZS/ZL propagation: no configuration passes; best loses 1.098 ticks a trade | reused | program |
| F09.E03 | de Boer et al. 2022 JFM (GRAINS-24) | soy complex | 30 s | 2015 | - | - | liquidity spillovers mainly within 30 s; negative at longer horizons | abstract | peer-reviewed |
| F09.E06 | Maier-Paape and Platen 2015 arXiv (EQUITY-13) | NQ, ES, Russell | 60-min chart extrema | 2004-09..2014-05 | in sample | none | NQ leads ES by about 9-12 min and Russell by 8-11 min; Russell leads ES by about 5 min | full_text | preprint |
| F09.E10 | Mechanical pairs (EQUITY-12, GRAINS-45, GRAINS-27, METALS-38, CRYPTO-32, FX-14) | micro/mini vs full | - | - | - | - | micros and minis settle from the full-size settlement or share the underlying: arbitrage-tight | full_text / reused | exchange documents |
| F10.E01 | Chordia, Roll, Subrahmanyam 2005 (via E.32 M1) () | NYSE stocks | 5-60 min forward | 1996 and later | in sample | - | forward R2 3.32% at 5 min, 0.53% at 30 min (1996); imbalance coefficient loses significance by 30 min | full_text (E.32 M1) | peer-reviewed |
| F10.E02 | Kolm, Turiel, Westray 2023 () | equities | about two price changes | n/a | - | - | deep order-flow forecasts effective for about two average price changes (about 12 s in ZM) | abstract | peer-reviewed |
| F10.E03 | Christensen, Oomen, Renò (via E.32 M1) () | ZC | after drift bursts | n/a, 97 events | in sample | - | post-drift-burst reversal b = -0.20, R2 41.5%; event time set at a local extremum of the test statistic (look-ahead to remove) | full_text (E.32 M1) | peer-reviewed |
| F10.E04 | Volkenand et al. 2018 (GRAINS-41) | corn, wheat, soybeans, cattle, hogs | unknown (full text 403) | March 2008, March 2016 | - | - | lagged order imbalance predicts returns for some contracts | abstract | paper |
| F10.E06 | Adams et al. draft 2026 (EQUITY-39) | ES | 10-60 min | 2018-2024 | in sample | gross | net gamma predicts stronger order-flow reversals | reused (full text) | working paper |
| F10.E07 | Program E.33c S3 (R1-21) (R1-21) | ZM order flow and book state (MBO) | 5-60 min | 2020-12..2024-02 | registered | net | no configuration passes; all G1 configurations lose over 1.0 tick a trade | reused | program |
| F10.E08 | Excluded sub-5-minute items (EQUITY-45, CRUDE-21, RATES-47, NATGAS-44) | NQ, CL, ZN, NG | <5 min / passive | - | - | - | excluded by the T6 rule (sub-5-minute or passive-fill) | abstract/reused | - |
| F11.E01 | Safari and Schmidhuber 2025 Physica A (CRUDE-40, RATES-42) | 16-24 futures incl. crude and the 10-year | minutes to hours | 2010-2023 | OOS | gross | reversion at 2-16 min, weak trend persistence at 1 h or more; OOS R2 0.55 bp and 0.020 bp | full_text | peer-reviewed |
| F11.E05 | Chinese commodities (CRUDE-44) | Chinese commodity futures | intraday | n/a | - | net | intraday momentum and reversal do not cover costs | abstract | paper |
| F11.E09 | Zarattini, Aziz, Barbon WP (noise-area momentum) (EQUITY-42) | SPY | intraday | 2007-2024 | in sample | net of commission | 6.2%/yr net, Sharpe 0.61; V45 item 3: dropped on post-publication evidence (no independent S&P test distinguishable from zero) | reused | practitioner WP |
| F11.E10 | Mesfin 2026; Taylor 2026 (EQUITY-43, EQUITY-44) | MNQ 5-min; NQ 15-min | 5-15 min | 2021-2025; 2022-2026 | walk-forward OOS; in sample | net of 2 MNQ points | none of 14 OHLCV families passes; AMD signal has no direction beyond the daily trend regime | reused / full_text | preprints |
| F12.E01 | Baltussen, Terstegge, Whelan (V45 exception) (R1-19) | ES (cousin; not a candidate) | 3rd-Friday | 2003-2021 | in sample | gross | -12.89 bp (t -2.40); 2015-23 not significant alone | reused (E.25) | working paper |
| F12.E02 | Barbon, Beckmeyer, Buraschi, Moerke (via E.20) () | US stocks/ETFs | end of day | n/a | in sample | gross | large negative (positive) gamma imbalance gives end-of-day momentum (reversal); leveraged-ETF effect economically larger; effects revert | full_text | working paper |
| F12.E03 | Adams et al. draft 2026 (EQUITY-39) | ES | 60 min | 2018-2024 | in sample | gross | momentum reverses in the high net-gamma quartile | reused | working paper |

Quotes (verbatim from the R2 file, with the saved source):

- F01.E01: "/ Equity / 4.97*** (6.06) / 1.67 / 4.83*** (6.02) / 2.42*** (3.82) / 8.89*** (4.11) / 2.73 / 3.98*** (6.65) / 2.34 /" (reports/stage_e13_briefs/pages/InfoSource/baltussen_etal_2021_jfe.md:1666-1669)
- F01.E02: "None" (F2_shared_baltussen.json)
- F01.E03: "None" (F2_shared_baltussen.json)
- F01.E04: "Note that we do not consider transaction costs." (F2_shared_baltussen.json SB-6)
- F01.E05: "None" (F2_equity.json)
- F01.E06: "None" (F2_equity.json)
- F01.E09: "None" (F2_grains.json / F2_metals.json)
- F01.E10: "None" (F2_equity.json)
- F01.E11: "None" (F2_equity.json)
- F01.E12: "None" (F2_equity.json)
- F01.E13: "None" (F2_rates.json)
- F01.E14: "None" (R1_closed_lines.json)
- F01.E15: "None" (R1_closed_lines.json)
- F01.E16: "CBOT SM first-half-hour -> last half-hour slope -0.95 (t -1.58), OOS R2 < 0 (Baltussen)" (reports/stage_e32_methods_brief.md:3225)
- F03.E01: "We do not find a significant market reaction within the first ten minutes after the report release time. However, we do find significant and directionally appropriate price reactions after 30 minutes." (F2_grains.json)
- F03.E02: "Notice that during small events the price initially moves in the opposite direction of the final price." (reports/stage_e32_methods_brief.md:2797, 2852-2876; reports/stage_e32_briefs/pages/R4_events/R4_ideals_usda_release_policy_2022.txt)
- F03.E03: "Return correlations provide little evidence to support systematic under- or overreaction in prices regardless of when the report is rel" (F2_grains.json)
- F03.E04: "None" (F2_grains.json)
- F03.E05: "None" (F2_grains.json)
- F03.E06: "None" (F2_grains.json)
- F03.E07: "None" (F2_grains.json)
- F03.E08: "None" (F2_grains.json)
- F03.E09: "None" (reports/stage_e32_methods_brief.md:3214-3250)
- F04.E01: "price discovery usually happens very quickly, with the majority of permanent price changes restricted to the minutes," (F2_rates.json)
- F04.E03: "a joint test of significance of price moves in the [t + 10min, t + 30min] window for all 30 announcements shows some evidence of continuing adjustment." (F2_equity.json)
- F04.E08: "None" (F2_equity.json)
- F05.E01: "In the three hours prior to each announcement, yield changes are not systematically different from zero. Following employment report releases, yield changes remain largely insignificant. FOMC announcements are followed by a significant and persistent decline" (F2_rates.json)
- F05.E02: "None" (F2_equity.json)
- F05.E06: "None" (F2_equity.json; F2_rates.json)
- F08.E03: "None" (F2_equity.json)
- F08.E07: "None" (F2_grains.json)
- F08.E08: "None" (F2_grains.json)
- F08.E09: "None" (reports/stage_e32_methods_brief.md:3224)
- F08.E13: "None" (F2_crude/natgas/grains.json)
- F09.E01: "A high level of cointegration is indeed observed during session 2 trading hours, which fades away during session 1." (F2_grains.json)
- F09.E02: "None" (R1_closed_lines.json)
- F09.E03: "None" (F2_grains.json)
- F09.E06: "None" (F2_equity.json)
- F09.E10: "None" (F2 files)
- F10.E01: "the forward part decays to statistical insignificance by 5 to 30 minutes in the best-documented case (Chordia, Roll and Subrahmanyam 2005, NYSE)" (reports/stage_e32_methods_brief.md:3638-3640)
- F10.E02: "None" (reports/stage_e32_methods_brief.md:3640-3641)
- F10.E03: "None" (reports/stage_e32_methods_brief.md:3643-3647)
- F10.E04: "None" (F2_grains.json)
- F10.E06: "None" (F2_equity.json)
- F10.E07: "None" (R1_closed_lines.json)
- F10.E08: "None" (F2 files)
- F11.E01: "weak trends tend to persist (b > 0), while strong trends tend to revert (c < 0)." (F2_crude.json)
- F11.E05: "None" (F2_crude.json)
- F11.E09: "None" (F2_equity.json; docs/DECISIONS.md:898-909)
- F11.E10: "None" (F2_equity.json)
- F12.E01: "None" (docs/DECISIONS.md:917-920)
- F12.E02: "We find that a large and negative (positive) aggregated gamma imbalance, relative to the average dollar volume, gives rise to an economically and statistically significant end-of-day momentum (reversal)." (reports/stage_e20_briefs/shared/barbon_beckmeyer_buraschi_moerke_letf.pdf.txt:31-34)
- F12.E03: "None" (F2_equity.json)

## R1 closed-line catalog

- **R1-01** [intraday_screen_confirm] MES intraday program (Stage D.1, D.1a, D.1b, D.1d, D.1e, D.1f): 58 Tier A tests in 7 classes C1-C7; families A calendar/clock windows, B opening-range and breakout, C reversal and fade, D vol-regime gates and gaps, E scheduled-macro and calendar, F data-native, G bucket/price-path statistics, H NR4/NR7/inside-day ORB and prior-close follow-through. Products: MES (traded). Horizons: from 5 minutes to the session close (A-H2 30 min; A-H1 about 60 min; B-H1 hold 5 and 75; D.1d sweep at 5/15/30/60-minute bars). Windows: screens D.1/D.1a/D.1b/D.1d/D.1e: research window 2025-04-01..2026-05-13 (289 train-union dates); D.1f confirmation 2020-02-03..2024-02-29 (S = 2020-02-03, 1,055 window days); Family H never read before D.1f; holdout-2 2024-04-01..2025-03-31 sealed (docs/STAGES.md:44-47). Trials: 58. Closing: V38/V40 (programme level); D.1f verdict in STAGES, "no member passed confirmation (Holm rejects none of 58); C1–C5 and C7 null under docs/NULL_CRITERIA.md (C5 null by inactivity via E-H3), C6 awaits D.1g; independently verified with no discrepancy; N = 58." (docs/STAGES.md:55). Exceptions: MES enters later only as a leg (STAGES:65: "MES is closed and enters only as a leg").
- **R1-03** [intraday_screen] K1 equity-index screen: CP1 open-to-first-half-hour momentum port, CP2 opening-range breakout, CP3 prior-day close-location, VXN band fade, VWAP stop-and-reverse. Products: MNQ (traded), M2K (traded), MYM (traded), NQ (price path/W_ext), RTY (price path/W_ext), YM (price path). Horizons: intraday holds, flat by the exchange-set F (15:08 CT equity/rates; see members); decision times in members. Windows: E.7 screen: research window 2025-04-01..2026-06-12, 299 trade dates; all eleven Tier B, Tier A empty; no confirmation run. Trials: 11. Closing: V40 (and V38), "Stage E's intraday clusters are closed (E.22 return item 3 accepted); no holdout read." (docs/DECISIONS.md:728-729).
- **R1-04** [intraday_screen] K2 rates screen: CP1/CP2/CP3 ports, pre/post Treasury-auction windows, post-FOMC, ISM pre-drift, month-end. Products: ZT (traded), ZF (traded), ZN (traded), TN (traded), ZB (traded), UB (traded). Horizons: intraday holds, flat by the exchange-set F (15:08 CT equity/rates; see members); decision times in members. Windows: E.3 screen: research window 2025-04-01..2026-06-17, 299 trade dates (15 roll-blackout, 2 UR-1 removed); all 44 Tier B; K2 confirmation never run (STAGES:260 still lists it "planned"). Trials: 44. Closing: V40 (and V38), "Stage E's intraday clusters are closed (E.22 return item 3 accepted); no holdout read." (docs/DECISIONS.md:728-729).
- **R1-07** [intraday_screen] K5 metals screen: CP1/CP2/CP3, LBMA AM/PM auction windows, FOMC, overreaction fade. Products: MGC (traded (GC bars)), MHG (traded (HG bars)), GC (price path). Horizons: intraday holds, flat by the exchange-set F (15:08 CT equity/rates; see members); decision times in members. Windows: E.4b screen: research 2025-04-01..2026-06-17, 295 trade dates; E.22 confirmation K5-fomc-01 MGC W_cf 2019-05-06..2024-02-29 (1174 days): null. Trials: 9. Closing: V40 (and V38), "Stage E's intraday clusters are closed (E.22 return item 3 accepted); no holdout read." (docs/DECISIONS.md:728-729).
- **R1-08** [intraday_screen] K6 grains/oilseeds/livestock screen: CP1/CP2/CP3, soybean crush gap, WASDE pre/post, livestock limit continuation. Products: ZC (traded), ZS (traded), ZL (traded), ZM (traded), ZW (traded), HE (traded), LE (traded). Horizons: intraday holds, flat by the exchange-set F (15:08 CT equity/rates; see members); decision times in members. Windows: E.8 screen: research window 2025-04-01..2026-06-19 (264-287 dates per trial); E.22 confirmation K6-limitcont-01 HE: null by inactivity (2019-05-06..2024-02-29). Trials: 27. Closing: V40 (and V38), "Stage E's intraday clusters are closed (E.22 return item 3 accepted); no holdout read." (docs/DECISIONS.md:728-729).
- **R1-10** [intraday_screen] K8 cross-market screen: equity-flight into gold (H30, HEOD), oil/CAD, weekend bitcoin to NQ. Products: MGC (traded), MES (signal leg), 6C (traded), MCL (signal leg), MNQ (traded), MBT (signal leg). Horizons: intraday holds, flat by the exchange-set F (15:08 CT equity/rates; see members); decision times in members. Windows: E.9 screen: research 2025-04-01..2026-06-16 (250-280 dates); E.22 confirmation: K8-flight-01 HEOD null (2020-02-04..2024-02-29, 944 dates); K8-wkndbtc-01 inconclusive by design (not run). Trials: 4. Closing: V40 (and V38), "Stage E's intraday clusters are closed (E.22 return item 3 accepted); no holdout read." (docs/DECISIONS.md:728-729).
- **R1-11** [ml_search] ML route v2 Gate 0: Family A (64 generic signals x 3 horizons = 192 tests) and Family B (27 products x 3 horizons = 81 product-horizon tests), ridge/LightGBM design, cost-gated. Products: 6A (tested), 6B (tested), 6C (tested), 6E (tested), 6J (tested), 6N (tested), 6S (tested), HE (tested), LE (tested), M2K (tested), MCL (tested), MGC (tested), MHG (tested), MNQ (tested), MYM (tested), NG (tested), TN (tested), UB (tested), ZB (tested), ZC (tested), ZF (tested), ZL (tested), ZM (tested), ZN (tested), ZS (tested), ZT (tested), ZW (tested). Horizons: h60, h120, hF (minutes; hF = to flat). Windows: training window 2019-05..2024-02 (S_X 2019-05-06; ZF 2020-10-01, ZT 2021-10-01); 1,067-1,068 dates; MBT no Gate 0 row; holdout-2 not read. Trials: 273. Closing: V24, "Under the frozen V2.2b, ML route v2 stops: no phase-2 purchase, no V2.6 model, no holdout-2 registration." (docs/DECISIONS.md:449-451). Exceptions: V24: "any reuse needs a new pre-registration that counts N = 471" (DECISIONS:453-454); V43 reopens ML for order-book/limit-order strategies only. [corrected s4: see errata] Cross-market content: includes G17: 60-minute log returns (x 1e4) of the other clusters' lead prices, g17_nq, g17_zn, g17_6e, g17_cl, g17_gc, g17_zc and (E.12 only) g17_mbt (ml_route_v2/signals/generic.py:22-25, 390-392; leads ml_route_v2/constants.py:36-37), never applied on the product's own cluster (generic.py:343, 351-352; c1_replication/c1b.py:53-54). g17_mes is defined but was excluded in E.12 by rule P-1a (MES store refused; reports/stage_e12_rulings.md:49), and MBT's E.12 store starts 2024-01-02 (reports/stage_e12_phase1_bars.json roots.MBT.s_x), so g17_mbt was live only 2024-01-02..2024-02-29. Tested pooled over the 27 products in Family A at h60, h120, hF (reports/stage_e12_gate0.md:158-164, 222-228, 286-292, rows gate0A_g17_*) and as inputs of Family B's ridge (all features, one model per horizon pooled across products, tested per product and horizon; ml_route_v2/gate0.py:11-12); decision times t1-t3 (equity 09:00, 11:00, 13:00 CT; grains 09:00, 10:00, 11:00; ml_route_v2/constants.py:50, 57). Live on M2K (cluster K1, own lead NQ excluded; constants.py:23): ZN, 6E, CL, GC, ZC (MBT from 2024-01-02). Live on ZL (cluster K6, own lead ZC excluded; constants.py:31): NQ, ZN, 6E, CL, GC (MBT from 2024-01-02); ZS and ZM are not G17 leads.
- **R1-13** [base_rule_batch] E.16 forced-flow base rules: H1 settlement-window intraday momentum (pooled), H2 month-end NQ vs ZN pair, H3 Treasury auction cycle, H4 next-day reversal of the settlement-window move, H5 equal-risk combination. Products: NQ (pooled (H1/H4)), YM (pooled (H1/H4)), RTY (pooled (H1/H4)), ZT (pooled (H1/H4)), ZF (pooled (H1/H4)), ZN (pooled (H1/H4)), TN (pooled (H1/H4)), ZB (pooled (H1/H4)), UB (pooled (H1/H4)), 6E (pooled (H1/H4)), 6A (pooled (H1/H4)), 6B (pooled (H1/H4)), 6C (pooled (H1/H4)), 6J (pooled (H1/H4)), 6S (pooled (H1/H4)), 6N (pooled (H1/H4)), CL (pooled (H1/H4)), NG (pooled (H1/H4)), GC (pooled (H1/H4)), HG (pooled (H1/H4)), ZC (pooled (H1/H4)), ZW (pooled (H1/H4)), ZS (pooled (H1/H4)), ZM (pooled (H1/H4)), ZL (pooled (H1/H4)), LE (pooled (H1/H4)), HE (pooled (H1/H4)). Horizons: H1/H4 settlement-window intraday; H2 and H3 hold overnight (multi-day, personal-account venue); H5 combination. Windows: 2010-07..2024-02 on the 17 W_ext roots; 2019-05-06..2024-02-29 on the 10 fallback roots (YM 6A 6B 6C 6J 6S 6N HG ZW ZM). Trials: 5. Closing: V31, "The base-rule batch H1 to H5 is closed: all five failed (H1's gross is about a quarter of its D8 cost; H2 positive at p 0.068, not a pass); no rerun or variant on these windows, no purchase of the 10 fallback roots, no holdout-2 read." (docs/DECISIONS.md:568-571). Exceptions: H2 (month-end NQ/ZN) noted as a personal-account candidate only, not pursued (V33 item 4, DECISIONS:608).
- **R1-14** [intraday_test] H6 rest-of-day to last-half-hour momentum on NQ (Baltussen, Da, Lammers, Martens 2021): T1 always, T2 above trailing |r_ROD| median, T3 negative prior-day GEX. Products: NQ (traded (MNQ cost)). Horizons: last half hour (about 30 min), entry at 14:30 CT. Windows: 2020-06-01..2024-02-29 (GEX rows 2020-05-29..2024-02-28), run once. Trials: 3. Closing: V38, "The intraday program on Topstep is closed: nothing in 528 trials passed" (docs/DECISIONS.md:678-679).
- **R1-15** [ml_search] E.20 Part C ML pattern search: ridge and shallow LightGBM, 45 configurations, extra decision time t4 = F_X - 60 min, r_ROD features. Products: NQ (searched), RTY (searched), ZT (searched), ZF (searched), ZN (searched), TN (searched), ZB (searched), UB (searched), 6E (searched), CL (searched), NG (searched), GC (searched), ZC (searched), ZS (searched), ZL (searched), LE (searched), HE (searched). Horizons: h60, h120, hF. Windows: 2019-05-06..2024-02-29 (nested CPCV, 57,775 decision rows); backward 2010-2019 read not run. Trials: 45. Closing: V38, "nothing in 528 trials passed, and no published post-2015 intraday effect on the 17 roots exceeds 1.5 x the D8 round trip (E.20 Part A, 157 evidence rows)" (docs/DECISIONS.md:679-681). Exceptions: V45 item 4 amends the sentence: three working-paper effects (see R1-19). [corrected s4: see errata] Cross-market content: includes G17: 60-minute log returns (x 1e4) of the other clusters' lead prices, g17_nq, g17_zn, g17_6e, g17_cl, g17_gc, g17_zc, six of the 36 frozen features (pattern_search/constants.py:59, 66; reports/stage_e20_search_freeze.json feature_names), computed by the frozen ml_route_v2 code (pattern_search/panel.py:64, 75; ml_route_v2/signals/generic.py:22-25, 343, 351-352), so never applied on the product's own cluster; g17_mbt and g17_mes dropped by the leg rule (reports/stage_e20_plan.md:138). One pooled model per horizon over the 17 vehicles (stage_e20_plan.md:28) at h60, h120, hF, 2019-05-06..2024-02-29 (pattern_search/constants.py:30-31); decision times t1-t3 (equity 09:00, 11:00, 13:00 CT; grains 09:00, 10:00, 11:00; ml_route_v2/constants.py:50, 57) and t4 = F_X - 60 min (14:08 CT equity, 12:18 CT grains; stage_e20_plan.md:81-82). Live on RTY (vehicle M2K, cluster K1): ZN, 6E, CL, GC, ZC (not NQ). Live on ZL (cluster K6): NQ, ZN, 6E, CL, GC (not ZC; ZS and ZM are not G17 leads).
- **R1-18** [multiday] E.23 program triggers at 5- and 20-day holds (entered at the trigger day's settlement; alpha over E.21 trend returns): K2-monthend-01 long ZF/ZN/ZB at 5 days; E20H6-T1 reversal on NQ at 5 and 20 days. Products: ZF (traded), ZN (traded), ZB (traded), NQ (traded). Horizons: 5 and 20 trading days. Windows: discovery W_ext 2011-07-27..2019-04-30, read once; confirmation W_cf 2019-05..2024-02 not computed (power 0.18). Trials: 5. Closing: V41, ""The program's intraday triggers at multi-day holds" is closed as a direction; no variant (other roots, other holds, the opposite H6 direction) is tested on these windows." (docs/DECISIONS.md:749-751). Exceptions: W_cf (2019-05..2024-02, trigger-conditional multi-day outcomes unread) and holdout-2 kept for a hypothesis with a stronger prior (DECISIONS:751-754).
- **R1-19** [intraday_closure_umbrella] Intraday program closure with its exceptions (E.20 Part A literature, 17 roots, 157 evidence rows; re-dug in E.25). Products: NQ (scope), RTY (scope), ZT (scope), ZF (scope), ZN (scope), TN (scope), ZB (scope), UB (scope), 6E (scope), CL (scope), NG (scope), GC (scope), ZC (scope), ZS (scope), ZL (scope), LE (scope), HE (scope). Horizons: intraday. Windows: n/a. Trials: 0. Closing: V38 as amended by V45 item 4, "no published post-2015 intraday effect on the 17 roots exceeds 1.5 x the D8 round trip, except three working-paper effects whose samples run past 2015, none with a significant post-2015 estimate" (docs/DECISIONS.md:910-916). Exceptions: V45: pre-refunding-announcement ZN gain (Wang and Zhao 2025, cash, +12.62 bp, t 3.32); V45: pre-FOMC ZN drift (Pan and Peng 2026, futures, +7.26 bp, t 2.82, 2004-01..2025-06); V45: ES 3rd-Friday reversal (Baltussen, Terstegge and Whelan, -12.89 bp, t -2.40, 2003-2021; 2015-23 not significant alone); V45: "Each gives 3 to 15 events in the research window (power 0.11 to 0.22 at the published sizes), so none can be tested with adequate power on owned data." (DECISIONS:919-921).
- **R1-20** [passive_execution_measured] Passive spread capture at the touch, one lot, trade-through fills (E.31 ZM order-book pilot); covers ZM, QM (frozen QM pilot never bought) and ZL follow-up (skipped). Products: ZM (measured), QM (closed by decision, not measured), ZL (closed by decision, skipped), ZS (conditioning data (MBP-1)). Horizons: 10 s markout per fill. Windows: 2020-12..2024-02 (39 whole months; 816 trade dates measured, 764 DAY dates usable); nothing on or after 2024-03-01. Trials: 0. Closing: V50, "Passive spread capture at the touch with a one-lot at prop-firm simulators is closed. This covers ZM, QM (E.28's frozen QM pilot is closed, never bought) and the ZL follow-up of V49 (skipped). E.29 D2 (baskets around ZM) is not run." (docs/DECISIONS.md:1034-1037). Exceptions: V50 item 2: "Limit orders stay allowed as an execution method for a directional signal. They are not a source of edge in themselves."; V56 item 2: limit orders as execution of a directional signal stay open; "Order-book direction is not closed for other products." (DECISIONS:1149-1152).
- **R1-21** [directional_search] ZM directional 5-60 minute search, five feature sets: S1 crush residual, S2 cross-asset propagation from ZS and ZL, S3 ZM order flow and book state, S4 ZM own price path, S5 all four pooled; x 6 labels x 10 model settings (6 regularised multinomial logits, 4 shallow LightGBM). Products: ZM (traded), ZS (input), ZL (input). Horizons: fixed horizons 5, 15, 30, 60 minutes; triple barrier at 15 and 30. Windows: 796 out-of-fold dates 2020-12-30..2024-02-29, 6 blocked folds, 21-date embargo; test window 2017-05-01..2020-11-30 sealed, unread. Trials: 300. Closing: V56, "ZM's directional route at 5-60 minute holds is closed. There is no E.34 and no purchase. The 2017-05..2020-11 window stays sealed for a future hypothesis family." (docs/DECISIONS.md:1146-1148). Exceptions: V56 item 2: order-book direction not closed for other products; limit orders as execution of a directional signal stay open.
- **R1-22** [product_decision] NQ dropped for the passive limit-order direction. Products: NQ (dropped). Horizons: n/a. Windows: none read. Trials: 0. Closing: V49 item 1, "NQ is dropped as a candidate at every firm (E.28 ranks 33, 45, 52, 54 and 62), despite Topstep's 0.44-tick break-even. Reasons: very long queues and HFT competition ... Topstep's Tier 1 news windows block NQ. NQ is not used as a pilot or comparison contract." (docs/DECISIONS.md:1010-1016).
- **R1-23** [closed_directions_no_trials] Directions closed by the user without a program trial: prediction markets; crypto; commodity event drift as a standalone stage; ML overlay on trend; C2 GEX late-session momentum stopped before freeze. Products: MBT (crypto direction (K7 screened, R1-09)), CRUDE_METALS_NATGAS (commodity event drift direction, no product list given). Horizons: n/a. Windows: none read. Trials: 0. Closing: V39 (and V27 for C2), "Closed as directions: prediction markets (user), crypto (every prior crypto line closed negative across the user's projects), commodity event drift as a standalone stage (planning research: geopolitical news is priced fast, OPEC drift has decayed; at most an overlay on trend)." (docs/DECISIONS.md:702-706). Exceptions: V39: small caps "marginal ... not run now" (DECISIONS:706-709): not closed; V27: C2 "stays stopped with no rerun planned" (DECISIONS:499-501).

## Not built

- EQ3 at bulenox: no F5 band for ['MNQ'] at bulenox (not top-15 pairs; LR-R2a/b)
- EQ3 at lucid: no F5 band for ['RTY'] at lucid (not top-15 pairs; LR-R2a/b)
- EQ3m at bulenox: no F5 band for ['MYM', 'MNQ'] at bulenox (not top-15 pairs; LR-R2a/b)
- EQ3m at topstep: no F5 band for ['MYM'] at topstep (not top-15 pairs; LR-R2a/b)
- EQ3m at tradeify: no F5 band for ['MYM'] at tradeify (not top-15 pairs; LR-R2a/b)
- EQ3m at lucid: no F5 band for ['MYM', 'RTY'] at lucid (not top-15 pairs; LR-R2a/b)
- YM + MYM: one underlying (MYM settles from YM): not a pool
- EQ3 or EQ3m at bulenox (YM, RTY) and lucid (YM, MNQ): a pool at a venue needs every member there with an F5 band; bulenox|MNQ, lucid|RTY (and every non-mffu MYM pair) are not top-15 pairs, so F5 has no band for them (LR-R2a, LR-R2b). Two-member sub-pools were not built (a pool is its member set).
- ZL with the equity codes: different asset class; the families ZL shares with them (F01, F08, F10, F11) are generic, and F01 is null on ZL (F01.E03)
- ZL with ZS and ZM (soy crush, F09): ZS and ZM are not top-15 codes (LR-R2a: pools only among the top-15 codes)
- F09 equity pool: F09 applies only to RTY among the equity codes (EQUITY-13, -14)

