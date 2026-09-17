# MES 1-minute bar validation — Stage A.1, Task 3

**Date:** 2026-09-16 · **Series:** Databento GLBX.MDP3 `MES.v.0` ohlcv-1m, unadjusted
**Window:** 2025-04-01 00:00 UTC → 2026-09-16 00:00 UTC (first bar Mon 2025-03-31 19:00 CT, last bar Tue 2026-09-15 18:59 CT)
**Reproduce:** `uv run python -m data.build_mes_bars` and `uv run python -m data.tick_crosscheck`
**Machine-readable results:** `reports/bar_validation_summary.json`, `reports/tick_crosscheck_summary.json`
**Output series (as validated, 2026-09-16):** `data/processed/MES/ohlcv-1m_MES_v_0_2025-04-01_2026-09-16.parquet` (517,197 bars, flag columns documented in `data/bars.py`). **That file no longer exists.** The Stage C Task 6 seal migration split it into the research slice `data/processed/MES/ohlcv-1m_MES_v_0_2025-04-01_2026-06-19_research.parquet` (431,999 bars, read-only — the name `data/research_bars.py` hardcodes) plus the encrypted holdout under `data/sealed/`. Rebuilding the full-window file is refused by `data/build_mes_bars.py` by design. Everything below describes the full 517,197-bar series as it was validated.

## Verdict

**Passed. No hard integrity failures.** Two issues were found and handled:

- **Calendar error.** Validation found an error in the new holiday calendar. It was corrected and the bars rebuilt (see §3).
- **Real gaps.** The data has 19 gaps totalling 663 minutes. Every gap is flagged on the bars and none is filled (see §2).

The tick cross-check matches exactly at a stated 0-tick, 0-contract tolerance (see §5).

## 1. Integrity checks

| Check | Result |
|---|---|
| Timestamps strictly increasing (`ts_event`, bar open) | **Pass.** 0 non-increasing steps in 517,197 bars |
| Duplicate bars by timestamp | **Pass.** 0 |
| Volume non-negative | **Pass.** 0 negative. The DBN field is unsigned; checked anyway after conversion. There are also 0 zero-volume bars |
| Prices on the 0.25 tick grid | **Pass.** 0 off-grid |
| High ≥ max(open, close), low ≤ min(open, close) | **Pass.** 0 inconsistent |
| Bars inside scheduled closures (halt, weekend, holidays) | **Pass.** 0 after the calendar fix. There were 1,140 before it (§3) |
| Roll splices match vendor symbology | **Pass.** 5 of 5 splices sit exactly on the resolved boundary, with 0 unexplained instrument changes |
| Quarterly cycle H→M→U→Z | **Pass.** MESM5→U5→Z5→H6→M6→U6 |

**Ordering clock.** Bars have no `ts_recv`, so they are ordered on `ts_event`. The ported `ts_recv` monotonicity check was run on the tick data instead:

- **Trades files:** 815,763 records, 0 regressions.
- **mbp-10 files:** 25,639,061 records, 0 regressions (checked during the Task 4 calibration).

## 2. Gaps: flagged, never filled

**How expected minutes are defined.** An expected minute is any minute whose start falls outside the session calendar's closed windows. Those windows are the daily 16:00–17:00 CT halt, the Friday 16:00 → Sunday 17:00 CT weekend, and the holiday calendar.

**Coverage.** There were 517,860 expected minutes and 517,197 had a bar. That leaves **663 missing minutes, in 19 runs**. Every bar that follows a gap carries `gap_before_minutes > 0` (19 bars). No row was synthesized.

**Where the gaps are:**
- **RTH (08:30–15:00 CT):** 0 missing minutes.
- **Single missing minutes:** 18, all in ETH. These are overnight minutes with no trade. OHLCV bars exist only when a trade prints.
  - 2025: 04-02 15:39, 07-13 23:36, 07-28 00:15, 08-26 23:44, 09-14 23:05, 09-14 23:56, 09-15 20:21, 09-16 18:13, 09-16 18:36, 09-16 23:52, 09-24 23:36, 10-01 21:53, 10-02 23:40, 12-24 01:51, 12-24 01:55, 12-30 00:45
  - 2026: 09-15 18:33, 09-15 18:36
