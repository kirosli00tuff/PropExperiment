# E.25 open choices (lead's running log; copied into the return, section 6)

1. **User-directed change, addendum 1 (01:33 PDT).** The user's planner addendum added every research tool
   at full depth (Firecrawl search, scrape and research_* paper tools; OpenAlex; Semantic Scholar; Playwright;
   WebSearch/WebFetch) and re-dig readers in waves (at most 20 at once, about 2 per domain) on the sources E.13
   and E.20 cited, reported in their own return section and folded into S1/S2. Applied as written.
2. **User-directed change, addendum 2 (01:40 PDT).** Podcasts that publish official transcripts or show notes
   on their own sites, read under each site's terms, pointers only unless a guest cites a checkable public
   record, no YouTube transcripts by any route. R11 was already running inside a workflow and cannot take new
   instructions, so the family went to a spare reader (R14, SourceReader-Podcasts-OpusHigh), launched when a
   wave-1 slot freed (the cap of 20 was full). R11's fetch log is checked for any YouTube transcript.
3. **Semantic Scholar without a key.** SEMANTIC_SCHOLAR_API_KEY in .env has length 1 (checked by length only,
   value never printed), so it is unusable; readers call the public API keyless at most once per 10 s and fall
   back to OpenAlex (polite pool, OPENALEX_EMAIL read into the environment, never echoed).
4. **MES cost in the hurdle table.** MES is not in the frozen D8 table (MES closed after Stage D and enters
   Stage E only as a leg). The brief uses the Stage D MES model (sim/costs.py: $1.22 commission + about 0.53
   tick half-spread per side at 1 lot, sim/slippage_calibration.json), about 2.0 ticks or $2.53 per round
   trip, labelled as such. MNQ, the D8 vehicle, is the primary equity-index hurdle.
5. **"Unread research window".** The Stage E cluster screens (E.3-E.9) and D.1 read the research window
   2025-04-01..2026-06-19 for their own members. The brief reads the prompt's "unread" as: no new hypothesis's
   outcome has been computed on it (V42 keeps intraday registered reads of it possible). Overlap of a new
   rule's trades with earlier members' trades is flagged in S1.
6. **Guardrail quoting.** `git status --short` shows no tracked change at the start; its 1,271 untracked lines
   (raw pages of earlier stages) are counted, not listed, as E.23 did. Both ledgers are quoted: the spend ledger
   (line count, sha256) and the trial ledger (line count, sha256, N from `screening.trial_registry status`).
7. **R0 extraction delegated.** The prompt makes R0 the lead's. The lead wrote the brief (costs, prop rules,
   data, family-level overlap list) and delegated two extractions it feeds: the mechanism index
   (MechIndexer-SonnetMed, a multi-source join) and the prior-sources and E.20 evidence lists
   (PriorSources-HaikuMed). The lead spot-checked the index's N reconciliation (sums to 538; the registry's
   "9 lines" are the baseline line plus r001-r008).
8. **Readers run as dynamic workflows.** Ultracode is on, so wave 1 ran as two parallel workflows (13 topic
   readers; 7 re-dig readers), each agent at model opus, effort high, agent type worker-high, labelled with its
   CLAUDE.md role name. Two workflows keep each under the per-workflow concurrency cap of 16.
9. **Re-dig split.** Wave 1 re-dig readers were split by the E.20 product files' asset classes (equity; rates;
   energy and metals; FX, grains and livestock) and by E.13's three source families (dealer gamma; other
   information sources; trend and carry). E.10's sources (142 groups) were not re-dug in wave 1: the addendum
   names E.13 and E.20.
