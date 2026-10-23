# Brief: PullCoder-OpusXHigh (worker-xhigh, model opus) - Stage E.31 Part 3, purchase and verify code

Objective (one): write the span-search, quote, buy and verify code for the ZM pilot data, to spec sections 0, 1
and 9 of reports/stage_e31_pilot_spec.md (read sections 0, 1, 2, 9 and 10; section 3.1 is still being filled
and is not yours). Synthetic tests only.

Reuse: E.28's reports/stage_e28_briefs/work/B_pilot/pilot_pull.py, pilot_common.py, verify.py and README.md
sections 2-5 (guards, raising guards on the data namespaces in quote-only modes, resume rules, .partial ->
link -> read-only, record-byte check, settle, condition list). Read them by section. They are read-only: copy
what fits into new files. Also reuse data.pull_universe.download, data.adapter.delivered_record_bytes,
data.pull_mes.RequestCappedGate, data.config (VENDOR_ROOT, DATASET, require_databento_key(account="acct-3")).
acct-3's pilot-only guard (data.config.PILOT_ONLY_ACCOUNTS) stays: use SpendGate directly, never data.pull_step2
or data.pull_hist. Do not edit anything under data/.

Files (all new, in reports/stage_e31_briefs/work/pilot/):
- pilot31_common.py: constants and guards. Series Z1 ZM mbo [ZM.v.0, ZM.v.1] continuous; Z2 ZS mbp-1 [ZS.v.0]
  continuous; Z3 ZL mbp-1 [ZL.v.0] continuous; Z4 definition [ZM.FUT, ZS.FUT, ZL.FUT] parent. Month request
  bounds: 16:00 America/Chicago on the last calendar day of the previous month -> 16:00 America/Chicago on the
  month's last calendar day, in UTC (zoneinfo; check Oct/Nov 2023 DST: 2023-10-31 16:00 CDT = 21:00Z). The last
  month is Feb 2024 and its end must equal exactly 2024-02-29T22:00:00Z. Refuse before any call: any other root,
  schema, symbol set or stype; any month after 2024-02; any end other than the month rule; any account but acct-3.
  TARGET = (125.00 - acct-3 committed so far) - 2.00, rounded down to the cent (122.27 now).
- pull31.py with modes:
  --plan (no call): prints the 4k requests for --months k, target paths, TARGET, acct-3 ledger position.
  --span-search: free ledgered quotes (session stage-E.31-2026-10-22-pilot-span, cap 0.00), month by month from
    2024-02 backwards, all 4 series per month; stop at the first month whose addition makes the cumulative sum
    exceed TARGET; k = months before it; k < 2 = buy nothing (exit 1). Writes runs/span31.json with every quote,
    k, the cumulative sums. Hard earliest month 2019-06 (grain calendar coverage starts 2019-05-01).
  --quote --months k: fresh quotes of all 4k requests (session stage-E.31-2026-10-22-pilot), runs/quote31.json
    with each quote and the sum.
  --buy --months k --approved-usd X: refuses unless runs/quote31.json's quotes are this plan's, under 24 h old,
    sum <= TARGET and sum <= X < sum + 0.01; session cap TARGET; order Z1 latest month first, then earlier Z1
    months, then Z2, Z3, Z4 (same month order); each request: fresh re-quote must not exceed its quote31 value by
    more than 1% (else stop, rc 1), authorize, commit, download to
    VENDOR_ROOT/GLBX.MDP3/<schema>/<SERIES>_<SYMBOLS>/range=<start>_<end>.dbn.zst, link, read-only, record-byte
    check, settle (billing > 3% above the quote: settle pro rata, stop the remaining buys, rc 1), then a per-file
    runs/purchase31_<series>_<month>.json (bytes, sha256, quote, settled). Resume: an already settled file is
    skipped; an open commit with no file is refused (rc 2) for the lead; never delete anything. Refuse if acct-3's
    ledger holds commits for any request other than the Part 1 volume request (session
    stage-E.31-2026-10-22-volume) and this plan's requests.
  Save the free condition list (metadata.get_dataset_condition) for the span, best effort.
- verify31.py: for every purchased file: bytes, sha256, record counts by rtype and instrument_id, ts_event
  min/max inside [start, end), no record at or after 2024-03-01T00:00:00Z, the DBN metadata (schema, symbols,
  stype, start, end, mappings) matches the request; writes runs/manifest31.json and copies it beside the data as
  manifest.json. Exit 0 ok, 3 data-quality findings only (listed), 2 failure.
- README31.md: every command, exit codes, resume rules, run from the repo root; detached buys with setsid nohup
  and an rc line in the log (the E.28 README pattern).
- tests/test_pull31.py: fake Databento client only; guards refuse each forbidden input; month bounds incl. DST;
  span search stopping rule and k < 2; buy refusals (stale, mismatched, sum > TARGET, approved mismatch,
  re-quote +1%); resume cases; verify flags a record at or after the end. Run with
  uv run pytest -q -p no:cacheprovider reports/stage_e31_briefs/work/pilot/tests/test_pull31.py
Boundaries: no Databento call of any kind, no API key read, no network. SimCoder (later) owns the book,
matching and measurement files (mbo_book*, kalgo*, measure31*); vol_pull.py and vol_measure.py are Part 1's:
do not edit them. No commits. Keep output short (pytest -q).
Return: the paths, a summary of at most 200 words, test counts, and anything unfinished.
