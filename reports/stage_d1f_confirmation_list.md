# Stage D.1f pre-registration: the second holdout and the frozen confirmation list

STATUS: FROZEN (Stage D.1e, lead, hashed 2026-09-22T08:50:46Z after the Task 5d adversarial review was
adjudicated and re-reviewed). After hashing nothing in this file changes; a
later stage that needs a different list writes a new declaration under a new name.

Written by the Stage D.1e lead against the stage prompt. Every number below is fixed
before any bar of the extended history has been bought, downloaded or read. The two
values marked [FILLED BEFORE HASHING] are computed in this stage from existing data only
(Task 2's epsilon and Task 3's power table) and are written in before the hash.

Companion document: docs/NULL_CRITERIA.md (the standing null criteria; hashed together
with this file). Where the two overlap, NULL_CRITERIA.md holds the definitions and this
file holds the list.

## 0. Provenance: what "frozen" refers to

Repository state at declaration: commit f1bb073 (2026-09-22) plus the uncommitted Stage D.1e
files listed in the progress entry. The definitions below are given by reference to files
whose sha256 is recorded here; the harness itself is pinned by the freeze manifest of section
1.5 step 1b, not by this list. A member
whose referenced file changes before D.1f runs is INVALID until this list is re-issued
under a new hash; D.1f must verify every hash before running.

Declarations and statistics code:
- reports/stage_d1b_family_f_declaration.md  9c17c508c50ee66e37fc471136368c4b364922bc16437f7d9f0b5d860314448d
- reports/stage_d1d_timeframe_declaration.md  07a906328a2aae2097ae30ea02e5b547cf37247245e1cd91b63808809619c745
- strategy/research/f_data_native/_stylized_facts.py  a692c47f226638876cda94541c5669e821873ef10f401b1564a85365ebf1f056
- strategy/research/g_timeframe/_stylized_facts.py  61ae1930f9b2aa466e178842f0b02d0486e22c084615ea491fdaccd54b39653d
- strategy/research/g_timeframe/resample.py  a0851b43ef33818563805b04d4ee27d851914f2e42e8c7ba3255d04e2f40bdc2

Trial modules (the code is the definition; every parameter is the literal in the file):
- strategy/research/a_session_clock/_clock.py  a57f26a8cf30b6b7ab15fd84478a39117423ac7f377fe9cebc9eee02e699c1d1
- strategy/research/a_session_clock/h1_european_open_overnight_drift.py  651033cf22e4de1043153d586dd8f5a26275d7caa9b6f7b15511eadbc64b99c3
- strategy/research/a_session_clock/h2_rth_close_window_session_position.py  0f471834dd8745b8458c7b4a5bec953a09c7511c2fdc6a6aae1d5e67349abedd
- strategy/research/a_session_clock/h3_weekend_effect.py  35b6dd6d057b31f3e488e2987e6a06345c34a89a933243bbd4fabee90500bf86
- strategy/research/a_session_clock/h4_eth_vs_rth_decomposition.py  ce0c68fa0539a4b46efa459066d40821e544f3abc1163297e4dc8d0d54f0ee7d
- strategy/research/b_reference_breakout/h1_friction_aware_opening_range_breakout.py  20741f35ed0bd82be7be712abb923b8ebaf87d43192378247d24b8d671a2221a
- strategy/research/b_reference_breakout/h2_prior_day_stop_cascade.py  92ca8e44d4afb8cebbca1817988c665c473c0d323101fe830756096bb8cbd592
- strategy/research/b_reference_breakout/h3_breakout_vs_fade_horse_race.py  0d6fe324abfc207e0a1d24642b7a52408e75504b3b5d6af400a580039174477b
- strategy/research/b_reference_breakout/h4_narrow_range_contraction_breakout.py  aa6d9ee5a86e1d8629b39cefc3e2b3fe337358c2d5583bfae35987f44c7d9952
- strategy/research/c_short_horizon_reversal/h1_magnitude_conditioned_reversal.py  0512716d662bbda9e436f5c9b7d3e3fdf7356058d93a42dd1ddb951d75fa1d0c
- strategy/research/c_short_horizon_reversal/h2_post_spike_exhaustion_fade.py  609014ce0da97ce8090fe78a0d2082fcaa178d9cfd45022c60a2b02f5dc557e7
- strategy/research/c_short_horizon_reversal/h3_close_location_value_reversal.py  38819a8a29a5056ec64bcc1313ed9d62d109372f3d84474732730be5d91c3427
- strategy/research/c_short_horizon_reversal/h4_passive_fill_reversal.py  004880079dfc9809fa6f618c41c85773f223ad59061ae8b684a46eecd9a338a8
- strategy/research/c_short_horizon_reversal/h4_passive_fill_wrapper.py  098def61082520e9cc4ea6b165a864a0860e9a06d0d2ad36c8f3fed01222b4ac
- strategy/research/d_volatility_state/h1_trailing_volatility_regime_gate.py  447c39113fdb50f76e4aa7284cad1d7018cf46698a0932cb3704faac4d9a812e
- strategy/research/d_volatility_state/h2_inverse_volatility_sizing.py  c05aaab3843b96efc57ec3c2c97f6ba6ee9d2fa677ff55c38595bf2a4a4f8b8f
- strategy/research/d_volatility_state/h3_range_compression_gate.py  2b3fcaf64adf5250b56298e755db37bb67be2b20e46e5130ad1d5c96c5f24da5
- strategy/research/d_volatility_state/h4_overnight_gap_fade.py  68f041035bf34bc49e578ffd8f3ed6020efbfd1cece91f483dbcba31406800f9
- strategy/research/d_volatility_state/_metrics.py  80a0d3929e95378fe30f8ae7b96f6527aa3c94908aff10ec6ba5e3bc583bcc4f
- strategy/research/e_calendar_event/h1_scheduled_macro_drift.py  94e92ff15efe2160c5e967da6d1a415385681a43cf500505004b87b363ab25b2 (pre-amendment hash; the post-amendment hash is recorded in reports/stage_d1f_harness_freeze.json under the declared amendment of 5.7, and for these two files only, section 0's INVALID rule and 5.6's refusal read the freeze manifest, NEW-1)
- strategy/research/e_calendar_event/h2_post_release_momentum.py  b2f09ab6e71dafe554c8db35c04a02f3476cb25e0f3783ca740ebffc19b5f005 (pre-amendment hash; same carve-out as h1_scheduled_macro_drift.py, NEW-1)
- strategy/research/e_calendar_event/h3_quarterly_witching.py  85c8c4904ea882800f365025aecc5e4e6982d2443e9462cde798bfd4d4b9b10c
- strategy/research/e_calendar_event/h4_turn_of_month.py  4bbca056ec154c158654330d28cb3aab3623da05e3f238077bb1d327a81a9b0d
- strategy/research/g_timeframe/retests.py  2780096507bcd33912e9abe76102acc3a168f9135cd9e2a2705c50bc4672ada1
- strategy/research/_d1b_accounting.py (ALL_TRIALS: the 24 label-to-factory pairs)  386addcb7014a26ed5a183520e21d11eaa4a4fe1c49d5dc0ecc465950e46b716

