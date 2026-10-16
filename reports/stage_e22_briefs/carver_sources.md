# Stage E.22 Part B: Carver's published method, sourced (CarverReader)

Written 2026-10-16 (fetches 07:59-08:05 UTC = 00:59-01:05 PDT). Scope is the lead_spec_B.md S3 (rule) and S4
(rounding) needs. Every value below has a verbatim quote from a saved file. Code is quoted from pysystemtrade at a
pinned commit, and code line numbers refer to the saved copy. Nothing here is a decision. Where the post and the
code differ, both are given, and the choice is left to the lead (S4(b) says follow the post).

## 0. Sources (saved raw, read by grep)

Blog posts (qoppac.blogspot.com, Robert Carver):

| ID | URL | Saved file | Fetched (UTC) | sha256 (saved file) |
|---|---|---|---|---|
| P-NOV21 | https://qoppac.blogspot.com/2021/11/mr-greedy-and-tale-of-minimum-tracking.html ("Mr Greedy and the Tale of the Minimum Tracking Error Variance - Part two") | reports/stage_e22_briefs/carver_pages/carver_2021_11_mr-greedy-part-two.html (text extract: same name .txt, sha 1dca12a118d742512f102145da63d42504b65b9718cde22488c3a67e7f9abf67) | 2026-10-16T08:00:06Z | 0675e1c74a13a2f781fa64c6c221a9d0f10ecaf9de42d828a614a86dd993addb |
| P-OCT21 | https://qoppac.blogspot.com/2021/10/mr-greedy-and-tale-of-minimum-tracking.html (1 Oct 2021) | reports/stage_e13_briefs/pages/TrendCarry/carver_2021_10_mr-greedy-and-tale-of-minimum-tracking.html (.txt sha 1f7f02a6f5aa0c889bda331923b63bd7e901e5b974f3548da969b28a63736e2a) | 2026-10-03T21:42:54Z (E.13 fetch_log F25) | cae733da739e8e3d8cbeb5eba2eb394d09b4fd99a485f1aafd2f435c35db8194 |
| P-JUN21 | https://qoppac.blogspot.com/2021/06/optimising-portfolios-for-small.html (25 Jun 2021) | reports/stage_e13_briefs/pages/TrendCarry/carver_2021_06_optimising-portfolios-for-small.html (.txt sha 86dc5c38038f3e834c6d08ea6641715fab71da1f7ee972012db549a7fda425f0) | 2026-10-03T21:45:07Z (E.13 F31) | ec72d5e23e39a306337d26b281f67c3635d6ec4bc8bfebea56820cb9d749a312 |
| P-JAN16 | https://qoppac.blogspot.com/2016/01/correlations-weights-multipliers.html | reports/stage_e22_briefs/carver_pages/carver_2016_01_correlations-weights-multipliers.html (.txt sha 1e606c8f468670a5cac756ae86bc581a3416a731e78b48d884ef1eb009b4f988) | 2026-10-16T08:04:35Z | d069bb10804478719014fec4100e393abcf1b6673ce1f7f1eb5a5c82bf281ee2 |
| ARCH | https://qoppac.blogspot.com/2021/11/ (archive; one post that month: Part two) | carver_pages/archive_2021_11.html | 2026-10-16T07:59:49Z | 041033635b0549bf3386a818747d25769c8a55e98ef92127b144c87d520f7579 |

The November 2021 archive lists a single post, "Mr Greedy and the Tale of the Minimum Tracking Error Variance - Part
two". P-OCT21 carries an update banner pointing to it: "UPDATE (November 2021) The alternative version is here . This
is now what I use in production."

pysystemtrade (github.com/robcarver17/pysystemtrade). Pinned to the master commit
a62269d27707806ba61f516791b71a9cd14cf268 (committer date 2026-09-29T21:13:27Z, from the GitHub API, saved as
carver_pages/gh_master_commit.json). Each file was fetched with curl from
`https://raw.githubusercontent.com/robcarver17/pysystemtrade/a62269d27707806ba61f516791b71a9cd14cf268/<path>` and
saved as `reports/stage_e22_briefs/carver_pages/pst_<path with / -> _>.txt`. The full log, with UTC time, HTTP code,
bytes and sha256 for every fetch, is `carver_pages/fetch_log.tsv`. The files cited below:

