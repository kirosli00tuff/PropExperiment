# Stage E.33 B5 synthetic search proofs (P4.2)

Written 2026-10-28 07:44:01 PDT by run_proofs33.py from /mnt/large-storage/market_data/PropExperiment/derived/e33/proofs. Thresholds at N = 838 (P4.2: the expected N; if the registered N differs the proofs are not rerun). Configurations: S5 x {F15, T30} x 10 grid points (20 per seed, 120 fits). Plant: F3_4, beta = 0.367 ticks per minute per unit (synth33; oracle calibration in ProofCoder_calibration.json). The plant is the only source of signal; under it the past-path features (F4, F2_7) carry derived momentum, so F4 weight in a planted fold model is not a leak (ProofReview N1). The oracle (P3.5 with the true class probabilities and class-level means) is a calibration anchor, not a ceiling: P3.5 is not Bayes-optimal, so a fitted configuration can exceed it (ProofReview N3).

Code sha256 (run manifest): `{"cal33.py": "f054788ee5ca361cec4421674a331f1837acea6c86273b4f3ee30824045bc9b0", "data33.py": "8295a6ee26e5514cde23927e4a0649f8ceb9ab211e77cad167b60b6b403005fc", "guard33.py": "782929fed0141318c0791e970056cc2c7f2059106064da1a30417394ba5cc297", "p7_final.py": "3db06f1276bf949529cb8b0d5f3e07c3d155db13fdb819666a7c51377385e828", "p7_thresholds.py": "5d3590197bbc19ea2c48070910509f7fe976524ec39b9ad41e65af148b22d219", "run_proofs33.py": "4a0f4e9825cd7880ea784e3910073ccf18eb80929e6f10c636799c61a3268698", "run_search33.py": "d44fb7c16e5589e99e6061c9ada3a4d9af3cdf0a2b2a2bc2d15fa909a80efbc3", "search33.py": "a7d30b2a6786bd1437794b9cdbd504c8945a4887b6161c65973f9befaec6676f", "select33.py": "9b9928066a352dc324c14c46b92749f1953cf753d389d57f4c086511214d576b", "synth33.py": "5a5ed5b91f090aeab46dbba539ff88f487febf9207d6081f3ce72289ee8eba30"}`
Engine PIPELINE_SHA (manifest): `323a82ff96cabbd509ba2c8dc358dcf50c3aa09cee8a22fbc2e57285739e7b64`; versions (manifest): `{"lightgbm": "4.7.0", "numpy": "2.5.3", "pandas": "3.0.5", "pyarrow": "25.0.1", "python": "3.12.13", "scipy": "1.18.1", "sklearn": "1.9.1", "uv_lock_sha256": "7fecbfa47327208882aa67d8141994187a597f325bdcbb17cbb2d7eb6cdb459d"}`
run_proofs33.py that wrote this summary: `4a0f4e9825cd7880ea784e3910073ccf18eb80929e6f10c636799c61a3268698`
Starts (manifest): 2026-10-28 02:36:25 PDT seeds [1, 101, 2, 102, 3, 103, 4, 104, 5, 105, 6, 106, 7, 107, 8, 108, 9, 109, 10, 110, 11, 111, 12, 112, 13, 113, 14, 114, 15, 115, 16, 116, 17, 117, 18, 118, 19, 119, 20, 120]

Columns: Tier A members; failed fits = configurations that failed (P5; they fail G1 and have no series); the best configuration over all 20 (P8 total order, gates ignored) and its SR_d; the funnel in order G1 / G1..G2 / ... / G1..G5 (and each gate alone); search wall minutes.
Counting rule (ProofReview SF1): a seed with any failed configuration is never a clean empty Tier A. Null: it counts against the proof together with the seeds whose Tier A is non-empty. Planted: it does not count toward the pass count, even with Tier A non-empty. Both raw counts are printed.

## Null seeds

