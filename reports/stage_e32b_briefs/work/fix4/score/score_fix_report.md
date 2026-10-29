# F1 ScoreFixer-OpusHigh: RV1 S1, S2, S3, N1, N2 (Stage E.32b wave F, 2026-10-29 08:47-08:56 PDT)

Brief: reports/stage_e32b_briefs/brief_wave_f.md section F1. B = reports/stage_e32b_briefs. Every score, gate and rank
is unchanged between the 05:40:30 run and the rerun (step 5). Pre-edit copies of every file I changed are in
B/work/fix4/score/ (*.pre.py, econ_README.pre.md, ranking_pre.md, rankmd_pre/ with the template, scripts and out/).

## 1. Market-case field check (before any edit)

`cost_per_attempt_mkt_mu0` is present and non-null in every block the scorer reads:
- econ32b.json (current file, e5673466...): primary 112/112, spread1 112/112, E_dir60 112/112.
- econ32b_smean.json (dff37bc9...): primary 4/4, spread1 4/4, E_dir60 4/4. These blocks reach the scorer as RL-SMEAN
  patches in work/score/lead_variants.json, which carry the field too.
- Not present in the pairs' `inputs` records (these are not econ blocks) or in the 15 nested E_dir.{30,120,240} blocks,
  which the scorer does not read.

## 2. Code changes

B/work/score/s32b_layer2.py
- lines 42-45 (`e_score`): the tie-break cost is now `cost_per_attempt_mkt_mu0` (market case) and no longer
  `cost_per_attempt`. A missing market field gives None (the tie level counts it as infinite, as before), never a
  silent fallback to the limit case.
- lines 49-51: new `cost_lim(block)` returns the limit-case `cost_per_attempt` (reported, not ranked).
- lines 161-164, 199: `pair_row` writes `cost_per_attempt` (market) and `cost_per_attempt_lim` (limit) side by side.
  The 5 NQ rows (excluded, V49) carry neither field, as before. `__all__` (209-210) adds cost_lim.

B/work/score/score32b.py
- line 110: `validate` appends `unconfirmed_searches(econ)` to the soft checks.
- lines 114-141: new `_econ_search_blocks` (each block with a `search` record, nested E_dir.<h> included, `inputs`
  excluded) and `unconfirmed_searches`, which writes one input check per search with `confirmed` != true: pair, block,
  search name, confirmed value, recorded value, k_bisection, and the number of violations out of n_checked.
- lines 315-317 (`run_all`): an econ block patched in by a lead ruling is scanned too. Any new unconfirmed search is
  listed as "ruling <name> (patched econ): ...". There is none in the real run.
- rank_key (line 144 before the edit, now def at 171, cost at 175) is unchanged. It reads row["cost_per_attempt"], which is now the
  market value.

## 3. Tests

- test_score32b_rules.py: `_blk` (line 226) also carries `cost_per_attempt_mkt_mu0`. New tests:
  `test_e_score_tie_cost_is_market_case_and_limit_case_is_reported_beside` (239) uses topstep|M6A's real values
  98.82 / 202.80; `test_e_score_missing_market_cost_is_none_not_the_limit_case` (246).
- test_score32b_run.py: new tests `test_pair_row_ranks_on_market_cost_and_carries_limit_cost` (205; the market and
  limit cases order a cost-level tie in opposite ways), `test_unconfirmed_econ_searches_listed_in_input_checks` (223;
  includes a nested E_dir.30 block and checks that a confirmed search is not listed), and
  `test_unconfirmed_search_in_a_ruling_patch_is_listed_with_the_ruling` (237). The E_dir60 allowed-change set (293)
  adds cost_per_attempt_lim.
- `uv run pytest -q reports/stage_e32b_briefs/work/score/`: **178 passed** (173 before: 172 passed and 1 failed,
  test_e_score_formula_and_ends, until `_blk` carried the market field). Red check: in a scratch copy with the
  pre-edit layer2 and score32b, the 3 new run tests fail and the rules file fails to import cost_lim.
- ruff: only E501 (line length; the house style uses 120 columns) increases. There are no new non-E501 findings.

## 4. Rerun (score_run3.log)

- Run 2 copied with timestamps kept: B/work/score/score32b_out_run2.json (sha256 70809d501bf316c1...) and .md
  (8bf2ddeb5579331e...). The run1 files are untouched.
