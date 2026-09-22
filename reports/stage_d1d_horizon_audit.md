# Stage D.1d — Task 1: horizon-resolution audit of the 24 trials

Written 2026-09-21 by the lead (Opus), before the Task 2 declaration and before any D.1d
computation code existed. It judges only whether each trial was tested at the resolution
its cited source specifies. It says nothing about whether any effect is real.

**Evidence used:**
- D.1's untruncated literature log (`all_results.json` in the D.1 session's workflow
  directory, keys `lit` and `scr`), not progress.md's truncated table;
- each trial module's code and docstring;
- two primary sources re-read this session because the log was ambiguous on horizon:
  - Mesfin (2026), arXiv 2605.04004: PDF → `pdftotext`, exact text;
  - Carver (2018), "Vol targeting and trend following": raw HTML, tags stripped by hand,
    exact text (not through a summarizer).

**Process, stated plainly:**
- Family A was audited by one subagent. Its adversarial verifier failed with the rest of
  that workflow on the account's weekly limit. I reviewed its records against the code;
  every A trigger is a clock instant, a trade-date change or a weekday label.
- Families B–E were audited by the lead, inline, after the other four auditors failed on
  the same limit.

**Verdicts:**
- **FAITHFUL:** the trial matches the source's horizon, or the source's horizon is a clock
  window that a 1-minute grid represents exactly.
- **RESOLUTION_MISMATCH:** the source's signal, trigger, window or hold is 5 minutes or
  coarser, and the trial forced a finer one.
- **SOURCE_SILENT:** no stated horizon to compare against.
- **NON-RESOLUTION:** the horizon differs for a reason other than bar size (flatten
  truncation, window definition). D.1c's scope, not this session's.
- **Flag:** a RESOLUTION_MISMATCH with a plausible mechanism by which the finer grid could
  understate the claimed effect.

**Harness fact behind every row:** `on_bar(N)` runs after 1-minute bar N closes, and a
market order fills at bar N+1's open.

## Table