| seed | Tier A | failed | best | best SR_d | funnel | search min |
|---|---|---|---|---|---|---|
| 1 | - | failed fits: 0 | S5F15L010E | 0.0081 | 7 / 0 / 0 / 0 / 0 (alone 7 / 1 / 0 / 0 / 0) | 11.8 |
| 2 | - | failed fits: 0 | S5F15G2050 | 0.0112 | 9 / 0 / 0 / 0 / 0 (alone 9 / 1 / 0 / 0 / 0) | 12.7 |
| 3 | - | failed fits: 0 | S5F15G2050 | 0.0602 | 9 / 0 / 0 / 0 / 0 (alone 9 / 1 / 0 / 0 / 0) | 7.5 |
| 4 | - | failed fits: 0 | S5F15L001A | -0.0757 | 5 / 0 / 0 / 0 / 0 (alone 5 / 0 / 0 / 0 / 0) | 8.4 |
| 5 | - | failed fits: 0 | S5F15G3200 | 0.0182 | 10 / 0 / 0 / 0 / 0 (alone 10 / 1 / 0 / 0 / 0) | 7.0 |
| 6 | - | failed fits: 0 | S5F15G2200 | -0.0058 | 9 / 0 / 0 / 0 / 0 (alone 9 / 0 / 0 / 0 / 0) | 7.1 |
| 7 | - | failed fits: 0 | S5F15G2050 | 0.0397 | 7 / 0 / 0 / 0 / 0 (alone 7 / 1 / 0 / 0 / 0) | 8.3 |
| 8 | - | failed fits: 0 | S5F15L010E | -0.0577 | 10 / 0 / 0 / 0 / 0 (alone 10 / 0 / 0 / 0 / 0) | 7.8 |
| 9 | - | failed fits: 0 | S5F15G2200 | 0.0293 | 10 / 0 / 0 / 0 / 0 (alone 10 / 4 / 0 / 0 / 0) | 8.8 |
| 10 | - | failed fits: 0 | S5F15G3200 | 0.0318 | 5 / 0 / 0 / 0 / 0 (alone 5 / 2 / 0 / 0 / 0) | 7.9 |
| 11 | - | failed fits: 0 | S5F15L010E | -0.0409 | 7 / 0 / 0 / 0 / 0 (alone 7 / 0 / 0 / 0 / 0) | 7.3 |
| 12 | - | failed fits: 0 | S5F15L100A | -0.0259 | 5 / 0 / 0 / 0 / 0 (alone 5 / 0 / 0 / 0 / 0) | 8.1 |
| 13 | - | failed fits: 0 | S5F15L010E | 0.0086 | 10 / 0 / 0 / 0 / 0 (alone 10 / 1 / 0 / 0 / 0) | 7.9 |
| 14 | - | failed fits: 0 | S5F15L010E | -0.0413 | 9 / 0 / 0 / 0 / 0 (alone 9 / 0 / 0 / 0 / 0) | 7.3 |
| 15 | - | failed fits: 0 | S5F15G3200 | -0.0317 | 9 / 0 / 0 / 0 / 0 (alone 9 / 0 / 0 / 0 / 0) | 7.5 |
| 16 | - | failed fits: 0 | S5T30L001E | -0.0085 | 9 / 0 / 0 / 0 / 0 (alone 9 / 0 / 0 / 0 / 0) | 8.5 |
| 17 | - | failed fits: 0 | S5F15G3050 | 0.0203 | 9 / 0 / 0 / 0 / 0 (alone 9 / 2 / 0 / 0 / 0) | 8.0 |
| 18 | - | failed fits: 0 | S5F15L010E | 0.0034 | 5 / 0 / 0 / 0 / 0 (alone 5 / 0 / 0 / 0 / 0) | 8.4 |
| 19 | not run | | | | |
| 20 | not run | | | | |

- Seeds run: 18 of 20. Tier A non-empty: 0; seeds with any failed configuration: 0; counted against the null proof (either): 0 (P4.2 criterion: the null proof fails at 2 or more of 20).
- Seeds with at least one failed configuration (P5): 0.
- Best SR_d over seeds: min -0.0757, median 0.0058, max 0.0602; values [-0.0757, -0.0577, -0.0413, -0.0409, -0.0317, -0.0259, -0.0085, -0.0058, 0.0034, 0.0081, 0.0086, 0.0112, 0.0182, 0.0203, 0.0293, 0.0318, 0.0397, 0.0602].
- SD of the null daily Sharpes centred on each configuration's mean: 0.0425 (df-corrected 0.0437) over 360 (all series; 29 constant no-trade series count as 0) and 0.0433 (df-corrected 0.0446) over 330 non-constant series; reference 1/sqrt(796) = 0.0354 (0.0345 for the uncorrected centred SD over 20 seeds).

## Planted seeds

