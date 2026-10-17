# Stage E.23 code review (CodeReviewer-FableXHigh), before registration and before any outcome read

Reviewer: Fable 5.1 at xhigh, independent of BookCoder (Opus) and TriggerCoder (Opus). Lens: the code line by
line, `trigger_hold/*.py` and `tests/test_trigger_hold_*.py`, against reports/stage_e23_briefs/lead_spec.md
(sections 0-8 and R) and the frozen code it reuses (multiday/, base_rules/, screening/stage_e_verdict.py,
screening/trial_registry.py, the Stage E engine and bars loaders, strategy/members/k2/monthend.py, h6_rod/,
pattern_search/backward.py). Freeze sha256 3fdd98d74cae1c618e98438b5308ca7c38b10339f1c1037ce2b92a7ab6c921c7
verified (`trigger_hold.freeze_manifest verify`: 20 inputs, 5 ids, rc 0). Design and registration are the
RegReviewer's; this file grades code.

What I ran (read-only; no `evaluate`, no marker, no book on real bars, no registration, no file edited):
`uv run pytest -q -p no:cacheprovider tests/test_trigger_hold_*.py` at nice 10: 93 passed in 5.19 s; the freeze
verify above; an in-memory recomputation of the power table from the frozen config, events, calendars and store
metadata (`trigger_hold.run.power_table`, no bar row, nothing written) compared field by field with
reports/stage_e23_power.json: 0 differences, `events_sha256` equal; a tabulation of the decision instants in the
eight events files (CT clock time, and tau's CT date against d0); the code sha256s recorded inside the events
files against the current trigger_hold files (all equal); the ledger's last line (E22, n_after 533, no E23
entry); REGISTRATION.md 0 bytes.

## Verdict: APPROVE WITH FIXES

No BLOCKING finding. One SHOULD FIX (a run-discipline gap in the test mode, inherited from multiday.run), the rest
NOTEs. I found no look-ahead in the entry timing, the sizing or the eligibility, no price or exit information in
the events files, and the statistics wired as the spec says.

## Findings

