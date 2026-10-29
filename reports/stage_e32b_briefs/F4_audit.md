# F4 audit (Stage E.32b C1v, FactAuditor-FableXHigh)

Independent check of the FactTable's outputs, written 2026-10-29 01:36-01:55 PDT. Read-only on every FactTable file.
Inputs as found: F4_facts_unmasked.json sha256 4a4d1e29... (F4_unmasked_READY.txt, 01:16:45 PDT); masked sheets and
key as in F4_masks_FINAL.txt (contracts a64a78eb..., firms e1ee7791..., key cbd8d3e2..., 01:35:01 PDT). Helper scripts
and their outputs: reports/stage_e32b_briefs/work/factaudit/ (leak_audit.py and leak_audit_out.txt, complete_audit.py,
unmask_synth.py and the synth_*.json files it wrote). Every F4 value below was re-derived from the F2, F3 and E.28 files
by script; quotes are verbatim from the source files named.

## Verdict

**FAIL on blinding for one firm; PASS on every value that feeds a score.** The 47 codes' ticks, multipliers, ADV,
spread/touch, settlement, siblings and data-access fields, the 5 firms' limits and P inputs, all 235 pairs' listing
flags and fees, the S_mean variant, the IBKR venue and the cross-family attachments match their sources (0 wrong
values). One BLOCKING item: the masked firm sheet names Lucid through its plan names (LucidBLACK, LucidDaily,
LucidMaxx) and leaves Flex/Pro/Direct unmasked in four items of V-PCDG. Two SHOULD FIX items concern how facts are
stated (HG's LR-S basis; the IIP item's text and relation), not the numbers. The masked sheets are FINAL by hash, so
every fix below is the lead's decision.

## BLOCKING

- **B1. Firm-name leak, F4_masked_firms.json, firm V-PCDG (= lucid), items I-7695386 (Rel_facts
  reliability.rule_changes_12m), I-1735555 (Rel_facts rel_rule_changes_12m), I-1219000 (R_facts_firm_wide
  restrictions.news_plan), I-0716183 (R_facts_firm_wide news_windows).** Masked text (verbatim from the sheet):
  `"LucidBLACK legacy, LucidDaily/LucidMaxx added, new Live structure 2026-10-14", "news: LucidDaily ban added
  2026-07..08"`; `"note": "LucidDaily: red folder news is a hard breach"`; `"quote": "News Trading Not allowed on Daily
  Trading red folder news on the LucidDaily is a hard breach Allowed on Flex, Pro and Direct Traders may enter or exit
  positions around scheduled or unscheduled news events"`. Counts: "Lucid" inside a word 7, "LucidDaily" 5, "Flex" 3,
  "Direct" 2, "Daily Trading" 1, "red folder" 2. The FactTable's leak check (387 patterns, 0 hits) used word boundaries,
  so a firm name glued to a plan name passed. A BlindScorer reading these knows which firm V-PCDG is (and from the fee
  pattern, the other four). Fix: replace Lucid* plan names with plan labels (P2, P3 ...), Flex/Pro/Direct with labels,
  re-hash the firms sheet and the key; or, if the lead keeps the FINAL set, record the exposure for the firm ratings
  (Rel and R of V-PCDG) in the stage entry. No code, firm, plan or platform name, URL, path, reader item id or E.28
  label was found anywhere else in either sheet (see Residual blinding below for what remains by ruling).

## SHOULD FIX

