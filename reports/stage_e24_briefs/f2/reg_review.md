# E22-F2 registration review (C4b RegReviewer-FableXHigh, Stage E.24)

Reviewer: Fable 5.1, xhigh, independent (wrote none of the files reviewed). 11:26-11:49 PDT 2026-10-18.
Object: reports/stage_e24_prereg_F2.md (DRAFT, sections 5-6 revised 11:16-11:20 PDT, rulings Q1-Q23 in
reports/stage_e24_briefs/f2/f2book_report.md) and forward/strategy_f2.py, forward/runner_f2.py (post wave-2 fix,
sha256 db7580a0...), forward/evaluate_f2.py, forward/daily_f2.py, forward/config_f2.json, forward/tables_f2.json,
tests/test_forward_f2_*.py. Read by section; nothing under review was modified; no network, no market data, no .env.
forward/sources_alpaca.py and forward/etf_bars.py were grepped only where the runner's semantics depend on them
(C4a owns them). Every probe below was run on synthetic bars (InMemoryEtfSource or position_steps inputs).

Labels follow the brief: BLOCKING (wrong result, frozen behaviour changed, a silent failure that can corrupt a ledger
or a verdict, a spec violation), SHOULD FIX (a real defect with limited reach, a missing test of a required case),
NOTE. Line numbers are those of the files at review time.

## 1. Verified (passes)

- IDM. Recomputed from forward/config_f1.json `idm.correlation` with the rows and columns of MNQ, M2K, MGC, MCL, MNG,
  M6E, 2YY, 10Y, 30Y, MZC, MZS (MZL dropped), equal weights 1/11, negative entries floored at 0 (one entry is
  -0.1545), dm_max 2.5, via forward.core.idm_for_live: **2.3293791420997985**, bit-equal to section 2 and to
  config_f2.json `idm.value`. The cap does not bind (uncapped value is the same number). The 11 x 11 block in
  config_f2.json equals the F1 sub-matrix taken by the `e22_f1_micro` map; `source.sha256` equals the sha256 of
  config_f1.json. F1's own 12-live value 2.3518129452424255 reproduces.
- FDM 1.1313802916085167 and its 4 x 4 correlation are identical to F1's. The blocks `ewmac`, `forecast_cap`,
  `average_abs_forecast`, `vol`, `vol_target`, `fdm`, `warmup_diffs`, `simple_rounding` are value-equal to F1's.
- Power statement: 1 - Phi(1.645 - S sqrt 3) = 0.130, 0.218, 0.535 for S = 0.3, 0.5, 1.0; SR at t = 1.645 over 3
  years = 0.95. All as printed.
- Constants against the fact files: B = 2 x 25,000 (alpaca_facts.md A7 "2x ... overnight buying power"); 0.001 share
  and 9 decimals (A5); SEC 0.0000206 on sells, TAF "$0 per share", CAT 0.000003 every fill, "each fee total is rounded
  up to the nearest cent" (fees_facts.md F1, l.17-20); 6.50% on the debit over 360 (F4); ETB $0 borrow and "paper
  trading does not account for ... Regulatory fees ... Dividends" (F5); schedule "Revised on October 12, 2026"
  (fees_facts l.21). The saved FRB page has sha256 prefix f0803636 and contains "September 17" and "3.75"; I did not
  reproduce the exact cell string with grep (table markup), so that passage stays [unverified by me].
