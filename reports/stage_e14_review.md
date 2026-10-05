# Stage E.14 review (Fable)

## Freeze review (Task 4)

Reviewer: FreezeReviewer-FableXHigh (worker-xhigh on fable), 2026-10-05 03:10-04:10 PDT, on the main checkout
with harness v10 staged and uncommitted (candidate manifest sha256 22fcdbbb2644e87cedab488a4e968b760e2a90610d96920e89801e142629285e,
preflight OK on the working tree at 03:40). Brief: reports/stage_e14_briefs/brief_freeze_review.md. Read-only
except this file. No market data, no GEX value, no E.12 state content (names and sizes only), no .env, no key,
no network call. Scripts and outputs: the session scratchpad folder `freeze_review/` (quote_check3.py and its
`unmatched3_<group>.txt` files, pytest_review.out).

### Verdict: APPROVE WITH FIXES

1 BLOCKING (a one-paragraph edit to the C1 freeze text; no code or manifest change), 2 SHOULD FIX (one freeze-text
reconciliation, one .gitignore line), 12 NOTE. Nothing in harness v10's code needs to change before the commit, so
the candidate manifest sha256 22fcdbbb... stands unless the lead adopts one of the optional code improvements
(F-04, F-05), each of which would need a manifest rebuild, a rerun of c1_freeze_inputs.py and a new prereg_C1.md
sha in STATE. The text fixes F-01 and F-02 change reports/stage_e14_prereg_C1.md's sha256 only (that file is in
neither the manifest nor the freeze-inputs list); STATE must record the new sha.

### Findings

**F-01 BLOCKING (freeze text; C1).** Section 11's later-session check is unsatisfiable as written.
reports/stage_e14_prereg_C1.md:193: "verify that its harness differs from v10 only in data/config.py, and there only
in ACCOUNT_2_CAP_USD and E14_EXT2010_SESSION_CAP_USD (and the comments beside them)"; the same promise at :134
("a harness that raises only ACCOUNT_2_CAP_USD and E14_EXT2010_SESSION_CAP_USD") and c1_replication/README.md:43
("the later harness that changes only the caps"). But four harness-manifest test files pin those two values:
tests/test_e14_config_v10.py:20 `assert config.E14_EXT2010_SESSION_CAP_USD == 0.00`, :32-33 `assert
config.ACCOUNT_2_CAP_USD == 249.67` / `ACCOUNTS[...].cap_usd == 249.67`; tests/test_e14_pull_hist.py:300 `assert
config.E14_EXT2010_SESSION_CAP_USD == 0.0`; tests/test_stage_e_config_v8.py:64 `assert floored == 249.67 ==
config.ACCOUNT_2_CAP_USD`. All match harness_freeze.TEST_PATTERNS (screening/harness_freeze.py:270-273: test_e14_*.py,
test_stage_e_*.py), so a cap-raising harness v11 either fails the full suite (the start checks require it green) or
edits those tests, which the clause forbids. Either way the later session hits a guardrail conflict by construction.
Fix (text only): reword :193 and :134, and README:43, to "differs from v10 only in data/config.py (ACCOUNT_2_CAP_USD,
E14_EXT2010_SESSION_CAP_USD and their comments) and in the assertions that pin those two values
(tests/test_e14_config_v10.py:20,32-33; tests/test_e14_pull_hist.py:300; tests/test_stage_e_config_v8.py:62-64),
nothing else". Do not relax the asserts now: that would change v10 and the manifest for no gain.

