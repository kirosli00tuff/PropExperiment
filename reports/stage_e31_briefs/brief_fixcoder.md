# Brief: FixCoder-OpusXHigh (worker-xhigh, model opus) - Stage E.31, pass-1 fixes to the purchase/verify code

Objective (one): apply SpecReviewer pass 1's items 4, 5 and 12 (reports/stage_e31_briefs/R_spec31.md) and the canary
check of spec v2 section 9 (reports/stage_e31_pilot_spec.md, v2, sha256 31d33e68...) to the purchase/verify code.
Files you own (in reports/stage_e31_briefs/work/pilot/): pull31.py, pilot31_common.py, verify31.py, README31.md,
tests/test_pull31.py, and a new canary_check31.py (+ tests/test_canary31.py).
1. Recovery (item 4, spec v2): a lead-only `--retry-download --series S --month YYYY-MM` path in pull31.py: allowed only
   when that request has an open commit and no target file and no .partial; makes a fresh quote; authorizes against a
   separate retry session id stage-E.31-2026-10-22-pilot-retry whose cap = 125.00 - acct-3 committed so far (the failed
   commit counted as spent); at most one retry per request (refuse a second); then the normal download/check/settle
   path. Everything else in --buy keeps refusing open commits. Tests with the fake client.
2. verify31.py (item 5): hard check delivered record bytes == records x record size == the purchase record's
   settled.delivered_record_bytes, and compare with quote billable_bytes (flag any difference, hard if delivered <
   billable); quality checks: for Z1 every UTC weekday 00:00Z of the request has a snapshot (R with F_SNAPSHOT) for each
   instrument mapped that day; for Z1/Z2/Z3 ts_event max reaches the month's last DAY session (13:20 CT on its last
   grain trade date, data.calendars.grains), else a listed finding. Tests on synthetic files.
3. Item 12: a lock file for --buy and --retry-download (refuse if another holds it); README note: run outside nothing
   heavy, detached with setsid nohup and an rc line.
4. canary_check31.py: structure only, on the purchased files of given months (default 2024-01 and 2024-02): per Z1 file,
   the snapshot presence table (weekday x instrument), the v.0/v.1 instrument mapping per date from the DBN metadata,
   counts of T and F records and whether every T is followed by F records summing to its size or less; from Z4, the ZM,
   ZS and ZL outrights' match_algorithm and min_price_increment (assert ticks 0.10, and ZS/ZL as found, x the contract
   size = 10.00, 12.50, 6.00 USD); for Z2/Z3 record counts per day. It must NOT compute any fill, markout, spread
   statistic or price summary. Output runs/canary31.json and runs/canary31.md; exit 0 when the structure holds, 3 with
   findings.
Run all tests: uv run pytest -q -p no:cacheprovider reports/stage_e31_briefs/work/pilot/tests/test_pull31.py
reports/stage_e31_briefs/work/pilot/tests/test_canary31.py.
Boundaries: no Databento call (fake client only), no API key, no edits under data/, no edits to other workers' files
(mbo_book*, kalgo*, measure31*, stats31*, vol_*), no commits. The lead may be running `pull31.py --buy --months 2` (the
canary) while you work: do not run any real pull31 mode yourself, and keep the CLI of --quote/--buy/--plan unchanged.
Return: the paths, a summary of at most 200 words with test counts, and anything unfinished.
