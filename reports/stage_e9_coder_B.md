<!-- Saved by the Stage E.9 lead from MemberCoder-B-OpusXHigh's final message (the harness refused the worker's own write), 2026-10-01 23:08 PDT. Text unchanged. -->

# Stage E.9 Task 2, coder B: K8-oilcad-01 and K8-wkndbtc-01

MemberCoder-B-OpusXHigh (worker-xhigh, opus), 2026-10-01, about 22:37 to 23:10 PDT. I took the tables from coder A and wrote none of them. No bar file was opened, there was no web access, the harness was not changed and nothing was committed. Holdout `unlocks_logged` was 0 at start and end, and REGISTRATION.md is 0 bytes.

## 1. Files

| File | Lines | sha256 |
|---|---|---|
| strategy/members/k8/oilcad.py | 271 | b64db6b459c047dfba3ebb5ec94b91deba0cd0aace17a4e816ad911d0d5b910c |
| strategy/members/k8/wkndbtc.py | 191 | 04847787d465c10f66e8250d860e9ac744cba5ee0c104c55bb3458ab3906a243 |
| tests/test_k8_members_oilcad.py | 797 | 9c84f2bb5a8a6a1901fc5fddbadbaceb6fea31b348a574ad95bdc9254a5d51b4 |
| tests/test_k8_members_wkndbtc.py | 386 | fe6708d3e1aeaa28f9c1ec72203a6ed4ec567bfeedf78ad6251df1f9f4a65cb7 |

- Both member files pass `check_member_source` for cluster K8 with no finding.
- Each member file defines its own small clock and tick helpers. No `_common.py` existed when I wrote them, and that file is coder A's.
- tests/test_k8_members_oilcad.py also holds the shared K8 test kit (synthetic bars, direct-call driver, engine frames, runner-style rules). The wkndbtc tests import it.

## 2. What the code does

**K8-oilcad-01** ("K8-oilcad-01 6C"; legs 6C traded, MCL signal; q_c from the frozen vehicle table = 1)
- Trading windows: 6C (08:04, 13:41), MCL (07:59, 13:25).
- MCL bars are read only on their own CT date (CT date equals trade_date).
- Each close at a t - 6 clock (07:59 to 13:19) is kept with its instrument_id. At the bar at t - 1, r_t = (c1 - c6) / c6 is computed from integer ticks as a float.
- r_t is defined only when the two ids are equal and c6 > 0. Every defined r_t is filed under its trade date, whether or not it trades.
- The kept t - 6 bars are cleared at each new MCL trade date.
- s(d) is `statistics.stdev` over `previous_dates(OILCAD_DATES, d, 20)`, computed once per day. It is None (no trade on d) when:
  - fewer than 20 reference dates exist;
  - a reference date precedes the trade date of the first bar received (K4-L-09);
  - n < 1,000;
  - s = 0.
- Entry happens on the t - 1 view when all of these hold:
  - both the MCL and 6C bars at t - 1 are present, and the 6C bar is on its own CT date;
  - d is in OILCAD_DATES;
  - the account is flat on 6C (no position and no pending order);
  - |r / s| >= 2.0;
  - `in_guard("6C", 6C bar open + 60 s)` is False, which tests the fill minute t.
- The intent is market q_c: buy if c1 > c6, sell if c1 < c6.
- T_e is the minute of the first view whose account shows a position; it resets when flat.
- Exit: on every present 6C bar at or after T_e + 14 while the position is open and nothing is pending, a market intent for the whole position.

**K8-wkndbtc-01** ("K8-wkndbtc-01 MNQ"; legs MNQ traded, MBT signal; q_c 1)
- Trading windows as S0.12.
- The member keeps the latest MBT bar at 14:59 whose CT date equals its trade date.
- Entry happens on the view of the MNQ bar at 17:59 on CT date d - 1 (trade_date d) when all of these hold:
  - d is a Monday, and both d and d - 3 are in WKNDBTC_DATES;
  - the MBT bar of that same minute is present with trade_date d;
  - the kept 14:59 bar is from CT date d - 3, with the same instrument_id;
  - G = P_S - P_F in ticks is not 0;
  - the account is flat;
  - the Sunday 18:00 fill minute is not guarded for MNQ.