**F-02 SHOULD FIX (freeze text; C1).** The freeze contradicts itself on ruling C7. Section 3 (:48-49): "The CL and MBT
frames are empty, with an equality test (ruling C7)." Section 11 (:183): "CL and MBT are each given one sentinel bar
dated 2019-05-31, after the window, because a truly empty frame crashes the frozen g17 code". Section 12 claims to
list "every" change from the draft and does not list this one. The code is the sentinel: c1_replication/world.py:48
`C7_SENTINEL_DAY = date(2019, 5, 31)`, :123 `bars.update({r: sentinel_frame() for r in EMPTY_ROOTS})`; the equality
test is tests/test_c1_world.py:78 (`pd.testing.assert_frame_equal(a.frame, b.frame)`, NG rows with the sentinel
versus synthetic CL bars) and :55 shows the IndexError on a frame with no row. Fix: amend section 3's sentence
("empty within the window: one sentinel bar dated 2019-05-31, after the window, so no lead bar is ever closed at an
NG decision time; equality test tests/test_c1_world.py::test_c7_ng_rows_equal_those_with_synthetic_cl_bars") and add
the item to section 12. The design is sound; only the text disagrees with itself.

**F-03 SHOULD FIX (repository hygiene; C2 file).** The SqueezeMetrics CSV is not git-ignored: `git check-ignore
reports/stage_e14_briefs/gex/DIX.csv` exits 1; the only guard is reports/stage_e14_briefs/gex/DO_NOT_COMMIT.txt (DIX.csv,
DIX.csv.headers, ../pages/gex/wayback/DIX_*.csv). Task 9's commit includes "the briefs", and open choice 3 promises
the file "stays uncommitted ... so the program does not redistribute it". Fix: add
`reports/stage_e14_briefs/gex/DIX.csv`, `reports/stage_e14_briefs/gex/DIX.csv.headers` and
`reports/stage_e14_briefs/pages/gex/wayback/DIX_*.csv` to .gitignore. .gitignore is not in the harness manifest
(0 occurrences in reports/stage_e2b_harness_freeze.json), so v10's sha256 does not change. The E.12/E.13 precedent
(untracked DO_NOT_COMMIT page folders) covered the program's own page copies; this file is a third party's data set.

**F-04 NOTE (order of events in code).** screening/trial_registry.register (:199-231) runs the harness preflight
(:208), hashes the freeze file (:186-197 `_freeze_record`) and chains N, but does not check that the freeze file is
committed and clean in git. "Freeze commit, then registration" is therefore evidenced by timestamps (the registry's
`time_local` against the commit time), not enforced by code. Optional for a later harness (it would change v10 and
the manifest now): refuse unless `git ls-files --error-unmatch <freeze>` and `git diff --quiet HEAD -- <freeze>`
both pass. Everything else in the order is enforced: the ES or ext2010 buy refuses without the plan's registration
(data/pull_hist.py:284 `trial_registry.require_registered(plan.test_ids, test=plan.test, ...)`, inside
`require_buy_ready` :270-291, called before the key is loaded, data/pull_hist.py main), and both evaluations
refuse without a registration under the same freeze sha256 (screening/stage_e14_c2.py preconditions, :445-480;
c1_replication/evaluate.py preconditions :305-361), run once (marker and --out must not exist; the marker is
written before any bar is read, stage_e14_c2.py:508-510, evaluate.py:553), and cannot run under another freeze
file (the file given must hash to --freeze-sha256 and that sha must equal the registry entry's).

**F-05 NOTE (C1 code hashes are not self-verified).** c1_replication/ and tests/test_c1_*.py are outside the harness
manifest by design (open choice 10; harness_freeze.py:270-273 lists test_e14_*.py but not test_c1_*.py) and are
pinned only by reports/stage_e14_c1_freeze_inputs.json (43 entries; all 43 verify on disk at 03:35, including the
six hist2010 calendars byte-identical to the reports/ copies). evaluate.preconditions records its own code hashes
(`_code_hashes()`, :363-367) and the calendars by caller-supplied hashes, but verifies nothing against the inputs
file. The later session's manual step (1) in section 11 is the only guard that the code and calendars are the
frozen ones. Suggest: the later session runs a scripted check of every entry of the inputs file (the loop in this
review's scratchpad does it in two seconds) and records the result in its STATE before registering; a later
harness may add that check to preconditions.

**F-06 NOTE (harness sha at registration versus evaluation).** trial_registry.require_registered (:136-163) compares
the test, the ids and the freeze sha256, not the registration's `harness_sha256` with the harness in force. For
C1 this is intended (section 11 allows a later cap-raising harness); both evaluations record the preflight's sha
and the registry entry id in their output, so the verifier can reconcile them.

**F-07 NOTE (C2, for any future freeze; inert now).** The C2 code is exactly the draft's sections 3-5 except where
it had to choose a decimal or an interpretation; a C2 freeze, if the user ever runs C2, must state these:
c = 2.0379 and bar = 3.05685 (screening/stage_e14_c2.py:81-82) versus the draft's rounded "2.038" and "3.057"
(open choice 9); late-open dates excluded (:202; the draft names early closes only); `prior_trade_date_unsourced`
(:210); lag 1 = the row of the latest CSV date strictly before d (:182), not the calendar's prior trade date; T1 =
GEX < 0 strictly (:312). The statistic matches section 5 line by line: sd with ddof 1 (:346), t = mean / (sd /
sqrt n) (:348), one-sided p = Student t survival function at n - 1 degrees of freedom (:353), pass iff mean >=
3.05685 and p <= 0.025 and n >= 30, inclusive (:354-356), the hypothesis passes iff T1 passes and mean_T1 >
mean_T2 (:374-375); "T2 passes alone" is a FAIL with its own reading. The 2% unsourced stop and the 200-date
power stop are lead checks, not code refusals: `count_gex_negative` reports `window_unsourced_share_of_weekdays`
(:239) and the count, and reports/stage_e14_briefs/gex_count.py prints `power_stop_fires`; neither stops a run,
and `evaluate` does not test the 2% share. Under v10 nothing can buy ES or run C2: E14_SESSION_CAP_USD = 0.00
(data/config.py:181; `require_buy_ready` refuses at :281 before the registry check), no C2 registration exists
(ledger/trial_registrations.jsonl holds the baseline line only), and reports/stage_e14_prereg_C2.md does not exist
(the run's freeze check refuses). Tests: tests/test_e14_pull_hist.py:290 (es2011 refuses at cap 0), :317 (refuses
without C2's registration), tests/test_e14_c2.py:398 (run refuses without the registration or with a marker).

**F-08 NOTE (web-access guardrail, C2).** reports/stage_e14_gex.md sections 2-3 and open choices 4-5 use seven
Wayback captures of SqueezeMetrics' CSV (2020-11-29 to 2026-10-02) for the timing rule and the revision check. The
prompt's Guardrails allow "Official government and exchange calendar pages, Wayback captures of them, and
SqueezeMetrics' public CSV page only"; Wayback captures of the SqueezeMetrics CSV are not on that list. Read-only,
hashes and last-row dates only, and no verdict depends on it (C2 stopped). Record it as a deviation under Open
choices, not only as a method.

**F-09 NOTE (the C2 stop and its two rulings).** The terms ruling is defensible: the clause quoted in gex.md
section 1 bars "systematically retrieve data ... to create or compile ... a collection, compilation, database, or
directory without written permission"; one download of the file the free page offers through its own button, kept
uncommitted, is not that. The timing ruling follows the draft's own default: lag 2 applies only "if SqueezeMetrics
documents that a row dated d-1 can be published after 14:30 CT on d"; it documents nothing, and the server's
Last-Modified (16:57 CT on the last row's date) and the same-evening captures corroborate lag 1. The disclosed limit
(the 2011-2019 rows were most likely computed later, so information timing is moot for the window) belongs in any
future C2 freeze. The power stop is applied to an upper bound (the roll blackout and bar presence can only lower
the count) and the calendar-free bound of 146 makes it independent of the equity calendar; 135 < 200 by a margin
no calendar correction can close. Not checked here: the count itself (the brief forbids reading GEX values);
Task 8 recomputes it. The count script (gex_count.py) and v10's helper (`count_gex_negative`) are two
implementations and agree.

**F-10 NOTE (timeline accuracy).** data/config.py's mtime is 01:34:22 PDT, but its comment (:175-180) and the STATE
say the cap was set to 10.41 at 01:33 and reset to 0.00 at 01:42. Harmless (the value, the test pins and the
02:29 manifest agree), but the return's order-of-events table should quote actual times. The registry baseline is
timed 01:02:35 in the worktree, before the merge; fine for a baseline (v10 notes section 4 item 5 offers a
re-init if the lead wants it timed in main).

**F-11 NOTE (the 3% stop measures a proxy).** data/pull_hist.py:469-491 (`_settle`) and :512 settle a chunk at
quote x delivered / quoted bytes and stop when that ratio exceeds 1.03. That is a proxy for Databento's bill (v10
notes D-3), not the bill; the program never reads the billing API. The purchase report should set the ledger's
settled total against the account balance the user reads on Databento's billing page.

**F-12 NOTE (calendar citations and grades, question F).** Every status_quote, time_quote and no_entry_finding
quote of the six group files was checked by script against its saved source (1,478 quotes): 658 verbatim text
matches (PDF and HTML text), 123 row-level matches in PDF/doc text, 534 CSV cell matches for the 2013-2019 CME
workbook sheets (the workers rendered cells as "Row | Date/Header=Value", abbreviating the sheet's "Monday, January
21" to "Mon Jan 21"; the script maps date and header columns and compares the cell), 162 CSV-row matches for the
xls sheets, and one item verified by `strings` on the cited xls: energy and metals 2019-01-01 (and the 2018-12-31
no-entry finding) cite the 2018 zip's member 2019-new-years-holiday-schedule-compact.xls, which holds "CME Group
Globex New Years Holiday Schedule: December 31, 2018 - January 2, 2019", "Monday,Dec 31" and "Wednesday, January
2" as quoted, while the derived sidecar beside it (`...compact-New Years 2018.csv`) holds the 2019-2020 sheet
("Tuesday,Dec 31"). A derived-file mix-up in the briefs folder, not a calendar error. The probe's 2012 energy
entries equal the commodity builder's (11 of 11). Grades: every entry, session and year row is "cme"; every source
is a Wayback copy of cmegroup.com (plus one cmegroup.mediaroom.com press release) except one cftc.gov file per
group. The equity and rates 2012-10-29 halts (equity 08:15, rates 11:00) cite `cftc_12_29`, CME's emergency rule
filing as hosted on cftc.gov, at grade "cme"; under calendar_rules.md's letter ("cmegroup.com file or page ... or a
CME clearing/Globex notice") that is a "secondary" document. Both grades are sourced, so no count or exclusion
changes; note it in reports/stage_e14_calendars.md's Limits rather than regrade (a regrade changes the equity and
rates JSON bytes, the hist2010 copies, the manifest and the freeze inputs).

**F-13 NOTE (the 2% windows and the exclusion code).** Recomputed from v10's loader on data/calendars/hist2010:
C1 window 2010-06-07..2019-04-30 trade dates equity 2,298, rates 2,297, fx 2,298, energy 2,296, metals 2,296,
grains 2,243, 0 unsourced in each; C2 window 2011-05-03..2019-04-30 equity 2,064 trade dates, 0 unsourced, 71
early halts and 6 late opens, so 1,987 calendar-eligible, as reports/stage_e14_calendars.md and gex.md state. The
release file has one unsourced instant (WPSR-2012-11-01, listed in `unsourced[]`; the only null instant) and
c1_replication/tables.py refuses any other null instant (:20-23, :152-163). Unsourced dates are excluded by code,
not just listed: data/hist_store.drop_outside_window drops their rows before any price column is read
(:186-187), data/hist_bars.check_hist_bookings refuses them (:78) and refuses any row outside the plan's window or
in a holdout class (:74), stage_e14_c2.calendar_reason excludes them (:195) and c1_replication/exclusions.py
excludes them with the prior-date and release rules and stops at > 2% before the marker (evaluate.py:336). The
loader derives unsourced from four reasons (data/hist_calendar.py:21-28), not only the file's own list. The lead's
loader edits (Friday-to-Monday session handover; one early halt plus one late open on a day) refuse any weekday
gap and any late open beside a full closure (data/hist_calendar.py:252-261, :307-317) and have tests
(tests/test_e14_hist_calendar.py, the two added tests).

**F-14 NOTE (process: what a change invalidates).** The C1 freeze (:164) and reports/stage_e14_c1_freeze_inputs.json
(`harness_manifest_sha256`) pin the v10 manifest sha 22fcdbbb...; the freeze (:169-171) pins the inputs file's sha. Any
v10 file change before the commit (none required here) means rebuilding the manifest, rerunning
c1_freeze_inputs.py and re-recording prereg_C1.md's sha in STATE, in that order. F-01 and F-02 touch
prereg_C1.md only.

**F-15 NOTE (C2 cap pin).** tests/test_e14_pull_hist.py:292 asserts `config.E14_SESSION_CAP_USD == 0.0` inside the
es2011 refusal test, so a future C2 run under a cap above zero must change that test too (the C2 side of F-01;
inert while C2 is stopped).

### Verification record (questions A-H of the brief)

- **A. No free parameter.** C2: every number is a module constant (stage_e14_c2.py:73-97: window, store first
  date, tick, commission 0.976, spreads 0.5191 and 0.5428, c, bar, alpha, 30 trades, lags 1 or 2 fixed by the
  freeze and given on the command line, bar times) and the statistic matches section 5 (F-07). C1: every parameter
  is in c1_replication/constants.py (tests, horizons, window 2010-06-07..2019-04-30, 1.5c, 0.025, 30, 2%, H-1's
  30-minute lead, the pinned sha256s of the v2 freeze, the Gate 0 report and list); q = min |r_hat| of NG's Gate 0
  trades at h (q_m1.py:210-220, ruling C3; Gate 0's own cutoff is the top fraction, gate0.py:301-306, so min |r_hat|
  with `>=` reproduces that set up to ties, which q_m1 counts); M1 = ridge_spec(GATE0_RIDGE_LAMBDA) on
  horizon_data(panel, h, admissible), fitted twice with equal payload sha256 (q_m1.py:223-236); feature_cols =
  E.12's, checked before the marker against the model JSON (evaluate.py:329) and after against the panel (:512);
  trade rule |r_hat| >= q and sign != 0, one contract (evaluate.py:386-407); statistic gate0._b_test applied as
  Gate 0 applies it (:528); pass bar mean >= 1.5c, p <= 0.025, n >= 30, inclusive, NaN never passes (:410-412);
  C10 reference counts from the E.12 panel (q_m1.py:238-249) against the replication's (evaluate.py:376-383), a
  stop after the marker; C11 before and after. Costs: c(NG,h) is _b_test's mean cost of the sides taken.
- **B. Stop rules.** C1: the probe rule was a lead ruling on Task 1 (0 of 258 energy dates, 0 or 1 of 52 NGS,
  under the 2%/2 limits either way); the 2% stop is code (exclusions.py, pre-marker refusal); the q-reproduction
  mismatch stop is code (q_m1.py `compare`, absolute 1e-9 on mean and t_B, exact counts, exit 3 with nothing
  written; the no-fit guard patches gate0.fit_model, which gate0 imports by name at gate0.py:65 and calls at :288,
  and the tests' spy on models._fit_ridge counts only M1's four fits); the C10 stop closes the attempt (after the
  marker, verdict STOPPED, exit 1); run-once by marker and --out. C2: the 2% and the 200-date stops are lead
  checks (F-07), the terms stop a lead ruling (F-09); the spend stops are code: session cap = quote x 1.03 and
  `left > headroom` refuses (pull_hist.py:287), billed above the quote by more than 3% stops before the next
  chunk (:512), a Databento refusal surfaces as DownloadError or BudgetRefusedError and the run stops (:690-696).
- **C. Order of events.** Enforced in code except the git half of "freeze commit then registration" (F-04). The
  ES buy cannot run without C2's registration (pull_hist.py:284) nor at cap 0.00 (:281). C2's evaluation cannot run
  twice (marker, --out), without the registration, or with a different freeze file (preconditions :445-480). C1's
  buy cannot run under v10: E14_EXT2010_SESSION_CAP_USD = 0.00 (config.py:189) refuses at :281 before any key is
  loaded and before the registry check; no C1 registration exists either (tests/test_e14_pull_hist.py:297).
- **D. Windows disjoint.** No file under data/ carries a pre-2019-05 bar: data/vendor/databento/GLBX.MDP3/ohlcv-1m
  holds 46 root folders whose chunk names start no earlier than the step 2 window; rolls and condition files start
  2019-04-01 (symbology spans only); data/processed_hist does not exist. The hist plans refuse any chunk outside
  their windows and any end past 2019-05-01 (pull_hist.py:179-197, the module-level check at :148-153); the stores
  drop rows outside the plan's trade dates unread and refuse holdout-class rows (hist_store.py:165-195); the
  loader refuses rows outside the window or in a holdout class (hist_bars.py:74). C2 reads ES on es2011 only
  (`evaluate` refuses another root or group, stage_e14_c2.py:288-289) and never MES. C1 reads the six ext2010
  stores (constants.STORE_ROOTS) through load_hist_leg. Nothing in v10 changes behaviour from 2019-05 on: the
  diff to existing modules is config.py (additive block), pull_step2.py (`--plan` branch only, :1126-1128), .gitignore
  and harness_freeze.py's lists; data/stage_e_bars.py is unchanged.
- **E. Spend safety.** ACCOUNT_2_CAP_USD = 249.67 (config.py:85; tests/test_e14_config_v10.py:32). E14 session
  caps 0.00 (config.py:181, :189). acct-2 only (`require_buy_ready` :273-275, E14_BUY_ACCOUNT = ACCOUNT_2_ID
  :192). Only ES in plan es2011; ext2010 at cap 0.00. The 738 new ledger lines are all `event: quote`, acct-2,
  session stage-E.14-2026-10-05, usd and actual_usd 0.00 (96 ES, 107 each of NG, NQ, ZN, 6E, GC, ZC); ledger 27,756
  lines, sha256 0312fbc0b1ca2da652ca7caaab2313ccbbc6920ae3a19d9651ff2e94cd1c48fb at 03:35.
- **F. Calendars.** F-12, F-13.
- **G. C1's code.** q_m1 reproduces with no refit (B above) and no write to the ML ledger (guards.ledger_copy:
  gate0_b_trades writes to a temporary copy; the real file's and the copy's sha256 must be unchanged, q_m1.py:
  `run`); M1 is the annex's M1 (A above); the context restores every patched name by identity, also after an
  exception, refuses nesting and clears the calendar caches (tests/test_c1_context.py:71, :89, :108); C7's equality
  test is tests/test_c1_world.py:78 with the sentinel deviation (F-02).
- **H. Other checks.** Freeze-input hashes: 43 of 43 verify; prereg_C1.md fe4b80fb..., draft a16e8600..., annex
  9685fe80..., state manifest 8a38eeb1..., releases 9a051211... as recorded. E.12 state copy: 51 files, names
  and sizes equal the manifest's, no extra file, all 0444 (contents not read). Tests: 249 passed in the v10, C1
  and harness-freeze files at 03:45 (the three bytecode tests fail only under PYTHONPYCACHEPREFIX, as E.12 ruled,
  and pass without it); the lead's full suite 6,737 passed at 02:45 on the same bytes (mtimes 02:28-02:29 precede
  it). Preflight of the candidate manifest on the working tree: OK.

### Could not check

The GEX < 0 count (135) and the calendar-free bound (146): the brief forbids reading GEX values; only the two
scripts' logic was read (F-09). The Wayback and SqueezeMetrics pages' contents beyond the quoted lines in gex.md.
The behaviour of a real Databento refusal (no network).

## Verification (Task 8)

Verifier: VerdictVerifier-FableXHigh (Fable 5.1, xhigh), 2026-10-05 03:31-03:38 PDT. Every number below was
recomputed from the inputs with my own scripts before the lead's figure for it was read. Scratch:
/tmp/claude-1000/-home-kiros-li-Documents-GitHub-PropExperiment/19c73927-ec62-4304-916b-b9a703235eab/scratchpad/verify/
(c2_count.py, c2_count.out, c1_model_verify.json, m1_verify/, q_m1_run.log). Read-only otherwise; no market data
beyond GEX signs, no .env, no key, no Databento call; holdout untouched.

### Item 1: Test C2's verdict (STOPPED at the power rule)

Inputs used: reports/stage_e14_briefs/gex/DIX.csv (sha256 51bef9ea...9ce62 verified; 3,879 data rows, header
`date,price,dix,gex`, 2011-05-02..2026-10-02, no duplicate or weekend dates, no unparsable gex), the equity
calendar data/calendars/hist2010/equity.json (sha256 b12aee43...657be, byte-identical to
reports/stage_e14_cal_equity.json; 24 full closures, 78 early halts, 6 late opens, 0 unsourced, coverage
2010-06-01..2019-05-31), the draft reports/stage_e13_prereg_gexmom.md sections 2, 3, 7, 9. Eligibility as the brief
defines it: weekday in 2011-05-03..2019-04-30, not a full closure, not an early halt, not a late open, not
unsourced, with a prior trade date, with a lag-1 GEX row (the row of the latest CSV date strictly before d). Only
the sign of gex entered the count.

| Count | Mine | Lead (c2_result.json / gex.md s.4) | Result |
|---|---|---|---|
| weekdays in window | 2,086 | 2,086 | MATCH |
| CME equity trade dates | 2,064 | 2,064 | MATCH |
| excluded: full closure (weekdays) | 22 | 22 | MATCH |
| excluded: early halt / late open | 71 / 6 | 71 / 6 | MATCH |
| excluded: unsourced / no prior / no GEX row | 0 / 0 / 0 | 0 / 0 / 0 | MATCH |
| calendar-eligible dates | 1,987 | 1,987 | MATCH |
| **eligible dates with GEX < 0 (lag 1)** | **135** (share 0.0679) | **135** (0.0679) | **MATCH** |
| calendar-free upper bound (weekdays, lag-1 row negative) | 146 | 146 | MATCH |
| rows dated 2011-05-02..2019-04-29 / negative | 2,011 / 138 | 2,011 / 138 | MATCH |
| stop rule (< 200) fires | yes | yes (STOPPED 01:34) | MATCH |

Robustness of the stop: under the strictest reading of the draft's timing sentence (the row must be dated on the
prior CME trade date itself) the count is 131; under the lag-1 reading 135; the calendar-free bound is 146. The
stop fires under every reading, and the two exclusions not applied (roll blackout, bar presence) can only lower it.
Zero-GEX rows: the CSV holds one (counted as not negative by both implementations). Verdict STOPPED: MATCH.

Section 3 (timing rule, lag 1) on its merits: the capture evidence on disk
(reports/stage_e14_briefs/pages/gex/wayback/capture_last_dates.txt, DIX.csv.headers) supports it. The six evening
captures cited (17:20-18:55 CT) each hold that day's row; `Last-Modified: Fri, 02 Oct 2026 21:57:14 GMT` is
16:57 CDT. The section's disclosed limit (2011-2019 rows most likely computed later, real-time publication not
observable) is right. Revision check: my own hash of the 2,012 rows dated 2011-05-02..2019-04-30 reproduces both
prefixes (all columns d3c8bc82111499f0, date+gex 0ec46859ebf506d9; lines joined by "\n"), and the same 2,012 rows
are identical in all eight Wayback captures on disk. MATCH.

