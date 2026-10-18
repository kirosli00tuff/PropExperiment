# Stage E.25 STATE (untapped sources research pass)

Prompt: docs/prompts/STAGE_E.25.md. Lead: Opus 5.5 xhigh, ultracode on. Session 37fc9660-82d1-49fd-be83-50b822ab0a5b.
Times PDT (America/Vancouver), from `date`. Work ends 07:00; return written by 07:30.
On resume: read this file first, skip finished tasks.

## Task status

| # | Task | Owner | Status | Start | End | Artifacts |
|---|---|---|---|---|---|---|
| 0 | Startup checks | lead | done | 01:27 | 01:28 | reports/stage_e25_briefs/start_checks.txt (N 538, unlocks 0, REGISTRATION 0 bytes) |
| R0a | Tested-mechanism index | MechIndexer-SonnetMed | done | 01:32 | 01:38 | reports/stage_e25_briefs/r0_mechanism_index.md (289 lines, N reconciles 538) |
| R0b | Prior sources + E.20 evidence index | PriorSources-HaikuMed | done | 01:32 | 01:34 | reports/stage_e25_briefs/r0_prior_sources.md (253 groups), r0_e20_evidence_index.md (157 rows) |
| R0 | Shared brief | lead | done | 01:29 | 01:36 | reports/stage_e25_briefs/brief_shared.md |
| R1-R13 | Topic readers | SourceReader-*-OpusHigh | running (workflow wf_67286733-e36, task w06og421o) | 01:38 | | reports/stage_e25_briefs/R<k>_*.md/.json |
| RD1-RD7 | Re-dig readers (addendum 1) | RedigReader-*-OpusHigh | running (workflow wf_a72a1974-11c, task wk10xg3ti) | 01:38 | | reports/stage_e25_briefs/RD<k>_*.md/.json |
| R14 | Podcasts with own transcripts/show notes (addendum 2) | SourceReader-Podcasts-OpusHigh | next (when a slot frees; cap 20) | | | reports/stage_e25_briefs/R14_podcasts.md/.json |
| R15 | Niche/non-US futures: evidence of intraday inefficiency (addendum 3a; academic query families) | SourceReader-NicheMarkets-OpusHigh | next (slot) | | | reports/stage_e25_briefs/R15_niche_markets.md/.json |
| R16 | Niche/non-US futures: prop firms per market, tick-data sources and costs, Canadian retail access (addendum 3b,c; firm/vendor query families) | SourceReader-NicheAccess-OpusHigh | next (slot) | | | reports/stage_e25_briefs/R16_niche_access.md/.json |
| NM1 | Near-miss extraction (addendum 4 step 1): every intraday trial failed mainly on cost, recorded gross, D8 fee/slippage split, shortfall, entry/exit type | NearMissExtractor-SonnetMed | next (slot) | | | reports/stage_e25_briefs/NM1_nearmiss_table.md/.json |
| R17 | Maker-native / passive liquidity provision and small-scale market making (addenda 5 Group B + 6a): published strategies, net returns, inventory and adverse-selection handling, retail latency/fees, predictable-flow provision | SourceReader-MakerNative-OpusHigh | next (slot; priority 1) | | | reports/stage_e25_briefs/R17_maker_native.md/.json |
| R18 | Fill-probability and queue models, adverse selection on CME, data needs, honest limit-order backtests, prop rules on passive/HF order use (addendum 6b) | SourceReader-QueueFill-OpusHigh | next (slot; priority 2) | | | reports/stage_e25_briefs/R18_queue_fill.md/.json |
| NM2 | Execution triage (addendum 4 steps 2-4 + addendum 5 groups A/B, one shared calibration slice): passive saving vs shortfall, classification, top 5, Databento data spec; after NM1, R3, R4 | ExecTriage-OpusXHigh | pending | | | reports/stage_e25_briefs/NM2_exec_triage.md |
| T1 | Triage, assign wave 2 (R19-R20, RD8+) | lead | pending | | | |
| R19-R20, RD8+ | Wave 2: deep follow-ups and re-dig | DeepReader-*/RedigReader-*-OpusHigh | pending | | | |
| S1-S3 | Synthesis | lead | pending | | | reports/stage_e25_briefs/synthesis.md |
| S4 | Review | ShortlistReviewer-FableXHigh | pending | | | reports/stage_e25_briefs/review_S4.md |
| F | Fixes | lead | pending | | | |
| Ret | Return, progress, STAGES, end checks, commit | lead | pending | | | reports/E.25_RETURN.md |

