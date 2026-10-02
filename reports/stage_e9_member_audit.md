# Stage E.9 member audit, cluster K8 (MemberAuditor-K8-FableXHigh)

Worker: worker-xhigh on fable (Fable 5.1), effort xhigh. Brief: reports/stage_e9_briefs/auditor_task3_K8.md.
I wrote none of the code, the specs or the tests. Read-only on the repository except this report and my
scripts and logs under reports/stage_e9_briefs/audit_k8/. No bar file read, no runner call, no freeze
written, no web, no git change.

## Part 1: fidelity audit (Task 3)

Started 2026-10-01 23:10 PDT. Ended 2026-10-01 23:37 PDT.

### Files as audited (sha256)

| File | sha256 |
|---|---|
| strategy/members/k8/__init__.py (0 bytes) | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 |
| strategy/members/k8/_calendar.py | 1e10dc29234abd5fea8431404d3798b99a22b141298d7c45ab924dad35278f3c |
| strategy/members/k8/_releases.py | 2acb8ab3fb2d230aaa482e25909a682338d266fe4d5e4336d6b4bb8735db8ea4 |
| strategy/members/k8/flight.py | 020056632df9eea78bcd60a869a5b71eba7083190ed89d969944a4acb1f81b92 |
| strategy/members/k8/oilcad.py | b64db6b459c047dfba3ebb5ec94b91deba0cd0aace17a4e816ad911d0d5b910c |
| strategy/members/k8/wkndbtc.py | 04847787d465c10f66e8250d860e9ac744cba5ee0c104c55bb3458ab3906a243 |
| tests/test_k8_members_tables.py | 0f0fdbd88ab79ecba1eb0d0978f7eb40f8288a646194153c46f5505520d7ea38 |
| tests/test_k8_members_flight.py | e05986b70134d13418526bf1a603fec1c99a6b7a64299543b4a746b4d3791492 |
| tests/test_k8_members_flight_exits.py | 97d770f841efae4d7117e27b00bc94b7347db9ab9967279cfd18ad36d45e1648 |
| tests/test_k8_members_flight_engine.py | 78ce2f12b64d5c1a103b0d43a55020bb00d8b460bf9114256eb4c0c16023e4a8 |
| tests/test_k8_members_oilcad.py | 9c84f2bb5a8a6a1901fc5fddbadbaceb6fea31b348a574ad95bdc9254a5d51b4 |
| tests/test_k8_members_wkndbtc.py | fe6708d3e1aeaa28f9c1ec72203a6ed4ec567bfeedf78ad6251df1f9f4a65cb7 |
| reports/stage_e9_member_specs.md | 3478d9ed1ac0bef13ece6a74db434471bca48b003dc855c26afeea2cf32b8a97 |
| reports/stage_e0_catalog_K8.md | 6bfe1add0f0824799c71666c9cc1267fb0d85276ccc8b2ea15d8345c34e691b9 |
| reports/stage_e9_briefs/gen_k8_tables.py | 77c5041f77cbbad04b464f6c6a8eeab9a47a2dd57f762af9ff641c8054e7f721 |
| reports/stage_e9_briefs/write_k8_freeze.py | 3860ba3725777c272e5f4073cf2b726feae86cfb887aea1c6ec3f06d1a32dd78 |
| reports/stage_e2b_release_calendar.json | 839f2437bedbeb7b3423d7058a9955a0d4ccd1aebc4b01c62be624ab11d7bcb8 |

Baseline: `nice -n 10 uv run pytest -q` on the six K8 test files (no PYTHONPYCACHEPREFIX): 209 passed in
4.9 s. `screening.stage_e_freeze.check_member_source` on every *.py under strategy/members/k8/: no finding
(audit_k8/static_and_decls.log). `write_k8_freeze.py --dry-run`: 4 declarations, ordinals 1-4, traded leg
first, as S0.2. git status at the end: only the untracked E.9 files the lead listed, plus audit_k8/.

My scripts and logs (reports/stage_e9_briefs/audit_k8/): recompute_tables.py (+ .log), static_and_decls.py
(+ .log), engine_checks.py (+ .log), coverage_intervals.py (+ .log), k8audit_mutplugin.py, mutants.py,
mutants_run.log, mutants_results.json, mutants/ (the mutated sources), mutlogs/ (one pytest log per
mutant).

### How the engine serves the members (read, not assumed)

- screening/stage_e_engine.py `iter_minutes` (239-266): the grid is the union of the legs' bar opens; a
  leg without a bar at a minute is absent (no forward fill). `step` (618-657): at grid minute ts the
  engine first fills pending market orders at the OPEN of this minute's traded-leg bar
  (`fill_pending_at_open`, 494-518, through `StageERules.admit_fill`), then checks MLL and forced
  reasons, then calls the member (`ask_member`, 589-617) with `MinuteView(ts, bars opening at ts)`; the
  intent is stamped ts + 60 s (`decision_ts`) and refused `engine_intent_timestamp_mismatch` otherwise
  (stage_e_rules.py 476-480). So a bar shown to the member has closed (open + 60 s = the decision
  instant), an intent on the view at t - 1 fills at the open of the leg's next bar (t when present), and
  the account the member sees at minute m already holds the fill made at m's open (K8-L-07).
- `_Run.visible` (584-587) masks the hindsight field (`vendor_degraded_day`). The members read only
  `ts_event_ns`, `close`, `instrument_id`, `trade_date` on bars and `position`/`pending` on the account
  (audit_k8/static_and_decls.log, [fields] rows).
- stage_e_rules.py `structural_refusal` (474-503): a signal-leg intent is refused `engine_not_a_traded_leg`;
  an open while any leg the member reads has no bar at the minute is refused `engine_leg_missing_bar`
  (D11.5); `_opening_refusal` (505-546) refuses opens outside `window_dates` and on `blackout` dates.
  stage_e_runner.py 425-455 builds both from `screening.stage_e_align.member_window` over EVERY declared
  leg's frame (the intersection of trade dates less the union of every leg's roll blackouts less UR-1;
  stage_e_align.py 57-78) and passes `mw.blackout_union` as `blackout`. `member_coverage` (432) runs on
  every leg over `mw.dates` with the member's `trading_windows`.
- `admit_fill` (375-401): a strategy order whose fill bar opens inside `releases.in_fill_guard(root, ·)`
  is deferred (D9.5a); `ReleaseCalendar.in_fill_guard` (138-140) tests R <= t < R + 120 s for the latest
  R <= t of `by_root[root]`, built from every calendar row whose "products" include the root (153-170).

### Table recomputation (item 5): my own code against the modules

