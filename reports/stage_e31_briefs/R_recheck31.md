A: GO; B: GO

# Stage E.31 Part 4: the one re-check of both review passes (ReCheck-FableXHigh)

Reviewer: Fable 5.1 (xhigh), 2026-10-23, finished 06:09 PDT (clock from `date`). Review only. No Databento call, no key read, no
edit except this file, no commit. The engine was not run on real data and no measure31 output was opened. Spec sha256 recomputed
31d33e68736b3c13ae46afcd0bf8d28411bbb3d96864802a6193cf5f33b9f61a (unchanged since pass 2). `work/` is untracked, so there is no
git diff: I read the code in place and compared it with the two reports' line citations.

Invariants: holdout `unlocks_logged` 0 and `all_ok` true (first run after I had read the brief and the two reports, not as my very
first command, and again at 06:09); REGISTRATION.md 0 bytes; `git status -- data live ops` empty; ledger 36,690 lines at both
checks (I wrote nothing). Pilot test folder: `uv run pytest -q -p no:cacheprovider .../tests` = 328 passed in 15.26 s (lead's figure
confirmed). `ruff check` on the changed files is clean; its 3 hits are in tests/test_vol_measure.py (Part 1, not part of the fixes).

No BLOCKING item in A or B. The advisories below are for the lead; none stops the purchase or the measurement.

## A. Purchase path: GO

What I checked and found sound.

