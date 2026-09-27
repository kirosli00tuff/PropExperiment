# Brief: ReleaseSourcerNamed-OpusHigh (worker-high on opus) - sourced data

Objective: a verified list of release instants, 2019-05-01 through 2026-06-21, for the member-named releases the lead
ruled into the calendar (lead ruling OC-N; reports/stage_e2b_release_names.json has each member's verbatim words):
1. PPI (BLS, 8:30 ET).
2. ISM Services (Non-Manufacturing) PMI (ISM, 10:00 ET, normally the third business day of the month).
3. G.17 Industrial Production and Capacity Utilization (Federal Reserve Board, 9:15 ET).
4. API Weekly Statistical Bulletin (American Petroleum Institute, normally Tuesday 4:30 pm ET, moved in holiday weeks).
5. USDA NASS Crop Progress (weekly in season, normally Monday 4:00 pm ET).
6. Treasury note and bond auction results: the coupon auctions the members' words cover (read their quotes in
   reports/stage_e2b_release_names.json; if their words cover all note and bond auctions, take every 2-, 3-, 5-, 7-, 10-,
   20- and 30-year nominal coupon auction, and say whether TIPS and FRNs are in or out and why, from the quotes). The
   instant is the auction's close for competitive bids (results follow within minutes); TreasuryDirect / fiscaldata.treasury.gov
   auction data is the source (an API download counts as a saved page: save the JSON/CSV and quote its rows).
Read reports/stage_e2b_briefs/00_common.md and reports/stage_e2b_briefs/g1_release_common.md (binding). The finished macro
list (reports/stage_e2b_release_sources_macro.json and data/vendor/release_pages/macro_scripts/) shows the file shape and a
working fetch/verify approach (bls.gov needs Wayback copies). A release series whose historical dates no source shows
(possibly the API bulletin) may be entered from its standing published schedule with each entry marked "[unverified]" and
the rule quoted; say so in the log. Output: reports/stage_e2b_release_sources_named.json (same shape: coverage, entries
with a "release" name from the list above, cancellations, coverage_table, verification) and a log
reports/stage_e2b_release_sources_named_log.md. Reply with the paths, a summary of at most 200 words, counts per release and
year, and anything unverified.
