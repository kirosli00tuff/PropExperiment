# Stage E.20 Part A: shared brief for the 17 product readers

Written by the E.20 lead (2026-10-11). Every ProductReader-<ROOT>-OpusHigh starts here. Your spawn
message names your ROOT and your shared assignment (section 7). Everything else is in this file.

## 1. Objective and outputs

One objective: for your ROOT, (1) the published intraday evidence since 2015 for that root or its
asset class, verified against primary sources; (2) the availability of every ML route v2 (V2.3)
feature that reads your root, over both windows; (3) at most two literature-sourced features you
propose; (4) NQ only: the H6 details and the SqueezeMetrics GEX terms ruling.

Write exactly two files (plus raw pages and, if assigned, shared notes):
- `reports/stage_e20_briefs/product_<ROOT>.md`: sections 1 to 6 below.
- `reports/stage_e20_briefs/product_<ROOT>.json`: the schema in section 11.
- Raw pages: `reports/stage_e20_briefs/pages/<ROOT>/` (shared-source pages and notes:
  `reports/stage_e20_briefs/shared/`).

Your final reply to the lead: the two paths, a summary of at most 200 words, and anything you
could not finish or verify. Aim to return within about 90 minutes. A thread that runs long is
stopped and listed under "Unfinished", never guessed.

## 2. Inputs (read by section: grep, line ranges, short scripts; never whole large files)

- Planning brief (your starting point for item 1): `reports/stage_e20_briefs/literature_planning_2026-10-10.md`.
  Its figures are leads, not facts: every claim you rely on is verified against the primary source.
- Root table (vehicle, tick, D8 round trip, session times, windows):
  `reports/stage_e20_briefs/root_table.md`. D8 costs per bucket: `reports/stage_e2a_costs.md`.
