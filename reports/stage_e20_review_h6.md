# Stage E.20 Step 2: independent review of the H6 pre-registration and h6_rod (H6Reviewer-FableXHigh)

Reviewed 2026-10-11, 15:10 to 15:45 PDT (`date`), on fable xhigh, from the brief
reports/stage_e20_briefs/brief_h6_review.md. Inputs: reports/stage_e20_prereg_H6.md (186 lines, the
state after the lead's S1/S2/S3 rulings), docs/prompts/STAGE_E.20.md F2, F3, F5, F9 (lines 70-89,
122-154, 212-217), reports/stage_e20_briefs/product_NQ.md sections 4a-4c, shared/baltussen_notes.md
and shared/rosa_2022_notes.md, the paper's saved full text (by line range only), h6_rod/*.py (14
files, 2,003 lines), tests/test_h6_rod_*.py and tests/_h6_rod_synth.py, and the frozen modules the
package calls (read by grep and line range: screening/stage_e_engine.py, stage_e_rules.py,
stage_e_frozen.py, trial_registry.py, harness_freeze.py, data/stage_e_bars.py, group_session.py,
rules/sessions.py, xfa_rules.py, ml_route_v2/gate0.py, pipeline.py, strategy/members/k1/cp1.py,
_port_common.py). No data store, no GEX value, no Gate 0 file and no E.15/E.17/E.18 result was
opened; nothing under h6_rod/, tests/ or the prereg was edited; no ledger write; no commit.

Test run: `nice -n 10 uv run pytest -q -p no:cacheprovider tests/test_h6_rod*.py` gave **84 passed in
5.55 s** (15:17 PDT). Scratch checks (synthetic bars and the frozen calendars only) are in
/tmp/claude-1000/.../scratchpad/adv_h6_checks.py and adv_t2_clean.py; their results are quoted below.

## Verdict

**APPROVE WITH FIXES.** No BLOCKING finding. Three SHOULD FIX items, all cheap and all before the
freeze: one code change (a catch-all after the run-once marker so a crash still writes a STOPPED
result, H6R-1) and two text changes (the prereg header's claim about the GEX values, H6R-2; two
missing rows in section 7a's list of differences from the paper, H6R-3). The lead's three rulings
(S1, S2, S3) are correct and are implemented as ruled; the five confirm items (C1-C5) are confirmed.
The text follows F5 clause by clause; every addition beyond F5 is an implementation choice F5 leaves
open, and each is the natural reading (listed in section C below). The code implements the text; the
causality, clock, engine path, statistic, guard and run discipline checks all pass.

## Findings

### H6R-1 (SHOULD FIX, code): an unhandled exception after the run-once marker leaves the marker and no result

- Where: h6_rod/run.py `evaluate`, lines 265-294 (after `pf.write_marker`), and `_evaluate_window`,
  `run_tests` (h6_rod/engine.py lines 79-92).
- What: after the marker is written, only three exception classes are converted into STOPPED
  records: `StageEBarRefusal` and `OSError` from `load_leg` (run.py 271-275; `GuardRefusal` is a
  `PermissionError`, so it is covered), and `EngineInvariantError` / `EngineRefusedCase` inside
  `run_tests`. Anything else raised after line 265 propagates out of `evaluate`: `ValueError` from
  `signal._bar_lookup` (bars not strictly increasing), `ValueError` from the frozen `make_bar`
  (`date.fromisoformat` on an unexpected trade_date label: my scratch run shows the frozen engine
  raises `ValueError: Invalid isoformat string: '2022-03-14T00:00:00.000000'` on a datetime64
  column), any `OSError` from `hooks.releases()` on its second read (run.py 280), a `KeyError` or
  `TypeError` inside the member or `report.window_record`, or an `OSError` from `_write`. The
  process would exit with the marker present and no result file; `check` then refuses forever
  ("run-once marker exists"), and the prereg (section 1, section 5) forbids a second evaluation.
- Why it matters: the brief's run-discipline check is "no data condition raising after the marker".
  The build record (h6_build.md section 4 item 7) states the design as "After the marker, nothing
  raises", but the code implements it only for the named classes. The realistic residual risk is
  low (the loader sorts by ts_event, lines 282 of data/stage_e_bars.py; the real store's trade_date
  labels are ISO strings, since the same loader and engine ran on these stores in E.15 and E.17;
  the release file was just read in `check`), but a crash here would leave H6 with no verdict and
  no permitted way to obtain one.
- Fix: wrap everything from `w = _windows(cal)` through `doc.update(verdicts(...))` in
  `try/except Exception as exc:` that sets every test's record to `_all_stopped(tests, exc)` (with
  `traceback.format_exc()` added to the record) and falls through to `_write`. Keep `_write` outside
  that block but let `main` print the exception and still return a non-zero code. Add a test that
  injects a hook raising `RuntimeError` after the marker and asserts the result file exists with
  every test STOPPED. This is a change to h6_rod/run.py only; the frozen engine is untouched.

