## 8. Session cost

No initial estimate table was printed before the first spawn (a deviation, section 4). The rows are set against the prompt's
clock instead: no outcome read after 10:30, the return by 11:30, the session ended by 12:00.

Sources:
- Times: PDT, from the STATE file, file mtimes, git, and each agent's first and last transcript message.
- Tokens: reports/stage_e23_briefs/ret/make_cost.py, run over the lead's .jsonl and every subagent transcript, counted to
  2026-10-17T14:29:56Z (07:29:56 PDT). The lead's last messages after that (final assembly and commit) are not counted.

### Final ETA table (actuals)

| Task | Owner | Model | Effort | Start | End | Time | Tokens | Status and deviations |
|---|---|---|---|---|---|---|---|---|
| 0 Start checks | lead | opus | xhigh | 02:03:59 | 02:04:14 | 15 s | in lead | done; all expected |
| 0 Start suite (detached, nice 10) | lead | - | - | 02:04:19 | 02:28:56 | 24.6 min | in lead | 1 failed (known h6), 7634 passed |
| Context reading, scouting, briefs, lead spec | lead | opus | xhigh | 02:04 | 02:21 | 17 min | in lead | done |
| P1.1 inventory | InventoryReaderK1..K8, H6, CDE-OpusHigh (10, workflow) | opus | high | 02:16:13 | 02:28:24 | 12 min | 71,417,556 | 10/10 done |
| P1.2 mechanisms | MechanismReaderM1..M11-OpusHigh (11, workflow) | opus | high | 02:16:30 | 02:32:13 | 16 min | 94,195,121 | 11/11 done (deadline 03:45) |
| P2 engine | BookCoder-OpusXHigh | opus | xhigh | 02:21:42 | 02:42:24 | 21 min | 13,544,251 | done; E.21 sums and T3 exact |
| P2 events | TriggerCoder-OpusXHigh | opus | xhigh | 02:22:14 | 03:08:16 | 46 min | 44,187,620 | done; counters incident 02:46-02:58 disclosed |
| P1.3-P1.4 shortlist, data-use map | lead | opus | xhigh | 02:33 | 02:37 | 4 min | in lead | done before any outcome read |
| Prereg text, window and power reasoning | lead | opus | xhigh | 02:37 | 03:09 | 32 min (with waits on TriggerCoder) | in lead | done |
| Power table, first freeze | lead | opus | xhigh | 03:09 | 03:11 | 2 min | in lead | 3fdd98d7... |
| Registration review | RegReviewer-FableXHigh | fable | xhigh | 03:10:51 | 03:24:42 | 14 min | 1,768,830 | APPROVE WITH FIXES, 0 BLOCKING |
| Code review | CodeReviewer-FableXHigh | fable | xhigh | 03:11:00 | 03:29:43 | 19 min | 3,723,290 | APPROVE WITH FIXES, 0 BLOCKING |
| Fixes, freeze rebuilds, dry runs, commits, registration | lead | opus | xhigh | 03:25 | 03:33:45 | 9 min | in lead | 25bc321, 75874c4; r008-E23 N 533 -> 538; id rename |
| Discovery read (once) | lead | - | - | 03:33:54 | 03:34:35 | 41 s | in lead | rc 0; no survivor |
| Confirmation step (once) | lead | - | - | 03:35:27 | 03:35:29 | 2 s | in lead | 0 survivors; nothing read |
| Verification, part 1 | VerdictVerifier-FableXHigh | fable | xhigh | 03:35:45 | 03:36:26 | 1 min | (in the verifier's total below) | cut by the usage limit |
| Return tables and drafts | lead | opus | xhigh | 03:36 | 03:38 | 2 min | in lead | done |
| PAUSE: usage limit | - | - | - | 03:38 | 05:21 | 1 h 43 min | - | excluded from work |
| End checks; end suite (detached, nice 10) | lead | - | - | 05:21:40 | 05:41:25 | 20 min | in lead | 1 failed (known h6), 7728 passed |
| Verification, part 2 (file-based, 343 rows) | VerdictVerifier-FableXHigh | fable | xhigh | 05:21 | 05:41:05 | 20 min | (below) | done; then waited on a wait that could not fire |
| Return drafts (sections 2, 3, 6, 7) | lead | opus | xhigh | 05:22 | 05:41:33 | 19 min | in lead | done |
| STALL: the verifier's self-matching wait; the lead idle | - | - | - | 05:41:33 | 07:21:27 | 1 h 40 min | - | excluded from work; the cause is the lead's and the verifier's (section 4) |
| Verification, part 3 (spot audit, verdict) | VerdictVerifier-FableXHigh | fable | xhigh | 07:22 | 07:25:07 | 3 min | 9,542,109 (all parts) | VERIFIED WITH NOTES, 0 BLOCKING |
| Return, progress, STAGES, final checks, cost, commit | lead | opus | xhigh | 07:21:27 | about 07:35 | about 14 min | in lead | done; no push |
| **Stage** | lead and 26 worker spawns | | | 02:02:54 | about 07:35 | **about 2 h 10 min of work** (02:03-03:38, 05:21-05:41, 07:21-07:35); wall clock 5 h 32 min, of which 1 h 43 min pause and 1 h 40 min stall | **323,355,480** (lead 84,976,703; workers 238,378,777) | reads done at 03:35 (deadline 10:30); return written by about 07:35 (deadline 11:30) |

### Tokens per model

| Model | Input | Output | Cache read | Cache creation | Total |
|---|---|---|---|---|---|
| claude-fable-5-1 | 1,904 | 235,012 | 13,416,877 | 1,380,436 | 15,034,229 |
| claude-opus-5-5 | 3,498 | 1,449,464 | 300,979,056 | 5,889,233 | 308,321,251 |
| all | 5,402 | 1,684,476 | 314,395,933 | 7,269,669 | 323,355,480 |

Delegation share: the lead 84,976,703 (26.3%), workers 238,378,777 (73.7%). By model: Fable 4.6%, Opus 95.4%.

### Per worker spawn (agent file, model, effort as set, tokens)

| Spawn | Agent file | Model | Effort | Tokens |
|---|---|---|---|---|
| TriggerCoder-OpusXHigh | worker-xhigh | opus | xhigh | 44,187,620 |
| BookCoder-OpusXHigh | worker-xhigh | opus | xhigh | 13,544,251 |
| VerdictVerifier-FableXHigh | worker-xhigh | fable | xhigh | 9,542,109 |
| CodeReviewer-FableXHigh | worker-xhigh | fable | xhigh | 3,723,290 |
| RegReviewer-FableXHigh | worker-xhigh | fable | xhigh | 1,768,830 |
| InventoryReaderCDE-OpusHigh | workflow agent | opus | high | 11,418,905 |
| InventoryReaderK2-OpusHigh | workflow agent | opus | high | 10,543,576 |
| InventoryReaderK3-OpusHigh | workflow agent | opus | high | 9,166,818 |
| InventoryReaderK4-OpusHigh | workflow agent | opus | high | 7,783,905 |
| InventoryReaderK6-OpusHigh | workflow agent | opus | high | 7,575,743 |
| InventoryReaderK5-OpusHigh | workflow agent | opus | high | 7,124,358 |
| InventoryReaderK1-OpusHigh | workflow agent | opus | high | 6,798,447 |
| InventoryReaderK8-OpusHigh | workflow agent | opus | high | 4,417,225 |
| InventoryReaderH6-OpusHigh | workflow agent | opus | high | 4,018,176 |
| InventoryReaderK7-OpusHigh | workflow agent | opus | high | 2,570,403 |
| MechanismReaderM10_USDA-OpusHigh | workflow agent | opus | high | 10,792,595 |
| MechanismReaderM11_OVERNIGHT_REVERSAL_VOL-OpusHigh | workflow agent | opus | high | 10,643,057 |
| MechanismReaderM2_FOMC-OpusHigh | workflow agent | opus | high | 10,306,577 |
| MechanismReaderM5_BREAKOUT_LOCATION-OpusHigh | workflow agent | opus | high | 9,481,681 |
| MechanismReaderM4_INTRADAY_MOM-OpusHigh | workflow agent | opus | high | 8,811,785 |
| MechanismReaderM9_ENERGY_REPORTS-OpusHigh | workflow agent | opus | high | 8,491,619 |
| MechanismReaderM6_AUCTION-OpusHigh | workflow agent | opus | high | 8,455,135 |
| MechanismReaderM3_FLIGHT-OpusHigh | workflow agent | opus | high | 7,882,276 |
| MechanismReaderM8_FIXES-OpusHigh | workflow agent | opus | high | 6,849,121 |
| MechanismReaderM7_MONTHEND-OpusHigh | workflow agent | opus | high | 6,500,415 |
| MechanismReaderM1_LIMIT-OpusHigh | workflow agent | opus | high | 5,980,860 |

These are token counts, not plan-credit percentages; the /usage meter is the user's to read. The 21 readers spent 165.6M
tokens (51% of the stage), most of it cache reads. That is the largest line to trim in a later stage, for example with
fewer, merged inventory readers.
