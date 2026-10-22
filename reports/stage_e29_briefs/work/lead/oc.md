- OC-1 E.28b had not finished at launch (no E.28 return or commit; its key-watch shell was still polling). E.29
  went ahead because it is simulation-only and touches no acct-3 or pilot file. E.29's code imports E.28's A3 files
  read-only. During the pause, E.28 was committed (60eb6b6, "Stage E.28 methods brief, ranking and pilot"), and
  the imported files are now tracked with unchanged sha256 (A3_funnel.py 9b0183b5..., A3_models.py f9389bf8...,
  A3_econ.json 6140c7d6...). V47 (QM research, pilot on hold) and the E.30 prompt (54f07ab) also arrived during
  the pause. The prompt binds V20 to V46; V47 is used only in section 7.
- OC-2 Fable is not available on Pro. The independent review was done by BasketReviewer-OpusXHigh in a fresh
  context (V46 item 5), not by Fable.
- OC-3 The correlation window is E.28's standard window, 2022-11-01 to 2023-10-31, rather than everything before
  2024-03-01. This keeps E.28's pilot window untouched.
- OC-4 The position limit form (declaration section 4): only Topstep B3 (2.1 lots) meets a binding limit, the
  2-lot first XFA tier. The primary form is no-overlap scheduling, which leaves P&L unchanged in this model. The
  sensitivity drops MGC on those days.
- OC-5 Members whose E.28 break-even is "> 4" had their alone break-evens recomputed on a 0 to 12 tick grid. The
  coder also extended MNQ's market case at Topstep and Tradeify (coder choice C7).
- OC-6 The best-basket rule is the lowest setting-(i) k* at rho 0.5, with "> 4" and "n/a" counted as infinity
  (coder choice C8). The market case was run at every rho for the best basket (coder choice C6).
- OC-7 The reporting points are k = 1.0, 1.5 and 2.0 in setting (i), and mu_QM = B0's mu*_lim, 0.50 and 1.00 in
  setting (ii).
- OC-8 The trade split is floor(20 / n), with the remainder going to members in basket order. That gives B3 7/7/6.
- OC-9 The E.29 tests live in reports/stage_e29_briefs/work/basket/test_e29_basket.py, outside tests/: the repo
  suite's testpaths is tests, and the tests depend on E.28's untracked files.
- OC-10 The main run skipped grid confirmation (A3_econ.md 2.4); the coder logged every threshold as "bisection,
  unconfirmed" (coder choice C3), because the usage-limit cuts and two reboots took the stage's time. The reviewer
  confirmed a sample, and the lead then confirmed every remaining record in a separate pass (work/confirm/,
  03:13 to 04:19, same code, seed and draws). It moved 0 of 470 thresholds. The labels in E29_cells.json and
  E29_tables.md were left as generated; a dated lead note at the head of E29_tables.md points to
  E29_confirmation.md.
- OC-11 Time. Work was interrupted twice by usage limits (about 19:38 to 21:54, and about 22:05 to 02:40) and by
  two reboots (20:42 and 22:21). The prompt's 23:00 stop fell inside the second pause. At 02:41 on 10-22 the user
  said to continue, so the stage finished on 10-22.
- OC-12 After the second reboot, the lead restarted the resumable grid run itself (one detached command) instead
  of through a worker. It is a mechanical step, and the coder was still blocked by the usage limit.
- OC-13 The realistic rho band (0 to 0.25 for a direction-neutral strategy's daily P&L) is the lead's judgment from
  price correlations. It was not measured.
- OC-14 The per-trade edge in sigma units used in section 3.4 is the lead's interpretation, added after the results.
  It is not in the declaration, and no number in the tables depends on it.
- OC-15 The coder's other choices were accepted as logged in work/basket/LOG.md: C1 evaluations cached by (M, S);
  C2 E.28's operation order; C4 P10K is computed only in limit cells; C5 pass rate = E.28's p_pass_attempt; C9 the
  2-lot tier set by E.19's tier_cap_vec on the previous close.
- OC-16 The declaration's header says it was written "about 19:40 PDT". That was the lead's clock estimate. The
  file mtime (19:24:16) governs, and the text was not changed after its hash. STATE's CorrMeasurer times
  (19:28 to 19:29) were lead entries too; its transcript shows 19:25:55 to 19:28:58. Section 4 uses transcript times.
- OC-17 The prompt's "at most 4 workers at once" was read as agents; at most two ran at once. Compute processes
  followed CLAUDE.md's compute limits (at most half the 20 logical CPUs, nice 10): the confirmation pass used 6
  processes. Its memory peak was not recorded.
- OC-18 The lead did not print the initial ETA table in chat before the first spawn (CLAUDE.md asks for one). The
  final table in section 8 is therefore set against the prompt's own schedule (start 19:19, return by 23:30 on
  10-21) instead.
