# Stage E.23 P1.1-P1.4: inventory, mechanism memo, shortlist and data-use map (lead, 2026-10-17 02:37 PDT)

Written by the lead before any outcome read. No trigger-hold book has been computed; no forward return of any trigger has
been read. Sources: reports/stage_e23_briefs/inventory/*.json and *.md (10 InventoryReader workers, 02:17-02:29 PDT),
reports/stage_e23_briefs/mech/M1..M11 (11 MechanismReader workers, 02:17-02:33 PDT; pages and fetch logs under
reports/stage_e23_briefs/mech_pages/), reports/stage_e23_briefs/inventory_compact.txt (lead's extract of the 13 long roots).

## P1.1 Inventory (summary; full rows in the inventory files)
208 frozen intraday trigger rows: K1 11, K2 44, K3 30, K4 12, K5 11, K6 27, K7 6, K8 4, H6 3 (E20H6-T1..T3), CDE 60
(the D.1-D.1f MES families and E16-H1, E16-H4). 34 items excluded by the readers with reasons: ML models (C1, C1b, every
K*-ml member), drafts never frozen (E.13 C1/C2 drafts, E.14 C2), H2 and H3 (already multi-day; H2 is E.21 T4), H5 and
the cluster books (combinations, not triggers), Stage C (no trading rule), non-directional D.1f statistics, members
never declared (K1-predrift, K3-mehedge 6E, K2 X-01..X-09).

Lead exclusions for data not owned on BOTH windows (P1.1), from the rows' inputs_needed:
- Every rule on a root with no W_ext store: MES (all D.1-D.1f rules), MYM/YM, 6A 6B 6C 6J 6S 6N, ZW, ZM, MHG, MBT (all K7);
  and every multi-leg rule whose signal leg has no W_ext store: K8-flight-01 H30/HEOD (MES leg), K8-oilcad-01 (6C traded),
  K8-wkndbtc-01 (MBT leg), K6-crushgap-01 (ZM leg).
- Rules whose own inputs do not exist for 2010-2019 in the repo: K1-vxnband-01 (VXN table 2019-04-30 on), K2-predrift-01
  (ISM Services dates), K6-wasdepre-01 and K6-wasdepost-01 (WASDE dates), K3-ldnrev/ldnmom/ecbfix 6E (fix clocks, E&W and
  TARGET holiday tables 2019 on), K5-pmfix-01 and K5-preauc-01 (LBMA auction tables 2019 on), K4-apipre-01 (federal
  Monday holidays, API dropped weeks), K4-eiamom-01 (NYSE_NOT_FULL), E20H6-T3 (GEX from 2011-05 only, and its terms ruling
  covers one registered test).
- Roots with W_ext stores too short to read (P2.3, see the power section of the prereg): TN (from 2016-01-11), RTY (from
  2017-07-10), HE (from 2017-07-01), LE (from 2014-12-15): every rule on them (incl. K6-limitcont-01 HE and LE).

## P1.2 Mechanism memo (per member; the full paragraphs with verbatim quotes are in the memo files)
| Member(s) | Memo | Strength | Direction (5 / 20 days) | Lead note |
|---|---|---|---|---|
| K6-limitcont-01 HE, LE | M1 | weak | flat after t+1 (the published continuation is at t+1, before the entry) | dropped: weak; roots too short |
| K5-fomc-01 MGC | M2 | weak | continuation by analogy; a source disagrees | dropped: weak |
| K2-fomcpost-01 rates (fixed BUY) | M2 | weak | same side, not significant; disagreement | dropped: weak |
| K2-predrift-01 ZN, ZB (ISM pre-release) | M2 | none: intraday-only | - | dropped: intraday-only; no data |
| K8-flight-01 H30, HEOD MGC | M3 | moderate | reversal (opposite side) at 20 days; flat at 5 | not readable: MES leg not owned on W_ext; W_cf alone is power-gated |
| K8-oilcad-01, K8-wkndbtc-01 | M3 | none (one-step / Monday only) | - | dropped |
| E20H6-T1 NQ (and T2) | M4 | moderate | reversal at 5 (BDLM2021 1-3 days, t -3.16; BvD2019 anti-MAC(5) Sharpe 0.63 after 1999); 20 days disputed | SHORTLISTED (T1) |
| CP1 port, every root | M4 | moderate on equity (reversal at 5); weak to moderate rates and index commodities; weak FX, livestock | as left | not shortlisted: on NQ the same mechanism as H6 (redundant); weaker elsewhere |
| E16-H1 settlement-window momentum (pooled) | M4 | moderate pooled (reversal at 5) | 20 days disputed | not shortlisted: on NQ the same mechanism as H6; pooled multi-root trial |
| CP2 opening-range breakout | M5 | none: intraday-only | - | dropped |
| CP3 prior-close location | M5 | weak, reversal, one day | - | dropped |
| K1-vwap-01 | M5 | none: intraday-only | - | dropped |
| K2-aucpre-01, K2-aucpost-01 | M6 | moderate on ZT, ZF (FNR2024, fading after 2010/2014); weak ZN, TN, ZB, UB | long after the auction at 5 days; 20 days none | dropped: their 5-day post-auction long from the auction day's settlement IS the long leg of E16-H3, already read on 2010-07..2024-02 (E.17 FAIL); the two members are one bet (M6) |
| K2-monthend-01 rates | M7 | strong at 5 days for the N-1 trigger (Hartley-Schwarz 2019 Table 8, futures: 5y +7 bp, 10y +9 bp, 30y +15 bp on day N, se 1-2); N trigger weak/disputed | same side (long) at 5; 20 days only the unconditional premium | SHORTLISTED on ZF, ZN, ZB at 5 days |
| K3-mehedge-01 6J | M7 | none: intraday-only | - | dropped (no W_ext data either) |
| K3 fix members, K5-pmfix, K5-preauc | M8 | none: intraday-only (ldnrev weak, disputed) | - | dropped |
| K4-eiafade, K4-apipre | M9 | none: intraday-only | - | dropped |
| K4-eiamom-01 | M9 | weak, disputed | - | dropped |
| K4-ngpre-01 NG | M9 | moderate as a report-day calendar premium only (Prokopczuk et al., t -2.19, absent 2014-2018) | same side (short) | dropped: weekly events with 5- or 20-day holds keep the book short on almost every day: a buy-and-hold short, not a trigger test |
| K6-wasdepre, K6-wasdepost | M10 | weak | short continuation or null | dropped (no W_ext WASDE table either) |
| K6-crushgap-01 | M10 | weak (single leg) | - | dropped (ZM not owned on W_ext) |
| K4-ovr-01, K5-ovr-01 | M11 | weak, disputed | - | dropped |
| E16-H4 next-day reversal | M11 | moderate (reversal, the member's side; evidence to 3 days) | - | not shortlisted: on NQ the same bet as H6 one day later |
| K1-vxnband-01 | M11 | moderate (reversal at 5) | - | not readable: VXN not owned for 2010-2019 |
| K7 (MBT), D.1-D.1f MES rules | - | not researched | - | excluded for data (no W_ext store) |

## P1.3 Shortlist (4 triggers, 5 trigger-holds; at most 12 and 24 allowed)
Rule applied: a trigger is shortlisted if its stated multi-day mechanism is moderate or strong, its data exist on both
windows, its multi-day outcome has not been read before, it is not a duplicate of a shortlisted trigger's mechanism on
the same root, and its book is a trigger test: a FIXED-side book that would be in the market on almost every day is
the root's buy-and-hold, not a trigger test (amended 03:10 PDT from the power table's calendar facts: the H6 books are in
the market on 91-94% of days, but their side follows the trigger, so they remain trigger tests).

| Id (registry) | Trigger (frozen) | Root (price path, vehicle) | m | Hold | Mechanism (memo) | Expected events per year |
|---|---|---|---|---|---|---|
| E23-MEZF-h5 | K2-monthend-01 ZF | ZF (ZF) | +1 (same side: long) | 5 | month-end Treasury index-extension demand (M7: HS19 Table 8, ERSV20) | 24 (N-1 and N), 12 non-overlapping |
| E23-MEZN-h5 | K2-monthend-01 ZN | ZN (ZN) | +1 | 5 | same | same |
| E23-MEZB-h5 | K2-monthend-01 ZB | ZB (ZB) | +1 | 5 | same | same |
| E23-H6NQ-h5 | E20H6-T1 | NQ (NQ bars, MNQ costs) | -1 (reversal of sign(r_ROD)) | 5 | hedging price pressure reverses; post-2000 index anti-autocorrelation (M4: BDLM2021 Table 11, BvD2019) | about 240 |
| E23-H6NQ-h20 | E20H6-T1 | NQ | -1 | 20 | same; 20-day evidence disputed (M4) | about 240 |

Lead choices on the shortlist (Open choices in the return): K2-monthend-01's 20-day hold is not registered: with N-1 and N
every month and a 20-trading-day hold the book is long on nearly every day (a buy-and-hold long, not a trigger test);
"two holds each" is read as the default, not an obligation to register a degenerate book. Roots for K2-monthend-01: one per
published futures tenor (HS19 Table 8: 5y ZF, 10y ZN, 30y ZB); ZT has only a cash 2y figure (+3 bp) and TN/UB have no
row (TN is also too short on W_ext). H6: T1 only (T2 is a magnitude-filtered variant of the same rule; T3 is excluded).

Cost feasibility (V31): published gross per event against the D8 round trip of the vehicle (round trips: reports and
base_rules.costs; approximate bp at typical prices): month-end day N +7 / +9 / +15 bp (ZF / ZN / ZB) against about 1 / 2
/ 3 bp; H6 reversal about 6 bp over 2 to 3 days per a 20 bp last half hour (M4, the reader's arithmetic) against MNQ's
about 0.4-0.7 bp. Each clears 1.5 x its cost. The exact round trips go in the prereg table from base_rules.costs.

## P1.4 Data-use map and declared windows
| Trigger | Selected on (screen, discovery) | Confirmed or tested on | Other reads | Discovery window | Confirmation window |
|---|---|---|---|---|---|
| K2-monthend-01 ZF, ZN, ZB | research window 2025-04-01..2026-06-17 (E.3 screen, FAIL, Tier B; E.4 replay) | none (K2's confirmation never ran) | its month-end feature in the ML runs E.12 Gate 0 and E.20 (2019-05..2024-02; ML, no rule read); E.21 T1/T2 read the roots' daily series 2010-07..2024-02; for ZN only, E16-H2 (E.17, 2010-07..2024-02) held ZN from the fifth-last to the last trading day's settlement, long or short by the NQ-vs-ZN month-to-date sign, so ZN's day-N return entered H2's pair P&L with a conditional sign (partial overlap: one day of the 5-day hold, signed differently; not the same book) | W_ext 2011-07-27..2019-04-30 | W_cf 2019-05-06..2024-02-29 (ZF S_X 2020-10-01 per E.12's D4 path table, if declared; else 2019-05-06): inconclusive by design (power below 0.2) |
| E20H6-T1 NQ | none (registered from the literature, V34) | E.20 once on 2020-06-01..2024-02-29 (FAIL); descriptive overlap 2019-05-06..2020-05-29 | E.20 search feature rod_ret on 2019-05..2024-02 (ML); E16-H1 (a related settlement-window rule incl. NQ) tested on 2010-07..2024-02; E.21 T1/T2/T3 read NQ's daily series 2010-07..2024-02 | W_ext 2011-07-27..2019-04-30 | W_cf 2019-05-06..2024-02-29: inconclusive by design |

Stated plainly (P1.4): E.21 read the daily series of 2010-07..2024-02 for the 17 roots, so the aggregate multi-day drift
of both windows is known. The alpha over the same root's E.21 T1 and T2 returns is the registered guard; alpha3 (adding
the root's own buy-and-hold return, descriptive) is reported beside it because the month-end book is long-only.

Window reasoning (the full text is in the prereg): the ideal discovery window, the data each trigger was screened on, is
the research window, barred by P2.4. W_cf is at most 4.82 years and cannot reach the bar with power 0.2 in any role; W_ext
(7.76 years on these roots) can. Discovery is therefore W_ext and the declared confirmation window W_cf is inconclusive by
design, leaving every trigger's multi-day outcome on 2019-05..2024-02 unread for a later registered confirmation.