- Command, in B/work/score/score_run3.log: score32b.py with --f3 F3_vol.json, --f4 F4_facts_unmasked.json, --blind
  F4_blind_unmasked.json, --econ econ32b.json, --attention work/F5run/F2_attention_listcodes.json, --data-access
  F2_data_access.json, --rulings work/score/lead_variants.json, the default --e28, and --out/--md B/score32b_out.*.
  All non-econ input hashes equal the 05:40:30 run's inputs record (F3 9ba14d56, F4 4a4d1e29, blind aeae3296,
  attention 7ae497c0, data access 4bad06bd, rulings 6d32a1fd). Spec 09ebe697...8635.
- **econ32b.json: 05:40:30 run 0567890e5a6f94ca6368d025ed6253dc30453830902e051faf6541260dbe50bb; rerun (file
  rewritten 07:27:59 by econ pass 2's collect) e56734663dd7ef083462595636e0e6b20c28954e62add436a56b0483bbd54e4c.**
- Run 3 ended 08:51:03 PDT, rc 0: survivors 35, ranked 103, the same top 5 and MNQ ranks, lead notes 25, input checks 55
  (47 + 8 new). New outputs: score32b_out.json ee74c6a0aa508ae9..., score32b_out.md 5f319e9c86627420....

## 5. Diff run 2 against run 3 (B/work/fix4/score/diff_score.py, result diff_score_out.json)

- Full recursive diff: 266 differing paths, all allowed: cost_per_attempt_lim 230 (new key, every non-NQ pair),
  cost_per_attempt 33, input_checks 1, inputs 1 (the econ hash), generated_pdt 1. **Unexpected: 0.**
- Named checks, all equal. 235 pairs in the same order, with no mismatch in S, S_rounded, L1, L2, E, R, A, D, Rel, P,
  m_star, m10K, status, gate_reasons, rank, econ_block, room_a or room_b. 47 Layer 1 rows identical. The 21 ties,
  including decided_by, are equal, as are top 5, top 15, MNQ ranks, survivors, n_ranked, L1_below_2, f5_handoff,
  moves_vs_e28 and for_lead. All 28 variant summaries are identical.
- Cost: on all 103 ranked pairs, run 2's cost equals run 3's cost_per_attempt_lim, and 31 of them differ from the market
  value. The two cost-decided ties keep their order: tradeify|M6A over topstep|M6A at 94/95 (market 95.833 < 98.817)
  and tradeify|M6E over topstep|M6E at 101/102 (95.833 < 98.347).
- The .md differs only in the header time and the 8 new input-check lines.

## 6. Ranking file rebuild (reports/stage_e32b_ranking.md)

Rebuilt with the RankingWriter's own sequence: make_rankmd.py, extra_frags.py (its sat1 self-check passed: "ok 112"),
then assemble.py (980 lines, sha256 eaae17b4...). Pre-rebuild copy: B/work/fix4/score/ranking_pre.md. Diffs:
ranking_rebuild.diff and ranking_rebuild.udiff (115 lines out, 128 in).

| ranking.md lines (new) | template.md lines (new) | change |
|---|---|---|
| 3 | (the {{NOW}} placeholder) | assembly time 08:53 PDT |
| 8-11 | 8-11 | new sentence: wave F rerun at 08:51:03, run 2 kept, what differs (see deviation a) |
| 18 | 18 | N2: econ32b.json e5673466... (rewritten 07:27:59 by pass 2's collect); the 05:40:30 run read 0567890e... |
| 65-68 | 65-68 | S2: the brief's replacement text, introduced as "The lead's reading, as corrected by review RV1 S2" |
| 73-75 | 73-75 | input checks 47 -> 55; added "The other 8 are the unconfirmed econ searches..." (see deviation b) |
| 255-368 | 108-115 + sec3a | S1 and S3: the 3a notes say the tie-break cost is the market case, with the limit case beside it; the two cost-decided ties under both values; the econ note on bulenox CL/NG (confirmed false, k_final, mu* 1.76 and mu10K 2.44 ticks, equal to E.28's, E right). The table has two columns, "tie-break cost/attempt USD (market case)" and "cost/attempt USD (limit case, reported)" |
| 569 | 134 | N1: D3 3.51 -> 3.50. I recomputed all 13 means at 2 decimals (half-up) and only D3 differed (exact 3.5049) |

Table 3a check: 103 rows, no cell outside the cost columns changed, and the old cost column equals the new limit-case
column in every row. The market column shows a different whole-dollar value in 19 rows. The other fragments (2a, 2b,
2c, 3b, 3c, 4, 5, 6, 7q, 7u) are byte-identical. facts.json differs only in the econ hash and score_generated.
Every other sentence, including the lead-ruling text, is unchanged.

To produce the two cost columns I edited make_rankmd.py lines 145-149, which the brief cited (B/work/rankmd/ is in the
write list).

## 7. Econ README (B/work/econ/README.md)

Lines 185-189 are a new dated note under line 184. Line 184 itself is not rewritten. The note says the real pass 1 had
two pairs with unconfirmed searches (bulenox|CL and bulenox|NG, primary and spread1, both searches), that the recorded
values are k_final (1.76 and 2.44, equal to E.28's), and that score32b.py now lists such searches.

## 8. Stage files that record score32b_out.json's sha256 or read cost_per_attempt from it (not changed)

The 05:40:30 sha256 70809d501bf316c1... is recorded in:
- B/R2_combinations.json, B/R2_combinations_unrated.json, B/R2_combinations_unrated_q6p.json
- B/work/R2/R2_combinations_v1.json, R2_combinations_nozlw.json, R2_combinations_ts150_v2.json,
  R2_combinations_q3only.json, R2_combinations_q3bleg.json, R2_combinations_topstep150.json, combos_detail.json,
  groundwork.json
- reports/stage_e32b_recommendations.md line 880 (input hash table)

These come from scripts that read score32b_out.json: B/work/R2/r2_common.py (SCORE_PATH), build_groundwork.py and
build_combos.py. They record its hash as metadata and do not refuse on a mismatch. None of them reads
cost_per_attempt. Their "cost" fields are data costs, and build_combos' "c_lim" is a queue-limit variant unrelated to
this field.

Files that read cost_per_attempt from score32b_out.json: reports/stage_e32b_ranking.md (table 3a, rebuilt here; via
work/rankmd/make_rankmd.py) and work/rankmd/extra_frags.py:41 (the sat1 tie chain; it now gets the market value and
its self-check against the score run's sat1 output passed). In B/work/F5run, econ_stub_layer1only.json,
score_stub_layer1only.json and make_econ_stub.py use cost_per_attempt (a stub set to 0) but do not read
score32b_out.json. B/work/F5 and B/work/scope have no hits.

## Deviations and items for the lead

a. Header (ranking.md 8-11): the file is now built from the 08:51:03 rerun, so I added one sentence saying so. The
   original sentence ("built from the score run of 05:40:30") is kept unchanged.
b. The "Data-access encoding" bullet said the score run has 47 input checks. The rerun has 55, so I changed the count
   and added one sentence on the other 8. This edit goes beyond the brief's list; without it the count would be wrong.
c. Not in my write list, so not changed: work/score/SCHEMA.md section 4 (it still says the cost tie level reads
   `cost_per_attempt` and does not mention `cost_per_attempt_mkt_mu0`, `cost_per_attempt_lim` or the unconfirmed
   check); work/score/README.md ("tests (159)"); work/score/make_fixture.py (the synthetic fixture has no market
   field, so on the fixture the cost tie level is None, i.e. infinite, for every pair; the new tests set the field
   themselves); and the fixture dry-run outputs (fixture_out.*, not rerun).
d. Downstream files in section 8 record the old score-output hash. The scores they use are unchanged.

## Follow-up (session 4, lead message after the first return; 08:56 PDT)

The lead accepted deviations a and b and the make_rankmd.py edit. The four leftovers from item c are done.
Pre-edit copies are in B/work/fix4/score/followup_pre/.
1. work/score/SCHEMA.md lines 90-100: a dated "Session 4 note" under section 4; the old text is kept. It covers the tie
   level reading `cost_per_attempt_mkt_mu0` (market case), `cost_per_attempt_lim` reported beside it, no
   fallback when the field is missing, and the `input_checks` entries for searches with confirmed not true (ruling
   patches included; 8 entries in the real run).
2. work/score/README.md line 8: the test count is now 178 (since session 4). Lines 17-18: the real runs read
   work/F5run/F2_attention_listcodes.json (LR-ATT), not the B/F2_attention.json the command shows.
3. work/score/make_fixture.py `_block`: the synthetic blocks carry `cost_per_attempt_mkt_mu0` (15 + 50 x firm
   offset, below the limit case's 20 + 100 x offset, so the firms keep the same order; 30 for the above-cap MZM block).
   I reran make_fixture.py and dry_run.py, which write only fixture/*.json, fixture_out.json and fixture_out.md.
   Only fixture/econ32b.json changed among the fixture inputs. fixture_out.json has 57 differing paths, all in
   allowed fields (cost_per_attempt 24, cost_per_attempt_lim 30, generated_pdt 2, inputs 1); no score, rank or tie
   changed (dry run: 6 survivors, 16 ranked, 1 tie, 11 variants).
4. `uv run pytest -q reports/stage_e32b_briefs/work/score/`: **178 passed**, both before and after the fixture change.
