# Stage E.31 ZM pilot: statistics and kill rule

Generated 2026-10-23 12:46:58 PDT by stats31.py from reports/stage_e31_briefs/work/pilot/runs/measure31: 816 trade dates with a done marker (2020-12-01 to 2024-02-29); expected dates 816 (sha256 a97ba35a937ce2f4...); folders without a marker: 0. Inputs sha256 47a553ef01305c62... over 3264 files. Bootstrap: 2000 replicates, seed 31, unit trade date (all done trade dates; one draw matrix for every statistic). Intervals are 95% two-sided percentile intervals; labels: positive (lower bound > 0), negative (upper bound < 0), not distinguishable from 0. Units: ticks of 0.10 USD/short ton (10.00 USD).

## Verdict: FAIL

Primary population (spec 7, v2): ZM.v.0, DAY session, model (c), buy and sell pooled, after all exclusions. ZM fails if any test holds; K1 holds if either variant's bound is not above 0. Nothing else decides.

| test | statistic | value | rule | result |
|---|---|---|---|---|
| K1 (dropping markout) | lower 95% bound of mean N_10(Topstep) = E_10 - 0.264 | lower bound -1.2524; mean -1.2339 [-1.2524, -1.2142] negative over 44045 fills with a valid 10 s markout (0 without) | holds if not above 0 | **holds** |
| K1 (no-drop markout) | lower 95% bound of mean N_10(Topstep) = E_10 - 0.264 | lower bound -1.2524; mean -1.2339 [-1.2524, -1.2142] negative over 44045 fills with a valid 10 s markout (0 without) | holds if not above 0 | **holds** |
| K2 | model (c) fills of the population, before any markout drop | 44045 | holds if < 400 | does not hold |
| K3 | mean loop round trips per DAY trade date, model (c) | 111.5681; interval 111.5681 [109.5533, 113.4611] over 764 DAY trade dates | holds if < 20 | does not hold |

Information only (decides nothing; a PASS whose K1 would hold here is labelled "PASS, fragile (fee reading)"):

- K1 (dropping markout) with the full round-trip fee on every fill (E_10 - 0.528): lower bound -1.5164; mean -1.4979 [-1.5164, -1.4782] negative.
- K1 (no-drop markout) with the full round-trip fee on every fill (E_10 - 0.528): lower bound -1.5164; mean -1.4979 [-1.5164, -1.4782] negative.

## Primary population, the three models side by side (ZM.v.0, DAY, sides pooled)

| statistic | (a) K | (b) FIFO back of queue | (c) trade-through (gate) |
|---|---|---|---|
| placements | 85568 | 85568 | 85568 |
| fills (of which in the 50 ms cancel latency) | 60216 (33) | 61078 (27) | 44045 (46) |
| fills by trigger | queue 46930, through 13286 | queue 48897, through 12181 | queue 0, through 44045 |
| fill rate | 0.7037 [0.6992, 0.7079] | 0.7138 [0.7093, 0.7180] | 0.5147 [0.5090, 0.5201] |
| touch rate | 0.8047 [0.8013, 0.8081] | 0.8047 [0.8013, 0.8081] | 0.8047 [0.8013, 0.8081] |
| stale share (best price at g differs from j) | 0.0625 [0.0598, 0.0652] | 0.0625 [0.0598, 0.0652] | 0.0625 [0.0598, 0.0652] |
| KM P(fill by 1 s) | 0.0626 [0.0605, 0.0648] | 0.0663 [0.0639, 0.0686] | 0.0271 [0.0258, 0.0285] |
| KM P(fill by 10 s) | 0.3668 [0.3611, 0.3723] | 0.3861 [0.3804, 0.3917] | 0.2009 [0.1962, 0.2052] |
| KM P(fill by 60 s) | 0.7033 [0.6988, 0.7075] | 0.7135 [0.7090, 0.7177] | 0.5142 [0.5085, 0.5196] |
| KM median time to fill (s) | 19.831 | 17.962 | 55.937 |
| KM censored before 60 s | 0 | 0 | 0 |
| mean c_half, all fills (ticks) | 0.3414 [0.3350, 0.3477] positive | 0.3594 [0.3536, 0.3651] positive | -0.4251 [-0.4317, -0.4185] negative |
| median c_half, all fills | 0.5000 | 0.5000 | -0.5000 |
| 1 s: fills with E_h (dropped) | 60216 (0) | 61078 (0) | 44045 (0) |
| 1 s: mean markout (ticks) | -0.6142 [-0.6232, -0.6049] negative | -0.5964 [-0.6052, -0.5871] negative | -0.5285 [-0.5406, -0.5154] negative |
| 1 s: median markout | -0.5000 | -0.5000 | -0.5000 |
| 1 s: mean c_half on these fills | 0.3414 [0.3350, 0.3477] positive | 0.3594 [0.3536, 0.3651] positive | -0.4251 [-0.4317, -0.4185] negative |
| 1 s: mean E_h | -0.2728 [-0.2839, -0.2620] negative | -0.2370 [-0.2471, -0.2264] negative | -0.9536 [-0.9664, -0.9406] negative |
| 1 s: median E_h | 0.0000 | 0.0000 | -1.0000 |
| 1 s: share E_h > 0 | 0.2754 [0.2707, 0.2806] | 0.2868 [0.2821, 0.2919] | 0.0527 [0.0506, 0.0549] |
| 1 s: mean N_h(Topstep) | -0.5368 [-0.5479, -0.5260] negative | -0.5010 [-0.5111, -0.4904] negative | -1.2176 [-1.2304, -1.2046] negative |
| 1 s: median N_h(Topstep) | -0.2640 | -0.2640 | -1.2640 |
| 1 s: VPO_h(Topstep) per resting order | -0.3778 [-0.3856, -0.3700] negative | -0.3576 [-0.3651, -0.3498] negative | -0.6267 [-0.6370, -0.6158] negative |
| 1 s no-drop: fills with E_h (dropped) | 60216 (0) | 61078 (0) | 44045 (0) |
| 1 s no-drop: mean E_h | -0.2728 [-0.2839, -0.2620] negative | -0.2370 [-0.2471, -0.2264] negative | -0.9536 [-0.9664, -0.9406] negative |
| 1 s no-drop: mean N_h(Topstep) | -0.5368 [-0.5479, -0.5260] negative | -0.5010 [-0.5111, -0.4904] negative | -1.2176 [-1.2304, -1.2046] negative |
| 1 s no-drop: VPO_h(Topstep) | -0.3778 [-0.3856, -0.3700] negative | -0.3576 [-0.3651, -0.3498] negative | -0.6267 [-0.6370, -0.6158] negative |
| 10 s: fills with E_h (dropped) | 60216 (0) | 61078 (0) | 44045 (0) |
| 10 s: mean markout (ticks) | -0.6286 [-0.6425, -0.6157] negative | -0.6114 [-0.6248, -0.5981] negative | -0.5448 [-0.5633, -0.5256] negative |
| 10 s: median markout | -0.5000 | -0.5000 | -0.5000 |
| 10 s: mean c_half on these fills | 0.3414 [0.3350, 0.3477] positive | 0.3594 [0.3536, 0.3651] positive | -0.4251 [-0.4317, -0.4185] negative |
| 10 s: mean E_h | -0.2872 [-0.3031, -0.2728] negative | -0.2519 [-0.2665, -0.2385] negative | -0.9699 [-0.9884, -0.9502] negative |
| 10 s: median E_h | 0.0000 | 0.0000 | -1.0000 |
| 10 s: share E_h > 0 | 0.3732 [0.3687, 0.3779] | 0.3830 [0.3784, 0.3878] | 0.1877 [0.1838, 0.1915] |
| 10 s: mean N_h(Topstep) | -0.5512 [-0.5671, -0.5368] negative | -0.5159 [-0.5305, -0.5025] negative | -1.2339 [-1.2524, -1.2142] negative |
| 10 s: median N_h(Topstep) | -0.2640 | -0.2640 | -1.2640 |
| 10 s: VPO_h(Topstep) per resting order | -0.3879 [-0.3992, -0.3778] negative | -0.3683 [-0.3789, -0.3584] negative | -0.6351 [-0.6475, -0.6222] negative |
| 10 s no-drop: fills with E_h (dropped) | 60216 (0) | 61078 (0) | 44045 (0) |
| 10 s no-drop: mean E_h | -0.2872 [-0.3031, -0.2728] negative | -0.2519 [-0.2665, -0.2385] negative | -0.9699 [-0.9884, -0.9502] negative |
| 10 s no-drop: mean N_h(Topstep) | -0.5512 [-0.5671, -0.5368] negative | -0.5159 [-0.5305, -0.5025] negative | -1.2339 [-1.2524, -1.2142] negative |
| 10 s no-drop: VPO_h(Topstep) | -0.3879 [-0.3992, -0.3778] negative | -0.3683 [-0.3789, -0.3584] negative | -0.6351 [-0.6475, -0.6222] negative |
| 60 s: fills with E_h (dropped) | 60216 (0) | 61078 (0) | 44045 (0) |
| 60 s: mean markout (ticks) | -0.6314 [-0.6515, -0.6108] negative | -0.6123 [-0.6320, -0.5918] negative | -0.5539 [-0.5833, -0.5244] negative |
| 60 s: median markout | -0.5000 | -0.5000 | -0.5000 |
| 60 s: mean c_half on these fills | 0.3414 [0.3350, 0.3477] positive | 0.3594 [0.3536, 0.3651] positive | -0.4251 [-0.4317, -0.4185] negative |
| 60 s: mean E_h | -0.2900 [-0.3110, -0.2680] negative | -0.2529 [-0.2732, -0.2321] negative | -0.9789 [-1.0086, -0.9491] negative |
| 60 s: median E_h | -0.5000 | 0.0000 | -1.0000 |
| 60 s: share E_h > 0 | 0.4405 [0.4372, 0.4439] | 0.4459 [0.4428, 0.4493] | 0.3413 [0.3370, 0.3455] |
| 60 s: mean N_h(Topstep) | -0.5540 [-0.5750, -0.5320] negative | -0.5169 [-0.5372, -0.4961] negative | -1.2429 [-1.2726, -1.2131] negative |
| 60 s: median N_h(Topstep) | -0.7640 | -0.2640 | -1.2640 |
| 60 s: VPO_h(Topstep) per resting order | -0.3899 [-0.4043, -0.3750] negative | -0.3690 [-0.3832, -0.3540] negative | -0.6398 [-0.6564, -0.6220] negative |
| 60 s no-drop: fills with E_h (dropped) | 60216 (0) | 61078 (0) | 44045 (0) |
| 60 s no-drop: mean E_h | -0.2900 [-0.3110, -0.2680] negative | -0.2529 [-0.2732, -0.2321] negative | -0.9789 [-1.0086, -0.9491] negative |
| 60 s no-drop: mean N_h(Topstep) | -0.5540 [-0.5750, -0.5320] negative | -0.5169 [-0.5372, -0.4961] negative | -1.2429 [-1.2726, -1.2131] negative |
| 60 s no-drop: VPO_h(Topstep) | -0.3899 [-0.4043, -0.3750] negative | -0.3690 [-0.3832, -0.3540] negative | -0.6398 [-0.6564, -0.6220] negative |

## Net results for the five firms (ZM.v.0, DAY, sides pooled)

Mean N_h(firm) = E_h - fee per fill over fills, and VPO_h = fill rate x mean N_h.

| h | firm (fee per fill, ticks) | (a) K | (b) FIFO back of queue | (c) trade-through (gate) |
|---|---|---|---|---|
| 1 s | Topstep (0.264) | -0.5368 [-0.5479, -0.5260] negative; VPO -0.3778 [-0.3856, -0.3700] negative | -0.5010 [-0.5111, -0.4904] negative; VPO -0.3576 [-0.3651, -0.3498] negative | -1.2176 [-1.2304, -1.2046] negative; VPO -0.6267 [-0.6370, -0.6158] negative |
| 1 s | Lucid (0.280) | -0.5528 [-0.5639, -0.5420] negative; VPO -0.3890 [-0.3969, -0.3812] negative | -0.5170 [-0.5271, -0.5064] negative; VPO -0.3690 [-0.3765, -0.3612] negative | -1.2336 [-1.2464, -1.2206] negative; VPO -0.6350 [-0.6453, -0.6239] negative |
| 1 s | Bulenox (0.286) | -0.5588 [-0.5699, -0.5480] negative; VPO -0.3933 [-0.4011, -0.3855] negative | -0.5230 [-0.5331, -0.5124] negative; VPO -0.3733 [-0.3808, -0.3654] negative | -1.2396 [-1.2524, -1.2266] negative; VPO -0.6381 [-0.6484, -0.6270] negative |
| 1 s | MFFU (0.306) | -0.5788 [-0.5899, -0.5680] negative; VPO -0.4073 [-0.4152, -0.3995] negative | -0.5430 [-0.5531, -0.5324] negative; VPO -0.3876 [-0.3951, -0.3796] negative | -1.2596 [-1.2724, -1.2466] negative; VPO -0.6484 [-0.6588, -0.6372] negative |
| 1 s | Tradeify (0.460) | -0.7328 [-0.7439, -0.7220] negative; VPO -0.5157 [-0.5237, -0.5076] negative | -0.6970 [-0.7071, -0.6864] negative; VPO -0.4975 [-0.5051, -0.4893] negative | -1.4136 [-1.4264, -1.4006] negative; VPO -0.7276 [-0.7388, -0.7157] negative |
| 10 s | Topstep (0.264) | -0.5512 [-0.5671, -0.5368] negative; VPO -0.3879 [-0.3992, -0.3778] negative | -0.5159 [-0.5305, -0.5025] negative; VPO -0.3683 [-0.3789, -0.3584] negative | -1.2339 [-1.2524, -1.2142] negative; VPO -0.6351 [-0.6475, -0.6222] negative |
| 10 s | Lucid (0.280) | -0.5672 [-0.5831, -0.5528] negative; VPO -0.3992 [-0.4104, -0.3891] negative | -0.5319 [-0.5465, -0.5185] negative; VPO -0.3797 [-0.3903, -0.3699] negative | -1.2499 [-1.2684, -1.2302] negative; VPO -0.6434 [-0.6558, -0.6304] negative |
| 10 s | Bulenox (0.286) | -0.5732 [-0.5891, -0.5588] negative; VPO -0.4034 [-0.4147, -0.3933] negative | -0.5379 [-0.5525, -0.5245] negative; VPO -0.3840 [-0.3946, -0.3742] negative | -1.2559 [-1.2744, -1.2362] negative; VPO -0.6465 [-0.6589, -0.6335] negative |
| 10 s | MFFU (0.306) | -0.5932 [-0.6091, -0.5788] negative; VPO -0.4175 [-0.4287, -0.4074] negative | -0.5579 [-0.5725, -0.5445] negative; VPO -0.3982 [-0.4089, -0.3884] negative | -1.2759 [-1.2944, -1.2562] negative; VPO -0.6567 [-0.6693, -0.6438] negative |
| 10 s | Tradeify (0.460) | -0.7472 [-0.7631, -0.7328] negative; VPO -0.5258 [-0.5372, -0.5155] negative | -0.7119 [-0.7265, -0.6985] negative; VPO -0.5082 [-0.5190, -0.4982] negative | -1.4299 [-1.4484, -1.4102] negative; VPO -0.7360 [-0.7493, -0.7224] negative |
| 60 s | Topstep (0.264) | -0.5540 [-0.5750, -0.5320] negative; VPO -0.3899 [-0.4043, -0.3750] negative | -0.5169 [-0.5372, -0.4961] negative; VPO -0.3690 [-0.3832, -0.3540] negative | -1.2429 [-1.2726, -1.2131] negative; VPO -0.6398 [-0.6564, -0.6220] negative |
| 60 s | Lucid (0.280) | -0.5700 [-0.5910, -0.5480] negative; VPO -0.4011 [-0.4156, -0.3863] negative | -0.5329 [-0.5532, -0.5121] negative; VPO -0.3804 [-0.3946, -0.3654] negative | -1.2589 [-1.2886, -1.2291] negative; VPO -0.6480 [-0.6647, -0.6301] negative |
| 60 s | Bulenox (0.286) | -0.5760 [-0.5970, -0.5540] negative; VPO -0.4054 [-0.4198, -0.3905] negative | -0.5389 [-0.5592, -0.5181] negative; VPO -0.3847 [-0.3989, -0.3697] negative | -1.2649 [-1.2946, -1.2351] negative; VPO -0.6511 [-0.6678, -0.6332] negative |
| 60 s | MFFU (0.306) | -0.5960 [-0.6170, -0.5740] negative; VPO -0.4194 [-0.4340, -0.4046] negative | -0.5589 [-0.5792, -0.5381] negative; VPO -0.3989 [-0.4131, -0.3839] negative | -1.2849 [-1.3146, -1.2551] negative; VPO -0.6614 [-0.6781, -0.6434] negative |
| 60 s | Tradeify (0.460) | -0.7500 [-0.7710, -0.7280] negative; VPO -0.5278 [-0.5424, -0.5128] negative | -0.7129 [-0.7332, -0.6921] negative; VPO -0.5089 [-0.5229, -0.4939] negative | -1.4389 [-1.4686, -1.4091] negative; VPO -0.7407 [-0.7579, -0.7222] negative |

## All cells (model x symbol x session; pooled, buy, sell)

### (a) K, ZM.v.0, DAY

| statistic | pooled | buy | sell |
|---|---|---|---|
| placements | 85568 | 42784 | 42784 |
| fills (of which in the 50 ms cancel latency) | 60216 (33) | 29605 (18) | 30611 (15) |
| fills by trigger | queue 46930, through 13286 | queue 23252, through 6353 | queue 23678, through 6933 |
| fill rate | 0.7037 [0.6992, 0.7079] | 0.6920 [0.6850, 0.6987] | 0.7155 [0.7085, 0.7223] |
| touch rate | 0.8047 [0.8013, 0.8081] | 0.7932 [0.7876, 0.7987] | 0.8163 [0.8110, 0.8214] |
| stale share (best price at g differs from j) | 0.0625 [0.0598, 0.0652] | 0.0621 [0.0591, 0.0652] | 0.0629 [0.0599, 0.0657] |
| KM P(fill by 1 s) | 0.0626 [0.0605, 0.0648] | 0.0611 [0.0583, 0.0637] | 0.0641 [0.0612, 0.0671] |
| KM P(fill by 10 s) | 0.3668 [0.3611, 0.3723] | 0.3539 [0.3465, 0.3608] | 0.3797 [0.3723, 0.3872] |
| KM P(fill by 60 s) | 0.7033 [0.6988, 0.7075] | 0.6915 [0.6847, 0.6982] | 0.7151 [0.7081, 0.7219] |
| KM median time to fill (s) | 19.831 | 21.074 | 18.377 |
| KM censored before 60 s | 0 | 0 | 0 |
| mean c_half, all fills (ticks) | 0.3414 [0.3350, 0.3477] positive | 0.3414 [0.3330, 0.3499] positive | 0.3413 [0.3322, 0.3502] positive |
| median c_half, all fills | 0.5000 | 0.5000 | 0.5000 |
| 1 s: fills with E_h (dropped) | 60216 (0) | 29605 (0) | 30611 (0) |
| 1 s: mean markout (ticks) | -0.6142 [-0.6232, -0.6049] negative | -0.6105 [-0.6228, -0.5977] negative | -0.6177 [-0.6300, -0.6059] negative |
| 1 s: median markout | -0.5000 | -0.5000 | -0.5000 |
| 1 s: mean c_half on these fills | 0.3414 [0.3350, 0.3477] positive | 0.3414 [0.3330, 0.3499] positive | 0.3413 [0.3322, 0.3502] positive |
| 1 s: mean E_h | -0.2728 [-0.2839, -0.2620] negative | -0.2691 [-0.2836, -0.2544] negative | -0.2764 [-0.2905, -0.2623] negative |
| 1 s: median E_h | 0.0000 | 0.0000 | 0.0000 |
| 1 s: share E_h > 0 | 0.2754 [0.2707, 0.2806] | 0.2780 [0.2719, 0.2843] | 0.2730 [0.2669, 0.2793] |
| 1 s: mean N_h(Topstep) | -0.5368 [-0.5479, -0.5260] negative | -0.5331 [-0.5476, -0.5184] negative | -0.5404 [-0.5545, -0.5263] negative |
| 1 s: median N_h(Topstep) | -0.2640 | -0.2640 | -0.2640 |
| 1 s: VPO_h(Topstep) per resting order | -0.3778 [-0.3856, -0.3700] negative | -0.3689 [-0.3788, -0.3582] negative | -0.3866 [-0.3984, -0.3752] negative |
| 1 s no-drop: fills with E_h (dropped) | 60216 (0) | 29605 (0) | 30611 (0) |
| 1 s no-drop: mean E_h | -0.2728 [-0.2839, -0.2620] negative | -0.2691 [-0.2836, -0.2544] negative | -0.2764 [-0.2905, -0.2623] negative |
| 1 s no-drop: mean N_h(Topstep) | -0.5368 [-0.5479, -0.5260] negative | -0.5331 [-0.5476, -0.5184] negative | -0.5404 [-0.5545, -0.5263] negative |
| 1 s no-drop: VPO_h(Topstep) | -0.3778 [-0.3856, -0.3700] negative | -0.3689 [-0.3788, -0.3582] negative | -0.3866 [-0.3984, -0.3752] negative |
| 10 s: fills with E_h (dropped) | 60216 (0) | 29605 (0) | 30611 (0) |
| 10 s: mean markout (ticks) | -0.6286 [-0.6425, -0.6157] negative | -0.6095 [-0.6289, -0.5892] negative | -0.6471 [-0.6722, -0.6247] negative |
| 10 s: median markout | -0.5000 | -0.5000 | -0.5000 |
| 10 s: mean c_half on these fills | 0.3414 [0.3350, 0.3477] positive | 0.3414 [0.3330, 0.3499] positive | 0.3413 [0.3322, 0.3502] positive |
| 10 s: mean E_h | -0.2872 [-0.3031, -0.2728] negative | -0.2681 [-0.2897, -0.2454] negative | -0.3058 [-0.3318, -0.2802] negative |
| 10 s: median E_h | 0.0000 | 0.0000 | -0.5000 |
| 10 s: share E_h > 0 | 0.3732 [0.3687, 0.3779] | 0.3739 [0.3678, 0.3802] | 0.3725 [0.3659, 0.3792] |
| 10 s: mean N_h(Topstep) | -0.5512 [-0.5671, -0.5368] negative | -0.5321 [-0.5537, -0.5094] negative | -0.5698 [-0.5958, -0.5442] negative |
| 10 s: median N_h(Topstep) | -0.2640 | -0.2640 | -0.7640 |
| 10 s: VPO_h(Topstep) per resting order | -0.3879 [-0.3992, -0.3778] negative | -0.3682 [-0.3841, -0.3513] negative | -0.4076 [-0.4276, -0.3882] negative |
| 10 s no-drop: fills with E_h (dropped) | 60216 (0) | 29605 (0) | 30611 (0) |
| 10 s no-drop: mean E_h | -0.2872 [-0.3031, -0.2728] negative | -0.2681 [-0.2897, -0.2454] negative | -0.3058 [-0.3318, -0.2802] negative |
| 10 s no-drop: mean N_h(Topstep) | -0.5512 [-0.5671, -0.5368] negative | -0.5321 [-0.5537, -0.5094] negative | -0.5698 [-0.5958, -0.5442] negative |
| 10 s no-drop: VPO_h(Topstep) | -0.3879 [-0.3992, -0.3778] negative | -0.3682 [-0.3841, -0.3513] negative | -0.4076 [-0.4276, -0.3882] negative |
| 60 s: fills with E_h (dropped) | 60216 (0) | 29605 (0) | 30611 (0) |
| 60 s: mean markout (ticks) | -0.6314 [-0.6515, -0.6108] negative | -0.6335 [-0.6809, -0.5858] negative | -0.6293 [-0.6744, -0.5825] negative |
| 60 s: median markout | -0.5000 | -0.5000 | -0.5000 |
| 60 s: mean c_half on these fills | 0.3414 [0.3350, 0.3477] positive | 0.3414 [0.3330, 0.3499] positive | 0.3413 [0.3322, 0.3502] positive |
| 60 s: mean E_h | -0.2900 [-0.3110, -0.2680] negative | -0.2921 [-0.3405, -0.2429] negative | -0.2880 [-0.3353, -0.2389] negative |
| 60 s: median E_h | -0.5000 | -0.5000 | 0.0000 |
| 60 s: share E_h > 0 | 0.4405 [0.4372, 0.4439] | 0.4342 [0.4276, 0.4414] | 0.4466 [0.4399, 0.4532] |
| 60 s: mean N_h(Topstep) | -0.5540 [-0.5750, -0.5320] negative | -0.5561 [-0.6045, -0.5069] negative | -0.5520 [-0.5993, -0.5029] negative |
| 60 s: median N_h(Topstep) | -0.7640 | -0.7640 | -0.2640 |
| 60 s: VPO_h(Topstep) per resting order | -0.3899 [-0.4043, -0.3750] negative | -0.3848 [-0.4199, -0.3493] negative | -0.3949 [-0.4301, -0.3583] negative |
| 60 s no-drop: fills with E_h (dropped) | 60216 (0) | 29605 (0) | 30611 (0) |
| 60 s no-drop: mean E_h | -0.2900 [-0.3110, -0.2680] negative | -0.2921 [-0.3405, -0.2429] negative | -0.2880 [-0.3353, -0.2389] negative |
| 60 s no-drop: mean N_h(Topstep) | -0.5540 [-0.5750, -0.5320] negative | -0.5561 [-0.6045, -0.5069] negative | -0.5520 [-0.5993, -0.5029] negative |
| 60 s no-drop: VPO_h(Topstep) | -0.3899 [-0.4043, -0.3750] negative | -0.3848 [-0.4199, -0.3493] negative | -0.3949 [-0.4301, -0.3583] negative |

### (a) K, ZM.v.0, OVERNIGHT

| statistic | pooled | buy | sell |
|---|---|---|---|
| placements | 230662 | 115331 | 115331 |
| fills (of which in the 50 ms cancel latency) | 46783 (72) | 23114 (33) | 23669 (39) |
| fills by trigger | queue 25738, through 21045 | queue 12343, through 10771 | queue 13395, through 10274 |
| fill rate | 0.2028 [0.1985, 0.2071] | 0.2004 [0.1958, 0.2050] | 0.2052 [0.2005, 0.2100] |
| touch rate | 0.4063 [0.4015, 0.4113] | 0.4130 [0.4073, 0.4189] | 0.3996 [0.3940, 0.4056] |
| stale share (best price at g differs from j) | 0.0136 [0.0129, 0.0143] | 0.0136 [0.0128, 0.0144] | 0.0136 [0.0128, 0.0145] |
| KM P(fill by 1 s) | 0.0041 [0.0038, 0.0044] | 0.0045 [0.0041, 0.0049] | 0.0038 [0.0034, 0.0041] |
| KM P(fill by 10 s) | 0.0526 [0.0510, 0.0543] | 0.0530 [0.0510, 0.0550] | 0.0523 [0.0504, 0.0543] |
| KM P(fill by 60 s) | 0.2025 [0.1982, 0.2068] | 0.2001 [0.1955, 0.2047] | 0.2049 [0.2002, 0.2096] |
| KM median time to fill (s) | not reached | not reached | not reached |
| KM censored before 60 s | 0 | 0 | 0 |
| mean c_half, all fills (ticks) | 0.1433 [0.1326, 0.1540] positive | 0.1084 [0.0949, 0.1221] positive | 0.1774 [0.1647, 0.1907] positive |
| median c_half, all fills | 0.5000 | 0.5000 | 0.5000 |
| 1 s: fills with E_h (dropped) | 46783 (0) | 23114 (0) | 23669 (0) |
| 1 s: mean markout (ticks) | -0.6200 [-0.6295, -0.6104] negative | -0.5950 [-0.6079, -0.5824] negative | -0.6444 [-0.6580, -0.6314] negative |
| 1 s: median markout | -0.5000 | -0.5000 | -0.5000 |
| 1 s: mean c_half on these fills | 0.1433 [0.1326, 0.1540] positive | 0.1084 [0.0949, 0.1221] positive | 0.1774 [0.1647, 0.1907] positive |
| 1 s: mean E_h | -0.4767 [-0.4912, -0.4626] negative | -0.4866 [-0.5036, -0.4691] negative | -0.4670 [-0.4843, -0.4504] negative |
| 1 s: median E_h | -0.5000 | -0.5000 | -0.5000 |
| 1 s: share E_h > 0 | 0.1650 [0.1605, 0.1695] | 0.1642 [0.1583, 0.1701] | 0.1658 [0.1599, 0.1716] |
| 1 s: mean N_h(Topstep) | -0.7407 [-0.7552, -0.7266] negative | -0.7506 [-0.7676, -0.7331] negative | -0.7310 [-0.7483, -0.7144] negative |
| 1 s: median N_h(Topstep) | -0.7640 | -0.7640 | -0.7640 |
| 1 s: VPO_h(Topstep) per resting order | -0.1502 [-0.1551, -0.1457] negative | -0.1504 [-0.1561, -0.1453] negative | -0.1500 [-0.1555, -0.1449] negative |
| 1 s no-drop: fills with E_h (dropped) | 46783 (0) | 23114 (0) | 23669 (0) |
| 1 s no-drop: mean E_h | -0.4767 [-0.4912, -0.4626] negative | -0.4866 [-0.5036, -0.4691] negative | -0.4670 [-0.4843, -0.4504] negative |
| 1 s no-drop: mean N_h(Topstep) | -0.7407 [-0.7552, -0.7266] negative | -0.7506 [-0.7676, -0.7331] negative | -0.7310 [-0.7483, -0.7144] negative |
| 1 s no-drop: VPO_h(Topstep) | -0.1502 [-0.1551, -0.1457] negative | -0.1504 [-0.1561, -0.1453] negative | -0.1500 [-0.1555, -0.1449] negative |
| 10 s: fills with E_h (dropped) | 46783 (0) | 23114 (0) | 23669 (0) |
| 10 s: mean markout (ticks) | -0.6446 [-0.6573, -0.6326] negative | -0.6302 [-0.6474, -0.6136] negative | -0.6588 [-0.6750, -0.6428] negative |
| 10 s: median markout | -0.5000 | -0.5000 | -0.5000 |
| 10 s: mean c_half on these fills | 0.1433 [0.1326, 0.1540] positive | 0.1084 [0.0949, 0.1221] positive | 0.1774 [0.1647, 0.1907] positive |
| 10 s: mean E_h | -0.5014 [-0.5181, -0.4844] negative | -0.5218 [-0.5427, -0.5004] negative | -0.4814 [-0.5018, -0.4621] negative |
| 10 s: median E_h | -0.5000 | -0.5000 | -0.5000 |
| 10 s: share E_h > 0 | 0.2158 [0.2111, 0.2208] | 0.2145 [0.2083, 0.2212] | 0.2172 [0.2108, 0.2232] |
| 10 s: mean N_h(Topstep) | -0.7654 [-0.7821, -0.7484] negative | -0.7858 [-0.8067, -0.7644] negative | -0.7454 [-0.7658, -0.7261] negative |
| 10 s: median N_h(Topstep) | -0.7640 | -0.7640 | -0.7640 |
| 10 s: VPO_h(Topstep) per resting order | -0.1552 [-0.1606, -0.1500] negative | -0.1575 [-0.1639, -0.1516] negative | -0.1530 [-0.1589, -0.1473] negative |
| 10 s no-drop: fills with E_h (dropped) | 46783 (0) | 23114 (0) | 23669 (0) |
| 10 s no-drop: mean E_h | -0.5014 [-0.5181, -0.4844] negative | -0.5218 [-0.5427, -0.5004] negative | -0.4814 [-0.5018, -0.4621] negative |
| 10 s no-drop: mean N_h(Topstep) | -0.7654 [-0.7821, -0.7484] negative | -0.7858 [-0.8067, -0.7644] negative | -0.7454 [-0.7658, -0.7261] negative |
| 10 s no-drop: VPO_h(Topstep) | -0.1552 [-0.1606, -0.1500] negative | -0.1575 [-0.1639, -0.1516] negative | -0.1530 [-0.1589, -0.1473] negative |
| 60 s: fills with E_h (dropped) | 46783 (0) | 23114 (0) | 23669 (0) |
| 60 s: mean markout (ticks) | -0.6430 [-0.6612, -0.6250] negative | -0.6205 [-0.6466, -0.5936] negative | -0.6649 [-0.6905, -0.6382] negative |
| 60 s: median markout | -0.5000 | -0.5000 | -0.5000 |
| 60 s: mean c_half on these fills | 0.1433 [0.1326, 0.1540] positive | 0.1084 [0.0949, 0.1221] positive | 0.1774 [0.1647, 0.1907] positive |
| 60 s: mean E_h | -0.4997 [-0.5215, -0.4785] negative | -0.5121 [-0.5424, -0.4837] negative | -0.4875 [-0.5160, -0.4590] negative |
| 60 s: median E_h | -0.5000 | -0.5000 | -0.5000 |
| 60 s: share E_h > 0 | 0.3185 [0.3137, 0.3234] | 0.3141 [0.3076, 0.3208] | 0.3227 [0.3159, 0.3295] |
| 60 s: mean N_h(Topstep) | -0.7637 [-0.7855, -0.7425] negative | -0.7761 [-0.8064, -0.7477] negative | -0.7515 [-0.7800, -0.7230] negative |
| 60 s: median N_h(Topstep) | -0.7640 | -0.7640 | -0.7640 |
| 60 s: VPO_h(Topstep) per resting order | -0.1549 [-0.1609, -0.1491] negative | -0.1555 [-0.1634, -0.1481] negative | -0.1542 [-0.1617, -0.1472] negative |
| 60 s no-drop: fills with E_h (dropped) | 46783 (0) | 23114 (0) | 23669 (0) |
| 60 s no-drop: mean E_h | -0.4997 [-0.5215, -0.4785] negative | -0.5121 [-0.5424, -0.4837] negative | -0.4875 [-0.5160, -0.4590] negative |
| 60 s no-drop: mean N_h(Topstep) | -0.7637 [-0.7855, -0.7425] negative | -0.7761 [-0.8064, -0.7477] negative | -0.7515 [-0.7800, -0.7230] negative |
| 60 s no-drop: VPO_h(Topstep) | -0.1549 [-0.1609, -0.1491] negative | -0.1555 [-0.1634, -0.1481] negative | -0.1542 [-0.1617, -0.1472] negative |

