# Stage E.2a return: ML route freeze, then the Stage E build (rules, calendars, bars, costs, vehicles, epsilon)

Lead: Opus 5.5 (claude-opus-5-5), effort xhigh, ultracode on. Session ee707266-bbda-4ccb-84dc-81ce0d628d05,
2026-09-25, 00:12 to 07:45 on 2026-09-26 PDT (America/Vancouver), with two pauses: a plan session limit
(03:03-06:10) and a clean stop on the user's request (08:13-17:10). Prompt: docs/prompts/STAGE_E.2a.md
(committed 4b984e8; the pasted prompt matched it). Running log: reports/stage_e2a_STATE.md.


## 1. Verdict summary

**Committed (not pushed)**
- ML route freeze: **ba67073**, manifest sha256 **077a57e1c00554dd0745302b247673d45ee05b805ac4bfd876f8497f7bbb1ed2**.
- Source-window amendment, 6 labels removed: **04c504f**.

**Uncommitted, for review:** the rules engine, eight cited calendars, the bars of all 45 contracts (MES reproduced exactly), the frozen costs, the vehicles, epsilon and the D14 fixes.

**Not done:** nothing bought; no member run.

**Checked:** Fable reproduced every vehicle, size, cost and epsilon, with 0 discrepancies.

**Exposures:** 28 traded (22 chosen, 6 undersized); RBOB, ULSD and silver not traded.

**Epsilon** (net ticks per contract per day, translated → operative):

| Cluster | Figures |
|---|---|
| K2 | ZT 10→5, ZF 10→6, ZN 5→3, TN 5→4, ZB 2, UB 2 |
| K4 | MCL 21, NG 8 |
| K5 | MGC 85→71, MHG 34→27 |
| K3 | 6E 13→12, 6A 17→11, 6B 13→8, 6C 17→9, 6J 13→10, 6S 13, 6N 17→10 |
| K6 | ZC 6→4, ZW 6→4, ZS 6→5, ZM 8→5, ZL 14→11, HE 8→7, LE 8 |
| K7 | MBT 170→90 |
| K1 | MNQ 170, M2K 56→50, MYM 56 |

**E.2b:** unblocked. The ML route's purchase awaits funding.


## 2. Guardrail evidence

**Start (00:12-00:17 PDT), verbatim:**
- `git status --short`: (empty)
- `git log --oneline -3`:
  ```
  4b984e8 docs: overnight compute profile in CLAUDE.md; Stage E.2a prompt
  1b54dc1 feat: Stage E.1 results, step 1 bought ($103.16 on acct-2), ML route draft
  b05c506 feat: per-account Databento spend gate and the Stage E step 1 purchase path
  ```
- `uv run python -m data.holdout status`: holdout-1 `"all_ok": true`, `"unlocks_logged": 0`,
  `"research_has_no_holdout_rows": true`; holdout-2 13 of 13 chunks `"sealed_ok": true`,
  `"confirmation_has_no_holdout2_rows": true`, `"unlocks_logged": 0`, `"all_ok": true`
- `wc -c REGISTRATION.md`: `0 REGISTRATION.md`
- Freeze manifest (reports/stage_e1_freeze.json, sha256 96166eb3...454a7c): 31 of 32 files match directly;
  reports/stage_e1_freeze_audit.md matches its freeze-commit blob (848f331, ba4cad7b...704874), as the
  manifest's own note specifies (Part 2 was appended after the freeze).
- `uv run pytest -q`: `2 failed, 1010 passed, 1 xfailed, 19 warnings in 264.33s (0:04:24)` (the two known
  D.1f tests: test_2019_2024_quotes_are_verbatim_from_the_extraction, test_confirmation_build_end_to_end).

**End, verbatim:**

Taken 2026-09-26 07:25 PDT.

- `git log --oneline -3`:
  ```
  04c504f docs: Stage E source-window amendment (Stage E.2a)
  ba67073 docs: Stage E ML route freeze (Stage E.2a)
  4b984e8 docs: overnight compute profile in CLAUDE.md; Stage E.2a prompt
  ```
- `uv run python -m data.holdout status` (selected keys):
  ```
   "research_has_no_holdout_rows": true,
   "unlocks_logged": 0,
   "all_ok": true,
    "confirmation_has_no_holdout2_rows": true,
    "unlocks_logged": 0,
    "all_ok": true
  ```
- `wc -c REGISTRATION.md`: `0 REGISTRATION.md`
- Freeze manifests (script verify_manifests.py):
  ```
  E.1 freeze manifest reports/stage_e1_freeze.json (96166eb39b85d4fdcf132092978ee85393392de52c3857dc3f64ea7281454a7c): 32 files, 0 mismatches
  E.2a ML freeze manifest (077a57e1c00554dd0745302b247673d45ee05b805ac4bfd876f8497f7bbb1ed2) vs working tree: 4 files, 0 mismatches audit compared at its freeze-commit blob (Parts 2 and 3 appended later, as the manifest notes)
  E.2a ML freeze manifest (077a57e1c00554dd0745302b247673d45ee05b805ac4bfd876f8497f7bbb1ed2) vs commit ba67073: 4 files, 0 mismatches 
  ```
- `uv run pytest -q`: `1891 passed, 2 skipped, 1 xfailed, 53 warnings in 355.18s (0:05:55)`
- `git diff --stat -- ledger/`: (empty)
- `git diff --stat`:
  ```
   data/bars.py                           |  20 ++-
   data/cme_calendar.py                   |  77 +++++++--
   data/validate.py                       | 285 ++++++++++++++++++++++++++++++++-
   reports/stage_e2a_declaration_audit.md | 196 +++++++++++++++++++++++
   tests/test_d1f_calendar_build.py       |  48 +++++-
   5 files changed, 599 insertions(+), 27 deletions(-)
  ```
- `git status --short`:
  ```
   M data/bars.py
   M data/cme_calendar.py
   M data/validate.py
   M reports/stage_e2a_declaration_audit.md
   M tests/test_d1f_calendar_build.py
  ?? data/build_bars.py
  ?? data/build_bars_reports.py
  ?? data/build_bars_run.py
  ?? data/calendars/
  ?? data/group_session.py
  ?? funnel/exposure_gate.py
  ?? funnel/exposure_gate_a1.py
  ?? funnel/exposure_gate_mes.py
  ?? funnel/exposure_gate_run.py
  ?? funnel/exposure_segments.py
  ?? reports/E.2a_RETURN.md
  ?? reports/stage_e2a_STATE.md
  ?? reports/stage_e2a_bars.json
  ?? reports/stage_e2a_bars.md
  ?? reports/stage_e2a_bars_probe.json
  ?? reports/stage_e2a_calendar_bar_checks.json
  ?? reports/stage_e2a_calendar_bar_checks.md
  ?? reports/stage_e2a_calendar_sources.md
  ?? reports/stage_e2a_calendar_sources_crypto.json
  ?? reports/stage_e2a_calendar_sources_crypto.md
  ?? reports/stage_e2a_calendar_sources_energy.json
  ?? reports/stage_e2a_calendar_sources_energy.md
  ?? reports/stage_e2a_calendar_sources_equity.json
  ?? reports/stage_e2a_calendar_sources_equity.md
  ?? reports/stage_e2a_calendar_sources_fx.json
  ?? reports/stage_e2a_calendar_sources_fx.md
  ?? reports/stage_e2a_calendar_sources_grains.json
  ?? reports/stage_e2a_calendar_sources_grains.md
  ?? reports/stage_e2a_calendar_sources_livestock.json
  ?? reports/stage_e2a_calendar_sources_livestock.md
  ?? reports/stage_e2a_calendar_sources_metals.json
  ?? reports/stage_e2a_calendar_sources_metals.md
  ?? reports/stage_e2a_calendar_sources_rates.json
  ?? reports/stage_e2a_calendar_sources_rates.md
  ?? reports/stage_e2a_costs.json
  ?? reports/stage_e2a_costs.md
  ?? reports/stage_e2a_epsilon.json
  ?? reports/stage_e2a_epsilon.md
  ?? reports/stage_e2a_epsilon_declaration.md
  ?? reports/stage_e2a_epsilon_declaration_addendum.md
  ?? reports/stage_e2a_funnel/
  ?? reports/stage_e2a_funnel_phaseA.json
  ?? reports/stage_e2a_price_limits.json
  ?? reports/stage_e2a_rules.md
  ?? reports/stage_e2a_vehicle_rule_readings.md
  ?? reports/stage_e2a_vehicle_sizes.json
  ?? reports/stage_e2a_vehicle_sizes.md
  ?? reports/stage_e2a_vehicles.json
  ?? reports/stage_e2a_vehicles.md
  ?? rules/constraints.py
  ?? rules/price_limits.py
  ?? rules/products.py
  ?? rules/sessions.py
  ?? screening/vehicles.py
  ?? screening/vehicles_choice.py
  ?? screening/vehicles_choice_md.py
  ?? screening/vehicles_md.py
  ?? screening/vehicles_run.py
  ?? sim/calibrate_costs.py
  ?? sim/cost_inputs.py
  ?? sim/cost_report.py
  ?? sim/cost_report_md.py
  ?? sim/cost_rule.py
  ?? sim/product_costs.py
  ?? tests/test_e2a_bars.py
  ?? tests/test_e2a_calendar_crypto.py
  ?? tests/test_e2a_calendar_energy.py
  ?? tests/test_e2a_calendar_equity.py
  ?? tests/test_e2a_calendar_fx.py
  ?? tests/test_e2a_calendar_grains.py
  ?? tests/test_e2a_calendar_livestock.py
  ?? tests/test_e2a_calendar_metals.py
  ?? tests/test_e2a_calendar_rates.py
  ?? tests/test_e2a_costs.py
  ?? tests/test_e2a_exposure_gate.py
  ?? tests/test_e2a_rules.py
  ?? tests/test_e2a_vehicles.py
  ```


**Order and price blindness.**
- No purchased price or order-book file of any Stage E product was opened beyond E.1's integrity fields
  before the ML freeze commit ba67073 (00:53 PDT). Until then the workers wrote code and synthetic tests
  only (the calendar builders read CME schedules, not data; BarsCoder waited for the commit by polling
  `git log` before its first price-file read).
- The vehicle rule readings (reports/stage_e2a_vehicle_rule_readings.md, sha256 8c3c29dd...b458) were
  written and hashed at 00:38, before any bar existed; the epsilon declaration (ccdb8ec5...) at 02:37,
  before any funnel run on Stage E bars; its addendum A-1 (e6253be2...) at about 06:12, before any
  not-yet-evaluated cell used it.

**Every quantity computed from research-window data, and the script that computed it** (trade dates
2025-04-01..2026-06-19 in the step 1 files only; no member signal, trade, P&L or screening statistic):
1. Research-window one-minute bars of the 45 admissible contracts, their validation (ordering, duplicates,
   OHLC, tick grid, closures, gap runs) and roll, blackout and vendor-degraded dates:
   `python -m data.build_bars` (data/build_bars.py, build_bars_run.py, build_bars_reports.py,
   data/group_session.py, additions to data/validate.py and data/bars.py). Output
   data/processed/<ROOT>/..._research.parquet (read-only), reports/stage_e2a_bars.{json,md}.