recompute_tables.py classifies every calendar day 2019-05-01..2026-06-19 directly from
`data.group_session.load_group_calendar(group)` and `rules.sessions.flatten_time_ct(root, d)` (not the
generator's code) and compares with the modules. Results (audit_k8/recompute_tables.log):

| Set | Mine | Module | Research window | Differences |
|---|---|---|---|---|
| EQUITY_FULL_SESSIONS (MES, MNQ agree on F every date) | 1779 | 1779 | 303 | none |
| CRYPTO_FULL_SESSIONS (MBT) | 1782 | 1782 | 304 | none |
| METALS_FULL_SESSIONS (MGC) | 1783 | 1783 | 304 | none |
| ENERGY_FULL_SESSIONS (MCL) | 1783 | 1783 | 304 | none |
| FX_FULL_SESSIONS (6C) | 1783 | 1783 | 304 | none |
| FLIGHT_DATES = EQUITY & METALS | 1779 | 1779 | 303 | none; sorted |
| OILCAD_DATES = ENERGY & FX | 1783 | 1783 | 304 | none; sorted |
| WKNDBTC_DATES = EQUITY & CRYPTO | 1779 | 1779 | 303 | none; sorted |
| Research Mondays d with d, d-3 in WKNDBTC_DATES | 54 (3 after 2026-05-29: 06-01, 06-08, 06-15) | | | the 9 excluded: 2025-04-21, 05-26, 07-07, 09-01, 12-01, 2026-01-19, 02-16, 04-06, 05-25 (as Task 1b B) |
| GUARD_INSTANTS["MGC"] | 312 | 312 | 52 | none; equals the engine's `by_root["MGC"]` (312) |
| GUARD_INSTANTS["6C"] | 513 | 513 | 88 | none; equals `by_root["6C"]` (513) |
| GUARD_INSTANTS["MNQ"] | 313 | 313 | 53 | none; equals `by_root["MNQ"]` (313) |

Other facts checked: no weekend is an EC-CAL trade date; the only weekday non-trade dates that are not
full closures are 31 crypto booked-forward days; the dates where "no early halt" and "F = 15:08" disagree
are 2024-07-03 (crypto, metals, energy: halt none, F 11:30) and 31 FX US-holiday dates 2022-2026 (halt
none, F 11:30 or 11:45), all removed by the F test as S0.8 requires; every calendar row naming a K8 root
is dated inside the table range (the date filter is not binding) and every row's CT date equals its
"date"; GUARD_ROWS holds WPSR-2025-12-29 and WPSR-2026-05-28 (R-1b-1, no correction); `in_guard` agrees
with the engine's `in_fill_guard` at every instant's edges (R - 120 s, R - 60 s, R - 1 ns, R, R + 1 s,
R + 59 s, R + 60 s, R + 61 s, R + 119 s, R + 120 s - 1 ns, R + 120 s, R + 121 s, R + 180 s) for all 1,138
instants: 0 disagreements. Research-window instants that meet a K8 fill minute: MGC 10 (the FOMC 13:00
CT dates 2025-05-07 .. 2026-06-17), 6C 73 (56 WPSR 09:30, 7 WPSR 11:00 including 2026-05-28, 10 FOMC
13:00), MNQ 0: Task 1b A3 confirmed.

Comparison with the earlier clusters' frozen tables (over 2019-05-01..2026-06-18, their range): equity
(k1) and crypto (k7) identical; metals (k5) and energy (k4) hold 2024-07-03, which the K8 F test removes
(those tables tested the early halt only); fx (k3) holds 14 US-holiday dates 2022-01-17 .. 2023-11-23
that K8 removes (K3's table was generated under rules/sessions.py d9a7fcfe..., before E.5's pre-2024
holidays). The K8 set is never larger than an earlier set. All differences are in the confirmation
window; none touches K8's research-window behaviour. Coder A's section 2 table says the same.

### Checklist per member (items 1-13; verdict and file:line)

Legend: OK = implements the frozen entry as the specs restate it; see F-n = a finding below.

**K8-flight-01 (strategy/members/k8/flight.py; trials 1 and 2)**

| Item | Check | Verdict | Where |
|---|---|---|---|
| 1 | 77 blocks, t_k = 08:30 + 5k, 08:35..14:55; bars t_k - 1 and t_k - 6 (08:34 and 08:29 for k = 1); 20 reference dates; n >= 1,200; m = (n + 199) // 200 = ceil(0.005 n); the m-th smallest with duplicates; r_k < 0; H30 intent at min(T_e + 29, 15:04); HEOD at 15:04 | OK | flight.py:75-84, 96-98, 124-131, 134-136, 183-186, 267-274 |
| 2 | BUYS MGC (literal "buy"); exit side opposite to the position | OK | flight.py:264, 286 |
| 3 | T_e = open of the first view showing the position (K8-L-07); exit on the first present MGC bar at or after the exit bar; refused exit resent (nothing pending); flat account sends nothing; nothing after the 15:05 fill (last exit bar 15:04; the engine's F is the backstop) | OK | flight.py:276-287, 297-300; engine check audit_k8/engine_checks.log (HEOD fill 15:05) |
| 4 | q_c from load_frozen_tables().vehicles["MGC"].q_c, never a literal; exit for abs(position); only MGC intents (leg_market_intent on TRADED only) | OK | flight.py:180, 264, 287 |
| 5 | FLIGHT_DATES and GUARD_INSTANTS["MGC"] recomputed: identical | OK | table above |
| 6 | Signal bars read only from the view's own minute (closed at the decision) or from earlier views (`_starts`); a bar is keyed by its own open minute, so a late bar is never the earlier minute's bar; a missing t_k - 1 or t_k - 6 bar makes r_k undefined; the intent is on the view at t_k - 1 and fills at the MGC open at t_k or later; no hindsight field read; release instants and calendars are literal tables of scheduled instants | OK | flight.py:207-239, 256-264; engine check: 1607 views, 0 bars not opening at the view minute |
| 7 | MES block bars require CT date == trade_date (evening bars rejected); the MGC entry bar must carry trade_date d (same instant as the MES bar, so the same CT date) | OK | flight.py:212-215, 260-261 |
| 8 | d in FLIGHT_DATES (EQUITY & METALS full sessions, K8-L-03); reference dates = the 20 FLIGHT_DATES strictly before d, roll-blackout dates included (K8-L-04); warm-up K4-L-09 (no trade while refs[0] precedes the first bar's trade date); r_k per computation with one instrument_id (K8-L-05); the union blackout is the runner's (member_window over both legs) and nothing in the member contradicts it | OK; see F-1, F-3 | flight.py:243-248, 237, 292-295; engine test test_a_roll_blackout_of_the_signal_leg_only_blocks_the_entry_v16a |
| 9 | C6 tests the fill minute t_k = view.decision_ts_ns against GUARD_INSTANTS["MGC"] = the engine's D9.5a set; a skipped trigger keeps the day's entry; exits never guarded; against the real release calendar through the engine: 13:00 skipped on FOMC 2025-06-18, 13:05 enters, no fill_guard_deferral | OK | flight.py:256-258; audit_k8/engine_checks.log |
| 10 | Nothing against F (last fill 15:05), the entry cap (1 a day), the 2-minute rule (hold >= 10 min), D11.5 (no intent when the MES bar is missing), D9.7 (MGC DCB_ONLY; a flat account after any engine close sends nothing and `_done` stays set); trading_windows MGC (08:34, 15:06), MES (08:29, 14:55) = S0.12; the sessions never clip either interval on any research date | OK | flight.py:189-193, 297-300; audit_k8/coverage_intervals.log |
| 11 | No extra filter, guard, re-entry, size rule or state beyond the entry and the specs' narrowings (one entry per d via `_done`; the history pruning is bookkeeping) | OK; see F-5 | flight.py:148-174 |
| 12 | make_h30 / make_heod; names "K8-flight-01 H30 MGC", "K8-flight-01 HEOD MGC"; legs (MGC traded, MES signal); static check clean; __init__.py 0 bytes; freeze dry run matches | OK | flight.py:178-179, 307-312 |
| 13 | Tests pin the prompt's cases and failed on every one of my mutants (table below) | OK; see F-6 | tests/test_k8_members_flight*.py |

**K8-oilcad-01 (strategy/members/k8/oilcad.py; trial 3)**

| Item | Check | Verdict | Where |
|---|---|---|---|
| 1 | T = 08:05..13:25 step 5 (65); bars t - 1 and t - 6; 20 reference dates; n >= 1,000; statistics.stdev (ddof 1); s = 0 no trade; abs(r / s) >= 2.0 in float; exit intent at T_e + 14 | OK | oilcad.py:62-70, 80-88, 101-121, 152-153, 238 |
| 2 | BUY if c1 > c6 (z > 0), SELL if c1 < c6 (diff = c1 - c6 in ticks; diff = 0 unreachable under |z| >= 2 with s > 0) | OK | oilcad.py:195, 262 |
| 3 | T_e = first view showing the position; exit on the first present 6C bar at or after T_e + 14 while nothing is pending; resent after a refusal; engine closures leave the account flat and later decisions apply (K7-L-07); last fill 13:40 | OK | oilcad.py:219-241; engine tests test_engine_closure_leaves_the_account_flat..., test_engine_nothing_after_the_13_40_fill |
| 4 | q_c from the frozen vehicle table; exit abs(position); 6C intents only | OK | oilcad.py:148, 241, 263 |
| 5 | OILCAD_DATES and GUARD_INSTANTS["6C"] recomputed: identical | OK | table above |
| 6 | MCL bars keyed by own open minute; the t - 6 close is kept per decision t and cleared each MCL day; a late bar is never a substitute; missing bar: r_t undefined; the entry is on the view at t - 1 (the 6C bar of that minute) and fills at t or later; the C6 test uses t = bar open + 60 s | OK | oilcad.py:173-199, 243-263; engine check (real calendar): 09:30 skipped on 2025-07-09, 09:35 fills; 13:00 skipped on FOMC 2025-07-30; 11:00 skipped on 2026-05-28 (R-1b-1); no fill_guard_deferral in any knowable case |
| 7 | MCL bars read on their own CT date only; the 6C entry bar must open on CT date == its trade_date | OK | oilcad.py:180-183, 249-251 |
| 8 | d in OILCAD_DATES; reference dates roll-blackout dates included; warm-up K4-L-09; per-computation instrument guard; union blackout by the runner, pinned end to end (test_engine_refuses_on_a_signal_leg_roll_blackout_date_only) | OK; see F-1, F-2, F-3 | oilcad.py:191, 201-210, 252 |
| 9 | C6 skips the decision whose fill minute t is guarded for 6C; 09:35 not skipped; exits unguarded; the engine's D9.5a set is the same set (recomputed) | OK | oilcad.py:260-261 |
| 10 | <= 17 entries a day, 15-minute holds, entries >= 20 min apart (the exit view blocks t_e + 15; test_engine_spacing...), nothing after 13:40; D11.5 never needed; 6C DCB_ONLY; trading_windows 6C (08:04, 13:41), MCL (07:59, 13:25) = S0.12; never clipped | OK | oilcad.py:158-163; audit_k8/coverage_intervals.log |
| 11 | Nothing beyond the entry and the specs | OK | |
| 12 | make_6c; name "K8-oilcad-01 6C"; legs (6C traded, MCL signal); static check clean | OK | oilcad.py:148-151, 266-267 |
| 13 | Tests pin the prompt's cases; every mutant of mine killed | OK; see F-6 | tests/test_k8_members_oilcad.py |

**K8-wkndbtc-01 (strategy/members/k8/wkndbtc.py; trial 4)**

| Item | Check | Verdict | Where |
|---|---|---|---|
| 1 | P_F = MBT 14:59 on CT date d - 3 (trade_date d - 3); P_S = MBT 17:59 on CT date d - 1 (trade_date d); entry on the MNQ 17:59 bar of CT date d - 1 (trade_date d), fill 18:00; exit intent 14:58 on d, fill 14:59 | OK | wkndbtc.py:57-62, 129-134, 161-183 |
| 2 | BUY if P_S - P_F > 0 in ticks, SELL if < 0, G = 0 no trade | OK | wkndbtc.py:88-94, 177-179 |
| 3 | Exit on the first present MNQ bar at or after Monday 14:58 (ct_ns(d, 14:58)) while nothing is pending; resent after a refusal; flat account sends nothing; last fill 14:59 | OK | wkndbtc.py:151-159, 182 |
| 4 | q_c from the frozen vehicle table; exit abs(position); MNQ intents only | OK | wkndbtc.py:114, 159, 183 |
| 5 | WKNDBTC_DATES and GUARD_INSTANTS["MNQ"] recomputed: identical; 54 eligible research Mondays | OK | table above |
| 6 | P_F is kept from an earlier view (closed); P_S is the view's own MBT bar (closed at the 18:00 decision); the MNQ intent is on the 17:59 view and fills at the 18:00 open; a missing Friday 14:59, Sunday 17:59 or MNQ 17:59 bar means no trade; a bar at 15:00 / 18:00 is never the 14:59 / 17:59 bar (exact clock match); C6 on the 18:00 fill minute | OK | wkndbtc.py:129-134, 161-183; engine check (real calendar): fill Sun 18:00, exit Mon 14:59, no deferral |
| 7 | Both regimes: the Sunday 17:59 bar must carry trade_date d; the Friday store keeps only 14:59 bars whose CT date is their trade_date (so post-2026-06-01 Saturday/Sunday 14:59 bars booked to Monday are never P_F); holiday Mondays and the Mondays after Good Friday or a Friday halt excluded through d and d - 3 in WKNDBTC_DATES | OK | wkndbtc.py:82-85, 132, 169-173 |
| 8 | EQUITY & CRYPTO full sessions for d and d - 3 (K8-L-03, K8-L-12); one instrument_id across P_F and P_S; the union blackout by the runner, pinned end to end; a Friday-only MBT blackout does not block d (K8-L-12, pinned) | OK | wkndbtc.py:85, 175-176 |
| 9 | C6 at the 18:00 fill on GUARD_INSTANTS["MNQ"]; no research-window instant there (recomputed); exits unguarded | OK | wkndbtc.py:180-181 |
| 10 | 1 entry a week, hold 20 h 59 min; nothing after 14:59; D9.7 equity bands are the engine's (a forced exit leaves the account flat; the member's only entry view is Sunday 17:59); trading_windows = S0.12; never clipped by the equity or crypto sessions on any research date | OK; see F-7 | wkndbtc.py:120-127; audit_k8/coverage_intervals.log |
| 11 | Nothing beyond the entry | OK | |
| 12 | make_mnq; name "K8-wkndbtc-01 MNQ"; legs (MNQ traded, MBT signal); static check clean | OK | wkndbtc.py:114-117, 186-187 |
| 13 | Tests pin the Friday and Sunday clock points, both regimes, G = 0, the exclusions, C6, the exit; every mutant of mine killed | OK; see F-6 | tests/test_k8_members_wkndbtc.py |

### Item 6 in detail: availability and cross-leg timing

For every K8 decision the signal bar used last is the bar at t - 1 of the signal leg: it opens at t - 1
and is handed to the member in the view whose `ts_event_ns` is t - 1, at decision instant t (bar close).
The member's intent is stamped t and the engine fills it at the open of the traded leg's bar at t (the
first traded bar at or after t). My spy over 1,607 engine views (audit_k8/engine_checks.log, [timing])
found no bar in any view opening at a minute other than the view's. The only earlier bars a member
holds are its own earlier views' bars (flight `_starts`, oilcad `_firsts`, wkndbtc `_friday`), each keyed
by that bar's own open, so a bar arriving at a later minute never stands in for an earlier minute (pinned:
test_an_mes_bar_absent_at_tk_minus_1_and_present_at_tk_is_never_used, test_mcl_bar_arriving_late_is_never_
used, test_sunday_17_59_mbt_missing_17_58_never_used_and_the_late_18_00_bar_neither; my mutants AF55,
AO43, AW32, AW33). A None is never a price (all three members return () or leave the computation
undefined). No member reads a hindsight or calendar flag off a bar; the release instants and full-session
dates are literal tables of scheduled facts known before d.

### Item 9 in detail: C6's skip set and the engine's D9.5a set

GUARD_INSTANTS[root] equals the engine's `ReleaseCalendar.by_root[root]` exactly (312 / 513 / 313
instants) and `in_guard` equals `in_fill_guard` at every edge, so an entry the member emits (fill minute t
with `in_guard(root, t)` False) can never be deferred by `admit_fill` when the traded bar at t is present.
Through the real engine with the real frozen calendar (audit_k8/engine_checks.log): oilcad 2025-07-09
(WPSR 09:30 CT) with triggers at 09:30 and 09:35 fills once at 09:35, exits 09:50; FOMC 2025-07-30 fills
13:05 only; 2026-05-28 fills 11:05 only (R-1b-1); flight on FOMC 2025-06-18 fills 13:05 and exits 13:35
(H30) / 15:05 (HEOD); `fill_guard_deferral` is absent from every counter. The one deferral the engine
can still make is the edge the specs log under K8-L-08: a trigger at 09:25 whose 6C bars 09:25..09:29 are
missing fills at 09:32 with `fill_guard_deferral` 2 (deferred at the 09:30 and 09:31 bars). The member
cannot know at 09:24 that the 09:25 bar will be missing, so this is not a skip the member could make
(see F-8).

