# Stage E.2b worker report: CalendarAssembler-OpusXHigh (release calendar, lead rulings OC-J, OC-N)

Worker: CalendarAssembler-OpusXHigh (worker-xhigh, opus). Brief: reports/stage_e2b_briefs/g2b_calendar.md with
00_common.md and g1_release_common.md; lead messages: commodity file final, NGS ruling, CROP_ANNUAL ruling.
Times PDT (America/Vancouver), 2026-09-26. Work ran about 16:50 to 17:12.

## Result

- `reports/stage_e2b_release_calendar.json`, schema `stage_e_release_calendar/1`, written 17:08, read-only (0444),
  sha256 `839f2437bedbeb7b3423d7058a9955a0d4ccd1aebc4b01c62be624ab11d7bcb8`, 2,118,589 bytes.
  `--check` (a rebuild in memory) reproduces it byte for byte. The JSON has no timestamp.
- `reports/stage_e2b_release_calendar.md`, the summary, read-only, sha256 `f2a1360b8eab94bb7ebec938632e1afb44be7597a987d576a98c4658716467f5`.
- 2,609 entries (macro 227, commodity 921, named 1,461): 1,872 verified, 365 [unverified] (all NGS), 372
  announced_schedule (all API_WSB). All are kept and have products. 14 cancellations have no entry (CPI 1, CROP 1,
  CROP_PROGRESS 6, FOMC 1, G17 2, NFP 1, PPI 1, WASDE 1).
- Loader round trip: `screening.stage_e_rules.release_calendar_from_dict` reads 47 roots (every root in
  rules/products.py), 85 CPI instants, coverage 2019-05-01..2026-06-21, 142 to 1,173 instants per root.
  `ml_route.inputs.load_event_calendar()` reads the written file, and `require_coverage(2019-05-06, 2024-02-29)` passes.
- Products per release (after ruling OC-N):

| Release | Products |
|---|---|
| NFP | 32: the 24 F6.4 roots in the product table, plus micro siblings M2K M6B MES MGC MHG MNQ MYM SIL |
| FOMC | all 47 |
| CPI (cpi: true) | GC HG MBT MGC MHG MNQ NQ SI |
| WPSR | CL MCL QM RB (F6.4), plus 6C (K8-oilcad-01), HO, NG (K4-cp3-01) |
| NGS | NG QG MNG (F6.4 and micro), plus CL MCL RB HO (K4 members) |
| CROP, CROP_ANNUAL, WASDE | ZC ZS ZW ZM ZL, plus HE LE (K6-cp2, K6-cp3, K6-limitcont) |
| PPI | MBT |
| ISM_SERVICES | MNQ NQ M2K RTY MYM YM ZN ZB |
| G17 | GC MGC SI HG MHG |
| API_WSB | CL MCL |
| CROP_PROGRESS | ZC |
| TREASURY_AUCTION | ZT ZF ZN TN ZB UB (every tenor in the source) |

## Files created (all new; no existing file modified)

- `screening/build_release_calendar.py` (702 lines): constants and rulings, input loading with hash pins, the F6.4
  parse, micro siblings, product universe, word to exposure to roots, member-named products, release products,
  assembly, write-once, `build`, CLI (`python -m screening.build_release_calendar [--check]`).
- `screening/build_release_calendar_checks.py` (196 lines): source checks (DRAFT marker, coverage window, coverage-table
  arithmetic and recount), quote and instant verification, evidence-quote verification. Split out to keep the main
  module under 800 lines. The main module re-exports every name in it.
- `screening/build_release_calendar_md.py` (154 lines): the .md renderer (imported lazily inside `build`).
- `tests/test_build_release_calendar.py` (43 tests).
- `reports/stage_e2b_release_calendar.json` and `.md` (outputs); this report.

The brief listed `screening/build_release_calendar.py` as the module. The two helper modules are new files that nobody
else owns. harness_freeze's import-closure walk (ast.walk, which also sees function-level imports) should pick them up.
The harness freeze already lists `screening.build_release_calendar` in ENTRY_MODULES and `test_build_release_calendar.py`
in TEST_PATTERNS.

## How the build works (what the code encodes)

- Inputs are pinned by hash. Topstep facts, liquidity and catalog are checked against reports/stage_e1_freeze.json.
  The vehicles file is checked against `screening.stage_e_frozen.E2A_TABLES["vehicles"]`. The E.2b source files and
  names file are hashed into `inputs`.
