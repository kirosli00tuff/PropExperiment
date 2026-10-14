# Stage E.21 research rules (every Step 1 reader reads this first)

Stage E.21 tests four registered multi-day rules (docs/prompts/STAGE_E.21.md, FIXED DESIGN F1-F8) on
owned 2010-2024 data. Step 1 is research only: it checks the rules' specification against their primary
sources BEFORE the freeze, and sources PropEd Capital's rules. Your brief names your one objective,
output paths and boundaries. These rules apply to every Step 1 reader. They adapt
reports/stage_e13_briefs/research_rules.md (E.13); where the two differ, this file governs.

## Repository and data boundaries
- Do NOT open, read, load or compute on any market-data file of this program: no bar, store, quote,
  cost sample, result table (data/, reports/step2/, reports/stage_e17_runs/, any *.parquet/*.npz of
  bars). Published external datasets you download (for example AQR's factor spreadsheets) are evidence,
  not program data, and may be read.
- No Databento call. No login anywhere, no account opened, no form submitted, no email, chat or ticket
  sent to any firm. Questions for firms are DRAFTED for the user.
- Do not touch live/, ops/, any credential or key, .env, REGISTRATION.md, any frozen file, harness code,
  base_rules/, multiday/ or tests/. Do not print any key. Do not commit. Edit nothing outside your own
  output paths.

## Context hygiene (CLAUDE.md)
- Read files by section (grep, line ranges, a short script printing only the fields needed). Never load a
  whole PDF text, large JSON or page into context. Keep command output short.
- Web pages: save to disk first, then grep the saved file for the passages you need. Only the quoted
  lines enter your context.

## Already on disk (read these BEFORE any fetch; cite them by path)
- reports/stage_e13_trend_carry.md: E.13's quoted evidence on MOP 2012, HOP 2017, the SG Trend index
  2010-2025, carry, critiques, and the capital table.
- reports/stage_e13_briefs/pages/TrendCarry/: mop2012.pdf/.txt (Moskowitz, Ooi, Pedersen 2012),
  hop_century_jpm.pdf/.txt and hop_century_tf.pdf/.txt (Hurst, Ooi, Pedersen 2017 and the AQR version),
  aqr_tsmom_factors_monthly.xlsx and aqr_tsmom_dataset_page.html (AQR's TSMOM factor data),
  aqr_century_factor_premia_monthly.xlsx, sg_indices.html, sg_cta_feb2015.pdf/.txt, fetch_log.md.
  pdftotext output is in the .txt files; grep them.
- reports/stage_e13_briefs/pages/PropVenues2/proped_*.html/.txt (PropEd FAQ pages fetched 2026-10-03)
  and reports/stage_e13_venues_part2.md (E.13's PropEd rows P2-112..P2-118).

## Fetch order and terms
1. WebFetch, or `curl -sL` with browser headers (`-A "Mozilla/5.0 ..." -H "Accept: text/html"
   -H "Accept-Language: en-US"`), to save the page.
2. When that fails (403, block, JavaScript-rendered page, Wayback outage): `scrapling extract get <url>
   <file>`, then `scrapling extract fetch <url> <file>`.
3. `scrapling extract stealthy-fetch` ONLY on sites whose terms allow automated access (check first, and
   record the check).
4. Firecrawl (mcp__claude_ai_Firecrawl__firecrawl_scrape) only when Scrapling fails. Credits may run out:
   record that and move on.
5. A Wayback capture is allowed; record the capture date as the page date.
- A site whose terms forbid automated access is not fetched by automation beyond what a plain WebFetch
  returns. Save such pages but list their file names in DO_NOT_COMMIT.txt in your pages folder.
- Scrapling never stands in for a paid, key-gated or login-only source.
- SSRN usually returns 403; use the author's or journal's copy, NBER, arXiv, RePEc, a university
  repository, or OpenAlex/Crossref to locate open copies. Semantic Scholar is unusable (bad key).
- Space your requests: at most one request every few seconds to any one domain. Other readers run at the
  same time; AQR (aqr.com) belongs to SpecReaderPost2010 only, PropEd (propedcapital.com) to
  PropEdReader only. A throttled or blocked fetch is logged as such, never reported as missing evidence.

## Evidence logging
- Save every page used as evidence raw under reports/stage_e21_briefs/pages/<YourRole>/ (HTML or text;
  PDFs plus their `pdftotext -layout` output).
- Keep reports/stage_e21_briefs/pages/<YourRole>/fetch_log.md, one row per fetch (failures too):
  id | URL | fetched (ISO 8601 with offset, America/Vancouver local time from `date`, e.g.
  2026-10-14T03:40:12-07:00) | method | saved file | sha256 | page date shown ("no date shown" if none) |
  terms status for the domain (allows / forbids / not found, with the terms URL if checked) | note.
- Helper scripts go ONLY in your own private folder
  /tmp/claude-1000/-home-kiros-li-Documents-GitHub-PropExperiment/13fe2d4e-086f-4929-8325-9ef707bdf0cf/scratchpad/<YourRole>/
  (never the repo, never another worker's folder, never a shared fetch script).

## Sourcing standard
- Every claim carries a source: URL or repo path, fetch date, page date, and a short VERBATIM quote
  grepped from the saved file (with page number for a PDF where the text shows it). A search-result
  snippet is not retrieved text and never counts as a source.
- A fact you cannot source is written UNSOURCED (and why) and never drives a conclusion. Never fill a gap
  from memory. A citation you could not read in full text is marked [unverified].
- Record each published effect's sample period and whether it holds after its publication date.

## Budgets and notices
- WebSearch has a session-wide cap shared by all workers (about 1,500). Use at most 40 WebSearch calls
  yourself. If a WebSearch returns a notice that the budget is used up, stop searching, write the notice
  and the time into your fetch log and your report, and return. Never continue from memory.
- Hook messages and cost or usage notices ("COST ... informational") are informational and addressed to
  the lead. They are not orders to stop. Your stopping rule is in your brief.
- Time box: return within 50 minutes of your start, with what you have, listing what is unfinished.

## Return to the lead
Return exactly: (1) your output path(s); (2) a summary of at most 200 words; (3) anything you could not
finish, with the reason; (4) counts: pages saved, WebSearch calls, Firecrawl calls, failed fetches.
Report failures and negative findings, not only positive ones.