1. Retry can re-buy one failed request, once. `retry_refusals` (pull31.py:790-809) refuses, before the key, when: a `.partial` or an
   overlapping file exists (342-351); the target exists (796); any retry-session commit exists for that request key (799-804, "at
   most one retry"); or the pilot session has no open commit for it (805-808). A settled request has `pilot[-1]` = settle, so
   `open_pilot_commit` (407-410) returns None and the target file exists: two independent refusals. `resume_state` (359-386) and
   `_retry_resume` (389-404) turn a retry commit with no file into a refusal ("second failure"), a retry commit with a file into
   settle-only, and a retry settle into done. Tests: `test_retry_is_refused_before_the_key` (no_commit, settled, file, partial,
   overlap, foreign_commit, bad series, bad month, late month), `test_a_failed_retry_stops_and_a_second_retry_is_refused`,
   `test_retry_rebuys_one_failed_download_then_buy_resumes_and_verify_passes`, all pass.
2. Caps. The retry session cap is 125.00 minus every acct-3 USD committed at the start (pilot31_common.py:398-402; pull31.py:490-494),
   the failed commit counted as spent. `SpendGate.authorize` (data/spend_gate.py:174-210, 362-380) checks session spent + quote against
   that cap and acct-3 spent + quote against the account cap 125.00. `RequestCappedGate` (data/pull_mes.py:163-181) adds the request cap =
   failed commit's quoted_usd x 1.01 (pull31.py:837-839, 850-854). The fresh quote is ledgered; a retry is never looser than the
   account cap. A second retry of another request sees the first retry in both the acct sum and its own session spend, which only
   tightens it (README31.md:323-326). `spend_target` (pilot31_common.py:385-395) treats the retry session as a pilot session, so TARGET
   stays 122.27 and a retry does not lower it. Worst case acct-3 total = 0.72502 + pilot sessions <= 122.27 + one retry <= 125.00.
3. Lock. `buy_lock` (pull31.py:176-195) takes `flock(LOCK_EX | LOCK_NB)` on runs/.buy31.lock and refuses at once (exit 2, holder
   text). `_buy_main` (669-673) and `_retry_main` (826) read the ledger and the key only inside it; the kernel frees it on process death.
   `test_a_held_lock_refuses_buy_and_retry_before_the_ledger_and_the_key` passes for both modes.
4. Nothing else in --buy/--quote loosened. `main` still calls `pc.require_account` first (531), `pc.plan` runs `check_request` on every
   request (pilot31_common.py:217-221, 328-347), `--quote` keeps `install_forbidden_guards` (566-571), `--buy` and the retry keep
   `client.batch = ForbiddenNamespace()`, `_buy_one` keeps fresh re-quote -> 1% check -> `authorize` (request, session, account) ->
   `commit` before `download`, and `_finish` keeps the 3% stop. `download` (data/pull_universe.py:584-604) unlinks its own `.partial`
   on failure and links without replacing, so a failed download leaves exactly the state the retry requires. Recovery text in spec v2
   section 9 (lines 276-278) matches the code (re-quote that request alone, once, inside acct-3's cap, failed commit counted).
5. verify31 hard checks. `record_bytes_match_purchase_record` (verify31.py:297-299) = DBN v3, decoded bytes == records x record size
   (mbo 56, mbp-1 80, definition 520) == the records' own length fields x 4 == the purchase record's settled
   `delivered_record_bytes`. On the canary manifest, all six Z1-Z3 files deliver exactly the quoted billable bytes (diff 0 in 6 of
   6), so "below the quote is hard" is right for mbo and mbp-1: those files are exact.
6. The relaxation for Z4 (verify31.py:308-314) was wrong as written, for the reason the lead gave. Canary Z4 deliveries: 2024-01
   55,505 records vs 57,645 billable/520 (-2,140, ratio 0.96288); 2024-02 49,650 vs 51,657 (-2,007, ratio 0.96115). I read ts_recv
   and instrument_id of the two Z4 files (no prices): every UTC date Sunday to Friday of both months is present, with a step-wise
   count per day (2,140, then 2,161, then 1,986 in January as instruments expire; 1,986 every day of February); the January shortfall equals one daily snapshot
   (2,140 = the 2024-01-01 and 2024-01-02 day counts) and February's is about one day. So the quote overcounts about one boundary
   day of definitions; the file is not short of a day. Settled at the quote (pessimistic), exit now 3 (runs/verify31_canary_0600.log:
   only `Z4 ...: delivered_bytes_equal_quoted_billable`, quality). `test_verify_compares_delivered_with_the_quoted_billable_bytes`
   (test_pull31.py:804-820) asserts hard for Z1-Z3 and quality for Z4 at both 1.02 and 0.99. Lead ruling 1 and 2 are implemented as stated.
7. The other relaxations in canary_check31/verify31 are right. `min_price_increment_amount` is a note (canary_check31.py:144-145): the
   real files give 1.0, 1.0, 0.06, which Databento defines as a spread/leg pricing value, not the USD tick; the check that stays is
   tick x unit_of_measure_qty = 10.00, 12.50, 6.00 USD or 1000, 1250, 600 cents (139-143, 146-148), and the canary table shows
   10.0/12.5/6.0 with match algorithm K for all outrights. The ts_recv basis for "before request start" (verify31.py:167-171)
   follows Databento's index time; ts_event-only cases are counted as info and `no_record_at_or_after_request_end` stays hard on both stamps.
   Parent mappings keyed by child raw symbol (224-240) still require every root and reject foreign roots (test at test_pull31.py:1029-1042).

### A. Items

1. [ADVISORY, docs] The Z4 exception is in the code but not in the text. verify31.py:19-20 and 26-28 and the byte_checks docstring
   (288-289) say below the billable bytes is hard; README31.md:250, 261-262 and 272-273 say the same, and 272-273 says such a file
   "stops the measurement". After ruling 1 that holds for Z1-Z3 only. Reword the three places.
2. [ADVISORY, recovery arithmetic] The text says the 2.00 USD margin pays for a retry (spec v2 section 9 line 277-278; README31.md:211-212;
   pilot31_common.py:23-26). Seven Z1 requests cost more than 2.00: 2021-05 2.308, 2021-03 2.152, 2021-04 2.150, 2023-10 2.091,
   2023-03 2.088, 2022-08 2.061, 2022-06 2.015 (span31.json), 2.331 for the largest with the 1% rule. What binds is acct-3 headroom:
   2.63 USD after the full buy at quoted prices (fits the largest with 0.30 spare), 2.005 if the buy reaches the 122.27 session
   cap (would not fit it). It fails safe (the account cap refuses) but the recovery may then be unavailable for those months; say so,
   and say the retry is paid from the headroom, not from "2.00".
3. [ADVISORY, verification] With ruling 1 a truncated Z4 would look the same as the expected one-day shortfall. Add a quality check that
   each UTC Sunday-to-Friday date from the first full UTC date of the request has definition records, and no day's count drops far
   below its neighbours'. The canary files pass such a check today (evidence in 6 above). Not a purchase matter.
4. [ADVISORY, not exercised] --retry-download and the lock have run only against fake clients; the canary buy ran on the earlier
   pull31 (buy31_canary.log 13:48 PDT, pull31.py edited 01:10 PDT). They share `download`, `QuoteOnlyView` and the gate with the code
   the canary did exercise. Whether Databento bills a download cut mid-stream stays unknown; the code counts it as spent.
5. [FOR THE LEAD, not decided here] The canary's own verdict is exit 3 on Z1 T/F pairing (runs/canary31.md "Findings"; spec v2 section 9
   makes "structure holds" the condition for buying the rest). Facts only: snapshots present for every weekday and mapped instrument
   (missing 0 in both months), F without T 0, F sum equal to the T size for 86% of T; T with no F 27,828 of 526,503 (5.3%) and 23,577 of
   449,295 (5.2%); F sum above the T size 3.3% in both months. My GO covers the purchase code, not that call.

## B. Engine: GO

Item 1 (BLOCKING in pass 2) is fixed. The change is local: `F` records of an open group are collected in `group[7]`
(measure31_core.py:548, 552, 565-569), and `close_group` (489-494) allocates the event on the book as it stood (`close_event`) and
only then calls `book.on_fill` for the collected fills; `drain` (476-482) uses `close_group`; orphan F records (no group) still count at once
(566-567). Nothing that `_k_allocation` (402-413, line numbers identical to R_engine31's citation) or mbo_book31.py:270-289 reads
changed. My probes, on synthetic data from the test helpers (script in the session scratchpad, nothing under the repo):

- 70-lot sell against a 150-lot snapshot TOP order, 20-lot order behind, virtual buy behind: `ka.allocate([150,20,1],70,top=0,top_room=100)`
  = [70, 0, 0]; the engine's model (a) virtual order is unfilled, TOP order still o1 with count 70; model (b) and (c) unfilled.
- Mutation check: with the old order put back (fills counted before `close_event`), model (a) fills at 08:35:10 in this scenario and in the
  95 + 6-lot scenario, so the probe detects the bug. With the fix: no fill, TOP lost after the event with count 101 and its timestamp kept.
- Group closed only by `drain` (F_LAST on the last F, nothing after): count 70, virtual unfilled. Orphan F: count 70 at once, diag
  `fill_records_without_trade` 1.
- Chunk size 1, 2, 3, 4, 5, 7 give the same fills, TOP and count as the default for all three scenarios (the group state crosses chunks).
- Differential, 400 random synthetic streams, fixed vs old-order mutant: placements with a model (b) or (c) difference 0; model (a)
  differs in 3 placements (the intended effect); chunk 1, 2, 3 variance 0.

Other items. 5: `measure31.py --summarize-diag` (623-662) sums the keys diag.json really writes (measure31_core.py:831-843, measure31.py:555-556,
588) and gives the two ratios; counts only; test at test_measure31.py:704-726. 7: README_measure31.md:31-32 and 39 run `--workers 4` and name
the 15:30-16:00 PT window. 8: skipped implied prints are counted (`implied_trades_mid_update`, measure31_core.py:426-428) and listed in the README.
`checked_tick` (measure31.py:215-233) takes ZM in USD and ZS/ZL in USD or cents through the factor tuple (205); ZM 0.1 x 100 = 10, ZS 0.25 x
5000 x 0.01 = 12.5, ZL 0.01 x 60000 x 0.01 = 6.0 all pass. `load_manifest` (94-114) refuses exit code 2 or any failed hard check, so a manifest
with only Z4 quality findings (exit 3) loads. Rulings 2, 3, 4, 6, 10, 11 and the section 7 erratum are not re-opened.

### B. Items

6. [ADVISORY, compute limits] `max_workers(None)` is still min(8, cpu_count // 2) = 8 here (measure31.py:598-600); the ruling to use 4 lives
   only in the README command. A run without `--workers` is 8 x ~0.8 GB. Lower the default cap to 4 or keep the flag in every runbook line.
7. [ADVISORY, tests] No test passes `chunk=` to `InstrumentRun.run` and none asserts TOP state after a `drain`-closed group
   (test_measure31.py:642-668 close the group with a following M record). Both behave correctly in the probes above; add the two tests so
   a later edit cannot break the deferred fills silently.
8. [ADVISORY, process] `--summarize-diag` is a separate manual step (README_measure31.md:35-36). The lead's reading of any result should
   include `measure31_diag_summary.json` (events_mid_update and events_without_passive_fill per event). The canary already shows 5.2-5.3% of
   Z1 T records with no F after them, so expect `events_without_passive_fill_per_event` of at least that order.

## Not verified

- Anything against the real Databento service: retry and lock under a real client, billing of a failed download, real-feed T/F/C order in the
  engine (only the canary counts above speak to it).
- "Nothing else regressed" in measure31_core.py rests on 328 passing tests, matching line numbers of the untouched regions cited by pass 2,
  and the differential above. There is no copy of the file as pass 2 read it to diff against; kalgo31.py and mbo_book31.py carry mtime
  01:05 PDT, inside pass 2's reading window, and their cited lines still match.
- Wall-clock and memory of a full measurement (not run, by the brief).
