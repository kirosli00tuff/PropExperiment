# R_spec: adversarial review of the Part B pilot spec, code and spend plan (SpecReviewer-FableXHigh)

Reviewer: Fable 5.1 (claude-fable-5-1), xhigh. Started 2026-10-21 16:10 PDT (23:10 UTC); finished 16:32 PDT
(23:32 UTC), times from `TZ=America/Vancouver date`. Status: COMPLETE.
Inputs read: reports/stage_e28_pilot_spec.md (sha256 e1abc05ebf75b1789ba06c1d2e9be0ec7438d8b636e34e90782def85c890fd99,
identical to reports/stage_e28_briefs/B_spec_draft.md), docs/prompts/STAGE_E.28.md lines 155-260 (Part B, SCOPE,
GUARDRAILS), reports/stage_e28_briefs/work/B_pilot/ (pilot_common.py, pilot_pull.py, pilot_stream.py, measure_core.py,
measure_stats.py, measure.py, verify.py, README.md, tests/), data/spend_gate.py (decide, SpendGate), data/config.py
(acct-3 block), data/pull_universe.py (window constants, download), data/trade_date_guard.py (holdout dates).
Work folder: reports/stage_e28_briefs/work/REV_spec/ (scripts, test file, pytest logs). Pages:
reports/stage_e28_briefs/pages/REV_spec/ with log.tsv (6 pages, all by curl or Wayback+curl; no Scrapling, no Firecrawl).
WebSearch used: 4 of 25. No Databento, broker or paid call; no key read; nothing under B_pilot/ edited.

Severity scale (from the brief): BLOCKING = a wrong number or rule that changes the top pair, the top-five order, the
purchase or the measurement's validity. SHOULD FIX = misleading or wrong but not decision-changing. NOTE = the rest.

## 0. Findings table

