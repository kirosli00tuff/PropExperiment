# Stage E.32b wave-C briefs (one section per worker)

Written by the lead (session 3, Opus 5.5 max) on 2026-10-29 from about 01:00 PDT. Read "Common rules" and "Shared data
contract" in briefs/brief_wave_b.md (they apply unchanged), then only your own section here. The frozen spec
reports/stage_e32b_ranking_spec.md (sha256 09ebe6970fcf027009152fa81a414360a015d535b095138cdf65cf1a4eb58635) is the
contract: never edit it. The BlindScorer does NOT read this file (its brief is briefs/brief_blind.md).

## C1 FactTable-OpusHigh (worker-high, opus): F4, the fact table, masked sheets and mask key

Objective: assemble every fact the scripts and the BlindScorer need into the files below (spec sections 1, 3, 4, 6).
You assemble and mask; you never score or rate anything.

Read first (by section; grep or short scripts; never load a large JSON whole into your context):
- spec sections 0, 1, 3, 4, 6 and 9.2;
- briefs/work/score/SCHEMA.md sections 2 and 3: the EXACT field names of F4_facts_unmasked.json and of the unmasked
  ratings file. They override the sketch in brief_wave_b.md;
- briefs/work/F5/SCHEMA.md "F4_facts_unmasked.json (read fields only)";
- briefs/work/econ/README.md ("How to run", preconditions) and briefs/work/econ/econ32b_inputs.py: which F4 fields the
  econ code reads and how firm names are matched to E.28's firm models (case-insensitive);
- briefs/work/score/README.md "Interpretation points" 4, 9, 10, 11 and 13.

Inputs (read-only):
- E.28 facts (F1): reports/stage_e28_briefs/A1_*.json, A2_firm_*.json, A2_platforms.json, A3_facts.json (and .md),
  A3_firm_products.json, A3_lead_rulings_v2.json (RR-05 and the other rulings), A0_contract_stats.json (ADV v_0),
  A3_masked_contracts.json and A3_masked_firms.json (format model only), A3_mask_key.json (only to avoid reusing E.28's
  labels).
- New facts (F2): briefs/F2_{crude,natgas,metals,grains,rates,equity,fx,crypto}.json, F2_shared_cftc_automation.json,
  F2_shared_baltussen.json, F2_firms.json, F2_data_access.json (primary fields, plus its k_ZM and p_brief fields),
  F2_nonprop.json (IBKR, for output 3 only). briefs/F3_vol.json (status per code, median_close).

Lead rulings in force (verbatim from reports/stage_e32b_STATE.md; do not read the STATE file):
- LR-S (spread and touch). S stays the spec's "sourced median main-session spread". A figure qualifies if it covers
  the main session, the US day session or the whole day and is (i) a median, or (ii) a mean, time-weighted mean or set
  of hourly means all below 1.5 ticks: quoted spreads are whole ticks >= 1, so P(S >= 2) <= mean - 1 < 0.5 and the
  median is exactly 1 tick (a derivation, not a substitution), or (iii) a sourced statement that the spread sits at one
  tick more than half the time, for the tick size in force in the F3 window (ZT's 2018 figure predates its 2019 tick
  change: not qualifying). Anything else (a mean >= 1.5 ticks, another named session such as Asia hours, an unstated
  session, snippet-only) leaves S = 1 (u) as spec section 1 says. Touch size counts only as a sourced median (D4 L).
  Declared variant S_mean: for a code with no qualifying figure, S (and touch) = its sourced mean or average (main
  session, US day hours, whole day or unstated session; not another named session; not snippet-only), the figure whose
  window is nearest the F3 window (2022-11-01..2023-10-31); expected to move MNG (2.41) and BTC (4.72, Apr 2023) at
  least.
- A figure for one code never stands for another code: no sibling transfer of S or touch.
- LR-D0..D3 are already applied inside F2_data_access.json (primary fields); copy them, do not recompute.
- FirmRules (F2_firms.json) found no DLL or MLL change since E.28 (only Bulenox payout rules changed). If your firm
  DLL or MLL differ from E.28's firm models anyway, stop and report it: the econ run refuses (rc 3) on a mismatch.

Field rules:
- All 47 codes of spec 0 (NQ with excluded true; it keeps its facts, because MNQ is its satellite and NQ counts in
  family shares), the 5 firms, and every (firm, code) pair of A3_firm_products.json with listed_50k true, false or
  unknown, updated only by a verified F2_firms change (new value used, E.28 value shown beside, both items cited).