- F6.4 is held verbatim in `F6_4_QUOTE`. The build requires the facts file's quote to match it exactly, and the note
  must contain "**Micro contracts also apply.". The quote is parsed into rows by a regex that must tile it exactly.
  Row to release code: Unemployment Rate = NFP, FOMC Statement = FOMC, Crude Oil Inventories (EIA) = WPSR, Natural
  Gas Inventories (EIA) = NGS, Crop Production = CROP and CROP_ANNUAL (lead ruling).
- Micro siblings: roots in rules/products.py with the same `exposure` field and contract_type MICRO or SIL. Examples:
  NQ gives MNQ, ES gives MES, SI gives SIL, CL gives MCL, NG gives MNG, 6E gives M6E. The rule applies to every F6.4
  row, including FOMC's "All products", which is how MES gets FOMC (as ES's micro sibling).
- Product universe: admissible contracts, vehicles and contracts from vehicles.json, plus liquidity products, plus
  ML PRICE_PATH_CONTRACTS. That gives 46 roots in the product table plus 6M, MET, NKD, PL outside it.
- Member-named releases: extraction rows are cross-checked field by field against the frozen catalog
  (exposures = read_products, starred_products = traded_products, status). Each catalog exposure word maps to its
  vehicles.json exposure, then to {vehicle, ML price-path root}. The word match is by exposure name, by an exposure's
  only admissible root, or by an alias (crude = WTI crude, gas = Henry Hub gas, from catalog_K4.md line 65). An
  unknown word, an unknown release name, or a starred product outside the member's exposures is refused.
- Excluded by ruling, with their naming members listed in the .md: ECB fix, London 4pm fix, Tokyo fix, LBMA AM and PM
  auctions, CME CF BRR.
- Checks. Each source's log must not contain "STATUS: DRAFT". Coverage must be exactly 2019-05-01..2026-06-21. Every
  coverage-table row must satisfy expected = found + unverified + cancelled, and those counts must recount from the
  entries and the cancellation records. Year attribution uses originally_scheduled, or reference_period when the
  former is "[unverified]" (G17). Every quote must match its saved page verbatim after whitespace normalisation
  (strict UTF-8). Every instant must equal date + time_local in tz (a DST-gap local time fails). Ids must be unique,
  dates inside coverage, every release on the lead's list must have entries, and every release must have at least one
  product. Each exposure's vehicle and price-path root must carry identical instant sets (ml_route's
  ReleaseListMismatch condition). Finally the runner's loader is run on the built dict.