The 31 trial IDs are the label strings in strategy.research._d1d_accounting.ALL_TRIALS
(24 from _d1b_accounting.ALL_TRIALS plus the 7 RETESTS in g_timeframe/retests.py). D.1f
imports that tuple; it does not retype labels or factories, except the two confirmation
factories of E-H1 and E-H2 listed in A1 (NEW-1).

Trial assembly, parameters and continuity targets (added after the Task 5d review, R-2):
- strategy/research/_lead_accounting.py  456be614636748809ab986656654a1fcf7269ee542cc769f77e36da1e9c401ee
- strategy/research/_d1d_accounting.py  df741c259408647fc5e09540e9669dc8c384e657a59991b41ef6243c6ca8c8ff
- strategy/research/f_data_native/trials.py  cf9073b326c5b43bc5d74dc5bcacfd1da05ee2bd85c9b4bcd4df5f41f020b9fd
- strategy/research/g_timeframe/trials.py  0a0bd610ae6e2f6644b0429eda3d27654d09f49b6662bfdc46bc111d1a7b97b1
- reports/stage_d1d_accounting.json  d00ff04ba381b1e077d859393ee374746aa954db190b12ac06e64c7dc259c968
- reports/stage_d1b_accounting.json  fd9120990606f8e533904299102de157883d9aacf6316906a63fa3009f2b0a5f
- reports/stage_d1_accounting.json  7e50a98e983e164e1f27e698bb892be7cfbf6c0b7cdbf2b42ff3a508f9b32201

Event-value definitions of the 64 statistics (R-5):
- strategy/research/_d1e_event_series.py  51ec1d881cfdd9385f421809c2cdcfa9f8233d18ac5dcddbd92e84c3f8e90645

Pinned inputs of epsilon and of the cost model (E-1, V-4, R-8):
- reports/power_gate.json  e57088247881c184a411344d6b1b696a782987eb92ef3a4328e6b6f39315c40c
- reports/stage_d1e_gate_extension.json  d569e261f0eb9297aa7af2c78fb09b65e113adb6c3f9009b2d6fa94867d06858 (final, 100 rows)
- reports/stage_d1e_power_gate_cells.json  433a3ea6361cffaa9544e56e3952d047d067d1a788df3706eca21e23770f3acb
- sim/slippage_calibration.json  2d680dd2e2d09895cd28d81f258c525092f503688cc6801f28ca0171abbe30b5
- data/cme_calendar.py (2025-2026 entries, which the extended file must keep byte-identical)  5f24edda9504ca7e091c980969d743c05ba0472d8bd613473611d2335971cd54

Load-bearing Stage D.1e artifacts behind section 4 (V-2; the first three were regenerated by the
unit correction of R-1 and hashed now; any regeneration of these files before hashing
re-fills these three lines, NEW-7):
- reports/stage_d1e_members_trials.json  f546e3f325b07267988fccaf30550e04e59e12f4765805073f0e1d505d648e74
- reports/stage_d1e_power.json  29b0e03e16edfd7d1b0fe09ed0e03963d03127e978dd88c79c5160d77ad793ca
- reports/stage_d1e_coverage.md  63e18451e4e5947863be23dd031d87bc23a34b2c932493491d93bb5fac98dc61
- reports/stage_d1e_members_events.json  c6db647fe818faec0f70772a9b241c78f0865999ee83c6d4b9d4a19317bc2df8
- reports/stage_d1e_quotes.json  a796ef7328e94a75dc3bc7d0d9c53a42a034f109002e0a1dfd39de9e57123f8a

## 1. Data and windows

### 1.1 What D.1f buys (nothing else)
MES.v.0 (volume-ranked continuous front), schema ohlcv-1m, dataset GLBX.MDP3, stype_in
continuous, in monthly chunks exactly as data.pull_mes.monthly_chunks produces them, from
the first calendar month in which MES exists (Task 4a: 2019-05, chunk
range=2019-05-01_2019-06-01; MES's symbology interval opens 2019-04-01 but the 2019-04
chunk quotes at 0 billable bytes and is not bought) through the chunk range=2025-03-01_2025-04-01. The last chunk ends at UTC
2025-04-01T00:00, where the existing raw data begins: no overlap, no gap. Every chunk is
quoted, gated and ledgered through data.spend_gate.SpendGate and data.adapter.fetch_range,
with the caps in data/config.py as the user sets them for D.1f. Roll boundaries come from
symbology.resolve (free); vendor-degraded days from metadata.get_dataset_condition
(free). No other schema is bought for the confirmation. Order-book data (C6) is Stage
D.1g's purchase and is not part of this list. The raw symbol of a bar is the symbol symbology maps to its instrument_id ON THE BAR'S
DATE; a bar is dropped only if no MES outright (MES, a month letter and a year digit) maps to
its instrument_id on that date, and every drop is logged. Symbology maps instrument 7849's
2019 interval to 'DNMH929 C35' as well as 'MESM9'; the number of dropped bars per month is
expected to be zero from 2019-05-06 on, and a non-zero count stops the run for a lead
decision before step 5 (D-4, NEW-6).

### 1.2 The second holdout (sealed on arrival, before any read)
- Holdout-2 trade dates: 2024-04-01 through 2025-03-31 inclusive (about 259 calendar trade
  dates before exclusions, about 239 after the roll blackout and vendor-degraded dates; the
  exact counts are recorded at sealing).
- Sealed raw chunks: the 13 monthly chunks range=2024-03-01_2024-04-01 through
  range=2025-03-01_2025-04-01. The first holdout-2 session opens at 17:00 CT on Sunday
  2024-03-31, inside the March 2024 chunk, which is why that chunk is sealed whole.
- Embargo: every March 2024 trade date is in no window:
  they sit in a sealed chunk and are never built into bars.
- The 2025-03-31 22:00 to 24:00 UTC bars (the missing first two hours of the mined trade
  date 2025-04-01) sit in the sealed 2025-03 chunk and stay sealed; the research parquet
  is not rebuilt.