### (a) K, ZM.v.1, DAY

| statistic | pooled | buy | sell |
|---|---|---|---|
| placements | 76608 | 38304 | 38304 |
| fills (of which in the 50 ms cancel latency) | 37621 (38) | 18327 (18) | 19294 (20) |
| fills by trigger | queue 19050, through 18571 | queue 9431, through 8896 | queue 9619, through 9675 |
| fill rate | 0.4911 [0.4805, 0.5010] | 0.4785 [0.4668, 0.4895] | 0.5037 [0.4920, 0.5152] |
| touch rate | 0.6737 [0.6639, 0.6825] | 0.6620 [0.6510, 0.6718] | 0.6855 [0.6742, 0.6961] |
| stale share (best price at g differs from j) | 0.0656 [0.0627, 0.0685] | 0.0660 [0.0627, 0.0692] | 0.0653 [0.0620, 0.0685] |
| KM P(fill by 1 s) | 0.0201 [0.0188, 0.0213] | 0.0199 [0.0181, 0.0216] | 0.0202 [0.0185, 0.0219] |
| KM P(fill by 10 s) | 0.1690 [0.1628, 0.1747] | 0.1599 [0.1531, 0.1661] | 0.1782 [0.1706, 0.1849] |
| KM P(fill by 60 s) | 0.4906 [0.4800, 0.5005] | 0.4780 [0.4663, 0.4890] | 0.5032 [0.4914, 0.5146] |
| KM median time to fill (s) | not reached | not reached | 59.190 |
| KM censored before 60 s | 0 | 0 | 0 |
| mean c_half, all fills (ticks) | -0.1018 [-0.1218, -0.0809] negative | -0.1032 [-0.1300, -0.0785] negative | -0.1004 [-0.1235, -0.0757] negative |
| median c_half, all fills | 0.5000 | 0.5000 | 0.5000 |
| 1 s: fills with E_h (dropped) | 37621 (0) | 18327 (0) | 19294 (0) |
| 1 s: mean markout (ticks) | -0.5058 [-0.5172, -0.4938] negative | -0.5026 [-0.5175, -0.4864] negative | -0.5087 [-0.5247, -0.4934] negative |
| 1 s: median markout | -0.5000 | -0.5000 | -0.5000 |
| 1 s: mean c_half on these fills | -0.1018 [-0.1218, -0.0809] negative | -0.1032 [-0.1300, -0.0785] negative | -0.1004 [-0.1235, -0.0757] negative |
| 1 s: mean E_h | -0.6075 [-0.6298, -0.5833] negative | -0.6058 [-0.6330, -0.5780] negative | -0.6091 [-0.6367, -0.5811] negative |
| 1 s: median E_h | -0.5000 | -0.5000 | -0.5000 |
| 1 s: share E_h > 0 | 0.1883 [0.1832, 0.1939] | 0.1873 [0.1808, 0.1941] | 0.1892 [0.1823, 0.1963] |
| 1 s: mean N_h(Topstep) | -0.8715 [-0.8938, -0.8473] negative | -0.8698 [-0.8970, -0.8420] negative | -0.8731 [-0.9007, -0.8451] negative |
| 1 s: median N_h(Topstep) | -0.7640 | -0.7640 | -0.7640 |
| 1 s: VPO_h(Topstep) per resting order | -0.4280 [-0.4399, -0.4150] negative | -0.4162 [-0.4314, -0.4008] negative | -0.4398 [-0.4556, -0.4227] negative |
| 1 s no-drop: fills with E_h (dropped) | 37621 (0) | 18327 (0) | 19294 (0) |
| 1 s no-drop: mean E_h | -0.6075 [-0.6298, -0.5833] negative | -0.6058 [-0.6330, -0.5780] negative | -0.6091 [-0.6367, -0.5811] negative |
| 1 s no-drop: mean N_h(Topstep) | -0.8715 [-0.8938, -0.8473] negative | -0.8698 [-0.8970, -0.8420] negative | -0.8731 [-0.9007, -0.8451] negative |
| 1 s no-drop: VPO_h(Topstep) | -0.4280 [-0.4399, -0.4150] negative | -0.4162 [-0.4314, -0.4008] negative | -0.4398 [-0.4556, -0.4227] negative |
| 10 s: fills with E_h (dropped) | 37621 (0) | 18327 (0) | 19294 (0) |
| 10 s: mean markout (ticks) | -0.5153 [-0.5340, -0.4967] negative | -0.5037 [-0.5296, -0.4772] negative | -0.5264 [-0.5560, -0.4981] negative |
| 10 s: median markout | -0.5000 | -0.5000 | -0.5000 |
| 10 s: mean c_half on these fills | -0.1018 [-0.1218, -0.0809] negative | -0.1032 [-0.1300, -0.0785] negative | -0.1004 [-0.1235, -0.0757] negative |
| 10 s: mean E_h | -0.6171 [-0.6441, -0.5887] negative | -0.6068 [-0.6427, -0.5686] negative | -0.6268 [-0.6642, -0.5893] negative |
| 10 s: median E_h | -0.5000 | -0.5000 | -0.5000 |
| 10 s: share E_h > 0 | 0.2786 [0.2729, 0.2843] | 0.2790 [0.2711, 0.2871] | 0.2782 [0.2703, 0.2859] |
| 10 s: mean N_h(Topstep) | -0.8811 [-0.9081, -0.8527] negative | -0.8708 [-0.9067, -0.8326] negative | -0.8908 [-0.9282, -0.8533] negative |
| 10 s: median N_h(Topstep) | -0.7640 | -0.7640 | -0.7640 |
| 10 s: VPO_h(Topstep) per resting order | -0.4327 [-0.4466, -0.4180] negative | -0.4167 [-0.4354, -0.3976] negative | -0.4487 [-0.4704, -0.4275] negative |
| 10 s no-drop: fills with E_h (dropped) | 37621 (0) | 18327 (0) | 19294 (0) |
| 10 s no-drop: mean E_h | -0.6171 [-0.6441, -0.5887] negative | -0.6068 [-0.6427, -0.5686] negative | -0.6268 [-0.6642, -0.5893] negative |
| 10 s no-drop: mean N_h(Topstep) | -0.8811 [-0.9081, -0.8527] negative | -0.8708 [-0.9067, -0.8326] negative | -0.8908 [-0.9282, -0.8533] negative |
| 10 s no-drop: VPO_h(Topstep) | -0.4327 [-0.4466, -0.4180] negative | -0.4167 [-0.4354, -0.3976] negative | -0.4487 [-0.4704, -0.4275] negative |
| 60 s: fills with E_h (dropped) | 37620 (1) | 18327 (0) | 19293 (1) |
| 60 s: mean markout (ticks) | -0.5354 [-0.5642, -0.5062] negative | -0.5347 [-0.5836, -0.4862] negative | -0.5362 [-0.5881, -0.4849] negative |
| 60 s: median markout | -0.5000 | -0.5000 | -0.5000 |
| 60 s: mean c_half on these fills | -0.1018 [-0.1219, -0.0810] negative | -0.1032 [-0.1300, -0.0785] negative | -0.1005 [-0.1236, -0.0757] negative |
| 60 s: mean E_h | -0.6372 [-0.6735, -0.6009] negative | -0.6378 [-0.6947, -0.5812] negative | -0.6367 [-0.6955, -0.5778] negative |
| 60 s: median E_h | -0.5000 | -0.5000 | -0.5000 |
| 60 s: share E_h > 0 | 0.3792 [0.3743, 0.3840] | 0.3784 [0.3704, 0.3862] | 0.3799 [0.3721, 0.3877] |
| 60 s: mean N_h(Topstep) | -0.9012 [-0.9375, -0.8649] negative | -0.9018 [-0.9587, -0.8452] negative | -0.9007 [-0.9595, -0.8418] negative |
| 60 s: median N_h(Topstep) | -0.7640 | -0.7640 | -0.7640 |
| 60 s: VPO_h(Topstep) per resting order | -0.4426 [-0.4600, -0.4236] negative | -0.4315 [-0.4610, -0.4031] negative | -0.4537 [-0.4858, -0.4211] negative |
| 60 s no-drop: fills with E_h (dropped) | 37621 (0) | 18327 (0) | 19294 (0) |
| 60 s no-drop: mean E_h | -0.6373 [-0.6735, -0.6009] negative | -0.6378 [-0.6947, -0.5812] negative | -0.6368 [-0.6957, -0.5779] negative |
| 60 s no-drop: mean N_h(Topstep) | -0.9013 [-0.9375, -0.8649] negative | -0.9018 [-0.9587, -0.8452] negative | -0.9008 [-0.9597, -0.8419] negative |
| 60 s no-drop: VPO_h(Topstep) | -0.4426 [-0.4601, -0.4237] negative | -0.4315 [-0.4610, -0.4031] negative | -0.4538 [-0.4859, -0.4213] negative |

### (a) K, ZM.v.1, OVERNIGHT

| statistic | pooled | buy | sell |
|---|---|---|---|
| placements | 206566 | 103283 | 103283 |
| fills (of which in the 50 ms cancel latency) | 16768 (28) | 8169 (16) | 8599 (12) |
| fills by trigger | queue 6672, through 10096 | queue 3220, through 4949 | queue 3452, through 5147 |
| fill rate | 0.0812 [0.0776, 0.0845] | 0.0791 [0.0755, 0.0826] | 0.0833 [0.0793, 0.0870] |
| touch rate | 0.2331 [0.2265, 0.2396] | 0.2345 [0.2272, 0.2415] | 0.2317 [0.2248, 0.2387] |
| stale share (best price at g differs from j) | 0.0142 [0.0134, 0.0150] | 0.0145 [0.0136, 0.0154] | 0.0139 [0.0130, 0.0149] |
| KM P(fill by 1 s) | 0.0012 [0.0010, 0.0013] | 0.0014 [0.0012, 0.0017] | 0.0010 [0.0008, 0.0012] |
| KM P(fill by 10 s) | 0.0160 [0.0150, 0.0169] | 0.0163 [0.0152, 0.0174] | 0.0157 [0.0146, 0.0168] |
| KM P(fill by 60 s) | 0.0810 [0.0775, 0.0844] | 0.0789 [0.0753, 0.0825] | 0.0831 [0.0792, 0.0869] |
| KM median time to fill (s) | not reached | not reached | not reached |
| KM censored before 60 s | 0 | 0 | 0 |
| mean c_half, all fills (ticks) | -0.1349 [-0.1615, -0.1093] negative | -0.1720 [-0.2034, -0.1417] negative | -0.0997 [-0.1314, -0.0700] negative |
| median c_half, all fills | 0.0000 | 0.0000 | 0.0000 |
| 1 s: fills with E_h (dropped) | 16768 (0) | 8169 (0) | 8599 (0) |
| 1 s: mean markout (ticks) | -0.6005 [-0.6209, -0.5791] negative | -0.5760 [-0.6071, -0.5399] negative | -0.6237 [-0.6476, -0.6002] negative |
| 1 s: median markout | -0.5000 | -0.5000 | -0.5000 |
| 1 s: mean c_half on these fills | -0.1349 [-0.1615, -0.1093] negative | -0.1720 [-0.2034, -0.1417] negative | -0.0997 [-0.1314, -0.0700] negative |
| 1 s: mean E_h | -0.7354 [-0.7690, -0.7025] negative | -0.7479 [-0.7903, -0.7013] negative | -0.7234 [-0.7610, -0.6914] negative |
| 1 s: median E_h | -0.5000 | -0.5000 | -0.5000 |
| 1 s: share E_h > 0 | 0.1624 [0.1555, 0.1696] | 0.1584 [0.1494, 0.1673] | 0.1662 [0.1569, 0.1752] |
| 1 s: mean N_h(Topstep) | -0.9994 [-1.0330, -0.9665] negative | -1.0119 [-1.0543, -0.9653] negative | -0.9874 [-1.0250, -0.9554] negative |
| 1 s: median N_h(Topstep) | -0.7640 | -0.7640 | -0.7640 |
| 1 s: VPO_h(Topstep) per resting order | -0.0811 [-0.0857, -0.0767] negative | -0.0800 [-0.0851, -0.0748] negative | -0.0822 [-0.0871, -0.0775] negative |
| 1 s no-drop: fills with E_h (dropped) | 16768 (0) | 8169 (0) | 8599 (0) |
| 1 s no-drop: mean E_h | -0.7354 [-0.7690, -0.7025] negative | -0.7479 [-0.7903, -0.7013] negative | -0.7234 [-0.7610, -0.6914] negative |
| 1 s no-drop: mean N_h(Topstep) | -0.9994 [-1.0330, -0.9665] negative | -1.0119 [-1.0543, -0.9653] negative | -0.9874 [-1.0250, -0.9554] negative |
| 1 s no-drop: VPO_h(Topstep) | -0.0811 [-0.0857, -0.0767] negative | -0.0800 [-0.0851, -0.0748] negative | -0.0822 [-0.0871, -0.0775] negative |
| 10 s: fills with E_h (dropped) | 16768 (0) | 8169 (0) | 8599 (0) |
| 10 s: mean markout (ticks) | -0.6330 [-0.6582, -0.6063] negative | -0.6189 [-0.6567, -0.5781] negative | -0.6464 [-0.6761, -0.6173] negative |
| 10 s: median markout | -0.5000 | -0.5000 | -0.5000 |
| 10 s: mean c_half on these fills | -0.1349 [-0.1615, -0.1093] negative | -0.1720 [-0.2034, -0.1417] negative | -0.0997 [-0.1314, -0.0700] negative |
| 10 s: mean E_h | -0.7679 [-0.8056, -0.7316] negative | -0.7909 [-0.8410, -0.7379] negative | -0.7461 [-0.7874, -0.7078] negative |
| 10 s: median E_h | -0.5000 | -0.5000 | -0.5000 |
| 10 s: share E_h > 0 | 0.1967 [0.1900, 0.2041] | 0.1921 [0.1831, 0.2018] | 0.2012 [0.1920, 0.2103] |
| 10 s: mean N_h(Topstep) | -1.0319 [-1.0696, -0.9956] negative | -1.0549 [-1.1050, -1.0019] negative | -1.0101 [-1.0514, -0.9718] negative |
| 10 s: median N_h(Topstep) | -0.7640 | -0.7640 | -0.7640 |
| 10 s: VPO_h(Topstep) per resting order | -0.0838 [-0.0885, -0.0789] negative | -0.0834 [-0.0893, -0.0776] negative | -0.0841 [-0.0891, -0.0792] negative |
| 10 s no-drop: fills with E_h (dropped) | 16768 (0) | 8169 (0) | 8599 (0) |
| 10 s no-drop: mean E_h | -0.7679 [-0.8056, -0.7316] negative | -0.7909 [-0.8410, -0.7379] negative | -0.7461 [-0.7874, -0.7078] negative |
| 10 s no-drop: mean N_h(Topstep) | -1.0319 [-1.0696, -0.9956] negative | -1.0549 [-1.1050, -1.0019] negative | -1.0101 [-1.0514, -0.9718] negative |
| 10 s no-drop: VPO_h(Topstep) | -0.0838 [-0.0885, -0.0789] negative | -0.0834 [-0.0893, -0.0776] negative | -0.0841 [-0.0891, -0.0792] negative |
| 60 s: fills with E_h (dropped) | 16768 (0) | 8169 (0) | 8599 (0) |
| 60 s: mean markout (ticks) | -0.6378 [-0.6733, -0.6027] negative | -0.6277 [-0.6806, -0.5714] negative | -0.6473 [-0.6929, -0.6020] negative |
| 60 s: median markout | -0.5000 | -0.5000 | -0.5000 |
| 60 s: mean c_half on these fills | -0.1349 [-0.1615, -0.1093] negative | -0.1720 [-0.2034, -0.1417] negative | -0.0997 [-0.1314, -0.0700] negative |
| 60 s: mean E_h | -0.7727 [-0.8171, -0.7313] negative | -0.7997 [-0.8608, -0.7372] negative | -0.7470 [-0.7977, -0.6958] negative |
| 60 s: median E_h | -0.5000 | -0.5000 | -0.5000 |
| 60 s: share E_h > 0 | 0.2822 [0.2749, 0.2899] | 0.2782 [0.2679, 0.2888] | 0.2860 [0.2765, 0.2958] |
| 60 s: mean N_h(Topstep) | -1.0367 [-1.0811, -0.9953] negative | -1.0637 [-1.1248, -1.0012] negative | -1.0110 [-1.0617, -0.9598] negative |
| 60 s: median N_h(Topstep) | -0.7640 | -0.7640 | -0.7640 |
| 60 s: VPO_h(Topstep) per resting order | -0.0842 [-0.0893, -0.0790] negative | -0.0841 [-0.0906, -0.0774] negative | -0.0842 [-0.0899, -0.0787] negative |
| 60 s no-drop: fills with E_h (dropped) | 16768 (0) | 8169 (0) | 8599 (0) |
| 60 s no-drop: mean E_h | -0.7727 [-0.8171, -0.7313] negative | -0.7997 [-0.8608, -0.7372] negative | -0.7470 [-0.7977, -0.6958] negative |
| 60 s no-drop: mean N_h(Topstep) | -1.0367 [-1.0811, -0.9953] negative | -1.0637 [-1.1248, -1.0012] negative | -1.0110 [-1.0617, -0.9598] negative |
| 60 s no-drop: VPO_h(Topstep) | -0.0842 [-0.0893, -0.0790] negative | -0.0841 [-0.0906, -0.0774] negative | -0.0842 [-0.0899, -0.0787] negative |

### (b) FIFO back of queue, ZM.v.0, DAY

| statistic | pooled | buy | sell |
|---|---|---|---|
| placements | 85568 | 42784 | 42784 |
| fills (of which in the 50 ms cancel latency) | 61078 (27) | 30016 (15) | 31062 (12) |
| fills by trigger | queue 48897, through 12181 | queue 24178, through 5838 | queue 24719, through 6343 |
| fill rate | 0.7138 [0.7093, 0.7180] | 0.7016 [0.6949, 0.7079] | 0.7260 [0.7190, 0.7327] |
| touch rate | 0.8047 [0.8013, 0.8081] | 0.7932 [0.7876, 0.7987] | 0.8163 [0.8110, 0.8214] |
| stale share (best price at g differs from j) | 0.0625 [0.0598, 0.0652] | 0.0621 [0.0591, 0.0652] | 0.0629 [0.0599, 0.0657] |
| KM P(fill by 1 s) | 0.0663 [0.0639, 0.0686] | 0.0650 [0.0619, 0.0678] | 0.0676 [0.0646, 0.0706] |
| KM P(fill by 10 s) | 0.3861 [0.3804, 0.3917] | 0.3731 [0.3656, 0.3803] | 0.3991 [0.3914, 0.4071] |
| KM P(fill by 60 s) | 0.7135 [0.7090, 0.7177] | 0.7012 [0.6946, 0.7075] | 0.7257 [0.7188, 0.7324] |
| KM median time to fill (s) | 17.962 | 19.413 | 16.644 |
| KM censored before 60 s | 0 | 0 | 0 |
| mean c_half, all fills (ticks) | 0.3594 [0.3536, 0.3651] positive | 0.3581 [0.3503, 0.3660] positive | 0.3607 [0.3521, 0.3687] positive |
| median c_half, all fills | 0.5000 | 0.5000 | 0.5000 |
| 1 s: fills with E_h (dropped) | 61078 (0) | 30016 (0) | 31062 (0) |
| 1 s: mean markout (ticks) | -0.5964 [-0.6052, -0.5871] negative | -0.5930 [-0.6045, -0.5808] negative | -0.5998 [-0.6122, -0.5882] negative |
| 1 s: median markout | -0.5000 | -0.5000 | -0.5000 |
| 1 s: mean c_half on these fills | 0.3594 [0.3536, 0.3651] positive | 0.3581 [0.3503, 0.3660] positive | 0.3607 [0.3521, 0.3687] positive |
| 1 s: mean E_h | -0.2370 [-0.2471, -0.2264] negative | -0.2348 [-0.2482, -0.2213] negative | -0.2391 [-0.2531, -0.2254] negative |
| 1 s: median E_h | 0.0000 | 0.0000 | 0.0000 |
| 1 s: share E_h > 0 | 0.2868 [0.2821, 0.2919] | 0.2889 [0.2832, 0.2951] | 0.2847 [0.2788, 0.2912] |
| 1 s: mean N_h(Topstep) | -0.5010 [-0.5111, -0.4904] negative | -0.4988 [-0.5122, -0.4853] negative | -0.5031 [-0.5171, -0.4894] negative |
| 1 s: median N_h(Topstep) | -0.2640 | -0.2640 | -0.2640 |
| 1 s: VPO_h(Topstep) per resting order | -0.3576 [-0.3651, -0.3498] negative | -0.3500 [-0.3598, -0.3396] negative | -0.3653 [-0.3766, -0.3539] negative |
| 1 s no-drop: fills with E_h (dropped) | 61078 (0) | 30016 (0) | 31062 (0) |
| 1 s no-drop: mean E_h | -0.2370 [-0.2471, -0.2264] negative | -0.2348 [-0.2482, -0.2213] negative | -0.2391 [-0.2531, -0.2254] negative |
| 1 s no-drop: mean N_h(Topstep) | -0.5010 [-0.5111, -0.4904] negative | -0.4988 [-0.5122, -0.4853] negative | -0.5031 [-0.5171, -0.4894] negative |
| 1 s no-drop: VPO_h(Topstep) | -0.3576 [-0.3651, -0.3498] negative | -0.3500 [-0.3598, -0.3396] negative | -0.3653 [-0.3766, -0.3539] negative |
| 10 s: fills with E_h (dropped) | 61078 (0) | 30016 (0) | 31062 (0) |
| 10 s: mean markout (ticks) | -0.6114 [-0.6248, -0.5981] negative | -0.5906 [-0.6099, -0.5699] negative | -0.6314 [-0.6548, -0.6085] negative |
| 10 s: median markout | -0.5000 | -0.5000 | -0.5000 |
| 10 s: mean c_half on these fills | 0.3594 [0.3536, 0.3651] positive | 0.3581 [0.3503, 0.3660] positive | 0.3607 [0.3521, 0.3687] positive |
| 10 s: mean E_h | -0.2519 [-0.2665, -0.2385] negative | -0.2325 [-0.2530, -0.2106] negative | -0.2707 [-0.2957, -0.2461] negative |
| 10 s: median E_h | 0.0000 | 0.0000 | 0.0000 |
| 10 s: share E_h > 0 | 0.3830 [0.3784, 0.3878] | 0.3832 [0.3770, 0.3897] | 0.3828 [0.3761, 0.3896] |
| 10 s: mean N_h(Topstep) | -0.5159 [-0.5305, -0.5025] negative | -0.4965 [-0.5170, -0.4746] negative | -0.5347 [-0.5597, -0.5101] negative |
| 10 s: median N_h(Topstep) | -0.2640 | -0.2640 | -0.2640 |
| 10 s: VPO_h(Topstep) per resting order | -0.3683 [-0.3789, -0.3584] negative | -0.3483 [-0.3638, -0.3315] negative | -0.3882 [-0.4078, -0.3688] negative |
| 10 s no-drop: fills with E_h (dropped) | 61078 (0) | 30016 (0) | 31062 (0) |
| 10 s no-drop: mean E_h | -0.2519 [-0.2665, -0.2385] negative | -0.2325 [-0.2530, -0.2106] negative | -0.2707 [-0.2957, -0.2461] negative |
| 10 s no-drop: mean N_h(Topstep) | -0.5159 [-0.5305, -0.5025] negative | -0.4965 [-0.5170, -0.4746] negative | -0.5347 [-0.5597, -0.5101] negative |
| 10 s no-drop: VPO_h(Topstep) | -0.3683 [-0.3789, -0.3584] negative | -0.3483 [-0.3638, -0.3315] negative | -0.3882 [-0.4078, -0.3688] negative |
| 60 s: fills with E_h (dropped) | 61078 (0) | 30016 (0) | 31062 (0) |
| 60 s: mean markout (ticks) | -0.6123 [-0.6320, -0.5918] negative | -0.6152 [-0.6623, -0.5678] negative | -0.6095 [-0.6539, -0.5643] negative |
| 60 s: median markout | -0.5000 | -0.5000 | -0.5000 |
| 60 s: mean c_half on these fills | 0.3594 [0.3536, 0.3651] positive | 0.3581 [0.3503, 0.3660] positive | 0.3607 [0.3521, 0.3687] positive |
| 60 s: mean E_h | -0.2529 [-0.2732, -0.2321] negative | -0.2571 [-0.3041, -0.2097] negative | -0.2488 [-0.2954, -0.2003] negative |
| 60 s: median E_h | 0.0000 | -0.5000 | 0.0000 |
| 60 s: share E_h > 0 | 0.4459 [0.4428, 0.4493] | 0.4392 [0.4326, 0.4463] | 0.4524 [0.4458, 0.4588] |
| 60 s: mean N_h(Topstep) | -0.5169 [-0.5372, -0.4961] negative | -0.5211 [-0.5681, -0.4737] negative | -0.5128 [-0.5594, -0.4643] negative |
| 60 s: median N_h(Topstep) | -0.2640 | -0.7640 | -0.2640 |
| 60 s: VPO_h(Topstep) per resting order | -0.3690 [-0.3832, -0.3540] negative | -0.3656 [-0.4003, -0.3309] negative | -0.3723 [-0.4075, -0.3363] negative |
| 60 s no-drop: fills with E_h (dropped) | 61078 (0) | 30016 (0) | 31062 (0) |
| 60 s no-drop: mean E_h | -0.2529 [-0.2732, -0.2321] negative | -0.2571 [-0.3041, -0.2097] negative | -0.2488 [-0.2954, -0.2003] negative |
| 60 s no-drop: mean N_h(Topstep) | -0.5169 [-0.5372, -0.4961] negative | -0.5211 [-0.5681, -0.4737] negative | -0.5128 [-0.5594, -0.4643] negative |
| 60 s no-drop: VPO_h(Topstep) | -0.3690 [-0.3832, -0.3540] negative | -0.3656 [-0.4003, -0.3309] negative | -0.3723 [-0.4075, -0.3363] negative |

### (b) FIFO back of queue, ZM.v.0, OVERNIGHT

| statistic | pooled | buy | sell |
|---|---|---|---|
| placements | 230662 | 115331 | 115331 |
| fills (of which in the 50 ms cancel latency) | 51308 (82) | 25518 (43) | 25790 (39) |
| fills by trigger | queue 31011, through 20297 | queue 15099, through 10419 | queue 15912, through 9878 |
| fill rate | 0.2224 [0.2181, 0.2270] | 0.2213 [0.2165, 0.2262] | 0.2236 [0.2188, 0.2287] |
| touch rate | 0.4063 [0.4015, 0.4113] | 0.4130 [0.4073, 0.4189] | 0.3996 [0.3940, 0.4056] |
| stale share (best price at g differs from j) | 0.0136 [0.0129, 0.0143] | 0.0136 [0.0128, 0.0144] | 0.0136 [0.0128, 0.0145] |
| KM P(fill by 1 s) | 0.0042 [0.0039, 0.0045] | 0.0046 [0.0042, 0.0050] | 0.0038 [0.0034, 0.0042] |
| KM P(fill by 10 s) | 0.0577 [0.0560, 0.0596] | 0.0587 [0.0566, 0.0609] | 0.0567 [0.0547, 0.0589] |
| KM P(fill by 60 s) | 0.2221 [0.2177, 0.2266] | 0.2209 [0.2162, 0.2258] | 0.2233 [0.2185, 0.2284] |
| KM median time to fill (s) | not reached | not reached | not reached |
| KM censored before 60 s | 0 | 0 | 0 |
| mean c_half, all fills (ticks) | 0.1913 [0.1825, 0.2007] positive | 0.1624 [0.1508, 0.1741] positive | 0.2199 [0.2092, 0.2306] positive |
| median c_half, all fills | 0.5000 | 0.5000 | 0.5000 |
| 1 s: fills with E_h (dropped) | 51308 (0) | 25518 (0) | 25790 (0) |
| 1 s: mean markout (ticks) | -0.5890 [-0.5986, -0.5797] negative | -0.5631 [-0.5750, -0.5523] negative | -0.6147 [-0.6279, -0.6022] negative |
| 1 s: median markout | -0.5000 | -0.5000 | -0.5000 |
| 1 s: mean c_half on these fills | 0.1913 [0.1825, 0.2007] positive | 0.1624 [0.1508, 0.1741] positive | 0.2199 [0.2092, 0.2306] positive |
| 1 s: mean E_h | -0.3977 [-0.4110, -0.3854] negative | -0.4007 [-0.4164, -0.3852] negative | -0.3948 [-0.4108, -0.3797] negative |
| 1 s: median E_h | 0.0000 | 0.0000 | 0.0000 |
| 1 s: share E_h > 0 | 0.1788 [0.1743, 0.1833] | 0.1817 [0.1762, 0.1875] | 0.1760 [0.1704, 0.1815] |
| 1 s: mean N_h(Topstep) | -0.6617 [-0.6750, -0.6494] negative | -0.6647 [-0.6804, -0.6492] negative | -0.6588 [-0.6748, -0.6437] negative |
| 1 s: median N_h(Topstep) | -0.2640 | -0.2640 | -0.2640 |
| 1 s: VPO_h(Topstep) per resting order | -0.1472 [-0.1519, -0.1428] negative | -0.1471 [-0.1525, -0.1421] negative | -0.1473 [-0.1526, -0.1422] negative |
| 1 s no-drop: fills with E_h (dropped) | 51308 (0) | 25518 (0) | 25790 (0) |
| 1 s no-drop: mean E_h | -0.3977 [-0.4110, -0.3854] negative | -0.4007 [-0.4164, -0.3852] negative | -0.3948 [-0.4108, -0.3797] negative |
| 1 s no-drop: mean N_h(Topstep) | -0.6617 [-0.6750, -0.6494] negative | -0.6647 [-0.6804, -0.6492] negative | -0.6588 [-0.6748, -0.6437] negative |
| 1 s no-drop: VPO_h(Topstep) | -0.1472 [-0.1519, -0.1428] negative | -0.1471 [-0.1525, -0.1421] negative | -0.1473 [-0.1526, -0.1422] negative |
| 10 s: fills with E_h (dropped) | 51308 (0) | 25518 (0) | 25790 (0) |
| 10 s: mean markout (ticks) | -0.6131 [-0.6253, -0.6009] negative | -0.5941 [-0.6094, -0.5786] negative | -0.6320 [-0.6483, -0.6161] negative |
| 10 s: median markout | -0.5000 | -0.5000 | -0.5000 |
| 10 s: mean c_half on these fills | 0.1913 [0.1825, 0.2007] positive | 0.1624 [0.1508, 0.1741] positive | 0.2199 [0.2092, 0.2306] positive |
| 10 s: mean E_h | -0.4218 [-0.4372, -0.4064] negative | -0.4317 [-0.4507, -0.4126] negative | -0.4121 [-0.4315, -0.3937] negative |
| 10 s: median E_h | 0.0000 | -0.5000 | 0.0000 |
| 10 s: share E_h > 0 | 0.2328 [0.2280, 0.2375] | 0.2347 [0.2285, 0.2409] | 0.2310 [0.2247, 0.2366] |
| 10 s: mean N_h(Topstep) | -0.6858 [-0.7012, -0.6704] negative | -0.6957 [-0.7147, -0.6766] negative | -0.6761 [-0.6955, -0.6577] negative |
| 10 s: median N_h(Topstep) | -0.2640 | -0.7640 | -0.2640 |
| 10 s: VPO_h(Topstep) per resting order | -0.1526 [-0.1578, -0.1476] negative | -0.1539 [-0.1602, -0.1481] negative | -0.1512 [-0.1569, -0.1457] negative |
| 10 s no-drop: fills with E_h (dropped) | 51308 (0) | 25518 (0) | 25790 (0) |
| 10 s no-drop: mean E_h | -0.4218 [-0.4372, -0.4064] negative | -0.4317 [-0.4507, -0.4126] negative | -0.4121 [-0.4315, -0.3937] negative |
| 10 s no-drop: mean N_h(Topstep) | -0.6858 [-0.7012, -0.6704] negative | -0.6957 [-0.7147, -0.6766] negative | -0.6761 [-0.6955, -0.6577] negative |
| 10 s no-drop: VPO_h(Topstep) | -0.1526 [-0.1578, -0.1476] negative | -0.1539 [-0.1602, -0.1481] negative | -0.1512 [-0.1569, -0.1457] negative |
| 60 s: fills with E_h (dropped) | 51308 (0) | 25518 (0) | 25790 (0) |
| 60 s: mean markout (ticks) | -0.6118 [-0.6300, -0.5942] negative | -0.5888 [-0.6136, -0.5645] negative | -0.6346 [-0.6597, -0.6097] negative |
| 60 s: median markout | -0.5000 | -0.5000 | -0.5000 |
| 60 s: mean c_half on these fills | 0.1913 [0.1825, 0.2007] positive | 0.1624 [0.1508, 0.1741] positive | 0.2199 [0.2092, 0.2306] positive |
| 60 s: mean E_h | -0.4205 [-0.4406, -0.4012] negative | -0.4264 [-0.4537, -0.3997] negative | -0.4147 [-0.4421, -0.3887] negative |
| 60 s: median E_h | -0.5000 | -0.5000 | 0.0000 |
| 60 s: share E_h > 0 | 0.3324 [0.3279, 0.3372] | 0.3295 [0.3233, 0.3362] | 0.3353 [0.3286, 0.3418] |
| 60 s: mean N_h(Topstep) | -0.6845 [-0.7046, -0.6652] negative | -0.6904 [-0.7177, -0.6637] negative | -0.6787 [-0.7061, -0.6527] negative |
| 60 s: median N_h(Topstep) | -0.7640 | -0.7640 | -0.2640 |
| 60 s: VPO_h(Topstep) per resting order | -0.1523 [-0.1582, -0.1464] negative | -0.1528 [-0.1605, -0.1455] negative | -0.1518 [-0.1592, -0.1447] negative |
| 60 s no-drop: fills with E_h (dropped) | 51308 (0) | 25518 (0) | 25790 (0) |
| 60 s no-drop: mean E_h | -0.4205 [-0.4406, -0.4012] negative | -0.4264 [-0.4537, -0.3997] negative | -0.4147 [-0.4421, -0.3887] negative |
| 60 s no-drop: mean N_h(Topstep) | -0.6845 [-0.7046, -0.6652] negative | -0.6904 [-0.7177, -0.6637] negative | -0.6787 [-0.7061, -0.6527] negative |
| 60 s no-drop: VPO_h(Topstep) | -0.1523 [-0.1582, -0.1464] negative | -0.1528 [-0.1605, -0.1455] negative | -0.1518 [-0.1592, -0.1447] negative |