Section 1 (terms ruling) on its merits: the quoted clause is in the captured page (terms.html sha256 695c1bbd...
matches the fetch log; robots.txt is a 404). The clause bars systematic retrieval to compile a database; one
download of the file the free page's own button serves, kept uncommitted and not redistributed, is a defensible
reading, and no publication-time statement exists in docs.html or dix.html (checked by grep). The ruling stands.
See F-V1 for what it leaves undisclosed.

### Item 2: Test C1's q reproduction and M1 hash

Rerun of the frozen code at nice 10 into scratch (03:32:46-03:32:48 PDT, rc 0, 10.8 GB available before launch):
`python -m c1_replication.q_m1 --state ~/.cache/propexp_e14_c1/e12_state_copy --state-manifest
reports/stage_e14_c1_e12_state_manifest.json --state-manifest-sha256 8a38eeb1...1ad9 --out <scratch>/c1_model_verify.json
--model-dir <scratch>/m1_verify`.

| Quantity | Mine (rerun) | E.12 report / lead's model JSON | Result |
|---|---|---|---|
| NG h60: n_trades / n_dates / n_obs | 518 / 330 / 2,590 | 518 / 330 / 2,590 (E.12 and lead) | MATCH (exact) |
| NG h60: mean / t_B | 5.5694980694980805 / 2.5143449337178385 | same (E.12 and lead; abs diff 0.0) | MATCH |
| NG hF: n_trades / n_dates / n_obs | 494 / 283 / 2,473 | 494 / 283 / 2,473 | MATCH (exact) |
| NG hF: mean / t_B | 13.92105263157894 / 2.329878707167312 | same (abs diff 0.0) | MATCH |
| q_h60 | 0.033735277284776724 (OOF rows at or above q: 518 = n_trades, no ties) | 0.033735277284776724 | MATCH |
| q_hF | 0.0831931045522869 (494 = n_trades, no ties) | 0.0831931045522869 | MATCH |
| M1 h60 payload sha256 | 9c2d9986ec788a0abcd08186cf249061f91ed0794d3519532ef779de4ccfb9d8 (1,216 bytes, 67,797 rows, 150 features) | same; ~/.cache/propexp_e14_c1/m1/c1_m1_h60.ridge hashes the same | MATCH |
| M1 hF payload sha256 | 153c2bdc25087e0b2f2f236d46fa186e78bb85fa2d50d8702d4c7e5ac4dfbe99 (1,216 bytes, 64,695 rows) | same; c1_m1_hF.ridge hashes the same | MATCH |
| feature_cols sha256 (150 columns, follow from signals) | af7d43d63b1af935559a745d9708e4657486ef01bc9100e3ddea37aa934ffd1b | same | MATCH |
| ML ledger sha256 unchanged | aacca512e2cdafda5ed8d2cec745b43ebd1e8fa052cde2f2ea2cd0c18eb0bf67 before, after, and the live file now | same | MATCH |
| state dir before == after; v2 freeze (91 files) | true; a647cd06... | same | MATCH |

