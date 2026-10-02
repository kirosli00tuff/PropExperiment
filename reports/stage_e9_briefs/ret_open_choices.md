Readings (specs section 6; the full text there):
1. **K8-L-01** 4 declarations, labels "<member> [grid] <traded root>", catalog order, traded leg first: the template's
   primary-leg rule; the ordinal seeds the power check.
2. **K8-L-02** bars by CT date and clock per leg (E.3-L-03, K7-L-01): MBT's weekend bars carry Monday's trade date from
   2026-06-01.
3. **K8-L-03** C5's "any leg's D10 group calendar" = every leg's own calendar; "equity-and-crypto" = both the equity and
   the crypto calendar (narrowest); full session = no early halt and engine F 15:08 (K3-L-11, K7-L-02).
4. **K8-L-04 / R-T3-1 / R-T3-3** reference dates = the 20 most recent member full sessions, roll-blackout dates included
   (K5-L-05, K4-L-08; the member cannot read a roll calendar); values from the signal leg only; warm-up K4-L-09.
5. **K8-L-05** signal computations guarded per computation within the signal leg (C4; the entries).
6. **K8-L-06 / R-T3-2** a missing entry bar: flight's first trigger ends the day (C5 "the entry bar is missing"; E.3-L-08's
   analogue); oilcad per decision time (K4-L-14), not C5's date-level letter; wkndbtc no trade.
7. **K8-L-07** T_e = the actual fill minute (the text: "the entry fill minute").
8. **K8-L-08 / R-1b-1** C6's skip set = the engine's D9.5a set for the traded root (the frozen release calendar, unchanged,
   including two WPSR rows E.4 dropped for its own event members); the extra rows (MGC G17 08:15 CT, MNQ ISM 09:00 CT) can
   never meet a K8 fill minute; the skip tests the scheduled fill minute (a missing traded bar could still push a fill into
   a guard: 0 occurrences, Part 2).
9. **K8-L-09** arithmetic: flight exact integer-pair order statistic (no `fractions` on the allowlist); oilcad float z
   with statistics.stdev, ddof 1 (K4-L-05's statistic route); wkndbtc integer tick sign.
10. **K8-L-10** flight requires c6 > 0 only to avoid a division by zero (never binds on MES).
11. **K8-L-11** oilcad's "no open position; no exit pending" = flat: no position and no pending order of either side.
12. **K8-L-12** wkndbtc: d a Monday; the Friday = d - 3 (calendar), full in both calendars; P_F, P_S and the MNQ entry
    bar by CT date, clock and trade date; one instrument_id across P_F and P_S; an MBT blackout on the Friday alone does
    not remove the Monday (V16(a) removes trade dates).
13. **K8-L-13 / R-T3-7** trading_windows measured on every window date (wkndbtc's Friday bar on each date's own 14:59).
14. **K8-L-14** tables span 2019-05-01..2026-06-19.
15. **K8-L-15** C section 6: items 1-4 by V16; item 5 as built in the frozen calendar (WPSR concerns 6C program-wide);
    items 6, 9, 12 as frozen; items 7, 8, 10 no member effect; item 11 for the user (section 7).
16. **K8-L-16** the N rule: a trial counts when the runner writes its screen record.
17. **K8-L-17** two coders; coder A wrote the shared tables first.
Task 1b rulings: 18. **R-1b-2** MES's blackouts taken from the runner's record (15 dates), no member label. 19. **R-1b-3**
a late open (2026-06-01 crypto) is not an early close. 20. **R-1b-4** unscheduled publications not added to any guard.
Audit rulings: 21. **R-T3-4..R-T3-6, R-T3-8** no code or test change (immaterial, unreachable, or checked by the auditor's
own engine runs).
Process choices:
22. Coder A was spawned at 22:29, before Task 1b returned (the prompt runs 2A after Task 1 and only 2B after 1b); section
    7 arrived by message at 22:33 with no table correction.
23. Task 6 rebuilt three trials (HEOD, wkndbtc, oilcad) instead of "one port, one other member": K8 has no port, so both
    Tier A trials and the trial with event-window fills and MLL liquidations were named.
24. Pytest runs used `-p no:cacheprovider` and no PYTHONPYCACHEPREFIX (E.6-E.8 precedent: three bytecode tests fail
    under a prefix); scripts and the runner used a fresh prefix.
25. Coder B's report was saved by the lead from its final message (the harness refused the worker's write), text unchanged.
26. The descriptive sign checks and splits (section 3) were computed by the lead from the trip lists; they are not trials
    and enter no verdict.
27. After the accidental exit, the interrupted end suite was kept and re-run in full rather than resumed.