| ID | Severity | Where | Finding (one line; details in the section named) | Fix |
|---|---|---|---|---|
| RS-01 | BLOCKING | pilot_common.py:71-74, 249-251, 290, 311; verify.py:142; pilot_pull.py defaults; README | The code's request end is `2024-03-01` (00:00 UTC = 18:00 CT on 2024-02-29). The spec (section 0) and the brief fix the end at `2024-02-29T22:00:00Z` (16:00 CT, the end of trade date 2024-02-29). The code therefore buys 17:00-18:00 CT of 2024-02-29, the first hour of CME trade date 2024-03-01 (the embargo's first trade date; data/trade_date_guard.py:31 itself notes that the February 2024 chunk's last evening books to 2024-03-01), and `pilot_pull.py --end 2024-03-01` is accepted where the brief expects a refusal at or after 22:00Z. The measurement is unaffected (CUTOFF_TRADE_DATE excludes trade date 2024-03-01), the purchase and its verification are. Section 4.3 | Set CUTOFF_BOUND = "2024-02-29T22:00:00Z" (CUTOFF_UTC to match); verify: no record with ts_event >= 2024-02-29T23:00:00Z (the 17:00 CT open of trade date 2024-03-01), count records in [22:00Z, 23:00Z) as info; update docstrings, README and the tests that spell the old bound (test_b_pull.py:125-126, 146-147, 165, 186-188, 231; test_b_files.py:61-66; test_b_sessions.py:98) |
| RS-02 | none (positive) | spec section 0 "Matching algorithm" | QG outright futures match FIFO (tag 1142 = F) on the CME Globex Product Reference Sheet in two Wayback snapshots that bracket the pilot window (2023-06-22 and 2024-02-26). Section 1 | Fill the parameter row: "FIFO (F), CME Globex Product Reference Sheet, 2024-02-26 and 2023-06-22 snapshots, SpecReviewer" |
| RS-03 | SHOULD FIX | spec sections 1-3 | QG is implied-eligible (same sheet, "Yes, Note 4"); Databento's mbp-1 is the direct (outright) book: implied liquidity is merged only in CMBP-1, and implied-involved trades carry side N. The spec never says so. Under CME's FIFO-for-implied rule (outright orders at a price trade before implied orders at that price) Q_ahead = outright displayed size is right, and excluding side-N trades from V(t) is conservative; but placement prices and mids come from an outright-only BBO that can be wider than the merged one. Section 1.2 | Add one paragraph to section 1 stating this; add per-day trade counts by side (A/B/N) and the share of fills triggered by a side-N trade to the data checks (measure_core.day_summary_counts / pilot_stream counts) |
| RS-04 | SHOULD FIX | spec section 3 fill rule; measure_core.through_index, spec_fill_index | The trade-through clause accepts any trade, side N included. Side-N prints are implied-involved or opening trades; a side-N print strictly through the price fills the order although the outright queue at its price may not have traded (anti-conservative; magnitude unknown, probably small since price priority makes it rare). Section 3.1 | Require a defined aggressor (A or B) for the through clause, or report fills split by trigger (queue / through with A-B / through with N). One line in the spec and one mask in the code |
| RS-05 | SHOULD FIX | spec section 3 markouts; measure_core.markouts | A markout is dropped when ANY book state over [t_f, t_f + h] is crossed, locked or has an empty side. A sweep that empties the top of one side is exactly an adverse-selection event, so the drop removes adverse markouts first and flatters the mean. The drop count is reported per cell, so nothing is hidden. The "session_end" drop can never fire under the 5-minute edge rule (my test). Section 3.2 | Report, beside the headline, a no-drop variant (mid from the last VALID state at or before t_f + h, which is what the spec's own mid sentence says) and the dropped share per cell |
| RS-06 | SHOULD FIX | spec section 3 latency; README convention 4; pilot_stream._resolve_joins | The limit price is read from the book at j = g + 50 ms, not at the decision time g. This removes every placement whose price would have been stale on arrival (marketable: an immediate aggressive fill with adverse markout; or behind the touch: fewer fills), both of which flatter. Section 3.3 | Count placements whose best bid or ask at g differs from that at j and report the share per cell; if it is above about 2% anywhere, also report the price-from-g variant (marketable at j = skipped and counted) |
| RS-07 | SHOULD FIX | spec section 6 | With 152 placements a day (76 MAIN grid times; the repo calendar for QG gives exactly 76) the fill-rate target needs ceil(3,201 / 152) = 22 MAIN days, not 21, and 22 x 1.15 = 25.3, so 26 trade dates, not 25. The repo calendar gives 85 trade dates in 2023-11-01..2024-02-29, 4 excluded as holiday or early close (2023-11-23, 2023-11-24, 2024-01-15, 2024-02-19), and two v.0 rolls (late January and late February) will take about 4 more, so "the last 25 trade dates" yields about 21 usable MAIN days, below the target with no margin. n_10 is 151.65, i.e. 152 fills (spec: 151). Section 3.5 | Minimum span = 26 USABLE trade dates after holiday and roll exclusions, i.e. a first trade date no later than 2024-01-18 (the last 30 trade dates); write the check into the buy step: if the span search's first_trade_date is later than 2024-01-18, buy nothing |
| RS-08 | SHOULD FIX | spec B3 / README steps 2-4 | "A few dollars of margin" is not encoded anywhere: the span search takes TARGET from the lead and the buy takes APPROVED; the account cap (125.00) cannot see the balance; a billed amount may exceed the quote by up to 3% before the run stops. Section 5 | State in the spec and README: TARGET = balance - max(3.00, 0.03 x TARGET) rounded down to the cent; APPROVED = the quote; buy nothing if the quote exceeds balance - 3.00 |
| RS-09 | NOTE | README steps 5-6; stage prompt B4 | The README never names the "ACCOUNT_3 SAFE TO WIPE" line or its precondition. Section 5 | Add to step 5: write the line only after verify.py exits 0 or 3 (3 = data-quality only, the data is what was bought) and the manifest sha256 matches the purchase record; never after 1 or 2 |
| RS-10 | NOTE | spec section 2; measure.py Plan | The spec names the window 2023-11-01..2024-02-29 but the purchase extends earlier as funds allow and measure.py measures every trade date in the file. Say explicitly that every purchased trade date (after the exclusions) enters the statistics, or that only the window does | Spec wording |
| RS-11 | NOTE | spec section 3 latency | 50 ms each way is an assumption; a retail path Vancouver -> TopstepX/Rithmic -> Aurora is likelier 60-120 ms. The spec rightly forbids varying it; the number should be labelled an assumption in section 0 | Spec wording |
| RS-12 | NOTE | spec section 2 "sorted by the exchange sequence and ts_recv" | The code sorts by ts_recv then sequence and uses ts_event (made non-decreasing) as the time axis, counting every inversion. That is the right axis for a simulation with added latency; the spec sentence should name ts_event as the time axis | Spec wording |
| RS-13 | NOTE | measure_core.day_orders life window | The life (j, j + 60.05 s) is never clipped at a session piece end; only the 5-minute edge exclusion keeps it inside (my test shows a fill after the piece end when the grid is forced). Harmless under the spec grid; a comment or an assertion would make it robust | Code comment or assert |
| RS-14 | NOTE | B1 | mbp-1 is sufficient and the cheapest sufficient schema (section 2 of this file): every trade is a T record with aggressor side A/B/N; top-of-book prices and sizes at every change; exchange timestamps. tbbo lacks the book between trades; mbp-10 adds unused depth at more bytes; mbo is needed only for order-level queue position | none |
| RS-15 | NOTE | pilot_pull.py refusals | Every refusal the brief lists is present and tested before any vendor call: account (acct-3 only, by name), dataset, schema, symbol = ROOT.v.0, stype continuous, end bound (at the wrong bound: RS-01), start before dataset first date, embargo/holdout-2, research window, holdout-1, sealed windows, trade-date guard, session id prefix, session cap in (0, 125], target_usd <= 125, approved_usd > 0, stale/foreign/failed/committed quote | none beyond RS-01 |

Counts: 1 BLOCKING (RS-01), 6 SHOULD FIX (RS-03 to RS-08), 7 NOTE (RS-09 to RS-15), 1 positive result (RS-02, the
matching algorithm: FIFO confirmed, no defect).

## 1. Matching algorithm for QG outright futures (BLOCKING check, task 1)

Result: FIFO (tag 1142-MatchAlgorithm = F). Confirmed from the exchange's own product list in two snapshots that
bracket the pilot window. The spec's condition "if QG is not FIFO ... Part B buys nothing" is therefore not triggered.

Source A (exchange): CME Globex Product Reference Sheet, Wayback snapshot of 2024-02-26 (file author/last-saved
metadata "Connell, Stephen", saved 2024-02-26 16:28), saved as
pages/REV_spec/globex_product_reference_sheet_20240226.xls (sha256 in log.tsv). Sheet "All Futures and Options", header
row (0-based row 2): `4:Globex Symbol | 5:Group Code (tag 1151) | 6:Strategy Type* | 7:Implied Eligible* | 8:Minimum
Futures Tick and Options Minimum or Inner Tick | 9:Value of a Minimum Futures Tick ... | 10:Algorithm*`. Row 1034
(0-based; Excel row 1035), verbatim cell values:
`Energy | Futures | NYMEX | E-mini Natural Gas Futures | QG | NG | Outright | Yes, Note 4 | 0.005 | 12.5 | F`
(then FIFO Percent Allocation 1.0, velocity logic 0.15/0.05, price banding 0.05, stop price value 0.1, protection point
0.025, maximum quantity 999, minimum quantity 1, market segment id 78, MDP 3.0 channel 386). Row 1035 is the QG-QG
calendar spread (`SP`), also `F`. Sheet "LEGEND", row 56: `F: First In, First Out (FIFO)`; row 34: `Note 4: All Contracts
months 1 to 24 and June and December months 25 to 36` (the implied-eligible months).

Source B (exchange, before the window): the same sheet's Wayback snapshot of 2023-06-22,
pages/REV_spec/globex_product_reference_sheet_20230622.xls, row 1061: identical values
(`... | QG | NG | Outright | Yes, Note 4 | 0.005 | 12.5 | F | ...`).

Source C (exchange, the algorithm's definition): CME Group Client Systems Wiki, "Supported Matching Algorithms"
(updated Feb 11, 2025), pages/REV_spec/cme_wiki_supported_matching_algorithms.html. Table "Algorithm / tag
1142-MatchAlgorithtm Value": `FIFO | F`. Text: "The FIFO algorithm uses price and time as the only criteria for filling
an order. In this algorithm, all orders at the same price level are filled according to time priority; the first order
at a price level is the first order matched." And under "FIFO for Implied Orders": "When trades are matched using the
FIFO method, outright orders at the same price level are filled according to time priority. After all possible matches
have been made for the outright orders; the implied orders will trade using the rules based system mentioned under the
Priority Rules section".

Parsing: pages were read by script (work/REV_spec/REV_spec_parse_xls.py and REV_spec_xls_headers.py, run with an
ephemeral `uv run --with xlrd`, nothing added to the project), output in work/REV_spec/REV_spec_xls_parse.txt. Both
.xls files have the same column layout. The tick (0.005) and tick value (12.5) in the sheet match the spec's section 0.

Not consulted: the NYMEX rulebook chapter (contract terms, not the matching algorithm) and CFTC filings (not needed
once the exchange's own product list gave the value twice). cmegroup.com itself was not fetched (blocked IP; Wayback
copies used, as the brief allows).

### 1.2 Implied prices in Databento's GLBX mbp-1 for QG, and what it means for the queue-ahead rule

Facts, with quotes from pages/REV_spec/databento_glbx_mdp3.html (Databento, "CME Globex MDP 3.0" venue page):
- "CME's MDP3 feed has support for implied orders over their MBP feed. The MBP feed provides up to 10 levels of real
  liquidity and 2 levels of implied liquidity. Databento combines the real and implied books, publishing the merged
  top-of-book on the CMBP-1 schema."
- "Across all of Databento's feeds, it is important to use the F_LAST flag when calculating the best bid and offer, like
  our MBP-1 schema. ... This is accounted for when we construct our other schemas, such as MBP-1 and Trades."
- "Implied trades may not have an aggressing side set. These trades will be normalized with side set to None."
- (schema page, fetched by WebFetch, not saved) side: "The side that initiates the event. Can be Ask for a sell order
  (or sell aggressor in a trade), Bid for a buy order (or buy aggressor in a trade), or None where no side is specified."
Inference [from the first two quotes; Databento does not state it in one sentence]: mbp-1 is built from the MBO (direct
order) feed and holds the outright book only; implied quantities appear only in CMBP-1/CBBO.

CME on side-N trades (pages/REV_spec/cme_wiki_mdp3_trade_summary.html, tag 5797 AggressorSide): "0=No aggressor ...
Trades without aggressors occur at Market Open, after a Pre-Open or after a Pause, and also when the event includes
customer order participation in a trade with a CME Globex-generated implied bid or offer." And
(pages/REV_spec/cme_wiki_mdp3_trade_summary_order_detail.html): "If the aggressor quantity (tag 32) is not equal to the
sum of the remaining Order Detail entries quantity associated with that Summary Level, customer and implied orders were
filled in the trade. The unreported quantity are the participating implied orders." ... "Additionally, trades that only
involve implied orders are not published in a Trade Summary message, but volume and price statistics are updated
real-time."

Consequences for the spec's rule (QG is implied-eligible, so this applies):
1. Q_ahead = the outright displayed size at j is the right queue under FIFO-for-implied: outright orders at a price
   trade before implied orders at that price, so implied quantity never stands ahead of a resting outright order. No
   change needed.
2. A trade at our price with a defined aggressor (side A for a buy) counts its whole size toward V(t), including any
   implied participation at that level. That is correct: our order would have traded before the implied quantity.
3. Side-N trades at our price (QG outright resting orders executed as legs of an implied spread match) deplete the
   outright queue ahead of us but are excluded from V(t): conservative. Side-N trades strictly through our price fill
   under the "any aggressor" clause: see RS-04.
4. The placement price (best bid or ask) and the mid come from the outright-only BBO. Where an implied order is inside
   the outright spread, the merged BBO is tighter; a real trader at "the touch" would quote the merged touch. The effect
   is fewer trades at the outright touch (fewer fills, conservative) and an outright mid that differs from the merged
   mid (symmetric between buys and sells when pooled). Acceptable for a pilot; the spec should say it (RS-03), and the
   side counts of RS-03 measure how much implied activity QG actually has.

## 2. B1: is mbp-1 sufficient, and the cheapest that is (task 2)

Sufficient: yes. Every measurement in section 3 of the spec needs (a) the best bid and ask with displayed sizes at
every change (the queue at j, the spread for I placements, the mid at horizons), and (b) every trade with price, size
and aggressor side. Databento's mbp-1 schema page (WebFetch): "This includes every trade and changes to book depth,
alongside total size and order count at the BBO"; the side field carries the aggressor for trades (quote in 1.2). The
venue page confirms that each CME Trade Summary becomes one Trade record in "The MBP-n and trades schemas" (Fill detail
records exist only in MBO and are not needed). Exchange timestamps: ts_event is "The matching-engine-received timestamp"
and ts_recv the capture time (schema page). The order-level identities that mbo adds are not used by a rule that treats
the whole displayed queue as ahead and ignores cancellations.

Cheapest sufficient: yes, by elimination. tbbo gives the book only at trade instants, so the queue at a clock-grid join
and the mid at fixed horizons are unobserved (the spec's own reason, correct). mbp-10 carries the same top-of-book and
trade information plus nine unused levels, with records emitted for depth changes that mbp-1 does not emit, so it is
strictly more bytes for the same measurement. mbo is the most bytes and buys only queue-position detail the rule does not
use. Databento prices historical data by billable bytes, so mbp-1 is the least costly schema that supports the spec. No
quote was made in this review (quoting is the lead's step).

One caveat the spec should state (RS-03): the mbp-1 book is the outright book; implied liquidity is not in it.

## 3. B2: could the measurement flatter the result; statistics; span arithmetic (task 3)

### 3.1 Fill rule
- Queue clause: conservative under FIFO (confirmed in section 1). Nothing can get ahead of a resting outright order at
  its price; order modifications that increase size or change price lose priority (CME wiki, quoted in 1.2's source C
  page: "an order loses order priority and is re-queued when changed in any of the following ways: Increase the
  quantity, Change the price, Change the account number"). Cancellations ahead are ignored (conservative). Iceberg
  (display-quantity) remainders re-enter behind us. Verified in code: spec_fill_index counts only trades at exactly the
  price with the opposite aggressor, fills at V >= Q_ahead + 1 (my tests: partial depletion 2+2+1 does not fill at
  Q_ahead = 5; the next 1 does; a same-side trade at the price never counts; a trade at exactly j is join state).
- Through clause: accepts side-N trades (RS-04). Under price priority a print strictly through our price almost always
  means our level was swept first, so the exposure is small, but the fix is one mask and keeps the rule conservative.
- Touch without trade: never a fill (tested, including a crossed opposite quote).
- Price moving away and back: Q_ahead stays as at join and later trades at the price count (tested). Conservative under
  FIFO.
- Locked book then same-side trades at our price: not a spec fill, a fill under trade_at_or_through (tested; documents
  why the firm's sim rule must be re-scored separately, as the spec does).

### 3.2 Markouts
- Reference: mid from the last book state at or before t_f + h, a change at exactly t_f + h included (tested).
- Drop on any invalid state in [t_f, t_f + h]: see RS-05 (flattering direction; counted). The session_end drop is dead
  under the grid's 5-minute edge rule (tested: a forced grid 30 s before a piece end does produce the drop).
- Fee: net = markout - FEE_SIDE, with FEE_SIDE 0.0808 ticks (2.02 USD per round trip / 2 / 12.50) and the 0.296
  conservative reading also reported. Arithmetic checked. The fee source conflict belongs to Part A, as the spec says.

### 3.3 Latency and look-ahead
- Join at g + 50 ms, cancel effective 50 ms after j + 60 s; fills inside the latency count (tested at +30 ms, +49.999 ms
  yes; +50 ms, +51 ms no). The book state at j is the last record with ts_event <= j (tested).
- Price from the book at j, not g: RS-06.
- Latency value: RS-11.

### 3.4 Sessions, rolls, data checks
- Trade date, MAIN 06:30-13:00 PT, OVERNIGHT the rest, 5-minute edges, maintenance halt from the repo calendar: the
  code matches the spec (76 MAIN grid times and 270 in all on a regular day; the Presidents Day early close 2024-02-19
  is excluded by the calendar).
- Roll days: a trade date with two v.0 instruments (the Databento mapping changes at 00:00 UTC, mid trade date) or a
  first instrument different from the previous trade date's last, and the day after, are excluded. Matches the spec.
- Bad-flag records dropped and counted; crossed/locked/empty counted and timed; MAIN gap > 60 s excludes the date.
  Matches the spec. Side counts per trade (A/B/N) are not reported: RS-03.
- Survivorship: a dropped markout leaves the fill in the fill rate but not in the markout mean (RS-05); VPO uses the
  fill rate times the mean of surviving markouts, so the same drop enters VPO.

### 3.5 Statistics and the bootstrap
- Kaplan-Meier from j with censoring at 60 s; late fills (inside the cancel latency) count in the fill rate and are
  censored in the curve, reported separately. Correct and stated.
- Day-block bootstrap: trade dates with replacement, 2,000 replicates, default_rng(28), one draw matrix shared by every
  cell and statistic, percentile 95% intervals, ratio-of-sums statistics (fill rate, means, shares, VPO). Correct. The
  KM point at 1, 10 s equals the empirical share filled by then (no censoring before 60 s), so pairing it with the
  ratio-of-sums interval is consistent.
- Labels (positive / negative / not distinguishable) from the interval: as the spec says.
- Span arithmetic: fill-rate n = 3 x (1.96 x 0.5 / 0.03)^2 = 3,201 placements (correct); n_10 = 1.5 x (1.96 x 0.513 /
  0.10)^2 = 151.65 -> 152 fills (spec says 151); n_60 = 1.5 x (1.96 x 1.256 / 0.20)^2 = 227.3 -> 228 (spec 227).
  Days: 3,201 / 152 = 21.06 -> 22 (spec 21, from 156); 152 x 0.3 = 45.6 fills a day -> 4 and 5 days (correct); at
  p_fill = 0.05, 7.6 fills a day -> 30 days (correct). Minimum = max(22, 4, 5) = 22, x 1.15 = 25.3 -> 26 trade dates
  (spec 25). Calendar check (work/REV_spec/REV_spec_calendar_count.py, the repo's energy group calendar, no market data
  read): 85 trade dates in 2023-11-01..2024-02-29, 4 excluded statically, 81 usable before roll exclusions; the last 25
  usable start 2024-01-25, the last 26 start 2024-01-24, the last 30 start 2024-01-18. Two v.0 rolls fall in the last
  25 trade dates (late January and late February), costing about 4 dates. See RS-07.
- sigma_1m: 6.28 NG ticks x 0.001 / 0.005 = 1.256 QG ticks (correct; assumes QG's price volatility equals NG's, a fair
  assumption for the same underlying and stated as derived).

## 4. Code against the spec; tests; adversarial cases; refusals (task 4)

### 4.1 Tests
- The coder's suite: `uv run pytest -q reports/stage_e28_briefs/work/B_pilot/tests -p no:cacheprovider`: 137 passed in
  3.00 s (work/REV_spec/REV_spec_pytest_bpilot.txt). The repo suite was not run (the brief: this folder only).
- My adversarial suite: work/REV_spec/test_rev_spec_adversarial.py, 20 tests, all passed
  (work/REV_spec/REV_spec_pytest_adversarial.txt): a trade at exactly the join instant (join state, not a fill; one ns
  later fills); partial queue depletion by several trades with a same-side trade mixed in; a trade-through after partial
  depletion; a side-N trade at the price (never adds to V) and strictly through (fills: documents RS-04); Q_ahead fixed
  at join while the price leaves and returns; a crossed book during the life (no fill, the opposite side's touch, all
  markouts dropped as invalid_book); a locked book then same-side trades at the price (spec: no fill;
  trade_at_or_through: fill); fills inside the cancel latency at +30 ms and +49.999 ms, none at +50 ms and +51 ms; a
  life forced across a piece end (fills, markouts dropped as session_end: documents RS-13) and the proof that the spec
  grid never allows it; inside orders at a two-tick spread (shared price, Q_ahead 0, fill by aggressor side, a trade at
  the old best bid is a through fill); no inside placement at a one-tick spread (skips counted); markout reference at
  exactly t_f + h; price read at j not g (documents RS-06); a bad-flag trade cannot fill; an undefined opposite quote
  at join takes no placement on either side; int64 cumulative volume at 2^40.
- Tests I did not write: none of the stream tests use a real DBN file (none exists; nothing was bought), so the
  databento decode path (open_store, to_ndarray chunks) is covered only by the coder's synthetic-DBN tests
  (test_b_files.py, test_b_stream.py), which pass.

### 4.2 Code by section against the spec
- pilot_stream: sorts by (ts_recv, sequence), ts_event as the axis with a running maximum, counts every inversion,
  drops F_BAD_TS_RECV and F_MAYBE_BAD_BOOK records (counted, still in the gap check), keeps every trade and every
  top-price or validity change, resolves join states from the full segment before reduction (so sizes at j are exact),
  handles a j between segments from the previous segment's last record. Matches spec section 2.
- measure_core: matches spec section 3 as tested above. RULES computes spec, trade_through_only, trade_at_or_through and
  touch for every date; phase 2 reports spec and the chosen SIMRULE (trade_through_only for Topstep, as section 0).
- measure_stats: matches spec section 4 (3.5 above).
- measure: fingerprint (parameters, code version, file names and sizes) refuses a changed run; nice 10; at most 4
  workers cut by MemAvailable x 0.7; day files written atomically; exclusions applied at phase 2 and counted. OK.
- verify: header equals the pilot request; sha256 against the purchase record; no record at or after the cutoff
  (wrong cutoff: RS-01); instrument ids in the symbology; ts_recv order; on-tick prices; MAIN gap as a quality check.
  OK apart from RS-01.
- README conventions 1-12 agree with the code and (where the spec leaves a choice) do not contradict the spec.

### 4.3 Refusals in pilot_pull.py (every one checked in code and in test_b_pull.py)
- Account: `require_account` refuses anything but acct-3 that is also in PILOT_ONLY_ACCOUNTS; the key is loaded by
  `require_databento_key(account="acct-3")` (variable DATABENTO_API_KEY3 by name) only after every refusal, never
  printed. Tested with acct-1 and acct-2 for --plan, --quote, --buy.
- Dataset GLBX.MDP3 only; schema mbp-1 only; symbols exactly (ROOT.v.0,); stype_in continuous; canonical bounds.
  Tested (XNAS.ITCH, mbp-10, tbbo, NQ.v.0, ES.c.0, raw_symbol, non-canonical bounds).
- End bound: refused when later than CUTOFF_UTC, which is 2024-03-01T00:00:00Z in the code but 2024-02-29T22:00:00Z in
  the spec and the brief: RS-01. The tests at :125-126 encode the wrong bound.
- Start before 2010-06-06 refused; embargo/holdout-2 (2024-03-01..2025-04-01 UTC), research window
  (2025-04-01..2026-06-21), holdout-1 (after 2026-06-21), sealed windows (data.holdout) and the trade-date guard are all
  checked and each named in the refusal (tested: test_window_refusals, test_research_window_guard_names_each_window).
- Cap: `--session-cap-usd` must be in (0, 125.00]; `--target-usd` <= 125.00; the gate's `decide` checks session then
  account cap with the ledger's acct-3 total (0 lines on acct-3 today; ledger 36,402 lines); a refusal is ledgered and
  written to docs/ACCESS.md and raises before any commit. Tested (acct-3 cap, session cap, session cap above account
  cap).
- Buy preconditions: `--approved-usd` > 0; the newest quote of session stage-E.28-pilot must be on acct-3, for this
  exact request, priced, younger than 24 h, with no commit after it, and <= approved. Tested (each reason).
- Exit codes: 2 before any vendor call, 1 after one, 0 done; the `network` flag flips when the client is built.

## 5. Spend plan (task 5)

- acct-3 only: enforced in code (4.3) and in data/config.py (ACCOUNT_3_ID "acct-3", ACCOUNT_3_CAP_USD = 125.00,
  PILOT_ONLY_ACCOUNTS = {acct-3}, key variable DATABENTO_API_KEY3). Spend gate account = acct-3 with no external ledger.
- One schema, one contract: schema fixed to mbp-1 and symbol to ROOT.v.0 by refusal; the span search prices only
  [start, CUTOFF_BOUND) with the same refusals on every candidate.
- 125.00 as the hard ceiling: the account cap in config; the session cap defaults to it and cannot exceed it; the
  target cannot exceed it. The ceiling the account actually has is its balance, which the code cannot see: the margin is
  the lead's choice of TARGET and APPROVED (RS-08).
- Backward extension never past the end: the end is fixed (CUTOFF_BOUND) in every mode and --span-search refuses any
  other end; the bisection moves only the start earlier. The lower bound defaults to the calendar coverage start
  (2019-05-01); with --earliest unset a large balance would reach far before 2023-11-01, which the stage prompt allows
  ("earlier dates only") but the spec should say (RS-10).
- One fresh quote before the buy: --quote ledgers one priced line; --buy uses only that newest quote (4.3). The span
  search's quotes are free metadata calls under a separate session with a 0.00 cap.
- Detached buy with an rc line: README step 4 (setsid nohup, nice 10, `rc=$? <time>` appended to the log). Resume rules
  are stated and tested (settle-only, done, retry needs a new quote, foreign files stop the run, nothing deleted).
- Verification before "ACCOUNT_3 SAFE TO WIPE": verify.py checks the sha256 against the purchase record, the header,
  the cutoff, the symbology and the record order; the README does not name the SAFE TO WIPE line or its precondition
  (RS-09).
- The minimum-span condition of B3 ("if the balance does not cover even the minimum span ... buy nothing") is not
  encoded: RS-07 gives the date to check against the span search's first_trade_date.

## 6. Verdict

GO WITH FIXES. Required before the spec is hashed and before any quote:
1. RS-01: request end 2024-02-29T22:00:00Z in pilot_common (CUTOFF_BOUND, CUTOFF_UTC) and the verify cutoff at the
   17:00 CT open of trade date 2024-03-01 (2024-02-29T23:00:00Z, ts_event), with the tests that spell the old bound
   updated; rerun the B_pilot suite and my adversarial suite (both must stay green).
2. RS-02: fill the matching-algorithm row of section 0 with "FIFO (F)" and the two snapshot sources.
3. RS-07: minimum span = 26 usable trade dates after exclusions; first trade date no later than 2024-01-18; the
   buy-nothing check written into the buy step.
4. RS-04: restrict the through clause to trades with a defined aggressor, or report fills by trigger and side.
Recommended before the freeze (cheap, each a sentence or a counter): RS-03 (state the outright-only book and add side
counts), RS-05 (no-drop markout variant beside the headline), RS-06 (share of placements whose touch moved between g and
j), RS-08 (margin rule in numbers), RS-09 (SAFE TO WIPE precondition), RS-10 to RS-13 (wording).
Nothing found changes the top pair or the top-five order; RS-01 changes the purchase bound and RS-07 the minimum span.

## 7. Files

- Output: reports/stage_e28_briefs/R_spec.md (this file).
- Work: reports/stage_e28_briefs/work/REV_spec/REV_spec_parse_xls.py, REV_spec_xls_headers.py, REV_spec_xls_parse.txt,
  REV_spec_calendar_count.py, test_rev_spec_adversarial.py, REV_spec_pytest_bpilot.txt, REV_spec_pytest_adversarial.txt.
- Pages: reports/stage_e28_briefs/pages/REV_spec/log.tsv (URL, UTC, PDT, method, sha256, file, note) and the six saved
  pages (two .xls snapshots, Databento venue page, three CME wiki pages) with .txt extractions.
- Not finished: nothing in the brief. Not verified from full text: the Databento mbp-1 schema page was read by
  WebFetch only (quotes marked as such, not saved); the inference that mbp-1 excludes implied liquidity rests on the
  two Databento sentences quoted in 1.2 rather than on an explicit statement.