### H6R-2 (SHOULD FIX, text): the prereg header says the GEX CSV's values were not read, but section 6 reports a count of them

- Where: reports/stage_e20_prereg_H6.md line 3-4 ("before the GEX CSV's values were read") against
  lines 120-121 ("the GEX CSV holds 148 rows with GEX < 0 dated 2020-05-29..2024-02-28 (a count of
  the conditioning variable, made after T3's status was fixed; no price was read)").
- What: the two statements cannot both describe the frozen text. The count is a read of the sign
  of every GEX row in the window. It is harmless to the verdict (F5 fixes T3's rule and its floor of
  30 trades, and the sign count says nothing about NQ returns), and nothing in F4 or F5 forbids it,
  but a frozen pre-registration whose header misstates what was read before it is a weakness the
  freeze should not carry, and the verifier (Step 4) will trip on it.
- Fix: amend line 3-4 to "before any NQ bar was read for this rule and before Gate 0's NQ rows were
  read; the only GEX value read before the freeze is the sign count in section 6, made after T3's
  status was fixed", and add to section 6 who made the count, when (PDT), and the one-line command,
  so the verifier can reproduce the 148. I could not check the 148 (the brief forbids me the GEX
  values); the verifier should.

### H6R-3 (SHOULD FIX, text): section 7a omits two differences the NQ reader lists

- Where: prereg section 7a (lines 142-160) against product_NQ.md section 4b (lines 144-159).
- What: 7a carries the exit, early-close, T2, T3 and execution rows. Two rows of the reader's table
  are missing:
  1. **Prior close after an early-close day** (4b "Prior close" row). The paper removes early-close
     days (L527-534: "removing all days in which the exchange closed earlier (such as Memorial
     Day)"), so its P(prior C) for the next day comes from the last retained day, which the paper
     does not state. F5 uses the early close as C, so on the day after a shortened day P(prior C) is
     the close of the bar ending at the early close (for example Memorial Day 2022-05-30 11:59 CT for
     2022-05-31; my calendar check confirms 2022-05-30 is a shortened equity trade date with C
     12:00). The r_ROD of that day then spans the holiday's half session. There are 33 shortened
     dates in the verdict window (verified), so about 33 verdict dates differ from the paper in this
     way (fewer where two shortened days are adjacent).
  2. **Roll** (4b "Roll" row). The paper rolls on the back month's volume crossover (L525-527); the
     E.12 store rolls on its own L-8 rule, and F5 makes the roll date ineligible (instrument_change)
     and the engine refuses entries on the vehicle's roll-blackout dates. The paper's series has a
     return on those days; F5's has none.
  Both are disclosures, not changes (F5 binds). A third item is worth one clause: shortened days are
  eligible and feed T2's median although their |r_ROD| spans a shorter day (and on an 08:15 CT
  Good-Friday halt, 2021-04-02 and 2023-04-07, the signal bar is at 07:44 CT), which the paper's
  exclusion avoids.
- Fix: add the two rows (and the one clause) to 7a, citing product_NQ.md 4b.

### H6R-4 (NOTE): the day after a futures-only holiday session has no GEX row, so T3 skips it