### Item 14: the lead's readings (one line each)

| Reading | Verdict | Note |
|---|---|---|
| K8-L-01 declarations, labels, leg order | fixed by the template (step 3) and C section 5 | code and freeze script match |
| K8-L-02 bars by CT date and clock per leg | fixed by E.3-L-03, K7-L-01 | implemented in all three |
| K8-L-03 every leg's own group calendar; "equity-and-crypto" = both calendars | narrowest the text allows | reading "equity-and-crypto" as one joint calendar would add nothing in the research window (EQUITY is a subset of CRYPTO there: crypto keeps 2025-07-03) and the text ("any leg's D10 group calendar") points to the leg's own calendar; agree |
| K8-L-04 reference dates = full-session dates, roll-blackout dates included | fixed by K5-L-05, K4-L-08 (cited); NOT the literal text | C5 line 126-128 says a rolling statistic uses dates "that pass these exclusions", which include the traded leg's roll blackout; the member has no roll input and the engine removes those dates as trade dates. I would take the same reading for consistency with K4/K5; recorded as F-3 for the lead's awareness. The sentence "a reference date on which a leg has no bars at all contributes no values" is implemented for the signal leg (the only leg that yields values); see F-1 |
| K8-L-05 per-computation instrument and presence guard | fixed by C4 lines 110-111 and the entries' text | agree |
| K8-L-06 flight: a missing entry bar ends the day; oilcad: per decision; wkndbtc: no trade | flight and wkndbtc: the text (C5 line 119); oilcad: fixed by K4-L-14 (cited) | a stricter causal alternative for oilcad exists (no further entry on d once a 6C bar at a t - 1 minute is missing) and is not what the text says either; the per-decision reading matches K4-L-14; agree, recorded as F-2 |
| K8-L-07 T_e = the actual fill minute | fixed by the text ("T_e is the entry fill minute", C 288, 418) | implemented as the first view showing the position, which the engine makes the fill minute |
| K8-L-08 C6's set = the engine's D9.5a set for the traded root | fixed by C6's first sentence; verified: the two sets are identical and no other instant meets a K8 fill minute in the research window | agree; the logged edge is real (engine check) and is the engine's deferral, not a member skip |
| K8-L-09 exact rational for flight; float stdev for oilcad; tick-sign sides | narrowest/precedent (E.3-L-19, K4-L-05) | the integer-pair compare equals Fraction's (test_compare_and_trigger_are_exact_beyond_float; my AF19 killed). "Equality |z| = 2.0 reported if it occurs" cannot be done by a member; it belongs to the Task 6 recomputation (Part 2) |
| K8-L-10 c6 > 0 for flight | narrowest; cannot change a decision on real bars | agree |
| K8-L-11 flat = no position and no pending order of either side | narrowest (the text names only a pending exit) | agree; implemented oilcad.py:229-230 |
| K8-L-12 wkndbtc's dates and the Friday/Sunday MBT roll | fixed by the text (C 524-527, 539-543) and V16(a) | agree; a Friday-only MBT blackout leaves the trade to the instrument test, pinned |
| K8-L-13 trading_windows as S0.12 | fixed by E.3-L-17 | agree; the wkndbtc intervals are measured on every window date (F-7) |
| K8-L-14 tables span 2019-05-01..2026-06-19 | fixed by K3-L-01, K4-L-01 | the date filter is not binding on the release rows |
| K8-L-15 section 6 settled by V16 and the frozen text | fixed by V16 (1-4) and the frozen calendar (5) | agree; (6) C6 as written is what the code does |
| K8-L-16 the N rule | fixed by K1-L-16, pre-declared | no member effect |
| K8-L-17 two coders | organisational | both reports exist; B's saved by the lead |
| R-1b-1 the E.4-dropped WPSR rows stay in GUARD_INSTANTS | right: skipping there is what keeps the fill from being deferred (the engine's set still holds them); dropping them would make the member enter at 11:00 on 2026-05-28 and the engine defer to 11:02, which C6 forbids | agree; verified end to end |
| R-1b-2 MES roll blackouts are the runner's | agree; not a member input | |
| R-1b-3 2026-06-01 a crypto full session | consistent with K7-L-02 and K6 S0.8; moot (MBT roll blackout) | recomputed: in CRYPTO_FULL_SESSIONS |
| R-1b-4 unscheduled items not added | agree (hindsight otherwise) | |
| R-1b-5, R-1b-6 counts for the return | arithmetic; 54 Mondays, 51 + 3 confirmed | |

### Mutants (item 13)

Method: audit_k8/mutants.py replaces one unique source fragment of one module, writes the mutated text
under audit_k8/mutants/<id>.py, and audit_k8/k8audit_mutplugin.py (a pytest plugin passed with `-p`)
installs it in sys.modules under the real module name before collection, so nothing under strategy/ or
tests/ is modified (sha256 of every K8 source and test file verified unchanged at the end). The six K8
test files run per mutant (`nice -n 10 uv run pytest -q -rf -p no:cacheprovider`). Five no-op injections
(the real source through the plugin) pass 209/209 each, so the harness itself changes no outcome. My
mutants were written from the frozen entries before reading the coders' mutant tables.

Totals: 146 mutants, 143 killed, 3 survived (AF41, AC04, AC05), 0 badly built (none); controls ['control_ok', 'control_ok', 'control_ok', 'control_ok', 'control_ok']; guarded files changed: none; wall time 11.5 min.

| Id | Module | Mutant | Result | Tests failing (count; first two) |
|---|---|---|---|---|
| AF01 | flight | block clock starts 08:31 | killed | 56; test_trading_windows_are_the_s0_12_intervals, test_the_entry_size_is_the_frozen_q_c |
| AF02 | flight | 4-minute blocks | killed | 56; test_trading_windows_are_the_s0_12_intervals, test_the_entry_size_is_the_frozen_q_c |
| AF03 | flight | 78 blocks | killed | 4; test_trading_windows_are_the_s0_12_intervals, test_decision_times_are_0835_to_1455_every_5_minutes |
| AF04 | flight | 76 blocks | killed | 4; test_trading_windows_are_the_s0_12_intervals, test_decision_times_are_0835_to_1455_every_5_minutes |
| AF05 | flight | end bar t_k - 2 | killed | 55; test_trading_windows_are_the_s0_12_intervals, test_the_entry_size_is_the_frozen_q_c |
| AF06 | flight | start bar t_k - 5 | killed | 55; test_trading_windows_are_the_s0_12_intervals, test_the_entry_size_is_the_frozen_q_c |
| AF07 | flight | start bar t_k - 7 | killed | 55; test_trading_windows_are_the_s0_12_intervals, test_the_entry_size_is_the_frozen_q_c |
| AF08 | flight | 19 reference dates | killed | 52; test_the_entry_size_is_the_frozen_q_c, test_k1_reads_the_0829_and_0834_bars |
| AF09 | flight | 21 reference dates | killed | 51; test_the_entry_size_is_the_frozen_q_c, test_k1_reads_the_0829_and_0834_bars |
| AF10 | flight | n >= 1,199 | killed | 2; test_threshold_m_and_the_value_floor, test_member_n_1199_is_no_trade_and_n_1200_trades |
| AF11 | flight | n >= 1,201 | killed | 3; test_threshold_m_and_the_value_floor, test_m_is_ceil_of_n_over_200[1200-6] |
| AF12 | flight | tail 1/199 | killed | 4; test_threshold_m_and_the_value_floor, test_m_is_ceil_of_n_over_200[1200-6] |
| AF13 | flight | m = floor(n/200) | killed | 11; test_r_equal_to_q_in_another_form_triggers, test_threshold_m_and_the_value_floor |
| AF14 | flight | (m+1)-th smallest | killed | 11; test_threshold_m_and_the_value_floor, test_threshold_counts_duplicates |
| AF15 | flight | H30 intent T_e + 30 | killed | 8; test_a_second_trigger_while_long_and_after_the_exit_does_nothing, test_h30_exit_is_sent_on_the_bar_at_te_plus_29 |
| AF16 | flight | H30 intent T_e + 28 | killed | 11; test_a_second_trigger_while_long_and_after_the_exit_does_nothing, test_h30_exit_is_sent_on_the_bar_at_te_plus_29 |
| AF17 | flight | exit bar 15:05 | killed | 6; test_trading_windows_are_the_s0_12_intervals, test_heod_exit_is_sent_on_the_bar_at_1504 |
| AF18 | flight | exit bar 15:03 | killed | 9; test_trading_windows_are_the_s0_12_intervals, test_heod_exit_is_sent_on_the_bar_at_1504 |
| AF19 | flight | float compare | killed | 1; test_compare_and_trigger_are_exact_beyond_float |
| AF20 | flight | c6 = 0 allowed | killed | 1; test_block_return_is_the_tick_ratio_and_needs_c6_positive |
| AF21 | flight | r over c1 | killed | 1; test_block_return_is_the_tick_ratio_and_needs_c6_positive |
| AF22 | flight | no r < 0 condition | killed | 2; test_trigger_needs_r_negative_even_at_or_below_q, test_a_positive_q_never_triggers_a_non_negative_r |
| AF23 | flight | r < Q strict | killed | 7; test_r_equal_to_q_in_another_form_triggers, test_member_n_1199_is_no_trade_and_n_1200_trades |
| AF24 | flight | ticks truncated | killed | 1; test_ticks_round_a_near_grid_float_to_the_nearest_tick |
| AF25 | flight | no MES instrument guard | killed | 2; test_an_mes_roll_inside_a_block_is_no_trigger_and_later_blocks_trigger, test_undefined_reference_computations_are_not_values |
| AF26 | flight | no MES CT-date check | killed | 1; test_a_bar_whose_trade_date_is_not_its_ct_date_is_not_a_block_bar |
| AF27 | flight | d need not be a FLIGHT date | killed | 1; test_a_non_full_date_is_skipped_as_a_reference_and_as_d |
| AF28 | flight | no warm-up | killed | 1; test_warm_up_the_20th_date_does_not_trade_and_the_21st_does |
| AF29 | flight | fewer than 20 refs accepted | killed | 1; test_fewer_than_20_reference_dates_at_the_tables_start_is_no_trade |
| AF30 | flight | C6 tests the entry-bar minute | killed | 5; test_values_of_d_itself_never_enter_q_of_d, test_c6_skips_the_1300_trigger_on_an_fomc_date_and_enters_at_1305 |
| AF31 | flight | no C6 | killed | 5; test_values_of_d_itself_never_enter_q_of_d, test_c6_skips_the_1300_trigger_on_an_fomc_date_and_enters_at_1305 |
| AF32 | flight | C6 skip uses the day's entry | killed | 5; test_values_of_d_itself_never_enter_q_of_d, test_c6_skips_the_1300_trigger_on_an_fomc_date_and_enters_at_1305 |
| AF33 | flight | missing entry bar does not end the day | killed | 2; test_a_missing_entry_bar_at_the_first_trigger_ends_the_day, test_an_entry_bar_of_another_trade_date_counts_as_missing |
| AF34 | flight | entry bar trade date unchecked | killed | 1; test_an_entry_bar_of_another_trade_date_counts_as_missing |
| AF35 | flight | entry while pending | killed | 1; test_no_entry_while_an_order_is_pending_on_mgc |
| AF36 | flight | sells | killed | 51; test_the_entry_size_is_the_frozen_q_c, test_k1_reads_the_0829_and_0834_bars |
| AF37 | flight | q_c + 1 | killed | 49; test_the_entry_size_is_the_frozen_q_c, test_k1_reads_the_0829_and_0834_bars |
| AF38 | flight | every trigger enters | killed | 7; test_only_the_first_trigger_of_d_enters_even_when_refused, test_a_second_trigger_while_long_and_after_the_exit_does_nothing |
| AF39 | flight | HEOD exits like H30 | killed | 5; test_heod_exit_is_sent_on_the_bar_at_1504, test_a_missing_exit_bar_sends_the_exit_on_the_first_later_bar[HEOD-missing2-905] |
| AF40 | flight | H30 uncapped | killed | 3; test_h30_exit_is_capped_at_1504[74-904], test_h30_exit_is_capped_at_1504[77-904] |
| AF41 | flight | T_e one minute late | SURVIVED | 0;  |
| AF42 | flight | exit while pending | killed | 2; test_a_second_trigger_while_long_and_after_the_exit_does_nothing, test_a_refused_exit_is_resent_and_a_pending_exit_is_not_duplicated |
| AF43 | flight | exit one bar late | killed | 14; test_a_second_trigger_while_long_and_after_the_exit_does_nothing, test_h30_exit_is_sent_on_the_bar_at_te_plus_29 |
| AF44 | flight | exit side reversed | killed | 18; test_a_second_trigger_while_long_and_after_the_exit_does_nothing, test_h30_exit_is_sent_on_the_bar_at_te_plus_29 |
| AF45 | flight | exit quantity + 1 | killed | 18; test_a_second_trigger_while_long_and_after_the_exit_does_nothing, test_h30_exit_is_sent_on_the_bar_at_te_plus_29 |
| AF46 | flight | T_e not reset when flat | killed | 1; test_t_e_resets_when_flat |
| AF47 | flight | only negative r recorded | killed | 54; test_the_entry_size_is_the_frozen_q_c, test_k1_reads_the_0829_and_0834_bars |
| AF48 | flight | prune the oldest reference | killed | 3; test_member_n_1199_is_no_trade_and_n_1200_trades, test_member_m_at_1201_and_1540 |
| AF49 | flight | a filed date keeps no values | killed | 54; test_the_entry_size_is_the_frozen_q_c, test_k1_reads_the_0829_and_0834_bars |
| AF50 | flight | signal leg declared first | killed | 1; test_declarations_names_legs_and_factories |
| AF51 | flight | label order | killed | 1; test_declarations_names_legs_and_factories |
| AF52 | flight | MGC window ends 15:05 | killed | 1; test_trading_windows_are_the_s0_12_intervals |
| AO01 | oilcad | first t 08:00 | killed | 3; test_trading_windows_are_s0_12, test_decision_clock_is_08_05_to_13_25_every_5_minutes |
| AO02 | oilcad | last t 13:30 | killed | 3; test_trading_windows_are_s0_12, test_decision_clock_is_08_05_to_13_25_every_5_minutes |
| AO03 | oilcad | last t 13:20 | killed | 4; test_trading_windows_are_s0_12, test_decision_clock_is_08_05_to_13_25_every_5_minutes |
| AO04 | oilcad | 10-minute step | killed | 32; test_decision_clock_is_08_05_to_13_25_every_5_minutes, test_first_and_last_decisions_trade |
| AO05 | oilcad | c1 bar t - 2 | killed | 32; test_trading_windows_are_s0_12, test_first_and_last_decisions_trade |
| AO06 | oilcad | c6 bar t - 5 | killed | 32; test_trading_windows_are_s0_12, test_first_and_last_decisions_trade |
| AO07 | oilcad | 19 reference dates | killed | 31; test_first_and_last_decisions_trade, test_r_t_reads_the_mcl_bars_at_t_minus_1_and_t_minus_6 |
| AO08 | oilcad | n >= 999 | killed | 2; test_scale_refuses_fewer_than_1000_values_and_a_zero_deviation, test_n_1000_trades_and_n_999_does_not |
| AO09 | oilcad | n >= 1001 | killed | 2; test_scale_refuses_fewer_than_1000_values_and_a_zero_deviation, test_n_1000_trades_and_n_999_does_not |
| AO10 | oilcad | \|z\| >= 1.9999 | killed | 1; test_threshold_is_inclusive_at_exactly_2 |
| AO11 | oilcad | \|z\| >= 2.0001 | killed | 4; test_threshold_is_inclusive_at_exactly_2, test_z_exactly_2_trades_end_to_end |
| AO12 | oilcad | exit T_e + 13 | killed | 14; test_trading_windows_are_s0_12, test_exit_on_the_first_6c_bar_at_t_e_plus_14_resent_while_not_pending |
| AO13 | oilcad | exit T_e + 15 | killed | 12; test_trading_windows_are_s0_12, test_exit_on_the_first_6c_bar_at_t_e_plus_14_resent_while_not_pending |
| AO14 | oilcad | c6 = 0 allowed | killed | 2; test_block_return_requires_a_positive_denominator, test_a_zero_mcl_close_at_t_minus_6_leaves_r_t_undefined |
| AO15 | oilcad | r over c1 | killed | 4; test_block_return_requires_a_positive_denominator, test_z_exactly_2_trades_end_to_end |
| AO16 | oilcad | pstdev (ddof 0) | killed | 3; test_scale_is_the_sample_standard_deviation_ddof_1, test_scale_refuses_fewer_than_1000_values_and_a_zero_deviation |
| AO17 | oilcad | n < MIN -> <= | killed | 2; test_scale_refuses_fewer_than_1000_values_and_a_zero_deviation, test_n_1000_trades_and_n_999_does_not |
| AO18 | oilcad | s = 0 allowed | killed | 2; test_scale_refuses_fewer_than_1000_values_and_a_zero_deviation, test_zero_scale_is_no_trade_on_d |
| AO19 | oilcad | \|z\| > 2 strict | killed | 4; test_threshold_is_inclusive_at_exactly_2, test_z_exactly_2_trades_end_to_end |
| AO20 | oilcad | no abs (one side) | killed | 5; test_threshold_is_inclusive_at_exactly_2, test_z_exactly_2_trades_end_to_end |
| AO21 | oilcad | no MCL instrument guard | killed | 5; test_z_exactly_2_trades_end_to_end, test_n_1000_trades_and_n_999_does_not |
| AO22 | oilcad | no MCL CT-date check | killed | 1; test_an_mcl_bar_is_read_on_its_own_ct_date_only |
| AO23 | oilcad | t-6 store not reset per day | killed | 1; test_a_previous_dates_t_minus_6_bar_is_never_used |
| AO24 | oilcad | prune the oldest reference | killed | 29; test_first_and_last_decisions_trade, test_r_t_reads_the_mcl_bars_at_t_minus_1_and_t_minus_6 |
| AO25 | oilcad | no warm-up | killed | 1; test_warm_up_20th_eligible_date_no_trade_21st_trades |
| AO26 | oilcad | fewer than 20 refs accepted | killed | 1; test_too_few_reference_dates_at_the_table_start_no_trade |
| AO27 | oilcad | T_e not reset when flat | killed | 14; test_no_entry_while_a_position_or_a_pending_order_exists[1-0], test_no_entry_while_a_position_or_a_pending_order_exists[-1-0] |
| AO28 | oilcad | T_e one minute late | killed | 10; test_exit_on_the_first_6c_bar_at_t_e_plus_14_resent_while_not_pending, test_exit_of_a_short_buys_the_whole_position |
| AO29 | oilcad | entry while pending | killed | 2; test_no_entry_while_a_position_or_a_pending_order_exists[0-1], test_no_entry_while_a_position_or_a_pending_order_exists[0--1] |
| AO30 | oilcad | exit while pending | killed | 1; test_exit_on_the_first_6c_bar_at_t_e_plus_14_resent_while_not_pending |
| AO31 | oilcad | exit one bar late | killed | 10; test_exit_on_the_first_6c_bar_at_t_e_plus_14_resent_while_not_pending, test_exit_of_a_short_buys_the_whole_position |
| AO32 | oilcad | exit side reversed | killed | 12; test_exit_on_the_first_6c_bar_at_t_e_plus_14_resent_while_not_pending, test_exit_of_a_short_buys_the_whole_position |
| AO33 | oilcad | exit quantity + 1 | killed | 11; test_exit_on_the_first_6c_bar_at_t_e_plus_14_resent_while_not_pending, test_exit_of_a_short_buys_the_whole_position |
| AO34 | oilcad | no 6C CT-date check | killed | 1; test_bars_are_identified_by_ct_date_not_trade_date_alone |
| AO35 | oilcad | d need not be an OILCAD date | killed | 1; test_a_date_outside_oilcad_dates_never_trades |
| AO36 | oilcad | C6 tests t - 1 | killed | 5; test_c6_skips_09_30_on_a_standard_wpsr_date_and_not_09_35, test_c6_skips_13_00_on_an_fomc_date |
| AO37 | oilcad | no C6 | killed | 5; test_c6_skips_09_30_on_a_standard_wpsr_date_and_not_09_35, test_c6_skips_13_00_on_an_fomc_date |
| AO38 | oilcad | entry side reversed | killed | 31; test_first_and_last_decisions_trade, test_r_t_reads_the_mcl_bars_at_t_minus_1_and_t_minus_6 |
| AO39 | oilcad | q_c + 1 | killed | 26; test_first_and_last_decisions_trade, test_r_t_reads_the_mcl_bars_at_t_minus_1_and_t_minus_6 |
| AO40 | oilcad | signal leg declared first | killed | 1; test_factory_name_legs_size_and_protocol |
| AO41 | oilcad | 6C window ends 13:40 | killed | 1; test_trading_windows_are_s0_12 |
| AO42 | oilcad | only positive r filed | killed | 31; test_first_and_last_decisions_trade, test_r_t_reads_the_mcl_bars_at_t_minus_1_and_t_minus_6 |
| AW01 | wkndbtc | Tuesday | killed | 18; test_research_window_mondays_and_no_mnq_guard_at_sunday_18_00, test_buy_on_the_sunday_17_59_view_when_p_s_above_p_f |
| AW02 | wkndbtc | Friday d - 2 | killed | 18; test_research_window_mondays_and_no_mnq_guard_at_sunday_18_00, test_buy_on_the_sunday_17_59_view_when_p_s_above_p_f |
| AW03 | wkndbtc | Sunday d - 2 | killed | 17; test_trading_windows_are_s0_12, test_buy_on_the_sunday_17_59_view_when_p_s_above_p_f |
| AW04 | wkndbtc | P_F 14:58 | killed | 21; test_trading_windows_are_s0_12, test_buy_on_the_sunday_17_59_view_when_p_s_above_p_f |
| AW05 | wkndbtc | P_F 15:00 | killed | 21; test_trading_windows_are_s0_12, test_buy_on_the_sunday_17_59_view_when_p_s_above_p_f |
| AW06 | wkndbtc | P_S 17:58 | killed | 24; test_trading_windows_are_s0_12, test_buy_on_the_sunday_17_59_view_when_p_s_above_p_f |
| AW07 | wkndbtc | P_S 18:00 | killed | 24; test_trading_windows_are_s0_12, test_buy_on_the_sunday_17_59_view_when_p_s_above_p_f |
| AW08 | wkndbtc | exit bar 14:57 | killed | 7; test_trading_windows_are_s0_12, test_exit_at_monday_14_58_resent_while_not_pending |
| AW09 | wkndbtc | exit bar 14:59 | killed | 5; test_trading_windows_are_s0_12, test_exit_at_monday_14_58_resent_while_not_pending |
| AW10 | wkndbtc | weekday check removed | killed | 2; test_research_window_mondays_and_no_mnq_guard_at_sunday_18_00, test_a_non_monday_never_trades |
| AW11 | wkndbtc | d full-session check removed | killed | 2; test_excluded_mondays_do_not_trade[monday0], test_is_trade_monday_needs_both_d_and_d_minus_3 |
| AW12 | wkndbtc | Friday full-session check removed | killed | 4; test_research_window_mondays_and_no_mnq_guard_at_sunday_18_00, test_excluded_mondays_do_not_trade[monday1] |
| AW13 | wkndbtc | G = 0 buys | killed | 2; test_g_zero_is_no_trade, test_side_of_is_the_sign_of_the_tick_difference |
| AW14 | wkndbtc | sides swapped | killed | 17; test_buy_on_the_sunday_17_59_view_when_p_s_above_p_f, test_sell_when_p_s_below_p_f |
| AW15 | wkndbtc | P_F CT-date check removed | killed | 3; test_both_regimes_read_the_same_two_bars[monday1], test_a_saturday_mnq_bar_booked_to_monday_is_not_the_entry_bar |
| AW16 | wkndbtc | entry CT-date check removed | killed | 1; test_a_saturday_mnq_bar_booked_to_monday_is_not_the_entry_bar |
| AW17 | wkndbtc | P_S trade_date check removed | killed | 1; test_mbt_sunday_bar_must_carry_trade_date_d |
| AW18 | wkndbtc | P_F date check removed (stale Friday) | killed | 1; test_p_f_comes_from_ct_date_d_minus_3_only_never_a_stale_friday |
| AW19 | wkndbtc | instrument guard removed | killed | 1; test_one_instrument_id_across_p_f_and_p_s |
| AW20 | wkndbtc | C6 tests 17:59 | killed | 2; test_c6_tests_the_mnq_sunday_18_00_fill, test_c6_skips_a_guarded_sunday_18_00_fill |
| AW21 | wkndbtc | no C6 | killed | 2; test_c6_tests_the_mnq_sunday_18_00_fill, test_c6_skips_a_guarded_sunday_18_00_fill |
| AW22 | wkndbtc | exit instant on the Sunday | killed | 6; test_exit_at_monday_14_58_resent_while_not_pending, test_exit_of_a_short_buys_and_a_missing_exit_bar_goes_to_the_next_bar |
| AW23 | wkndbtc | exit while pending | killed | 3; test_exit_at_monday_14_58_resent_while_not_pending, test_exit_of_a_short_buys_and_a_missing_exit_bar_goes_to_the_next_bar |
| AW24 | wkndbtc | exit one bar late | killed | 4; test_exit_at_monday_14_58_resent_while_not_pending, test_every_exit_closes_the_whole_position |
| AW25 | wkndbtc | exit side reversed | killed | 6; test_exit_at_monday_14_58_resent_while_not_pending, test_exit_of_a_short_buys_and_a_missing_exit_bar_goes_to_the_next_bar |
| AW26 | wkndbtc | exit quantity + 1 | killed | 6; test_exit_at_monday_14_58_resent_while_not_pending, test_exit_of_a_short_buys_and_a_missing_exit_bar_goes_to_the_next_bar |
| AW27 | wkndbtc | entry while pending | killed | 2; test_no_entry_while_a_position_or_a_pending_order_exists[0-1], test_no_entry_while_a_position_or_a_pending_order_exists[0--1] |
| AW28 | wkndbtc | q_c + 1 | killed | 12; test_buy_on_the_sunday_17_59_view_when_p_s_above_p_f, test_sell_when_p_s_below_p_f |
| AW29 | wkndbtc | signal leg declared first | killed | 1; test_factory_name_legs_size_and_protocol |
| AW30 | wkndbtc | G sign flipped | killed | 16; test_buy_on_the_sunday_17_59_view_when_p_s_above_p_f, test_sell_when_p_s_below_p_f |
| AW31 | wkndbtc | MNQ Monday window ends 14:59 | killed | 1; test_trading_windows_are_s0_12 |
| AR01 | _releases | 1-minute guard | killed | 4; test_releases_source_is_the_frozen_calendar, test_in_guard_edges |
| AR02 | _releases | 3-minute guard | killed | 3; test_releases_source_is_the_frozen_calendar, test_in_guard_edges |
| AR03 | _releases | R itself not guarded | killed | 10; test_in_guard_edges, test_mgc_guards_on_the_flight_fill_grid_are_the_fomc_1300_dates |
| AR04 | _releases | R + 120 s guarded | killed | 2; test_in_guard_edges, test_c6_tests_the_fill_minute_t_k_against_r_and_r_plus_2_min[658-True] |
| AC01 | _calendar | previous_dates includes d | killed | 61; test_previous_dates_are_the_k_most_recent_strictly_before_d, test_k1_reads_the_0829_and_0834_bars |
| AC02 | _calendar | previous_dates k - 1 | killed | 107; test_previous_dates_are_the_k_most_recent_strictly_before_d, test_the_entry_size_is_the_frozen_q_c |
| AC03 | _calendar | FLIGHT_DATES a union | killed | 1; test_member_dates_are_the_sorted_intersections |
| AC04 | _calendar | OILCAD_DATES energy only | SURVIVED | 0;  |
| AC05 | _calendar | WKNDBTC_DATES equity only | SURVIVED | 0;  |
| AF53 | flight | missing entry bar checked BEFORE C6 ends the day | killed | 1; test_a_skipped_trigger_with_a_missing_entry_bar_does_not_end_the_day |
| AF54 | flight | C6 on the wrong root (6C) | killed | 4; test_values_of_d_itself_never_enter_q_of_d, test_c6_tests_the_fill_minute_t_k_against_r_and_r_plus_2_min[659-False] |
| AF55 | flight | a late MES bar (at t_k) used as the t_k - 1 bar | killed | 2; test_an_mes_bar_absent_at_tk_minus_1_and_present_at_tk_is_never_used, test_no_entry_from_a_view_after_1454 |
| AF56 | flight | t_k - 6 store not reset per MES day | killed | 2; test_k1_reads_the_0829_and_0834_bars, test_a_bar_at_0830_is_not_the_start_bar_of_k1 |
| AF57 | flight | any variant accepted | killed | 1; test_declarations_names_legs_and_factories |
| AF59 | flight | blocks shifted to 08:30..14:50 | killed | 4; test_trading_windows_are_the_s0_12_intervals, test_decision_times_are_0835_to_1455_every_5_minutes |
| AO43 | oilcad | a late MCL bar (at t) used as the t - 1 bar | killed | 1; test_mcl_bar_arriving_late_is_never_used |
| AO44 | oilcad | C6 on the wrong root (MGC) | killed | 3; test_c6_skips_09_30_on_a_standard_wpsr_date_and_not_09_35, test_c6_skips_11_00_on_holiday_week_wpsr_dates_including_the_e4_dropped_row |
| AW32 | wkndbtc | the 18:00 MNQ bar also accepted as the entry bar | killed | 16; test_buy_on_the_sunday_17_59_view_when_p_s_above_p_f, test_sell_when_p_s_below_p_f |
| AW33 | wkndbtc | the Friday 15:00 MBT bar also accepted as P_F | killed | 20; test_buy_on_the_sunday_17_59_view_when_p_s_above_p_f, test_sell_when_p_s_below_p_f |
| AW34 | wkndbtc | C6 on the wrong root (6C) | killed | 1; test_c6_tests_the_mnq_sunday_18_00_fill |
| AF41b | flight | exit clock computed from T_e + 1 min (the real T_e mutant; AF41 only moved a flag) | killed | 8; test_a_second_trigger_while_long_and_after_the_exit_does_nothing, test_h30_exit_is_sent_on_the_bar_at_te_plus_29 |

Survivors, all equivalent (no test gap):
- AF41 (flight, `_t_e_ns` moved one minute): flight.py:278-280 stores `_t_e_ns` but computes the exit
  clock from `view.ts_event_ns` directly; the stored value is only ever tested for None, so moving it
  changes nothing. The real T_e mutant AF41b (the `_exit_due_ns` argument shifted) is killed by 8 tests.
  Observation only: `_t_e_ns` could be a bool; no behaviour depends on it.
- AC04 (OILCAD_DATES = ENERGY only) and AC05 (WKNDBTC_DATES = EQUITY only): on the frozen calendars
  ENERGY_FULL_SESSIONS equals FX_FULL_SESSIONS over 2019-05-01..2026-06-19 (1783 = 1783 = 1783) and
  EQUITY_FULL_SESSIONS is a subset of CRYPTO_FULL_SESSIONS (1779 of 1782), so each intersection equals
  one operand and no test on this data can tell them apart (test_member_dates_are_the_sorted_
  intersections recomputes the intersection, which the mutant also equals). Information for the lead:
  on the current calendars wkndbtc's crypto-calendar condition removes no Monday that the equity
  calendar keeps, and oilcad's FX condition removes no date the energy calendar keeps. AC03 (FLIGHT a
  union) is killed because EQUITY and METALS differ.


