# Stage E.9 Task 4: the lead's rulings on the fidelity audit (cluster K8)

Lead: Opus 5.5 xhigh, 2026-10-01 23:38 PDT. Audit: reports/stage_e9_member_audit.md Part 1
(MemberAuditor-K8-FableXHigh, 23:10-23:37 PDT): 0 BLOCKING, 0 SHOULD FIX, 8 NOTE; every table recomputed
identical by the auditor's own code (full sessions 1779/1782/1783/1783/1783 over 2019-05-01..2026-06-19;
FLIGHT 1779, OILCAD 1783, WKNDBTC 1779; guard instants MGC 312, 6C 513, MNQ 313, equal to the engine's set;
54 research Mondays); 146 auditor mutants, 143 killed, 3 equivalent. No member is unimplementable.

No finding requires a code or test change, so the audited files are frozen exactly as audited (sha256 in
reports/stage_e9_briefs/k8_files_pre_audit.sha256, unchanged at 23:33 and at the freeze).

| Finding | Grade | Ruling | Change |
|---|---|---|---|
| F-1 reference values from the signal leg only | NOTE | **R-T3-1** Confirmed. The entries define each reference value by the signal leg's two bars (C lines 273-275, 402-403); the traded leg plays no part. A full-session date with no traded-leg bars is removed as a trade date by the runner (not every leg trades), which the member cannot read, the same logic as the roll-blackout clause (K5-L-05). Specs K8-L-04's wording "a leg" clarified to "the SIGNAL leg". | specs wording only |
| F-2 oilcad per-decision missing entry bar | NOTE | **R-T3-2** Kept: K4-L-14's per-decision reading for a multi-decision member, for consistency with ovr. C5's date-level letter would make a later absence void earlier decisions (non-causal). Open choice in the return. | none |
| F-3 reference dates include roll-blackout dates | NOTE | **R-T3-3** Kept: K5-L-05 and K4-L-08 (the member has no roll input; the engine removes the dates as trade dates). Open choice in the return. | none |
| F-4 "equity-and-crypto" as one calendar | NOTE | **R-T3-4** Agreed with the auditor: immaterial in the research window (EQUITY full sessions are a subset of CRYPTO's). K8-L-03 stands. | none |
| F-5 flight marks the day used before the position/pending check | NOTE | **R-T3-5** No change: the branch is unreachable on real bars (one entry a day; a position routes to the exit; a pending order without a position means the day's entry was already taken). | none |
| F-6 engine tests use NO_RELEASES | NOTE | **R-T3-6** No change: the auditor's own engine checks with the real frozen calendar (reports/stage_e9_briefs/audit_k8/engine_checks.py) show no D9.5a deferral of a K8 entry in any case the member could know; C6 is pinned by direct-call and table tests. | none |
| F-7 wkndbtc coverage measured on every window date | NOTE | **R-T3-7** Kept as designed (S0.12, K8-L-13, E.3-L-17): stricter, and never clipped by a session boundary. | none |
| F-8 the K8-L-08 edge (missing traded bar at t, later fill inside a guard) | NOTE | **R-T3-8** Accepted as logged. Task 6 and Task 7 read each K8 record's `fill_guard_deferral` counter, and the return reports the count. | none |

Information items: (i) the earlier clusters' frozen calendar tables differ from the current rules/sessions.py
on 2024-07-03 (K4, K5) and on 14 FX US-holiday dates 2022-2023 (K3), all outside the research window: for the
user, before those clusters' confirmation sessions (return section 7). (ii) oilcad's "|z| = 2.0 reported if it
occurs" (K8-L-09) cannot be checked without reading bars; its probability is zero, and it is listed as not
checked.