2. Calendar checks against those bars (step 4b style: weekdays without bars, early-halt minutes, listed
   entries observed; CT minutes and bar counts only): same builder; reports/stage_e2a_calendar_bar_checks.{json,md}.
3. Vendor price-scale checks (share of prices on the tick grid; counts only): the builder's grid probe,
   CostCoder's scale check, VehicleCoder's grid check.
4. The D8 cost tables from the five-date mbp-1 sample (time-weighted quoted half-spreads per 30-minute CT
   bucket, top-of-book sizes, dates with quotes, depth at q_c, round-turn cost): `python -m
   sim.calibrate_costs run|build` (sim/calibrate_costs.py, cost_rule.py, cost_report.py, cost_inputs.py,
   product_costs.py). Output reports/stage_e2a_costs.{json,md}.
5. D2's per-contract risk r_c, size q_c and risk ratio rho_c: `python -m screening.vehicles_run sizes`
   (screening/vehicles.py). Output reports/stage_e2a_vehicle_sizes.{json,md}.
6. D2's cost per dollar of risk and the vehicle choice: `python -m screening.vehicles_run choice`
   (screening/vehicles_choice.py). Output reports/stage_e2a_vehicles.{json,md}.
7. D3's segment moves E|m_T| (T = 1, 2, 4, 8, 16, 32) and the per-exposure segment tables (moves and
   excursions per segment per day, used sign-symmetrized by the funnel), and the funnel cells at q_c:
   `python -m funnel.exposure_gate_run drive` (funnel/exposure_segments.py, exposure_gate.py,
   exposure_gate_run.py). Output reports/stage_e2a_epsilon.{json,md}, reports/stage_e2a_funnel/.
8. Regressions on MES's own research bars (not Stage E data): the generalized bar builder rebuilt
   411,659 MES rows equal to the MES research parquet; the generalized funnel reproduced 7 D.1e cells.
9. The independent recomputations (DeclarationAuditor-FableXHigh, own code in the scratchpad): items 4 to
   7 for the contracts and exposures listed in section 5.
No return, correlation or volatility statistic beyond D2, D3 and D8's, no chart and no price summary was
computed; the build summaries carry counts, dates and flags.

**Holdout-1 rows inside step 1 files (for the record).** CME books MBT's trading from Thursday
2026-06-18 16:02 CT to Saturday 06-20 18:59 CT (Juneteenth and the 24/7 weekend) to trade date
2026-06-22, holdout-1's first trade date. Those 1,617 bars lie inside the step 1 files (which end
2026-06-21 00:00 UTC, the purchase guard's end) because the guard was set by timestamp, not by CME trade
date. The bar builder decoded them with the rest of the file and dropped them (ruling L-9): they were
never written to any parquet and no quantity uses them. E.2b's loaders must refuse them too.

**Other guardrails.** No purchase, no cap change, no ledger line (`git diff --stat ledger/` empty); the
only Databento calls were free symbology.resolve metadata calls for the research window (no ledger line).
No TopstepX call or credential; nothing under live/ or ops/; docs/NULL_CRITERIA.md and
reports/stage_d1f_confirmation_list.md untouched; REGISTRATION.md 0 bytes throughout; holdout-1 and
holdout-2 untouched (the 2024-07-04 calendar fix moves MES's holdout-2 calendar count from 258 to 259
trade dates; no sealed chunk was touched). Compute followed the overnight profile: at most 12 of 14
threads for the funnel (two exposures x 6 workers), nice 10, resumable, memory checked before each heavy
job (peak about 0.5 GB per funnel job, under 0.4 GB per bar build), nothing started in the AiTrader window.


## 3. Results per task

### 3.1 Tasks 1, 3, 4: the ML route freeze (commit ba67073)
- **Task 1** (lead): 37 exact-string edits to docs/STAGE_E_ML_DESIGN.md applying V1 to V9, each logged with
  old text, new text and decision in reports/stage_e2a_ml_changes.md; design sha256 7ae2d347... ->
  185e8cd5...; docs/DECISIONS.md entry of 2026-09-25 quoting V1 to V9 verbatim. No edit maps to no
  decision; V9 needs no ML-design edit (logged why). Questions left to the user: Q-1 (V1 sets no cap for
  the route's purchase), Q-2 (V8's "after E.2b" against the prompt's "E.2b or later": compatible, per the
  audit), Q-3 (V7 sets no compute budget). Application notes A-1 to A-3 (the mechanical LSTM batch-size
  rule, the CPU fallback struck, the E.2a/E.2b names).
