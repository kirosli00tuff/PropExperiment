# F2 data access (Stage E.32b, B4 DataAccess-SonnetHigh), with lead rulings LR-D1, LR-D2, FL-9 applied

Full facts, sources, per-code inputs: F2_data_access.json. Pages and log: pages/DATA/. Scripts: work/DATA/ (DATA_build.py, DATA_forlead.py, DATA_rulings.py).

Databento GLBX.MDP3: bars from 2010-06-06; MBO granularity from 2017-05-21. No numeric published $/GB for MBO retrievable (FL-5).
Sealed windows: holdout 1 (MES) 2026-06-01..2026-09-16; holdout 2 (MCL MGC MHG NG) 2024-03-01..2025-03-31; soy test (ZM ZS ZL) 2017-05-01..2020-11-30. unlocks_logged 0.

Primary r = 0.9195 (MES MBO / ES mbp-1, same 5 days); one sampled day x 21 = one month. Variant k_ZM uses r = 3.06 (LR-D1). Primary p follows the spec text (pre-2024-03 seals only); p_brief is the variant (LR-D2).

| code | MBO start | h | k USD/month | k | k_ZM USD | k_ZM | o | p | p_brief | D5 |
|---|---|---|---|---|---|---|---|---|---|---|
| MCL | 2021-07-12 | 2 | 2.49 | 0 | 8.29 | 0 | 0 | 1 | 0 | 1 |
| QM | 2017-05-21 | 0 | 0.49 | 0 | 1.63 | 0 | 0 | 1 | 0 | 3 |
| CL | 2017-05-21 | 0 | 3.43 | 0 | 11.43 | 1 | 0 | 1 | 0 | 3 |
| MNG | 2023-11-06 | 2 | 0.49 | 0 | 1.63 | 0 | 0 | 1 | 0 | 1 |
| QG | 2017-05-21 | 0 | 0.20 | 0 | 0.66 | 0 | 0 | 1 | 0 | 3 |
| NG | 2017-05-21 | 0 | 0.98 | 0 | 3.27 | 0 | 0 | 1 | 0 | 3 |
| MGC | 2017-05-21 | 0 | 8.86 | 0 | 29.48 | 1 | 0 | 1 | 0 | 3 |
| GC | 2017-05-21 | 0 | 3.96 | 0 | 13.18 | 1 | 0 | 1 | 0 | 3 |
| SIL | 2017-05-21 | 0 | 2.55 | 0 | 8.47 | 0 | 1 | 0 | 0 | 3 |
| SI | None | 1 | 2.23 | 0 | 7.42 | 0 | 1 | 0 | 0 | 2 |
| MHG | 2022-05-02 | 2 | 1.08 | 0 | 3.60 | 0 | 0 | 0 | 0 | 2 |
| HG | 2017-05-21 | 0 | 0.99 | 0 | 3.29 | 0 | 0 | 0 | 0 | 4 |
| M6E | 2017-05-21 | 0 | 0.99 | 0 | 3.29 | 0 | 0 | 1 | 1 | 3 |
| 6E | 2017-05-21 | 0 | 3.33 | 0 | 11.07 | 1 | 0 | 1 | 1 | 3 |
| M6A | 2017-05-21 | 0 | 0.41 | 0 | 1.37 | 0 | 0 | 0 | 0 | 4 |
| 6A | 2017-05-21 | 0 | 2.54 | 0 | 8.44 | 0 | 0 | 0 | 0 | 4 |
| MET | 2021-12-06 | 2 | 1.58 | 0 | 5.25 | 0 | 1 | 0 | 0 | 1 |
| ETH | 2021-02-08 | 2 |  | 1 |  | 1 | 1 | 0 | 0 | 0 |
| MBT | 2021-05-03 | 2 | 4.65 | 0 | 15.46 | 1 | 1 | 0 | 0 | 1 |
| BTC | 2017-12-18 | 1 |  | 1 |  | 1 | 1 | 0 | 0 | 1 |
| M2K | 2019-05-06 | 1 | 5.16 | 0 | 17.18 | 1 | 0 | 1 | 1 | 2 |
| RTY | 2017-07-10 | 1 | 7.19 | 0 | 23.94 | 1 | 0 | 1 | 1 | 2 |
| MYM | 2019-05-06 | 1 | 9.65 | 0 | 32.11 | 1 | 0 | 0 | 0 | 3 |
| YM | 2017-05-21 | 0 | 5.84 | 0 | 19.42 | 1 | 0 | 0 | 0 | 4 |
| MNQ | 2019-05-06 | 1 | 51.97 | 2 | 172.95 | 2 | 0 | 1 | 1 | 0 |
| NQ | 2017-05-21 | 0 | 22.88 | 1 | 76.14 | 2 | 0 | 1 | 1 | 2 |
| 2YY | 2021-08-16 | 2 |  | 1 |  | 1 | 1 | 1 | 1 | 0 |
| 5YY | 2021-08-16 | 2 |  | 1 |  | 1 | 1 | 1 | 1 | 0 |
| 10Y | 2021-08-16 | 2 |  | 1 |  | 1 | 1 | 1 | 1 | 0 |
| 30Y | 2021-08-16 | 2 |  | 1 |  | 1 | 1 | 1 | 1 | 0 |
| ZT | 2017-05-21 | 0 | 3.90 | 0 | 12.98 | 1 | 0 | 1 | 1 | 3 |
| ZF | 2017-05-21 | 0 | 4.14 | 0 | 13.79 | 1 | 0 | 1 | 1 | 3 |
| ZN | 2017-05-21 | 0 | 5.07 | 0 | 16.88 | 1 | 0 | 1 | 1 | 3 |
| ZB | 2017-05-21 | 0 | 2.32 | 0 | 7.72 | 0 | 0 | 1 | 1 | 3 |
| MZC | 2025-02-24 | 2 |  | 1 |  | 1 | 0 | 1 | 1 | 0 |
| MZS | 2025-02-24 | 2 |  | 1 |  | 1 | 0 | 0 | 0 | 1 |
| MZW | 2025-02-24 | 2 |  | 1 |  | 1 | 0 | 0 | 0 | 1 |
| MZL | 2025-02-24 | 2 |  | 1 |  | 1 | 0 | 0 | 0 | 1 |
| MZM | 2025-02-24 | 2 |  | 1 |  | 1 | 0 | 0 | 0 | 1 |
| XC | 2017-05-21 | 0 |  | 1 |  | 1 | 0 | 1 | 1 | 2 |
| XK | 2017-05-21 | 0 |  | 1 |  | 1 | 0 | 0 | 0 | 3 |
| XW | 2017-05-21 | 0 |  | 1 |  | 1 | 0 | 0 | 0 | 3 |
| ZC | 2017-05-21 | 0 | 0.36 | 0 | 1.21 | 0 | 0 | 1 | 1 | 3 |
| ZS | 2017-05-21 | 0 | 0.79 | 0 | 2.62 | 0 | 0 | 0 | 0 | 4 |
| ZW | 2017-05-21 | 0 | 0.37 | 0 | 1.23 | 0 | 0 | 0 | 0 | 4 |
| ZL | 2017-05-21 | 0 | 0.50 | 0 | 1.66 | 0 | 0 | 0 | 0 | 4 |
| ZM | 2017-05-21 | 0 | 1.67 | 0 | 1.67 | 0 | 0 | 0 | 0 | 4 |

