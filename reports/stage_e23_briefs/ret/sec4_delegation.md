## 4. Delegation record

The lead was Opus 5.5 at xhigh, under ultracode. It kept the reserved work for itself:
- the decomposition and every brief, and the lead spec (lead_spec.md);
- the shortlist and data-use map (P1.3-P1.4), and the prereg text and power reasoning;
- the rulings on both reviews, the registration, the two run-once reads, the discovery screen judgment, and this synthesis.

Every number entering a verdict was rechecked by a Fable worker that did not produce it. Times are PDT, taken from each agent's first and last transcript message; tokens per spawn are in section 8.

| Spawn (name) | Agent file | Model | Effort | Parallel or serial | Start-end (PDT) | Objective | Output | Status, check |
|---|---|---|---|---|---|---|---|---|
| InventoryReaderK1 .. K8, H6, CDE-OpusHigh (10) | workflow agent (e23-p1-inventory, wf_b90fd95b-792) | opus | high | all 10 at once | 02:16-02:28 | P1.1: one cluster's frozen intraday triggers, with inputs, windows read and data needs | reports/stage_e23_briefs/inventory/{K1..K8,H6,CDE}.json, .md | 10/10 done. The lead checked row counts (208 rows, 34 excluded with reasons) and compiled inventory_compact.txt |
| MechanismReaderM1 .. M11-OpusHigh (11) | workflow agent (e23-p1-mechanisms, wf_e33ecfd4-8a1) | opus | high | all 11 at once, one shared brief, at most 60 searches each, deadline 03:45 | 02:16-02:32 | P1.2: the stated multi-day mechanism per family, with strength and direction at 5 and 20 days and verbatim quotes | reports/stage_e23_briefs/mech/M1..M11.md, raw pages in mech_pages/ | 11/11 done by 02:33. The lead judged strength and direction itself (shortlist.md); RegReviewer re-read the memos the shortlist cites |
| BookCoder-OpusXHigh | worker-xhigh | opus | xhigh | parallel with TriggerCoder | 02:21-02:42 | The unit-book engine, trend regressors, statistics, power, config, run-once runner, freeze manifest and tests | trigger_hold/{types,constants,units,book,stats,power,trend,config,evaluate,run,freeze_manifest}.py; tests; bookcoder_report.md | Done. Per-root trend sums equal E.21's (max diff 0.0); T3 reproduced exactly; reviewed by CodeReviewer; recomputed by VerdictVerifier |
| TriggerCoder-OpusXHigh | worker-xhigh | opus | xhigh | parallel with BookCoder | 02:22-03:08 | Extract each shortlisted frozen trigger's decision events (d0, tau, side) on both windows from the frozen member code, without outcomes | trigger_hold/events*.py; reports/stage_e23_events/*.json (8 files) and validation/; triggercoder_report.md | Done. W_cf validations 0 differences against the harness. Exit-side counters were on disk 02:46-02:58, then scrubbed and disclosed (R-08, C-09) |
| RegReviewer-FableXHigh | worker-xhigh | fable | xhigh | parallel with CodeReviewer | 03:10-03:24 | Adversarial review of the design and registration before any read | reports/stage_e23_briefs/reg_review.md | APPROVE WITH FIXES, 0 BLOCKING (R-01..R-09; section 5) |
| CodeReviewer-FableXHigh | worker-xhigh | fable | xhigh | parallel with RegReviewer | 03:11-03:29 | Line-by-line review of trigger_hold/ against the spec before any read | reports/stage_e23_briefs/code_review.md | APPROVE WITH FIXES, 0 BLOCKING (C-01..C-09; section 5) |
| VerdictVerifier-FableXHigh | worker-xhigh | fable | xhigh | serial, after the confirmation step | 03:35-03:36; 05:21-05:41; 07:22-07:25 | Recompute every verdict number from the written files with its own code; spot-audit the books from the bar stores | reports/stage_e23_briefs/verify/verdict_verify.md, recompute_file_based.json, spot_audit.json, tables.md | Done: VERIFIED WITH NOTES, 0 BLOCKING, 7 NOTEs (section 5.3). The usage limit cut it at its start; it stalled 05:41-07:21 on a wait that matched itself, which the lead killed at 07:22 |

Messages the lead sent to running workers (SendMessage):
- To TriggerCoder: inventory facts (02:29) and the final shortlist (02:35).
- To BookCoder: the shortlist and two spec additions (02:35).
- To VerdictVerifier: resume after the usage limit (05:21), and run the spot audit now (07:22).

Deviations:
- No opening estimate table was printed in chat before the first spawn, against the CLAUDE.md rule. The plan ran against the prompt's clock instead: outcome reads by 10:30, return by 11:30.
- The usage limit (03:38-05:21) cut the verifier at its start.
- From 05:41 to 07:21 the session stalled. The verifier's wait for the end suite matched its own command line in `pgrep -f`, so it never fired, and the lead waited on the verifier instead of checking the wait. Section 8 shows both gaps as their own rows.
- Workers spawned no further workers.
- At most 2 heavy jobs ran at once: the start suite with the coders' tests, the discovery read alone, and the end suite alone.
