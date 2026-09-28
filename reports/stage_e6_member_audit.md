# Stage E.6 member audit, cluster K7 (bitcoin, MBT)

## Part 1: fidelity audit (Task 3)

Auditor: MemberAuditor-K7-FableXHigh (worker-xhigh, Fable 5.1, xhigh). Brief:
reports/stage_e6_briefs/auditor_task3_K7.md. Started 22:15 PDT 2026-09-27, ended 22:43 PDT.
I wrote none of the code, specs or tests. Read-only on the repository except this report and my own
scripts and outputs under reports/stage_e6_briefs/audit_k7/ (recompute_tables.py and .out,
mutant_plugin.py, run_mutants.py, mutants.json, mutants.md, mutants_table.py, mutants_run.log).
Nothing under strategy/ or tests/ was modified: every mutant ran on a copy of strategy/members/k7
under the scratchpad, shadowing the package through a pytest plugin (`strategy.members.__path__`).
No bar file was read, no runner ran, no freeze was written (write_k7_freeze.py ran with --dry-run
only), no web, no Databento, no TopstepX.

### Files as audited

sha256 identical to reports/stage_e6_briefs/k7_files_pre_audit.sha256 (`sha256sum -c`: all 17 OK at
22:16 PDT and again at 22:43 PDT).

```
8c26b190eaf65af72ce4cc4787a14581c7a59beffd1e17b3ac31527c7e103b4a  strategy/members/k7/_calendar.py
94202bf614dcc2065604d6c883247069d4c6c215d5157615ba0afb8b93d56ce9  strategy/members/k7/cp1.py
0ecf4c64becec4e87cb1984f929cd5f610db6ed100987aa9724607ef761a995b  strategy/members/k7/cp2.py
25b013d07cc70735c735fdc1b8b61a80e910c90a5ce7981f3219971d053acfd0  strategy/members/k7/cp3.py
89996f5f6f78cf9863fe8532dd53d2ae7aa25339cd9b047546603294455b969b  strategy/members/k7/_event_common.py
9f659c2f16de6a74c81139bc3435ae0a37126b8ab5cf5068568910168c928130  strategy/members/k7/expiry.py
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  strategy/members/k7/__init__.py (0 bytes)
bff5d7a17da31ed5ed398bf8528d4711268ebcfc84223634960c8da8157a9417  strategy/members/k7/montrend.py
4fd2bc1bbfb5cba1f79bfb2edd70f0b9d8fb19bd76a97d559f5a7cbbfd0ba840  strategy/members/k7/_port_common.py
1c9bebebe9e4fdc42124ef8ff5284729e06c333d2a714da9939f0f7aa90c716e  strategy/members/k7/rev2h.py
8d5cd53569f50308b1731fa30e723e9bf8dfced7a938f99a773df7af93d0ec53  tests/test_k7_members_events_montrend.py
df7449b24d8fdeaeeda0d530e2539c98a4846907e8fe54e1f20cb21d152c1ae2  tests/test_k7_members_events.py
205eeb504953f21216fcb29a012d91feabb2670da1e79a07eece85351f973755  tests/test_k7_members_events_rev2h.py
afe934058d801199a726f22dc323d2dfc5dd4d8bb9812a98cef5513bcbafc414  tests/test_k7_members_ports_cp2.py
cfd8785492e4dfe5c86afdaeadcf1450ee937fe3c0967b3272c622faeae7e026  tests/test_k7_members_ports_cp3.py
ee78d12a957859b69043d66f5aee274a3365b5fdfe54498a800c4edb4d274423  tests/test_k7_members_ports.py
6659331fe9a89f6278a45494f428c09d848fefe4f354beb8814cc842cd8a0bb3  reports/stage_e6_briefs/gen_k7_calendar.py
```

### Method

1. Read: catalog banner, C1-C14, the six member entries and section 7 (reports/stage_e0_catalog_K7.md
   lines 1-7, 85-243, 249-694, 944-1026); D6 (docs/STAGE_E_DESIGN.md 348-411) and D9 (478-614); the
   specs (reports/stage_e6_member_specs.md, all); the six modules and six test files in full; the
   member contract (strategy/stage_e/interface.py, _template.py) and the engine's call path
   (screening/stage_e_rules.py account_view, call_member, _opening_refusal, _exit_refusal,
   forced_reasons; screening/stage_e_engine.py step, ask_member, queue_forced, visible); the K4 ports
   (diff against the K7 ports); the MES references (h_daily_bar/_mechanics.py docstring,
   h6_prior_close_location.py, h1_friction_aware_opening_range_breakout.py 135-182); the frozen table
   sources (data/calendars/crypto.py constants through data.group_session, rules.sessions.flatten_time_ct,
   both Databento condition files, data/build_bars.py 685-687 and 728, reports/stage_e2a_bars.json
   products/MBT/degraded, reports/stage_e4c_release_check.json ec_ew, reports/stage_e6_release_check.md
   and .json); both coder reports; write_k7_freeze.py (--dry-run).
2. Recomputed CRYPTO_FULL_SESSIONS, VENDOR_DEGRADED (both mappings) and MBTX (both rule wordings, T_exp
   by zoneinfo, US holidays by my own OPM-rule code) in reports/stage_e6_briefs/audit_k7/recompute_tables.py.
3. Ran the six K7 test files unmutated (206 passed: 119 port, 87 event) and 105 mutants (section 5).
4. Probed the members on synthetic bars through the real engine with the tests' own scenario helpers:
   the fall-back Sunday (2025-11-02 to Monday 11-03) and the spring-forward Sunday (2026-03-08 to
   03-09) for montrend and rev2h; the survivor's scenario (an end bar whose open differs from its close).
5. Ran screening.stage_e_freeze.check_member_source on every K7 file (all pass) and confirmed
   strategy/members/k7/__init__.py is 0 bytes.

### 1. Per-member checklists

Items: 1 literals and clock times; 2 direction; 3 exits and flattens; 4 sizing; 5 tables (detail in
section 3); 6 availability and leakage; 7 K7-L-01 (bar by CT date and clock); 8 C4 exclusions and guards;
9 engine F, D9 floor, trading_windows; 10 nothing more; 11 factory, name, legs, static check; 12 tests and
mutants. "C" = the catalog, "S" = the specs, "cp1.py:239" = strategy/members/k7/cp1.py line 239,
"ports.py:557" = tests/test_k7_members_ports.py line 557, and so on.

#### K7-cp1-01 (cp1.py, _port_common.py; ports.py)

| Item | Verdict | Evidence |
|---|---|---|
| 1 | OK | GLOBEX_OPEN_CT 17:00, SIGNAL_AFTER_O_MIN 29, ENTRY_BEFORE_C_MIN 31, EXIT_BEFORE_C_MIN 2 (cp1.py:168-171); O = 08:30, C = 15:00 from load_frozen_tables().day_session_ct (_port_common.py:66-68), so 08:59, 14:29, 14:58 (cp1.py:202-204). First bar: CT date d-1 and clock 17:00 (cp1.py:239). Matches C 273-279, 293-294, D6 364. |
| 2 | OK | s = close(08:59) - open(first bar) in ticks (cp1.py:222; open read via asdict, :178); buy if s > 0, sell if s < 0, zero: no trade (cp1.py:223-225). |
| 3 | OK | Exit on the first present bar of CT date d at or after 14:58 while the position is non-zero and nothing is pending (_port_common.py:95-107); a refused exit is resent (ports.py:514); after an engine-forced exit nothing more (ports.py:523, 529). |
| 4 | OK | q_c from tables.vehicles["MBT"].q_c (_port_common.py:68; cp1.py:253); exits close abs(position) (_port_common.py:107). |
| 5 | n/a | Reads no table. |
| 6 | OK | Reads open, close, instrument_id of bars at their close (first bar at 17:01, signal at 09:00, decision at the 14:29 close); no hindsight field; account read for position and pending only. |
| 7 | OK | A bar is selected by CT date and clock (cp1.py:239, 242-244); nothing outside [d-1 17:00, d 16:00) is read: bars on another CT date return () (:242-243), weekday 16:00-16:59 bars of d-1 fail `at == 17:00` (:239). Tests: booked-forward 2026-01-19 (ports.py:613-632), 24/7 weekend 2026-06-06/07 (ports.py:567-597), Sunday 17:00 open (ports.py:557). |
| 8 | OK | Only D6's two-signal-bar guard (cp1.py:220-221); no C4 set, no early-halt test (the engine refuses: ports.py:537). |
| 9 | OK | trading_windows {(17:00, 17:01, -1, -1), (08:59, 09:00), (14:29, 15:00)} = S0.12 (cp1.py:206-210). The only entry is at 14:29; the 2-minute rule cannot bind except through a data gap, where the refused exit is resent (ports.py:514). |
| 10 | OK | State: _day, _first, _signal, _entered. No filter, size rule or re-entry. Diff against strategy/members/k4/cp1.py: docstring, root, factory names, comments, and the K7-L-01 comment only (the rule body is identical). |
| 11 | OK | make_mbt (cp1.py:256); name "K7-cp1-01 MBT" = label; legs (LegSpec("MBT", True),); check_member_source: no findings. |
| 12 | OK | 12 cp1 mutants and 5 _port_common mutants all killed by rule tests (section 5). Prompt cases pinned: entry and exit times (ports.py:449, 502, 508), Sunday session open (:557), trade-date boundary (:551, 567, 613), missing bar (:474-502), refused exit (:514), engine flatten (:523). |

