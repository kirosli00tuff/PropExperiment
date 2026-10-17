| Cluster | Statement | Tier A trial | Status | theta_hat | UCB95 | eps_X | Trips | Holm p (K = 5; alpha 0.01) | t | DSR (N 533) | PBO | Chain |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| K5 | no statement | K5-fomc-01 MGC | null | -0.3129 | +0.0930 | +71 | 34 | 0.8938 (not rejected) | -1.253 | 5.43e-12 | +0.043 | no edge (first failing: holm) |
| K8 | null | K8-flight-01 HEOD MGC | null | -0.3075 | +2.2464 | +71 | 231 | 0.5738 (not rejected) | -0.201 | 0.00e+00 | +0.971 | no edge (first failing: holm) |
| K8 | null | K8-wkndbtc-01 MNQ | not run | - | - | - | - | 1.0000 (not rejected) | - | no series | +0.971 | no edge (first failing: holm) |
| K3 | no statement | K3-ldnrev-01 6E | null | -0.1071 | +0.1032 | +12 | 55 | 0.7974 (not rejected) | -0.844 | 3.04e-10 | +0.543 | no edge (first failing: holm) |
| K6 | no statement | K6-limitcont-01 HE | null by inactivity | +0.0495 | +0.3869 | +7 | 10 | 0.4088 (not rejected) | +0.237 | 5.77e-09 | +0.557 | no edge (first failing: holm) |

#### K5 (verdict sha256 51061000f6b0...; statement: no statement)

| Ord | Trial | Tier | Status | Days | Trips | theta_hat | UCB95 | SE_boot | eps_X | Null power | p_upper |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | K5-cp1-01 MGC | B | null | 1174 | 1132 | -3.2051 | -2.1072 | +0.6593 | 71.0 | +1.000 | +1.0000 |
| 2 | K5-cp1-01 MHG | excluded | not run | - | - | - | - | - | - | - | - |
| 3 | K5-cp2-01 MGC | B | null | 1174 | 1166 | -3.8527 | -0.3417 | +2.1091 | 71.0 | +1.000 | +0.9692 |
| 4 | K5-cp2-01 MHG | excluded | not run | - | - | - | - | - | - | - | - |
| 5 | K5-cp3-01 MGC | B | null | 1174 | 489 | -5.1667 | -1.5998 | +2.1632 | 71.0 | +1.000 | +0.9916 |
| 6 | K5-cp3-01 MHG | B | inconclusive | - | - | - | - | - | - | - | - |
| 7 | K5-preauc-01 MGC | B | null | 1174 | 1115 | -4.0368 | -3.0145 | +0.6180 | 71.0 | +1.000 | +1.0000 |
| 8 | K5-pmfix-01 MGC | excluded | not run | - | - | - | - | - | - | - | - |
| 9 | K5-fomc-01 MGC | A | null | 1174 | 34 | -0.3129 | +0.0930 | +0.2505 | 71.0 | +1.000 | +0.8938 |
| 10 | K5-ovr-01 MGC | B | null | 1174 | 1221 | -5.5728 | -2.8922 | +1.6550 | 71.0 | +1.000 | +0.9992 |
| 11 | K5-ovr-01 MHG | B | inconclusive | - | - | - | - | - | - | - | - |

Covered: 8; not covered: K5-cp1-01 MHG (not run: excluded (not Tier A or B)); K5-cp2-01 MHG (not run: excluded (not Tier A or B)); K5-pmfix-01 MGC (not run: excluded (not Tier A or B)); blocking: K5-cp3-01 MHG (inconclusive: record status 'excluded_before_screening': no series); K5-ovr-01 MHG (inconclusive: record status 'excluded_before_screening': no series); null by inactivity: none.
Edge chain: Holm K = 5 (m = 1); descriptive K = 9: K5-fomc-01 MGC p 0.8938 vs 0.00556; DSR variance 0.00269005 over 6 series; PBO +0.0429 over 6 series.

#### K8 (verdict sha256 0a2a820b2210...; statement: null)