| ID | path | fetched (UTC) | sha256 |
|---|---|---|---|
| C-DEF | sysdata/config/defaults.yaml | 08:00:42Z | 6ab5e12dae82dd4b2b78f0cf951bc258b92f81bb4f9a975d6bbb746d6d7e9972 (byte-identical to the E.13 copy at commit 326b5d4) |
| C-EWMAC | systems/provided/rules/ewmac.py | 08:00:42Z | 6794f76f5183e71a760b5a7a05fbd6fa79485374a7ac1d0a72cfd697863702ba |
| C-VOL | sysquant/estimators/vol.py | 08:00:43Z | d2823c230c6fb6336eed667a16ffdb361f77bd7033fc0fa02065a6bfbb7463cd |
| C-RAW | systems/rawdata.py | 08:01:31Z | 8857bdaca5fde314fdfa29ceb1b138b02ec6f7cf85ea75830e51f75f7dd56584 |
| C-DATE | syscore/dateutils.py | 08:01:31Z | ffd25f0f9c3f299fc4db4c8595e7d56759a31d94795a7f4d9956a2d8dae9faab |
| C-CH15 | systems/provided/futures_chapter15/futuresconfig.yaml | 08:00:45Z | dc5319d6fb0c7517a6d033a8524b68d1b49efb833fbded1c0e2595e321a84f38 |
| C-ROB | systems/provided/rob_system/config.yaml | 08:00:45Z | 469dc123dd0133e0da7950ebc259061b1a13623b7f60e35430e02bda3f6a7262 |
| C-POS | systems/positionsizing.py | 08:00:47Z | a75386ff4e14893ad0288b34212f4b73d71781828138b3b736d88c0631ab8320 |
| C-PORT | systems/portfolio.py | 08:00:46Z | 65eaa0e96bb04ceb567808dcfe12c1c564f29dcc535bb3f07ede7386b5c652a9 |
| C-DM | sysquant/estimators/diversification_multipliers.py | 08:00:43Z | 4e33f92a46af860db077e52131b782367d7cd9183b11d86df2ca197d9e06fefa |
| C-CORR | sysquant/estimators/correlations.py | 08:00:47Z | 6c24ea70a07e3025df3e278cca22b653f60640e56ae15457da84954ac142f336 |
| C-POOL | sysquant/estimators/pooled_correlation.py | 08:02:45Z | a7d6783b6468470d3cca9e5a37373a49668be378d9328792099d99f1cd79e29c |
| C-CORRT | sysquant/estimators/correlation_over_time.py | 08:02:44Z | 47a59bb57f77fd672d71ab5bee32d3db6970ada2092f80bd22e1c93367bd8a76 |
| C-EXPC | sysquant/estimators/exponential_correlation.py | 08:02:45Z | 80779dc9b6b7a6fdd41e86ca0d60d4f91590a2316996613edbb898ba7aa50024 |
| C-BUF | systems/buffering.py | 08:00:43Z | e73d927fb9e0e173a7837c60c587aea8fe2632dbd3eef4c7c2bdd7ea63d76458 |
| C-ABS | systems/accounts/account_buffering_subsystem.py | 08:03:22Z | 4d6f924c4bde8513960adb276d44465cb3ee989f8d4afb0b5a2b1306737009cc |
| C-ABSYS | systems/accounts/account_buffering_system.py | 08:03:17Z | de03857df62ba8d869906192ebf10175821b8c83fa5b851c0fb91acb3dcc5ca7 |
| C-GREEDY | systems/provided/dynamic_small_system_optimise/greedy_algo.py | 08:00:43Z | 2cad3ccc976223739a862f8447990de5ddfd5344e26b670d3eacad68f5c8d79c |
| C-OPT | systems/provided/dynamic_small_system_optimise/optimisation.py | 08:00:43Z | 07a13d7a4487c30318648cb70d8124bd1355cbcfacd54bdde591ddec165324fa |
| C-DBUF | systems/provided/dynamic_small_system_optimise/buffering.py | 08:00:44Z | b01dc56b0b9e41dc9ce8585c6bba83839aed2d02a2d30bf3ce729855f41faed4 |
| C-STAGE | systems/provided/dynamic_small_system_optimise/optimised_positions_stage.py | 08:00:44Z | 9b547630ed6063cb6a8f56d792036eeca33a461233827f44cc15cb177d8d4a82 |
| C-CONS | systems/provided/dynamic_small_system_optimise/set_up_constraints.py | 08:00:44Z | 01ca932d94b900407bc8a606bd426576dcf599aa08734298566e6d8faa166146 |
| C-STRAT | syscore/pandas/strategy_functions.py | 08:02:44Z | 1f495b081676f1a1a0f73315ad38e312e4d1c58b257b6f9f88ccc28d4ac8f3df |
| C-GEN | syscore/genutils.py | 08:02:44Z | 6acc1fc99b54bbc873df551fadd112bfee8cf117a82acec6da8b9190bd986d75 |
| C-W | sysquant/optimisation/weights.py | 08:05:01Z | 1f0aedd1c1dc64727eccfde4ff34246b75a2117a5da36da0b75775df4a16f8ac |

All fetch dates above are 2026-10-16.

## A. Constants table (rule, S3)