- **S1. HG spread_S: sourced true under "LR-S (ii)" rests on a window that is neither the main session, the US day
  session nor the whole day.** F4: `spread_S {value 1, sourced true, item METALS-50, clause "LR-S (ii)"}`; F4_facts.md
  line 76: "hourly AVERAGE spreads over ET 08:00-13:00 (US day hours), Q1 2023: 1.38-1.45 ticks, all < 1.5 (all-hours
  average 1.55 is above 1.5...)". Source (reports/stage_e32b_briefs/pages/METALS/cme_wp_asia_hours_cross_commodity_
  liquidity.html, Table 3, "Hour Starting (Singapore Time)", Copper column, re-extracted by me): 21:00 1.45, 22:00 1.44,
  23:00 1.44, 0:00 1.39, 1:00 1.38, **2:00 1.50, 3:00 1.56**, 4:00 1.49; "Asia hours Average ... 1.60"; "All hours
  Average ... 1.55". The reader's window SGT 21:00-02:00 = ET 08:00-13:00 (EST) is a sub-window chosen by the reader's
  parse script (work/METALS/METALS_parse_cme_wp.py). The spec's main session for HG is 06:30-13:00 PT = 09:30-16:00 ET
  = SGT 22:30-05:00 (EST; 21:30-04:00 after 2023-03-12 EDT), whose hourly means are 1.44, 1.44, 1.39, 1.38, 1.50, 1.56,
  1.49: NOT all below 1.5 (two hours at 1.50 and 1.56), so the "set of hourly means all below 1.5" leg of clause (ii)
  fails over the main session, and the whole-day mean 1.55 fails too. A time-weighted mean of those hourly means over
  09:30-16:00 ET is 1.46 (my arithmetic: (0.5x1.44+1.44+1.39+1.38+1.50+1.56+1.49)/6.5), which would pass the "mean"
  leg of (ii) only as a derived figure. Lead decision: accept the derived main-session mean (keep S = 1 sourced, restate
  the basis) or set HG to S = 1 (u), sourced false. Score effect: none in either case (S = 1 both ways; L's spread test
  is unaffected at 1 tick); the "u" marking and the F4_facts.md basis text change.
- **S2. The IIP item (RATES-11) is attached to 35 codes with applies_to "the product group" for every one of them,
  and its masked text never names 26 of those products or their groups.** Under the brief's definitions the fee table
  names nine codes by code (source reports/stage_e32b_briefs/pages/RATES/cftc_rules01102513618.pdf.txt: "Henry Hub
  Natural Gas Futures (NG)1 $0.90", "Light Sweet Crude Oil (WTI) Futures (CL)1 $0.90", "E-mini Crude Oil Futures (QM)
  $0.88", "E-mini Natural Gas Futures (QG) $0.45", "Core Metal (GC, SI, HG)1 $1.00", "E-micro Gold (MGC)1 $0.20",
  "1,000 oz. Silver (SIL) $0.40"), so "this contract" is the accurate word for CL QM QG NG GC SI HG MGC SIL; "the
  product group" fits the category rows (U.S. Treasury Futures, Micro Treasury Yield Futures, E-micro FX, Full Size FX,
  E-mini and Micro E-mini Equity Index, E-mini Dow/DJ U.S. Real Estate, Micro E-Mini Dow, Full Size and Mini
  Agricultural). The masked item carries the same Treasury quote under every label (for K-LRVK = CL: `"quote": "U.S.
  Treasury Futures $0.54 | Start date is December 16, 2011. End date is January 31, 2025 January 31, 2026, or the date
  on which | [size class] Treasury Yield Futures $0.21"`, detail "...The same fee table also lists [size class] FX,
  [size class] equity, K-DNXQ, agricultural, Henry Hub natural gas and other products"), so a BlindScorer rating D2b
  for CL, GC, M2K, 6E, ZC etc. cannot see from the sheet that the program covers that product (and sees MYM's label
  K-DNXQ inside every copy). Fix (lead): add the product's own fee-table line as the quote for each attached code, or
  rate the IIP question centrally; see FT-8 below for the program's nature.
- **S3. Contract size and tick facts survive inside masked s1 (mechanical pair) items, against the format field's
  statement "The sheet carries no ADV, contract size, multiplier, tick, fee, settlement method, sibling or leader
  facts".** F4_masked_contracts.json: `Members K-SGKW (100 bbl, 0.01 tick), K-PXYN (500 bbl, 0.025 tick = 2.5 K-LRVK
  ticks ...)` (6 "bbl" hits, 24 "... tick(s)" hits), `K-OTEO is EUR 12,500, K-ASSS EUR 125,000` (8 EUR/AUD notional
  hits), `Index Futures ($5 Multiplier)` (12 "multiplier" hits in quotes). With the asset word kept by ruling, "100 bbl"
  identifies MCL as surely as "Micro" would. Fix (lead): strip sizes and ticks from the s1 detail texts, or amend the
  format statement and accept, as the lead accepted the micro/full-size words.
- **S4. lucid|SIL fee under RR-05 (u) is 2.84, below Lucid's own published commission round trip of 3.20.** F4 pairs
  "lucid|SIL": `fee_rt_usd 2.84, fee_kind "RR-05 (u)", fee_basis "highest round trip for SIL at the other four firms:
  mffu 2.84 (all: {'topstep': 2.72, 'mffu': 2.84})"`. Source reports/stage_e28_briefs/A2_firm_lucid.json
  products.SIL.commission_per_side: value 1.6, quote "SIL / Micro Silver / 1.60 / COMEX", note "column 'Commission (Per
  Side)'; inclusion of exchange/NFA fees not stated"; round trip 3.20 before any exchange or NFA fee. RR-05
  (A3_lead_rulings_v2.json): "Lucid's table gives commission per side and never states whether exchange and NFA fees
  are included, so the all-in fee is unknown; the spec's rule applies: 'If a fee is unknown, the highest fee found for
  that product class at the other four firms is used and marked u.'" The FactTable applied the ruling as written; SIL
  is the only pair of 23 listed Lucid pairs where RR-05 falls below Lucid's commission alone (all others are above:
  MCL 2.12 vs 1.00, QM 5.40 vs 4.00, CL 5.98 vs 4.00, QG 4.00 vs 2.60, NG 6.20 vs 4.00, MGC 2.20 vs 1.60, GC/SI/HG 6.20
  vs 4.60, 6E/6A 6.20 vs 4.80, M2K/MYM/MNQ 1.90 vs 1.00, RTY/YM/NQ 5.76 vs 3.50, ZC/ZL 7.20 vs 5.60, ZS 15.20, ZW 17.20,
  ZM 9.20 vs 5.60). Score effect now: none (SIL has F3 status unknown and fails the Layer 1 gate). Lead decision:
  floor RR-05 at Lucid's commission plus the exchange and NFA fees, or leave as ruled.