10. **User-directed change, addendum 3 (01:47 PDT).** Two readers on niche and non-US futures markets. The
    lead split them by query family: R15 (academic evidence of intraday or short-horizon inefficiency on Eurex,
    ICE Europe, OSE, SGX, HKEX, INE/SHFE, thin CME contracts and CME during Asian hours) and R16 (firm, vendor and
    exchange pages: which prop firms allow each market plan by plan with automation rules; tick-data sources and
    published costs per venue; retail access for a Canadian resident). R16 coordinates with R9 on prop-firm
    domains (grep R9's saved pages before fetching). Both queue for free slots under the cap of 20, after R14.
    Spare-reader numbering shifts: wave-2 deep follow-ups are R17-R20.
11. **User-directed change, addendum 4 (01:52 PDT).** Near-miss execution triage from recorded results only.
    The lead split it into an extraction (NM1, NearMissExtractor-SonnetMed: the trial list, recorded gross, the
    D8 fee and slippage split, the shortfall, entry and exit types as written) and an analysis (NM2,
    ExecTriage-OpusXHigh: passive-execution savings against each shortfall using R3/R4's fill-rate and
    adverse-selection evidence, the classification, a top 5 and the Databento data spec), run after R3 and R4.
    The lead rules on what enters S1/S2. The prior closure of passive execution (D.1g/C6: TopstepX fills limits
    only on trade-through; edges resting on SIM fill mechanics are prohibited, P07) is part of NM2's brief and
    of every ranking.
12. **User-directed change, addendum 5 (01:54 PDT).** The triage and S2 keep Group A (up to 5 earlier rules
    that enter against the move and fell short by less than the realistic passive saving) and Group B (1-3 new
    maker-native hypotheses with a published mechanism), excluding breakouts and momentum entries, rules whose
    gross does not cover fees and rules that failed on non-cost grounds, with one shared calibration slice. R3
    and R4 were briefed before this addendum and not on maker-native designs, so the lead added a dedicated
    reader, R17 (SourceReader-MakerNative-OpusHigh), whose output feeds Group B; NM2 builds both groups.
    Launch order under the cap of 20: NM1 (it gates NM2), R17, then R14, R15, R16.
13. **User-directed change, addendum 6 (01:56 PDT).** Two dedicated limit-order readers feeding Group B. R17,
    already queued for addendum 5's maker-native hypotheses, took addendum 6(a) (passive liquidity provision and
    small-scale market making: published strategies, net returns, inventory and adverse-selection handling,
    what survives at retail latency and fees), since the two briefs are one query family. R18
    (SourceReader-QueueFill-OpusHigh) took 6(b) (fill-probability and queue models, adverse selection measured
    on CME or similar futures, data needed, honest limit-order backtest methods, and each prop firm's rules on
    passive or high-frequency order use). New launch order under the cap: R17, R18, R14, R15, R16 (NM1 launched
    01:53 in RD5's slot).
14. **OpenAlex exhausted at 01:47 PDT.** OpenAlex's free daily budget for the machine's IP ran out at 01:46-01:47
    PDT (resets at midnight UTC); the mailto polite pool no longer lifts that cap. The lead added a dated note to
    the shared brief at 01:57: no further OpenAlex calls; forward citations through OpenCitations (free, by DOI),
    Crossref metadata, Semantic Scholar keyless, Firecrawl's related-papers tool and search results. Readers
    already running log the gap and fall back per the brief's rule; a gap is never reported as absence.
15. **Usage-limit cut and scope at resume (06:11 PDT).** The 5-hour usage window ran out at 01:58-02:01 PDT, about
    20 minutes after wave 1's 20 readers started (Stage E.24 shares the account); every running worker stopped.
    The pause (02:01-06:10) is not work time. The prompt's clock was kept (work to 07:00, return by 07:30), so the
    lead resumed only what fits: NM1, R14-R18 by message (06:33 deadline) and fresh R1 and R5 (workflow agents
    cannot be resumed; 06:36 deadline), all told the tool state. R3, R4, R6, R7, RD1, RD2 had substantial partial
    files and are read as left (marked "cut at about 01:58" wherever cited). R2, R8, RD3 and RD6 were not resumed
    (thin partials; R1 and R9 cover the nearest ground), and wave 2 (deep follow-ups R19-R20 and RD8) was dropped.
    NM2 (the execution-triage analysis) was folded into the lead's S2, which owns the shortlist anyway.
16. **Tool exhaustion during wave 1.** Firecrawl's credits ran out at 08:43-08:47 UTC (01:43-01:47 PDT) and OpenAlex's
    daily IP budget at 08:46-08:47 UTC; Playwright's Chrome is not installed (R9). Readers logged each gap; no gap
    is reported as absence.
17. **Planner-approved window change (06:18 PDT).** The planner moved the end of work to 09:00 PDT and the return to
    09:30 PDT, replacing the prompt's 07:00/07:30, and asked that no reader be cut short. The readers resumed at
    06:12 with a 06:33 deadline (choice 15) had already returned by 06:17 with partial lists; with the new window the
    lead ran a second wave for the remaining work (choice 18) instead of re-opening each of them.
18. **Wave 2 composition (06:22 PDT).** With the extended window the lead ran one workflow of 10: three second
    readers on the shortlist (DF1 noise-area momentum, DF2 the 3rd-Friday spike, DF3 the two Treasury drifts; the
    prompt's "second reader on any candidate ranked in the top five"), R6, R2 and R8 finished from their partial
    files, re-digs RD3, RD6 and RD8 (E.20's planning-brief leads), and NM2 (the execution triage at opus xhigh,
    checking the lead's draft Groups A/B). R3, R4, R7, RD1 and RD2 were not rerun: their partial files are
    substantive and are cited as cut. R1, R5, R14, R15, R16 and R18 returned early to the old deadline; their
    unfinished lists stand in their section 10. Ten agents instead of twenty keep the usage burn below wave 1's,
    which exhausted the window in about 20 minutes.
19. **Group A rule (lead, before ranking).** "Failed mainly on cost" was read as gross t >= 1.0 (D5's screen bar)
    with net below zero; "realistic passive saving" as at most the slippage share of the D8 round trip, less under
    TopstepX trade-through fills. Both were fixed before NM1's rows were ranked.
20. **Shortlist vehicles.** C1-C3 are sized on SPY/ES; the program's equity vehicle is MNQ (MES is closed as a
    vehicle since Stage E), so MNQ is the proposed vehicle and MES is shown for reference only; the NQ size of the
    3rd-Friday spike is unverified (NQ appears only in a figure). C4/C5 have no micro (1 ZN).
21. **Second usage-limit cut and planner-approved window (11:16 PDT).** Wave 2 hit the session limit at about
    06:35 PDT (R2 and R6 finished; RD8 finished on disk; DF3 and R8 left near-complete files; DF1, DF2 and NM2 left
    only saved pages); the laptop rebooted at about 10:50. The pause 06:35-11:10 is not work time. The planner set
    work until 15:00 PDT and the return by 15:30 PDT, at most 6 workers at once in this session (two sessions share
    one usage window), finishing started items before opening new ones. The lead re-spawned only the unfinished
    items (DF1, DF2, NM2, RD3, RD6 and a mechanical finisher for DF3's JSON and R8's md), each told to read its own
    files and pages first.
22. **Agent tool instead of a workflow for wave 3.** Ultracode favours workflows, but two usage cuts had already
    discarded the context of every cut workflow agent (workflow agents cannot be resumed by message). Wave 3 used
    the Agent tool so any agent cut by a third limit can be resumed with its context.
23. **What is committed.** The commit holds the return, the STATE file, the progress and STAGES entries, and every
    md, json, py and txt file at the top of reports/stage_e25_briefs/ plus terms/terms_log.md. The raw fetched pages
    (pages/, 273 MB) and saved terms pages (terms/*.html, 12 MB) stay untracked, as in E.13 and E.20: their size,
    and several sites' terms forbid republishing (DO_NOT_COMMIT.txt lists the hosts). Every quote used is in the
    reader files with its URL, fetch time and sha256.
24. **Return sections from parts.** The return was assembled by script (assemble_return.py) from the summary, the
    verbatim check files, the synthesis (v3, after the S4 fixes), the per-reader source lists, the delegation table
    from the transcripts, the verification table, this list, the decisions and the cost section, so that no figure
    was retyped.