### (b) FIFO back of queue, ZM.v.1, DAY

| statistic | pooled | buy | sell |
|---|---|---|---|
| placements | 76608 | 38304 | 38304 |
| fills (of which in the 50 ms cancel latency) | 39603 (31) | 19302 (16) | 20301 (15) |
| fills by trigger | queue 22781, through 16822 | queue 11234, through 8068 | queue 11547, through 8754 |
| fill rate | 0.5170 [0.5062, 0.5269] | 0.5039 [0.4918, 0.5150] | 0.5300 [0.5181, 0.5416] |
| touch rate | 0.6737 [0.6639, 0.6825] | 0.6620 [0.6510, 0.6718] | 0.6855 [0.6742, 0.6961] |
| stale share (best price at g differs from j) | 0.0656 [0.0627, 0.0685] | 0.0660 [0.0627, 0.0692] | 0.0653 [0.0620, 0.0685] |
| KM P(fill by 1 s) | 0.0220 [0.0207, 0.0234] | 0.0216 [0.0199, 0.0234] | 0.0225 [0.0207, 0.0242] |
| KM P(fill by 10 s) | 0.1871 [0.1804, 0.1931] | 0.1769 [0.1696, 0.1836] | 0.1972 [0.1889, 0.2046] |
| KM P(fill by 60 s) | 0.5166 [0.5057, 0.5265] | 0.5035 [0.4914, 0.5145] | 0.5296 [0.5178, 0.5413] |
| KM median time to fill (s) | 55.363 | 59.200 | 51.852 |
| KM censored before 60 s | 0 | 0 | 0 |
| mean c_half, all fills (ticks) | -0.0136 [-0.0323, 0.0055] not distinguishable from 0 | -0.0152 [-0.0391, 0.0076] not distinguishable from 0 | -0.0122 [-0.0336, 0.0100] not distinguishable from 0 |
| median c_half, all fills | 0.5000 | 0.5000 | 0.5000 |
| 1 s: fills with E_h (dropped) | 39603 (0) | 19302 (0) | 20301 (0) |
| 1 s: mean markout (ticks) | -0.5002 [-0.5116, -0.4888] negative | -0.4989 [-0.5136, -0.4828] negative | -0.5015 [-0.5161, -0.4858] negative |
| 1 s: median markout | -0.5000 | -0.5000 | -0.5000 |
| 1 s: mean c_half on these fills | -0.0136 [-0.0323, 0.0055] not distinguishable from 0 | -0.0152 [-0.0391, 0.0076] not distinguishable from 0 | -0.0122 [-0.0336, 0.0100] not distinguishable from 0 |
| 1 s: mean E_h | -0.5139 [-0.5351, -0.4916] negative | -0.5141 [-0.5390, -0.4881] negative | -0.5136 [-0.5392, -0.4872] negative |
| 1 s: median E_h | -0.5000 | -0.5000 | -0.5000 |
| 1 s: share E_h > 0 | 0.2076 [0.2025, 0.2130] | 0.2051 [0.1986, 0.2121] | 0.2099 [0.2034, 0.2170] |
| 1 s: mean N_h(Topstep) | -0.7779 [-0.7991, -0.7556] negative | -0.7781 [-0.8030, -0.7521] negative | -0.7776 [-0.8032, -0.7512] negative |
| 1 s: median N_h(Topstep) | -0.7640 | -0.7640 | -0.7640 |
| 1 s: VPO_h(Topstep) per resting order | -0.4021 [-0.4135, -0.3898] negative | -0.3921 [-0.4066, -0.3769] negative | -0.4121 [-0.4281, -0.3957] negative |
| 1 s no-drop: fills with E_h (dropped) | 39603 (0) | 19302 (0) | 20301 (0) |
| 1 s no-drop: mean E_h | -0.5139 [-0.5351, -0.4916] negative | -0.5141 [-0.5390, -0.4881] negative | -0.5136 [-0.5392, -0.4872] negative |
| 1 s no-drop: mean N_h(Topstep) | -0.7779 [-0.7991, -0.7556] negative | -0.7781 [-0.8030, -0.7521] negative | -0.7776 [-0.8032, -0.7512] negative |
| 1 s no-drop: VPO_h(Topstep) | -0.4021 [-0.4135, -0.3898] negative | -0.3921 [-0.4066, -0.3769] negative | -0.4121 [-0.4281, -0.3957] negative |
| 10 s: fills with E_h (dropped) | 39603 (0) | 19302 (0) | 20301 (0) |
| 10 s: mean markout (ticks) | -0.5115 [-0.5301, -0.4928] negative | -0.5033 [-0.5287, -0.4763] negative | -0.5193 [-0.5476, -0.4914] negative |
| 10 s: median markout | -0.5000 | -0.5000 | -0.5000 |
| 10 s: mean c_half on these fills | -0.0136 [-0.0323, 0.0055] not distinguishable from 0 | -0.0152 [-0.0391, 0.0076] not distinguishable from 0 | -0.0122 [-0.0336, 0.0100] not distinguishable from 0 |
| 10 s: mean E_h | -0.5252 [-0.5508, -0.4982] negative | -0.5185 [-0.5524, -0.4842] negative | -0.5315 [-0.5690, -0.4947] negative |
| 10 s: median E_h | -0.5000 | -0.5000 | -0.5000 |
| 10 s: share E_h > 0 | 0.2978 [0.2921, 0.3034] | 0.2981 [0.2904, 0.3059] | 0.2976 [0.2896, 0.3056] |
| 10 s: mean N_h(Topstep) | -0.7892 [-0.8148, -0.7622] negative | -0.7825 [-0.8164, -0.7482] negative | -0.7955 [-0.8330, -0.7587] negative |
| 10 s: median N_h(Topstep) | -0.7640 | -0.7640 | -0.7640 |
| 10 s: VPO_h(Topstep) per resting order | -0.4080 [-0.4213, -0.3939] negative | -0.3943 [-0.4126, -0.3756] negative | -0.4216 [-0.4433, -0.4004] negative |
| 10 s no-drop: fills with E_h (dropped) | 39603 (0) | 19302 (0) | 20301 (0) |
| 10 s no-drop: mean E_h | -0.5252 [-0.5508, -0.4982] negative | -0.5185 [-0.5524, -0.4842] negative | -0.5315 [-0.5690, -0.4947] negative |
| 10 s no-drop: mean N_h(Topstep) | -0.7892 [-0.8148, -0.7622] negative | -0.7825 [-0.8164, -0.7482] negative | -0.7955 [-0.8330, -0.7587] negative |
| 10 s no-drop: VPO_h(Topstep) | -0.4080 [-0.4213, -0.3939] negative | -0.3943 [-0.4126, -0.3756] negative | -0.4216 [-0.4433, -0.4004] negative |
| 60 s: fills with E_h (dropped) | 39602 (1) | 19302 (0) | 20300 (1) |
| 60 s: mean markout (ticks) | -0.5346 [-0.5620, -0.5056] negative | -0.5302 [-0.5786, -0.4827] negative | -0.5387 [-0.5905, -0.4878] negative |
| 60 s: median markout | -0.5000 | -0.5000 | -0.5000 |
| 60 s: mean c_half on these fills | -0.0137 [-0.0323, 0.0055] not distinguishable from 0 | -0.0152 [-0.0391, 0.0076] not distinguishable from 0 | -0.0123 [-0.0337, 0.0099] not distinguishable from 0 |
| 60 s: mean E_h | -0.5483 [-0.5827, -0.5152] negative | -0.5454 [-0.6003, -0.4898] negative | -0.5510 [-0.6076, -0.4947] negative |
| 60 s: median E_h | -0.5000 | -0.5000 | -0.5000 |
| 60 s: share E_h > 0 | 0.3907 [0.3861, 0.3953] | 0.3898 [0.3817, 0.3973] | 0.3915 [0.3839, 0.3992] |
| 60 s: mean N_h(Topstep) | -0.8123 [-0.8467, -0.7792] negative | -0.8094 [-0.8643, -0.7538] negative | -0.8150 [-0.8716, -0.7587] negative |
| 60 s: median N_h(Topstep) | -0.7640 | -0.7640 | -0.7640 |
| 60 s: VPO_h(Topstep) per resting order | -0.4199 [-0.4371, -0.4020] negative | -0.4079 [-0.4374, -0.3797] negative | -0.4320 [-0.4636, -0.3995] negative |
| 60 s no-drop: fills with E_h (dropped) | 39603 (0) | 19302 (0) | 20301 (0) |
| 60 s no-drop: mean E_h | -0.5484 [-0.5827, -0.5153] negative | -0.5454 [-0.6003, -0.4898] negative | -0.5512 [-0.6076, -0.4949] negative |
| 60 s no-drop: mean N_h(Topstep) | -0.8124 [-0.8467, -0.7793] negative | -0.8094 [-0.8643, -0.7538] negative | -0.8152 [-0.8716, -0.7589] negative |
| 60 s no-drop: VPO_h(Topstep) | -0.4200 [-0.4372, -0.4021] negative | -0.4079 [-0.4374, -0.3797] negative | -0.4320 [-0.4639, -0.3996] negative |

### (b) FIFO back of queue, ZM.v.1, OVERNIGHT

| statistic | pooled | buy | sell |
|---|---|---|---|
| placements | 206566 | 103283 | 103283 |
| fills (of which in the 50 ms cancel latency) | 19096 (32) | 9383 (20) | 9713 (12) |
| fills by trigger | queue 9359, through 9737 | queue 4593, through 4790 | queue 4766, through 4947 |
| fill rate | 0.0924 [0.0886, 0.0961] | 0.0908 [0.0868, 0.0947] | 0.0940 [0.0898, 0.0981] |
| touch rate | 0.2331 [0.2265, 0.2396] | 0.2345 [0.2272, 0.2415] | 0.2317 [0.2248, 0.2387] |
| stale share (best price at g differs from j) | 0.0142 [0.0134, 0.0150] | 0.0145 [0.0136, 0.0154] | 0.0139 [0.0130, 0.0149] |
| KM P(fill by 1 s) | 0.0013 [0.0011, 0.0015] | 0.0016 [0.0013, 0.0018] | 0.0010 [0.0008, 0.0013] |
| KM P(fill by 10 s) | 0.0185 [0.0175, 0.0195] | 0.0189 [0.0176, 0.0201] | 0.0182 [0.0170, 0.0194] |
| KM P(fill by 60 s) | 0.0923 [0.0884, 0.0959] | 0.0907 [0.0866, 0.0945] | 0.0939 [0.0897, 0.0980] |
| KM median time to fill (s) | not reached | not reached | not reached |
| KM censored before 60 s | 0 | 0 | 0 |
| mean c_half, all fills (ticks) | -0.0239 [-0.0475, -0.0021] negative | -0.0521 [-0.0797, -0.0258] negative | 0.0034 [-0.0240, 0.0286] not distinguishable from 0 |
| median c_half, all fills | 0.5000 | 0.5000 | 0.5000 |
| 1 s: fills with E_h (dropped) | 19096 (0) | 9383 (0) | 9713 (0) |
| 1 s: mean markout (ticks) | -0.5787 [-0.5972, -0.5592] negative | -0.5550 [-0.5822, -0.5238] negative | -0.6015 [-0.6237, -0.5803] negative |
| 1 s: median markout | -0.5000 | -0.5000 | -0.5000 |
| 1 s: mean c_half on these fills | -0.0239 [-0.0475, -0.0021] negative | -0.0521 [-0.0797, -0.0258] negative | 0.0034 [-0.0240, 0.0286] not distinguishable from 0 |
| 1 s: mean E_h | -0.6026 [-0.6333, -0.5735] negative | -0.6072 [-0.6447, -0.5660] negative | -0.5981 [-0.6317, -0.5692] negative |
| 1 s: median E_h | -0.5000 | -0.5000 | -0.5000 |
| 1 s: share E_h > 0 | 0.1827 [0.1756, 0.1898] | 0.1782 [0.1690, 0.1874] | 0.1870 [0.1778, 0.1957] |
| 1 s: mean N_h(Topstep) | -0.8666 [-0.8973, -0.8375] negative | -0.8712 [-0.9087, -0.8300] negative | -0.8621 [-0.8957, -0.8332] negative |
| 1 s: median N_h(Topstep) | -0.7640 | -0.7640 | -0.7640 |
| 1 s: VPO_h(Topstep) per resting order | -0.0801 [-0.0846, -0.0757] negative | -0.0791 [-0.0841, -0.0740] negative | -0.0811 [-0.0859, -0.0765] negative |
| 1 s no-drop: fills with E_h (dropped) | 19096 (0) | 9383 (0) | 9713 (0) |
| 1 s no-drop: mean E_h | -0.6026 [-0.6333, -0.5735] negative | -0.6072 [-0.6447, -0.5660] negative | -0.5981 [-0.6317, -0.5692] negative |
| 1 s no-drop: mean N_h(Topstep) | -0.8666 [-0.8973, -0.8375] negative | -0.8712 [-0.9087, -0.8300] negative | -0.8621 [-0.8957, -0.8332] negative |
| 1 s no-drop: VPO_h(Topstep) | -0.0801 [-0.0846, -0.0757] negative | -0.0791 [-0.0841, -0.0740] negative | -0.0811 [-0.0859, -0.0765] negative |
| 10 s: fills with E_h (dropped) | 19096 (0) | 9383 (0) | 9713 (0) |
| 10 s: mean markout (ticks) | -0.6067 [-0.6301, -0.5827] negative | -0.5913 [-0.6252, -0.5539] negative | -0.6215 [-0.6502, -0.5957] negative |
| 10 s: median markout | -0.5000 | -0.5000 | -0.5000 |
| 10 s: mean c_half on these fills | -0.0239 [-0.0475, -0.0021] negative | -0.0521 [-0.0797, -0.0258] negative | 0.0034 [-0.0240, 0.0286] not distinguishable from 0 |
| 10 s: mean E_h | -0.6306 [-0.6656, -0.5974] negative | -0.6434 [-0.6893, -0.5966] negative | -0.6181 [-0.6554, -0.5842] negative |
| 10 s: median E_h | -0.5000 | -0.5000 | -0.5000 |
| 10 s: share E_h > 0 | 0.2189 [0.2119, 0.2260] | 0.2141 [0.2052, 0.2234] | 0.2235 [0.2142, 0.2324] |
| 10 s: mean N_h(Topstep) | -0.8946 [-0.9296, -0.8614] negative | -0.9074 [-0.9533, -0.8606] negative | -0.8821 [-0.9194, -0.8482] negative |
| 10 s: median N_h(Topstep) | -0.7640 | -0.7640 | -0.7640 |
| 10 s: VPO_h(Topstep) per resting order | -0.0827 [-0.0872, -0.0780] negative | -0.0824 [-0.0882, -0.0768] negative | -0.0830 [-0.0879, -0.0782] negative |
| 10 s no-drop: fills with E_h (dropped) | 19096 (0) | 9383 (0) | 9713 (0) |
| 10 s no-drop: mean E_h | -0.6306 [-0.6656, -0.5974] negative | -0.6434 [-0.6893, -0.5966] negative | -0.6181 [-0.6554, -0.5842] negative |
| 10 s no-drop: mean N_h(Topstep) | -0.8946 [-0.9296, -0.8614] negative | -0.9074 [-0.9533, -0.8606] negative | -0.8821 [-0.9194, -0.8482] negative |
| 10 s no-drop: VPO_h(Topstep) | -0.0827 [-0.0872, -0.0780] negative | -0.0824 [-0.0882, -0.0768] negative | -0.0830 [-0.0879, -0.0782] negative |
| 60 s: fills with E_h (dropped) | 19096 (0) | 9383 (0) | 9713 (0) |
| 60 s: mean markout (ticks) | -0.6123 [-0.6454, -0.5799] negative | -0.6078 [-0.6557, -0.5577] negative | -0.6167 [-0.6598, -0.5753] negative |
| 60 s: median markout | -0.5000 | -0.5000 | -0.5000 |
| 60 s: mean c_half on these fills | -0.0239 [-0.0475, -0.0021] negative | -0.0521 [-0.0797, -0.0258] negative | 0.0034 [-0.0240, 0.0286] not distinguishable from 0 |
| 60 s: mean E_h | -0.6362 [-0.6780, -0.5974] negative | -0.6599 [-0.7161, -0.6041] negative | -0.6133 [-0.6611, -0.5669] negative |
| 60 s: median E_h | -0.5000 | -0.5000 | -0.5000 |
| 60 s: share E_h > 0 | 0.3055 [0.2988, 0.3128] | 0.3005 [0.2915, 0.3102] | 0.3103 [0.3011, 0.3201] |
| 60 s: mean N_h(Topstep) | -0.9002 [-0.9420, -0.8614] negative | -0.9239 [-0.9801, -0.8681] negative | -0.8773 [-0.9251, -0.8309] negative |
| 60 s: median N_h(Topstep) | -0.7640 | -0.7640 | -0.7640 |
| 60 s: VPO_h(Topstep) per resting order | -0.0832 [-0.0884, -0.0780] negative | -0.0839 [-0.0906, -0.0771] negative | -0.0825 [-0.0882, -0.0770] negative |
| 60 s no-drop: fills with E_h (dropped) | 19096 (0) | 9383 (0) | 9713 (0) |
| 60 s no-drop: mean E_h | -0.6362 [-0.6780, -0.5974] negative | -0.6599 [-0.7161, -0.6041] negative | -0.6133 [-0.6611, -0.5669] negative |
| 60 s no-drop: mean N_h(Topstep) | -0.9002 [-0.9420, -0.8614] negative | -0.9239 [-0.9801, -0.8681] negative | -0.8773 [-0.9251, -0.8309] negative |
| 60 s no-drop: VPO_h(Topstep) | -0.0832 [-0.0884, -0.0780] negative | -0.0839 [-0.0906, -0.0771] negative | -0.0825 [-0.0882, -0.0770] negative |

### (c) trade-through (gate), ZM.v.0, DAY

| statistic | pooled | buy | sell |
|---|---|---|---|
| placements | 85568 | 42784 | 42784 |
| fills (of which in the 50 ms cancel latency) | 44045 (46) | 21433 (26) | 22612 (20) |
| fills by trigger | queue 0, through 44045 | queue 0, through 21433 | queue 0, through 22612 |
| fill rate | 0.5147 [0.5090, 0.5201] | 0.5010 [0.4928, 0.5085] | 0.5285 [0.5200, 0.5362] |
| touch rate | 0.8047 [0.8013, 0.8081] | 0.7932 [0.7876, 0.7987] | 0.8163 [0.8110, 0.8214] |
| stale share (best price at g differs from j) | 0.0625 [0.0598, 0.0652] | 0.0621 [0.0591, 0.0652] | 0.0629 [0.0599, 0.0657] |
| KM P(fill by 1 s) | 0.0271 [0.0258, 0.0285] | 0.0259 [0.0242, 0.0277] | 0.0284 [0.0265, 0.0303] |
| KM P(fill by 10 s) | 0.2009 [0.1962, 0.2052] | 0.1883 [0.1825, 0.1938] | 0.2136 [0.2074, 0.2199] |
| KM P(fill by 60 s) | 0.5142 [0.5085, 0.5196] | 0.5004 [0.4922, 0.5079] | 0.5280 [0.5195, 0.5357] |
| KM median time to fill (s) | 55.937 | 59.959 | 51.640 |
| KM censored before 60 s | 0 | 0 | 0 |
| mean c_half, all fills (ticks) | -0.4251 [-0.4317, -0.4185] negative | -0.4388 [-0.4467, -0.4305] negative | -0.4121 [-0.4210, -0.4033] negative |
| median c_half, all fills | -0.5000 | -0.5000 | -0.5000 |
| 1 s: fills with E_h (dropped) | 44045 (0) | 21433 (0) | 22612 (0) |
| 1 s: mean markout (ticks) | -0.5285 [-0.5406, -0.5154] negative | -0.5240 [-0.5396, -0.5080] negative | -0.5329 [-0.5486, -0.5165] negative |
| 1 s: median markout | -0.5000 | -0.5000 | -0.5000 |
| 1 s: mean c_half on these fills | -0.4251 [-0.4317, -0.4185] negative | -0.4388 [-0.4467, -0.4305] negative | -0.4121 [-0.4210, -0.4033] negative |
| 1 s: mean E_h | -0.9536 [-0.9664, -0.9406] negative | -0.9627 [-0.9785, -0.9469] negative | -0.9449 [-0.9614, -0.9291] negative |
| 1 s: median E_h | -1.0000 | -1.0000 | -1.0000 |
| 1 s: share E_h > 0 | 0.0527 [0.0506, 0.0549] | 0.0514 [0.0485, 0.0542] | 0.0540 [0.0510, 0.0571] |
| 1 s: mean N_h(Topstep) | -1.2176 [-1.2304, -1.2046] negative | -1.2267 [-1.2425, -1.2109] negative | -1.2089 [-1.2254, -1.1931] negative |
| 1 s: median N_h(Topstep) | -1.2640 | -1.2640 | -1.2640 |
| 1 s: VPO_h(Topstep) per resting order | -0.6267 [-0.6370, -0.6158] negative | -0.6145 [-0.6269, -0.6012] negative | -0.6389 [-0.6533, -0.6238] negative |
| 1 s no-drop: fills with E_h (dropped) | 44045 (0) | 21433 (0) | 22612 (0) |
| 1 s no-drop: mean E_h | -0.9536 [-0.9664, -0.9406] negative | -0.9627 [-0.9785, -0.9469] negative | -0.9449 [-0.9614, -0.9291] negative |
| 1 s no-drop: mean N_h(Topstep) | -1.2176 [-1.2304, -1.2046] negative | -1.2267 [-1.2425, -1.2109] negative | -1.2089 [-1.2254, -1.1931] negative |
| 1 s no-drop: VPO_h(Topstep) | -0.6267 [-0.6370, -0.6158] negative | -0.6145 [-0.6269, -0.6012] negative | -0.6389 [-0.6533, -0.6238] negative |
| 10 s: fills with E_h (dropped) | 44045 (0) | 21433 (0) | 22612 (0) |
| 10 s: mean markout (ticks) | -0.5448 [-0.5633, -0.5256] negative | -0.5270 [-0.5522, -0.5001] negative | -0.5617 [-0.5921, -0.5312] negative |
| 10 s: median markout | -0.5000 | -0.5000 | -0.5000 |
| 10 s: mean c_half on these fills | -0.4251 [-0.4317, -0.4185] negative | -0.4388 [-0.4467, -0.4305] negative | -0.4121 [-0.4210, -0.4033] negative |
| 10 s: mean E_h | -0.9699 [-0.9884, -0.9502] negative | -0.9658 [-0.9913, -0.9385] negative | -0.9738 [-1.0047, -0.9425] negative |
| 10 s: median E_h | -1.0000 | -1.0000 | -1.0000 |
| 10 s: share E_h > 0 | 0.1877 [0.1838, 0.1915] | 0.1850 [0.1797, 0.1904] | 0.1902 [0.1845, 0.1958] |
| 10 s: mean N_h(Topstep) | -1.2339 [-1.2524, -1.2142] negative | -1.2298 [-1.2553, -1.2025] negative | -1.2378 [-1.2687, -1.2065] negative |
| 10 s: median N_h(Topstep) | -1.2640 | -1.2640 | -1.2640 |
| 10 s: VPO_h(Topstep) per resting order | -0.6351 [-0.6475, -0.6222] negative | -0.6161 [-0.6331, -0.5982] negative | -0.6542 [-0.6754, -0.6329] negative |
| 10 s no-drop: fills with E_h (dropped) | 44045 (0) | 21433 (0) | 22612 (0) |
| 10 s no-drop: mean E_h | -0.9699 [-0.9884, -0.9502] negative | -0.9658 [-0.9913, -0.9385] negative | -0.9738 [-1.0047, -0.9425] negative |
| 10 s no-drop: mean N_h(Topstep) | -1.2339 [-1.2524, -1.2142] negative | -1.2298 [-1.2553, -1.2025] negative | -1.2378 [-1.2687, -1.2065] negative |
| 10 s no-drop: VPO_h(Topstep) | -0.6351 [-0.6475, -0.6222] negative | -0.6161 [-0.6331, -0.5982] negative | -0.6542 [-0.6754, -0.6329] negative |
| 60 s: fills with E_h (dropped) | 44045 (0) | 21433 (0) | 22612 (0) |
| 60 s: mean markout (ticks) | -0.5539 [-0.5833, -0.5244] negative | -0.5632 [-0.6179, -0.5085] negative | -0.5450 [-0.5978, -0.4906] negative |
| 60 s: median markout | -0.5000 | -0.5000 | -0.5000 |
| 60 s: mean c_half on these fills | -0.4251 [-0.4317, -0.4185] negative | -0.4388 [-0.4467, -0.4305] negative | -0.4121 [-0.4210, -0.4033] negative |
| 60 s: mean E_h | -0.9789 [-1.0086, -0.9491] negative | -1.0020 [-1.0568, -0.9463] negative | -0.9570 [-1.0101, -0.9016] negative |
| 60 s: median E_h | -1.0000 | -1.0000 | -0.5000 |
| 60 s: share E_h > 0 | 0.3413 [0.3370, 0.3455] | 0.3329 [0.3258, 0.3398] | 0.3493 [0.3424, 0.3562] |
| 60 s: mean N_h(Topstep) | -1.2429 [-1.2726, -1.2131] negative | -1.2660 [-1.3208, -1.2103] negative | -1.2210 [-1.2741, -1.1656] negative |
| 60 s: median N_h(Topstep) | -1.2640 | -1.2640 | -0.7640 |
| 60 s: VPO_h(Topstep) per resting order | -0.6398 [-0.6564, -0.6220] negative | -0.6342 [-0.6664, -0.6033] negative | -0.6453 [-0.6785, -0.6107] negative |
| 60 s no-drop: fills with E_h (dropped) | 44045 (0) | 21433 (0) | 22612 (0) |
| 60 s no-drop: mean E_h | -0.9789 [-1.0086, -0.9491] negative | -1.0020 [-1.0568, -0.9463] negative | -0.9570 [-1.0101, -0.9016] negative |
| 60 s no-drop: mean N_h(Topstep) | -1.2429 [-1.2726, -1.2131] negative | -1.2660 [-1.3208, -1.2103] negative | -1.2210 [-1.2741, -1.1656] negative |
| 60 s no-drop: VPO_h(Topstep) | -0.6398 [-0.6564, -0.6220] negative | -0.6342 [-0.6664, -0.6033] negative | -0.6453 [-0.6785, -0.6107] negative |

### (c) trade-through (gate), ZM.v.0, OVERNIGHT