- Exit: on every present MNQ bar at or after Monday 14:58 of d, with nothing pending, for the whole position.

Readings applied as written: K8-L-04 to K8-L-12. R-1b-1 holds: the dropped WPSR row at 2026-05-28 11:00 is still skipped, and a test covers it.

## 3. What the tests pin

**oilcad (60 tests).** The reference set STANDARD has 20 dates with 125 values of +u, 125 of -u and 751 zeros (u = 1/6000, n = 1001), so s(d) is exactly u/2. Each nonzero step returns to the base under a new instrument_id, so the returns don't count as values.
- Clock:
  - 65 decisions from 08:05 to 13:25;
  - no decision at 08:00 or 13:30, even with big MCL moves and 6C bars present;
  - r_t reads exactly the 08:04 and 07:59 closes (decoy bars around them are ignored);
  - the entry is on the t - 1 view.
- Arithmetic:
  - c6 > 0, both in `block_return` and with a zero close at 07:59;
  - ddof 1 with a hand-computed case, and end to end at z = 1.99967 vs 2.00067;
  - n = 999 refused, n = 1000 accepted;
  - s = 0 means no trade;
  - |z| = 2.0 exactly trades, and the float just below does not;
  - sign.
- Reference dates and warm-up:
  - only the 20 previous OILCAD dates count (extra values on 2025-06-09, 2025-06-19 and 2025-07-04 would break z = 2.0);
  - a run starting on S[0] has no trade on S[19] (n = 1045, z about 7) and trades on S[20];
  - only 19 dates at the table start means no trade;
  - a non-OILCAD date never trades.
- Guards and missing bars:
  - an MCL id change at 09:04 blocks 09:05 while 09:10 still trades;
  - a missing 6C bar at t - 1 blocks that t only;
  - a missing MCL bar at t - 1 blocks two blocks;
  - a late MCL bar is never used;
  - a missing t - 6 bar blocks t;
  - the previous date's t - 6 bar is never used;
  - mislabelled bars for 6C and for MCL (CT date d + 1 carrying trade date d) are rejected.
- C6:
  - 09:30 is skipped on a WPSR date and 09:35 is not;
  - 09:30 is not skipped on a non-WPSR date;
  - 13:00 is skipped on an FOMC date;
  - 11:00 is skipped on holiday-week WPSR dates, including 2026-05-28;
  - a spy shows the guard is called once with ("6C", t);
  - a skipped decision leaves later decisions alone.
- Flat-only and exit:
  - no entry with a position of plus or minus 1, or a pending order of plus or minus 1;
  - the exit at T_e + 14 is resent until it is pending;
  - a short's exit buys;
  - a position of 2 is closed whole;
  - a missing exit bar moves the exit to the next present bar.
- Engine:
  - fills at 09:05 and exits at 09:20, 6C intents only, quantity 1;
  - the sell side;
  - T_e = 09:06 when the 09:05 bar is missing;
  - a missing exit bar gives an exit fill at 09:21;
  - spacing: the 09:20 decision falls on the exit view (no entry), 09:25 enters and exits at 09:40;
  - a late fill at 09:09 holds through the 09:10 decision;
  - engine closure via a bar flatten flag (forced_flatten at 09:11, then 09:20 re-enters and exits at 09:35);
  - nothing after the 13:40 fill;
  - a roll blackout on MCL only is refused with `engine_not_a_window_date` under the runner's rules and with `engine_roll_blackout` when the date stays in the window;
  - a 6C blackout also refuses;
  - a roll-blackout reference date still contributes its values.

