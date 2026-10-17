# Stage E.23 TriggerCoder report: trigger extraction (trigger_hold/events*)

Worker: TriggerCoder-OpusXHigh. Times PDT (from `date`). Status: DONE 03:07 PDT (adapter, tests, four W_cf validations identical, eight events files written).

## 1. Scope after the lead's messages

- Lead message 1 (facts): FOMC 13:00 CT rows start 2013-03-20; auctions in ec_auc_2010_2019.json; pattern_search/backward.py
  derives S5/S6; reproduce only engine rules that change whether and when a member enters; K2's confirmation never ran.
- Lead message 2 (shortlist FINAL): K2-monthend-01 on ZF, ZN, ZB; E20H6-T1 on NQ. The three earlier examples (K2-fomcpost,
  K2-aucpost, K5-fomc) are not shortlisted; their table code stays as generic adapter code (tested on the frozen tables) but no
  event file is written for them. W_ext events 2011-06-01..2019-04-30; W_cf 2019-05-06..2024-02-29.

## 2. Files (new only)

| File | Role |
|---|---|
| trigger_hold/events.py | CLI (`extract`, `validate`), the capture (`entries_of`), the Stage E member run (`run_member`), window bounds, inputs record |
| trigger_hold/events_bars.py | bars: price-path root, `base_rules.store.load_product`, full engine columns of the same checked file, LegFrame, D9 coverage on the era's calendar |
| trigger_hold/events_members.py | trigger id -> frozen member (harness freeze verification), table injection, decision schedule |
| trigger_hold/events_tables.py | FOMC 13:00 CT, Treasury auction and month-end tables (2010-2019 rows), overlap check |
| trigger_hold/events_context.py | the W_ext context: pattern_search.backward's 2010-2019 swap plus two bindings |
| trigger_hold/events_h6.py | E20H6-T1 through the frozen h6_rod code |
| trigger_hold/events_validate.py | W_cf validation (Stage E harness run for K2; E.20's own records for H6) |
| tests/test_trigger_hold_events.py | synthetic-bar tests, table tests, recorded W_cf checks |
| reports/stage_e23_events/ | events files, meta files, validation files |

BookCoder's trigger_hold/types.py (TriggerEvent, events_record, schema stage_e23_events/1) is used unchanged.

## 3. Adapter design and fidelity to the harness

The adapter does not re-implement the engine. A Stage E member runs through the harness's own objects, in
`screening/stage_e_runner.screen_member`'s order, with only the bar source replaced:

| Harness step (screen_member / h6_rod.run) | Adapter | How it is reproduced |
|---|---|---|
| `harness_freeze.preflight(sha)` first | same call, v13 dd2bcc60... | identical |
| cluster freeze, `verify_cluster_code`, `resolve_member`, frozen factory | same calls (`events_members.resolve`) | identical; the member object is the factory's |
| `_legs_inputs` (frozen vehicle/cost tables per leg) | `events.legs_inputs`, line for line | identical |
| bars: `data.stage_e_bars.load_confirmation_leg` (step 2, S_X cut, price path) | `base_rules.store.load_product` (E.17 manifest, both eras, every refusal), then the window's era file is read again for the 16 `BAR_COLUMNS` after its sha256 is re-checked; timestamps, the trade-date booking and closure flags must equal load_product's row for row (else refused); cut to the window's trade dates | W_cf: the frame equals the harness's column for column (validation `frames_equal`) |
| price path (v13 N1: MGC -> GC) | `base_rules.constants.VEHICLE_OF` inverted (MNQ->NQ, M2K->RTY, MCL->CL, MGC->GC), checked by `data.stage_e_bars.check_price_path` | MNQ on NQ's bars, as h6_rod does |
| `member_window` (common trade dates less every leg's roll blackout) | the same function on the adapter's LegFrames | identical on W_cf (same window dates); the adapter's blackout set is the union of both eras' blackouts (so it holds extra pre-2019 dates on W_cf, none inside the window) |
| release calendar (`load_release_calendar`, coverage check) | W_cf: the same file; W_ext: `pattern_search.backward.backward_release_rules().calendar` (S11: base_rules' combined rows) | W_cf identical |
| D9 coverage (`member_coverage`, 2019-on calendar) | `events_bars.leg_coverage_on`: the same arithmetic with the era's calendar passed in | recorded as counts; not used to drop a member (question Q3) |
| `StageERules(...)` + `run_engine` | same objects, same arguments | identical: every structural refusal, D9 guards, flatten/no-new (sessions + bar flags), roll blackout, instrument guard (`engine_leg_missing_bar`, splice invariant), fill guard, CPI window, price limits, account gate |
| entries | `entries_of`: opening strategy fills only | d0 = trade date of the decision bar, tau = decision instant (bar open + 60 s), side |

W_ext context (`events_context.hist_context`): the program's own 2010-2019 swap, `pattern_search.backward.backward_context(
backward_tables())` (Stage E.20 B1; S1 hist calendars for `data.group_session.load_group_calendar`, S2 rules.sessions holidays
and late opens, S3 Rule H-1 Topstep rows from the hist equity calendar and the 30-minute early-close lead for 2010-2018, S6
K2 monthend EVENT_DATES, and the other members' tables), plus two bindings restored on exit: the functools cache
`screening.stage_e_rules._calendar` cleared (not in backward's CACHE_MODULES), and `rules.price_limits.HARD_LIMIT_PRODUCTS`
bound to the empty set (the limit table starts 2019-05-01 and raises `LimitPending` before it).

Engine rules NOT reproduced on W_ext, and their effect on events:

| Rule | Why | Effect on the four triggers |
|---|---|---|
| D9.7 price-limit proximity (entry refusal, forced exit, locked fill) | no CME limit table before 2019-05-01 (`rules.price_limits.TABLE_WINDOW`); base_rules.limits' reading RR-4 ("a date before the table: no lock can be shown") carried to the entry check | rates are DCB-only (never hard-limit): none for K2-monthend. MNQ: an H6 entry at C-30 on a day NQ trades inside the stop zone of a 7%/13%/20% band would have been refused; not computed (it needs a limit table and prices); expected 0 to a few dates in 2011-2019 |
| D9.12 CPI window | no CPI rows before 2019-05-01 in the combined release rows | binds only full-size NQ/RTY/YM/GC/SI/HG or micros above 3 contracts: none (K2 rates; H6 trades 1 MNQ) |
| D8 event-window cost, D9.5a fill guard | release rows before 2019-05 are FOMC, NGS, WPSR and Treasury auctions only | costs never change an entry; the guard only delays a fill inside [release, release + 2 min): monthend fills at 07:21 CT, H6 at C-30 (14:30 CT); no 2010-2019 release type in the rows sits there except FOMC at 13:00 CT; no effect on whether an entry happens |
| Topstep's published schedule | none before 2024; E.5's Rule H-1 rows are derived for 2019-2023; S3 derives them for 2010-2018 from the hist equity calendar with the 30-minute lead | as the harness treats 2019-2023 (lead message: H6 shortened days refused at F = C-30) |

## 4. Release and calendar tables (brief item 3)

Built only from the program's files, never from the web. Each filter reproduces the frozen member table exactly when applied
to the frozen calendar (tests), and the sourced 2010-2019 files agree with the frozen calendar on their overlap
(`events_tables.overlap_check`: FOMC 2019-05-01..2019-05-30 1 = 1 row; auctions 2019-05-01..2019-06-27 7 = 7 rows).

| Table | Member(s) | Rule (frozen definition) | 2010-2019 source | W_ext result |
|---|---|---|---|---|
| month-end N-1, N | K2-monthend-01 (shortlisted) | gen_k2_month_end.py month_end_rows(): N = last trade date of the calendar month, N-1 = the trade date before it, on the rates calendar; early-halt days stay listed (the member drops them, C4) | data/calendars/hist2010/rates.json (via base_rules.calendars.load_hist) | 95 months, 190 dates (2011-06-29 .. 2019-04-30); equal to pattern_search.backward S6 on 2011-06-01..2019-04-30 (checked in every W_ext run and in a test); the rule reproduces the frozen _month_end.MONTH_END on the frozen calendar (test) |
| FOMC statement dates | K2-fomcpost-01, K5-fomc-01 (not shortlisted) | FOMC rows whose instant is 13:00 CT on the row's date (E.3-L-15) | reports/stage_e14_cal_releases.json | 2011-06..2019-04: 49 kept from 2013-03-20; excluded (statement not at 13:00 CT) 14 at 13:15 CT, 4 at 11:30, 3 at 11:35, 1 at 11:20 (counts over all E.14 rows from 2010-06) |
| Treasury auctions | K2-aucpre-01, K2-aucpost-01 (not shortlisted) | every TREASURY_AUCTION row of tenor 2Y/5Y/10Y/30Y (id suffix), T_a = instant in CT | reports/stage_e16_calendars/ec_auc_2010_2019.json (frozen row format) | 440 rows to 2019-04-30 (10Y: T_a 10:30 or 12:00 CT); 3Y and 7Y rows excluded by tenor |

Note on pattern_search.backward S5 (not used: aucpost is not shortlisted): S5 binds strategy.members.k2._releases.
TREASURY_AUCTIONS, but K2 aucpre/aucpost read the name bound in strategy.members.k2._event_common at import
(auction_schedule), so S5 does not reach those two members' own code (it may still reach a reader that looks the name up
on _releases, such as an ML signal module); trigger_hold.events_members binds _event_common's name instead. Worth a look by
whoever owns E.20 B1.

## 5. W_cf validation (brief item 4): every difference is zero

Files: reports/stage_e23_events/validation/<trigger>__cf.json (written once; entries only, no price, no P&L).

| Trigger | Harness side | Adapter events | Harness events | Identical (d0, tau, side) | Frames |
|---|---|---|---|---|---|
| K2-monthend-01 ZF | Stage E harness run by me: runner `_legs_inputs`, `data.stage_e_bars.load_confirmation_leg` from 2019-05-06 (no start rule lists ZF; the E.17 manifest's sha256), `member_window`, `member_coverage`, runner `_run_member`; P&L dropped unread | 79 | 79 | yes, 0 differences | all 16 columns, rows (1.6M) and trade dates equal |
| K2-monthend-01 ZN | same | 77 | 77 | yes, 0 differences | equal |
| K2-monthend-01 ZB | same | 79 | 79 | yes, 0 differences | equal |
| E20H6-T1 NQ | E.20's own records, reports/stage_e20_H6_result.json: overlap.T1 (2019-05-06..2020-05-29, 254 trades) and tests.T1 (2020-06-01..2024-02-29, 893 trades); only trade_date, side, entry_fill_utc read | 1147 | 1147 | yes, 0 differences; tau equals E.20's entry fill instant on all 1147 | (E.20 frame not rebuilt) |

The only frame attribute that differs is the roll-blackout set (`blackout_equal` false): the adapter's set is the union of
both eras' L-8 blackouts, so it also holds ext2010 dates before 2019-05; the window dates (1188 ZN, 1191 ZF/ZB) are equal.
The H6 adapter is one continuous 2019-05-06..2024-02-29 run; E.20 ran the overlap and the verdict windows separately (a fresh
account and one lead-in date at 2020-06-01); the entries still match one for one.

W_cf counts (adapter = harness):
- K2-monthend ZF / ZN / ZB: 116 table dates in the window each; entered 79 / 77 / 79; outside the member window (roll
  blackout) 37 / 39 / 37 (the engine refused 32 / 33 / 31 intents with engine_not_a_window_date; the rest had no intent);
  no early-halt or missing 07:20 bar among the table dates; D9 coverage 0.993 / 0.997 / 0.985.
- E20H6-T1: 1248 equity trade dates; 1228 scheduled (19 instrument_change, 1 missing_prior_bar excluded by h6_rod.signal);
  1147 entered; 43 shortened dates refused by engine_flatten_window (F = C-30 at the decision); 38 refused by
  engine_roll_blackout.

## 6. Tests (tests/test_trigger_hold_events.py; my file only, `pytest -q`)

35 passed (03:07; the recorded W_cf checks and the no-exit-side check over every written file included). No store is read
by a test.
- synthetic flat bars (06:00-15:30 CT, 2023-06-27..30) through the frozen K2-monthend-01 ZN member, the adapter's
  `run_member` and the real engine: entries exactly on N-1 and N at tau = 07:21 CT (the 07:20 bar's close), side +1;
- a halted day (early_halt_ct on N): no entry, counted table_date:early_halt;
- a missing decision bar (07:20 on N-1 dropped): no entry, no later entry, counted table_date:decision_bar_missing;
- a roll-blackout date: refused by the engine (engine_not_a_window_date), counted;
- the events record holds only d0, tau_ns, side and integer counts;
- table filters: FOMC 12:30 / 14:15 / 14:00 ET rows (only 14:00 ET = 13:00 CT kept, the others counted by CT time); the
  auction tenor filter; the filters reproduce the frozen K2/K5 FOMC and auction tables; the month-end rule reproduces the
  frozen _month_end.MONTH_END on the frozen rates calendar; the hist month-end table equals backward S6 (190 dates) and
  the swap is restored on exit; the sourced files agree with the frozen calendar on the overlap; hist FOMC starts 2013-03-20;
- a table member without a declared 2010-2019 table (K2-predrift-01) is refused on W_ext; trigger id spellings;
- recorded W_cf comparisons: same (d0, side) and the same count for all four triggers.

## 7. The eight events files (lead: cleared after tests and W_cf validation)

reports/stage_e23_events/<trigger>__<window>.json (schema stage_e23_events/1, parsed by trigger_hold.types.load_events) with a
sidecar <trigger>__<window>.meta.json (window bounds, coverage ratio, bars provenance, rules not reproduced). Events only: d0,
tau_ns, side. Inputs recorded per file: harness freeze sha256, run manifest, cluster freeze (K2) or every h6_rod file and the
H6 prereg/freeze (H6), member module, both era stores checked by load_product and the era file read, release calendar
(W_cf) or pattern_search.backward's pinned sources and module (W_ext), calendars, table sources, and every trigger_hold
file of the extraction.

| File | Events | First | Last | Sides | Window trade dates | Key counts |
|---|---|---|---|---|---|---|
| K2-monthend-01_ZF__cf | 79 | 2019-06-27 | 2024-02-29 | all +1 | 1191 | 116 table dates: 79 entered, 37 roll blackout |
| K2-monthend-01_ZN__cf | 77 | 2019-06-27 | 2024-01-31 | all +1 | 1188 | 116: 77 entered, 39 roll blackout |
| K2-monthend-01_ZB__cf | 79 | 2019-06-27 | 2024-02-29 | all +1 | 1191 | 116: 79 entered, 37 roll blackout |
| E20H6-T1_NQ__cf | 1147 | 2019-05-07 | 2024-02-29 | 630 buy / 517 sell | 1248 | 1228 scheduled; 43 shortened refused (engine_flatten_window); 38 roll blackout |
| K2-monthend-01_ZF__ext | 137 | 2011-06-29 | 2019-04-30 | all +1 | 1935 | 190 table dates: 137 entered, 51 roll blackout, 1 early halt, 1 no bars (2013-11-28) |
| K2-monthend-01_ZN__ext | 143 | 2011-06-29 | 2019-04-30 | all +1 | 1939 | 190: 143 entered, 45 roll blackout, 1 early halt, 1 no bars |
| K2-monthend-01_ZB__ext | 142 | 2011-06-29 | 2019-04-30 | all +1 | 1939 | 190: 142 entered, 46 roll blackout, 1 early halt, 1 no bars |
| E20H6-T1_NQ__ext | 1860 | 2011-06-01 | 2019-04-30 | 1039 buy / 821 sell | 2043 | 1981 scheduled (excluded: 31 instrument_change, 15 missing_signal_bar, 12 missing_prior_bar, 4 zero_signal); 59 shortened refused at F = C-30; 62 roll blackout |

D9 coverage (recorded, not used to drop): ZF 0.993 / 0.982, ZN 0.997 / 0.995, ZB 0.985 / 0.985 (W_cf / W_ext); all >= 0.95.
Stores read on W_ext: ZN ext2010 (2010-06-07..), ZF and ZB ext2010h (2010-07-01..), NQ ext2010 (2010-06-07..). Peak RSS per
run 1.2-1.7 GB, 33-48 s each, nice 10, one at a time.

## 8. Incident (reported, fixed): exit-side counts were written in the first pass

The first pass of the eight files (02:49-02:55) and the four validation files carried the engine's own counters
(`EngineResult.counters`) and all order cancels. Those include exit-side facts from the intraday path after the decision bar:
forced flattens and MLL liquidations, and on W_ext both appeared (single-digit counts) for some triggers. They are not prices or
P&L, but the brief says nothing after the decision bar is written, and on W_ext that intraday path had never been read. Fix:
`entries_of` now counts only entry-side facts (entry intents accepted / refused by reason, and accepted entry orders cancelled
before filling, matched by decision instant); engine counters and exit orders are never counted; a test checks every
written file. All first-pass files (events, metas, validations, my smoke file) were deleted, the counter text was scrubbed from
my run logs, and everything was regenerated from the fixed code (section 9). The event lists themselves did not depend on the
fix. The lead should know that those exit-side counts reached my context (not the lead's) and lived on disk for about five
minutes (02:46-02:58); I passed them to no one, and I cannot tell whether another worker opened those files then.

## 9. Final files and sha256 (regenerated 02:58-03:07 with the fixed capture)

| sha256 | File (reports/stage_e23_events/) | Events |
|---|---|---|
| 05eb3fb49b5ca223e67fdfaba043905c8db4033e32c297ea9ffed2d00d688a2a | E20H6-T1_NQ__cf.json | 1147 |
| c51d3398ae2e8e5fb82db1209be46f2215c3f2c0fe664bb4d24084bfad32d41a | E20H6-T1_NQ__ext.json | 1860 |
| bd6b3c43e226ba575cbfdcb96419518bfa1b27c5442d05427b721fa6b75ccae9 | K2-monthend-01_ZB__cf.json | 79 |
| 6cfccf6ff10ffc6b346cd77a09218b443ab8711af95487deae0f614f836a4138 | K2-monthend-01_ZB__ext.json | 142 |
| f3d952ad74ce66c1698cd3e877b870494db893c0b86dbc8556fad04f6da769f5 | K2-monthend-01_ZF__cf.json | 79 |
| 7765aa669421353d7cbc5065299288f575f60b427c820d59befd28fbb9ff1b83 | K2-monthend-01_ZF__ext.json | 137 |
| d4d99504ed06d7d9785cb443f7fb6c1b7f3af2d4cedb7a413fcbe288c7c47fbe | K2-monthend-01_ZN__cf.json | 77 |
| 643b83b2694871cf5afb29240123e1e452bfc33d2a8941d837c856bb9cf98ae6 | K2-monthend-01_ZN__ext.json | 143 |
| 1d652796cda9f1f7838d0d36a4d61a8610b6a8672a0ed904c9f90218891f531f | validation/E20H6-T1_NQ__cf.json | - |
| 8c118e81d6d487328b06572436b396261833f3e44dca71834f1e317bae74e09e | validation/K2-monthend-01_ZB__cf.json | - |
| cb87c57921193f38ccb06efdee43b796587b90c526b5c4c863793c210528032a | validation/K2-monthend-01_ZF__cf.json | - |
| aab242d466fed59fd4a2e2d4a3d62861b9b6b9b6935b9d0022f807a11c9c2c3b | validation/K2-monthend-01_ZN__cf.json | - |

The .meta.json sidecars are not listed (no events; regenerate-able). Event counts, first/last dates and sides are unchanged
from the first pass. Logs: reports/stage_e23_briefs/tmp_triggercoder/{validate,extract}.log (first pass: *_run1.log, counter
text scrubbed). Re-run: `python -m trigger_hold.events extract --trigger "<id>" --window ext|cf --out <path>` (refuses an
existing output) or the two scripts run_validate.sh / run_extract.sh in the same folder.

## 10. Questions for the lead (each taken at the most conservative reading; nothing waits on them)

1. Trigger ids. The files carry trigger_id = the freeze label with a space ("K2-monthend-01 ZN") and "E20H6-T1 NQ"; file
   names use an underscore, as the lead asked. If the registration config names them otherwise, the files must be
   regenerated (the id is inside each file), about 6 minutes for all eight.
2. Event = an opening strategy fill of the engine (an accepted entry intent that filled), not the bare intent. On these
   four triggers every accepted entry intent filled (no entry order was cancelled), so the two readings give the same list.
3. D9 coverage: the harness drops a member below 0.95 before screening; the adapter records coverage and drops nothing.
   All four are 0.982-0.997 on both windows, so the point is moot here.
4. D9.7 on W_ext for H6 (MNQ): not applied (no limit table before 2019-05-01; base_rules.limits' reading). On W_cf the
   engine refused no H6 entry for D9.7 in 2019-05..2024-02 (March 2020 included), so the effect on W_ext is likely zero;
   not proven.
5. H6 lead-in on W_ext: h6_rod.clock.lead_in_dates clamps the lead-in at 2019-05-06 (the step 2 store's first date). On
   W_ext I applied the same rule (ENGINE_LEAD_IN_DATES = 1 previous equity trade date) without that clamp, so 2011-06-01 has
   its prior-close bar (2011-05-31). With the clamp, 2011-06-01 would be missing_prior_bar: one event fewer, before the book's
   2011-07-27 start.
6. W_ext month-end table dates dropped: 2013-11-28 (Thanksgiving) is a trade date of the hist rates calendar (N-1 of Nov 2013)
   but no ext2010/ext2010h bar is booked to it in ZF, ZN or ZB (counted table_date:not_a_trade_date). One more table date per
   root had an early-halt flag on its 07:20 bar (member rule C4). Many other early-halt month-ends (Aug/Nov/May) fall on roll
   blackouts first and are counted there.
7. The hist store's early_halt_ct is set per bar by CT calendar date (e.g. the evening bars of a holiday booked to the next
   trade date carry the holiday's halt: 2016-05-31, 2017-05-30). The member reads only its 07:20 bar's flag, so the event
   list follows the store's flag exactly as the harness would; I did not check that the step 2 builder uses the same
   convention (the W_cf comparison is identical either way).
8. Month-end events are all BUY by the member's rule (side +1); H6 sides follow sign(r_ROD). Direction m per trigger is the
   freeze's choice, not mine.

## 11. Not done / not verified

- No event file for the three earlier examples (K2-fomcpost, K2-aucpost, K5-fomc): dropped by the lead's shortlist. Their
  table code is tested on the frozen tables only, never run on W_ext or W_cf bars.
- The adapter supports other Stage E members generically, but a member that reads another 2019-on table (K1 equity full
  sessions, K4/K5 calendars, K2 predrift) is refused on W_ext until its injection is declared; untested on real bars.
- No independent (Fable) review of this code yet; the W_cf identity checks are the only cross-check.
- Holdout status, the full suite and REGISTRATION.md are the lead's checks; I ran only my own test file and changed no
  existing file.