## NOTE

- N1. GC touch 4.62 (sourced median, METALS-3: "4.62 contracts level-1 median (2010, 06:30-13:30)", Richards, Peters
  and Dunsmuir 2015 on 2010 data) and MNG touch 3 (NATGAS-6, E.2a program measurement, median) are the only touch
  values below 5, so they alone set D4 L = 1 for GC and MNG. Both follow LR-S ("Touch size counts only as a sourced
  median") and are correctly copied; the GC figure is 13 years older than the F3 window and the newer GC figures
  (METALS-51: averages 6.76 all hours, 6.82-8.36 in US hours) are means and so cannot replace it. For the lead's
  awareness; no change proposed by me.
- N2. P inputs: oco_api is true for all five firms in F4, while F2_firms.json records oco_api "unknown" for lucid,
  tradeify, mffu and bulenox. F4 carries E.28's ruling OC-A3-8 (reports/stage_e28_briefs/A3_facts.md line 95: "OCO on
  the API is judged on the back end (Rithmic, Tradovate, ProjectX all have it)"), and FirmRules found no change. P
  reproduces E.28's values (Topstep 2, Bulenox 2, Lucid 1, Tradeify 1, MFFU 1). An inherited judgment, not a sourced
  firm statement; consistent with spec 4 ("E.28's rubric unchanged").
- N3. Seven F2 items are attached to no code: SB-6 ("not net of costs; positive net Sharpe for S&P 500 futures at
  1 tick cost"), SB-7 ("effect reverts over the next days"), SB-11 (ES), SB-16 (UB), CFTC-52 (ES), CFTC-54 (all
  futures, 51), RATES-48 (excluded by the reader). SB-11/16, CFTC-52 are out of the universe; RATES-48 excluded by its
  reader. SB-6/SB-7 are caveats on a study whose class rows already say "(gross)" in their details, and CFTC-54 is a
  futures-wide figure where CFTC-53 (also futures_broad) was attached to every code: a small inconsistency, no fact
  lost that the class rows do not state.
- N4. applies_to imprecisions where the reader's scope was coarser than the item (from the 84 distinct (family, scope,
  applies_to) combinations I read; see FT-9): EQUITY-15 (quarterly calendar spreads, evidence about NQ) is "a
  same-underlying sibling" for M2K/MYM, whose sibling is RTY/YM; EQUITY-21 (pre-FOMC drift in SPX) is "this contract"
  for RTY and "a same-underlying sibling" for M2K, where "another venue"/"a close cousin" would be exact; RATES-39
  (Baltussen ZT row) is "a same-underlying sibling" for 2YY although F4 lists no siblings for the micro yields (spec 0:
  "10Y and ZN are NOT siblings for price transfer"). The micro yields fail the Layer 1 gate (sigma unknown), so no
  ranking effect; M2K/RTY D3 s1/s2 could be read one level too generously.
