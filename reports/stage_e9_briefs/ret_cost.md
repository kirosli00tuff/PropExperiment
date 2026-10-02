**Wall clock** 2026-10-01 22:12 to 2026-10-02 00:42 PDT (2 h 30 min), of which **one pause, 00:04-00:23 (19 min)**: the
session exited by accident and was resumed by the user ("resume please accidentally exited"); the end suite running at
the time died at about 50% and was re-run. **Work time 2 h 11 min.** First estimate 3 h 25 min (to about 01:37; the prompt
expected about 1.5 h), revised at 23:10 to about 00:50 as the coders finished 50 minutes early; the screen took 1 minute
and the recomputation 8.

**Final ETA table** (PDT; tokens from the transcripts):

| Task | Owner | Model | Effort | Start | End | Time | Tokens | Status and deviations |
|---|---|---|---|---|---|---|---|---|
| 0 Startup checks (start suite to 22:26) | lead | opus | xhigh | 22:12 | 22:26 | 14 min | in lead | done; suite = E.8's end |
| 1 Member specs (section 7 at 22:33) | lead | opus | xhigh | 22:21 | 22:33 | 12 min | in lead | done |
| 1b Event checks | ReleaseChecker-OpusMed | opus | medium | 22:20 | 22:31 | 11 min | 10,204,160 | done; MES blackouts unverifiable pre-run |
| 2A Tables and flight | MemberCoder-A-OpusXHigh | opus | xhigh | 22:28 | 23:09 | 41 min | 20,290,233 | done; spawned before 1b returned |
| 2B oilcad and wkndbtc | MemberCoder-B-OpusXHigh | opus | xhigh | 22:32 | 23:09 | 37 min | 14,813,091 | done; .md write refused, saved by the lead; stray files deleted |
| 2g Gate suite | lead | - | - | 23:09 | 23:21 | 12 min | in lead | 5582 passed |
| 3 Fidelity audit | MemberAuditor-K8-FableXHigh | fable | xhigh | 23:09 | 23:37 | 28 min | 11,285,770 (Parts 1 and 2) | 0 blocking, 0 should-fix, 8 notes |
| 4 Rulings, freeze, suite, commit 558a5dc | lead | opus | xhigh | 23:37 | 23:53 | 16 min | in lead | done; no code change |
| 5 Screening run | lead | opus | xhigh | 23:53 | 23:54 | 1 min | in lead | 4 run, 0 refused |
| 6 Recomputation | MemberAuditor-K8-FableXHigh (resumed) | fable | xhigh | 23:55 | 00:03 | 8 min | above | no discrepancy |
| 7a Result, return draft, first end suite (died at 50%) | lead | opus | xhigh | 23:54 | 00:04 | 10 min | in lead | interrupted by the exit |
| Pause (accidental exit and resume) | - | - | - | 00:04 | 00:23 | 19 min | - | excluded from work |
| 7b Return, end suite re-run (00:24-00:38), end checks, cost, progress | lead | opus | xhigh | 00:23 | 00:42 | 19 min | in lead | done |
| **Stage** | | | | 22:12 | 00:42 | **2 h 30 min wall, 2 h 11 min work** | **99,814,881** (lead 43,221,627, 43.3%; workers 56,593,254, 56.7%) | first estimate 3 h 25 min; the prompt expected about 1.5 h |

**Tokens per model** (the lead transcript 20d17daf's .jsonl, which the resumed session kept writing to, plus every worker
transcript under its subagents/ folder; reports/stage_e9_briefs/cost.py, output cost.out; counted at 00:38, so the last
few lead steps after it are not in the table):

| Model | Input | Output | Cache read | Cache creation | Total |
|---|---|---|---|---|---|
| claude-opus-5-5 | 786 | 573,924 | 86,658,681 | 1,295,720 | 88,529,111 |
| claude-fable-5-1 | 1,004 | 161,926 | 10,240,730 | 882,110 | 11,285,770 |
| all | 1,790 | 735,850 | 96,899,411 | 2,177,830 | 99,814,881 |

Per worker spawn: worker-medium opus medium (ReleaseChecker) 10,204,160; worker-xhigh opus xhigh (MemberCoder-A)
20,290,233; worker-xhigh opus xhigh (MemberCoder-B) 14,813,091; worker-xhigh fable xhigh (MemberAuditor, both parts)
11,285,770. Delegation share: lead 43.3%, workers 56.7%; by model tier opus 88.7% (lead 43.3%, workers 45.4%), fable
11.3%. Cache reads are 97.1% of the total. E.8 used 129.7M tokens for 27 trials; E.9 used 99.8M for 4 (two-leg members,
four test files per coder, and the extra cross-leg audit items).