## Lead rulings

- LR-D1: Primary r = 0.9195 (ES-proxy, same 5 days). Variant field per code k_ZM = k and band with r = 3.06 (ZM ratio); primary k fields unchanged. FL-1 accepted: one sampled day x 21 trading days = one month.
- LR-D2: Primary p_all_read follows the spec text: only seals of pre-2024-03 windows count; holdout 2 (2024-03-01..2025-03-31) does not by itself set p = 0. The brief-based value is kept as p_brief. Codes where they differ: MCL, QM, CL, MNG, QG, NG, MGC, GC
- FL-9 rule: A registration counts as a read only for the windows its search actually ran on. E22-F1 (r007) was registered but parked without running: not a read. This census never counted r007 (read windows come from r002-E16, r005-E20S, r006-E21, r009-E33 only; r008-E23 and r001/r003 listed but not used), so no p value changed on this ruling.
- p_changed_primary_vs_previous_file: ['MCL', 'QM', 'CL', 'MNG', 'QG', 'NG', 'MGC', 'GC']
- LR-D3: FL-9 further ruling: r003-C1b (evaluated once) is a read of NG's window 2010-07..2019-04 (traded leg); its feature legs NQ, ZN, 6E (and GC, ZC per R1-12) are listed in read_windows with role 'feature leg' and counts_for_p false. r001-C1 (stopped at guard C10 before any statistic) is not a read (its entry removed). r008-E23 discovery W_ext 2011-07-27..2019-04-30 is a read for traded legs ZF, ZN, ZB, NQ (NQ counts for the Nasdaq underlying, MNQ); its confirmation window 2019-05..2024-02 was not computed: not a read. Source: R1_closed_lines.json R1-12, R1-18. Effect on p: none, because E16 (r002) already covers NG, ZF, ZN, ZB and NQ over 2010-07..2024-02; p and p_brief unchanged.