- Mechanism: data/holdout.py's cipher and ceremony, parametrized (a second HoldoutPaths:
  sealed store data/sealed/MES_holdout_v2/, manifest docs/HOLDOUT2_MANIFEST.json, the same
  append-only docs/HOLDOUT_UNLOCK_LOG.md, the same REGISTRATION.md requirement, the same
  acknowledgement phrase with "holdout 2" named in the stage argument). Each holdout-2
  chunk is sealed by the same function call that downloads it, after the adapter's
  record-byte verification (the only decode of a holdout-2 chunk, which yields a byte count
  and nothing else) and before the next chunk is requested; the D.1f pull order is
  oldest-first; the holdout-2 manifest records per chunk only bytes and sha256 (plaintext
  and sealed), no row counts and no dates; the puller refuses to re-buy any chunk listed in
  either manifest (L-1). Unlock headings name the holdout ("UNLOCK holdout 2"); prior
  unlocks are counted per holdout; the ceremony's stage argument must match
  `(stage\s+)?d\.2(\s+holdout\s+2)?` exactly (L-3). Holdout-2 is unreadable in D.1f and
  D.1g; any unlock of either holdout before a registered Stage D.2 voids this list.
  verify_seal must report all_ok for both holdouts at the start and end of every later
  session.
- Why these bounds: (a) adjacency: it is the year immediately before the mined research
  window, so it is the closest available regime to live conditions for a final Stage D.2
  read, and together with the current holdout (2026-06-22 to 2026-09-16) it gives D.2 two
  separated seasons, and no embargo is needed on the mined side because every member is
  intraday-only and the mined window's runs began 2025-04-01 with their warm-up inside that
  window, so no bar and no trailing state crosses the 2025-03-31 boundary in either
  direction, while D.2's read of holdout-2 warms up on the confirmation window's tail, which
  lies before it (L-4); (b) size: about 239 usable days exceeds the binding n_b of every class except C3 (566,
  section 4), whose null power holdout-2 alone cannot reach, and it matches the Stage C
  design of the first holdout in kind (NEW-2); (c) sealing at whole-chunk granularity is
  byte-exact and needs no partial-file logic, which is why the embargo is a calendar
  month rather than five sessions.

### 1.3 The confirmation window
Trade dates from S (the start date the data-quality start rule in docs/NULL_CRITERIA.md
section 4 yields) through 2024-02-29 inclusive, built from the unsealed chunks only, with
trade dates after 2024-02-29 dropped at build time (the 2024-02-29 22:00 to 24:00 UTC bars
belong to trade date 2024-03-01, an embargo date, and are dropped). Exclusions inside the
window are exactly the current pipeline's: the roll blackout (splice trade date plus the
two prior sessions, from symbology), vendor-degraded days handled as now (N-3): trials trade
through them with the flag hidden from the strategy and the day's P&L counted, event
statistics exclude every trade date with any flagged bar, the two differ by design and stay
so, and the degraded-date list is fetched once at step 2, frozen in the run JSON, compared
with the eight dates known at declaration (2020-02-27, 2020-02-28, 2020-05-05, 2020-06-30,
2020-07-01, 2021-12-05, 2022-01-02, 2024-09-18) and any difference logged before step 5, early-close days handled by each
member as its code already handles them.

### 1.4 The mined data
The 289 train-union dates (2025-04-01 to 2026-05-13) and the 139 EDA dates are never
pooled with the confirmation window in any figure that enters a verdict. They are used in
D.1f only for continuity: every trial re-run on the train union must reproduce
reports/stage_d1d_accounting.json to the cent before any confirmation figure is read.

### 1.5 Order of operations in D.1f (mandatory)
1. Harness work (section 5), built and tested on the existing research bars and on synthetic
   bars, before any purchase; H1 to H6 are exercised only on synthetic bars (R-7).