| id | grade | file:line | what | concrete failure | fix |
|---|---|---|---|---|---|
| C-01 | SHOULD FIX | trigger_hold/run.py:113-131, 139-153 | The test mode (`--input-paths <json>`) is entered by the mere presence of the flag; with an empty object `{}` every input role stays the freeze's real file (the real run manifest, so the real stores), while `--registry`, `--marker` and `--out-dir` may be any path (`_fixed_paths`, `BG.check_registry_path(..., test_mode=True)`). `FM.verify` only requires that an override be a file of the freeze, which the real inputs are. | A deliberate `evaluate --phase discovery --input-paths empty.json --registry <a test ledger holding the 5 ids under E23 and this sha> --marker /tmp/m --out-dir /tmp/o` computes the real W_ext books on the real stores and writes them outside reports/, with no marker at reports/stage_e23_RUN_ONCE_discovery.json. The run-once invariant (section 8: "writes the marker ... BEFORE any bar is read; a second run is refused") then holds only by operator discipline. multiday/run.py:93-112 has the same structure, so this is inherited, not new. | One guard in `preconditions`, after `inputs` is known: `if test_mode and Path(inputs["run_manifest"]["path"]).resolve() == K.repo_path(K.RUN_MANIFEST_PATH).resolve(): raise Refused("the test mode must name another run manifest (no real store in test mode)")`. tests/test_trigger_hold_run.py stubs `pre_fn` and never enters `preconditions`, so no test changes. The edit changes the freeze: rebuild reports/stage_e23_freeze.json (delete and `build`; nothing is registered yet) and re-verify. If the lead rules it a NOTE (E.21 ran with the same pattern), record the reason in the return. |
| C-02 | NOTE | trigger_hold/units.py:151-153 | Window membership is tested on the event's d0 (`window.holds(e.d0)`) before d_e is derived; the spec (section 1) assigns a unit by its entry and exit MARK dates and excludes "a unit with entry before the window start". | An event on the trade date before the window start whose tau is at or after S (so d_e = the window's first mark date) is excluded as "event outside the window" although its d_e is inside; symmetrically none at the end (d_x would be outside anyway). No effect on the registered set: every event's tau is 07:21 CT (K2, S = 14:00) or 14:30 CT (H6, S = 15:15 to 2020-10-25, 15:00 after), so d_e = d0 for all 2,000 events (the power table shows no "entry moved to the next mark date" count, and my tabulation confirms tau < S everywhere). | Either test `window.holds(d_e)` only (drop the d0 test, keep the exit tests), or leave it and state the rule in the return as "events with d0 inside the window". No number changes for E.23. |
| C-03 | NOTE | trigger_hold/evaluate.py:141-151 with reports/stage_e23_power.json | With the frozen power table every W_cf row has power_gate 0.178-0.182 < 0.2 at hurdle 2.0; `confirmation_hurdle(S) >= 2.0`, so `confirmation_gate` returns INCONCLUSIVE BY DESIGN for every possible survivor. | The confirmation phase, if run, writes its marker and a result in which no trigger-hold is read; a PASS is impossible on this freeze. This is the design the prereg declares (its power table says the same), not a code error; the code does what section 7 says (reads nothing for a gated row: `_read` is called with an empty id list, `read_root` is never entered). | None in code. The lead's return should say so before the discovery read, so it is not learned from the confirmation output. |
| C-04 | NOTE | trigger_hold/run.py:136-138 | `preconditions` checks the power table's schema and that its row ids equal the config's, not that its recorded `events_sha256` equal the frozen events files, nor `config` sha256. | A power table computed from earlier events files, then frozen together with regenerated events, would pass the preconditions (the freeze pins both files but not their mutual consistency). Verified consistent today: my in-memory recomputation matched the frozen table on every field (0 diffs) and `events_sha256` equal. | Optional hardening (changes the freeze): compare `power["events_sha256"][p]` with the freeze's sha256 of each config events path, refuse on mismatch. Not needed for this freeze. |
| C-05 | NOTE | trigger_hold/book.py:215-217; trigger_hold/evaluate.py:74-76 | The trend regressors are projected on the unit book's series dates (`regressor_on(trend, dates)`); a T1/T2 value booked on a non-mark date (a roll leg filled on a trade date without a mark) is dropped unless the unit book also booked on that date (then `daily_series` adds the date). | A negligible misalignment on at most a handful of roll dates per root over 8 years; it cannot create alpha (it drops regressor variance, it does not shift y). | None required; mention in the return. |
| C-06 | NOTE | trigger_hold/units.py:178-180 (lead ruling R1) | Exit eligibility (`action_why(d_x)`) is a condition on bar existence and the calendar at d_x, h mark dates after the entry: a unit is kept or dropped on information about a future date (whether a bar exists, a blackout, an early halt). | Not a price condition, so no look-ahead into returns; it is a calendar/existence filter the lead accepted (R1, as E.21 T3 did). On W_ext it removes 92-93 H6 units (roll blackout) and 2 K2 units per root (early halt). | None. |
| C-07 | NOTE | trigger_hold/freeze_manifest.py:54-57 | The freeze lists trigger_hold, its tests, multiday, base_rules, trial_registry and stage_e_verdict, but not tests/test_multiday_world.py (imported by the trigger_hold tests), nor the member code the events came from (h6_rod/, pattern_search/backward.py, strategy/members/k2/, the Stage E engine). | The member code is pinned indirectly: each events file (frozen) records the sha256 of every h6_rod file, backward.py, the member module, the cluster freeze and the harness freeze (I checked that the recorded trigger_hold code sha256s equal the current files). A later change to test_multiday_world.py would change what the trigger_hold tests exercise, not the production code. | None required; the return can state the indirect pinning. |
| C-08 | NOTE | trigger_hold/book.py:38-43 (lead ruling R3) | Stress per side = commission + 2 x (base - commission) = commission + 2 x ceil(slippage ticks x tick value); ceil(2 x ticks x tv) would be up to 1 cent lower per side. | Matches R3 as written; conservative by at most 1 cent per side. | None. |
| C-09 | NOTE | reports/stage_e23_briefs/triggercoder_report.md section 8 | TriggerCoder's first-pass events files carried the engine's exit-side counters (forced flattens, MLL liquidations) for about five minutes before being scrubbed and regenerated; the event lists did not change. | Not a book outcome, no price or P&L; the final files hold only `d0, tau_ns, side` per event and integer counts. Already disclosed to the lead. | None. |

## Checked and found correct

Entry timing and look-ahead (units.py, lead_spec 2, R7).
- `entry_mark_date`: d_e = d0 iff tau_ns < the UTC instant of CT minute S_i(d0) (`ct_ns(d, S)`), else the first mark
  date after d0 (`bisect_right`). MK's fill instant is S in both R-B1 cases (open of bar S, or close of bar S-1 at a
  closure), so the comparison is against the fill instant; the test asserts `settle_open_ns(d0) == marks[d0].ts`.
  tau at exactly S goes to the next mark date (strictly after). A d0 without a settlement minute goes to the next mark
  date (R7).
