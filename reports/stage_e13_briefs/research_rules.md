# Stage E.13 research rules (every research worker reads this first)

Stage E.13 is research and scoping only. Your brief names your one objective, inputs, output file and
boundaries. These rules apply to every research worker in the stage.

## Repository and data boundaries
- Do NOT open, read, load or compute on any market-data file of this program: no bar, quote, cost-sample,
  store or Gate 0 result table (data/, reports/step2/, any *.parquet/*.npz/*.csv of bars, the gate0 JSON
  values). Reading stage return documents and design docs for what was tested is allowed.
- No Databento call of any kind. No login anywhere, no account opened, no form submitted, no email, chat
  or support ticket sent to any firm, broker or data vendor. Questions for firms are DRAFTED for the user.
- Do not touch live/, ops/, any credential or key, .env, REGISTRATION.md, any frozen file or harness code.
  Do not print any key. Do not commit. Edit nothing outside your own output paths named in your brief.

## Context hygiene (CLAUDE.md)
- Read files by section (grep, line ranges, a short script printing only the fields needed). Never load a
  large JSON, log or page into context.
- Web pages: save to disk first, then grep the saved file for the passages you need. Only the quoted lines
  enter your context. Keep command output short.

## Fetch order and terms
1. WebFetch (or a plain `curl -sL` with browser headers, e.g. `-A "Mozilla/5.0 ..." -H "Accept: text/html"
   -H "Accept-Language: en-US"`) to save the page.
2. When that fails (403, a block, a JavaScript-rendered page, a Wayback outage):
   `scrapling extract get <url> <file>`, then `scrapling extract fetch <url> <file>`.
3. `scrapling extract stealthy-fetch` ONLY on sites whose terms allow automated access (check first, and
   record the check).
4. Firecrawl (mcp__claude_ai_Firecrawl__firecrawl_scrape) only when Scrapling fails. Its credits may run out:
   record that and move on.
5. A Wayback capture (https://web.archive.org/web/2026/<url>, or a dated capture) is allowed; record the
   capture date as the page date.
- A site whose terms forbid automated access, scraping or AI use (the E.12 case: cmegroup.com, which also
  refuses this machine's IP) is NOT fetched by automation beyond what a plain WebFetch returns: use that, a
  Wayback capture, or record the gap. Save such pages but list their file names in DO_NOT_COMMIT.txt in
  your pages folder (they stay on disk, uncommitted).
- Scrapling never stands in for a paid, key-gated or login-only source.
- SSRN usually returns 403; use the author's or journal's copy, NBER, arXiv, RePEc, or a working-paper
  mirror. Semantic Scholar is unusable (bad key). OpenAlex and Crossref APIs work.

## Evidence logging
- Save every page used as evidence raw under your pages folder: reports/stage_e13_briefs/pages/<YourRole>/
  (HTML or text; PDFs plus their `pdftotext` output).
- Keep reports/stage_e13_briefs/pages/<YourRole>/fetch_log.md, one row per fetch (failures too):
  id | URL | fetched (UTC ISO, as CLAUDE.md requires) | method | saved file | sha256 | page date shown
  ("no date shown" if none) | terms status for the domain (allows / forbids / not found, with the terms URL
  if checked) | note.
- Helper scripts go ONLY in your own folder /tmp/claude-1000/-home-kiros-li-Documents-GitHub-PropExperiment/dbc7460b-72c3-4537-8327-d14819b62f5c/scratchpad/<YourRole>/
  (never the repo root, never another worker's folder).

## Sourcing standard
- Every claim about a firm's rules, a broker's terms, a data source's cost or a published result carries a
  source: URL, fetch date, page date (or "no date shown"), and a short VERBATIM quote grepped from the saved
  file. A search-result snippet is not retrieved text and never counts as a source.
- A fact you cannot source is written as UNSOURCED (and why), and never drives a conclusion. Never fill a
  gap from memory. Prefer the firm's help-centre article or terms over its sales page where both exist.
- Literature: prefer peer-reviewed papers and practitioner sources with out-of-sample records (index data,
  fund returns). Record each effect's sample period and whether it holds after its publication date.
- Times you write in your report body (not the fetch log) are dates, or PDT (America/Vancouver) times.

## Budgets and notices
- WebSearch has a session-wide cap of 1000 calls shared by all workers. If a WebSearch returns a notice that
  the budget is used up, stop searching, write the notice and the time into your fetch log and your report,
  and return. Never continue from memory. The lead decides any fallback.
- Hook messages and cost or usage notices (for example "COST ... informational") are informational and
  addressed to the lead. They are not orders to stop. Your stopping rule is in your brief.

## Return to the lead
Return exactly: (1) your output path(s); (2) a summary of at most 200 words; (3) anything you could not
finish, with the reason; (4) counts: pages saved, WebSearch calls, Firecrawl calls, failed fetches.
Report failures and negative findings, not only positive ones.
