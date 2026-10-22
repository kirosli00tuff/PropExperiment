# Stage E.28 A3: Part A fact table, masked sheets and scoring script (FactTable-OpusHigh)

Worker FactTable-OpusHigh (Opus 5.5, high), 2026-10-21 10:15-10:36 PDT. Facts only. Qualitative criteria (C1, C6,
R, A, F, Rel) are not rated here; the blind scorer rates them from the masked sheets. The spec
(reports/stage_e28_ranking_spec.md, sha256 89347e972ee14f637f0504035750ed952dc999e4787d92394ff7decd5a499a5f, checked
at every score.py run) is applied literally. No reader file was edited. No market data was read: all magnitudes come
from A0's JSON.

## Outputs

| File | Content |
|---|---|
| A3_facts.json | 47 Layer 1 candidates; each spec input as {value, unit, provenance, u, flags, note, quote, window}; variants block (OC1_off, C4_jump_transfer, OC2_published) |
| A3_firm_products.json | 5 firms x 47 codes = 235 pairs (listed yes/no/unknown, fee USD and ticks, 50K position limit, product cap, restriction text); per-firm facts for D, R, A, F, P, Rel, BC gate |
| A3_masked_contracts.json | labels C01..C47: evidence for C1(a), C1(b), C6 only; study relation normalized to SAME/SIBLING/COUSIN/CLASS/UNSTATED/NONE; rating schema |
| A3_masked_firms.json | labels F01..F05: evidence for R (by product class), A, F, Rel; platforms as P01..P21; rating schema |
| A3_mask_key.json | label key (seed 28); for the lead only |
| work/A3_facts/score.py | all criterion scores, gates, L1, L2, S, ranks with the tie rule; six variants; writes A3_ranking_table.json/.md |
| work/A3_facts/test_score.py | 101 unit tests (every anchor at its boundaries, tie rule, readers, pipeline smoke, hash refusal): 101 passed |
| A3_ranking_table.json/.md | written by score.py; currently INCOMPLETE (A3_blind_ratings.json and A3_econ.json not yet on disk, so nothing ranked) |

Rebuild order: `python3 A3_build_facts.py; python3 A3_build_firms.py; python3 A3_build_masked.py; python3 score.py`
(all in work/A3_facts/). Helpers: A3_common.py (constants, masker), A3_research_items.py, A3_dump.py,
A3_dumpfirm.py, A3_leakcheck.py.

## 1. Method and the source of each field

| Field | Owned root (A0 window bars 2022-11-01..2023-10-31) | No owned window bars |
|---|---|---|
| tick size, tick value | A1 `tick_size`, `tick_value`; cross-checked against A0 (`rules/products.py`), unit-aware for cents-quoted grains: 0 conflicts | A1 |
| sigma_1m (ticks) | A0 `sigma_1m_ticks` | OC-1: sibling's A0 value x tick(sibling)/tick(candidate), A1 ticks on both sides, price units checked equal; else unknown |
| R_d (ticks) | A0 `R_d_median_ticks` | OC-1 as above; else unknown |
| QV (minutes) | published best-level displayed size (A1) / A0 `vol_per_min_main_median`, where a size figure exists (CL, GC, ZN, ZF, ZB, ZC, ZS, ZW) | not formable (no owned volume) |
| proxy r | 1 / sigma_1m, used where QV is not formed | 1 / sigma_1m (OC-1 sigma) or unknown |
| ADV | OC-2: A0 `ADV_median_contracts_v0_front`; A1's published all-expiry figures reported beside it (`ADV_published_all_expiry`) | OC-2: A1 published all-expiry ADV, latest available (table in section 4) |
| spread main / overnight / ratio | A1 spread fields; ratio only where both sessions are sourced (ZS only: 1.09) | same |
| C4 releases, weekend gap | A1 family facts, encoded true/false with the basis (section 3) | same |
| C4 limit hits | A1 `limit_hit_days_*`: no product has a sourced 2019-2024 count, so every product is "unknown, holds" | same |
| C4 big moves (>= 10/yr at 4 SD) | A0 `c4_rate_per_252d_2019_to_2023_10_31` (max 1.43/yr, ZT): false | A1 value where a reader sourced one (M6E, M6A from 6E, 6A); else unknown, holds |
| 60-date gate | A1 gate field (inferred from listing, not counted) and A0 pilot-window file names (4 monthly files, not opened) | A1 gate field |
| firm listing, fees | A2 `products.<code>` (allowed; fee field per firm) | |
| MLL, DLL, position limit, BC | A2 plan and eligibility fields (paths in A3_firm_products.json) | |
| P items | A2 firm automation/VPS fields and A2_platforms API records (section 5) | |

