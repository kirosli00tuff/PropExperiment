# F5: holding-time scope code (E.32b, spec section 7)

Written by HoldingCoder (Opus 5.5, xhigh), 2026-10-28, from 23:22 PDT. Facts only: no strategy outcome is computed or
read. In this wave the script ran only on synthetic fixtures, plus one smoke run that used F3_vol.json's real shapes
with a synthetic F4 and selection. That run printed counts only and its outputs were deleted. The lead runs it on
real facts after the ranking.

## Files

| File | Role |
|---|---|
| sr80.py | SR80 from E.32 P7.2, using p7_final.py's definitions (imported read-only, no bytecode written) and an independent re-implementation; writes SR80.json |
| SR80.json | SR80 values, formulas, thresholds, cross-check (pass) |
| f5_core.py | the pure section 7 formulas: costs, k(h), g, p, n_max and n_cap, e80, G, prop columns, band B, verdict |
| f5_holding.py | CLI: spec and input hash checks, input validation, assembly, F5_holding.json and F5_holding.md |
| f5_venue.py | own-broker venue rows "ibkr|<CODE>" (spec 8.2-8.3, lead rulings LR-F5-IBKR and LR-Q6d), used by --venue-file |
| SCHEMA.md | input and output schemas, including the selection file |
| test_f5_core.py, test_f5_holding.py, test_sr80.py, test_f5_venue.py | unit and end-to-end tests on synthetic inputs (101 tests, plus 28 venue tests added 2026-10-29: 129) |

## Run

    uv run python reports/stage_e32b_briefs/work/F5/sr80.py                      # already run; rewrites SR80.json
    uv run python reports/stage_e32b_briefs/work/F5/f5_holding.py \
        --selection <score output JSON, or F5_selection.json per SCHEMA.md> \
        [--venue-file reports/stage_e32b_briefs/F4_venue_ibkr.json]   # optional own-broker rows; other inputs default to briefs/
    uv run pytest -q -p no:cacheprovider reports/stage_e32b_briefs/work/F5/

f5_holding.py refuses to run (exit 2, nothing written) in any of these cases: the spec's sha256 is not
09ebe697...8635; an input lacks that hash; SR80.json's cross-check did not pass; or the selection, tick sizes,
fees or listing are inconsistent (SCHEMA.md lists the rules). It runs in under a second, so it needs no heavy.lock.

## SR80 (daily Sharpe, N = 838, normal moments)

| Gate | Bar | T | SR80 (p7_final convention) | Exact root of p7 power = 0.80 |
|---|---|---|---|---|
| discovery, G3 alone | G3 = 0.17242 | 796 | 0.20249 | 0.20258 |
| discovery, G3 + G4 (binding) | max(G3, G4) = G4 = 0.20070 | 796 | 0.23085 | 0.23095 |
| test | b_test = DSR bar 0.16488 (> t-bar 0.10171) | 870 | 0.19363 | 0.19370 |

Primary: SR80 = bar + z_0.80 se(bar, T). This is p7_final's "80%-power true daily Sharpe" (`s80` in its report()),
and it reproduces the printed 0.1936. Two cross-checks were run:
(A) p7_final's own functions, imported, against (B) a re-implementation from the DSR definition with
statistics.NormalDist only: the largest difference is 8.4e-11. p7_final.report(300) was also regenerated, and it equals
p7_final_budget300.md byte for byte; every value printed there matches at 4 decimal places.
N = 538 + 300, T_disc = 796 and T_test = 870 come from p7_final's own trade-date counts.

## Interpretations of spec section 7 (for the lead to confirm or overrule)

1. SR80 convention: as above, closed form at the bar's standard error. The exact root of p7_final's power() (standard
   error at the true Sharpe) is about 1e-4 higher and is reported beside it in SR80.json.
2. SR80 at discovery: "passes" means the observed discovery Sharpe reaches the gate's bar (G3 alone, or max(G3, G4)),
   with G4 = the smallest SR_d with SR_d - se(SR_d) >= b_test (P3.8 / P7.2 as coded in p7_final.py).
3. Firm-independent rows (survivors): spec 7's g, p, e80 and G are written with c_f. Survivor rows use c_RT as the
   cost basis (G_RT, etc.). The band and the verdict are computed only for pairs.
4. min G is one minimum over every row with a G: 1, 2, 5, ..., 240, OC and the overnight rows cc and on. The same
   minimum serves the band's "1.10 min G" and the verdict's "minimum of G lies at ...". Ties are values within a
   relative 1e-12 of the minimum.
5. Band boundaries are inclusive: G(h) <= 1.10 min G and DLL_f / (sigma_h v) >= 2, each with a relative tolerance of
   1e-12.
6. Unknown DLL ratio or unknown flat-by-close: the condition does not exclude h. It is listed under
   band.unknown_conditions and the pair's u list. DLL "none" uses MLL (spec 4 D). A null DLL is unknown and is not
   replaced by MLL (as in ScoreCoder's D).
7. "Fits before flat-by-close": an h-minute hold must end by min(main-session end, flat-by-close) and start at or
   after the main-session start. OC fits if and only if flat-by-close is not before the main-session end. n_max stays
   floor(L_main / h) as spec 7 writes it, even where an early flat-by-close shortens the usable session.
8. Verdict precedence: the fail conditions (B empty; min G at 1 or 2 minutes; the min-G set lying only in {OC, cc,
   on}) override everything else. Otherwise the verdict is partly if B contains OC, and holds if not.
   B = {OC} alone with an intraday minimum gives partly. The spec's "also" leaves this case open, and it is flagged.
9. Overnight rows (cc, on) are computed with one trade a day and count toward min G. They are never in B. Their
   permission (overnight_allowed) is reported but not applied.
10. "Where k flattens" has no numeric definition in the spec. The script reports k's successive ratios and the first
    h where the power term SR80_test / sqrt(n_cap) reaches the cost term c_f / sigma_h. The lead writes the prose.
11. News windows and pauses are reported (pauses get inside / adjacent / outside where they carry PT times). They do
    not enter B, because spec 7's B rule does not name them.
12. Other edge handling: a horizon with n_cap = 0 (h > L_main) or with sigma unknown or non-positive has no G. Hit
    rates above 1 are kept as computed. Flat-by-close zones are converted with fixed offsets from PT.

## Not covered here

- (Since 2026-10-29, F5Runner: the own-broker venue IS wired in. `--venue-file` adds `own_broker.rows."ibkr|<CODE>"`
  for every selected code (survivors, then top-15 codes) under the lead's rulings LR-F5-IBKR (c_f = c_RT + F_rt / v,
  F_rt = 2 x the all-in fee per side; B = {h in 5..240, OC : G(h) <= 1.10 min G}, no DLL or flat-by-close condition;
  overnight rows carry the overnight margin) and LR-Q6d (margins against the capital ceiling, USD 6,000 (u) when
  none is recorded; sigma_day = sigma_cc x v against 2% of it; sigma_OC x v beside). min G, the verdict and
  band_context are the same functions as for the firm pairs. A code missing from the venue file or without a
  published per-side fee is listed under own_broker.not_computed. Without --venue-file the output is unchanged.)
- E.33's cost and trade-count citations (spec 7, last bullet): these are for the lead's scope file.