| statistic | pooled | buy | sell |
|---|---|---|---|
| placements | 230662 | 115331 | 115331 |
| fills (of which in the 50 ms cancel latency) | 30543 (53) | 15236 (27) | 15307 (26) |
| fills by trigger | queue 0, through 30543 | queue 0, through 15236 | queue 0, through 15307 |
| fill rate | 0.1324 [0.1288, 0.1361] | 0.1321 [0.1281, 0.1363] | 0.1327 [0.1288, 0.1368] |
| touch rate | 0.4063 [0.4015, 0.4113] | 0.4130 [0.4073, 0.4189] | 0.3996 [0.3940, 0.4056] |
| stale share (best price at g differs from j) | 0.0136 [0.0129, 0.0143] | 0.0136 [0.0128, 0.0144] | 0.0136 [0.0128, 0.0145] |
| KM P(fill by 1 s) | 0.0023 [0.0021, 0.0026] | 0.0025 [0.0022, 0.0028] | 0.0021 [0.0019, 0.0024] |
| KM P(fill by 10 s) | 0.0314 [0.0301, 0.0328] | 0.0316 [0.0300, 0.0333] | 0.0312 [0.0297, 0.0327] |
| KM P(fill by 60 s) | 0.1322 [0.1286, 0.1359] | 0.1319 [0.1279, 0.1361] | 0.1325 [0.1285, 0.1366] |
| KM median time to fill (s) | not reached | not reached | not reached |
| KM censored before 60 s | 0 | 0 | 0 |
| mean c_half, all fills (ticks) | -0.4057 [-0.4165, -0.3944] negative | -0.4401 [-0.4536, -0.4262] negative | -0.3714 [-0.3853, -0.3574] negative |
| median c_half, all fills | -0.5000 | -0.5000 | -0.5000 |
| 1 s: fills with E_h (dropped) | 30543 (0) | 15236 (0) | 15307 (0) |
| 1 s: mean markout (ticks) | -0.5640 [-0.5782, -0.5499] negative | -0.5363 [-0.5544, -0.5182] negative | -0.5916 [-0.6099, -0.5727] negative |
| 1 s: median markout | -0.5000 | -0.5000 | -0.5000 |
| 1 s: mean c_half on these fills | -0.4057 [-0.4165, -0.3944] negative | -0.4401 [-0.4536, -0.4262] negative | -0.3714 [-0.3853, -0.3574] negative |
| 1 s: mean E_h | -0.9697 [-0.9850, -0.9545] negative | -0.9764 [-0.9948, -0.9571] negative | -0.9630 [-0.9818, -0.9441] negative |
| 1 s: median E_h | -1.0000 | -1.0000 | -1.0000 |
| 1 s: share E_h > 0 | 0.0343 [0.0318, 0.0367] | 0.0322 [0.0290, 0.0355] | 0.0363 [0.0333, 0.0395] |
| 1 s: mean N_h(Topstep) | -1.2337 [-1.2490, -1.2185] negative | -1.2404 [-1.2588, -1.2211] negative | -1.2270 [-1.2458, -1.2081] negative |
| 1 s: median N_h(Topstep) | -1.2640 | -1.2640 | -1.2640 |
| 1 s: VPO_h(Topstep) per resting order | -0.1634 [-0.1691, -0.1580] negative | -0.1639 [-0.1703, -0.1579] negative | -0.1629 [-0.1693, -0.1567] negative |
| 1 s no-drop: fills with E_h (dropped) | 30543 (0) | 15236 (0) | 15307 (0) |
| 1 s no-drop: mean E_h | -0.9697 [-0.9850, -0.9545] negative | -0.9764 [-0.9948, -0.9571] negative | -0.9630 [-0.9818, -0.9441] negative |
| 1 s no-drop: mean N_h(Topstep) | -1.2337 [-1.2490, -1.2185] negative | -1.2404 [-1.2588, -1.2211] negative | -1.2270 [-1.2458, -1.2081] negative |
| 1 s no-drop: VPO_h(Topstep) | -0.1634 [-0.1691, -0.1580] negative | -0.1639 [-0.1703, -0.1579] negative | -0.1629 [-0.1693, -0.1567] negative |
| 10 s: fills with E_h (dropped) | 30543 (0) | 15236 (0) | 15307 (0) |
| 10 s: mean markout (ticks) | -0.5908 [-0.6082, -0.5747] negative | -0.5744 [-0.5983, -0.5513] negative | -0.6072 [-0.6299, -0.5851] negative |
| 10 s: median markout | -0.5000 | -0.5000 | -0.5000 |
| 10 s: mean c_half on these fills | -0.4057 [-0.4165, -0.3944] negative | -0.4401 [-0.4536, -0.4262] negative | -0.3714 [-0.3853, -0.3574] negative |
| 10 s: mean E_h | -0.9965 [-1.0149, -0.9793] negative | -1.0145 [-1.0378, -0.9907] negative | -0.9786 [-1.0013, -0.9560] negative |
| 10 s: median E_h | -1.0000 | -1.0000 | -1.0000 |
| 10 s: share E_h > 0 | 0.0815 [0.0776, 0.0852] | 0.0803 [0.0754, 0.0856] | 0.0826 [0.0779, 0.0872] |
| 10 s: mean N_h(Topstep) | -1.2605 [-1.2789, -1.2433] negative | -1.2785 [-1.3018, -1.2547] negative | -1.2426 [-1.2653, -1.2200] negative |
| 10 s: median N_h(Topstep) | -1.2640 | -1.2640 | -1.2640 |
| 10 s: VPO_h(Topstep) per resting order | -0.1669 [-0.1729, -0.1611] negative | -0.1689 [-0.1759, -0.1624] negative | -0.1649 [-0.1717, -0.1587] negative |
| 10 s no-drop: fills with E_h (dropped) | 30543 (0) | 15236 (0) | 15307 (0) |
| 10 s no-drop: mean E_h | -0.9965 [-1.0149, -0.9793] negative | -1.0145 [-1.0378, -0.9907] negative | -0.9786 [-1.0013, -0.9560] negative |
| 10 s no-drop: mean N_h(Topstep) | -1.2605 [-1.2789, -1.2433] negative | -1.2785 [-1.3018, -1.2547] negative | -1.2426 [-1.2653, -1.2200] negative |
| 10 s no-drop: VPO_h(Topstep) | -0.1669 [-0.1729, -0.1611] negative | -0.1689 [-0.1759, -0.1624] negative | -0.1649 [-0.1717, -0.1587] negative |
| 60 s: fills with E_h (dropped) | 30543 (0) | 15236 (0) | 15307 (0) |
| 60 s: mean markout (ticks) | -0.5814 [-0.6080, -0.5554] negative | -0.5557 [-0.5935, -0.5196] negative | -0.6069 [-0.6421, -0.5720] negative |
| 60 s: median markout | -0.5000 | -0.5000 | -0.5000 |
| 60 s: mean c_half on these fills | -0.4057 [-0.4165, -0.3944] negative | -0.4401 [-0.4536, -0.4262] negative | -0.3714 [-0.3853, -0.3574] negative |
| 60 s: mean E_h | -0.9871 [-1.0133, -0.9602] negative | -0.9958 [-1.0340, -0.9589] negative | -0.9784 [-1.0127, -0.9435] negative |
| 60 s: median E_h | -1.0000 | -1.0000 | -1.0000 |
| 60 s: share E_h > 0 | 0.2109 [0.2057, 0.2162] | 0.2056 [0.1987, 0.2127] | 0.2162 [0.2093, 0.2232] |
| 60 s: mean N_h(Topstep) | -1.2511 [-1.2773, -1.2242] negative | -1.2598 [-1.2980, -1.2229] negative | -1.2424 [-1.2767, -1.2075] negative |
| 60 s: median N_h(Topstep) | -1.2640 | -1.2640 | -1.2640 |
| 60 s: VPO_h(Topstep) per resting order | -0.1657 [-0.1722, -0.1592] negative | -0.1664 [-0.1745, -0.1588] negative | -0.1649 [-0.1724, -0.1573] negative |
| 60 s no-drop: fills with E_h (dropped) | 30543 (0) | 15236 (0) | 15307 (0) |
| 60 s no-drop: mean E_h | -0.9871 [-1.0133, -0.9602] negative | -0.9958 [-1.0340, -0.9589] negative | -0.9784 [-1.0127, -0.9435] negative |
| 60 s no-drop: mean N_h(Topstep) | -1.2511 [-1.2773, -1.2242] negative | -1.2598 [-1.2980, -1.2229] negative | -1.2424 [-1.2767, -1.2075] negative |
| 60 s no-drop: VPO_h(Topstep) | -0.1657 [-0.1722, -0.1592] negative | -0.1664 [-0.1745, -0.1588] negative | -0.1649 [-0.1724, -0.1573] negative |

### (c) trade-through (gate), ZM.v.1, DAY

| statistic | pooled | buy | sell |
|---|---|---|---|
| placements | 76608 | 38304 | 38304 |
| fills (of which in the 50 ms cancel latency) | 28537 (49) | 13832 (22) | 14705 (27) |
| fills by trigger | queue 0, through 28537 | queue 0, through 13832 | queue 0, through 14705 |
| fill rate | 0.3725 [0.3641, 0.3800] | 0.3611 [0.3517, 0.3702] | 0.3839 [0.3739, 0.3936] |
| touch rate | 0.6737 [0.6639, 0.6825] | 0.6620 [0.6510, 0.6718] | 0.6855 [0.6742, 0.6961] |
| stale share (best price at g differs from j) | 0.0656 [0.0627, 0.0685] | 0.0660 [0.0627, 0.0692] | 0.0653 [0.0620, 0.0685] |
| KM P(fill by 1 s) | 0.0102 [0.0093, 0.0110] | 0.0096 [0.0084, 0.0107] | 0.0108 [0.0096, 0.0120] |
| KM P(fill by 10 s) | 0.1054 [0.1013, 0.1093] | 0.0983 [0.0938, 0.1029] | 0.1125 [0.1069, 0.1178] |
| KM P(fill by 60 s) | 0.3719 [0.3635, 0.3793] | 0.3605 [0.3511, 0.3696] | 0.3832 [0.3731, 0.3930] |
| KM median time to fill (s) | not reached | not reached | not reached |
| KM censored before 60 s | 0 | 0 | 0 |
| mean c_half, all fills (ticks) | -0.7627 [-0.7805, -0.7450] negative | -0.7791 [-0.8041, -0.7556] negative | -0.7473 [-0.7672, -0.7268] negative |
| median c_half, all fills | -0.5000 | -0.5000 | -0.5000 |
| 1 s: fills with E_h (dropped) | 28537 (0) | 13832 (0) | 14705 (0) |
| 1 s: mean markout (ticks) | -0.4120 [-0.4260, -0.3968] negative | -0.4031 [-0.4224, -0.3825] negative | -0.4203 [-0.4391, -0.4019] negative |
| 1 s: median markout | -0.5000 | -0.5000 | -0.5000 |
| 1 s: mean c_half on these fills | -0.7627 [-0.7805, -0.7450] negative | -0.7791 [-0.8041, -0.7556] negative | -0.7473 [-0.7672, -0.7268] negative |
| 1 s: mean E_h | -1.1747 [-1.1957, -1.1519] negative | -1.1822 [-1.2099, -1.1533] negative | -1.1677 [-1.1953, -1.1406] negative |
| 1 s: median E_h | -1.0000 | -1.0000 | -1.0000 |
| 1 s: share E_h > 0 | 0.0364 [0.0338, 0.0390] | 0.0356 [0.0322, 0.0392] | 0.0371 [0.0339, 0.0406] |
| 1 s: mean N_h(Topstep) | -1.4387 [-1.4597, -1.4159] negative | -1.4462 [-1.4739, -1.4173] negative | -1.4317 [-1.4593, -1.4046] negative |
| 1 s: median N_h(Topstep) | -1.2640 | -1.2640 | -1.2640 |
| 1 s: VPO_h(Topstep) per resting order | -0.5359 [-0.5498, -0.5216] negative | -0.5222 [-0.5400, -0.5040] negative | -0.5496 [-0.5678, -0.5312] negative |
| 1 s no-drop: fills with E_h (dropped) | 28537 (0) | 13832 (0) | 14705 (0) |
| 1 s no-drop: mean E_h | -1.1747 [-1.1957, -1.1519] negative | -1.1822 [-1.2099, -1.1533] negative | -1.1677 [-1.1953, -1.1406] negative |
| 1 s no-drop: mean N_h(Topstep) | -1.4387 [-1.4597, -1.4159] negative | -1.4462 [-1.4739, -1.4173] negative | -1.4317 [-1.4593, -1.4046] negative |
| 1 s no-drop: VPO_h(Topstep) | -0.5359 [-0.5498, -0.5216] negative | -0.5222 [-0.5400, -0.5040] negative | -0.5496 [-0.5678, -0.5312] negative |
| 10 s: fills with E_h (dropped) | 28537 (0) | 13832 (0) | 14705 (0) |
| 10 s: mean markout (ticks) | -0.4235 [-0.4469, -0.3995] negative | -0.4067 [-0.4387, -0.3724] negative | -0.4393 [-0.4728, -0.4046] negative |
| 10 s: median markout | -0.5000 | -0.5000 | -0.5000 |
| 10 s: mean c_half on these fills | -0.7627 [-0.7805, -0.7450] negative | -0.7791 [-0.8041, -0.7556] negative | -0.7473 [-0.7672, -0.7268] negative |
| 10 s: mean E_h | -1.1863 [-1.2147, -1.1572] negative | -1.1858 [-1.2262, -1.1443] negative | -1.1867 [-1.2259, -1.1486] negative |
| 10 s: median E_h | -1.0000 | -1.0000 | -1.0000 |
| 10 s: share E_h > 0 | 0.1372 [0.1327, 0.1416] | 0.1362 [0.1302, 0.1422] | 0.1380 [0.1318, 0.1438] |
| 10 s: mean N_h(Topstep) | -1.4503 [-1.4787, -1.4212] negative | -1.4498 [-1.4902, -1.4083] negative | -1.4507 [-1.4899, -1.4126] negative |
| 10 s: median N_h(Topstep) | -1.2640 | -1.2640 | -1.2640 |
| 10 s: VPO_h(Topstep) per resting order | -0.5402 [-0.5554, -0.5244] negative | -0.5236 [-0.5431, -0.5027] negative | -0.5569 [-0.5795, -0.5346] negative |
| 10 s no-drop: fills with E_h (dropped) | 28537 (0) | 13832 (0) | 14705 (0) |
| 10 s no-drop: mean E_h | -1.1863 [-1.2147, -1.1572] negative | -1.1858 [-1.2262, -1.1443] negative | -1.1867 [-1.2259, -1.1486] negative |
| 10 s no-drop: mean N_h(Topstep) | -1.4503 [-1.4787, -1.4212] negative | -1.4498 [-1.4902, -1.4083] negative | -1.4507 [-1.4899, -1.4126] negative |
| 10 s no-drop: VPO_h(Topstep) | -0.5402 [-0.5554, -0.5244] negative | -0.5236 [-0.5431, -0.5027] negative | -0.5569 [-0.5795, -0.5346] negative |
| 60 s: fills with E_h (dropped) | 28536 (1) | 13832 (0) | 14704 (1) |
| 60 s: mean markout (ticks) | -0.4459 [-0.4821, -0.4087] negative | -0.4483 [-0.5071, -0.3875] negative | -0.4437 [-0.5055, -0.3844] negative |
| 60 s: median markout | -0.5000 | -0.5000 | -0.5000 |
| 60 s: mean c_half on these fills | -0.7627 [-0.7806, -0.7450] negative | -0.7791 [-0.8041, -0.7556] negative | -0.7473 [-0.7672, -0.7268] negative |
| 60 s: mean E_h | -1.2087 [-1.2479, -1.1686] negative | -1.2274 [-1.2924, -1.1614] negative | -1.1911 [-1.2562, -1.1285] negative |
| 60 s: median E_h | -1.0000 | -1.0000 | -1.0000 |
| 60 s: share E_h > 0 | 0.2940 [0.2889, 0.2993] | 0.2916 [0.2834, 0.2995] | 0.2962 [0.2882, 0.3042] |
| 60 s: mean N_h(Topstep) | -1.4727 [-1.5119, -1.4326] negative | -1.4914 [-1.5564, -1.4254] negative | -1.4551 [-1.5202, -1.3925] negative |
| 60 s: median N_h(Topstep) | -1.2640 | -1.2640 | -1.2640 |
| 60 s: VPO_h(Topstep) per resting order | -0.5486 [-0.5663, -0.5296] negative | -0.5386 [-0.5679, -0.5108] negative | -0.5586 [-0.5901, -0.5279] negative |
| 60 s no-drop: fills with E_h (dropped) | 28537 (0) | 13832 (0) | 14705 (0) |
| 60 s no-drop: mean E_h | -1.2088 [-1.2482, -1.1688] negative | -1.2274 [-1.2924, -1.1614] negative | -1.1913 [-1.2565, -1.1285] negative |
| 60 s no-drop: mean N_h(Topstep) | -1.4728 [-1.5122, -1.4328] negative | -1.4914 [-1.5564, -1.4254] negative | -1.4553 [-1.5205, -1.3925] negative |
| 60 s no-drop: VPO_h(Topstep) | -0.5486 [-0.5664, -0.5297] negative | -0.5386 [-0.5679, -0.5108] negative | -0.5587 [-0.5902, -0.5279] negative |

### (c) trade-through (gate), ZM.v.1, OVERNIGHT

| statistic | pooled | buy | sell |
|---|---|---|---|
| placements | 206566 | 103283 | 103283 |
| fills (of which in the 50 ms cancel latency) | 12014 (22) | 5844 (14) | 6170 (8) |
| fills by trigger | queue 0, through 12014 | queue 0, through 5844 | queue 0, through 6170 |
| fill rate | 0.0582 [0.0554, 0.0608] | 0.0566 [0.0538, 0.0593] | 0.0597 [0.0568, 0.0625] |
| touch rate | 0.2331 [0.2265, 0.2396] | 0.2345 [0.2272, 0.2415] | 0.2317 [0.2248, 0.2387] |
| stale share (best price at g differs from j) | 0.0142 [0.0134, 0.0150] | 0.0145 [0.0136, 0.0154] | 0.0139 [0.0130, 0.0149] |
| KM P(fill by 1 s) | 0.0006 [0.0005, 0.0008] | 0.0008 [0.0006, 0.0010] | 0.0005 [0.0004, 0.0007] |
| KM P(fill by 10 s) | 0.0106 [0.0099, 0.0112] | 0.0108 [0.0100, 0.0116] | 0.0103 [0.0095, 0.0112] |
| KM P(fill by 60 s) | 0.0581 [0.0554, 0.0607] | 0.0564 [0.0537, 0.0592] | 0.0597 [0.0567, 0.0624] |
| KM median time to fill (s) | not reached | not reached | not reached |
| KM censored before 60 s | 0 | 0 | 0 |
| mean c_half, all fills (ticks) | -0.6323 [-0.6587, -0.6061] negative | -0.6715 [-0.7023, -0.6399] negative | -0.5953 [-0.6275, -0.5654] negative |
| median c_half, all fills | -0.5000 | -0.5000 | -0.5000 |
| 1 s: fills with E_h (dropped) | 12014 (0) | 5844 (0) | 6170 (0) |
| 1 s: mean markout (ticks) | -0.5604 [-0.5832, -0.5375] negative | -0.5460 [-0.5791, -0.5135] negative | -0.5741 [-0.6036, -0.5431] negative |
| 1 s: median markout | -0.5000 | -0.5000 | -0.5000 |
| 1 s: mean c_half on these fills | -0.6323 [-0.6587, -0.6061] negative | -0.6715 [-0.7023, -0.6399] negative | -0.5953 [-0.6275, -0.5654] negative |
| 1 s: mean E_h | -1.1928 [-1.2248, -1.1640] negative | -1.2175 [-1.2563, -1.1800] negative | -1.1694 [-1.2079, -1.1355] negative |
| 1 s: median E_h | -1.0000 | -1.0000 | -1.0000 |
| 1 s: share E_h > 0 | 0.0431 [0.0387, 0.0479] | 0.0361 [0.0307, 0.0419] | 0.0498 [0.0435, 0.0560] |
| 1 s: mean N_h(Topstep) | -1.4568 [-1.4888, -1.4280] negative | -1.4815 [-1.5203, -1.4440] negative | -1.4334 [-1.4719, -1.3995] negative |
| 1 s: median N_h(Topstep) | -1.2640 | -1.2640 | -1.2640 |
| 1 s: VPO_h(Topstep) per resting order | -0.0847 [-0.0894, -0.0802] negative | -0.0838 [-0.0889, -0.0789] negative | -0.0856 [-0.0907, -0.0806] negative |
| 1 s no-drop: fills with E_h (dropped) | 12014 (0) | 5844 (0) | 6170 (0) |
| 1 s no-drop: mean E_h | -1.1928 [-1.2248, -1.1640] negative | -1.2175 [-1.2563, -1.1800] negative | -1.1694 [-1.2079, -1.1355] negative |
| 1 s no-drop: mean N_h(Topstep) | -1.4568 [-1.4888, -1.4280] negative | -1.4815 [-1.5203, -1.4440] negative | -1.4334 [-1.4719, -1.3995] negative |
| 1 s no-drop: VPO_h(Topstep) | -0.0847 [-0.0894, -0.0802] negative | -0.0838 [-0.0889, -0.0789] negative | -0.0856 [-0.0907, -0.0806] negative |
| 10 s: fills with E_h (dropped) | 12014 (0) | 5844 (0) | 6170 (0) |
| 10 s: mean markout (ticks) | -0.5945 [-0.6255, -0.5648] negative | -0.5975 [-0.6416, -0.5558] negative | -0.5917 [-0.6321, -0.5550] negative |
| 10 s: median markout | -0.5000 | -0.5000 | -0.5000 |
| 10 s: mean c_half on these fills | -0.6323 [-0.6587, -0.6061] negative | -0.6715 [-0.7023, -0.6399] negative | -0.5953 [-0.6275, -0.5654] negative |
| 10 s: mean E_h | -1.2268 [-1.2669, -1.1921] negative | -1.2689 [-1.3205, -1.2199] negative | -1.1870 [-1.2327, -1.1463] negative |
| 10 s: median E_h | -1.0000 | -1.0000 | -1.0000 |
| 10 s: share E_h > 0 | 0.0832 [0.0777, 0.0887] | 0.0763 [0.0690, 0.0837] | 0.0898 [0.0823, 0.0973] |
| 10 s: mean N_h(Topstep) | -1.4908 [-1.5309, -1.4561] negative | -1.5329 [-1.5845, -1.4839] negative | -1.4510 [-1.4967, -1.4103] negative |
| 10 s: median N_h(Topstep) | -1.2640 | -1.2640 | -1.2640 |
| 10 s: VPO_h(Topstep) per resting order | -0.0867 [-0.0915, -0.0819] negative | -0.0867 [-0.0925, -0.0813] negative | -0.0867 [-0.0919, -0.0817] negative |
| 10 s no-drop: fills with E_h (dropped) | 12014 (0) | 5844 (0) | 6170 (0) |
| 10 s no-drop: mean E_h | -1.2268 [-1.2669, -1.1921] negative | -1.2689 [-1.3205, -1.2199] negative | -1.1870 [-1.2327, -1.1463] negative |
| 10 s no-drop: mean N_h(Topstep) | -1.4908 [-1.5309, -1.4561] negative | -1.5329 [-1.5845, -1.4839] negative | -1.4510 [-1.4967, -1.4103] negative |
| 10 s no-drop: VPO_h(Topstep) | -0.0867 [-0.0915, -0.0819] negative | -0.0867 [-0.0925, -0.0813] negative | -0.0867 [-0.0919, -0.0817] negative |
| 60 s: fills with E_h (dropped) | 12014 (0) | 5844 (0) | 6170 (0) |
| 60 s: mean markout (ticks) | -0.6010 [-0.6466, -0.5548] negative | -0.5899 [-0.6565, -0.5250] negative | -0.6114 [-0.6710, -0.5529] negative |
| 60 s: median markout | -0.5000 | -0.5000 | -0.5000 |
| 60 s: mean c_half on these fills | -0.6323 [-0.6587, -0.6061] negative | -0.6715 [-0.7023, -0.6399] negative | -0.5953 [-0.6275, -0.5654] negative |
| 60 s: mean E_h | -1.2333 [-1.2863, -1.1862] negative | -1.2614 [-1.3368, -1.1934] negative | -1.2067 [-1.2671, -1.1488] negative |
| 60 s: median E_h | -1.0000 | -1.0000 | -1.0000 |
| 60 s: share E_h > 0 | 0.1895 [0.1821, 0.1973] | 0.1899 [0.1795, 0.2009] | 0.1891 [0.1790, 0.1996] |
| 60 s: mean N_h(Topstep) | -1.4973 [-1.5503, -1.4502] negative | -1.5254 [-1.6008, -1.4574] negative | -1.4707 [-1.5311, -1.4128] negative |
| 60 s: median N_h(Topstep) | -1.2640 | -1.2640 | -1.2640 |
| 60 s: VPO_h(Topstep) per resting order | -0.0871 [-0.0922, -0.0818] negative | -0.0863 [-0.0928, -0.0799] negative | -0.0879 [-0.0935, -0.0823] negative |
| 60 s no-drop: fills with E_h (dropped) | 12014 (0) | 5844 (0) | 6170 (0) |
| 60 s no-drop: mean E_h | -1.2333 [-1.2863, -1.1862] negative | -1.2614 [-1.3368, -1.1934] negative | -1.2067 [-1.2671, -1.1488] negative |
| 60 s no-drop: mean N_h(Topstep) | -1.4973 [-1.5503, -1.4502] negative | -1.5254 [-1.6008, -1.4574] negative | -1.4707 [-1.5311, -1.4128] negative |
| 60 s no-drop: VPO_h(Topstep) | -0.0871 [-0.0922, -0.0818] negative | -0.0863 [-0.0928, -0.0799] negative | -0.0879 [-0.0935, -0.0823] negative |

## Model (a), trade dates from 2023-11-01 alone (spec 3.1; decides nothing)

82 trade dates; intervals resample trade dates on or after 2023-11-01 only.

### (a) K from 2023-11-01, ZM.v.0, DAY

| statistic | pooled | buy | sell |
|---|---|---|---|
| placements | 8176 | 4088 | 4088 |
| fills (of which in the 50 ms cancel latency) | 5871 (1) | 2923 (0) | 2948 (1) |
| fills by trigger | queue 4760, through 1111 | queue 2384, through 539 | queue 2376, through 572 |
| fill rate | 0.7181 [0.7081, 0.7276] | 0.7150 [0.6964, 0.7343] | 0.7211 [0.7028, 0.7401] |
| touch rate | 0.8146 [0.8060, 0.8233] | 0.8063 [0.7879, 0.8239] | 0.8229 [0.8083, 0.8371] |
| stale share (best price at g differs from j) | 0.0718 [0.0624, 0.0819] | 0.0727 [0.0627, 0.0831] | 0.0709 [0.0600, 0.0830] |
| KM P(fill by 1 s) | 0.0668 [0.0591, 0.0741] | 0.0619 [0.0531, 0.0705] | 0.0717 [0.0608, 0.0827] |
| KM P(fill by 10 s) | 0.3772 [0.3619, 0.3925] | 0.3650 [0.3432, 0.3867] | 0.3894 [0.3668, 0.4129] |
| KM P(fill by 60 s) | 0.7180 [0.7078, 0.7275] | 0.7150 [0.6964, 0.7343] | 0.7209 [0.7025, 0.7398] |
| KM median time to fill (s) | 17.930 | 18.981 | 16.920 |
| KM censored before 60 s | 0 | 0 | 0 |
| mean c_half, all fills (ticks) | 0.3669 [0.3485, 0.3858] positive | 0.3724 [0.3531, 0.3917] positive | 0.3614 [0.3333, 0.3903] positive |
| median c_half, all fills | 0.5000 | 0.5000 | 0.5000 |
| 1 s: fills with E_h (dropped) | 5871 (0) | 2923 (0) | 2948 (0) |
| 1 s: mean markout (ticks) | -0.5999 [-0.6267, -0.5752] negative | -0.6083 [-0.6452, -0.5736] negative | -0.5916 [-0.6257, -0.5605] negative |
| 1 s: median markout | -0.5000 | -0.5000 | -0.5000 |
| 1 s: mean c_half on these fills | 0.3669 [0.3485, 0.3858] positive | 0.3724 [0.3531, 0.3917] positive | 0.3614 [0.3333, 0.3903] positive |
| 1 s: mean E_h | -0.2330 [-0.2662, -0.1985] negative | -0.2359 [-0.2781, -0.1945] negative | -0.2302 [-0.2743, -0.1873] negative |
| 1 s: median E_h | 0.0000 | 0.0000 | 0.0000 |
| 1 s: share E_h > 0 | 0.2931 [0.2751, 0.3117] | 0.2918 [0.2711, 0.3129] | 0.2944 [0.2724, 0.3167] |
| 1 s: mean N_h(Topstep) | -0.4970 [-0.5302, -0.4625] negative | -0.4999 [-0.5421, -0.4585] negative | -0.4942 [-0.5383, -0.4513] negative |
| 1 s: median N_h(Topstep) | -0.2640 | -0.2640 | -0.2640 |
| 1 s: VPO_h(Topstep) per resting order | -0.3569 [-0.3813, -0.3319] negative | -0.3574 [-0.3894, -0.3265] negative | -0.3564 [-0.3911, -0.3230] negative |
| 1 s no-drop: fills with E_h (dropped) | 5871 (0) | 2923 (0) | 2948 (0) |
| 1 s no-drop: mean E_h | -0.2330 [-0.2662, -0.1985] negative | -0.2359 [-0.2781, -0.1945] negative | -0.2302 [-0.2743, -0.1873] negative |
| 1 s no-drop: mean N_h(Topstep) | -0.4970 [-0.5302, -0.4625] negative | -0.4999 [-0.5421, -0.4585] negative | -0.4942 [-0.5383, -0.4513] negative |
| 1 s no-drop: VPO_h(Topstep) | -0.3569 [-0.3813, -0.3319] negative | -0.3574 [-0.3894, -0.3265] negative | -0.3564 [-0.3911, -0.3230] negative |
| 10 s: fills with E_h (dropped) | 5871 (0) | 2923 (0) | 2948 (0) |
| 10 s: mean markout (ticks) | -0.6476 [-0.6919, -0.6034] negative | -0.6988 [-0.7532, -0.6436] negative | -0.5968 [-0.6575, -0.5373] negative |
| 10 s: median markout | -0.5000 | -0.5000 | -0.5000 |
| 10 s: mean c_half on these fills | 0.3669 [0.3485, 0.3858] positive | 0.3724 [0.3531, 0.3917] positive | 0.3614 [0.3333, 0.3903] positive |
| 10 s: mean E_h | -0.2807 [-0.3291, -0.2306] negative | -0.3264 [-0.3843, -0.2663] negative | -0.2354 [-0.3009, -0.1687] negative |
| 10 s: median E_h | -0.5000 | -0.5000 | 0.0000 |
| 10 s: share E_h > 0 | 0.3817 [0.3643, 0.3995] | 0.3644 [0.3420, 0.3856] | 0.3989 [0.3780, 0.4201] |
| 10 s: mean N_h(Topstep) | -0.5447 [-0.5931, -0.4946] negative | -0.5904 [-0.6483, -0.5303] negative | -0.4994 [-0.5649, -0.4327] negative |
| 10 s: median N_h(Topstep) | -0.7640 | -0.7640 | -0.2640 |
| 10 s: VPO_h(Topstep) per resting order | -0.3911 [-0.4257, -0.3564] negative | -0.4221 [-0.4664, -0.3774] negative | -0.3601 [-0.4091, -0.3099] negative |
| 10 s no-drop: fills with E_h (dropped) | 5871 (0) | 2923 (0) | 2948 (0) |
| 10 s no-drop: mean E_h | -0.2807 [-0.3291, -0.2306] negative | -0.3264 [-0.3843, -0.2663] negative | -0.2354 [-0.3009, -0.1687] negative |
| 10 s no-drop: mean N_h(Topstep) | -0.5447 [-0.5931, -0.4946] negative | -0.5904 [-0.6483, -0.5303] negative | -0.4994 [-0.5649, -0.4327] negative |
| 10 s no-drop: VPO_h(Topstep) | -0.3911 [-0.4257, -0.3564] negative | -0.4221 [-0.4664, -0.3774] negative | -0.3601 [-0.4091, -0.3099] negative |
| 60 s: fills with E_h (dropped) | 5871 (0) | 2923 (0) | 2948 (0) |
| 60 s: mean markout (ticks) | -0.6910 [-0.7532, -0.6296] negative | -0.8414 [-0.9814, -0.6928] negative | -0.5419 [-0.6922, -0.4089] negative |
| 60 s: median markout | -0.5000 | -1.0000 | -0.5000 |
| 60 s: mean c_half on these fills | 0.3669 [0.3485, 0.3858] positive | 0.3724 [0.3531, 0.3917] positive | 0.3614 [0.3333, 0.3903] positive |
| 60 s: mean E_h | -0.3241 [-0.3887, -0.2603] negative | -0.4690 [-0.6173, -0.3148] negative | -0.1805 [-0.3337, -0.0428] negative |
| 60 s: median E_h | -0.5000 | -0.5000 | 0.0000 |
| 60 s: share E_h > 0 | 0.4425 [0.4322, 0.4528] | 0.4211 [0.4001, 0.4445] | 0.4637 [0.4435, 0.4819] |
| 60 s: mean N_h(Topstep) | -0.5881 [-0.6527, -0.5243] negative | -0.7330 [-0.8813, -0.5788] negative | -0.4445 [-0.5977, -0.3068] negative |
| 60 s: median N_h(Topstep) | -0.7640 | -0.7640 | -0.2640 |
| 60 s: VPO_h(Topstep) per resting order | -0.4223 [-0.4690, -0.3776] negative | -0.5241 [-0.6334, -0.4093] negative | -0.3205 [-0.4357, -0.2197] negative |
| 60 s no-drop: fills with E_h (dropped) | 5871 (0) | 2923 (0) | 2948 (0) |
| 60 s no-drop: mean E_h | -0.3241 [-0.3887, -0.2603] negative | -0.4690 [-0.6173, -0.3148] negative | -0.1805 [-0.3337, -0.0428] negative |
| 60 s no-drop: mean N_h(Topstep) | -0.5881 [-0.6527, -0.5243] negative | -0.7330 [-0.8813, -0.5788] negative | -0.4445 [-0.5977, -0.3068] negative |
| 60 s no-drop: VPO_h(Topstep) | -0.4223 [-0.4690, -0.3776] negative | -0.5241 [-0.6334, -0.4093] negative | -0.3205 [-0.4357, -0.2197] negative |

### (a) K from 2023-11-01, ZM.v.0, OVERNIGHT