- ADV: E.28's (A0 v_0 front-contract median over the standard window, or the published all-expiry figure); a newer
  sourced figure goes beside it, never in its place (spec 1).
- spread_S and touch: by LR-S, each with the F2 item id it rests on and the LR-S clause used ((i), (ii), (iii) or
  "none: S = 1 (u)"). sourced = true only for a qualifying figure.
- settles_off_sibling: true only where an F2 item states that the contract is financially settled at a sibling's
  settlement price (the readers report: MCL and QM at CL; QG and MNG at NG; the micro grains at the full-size; check
  MHG against F2_metals.json). Physically delivered contracts (the mini grains XC XK XW, MGC, SIL, M6E, M6A) and index-
  or benchmark-settled ones (MBT, MET, the micro equities, the micro yields) are false. Cite the item for every true.
- Cross-family items go to every code they name: the CME International Incentive Program item in F2_rates.json; the
  MNG prop-firm volume incentive; the FX Micros, Micro E-mini and micro-yield market-maker programs; the CBOT grain
  overnight-session and deferred-month programs; the GC/SI/HG volume incentive; the CL programs and the MCL Liquidity
  Provider Program; the NG program; the Micro Crypto fee-discount program. The CFTC group figures and the 2020 HFT
  shares (F2_shared_cftc_automation.json) go to every code of the matching product group or named contract; the
  Baltussen rows (F2_shared_baltussen.json) to every code of the matching asset class.
- pauses: scheduled pauses inside or next to the main session from the readers' session-structure facts (for example
  the grains' 07:45-08:30 CT break), each with its item.
- firms: DLL, MLL and its type, BC acceptance, flat-by-close time, overnight rules, payout qualification (winning-day
  minimums, consistency rules, per E.29 where E.28 cited it), news windows (events, products, minutes before and after),
  the P inputs and the Rel facts, from E.28 updated by F2_firms.json.
- pairs: listed_50k; fee_rt_usd (all-in round trip); fee_kind "stated" or "RR-05 (u)" (Lucid: the highest fee for that
  product at the other four firms, unless Lucid states an all-in fee); the news-window items that name the product or
  its class.
- Unknowns stay unknown (null plus a reason). Do not look anything up: no web access in this task. List every missing
  fact the scripts need in the for_lead list.

