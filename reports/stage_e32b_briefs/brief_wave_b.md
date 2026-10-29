# Stage E.32b wave-B briefs (one section per worker)

Written by the lead (session 2, Opus 5.5 max) on 2026-10-28 from about 22:55 PDT. Read "Common rules" and "Shared data
contract", then only your own section. The frozen spec reports/stage_e32b_ranking_spec.md (sha256 09ebe6970fcf0270
09152fa81a414360a015d535b095138cdf65cf1a4eb58635) is the contract: never edit it; read the sections your section names.

## Common rules

- Repo: /home/kiros-li/Documents/GitHub/PropExperiment. All paths below are relative to it. Output folder:
  reports/stage_e32b_briefs/ (written "briefs/" below).
- Workers that fetch web pages (FirmRules, DataAccess, NonProp, IdeaFamilies) follow briefs/READER_RULES.md in full.
- Coders: work only in your own work folder; write unit tests and run only your own (`uv run pytest -q <your tests>`),
  never the full suite. Run at nice 10, at most os.cpu_count()//2 processes (never more than 8). Any run expected to
  take more than 2 minutes or 1 GB goes through `flock briefs/work/heavy.lock <command>` so that only one heavy job runs
  at a time across all workers; check `free -m` first. Long runs are resumable (parts on disk). Logs go to files; read
  only tails.
