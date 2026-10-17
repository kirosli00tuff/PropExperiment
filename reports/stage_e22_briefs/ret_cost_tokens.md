| Model | Input | Output | Cache read | Cache creation | Total |
|---|---|---|---|---|---|
| claude-fable-5-1 | 4,034 | 474,495 | 23,583,225 | 1,970,771 | 26,032,525 |
| claude-opus-5-5 | 1,898 | 1,044,899 | 266,933,115 | 3,880,987 | 271,860,899 |
| claude-sonnet-5-5 | 182 | 80,926 | 10,447,508 | 541,917 | 11,070,533 |
| all | 6,114 | 1,600,320 | 300,963,848 | 6,393,675 | 308,963,957 |

Delegation share: lead 138,941,079 (45.0%), workers 170,022,878 (55.0%). By model: claude-fable-5-1 8.4%, claude-opus-5-5 88.0%, claude-sonnet-5-5 3.6%

| Spawn (name) | Model | Effort | First (UTC) | Last (UTC) | Tokens |
|---|---|---|---|---|---|
| lead (Opus 5.5) | claude-opus-5-5 | xhigh | 2026-10-16T07:46:49 | 2026-10-17T02:15:19 | 138,941,079 |
| VerdictVerifier-K6-FableXHigh | claude-fable-5-1 | xhigh | 2026-10-17T01:59:44 | 2026-10-17T02:12:29 | 2,435,262 |
| HarnessBuilder-OpusXHigh | claude-opus-5-5 | xhigh | 2026-10-16T08:15:36 | 2026-10-16T09:08:01 | 36,721,085 |
| VerdictVerifier-K3-FableXHigh | claude-fable-5-1 | xhigh | 2026-10-17T01:49:24 | 2026-10-17T02:02:28 | 2,424,785 |
| MicroBookCoder-OpusXHigh | claude-opus-5-5 | xhigh | 2026-10-16T08:00:13 | 2026-10-16T08:36:09 | 31,993,960 |
| DataSourceReader-OpusHigh | claude-opus-5-5 | high | 2026-10-16T07:59:53 | 2026-10-16T08:19:17 | 21,314,667 |
| F1FixApplier-SonnetMed | claude-sonnet-5-5 | medium | 2026-10-16T08:49:57 | 2026-10-16T08:50:39 | 377,319 |
| ForwardRunnerCoder-OpusXHigh | claude-opus-5-5 | xhigh | 2026-10-16T08:00:33 | 2026-10-16T08:19:52 | 8,799,199 |
| HarnessReviewer-FableXHigh | claude-fable-5-1 | xhigh | 2026-10-16T08:40:40 | 2026-10-16T09:10:27 | 7,287,736 |
| ListReviewer-FableXHigh | claude-fable-5-1 | xhigh | 2026-10-16T09:20:22 | 2026-10-16T09:43:00 | 4,371,839 |
| RegReviewer-FableXHigh | claude-fable-5-1 | xhigh | 2026-10-16T08:36:21 | 2026-10-16T08:55:33 | 3,943,562 |
| VerdictVerifier-K5-FableXHigh | claude-fable-5-1 | xhigh | 2026-10-17T01:32:26 | 2026-10-17T01:43:39 | 2,471,132 |
| VerdictVerifier-K8-FableXHigh | claude-fable-5-1 | xhigh | 2026-10-17T01:35:10 | 2026-10-17T01:49:55 | 3,098,209 |
| CarverReader-OpusHigh | claude-opus-5-5 | high | 2026-10-16T07:59:34 | 2026-10-16T08:08:21 | 10,371,337 |
| HarnessGapAudit-OpusXHigh | claude-opus-5-5 | high | 2026-10-16T07:53:52 | 2026-10-16T08:11:29 | 23,719,572 |
| TierAFactsK6K8-SonnetMed | claude-sonnet-5-5 | high | 2026-10-16T07:53:54 | 2026-10-16T07:56:28 | 2,400,102 |
| TierAFactsK5K3-SonnetMed | claude-sonnet-5-5 | high | 2026-10-16T07:53:51 | 2026-10-16T07:57:50 | 3,488,024 |
| DecisionsScan-SonnetMed | claude-sonnet-5-5 | high | 2026-10-16T07:53:57 | 2026-10-16T07:58:38 | 4,805,088 |