- The v2 feature library (item 2): `docs/STAGE_E_ML_V2_DESIGN.md` V2.2 (clock) and V2.3 (signals);
  `reports/stage_e11_signal_coverage.md` (families, legs, rows each signal applies on);
  `reports/stage_e11_briefs/member_inventory.md` and `.json` (each family's calendars and literals);
  the covered and uncovered signal names in `reports/stage_e12_gate0_list.json` (keys
  `covered_signals`, `uncovered_signals` only: a list, not results); the signal code
  `ml_route_v2/signals/*.py` and each member's own module under `strategy/stage_e/` (code may be read).
- Calendars, to decide coverage (read their date ranges and source notes, never a bar):
  2019-2024 group calendars `data/calendars/*.py`; 2010-2019 group calendars
  `data/calendars/hist2010/*.json`; release calendar `screening/stage_e_rules.py` (ReleaseCalendar)
  and the file it loads; 2010-2019 release and session calendars built in E.14
  (`reports/stage_e14_cal_*.json`, `reports/stage_e14_calendars.md`, `reports/stage_e14_cal_releases.md`)
  and E.16 (`reports/stage_e16_calendars.md`, `reports/stage_e16_calendars/`); EC-K9 2019-2024
  `reports/stage_e12_ec_k9_2019_2024.md`; E.16 settlement table `reports/stage_e16_settlement.md`;
  E.16 rulings `reports/stage_e16_rulings.md` (session eras, listing dates R-S4, LE R-S3).
- Listing dates: `reports/stage_e16_windows.json` ("products"), `reports/stage_e16_rulings.md` R-S4,
  and public exchange or vendor documentation (never cmegroup.com by automation; see section 8).
- E.13 sources notes (dealer gamma, GEX, terms): `reports/stage_e13_info_sources.md` section 2.7.
- Decisions: `docs/DECISIONS.md` V31 (cost-feasibility gate), V33 item 5, V34 (what was dropped).

## 3. The two windows and the decision clock

- Backward window: each root's 2010-2019 window in the root table (ends 2019-05-05).
- Search window: 2019-05-06..2024-02-29.
- Decision times (V2.2 plus E.20's t4): t1, t2, t3 from the V2.2 table, and t4 = F_X - 60 min
  (equity, rates, FX, energy, gold: 14:08 CT; grains 12:18; livestock 12:03). Horizons: 60 min,
  120 min, and F (exit at the forced flatten F_X). t4 rows use h60 and F only. Market orders only.
- Already added by the prompt (do not propose these): r_ROD(t) = P(t) / P(prior close) - 1 with the
  group's close C (D6 table), and |r_ROD(t)| over its median over the previous 60 trade dates.

## 4. Item 1: published intraday evidence since 2015 (md section 1)

- Scope: studies published since 2015 on intraday return patterns (momentum, reversal, event or
  release windows, settlement or close windows, lead-lag at retail latency, seasonality within the
  day) for your root or its asset class. Holds within a day session; nothing overnight.
- Per effect, one table row: effect, rule (precise enough to code), hold, gross per trade (bp of
  notional and ticks of the vehicle, with the conversion and the public price level used),
  gross or net, sample (instrument, years, bar size), decay evidence (out-of-sample or
  post-publication results), source (authors, year, venue, URL).
- Verification: every number you use carries a verbatim quote from the fetched full text, with
  its location (page, table or section). A claim you could read only in an abstract, a secondary
  source or a search snippet is marked [secondary-only] or [unverified]. Never present a search
  summary as retrieved text.
- Report what fails as well as what works: null results, decay, after-cost failures.
- V34 dropped from the H-test shortlist: the overnight drift, closing-auction distortions,
  pre-announcement drift (unsized) and noise-area momentum. Do not re-propose them as features
  unless you find a sized per-trade figure in a primary source.

## 5. Item 2: feature availability over both windows (md section 2)

List every V2.3 feature (by its code name, e.g. `cp1_ret`, `g13_min_to_rel`, `k2_auction_mto`,
`g17_zn`) that reads your root's bars or applies on your root's rows, with:
- legs: every root whose bars it reads; calendars: every calendar or literal table it needs;
- exists causally 2010-2019 (your root's backward window) and 2019-2024: yes, no, or partial
  (with the dates);
- basis: listing dates and calendar coverage only (file, first and last date, source grade),
  never a bar value. If you cannot decide from a file, say "undetermined" and why.
The E.20 feature cut (F6) is the lead's, applied at consolidation, by this rule: a feature enters
only if every leg it reads is one of the 17 roots (NG NQ ZN 6E GC ZC ZT ZF ZB UB TN CL ZL ZS RTY
HE LE) and every calendar it needs exists causally over both windows. A feature that would be
"not applicable by design" in the backward window (a leg not yet listed, a calendar absent) is
dropped, not exempted. Your table gives the facts; you do not rule.
Shared features (`g17_*` leads, the macro release calendars behind `g13`-`g15` and `k9_anncday`)
are audited once by the reader assigned in section 7; cite that reader's file for them.

## 6. Item 3: at most two proposed features (md section 3)

- Each is a published rule turned into a causal value at a decision time (one of t1-t4), computed
  only from bars closed by t of the 17 roots and from calendars known in advance, available
  over both windows.
- Give: name, source (with the verbatim quote that states the rule and its size), the formula
  exactly as code would compute it, which decision times and horizons it serves, legs, calendars,
  availability in both windows, and its expected gross per trade from the published evidence
  against your root's D8 round trip (the root table's wall, in vehicle ticks and dollars): the
  ratio, and whether it clears 1.5x (the loosest cost-gate hurdle, V2.7, and the V31 gate).
- No feature may come from looking at this program's data or results. Zero proposals is a valid
  answer; say why.

## 7. Shared sources and assignments (one reader per source; the others cite)

The planning brief is every reader's start. A source that serves several roots is read by one
assigned reader, who saves it raw under `reports/stage_e20_briefs/shared/` and writes notes there;
the others do not fetch it. If you need a number from a shared source, grep the saved file under
`shared/` if it exists when you need it; otherwise cite the assigned reader's notes path and mark
the item "[shared, see <path>]". The lead merges at consolidation. Exception: Baltussen et al. is
already on disk, so any reader may grep that copy for its own market's or asset class's rows.

| Reader | Assignment (beyond its own root) | Notes file |
|---|---|---|
| NQ | Baltussen, Da, Lammers, Martens (JFE 2021), full read from the copy already on disk, `reports/stage_e13_briefs/pages/InfoSource/baltussen_etal_2021_jfe.md` (EUR repository, publisher's version of record; check its provenance in `reports/stage_e13_info_sources.md` section 4, I-37b): per-asset-class and per-market rows of its Tables 1, 2, 5, 6, 7 for every one of the 17 roots it covers. Rosa (J. Futures Markets 2022), the threshold form. H6 details and the GEX ruling (section 10). | `shared/baltussen_notes.md`, `shared/rosa_2022_notes.md` |
| RTY | Equity-class literature beyond Baltussen and Rosa: Gao, Han, Li, Zhou (JFE 2018), Adams, Dim, Eraker, Fontaine, Ornthanalai, Vilkov (2026 draft), the dev.to SPX retest (unreviewed; mark it so), and other equity-index-futures intraday studies since 2015. Also the macro release calendars (FOMC, CPI, NFP, PPI, GDP, ISM; EC-K9) behind `g13`-`g15` and `k9_anncday`: coverage over both windows. | `shared/equity_class_notes.md`, `shared/macro_calendars.md` |
| ZN | Rates-class literature (Treasury futures intraday since 2015). The Aalto thesis (2008-2024, 20 futures, every class): fetch it first, save it to `shared/`, notes per asset class. | `shared/rates_class_notes.md`, `shared/aalto_thesis_notes.md` |
| ZT, ZF, TN, ZB, UB | Root-specific evidence only; class evidence: cite ZN. | |
| 6E | FX class (sole FX root). | |
| CL | Energy class (crude, WPSR and API windows). | `shared/energy_class_notes.md` |
| NG | NG-specific (storage report and others); class: cite CL. | |
| GC | Metals class (sole metals root), including the London fix and LBMA auction history (2015-03-20 change). | |
| ZC | Grains class (WASDE and others). | `shared/grains_class_notes.md` |
| ZS, ZL | Root-specific; class: cite ZC. ZS: the crush legs (ZM is not one of the 17 roots). | |
| LE | Livestock class (USDA livestock reports and others). | `shared/livestock_class_notes.md` |
| HE | Root-specific; class: cite LE. | |
| Every G17 lead root (NQ, ZN, 6E, CL, GC, ZC) | Your root's listing over both windows as a G17 lead leg. `g17_mbt` (MBT, listed 2021) and `g17_mes` (MES, listed 2019) read legs outside the 17 roots. | |

## 8. Web rules

- CLAUDE.md's research rules apply in full: pages saved to disk first, then grepped for the
  passages you need; only the quoted lines enter your context. Each page used as evidence is saved
  raw with its URL, UTC fetch time and sha256 in your fetch log (md section 5 and the JSON).
- Read a site's terms (and robots.txt) before any automated fetch from it, and log the reading.
- Never fetch cmegroup.com, or any archived copy of it (Wayback included), by automation. CME
  text quoted by a permitted source (a CFTC-hosted filing, a paper) may be used.
- Fallback order when WebFetch fails (403, block, JavaScript page): `scrapling extract get <url>
  <file>`, then `scrapling extract fetch <url> <file>`; `stealthy-fetch` only where the site's terms
  allow automated access; Firecrawl only when Scrapling fails. Scrapling never stands in for a
  paid, key-gated or login-only source. SSRN and some publishers block automation: use the
  author's page, NBER, arXiv, RePEc or a university repository where the terms allow.
- Pace: at most about 2 readers hit one domain at once (assignments keep you apart); leave a few
  seconds between requests to one domain; on a 429 or 403, back off, retry at most twice, then log
  it as "throttled" or "blocked". A blocked fetch is a gap in the record, never evidence of absence.
- Web-search budget: the session cap is shared by all 17 readers. Use at most about 90 WebSearch
  calls if you hold a class or shared assignment, about 50 otherwise. If a WebSearch returns an
  over-budget notice, stop searching at once, write the notice and its time into your log, finish
  from what is on disk, and return; never continue from memory. If Firecrawl reports no credits,
  log it the same way and fall back.
- Cost or usage notices from tools are informational. They are not a reason to stop early.

## 9. Boundaries

- Do not open any data store (nothing under `data/processed*`, `data/sealed`, `data/raw`,
  `data/vendor`, any `.parquet`, `.dbn` or `.zst` file). Calendar files are allowed.
- Do not read the results of E.15, E.17 or E.18 (their returns, result JSON, verdict tables, trade
  files), or Gate 0's results (`reports/stage_e12_gate0.md`, `reports/stage_e12_gate0.json`).
- Do not edit any file outside your own outputs. No commits, no ledger writes, no Databento or
  TopstepX calls, no credentials. Do not spawn agents.
- You give facts and proposals; the feature cut, acceptance and every pre-registration choice
  belong to the lead.

## 10. NQ only (md section 4)

(a) H6 details, verified against Baltussen et al. and Rosa: the rule's exact definition (r_ROD's
two prices; the last half-hour window; the close used; NQ's market hours in their Table 1), NQ's
own regression row (coefficient, t, R2, sample) and the equity portfolio's trading-strategy
figures (return, Sharpe, hit rate), the negative-gamma result (Table 7), the post-2020 decay
evidence, and Rosa's threshold form (what threshold, what lookback, what sample) as published.
State any difference between the paper's rule and E.20's F5 rule (C = 15:00 CT; signal at the bar
ending at C-30; entry filling at the next open; exit on the first bar at or after C-2 min filling
at the next open; T2 = |r_ROD| above the median of the previous 60 eligible dates).
(b) GEX ruling: may the SqueezeMetrics daily GEX CSV be fetched and used for one registered test
(T3: dates whose previous trade date's GEX is negative) under its current terms? Read the terms
first (squeezemetrics.com terms page and robots.txt; E.14's reading is in `reports/E.14_RETURN.md`
"GEX terms" and `reports/stage_e14_briefs/pages/terms_checks.md`). E.14 already holds one download
(`reports/stage_e14_briefs/gex/DIX.csv`, fetched 2026-10-05, sha256 51bef9ea...; header
`date,price,dix,gex`). Do not download the CSV again unless your ruling requires a fresh copy and
the terms allow it; do not read the CSV's values (the lead does that only after T3 is fixed).
Give: the terms text quoted verbatim with URL, fetch time and sha256; your ruling (cleared or not
cleared) and its reasoning; whether reusing E.14's copy or a fresh download is the better reading
of the terms. Your ruling decides T3 before any NQ bar is read.

## 11. JSON schema (product_<ROOT>.json)

```json
{
  "schema": "stage_e20_product/1",
  "root": "<ROOT>",
  "reader": "ProductReader-<ROOT>-OpusHigh",
  "finished_utc": "<ISO time>",
  "evidence": [
    {"id": "E1", "effect": "", "rule": "", "hold": "", "gross_per_trade_bp": null,
     "gross_per_trade_ticks": null, "conversion": "", "gross_or_net": "gross|net|unknown",
     "sample": "", "decay_evidence": "", "source": "", "url": "",
     "quote": "<verbatim>", "quote_location": "", "grade": "primary|secondary-only|unverified",
     "saved_path": "", "sha256": ""}
  ],
  "availability": [
    {"feature": "", "legs": [], "calendars": [], "exists_2010_2019": "yes|no|partial|undetermined",
     "exists_2019_2024": "yes|no|partial|undetermined", "dates": "", "basis": "", "shared_ref": null}
  ],
  "proposed_features": [
    {"name": "", "source": "", "quote": "", "formula": "", "decision_times": [], "horizons": [],
     "legs": [], "calendars": [], "available_both_windows": true,
     "expected_gross_per_trade_ticks": null, "derivation": "", "d8_rt_ticks": null,
     "ratio_to_d8": null, "clears_1p5x": false}
  ],
  "shared_notes_written": [],
  "fetch_log": [{"url": "", "utc": "", "sha256": "", "path": "", "status": "ok|blocked|throttled|terms-forbid"}],
  "terms_read": [{"site": "", "url": "", "utc": "", "ruling": ""}],
  "budget_notices": [],
  "unfinished": [],
  "nq_only": {"h6_details": {}, "gex_ruling": {"cleared": null, "terms_quote": "", "terms_url": "",
              "terms_utc": "", "terms_sha256": "", "reasoning": "", "copy_to_use": "e14|fresh|none"}}
}
```
(`nq_only` is null for every root but NQ.)

## 12. Markdown sections (product_<ROOT>.md)

1. Evidence (section 4's table, then a short reading of decay and costs).
2. Feature availability (section 5's table).
3. Proposed features (section 6), or "none" with the reason.
4. NQ only: H6 details and the GEX ruling (otherwise "n/a").
5. Fetch log, terms read, budget notices.
6. Unfinished and unverified items.