1b. Harness freeze (R-4): D.1f writes reports/stage_d1f_harness_freeze.json listing the sha256
   of every file under screening/, sim/ (including sim/slippage_calibration.json), funnel/
   (including reports/power_gate.json), rules/, data/*.py, strategy/interface.py,
   strategy/research/h_daily_bar/*, strategy/research/_d1f_*.py, the release-table module of
   section 5.7 and every file hashed in section 0, prints it into the STATE file before any
   quote or purchase, and asks the user to commit it (NEW-4). data/config.py's D.1f session
   id and spend caps are set by the user before step 1b and are frozen with it (NEW-5). strategy/research/_d1f_confirmation.py refuses to run if
   any listed hash differs, checks again when step 8 completes, and records the manifest's own
   sha256 in every output JSON. Any change to a listed file after step 1b voids the run; a
   re-run is a new declaration under a new name, and the voided run's results are still
   reported.
2. Quote, gate, download every chunk, oldest first; fetch the dataset condition once and
   freeze it. 3. Seal each holdout-2 chunk as it arrives (section 1.2). 4. Build the
   confirmation parquet from the unsealed chunks; drop trade dates after 2024-02-29.
4b. Calendar validation (D-2): run data.validate.observe_holidays over the confirmation bars
   and require that every weekday with no bars is a listed full closure, that every day whose
   last RTH bar opens before 14:59 CT is a listed early halt whose halt time equals the
   observed last minute plus one, and that every listed 2019-2024 entry is observed. Any
   discrepancy stops the run; the calendar is corrected, re-hashed into the freeze manifest
   and the correction logged, all before step 5. Once step 7 starts the calendar is immutable.
5. Compute S by the start rule (docs/NULL_CRITERIA.md 4.1); log S and every monthly median.
6. Continuity check on the train union (1.4). 7. Run the list. 8. Apply the decision rules.
   Nothing in steps 5 to 8 may be revisited after step 8. Any H module run on the research
   parquet, the train union or any fold before step 7 is logged in the STATE file as a look
   and counts as one screen in N for that member (R-7).

## 2. The frozen list

### 2.1 Tier A: 58 confirmation tests (the Holm family, m = 58)

A1. The 31 trials, parameters frozen at their recorded values (section 0 hashes), run
through screening.screen_candidate on the confirmation window, each trial at its coded
contract quantity (QUANTITY_MICROS = 1 for the 29 fixed-size trials and for C-H4; D-H2 and
RT7 size 1 to 5 micros by their rule), market fills at the calibrated cost model, C-H4 with
the existing trade-through passive fill model, and the canonical engine configuration
otherwise. The trials are never instantiated at any other size (R-1). The factory column is
the expression in the hashed assembly files, verbatim; a trial whose factory takes no
argument has every parameter as a literal in its hashed module (R-2). Class in brackets.

| ID (label in ALL_TRIALS) | Class | Factory (verbatim, hashed assembly files) |
|---|---|---|
| A-H1 european-open overnight drift | C1 | `H1EuropeanOpenOvernightDrift` |
| A-H2 rth close window (buy) | C1 | `lambda: H2RthCloseWindowSessionPosition(direction="buy")` |
| A-H2 rth close window (sell) | C1 | `lambda: H2RthCloseWindowSessionPosition(direction="sell")` |
| A-H3 weekend effect | C1 | `H3WeekendEffect` |
| A-H4 eth leg | C1 | `lambda: H4EthVsRthDecomposition(session="eth")` |
| A-H4 rth leg | C1 | `lambda: H4EthVsRthDecomposition(session="rth")` |
| B-H1 opening-range breakout (hold 5) | C2 | `lambda: H1FrictionAwareOpeningRangeBreakout(hold_minutes=5)` |
| B-H1 opening-range breakout (hold 75) | C2 | `lambda: H1FrictionAwareOpeningRangeBreakout(hold_minutes=75)` |
| B-H2 prior-day stop cascade | C2 | `H2PriorDayStopCascade` |
| B-H3 breakout leg | C2 | `H3BreakoutLeg` |
| B-H3 fade leg | C2 | `H3FadeLeg` |
| B-H4 narrow-range breakout | C2 | `H4NarrowRangeContractionBreakout` |
| RT1 B-H1 ORB 5-min bars (hold 1 bar) | C2 | `lambda: OrbRetest(hold_bars=1, leg="breakout", name="rt1_orb_5min_hold1")` |
| RT2 B-H1 ORB 5-min bars (hold 15 bars) | C2 | `lambda: OrbRetest(hold_bars=15, leg="breakout", name="rt2_orb_5min_hold15")` |
| RT3 B-H3 breakout leg 5-min bars | C2 | `lambda: OrbRetest(hold_bars=6, leg="breakout", name="rt3_orb_5min_breakout_hold6")` |
| RT4 B-H3 fade leg 5-min bars | C2 | `lambda: OrbRetest(hold_bars=6, leg="fade", name="rt4_orb_5min_fade_hold6")` |
| C-H1 magnitude-conditioned reversal | C3 | `H1MagnitudeConditionedReversal` |
| C-H2 post-spike exhaustion fade | C3 | `H2PostSpikeExhaustionFade` |
| C-H3 close-location-value reversal | C3 | `H3CloseLocationValueReversal` |
| RT5 C-H2 spike fade 5-min bars | C3 | `SpikeFadeRetest` |
| D-H1 trailing-vol regime gate | C4 | `H1TrailingVolatilityRegimeGate` |
| D-H2 inverse-vol sizing | C4 | `H2InverseVolatilitySizing` |
| D-H3 range-compression gate | C4 | `H3RangeCompressionGate` |
| D-H4 overnight gap fade | C4 | `H4OvernightGapFade` |
| RT6 D-H1 daily-vol regime gate | C4 | `DailyVolRegimeGateRetest` |
| RT7 D-H2 daily-vol sizing | C4 | `DailyVolSizingRetest` |
| E-H1 scheduled macro drift | C5 | `H1ScheduledMacroDrift` (continuity run); D.1f confirmation factory, verbatim as the 5.7 amendment writes it: `lambda: H1ScheduledMacroDrift(release_table=RELEASE_TABLE_ET | RELEASE_TABLE_2019_2024)` |
| E-H2 post-release momentum | C5 | `H2PostReleaseMomentum` (continuity run); D.1f confirmation factory, verbatim as the 5.7 amendment writes it: `lambda: H2PostReleaseMomentum(release_table=RELEASE_TABLE_ET | RELEASE_TABLE_2019_2024)` |
| E-H3 quarterly witching short | C5 | `H3QuarterlyWitchingShort` |
| E-H4 turn-of-month long | C5 | `H4TurnOfMonthLong` |
| C-H4 passive-fill reversal | C6 (lower bound only; see 3.5) | `H4PassiveFillReversal` |

The continuity run of 1.4 uses the no-argument factories with the default table; the amended
E-H modules must reproduce their train-union figures to the cent under both factories, and
only the confirmation factories above pass the combined table (NEW-1).

A2. The 21 event statistics. Definition: the statistic's declared construction in the
hashed declaration, computed by the hashed module, on the confirmation window's dates in
place of the EDA dates (the only change is the date set; every threshold, bucket grid,
refractory period, baseline length and timeframe is the declared literal, and the thresholds
the declarations define as sample quantities, the F2.4, F5.1 and F5.2 tercile edges, F5.3's
log-range on log-volume regression, G1 and G4's Q80 and the F5.1, G1 and G4 trailing 20-date
baselines, are recomputed on the confirmation window's own dates, pooled over the whole
window, exactly as the hashed code computes them on the EDA dates; they are not frozen at
the EDA values, R-6). Confirmation
direction s = the sign of the recorded implied edge (a negative recorded edge means the
tested trade is the reversal of the predictor's sign, exactly as in the near-miss).
Tested quantity: the per-event net value v = s x e - c, where e is the event value the
declaration averages (for correlation statistics, sign(predictor) x forward move in
ticks, the "economic companion"; for F4.1 and every G statistic, the signed forward move in
ticks the estimate averages; for F4.4, e = the signed forward 15-minute move from the round
level, with NO control-level adjustment: the recorded implied edge -3.3631 is that plain mean
and the control-subtracted estimate -4.5774 is reported descriptively beside it, R-5), the
per-event definitions being exactly those strategy/research/_d1e_event_series.py (section 0)
computes, which the D.1f wrapper of section 5.4 reproduces, and c = 2.11 ticks, the modelled market
round-turn cost at one round turn per day (every one of these is a market-order
construction). c = 2.11 ticks is the modelled market round turn (commission $1.22 plus
two one-side slippages at the mean of the calibrated table). It is charged per event at every
frequency; the funnel's T-dependent round-turn figures (2.111 at T=1 down to 2.064 at T=8)
are segment artefacts of where the funnel's round turns fall in the session, not frequency
discounts. Statistics ignore the time-of-day slippage table; the RTH/ETH difference is about
0.05 ticks per round turn (E-3). F3.3 statistics, whose event is one per day, and F3.2 statistics, one per
day per bucket pair, are treated the same way.

| ID (id in the facts file) | Family / class | Recorded implied edge (ticks, EDA) | s | Recorded n |
|---|---|---|---|---|
| F3_2_bucket07_bucket08 | F / C3 | -7.5597 | -1 | 134 |
| F6_1_overnight_range_position | F / C2 | +6.5797 | +1 | 138 |
| F3_3_opening_30min_to_close_momentum | F / C3 | -6.3358 | -1 | 134 |
| F3_2_bucket08_bucket09 | F / C3 | -6.2239 | -1 | 134 |
| F3_3_overnight_to_close_momentum | F / C3 | -4.9925 | -1 | 134 |
| F4_4_round_number_multiples_of_100 | F / C2 | -3.3631 (plain mean of the round-level leg; the control-subtracted estimate is -4.5774) | -1 | 559 |
| F3_2_bucket01_bucket02 | F / C3 | +4.1739 | +1 | 138 |
| F3_2_bucket10_bucket11 | F / C3 | +3.6940 | +1 | 134 |
| F4_1_rth_open_crossing | F / C2 | -3.4521 | -1 | 261 |
| F3_2_bucket02_bucket03 | F / C3 | +3.0580 | +1 | 138 |
| F3_2_bucket05_bucket06 | F / C3 | +2.9420 | +1 | 138 |
| F3_2_bucket04_bucket05 | F / C3 | +2.5870 | +1 | 138 |
| F3_2_bucket06_bucket07 | F / C3 | -2.4855 | -1 | 138 |
| F3_2_bucket12_bucket13 | F / C3 | +2.3806 | +1 | 134 |
| G2.RTH.30 | G / C2 | +5.1912 | +1 | 319 |
| G1.RTH.5 | G / C3 | +0.8793 | +1 | 1789 |
| G2.ETH.30 | G / C2 | -1.6221 | -1 | 598 |
| G2.ETH.5 | G / C2 | -0.4917 | -1 | 1328 |
| G5.RTH.15 | G / C2 | -4.0155 | -1 | 129 |
| G5.RTH.30 | G / C2 | +4.5161 | +1 | 124 |
| G3.RTH.15 | G / C2 | -10.0797 | -1 | 138 |

A3. Family H: daily-bar constructions for intraday entries (6 tests, class C7). New
strategy modules under strategy/research/h_daily_bar/, written in D.1f to these
specifications, market orders, 2 micros, screened through screen_candidate.

Common mechanics for every H test (H1 to H6):
- Daily bar of a trade date d, built inside the strategy from the 1-minute bars it has
  already seen: O = open of the bar whose CT clock time is 08:30; H = max high and L =
  min low over bars with CT time in [08:30, 15:00); C = close of the bar with CT time
  14:59. A daily bar is COMPLETE only if the 08:30 bar and the 14:59 bar both exist, the
  date has early_halt_ct null, and all its RTH bars carry one instrument_id. Incomplete
  days do not exist for the lookbacks: "the last k daily bars" means the last k complete
  ones. Range = H - L in ticks (0.25 points).
- Conditioning for day d uses only complete daily bars of trade dates strictly before d.
  Lookbacks count complete bars: k = 4 (H1), 7 (H2), 2 (H3), 61 (H4, H5: d-1 plus the 60
  complete bars before it, over which the percentiles are taken, excluding d-1), 1 (H6).
  Until the lookback is full, no trade (warm-up comes from the confirmation window's own
  start). A bar's CT clock time is the America/Chicago wall-clock minute of its ts_event, its
  open; "the 08:30 bar" has ts_event at 08:30:00 CT (H-8).
- Instrument guard (H-1): every daily bar that enters day d's condition (d-1 for H1, H2, H4,
  H5 and H6; d-1 and d-2 for H3) must carry the instrument_id of day d's 08:30 bar; otherwise
  no trade on day d. The earlier ranges of H1 (d-2 to d-4) and H2 (d-2 to d-7) are basis-free
  and exempt, as are the trailing 60 ranges of H4 and H5 (NEW-9). The splice
  falls inside the splice trade date's ETH, so that date's daily bar is complete; this guard
  is what removes the first post-splice day for H3, which the roll blackout does not.
- Opening range (OR): OR_high = max high and OR_low = min low over the 1-minute bars of
  day d with CT time in [08:30, 09:00). Requires the 08:30 bar and at least 25 of the 30
  bars; otherwise no trade.
- Breakout entry (H1 to H4): on the first 1-minute bar with CT time in [09:00, 14:30)
  whose close > OR_high, emit market_intent BUY 2 micros; whose close < OR_low, emit
  market_intent SELL 2 micros. The engine fills at the next bar's open. One entry per
  trade date, the first side breached. Fade entry (H5): the same triggers, opposite side.
  Open entry (H6): market_intent on the 08:30 bar (fills at the 08:31 open).
- Exit for every H test: a market_intent to flatten emitted on the first bar the strategy
  sees with CT time >= 14:58 and before the engine's no-new-positions time (fills at the next
  open); if no such bar exists, the engine's forced flatten applies and the day is counted and
  logged as a forced exit (H-3). No stop, no target. Days with early_halt_ct set: no trade.
- Parameters, all fixed here: OR = 30 minutes (the OR30 of B-H3's declaration and the six
  five-minute bars of RT1 to RT4, not a figure read off any result, H-9); latest entry 14:29;
  exit 14:58; 2 micros (which pay the size-5 bucket of the slippage table, the smallest
  calibrated size at or above 2, R-8); lookbacks 4, 7, 2, 61, 61, 1; tercile cuts
  np.percentile(ranges, q, method="linear") with q = 33.33 and 66.67 exactly, over the 60
  complete ranges before d-1 (H-7); CLV cuts 0.2 and 0.8; inequalities exactly as the table
  writes them: strict for H1, H2, H3 and the breakout triggers, non-strict for H4, H5 and
  H6's CLV cuts (H-6). The six factories registered for D.1f take no arguments; every constant
  is a module-level literal, and the test-only warm-up override is a private constructor
  argument with the production default, read from no configuration and unused by the
  factory (H-4).

| ID | Condition on day d (all quantities from complete prior daily bars) | Entry |
|---|---|---|
| H1 NR4 opening-range breakout | Range[d-1] is strictly smaller than each of Range[d-2], Range[d-3], Range[d-4] | breakout |
| H2 NR7 opening-range breakout | Range[d-1] strictly smaller than each of Range[d-2] to Range[d-7] | breakout |
| H3 inside-day opening-range breakout | H[d-1] < H[d-2] and L[d-1] > L[d-2] | breakout |
| H4 bottom-tercile prior range, breakout | Range[d-1] <= P33.33 of Range over the 60 complete bars before d-1 | breakout |
| H5 top-tercile prior range, opening-range fade | Range[d-1] >= P66.67 of Range over the 60 complete bars before d-1 | fade |
| H6 prior-close location follow-through | CLV = (C[d-1] - L[d-1]) / (H[d-1] - L[d-1]); Range[d-1] > 0; CLV >= 0.8 buys, CLV <= 0.2 sells, otherwise no trade | open |

Look-ahead check for each H test (all six, before any confirmation run):
1. Prior-day dependence: a unit test replaces every bar of day d by a scaled copy (prices
   x 1.01, volume x 2) and asserts that day d's condition value is unchanged; and it
   replaces day d-1's bars and asserts the condition changes as computed by hand.
2. Timing: the OR uses bars with CT time <= 08:59 only; the trigger reads a bar's close
   and the order fills at the next bar's open, which the engine enforces and the leakage
   canaries verify (tests/test_leakage_canaries.py must pass after the module is added).
3. Hand-built known answers: a synthetic 8-day series with one NR4 day, one NR7 day, one
   inside day, a bottom-tercile and a top-tercile day (61-bar warm-up shortened to 7 in
   the test through the private constructor argument of the parameters paragraph), and CLV
   0.9 / 0.1 days, each producing exactly the specified trade to the cent.
Sources: Crabel (narrow-range and inside-day conditioning of opening-range breakouts) as
carried in D.1's family B and D notes; no parameter is taken from any result seen in
this program.

### 2.2 Tier B: 43 null-side coverage statistics (no edge claim possible)
Every directional Family F and G statistic not in Tier A, recomputed by the same hashed
code on the confirmation window with the same net construction (s = sign of its recorded
implied edge; c = 2.11): F1_1 at h in {1,5,15,30,60} for RTH and ETH (10);
F2_4_15min_vol_tercile_bottom, F2_4_15min_vol_tercile_top (2); F3_2_bucket03_bucket04,
F3_2_bucket09_bucket10, F3_2_bucket11_bucket12 (3); F4_2_prior_rth_close_crossing (1);
F4_4_round_number_multiples_of_50 (1); F5_1_relvol_tercile_bottom, F5_1_relvol_tercile_top,
F5_2_efficiency_tercile_bottom, F5_2_efficiency_tercile_top, F5_3_range_volume_residual
(5); and the 21 G statistics not in Tier A (G1.ETH.5, G2.RTH.5, G3.RTH.5, G4.RTH.5,
G5.RTH.5, G1.ETH.15, G2.ETH.15, G1.RTH.15, G2.RTH.15, G4.RTH.15, G1.ETH.30, G1.RTH.30,
G3.RTH.30, G4.RTH.30, G1.ETH.60, G2.ETH.60, G1.RTH.60, G2.RTH.60, G3.RTH.60, G4.RTH.60,
G5.RTH.60). Class: F1_1 and F2_4, F3_2, F5 and G1, G4 in C3 or C4 as section 2.3 lists;
F4_2, F4_4x50, G2, G3, G5 in C2.
Tier B members enter the class null (each needs UCB below epsilon with 80% achieved null
power) and never an edge claim: they were not near-misses, and promoting one after seeing
the confirmation window would be selection. A Tier B statistic is reported as an
anomaly only if it is BH-significant (one-sided, in direction s) at 10% within Tier B with
net edge >= +2.11 ticks per event in direction s; a significant negative value is reported
as a sign reversal versus the mined window, not as an anomaly. Any future test of an anomaly
runs on forward data (Stage E) or on a new purchase outside both holdouts, the confirmation
window and the mined window, under a new declaration, and adds to N; it is not a D.1f
finding (M-2).

Non-directional facts (F1_2 variance ratios, F2_1, F2_2, F2_3, F4_3 gap-fill rates, G0)
are recomputed and reported descriptively. They are evidence about the data, not members:
a variance ratio has no side.

### 2.3 Class membership (the coverage map, restated so this file stands alone)
- C1 session clock: A-H1, A-H2 (buy), A-H2 (sell), A-H3, A-H4 eth, A-H4 rth.
- C2 reference levels and breakouts: B-H1 (5), B-H1 (75), B-H2, B-H3 breakout, B-H3 fade,
  B-H4, RT1, RT2, RT3, RT4; F6_1, F4_4x100, F4_1, G2.RTH.30, G2.ETH.30, G2.ETH.5, G5.RTH.15,
  G5.RTH.30, G3.RTH.15; Tier B: F4_2, F4_4x50, G2.RTH.5, G3.RTH.5, G5.RTH.5, G2.ETH.15,
  G2.RTH.15, G3.RTH.30, G2.ETH.60, G2.RTH.60, G3.RTH.60, G5.RTH.60.
- C3 short-horizon reversal and momentum at market fills: C-H1, C-H2, C-H3, RT5; the nine
  F3_2 Tier A buckets, F3_3 (a) and (b), G1.RTH.5; Tier B: F1_1 x10, F3_2_bucket03_bucket04,
  F3_2_bucket09_bucket10, F3_2_bucket11_bucket12, G1.ETH.5, G4.RTH.5, G1.ETH.15, G1.RTH.15,
  G4.RTH.15, G1.ETH.30, G1.RTH.30, G4.RTH.30, G1.ETH.60, G1.RTH.60, G4.RTH.60.
- C4 volatility-state conditioning: D-H1, D-H2, D-H3, D-H4, RT6, RT7; Tier B: F2_4 (2),
  F5_1 (2), F5_2 (2), F5_3.
- C5 calendar and scheduled events: E-H1, E-H2, E-H3, E-H4.
- C6 passive execution: C-H4 (Tier A gives only the trade-through lower bound; the class
  verdict is Stage D.1g's, section 3.5).
- C7 daily-bar constructions: H1 to H6.
Out of scope, so the verdict never speaks for them: multi-day holding (excluded by the
venue, D.1c), instruments other than MES and every cross-asset effect (user decision),
order-flow signals needing book data beyond C6's fill model, any sizing other than the
2-micro headline (NULL_CRITERIA.md section 2).

## 3. Tests and decision rules (fixed now)

### 3.1 The edge statistic and its uncertainty, per member
Unit: net ticks per micro per day. For a trial (R-1): d_t = the sum over the round trips
that close on trade date t of trip_pnl_usd / (1.25 x trip_micros), where trip_micros is the
maximum absolute position in micros held during that trip, recorded by the runner's
additive field ScreeningReport.trip_micros (Stage D.1e), and the sum runs over every window
date, 0 on dates without a closed trip, roll-blackout dates included. This is exact at each
member's coded size: q = 1 for the 29 fixed-size trials and C-H4, q = 2 for H1 to H6, and
the per-trip q in 1..5 for D-H2 and RT7; no member is instantiated at another size. Scaling a
1-micro P&L to the 2-micro bar assumes per-micro costs do not rise with size; the size-5
slippage bucket a 2-micro order pays is slightly higher, so the assumption overstates the
2-micro edge, which is conservative for a null claim and not for an edge claim. For a
statistic: d_t = the sum over that date's events of v (section 2.1 A2), 0 on dates without
events, over the statistic's own post-exclusion date set (the two denominators differ and
are not harmonised after the run, N-4). theta_hat = mean(d_t). Uncertainty (R-9):
stationary block bootstrap of the daily series through
funnel.null_generator.stationary_bootstrap_indices(rng, n, n, 5.0) as
screening.drift.bootstrap_mean_lower_bounds uses it, mean block 5 days, B = 10,000
resamples, a fresh np.random.default_rng(20260921) per member; UCB95 =
np.quantile(means, 0.95) (default linear method); SE_boot = the standard deviation of the
resampled means; one-sided p for H0: theta <= 0 is (1 + #{theta* - theta_hat >= theta_hat})
/ (B + 1). Per-trade translation, reported alongside and used for nothing else: theta_hat /
r and UCB95 / r, with r = ScreeningReport.trades_per_day on the confirmation window for a
trial (closed round trips over all window dates) and events over the statistic's own
post-exclusion date count for a statistic (E-5).

### 3.2 "Edge exists" (a member passes confirmation)
All of: (i) Holm step-down over the 58 one-sided Tier A p-values at family-wise 5%
rejects the member; (ii) the member's composite screening verdict on the confirmation
window is "pass" (robust zero-edge gate on measured p/R/T and both drift sub-checks; for a
statistic, the gate call on its event series with p = the share of events with v > 0 (ties
count for neither side), R = the mean of the positive v over the mean of |negative v|, T =
screening.trips.nearest_segments_per_day(events per window day) on the grid {1, 2, 4},
standard path, robust, exactly as screening.runner._gate does for trips (R-10), and the
drift sub-checks applied to its event series as screening/drift.py applies them to trips:
an event's drift charge
is s x the window-mean price change over the event's own forward clock interval, the
exposure-matched charge with the forward window as the holding interval, so a statistic
is charged exactly what an unconditional position over the same minutes would have
earned on average); (iii) the cumulative
multiple-comparisons accounting carried forward from N = 31: N after D.1f is 58 (31 + 6
Family H + 21 statistics tested for edge for the first time), computed as follows (M-1):
DSR = funnel.multiple_comparisons.deflated_sharpe_ratio(sharpe_m, n_days, 58, the population
variance of the 58 Tier A members' confirmation-window daily Sharpes, skew_m, kurt_m) with
moments from strategy.research._d1b_accounting._moments on the member's d_t, must exceed
0.95; t = harvey_liu_zhu_verdict(mean, population sd, n_days) on d_t, one-sided, must exceed
3.0; PBO = probability_of_backtest_overfitting over the 58 Tier A daily series on 8
contiguous equal blocks of n_days // 8 dates, must be below 0.5. Reported alongside, not
criteria: the same three at N = 101 (58 plus the 43 Tier B members) and at N = 186 (plus the
85 EDA statistics), as the D.1b and D.1d entries did. A member meeting (i) to (iii) goes to the user as a Stage D.2
discussion item. It is not registered and REGISTRATION.md is not written by D.1f.

### 3.3 "Null" for a class
Every member of the class in Tier A and Tier B satisfies both: UCB95 < epsilon_day, and
achieved null power >= 80%, where achieved null power = Phi(epsilon_day / SE_boot - 1.645),
which is the probability that a member with true edge 0 and this SE shows UCB95 below
epsilon_day (equivalently SE_boot <= epsilon_day / 2.4865). The power uses SE_boot and the
normal quantile while UCB95 is a percentile; both are used as written and are not
reconciled after the run (N-5). A member with SE_boot = 0 does not meet this condition (see
3.4). A member that meets both conditions with fewer than 30 closed round trips or events
on the window is marked "null by inactivity" (E-2; the criteria's section 7 says what the
class statement must then carry). epsilon_day is the class
threshold in net ticks per micro per day from docs/NULL_CRITERIA.md section 2:
34 net ticks per micro per day ($85.00 per day at 2 micros; docs/NULL_CRITERIA.md section 2.2).

### 3.4 "Inconclusive"
Any member meeting neither 3.2 nor both conditions of 3.3 is inconclusive, and an
inconclusive member keeps its whole class out of the null verdict. Nothing is rounded;
no member is dropped, re-parametrized or moved between tiers after the run. A member with
zero closed round trips or zero events on the confirmation window, or with SE_boot = 0
(for example an H test whose condition never fires in the window), is inconclusive (no
evidence), not null, and its class is out of the null verdict (N-2).

### 3.5 C6 (passive execution), inherited unchanged by Stage D.1g
- C-H4 in Tier A uses the trade-through fill model, which is pessimistic by
  construction (docs/SCREENING.md). Its Tier A result can therefore establish "edge
  exists" (a pass under the pessimistic model is a pass) but cannot establish the C6
  null. A C-H4 UCB95 below epsilon under the trade-through model is recorded as "null
  under the pessimistic fill model" and the class stays inconclusive until D.1g.
- D.1g's fill model: a queue-position simulation from MBO data, specified and hashed in
  D.1g BEFORE the MBO purchase; any parameter it needs from book data is estimated on days
  declared in advance and outside the N_C6 evaluation dates, never on them (C-2); the same
  runner, C-H4 at its coded 1 micro (R-1), and the passive cost bar of 0.98 ticks per round
  turn (commission only) for gross reporting.
- D.1g's data: full trade-date MBO (17:00 CT to 16:00 CT, because C-H4 rests orders in
  every session and RTH-only books could not fill its ETH orders, C-1) for N_C6 days chosen
  by a rule declared here: the N_C6 trade dates are the LAST N_C6 confirmation-window dates
  on or before 2024-02-29 that are not roll-blackout or vendor-degraded dates (no selection
  by outcome), where N_C6 = the days C-H4 needs for 80% null power at epsilon per Task 3 (181 days: C-H4's chosen n_b at epsilon = 34 at the per-micro unit, reports/stage_d1e_power.json), and never a
  date inside either holdout.
- D.1g's decision rules: 3.1 to 3.4 verbatim, with C-H4 as the single Tier A member of
  C6 and Holm family m = 1. The queue-model C-H4 is a new execution hypothesis: D.1g's DSR
  uses N = 59. Its dates were already read by D.1f's trade-through run of the same signal, so
  the D.1g result is out of sample only in the fill model, and any C6 edge claim says so
  (M-3).

### 3.6 Regime slices
Every member's theta_hat and UCB95 are also reported per calendar year of the
confirmation window, descriptively. No slice is chosen, dropped, weighted or used in any
verdict. No market-regime exclusion of any kind is applied (2020 included for every trial; for the
statistics the vendor flag removes five 2020 dates, 2020-02-27, 02-28, 05-05, 06-30 and
07-01, by the rule of 1.3, D-5). Anything learned from a slice can seed only a new
declaration under a new name, counted in N and tested on data outside the confirmation
window, the mined window and both holdouts (M-4).

## 4. Power at epsilon (Task 3, filled before hashing)
Computed in Stage D.1e from the existing train-window series (reports/stage_d1e_power.json,
verified in reports/stage_d1e_power_verification.md); unit net ticks per micro per day; n_b = days
for 80% null power at epsilon, n_a = days for 80% detection power at Holm's most stringent step
(alpha = 0.05/58); chosen = analytic unless the block-bootstrap simulation differed by more than
15%, then the larger of the two. Days supplied = confirmation window S..2024-02-29 after the roll
blackout and vendor-degraded dates, calendar estimate +/-3%, for the start dates the rule could
yield; S is computed in D.1f by NULL_CRITERIA.md section 4.1.

| Class | Binding member for null power | n_b analytic / simulated / chosen | Binding member for detection | n_a chosen | Days supplied at S = 2019-05-06, 2019-07-01, 2020-01-02, 2021-01-04, 2022-01-03, 2023-01-03 | Null power at epsilon reachable |
|---|---|---|---|---|---|---|
| C1 | A-H4 rth leg | 149 / 161 / 149 | A-H4 rth leg | 379 | 1151, 1114, 992, 755, 516, 277 | all S |
| C2 | G3.RTH.5 | 193 / 182 / 193 | G3.RTH.5 | 492 | 1151, 1114, 992, 755, 516, 277 | all S |
| C3 | F1_1_h1_RTH | 566 / 571 / 566 | F1_1_h1_RTH | 1447 | 1151, 1114, 992, 755, 516, 277 | S <= 2021-01-04 |
| C4 | F2_4_15min_vol_tercile_top | 171 / 152 / 171 | F2_4_15min_vol_tercile_top | 436 | 1151, 1114, 992, 755, 516, 277 | all S |
| C5 | E-H1 scheduled macro drift | 16 / 10 / 16 | E-H1 scheduled macro drift | 41 | 1151, 1114, 992, 755, 516, 277 | all S |
| C6 | C-H4 passive-fill reversal | 181 / 174 / 181 | C-H4 passive-fill reversal | 461 | 1151, 1114, 992, 755, 516, 277 | all S |
| C7 | H6 prior-close location follow-through (projected) | 114 / censored / 114 | H6 prior-close location follow-through | 290 | 1151, 1114, 992, 755, 516, 277 | all S |

Supplied days: S = 2019-05-06: 1151, S = 2019-07-01: 1114, S = 2020-01-02: 992, S = 2021-01-04: 755, S = 2022-01-03: 516, S = 2023-01-03: 277. Holdout-2 (2024-04-01..2025-03-31): about 239 trade dates.
Achieved null power is measured in D.1f for every member from its own confirmation series; the
table is the plan, not the criterion. Family H rows are projections from the coverage map's proxies.
Descriptive resolution (not a criterion): the smallest per-trade edge the data could rule out at
80% null power with the full extension is C1 2.45 to 23.62 (A-H3 weekend effect); C2 0.30 to 14.00 (G3.RTH.5); C3 0.02 to 5.22 (G4.RTH.60); C4 0.46 to 3.27 (D-H4 overnight gap fade); C5 1.96 to 37.26 (E-H1 scheduled macro drift); C6 0.15 to 0.15 (C-H4 passive-fill reversal); C7 26.65 to 40.88 (H2 NR7 opening-range breakout) ticks per trade at S = 2019-05-06.

## 5. Harness work D.1f does before any purchase (so the new data cannot shape it)
1. screening.runner: a ConfirmationWindow object accepted by screen_candidate, loading the
   confirmation parquet through a loader with the same refusal semantics as
   data.research_bars (holdout-1 and holdout-2 dates refused always, mined dates refused for
   confirmation runs); its own splice dates, drift path and session benchmark recomputed on
   the confirmation bars; the research-slice refusal in funnel.null_generator replaced by
   that same refusal (R-3). The train-union path stays as is for continuity runs. Leakage
   canaries re-run.
2. data/holdout.py: sealing and verification for holdout-2 through a second HoldoutPaths,
   new logic where the current functions assume holdout-1 (L-2). Its tests must assert: (i)
   after sealing, no plaintext of any of the 13 chunks exists under the repo, in /tmp or in
   the vendor client's cache; (ii) the manifest lists 13 raw records with sha256 of the
   plaintext and of the sealed blob; (iii) verify_seal on the holdout-2 paths reports all_ok
   with plaintext absent for all 13; (iv) the confirmation loader asserts max(trade_date) <=
   2024-02-29 and refuses trade dates in 2024-03-01..2025-03-31 and >= 2025-04-01 on the
   confirmation path; (v) `python -m data.holdout status` reports both holdouts at the start
   and end of every later session. The existing manifest untouched.
3. data/cme_calendar.py: holidays and early closes for 2019 through 2024 from CME's
   published schedules, each entry citing its source verbatim; CALENDAR_COVERAGE extended to
   2019-01-01 and asserted by the bar builder for every built date; the 2025-2026 entries
   byte-identical to the hashed file of section 0; validated against the confirmation bars
   at step 4b and immutable from step 7 (D-2); the flatten-time logic unchanged.
4. The F and G statistics: the two hashed modules are NOT edited (R-3). A new module,
   strategy/research/_d1f_statistics.py, calls their builders with the confirmation date set
   exactly as strategy/research/_d1e_event_series.py calls them with the EDA dates; a test
   asserts that the wrapper on the 139 EDA dates reproduces every recorded estimate, n and
   implied edge to 1e-9 (the Task 1c check) and every per-event value of the hashed
   _d1e_event_series.py.
5. strategy/research/h_daily_bar/: the six H modules with the look-ahead tests of 2.1 A3,
   exercised on synthetic bars only before step 7 (R-7).
6. strategy/research/_d1f_confirmation.py: runs the whole list, writes one JSON per tier,
   computes 3.1 to 3.4, and refuses to run if any hash in section 0, in the harness-freeze
   manifest, or of this file or of docs/NULL_CRITERIA.md has changed.
7. The release table for E-H1 and E-H2 (N-1): before the purchase, a hashed module
   strategy/research/e_calendar_event/_release_table_2019_2024.py with the scheduled FOMC
   statement dates and 2:00pm ET times from the Federal Reserve's historical FOMC calendars
   and the CPI and Employment Situation release dates and 8:30am ET times from the BLS
   schedule archives, for 2019-05-01..2024-02-29, using the published date where a release
   moved, excluding unscheduled FOMC actions (the hashed module's own "regularly scheduled"
   convention), each entry citing its source. The two strategy modules read a module-level
   table with no constructor hook, so they are amended to accept a table argument whose
   default is the existing table, re-hashed in a declared amendment recorded in the STATE
   file before the purchase, with a test that the amended modules reproduce their
   train-union figures to the cent; the D.1f factories for E-H1 and E-H2 pass the combined
   table. Nothing else in the two modules changes.
8. Files D.1f MAY change, and only these (R-3): screening/runner.py, screening/drift.py,
   funnel/null_generator.py (the refusal only), data/pull_mes.py, data/build_mes_bars.py,
   data/bars.py, data/validate.py, data/holdout.py, data/cme_calendar.py,
   data/research_bars.py, the two E-H modules as in item 7, and the new modules
   h_daily_bar/*, _d1f_statistics.py, _d1f_confirmation.py and _release_table_2019_2024.py.
   Every other file under screening/, sim/, funnel/, rules/, data/ and strategy/ is
   byte-identical to the harness-freeze manifest of step 1b.
All of this is opus xhigh work under CLAUDE.md's routing because it touches screening/
and data/holdout; its tests are written before the purchase.

## 6. Hashing procedure and record (V-1)
Order: (1) this file is finalised and hashed first; this section records only the UTC time
and the chmod, because a file cannot hold its own hash. (2) docs/NULL_CRITERIA.md section 1
embeds this file's sha256 and is hashed second. (3) Both hashes are written to
reports/stage_d1e_declaration_hashes.json, which strategy/research/_d1f_confirmation.py
checks, and to the Stage D.1e progress entry. (4) The lead asks the user to commit the three
files; the commit hash is the anchor and the chmod is a convenience.
Hashed 2026-09-22T08:50:46Z; chmod 444 applied at the same time. STATUS line at the top of this file: FROZEN.