- Where: prereg section 3 lines 79-81; h6_rod/signal.py `t3_schedule` line 205 (`gex.get(f.prior_day)`).
- What: F5's "previous trade date" is the equity group calendar's. On the day after Memorial Day,
  Labor Day, MLK Day, Presidents' Day, Juneteenth, Independence Day (observed), Thanksgiving and
  Good Friday, the previous trade date is a futures-only half session with no cash close and so no
  SqueezeMetrics row; such a day is "gex_missing" and has no T3 trade. The paper's NGE_{t-1} is the
  previous day in its sample (the last cash day). The prereg's reading is the literal one and is
  stated ("A previous trade date with no GEX row gives no T3 trade"), so this is a disclosure; it
  costs T3 roughly 7 to 8 verdict dates a year (about 30 of 971), of which perhaps 40% would have
  had a negative GEX.
- Fix (optional, text only): one sentence in section 3 naming this case and its approximate count,
  so the verifier does not read the gex_missing count as a data defect.

### H6R-5 (NOTE): T2's warm-up reading is the literal one; the first verdict date may fall in "t2_warmup"

- Where: prereg section 2 lines 29-32; h6_rod/clock.py `t2_warmup_first`; signal.py `t2_thresholds`.
- What: F2 allows "the 60 trade dates before 2020-06-01" as warm-up and F5 wants "the previous 60
  eligible trade dates". The prereg takes exactly 60 trade dates (2020-03-06..2020-05-29, verified:
  60 equity trade dates, Memorial Day 2020-05-25 included as a shortened date, Good Friday 2020-04-10
  not a trade date) and requires 60 eligible dates inside them; any ineligible warm-up date (the
  March 2020 roll date, for instance) pushes the first T2 threshold to the second or third verdict
  date. The alternative reading (extend back until 60 eligible dates are found) would read more than
  60 warm-up dates, which F2 does not allow. The prereg's reading is the natural one and the case is
  counted ("t2_warmup"). Causality verified by perturbation: changing r_ROD on d or any later date
  leaves d's threshold unchanged; changing the 61st-most-recent eligible date leaves it unchanged;
  changing the 60th changes it; a lookback_first that leaves 59 eligible dates gives None.
- Fix: none required.

### H6R-6 (NOTE): the registry names differ from the prompt's, as ruled (S1)

- Where: prereg section 8; h6_rod/constants.py lines 79-80; screening/trial_registry.py lines 48-49.
- What: the frozen registry's label regex `[A-Z][A-Za-z0-9]{0,15}` allows no hyphen and ids must be
  `<label>-<suffix>` (verified). F9's names E20-H6-T1..T3 cannot be registered; `E20H6` with
  `E20H6-T1..T3` is the E16 pattern and the regex accepts it (`pf.registry_names_valid` passes;
  the hyphenated label is refused, test at tests/test_h6_rod_run.py line 55). The registry's current
  N is 480 (ledger last entry r003-C1b, n_after 480), so section 8's "N 480 -> 483" is right.
- Fix: none. The progress entry should map the prompt's names to the registered ids once.

### H6R-7 (NOTE): the freeze manifest need not list the tests; recommend listing them anyway