| Ord | Trial | Tier | Status | Days | Trips | theta_hat | UCB95 | SE_boot | eps_X | Null power | p_upper |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | K8-flight-01 H30 MGC | B | null | 944 | 231 | -0.2280 | +1.2278 | +0.8700 | 71.0 | +1.000 | +0.5969 |
| 2 | K8-flight-01 HEOD MGC | A | null | 944 | 231 | -0.3075 | +2.2464 | +1.5217 | 71.0 | +1.000 | +0.5738 |
| 3 | K8-oilcad-01 6C | B | null | 569 | 1438 | -4.1124 | -2.6674 | +0.8864 | 9.0 | +1.000 | +1.0000 |
| 4 | K8-wkndbtc-01 MNQ | A | not run | - | - | - | - | - | - | - | - |

Covered: 3; not covered: K8-wkndbtc-01 MNQ (not run: inconclusive by design); blocking: none; null by inactivity: none.
Edge chain: Holm K = 5 (m = 2); descriptive K = 9: K8-flight-01 HEOD MGC p 0.5738 vs 0.00278, K8-wkndbtc-01 MNQ p 1.0000 vs 0.00556; DSR variance 0.00937685 over 3 series; PBO +0.9714 over 3 series.

#### K3 (verdict sha256 9f6e74c8605f...; statement: no statement)

| Ord | Trial | Tier | Status | Days | Trips | theta_hat | UCB95 | SE_boot | eps_X | Null power | p_upper |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | K3-cp1-01 6E | B | null | 1191 | 1134 | -0.4478 | +0.3306 | +0.4680 | 12.0 | +1.000 | +0.8279 |
| 2 | K3-cp1-01 6A | B | null | 1191 | 1100 | -1.6585 | -0.9911 | +0.4024 | 11.0 | +1.000 | +1.0000 |
| 3 | K3-cp1-01 6B | B | null | 1191 | 1107 | -0.3684 | +0.1347 | +0.3064 | 8.0 | +1.000 | +0.8849 |
| 4 | K3-cp1-01 6C | B | null | 1191 | 1131 | -1.3204 | -0.7847 | +0.3239 | 9.0 | +1.000 | +1.0000 |
| 5 | K3-cp1-01 6J | B | null | 1191 | 1118 | -1.2085 | -0.6233 | +0.3462 | 10.0 | +1.000 | +0.9998 |
| 6 | K3-cp1-01 6S | excluded | not run | - | - | - | - | - | - | - | - |
| 7 | K3-cp1-01 6N | excluded | not run | - | - | - | - | - | - | - | - |
| 8 | K3-cp2-01 6E | B | null | 1191 | 1183 | -3.4087 | -1.6286 | +1.0651 | 12.0 | +1.000 | +0.9993 |
| 9 | K3-cp2-01 6A | B | null | 1191 | 1184 | -1.5796 | +0.0108 | +0.9438 | 11.0 | +1.000 | +0.9565 |
| 10 | K3-cp2-01 6B | B | null | 1191 | 1186 | -1.7056 | -0.5354 | +0.7028 | 8.0 | +1.000 | +0.9920 |
| 11 | K3-cp2-01 6C | B | null | 1191 | 1182 | -1.3914 | -0.1754 | +0.7275 | 9.0 | +1.000 | +0.9711 |
| 12 | K3-cp2-01 6J | B | null | 1191 | 1173 | -1.3200 | -0.0282 | +0.7783 | 10.0 | +1.000 | +0.9571 |
| 13 | K3-cp2-01 6S | B | inconclusive | - | - | - | - | - | - | - | - |
| 14 | K3-cp2-01 6N | excluded | not run | - | - | - | - | - | - | - | - |
| 15 | K3-cp3-01 6E | B | null | 1191 | 513 | +0.2227 | +2.2949 | +1.2761 | 12.0 | +1.000 | +0.4292 |
| 16 | K3-cp3-01 6A | B | null | 1191 | 544 | -1.0236 | +1.0324 | +1.2198 | 11.0 | +1.000 | +0.8050 |
| 17 | K3-cp3-01 6B | B | null | 1191 | 548 | +0.2622 | +2.0640 | +1.0557 | 8.0 | +1.000 | +0.3997 |
| 18 | K3-cp3-01 6C | B | null | 1191 | 538 | -2.3067 | -0.6401 | +1.0086 | 9.0 | +1.000 | +0.9892 |
| 19 | K3-cp3-01 6J | B | null | 1191 | 543 | -0.2039 | +1.6850 | +1.1603 | 10.0 | +1.000 | +0.5728 |
| 20 | K3-cp3-01 6S | B | null | 1191 | 497 | -0.5882 | +1.5190 | +1.2898 | 13.0 | +1.000 | +0.6775 |
| 21 | K3-cp3-01 6N | B | inconclusive | - | - | - | - | - | - | - | - |
| 22 | K3-ldnrev-01 6E | A | null | 1191 | 55 | -0.1071 | +0.1032 | +0.1287 | 12.0 | +1.000 | +0.7974 |
| 23 | K3-ldnrev-01 6J | B | null | 1191 | 53 | -0.1314 | +0.0203 | +0.0961 | 10.0 | +1.000 | +0.9069 |
| 24 | K3-ldnrev-01 6S | B | null | 1191 | 55 | -0.0320 | +0.2120 | +0.1483 | 13.0 | +1.000 | +0.5863 |
| 25 | K3-ldnmom-01 6E | B | null | 1191 | 1063 | -1.5901 | -0.7328 | +0.5113 | 12.0 | +1.000 | +0.9986 |
| 26 | K3-ldnmom-01 6J | B | null | 1191 | 1033 | -2.1492 | -1.5410 | +0.3734 | 10.0 | +1.000 | +1.0000 |
| 27 | K3-mehedge-01 6J | B | null | 1191 | 55 | -0.1134 | +0.2476 | +0.2204 | 10.0 | +1.000 | +0.6955 |
| 28 | K3-ecbfix-01 6E | B | null | 1191 | 2301 | -1.2285 | +3.3484 | +2.6948 | 12.0 | +0.998 | +0.6753 |
| 29 | K3-tkypre-01 6J | B | null | 1191 | 224 | +0.7285 | +1.3478 | +0.3684 | 10.0 | +1.000 | +0.0271 |
| 30 | K3-tkypost-01 6J | B | null | 1191 | 1091 | -1.0613 | +0.6714 | +1.0283 | 10.0 | +1.000 | +0.8550 |

