# Stage E.33c Part D5: StatsReviewer-FableXHigh review of Part D (branch N)

Reviewer: StatsReviewer-FableXHigh (Fable 5.1, xhigh, fresh context). Brief: reports/stage_e33c_briefs/brief_StatsReviewer_c.md
with its E.33c addendum; branch N (Tier A empty) as named in the spawn message. Started 2026-10-28 21:01 PDT; written
21:14 PDT. Read only, except this file; three recomputation scripts in my scratch folder (nice 10, one process each).

Verdict: **0 BLOCKING, 4 SHOULD FIX, 8 NOTE.** The selection decision (Tier A empty, no test list, no purchase) follows
from the gates as written and as ruled; every gate-relevant number agrees across select33, the StatsCoder's final
D_stats.json (cdaa33b8), the VerifyWorker's gates_own.json and my own third recomputation. The SHOULD FIX items are
all in the wording of the lead's draft section 3 (one overclaim, one number that overstates by rounding, one
ambiguous sentence, one missing like-for-like line); none changes a result.

## Inputs verified

- Protocol 0.3: sha256 a2a2856f49723f97319a4db2819ba4d1b5c4b8a1dc86a596e7c48110dbb48246 (equal to the addendum; read P6.1-P6.3,
  P7.2, P8, P10, P4.2). Readings: R-L8, P01-P08, K01. docs/NULL_CRITERIA_E.md sha256 b27ca69c... (equal to D_stats.json
  families.criteria_sha256). N = 838: reports/stage_e33_STATE.md:366 and search_end.txt ("current_n 838 | last r009-E33
  538 -> 838").
- D_stats.json: sha256 cdaa33b85f18c7d8..., mtime 20:57:27 PDT; D_stats.md mtime 20:57:28 (written from that file).
  P8_select33.json sha256 ee506884... (equal to D_stats.json inputs.select_json_sha256 and D4 section 1).
- gates_own.json (verify_c, 20:50 PDT), gates_table.csv (301 lines), compare.json; D4_verify.md (20:59).

## Check (a): final D_stats.json (cdaa33b8) against the VerifyWorker's own numbers

The VerifyWorker compared an earlier write (fac9aea9, 20:50). I compared the final file against gates_own.json and
P8_select33.json field by field (scratch script cmp_final.py; 1e-9 relative, 1e-12 absolute, exact for flags):

| item | result |
|---|---|
| per-configuration moments (mean, SD, SR_d, skew, kurtosis, n), t, trade count, dates with trade, trades per date, mean net per trade, hit rate, total net | 300 of 300 equal, 0 numeric differences |
| DSR (program function), se, sr_lower | 222 trading configurations equal; 78 constant series None in D_stats vs 0.000676 / 0.03547 / -0.03547 in gates_own (D4 section 6 item 1; same convention as P8) |
| gate flags G1-G5, G5 parts a-d, quarters positive, max month share, total, tercile means | 300 of 300 equal |
| G5 min leave-one-month-out t | 292 equal; 8 None in gates_own vs minimum over 38 months in D_stats (D4 item 3; same as P8) |
| funnel alone and in order | equal: 61 / 8 / 0 / 0 / 0 and 61 / 0 / 0 / 0 / 0 |
| ranking: D_stats ranking_top10 = gates_own top10 = gates_own ranking[:10] = P8 ranking_all[:10]; P8 ranking_all (300) = gates_own ranking (300) | equal |
| Tier A [], Tier B [E33-S2F30G2200, E33-S1F15G3200] (own correlation -0.00226) | equal in all three |
| thresholds b_test 0.16488165417252623, G3 0.17242150688451255, SR0 0.11365258253614735, G4 0.20070338124341464 | equal (gates_own b_test_program, g3_sr_threshold_normal_program) |
| top-10 per-fold, per-month and per-quarter sums (D_stats top10.p62) vs gates_own stats | 10 of 10 equal each |
| D_stats vs P8_select33 on SR_d, skew, kurtosis, t, DSR, se, sr_lower, counts, mean net, gates, G5 parts | 0 differences |

So the final file carries no gate-relevant change from the write the VerifyWorker compared; the lead's open item at
E.33c_RETURN.md:207-208 ("the final file (cdaa33b8, 20:57:27) is checked in D5") can be closed as "equal" (NOTE 1).

## Independent third recomputation (mine, from D_stats.json's own moments)

- SR0 = E[max] at N 838, V = 1/795 with my own NormalDist implementation: 0.1136525826 (D_stats 0.11365258253614735).
- DSR with the formula z = (SR - SR0) sqrt(795) / sqrt(1 - g3 SR + (g4 - 1)/4 SR^2): max abs diff vs D_stats over the 222
  trading configurations 1.4e-10; se max abs diff 6.9e-18; t 8.9e-16; SR_d 0. By hand for E33-S2F30G2200: radicand
  0.8943, z = -1.964, DSR 0.0248; se 0.03354; SR_d - se 0.01425.
- Gate flags recomputed from the thresholds: 0 differ from D_stats on 300; my funnel: alone G1 61, G2 8, G3 0, G4 0,
  G5 0; in order G1 61, then 0.
- BH (q 0.05) and Holm (0.05) over 300 one-sided p = 1 - Phi(t), p = 1 for the 78 no-t configurations (P07): 0 and 0;
  smallest p 0.0888 (equal to D_stats).
- s80 at the binding bar 0.200703 on T_disc 796: 0.230852 (D_stats 0.230852; exact-se variant 0.230948); at G3
  0.172422: 0.202492. P7.2's test figure reproduces: b_test + z_0.80 se(b_test, 870) = 0.1936. Random-walk e80 at the
  binding bar: 0.81 (h 5, n 4), 1.41 (15, 4), 1.99 (30, 4), 3.98 (60, 2), equal to D_stats and the RETURN.
- Measured per-configuration e80 among G1 passers (s80 x SD(X_D) / trades per date), medians: T15 1.57 (n 5), T30 1.95
  (34), F60 4.33 (20), F30 4.37 (2); equal to D_stats.json mde and E.33c_RETURN.md:156-158.
- B5 per-seed maxima: the 20 values in D_stats.json null.seed_maxima equal B5_proofs.md's table to 4 dp, 20 of 20.
- K6 list reports/stage_e22_k6_confirmation_list.json: sha256 ebb3d034ed001498... (as stated), 27 trials, 0 with an E33 id.

## Checks 1 to 8 (branch N; check 6 replaced by the section 3.8 check)

1. Gates and funnel follow P8 as written and ruled (P01 integer comparisons, P02 fsum / count, P04 (a), P05 undefined
   t fails (c), R-L8 Tier B continue from position 0). Selection follows: no passer, Tier A empty. PASS.
2. DSR, SR0, G3 and G4 at N 838 (STATE:366), V = 1/(T_disc - 1) (dstats_lib.evaluate:143 `1.0 / (t - 1)`, t = 796;
   run_dstats.thresholds:42), each configuration's own skew and raw kurtosis (moments()). b_test is the pinned
   0.164882 (the program function's value, as P7.2 requires). PASS.
3. BH, Holm and PBO are reports only (D_stats.md section "DSR at N, BH and Holm (reports, never gates)"; P6.3) on the
   declared sets: m = 300 with p = 1 for no-t configurations (P07); PBO over all 300 series, constants included, 0
   failed (P08), 8 blocks of 99 dates, 70 splits, PBO 0.1429 (10 of 70). PASS.
4. D3 null comparison: same statistic (moments() SR_d, no-trade series at 0), same 796 dates, the 20 null seeds as run
   (400 series, 31 constant; per-seed maxima over 20 configurations, not 300; B5 table reproduced 20 of 20;
   stats_json_max_sharpe_diff 0). The figure (D3_sharpe_hist.png) shows both panels and labels the per-seed maxima
   as maxima over 20. PASS, with SHOULD FIX 4 (the strictly like-for-like subset line is missing) and NOTE 2.
5. P10 (i)-(vi) complete: (i) funnel; (ii) 10 best with every P6.2 statistic (D_stats.md tables: moments, t, counts,
   mean net, hit rate, share of dates; gates, DSR, se, p, tercile means, rho rows and trades, mid-sign hit, top decile;
   per-fold, per-quarter, per-month sums); (iii) distribution beside the null and SR0 0.1137; (iv) PBO; (v) MDE per
   label with the formula e80 = s80 sigma_h / sqrt(n), sigma_h = 3.15 sqrt(h), s80 = bar + z_0.80 se(bar) at normal
   moments on T_disc, which reproduces P7.2's per-trade line (0.71, 0.50, 1.22, 0.87, 1.73, 3.46) and its s80
   convention (0.1936); (vi) "no statement" for all five sets, with the criteria file's conditions quoted verbatim
   (I re-found each quoted string in docs/NULL_CRITERIA_E.md sections 1, 3 and 6). (vii) is the lead's sentence,
   present verbatim at E.33c_RETURN.md:164. PASS.
6. (replaced) Section 3.8 promotes no near miss: the best configuration is named with its SR_d (0.0478 = 0.238 of
   0.2007), its 55 trades and its gate record, and no language suggests a follow-up on it. Claims beyond the
   evidence: one (SHOULD FIX 1); numbers in prose vs tables: one (SHOULD FIX 2); one ambiguous sentence (SHOULD FIX 3).
7. D4 independence in fact: the verify code imports only numpy, pyarrow, statistics, verify_common, cal33 (allowed
   by brief_VerifyWorker_c.md:32-33) and funnel.multiple_comparisons.deflated_sharpe_ratio (the program's function G3
   names; not a pipeline module); nothing from search33, select33 or work/stats. Its disclosure (D4_verify.md:37,
   read P8_select33.out before computing) is reported in the RETURN (line 206). Its three differences are reported in
   the RETURN (lines 204-207) and are conventions, not numbers; my check (a) above confirms none exists in the final
   D_stats.json beyond those. PASS.
8. Language: the RETURN's 3.4 table equals D_stats.json on all 10 rows (SR_d, t, DSR, counts, mean net, gates); the
   prose figures -1.098, -0.0522, 61 by set and label, 8 G2 passers with 8-55 trades on 2-47 dates, 0.0248, 0.0305,
   0.0888, t 1.348, medians -2.207 and -2.599, 6 at or above 0.50 under 0.920 with at most 55 trades, 10 positive
   totals each with a month above 25%, all equal the JSON. Section 2's search-end figures (300/300, 1,800 folds,
   0 failed, 6,311 MB, 14,047.4 s = 0.390 of the stop, current_n 838) equal search_end.txt. Items: SHOULD FIX 1-3,
   NOTES 3-5.

## BLOCKING

None.

## SHOULD FIX

1. reports/E.33c_RETURN.md:179-180, "within this frozen design, the discovery data hold no ZM signal of the size the
   search could select (section 3.7 v)". This is a claim about the data, and the search's power at that size is 80%,
   not 100%: a configuration with a true daily Sharpe of 0.2309 would have been missed one time in five, and one at
   the binding 0.2007 half the time. Fix: "within this frozen design, the search selected nothing; a configuration
   with a true daily Sharpe of 0.2309 (the 80%-power size of section 3.7 v) would have been selected four times in
   five, so an edge of that size or larger is unlikely in these 300 configurations but not excluded; it is not
   evidence that no ZM edge exists, and not a null statement in the program's sense (item vi)."
2. reports/E.33c_RETURN.md:175-176, "lose at least 1.1 ticks a trade after costs". The best G1 passer's mean net is
   -1.098 ticks (D_stats.md section "D1 and P10 (i)"; D_stats.json), so "at least 1.1" overstates by rounding. Fix:
   "lose more than 1.0 tick a trade after costs (best -1.098)", which also matches section 3.7 (v)'s "below -1.0".
3. reports/E.33c_RETURN.md:177-178, "no configuration passes more than one gate together with G1". True, but it
   reads as if some configuration passed G1 plus one other gate; none does (the 61 G1 passers pass no other gate; the
   8 G2 passers pass only G2; G3, G4 and G5 pass 0 alone). Fix: "no configuration passes two gates: the 61 G1 passers
   pass nothing else, and the 8 G2 passers fail G1, G3, G4 and G5."
4. reports/E.33c_RETURN.md:132-134 (and D_stats.md:235 for the same point). The comparison made is the real maximum
   over 300 configurations (5 sets x 6 labels) against null maxima over 20 configurations (S5 x {F15, T30}), which
   the text says; the strictly like-for-like line (same 20 configurations, same statistic, same dates) is missing
   and is computable from D_stats.json: the real S5 x {F15, T30} subset (20 configurations) has maximum SR_d 0.0426
   (E33-S5F15G2050, 39 trades); 2 of the 20 null per-seed maxima exceed it (one-sided rank p = 3/21 = 0.14); 2 of
   the 20 real subset configurations have SR_d > 0 (E33-S5F15G2050, E33-S5F15G3050). Fix: add after line
   134: "On the 20 configurations the null actually covers (S5 x {F15, T30}), the real maximum is 0.0426
   (E33-S5F15G2050); 2 of the 20 null per-seed maxima exceed it (rank 3 of 21)." This strengthens "looks like the
   null" (line 173) without overstating it.

## NOTE

1. reports/E.33c_RETURN.md:207-208: the D5 check of the final D_stats.json (cdaa33b8) against gates_own.json is done:
   0 numeric differences on all gate-relevant fields of 300 configurations, funnel, ranking (300), tiers and
   thresholds; only the two None conventions (78 and 8) already listed. Fix: replace "is checked in D5" with "was
   checked in D5: equal on every gate-relevant number (review/StatsReview_c.md, check (a))".
2. Two values for the same report: reports/E.33c_RETURN.md:136-138 and D_stats.md:243 give E[max over 300] = 0.1230
   (sigma_c 0.0425, uncorrected), while the figure's bottom-panel legend (plot_dstats.py:49, fed by
   run_dstats.py:431 `E_max_300_zero_edge_df`) prints 0.1262 (df-corrected 0.0436). Fix: quote one of them in the
   RETURN with its sigma_c, or write "0.1230 (0.1262 with the df-corrected SD 0.0436, the figure's line)".