- The trigger day's intraday P&L is never counted: the unit's P&L is the frozen path's increments on (d_e, d_x]
  (`simulate_book` books `iv.increments` from MK(d_e) on; `book.gross` has nothing before the open fill). The test
  `test_exit_is_the_hth_mark_date_and_a_missing_mark_carries_the_pnl` checks gross = n x (MK(d_x) - MK(d_e)) x tv
  with a missing mark carried.
- Real events: K2 tau = 07:21 CT on every event (the 07:20 decision bar's close; member rule O = 07:20), rates S =
  14:00 CT in both eras; H6 tau = 14:30 CT on every event (the C-31 bar's close, C = 15:00), NQ S = 15:15 CT to
  2020-10-25 and 15:00 after. tau's CT date equals d0 on all 2,000 + 2,000 events. So d_e = d0 everywhere and the
  entry is 6h39m (K2) or 30-45 min (H6) after the decision, at the settlement mark.
- Side: s from the member's fill side (buy +1, sell -1); u = s x m with m from the config (+1 K2, -1 H6), fixed
  before the read. Sigma(i, d_e) is `ewma_sigma_before` on returns dated strictly before d_e (frozen E.21 code);
  V uses MK(d_e), the fill price itself. No W_cf mark, sigma or path is computed in discovery (`ctx.last =
  2019-04-30`, R6; marks, returns, sigma and rebalances all stop there).
- Eligibility: `action_why` in full on d_e (R2) and d_x (R1); every exclusion is a calendar or bar-existence fact,
  counted by reason; nothing reads a price (BarMarks reads mark existence only; CalendarMarks reads calendars, the
  settlement table and store metadata).

Netting, flips, sizing (book.py, lead_spec 3).
- `net_path`: clip(sum u, -1, 1) after the fills at MK(d); an order only where net changes; 0 -> +-1 open, +-1 -> 0
  close, +-1 -> -+1 flip (one fill of the difference, sized at the flip date); a same-side overlapping unit trades
  nothing and extends the hold; opposite units net to 0 (tests cover each). n = net x 0.40 / sigma / V, divisor 1
  (the T3 `divisor_at` parameter is test-only); undefined or zero sigma or non-positive V: target 0, counted.
- The T3 reproduction (the only real-bar run of the unit engine before the freeze) matches the frozen t3_orders +
  simulate_book bitwise on NQ (154 units, 308 fills) and RTY (73, 146) and the published T3 series (3,319 dates,
  max |diff| 0.0): reports/stage_e23_briefs/tmp_bookcoder/t3_reproduction.json `passed: true`.

Rolls and costs (book.py 34-63, lead_spec 0, R3).
- `prepare_root` = frozen `process_root` with `E23VehicleCost` plus a fill cost for every mark date (same
  `fill_cost(bars, vc, ctx.releases, pt[0], pt[1], locks)` call as process_root). Roll legs, roll fill guards, limit
  lock diagnostics and event-window costs come from the frozen path (`_interval`, `RollLeg`) with the same vc, so
  every fill (open, close, flip, roll_out, roll_in) carries base = D8 unchanged (test: equal to the default
  VehicleCost on every fill date) and stress = commission + 2 x (base - commission). `daily_series` and
  `book_summary` report `K.CASES = (base, stress)` only; slip150 is computed by the frozen code and never reported.

Windows, boundaries, series dates (units.py, lead_spec 1).
- W_ext = max(2011-07-27, first mark) .. 2019-04-30; W_cf = max(2019-05-06, S_X) .. 2024-02-29 (S_X null for all 5
  rows). A unit needs d_e and d_x inside the window, the same store era (`era_of`), and an h-th mark date; each
  failure counted. Series dates: the root's mark dates inside the window from the first unit's d_e on
  (`book_days`), zero when flat; a value booked on a non-mark date inside the span adds that date, counted; a value
  outside the span raises (none can occur: every unit closes on a window mark date).
- Events are extracted from 2011-06-01 so the K2 June 2011 and H6 June-July 2011 events exist and are excluded by
  the window test (2 per K2 root, 36 for H6: the power table's counts), as section 1 says.

Trend regressors and the regression (trend.py, stats.py, lead_spec 0 and 4).
- v_T1, v_T2 per root recomputed by the frozen E.21 code under the verified E.21 freeze (`MFM.verify`
  0bb899e5...), e21_starts, lock_rule, process_root, t12_orders, simulate_book; `check_sum`: the sum over the 17
  roots equals T1_result.json and T2_result.json `series.base` on all 3,205 dates, max |diff| 0.0, 0 values off the
  series; written into every root file; `load_trend` refuses an unchecked file (ZF and NQ files inspected: `check`
  passed, 3,130 and 3,113 booked dates, 2011-07-29..2024-02-29).
- Alignment: y and both regressors on the same list `dates` (the book's series dates), zero where the trend book
  is flat (a flat T1/T2 date has no booking; an in-position date always has one, so zero-fill is only used when
  flat).
- HAC: `hac_sandwich` is (X'X)^-1 S (X'X)^-1 with S = sum e^2 x x' + sum_{l<=min(h,n-1)} (1 - l/(h+1)) x (G_l +
  G_l'), G_l = sum_t e_t e_{t-l} x_t x_{t-l}': Bartlett with lags h, the kernel and normalization of
  `base_rules.stats.newey_west_se` (with no regressor the two are equal to 1e-15, tested; an independent pure-Python
  loop implementation agrees to 1e-10 at lags 1, 5, 20). Plain se = s^2 (X'X)^-1 with s^2 = e'e/(n-3). p_alpha =
  max(one-sided Student p of the plain t with n-3 df, one-sided normal p of t_NW). Rank deficiency or n <= 3 ->
  undefined (p None, counted in Holm's m). Raw stats: mean, sd ddof 1, Sharpe x sqrt(252), t, NW t with lags h.

Holm, survivors, DSR, PBO, confirmation (stats.py, evaluate.py, lead_spec 7, R8, R11, R12).
- `holm05` = base_rules.stats.holm at 0.05 one-sided over every registered trigger-hold (None for inconclusive or
  store-refused rows: never rejected, counted in m). Survivor = Holm rejection AND alpha t_NW >= 2.0 AND base net
  Sharpe >= 0.3; ranked by alpha t_NW desc, base Sharpe desc, id asc; cut at 4; `screen_row` takes the BASE case's
  `alpha.t_nw`, `alpha.p_alpha`, `raw.sharpe`. `survivors_from` re-derives the list from the discovery file and
  raises if it differs.
- DSR descriptive: `dsr_at_n` over the read discovery base series at n_trials = `current_n(ledger)` (533 + 5
  after registration). PBO: `stage_e_verdict.pbo` on the K series aligned on the union of their dates, zero off
  own dates, 8 contiguous blocks of n // 8 dates.
- Confirmation: `confirmation_gate` -> UNCONFIRMABLE when no W_cf events file, no W_cf power row or n_dates 0;
  INCONCLUSIVE when nonoverlapping < 30 or power at b = max(2.0, z_{1-0.05/S}) < 0.2; only "read" ids reach
  `_read`, which loads a root only when it has an id to read, so a gated row reads nothing. Verdicts: Holm over
  all S survivors (gated with p None), then t_NW >= 2.0, base Sharpe >= 0.3, stress Sharpe > 0, DSR > 0.95 (Sharpe
  variance over the read discovery series, Q4), PBO (discovery) < 0.5; PASS / NULL / INCONCLUSIVE BY DESIGN /
  UNCONFIRMABLE ON OWNED DATA; a store-refused root -> UNCONFIRMABLE (R12).

Run discipline (run.py, freeze_manifest.py, lead_spec 8).
- Order in `preconditions`: freeze verify (sha256, every listed file's sha256 and size, every trigger_hold/*.py,
  test, reused file, input role, events and trend file listed), config (schema, 1-24 rows, exact row keys, ids =
  the freeze's), registry path F-03, `require_registered(ids, test="E23", freeze_sha256)` (one entry holding every
  id), output free (marker and results), confirmation: the discovery result complete and its survivors re-derived,
  power table schema and ids, run manifest (both eras for every config root), context with e21_starts,
  `ctx.last = 2019-04-30` in discovery, preflight of every root (metadata, no row). Any exception -> "REFUSED",
  exit 2, nothing written. Then `write_marker` with O_EXCL (0o444; FileExistsError -> Refused, exit 2), and only
  then `compute` -> `load_or_exclude` reads bars. An exception after the marker writes STOPPED.json and exits 1;
  the marker stays and a rerun is refused (tests cover all three paths and the stub order).
- The power command writes once (O_EXCL) from events, calendars, the settlement table and store metadata; the
  frozen table reproduces exactly from the frozen inputs today.

Trigger extraction (events*.py, lead_spec 6; the TriggerCoder files).
- The member is the frozen factory's object, resolved through `screening.stage_e_freeze` (cluster freeze, code
  verified) after `harness_freeze.preflight` (v13 dd2bcc60...), run by `run_engine` with `StageERules` built as
  `screen_member` builds them (`legs_inputs` step for step, `member_window`, release calendar coverage); only the
  bar source differs (`base_rules.store.load_product`, both eras, every refusal; the era file re-read for the
  engine's 16 columns after its sha256 is re-checked and compared row for row with load_product's timestamps,
  trade-date bookings and closure flags). H6 runs through the frozen h6_rod code (`compute_facts`, `t1_schedule`,
  `run_schedule`) on MNQ with NQ's bars, as h6_rod.run does.
- An event = an opening strategy fill (`Fill.reason == "strategy" and Fill.opening`); tau = `Fill.decision_ts_ns`
  = the decision bar's open + 60 s (`strategy/stage_e/interface.py:72`), d0 = that bar's trade-date label (the bar
  is looked up by tau - 60 s and must exist). Nothing else of a fill is read; `del result` drops the ledger.
- W_ext context: `pattern_search.backward.backward_context(backward_tables())` (S1-S11: hist calendars, session
  rules, Rule H-1 rows, S6 month-end dates on the hist rates calendar, the combined release rows) plus the
  `stage_e_rules._calendar` cache cleared and `HARD_LIMIT_PRODUCTS` emptied (no limit table before 2019-05-01),
  both restored. The K2 table under the swap equals `events_tables.hist_month_end_table` (190 dates 2011-06..
  2019-04, tested), whose rule reproduces the frozen MONTH_END on the frozen calendar (tested); `build_member`
  refuses a member whose schedule differs from the table.
- W_cf validation (reports/stage_e23_events/validation/*.json): K2 ZF/ZN/ZB adapter vs the harness's own path
  (`_legs_inputs`, `load_confirmation_leg` from 2019-05-06 with the E.17 sha256, `member_window`,
  `member_coverage`, `_run_member`): identical (d0, tau, side), 79/77/79 events, 0 differences, all 16 frame
  columns and the trade dates equal (only the blackout set differs by pre-2019 dates outside the window). H6 vs
  E.20's own records (overlap.T1 + tests.T1, 1,147 trades): identical, tau = E.20's entry fill instant on all.
- Events files: top-level keys {schema, trigger_id, root, window, events, counts, inputs}; event rows exactly
  {d0, tau_ns, side} (`parse_events` refuses any other key; a `pnl` key is refused in a test); counts are integers
  about entries, refusals, coverage minutes, window and table dates; inputs are paths and sha256s. The meta files
  hold paths, sha256s, row counts, coverage ratios and the member declaration. No price, fill price, exit, mark,
  P&L or forward return anywhere (grep of every events, meta and validation file).

Tests: 93 passed (book 23, events 25 incl. the 8 written-file checks and the 4 recorded W_cf comparisons, run 13,
stats 22 plus parametrizations). The HAC, the entry timing at a 1 ns boundary, the clip, the flip, rolls paying
both legs, stress on every fill, the marker order, and the power numbers are each tested against hand or
independent computations, not against the code's own output.

Not verified by me: the frozen E.21 engine itself (multiday/, base_rules/) beyond reading the parts the unit book
calls; the 2010-2019 swap tables' sources (E.20 B1's work); statsmodels is not installed, so the HAC has only the
hand and loop checks above.

## Addendum (written after the review above): the spec changed at 03:25 PDT, the freeze no longer verifies

reports/stage_e23_briefs/lead_spec.md was amended at 03:25:54 PDT (mtime; 13,597 bytes, sha256 37a65616...) on the
RegReviewer's R-02, R-03 and R-04, after the 03:10 freeze (which pins the spec at 17f567bf..., 13,111 bytes). A
second `freeze_manifest verify` at the end of this review is REFUSED on that file; every trigger_hold/*.py, test and
reused file precedes the spec in the manifest's list and verified in that run, and the events and trend files
verified in the first run. The three amendments are clarifications the code already implements: R-02 (an absent
regressor value on a book date is zero: `trigger_hold.book.regressor_on`, and the first per-root T1/T2 values for
ZF, ZN, ZB, NQ are indeed dated 2011-07-29, see the trend files); R-03 (the confirmation hurdle b = max(2.0,
z_{1-0.05/S}) in `trigger_hold.evaluate.confirmation_gate`, power_gate being its S = 1 value); R-04 (s_x null for
every row, `window_for` then starts W_cf at 2019-05-06). No code change follows from them. The freeze must be
rebuilt (delete and `build`) before registration, with C-01's guard included if the lead adopts it, and the new
sha256 verified; the findings above hold for the code files as they stand.
