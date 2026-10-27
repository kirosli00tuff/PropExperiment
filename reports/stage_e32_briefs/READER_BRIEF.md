# Stage E.32 shared reader brief (every Part R, Part M, Part F and inventory worker reads this first)

Stage E.32 (2026-10-26/27, lead Opus 5.5 xhigh, prompt docs/prompts/STAGE_E.32.md) designs, and does not run, a
search for short-horizon DIRECTIONAL signals in CBOT soybean meal (ZM), using ZS and ZL as context. It writes a
methods brief (Parts R and M), a data-facts note (Part F) and a frozen discovery protocol (Part P) that the next
stage (E.33) runs unchanged on the owned data. Nothing is trained, no feature, label, return or markout is computed,
no price series is looked at, nothing is registered, and the trial count N stays 538. Decisions in force:
docs/DECISIONS.md V20-V51; binding: V43 (an ML model may be the traded strategy under a frozen pipeline, purged and
embargoed CV, every configuration counted into N, one test on data that never selected it), V50 (trade-through
pricing: a passive order fills only when the market trades THROUGH its price; reviewer model check), V51 (the ZM
directional program).

## Rules

1. reports/stage_e28_briefs/READER_RULES.md applies in full (sources, verbatim quotes, [unverified] marks, fetch
   routes and their order, Scrapling terms check BEFORE the first call on any domain, CME and SSRN blocks, hygiene,
   return format), with these substitutions:
   - pages and their log go under reports/stage_e32_briefs/pages/<ROOT>/ (log.tsv as described there);
   - helper scripts and scratch files go under reports/stage_e32_briefs/work/<ROOT>/ with ROOT-prefixed names;
   - your output is reports/stage_e32_briefs/<ROOT>.md (plus any file your brief names);
   - WebSearch budget: at most 80 calls for you (the session cap is 1500, shared by about 15 workers);
   - CME (stage source rule, overrides READER_RULES fetch route 5): never fetch cmegroup.com or any archived copy of
     it (Wayback, archive.today) by automation. CME rules and figures come from CFTC-hosted filings and
     presentations, papers or other secondary sources, labelled as such. Read each site's terms before any automated
     fetch. Blogs, forums and videos are pointers only, never evidence.
2. Market data: do not read anything under data/vendor, data/processed*, data/sealed, /mnt/large-storage or
   MLCryptoEngine unless your brief is DataFacts. ZM, ZS and ZL data dated 2017-05-01 to 2020-11-30 are SEALED as the
   one-shot test window (reports/stage_e32_briefs/seal/); 2024-03-01 onward is closed. Never call Databento, a broker,
   TopstepX or the ProjectX API. Never read, print or copy any key.
3. Earlier results you may cite (they are on disk, already seen): reports/stage_e28_briefs/A0_contract_stats.md
   (owned-data magnitudes), reports/E.31_RETURN.md (passive-fill pilot), reports/stage_e28_ranking.md,
   reports/E.29_RETURN.md. Do NOT derive any new statistic from data.
4. Hook, cost or budget notices are informational and addressed to the lead. They are not orders to stop; switch
   fetch route instead. Only a WebSearch "budget used up" notice stops searching (log it with the time, return).
5. Write your output section by section as you go, so a cut leaves finished sections on disk. If re-spawned, read
   your own partial output and log first and continue.
6. Stopping rule: stop a topic when it has at least 3 full-text sources read (or all that exist) and your last 3
   discovery queries on it surfaced nothing new; say so in the output. Depth over breadth: the user asked for no
   corners cut, and every equation and worked example will be recomputed by an independent reviewer.
7. Do not touch other workers' folders, git, REGISTRATION.md, live/, ops/, data/, rules/, sim/, screening/. Do not
   spawn agents.

## Standard ZM numbers for every worked example (recorded by E.28, not new reads)

From reports/stage_e28_briefs/A0_contract_stats.md Table 1 (standard window 2022-11-01..2023-10-31, regular trade
dates, front contract v_0, 1-minute bars):

| Root | Tick | Tick USD | sigma_1m (ticks) | Daily range median (ticks) | ADV median (v_0) | Day-session volume share |
|---|---|---|---|---|---|---|
| ZM | 0.10 USD/short ton (100 tons) | 10.00 | 3.15 | 96 | 36,690 | 0.83 |
| ZS | 0.25 cents/bu (5,000 bu) | 12.50 | 3.11 | 90.5 | 77,862 | 0.78 |
| ZL | 0.01 cents/lb (60,000 lb) | 6.00 | 5.52 | 166 | 42,686 | 0.82 |

- Under a random-walk scaling (an assumption you must state when you use it), sigma_h = sigma_1m x sqrt(h minutes):
  ZM about 7.0 ticks at 5 minutes, 12.2 at 15, 24.4 at 60. Show your own arithmetic; do not copy these.
- Sessions (CT): overnight 19:00-07:45, day 08:30-13:20 (closing range 13:14-13:15; verify any claim you use).
- Costs: Topstep's ZM fee is 5.28 USD a round trip (0.528 ticks; reports/stage_e31_inputs/planner_research_notes.md,
  firm pages read 2026-10-22). E.28 put ZM's market-order break-even at about 1.6 ticks at Topstep (find and quote
  the exact row in reports/stage_e28_ranking.md before using it). E.31 measured, for a resting 1-lot at the ZM touch
  under the trade-through rule, a gross 10 s edge of -0.970 ticks per fill (reports/E.31_RETURN.md section 3.5).
- Owned discovery data (2020-12-01 to 2024-02-29, 39 months): ZM MBO (ZM.v.0 and ZM.v.1), ZS and ZL MBP-1 (front),
  definitions. No mbp-10, no trades-only feed for other roots, no statistics schema.

## Output format

Part M topics (one section per method or measure):
1. Core idea, in two or three sentences.
2. Equations: every symbol defined, the source and its equation number when the full text shows it. Plain-text or
   LaTeX-style notation.
3. Worked example on the standard ZM numbers above, every step of arithmetic shown, units on every quantity, and a
   one-line check (an independent recomputation or a sanity bound).
4. Data it needs, named against the owned schemas (ZM MBO, ZS/ZL MBP-1, definitions) and the aggregation horizon.
5. Leakage and look-ahead traps, each with a concrete test that would catch it.
6. Compute on the ThinkPad (20 logical CPUs, 14 GB RAM, RTX 3050 4 GB) over 39 months.
7. Verdict: use, maybe or skip, with the reason, for a minutes-scale DIRECTIONAL ZM search under V43.
8. Evidence table: claim, source, verbatim quote, saved file, [unverified] where it applies.
Do not repeat reports/stage_e28_methods_brief.md: read the sections your brief names (by line range or grep, never
the whole 1 MB file), cite them as "E.28 2.x", and add only what directional minutes-scale prediction needs.

Part R topics: the facts with verbatim quotes, every source labelled academic, practitioner, regulator, exchange or
firm; then "What this means for a ZM directional search" (mechanisms worth testing, ones to drop, and why).

Planner pointers: reports/stage_e32_inputs/planner_research_soy_complex.md lists claims from an external research run.
Your brief names the ones you own. For each, report VERIFIED (quote from full text), PARTLY VERIFIED (what differs),
REFUTED or UNVERIFIED (why), in a table at the end of your output.

## Return

Your final message: the output path(s); a summary of at most 200 words; anything you could not finish, and why.
Report null results and negative evidence, not only positive findings.