| statistic | pooled | buy | sell |
|---|---|---|---|
| placements | 22046 | 11023 | 11023 |
| fills (of which in the 50 ms cancel latency) | 4330 (16) | 2032 (8) | 2298 (8) |
| fills by trigger | queue 2589, through 1741 | queue 1216, through 816 | queue 1373, through 925 |
| fill rate | 0.1964 [0.1852, 0.2083] | 0.1843 [0.1723, 0.1966] | 0.2085 [0.1948, 0.2227] |
| touch rate | 0.3989 [0.3846, 0.4134] | 0.3937 [0.3768, 0.4097] | 0.4042 [0.3884, 0.4203] |
| stale share (best price at g differs from j) | 0.0108 [0.0090, 0.0126] | 0.0111 [0.0089, 0.0132] | 0.0105 [0.0084, 0.0126] |
| KM P(fill by 1 s) | 0.0044 [0.0034, 0.0054] | 0.0047 [0.0033, 0.0062] | 0.0040 [0.0028, 0.0052] |
| KM P(fill by 10 s) | 0.0432 [0.0394, 0.0473] | 0.0403 [0.0357, 0.0453] | 0.0462 [0.0414, 0.0509] |
| KM P(fill by 60 s) | 0.1957 [0.1843, 0.2076] | 0.1836 [0.1715, 0.1959] | 0.2077 [0.1941, 0.2222] |
| KM median time to fill (s) | not reached | not reached | not reached |
| KM censored before 60 s | 0 | 0 | 0 |
| mean c_half, all fills (ticks) | 0.1726 [0.1463, 0.2001] positive | 0.1565 [0.1261, 0.1878] positive | 0.1869 [0.1500, 0.2225] positive |
| median c_half, all fills | 0.5000 | 0.5000 | 0.5000 |
| 1 s: fills with E_h (dropped) | 4330 (0) | 2032 (0) | 2298 (0) |
| 1 s: mean markout (ticks) | -0.5898 [-0.6130, -0.5644] negative | -0.5861 [-0.6183, -0.5524] negative | -0.5931 [-0.6303, -0.5547] negative |
| 1 s: median markout | -0.5000 | -0.5000 | -0.5000 |
| 1 s: mean c_half on these fills | 0.1726 [0.1463, 0.2001] positive | 0.1565 [0.1261, 0.1878] positive | 0.1869 [0.1500, 0.2225] positive |
| 1 s: mean E_h | -0.4172 [-0.4522, -0.3785] negative | -0.4296 [-0.4742, -0.3785] negative | -0.4062 [-0.4496, -0.3600] negative |
| 1 s: median E_h | -0.5000 | -0.5000 | -0.5000 |
| 1 s: share E_h > 0 | 0.1841 [0.1710, 0.1997] | 0.1806 [0.1589, 0.2045] | 0.1871 [0.1700, 0.2051] |
| 1 s: mean N_h(Topstep) | -0.6812 [-0.7162, -0.6425] negative | -0.6936 [-0.7382, -0.6425] negative | -0.6702 [-0.7136, -0.6240] negative |
| 1 s: median N_h(Topstep) | -0.7640 | -0.7640 | -0.7640 |
| 1 s: VPO_h(Topstep) per resting order | -0.1338 [-0.1454, -0.1220] negative | -0.1279 [-0.1400, -0.1149] negative | -0.1397 [-0.1543, -0.1253] negative |
| 1 s no-drop: fills with E_h (dropped) | 4330 (0) | 2032 (0) | 2298 (0) |
| 1 s no-drop: mean E_h | -0.4172 [-0.4522, -0.3785] negative | -0.4296 [-0.4742, -0.3785] negative | -0.4062 [-0.4496, -0.3600] negative |
| 1 s no-drop: mean N_h(Topstep) | -0.6812 [-0.7162, -0.6425] negative | -0.6936 [-0.7382, -0.6425] negative | -0.6702 [-0.7136, -0.6240] negative |
| 1 s no-drop: VPO_h(Topstep) | -0.1338 [-0.1454, -0.1220] negative | -0.1279 [-0.1400, -0.1149] negative | -0.1397 [-0.1543, -0.1253] negative |
| 10 s: fills with E_h (dropped) | 4330 (0) | 2032 (0) | 2298 (0) |
| 10 s: mean markout (ticks) | -0.5970 [-0.6276, -0.5643] negative | -0.5893 [-0.6317, -0.5479] negative | -0.6038 [-0.6557, -0.5540] negative |
| 10 s: median markout | -0.5000 | -0.5000 | -0.5000 |
| 10 s: mean c_half on these fills | 0.1726 [0.1463, 0.2001] positive | 0.1565 [0.1261, 0.1878] positive | 0.1869 [0.1500, 0.2225] positive |
| 10 s: mean E_h | -0.4244 [-0.4672, -0.3776] negative | -0.4328 [-0.4820, -0.3775] negative | -0.4169 [-0.4775, -0.3552] negative |
| 10 s: median E_h | -0.5000 | -0.5000 | -0.5000 |
| 10 s: share E_h > 0 | 0.2400 [0.2256, 0.2555] | 0.2377 [0.2160, 0.2599] | 0.2419 [0.2223, 0.2617] |
| 10 s: mean N_h(Topstep) | -0.6884 [-0.7312, -0.6416] negative | -0.6968 [-0.7460, -0.6415] negative | -0.6809 [-0.7415, -0.6192] negative |
| 10 s: median N_h(Topstep) | -0.7640 | -0.7640 | -0.7640 |
| 10 s: VPO_h(Topstep) per resting order | -0.1352 [-0.1479, -0.1223] negative | -0.1285 [-0.1413, -0.1152] negative | -0.1419 [-0.1606, -0.1250] negative |
| 10 s no-drop: fills with E_h (dropped) | 4330 (0) | 2032 (0) | 2298 (0) |
| 10 s no-drop: mean E_h | -0.4244 [-0.4672, -0.3776] negative | -0.4328 [-0.4820, -0.3775] negative | -0.4169 [-0.4775, -0.3552] negative |
| 10 s no-drop: mean N_h(Topstep) | -0.6884 [-0.7312, -0.6416] negative | -0.6968 [-0.7460, -0.6415] negative | -0.6809 [-0.7415, -0.6192] negative |
| 10 s no-drop: VPO_h(Topstep) | -0.1352 [-0.1479, -0.1223] negative | -0.1285 [-0.1413, -0.1152] negative | -0.1419 [-0.1606, -0.1250] negative |
| 60 s: fills with E_h (dropped) | 4330 (0) | 2032 (0) | 2298 (0) |
| 60 s: mean markout (ticks) | -0.6184 [-0.6635, -0.5705] negative | -0.6307 [-0.7062, -0.5549] negative | -0.6075 [-0.6883, -0.5234] negative |
| 60 s: median markout | -0.5000 | -0.5000 | -0.5000 |
| 60 s: mean c_half on these fills | 0.1726 [0.1463, 0.2001] positive | 0.1565 [0.1261, 0.1878] positive | 0.1869 [0.1500, 0.2225] positive |
| 60 s: mean E_h | -0.4457 [-0.5013, -0.3866] negative | -0.4742 [-0.5517, -0.3936] negative | -0.4206 [-0.5061, -0.3299] negative |
| 60 s: median E_h | -0.5000 | -0.5000 | -0.5000 |
| 60 s: share E_h > 0 | 0.3330 [0.3162, 0.3502] | 0.3268 [0.3036, 0.3519] | 0.3386 [0.3168, 0.3610] |
| 60 s: mean N_h(Topstep) | -0.7097 [-0.7653, -0.6506] negative | -0.7382 [-0.8157, -0.6576] negative | -0.6846 [-0.7701, -0.5939] negative |
| 60 s: median N_h(Topstep) | -0.7640 | -0.7640 | -0.7640 |
| 60 s: VPO_h(Topstep) per resting order | -0.1394 [-0.1538, -0.1252] negative | -0.1361 [-0.1503, -0.1204] negative | -0.1427 [-0.1661, -0.1200] negative |
| 60 s no-drop: fills with E_h (dropped) | 4330 (0) | 2032 (0) | 2298 (0) |
| 60 s no-drop: mean E_h | -0.4457 [-0.5013, -0.3866] negative | -0.4742 [-0.5517, -0.3936] negative | -0.4206 [-0.5061, -0.3299] negative |
| 60 s no-drop: mean N_h(Topstep) | -0.7097 [-0.7653, -0.6506] negative | -0.7382 [-0.8157, -0.6576] negative | -0.6846 [-0.7701, -0.5939] negative |
| 60 s no-drop: VPO_h(Topstep) | -0.1394 [-0.1538, -0.1252] negative | -0.1361 [-0.1503, -0.1204] negative | -0.1427 [-0.1661, -0.1200] negative |

### (a) K from 2023-11-01, ZM.v.1, DAY

| statistic | pooled | buy | sell |
|---|---|---|---|
| placements | 7616 | 3808 | 3808 |
| fills (of which in the 50 ms cancel latency) | 4359 (6) | 2157 (1) | 2202 (5) |
| fills by trigger | queue 2641, through 1718 | queue 1299, through 858 | queue 1342, through 860 |
| fill rate | 0.5723 [0.5350, 0.6045] | 0.5664 [0.5269, 0.6001] | 0.5783 [0.5389, 0.6147] |
| touch rate | 0.7212 [0.6859, 0.7492] | 0.7148 [0.6801, 0.7434] | 0.7277 [0.6875, 0.7621] |
| stale share (best price at g differs from j) | 0.0708 [0.0603, 0.0821] | 0.0754 [0.0629, 0.0877] | 0.0662 [0.0552, 0.0779] |
| KM P(fill by 1 s) | 0.0277 [0.0231, 0.0325] | 0.0281 [0.0224, 0.0338] | 0.0273 [0.0212, 0.0340] |
| KM P(fill by 10 s) | 0.2193 [0.1976, 0.2392] | 0.2169 [0.1943, 0.2385] | 0.2216 [0.1969, 0.2457] |
| KM P(fill by 60 s) | 0.5716 [0.5346, 0.6036] | 0.5662 [0.5264, 0.6000] | 0.5769 [0.5373, 0.6133] |
| KM median time to fill (s) | 41.007 | 42.806 | 39.256 |
| KM censored before 60 s | 0 | 0 | 0 |
| mean c_half, all fills (ticks) | 0.0752 [0.0392, 0.1085] positive | 0.0403 [-0.0053, 0.0844] not distinguishable from 0 | 0.1094 [0.0661, 0.1509] positive |
| median c_half, all fills | 0.5000 | 0.5000 | 0.5000 |
| 1 s: fills with E_h (dropped) | 4359 (0) | 2157 (0) | 2202 (0) |
| 1 s: mean markout (ticks) | -0.5164 [-0.5485, -0.4862] negative | -0.4963 [-0.5345, -0.4572] negative | -0.5361 [-0.5841, -0.4935] negative |
| 1 s: median markout | -0.5000 | -0.5000 | -0.5000 |
| 1 s: mean c_half on these fills | 0.0752 [0.0392, 0.1085] positive | 0.0403 [-0.0053, 0.0844] not distinguishable from 0 | 0.1094 [0.0661, 0.1509] positive |
| 1 s: mean E_h | -0.4412 [-0.4860, -0.3991] negative | -0.4560 [-0.5101, -0.4016] negative | -0.4267 [-0.4857, -0.3734] negative |
| 1 s: median E_h | -0.5000 | -0.5000 | -0.5000 |
| 1 s: share E_h > 0 | 0.2191 [0.2037, 0.2344] | 0.2179 [0.1988, 0.2371] | 0.2203 [0.1987, 0.2418] |
| 1 s: mean N_h(Topstep) | -0.7052 [-0.7500, -0.6631] negative | -0.7200 [-0.7741, -0.6656] negative | -0.6907 [-0.7497, -0.6374] negative |
| 1 s: median N_h(Topstep) | -0.7640 | -0.7640 | -0.7640 |
| 1 s: VPO_h(Topstep) per resting order | -0.4036 [-0.4356, -0.3722] negative | -0.4078 [-0.4487, -0.3648] negative | -0.3994 [-0.4404, -0.3605] negative |
| 1 s no-drop: fills with E_h (dropped) | 4359 (0) | 2157 (0) | 2202 (0) |
| 1 s no-drop: mean E_h | -0.4412 [-0.4860, -0.3991] negative | -0.4560 [-0.5101, -0.4016] negative | -0.4267 [-0.4857, -0.3734] negative |
| 1 s no-drop: mean N_h(Topstep) | -0.7052 [-0.7500, -0.6631] negative | -0.7200 [-0.7741, -0.6656] negative | -0.6907 [-0.7497, -0.6374] negative |
| 1 s no-drop: VPO_h(Topstep) | -0.4036 [-0.4356, -0.3722] negative | -0.4078 [-0.4487, -0.3648] negative | -0.3994 [-0.4404, -0.3605] negative |
| 10 s: fills with E_h (dropped) | 4359 (0) | 2157 (0) | 2202 (0) |
| 10 s: mean markout (ticks) | -0.5420 [-0.5874, -0.4982] negative | -0.5598 [-0.6247, -0.4912] negative | -0.5245 [-0.5933, -0.4577] negative |
| 10 s: median markout | -0.5000 | -0.5000 | -0.5000 |
| 10 s: mean c_half on these fills | 0.0752 [0.0392, 0.1085] positive | 0.0403 [-0.0053, 0.0844] not distinguishable from 0 | 0.1094 [0.0661, 0.1509] positive |
| 10 s: mean E_h | -0.4667 [-0.5191, -0.4146] negative | -0.5195 [-0.5899, -0.4405] negative | -0.4151 [-0.4904, -0.3398] negative |
| 10 s: median E_h | -0.5000 | -0.5000 | -0.5000 |
| 10 s: share E_h > 0 | 0.3102 [0.2951, 0.3242] | 0.2990 [0.2801, 0.3189] | 0.3211 [0.2997, 0.3424] |
| 10 s: mean N_h(Topstep) | -0.7307 [-0.7831, -0.6786] negative | -0.7835 [-0.8539, -0.7045] negative | -0.6791 [-0.7544, -0.6038] negative |
| 10 s: median N_h(Topstep) | -0.7640 | -0.7640 | -0.7640 |
| 10 s: VPO_h(Topstep) per resting order | -0.4182 [-0.4539, -0.3794] negative | -0.4438 [-0.4950, -0.3870] negative | -0.3927 [-0.4398, -0.3426] negative |
| 10 s no-drop: fills with E_h (dropped) | 4359 (0) | 2157 (0) | 2202 (0) |
| 10 s no-drop: mean E_h | -0.4667 [-0.5191, -0.4146] negative | -0.5195 [-0.5899, -0.4405] negative | -0.4151 [-0.4904, -0.3398] negative |
| 10 s no-drop: mean N_h(Topstep) | -0.7307 [-0.7831, -0.6786] negative | -0.7835 [-0.8539, -0.7045] negative | -0.6791 [-0.7544, -0.6038] negative |
| 10 s no-drop: VPO_h(Topstep) | -0.4182 [-0.4539, -0.3794] negative | -0.4438 [-0.4950, -0.3870] negative | -0.3927 [-0.4398, -0.3426] negative |
| 60 s: fills with E_h (dropped) | 4359 (0) | 2157 (0) | 2202 (0) |
| 60 s: mean markout (ticks) | -0.6155 [-0.6908, -0.5388] negative | -0.7415 [-0.9056, -0.5825] negative | -0.4921 [-0.6208, -0.3729] negative |
| 60 s: median markout | -0.5000 | -0.5000 | -0.5000 |
| 60 s: mean c_half on these fills | 0.0752 [0.0392, 0.1085] positive | 0.0403 [-0.0053, 0.0844] not distinguishable from 0 | 0.1094 [0.0661, 0.1509] positive |
| 60 s: mean E_h | -0.5403 [-0.6210, -0.4588] negative | -0.7012 [-0.8677, -0.5341] negative | -0.3826 [-0.5195, -0.2567] negative |
| 60 s: median E_h | -0.5000 | -0.5000 | -0.5000 |
| 60 s: share E_h > 0 | 0.4006 [0.3888, 0.4120] | 0.3802 [0.3576, 0.4018] | 0.4205 [0.3986, 0.4431] |
| 60 s: mean N_h(Topstep) | -0.8043 [-0.8850, -0.7228] negative | -0.9652 [-1.1317, -0.7981] negative | -0.6466 [-0.7835, -0.5207] negative |
| 60 s: median N_h(Topstep) | -0.7640 | -0.7640 | -0.7640 |
| 60 s: VPO_h(Topstep) per resting order | -0.4603 [-0.5109, -0.4094] negative | -0.5467 [-0.6469, -0.4469] negative | -0.3739 [-0.4578, -0.2982] negative |
| 60 s no-drop: fills with E_h (dropped) | 4359 (0) | 2157 (0) | 2202 (0) |
| 60 s no-drop: mean E_h | -0.5403 [-0.6210, -0.4588] negative | -0.7012 [-0.8677, -0.5341] negative | -0.3826 [-0.5195, -0.2567] negative |
| 60 s no-drop: mean N_h(Topstep) | -0.8043 [-0.8850, -0.7228] negative | -0.9652 [-1.1317, -0.7981] negative | -0.6466 [-0.7835, -0.5207] negative |
| 60 s no-drop: VPO_h(Topstep) | -0.4603 [-0.5109, -0.4094] negative | -0.5467 [-0.6469, -0.4469] negative | -0.3739 [-0.4578, -0.2982] negative |

### (a) K from 2023-11-01, ZM.v.1, OVERNIGHT

| statistic | pooled | buy | sell |
|---|---|---|---|
| placements | 20536 | 10268 | 10268 |
| fills (of which in the 50 ms cancel latency) | 2089 (6) | 976 (2) | 1113 (4) |
| fills by trigger | queue 989, through 1100 | queue 444, through 532 | queue 545, through 568 |
| fill rate | 0.1017 [0.0914, 0.1125] | 0.0951 [0.0840, 0.1060] | 0.1084 [0.0968, 0.1205] |
| touch rate | 0.2633 [0.2438, 0.2822] | 0.2556 [0.2345, 0.2752] | 0.2710 [0.2507, 0.2910] |
| stale share (best price at g differs from j) | 0.0144 [0.0118, 0.0172] | 0.0170 [0.0131, 0.0216] | 0.0117 [0.0093, 0.0140] |
| KM P(fill by 1 s) | 0.0015 [0.0009, 0.0021] | 0.0019 [0.0010, 0.0030] | 0.0010 [0.0004, 0.0017] |
| KM P(fill by 10 s) | 0.0188 [0.0161, 0.0216] | 0.0188 [0.0156, 0.0219] | 0.0188 [0.0156, 0.0224] |
| KM P(fill by 60 s) | 0.1014 [0.0912, 0.1122] | 0.0949 [0.0838, 0.1057] | 0.1080 [0.0965, 0.1199] |
| KM median time to fill (s) | not reached | not reached | not reached |
| KM censored before 60 s | 0 | 0 | 0 |
| mean c_half, all fills (ticks) | 0.0005 [-0.0536, 0.0543] not distinguishable from 0 | -0.0784 [-0.1549, -0.0036] negative | 0.0696 [0.0102, 0.1300] positive |
| median c_half, all fills | 0.5000 | 0.0000 | 0.5000 |
| 1 s: fills with E_h (dropped) | 2089 (0) | 976 (0) | 1113 (0) |
| 1 s: mean markout (ticks) | -0.6060 [-0.6522, -0.5579] negative | -0.5707 [-0.6545, -0.4929] negative | -0.6370 [-0.6888, -0.5828] negative |
| 1 s: median markout | -0.5000 | -0.5000 | -0.5000 |
| 1 s: mean c_half on these fills | 0.0005 [-0.0536, 0.0543] not distinguishable from 0 | -0.0784 [-0.1549, -0.0036] negative | 0.0696 [0.0102, 0.1300] positive |
| 1 s: mean E_h | -0.6056 [-0.6686, -0.5379] negative | -0.6491 [-0.7419, -0.5601] negative | -0.5674 [-0.6392, -0.4857] negative |
| 1 s: median E_h | -0.5000 | -0.5000 | -0.5000 |
| 1 s: share E_h > 0 | 0.1853 [0.1636, 0.2073] | 0.1895 [0.1576, 0.2202] | 0.1815 [0.1554, 0.2088] |
| 1 s: mean N_h(Topstep) | -0.8696 [-0.9326, -0.8019] negative | -0.9131 [-1.0059, -0.8241] negative | -0.8314 [-0.9032, -0.7497] negative |
| 1 s: median N_h(Topstep) | -0.7640 | -0.7640 | -0.7640 |
| 1 s: VPO_h(Topstep) per resting order | -0.0885 [-0.1004, -0.0763] negative | -0.0868 [-0.0993, -0.0743] negative | -0.0901 [-0.1052, -0.0752] negative |
| 1 s no-drop: fills with E_h (dropped) | 2089 (0) | 976 (0) | 1113 (0) |
| 1 s no-drop: mean E_h | -0.6056 [-0.6686, -0.5379] negative | -0.6491 [-0.7419, -0.5601] negative | -0.5674 [-0.6392, -0.4857] negative |
| 1 s no-drop: mean N_h(Topstep) | -0.8696 [-0.9326, -0.8019] negative | -0.9131 [-1.0059, -0.8241] negative | -0.8314 [-0.9032, -0.7497] negative |
| 1 s no-drop: VPO_h(Topstep) | -0.0885 [-0.1004, -0.0763] negative | -0.0868 [-0.0993, -0.0743] negative | -0.0901 [-0.1052, -0.0752] negative |
| 10 s: fills with E_h (dropped) | 2089 (0) | 976 (0) | 1113 (0) |
| 10 s: mean markout (ticks) | -0.6338 [-0.6876, -0.5838] negative | -0.5753 [-0.6716, -0.4895] negative | -0.6851 [-0.7568, -0.6149] negative |
| 10 s: median markout | -0.5000 | -0.5000 | -0.5000 |
| 10 s: mean c_half on these fills | 0.0005 [-0.0536, 0.0543] not distinguishable from 0 | -0.0784 [-0.1549, -0.0036] negative | 0.0696 [0.0102, 0.1300] positive |
| 10 s: mean E_h | -0.6333 [-0.7035, -0.5587] negative | -0.6537 [-0.7528, -0.5581] negative | -0.6155 [-0.7093, -0.5135] negative |
| 10 s: median E_h | -0.5000 | -0.5000 | -0.5000 |
| 10 s: share E_h > 0 | 0.2092 [0.1883, 0.2284] | 0.2111 [0.1792, 0.2402] | 0.2075 [0.1833, 0.2339] |
| 10 s: mean N_h(Topstep) | -0.8973 [-0.9675, -0.8227] negative | -0.9177 [-1.0168, -0.8221] negative | -0.8795 [-0.9733, -0.7775] negative |
| 10 s: median N_h(Topstep) | -0.7640 | -0.7640 | -0.7640 |
| 10 s: VPO_h(Topstep) per resting order | -0.0913 [-0.1041, -0.0789] negative | -0.0872 [-0.1003, -0.0747] negative | -0.0953 [-0.1127, -0.0785] negative |
| 10 s no-drop: fills with E_h (dropped) | 2089 (0) | 976 (0) | 1113 (0) |
| 10 s no-drop: mean E_h | -0.6333 [-0.7035, -0.5587] negative | -0.6537 [-0.7528, -0.5581] negative | -0.6155 [-0.7093, -0.5135] negative |
| 10 s no-drop: mean N_h(Topstep) | -0.8973 [-0.9675, -0.8227] negative | -0.9177 [-1.0168, -0.8221] negative | -0.8795 [-0.9733, -0.7775] negative |
| 10 s no-drop: VPO_h(Topstep) | -0.0913 [-0.1041, -0.0789] negative | -0.0872 [-0.1003, -0.0747] negative | -0.0953 [-0.1127, -0.0785] negative |
| 60 s: fills with E_h (dropped) | 2089 (0) | 976 (0) | 1113 (0) |
| 60 s: mean markout (ticks) | -0.6321 [-0.7149, -0.5534] negative | -0.6230 [-0.7526, -0.5092] negative | -0.6402 [-0.7603, -0.5114] negative |
| 60 s: median markout | -0.5000 | -0.5000 | -0.5000 |
| 60 s: mean c_half on these fills | 0.0005 [-0.0536, 0.0543] not distinguishable from 0 | -0.0784 [-0.1549, -0.0036] negative | 0.0696 [0.0102, 0.1300] positive |
| 60 s: mean E_h | -0.6316 [-0.7207, -0.5405] negative | -0.7013 [-0.8342, -0.5789] negative | -0.5705 [-0.7066, -0.4187] negative |
| 60 s: median E_h | -0.5000 | -0.5000 | -0.5000 |
| 60 s: share E_h > 0 | 0.2944 [0.2697, 0.3187] | 0.2828 [0.2490, 0.3157] | 0.3046 [0.2740, 0.3353] |
| 60 s: mean N_h(Topstep) | -0.8956 [-0.9847, -0.8045] negative | -0.9653 [-1.0982, -0.8429] negative | -0.8345 [-0.9706, -0.6827] negative |
| 60 s: median N_h(Topstep) | -0.7640 | -0.7640 | -0.7640 |
| 60 s: VPO_h(Topstep) per resting order | -0.0911 [-0.1043, -0.0782] negative | -0.0918 [-0.1068, -0.0777] negative | -0.0905 [-0.1106, -0.0713] negative |
| 60 s no-drop: fills with E_h (dropped) | 2089 (0) | 976 (0) | 1113 (0) |
| 60 s no-drop: mean E_h | -0.6316 [-0.7207, -0.5405] negative | -0.7013 [-0.8342, -0.5789] negative | -0.5705 [-0.7066, -0.4187] negative |
| 60 s no-drop: mean N_h(Topstep) | -0.8956 [-0.9847, -0.8045] negative | -0.9653 [-1.0982, -0.8429] negative | -0.8345 [-0.9706, -0.6827] negative |
| 60 s no-drop: VPO_h(Topstep) | -0.0911 [-0.1043, -0.0782] negative | -0.0918 [-0.1068, -0.0777] negative | -0.0905 [-0.1106, -0.0713] negative |

Loop (ZM.v.0, DAY, model (a)) from 2023-11-01: 73 dates, mean 219.507 [211.421, 227.724] round trips per date, median 213.0.

## Splits (spec 5; reported for every model, they decide nothing)

ZS / ZL moves: sign of s x d, d = mid(t_f) - mid(t_f - L) in that contract's ticks; joint: both against, both with, other, missing if either mid is missing. USDA: signed minutes from the nearest release on the trade date (no release: other). These are fill-time conditions, so only statistics among fills are shown. Queue imbalance s x I at j is an entry-time quantity, so its buckets also show placements and fill rate. Headline (dropping) markouts; sides pooled. JSON: every firm and horizon.

### Splits: (a) K, ZM.v.0, DAY

| family | bucket | placements (fill rate) | fills | mean E_1 | mean E_10 | mean E_60 | median E_10 | share E_10 > 0 | mean N_10(Topstep) |
|---|---|---|---|---|---|---|---|---|---|
| ZS L=1 s | against | - | 26131 | -0.3768 | -0.3889 [-0.4140, -0.3641] negative | -0.4043 | -0.5000 | 0.3513 [0.3453, 0.3574] | -0.6529 [-0.6780, -0.6281] negative |
| ZS L=1 s | flat | - | 29925 | -0.2134 | -0.2348 [-0.2531, -0.2164] negative | -0.2312 | 0.0000 | 0.3839 [0.3778, 0.3903] | -0.4988 [-0.5171, -0.4804] negative |
| ZS L=1 s | with | - | 4160 | -0.0476 | -0.0254 [-0.0837, 0.0355] not distinguishable from 0 | 0.0049 | 0.0000 | 0.4334 [0.4188, 0.4489] | -0.2894 [-0.3477, -0.2285] negative |
| ZS L=1 s | missing | - | 0 | n/a | n/a | n/a | n/a | n/a | n/a |
| ZL L=1 s | against | - | 18630 | -0.3230 | -0.3448 [-0.3768, -0.3120] negative | -0.3670 | -0.5000 | 0.3697 [0.3630, 0.3768] | -0.6088 [-0.6408, -0.5760] negative |
| ZL L=1 s | flat | - | 30088 | -0.2491 | -0.2696 [-0.2890, -0.2504] negative | -0.2693 | 0.0000 | 0.3729 [0.3665, 0.3793] | -0.5336 [-0.5530, -0.5144] negative |
| ZL L=1 s | with | - | 11498 | -0.2535 | -0.2401 [-0.2768, -0.2051] negative | -0.2196 | 0.0000 | 0.3795 [0.3701, 0.3887] | -0.5041 [-0.5408, -0.4691] negative |
| ZL L=1 s | missing | - | 0 | n/a | n/a | n/a | n/a | n/a | n/a |
| ZS L=10 s | against | - | 33208 | -0.3610 | -0.3791 [-0.4015, -0.3576] negative | -0.3826 | -0.5000 | 0.3554 [0.3500, 0.3613] | -0.6431 [-0.6655, -0.6216] negative |
| ZS L=10 s | flat | - | 15979 | -0.1944 | -0.2058 [-0.2289, -0.1836] negative | -0.1998 | 0.0000 | 0.3830 [0.3749, 0.3910] | -0.4698 [-0.4929, -0.4476] negative |
| ZS L=10 s | with | - | 11029 | -0.1209 | -0.1285 [-0.1616, -0.0962] negative | -0.1421 | 0.0000 | 0.4125 [0.4028, 0.4218] | -0.3925 [-0.4256, -0.3602] negative |
| ZS L=10 s | missing | - | 0 | n/a | n/a | n/a | n/a | n/a | n/a |
| ZL L=10 s | against | - | 26984 | -0.3025 | -0.3243 [-0.3490, -0.2998] negative | -0.3205 | -0.5000 | 0.3711 [0.3646, 0.3777] | -0.5883 [-0.6130, -0.5638] negative |
| ZL L=10 s | flat | - | 10439 | -0.2244 | -0.2216 [-0.2485, -0.1949] negative | -0.2536 | 0.0000 | 0.3832 [0.3730, 0.3933] | -0.4856 [-0.5125, -0.4589] negative |
| ZL L=10 s | with | - | 22793 | -0.2598 | -0.2734 [-0.2974, -0.2507] negative | -0.2707 | 0.0000 | 0.3711 [0.3641, 0.3774] | -0.5374 [-0.5614, -0.5147] negative |
| ZL L=10 s | missing | - | 0 | n/a | n/a | n/a | n/a | n/a | n/a |
| ZS+ZL L=1 s | both against | - | 13961 | -0.3756 | -0.3935 [-0.4319, -0.3534] negative | -0.4226 | -0.5000 | 0.3558 [0.3474, 0.3640] | -0.6575 [-0.6959, -0.6174] negative |
| ZS+ZL L=1 s | both with | - | 2643 | -0.0706 | -0.0535 [-0.1209, 0.0135] not distinguishable from 0 | -0.0257 | 0.0000 | 0.4272 [0.4082, 0.4453] | -0.3175 [-0.3849, -0.2505] negative |
| ZS+ZL L=1 s | other | - | 43612 | -0.2522 | -0.2674 [-0.2843, -0.2504] negative | -0.2636 | 0.0000 | 0.3755 [0.3702, 0.3810] | -0.5314 [-0.5483, -0.5144] negative |
| ZS+ZL L=1 s | missing | - | 0 | n/a | n/a | n/a | n/a | n/a | n/a |
| ZS+ZL L=10 s | both against | - | 21138 | -0.3531 | -0.3729 [-0.4020, -0.3442] negative | -0.3682 | -0.5000 | 0.3598 [0.3528, 0.3668] | -0.6369 [-0.6660, -0.6082] negative |
| ZS+ZL L=10 s | both with | - | 8269 | -0.1369 | -0.1459 [-0.1841, -0.1091] negative | -0.1391 | 0.0000 | 0.4057 [0.3952, 0.4159] | -0.4099 [-0.4481, -0.3731] negative |
| ZS+ZL L=10 s | other | - | 30809 | -0.2542 | -0.2664 [-0.2857, -0.2478] negative | -0.2769 | 0.0000 | 0.3736 [0.3677, 0.3795] | -0.5304 [-0.5497, -0.5118] negative |
| ZS+ZL L=10 s | missing | - | 0 | n/a | n/a | n/a | n/a | n/a | n/a |
| USDA release | pre (-30, 0) | - | 388 | -0.3376 | -0.3312 [-0.5000, -0.1708] negative | -0.2951 | -0.5000 | 0.3711 [0.3223, 0.4220] | -0.5952 [-0.7640, -0.4348] negative |
| USDA release | post [0, 5) | - | 71 | -6.9296 | -7.9930 [-13.7118, -3.5000] negative | -8.4507 | -7.5000 | 0.3944 [0.2931, 0.4853] | -8.2570 [-13.9758, -3.7640] negative |
| USDA release | post [5, 30) | - | 370 | -0.4284 | -0.4662 [-0.7212, -0.2174] negative | -0.5527 | -0.5000 | 0.4108 [0.3747, 0.4483] | -0.7302 [-0.9852, -0.4814] negative |
| USDA release | other | - | 59387 | -0.2635 | -0.2766 [-0.2911, -0.2638] negative | -0.2786 | 0.0000 | 0.3729 [0.3684, 0.3777] | -0.5406 [-0.5551, -0.5278] negative |
| queue imbalance | (-1, -0.6] | 8211 (0.8219 [0.8129, 0.8312]) | 6749 | -0.2511 | -0.2641 [-0.3061, -0.2242] negative | -0.3088 | -0.5000 | 0.3734 [0.3607, 0.3861] | -0.5281 [-0.5701, -0.4882] negative |
| queue imbalance | (-0.6, -0.2] | 20260 (0.7498 [0.7429, 0.7563]) | 15190 | -0.2741 | -0.2937 [-0.3256, -0.2619] negative | -0.3206 | 0.0000 | 0.3732 [0.3652, 0.3815] | -0.5577 [-0.5896, -0.5259] negative |
| queue imbalance | (-0.2, 0.2) | 28626 (0.6731 [0.6670, 0.6788]) | 19267 | -0.2763 | -0.3030 [-0.3268, -0.2794] negative | -0.2898 | 0.0000 | 0.3695 [0.3626, 0.3771] | -0.5670 [-0.5908, -0.5434] negative |
| queue imbalance | [0.2, 0.6) | 20260 (0.6709 [0.6636, 0.6782]) | 13592 | -0.2895 | -0.2803 [-0.3173, -0.2431] negative | -0.2863 | -0.5000 | 0.3726 [0.3639, 0.3817] | -0.5443 [-0.5813, -0.5071] negative |
| queue imbalance | [0.6, 1) | 8211 (0.6598 [0.6472, 0.6714]) | 5418 | -0.2421 | -0.2592 [-0.3035, -0.2120] negative | -0.1911 | 0.0000 | 0.3872 [0.3737, 0.4012] | -0.5232 [-0.5675, -0.4760] negative |
| queue imbalance | outside (-1, 1) | 0 (n/a) | 0 | n/a | n/a | n/a | n/a | n/a | n/a |
| queue imbalance | missing | 0 (n/a) | 0 | n/a | n/a | n/a | n/a | n/a | n/a |

