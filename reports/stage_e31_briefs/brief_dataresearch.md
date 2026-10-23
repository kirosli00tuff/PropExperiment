# Brief: DataResearch-OpusHigh (worker-high, model opus) - Stage E.31 data and calendar facts

Objective (one): establish, with verbatim quotes from fetched sources, the data, calendar and contract facts
the ZM order-book pilot spec needs. Four topics:

(a) Databento GLBX.MDP3 historical data (docs at databento.com/docs, Context7 databento docs, and the
installed `databento` / `databento_dbn` packages in .venv for field names):
  - MBO: does a historical MBO request include book snapshot records at the start of each day/session or
    of the request (F_SNAPSHOT flag, action R "clear book")? At what time? What happens for a request that
    starts mid-week? With continuous symbols (ZM.v.0, ZM.v.1, stype_in "continuous"), when the mapped
    instrument changes at a roll, does the new instrument's book start from a snapshot?
  - MBO actions and sides: A, C, M, R, T, F, N; for T (trade) records is `side` the aggressor side, and when
    is it N; how a fill of a resting order appears (F with order_id); flags F_LAST, F_TOB, F_MBP,
    F_BAD_TS_RECV, F_MAYBE_BAD_BOOK; the meaning of `sequence`, ts_event vs ts_recv; whether implied
    liquidity appears in MBO or MBP-1 (expected not).
  - definition schema: the fields for match algorithm (`match_algorithm`), implied-spread/implied
    eligibility (e.g. `market_depth_implied`, flags, `security_update_action`), `min_price_increment`,
    `contract_multiplier`, trading-status fields; values expected for CBOT grains.
  - mbp-1: fields and whether trades carry aggressor side.
(b) USDA release calendar 2022-11-01..2024-02-29 with release times (ET): WASDE (and Crop Production released
  with it), NASS Grain Stocks, NASS Crop Progress (Mondays 16:00 ET in season), FAS Weekly Export Sales
  (Thursdays 08:30 ET; note holiday shifts), NASS Fats & Oils (oilseed crushings). Separately, NOPA monthly
  crush (not USDA). Sources: usda.gov/oce WASDE archive, NASS calendar/report archives, FAS export sales
  archive. Output CSV reports/stage_e31_briefs/research/usda_releases.csv: date,time_et,report,source_url.
  Missing or uncertain dates are marked, never guessed.
(c) CBOT daily price limits for ZM, ZS, ZL: the semi-annual reset rule (which months, effective date, formula)
  and the ZM limit values in effect in 2022-11..2024-02 if findable (CME notices via web.archive.org, or the
  CME rulebook chapter for soybean meal).
(d) ZM, ZS, ZL contract specs: tick size and value, listed months, CT trading hours (overnight and day
  session in 2023-2024), last trading day / first notice day rules (to explain volume rolls), and the board
  crush ratio (10 ZS : 11 ZM : 9 ZL) as CME states it.
Fetching: cmegroup.com blocks direct fetches: use web.archive.org snapshots. When WebFetch fails, fall back to
`scrapling extract get <url> <file>`, then `scrapling extract fetch <url> <file>`. Save every page used as
evidence raw under reports/stage_e31_briefs/research/pages/data/ and read by grep. If a WebSearch returns an
over-budget notice, stop searching, log it with the time and return. Use at most 60 searches.

Output: reports/stage_e31_briefs/research/data_facts.md (one section per topic, each fact with value, source,
verbatim quote; a "not found / conflicting" list), usda_releases.csv, and
reports/stage_e31_briefs/research/data_fetch_log.md (URL, UTC time, sha256, method, ok/failed).
Boundaries: research only. No Databento API call, no API key, no market data download, no repo edits outside
reports/stage_e31_briefs/research/. KResearch-OpusHigh covers the K matching algorithm: do not research it.
Mark anything not from fetched text [unverified].
Return: the paths, a summary of at most 200 words, and anything unfinished.