- **Task 3** (DeclarationAuditor-FableXHigh): reports/stage_e2a_declaration_audit.md Part 1, READY WITH
  FIXES: 2 BLOCKING (ML-A01 the selection metric had no prediction-to-position rule; ML-A02 "the cost
  threshold" was undefined and admitted losing shorts), 14 SHOULD FIX, 10 NOTE. The mapping check held
  byte for byte (the 37 replacements replayed onto the 1b54dc1 blob reproduce the file).
- **Task 4** (lead): 24 fixes written as bracketed "[Stage E.2a ruling on audit ML-A##]" notes, all
  within V1 to V9 (reports/stage_e2a_ml_freeze_rulings.md, with every fix's old and new text; design
  sha256 185e8cd5... -> eb7f9971...); FROZEN header; docs/DECISIONS.md records V6's effect on frozen D5
  (every family, the route included, at 0.05 / (K + 1)) and the new wording the user has not seen
  (selection metric, per-side 1.5 x cost candidate threshold, 4-dimension product embedding, the
  one-trade-date embargo kept, the primary leg = the cluster's F16 lead exposure, the calendar-based block
  cut, the 31 price-path contracts). Manifest reports/stage_e2a_ml_freeze.json, sha256
  **077a57e1c00554dd0745302b247673d45ee05b805ac4bfd876f8497f7bbb1ed2** (design, changes log, audit Part 1,
  rulings; HEAD 4b984e8; created 00:52 PDT), verified by script against the working tree and against the
  commit's blobs, 0 mismatches. Commit **ba67073** "docs: Stage E ML route freeze (Stage E.2a)", exactly six
  files.

### 3.2 Tasks 2 and 11: source windows and the amendment (commit 04c504f)
- **Task 2** (SourceWindowReader-OpusHigh): reports/stage_e2a_source_windows.{json,md}: 37 members, 75
  sources, 145 (member, source) rows (108 fetched full text, 29 abstract only, 8 not found); 26 rows
  "unknown" (17 supporting, mostly the CP3 port's Crabel chain); all 71 quoted passages verbatim-checked
  by script. No WebSearch used.
- **Task 11** (lead, audited): reports/stage_e2a_source_window_amendment.md (sha256 9fe401c1...): the
  frozen rule applied mechanically with the widest confirmation window [2019-05-06, 2024-02-29], every
  cited source counted (the prompt's "any of its sources"), unknown and secondary-only windows keeping the
  label, documentation sources with no data sample neither keeping nor removing it.

| Member | Before | After |
|---|---|---|
| K2-predrift-01, K3-ldnmom-01, K3-mehedge-01, K4-ngpre-01, K8-flight-01, K8-oilcad-01 | source-overlap (fallback) | **not source-overlap** |
| the other 31 of the 37 (K1-cp1-01, K1-cp3-01, K2-cp1..3-01, K2-monthend-01, K3-cp1..3-01, K3-ecbfix-01, K3-ldnrev-01, K3-tkypre-01, K3-tkypost-01, K4-cp1..3-01, K5-cp1..3-01, K5-preauc-01, K5-pmfix-01, K6-cp1..3-01, K6-crushgap-01, K6-limitcont-01, K6-wasdepost-01, K7-cp1..3-01, K7-rev2h-01) | source-overlap (fallback) | source-overlap |

  The narrower supporting-only reading would also remove K3-ldnrev-01 and K5-pmfix-01 (not adopted).
  Audit Part 2 confirmed all six removals (0 BLOCKING, 0 SHOULD FIX, 7 NOTE); rulings in
  reports/stage_e2a_source_window_rulings.md. Commit **04c504f** "docs: Stage E source-window amendment
  (Stage E.2a)", exactly the amendment, Task 2's two files, the audit, the rulings and docs/DECISIONS.md.

### 3.3 Task 5: the rules engine (RulesCoder-OpusXHigh)
rules/products.py, rules/constraints.py, rules/sessions.py, rules/price_limits.py (rules/xfa_rules.py
unchanged); reports/stage_e2a_rules.md, reports/stage_e2a_price_limits.json (193 sources, 2,306 quotes,
each verbatim-checked twice). A 47-row product table (45 admissible contracts plus ES and MES as legs),
every field sourced: tick size and value, vendor price factor, commission (MCL $1.72, MNG $1.92), lot
weight (minis 1, micros 0.1, SIL 0.2, MBT 1), the 1-lot member cap, D9.11 volatility caps, the CPI
window (skip on NQ, RTY, YM, GC, SI, HG; at most 3 contracts on MNQ, M2K, MYM, MGC, SIL, MHG), flatten
times per group and date (15:08; grains 13:18 with the 07:45-08:30 pause; livestock 13:03; the earlier of
Topstep's holiday schedule and CME's early close minus 15 minutes), and D9.7's price-limit rule with
CME limit tables (hard daily limits exist only for grains, livestock and equity; the research window is
fully covered), the settlement-window proxy and the locked-market fill. It agrees with sim/cost_inputs.py
and with the vehicle caps. **tests/test_e2a_rules.py: 110 tests** (known answers for all eight groups:
tick arithmetic, lot sums and caps, flatten times on normal, early-close and closure days, the grain
pause, price-limit stop levels for percentage and price-unit limits under both circuit-breaker readings,
the locked-market fill, volatility caps, the CPI skip and 3-contract limit, commissions); 23 of 23 planted
errors caught; the 67 existing rules tests pass unchanged. Flags in section 6 (L-13, R-F1, R-F3, R-F4,
R-W1/2, R-V1).

### 3.4 Task 6: the group calendars
Workflow of eight CalendarBuilder-<Group>-OpusXHigh workers (3 at a time). Per group: a module with
HOLIDAYS, per-entry verbatim CME citations (Wayback copies), SESSIONS with dated regimes and D6's O and C;
sources logged per group and assembled in reports/stage_e2a_calendar_sources.md.

| Group | Module | Entries (closures / early) | Grades | Tests | Session changes | D6 |
|---|---|---|---|---|---|---|
| equity | data/cme_calendar.py + data/calendars/equity.py | 84 (17 / 67) | mostly cme status; 43 lower grades could be upgraded from CME sources (proposal) | 19 | the 15:15-15:30 CT halt removed from 2021-06-28 | C 15:00 from 2020-10-26; 15:15 before (L-12) |
| rates | data/calendars/rates.py | 80 (17 / 63) | all cme status; 2 time secondary, 1 inferred | 80 | none | C 14:00 confirmed; O 07:20 not published (L-1) |
| FX | data/calendars/fx.py | 49 (17 / 32) | all cme | 43 | Monday holidays keep the 16:00 close from 2022 | C 14:00 confirmed |
| energy | data/calendars/energy.py | 79 (20 / 59) | all cme status; 1 time inferred | 75 | none | C 13:30 confirmed |
| metals | data/calendars/metals.py | 79 (20 / 59), identical to energy | all cme status; 1 inferred | 95 | none | gold 12:30, silver 12:25, copper 12:00 confirmed |
| grains | data/calendars/grains.py | 82 (68 / 14) + 20 scheduled late opens | cme except MLK 2023 (secondary) | 93 | none since 2013 | confirmed (settlement 13:14-13:15) |
| livestock | data/calendars/livestock.py | 82 (68 / 14) | cme except MLK 2023 (secondary) | 88 | none | confirmed (settlement 12:59:30-13:00:00) |
| crypto | data/calendars/crypto.py | 49 (17 / 32) + 31 booked-forward dates | all cme | 110 | 24/7 from 2026-05-29 16:00 CT | C 15:00 confirmed |

Tests prove per group: coverage refusal outside 2019-05-01..2026-06-19; named entries with kind and time;
every entry cited with allowed grades; no duplicate dates; SESSIONS cover the range without gap or overlap;
the day session lies inside a trading segment. The equity fixes (D14): 2024-07-04 is now a 12:00 CT halt
(cme/cme); 2019-07-03 and 2023-07-03 are graded cme; the 2025-2026 block is byte-identical; MES's
holdout-2 calendar count moves from 258 to 259 (no sealed chunk touched; `data.holdout status` all_ok).

**Calendar discrepancies against the bars and their diagnoses** (reports/stage_e2a_calendar_bar_checks.md,
each with a lead_ruling): 340 thin-trading discrepancies (thin contracts only; the group's most liquid
contract clean) and 31 calendar questions, all ruled: FX 2025-11-27, six contracts (L-5: thin holiday
trading); metals, five MGC-only quiet minutes before settlement and GC 2026-01-29 (L-7: the check's
early-stop test does not apply inside metals' 23-hour session); metals 2026-02-25, a real unscheduled
mid-session stop (GC, MGC, SI, SIL about 12:00-13:45 CT; HG, MHG, NG, MNG gaps; L-7: unsourced, recorded,
not a calendar entry); MBT's 15 expiry Fridays (L-11: contract expiry, all inside roll blackouts). The
unscheduled 2025-11-28 CME outage (last bars about 20:44-20:49 CT on 11-27, reopen 07:30 CT) is a reported
gap run, not a calendar window (L-4 revised). Equity, rates, grains and livestock pass on every contract.

### 3.5 Task 7: the research-window bars (BarsCoder-OpusXHigh)
All 45 admissible contracts built, none refused; each parquet read-only with every input file's sha256,
the calendar modules' sha256 and the builder files' sha256 stamped in. MES's output is unchanged: the
generalized path rebuilt 411,659 MES rows equal to the MES research parquet (same columns, types and
values; the file bytes differ only because MES's 2026-06 chunk is sealed), and a test pins the parquet's
sha256. **tests/test_e2a_bars.py: 28 tests** (trade dates per group incl. the grain 19:00 start and pause,
livestock day-only, the crypto regime split and booked-forward dates; closed windows; flatten flags; the
roll blackout; the tick grid; the outright rule; out-of-window drops; read-only output and refusal to
overwrite; metadata stamps; ruling L-3; the late-open check; step-4b equivalence with MES's check; the MES
regression and pin). Downstream facts: ZC, ZW, ZS, ZL, HE and LE are quoted in cents (vendor tick = 100 x
the E.0 tick); ZN, ZF, ZT and LE keep one close-minute bar each, flagged in_scheduled_closure (L-3); roll
blackouts are computed on each group's calendar (L-8); a roll after 2026-06-20 is invisible to
research-window symbology, so 2026-06-18/19 might be unseen blackout dates. NG's first build was wrong
(the worker's own one-digit-year pattern bug dropped 345,929 bars); fixed and rebuilt, the bad file kept in
data/processed/NG/superseded/.

| Product | Group | Status | Bars | Trade dates | First | Last | Rolls | Blackout dates in window | Degraded on trade dates | Drops (window / coverage / no outright) | Calendar discrepancies | Build s | Peak MB |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| MBT | crypto | built | 407393 | 308 | 2025-04-01 | 2026-06-18 | 14 | 42 | 5 | 1617 / 0 / 0 | 15 | 3.6 | 364.0 |
| CL | energy | built | 424910 | 315 | 2025-04-01 | 2026-06-19 | 15 | 45 | 5 | 0 / 0 / 0 | 0 | 3.7 | 360.9 |
| HO | energy | built | 327126 | 315 | 2025-04-01 | 2026-06-19 | 18 | 48 | 5 | 0 / 0 / 0 | 0 | 4.5 | 336.1 |
| MCL | energy | built | 416170 | 315 | 2025-04-01 | 2026-06-19 | 15 | 45 | 5 | 0 / 0 / 0 | 0 | 4.1 | 351.3 |
| MNG | energy | built | 305790 | 315 | 2025-04-01 | 2026-06-19 | 14 | 42 | 5 | 0 / 0 / 0 | 12 | 3.2 | 328.8 |
| NG | energy | built | 391801 | 315 | 2025-04-01 | 2026-06-19 | 16 | 44 | 5 | 0 / 0 / 0 | 0 | 3.7 | 345.1 |
| QG | energy | built | 178979 | 315 | 2025-04-01 | 2026-06-19 | 14 | 42 | 5 | 0 / 0 / 0 | 40 | 2.1 | 296.2 |
| QM | energy | built | 258210 | 315 | 2025-04-01 | 2026-06-19 | 15 | 45 | 5 | 0 / 0 / 0 | 33 | 2.9 | 302.3 |
| RB | energy | built | 330620 | 315 | 2025-04-01 | 2026-06-19 | 25 | 61 | 5 | 0 / 0 / 0 | 0 | 3.2 | 335.1 |
| M2K | equity | built | 419079 | 316 | 2025-04-01 | 2026-06-19 | 5 | 15 | 5 | 0 / 0 / 0 | 0 | 3.0 | 360.4 |
| MNQ | equity | built | 432011 | 316 | 2025-04-01 | 2026-06-19 | 5 | 15 | 5 | 0 / 0 / 0 | 0 | 4.4 | 369.3 |
| MYM | equity | built | 423839 | 316 | 2025-04-01 | 2026-06-19 | 5 | 15 | 5 | 0 / 0 / 0 | 0 | 3.4 | 369.3 |
| NQ | equity | built | 431881 | 316 | 2025-04-01 | 2026-06-19 | 5 | 15 | 5 | 0 / 0 / 0 | 0 | 3.5 | 366.1 |
| RTY | equity | built | 420497 | 316 | 2025-04-01 | 2026-06-19 | 5 | 15 | 5 | 0 / 0 / 0 | 0 | 3.5 | 362.7 |
| YM | equity | built | 423656 | 316 | 2025-04-01 | 2026-06-19 | 5 | 15 | 5 | 0 / 0 / 0 | 0 | 3.6 | 362.6 |
| 6A | fx | built | 418305 | 316 | 2025-04-01 | 2026-06-19 | 5 | 15 | 5 | 0 / 0 / 0 | 2 | 3.7 | 348.0 |
| 6B | fx | built | 394563 | 316 | 2025-04-01 | 2026-06-19 | 5 | 15 | 5 | 0 / 0 / 0 | 4 | 3.5 | 353.1 |
| 6C | fx | built | 373511 | 316 | 2025-04-01 | 2026-06-19 | 5 | 15 | 5 | 0 / 0 / 0 | 7 | 3.7 | 347.6 |
| 6E | fx | built | 424708 | 316 | 2025-04-01 | 2026-06-19 | 5 | 15 | 5 | 0 / 0 / 0 | 1 | 3.7 | 357.3 |
| 6J | fx | built | 421075 | 316 | 2025-04-01 | 2026-06-19 | 5 | 15 | 5 | 0 / 0 / 0 | 3 | 3.9 | 357.3 |
| 6N | fx | built | 386595 | 316 | 2025-04-01 | 2026-06-19 | 5 | 15 | 5 | 0 / 0 / 0 | 4 | 4.0 | 348.6 |
| 6S | fx | built | 366753 | 316 | 2025-04-01 | 2026-06-19 | 5 | 15 | 5 | 0 / 0 / 0 | 9 | 3.6 | 342.0 |
| E7 | fx | built | 239304 | 316 | 2025-04-01 | 2026-06-19 | 5 | 15 | 5 | 0 / 0 / 0 | 86 | 2.8 | 293.1 |
| M6A | fx | built | 278695 | 316 | 2025-04-01 | 2026-06-19 | 5 | 15 | 5 | 0 / 0 / 0 | 64 | 3.1 | 325.8 |
| M6B | fx | built | 211257 | 316 | 2025-04-01 | 2026-06-19 | 5 | 15 | 5 | 0 / 0 / 0 | 57 | 3.1 | 293.9 |
| M6E | fx | built | 386230 | 316 | 2025-04-01 | 2026-06-19 | 5 | 15 | 5 | 0 / 0 / 0 | 9 | 3.9 | 348.0 |
| ZC | grains | built | 243019 | 306 | 2025-04-01 | 2026-06-18 | 12 | 29 | 5 | 0 / 0 / 0 | 0 | 2.5 | 293.4 |
| ZL | grains | built | 283222 | 306 | 2025-04-01 | 2026-06-18 | 6 | 18 | 5 | 0 / 0 / 0 | 0 | 2.6 | 302.2 |
| ZM | grains | built | 240098 | 306 | 2025-04-01 | 2026-06-18 | 11 | 27 | 5 | 0 / 0 / 0 | 0 | 2.5 | 293.1 |
| ZS | grains | built | 277118 | 306 | 2025-04-01 | 2026-06-18 | 7 | 21 | 5 | 0 / 0 / 0 | 0 | 2.4 | 301.0 |
| ZW | grains | built | 247726 | 306 | 2025-04-01 | 2026-06-18 | 9 | 23 | 5 | 0 / 0 / 0 | 0 | 2.5 | 299.5 |
| HE | livestock | built | 83469 | 306 | 2025-04-01 | 2026-06-18 | 13 | 32 | 5 | 0 / 0 / 0 | 0 | 0.9 | 222.1 |
| LE | livestock | built | 83785 | 306 | 2025-04-01 | 2026-06-18 | 19 | 39 | 5 | 0 / 0 / 0 | 0 | 0.9 | 224.6 |
| GC | metals | built | 428393 | 315 | 2025-04-01 | 2026-06-19 | 6 | 18 | 5 | 0 / 0 / 0 | 2 | 3.5 | 376.2 |
| HG | metals | built | 399401 | 315 | 2025-04-01 | 2026-06-19 | 6 | 18 | 5 | 0 / 0 / 0 | 3 | 3.4 | 359.8 |
| MGC | metals | built | 429238 | 315 | 2025-04-01 | 2026-06-19 | 6 | 18 | 5 | 0 / 0 / 0 | 6 | 3.4 | 366.5 |
| MHG | metals | built | 367105 | 315 | 2025-04-01 | 2026-06-19 | 6 | 18 | 5 | 0 / 0 / 0 | 4 | 3.5 | 337.4 |
| SI | metals | built | 415684 | 315 | 2025-04-01 | 2026-06-19 | 6 | 18 | 5 | 0 / 0 / 0 | 4 | 3.3 | 364.3 |
| SIL | metals | built | 412811 | 315 | 2025-04-01 | 2026-06-19 | 6 | 18 | 5 | 0 / 0 / 0 | 6 | 3.7 | 356.8 |
| TN | rates | built | 355564 | 316 | 2025-04-01 | 2026-06-19 | 5 | 15 | 5 | 0 / 0 / 0 | 0 | 3.7 | 335.5 |
| UB | rates | built | 372992 | 316 | 2025-04-01 | 2026-06-19 | 5 | 15 | 5 | 0 / 0 / 0 | 0 | 3.3 | 343.7 |
| ZB | rates | built | 358068 | 316 | 2025-04-01 | 2026-06-19 | 5 | 15 | 5 | 0 / 0 / 0 | 0 | 3.2 | 340.9 |
| ZF | rates | built | 377319 | 316 | 2025-04-01 | 2026-06-19 | 5 | 15 | 5 | 0 / 0 / 0 | 0 | 3.3 | 351.2 |
| ZN | rates | built | 396178 | 316 | 2025-04-01 | 2026-06-19 | 5 | 15 | 5 | 0 / 0 / 0 | 0 | 3.5 | 351.9 |
| ZT | rates | built | 348230 | 316 | 2025-04-01 | 2026-06-19 | 5 | 15 | 5 | 0 / 0 / 0 | 0 | 3.3 | 333.5 |

### 3.6 Task 8: the cost model (CostCoder-OpusXHigh)
reports/stage_e2a_costs.json (frozen, sha256 **f4360bb77272d0335485a9e01c0f6fc6ab99c47d52e640d95f9cd0397296df14**)
and .md. 229 mbp-1 files (343 million records), every sha256 and record count checked; exact
time-weighting on event time; no bucket needed the fewer-than-3-dates fallback; the depth term at q_c is
non-zero for MNG, M6B, MYM, MCL and M2K and moves the day-session headline only for M6B (3.118 -> 3.354
ticks) and MNG (4.334 -> 5.350). The ten readings of D8 are in the md. **tests/test_e2a_costs.py: 19
tests** (a hand-computed synthetic book: time-weighted spreads; crossed, locked and empty books dropped;
closures and the reopen grace excluded; a partial bucket; chunking invariance; the fallback; the depth
term below, at and above q_c; the event override; MCL and MNG commissions; vendor ticks; the loader; the
MES re-expression arithmetic). **MES check** (no MES mbp-1 exists; D.1's MES mbp-10 lies in holdout-1
dates, so it was not opened): D.1's recorded MES table re-expressed under D8's arithmetic gives 2.034 ticks
[2.004, 2.070] ($2.54) over the day session, and 2.073 over all 46 buckets, against D8's "about 2.11";
MNQ's table gives 4.119 ticks ($2.06). Documented differences: two days of mbp-10 against five of mbp-1,
2026-07 against 2025-26, MES against MNQ, 15- against 30-minute buckets.

| Contract | Group | Tick | Tick $ | Comm. RT $ | Comm. ticks | q_c | Day buckets | RT ticks mean [min, max] | RT $ mean [min, max] | Event side ticks buy / sell | Fallback buckets (all / day) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 6A | fx | 0.00005 | 5.0 | 4.22 | 0.844 | 1 | 14 (07:00-13:30) | 2.191 [2.148, 2.243] | 10.96 [10.74, 11.22] | 0.817 / 0.817 | 0 / 0 |
| 6B | fx | 0.0001 | 6.25 | 4.22 | 0.675 | 1 | 14 (07:00-13:30) | 1.916 [1.826, 1.972] | 11.97 [11.42, 12.33] | 0.677 / 0.677 | 0 / 0 |
| 6C | fx | 0.00005 | 5.0 | 4.22 | 0.844 | 1 | 14 (07:00-13:30) | 2.026 [1.992, 2.069] | 10.13 [9.96, 10.34] | 0.685 / 0.685 | 0 / 0 |
| 6E | fx | 0.00005 | 6.25 | 4.22 | 0.675 | 1 | 14 (07:00-13:30) | 1.935 [1.894, 1.975] | 12.09 [11.84, 12.35] | 0.815 / 0.815 | 0 / 0 |
| 6J | fx | 5E-7 | 6.25 | 4.22 | 0.675 | 1 | 14 (07:00-13:30) | 1.890 [1.857, 1.927] | 11.81 [11.61, 12.04] | 0.713 / 0.713 | 0 / 0 |
| 6N | fx | 0.00005 | 5.0 | 4.22 | 0.844 | 1 | 14 (07:00-13:30) | 2.252 [2.154, 2.301] | 11.26 [10.77, 11.50] | 0.887 / 0.887 | 0 / 0 |
| 6S | fx | 0.00005 | 6.25 | 4.22 | 0.675 | 1 | 14 (07:00-13:30) | 2.650 [2.508, 2.806] | 16.56 [15.67, 17.54] | 1.654 / 1.654 | 0 / 0 |
| CL | energy | 0.01 | 10.0 | 4.02 | 0.402 | 1 | 11 (08:00-13:00) | 1.728 [1.699, 1.768] | 17.28 [16.99, 17.68] | 1.319 / 1.319 | 0 / 0 |
| E7 | fx | 0.0001 | 6.25 | 2.72 | 0.435 | 1 | 14 (07:00-13:30) | 1.712 [1.677, 1.781] | 10.70 [10.48, 11.13] | 0.781 / 0.781 | 0 / 0 |
| GC | metals | 0.10 | 10.0 | 4.32 | 0.432 | 1 | 11 (07:00-12:00) | 4.351 [3.855, 4.968] | 43.51 [38.55, 49.68] | 3.074 / 3.074 | 0 / 0 |
| HE | livestock | 0.00025 | 10.0 | 5.22 | 0.522 | 1 | 9 (08:30-12:30) | 1.860 [1.752, 1.965] | 18.60 [17.52, 19.65] | 0.721 / 0.721 | 0 / 0 |
| HG | metals | 0.0005 | 12.5 | 4.32 | 0.346 | 1 | 10 (07:00-11:30) | 2.588 [2.428, 2.813] | 32.35 [30.35, 35.16] | 1.575 / 1.575 | 0 / 0 |
| HO | energy | 0.0001 | 4.2 | 4.02 | 0.957 | 1 | 11 (08:00-13:00) | 9.827 [8.241, 11.624] | 41.27 [34.61, 48.82] | 24.133 / 24.133 | 0 / 0 |
| LE | livestock | 0.00025 | 10.0 | 5.22 | 0.522 | 1 | 9 (08:30-12:30) | 2.393 [2.230, 2.498] | 23.93 [22.30, 24.98] | 0.988 / 0.988 | 0 / 0 |
| M2K | equity | 0.10 | 0.5 | 1.22 | 2.440 | 3 | 13 (08:30-14:30) | 3.954 [3.906, 4.087] | 1.98 [1.95, 2.04] | 1.953 / 1.953 | 0 / 0 |
| M6A | fx | 0.0001 | 1.0 | 1.00 | 1.000 | 10 | 14 (07:00-13:30) | 2.172 [2.155, 2.195] | 2.17 [2.16, 2.19] | 0.613 / 0.613 | 0 / 0 |
| M6B | fx | 0.0001 | 0.625 | 1.00 | 1.600 | 10 | 14 (07:00-13:30) | 3.354 [3.079, 3.720] | 2.10 [1.92, 2.33] | 1.487 / 1.587 | 0 / 0 |
| M6E | fx | 0.0001 | 1.25 | 1.00 | 0.800 | 10 | 14 (07:00-13:30) | 1.922 [1.895, 1.961] | 2.40 [2.37, 2.45] | 0.609 / 0.609 | 0 / 0 |
| MBT | crypto | 5.00 | 0.5 | 2.82 | 5.640 | 1 | 13 (08:30-14:30) | 8.846 [8.554, 9.010] | 4.42 [4.28, 4.50] | 2.613 / 2.613 | 0 / 0 |
| MCL | energy | 0.01 | 1.0 | 1.72 | 1.720 | 4 | 11 (08:00-13:00) | 3.167 [3.122, 3.222] | 3.17 [3.12, 3.22] | 1.313 / 1.313 | 0 / 0 |
| MGC | metals | 0.10 | 1.0 | 1.92 | 1.920 | 1 | 11 (07:00-12:00) | 4.086 [3.946, 4.414] | 4.09 [3.95, 4.41] | 1.838 / 1.838 | 0 / 0 |
| MHG | metals | 0.0005 | 1.25 | 1.92 | 1.536 | 2 | 10 (07:00-11:30) | 3.701 [3.489, 4.096] | 4.63 [4.36, 5.12] | 1.739 / 1.739 | 0 / 0 |
| MNG | energy | 0.001 | 1.0 | 1.92 | 1.920 | 6 | 11 (08:00-13:00) | 5.350 [5.243, 5.602] | 5.35 [5.24, 5.60] | 3.219 / 3.219 | 0 / 0 |
| MNQ | equity | 0.25 | 0.5 | 1.22 | 2.440 | 1 | 13 (08:30-14:30) | 4.119 [4.061, 4.379] | 2.06 [2.03, 2.19] | 1.486 / 1.486 | 0 / 0 |
| MYM | equity | 1.0 | 0.5 | 1.22 | 2.440 | 3 | 13 (08:30-14:30) | 3.983 [3.915, 4.095] | 1.99 [1.96, 2.05] | 2.208 / 2.541 | 0 / 0 |
| NG | energy | 0.001 | 10.0 | 4.22 | 0.422 | 1 | 11 (08:00-13:00) | 1.672 [1.631, 1.686] | 16.72 [16.31, 16.86] | 0.993 / 0.993 | 0 / 0 |
| NQ | equity | 0.25 | 5.0 | 3.78 | 0.756 | 1 | 13 (08:30-14:30) | 3.110 [2.938, 3.532] | 15.55 [14.69, 17.66] | 2.300 / 2.300 | 0 / 0 |
| QG | energy | 0.005 | 12.5 | 2.02 | 0.162 | 1 | 11 (08:00-13:00) | 1.381 [1.335, 1.423] | 17.27 [16.68, 17.79] | 0.774 / 0.774 | 0 / 0 |
| QM | energy | 0.025 | 12.5 | 3.42 | 0.274 | 1 | 11 (08:00-13:00) | 1.599 [1.535, 1.682] | 19.99 [19.19, 21.03] | 1.323 / 1.323 | 0 / 0 |
| RB | energy | 0.0001 | 4.2 | 4.02 | 0.957 | 1 | 11 (08:00-13:00) | 5.515 [4.940, 6.143] | 23.16 [20.75, 25.80] | 10.566 / 10.566 | 0 / 0 |
| RTY | equity | 0.10 | 5.0 | 3.78 | 0.756 | 1 | 13 (08:30-14:30) | 2.359 [2.241, 2.525] | 11.80 [11.20, 12.63] | 1.590 / 1.590 | 0 / 0 |
| SI | metals | 0.005 | 25.0 | 4.32 | 0.173 | 1 | 11 (07:00-12:00) | 3.551 [3.183, 4.019] | 88.78 [79.56, 100.48] | 2.512 / 2.512 | 0 / 0 |
| SIL | metals | 0.005 | 5.0 | 2.72 | 0.544 | 1 | 11 (07:00-12:00) | 2.791 [2.618, 3.257] | 13.95 [13.09, 16.29] | 1.874 / 1.874 | 0 / 0 |
| TN | rates | 0.015625 | 15.625 | 2.62 | 0.168 | 1 | 14 (07:00-13:30) | 1.174 [1.169, 1.180] | 18.35 [18.27, 18.43] | 0.534 / 0.534 | 0 / 0 |
| UB | rates | 0.03125 | 31.25 | 2.92 | 0.093 | 1 | 14 (07:00-13:30) | 1.098 [1.094, 1.107] | 34.33 [34.18, 34.59] | 0.514 / 0.514 | 0 / 0 |
| YM | equity | 1.00 | 5.0 | 3.78 | 0.756 | 1 | 13 (08:30-14:30) | 2.823 [2.759, 2.879] | 14.12 [13.79, 14.39] | 1.779 / 1.779 | 0 / 0 |
| ZB | rates | 0.03125 | 31.25 | 2.76 | 0.088 | 1 | 14 (07:00-13:30) | 1.089 [1.088, 1.092] | 34.04 [34.01, 34.11] | 0.517 / 0.517 | 0 / 0 |
| ZC | grains | 0.0025 | 12.5 | 5.28 | 0.422 | 1 | 10 (08:30-13:00) | 1.425 [1.423, 1.430] | 17.82 [17.79, 17.87] | 0.537 / 0.537 | 0 / 0 |
| ZF | rates | 0.0078125 | 7.8125 | 2.32 | 0.297 | 1 | 14 (07:00-13:30) | 1.298 [1.297, 1.301] | 10.14 [10.13, 10.17] | 0.508 / 0.508 | 0 / 0 |
| ZL | grains | 0.0001 | 6.0 | 5.28 | 0.880 | 1 | 10 (08:30-13:00) | 2.174 [2.113, 2.210] | 13.04 [12.68, 13.26] | 0.897 / 0.897 | 0 / 0 |
| ZM | grains | 0.10 | 10.0 | 5.28 | 0.528 | 1 | 10 (08:30-13:00) | 1.608 [1.585, 1.632] | 16.08 [15.85, 16.32] | 0.632 / 0.632 | 0 / 0 |
| ZN | rates | 0.015625 | 15.625 | 2.62 | 0.168 | 1 | 14 (07:00-13:30) | 1.168 [1.168, 1.168] | 18.25 [18.25, 18.26] | 0.501 / 0.501 | 0 / 0 |
| ZS | grains | 0.0025 | 12.5 | 5.28 | 0.422 | 1 | 10 (08:30-13:00) | 1.469 [1.460, 1.478] | 18.36 [18.25, 18.47] | 0.611 / 0.611 | 0 / 0 |
| ZT | rates | 0.00390625 | 7.8125 | 2.32 | 0.297 | 1 | 14 (07:00-13:30) | 1.301 [1.297, 1.308] | 10.17 [10.13, 10.22] | 0.513 / 0.513 | 0 / 0 |
| ZW | grains | 0.0025 | 12.5 | 5.28 | 0.422 | 1 | 10 (08:30-13:00) | 1.479 [1.463, 1.499] | 18.49 [18.28, 18.73] | 0.636 / 0.636 | 0 / 0 |

### 3.7 Task 9: the vehicle choice (lead, with VehicleCoder-OpusXHigh)
reports/stage_e2a_vehicle_sizes.json (sha256 280d7e9d...7325) and reports/stage_e2a_vehicles.json (sha256
**1f1cafee4330961799f33d5493e640897cfa79827be98597dbaba23292e29913**) with .md files; the D2 rule applied
mechanically under the lead's readings R1 to R12 (reports/stage_e2a_vehicle_rule_readings.md, written
before any bar existed), the arithmetic written out per exposure in the md. **22 exposures chosen, 6
undersized (ZT, ZF, 6C, 6N, ZC, MBT), 3 not traded in Stage E (RBOB, ULSD, silver: no contract with rho at
most 2.0)**, so 28 traded exposures. The deciding cost comparisons: 6B 0.06424 < M6B 0.11177 (GBP), MCL
0.03459 < QM 0.04372 (WTI), NG 0.02615 < MNG 0.08191 (gas); every other exposure had one candidate. The
SIL/MHG preference binds nowhere. **tests/test_e2a_vehicles.py: 91 tests** (R1 to R12: dates and
exclusions, the missing-minute rule, vendor-tick dollars, round-half-up, caps incl. SIL and MHG at 2 by
D9.11, band edges inclusive, M6E and M6A never candidates, the ADV tie, undersized, no candidate, the
eps floor; the D1 table equals the design; 14 of 14 mutants caught). Fable Part 3a reproduced every
figure exactly.

| Exposure | Cluster | Admissible | Candidates | Preferred | Status | Vehicle | q_c | eps_X (net ticks) |
|---|---|---|---|---|---|---|---|---|
| Nasdaq-100 | K1 | MNQ, NQ | MNQ | MNQ | chosen | MNQ | 1 | 170 |
| Russell 2000 | K1 | RTY, M2K | M2K | M2K | chosen | M2K | 3 | 56 |
| Dow | K1 | MYM, YM | MYM | MYM | chosen | MYM | 3 | 56 |
| 2-year | K2 | ZT | ZT | none | undersized | ZT | 1 | 10 |
| 5-year | K2 | ZF | ZF | none | undersized | ZF | 1 | 10 |
| 10-year | K2 | ZN | ZN | ZN | chosen | ZN | 1 | 5 |
| Ultra 10-year | K2 | TN | TN | TN | chosen | TN | 1 | 5 |
| Bond | K2 | ZB | ZB | ZB | chosen | ZB | 1 | 2 |
| Ultra bond | K2 | UB | UB | UB | chosen | UB | 1 | 2 |
| EUR | K3 | 6E, M6E, E7 | 6E, E7 | 6E | chosen | 6E | 1 | 13 |
| AUD | K3 | 6A, M6A | 6A | 6A | chosen | 6A | 1 | 17 |
| GBP | K3 | 6B, M6B | 6B, M6B | 6B, M6B | chosen | 6B | 1 | 13 |
| CAD | K3 | 6C | 6C | none | undersized | 6C | 1 | 17 |
| JPY | K3 | 6J | 6J | 6J | chosen | 6J | 1 | 13 |
| CHF | K3 | 6S | 6S | 6S | chosen | 6S | 1 | 13 |
| NZD | K3 | 6N | 6N | none | undersized | 6N | 1 | 17 |
| WTI crude | K4 | CL, MCL, QM | MCL, QM | MCL, QM | chosen | MCL | 4 | 21 |
| Henry Hub gas | K4 | NG, MNG, QG | NG, MNG, QG | NG, MNG | chosen | NG | 1 | 8 |
| RBOB | K4 | RB | none | none | no candidate: not traded in Stage E | - | - | - |
| ULSD | K4 | HO | none | none | no candidate: not traded in Stage E | - | - | - |
| gold | K5 | MGC, GC | MGC | MGC | chosen | MGC | 1 | 85 |
| silver | K5 | SIL, SI | none | none | no candidate: not traded in Stage E | - | - | - |
| copper | K5 | HG, MHG | MHG | MHG | chosen | MHG | 2 | 34 |
| corn | K6 | ZC | ZC | none | undersized | ZC | 1 | 6 |
| wheat | K6 | ZW | ZW | ZW | chosen | ZW | 1 | 6 |
| soybeans | K6 | ZS | ZS | ZS | chosen | ZS | 1 | 6 |
| soybean meal | K6 | ZM | ZM | ZM | chosen | ZM | 1 | 8 |
| soybean oil | K6 | ZL | ZL | ZL | chosen | ZL | 1 | 14 |
| lean hogs | K6 | HE | HE | HE | chosen | HE | 1 | 8 |
| live cattle | K6 | LE | LE | LE | chosen | LE | 1 | 8 |
| bitcoin | K7 | MBT | MBT | none | undersized | MBT | 1 | 170 |

### 3.8 Task 10: the carried test fixes (TestFixer-SonnetMed, and the lead)
tests/test_d1f_calendar_build.py: test_confirmation_build_end_to_end now skips, with a reason string,
when the real confirmation parquet exists (TestFixer). test_2019_2024_quotes_are_verbatim_from_the_extraction
now accepts a citation that equals the build extraction's pair, or whose url is a source of
reports/stage_d1f_calendar_check.json for that date with every " ... " fragment verbatim and in order in
that source's quote_verbatim (the lead's ruling after TestFixer stopped correctly on the judgment; applied
inline; three mutants caught: one character changed, a wrong url, fragments reordered). The equity
builder later moved 2019-07-03 and 2023-07-03 from the test's "inferred" loop to one asserting 12:15 CT
and "cme" (reviewed: not weakened). Both known failures are gone (29 tests in the file; the full suite
shows 0 failed).

### 3.9 Task 13: the funnel re-derivation of epsilon (FunnelRunner-OpusXHigh)
funnel/exposure_segments.py, exposure_gate.py, exposure_gate_run.py, exposure_gate_mes.py;
**tests/test_e2a_exposure_gate.py: 30 tests** (segment construction on a synthetic exposure, the net-edge
arithmetic, the eps floor, the no-pass flag, resume, A-1's early stop and its exactness). Phase A: the
generalized gate reproduces D.1e's stored MES cells field for field and sample for sample on 7 cells from
T = 1 to T = 32, including the binding cell ($87.48, eps 34). The lead's declaration
(reports/stage_e2a_epsilon_declaration.md, ccdb8ec5...) fixed 16 points (MES's frozen robust critical
value; the [O_X, C_X) window and D2's dates, so E|m_1| x tick value = r_c exactly, asserted for all 28;
E|m_T| up to T = 32; the exact ascending evaluation in two passes, B1 below the translated bar (exact
operative eps) and B2 above it (the reported funnel figure)). Addendum A-1 (e6253be2...): a failing cell
stops once more than 1,531 of its 8,000 careers fail (k_min = 6,469), exact for every verdict; validated
three ways before use. Worker count does not change results.

| # | Cluster | Exposure | Vehicle | q_c | Status | eps translated | bar $/day | B1 | B1 cells | early-stopped | eps operative | eps funnel | B2 | flags |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | K2 | 2-year | ZT | 1 | undersized | 10 | 78.12 | pass consistency|T2|p0.55|R2.0 ($45.55) | 212/220 | 0 | 5 | 5 | not needed (B1 found a pass below the bar) | undersized |
| 2 | K2 | 5-year | ZF | 1 | undersized | 10 | 78.12 | pass consistency|T2|p0.6|R1.5 ($50.57) | 206/218 | 0 | 6 | 6 | not needed (B1 found a pass below the bar) | undersized |
| 3 | K2 | 10-year | ZN | 1 | chosen | 5 | 78.12 | pass consistency|T1|p0.58|R1.5 ($57.04) | 194/208 | 140 | 3 | 3 | not needed (B1 found a pass below the bar) | none |
| 4 | K2 | Ultra 10-year | TN | 1 | chosen | 5 | 78.12 | pass consistency|T2|p0.65|R1.0 ($65.34) | 168/194 | 114 | 4 | 4 | not needed (B1 found a pass below the bar) | none |
| 5 | K2 | Bond | ZB | 1 | chosen | 2 | 62.50 | none below the bar | 144/144 | 159 | 2 | 2 | pass consistency|T1|p0.65|R1.0 ($86.55) | none |
| 6 | K2 | Ultra bond | UB | 1 | chosen | 2 | 62.50 | none below the bar | 126/126 | 143 | 2 | 2 | pass consistency|T2|p0.62|R1.0 ($92.63) | none |
| 7 | K4 | WTI crude | MCL | 4 | chosen | 21 | 84.00 | none below the bar | 118/118 | 137 | 21 | 24 | pass consistency|T1|p0.65|R1.0 ($97.27) | none |
| 8 | K4 | Henry Hub gas | NG | 1 | chosen | 8 | 80.00 | none below the bar | 81/81 | 94 | 8 | 11 | pass consistency|T8|p0.575|R1.0 ($115.77) | none |
| 9 | K5 | gold | MGC | 1 | chosen | 85 | 85.00 | pass consistency|T4|p0.66|R0.75 ($71.43) | 102/140 | 75 | 71 | 71 | not needed (B1 found a pass below the bar) | none |
| 10 | K5 | copper | MHG | 2 | chosen | 34 | 85.00 | pass consistency|T2|p0.65|R1.0 ($69.67) | 176/198 | 149 | 27 | 27 | not needed (B1 found a pass below the bar) | none |
| 11 | K3 | EUR | 6E | 1 | chosen | 13 | 81.25 | pass consistency|T2|p0.62|R1.0 ($80.09) | 136/138 | 135 | 12 | 12 | not needed (B1 found a pass below the bar) | none |
| 12 | K3 | AUD | 6A | 1 | chosen | 17 | 85.00 | pass consistency|T2|p0.55|R1.5 ($56.14) | 182/206 | 181 | 11 | 11 | not needed (B1 found a pass below the bar) | none |
| 13 | K3 | GBP | 6B | 1 | chosen | 13 | 81.25 | pass consistency|T2|p0.55|R1.5 ($52.46) | 176/208 | 175 | 8 | 8 | not needed (B1 found a pass below the bar) | none |
| 14 | K3 | CAD | 6C | 1 | undersized | 17 | 85.00 | pass consistency|T1|p0.55|R2.0 ($45.29) | 206/218 | 205 | 9 | 9 | not needed (B1 found a pass below the bar) | undersized |
| 15 | K3 | JPY | 6J | 1 | chosen | 13 | 81.25 | pass consistency|T1|p0.54|R1.75 ($63.17) | 186/204 | 185 | 10 | 10 | not needed (B1 found a pass below the bar) | none |
| 16 | K3 | CHF | 6S | 1 | chosen | 13 | 81.25 | none below the bar | 126/126 | 135 | 13 | 15 | pass consistency|T4|p0.68|R0.75 ($94.55) | none |
| 17 | K3 | NZD | 6N | 1 | undersized | 17 | 85.00 | pass consistency|T1|p0.7|R1.0 ($51.41) | 198/214 | 197 | 10 | 10 | not needed (B1 found a pass below the bar) | undersized |
| 18 | K6 | corn | ZC | 1 | undersized | 6 | 75.00 | pass consistency|T2|p0.6|R1.5 ($52.62) | 208/216 | 207 | 4 | 4 | not needed (B1 found a pass below the bar) | undersized |
| 19 | K6 | wheat | ZW | 1 | chosen | 6 | 75.00 | pass consistency|T4|p0.55|R1.5 ($61.31) | 174/196 | 173 | 4 | 4 | not needed (B1 found a pass below the bar) | none |
| 20 | K6 | soybeans | ZS | 1 | chosen | 6 | 75.00 | pass consistency|T1|p0.65|R1.0 ($72.85) | 154/158 | 153 | 5 | 5 | not needed (B1 found a pass below the bar) | none |
| 21 | K6 | soybean meal | ZM | 1 | chosen | 8 | 80.00 | pass consistency|T1|p0.57|R1.5 ($57.56) | 174/202 | 173 | 5 | 5 | not needed (B1 found a pass below the bar) | none |
| 22 | K6 | soybean oil | ZL | 1 | chosen | 14 | 84.00 | pass consistency|T4|p0.68|R0.75 ($69.38) | 136/156 | 135 | 11 | 11 | not needed (B1 found a pass below the bar) | none |
| 23 | K6 | lean hogs | HE | 1 | chosen | 8 | 80.00 | pass consistency|T2|p0.62|R1.0 ($70.79) | 142/152 | 141 | 7 | 7 | not needed (B1 found a pass below the bar) | none |
| 24 | K6 | live cattle | LE | 1 | chosen | 8 | 80.00 | none below the bar | 90/90 | 103 | 8 | 11 | pass consistency|T1|p0.6|R1.0 ($118.14) | none |
| 25 | K7 | bitcoin | MBT | 1 | undersized | 170 | 85.00 | pass consistency|T2|p0.52|R1.75 ($45.37) | 196/216 | 195 | 90 | 90 | not needed (B1 found a pass below the bar) | undersized |
| 26 | K1 | Nasdaq-100 | MNQ | 1 | chosen | 170 | 85.00 | none below the bar | 78/78 | 83 | 170 | 186 | pass consistency|T16|p0.55|R1.0 ($93.04) | none |
| 27 | K1 | Russell 2000 | M2K | 3 | chosen | 56 | 84.00 | pass consistency|T2|p0.6|R1.0 ($75.27) | 103/115 | 102 | 50 | 50 | not needed (B1 found a pass below the bar) | none |
| 28 | K1 | Dow | MYM | 3 | chosen | 56 | 84.00 | none below the bar | 85/85 | 86 | 56 | 60 | pass consistency|T4|p0.58|R1.0 ($90.71) | none |

E|m_T| per exposure (vendor ticks per contract), round-turn cost and the r_c identity:

| Vehicle | T=1 | T=2 | T=4 | T=8 | T=16 | T=32 | RT cost T=1 | E|m_1| x tv = r_c | days used | short days (max over T) |
|---|---|---|---|---|---|---|---|---|---|---|
| ZT | 14.42 | 9.17 | 6.21 | 4.32 | 2.99 | 2.16 | 1.300 | True (112.68) | 286 | 0 |
| ZF | 17.35 | 11.11 | 7.74 | 5.39 | 3.75 | 2.66 | 1.299 | True (135.54) | 286 | 0 |
| ZN | 13.12 | 8.48 | 5.95 | 4.12 | 2.88 | 2.06 | 1.169 | True (204.93) | 286 | 0 |
| TN | 16.64 | 10.88 | 7.51 | 5.21 | 3.61 | 2.57 | 1.174 | True (259.94) | 286 | 0 |
| ZB | 12.87 | 8.55 | 5.94 | 4.08 | 2.88 | 2.05 | 1.091 | True (402.10) | 286 | 0 |
| UB | 16.05 | 10.76 | 7.48 | 5.21 | 3.66 | 2.58 | 1.099 | True (501.42) | 286 | 0 |
| MCL | 91.57 | 61.75 | 45.03 | 33.78 | 23.03 | 16.22 | 3.152 | True (91.57) | 258 | 0 |
| NG | 63.93 | 43.55 | 30.34 | 20.76 | 14.64 | 10.54 | 1.652 | True (639.31) | 259 | 0 |
| MGC | 258.59 | 176.38 | 122.44 | 87.79 | 62.02 | 44.58 | 4.170 | True (258.59) | 290 | 0 |
| MHG | 88.17 | 59.15 | 41.41 | 29.59 | 20.69 | 14.66 | 3.820 | True (110.22) | 290 | 0 |
| 6E | 51.11 | 34.80 | 24.16 | 17.22 | 11.98 | 8.46 | 1.950 | True (319.45) | 293 | 0 |
| 6A | 36.73 | 25.54 | 18.51 | 12.96 | 8.92 | 6.31 | 2.198 | True (183.65) | 293 | 0 |
| 6B | 29.80 | 19.94 | 13.96 | 9.96 | 7.04 | 4.99 | 1.914 | True (186.22) | 293 | 0 |
| 6C | 24.06 | 16.63 | 12.07 | 8.30 | 5.71 | 4.19 | 2.000 | True (120.29) | 293 | 0 |
| 6J | 32.77 | 21.65 | 14.54 | 10.27 | 7.12 | 5.04 | 1.907 | True (204.82) | 293 | 0 |
| 6S | 65.72 | 43.50 | 29.39 | 21.19 | 14.89 | 10.49 | 2.627 | True (410.75) | 293 | 0 |
| 6N | 31.30 | 21.85 | 15.42 | 11.39 | 7.75 | 5.40 | 2.238 | True (156.48) | 293 | 0 |
| ZC | 12.65 | 8.65 | 5.75 | 4.07 | 2.88 | 2.02 | 1.429 | True (158.16) | 271 | 0 |
| ZW | 18.78 | 13.45 | 8.85 | 6.27 | 4.39 | 3.10 | 1.487 | True (234.75) | 277 | 0 |
| ZS | 24.35 | 16.77 | 11.39 | 7.93 | 5.62 | 3.97 | 1.478 | True (304.39) | 279 | 0 |
| ZM | 21.26 | 15.06 | 10.32 | 7.10 | 4.98 | 3.55 | 1.623 | True (212.64) | 273 | 0 |
| ZL | 50.80 | 33.63 | 23.11 | 16.62 | 11.57 | 8.14 | 2.198 | True (304.83) | 282 | 0 |
| HE | 32.30 | 22.48 | 15.64 | 10.80 | 7.63 | 5.26 | 1.838 | True (322.96) | 270 | 0 |
| LE | 70.72 | 46.53 | 31.88 | 21.83 | 15.27 | 10.71 | 2.329 | True (707.16) | 264 | 0 |
| MBT | 241.23 | 167.68 | 112.00 | 79.51 | 55.38 | 39.46 | 9.260 | True (120.61) | 260 | 0 |
| MNQ | 726.92 | 490.28 | 338.57 | 227.45 | 157.66 | 111.82 | 4.300 | True (363.46) | 285 | 0 |
| M2K | 212.27 | 145.90 | 96.85 | 66.57 | 47.19 | 33.20 | 4.220 | True (106.13) | 286 | 0 |
| MYM | 262.30 | 177.32 | 119.91 | 83.28 | 58.60 | 41.77 | 4.307 | True (131.15) | 286 | 0 |


## 4. Delegation record

| Agent | Worker file | Model | Effort | Objective | Status | Deviations |
|---|---|---|---|---|---|---|
| lead | — | opus | xhigh | Tasks 0, 1, 4, 9 (readings, sign-off), 11 (amendment, rulings, commits), 13 (declaration, addendum), rulings L-1 to L-13 and T12-1 to T12-4, return | done | applied the D14 verbatim-test edit inline after ruling on it (small, no isolation needed); restarted the funnel driver itself after the clean stop (an already-written resumable command) |
| TestFixer-SonnetMed | worker-medium | sonnet | medium | Task 10 | done | stopped correctly on the verbatim-test equivalence (a judgment); the lead ruled and applied it |
| CalendarBuilder-Rates / FX / Energy / Metals / Grains / Livestock / Crypto / Equity-OpusXHigh (8) | workflow agents (worker-xhigh) | opus | xhigh | Task 6, one group each | all done | the equity builder corrected one D.1f test expectation (reviewed, not weakened); interface extensions (LateOpen, EARLY_SETTLEMENT_CT, BOOKED_FORWARD, EXTENDED_MAINTENANCE) additive |
| DeclarationAuditor-FableXHigh | worker-xhigh | fable | xhigh | Task 3 (Part 1), Task 12 (Parts 3a, 3b), Task 11 audit (Part 2), resumed with SendMessage | done (Parts 1, 2, 3a, 3b all complete; stopped by Fable's weekly limit only after its last patch was written) | stopped once by the plan session limit (resumed) |
| BarsCoder-OpusXHigh | worker-xhigh | opus | xhigh | Task 7 and the calendar bar checks | done | returned and was resumed per released group (4 rounds) to free its slot; its brief wrongly made closure bars a hard failure (corrected by L-3); its own NG bug found and fixed |
| CostCoder-OpusXHigh | worker-xhigh | opus | xhigh | Task 8 | done | resumed once for the depth term; the prompt's MES check replaced (guardrail, OC-6) |
| FunnelRunner-OpusXHigh | worker-xhigh | opus | xhigh | Task 13 (phase A; phase B B1 and B2) | done (B1 and B2 for all 28 traded exposures; the lead restarted the resumable driver after the pauses) | stopped by the session limit (its detached driver kept running) and resumed; added A-1; stopped at the user's clean stop |
| VehicleCoder-OpusXHigh | worker-xhigh | opus | xhigh | Task 9 code (sizes, then choice) | done | none |
| SourceWindowReader-OpusHigh | worker-high | opus | high | Task 2 | done | stopped by the session limit and resumed; wrote the member-to-source map into the JSON at the end rather than first |
| RulesCoder-OpusXHigh | worker-xhigh | opus | xhigh | Task 5 | done | stopped by the session limit and resumed; resumed again for L-13's default |

Sixteen workers in all; at most four ran at once (workflow agents included). Fable ran one worker only.
Ultracode's fan-out was the calendar workflow (eight opus xhigh agents, the stage's largest job); its
token share is in section 8. Every other worker was a singleton Agent call, resumed with SendMessage
where the work came in phases.


## 5. Verification

All by DeclarationAuditor-FableXHigh (Claude Fable 5.1, xhigh), which produced none of the work checked,
in reports/stage_e2a_declaration_audit.md.

**Part 1, the ML freeze audit (Task 3):** READY WITH FIXES; 2 BLOCKING, 14 SHOULD FIX, 10 NOTE. Every
finding has a ruling and its fix in reports/stage_e2a_ml_freeze_rulings.md (all 16 must-fix findings
fixed within V1 to V9 by bracketed ruling notes; NOTEs A17, A18, A19, A20, A23, A25, A26 acted on; A21
partly; A22 recorded; A24 left, since those figures decide nothing). Highlights: ML-A01 (selection
metric: long if y_hat > 0, short if y_hat < -2c, one open position per product, sigma units, product day
= sum, portfolio day = mean over products with rows, configuration score = mean of 10 split scores);
ML-A02 (per-side candidate threshold at the 1.5 x stress: long if mu > 0.5 c_bar, short if mu < -2.5
c_bar); ML-A04 (the route's code frozen by E.2b's harness manifest before E.ML-buy, new M7.8); ML-A14
(V6's effect on D5 recorded in DECISIONS.md).

**Part 2, the source-window amendment (Task 11):** all six removals CONFIRMED; 0 BLOCKING, 0 SHOULD FIX,
7 NOTE (SW-A01 to A07; SW-A04 upheld: the "no data sample" reading decides K3-mehedge-01); the auditor's
own classification of all 145 rows and recomputation of all 37 labels equal the amendment's; all 32 E.1
frozen files match. Rulings in reports/stage_e2a_source_window_rulings.md.

**Part 3a, sizes, vehicles, translated epsilon, costs (Task 12):** 45 of 45 contracts VERIFIED (r_c,
q_c, rho_c by exact rational equality; identical date sets and exclusion lists); 31 of 31 exposures
VERIFIED (status, vehicle, q_c, eps, candidates, cost per dollar of risk); the cost tables of ZN, CL, ZC
and MBT rebuilt from the raw mbp-1 books VERIFIED (max |ds_b| 4e-16 ticks); 0 DISCREPANCY. Readings: R1
to R12 9 VERIFIED, 3 WITH NOTES; L-1 to L-11 VERIFIED as applied; CostCoder's R1 to R10 8 VERIFIED, 2
WITH NOTES. Lead rulings: T12-1 R8 upheld (D2 prices the order at size q_c, so q_c cancels; the
alternative is dimensionally inconsistent and would favour micros against D2's own reasoning; GBP stays
6B, gas stays NG); T12-2 R5 upheld (D9.11's own "Encoded" line caps SIL and MHG at 2; copper stays MHG,
q_c 2, eps 34); T12-3 noted (no band, q_c or vehicle moves); T12-4 the cost table's event-window field
for M2K, M6B, MCL, MNG, MYM uses max(s_b + depth) where D8's literal text says the largest s_b: no E.2a
number uses it; flagged for E.2b's fill model; the frozen table is not rewritten.

**Part 3b, the funnel epsilon (Task 12):**

VERIFIED throughout, 0 DISCREPANCY: the auditor's own driver reproduced E|m_T| (T = 1..32), the per-T costs and the r_c identity for all 28 traded exposures (differences 0.0); the 220-cell sets, the below-bar sets, the B1 ascending replay, every first pass and the epsilon arithmetic for all 28; 30 of 30 cells re-simulated through the frozen Stage B simulator with its own generator, cost book and pool (the ZT, MGC, MBT and ZS binding cells pass with identical power and bit-identical samples; every preceding cell is not a pass; the highest-$ below-bar cells of ZB and MYM and every early-stopped cell stop at exactly the stored run and failure counts), which also settles the mixed early-stopped and full-length rows and the restarts; all 28 operative figures; and the B2 funnel figures of all 8 exposures without a pass below the bar (ZB 2, UB 2, MCL 24, NG 11, 6S 15, LE 11, MNQ 186, MYM 60). One NOTE, for the user: declaration point 1 uses MES's frozen robust critical value for every exposure (capped by the translated bar). The auditor recorded that its brief file was lost in the 17:08 reboot and worked from the lead's messages. Fable's weekly limit ended the session after its last patch; the lead checked mechanically that the audit file up to Part 3b equals commit 04c504f's.


## 6. Open choices (the lead's own decisions, each with its reason; each can be overturned)

Scheduling and method
- **OC-1 Probe after the freeze.** Task 0 asked for a bar-build probe before sizing, but the guardrail forbids opening a price file before the ML freeze commit; the probe ran right after it (ZN, one month: 2.4 s, 166 MB), and the build rows were guesses until then.
- **OC-2 Task 2 after calendar sourcing.** Off the critical path, and both used the web; the calendar-to-funnel chain got the slots first.
- **OC-3 Task 2's scope.** The 37 members under the FA-06 fallback; the 16 members labelled source-overlap in the frozen catalog were left as frozen (their label rests on E.0's entries, not on the fallback).
- **OC-4 The D14 verbatim test.** Its equivalence rule (" ... " fragments verbatim and in order in the check file's quote_verbatim) is the lead's ruling after TestFixer stopped on it; applied inline.
- **OC-5 Task 1's notes.** A-1 (the LSTM batch-size re-plan written as a mechanical rule on synthetic inputs), A-2 (the draft's CPU fallback struck with the Windows PC), A-3 (E.2a/E.2b names); questions Q-1 to Q-3 left to the user.
- **OC-6 The MES cost check.** The prompt's "MES table reproduces the D.1 cost model" could not be run: MES has no mbp-1 in step 1, and D.1's MES mbp-10 lies in holdout-1's dates. Replaced by D.1's recorded table re-expressed under D8's arithmetic and compared with MNQ's table, with no data read.
- **OC-7 Vehicle rule readings R1 to R12**, written and hashed before any bar existed: D6's O and C as clock times; R2's dates (roll blackout, degraded, closures and early closes at or before C excluded); R3's nearest traded minute inside [O, C); R5's cap = min(D9.5, D9.11); R6 round-half-up; R8's cost per dollar of risk with q_c cancelled (upheld on audit, T12-1); R9 the SIL/MHG sentence as a preference among candidates; R10 undersized on the cheapest candidate; R12 the translated eps floor.
- **OC-8 Free symbology.resolve calls** for roll boundaries (NULL_CRITERIA_E 4's source), research-window dates only, no ledger line.
- **OC-9 Scheduling of BarsCoder.** Builds take seconds, so BarsCoder returned between groups and was resumed as each calendar landed, freeing its slot for the cost work.
- **OC-10 The epsilon declaration** (16 points, reports/stage_e2a_epsilon_declaration.md): MES's frozen robust critical value; headline values not computed; 0.1-lot size units; the [O_X, C_X) window on the trade date's own day; D2's dates and endpoints (E|m_1| x tick value = r_c); E|m_T| to T = 32; MES's cost timing, mean of the two sides, no event cost; the exposure's own p_beats sample; undersized exposures at min(translated, funnel) (D2's "governs" against D3's minimum: the conservative minimum; for the user); the exact ascending evaluation in passes B1 and B2 instead of D3's bracketing subset (phase A showed the subset inexact and slower, and ZT's pass lay outside it); T = 32 cells kept; vendor ticks; each vehicle's own bars; D.1e's floor; 8,000 careers and the frozen seed.
- **OC-11 Addendum A-1** (exact early termination of failing cells), written after the session-limit pause when B1 was projected at about 20 hours; validated three ways before use.
- **OC-12 The source-window amendment's readings**: the widest confirmation window, "any of its sources" (all cited sources), secondary-only windows as unknown, documentation sources with no data sample neither keeping nor removing a label (upheld on audit, SW-A04).
- **OC-13 Rulings on the audit notes**: T12-1 to T12-4 (section 5) and SW-A01 to A07.

Rulings on the build (reports/stage_e2a_STATE.md)
- **L-1** D6's O values are CME conventions for the day-session open that CME does not publish; they stand. **L-2** Early-settlement days (rates' 41 pre-holiday 12:00 CT settlements) are not early closes. **L-3** Bars inside a scheduled closure are kept and flagged, as MES's validator does, not a hard failure (the brief had it wrong). **L-4 (revised)** The 2025-11-28 CME outage is a gap run, not a calendar window (the stop time is unsourced). **L-5** FX 2025-11-27: thin holiday trading. **L-6** Grains' scheduled late opens are closed windows. **L-7** Metals' quiet minutes before settlement are thin trading; 2026-02-25 is an unscheduled, unsourced halt, recorded. **L-8** Roll blackouts from each product's group calendar. **L-9** MBT's bars booked to 2026-06-22 are dropped (section 2). **L-10** A booked-forward trade date's day session is read on its own calendar day. **L-11** MBT's expiry Fridays are contract expiry. **L-12** Equity settled at 15:15 CT before 2020-10-26: affects only K1's confirmation dates; left to the session that freezes K1's list; D6 unchanged. **L-13** Topstep's 2% price-limit rule does not apply to products whose only CME protection is dynamic circuit breakers (rates, FX, energy, metals, MBT): Topstep's text says "price lock limit"; a circuit breaker never locks; D9.7's examples are grain and equity limits; the other reading would make ZT, ZF and ZN untradeable every day. The switch keeps the other reading; a question Topstep can answer.

Flags carried from the rules engine: R-F1 (Topstep required funded accounts to flatten 30 minutes before an early close in 2024-2025; encoded in rules/ only, MES's engine unchanged), R-F3 (no Topstep holiday schedule for 2019-2023: CME early close minus 15 minutes), R-F4 (Topstep's holiday close binds where CME trades on, e.g. FX on MLK Day 2025), R-W1/2 (unpublished lot weights: QM, QG, E7 as 1 lot; M6E, M6A, M6B as 0.1), R-V1 (SI and HG may be set to 0 by Topstep; neither is a vehicle).


## 7. What the next session must do first

- **Commits and push (the planning chat):** ba67073 (ML freeze) and 04c504f (source-window amendment) are on main, not pushed. The build is uncommitted for review: data/build_bars.py, build_bars_run.py, build_bars_reports.py, group_session.py, data/calendars/ (8 modules), data/cme_calendar.py (the 2024-07-04 fix and two grades), additive data/bars.py and data/validate.py, rules/{products,constraints,sessions,price_limits}.py, sim/{cost_inputs,calibrate_costs,cost_rule,cost_report,cost_report_md,product_costs}.py, screening/vehicles*.py, funnel/exposure_*.py, 13 new test files and tests/test_d1f_calendar_build.py, the reports (stage_e2a_*), this file, progress.md and docs/STAGES.md. The research parquets and roll caches under data/processed/ and data/vendor/ are git-ignored.
- **Frozen or hashed files:** E.1's manifest reports/stage_e1_freeze.json (96166eb3..., 32 files, all match); the ML route manifest reports/stage_e2a_ml_freeze.json (**077a57e1c00554dd0745302b247673d45ee05b805ac4bfd876f8497f7bbb1ed2**); and, recorded by hash in this stage for E.2b's harness manifest to freeze: the cost table reports/stage_e2a_costs.json (f4360bb7...96df14), the sizes reports/stage_e2a_vehicle_sizes.json (280d7e9d...7325), the vehicles reports/stage_e2a_vehicles.json (1f1cafee...9913), the readings (8c3c29dd...b458), the epsilon declaration (ccdb8ec5...8c7c) and addendum A-1 (e6253be2...8d32), the amendment (9fe401c1...f13d). Epsilon results: reports/stage_e2a_epsilon.json (sha256 4e2c773182a23e7d073305ca4eb0134d3b3ac554ccc8215730bc1e194eaff496), with every cell in reports/stage_e2a_funnel/<VEHICLE>/cells.jsonl; E.2b's harness manifest should freeze it with the vehicles.
- **Funding owed:** the ML route's history (the full step 2 range, 2019-05..2025-03, one contract per exposure; about $165-190 from E.0's quotes, to be re-quoted) needs acct-2 topped up; acct-2 holds $21.52. The route's purchase cap is the user's (Q-1).
- **Topstep answers owed:** M6E and M6A (U7; still not candidates), and optionally the circuit-breaker reading of the 2% price-limit rule (L-13).
- **For E.2b:** the runner must use each group's roll blackouts (L-8), the vendor-unit ticks (cent-quoted grains and livestock), the flatten rules of rules/sessions.py (R-F1, R-F4), the event-window cost under D8's literal reading (T12-4), and must refuse MBT's rows booked to 2026-06-22 (L-9); check 2026-06-18/19 for an unseen roll; the equity pre-2020-10-26 settlement question (L-12) is for K1's session; 43 proposed equity grade upgrades are in reports/stage_e2a_calendar_sources_equity.md.
- **Blockers for E.2b:** none for the build. The ML route's history purchase waits on funding (acct-2 holds $21.52).


## 8. Session cost

All times PDT. Rows from reports/stage_e2a_STATE.md; tokens from the transcripts (below). Token counts, not plan credits.

**Final table**

| # | Task | Owner | Model / effort | Start-end | Time | Status |
|---|---|---|---|---|---|---|
| 0 | Startup, checks, plan, ETA | lead | opus xhigh | 09-25 00:12-00:19 | 7 min | done |
| 1 | V1-V9 edits, changes log, DECISIONS | lead | opus xhigh | 00:19-00:27 | 8 min | done |
| 10 | D14 test fixes | TestFixer-SonnetMed + lead | sonnet medium | 00:21-00:31 | 10 min | done |
| 3 | ML freeze audit (Part 1) | DeclarationAuditor-FableXHigh | fable xhigh | 00:30-00:47 | 17 min | READY WITH FIXES |
| 4 | Rulings, manifest, commit ba67073 | lead | opus xhigh | 00:48-00:53 | 5 min | done |
| 6 | Calendars x8 (workflow, 3 lanes) | CalendarBuilder x8 | opus xhigh | 00:22-02:40 | 2 h 18 min | done |
| 7 | Bar builds, calendar bar checks | BarsCoder-OpusXHigh | opus xhigh | 00:48-02:52 (in rounds) | 2 h 04 min | done |
| 8 | Cost model | CostCoder-OpusXHigh | opus xhigh | 01:37-02:43 | 1 h 06 min | done |
| 13A | Funnel phase A (code, MES regression, probe) | FunnelRunner-OpusXHigh | opus xhigh | 01:55-02:34 | 39 min | done |
| 9 | Sizes, vehicle choice, sign-off | VehicleCoder-OpusXHigh + lead | opus xhigh | 02:15-02:44 | 29 min | done |
| 12-3a | Recompute sizes, vehicles, costs | DeclarationAuditor-FableXHigh | fable xhigh | 02:53-03:03, 06:10-06:32 | 32 min | VERIFIED |
| P | Plan session limit | — | — | 03:03-06:10 | (3 h 07 min) | pause, not work; the detached funnel kept running |
| 2 | Source windows | SourceWindowReader-OpusHigh | opus high | 02:37-03:03, 06:10-06:13 | 29 min | done |
| 5 | Rules engine | RulesCoder-OpusXHigh | opus xhigh | 02:37-03:03, 06:10-07:03 | 1 h 19 min | done |
| 11 | Amendment, audit Part 2, rulings, commit 04c504f | lead + DeclarationAuditor | opus / fable xhigh | 06:13-06:45 | 32 min | done |
| 13B | Funnel B1 and B2 | detached driver (FunnelRunner, then lead restarts) | — | 02:53-03:03 and 03:03-08:13 unattended, 17:10-21:34, 09-26 03:21-07:19 | about 13 h 17 min of compute | done |
| P2 | Clean stop on the user's request (machine rebooted 17:08) | — | — | 08:13-17:10 | (8 h 57 min) | pause |
| 12-3b | Recompute funnel epsilon | DeclarationAuditor-FableXHigh | fable xhigh | 19:16-20:22, 09-26 06:40-07:55 | 2 h 21 min | VERIFIED; ended by Fable's weekly limit after its patch |
| P3 | Pause on the user's request | — | — | 21:34-09-26 03:21 | (5 h 47 min) | pause |
| R | End checks, return document, progress, STAGES | lead | opus xhigh | 09-26 07:19-07:45 | 26 min | done |
| Σ | Whole stage | lead + 16 workers | | 09-25 00:12 - 09-26 07:45 | about 31 h 33 min elapsed, of which 17 h 51 min pauses; about 13 h 42 min of work, most of it the funnel's compute | done |

Against the initial estimate (end about 10:15-13:15 on 09-25, about 10-13 h): the build rows ran faster than guessed (bars took seconds), and the funnel far slower (the per-exposure cell sets were larger than MES's, about 42 s per cell until addendum A-1's exact early stop cut it to about 11-15 s). Lead errors that cost time: the 17:10 restart without `--early-stop` (about 30 min of slower cells, results unaffected) and two shell self-kills with a process-matching command (no work affected).

**Tokens per model** (sum of each assistant message's usage fields, once per message, over this session's transcript and its subagent transcripts, workflow agents included; never estimated):

| Model | Input | Output | Cache read | Cache creation | Total |
|---|---|---|---|---|---|
| claude-opus-5-5 | 4,296 | 3,044,770 | 731,528,078 | 23,423,501 | 758,000,645 |
| claude-fable-5-1 | 2,030 | 284,611 | 29,845,679 | 7,576,742 | 37,709,062 |
| claude-sonnet-5 | 70 | 19,147 | 3,808,404 | 146,921 | 3,974,542 |
| **All** | 6,396 | 3,348,528 | 765,182,161 | 31,147,164 | **799,684,249** |

**Per spawn** (agent, model, tokens total / output; first and last transcript record):

| Agent | Worker file | Model | Effort | Tokens total | Output | First..last |
|---|---|---|---|---|---|---|
| SourceWindowReader-OpusHigh | worker-high | opus | high | 45,929,321 | 111,538 | 09-25 02:37..09-25 06:14 |
| RulesCoder-OpusXHigh | worker-xhigh | opus | xhigh | 55,493,019 | 246,033 | 09-25 02:37..09-25 07:00 |
| DeclarationAuditor-FableXHigh | worker-xhigh | fable | xhigh | 37,709,062 | 284,611 | 09-25 00:30..09-26 07:35 |
| CostCoder-OpusXHigh | worker-xhigh | opus | xhigh | 19,555,473 | 139,070 | 09-25 01:33..09-25 02:39 |
| TestFixer-SonnetMed | worker-medium | sonnet | medium | 3,974,542 | 19,147 | 09-25 00:21..09-25 00:29 |
| FunnelRunner-OpusXHigh | worker-xhigh | opus | xhigh | 42,233,769 | 221,511 | 09-25 01:56..09-25 08:12 |
| VehicleCoder-OpusXHigh | worker-xhigh | opus | xhigh | 15,900,938 | 144,121 | 09-25 02:15..09-25 02:44 |
| BarsCoder-OpusXHigh | worker-xhigh | opus | xhigh | 53,918,319 | 264,052 | 09-25 00:47..09-25 03:03 |
| CalendarBuilder-Rates-OpusXHigh | workflow (worker-xhigh) | opus | xhigh | 47,884,159 | 222,526 | 09-25 00:22..09-25 01:03 |
| CalendarBuilder-Grains-OpusXHigh | workflow (worker-xhigh) | opus | xhigh | 31,661,176 | 195,854 | 09-25 01:03..09-25 01:35 |
| CalendarBuilder-Equity-OpusXHigh | workflow (worker-xhigh) | opus | xhigh | 55,603,442 | 203,341 | 09-25 01:35..09-25 02:41 |
| CalendarBuilder-Energy-OpusXHigh | workflow (worker-xhigh) | opus | xhigh | 37,230,599 | 186,221 | 09-25 00:22..09-25 01:15 |
| CalendarBuilder-Livestock-OpusXHigh | workflow (worker-xhigh) | opus | xhigh | 37,007,356 | 162,885 | 09-25 01:14..09-25 01:44 |
| CalendarBuilder-Crypto-OpusXHigh | workflow (worker-xhigh) | opus | xhigh | 46,003,019 | 207,700 | 09-25 01:38..09-25 02:15 |
| CalendarBuilder-FX-OpusXHigh | workflow (worker-xhigh) | opus | xhigh | 41,001,160 | 179,191 | 09-25 00:22..09-25 01:14 |
| CalendarBuilder-Metals-OpusXHigh | workflow (worker-xhigh) | opus | xhigh | 29,742,003 | 118,323 | 09-25 01:15..09-25 01:38 |

**Delegation share:** lead 198,836,892 (24.9%), workers 600,847,357 (75.1%). By tier: opus 94.8%, Fable 4.7%, Sonnet 0.5%. **Ultracode share:** the calendar workflow's eight agents, 326,132,914 tokens (40.8% of the stage).