### Splits: (a) K, ZM.v.0, OVERNIGHT

| family | bucket | placements (fill rate) | fills | mean E_1 | mean E_10 | mean E_60 | median E_10 | share E_10 > 0 | mean N_10(Topstep) |
|---|---|---|---|---|---|---|---|---|---|
| ZS L=1 s | against | - | 19863 | -0.6091 | -0.6412 [-0.6645, -0.6172] negative | -0.6291 | -0.5000 | 0.1772 [0.1713, 0.1837] | -0.9052 [-0.9285, -0.8812] negative |
| ZS L=1 s | flat | - | 24437 | -0.3938 | -0.4113 [-0.4295, -0.3937] negative | -0.4166 | -0.5000 | 0.2379 [0.2318, 0.2441] | -0.6753 [-0.6935, -0.6577] negative |
| ZS L=1 s | with | - | 2483 | -0.2332 | -0.2686 [-0.3234, -0.2154] negative | -0.2823 | 0.0000 | 0.3081 [0.2890, 0.3260] | -0.5326 [-0.5874, -0.4794] negative |
| ZS L=1 s | missing | - | 0 | n/a | n/a | n/a | n/a | n/a | n/a |
| ZL L=1 s | against | - | 12982 | -0.5761 | -0.5987 [-0.6249, -0.5714] negative | -0.5903 | -0.5000 | 0.1925 [0.1848, 0.2007] | -0.8627 [-0.8889, -0.8354] negative |
| ZL L=1 s | flat | - | 29582 | -0.4444 | -0.4665 [-0.4847, -0.4484] negative | -0.4636 | -0.5000 | 0.2218 [0.2162, 0.2274] | -0.7305 [-0.7487, -0.7124] negative |
| ZL L=1 s | with | - | 4219 | -0.3975 | -0.4464 [-0.4877, -0.4072] negative | -0.4736 | -0.5000 | 0.2463 [0.2335, 0.2586] | -0.7104 [-0.7517, -0.6712] negative |
| ZL L=1 s | missing | - | 0 | n/a | n/a | n/a | n/a | n/a | n/a |
| ZS L=10 s | against | - | 26809 | -0.6002 | -0.6289 [-0.6497, -0.6089] negative | -0.6345 | -0.5000 | 0.1785 [0.1729, 0.1841] | -0.8929 [-0.9137, -0.8729] negative |
| ZS L=10 s | flat | - | 14492 | -0.3533 | -0.3680 [-0.3880, -0.3479] negative | -0.3658 | 0.0000 | 0.2452 [0.2373, 0.2521] | -0.6320 [-0.6520, -0.6119] negative |
| ZS L=10 s | with | - | 5482 | -0.1992 | -0.2303 [-0.2640, -0.1961] negative | -0.1939 | 0.0000 | 0.3207 [0.3084, 0.3333] | -0.4943 [-0.5280, -0.4601] negative |
| ZS L=10 s | missing | - | 0 | n/a | n/a | n/a | n/a | n/a | n/a |
| ZL L=10 s | against | - | 20870 | -0.5552 | -0.5808 [-0.6040, -0.5585] negative | -0.5795 | -0.5000 | 0.1945 [0.1879, 0.2010] | -0.8448 [-0.8680, -0.8225] negative |
| ZL L=10 s | flat | - | 15739 | -0.4308 | -0.4545 [-0.4769, -0.4332] negative | -0.4580 | -0.5000 | 0.2194 [0.2118, 0.2263] | -0.7185 [-0.7409, -0.6972] negative |
| ZL L=10 s | with | - | 10174 | -0.3866 | -0.4109 [-0.4373, -0.3852] negative | -0.4004 | -0.5000 | 0.2542 [0.2454, 0.2630] | -0.6749 [-0.7013, -0.6492] negative |
| ZL L=10 s | missing | - | 0 | n/a | n/a | n/a | n/a | n/a | n/a |
| ZS+ZL L=1 s | both against | - | 10788 | -0.6178 | -0.6459 [-0.6745, -0.6155] negative | -0.6430 | -0.5000 | 0.1809 [0.1727, 0.1896] | -0.9099 [-0.9385, -0.8795] negative |
| ZS+ZL L=1 s | both with | - | 1331 | -0.2025 | -0.2457 [-0.3120, -0.1827] negative | -0.2926 | 0.0000 | 0.3080 [0.2839, 0.3323] | -0.5097 [-0.5760, -0.4467] negative |
| ZS+ZL L=1 s | other | - | 34664 | -0.4433 | -0.4662 [-0.4832, -0.4489] negative | -0.4630 | -0.5000 | 0.2232 [0.2180, 0.2285] | -0.7302 [-0.7472, -0.7129] negative |
| ZS+ZL L=1 s | missing | - | 0 | n/a | n/a | n/a | n/a | n/a | n/a |
| ZS+ZL L=10 s | both against | - | 17282 | -0.6115 | -0.6395 [-0.6633, -0.6149] negative | -0.6460 | -0.5000 | 0.1773 [0.1707, 0.1843] | -0.9035 [-0.9273, -0.8789] negative |
| ZS+ZL L=10 s | both with | - | 3490 | -0.2083 | -0.2426 [-0.2845, -0.1985] negative | -0.2182 | 0.0000 | 0.3138 [0.2986, 0.3298] | -0.5066 [-0.5485, -0.4625] negative |
| ZS+ZL L=10 s | other | - | 26011 | -0.4231 | -0.4443 [-0.4625, -0.4269] negative | -0.4402 | -0.5000 | 0.2283 [0.2225, 0.2337] | -0.7083 [-0.7265, -0.6909] negative |
| ZS+ZL L=10 s | missing | - | 0 | n/a | n/a | n/a | n/a | n/a | n/a |
| USDA release | pre (-30, 0) | - | 781 | -0.4142 | -0.4513 [-0.5445, -0.3598] negative | -0.3873 | -0.5000 | 0.2586 [0.2258, 0.2917] | -0.7153 [-0.8085, -0.6238] negative |
| USDA release | post [0, 5) | - | 136 | -0.5846 | -0.8346 [-1.2263, -0.4642] negative | -1.2353 | -0.5000 | 0.2868 [0.2195, 0.3566] | -1.0986 [-1.4903, -0.7282] negative |
| USDA release | post [5, 30) | - | 169 | -0.3817 | -0.3432 [-0.5292, -0.1646] negative | -0.3077 | 0.0000 | 0.3254 [0.2534, 0.3967] | -0.6072 [-0.7932, -0.4286] negative |
| USDA release | other | - | 45697 | -0.4778 | -0.5018 [-0.5190, -0.4846] negative | -0.5001 | -0.5000 | 0.2145 [0.2097, 0.2194] | -0.7658 [-0.7830, -0.7486] negative |
| queue imbalance | (-1, -0.6] | 19613 (0.2829 [0.2727, 0.2919]) | 5549 | -0.4524 | -0.4750 [-0.5044, -0.4435] negative | -0.4653 | -0.5000 | 0.2076 [0.1964, 0.2185] | -0.7390 [-0.7684, -0.7075] negative |
| queue imbalance | (-0.6, -0.2] | 59718 (0.2238 [0.2187, 0.2290]) | 13362 | -0.4942 | -0.5219 [-0.5462, -0.4973] negative | -0.5127 | -0.5000 | 0.2060 [0.1981, 0.2137] | -0.7859 [-0.8102, -0.7613] negative |
| queue imbalance | (-0.2, 0.2) | 72000 (0.1803 [0.1757, 0.1850]) | 12985 | -0.4827 | -0.5078 [-0.5316, -0.4827] negative | -0.5070 | -0.5000 | 0.2163 [0.2088, 0.2241] | -0.7718 [-0.7956, -0.7467] negative |
| queue imbalance | [0.2, 0.6) | 59718 (0.1844 [0.1794, 0.1893]) | 11014 | -0.4792 | -0.5003 [-0.5268, -0.4730] negative | -0.5031 | -0.5000 | 0.2212 [0.2120, 0.2301] | -0.7643 [-0.7908, -0.7370] negative |
| queue imbalance | [0.6, 1) | 19613 (0.1975 [0.1896, 0.2052]) | 3873 | -0.4237 | -0.4498 [-0.4908, -0.4088] negative | -0.4695 | -0.5000 | 0.2450 [0.2304, 0.2591] | -0.7138 [-0.7548, -0.6728] negative |
| queue imbalance | outside (-1, 1) | 0 (n/a) | 0 | n/a | n/a | n/a | n/a | n/a | n/a |
| queue imbalance | missing | 0 (n/a) | 0 | n/a | n/a | n/a | n/a | n/a | n/a |

### Splits: (a) K, ZM.v.1, DAY

| family | bucket | placements (fill rate) | fills | mean E_1 | mean E_10 | mean E_60 | median E_10 | share E_10 > 0 | mean N_10(Topstep) |
|---|---|---|---|---|---|---|---|---|---|
| ZS L=1 s | against | - | 16988 | -0.7607 | -0.7785 [-0.8175, -0.7394] negative | -0.8214 | -0.5000 | 0.2505 [0.2429, 0.2579] | -1.0425 [-1.0815, -1.0034] negative |
| ZS L=1 s | flat | - | 17702 | -0.4848 | -0.4870 [-0.5153, -0.4565] negative | -0.4868 | -0.5000 | 0.2982 [0.2906, 0.3055] | -0.7510 [-0.7793, -0.7205] negative |
| ZS L=1 s | with | - | 2931 | -0.4609 | -0.4666 [-0.5467, -0.3887] negative | -0.4785 | -0.5000 | 0.3228 [0.3044, 0.3417] | -0.7306 [-0.8107, -0.6527] negative |
| ZS L=1 s | missing | - | 0 | n/a | n/a | n/a | n/a | n/a | n/a |
| ZL L=1 s | against | - | 11660 | -0.7017 | -0.7344 [-0.7821, -0.6871] negative | -0.7902 | -0.5000 | 0.2676 [0.2590, 0.2760] | -0.9984 [-1.0461, -0.9511] negative |
| ZL L=1 s | flat | - | 18591 | -0.5541 | -0.5430 [-0.5741, -0.5134] negative | -0.5462 | -0.5000 | 0.2855 [0.2779, 0.2927] | -0.8070 [-0.8381, -0.7774] negative |
| ZL L=1 s | with | - | 7370 | -0.5931 | -0.6183 [-0.6642, -0.5728] negative | -0.6249 | -0.5000 | 0.2786 [0.2678, 0.2891] | -0.8823 [-0.9282, -0.8368] negative |
| ZL L=1 s | missing | - | 0 | n/a | n/a | n/a | n/a | n/a | n/a |
| ZS L=10 s | against | - | 22871 | -0.7693 | -0.7905 [-0.8250, -0.7558] negative | -0.8070 | -0.5000 | 0.2457 [0.2392, 0.2524] | -1.0545 [-1.0890, -1.0198] negative |
| ZS L=10 s | flat | - | 8733 | -0.3971 | -0.3838 [-0.4184, -0.3495] negative | -0.3938 | 0.0000 | 0.3121 [0.3020, 0.3226] | -0.6478 [-0.6824, -0.6135] negative |
| ZS L=10 s | with | - | 6017 | -0.2979 | -0.2962 [-0.3405, -0.2485] negative | -0.3451 | 0.0000 | 0.3548 [0.3424, 0.3679] | -0.5602 [-0.6045, -0.5125] negative |
| ZS L=10 s | missing | - | 0 | n/a | n/a | n/a | n/a | n/a | n/a |
| ZL L=10 s | against | - | 17361 | -0.6766 | -0.6979 [-0.7389, -0.6582] negative | -0.7204 | -0.5000 | 0.2693 [0.2616, 0.2771] | -0.9619 [-1.0029, -0.9222] negative |
| ZL L=10 s | flat | - | 6296 | -0.5278 | -0.5060 [-0.5502, -0.4647] negative | -0.5323 | -0.5000 | 0.2862 [0.2738, 0.2983] | -0.7700 [-0.8142, -0.7287] negative |
| ZL L=10 s | with | - | 13964 | -0.5576 | -0.5667 [-0.6015, -0.5336] negative | -0.5811 | -0.5000 | 0.2867 [0.2782, 0.2949] | -0.8307 [-0.8655, -0.7976] negative |
| ZL L=10 s | missing | - | 0 | n/a | n/a | n/a | n/a | n/a | n/a |
| ZS+ZL L=1 s | both against | - | 8921 | -0.7802 | -0.8184 [-0.8781, -0.7615] negative | -0.8751 | -0.5000 | 0.2569 [0.2475, 0.2668] | -1.0824 [-1.1421, -1.0255] negative |
| ZS+ZL L=1 s | both with | - | 1773 | -0.4411 | -0.4625 [-0.5529, -0.3733] negative | -0.4820 | -0.5000 | 0.3283 [0.3053, 0.3516] | -0.7265 [-0.8169, -0.6373] negative |
| ZS+ZL L=1 s | other | - | 26927 | -0.5613 | -0.5605 [-0.5876, -0.5334] negative | -0.5686 | -0.5000 | 0.2825 [0.2761, 0.2887] | -0.8245 [-0.8516, -0.7974] negative |
| ZS+ZL L=1 s | missing | - | 0 | n/a | n/a | n/a | n/a | n/a | n/a |
| ZS+ZL L=10 s | both against | - | 14340 | -0.7650 | -0.7954 [-0.8393, -0.7506] negative | -0.8055 | -0.5000 | 0.2505 [0.2428, 0.2586] | -1.0594 [-1.1033, -1.0146] negative |
| ZS+ZL L=10 s | both with | - | 4583 | -0.3269 | -0.3389 [-0.3887, -0.2855] negative | -0.3801 | 0.0000 | 0.3441 [0.3298, 0.3588] | -0.6029 [-0.6527, -0.5495] negative |
| ZS+ZL L=10 s | other | - | 18698 | -0.5555 | -0.5485 [-0.5773, -0.5195] negative | -0.5712 | -0.5000 | 0.2840 [0.2765, 0.2913] | -0.8125 [-0.8413, -0.7835] negative |
| ZS+ZL L=10 s | missing | - | 0 | n/a | n/a | n/a | n/a | n/a | n/a |
| USDA release | pre (-30, 0) | - | 271 | -0.7509 | -0.7878 [-1.0023, -0.6023] negative | -0.6199 | -0.5000 | 0.2362 [0.1912, 0.2819] | -1.0518 [-1.2663, -0.8663] negative |
| USDA release | post [0, 5) | - | 56 | -9.1429 | -9.6429 [-15.8644, -4.2839] negative | -14.3125 | -11.2500 | 0.3929 [0.2631, 0.5128] | -9.9069 [-16.1284, -4.5479] negative |
| USDA release | post [5, 30) | - | 294 | -0.8878 | -1.1616 [-1.6108, -0.7556] negative | -0.9932 | -1.0000 | 0.2993 [0.2399, 0.3558] | -1.4256 [-1.8748, -1.0196] negative |
| USDA release | other | - | 37000 | -0.5913 | -0.5978 [-0.6223, -0.5717] negative | -0.6138 | -0.5000 | 0.2785 [0.2728, 0.2842] | -0.8618 [-0.8863, -0.8357] negative |
| queue imbalance | (-1, -0.6] | 6396 (0.5863 [0.5653, 0.6058]) | 3750 | -0.5705 | -0.6001 [-0.6685, -0.5362] negative | -0.5565 | -0.5000 | 0.2667 [0.2518, 0.2815] | -0.8641 [-0.9325, -0.8002] negative |
| queue imbalance | (-0.6, -0.2] | 18968 (0.5232 [0.5117, 0.5347]) | 9925 | -0.6479 | -0.6680 [-0.7117, -0.6251] negative | -0.7215 | -0.5000 | 0.2669 [0.2573, 0.2765] | -0.9320 [-0.9757, -0.8891] negative |
| queue imbalance | (-0.2, 0.2) | 25880 (0.4624 [0.4506, 0.4738]) | 11966 | -0.5931 | -0.5987 [-0.6358, -0.5605] negative | -0.6048 | -0.5000 | 0.2843 [0.2760, 0.2928] | -0.8627 [-0.8998, -0.8245] negative |
| queue imbalance | [0.2, 0.6) | 18968 (0.4687 [0.4570, 0.4796]) | 8891 | -0.6344 | -0.6346 [-0.6825, -0.5858] negative | -0.6381 | -0.5000 | 0.2789 [0.2694, 0.2892] | -0.8986 [-0.9465, -0.8498] negative |
| queue imbalance | [0.6, 1) | 6396 (0.4830 [0.4644, 0.5012]) | 3089 | -0.5013 | -0.4948 [-0.5591, -0.4288] negative | -0.5879 | -0.5000 | 0.3072 [0.2904, 0.3244] | -0.7588 [-0.8231, -0.6928] negative |
| queue imbalance | outside (-1, 1) | 0 (n/a) | 0 | n/a | n/a | n/a | n/a | n/a | n/a |
| queue imbalance | missing | 0 (n/a) | 0 | n/a | n/a | n/a | n/a | n/a | n/a |

### Splits: (a) K, ZM.v.1, OVERNIGHT

| family | bucket | placements (fill rate) | fills | mean E_1 | mean E_10 | mean E_60 | median E_10 | share E_10 > 0 | mean N_10(Topstep) |
|---|---|---|---|---|---|---|---|---|---|
| ZS L=1 s | against | - | 7586 | -0.9323 | -0.9637 [-1.0131, -0.9183] negative | -0.9685 | -1.0000 | 0.1574 [0.1491, 0.1657] | -1.2277 [-1.2771, -1.1823] negative |
| ZS L=1 s | flat | - | 8175 | -0.5752 | -0.6017 [-0.6439, -0.5565] negative | -0.6221 | -0.5000 | 0.2257 [0.2156, 0.2359] | -0.8657 [-0.9079, -0.8205] negative |
| ZS L=1 s | with | - | 1007 | -0.5516 | -0.6415 [-0.7421, -0.5473] negative | -0.5199 | -0.5000 | 0.2582 [0.2313, 0.2857] | -0.9055 [-1.0061, -0.8113] negative |
| ZS L=1 s | missing | - | 0 | n/a | n/a | n/a | n/a | n/a | n/a |
| ZL L=1 s | against | - | 4633 | -0.8677 | -0.9111 [-0.9618, -0.8600] negative | -0.9177 | -1.0000 | 0.1709 [0.1596, 0.1828] | -1.1751 [-1.2258, -1.1240] negative |
| ZL L=1 s | flat | - | 10417 | -0.6759 | -0.7005 [-0.7473, -0.6567] negative | -0.7041 | -0.5000 | 0.2040 [0.1951, 0.2129] | -0.9645 [-1.0113, -0.9207] negative |
| ZL L=1 s | with | - | 1718 | -0.7389 | -0.7905 [-0.8667, -0.7142] negative | -0.7977 | -0.5000 | 0.2224 [0.2034, 0.2426] | -1.0545 [-1.1307, -0.9782] negative |
| ZL L=1 s | missing | - | 0 | n/a | n/a | n/a | n/a | n/a | n/a |
| ZS L=10 s | against | - | 10096 | -0.9010 | -0.9409 [-0.9835, -0.9005] negative | -0.9285 | -1.0000 | 0.1605 [0.1523, 0.1684] | -1.2049 [-1.2475, -1.1645] negative |
| ZS L=10 s | flat | - | 4771 | -0.5036 | -0.5214 [-0.5767, -0.4591] negative | -0.5458 | -0.5000 | 0.2364 [0.2246, 0.2495] | -0.7854 [-0.8407, -0.7231] negative |
| ZS L=10 s | with | - | 1901 | -0.4377 | -0.4679 [-0.5502, -0.3894] negative | -0.5147 | 0.0000 | 0.2898 [0.2690, 0.3108] | -0.7319 [-0.8142, -0.6534] negative |
| ZS L=10 s | missing | - | 0 | n/a | n/a | n/a | n/a | n/a | n/a |
| ZL L=10 s | against | - | 7568 | -0.8349 | -0.8783 [-0.9226, -0.8361] negative | -0.8724 | -1.0000 | 0.1768 [0.1679, 0.1863] | -1.1423 [-1.1866, -1.1001] negative |
| ZL L=10 s | flat | - | 5402 | -0.6557 | -0.6731 [-0.7228, -0.6291] negative | -0.6870 | -0.5000 | 0.2025 [0.1906, 0.2133] | -0.9371 [-0.9868, -0.8931] negative |
| ZL L=10 s | with | - | 3798 | -0.6503 | -0.6827 [-0.7525, -0.6012] negative | -0.6960 | -0.5000 | 0.2283 [0.2141, 0.2424] | -0.9467 [-1.0165, -0.8652] negative |
| ZL L=10 s | missing | - | 0 | n/a | n/a | n/a | n/a | n/a | n/a |
| ZS+ZL L=1 s | both against | - | 3928 | -0.9196 | -0.9622 [-1.0187, -0.9054] negative | -0.9684 | -1.0000 | 0.1601 [0.1484, 0.1722] | -1.2262 [-1.2827, -1.1694] negative |
| ZS+ZL L=1 s | both with | - | 542 | -0.4926 | -0.6061 [-0.7426, -0.4759] negative | -0.5268 | -0.5000 | 0.2712 [0.2344, 0.3094] | -0.8701 [-1.0066, -0.7399] negative |
| ZS+ZL L=1 s | other | - | 12298 | -0.6872 | -0.7130 [-0.7558, -0.6729] negative | -0.7210 | -0.5000 | 0.2052 [0.1970, 0.2132] | -0.9770 [-1.0198, -0.9369] negative |
| ZS+ZL L=1 s | missing | - | 0 | n/a | n/a | n/a | n/a | n/a | n/a |
| ZS+ZL L=10 s | both against | - | 6445 | -0.9004 | -0.9420 [-0.9908, -0.8948] negative | -0.9334 | -1.0000 | 0.1618 [0.1524, 0.1718] | -1.2060 [-1.2548, -1.1588] negative |
| ZS+ZL L=10 s | both with | - | 1267 | -0.4566 | -0.4795 [-0.5668, -0.3941] negative | -0.5442 | 0.0000 | 0.2904 [0.2671, 0.3142] | -0.7435 [-0.8308, -0.6581] negative |
| ZS+ZL L=10 s | other | - | 9056 | -0.6569 | -0.6844 [-0.7302, -0.6408] negative | -0.6903 | -0.5000 | 0.2085 [0.1994, 0.2174] | -0.9484 [-0.9942, -0.9048] negative |
| ZS+ZL L=10 s | missing | - | 0 | n/a | n/a | n/a | n/a | n/a | n/a |
| USDA release | pre (-30, 0) | - | 343 | -0.6910 | -0.7143 [-0.8995, -0.5390] negative | -0.6122 | -0.5000 | 0.2012 [0.1583, 0.2468] | -0.9783 [-1.1635, -0.8030] negative |
| USDA release | post [0, 5) | - | 62 | -1.1774 | -1.4355 [-2.1251, -0.8621] negative | -1.6532 | -1.0000 | 0.2097 [0.1111, 0.3077] | -1.6995 [-2.3891, -1.1261] negative |
| USDA release | post [5, 30) | - | 77 | -0.7532 | -0.6623 [-0.9931, -0.3636] negative | -0.3636 | -0.5000 | 0.2987 [0.1860, 0.4030] | -0.9263 [-1.2571, -0.6276] negative |
| USDA release | other | - | 16286 | -0.7345 | -0.7670 [-0.8061, -0.7301] negative | -0.7747 | -0.5000 | 0.1961 [0.1891, 0.2035] | -1.0310 [-1.0701, -0.9941] negative |
| queue imbalance | (-1, -0.6] | 12920 (0.1073 [0.0978, 0.1165]) | 1386 | -0.6984 | -0.7410 [-0.8376, -0.6589] negative | -0.7551 | -0.5000 | 0.2035 [0.1812, 0.2266] | -1.0050 [-1.1016, -0.9229] negative |
| queue imbalance | (-0.6, -0.2] | 55151 (0.0902 [0.0861, 0.0944]) | 4974 | -0.7909 | -0.8241 [-0.8719, -0.7759] negative | -0.8445 | -0.5000 | 0.1819 [0.1706, 0.1936] | -1.0881 [-1.1359, -1.0399] negative |
| queue imbalance | (-0.2, 0.2) | 70424 (0.0724 [0.0686, 0.0760]) | 5099 | -0.7430 | -0.7729 [-0.8244, -0.7285] negative | -0.8026 | -0.5000 | 0.1869 [0.1751, 0.1979] | -1.0369 [-1.0884, -0.9925] negative |
| queue imbalance | [0.2, 0.6) | 55151 (0.0746 [0.0709, 0.0786]) | 4116 | -0.7281 | -0.7535 [-0.8027, -0.7059] negative | -0.7255 | -0.5000 | 0.2065 [0.1951, 0.2190] | -1.0175 [-1.0667, -0.9699] negative |
| queue imbalance | [0.6, 1) | 12920 (0.0923 [0.0841, 0.1005]) | 1193 | -0.5390 | -0.5930 [-0.7452, -0.3779] negative | -0.5289 | -0.5000 | 0.2590 [0.2346, 0.2845] | -0.8570 [-1.0092, -0.6419] negative |
| queue imbalance | outside (-1, 1) | 0 (n/a) | 0 | n/a | n/a | n/a | n/a | n/a | n/a |
| queue imbalance | missing | 0 (n/a) | 0 | n/a | n/a | n/a | n/a | n/a | n/a |

### Splits: (b) FIFO back of queue, ZM.v.0, DAY

| family | bucket | placements (fill rate) | fills | mean E_1 | mean E_10 | mean E_60 | median E_10 | share E_10 > 0 | mean N_10(Topstep) |
|---|---|---|---|---|---|---|---|---|---|
| ZS L=1 s | against | - | 25758 | -0.3565 | -0.3705 [-0.3942, -0.3452] negative | -0.3801 | -0.5000 | 0.3574 [0.3512, 0.3631] | -0.6345 [-0.6582, -0.6092] negative |
| ZS L=1 s | flat | - | 30500 | -0.1738 | -0.1958 [-0.2137, -0.1791] negative | -0.1961 | 0.0000 | 0.3946 [0.3884, 0.4008] | -0.4598 [-0.4777, -0.4431] negative |
| ZS L=1 s | with | - | 4820 | 0.0013 | 0.0266 [-0.0279, 0.0803] not distinguishable from 0 | 0.0674 | 0.0000 | 0.4471 [0.4319, 0.4614] | -0.2374 [-0.2919, -0.1837] negative |
| ZS L=1 s | missing | - | 0 | n/a | n/a | n/a | n/a | n/a | n/a |
| ZL L=1 s | against | - | 18754 | -0.2934 | -0.3125 [-0.3451, -0.2810] negative | -0.3308 | 0.0000 | 0.3791 [0.3719, 0.3862] | -0.5765 [-0.6091, -0.5450] negative |
| ZL L=1 s | flat | - | 30386 | -0.2107 | -0.2321 [-0.2516, -0.2132] negative | -0.2249 | 0.0000 | 0.3832 [0.3767, 0.3897] | -0.4961 [-0.5156, -0.4772] negative |
| ZL L=1 s | with | - | 11938 | -0.2154 | -0.2073 [-0.2408, -0.1766] negative | -0.2018 | 0.0000 | 0.3889 [0.3799, 0.3980] | -0.4713 [-0.5048, -0.4406] negative |
| ZL L=1 s | missing | - | 0 | n/a | n/a | n/a | n/a | n/a | n/a |
| ZS L=10 s | against | - | 33267 | -0.3307 | -0.3463 [-0.3679, -0.3248] negative | -0.3481 | -0.5000 | 0.3633 [0.3579, 0.3691] | -0.6103 [-0.6319, -0.5888] negative |
| ZS L=10 s | flat | - | 16232 | -0.1587 | -0.1697 [-0.1922, -0.1481] negative | -0.1593 | 0.0000 | 0.3958 [0.3878, 0.4037] | -0.4337 [-0.4562, -0.4121] negative |
| ZS L=10 s | with | - | 11579 | -0.0777 | -0.0961 [-0.1269, -0.0676] negative | -0.1105 | 0.0000 | 0.4218 [0.4122, 0.4307] | -0.3601 [-0.3909, -0.3316] negative |
| ZS L=10 s | missing | - | 0 | n/a | n/a | n/a | n/a | n/a | n/a |
| ZL L=10 s | against | - | 27364 | -0.2674 | -0.2862 [-0.3102, -0.2628] negative | -0.2820 | 0.0000 | 0.3806 [0.3745, 0.3870] | -0.5502 [-0.5742, -0.5268] negative |
| ZL L=10 s | flat | - | 10519 | -0.1882 | -0.1856 [-0.2110, -0.1591] negative | -0.1921 | 0.0000 | 0.3938 [0.3839, 0.4037] | -0.4496 [-0.4750, -0.4231] negative |
| ZL L=10 s | with | - | 23195 | -0.2233 | -0.2416 [-0.2653, -0.2192] negative | -0.2461 | 0.0000 | 0.3811 [0.3743, 0.3874] | -0.5056 [-0.5293, -0.4832] negative |
| ZL L=10 s | missing | - | 0 | n/a | n/a | n/a | n/a | n/a | n/a |
| ZS+ZL L=1 s | both against | - | 13819 | -0.3528 | -0.3752 [-0.4147, -0.3361] negative | -0.4065 | -0.5000 | 0.3629 [0.3544, 0.3709] | -0.6392 [-0.6787, -0.6001] negative |
| ZS+ZL L=1 s | both with | - | 2938 | -0.0265 | -0.0029 [-0.0667, 0.0589] not distinguishable from 0 | 0.0075 | 0.0000 | 0.4432 [0.4249, 0.4614] | -0.2669 [-0.3307, -0.2051] negative |
| ZS+ZL L=1 s | other | - | 44321 | -0.2148 | -0.2300 [-0.2463, -0.2139] negative | -0.2223 | 0.0000 | 0.3853 [0.3801, 0.3908] | -0.4940 [-0.5103, -0.4779] negative |
| ZS+ZL L=1 s | missing | - | 0 | n/a | n/a | n/a | n/a | n/a | n/a |
| ZS+ZL L=10 s | both against | - | 21256 | -0.3214 | -0.3385 [-0.3664, -0.3107] negative | -0.3327 | -0.5000 | 0.3672 [0.3607, 0.3742] | -0.6025 [-0.6304, -0.5747] negative |
| ZS+ZL L=10 s | both with | - | 8669 | -0.0927 | -0.1145 [-0.1499, -0.0814] negative | -0.1222 | 0.0000 | 0.4152 [0.4048, 0.4253] | -0.3785 [-0.4139, -0.3454] negative |
| ZS+ZL L=10 s | other | - | 31153 | -0.2195 | -0.2311 [-0.2493, -0.2120] negative | -0.2348 | 0.0000 | 0.3849 [0.3790, 0.3908] | -0.4951 [-0.5133, -0.4760] negative |
| ZS+ZL L=10 s | missing | - | 0 | n/a | n/a | n/a | n/a | n/a | n/a |
| USDA release | pre (-30, 0) | - | 394 | -0.3020 | -0.3135 [-0.4707, -0.1571] negative | -0.2462 | -0.5000 | 0.3706 [0.3246, 0.4196] | -0.5775 [-0.7347, -0.4211] negative |
| USDA release | post [0, 5) | - | 70 | -6.8143 | -8.9071 [-14.7464, -4.3093] negative | -9.5286 | -9.0000 | 0.3714 [0.2727, 0.4561] | -9.1711 [-15.0104, -4.5733] negative |
| USDA release | post [5, 30) | - | 371 | -0.4501 | -0.4353 [-0.6820, -0.1777] negative | -0.5943 | -0.5000 | 0.4259 [0.3905, 0.4618] | -0.6993 [-0.9460, -0.4417] negative |
| USDA release | other | - | 60243 | -0.2276 | -0.2403 [-0.2531, -0.2278] negative | -0.2401 | 0.0000 | 0.3829 [0.3782, 0.3877] | -0.5043 [-0.5171, -0.4918] negative |
| queue imbalance | (-1, -0.6] | 8211 (0.8419 [0.8328, 0.8509]) | 6913 | -0.1875 | -0.2048 [-0.2457, -0.1652] negative | -0.2483 | 0.0000 | 0.3920 [0.3798, 0.4044] | -0.4688 [-0.5097, -0.4292] negative |
| queue imbalance | (-0.6, -0.2] | 20260 (0.7631 [0.7564, 0.7696]) | 15460 | -0.2216 | -0.2422 [-0.2729, -0.2124] negative | -0.2651 | 0.0000 | 0.3865 [0.3788, 0.3947] | -0.5062 [-0.5369, -0.4764] negative |
| queue imbalance | (-0.2, 0.2) | 28626 (0.6830 [0.6770, 0.6888]) | 19552 | -0.2447 | -0.2688 [-0.2909, -0.2471] negative | -0.2557 | 0.0000 | 0.3790 [0.3722, 0.3864] | -0.5328 [-0.5549, -0.5111] negative |
| queue imbalance | [0.2, 0.6) | 20260 (0.6774 [0.6703, 0.6847]) | 13724 | -0.2667 | -0.2557 [-0.2939, -0.2186] negative | -0.2566 | 0.0000 | 0.3788 [0.3703, 0.3879] | -0.5197 [-0.5579, -0.4826] negative |
| queue imbalance | [0.6, 1) | 8211 (0.6612 [0.6486, 0.6726]) | 5429 | -0.2413 | -0.2696 [-0.3104, -0.2258] negative | -0.2046 | 0.0000 | 0.3870 [0.3735, 0.4009] | -0.5336 [-0.5744, -0.4898] negative |
| queue imbalance | outside (-1, 1) | 0 (n/a) | 0 | n/a | n/a | n/a | n/a | n/a | n/a |
| queue imbalance | missing | 0 (n/a) | 0 | n/a | n/a | n/a | n/a | n/a | n/a |