## for_lead (original items, with status)

- FL-1 (k: sample days vs months) [ruled by lead (see lead_rulings)]: The ledger's mbp-1 and tbbo quotes for the universe roots other than ZM, ZS and ZL are 5 single trade-day ranges (one per month 2025-05, 2025-08, 2025-11, 2026-02, 2026-04), not months. The literal rule (sum of quote lines / months covered) gives USD per sampled day, about 1/21 of a month. I scaled one day to a month with 21 trading days (check: MES mean MBO day x 21 = 21.0 vs the MES MBO whole-month quote 2025-10-01..10-29 of 22.03; ZS and ZL whole-month mbp-1 quotes average 0.855 and day x 21 = 0.874 for ZS). Repeated quote lines (same range, same USD, quoted again in later sessions) were deduplicated. Bands change under other scalings only for MYM, MNQ and NQ (see each code's k_band_sensitivity).
- FL-2 (r cannot be computed as written) [ruled by lead (see lead_rulings)]: The ledger has no MES mbp-1 or tbbo quote (MES has mbo and mbp-10 only; mbp-1 and tbbo exist for ES). r = MES MBO / ES mbp-1 over the same 5 sample days = 0.9195 (proxy). Alternatives: MES MBO / MES mbp-10 = 0.6542 (different schema); month cross-check 0.9647. ZM comparison (not used, different months, two contracts): ZM MBO per month / ZM mbp-1 per month = 3.064; against ZS and ZL whole-month mbp-1 in the same 40 months: 1.954 and 3.076. If r were the ZM comparison ratio, k bands would change for 13 of 30 scaled codes: ['CL', 'MGC', 'GC', '6E', 'MBT', 'M2K', 'RTY', 'MYM', 'YM', 'NQ', 'ZT', 'ZF', 'ZN'].
- FL-3 (ZM ledger MBO covers two contracts) [accepted by lead]: ZM k (1.671 USD/month, ledger MBO) is the mean of 40 whole-month quotes for ZM.v.0,ZM.v.1 together (2020-11..2024-02); a front-only month is lower. Band 0 either way.
- FL-4 (k unknown (rule step 4)) [accepted by lead]: No ledger MBO, mbp-1 or tbbo quote for: ETH, BTC, 2YY, 5YY, 10Y, 30Y, MZC, MZS, MZW, MZL, MZM, XC, XK, XW (14 codes). k = unknown, band 1 under spec D5.
- FL-5 (published Databento price) [accepted by lead]: No numeric $/GB for GLBX.MDP3 MBO could be retrieved: the pricing page renders its rate table client-side (Scrapling-rendered copy saved), the FAQ gives only the basis ($/GB of uncompressed size). The "$0.50/GB" figure is a search snippet, [unverified], unused.
- FL-6 (h evidence for listing dates) [accepted by lead]: E.28 A1 has no listing date for GC, SI, HG, YM, 6E, 6A, ZT, ZF, ZN and the CBOT grains. For all but SI, evidence that the product traded by 2010-07 (vendor ohlcv-1m file names from 2010, or stage_e16_windows start_month 2010-07 with e12_quoted_usd > 0) puts the MBO start at 2017-05-21 (h = 0). SI has no such evidence (vendor files 2025-04 on; not in the 27 E.16 markets): h = 1 (unknown). XC, XK, XW are scored from E.28 listing 2003/2007 but whether Databento GLBX.MDP3 carries them was not verifiable without the API. Databento states MBO granularity only from 2017-05-21 for the whole dataset (no per-product MBO dates published).
- FL-7 (p: holdout-2 seal after 2024-03) [ruled by lead (see lead_rulings)]: Brief reading (no window of the underlying sealed for a future test) gives p = 0 for the WTI, gold, copper and natural-gas families because holdout 2 (2024-03-01..2025-03-31, MCL MGC MHG NG) is sealed. Spec D5 text ('every pre-2024-03 window ... and none is sealed') can be read as pre-2024-03 seals only, which gives p = 1 for them. Codes where the two readings differ: MCL, QM, CL, MNG, QG, NG, MGC, GC. Used: brief reading (field p); the spec reading is in p_spec_reading.
- FL-8 (p: vacuous 1 on short history) [accepted by lead]: p = 1 only because the underlying has under 36 months of history before 2024-03-01 (so no 36-month stretch exists), although no registered search read it: 2YY, 5YY, 10Y, 30Y (listed 2021-08-16, 30.5 months). Borderline other way: ETH and MET (ETH listed 2021-02-08, 36.7 months, unread) get p = 0; MBT and BTC (BTC listed 2017-12-18) p = 0.
- FL-9 (p: what counts as a read) [ruled by lead (see lead_rulings)]: Read windows come from E16 (r002, 27 markets: 17 long roots from their windows file start, 10 fallback roots YM HG 6S 6J 6A 6B 6N ZM ZW 6C from 2019-05-06 only), E21 and E20S (17 roots, subsets), E33 (ZM, ZS, ZL 2020-12..2024-02). E.21's multi-day TSMOM and E.16's settlement-window tests are counted as bar-based directional reads of the whole window; E.23 (confirmation window not computed) and E.22 (forward test after 2024-03) add nothing before 2024-03. C1/C1b used CL and MBT as feature legs of an NG test and are not counted as reads of CL or MBT. Fallback roots therefore leave 2010-06..2019-05 unread (106+ months): YM, HG, 6A, ZW get p = 0 for that reason; silver (SI, SIL) was never read: p = 0.
- FL-10 (o borderline) [accepted by lead]: MBT owned ohlcv-1m covers 35.0 months (1065 days from 2021-05-03) before 2024-03-01 (listing 2021-05-03), under 36; o = 1 for MBT/BTC (no sibling data). SI and SIL, MET, ETH, rates yields, MNQ siblings: see o_inputs. MNQ gets o = 0 through its sibling NQ.
- FL-11 (spent windows (reported, not scored)) [accepted by lead]: docs/DECISIONS.md:773-777: E22-F1 spends holdout 2 for MGC, MCL and MNG on daily prices (trend-type and multi-day hypotheses only). E.33 spent ZM MBO and ZS/ZL MBP-1 2020-12..2024-02 (discovery). The soy test window 2017-05-01..2020-11-30 stays sealed (E.33c_RETURN.md:32,344). holdout status unlocks_logged 0 at start and end.
