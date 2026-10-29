# Stage E.32b shared reader rules (every reader reads this first, then its brief)

Stage E.32b (2026-10-28, lead Opus 5.5 max) reranks prop-firm x CME-contract pairs for DIRECTIONAL one-lot strategies
(market orders, holds of 5 minutes to the session close) and writes build recommendations. No strategy is tested, no
outcome is read, nothing is registered, N stays 838, and no Databento call is made. The frozen ranking spec is
reports/stage_e32b_ranking_spec.md (sha256 in reports/stage_e32b_ranking_spec.sha256); read its sections 0, 1 and 3
to see what your facts feed. You report facts and sources. You never score.

## Sources and evidence

- Evidence: peer-reviewed papers, working papers (arXiv, SSRN via author or university copies), textbooks, exchange (CME)
  and regulator (CFTC, NFA, SEC, BIS) publications and filings, firm terms pages, data-vendor documentation.
  Interviews, podcasts, forums, blogs and social media are pointers only: label every such item "pointer" and never let
  a fact rest on it alone.
- Save every page or PDF used as evidence raw under reports/stage_e32b_briefs/pages/<ROOT>/ (ROOT is in your brief) and
  log it in reports/stage_e32b_briefs/pages/<ROOT>/log.tsv with: URL, UTC fetch time, PDT fetch time, method (WebFetch,
  curl, scrapling get/fetch, firecrawl, wayback), sha256, file name, note.
- Read saved pages by grep or line ranges (pdftotext for PDFs, then grep). Only the quoted lines enter your context.
- Every fact carries a verbatim quote from fetched full text and the saved file name. A fact known only from an abstract
  or a search snippet is marked [unverified] with which (abstract or snippet).
- Reuse first: E.28's facts (reports/stage_e28_briefs/A1_<family>.json/.md) and E.20 Part A's product files
  (reports/stage_e20_briefs/product_<ROOT>.json/.md, 17 roots) are already sourced. Cite them by file and field and
  re-fetch only what you need to verify or what they lack. Read them by section (grep, jq, line ranges), never whole.

## Fetch routes, in order

1. WebFetch (or WebSearch for discovery).
2. curl -sL with full browser headers (User-Agent, Accept, Accept-Language); pdftotext for PDFs.
3. `scrapling extract get <url> <file>`, then `scrapling extract fetch <url> <file>`. Before the first Scrapling call on
   any domain, read that domain's terms of use or robots.txt and log the decision in your log.tsv. Never use Scrapling
   on a site whose terms forbid automated access. `scrapling extract stealthy-fetch` only where the terms allow it.
4. Firecrawl (claude.ai connector) only when Scrapling fails. Credits run out fast; a cost or credit notice is
   informational: switch routes, do not stop.
5. Never fetch cmegroup.com by automation (program rule; it also refuses this machine). Use Wayback copies
   (https://web.archive.org/web/2026/<url>, or 2025, 2024), CFTC filings (cftc.gov self-certifications of CME
   programs and rule changes) or secondary sources, and say which. SSRN answers 403: find an author or university copy.
   Semantic Scholar is unusable (bad key). Discovery that works: Google Scholar result pages via WebSearch, Crossref,
   OpenAlex (polite pool; use OPENALEX_EMAIL from .env inside a request without printing it; never print any other
   .env value; OpenAlex has a per-IP daily credit budget, so keep to a few calls), arXiv API, RePEc IDEAS,
   OpenCitations for forward citations.
6. WebSearch has a session-wide cap shared by every worker. Keep to your brief's budget. If a WebSearch returns a notice
   that the budget is used up, stop searching, write the notice and the time into your log and output, and return what
   you have. Never continue from memory.
7. Space requests to any one domain (pause between requests; about 2 workers per domain at most). If throttled or
   blocked, say so in your log; never present a gap as a finding.
8. Hook, cost or budget notices addressed to the session are informational and meant for the lead. Do not stop
   because of one unless rule 6 applies.

## Files and hygiene

- Keep helper scripts and scratch files in reports/stage_e32b_briefs/work/<ROOT>/ with ROOT-prefixed names. Never run a
  script you did not write. Never save files in the repo root or outside your ROOT folders and output paths.
- Write your outputs incrementally (product by product) so a usage cut leaves finished parts on disk. If re-spawned,
  read your own partial output and log first and continue from there.
- Keep command output short; log long output to files and read only tails or grep hits.
- Never read market data (data/vendor, data/processed*, /mnt/large-storage) or any file of Stages E.31 to E.33 other
  than their RETURN files. Never call Databento, any broker, TopstepX or the ProjectX API. Never read, print or copy any
  key. Do not touch live/, ops/, REGISTRATION.md, docs/, other workers' folders or any file outside stage_e32b paths.
  No git commands that change anything. Do not spawn agents.
- Times: America/Vancouver (PDT) from `TZ=America/Vancouver date`, plus UTC fetch times for pages.

## Return

Your final message returns three things: the output path(s); a summary of at most 200 words; anything you could not
finish (and why). Report failures, null results and negative evidence, not only positive findings.