A structural diff of my JSON against reports/stage_e14_c1_model.json, after removing only the two timestamps and
the model-dir paths, finds no differing key (code_sha256 of all nine c1_replication files, versions, c10_reference,
reproduction rows, e12 facts all equal). The lead's model JSON hashes to c6075306...21e6, as STATE records.

Code reading (independent of the run): in ml_route_v2/gate0.py, `_top_trades` takes the top floor(fraction x n)
|r_hat| among non-zero OOF predictions (stable sort) and `gate0_b_trades` builds NG's trades from those indices, so
the smallest |r_hat| in NG's trade frame is the selection threshold; c1_replication/q_m1.py `q_record` computes
exactly `min(|r_hat|)` over the trades with test_id gate0B_NG_<h>, keeps repr, and counts OOF rows with |r_hat| >= q
(equal to n_trades at both horizons, so no boundary tie). 0.2 x 2,590 = 518 and floor(0.2 x 2,473) = 494 agree with
the trade counts. No refit: `_oof` calls `fit_model` only when a split file is missing, and `no_fits` (guards.py)
rebinds `gate0.fit_model`, the very name `_oof` resolves, to a function that raises and counts; `split_files`
requires every gate0B_<h>_sNN.npy before the call; `fit_attempts` is checked after; and the state dir re-verifies
unchanged (51 files, 45 npy) after the run, so no OOF prediction was recomputed or written. The only fits are the two
deliberate M1 fits per horizon (`fit_m1`, via models.fit_model, outside the guard), whose equal sha256s confirm
determinism. MATCH.

