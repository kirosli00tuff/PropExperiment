# Brief: KResearch-OpusHigh (worker-high, model opus) - Stage E.31 K-algorithm rules

Objective (one): establish, with verbatim quotes from fetched full text, the CME Globex matching rules
that applied to CBOT soybean meal (ZM) outright futures in 2023-11..2024-02, precisely enough to code a
simulator of the allocation an incoming aggressor order gets across the resting orders at one price.

Find and quote (each: value, source URL, fetch time UTC, sha256 of the saved raw page, verbatim lines):
1. ZM's match algorithm code (tag 1142 MatchAlgorithm; expected K = "Configurable") in the CME Globex
   Product Reference Sheet. E.28 saved Wayback copies of that sheet in reports/stage_e28_briefs/pages/REV_spec/
   and a reader script reports/stage_e28_briefs/work/lead/lead_xls_rows.py: reuse them first (find the
   ZM, ZS, ZL rows: algorithm, TOP/LMM columns, any percentages or minimums).
2. The K algorithm's steps and parameters for grains/oilseeds outrights: TOP order eligibility (what makes
   an order TOP, when TOP status is lost), TOP maximum / minimum quantities (planner notes say a cap of 100
   on grain outrights: verify), LMM (any for ZM?), FIFO percentage (40%?), pro-rata percentage (60%?),
   pro-rata rounding and minimum allocation, leveling (exact rule: who gets the leveled lot, in what order,
   how many), residual FIFO, and the rule that an aggressor at least as large as all displayed quantity
   is matched FIFO (or fills everyone). How implied orders participate (they are not disseminated).
3. CME's published worked examples of this algorithm (resting orders with sizes and times, incoming size,
   the resulting allocation per order). Transcribe every example exactly; they become unit tests.
Sources to try: CME Client Systems wiki pages "Matching Algorithm Overview" / "Configurable" / "Split FIFO
Pro-Rata" / "Implied Intercommodity Ratio Spreads" (cmegroupclientsite.atlassian.net, through Wayback);
the CME presentation to the CFTC Agricultural Advisory Committee 2019-04
(https://www.cftc.gov/system/files/2019/04/10/aac041119presentation_cmegroup.pdf); CME rule filing 14-270
on cftc.gov; any CME Globex notice on grain matching changes (e.g. the 2014-2015 grain algorithm change);
Peng (J. Futures Markets 2024) only if its full text is openly reachable.
Fetching: cmegroup.com pages block direct fetches: use web.archive.org snapshots. When WebFetch fails,
fall back to `scrapling extract get <url> <file>`, then `scrapling extract fetch <url> <file>` (CLAUDE.md).
Save every page used as evidence raw under reports/stage_e31_briefs/research/pages/K/, and read it by grep
(context hygiene: never load a whole page into context). If a WebSearch returns an over-budget notice,
stop searching, log it with the time, and return. Use at most 50 searches.

Output: reports/stage_e31_briefs/research/K_algorithm.md: (a) a parameter table (parameter, value, applies
to ZM?, source, verbatim quote); (b) the step order of the algorithm as the sources state it; (c) every
worked example transcribed with its source; (d) a "not found / conflicting" list; plus
reports/stage_e31_briefs/research/K_fetch_log.md (URL, UTC time, sha256, method, ok/failed).
Boundaries: research only. No Databento call, no API key, no market data, no repo file edits outside
reports/stage_e31_briefs/research/. DataResearch-OpusHigh covers Databento, USDA, price limits and
contract specs: do not research those. Mark anything not from fetched full text [unverified].
Return: the paths, a summary of at most 200 words, and anything unfinished.
