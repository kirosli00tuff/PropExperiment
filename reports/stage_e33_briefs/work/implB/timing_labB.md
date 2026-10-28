# Timing note: implementation B labels (LabelCoder2-OpusXHigh, Stage E.33 B2)

All times PDT on 2026-10-27, taken from `date` calls and the builder's own clocks.

| Step | Start | End | Wall time | Notes |
|---|---|---|---|---|
| Read brief, INTERFACE, protocol, E.31 library | 14:46:52 | 14:54 | about 7 min | |
| labB.py, labB_book.py, labB_cal.py, tests | 14:54 | 15:00 | about 6 min | 33 tests, 0.8 s |
| One-date probe (2021-03-11) | 15:02:21 | 15:02:36 | 14.5 s | sigma history of 20 dates: 11.9 s |
| First 20-date build (discarded) | 15:02:48 | 15:05:35 | 165.9 s | rebuilt after the sigma cutoff fix (readings LB-16) |
| Second 20-date build | 15:07:43 | 15:10:22 | 158.5 s | code_sha12 e0c36f590c7f; superseded by comment-only edits |
| Final 20-date build | 15:13:04 | 15:15:51 | 165.6 s | code_sha12 efdde5c74ee1; row counts equal to the second build |

Final build breakdown (3 worker processes, nice 10; the label figures are from the second build, whose code differs only in comments):
- Sigma history (own sigma_ZM, P0.3): 306 distinct prior trade dates replayed up to 13:13:00 CT,
  147.9 s in total. The cache is DERIVED/implB/labels/_mids/<D>.npz.
- Labels: 20 dates, 11.9 s in total. Per date: book replay 0.8 to 4.7 s (load and replay of
  0.2 to 1.5 M ZM records); all six label tables plus both simulated sides take 0.2 to 0.5 s.
  The sum over the 20 dates is 34.7 s of process time.
- Peak memory: 472 MB RSS for one process on the busiest date (2021-05-04, 1.48 M records).
  At most 3 processes, so the peak is about 1.5 GB. Available memory before the run was 9.9 GB.

Scale-up estimate (a guess from these measurements, not a run): 796 OOF dates at about 2 s each
for replay and labels, plus 816 sigma-history replays at about 1.4 s each, comes to about
20 min of process time, or about 7 min wall time on 3 processes. The sigma history is cached per
date.

Self-checks on the 120 written tables: 29 structural checks, 0 violations. They cover row_ok
within entry_ok; NaN, -1 and 0 sentinels off the rows; spans inside [08:35, 13:13]; the FH span
end equal to t + L + h; the TB span end inside (t + 2L, t + 2L + h]; fills after t + L; exits
after entries and by 13:20; every unmade entry flagged; and clean simulated nets equal to the
labels exactly. These checks print counts only.