| # | Item | Value | Verbatim quote | Source (file:line) |
|---|---|---|---|---|
| A1 | EWMA definition for EWMAC | pandas `ewm(span=L)`, i.e. span (alpha = 2/(L+1)), not com; `min_periods=1` | `fast_ewma = price.ewm(span=Lfast, min_periods=1).mean()` / `slow_ewma = price.ewm(span=Lslow, min_periods=1).mean()` / `raw_ewmac = fast_ewma - slow_ewma` / `return raw_ewmac / vol.ffill()`; comment: "We don't need to calculate the decay parameter, just use the span" | C-EWMAC:120-124, :117 |
| A2 | EWMAC speeds | (8,32), (16,64), (32,128), (64,256) defined as `Lfast`/`Lslow` | "ewmac8_32: ... Lfast: 8 Lslow: 32", ... "ewmac64_256: ... Lfast: 64 Lslow: 256" | C-CH15:28-63 |
| A3 | Price for EWMAC and denominator | back-adjusted daily price; denominator = `rawdata.daily_returns_volatility` | `data: - "rawdata.get_daily_prices" - "rawdata.daily_returns_volatility"` | C-CH15:30-32 (and each rule) |
| A4 | Daily returns for the vol | price differences, not % | "Gets daily returns (not % returns)" ... `dailyreturns = instrdailyprice.diff()` | C-RAW:105-126 |
| A5 | Price-vol for EWMAC denominator (configured systems) | `mixed_vol_calc` on the price differences (see A12): EWMA std span 35, blended with its slow average | `volatility_calculation: func: "sysquant.estimators.vol.mixed_vol_calc" name_returns_attr_in_rawdata: "daily_returns" multiplier_to_get_daily_vol: 1.0 days: 35 min_periods: 10 slow_vol_years: 10 proportion_of_slow_vol: 0.3` | C-DEF:112-119 |
| A5b | Variant: `ewmac_calc_vol` (used by some rules in rob_system) | `robust_vol_calc(price.diff(), 35)`: EWMA std span 35 plus a floor at the rolling 5% quantile of vol over 500 days (min 100 obs). No slow-vol blend | `vol = robust_vol_calc(price.diff(), vol_days)` (vol_days=35); `vol_floor: bool = True, floor_min_quant: float = 0.05, floor_min_periods: int = 100, floor_days: int = 500` | C-EWMAC:127,169; C-VOL:17-26 |
| A6 | Forecast scalars, book set (Systematic Trading ch.15 config) | ewmac8_32 **5.3**, ewmac16_64 **3.75**, ewmac32_128 **2.65**, ewmac64_256 **1.87** | "forecast_scalar: 5.3" (8_32), "forecast_scalar: 3.75" (16_64), "forecast_scalar: 2.65" (32_128), "forecast_scalar: 1.87" (64_256) | C-CH15:36,45,54,63 |
| A6b | Forecast scalars, Carver's own production config (estimated) | momentum8 **5.949404365193165**, momentum16 **4.104172020369661**, momentum32 **2.786994330124792**, momentum64 **1.9093945630747895** (these rules are `ewmac` with Lfast/Lslow 8/32 ... 64/256) | "momentum8: 5.949404365193165", "momentum16: 4.104172020369661", "momentum32: 2.786994330124792", "momentum64: 1.9093945630747895"; rule: "momentum8: function: systems.provided.rules.ewmac.ewmac ... Lfast: 8 Lslow: 32" | C-ROB:364-368, :247-254 |
| A7 | Target average absolute forecast | 10 | "average_absolute_forecast: 10.0"; and "an average absolute value of 10 is my own preference" | C-DEF:143; P-JAN16 (.txt line 222) |
| A8 | Forecast cap | +-20 (individual and combined) | "forecast_cap: 20.0" | C-DEF:141; C-CH15:71. The combined forecast is capped after the FDM: "# apply cap and /or any non linear mapping" applied to `raw_multiplied_combined_forecast` (C-FC, forecast_combine.py:92-103, sha da67aa30f050c9a1098fd961eba8f4dad5d8735553c1e60b88db20a8eb8912c8) |
| A9 | FDM formula | DM = min(1/sqrt(w' H w), 2.5) | docstring: "Given N assets with a correlation matrix of H and  weights W summing to 1, the diversification multiplier will be 1 / [ ( W x H x WT ) 1/2 ]"; `dm = np.min([1.0 / risk, dm_max])`; `dm_max: float = 2.5` | C-DM:78-80, :94, :76 |
| A9b | FDM correlation treatment | correlation **of the forecasts**, **pooled** across instruments (stacked), weekly ("W") resample, exponential with ew_lookback 250 (multiplied by the number of instruments when pooled), expanding window, **negative correlations floored at 0**, DM capped at 2.5, DM smoothed with EWMA span 125 | `forecast_correlation_estimate: pool_instruments: True func: sysquant.estimators.pooled_correlation.pooled_correlation_estimator frequency: "W" date_method: "expanding" using_exponent: True ew_lookback: 250 min_periods: 20 cleaning: True rollyears: 20 floor_at_zero: True forward_fill_data: True`; `forecast_div_mult_estimate: ... ewma_span: 125 dm_max: 2.5`. Blog: "I also floor negative correlations to avoid getting very large values for the multiplier." Pooling: `length_adjustment = len(downsampled_data)` then `correlation_over_time(pooled_data, **kwargs, length_adjustment=length_adjustment)`. Floor: `corr_matrix_values[corr_matrix_values < floor] = floor` | C-DEF:152-169; P-JAN16 .txt:240; C-POOL:20-34; C-CORR:151 |
| A10 | IDM formula and cap | same formula as A9, cap 2.5, smoothed span 125 | `instrument_div_mult_estimate: func: sysquant.estimators.diversification_multipliers.diversification_multiplier_from_list ... ewma_span: 125 dm_max: 2.5` | C-DEF:250-254 |
| A10b | IDM correlation treatment | correlation of **instrument subsystem returns** (`pandl_across_subsystems`), weekly, exponential ew_lookback 25, expanding, **floor at 0** | `instrument_correlation_estimate: func: sysquant.estimators.correlation_over_time.correlation_over_time_for_returns frequency: "W" date_method: "expanding" using_exponent: True ew_lookback: 25 min_periods: 20 cleaning: True rollyears: 20 floor_at_zero: True forward_fill_price_index: True`; `pandl = self.pandl_across_subsystems().to_frame()` | C-DEF:238-248; C-PORT:415 |
| A11 | Position formula (subsystem) | subsystem position = vol_scalar x forecast / 10, where vol_scalar = daily cash vol target / instrument value vol | `subsystem_position_raw = vol_scalar * forecast / avg_abs_forecast`; `vol_scalar = cash_vol_target / instr_value_vol` | C-POS:128, :201 |
| A11b | Pieces of A11 | block value = price x multiplier x 0.01; instr value vol = block value x daily % vol; daily cash vol target = capital x vol target % / 100 / 16 | `block_value = underlying_price.ffill() * value_of_price_move * 0.01`; `instr_ccy_vol = block_value.ffill() * daily_perc_vol`; `notional_trading_capital * percentage_vol_target / 100.0`; `daily_cash_vol_target = annual_cash_vol_target / ROOT_BDAYS_INYEAR` | C-POS:323, :286, :492, :482 |
| A11c | Portfolio position | position = subsystem position x instrument weight x IDM | `subsys_position * inst_weight_this_code_reindexed`; `notional_position = notional_position_without_idm * idm_reindexed` | C-PORT:265, :245 |
| A11d | Price used for % vol and sizing | the current (held) contract's price, not the back-adjusted price | `prices = self.get_instrument_raw_carry_data(instrument_code).PRICE` ... `daily_prices = prices.resample("1B").last()`; `perc_vol = 100.0 * (return_vol / denom_price.ffill().abs())` | C-RAW:711-722, :268 |
| A12 | Instrument vol estimate (mixed vol) | recent = EWMA std of daily price differences, span 35, min 10 obs, `adjust=True`; slow = EWMA (span = slow_vol_years x 256 business days) of the recent vol series; blend = 0.3 x slow + 0.7 x recent | `vol = daily_returns.ewm(adjust=True, span=days, min_periods=min_periods).std()`; `slow_vol_days = slow_vol_years * BUSINESS_DAYS_IN_YEAR`; `long_vol = vol.ewm(span=slow_vol_days).mean()`; `vol = long_vol * proportion_of_slow_vol + vol * (1 - proportion_of_slow_vol)` | C-VOL:188, :170-173 |
| A12b | Slow-vol lookback and proportion | defaults.yaml: 10 years, 0.3. Function default is 20 years. Carver's production config: 20 years, 0.35, backfill True | defaults: "slow_vol_years: 10", "proportion_of_slow_vol: 0.3"; function: `slow_vol_years: int = 20, proportion_of_slow_vol: float = 0.3`; rob_system: "slow_vol_years: 20 proportion_of_slow_vol: 0.35 backfill: True" | C-DEF:118-119; C-VOL:125-126; C-ROB:20-27 |
| A12c | Annualisation | x sqrt(256) = 16 | `BUSINESS_DAYS_IN_YEAR = 256.0`, `ROOT_BDAYS_INYEAR = BUSINESS_DAYS_IN_YEAR**0.5`; `return ROOT_BDAYS_INYEAR * daily_vol / 100.0` | C-DATE:26-27; C-PORT:1263 |
| A12d | Mixed vol has no quantile floor | only an absolute minimum of 1e-10 (unlike robust_vol_calc) | `vol = apply_min_vol(vol, vol_abs_min=vol_abs_min)` (no `apply_vol_floor` call in mixed_vol_calc) | C-VOL:121-180 |
| A13 | Static position buffer (classic system) | buffer = 10% of the average position (position at forecast +10, x instrument weight x IDM); trade to the buffer edge | `buffer_method: forecast buffer_size: 0.10 buffer_trade_to_edge: True`; `average_position = abs(vol_scalar_indexed * instr_weight_this_code_indexed * idm_indexed)` / `buffer = average_position * buffer_size`. Blog: "I've always used a simple 10% of average position (the position I'd get with an average forecast of +10)." | C-DEF:296-298; C-BUF:167-171; P-NOV21 .txt:95 |
| A13b | Buffer with rounding | optimal, top and bottom are each rounded with pandas `.round()` (half to even). If the last position > top, go to top; if < bottom, go to bottom; else hold. The docstring says "floor and ceiling" but the code rounds | `use_optimal_position = use_optimal_position.round()` / `top_pos = top_pos.round()` / `bot_pos = bot_pos.round()`; `if last_position > top_pos: if trade_to_edge: return top_pos ... elif last_position < bot_pos: ... return bot_pos ... else: return last_position`; docstring "If we're rounding positions, then we floor and ceiling the buffers." | C-ABS:141-144, :197-208, :118 |

Notes on A:
- A5 versus the spec's S3.1. In both of Carver's configured EWMAC systems (ch.15 and rob_system "momentum" rules), the
  EWMAC denominator is the same mixed vol (A12) used for sizing. It is not a plain 35-span EWMA. The plain 35-span
  version exists only as `robust_vol_calc` in `ewmac_calc_vol`, and that version adds a 5%-quantile floor. Which to use
  is the lead's call.
- Scalars: the spec asks for "Carver's published scalars for these four speeds". Two published sets exist (A6 is the
  book config, A6b is his estimated production values). I have not chosen between them.

## B. Greedy dynamic optimisation, November 2021 version

### B.1 From the posts (numbered steps)

1. **Units: portfolio weights.** P-OCT21 (.txt:65): "We move in steps of per_contract_value . Since everything is being
   done in portfolio weights space (eg 150% means the notional value of our position is equal to 1.5 times our
   capital: see the  first  post for more detail), not contract space, these won't be integers; and the
   per_contract_value will be different for each instrument we're trading." P-JUN21 (.txt:51): "Since we want to hold
   0.23 of a contract, our desired portfolio weight is going to be 0.23 * 0.96 = 0.22."
2. **Objective: tracking error of the held portfolio against the unrounded optimal portfolio, plus costs.**
   P-OCT21 (.txt:82): "The tracking error portfolio is just the portfolio whose weights are the gap between our current
   weights and the optimal unrounded weights, and what we are trying to minimise is the standard deviation of that
   portfolio." Code in the post (.txt:70-74): `solution_gap = weights - self .weights_optimal_as_np` ...
   `(solution_gap.dot( self .covariance_matrix_as_np).dot(solution_gap))** .5` ... `return track_error + trade_costs`.
   P-NOV21 (.txt:127): "Remember the utility function is tracking error - costs. Tracking error is measured in units of
   annualised standard deviation."
3. **Covariance: from instrument returns, not subsystem returns.** P-OCT21 (.txt:83): "The covariance matrix used to
   calculate the standard deviation is the one for instrument returns (not trading subsystem returns) ... For this
   particular methodology the use of instrument returns is a complete no-brainer." P-JUN21 (.txt:53): "We now need a
   covariance matrix, which we construct from a correlation and a standard deviation."
   P-JUN21 (.txt:70): "We don't  floor_at_zero . I want to know if correlations are negative".
   **Shrinkage (Nov 2021)**: P-NOV21 (.txt:153): "What eventually came to the rescue, just as I was about to give up,
   was shrinking the correlation matrix. ... shrinkage is a good way of fixing PSD issues." The post gives **no
   shrinkage value or target** (see B.3, code: 0.5 toward zero off-diagonal).
4. **Greedy loop: start point, direction, step, stop.** P-OCT21 (.txt:28-46, code): "## Starting weights ## These will
   eithier be all zero, or in the presence of constraints will include the minima", then
   `while not done:` evaluate every single-asset step and keep the best one, `if new_best_value<best_value:` accept it,
   `else: # we can't do any better (or we're in a local minima, but such is greedy algorithim life) break`. One step is
   `temp_step[i] = temp_step[i] + per_contract_value[i] * direction[i]` (.txt:57): one contract in one instrument.
   Direction (.txt:64): "The direction will always be the sign of the optimal position. So we'd normally start at zero
   ( start_weights ), and then get gradually longer (if the optimal is positive), or start at zero and get gradually
   shorter (if the optimal position is a negative short). This means we're only ever moving in one direction which makes
   the greedy algorithim work." P-NOV21 (.txt:73) confirms that the November version keeps this: "the algo always starts
   at zero (in the absence of corner case constraints) and then starts changing position with the sign of the optimal
   unrounded position."
5. **Cost penalty.** P-OCT21 (.txt:78-80, code): `trade_gap = weights - self .weights_prior_as_np`,
   `trade_costs = sum ( abs (costs_per_trade * trade_gap * self .trade_shadow_cost))`, with zero cost when there are no
   prior weights. P-NOV21 (.txt:71): "Remember the shadow cost is a multiplier on the cost penalty applied to the dynamic
   optimisation." **Shadow cost value (Nov 2021): 250.** P-NOV21 (.txt:136-141): "So a shadow cost of 250 would
   annualise costs and put them in the same units as the tracking error. To recap then: - Shadow cost 250 - Buffer size
   0.0125". (The Oct value is superseded: P-OCT21 .txt:84 "It defaults to 10 in my code"; P-NOV21 .txt:127 "In my prior
   post I said that a shadow cost of 10 'looked about right', but a few moments thought reveals it is not.")
   How costs are measured (P-NOV21 .txt:53-58): "Work out the current cost of trading in actual $$$ terms / For each
   historic trade, multiply that by the number of contracts traded / ... / Deflate these figures according to the
   difference in price volatility between then and now / So for example, if the vol of S&P 500 is 20% with a price of
   5000, that's a price vol of 1000 / If that figure was 200 at some point in the past, then we'd divide the historic
   cost by 5". (Strictly, this describes his backtest cost accounting. B.3 shows that the optimiser's cost input uses
   the same deflator.)
6. **Buffering on tracking error (three steps).** P-NOV21 (.txt:103-117):
   - "if the tracking error of the current portfolio is less than some buffer level, we'll stick with the current
     portfolio (='inside the buffer'). If it isn't, we'll trade in such a way to bring our tracking error down to the
     buffered level (='trading to the edge of the buffer')."
   - Step 1: "we calculate the tracking error of the current portfolio, versus the portfolio with unrounded optimal
     positions (let's call this tracking error /unrounded). If this is less than the buffer, we stick with the current
     positions. No optimisation is needed."
   - Step 2: "we do the optimisation, which gives a portfolio consisting of integer positions."
   - Step 3: "we now calculate a second tracking error: the tracking error of the currently held portfolio versus the
     integer positions (tracking error/rounded). By construction, this tracking error will be lower than tracking
     error/unrounded."
   - "Adjustment factor = max((x - b)/x, 0)" with x = tracking error/rounded and b = the buffer. "We then multiply all
     our required trades (from current to integer optimised) by the adjustment factor. And then round them, obviously."
   - "So if the tracking error is less than the buffer, we don't trade. Otherwise we do a proportion of the required
     trade. ... Note that (ignoring the fact we need to round trades) doing this will bring our tracking error back to
     the edge of the buffer."
7. **Buffer value: 0.0125 (annualised TE units).** P-NOV21 (.txt:125): "Firstly, with an average target risk of 25%, a
   10% buffer around that means our dynamic buffer size should be around 1.25% (not 2.5% as you might expect as this
   buffer is expressed differently)." Recap (.txt:140-141): "Shadow cost 250 / Buffer size 0.0125".
   The buffer does not replace the shadow cost (.txt:121): "Note the buffer doesn't replace the shadow cost; it's in
   addition to it."
   The value is derived for a 25% risk target. The spec's tau is 20%. Whether to rescale it (the same "10% around the
   target" logic would give a different number) is a **lead decision**; the post states only 0.0125 at 25%.
   The shadow cost 250 is derived under stated assumptions (.txt:129-136): "Sharpe Ratio 1.0 / Target annual standard
   deviation 25% ... If SR = 1, then tracking error is effectively in annualised return units".
8. **Constraints (optional, production).** P-OCT21 (.txt:194-197): "A 'reduce only' constraint ... A 'do not trade'
   constraint ... Maximum position constraints ... It adjusts the starting weights and direction depending on the
   constraints above, and also introduces minima and maxima into the optimisation (and prevents the greedy algorithim
   from adjusting weights any further once they've hit those)."
9. **Known limit.** P-NOV21 (.txt:75): "every time the underlying forecast changes sign, we'll definitely trade
   regardless of the size of the shadow cost."

### B.2 pysystemtrade code (commit a62269d), same steps

- Optimal (target) positions are the unrounded, unbuffered notional positions:
  `self.get_notional_position_before_risk_scaling(instrument_code)` (C-PORT:1211). These are converted to weights with
  `weights_optimal = contracts_optimal * per_contract_value` (C-OPT:54). Per-contract value is
  `fx_rate_aligned * contract_prices * contract_multiplier` / `trading_capital` (C-PORT, get_baseccy_value_per_contract
  and get_per_contract_value_as_proportion_of_capital, about lines 1242-1260).
- Backtest loop: the prior is the previous day's optimised integer position, starting from zeros:
  `previous_optimal_positions = portfolioWeights.allzeros(self.instrument_list())` ...
  `previous_optimal_positions = copy(optimal_positions)` (C-STAGE:62, :70). On any exception the previous positions are
  kept: `print(msg) return previous_positions` (C-STAGE:90-98).
- Step 1: `if tracking_error_of_prior_smaller_than_buffer: return self.weights_prior_as_np_replace_nans_with_zeros`,
  with TE of prior versus `self.weights_optimal_as_np` and `tracking_error < tracking_error_buffer` (C-OPT:108-140).
- Step 2: `optimised_weights_as_np = greedy_algo_across_integer_values(self)`. If the result is all zeros:
  `self.log.error("All zeros in optimisation, using prior weights")` and return the prior (C-OPT:164-170).
- Objective: `return track_error + trade_costs + constraint_function_value`, with
  `track_error_var = solution_gap.dot(self.covariance_matrix_as_np).dot(solution_gap)` and
  `trade_costs = sum(abs(costs_per_trade * trade_gap * trade_shadow_cost))`, where trade_gap = weights - prior
  (C-OPT:219-265). A negative variance raises "Negative covariance when optimising!" (C-OPT:241-246).
- Greedy loop (C-GREEDY:6-69): start at `obj_instance.starting_weights_as_np`. In each pass, try +1 contract
  (`per_contract_value[i] * direction[i]`) on each instrument not at its limit, keep the single best improvement, and
  stop when no step improves ("# we can't do any better" / `break`). Start weight is 0 unless constraints bind
  (C-CONS:187-198). Direction is `sign(optimum_weight)`, with `minimum >= 0` giving +1, `maximum <= 0` giving -1 and
  NaN giving +1 (C-CONS:169-184). `sign(0)` returns 1.0 (`return copysign(1, x)`, doctest `>>> sign(0)  1.0`,
  C-GEN:142-157).
- Step 3: `tracking_error_of_prior = self.tracking_error_against_passed_weights(prior_weights_as_np, optimised_weights_as_np)`
  (C-OPT:191-194); `excess_tracking_error = tracking_error_of_prior - tracking_error_buffer`,
  `adj_factor = excess_tracking_error / tracking_error_of_prior`, `adj_factor = max(adj_factor, 0.0)` (C-DBUF:25-28).
  If `adj_factor <= 0` keep the prior (C-OPT:207-208). Otherwise
  `adjusted_trades_weight_space = adj_factor * desired_trades_weight_space`, converted to contracts and
  `np.round(adjusted_trades_in_contracts)` (round half to even), and new = prior + rounded trades (C-DBUF:39-60).
  Final positions use `np.round(value)` again (C-W:54-61).
- Covariance: `covariance_from_stdev_and_correlation(correlation_estimate, stdev_estimate)` (C-STAGE:272-273).
  Correlation is the instrument-returns correlation, shrunk:
  `corr_matrix.shrink_to_offdiag(shrinkage_corr=self.correlation_shrinkage, offdiag=0.0)` (C-STAGE:285-286), where
  shrink = `shrinkage_corr * prior_corr_values + (1 - shrinkage_corr) * corr_values` (C-CORR:95). Stdev is the
  annualised % vol, `ROOT_BDAYS_INYEAR * daily_vol / 100.0` (C-PORT:1263), i.e. the mixed vol of A12 divided by the
  held-contract price. Returns are `self.rawdata.get_daily_percentage_returns(instrument_code)` (C-PORT:1117).
- Correlation estimate settings for the optimiser (C-DEF:311-326): `instrument_returns_correlation: func:
  sysquant.estimators.correlation_over_time.correlation_over_time_for_returns interval_frequency: "W" frequency: "7D"
  date_method: "rolling" using_exponent: True ew_lookback: 75 min_periods: 10 cleaning: True offdiag: 0.0 rollyears: 5
  floor_at_zero: False forward_fill_price_index: True clip: 0.99`. Here `frequency` resamples cumulated returns
  (`index_prices_for_correlation.resample(frequency).last()` then `.diff()`, C-CORRT:15-22), and the EW estimate is
  `ewm(span=ew_lookback, min_periods=min_periods, ignore_na=True)` (C-EXPC:151-152), so the span is 75 seven-day
  returns. The most recent estimate before the date is used, with a zero-off-diagonal identity fallback (C-PORT:1066-1080).
- Speed parameters (C-DEF:327-330): `small_system: shadow_cost: 50 cost_multiplier: 1.0 tracking_error_buffer: 0.0125
  shrink_instrument_returns_correlation: 0.5`. These are read as `small_config["shadow_cost"]` and
  `small_config["tracking_error_buffer"]` (C-STAGE:156-157). The dataclass defaults (unused when the config is present)
  are `trade_shadow_cost: float = (10,)` and `tracking_error_buffer: float = (0.02,)` (C-DBUF:8-9).
- Cost input (C-STAGE:188-262, C-STRAT:164-172): cost per unit weight = `cost_multiplier * cost_per_contract /
  notional_value_per_contract_as_proportion_of_capital / capital`, times a deflator.
  `cost_per_contract` uses the **final** price and FX (`self.get_raw_price(instrument_code).ffill().iloc[-1]`).
  The deflator is `vol_price = daily_returns.rolling(180, min_periods=3).std().ffill()`,
  `final_vol = vol_price.iloc[-1]`, `cost_scalar = vol_price / final_vol`, and missing values are set to 10000.0
  (C-STAGE:215).

### B.3 Differences between the November post and the code (S4(b): follow the post)

| # | Item | Post (Nov 2021 unless noted) | Code (a62269d) |
|---|---|---|---|
| D1 | Shadow cost | **250** ("Shadow cost 250") | **50** (defaults.yaml:327); dataclass default 10 |
| D2 | TE buffer | 0.0125 | 0.0125 (same); dataclass default 0.02 |
| D3 | Correlation shrinkage | "shrinking the correlation matrix", no value or target given | 0.5 toward a zero off-diagonal matrix |
| D4 | Correlation estimate settings | Nov: none stated. June 2021 config: "frequency : "W" ... ew_lookback : 25 ... floor_at_zero : False ... offdiag : 0.0 clip : 0.90 interval_frequency: 1M" (P-JUN21 .txt:57-68). June text: "a half life of 25 weeks" | ew_lookback 75 (as a pandas **span**, not a half-life), 7D returns, re-estimated weekly, rolling 5 years, clip 0.99, floor_at_zero False |
| D5 | Cost deflation | "Deflate these figures according to the difference in price volatility between then and now" (backtest accounting) | Optimiser costs are deflated by rolling-180-day price-vol / **end-of-sample** price-vol, with cost per contract at the **final** price. Used as-is in a backtest this is look-ahead; lead to decide |
| D6 | Rounding of the adjusted trade | "And then round them, obviously." (method unstated) | `np.round` (half to even) |
| D7 | Optimiser failure | not discussed | all-zero result or exception keeps the prior positions |
| D8 | Constraints in backtest | "reduce only", "do not trade", maximum position (production) | backtest: reduce-only for markets not trading, optional long-only; no maximum positions |
| D9 | Sign of zero optimum | not discussed | `sign(0) = 1` (moves long) |

No difference was found in: the start point (zero), the direction (sign of the optimum), the step (one contract), the
stop rule (no improvement), the objective (sqrt(gap' Sigma gap) + shadow x sum |cost x trade|), the buffer steps 1-3
and the adjustment factor max((x-b)/x, 0), where x = TE(current vs integer-optimised).

## C. Carver's rounded baseline in the 2021 comparisons

- It is **rounded AND buffered** (the classic 10%-of-average-position buffer, trade to edge; A13/A13b):
  - P-OCT21 (.txt:177): "The green line is the unrounded position we'd ideally want to have on, wheras the red line
    shows our simple rounded (and buffered) position."
  - P-JUN21 (.txt:329): "a time series of positions (original unrounded, rounded & buffered, and optimised using a cost
    penalty)", and the code used, "rounded_position = system.risk.get_original_buffered_rounded_position_for_instrument(instrument_code)"
    (.txt:347); also (.txt:158) "this is a substitute for the buffering method I currently use".
  - P-NOV21 (.txt:63): turnover is measured "at the portfolio level (after dynamic optimisation, or after buffering for
    the static system)". The benchmark is (.txt:172) "the 30 or so instrument static portfolio you'd actually be able to
    trade with say $500K in your account" rather than "the simple rounded static portfolio with say 100 instruments".
- Code for the rounded and buffered baseline: with `buffer_method` "none" it is `optimal_position.round()` (C-ABSYS:84).
  With the default "forecast" method it is A13b (rounded edges, trade to edge).
- The spec's fallback (round half away from zero, no buffer) is therefore **not** what the posts describe. Carver's
  baseline applies his position buffer. The posts do not state the rounding direction for halves. The code uses
  pandas/numpy round (half to even).

## D. Reported results at small capital (context only)

- P-OCT21 ($100K, 45 instruments, "the same basic 3 momentum crossover+carry rules I introduce in chapter 15"; .txt:86-91):
  "if we were able to take fractional positions ... (which has a Sharpe Ratio of 1.17). But we can't take fractional
  positions! (sad face and a Sharpe Ratio of just 1.06). But if we run the optimiser ... a Sharpe Ratio of .... 1.19."
  "Costs? About 0.13 SR units for all three versions." "correlation of returns 0.94). OK the rounded portfolio is even
  more correlated (0.97)". "the optimised version is significantly better than the rounded positions: a T-statistic of
  3.7".
- P-OCT21 ($50K, .txt:181): "the optimised version is still better than the rounded (SR improvement around 0.1), but
  nowhere near as good as the unrounded (SR penalty around 0.2). ... The tracking error vs the unrounded portfolio is
  0.72% for the optimiser (versus 0.49% earlier with 100K), but is even higher for the rounded portfolio (0.76%). The
  correlation between the optimiser and ideal unrounded optimal returns has dropped to 0.86 (0.94 with 100K); but for
  rounded positions is even lower: 0.84 (0.97 with 100K)."
- P-OCT21 (.txt:187): "just let our positions be  rounded . This gives us a SR penalty of around 0.1 SR versus what we
  could do with unrounded positions. ... (eg it's 0.3SR with 50k)."
- **Caveat (Carver's own):** P-NOV21 (.txt:12): "Thus the results in my previous post were misleading and wrong"
  (because of costs and turnover with sparse positions).
- P-NOV21 (114 instruments, 25% target; .txt:211-217): "the return correlation between the unrounded and optimised
  portfolios. This comes in at a very unshabby 0.986." "The Sharpe Ratio of the optimised portfolio is 1.336 gross,
  1.287 net. ... The portfolio level turnover is 51.1 times a year." "the benchmark portfolio hits a Sharpe Ratio of
  gross 1.322, net 1.275 ... Turnover is 37.5." "the (unachievable!) Sharpe Ratio of the unrounded portfolio with 114
  instruments is 1.359." Holdings (.txt:203): "in the dynamic optimised portfolio we end up holding around a quarter to
  a third of what's available on any given day".
- Earlier rule of thumb (P-JUN21's companion, static post, E.13 file carver_2021_06_static-optimisation-of-best-set-of.txt:35):
  "There is around a 20% penalty to Sharpe if you can only hold one contract; around 5% with a maximum position of
  two. This falls to zero if you can hold 3 or 4 contracts".

## E. Not found / UNKNOWN / [unverified]

- **Capital of the Nov 2021 dynamic test: UNKNOWN.** The text names $500K only for the static benchmark (.txt:174).
  The dynamic run's capital is not stated in the text I extracted (it may be in an image).
- **Shrinkage value in the Nov post: not stated** (code 0.5 to zero; D3).
- **Why the code's shadow cost is 50 rather than the post's 250: UNKNOWN.** No later post found. I ran one WebSearch
  (no Carver hits) and three blog-search pages (sidebar links only). 1 of 30 web searches used; no budget notice seen.
- **Rescaling of the 0.0125 buffer and the 250 shadow cost to tau = 20%:** the post derives both at 25% (and SR 1 for
  the shadow cost) and gives no rule for other targets. This is a lead decision, not a sourced value.
- **Rounding of halves in Carver's rounded baseline:** not stated in any post; the code uses half-to-even.
- **`length_adjustment` for the non-pooled instrument-returns correlation:** the default is 1
  (`length_adjustment: int = 1`, generic_estimator.py:36, sha 4fa5ae5fde4b01b5022c025cc935bbefc1a30b96e8cef5ef917462316e803b96).
  I did not trace whether any caller passes another value for that path [unverified].
- **Book texts (Systematic Trading, AFTS): not fetched.** The forecast scalars come from the repo configs only. A6 is
  labelled the ch.15 config, which Carver's own post ties to "chapter 15 of my first book"; the printed book table
  itself is [unverified].
- `pysystemtrade` is fetched at master a62269d (2026-09-29). Its code may differ from what ran in Nov 2021 (D1 and D4
  probably reflect later changes). The 2021 code was not fetched.