**wkndbtc (39 tests).** Every MBT bar other than P_F and P_S is priced so that reading it flips the side. After the 24/7 change, the test week also has weekend MBT decoys booked to Monday.
- Facts: 54 eligible research Mondays (51 before the change); no MNQ guard at any Sunday 18:00 or Monday 14:59.
- Declaration: name, legs, q_c, windows, static check.
- Clock points and sign:
  - buy, sell, G = 0, and one-tick moves;
  - Friday 14:59 missing: the 14:58 and 15:00 bars are never used;
  - Sunday 17:59 missing: 17:58 and the late 18:00 bar are never used;
  - MNQ 17:59 missing;
  - an MBT Sunday bar wrongly labelled with Sunday's trade date;
  - an id change between P_F and P_S;
  - a stale Friday (2025-06-06) is never used for 2025-06-16;
  - a Thursday whose d - 3 is a Monday never trades.
- Exclusions: 2025-05-26, 2025-04-21, 2025-12-01.
- Regimes:
  - 2026-05-18 and 2026-06-08 both buy and sell from the same two bars;
  - after the change, Saturday and Sunday 14:59 bars and Saturday and Friday 17:59 bars never stand in;
  - a synthetic Saturday 17:59 MNQ bar booked to Monday is never the entry bar.
- C6: a spy shows the guard is called once with ("MNQ", Sunday 18:00); a guarded 18:00 is skipped.
- Flat-only and exit:
  - no entry with a position or a pending order;
  - the 14:58 exit is resent at 14:59 and stops once pending;
  - a short's exit buys, and a missing 14:58 bar moves the exit to 14:59;
  - a position of 2 is closed whole.
- Engine:
  - fills Sunday 18:00 and exits Monday 14:59, MNQ intents only, nothing decided after 14:59;
  - sell side after the change;
  - a missing 14:58 bar gives an exit fill at 15:00;
  - MBT-only blackout refused, as for oilcad;
  - an MBT blackout on Friday d - 3 alone does not block the Monday.

## 4. Mutants

The script changes one item in place, runs the member's test file with a fresh pycache prefix and no bytecode writes, then restores the file. Both files' sha256 matched after the run. The table shows the number of failing tests and up to two of them.

