# Stage E.10 return: low-frequency full-session holds (K9): literature research and a draft catalog

Lead Opus 5.5 (claude-opus-5-5), effort xhigh; ultracode off. Run 2026-10-02 22:20 PDT to 2026-10-03
00:15 PDT, unattended, no pauses. No market data read, nothing bought, no freeze, no code. One commit
(section 2).

## 1. Verdict summary

The literature yields **one K9 member that survives every check: K9-anncday-01, the macro-announcement-day
premium.** It is long the US equity index over each trade date that carries FOMC, payrolls, GDP (first or last
estimate), ISM manufacturing, or the earlier of CPI/PPI. The fill is at 18:00 CT the prior evening and the exit
at 14:59 CT, about 21 hours. It trades MNQ (q_c 1), M2K (3) and MYM (3): **3 trials of the 40-trial budget,
projected N 198 → 201.** It is labelled source-overlap (main source sample to 2023-08). It expects 58
announcement dates in the window, 53.0 after the weekly cap on the 299 screened dates, and 44.5 in the worst
case (above the proposed 30-trip floor).

On paper it clears the cost wall M_X on all three exposures (1.6x to 6.5x), but its documented move is
about one ninth of what eps_X would need at this frequency. The design target shows that this holds for any
low-frequency trial: a K9 edge can only be a component edge.

Two members were drafted and withdrawn, with full texts kept for the user. **K9-vixspike-01** was withdrawn on
the Fable review's R-01: a one-day VIX change fails the X10 test fixed before any source was read.
**K9-vixback-01** was withdrawn because its state persists under the weekly cap. Seventeen other candidates are
excluded with reasons. Commodity, FX and rates evidence fell below the cost wall, traded every day, was monthly,
or did not survive.

**The user owes 11 decisions (section 7):**
- the E-H1 overlap ruling, and the hold window;
- reinstating either withdrawn member;
- the 18:00 CT reopen entry, the 30-trip floor, Holm K = 10, the budget, the eps reading and the exposures;
- whether K9 goes to E.11 at all.

## 2. Guardrail evidence

Start (reports/stage_e10_briefs/start_checks.txt). The briefs folder had been created seconds earlier. The very
first command at 22:20:51 printed an empty `git status --short` (clean tree at ace7b9d, the commit holding the
E.10 prompt).

```
$ date
Fri Oct  2 10:21:06 PM PDT 2026
$ git status --short
?? reports/stage_e10_briefs/
$ git log --oneline -3
ace7b9d docs: E.10 prompt, Firecrawl as the logged last resort (matches CLAUDE.md)
efc3dcb docs: DECISIONS V20 (ML route v2, quant-style model, after K9)
b4496e1 docs: Stage E.10 prompt (K9 low-frequency research, draft catalog) and V19
$ uv run python -m data.holdout status (keys)
top all_ok True unlocks_logged 0 unlock_log_ok True
holdout_2 all_ok True unlocks_logged 0 unlock_log_ok True
MCL all_ok True unlocks_logged 0 unlock_log_ok True
MGC all_ok True unlocks_logged 0 unlock_log_ok True
MHG all_ok True unlocks_logged 0 unlock_log_ok True
NG all_ok True unlocks_logged 0 unlock_log_ok True
$ wc -c REGISTRATION.md
0 REGISTRATION.md
$ ledger
17400 ledger/databento_spend.jsonl
0b5466c4366ca9eaba7e10525545631c83e97c1184a7e745d5ed8ad47a9fe957
```

End, before the commit (reports/stage_e10_briefs/end_checks.txt):

