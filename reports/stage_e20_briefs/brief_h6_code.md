# Brief: H6Coder-OpusXHigh (Stage E.20 Step 2, the h6_rod package)

One objective: build a new package `h6_rod/` and its tests that implement
`reports/stage_e20_prereg_H6.md` (the H6 pre-registration, DRAFT) exactly, on synthetic data only.
The lead wrote the text from docs/prompts/STAGE_E.20.md F5 (lines 122-155); read both. Where the
text cannot be implemented as written, or leaves a choice open, STOP that item and report it to
the lead with options; do not decide a rule yourself.

## Inputs (read by section: grep, line ranges; never whole large files)

- The rule: reports/stage_e20_prereg_H6.md; docs/prompts/STAGE_E.20.md F2, F3, F5.
- CP1's conventions, which H6 copies (bar named by its CT open minute; intent at a bar's close
  fills at the next bar's open; entry on the bar opening at C-31; exit on the first present bar at or
  after C-2; both signal bars present with one instrument_id): strategy/members/k1/cp1.py and
  strategy/members/k1/_port_common.py (exit_if_due, leg_facts). Copy structure; never import from
  a member module, never edit it.
- The frozen engine, called unchanged: screening/stage_e_engine.py (run_engine, restart_on_terminal,
  check_mll, the forced flatten incl. early close F = early close - 15 min), screening/stage_e_rules.py
  (StageERules, ReleaseCalendar, the roll-blackout refusal), screening/stage_e_frozen.py (D8 costs:
  ProductCosts, slippage, leg_inputs), rules/ (XFA 50K).
- How the program already runs the frozen engine on the E.12 step2 stores with the NQ price path
  and the MNQ vehicle: ml_route_v2/phase1/ (world.py, build.py, _io.py: the frozen store loader with
  its L-3 booking check, the D4 roll-blackout sets in world.blackout), ml_route_v2/pipeline.py
  own_blackout, ml_route_v2/simulate.py (PortfolioRules, a StageERules subclass, and its test that
  a single-product portfolio reproduces the frozen StageERules run fill for fill),
  ml_route_v2/engine_stage.py. Use the same loader and the same engine entry; do not reimplement fills
  or costs.
- The statistic: ml_route_v2/gate0.py `_b_test`, `p_value`, `date_t` (call `_b_test` itself).
- The registry: screening/trial_registry.py (its API and test mode). Patterns for the freeze check,
  the registration check and the run-once marker: base_rules/guards.py, c1_replication/guards.py,
  c1_replication/c1b.py (MARKER_PATH), base_rules/run.py.
- Calendars: data/calendars/equity.py and data/group_session.py (equity trade dates, previous trade
  date, early halts and their times).
- GEX (T3 only): reports/stage_e14_briefs/gex/DIX.csv's header is `date,price,dix,gex` (E.14
  fetch record in reports/stage_e14_briefs/gex/fetch_record.txt). Do NOT read that file's values;
  write the loader and test it on a synthetic CSV only.

## Package (suggested layout; keep files small and focused)

- `h6_rod/constants.py`: every literal: the NQ store path and sha256 (prereg section 2), windows
  (verdict 2020-06-01..2024-02-29, overlap 2019-05-06..2020-05-29, warm-up 60 trade dates), the
  entry and exit minute offsets (31, 2), trade floors (100; 30 for T3), Holm family alpha 0.025,
  cost multiple 1.5, Sharpe bar 0.5, annualization 252, registry label `E20-H6` and ids
  `E20-H6-T1`, `E20-H6-T2`, `E20-H6-T3`; `T3_REGISTERED = None` (the lead sets True or False before
  the freeze; every entry point refuses while it is None); the GEX CSV path and sha256 (lead fills
  at the freeze); the marker path `reports/stage_e20_H6_RUN_ONCE.json`; the freeze manifest path
  `reports/stage_e20_h6_freeze.json`; result paths `reports/stage_e20_H6_result.json` and `.md`.
- `h6_rod/guard.py`: the F3 read guard, imported by every h6_rod entry point. (a) A path check the
  loader calls before opening anything: the only store it may open is the NQ step2 file; refuse any
  path under data/processed_hist/, data/sealed/, any holdout store (take the sealed and holdout
  paths from data/holdout.py rather than retyping them), and any other root's store. (b) Defense in
  depth: a `sys.addaudithook` hook that refuses Python-level `open` of those prefixes. (c) A bar
  check after load: any bar with ts or trade_date on or after 2024-03-01 raises. Planted-case tests
  for each.