## 2. Lead decisions applied (OC-1, OC-2)

- OC-1 derived codes (factor = tick(sibling)/tick(candidate)): MNQ from NQ (x1), M2K from RTY (x1), MYM from YM (x1),
  MNG from NG (x1), QG from NG (x0.2), QM from CL (x0.4), M6E from 6E (x0.5), M6A from 6A (x0.5), BTC from MBT (x1),
  XC/XK/XW from ZC/ZS/ZW (x2), MZC/MZS/MZW from ZC/ZS/ZW (x0.5), MZL from ZL (x0.5), MZM from ZM (x0.5). A1 price
  units match in every pair (US cents per bushel, US cents per pound, USD per short ton). SIL, SI, MET, ETH and
  the four micro yields stay unknown: no A1 reader sourced a sigma_1m or R_d. Volume statistics never transfer.
- OC-2: owned roots use A0's v_0 front-contract median. Where A1 has a clean published all-expiry figure the gap is
  large for products whose volume spreads over many expiries: NG 85,334 (A0) vs 400,923 (CME, 2023-01..08); ZC
  91,946 vs 361,462; ZS 77,862 vs 243,723; ZW 39,362 vs 128,465; ZL 42,686 vs 147,995; ZM 36,690 vs 140,498; ZT
  472,003 vs 797,491; RTY 181,060 vs 217,387; 6E 176,291 vs 223,555. Five of these cross a C3 boundary (NG, ZC, ZS,
  RTY, 6E: 3 -> 4; ZW, ZL, ZM: 2 -> 3). The informational variant OC2_published shows the effect on the ranking.

## 3. Reading choices the spec leaves open (open choices for the lead; each has a flag and, where cheap, a variant)

- OC-A3-1 (60-date gate unknown): MNG (launched 2023-11-06; 79 trade dates to 2024-02-29 by the reader's calendar,
  activity on each not verified), 5YY (published ADV 0 in Nov 2023, OI 0 in Feb-Mar 2024) and 30Y (ADV 48 in Nov
  2023) have no reader value. score.py treats an unknown gate as not shown (excluded), conservative. 5YY and 30Y fail
  anyway (C3 = 0). MNG is the only candidate this choice can decide. Every other gate value is "inferred from
  continuous listing", not a count of trade dates; the micro grains (listed 2025-02-24) fail.
- OC-A3-2 (D with unknown R_d): the spec names no default. score.py gives D = 0 and flags u (SIL, SI, MET, ETH, micro
  yields; under OC1_off also every OC-1 code).
- OC-A3-3 (E with unknown mu): when A3_econ.json has no row for a listed pair, or (OC1_off) sigma_1m is unknown,
  score.py gives E = 0 and flags u. The spec names no default.
- OC-A3-4 (QV from mixed windows): QV is formed from a published best-level size and A0's 2022-23 main-session median
  volume per minute, even though the size figures come from other windows and some are means: CL 7 / 241 = 0.029
  (median 2012-13, bid side); GC 4.62 / 116 = 0.040 (level-1 median, 2010); ZN 2,507 / 1,359 = 1.84, ZF 1,319 / 942 =
  1.40, ZB 377 / 323 = 1.17 (CME 2018 RTH averages, side not split); ZC 376.5 / 183 = 2.06, ZW 44.6 / 70 = 0.64 (2015-16
  means per side); ZS 51.5 / 143 = 0.36 (H1 2019 bid+ask 103 / 2, preferred over the 2015-16 per-side 62-64 as more
  recent). ZT is not formed: CME's 2018 depth predates the early-2019 tick halving (A1_rates.md F12, note on R8). The
  variant QV_proxy_only replaces every formed QV by the proxy r.