- Code equals text, sections 4-8, except where listed below: steps 1-6 (strategy_f2.position_steps, decide);
  fills at the next processed session's raw close and order expiry (runner_f2._symbol_day); a sign change as two
  legs (fill_legs); SEC on every sell leg including short opens, TAF on sells (0), CAT on all fills, per-type ceil to
  the cent with the 6-decimal guard, half spread unrounded (leg_record, session_costs, ceil_cent); d from the last
  record that is not a missing day (accrual_base; a missing day's accruals roll forward); shorts and leverage terms
  (_pnl); share update k x (1 + D/close) through mark x (1 + r)/close; late distribution, split and BIL rules per
  Q15/Q16/Q17/Q21/Q23 (late_corporate_actions, _late_cash_dr, session_return, corrected_rows; recorded days
  unchanged); missing day = no bar for any of the 11 ETFs whatever BIL delivers; SourceUnavailable writes nothing;
  check_date, re-run and LedgerConflictError are F1's; feed validated against the registered pair, stored per record,
  refused on change; verdict = section 8 with forward.evaluate's newey_west, one_sided_p, annualised_sharpe,
  passes, window [start, start + 36 months), start = first record, no clock-start option, missing days count 0,
  looks descriptive only.
- The late BIL correction -L_ex x dr_c is the complete correction: the excess term's -sum N_i dr_c and the shorts
  term's -S_ex dr_c combine to -L_ex dr_c (shorts earn no credit either way).
- Look-ahead: none found. decide() raises when history holds data after t; orders decided at t fill on t+1's bar;
  late corrections use only publication-day information; the warm-up is read before the start.
- E22-F1 untouched: `sha256sum -c --quiet reports/stage_e22_f1_files.sha256` OK; no setattr/monkeypatch of
  forward.core, forward.strategy or forward.evaluate in any F2 file (grep); F2 imports them read-only.
- Tests: `uv run pytest -q -p no:cacheprovider tests/test_forward_f2_*.py` 60 passed (1.49 s).

## 2. Findings

### BLOCKING

**B1. Silent position drift when the source's copy of the previous close differs from the stored one.**
forward/runner_f2.py:665 `factor = mark[0] * (1.0 + bar.ret) / bar.close`; prereg lines 127 and 148.
Failure scenario (reproduced): QQQ held 100 shares; the ledger stores close(D2) = 500.00; on D3 the source's bar
carries ret = 505/500.25 - 1 because its history now holds 500.25 for D2 (a corrected print, or a daily bar
re-aggregated after the 2 h cutoff) and no corporate action. factor = 500 x (1 + ret)/505 = 0.99950; the shares
become 99.950025 with no trade and no flag (`prev_date_mismatch` compares dates, not prices). The position is
permanently 0.05% below the declared rule, every later P&L is 0.05% low, and the $25 revision is never booked. The
record stays internally consistent (value before + booked P&L = value after), so the ledger cannot detect it. The
text's "a correction the tape sends later never changes a recorded day" holds for the record; the correction leaks
into the position instead. The text's own formula causes this: r uses the source's rawclose(prev) while the share
update uses the recorded rawclose(t-1), two copies of one number. Frequency unknown: if Alpaca finalizes daily bars
after the cutoff it fires every day. Fix (text and code): define rawclose(prev) as the recorded close. With
`ca_applied` stored (Q23) the runner has k and D for each symbol-day: share-update factor = k x (close + D)/close;
P&L return = k x (close + D)/mark - 1; flag `prev_close_mismatch:S` (or refuse the day) when
|k (close + D)/(1 + ret) - mark| exceeds a declared tolerance. Keep the current formula only when ca_applied is None
(CSV and in-memory sources). Add the test.

**B2. The late-action key `symbol|type|ex_date` collides for two same-type distributions on one ex_date.**
forward/runner_f2.py:331 `_ca_key`; :365 (conflict raise); :528 (`inside_recorded_return` skip); seen_keys.
Scenario A, stall: both arrive late (the expected case for distributions, prereg l.165-168) with different amounts.
normalize_late_actions raises RunnerError "conflicting late actions" on every run of that date; daily_f2 adds them
from the endpoint automatically and `--late-ca` cannot remove one; the day cannot be written, later dates are refused
(order), and the only remedy changes frozen code: the test stalls or is abandoned.
Scenario B, silent drop: one was counted in the recorded r (0.25) and the other arrives late (0.10): skipped as
`inside_recorded_return`; or both arrive late on different days: the second is `already_handled`. The P&L misses a
real distribution (a gain for longs, a charge for shorts), unflagged.
Plausibility: bond ETFs pay a December income distribution and a capital-gain distribution on one ex_date; if Alpaca
types both `cash_dividend` (the fixer's Q23 test assumes exactly this pattern) the key collides. The fixer listed
this under "Not done". Fix: put amount_or_ratio (or Alpaca's action id) in the key; same-key dedupe then means the
same action; update applied_keys and seen_keys; test both scenarios.

### SHOULD FIX

**S1. Section 4 step 5 contradicts itself for shorts (text).** prereg lines 83-87: "shorts ... are left as they are"
and "so the gross never exceeds B" cannot both hold. Reproduced with position_steps: n_A = -300 at $100, B = 30,000,
held -320: the buffer's lower edge is -310, gross 31,000; the second check runs with factor 0, scales nothing, and
the gross stays 31,000 (also: held -290 after a 5% price rise, gross 30,450). Two honest implementers differ (one
would trim shorts toward zero). Fix the text either way: state that the gross may exceed B by the shorts' buffer
margin and price drift, or declare the short trim and change strategy_f2.position_steps:211-227.

**S2. Q24: a late distribution on a session whose r held a split books q_ex x amount, under-booking by k.**
prereg lines 155-156; runner_f2.py:560. 2:1 split recorded, q_ex = 10, late $1.00 per post-split share: books $10,
the shares received $20. Conservative for longs, anti-conservative for shorts (half the charge). Fix text:
q_ex x k x amount with k the product of the session's split ratios (recorded and late); code `held * k * amount`.
The second-order miss the fixer notes (a late split skipping (k - 1) x q_ex x D0/close reinvested shares) is
negligible; state it or ignore it explicitly.

**S3. Section 6 line 173 is ambiguous on the cash term of an ETF without a bar (text).** "its P&L accrues when its
data returns" reads as the whole N_i (r_i - r_c); the code (runner_f2.py:683-690, Q3) charges -N_i x r_c on every
session BIL has a bar and books N_i x r_i on return. Reading it the first way under-charges N_i x r_c(gap). Fix:
"its N_i x r_i accrues when its data returns; -N_i x r_c is charged each session on which BIL has a bar".

**S4. Carried positions enter step 5 but not step 2 (design and text).** strategy_f2.py:199 (G over new targets
only, Q8) and :215 (step 5 includes carried positions). When the cap binds and one ETF has no bar, the others are
scaled to fill B and step 5 then cuts the new-target longs to make room for the carried one; the next day everything
reverts. Reproduced: book {A 12,000, B 12,000, C -6,000, D 25,000} at $1 at the cap, D missing on t: A, B -> 7,550
(sell 37%), C -> -9,900; t+1 with D back: A, B -> 10,986, C -> -5,611, D -> 22,416: about $18k traded over two
sessions on a $50k book with no signal change. Text line 72 does not say G excludes carried positions; only step 5's
"including" implies it. Fix: include carried notional (last close) as a fixed term in step 2 (scale the new targets
to B - carried, floored at 0) and say so; or state the exclusion and accept the round trip. Reach: missing bars are
rare (the source re-queries single symbols), but the cap is expected to bind most days.

**S5. The expected-behaviour paragraph (lines 213-217) omits two drags a FAIL would otherwise be blamed on (text).**
(i) Financing at the cap: with L up to 50,000 the leverage term is up to 25,000 x 2.5% = $625 a year; on the
paragraph's own premise (book scaled to B/G, about 0.36 with general-knowledge vols, unsourced, as the text does) the
book's daily vol is about 0.36 x 25,000 x 0.2/16 = $110, about $1,800 a year, so the spread alone costs 0.2-0.35
Sharpe against a 0.3 bar (a 40k-long book: $375, 0.2). (ii) Dividend timing: with distributions expected to be
published about 15 days late (lines 165-168), every monthly bond-ETF and BIL ex_date books a false move (SHY at half
the gross: 0.3% x 25k = $75; BIL via -L x dr_c: 0.3% x L = $150) reversed when booked; zero-mean, but it adds
roughly 15-20% to the daily variance (about -8% on the Sharpe) and the reversal lies outside the lag-10 Bartlett
window, so the Newey-West LRV is overstated (t understated: conservative). State both so the power statement is read
against the recorded net series.

**S6. A late split distorts exposure until booked (text).** prereg line 156. The late rule repairs the P&L exactly
(probe: an unpublished 1:4 reverse split records +150,000 excess on 100 shares at 500 -> 2,000 and the late entry
books -150,000; the sum is 0), but between ex_date and booking the book holds q_ex shares at k^-1 x price: held
gross 200,000 against a 50,000 cap, so the next decision's second check zeroes every other new-target long and the
signal sees a +300% jump. UNG and USO reverse-split repeatedly. Whether Alpaca publishes splits before their ex_date
is unverified (alpaca_report.md speaks only of dividends). State the consequence in the expected-behaviour
paragraph, or pre-register a guard (for example: a raw close moving more than X% with no stored action puts the
symbol in `missing` until an action arrives or the operator confirms). The lead's decision.

**S7. No rule for delisting, liquidation, merger or ticker change (text).** grep finds none in the prereg or the
code. CORN, SOYB and FXE are small funds and the horizon is 36 months. Today a liquidated ETF yields `missing:S` every
day, its position is carried at its last close forever, consumes the cap (S4) and earns nothing; a cash merger or
redemption is "flagged and not booked" (lines 163-164), so the cash paid is lost; a ticker change breaks the symbol
map. Two implementers would differ. Declare (for example: close at the last recorded close on the effective date as
a fill with costs, drop the instrument, n_live falls; map a renamed ticker) and test.

**S8. Missing tests of required cases.** None covers: a revised previous close (B1); same-key distributions
arriving late (B2); a reverse split through the share update and the late rule (my probe passes); a late
distribution on a short (my probe books -15.00 for -50 x 0.30: correct, untested); the shorts-above-cap path (S1).

### NOTE

N1. Buffer-plus-cap trickle: after one step-5 event, an instrument left below its lower edge is bought back each
session while the others are scaled down: 11 sessions of shrinking trades in a 3-instrument probe (26 -> 0.001
shares). Costs are cents (fee round-ups). A design consequence, not a defect; worth one sentence in section 4.
N2. Late actions with ex_date in the warm-up are never booked (`not_in_a_recorded_session`); the text's rule covers
"a session already recorded" only. With distributions published about 15 days late, the warm-up's last two weeks
miss them (one false drop per fund in the signal history). Say so in section 7.
N3. The share update applies to shorts: a $0.30 dividend turns -50 into -50.1667 shares; the next decision truncates
to -50 with a 0.1667-share buy-to-cover. Economics right (-$15.00). Lines 79-80 say shorts are whole shares only;
state the exception.
N4. strategy_f2.py:135 `_trim_to_cap` is a third float guard; section 2 declares two. floor_long already makes the
gross <= B mathematically; the trim covers fsum noise only. Declare it or drop it.
N5. `second_check.applied` is True with `scaled: []` when there are no new-target longs (S1 probe); evaluate_f2.look
counts `days_second_cap_check` from it. Record applied False (or a `no_longs` marker) in that branch.
N6. daily_f2.py:24 docstring says the warm-up reads "raw and all-adjusted" bars; section 6 says "all" is not used and
sources_alpaca.fetch_warmup requests only "raw" (grepped). Fix the docstring.
N7. evaluate_f2.py:49 redefines HORIZON_MONTHS = 36 rather than importing forward.evaluate.HORIZON_MONTHS (FROZEN_BAR
carries 36). Equal today; import it so they cannot diverge.
N8. evaluate_f2.py:78: the verdict needs a record dated on or after start + 36 months, so the operator must run at
least one session past the horizon (as in F1). Put it in section 8 or the user checklist.
N9. Line 3 STATUS "DRAFT 1" is stale (sections 5-6 revised); the four module docstrings cite "DRAFT 1" too. Update at
the freeze.
N10. TAF at Alpaca's printed $0 against FINRA's $0.000166 per share (fees_facts.md l.23): declared and sourced; the
conservative choice is FINRA's rate; about $0.08 a day at 500 shares sold, negligible.
N11. evaluate_f2.integrity_problem (:54-69) abandons on differing config, warm-up, feed or schema values; the text's
abandonment list (lines 186-187) names only a broken chain, a rewrite and an out-of-order date. Add them to
section 6.
N12. Fractionability is per asset on Alpaca (alpaca_facts.md A5: "check ... fractionable = true"); the text treats
all 11 as fractional to 0.001. Verdict-neutral (paper book), but the shadow route may reject CORN, SOYB or FXE
fractions; record each asset's flag in the first connection session.
N13. daily_f2.py:138 queries process_date in [first record - 31 days, last record]: an action processed on day t is
offered on t+1 (fine); one processed on the horizon's last session is never booked (negligible). "Each action is
booked once" (line 161) also depends on sources_alpaca's windows (DAILY_WINDOW_DAYS 21 + CA_MARGIN_DAYS 60): an action
processed more than 81 days before its ex_date and more than 31 days before the first record is seen by neither path.
Not reviewed here (C4a).
N14. Line 95 writes N_i = q_i x rawclose_i(t-1); after a gap the code uses the ETF's last recorded close (Q6). Write
rawclose_i(prev) as section 6 does.

## 3. Not verified

Alpaca's bar finalization after the 2 h cutoff (decides how often B1 fires); process_date timing for splits (S6);
per-asset fractionability (N12); the FRB page's exact cell string (sha256 prefix matches). No network per the brief.

## 4. Counts and verdict

BLOCKING 2 (B1, B2). SHOULD FIX 8 (S1-S8). NOTE 14 (N1-N14).

Verdict: **BLOCK** until B1 and B2 are fixed and tested (both are small, contained changes to forward/runner_f2.py
plus one text definition); S1-S7 are text edits (S2 and S4 also code) that belong before the freeze; the NOTEs can go
with it. Everything verified in section 1 stands: the IDM, FDM, frozen blocks, power figures, F1 integrity, the
verdict code and the absence of look-ahead.