### Splits: (b) FIFO back of queue, ZM.v.0, OVERNIGHT

| family | bucket | placements (fill rate) | fills | mean E_1 | mean E_10 | mean E_60 | median E_10 | share E_10 > 0 | mean N_10(Topstep) |
|---|---|---|---|---|---|---|---|---|---|
| ZS L=1 s | against | - | 20612 | -0.5634 | -0.5978 [-0.6200, -0.5748] negative | -0.5893 | -0.5000 | 0.1833 [0.1774, 0.1898] | -0.8618 [-0.8840, -0.8388] negative |
| ZS L=1 s | flat | - | 27175 | -0.3120 | -0.3273 [-0.3434, -0.3115] negative | -0.3308 | 0.0000 | 0.2570 [0.2510, 0.2625] | -0.5913 [-0.6074, -0.5755] negative |
| ZS L=1 s | with | - | 3521 | -0.0893 | -0.1214 [-0.1637, -0.0790] negative | -0.1251 | 0.0000 | 0.3357 [0.3205, 0.3518] | -0.3854 [-0.4277, -0.3430] negative |
| ZS L=1 s | missing | - | 0 | n/a | n/a | n/a | n/a | n/a | n/a |
| ZL L=1 s | against | - | 13600 | -0.5203 | -0.5470 [-0.5719, -0.5215] negative | -0.5416 | -0.5000 | 0.2020 [0.1944, 0.2101] | -0.8110 [-0.8359, -0.7855] negative |
| ZL L=1 s | flat | - | 32588 | -0.3660 | -0.3863 [-0.4036, -0.3696] negative | -0.3845 | 0.0000 | 0.2394 [0.2337, 0.2447] | -0.6503 [-0.6676, -0.6336] negative |
| ZL L=1 s | with | - | 5120 | -0.2740 | -0.3151 [-0.3521, -0.2804] negative | -0.3282 | 0.0000 | 0.2730 [0.2609, 0.2854] | -0.5791 [-0.6161, -0.5444] negative |
| ZL L=1 s | missing | - | 0 | n/a | n/a | n/a | n/a | n/a | n/a |
| ZS L=10 s | against | - | 28375 | -0.5393 | -0.5666 [-0.5854, -0.5475] negative | -0.5725 | -0.5000 | 0.1897 [0.1843, 0.1952] | -0.8306 [-0.8494, -0.8115] negative |
| ZS L=10 s | flat | - | 16182 | -0.2762 | -0.2890 [-0.3076, -0.2705] negative | -0.2883 | 0.0000 | 0.2631 [0.2555, 0.2701] | -0.5530 [-0.5716, -0.5345] negative |
| ZS L=10 s | with | - | 6751 | -0.0941 | -0.1315 [-0.1609, -0.1028] negative | -0.0989 | 0.0000 | 0.3414 [0.3307, 0.3526] | -0.3955 [-0.4249, -0.3668] negative |
| ZS L=10 s | missing | - | 0 | n/a | n/a | n/a | n/a | n/a | n/a |
| ZL L=10 s | against | - | 22334 | -0.4843 | -0.5119 [-0.5324, -0.4913] negative | -0.5105 | -0.5000 | 0.2089 [0.2024, 0.2154] | -0.7759 [-0.7964, -0.7553] negative |
| ZL L=10 s | flat | - | 17391 | -0.3535 | -0.3719 [-0.3917, -0.3523] negative | -0.3771 | 0.0000 | 0.2382 [0.2312, 0.2449] | -0.6359 [-0.6557, -0.6163] negative |
| ZL L=10 s | with | - | 11583 | -0.2972 | -0.3231 [-0.3475, -0.2985] negative | -0.3123 | 0.0000 | 0.2709 [0.2624, 0.2795] | -0.5871 [-0.6115, -0.5625] negative |
| ZL L=10 s | missing | - | 0 | n/a | n/a | n/a | n/a | n/a | n/a |
| ZS+ZL L=1 s | both against | - | 11092 | -0.5731 | -0.6053 [-0.6342, -0.5772] negative | -0.6062 | -0.5000 | 0.1882 [0.1799, 0.1970] | -0.8693 [-0.8982, -0.8412] negative |
| ZS+ZL L=1 s | both with | - | 1877 | -0.0605 | -0.1002 [-0.1527, -0.0474] negative | -0.1063 | 0.0000 | 0.3340 [0.3142, 0.3546] | -0.3642 [-0.4167, -0.3114] negative |
| ZS+ZL L=1 s | other | - | 38339 | -0.3635 | -0.3845 [-0.4004, -0.3688] negative | -0.3822 | 0.0000 | 0.2408 [0.2356, 0.2457] | -0.6485 [-0.6644, -0.6328] negative |
| ZS+ZL L=1 s | missing | - | 0 | n/a | n/a | n/a | n/a | n/a | n/a |
| ZS+ZL L=10 s | both against | - | 18216 | -0.5487 | -0.5767 [-0.5992, -0.5538] negative | -0.5823 | -0.5000 | 0.1896 [0.1828, 0.1967] | -0.8407 [-0.8632, -0.8178] negative |
| ZS+ZL L=10 s | both with | - | 4305 | -0.1062 | -0.1502 [-0.1840, -0.1134] negative | -0.1261 | 0.0000 | 0.3296 [0.3156, 0.3433] | -0.4142 [-0.4480, -0.3774] negative |
| ZS+ZL L=10 s | other | - | 28787 | -0.3458 | -0.3645 [-0.3809, -0.3477] negative | -0.3622 | 0.0000 | 0.2457 [0.2400, 0.2512] | -0.6285 [-0.6449, -0.6117] negative |
| ZS+ZL L=10 s | missing | - | 0 | n/a | n/a | n/a | n/a | n/a | n/a |
| USDA release | pre (-30, 0) | - | 834 | -0.3567 | -0.4017 [-0.4899, -0.3164] negative | -0.3819 | -0.5000 | 0.2686 [0.2357, 0.2993] | -0.6657 [-0.7539, -0.5804] negative |
| USDA release | post [0, 5) | - | 140 | -0.5143 | -0.7821 [-1.1633, -0.4244] negative | -1.0929 | -0.5000 | 0.3071 [0.2368, 0.3778] | -1.0461 [-1.4273, -0.6884] negative |
| USDA release | post [5, 30) | - | 178 | -0.3174 | -0.2247 [-0.3970, -0.0513] negative | -0.2051 | 0.0000 | 0.3652 [0.2938, 0.4325] | -0.4887 [-0.6610, -0.3153] negative |
| USDA release | other | - | 50156 | -0.3984 | -0.4218 [-0.4372, -0.4060] negative | -0.4201 | 0.0000 | 0.2315 [0.2268, 0.2362] | -0.6858 [-0.7012, -0.6700] negative |
| queue imbalance | (-1, -0.6] | 19613 (0.3242 [0.3135, 0.3339]) | 6358 | -0.3420 | -0.3662 [-0.3933, -0.3390] negative | -0.3586 | 0.0000 | 0.2323 [0.2216, 0.2429] | -0.6302 [-0.6573, -0.6030] negative |
| queue imbalance | (-0.6, -0.2] | 59718 (0.2529 [0.2476, 0.2585]) | 15105 | -0.3918 | -0.4167 [-0.4390, -0.3946] negative | -0.4072 | 0.0000 | 0.2301 [0.2223, 0.2377] | -0.6807 [-0.7030, -0.6586] negative |
| queue imbalance | (-0.2, 0.2) | 72000 (0.1980 [0.1931, 0.2031]) | 14255 | -0.4031 | -0.4302 [-0.4520, -0.4075] negative | -0.4290 | -0.5000 | 0.2307 [0.2235, 0.2380] | -0.6942 [-0.7160, -0.6715] negative |
| queue imbalance | [0.2, 0.6) | 59718 (0.1962 [0.1911, 0.2012]) | 11718 | -0.4197 | -0.4403 [-0.4656, -0.4143] negative | -0.4474 | -0.5000 | 0.2347 [0.2261, 0.2435] | -0.7043 [-0.7296, -0.6783] negative |
| queue imbalance | [0.6, 1) | 19613 (0.1974 [0.1893, 0.2056]) | 3872 | -0.4260 | -0.4465 [-0.4870, -0.4071] negative | -0.4619 | -0.5000 | 0.2461 [0.2320, 0.2604] | -0.7105 [-0.7510, -0.6711] negative |
| queue imbalance | outside (-1, 1) | 0 (n/a) | 0 | n/a | n/a | n/a | n/a | n/a | n/a |
| queue imbalance | missing | 0 (n/a) | 0 | n/a | n/a | n/a | n/a | n/a | n/a |

### Splits: (b) FIFO back of queue, ZM.v.1, DAY

| family | bucket | placements (fill rate) | fills | mean E_1 | mean E_10 | mean E_60 | median E_10 | share E_10 > 0 | mean N_10(Topstep) |
|---|---|---|---|---|---|---|---|---|---|
| ZS L=1 s | against | - | 17045 | -0.6903 | -0.7052 [-0.7437, -0.6684] negative | -0.7341 | -0.5000 | 0.2641 [0.2568, 0.2715] | -0.9692 [-1.0077, -0.9324] negative |
| ZS L=1 s | flat | - | 18987 | -0.3934 | -0.4030 [-0.4301, -0.3753] negative | -0.4215 | 0.0000 | 0.3180 [0.3106, 0.3251] | -0.6670 [-0.6941, -0.6393] negative |
| ZS L=1 s | with | - | 3571 | -0.3124 | -0.3152 [-0.3842, -0.2489] negative | -0.3353 | 0.0000 | 0.3512 [0.3346, 0.3675] | -0.5792 [-0.6482, -0.5129] negative |
| ZS L=1 s | missing | - | 0 | n/a | n/a | n/a | n/a | n/a | n/a |
| ZL L=1 s | against | - | 12084 | -0.6108 | -0.6385 [-0.6856, -0.5943] negative | -0.6753 | -0.5000 | 0.2854 [0.2770, 0.2933] | -0.9025 [-0.9496, -0.8583] negative |
| ZL L=1 s | flat | - | 19561 | -0.4613 | -0.4532 [-0.4824, -0.4245] negative | -0.4726 | -0.5000 | 0.3057 [0.2987, 0.3125] | -0.7172 [-0.7464, -0.6885] negative |
| ZL L=1 s | with | - | 7958 | -0.4960 | -0.5299 [-0.5725, -0.4856] negative | -0.5413 | -0.5000 | 0.2972 [0.2861, 0.3085] | -0.7939 [-0.8365, -0.7496] negative |
| ZL L=1 s | missing | - | 0 | n/a | n/a | n/a | n/a | n/a | n/a |
| ZS L=10 s | against | - | 23473 | -0.6823 | -0.7046 [-0.7382, -0.6712] negative | -0.7185 | -0.5000 | 0.2623 [0.2556, 0.2688] | -0.9686 [-1.0022, -0.9352] negative |
| ZS L=10 s | flat | - | 9429 | -0.3080 | -0.2941 [-0.3248, -0.2629] negative | -0.3139 | 0.0000 | 0.3338 [0.3240, 0.3439] | -0.5581 [-0.5888, -0.5269] negative |
| ZS L=10 s | with | - | 6701 | -0.2138 | -0.2217 [-0.2639, -0.1775] negative | -0.2820 | 0.0000 | 0.3716 [0.3593, 0.3831] | -0.4857 [-0.5279, -0.4415] negative |
| ZS L=10 s | missing | - | 0 | n/a | n/a | n/a | n/a | n/a | n/a |
| ZL L=10 s | against | - | 18159 | -0.5806 | -0.5966 [-0.6356, -0.5595] negative | -0.6077 | -0.5000 | 0.2905 [0.2830, 0.2984] | -0.8606 [-0.8996, -0.8235] negative |
| ZL L=10 s | flat | - | 6688 | -0.4307 | -0.4201 [-0.4604, -0.3812] negative | -0.4519 | -0.5000 | 0.3076 [0.2960, 0.3188] | -0.6841 [-0.7244, -0.6452] negative |
| ZL L=10 s | with | - | 14756 | -0.4695 | -0.4849 [-0.5188, -0.4526] negative | -0.5189 | -0.5000 | 0.3024 [0.2939, 0.3102] | -0.7489 [-0.7828, -0.7166] negative |
| ZL L=10 s | missing | - | 0 | n/a | n/a | n/a | n/a | n/a | n/a |
| ZS+ZL L=1 s | both against | - | 9035 | -0.7019 | -0.7329 [-0.7911, -0.6789] negative | -0.7618 | -0.5000 | 0.2690 [0.2596, 0.2782] | -0.9969 [-1.0551, -0.9429] negative |
| ZS+ZL L=1 s | both with | - | 2110 | -0.3092 | -0.3521 [-0.4355, -0.2740] negative | -0.3979 | 0.0000 | 0.3445 [0.3239, 0.3651] | -0.6161 [-0.6995, -0.5380] negative |
| ZS+ZL L=1 s | other | - | 28458 | -0.4693 | -0.4720 [-0.4979, -0.4460] negative | -0.4916 | -0.5000 | 0.3035 [0.2972, 0.3099] | -0.7360 [-0.7619, -0.7100] negative |
| ZS+ZL L=1 s | missing | - | 0 | n/a | n/a | n/a | n/a | n/a | n/a |
| ZS+ZL L=10 s | both against | - | 14767 | -0.6713 | -0.6984 [-0.7413, -0.6560] negative | -0.6998 | -0.5000 | 0.2707 [0.2629, 0.2786] | -0.9624 [-1.0053, -0.9200] negative |
| ZS+ZL L=10 s | both with | - | 5058 | -0.2442 | -0.2707 [-0.3181, -0.2218] negative | -0.3322 | 0.0000 | 0.3582 [0.3450, 0.3713] | -0.5347 [-0.5821, -0.4858] negative |
| ZS+ZL L=10 s | other | - | 19778 | -0.4653 | -0.4609 [-0.4898, -0.4335] negative | -0.4904 | -0.5000 | 0.3026 [0.2951, 0.3099] | -0.7249 [-0.7538, -0.6975] negative |
| ZS+ZL L=10 s | missing | - | 0 | n/a | n/a | n/a | n/a | n/a | n/a |
| USDA release | pre (-30, 0) | - | 284 | -0.6708 | -0.7165 [-0.9448, -0.5326] negative | -0.5757 | -0.5000 | 0.2500 [0.2045, 0.2934] | -0.9805 [-1.2088, -0.7966] negative |
| USDA release | post [0, 5) | - | 55 | -9.1182 | -10.0727 [-16.3696, -4.6967] negative | -14.8909 | -11.5000 | 0.3818 [0.2500, 0.5079] | -10.3367 [-16.6336, -4.9607] negative |
| USDA release | post [5, 30) | - | 297 | -0.7946 | -0.9882 [-1.4632, -0.5889] negative | -0.8754 | -1.0000 | 0.3165 [0.2554, 0.3754] | -1.2522 [-1.7272, -0.8529] negative |
| USDA release | other | - | 38967 | -0.4984 | -0.5068 [-0.5297, -0.4821] negative | -0.5253 | -0.5000 | 0.2979 [0.2922, 0.3037] | -0.7708 [-0.7937, -0.7461] negative |
| queue imbalance | (-1, -0.6] | 6396 (0.6268 [0.6057, 0.6468]) | 4009 | -0.4486 | -0.4787 [-0.5451, -0.4208] negative | -0.4300 | -0.5000 | 0.2968 [0.2824, 0.3122] | -0.7427 [-0.8091, -0.6848] negative |
| queue imbalance | (-0.6, -0.2] | 18968 (0.5544 [0.5425, 0.5657]) | 10515 | -0.5317 | -0.5535 [-0.5931, -0.5128] negative | -0.5950 | -0.5000 | 0.2889 [0.2792, 0.2985] | -0.8175 [-0.8571, -0.7768] negative |
| queue imbalance | (-0.2, 0.2) | 25880 (0.4873 [0.4754, 0.4987]) | 12612 | -0.4985 | -0.5067 [-0.5420, -0.4718] negative | -0.5303 | -0.5000 | 0.3038 [0.2953, 0.3123] | -0.7707 [-0.8060, -0.7358] negative |
| queue imbalance | [0.2, 0.6) | 18968 (0.4911 [0.4794, 0.5019]) | 9316 | -0.5569 | -0.5568 [-0.6048, -0.5108] negative | -0.5684 | -0.5000 | 0.2954 [0.2855, 0.3056] | -0.8208 [-0.8688, -0.7748] negative |
| queue imbalance | [0.6, 1) | 6396 (0.4927 [0.4741, 0.5108]) | 3151 | -0.4718 | -0.4699 [-0.5320, -0.4067] negative | -0.5554 | -0.5000 | 0.3120 [0.2950, 0.3284] | -0.7339 [-0.7960, -0.6707] negative |
| queue imbalance | outside (-1, 1) | 0 (n/a) | 0 | n/a | n/a | n/a | n/a | n/a | n/a |
| queue imbalance | missing | 0 (n/a) | 0 | n/a | n/a | n/a | n/a | n/a | n/a |

### Splits: (b) FIFO back of queue, ZM.v.1, OVERNIGHT

| family | bucket | placements (fill rate) | fills | mean E_1 | mean E_10 | mean E_60 | median E_10 | share E_10 > 0 | mean N_10(Topstep) |
|---|---|---|---|---|---|---|---|---|---|
| ZS L=1 s | against | - | 8187 | -0.8310 | -0.8617 [-0.9094, -0.8180] negative | -0.8571 | -0.5000 | 0.1723 [0.1638, 0.1806] | -1.1257 [-1.1734, -1.0820] negative |
| ZS L=1 s | flat | - | 9434 | -0.4510 | -0.4734 [-0.5109, -0.4342] negative | -0.4945 | 0.0000 | 0.2460 [0.2365, 0.2560] | -0.7374 [-0.7749, -0.6982] negative |
| ZS L=1 s | with | - | 1475 | -0.3041 | -0.3522 [-0.4274, -0.2767] negative | -0.3166 | 0.0000 | 0.3037 [0.2790, 0.3279] | -0.6162 [-0.6914, -0.5407] negative |
| ZS L=1 s | missing | - | 0 | n/a | n/a | n/a | n/a | n/a | n/a |
| ZL L=1 s | against | - | 5080 | -0.7634 | -0.8060 [-0.8566, -0.7556] negative | -0.8151 | -0.5000 | 0.1876 [0.1761, 0.1996] | -1.0700 [-1.1206, -1.0196] negative |
| ZL L=1 s | flat | - | 11869 | -0.5470 | -0.5685 [-0.6085, -0.5291] negative | -0.5682 | -0.5000 | 0.2258 [0.2172, 0.2349] | -0.8325 [-0.8725, -0.7931] negative |
| ZL L=1 s | with | - | 2147 | -0.5293 | -0.5582 [-0.6252, -0.4924] negative | -0.5890 | 0.0000 | 0.2548 [0.2359, 0.2737] | -0.8222 [-0.8892, -0.7564] negative |
| ZL L=1 s | missing | - | 0 | n/a | n/a | n/a | n/a | n/a | n/a |
| ZS L=10 s | against | - | 11030 | -0.7905 | -0.8269 [-0.8690, -0.7877] negative | -0.8115 | -0.5000 | 0.1779 [0.1700, 0.1856] | -1.0909 [-1.1330, -1.0517] negative |
| ZS L=10 s | flat | - | 5567 | -0.3804 | -0.3947 [-0.4417, -0.3405] negative | -0.4079 | 0.0000 | 0.2572 [0.2449, 0.2704] | -0.6587 [-0.7057, -0.6045] negative |
| ZS L=10 s | with | - | 2499 | -0.2679 | -0.2891 [-0.3546, -0.2278] negative | -0.3709 | 0.0000 | 0.3145 [0.2952, 0.3344] | -0.5531 [-0.6186, -0.4918] negative |
| ZS L=10 s | missing | - | 0 | n/a | n/a | n/a | n/a | n/a | n/a |
| ZL L=10 s | against | - | 8337 | -0.7212 | -0.7642 [-0.8078, -0.7221] negative | -0.7648 | -0.5000 | 0.1955 [0.1864, 0.2054] | -1.0282 [-1.0718, -0.9861] negative |
| ZL L=10 s | flat | - | 6218 | -0.5211 | -0.5369 [-0.5813, -0.4976] negative | -0.5397 | -0.5000 | 0.2239 [0.2128, 0.2353] | -0.8009 [-0.8453, -0.7616] negative |
| ZL L=10 s | with | - | 4541 | -0.4961 | -0.5134 [-0.5736, -0.4447] negative | -0.5322 | 0.0000 | 0.2550 [0.2411, 0.2688] | -0.7774 [-0.8376, -0.7087] negative |
| ZL L=10 s | missing | - | 0 | n/a | n/a | n/a | n/a | n/a | n/a |
| ZS+ZL L=1 s | both against | - | 4233 | -0.8247 | -0.8674 [-0.9254, -0.8110] negative | -0.8658 | -0.5000 | 0.1760 [0.1642, 0.1880] | -1.1314 [-1.1894, -1.0750] negative |
| ZS+ZL L=1 s | both with | - | 796 | -0.2506 | -0.3059 [-0.4068, -0.2087] negative | -0.2959 | 0.0000 | 0.3141 [0.2808, 0.3481] | -0.5699 [-0.6708, -0.4727] negative |
| ZS+ZL L=1 s | other | - | 14067 | -0.5556 | -0.5777 [-0.6150, -0.5425] negative | -0.5864 | -0.5000 | 0.2264 [0.2184, 0.2346] | -0.8417 [-0.8790, -0.8065] negative |
| ZS+ZL L=1 s | missing | - | 0 | n/a | n/a | n/a | n/a | n/a | n/a |
| ZS+ZL L=10 s | both against | - | 6982 | -0.7959 | -0.8372 [-0.8847, -0.7912] negative | -0.8309 | -0.5000 | 0.1785 [0.1689, 0.1884] | -1.1012 [-1.1487, -1.0552] negative |
| ZS+ZL L=10 s | both with | - | 1650 | -0.2776 | -0.2927 [-0.3669, -0.2205] negative | -0.3818 | 0.0000 | 0.3127 [0.2903, 0.3356] | -0.5567 [-0.6309, -0.4845] negative |
| ZS+ZL L=10 s | other | - | 10464 | -0.5248 | -0.5459 [-0.5853, -0.5075] negative | -0.5464 | -0.5000 | 0.2311 [0.2221, 0.2403] | -0.8099 [-0.8493, -0.7715] negative |
| ZS+ZL L=10 s | missing | - | 0 | n/a | n/a | n/a | n/a | n/a | n/a |
| USDA release | pre (-30, 0) | - | 367 | -0.5981 | -0.6512 [-0.8246, -0.4935] negative | -0.5054 | -0.5000 | 0.2098 [0.1678, 0.2521] | -0.9152 [-1.0886, -0.7575] negative |
| USDA release | post [0, 5) | - | 67 | -1.0896 | -1.2239 [-1.9422, -0.6555] negative | -1.3284 | -0.5000 | 0.2537 [0.1552, 0.3519] | -1.4879 [-2.2062, -0.9195] negative |
| USDA release | post [5, 30) | - | 84 | -0.7262 | -0.5714 [-0.8714, -0.2870] negative | -0.2321 | -0.5000 | 0.3333 [0.2292, 0.4330] | -0.8354 [-1.1354, -0.5510] negative |
| USDA release | other | - | 18578 | -0.6003 | -0.6283 [-0.6642, -0.5940] negative | -0.6381 | -0.5000 | 0.2184 [0.2114, 0.2257] | -0.8923 [-0.9282, -0.8580] negative |
| queue imbalance | (-1, -0.6] | 12920 (0.1294 [0.1186, 0.1405]) | 1672 | -0.5314 | -0.5577 [-0.6411, -0.4839] negative | -0.5700 | -0.5000 | 0.2356 [0.2147, 0.2568] | -0.8217 [-0.9051, -0.7479] negative |
| queue imbalance | (-0.6, -0.2] | 55151 (0.1064 [0.1018, 0.1111]) | 5870 | -0.6176 | -0.6533 [-0.6981, -0.6099] negative | -0.6660 | -0.5000 | 0.2123 [0.2009, 0.2235] | -0.9173 [-0.9621, -0.8739] negative |
| queue imbalance | (-0.2, 0.2) | 70424 (0.0836 [0.0796, 0.0875]) | 5886 | -0.6010 | -0.6205 [-0.6643, -0.5823] negative | -0.6510 | -0.5000 | 0.2134 [0.2013, 0.2244] | -0.8845 [-0.9283, -0.8463] negative |
| queue imbalance | [0.2, 0.6) | 55151 (0.0828 [0.0788, 0.0869]) | 4567 | -0.6213 | -0.6410 [-0.6856, -0.5964] negative | -0.6173 | -0.5000 | 0.2227 [0.2107, 0.2351] | -0.9050 [-0.9496, -0.8604] negative |
| queue imbalance | [0.6, 1) | 12920 (0.0852 [0.0776, 0.0928]) | 1101 | -0.5609 | -0.6303 [-0.7973, -0.3954] negative | -0.5777 | -0.5000 | 0.2425 [0.2177, 0.2684] | -0.8943 [-1.0613, -0.6594] negative |
| queue imbalance | outside (-1, 1) | 0 (n/a) | 0 | n/a | n/a | n/a | n/a | n/a | n/a |
| queue imbalance | missing | 0 (n/a) | 0 | n/a | n/a | n/a | n/a | n/a | n/a |

### Splits: (c) trade-through (gate), ZM.v.0, DAY

| family | bucket | placements (fill rate) | fills | mean E_1 | mean E_10 | mean E_60 | median E_10 | share E_10 > 0 | mean N_10(Topstep) |
|---|---|---|---|---|---|---|---|---|---|
| ZS L=1 s | against | - | 20710 | -1.0832 | -1.1004 [-1.1311, -1.0700] negative | -1.1333 | -1.0000 | 0.1746 [0.1692, 0.1797] | -1.3644 [-1.3951, -1.3340] negative |
| ZS L=1 s | flat | - | 20851 | -0.8540 | -0.8781 [-0.8984, -0.8568] negative | -0.8818 | -0.5000 | 0.1927 [0.1869, 0.1983] | -1.1421 [-1.1624, -1.1208] negative |
| ZS L=1 s | with | - | 2484 | -0.7091 | -0.6520 [-0.7240, -0.5776] negative | -0.5074 | -0.5000 | 0.2548 [0.2381, 0.2716] | -0.9160 [-0.9880, -0.8416] negative |
| ZS L=1 s | missing | - | 0 | n/a | n/a | n/a | n/a | n/a | n/a |
| ZL L=1 s | against | - | 14006 | -1.0231 | -1.0435 [-1.0849, -1.0038] negative | -1.0840 | -1.0000 | 0.1907 [0.1836, 0.1974] | -1.3075 [-1.3489, -1.2678] negative |
| ZL L=1 s | flat | - | 21800 | -0.9135 | -0.9332 [-0.9588, -0.9072] negative | -0.9398 | -0.5000 | 0.1811 [0.1757, 0.1867] | -1.1972 [-1.2228, -1.1712] negative |
| ZL L=1 s | with | - | 8239 | -0.9417 | -0.9417 [-0.9816, -0.9011] negative | -0.9039 | -1.0000 | 0.2001 [0.1913, 0.2096] | -1.2057 [-1.2456, -1.1651] negative |
| ZL L=1 s | missing | - | 0 | n/a | n/a | n/a | n/a | n/a | n/a |
| ZS L=10 s | against | - | 28876 | -1.0233 | -1.0416 [-1.0655, -1.0176] negative | -1.0487 | -1.0000 | 0.1776 [0.1730, 0.1820] | -1.3056 [-1.3295, -1.2816] negative |
| ZS L=10 s | flat | - | 9710 | -0.8376 | -0.8629 [-0.8926, -0.8315] negative | -0.8922 | -0.5000 | 0.1871 [0.1792, 0.1952] | -1.1269 [-1.1566, -1.0955] negative |
| ZS L=10 s | with | - | 5459 | -0.7909 | -0.7811 [-0.8343, -0.7316] negative | -0.7641 | -0.5000 | 0.2424 [0.2303, 0.2542] | -1.0451 [-1.0983, -0.9956] negative |
| ZS L=10 s | missing | - | 0 | n/a | n/a | n/a | n/a | n/a | n/a |
| ZL L=10 s | against | - | 20854 | -0.9887 | -1.0138 [-1.0442, -0.9830] negative | -1.0163 | -1.0000 | 0.1863 [0.1810, 0.1917] | -1.2778 [-1.3082, -1.2470] negative |
| ZL L=10 s | flat | - | 7057 | -0.9055 | -0.8937 [-0.9272, -0.8617] negative | -0.8990 | -0.5000 | 0.1817 [0.1720, 0.1907] | -1.1577 [-1.1912, -1.1257] negative |
| ZL L=10 s | with | - | 16134 | -0.9293 | -0.9465 [-0.9769, -0.9158] negative | -0.9656 | -0.5000 | 0.1921 [0.1859, 0.1982] | -1.2105 [-1.2409, -1.1798] negative |
| ZL L=10 s | missing | - | 0 | n/a | n/a | n/a | n/a | n/a | n/a |
| ZS+ZL L=1 s | both against | - | 11067 | -1.0811 | -1.1036 [-1.1518, -1.0564] negative | -1.1764 | -1.0000 | 0.1799 [0.1724, 0.1870] | -1.3676 [-1.4158, -1.3204] negative |
| ZS+ZL L=1 s | both with | - | 1553 | -0.7595 | -0.7202 [-0.8031, -0.6348] negative | -0.6101 | -0.5000 | 0.2447 [0.2235, 0.2666] | -0.9842 [-1.0671, -0.8988] negative |
| ZS+ZL L=1 s | other | - | 31425 | -0.9183 | -0.9352 [-0.9567, -0.9137] negative | -0.9276 | -0.5000 | 0.1876 [0.1830, 0.1924] | -1.1992 [-1.2207, -1.1777] negative |
| ZS+ZL L=1 s | missing | - | 0 | n/a | n/a | n/a | n/a | n/a | n/a |
| ZS+ZL L=10 s | both against | - | 17946 | -1.0261 | -1.0452 [-1.0772, -1.0130] negative | -1.0419 | -1.0000 | 0.1789 [0.1733, 0.1848] | -1.3092 [-1.3412, -1.2770] negative |
| ZS+ZL L=10 s | both with | - | 4294 | -0.8121 | -0.8009 [-0.8561, -0.7458] negative | -0.7927 | -0.5000 | 0.2345 [0.2213, 0.2469] | -1.0649 [-1.1201, -1.0098] negative |
| ZS+ZL L=10 s | other | - | 21805 | -0.9218 | -0.9412 [-0.9657, -0.9175] negative | -0.9637 | -0.5000 | 0.1857 [0.1806, 0.1908] | -1.2052 [-1.2297, -1.1815] negative |
| ZS+ZL L=10 s | missing | - | 0 | n/a | n/a | n/a | n/a | n/a | n/a |
| USDA release | pre (-30, 0) | - | 293 | -0.9454 | -0.9625 [-1.1514, -0.7846] negative | -0.8242 | -1.0000 | 0.1775 [0.1374, 0.2174] | -1.2265 [-1.4154, -1.0486] negative |
| USDA release | post [0, 5) | - | 68 | -7.8824 | -8.9779 [-15.2470, -4.2997] negative | -11.1176 | -9.0000 | 0.3824 [0.2769, 0.4789] | -9.2419 [-15.5110, -4.5637] negative |
| USDA release | post [5, 30) | - | 330 | -1.1606 | -1.2015 [-1.4984, -0.9169] negative | -1.2061 | -1.0000 | 0.2727 [0.2360, 0.3063] | -1.4655 [-1.7624, -1.1809] negative |
| USDA release | other | - | 43354 | -0.9412 | -0.9556 [-0.9724, -0.9384] negative | -0.9623 | -1.0000 | 0.1868 [0.1830, 0.1907] | -1.2196 [-1.2364, -1.2024] negative |
| queue imbalance | (-1, -0.6] | 8211 (0.6065 [0.5948, 0.6184]) | 4980 | -0.8965 | -0.9317 [-0.9798, -0.8844] negative | -0.9693 | -0.5000 | 0.1821 [0.1710, 0.1942] | -1.1957 [-1.2438, -1.1484] negative |
| queue imbalance | (-0.6, -0.2] | 20260 (0.5556 [0.5473, 0.5634]) | 11257 | -0.9490 | -0.9552 [-0.9946, -0.9175] negative | -0.9972 | -1.0000 | 0.1904 [0.1831, 0.1978] | -1.2192 [-1.2586, -1.1815] negative |
| queue imbalance | (-0.2, 0.2) | 28626 (0.4898 [0.4826, 0.4966]) | 14021 | -0.9707 | -0.9984 [-1.0302, -0.9668] negative | -0.9622 | -1.0000 | 0.1868 [0.1802, 0.1932] | -1.2624 [-1.2942, -1.2308] negative |
| queue imbalance | [0.2, 0.6) | 20260 (0.4921 [0.4837, 0.5001]) | 9969 | -0.9701 | -0.9601 [-1.0053, -0.9159] negative | -0.9925 | -1.0000 | 0.1909 [0.1834, 0.1986] | -1.2241 [-1.2693, -1.1799] negative |
| queue imbalance | [0.6, 1) | 8211 (0.4650 [0.4514, 0.4774]) | 3818 | -0.9358 | -0.9840 [-1.0360, -0.9340] negative | -0.9637 | -1.0000 | 0.1820 [0.1695, 0.1945] | -1.2480 [-1.3000, -1.1980] negative |
| queue imbalance | outside (-1, 1) | 0 (n/a) | 0 | n/a | n/a | n/a | n/a | n/a | n/a |
| queue imbalance | missing | 0 (n/a) | 0 | n/a | n/a | n/a | n/a | n/a | n/a |