Covered: 27; not covered: K3-cp1-01 6S (not run: excluded (not Tier A or B)); K3-cp1-01 6N (not run: excluded (not Tier A or B)); K3-cp2-01 6N (not run: excluded (not Tier A or B)); blocking: K3-cp2-01 6S (inconclusive: record status 'excluded_before_screening': no series); K3-cp3-01 6N (inconclusive: record status 'excluded_before_screening': no series); null by inactivity: none.
Edge chain: Holm K = 5 (m = 1); descriptive K = 9: K3-ldnrev-01 6E p 0.7974 vs 0.00556; DSR variance 0.00241732 over 25 series; PBO +0.5429 over 25 series.

#### K6 (verdict sha256 265d9ec018f2...; statement: no statement)

| Ord | Trial | Tier | Status | Days | Trips | theta_hat | UCB95 | SE_boot | eps_X | Null power | p_upper |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | K6-cp1-01 ZC | B | null | 1130 | 1060 | -1.5630 | -1.2071 | +0.2182 | 4.0 | +1.000 | +1.0000 |
| 2 | K6-cp1-01 ZW | B | null | 1129 | 1075 | -1.1743 | -0.6529 | +0.3159 | 4.0 | +1.000 | +0.9998 |
| 3 | K6-cp1-01 ZS | B | null | 1136 | 1109 | -1.7015 | -1.1732 | +0.3261 | 5.0 | +1.000 | +1.0000 |
| 4 | K6-cp1-01 ZM | B | null | 1106 | 1075 | -1.2097 | -0.6902 | +0.3119 | 5.0 | +1.000 | +0.9999 |
| 5 | K6-cp1-01 ZL | B | null | 1129 | 1076 | -2.4878 | -1.6296 | +0.5172 | 11.0 | +1.000 | +1.0000 |
| 6 | K6-cp1-01 HE | B | null | 1104 | 833 | -1.0354 | -0.4729 | +0.3433 | 7.0 | +1.000 | +0.9986 |
| 7 | K6-cp1-01 LE | B | null | 1109 | 915 | -2.0954 | -1.6102 | +0.3000 | 8.0 | +1.000 | +1.0000 |
| 8 | K6-cp2-01 ZC | B | null | 1130 | 1008 | -1.6711 | -1.0677 | +0.3695 | 4.0 | +1.000 | +1.0000 |
| 9 | K6-cp2-01 ZW | B | null | 1129 | 1070 | -0.8385 | +0.3623 | +0.7176 | 4.0 | +1.000 | +0.8807 |
| 10 | K6-cp2-01 ZS | B | null | 1136 | 1077 | -1.7164 | -0.4434 | +0.7787 | 5.0 | +1.000 | +0.9845 |
| 11 | K6-cp2-01 ZM | B | null | 1106 | 1033 | -1.3235 | -0.1204 | +0.7288 | 5.0 | +1.000 | +0.9666 |
| 12 | K6-cp2-01 ZL | B | null | 1129 | 1081 | -2.0867 | -0.1249 | +1.2129 | 11.0 | +1.000 | +0.9531 |
| 13 | K6-cp2-01 HE | B | null | 1104 | 906 | -1.0058 | +0.3860 | +0.8592 | 7.0 | +1.000 | +0.8747 |
| 14 | K6-cp2-01 LE | B | null | 1109 | 973 | -2.9227 | -1.8320 | +0.6727 | 8.0 | +1.000 | +1.0000 |
| 15 | K6-cp3-01 ZC | B | null | 1130 | 501 | -1.1126 | -0.2403 | +0.5310 | 4.0 | +1.000 | +0.9810 |
| 16 | K6-cp3-01 ZW | B | null | 1129 | 472 | -1.5916 | -0.0890 | +0.8982 | 4.0 | +0.998 | +0.9643 |
| 17 | K6-cp3-01 ZS | B | null | 1136 | 511 | -1.9350 | -0.3332 | +0.9650 | 5.0 | +1.000 | +0.9770 |
| 18 | K6-cp3-01 ZM | B | null | 1106 | 515 | -1.4151 | +0.0896 | +0.8933 | 5.0 | +1.000 | +0.9452 |
| 19 | K6-cp3-01 ZL | B | null | 1129 | 482 | -1.1039 | +1.3205 | +1.4759 | 11.0 | +1.000 | +0.7683 |
| 20 | K6-cp3-01 HE | B | null | 1104 | 480 | -1.6296 | +0.1612 | +1.1061 | 7.0 | +1.000 | +0.9268 |
| 21 | K6-cp3-01 LE | B | null | 1109 | 487 | -1.8153 | -0.5006 | +0.7969 | 8.0 | +1.000 | +0.9875 |
| 22 | K6-crushgap-01 ZS | B | null | 1028 | 516 | -2.5773 | -0.6257 | +1.1941 | 5.0 | +0.994 | +0.9822 |
| 23 | K6-limitcont-01 HE | A | null by inactivity | 1104 | 10 | +0.0495 | +0.3869 | +0.2068 | 7.0 | +1.000 | +0.4088 |
| 24 | K6-limitcont-01 LE | B | inconclusive | 1109 | 0 | +0.0000 | +0.0000 | +0.0000 | 8.0 | +0.000 | +1.0000 |
| 25 | K6-wasdepre-01 ZC | B | null | 1130 | 55 | -0.2534 | +0.0387 | +0.1776 | 4.0 | +1.000 | +0.9264 |
| 26 | K6-wasdepre-01 ZS | B | null | 1136 | 57 | -0.4458 | +0.1724 | +0.3788 | 5.0 | +1.000 | +0.8782 |
| 27 | K6-wasdepost-01 ZC | B | null | 1130 | 54 | -0.0691 | +0.1482 | +0.1351 | 4.0 | +1.000 | +0.7068 |

Covered: 27; not covered: ; blocking: K6-limitcont-01 LE (inconclusive: zero trips, SE_boot = 0, null power < 0.80); null by inactivity: K6-limitcont-01 HE.
Edge chain: Holm K = 5 (m = 1); descriptive K = 9: K6-limitcont-01 HE p 0.4088 vs 0.00556; DSR variance 0.0035193 over 27 series; PBO +0.5571 over 27 series.
