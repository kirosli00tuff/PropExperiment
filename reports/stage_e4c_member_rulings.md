# Stage E.4 Part 3 (K3), Task 4: the lead's rulings on the K3 fidelity audit

Lead: Opus 5.5 (xhigh), 2026-09-27. Audit: reports/stage_e4c_member_audit.md Part 1 (MemberAuditor-K3-FableXHigh, fable
xhigh, 09:13-09:34, which wrote none of the code, specs or tests): BLOCKING 0, SHOULD FIX 2 (tests only), NOTE 10. All nine
modules implement their frozen entries and nothing more; the file hashes equal the lead's pre-audit list; every literal table
recomputes equal from its sources (FX_FULL_SESSIONS 1,797 with the 17 early-F dates; MONTH_ENDS 85; EW 63; TGT 48; Tokyo
business days 1,761; gotobi-or-month-end 404; T_L/T_E 1,885; T_T 1,761; all C9 known answers; R_eq 85 of 85 exact); the
dropped EUR mehedge trial follows the entry's rule (no saved SX5E close after 2025-06-17 for 13 of 14 research month-ends);
the freeze static check passes on all 15 files; the dry run gives 30 declarations.

## SHOULD FIX (tests only) and a minor note, ruling R-K3-1

- **S-1** `test_ldnrev_signal_reads_closes_not_opens` did not separate closes from opens (its open and close moves had the
  same sign); **S-2** the ldnmom field test did not pin the T_L-13 close; **N-5** the ldnrev window test did not separate a
  T_L-10 read from T_L-11. Ruling R-K3-1: accepted; MemberCoder-B-OpusXHigh (resumed) changed the fixtures as the auditor
  proposed and showed each mutant now fails. No member module changed (section below).

## NOTE

| Note | Finding | Ruling |
|---|---|---|
| N-1 | K3-L-11: the literal C4 test keeps 1,814 sessions, the ruling 1,797; the engine-F condition binds only where rules/sessions.py carries Topstep's holiday schedule (2024 on): 15 US-holiday dates in 2019-2023 with no FX halt stay in FX_FULL_SESSIONS, and on them the engine's F is regular | Recorded with K3-L-11. **Flagged for the user and every confirmation session:** the frozen session rules have no Topstep holiday schedule before 2024, so the confirmation-window simulation holds trades to their natural exits on those US holidays where a live account would have closed by 11:30 or 11:45. A harness-coverage fact, not a member defect; nothing changed |
| N-2 | the ports on those dates trade and are flattened at F (CP1's 13:29 entry refused) | D6 and E.3-L-11. No change |
| N-3 | a data gap that defers an entry fill past the exit bar leads to a refused and resent exit two minutes later | consistent with "first bar at or after" and D9.3b. No change |
| N-4 | K3-L-09 silent on item 11(d): tick history confirmed for the research-window bars only (reports/stage_e2a_bars.md "raw off-tick prices 0") | The confirmation session checks the confirmation-window bars' ticks before reading them (they are not bought yet). Listed in the return |
| N-5 | see R-K3-1 | fixed |
| N-6 | E.3 notes inherited by the copies (asdict idiom, F literal in cp2's window, exit helpers, cp2's reset) | as E.3. No change |
| N-7 | `assert ticks == ()` in tkypre/tkypost member code, unreachable | cosmetic. No change |
| N-8 | TARGET 2026 capture's markup | informational. No change |
| N-9 | MURC year-end xls and the FRED spot check not re-read by the auditor | neither enters a research-window decision. No change |
| N-10 | 30 trials declared, not the banner's 31; the dropped EUR mehedge trial adds nothing to N | as the specs say (section 9b). No change |

## The fix (R-K3-1)

MemberCoder-B-OpusXHigh (resumed) changed the fixtures of the three tests in tests/test_e4_k3_members_b_ldn.py as ruled (now
45cfdc684d8260a3d69a7abf44b64ab5471e11445d8be0c69877a7f3236ed613). Four in-memory mutants each fail their test (ldnrev reads OPEN; ldnmom's 09:47 read OPEN; ldnmom's 09:45 read CLOSE;
ldnrev reads T_L-10) and pass again after the restore. Its reference command ended `198 passed in 3.08s`. Against
reports/stage_e4_briefs/k3_files_pre_audit.sha256 exactly one file differs (that test file); every member module equals the
audited hash.

Cluster freeze (write_cluster_freeze): reports/stage_e_k3_member_freeze.json, sha256 c4fb5da41d69a6be54ea07d1ab35bd2b238d1fbeafaeb3008b886f8fc6888d95, 30 members;
load_cluster_freeze + verify_cluster_code OK.