- OC-A3-5 (C4 readings): limit hits are unknown everywhere, so the item holds for all 47. For the equity family the
  reader sourced 4 RTH halt days (all March 2020), a lower bound of 0.67/yr; overnight limit hits in March 2020 are
  not verified, so the >= 1/yr average stays unknown and holds. Reader-flagged judgments read as false in the primary
  table and as holding in the variant C4_conservative: crude releases (EIA 1/week; API 1/week with weak measured
  impact; the reader left the count to the scorer), "none found" releases for metals, crypto and equity (metals and
  crypto readers coded 0, the equity reader null: read alike), rates releases (Treasury auctions 0.23/week per tenor),
  rates weekend gap (reader null; no source shows cash Treasuries trading while Globex is closed). Grains releases
  hold (USDA, 2 weekly in season plus WASDE). Crypto weekend gap holds (reference rate published every day; 24/7
  Globex only from 2026-05-29).
- OC-A3-6 (big-move counts of non-owned codes): only A0's own counts and A1 reader values are used (the FX reader gave
  M6E and M6A the 6E and 6A counts). MNQ, M2K, MYM, QM, MNG, QG, BTC, the mini and micro grains and the rest stay
  unknown (holds). OC-1 covers sigma_1m and R_d only. The variant C4_jump_transfer applies the same-underlying sibling
  counts to the OC-1 codes; it raises C4 by 1 for MNQ, M2K, MYM, QM, MNG, QG, BTC and the mini and micro grains.
- OC-A3-7 (ADV of non-owned codes): latest published figure within 12 months of the lookup date, multi-month where one
  exists (section 4). BTC has only an Oct 2023 single-month figure (13,000), so ADV is unknown (C3 = 1); M2K and MYM
  use the reader's derived 2022-11..2023-10 figure (no later product ADV found); MET uses calendar 2025 (secondary
  report citing CME); ETH uses April 2026 (single month); micro grains unknown.
- OC-A3-8 (P items): a firm that documents automation only through desktop platforms and names no API counts "no
  documented API" (Lucid, MFFU); Tradeify's Tradovate API is live-funded only (not evaluation or sim funded): counted.
  OCO on the API is judged on the back end (Rithmic, Tradovate, ProjectX all have it). Tradeify's conditional VPS ban
  ("where it obscures verification") is counted. Unpublished rate limits (Rithmic) count as unknown. Result: P =
  Topstep 2, Bulenox 2, Lucid 1, Tradeify 1, MFFU 1.
- OC-A3-9 (Topstep SI and HG): listed on the products page but capped at 0 contracts on the 50K plan (volatility
  caps, temporary, no end date): not listed for the 50K plan.
- OC-A3-10 (numerics): the L1 >= 2.00 test is made on L1 rounded to 10 decimals (float sums); the tie rule rounds S
  half-up to 2 decimals; a mu reported "> 4" or above 4 is treated as > 4 (score 0, sorts last on mu).
- OC-A3-11 (R by class): the masked firm sheets give R evidence per product class (equity_index, crude_oil,
  natural_gas, metals, fx, crypto, rates, grains) with the class's Globex hours and its class-specific scheduled
  events, so the scorer can apply the 25%-of-hours and weekly-event anchors. score.py takes R per class, an "all"
  fallback, or one integer; a class without a rating takes the spec's unknown default (1).

## 4. Conflicts between sources and their resolution

