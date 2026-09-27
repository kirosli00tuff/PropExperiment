# Stage E.4b member specifications, cluster K5 metals (Part 2, Task 1)

Written by the Stage E.4 lead (Opus 5.5, xhigh), 2026-09-27 05:06-05:25 PDT, before any K5 member code exists and
before any K5 bar has been read by this session. Same method as reports/stage_e4_member_specs.md (K4): each frozen
entry restated as the code must implement it, with line references; every reading the lead took is in section 10;
no rule is changed. Where K5's text is the same as K2's or K4's, the earlier reading is adopted and cited (E.3-L-nn,
K4-L-nn).

Sources and their state:
- C = reports/stage_e0_catalog_K5.md, frozen by reports/stage_e1_freeze.json. Header and C1-C14 lines 75-281. E.1
  edits to K5 (reports/stage_e1_changes.md K5-00..K5-34) remove platinum (U2), the ML member (U6) and set
  K5-preauc-01's count (U9); no active member's rule changed. K5-ml-01 is excluded (U6); platinum is OUT (U2).
- D = docs/STAGE_E_DESIGN.md (frozen): D6 port texts lines 364-366, "4 ticks of P" lines 368-374, the gold row
  (O 07:20, C 12:30, F 15:08) and the copper row (O 07:10, C 12:00, F 15:08), lines 396 and 398; D9.5a lines 516-522;
  D9.7 lines 531-550; D9.11, D9.12.
- Vehicles (reports/stage_e2a_vehicles.md lines 35-37): gold -> MGC, chosen, q_c = 1; copper -> MHG, chosen, q_c = 2;
  silver: no candidate, not traded. Operative eps (reports/stage_e2a_epsilon.md lines 19-20): MGC 85 ticks, MHG 34
  ticks.
- Frozen per-root values (checked 05:12): day_session_ct MGC (07:20, 12:30), MHG (07:10, 12:00); vendor_tick MGC
  0.10, MHG 0.0005; product group metals. F = 15:08 CT on a regular day, earlier on early-halt days.
- Release calendar reports/stage_e2b_release_calendar.json (frozen, sha256 839f2437...): FOMC rows (EC-FOMC, 13:00 CT);
  it holds no LBMA auction row. E.3's FOMC table: strategy/members/k2/_releases.py FOMC_STATEMENT_DATES.
- The K5 release check: reports/stage_e4b_release_check.md and .json (Task 1b). Section 11 applies it.
- Source-window labels (reports/stage_e2a_source_window_amendment.md lines 62-66): every K5 member keeps
  "source-overlap" (K5-fomc-01 and K5-ovr-01 by R-04, C lines 642 and 715).
- EC-CAL = the D10 metals calendar (data/calendars/metals.py through data.group_session.load_group_calendar("metals")).
  Research window: 315 trade dates; early halts 2025-05-26, 06-19, 07-04, 09-01, 11-27, 11-28, 12-24, 2026-01-19,
  02-16, 05-25, 06-19; weekday non-trade dates 2025-04-18, 12-25, 2026-01-01, 04-03 (checked 05:12).

What the member does NOT implement (the engine and runner do): the window's trade dates and roll-blackout dates (opens
refused by name, bars still delivered); UR-1; F and the forced flatten; D8 costs and the event-window cost; D9.5a's
fill guard (it reads the frozen release calendar, so FOMC, CPI, NFP and G.17 minutes, not auction starts: K5-L-04);
D9.3a/b; the skip of an entry whose fill would come less than 2 minutes before F; D9.7; D9.5 and D9.11's caps (MGC 1
and MHG 2 are within them); D9.12's CPI window (MGC and MHG may open at most 3 contracts inside it; q_c is 1 and 2).

---

## 0. Common to all seven members

S0.1 Legs. One leg each, the traded exposure's own vehicle, `LegSpec(root, True)`: MGC (gold) or MHG (copper). No
signal legs. SI, SIL, PL and GC/HG are never read or traded.