- Where: h6_rod/preflight.py `required_files` lines 111-115.
- What: the manifest must list h6_rod/*.py, the prereg, every loaded ml_route_v2 module and the GEX
  CSV. The tests and tests/_h6_rod_synth.py are not required. The frozen clock and cost inputs are
  covered elsewhere: data/calendars/equity.py and data/cme_calendar.py are harness-v12 files,
  reports/stage_e2b_release_calendar.json is in the harness manifest, and the D8 tables are checked
  against pinned hashes in screening/stage_e_frozen.py (`_read_verified`). The harness preflight
  passes on this tree (verified: `harness_freeze.preflight(v12 sha)` returns the sha).
- Fix (optional): add tests/test_h6_rod_*.py and tests/_h6_rod_synth.py to the manifest so the
  frozen record carries the tests the verdict rests on.

### H6R-8 (NOTE): two wording points in the prereg

- Section 1 line 12: "the return over the last half hour, from C-30 to C-1" mixes the paper's
  variable (to C) with the traded window (to the 14:59 fill). Say "the paper's last half hour (C-30
  to C); traded here from the C-30 open to the open after the first bar at or after C-2".
- Section 1 line 17 attributes T2 to "Rosa ... the threshold form" (F5's words); 7a corrects this.
  Fine as is, since F5 binds and 7a discloses.

### H6R-9 (NOTE): `member.trading_windows` is nominal and unused on this path

- h6_rod/member.py line 57 declares (14:29, 15:00) on every day. Only screening/stage_e_runner.py's
  coverage check reads `trading_windows`; h6_rod calls `run_engine` directly, so nothing reads it.
  On a shortened day the real bars lie outside it, which has no effect. No fix needed; a comment
  saying it is unused would help the verifier.

### H6R-10 (NOTE): the CLI refusal test is weak

- tests/test_h6_rod_run.py lines 66-75 run the real `python -m h6_rod check` with a wrong freeze
  sha and assert only `RC_REFUSED` and "REFUSED" in stderr. Any refusal satisfies it (today it
  refuses because the manifest does not exist yet). Harmless; after the freeze it still passes for
  the intended reason. Optionally assert "freeze manifest" in stderr.

## A. The lead's rulings, checked

- **S1** (label E20H6, ids E20H6-T1..T3): correct, see H6R-6.
- **S2** (a shortened day's entry is refused because F = C-30): verified independently. For every
  shortened equity trade date from 2019-05-06 to 2024-02-29, `rules.sessions.flatten_time_ct("MNQ",
  d)` equals the early halt minus 30 minutes (none differ); `TOPSTEP_EARLY_CLOSE_LEAD` is 30 minutes
  for 2019-2025 and 15 for 2026 (rules/sessions.py lines 210-213), so the prereg's "30 minutes for
  2019-2025" is right. The frozen rules refuse an intent when `sessions.session_state(root,
  decision).must_be_flat` or the bar's flatten flag is set (stage_e_rules.py lines 493-496); the
  decision at the C-31 bar's close is C-30 = F, and the engine test on 2022-11-25 (halt 12:15, F
  11:45) shows `engine_flatten_window`. The verdict window has 971 equity trade dates, 33 shortened
  (verified), with halts at 08:15, 12:00 and 12:15 CT; the overlap window has 277 and 10. Section 3
  and 7a now describe this correctly.
- **S3** (one lead-in trade date per engine run): correct. `clock.lead_in_dates(2020-06-01, 1)` is
  (2020-05-29,) and for the overlap window () (the store starts 2019-05-06). The lead-in has no
  schedule entry and is not in the rules' `window_dates`, so no entry is possible there (two
  independent refusals); rules/xfa_rules.py has no inactivity rule (grep: none), so the account is
  unchanged by a day without a trade. Without the lead-in the first verdict date would be refused
  `engine_price_limit_reference_unavailable` (test at test_h6_rod_engine.py line 123).

## B. The confirm items C1-C5

- **C1** reason precedence (missing_signal_bar, missing_prior_bar, instrument_change, zero_signal):
  confirmed; it is the order of section 3 line 53 and affects counts only (signal.py lines 97-108).
- **C2** one engine run per test and window with its own account: confirmed; `run_schedule` builds
  a new `StageERules`, a new member and `run_engine` builds a new `_Run` per call (stage_e_engine.py
  line 681). `restart_on_terminal` defaults to True in `StageERules` (stage_e_rules.py line 285),
  so the MLL restart the prereg names is in force although engine.py does not pass it; recommend
  passing it explicitly for the record.
- **C3** the vehicle's blackout = NQ's set via `own_blackout`: confirmed (pipeline.py lines 260-266,
  `exclude_union` over the path as the only leg; test at test_h6_rod_engine.py line 131). "Its
  root's" set contributes nothing because MNQ's own store is never read (E.12 P-1).
- **C4** a STOPPED test enters Holm with p = 1 and m unchanged: confirmed and conservative; with
  (0.008, 1.0, 0.012) Holm rejects the first two and not the stopped one (scratch check).
- **C5** `check` reads no bar; the price-free validation runs inside `evaluate` before the marker;
  price-level defects surface after the marker as STOPPED: confirmed as the right design, because
  the prereg says prices are loaded only after the marker. The one gap is H6R-1 (a non-engine
  exception after the marker).

## C. Text against F2, F3, F5, F9: clause by clause

Every F5 clause is present and exact: vehicle, lot and D8 buckets (s2, s3); C as CP1 defines it
(s3); CP1's bar, intent and fill conventions through the frozen engine (s3); r_ROD's definition,
both bars with one instrument_id, r_ROD = 0 no trade (s3); entry on the bar ending at C-30 in
sign(r_ROD) filling at the next open (s3); CP1's exit (s3, matching cp1.py lines 18-21 and
_port_common.exit_if_due); T1, T2 (median over the previous 60 eligible dates, "exceeds" read as
strictly greater), T3 with its condition and status (s1, s3, s7); the statistic by gate0._b_test with
the Sharpe over all window trade dates with zeros (s4); the four pass conditions with Holm at 0.025
over the registered tests (s5); the descriptive list and the power line (s6). F2's windows, warm-up
and never-read list are s2. F3's guard is s9 and h6_rod/guard.py. F9's N is s8 (H6R-6).

Additions beyond F5, each an implementation choice F5 leaves open, each the natural reading:
1. The four eligibility reason codes and their precedence (counts only).
2. The warm-up rule's "t2_warmup" case (H6R-5).
3. "gex_missing" for a previous trade date with no row (H6R-4).
4. Engine refusals of eligible dates counted by reason with zero P&L; the engine's F and D9.7 as
   backstops; the MLL restart; roll-blackout refusal: all the frozen engine's behaviour, which F5
   invokes ("through the frozen engine").
5. The lead-in date (S3).
6. The STOPPED rule (p = 1, m unchanged).
7. Extra descriptive outputs (exit types, refusal counts, MLL breach dates, the GEX sign count):
   never in the verdict; the GEX count needs H6R-2's header fix.
8. The registry names (S1).
9. The 1.5 x slippage stress defined as each fill's slippage ticks x 1.5 through the frozen
   `slippage_cents` rounding, commission unchanged: the natural reading of F5's "1.5 x slippage
   stress" (descriptive only).

T3's status: product_NQ.md 4c rules CLEARED (terms fetched 2026-10-11T17:34:43Z, byte-identical to
E.14's copy; robots.txt 404; the free DIX page's own download button; the single existing copy
reused, nothing redistributed). F5's condition is "only if the NQ reader clears the GEX source under
its terms before any NQ bar is read": the ruling predates the build (10:52 PDT) and no NQ bar has
been read for H6 (the evaluation has not run), so the condition is met on the record. Section 7
states the ruling faithfully (the quoted clause matches 4c's verbatim text). The reasoning is the
reader's and the lead's to own; I did not re-fetch the terms.

## D. The rule against the papers

The notes' quotations match the saved paper at the cited lines (checked L589-596 r_ROD's definition,
L525-534 the roll and the four filters including early-close removal, L541-546 the 09:30-16:00
hours, L1970-1976 NGE from OptionMetrics then SqueezeMetrics, and the Table 6 and 7 descriptions by
grep). Section 7a's listed differences are correct; the list is incomplete by the two rows of
H6R-3. T2 is correctly disclosed as the planning brief's variant, not Rosa's (the Rosa notes have
only the abstract; the predictor there is the overnight return). T3 is correctly disclosed as an
S&P 500 gamma result (Table 7, S&P 500 futures only) applied to NQ by sign.

## E. Code against the text

- **Causality.** `compute_facts` reads only the bar opening at C(d)-31 and the bar opening at
  C(p)-1 of the previous trade date, by exact open instant (signal.py 118-126); nothing is forward
  filled. T2 uses only eligible dates before d within [lookback_first, d) (perturbation results in
  H6R-5). T3 uses only the row dated `prior_day` (perturbing every other row leaves d's membership
  unchanged; a zero row excludes; a missing row gives "gex_missing"). GEX rows dated 2024-03-01 or
  later are cut after the date field is parsed and before any other field (gex.py 44-49).
- **Clock.** C is the frozen equity calendar's early halt else the frozen day_session_ct, checked
  to equal 15:00 (clock.py 41-61). Signal bar C-31, prior bar C-1, exit from the bar at C-2, all
  as CP1 (cp1.py lines 59-60 use the same 31 and 2). The engine test shows the entry fill at the
  14:30 open and the exit fill at the 14:59 open (decided at the 14:58 bar's close), a missing 14:58
  bar exiting at 15:00, and no bars 14:58-15:07 giving the forced flatten at 15:09 (F 15:08 on a
  normal day, verified). Shortened days: S2 above. The instrument_id rule: `eligibility_reason`.
  Each no-trade reason: section 3's four, plus t2_warmup, t2_not_above_median, gex_missing,
  gex_not_negative, plus the engine's refusal reasons from `IntentRecord` (report.py 56-85).
- **Engine path.** `run_engine` with `StageERules({MNQ: leg_inputs(MNQ, traded=True)},
  window_dates, blackout, releases)` on the NQ frame fed as the MNQ leg (engine.py 50-76); the
  frozen engine, rules, loader, sessions, price limits and XFA rules are all harness-v12 files
  (checked against reports/stage_e2b_harness_freeze.json). D8 MNQ costs per bucket come from the
  engine's own Fill records (commission 122 cents plus 41 a side in the 14:30 bucket, test at
  test_h6_rod_engine.py 137-149); gross from `gross_realized_cents`, cross-checked against the fill
  prices (`price_check_ok`). Roll-blackout refusal, D9.7 reference refusal, MLL restart: above.
- **Statistic.** `stats.b_test` calls `ml_route_v2.gate0._b_test(test_id, "MNQ", horizon, frame,
  n)` with g_ticks = net_i and cost_ticks = c_i, as section 4 says; `_b_test` takes per-date means
  (one trade a day, so net_i), `date_t` and the one-sided `student_t.sf(t, n_dates - 1)`; a losing
  sample gives p 0.994 (direction verified). Holm: ascending, bound 0.025/(m-k+1), stop at the
  first non-rejection, ties by (p, name) (stats.py 156-173; cases checked). Sharpe: daily net
  dollars over every equity trade date of the window with zeros, ddof 1, sqrt(252) (stats.py
  135-153); a trade dated outside the window raises, which cannot happen (no lead-in entries). The
  pass bar's four conditions (stats.py 180-190) with NaN failing. The 1.5 x stress and bp
  (report.py 99-129) are descriptive. Zero-trade paths (a per-year bucket or the overlap T3) give
  t NaN, p 1.0, FAIL without raising (verified; the suite's overlap T1 has 0 trades).
- **Guard (F3).** `check_store_path` refuses every path but the NQ store; planted tests cover
  processed_hist, sealed, the holdout blob and roots, the MES research and confirmation parquets,
  another root's step 2 store, another research store, vendor raw, and a symlink into sealed; the
  audit hook refuses Python-level opens in a subprocess; `check_bars` raises on a bar with
  trade_date 2024-03-01 or ts_event at or after 2024-03-01 00:00 UTC (tests at
  test_h6_rod_guard.py 44-151). The loader path: `validate_store` and `load_leg` call
  `check_store_path` before anything is opened (run.py 74-75, 96). GEX rows on or after 2024-03-01
  cut (above).
- **Run discipline.** `check` verifies the lead's settings, the harness at v12, the freeze manifest
  (its own sha, every listed file's sha and size, every h6_rod/*.py, the prereg, every loaded
  ml_route_v2 module, the GEX CSV), the store and GEX pins, the release calendar's coverage and the
  absence of the marker; `register` adds the refusal of a second registration; `evaluate` adds the
  registration check under this freeze sha, the price-free store validation and the GEX parse
  before the marker, then the marker by O_EXCL, then the prices. A second `evaluate` is refused by
  the marker (test at test_h6_rod_run.py 148-149). The gap is H6R-1.
- **Forbidden reads.** No h6_rod module names reports/stage_e12_gate0.*, E.15, E.17 or E.18 paths
  (grep: none). Bars outside 2019-05-06..2024-02-29 cannot enter: the store's own range, the
  loader's `start`, and `check_bars`.

## F. What I could not check

1. The real NQ store's `trade_date` column type (the brief forbids opening the store). The frozen
   `make_bar` converts every label with `date.fromisoformat(str(label))`, so ISO-string labels (what
   the same loader and engine consumed in E.15 and E.17) work and a datetime64 column would raise
   after the marker (H6R-1 covers the consequence). The verifier can confirm the dtype from the
   parquet schema at Step 4.
2. The GEX sign count 148 (section 6): values forbidden to me.
3. The order of events in time (the ruling before any NQ bar; the freeze commit before the
   registration line): documentary here, git and the registry at Step 4.
4. The SqueezeMetrics terms themselves: I read the reader's saved quotations, not the page.
5. The lead's test edits in tests/test_h6_rod_run.py: I read the current file (84 passed) and did
   not diff against the coder's version.