| # | Trial | Source's stated horizon (evidence tier) | What the trial used | Verdict | Flag → re-test grid |
|---|---|---|---|---|---|
| 1 | A-H1 european-open overnight drift | 02:00–03:00 ET clock hour (SR 917; log, PDF) | fills at the 02:00 / 03:00 ET 1-min opens | FAITHFUL | no |
| 2 | A-H2 rth close window (buy) | last 30 min, 15:30–16:00 ET (Baltussen et al.; log, PDF). The source's rest-of-day predictor was dropped by design: a content change, not resolution | fills at 15:30 / 16:00 ET | FAITHFUL | no |
| 3 | A-H2 rth close window (sell) | same | same | FAITHFUL | no |
| 4 | A-H3 weekend effect | JKM (JFQA 1991) compute close-to-close, close-to-open and open-to-close daily returns and locate their significant Monday seasonal in the **open-to-close** (trading-hours) return (primary, fetched twice this session; amended, see below) | RTH-only Monday short / Friday long, clock fills, i.e. one session open-to-close | FAITHFUL on the named source. (NON-RESOLUTION only under the docstring's secondhand French-1980 cash-equity reading, which is close-to-close; D.1c's "weekend gap" rationale is Rogalski 1984, which JKM cite but do not reproduce) | no |
| 5 | A-H4 eth leg | close-to-open overnight, 16:00 → 09:30 ET (the cash-equity convention; the log says only "earned entirely overnight") | fill at the 17:01 CT open (the 17:00 bar's decision) → the 08:30 CT open | NON-RESOLUTION (flatten truncation; D.1c) | no |
| 6 | A-H4 rth leg | 09:30–16:00 ET | same clock window | FAITHFUL | no |
| 7 | B-H1 ORB (hold 5) | Mesfin §4.1: **5-min bars**; opening range 09:30–09:55 ET ("the first six five-minute bars", i.e. 30 min); signal at bar close, entry at the next bar's open; hold bar+1 = 5 min (primary PDF, exact) | OR **15 min**, trigger on the first **1-min** close ≥ OR ± 4 ticks, hold 5 × 1-min | **RESOLUTION_MISMATCH** (trigger bar; the OR window also differs from the source) | **yes → 5 min** |
| 8 | B-H1 ORB (hold 75) | same, bar+15 = 75 min | same trigger, hold 75 × 1-min | **RESOLUTION_MISMATCH** | **yes → 5 min** |
| 9 | B-H2 prior-day stop cascade | stop-order execution at the trigger moment; Kirilenko "hot potato" (transaction-level, sub-minute; log, PDF) | first RTH 1-min close through the prior session's high/low ± 4 ticks; 15-min cap or volume-decay exit | FAITHFUL (the source is finer than 1 min, so a 1-min close is coarser, not finer) | no |
| 10 | B-H3 breakout leg | Mesfin §4.1 (5-min bars, OR = six 5-min bars); Holmberg et al. (crude oil, threshold from the open) | OR 30 on 1-min bars, trigger on a 1-min close ± 4 ticks, hold 30 | **RESOLUTION_MISMATCH** (trigger bar) | **yes → 5 min** |
| 11 | B-H3 fade leg | same | same trigger, opposite side | **RESOLUTION_MISMATCH** | **yes → 5 min** |
| 12 | B-H4 narrow-range breakout | Holmberg et al. (threshold-from-open entry, i.e. finer than 1 min); Crabel's contraction principle cited only secondhand; Carver breakout 10–320 *days* (summarizer, [unverified]). The log gives no intraday resolution for the contraction measure | OR15 width vs trailing 20 sessions; 1-min trigger | SOURCE_SILENT | no |
| 13 | C-H1 magnitude-conditioned reversal | Safari & Schmidhuber: **minute** data, next-minute reversion; Carver: "fast" = 2–30 min (log, PDF) | 5-min return re-evaluated every 1-min bar; 5-min hold | FAITHFUL (the source's own grid is the minute) | no |
| 14 | C-H2 post-spike exhaustion fade | Mesfin §4.2: **5-min bars**, range > k × rolling **20-bar** average, reversal T = −11.52 at **bar+1**; §4.5: 5-min volume spike, H = 1 (primary PDF, exact) | 1-min bars, 60-bar baseline, range ratio > 3 or volume z > 3, fade, hold 2 × 1-min | **RESOLUTION_MISMATCH** (trigger bar, baseline, hold) | **yes → 5 min** |
| 15 | C-H3 CLV reversal | the CLV construction has no sourced horizon (task-scope proxy); nearest evidence is Mesfin §4.6 (a day-level classifier) and opening-reversal abstracts, which are different constructions | 1-min CLV bars | SOURCE_SILENT | no |
| 16 | D-H1 trailing-vol regime gate | a daily-regime claim: "a high- or low-vol state today predicts a similar state tomorrow" (daily RV persistence; D2 and HAR, log-summarized) | EWMA λ = 0.94 over **1-min** returns (half-life ≈ 11 min), snapshotted at the day's first bar, so in practice the prior session's last ~20–30 minutes | **RESOLUTION_MISMATCH** (signal window) | **yes → daily RV built from 5-min returns (5-min workstream)** |
| 17 | D-H2 inverse-vol sizing | Carver: "This is a system which vol targets using the last month or so of returns" (daily pysystemtrade; primary HTML, exact) | EWMA λ = 0.94 over **1-min** returns, updated every bar | **RESOLUTION_MISMATCH** (signal window) | **yes → daily RV built from 5-min returns (5-min workstream)** |
| 18 | D-H3 range-compression gate | Bookmap narrative; no timeframe stated, mechanism [unverified] | 1-min 20-bar range, 20-bar breakout | SOURCE_SILENT | no |
| 19 | D-H4 overnight gap fade | SR 917 overnight return; its verified figure is the 02:00–03:00 ET drift. "Close 16:00 ET → open 09:30 ET" is the lead's reconstruction of the paper's overnight window, not a log quote | gap = the 17:00 CT first-bar open vs the prior trade date's last bar (~15:59 CT): the 1-hour **halt gap** on a weekday, and the ~49-hour weekend closure on a Monday or post-holiday date; entry 17:01 CT, hold 30, flat by 17:31 CT, i.e. never inside the source's 02:00–03:00 ET window | NON-RESOLUTION (a different conditioning variable, sometimes finer and sometimes coarser than the source's; bar size is not the issue). **New relative to D.1c**, which treated D-H4 as horizon-faithful | no |
| 20 | E-H1 scheduled macro drift | 24-h pre-FOMC | truncated at the 17:00 CT open | NON-RESOLUTION (D.1c) | no |
| 21 | E-H2 post-release momentum | price discovery within ~1 min, normalizing over 5–15 min (transaction data) | 5-min reaction window, 10-min hold | FAITHFUL | no |
| 22 | E-H3 quarterly witching short | last half hour of expiration Friday | 14:30–15:00 CT | FAITHFUL | no |
| 23 | E-H4 turn-of-month long | a 4-session hold | single-session longs | NON-RESOLUTION (D.1c) | no |
| 24 | C-H4 passive-fill reversal | as C-H1 (Carver 2–30 min; S&S minute data) | C-H1's signal, passive fills | FAITHFUL | no |

**Counts (after the amendments below):** FAITHFUL 10, RESOLUTION_MISMATCH 7 (all 7
flagged), SOURCE_SILENT 3, NON-RESOLUTION 4; 24 in total. As first written, before the
verification pass, the counts were 9 / 7 / 3 / 5; the flagged list did not change.

**Flagged list, which is the exact and only scope of Task 3's re-tests:**
- B-H1 (hold 5)
- B-H1 (hold 75)
- B-H3 breakout leg
- B-H3 fade leg
- C-H2
- D-H1
- D-H2

## Notes on the calls that were not obvious

- **All five B/C flags trace to one source.** Mesfin's MNQ study is built entirely on
  5-minute RTH bars ("Bar resolution: 5-minute OHLCV", Table 1; "Signal at bar close.
  Entry at next bar open", §2.2). D.1's hypotheses carried its horizons (bar+1, bar+15,
  the 20-bar baseline) but moved every trigger to 1-minute closes.
- **Mechanism of plausible understatement (B, C):** a 1-minute close-through admits
  noise-level penetrations of the level that a 5-minute close would filter. A 1-minute
  spike selects a different, noisier event population than the 5-minute expansion bar
  whose bar+1 reversal the source measured.
- **B-H1's opening range was also not the source's.** D.1 read the source as "15–30
  minutes" and chose OR15. The primary text says 09:30–09:55 ET, i.e. 30 minutes. The
  re-test uses the source's 30 minutes (see the declaration's rule for which parameters
  follow the source).
- **D-H1/D-H2 (signal window):** RiskMetrics' λ = 0.94 is a daily-return constant, with a
  half-life of ≈ 11 observations. Applied to 1-minute returns, it measures the last
  quarter-hour of volatility, not the "state today" or the "last month or so" the sources
  describe. A quarter-hour reading is a noisy proxy for the daily regime. That plausibly
  weakens a low-vol gate (D-H1) and the risk normalization vol targeting relies on (D-H2).
  - Confidence is medium for D-H1: its daily horizon rests on log-summarized sources.
  - Confidence is high for D-H2: Carver's text is exact.
- **Not flagged, with reasons:**
  - B-H2 and E-H2: the sources are finer than 1 minute.
  - C-H1 and C-H4: the source's grid is 1 minute.
  - B-H4, C-H3, D-H3: no intraday horizon is stated for the construction the trial used.
    Crabel's narrow-range days are a daily construction by general knowledge, but that is
    not in the log. Conditioning on prior days' ranges would be a different hypothesis,
    not a resolution re-test.
- **Every flag maps to the 5-minute grid.** None of the sources the 24 trials cite
  specifies a 15-, 30- or 60-minute bar. The 15/30/60-minute workstreams therefore carry
  no re-tests; they run only the declared sweep.

## Amendments after adversarial verification (2026-09-21, after the declaration was hashed)

Five Opus verifiers, one per family, re-derived every row from the log, the code and the
primary sources and tried to refute each verdict in both directions. **All 24 verdicts'
flags and all 7 re-test grids were upheld, so Task 3's scope is exactly the list above.**
Three descriptive corrections were accepted and applied to the table; none touches a flag:

1. **A-H3 (row 4): verdict relabelled NON-RESOLUTION → FAITHFUL on the named source.** JKM
   (1991, p. 26 and p. 31, pdftotext of the Purdue mirror) compute all three daily return
   series and report that "the significant seasonals observed using close to close data
   are concentrated during trading hours. Using open to close returns, average returns
   from GNMA and T-bond contracts are negative on Monday and significant at the 0.05
   level." The trial holds exactly one session open-to-close. The "weekend gap is not
   held" rationale, carried over from D.1c, is Rogalski (1984)'s cash-equity finding,
   which JKM cite but do not reproduce. The verifier kept this at medium confidence
   because the module's docstring names the classic equity Monday/Friday pattern (French
   1980, secondhand, absent from the log), under which close-to-close and NON-RESOLUTION
   would be right. Neither reading is flagged.
2. **A-H4 ETH leg (row 5): the entry fills at the 17:01 CT open**, not 17:00 (the 17:00
   bar's decision is 17:01). The table already said 17:01 for D-H4 on the identical
   mechanism; row 5 was inconsistent with it. The verdict and its reason stand: a hold
   from the source's 16:00 ET start would be force-flattened at 15:10 CT.
3. **D-H4 (row 19): two omissions filled.** The trial's gap spans the ~49-hour weekend
   closure on Mondays and post-holiday dates, not only the 1-hour halt; and the
   "16:00 → 09:30 ET" horizon is the lead's reconstruction of SR 917's overnight window,
   not a log quote (the log's verified figure is the 02:00–03:00 ET drift). The verifier's
   sharpest challenge, that a 17.5-hour source window forced to a 1-hour one is the same
   species of mismatch as D-H1/D-H2, was rejected on the ground the table now states: the
   trial's variable is disjoint from the source's effect window and sometimes coarser than
   it, so no bar-size change repairs it. Lengthening D-H1/D-H2's estimator on the same
   bars does.

Also noted by the verifiers: the "(log, PDF)" horizon cells for A-H1, A-H2 and A-H4 are
close paraphrases of the log's verified claims, not quotations (e.g. "15:30–16:00 ET" is
derived from "last-30-minutes-before-close" plus "09:30–16:00 ET"); every Mesfin and Carver
string in quotation marks was found verbatim in the fetched text.