- N5. Residual identifiers inside the masked contract sheet that the lead's ruling does not name: CFTC filing numbers
  (53 hits, e.g. "CFTC self-certification NYMEX 24-499", "CME 22-047") and filing file ids (4 hits, "rules0812244266");
  program windows that coincide with listing dates (2021-07-12 MCL LPP, 2019-05-06 Micro E-mini MM program 15 hits,
  2021-05-03/2021-12-06 MBT/MET, 2023-11-06 MNG, 2025-02-24 micro grains 13 hits, 2021-08-16 micro yields 12 hits,
  2010-10-04 MGC); "[ref].txt" remnants (16 in contracts, 1 in firms); "Wayback copy" mentions (60 and 7). None names
  a code; the dates and filing ids would identify contracts only to someone who already knows the listing calendar
  (the size-class words the lead allowed identify them more directly). Exchange names (CME 794, CBOT 251, NYMEX 116,
  COMEX 83, Globex 330), underlying words (WTI 76, Henry Hub 61, Brent 48, Russell 2000 32, Nasdaq-100 16, Dow Jones
  23, EUR/USD 41, AUD/USD 28, soybean meal 34, Chicago SRW 26) and report names (EIA 92, USDA 86, WASDE 63) stay by
  ruling. IWM (Russell 2000 ETF, 4 hits) is an other-venue ticker, not a universe code. In the firm sheet the firm-
  specific rule numbers (16:45 ET 293 hits, 15:10 CT 194, 16:10 ET 145, 15:59 CT 97, "Tier 1" 62, "volatility cap"
  18, 52,100 4, $172 2, $125 1, 90/10 4) are the R and Rel facts themselves, as in E.28.
- N6. Topstep dll_50k "none" (E.28 firm model: dll None; F2: "optional, chosen at purchase (fixed) ... amount 1000")
  and Bulenox dll_50k "none" (Option 1, the modelled plan; Option 2 has 1,100 soft) follow the modelled plans and
  match E.28's firm models (econ firm check: "unverifiable, not a mismatch"). Bulenox "fees changed: true" in
  F2_firms.json is the professional data fee 116 -> 133 ("Traders with professional status pay a monthly fee of $133
  for the exchange data feed"), with "changes_vs_e28_for_47": []; per-contract fees unchanged, correctly left as E.28's.
- N7. GC spread basis is stated too narrowly but is right: the whole-day mean 1.39 and every main-session hourly mean
  (1.35, 1.35, 1.32, 1.31, 1.35, 1.40, 1.39 for SGT 22:00-04:00) are below 1.5, so LR-S (ii) holds over the main
  session and the whole day, not only over ET 08:00-13:00; METALS-1 ("one tick during almost all trading hours",
  2017-Q1 2018) supports (iii) as well. The Q1 2023 table is in fixed Singapore time; 2023-03-12 (EDT) shifts the ET
  mapping by one hour for the last 14 trading days of the quarter (no hour changes side of 1.5 for GC either way).
- N8. F4_smean.json HG touch_mean uses the all-hours average 5.35 (METALS-52) where the same table gives US-hours
  hourly averages 6.42-7.07; both are Q1 2023, so "nearest window" does not choose between them. 6A touch_mean 15 is
  the lower bound of the reader's "15 to 20". All other S_mean and touch_mean values match their items exactly.

## The lead's added checks

**FT-1 (o and p direction).** F2_data_access.json stores o and p as D5 scores: work/DATA/DATA_build.py line 512
`"owned": owned, "o_owned_36m": o, "o": o, "o_inputs": o_info,` and line 514 `"p_all_read": p, "p": p, "p_basis":
p_basis,`; F2_data_access.md table header "| code | MBO start | h | k USD/month | k | k_ZM USD | k_ZM | o | p | p_brief
| D5 |" with "| MCL | 2021-07-12 | 2 | 2.49 | 0 | 8.29 | 0 | 0 | 1 | 0 | 1 |" (D5 = 4 - 2 - 0 - 0 - 1 = 1, so o = 0
means owned and p = 1 means all read, as spec D5 defines them). F4 converts o_owned_36m = (F2 o == 0) and p_all_read =
(F2 p == 1). Checked for all 47 codes against F2 o, p, mbo_start and k_usd_month: 47 consistent, 0 wrong. Direction
spot-checks from F2 o_inputs: MBT o = 1 (own bars 35.0 months, BTC 0) -> F4 false; MCL o = 0 (own 33.0 months, sibling
CL 164.0) -> F4 true; 2YY o = 1 -> false; MZC o = 0 (ZC 164.8) -> true. SCHEMA.md 2 reads the booleans; the score
script's 47 soft "o_owned_36m" findings are the 0/1-vs-boolean format difference the FactTable documented.