## Log
- 01:27 holdout status all_ok, unlocks_logged 0; N 538 (9 registry lines); E.24 runs in parallel (do not touch forward/, base_rules/, multiday/, harness, tests).
- WebSearch cap 1500/session (.claude/settings.json), shared by all workers.
- 01:33 user addendum 1: all research tools at full depth (Firecrawl incl. research_* paper tools, OpenAlex, Semantic Scholar, Playwright, WebSearch/WebFetch); re-dig readers in waves (max 20 at once, ~2 per domain) on E.13/E.20 sources; own return section; fold candidates into S1/S2; Open choice (user-directed).
- 01:35 .env: SEMANTIC_SCHOLAR_API_KEY length 1 (unusable) -> S2 keyless at 1 call/10 s per reader; OpenAlex via OPENALEX_EMAIL (polite pool). Values never printed.
- 01:38 wave 1 launched: R1-R13 + RD1-RD7 = 20 concurrent (available memory 5.7 GB at 01:37).
- 01:40 user addendum 2: podcasts with official transcripts/show notes on their own sites (Chat With Traders, Top Traders Unplugged, Flirting with Models, Better System Trader...), pointers only unless a guest cites a checkable public record; no YouTube transcripts by any route -> spare reader R14; Open choice (user-directed). R11 (already running) was told 'no transcript download unless terms allow'; its fetch log is checked for YouTube transcripts at triage.
- Registry '9 lines' = baseline line + r001..r008 (resolves MechIndexer's open point).
- 01:47 user addendum 3: two readers on niche and non-US futures (Eurex, ICE Europe, OSE, SGX, HKEX, INE/SHFE, thin CME, Asian hours): evidence, prop firms per market plan by plan with automation rules, tick-data sources/costs, Canadian retail access -> R15 (evidence, academic queries) and R16 (access, firm/vendor/exchange queries); Open choice (user-directed). Spare-reader ids shift: wave-2 deep follow-ups are R17-R20.
- 01:52 user addendum 4: near-miss execution triage from recorded results only (no market data): NM1 extraction (sonnet medium), NM2 analysis (opus xhigh) after R3/R4; own return section; top candidates into S1/S2; Open choice (user-directed). Prior closure to face: D.1g/C6 (TopstepX fills limits on trade-through only; SIM queue-position edges prohibited, P07).
- 01:54 user addendum 5: triage/S2 Group A (<=5 earlier against-the-move rules short by less than the passive saving) and Group B (1-3 new maker-native hypotheses with published mechanisms); exclude breakouts/momentum, gross < fees, non-cost failures; one shared calibration slice. -> R17 maker-native reader added (R3/R4 were not briefed on maker-native designs). Launch queue: NM1, R17, R14, R15, R16. Open choice (user-directed).
- 01:52 RD5 done (14 min; supports C2 stop and E20H6-T3; no sized candidate). NM1 launched 01:53 in its slot.
- 01:56 user addendum 6: two dedicated limit-order readers feeding Group B: (a) passive liquidity provision / small-scale market making -> merged into R17 (already queued for addendum 5's maker-native flows); (b) fill-probability/queue models, honest limit-order backtests, prop rules on passive/HF order use -> R18. Launch queue: R17, R18, R14, R15, R16. Open choice (user-directed).
- 01:53 R11 done (communities: 107 pointers, no sized setup). 01:55 R17 launched in its slot.
- 01:55 R10 done (practitioner; lead: Zarattini-Aziz-Barbon noise-area momentum about 4.0 bp gross, never screened; V34 dropped it as unsized). 01:57 R18 launched in its slot.
- 01:47 OpenAlex free daily IP budget exhausted (resets 17:00 PDT); 01:57 brief section 7 updated: OpenCitations + Crossref + S2 keyless + Firecrawl for forward citations.
- 01:57 R13, RD7, R12 done. 01:59 R14, R15, R16 launched in their slots (queue empty).

## RESUME POINT (usage limit reached, ~02:00 PDT)
- Done on disk: R0 (brief, index, prior sources), RD5, R11, R10, R13, RD7, R12 (md+json). candidates_raw.md first pass (20 candidates from 6 readers; R9 json had 0 candidates at 02:00, still running).
- Running at the cut (may have been killed): workflow wf_67286733-e36 (R1-R9 still open), workflow wf_a72a1974-11c (RD1-RD4, RD6 open), agents NM1, R17, R18, R14, R15, R16. Monitor by1y8mzm3.
- On resume: (1) for each reader, check its json 'finished_utc' and md section 10 on disk before re-spawning; re-spawn only unfinished ones (resume workflows with resumeFromRunId, completed agents cached); (2) T1 triage: wave-2 second readers on top leads (R10-C1 Zarattini noise-area momentum, R12-C1/C2 monthly-expiry effects, R12-C3, R13-C1) and RD8 (E.20 planning-brief leads); (3) NM2 ExecTriage-OpusXHigh after NM1, R3, R4, R17, R18 (groups A/B, one calibration slice, D.1g/C6 closure); (4) S1-S3 lead; (5) S4 ShortlistReviewer-FableXHigh; (6) return, progress, STAGES, end checks (reports/stage_e25_briefs/checks.sh > end_checks.txt), cost tables, commit 'Stage E.25 untapped sources research' (stage files only; no E.24 file staged; no push).
- E.24 pytest held ~6.9 GB at 01:58 (available 2.45 GB): check free -m before relaunching anything.

## Resume 06:11 PDT (pause 02:01-06:10, usage limit; not work time)
- Usage limit cut every running worker at 01:58-02:01. Complete: R9 R10 R11 R12 R13 RD4 RD5 RD7. Partial md on disk (read as left): R3 (md+json), R4, R6, R7, RD1 (md+json), RD2 (md+json). Thin: R1, R2, R5, R8, RD3. None: RD6.
- 06:12 resumed by SendMessage with a 06:33 deadline: NM1, R14, R15, R16, R17, R18. Workflow agents cannot be resumed: fresh R1 and R5 spawned 06:13 (deadline 06:36), reusing partial files.
- Not resumed (time and usage; wave 1 burned the 5-hour window in ~20 min): R2, R8, RD3, RD6; wave 2 (R19-R20, RD8) dropped; NM2 folded into the lead's S2 (Groups A/B).
- Plan: S1-S3 by 06:50; S4 Fable 06:50-07:10; fixes and return by 07:30.

## 06:18 planner-approved window change
- New times (planner message 06:18 PDT): work until 09:00 PDT, return by 09:30 PDT; do not cut readers short.
- 06:15-06:17 done: NM1, R17, R15, R5 (rerun), R18, R1 (rerun), R14, R16 (several returned early to the old 06:33 deadline; partial lists in their section 10).
- 06:19 synthesis.md draft v1 written (S1 22 rows, S2 C1-C5 with power from s2_power.py/.out, Group A empty, Group B B1).
- Next: wave 2 (workflow, 10 agents): DF1 noise-area momentum second reader, DF2 3rd-Friday spike second reader, DF3 Treasury pre-refunding/pre-FOMC second reader, R6 finish, R2 0DTE vendor/data costs, R8 prop outcomes, RD3 energy/metals re-dig, RD6 E.13 info-sources re-dig, RD8 E.20 planning-brief leads re-dig, NM2 execution triage (opus xhigh). Then S1-S3 v2, S4 Fable, return.
- 06:22 wave 2 launched (workflow wf_d3a0c18c-d92, task wxhrocru3): DF1 DF2 DF3 R6 R2 R8 RD3 RD6 RD8 (opus high) + NM2 (opus xhigh); finish by 08:00. Memory 9.7 GB available at 06:20.

## Resume 11:15 PDT (second usage limit ~06:35-11:10; laptop reboot ~10:50; not work time)
- Planner 11:16: work until 15:00 PDT, return by 15:30 PDT; at most 6 workers at once; finish started items first.
- On disk after wave 2: done R2, R6 (md+json), RD8 (md+json, complete). Partial: DF3 (md complete, no json), R8 (json complete, md stub), RD3 (md partial), RD6 (md skeleton), DF1/DF2/NM2 (pages only, no md).
- Wave 3 (11:18, Agent tool, 6 at once): DF1, DF2 (opus high), NM2 (opus xhigh), RD3, RD6 (opus high), Finisher (sonnet medium: DF3 json from md, R8 md from json). Target 12:15.
- Then: synthesis v2 (lead), S4 ShortlistReviewer-FableXHigh, fixes, return, cost tables, commit.
- 11:19 FileFinisher done (DF3 json, R8 md). 11:23 RD6 done (supports E.13 ranking and C1/C1b; R6-C3 FOMC pre-announcement reversal noted; no new sized candidate).
- 11:24 DF1 done: C1 numbers check (trade count ambiguous: replications 0.9/day); post-publication S&P side <= 0 in every test; NQ side VigorTas ~41 MNQ ticks t 1.37 (pointer); RW no longer blind for C1 (third-party results cover 2025-26); worst DD at 1 MNQ $3.4-4.25k > 50K MLL $2,000.
- 11:24 RD3 done: supports K4-ngpre-01, K5-fomc-01, K4-eia*, PM fix, C1/C1b, V38, V39; weakens K4-apipre-01 slightly (Alturki-Kurov 4.5 MCL ticks vs 4.75 hurdle); RD3-C1 own construction (not published), RD3-C2 under hurdle.
- 11:28 DF2 done (ES table verified; run-up from 17:00 CT +12.75 bp, decayed to 1.6-4.2 bp after 2015; reversal 14.8-17.6 bp after 2015, 70% in 08:30-09:00 CT, quarterly-heavy; 15 monthly expiries in RW, 5 quarterly). s2_power.py sensitivity rows added. synthesis.md v2 written (S1 27 rows, S2 C1-C5, Groups A/B, re-dig table, prop landscape, S3). NM2 pending.
- 11:29 DF2 done (ES table verified; run-up from 17:00 CT +12.75 bp, decayed to 1.6-4.2 bp after 2015; reversal 14.8-17.6 bp after 2015, 70% in 08:30-09:00 CT, quarterly-heavy; 15 monthly expiries in RW, 5 quarterly). s2_power.py sensitivity rows added. synthesis.md v2 written. NM2 pending.
- 11:30 NM2 done (Group A empty confirmed; passive saving per side under trade-through MNQ +0.36..+0.68, MES -0.57..+0.06, ZN -0.78..0; calibration slice to 2024-02-29). synthesis v2 corrected and final for review. S4 ShortlistReviewer-FableXHigh launched (target 13:15).
- 11:31 return parts drafted: ret_events.md, ret_decisions.md, ret_sources.md (27 readers). Waiting for S4.
- 11:45 S4 review done: BLOCK (2), SHOULD FIX (10), NOTE (10); 11:48 all applied (synthesis v3, s2_power v2, ret_decisions); ret_verification.md written; Fable re-check of fixes requested (resume).
- 11:51 Fable re-check READY (returned by 11:51 per date; its own note says 11:55); 11:51 its 4 NOTEs applied. Next: end checks, cost, progress, STAGES, assemble, commit.
- 11:53 STAGES.md line added. Next: progress entry, end checks, final cost, assemble, commit.
- 11:53 progress_entry.md drafted. Next: end checks, final cost, assemble, append progress, commit.

## FINAL (11:55 PDT)
- Done: S1-S3 (synthesis v3), S4 (BLOCK -> fixed -> re-check READY), return reports/E.25_RETURN.md (assembled), progress.md entry, docs/STAGES.md line, end checks (end_checks.txt: holdout all_ok, unlocks 0, REGISTRATION 0 bytes, ledgers unchanged, N 538).
- No worker or background shell running. Commit "Stage E.25 untapped sources research" (stage files only; no push).