```
$ date
Sat Oct  3 12:09:36 AM PDT 2026
$ git status --short
?? docs/STAGE_E_DESIGN_K9_DRAFT.md
?? reports/stage_e10_STATE.md
?? reports/stage_e10_briefs/
?? reports/stage_e10_catalog_K9.json
?? reports/stage_e10_catalog_K9.md
?? reports/stage_e10_catalog_review.md
?? reports/stage_e10_catalog_rulings.md
?? reports/stage_e10_design_target.md
?? reports/stage_e10_research/
?? reports/stage_e10_research_calendar.md
?? reports/stage_e10_research_commodity.md
?? reports/stage_e10_research_overnight.md
?? reports/stage_e10_research_regime.md
?? reports/stage_e10_search_plan.md
$ git log --oneline -3
ace7b9d docs: E.10 prompt, Firecrawl as the logged last resort (matches CLAUDE.md)
efc3dcb docs: DECISIONS V20 (ML route v2, quant-style model, after K9)
b4496e1 docs: Stage E.10 prompt (K9 low-frequency research, draft catalog) and V19
$ uv run python -m data.holdout status (keys)
top all_ok True unlocks_logged 0 unlock_log_ok True
holdout_2 all_ok True unlocks_logged 0 unlock_log_ok True
MCL all_ok True unlocks_logged 0 unlock_log_ok True
MGC all_ok True unlocks_logged 0 unlock_log_ok True
MHG all_ok True unlocks_logged 0 unlock_log_ok True
NG all_ok True unlocks_logged 0 unlock_log_ok True
$ wc -c REGISTRATION.md
0 REGISTRATION.md
$ ledger
17400 ledger/databento_spend.jsonl
0b5466c4366ca9eaba7e10525545631c83e97c1184a7e745d5ed8ad47a9fe957
```

After the end checks, this return, progress.md (one entry) and docs/STAGES.md (one line) were written. Then
came the single commit "Stage E.10 K9 research and draft catalog", which holds exactly the files listed above
plus those three. No tracked file other than progress.md and docs/STAGES.md changed. No frozen file, manifest,
docs/STAGE_E_DESIGN.md, docs/NULL_CRITERIA*.md or data/config.py was edited. No push, no Databento call, no
quote, no purchase. No key was printed or logged: a scan of every saved file found no .env value. Neither
holdout was touched: both all_ok with 0 unlocks at start and end, and the ledger is unchanged (17,400 lines,
same sha256).

**Guardrail deviations (reported, no effect found):**
- About 22:22 PDT, before Task 1, the lead grepped reports/ for "299" to trace the prompt's 299 research
  dates. The output printed line fragments of reports/E.3_RETURN.md and reports/E.4c_RETURN.md that hold
  result figures: a K3-ldnrev-01 6E mean per day and E.3's largest port mean. No design rule, member or
  literal uses them. The 299 figure is the prompt's calendar count.
- About 23:31 and 00:09 PDT, the lead printed the last progress.md entry and the docs/STAGES.md E.9 line to
  copy their format. Both contain E.9 result figures. By then the catalog and both rounds of lead rulings were
  final. The only later rulings are those on the Fable review, which turn on source text and the design
  target's pre-declared tests, and none uses those figures.
- The reviewer read progress.md lines on D.1's MES family E-H1 (pre-Stage E) to raise R-02. That is a D.1
  verdict, not a Stage E result.

## 3. Results per task

### Task 1: design target and exclusions (reports/stage_e10_design_target.md, sha256 ce798814..., fixed 22:29 PDT before any source was read)

- **Cost wall** per traded exposure, from the frozen D8 cost table and the E.2a epsilon report:
  - RT_X = commission + 2 x the worst bucket's one-side slippage;
  - M_X = 3 x RT_X, which ranges from 3.4 ticks (ZB, UB) to 32.6 (MBT);
  - G_X(f) = eps_X / f + RT_X, at f = 0.40, 0.20 and 0.10.

  **Finding:** for full-session holds the round trip is not the binding constraint; eps is. At two trades a
  week a trial must gross 0.32 to 1.03 x E|m_1| per trade, and at one a week 0.60 to 1.96 x. So a single
  low-frequency trial cannot plausibly reach eps_X, and a K9 edge would be a component edge (design draft
  K9-D).
- **Shape** (b):
  - at most two entries a week per product (the D-wk cap), one position at a time;
  - inside one trade date, hold of at least two hours, flat by F, market orders, size q_c, every D9 rule;
  - at least 40 expected trips;
  - default definitions D-ret, D-rng, D-pct (the 80/20 cut over a trailing 250 dates), D-exit, D-entry, and no
    grids.