S0.2 Declarations. 11 trials. Label `"<member id> <ROOT>"`. Modules under strategy/members/k5/; factories
`make_mgc`, `make_mhg` (only the exposures the member trades). Ordinals: catalog order, then gold before copper (the
catalog's exposure order):

| Member | Module | MGC (gold) | MHG (copper) |
|---|---|---|---|
| K5-cp1-01 | strategy.members.k5.cp1 | 1 | 2 |
| K5-cp2-01 | strategy.members.k5.cp2 | 3 | 4 |
| K5-cp3-01 | strategy.members.k5.cp3 | 5 | 6 |
| K5-preauc-01 | strategy.members.k5.preauc | 7 | - |
| K5-pmfix-01 | strategy.members.k5.pmfix | 8 | - |
| K5-fomc-01 | strategy.members.k5.fomc | 9 | - |
| K5-ovr-01 | strategy.members.k5.ovr | 10 | 11 |

S0.3 Size. `q_c` from `load_frozen_tables().vehicles[root].q_c` (MGC 1, MHG 2), never a literal (C6 lines 121-132).
Every exit closes the whole position. No member sizes by signal.

S0.4 Clock. As K4 S0.4: America/Chicago; "the bar at hh:mm" is on CT date d (C1 lines 92-95; E.3-L-03), except CP1's
17:00 CT Globex-open bar of d-1 (C3 lines 98-104; E.3-L-05). O and C from `day_session_ct[root]`. London times convert
by C10 (lines 195-230): T_CT(d, L) = the America/Chicago wall time of the instant whose Europe/London wall time is L on
d, with zoneinfo; literal tables carry the converted instants (S0.11).

S0.5 Orders. Market intents only (C2 lines 96-97).

S0.6 Named entry bar (E.3-L-04), S0.7 Exits (C4 lines 105-114, "If an exit's named bar is missing, the exit is sent on
the first later bar"; E.3-L-22; an engine-closed position is not re-entered that trade date, or at that decision time
for ovr), S0.8 Early halts (C4; E.3-L-11: the entry decision bar's early_halt_ct; the ports follow D6), S0.9 Instrument
guard (C4; E.3-L-12/13: the bars read at or before the entry decision carry the entry decision bar's instrument_id;
ovr per computation, K4-L-14), S0.10 integer vendor ticks (E.3-L-19): all exactly as K4's S0.6-S0.10.

S0.11 Event and calendar data (E.3-L-01), literal tables in the cluster package, generated from their sources and pinned
by tests:
- strategy/members/k5/_calendar.py (MemberCoder-A): METALS_FULL_SESSIONS, every EC-CAL metals trade date with no early
  halt, over the calendar's coverage (K4-L-13), for ovr's reference dates.
- strategy/members/k5/_releases.py (MemberCoder-B): GOLD_AM_AUCTIONS and GOLD_PM_AUCTIONS, tuples of (date, T_CT
  "HH:MM") for every scheduled gold AM and PM auction day 2019-05-01..2026-06-19 per section 11 (weekdays not
  England-and-Wales bank holidays, less days announced in advance with no such auction); FOMC_STATEMENT_DATES (the
  frozen calendar's FOMC rows at 13:00 CT, equal to E.3's table); the sha256 of each source file.

S0.12 trading_windows (E.3-L-17; offset 0 unless stated; measured on every research date):

| Member | MGC intervals [start, end) CT | MHG intervals |
|---|---|---|
| CP1 | (17:00, 17:01) on day -1; (07:49, 07:50); (11:59, 12:30) | (17:00, 17:01) on day -1; (07:39, 07:40); (11:29, 12:00) |
| CP2 | (07:20, 15:08) | (07:10, 15:08) |
| CP3 | (07:20, 12:30) | (07:10, 12:00) |
| preauc | (03:59, 04:30); (04:59, 05:30) (the normal and 5-hour-week slots) | - |
| pmfix | (08:59, 09:13); (09:59, 10:13) | - |
| fomc | (12:59, 13:16) | - |
| ovr | (07:20, 13:20) | (07:10, 12:10) |

S0.13 Topstep (C lines 325-337 and each entry): flat by F; market; at most 1 entry a day (ovr at most 5 on gold, 4 on
copper); holds of at least 10 minutes by rule (pmfix and fomc exactly 10: the D9 mean-hold floor is met at its boundary,
C lines 614 and 687; a shorter realized mean would be labelled by the engine, not dropped); no stops; MGC is starred
(F1: volatility cap 30, CPI-window cap 3; q_c 1); MHG unstarred but capped at 2 (q_c 2); <= 1 lot-equivalent (MGC 0.1,
MHG 0.2); D9.7 per the engine (C13).

S0.14 C10 of K4 has no K5 twin: K5's percent return (ovr) requires its open > 0 as K4-ovr-01 does (the same rule text,
F-7). No other K5 member computes a percent return (C lines 157-159).

---

## 1. K5-cp1-01 (CP1). C lines 284-339; D line 364

| Field | MGC (gold) | MHG (copper) | Reference |
|---|---|---|---|
| Signal | sign(close of 07:49 - open of the 17:00 CT bar of d-1), ticks | sign(close of 07:39 - open of the 17:00 bar of d-1) | C 303-311; D 364; E.3-L-05, L-06 |
| Zero signal / guard | no trade; both signal bars present with one instrument_id | same | D 364 |
| Entry | intent on 11:59, fill 12:00 | intent on 11:29, fill 11:30 | C 303-311 |
| Exit | first bar at or after 12:28, fill 12:29 | first bar at or after 11:58, fill 11:59 | C 303-311; S0.7 |
| Hold | 29 minutes | 29 minutes | C 312 |
| Parameters | O+29, C-31, C-2 from O/C; no grid | same | C 319 |
| Trials | 2 | | C 338 |

## 2. K5-cp2-01 (CP2). C lines 340-392; D line 365

| Field | MGC | MHG | Reference |
|---|---|---|---|
| Opening range | present bars in [07:20, 07:35) | [07:10, 07:25) | C 355-366; E.3-L-08 |
| Buffer | 4 x vendor_tick = 0.40 (= 4 ticks of MGC, gold's most active contract) | 4 x vendor_tick = 0.0020 (= 4 ticks of HG) | C 355-366; D 368-374; K5-L-07 |
| Eligible bars | opening in [07:35, 12:30) | [07:25, 12:00) | C 355-366 |
| Entry | first eligible close >= OR_high + buffer buys, <= OR_low - buffer sells; one per trade date | same | C 367 |
| Exit | 75 present bars after the entry decision bar (MES count); no C-2 exit; F backstop | same | C 368-369; E.3-L-07 |
| Trials | 2 | | C 391 |

## 3. K5-cp3-01 (CP3). C lines 393-442; D line 366

| Field | MGC | MHG | Reference |
|---|---|---|---|
| Daily bar | [07:20, 12:30): O_d open of 07:20, H/L over present bars, C_d close of 12:29 | [07:10, 12:00): C_d close of 11:59 | C 411-420 |
| Complete day, d-1, warm-up, guard, CLV cuts, early-halt day d | as K4 section 3 (Family H; E.3-L-09, L-11) | same | C 400-420 |
| Entry | intent on the 07:20 bar, fill 07:21 | intent on the 07:10 bar, fill 07:11 | C 411-420 |
| Exit | first bar at or after 12:28 (fill 12:29) | first bar at or after 11:58 (fill 11:59) | E.3-L-10 |
| Trials | 2 | | C 441 |

## 4. K5-preauc-01 (short into the gold AM auction). C lines 443-537

| Field | Rule | Reference |
|---|---|---|
| Exposure | gold MGC, q_c 1 (silver has no vehicle; platinum removed by the lead's 01:47 ruling and U2) | C 445-450, 536 |
| Days | each trade date d that is a scheduled gold AM auction day (GOLD_AM_AUCTIONS, section 11) with no early halt (C4) | C 484; C9 lines 163-172; K5-L-03 |
| T | T_CT(d, 10:30 London): 04:30 CT, or 05:30 CT in 5-hour weeks (the table's value) | C 485-487; C10 |
| Entry | SELL q_c, market intent on the bar at T-31 (normally 03:59), fill at T-30; no signal; if the T-31 bar is missing, no trade | C 488-491; S0.6 |
| Exit | market intent on the bar at T-2 (normally 04:28), fill at T-1; if missing, the first later present bar | C 492-493; S0.7 |
| Hold | 29 minutes | C 494 |
| Guard | the only bar read before the entry is the T-31 bar: satisfied by construction | S0.9 |
| Parameters | 30-minute pre-auction window, exit one minute before the start; no grid | C 503-513 |
| Trials | 1 | C 536; K5-L-11 |

## 5. K5-pmfix-01 (gold PM auction continuation). C lines 538-639

| Field | Rule | Reference |
|---|---|---|
| Exposure | gold MGC, q_c 1 | C 540 |
| Days | each trade date d that is a scheduled gold PM auction day (GOLD_PM_AUCTIONS, section 11) with no early halt | C 589; K5-L-03 |
| T_P | T_CT(d, 15:00 London): 09:00 CT, or 10:00 CT in 5-hour weeks | C 590; C10 |
| Signal | s = ticks(close of the bar at T_P+1) - ticks(close of the bar at T_P-1); both present with one instrument_id; s = 0: no trade | C 591-593 |
| Entry | s > 0 BUY, s < 0 SELL, market intent on the bar at T_P+1, fill at T_P+2 | C 594-595 |
| Exit | market intent on the bar at T_P+11, fill at T_P+12; if missing, first later present bar | C 596; S0.7 |
| Hold | 10 minutes | C 597 |
| Guard | the T_P-1 and T_P+1 bars (the entry decision bar is T_P+1) carry one instrument_id | S0.9 |
| Parameters | signal span 2 minutes, hold 10 minutes, no size threshold; no grid | C 606-617 |
| Trials | 1 | C 638 |

## 6. K5-fomc-01 (gold, post-FOMC continuation). C lines 640-712

| Field | Rule | Reference |
|---|---|---|
| Exposure | gold MGC, q_c 1 | C 644 |
| Days | each trade date d in FOMC_STATEMENT_DATES (statement at 13:00 CT) with no early halt | C 672; C9 lines 175-182; E.3-L-15 |
| Signal | s = ticks(close of 13:04) - ticks(close of 12:59); both present with one instrument_id; s = 0: no trade | C 673-674 |
| Entry | s > 0 BUY, s < 0 SELL, market intent on the bar at 13:04, fill 13:05 | C 675-676 |
| Exit | market intent on the bar at 13:14, fill 13:15; if missing, first later present bar | C 677; S0.7 |
| Hold | 10 minutes | C 678 |
| Guard | the 12:59 and 13:04 bars carry one instrument_id | S0.9 |
| Trials | 1 | C 711 |

## 7. K5-ovr-01 (hourly overreaction reversal). C lines 713-804

| Field | MGC | MHG | Reference |
|---|---|---|---|
| Decision times | t = O + 60k while t <= C: 08:20, 09:20, 10:20, 11:20, 12:20 | 08:10, 09:10, 10:10, 11:10 | C 745-747 |
| Signal | r(t) = (close of t-1 - open of t-60) / open of t-60, float from integer ticks, open > 0, both bars one instrument_id | same | C 748-749; K4-L-05 |
| Reference dates | the 20 most recent METALS_FULL_SESSIONS dates before d (EC-CAL; K5-L-05) | same | C 751-752; F-7 |
| Values required | at least 80 of 100 | at least 64 of 80 | C 753 |
| Cuts | numpy.percentile(values, [10, 90], method="linear") | same | C 755 |
| Warm-up | as K4-L-09 (the first 20 eligible dates of the window) | same | C 756-757 |
| Entry | r <= P10 BUY; r >= P90 SELL; P10 = P90 = r no trade (K4-L-10); intent on the bar at t-1, fill at t; only flat with no pending order | same | C 758-760 |
| Exit | intent on the bar at t+58, fill at t+59; missing: first later present bar | same | C 761-762 |
| Early halts | no trade on an early-halt date | same | S0.8 |
| Trials | 2 | | C 803 |
| F-7 | the same rule text as K4-ovr-01 with K5's clocks; the auditor confirms the modules differ only in the clock, the calendar table and the value floor (80% of the possible values: 80 on gold as K4's 80; 64 on copper) | | E.1 F-7 |

## 8. (unused)

## 9. Trial count

11 declarations (S0.2): gold 7 (cp1, cp2, cp3, preauc, pmfix, fomc, ovr), copper 4 (cp1, cp2, cp3, ovr). Program N
after K5: 114 + 11 = 125 if all 11 are screened (the lead takes the count from the freeze declarations).

## 10. Lead readings

Adopted: E.3-L-01, L-03..L-13, L-15, L-17, L-19, L-22 (as K4); K4-L-05 (percent returns from integer ticks),
K4-L-09 (ovr warm-up), K4-L-10 (ovr tie), K4-L-13 (the calendar table spans the calendar's coverage), K4-L-14 (ovr's
guard per computation).

New readings for K5:
- **K5-L-01 Tables span 2019-05..2026-06** (as K4-L-01): the auction and FOMC tables carry every row the sources give
  for 2019-05-01..2026-06-19, so the frozen code serves the confirmation window; Task 1b checks the research window
  first and extends as far as its sources reach, and anything unchecked is listed in section 11.
- **K5-L-02 London instants by zoneinfo.** T_CT is computed with Europe/London and America/Chicago zoneinfo (C10's
  rule), and the table carries the converted "HH:MM"; C10's 5-hour-week table is the check.
- **K5-L-03 A scheduled auction day is per auction.** A weekday that is an England-and-Wales bank holiday has no
  auction (C9). A day on which IBA or LBMA announced in advance that one auction (for example the PM on 24 or 31
  December) would not be held is not a scheduled day for that auction only: pmfix does not trade it; preauc trades it
  if its AM auction was scheduled. A day announced in advance with no auction is not a scheduled day (C9 line 171).
  No day is dropped after the fact because an auction started late (C9 lines 168-169).
- **K5-L-04 Catalog section 7 item 1 (auction starts and the D9.5a guard) is settled by the frozen harness.** The
  prompt: "use whatever the frozen D9 and D8 text and the E.2b release calendar already do". The frozen release
  calendar has no LBMA row, so neither D8's event-window cost nor D9.5a's guard applies at an auction start; C11's
  "D8 cost only, pending the lead" row is not in force. No member fill lands in [T, T + 2) of an auction anyway (C
  line 244); only port fills could, and they are not deferred.
- **K5-L-05 ovr's "eligible trade dates (C4)" are EC-CAL full sessions.** The K5 entry says "the 20 most recent earlier
  eligible trade dates (C4) of the exposure", K4-ovr-01 says "the 20 most recent earlier trade dates that are full
  sessions in EC-CAL", and E.1's F-7 records that the two carry one rule text. C4's date-level exclusions that a member
  can apply are the early halt and close (EC-CAL); its roll-blackout clause is met by the runner, not the member (E.3
  specs, "What the member does NOT implement"), and its missing-bar clause is per computation, which the entry's own
  "At least 80% of the possible values must exist" handles. So the reference dates are the 20 most recent
  METALS_FULL_SESSIONS dates, roll-blackout dates included, exactly as K4-L-08. The stricter reading (drop roll-blackout
  dates) would need a roll calendar the member cannot read and would break F-7.
- **K5-L-06 The value floor is 80% of the possible values** (C line 753): 80 of 100 on gold, 64 of 80 on copper.
- **K5-L-07 CP2's buffer as 4 x vendor_tick** (MGC 0.40, MHG 0.0020), equal to 4 ticks of the exposure's most active
  contract (MGC for gold; HG for copper, the same 0.0005 tick; C7 lines 145-148). A test pins both literals.
- **K5-L-08 preauc's and pmfix's coverage minutes include both clock slots** (normal and 5-hour weeks), measured on
  every research date (E.3-L-17), as ngpre's two slots in K4.
- **K5-L-09 pmfix's and fomc's 10-minute hold** sits at D9's mean-hold floor (C lines 614, 687): the rule is coded as
  written; if a missing exit bar or the engine shortens a hold, the engine's label applies (a label, not a drop).
- **K5-L-10 preauc is unconditional** (no signal); its only guard is the entry bar's presence (C line 490-491).
- **K5-L-11 11 declarations**, catalog order, gold before copper. K5-preauc-01 has 1 trial (silver has no vehicle),
  not the 2 of U9's count, which assumed silver admitted.
- **K5-L-12 Two coders and their test files** (tests/test_e4_k5_members*.py).

## 11. The K5 release check and the tables (lead ruling 05:40 PDT, after Task 1b)

Source: reports/stage_e4b_release_check.json (sha256 0715d01f0ab7f9176a7d559e4f8bde151e656c29271a9a1de22bece3218789b7)
and .md (ReleaseChecker-OpusMed, 05:07-05:38). Its rows govern; the tables are generated from them.

- **EC-UKBH:** 61 England-and-Wales bank holidays 2019-05-01..2026-06-19 (gov.uk's live file, which covers 2019-2028),
  equal in both directions to IBA's LBMA Gold Price holiday calendars for 2019-2026.
- **Scheduled auction days (K5-L-03):** 1,863 weekdays less 61 bank holidays = 1,802 gold AM and PM auction days;
  research window 319 weekdays, 12 bank holidays, 307 auction days.
- **No-auction days announced in advance: 14, all PM only** (AM held, PM not held), the Christmas and New Year half
  days, each with a dated LBMA notice that predates the day: 2019-12-24, 12-31; 2020-12-24, 12-31; 2021-12-24, 12-31;
  2022-12-23, 12-30; 2023-12-22, 12-29; 2024-12-24, 12-31; 2025-12-24, 12-31 (in 2022 and 2023 the Friday before).
  GOLD_PM_AUCTIONS leaves them out; GOLD_AM_AUCTIONS keeps them. In the research window: 2025-12-24 (also a metals
  early-halt date, so no member trades it) and 2025-12-31 (preauc may trade its AM auction; pmfix does not).
- **Instants (K5-L-02):** 04:30 / 09:00 CT on 1,678 days and 05:30 / 10:00 CT on the 124 weekdays of 5-hour weeks;
  C10's table matches in all eight years; no published change to the 10:30 and 15:00 London start times was found.
- **EC-FOMC:** the calendar's 57 FOMC rows are all 13:00 CT and equal E.3's FOMC_STATEMENT_DATES exactly; 10 in the
  research window (C12's list).
- **Unverified, confirmation window only:** the IBA calendars' publication dates rest on PDF metadata, and the 2019 PDF
  was served from a 2020-12-02 capture (its advance publication rests on the 2019-06-08 page capture that links to it);
  two CDX lookups timed out; the 10:30 and 15:00 start times were not checked page by page for 2020-2025. None of this
  touches a research-window date, so no K5 member carries "calendar partly unverified" for the screen. A Tier A event
  member's confirmation session re-checks the 2019-2024 no-auction days first (K5-L-01).