| Id | Mutant | n | Killed by |
|---|---|---|---|
| O01 | first t 08:05 -> 08:00 | 3 | decision_clock; no_decision_at_08_00 |
| O02 | first t -> 08:10 | 31 | 09_30_non_wpsr; many |
| O03 | last t 13:25 -> 13:30 | 3 | decision_clock; no_decision_at_13_30 |
| O04 | last t -> 13:20 | 4 | decision_clock; engine_nothing_after_13_40 |
| O05 | step 5 -> 10 | 32 | many |
| O06 | step 5 -> 1 | 1 | decision_clock |
| O07 | c1 bar t-1 -> t-2 | 32 | many |
| O08 | c1 bar t-1 -> t | 32 | many |
| O09 | c6 bar t-6 -> t-5 | 32 | many |
| O10 | c6 bar t-6 -> t-7 | 32 | many |
| O11 | 20 reference dates -> 19 | 31 | many |
| O12 | 20 -> 21 | 31 | many |
| O13 | n >= 1000 -> 999 | 2 | n_1000_trades_and_n_999_does_not; scale_refuses |
| O14 | n >= 1000 -> 1001 | 2 | same |
| O15 | \|z\| >= 2.0 -> 1.9996 | 2 | ddof_1_end_to_end; threshold_inclusive |
| O16 | \|z\| >= 2.0 -> 2.0000001 | 4 | reference_dates_are_the_20_previous; z_exactly_2 |
| O17 | exit T_e+14 -> +13 | 14 | engine_fills; engine_closure |
| O18 | exit -> +15 | 12 | engine_fills; engine_closure |
| O19 | c6 <= 0 -> < 0 | 2 | zero_close; block_return |
| O20 | n < MIN -> <= | 2 | n_1000; scale_refuses |
| O21 | stdev -> pstdev | 3 | ddof_1_end_to_end; scale_ddof_1 |
| O22 | s <= 0 -> < 0 | 2 | scale_refuses; zero_scale |
| O23 | >= -> > | 4 | z_exactly_2; references |
| O24 | abs removed | 5 | engine_sell_side; others |
| O25 | prune drops refs[0] | 29 | many |
| O26 | MCL CT-date check removed | 1 | an_mcl_bar_is_read_on_its_own_ct_date_only |
| O27 | MCL id guard removed | 5 | mcl_roll_inside_a_block; others |
| O28 | warm-up >= -> > | 30 | many |
| O29 | warm-up removed | 1 | warm_up_20th_21st |
| O30 | accepts 19 refs | 1 | too_few_reference_dates |
| O31 | pending blocks entry removed | 2 | no_entry_while_pending (both) |
| O32 | pending blocks exit removed | 1 | exit_resent_while_not_pending |
| O33 | exit < -> <= | 10 | engine_fills; others |
| O34 | exit side swapped | 12 | engine tests |
| O35 | exit qty -> 1 | 1 | every_exit_closes_the_whole_position |
| O36 | 6C CT-date check removed | 1 | bars_are_identified_by_ct_date |
| O37 | r_t-defined check removed | 42 | many |
| O38 | OILCAD membership removed | 1 | a_date_outside_oilcad_dates |
| O39 | C6 at t-1 | 5 | c6_skips_09_30; spy |
| O40 | C6 at t+1 | 2 | c6_spy; skipped_decision |
| O41 | C6 on MGC | 3 | c6_skips_09_30; c6_11_00 |
| O42 | entry side swapped | 31 | many |
| O43 | diff > 0 -> >= 0 | 0 | SURVIVED (equivalent) |
| O44 | q_c + 1 | 27 | many |
| O45 | T_e = decision minute | 12 | engine tests |
| O46 | T_e not reset | 14 | engine tests |
| O47 | first-day min -> max | 0 | SURVIVED (equivalent) |
| O48 | t-6 store not reset per day | 1 | a_previous_dates_t_minus_6_bar_is_never_used |
| O49 | diff sign flipped | 31 | many |
| O50 | 6C window end 13:41 -> 13:40 | 1 | trading_windows |
| O51 | MCL window end -> 13:26 | 1 | trading_windows |
| O52 | s(d) cache removed | 0 | SURVIVED (equivalent) |
| O53 | undefined r filed | 1 | zero_close |
| W01 | Monday -> Tuesday | 18 | many |
| W02 | P_F d-3 -> d-2 | 18 | many |
| W03 | P_F d-3 -> d-4 | 18 | many |
| W04 | Sunday d-1 -> d-2 | 17 | many |
| W05 | Sunday d-1 -> d | 17 | many |
| W06 | P_F 14:59 -> 14:58 | 21 | many |
| W07 | P_F 14:59 -> 15:00 | 21 | many |
| W08 | 17:59 -> 17:58 | 24 | many |
| W09 | 17:59 -> 18:00 | 24 | many |
| W10 | exit 14:58 -> 14:57 | 7 | engine_fills; engine_missing_exit |
| W11 | exit 14:58 -> 14:59 | 5 | engine_fills; engine_sell_side |
| W12 | weekday check removed | 2 | a_non_monday_never_trades; research_window_mondays |
| W13 | d in WKNDBTC removed | 2 | excluded_mondays[2025-05-26]; is_trade_monday |
| W14 | d-3 in WKNDBTC removed | 4 | excluded_mondays[04-21, 12-01] |
| W15 | G > 0 -> >= 0 | 2 | g_zero; side_of |
| W16 | G < 0 -> <= 0 | 2 | g_zero; side_of |
| W17 | entry side swapped | 17 | many |
| W18 | P_F CT-date check removed | 3 | saturday_mnq; both_regimes[after] |
| W19 | P_F clock check removed | 20 | many |
| W20 | entry clock check removed | 23 | many |
| W21 | entry CT-date check removed | 1 | a_saturday_mnq_bar_booked_to_monday |
| W22 | P_S trade_date check removed | 1 | mbt_sunday_bar_must_carry_trade_date_d |
| W23 | P_F date check removed | 1 | p_f_from_d_minus_3_never_stale |
| W24 | id guard removed | 1 | one_instrument_id_across_p_f_and_p_s |
| W25 | C6 at 17:59 | 2 | c6 spy; c6 skip |
| W26 | C6 on MGC | 1 | c6 spy |
| W27 | exit < -> <= | 4 | engine_fills; engine_sell_side |
| W28 | exit side swapped | 6 | engine tests |
| W29 | pending blocks exit removed | 3 | exit_resent_while_not_pending; whole_position |
| W30 | pending blocks entry removed | 2 | no_entry_while_pending (both) |
| W31 | exit qty -> 1 | 1 | every_exit_closes_the_whole_position |
| W32 | exit instant on d-1 | 6 | engine tests |
| W33 | q_c + 1 | 13 | many |
| W34 to W37 | window ends | 1 each | trading_windows |
| W38 | G sign flipped | 16 | many |

