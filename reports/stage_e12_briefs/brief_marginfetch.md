# Brief: MarginFetch-OpusHigh (worker-high, opus). Stage E.12 Task 2a

You are a worker in Stage E.12 (prompt docs/prompts/STAGE_E.12.md, Task 2a). Read CLAUDE.md's
"Web research budgets", "Page-fetch fallback" and "Context hygiene" paragraphs and follow them.

## Objective
For each of the 28 v2 vehicles and each distinct price-path contract, the CME Group FRONT-MONTH
MAINTENANCE margin per contract in USD as published now (2026-10-03), with source URL, fetch time
and method. The lead ranks the phase-1 purchase by RT_X / margin (design V2.1, V23 item 3).

Vehicles (28): MNQ M2K MYM ZT ZF ZN TN ZB UB 6E 6A 6B 6C 6J 6S 6N MCL NG MGC MHG ZC ZW ZS ZM ZL HE LE
MBT. Price paths that differ from their vehicle (6): NQ RTY YM CL GC HG.

## Method
- Sources: CME Group's public margin pages (product page "Margins" tab, e.g.
  https://www.cmegroup.com/markets/equities/nasdaq/micro-e-mini-nasdaq-100.margins.html), the public
  JSON the page itself loads (CME's CmeWS margins service, if reachable without login), CME Clearing's
  public performance-bond advisories / margin files, and Wayback Machine captures of those pages.
  No login, no paid source, no broker's page as a substitute. Fetch order per CLAUDE.md: WebFetch,
  then `scrapling extract get <url> <file>`, then `scrapling extract fetch <url> <file>`
  (stealthy-fetch only where the site's terms allow automated access; record your check), then
  Firecrawl, then Wayback (latest capture; record the capture timestamp).
- Save every page used as evidence raw under reports/stage_e12_briefs/margin_pages/ and read it by
  grep or a short script; log URL, UTC fetch time and sha256 per page in the log below. Never paste
  a whole page into context.
- Maintenance, not initial. Front month = the contract month CME lists first for outright futures
  (record which month). If CME shows hedger and speculator figures, record both and use maintenance
  (the same for both since CME's change; note it if not). Record the effective date CME shows.
- A WebSearch over-budget notice: stop searching, log it with the time, and return what you have.
  Cost notices are informational; carry on.

## Output
reports/stage_e12_cme_margins.json:
{"schema": "cme_margins/1", "fetched_pdt": "...", "rows": [{"symbol": "MNQ", "role": "vehicle" |
"price_path", "maintenance_usd": 0.0 | null, "contract_month": "...", "effective_date": "...",
"url": "...", "method": "webfetch|scrapling-get|scrapling-fetch|firecrawl|wayback",
"capture_ts": "... (wayback only)", "page_file": "...", "page_sha256": "...", "quote": "the line
holding the figure, verbatim"}], "blocked": [{"symbol": ..., "routes_tried": [...], "errors": [...]}]}
plus reports/stage_e12_briefs/marginfetch_log.md (every fetch: time, URL, route, result, sha256).
A figure without a verbatim quote from a saved page is null and listed in "blocked". Never
estimate, never carry a figure from memory.

## Boundaries
Read-only web fetches of CME pages and their Wayback captures only. No TopstepX/ProjectX page or
API, no Databento, no key, no repo file edits outside your two outputs and the pages folder, no
commits. Do not read any market-data store.

## Return (at most 200 words)
The output path, how many of the 34 symbols have a quoted figure, the routes that worked, the
blocked symbols with reasons, and anything open.