- **Exclusion list** X1-X15: the three core ports, the release members (ISM pre-release drift, auctions,
  post-FOMC, energy inventories, WASDE), the fixes and auctions, overreaction reversal at any frequency, limit
  continuation, month-end, roll and expiry, cross-market leads, and the Monday MBT trend. Four borderline cases
  were named before any source was read. One correction is recorded in the rulings (R-02): X4's cell lists
  K1-predrift-01, which E.0 excluded with 0 trials.
- **Screen proposal** (d): D5 plus at least 30 completed round trips per trial (V18), with the arithmetic on
  299 dates.

### Task 2: search plan (reports/stage_e10_search_plan.md)

Ten topics in four reader groups:
- Regime: volatility states, large prior-day moves, range compression.
- Overnight: overnight-to-day relations, daily-scale TSMOM held in a session.
- Calendar: day-of-week, announcement-day premia, pre-holiday and expiry.
- Commodity: curve, carry and basis; inventory and seasonal regimes.

Each topic has OpenAlex/Semantic Scholar and web queries and a stated link to the cost wall.

### Task 3: search coverage

| Reader | Records screened | Sources logged | Full text | Abstract only | WebSearch calls | Stop |
|---|---|---|---|---|---|---|
| Regime (K9R) | about 460 | 25 | 16 | 8 (+1 summary page) | 38 | saturation, all three topics |
| Overnight (K9O) | about 450 | 19 | 11 | 8 | 23 | saturation, both topics |
| Calendar (K9C) | about 630 | 22 | 15 | 7 | 20 | saturation, all three topics |
| Commodity (K9M) | about 520 | 22 | 20 | 2 | 28 | saturation, both topics |
| **Total** | **about 2,060** | **88** | **62** | **25 (+1)** | **109 of the session's 1,000** | no budget notice |

**Used in the active member:** K9C-001, -002, -003, -004 and -007, with K9R-001 / K9C-006 for the excluded
variant row.

**Saved sources:** 291 files, 106 MB under reports/stage_e10_research/ (68 PDFs with text extractions, 36 HTML
pages, about 17 MB of OpenAlex search records, fetch logs with URL, UTC time and sha256).

**Semantic Scholar was unusable:** the .env key holds one character (403 with the key, 429 without). Per the
prompt, the readers continued with OpenAlex and the web, and logged it.

**Firecrawl** was used three times (Overnight 2, Commodity 1), each logged.

### Task 4: draft catalog (reports/stage_e10_catalog_K9.md and .json) and design draft (docs/STAGE_E_DESIGN_K9_DRAFT.md)

