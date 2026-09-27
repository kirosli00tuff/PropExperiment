# Brief: CalendarAssembler-OpusXHigh (worker-xhigh on opus) - the release calendar file (lead ruling OC-J)

Objective: build and test the assembler that turns the sourced release lists into reports/stage_e2b_release_calendar.json
in the schema the runner already reads, run it on the real source files, and verify the result.

Read: reports/stage_e2b_briefs/00_common.md and g1_release_common.md (binding); screening/stage_e_rules.py lines 90-190
(RELEASE_CALENDAR_PATH, schema "stage_e_release_calendar/1", ReleaseCalendar, release_calendar_from_dict,
load_release_calendar; do not change the schema without telling the lead); reports/stage_e0_topstep_facts.json fact F6.4;
the source files reports/stage_e2b_release_sources_macro.json, reports/stage_e2b_release_sources_commodity.json and, if the
lead lists it, reports/stage_e2b_release_sources_named.json; reports/stage_e2b_release_names.json (member-named releases).
The product universe: every root in reports/stage_e2a_vehicles.json, reports/stage_e0_liquidity.json and the ML route's 31
price-path contracts (ml_route's frozen inputs), read-only.

Build screening/build_release_calendar.py (+ tests/test_build_release_calendar.py):
- product mapping per release from F6.4's table verbatim, plus "**Micro contracts also apply" (each listed root's micro
  siblings, from rules/products.py's product families; cite the mapping in the module), FOMC to "All products" (every root
  of the universe above), plus the member-named releases the lead rules in (a lead list you will receive; until then
  none). CPI entries carry "cpi": true (D9.12) and concern the products the lead lists (default: none beyond the CPI
  window's use; the CPI window itself reads cpi instants for every product).
- every entry keeps its id, instant_utc, products, cpi flag and source (url + saved_path); [unverified] entries are kept
  (dropping them would understate the event-window cost) and counted in the output's "verification" block.
- coverage first 2019-05-01, last 2026-06-21; the assembler refuses if any source's coverage table shows an expected
  release neither found, unverified nor logged as cancelled.
- a verification step re-checks every quote verbatim (whitespace normalised) in its saved page and every instant against
  date + time + tz; any failure refuses the build.
- output written read-only, refusing to overwrite; a summary reports/stage_e2b_release_calendar.md (counts per release x
  year, per product, unverified, cancelled).
Run it once the source files exist (wait by polling every 60 s for up to 60 minutes if they do not; build and test the
code first). Report: reports/stage_e2b_g2b_calendar_worker.md. Reply with path, summary <= 200 words, anything unfinished.
Ownership: screening/build_release_calendar.py, its tests, reports/stage_e2b_release_calendar.json and .md.

## Lead list (ruling OC-N, 13:52 PDT) - which releases, and which products each concerns
Sources: reports/stage_e2b_release_sources_macro.json (NFP, CPI, FOMC), reports/stage_e2b_release_sources_commodity.json
(EIA WPSR, EIA gas storage, Crop Production, WASDE), reports/stage_e2b_release_sources_named.json (PPI, ISM Services,
G.17, API bulletin, Crop Progress, Treasury auctions).
- F6.4 releases (Unemployment Rate = Employment Situation, FOMC, Crude Oil Inventories = EIA WPSR, Natural Gas
  Inventories = EIA gas storage, Crop Production): the products F6.4 lists, each listed root's micro siblings
  ("**Micro contracts also apply"), FOMC = every root of the universe; PLUS the member-named products below.
- Member-named releases (reports/stage_e2b_release_names.json): a release concerns every product TRADED by a member that
  names it (signal or mentioned), mapped from the extraction's exposure words (gold, EUR, Nasdaq-100, crude, ...) to the
  frozen vehicle root and the ML price-path root of that exposure (reports/stage_e2a_vehicles.json and ml_route's frozen
  price-path list); write the word -> roots mapping table into the .md summary. This adds CPI, PPI, ISM Services, G.17,
  API bulletin, WASDE, Crop Progress and Treasury note/bond auctions (all tenors in the source file: the union over the
  naming members) to the products of their naming members, and adds named products to F6.4 releases.
- CPI entries also carry "cpi": true for D9.12 (the CPI window reads the cpi instants for its own product list).
- Kept and counted, not dropped: entries marked [unverified] and the API bulletin's "announced_schedule" entries (dates
  from API's announced schedule, publication not confirmed).
- Excluded by ruling (not releases of information, and daily, so already inside E.2a's time-of-day cost buckets): ECB
  fix, London 4pm fix, Tokyo fix, LBMA auctions, CME CF BRR. List them in the .md as excluded with the reason.
- Known gap to list in the .md: G.17's 2025-11-24 annual revision not entered.