**FT-4 (GC and HG spread).** Source: CME whitepaper "Leveraging CME Group Asia Trading Hours Liquidity for Cross
Commodity Trading" (saved page above), "Table 3. Average of best bid/ask spread (ticks)", "Hour Starting (Singapore
Time)", Q1 2023, most active contract month, all 24 hours. The figures are AVERAGES by hour, not medians (text: "Table
3 shows the average bid/ask spread by hour of the most active contract month in each market during the first quarter of
2023"). Gold column: 0:00 1.32, 1:00 1.31, 2:00 1.35, 3:00 1.40, 4:00 1.39, 5:00 1.41, 6:00 1.82, 7:00 1.55, 8:00 1.40,
9:00 1.40, 10:00 1.38, 11:00 1.37, 12:00 1.34, 13:00 1.36, 14:00 1.43, 15:00 1.36, 16:00 1.37, 17:00 1.36, 18:00 1.36,
19:00 1.33, 20:00 1.33, 21:00 1.35, 22:00 1.35, 23:00 1.35; Asia hours average 1.37; all hours average 1.39. Copper
column: 0:00 1.39, 1:00 1.38, 2:00 1.50, 3:00 1.56, 4:00 1.49, 5:00 1.48, 6:00 1.84, 7:00 1.58, 8:00 1.55, 9:00 1.62,
10:00 1.61, 11:00 1.60, 12:00 1.56, 13:00 1.60, 14:00 1.59, 15:00 1.59, 16:00 1.66, 17:00 1.62, 18:00 1.61, 19:00 1.56,
20:00 1.51, 21:00 1.45, 22:00 1.44, 23:00 1.44; Asia hours average 1.60; all hours average 1.55. The reader (METALS-49,
METALS-50) and the FactTable took SGT 21:00-02:00 = ET 08:00-13:00 (EST), calling it "US day hours": GC 1.35, 1.35,
1.35, 1.32, 1.31 and HG 1.45, 1.44, 1.44, 1.39, 1.38, all below 1.5 (verified). Over the spec's main session 09:30-16:00
ET (SGT 22:30-05:00 EST): GC 1.35, 1.35, 1.32, 1.31, 1.35, 1.40, 1.39, all below 1.5 (GC S = 1 under (ii) stands, also
via the whole-day mean 1.39); HG 1.44, 1.44, 1.39, 1.38, 1.50, 1.56, 1.49, NOT all below 1.5 (S1 above). Not Asia
hours: the Asia-hours averages (1.37 and 1.60) are separate rows the FactTable did not use.

