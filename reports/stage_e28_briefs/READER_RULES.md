# Stage E.28 shared reader rules (every reader and coder reads this first)

Stage E.28 (2026-10-21, lead Opus 5.5 xhigh) writes a methods brief (Part C), a blind ranking of prop-firm and
contract pairs for limit-order strategies (Part A), and a one-contract order-book data pilot (Part B, later). No rule
is tested, nothing is registered, and the trial count N stays 538. Your brief, in the spawn message, gives your
objective, output paths and search budget. These rules apply on top of CLAUDE.md.

## Program context (for framing; cite the returns, not this paragraph)

The program (PropExperiment) has screened rules on CME futures 1-minute bars (MES first, then a 45-root universe)
for an automated prop account (Topstep XFA via TopstepX), with Newey-West t, Holm, the deflated Sharpe ratio (DSR)
and PBO/CSCV, ridge and LightGBM on a 64-feature library, and EWMAC trend sizing. Nothing has passed after costs.
E.25 found that limit orders rescue no earlier rule. The direction is now limit-order and order-book strategies
(V44), where V43 allows a machine-learning model to be the traded strategy under a frozen pipeline, purged and
embargoed cross-validation, every configuration counted into N, and one test on data that never selected it. Part B
will buy ONE Databento schema (likely mbp-10, possibly mbo or tbbo) for ONE CME contract for about 4 months
(2023-11..2024-02, extended earlier), to measure fill rates, queue times and markouts at 1, 10 and 60 seconds for a
1-lot passive order. Hardware: a ThinkPad with 20 logical CPUs, 14 GB RAM and an RTX 3050 Laptop GPU (4 GB VRAM).
Order latency from Vancouver to CME Aurora is tens of milliseconds; no co-location.

## Sources and evidence

- Sources: textbooks, peer-reviewed papers, working papers (arXiv, SSRN pages via mirrors), public firm research and
  talks, exchange (CME) and regulator (CFTC, NFA, SEC, FCA, OSC/BCSC, CRA) publications, firm terms pages.
  Interviews, podcasts, forums and social media are pointers only, never evidence.
- Save every page or PDF used as evidence raw under reports/stage_e28_briefs/pages/<ROOT>/ (your ROOT is in your
  brief). Log each in reports/stage_e28_briefs/pages/<ROOT>/log.tsv with: URL, UTC fetch time, PDT fetch time,
  method (WebFetch, curl, scrapling get/fetch, firecrawl, wayback), sha256, file name, note.
- Read saved pages by grep or line ranges (pdftotext for PDFs, then grep). Only the quoted lines enter your context.
- Every claim you cite carries a verbatim quote from fetched full text and the saved file name. A claim you could
  not verify from full text is marked [unverified] (for example, known only from an abstract or a search snippet:
  say which).
- Equations: write them in plain-text or LaTeX-style notation, define every symbol, and say where each comes from
  (the paper and its equation number when the full text shows it). Do not invent equation numbers.

## Fetch routes, in order

1. WebFetch (or WebSearch for discovery).
2. curl -sL with full browser headers (User-Agent, Accept, Accept-Language). pdftotext for PDFs.
3. `scrapling extract get <url> <file>`, then `scrapling extract fetch <url> <file>`. Before the first Scrapling call
   on any domain, read that domain's terms of use or robots.txt and log the decision in your log.tsv. Never use
   Scrapling on a site whose terms forbid automated access. `scrapling extract stealthy-fetch` only where the terms
   allow automated access.
4. Firecrawl (claude.ai connector) only when Scrapling fails.
5. Known blocks: cmegroup.com refuses this machine's IP (use Wayback copies:
   https://web.archive.org/web/2026/<url>, or 2025/2024); SSRN answers 403 (look for the author's or a university
   copy, or an arXiv version); Semantic Scholar is unusable (bad key). Discovery that works: arXiv API
   (export.arxiv.org/api/query), Crossref, OpenAlex (polite pool; OPENALEX_EMAIL is in .env: use it in a request
   without printing it, and never print any other .env value), RePEc IDEAS, Google Scholar result pages via
   WebSearch.
6. Firecrawl or other cost notices are informational. Do not stop because of one; switch routes.
7. WebSearch has a session-wide cap of 1500 calls shared by every worker; keep to your brief's budget. If a WebSearch
   returns a notice that the budget is used up, stop searching, write the notice and the time into your log and
   your output, and return what you have. Never continue from memory.
8. Space requests to any one domain (a pause between requests; no more than about 2 workers on one domain).
   If throttled or blocked, say so in your log; never present a gap as a finding.

## Files and hygiene

- Keep helper scripts and scratch files in reports/stage_e28_briefs/work/<ROOT>/ with ROOT-prefixed names. Never run
  a script you did not write. Never save files in the repo root or anywhere outside your ROOT folders and your
  output paths.
- Write your output file incrementally (section by section) so a usage cut leaves finished sections on disk. If you
  are re-spawned, read your own partial output and log first and continue from there.
- Keep command output short; log long output to files and read only tails.
- Do not read market data (data/vendor, data/processed*, MLCryptoEngine files) unless your brief says so. Never read
  any data dated 2023-11-01 or later. Never call Databento, any broker, TopstepX or the ProjectX API. Never read,
  print or copy any key.
- Do not touch Stage E.26's files (the data move, data/config.py, docs/DECISIONS.md), live/, ops/, REGISTRATION.md,
  or other workers' folders. No git commits. Do not spawn other agents.
- Times in logs: America/Vancouver (PDT) from `TZ=America/Vancouver date`, plus UTC fetch time for pages.

## Return

Your final message returns three things: the output path(s); a summary of at most 200 words; anything you could not
finish (and why). Report failures, null results and negative evidence, not only positive findings.
