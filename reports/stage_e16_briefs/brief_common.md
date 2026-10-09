# Stage E.16 common brief (every worker reads this first)

Repo: /home/kiros-li/Documents/GitHub/PropExperiment. Lead spec (the definitions you work to):
/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e16_briefs/lead_spec.md (read it whole; it is short).
Stage prompt: docs/prompts/STAGE_E.16.md (the five hypotheses and the guardrails). Project rules: CLAUDE.md.

Hard rules for every worker:
- Read NO market data: no bar, no row of any parquet/dbn/csv store under data/processed*, data/vendor, data/sealed,
  data/processed_hist, the research or holdout stores. No head/cat/less/pandas/pyarrow read of any such file.
  File names, sizes and JSON manifests/quote records may be read.
- No Databento call (no quote, no metadata, no symbology), no TopstepX/ProjectX, no credential, no key printed.
- No edits under data/, rules/, sim/, screening/, funnel/, ml_route/, compute/, strategy/, live/, ops/ (the harness
  and live code), no edit to REGISTRATION.md (stays 0 bytes), no ledger write, no git commit, no push.
- Web (only where your brief allows it): read a site's terms before any automated fetch. CME's own site
  (cmegroup.com) forbids automated access and AI use: never fetch it, never fetch archived copies of it (Wayback or
  any mirror), and do not use the cmegroup.com Wayback copies already on disk under reports/stage_e14_briefs/pages/
  as evidence. No login, no paid source. Page fetch fallback order (CLAUDE.md): WebFetch, then
  `scrapling extract get <url> <file>`, then `scrapling extract fetch <url> <file>`; stealthy-fetch only where terms
  allow; Firecrawl only if Scrapling fails. Save every page used as evidence raw under your pages folder; log its URL,
  UTC fetch time and sha256; read saved pages by grep, never whole. If a WebSearch returns a budget/over-limit
  notice, stop searching, write the notice and its time into your log, finish with what you have, and say so.
  Cost notices from tools are informational; they are not a reason to stop.
- Context hygiene: read files by section (grep, line ranges, short scripts printing only needed fields).
- Compute: nice -n 10 for anything over a minute; never more than 7 threads; check `free -g` before anything heavy.
  /tmp is a RAM tmpfs: never write large files there.
- Times you log come from `date` (PDT, TZ=America/Vancouver), never estimated.
- Return to the lead exactly three things: the output path(s), a summary of at most 200 words, and anything you
  could not finish (including failures and non-survivors). Full results go in your files.