- Never: read market data (VolCoder's allow-listed files are the only exception); call Databento, a broker, TopstepX or
  the ProjectX API; read, print or copy any key or .env value (AttentionCounter's OPENALEX_EMAIL is used inside a request
  only, never printed or written); write outside your own paths; edit any file of Stages E.28 to E.33 (reading is allowed
  where your section says); run git commands that change anything; spawn agents. No outcome of any strategy is computed
  or read anywhere.
- Write outputs incrementally. If you were re-spawned after a cut, read your partial outputs and logs first and continue.
- Hook, cost or budget notices addressed to the session are informational: keep working. The one exception: a WebSearch
  that says the search budget is used up (stop searching, log the notice with the time, finish from what you have).
- A GateGuard hook may deny your first Bash command or your first Write or Edit of a file and ask for facts. State the
  facts it asks for in your reply and retry the same call.
- Times in PDT from `TZ=America/Vancouver date`.
- Facts only: readers never score. Coders implement the frozen spec's rules and run them only on synthetic fixtures in
  this wave.
- Return: the output paths; a summary of at most 200 words; what you could not finish, and why.

## Shared data contract (file names in briefs/; field names fixed here, ScoreCoder's work/score/SCHEMA.md adds detail)

- F2_<family>.json (family readers; schema in briefs/brief_family_readers.md), F2_shared_cftc_automation.json,
  F2_shared_baltussen.json, F2_firms.json, F2_data_access.json, F2_attention.json, F2_nonprop.json,
  R1_closed_lines.json, R2_idea_families.json.
- F3_vol.json (VolCoder). All statistics in ticks of the code's own tick size, after any OC-1 transfer:

      { "spec_sha256", "window": "2022-11-01..2023-10-31", "generated_pdt", "files_opened": ["..."],
        "roots": { "<CODE>": {
          "status": "owned | OC1 | unknown", "oc1_source": null, "oc1_factor": null,
          "tick_size": 0.25, "n_dates": 0, "L_main": 390, "main_session_pt": ["06:30", "13:00"],
          "h": { "1": {"sigma": 0.0, "m": 0.0, "median_abs": 0.0, "p99_abs": 0.0, "n": 0},
                 "2": {}, "5": {}, "15": {}, "30": {}, "60": {}, "120": {}, "240": {} },
          "OC": {"sigma": 0.0, "m": 0.0, "n": 0},
          "overnight": {"cc": {"sigma": 0.0, "m": 0.0, "n": 0}, "on": {"sigma": 0.0, "m": 0.0, "n": 0}},
          "R_d": {"median": 0.0, "p99": 0.0, "n": 0}, "main_range_median": 0.0, "median_close": 0.0 } } }

- F4_facts_unmasked.json (FactTable, wave C), sketch:

      { "spec_sha256",
        "codes": { "<CODE>": { "family", "underlying", "excluded": false, "tick_size", "tick_value_usd", "multiplier",
          "adv": {"value", "kind", "source"}, "spread_S": {"value": null, "sourced": false, "item"},
          "touch": {"value": null, "sourced": false, "item"}, "siblings": [], "leader": "<CODE>",
          "settles_off_sibling": {"value": null, "sibling": null, "item"}, "main_session_pt", "pauses": [], "listing",
          "data_access": {"mbo_start", "k_usd_month", "k_kind", "o_owned_36m", "p_all_read"} } },
        "firms": { "<firm>": { "dll_50k", "mll_50k", "mll_type", "bc_accepts", "flat_by_close", "overnight": {},
          "payout": {}, "news_windows": [],
          "p_inputs": {"native_api", "oco_api", "vps_chicago", "api_rate_limit_per_s"}, "rel_facts": {} } },
        "pairs": { "<firm>|<CODE>": { "listed_50k": true, "fee_rt_usd", "fee_kind": "stated | RR-05 (u)",
          "news_window_items": [] } } }

- F4_blind_unmasked.json (the lead unmasks the BlindScorer's ratings, wave C), with R = {"value", "unknown", "reason"}:

      { "codes": { "<CODE>": { "D2a": R, "D2b": R, "s1": R, "s2": R, "s3": R, "sat_iii": R, "D6": R } },
        "pairs": { "<firm>|<CODE>": { "R": R, "A": R } },
        "firms": { "<firm>": { "rel_age": R, "rel_payout": R, "rel_rules": R, "rel_regulatory": R } } }

- econ32b.json (EconCoder, wave C):

      { "spec_sha256", "grid": {},
        "pairs": { "<firm>|<CODE>": {
          "primary":  {"mu_star_mkt", "mu10K_mkt", "above_cap": {"mu_star": false, "mu10K": false},
                       "cost_per_attempt", "sigma60", "m_star", "m10K", "grid_cap"},
          "E_dir60":  {same fields}, "spread1": {same fields},
          "E_dir": {"30": {}, "120": {}, "240": {}} } } }

## B3 FirmRules-OpusHigh (worker-high, opus)

Objective: the firm facts that Layer 2 (R, A, D, Rel, P), F5 and R2 need, verified on the firms' own pages as of now, for
Topstep, Lucid, Tradeify, MFFU (MyFundedFutures) and Bulenox, standard 50K plan. Spec sections 0, 4, 7 and 8.3 Q6 say
what they feed.
Inputs: reports/stage_e28_briefs/A2_firm_<firm>.json and .md (facts of 2026-10-21), A2_platforms.json, A3_facts.json
(grep firm rows), A3_firm_products.json; reports/stage_e31_inputs/planner_research_notes.md (pointers: "Topstep's Tier 1
list blocks named minis only" and "MFFU's EIA rule covers energy": verify both on the firm pages); reports/E.29_RETURN.md
section 1 (payout reachability).
Facts per firm; beside every changed value give the old value and its E.28 field path:
1. 50K plan product list: changes against A3_firm_products.json for the 47 codes of spec section 0.
2. News windows: which events, which products (Topstep's Tier 1 list product by product, exactly as the page states),
   minutes before and after, evaluation and funded stages.
3. Flat-by-close time (with zone), session cut-offs, weekend rule; overnight holds (allowed in evaluation and in funded
   accounts; overnight margin or contract limits; fees).
4. 50K daily loss limit and maximum loss limit: amounts, trailing type (intraday, end of day, static), lock level.
5. Payout qualification: winning-day minimums (count, minimum profit per day), consistency rules, buffers, minimum days,
   caps.
6. Automation: API or automated trading in evaluation and funded stages; named platforms; published order-rate limits,
   minimum-hold or scalping rules (seconds), HFT prohibitions; changes since 2026-10-21.
7. Fees: Lucid's all-in fee per product if Lucid now states it (commission plus exchange and NFA fees); any fee change
   at any firm for the 47 codes.
8. Reliability inputs: firm start date; documented payout delays, denials or disputes in the last 12 months (sourced;
   forums are pointers only); material adverse rule changes in the last 12 months (date, what); regulatory actions
   against the firm.
9. British Columbia residents accepted or not; platform and API inputs (native or documented API, OCO or bracket orders
   on the API, VPS near Chicago allowed or prohibited, API rate limit) where changed.
Output: briefs/F2_firms.json {"firms": {"<firm>": {"<field>": {"value", "old_value", "old_path", "changed", "quote",
"source": {"file", "url", "fetched_utc", "sha256"}, "verified"}}}, "notices": [], "gaps": []} and briefs/F2_firms.md
(at most about 80 lines a firm). Pages: briefs/pages/FIRMS/ with log.tsv; helpers: briefs/work/FIRMS/. WebSearch
budget 50. Reuse first; refetch what changed and what F5 and R2 need (items 2 to 7).
Boundaries: public firm pages, help centres and terms only; no login, account or API call; no TopstepX credential.

## B4 DataAccess-SonnetHigh (worker-high, sonnet)

Objective: the inputs of spec section 3 D5 (h, k, o, p) and the data facts R2 needs, per code (the 47 codes of spec
section 0). Apply the rules below mechanically; where they do not settle a case, write it under "for_lead" and move on.
(a) h: Databento GLBX.MDP3 MBO history start per product, from Databento's public documentation and dataset pages (no
    API, no key), and the product's listing date (E.28 A1_<family>.json listing fields): start = the later of the two.
    Quote and save the pages.
(b) k: approximate USD price of one month of front-contract MBO per product:
    - if Databento publishes a per-GB or per-record price for GLBX.MDP3 MBO, record it (quote);
    - from ledger/databento_spend.jsonl, read only by a script that prints summaries (fields: event = quote, commit or
      settle; schema; symbol; date; quoted_usd; billable_bytes), using "quote" events only: per root and schema, USD per
      month = the sum of quoted_usd over the root's quote lines for that schema / the number of months they cover (state
      the months);
    - method, in this order: (1) a ledger MBO quote for the root: its USD per month; (2) else the root's ledger mbp-1
      USD per month x r, r = MES's MBO USD per month / MES's mbp-1 USD per month over the same months (2025-05..2026-04);
      also report ZM's ratio for comparison (different months; not used); (3) else the root's tbbo USD per month x MES's
      MBO / tbbo ratio; (4) else unknown. Label each k "ledger MBO", "scaled from mbp-1 (estimate)", "scaled from tbbo
      (estimate)" or "unknown".
(c) o: does the program own one-minute bars or book data (MBO, MBP, TBBO) for the product or a same-underlying sibling
    covering at least 36 months before 2024-03-01 outside every sealed window? From folder and file names only (`ls`
    under data/vendor/databento/GLBX.MDP3/<schema>/); never open a data file.
(d) p: per spec D5 p. Build the census: per underlying, the date ranges read by registered bar-based or directional
    searches (ledger/trial_registrations.jsonl: 10 registrations, N 838; the E.23 inventory
    reports/stage_e23_briefs/inventory_compact.txt and inventory/), each with registration id and source line, and the
    sealed windows. p = 1 only if no unread, unsealed stretch of 36 months or more remains before 2024-03-01 within the
    available history (from the later of the listing date and Databento's GLBX.MDP3 start, verified on its docs) and no
    window of the underlying is sealed for a future test; else 0; unsettled cases go to for_lead.
Sealed and spent windows: from `uv run python -m data.holdout status` (names and windows only),
`uv run python reports/stage_e32_briefs/seal/soy_test_seal.py status`, docs/DECISIONS.md and docs/STAGES.md (grep:
holdout, embargo, seal, research window), reports/E.33c_RETURN.md. List each with its source.
Output: briefs/F2_data_access.json {"codes": {"<CODE>": {"mbo_start", "mbo_start_source", "listing_date", "k_usd_month",
"k_method", "k_inputs", "owned": [{"schema", "root", "first_month", "last_month", "sealed"}], "o_owned_36m",
"sealed_windows", "read_windows", "p_all_read", "p_basis"}}, "ratios": {}, "published_prices": [], "for_lead": []} and
briefs/F2_data_access.md. Pages: briefs/pages/DATA/ with log.tsv; helpers: briefs/work/DATA/. WebSearch budget 20.
Boundaries: names only for market data; the ledgers read-only; no Databento call or key.

## B5 AttentionCounter-HaikuMed (worker-medium, haiku)

Objective: the OpenAlex counts of spec section 3 D2 d, exactly as specified. No judgment, no scores, no terciles.
- The 18 underlyings and their phrases: spec section 9.1, copied exactly. Codes per underlying: crude oil MCL QM CL;
  natural gas MNG QG NG; gold MGC GC; silver SIL SI; copper MHG HG; euro M6E 6E; Australian dollar M6A 6A; bitcoin MBT
  BTC; ether MET ETH; Nasdaq-100 MNQ NQ; Russell 2000 M2K RTY; Dow MYM YM; US Treasuries 2YY 5YY 10Y 30Y ZT ZF ZN ZB;
  corn MZC XC ZC; soybeans MZS XK ZS; wheat MZW XW ZW; soybean oil MZL ZL; soybean meal MZM ZM.
- The search value per underlying: ("phrase 1" OR "phrase 2" ...) AND (intraday OR "intra-day" OR "high-frequency" OR
  "high frequency" OR microstructure). Request https://api.openalex.org/works?filter=title_and_abstract.search:<the
  URL-encoded value>&per-page=1 plus mailto=<OPENALEX_EMAIL, read from .env inside the script, never printed or logged>.
  Record meta.count.
- Diagnostic only: the phrase clause alone (without the AND clause), its meta.count.
- One call at a time, at least 0.6 s apart; at most 2 retries on an HTTP error (log each). If the API rejects the query
  syntax, log the error and stop: do not change the query.
- Log per call: the URL without the mailto parameter, HTTP status, meta.count, UTC and PDT times.
Output: briefs/F2_attention.json {"underlyings": {"<name>": {"codes", "query_value", "url_logged", "status", "count",
"phrase_only_count", "fetched_utc", "fetched_pdt", "retries"}}, "notes": []}; the script in briefs/work/ATTN/.
Boundaries: the OpenAlex API only; never print or write the email or any other .env value.

## B6 VolCoder-OpusXHigh (worker-xhigh, opus): F3

Objective: spec section 2 exactly (2.1 files, 2.2 sessions and grid, 2.3 statistics, 2.4 OC-1 transfer) for the 47
codes (and NQ as MNQ's transfer source), written to briefs/F3_vol.json (schema above) and briefs/F3_vol.md.
- Start from reports/stage_e28_briefs/work/A0/A0_stats.py and reports/stage_e28_briefs/A0_contract_stats.md (Method):
  copy what you need into briefs/work/F3/ and extend it there. Tick sizes from rules/products.py (read-only); codes
  missing there take E.28's A1_<family>.json tick fields, flagged. Which codes own standard-window bars: from the folder
  listing (E.28 found 22 candidates with owned window statistics).
- Guard: an allow-list on the resolved path (only data/vendor/databento/GLBX.MDP3/ohlcv-1m/<ROOT>_v_0/range=YYYY-MM-01_...
  files for the 12 months 2022-11 to 2023-10); refuse every other path, and any path containing mbo, mbp, tbbo, holdout,
  sealed or enc, before opening; log every open to briefs/work/F3/opens.log. Unit-test the guard.
- Before and after the run: the holdout status, the E.32 soy test-seal status and the guard33 dry-check, using the
  commands in briefs/checks.sh (its data.holdout, soy_test_seal.py and guard33.py lines), saved to
  briefs/work/F3/holdout_before.txt and holdout_after.txt.
- Unit tests on synthetic bars: D_h with overlapping starts; roll (instrument_id change) exclusion; the session cut; the
  17:00 CT trade-date rule; the OC and overnight definitions; R_d. Known quirk (E.21): the equity calendar books US
  holidays as trade dates; follow A0's handling and report the count of such dates per root.
- Regression: for at least 3 owned roots, compare with E.28's A0_contract_stats.json for every statistic both compute on
  the same window; report the differences and explain any above 1%.
- Run at nice 10, one process, resumable (one JSON part per root under briefs/work/F3/parts/), through flock on
  briefs/work/heavy.lock; check free -m first (A0's peak was about 170 MB).
- Volatility statistics only: no signed, conditional or autocorrelation statistic, nothing about strategies.
Output: briefs/F3_vol.json; briefs/F3_vol.md (method, number of files opened, a per-root table of sigma_5 to sigma_240,
OC, R_d, transfers, unknowns, the before and after guard lines); code, tests and logs in briefs/work/F3/.

## B7 ScoreCoder-OpusXHigh (worker-xhigh, opus)

Objective: the scoring scripts for spec sections 3, 4, 5 and 8.3, unit-tested on synthetic inputs, before any real fact
exists. Read spec sections 0 and 3 to 9 in full.
- briefs/work/score/SCHEMA.md: the exact input files and fields (extend the shared data contract above; you may add
  fields, never rename them), each field's spec clause and its unknown rule.
- briefs/work/score/score32b.py: D1 (r_5, r_15 and r_OC reported); D2 c and d (terciles by count, equal counts to the
  higher tier, a missing count 0.5 u); satellites' D2 a, b and c from the leader; D4 L, J and Sat (i, ii), plus the
  blind Sat (iii); D2 a and b, D3, D6 from the blind ratings; D5; the Layer 1 gates with the arithmetic string
  "sigma_60 = x ticks vs 2 x (S + 0.5) = y ticks"; L1. Layer 2: E from econ32b.json, R and A (blind), D, Rel (4 minus
  the blind deductions, floor 0), P (script), the Layer 2 gates, L2. S, the half-up 2-decimal ties and the tie-break
  chain, ranks, the full table, the top 15, the moves against E.28's v2 order (reports/stage_e28_briefs/
  A3_ranking_table.json, read-only; name the criteria that moved each pair). Every declared variant (slip0, slip1, mad,
  D1_all, E_dir60, OC1_off, sat1, D2_own, L1min2, spread1) and a hook for extra lead-ruling variants defined in a JSON
  file, each reporting its top 5 and the MNQ ranks. NQ is listed as "excluded (V49)", never scored or ranked.
- briefs/work/score/r3_score.py: spec 8.3: Q4, Q5, Q6 and Q7 by script from a combinations file (define its schema in
  SCHEMA.md: per combination the product or pool, venue, family, band members, h_c, c_f, sigma_hc, v, K_test, DLL,
  payout threshold, news-window flags, data costs and windows, Q1 to Q3 from the CombinationScorer), K_eff for pools,
  C, ties, and the R4 selection (top 5 distinct (product or pool, family) by best C, marked weak if C < 2.00).
- Both refuse to run unless the spec's sha256 is the one above.
- Tests: every band boundary (the boundary goes to the higher score), every unknown rule, both Layer 1 gates and the
  Layer 2 gates, the tie chain, each variant flipping only its one thing, the satellite logic, D2 d terciles with ties,
  K_eff. Run `uv run pytest -q briefs/work/score/` only (full path reports/stage_e32b_briefs/work/score/). Then a dry
  run on a small synthetic fixture -> briefs/work/score/fixture_out.json.
- Also a short briefs/work/score/README.md: how to run, and which spec clause each function implements. Do not run on
  real facts: they do not exist yet.

## B8 HoldingCoder-OpusXHigh (worker-xhigh, opus): F5 code

Objective: the script for spec section 7 (F5), unit-tested, plus the SR80 values, before real facts exist.
- SR80 from E.32 protocol P7.2 as implemented in reports/stage_e32_briefs/protocol/p7_final.py (read-only; import it or
  re-implement and cross-check against its own outputs): the true daily Sharpe that passes with probability 0.80 with
  the DSR at N = 838; discovery T = 796 (at G3 alone and at the binding G3 + G4), test T = 870. You may read the protocol
  text for P3.8 and P7.2 (grep under reports/stage_e32_briefs/protocol/) to understand G3 and G4. Write
  briefs/work/F5/SR80.json with the values, the formula and the cross-check.
- briefs/work/F5/f5_holding.py: per Layer 1 survivor (firm-independent rows) and per top-15 pair (firm rows), at h in
  {1, 2, 5, 15, 30, 60, 120, 240} minutes and OC, overnight rows apart: c_RT, c_f, k(h), g_be, g_1, the hit rate p
  (empirical m_h and the normal approximation), n_max, n_cap, trades per year, e80 (discovery and test), G(h),
  DLL_f / (sigma_h v), MLL_f / (sigma_h v), the flat-by-close time against the main session's end and the latest start
  of an h hold, overnight rules, news windows, pauses, the band B and the prior's verdict (holds, partly, fails), exactly
  as spec section 7 defines them. Inputs: F3_vol.json, F4_facts_unmasked.json, SR80.json, and a survivors-and-top-15
  file from the score run (define its schema in briefs/work/F5/SCHEMA.md).
- Tests on synthetic inputs: band-rule edge cases, each verdict case, the latest start against flat-by-close, an empty
  band. Refuse to run unless the spec hash matches. Output: code, tests, SR80.json, SCHEMA.md and README.md in
  briefs/work/F5/. Do not run on real facts.

## B12 EconSetup-OpusXHigh (worker-xhigh, opus): the economics code, prepared now, run in wave C

Objective: prepare E.28's economic model for spec section 4 E and prove it reproduces E.28.
- Copy the code of reports/stage_e28_briefs/work/A3_econ/ (*.py and A3_inputs.json; not logs or caches) to
  briefs/work/econ/; read reports/stage_e28_briefs/A3_econ.md sections 1 and 2 for the model.
- Changes: c_mkt = F_rt / v + S_rt with S_rt = the code's sourced spread S (1 tick where none is sourced); the grid from 0
  to max(4, ceil(0.30 sigma_60)) ticks at 0.01 (a coarser scan only if every threshold is then confirmed on the 0.01
  grid, as E.28's grid check did); outputs mu*_mkt and mu10K_mkt in ticks and in sigma_60 units, and the cost per
  attempt; the variant E_dir60 (T = min(20, floor(L_main / 60)), sigma_T = sigma_60); the variant spread1 (S = 1 for
  every code); E_dir at h = 30, 120 and 240 (T = min(20, floor(L_main / h)), sigma_T = sigma_h) for a given list of
  pairs. E.28's limit case is not used.
- Inputs: F3_vol.json and F4_facts_unmasked.json (contract above; follow work/score/SCHEMA.md once it exists); output
  briefs/econ32b.json (contract above).
- Regression: with E.28's own inputs (A3_inputs.json) and S = 1, reproduce E.28's mu*_mkt and mu10K_mkt (A3_econ.json)
  for every pair within one grid step; write the result to briefs/work/econ/REGRESSION.md.
- Time a run on a few pairs and estimate the full run's time and peak memory (briefs/work/econ/README.md). Runs go
  through flock on briefs/work/heavy.lock, at nice 10, at most os.cpu_count()//2 processes (never more than 8).
- Do not run on real facts yet.

## B9 ClosedLines-SonnetHigh (worker-high, sonnet): R1

Objective: spec section 8.1's inventory of closed lines, with sources, so that no recommendation re-tests one.
Extraction only: no judgment on what a new idea overlaps (the CombinationScorer and the lead do that).
- Sources: docs/DECISIONS.md (grep V38, V45, V49, V50, V56 and any later V entry that closes a line); docs/STAGES.md;
  reports/stage_e23_briefs/inventory_compact.txt and inventory/ (the 538 bar-based trials by family);
  ledger/trial_registrations.jsonl (10 registrations; N 538 -> 838 by r009-E33); reports/E.33c_RETURN.md sections 1 and
  7 (the ZM directional families: crush, cross-asset, order flow, own price path, pooled; 5 to 60 minutes);
  reports/E.31_RETURN.md section 1 (passive spread capture, V50).
- Per closed line: id (R1-nn), family or mechanism, products, horizons, bar size or data schema, windows read (dates),
  registration ids and trial counts, the closing decision (V number) with a verbatim quote and file:line, exceptions
  (V45), notes.
- Two lookup tables: by product (the 47 codes and the program's other roots) and by family or mechanism.
Output: briefs/R1_closed_lines.json and briefs/R1_closed_lines.md (at most about 250 lines). Read-only; no web.

## B10 IdeaFamilies-OpusHigh (worker-high, opus): R2 families (runs after ClosedLines and the family readers)

Objective: the directional idea families at horizons from 5 minutes to the session close (overnight holds reported
apart) that R2 combines with products and venues: mechanisms, evidence and data needs. Sourced facts only; no scores.
- Sources: reports/stage_e28_briefs/C2_*.md; reports/stage_e28_methods_brief.md and reports/stage_e32_methods_brief.md
  (large: grep headings and keywords, read by line ranges); reports/stage_e31_inputs/planner_research_notes.md and
  reports/stage_e32_inputs/planner_research_soy_complex.md (planner pointers: verify against cited full text before
  relying on them); the family readers' F2_<family>.json T3, T4, T6 and T7 items and the two shared files (cite item
  ids); briefs/R1_closed_lines.json (flag overlaps by R1 id).
- Consider at least: event drift (EIA for crude and natural gas, USDA for grains, macro releases for rates, gold and the
  equity indices); cross-market or spread reversion (crush, cracks, calendar spreads, mini or micro to full pairs,
  cross-asset pairs); session handoffs (the day-session open, regional opens and closes, the settlement window,
  fixings); market intraday momentum (Baltussen et al.); order-book state at longer horizons; and any other family the
  sources support.
- Per family: name; mechanism (whose flow, why predictable, why an edge could exist at retail size); applicable codes;
  horizons; evidence items (source, product, horizon, period, in or out of sample, net of costs, verified level); data
  needs (schema, history, event calendars); overlap with R1 (ids and how); open questions.
Output: briefs/R2_idea_families.json and briefs/R2_idea_families.md (at most about 300 lines). WebSearch budget 25,
only to verify a pointer's full text; pages under briefs/pages/IDEAS/ with log.tsv; helpers briefs/work/IDEAS/.

## B11 NonProp-SonnetHigh (worker-high, sonnet)

Objective: facts for the own-broker venue (IBKR, non-prop) for a British Columbia resident (Interactive Brokers Canada's
terms where they differ from IBKR LLC's).
- Futures commissions for CME products: tiered and fixed schedules plus exchange, clearing, NFA and regulatory fees, as
  all-in USD per contract per side, for the 47 codes where published (at least one product per family and every micro).
- Margins: intraday and overnight initial and maintenance margins for the 47 codes where published (with the page date).
- Market data: the monthly fee for real-time CME, CBOT, NYMEX and COMEX data for a non-professional (bundle names and
  prices).
- Account minimums and futures-permission requirements for a Canadian resident.
- The own-account capital ceiling recorded in docs/DECISIONS.md (grep: capital, ceiling, own account, IBKR, broker); if
  none is recorded, say so (the spec then uses USD 6,000, marked u).
- Reuse first: reports/stage_e13_briefs/pages/BrokerVenues/ and reports/stage_e12_briefs/margin_pages/ (saved pages;
  read by grep).
Output: briefs/F2_nonprop.json and briefs/F2_nonprop.md. Pages: briefs/pages/NONPROP/ with log.tsv; helpers:
briefs/work/NONPROP/. WebSearch budget 30. Public pages only; no login.
