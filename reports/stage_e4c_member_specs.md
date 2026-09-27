# Stage E.4c member specifications, cluster K3 FX (Part 3, Task 1)

Written by the Stage E.4 lead (Opus 5.5, xhigh), 2026-09-27 06:13-06:40 PDT, before any K3 member code exists and before
any K3 bar has been read by this session. Same method as the K4 and K5 specs: each frozen entry restated as the code must
implement it, with line references; every reading in section 10; no rule changed; earlier readings adopted where the text
is the same (E.3-L-nn, K4-L-nn, K5-L-nn).

Sources and their state:
- C = reports/stage_e0_catalog_K3.md, frozen by reports/stage_e1_freeze.json. Header and C1-C12 lines 62-234. E.1 edits
  to K3 (reports/stage_e1_changes.md K3-00..K3-03) touch only the banner (U6, U7) and the excluded K3-ml-01; no active
  member's rule changed. Lead rulings inside the catalog that bind: R-05 (K3-ldnrev-01's signal window, C line 382) and
  the 01:40 narrowing of K3-ldnmom-01 to EUR and JPY (C line 482).
- D = docs/STAGE_E_DESIGN.md: D6 port texts lines 364-366, "4 ticks of P" lines 368-374, the FX row (O 07:20, C 14:00,
  F 15:08) line 394; D9.
- Vehicles (reports/stage_e2a_vehicles.md lines 24-30): EUR 6E, AUD 6A, GBP 6B, JPY 6J, CHF 6S "chosen"; CAD 6C and NZD 6N
  "undersized"; every q_c = 1. The frozen runner trades both statuses (E.3-L-20). Operative eps (reports/stage_e2a_epsilon.md
  lines 21-27): 6E 13, 6A 17, 6B 13, 6C 17, 6J 13, 6S 13, 6N 17 ticks.
- Frozen per-root values (checked 06:20): day_session_ct (07:20, 14:00) for all seven; vendor_tick 6E, 6A, 6C, 6S, 6N
  0.00005, 6B 0.0001, 6J 0.0000005; group fx.
- EC-CAL = data.group_session.load_group_calendar("fx"). Research window: 316 trade dates; early halts 2025-07-04, 11-28,
  12-24, 2026-04-03, 06-19. A bar's `early_halt_ct` is that of its CT CALENDAR date, not its trade date
  (data/group_session.py lines 583-590), which matters for the members that trade the CT evening of d-1 (K3-L-04).
- The K3 check: reports/stage_e4c_release_check.md and .json (Task 1b): the clocks T_L, T_E, T_T, EC-EW, EC-TGT, EC-JP,
  gotobi and Tokyo month-ends, ME(m), and the index histories. Section 11 applies it.
- Source-window labels (reports/stage_e2a_source_window_amendment.md): K3-ldnmom-01 and K3-mehedge-01 lost
  "source-overlap"; the others keep it (the confirmation session reads the labels).

What the member does NOT implement (engine and runner, as in K4/K5): trade dates and roll blackouts (opens refused, bars
delivered); UR-1; F and the flatten; D8 costs; D9.5a's guard (the release calendar's NFP, CPI, FOMC and the other rows
naming FX roots; no fix instant is a release row); D9.3; the skip of a fill less than 2 minutes before F; D9.7 (no hard FX
price limit is expected: C11); D9.5.

---

## 0. Common to all nine members

S0.1 Legs. One leg each, the traded exposure's vehicle, `LegSpec(root, True)`; the index of K3-mehedge-01 is NOT a leg
(it is a literal monthly table, S0.11). No micro, E7 or M6* contract is read.

S0.2 Declarations and ordinals: catalog order, then the catalog's exposure order EUR, AUD, GBP, CAD, JPY, CHF, NZD.
Label `"<member id> <ROOT>"`; factories `make_6e`, `make_6a`, `make_6b`, `make_6c`, `make_6j`, `make_6s`, `make_6n` (only
the exposures a member trades).