- **One 645-minute gap:** Thu 2025-11-27 20:45 CT → Fri 2025-11-28 07:30 CT. This was an **exchange outage, not a data defect**: CME Globex halted after a cooling failure at a CyrusOne data center, as reported by CNBC and Bloomberg on 2025-11-28. Databento also marks 2025-11-28 as degraded. It is left as a flagged gap. It is deliberately not added to the holiday calendar, because it was unscheduled.

**Databento "degraded" days.** Databento marks 10 dates in the window as degraded:
- 2025: 09-17, 09-24, 11-28
- 2026: 01-31, 03-15, 03-16, 03-21, 04-10, 05-24, 08-29

The source is the free `metadata.get_dataset_condition` call, cached at `data/vendor/databento/condition/`. Bars on those UTC dates carry `vendor_degraded_day = True` (6,089 bars). Of the 663 missing minutes, 646 fall on degraded dates: the outage plus one minute. The others show no bar-level defect, but Stage C should treat them as lower-trust.

## 3. Session calendar: halt window, flatten boundary, holidays

**Daily halt.** The ported calendar encodes 16:00–17:00 CT, which matches the figure in prior research. The bars confirm it:
- No bar starts inside 16:00–16:59 CT on any day.
- 363 sessions print a 15:59 CT bar and 378 print a 17:00 CT bar.

**Flatten boundary.** This comes from `rules/xfa_rules.py`, the same function the rules engine uses:
- **`in_flatten_window`** (18,374 bars): the bar starts at or after 15:10 CT and before the 17:00 CT reopen. On a CME early-close day the flatten is 15 minutes before the early close.
- **`in_no_new_positions_window`** (19,130 bars): the bar starts at or after 15:08 CT.
- **Last tradeable bar:** the 15:09 CT bar covers [15:09, 15:10).

**Holidays, checked against the bars.** Each calendar entry inside the window was compared with the last traded minute before the closure and the first after it:

| CT date | Holiday | Calendar | Last bar before | First bar after | Result |
|---|---|---|---|---|---|
| 2025-04-18 | Good Friday | full closure | Thu 15:59 | Sun 04-20 17:00 | ✔ |
| 2025-05-26 | Memorial Day | halt 12:00 | 11:59 | 17:00 | ✔ |
| 2025-06-19 | Juneteenth | halt 12:00 | 11:59 | 17:00 | ✔ |
| 2025-07-03 | Day before July 4 | close 12:15 | 12:14 | Thu 17:00 | ✔ |
| 2025-07-04 | Independence Day | halt 12:00 (**corrected**) | Fri 11:59 | Sun 07-06 17:00 | ✔ after fix |
| 2025-09-01 | Labor Day | halt 12:00 | 11:59 | 17:00 | ✔ |
| 2025-11-27 | Thanksgiving | halt 12:00 | 11:59 | 17:00 | ✔ |
| 2025-11-28 | Day after Thanksgiving | close 12:15 | 12:14 | Sun 11-30 17:00 | ✔ |
| 2025-12-24 | Christmas Eve | close 12:15 | 12:14 | Thu 12-25 17:00 | ✔ |
| 2025-12-25 | Christmas | full closure | Wed 12:14 | Thu 17:00 | ✔ |
| 2026-01-01 | New Year's Day | full closure | Wed 12-31 15:59 | Thu 17:00 | ✔ |
| 2026-01-19 | MLK Day | halt 12:00 | 11:59 | 17:00 | ✔ |
| 2026-02-16 | Presidents Day | halt 12:00 | 11:59 | 17:00 | ✔ |
| 2026-04-03 | Good Friday (jobs report) | halt 08:15 | 08:14 | Sun 04-05 17:00 | ✔ |
| 2026-05-25 | Memorial Day | halt 12:00 | 11:59 | 17:00 | ✔ |
| 2026-06-19 | Juneteenth (Fri) | halt 12:00 | 11:59 | Sun 06-21 17:00 | ✔ |
| 2026-07-03 | July 4 observed (Fri) | halt 12:00 | 11:59 | Sun 07-05 17:00 | ✔ |
| 2026-09-07 | Labor Day | halt 12:00 | 11:59 | 17:00 | ✔ |

**Calendar error found and fixed: 2025-07-04.** CME publishes "no settlement" for that date, and the research first read that as a full closure. The bars show 1,140 minutes of trading from Thu 17:00 CT to Fri 11:59 CT. So the day was an early 12:00 CT halt with the trade date combined, like other Monday–Friday holidays. The calendar entry is corrected, and a regression test pins it (`tests/test_session_calendar.py`).