Outputs (briefs/ unless stated), in this order:
1. F4_facts_unmasked.json, exactly as SCHEMA.md section 2 (plus `spec_sha256`). Validate it before anything else:
   import (do not run) the econ input loader from work/econ/econ32b_inputs.py and the F4 checks in work/score/*.py and
   F5's reader, and call them on the file; fix until they pass. Then write F4_unmasked_READY.txt (one line: the sha256
   of F4_facts_unmasked.json and the PDT time). From that moment the file is FROZEN (the lead starts the econ run on
   it, and the run fingerprints it): never edit it again. Any later correction goes to F4_corrections.json as a list
   of {code or pair, field, old, new, item, reason} for the lead.
2. F4_smean.json: the S_mean variant per LR-S: {"codes": {CODE: {"spread_S_mean": {value, item, window, kind},
   "touch_mean": {...} or null}}, "unchanged": {CODE: reason}}.
3. F4_venue_ibkr.json: the own-broker venue (F2_nonprop.json): per code the all-in fee per side and per round trip in
   USD with components and items, intraday and overnight initial margin in USD with items, market-data fee, account
   minimum, overnight holds allowed, no DLL, MLL or flat-by-close (own account), capital ceiling null with the note
   "none recorded in docs/DECISIONS.md: spec 8.3 uses USD 6,000 (u)".
4. F4_masked_contracts.json and F4_masked_firms.json, the BlindScorer's only inputs (format model: E.28's
   A3_masked_*.json). Each starts with a "format" field that explains its structure and the evidence levels.
   - Labels: fresh random labels from the secrets module, a different scheme from E.28's (E.28 used C07, F04 and the
     like; use, for example, "K-" plus 4 random letters for contracts and "V-" plus 4 for firms; a pair is
     "<firm label>|<contract label>"); none may equal any E.28 label.
   - Per masked contract (all 47, NQ included under its own label without saying it is excluded): the facts for D2 a
     (automated or HFT shares for the product and for its CME product group: figure, year, scope, verified level),
     D2 b (market-maker, lead market-maker and volume-incentive programs for its outright futures in force at any time
     in 2021-2026, or a source that documents none), D3 s1 (spread relationships, cointegration, lead-lag, with
     horizon), s2 (scheduled releases, timing, absorption speed with quotes), s3 (session handoffs), Sat (iii) (
     information-share or price-discovery studies with the share), and D6 (directional evidence: study, horizon, data
     period, in or out of sample, net of costs, finding, verified level). Nothing else: no ADV, size, multiplier, tick,
     fee, settlement method, sibling or leader relationship.
   - Per masked firm: A facts (automation and API rules, order-rate, minimum-hold and scalping rules, evaluation and
     funded stages) and Rel facts (operating age, payout delays, denials or disputes and material rule changes in the
     12 months before the lookup, regulatory actions against the firm itself), each with its date. Per masked pair: R
     facts (news windows and product restrictions that apply to that contract at that firm, trading-hour limits, and
     which plan or stage a rule binds).
   - Quotes stay verbatim except that product names, product codes, firm names and platform names are replaced by the
     labels (asset-class words such as "crude oil" or "weekly inventory report" stay; spec 6). No URLs, file paths,
     page names or the readers' item ids: give fresh item ids (the key maps them back). Every evidence item carries its
     verified level (full text, abstract, snippet [unverified]).
   - Leak check: a script greps both masked files for every code, product name, firm name and platform name in the
     universe (E.28's lists and A2_platforms.json), for "http", "www", ".com", "reports/", ".json", ".md" and for every
     E.28 label; zero hits required (log the counts in your build log).
5. F4_mask_key.json: contract, firm and pair labels to codes, firms and pairs; masked item ids to source item ids.
6. work/facts/unmask.py with a test: reads briefs/F4_blind_ratings_masked.json (the BlindScorer's output; its shape is
   in briefs/brief_blind.md) and F4_mask_key.json and writes briefs/F4_blind_unmasked.json exactly as SCHEMA.md
   section 3. It refuses on an unknown label, a missing rating or a value outside its scale.
7. F4_facts.md: readable unmasked tables (codes, firms, pairs, S and touch with the LR-S clause, settles_off_sibling,
   cross-family items, data access, unknowns), for the lead and the reviewer.
8. work/facts/: your helper scripts and build_log.txt (counts: codes, firms, pairs listed/unlisted/unknown, S sourced,
   S_mean changes, masked items, leak-check hits).

Boundaries: write only briefs/F4_* and briefs/work/facts/. Never edit the F2 or F3 files, the spec, or anything in
work/score, work/econ or work/F5 (import and call only). Never run the econ or score computations. No web access, no
market data. E.28 measured 24 minutes for its FactTable.

Return: the output paths; a summary of at most 200 words with the counts above; the for_lead list (cases the rules
above do not settle, with your proposed reading); anything you could not finish.

## C5a F5Runner-OpusXHigh (worker-xhigh, opus): provisional Layer 1, survivors' F5 rows, own-broker venue

Objective: (a) list the Layer 1 survivors before the economics run ends; (b) wire the own-broker venue (IBKR) into the
F5 code; (c) compute the survivors' F5 rows. Precondition: briefs/F4_blind_unmasked.json exists (the lead unmasks the
BlindScorer's ratings first).

Read first: spec sections 3 (Layer 1 gate), 7 and 8.2-8.3 (own-broker venue); work/F5/SCHEMA.md, work/F5/README.md;
work/score/README.md "Run" and SCHEMA.md sections 4 and 8; briefs/F4_venue_ibkr.json "format" or top-level fields.

(a) Provisional Layer 1. Layer 1 (D1-D6, the gates) does not use E, so an exact Layer 1 can be computed before the
economics run ends. Build work/F5run/econ_stub_layer1only.json: for every pair score32b.py requires (SCHEMA.md section
4), the blocks primary, E_dir60 and spread1 each with above_cap {mu_star: true, mu10K: true}, mu_star_mkt, mu10K_mkt,
m_star and m10K null, cost_per_attempt 0, grid_cap 0, sigma60 from F3 (and "stub": true if the script tolerates it).
Run score32b.py with the real F3_vol.json, F4_facts_unmasked.json, F4_blind_unmasked.json, F2_attention.json,
F2_data_access.json and the stub econ, --out work/F5run/score_stub_layer1only.json --md ...md. Use only its Layer 1
fields: everything in it about E, L2, S, pair ranks or top 15 is meaningless and must not be copied anywhere. Write
work/F5run/L1_provisional.json and .md: per code, D1-D6, L1, the gate result with the spec's arithmetic line
("sigma_60 = x ticks vs 2 x (S + 0.5) = y ticks"), and D4's L, J, Sat with the rule that set Sat; plus the survivors
list. If the script refuses the stub, stop and report the refusal text; do not edit score32b.py.

(b) Own-broker venue. Add to work/F5/f5_holding.py an optional input (for example --venue-file
briefs/F4_venue_ibkr.json) that adds rows "ibkr|<CODE>" for each selected code, with tests (run only your tests and
the existing F5 tests: `uv run pytest -q reports/stage_e32b_briefs/work/F5/`). Lead rulings:
- LR-F5-IBKR: c_f = c_RT + F_rt / v with F_rt = 2 x the all-in fee per side; an own account has no DLL, MLL or
  flat-by-close, so the band is B = {h in {5, 15, 30, 60, 120, 240, OC} : G(h) <= 1.10 min G} (no DLL or flat-by-close
  condition; intraday holds end by the main session's end); overnight rows report the overnight margin.
- LR-Q6d: spec 8.3's own-broker Q6 inputs are reported per code: one contract's initial margin (intraday and
  overnight) against the ceiling USD 6,000 (u), and sigma_day = sigma_cc (F3 overnight close-to-close) x tick value in
  USD against 2% of that ceiling (USD 120), with sigma_OC x tick value beside.
Firm rows for the five firms stay exactly as the HoldingCoder wrote them.

(c) Run f5_holding.py with a minimal selection work/F5run/F5_selection_survivors.json (layer1_survivors from (a),
top15 empty) plus the venue file -> work/F5run/F5_survivors.json and .md. The final F5_holding.json comes later from
the lead's selection (survivors plus the real top 15).

Boundaries: write only work/F5run/ and the F5 code and tests in work/F5/ (keep every existing test passing). Never edit
score32b.py, the econ code, the F2/F3/F4 files or the spec. No web access, no market data. Light jobs only (no heavy
lock needed for seconds-long runs; the economics run holds the heavy lock).

Return: paths; at most 200 words: the survivors (count and codes), the gate failures by reason, each survivor's
G_argmin, the IBKR rows' bands, test counts; anything unfinished.

## C1v FactAuditor-FableXHigh (worker-xhigh, fable): independent check of the fact table before scoring

Objective: verify the FactTable's outputs independently, before the blind rating and the score run, so that input
errors are found while they are cheap to fix. You did not build them; check them against their sources. Read-only.

Read first: section C1 above (the FactTable's brief, including the lead rulings LR-S and the field rules); spec
sections 1, 3, 4 and 6; work/score/SCHEMA.md sections 2 and 3. Then the FactTable's outputs: briefs/F4_facts_unmasked.json,
F4_smean.json, F4_venue_ibkr.json, F4_masked_contracts.json, F4_masked_firms.json, F4_mask_key.json, F4_facts.md,
work/facts/ (build_log.txt, unmask.py and its test), F4_corrections.json if present. Sources: the F2 files, F3_vol.json
and the E.28 files that C1 lists. Read by section with short scripts; never load a large JSON whole.

Checks (script them where possible; report counts checked and failed per check):
1. Economics and score inputs, every value: per pair listed_50k, fee_rt_usd and fee_kind (Lucid RR-05 = the highest fee
   for that product at the other four firms, unless Lucid states an all-in fee); per code tick_size, tick_value_usd,
   multiplier, ADV (E.28's figure, a newer one only beside it), spread_S and touch (the LR-S clause and the item:
   re-derive each code's S from the readers' spread items yourself and compare), settles_off_sibling (each true has an
   item that states financial settlement at a sibling's settlement price), siblings and leader, data_access fields
   against F2_data_access.json; per firm DLL, MLL and type, BC acceptance, flat-by-close, overnight, payout
   qualification, news windows and the P inputs against E.28 and F2_firms.json.
2. S_mean values (LR-S variant) and the IBKR venue values against F2_nonprop.json.
3. Cross-family items: each program or shared study is attached to every code it names (C1's list), and to no other.
4. Masked sheets. Completeness: for a sample of at least 12 contracts across all eight families (include NQ, ZM, ZL,
   QM, MGC and one micro yield) and every firm, every D2 a, D2 b, D3, Sat (iii), D6, R, A and Rel fact in the F2 and
   E.28 sources appears under the right label (use the key), with the right "applies_to" relation, verified level,
   dates and plan or stage scope. Blinding: rerun a leak check with your own greps (every code, product name, firm
   name, plan name and platform name, URLs, file paths, reader item ids, E.28 labels); labels are fresh (none equal to
   an E.28 label); nothing in a masked sheet beyond the rating facts (no ADV, size, tick, fee, settlement method,
   sibling or leader).
5. unmask.py: run its test, then feed it a synthetic ratings file you write in work/factaudit/ (every label, values on
   the scales, one out-of-scale value, one unknown label) and check that it maps correctly and refuses the bad cases.

Output: briefs/F4_audit.md: a verdict line, then items labelled BLOCKING (a wrong value that feeds a score, a leak, a
missing rating fact), SHOULD FIX or NOTE, each with the field, the F4 value, the source value with a verbatim quote
and its file and item id, and the fix. Helpers in briefs/work/factaudit/ only.

Boundaries: never edit any F4 file or anything outside work/factaudit/ and F4_audit.md; do not run the economics or
score computations; no web access, no market data.

Return: the path; at most 200 words: verdict, counts, the BLOCKING items in one line each; anything unchecked.

## C4v VariantBuilder-SonnetHigh (worker-high, sonnet): the lead-ruling variants file for the score run

Objective: write reports/stage_e32b_briefs/work/score/build_lead_variants.py, which writes
reports/stage_e32b_briefs/work/score/lead_variants.json in the exact format of work/score/SCHEMA.md section 6 (read
it, and the SCHEMA sections for the files you patch). Mechanical: every value below is decided; if a case needs a
judgment, stop and report it.

Rulings (names must not repeat a declared variant of spec 5):
1. "RL-SMEAN" (ruling LR-S, variant S_mean). F4 patches: codes.HG.spread_S = {value 1.55, sourced true, item
   "METALS-50", clause "S_mean variant"}; codes.MNG.spread_S = {2.414, true, "NATGAS-3", ...}; codes.BTC.spread_S =
   {4.72, true, "CRYPTO-2", ...}; codes.10Y.spread_S = {1.67, true, "RATES-5", ...}; and touch = {value, sourced
   true, item, clause "S_mean variant"} for every code that has a touch_mean in briefs/F4_smean.json. Econ patches:
   for each pair in briefs/econ32b_smean.json (lucid|HG, tradeify|HG, bulenox|HG, topstep|MNG), that file's
   "primary" block replaces pairs.<pair>.primary of briefs/econ32b.json. No params flipped.
2. "RL-KZM" (ruling LR-D1, variant k_ZM): for every code where F2_data_access.json's k_ZM value differs from its
   primary k, patch the F4 data_access field that score32b.py reads for k with the k_ZM value.
3. "RL-PBRIEF" (ruling LR-D2, variant p_brief): for every code where p_brief differs from primary p, patch the F4
   data_access p field (F4 stores p_all_read as a boolean: true when the D5 score p = 1; the FactTable converted the
   primary the same way).
4. "RL-TRECENT" (ruling FT-2, variant T_recent): for every code whose F4 touch figure rests on data from before
   2015-01-01 (read each touch item's window in F4_facts_unmasked.json and briefs/F4_facts.md), touch = {value null,
   sourced false, clause "T_recent: pre-2015 touch not counted"}.
Each patch carries "source" (the file and field it came from). The builder must check that every patch path exists in
its target file (F4: briefs/F4_facts_unmasked.json; econ: briefs/econ32b.json; if econ32b.json or econ32b_smean.json
does not exist yet, write the F4 patches, list the econ patches as pending, and exit 3; the lead reruns the builder
when both exist). Print a summary: patches per ruling, and the codes each one touches.
Write a small test (synthetic inputs) and run it with `uv run pytest -q <your test>`.

Boundaries: write only work/score/build_lead_variants.py, work/score/test_build_lead_variants.py and
work/score/lead_variants.json. Never edit score32b.py or any input file; do not run score32b.py; no web, no market data.
Return: paths; at most 120 words: patch counts per ruling, codes touched, test result, pending items.