3. reports/E.33c_RETURN.md:136-138: the construction assumes independence and a zero true edge for every
   configuration (D_stats.md:230-233 says both; the null's own means are negative). Fix: "as if the 300 were
   independent with zero true edge".
4. reports/E.33c_RETURN.md:175, "the 61 configurations that trade at least once a date": G1 is at least 1.0 trade per
   date on average and a trade on at least half the dates. Fix: "the 61 configurations that meet G1 (at least one
   trade a date on average, on at least half the dates)".
5. docs/prompts/STAGE_E.33.md:177 asks D1 for "stability across months and sessions"; the session split is a P6.5
   item and was not run (RETURN:141-142 covers P6.5 generally). Fix: name it in 3.4 or 3.6: "by session: not
   computed (P6.5, after a hashed test list; none)".
6. reports/stage_e33c_briefs/work/D_stats.md:45, "(d) all three sigma_ZM terciles positive: 1; all four: 0": "all
   four" means all four G5 parts, which the sentence does not say. Fix (StatsCoder or the lead when quoting): "all
   four parts (a)-(d): 0".
7. reports/E.33c_RETURN.md:154-156, the random-walk e80 figures use normal-moment se; the top-10 series have raw
   kurtosis 47 to 696, so their true se is larger and the random-walk e80 is a lower-side figure. The measured
   per-configuration column already covers this. Fix: insert "normal-moment" before "random-walk formula".
8. reports/stage_e33c_briefs/work/D4_verify.md:36 says the comparison read D_stats.json at mtime 20:50; the RETURN
   (line 207) says "read at 20:53" (the compare run). Both are right (file 20:50, read 20:53); no change needed
   beyond NOTE 1.

## Not done, and limits

- I did not re-simulate any configuration from fold predictions; D4 did that (300 of 300 equal), and I checked D4's
  own outputs against the final D_stats.json and P8_select33.json instead.
- P6.2's reported-only statistics (rho, mid-sign hit rate, top decile) are quoted from stats.json by both workers and
  were not recomputed by me (they need the fold predictions and the label store).
- The PBO value itself was not recomputed (program function; report only); I checked the declared set and parameters.
- No test-window data, nothing dated 2024-03-01 or later, no Databento call, nothing under live/ or ops/ was read or
  written. No file outside this review and my scratch folder was written. Times from `date` (PDT): start 21:01:40,
  comparison scripts 21:05-21:13, this file 21:14.