### Item 3: order of events

| Check | Found | Result |
|---|---|---|
| git order | dc93e9b "harness v10, E.14 caps and stores" 03:29:15 PDT, then 1680982 "E.14 freezes..." 03:29:42 PDT | MATCH |
| freeze commit holds reports/stage_e14_prereg_C1.md | yes (216 lines); its sha256 at HEAD afc5c10f...1c0b = STATE line 37; reports/stage_e14_c1_freeze_inputs.json 3356d676...40e = STATE and prereg line 173; freeze_inputs does not reference the prereg (no circular hash) | MATCH |
| v10 manifest sha256 | reports/stage_e2b_harness_freeze.json at dc93e9b, at HEAD and in the worktree all hash fde3a49c...e34b, as prereg_C1.md line 167 and freeze_inputs.json record | MATCH |
| model JSON after the freeze | reports/stage_e14_c1_model.json mtime 03:29:57.54, started_local 03:29:54, created 03:29:57; M1 payloads 03:29:57.53; all after 03:29:42; the JSON is untracked (written after the commit) | MATCH |
| no 2010-2019 byte | no ext2010 / es2011 / 2010 / 2011 name under data/vendor/databento (depth 5); data/processed_hist does not exist | MATCH |
| ledger/databento_spend.jsonl | 27,756 lines; 738 with session_id stage-E.14-2026-10-05 (96 ES.v.0 + 107 x 6 roots), all event "quote", usd 0.0, actual_usd null; shared_cumulative_usd acct-2 231.59973 on every session line, acct-1 last 118.39002 (2026-10-03) | MATCH |
| ledger/trial_registrations.jsonl | one line, entry_id baseline, n_after 471, no C1 or C2 entry | MATCH |
| C2 before any freeze | fetch 00:43 PDT (07:43:01Z), count 01:33 and rerun 02:25, stop 01:34, c2_result.json written 03:26:59, all before 03:29:42; no reports/stage_e14_prereg_C2* exists and git tracks no C2 freeze | MATCH |
| `uv run python -m data.holdout status` | all_ok true, unlocks_logged 0 | MATCH |