#### K7-cp2-01 (cp2.py; ports_cp2.py)

| Item | Verdict | Evidence |
|---|---|---|
| 1 | OK | RANGE_MINUTES 15, BUFFER_TICKS 4, HOLD_BARS 75 (cp2.py:54-56); range bars [08:30, 08:45) (:111), eligible bars [08:45, 15:00) (:117); 4 x vendor_tick = 20.00 pinned (ports_cp2.py:63-66, 115-123). Matches C 336-347, 352; D6 365, 368-372. |
| 2 | OK | close >= OR_high + 4 ticks buys, <= OR_low - 4 ticks sells, in integer ticks (cp2.py:119-123). |
| 3 | OK | Present bars counted while the position is open, from the bar after the entry bar; exit on the 75th, resent while refused (cp2.py:87-96) = B-H1's count (h1 lines 143-151). No C-2 exit (ports_cp2.py:142). A missing bar extends the hold by one (:137); a D9.5a-deferred fill starts the count at the fill (:239). F binds (:152, 160, 169). |
| 4 | OK | cp2.py:127 (q), :96 (abs(position)). |
| 5 | n/a | |
| 6 | OK | high/low of range bars, close of eligible bars, all at their close; account position and pending only. |
| 7 | OK | Bars of another CT date return () before the range or trigger (cp2.py:108-109); tests: weekend (ports_cp2.py:284), booked-forward holiday session (:295). |
| 8 | OK | No C4 set, no instrument guard, no early-halt test (D6; ports_cp2.py:233, 260). |
| 9 | OK | trading_windows (08:30, 15:08) = S0.12 (cp2.py:82; F is a literal, see F-6). Entries stop at C; the engine's flatten at F closes late fills (ports_cp2.py:152, 160). |
| 10 | OK | State: _day, _hi, _lo, _triggered, _held. Diff against k4/cp2.py: names and comments only. |
| 11 | OK | make_mbt (cp2.py:130); label; one leg; static check clean. |
| 12 | OK | 17 cp2 mutants all killed. Pinned: fill and 75-bar exit (:68), buffer ties (:104, 115), no entry from 15:00 (:147), first qualifying bar uses the entry (:175, 181), range from present bars (:192-227), FOMC 13:00 fill moved by the engine (:246). |

#### K7-cp3-01 (cp3.py; ports_cp3.py)

| Item | Verdict | Evidence |
|---|---|---|
| 1 | OK | CLV cuts Decimal 0.8 / 0.2, CLOSE_BEFORE_C_MIN 1, EXIT_BEFORE_C_MIN 2 (cp3.py:194-197); O = 08:30 entry bar (:317), C_d = the 14:59 close (:287-288), daily H/L over [08:30, 15:00) (:280-284), exit from 14:58 (:316). Matches C 390-404; D6 366. |
| 2 | OK | clv_side: Range > 0, CLV >= 0.8 buys, <= 0.2 sells, compared as integer cross-products (cp3.py:211-224); 14 exact cases pinned (ports_cp3.py:100). |
| 3 | OK | exit_if_due on the first present bar of CT date d at or after 14:58 (cp3.py:315-316); missing 14:58 (ports_cp3.py:202); engine F and D9.7 backstops (:212, 218). |
| 4 | OK | cp3.py:323; abs(position) in exit_if_due. |
| 5 | n/a | |
| 6 | OK | Day d's condition uses only the complete daily bar of an earlier trade date, finalised when the first bar of a later trade date arrives (cp3.py:269-275, 307-308): day d's own bar never enters day d's condition (ports_cp3.py:140). early_halt_ct is a calendar field (strategy/interface.py BAR_FIELD_AVAILABILITY). |
| 7 | OK | Bars on another CT date return () before accumulation (cp3.py:311-312): a booked-forward holiday's session and weekend bars never form a daily bar; d-1 after a booked-forward Monday is the Friday (ports_cp3.py:244, 257); weekend (:231). |
| 8 | OK | Family H by reference (_mechanics.py docstring lines 7-15, 34): complete day = 08:30 and 14:59 bars present, no early_halt_ct on CT date d, one instrument_id (cp3.py:259-263); day d not traded if its 08:30 bar carries early_halt_ct (:292-293); instrument guard d-1 vs the 08:30 bar (:297-298). No vendor-degraded test (a port). |
| 9 | OK | trading_windows (08:30, 15:00) = S0.12 (cp3.py:256). Entry at 08:30 only; hold about 388 minutes. |
| 10 | OK | State: _prior and the day accumulators. Diff against k4/cp3.py: names, comments, and the removal of an unused LOOKBACK constant. |
| 11 | OK | make_mbt (cp3.py:326); label; one leg; static check clean. |
| 12 | OK | 22 cp3 mutants all killed. Pinned: 08:31 entry and 14:59 exit (ports_cp3.py:73), non-strict cuts (:91, 100), range 0 (:129), warm-up (:134), most recent complete day (:147), two ids (:156), halt day not traded and incomplete (:185, 195), booked-forward and weekend (:244-266). |

#### K7-expiry-01 (expiry.py, _event_common.py, _calendar.py; events.py)

| Item | Verdict | Evidence |
|---|---|---|
| 1 | OK | ENTRY_FILL_BEFORE_T_MIN 300, EXIT_FILL_BEFORE_T_MIN 1, FILL_DELAY_MIN 1: entry bar T_exp - 301, exit bar T_exp - 2 (expiry.py:53-54, 69-70); T_exp per date from MBTX (10:00 or 11:00; 11:00 on 2025-10-31 and 2026-03-27). Probes: 2025-06-27 04:59 / 09:58 CDT, 2025-10-31 and 2026-03-27 05:59 / 10:58 CDT. Matches C 457-464, 478-488. |
| 2 | OK | BUY only (expiry.py:106); "sell" mutant killed. |
| 3 | OK | Exit on the first present bar at or after the exit bar while the position is non-zero and nothing is pending, resent while refused (expiry.py:98-101; _event_common.py close_items :126-132); tests events.py:530, 539, 588; engine-forced exit: no duplicate, no re-entry (:567). |
| 4 | OK | q from the frozen vehicle table (_event_common.py:69-72; expiry.py:106); abs(position). |
| 5 | OK | MBTX and the event set recomputed (section 3): 60 rows, 54 events, 12 in the research window. |
| 6 | OK | Reads only ts_event_ns and trade_date of the bar plus the table; no price is read at all; the position from the account. MBTX is known in advance (contract terms, holiday calendars). |
| 7 | OK | The entry bar is the exact UTC instant of (CT date d, T_exp - 301) AND trade_date d (expiry.py:102-103, ct_open_ns); events.py:578. |
| 8 | OK | Event set = MBTX dates in CRYPTO_FULL_SESSIONS less VENDOR_DEGRADED (expiry.py:64-67, is_entry_date); events.py:553 (five off-set dates including 2025-12-26 and 2025-12-24), :558. The rule reads no signal, so S0.9 is met by the entry bar alone. |
| 9 | OK | trading_windows (05:00, 11:00) = S0.12 (expiry.py:56-57, 90; literals, F-6). Flat by 09:59 or 10:59; hold 299 minutes. |
| 10 | OK | State: _exit_ns. No filter. |
| 11 | OK | make_mbt (expiry.py:109); label "K7-expiry-01 MBT"; one leg; static check clean. |
| 12 | OK | 8 expiry mutants all killed; the two T_exp slots, the missing entry bar, the missing exit bar, the expiry instant and the off-set dates are pinned (events.py:509-598). |