- Output entries keep id, release, release_name, date, time_local, tz, instant_utc, products, cpi, evidence
  (verified / unverified / announced_schedule), source {file, url, saved_path}, and a note for non-verified entries.
  Also recorded: `shared_instants` (85 groups; the CROP, WASDE and January CROP_ANNUAL ids share an instant, per the
  lead's ruling 2), `release_products` (composition, naming members by status), `word_to_roots`, `f6_4`,
  `product_universe`, `excluded_by_ruling`, `known_gaps`, `cancellations` and `verification`.

## Tests: tests/test_build_release_calendar.py, 43 tests (33 functions, one parametrized 10 ways)

- Frozen inputs (1): a changed liquidity byte, or a manifest without the catalog's sha256, is refused.
- F6.4 (4): parses into its 5 rows (28 Unemployment roots, All products, the "9:30 AM / 10:00 AM*" time, Crop
  Production to CROP and CROP_ANNUAL); text that does not tile is refused; the frozen facts file carries the encoded
  quote; an altered quote or a missing micro note is refused.
- Product mapping (5 functions, 14 tests): micro siblings from the product table (QM and E7 are E-minis, NKD unknown);
  universe split (46 in the table, 6M MET NKD PL outside); 10 word-to-roots cases; an unknown word is refused; the
  extraction matches the catalog, and a changed field is refused.
- Rulings (3): a member-named release with no ruling is refused; excluded fixes add no products; release products
  follow OC-N on the real inputs (FOMC = all 47; NFP includes the micros and none of NKD, GE, 6M, MET; CPI, PPI,
  CROP_PROGRESS, TREASURY_AUCTION, WPSR and the grain releases as in the table above).
- Synthetic assemble (2): [unverified] and announced entries are kept and counted; cpi is set only on CPI; the output
  is sorted; shared instants list all three ids and the loader de-duplicates per root.
- Refusals on synthetic sources (13): quote missing from its page; instant not equal to date + time + tz; DST gap and
  non-Z formats; an expected release neither found, unverified nor cancelled; a coverage table the entries do not
  reproduce; a DRAFT log; a different coverage window; a release in the wrong source; a listed release without
  entries; duplicate id; date outside coverage; missing cancellation evidence quote; saved_path with ".."; unknown
  evidence_kind; vehicle and price path with different instants.
- Writing (3): write_once makes the file read-only and refuses to overwrite; main writes both files, `--check` says
  identical, a second build returns 2; a refused build writes nothing.
- Real sources (2; skipped when the git-ignored pages or the written file are absent): the real build gives
  2609/2609 quotes and instants, 365 NGS unverified, 372 API announced; both loaders read the result (ml_route
  `event_calendar_from_release` gives NQ the MNQ vehicle's list); the written file loads via `load_release_calendar()`
  and `load_event_calendar()`, and the training window is covered.
- Line coverage (`coverage run`): build_release_calendar 95%, _checks 92%, _md 100%, 95% overall. pytest-cov itself
  fails here with numpy's "cannot load module more than once"; `python -m coverage run` works.

## Commands run (results)

- `uv run --no-sync python -m pytest -q tests/test_build_release_calendar.py`: 43 passed (0.97 s).
- `uv run --no-sync ruff check screening/build_release_calendar*.py tests/test_build_release_calendar.py`: all
  checks passed.
- `uv run --no-sync python -m screening.build_release_calendar` (17:08): wrote both files. Summary: entries 2609,
  unverified 365, announced 372, roots 47, cpi 85. A second run is refused ("written once and never overwritten").
  `--check`: identical (run twice, the second after the last code edit).
- Through `reports/stage_e2b_briefs/heavy.sh`: `pytest tests/test_ml_route_stage_e_inputs.py tests/test_stage_e_rules.py
  -k "calendar or release or event"` gave 13 passed; `pytest tests/test_cross_platform_static.py` gave 6 passed.
- Consumer tests that expected the calendar to be absent (test_stage_e_runner.py:150,
  test_ml_route_distil_entry.py:129) use tmp roots, so the written file does not affect them. Not run (full suite
  is the lead's).

## Deviations and readings (for the lead)

1. Roots outside the product table are dropped, not written. The loader calls `rules.products.product(root)` on every
   root and would raise UnknownProduct (not ReleaseCalendarMissing). F6.4's NKD, GE, 6M, MET and the universe's
   6M, MET, NKD, PL are therefore listed in the output and the .md, not written. None of them has a product row, so
   the engine cannot trade them. This is a schema constraint, not a schema change.
2. Member status: every catalog status counts (active, excluded_by_lead, excluded_superseded_ml_route). Without the
   superseded ML members, PPI (named only by K7-ml-01) and Crop Progress (only K6-ml-01) would concern no product,
   and the lead's list includes both. The .md shows naming members by status per release. If the lead wants active
   members only, PPI and CROP_PROGRESS would have no products and the build would refuse by name.
3. Starred products that are neither vehicle nor price path (SIL, M6E, M6A) are not added by the member-named rule.
   They still get NFP and FOMC through F6.4's micro rule. Silver has no vehicle, so SI (price path) gets CPI and G17
   and SIL does not.
4. MES, the D1.5 leg that is never traded in Stage E, gets NFP and FOMC as ES's micro sibling.
5. No harness preflight in the builder. It reads no bar, and the harness manifest lists the calendar as a frozen
   input, so the builder has to run before the freeze. `--check` can confirm the file after the freeze.
6. Outlier times are kept as sourced: WPSR-2024-12-27 at 13:00 and WPSR-2025-12-29 at 17:00 (EIA holiday schedule;
   the 2025 date comes from the current schedule page), TREASURY_AUCTION-2019-12-24-5Y at 10:00, CROP_PROGRESS-2021-04-05
   at 17:00. All passed quote verification.

## Open questions

- None block the file. Readings 1 and 2 are the ones to confirm; either would change products, not instants.

## Unfinished

- Nothing in the brief. Not done (outside my scope): independent fable verification of the calendar, and the
  full test suite run.