**Conflict resolved by the data: Good Friday 2026.** CME's clearing advisory confirms an abbreviated equity session but gives no close time. Secondary sources disagreed (08:15 CT per AMP, about 09:15 per another). The bars show the last trade in the 08:14 minute and nothing again until Sunday, so 08:15 CT is right.

**Could not be checked against data** (outside the window):
- 2025-01-01, 2025-01-09 (Day of Mourning, 08:30 CT per a CME press release), 2025-01-20, 2025-02-17.
- 2026-11-26, 2026-11-27, 2026-12-24, 2026-12-25.
- For these, the halt times rest on CME-direct status plus secondary or inferred clock times. Each entry's evidence grade is recorded in `data/cme_calendar.py`.

**Source limitation.** cmegroup.com blocks automated fetches, so CME documents were read through Wayback Machine copies.

## 4. Continuous contract and rolls

**Roll rule.** The series uses `MES.v.0` (volume-ranked front) rather than `MES.c.0`. Databento's calendar rule rolls only after expiration. The splice boundaries were resolved for free from vendor symbology:

| Rule | 2025-Q2 | 2025-Q3 | 2025-Q4 | 2026-Q1 | 2026-Q2 |
|---|---|---|---|---|---|
| `.v.0` (used) | 06-18 | 09-17 | 12-17 | 03-18 | 06-17 |
| `.c.0` | 06-22 | 09-21 | 12-21 | 03-22 | 06-19 |

**Finding for Stage C: `.v.0` still rolls about two sessions late.** Volume moves to the next contract before the vendor splice, so the series stays on the thinning expiring contract for those sessions. For example, MESM6 traded 2.29M, 1.93M, 2.17M and 1.49M contracts on 06-09 to 06-12, then 433k on 06-15 and 340k on 06-16. The splice came on 06-17. Every quarter follows the same pattern (`roll_volume_context` in the JSON).

**Unadjusted prices and midnight splices.** Prices are not back-adjusted. Splices fall at 00:00 UTC, which is 18:00/19:00 CT, in the middle of the overnight session. `is_roll_session` flags every bar of each affected trade date (6,897 bars).

**Stage C decision.** Stage C should exclude the low-volume pre-splice sessions, or define an explicit liquidity roll. That is a decision for Stage C, not something invented here.

## 5. Tick-to-bar cross-check (read in place from MLCryptoEngine)

**Files.** The check used `MLCryptoEngine/data/vendor/databento/GLBX.MDP3/date={2026-07-15,2026-07-31}/MES_c_0.trades.dbn.zst`, read-only and not copied. Both dates are inside the pulled window.

**Stated tolerance:**
- **OHLC:** exactly equal, 0 ticks.
- **Volume:** exactly equal, 0 contracts.
- **Minute coverage:** the set of minutes with trades equals the set of bar minutes exactly.

| Day | Trades | Minutes compared | Mismatched minutes | Minutes only in ticks / only in bars | Instrument |
|---|---|---|---|---|---|
| 2026-07-15 | 360,571 | 1,380 | **0** | 0 / 0 | 42003239 (MESU6) on both sides |
| 2026-07-31 | 455,192 | 1,260 | **0** | 0 / 0 | 42003239 (MESU6) on both sides |

**Result: pass.** The table uses the vendor's own bucketing clock.

**Finding: bars bucket trades by `ts_recv`, Databento's capture clock, not by `ts_event`, the CME clock.** The first aggregation, by `ts_event`, gave 12 mismatched minutes (8 and 4). Each was one of a pair of adjacent minutes whose volume differences cancelled exactly. Those minutes contained trades CME stamped in the last millisecond of a minute that Databento received in the next minute. The largest case: 187 contracts stamped 04:59:59.9998 UTC but received 05:00:00.0095, which moved that minute's high and close by 6 ticks.

Re-aggregating by `ts_recv` gives the 0/0 result above. The tolerance was not loosened: the ts_event-bucketed result is kept in the JSON as a diagnostic.

**Implication for Stage C.** A bar's contents are "what Databento received in that minute". Leakage canaries should treat the bar boundary as a receive-clock boundary.

## 6. What this validation does not establish

- **Bar-level vs tick-level.** Bars were only cross-checked against ticks on two days. The rest of the window is validated for structure and calendar, not reconciled trade by trade.
- **Degraded days.** Databento's degraded dates were not inspected beyond their bar-level checks.