#### K7-rev2h-01 (rev2h.py, _event_common.py; events_rev2h.py)

| Item | Verdict | Evidence |
|---|---|---|
| 1 | OK | Anchor O = 08:30 from the frozen tables (rev2h.py:207), BLOCK_MINUTES 120, DECISION_BLOCKS (1, 2), SIGNAL_END 1, FINAL_EXIT 1 (rev2h.py:169-173): decisions at 10:30 and 12:30 with signal bars 08:30..10:29 and 10:30..12:29, entry bars 10:30 and 12:30, final exit bar 14:29 (day_schedule :178-187; probed on 2025-11-03 CST). Matches C 548-559. |
| 2 | OK | DIRECTION -1: target = -sign(close(t-1) - open(start)) in ticks (rev2h.py:175; _event_common.py:203); r = 0 gives 0 (events_rev2h.py:78). |
| 3 | OK | Flatten on the t-1 bar when the position's sign differs from the target (s = 0 included), fills at the decision-time open; hold on an equal target; entry on the exact t bar only when flat (never one 2q order, C2); a missing t-1 bar gives target 0 and a flatten on the first later present bar (K7-L-08); final exit on 14:29 or the first later bar (_event_common.py:184-224; events_rev2h.py:55, 71, 97, 104, 110, 173). Refused or pending flattens are resent (:158). |
| 4 | OK | q from the frozen table (rev2h.py:218-219); close_items abs(position). |
| 5 | OK | ENTRY_DATES = CRYPTO_FULL_SESSIONS less VENDOR_DEGRADED, recomputed (section 3): 300 research trade dates. |
| 6 | OK | Signal = open of the start bar (recorded when that bar closes) and close of the t-1 bar; orders decided at the t-1 close (C "The latest input is the bar closing at the decision time"). No hindsight field; account position and pending only. The book only inspects ts_event_ns of other bars. |
| 7 | OK | Bars matched by the UTC instant of (CT date d, clock) and trade_date (day_schedule uses ct_open_ns(day, ...)); the prior evening's and a booked-forward holiday's bars are never matched (events_rev2h.py:202, 212). |
| 8 | OK | is_entry_date gate (rev2h.py:220); tests: vendor-degraded 2025-09-17, halt 2025-07-04, early-F 2024-07-03 (events_rev2h.py:192-199). Instrument guard: the two endpoints must share an id (target 0 otherwise) and the entry bar must carry it (_event_common.py:200-201, 221-222); F-2 on the wording. |
| 9 | OK | trading_windows (08:30, 14:31) = S0.12 (rev2h.py:208-209). At most 2 entries; holds >= 119 minutes; flat 38 minutes before F; an engine closure leaves the account flat and the 12:30 decision applies as written (K7-L-07; events_rev2h.py:179). |
| 10 | OK | State: the day's DecisionBook (_starts, _next, _target, _entry). The flatten test runs on every bar, but the target changes only at a decision or a missed decision, so it is the same rule. |
| 11 | OK | make_mbt (rev2h.py:226); label; one leg; static check clean. |
| 12 | SHOULD FIX (tests only) | 8 rev2h mutants killed; of the 16 shared DecisionBook mutants 15 killed, 1 survived: `ec-end-close` (the signal read from the t-1 bar's OPEN instead of its CLOSE) passes all 87 event tests, because every event-test scenario gives the end bars open = close (events.py:124-140 `_rows`; the rev2h and montrend scenarios set `opens` only on the START bars). The code is right (probe: rev2h sells on r1 = +10 when the 10:29 bar opens at -30 and closes at +10). Finding F-1. |

#### K7-montrend-01 (montrend.py, _event_common.py; events_montrend.py)

| Item | Verdict | Evidence |
|---|---|---|
| 1 | OK | FIRST_DECISION Sunday 18:00 (CT date d-1), LAST_DECISION Monday 13:00, STEP 60, LOOKBACK 60, SIGNAL_END 1, FLAT_AT 14:00, FINAL_EXIT 1 (montrend.py:289-298): 20 decisions, each with start bar t - 60, end bar t - 1, entry bar t; final exit bar 13:59 (events_montrend.py:137). Probed on 2025-11-03 (CST) and 2026-03-09 (CDT): every span exactly 60 wall-clock minutes. Matches C 634-648, 654-667. |
| 2 | OK | DIRECTION +1: target = s_t (montrend.py:298). |
| 3 | OK | As rev2h (shared book): flatten on t - 1 when the sign differs (s_t = 0 included), entry on t when flat, hold on an equal sign, missing t - 1 bar: flatten on the first later present bar without entry (events_montrend.py:110), missing t bar: no entry but the flatten stands (:117), final exit 13:59 or the first later bar (:75, 84). |
| 4 | OK | montrend.py:355 (q from the frozen table). |
| 5 | OK | ENTRY_DATES as rev2h; Mondays only (is_trade_day, montrend.py:320-321): 57 research Mondays trade (section 3). |
| 6 | OK | Inputs at the close of the bar at t - 1; the Sunday 17:00 bar's open is the first input (17:01). No weekend bar is read (its ts matches no start or end instant; events_montrend.py:150 plants loud weekend signals). |
| 7 | OK | Bars by CT date and clock through ct_open_ns with negative minutes for the Sunday (montrend.py:301-317); a booked-forward Monday's bars carry Tuesday's trade date and is_trade_day is False (:160; see F-8a). |
| 8 | OK | Mondays in ENTRY_DATES only (montrend.py:320-321; events_montrend.py:169-176: degraded 2026-03-16, halt 2021-09-06, a Tuesday). Instrument guard on the two signal bars and the entry bar (:189, 195, 204). |
| 9 | OK | trading_windows (17:00 day -1, 14:00 day 0) = S0.12 (montrend.py:342-344). At most 20 entries, one per decision (:124); holds >= 59 minutes; no fill in the first hour after Sunday 17:00; an engine closure leaves later decisions as written (:179). |
| 10 | OK | State: the day's DecisionBook. |
| 11 | OK | make_mbt (montrend.py:364); label; one leg; static check clean. |
| 12 | SHOULD FIX (tests only) | 13 montrend mutants killed; the shared survivor `ec-end-close` applies here too (FIRST_UP sets the 17:59 bar open = close). Finding F-1. |

### 2. Common checks (items 11 and 9)

- write_k7_freeze.py --dry-run prints 6 declarations, ordinals 1-6 in catalog order, labels
  "<id> MBT", factory make_mbt, one leg MBT: matches S0.2 and K7-L-10.
- check_member_source(rel, source, "K7") returns no findings for all 10 files; __init__.py is 0 bytes.
- Every member's `name` equals its label and `legs` == (LegSpec("MBT", True),) (ports.py:335, events.py:424).
- trading_windows equal S0.12 for all six (ports.py:351, events.py:434 and my reading of each module).
- Nothing in a member works against the engine: entries are market intents on the named bars only;
  exits are sent while the position is non-zero and nothing is pending, so an engine-forced exit
  (pending until it fills) is never duplicated; after an engine closure the one-decision members make no
  further entry that date and the multi-decision members apply the next decision to a flat account
  (K7-L-07). MBT is DCB-only in rules/price_limits.py (not in HARD_LIMIT_PRODUCTS), so the D9.7 exit
  never fires on it in the real engine; the tests force one through a test-only rules subclass.
- Ruling on K7-L-03 leakage (item 6): VENDOR_DEGRADED is the vendor's after-the-fact list (condition
  files last modified 2026-08). It enters the three new members only as a set difference on trade dates
  (ENTRY_DATES, _event_common.py:50-51), tested by `is_entry_date(bar.trade_date)`: it can remove a trade
  date and nothing else. It cannot set a direction, a time, a size or a price, and no member reads the
  bar's `vendor_degraded_day` (masked by the engine anyway). No member reads a future bar, a hindsight
  field, or any account field other than position and pending. It is a data-quality exclusion fixed
  before any run, as C4 requires. Consequence to keep in view: the new members' research trade-date set
  is 300 dates against the ports' 304 (F-3).

### 3. Table recomputation (item 5), my own code, from the frozen sources