| # | Item | Sources | Resolution |
|---|---|---|---|
| 1 | Topstep SI, HG at 50K | products list: allowed; rules.volatility_caps_50k: SI 0, HG 0 | more specific (50K cap) wins: not listed |
| 2 | ADV of owned roots | A0 v_0 front median vs A1 CME all-expiry | OC-2: A0; both recorded; variant OC2_published |
| 3 | ZS best-level depth | 2015-16 per side 62.45/64.0 vs H1 2019 bid+ask 103 (day) | more recent: 103/2 = 51.5 per side (QV score 4 either way) |
| 4 | ZT best-level depth | CME 2018 average 99,471 vs the early-2019 tick halving | not used (pre-change tick); proxy r |
| 5 | Study relation for MNG, QG | natgas reader codes NG studies "same product" for all three | normalized: SAME for NG, SIBLING for MNG and QG |
| 6 | MCL, QM, MGC, SIL, MHG, micro grains studies | readers point to the full-size record ("see CL record", "see GC entry", "see ZC") | expanded from the sibling's record with relation SIBLING |
| 7 | Big-move counts for micros | FX reader transfers 6E/6A counts to M6E/M6A; equity reader leaves micros unknown | each reader's value kept (OC-A3-6); uniform transfer in variant C4_jump_transfer |
| 8 | "No product-specific releases" | metals, crypto readers 0; equity reader null | both read as false, flagged ambiguous (variant C4_conservative) |
| 9 | Weekend gap, rates | rates reader null; equity, FX readers false on similar unverified grounds | false, flagged ambiguous |
| 10 | Tradeify 10-second rule | rule page: funded only; news article: also gates evaluation activation | both shown in the masked A evidence; the scorer rates A |
| 11 | MFFU news rule | Builder page: unrestricted in evaluation and sim funded; general news page: 2-minute window | Builder-specific source shown first; both in the masked R evidence |
| 12 | MFFU evaluation minimum days | plan table 1 day vs plan page box 2 days | recorded (A2 note); EconCoder's domain |
| 13 | Lucid fees | per-side commission column; inclusion of exchange/NFA fees not stated | recorded as given; EconCoder's domain |
| 14 | Lucid 50K plan identity | first plan type in the pricing config (Wayback 2026-10-05; today's page 403) | recorded; EconCoder's domain |
| 15 | Lalor and Swishchuk citation year | crude reader 2026 (v3), equity reader 2024 | same arXiv 2409.12721v3; no effect |
| 16 | QG ADV | adv_latest Sep 2026 month 2,961 vs YTD Jan-Sep 2026 3,937 | longer window (YTD) used; both give C3 = 1 |
| 17 | SIL ADV | Q2 2026 74,000 vs 2025 annual 48,000 [unverified snippet] | verified quarter used (C3 3; the snippet would give 2) |
| 18 | Six pairs "listed but not tradeable now" | EconCoder's input table (work/A3_econ/A3_inputs.json, 132 pairs) keeps Topstep SI, HG (50K cap 0) and MFFU SI, HG, NG, QG ("currently restricted", temporary since 2026-02-07) with flags; A2 MFFU marks the four as not allowed | A3 treats all six as not listed for the 50K plan (126 pairs); score.py ranks only those; econ rows for the six are ignored. A lead call if the temporary restrictions should be read otherwise |

No tick-size or tick-value conflict between A0 and A1 once the cents quoting of ZC, ZS, ZW, ZL is allowed for.

## 5. Firm facts (A3_firm_products.json)

| Firm | 50K plan (A2) | MLL USD | DLL | Position limit 50K | BC | P items holding | Listed of 47 |
|---|---|---|---|---|---|---|---|
| Topstep | 50K Trading Combine, Standard Path | 2,000 (EOD trailing) | optional 1,000 | 5 minis / 50 micros (Combine); XFA 2/3/5 by balance; volatility caps | yes | VPS prohibited; 3.3 req/s | 31 |
| Lucid | LucidPro 50K | 2,000 (EOD trailing) | 1,200 soft (optional) | 4 / 40 | yes | no documented API; VPS unknown; rate limits | 23 |
| Tradeify | Growth 50K | 2,000 (EOD trailing) | 1,250 soft | 4 / 40 | yes | API live-funded only; conditional VPS ban; rate limits | 24 |
| MFFU | Builder 50K | 2,000 (EOD trailing) | 1,000 soft | 4 / 40; metals micros 5; MBT as mini | yes | no documented API; VPS unknown; 1.4 req/s | 23 |
| Bulenox | Qualification 50K, Option 1 | 2,500 (intraday trailing) | none (Option 2: 1,100) | 7 / 70 (Option 1) | yes | VPS unknown; rate limit unknown | 25 |

Listed counts from A3_firm_products.json `pairs` (126 listed pairs in all; table 8b).

## 6. Masking (A3_masked_*.json, key in A3_mask_key.json)

- Labels: `random.Random(28)`; sorted candidate codes shuffled -> C01..C47; then sorted firm keys -> F01..F05; then
  sorted platform names -> P01..P21; then sorted other product codes -> X01.. .
- Replaced: product codes (candidates by label, other codes by X label, in firm sheets by "[class product]"), product
  names, underlying and asset words ([U]), exchanges, agencies and report names, firm names, platform names, plan
  names, payment services, URLs, file paths and snake_case reference names. Source file names are dropped from the
  masked sheets (provenance stays in A3_facts.json and the key).
- A3_leakcheck.py found no candidate code and no firm or platform name left; remaining word hits are false positives
  ("window", "announcements", "Nguyen", "Bondarenko", a journal title "European J. Finance").
- Residual risks: numbers (ADV, depth, trade sizes) and some study titles still hint at an asset class; sibling labels
  inside the text reveal which labels share an underlying; the firm sheets name product classes (needed for R),
  founding years and a court case number. The scorer is told not to search.

## 7. Not finished

- A3_ranking_table.json/.md are INCOMPLETE until A3_blind_ratings.json (BlindScorer) and A3_econ.json (EconCoder)
  exist; rerun `python3 score.py` then. score.py reads the econ rows by firm and code (fields mu_star_lim, mu_star_mkt,
  mu10K, cost_per_attempt_usd; "> 4" accepted) and the blind ratings by label through the key, in the schema printed
  in both masked files; it stops with an error message only for a hash mismatch or a missing fact file.

## 8. Generated tables

### 8a. Layer 1 facts per candidate (primary; "u" = unknown default)

| Code | Tick | Tick USD | sigma_1m | R_d | QV or r | ADV | ADV source | Gate 60 | C4 rel / wknd / limit / 4SD | Flags |
|---|---|---|---|---|---|---|---|---|---|---|
| MCL | 0.01 | 1 | 6.49 | 245 | r 0.154 | 79,142 | A0 v_0 | True | F* / F / u / F |  |
| QM | 0.025 | 12.5 | 2.52 | 97.6 | r 0.397 | - | u | True | F* / F / u / u | OC1_derived |
| CL | 0.01 | 10 | 6.3 | 244 | QV 0.029 | 227,772 | A0 v_0 | True | F* / F / u / F |  |
| MNG | 0.001 | 1 | 6.28 | 158 | r 0.159 | 13,781 | A1 2025-01..2025-10 (YTD) | unknown | F / F / u / u | OC1_derived |
| QG | 0.005 | 12.5 | 1.26 | 31.6 | r 0.796 | 3,937 | A1 2026-01..2026-09 (YTD) | True | F / F / u / u | OC1_derived |
| NG | 0.001 | 10 | 6.28 | 158 | r 0.159 | 85,334 | A0 v_0 | True | F / F / u / F |  |
| MGC | 0.1 | 1 | 5.4 | 220 | r 0.185 | 52,744 | A0 v_0 | True | F* / F / u / F |  |
| GC | 0.1 | 10 | 5.29 | 220 | QV 0.0398 | 160,118 | A0 v_0 | True | F* / F / u / F |  |
| SIL | 0.005 | 5 | - | - | - | 74,000 | A1 Q2 2026 (quarter) | True | F* / F / u / u |  |
| SI | 0.005 | 25 | - | - | - | 64,000 | A1 Q2 2026 (quarter) | True | F* / F / u / u |  |
| MHG | 0.0005 | 1.25 | 3.38 | 159 | r 0.296 | 4,373 | A0 v_0 | True | F* / F / u / F |  |
| HG | 0.0005 | 12.5 | 3.14 | 159 | r 0.318 | 59,578 | A0 v_0 | True | F* / F / u / F |  |
| M6E | 0.0001 | 1.25 | 1.78 | 76.5 | r 0.562 | 23,742 | A1 2026-01..2026-09 (YTD) | True | F / F / u / F | OC1_derived |
| 6E | 5e-05 | 6.25 | 3.56 | 153 | r 0.281 | 176,291 | A0 v_0 | True | F / F / u / F |  |
| M6A | 0.0001 | 1 | 1.55 | 69 | r 0.647 | 7,384 | A1 2026-01..2026-09 (YTD) | True | F / F / u / F | OC1_derived |
| 6A | 5e-05 | 5 | 3.09 | 138 | r 0.323 | 82,950 | A0 v_0 | True | F / F / u / F |  |
| MET | 0.5 | 0.05 | - | - | - | 144,000 | A1 calendar 2025 | True | F* / T / u / u |  |
| ETH | 0.5 | 25 | - | - | - | 19,000 | A1 2026-04 (single month) | True | F* / T / u / u |  |
| MBT | 5 | 0.5 | 4.92 | 169 | r 0.203 | 6,678 | A0 v_0 | True | F* / T / u / F |  |
| BTC | 5 | 25 | 4.92 | 169 | r 0.203 | - | u | True | F* / T / u / u | OC1_derived |
| M2K | 0.1 | 0.5 | 10 | 341 | r 0.0999 | 79,724 | A1 2022-11..2023-10 (derived from CME monthly reports) | True | F* / F / u / u | OC1_derived |
| RTY | 0.1 | 5 | 10 | 341 | r 0.0999 | 181,060 | A0 v_0 | True | F* / F / u / F |  |
| MYM | 1 | 0.5 | 12.1 | 393 | r 0.0824 | 114,779 | A1 2022-11..2023-10 (derived from CME monthly reports) | True | F* / F / u / u | OC1_derived |
| YM | 1 | 5 | 12.1 | 393 | r 0.0824 | 163,416 | A0 v_0 | True | F* / F / u / F |  |
| MNQ | 0.25 | 0.5 | 27.8 | 967 | r 0.0359 | 1,600,000 | A1 calendar 2025 | True | F* / F / u / u | OC1_derived |
| NQ | 0.25 | 5 | 27.8 | 967 | r 0.0359 | 618,345 | A0 v_0 | True | F* / F / u / F |  |
| 2YY | 0.001 | 1 | - | - | - | 0 | A1 2026-01..2026-09 (YTD) | True | F* / F* / u / u |  |
| 5YY | 0.001 | 1 | - | - | - | 0 | A1 2026-01..2026-09 (YTD) | unknown | F* / F* / u / u |  |
| 10Y | 0.001 | 1 | - | - | - | 1,277 | A1 2026-01..2026-09 (YTD) | True | F* / F* / u / u |  |
| 30Y | 0.001 | 1 | - | - | - | 0 | A1 2026-01..2026-09 (YTD) | unknown | F* / F* / u / u |  |
| ZT | 0.00391 | 7.81 | 1.58 | 52.5 | r 0.633 | 472,003 | A0 v_0 | True | F* / F* / u / F |  |
| ZF | 0.00781 | 7.81 | 1.68 | 63 | QV 1.4 | 927,861 | A0 v_0 | True | F* / F* / u / F |  |
| ZN | 0.0156 | 15.6 | 1.28 | 46.5 | QV 1.84 | 1,385,806 | A0 v_0 | True | F* / F* / u / F |  |
| ZB | 0.0312 | 31.2 | 1.22 | 48 | QV 1.17 | 291,523 | A0 v_0 | True | F* / F* / u / F |  |
| MZC | 0.5 | 2.5 | 0.857 | 21.8 | r 1.17 | - | u | False | T / F / u / u | OC1_derived |
| MZS | 0.5 | 2.5 | 1.55 | 45.2 | r 0.644 | - | u | False | T / F / u / u | OC1_derived |
| MZW | 0.5 | 2.5 | 1.36 | 38.8 | r 0.734 | - | u | False | T / F / u / u | OC1_derived |
| MZL | 0.02 | 1.2 | 2.76 | 83 | r 0.363 | - | u | False | T / F / u / u | OC1_derived |
| MZM | 0.2 | 2 | 1.58 | 48 | r 0.634 | - | u | False | T / F / u / u | OC1_derived |
| XC | 0.125 | 1.25 | 3.43 | 87 | r 0.292 | 1,160 | A1 2026-01..2026-09 (YTD) | True | T / F / u / u | OC1_derived |
| XK | 0.125 | 1.25 | 6.21 | 181 | r 0.161 | 1,980 | A1 2026-01..2026-09 (YTD) | True | T / F / u / u | OC1_derived |
| XW | 0.125 | 1.25 | 5.45 | 155 | r 0.183 | 922 | A1 2026-01..2026-09 (YTD) | True | T / F / u / u | OC1_derived |
| ZC | 0.25 | 12.5 | 1.71 | 43.5 | QV 2.06 | 91,946 | A0 v_0 | True | T / F / u / F |  |
| ZS | 0.25 | 12.5 | 3.11 | 90.5 | QV 0.36 | 77,862 | A0 v_0 | True | T / F / u / F |  |
| ZW | 0.25 | 12.5 | 2.72 | 77.5 | QV 0.637 | 39,362 | A0 v_0 | True | T / F / u / F |  |
| ZL | 0.01 | 6 | 5.52 | 166 | r 0.181 | 42,686 | A0 v_0 | True | T / F / u / F |  |
| ZM | 0.1 | 10 | 3.15 | 96 | r 0.317 | 36,690 | A0 v_0 | True | T / F / u / F |  |

(* = reader-flagged judgment, counted as holding in the C4_conservative variant.)

### 8b. Listing and round-trip fees per firm (USD; ticks in brackets; "no" = not listed for 50K)

| Code | topstep | lucid | tradeify | mffu | bulenox |
|---|---|---|---|---|---|
| MCL | 1.72 (1.72); 50K volatility cap 30 contracts (Combine/XFA/Pro; temporary) | 1.00 (1.00) | 2.12 (2.12) | 1.16 (1.16) | 1.52 (1.52) |
| QM | 3.42 (0.27); 50K volatility cap 3 contracts (Combine/XFA/Pro; temporary) | 4.00 (0.32) | 5.40 (0.43) | 4.32 (0.35) | 3.92 (0.31) |
| CL | 4.02 (0.40); 50K volatility cap 3 contracts (Combine/XFA/Pro; temporary) | 4.00 (0.40) | 5.98 (0.60) | 4.92 (0.49) | 4.52 (0.45) |
| MNG | 1.92 (1.92) | no | no | no | no |
| QG | 2.02 (0.16) | 2.60 (0.21) | 4.00 (0.32) | no | 2.52 (0.20) |
| NG | 4.22 (0.42) | 4.00 (0.40) | 6.20 (0.62) | no | 4.52 (0.45) |
| MGC | 1.92 (1.92); 50K volatility cap 30 contracts (Combine/XFA/Pro; temporary) | 1.60 (1.60) | 2.12 (2.12) | 2.20 (2.20); 50K metals micros cap 5 contracts (since 2026-04-17) | 1.52 (1.52) |
| GC | 4.32 (0.43); 50K volatility cap 3 contracts (Combine/XFA/Pro; temporary) | 4.60 (0.46) | 6.20 (0.62) | 5.12 (0.51) | 4.62 (0.46) |
| SIL | 2.72 (0.54); 50K volatility cap 2 contracts (Combine/XFA/Pro; temporary) | 3.20 (0.64) | no | 2.84 (0.57); 50K metals micros cap 5 contracts (since 2026-04-17) | no |
| SI | no | 4.60 (0.18) | 6.20 (0.25) | no | 4.62 (0.18) |
| MHG | 1.92 (1.54); 50K volatility cap 2 contracts (Combine/XFA/Pro; temporary) | no | no | no | no |
| HG | no | 4.60 (0.37) | 6.20 (0.50) | no | 4.62 (0.37) |
| M6E | 1.00 (0.80) | no | 1.60 (1.28) | 1.44 (1.15) | 1.00 (0.80) |
| 6E | 4.22 (0.68) | 4.80 (0.77) | 6.20 (0.99) | 5.12 (0.82) | 4.72 (0.76) |
| M6A | 1.00 (1.00) | no | 1.60 (1.60) | 1.44 (1.44) | 1.00 (1.00) |
| 6A | 4.22 (0.84) | 4.80 (0.96) | 6.20 (1.24) | 5.04 (1.01) | 4.72 (0.94) |
| MET | 0.72 (14.40) | no | no | 1.16 (23.20) | 0.92 (18.40) |
| ETH | no | no | no | no | no |
| MBT | 2.82 (5.64) | no | no | 3.50 (7.00); MBT counted as a mini contract | 5.52 (11.04) |
| BTC | no | no | no | no | no |
| M2K | 1.22 (2.44) | 1.00 (2.00) | 1.82 (3.64) | 1.90 (3.80) | 1.22 (2.44) |
| RTY | 3.78 (0.76) | 3.50 (0.70) | 5.76 (1.15) | 4.68 (0.94) | 4.18 (0.84) |
| MYM | 1.22 (2.44) | 1.00 (2.00) | 1.82 (3.64) | 1.90 (3.80) | 1.22 (2.44) |
| YM | 3.78 (0.76) | 3.50 (0.70) | 5.76 (1.15) | 5.76 (1.15) | 4.18 (0.84) |
| MNQ | 1.22 (2.44) | 1.00 (2.00) | 1.82 (3.64) | 1.90 (3.80) | 1.22 (2.44) |
| NQ | 3.78 (0.76) | 3.50 (0.70) | 5.76 (1.15) | 4.68 (0.94) | 4.18 (0.84) |
| 2YY | no | no | no | no | no |
| 5YY | no | no | no | no | no |
| 10Y | no | no | no | no | no |
| 30Y | no | no | no | no | no |
| ZT | 2.32 (0.30) | no | no | no | no |
| ZF | 2.32 (0.30) | no | no | no | no |
| ZN | 2.62 (0.17) | no | no | no | no |
| ZB | 2.76 (0.09) | no | no | no | no |
| MZC | no | no | no | no | no |
| MZS | no | no | no | no | no |
| MZW | no | no | no | no | no |
| MZL | no | no | no | no | no |
| MZM | no | no | no | no | no |
| XC | no | no | no | no | no |
| XK | no | no | no | no | no |
| XW | no | no | no | no | no |
| ZC | 5.28 (0.42) | 5.60 (0.45) | 7.20 (0.58) | 6.12 (0.49) | no |
| ZS | 5.28 (0.42) | 5.60 (0.45) | 15.20 (1.22) | 6.12 (0.49) | 5.72 (0.46) |
| ZW | 5.28 (0.42) | 5.60 (0.45) | 17.20 (1.38) | 6.12 (0.49) | 5.72 (0.46) |
| ZL | 5.28 (0.88) | 5.60 (0.93) | 7.20 (1.20) | 6.12 (1.02) | 5.72 (0.95) |
| ZM | 5.28 (0.53) | 5.60 (0.56) | 9.20 (0.92) | 6.12 (0.61) | 5.72 (0.57) |

Listed pairs per firm: topstep 31, lucid 23, tradeify 24, mffu 23, bulenox 25. Total 126.
