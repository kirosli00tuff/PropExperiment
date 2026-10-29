# Stage E.34 session cost (tokens from transcript message.usage; times PDT)

Window: 2026-10-29T18:50:00Z <= ts < 2026-10-29T22:50:05Z UTC (10-29 11:50:00 to 10-29 15:50:05 PDT). Scan keeps each message's final usage (per-field max over its records). Token counts only, never estimated.

## 1. Tokens per model, whole stage (lead + workers, three sessions)

| Model | Messages | Input | Output | Cache read | Cache creation | Total |
|---|---|---|---|---|---|---|
| claude-fable-5-1 | 71 | 2,194 | 260,904 | 10,388,121 | 1,154,411 | 11,805,630 |
| claude-haiku-5-5 | 86 | 172 | 122,945 | 10,913,137 | 403,808 | 11,440,062 |
| claude-opus-5-5 | 523 | 1,080 | 778,566 | 94,012,384 | 2,177,830 | 96,969,860 |
| claude-sonnet-5-5 | 58 | 118 | 78,022 | 8,166,627 | 297,211 | 8,541,978 |
| all | 738 | 3,564 | 1,240,437 | 123,480,269 | 4,033,260 | 128,757,530 |

## 2. One line per worker spawn

| Session | Role (Agent description) | Agent file | Requested model | Model(s) in transcript | First (PDT) | Last (PDT) | Msgs | Input | Output | Cache read | Cache creation | Total |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | MathReaderM1-OpusHigh | worker-high | opus | claude-opus-5-5 | 10-29 12:10:30 | 10-29 12:21:58 | 62 | 126 | 62,237 | 9,207,452 | 225,107 | 9,494,922 |
| 1 | MathReaderM2-OpusHigh | worker-high | opus | claude-opus-5-5 | 10-29 12:10:31 | 10-29 12:28:19 | 95 | 192 | 83,765 | 17,957,525 | 273,604 | 18,315,086 |
| 1 | MathReaderM3-OpusHigh | worker-high | opus | claude-opus-5-5 | 10-29 12:10:34 | 10-29 12:23:18 | 75 | 154 | 63,811 | 12,012,927 | 235,273 | 12,312,165 |
| 1 | MathReaderM4-OpusHigh | worker-high | opus | claude-opus-5-5 | 10-29 12:10:36 | 10-29 12:16:45 | 34 | 70 | 37,007 | 3,778,882 | 159,132 | 3,975,091 |
| 1 | DataFacts-SonnetHigh | worker-high | sonnet | claude-sonnet-5-5 | 10-29 12:10:39 | 10-29 12:23:38 | 55 | 112 | 76,579 | 8,030,086 | 221,063 | 8,327,840 |
| 1 | ExposureExtract-HaikuMed | worker-medium | haiku | claude-haiku-5-5 | 10-29 12:10:41 | 10-29 12:15:42 | 36 | 72 | 60,849 | 4,569,471 | 213,966 | 4,844,358 |
| 1 | CodeExtract-HaikuMed | worker-medium | haiku | claude-haiku-5-5 | 10-29 12:15:56 | 10-29 12:22:08 | 50 | 100 | 62,096 | 6,343,666 | 189,842 | 6,595,704 |
| 1 | ExposureAuditor-OpusHigh | worker-high | opus | claude-opus-5-5 | 10-29 12:22:27 | 10-29 12:29:42 | 31 | 62 | 42,286 | 4,039,675 | 174,496 | 4,256,519 |
| 2 | MathReviewer-FableXHigh | worker-xhigh | fable | claude-fable-5-1 | 10-29 14:02:22 | 10-29 14:22:45 | 19 | 582 | 97,739 | 2,872,394 | 306,243 | 3,276,958 |
| 2 | ComputeRef-OpusHigh | worker-high | opus | claude-opus-5-5 | 10-29 14:02:31 | 10-29 14:08:00 | 23 | 48 | 32,826 | 2,316,897 | 139,140 | 2,488,911 |
| 2 | ProtocolReviewer-FableXHigh | worker-xhigh | fable | claude-fable-5-1 | 10-29 14:13:31 | 10-29 14:30:19 | 26 | 809 | 78,186 | 4,070,794 | 584,575 | 4,734,364 |
| 3 | FixVerifier-FableXHigh | worker-xhigh | fable | claude-fable-5-1 | 10-29 15:28:00 | 10-29 15:45:12 | 26 | 803 | 84,979 | 3,444,933 | 263,593 | 3,794,308 |
| 3 | CostTally-SonnetMed | worker-medium | sonnet | claude-sonnet-5-5 | 10-29 15:49:53 | 10-29 15:50:05 | 3 | 6 | 1,443 | 136,541 | 76,148 | 214,138 |

Worker spawns listed: 13. Distinct models seen in worker transcripts: claude-fable-5-1, claude-haiku-5-5, claude-opus-5-5, claude-sonnet-5-5.

## 3. Per session

| Session | Id | First record (PDT) | Last record (PDT) | Wall-clock | Lead tokens | Worker spawns | Worker tokens | Session total |
|---|---|---|---|---|---|---|---|---|
| 1 | 61379f35 | 10-29 11:52:37 | 10-29 12:30:55 | 0h38m | 18,845,495 | 8 | 68,121,685 | 86,967,180 |
| 2 | 92545abe | 10-29 13:50:52 | 10-29 14:31:07 | 0h40m | 14,448,452 | 3 | 10,500,233 | 24,948,685 |
| 3 | 4b0394a9 | 10-29 15:09:49 | 10-29 15:50:05 | 0h40m | 12,833,219 | 2 | 4,008,446 | 16,841,665 |

Idle gaps >= 30 min inside a session (union of lead and subagent timestamps), candidate pauses:
- none

Gaps between sessions (last record of one to first record of the next, PDT):
- session 1 to 2: 10-29 12:30:55 to 10-29 13:50:52, 80 min
- session 2 to 3: 10-29 14:31:07 to 10-29 15:09:49, 39 min

## 4. Delegation share

| Group | Tokens | Share of all tokens |
|---|---|---|
| lead (three sessions) | 46,127,166 | 35.8% |
| workers (all spawns) | 82,630,364 | 64.2% |

| Model tier | Lead tokens | Worker tokens | Total | Share of all tokens |
|---|---|---|---|---|
| fable | 0 | 11,805,630 | 11,805,630 | 9.2% |
| haiku | 0 | 11,440,062 | 11,440,062 | 8.9% |
| opus | 46,127,166 | 50,842,694 | 96,969,860 | 75.3% |
| sonnet | 0 | 8,541,978 | 8,541,978 | 6.6% |

Note: cache-read tokens dominate the totals; the shares are by raw token count, not by cost.
