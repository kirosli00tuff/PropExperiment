# A3 score.py: lead rulings v2 applied (ScoreApplierV2, 2026-10-21)

Script: reports/stage_e28_briefs/work/A3_facts/score.py. Tests: work/A3_facts/test_score.py. Rulings file
A3_lead_rulings_v2.json, sha256 f99b6e9f63de7f22a83838f7f57b193083a68a835eb7f8f235b456751c4f3b1f (full-hash guard,
refuses on mismatch); it inherits A3_lead_rulings.json (v1, sha256 82581c92..., guard unchanged). The v1 table is kept as
A3_ranking_table_v1.json and A3_ranking_table_v1.md (byte copies made before editing, sha256 3213441a... and 769de384...).
A3_ranking_table.json and .md are regenerated: status COMPLETE.

## Code changes
- `load_rulings()` reads both rulings files and returns the v1 parameters plus C1b_override, C6_cap_labels,
  topstep_R_by_size, lucid_fee_u_rule.
- RR-01: `score_layer1(..., c1b_override)` sets C40's C1(b) to high (the override is keyed by blind label; u-flag `C1b:RR-01`).
  QG: C1 2 -> 1, L1 2.100 -> 1.850, fails the Layer 1 gate (L1 < 2.00).
- RR-03: `score_layer1(..., c6_cap_labels)` caps C6 at 2 for the 13 labels C04 C08 C10 C11 C13 C14 C16 C23 C28 C29 C35 C39
  C45 (= MZM XK ZM MZL ZC ZS ZL MZC ZW XW MZS MZW XC, i.e. the 13 grain codes of R_rank.md RR-03; mapping read from
  A3_mask_key.json only, and fixed in the constant `RR03_CAP_LABELS`). `C6_rated` keeps 3. The five equity C6 = 3 stand.
- RR-04: `r_by_size_for()` and `score_layer2(..., r_by_size)`: Topstep's R comes from the blind F03 R_by_size (micro 4,
  non-micro 3) for equity_index and metals; other classes keep the class dict (which is 4 for them). `MICRO_CODES` is the
  reviewer's micro list (rr_score.py).
- RR-05: `lucid_u_rule()`: Lucid's fee is the highest fee for that code at the other four firms (A3_econ.json): QG 4.00,
  QM 5.40. Economics from work/REV_rank/rr_econ_lucidalt.json for the two pairs it holds (QG mu* 0.33 / 1.33, mu10K 0.85;
  QM 0.44 / 1.44, 0.88; cost per attempt unchanged 120.87; the file's sha256 is in the json as lucid_alt_econ_sha256).
  The file has NO other Lucid pair: for every other Lucid pair (A3_econ has rows for 6A 6E CL GC HG M2K MCL MGC MNQ MYM NG NQ RTY SI SIL YM
  ZC ZL ZM ZS ZW) E is A3_econ's, unchanged, flagged `u` "fee" with the text "E from A3_econ unchanged (not
  rerun)", and the u-rule fee is shown (field `fee_rt_usd_u_rule`). A new md section "Lucid fee reading" lists each Lucid
  pair's reading and rank. Their E is therefore optimistic (fee not applied to the simulation).
- New variant `v1_rulings_only` (the four v2 rulings off). The other variants now sit on the new primary.

## Tests
`uv run python -m pytest -q reports/stage_e28_briefs/work/A3_facts/test_score.py`: 117 passed (110 before). One old test
changed (exact-dict equality of load_rulings narrowed to the v1 keys). New tests: v2 load and hash guard; v1_rulings_only
flips exactly the four v2 parameters and the other variants keep them; v1_rulings_only reproduces the v1 ranked list (rank,
firm, code, S, E, R) and Layer 1 gates; RR-01 (QG C1 1, L1 1.85, fails; only QG changes; QG absent from the primary ranking);
RR-03 (13 labels map to the 13 grain codes, C6 3 -> 2, L1 down 0.15, equity 3s stand, others unchanged); RR-04 (micro 4,
non-micro 3, other firms and classes unchanged); RR-05 (u fees 4.00 and 5.40, rerun mu, E lower, non-rerun pairs flagged
with E unchanged, other firms 'sourced', inputs not mutated).

Each ruling run alone on the v1 base reproduces the reviewer's variant (lucid_fee_u_rule: lucid QG 2.386 rank 6, lucid QM
2.353 rank 9; topstep_R_by_size_micro4: topstep MGC 2.275 rank 13, MNQ 2.175 rank 21), and the v1_rulings_only run equals the v1 table.

## One discrepancy with the reviewer's RR-03 numbers
The reviewer's variant OC6_cap_abstract_only_C6 selected codes by the text "abstract only" in the C6 reason, which caught 15
codes (the 13 grains plus M2K and YM). The ruling caps the 13 grains and says the equity ratings stand, so score.py caps 13.
Result: topstep MNQ rank 28 in the reviewer's variant is 30 under RR-03 alone here (MGC 17 and ZM 10 agree).

## Result: new primary (v1 + v2 rulings)
Layer 1 survivors: 19 (v1: 20; the change is QG failing under RR-01). Listed pairs 126, ranked 67 (v1: 71).

| Rank | Pair | S | L1 | L2 |
|---|---|---|---|---|
| 1 | topstep QM | 2.484 | 2.400 | 2.569 |
| 2 | mffu QM | 2.427 | 2.400 | 2.454 |
| 3 | tradeify QM | 2.415 | 2.400 | 2.429 |
| 4 | bulenox QM | 2.388 | 2.400 | 2.375 |
| 5 | lucid QM | 2.353 | 2.400 | 2.306 |
| 6 | topstep ZM | 2.312 | 2.150 | 2.475 |
| 7 | topstep MGC | 2.275 | 2.950 | 1.600 |
| 8 | bulenox MGC | 2.275 | 2.950 | 1.600 |
| 9 | lucid MGC | 2.262 | 2.950 | 1.573 |
| 10 | mffu ZM | 2.250 | 2.150 | 2.349 |

Ranks 7 and 8 tie at S 2.28 (topstep over bulenox by cost per attempt). Lucid MGC (rank 9) carries the "fee" u flag with E
from A3_econ unchanged (not rerun at the u fee), so its rank is not settled; lucid QM (rank 5) uses the reviewer's rerun.
MGC pairs have E 0.0 (known mu > 4 at topstep/bulenox/mffu/tradeify), their S comes from L1 2.95.

MNQ baseline ranks: topstep 14, bulenox 15, tradeify 18, mffu 19, lucid 36 (v1: topstep 33, lucid 41, tradeify 24, mffu 25,
bulenox 21).

Variants (top 1 / MNQ topstep rank / survivors): OC1_off ZM topstep 2.312 / 16 / 13; C4_conservative topstep QM / 17 / 15;
OC2_published topstep QM / 19 / 19; C4_no_transfer topstep QM / 24 / 18; C6_as_rated topstep QM / 13 / 16;
v1_rulings_only topstep QG 2.524 / 33 / 20. Full lists are in A3_ranking_table.md and .json.