### Vacuity check of the tests the prompt names

Read in full: test_a_skipped_trigger_with_a_missing_entry_bar_does_not_end_the_day (it pins the ORDER C6
before the entry-bar check: my AF53 reverses the order and is killed by it), test_c6_reads_the_traded_
roots_instants_only (kills AF54), test_values_of_d_itself_never_enter_q_of_d (a guard-skipped -60/B value
on d would move Q; d's values enter Q(d + 1)), test_an_mes_bar_absent_at_tk_minus_1_and_present_at_tk_is_
never_used, test_mcl_bar_arriving_late_is_never_used, test_a_previous_dates_t_minus_6_bar_is_never_used,
test_bars_are_identified_by_ct_date_not_trade_date_alone, test_both_regimes_read_the_same_two_bars (the
decoy bars of the kit flip the side if read), test_after_the_change_saturday_and_sunday_bars_never_stand_
in, test_c6_skips_a_guarded_sunday_18_00_fill, test_engine_refuses_on_a_signal_leg_roll_blackout_date_only
(the runner's member_window end to end), test_reference_dates_include_roll_blackout_dates. Each carries a
positive control or a mutant of mine that it kills; none passes vacuously. Coder A's own mutant run found
and fixed one vacuous test (a_bar_at_0830_is_not_the_start_bar_of_k1) before I started; it now kills my
AF06.

### Findings

No BLOCKING finding. No SHOULD FIX finding. Eight NOTEs.

- **F-1 NOTE (reading K8-L-04, both coders): "a reference date on which a leg has no bars at all
  contributes no values" is implemented for the signal leg only.** flight.py:242-248 and
  oilcad.py:201-210 build the reference values from the signal leg's filed r values; a reference date on
  which the traded leg (MGC, 6C) had no bars at all still contributes its r values. The specs' member
  tables ("every defined r_k ... each with its own two bars present") support this reading: the values
  depend on the signal leg only, and the traded leg's absence makes the date a non-window date for the
  runner, which the member cannot read (the same logic as the roll-blackout clause). Coder B raised it
  (report section 6 item 1). Lead to confirm the reading; no code change if confirmed. Effect only on a
  full-session research date with zero traded-leg bars (none expected).
- **F-2 NOTE (reading K8-L-06, oilcad): per-decision handling of a missing 6C entry bar is K4-L-14's
  reading, not the letter of C5.** C5 line 119 removes the DATE when "the entry bar" is missing; for a
  65-decision member the literal reading is non-causal, and the narrowest causal alternative ("no further
  entry on d after a missing 6C bar at any t - 1") was not taken. oilcad.py:224-226, 243-246 implement
  the lead's reading exactly (pinned: test_missing_6c_entry_bar_blocks_that_t_only). Recorded; I would
  keep K4-L-14's reading for consistency.
- **F-3 NOTE (reading K8-L-04): reference dates include roll-blackout dates although C5 lines 126-128
  say the rolling statistic uses dates "that pass these exclusions".** Fixed by K5-L-05 and K4-L-08
  (cited) and by the member's lack of a roll input; the engine removes the dates as trade dates. The
  members implement it (flight.py:139-141, oilcad.py:168, 205; pinned by
  test_reference_dates_include_roll_blackout_dates). Recorded for the return's open-choices list; no code
  change proposed.
- **F-4 NOTE (K8-L-03): immaterial alternative.** In the research window EQUITY_FULL_SESSIONS is a
  subset of CRYPTO_FULL_SESSIONS (crypto keeps 2025-07-03), so reading "equity-and-crypto" as one joint
  calendar for flight would not change a research-window date. Agree with the lead.
- **F-5 NOTE (flight.py:258-263): S0.6's "no entry while a position or a pending order exists" is
  checked after the day's entry is marked used.** At the first non-skipped trigger, `_done` is set
  (258), then the entry bar is checked (259-261), then the position/pending check (262-263) returns ()
  with the day used. Unreachable on real bars (one entry a day; a position cannot exist at a trigger
  because `on_minute` routes a non-zero position to `_exit`; a pending order without a position means an
  earlier accepted entry, which already set `_done`), and coder A reports the "day used" branch is not
  pinned. Smallest change inside the entry if the lead wants it pinned: a test with a pending order at
  the first trigger asserting no later trigger enters that day. No code change needed.
- **F-6 NOTE (tests): every engine-level K8 test runs with NO_RELEASES.** The C6 skip against the real
  frozen calendar is pinned only by direct-call tests (`in_guard` on the literal table) and by the
  tables test; the interaction with `admit_fill` (no deferral of a K8 entry in a knowable case) was shown
  here by audit_k8/engine_checks.py. Suggested addition, not required: one engine test per member with
  `load_release_calendar()` asserting a guarded decision is skipped and `fill_guard_deferral` is absent.
- **F-7 NOTE (K8-L-13, wkndbtc.py:120-127): the coverage intervals are measured on every window date,
  not only on Mondays and their Fridays.** As the specs decide (S0.12, K8-L-13), the MBT (14:59, 15:00)
  and (17:59, 18:00) day -1 intervals and the MNQ intervals are measured on each window date's own
  clock, so Monday-to-Thursday 14:59 MBT bars the member never reads enter the ratio. This is the lead's
  design for D9's check; it cannot fail for a session reason (audit_k8/coverage_intervals.log: never
  clipped) and it is stricter, not looser. Recorded.
- **F-8 NOTE (K8-L-08's logged edge): the engine can still defer a K8 entry when the traded bar at t
  is missing and the next bar opens inside a guard.** Shown with the real engine and calendar
  (audit_k8/engine_checks.log): oilcad trigger 09:25 on 2025-07-09, 6C bars 09:25..09:29 absent, fill
  at 09:32 with `fill_guard_deferral` 2. The specs accept and log it. Suggest that Task 7 reads
  `fill_guard_deferral` from each K8 record's counters so the count of such fills is in the return.

Information for the lead, not findings: (i) the earlier clusters' frozen calendar tables differ from the
current rules/sessions.py on 2024-07-03 (k4, k5) and on 14 FX US-holiday dates 2022-2023 (k3), all in
the confirmation window (table recomputation above); (ii) oilcad's "|z| = 2.0 reported if it occurs"
(K8-L-09) is a Part 2 recomputation item, since a member has no reporting channel.

## Part 2: recomputation (Task 6)