### Findings

- F-V1 SHOULD FIX (disclosure, gex.md section 1): the ruling describes the act as "the single download of a file
  the free page offers through its own button", but the record shows the file was fetched with curl carrying
  browser-imitating headers (fetch_record.txt, gex.md section 2) and eight further copies were taken from Wayback
  (pages/gex/wayback/). Neither act is one the quoted terms forbid (the "automated means" clause concerns account
  creation; the Wayback copies are not retrieval from the Platform), so the ruling's conclusion stands, but the
  ruling should state what was actually done. No number changes.
- F-V2 NOTE (gex.md section 4 / c2_result.json): 44 of the 1,987 eligible dates take a lag-1 row dated before the
  prior CME trade date (the prior trade date is a CME early-halt day with no CSV row, so the row is one NYSE day
  older). Under the strictest reading of the draft's timing sentence those dates lack "a GEX row dated on the latest
  trading day strictly before d" and the count is 131. Both readings stop C2; worth one sentence in section 4.
- F-V3 NOTE (c2_result.json): `stopped_at` 01:34:00 PDT, file mtime 03:26:59 PDT. The file records a decision taken
  two hours earlier (after the final calendar rerun at 02:25); still before the freeze commit. Say so in the file or
  add a `written_local` field.
- F-V4 NOTE (gex.md section 3, supportive): the uncited capture 20221205141903 (Monday 2022-12-05 08:19 CT) already
  holds the row dated Friday 2022-12-02, and 20201129154647 (Sunday) holds 2020-11-27. The Monday-morning capture is
  the one piece of evidence that is actually taken before 14:30 CT on d and holds the d-1 row; it strengthens lag 1
  and could be cited.
- F-V5 NOTE (count semantics): one eligible date's lag-1 row has GEX exactly 0; both implementations count it as not
  negative, which is the draft's "GEX < 0". Recorded so the 135 is reproducible to the row.
- F-V6 NOTE (verifier process): my first look at the CSV printed its header with `head -3`, and a redaction that
  should have blanked the values did not apply, so the price, dix and gex values of 2011-05-02 and 2011-05-03 entered
  my context. Nothing was derived from them; every later read used scripts that print counts only. Logged here so the
  "one read of GEX values" record in gex.md is complete.

Grades: BLOCKING 0, SHOULD FIX 1, NOTE 5. Verdict numbers: all MATCH.

### Could not check

Whether the 2011-2019 GEX rows were published in real time (not observable; the lead discloses this). The terms
ruling is the lead's judgment; I checked its evidence and logic, not its legal standing. The lead's own count
scripts were not run (my count is from an independent script); their output files hash as c2_result.json records.