Survivors, all equivalent on any input the engine can produce:
- **O43:** an entry needs |z| >= 2 with s > 0, so the tick difference is never 0 at an entry.
- **O47:** the two bars of one view share a minute, and energy and FX change trade date at the same moment (17:00 CT), so min and max are the same date.
- **O52:** the cache only saves time; the history s(d) depends on is complete before d's first decision.

Two earlier survivors were closed by new or changed tests: O26 and O30. One redundant check (the signal's t compared with the 6C bar's t, always equal within one view) was removed from `oilcad._entry`.

## 5. Commands and results

- `uv run pytest -q tests/test_k8_members_oilcad.py tests/test_k8_members_wkndbtc.py tests/test_stage_e_template.py tests/test_stage_e_freeze.py -p no:cacheprovider`, with PYTHONPYCACHEPREFIX unset: 146 passed in 2.26 s.
- `uv run ruff check` on the four files: all checks passed.
- `check_member_source` on both member files: no findings.
- Mutation run (`python3 coderB/mutate.py`, at nice 10): 91 mutants, 88 killed.
- `uv run python -m data.holdout status`: `unlocks_logged` 0 at start and end.
- Incident: the two stray empty files described above (`0` and `=`, 23:06:58 PDT), deleted at once.

## 6. Notes for the lead

None of these changes a trade.

1. **Reference values when one leg has no bars.** K8-L-04 says "A reference date on which a leg has no bars at all contributes no values". I read "a leg" through section 2 ("every defined r_t") and catalog lines 404-405, where r_t depends only on its two MCL bars. So a reference date with MCL bars but no 6C bars still counts. If you read "a leg" as "any leg", the code needs a per-date 6C presence flag. That only matters on an OILCAD date where the 6C file has no bars at all.
2. **Warm-up with two legs.** "The first bar received" is read as the earliest bar of either leg. That is the same as either leg's first bar whenever both research files start on the same trade date.
3. **wkndbtc Friday store.** It keeps only the latest qualifying 14:59 bar rather than a dict by CT date. The result is the same, because the lookup requires CT date d - 3.
4. **Refusal name on a signal-leg blackout.** Under the runner's rules (member_window), the open is refused as `engine_not_a_window_date`, because the date leaves the window before the blackout check. It is refused as `engine_roll_blackout` only when the date stays in the window. Both are pinned.
5. **Engine-closure test.** It uses a bar flatten flag on one 6C bar, because D9.7 does not fire on 6C (DCB_ONLY).
