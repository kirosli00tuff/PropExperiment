# E.31 pilot: per-day tables (the interface between the engine and the stats layer)

Fixed by the lead 2026-10-22 08:3x. The engine (SimCoder: measure31.py and its modules) writes, per trade date,
one parquet file per table under runs/measure31/<YYYY-MM-DD>/ plus a done marker; the stats layer
(StatsCoder: stats31.py) reads all dates and never touches DBN files. Times are int64 UTC nanoseconds; prices
are float64 in USD/short ton; ticks are float64 in the contract's ticks (ZM 0.10, ZS 0.0025, ZL 0.0001).
NaN means missing or dropped. Spec: reports/stage_e31_pilot_spec.md.

## placements.parquet (one row per placement per fill model; spec sections 4 and 5)
trade_date (date32) | session ("DAY"|"OVERNIGHT") | symbol ("ZM.v.0"|"ZM.v.1") | instrument_id (uint32) |
raw_symbol (str) | model ("a"|"b"|"c") | side (int8, +1 buy, -1 sell) | g_ns | j_ns | price |
stale (bool: best price on its side at g differs from j) | filled (bool) | t_fill_ns (int64, -1 if not filled) |
trigger ("queue"|"through"|"") | wait_s (float: time to fill from j, or the censoring time 60.05) |
mid0 (float, the ZM mid just before the fill event; NaN if not filled) | c_half (ticks, s x (mid0 - p)/tick) |
mo_1, mo_10, mo_60 (ticks, markout_h, NaN if dropped) | mo_nd_1, mo_nd_10, mo_nd_60 (no-drop variant) |
zs_d1, zs_d10, zl_d1, zl_d10 (ticks, d = mid(t_f) - mid(t_f - L) of ZS / ZL; NaN = missing) |
usda_min (float, signed minutes from the nearest USDA release on the same trade date; NaN = none) |
imb (float, side-adjusted s x I at j) | touched (bool: within 60 s of j a trade printed at p or the opposite
best quote reached p; E.28's touch rate)
The fill-model columns depend on the model; g_ns, j_ns, price, stale, imb are the same across models.

## loop.parquet (one row per trade date, symbol ZM.v.0, DAY session, model; spec section 6)
trade_date | symbol | model | round_trips (int32) | entries_filled (int32) | orders_placed (int32) |
mean_rt_s (float, mean duration of completed round trips; NaN if none)

## implied.parquet (one row per trade date, symbol, session; spec section 8)
trade_date | symbol | session | n_ab, vol_ab (trades with aggressor A or B) | n_none, vol_none (no displayed
resting quantity on the passive side at the price) | n_short, vol_short (displayed resting quantity below the
trade's size) | n_n, vol_n (trades with side N)

## days.parquet (one row per trade date and symbol; spec section 2)
trade_date | symbol | instrument_id | raw_symbol | included (bool) | reason (str, "" if included) |
n_records | inversions | bad_flag_records | crossed_moments | max_gap_day_s | placements_day | placements_on
