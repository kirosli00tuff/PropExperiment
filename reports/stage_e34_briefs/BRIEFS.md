# Stage E.34 worker briefs (lead: Opus 5.5 max). Read `## RULES` first, then only your own section.

Find line ranges with `grep -n '^## ' reports/stage_e34_briefs/BRIEFS.md` and read by range.

## RULES

Stage E.34 (2026-10-29) designs one ZL (CBOT soybean oil) directional program for Topstep and freezes its discovery
protocol for a later run stage. Two families in one future registration: F10 order-book state at 5 minutes and longer,
and F09 soy-complex lead-lag and relative value into ZL. Discovery dates 2020-12-01..2024-02-29; the single sealed test
read 2017-05..2020-11 belongs to a later stage. Prior about 4%. This stage buys nothing, registers nothing, trains
nothing and reads no outcome. N stays 838 (ledger r009-E33).

Hard rules (a breach voids your work):
1. Never open, decode, summarise or derive anything from ZM, ZS or ZL data of any schema dated 2017-05-01..2020-11-30
   (the sealed test window; sealed blobs live under data/sealed/), or any market data dated 2024-03-01 or later. Never
   open data/vendor/databento/rolls/*, reports/stage_e20_briefs/pages/ZL/fred_PSOILUSDM.csv, the E.12/E.14/E.20 ML
   caches (~/.cache/propexp_*) or any file listed in reports/stage_e32_briefs/seal/derived_unsealed_files.tsv.
2. Compute no price, return, feature value, label, markout or model output, and train nothing. Only DataFacts reads
   market-data files at all (counts and schemas only, through its guard).
3. Do not copy numeric results of statistics earlier stages computed on ZL data (means, t-stats, split results) into
   your outputs. Record what was computed, on which dates, with which labels, and where the value is recorded
   (file:line). Aggregate program outcomes already in RETURN summaries (for example "E.33: Tier A empty, best -1.098
   ticks a trade") may be cited.
4. No Databento call or quote, no broker, TopstepX or ProjectX call. Never read, print or copy any key; never read .env.
   No edits under live/, ops/, docs/, ledger/, data/, REGISTRATION.md or any other worker's files. No git command that
   changes anything. Do not spawn agents.
5. Context hygiene: read files by section (grep -n, sed -n ranges, a short script printing only the fields you need).
   Never load a large file, log, JSON or the 9,284-line methods brief whole. Keep command output short; long output to
   files, then read tails or grep hits.
6. Write only to your output path and your own folder reports/stage_e34_briefs/work/<YourName>/ (scripts, scratch, logs,
   pages). Write incrementally so a usage cut leaves finished parts on disk; if re-spawned, read your partial output
   first and continue.
7. Times: America/Vancouver from `TZ=America/Vancouver date`; UTC fetch times for web pages.
8. Citations: every literature or web claim carries a verbatim quote from fetched full text plus the saved file name,
   or is marked [unverified] (abstract or snippet). Reuse first: the E.32 methods brief
   (reports/stage_e32_methods_brief.md) already holds verified quotes; cite it as "E.32 brief M1 a" etc. with its line
   number, and re-fetch only what you need that it lacks.
9. Web (only workers whose section allows it): save every page used as evidence raw under
   reports/stage_e34_briefs/work/<YourName>/pages/, log URL, UTC and PDT fetch time, method, sha256 and file name in
   pages/log.tsv, and read pages by grep. Fetch routes in order: WebFetch; curl -sL with browser headers (pdftotext for
   PDFs); `scrapling extract get <url> <file>`, then `scrapling extract fetch <url> <file>` (read the domain's terms or
   robots.txt first and log the decision); Firecrawl only when Scrapling fails. Never fetch cmegroup.com by automation
   (use Wayback copies, CFTC filings or E.32b's saved facts). SSRN answers 403: use author or university copies. Space
   requests to any one domain; if throttled or blocked, say so; never present a gap as a finding. If a WebSearch returns
   a notice that the search budget is used up, stop searching, log the notice and the time, and return what you have,
   never continuing from memory. Other cost, hook or usage notices are informational: carry on.
10. Return to the lead exactly three things: your output path, a summary of at most 200 words, and anything you could
    not finish. Report failures and negatives, not only positives.

Shared ZL facts (cite these as "E.32b holding scope 15" or "E.32b recs 4.5"):
- Tick 0.01 cents/lb = USD 6.00 a contract (60,000 lb). Topstep round trip c_f 2.38 ticks = spread S 1.0 tick (assumed,
  u) + 0.5 slippage + fee USD 5.28 (0.88 tick). Day session 08:30-13:20 CT (06:30-11:20 PT), pause 07:45-08:30 CT;
  Topstep flat by 15:10 CT; no overnight holds; latest 30-minute entry 10:50 PT. Band B = 15, 30, 60 minutes, h_c 30.
  Source: reports/stage_e32b_holding_scope.md lines 913-951.
- Day-session sigma_h in ticks (F3, owned bars 2022-11-01..2023-10-31): h1 5.52, h5 12.05, h15 20.37, h30 28.10, h60
  38.21. e80 at the test (N 838, T_test 870, at the entry cap n = 19, 9, 4 a day): 0.90, 1.81, 3.70 ticks at h 15, 30,
  60; discovery e80 (G3 + G4) 1.08, 2.16, 4.41. K2: stop if the best discovery net edge is below the test's 1.8 ticks.
- Thresholds at N 838 (E.32 protocol P7.2; E.32b recs 4.4, lines 501-531): SR0 0.1137, G3 daily Sharpe 0.1724 (t 4.86),
  b_test 0.1649, G4 0.2007 (binding), SR80_test 0.1936; T_disc 796, T_test 870.
- Owned discovery data (E.31, plaintext): ZL MBP-1 front month data/vendor/databento/GLBX.MDP3/mbp-1/Z3_ZL_v_0/ (39
  monthly files from range=2020-11-30T220000Z, 3.5 GB; E.33 split it into 158,044,028 records on 816 dates); ZS MBP-1
  Z2_ZS_v_0 (5.4 GB); ZM MBO Z1_ZM_v_0-ZM_v_1; definitions Z4_ZM_FUT-ZS_FUT-ZL_FUT; ohlcv-1m ZL_v_0, ZS_v_0, ZM_v_0
  for 2020-12..2024-02 (39 files each). CL ohlcv-1m is owned 2010-07..2026-06; HO and RB ohlcv-1m only 2025-04..2026-06
  (closed: 2024-03 onward). No ZL MBO is owned.
- Test window (sealed, later stage): ZL MBO exists from 2017-05-21 (test trade dates 2017-05-22..2020-11-30); test bars
  for ZL, ZS, ZM are owned inside the sealed files. Cost estimates (E.32b recs 4.5(c), estimates, not quotes): ZL MBO
  discovery USD 19.48; ZL MBO test USD 21.48; ZL MBP-1 test USD 23.36; definitions for the test window not priced.
- Model rule (V43, docs/DECISIONS.md lines 788-806): ML may be the traded strategy only for order-book strategies; V28
  (rules only) elsewhere. E.33 ran its crush and propagation sets as ML inside an order-book program.

## ExposureExtract-HaikuMed

Objective: one table of every earlier read of ZL data, or computation using ZL data, whose dates intersect the
discovery dates 2020-12-01..2024-02-29, from the program's records. Extraction only: no conclusions, no judgments.

Sources (read by grep and line ranges):
- ledger/trial_registrations.jsonl (10 lines): per line print entry_id, stage, number of trial ids, and any key whose
  value mentions ZL or a soy root or a date window (print keys first; never print whole long lines).
- ledger/databento_spend.jsonl (37,290 lines): with a short script, count lines whose dataset/symbol fields mention ZL,
  grouped by (event type, schema, symbols, start, end); print only counts and date ranges.
- The E.23 inventory: reports/stage_e23_briefs/inventory/ and reports/stage_e23_briefs/inventory_compact.txt: every
  member or trial whose roots include ZL: id, mechanism (short verbatim phrase), data window, registration.
- reports/stage_e32_briefs/X1_exposure.md Tables B1-B8 and C (lines 87-326) and reports/stage_e32_briefs/X1_verify.md
  corrections that touch those rows; reports/stage_e32_test_seal.md lines 121-132.
- reports/stage_e32b_briefs/R1_closed_lines.md: every row naming ZL (for example R1-08, R1-11, R1-15, R1-20, R1-21).
- `ls reports/E.*_RETURN.md`, then grep -n 'ZL' in the returns of E.12, E.14, E.16/E.17, E.20, E.21, E.22, E.25, E.28,
  E.31, E.32, E.32b, E.33, E.33b, E.33c: keep lines describing a computation on ZL data.
- E.32b's volatility and holding work on ZL: reports/stage_e32b_briefs/F3_vol.md and F5_holding.md (grep ZL: window,
  statistic names only).

Output: reports/stage_e34_briefs/X_extract_records.md with one table, columns: stage | trial or registration id |
what was computed (verbatim phrase) | ZL data used (schema; dates) | overlaps 2020-12..2024-02 (yes / no / partial, with
dates) | labels (on ZL, or ZL only as an input to another product's label) | outcome recorded (where: file:line; no
numbers, rule 3) | source file:line. Then the row count per stage and a list of sources you could not read. Tools:
Read, Bash (grep, sed, short python). No web.

## CodeExtract-HaikuMed

Objective: list every place where the code of E.31, E.33 (with E.33b and E.33c additions) and E.32b's F3 reads ZL data,
and every quantity it computes from ZL data. Extraction only: no conclusions.

Sources: reports/stage_e31_briefs/work/pilot/*.py (pilot31_common, measure31, measure31_core, mbo_book31, kalgo31,
stats31, stats31_core, stats31_report, vol_measure, vol_pull); reports/stage_e33_briefs/work/pipeline/*.py (data33,
split33, cal33, feat33, lab33, cost33, g6_33, check33, guard33, search33, select33, synth33, run_search33,
build_features33, build_labels33); any .py under reports/stage_e33b_briefs/ and reports/stage_e33c_briefs/tools/;
reports/stage_e32b_briefs/work/F3/f3_core.py, f3_vol.py. Find ZL uses with grep -n for ZL, Z3_, "ZL.v.0", mbp-1,
instrument, and the feature tables in feat33.py. For E.33's feature ids, the protocol's definitions are in
reports/stage_e32_discovery_protocol.md lines 367-465 (P4).

Output: reports/stage_e34_briefs/X_extract_code.md with one table, columns: stage | file:line | function | ZL input
(schema; fields used: prices, sizes, timestamps, sides, actions) | dates | what is computed (verbatim from code or
comment) | ZL alone, or an input to a ZM label | output path | where a statistic of it is reported (grep the stage's
RETURN or stats files for the output or feature name; file:line only, no values). Then a second table of E.33 feature
ids that use ZL (id, verbatim formula line from feat33.py, protocol line). Row counts at the end. Tools: Read, Bash. No
web.

## ExposureAuditor-OpusHigh

Objective: write reports/stage_e34_exposure.md, the Part 0.2 exposure audit of ZL's discovery dates
2020-12-01..2024-02-29, as the stage prompt requires: "List every earlier read of ZL data and what was computed ...
State plainly which proposed features or labels were already looked at in any form. State how the protocol keeps that
exposure from steering its choices, or which choices are excluded because of it."

Inputs: reports/stage_e34_briefs/X_extract_records.md and X_extract_code.md (Haiku extractions: verify every row that
enters a verdict against its cited source and correct errors, saying so); reports/stage_e32_discovery_protocol.md P1.5
(lines 146-177, E.32's firewall for ZM, your model); reports/stage_e32_test_seal.md section 4 (lines 104-154);
reports/stage_e32_briefs/X1_exposure.md Table C (lines 209-326); docs/DECISIONS.md V50 item 4 (lines 1029-1055);
reports/stage_e32b_recommendations.md 4.2 L3 and L11 (lines 384-398, 442-463) and 4.5(b) P1 (lines 591-602);
reports/stage_e34_briefs/seal/part01_seal_check.md. The proposed features and labels to judge are E.32b's draft (recs
4.5(b), lines 589-633: F10 = E.32's F3 order-book features on ZL's own book; F09 = E.32's F1 crush residual and F2
propagation mirrored with ZL as the traded leg, ZS and ZM as leaders, possibly CL; context block C; labels F15, F30,
F60, T15, T30 on ZL) with E.32's exact definitions in reports/stage_e32_discovery_protocol.md lines 367-465.
Also disclose this stage's own exposure: the lead read reports/E.33c_RETURN.md sections 1-3.8 (aggregate ZM outcomes,
per-set gate counts and the top-10 configuration list) while orienting.

Required sections: (1) inventory table (stage; what was computed; ZL data and dates; labels on ZL or ZL as an input;
what of the outcome was published; source); (2) a per-item verdict for each proposed feature group and each label:
none / indirect (ZL used only as an input to another product's label, or volatility and calendar statistics) / direct
(an outcome with a ZL label, or a ZL order-book statistic conditioned on a candidate feature, for example E.31's
queue-imbalance splits of ZL markouts); (3) firewall rules for protocol P1.5, concrete and checkable (what the run
stage may and may not read, which earlier results may not be consulted, how the families' definitions are fixed from
E.32's frozen text and E.32b's draft rather than from any earlier result); (4) choices excluded because of exposure,
each with its reason, or "none" with the reason; (5) a verdict paragraph. Tools: Read, Bash. No web.

## MathReaderM1-OpusHigh

Objective: the M1 section of the ZL methods addendum: F10 (order-book state at 5 minutes and longer) on ZL. Prompt
text: "which of E.32's F3 order-book features carry over to ZL, which need MBO and which work from MBP-1, and the
minimum aggregation horizon given ZL's message rate. Decide whether discovery needs ZL MBO (a purchase in the run
stage) or can use the owned ZL MBP-1 front month. Give the reasons and the cost difference (E.32b 4.5(c))."

Inputs: E.32 methods brief M1 (reports/stage_e32_methods_brief.md lines 3613-4402) and R3b (2102-2686), M6 (8346-9187)
by search; the E.32 protocol's F3 family and features (reports/stage_e32_discovery_protocol.md lines 209-222 and
436-450), general feature rules (369-395), executable prices (262-276), data and sessions (88-145); E.33's code for F3
and the data layer (reports/stage_e33_briefs/work/pipeline/feat33.py, data33.py, split33.py; read by grep) to see how
each F3 feature was built from ZM MBO and which ZL MBP-1 inputs E.33 used; reports/stage_e32b_recommendations.md 4.5
(lines 532-657); reports/stage_e32b_briefs/F2_grains.md and F2_data_access.md (ZL book facts, MBO availability and
prices); the shared ZL facts above. Databento's public schema documentation (MBO, MBP-1, MBP-10 field lists and how
CME MBP-1 is generated) may be fetched under rule 9; at most 20 web searches. Part F (DataFacts) may write per-day
message counts to reports/stage_e34_data_facts.md while you work; use them if present, citing them, else the shared
facts.

Required content, per topic: equations, a worked ZL example (tick USD 6, sigma_30 28.10 ticks), data needs, leakage
traps, a verdict. (a) Carry-over table: every E.32 F3 feature (F3.1-F3.12) and the context block's book items: ZL
formula, computable from MBP-1 (yes / partial / no) and why, needs MBO, verdict (carry over / adapt / drop). (b) ZL's
message rate and the minimum aggregation horizon (state the reasoning, for example events per bucket needed for a
stable imbalance estimate, against E.32 brief M1's finding that order-flow predictability fades within about 30
minutes). (c) The decision for discovery, MBO or MBP-1, with reasons, the schema used in the test (the same schema in
both windows unless you show the features are identical), and the cost difference using the estimates above. (d)
Leakage traps (timestamps ts_recv vs ts_event, Topstep 1 s latency, roll dates, the pause, the 13:20 CT close). (e) A
"Protocol inputs" block at the end: the exact F10 feature list with formulas, windows, normalisations and parameters,
ready to paste into protocol P4. Output: reports/stage_e34_briefs/M1_F10_ZL.md. Tools: Read, Bash, WebFetch/WebSearch
under rule 9.

## MathReaderM2-OpusHigh

Objective: the M2 section of the ZL methods addendum: F09 into ZL. Prompt text: "the crush residual with ZL as the
adjusting leg (E.33 tested ZM as the adjusting leg); ZS and ZM leading ZL; the biofuel and energy linkages (CL, HO, RB)
as candidate leaders, only if the data is owned or free; whether ZL, not ZM, is the leg that adjusts, with the
half-life method. E.33's negative on ZM constrains what is plausible here; say how."

Inputs: E.32 methods brief M2 (lines 4403-5231) and R3a (1360-2101) by search (crush economics, cointegration,
VECM, half-life, oil-share regime, leadership); the E.32 protocol's F1 and F2 (reports/stage_e32_discovery_protocol.md
lines 184-208, 412-435); E.33's feat33.py by grep for the F1/F2 code; reports/E.33c_RETURN.md sections 1 and 3.4-3.8
(aggregate ZM outcome) and reports/E.33_RETURN.md section 3; reports/stage_e32b_recommendations.md 4.2 L11 (lines
442-463: E.12 and E.20 already searched 60-minute G17 leads NQ, ZN, 6E, CL, GC on ZL at h60-hF without a pass) and 4.5
(532-657); reports/stage_e32b_briefs/R1_closed_lines.md rows R1-08, R1-11, R1-15, R1-21; F2_grains.md. Literature:
use the E.32 brief's verified quotes first (Zhou et al. intraday crush cointegration, 180 of 243 sessions; Simon;
Rechner and Poitras; Mitchell; the oil-share regime); search for evidence on which leg adjusts in the board crush, on
soybean oil and energy (crude oil, heating oil or diesel, RINs) price transmission at intraday or daily horizons, and on
soybean oil lead-lag; at most 60 web searches; Opus-level care with full text.

Required content, per topic: equations, a worked ZL example (a 1 cent/bushel board-crush dislocation equals 1/11
cent/lb in ZL, about 9.09 ZL ticks; tick USD 6; sigma_30 28.10 ticks), data needs, leakage traps, a verdict. Cover:
(a) the crush residual with ZL as the adjusting leg (residual definition, causal normalisation as E.32 F1 requires,
the hedge ratios, and what share of a dislocation ZL must close to pay 2.38 ticks); (b) ZS and ZM leading ZL at minute
look-backs within the 15-60 minute band, and whether bars (ohlcv-1m, owned for both windows) suffice or the leaders'
books are needed (state the test-window data consequence: ZS and ZM book data for 2017-05..2020-11 would be a
purchase); (c) CL, HO, RB: data status (CL bars owned; HO and RB only 2025-04 onward, closed) and the exposure that E.12
and E.20 already used CL as a 60-minute lead on ZL; verdict include or exclude; (d) which leg adjusts: VECM loadings,
Gonzalo-Granger or information-share methods and the OU half-life (hl = -ln 2 / ln phi), how the run stage would
estimate them without turning a diagnostic into a selection (inside training folds only, or report-only), and what
the literature says for intraday soy; (e) how E.33's ZM negative (all five sets failed net, ZL an input leg) constrains
the prior for ZL as the traded leg; (f) a "Protocol inputs" block: exact F09 feature list with formulas, look-backs,
normalisations and parameters, plus any rule-based variant (V28 reading) if you judge F09 on bars must be rules.
Output: reports/stage_e34_briefs/M2_F09_ZL.md. Tools: Read, Bash, WebFetch/WebSearch under rule 9.

## MathReaderM3-OpusHigh

Objective: the M3 section of the ZL methods addendum: labels and holding band. Prompt text: "Labels and holding band
from E.32b's F5 (Topstep ZL band 15-60 minutes): the label set, cost-aware targets, and the trade-through and market
execution variants of E.32 M6."

Inputs: E.32 methods brief M3 (lines 5232-6146) and M6 (8346-9187) by search; the E.32 protocol P3 (lines 254-366:
horizons, executable prices, fixed-horizon and triple-barrier labels, trade rule, exclusions, weights, simulation) and
P6.4 (641-662); E.33's lab33.py and cost33.py by grep; reports/stage_e32b_holding_scope.md lines 913-951 (ZL) and
337-368 (firm rules); reports/stage_e32b_briefs/F5_holding.md and F2_firms.md (Topstep rules, news windows) and
F2_grains.md (ZL session, daily price limits, release calendars) by grep. ZL-specific events to consider: USDA WASDE,
NOPA crush reports, EIA, and EPA renewable-fuel (RFS/RVO) announcements; sources already in E.32b's files first; at
most 30 web searches (never cmegroup.com by automation).

Required content: equations, a worked ZL example (tick USD 6, sigma_15/30/60 = 20.37/28.10/38.21 ticks, c_f 2.38),
data needs, leakage traps, a verdict, for: (a) the label set inside B (E.33 used FH05, FH15, FH30, FH60, TB15, TB30;
E.32b's draft keeps F15, F30, F60, T15, T30); decide each label in or out, including whether a T60 triple barrier
earns a place, with reasons (power, session length 290 minutes, pause, flat-by); (b) cost-aware targets and the dead
zone (spread plus costs, never a tuned threshold) in ZL ticks; (c) executable prices from ZL's book with Topstep's 1 s
latency, and the trade-through and market execution variants of E.32 M6 for ZL; (d) the trade rule and entry limits
(non-overlapping holds, entries per day, latest entry times per horizon); (e) exclusions (open, close, pause, USDA
and other release windows, roll dates, ZL daily price-limit states and how E.33's rule 5 for ZM maps to ZL, low-
liquidity dates); (f) sample weights and rows per day; (g) a "Protocol inputs" block with exact label formulas and
parameters ready for protocol P3. Output: reports/stage_e34_briefs/M3_labels_ZL.md. Tools: Read, Bash,
WebFetch/WebSearch under rule 9.

## MathReaderM4-OpusHigh

Objective: the M4 section of the ZL methods addendum: power and N. Prompt text: "the minimum detectable net edge at
the discovery and test windows' lengths, at N 838 plus this program's budget, against E.32b's 1.8-tick test detectable
edge (K2)."

Inputs: E.32 methods brief M5a (lines 6919-7714) and M5b (7715-8345) by search; the E.32 protocol P7, P8 and P9 (lines
683-829); reports/stage_e32_briefs/protocol/p7_final.py and p7_final_budget300.md; the functions named in
reports/stage_e32b_recommendations.md 4.4 (lines 501-531: p7_final.se_sharpe and g4_threshold,
p7_thresholds.required_sharpe, funnel.multiple_comparisons.expected_max_sharpe; find them with grep -rn in the repo,
and E.32b's scripts hurdles.py and short_test.py if the scratchpad path still exists); reports/stage_e32b_holding_scope.md
section 1.5 (lines 255-298) and lines 913-951; reports/E.33c_RETURN.md section 3.7 item (v) (measured e80 against the
formula); screening/stage_e_verdict.py (Holm at K, the test verdict). Pure arithmetic: no market data.

Required content: equations, a worked ZL example, the inputs used and their sources, a verdict, for: (a) T_disc and
T_test for ZL (discovery 2020-12-01..2024-02-29 with E.33's burn-in and OOF construction; test 2017-05-22..2020-11-30
if MBO, or 2017-05-01..2020-11-30 if MBP-1; state the CBOT trade-date counts you use and how you got them without
opening sealed data, for example from a calendar module or E.33's recorded counts); (b) the threshold table (SR0, G3,
b_test, G4, binding, SR80_test) at N = 838 + B for B in {0, 40, 62, 100, 150, 200, 250, 300}, reproducing E.32b's N 838
row first; (c) e80 in ticks per trade at h 15, 30, 60 for the discovery gate and the test, at the entry cap and at
realistic trade rates (for example 1, 2 and 4 trades a day; E.33's G1 passers traded about one to two a date), with
the random-walk formula and its heavy-tail caveat (E.33c 3.7 v); (d) the K2 comparison against 1.8 ticks and how the
program's budget moves it; (e) Holm at the test with up to 3 finalists and its effect on the test bar; (f) the open
E.32 D2 item (V14 (c), the test DSR variance) and what it changes; (g) a "Protocol inputs" block: the threshold rows
for the budgets the lead may choose and the formulas, ready for protocol P7. Output:
reports/stage_e34_briefs/M4_power_ZL.md; scripts in reports/stage_e34_briefs/work/MathReaderM4-OpusHigh/. Tools:
Read, Bash, Write. No web.

## DataFacts-SonnetHigh

Objective: write reports/stage_e34_data_facts.md, Part F of the stage prompt: "From the owned ZL MBP-1 (E.31) and the
ZS, ZM and ZL bars, record: schemas, fields and timestamps; message counts per day; roll handling; disk and memory
needs; what E.33's pipeline can reuse. No price, return, feature value or label is computed or looked at."

Allowed data: only the 39 files in data/vendor/databento/GLBX.MDP3/mbp-1/Z3_ZL_v_0/ (plus its manifest.json), the
definition files in data/vendor/databento/GLBX.MDP3/definition/Z4_ZM_FUT-ZS_FUT-ZL_FUT/, and the ohlcv-1m files
range=2020-12-01_2021-01-01 .. range=2024-02-01_2024-03-01 in data/vendor/databento/GLBX.MDP3/ohlcv-1m/{ZL_v_0,ZS_v_0,
ZM_v_0}/ (39 each). Everything else is refused, above all rule 1's paths.

Steps:
1. First write reports/stage_e34_briefs/work/DataFacts-SonnetHigh/guard34.py: an explicit allowlist built from the
   names above (resolve symlinks; compare real paths), a check(path) that refuses anything else (raise) and logs every
   allowed open with the PDT time to opens.log in the same folder, and a dry_check() that must refuse a sealed blob
   path under data/sealed/, an in-window raw path (for example the ZL ohlcv-1m range=2020-11-01_2020-12-01 name), a
   2024-03 or later file, a rolls file and the FRED csv. Run the dry check and put its output in your report. Open every
   data file only through guard34.check.
2. Reuse before decoding: E.33 already split ZL MBP-1 by date (reports/E.33_RETURN.md line 136: 158,044,028 records,
   816/816 dates) and logged it (reports/stage_e33_briefs/work/logs/split33_ZL.log; split33.py, data33.py, cal33.py
   in reports/stage_e33_briefs/work/pipeline/). Take per-date counts from those logs where they exist.
3. Decode raw files only for what is not recorded, and then read only the fields ts_recv, ts_event, action, side,
   flags, instrument_id (never price or size fields; never print a record). Counts to record: records per trade date
   for ZL MBP-1, split by action (trades T, adds A, cancels C, modifies M, others) and by segment (day session
   08:30-13:20 CT, the rest), with daily median, 5th and 95th percentiles over the discovery dates and per calendar
   year; bars per trade date per root (median, min, max). Trade dates: use E.33's calendar (cal33.py) or the CME
   trade-date rule E.33 used; state it.
4. Schemas and fields: the DBN metadata (schema, dataset, stype, start, end, symbols) and the record fields with their
   types; which timestamps exist and their meaning; the definition files' fields relevant to rolls and ticks
   (min_price_increment, expiration, raw_symbol).
5. Roll handling: instrument_id changes across dates inside the ZL.v.0 MBP-1 files and the ohlcv-1m v.0 files (count
   them and list the change dates within the discovery window only), and how E.33's code handled rolls (file:line).
6. Disk and memory: bytes on disk per file and in total, decompressed bytes and peak resident memory to decode one
   month (measure one month with /usr/bin/time -v at nice 10, one job at a time), an estimate for ZL MBO in both
   windows from the measured MBP-1 size and E.31's ZM MBO sizes (state the ratio you assume), and the free disk on
   /mnt/large-storage.
7. Reuse: for each E.33 pipeline module, what it does, whether it runs unchanged on ZL as the traded leg, what must
   change (labels on ZL, cost33's tick and fee, the guard's allowlist, the bar inputs), with file:line.
Compute rules: check `free -m` before decoding; nice -n 10; one heavy process at a time; resumable (write per-file
results as you go). Output: reports/stage_e34_data_facts.md (facts with counts, sources and file:line; no price,
return or feature value); scripts, logs and opens.log in your folder. Tools: Read, Bash, Write. No web.

## MathReviewer-FableXHigh

(Session 2, spawned about 14:05 PDT; worker-xhigh, model fable.) Objective: an independent check of Part M before the
protocol freezes. Are the equations right, do the worked ZL examples and every number that will enter the protocol
recompute, is the list of leakage traps complete, and does each verdict follow from its evidence?

Inputs (read by section, grep -n first): reports/stage_e34_briefs/M1_F10_ZL.md, M2_F09_ZL.md, M3_labels_ZL.md,
M4_power_ZL.md and L_lead_reconciliations.md (the lead's rulings L.a-L.e); the workers' scripts and outputs:
work/MathReaderM1-OpusHigh/scripts/m1_examples.py (+ m1_examples.out), work/MathReaderM2-OpusHigh/scripts/m2_examples.py
(+ m2_examples.json), work/MathReaderM3-OpusHigh/M3_calc.py (+ M3_calc.out), work/MathReaderM4-OpusHigh/m4_power.py
(+ m4_out.md); the frozen E.32 functions m4_power.py imports; reports/stage_e34_data_facts.md (counts only) and
reports/stage_e34_exposure.md sections 2-4; the E.32 methods brief and protocol only at the lines the M files cite.

Checks:
1. Recompute. First grep each script for file reads (it must open no market data), then rerun it
   (`nice -n 10 uv run python <script>`, seconds each) and compare every number the M files and L quote: M4's
   thresholds at N 838 and N 1038 (B 200), its e80 tables and its D2 simulation (synthetic draws, same seed); M3's
   caps 17 / 8 / 4, its dead zone and execution-variant figures; M2's break-even shares (0.52, 0.35, 0.26) and cost
   per sigma (0.085, 0.092); M1's per-bucket SDs; L's arithmetic (the L.a table, the L.b caps and e80, the L.e span).
2. Equations. For each feature, label and test formula: units (ZL tick 0.01 c/lb = USD 6; crush units), signs,
   causality (only records with ts_recv <= t), and agreement with the E.32 text it adapts (cite E.32 lines).
3. Leakage and look-ahead. Is every trap listed with a test? Name any missing one (roll days and ZL.v.0 flips, the
   07:45-08:30 pause and the uncross, settlement, ts_event, a bar that closes after t, cross-market bar stamps).
4. Verdicts. Does each follow from its evidence (M1: MBP-1 for discovery and test, 5-minute minimum; M2: CL excluded,
   ZS and ZM leaders from bars, the crush residual with ZL adjusting; M3: labels F15 F30 F60 T15 T30, dead zone,
   caps; M4: power, K2 and D2; L.a-L.e)? Flag overclaims and any statement resting on an earlier ZL outcome (RULES 3).
5. Citations. Spot-check at least 10 verbatim quotes against the saved pages in the workers' pages/ folders or the
   E.32 brief lines cited; list each check and its result.

Output: reports/stage_e34_briefs/review/MathReview.md. First a verdict (GO / GO WITH FIXES / NO-GO). Then numbered
items, each tagged BLOCKING (a wrong number or formula that would enter the protocol, or a leakage hole), SHOULD FIX
(an error or gap that weakens a verdict) or NOTE, with file:line, what is wrong, the evidence or recomputed value, and
the exact fix. Then a table of every number recomputed (quoted, recomputed, match). Scratch:
work/MathReviewer-FableXHigh/.

Boundaries: RULES 1-10. No web fetch except to re-verify a quote whose saved page is missing (log it under rule 9).
Do not edit any M file, L, or another worker's file. The protocol is not written yet and is not yours to review.

## ComputeRef-OpusHigh

(Session 2, spawned about 14:05 PDT; worker-high, model opus.) Objective: set the ZL protocol's P10 compute-stop
reference R_ZL (and the stop at 3 x R_ZL) as a stated guess range, from E.33's measured fold times scaled to the ZL
search. No real-data probe is allowed in E.34 (it would compute features) and a synthetic-only probe is not allowed
(E.33b D3), so the reference is "the protocol's own guess range" (prompt Part P).

Inputs (by section): reports/E.33c_RETURN.md lines 93-110 (3.2-3.3); reports/stage_e33c_briefs/ref_v03.json (fold
wall times and projections; times only) and reports/stage_e33c_briefs/tools/project_ref_v03.py (method);
reports/stage_e33c_briefs/protocol_v0.3.diff (the P5/P10 compute clause); reports/stage_e32_discovery_protocol.md P5
(lines 535-615) and P10 (830-865), by grep for the compute and parallelism rules; reports/stage_e34_data_facts.md
sections 3, 6 and 7 (ZL sizes, memory, what E.33's pipeline reuses); E.33's set sizes and feature counts (E.32
protocol P4, lines 367-534, by grep). The ZL grid (the lead's plan, to be frozen in P5): 4 sets, S_crush (the F09
crush features), S_prop (the F09 propagation features), S_book (F10.1-F10.12), S_pool (all three), each with the
context block C, x 5 labels (F15, F30, F60, T15, T30) x 10 model settings (6 LOGIT, 4 LGBM) = 200 configurations, 6
blocked folds each (1,200 fold fits), the same decision grid as E.33 (08:35..13:12 - h CT), 816 discovery dates. Take
the per-set feature counts from M1 section 7 and M2 section (f) (grep), and E.33's C count; parametrise the result by
feature count so the lead can rescale.

Output: reports/stage_e34_briefs/P10_compute_ref.md: (1) E.33's measured components (build B, fold times by family
and set, the /8 and /2 parallel divisors), each with file:key; (2) the scaling model for ZL (what scales with
records, rows, features and configurations), each assumption labelled; (3) R_ZL low / central / high and 3 x R_ZL in
seconds and hours; (4) peak memory per fold and for the build against 14 GB, and the parallelism CLAUDE.md's compute
limits allow; (5) what the run stage measures first to report against the guess. Scripts in
work/ComputeRef-OpusHigh/ (nice 10, arithmetic only).

Boundaries: RULES 1-10. Open no market data. Do not open E.33's search_real.log or any E.33 statistics or selection
output (stats.json, P8_select33.json, D_stats.*): ref_v03.json carries the times you need. No web.

## ProtocolReviewer-FableXHigh

(Session 2, spawned about 14:15 PDT; worker-xhigh, model fable.) Objective: an independent, adversarial review of the
draft protocol reports/stage_e34_zl_protocol.md (DRAFT v0.1, P0-P11) before the lead freezes it. The prompt's
checklist: leakage, exposure handling, hidden degrees of freedom, the budget and threshold arithmetic, and
feasibility.

Inputs (by section, grep -n first): the protocol; the frozen E.32 protocol reports/stage_e32_discovery_protocol.md
(every "as E.32 Pn.m (lines a-b)" reference: read the cited lines and check that, after the protocol's 0.4
substitutions, the E.32 text is well defined and correct for ZL on MBP-1 with bar leaders); Part M sources
(stage_e34_briefs/M1_F10_ZL.md section 7, M2_F09_ZL.md section (f), M3_labels_ZL.md section (g), M4_power_ZL.md
sections (d)-(g), L_lead_reconciliations.md); reports/stage_e34_exposure.md sections 3-6; reports/stage_e34_data_facts.md;
stage_e34_briefs/P10_compute_ref.md with work/ComputeRef-OpusHigh/ref_zl.py and ref_zl.json; reports/stage_e32b_recommendations.md
section 4.5 (lines 532-657) and section 6 (1012-1026); docs/DECISIONS.md V43 (788-806); E.33's pipeline code under
reports/stage_e33_briefs/work/pipeline/ (guard33.py, data33.py, cal33.py, lab33.py, cost33.py) only where the protocol
relies on it.

Checks:
1. Leakage and look-ahead: rule B bar timing, ts_recv clocks, the P1.2 drops, label spans, roll and flip dates,
   fold hygiene and the embargo, the trailing references, the L1.3 fit window, anything that lets a feature see
   records after t or the test window.
2. Exposure handling: the firewall rules and E1-E6 as adopted in P1.5; anything in the protocol that could have been
   steered by an earlier ZL or E.33 outcome; whether the own-price statement in P1.5 is honest and sufficient.
3. Hidden degrees of freedom: any choice left open that could affect an outcome (a reading the run stage would have
   to make, an unspecified parameter, a fork); every grid element sourced; the option A ruling (P2) and its V43
   basis.
4. Arithmetic: recompute P7.2 at N 1038 with the frozen functions M4 names (T_disc 796, T_test 870); the L.b caps and
   e80; the P9.4 multipliers and table; the P10.3 compute reference (rerun ref_zl.py, nice 10; it opens no market
   data, confirm by grep); the feature counts (C 14, sets 22/23/26/43) and the budget 200.
5. Feasibility: can the run stage implement every rule as written with the owned data and E.33's code (MBP-1 bad-book
   reading, definitions for C.7 and limits, the test calendar, the purchase steps); is anything impossible or
   ambiguous.
6. Consistency: the spliced feature tables in P4 must match M1 section 7 and M2 (f) exactly; cross-references (P,
   L, M, X, DF34 section numbers) must point to the right place.

Output: reports/stage_e34_briefs/review/ProtocolReview.md: a verdict (GO / GO WITH FIXES / NO-GO), then numbered
items tagged BLOCKING (a leak, an outcome-steered choice, a wrong threshold, or an unimplementable rule), SHOULD FIX
or NOTE, each with protocol line, the problem, the evidence, and the exact replacement text. Then a table of every
number recomputed (quoted, recomputed, match). Scratch: work/ProtocolReviewer-FableXHigh/.

Boundaries: RULES 1-10. Do not edit the protocol or any other file but your own output and scratch. The MathReviewer
reviews Part M separately (review/MathReview.md, if present, may be read but not relied on). No web.

## Correction to RULES (session 3, 15:26 PDT; ProtocolReview B1)
RULES lines 65-66, "test bars for ZL, ZS, ZM are owned inside the sealed files", is wrong for ZM: ZM raw ohlcv-1m
chunks are owned only for 2019-05..2020-11 (reports/stage_e32_test_seal.md section 2, "no earlier ZM file is owned");
ZL and ZS have 44 chunks each, 2017-04..2020-11.

## FixVerifier-FableXHigh (worker-xhigh, model fable; session 3)
Objective: check that DRAFT v0.2 of reports/stage_e34_zl_protocol.md fixes every BLOCKING and SHOULD FIX item of
review/MathReview.md and review/ProtocolReview.md correctly, and that the edits add no new error (a leak or
look-ahead, a contradiction between sections, a hidden degree of freedom, a wrong number, a broken reference).
Inputs (read by section, never whole): review/protocol_v0.1_to_v0.2.diff (all of it: this is the object under
review); review/FixLog.md; the two reviews' items; the v0.2 protocol around each change; review/protocol_v0.1.md;
L_lead_reconciliations.md section L.f; the sources each fix cites (reports/stage_e32_discovery_protocol.md at the cited
lines; reports/stage_e33_briefs/work/pipeline/feat33.py lines 558-610; reports/stage_e32_test_seal.md section 2;
M1/M2/M3 at the cited lines; ledger/databento_spend.jsonl through a script that prints aggregates only, never rows).
Checks: (1) each BLOCKING and SHOULD FIX item: FIXED, PARTLY, NOT FIXED or WRONG, with the evidence; (2) every new
problem the edits cause, as BLOCKING / SHOULD FIX / NOTE with replacement text; (3) recompute every new number: z
5.72; the K2 trigger 810; 2.25 ticks, 41% and 19%; 43 columns, 258 SFI fits, 180/120 folds; 0.898/0.905 at N 1038
(the ProtocolReviewer's work/ProtocolReviewer-FableXHigh/recompute_p7.out, or your own rerun with the frozen
functions); the ledger figures (73 settled ZM.v.0 ohlcv-1m months, median 0.0608, max 0.0738; 39 definition months,
median 0.0385; 1.46, 1.77, 1.66, about 26.5); (4) consistency: one bad-book reading everywhere; run order equals cut
order; FH versus TB caps; the ZM bars in P9.1, P9.2 and P11; OC-5 in the header, P2 and P11; (5) the new F10.7 and
F10.9 definitions: point in time, and correct on small hand examples including the MathReviewer's two
counterexamples; (6) no v0.2 sentence takes an outcome file of P1.2's list as its source.
Boundaries: no market-data file (no .dbn, .zst, .npy or .parquet opened); no file of P1.2's outcome list and no
E.33, E.33b or E.33c result file; no web; no .env, no key, no Databento; no git change; do not edit the protocol or
any other stage file. Write only review/FixVerify.md and files under work/FixVerifier-FableXHigh/. Scripts at nice 10.
Times from `TZ=America/Vancouver date`.
Output: review/FixVerify.md: verdict (PASS, PASS WITH FIXES or FAIL), counts, the per-item table, new findings with
replacement text, a recomputation table (quoted | recomputed | match), and "Not finished or not verified". Return the
path, a summary of at most 200 words, and anything you could not finish.