| Member | Condition | Hold | Exposures (q_c) | Expected trips (window / 299 screened, before and after the cap) | Cost wall | Label | Trials |
|---|---|---|---|---|---|---|---|
| K9-anncday-01 | The trade date carries FOMC, Employment Situation, GDP (first or last), ISM manufacturing or the earlier of CPI/PPI by reference month. Early-close, early-halt and closure dates are excluded. | Intent 17:59 CT the evening before, fill 18:00; exit at C_X - 2 min (fill 14:59); long | MNQ 1, M2K 3, MYM 3 | 58 / 56; 54.9 / 53.0 (worst case with the lapse-rescheduled BLS and BEA dates dropped: 46.4 / 44.5) | Clears M_X (6.5x MNQ, 1.62x M2K, 1.68x MYM via Savor-Wilson's ratio 0.145); about one ninth of G(f) | source-overlap | 3 |

- Withdrawn, with full texts in the appendices: K9-vixback-01 (Appendix A) and K9-vixspike-01 (Appendix B).
- 19 rows in the Excluded table.
- The catalog's section 8 verifies 138 quoted passages against the saved files.

**Design draft:**
- K9-A: K9 as its own Holm family with K = 10. The Bonferroni bound is 0.0544 if all eight earlier clusters were
  non-empty. It is immaterial because t > 3.0 means p < 0.00135, under 0.05/37.
- K9-B: the 30-trip floor.
- K9-C: the 40-trial budget (N at most 238; the DSR scale about 3.25 → 3.31).
- K9-D: the eps reading (component edge, D7 unchanged).
- K9-E: the step 2 path. The equity vehicles need their 2019-05..2025-03 history (E.0 quote $22.11-22.53)
  only if a Tier A trial appears.
- K9-F: the catalog table.
- K9-G: decisions and E.11/E.12 needs.
- K9-H: the 18:00 CT reopen entry, for the user's decision.

### Task 5: adversarial review (reports/stage_e10_catalog_review.md)

CatalogReviewer-FableXHigh: BLOCKING 0, SHOULD FIX 8, NOTE 8.
- All 123 passages were re-verified in the saved files. None was fabricated or misread by column, sample or
  sign, and one gloss was overstated.
- The arithmetic reproduces: trips, cap, unions, ratios, G(f), cost wall, Holm, DSR.
- The design target's hash matches, and its file predates the readers.

### Task 6: rulings (reports/stage_e10_catalog_rulings.md)

Every finding is ruled and applied (section 5).

## 4. Delegation record

| Spawn (description) | Agent file | Model | Effort | Start-end PDT | Time | Tokens (transcript) | Status |
|---|---|---|---|---|---|---|---|
| LitReader-Regime-OpusHigh | worker-high | opus | high | 22:32-22:52 | 20 min | 26,041,043 | accepted: 25 sources, saturation |
| LitReader-Overnight-OpusHigh | worker-high | opus | high | 22:32-22:54 | 22 min | 26,118,443 | accepted: 19 sources, 77 passages script-checked |
| LitReader-Calendar-OpusHigh | worker-high | opus | high | 22:33-22:52 | 20 min | 22,483,478 | accepted: 22 sources |
| LitReader-Commodity-OpusHigh | worker-high | opus | high | 22:33-22:54 | 21 min | 23,139,818 | accepted: 22 sources |
| CatalogWriter-OpusXHigh (round 1) | worker-xhigh | opus | xhigh | 22:58-23:22 | 24 min | 18,986,408 | done: 3 members, 17 questions |
| CatalogWriter-OpusXHigh (round 2, resumed) | worker-xhigh | opus | xhigh | 23:24-23:30 | 6 min | 5,540,591 | done: round-2 rulings applied |
| CatalogWriter-OpusXHigh (round 3, resumed) | worker-xhigh | opus | xhigh | 23:59-00:08 | 9 min | 12,829,055 | done: review rulings applied, recount |
| CatalogReviewer-FableXHigh | worker-xhigh | fable | xhigh | 23:31-23:56 | 25 min | 2,985,036 | done: 0 B, 8 SF, 8 N |

The four readers shared the session scratchpad for helper scripts. Two overwrote each other's helpers at
22:34, and two readers moved misplaced files back. No evidence file was affected (regime and calendar logs).

## 5. Verification

| Finding | Grade | Ruling | Fix applied |
|---|---|---|---|
| R-01 K9-vixspike-01 vs X10 | SHOULD FIX (BLOCKING on the stricter reading) | Accepted: the one-day ΔVIX condition fails the pre-declared "volatility level" test; the source correlates it -70% with returns, and Table 8 shows comparable next-day returns after price drops alone | Withdrawn to Appendix B; reinstatement conditions stated (test widened by the user, one cutoff, descriptive reversal diagnostic) |
| R-02 K9-anncday-01 vs D.1 E-H1 and E.0's K1-predrift-01 | SHOULD FIX | Kept on four grounds: D6 leaves announcement members to each cluster's literature; E-H1 was a non-resolution, not a null; date set, hold, exposures and source differ; the E.0 K1 brief does not govern K9 | Paragraph in the entry; E-H1 added to the variant's exclusion; user decision K9-G.1 |
| R-03 K9R-006 vs the label | SHOULD FIX (BLOCKING as written) | Accepted, fix (a); supersedes the lead's item-19 ruling | K9R-006 removed from the evidence and the JSON sources (Appendix B) |
| R-04 Table 8 gloss | SHOULD FIX | Accepted | Reworded to the source's claim; moved to the X10 risk paragraph |
| R-05 cutoff rule | SHOULD FIX | Accepted: no rule picked 1.0 over the source's 0.5 row | The rule stated; 0.5 offered as the reinstatement alternative |
| R-06 D-entry amendment not in the draft | SHOULD FIX | Accepted; the justification is a judgment, not a frozen rule | Design draft K9-H and K9-G.5 |
| R-07 "known in advance" for rescheduled BLS dates | SHOULD FIX | Accepted, plus BEA (writer's Q21) | Dates flagged; the E.11 check rule; worst-case recount 44.5 after the cap |
| R-08 pre-announcement row | SHOULD FIX | Accepted | "Weak" replaced by the source's statement; label and variance facts added; K9-G.2 |
| R-09 to R-16 | NOTE | R-09, R-16 applied in Appendix B; R-10 acknowledged (header times are the planned slot, hash intact); R-11 closed; R-12 accepted (early-close, halt and closure dates excluded, amending round 2 item 14); R-13 to R-15 acknowledged | as stated |

The lead's own checks:
- Spot checks of K9R-001 and K9C-003 against the saved texts (22:53, 22:55).
- The JSON parse check and totals.
- The design target's hash, recomputed at hand-off.

No number entering a verdict was produced in this stage (no screen), so no fable xhigh number check was needed
beyond the review.

## 6. Open choices (decisions the lead made on its own, with the reason)

1. **RT_X uses the worst 30-minute bucket on both sides** (equal to D8's event-window round turn). It is
   conservative and holds for any entry time.
2. **The context ratio G / E|m_1| reads E|m_1| from the frozen E.2a epsilon report.** It is used only to judge
   whether a target is reachable; no literal uses it.
3. **The design target's default definitions and frequency band were fixed before any source**: D-ret, D-rng,
   D-pct (80/20 over a trailing 250), D-exit, D-entry, D-wk, no grids, a 10% to 40% band, and at least 40
   expected trips. The 40 is a one-third margin over the proposed 30 floor.
4. **The exclusion list covers every catalogued K1-K8 mechanism.** E.0's excluded entries may be revisited only
   with a stated reason. The four borderline cases were named in advance.
5. **The topics were split into four reader groups**, each with 120 WebSearch calls, a saturation stop and
   about 70 minutes.
6. **Semantic Scholar's one-character key:** the readers continued with OpenAlex and the web, as the prompt
   directs for a missing key, and logged it.
7. **Catalog writing went to one CatalogWriter**, resumed twice by SendMessage for well-specified rounds 2 and
   3, rather than fresh workers re-reading the logs.
8. **Round 1** admitted three members and excluded seventeen candidates. The VIX-spike cutoff was 1.0 by
   (b)1; R-05 later showed the source's 0.5 row was not considered.
9. **Round 2:**
   - kept the VIX-spike non-announcement filter, because the source's statement outranks the writer's
     arithmetic inference;
   - withdrew VIX-backwardation;
   - moved reopen entries to an 18:00 CT fill (now K9-H for the user);
   - paired inflation releases by reference month;
   - restated the Treasury row's reasons;
   - ruled that K9R-006 did not change the label (later superseded by R-03).
10. **Rulings on the review:**
    - withdrew VIX-spike (R-01) and kept announcement-day (R-02);
    - flagged the lapse-rescheduled BLS and BEA dates rather than fetching more pages in E.10 (R-07, Q21);
    - excluded early-close, early-halt and closure dates, following K8's precedent (R-12);
    - kept the full-day window over the pre-announcement variant, with the trade-off stated for the user (R-08).
11. **All three equity exposures for the member.** The S&P 500 evidence transfers to large-cap, small-cap and
    price-weighted indices, and the extra trials are cheap. The user may keep the Nasdaq-100 only.
12. **The design target's header times ("22:40-23:10") were left unedited**, because editing would break the
    recorded hash. The file's mtime 22:29:01 and the hash time 22:29:07 are authoritative (R-10).
13. **All saved sources are committed: 106 MB, 291 files**, including the OpenAlex search records that back
    the coverage counts. The prompt requires the saved sources in the commit, and no file is over 7.4 MB. The
    repository grows by about that much.
14. **The platform's product name was removed from the stage's own guardrail sentences** (the search plan and
    the reviewer brief), so no stage file names it.
15. **Session cost uses a corrected script.** reports/stage_e10_briefs/cost.py takes the final usage per
    streamed message. The E.4 script keeps the first record per message, which undercounts output tokens (E.10:
    writer 8,285 vs 256,608; Fable 1,170 vs 116,450). Earlier stages' Session cost tables built with it likely
    undercount output tokens. Input and cache, which dominate the totals, are unaffected. Flagged for the user.
16. **K9-A recommends K = 10**, with 0.05/18 as the strict alternative. **K9-D proposes the "component edge"
    reading** without changing D7 or any eps.
17. **"The ledger total" is reported as the spend ledger's line count and sha256**, E.9's convention.
18. **The two incidental exposures to Stage E result fragments** (section 2) are disclosed. Neither was used.

## 7. Decisions for the user (the lead's recommendation first)

1. **K9 as its own Holm family, with maximum K = 10.** Recommended: K = 10 for K9 and the ML route, with the
   bound arithmetic recorded. The t > 3.0 gate makes the choice immaterial. The strict alternative is
   0.05/18 each.
2. **The minimum trade count.** Recommended: 30 completed round trips per trial on the research window. The
   alternatives are 20 or 50.
3. **The trial budget.** Recommended: keep the cap at 40. The draft uses 3.
4. **K9-anncday-01 against D.1's E-H1.** Recommended: keep it. The alternative is to cut it for consistency
   with E.0's K1-predrift-01 exclusion, which leaves K9 empty.
5. **K9-anncday-01's hold window.** Recommended: the full announcement day. The alternative is the
   pre-announcement variant (the prior evening to 5 minutes before NFP, ISM or GDP). The variant is not
   source-overlap and has lower variance, but it is E-H1's window on MES's research window.
6. **Members to cut or reinstate.** Recommended: no reinstatement.
   - K9-vixspike-01 can be reinstated only by widening the X10 borderline test to a one-day change. It would
     then need one cutoff (0.5, about 62 capped trips; or 1.0, about 37 with a margin waiver) and a descriptive
     reversal diagnostic, at +3 trials.
   - K9-vixback-01 is not recommended for reinstatement.
7. **Reopen entry** (K9-H). Recommended: fill at 18:00 CT. The alternative is the 17:00 CT first bar.
8. **The eps reading** (K9-D). Recommended: report each Tier A mean as a fraction of eps_X, and call a sub-eps
   edge a component edge for V20's ML route v2.
9. **Exposures.** Recommended: MNQ, M2K and MYM. The alternative is MNQ only (1 trial).
10. **Whether K9 proceeds to E.11 and E.12.** Recommended: yes. It costs 3 trials and no purchase. The
    alternative is to fold the member into V20's ML route v2 as a feature.
11. **The cost-script finding** (open choice 15). Decide whether earlier stages' Session cost output figures are
    re-run with the corrected script.

**What E.11 (freeze) will need:**
- the decisions above, written into a design amendment and docs/DECISIONS.md;
- BLS's and BEA's revised-schedule notices, to keep or drop each date the lapse moved;
- ISM's actual release dates;
- the CME early-close and holiday sessions in the window;
- the member text hashed into a K9 freeze manifest.

**What E.12 (code and screen) will need:**
- the member coded against the frozen text;
- the K9 announcement calendar built from official pages, with dates as known at each entry intent;
- the screen: D5 plus the trade floor, Holm at the agreed K, the per-trial eps fraction and D9.7 exit counts;
- a Fable audit before any verdict.

No purchase: MNQ, M2K and MYM research-window bars are owned. A confirmation would later need the equity
step 2 history (E.0 quote about $22) on acct-2, after V19's account-key preconditions.

## 8. Session cost

Counted from this session's transcripts with reports/stage_e10_briefs/cost.py, which takes the final usage
per streamed message (see open choice 15). Inputs: the lead transcript c0c85ee1-61ec-4348-b692-3b35ab945cfd.jsonl
and its subagents/*.jsonl, UTC slice 2026-10-03T05:15:00Z to 07:13:11Z (00:13 PDT). The lead's last messages
after the cutoff (the progress entry and the commit, about 2 minutes) are not counted. Raw output:
reports/stage_e10_briefs/cost_final.txt. These are token counts, not plan-credit percentages. The user reads
the /usage meter.

**Wall clock.** 2026-10-02 22:20 PDT to 00:15 PDT on 2026-10-03 (commit at 00:14): about 1 h 55 min, with no pauses or
outages, so work time equals wall time. The initial estimate was 4 h 50 min (ETA 03:10). The readers took 20-22
minutes against 60 estimated, the catalog and its rounds about 70 minutes against 60, and the review 25 minutes
against 45.

**Final table** (PDT; tokens are transcript totals; lead slices overlap by a few messages, so the lead total
row is authoritative):

| Row | Owner | Model | Effort | Start | End | Time | Tokens | Status, deviations |
|---|---|---|---|---|---|---|---|---|
| 0-2 Startup, design target, search plan | lead | opus | xhigh | 22:20 | 22:31 | 11 min | 8,250,978 | done; estimate 70 min |
| 3 Readers (lead waiting, spot checks) | lead | opus | xhigh | 22:32 | 22:55 | 23 min | 5,796,123 | done |
| 3a LitReader-Regime-OpusHigh | worker-high | opus | high | 22:32 | 22:52 | 20 min | 26,041,043 | accepted |
| 3b LitReader-Overnight-OpusHigh | worker-high | opus | high | 22:32 | 22:54 | 22 min | 26,118,443 | accepted |
| 3c LitReader-Calendar-OpusHigh | worker-high | opus | high | 22:33 | 22:52 | 20 min | 22,483,478 | accepted |
| 3d LitReader-Commodity-OpusHigh | worker-high | opus | high | 22:33 | 22:54 | 21 min | 23,139,818 | accepted |
| 4 Rulings rounds 1-2, design draft | lead | opus | xhigh | 22:55 | 23:31 | 36 min | 8,588,006 | done |
| 4b CatalogWriter-OpusXHigh round 1 | worker-xhigh | opus | xhigh | 22:58 | 23:22 | 24 min | 18,986,408 | done; 17 questions |
| 4d CatalogWriter-OpusXHigh round 2 (resumed) | worker-xhigh | opus | xhigh | 23:24 | 23:30 | 6 min | 5,540,591 | done |
| 5 CatalogReviewer-FableXHigh | worker-xhigh | fable | xhigh | 23:31 | 23:56 | 25 min | 2,985,036 | done; 0 B, 8 SF, 8 N |
| 5 (lead during the review: checks, return prep) | lead | opus | xhigh | 23:31 | 23:56 | 25 min | 2,504,092 | done |
| 6 Rulings on the review, design draft F-H, return | lead | opus | xhigh | 23:56 | 00:13 (cutoff) | 17 min | 13,460,226 | done |
| 6b CatalogWriter-OpusXHigh round 3 (resumed) | worker-xhigh | opus | xhigh | 23:59 | 00:08 | 9 min | 12,829,055 | done |
| Pauses or outages | | | | | | 0 | | none |
| **Stage total** | | | | 22:20 | 00:15 | **about 1 h 55 min** (estimate 4 h 50 min) | **176,034,389** | lead 37,910,517 (21.5%); workers 138,123,872 (78.5%) |

**Tokens per model:**

| Model | Input | Output | Cache read | Cache creation | Total |
|---|---|---|---|---|---|
| claude-fable-5-1 | 418 | 116,450 | 2,527,920 | 340,248 | 2,985,036 |
| claude-opus-5-5 | 1,656 | 857,034 | 169,735,011 | 2,455,652 | 173,049,353 |
| all | 2,074 | 973,484 | 172,262,931 | 2,795,900 | 176,034,389 |

**Per worker spawn:**
- LitReader-Regime-OpusHigh: worker-high, opus, high, 26,041,043.
- LitReader-Overnight-OpusHigh: worker-high, opus, high, 26,118,443.
- LitReader-Calendar-OpusHigh: worker-high, opus, high, 22,483,478.
- LitReader-Commodity-OpusHigh: worker-high, opus, high, 23,139,818.
- CatalogWriter-OpusXHigh: worker-xhigh, opus, xhigh, 37,356,054 over three rounds (18,986,408, 5,540,591 and
  12,829,055).
- CatalogReviewer-FableXHigh: worker-xhigh, fable, xhigh, 2,985,036.

**Delegation share:**
- The lead took 21.5% of tokens and the workers 78.5%.
- By tier: Opus lead 21.5%, Opus workers 76.8%, Fable 1.7%.
- Cache reads are 97.9% of all tokens.
