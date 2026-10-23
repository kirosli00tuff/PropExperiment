VERDICT: GO (no BLOCKING item; 16 ADVISORY items, items 1 to 5 recommended before the buy)

# Stage E.31 Part 4, pass 1: SpecReviewer-FableXHigh review of the ZM pilot spec v1 and the purchase/verify code

Reviewer: Fable 5.1 (xhigh), 2026-10-22, started 13:02 PDT. Review only: no Databento call (the one pull31 command run
was `--plan`, which reports vendor_calls 0), no key read, no edit except this file, no commit. Engine and stats code
(mbo_book31, kalgo31, measure31*, stats31*) are out of scope and untouched.

Inputs checked: spec sha256 9143d2b6...8ef0 recomputed = STATE value = work/lead/spec_v1_frozen.md (read-only copy,
13:02:19). The spec file's own mtime is 12:45:12, i.e. it was last edited before the span search finished (13:00:53),
so k = 39 did not shape it. E.28 spec sha256 8937740338e81103... matches the spec's reference.

## A. What I checked and found sound (evidence)

1. Part 2 coverage (prompt lines 98-148 vs spec): data (ZM MBO v.0/v.1, ZS and ZL MBP-1 v.0, definitions for all three),
   window, sessions, T-order grid with E.28 cancel rule, three models with (c) as gate, markouts at 1/10/60 s, ZS/ZL
   conditioning over 1 s and 10 s, splits by session, USDA distance and imbalance, five fees, kill rule, implied check:
   all present, no contradiction with the prompt. Fees re-read from E.28 A2_firm_*.json: Topstep 5.28 (quote "Each side
   (Buy or Sell) incurs half the total"), Lucid 2.80 per side = 5.60, Bulenox "2.86 5.72", MFFU "$6.12", Tradeify 9.20:
   no difference.
2. TARGET: ledger acct-3 sum of `usd` = 0.72502180934 exactly (one commit, one settle delta 0.0, 252 span quotes at usd 0,
   2 volume quotes); 125.00 - 0.72502180934 - 2.00 = 122.27497819 -> 122.27. `--plan --months 39`: 156 requests,
   target 122.27, other_acct3_commits [], position headroom 124.274978.
3. Window arithmetic: all 156 span quotes in span31.json match ledger quote lines (0 missing); the same 93 request keys quoted in
   both runs gave identical USD (0 unstable); sum of the 39 months = 121.645551; month 40 (2020-11) adds 2.694567 ->
   124.340118 > 122.27, so k = 39 is the largest contiguous fit. Margin to TARGET 0.624. Month bounds recomputed
   independently (zoneinfo, 16:00 America/Chicago on the previous and own last day): 0 mismatches over 156 requests,
   month m end = month m+1 start (no gap, no overlap), 21:00Z in CDT months and 22:00Z in CST months, hand-checked
   2021/2022/2023 March, April, October, November; last end 2024-02-29T22:00:00Z. 16:00 CT sits in the 13:20-19:00 CT
   closure so each request holds whole trade dates. WASDE day in every month (16 OCE-verified dates 2022-11..2024-02);
   Nov 2023 reset month included (k >= 4), plus the earlier May/Nov ones.
4. Purchase code: `pytest -q -p no:cacheprovider .../test_pull31.py` = 89 passed (0.98 s); ruff clean on the 4 files;
   `git status -- data/` clean (pilot-only guard and RequestCappedGate untouched). I probed `request_refusals` with 11
   hostile requests (extra root ZN, ZM.c.0, ZM.v.2, mbp-10, raw ZMH4, end +1 s, end 2024-03-01, early start, XNAS dataset,
   March 2024 month, date-only bounds, ES): all refused; acct-1 and acct-2 refused by `require_account`. The key is read
   only inside `_client` with `account=PILOT_ACCOUNT` (not the CLI value), is never printed or logged. Order per request:
   fresh ledgered re-quote -> 1% check -> `authorize` (request cap, session cap = TARGET, acct cap 125) -> `commit`
   BEFORE download -> `.partial` -> `os.link` (never replaces) -> read-only -> record-byte check -> `settle` -> record.
   Double-buy: an open commit with no file, a stray `.partial`, a file with no commit, or an overlapping file all
   refuse (exit 2) before any client exists; a file with an open commit settles without re-download. Overspend: the
   session cap makes the worst case (every re-quote +1%, 122.86) stop at the tail; billing >3% over stops the run.
5. K section vs research: spec 3.1 values equal K_algorithm.md (a); I grepped 6 key quotes in the saved pages (S7 TOP Max
   notice, FIFO exception ">= displayed quantity", "rounded up to the whole lot just above", one TOP per side, "rounded down",
   Leveling tiebreaks): all verbatim. I re-read ZM row 34 of both saved product sheets with xlrd (isolated env): tick 0.1/$10,
   K, TOP 1.0/1.0/100.0, FIFO 0.4, PR 0.6, PR min 1.0, Leveling, identical in 2023-06-22 and 2024-02-26. ceil(0.4 Q) in
   floating point equals (2Q+4)//5 for Q up to 200,000 (no rounding trap).
6. Dataset condition over the window (free list): 1015 available, 3 degraded, all Sundays (2021-12-05, 2022-01-02, 2022-11-06).
7. End checks: holdout unlocks_logged 0, all_ok true; REGISTRATION.md 0 bytes; ledger 36658 lines before and after my work.

## B. Items

No BLOCKING item. A BLOCKING item would be one that lets the buy exceed TARGET, touch a forbidden range or account,
double-buy, or leaves the kill rule undetermined; I found none.

### ADVISORY (ordered by weight)

1. [ADVISORY, kill rule] Fee per fill is the lenient reading. spec:207-220 and spec:20 gate K1 on E_10 - 0.264 (half of
   Topstep's 5.28 USD round trip). The prompt (docs/prompts/STAGE_E.31.md:140-143) says "less the Topstep fee in ticks"
   and its own summary (line 7-8) calls 0.53 tick "a round trip", so the literal reading is 0.528. The lead's reading is
   defensible: it follows E.28's FEE_SIDE convention, Topstep's per-side statement, and the K3 loop that pairs two passive
   fills per round trip. But a 10 s markout is one fill closed at the mid, and a real exit pays the other side's fee, so
   0.264 is the less conservative of the two and the spec only shows 0.528 "for information". The rule is fully determined
   (population ZM.v.0 DAY, model (c), buy+sell pooled, mean of N_10, 95% two-sided percentile day-block bootstrap, 2,000
   replicates, seed 31, fail if lower bound <= 0; K2 < 400 fills; K3 < 20 mean round trips per DAY date; only (c) decides).
   Fix (no code): the return's first verdict line states K1 under 0.264 and 0.528 and under drop/no-drop (item 2); a PASS
   that fails under 0.528 or no-drop is written "PASS, fragile (<which>)". If the lead prefers the literal reading as the
   gate, amend now: spec v2 with re-hash costs nothing before the purchase.
2. [ADVISORY, kill rule] The gate uses the dropping markout variant (spec:173-176, 215-216) although E.28 itself notes that
   dropping a markout whose book is crossed or empty "would flatter the mean" (reports/stage_e28_pilot_spec.md:91-95). Same
   remedy as item 1. Also state in one line: the K1 statistic is the pooled mean over fills with a valid 10 s markout
   (ratio of sums inside each bootstrap replicate), and K2 counts all model (c) fills before markout dropping.
3. [ADVISORY, process, recommended before the buy] Buy a canary tranche first. acct-3 is wiped after verification
   (prompt:67-68) and the engine gets its review only after the purchase (spec:246-249), so a data problem specific to the
   real feed cannot be repaired afterwards. Roll-time snapshots for a newly mapped instrument are "NOT FOUND in fetched docs"
   (data_facts.md:43-49), snapshot ts_event is unknown, and the tick scale is unconfirmed (item 9). The code already
   supports it (resume skips settled requests; `other_commits` allows plan keys): `--quote --months 2`, `--buy --months 2
   --approved-usd <sum>` (about 6 USD, months 2024-02 and 2024-01, all four series), `verify31.py --months 2`, a purely
   structural look at the Z1 and Z4 files (per weekday 00:00Z snapshot present for each mapped instrument, v.0/v.1 mapping
   table, match_algorithm and min_price_increment in the definitions; no fills, no markouts, no K1 inputs), then `--quote
   --months 39` and the full buy. The second run re-quotes all 156 (free) and the 39-month sum stays below TARGET.
4. [ADVISORY, failure path] One failed download blocks the whole run and cannot be re-bought. pull31.py:297-328 evaluates
   `resume_state` for all 156 items before any buy; an open commit with no file raises PilotRefused for the entire run
   (exit 2, "the lead decides"), and no flag voids or skips it. The failed commit stays counted in the session
   (pull31.py:622-628; spend_gate.py:140-146 and 279-281 sum every `usd` of the session), the headroom to TARGET is only 0.624 USD, and TARGET is hard-coded
   (pilot31_common.py:76), so a re-buy of any request above 0.624 USD (every Z1 month is 1.5-1.9 USD) is refused by the session
   cap. 156 sequential downloads of up to ~1 GB make one transient failure plausible. The code is safe; the gap is
   recoverability during an unattended run. Fix before the buy: add to README31 and test a lead-only recovery, either (a)
   `gate.settle(quote, actual_usd=0.0, note=...)` for exactly one request when there is no file, no `.partial`, and the user
   has confirmed on Databento's usage page that nothing was billed, or (b) a `--skip <series> <month>` that drops that month
   from all four series and from every later `--months`. State which one applies.
5. [ADVISORY, verification, fix before verify31 is run (not before the buy)] verify31.py does not verify record counts or
   coverage against anything independent, which Part 4 asks for ("sizes, record counts, sha256, date range", prompt:172).
   verify31.py:217-220 compares bytes and sha256 with a purchase record that pull31.write_record computed from the same file
   seconds earlier; verify31.py:239-244 counts records but compares them with nothing; the date check (183-186) is
   an upper bound only, so a file missing its last ten days passes every hard check; and pull31.py:340-341 flags only
   `ratio > 1.0`, so under-delivery is never flagged. Fix: add a hard check `scan.records * itemsize(rtype) ==
   record["settled"]["delivered_record_bytes"] == record["quote"]["billable_bytes"]` (equality is expected, Databento bills
   delivered bytes), a quality check that every UTC weekday of the month has its 00:00Z snapshot or clear for each mapped Z1
   instrument, and that ts_event_max of Z1/Z2/Z3 reaches the last DAY session of the month.
6. [ADVISORY, model (a), non-gating] K parameters were researched for 2023-11..2024-02 (K_algorithm.md title and header) but
   the window is 2020-12..2024-02. The earliest product sheet is 2023-06-21; ZM parameters for 2020-12..2023-05 are unverified
   (the 2021 and 2022 Steps-page captures only confirm the Split/FIFO/Pro Rata/Leveling text). The TOP Max counting rule
   changed on 2023-10-01 (S7 is a pre-announcement, research (d)-8), so 35 of 39 months precede it; spec:93-97 says "from
   2023-10-01" without saying what the engine does before. Also missing from the spec's "Not found" list (spec:130-137):
   FIFO-exception ">=" versus S6's ">" (research (d) conflict 3) and the unconfirmed TOP Max go-live. Fix: report model
   (a) for the full window and for trade dates from 2023-11-01 separately, state the pre-2023-10-02 TOP Max rule used, and add
   the two missing items to the list.
7. [ADVISORY, model (a), non-gating] Two internal inconsistencies in spec 3.1. (i) spec:100-108 lets an order that enters a
   level with no TOP order since it was established become TOP, then says "The virtual order is never TOP (it joins an
   existing level)"; a virtual order joining such a level would be TOP under the quoted S3/S4 rule and would take priority
   over every real order. (ii) The FIFO exception counts the virtual lot in the displayed quantity (spec:100-101) while
   spec:85 says it changes nothing in the book: at Q equal to the real displayed quantity D, real CME applies the exception
   (everyone fills, the virtual gets 0) but the spec's rule does not, and the virtual can take a lot from a real order. Both
   choices can be defended; state one and test the Q = D boundary.
8. [ADVISORY, spec gap for the engine review] The book, BBO, mid0 and Q_ahead must be read only after a record with F_LAST
   for that instrument (data_facts.md:77: "Between records without the F_LAST flag, the book is in the process of updating,
   and the apparent best bid and offer may have already been traded"). The spec never says so. Without it, multi-record
   sweeps expose transient crossed or empty states that the spec then books as exclusions and dropped markouts
   (spec:69, 173-175), which feeds the flattering side of item 2. Fix: one sentence in the spec (v2) or a checklist line in
   the engine review.
9. [ADVISORY, engine review] Tick scale. spec:15-17 gives USD ticks (ZS 0.0025 USD/bu, ZL 0.0001 USD/lb); Databento prices
   for ZS and ZL may be in cents, and data_facts.md:121 says the encodings "need one definition record to confirm". The
   engine should take each tick from Z4's `min_price_increment` and assert tick x contract size = 10.00, 12.50 and 6.00 USD.
10. [ADVISORY, schedule risk] The spec cites `usda_releases_ext.csv` (spec:183-186) and the file does not exist (research/ holds
    only usda_releases.csv; UsdaExt was spawned at 12:45, the same minute as the spec's last edit). spec:185-186 and 263-266
    then make an uncovered trade date "not measured until they cover it" while no part of the verdict may be computed until
    every purchased date is done, so a late or failed UsdaExt blocks the verdict through a split that decides nothing.
    The existing file also carries 40 rule-derived and 2 uncertain FAS dates out of 70, and 2 NOPA dates missing. Fix: put
    uncovered dates in the "other" bucket (counted), record the ext file's sha256 in STATE before the measurement, and report
    the USDA split also on the verified report types only (WASDE, Crop Production, Grain Stocks, Crop Progress, Fats & Oils).
11. [ADVISORY, arithmetic] Grid count. By spec:57-58 (first and last 5 minutes take no placements) and E.28's convention
    (6.5 h session -> 76 grid times, E.28 spec:140), 08:30-13:20 CT has 58 five-minute slots minus the first and last =
    56 grid times (08:35..13:10) and 112 placements; spec:258-259 says 57 and 114 (13:15:00 lies inside the last 5 minutes).
    Effect on K2 arithmetic about 2% (72 instead of 71 dates at p = 0.05). State the boundary convention.
12. [ADVISORY, operations] README31 has no lock and no collector-window note. Two concurrent `--buy` processes would both
    read the ledger once at start (pull31.py:553, 562), both see "new" for the same request and both commit. Fix: `flock` on
    runs/.buy31.lock, and keep verify31.py (decodes about 39 GB at nice 10) out of the AiTrader window 15:30-16:00 PT.
13. [ADVISORY, label] "Front and second month" are volume ranks 1 and 2 (ZM.v.0, ZM.v.1), not necessarily the two nearest
    expiries (spec:16, 224 "month (front, second)"). Z4 gives the expiries. Label those cells "volume rank 2" or assign by expiry.
14. [ADVISORY, spec silence] Databento's condition list marks 3 degraded dates in the window (all Sundays UTC, before any
    open; section A.6). The spec does not mention degraded days. Add one line: no effect expected; the three dates are recorded.
15. [ADVISORY, low] Vendor exception text is printed (pull31.py:440-441, 593-594, 627-628). It cannot contain the key as the
    code stands, but a scrub of the key value (`str(exc).replace(key, "***")`) is a one-line guarantee.
16. [ADVISORY, expectation] Model (c) fills are adverse-selected by construction: a buy at the bid fills only after the whole
    bid level traded and price went one tick or more lower, so E_10 is negative unless price rebounds more than a tick within 10 s.
    K1 is therefore very likely to FAIL, and K3 (two such fills per round trip, about 14 minutes per leg if the fill rate in 60 s
    is near 7%) may fail too. A K1 FAIL under (c) is the Topstep sim rule's verdict, not evidence about ZM's real queue economics;
    the return should say so and lead with models (a) and (b) and the implied-liquidity check beside it.

## C. Things I could not verify

- Whether Databento bills a download that fails mid-stream (item 4): not documented in the repo; the user's usage page knows.
- Whether the temporary account's real credit is 125.00 USD: no balance endpoint, no API call allowed.
- The roll-time snapshot behaviour of continuous symbols (item 3): documented as unknown; only the real files can show it.
- Engine, stats and USDA-extension files: out of scope or not yet written.
