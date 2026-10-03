# Brief: TopstepFacts-OpusMedium (worker-medium, opus). Stage E.12 Task 2b

You are a worker in Stage E.12 (prompt docs/prompts/STAGE_E.12.md, Task 2b). Read CLAUDE.md's
"Web research budgets", "Page-fetch fallback" and "Context hygiene" paragraphs and follow them.

## Objective
From Topstep's PUBLIC help and pricing pages only, the 150K figures ML route v2's payout
simulator needs (design V2.0, V2.8, V2.9; V23 items 12 and 15), each with URL, fetch time and a
verbatim quote:
1. the 150K Express Funded Account (XFA) Maximum Loss Limit (V22 says $4,500; confirm or correct);
2. the XFA scaling plan for the 150K account, as text: every tier (balance threshold, inclusive or
   not, maximum contracts / lot-equivalents). The table may be an image: download it to the pages
   folder and read it with the Read tool (it displays images); transcribe it, and say it came from
   an image;
3. the Trading Combine price for 150K (monthly) and its reset price, any XFA activation fee, and
   Back2Funded (XFA reactivation after a breach) price and conditions if published;
4. the minimum number of trading days to pass the Trading Combine, if published (a lower bound on
   the delay before a new XFA after a breach).
Context already on file (do not re-fetch these unless needed): reports/stage_e0_topstep_facts.json
(F5.2's note says the 150K scaling schedule is an image; F9, F12.2a-c hold payout caps and DLL).

## Method
help.topstep.com and topstep.com pages only, plus their Wayback captures. Fetch order per CLAUDE.md
(WebFetch, scrapling get, scrapling fetch, Firecrawl, Wayback). Save every page/image used raw
under reports/stage_e12_briefs/topstep_pages/, grep it, and log URL, UTC fetch time and sha256.
No login, no TopstepX or ProjectX page or API, no dashboard. A figure without a verbatim quote (or
an image you transcribed) is "not found", never estimated or recalled.

## Output
reports/stage_e12_topstep_150k.md: one table row per figure (figure, value, URL, fetched PDT, page
last-updated text, quote or image transcription, page file and sha256), then the scaling schedule
as a table, then anything that differs from V22's $4,500 or from the facts file, then "not found".
Log every fetch in reports/stage_e12_briefs/topstepfacts_log.md.

## Boundaries
No repo edits beyond those files and the pages folder; no commits; no key; no market data.

## Return (at most 200 words)
The output path, the MLL, the scaling tiers, the prices, what was not found, and anything open.