**FT-8 (IIP, RATES-11).** Source reports/stage_e32b_briefs/pages/RATES/cftc_rules01102513618.pdf.txt (CME submission
25-042, "Modifications to the International Incentive Program"). The product table (lines 160-230) lists under "CBOT
Products" two consecutive rows: "E-mini Dow/DJ U.S. Real Estate $0.75" and "Micro E-Mini Dow Futures $0.18". The first
is a combined row for two CBOT equity-index products, the E-mini Dow ($5) futures (YM) and the Dow Jones U.S. Real
Estate Index futures (a separate product, not in the universe); reading it as covering YM is right, and MYM has its own
row. Program nature, verbatim: "The purpose of this Program is to incentivize proprietary trading firms located
outside North America to trade the products listed below. The resulting increase in liquidity in the products listed
below benefits all participant segments in the market." "Only proprietary trading firms located outside of North
America and traders located outside of North America are eligible." "For continued eligibility and incentive
qualification, IIP participants must maintain a combined average daily volume ("ADV") in the Products of 250 contracts
(sides) measured over a given calendar quarter. Micro E-mini Equity Index products will be excluded from this ADV
requirement." "1. Fee Discounts: Participants will be eligible to receive fee discounts for the Products in accordance
with the following tables". "2. CME Products Progressive Volume Discount Incentives: Subject to the restrictions set
forth in #3 below, participants in the Program that maintain a monthly an ADV of 5,000 combined contract sides traded in
the respective CME Products denoted above are eligible to receive progressive volume fee discounts in those Products".
Term: "Start date is December 16, 2011. End date is January 31, 2025 January 31, 2026, or the date on which the
Exchanges determine to modify, extend, or terminate the Program." No quoting, two-sided-market or time-in-market
obligation appears in the filing: it is a fee-discount program for a class of participants (non-North-American
proprietary firms and traders) with a volume floor, covering almost every CME, CBOT, NYMEX and COMEX outright future,
not a market-maker program. Whether that is a "volume-incentive program for the product's outright futures" in the
D2 b sense is the BlindScorer's rating; I note that the same answer would then apply to 35 of 47 codes at once.
Attachment check: the 35 codes the FactTable attached (10Y 2YY 30Y 5YY 6A 6E CL GC HG M2K M6A M6E MGC MNQ MYM NG NQ QG
QM RTY SI SIL XC XK XW YM ZB ZC ZF ZL ZM ZN ZS ZT ZW) match the fee table's rows (Agricultural full-size and mini, E-micro
FX, Full Size FX, E-mini and Micro E-mini Equity Index, E-mini Dow, Micro E-Mini Dow, Micro Treasury Yield, U.S.
Treasury, NG, CL, QM, QG, Core Metal GC SI HG, MGC, SIL); MCL, MNG, MHG, the crypto codes and the micro grains are not
in the table (correctly left off).

**RR-05 floor.** 23 listed Lucid pairs compared with A2_firm_lucid.json commission_round_trip (2 x per side): 1 pair
below, SIL (2.84 vs 3.20); 22 above. Detail in S4. The 24 unlisted Lucid pairs carry RR-05 values or null that enter
no score.

