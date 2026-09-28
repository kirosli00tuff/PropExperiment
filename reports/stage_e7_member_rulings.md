# Stage E.7 Task 4: the lead's rulings on the K1 fidelity audit

Written by the Stage E.7 lead (Opus 5.5, xhigh), 2026-09-28 02:45-02:47 PDT, on reports/stage_e7_member_audit.md Part 1
(MemberAuditor-K1-FableXHigh, 02:09-02:45 PDT): 0 BLOCKING, 1 SHOULD FIX, 9 NOTE; tables recomputed equal (1846 / 1779 /
1794 rows, 0 differences); 113 auditor mutants: 106 killed, 4 equivalent, 2 non-equivalent survivors (VB-26, VW-28, both
finding 1), 1 ill-formed and killed by hand; every lead reading stands.

| Finding | Grade | Ruling | Fix |
|---|---|---|---|
| 1. vxnband and vwap engine-run tests never feed the previous evening's bars; "only bars of CT date d are read" (vxnband.py:226-227, vwap.py:180-181) has no failing mutant (VB-26, VW-28 survive and change trades on realistic bars) | SHOULD FIX | **R-T3-1: accepted, test-only.** The module code is correct (it skips the evening before any accumulation) | MemberCoder-B (resumed 02:46) adds per member an engine-run test whose dates start at the previous evening 17:00 CT, for vxnband with the post-Memorial-Day evening carrying the holiday's early_halt_ct label, asserting the normal round trip and that 2025-05-27 stays a complete C_prev for 2025-05-28; each shown to kill its mutant. No member module changes |
| 2. K1-L-14 item 10(c) defers C7's tick-history confirmation | NOTE | **R-T3-2: label, no code change.** No web access is allowed outside Task 1b. The data side is checked: reports/stage_e2a_bars.json raw_checks show 0 off-tick prices at the frozen tick (MNQ 0.25, M2K 0.10, MYM 1.0) over every research bar, so no finer tick occurred; a coarser tick in a sub-period is not excluded by that check. Only CP2's buffer ("4 ticks of P") depends on the tick size (CP1's sign, CP3's CLV, vxnband's band and vwap's sign are tick-invariant). The three K1-cp2-01 trials carry the label "tick history not source-verified for the research window (bars on the frozen grid)"; the confirmation session confirms the tick history (C7) before any confirmation bar is read | specs K1-L-14 amended (section 8) |
| 3. Cboe publication time observational | NOTE | **R-T3-3:** the return carries "VXN availability before 08:30 CT observational, not stated" with R-1b-1's label on K1-vxnband-01 | none |
| 4. No synthetic-F flatten test for vxnband and vwap | NOTE | **R-T3-4: adopted** (the prompt's test list names the flatten) | MemberCoder-B adds one test per member (same resumption as R-T3-1) |
| 5. K1-L-08 is one of two readings (sent vs filled) | NOTE | **R-T3-5: K1-L-08 stands** (the conservative one; never more intents than the fill count reading); the alternative is recorded here and in the return's open choices | none |
| 6. vxnband's hold is 28 minutes under a D9.5a-deferred entry | NOTE | as K1-L-05; no change | none |
| 7. _calendar.py starts 2019-05-01, so V for 2019-05-01 is None | NOTE | no trade date is affected (MNQ's S_X is 2019-05-06); no change | none |
| 8. cp2.py `F_REGULAR_CT = time(15, 8)` literal in trading_windows only | NOTE | no change (equals D line 391 and the audited K7 port; rules.sessions is not an allowed member import) | none |
| 9. Two behaviours reachable only by direct calls | NOTE | follow the specs; no change | none |
| 10. Nine research dates without V | NOTE | reported with K1-vxnband-01's result (R-1b-5) | none |

The auditor's line-drift remark on K1-L-01 (C9's availability line is 154, not 150-151) is corrected in the specs; the
C9 range in the header is corrected to 148-156. No reading changes.

After R-T3-1/R-T3-4, the lead re-hashes the member modules and tables (they must equal the pre-audit hashes in
reports/stage_e7_briefs/k1_files_pre_audit.sha256), writes the cluster freeze (reports/stage_e7_briefs/write_k1_freeze.py),
runs the full suite, and commits "K1 member freeze".