| Member | Module | 6E | 6A | 6B | 6C | 6J | 6S | 6N |
|---|---|---|---|---|---|---|---|---|
| K3-cp1-01 | strategy.members.k3.cp1 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
| K3-cp2-01 | strategy.members.k3.cp2 | 8 | 9 | 10 | 11 | 12 | 13 | 14 |
| K3-cp3-01 | strategy.members.k3.cp3 | 15 | 16 | 17 | 18 | 19 | 20 | 21 |
| K3-ldnrev-01 | strategy.members.k3.ldnrev | 22 | - | - | - | 23 | 24 | - |
| K3-ldnmom-01 | strategy.members.k3.ldnmom | 25 | - | - | - | 26 | - | - |
| K3-mehedge-01 | strategy.members.k3.mehedge | not traded (no free EURO STOXX 50 history, section 11) | - | - | - | 27 | - | - |
| K3-ecbfix-01 | strategy.members.k3.ecbfix | 28 | - | - | - | - | - | - |
| K3-tkypre-01 | strategy.members.k3.tkypre | - | - | - | - | 29 | - | - |
| K3-tkypost-01 | strategy.members.k3.tkypost | - | - | - | - | 30 | - | - |

The EURO STOXX 50 history could not be obtained free (section 11), so K3-mehedge-01 on 6E is not declared (the entry's rule, C lines 619-620) and the later ordinals close up: 30 declarations.

S0.3 Size: `q_c` from the frozen table (1 for all seven), never a literal; exits close the whole position.

S0.4 Clock: America/Chicago; "the bar at hh:mm" on CT date d (E.3-L-03) unless the entry names another day (CP1's 17:00
bar of d-1; tkypre's and tkypost's bars on the CT evening of d-1, C3 lines 82-86). O and C from `day_session_ct`. The fix
instants T_L, T_E and T_T are literal per-date tables (S0.11), not computed at run time.

S0.5-S0.10 as K4 (market intents; named entry bar exact, E.3-L-04; exits on the first present bar at or after the named
bar, E.3-L-22, no re-entry after an engine-forced close; integer vendor ticks, E.3-L-19). Instrument guard (C4 lines 87-96:
"the bars of one signal computation or of one position carry different instrument_ids"): the bars read at or before the
entry decision carry the entry decision bar's instrument_id (E.3-L-12); K3-L-03 reads "of one position".

S0.8' Early halts (C4 line 92): the TRADE DATE d must not be an early-halt date of EC-CAL FX; every new member reads it
from the literal FX_FULL_SESSIONS table (K3-L-04), not from a bar's field.

S0.11 Literal tables (E.3-L-01), generated from their sources and pinned by tests:
- strategy/members/k3/_calendar.py (MemberCoder-B): FX_FULL_SESSIONS (EC-CAL FX trade dates with no early halt and the
  regular F of 15:08 CT per the engine's session rules, K3-L-11, over the calendar's coverage, K4-L-13); MONTH_ENDS ((month, ME date): the last EC-CAL FX trade date of each calendar month,
  whether or not it is halted); EW_BANK_HOLIDAYS; TGT_CLOSING_DAYS; TOKYO_BUSINESS_DAYS (or the JP holidays plus the rule);
  GOTOBI_OR_TOKYO_MONTH_END (the tkypre event dates).
- strategy/members/k3/_clocks.py (MemberCoder-B): per weekday date 2019-04-01..2026-06-19, T_L and T_E as CT "HH:MM", and
  per Tokyo business day d, T_T as the CT "HH:MM" on d-1 (all computed with zoneinfo in the generator and checked against
  the release check).
- strategy/members/k3/_mehedge_signal.py (whichever coder takes mehedge): per month m with an obtained index, (ME date,
  R_eq for EUR, R_eq for JPY or None) from the saved free index files (section 11), each value from closes available before
  the entry time.

S0.12 trading_windows (E.3-L-17; both clock slots where a fix moves; overnight intervals at offset -1 where they lie on the
CT evening of d-1, which the coverage check keeps because trade date d's session starts at 17:00 of d-1):

| Member | Intervals [start, end) CT |
|---|---|
| CP1 | (17:00, 17:01) day -1; (07:49, 07:50); (13:29, 14:00) |
| CP2 | (07:20, 15:08) |
| CP3 | (07:20, 14:00) |
| ldnrev | (09:49, 10:21); (10:49, 11:21) |
| ldnmom | (09:45, 10:06); (10:45, 11:06) |
| mehedge | (08:59, 09:58); (09:59, 10:58) |
| ecbfix | (00:59, 15:06) |
| tkypre | (17:29, 19:56), both ends on day -1 |
| tkypost | one interval from 18:55 on day -1 to 01:01 on day d (start_offset_days -1, end_offset_days 0) |

S0.13 Topstep: flat by F (latest fill 15:05, ecbfix); market; at most one entry a day (ecbfix two legs, sequential); holds
15 to 469 minutes; no stops; no starred vehicle (M6E, M6A are not vehicles); 1 lot-equivalent; D9.11 and D9.12 name no FX
product (C11).

S0.14 C10-style guard: no K3 new member computes a percent return except mehedge's R_eq = ln(P_a / P_b) on index closes
(P > 0 by construction; a non-positive or missing close means no trade that month).

---

## 1-3. The ports (C lines 237-379; D lines 364-366)

The rule texts are D6's, on the FX row, identical in clock to E.3's K2 rates ports (O 07:20, C 14:00): E.3's
reports/stage_e3_member_specs.md sections 1-3 apply field by field with these K3 values.

| Field | CP1 (C 237-284) | CP2 (C 285-339) | CP3 (C 340-379) |
|---|---|---|---|
| Exposures | the seven roots | the seven roots | the seven roots |
| Clock | signal 17:00 bar of d-1 to 07:49; entry 13:29/13:30; exit first bar at or after 13:58 | OR [07:20, 07:35); eligible [07:35, 14:00); 75 present bars; no C-2 exit | daily bar [07:20, 14:00), C_d close of 13:59; entry on the 07:20 bar; exit at or after 13:58 |
| Buffer | - | 4 x vendor_tick: 0.0002 (6E, 6A, 6C, 6S, 6N), 0.0004 (6B), 0.000002 (6J), equal to the catalog's table (C lines 305-314) | - |
| Readings | E.3-L-05, L-06 | E.3-L-07, L-08; K4-L-06 | E.3-L-09, L-10, L-11 |
| Trials | 7 | 7 | 7 |

Catalog section 7 item 9 (C line 1154): CP2's range meets the 07:30 NFP release and CP1's 13:30 fill sits 30 minutes after
FOMC: the ports are copied unchanged; the engine's D9.5a and D8 apply (the D8 window is the harness's).

## 4. K3-ldnrev-01 (month-end London fix, contrarian). C lines 380-478

| Field | Rule | Reference |
|---|---|---|
| Exposures | 6E, 6J, 6S | C 384-386 |
| Event set | ME(m) (MONTH_ENDS) for each month m, if ME(m) is in FX_FULL_SESSIONS and not in EW_BANK_HOLIDAYS; no shift | C 425; C9 lines 196-201 |
| Signal | M = ticks(close of the bar at T_L-1) - ticks(close of the bar at T_L-11) (R-05; the text's T_L-16 is superseded); both present, one instrument_id; M = 0 no trade | C 382, 426-428 |
| Entry | BUY if M < 0, SELL if M > 0; market intent on the bar at T_L+4, fill T_L+5 (10:05 CT, or 11:05 CT in mismatch weeks) | C 429-433 |
| Exit | market intent on the bar at T_L+19, fill T_L+20; missing: first later present bar | C 434-435 |
| Guard | the T_L-11, T_L-1 and T_L+4 bars carry one instrument_id | S0.9 |
| Trials | 3 | C 477 |

## 5. K3-ldnmom-01 (front-running into the London fix). C lines 479-554

| Field | Rule | Reference |
|---|---|---|
| Exposures | 6E, 6J (the lead's 01:40 narrowing) | C 481-482 |
| Event set | every trade date d in FX_FULL_SESSIONS that is not in EW_BANK_HOLIDAYS | C 511-512 |
| Signal | S = ticks(close of the bar at T_L-13) - ticks(open of the bar at T_L-15); both present, one instrument_id; S = 0 no trade | C 513-515 |
| Entry | BUY if S > 0, SELL if S < 0; market intent on the bar at T_L-13, fill T_L-12 (09:48 CT standard) | C 516-517 |
| Exit | market intent on the bar at T_L+4, fill T_L+5 (10:05 CT standard) | C 518-519 |
| Guard | the T_L-15 and T_L-13 bars (T_L-13 is the entry decision bar) carry one instrument_id | S0.9 |
| Trials | 2 | C 553 |

## 6. K3-mehedge-01 (month-end equity-hedge rebalancing). C lines 555-647

| Field | Rule | Reference |
|---|---|---|
| Exposures | 6J with the Nikkei 225 (obtained free). 6E with the EURO STOXX 50 is NOT traded: its free history could not be obtained (section 11); no substitute | C 559-562, 619-620 |
| Event set | ME(m) as ldnrev (full session, not an E&W bank holiday) | C 589 |
| Signal | R_eq(m) = ln(P_a / P_b): P_a the index's last official close on a local date strictly before ME(m)'s calendar date; P_b its last official close in month m-1; no trade if R_eq = 0 or a close is missing; a literal monthly table | C 590-597 |
| Entry | SELL if R_eq > 0, BUY if R_eq < 0; market intent on the bar at T_L-61, fill T_L-60 (09:00 CT standard) | C 598-600 |
| Exit | market intent on the bar at T_L-4, fill T_L-3 (09:57 CT standard) | C 601-602 |
| Guard | the only bar read before the entry is the T_L-61 bar | S0.9 |
| Trials | 1 (6J) | C 646 |

## 7. K3-ecbfix-01 (euro, into and after the ECB fix). C lines 648-725

| Field | Rule | Reference |
|---|---|---|
| Exposure | 6E | C 650-651 |
| Event set | every trade date d in FX_FULL_SESSIONS that is not in TGT_CLOSING_DAYS | C 684-685 |
| Leg 1 | SELL, market intent on the bar at 00:59 CT on d, fill 01:00; exit intent on the bar at T_E-1, fill at T_E (07:15 CT, or 08:15 in mismatch weeks) | C 686-690 |
| Leg 2 | BUY, market intent on the bar at T_E, fill T_E+1, only when flat with no pending order (K3-L-05); exit intent on the bar at 15:04, fill 15:05 | C 691-693 |
| Guard | leg 1: its entry bar only; leg 2: its entry bar only (no signal) | S0.9 |
| Trials | 1 | C 724 |

## 8. K3-tkypre-01 (gotobi dollar demand into the Tokyo fix). C lines 726-800

| Field | Rule | Reference |
|---|---|---|
| Exposure | 6J | C 728 |
| Event set | trade dates d in FX_FULL_SESSIONS such that d, as a Tokyo date, is a Tokyo business day whose day of month is 5, 10, 15, 20, 25 or 30, or the last Tokyo business day of its month; no shift | C 751-756 |
| Entry | SELL; market intent on the bar at 17:29 CT on calendar day d-1, fill 17:30 | C 757-759 |
| Exit | market intent on the bar at T_T-1, fill at T_T (18:55 CST or 19:55 CDT on d-1) | C 760-762 |
| Guard | the entry bar only | S0.9 |
| Trials | 1 | C 799 |

## 9. K3-tkypost-01 (dollar weakness after the Tokyo fix). C lines 801-855

| Field | Rule | Reference |
|---|---|---|
| Exposure | 6J | C 803 |
| Event set | every trade date d in FX_FULL_SESSIONS such that d, as a Tokyo date, is a Tokyo business day | C 821-822 |
| Entry | BUY; market intent on the bar at T_T (d-1 evening), fill T_T+1 | C 823-824 |
| Exit | market intent on the bar at 00:59 CT on d, fill 01:00 | C 825-826 |
| Guard | the entry bar only | S0.9 |
| Trials | 1 | C 854 |

## 9b. Trial count

30 declarations: 21 port trials and 9 new (ldnrev 3, ldnmom 2, mehedge 1 (6J), ecbfix 1, tkypre 1, tkypost 1). The E.1 banner's
31 (C line 5) assumed both index histories; the EUR mehedge trial is dropped by the entry's own rule. Program N after K3:
123 + the trials screened.

## 10. Lead readings

Adopted: E.3-L-01, L-03..L-13, L-17, L-19, L-20 (6C and 6N undersized, coded and screened), L-22; K4-L-06 (CP2's buffer as
4 x vendor_tick), K4-L-13 (a calendar table spans its source's coverage), K5-L-02 (instants by zoneinfo, as literal
tables).

New readings for K3:
- **K3-L-01 Tables span 2019-04..2026-06** (as K4-L-01, K5-L-01): the frozen code serves the confirmation window; Task 1b
  checks the research window first; anything unchecked is listed in section 11.
- **K3-L-02 The fix instants are literal per-date tables**, generated with zoneinfo (C9's rule) and checked against C9's
  known-answer tests; no member calls zoneinfo at run time.
- **K3-L-03 C4's "bars of one position"**: the guard covers the bars read at or before the entry decision (E.3-L-12). A
  position's exit is sent whatever the exit bar's instrument_id, since the position must close; an instrument change
  inside a position can only happen across a roll, which the runner's roll blackout already removes.
- **K3-L-04 The early-halt test uses trade date d from an EC-CAL table.** C4 excludes "dates the D10 FX calendar marks as
  early halt or early close" (C line 92), that is, trade date d. A bar's early_halt_ct names its CT calendar date, which is
  d-1 for tkypre's and tkypost's entry bars, so every K3 new member reads FX_FULL_SESSIONS for d. For the daytime members
  this gives the same answer as E.3-L-11.
- **K3-L-05 ecbfix's legs are sequential.** Leg 2 enters only when leg 1 has closed (flat, no pending order) at the bar at
  T_E. If leg 1's exit bar was missing and its exit is still pending at T_E, there is no leg 2 that day (the narrowest
  reading of "sequential, at most one position").
- **K3-L-06 Month-ends include halted dates in the table**, and the member skips a month whose ME(m) is an early-halt date
  or an E&W bank holiday (C9 lines 196-201: "do not trade in month m if ME(m) is excluded by C4"); no shift to another day.
- **K3-L-07 mehedge's index is not a leg.** Its monthly R_eq table is generated from the saved free files and carries only
  values whose closes precede the entry time (C lines 590-597: P_a strictly before ME(m)'s calendar date).
- **K3-L-08 Tokyo business days and gotobi as C9 defines them** (the CAO holiday file; weekdays; 31 Dec-3 Jan closed; no
  shift), with Task 1b's check of the year-end rule reported in section 11.
- **K3-L-09 Catalog section 7** items are settled by the frozen text and E.1: items 1-5, 7, 8 and 10 as frozen (one trial
  per traded exposure; M6E/M6A are not vehicles); item 6's three judgments are applied as written (K3-L-06, K3-L-08, the
  London-holiday skip); item 9: the ports stay as D6 writes them.
- **K3-L-10 Two coders; mehedge goes to whichever finishes first** (the prompt); test files tests/test_e4_k3_members*.py.
- **K3-L-12 ecbfix trades leg 2 only after leg 1 opened that date** (ruling on MemberCoder-B's question). A missing 00:59
  bar is a C4 date exclusion ("does not trade on ... dates on which ... the entry bar is missing", C line 93), which covers the
  whole two-leg trade; if the engine refuses leg 1's intent, the sequential pair (C line 686, "two legs, sequential") never
  started, so there is no leg 2 either (the narrowest reading). An engine close of leg 1 (D9.7, MLL) also ends the day (S0.7).
- **K3-L-11 An FX date whose engine flatten time is early is an early-close date for C4** (ruling 06:50 on MemberCoder-A's
  observation). data/calendars/fx.py leaves early_halt_ct unset on the US holidays 2025-09-01, 11-27, 2026-01-19, 02-16 and
  05-25 (and their earlier-year twins), while the engine's session rules (rules/sessions.py, D10: "F = the early close minus
  15 minutes") flatten at 11:30 or 11:45 on them; the metals and rates calendars mark the same dates. C4 excludes "dates the
  D10 FX calendar marks as early halt or early close" (C line 92); D10 marks them through F. So FX_FULL_SESSIONS = the EC-CAL
  FX trade dates with no early halt AND the regular F (15:08 CT) per the engine's session rules; the generator lists the dates
  the second condition removes. This is the narrower event set. The ports follow D6 and do not test it (the engine's F
  governs them). **Flagged for the user:** the frozen FX calendar and the frozen session rules disagree on these dates; nothing
  in the harness is changed.

## 11. The K3 check and the tables (lead ruling 06:58 PDT, after Task 1b)

Source: reports/stage_e4c_release_check.json (sha256 c63c13a69559c90efdb72969e20244a261343839660436082fcaf44a35f931e9) and
.md (ReleaseChecker-OpusMed). Its rows govern; the tables are generated from them and from EC-CAL.

- **Clocks:** every C9 known-answer test passes (T_L 9/9, T_E 2/2, T_T 1/1 and C9's three worked T_T examples); the 11:00 CT
  London weeks equal C9's list exactly, and T_E's 08:15 CT weeks are the same weeks.
- **EC-EW:** 63 England-and-Wales bank holidays 2019-04..2026-06 (12 in the research window). **EC-TGT:** six TARGET closing
  days a year 2019-2026, equal across every capture read (2019-2021 from the ECB's written rule, since the page listed no
  dates for them; labelled); in the window 2025-04-18, 04-21, 05-01, 12-25, 12-26, 2026-01-01, 04-03, 04-06, 05-01.
- **EC-JP:** 148 Japanese holidays (Cabinet Office file); 350 gotobi dates and 87 Tokyo month-ends 2019-04..2026-06; the
  31 Dec-3 Jan rule matches MUFG Research's yearly TTM files exactly for 2019-01-01..2026-08-31 (1,868 business days on both
  sides, zero mismatches).
- **ME(m):** 87 FX month-ends; 2020-08-31 and 2021-05-31 are E&W bank holidays (dropped); none in the research window.
  ME(2019-04) and ME(2026-06) lie outside EC-CAL's coverage (2019-05-01..2026-06-19): MONTH_ENDS carries only months whose
  last day is inside the coverage (K4-L-13), so no member trades a month whose month-end the calendar cannot state (June
  2026's is 06-30, after the window; the window's last date, 06-19, is not a month-end).
- **Index histories (K3-mehedge-01):**
  - **Nikkei 225: obtained free** from Nikkei Inc.'s own daily file (https://indexes.nikkei.co.jp/nkave/historical/
    nikkei_stock_average_daily_en.csv, live plus three Wayback captures, saved under data/vendor/index_history/ with sha256),
    1,761 closes 2019-04-01..2026-06-19, no missing trading date, no value on a non-trading date; FRED spot checks agree
    (a Firecrawl scrape, not saved). K3-mehedge-01 trades 6J.
  - **EURO STOXX 50: not obtained.** STOXX's free file holds only a rolling three months and the full history needs a
    login; stitching 17 Wayback captures leaves 889 dates missing (257 in the research window). By the entry's rule ("that
    exposure's trial is dropped and logged, never substituted", C lines 619-620), K3-mehedge-01 on 6E is not traded and adds
    no trial. **Named for the user.**
- **Unverified (confirmation window only, or informational):** the FRED spot check was not saved; the 2019-2021 TARGET dates
  come from the written rule; the SX5E gap count assumes STOXX's days equal TARGET's. No research-window date the traded
  members use is unverified, so no K3 member carries "calendar partly unverified" for the screen.