**FT-9 (relations).** F4_mask_key.json "relations": 1565 assignments over 47 codes; scope -> applies_to table:
product_group -> "the product group" 188; asset_class/futures_broad -> "the asset class broadly or a multi-asset study"
190; other_venue -> "another venue of the same underlying" 108; product -> "this contract" 292 / "a same-underlying
sibling" 257; leader -> "this contract" 42 / "a same-underlying sibling" 56; underlying -> "this contract" 113 /
"a same-underlying sibling" 135 / "another venue" 103 / "broadly" 4; sibling -> "a same-underlying sibling" 22;
other -> "a close cousin" 42 / "broadly" 13. I read 84 assignments, one per distinct (family, scope, applies_to)
combination across all eight families (listed in complete_audit.py's output). Right under the brief's definitions in
80 (for example CRUDE-4 MCL LPP "this contract" for MCL; CRUDE-3 "a same-underlying sibling" for MCL and "this
contract" for CL; EQUITY-3 ES HFT share "a close cousin"; FX-9 FX Micros MM program "this contract" for M6E; EQUITY-11
E-nano program "a same-underlying sibling"; METALS-21 London OTC gold "another venue"; CFTC-1 energy group "the product
group"). Questionable in 4: the three in N4 and the IIP relation in S2 (nine codes named by code labelled "the product
group").

**Residual blinding.** Beyond the lead's ruling (exchange names, asset words, micro/full-size words in news-cap facts),
the items that could identify a contract or firm are B1 (firm name inside plan names), S3 (contract sizes and ticks
inside s1 items) and N5 (filing numbers, launch-coincident dates, "[ref].txt" remnants). Labels: 80 new labels (47
K-, 5 V-, 28 W-), none equal to any of E.28's 124 (C01.., F01.., P01.., X01..); sheet label sets equal the key's;
47 contracts, 5 firms and 235 pairs map one-to-one.

## Counts checked and failed, per brief check

| check | checked | failed |
|---|---|---|
| 1 pairs: listed_50k vs A3_firm_products, fee_rt_usd vs A2 fee_rt (4 firms), Lucid RR-05 recomputed from F4's other-firm fees | 235 pairs | 0 (S4 is a ruling question) |
| 1 codes: tick_size, tick_value_usd, multiplier (and multiplier x tick = value) vs A3_facts/A1 | 47 x 4 | 0 (grain ticks converted from cents) |
| 1 codes: ADV value and kind vs A3_facts (E.28), newer figures only beside | 47 | 0 (4 newer beside: QM BTC M2K RTY) |
| 1 codes: spread_S and touch re-derived from the readers' T1 items under LR-S | 47 codes, 35 items | 1 basis misstated (HG, S1); 0 value errors; 13 sourced S, 5 sourced touch confirmed |
| 1 codes: settles_off_sibling, each true with a settlement quote; falses against every T5 item | 10 true, 37 false | 0 |
| 1 codes: siblings and leader (notional rule, readers' leader where unknown) | 47 | 0 |
| 1 codes: data_access vs F2_data_access (mbo_start, k, k_kind, o, p) | 47 | 0 |
| 1 firms: DLL, MLL, type, BC, flat-by, overnight, payout, news windows, P inputs vs E.28 and F2_firms | 5 x 9 | 0 (N2, N6 notes) |
| 2 S_mean and touch_mean vs F2 items | 3 + 11 | 0 (N8) |
| 2 IBKR venue vs F2_nonprop (fee per side and RT, status, 3 margins) | 47 x 6 | 0 (SIL fee "not published" carried) |
| 3 cross-family: every F2 item attached to exactly the codes it lists | 528 items | 0 (RATES-11 extended to 35 codes by the lead's rule, correctly; 7 unattached, N3) |
| 4 completeness: F2 items of T2a T2b T3 T4 T5(info_share) T6 T7 present under the right label and section | 16 codes, 560 items | 0 missing; 0 settlement items leaked |
| 4 verified level and window carried, all masked contract items | 1565 | 0 |
| 4 firm sheets: A, Rel, R facts per firm vs F2_firms and E.28 fields | 5 firms, 149 items | 0 missing |
| 4 pairs: listed_on_modelled_plan vs F4 listed_50k | 235 | 0 |
| 4 blinding: own greps (47 codes, 23 other codes, 13 firm names, 24 plan names, 22 platforms, 12 URL/path markers, reader item ids, E.28 labels) | 2 files | 1 firm (B1): 7 + 13 hits; 0 elsewhere |
| 4 labels fresh and consistent | 80 | 0 |
| 5 unmask.py: test suite; synthetic full ratings; out-of-scale value; unknown label; missing rating; unrated listed pair | 19 tests + 5 runs | 0 (19 passed; good run maps 47/235/5 exactly; the four bad cases refused with exit 2) |
| FT-1 o/p direction | 47 | 0 |
| FT-4 GC and HG session and threshold | 2 codes, 48 hourly values | HG basis (S1) |
| FT-8 IIP row and nature | 1 item, 35 attachments | relation and text (S2) |
| RR-05 floor | 23 listed Lucid pairs | 1 below (SIL, S4) |
| FT-9 relations sample | 84 of 1565 | 4 imprecise (N4, S2) |
| D6 keyword flags (mechanical) contradiction scan | 396 items | 0 |

## Not checked, or checked only in part

- The relation words were read for 84 distinct combinations, not all 1565 assignments; combinations not in the sample
  share a scope and family with one I read.
- The E.28 firm models used by the econ run (reports/stage_e28_briefs/work/A3_econ/) were not opened; firm limits were
  checked against A3_firm_products.json and A2_firm_*.json, which the FactTable's econ firm_check also passed.
- No market data, no web, no F3 recomputation (F3 is VolCoder's; its reviewer is another worker).
- The BlindScorer's reading of the IIP item and of the residual words is a rating question, outside this audit.

## Re-check of the patch (FINAL2)

Run 2026-10-29 03:22-03:27 PDT on the files whose sha256 match F4_masks_FINAL2.txt (contracts 580dae9d..., firms
1a0595e5..., key 5ae2a549..., 03:20:50 PDT); F4_facts_unmasked.json unchanged (4a4d1e29...). Helpers: work/factaudit/
leak_audit.py --substring (output leak_audit_out2.txt), unmask_synth.py (rerun), synth_ratings_good_prepatch.json
(the pre-patch synthetic ratings, kept for the label comparison).

**Verdict: FAIL, one BLOCKING item left (a firm name in the MFFU sheet); everything else in the patch verified.**

- **BLOCKING B2. F4_masked_firms.json, firm V-CXFO (= mffu), R_facts_firm_wide item I-2721556
  (restrictions.hedging_ban):** `"quote": "MyFunded Futures prohibits hedging of any kind."` The firm's name with one
  unusual space; the FactTable's patterns ("My Funded Futures", "MyFundedFutures") and leak_check_v2.py missed it, as
  did my first pass. One substitution ("[the firm] prohibits hedging of any kind.") fixes it; the key and labels need
  no change.
- B1 fixed: "Lucid", "LucidBLACK/Daily/Maxx/Live", "Flex", "Daily Trading" 0 hits in the firms sheet (substring, any
  case); the four items I named (I-7695386, I-1735555, I-1219000, I-0716183) now read plan P1..P6 / live stage;
  "red folder" (2) stays as a generic phrase. The extension to V-FRQI, V-PCAN and V-CXFO (Pro, Flex, xfa/lfa words,
  live funded account) leaves no capitalised plan name in either sheet (Select, Combine, Rapid, Growth, Builder,
  Express: 0 word hits in the contracts sheet; "Master" 13 = "Research Master thesis").
- S2 fixed: 35 IIP items carry their own fee-table row as the quote ("Fee table row: [product name] (K-LRVK)1 $0.90 |
  The purpose of this Program is ...", "Core Metal (K-LGJM, [another product], [another product])1 $1.00", "[size
  class] Equity Index – Futures $0.18", "U.S. Treasury Futures $0.54", "[size class] Agricultural Contracts $0.90");
  applies_to "this contract" for CL QM QG NG GC SI HG MGC SIL, "the product group" for the other 26; no other
  contract's label inside any copy.
- S3 fixed: "bbl" 0, "0.0x tick" 0, "EUR/AUD n,nnn" 0, "$5 Multiplier" 0 (now "([multiplier])"); the remaining
  "tick" figures are costs, quoting obligations ("max spread 32 ticks") and "tick data", not tick sizes.
- Substring leak audit (names without word boundaries, any case), both sheets: codes, other codes, item ids, E.28
  labels, URLs and paths 0; platforms 0 (the "Rithmic" hits are "algorithmic", "ATAS" is "dataset"); firm names: 1
  (B2); plan-name vocabulary left in field keys and notes, SHOULD FIX, weaker than a name but the same words the
  patch replaced elsewhere: `combine_consistency`, `combine_min_days` (V-FRQI I-7933657 payout_qualification;
  "Trading Combine"), `builder_50k` and the what-field `restrictions.news_builder` (V-CXFO I-4787111, I-6573682;
  "Builder"), "growth eval 2026-10-14" (V-PCAN I-9780314 plan note; "Growth"), "master-trading-rules" and
  `master_inactivity` (V-OJVP I-3054604, I-1738667; "Master Account"). Everything else matched is a generic word
  (directional, combined, selected, rapid trades, sim funded, straight through, payout_qualification).
- The FactTable's 141 "justified" hits (work/facts/leak_v2_out.txt) reviewed: 46 lowercase "daily trading volume",
  8 "dataset", 15 "algorithmic", 40 currency pairs / years / "USD 10,000 monthly incentive" / TOB-size statements,
  12 "[multiplier]" placeholders, 16 cost or quoting figures in ticks, 1 "Daily Loss Limit", 1 "Algorithmic" in the
  firms sheet. All justified; none identifies a contract or firm. The gap was the pattern set, not the judgments.
- Labels and ids: the 47 contract, 5 firm and 235 pair labels equal the FINAL key's (compared with my synthetic
  ratings file built from the FINAL key at 01:49); 28 platform labels; 2684 item ids in the key and 2684 in the two
  sheets, one-to-one, same count as the 01:30 build log; 1565 relations, every masked id mapping to its logged
  source; new key sections are only `plan_labels` (per firm) and `patches`. I did not byte-compare against the FINAL
  key itself (no copy under my paths; the FactTable reports checking against its backup). F4_corrections.json holds
  exactly one entry: HG spread_S sourced true -> false, clause "none: S = 1 (u)", item METALS-50.
- unmask.py: test_unmask.py 19 passed; the pre-patch synthetic ratings unmask on the patched key (47 codes, 235
  pairs, 5 firms, exit 0); a fresh synthetic set maps every label exactly; the out-of-scale, unknown-label, missing-
  rating and unrated-listed-pair cases are refused with exit 2.