### Splits: (c) trade-through (gate), ZM.v.0, OVERNIGHT

| family | bucket | placements (fill rate) | fills | mean E_1 | mean E_10 | mean E_60 | median E_10 | share E_10 > 0 | mean N_10(Topstep) |
|---|---|---|---|---|---|---|---|---|---|
| ZS L=1 s | against | - | 13365 | -1.1330 | -1.1707 [-1.1954, -1.1469] negative | -1.1492 | -1.0000 | 0.0613 [0.0571, 0.0657] | -1.4347 [-1.4594, -1.4109] negative |
| ZS L=1 s | flat | - | 15771 | -0.8477 | -0.8634 [-0.8848, -0.8432] negative | -0.8627 | -1.0000 | 0.0947 [0.0894, 0.1000] | -1.1274 [-1.1488, -1.1072] negative |
| ZS L=1 s | with | - | 1407 | -0.7857 | -0.8348 [-0.9031, -0.7702] negative | -0.8412 | -1.0000 | 0.1251 [0.1077, 0.1423] | -1.0988 [-1.1671, -1.0342] negative |
| ZS L=1 s | missing | - | 0 | n/a | n/a | n/a | n/a | n/a | n/a |
| ZL L=1 s | against | - | 8590 | -1.1120 | -1.1490 [-1.1785, -1.1185] negative | -1.1164 | -1.0000 | 0.0631 [0.0579, 0.0686] | -1.4130 [-1.4425, -1.3825] negative |
| ZL L=1 s | flat | - | 19285 | -0.9102 | -0.9256 [-0.9462, -0.9051] negative | -0.9204 | -1.0000 | 0.0886 [0.0838, 0.0931] | -1.1896 [-1.2102, -1.1691] negative |
| ZL L=1 s | with | - | 2668 | -0.9417 | -1.0184 [-1.0719, -0.9661] negative | -1.0523 | -1.0000 | 0.0892 [0.0782, 0.0998] | -1.2824 [-1.3359, -1.2301] negative |
| ZL L=1 s | missing | - | 0 | n/a | n/a | n/a | n/a | n/a | n/a |
| ZS L=10 s | against | - | 19304 | -1.0662 | -1.0969 [-1.1185, -1.0758] negative | -1.0960 | -1.0000 | 0.0676 [0.0636, 0.0717] | -1.3609 [-1.3825, -1.3398] negative |
| ZS L=10 s | flat | - | 8444 | -0.8225 | -0.8440 [-0.8707, -0.8178] negative | -0.8280 | -0.5000 | 0.0907 [0.0840, 0.0973] | -1.1080 [-1.1347, -1.0818] negative |
| ZS L=10 s | with | - | 2795 | -0.7478 | -0.7635 [-0.8124, -0.7156] negative | -0.7154 | -0.5000 | 0.1492 [0.1356, 0.1635] | -1.0275 [-1.0764, -0.9796] negative |
| ZS L=10 s | missing | - | 0 | n/a | n/a | n/a | n/a | n/a | n/a |
| ZL L=10 s | against | - | 14448 | -1.0417 | -1.0731 [-1.0974, -1.0494] negative | -1.0564 | -1.0000 | 0.0719 [0.0674, 0.0763] | -1.3371 [-1.3614, -1.3134] negative |
| ZL L=10 s | flat | - | 9766 | -0.9023 | -0.9238 [-0.9500, -0.8979] negative | -0.9309 | -1.0000 | 0.0826 [0.0767, 0.0887] | -1.1878 [-1.2140, -1.1619] negative |
| ZL L=10 s | with | - | 6329 | -0.9092 | -0.9340 [-0.9649, -0.9008] negative | -0.9153 | -1.0000 | 0.1014 [0.0933, 0.1102] | -1.1980 [-1.2289, -1.1648] negative |
| ZL L=10 s | missing | - | 0 | n/a | n/a | n/a | n/a | n/a | n/a |
| ZS+ZL L=1 s | both against | - | 7299 | -1.1490 | -1.1911 [-1.2239, -1.1586] negative | -1.1685 | -1.0000 | 0.0593 [0.0537, 0.0653] | -1.4551 [-1.4879, -1.4226] negative |
| ZS+ZL L=1 s | both with | - | 697 | -0.7669 | -0.8300 [-0.9245, -0.7427] negative | -0.8644 | -1.0000 | 0.1220 [0.0976, 0.1464] | -1.0940 [-1.1885, -1.0067] negative |
| ZS+ZL L=1 s | other | - | 22547 | -0.9179 | -0.9387 [-0.9575, -0.9197] negative | -0.9321 | -1.0000 | 0.0874 [0.0829, 0.0918] | -1.2027 [-1.2215, -1.1837] negative |
| ZS+ZL L=1 s | missing | - | 0 | n/a | n/a | n/a | n/a | n/a | n/a |
| ZS+ZL L=10 s | both against | - | 12525 | -1.0794 | -1.1114 [-1.1374, -1.0862] negative | -1.1034 | -1.0000 | 0.0673 [0.0626, 0.0721] | -1.3754 [-1.4014, -1.3502] negative |
| ZS+ZL L=10 s | both with | - | 1790 | -0.7659 | -0.7955 [-0.8560, -0.7311] negative | -0.7221 | -0.5000 | 0.1419 [0.1254, 0.1589] | -1.0595 [-1.1200, -0.9951] negative |
| ZS+ZL L=10 s | other | - | 16228 | -0.9075 | -0.9300 [-0.9506, -0.9081] negative | -0.9265 | -1.0000 | 0.0857 [0.0809, 0.0908] | -1.1940 [-1.2146, -1.1721] negative |
| ZS+ZL L=10 s | missing | - | 0 | n/a | n/a | n/a | n/a | n/a | n/a |
| USDA release | pre (-30, 0) | - | 513 | -0.9386 | -0.9756 [-1.0707, -0.8874] negative | -0.9581 | -1.0000 | 0.1053 [0.0801, 0.1336] | -1.2396 [-1.3347, -1.1514] negative |
| USDA release | post [0, 5) | - | 110 | -1.1091 | -1.4136 [-1.8244, -1.0409] negative | -1.7591 | -1.2500 | 0.1818 [0.1111, 0.2538] | -1.6776 [-2.0884, -1.3049] negative |
| USDA release | post [5, 30) | - | 127 | -0.8898 | -0.7992 [-1.0217, -0.5789] negative | -0.6732 | -0.5000 | 0.1890 [0.1290, 0.2500] | -1.0632 [-1.2857, -0.8429] negative |
| USDA release | other | - | 29793 | -0.9700 | -0.9962 [-1.0146, -0.9789] negative | -0.9860 | -1.0000 | 0.0802 [0.0764, 0.0840] | -1.2602 [-1.2786, -1.2429] negative |
| queue imbalance | (-1, -0.6] | 19613 (0.1856 [0.1776, 0.1931]) | 3640 | -0.9173 | -0.9335 [-0.9704, -0.8955] negative | -0.8990 | -1.0000 | 0.0736 [0.0651, 0.0831] | -1.1975 [-1.2344, -1.1595] negative |
| queue imbalance | (-0.6, -0.2] | 59718 (0.1511 [0.1466, 0.1559]) | 9023 | -0.9531 | -0.9796 [-1.0076, -0.9529] negative | -0.9485 | -1.0000 | 0.0827 [0.0761, 0.0889] | -1.2436 [-1.2716, -1.2169] negative |
| queue imbalance | (-0.2, 0.2) | 72000 (0.1182 [0.1143, 0.1223]) | 8511 | -0.9777 | -1.0130 [-1.0409, -0.9861] negative | -1.0059 | -1.0000 | 0.0795 [0.0737, 0.0853] | -1.2770 [-1.3049, -1.2501] negative |
| queue imbalance | [0.2, 0.6) | 59718 (0.1183 [0.1141, 0.1224]) | 7065 | -0.9948 | -1.0135 [-1.0435, -0.9834] negative | -1.0231 | -1.0000 | 0.0858 [0.0787, 0.0923] | -1.2775 [-1.3075, -1.2474] negative |
| queue imbalance | [0.6, 1) | 19613 (0.1175 [0.1116, 0.1237]) | 2304 | -1.0109 | -1.0495 [-1.1013, -0.9967] negative | -1.0968 | -1.0000 | 0.0829 [0.0720, 0.0941] | -1.3135 [-1.3653, -1.2607] negative |
| queue imbalance | outside (-1, 1) | 0 (n/a) | 0 | n/a | n/a | n/a | n/a | n/a | n/a |
| queue imbalance | missing | 0 (n/a) | 0 | n/a | n/a | n/a | n/a | n/a | n/a |

### Splits: (c) trade-through (gate), ZM.v.1, DAY

| family | bucket | placements (fill rate) | fills | mean E_1 | mean E_10 | mean E_60 | median E_10 | share E_10 > 0 | mean N_10(Topstep) |
|---|---|---|---|---|---|---|---|---|---|
| ZS L=1 s | against | - | 13624 | -1.3072 | -1.3236 [-1.3657, -1.2825] negative | -1.3733 | -1.0000 | 0.1275 [0.1212, 0.1337] | -1.5876 [-1.6297, -1.5465] negative |
| ZS L=1 s | flat | - | 12794 | -1.0542 | -1.0584 [-1.0899, -1.0270] negative | -1.0565 | -1.0000 | 0.1425 [0.1367, 0.1480] | -1.3224 [-1.3539, -1.2910] negative |
| ZS L=1 s | with | - | 2119 | -1.0503 | -1.0750 [-1.1655, -0.9843] negative | -1.0694 | -1.0000 | 0.1671 [0.1499, 0.1841] | -1.3390 [-1.4295, -1.2483] negative |
| ZS L=1 s | missing | - | 0 | n/a | n/a | n/a | n/a | n/a | n/a |
| ZL L=1 s | against | - | 9076 | -1.2583 | -1.2858 [-1.3416, -1.2299] negative | -1.3231 | -1.0000 | 0.1350 [0.1279, 0.1420] | -1.5498 [-1.6056, -1.4939] negative |
| ZL L=1 s | flat | - | 13865 | -1.1225 | -1.1184 [-1.1510, -1.0875] negative | -1.1305 | -1.0000 | 0.1350 [0.1288, 0.1408] | -1.3824 [-1.4150, -1.3515] negative |
| ZL L=1 s | with | - | 5596 | -1.1682 | -1.1931 [-1.2423, -1.1428] negative | -1.2168 | -1.0000 | 0.1460 [0.1364, 0.1553] | -1.4571 [-1.5063, -1.4068] negative |
| ZL L=1 s | missing | - | 0 | n/a | n/a | n/a | n/a | n/a | n/a |
| ZS L=10 s | against | - | 19595 | -1.2670 | -1.2858 [-1.3202, -1.2513] negative | -1.3120 | -1.0000 | 0.1275 [0.1225, 0.1325] | -1.5498 [-1.5842, -1.5153] negative |
| ZS L=10 s | flat | - | 5520 | -0.9896 | -0.9779 [-1.0163, -0.9426] negative | -0.9918 | -1.0000 | 0.1391 [0.1302, 0.1480] | -1.2419 [-1.2803, -1.2066] negative |
| ZS L=10 s | with | - | 3422 | -0.9446 | -0.9524 [-1.0152, -0.8913] negative | -0.9667 | -1.0000 | 0.1891 [0.1762, 0.2030] | -1.2164 [-1.2792, -1.1553] negative |
| ZS L=10 s | missing | - | 0 | n/a | n/a | n/a | n/a | n/a | n/a |
| ZL L=10 s | against | - | 13695 | -1.2241 | -1.2529 [-1.2949, -1.2061] negative | -1.2691 | -1.0000 | 0.1338 [0.1279, 0.1401] | -1.5169 [-1.5589, -1.4701] negative |
| ZL L=10 s | flat | - | 4538 | -1.0963 | -1.0772 [-1.1249, -1.0328] negative | -1.0973 | -1.0000 | 0.1280 [0.1170, 0.1383] | -1.3412 [-1.3889, -1.2968] negative |
| ZL L=10 s | with | - | 10304 | -1.1436 | -1.1457 [-1.1853, -1.1073] negative | -1.1774 | -1.0000 | 0.1456 [0.1388, 0.1527] | -1.4097 [-1.4493, -1.3713] negative |
| ZL L=10 s | missing | - | 0 | n/a | n/a | n/a | n/a | n/a | n/a |
| ZS+ZL L=1 s | both against | - | 7159 | -1.3160 | -1.3556 [-1.4219, -1.2900] negative | -1.3935 | -1.0000 | 0.1300 [0.1219, 0.1379] | -1.6196 [-1.6859, -1.5540] negative |
| ZS+ZL L=1 s | both with | - | 1205 | -1.0083 | -1.0419 [-1.1485, -0.9325] negative | -1.1228 | -1.0000 | 0.1718 [0.1493, 0.1951] | -1.3059 [-1.4125, -1.1965] negative |
| ZS+ZL L=1 s | other | - | 20173 | -1.1345 | -1.1348 [-1.1629, -1.1075] negative | -1.1482 | -1.0000 | 0.1376 [0.1327, 0.1424] | -1.3988 [-1.4269, -1.3715] negative |
| ZS+ZL L=1 s | missing | - | 0 | n/a | n/a | n/a | n/a | n/a | n/a |
| ZS+ZL L=10 s | both against | - | 12102 | -1.2649 | -1.2961 [-1.3428, -1.2482] negative | -1.3082 | -1.0000 | 0.1311 [0.1246, 0.1379] | -1.5601 [-1.6068, -1.5122] negative |
| ZS+ZL L=10 s | both with | - | 2706 | -0.9605 | -0.9699 [-1.0369, -0.9006] negative | -0.9982 | -1.0000 | 0.1914 [0.1769, 0.2072] | -1.2339 [-1.3009, -1.1646] negative |
| ZS+ZL L=10 s | other | - | 13729 | -1.1374 | -1.1321 [-1.1655, -1.1000] negative | -1.1625 | -1.0000 | 0.1318 [0.1257, 0.1377] | -1.3961 [-1.4295, -1.3640] negative |
| ZS+ZL L=10 s | missing | - | 0 | n/a | n/a | n/a | n/a | n/a | n/a |
| USDA release | pre (-30, 0) | - | 204 | -1.2770 | -1.3309 [-1.6111, -1.0787] negative | -1.0931 | -1.0000 | 0.1078 [0.0629, 0.1523] | -1.5949 [-1.8751, -1.3427] negative |
| USDA release | post [0, 5) | - | 55 | -9.3909 | -10.9182 [-17.2374, -5.3008] negative | -15.4091 | -11.5000 | 0.3455 [0.2128, 0.4746] | -11.1822 [-17.5014, -5.5648] negative |
| USDA release | post [5, 30) | - | 261 | -1.4483 | -1.7280 [-2.1533, -1.3167] negative | -1.4195 | -1.5000 | 0.2031 [0.1512, 0.2521] | -1.9920 [-2.4173, -1.5807] negative |
| USDA release | other | - | 28017 | -1.1553 | -1.1611 [-1.1850, -1.1367] negative | -1.1797 | -1.0000 | 0.1363 [0.1318, 0.1407] | -1.4251 [-1.4490, -1.4007] negative |
| queue imbalance | (-1, -0.6] | 6396 (0.4515 [0.4336, 0.4681]) | 2888 | -1.1066 | -1.1359 [-1.2203, -1.0570] negative | -1.1051 | -1.0000 | 0.1288 [0.1164, 0.1414] | -1.3999 [-1.4843, -1.3210] negative |
| queue imbalance | (-0.6, -0.2] | 18968 (0.4028 [0.3926, 0.4122]) | 7640 | -1.1909 | -1.2134 [-1.2631, -1.1637] negative | -1.2698 | -1.0000 | 0.1352 [0.1275, 0.1426] | -1.4774 [-1.5271, -1.4277] negative |
| queue imbalance | (-0.2, 0.2) | 25880 (0.3500 [0.3404, 0.3592]) | 9058 | -1.1579 | -1.1607 [-1.2028, -1.1198] negative | -1.1567 | -1.0000 | 0.1422 [0.1346, 0.1497] | -1.4247 [-1.4668, -1.3838] negative |
| queue imbalance | [0.2, 0.6) | 18968 (0.3544 [0.3444, 0.3638]) | 6722 | -1.2157 | -1.2211 [-1.2810, -1.1643] negative | -1.2361 | -1.0000 | 0.1373 [0.1288, 0.1464] | -1.4851 [-1.5450, -1.4283] negative |
| queue imbalance | [0.6, 1) | 6396 (0.3485 [0.3331, 0.3635]) | 2229 | -1.1519 | -1.1575 [-1.2367, -1.0809] negative | -1.2620 | -1.0000 | 0.1337 [0.1193, 0.1481] | -1.4215 [-1.5007, -1.3449] negative |
| queue imbalance | outside (-1, 1) | 0 (n/a) | 0 | n/a | n/a | n/a | n/a | n/a | n/a |
| queue imbalance | missing | 0 (n/a) | 0 | n/a | n/a | n/a | n/a | n/a | n/a |

### Splits: (c) trade-through (gate), ZM.v.1, OVERNIGHT

| family | bucket | placements (fill rate) | fills | mean E_1 | mean E_10 | mean E_60 | median E_10 | share E_10 > 0 | mean N_10(Topstep) |
|---|---|---|---|---|---|---|---|---|---|
| ZS L=1 s | against | - | 5719 | -1.3685 | -1.4037 [-1.4572, -1.3543] negative | -1.4129 | -1.0000 | 0.0626 [0.0564, 0.0691] | -1.6677 [-1.7212, -1.6183] negative |
| ZS L=1 s | flat | - | 5602 | -1.0290 | -1.0561 [-1.1013, -1.0133] negative | -1.0787 | -1.0000 | 0.1000 [0.0910, 0.1089] | -1.3201 [-1.3653, -1.2773] negative |
| ZS L=1 s | with | - | 693 | -1.0664 | -1.1472 [-1.2807, -1.0170] negative | -1.0007 | -1.0000 | 0.1183 [0.0932, 0.1437] | -1.4112 [-1.5447, -1.2810] negative |
| ZS L=1 s | missing | - | 0 | n/a | n/a | n/a | n/a | n/a | n/a |
| ZL L=1 s | against | - | 3464 | -1.3176 | -1.3640 [-1.4209, -1.3074] negative | -1.3694 | -1.0000 | 0.0693 [0.0607, 0.0782] | -1.6280 [-1.6849, -1.5714] negative |
| ZL L=1 s | flat | - | 7323 | -1.1252 | -1.1486 [-1.1959, -1.1071] negative | -1.1577 | -1.0000 | 0.0881 [0.0809, 0.0954] | -1.4126 [-1.4599, -1.3711] negative |
| ZL L=1 s | with | - | 1227 | -1.2437 | -1.3060 [-1.3970, -1.2179] negative | -1.3003 | -1.0000 | 0.0937 [0.0785, 0.1095] | -1.5700 [-1.6610, -1.4819] negative |
| ZL L=1 s | missing | - | 0 | n/a | n/a | n/a | n/a | n/a | n/a |
| ZS L=10 s | against | - | 7819 | -1.3058 | -1.3499 [-1.3970, -1.3089] negative | -1.3325 | -1.0000 | 0.0660 [0.0602, 0.0718] | -1.6139 [-1.6610, -1.5729] negative |
| ZS L=10 s | flat | - | 3050 | -0.9805 | -0.9985 [-1.0493, -0.9495] negative | -1.0403 | -1.0000 | 0.1010 [0.0895, 0.1132] | -1.2625 [-1.3133, -1.2135] negative |
| ZS L=10 s | with | - | 1145 | -0.9865 | -0.9948 [-1.1149, -0.8836] negative | -1.0703 | -1.0000 | 0.1537 [0.1330, 0.1770] | -1.2588 [-1.3789, -1.1476] negative |
| ZS L=10 s | missing | - | 0 | n/a | n/a | n/a | n/a | n/a | n/a |
| ZL L=10 s | against | - | 5753 | -1.2561 | -1.3019 [-1.3511, -1.2569] negative | -1.3064 | -1.0000 | 0.0758 [0.0689, 0.0830] | -1.5659 [-1.6151, -1.5209] negative |
| ZL L=10 s | flat | - | 3659 | -1.1055 | -1.1297 [-1.1841, -1.0792] negative | -1.1476 | -1.0000 | 0.0773 [0.0679, 0.0866] | -1.3937 [-1.4481, -1.3432] negative |
| ZL L=10 s | with | - | 2602 | -1.1754 | -1.1973 [-1.2612, -1.1325] negative | -1.1924 | -1.0000 | 0.1080 [0.0955, 0.1200] | -1.4613 [-1.5252, -1.3965] negative |
| ZL L=10 s | missing | - | 0 | n/a | n/a | n/a | n/a | n/a | n/a |
| ZS+ZL L=1 s | both against | - | 2978 | -1.3512 | -1.4014 [-1.4642, -1.3396] negative | -1.4105 | -1.0000 | 0.0645 [0.0558, 0.0731] | -1.6654 [-1.7282, -1.6036] negative |
| ZS+ZL L=1 s | both with | - | 351 | -1.0513 | -1.1581 [-1.3329, -0.9773] negative | -1.0556 | -1.0000 | 0.1168 [0.0850, 0.1530] | -1.4221 [-1.5969, -1.2413] negative |
| ZS+ZL L=1 s | other | - | 8685 | -1.1442 | -1.1697 [-1.2128, -1.1312] negative | -1.1797 | -1.0000 | 0.0883 [0.0815, 0.0948] | -1.4337 [-1.4768, -1.3952] negative |
| ZS+ZL L=1 s | missing | - | 0 | n/a | n/a | n/a | n/a | n/a | n/a |
| ZS+ZL L=10 s | both against | - | 5043 | -1.3023 | -1.3482 [-1.4014, -1.2995] negative | -1.3445 | -1.0000 | 0.0676 [0.0604, 0.0754] | -1.6122 [-1.6654, -1.5635] negative |
| ZS+ZL L=10 s | both with | - | 755 | -1.0159 | -1.0020 [-1.1228, -0.8841] negative | -1.0530 | -1.0000 | 0.1550 [0.1267, 0.1818] | -1.2660 [-1.3868, -1.1481] negative |
| ZS+ZL L=10 s | other | - | 6216 | -1.1254 | -1.1556 [-1.2027, -1.1145] negative | -1.1650 | -1.0000 | 0.0872 [0.0794, 0.0948] | -1.4196 [-1.4667, -1.3785] negative |
| ZS+ZL L=10 s | missing | - | 0 | n/a | n/a | n/a | n/a | n/a | n/a |
| USDA release | pre (-30, 0) | - | 257 | -1.0817 | -1.1323 [-1.3322, -0.9383] negative | -0.9183 | -1.0000 | 0.1012 [0.0681, 0.1371] | -1.3963 [-1.5962, -1.2023] negative |
| USDA release | post [0, 5) | - | 52 | -1.6250 | -1.9327 [-2.7176, -1.2613] negative | -2.3173 | -1.7500 | 0.1538 [0.0612, 0.2500] | -2.1967 [-2.9816, -1.5253] negative |
| USDA release | post [5, 30) | - | 59 | -1.1441 | -1.0085 [-1.3446, -0.6911] negative | -0.7119 | -1.0000 | 0.1864 [0.0952, 0.2807] | -1.2725 [-1.6086, -0.9551] negative |
| USDA release | other | - | 11646 | -1.1935 | -1.2269 [-1.2677, -1.1909] negative | -1.2381 | -1.0000 | 0.0820 [0.0764, 0.0876] | -1.4909 [-1.5317, -1.4549] negative |
| queue imbalance | (-1, -0.6] | 12920 (0.0772 [0.0700, 0.0842]) | 998 | -1.1182 | -1.1809 [-1.2981, -1.0782] negative | -1.1733 | -1.0000 | 0.0892 [0.0711, 0.1070] | -1.4449 [-1.5621, -1.3422] negative |
| queue imbalance | (-0.6, -0.2] | 55151 (0.0679 [0.0646, 0.0713]) | 3743 | -1.1973 | -1.2342 [-1.2861, -1.1824] negative | -1.2513 | -1.0000 | 0.0826 [0.0728, 0.0918] | -1.4982 [-1.5501, -1.4464] negative |
| queue imbalance | (-0.2, 0.2) | 70424 (0.0526 [0.0498, 0.0554]) | 3702 | -1.1796 | -1.2076 [-1.2622, -1.1587] negative | -1.2516 | -1.0000 | 0.0786 [0.0689, 0.0885] | -1.4716 [-1.5262, -1.4227] negative |
| queue imbalance | [0.2, 0.6) | 55151 (0.0522 [0.0492, 0.0552]) | 2881 | -1.2110 | -1.2279 [-1.2818, -1.1726] negative | -1.2017 | -1.0000 | 0.0861 [0.0753, 0.0965] | -1.4919 [-1.5458, -1.4366] negative |
| queue imbalance | [0.6, 1) | 12920 (0.0534 [0.0481, 0.0590]) | 690 | -1.2703 | -1.3522 [-1.4924, -1.2212] negative | -1.2565 | -1.0000 | 0.0913 [0.0692, 0.1145] | -1.6162 [-1.7564, -1.4852] negative |
| queue imbalance | outside (-1, 1) | 0 (n/a) | 0 | n/a | n/a | n/a | n/a | n/a | n/a |
| queue imbalance | missing | 0 (n/a) | 0 | n/a | n/a | n/a | n/a | n/a | n/a |

## Feasible round trips: the loop (spec 6; DAY session)

Completed round trips per DAY trade date; no P&L of the loop is computed.

| symbol | model | dates | round trips | mean per date [CI] | median | min / p10 / p25 / p75 / p90 / max | dates by count | mean RT duration (s) | entries filled / orders placed |
|---|---|---|---|---|---|---|---|---|---|
| ZM.v.0 | (a) K | 764 | 158654 | 207.662 [204.612, 210.449] | 207.0 | 38 / 156.0 / 179.0 / 234.2 / 259.0 / 341 | 0: 0, 1-4: 0, 5-9: 0, 10-19: 0, 20-29: 0, 30-49: 1, 50-99: 2, 100+: 761 | 80.75 | 159042 / 445656 |
| ZM.v.0 | (b) FIFO back of queue | 764 | 164365 | 215.137 [212.001, 218.005] | 213.0 | 36 / 163.0 / 186.0 / 245.0 / 269.7 / 352 | 0: 0, 1-4: 0, 5-9: 0, 10-19: 0, 20-29: 0, 30-49: 1, 50-99: 2, 100+: 761 | 77.94 | 164742 / 456568 |
| ZM.v.0 | (c) trade-through (gate) | 764 | 85238 | 111.568 [109.553, 113.461] | 110.0 | 29 / 75.0 / 93.0 / 129.0 / 148.0 / 221 | 0: 0, 1-4: 0, 5-9: 0, 10-19: 0, 20-29: 1, 30-49: 4, 50-99: 263, 100+: 496 | 150.02 | 85611 / 324883 |

## Implied-liquidity check (spec 8)

Among trades with aggressor A or B: (i) no displayed resting quantity on the passive side at the price just before the trade; (ii) displayed resting quantity below the trade's size (as the engine's n_short / vol_short define it). Side N beside.

| symbol | session | dates | A/B prints / volume | (i) share of prints | (i) share of volume | (ii) share of prints | (ii) share of volume | side N prints / volume | side N share of all prints |
|---|---|---|---|---|---|---|---|---|---|
| ZM.v.0 | DAY | 764 | 7823934 / 19702332 | 0.0552 [0.0536, 0.0569] | 0.0360 [0.0348, 0.0372] | 0.1180 [0.1158, 0.1200] | 0.2600 [0.2565, 0.2631] | 778470 / 1986541 | 0.0905 [0.0888, 0.0922] |
| ZM.v.0 | OVERNIGHT | 764 | 2112834 / 4402235 | 0.0461 [0.0443, 0.0479] | 0.0326 [0.0312, 0.0341] | 0.0959 [0.0937, 0.0982] | 0.2235 [0.2189, 0.2281] | 195134 / 467722 | 0.0845 [0.0824, 0.0867] |
| ZM.v.1 | DAY | 684 | 2491675 / 5534101 | 0.1445 [0.1406, 0.1485] | 0.1053 [0.1019, 0.1088] | 0.2200 [0.2156, 0.2246] | 0.3772 [0.3705, 0.3840] | 720127 / 1543510 | 0.2242 [0.2198, 0.2292] |
| ZM.v.1 | OVERNIGHT | 684 | 625008 / 1269286 | 0.1239 [0.1194, 0.1287] | 0.0904 [0.0866, 0.0944] | 0.1999 [0.1943, 0.2059] | 0.3507 [0.3421, 0.3593] | 175154 / 349947 | 0.2189 [0.2137, 0.2247] |

## Exclusions (days.parquet, spec 2)

| symbol | dates | included | excluded | excluded by reason | records | ts_event inversions | bad-book flag records | crossed/locked/empty moments | max DAY gap (s) | placements DAY / overnight | instruments |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ZM.v.0 | 816 | 764 | 52 | after_roll_day: 20; cme_holiday_or_early_close: 4; roll_day: 23; scheduled_late_open: 5 | 414363576 | 0 | 5417 | 33 | 32.3 (0 dates > 60 s) | 85568 / 230662 | ZMF1, ZMF2, ZMF3, ZMF4, ZMH1, ZMH2, ZMH3, ZMH4, ZMK1, ZMK2, ZMK3, ZMK4, ZMN1, ZMN2, ZMN3, ZMU1, ZMZ1, ZMZ2, ZMZ3 |
| ZM.v.1 | 816 | 684 | 132 | after_roll_day: 55; cme_holiday_or_early_close: 4; roll_day: 68; scheduled_late_open: 5 | 284374052 | 0 | 1732 | 1 | 805.2 (14 dates > 60 s) | 76608 / 206566 | ZMF1, ZMF2, ZMF3, ZMF4, ZMH1, ZMH2, ZMH3, ZMH4, ZMK1, ZMK2, ZMK3, ZMK4, ZMN1, ZMN2, ZMN3, ZMQ1, ZMQ2, ZMQ3, ZMU1, ZMU2, ZMU3, ZMV1, ZMV2, ZMV3, ZMZ0, ZMZ1, ZMZ2, ZMZ3 |

## Consistency checks (each should be 0 or empty)

| check | value |
|---|---|
| placement_rows_on_dates_not_included | 0 |
| placement_rows_on_dates_missing_from_days | 0 |
| loop_rows_on_dates_not_included | 0 |
| included_front_dates_without_loop_row | {'a': 0, 'b': 0, 'c': 0} |
| placement_counts_unequal_across_models | {} |
| model_c_fills_not_through | 0 |
| fills_with_t_fill_before_j | 0 |
| fills_with_nan_c_half | 0 |