- `h6_rod/signal.py`: pure functions: per-date facts (P(prior C) bar, P(C-30) bar, their
  instrument_ids, C for the date incl. early close), r_ROD, eligibility with the prereg's reason
  codes, T2's thresholds under section 2's warm-up rule (strict >; only eligible dates in the
  allowed range; fewer than 60: no threshold, reason "t2_warmup"), the T3 mask (the GEX row dated
  the previous equity trade date; strictly negative; missing row: "gex_missing"; rows on or after
  2024-03-01 never loaded).
- `h6_rod/member.py`: the engine member: market intent on the bar opening at C-31 per a per-date
  side schedule (T1, T2, T3 each a schedule), exit as CP1 (first present bar at or after C-2,
  resent while refused); the engine's flatten and D9.7 are the backstops.
- `h6_rod/stats.py`: per-trade gross, c and net in MNQ ticks and dollars from the engine's trip
  records; `_b_test` on (trade_date, g_ticks = net, cost_ticks = c); Holm step-down at 0.025 over the
  registered tests; the annualized net Sharpe over every equity trade date of the window with zeros
  on no-trade dates (ddof 1, sqrt 252); the pass bar; descriptive outputs of prereg section 6
  (per year, 1.5 x slippage re-pricing from each trade's cost components, bp of entry price, exit
  types, refusal and exclusion counts, MLL breach dates, the overlap window).
- `h6_rod/run.py` and `h6_rod/__main__.py`: `python -m h6_rod check | register | evaluate`.
  check: harness preflight (screening.harness_freeze, expected v12
  ece91ae8e6993ad3c64412d30cc0b6ff6a4af07a15a6956ce9f2927f7ea70d32), the H6 freeze manifest (sha256
  passed on the command line; every h6_rod file and every input listed), the store's sha256, no
  marker, T3_REGISTERED not None. register: one registry line (label E20-H6, the ids per T3's status,
  the freeze manifest sha256); refuse a second registration. evaluate: refuse unless registered with
  this freeze sha256 and no marker exists; write the marker first; then load, compute the schedules,
  run the engine once per test, write the result files. After the marker, no data condition raises:
  it is excluded and counted (E.16 ruling R-B3); every input problem is detected by check, before the
  marker.
- Tests `tests/test_h6_rod_*.py` (synthetic bars only, built in the tests; never open data/processed*
  or the GEX file): the signal on a normal day (hand-computed r_ROD); the C-30 entry fill and the C-2
  exit fill (incl. a missing 14:58 bar: exit on the next present bar); a shortened day (C = early
  close; entry at early close - 30; exit at the engine's flatten F); each no-trade reason (missing
  prior-C bar, missing C-30 bar, instrument change, zero signal, engine refusal on a roll-blackout
  date); T2's warm-up and strictness; T3's mask incl. a missing GEX row and a post-2024-02-29 row cut
  at load; every guard case raises; `_b_test` wrapper against a hand-computed t; Holm cases; Sharpe
  with zero days; one engine round trip whose cost equals the D8 table's commission plus the two
  bucket slippages to the cent; run-once (a second evaluate refuses; evaluate before register
  refuses; any registry write in tests goes to a temporary registry in test mode, never
  ledger/trial_registrations.jsonl).

## Output

- The package and tests, plus `reports/stage_e20_briefs/h6_build.md`: a table mapping every clause
  of prereg sections 2-6 and 9 to the function that implements it, your choices (each with its
  reason), the test list with the `uv run pytest -q -p no:cacheprovider tests/test_h6_rod*.py` result,
  and every item you stopped on.
- Reply to the lead: the path, a summary of at most 200 words, and anything unfinished.

## Boundaries

- No real data: do not open any store, the GEX CSV's values, or any result file of E.12 Gate 0,
  E.15, E.17 or E.18.
- Do not edit any existing file: screening/, rules/, sim/, ml_route_v2/, data/, base_rules/,
  c1_replication/, strategy/, the prereg (send text issues to the lead), tests of other packages.
- No writes to ledger/ (registry or spend), no commits, no Databento, no TopstepX. Run only the
  h6_rod tests (a full suite run is in progress; do not start another), at `nice -n 10`.
- Do not spawn agents.
