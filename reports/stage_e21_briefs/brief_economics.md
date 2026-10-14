# Brief: EconWorker-OpusHigh (Stage E.21 Step 4, F8 descriptive economics)

F8 of docs/prompts/STAGE_E.21.md (read lines 114-128) is DESCRIPTIVE: it is not part of any verdict
and never changes one. You compute it after the evaluation, from the run's files only. You read no bar
and never rerun the evaluation.

## Inputs (read by section; never load a whole large JSON into context: write a script)
- reports/stage_e21_runs/per_root/<ROOT>.json (17 files; schema stage_e21_per_root/1): `vehicle`,
  `tick_value_cents`, `per_contract_daily_dollars` (date -> roll-adjusted daily dollar P&L of ONE E.12
  vehicle contract held, costs excluded; null where the path breaks), `holdings[test]` (rows per
  rebalance/entry/exit: `date`, `kind`, `target` = contracts of the E.12 vehicle per unit of capital,
  `weight`, `sigma`, `S_M`/`S_u`, `V`, `price_ticks`), `fills[test]` (per fill: `date`, `kind`, `trade`,
  `cost_per_contract_cents` by case, `cost`).
- reports/stage_e21_runs/T1_result.json .. T4_result.json (series per cost case; stats; per_root);
  reports/stage_e21_runs/verdict.json.
- reports/stage_e13_trend_carry.md section C (C1 formula; C2 per-instrument table: "$ risk / contract /
  yr" for each vehicle, micros included).
- reports/stage_e21_proped_rules.json and .md (PropEd plans; Phidias Premium 50K under "comparison").
- reports/stage_e21_briefs/lead_spec.md sections 4, 5, 10 and A11.

## Lead's method (fixed here; record every further assumption in your output)
1. Per test T1, T2, T3 (T4 is a combination in risk units and has no contract book: report its daily
   series' realized volatility only, and say so).
2. Book volatility: sigma_b = sd (ddof 1) of the base-case daily series x sqrt(252) (capital units).
3. Vehicles for the personal account (F8): MNQ (NQ), M2K (RTY), MGC (GC), MCL (CL), M6E (6E), micro
   yields where the root maps (use the micro rows of E.13's C2 table for ZT, ZF, ZN, ZB and MTN for TN,
   MWN for UB if C2 lists them); full-size otherwise, FLAGGED (NG, ZC, ZS, ZL, HE, LE, and any root with
   no micro in C2). Per-contract annual dollar risk sigma$_i from C2's "$ risk / contract / yr" of that
   vehicle.
4. Personal account capital at target volatility tau in {15%, 25%}: leverage k = tau / sigma_b. A root's
   full-signal (|s| = 1) position at capital K is (k x K x 0.40 / S) / sigma$_i contracts (S = the
   test's divisor at its maximum, 17 for T1/T2, 2 for T3). K_min(tau) = the smallest K at which EVERY
   root's full-signal position is at least one contract = max_i sigma$_i x S / (k x 0.40). Report
   K_min(tau) per test, the binding root, the per-root contracts at K_min, and the per-root contracts at
   K = $10K, $25K, $50K, $100K (E.13 C3's levels; which roots round to zero). Cross-check against E.13
   C3's sizing table and say where they differ and why.
5. The integer book at its smallest integer size (the scale at which the binding root holds one
   contract at full signal; the same for both tau): contracts c(i,M) = round(scale x target(i,M)) in E.12
   vehicles, with scale from step 4 converted to E.12 vehicles (the run's per-contract P&L is per E.12
   vehicle; where the F8 vehicle differs, convert by the notional ratio and say so). Daily dollar P&L =
   sum_i c(i, held) x per_contract_daily_dollars(i, d) - fill costs (base case; per_contract cost x
   |delta c|; roll legs 2 x |c|). Report its daily and 5-day dollar sigma (empirical sd of daily and of
   non-overlapping 5-day sums), mean, and the tracking error to the fractional book scaled to the same
   dollar volatility.
6. PropEd (lead ruling A11): for EVERY PropEd plan that allows overnight holds (automation is
   UNCONFIRMED for all plans; flag it on every row), and for Phidias Premium 50K beside them: the plan's
   drawdown type and amount and daily loss limit (UNSOURCED where the JSON says so), whether the book's
   instruments and contract counts fit the plan's instrument list and max contracts, the daily and 5-day
   dollar sigma at the smallest integer size against the drawdown, and the share of rolling 21-trade-day
   windows whose worst drawdown would breach it: within each window, from the window's start, the EOD
   equity's maximum drop from its running peak (EOD trailing) or from the start (static), compared with
   the drawdown amount; a daily loss above the daily loss limit (where sourced) also breaches. Two
   variants: with weekend holds (the series as is; needs the paid add-on: show its price), and without
   weekend holds (set to zero the P&L of each date that follows a weekend gap and charge, per root, two
   extra fills x |contracts| x that root's median base per-contract cost for each weekend crossed). Also
   report the breach shares at the largest integer scale at which the book's daily dollar sigma is at
   most 10% of each plan's drawdown, if such a scale holds every root at one or more contracts; say
   "none" otherwise.
7. No fee or payout model. No new test, no variant of any rule's signal.

## Output
reports/stage_e21_economics.md (tables: per test K_min and per-root contracts; the integer book's
dollar statistics; the PropEd and Phidias table with breach shares; every assumption and every FLAG)
and reports/stage_e21_economics.json (the same numbers). Your script goes in
reports/stage_e21_briefs/econ/economics.py (it reads only the files above). Compute at nice 10.

## Limits
Never write under reports/stage_e21_runs/, never run multiday.run evaluate, never read a bar or any
data/ file, never edit multiday/, base_rules/, tests/, ledger/, live/, ops/, REGISTRATION.md; do not
commit. Time box 35 minutes. Return: paths, a summary of at most 200 words, and anything unfinished.
