# Stage E.2a: the lead's readings of the frozen D2 vehicle rule (Task 9)

Written by the Stage E.2a lead (Opus 5.5, xhigh) on 2026-09-25 at about 00:40 PDT, before any
research-window bar or mbp-1 record of any Stage E product was read by anyone, and before the ML
freeze commit. Its sha256 is recorded in reports/stage_e2a_STATE.md at writing. It is not a
design change: every point below is a place where the frozen text of docs/STAGE_E_DESIGN.md D2
(with D6, D8, D9.5, D9.11 and U7) must be read to be computed, and the reading is fixed here so
that nothing about it can be chosen after the numbers exist. The independent recomputation (Task
12) uses these readings, and may challenge any of them.

## r_c, the per-contract risk

- **R1. O_X and C_X** are design D6's session-table values for the exposure's group (equity
  08:30 / 15:00; rates and FX 07:20 / 14:00; energy 08:00 / 13:30; gold 07:20 / 12:30; silver
  07:20 / 12:25; copper 07:10 / 12:00; grains 08:30 / 13:15; livestock 08:30 / 13:00; crypto
  08:30 / 15:00; CT). D6 says they are "TO BE CONFIRMED against CME's published settlement
  procedures in E.2 before any bar is read, any correction logged". The CalendarBuilders report
  the confirmation; if CME's published time differs from D6, the lead rules on it in writing
  (reports/stage_e2a_STATE.md and the return document) before r_c is computed.
- **R2. The dates.** The contract's research-window trade dates 2025-04-01..2026-06-19 (its
  research parquet), excluding: its roll-blackout dates (the splice trade date and the two
  sessions before it); vendor-degraded dates; and dates on which the group calendar lists a full
  closure or an early halt or early close at or before C_X, because close(C_X - 1 min) does not
  exist on those dates.
- **R3. The two prices.** open(O_X) is the open of the first one-minute bar of the trade date that
  starts at or after O_X; close(C_X - 1 min) is the close of the last bar that starts before C_X.
  Both bars must lie in [O_X, C_X) of the same trade date; a date with no bar there is excluded.
  On a liquid contract these are exactly the bars at O_X and C_X - 1 min; on a thin contract a
  missing minute is replaced by the nearest traded minute inside the window, as the MES segment
  table behind R* does (first open and last close of the window). The count of dates where either
  exact bar was missing is reported per contract.
- **R4. Dollars.** |close - open| / tick_size x tick_value_usd, per contract, with tick_size and
  tick_value from reports/stage_e0_liquidity.json; r_c is the plain mean over the dates of R2.

## q_c, rho_c

- **R5. The cap.** cap_c = min(the D9.5 lot cap, the D9.11 50K volatility cap): minis 1, micros
  10, SIL 5 and MBT 1 by D9.5; D9.11 ("every size stays within the 50K figure at all times")
  lowers SIL and MHG to 2 (MCL and MGC stay 10; CL, QM, RB, HO and GC stay 1). D2's own text
  defines cap_c by D9.5 alone; D9.11, also frozen, forbids a size above the 50K figure, so the
  smaller governs.
- **R6. Rounding.** q_c = min(cap_c, max(1, round(R* / r_c))) with round-half-up
  (floor(x + 0.5)); R* = $360.68. rho_c = q_c r_c / R*.

## The choice

- **R7. Non-candidates by decision.** M6E and M6A are not candidates (U7), whatever their rho.
- **R8. Cost per dollar of risk.** (commission_c + 2 x one-side slippage_c) / r_c, the D2 formula
  with q_c cancelled (both terms scale with q_c), where commission_c is the D8 round-turn
  commission per contract (MCL $1.72, MNG $1.92) and one-side slippage_c is the minute-weighted
  mean over the day session [O_X, C_X) of D8's per-side cost at size q_c: s_b plus the mean of the
  two sides' depth terms at q_c (a round turn hits one ask and one bid), in USD per contract.
- **R9. The rule.** Candidates: admissible contracts (D1.3) with rho_c <= 2.0, less R7. Preferred:
  candidates with rho_c >= 0.5. The vehicle is the preferred candidate with the lowest R8 cost;
  ties go to the higher 2026 January-August ADV of design D1's table. D9.11's sentence "D2 prefers
  SIL and MHG for silver and copper whenever they are candidates" is read as: for silver and
  copper, if SIL (MHG) is a candidate it is the vehicle; the arithmetic shows whether this binds.
- **R10. Undersized.** If an exposure has candidates but none with rho_c >= 0.5, it is traded at
  the cap on the candidate with the lowest R8 cost and flagged "undersized" (its funnel-derived
  epsilon then governs, D2 and D3).
- **R11. No candidate.** If no admissible contract has rho_c <= 2.0 (after R7), the exposure is
  "no candidate: not traded in Stage E" (D2). The lead does not choose a vehicle by judgment.
- **R12. Translated epsilon.** eps_X = floor($85.00 / (q_c x tick_value_c)) net ticks per contract
  per day of the chosen vehicle (D3).

## What this file does not do

It fixes no number and reads no data. It does not change D2, D3, D6, D8 or D9.