Script and full output: reports/stage_e6_briefs/audit_k7/recompute_tables.py, recompute_tables.out.

CRYPTO_FULL_SESSIONS (K7-L-02, K3-L-11): EC-CAL crypto trade dates 2019-05-01..2026-06-19 with
`early_halt_ct(d) is None` and `flatten_time_ct("MBT", d) == 15:08`.
- Recomputed 1782 dates; module 1782; equal; no difference either way.
- Removed by the halt test alone: 0. Removed by the F test alone: 1 (2024-07-03, F 11:30; module
  CRYPTO_EARLY_F_DATES agrees). Removed by both: 32 (every early-halt date in the coverage).
- 31 booked-forward dates, none in the table (they are not trade dates).
- Research window: 304 full sessions of 308 trade dates (the 4 halts 2025-07-04, 11-28, 12-24,
  2026-04-03); the two tests agree on every research date.

VENDOR_DEGRADED (K7-L-03): 18 degraded UTC dates in the two condition files, 17 in the coverage.
- ISO mapping (trade date == degraded UTC date): 11 dates; module 11; equal. Research rows
  2025-09-17, 09-24, 11-28, 2026-03-16, 04-10 = reports/stage_e2a_bars.json on_research_trade_dates.
- Degraded UTC dates that are not trade dates (not listed, as the module's comment says): 2021-12-05,
  2022-01-02, 2026-01-31, 2026-03-15, 2026-03-21, 2026-05-24.
- Alternative per-bar mapping (any bar assigned to the trade date lies on a degraded UTC date, the flag
  of build_bars.py:728, computed with data.group_session.assign_trade_dates): 20 trade dates, the 11
  above plus 2020-05-06, 2020-07-02, 2021-12-06, 2022-01-03, 2024-09-19, 2025-09-18, 2025-09-25,
  2026-03-17, 2026-05-26 (the flagged bars are the next trade date's 17:00-18:59 CT bars, or a Sunday's
  evening bars). See F-3.
- ENTRY_DATES = 1772 = full less degraded; research: 300 entry dates; rev2h loses 2025-09-17, 09-24,
  2026-03-16, 04-10; montrend: 63 research Mondays, 5 not trade dates (2025-05-26, 09-01, 2026-01-19,
  02-16, 05-25), 58 trade-date Mondays, 57 traded (2026-03-16 removed); expiry loses none beyond the
  halt on 2025-11-28. All as the specs (K7-L-03, R-1b-2) state.

MBTX (K7-L-04, R-1b-1): last Friday of each month 2021-05..2026-06, else the preceding day that is a
business day in both the UK (ec_ew list, 63 dates) and the US (my own list: 5 U.S.C. 6103 holidays on
OPM-observed dates, Juneteenth from 2021, plus Good Friday; 72 dates 2021-2026 = Task 1b's 66 plus 6
Good Fridays), T_exp = 16:00 Europe/London in America/Chicago by zoneinfo.
- "both" wording: 62 rows; rows off the last Friday: 2021-12-30, 2024-03-28, 2025-12-24.
- "either" wording (CME's current text): 62 rows; differs from "both" exactly at 2021-12 (12-31) and
  2025-12 (12-26), as R-1b-1 says.
- Module MBTX = the "both" rows less 2021-12-30 and 2025-12-24: 60 rows; equal; neither 2021-12-31 nor
  2025-12-26 added. 11:00 rows: 2022-03-25, 2024-03-28, 2025-03-28, 2025-10-31, 2026-03-27; every T_exp
  re-derived from zoneinfo matches.
- Research rows by the rule: the catalog's 14 (C9). Task 1b verdicts: keep 3 (2025-06-27, 09-26,
  2026-03-27), drop 1 (2025-12-24), unverifiable 10 = MBTX_UNVERIFIED (10 rows, equal).
- Event set: 54 dates; research 12 (2025-11-28 out: halt and degraded; 2025-12-24 dropped); every
  research event is a roll-blackout date (E.2a L-11; Task 1b item E), so 0 trades are expected (K7-L-05).

### 4. Readings (items 13 and 14), one line each

Adopted readings (S section 8). Agree unless stated.
- E.3-L-01 literal tables: agree; the static check forbids file reads, and events.py:264-386 pin every table to its sources (sha256 and recomputation).
- E.3-L-03 the bar at hh:mm is on CT date d: agree (C1 line 103-104).
- E.3-L-04 named entry bars exact: agree (C2 "market intent on the bar at X").
- E.3-L-05 CP1's first bar is the 17:00 bar of CT date d-1: agree, fixed by C3 ("The first bar of trade date d is the 17:00 CT bar of the previous calendar day").
- E.3-L-06 CP1's guard is D6's: agree (D6 364 verbatim).
- E.3-L-07 CP2 counts present bars, no C-2 exit: agree, fixed by reference (h1 lines 143-151; D6 365 names no C-2 exit).
- E.3-L-08 CP2's range from present bars, first qualifying bar uses the entry: agree, fixed by reference (h1 lines 152-181: `_triggered` set when the intent is emitted).
- E.3-L-09, L-10, L-11 CP3 by Family H: agree, fixed by reference (_mechanics.py docstring lines 7-15 and 34; the "before the no-new-positions time" clause is redundant under the engine's F).
- E.3-L-12, L-13 the guard covers the entry bar: see F-2. K7's C4 (line 135-137) names "signal bars of one computation", not the entry bar (K2's C4 does); the entry-bar gate is an extra narrowing that cannot bind on real MBT bars. I would keep it but own it as a K7 reading, not as "the same text".
- E.3-L-17 fixed trading_windows measured on every date: fixed by the interface (no per-date condition); see F-9.
- E.3-L-19 integer vendor ticks: agree (C7).
- E.3-L-20 undersized vehicles screened: agree (E.2a).
- E.3-L-22 a refused exit is resent: agree (C4 "sent on the first later bar"; otherwise the position would ride to F).
- K4-L-01 tables span the whole period, research rows checked: agree (Task 1b's scope).
- K4-L-06 CP2's buffer 4 x vendor_tick: agree (D6 368-372; MBT is the exposure's only contract, so the most-active-contract tick is the vehicle's).
- K4-L-13 full-session table over EC-CAL's coverage: agree (outside coverage the calendar says nothing).
- K3-L-11 an early engine F is an early close for C4: agree; the narrower event set; recomputed (the F test alone removes only 2024-07-03, outside the research window).

New K7 readings.
- K7-L-01: agree; the narrowest (fewest bars read) and fixed by C3's clock definition; CME's assignment is named and rejected by C3 and section 7 item 2. Tests cover a booked-forward Monday and a 24/7 weekend for every port, rev2h and montrend.
- K7-L-02: agree; recomputed equal.
- K7-L-03: agree with the ISO mapping (fewest exclusions; fixed by reference to E.2a's on_research_trade_dates; the per-bar alternative would exclude 9 more dates on which no K7 member reads a flagged bar in the research window). Not a leak (section 2). See F-3 for the confirmation-window consequence.
- K7-L-04: agree; recomputed equal, T_exp verified.
- K7-L-05: agree that running the member as frozen is within the text and the narrowest (nothing changed); see F-5 for the wording.
- K7-L-06: agree on substance; see F-2 for the spec row wording and the basis.
- K7-L-07: agree; on MBT it is moot for D9.7 (DCB-only) and F (no opens after F), and an MLL liquidation ends the account; the tests show the member's side of it with a forced test-only exit.
- K7-L-08: agree; fixed by C2 (the flatten "is emitted on the bar that closes at the decision time") and the entry's "The latest input is the bar closing at the decision time".
- K7-L-09: agree that the code matches; see F-9.
- K7-L-10, K7-L-11: agree (dry run; six test files).
- K7-L-12: agree, with F-4 (items 13 b, c, d, h unstated).

Section 9 rulings.
- R-1b-1 drop, do not add: agree, the narrowest (C9 has E.2 confirm the rule's dates against CME's calendar, not supply new ones; the dropped date is not a final trading day). Both dropped dates are moot in the research window (2025-12-24 is an early halt and a roll-blackout date; 2025-12-26 is a roll-blackout date). The CME evidence is BTC's calendar (product 8478; no MBT capture) plus E.2a's bar check for 2025-12-26; the two chapters carry the same termination text, so I accept it. The 2021-12-31 consequence for confirmation is rightly flagged to the user.
- R-1b-2: agree; recomputed (63, 5, 58, 57).
- R-1b-3: agree; nothing for a member to do.
- R-1b-4: agree; 12 research events, all roll-blackout dates.

Item 14, catalog section 7 as settled by K7-L-12.
- 1 (24/7 confirmed): follows the text (C3 keeps the program convention; no design change).
- 2 (trade-date convention): K7-L-01; follows C3.
- 3 (regime mismatch): a label for confirmation; consistent with the header row.
- 4 (short history): the start rule's, later; consistent.
- 5 (coverage): the runner's D9 check on S0.12; no fallback written, as C12 says; consistent.
- 6 (low frequency): kept, the power check decides; consistent with the K4 Q4 ruling the text cites.
- 7 (ML): excluded by U6; consistent.
- 8 (expiry and the blackout): K7-L-05; see F-5.
- 9 (cost sample): a stated limitation; D8 frozen; consistent.
- 10-12: no action; consistent.
- 13 (E.2 checks): (a), (f) Task 1b and (e), (g) as stated; (b), (c), (d), (h) unstated, see F-4.

### 5. Mutants (item 12)

Harness: reports/stage_e6_briefs/audit_k7/run_mutants.py applies one text change to a copy of
strategy/members/k7 under the scratchpad and runs the three port test files (port mutants), the three
event test files (event mutants) or all six (table mutants) through mutant_plugin.py, which prepends the
copy to `strategy.members.__path__`; the repository tree is never modified. Baseline unmutated: 206 passed
(119 port, 87 event). Killing tests are rule tests (the source-hash and static-check tests read the
repository files, which were unchanged). Full data: mutants.json; table: mutants.md.

Totals: 105 mutants, 104 killed, 1 survived (`ec-end-close`), 0 pattern misses after one anchor fix.

| # | Mutant | File | What it tests | Result | Killing tests (count; first two) |
|---|---|---|---|---|---|
| 1 | cp1-direction | cp1.py | direction with the signal | KILLED | 16; test_cp1_a_refused_exit_is_resent_on_the_next_bar, test_cp1_after_a_booked_forward_monday_the_first_bar_is_monday_1700 |
| 2 | cp1-entry-31 | cp1.py | entry bar C-31 (14:29) | KILLED | 20; test_cp1_a_refused_exit_is_resent_on_the_next_bar, test_cp1_after_a_booked_forward_monday_the_first_bar_is_monday_1700 |
| 3 | cp1-exit-2 | cp1.py | exit bar C-2 (14:58) | KILLED | 13; test_cp1_after_a_booked_forward_monday_the_first_bar_is_monday_1700, test_cp1_after_a_booked_forward_monday_the_monday_1700_open_decides |
| 4 | cp1-first-1700 | cp1.py | first bar 17:00 on CT date d-1 | KILLED | 6; test_cp1_after_a_booked_forward_monday_the_monday_1700_open_decides, test_cp1_emits_at_most_one_entry_per_trade_date_and_none_while_pending |
| 5 | cp1-first-day | cp1.py | first bar by clock alone (K7-L-01) | KILLED | 2; test_cp1_after_a_booked_forward_monday_the_monday_1700_open_decides, test_cp1_monday_from_2026_06_01_the_sunday_1700_open_decides |
| 6 | cp1-first-open | cp1.py | signal uses the first bar's OPEN | KILLED | 16; test_cp1_a_refused_exit_is_resent_on_the_next_bar, test_cp1_after_a_booked_forward_monday_the_first_bar_is_monday_1700 |
| 7 | cp1-idguard | cp1.py | two instrument_ids: no trade | KILLED | 1; test_cp1_signal_bars_with_two_instrument_ids_are_no_trade_l06 |
| 8 | cp1-once | cp1.py | one entry decision per date | KILLED | 1; test_cp1_emits_at_most_one_entry_per_trade_date_and_none_while_pending |
| 9 | cp1-otherdate | cp1.py | bars of another CT date never read | KILLED | 4; test_cp1_after_a_booked_forward_monday_the_first_bar_is_monday_1700, test_cp1_after_a_booked_forward_monday_the_monday_1700_open_decides |
| 10 | cp1-signal-29 | cp1.py | signal bar O+29 (08:59) | KILLED | 17; test_cp1_a_refused_exit_is_resent_on_the_next_bar, test_cp1_after_a_booked_forward_monday_the_first_bar_is_monday_1700 |
| 11 | cp1-signal-close | cp1.py | signal uses the 08:59 CLOSE | KILLED | 2; test_cp1_sells_on_a_negative_signal, test_cp1_the_signal_is_one_tick_either_side_of_zero |
| 12 | cp1-zero | cp1.py | zero signal: no trade | KILLED | 1; test_cp1_zero_signal_is_no_trade |
| 13 | pc-exit-date | _port_common.py | exit only on CT date d | KILLED | 1; test_an_exit_is_not_sent_while_an_order_is_pending |
| 14 | pc-exit-lt | _port_common.py | exit at or AFTER the named bar | KILLED | 36; test_an_exit_is_not_sent_while_an_order_is_pending, test_cp1_a_refused_exit_is_resent_on_the_next_bar |
| 15 | pc-exit-pending | _port_common.py | no exit while an order is pending | KILLED | 1; test_an_exit_is_not_sent_while_an_order_is_pending |
| 16 | pc-flat-pending | _port_common.py | flat means no pending order | KILLED | 3; test_cp1_emits_at_most_one_entry_per_trade_date_and_none_while_pending, test_cp2_no_entry_while_an_order_is_pending |
| 17 | pc-ticks-trunc | _port_common.py | integer ticks by round() | KILLED | 1; test_prices_become_integer_vendor_ticks |
| 18 | cp2-buffer-3 | cp2.py | buffer 4 ticks (20.00) | KILLED | 5; test_cp2_literals_are_or_15_buffer_4_ticks_hold_75_k4_l06, test_cp2_the_0830_bar_is_a_range_bar |
| 19 | cp2-buffer-5 | cp2.py | buffer 4 ticks (20.00) | KILLED | 29; test_cp2_a_deferred_entry_fill_starts_the_count_at_the_fill, test_cp2_a_deferred_exit_is_not_sent_twice |
| 20 | cp2-c2exit | cp2.py | no C-2 exit (E.3-L-07) | KILLED | 2; test_cp2_f_binds_from_a_1353_fill, test_cp2_the_last_eligible_bar_1459_is_held_to_f |
| 21 | cp2-direction | cp2.py | break direction | KILLED | 25; test_cp2_a_deferred_entry_fill_starts_the_count_at_the_fill, test_cp2_a_deferred_exit_is_not_sent_twice |
| 22 | cp2-elig-c | cp2.py | no entry from C on | KILLED | 1; test_cp2_no_entry_from_1500 |
| 23 | cp2-elig-start | cp2.py | the 08:45 bar is eligible | KILLED | 19; test_cp2_a_deferred_entry_fill_starts_the_count_at_the_fill, test_cp2_a_deferred_exit_is_not_sent_twice |
| 24 | cp2-ge | cp2.py | close >= OR_high + buffer | KILLED | 26; test_cp2_a_deferred_entry_fill_starts_the_count_at_the_fill, test_cp2_a_deferred_exit_is_not_sent_twice |
| 25 | cp2-hold-74 | cp2.py | 75-bar count | KILLED | 24; test_cp2_a_deferred_entry_fill_starts_the_count_at_the_fill, test_cp2_a_deferred_exit_is_not_sent_twice |
| 26 | cp2-hold-76 | cp2.py | 75-bar count | KILLED | 24; test_cp2_a_deferred_entry_fill_starts_the_count_at_the_fill, test_cp2_a_deferred_exit_is_not_sent_twice |
| 27 | cp2-hold-count-start | cp2.py | count starts after the fill (present bars with a position) | KILLED | 2; test_cp2_a_deferred_entry_fill_starts_the_count_at_the_fill, test_cp2_an_fomc_1300_fill_is_moved_by_the_engine |
| 28 | cp2-le | cp2.py | close <= OR_low - buffer | KILLED | 5; test_cp2_breakout_down_sells, test_cp2_state_resets_each_trade_date |
| 29 | cp2-once | cp2.py | one entry per trade date | KILLED | 3; test_cp2_d97_engine_exit_no_duplicate_exit_and_no_reentry, test_cp2_one_entry_per_trade_date_after_the_exit |
| 30 | cp2-otherdate | cp2.py | bars of another CT date never read | KILLED | 2; test_cp2_after_a_booked_forward_monday_reads_only_the_tuesday, test_cp2_monday_from_2026_06_01_reads_no_weekend_bar |
| 31 | cp2-range-15 | cp2.py | range [O, O+15) | KILLED | 23; test_cp2_a_deferred_entry_fill_starts_the_count_at_the_fill, test_cp2_a_deferred_exit_is_not_sent_twice |
| 32 | cp2-range-end | cp2.py | the 08:45 bar is not a range bar | KILLED | 22; test_cp2_a_deferred_entry_fill_starts_the_count_at_the_fill, test_cp2_a_deferred_exit_is_not_sent_twice |
| 33 | cp2-range-start | cp2.py | the 08:30 bar is a range bar | KILLED | 1; test_cp2_the_0830_bar_is_a_range_bar |
| 34 | cp2-window-f | cp2.py | trading window to F 15:08 | KILLED | 1; test_trading_windows_are_the_s0_12_intervals |
| 35 | cp3-buy-079 | cp3.py | CLV >= 0.8 buys | KILLED | 1; test_cp3_literals_are_the_clv_cuts_and_the_clock |
| 36 | cp3-buy-081 | cp3.py | CLV >= 0.8 buys | KILLED | 23; test_cp3_a_booked_forward_holiday_session_is_never_a_daily_bar, test_cp3_after_a_booked_forward_monday_d_minus_1_is_the_friday |
| 37 | cp3-close-1 | cp3.py | C_d = close of 14:59 | KILLED | 27; test_cp3_a_booked_forward_holiday_session_is_never_a_daily_bar, test_cp3_after_a_booked_forward_monday_d_minus_1_is_the_friday |
| 38 | cp3-direction | cp3.py | direction by CLV | KILLED | 25; test_cp3_a_booked_forward_holiday_session_is_never_a_daily_bar, test_cp3_after_a_booked_forward_monday_d_minus_1_is_the_friday |
| 39 | cp3-entry-bar | cp3.py | entry on the 08:30 bar | KILLED | 25; test_cp3_a_booked_forward_holiday_session_is_never_a_daily_bar, test_cp3_a_day_with_two_instrument_ids_is_incomplete |
| 40 | cp3-exit-2 | cp3.py | exit bar C-2 (14:58) | KILLED | 24; test_cp3_a_booked_forward_holiday_session_is_never_a_daily_bar, test_cp3_a_day_with_two_instrument_ids_is_incomplete |
| 41 | cp3-ge | cp3.py | non-strict buy cut | KILLED | 22; test_cp3_a_booked_forward_holiday_session_is_never_a_daily_bar, test_cp3_after_a_booked_forward_monday_d_minus_1_is_the_friday |
| 42 | cp3-halt-complete | cp3.py | a halt day's bar is incomplete | KILLED | 2; test_cp3_early_halt_day_is_not_traded_and_is_incomplete, test_cp3_the_halt_flag_resets_each_trade_date |
| 43 | cp3-halt-entry | cp3.py | an early-halt day d is not traded | KILLED | 3; test_cp3_a_halt_day_with_a_buy_prior_is_still_not_traded, test_cp3_early_halt_day_is_not_traded_and_is_incomplete |
| 44 | cp3-idguard | cp3.py | instrument guard d-1 vs the 08:30 bar | KILLED | 1; test_cp3_instrument_guard_compares_d_minus_1_with_the_0830_bar |
| 45 | cp3-incomplete-used | cp3.py | incomplete days are dropped, never used as d-1 | KILLED | 4; test_cp3_a_day_with_two_instrument_ids_is_incomplete, test_cp3_early_halt_day_is_not_traded_and_is_incomplete |
| 46 | cp3-le | cp3.py | non-strict sell cut | KILLED | 10; test_cp3_a_day_with_two_instrument_ids_is_incomplete, test_cp3_after_a_booked_forward_monday_d_minus_1_is_the_friday |
| 47 | cp3-needs-close | cp3.py | the 14:59 bar must exist for a complete day | KILLED | 3; test_cp3_a_booked_forward_holiday_session_is_never_a_daily_bar, test_cp3_d_minus_1_is_the_most_recent_complete_day |
| 48 | cp3-needs-open | cp3.py | the 08:30 bar must exist for a complete day | KILLED | 1; test_cp3_missing_0830_bar_is_no_trade_and_the_day_is_incomplete |
| 49 | cp3-oneid | cp3.py | one instrument_id per daily bar | KILLED | 1; test_cp3_a_day_with_two_instrument_ids_is_incomplete |
| 50 | cp3-otherdate | cp3.py | bars of another CT date never read | KILLED | 3; test_cp3_a_booked_forward_holiday_session_is_never_a_daily_bar, test_cp3_after_a_booked_forward_monday_d_minus_1_is_the_friday |
| 51 | cp3-range0 | cp3.py | Range > 0 | KILLED | 2; test_cp3_clv_cuts_are_compared_exactly[0-0-None], test_cp3_zero_range_is_no_trade |
| 52 | cp3-sell-019 | cp3.py | CLV <= 0.2 sells | KILLED | 11; test_cp3_a_day_with_two_instrument_ids_is_incomplete, test_cp3_after_a_booked_forward_monday_d_minus_1_is_the_friday |
| 53 | cp3-sell-021 | cp3.py | CLV <= 0.2 sells | KILLED | 1; test_cp3_literals_are_the_clv_cuts_and_the_clock |
| 54 | cp3-window | cp3.py | daily bar over [O, C) | KILLED | 26; test_cp3_a_booked_forward_holiday_session_is_never_a_daily_bar, test_cp3_a_day_with_two_instrument_ids_is_incomplete |
| 55 | exp-dates | expiry.py | C4 exclusions (full sessions, vendor-degraded) | KILLED | 4; test_expiry_a_vendor_degraded_mbtx_date_is_not_traded, test_expiry_no_trade_off_the_event_set[day1] |
| 56 | exp-delay | expiry.py | entry intent one bar before the fill | KILLED | 8; test_expiry_10_00_enters_at_04_59_for_05_00_and_exits_at_09_58_for_09_59, test_expiry_11_00_enters_at_05_59_for_06_00_and_exits_at_10_58_for_10_59 |
| 57 | exp-direction | expiry.py | long only | KILLED | 6; test_expiry_10_00_enters_at_04_59_for_05_00_and_exits_at_09_58_for_09_59, test_expiry_11_00_enters_at_05_59_for_06_00_and_exits_at_10_58_for_10_59 |
| 58 | exp-entry-300 | expiry.py | entry bar T_exp - 301 | KILLED | 8; test_expiry_10_00_enters_at_04_59_for_05_00_and_exits_at_09_58_for_09_59, test_expiry_11_00_enters_at_05_59_for_06_00_and_exits_at_10_58_for_10_59 |
| 59 | exp-exact-bar | expiry.py | entry on the exact T_exp - 301 bar only | KILLED | 7; test_expiry_10_00_enters_at_04_59_for_05_00_and_exits_at_09_58_for_09_59, test_expiry_11_00_enters_at_05_59_for_06_00_and_exits_at_10_58_for_10_59 |
| 60 | exp-exit-1 | expiry.py | exit bar T_exp - 2 | KILLED | 6; test_expiry_10_00_enters_at_04_59_for_05_00_and_exits_at_09_58_for_09_59, test_expiry_11_00_enters_at_05_59_for_06_00_and_exits_at_10_58_for_10_59 |
| 61 | exp-exit-early | expiry.py | no exit before the exit bar | KILLED | 5; test_expiry_10_00_enters_at_04_59_for_05_00_and_exits_at_09_58_for_09_59, test_expiry_11_00_enters_at_05_59_for_06_00_and_exits_at_10_58_for_10_59 |
| 62 | exp-window | expiry.py | trading window (05:00, 11:00) | KILLED | 1; test_trading_windows_are_the_s0_12_intervals |
| 63 | rev-block-119 | rev2h.py | 120-minute blocks | KILLED | 17; test_trading_windows_are_the_s0_12_intervals, test_a_missing_10_30_bar_means_no_entry_and_no_b2_signal |
| 64 | rev-dates | rev2h.py | C4 exclusions (full sessions, vendor-degraded) | KILLED | 3; test_no_trade_off_the_entry_dates[d0], test_no_trade_off_the_entry_dates[d1] |
| 65 | rev-direction | rev2h.py | against sign(r) | KILLED | 14; test_a_missing_12_29_bar_flattens_on_the_first_later_bar_and_does_not_enter, test_a_missing_12_30_bar_flattens_but_does_not_enter |
| 66 | rev-final-1 | rev2h.py | final exit on 14:29 | KILLED | 7; test_an_engine_closed_position_leaves_the_12_30_decision_as_written, test_an_entry_bar_with_another_instrument_is_no_entry |
| 67 | rev-one-decision | rev2h.py | decisions at 10:30 and 12:30 | KILLED | 11; test_a_missing_12_29_bar_flattens_on_the_first_later_bar_and_does_not_enter, test_a_missing_12_30_bar_flattens_but_does_not_enter |
| 68 | rev-sigend-1 | rev2h.py | r closes on the t-1 bar | KILLED | 12; test_a_missing_12_29_bar_flattens_on_the_first_later_bar_and_does_not_enter, test_a_missing_12_30_bar_flattens_but_does_not_enter |
| 69 | rev-start | rev2h.py | r opens on the block's first bar | KILLED | 6; test_a_missing_10_30_bar_means_no_entry_and_no_b2_signal, test_a_missing_b1_endpoint_is_target_zero[510] |
| 70 | rev-window | rev2h.py | trading window to 14:31 | KILLED | 1; test_trading_windows_are_the_s0_12_intervals |
| 71 | mon-dates | montrend.py | C4 exclusions (full sessions, vendor-degraded) | KILLED | 2; test_no_trade_off_the_monday_entry_dates[d0], test_no_trade_off_the_monday_entry_dates[d1] |
| 72 | mon-direction | montrend.py | with s_t | KILLED | 14; test_a_flatten_is_not_sent_while_an_order_is_pending_and_is_resent, test_a_missing_13_59_bar_exits_on_the_first_later_bar |
| 73 | mon-final-1 | montrend.py | final exit on the 13:59 bar | KILLED | 3; test_at_most_20_entries_one_per_decision, test_monday_morning_decisions_and_the_final_exit_on_13_59 |
| 74 | mon-first-1700 | montrend.py | no decision at Sunday 17:00 | KILLED | 4; test_trading_windows_are_the_s0_12_intervals, test_at_most_20_entries_one_per_decision |
| 75 | mon-first-1900 | montrend.py | first decision Sunday 18:00 | KILLED | 12; test_trading_windows_are_the_s0_12_intervals, test_a_missing_t_bar_means_no_entry_but_the_flatten_stands |
| 76 | mon-flat-1401 | montrend.py | flat at 14:00 | KILLED | 4; test_trading_windows_are_the_s0_12_intervals, test_at_most_20_entries_one_per_decision |
| 77 | mon-last-1200 | montrend.py | 20 decisions | KILLED | 4; test_a_missing_13_59_bar_exits_on_the_first_later_bar, test_at_most_20_entries_one_per_decision |
| 78 | mon-last-1400 | montrend.py | last decision Monday 13:00 | KILLED | 3; test_at_most_20_entries_one_per_decision, test_no_decision_after_13_00 |
| 79 | mon-lookback-59 | montrend.py | t - 60 open | KILLED | 11; test_trading_windows_are_the_s0_12_intervals, test_a_missing_t_bar_means_no_entry_but_the_flatten_stands |
| 80 | mon-sigend-1 | montrend.py | t - 1 close | KILLED | 14; test_a_missing_13_59_bar_exits_on_the_first_later_bar, test_a_missing_t_bar_means_no_entry_but_the_flatten_stands |
| 81 | mon-step-30 | montrend.py | hourly decisions | KILLED | 12; test_a_missing_t_bar_means_no_entry_but_the_flatten_stands, test_a_missing_t_minus_1_bar_flattens_on_the_first_later_bar_without_entry |
| 82 | mon-weekday | montrend.py | Mondays only | KILLED | 15; test_a_flatten_is_not_sent_while_an_order_is_pending_and_is_resent, test_a_missing_13_59_bar_exits_on_the_first_later_bar |
| 83 | mon-window | montrend.py | trading window from Sunday 17:00 | KILLED | 1; test_trading_windows_are_the_s0_12_intervals |
| 84 | ec-close-pending | _event_common.py | no flatten while an order is pending | KILLED | 3; test_expiry_no_entry_while_pending_and_the_exit_waits_while_pending, test_a_flatten_is_not_sent_while_an_order_is_pending_and_is_resent |
| 85 | ec-close-side | _event_common.py | the flatten closes the position | KILLED | 30; test_expiry_10_00_enters_at_04_59_for_05_00_and_exits_at_09_58_for_09_59, test_expiry_11_00_enters_at_05_59_for_06_00_and_exits_at_10_58_for_10_59 |
| 86 | ec-end-close | _event_common.py | the signal uses the end bar's CLOSE | SURVIVED | none |
| 87 | ec-entry-dates | _event_common.py | ENTRY_DATES excludes VENDOR_DEGRADED | KILLED | 3; test_entry_dates_are_full_sessions_less_vendor_degraded, test_no_trade_off_the_monday_entry_dates[d0] |
| 88 | ec-entry-exact | _event_common.py | entry on the exact t bar only | KILLED | 16; test_a_missing_13_59_bar_exits_on_the_first_later_bar, test_a_missing_t_bar_means_no_entry_but_the_flatten_stands |
| 89 | ec-entry-flat | _event_common.py | entry only when flat (no pending) | KILLED | 2; test_a_flatten_is_not_sent_while_an_order_is_pending_and_is_resent, test_no_flatten_and_no_entry_while_an_order_is_pending |
| 90 | ec-entry-id | _event_common.py | the entry bar carries the signal bars' id | KILLED | 2; test_an_entry_bar_with_another_instrument_is_no_entry, test_an_entry_bar_with_another_instrument_is_no_entry |
| 91 | ec-entry-zero | _event_common.py | target 0: no entry | KILLED | 22; test_a_missing_13_59_bar_exits_on_the_first_later_bar, test_a_missing_t_bar_means_no_entry_but_the_flatten_stands |
| 92 | ec-final-ge | _event_common.py | final exit at or after the named bar | KILLED | 8; test_at_most_20_entries_one_per_decision, test_monday_morning_decisions_and_the_final_exit_on_13_59 |
| 93 | ec-flatten-zero | _event_common.py | s_t = 0 flattens | KILLED | 13; test_a_missing_t_minus_1_bar_flattens_on_the_first_later_bar_without_entry, test_a_missing_t_minus_60_bar_is_signal_zero |
| 94 | ec-hold | _event_common.py | hold on an equal target (flatten only on a sign change) | KILLED | 10; test_a_flatten_is_not_sent_while_an_order_is_pending_and_is_resent, test_a_missing_t_minus_1_bar_flattens_on_the_first_later_bar_without_entry |
| 95 | ec-idguard | _event_common.py | signal endpoints with two ids: target 0 | KILLED | 3; test_signal_bars_with_two_instruments_are_signal_zero, test_an_instrument_change_between_the_b1_endpoints_is_target_zero |
| 96 | ec-missed | _event_common.py | a missing t-1 bar gives target 0 (K7-L-08) | KILLED | 2; test_a_missing_t_minus_1_bar_flattens_on_the_first_later_bar_without_entry, test_a_missing_12_29_bar_flattens_on_the_first_later_bar_and_does_not_enter |
| 97 | ec-missing-start | _event_common.py | a missing start bar gives target 0 | KILLED | 4; test_a_missing_t_bar_means_no_entry_but_the_flatten_stands, test_a_missing_t_minus_60_bar_is_signal_zero |
| 98 | ec-q | _event_common.py | size q_c | KILLED | 26; test_a_missing_13_59_bar_exits_on_the_first_later_bar, test_a_missing_t_bar_means_no_entry_but_the_flatten_stands |
| 99 | ec-start-open | _event_common.py | the signal uses the start bar's OPEN | KILLED | 13; test_a_missing_12_29_bar_flattens_on_the_first_later_bar_and_does_not_enter, test_a_missing_12_30_bar_flattens_but_does_not_enter |
| 100 | ec-ticks-trunc | _event_common.py | integer ticks by round() | KILLED | 1; test_size_is_the_frozen_q_c_and_prices_are_integer_ticks |
| 101 | cal-degraded-drop | _calendar.py | VENDOR_DEGRADED row | KILLED | 2; test_entry_dates_are_full_sessions_less_vendor_degraded, test_vendor_degraded_is_the_build_bars_mapping_of_both_condition_files |
| 102 | cal-full-drop | _calendar.py | CRYPTO_FULL_SESSIONS row | KILLED | 15; test_crypto_full_sessions_are_ec_cal_dates_without_halt_and_with_the_regular_f, test_entry_dates_are_full_sessions_less_vendor_degraded |
| 103 | cal-mbtx-add | _calendar.py | R-1b-1: CME's 2025-12-26 not added | KILLED | 3; test_expiry_no_trade_off_the_event_set[day4], test_mbtx_is_the_c9_rule_less_the_two_r_1b_1_drops |
| 104 | cal-mbtx-drop | _calendar.py | an MBTX row | KILLED | 2; test_mbtx_is_the_c9_rule_less_the_two_r_1b_1_drops, test_the_expiry_event_set_and_its_clocks |
| 105 | cal-mbtx-texp | _calendar.py | T_exp 11:00 on 2026-03-27 | KILLED | 1; test_mbtx_is_the_c9_rule_less_the_two_r_1b_1_drops |

Totals: 105 mutants; KILLED 104, SURVIVED 1, PATTERN-MISS 0

Survivor analysis. `ec-end-close` changes _event_common.py:203 from `to_ticks(bar.close, ...)` to the
end bar's OPEN. All 87 event tests pass because tests/test_k7_members_events.py:124-140 builds every bar
with open = close unless `opens[minute]` is set, and the rev2h and montrend scenarios set `opens` only
on the START bars (08:30, 10:30; Sunday 17:00), never on the end bars (10:29, 12:29; xx:59). So the
frozen text's "close of the 10:29 bar" and "close of the bar at t - 1 min" is not pinned by any test. The
code is correct: with the 10:29 bar opening at -30 and closing at +10 (open(08:30) = 0) rev2h sells at
10:31 (r1 = +10), and montrend buys at 18:01 with the same shape on the 17:59 bar. Finding F-1.

Vacuous or weak tests found: events_montrend.py:160 `test_a_booked_forward_monday_is_not_traded` (see
F-8a). No other test passes vacuously: every remaining mutant was killed by at least one rule test, and I
read each test's assertion against its docstring.

### 6. Findings

BLOCKING: none. No module implements anything other than its frozen entry, and no member reads a
future bar, a hindsight field or an unavailable input.

SHOULD FIX
- F-1 (tests do not pin what they claim; tests/test_k7_members_events_rev2h.py:55-63, 65, and
  tests/test_k7_members_events_montrend.py:54-59 with tests/test_k7_members_events.py:124-140). No event
  test distinguishes the t - 1 bar's close from its open: mutant `ec-end-close` (signal from the end bar's
  OPEN) survives all 87 event tests. The docstrings claim "B1 up -> sell" and "s_18 = sign(close(17:59) -
  open(17:00))", but the scenarios give every end bar open = close. Smallest fix, inside the frozen entry:
  in B1_UP and b2() (events_rev2h.py:38-46) and FIRST_UP (events_montrend.py:44-46) give the end bars an
  open of the opposite sign to their close (for example `"opens": {hm(10, 29): -30}` with close +10, and
  `eve(17, 59): -30` with close +10) so an open-reading rule flips the direction; the existing assertions
  then kill the mutant. The code itself is right (_event_common.py:203).

NOTE
- F-2 (spec wording and basis; reports/stage_e6_member_specs.md section 5 rows "Decision 10:30" and
  "Decision 12:30", section 6 row "Entry", S0.9, and section 8's "the text is the same" for E.3-L-12/13).
  The rev2h rows say the target is 0 when "the 08:30, 10:29 and 10:30 (entry) bars do not carry one
  instrument_id", but the flatten or hold is decided at the 10:29 close, before the 10:30 bar exists; the
  code (and K7-L-06's own sentence "Exits and flattens are unguarded") lets the 10:30 bar's id gate only
  the entry (_event_common.py:221-223; events_rev2h.py:150; events_montrend.py:204). Coder B raised it
  (report section 6, question 1). Also, K7's C4 (line 135-137) says "signal bars of one computation carry
  different instrument_ids", while K2's C4 names "the entry bar"; the entry-bar gate is therefore a K7
  narrowing, not the same text. It cannot change a trade on real bars (MBT.v.0 changes instrument_id at
  00:00 UTC on a splice trade date, which is a roll-blackout date, and the engine raises if a position
  spans a change). Fix: reword the two rows to "target = 0 if an endpoint bar is missing or the two carry
  different instrument_ids; the entry on the decision-time bar is sent only if that bar carries their
  instrument_id", and cite the gate as K7-L-06's own reading.
- F-3 (K7-L-03 mapping consequence). Under the per-bar flag (build_bars.py:728) nine further trade dates
  carry flagged bars (section 3); none of them is a bar a K7 member reads in the research window (the
  flagged bars are the next trade date's 17:00-18:59 CT bars, which only montrend reads, and only on
  Sundays: 2026-03-15 leads to Monday 03-16, excluded anyway; 2026-05-24 to Tuesday 05-26, not a Monday).
  In the confirmation window Mondays 2021-12-06 and 2022-01-03 would trade on flagged Sunday-evening bars
  (coder B question 2). The ISO mapping is right; the lead's flag to the user should name those two Mondays.
- F-4 (K7-L-12 gaps). Section 7 item 13 (b), (c), (d), (h) are not named. (b) and (h) are moot for K7's
  members (none reads a release; D1's dates predate the change). (d) is settled by the harness: MBT is
  DCB-only in rules/price_limits.py, so D9.7 never fires on it, consistent with C13's "assumes no limit is
  hit", and K7-L-07 is moot except for F and an MLL liquidation. (c) MBT's tick history 2021-05..2026-06 is
  a confirmation-session check; the research window uses the frozen 5.00. One sentence in K7-L-12 closes it.
- F-5 (K7-L-05 wording). C section 7 item 8 offers two options (withdraw, or a different roll convention);
  the lead took a third (run as frozen, 0 trades expected, counted when the runner writes its record). It is
  within the text (the frozen entry stands unless withdrawn; the roll convention is frozen harness) and the
  narrowest (nothing changed). State the consequence in the entry: the trial adds 1 to N with a certain
  fail, which is conservative for the other five. Not a fidelity issue.
- F-6 (literals that duplicate derived values). expiry.py:56-57 WINDOW_START_CT / WINDOW_END_CT are
  literal 05:00 / 11:00 rather than derived from T_EXP_SLOTS and the two offsets; cp2.py:57 F_REGULAR_CT is
  a literal 15:08 (K4 precedent; rules.sessions is not an allowed member import). Both match S0.12 today
  and each is pinned by a test (events.py:434; ports.py:351, 307). No trade effect.
- F-7 (a source disagreement outside the window, for later sessions). The F test alone removes 2024-07-03
  from CRYPTO_FULL_SESSIONS: data/calendars/crypto.py has no early halt there while rules.sessions flattens
  MBT at 11:30. It lies in holdout-2, so nothing here depends on it; the two frozen sources disagree on
  that date and the confirmation and holdout sessions should know.
- F-8 (test coverage notes). (a) events_montrend.py:160 labels the booked-forward holiday's bars with
  trade date 2026-01-20, a Tuesday, so the test passes on the weekday check alone and pins nothing about
  the tables; the table fact is pinned separately (events.py:297 `not booked & set(full)`). (b) No port
  test feeds a weekday 16:00-16:59 CT bar of CT date d-1 carrying trade date d (the 24/7 regime's
  Tuesday-to-Friday case of C3); the code path is the generic `at != 17:00` / `opened.date() != day`
  (cp1.py:239-243) and the Friday 16:02 weekend bars exercise it. A coverage note, not a rule gap.
- F-9 (coverage windows). S0.12's intervals are measured on every research date (E.3-L-17), so
  montrend's (17:00 day -1, 14:00) and expiry's (05:00, 11:00) are measured on weekday overnights the
  members never trade; C12's "in its own window" is narrower, but the interface has no per-date condition.
  It can only exclude a member before screening (then, per K7-L-05's rule, it is not a trial); it cannot
  widen a rule. The lead should expect this when reading the runner's coverage output.

## Part 2: recomputation (Task 6)
