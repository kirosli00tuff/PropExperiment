## 8. Session cost

Computed at the end from the transcripts (reports/stage_e25_briefs/make_cost.py: the lead's .jsonl and every
subagent transcript under subagents/**, workflow agents included; each message's final usage). Times PDT.
Pauses are their own rows and excluded from work time. These are token counts, not plan-credit percentages.

### Final ETA table (actuals; the initial estimate in the last column)

| # | Task or spawn | Owner / agent | Model | Effort | Start | End | Minutes | Tokens | Status, deviations | Initial estimate |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0 Startup checks | lead | opus | xhigh | 01:27 | 01:28 | 1 | in the lead total | done | done 01:28 |
| 2 | R0 shared brief | lead | opus | xhigh | 01:29 | 01:36 | 7 | in the lead total | done | 25 min, to 02:05 |
| 3 | Wave 1 launch, addenda 1-6 handling, slot launches | lead | opus | xhigh | 01:37 | 02:01 | 24 | in the lead total | cut by the usage limit at 02:01 | R1-R13 60 min, to 03:10 |
| 4 | PAUSE (usage limit) | - | - | - | 02:01 | 06:10 | 249 | - | not work time | - |
| 5 | Resume, synthesis v1, power script, wave 2 launch | lead | opus | xhigh | 06:10 | 06:35 | 25 | in the lead total | cut by the usage limit at about 06:35 | T1 triage 20 min, R14-R20 60 min |
| 6 | PAUSE (usage limit; laptop reboot about 10:50) | - | - | - | 06:35 | 11:15 | 280 | - | not work time | - |
| 7 | Resume, wave 3 launch, synthesis v2, merges | lead | opus | xhigh | 11:15 | 11:30 | 15 | in the lead total | done | S1-S3 60 min, to 05:30 |
| 8 | S4 running: return parts drafted; review fixes, re-check | lead | opus | xhigh | 11:30 | 11:52 | 22 | in the lead total | done | F 20 min, to 06:35 |
| 9 | Cost, progress, STAGES, end checks, assembly, commit | lead | opus | xhigh | 11:52 | 11:54 | 2 | in the lead total | done | Ret 35 min, to 07:10 |
| 10 | spawn | MechIndexer-SonnetMed | sonnet-5-5 | medium | 01:31 | 01:37 | 6 | 5,834,390 | done | - |
| 11 | spawn | PriorSources-HaikuMed | haiku-5-5 | medium | 01:31 | 01:33 | 2 | 2,042,557 | done | - |
| 12 | spawn | SourceReader-0DTEAcademic-OpusHigh | opus-5-5 | high | 01:38 | 02:01 | 23 | 10,678,059 | cut by the usage limit about 01:58 (partial files on disk) | - |
| 13 | spawn | SourceReader-0DTEVendor-OpusHigh | opus-5-5 | high | 01:38 | 01:58 | 20 | 14,004,235 | cut by the usage limit about 01:58 (partial files on disk) | - |
| 14 | spawn | SourceReader-VolumeTradeSide-OpusHigh | opus-5-5 | high | 01:38 | 01:58 | 20 | 14,593,310 | cut by the usage limit about 01:58 (partial files on disk) | - |
| 15 | spawn | SourceReader-PropRules-OpusHigh | opus-5-5 | high | 01:38 | 01:58 | 20 | 15,820,818 | done | - |
| 16 | spawn | SourceReader-Communities-OpusHigh | opus-5-5 | high | 01:38 | 01:53 | 15 | 8,934,782 | done | - |
| 17 | spawn | SourceReader-RegimeFilters-OpusHigh | opus-5-5 | high | 01:38 | 01:57 | 19 | 15,697,314 | done | - |
| 18 | spawn | SourceReader-PropOutcomes-OpusHigh | opus-5-5 | high | 01:38 | 01:58 | 20 | 14,866,390 | cut by the usage limit about 01:58 (partial files on disk) | - |
| 19 | spawn | SourceReader-OrderFlow-OpusHigh | opus-5-5 | high | 01:38 | 01:59 | 21 | 17,703,698 | cut by the usage limit about 01:58 (partial files on disk) | - |
| 20 | spawn | SourceReader-News-OpusHigh | opus-5-5 | high | 01:38 | 01:59 | 21 | 14,396,977 | cut by the usage limit about 01:58 (partial files on disk) | - |
| 21 | spawn | SourceReader-SchedEvents-OpusHigh | opus-5-5 | high | 01:38 | 01:59 | 21 | 27,824,773 | cut by the usage limit about 01:58 (partial files on disk) | - |
| 22 | spawn | SourceReader-LiveRecords-OpusHigh | opus-5-5 | high | 01:38 | 02:00 | 22 | 11,733,083 | cut by the usage limit about 01:58 (partial files on disk) | - |
| 23 | spawn | SourceReader-LeadLag-OpusHigh | opus-5-5 | high | 01:38 | 01:57 | 19 | 17,598,648 | done | - |
| 24 | spawn | SourceReader-Practitioner-OpusHigh | opus-5-5 | high | 01:38 | 01:55 | 17 | 12,715,339 | done | - |
| 25 | spawn | RedigReader-EquityIndex-OpusHigh | opus-5-5 | high | 01:38 | 01:58 | 20 | 14,557,908 | cut by the usage limit about 01:58 (partial files on disk) | - |
| 26 | spawn | RedigReader-Rates-OpusHigh | opus-5-5 | high | 01:38 | 01:59 | 21 | 17,691,494 | cut by the usage limit about 01:58 (partial files on disk) | - |
| 27 | spawn | RedigReader-TrendCarry-OpusHigh | opus-5-5 | high | 01:38 | 01:57 | 19 | 17,923,544 | done | - |
| 28 | spawn | RedigReader-EnergyMetals-OpusHigh | opus-5-5 | high | 01:38 | 01:59 | 21 | 11,204,753 | cut by the usage limit about 01:58 (partial files on disk) | - |
| 29 | spawn | RedigReader-FXAgs-OpusHigh | opus-5-5 | high | 01:38 | 01:58 | 20 | 13,617,317 | done | - |
| 30 | spawn | RedigReader-InfoSources-OpusHigh | opus-5-5 | high | 01:38 | 01:58 | 20 | 12,142,629 | cut by the usage limit about 01:58 (partial files on disk) | - |
| 31 | spawn | RedigReader-DealerGamma-OpusHigh | opus-5-5 | high | 01:38 | 01:52 | 14 | 9,668,684 | done | - |
| 32 | spawn | NearMissExtractor-SonnetMed | sonnet-5-5 | medium | 01:53 | 06:12 | 259 | 8,567,134 | cut by the usage limit about 01:58; resumed by message 06:12; done | - |
| 33 | spawn | SourceReader-MakerNative-OpusHigh | opus-5-5 | high | 01:54 | 06:15 | 261 | 4,612,407 | cut by the usage limit about 01:58; resumed by message 06:12; done | - |
| 34 | spawn | SourceReader-QueueFill-OpusHigh | opus-5-5 | high | 01:56 | 06:16 | 260 | 3,881,034 | cut by the usage limit about 01:58; resumed by message 06:12; done | - |
| 35 | spawn | SourceReader-Podcasts-OpusHigh | opus-5-5 | high | 01:57 | 06:17 | 260 | 3,260,228 | cut by the usage limit about 01:58; resumed by message 06:12; done | - |
| 36 | spawn | SourceReader-NicheMarkets-OpusHigh | opus-5-5 | high | 01:58 | 06:16 | 258 | 2,541,068 | cut by the usage limit about 01:58; resumed by message 06:12; done | - |
| 37 | spawn | SourceReader-NicheAccess-OpusHigh | opus-5-5 | high | 01:58 | 06:17 | 259 | 3,783,035 | cut by the usage limit about 01:58; resumed by message 06:12; done | - |
| 38 | spawn | SourceReader-0DTEAcademic-OpusHigh | opus-5-5 | high | 06:13 | 06:17 | 4 | 2,664,791 | done | - |
| 39 | spawn | SourceReader-News-OpusHigh | opus-5-5 | high | 06:13 | 06:16 | 3 | 1,238,405 | done | - |
| 40 | spawn | DeepReader-NoiseAreaMomentum-OpusHigh | opus-5-5 | high | 06:21 | 06:33 | 12 | 7,773,021 | cut by the usage limit about 06:35 (partial files on disk) | - |
| 41 | spawn | ExecTriage-OpusXHigh | opus-5-5 | xhigh | 06:21 | 06:33 | 12 | 10,744,732 | cut by the usage limit about 06:35 (partial files on disk) | - |
| 42 | spawn | DeepReader-TreasuryDrifts-OpusHigh | opus-5-5 | high | 06:21 | 06:35 | 14 | 15,123,531 | cut by the usage limit about 06:35 (partial files on disk) | - |
| 43 | spawn | DeepReader-ThirdFriday-OpusHigh | opus-5-5 | high | 06:21 | 06:33 | 12 | 11,889,228 | cut by the usage limit about 06:35 (partial files on disk) | - |
| 44 | spawn | SourceReader-SchedEvents-OpusHigh | opus-5-5 | high | 06:21 | 06:30 | 9 | 7,929,184 | done | - |
| 45 | spawn | SourceReader-PropOutcomes-OpusHigh | opus-5-5 | high | 06:21 | 06:33 | 12 | 9,649,842 | cut by the usage limit about 06:35 (partial files on disk) | - |
| 46 | spawn | RedigReader-InfoSources-OpusHigh | opus-5-5 | high | 06:21 | 06:33 | 12 | 8,554,550 | cut by the usage limit about 06:35 (partial files on disk) | - |
| 47 | spawn | RedigReader-EnergyMetals-OpusHigh | opus-5-5 | high | 06:21 | 06:33 | 12 | 12,456,717 | cut by the usage limit about 06:35 (partial files on disk) | - |
| 48 | spawn | RedigReader-E20Planning-OpusHigh | opus-5-5 | high | 06:21 | 06:33 | 12 | 8,704,329 | cut by the usage limit about 06:35 after its md and json were complete | - |
| 49 | spawn | SourceReader-0DTEVendor-OpusHigh | opus-5-5 | high | 06:21 | 06:32 | 11 | 10,557,795 | done | - |
| 50 | spawn | DeepReader-NoiseAreaMomentum-OpusHigh | opus-5-5 | high | 11:16 | 11:24 | 8 | 4,697,821 | done | - |
| 51 | spawn | DeepReader-ThirdFriday-OpusHigh | opus-5-5 | high | 11:16 | 11:25 | 9 | 7,074,534 | done | - |
| 52 | spawn | ExecTriage-OpusXHigh | opus-5-5 | xhigh | 11:16 | 11:29 | 13 | 7,335,560 | done | - |
| 53 | spawn | RedigReader-EnergyMetals-OpusHigh | opus-5-5 | high | 11:16 | 11:24 | 8 | 6,034,214 | done | - |
| 54 | spawn | RedigReader-InfoSources-OpusHigh | opus-5-5 | high | 11:16 | 11:23 | 7 | 4,989,646 | done | - |
| 55 | spawn | FileFinisher-SonnetMed | sonnet-5-5 | medium | 11:16 | 11:17 | 1 | 590,206 | done | - |
| 56 | spawn | ShortlistReviewer-FableXHigh | fable-5-1 | xhigh | 11:30 | 11:51 | 21 | 3,721,751 | done | - |

| Cumulative | whole stage | lead + 47 spawns | | | 01:27 | 11:54 | wall 627 (pauses 529; work 98) | 527,784,311 (lead 58,158,846; workers 469,625,465) | | initial estimate: 01:28-07:10 (342 min of work) |

### Tokens per model

| Model | Input | Output | Cache read | Cache creation | Total |
|---|---|---|---|---|---|
| claude-fable-5-1 | 484 | 86,100 | 3,319,695 | 315,472 | 3,721,751 |
| claude-haiku-5-5 | 38 | 19,220 | 1,888,042 | 135,257 | 2,042,557 |
| claude-opus-5-5 | 6,028 | 2,323,698 | 494,675,807 | 10,022,740 | 507,028,273 |
| claude-sonnet-5-5 | 188 | 102,092 | 14,090,285 | 799,165 | 14,991,730 |
| all | 6,738 | 2,531,110 | 513,973,829 | 11,272,634 | 527,784,311 |

Delegation share: lead 58,158,846 (11.0%), workers 469,625,465 (89.0%). By model: claude-fable-5-1 0.7%, claude-haiku-5-5 0.4%, claude-opus-5-5 96.1%, claude-sonnet-5-5 2.8%

One line per worker spawn (agent file by effort: worker-medium, worker-high, worker-xhigh): the spawn rows of the
table above and section 4. The lead's last messages after the count (assembly and commit) are not included.