| seed | Tier A | failed | best | best SR_d | oracle SR_d (F15) | funnel | search min |
|---|---|---|---|---|---|---|---|
| 101 | S5F15L001E, S5F15L100A | failed fits: 0 | S5F15L001E | 0.3531 | 0.3286 | 20 / 10 / 10 / 10 / 10 (alone 20 / 10 / 10 / 10 / 10) | 14.3 |
| 102 | S5F15L001E, S5F15G3200, S5F15L100A | failed fits: 0 | S5F15L001E | 0.3155 | 0.3331 | 20 / 13 / 10 / 10 / 10 (alone 20 / 13 / 10 / 10 / 12) | 15.8 |
| 103 | S5F15L001E, S5F15G2050, S5F15L001A | failed fits: 0 | S5F15L001E | 0.3098 | 0.2953 | 20 / 10 / 10 / 8 / 8 (alone 20 / 10 / 10 / 8 / 10) | 8.2 |
| 104 | S5F15L001E, S5F15L010E, S5F15G3200 | failed fits: 0 | S5F15L001E | 0.3454 | 0.3480 | 20 / 10 / 10 / 10 / 10 (alone 20 / 10 / 10 / 10 / 10) | 8.6 |
| 105 | S5F15G3200, S5F15L010E | failed fits: 0 | S5F15G3200 | 0.3855 | 0.4013 | 20 / 14 / 10 / 10 / 10 (alone 20 / 14 / 10 / 10 / 12) | 8.3 |
| 106 | S5F15L001E, S5F15L001A, S5F15G2050 | failed fits: 0 | S5F15L001E | 0.3103 | 0.2940 | 20 / 10 / 10 / 10 / 10 (alone 20 / 10 / 10 / 10 / 10) | 8.0 |
| 107 | S5F15L001E, S5F15G2200, S5F15L010A | failed fits: 0 | S5F15L001E | 0.3264 | 0.3037 | 20 / 11 / 10 / 10 / 10 (alone 20 / 11 / 10 / 10 / 11) | 8.7 |
| 108 | S5F15L001E, S5F15L001A, S5F15G2200 | failed fits: 0 | S5F15L001E | 0.3953 | 0.3834 | 20 / 11 / 10 / 10 / 10 (alone 20 / 11 / 10 / 10 / 11) | 6.6 |
| 109 | S5F15L001E, S5F15L001A, S5F15G2200 | failed fits: 0 | S5F15L001E | 0.3865 | 0.3239 | 20 / 11 / 10 / 10 / 10 (alone 20 / 11 / 10 / 10 / 11) | 8.1 |
| 110 | S5F15L001E, S5F15L001A, S5F15G3050 | failed fits: 0 | S5F15L001E | 0.4072 | 0.3970 | 20 / 11 / 10 / 10 / 10 (alone 20 / 11 / 10 / 10 / 11) | 7.3 |
| 111 | S5F15L001E, S5F15L100A | failed fits: 0 | S5F15L001E | 0.3739 | 0.3370 | 20 / 11 / 7 / 6 / 6 (alone 20 / 11 / 7 / 6 / 11) | 7.9 |
| 112 | S5F15L001E, S5F15L100E, S5F15G2050 | failed fits: 0 | S5F15L001E | 0.3878 | 0.3791 | 20 / 11 / 10 / 10 / 10 (alone 20 / 11 / 10 / 10 / 11) | 7.6 |
| 113 | S5F15G2050, S5F15L001E, S5F15L100A | failed fits: 0 | S5F15G2050 | 0.3750 | 0.3666 | 20 / 13 / 10 / 10 / 10 (alone 20 / 13 / 10 / 10 / 13) | 7.4 |
| 114 | S5F15L001E, S5F15G2050, S5F15L010E | failed fits: 0 | S5F15L001E | 0.3620 | 0.2741 | 20 / 11 / 10 / 10 / 10 (alone 20 / 11 / 10 / 10 / 11) | 6.8 |
| 115 | S5F15L001E, S5F15L100A, S5F15G3200 | failed fits: 0 | S5F15L001E | 0.3964 | 0.3474 | 20 / 13 / 10 / 10 / 10 (alone 20 / 13 / 10 / 10 / 11) | 8.3 |
| 116 | S5F15L001E, S5F15G3050, S5F15L100E | failed fits: 0 | S5F15L001E | 0.3557 | 0.3411 | 20 / 11 / 10 / 10 / 10 (alone 20 / 11 / 10 / 10 / 11) | 7.8 |
| 117 | S5F15L001E, S5F15G2050 | failed fits: 0 | S5F15L001E | 0.4050 | 0.4001 | 20 / 15 / 10 / 10 / 10 (alone 20 / 15 / 10 / 10 / 15) | 8.1 |
| 118 | S5F15L001E, S5F15L001A, S5F15G3200 | failed fits: 0 | S5F15L001E | 0.3575 | 0.3289 | 20 / 13 / 10 / 10 / 10 (alone 20 / 13 / 10 / 10 / 12) | 7.0 |
| 119 | not run | | | | | |
| 120 | not run | | | | | |

- Seeds run: 18 of 20. Tier A non-empty: 18; seeds with any failed configuration: 0; pass count (Tier A non-empty and no failed configuration): 18 (P4.2 criterion: passes at 14 or more of 20).
- Seeds with at least one failed configuration (P5): 0.
- Oracle SR_d at F15 on the seeds' own series: mean 0.3435 (calibrated target 0.35 in expectation).
- Seeds in which each configuration entered Tier A: S5F15L001A 6, S5F15L001E 17, S5F15L010A 1, S5F15L010E 3, S5F15L100A 5, S5F15L100E 2, S5F15G2050 6, S5F15G2200 3, S5F15G3050 2, S5F15G3200 5, S5T30L001A 0, S5T30L001E 0, S5T30L010A 0, S5T30L010E 0, S5T30L100A 0, S5T30L100E 0, S5T30G2050 0, S5T30G2200 0, S5T30G3050 0, S5T30G3200 0

