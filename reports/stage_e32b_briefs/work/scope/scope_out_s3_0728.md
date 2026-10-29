# Stage E.32b: holding-time scope (F5; spec section 7)

Draft by ScopeWriter (Opus 5.5, high), 2026-10-29 from 05:27 PDT, for the lead. Facts only: every number comes from
the F5 script output (briefs/F5_holding.json, generated 2026-10-29 05:26:15 PDT), the econ model blocks (briefs/econ32b.json)
and the firm facts (briefs/F4_facts.md, briefs/F2_firms.md). No strategy outcome is computed or read. Tables are
script-built (reports/stage_e32b_briefs/work/scope/build_scope.py from scope_template.md); rerun it after the E_dir
fill. The lead's rulings on the draft's judgment items (2026-10-29) are applied in the text. Ticks unless stated; u = unknown; PT = Pacific
(America/Vancouver).

Definitions (spec 7; work/F5/README.md readings 1-12, accepted by the lead):
- c_RT = S + 0.5 (slippage, OC-5); c_f = c_RT + F_rt / v. k(h) = c / sigma_h.
- Gross edge per trade needed: break even g_be = c_f; net 1 tick g_1 = c_f + 1. Hit rate for a sign forecast:
  p = 0.5 + g / (2 m_h) with the empirical mean absolute move m_h ("emp"), and p = 0.5 + g / (1.596 sigma_h) ("norm").
- Trades: n_cap(h) = min(20, floor(L_main / h)) a day; OC, cc (close to next close) and on (close to next open) 1 a
  day; a year = 252 days.
- SR80 (true daily Sharpe that passes with probability 0.80, N = 838): discovery G3 0.2025, discovery G3 + G4
  0.2309 (binding), test 0.1936. e80(h) = SR80 sigma_h / sqrt(n_cap) ticks a trade, net (a lower bound: independent
  trades, normal moments). G(h) = c_f / sigma_h + SR80_test / sqrt(n_cap): the required gross per sigma at the test.
- Band B = {h in 5..240, OC : G <= 1.10 min G, DLL / (sigma_h v) >= 2, the hold fits before flat-by-close}; own
  broker (LR-F5-IBKR): G <= 1.10 min G only. min G runs over every row with a G, cc and on included (reading 4).
- Prior ("holds of multiple minutes to hours are best"): holds if B is non-empty within 5-240; partly if B also
  contains OC; fails if B is empty, or min G lies at 1-2 minutes, or only at OC / cc / on (reading 8 precedence).

## 0. Summary of the facts

- Top-15 prop pairs: all 15 verdicts are "holds". B is 15-30 minutes for 13 pairs, 30-60 for mffu|MYM and 15-60 for
  topstep|ZL. min G is at 30 minutes in every pair. No pair's B contains 5, 120, 240 or OC.
- Own broker (ibkr), 35 survivor codes: 20 holds, 1 partly (ZF), 14 fails (8 of them "fails (min G overnight)"
  with a non-empty band). The five top-15 codes (YM, MNQ, RTY, MYM,
  ZL) all hold at ibkr, with the same B as at the prop firms except MYM (30-120 at ibkr against 30-60 at MFFU).
- Survivors (firm-independent, c_RT basis, no verdict by reading 3): min G_RT is at 15 min for 4 codes, 30 for 20,
  60 for 4, 120 for 3 and at cc (overnight close to close) for 4 (MZC, MZW, ZB, ZN).
- k(h) falls at close to the square-root-of-time rate at every horizon for every code (section 1.2). In ratio terms
  it never flattens; what makes G turn up is the power term, which is flat up to 15 minutes (the 20-entry cap) and
  rises from 30 minutes as floor(L_main / h) cuts the number of trades a day. There is no flattening point: the band
  is set by G, that is by the 20-round-trip entry cap and the power term (section 6 item 2).
- Verdict on the prior per the spec rule: "holds" for all 15 top pairs (B lies within 5-240). Plainly: the facts
  favour holds of 15 to 60 minutes and do not support holds of hours; G rises past 60 minutes because the entry cap
  and the power term bind. The own broker shows the same, with MYM's band reaching 120.
- No prop firm allows overnight holds (evaluation, funded, weekend: all no). The prop rules (DLL against sigma_h,
  flat-by-close) never bind inside B; the DLL excludes some h from 120 minutes up, or OC, on 6 of the 15 pairs, all at h already
  outside B by G.
- The E_dir 30/120/240 economics for the top 15 are still running: section 4 has a marked placeholder table.

## 1. Layer 1 survivors (35 codes; firm-independent rows, cost basis c_RT)

All 35 survivors have S = 1 tick (sourced for 6A 6E CL GC HG NG ZB ZC ZF ZN ZS; "u" for the rest), so c_RT = 1.50
everywhere and g_be = 1.50, g_1 = 2.50 ticks for every survivor row (firm fees are added only in the pair rows).
OC1 codes take their sibling's sigma in ticks (LR-F3), so MYM = YM, M2K = RTY, M6A = 6A, M6E = 6E, MNG = NG,
BTC = MBT, XC = MZC = ZC, XK = MZS = ZS, MZL = ZL, MZM = ZM, MZW = ZW show the same sigma rows; the owned micros MCL,
MGC and MHG have their own, close values.

### 1.1 Trades a day (and a year) by horizon

| L_main | 1 | 2 | 5 | 15 | 30 | 60 | 120 | 240 | OC | cc | on |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 290 | 20 (5,040) | 20 (5,040) | 20 (5,040) | 19 (4,788) | 9 (2,268) | 4 (1,008) | 2 (504) | 1 (252) | 1 (252) | 1 (252) | 1 (252) |
| 390 | 20 (5,040) | 20 (5,040) | 20 (5,040) | 20 (5,040) | 13 (3,276) | 6 (1,512) | 3 (756) | 1 (252) | 1 (252) | 1 (252) | 1 (252) |

L_main is 390 minutes (06:30-13:00 PT) for every code except the CBOT grains and their minis and micros (290
minutes, 06:30-11:20 PT). The grains sit next to two scheduled pauses: 07:45-08:30 CT (05:45-06:30 PT, "no orders
accepted", GRAINS-14) just before the main session, and the 13:20 CT day close (11:20 PT) with Globex reopening at
19:00 CT. Both are adjacent to, not inside, the main session. The other codes' daily 60-minute breaks (16:00-17:00 CT
or 17:00-18:00 ET, 14:00-15:00 PT) lie outside the main session.

### 1.2 k_RT(h) = c_RT / sigma_h, with where the power term reaches the cost term

"power >= cost from" is the first h at which SR80_test / sqrt(n_cap) >= c_RT / sigma_h (reading 10). From that h on,
the power term, not the cost, is the larger part of G.

| code | L_main | c_RT | k 1 | k 2 | k 5 | k 15 | k 30 | k 60 | k 120 | k 240 | k OC | k cc | k on | power >= cost from | min G_RT at |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 6A | 390 | 1.50 | 0.4855 | 0.3460 | 0.2196 | 0.1279 | 0.0918 | 0.0671 | 0.0502 | 0.0361 | 0.0256 | 0.0149 | 0.0181 | 60 | 30 |
| 6E | 390 | 1.50 | 0.4218 | 0.3005 | 0.1913 | 0.1108 | 0.0788 | 0.0573 | 0.0431 | 0.0313 | 0.0221 | 0.0137 | 0.0176 | 60 | 30 |
| BTC | 390 | 1.50 u | 0.3052 | 0.2169 | 0.1396 | 0.0817 | 0.0581 | 0.0409 | 0.0292 | 0.0204 | 0.0143 | 0.0091 | 0.0125 | 60 | 30 |
| CL | 390 | 1.50 | 0.2384 | 0.1698 | 0.1087 | 0.0635 | 0.0448 | 0.0311 | 0.0214 | 0.0151 | 0.0124 | 0.0088 | 0.0120 | 30 | 30 |
| GC | 390 | 1.50 | 0.2838 | 0.2014 | 0.1272 | 0.0731 | 0.0520 | 0.0384 | 0.0287 | 0.0204 | 0.0134 | 0.0089 | 0.0132 | 30 | 30 |
| HG | 390 | 1.50 | 0.4779 | 0.3401 | 0.2175 | 0.1271 | 0.0909 | 0.0660 | 0.0478 | 0.0347 | 0.0266 | 0.0144 | 0.0166 | 60 | 30 |
| M2K | 390 | 1.50 u | 0.1515 | 0.1073 | 0.0683 | 0.0401 | 0.0290 | 0.0212 | 0.0157 | 0.0113 | 0.0077 | 0.0063 | 0.0105 | 15 | 30 |
| M6A | 390 | 1.50 u | 0.9709 | 0.6919 | 0.4391 | 0.2557 | 0.1835 | 0.1342 | 0.1005 | 0.0722 | 0.0513 | 0.0298 | 0.0362 | 120 | 120 |
| M6E | 390 | 1.50 u | 0.8437 | 0.6010 | 0.3826 | 0.2216 | 0.1575 | 0.1145 | 0.0862 | 0.0625 | 0.0441 | 0.0274 | 0.0351 | 120 | 60 |
| MBT | 390 | 1.50 u | 0.3052 | 0.2169 | 0.1396 | 0.0817 | 0.0581 | 0.0409 | 0.0292 | 0.0204 | 0.0143 | 0.0091 | 0.0125 | 60 | 30 |
| MCL | 390 | 1.50 u | 0.2314 | 0.1663 | 0.1075 | 0.0633 | 0.0447 | 0.0310 | 0.0214 | 0.0151 | 0.0125 | 0.0088 | 0.0120 | 30 | 30 |
| MGC | 390 | 1.50 u | 0.2781 | 0.1984 | 0.1260 | 0.0725 | 0.0517 | 0.0382 | 0.0287 | 0.0204 | 0.0134 | 0.0089 | 0.0132 | 30 | 30 |
| MHG | 390 | 1.50 u | 0.4438 | 0.3160 | 0.2044 | 0.1223 | 0.0887 | 0.0650 | 0.0475 | 0.0345 | 0.0267 | 0.0141 | 0.0163 | 60 | 30 |
| MNG | 390 | 1.50 u | 0.2391 | 0.1714 | 0.1104 | 0.0657 | 0.0461 | 0.0317 | 0.0227 | 0.0162 | 0.0142 | 0.0085 | 0.0100 | 30 | 30 |
| MNQ | 390 | 1.50 u | 0.0542 | 0.0384 | 0.0244 | 0.0142 | 0.0102 | 0.0074 | 0.0053 | 0.0038 | 0.0026 | 0.0021 | 0.0036 | 2 | 15 |
| MYM | 390 | 1.50 u | 0.1246 | 0.0885 | 0.0565 | 0.0332 | 0.0237 | 0.0169 | 0.0122 | 0.0090 | 0.0066 | 0.0054 | 0.0097 | 15 | 15 |
| MZC | 290 | 1.50 u | 1.7502 | 1.2855 | 0.8456 | 0.5015 | 0.3593 | 0.2536 | 0.1765 | 0.1231 | 0.1073 | 0.0831 | 0.1332 | 240 | cc |
| MZL | 290 | 1.50 u | 0.5438 | 0.3886 | 0.2489 | 0.1473 | 0.1068 | 0.0785 | 0.0568 | 0.0386 | 0.0331 | 0.0257 | 0.0428 | 60 | 30 |
| MZM | 290 | 1.50 u | 0.9517 | 0.6793 | 0.4386 | 0.2621 | 0.1871 | 0.1339 | 0.0955 | 0.0688 | 0.0578 | 0.0444 | 0.0674 | 120 | 60 |
| MZS | 290 | 1.50 u | 0.9660 | 0.6907 | 0.4465 | 0.2638 | 0.1877 | 0.1321 | 0.0921 | 0.0676 | 0.0584 | 0.0437 | 0.0641 | 120 | 60 |
| MZW | 290 | 1.50 u | 1.1009 | 0.7927 | 0.5169 | 0.3063 | 0.2249 | 0.1626 | 0.1204 | 0.0850 | 0.0723 | 0.0503 | 0.0758 | 120 | cc |
| NG | 390 | 1.50 | 0.2391 | 0.1714 | 0.1104 | 0.0657 | 0.0461 | 0.0317 | 0.0227 | 0.0162 | 0.0142 | 0.0085 | 0.0100 | 30 | 30 |
| RTY | 390 | 1.50 u | 0.1515 | 0.1073 | 0.0683 | 0.0401 | 0.0290 | 0.0212 | 0.0157 | 0.0113 | 0.0077 | 0.0063 | 0.0105 | 15 | 30 |
| XC | 290 | 1.50 u | 0.4376 | 0.3214 | 0.2114 | 0.1254 | 0.0898 | 0.0634 | 0.0441 | 0.0308 | 0.0268 | 0.0208 | 0.0333 | 60 | 30 |
| XK | 290 | 1.50 u | 0.2415 | 0.1727 | 0.1116 | 0.0660 | 0.0469 | 0.0330 | 0.0230 | 0.0169 | 0.0146 | 0.0109 | 0.0160 | 30 | 15 |
| YM | 390 | 1.50 u | 0.1246 | 0.0885 | 0.0565 | 0.0332 | 0.0237 | 0.0169 | 0.0122 | 0.0090 | 0.0066 | 0.0054 | 0.0097 | 15 | 15 |
| ZB | 390 | 1.50 | 1.2350 | 0.9131 | 0.6000 | 0.3576 | 0.2599 | 0.1924 | 0.1399 | 0.0975 | 0.0664 | 0.0435 | 0.0570 | 240 | cc |
| ZC | 290 | 1.50 | 0.8751 | 0.6428 | 0.4228 | 0.2507 | 0.1796 | 0.1268 | 0.0883 | 0.0615 | 0.0537 | 0.0416 | 0.0666 | 120 | 60 |
| ZF | 390 | 1.50 | 0.8958 | 0.6496 | 0.4169 | 0.2434 | 0.1758 | 0.1296 | 0.0947 | 0.0668 | 0.0455 | 0.0297 | 0.0390 | 120 | 120 |
| ZL | 290 | 1.50 u | 0.2719 | 0.1943 | 0.1245 | 0.0736 | 0.0534 | 0.0393 | 0.0284 | 0.0193 | 0.0166 | 0.0128 | 0.0214 | 30 | 30 |
| ZM | 290 | 1.50 u | 0.4759 | 0.3397 | 0.2193 | 0.1310 | 0.0935 | 0.0670 | 0.0478 | 0.0344 | 0.0289 | 0.0222 | 0.0337 | 60 | 30 |
| ZN | 390 | 1.50 | 1.1773 | 0.8818 | 0.5819 | 0.3466 | 0.2525 | 0.1877 | 0.1368 | 0.0952 | 0.0648 | 0.0420 | 0.0550 | 240 | cc |
| ZS | 290 | 1.50 | 0.4830 | 0.3454 | 0.2233 | 0.1319 | 0.0939 | 0.0661 | 0.0461 | 0.0338 | 0.0292 | 0.0218 | 0.0320 | 60 | 30 |
| ZT | 390 | 1.50 u | 0.9504 | 0.6919 | 0.4461 | 0.2609 | 0.1875 | 0.1363 | 0.0999 | 0.0718 | 0.0492 | 0.0312 | 0.0413 | 120 | 120 |
| ZW | 290 | 1.50 u | 0.5505 | 0.3964 | 0.2584 | 0.1531 | 0.1124 | 0.0813 | 0.0602 | 0.0425 | 0.0361 | 0.0251 | 0.0379 | 60 | 30 |

Square-root-of-time check: sigma(h1) / sigma(h2) x sqrt(h2 / h1) for each step (OC counted as L_main minutes). A value
of 1 means k falls exactly as 1/sqrt(h); above 1, sigma grows more slowly than sqrt(h) (k falls more slowly, the
curve flattens relative to a random walk); below 1, faster. Volatility statistics only (F3).

| code | 1->2 | 2->5 | 5->15 | 15->30 | 30->60 | 60->120 | 120->240 | 240->OC |
|---|---|---|---|---|---|---|---|---|
| 6A | 1.008 | 1.003 | 1.009 | 1.015 | 1.034 | 1.059 | 1.017 | 0.905 |
| 6E | 1.007 | 1.007 | 1.003 | 1.005 | 1.028 | 1.064 | 1.026 | 0.900 |
| BTC | 1.005 | 1.018 | 1.013 | 1.006 | 0.996 | 1.010 | 0.989 | 0.891 |
| CL | 1.007 | 1.012 | 1.012 | 0.997 | 0.981 | 0.976 | 0.996 | 1.047 |
| GC | 1.003 | 0.999 | 0.995 | 1.006 | 1.044 | 1.058 | 1.006 | 0.838 |
| HG | 1.007 | 1.011 | 1.012 | 1.012 | 1.026 | 1.025 | 1.026 | 0.978 |
| M2K | 1.002 | 1.007 | 1.017 | 1.022 | 1.034 | 1.046 | 1.022 | 0.872 |
| M6A | 1.008 | 1.003 | 1.009 | 1.015 | 1.034 | 1.059 | 1.017 | 0.905 |
| M6E | 1.007 | 1.007 | 1.003 | 1.005 | 1.028 | 1.064 | 1.026 | 0.900 |
| MBT | 1.005 | 1.018 | 1.013 | 1.006 | 0.996 | 1.010 | 0.989 | 0.891 |
| MCL | 1.017 | 1.022 | 1.021 | 0.998 | 0.982 | 0.977 | 0.996 | 1.052 |
| MGC | 1.009 | 1.004 | 0.996 | 1.008 | 1.046 | 1.061 | 1.008 | 0.838 |
| MHG | 1.007 | 1.023 | 1.036 | 1.025 | 1.037 | 1.034 | 1.026 | 0.986 |
| MNG | 1.014 | 1.018 | 1.031 | 0.992 | 0.974 | 1.012 | 1.011 | 1.115 |
| MNQ | 1.002 | 1.004 | 1.009 | 1.016 | 1.026 | 1.012 | 1.028 | 0.863 |
| MYM | 1.004 | 1.010 | 1.016 | 1.012 | 1.010 | 1.019 | 1.046 | 0.936 |
| MZC | 1.039 | 1.040 | 1.027 | 1.013 | 0.998 | 0.984 | 0.986 | 0.959 |
| MZL | 1.011 | 1.013 | 1.025 | 1.025 | 1.040 | 1.023 | 0.961 | 0.943 |
| MZM | 1.009 | 1.021 | 1.035 | 1.010 | 1.012 | 1.009 | 1.018 | 0.924 |
| MZS | 1.011 | 1.022 | 1.023 | 1.006 | 0.995 | 0.986 | 1.037 | 0.950 |
| MZW | 1.018 | 1.031 | 1.026 | 1.038 | 1.022 | 1.047 | 0.998 | 0.935 |
| NG | 1.014 | 1.018 | 1.031 | 0.992 | 0.974 | 1.012 | 1.011 | 1.115 |
| RTY | 1.002 | 1.007 | 1.017 | 1.022 | 1.034 | 1.046 | 1.022 | 0.872 |
| XC | 1.039 | 1.040 | 1.027 | 1.013 | 0.998 | 0.984 | 0.986 | 0.959 |
| XK | 1.011 | 1.022 | 1.023 | 1.006 | 0.995 | 0.986 | 1.037 | 0.950 |
| YM | 1.004 | 1.010 | 1.016 | 1.012 | 1.010 | 1.019 | 1.046 | 0.936 |
| ZB | 1.046 | 1.039 | 1.032 | 1.028 | 1.047 | 1.028 | 0.986 | 0.869 |
| ZC | 1.039 | 1.040 | 1.027 | 1.013 | 0.998 | 0.984 | 0.986 | 0.959 |
| ZF | 1.025 | 1.015 | 1.011 | 1.022 | 1.043 | 1.033 | 0.997 | 0.869 |
| ZL | 1.011 | 1.013 | 1.025 | 1.025 | 1.040 | 1.023 | 0.961 | 0.943 |
| ZM | 1.009 | 1.021 | 1.035 | 1.010 | 1.012 | 1.009 | 1.018 | 0.924 |
| ZN | 1.059 | 1.043 | 1.032 | 1.030 | 1.051 | 1.031 | 0.984 | 0.867 |
| ZS | 1.011 | 1.022 | 1.023 | 1.006 | 0.995 | 0.986 | 1.037 | 0.950 |
| ZT | 1.030 | 1.019 | 1.013 | 1.016 | 1.028 | 1.036 | 1.017 | 0.872 |
| ZW | 1.018 | 1.031 | 1.026 | 1.038 | 1.022 | 1.047 | 0.998 | 0.935 |

Reading of the two tables (facts): from 1 to 120 minutes every ratio lies between 0.97 and 1.07, so k(h) falls at
nearly the random-walk rate (about 0.71 per doubling of h) for every code; there is no horizon at which k levels off.
The largest departures are the rates and grains at 1-5 minutes (ratios up to 1.06: sigma grows a little slower than
sqrt(h), k falls a little slower) and the 240 -> OC step (0.84-0.99 for most codes; 1.05-1.12 for CL, MCL, NG, MNG),
where the open-to-close move is larger than the 240-minute scaling implies. k therefore has no flattening point; the
"power >= cost from" column marks where the power term, not the cost, becomes the larger part of G.

### 1.3 G_RT(h) (minimum in bold)

| code | G 1 | G 2 | G 5 | G 15 | G 30 | G 60 | G 120 | G 240 | G OC | G cc | G on | min G_RT | at |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 6A | 0.5288 | 0.3893 | 0.2629 | 0.1712 | **0.1455** | 0.1461 | 0.1620 | 0.2297 | 0.2193 | 0.2085 | 0.2117 | 0.1455 | 30 |
| 6E | 0.4651 | 0.3438 | 0.2346 | 0.1541 | **0.1325** | 0.1363 | 0.1549 | 0.2249 | 0.2157 | 0.2073 | 0.2112 | 0.1325 | 30 |
| BTC | 0.3485 | 0.2602 | 0.1829 | 0.1250 | **0.1118** | 0.1200 | 0.1410 | 0.2141 | 0.2079 | 0.2028 | 0.2061 | 0.1118 | 30 |
| CL | 0.2817 | 0.2131 | 0.1520 | 0.1068 | **0.0985** | 0.1101 | 0.1332 | 0.2087 | 0.2060 | 0.2024 | 0.2056 | 0.0985 | 30 |
| GC | 0.3271 | 0.2447 | 0.1705 | 0.1164 | **0.1057** | 0.1174 | 0.1405 | 0.2141 | 0.2071 | 0.2025 | 0.2069 | 0.1057 | 30 |
| HG | 0.5212 | 0.3834 | 0.2608 | 0.1704 | **0.1446** | 0.1450 | 0.1596 | 0.2283 | 0.2202 | 0.2080 | 0.2103 | 0.1446 | 30 |
| M2K | 0.1948 | 0.1506 | 0.1116 | 0.0834 | **0.0827** | 0.1002 | 0.1275 | 0.2049 | 0.2014 | 0.1999 | 0.2042 | 0.0827 | 30 |
| M6A | 1.0142 | 0.7352 | 0.4824 | 0.2990 | 0.2372 | 0.2132 | **0.2122** | 0.2659 | 0.2449 | 0.2234 | 0.2298 | 0.2122 | 120 |
| M6E | 0.8870 | 0.6443 | 0.4259 | 0.2649 | 0.2112 | **0.1936** | 0.1980 | 0.2561 | 0.2378 | 0.2211 | 0.2287 | 0.1936 | 60 |
| MBT | 0.3485 | 0.2602 | 0.1829 | 0.1250 | **0.1118** | 0.1200 | 0.1410 | 0.2141 | 0.2079 | 0.2028 | 0.2061 | 0.1118 | 30 |
| MCL | 0.2746 | 0.2096 | 0.1508 | 0.1066 | **0.0984** | 0.1101 | 0.1332 | 0.2087 | 0.2061 | 0.2024 | 0.2057 | 0.0984 | 30 |
| MGC | 0.3214 | 0.2417 | 0.1693 | 0.1158 | **0.1054** | 0.1173 | 0.1405 | 0.2140 | 0.2070 | 0.2025 | 0.2069 | 0.1054 | 30 |
| MHG | 0.4871 | 0.3593 | 0.2477 | 0.1656 | **0.1424** | 0.1441 | 0.1593 | 0.2281 | 0.2203 | 0.2078 | 0.2099 | 0.1424 | 30 |
| MNG | 0.2824 | 0.2147 | 0.1537 | 0.1090 | **0.0998** | 0.1108 | 0.1345 | 0.2099 | 0.2078 | 0.2022 | 0.2036 | 0.0998 | 30 |
| MNQ | 0.0975 | 0.0817 | 0.0677 | **0.0575** | 0.0639 | 0.0864 | 0.1171 | 0.1975 | 0.1962 | 0.1958 | 0.1973 | 0.0575 | 15 |
| MYM | 0.1679 | 0.1318 | 0.0998 | **0.0764** | 0.0774 | 0.0960 | 0.1240 | 0.2027 | 0.2003 | 0.1991 | 0.2033 | 0.0764 | 15 |
| MZC | 1.7935 | 1.3288 | 0.8889 | 0.5459 | 0.4238 | 0.3504 | 0.3135 | 0.3167 | 0.3010 | **0.2768** | 0.3268 | 0.2768 | cc |
| MZL | 0.5871 | 0.4319 | 0.2922 | 0.1917 | **0.1713** | 0.1753 | 0.1937 | 0.2322 | 0.2267 | 0.2193 | 0.2364 | 0.1713 | 30 |
| MZM | 0.9950 | 0.7226 | 0.4819 | 0.3065 | 0.2516 | **0.2307** | 0.2324 | 0.2624 | 0.2514 | 0.2380 | 0.2611 | 0.2307 | 60 |
| MZS | 1.0093 | 0.7340 | 0.4898 | 0.3082 | 0.2523 | **0.2289** | 0.2291 | 0.2612 | 0.2520 | 0.2373 | 0.2577 | 0.2289 | 60 |
| MZW | 1.1442 | 0.8360 | 0.5602 | 0.3507 | 0.2894 | 0.2594 | 0.2573 | 0.2786 | 0.2659 | **0.2439** | 0.2695 | 0.2439 | cc |
| NG | 0.2824 | 0.2147 | 0.1537 | 0.1090 | **0.0998** | 0.1108 | 0.1345 | 0.2099 | 0.2078 | 0.2022 | 0.2036 | 0.0998 | 30 |
| RTY | 0.1948 | 0.1506 | 0.1116 | 0.0834 | **0.0827** | 0.1002 | 0.1275 | 0.2049 | 0.2014 | 0.1999 | 0.2042 | 0.0827 | 30 |
| XC | 0.4808 | 0.3647 | 0.2547 | 0.1698 | **0.1544** | 0.1602 | 0.1811 | 0.2244 | 0.2205 | 0.2144 | 0.2269 | 0.1544 | 30 |
| XK | 0.2848 | 0.2160 | 0.1549 | **0.1104** | 0.1115 | 0.1298 | 0.1599 | 0.2105 | 0.2082 | 0.2045 | 0.2096 | 0.1104 | 15 |
| YM | 0.1679 | 0.1318 | 0.0998 | **0.0764** | 0.0774 | 0.0960 | 0.1240 | 0.2027 | 0.2003 | 0.1991 | 0.2033 | 0.0764 | 15 |
| ZB | 1.2783 | 0.9564 | 0.6433 | 0.4009 | 0.3136 | 0.2715 | 0.2516 | 0.2911 | 0.2600 | **0.2372** | 0.2507 | 0.2372 | cc |
| ZC | 0.9184 | 0.6861 | 0.4661 | 0.2952 | 0.2442 | **0.2236** | 0.2252 | 0.2552 | 0.2473 | 0.2352 | 0.2602 | 0.2236 | 60 |
| ZF | 0.9391 | 0.6929 | 0.4602 | 0.2867 | 0.2295 | 0.2087 | **0.2065** | 0.2604 | 0.2391 | 0.2233 | 0.2327 | 0.2065 | 120 |
| ZL | 0.3152 | 0.2376 | 0.1678 | 0.1181 | **0.1179** | 0.1361 | 0.1653 | 0.2129 | 0.2102 | 0.2065 | 0.2150 | 0.1179 | 30 |
| ZM | 0.5191 | 0.3830 | 0.2626 | 0.1755 | **0.1581** | 0.1638 | 0.1847 | 0.2280 | 0.2225 | 0.2158 | 0.2273 | 0.1581 | 30 |
| ZN | 1.2206 | 0.9251 | 0.6251 | 0.3899 | 0.3062 | 0.2668 | 0.2486 | 0.2889 | 0.2584 | **0.2356** | 0.2486 | 0.2356 | cc |
| ZS | 0.5263 | 0.3887 | 0.2666 | 0.1763 | **0.1584** | 0.1629 | 0.1830 | 0.2274 | 0.2228 | 0.2155 | 0.2257 | 0.1584 | 30 |
| ZT | 0.9937 | 0.7352 | 0.4894 | 0.3042 | 0.2412 | 0.2154 | **0.2116** | 0.2655 | 0.2428 | 0.2248 | 0.2350 | 0.2116 | 120 |
| ZW | 0.5938 | 0.4397 | 0.3017 | 0.1976 | **0.1770** | 0.1781 | 0.1971 | 0.2361 | 0.2298 | 0.2188 | 0.2315 | 0.1770 | 30 |

Where the minimum lies:

| min G_RT at | codes | list |
|---|---|---|
| 15 | 4 | MNQ MYM XK YM |
| 30 | 20 | 6A 6E BTC CL GC HG M2K MBT MCL MGC MHG MNG MZL NG RTY XC ZL ZM ZS ZW |
| 60 | 4 | M6E MZM MZS ZC |
| 120 | 3 | M6A ZF ZT |
| cc | 4 | MZC MZW ZB ZN |

### 1.4 Hit rate needed (empirical m_h): break even / net 1 tick

Values above 1 are kept as computed (reading 12): at 1 minute some codes cannot break even with any sign forecast.
The normal-approximation p (p_norm) is in F5_holding.json beside each value and in the pair tables below.

| code | p 1 | p 2 | p 5 | p 15 | p 30 | p 60 | p 120 | p 240 | p OC | p cc | p on |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 6A | 0.876 / 1.127 | 0.765 / 0.941 | 0.667 / 0.778 | 0.597 / 0.661 | 0.569 / 0.615 | 0.549 / 0.582 | 0.535 / 0.559 | 0.525 / 0.541 | 0.517 / 0.529 | 0.510 / 0.517 | 0.512 / 0.519 |
| 6E | 0.828 / 1.046 | 0.731 / 0.885 | 0.645 / 0.742 | 0.583 / 0.639 | 0.559 / 0.598 | 0.542 / 0.570 | 0.530 / 0.550 | 0.521 / 0.536 | 0.515 / 0.525 | 0.509 / 0.515 | 0.512 / 0.519 |
| BTC | 0.794 / 0.991 | 0.690 / 0.816 | 0.614 / 0.690 | 0.566 / 0.611 | 0.547 / 0.579 | 0.533 / 0.555 | 0.523 / 0.538 | 0.516 / 0.526 | 0.511 / 0.518 | 0.507 / 0.511 | 0.510 / 0.517 |
| CL | 0.672 / 0.787 | 0.621 / 0.702 | 0.577 / 0.628 | 0.544 / 0.574 | 0.531 / 0.552 | 0.521 / 0.536 | 0.515 / 0.524 | 0.510 / 0.517 | 0.508 / 0.513 | 0.505 / 0.509 | 0.508 / 0.513 |
| GC | 0.719 / 0.864 | 0.653 / 0.755 | 0.596 / 0.661 | 0.555 / 0.592 | 0.539 / 0.566 | 0.528 / 0.547 | 0.521 / 0.534 | 0.514 / 0.523 | 0.509 / 0.515 | 0.506 / 0.510 | 0.509 / 0.515 |
| HG | 0.858 / 1.097 | 0.752 / 0.920 | 0.660 / 0.766 | 0.593 / 0.654 | 0.567 / 0.611 | 0.548 / 0.580 | 0.534 / 0.557 | 0.524 / 0.539 | 0.518 / 0.529 | 0.509 / 0.516 | 0.511 / 0.519 |
| M2K | 0.607 / 0.678 | 0.576 / 0.626 | 0.548 / 0.580 | 0.528 / 0.547 | 0.520 / 0.534 | 0.515 / 0.524 | 0.511 / 0.518 | 0.507 / 0.512 | 0.505 / 0.508 | 0.504 / 0.507 | 0.507 / 0.512 |
| M6A | 1.252 / 1.753 | 1.029 / 1.382 | 0.834 / 1.056 | 0.693 / 0.822 | 0.638 / 0.729 | 0.599 / 0.665 | 0.571 / 0.618 | 0.549 / 0.582 | 0.535 / 0.558 | 0.520 / 0.533 | 0.523 / 0.539 |
| M6E | 1.156 / 1.593 | 0.962 / 1.270 | 0.791 / 0.984 | 0.667 / 0.778 | 0.617 / 0.695 | 0.584 / 0.640 | 0.560 / 0.600 | 0.543 / 0.571 | 0.530 / 0.550 | 0.518 / 0.530 | 0.523 / 0.539 |
| MBT | 0.794 / 0.991 | 0.690 / 0.816 | 0.614 / 0.690 | 0.566 / 0.611 | 0.547 / 0.579 | 0.533 / 0.555 | 0.523 / 0.538 | 0.516 / 0.526 | 0.511 / 0.518 | 0.507 / 0.511 | 0.510 / 0.517 |
| MCL | 0.667 / 0.779 | 0.619 / 0.698 | 0.576 / 0.626 | 0.544 / 0.573 | 0.531 / 0.552 | 0.521 / 0.536 | 0.515 / 0.524 | 0.510 / 0.517 | 0.508 / 0.513 | 0.505 / 0.509 | 0.508 / 0.513 |
| MGC | 0.715 / 0.859 | 0.652 / 0.753 | 0.596 / 0.660 | 0.555 / 0.592 | 0.539 / 0.565 | 0.528 / 0.547 | 0.521 / 0.534 | 0.514 / 0.523 | 0.509 / 0.515 | 0.506 / 0.510 | 0.509 / 0.515 |
| MHG | 0.902 / 1.170 | 0.755 / 0.925 | 0.653 / 0.755 | 0.589 / 0.648 | 0.565 / 0.608 | 0.547 / 0.579 | 0.534 / 0.557 | 0.524 / 0.539 | 0.518 / 0.530 | 0.509 / 0.516 | 0.511 / 0.518 |
| MNG | 0.703 / 0.839 | 0.644 / 0.740 | 0.591 / 0.652 | 0.553 / 0.588 | 0.537 / 0.562 | 0.526 / 0.543 | 0.518 / 0.530 | 0.513 / 0.521 | 0.510 / 0.517 | 0.506 / 0.510 | 0.508 / 0.513 |
| MNQ | 0.538 / 0.563 | 0.527 / 0.545 | 0.517 / 0.528 | 0.510 / 0.516 | 0.507 / 0.512 | 0.505 / 0.508 | 0.504 / 0.506 | 0.502 / 0.504 | 0.502 / 0.503 | 0.501 / 0.502 | 0.502 / 0.504 |
| MYM | 0.589 / 0.648 | 0.563 / 0.605 | 0.540 / 0.567 | 0.523 / 0.539 | 0.517 / 0.528 | 0.512 / 0.519 | 0.508 / 0.514 | 0.506 / 0.510 | 0.504 / 0.507 | 0.504 / 0.506 | 0.507 / 0.511 |
| MZC | 1.794 / 2.657 | 1.436 / 2.061 | 1.109 / 1.515 | 0.859 / 1.099 | 0.755 / 0.925 | 0.679 / 0.798 | 0.625 / 0.708 | 0.584 / 0.641 | 0.572 / 0.620 | 0.557 / 0.594 | 0.596 / 0.660 |
| MZL | 0.884 / 1.140 | 0.771 / 0.951 | 0.671 / 0.785 | 0.600 / 0.667 | 0.572 / 0.620 | 0.553 / 0.588 | 0.537 / 0.562 | 0.525 / 0.541 | 0.521 / 0.535 | 0.516 / 0.527 | 0.529 / 0.548 |
| MZM | 1.185 / 1.642 | 0.981 / 1.302 | 0.806 / 1.010 | 0.679 / 0.799 | 0.627 / 0.712 | 0.591 / 0.651 | 0.564 / 0.607 | 0.544 / 0.574 | 0.536 / 0.561 | 0.529 / 0.548 | 0.543 / 0.571 |
| MZS | 1.205 / 1.674 | 0.998 / 1.330 | 0.817 / 1.029 | 0.684 / 0.806 | 0.631 / 0.718 | 0.593 / 0.655 | 0.565 / 0.608 | 0.546 / 0.576 | 0.539 / 0.564 | 0.528 / 0.547 | 0.542 / 0.569 |
| MZW | 1.296 / 1.827 | 1.065 / 1.442 | 0.863 / 1.105 | 0.713 / 0.855 | 0.654 / 0.757 | 0.611 / 0.686 | 0.582 / 0.636 | 0.555 / 0.591 | 0.546 / 0.577 | 0.534 / 0.556 | 0.553 / 0.589 |
| NG | 0.703 / 0.839 | 0.644 / 0.740 | 0.591 / 0.652 | 0.553 / 0.588 | 0.537 / 0.562 | 0.526 / 0.543 | 0.518 / 0.530 | 0.513 / 0.521 | 0.510 / 0.517 | 0.506 / 0.510 | 0.508 / 0.513 |
| RTY | 0.607 / 0.678 | 0.576 / 0.626 | 0.548 / 0.580 | 0.528 / 0.547 | 0.520 / 0.534 | 0.515 / 0.524 | 0.511 / 0.518 | 0.507 / 0.512 | 0.505 / 0.508 | 0.504 / 0.507 | 0.507 / 0.512 |
| XC | 0.824 / 1.039 | 0.734 / 0.890 | 0.652 / 0.754 | 0.590 / 0.650 | 0.564 / 0.606 | 0.545 / 0.575 | 0.531 / 0.552 | 0.521 / 0.535 | 0.518 / 0.530 | 0.514 / 0.524 | 0.524 / 0.540 |
| XK | 0.676 / 0.794 | 0.625 / 0.708 | 0.579 / 0.632 | 0.546 / 0.577 | 0.533 / 0.554 | 0.523 / 0.539 | 0.516 / 0.527 | 0.511 / 0.519 | 0.510 / 0.516 | 0.507 / 0.512 | 0.510 / 0.517 |
| YM | 0.589 / 0.648 | 0.563 / 0.605 | 0.540 / 0.567 | 0.523 / 0.539 | 0.517 / 0.528 | 0.512 / 0.519 | 0.508 / 0.514 | 0.506 / 0.510 | 0.504 / 0.507 | 0.504 / 0.506 | 0.507 / 0.511 |
| ZB | 1.435 / 2.059 | 1.172 / 1.620 | 0.933 / 1.221 | 0.755 / 0.925 | 0.684 / 0.807 | 0.633 / 0.722 | 0.595 / 0.659 | 0.565 / 0.608 | 0.542 / 0.570 | 0.527 / 0.545 | 0.537 / 0.562 |
| ZC | 1.147 / 1.578 | 0.968 / 1.280 | 0.804 / 1.007 | 0.680 / 0.799 | 0.627 / 0.712 | 0.590 / 0.649 | 0.562 / 0.604 | 0.542 / 0.570 | 0.536 / 0.560 | 0.528 / 0.547 | 0.548 / 0.580 |
| ZF | 1.212 / 1.686 | 1.006 / 1.344 | 0.821 / 1.035 | 0.687 / 0.811 | 0.634 / 0.723 | 0.597 / 0.661 | 0.568 / 0.614 | 0.547 / 0.578 | 0.531 / 0.552 | 0.519 / 0.532 | 0.526 / 0.544 |
| ZL | 0.692 / 0.820 | 0.635 / 0.726 | 0.585 / 0.642 | 0.550 / 0.583 | 0.536 / 0.560 | 0.526 / 0.544 | 0.519 / 0.531 | 0.512 / 0.521 | 0.510 / 0.517 | 0.508 / 0.513 | 0.514 / 0.524 |
| ZM | 0.843 / 1.071 | 0.741 / 0.901 | 0.653 / 0.755 | 0.590 / 0.649 | 0.564 / 0.606 | 0.545 / 0.576 | 0.532 / 0.554 | 0.522 / 0.537 | 0.518 / 0.530 | 0.514 / 0.524 | 0.521 / 0.536 |
| ZN | 1.397 / 1.995 | 1.163 / 1.606 | 0.934 / 1.223 | 0.757 / 0.929 | 0.686 / 0.809 | 0.635 / 0.724 | 0.595 / 0.659 | 0.565 / 0.608 | 0.544 / 0.573 | 0.526 / 0.544 | 0.536 / 0.560 |
| ZS | 0.852 / 1.087 | 0.749 / 0.915 | 0.659 / 0.764 | 0.592 / 0.653 | 0.565 / 0.609 | 0.546 / 0.577 | 0.533 / 0.554 | 0.523 / 0.538 | 0.519 / 0.532 | 0.514 / 0.524 | 0.521 / 0.535 |
| ZT | 1.313 / 1.854 | 1.080 / 1.467 | 0.870 / 1.117 | 0.715 / 0.858 | 0.653 / 0.754 | 0.608 / 0.681 | 0.577 / 0.628 | 0.553 / 0.589 | 0.535 / 0.559 | 0.522 / 0.537 | 0.531 / 0.552 |
| ZW | 0.898 / 1.163 | 0.783 / 0.971 | 0.682 / 0.803 | 0.607 / 0.678 | 0.577 / 0.629 | 0.556 / 0.593 | 0.541 / 0.568 | 0.527 / 0.546 | 0.523 / 0.539 | 0.517 / 0.528 | 0.527 / 0.544 |

### 1.5 e80 at the test (ticks a trade, net)

Discovery values are fixed multiples of the test value because e80 = SR80 sigma_h / sqrt(n_cap): e80 disc G3 =
1.0458 x e80 test, e80 disc G3 + G4 = 1.1923 x e80 test (checked on every survivor row; full values in
F5_holding.json and in the pair tables). The gross needed for detection is c_RT + e80 (1.50 + the value below).

| code | e80 1 | e80 2 | e80 5 | e80 15 | e80 30 | e80 60 | e80 120 | e80 240 | e80 OC | e80 cc | e80 on |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 6A | 0.13 | 0.19 | 0.30 | 0.51 | 0.88 | 1.77 | 3.34 | 8.04 | 11.32 | 19.49 | 16.05 |
| 6E | 0.15 | 0.22 | 0.34 | 0.59 | 1.02 | 2.07 | 3.89 | 9.29 | 13.16 | 21.17 | 16.54 |
| BTC | 0.21 | 0.30 | 0.47 | 0.80 | 1.39 | 2.90 | 5.74 | 14.21 | 20.34 | 31.81 | 23.21 |
| CL | 0.27 | 0.38 | 0.60 | 1.02 | 1.80 | 3.82 | 7.82 | 19.24 | 23.42 | 33.10 | 24.22 |
| GC | 0.23 | 0.32 | 0.51 | 0.89 | 1.55 | 3.09 | 5.84 | 14.21 | 21.61 | 32.69 | 21.96 |
| HG | 0.14 | 0.19 | 0.30 | 0.51 | 0.89 | 1.80 | 3.51 | 8.37 | 10.91 | 20.22 | 17.46 |
| M2K | 0.43 | 0.61 | 0.95 | 1.62 | 2.78 | 5.59 | 10.70 | 25.65 | 37.49 | 46.05 | 27.57 |
| M6A | 0.07 | 0.09 | 0.15 | 0.25 | 0.44 | 0.88 | 1.67 | 4.02 | 5.66 | 9.75 | 8.02 |
| M6E | 0.08 | 0.11 | 0.17 | 0.29 | 0.51 | 1.04 | 1.95 | 4.65 | 6.58 | 10.59 | 8.27 |
| MBT | 0.21 | 0.30 | 0.47 | 0.80 | 1.39 | 2.90 | 5.74 | 14.21 | 20.34 | 31.81 | 23.21 |
| MCL | 0.28 | 0.39 | 0.60 | 1.03 | 1.80 | 3.82 | 7.82 | 19.25 | 23.32 | 33.03 | 24.11 |
| MGC | 0.23 | 0.33 | 0.52 | 0.90 | 1.56 | 3.10 | 5.85 | 14.22 | 21.64 | 32.72 | 21.95 |
| MHG | 0.15 | 0.21 | 0.32 | 0.53 | 0.91 | 1.82 | 3.53 | 8.43 | 10.89 | 20.54 | 17.83 |
| MNG | 0.27 | 0.38 | 0.59 | 0.99 | 1.75 | 3.74 | 7.38 | 17.88 | 20.45 | 34.07 | 29.17 |
| MNQ | 1.20 | 1.69 | 2.66 | 4.57 | 7.90 | 16.02 | 31.67 | 75.47 | 111.54 | 135.52 | 79.62 |
| MYM | 0.52 | 0.73 | 1.15 | 1.96 | 3.40 | 7.00 | 13.74 | 32.18 | 43.82 | 53.34 | 29.93 |
| MZC | 0.04 | 0.05 | 0.08 | 0.13 | 0.27 | 0.57 | 1.16 | 2.36 | 2.71 | 3.49 | 2.18 |
| MZL | 0.12 | 0.17 | 0.26 | 0.45 | 0.91 | 1.85 | 3.62 | 7.53 | 8.77 | 11.31 | 6.79 |
| MZM | 0.07 | 0.10 | 0.15 | 0.25 | 0.52 | 1.08 | 2.15 | 4.22 | 5.02 | 6.55 | 4.31 |
| MZS | 0.07 | 0.09 | 0.15 | 0.25 | 0.52 | 1.10 | 2.23 | 4.30 | 4.97 | 6.65 | 4.53 |
| MZW | 0.06 | 0.08 | 0.13 | 0.22 | 0.43 | 0.89 | 1.71 | 3.42 | 4.02 | 5.78 | 3.83 |
| NG | 0.27 | 0.38 | 0.59 | 0.99 | 1.75 | 3.74 | 7.38 | 17.88 | 20.45 | 34.07 | 29.17 |
| RTY | 0.43 | 0.61 | 0.95 | 1.62 | 2.78 | 5.59 | 10.70 | 25.65 | 37.49 | 46.05 | 27.57 |
| XC | 0.15 | 0.20 | 0.31 | 0.53 | 1.08 | 2.29 | 4.65 | 9.44 | 10.82 | 13.97 | 8.72 |
| XK | 0.27 | 0.38 | 0.58 | 1.01 | 2.06 | 4.40 | 8.92 | 17.19 | 19.90 | 26.60 | 18.13 |
| YM | 0.52 | 0.73 | 1.15 | 1.96 | 3.40 | 7.00 | 13.74 | 32.18 | 43.82 | 53.34 | 29.93 |
| ZB | 0.05 | 0.07 | 0.11 | 0.18 | 0.31 | 0.62 | 1.20 | 2.98 | 4.37 | 6.67 | 5.09 |
| ZC | 0.07 | 0.10 | 0.15 | 0.27 | 0.54 | 1.15 | 2.33 | 4.72 | 5.41 | 6.99 | 4.36 |
| ZF | 0.07 | 0.10 | 0.16 | 0.27 | 0.46 | 0.91 | 1.77 | 4.35 | 6.38 | 9.77 | 7.44 |
| ZL | 0.24 | 0.33 | 0.52 | 0.90 | 1.81 | 3.70 | 7.23 | 15.05 | 17.54 | 22.62 | 13.58 |
| ZM | 0.14 | 0.19 | 0.30 | 0.51 | 1.03 | 2.17 | 4.30 | 8.45 | 10.05 | 13.09 | 8.61 |
| ZN | 0.06 | 0.07 | 0.11 | 0.19 | 0.32 | 0.63 | 1.23 | 3.05 | 4.48 | 6.92 | 5.28 |
| ZS | 0.13 | 0.19 | 0.29 | 0.51 | 1.03 | 2.20 | 4.46 | 8.60 | 9.95 | 13.30 | 9.07 |
| ZT | 0.07 | 0.09 | 0.15 | 0.25 | 0.43 | 0.87 | 1.68 | 4.04 | 5.91 | 9.31 | 7.03 |
| ZW | 0.12 | 0.16 | 0.25 | 0.44 | 0.86 | 1.79 | 3.41 | 6.84 | 8.04 | 11.56 | 7.66 |

## 2. Top-15 pairs (firm rows, cost basis c_f)

### 2.1 Summary

| # | pair | v USD | fee RT USD | fee ticks | c_RT | c_f | DLL used | MLL | flat by PT | flat - main end (min) | overnight | min G at | min G | B | power >= cost from | prior |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | bulenox|YM | 5.00 | 4.18 (stated) | 0.836 | 1.50 u | 2.336 | 2,500 | 2,500 | 13:59 | 59 | no | 30 | 0.0906 | 15, 30 | 30 | holds |
| 2 | topstep|MNQ | 0.50 | 1.22 (stated) | 2.440 | 1.50 u | 3.940 | 2,000 | 2,000 | 13:10 | 10 | no | 30 | 0.0805 | 15, 30 | 15 | holds |
| 3 | tradeify|MNQ | 0.50 | 1.82 (stated) | 3.640 | 1.50 u | 5.140 | 1,250 | 2,000 | 13:45 | 45 | no | 30 | 0.0886 | 15, 30 | 30 | holds |
| 4 | tradeify|YM | 5.00 | 5.76 (stated) | 1.152 | 1.50 u | 2.652 | 1,250 | 2,000 | 13:45 | 45 | no | 30 | 0.0956 | 15, 30 | 30 | holds |
| 5 | topstep|YM | 5.00 | 3.78 (stated) | 0.756 | 1.50 u | 2.256 | 2,000 | 2,000 | 13:10 | 10 | no | 30 | 0.0894 | 15, 30 | 30 | holds |
| 6 | mffu|YM | 5.00 | 5.76 (stated) | 1.152 | 1.50 u | 2.652 | 1,000 | 2,000 | 13:10 | 10 | no | 30 | 0.0956 | 15, 30 | 30 | holds |
| 7 | bulenox|RTY | 5.00 | 4.18 (stated) | 0.836 | 1.50 u | 2.336 | 2,500 | 2,500 | 13:59 | 59 | no | 30 | 0.0988 | 15, 30 | 30 | holds |
| 8 | mffu|MNQ | 0.50 | 1.90 (stated) | 3.800 | 1.50 u | 5.300 | 1,000 | 2,000 | 13:10 | 10 | no | 30 | 0.0897 | 15, 30 | 30 | holds |
| 9 | topstep|RTY | 5.00 | 3.78 (stated) | 0.756 | 1.50 u | 2.256 | 2,000 | 2,000 | 13:10 | 10 | no | 30 | 0.0973 | 15, 30 | 30 | holds |
| 10 | tradeify|RTY | 5.00 | 5.76 (stated) | 1.152 | 1.50 u | 2.652 | 1,250 | 2,000 | 13:45 | 45 | no | 30 | 0.1049 | 15, 30 | 30 | holds |
| 11 | lucid|YM | 5.00 | 5.76 (RR-05 (u)) | 1.152 | 1.50 u | 2.652 | 1,200 | 2,000 | 13:45 | 45 | no | 30 | 0.0956 | 15, 30 | 30 | holds |
| 12 | lucid|MNQ | 0.50 | 1.90 (RR-05 (u)) | 3.800 | 1.50 u | 5.300 | 1,200 | 2,000 | 13:45 | 45 | no | 30 | 0.0897 | 15, 30 | 30 | holds |
| 13 | mffu|RTY | 5.00 | 4.68 (stated) | 0.936 | 1.50 u | 2.436 | 1,000 | 2,000 | 13:10 | 10 | no | 30 | 0.1008 | 15, 30 | 30 | holds |
| 14 | mffu|MYM | 0.50 | 1.90 (stated) | 3.800 | 1.50 u | 5.300 | 1,000 | 2,000 | 13:10 | 10 | no | 30 | 0.1375 | 30, 60 | 60 | holds |
| 15 | topstep|ZL | 6.00 | 5.28 (stated) | 0.880 | 1.50 u | 2.380 | 2,000 | 2,000 | 13:10 | 110 | no | 30 | 0.1492 | 15, 30, 60 | 60 | holds |

All five top-15 codes have S = 1 tick (u), so every c_RT here is 1.50 u (ZL: the only figure is a snippet-only average
of 2.06 ticks, which would give c_RT 2.56; section 6 item 6). Lucid's fees are RR-05 (u): the
highest round trip for the product at the other four firms (F4_facts.md section 5).

Facts that hold across the 15 pairs:
- min G is at 30 minutes in all 15. The G(15) / min G ratio is 1.00-1.09 (inside B) for 14 pairs; for mffu|MYM it is
  1.17 (outside B), and 60 minutes enters instead (1.10 or less).
- The band ends: 5 minutes is 1.33-1.77 x min G; 120 minutes 1.13-1.56 x; 240 minutes 1.50-2.53 x; OC 1.47-2.49 x.
  1 minute is 2.31-3.52 x min G and 2 minutes 1.79-2.59 x (pair tables, "G/minG").
- At the band members the hit rate needed to break even (empirical) is 0.518-0.579, and to net 1 tick 0.523-0.613.
  The gross needed per trade for detection at the test (c_f + e80 test) is 3.3-13.2 ticks; the e80 part alone is
  0.9 (topstep|ZL at 15) to 7.9 ticks (MNQ at 30).
- The power term reaches the cost term at 30 minutes for 12 pairs, at 15 for topstep|MNQ and at 60 for mffu|MYM and
  topstep|ZL. In every pair B straddles that crossover: it is where the cost term has fallen enough and before the
  power term has grown (section 6 item 2).

### 2.2 Firm rules that bear on holding time (F2_firms.md, F4_facts.md sections 4-5)

| firm (50K plan) | DLL used in F5 | MLL | flat by (local / PT) | overnight | news windows on the plan | other timing rules |
|---|---|---|---|---|---|---|
| topstep (Combine, Standard Path) | none on the plan; MLL 2,000 used (LR-DLL). An optional USD 1,000 DLL at purchase is not a violation and is not modelled | 2,000, trailing on EOD balance, monitored intraday | 15:10 CT / 13:10 PT; no new opens after 15:08 CT; flat 15 min before an early close | no, any stage, no weekend | Tier 1 (CPI, NFP, PPI 07:30 CT; FOMC 13:00, presser 13:30 CT): no new opening transactions from 5 min before to 5 min after; blocks RTY, YM (full-size); MNQ, MYM capped at 3 (one lot allowed); grains not named | full maximum size into a major event prohibited (a one-lot is not max size) |
| lucid (LucidPro) | 1,200 (soft; optional at purchase) | 2,000 EOD trailing; 50,100 lock | 16:45 ET / 13:45 PT, auto-closed without failure; holiday close on early-close days | no | none on Pro (red-folder rule is LucidDaily only) | - |
| tradeify (Growth) | 1,250 | 2,000 EOD trailing, enforced in real time | 16:45 ET / 13:45 PT, or 12:59 ET on holiday early closes; auto-closed | no (no swing) | none | funded payout gate: more than 50% of trades and profit from holds over 10 s |
| mffu (Builder, Default MLL) | 1,000 (soft pause) | 2,000 EOD trailing, locks at start + 100 | 16:10 ET / 13:10 PT, auto-closed; on holiday half days no auto-liquidation and an open position breaches | no | none on Builder (T1 2-minute rule binds Rapid and Pro Sim Funded only; wording conflict on two pages, recorded unresolved) | burst strategies (straddles, strangles) banned |
| bulenox (Qualification, Option 1) | none on Option 1; MLL 2,500 used (LR-DLL). Option 2 has a 1,100 soft DLL | 2,500, real-time trailing incl. unrealized (Option 1) | 15:59 CT / 13:59 PT | no ("strictly prohibited") | none | - |

Times in PT: Topstep's FOMC windows (12:55-13:05 CT and 13:25-13:35 CT) are 10:55-11:05 and 11:25-11:35 PT, inside the
main session; the 07:30 CT windows (05:25-05:35 PT) lie before it. F5 reports news windows and pauses but they do not
enter B (reading 11).

Topstep news block, reported as excluded entry minutes (lead ruling: not a band condition under spec 7, which
builds B from G, the DLL and flat-by-close only): new opening transactions in YM and RTY (full-size, blocked) are
not accepted from 5 minutes before to 5 minutes after CPI, PPI and NFP (07:30 CT), the FOMC decision (13:00 CT) and
the FOMC press conference (13:30 CT); existing positions may be kept. In PT the FOMC windows are 10:55-11:05 and
11:25-11:35, inside the main session: 20 entry minutes on each FOMC decision day. The 07:30 CT windows (05:25-05:35
PT) lie before the main session and exclude no main-session minute. On the usual schedule (8 FOMC decisions a year;
CPI, PPI and NFP monthly; event counts from the regular calendar, not from a fetched page) that is about 3 windows a
month before the session and 160 excluded main-session entry minutes a year (about 13 a month, 0.16% of 252 x 390
main-session minutes). MNQ and MYM are capped at 3 (one lot still allowed), so a one-lot entry is not blocked; ZL is
not named (grains are not on the list). Spec Q6 counts news windows for the event families (R2/R3), not here.

Soft DLLs (Lucid USD 1,200 and MFFU USD 1,000: a pause, not a failure) are treated like hard ones in every DLL /
(sigma v) column: the conservative reading, since spec 7 draws no distinction. No DLL binds inside any B.

Limitation: holiday early-close rules (Topstep flat 15 minutes before an early close, Tradeify 12:59 ET, MFFU breach
on half days with no auto-liquidation, Lucid at the holiday close) are not modelled in "fits"; F5 checks the regular
close only, and F3 excluded the EARLY_HALT dates from the sigma estimates.

### 2.3 Per-pair detail

Each pair has two tables. (a) costs and hit rates: sigma_h, k for c_RT and c_f, g_be and g_1 (ticks), p for break
even and for net 1 tick (empirical and normal). (b) trades, power and prop rules: n_cap a day, trades a year, e80 at
discovery (G3, G3 + G4) and test (ticks a trade), the gross needed for detection at the test, G, G / min G, DLL and
MLL against sigma_h v at one contract (soft DLLs counted as hard: the conservative reading), the latest start for an h-minute hold, whether it fits before flat-by-close,
and membership of B. cc and on rows are reported apart (not tradable at any prop firm: overnight not allowed; they
count toward min G only, reading 9).

### 1. bulenox|YM

- Costs: S 1.00 tick (u) + 0.5 slippage = c_RT 1.50; fee USD 4.18 RT (stated) / v 5.00 = 0.836 ticks; c_f 2.336 ticks (g_be), g_1 3.336 ticks.
- Limits: DLL used USD 2,500 (mll_50k (no daily limit)); MLL USD 2,500 (Option 1: real-time trailing on highest intraday value incl. unrealized; Option 2: end-of-day trailing; Master: fixed at 50,100 once account value reaches 52,600).
- Session: main 06:30-13:00 PT; flat by 15:59 CT = 13:59 PT (59 min after the main-session end); overnight no (evaluation no, funded no, weekend no).
- News: no news rule -> none (F2_firms.json:firms.bulenox.news_windows).
- Pauses: 14:00-15:00 PT Sun-Fri (daily 60-minute break 17:00-18:00 ET; EQUITY-47): outside.
- G: min 0.0906 at 30; power term >= cost term from h = 30. B = 15, 30 (contiguous yes); excluded: 5: G/minG = 1.4486 > 1.10; 60: G/minG = 1.1630 > 1.10; 120: G/minG = 1.4429 > 1.10; 240: G/minG = 2.2912 > 1.10; OC: G/minG = 2.2500 > 1.10. Prior: holds (B = 15, 30 minutes, inside 5 to 240).
- u: S: no sourced spread -> 1 tick (u).

| h | sigma_h | k_RT | k_f | g_be | g_1 | p_be emp | p_be norm | p_1 emp | p_1 norm |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 12.04 | 0.1246 | 0.1941 | 2.336 | 3.336 | 0.638 | 0.622 | 0.697 | 0.674 |
| 2 | 16.95 | 0.0885 | 0.1378 | 2.336 | 3.336 | 0.598 | 0.586 | 0.641 | 0.623 |
| 5 | 26.54 | 0.0565 | 0.0880 | 2.336 | 3.336 | 0.563 | 0.555 | 0.589 | 0.579 |
| 15 | 45.24 | 0.0332 | 0.0516 | 2.336 | 3.336 | 0.536 | 0.532 | 0.552 | 0.546 |
| 30 | 63.23 | 0.0237 | 0.0369 | 2.336 | 3.336 | 0.526 | 0.523 | 0.537 | 0.533 |
| 60 | 88.56 | 0.0169 | 0.0264 | 2.336 | 3.336 | 0.518 | 0.517 | 0.526 | 0.524 |
| 120 | 122.94 | 0.0122 | 0.0190 | 2.336 | 3.336 | 0.513 | 0.512 | 0.518 | 0.517 |
| 240 | 166.20 | 0.0090 | 0.0141 | 2.336 | 3.336 | 0.509 | 0.509 | 0.513 | 0.513 |
| OC | 226.31 | 0.0066 | 0.0103 | 2.336 | 3.336 | 0.507 | 0.506 | 0.509 | 0.509 |
| cc | 275.49 | 0.0054 | 0.0085 | 2.336 | 3.336 | 0.506 | 0.505 | 0.508 | 0.508 |
| on | 154.57 | 0.0097 | 0.0151 | 2.336 | 3.336 | 0.510 | 0.509 | 0.515 | 0.514 |

| h | n_cap/day | trades/yr | e80 disc G3 | e80 disc G3+G4 | e80 test | c_f + e80 test | G | G/minG | DLL/(sigma v) | MLL/(sigma v) | latest start PT | fits flat-by | in B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 20 | 5,040 | 0.55 | 0.62 | 0.52 | 2.86 | 0.2373 | 2.618 | 41.54 | 41.54 | 12:59 | yes | no |
| 2 | 20 | 5,040 | 0.77 | 0.88 | 0.73 | 3.07 | 0.1811 | 1.998 | 29.49 | 29.49 | 12:58 | yes | no |
| 5 | 20 | 5,040 | 1.20 | 1.37 | 1.15 | 3.49 | 0.1313 | 1.449 | 18.84 | 18.84 | 12:55 | yes | no |
| 15 | 20 | 5,040 | 2.05 | 2.34 | 1.96 | 4.29 | 0.0949 | 1.047 | 11.05 | 11.05 | 12:45 | yes | yes |
| 30 | 13 | 3,276 | 3.55 | 4.05 | 3.40 | 5.73 | 0.0906 | 1.000 | 7.91 | 7.91 | 12:30 | yes | yes |
| 60 | 6 | 1,512 | 7.32 | 8.35 | 7.00 | 9.34 | 0.1054 | 1.163 | 5.65 | 5.65 | 12:00 | yes | no |
| 120 | 3 | 756 | 14.37 | 16.39 | 13.74 | 16.08 | 0.1308 | 1.443 | 4.07 | 4.07 | 11:00 | yes | no |
| 240 | 1 | 252 | 33.65 | 38.37 | 32.18 | 34.52 | 0.2077 | 2.291 | 3.01 | 3.01 | 09:00 | yes | no |
| OC | 1 | 252 | 45.83 | 52.24 | 43.82 | 46.16 | 0.2039 | 2.250 | 2.21 | 2.21 | 06:30 | yes | no |
| cc | 1 | 252 | 55.78 | 63.60 | 53.34 | 55.68 | 0.2021 | u | 1.81 | 1.81 | u | u | u |
| on | 1 | 252 | 31.30 | 35.68 | 29.93 | 32.26 | 0.2087 | u | 3.23 | 3.23 | u | u | u |

### 2. topstep|MNQ

- Costs: S 1.00 tick (u) + 0.5 slippage = c_RT 1.50; fee USD 1.22 RT (stated) / v 0.50 = 2.440 ticks; c_f 3.940 ticks (g_be), g_1 4.940 ticks.
- Limits: DLL used USD 2,000 (mll_50k (no daily limit)); MLL USD 2,000 (trailing on end-of-day balance, monitored intraday on realized+unrealized P&L; Combine: locks at the starting balance (50,000); XFA: starts -2,000, locks at 0 once balance reaches 2,000).
- Session: main 06:30-13:00 PT; flat by 15:10 CT = 13:10 PT (10 min after the main-session end); overnight no (evaluation no, funded no, weekend no).
- News: Tier 1 news window (same events): micro capped -> capped at 3 at 50K (one lot allowed) (F2_firms.json:firms.topstep.news_windows).
- Topstep news window: micro capped at 3 (one lot allowed): no entry minute excluded at one lot.
- Pauses: 14:00-15:00 PT Sun-Fri (daily 60-minute break 17:00-18:00 ET; EQUITY-47): outside.
- G: min 0.0805 at 30; power term >= cost term from h = 15. B = 15, 30 (contiguous yes); excluded: 5: G/minG = 1.3334 > 1.10; 60: G/minG = 1.2237 > 1.10; 120: G/minG = 1.5617 > 1.10; 240: G/minG = 2.5313 > 1.10; OC: G/minG = 2.4907 > 1.10. Prior: holds (B = 15, 30 minutes, inside 5 to 240).
- u: S: no sourced spread -> 1 tick (u).

| h | sigma_h | k_RT | k_f | g_be | g_1 | p_be emp | p_be norm | p_1 emp | p_1 norm |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 27.68 | 0.0542 | 0.1423 | 3.940 | 4.940 | 0.599 | 0.589 | 0.624 | 0.612 |
| 2 | 39.09 | 0.0384 | 0.1008 | 3.940 | 4.940 | 0.570 | 0.563 | 0.588 | 0.579 |
| 5 | 61.54 | 0.0244 | 0.0640 | 3.940 | 4.940 | 0.545 | 0.540 | 0.556 | 0.550 |
| 15 | 105.64 | 0.0142 | 0.0373 | 3.940 | 4.940 | 0.526 | 0.523 | 0.532 | 0.529 |
| 30 | 147.10 | 0.0102 | 0.0268 | 3.940 | 4.940 | 0.518 | 0.517 | 0.523 | 0.521 |
| 60 | 202.67 | 0.0074 | 0.0194 | 3.940 | 4.940 | 0.513 | 0.512 | 0.516 | 0.515 |
| 120 | 283.31 | 0.0053 | 0.0139 | 3.940 | 4.940 | 0.509 | 0.509 | 0.512 | 0.511 |
| 240 | 389.76 | 0.0038 | 0.0101 | 3.940 | 4.940 | 0.507 | 0.506 | 0.508 | 0.508 |
| OC | 576.05 | 0.0026 | 0.0068 | 3.940 | 4.940 | 0.504 | 0.504 | 0.505 | 0.505 |
| cc | 699.90 | 0.0021 | 0.0056 | 3.940 | 4.940 | 0.504 | 0.504 | 0.504 | 0.504 |
| on | 411.21 | 0.0036 | 0.0096 | 3.940 | 4.940 | 0.507 | 0.506 | 0.508 | 0.508 |

| h | n_cap/day | trades/yr | e80 disc G3 | e80 disc G3+G4 | e80 test | c_f + e80 test | G | G/minG | DLL/(sigma v) | MLL/(sigma v) | latest start PT | fits flat-by | in B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 20 | 5,040 | 1.25 | 1.43 | 1.20 | 5.14 | 0.1856 | 2.306 | 144.50 | 144.50 | 12:59 | yes | no |
| 2 | 20 | 5,040 | 1.77 | 2.02 | 1.69 | 5.63 | 0.1441 | 1.790 | 102.34 | 102.34 | 12:58 | yes | no |
| 5 | 20 | 5,040 | 2.79 | 3.18 | 2.66 | 6.60 | 0.1073 | 1.333 | 65.00 | 65.00 | 12:55 | yes | no |
| 15 | 20 | 5,040 | 4.78 | 5.45 | 4.57 | 8.51 | 0.0806 | 1.001 | 37.87 | 37.87 | 12:45 | yes | yes |
| 30 | 13 | 3,276 | 8.26 | 9.42 | 7.90 | 11.84 | 0.0805 | 1.000 | 27.19 | 27.19 | 12:30 | yes | yes |
| 60 | 6 | 1,512 | 16.75 | 19.10 | 16.02 | 19.96 | 0.0985 | 1.224 | 19.74 | 19.74 | 12:00 | yes | no |
| 120 | 3 | 756 | 33.12 | 37.76 | 31.67 | 35.61 | 0.1257 | 1.562 | 14.12 | 14.12 | 11:00 | yes | no |
| 240 | 1 | 252 | 78.92 | 89.98 | 75.47 | 79.41 | 0.2037 | 2.531 | 10.26 | 10.26 | 09:00 | yes | no |
| OC | 1 | 252 | 116.65 | 132.98 | 111.54 | 115.48 | 0.2005 | 2.491 | 6.94 | 6.94 | 06:30 | yes | no |
| cc | 1 | 252 | 141.72 | 161.57 | 135.52 | 139.46 | 0.1993 | u | 5.72 | 5.72 | u | u | u |
| on | 1 | 252 | 83.27 | 94.93 | 79.62 | 83.56 | 0.2032 | u | 9.73 | 9.73 | u | u | u |

### 3. tradeify|MNQ

- Costs: S 1.00 tick (u) + 0.5 slippage = c_RT 1.50; fee USD 1.82 RT (stated) / v 0.50 = 3.640 ticks; c_f 5.140 ticks (g_be), g_1 6.140 ticks.
- Limits: DLL used USD 1,250 (dll_50k); MLL USD 2,000 (end-of-day trailing, enforced in real time on net liquidation; evaluation: floor 50,100 at EOD 52,100 (per essential rules example); funded: locks at 50,100 at 52,100 EOD or first payout request (E.28)).
- Session: main 06:30-13:00 PT; flat by 16:45 ET = 13:45 PT (45 min after the main-session end); overnight no (evaluation no, funded no, weekend no).
- News: no news rule -> none (F2_firms.json:firms.tradeify.news_windows).
- Pauses: 14:00-15:00 PT Sun-Fri (daily 60-minute break 17:00-18:00 ET; EQUITY-47): outside.
- G: min 0.0886 at 30; power term >= cost term from h = 30. B = 15, 30 (contiguous yes); excluded: 5: G/minG = 1.4307 > 1.10; 60: G/minG = 1.1779 > 1.10; 120: G/minG = 1.4658 > 1.10; 240: G/minG = 2.3331 > 1.10; OC: G/minG = 2.2850 > 1.10. Prior: holds (B = 15, 30 minutes, inside 5 to 240).
- u: S: no sourced spread -> 1 tick (u).

| h | sigma_h | k_RT | k_f | g_be | g_1 | p_be emp | p_be norm | p_1 emp | p_1 norm |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 27.68 | 0.0542 | 0.1857 | 5.140 | 6.140 | 0.629 | 0.616 | 0.654 | 0.639 |
| 2 | 39.09 | 0.0384 | 0.1315 | 5.140 | 6.140 | 0.592 | 0.582 | 0.610 | 0.598 |
| 5 | 61.54 | 0.0244 | 0.0835 | 5.140 | 6.140 | 0.558 | 0.552 | 0.569 | 0.563 |
| 15 | 105.64 | 0.0142 | 0.0487 | 5.140 | 6.140 | 0.534 | 0.530 | 0.540 | 0.536 |
| 30 | 147.10 | 0.0102 | 0.0349 | 5.140 | 6.140 | 0.524 | 0.522 | 0.528 | 0.526 |
| 60 | 202.67 | 0.0074 | 0.0254 | 5.140 | 6.140 | 0.517 | 0.516 | 0.520 | 0.519 |
| 120 | 283.31 | 0.0053 | 0.0181 | 5.140 | 6.140 | 0.512 | 0.511 | 0.514 | 0.514 |
| 240 | 389.76 | 0.0038 | 0.0132 | 5.140 | 6.140 | 0.508 | 0.508 | 0.510 | 0.510 |
| OC | 576.05 | 0.0026 | 0.0089 | 5.140 | 6.140 | 0.506 | 0.506 | 0.507 | 0.507 |
| cc | 699.90 | 0.0021 | 0.0073 | 5.140 | 6.140 | 0.505 | 0.505 | 0.506 | 0.505 |
| on | 411.21 | 0.0036 | 0.0125 | 5.140 | 6.140 | 0.509 | 0.508 | 0.510 | 0.509 |

| h | n_cap/day | trades/yr | e80 disc G3 | e80 disc G3+G4 | e80 test | c_f + e80 test | G | G/minG | DLL/(sigma v) | MLL/(sigma v) | latest start PT | fits flat-by | in B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 20 | 5,040 | 1.25 | 1.43 | 1.20 | 6.34 | 0.2290 | 2.583 | 90.31 | 144.50 | 12:59 | yes | no |
| 2 | 20 | 5,040 | 1.77 | 2.02 | 1.69 | 6.83 | 0.1748 | 1.972 | 63.96 | 102.34 | 12:58 | yes | no |
| 5 | 20 | 5,040 | 2.79 | 3.18 | 2.66 | 7.80 | 0.1268 | 1.431 | 40.63 | 65.00 | 12:55 | yes | no |
| 15 | 20 | 5,040 | 4.78 | 5.45 | 4.57 | 9.71 | 0.0920 | 1.037 | 23.67 | 37.87 | 12:45 | yes | yes |
| 30 | 13 | 3,276 | 8.26 | 9.42 | 7.90 | 13.04 | 0.0886 | 1.000 | 16.99 | 27.19 | 12:30 | yes | yes |
| 60 | 6 | 1,512 | 16.75 | 19.10 | 16.02 | 21.16 | 0.1044 | 1.178 | 12.34 | 19.74 | 12:00 | yes | no |
| 120 | 3 | 756 | 33.12 | 37.76 | 31.67 | 36.81 | 0.1299 | 1.466 | 8.82 | 14.12 | 11:00 | yes | no |
| 240 | 1 | 252 | 78.92 | 89.98 | 75.47 | 80.61 | 0.2068 | 2.333 | 6.41 | 10.26 | 09:00 | yes | no |
| OC | 1 | 252 | 116.65 | 132.98 | 111.54 | 116.68 | 0.2025 | 2.285 | 4.34 | 6.94 | 06:30 | yes | no |
| cc | 1 | 252 | 141.72 | 161.57 | 135.52 | 140.66 | 0.2010 | u | 3.57 | 5.72 | u | u | u |
| on | 1 | 252 | 83.27 | 94.93 | 79.62 | 84.76 | 0.2061 | u | 6.08 | 9.73 | u | u | u |

### 4. tradeify|YM

- Costs: S 1.00 tick (u) + 0.5 slippage = c_RT 1.50; fee USD 5.76 RT (stated) / v 5.00 = 1.152 ticks; c_f 2.652 ticks (g_be), g_1 3.652 ticks.
- Limits: DLL used USD 1,250 (dll_50k); MLL USD 2,000 (end-of-day trailing, enforced in real time on net liquidation; evaluation: floor 50,100 at EOD 52,100 (per essential rules example); funded: locks at 50,100 at 52,100 EOD or first payout request (E.28)).
- Session: main 06:30-13:00 PT; flat by 16:45 ET = 13:45 PT (45 min after the main-session end); overnight no (evaluation no, funded no, weekend no).
- News: no news rule -> none (F2_firms.json:firms.tradeify.news_windows).
- Pauses: 14:00-15:00 PT Sun-Fri (daily 60-minute break 17:00-18:00 ET; EQUITY-47): outside.
- G: min 0.0956 at 30; power term >= cost term from h = 30. B = 15, 30 (contiguous yes); excluded: 5: G/minG = 1.4974 > 1.10; 60: G/minG = 1.1396 > 1.10; 120: G/minG = 1.3944 > 1.10; 240: G/minG = 2.1913 > 1.10, DLL_f / (sigma_h v) = 1.504 < 2; OC: G/minG = 2.1470 > 1.10, DLL_f / (sigma_h v) = 1.105 < 2. Prior: holds (B = 15, 30 minutes, inside 5 to 240).
- u: S: no sourced spread -> 1 tick (u).

| h | sigma_h | k_RT | k_f | g_be | g_1 | p_be emp | p_be norm | p_1 emp | p_1 norm |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 12.04 | 0.1246 | 0.2203 | 2.652 | 3.652 | 0.657 | 0.638 | 0.716 | 0.690 |
| 2 | 16.95 | 0.0885 | 0.1564 | 2.652 | 3.652 | 0.612 | 0.598 | 0.654 | 0.635 |
| 5 | 26.54 | 0.0565 | 0.0999 | 2.652 | 3.652 | 0.571 | 0.563 | 0.598 | 0.586 |
| 15 | 45.24 | 0.0332 | 0.0586 | 2.652 | 3.652 | 0.541 | 0.537 | 0.557 | 0.551 |
| 30 | 63.23 | 0.0237 | 0.0419 | 2.652 | 3.652 | 0.529 | 0.526 | 0.540 | 0.536 |
| 60 | 88.56 | 0.0169 | 0.0299 | 2.652 | 3.652 | 0.521 | 0.519 | 0.528 | 0.526 |
| 120 | 122.94 | 0.0122 | 0.0216 | 2.652 | 3.652 | 0.514 | 0.514 | 0.520 | 0.519 |
| 240 | 166.20 | 0.0090 | 0.0160 | 2.652 | 3.652 | 0.510 | 0.510 | 0.514 | 0.514 |
| OC | 226.31 | 0.0066 | 0.0117 | 2.652 | 3.652 | 0.508 | 0.507 | 0.510 | 0.510 |
| cc | 275.49 | 0.0054 | 0.0096 | 2.652 | 3.652 | 0.506 | 0.506 | 0.509 | 0.508 |
| on | 154.57 | 0.0097 | 0.0172 | 2.652 | 3.652 | 0.512 | 0.511 | 0.516 | 0.515 |

| h | n_cap/day | trades/yr | e80 disc G3 | e80 disc G3+G4 | e80 test | c_f + e80 test | G | G/minG | DLL/(sigma v) | MLL/(sigma v) | latest start PT | fits flat-by | in B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 20 | 5,040 | 0.55 | 0.62 | 0.52 | 3.17 | 0.2636 | 2.756 | 20.77 | 33.23 | 12:59 | yes | no |
| 2 | 20 | 5,040 | 0.77 | 0.88 | 0.73 | 3.39 | 0.1997 | 2.088 | 14.75 | 23.59 | 12:58 | yes | no |
| 5 | 20 | 5,040 | 1.20 | 1.37 | 1.15 | 3.80 | 0.1432 | 1.497 | 9.42 | 15.07 | 12:55 | yes | no |
| 15 | 20 | 5,040 | 2.05 | 2.34 | 1.96 | 4.61 | 0.1019 | 1.066 | 5.53 | 8.84 | 12:45 | yes | yes |
| 30 | 13 | 3,276 | 3.55 | 4.05 | 3.40 | 6.05 | 0.0956 | 1.000 | 3.95 | 6.33 | 12:30 | yes | yes |
| 60 | 6 | 1,512 | 7.32 | 8.35 | 7.00 | 9.65 | 0.1090 | 1.140 | 2.82 | 4.52 | 12:00 | yes | no |
| 120 | 3 | 756 | 14.37 | 16.39 | 13.74 | 16.40 | 0.1334 | 1.394 | 2.03 | 3.25 | 11:00 | yes | no |
| 240 | 1 | 252 | 33.65 | 38.37 | 32.18 | 34.83 | 0.2096 | 2.191 | 1.50 | 2.41 | 09:00 | yes | no |
| OC | 1 | 252 | 45.83 | 52.24 | 43.82 | 46.47 | 0.2053 | 2.147 | 1.10 | 1.77 | 06:30 | yes | no |
| cc | 1 | 252 | 55.78 | 63.60 | 53.34 | 55.99 | 0.2033 | u | 0.91 | 1.45 | u | u | u |
| on | 1 | 252 | 31.30 | 35.68 | 29.93 | 32.58 | 0.2108 | u | 1.62 | 2.59 | u | u | u |

### 5. topstep|YM

- Costs: S 1.00 tick (u) + 0.5 slippage = c_RT 1.50; fee USD 3.78 RT (stated) / v 5.00 = 0.756 ticks; c_f 2.256 ticks (g_be), g_1 3.256 ticks.
- Limits: DLL used USD 2,000 (mll_50k (no daily limit)); MLL USD 2,000 (trailing on end-of-day balance, monitored intraday on realized+unrealized P&L; Combine: locks at the starting balance (50,000); XFA: starts -2,000, locks at 0 once balance reaches 2,000).
- Session: main 06:30-13:00 PT; flat by 15:10 CT = 13:10 PT (10 min after the main-session end); overnight no (evaluation no, funded no, weekend no).
- News: Tier 1 news window: no new opening transactions 5 min before to 5 min after CPI, FOMC decision, FOMC press conference, NFP, PPI -> blocked (full-size) (F2_firms.json:firms.topstep.news_windows).
- Topstep news block (excluded entry minutes; not a band condition, spec 7): no new opens 10:55-11:05 and 11:25-11:35 PT on FOMC decision days (20 main-session minutes a day, about 160 a year on the usual 8-meeting schedule); the CPI/PPI/NFP windows (05:25-05:35 PT, about 3 a month) lie before the main session. Holds may span the windows.
- Pauses: 14:00-15:00 PT Sun-Fri (daily 60-minute break 17:00-18:00 ET; EQUITY-47): outside.
- G: min 0.0894 at 30; power term >= cost term from h = 30. B = 15, 30 (contiguous yes); excluded: 5: G/minG = 1.4354 > 1.10; 60: G/minG = 1.1694 > 1.10; 120: G/minG = 1.4560 > 1.10; 240: G/minG = 2.3182 > 1.10; OC: G/minG = 2.2779 > 1.10, DLL_f / (sigma_h v) = 1.767 < 2. Prior: holds (B = 15, 30 minutes, inside 5 to 240).
- u: S: no sourced spread -> 1 tick (u).

| h | sigma_h | k_RT | k_f | g_be | g_1 | p_be emp | p_be norm | p_1 emp | p_1 norm |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 12.04 | 0.1246 | 0.1874 | 2.256 | 3.256 | 0.634 | 0.617 | 0.693 | 0.669 |
| 2 | 16.95 | 0.0885 | 0.1331 | 2.256 | 3.256 | 0.595 | 0.583 | 0.637 | 0.620 |
| 5 | 26.54 | 0.0565 | 0.0850 | 2.256 | 3.256 | 0.560 | 0.553 | 0.587 | 0.577 |
| 15 | 45.24 | 0.0332 | 0.0499 | 2.256 | 3.256 | 0.535 | 0.531 | 0.551 | 0.545 |
| 30 | 63.23 | 0.0237 | 0.0357 | 2.256 | 3.256 | 0.525 | 0.522 | 0.536 | 0.532 |
| 60 | 88.56 | 0.0169 | 0.0255 | 2.256 | 3.256 | 0.517 | 0.516 | 0.525 | 0.523 |
| 120 | 122.94 | 0.0122 | 0.0184 | 2.256 | 3.256 | 0.512 | 0.511 | 0.518 | 0.517 |
| 240 | 166.20 | 0.0090 | 0.0136 | 2.256 | 3.256 | 0.509 | 0.509 | 0.513 | 0.512 |
| OC | 226.31 | 0.0066 | 0.0100 | 2.256 | 3.256 | 0.506 | 0.506 | 0.509 | 0.509 |
| cc | 275.49 | 0.0054 | 0.0082 | 2.256 | 3.256 | 0.505 | 0.505 | 0.508 | 0.507 |
| on | 154.57 | 0.0097 | 0.0146 | 2.256 | 3.256 | 0.510 | 0.509 | 0.514 | 0.513 |

| h | n_cap/day | trades/yr | e80 disc G3 | e80 disc G3+G4 | e80 test | c_f + e80 test | G | G/minG | DLL/(sigma v) | MLL/(sigma v) | latest start PT | fits flat-by | in B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 20 | 5,040 | 0.55 | 0.62 | 0.52 | 2.78 | 0.2307 | 2.581 | 33.23 | 33.23 | 12:59 | yes | no |
| 2 | 20 | 5,040 | 0.77 | 0.88 | 0.73 | 2.99 | 0.1764 | 1.973 | 23.59 | 23.59 | 12:58 | yes | no |
| 5 | 20 | 5,040 | 1.20 | 1.37 | 1.15 | 3.41 | 0.1283 | 1.435 | 15.07 | 15.07 | 12:55 | yes | no |
| 15 | 20 | 5,040 | 2.05 | 2.34 | 1.96 | 4.21 | 0.0932 | 1.042 | 8.84 | 8.84 | 12:45 | yes | yes |
| 30 | 13 | 3,276 | 3.55 | 4.05 | 3.40 | 5.65 | 0.0894 | 1.000 | 6.33 | 6.33 | 12:30 | yes | yes |
| 60 | 6 | 1,512 | 7.32 | 8.35 | 7.00 | 9.26 | 0.1045 | 1.169 | 4.52 | 4.52 | 12:00 | yes | no |
| 120 | 3 | 756 | 14.37 | 16.39 | 13.74 | 16.00 | 0.1301 | 1.456 | 3.25 | 3.25 | 11:00 | yes | no |
| 240 | 1 | 252 | 33.65 | 38.37 | 32.18 | 34.44 | 0.2072 | 2.318 | 2.41 | 2.41 | 09:00 | yes | no |
| OC | 1 | 252 | 45.83 | 52.24 | 43.82 | 46.08 | 0.2036 | 2.278 | 1.77 | 1.77 | 06:30 | yes | no |
| cc | 1 | 252 | 55.78 | 63.60 | 53.34 | 55.60 | 0.2018 | u | 1.45 | 1.45 | u | u | u |
| on | 1 | 252 | 31.30 | 35.68 | 29.93 | 32.18 | 0.2082 | u | 2.59 | 2.59 | u | u | u |

### 6. mffu|YM

- Costs: S 1.00 tick (u) + 0.5 slippage = c_RT 1.50; fee USD 5.76 RT (stated) / v 5.00 = 1.152 ticks; c_f 2.652 ticks (g_be), g_1 3.652 ticks.
- Limits: DLL used USD 1,000 (dll_50k); MLL USD 2,000 (end-of-day trailing (open equity counted at the end of the day); locks once it reaches $100 above the starting balance).
- Session: main 06:30-13:00 PT; flat by 16:10 ET = 13:10 PT (10 min after the main-session end); overnight no (evaluation no, funded no, weekend no).
- News: T1 news (FOMC, minutes, Employment, CPI; EIA for energy traders; agricultural reports for agricultural traders): 2 min before/after, restricted accounts only (Rapid, Pro Sim Funded); Builder 50K unrestricted (page wording conflict noted by FirmRules) -> none on the Builder 50K plan (F2_firms.json:firms.mffu.news_windows).
- Pauses: 14:00-15:00 PT Sun-Fri (daily 60-minute break 17:00-18:00 ET; EQUITY-47): outside.
- G: min 0.0956 at 30; power term >= cost term from h = 30. B = 15, 30 (contiguous yes); excluded: 5: G/minG = 1.4974 > 1.10; 60: G/minG = 1.1396 > 1.10; 120: G/minG = 1.3944 > 1.10, DLL_f / (sigma_h v) = 1.627 < 2; 240: G/minG = 2.1913 > 1.10, DLL_f / (sigma_h v) = 1.203 < 2; OC: G/minG = 2.1470 > 1.10, DLL_f / (sigma_h v) = 0.884 < 2. Prior: holds (B = 15, 30 minutes, inside 5 to 240).
- u: S: no sourced spread -> 1 tick (u).

| h | sigma_h | k_RT | k_f | g_be | g_1 | p_be emp | p_be norm | p_1 emp | p_1 norm |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 12.04 | 0.1246 | 0.2203 | 2.652 | 3.652 | 0.657 | 0.638 | 0.716 | 0.690 |
| 2 | 16.95 | 0.0885 | 0.1564 | 2.652 | 3.652 | 0.612 | 0.598 | 0.654 | 0.635 |
| 5 | 26.54 | 0.0565 | 0.0999 | 2.652 | 3.652 | 0.571 | 0.563 | 0.598 | 0.586 |
| 15 | 45.24 | 0.0332 | 0.0586 | 2.652 | 3.652 | 0.541 | 0.537 | 0.557 | 0.551 |
| 30 | 63.23 | 0.0237 | 0.0419 | 2.652 | 3.652 | 0.529 | 0.526 | 0.540 | 0.536 |
| 60 | 88.56 | 0.0169 | 0.0299 | 2.652 | 3.652 | 0.521 | 0.519 | 0.528 | 0.526 |
| 120 | 122.94 | 0.0122 | 0.0216 | 2.652 | 3.652 | 0.514 | 0.514 | 0.520 | 0.519 |
| 240 | 166.20 | 0.0090 | 0.0160 | 2.652 | 3.652 | 0.510 | 0.510 | 0.514 | 0.514 |
| OC | 226.31 | 0.0066 | 0.0117 | 2.652 | 3.652 | 0.508 | 0.507 | 0.510 | 0.510 |
| cc | 275.49 | 0.0054 | 0.0096 | 2.652 | 3.652 | 0.506 | 0.506 | 0.509 | 0.508 |
| on | 154.57 | 0.0097 | 0.0172 | 2.652 | 3.652 | 0.512 | 0.511 | 0.516 | 0.515 |

| h | n_cap/day | trades/yr | e80 disc G3 | e80 disc G3+G4 | e80 test | c_f + e80 test | G | G/minG | DLL/(sigma v) | MLL/(sigma v) | latest start PT | fits flat-by | in B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 20 | 5,040 | 0.55 | 0.62 | 0.52 | 3.17 | 0.2636 | 2.756 | 16.61 | 33.23 | 12:59 | yes | no |
| 2 | 20 | 5,040 | 0.77 | 0.88 | 0.73 | 3.39 | 0.1997 | 2.088 | 11.80 | 23.59 | 12:58 | yes | no |
| 5 | 20 | 5,040 | 1.20 | 1.37 | 1.15 | 3.80 | 0.1432 | 1.497 | 7.54 | 15.07 | 12:55 | yes | no |
| 15 | 20 | 5,040 | 2.05 | 2.34 | 1.96 | 4.61 | 0.1019 | 1.066 | 4.42 | 8.84 | 12:45 | yes | yes |
| 30 | 13 | 3,276 | 3.55 | 4.05 | 3.40 | 6.05 | 0.0956 | 1.000 | 3.16 | 6.33 | 12:30 | yes | yes |
| 60 | 6 | 1,512 | 7.32 | 8.35 | 7.00 | 9.65 | 0.1090 | 1.140 | 2.26 | 4.52 | 12:00 | yes | no |
| 120 | 3 | 756 | 14.37 | 16.39 | 13.74 | 16.40 | 0.1334 | 1.394 | 1.63 | 3.25 | 11:00 | yes | no |
| 240 | 1 | 252 | 33.65 | 38.37 | 32.18 | 34.83 | 0.2096 | 2.191 | 1.20 | 2.41 | 09:00 | yes | no |
| OC | 1 | 252 | 45.83 | 52.24 | 43.82 | 46.47 | 0.2053 | 2.147 | 0.88 | 1.77 | 06:30 | yes | no |
| cc | 1 | 252 | 55.78 | 63.60 | 53.34 | 55.99 | 0.2033 | u | 0.73 | 1.45 | u | u | u |
| on | 1 | 252 | 31.30 | 35.68 | 29.93 | 32.58 | 0.2108 | u | 1.29 | 2.59 | u | u | u |

### 7. bulenox|RTY

- Costs: S 1.00 tick (u) + 0.5 slippage = c_RT 1.50; fee USD 4.18 RT (stated) / v 5.00 = 0.836 ticks; c_f 2.336 ticks (g_be), g_1 3.336 ticks.
- Limits: DLL used USD 2,500 (mll_50k (no daily limit)); MLL USD 2,500 (Option 1: real-time trailing on highest intraday value incl. unrealized; Option 2: end-of-day trailing; Master: fixed at 50,100 once account value reaches 52,600).
- Session: main 06:30-13:00 PT; flat by 15:59 CT = 13:59 PT (59 min after the main-session end); overnight no (evaluation no, funded no, weekend no).
- News: no news rule -> none (F2_firms.json:firms.bulenox.news_windows).
- Pauses: 14:00-15:00 PT Sun-Fri (daily 60-minute break 17:00-18:00 ET; EQUITY-47): outside.
- G: min 0.0988 at 30; power term >= cost term from h = 30. B = 15, 30 (contiguous yes); excluded: 5: G/minG = 1.5139 > 1.10; 60: G/minG = 1.1337 > 1.10; 120: G/minG = 1.3780 > 1.10; 240: G/minG = 2.1374 > 1.10; OC: G/minG = 2.0810 > 1.10. Prior: holds (B = 15, 30 minutes, inside 5 to 240).
- u: S: no sourced spread -> 1 tick (u).

| h | sigma_h | k_RT | k_f | g_be | g_1 | p_be emp | p_be norm | p_1 emp | p_1 norm |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 9.90 | 0.1515 | 0.2359 | 2.336 | 3.336 | 0.667 | 0.648 | 0.738 | 0.711 |
| 2 | 13.98 | 0.1073 | 0.1670 | 2.336 | 3.336 | 0.618 | 0.605 | 0.669 | 0.649 |
| 5 | 21.97 | 0.0683 | 0.1063 | 2.336 | 3.336 | 0.575 | 0.567 | 0.607 | 0.595 |
| 15 | 37.41 | 0.0401 | 0.0624 | 2.336 | 3.336 | 0.544 | 0.539 | 0.563 | 0.556 |
| 30 | 51.75 | 0.0290 | 0.0451 | 2.336 | 3.336 | 0.531 | 0.528 | 0.545 | 0.540 |
| 60 | 70.77 | 0.0212 | 0.0330 | 2.336 | 3.336 | 0.523 | 0.521 | 0.533 | 0.530 |
| 120 | 95.69 | 0.0157 | 0.0244 | 2.336 | 3.336 | 0.517 | 0.515 | 0.524 | 0.522 |
| 240 | 132.46 | 0.0113 | 0.0176 | 2.336 | 3.336 | 0.511 | 0.511 | 0.516 | 0.516 |
| OC | 193.61 | 0.0077 | 0.0121 | 2.336 | 3.336 | 0.507 | 0.508 | 0.511 | 0.511 |
| cc | 237.81 | 0.0063 | 0.0098 | 2.336 | 3.336 | 0.506 | 0.506 | 0.509 | 0.509 |
| on | 142.40 | 0.0105 | 0.0164 | 2.336 | 3.336 | 0.511 | 0.510 | 0.516 | 0.515 |

| h | n_cap/day | trades/yr | e80 disc G3 | e80 disc G3+G4 | e80 test | c_f + e80 test | G | G/minG | DLL/(sigma v) | MLL/(sigma v) | latest start PT | fits flat-by | in B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 20 | 5,040 | 0.45 | 0.51 | 0.43 | 2.76 | 0.2792 | 2.824 | 50.49 | 50.49 | 12:59 | yes | no |
| 2 | 20 | 5,040 | 0.63 | 0.72 | 0.61 | 2.94 | 0.2103 | 2.128 | 35.75 | 35.75 | 12:58 | yes | no |
| 5 | 20 | 5,040 | 0.99 | 1.13 | 0.95 | 3.29 | 0.1496 | 1.514 | 22.76 | 22.76 | 12:55 | yes | no |
| 15 | 20 | 5,040 | 1.69 | 1.93 | 1.62 | 3.96 | 0.1057 | 1.070 | 13.36 | 13.36 | 12:45 | yes | yes |
| 30 | 13 | 3,276 | 2.91 | 3.31 | 2.78 | 5.12 | 0.0988 | 1.000 | 9.66 | 9.66 | 12:30 | yes | yes |
| 60 | 6 | 1,512 | 5.85 | 6.67 | 5.59 | 7.93 | 0.1121 | 1.134 | 7.06 | 7.06 | 12:00 | yes | no |
| 120 | 3 | 756 | 11.19 | 12.75 | 10.70 | 13.03 | 0.1362 | 1.378 | 5.23 | 5.23 | 11:00 | yes | no |
| 240 | 1 | 252 | 26.82 | 30.58 | 25.65 | 27.98 | 0.2113 | 2.137 | 3.77 | 3.77 | 09:00 | yes | no |
| OC | 1 | 252 | 39.20 | 44.70 | 37.49 | 39.82 | 0.2057 | 2.081 | 2.58 | 2.58 | 06:30 | yes | no |
| cc | 1 | 252 | 48.15 | 54.90 | 46.05 | 48.38 | 0.2034 | u | 2.10 | 2.10 | u | u | u |
| on | 1 | 252 | 28.84 | 32.87 | 27.57 | 29.91 | 0.2100 | u | 3.51 | 3.51 | u | u | u |

### 8. mffu|MNQ

- Costs: S 1.00 tick (u) + 0.5 slippage = c_RT 1.50; fee USD 1.90 RT (stated) / v 0.50 = 3.800 ticks; c_f 5.300 ticks (g_be), g_1 6.300 ticks.
- Limits: DLL used USD 1,000 (dll_50k); MLL USD 2,000 (end-of-day trailing (open equity counted at the end of the day); locks once it reaches $100 above the starting balance).
- Session: main 06:30-13:00 PT; flat by 16:10 ET = 13:10 PT (10 min after the main-session end); overnight no (evaluation no, funded no, weekend no).
- News: T1 news (FOMC, minutes, Employment, CPI; EIA for energy traders; agricultural reports for agricultural traders): 2 min before/after, restricted accounts only (Rapid, Pro Sim Funded); Builder 50K unrestricted (page wording conflict noted by FirmRules) -> none on the Builder 50K plan (F2_firms.json:firms.mffu.news_windows).
- Pauses: 14:00-15:00 PT Sun-Fri (daily 60-minute break 17:00-18:00 ET; EQUITY-47): outside.
- G: min 0.0897 at 30; power term >= cost term from h = 30. B = 15, 30 (contiguous yes); excluded: 5: G/minG = 1.4423 > 1.10; 60: G/minG = 1.1724 > 1.10; 120: G/minG = 1.4543 > 1.10; 240: G/minG = 2.3094 > 1.10; OC: G/minG = 2.2604 > 1.10. Prior: holds (B = 15, 30 minutes, inside 5 to 240).
- u: S: no sourced spread -> 1 tick (u).

| h | sigma_h | k_RT | k_f | g_be | g_1 | p_be emp | p_be norm | p_1 emp | p_1 norm |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 27.68 | 0.0542 | 0.1915 | 5.300 | 6.300 | 0.633 | 0.620 | 0.658 | 0.643 |
| 2 | 39.09 | 0.0384 | 0.1356 | 5.300 | 6.300 | 0.595 | 0.585 | 0.613 | 0.601 |
| 5 | 61.54 | 0.0244 | 0.0861 | 5.300 | 6.300 | 0.560 | 0.554 | 0.571 | 0.564 |
| 15 | 105.64 | 0.0142 | 0.0502 | 5.300 | 6.300 | 0.535 | 0.531 | 0.541 | 0.537 |
| 30 | 147.10 | 0.0102 | 0.0360 | 5.300 | 6.300 | 0.525 | 0.523 | 0.529 | 0.527 |
| 60 | 202.67 | 0.0074 | 0.0262 | 5.300 | 6.300 | 0.518 | 0.516 | 0.521 | 0.519 |
| 120 | 283.31 | 0.0053 | 0.0187 | 5.300 | 6.300 | 0.512 | 0.512 | 0.515 | 0.514 |
| 240 | 389.76 | 0.0038 | 0.0136 | 5.300 | 6.300 | 0.509 | 0.509 | 0.510 | 0.510 |
| OC | 576.05 | 0.0026 | 0.0092 | 5.300 | 6.300 | 0.506 | 0.506 | 0.507 | 0.507 |
| cc | 699.90 | 0.0021 | 0.0076 | 5.300 | 6.300 | 0.505 | 0.505 | 0.506 | 0.506 |
| on | 411.21 | 0.0036 | 0.0129 | 5.300 | 6.300 | 0.509 | 0.508 | 0.510 | 0.510 |

| h | n_cap/day | trades/yr | e80 disc G3 | e80 disc G3+G4 | e80 test | c_f + e80 test | G | G/minG | DLL/(sigma v) | MLL/(sigma v) | latest start PT | fits flat-by | in B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 20 | 5,040 | 1.25 | 1.43 | 1.20 | 6.50 | 0.2348 | 2.616 | 72.25 | 144.50 | 12:59 | yes | no |
| 2 | 20 | 5,040 | 1.77 | 2.02 | 1.69 | 6.99 | 0.1789 | 1.994 | 51.17 | 102.34 | 12:58 | yes | no |
| 5 | 20 | 5,040 | 2.79 | 3.18 | 2.66 | 7.96 | 0.1294 | 1.442 | 32.50 | 65.00 | 12:55 | yes | no |
| 15 | 20 | 5,040 | 4.78 | 5.45 | 4.57 | 9.87 | 0.0935 | 1.042 | 18.93 | 37.87 | 12:45 | yes | yes |
| 30 | 13 | 3,276 | 8.26 | 9.42 | 7.90 | 13.20 | 0.0897 | 1.000 | 13.60 | 27.19 | 12:30 | yes | yes |
| 60 | 6 | 1,512 | 16.75 | 19.10 | 16.02 | 21.32 | 0.1052 | 1.172 | 9.87 | 19.74 | 12:00 | yes | no |
| 120 | 3 | 756 | 33.12 | 37.76 | 31.67 | 36.97 | 0.1305 | 1.454 | 7.06 | 14.12 | 11:00 | yes | no |
| 240 | 1 | 252 | 78.92 | 89.98 | 75.47 | 80.77 | 0.2072 | 2.309 | 5.13 | 10.26 | 09:00 | yes | no |
| OC | 1 | 252 | 116.65 | 132.98 | 111.54 | 116.84 | 0.2028 | 2.260 | 3.47 | 6.94 | 06:30 | yes | no |
| cc | 1 | 252 | 141.72 | 161.57 | 135.52 | 140.82 | 0.2012 | u | 2.86 | 5.72 | u | u | u |
| on | 1 | 252 | 83.27 | 94.93 | 79.62 | 84.92 | 0.2065 | u | 4.86 | 9.73 | u | u | u |

### 9. topstep|RTY

- Costs: S 1.00 tick (u) + 0.5 slippage = c_RT 1.50; fee USD 3.78 RT (stated) / v 5.00 = 0.756 ticks; c_f 2.256 ticks (g_be), g_1 3.256 ticks.
- Limits: DLL used USD 2,000 (mll_50k (no daily limit)); MLL USD 2,000 (trailing on end-of-day balance, monitored intraday on realized+unrealized P&L; Combine: locks at the starting balance (50,000); XFA: starts -2,000, locks at 0 once balance reaches 2,000).
- Session: main 06:30-13:00 PT; flat by 15:10 CT = 13:10 PT (10 min after the main-session end); overnight no (evaluation no, funded no, weekend no).
- News: Tier 1 news window: no new opening transactions 5 min before to 5 min after CPI, FOMC decision, FOMC press conference, NFP, PPI -> blocked (full-size) (F2_firms.json:firms.topstep.news_windows).
- Topstep news block (excluded entry minutes; not a band condition, spec 7): no new opens 10:55-11:05 and 11:25-11:35 PT on FOMC decision days (20 main-session minutes a day, about 160 a year on the usual 8-meeting schedule); the CPI/PPI/NFP windows (05:25-05:35 PT, about 3 a month) lie before the main session. Holds may span the windows.
- Pauses: 14:00-15:00 PT Sun-Fri (daily 60-minute break 17:00-18:00 ET; EQUITY-47): outside.
- G: min 0.0973 at 30; power term >= cost term from h = 30. B = 15, 30 (contiguous yes); excluded: 5: G/minG = 1.5005 > 1.10; 60: G/minG = 1.1401 > 1.10; 120: G/minG = 1.3913 > 1.10; 240: G/minG = 2.1651 > 1.10; OC: G/minG = 2.1098 > 1.10. Prior: holds (B = 15, 30 minutes, inside 5 to 240).
- u: S: no sourced spread -> 1 tick (u).

| h | sigma_h | k_RT | k_f | g_be | g_1 | p_be emp | p_be norm | p_1 emp | p_1 norm |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 9.90 | 0.1515 | 0.2278 | 2.256 | 3.256 | 0.661 | 0.643 | 0.732 | 0.706 |
| 2 | 13.98 | 0.1073 | 0.1613 | 2.256 | 3.256 | 0.614 | 0.601 | 0.665 | 0.646 |
| 5 | 21.97 | 0.0683 | 0.1027 | 2.256 | 3.256 | 0.572 | 0.564 | 0.605 | 0.593 |
| 15 | 37.41 | 0.0401 | 0.0603 | 2.256 | 3.256 | 0.542 | 0.538 | 0.561 | 0.555 |
| 30 | 51.75 | 0.0290 | 0.0436 | 2.256 | 3.256 | 0.530 | 0.527 | 0.544 | 0.539 |
| 60 | 70.77 | 0.0212 | 0.0319 | 2.256 | 3.256 | 0.522 | 0.520 | 0.532 | 0.529 |
| 120 | 95.69 | 0.0157 | 0.0236 | 2.256 | 3.256 | 0.516 | 0.515 | 0.523 | 0.521 |
| 240 | 132.46 | 0.0113 | 0.0170 | 2.256 | 3.256 | 0.511 | 0.511 | 0.516 | 0.515 |
| OC | 193.61 | 0.0077 | 0.0117 | 2.256 | 3.256 | 0.507 | 0.507 | 0.510 | 0.511 |
| cc | 237.81 | 0.0063 | 0.0095 | 2.256 | 3.256 | 0.506 | 0.506 | 0.509 | 0.509 |
| on | 142.40 | 0.0105 | 0.0158 | 2.256 | 3.256 | 0.511 | 0.510 | 0.515 | 0.514 |

| h | n_cap/day | trades/yr | e80 disc G3 | e80 disc G3+G4 | e80 test | c_f + e80 test | G | G/minG | DLL/(sigma v) | MLL/(sigma v) | latest start PT | fits flat-by | in B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 20 | 5,040 | 0.45 | 0.51 | 0.43 | 2.68 | 0.2711 | 2.786 | 40.39 | 40.39 | 12:59 | yes | no |
| 2 | 20 | 5,040 | 0.63 | 0.72 | 0.61 | 2.86 | 0.2046 | 2.103 | 28.60 | 28.60 | 12:58 | yes | no |
| 5 | 20 | 5,040 | 0.99 | 1.13 | 0.95 | 3.21 | 0.1460 | 1.500 | 18.21 | 18.21 | 12:55 | yes | no |
| 15 | 20 | 5,040 | 1.69 | 1.93 | 1.62 | 3.88 | 0.1036 | 1.065 | 10.69 | 10.69 | 12:45 | yes | yes |
| 30 | 13 | 3,276 | 2.91 | 3.31 | 2.78 | 5.04 | 0.0973 | 1.000 | 7.73 | 7.73 | 12:30 | yes | yes |
| 60 | 6 | 1,512 | 5.85 | 6.67 | 5.59 | 7.85 | 0.1109 | 1.140 | 5.65 | 5.65 | 12:00 | yes | no |
| 120 | 3 | 756 | 11.19 | 12.75 | 10.70 | 12.95 | 0.1354 | 1.391 | 4.18 | 4.18 | 11:00 | yes | no |
| 240 | 1 | 252 | 26.82 | 30.58 | 25.65 | 27.90 | 0.2107 | 2.165 | 3.02 | 3.02 | 09:00 | yes | no |
| OC | 1 | 252 | 39.20 | 44.70 | 37.49 | 39.74 | 0.2053 | 2.110 | 2.07 | 2.07 | 06:30 | yes | no |
| cc | 1 | 252 | 48.15 | 54.90 | 46.05 | 48.30 | 0.2031 | u | 1.68 | 1.68 | u | u | u |
| on | 1 | 252 | 28.84 | 32.87 | 27.57 | 29.83 | 0.2095 | u | 2.81 | 2.81 | u | u | u |

### 10. tradeify|RTY

- Costs: S 1.00 tick (u) + 0.5 slippage = c_RT 1.50; fee USD 5.76 RT (stated) / v 5.00 = 1.152 ticks; c_f 2.652 ticks (g_be), g_1 3.652 ticks.
- Limits: DLL used USD 1,250 (dll_50k); MLL USD 2,000 (end-of-day trailing, enforced in real time on net liquidation; evaluation: floor 50,100 at EOD 52,100 (per essential rules example); funded: locks at 50,100 at 52,100 EOD or first payout request (E.28)).
- Session: main 06:30-13:00 PT; flat by 16:45 ET = 13:45 PT (45 min after the main-session end); overnight no (evaluation no, funded no, weekend no).
- News: no news rule -> none (F2_firms.json:firms.tradeify.news_windows).
- Pauses: 14:00-15:00 PT Sun-Fri (daily 60-minute break 17:00-18:00 ET; EQUITY-47): outside.
- G: min 0.1049 at 30; power term >= cost term from h = 30. B = 15, 30 (contiguous yes); excluded: 5: G/minG = 1.5629 > 1.10; 60: G/minG = 1.1103 > 1.10; 120: G/minG = 1.3293 > 1.10; 240: G/minG = 2.0358 > 1.10, DLL_f / (sigma_h v) = 1.887 < 2; OC: G/minG = 1.9755 > 1.10, DLL_f / (sigma_h v) = 1.291 < 2. Prior: holds (B = 15, 30 minutes, inside 5 to 240).
- u: S: no sourced spread -> 1 tick (u).

| h | sigma_h | k_RT | k_f | g_be | g_1 | p_be emp | p_be norm | p_1 emp | p_1 norm |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 9.90 | 0.1515 | 0.2678 | 2.652 | 3.652 | 0.689 | 0.668 | 0.761 | 0.731 |
| 2 | 13.98 | 0.1073 | 0.1896 | 2.652 | 3.652 | 0.634 | 0.619 | 0.685 | 0.664 |
| 5 | 21.97 | 0.0683 | 0.1207 | 2.652 | 3.652 | 0.585 | 0.576 | 0.617 | 0.604 |
| 15 | 37.41 | 0.0401 | 0.0709 | 2.652 | 3.652 | 0.550 | 0.544 | 0.569 | 0.561 |
| 30 | 51.75 | 0.0290 | 0.0512 | 2.652 | 3.652 | 0.536 | 0.532 | 0.549 | 0.544 |
| 60 | 70.77 | 0.0212 | 0.0375 | 2.652 | 3.652 | 0.526 | 0.523 | 0.536 | 0.532 |
| 120 | 95.69 | 0.0157 | 0.0277 | 2.652 | 3.652 | 0.519 | 0.517 | 0.526 | 0.524 |
| 240 | 132.46 | 0.0113 | 0.0200 | 2.652 | 3.652 | 0.513 | 0.513 | 0.518 | 0.517 |
| OC | 193.61 | 0.0077 | 0.0137 | 2.652 | 3.652 | 0.508 | 0.509 | 0.512 | 0.512 |
| cc | 237.81 | 0.0063 | 0.0112 | 2.652 | 3.652 | 0.507 | 0.507 | 0.510 | 0.510 |
| on | 142.40 | 0.0105 | 0.0186 | 2.652 | 3.652 | 0.513 | 0.512 | 0.517 | 0.516 |

| h | n_cap/day | trades/yr | e80 disc G3 | e80 disc G3+G4 | e80 test | c_f + e80 test | G | G/minG | DLL/(sigma v) | MLL/(sigma v) | latest start PT | fits flat-by | in B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 20 | 5,040 | 0.45 | 0.51 | 0.43 | 3.08 | 0.3111 | 2.964 | 25.24 | 40.39 | 12:59 | yes | no |
| 2 | 20 | 5,040 | 0.63 | 0.72 | 0.61 | 3.26 | 0.2329 | 2.220 | 17.88 | 28.60 | 12:58 | yes | no |
| 5 | 20 | 5,040 | 0.99 | 1.13 | 0.95 | 3.60 | 0.1640 | 1.563 | 11.38 | 18.21 | 12:55 | yes | no |
| 15 | 20 | 5,040 | 1.69 | 1.93 | 1.62 | 4.27 | 0.1142 | 1.088 | 6.68 | 10.69 | 12:45 | yes | yes |
| 30 | 13 | 3,276 | 2.91 | 3.31 | 2.78 | 5.43 | 0.1049 | 1.000 | 4.83 | 7.73 | 12:30 | yes | yes |
| 60 | 6 | 1,512 | 5.85 | 6.67 | 5.59 | 8.25 | 0.1165 | 1.110 | 3.53 | 5.65 | 12:00 | yes | no |
| 120 | 3 | 756 | 11.19 | 12.75 | 10.70 | 13.35 | 0.1395 | 1.329 | 2.61 | 4.18 | 11:00 | yes | no |
| 240 | 1 | 252 | 26.82 | 30.58 | 25.65 | 28.30 | 0.2136 | 2.036 | 1.89 | 3.02 | 09:00 | yes | no |
| OC | 1 | 252 | 39.20 | 44.70 | 37.49 | 40.14 | 0.2073 | 1.975 | 1.29 | 2.07 | 06:30 | yes | no |
| cc | 1 | 252 | 48.15 | 54.90 | 46.05 | 48.70 | 0.2048 | u | 1.05 | 1.68 | u | u | u |
| on | 1 | 252 | 28.84 | 32.87 | 27.57 | 30.22 | 0.2122 | u | 1.76 | 2.81 | u | u | u |

### 11. lucid|YM

- Costs: S 1.00 tick (u) + 0.5 slippage = c_RT 1.50; fee USD 5.76 RT (RR-05 (u)) / v 5.00 = 1.152 ticks; c_f 2.652 ticks (g_be), g_1 3.652 ticks.
- Limits: DLL used USD 1,200 (dll_50k); MLL USD 2,000 (end-of-day trailing (evaluation and funded); 50,100 once the account exceeds 52,100).
- Session: main 06:30-13:00 PT; flat by 16:45 ET = 13:45 PT (45 min after the main-session end); overnight no (evaluation no, funded no, weekend no).
- News: LucidPro: no news window; red-folder rule applies to the Daily plan only -> none (F2_firms.json:firms.lucid.news_windows).
- Pauses: 14:00-15:00 PT Sun-Fri (daily 60-minute break 17:00-18:00 ET; EQUITY-47): outside.
- G: min 0.0956 at 30; power term >= cost term from h = 30. B = 15, 30 (contiguous yes); excluded: 5: G/minG = 1.4974 > 1.10; 60: G/minG = 1.1396 > 1.10; 120: G/minG = 1.3944 > 1.10, DLL_f / (sigma_h v) = 1.952 < 2; 240: G/minG = 2.1913 > 1.10, DLL_f / (sigma_h v) = 1.444 < 2; OC: G/minG = 2.1470 > 1.10, DLL_f / (sigma_h v) = 1.060 < 2. Prior: holds (B = 15, 30 minutes, inside 5 to 240).
- u: S: no sourced spread -> 1 tick (u); fee: RR-05 (u).

| h | sigma_h | k_RT | k_f | g_be | g_1 | p_be emp | p_be norm | p_1 emp | p_1 norm |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 12.04 | 0.1246 | 0.2203 | 2.652 | 3.652 | 0.657 | 0.638 | 0.716 | 0.690 |
| 2 | 16.95 | 0.0885 | 0.1564 | 2.652 | 3.652 | 0.612 | 0.598 | 0.654 | 0.635 |
| 5 | 26.54 | 0.0565 | 0.0999 | 2.652 | 3.652 | 0.571 | 0.563 | 0.598 | 0.586 |
| 15 | 45.24 | 0.0332 | 0.0586 | 2.652 | 3.652 | 0.541 | 0.537 | 0.557 | 0.551 |
| 30 | 63.23 | 0.0237 | 0.0419 | 2.652 | 3.652 | 0.529 | 0.526 | 0.540 | 0.536 |
| 60 | 88.56 | 0.0169 | 0.0299 | 2.652 | 3.652 | 0.521 | 0.519 | 0.528 | 0.526 |
| 120 | 122.94 | 0.0122 | 0.0216 | 2.652 | 3.652 | 0.514 | 0.514 | 0.520 | 0.519 |
| 240 | 166.20 | 0.0090 | 0.0160 | 2.652 | 3.652 | 0.510 | 0.510 | 0.514 | 0.514 |
| OC | 226.31 | 0.0066 | 0.0117 | 2.652 | 3.652 | 0.508 | 0.507 | 0.510 | 0.510 |
| cc | 275.49 | 0.0054 | 0.0096 | 2.652 | 3.652 | 0.506 | 0.506 | 0.509 | 0.508 |
| on | 154.57 | 0.0097 | 0.0172 | 2.652 | 3.652 | 0.512 | 0.511 | 0.516 | 0.515 |

| h | n_cap/day | trades/yr | e80 disc G3 | e80 disc G3+G4 | e80 test | c_f + e80 test | G | G/minG | DLL/(sigma v) | MLL/(sigma v) | latest start PT | fits flat-by | in B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 20 | 5,040 | 0.55 | 0.62 | 0.52 | 3.17 | 0.2636 | 2.756 | 19.94 | 33.23 | 12:59 | yes | no |
| 2 | 20 | 5,040 | 0.77 | 0.88 | 0.73 | 3.39 | 0.1997 | 2.088 | 14.16 | 23.59 | 12:58 | yes | no |
| 5 | 20 | 5,040 | 1.20 | 1.37 | 1.15 | 3.80 | 0.1432 | 1.497 | 9.04 | 15.07 | 12:55 | yes | no |
| 15 | 20 | 5,040 | 2.05 | 2.34 | 1.96 | 4.61 | 0.1019 | 1.066 | 5.30 | 8.84 | 12:45 | yes | yes |
| 30 | 13 | 3,276 | 3.55 | 4.05 | 3.40 | 6.05 | 0.0956 | 1.000 | 3.80 | 6.33 | 12:30 | yes | yes |
| 60 | 6 | 1,512 | 7.32 | 8.35 | 7.00 | 9.65 | 0.1090 | 1.140 | 2.71 | 4.52 | 12:00 | yes | no |
| 120 | 3 | 756 | 14.37 | 16.39 | 13.74 | 16.40 | 0.1334 | 1.394 | 1.95 | 3.25 | 11:00 | yes | no |
| 240 | 1 | 252 | 33.65 | 38.37 | 32.18 | 34.83 | 0.2096 | 2.191 | 1.44 | 2.41 | 09:00 | yes | no |
| OC | 1 | 252 | 45.83 | 52.24 | 43.82 | 46.47 | 0.2053 | 2.147 | 1.06 | 1.77 | 06:30 | yes | no |
| cc | 1 | 252 | 55.78 | 63.60 | 53.34 | 55.99 | 0.2033 | u | 0.87 | 1.45 | u | u | u |
| on | 1 | 252 | 31.30 | 35.68 | 29.93 | 32.58 | 0.2108 | u | 1.55 | 2.59 | u | u | u |

### 12. lucid|MNQ

- Costs: S 1.00 tick (u) + 0.5 slippage = c_RT 1.50; fee USD 1.90 RT (RR-05 (u)) / v 0.50 = 3.800 ticks; c_f 5.300 ticks (g_be), g_1 6.300 ticks.
- Limits: DLL used USD 1,200 (dll_50k); MLL USD 2,000 (end-of-day trailing (evaluation and funded); 50,100 once the account exceeds 52,100).
- Session: main 06:30-13:00 PT; flat by 16:45 ET = 13:45 PT (45 min after the main-session end); overnight no (evaluation no, funded no, weekend no).
- News: LucidPro: no news window; red-folder rule applies to the Daily plan only -> none (F2_firms.json:firms.lucid.news_windows).
- Pauses: 14:00-15:00 PT Sun-Fri (daily 60-minute break 17:00-18:00 ET; EQUITY-47): outside.
- G: min 0.0897 at 30; power term >= cost term from h = 30. B = 15, 30 (contiguous yes); excluded: 5: G/minG = 1.4423 > 1.10; 60: G/minG = 1.1724 > 1.10; 120: G/minG = 1.4543 > 1.10; 240: G/minG = 2.3094 > 1.10; OC: G/minG = 2.2604 > 1.10. Prior: holds (B = 15, 30 minutes, inside 5 to 240).
- u: S: no sourced spread -> 1 tick (u); fee: RR-05 (u).

| h | sigma_h | k_RT | k_f | g_be | g_1 | p_be emp | p_be norm | p_1 emp | p_1 norm |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 27.68 | 0.0542 | 0.1915 | 5.300 | 6.300 | 0.633 | 0.620 | 0.658 | 0.643 |
| 2 | 39.09 | 0.0384 | 0.1356 | 5.300 | 6.300 | 0.595 | 0.585 | 0.613 | 0.601 |
| 5 | 61.54 | 0.0244 | 0.0861 | 5.300 | 6.300 | 0.560 | 0.554 | 0.571 | 0.564 |
| 15 | 105.64 | 0.0142 | 0.0502 | 5.300 | 6.300 | 0.535 | 0.531 | 0.541 | 0.537 |
| 30 | 147.10 | 0.0102 | 0.0360 | 5.300 | 6.300 | 0.525 | 0.523 | 0.529 | 0.527 |
| 60 | 202.67 | 0.0074 | 0.0262 | 5.300 | 6.300 | 0.518 | 0.516 | 0.521 | 0.519 |
| 120 | 283.31 | 0.0053 | 0.0187 | 5.300 | 6.300 | 0.512 | 0.512 | 0.515 | 0.514 |
| 240 | 389.76 | 0.0038 | 0.0136 | 5.300 | 6.300 | 0.509 | 0.509 | 0.510 | 0.510 |
| OC | 576.05 | 0.0026 | 0.0092 | 5.300 | 6.300 | 0.506 | 0.506 | 0.507 | 0.507 |
| cc | 699.90 | 0.0021 | 0.0076 | 5.300 | 6.300 | 0.505 | 0.505 | 0.506 | 0.506 |
| on | 411.21 | 0.0036 | 0.0129 | 5.300 | 6.300 | 0.509 | 0.508 | 0.510 | 0.510 |

| h | n_cap/day | trades/yr | e80 disc G3 | e80 disc G3+G4 | e80 test | c_f + e80 test | G | G/minG | DLL/(sigma v) | MLL/(sigma v) | latest start PT | fits flat-by | in B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 20 | 5,040 | 1.25 | 1.43 | 1.20 | 6.50 | 0.2348 | 2.616 | 86.70 | 144.50 | 12:59 | yes | no |
| 2 | 20 | 5,040 | 1.77 | 2.02 | 1.69 | 6.99 | 0.1789 | 1.994 | 61.40 | 102.34 | 12:58 | yes | no |
| 5 | 20 | 5,040 | 2.79 | 3.18 | 2.66 | 7.96 | 0.1294 | 1.442 | 39.00 | 65.00 | 12:55 | yes | no |
| 15 | 20 | 5,040 | 4.78 | 5.45 | 4.57 | 9.87 | 0.0935 | 1.042 | 22.72 | 37.87 | 12:45 | yes | yes |
| 30 | 13 | 3,276 | 8.26 | 9.42 | 7.90 | 13.20 | 0.0897 | 1.000 | 16.31 | 27.19 | 12:30 | yes | yes |
| 60 | 6 | 1,512 | 16.75 | 19.10 | 16.02 | 21.32 | 0.1052 | 1.172 | 11.84 | 19.74 | 12:00 | yes | no |
| 120 | 3 | 756 | 33.12 | 37.76 | 31.67 | 36.97 | 0.1305 | 1.454 | 8.47 | 14.12 | 11:00 | yes | no |
| 240 | 1 | 252 | 78.92 | 89.98 | 75.47 | 80.77 | 0.2072 | 2.309 | 6.16 | 10.26 | 09:00 | yes | no |
| OC | 1 | 252 | 116.65 | 132.98 | 111.54 | 116.84 | 0.2028 | 2.260 | 4.17 | 6.94 | 06:30 | yes | no |
| cc | 1 | 252 | 141.72 | 161.57 | 135.52 | 140.82 | 0.2012 | u | 3.43 | 5.72 | u | u | u |
| on | 1 | 252 | 83.27 | 94.93 | 79.62 | 84.92 | 0.2065 | u | 5.84 | 9.73 | u | u | u |

### 13. mffu|RTY

- Costs: S 1.00 tick (u) + 0.5 slippage = c_RT 1.50; fee USD 4.68 RT (stated) / v 5.00 = 0.936 ticks; c_f 2.436 ticks (g_be), g_1 3.436 ticks.
- Limits: DLL used USD 1,000 (dll_50k); MLL USD 2,000 (end-of-day trailing (open equity counted at the end of the day); locks once it reaches $100 above the starting balance).
- Session: main 06:30-13:00 PT; flat by 16:10 ET = 13:10 PT (10 min after the main-session end); overnight no (evaluation no, funded no, weekend no).
- News: T1 news (FOMC, minutes, Employment, CPI; EIA for energy traders; agricultural reports for agricultural traders): 2 min before/after, restricted accounts only (Rapid, Pro Sim Funded); Builder 50K unrestricted (page wording conflict noted by FirmRules) -> none on the Builder 50K plan (F2_firms.json:firms.mffu.news_windows).
- Pauses: 14:00-15:00 PT Sun-Fri (daily 60-minute break 17:00-18:00 ET; EQUITY-47): outside.
- G: min 0.1008 at 30; power term >= cost term from h = 30. B = 15, 30 (contiguous yes); excluded: 5: G/minG = 1.5300 > 1.10; 60: G/minG = 1.1260 > 1.10; 120: G/minG = 1.3619 > 1.10; 240: G/minG = 2.1039 > 1.10, DLL_f / (sigma_h v) = 1.510 < 2; OC: G/minG = 2.0462 > 1.10, DLL_f / (sigma_h v) = 1.033 < 2. Prior: holds (B = 15, 30 minutes, inside 5 to 240).
- u: S: no sourced spread -> 1 tick (u).

| h | sigma_h | k_RT | k_f | g_be | g_1 | p_be emp | p_be norm | p_1 emp | p_1 norm |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 9.90 | 0.1515 | 0.2460 | 2.436 | 3.436 | 0.674 | 0.654 | 0.745 | 0.717 |
| 2 | 13.98 | 0.1073 | 0.1742 | 2.436 | 3.436 | 0.623 | 0.609 | 0.674 | 0.654 |
| 5 | 21.97 | 0.0683 | 0.1109 | 2.436 | 3.436 | 0.578 | 0.569 | 0.610 | 0.598 |
| 15 | 37.41 | 0.0401 | 0.0651 | 2.436 | 3.436 | 0.546 | 0.541 | 0.565 | 0.558 |
| 30 | 51.75 | 0.0290 | 0.0471 | 2.436 | 3.436 | 0.533 | 0.529 | 0.546 | 0.542 |
| 60 | 70.77 | 0.0212 | 0.0344 | 2.436 | 3.436 | 0.524 | 0.522 | 0.533 | 0.530 |
| 120 | 95.69 | 0.0157 | 0.0255 | 2.436 | 3.436 | 0.517 | 0.516 | 0.524 | 0.522 |
| 240 | 132.46 | 0.0113 | 0.0184 | 2.436 | 3.436 | 0.512 | 0.512 | 0.517 | 0.516 |
| OC | 193.61 | 0.0077 | 0.0126 | 2.436 | 3.436 | 0.508 | 0.508 | 0.511 | 0.511 |
| cc | 237.81 | 0.0063 | 0.0102 | 2.436 | 3.436 | 0.506 | 0.506 | 0.509 | 0.509 |
| on | 142.40 | 0.0105 | 0.0171 | 2.436 | 3.436 | 0.512 | 0.511 | 0.516 | 0.515 |

| h | n_cap/day | trades/yr | e80 disc G3 | e80 disc G3+G4 | e80 test | c_f + e80 test | G | G/minG | DLL/(sigma v) | MLL/(sigma v) | latest start PT | fits flat-by | in B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 20 | 5,040 | 0.45 | 0.51 | 0.43 | 2.86 | 0.2893 | 2.870 | 20.19 | 40.39 | 12:59 | yes | no |
| 2 | 20 | 5,040 | 0.63 | 0.72 | 0.61 | 3.04 | 0.2175 | 2.158 | 14.30 | 28.60 | 12:58 | yes | no |
| 5 | 20 | 5,040 | 0.99 | 1.13 | 0.95 | 3.39 | 0.1542 | 1.530 | 9.10 | 18.21 | 12:55 | yes | no |
| 15 | 20 | 5,040 | 1.69 | 1.93 | 1.62 | 4.06 | 0.1084 | 1.076 | 5.35 | 10.69 | 12:45 | yes | yes |
| 30 | 13 | 3,276 | 2.91 | 3.31 | 2.78 | 5.22 | 0.1008 | 1.000 | 3.86 | 7.73 | 12:30 | yes | yes |
| 60 | 6 | 1,512 | 5.85 | 6.67 | 5.59 | 8.03 | 0.1135 | 1.126 | 2.83 | 5.65 | 12:00 | yes | no |
| 120 | 3 | 756 | 11.19 | 12.75 | 10.70 | 13.13 | 0.1372 | 1.362 | 2.09 | 4.18 | 11:00 | yes | no |
| 240 | 1 | 252 | 26.82 | 30.58 | 25.65 | 28.08 | 0.2120 | 2.104 | 1.51 | 3.02 | 09:00 | yes | no |
| OC | 1 | 252 | 39.20 | 44.70 | 37.49 | 39.92 | 0.2062 | 2.046 | 1.03 | 2.07 | 06:30 | yes | no |
| cc | 1 | 252 | 48.15 | 54.90 | 46.05 | 48.48 | 0.2039 | u | 0.84 | 1.68 | u | u | u |
| on | 1 | 252 | 28.84 | 32.87 | 27.57 | 30.01 | 0.2107 | u | 1.40 | 2.81 | u | u | u |

### 14. mffu|MYM

- Costs: S 1.00 tick (u) + 0.5 slippage = c_RT 1.50; fee USD 1.90 RT (stated) / v 0.50 = 3.800 ticks; c_f 5.300 ticks (g_be), g_1 6.300 ticks.
- Limits: DLL used USD 1,000 (dll_50k); MLL USD 2,000 (end-of-day trailing (open equity counted at the end of the day); locks once it reaches $100 above the starting balance).
- Session: main 06:30-13:00 PT; flat by 16:10 ET = 13:10 PT (10 min after the main-session end); overnight no (evaluation no, funded no, weekend no).
- News: T1 news (FOMC, minutes, Employment, CPI; EIA for energy traders; agricultural reports for agricultural traders): 2 min before/after, restricted accounts only (Rapid, Pro Sim Funded); Builder 50K unrestricted (page wording conflict noted by FirmRules) -> none on the Builder 50K plan (F2_firms.json:firms.mffu.news_windows).
- Pauses: 14:00-15:00 PT Sun-Fri (daily 60-minute break 17:00-18:00 ET; EQUITY-47): outside.
- G: min 0.1375 at 30; power term >= cost term from h = 60. B = 30, 60 (contiguous yes); excluded: 5: G/minG = 1.7669 > 1.10; 15: G/minG = 1.1667 > 1.10; 120: G/minG = 1.1264 > 1.10; 240: G/minG = 1.6399 > 1.10; OC: G/minG = 1.5783 > 1.10. Prior: holds (B = 30, 60 minutes, inside 5 to 240).
- u: S: no sourced spread -> 1 tick (u).

| h | sigma_h | k_RT | k_f | g_be | g_1 | p_be emp | p_be norm | p_1 emp | p_1 norm |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 12.04 | 0.1246 | 0.4403 | 5.300 | 6.300 | 0.814 | 0.776 | 0.873 | 0.828 |
| 2 | 16.95 | 0.0885 | 0.3126 | 5.300 | 6.300 | 0.723 | 0.696 | 0.765 | 0.733 |
| 5 | 26.54 | 0.0565 | 0.1997 | 5.300 | 6.300 | 0.642 | 0.625 | 0.669 | 0.649 |
| 15 | 45.24 | 0.0332 | 0.1171 | 5.300 | 6.300 | 0.583 | 0.573 | 0.598 | 0.587 |
| 30 | 63.23 | 0.0237 | 0.0838 | 5.300 | 6.300 | 0.558 | 0.553 | 0.569 | 0.562 |
| 60 | 88.56 | 0.0169 | 0.0598 | 5.300 | 6.300 | 0.541 | 0.537 | 0.549 | 0.545 |
| 120 | 122.94 | 0.0122 | 0.0431 | 5.300 | 6.300 | 0.529 | 0.527 | 0.534 | 0.532 |
| 240 | 166.20 | 0.0090 | 0.0319 | 5.300 | 6.300 | 0.521 | 0.520 | 0.525 | 0.524 |
| OC | 226.31 | 0.0066 | 0.0234 | 5.300 | 6.300 | 0.515 | 0.515 | 0.518 | 0.517 |
| cc | 275.49 | 0.0054 | 0.0192 | 5.300 | 6.300 | 0.512 | 0.512 | 0.515 | 0.514 |
| on | 154.57 | 0.0097 | 0.0343 | 5.300 | 6.300 | 0.523 | 0.521 | 0.528 | 0.526 |

| h | n_cap/day | trades/yr | e80 disc G3 | e80 disc G3+G4 | e80 test | c_f + e80 test | G | G/minG | DLL/(sigma v) | MLL/(sigma v) | latest start PT | fits flat-by | in B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 20 | 5,040 | 0.55 | 0.62 | 0.52 | 5.82 | 0.4836 | 3.516 | 166.14 | 332.28 | 12:59 | yes | no |
| 2 | 20 | 5,040 | 0.77 | 0.88 | 0.73 | 6.03 | 0.3559 | 2.588 | 117.97 | 235.94 | 12:58 | yes | no |
| 5 | 20 | 5,040 | 1.20 | 1.37 | 1.15 | 6.45 | 0.2430 | 1.767 | 75.35 | 150.70 | 12:55 | yes | no |
| 15 | 20 | 5,040 | 2.05 | 2.34 | 1.96 | 7.26 | 0.1604 | 1.167 | 44.20 | 88.41 | 12:45 | yes | no |
| 30 | 13 | 3,276 | 3.55 | 4.05 | 3.40 | 8.70 | 0.1375 | 1.000 | 31.63 | 63.26 | 12:30 | yes | yes |
| 60 | 6 | 1,512 | 7.32 | 8.35 | 7.00 | 12.30 | 0.1389 | 1.010 | 22.58 | 45.17 | 12:00 | yes | yes |
| 120 | 3 | 756 | 14.37 | 16.39 | 13.74 | 19.04 | 0.1549 | 1.126 | 16.27 | 32.54 | 11:00 | yes | no |
| 240 | 1 | 252 | 33.65 | 38.37 | 32.18 | 37.48 | 0.2255 | 1.640 | 12.03 | 24.07 | 09:00 | yes | no |
| OC | 1 | 252 | 45.83 | 52.24 | 43.82 | 49.12 | 0.2170 | 1.578 | 8.84 | 17.67 | 06:30 | yes | no |
| cc | 1 | 252 | 55.78 | 63.60 | 53.34 | 58.64 | 0.2129 | u | 7.26 | 14.52 | u | u | u |
| on | 1 | 252 | 31.30 | 35.68 | 29.93 | 35.23 | 0.2279 | u | 12.94 | 25.88 | u | u | u |

### 15. topstep|ZL

- Costs: S 1.00 tick (u) + 0.5 slippage = c_RT 1.50; fee USD 5.28 RT (stated) / v 6.00 = 0.880 ticks; c_f 2.380 ticks (g_be), g_1 3.380 ticks.
- Limits: DLL used USD 2,000 (mll_50k (no daily limit)); MLL USD 2,000 (trailing on end-of-day balance, monitored intraday on realized+unrealized P&L; Combine: locks at the starting balance (50,000); XFA: starts -2,000, locks at 0 once balance reaches 2,000).
- Session: main 06:30-11:20 PT; flat by 15:10 CT = 13:10 PT (110 min after the main-session end); overnight no (evaluation no, funded no, weekend no).
- News: no window names this product at this firm.
- Topstep news window: product not named (grains): no entry minute excluded.
- Pauses: 05:45-06:30 PT Mon-Fri (pause 07:45-08:30 CT between the overnight and day segments; no orders accepted; GRAINS-14): adjacent; 11:20-17:00 PT Mon-Fri (day session closes 13:20 CT; Globex reopens 19:00 CT; GRAINS-14): adjacent.
- G: min 0.1492 at 30; power term >= cost term from h = 60. B = 15, 30, 60 (contiguous yes); excluded: 5: G/minG = 1.6135 > 1.10; 120: G/minG = 1.2194 > 1.10; 240: G/minG = 1.5026 > 1.10; OC: G/minG = 1.4735 > 1.10. Prior: holds (B = 15, 30, 60 minutes, inside 5 to 240).
- u: S: no sourced spread -> 1 tick (u).

| h | sigma_h | k_RT | k_f | g_be | g_1 | p_be emp | p_be norm | p_1 emp | p_1 norm |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 5.52 | 0.2719 | 0.4314 | 2.380 | 3.380 | 0.804 | 0.770 | 0.932 | 0.884 |
| 2 | 7.72 | 0.1943 | 0.3083 | 2.380 | 3.380 | 0.715 | 0.693 | 0.805 | 0.774 |
| 5 | 12.05 | 0.1245 | 0.1975 | 2.380 | 3.380 | 0.636 | 0.624 | 0.693 | 0.676 |
| 15 | 20.37 | 0.0736 | 0.1168 | 2.380 | 3.380 | 0.579 | 0.573 | 0.613 | 0.604 |
| 30 | 28.10 | 0.0534 | 0.0847 | 2.380 | 3.380 | 0.557 | 0.553 | 0.581 | 0.575 |
| 60 | 38.21 | 0.0393 | 0.0623 | 2.380 | 3.380 | 0.542 | 0.539 | 0.559 | 0.555 |
| 120 | 52.82 | 0.0284 | 0.0451 | 2.380 | 3.380 | 0.529 | 0.528 | 0.542 | 0.540 |
| 240 | 77.74 | 0.0193 | 0.0306 | 2.380 | 3.380 | 0.520 | 0.519 | 0.528 | 0.527 |
| OC | 90.58 | 0.0166 | 0.0263 | 2.380 | 3.380 | 0.516 | 0.516 | 0.523 | 0.523 |
| cc | 116.84 | 0.0128 | 0.0204 | 2.380 | 3.380 | 0.513 | 0.513 | 0.518 | 0.518 |
| on | 70.12 | 0.0214 | 0.0339 | 2.380 | 3.380 | 0.523 | 0.521 | 0.532 | 0.530 |

| h | n_cap/day | trades/yr | e80 disc G3 | e80 disc G3+G4 | e80 test | c_f + e80 test | G | G/minG | DLL/(sigma v) | MLL/(sigma v) | latest start PT | fits flat-by | in B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 20 | 5,040 | 0.25 | 0.28 | 0.24 | 2.62 | 0.4747 | 3.181 | 60.42 | 60.42 | 11:19 | yes | no |
| 2 | 20 | 5,040 | 0.35 | 0.40 | 0.33 | 2.71 | 0.3516 | 2.356 | 43.18 | 43.18 | 11:18 | yes | no |
| 5 | 20 | 5,040 | 0.55 | 0.62 | 0.52 | 2.90 | 0.2408 | 1.614 | 27.66 | 27.66 | 11:15 | yes | no |
| 15 | 19 | 4,788 | 0.95 | 1.08 | 0.90 | 3.28 | 0.1613 | 1.081 | 16.36 | 16.36 | 11:05 | yes | yes |
| 30 | 9 | 2,268 | 1.90 | 2.16 | 1.81 | 4.19 | 0.1492 | 1.000 | 11.86 | 11.86 | 10:50 | yes | yes |
| 60 | 4 | 1,008 | 3.87 | 4.41 | 3.70 | 6.08 | 0.1591 | 1.066 | 8.72 | 8.72 | 10:20 | yes | yes |
| 120 | 2 | 504 | 7.56 | 8.62 | 7.23 | 9.61 | 0.1820 | 1.219 | 6.31 | 6.31 | 09:20 | yes | no |
| 240 | 1 | 252 | 15.74 | 17.95 | 15.05 | 17.43 | 0.2242 | 1.503 | 4.29 | 4.29 | 07:20 | yes | no |
| OC | 1 | 252 | 18.34 | 20.91 | 17.54 | 19.92 | 0.2199 | 1.474 | 3.68 | 3.68 | 06:30 | yes | no |
| cc | 1 | 252 | 23.66 | 26.97 | 22.62 | 25.00 | 0.2140 | u | 2.85 | 2.85 | u | u | u |
| on | 1 | 252 | 14.20 | 16.19 | 13.58 | 15.96 | 0.2276 | u | 4.75 | 4.75 | u | u | u |

## 3. Overnight holds and the own-broker venue

### 3.1 Overnight holds beside the intraday rows

No prop firm in the top 15 allows an overnight hold in evaluation or funded, nor a weekend hold (F2_firms.md; F5
`overnight`). At ibkr overnight holds are allowed, carry the overnight initial margin and, on Tiered pricing only, an
overnight position fee of USD 0.10 a contract a night when the account just meets margin (0.05 at 2x, 0 at 3x).

| row | overnight allowed | min G | at | G OC | G cc | G on | DLL/(sigma v) OC | DLL/(sigma v) cc | DLL/(sigma v) on |
|---|---|---|---|---|---|---|---|---|---|
| bulenox|YM | no | 0.0906 | 30 | 0.2039 | 0.2021 | 0.2087 | 2.21 | 1.81 | 3.23 |
| topstep|MNQ | no | 0.0805 | 30 | 0.2005 | 0.1993 | 0.2032 | 6.94 | 5.72 | 9.73 |
| tradeify|MNQ | no | 0.0886 | 30 | 0.2025 | 0.2010 | 0.2061 | 4.34 | 3.57 | 6.08 |
| tradeify|YM | no | 0.0956 | 30 | 0.2053 | 0.2033 | 0.2108 | 1.10 | 0.91 | 1.62 |
| topstep|YM | no | 0.0894 | 30 | 0.2036 | 0.2018 | 0.2082 | 1.77 | 1.45 | 2.59 |
| mffu|YM | no | 0.0956 | 30 | 0.2053 | 0.2033 | 0.2108 | 0.88 | 0.73 | 1.29 |
| bulenox|RTY | no | 0.0988 | 30 | 0.2057 | 0.2034 | 0.2100 | 2.58 | 2.10 | 3.51 |
| mffu|MNQ | no | 0.0897 | 30 | 0.2028 | 0.2012 | 0.2065 | 3.47 | 2.86 | 4.86 |
| topstep|RTY | no | 0.0973 | 30 | 0.2053 | 0.2031 | 0.2095 | 2.07 | 1.68 | 2.81 |
| tradeify|RTY | no | 0.1049 | 30 | 0.2073 | 0.2048 | 0.2122 | 1.29 | 1.05 | 1.76 |
| lucid|YM | no | 0.0956 | 30 | 0.2053 | 0.2033 | 0.2108 | 1.06 | 0.87 | 1.55 |
| lucid|MNQ | no | 0.0897 | 30 | 0.2028 | 0.2012 | 0.2065 | 4.17 | 3.43 | 5.84 |
| mffu|RTY | no | 0.1008 | 30 | 0.2062 | 0.2039 | 0.2107 | 1.03 | 0.84 | 1.40 |
| mffu|MYM | no | 0.1375 | 30 | 0.2170 | 0.2129 | 0.2279 | 8.84 | 7.26 | 12.94 |
| topstep|ZL | no | 0.1492 | 30 | 0.2199 | 0.2140 | 0.2276 | 3.68 | 2.85 | 4.75 |
| ibkr|YM | yes | 0.0916 | 30 | 0.2042 | 0.2023 | 0.2091 | n/a | n/a | n/a |
| ibkr|MNQ | yes | 0.0968 | 30 | 0.2046 | 0.2027 | 0.2091 | n/a | n/a | n/a |
| ibkr|RTY | yes | 0.1000 | 30 | 0.2060 | 0.2037 | 0.2105 | n/a | n/a | n/a |
| ibkr|MYM | yes | 0.1506 | 60 | 0.2216 | 0.2166 | 0.2346 | n/a | n/a | n/a |
| ibkr|ZL | yes | 0.1536 | 30 | 0.2213 | 0.2150 | 0.2293 | n/a | n/a | n/a |

Facts: in every top-15 pair and in the five ibkr rows, G at OC, cc and on is 0.20-0.23, 1.95-2.52 x the intraday
min G (1.40-1.66 x for MYM and ZL). The overnight rows' G is almost all power term (SR80_test / sqrt(1) = 0.194): one
trade a day cannot reach 80% power at the test unless the gross edge is 0.19-0.21 sigma a trade. At the prop firms
the DLL is below 2 x sigma_cc v on 8 of the 15 pairs (every YM and RTY pair except bulenox|RTY).

### 3.2 Own broker: all 35 codes (LR-F5-IBKR, LR-Q6d)

Venue: IBKR own account, British Columbia resident (Interactive Brokers Canada Inc.); no DLL, MLL or flat-by-close;
capital ceiling USD 6,000 (u: none recorded in docs/DECISIONS.md). Fee = 2 x (IBKR execution USD 0.85 + clearing 0 +
exchange fee + regulatory fee) a round trip. ">" marks a margin above the ceiling or a sigma_day above 2% of it
(USD 120).

| row | c_f | fee ticks | min G at | B | prior | IM intraday USD | IM overnight USD | sigma_day USD (cc) | sigma_OC USD |
|---|---|---|---|---|---|---|---|---|---|
| ibkr|6A | 2.48 | 0.98 | 60 | 30, 60, 120 | holds | 2,478 | 2,478 | 503 > | 292 |
| ibkr|6E | 2.29 | 0.79 | 60 | 30, 60, 120 | holds | 3,493 | 3,493 | 683 > | 425 |
| ibkr|BTC | 2.23 | 0.73 | 60 | 30, 60 | holds | 140,153 > | 140,153 > | 4,108 > | 2,626 |
| ibkr|CL | 1.97 | 0.47 | 30 | 30, 60 | holds | 23,442 > | 23,442 > | 1,710 > | 1,209 |
| ibkr|GC | 2.00 | 0.50 | 30 | 30, 60 | holds | 36,064 > | 36,064 > | 1,688 > | 1,116 |
| ibkr|HG | 1.90 | 0.40 | 60 | 30, 60, 120 | holds | 24,772 > | 24,772 > | 1,305 > | 705 |
| ibkr|M2K | 6.34 | 4.84 | 60 | 30, 60, 120 | holds | 876 | 1,252 | 119 | 97 |
| ibkr|M6A | 3.70 | 2.20 | cc | empty | fails | 248 | 248 | 50 | 29 |
| ibkr|M6E | 3.26 | 1.76 | cc | empty | fails | 349 | 349 | 68 | 42 |
| ibkr|MBT | 9.54 | 8.04 | cc | empty | fails | 2,803 | 2,803 | 82 | 53 |
| ibkr|MCL | 4.42 | 2.92 | 60 | 30, 60, 120 | holds | 2,351 | 2,351 | 171 > | 120 |
| ibkr|MGC | 4.62 | 3.12 | 60 | 30, 60, 120 | holds | 3,606 | 3,606 | 169 > | 112 |
| ibkr|MHG | 4.00 | 2.50 | cc | 60, 120 | fails (min G overnight) | 2,485 | 2,485 | 133 > | 70 |
| ibkr|MNG | 4.62 | 3.12 | 60 | 60, 120 | holds | 553 | 553 | 176 > | 106 |
| ibkr|MNQ | 6.34 | 4.84 | 30 | 15, 30 | holds | 4,623 | 6,604 > | 350 > | 288 |
| ibkr|MYM | 6.34 | 4.84 | 60 | 30, 60, 120 | holds | 1,270 | 1,814 | 138 > | 113 |
| ibkr|MZC | 2.59 | 1.09 | cc | empty | fails | 197 | 197 | 45 | 35 |
| ibkr|MZL | 3.77 | 2.27 | cc | 120, OC | fails (min G overnight) | 479 | 479 | 70 | 54 |
| ibkr|MZM | 2.86 | 1.36 | cc | OC | fails (min G overnight) | 301 | 301 | 68 | 52 |
| ibkr|MZS | 2.59 | 1.09 | cc | OC | fails (min G overnight) | 416 | 416 | 86 | 64 |
| ibkr|MZW | 2.59 | 1.09 | cc | empty | fails | 287 | 287 | 75 | 52 |
| ibkr|NG | 1.99 | 0.49 | 30 | 30, 60 | holds | 5,532 | 5,532 | 1,759 > | 1,056 |
| ibkr|RTY | 2.40 | 0.90 | 30 | 15, 30 | holds | 8,761 > | 12,515 > | 1,189 > | 968 |
| ibkr|XC | 4.57 | 3.07 | cc | 120, OC | fails (min G overnight) | 381 | 381 | 90 | 70 |
| ibkr|XK | 4.57 | 3.07 | 60 | 30, 60, 120 | holds | 832 | 832 | 172 > | 128 |
| ibkr|YM | 2.40 | 0.90 | 30 | 15, 30 | holds | 12,700 > | 18,143 > | 1,377 > | 1,132 |
| ibkr|ZB | 1.61 | 0.11 | cc | 120 | fails (min G overnight) | 4,284 | 4,284 | 1,077 > | 706 |
| ibkr|ZC | 1.98 | 0.48 | cc | 60, 120, OC | fails (min G overnight) | 1,905 | 1,905 | 451 > | 349 |
| ibkr|ZF | 1.89 | 0.39 | 120 | 60, 120, OC | partly | 1,439 | 1,439 | 394 > | 258 |
| ibkr|ZL | 2.50 | 1.00 | 30 | 15, 30, 60 | holds | 4,662 | 4,662 | 701 > | 543 |
| ibkr|ZM | 2.10 | 0.60 | 60 | 30, 60, 120 | holds | 2,920 | 2,920 | 676 > | 519 |
| ibkr|ZN | 1.71 | 0.21 | cc | empty | fails | 2,161 | 2,161 | 558 > | 362 |
| ibkr|ZS | 1.98 | 0.48 | 60 | 30, 60, 120 | holds | 4,160 | 4,160 | 859 > | 642 |
| ibkr|ZT | 1.89 | 0.39 | cc | 60, 120, OC | fails (min G overnight) | 1,380 | 1,380 | 376 > | 238 |
| ibkr|ZW | 1.98 | 0.48 | 60 | 30, 60, 120 | holds | 2,871 | 2,871 | 746 > | 519 |

Rows that do not hold, with the reason:

| row | B | intraday B | min G at | min G | min intraday G | prior | reason |
|---|---|---|---|---|---|---|---|
| ibkr|M6A | empty | none | cc | 0.2672 | 0.3202 | fails | B is empty; min G lies only at cc |
| ibkr|M6E | empty | none | cc | 0.2533 | 0.2896 | fails | B is empty; min G lies only at cc |
| ibkr|MBT | empty | none | cc | 0.2517 | 0.2845 | fails | B is empty; min G lies only at cc |
| ibkr|MHG | 60, 120 | 60, 120 | cc | 0.2313 | 0.2384 | fails (min G overnight) | min G lies only at cc |
| ibkr|MZC | empty | none | cc | 0.3371 | 0.3788 | fails | B is empty; min G lies only at cc |
| ibkr|MZL | 120, OC | 120 | cc | 0.2581 | 0.2768 | fails (min G overnight) | min G lies only at cc |
| ibkr|MZM | OC | none | cc | 0.2782 | 0.3038 | fails (min G overnight) | min G lies only at cc |
| ibkr|MZS | OC | none | cc | 0.2690 | 0.2944 | fails (min G overnight) | min G lies only at cc |
| ibkr|MZW | empty | none | cc | 0.2803 | 0.3183 | fails | B is empty; min G lies only at cc |
| ibkr|XC | 120, OC | 120 | cc | 0.2570 | 0.2714 | fails (min G overnight) | min G lies only at cc |
| ibkr|ZB | 120 | 120 | cc | 0.2404 | 0.2620 | fails (min G overnight) | min G lies only at cc |
| ibkr|ZC | 60, 120, OC | 60, 120 | cc | 0.2485 | 0.2535 | fails (min G overnight) | min G lies only at cc |
| ibkr|ZF | 60, 120, OC | 60, 120 | 120 | 0.2309 | 0.2309 | partly | B contains OC besides intraday holds |
| ibkr|ZN | empty | none | cc | 0.2415 | 0.2676 | fails | B is empty; min G lies only at cc |
| ibkr|ZT | 60, 120, OC | 60, 120 | cc | 0.2329 | 0.2374 | fails (min G overnight) | min G lies only at cc |

In 8 of the 14 "fails" rows B is non-empty (MHG, MZL, XC, ZB, ZC, ZT with intraday members; MZM and MZS with OC
only) and the verdict fails only because the
minimum G lies at cc; the cc G is 2-9% below the lowest intraday G there (columns "min G" and "min intraday G").
Spec 7's rule is literal (a minimum of G only at OC or overnight fails), so these rows are reported as "fails (min G
overnight)" with their intraday band beside (column "intraday B").

### 3.3 The five top-15 codes at ibkr (full detail)

### ibkr|YM

- Costs: fee USD 2.24 a side, F_rt USD 4.48 (published) = 0.896 ticks; c_RT 1.50 (S u); c_f 2.396 ticks.
- Margin (initial): intraday USD 12,699.91, overnight USD 18,142.73 (maintenance USD 15,345.97); ceiling USD 6,000 (u): intraday exceeds yes, overnight exceeds yes.
- sigma_day (sigma_cc 275.49 ticks x v) USD 1,377 against 2% of the ceiling (USD 120): exceeds yes; sigma_OC USD 1,132.
- Overnight: allowed; overnight position fee (Tiered only) USD/contract/night {"meets margin requirements": 0.1, "2x margin": 0.05, "3x margin": 0.0}.
- G: min 0.0916 at 30; power term >= cost term from h = 30. B = 15, 30; excluded: 5: G/minG = 1.4583 > 1.10; 60: G/minG = 1.1584 > 1.10; 120: G/minG = 1.4333 > 1.10; 240: G/minG = 2.2714 > 1.10; OC: G/minG = 2.2296 > 1.10. Prior: holds (B = 15, 30 minutes, inside 5 to 240).
- u: S: no sourced spread -> 1 tick (u); capital ceiling: none recorded -> USD 6,000 (u).

| h | sigma_h | k_RT | k_f | g_be | g_1 | p_be emp | p_be norm | p_1 emp | p_1 norm |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 12.04 | 0.1246 | 0.1990 | 2.396 | 3.396 | 0.642 | 0.625 | 0.701 | 0.677 |
| 2 | 16.95 | 0.0885 | 0.1413 | 2.396 | 3.396 | 0.601 | 0.589 | 0.643 | 0.626 |
| 5 | 26.54 | 0.0565 | 0.0903 | 2.396 | 3.396 | 0.564 | 0.557 | 0.591 | 0.580 |
| 15 | 45.24 | 0.0332 | 0.0530 | 2.396 | 3.396 | 0.537 | 0.533 | 0.553 | 0.547 |
| 30 | 63.23 | 0.0237 | 0.0379 | 2.396 | 3.396 | 0.526 | 0.524 | 0.537 | 0.534 |
| 60 | 88.56 | 0.0169 | 0.0271 | 2.396 | 3.396 | 0.519 | 0.517 | 0.526 | 0.524 |
| 120 | 122.94 | 0.0122 | 0.0195 | 2.396 | 3.396 | 0.513 | 0.512 | 0.519 | 0.517 |
| 240 | 166.20 | 0.0090 | 0.0144 | 2.396 | 3.396 | 0.509 | 0.509 | 0.513 | 0.513 |
| OC | 226.31 | 0.0066 | 0.0106 | 2.396 | 3.396 | 0.507 | 0.507 | 0.510 | 0.509 |
| cc | 275.49 | 0.0054 | 0.0087 | 2.396 | 3.396 | 0.506 | 0.505 | 0.508 | 0.508 |
| on | 154.57 | 0.0097 | 0.0155 | 2.396 | 3.396 | 0.511 | 0.510 | 0.515 | 0.514 |

| h | n_cap/day | trades/yr | e80 disc G3 | e80 disc G3+G4 | e80 test | c_f + e80 test | G | G/minG | latest start PT | in B | overnight IM USD |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 20 | 5,040 | 0.55 | 0.62 | 0.52 | 2.92 | 0.2423 | 2.646 | 12:59 | no |  |
| 2 | 20 | 5,040 | 0.77 | 0.88 | 0.73 | 3.13 | 0.1846 | 2.016 | 12:58 | no |  |
| 5 | 20 | 5,040 | 1.20 | 1.37 | 1.15 | 3.55 | 0.1336 | 1.458 | 12:55 | no |  |
| 15 | 20 | 5,040 | 2.05 | 2.34 | 1.96 | 4.35 | 0.0963 | 1.051 | 12:45 | yes |  |
| 30 | 13 | 3,276 | 3.55 | 4.05 | 3.40 | 5.79 | 0.0916 | 1.000 | 12:30 | yes |  |
| 60 | 6 | 1,512 | 7.32 | 8.35 | 7.00 | 9.40 | 0.1061 | 1.158 | 12:00 | no |  |
| 120 | 3 | 756 | 14.37 | 16.39 | 13.74 | 16.14 | 0.1313 | 1.433 | 11:00 | no |  |
| 240 | 1 | 252 | 33.65 | 38.37 | 32.18 | 34.58 | 0.2080 | 2.271 | 09:00 | no |  |
| OC | 1 | 252 | 45.83 | 52.24 | 43.82 | 46.22 | 0.2042 | 2.230 | 06:30 | no |  |
| cc | 1 | 252 | 55.78 | 63.60 | 53.34 | 55.74 | 0.2023 | u | u | u | 18,143 |
| on | 1 | 252 | 31.30 | 35.68 | 29.93 | 32.32 | 0.2091 | u | u | u | 18,143 |

### ibkr|MNQ

- Costs: fee USD 1.21 a side, F_rt USD 2.42 (published) = 4.844 ticks; c_RT 1.50 (S u); c_f 6.344 ticks.
- Margin (initial): intraday USD 4,622.90, overnight USD 6,604.14 (maintenance USD 4,233.24); ceiling USD 6,000 (u): intraday exceeds no, overnight exceeds yes.
- sigma_day (sigma_cc 699.90 ticks x v) USD 350 against 2% of the ceiling (USD 120): exceeds yes; sigma_OC USD 288.
- Overnight: allowed; overnight position fee (Tiered only) USD/contract/night {"meets margin requirements": 0.1, "2x margin": 0.05, "3x margin": 0.0}.
- G: min 0.0968 at 30; power term >= cost term from h = 30. B = 15, 30; excluded: 5: G/minG = 1.5118 > 1.10; 60: G/minG = 1.1396 > 1.10; 120: G/minG = 1.3858 > 1.10; 240: G/minG = 2.1678 > 1.10; OC: G/minG = 2.1134 > 1.10. Prior: holds (B = 15, 30 minutes, inside 5 to 240).
- u: S: no sourced spread -> 1 tick (u); capital ceiling: none recorded -> USD 6,000 (u).

| h | sigma_h | k_RT | k_f | g_be | g_1 | p_be emp | p_be norm | p_1 emp | p_1 norm |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 27.68 | 0.0542 | 0.2292 | 6.344 | 7.344 | 0.659 | 0.644 | 0.684 | 0.666 |
| 2 | 39.09 | 0.0384 | 0.1623 | 6.344 | 7.344 | 0.613 | 0.602 | 0.631 | 0.618 |
| 5 | 61.54 | 0.0244 | 0.1031 | 6.344 | 7.344 | 0.572 | 0.565 | 0.583 | 0.575 |
| 15 | 105.64 | 0.0142 | 0.0601 | 6.344 | 7.344 | 0.541 | 0.538 | 0.548 | 0.544 |
| 30 | 147.10 | 0.0102 | 0.0431 | 6.344 | 7.344 | 0.529 | 0.527 | 0.534 | 0.531 |
| 60 | 202.67 | 0.0074 | 0.0313 | 6.344 | 7.344 | 0.521 | 0.520 | 0.524 | 0.523 |
| 120 | 283.31 | 0.0053 | 0.0224 | 6.344 | 7.344 | 0.515 | 0.514 | 0.517 | 0.516 |
| 240 | 389.76 | 0.0038 | 0.0163 | 6.344 | 7.344 | 0.510 | 0.510 | 0.512 | 0.512 |
| OC | 576.05 | 0.0026 | 0.0110 | 6.344 | 7.344 | 0.507 | 0.507 | 0.508 | 0.508 |
| cc | 699.90 | 0.0021 | 0.0091 | 6.344 | 7.344 | 0.506 | 0.506 | 0.507 | 0.507 |
| on | 411.21 | 0.0036 | 0.0154 | 6.344 | 7.344 | 0.510 | 0.510 | 0.512 | 0.511 |

| h | n_cap/day | trades/yr | e80 disc G3 | e80 disc G3+G4 | e80 test | c_f + e80 test | G | G/minG | latest start PT | in B | overnight IM USD |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 20 | 5,040 | 1.25 | 1.43 | 1.20 | 7.54 | 0.2725 | 2.814 | 12:59 | no |  |
| 2 | 20 | 5,040 | 1.77 | 2.02 | 1.69 | 8.04 | 0.2056 | 2.123 | 12:58 | no |  |
| 5 | 20 | 5,040 | 2.79 | 3.18 | 2.66 | 9.01 | 0.1464 | 1.512 | 12:55 | no |  |
| 15 | 20 | 5,040 | 4.78 | 5.45 | 4.57 | 10.92 | 0.1033 | 1.067 | 12:45 | yes |  |
| 30 | 13 | 3,276 | 8.26 | 9.42 | 7.90 | 14.24 | 0.0968 | 1.000 | 12:30 | yes |  |
| 60 | 6 | 1,512 | 16.75 | 19.10 | 16.02 | 22.36 | 0.1103 | 1.140 | 12:00 | no |  |
| 120 | 3 | 756 | 33.12 | 37.76 | 31.67 | 38.02 | 0.1342 | 1.386 | 11:00 | no |  |
| 240 | 1 | 252 | 78.92 | 89.98 | 75.47 | 81.81 | 0.2099 | 2.168 | 09:00 | no |  |
| OC | 1 | 252 | 116.65 | 132.98 | 111.54 | 117.88 | 0.2046 | 2.113 | 06:30 | no |  |
| cc | 1 | 252 | 141.72 | 161.57 | 135.52 | 141.86 | 0.2027 | u | u | u | 6,604 |
| on | 1 | 252 | 83.27 | 94.93 | 79.62 | 85.97 | 0.2091 | u | u | u | 6,604 |

### ibkr|RTY

- Costs: fee USD 2.24 a side, F_rt USD 4.48 (published) = 0.896 ticks; c_RT 1.50 (S u); c_f 2.396 ticks.
- Margin (initial): intraday USD 8,760.56, overnight USD 12,515.08 (maintenance USD 10,882.68); ceiling USD 6,000 (u): intraday exceeds yes, overnight exceeds yes.
- sigma_day (sigma_cc 237.81 ticks x v) USD 1,189 against 2% of the ceiling (USD 120): exceeds yes; sigma_OC USD 968.
- Overnight: allowed; overnight position fee (Tiered only) USD/contract/night {"meets margin requirements": 0.1, "2x margin": 0.05, "3x margin": 0.0}.
- G: min 0.1000 at 30; power term >= cost term from h = 30. B = 15, 30; excluded: 5: G/minG = 1.5237 > 1.10; 60: G/minG = 1.1290 > 1.10; 120: G/minG = 1.3682 > 1.10; 240: G/minG = 2.1170 > 1.10; OC: G/minG = 2.0599 > 1.10. Prior: holds (B = 15, 30 minutes, inside 5 to 240).
- u: S: no sourced spread -> 1 tick (u); capital ceiling: none recorded -> USD 6,000 (u).

| h | sigma_h | k_RT | k_f | g_be | g_1 | p_be emp | p_be norm | p_1 emp | p_1 norm |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 9.90 | 0.1515 | 0.2420 | 2.396 | 3.396 | 0.671 | 0.652 | 0.742 | 0.715 |
| 2 | 13.98 | 0.1073 | 0.1714 | 2.396 | 3.396 | 0.621 | 0.607 | 0.672 | 0.652 |
| 5 | 21.97 | 0.0683 | 0.1091 | 2.396 | 3.396 | 0.577 | 0.568 | 0.609 | 0.597 |
| 15 | 37.41 | 0.0401 | 0.0641 | 2.396 | 3.396 | 0.545 | 0.540 | 0.564 | 0.557 |
| 30 | 51.75 | 0.0290 | 0.0463 | 2.396 | 3.396 | 0.532 | 0.529 | 0.546 | 0.541 |
| 60 | 70.77 | 0.0212 | 0.0339 | 2.396 | 3.396 | 0.523 | 0.521 | 0.533 | 0.530 |
| 120 | 95.69 | 0.0157 | 0.0250 | 2.396 | 3.396 | 0.517 | 0.516 | 0.524 | 0.522 |
| 240 | 132.46 | 0.0113 | 0.0181 | 2.396 | 3.396 | 0.512 | 0.511 | 0.517 | 0.516 |
| OC | 193.61 | 0.0077 | 0.0124 | 2.396 | 3.396 | 0.508 | 0.508 | 0.511 | 0.511 |
| cc | 237.81 | 0.0063 | 0.0101 | 2.396 | 3.396 | 0.506 | 0.506 | 0.509 | 0.509 |
| on | 142.40 | 0.0105 | 0.0168 | 2.396 | 3.396 | 0.511 | 0.511 | 0.516 | 0.515 |

| h | n_cap/day | trades/yr | e80 disc G3 | e80 disc G3+G4 | e80 test | c_f + e80 test | G | G/minG | latest start PT | in B | overnight IM USD |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 20 | 5,040 | 0.45 | 0.51 | 0.43 | 2.83 | 0.2853 | 2.852 | 12:59 | no |  |
| 2 | 20 | 5,040 | 0.63 | 0.72 | 0.61 | 3.00 | 0.2147 | 2.146 | 12:58 | no |  |
| 5 | 20 | 5,040 | 0.99 | 1.13 | 0.95 | 3.35 | 0.1524 | 1.524 | 12:55 | no |  |
| 15 | 20 | 5,040 | 1.69 | 1.93 | 1.62 | 4.02 | 0.1073 | 1.073 | 12:45 | yes |  |
| 30 | 13 | 3,276 | 2.91 | 3.31 | 2.78 | 5.18 | 0.1000 | 1.000 | 12:30 | yes |  |
| 60 | 6 | 1,512 | 5.85 | 6.67 | 5.59 | 7.99 | 0.1129 | 1.129 | 12:00 | no |  |
| 120 | 3 | 756 | 11.19 | 12.75 | 10.70 | 13.09 | 0.1368 | 1.368 | 11:00 | no |  |
| 240 | 1 | 252 | 26.82 | 30.58 | 25.65 | 28.04 | 0.2117 | 2.117 | 09:00 | no |  |
| OC | 1 | 252 | 39.20 | 44.70 | 37.49 | 39.88 | 0.2060 | 2.060 | 06:30 | no |  |
| cc | 1 | 252 | 48.15 | 54.90 | 46.05 | 48.44 | 0.2037 | u | u | u | 12,515 |
| on | 1 | 252 | 28.84 | 32.87 | 27.57 | 29.97 | 0.2105 | u | u | u | 12,515 |

### ibkr|MYM

- Costs: fee USD 1.21 a side, F_rt USD 2.42 (published) = 4.840 ticks; c_RT 1.50 (S u); c_f 6.340 ticks.
- Margin (initial): intraday USD 1,269.99, overnight USD 1,814.27 (maintenance USD 1,534.60); ceiling USD 6,000 (u): intraday exceeds no, overnight exceeds no.
- sigma_day (sigma_cc 275.49 ticks x v) USD 138 against 2% of the ceiling (USD 120): exceeds yes; sigma_OC USD 113.
- Overnight: allowed; overnight position fee (Tiered only) USD/contract/night {"meets margin requirements": 0.1, "2x margin": 0.05, "3x margin": 0.0}.
- G: min 0.1506 at 60; power term >= cost term from h = 60. B = 30, 60, 120; excluded: 5: G/minG = 1.8732 > 1.10; 15: G/minG = 1.2177 > 1.10; 240: G/minG = 1.5386 > 1.10; OC: G/minG = 1.4714 > 1.10. Prior: holds (B = 30, 60, 120 minutes, inside 5 to 240).
- u: S: no sourced spread -> 1 tick (u); capital ceiling: none recorded -> USD 6,000 (u).

| h | sigma_h | k_RT | k_f | g_be | g_1 | p_be emp | p_be norm | p_1 emp | p_1 norm |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 12.04 | 0.1246 | 0.5267 | 6.340 | 7.340 | 0.875 | 0.830 | 0.934 | 0.882 |
| 2 | 16.95 | 0.0885 | 0.3740 | 6.340 | 7.340 | 0.767 | 0.734 | 0.809 | 0.771 |
| 5 | 26.54 | 0.0565 | 0.2389 | 6.340 | 7.340 | 0.670 | 0.650 | 0.697 | 0.673 |
| 15 | 45.24 | 0.0332 | 0.1401 | 6.340 | 7.340 | 0.599 | 0.588 | 0.614 | 0.602 |
| 30 | 63.23 | 0.0237 | 0.1003 | 6.340 | 7.340 | 0.570 | 0.563 | 0.581 | 0.573 |
| 60 | 88.56 | 0.0169 | 0.0716 | 6.340 | 7.340 | 0.549 | 0.545 | 0.557 | 0.552 |
| 120 | 122.94 | 0.0122 | 0.0516 | 6.340 | 7.340 | 0.535 | 0.532 | 0.540 | 0.537 |
| 240 | 166.20 | 0.0090 | 0.0381 | 6.340 | 7.340 | 0.525 | 0.524 | 0.529 | 0.528 |
| OC | 226.31 | 0.0066 | 0.0280 | 6.340 | 7.340 | 0.518 | 0.518 | 0.521 | 0.520 |
| cc | 275.49 | 0.0054 | 0.0230 | 6.340 | 7.340 | 0.515 | 0.514 | 0.517 | 0.517 |
| on | 154.57 | 0.0097 | 0.0410 | 6.340 | 7.340 | 0.528 | 0.526 | 0.532 | 0.530 |

| h | n_cap/day | trades/yr | e80 disc G3 | e80 disc G3+G4 | e80 test | c_f + e80 test | G | G/minG | latest start PT | in B | overnight IM USD |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 20 | 5,040 | 0.55 | 0.62 | 0.52 | 6.86 | 0.5700 | 3.784 | 12:59 | no |  |
| 2 | 20 | 5,040 | 0.77 | 0.88 | 0.73 | 7.07 | 0.4173 | 2.770 | 12:58 | no |  |
| 5 | 20 | 5,040 | 1.20 | 1.37 | 1.15 | 7.49 | 0.2822 | 1.873 | 12:55 | no |  |
| 15 | 20 | 5,040 | 2.05 | 2.34 | 1.96 | 8.30 | 0.1834 | 1.218 | 12:45 | no |  |
| 30 | 13 | 3,276 | 3.55 | 4.05 | 3.40 | 9.74 | 0.1540 | 1.022 | 12:30 | yes |  |
| 60 | 6 | 1,512 | 7.32 | 8.35 | 7.00 | 13.34 | 0.1506 | 1.000 | 12:00 | yes |  |
| 120 | 3 | 756 | 14.37 | 16.39 | 13.74 | 20.08 | 0.1634 | 1.084 | 11:00 | yes |  |
| 240 | 1 | 252 | 33.65 | 38.37 | 32.18 | 38.52 | 0.2318 | 1.539 | 09:00 | no |  |
| OC | 1 | 252 | 45.83 | 52.24 | 43.82 | 50.16 | 0.2216 | 1.471 | 06:30 | no |  |
| cc | 1 | 252 | 55.78 | 63.60 | 53.34 | 59.68 | 0.2166 | u | u | u | 1,814 |
| on | 1 | 252 | 31.30 | 35.68 | 29.93 | 36.27 | 0.2346 | u | u | u | 1,814 |

### ibkr|ZL

- Costs: fee USD 3.01 a side, F_rt USD 6.02 (published) = 1.003 ticks; c_RT 1.50 (S u); c_f 2.503 ticks.
- Margin (initial): intraday USD 4,661.63, overnight USD 4,661.63 (maintenance USD 4,053.59); ceiling USD 6,000 (u): intraday exceeds no, overnight exceeds no.
- sigma_day (sigma_cc 116.84 ticks x v) USD 701 against 2% of the ceiling (USD 120): exceeds yes; sigma_OC USD 543.
- Overnight: allowed; overnight position fee (Tiered only) USD/contract/night {"meets margin requirements": 0.1, "2x margin": 0.05, "3x margin": 0.0}.
- G: min 0.1536 at 30; power term >= cost term from h = 60. B = 15, 30, 60; excluded: 5: G/minG = 1.6341 > 1.10; 120: G/minG = 1.1997 > 1.10; 240: G/minG = 1.4700 > 1.10; OC: G/minG = 1.4403 > 1.10. Prior: holds (B = 15, 30, 60 minutes, inside 5 to 240).
- u: S: no sourced spread -> 1 tick (u); capital ceiling: none recorded -> USD 6,000 (u).

| h | sigma_h | k_RT | k_f | g_be | g_1 | p_be emp | p_be norm | p_1 emp | p_1 norm |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 5.52 | 0.2719 | 0.4538 | 2.503 | 3.503 | 0.820 | 0.784 | 0.948 | 0.898 |
| 2 | 7.72 | 0.1943 | 0.3243 | 2.503 | 3.503 | 0.726 | 0.703 | 0.816 | 0.784 |
| 5 | 12.05 | 0.1245 | 0.2077 | 2.503 | 3.503 | 0.643 | 0.630 | 0.700 | 0.682 |
| 15 | 20.37 | 0.0736 | 0.1229 | 2.503 | 3.503 | 0.583 | 0.577 | 0.617 | 0.608 |
| 30 | 28.10 | 0.0534 | 0.0891 | 2.503 | 3.503 | 0.560 | 0.556 | 0.584 | 0.578 |
| 60 | 38.21 | 0.0393 | 0.0655 | 2.503 | 3.503 | 0.544 | 0.541 | 0.561 | 0.557 |
| 120 | 52.82 | 0.0284 | 0.0474 | 2.503 | 3.503 | 0.531 | 0.530 | 0.543 | 0.542 |
| 240 | 77.74 | 0.0193 | 0.0322 | 2.503 | 3.503 | 0.521 | 0.520 | 0.529 | 0.528 |
| OC | 90.58 | 0.0166 | 0.0276 | 2.503 | 3.503 | 0.517 | 0.517 | 0.524 | 0.524 |
| cc | 116.84 | 0.0128 | 0.0214 | 2.503 | 3.503 | 0.513 | 0.513 | 0.519 | 0.519 |
| on | 70.12 | 0.0214 | 0.0357 | 2.503 | 3.503 | 0.524 | 0.522 | 0.533 | 0.531 |

| h | n_cap/day | trades/yr | e80 disc G3 | e80 disc G3+G4 | e80 test | c_f + e80 test | G | G/minG | latest start PT | in B | overnight IM USD |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 20 | 5,040 | 0.25 | 0.28 | 0.24 | 2.74 | 0.4970 | 3.236 | 11:19 | no |  |
| 2 | 20 | 5,040 | 0.35 | 0.40 | 0.33 | 2.84 | 0.3676 | 2.393 | 11:18 | no |  |
| 5 | 20 | 5,040 | 0.55 | 0.62 | 0.52 | 3.03 | 0.2510 | 1.634 | 11:15 | no |  |
| 15 | 19 | 4,788 | 0.95 | 1.08 | 0.90 | 3.41 | 0.1673 | 1.089 | 11:05 | yes |  |
| 30 | 9 | 2,268 | 1.90 | 2.16 | 1.81 | 4.32 | 0.1536 | 1.000 | 10:50 | yes |  |
| 60 | 4 | 1,008 | 3.87 | 4.41 | 3.70 | 6.20 | 0.1623 | 1.057 | 10:20 | yes |  |
| 120 | 2 | 504 | 7.56 | 8.62 | 7.23 | 9.74 | 0.1843 | 1.200 | 09:20 | no |  |
| 240 | 1 | 252 | 15.74 | 17.95 | 15.05 | 17.56 | 0.2258 | 1.470 | 07:20 | no |  |
| OC | 1 | 252 | 18.34 | 20.91 | 17.54 | 20.04 | 0.2213 | 1.440 | 06:30 | no |  |
| cc | 1 | 252 | 23.66 | 26.97 | 22.62 | 25.13 | 0.2150 | u | u | u | 4,662 |
| on | 1 | 252 | 14.20 | 16.19 | 13.58 | 16.08 | 0.2293 | u | u | u | 4,662 |

Venue comparison (the same code at the prop firms and at ibkr):

| code | venue row | c_f | min G at | min G | B | prior |
|---|---|---|---|---|---|---|
| YM | bulenox|YM | 2.336 | 30 | 0.0906 | 15, 30 | holds |
| YM | tradeify|YM | 2.652 | 30 | 0.0956 | 15, 30 | holds |
| YM | topstep|YM | 2.256 | 30 | 0.0894 | 15, 30 | holds |
| YM | mffu|YM | 2.652 | 30 | 0.0956 | 15, 30 | holds |
| YM | lucid|YM | 2.652 | 30 | 0.0956 | 15, 30 | holds |
| YM | ibkr|YM | 2.396 | 30 | 0.0916 | 15, 30 | holds |
| MNQ | topstep|MNQ | 3.940 | 30 | 0.0805 | 15, 30 | holds |
| MNQ | tradeify|MNQ | 5.140 | 30 | 0.0886 | 15, 30 | holds |
| MNQ | mffu|MNQ | 5.300 | 30 | 0.0897 | 15, 30 | holds |
| MNQ | lucid|MNQ | 5.300 | 30 | 0.0897 | 15, 30 | holds |
| MNQ | ibkr|MNQ | 6.344 | 30 | 0.0968 | 15, 30 | holds |
| RTY | bulenox|RTY | 2.336 | 30 | 0.0988 | 15, 30 | holds |
| RTY | topstep|RTY | 2.256 | 30 | 0.0973 | 15, 30 | holds |
| RTY | tradeify|RTY | 2.652 | 30 | 0.1049 | 15, 30 | holds |
| RTY | mffu|RTY | 2.436 | 30 | 0.1008 | 15, 30 | holds |
| RTY | ibkr|RTY | 2.396 | 30 | 0.1000 | 15, 30 | holds |
| MYM | mffu|MYM | 5.300 | 30 | 0.1375 | 30, 60 | holds |
| MYM | ibkr|MYM | 6.340 | 60 | 0.1506 | 30, 60, 120 | holds |
| ZL | topstep|ZL | 2.380 | 30 | 0.1492 | 15, 30, 60 | holds |
| ZL | ibkr|ZL | 2.503 | 30 | 0.1536 | 15, 30, 60 | holds |

Facts: ibkr's round trip in ticks is close to the prop firms' for YM and RTY (2.40 against 2.26-2.65), above them for
MNQ and MYM (6.34 against 3.94-5.30: the micro's exchange and regulatory fees are a large share of a USD 0.50 tick)
and for ZL (2.50 against 2.38). B is unchanged for YM, MNQ, RTY and ZL; MYM's widens to 120 at ibkr because its min G
moves to 60. All five codes exceed the LR-Q6d sigma_day test (sigma_cc x v above USD 120); YM and RTY's intraday
margins (USD 12,700 and 8,761) and MNQ's overnight margin (6,604) exceed the USD 6,000 (u) ceiling; MYM (1,270 /
1,814) and ZL (4,662) do not.

## 4. Economics by horizon (E_dir, econ32b.json)

E_dir60 is in econ32b.json for every top-15 pair (pass 1). E_dir 30/120/240 for the top 15 (pass 2, --edir-pairs from
work/econ/edir_top15.json) were still running when this draft was written (expected to end about 10:30-11:00 PDT).
Each cell: mu*_mkt (smallest grid gross edge per trade with EV >= 0, market case) / mu10K_mkt (smallest with
P(USD 10,000 within 250 days) >= 0.5) / m* / m10K (both in sigma_60 units), ticks; "(>cap)" = no grid point
qualifies. T = min(20, floor(L_main / h)) trades a day, sigma_T = sigma_h; cap = max(4, ceil(0.30 sigma_60)) for every
curve of a pair. Cost there is c_mkt = F_rt / v + S (no 0.5 slippage, unlike F5's c_f).

**PLACEHOLDER: the lead fills the E_dir30, E_dir120 and E_dir240 columns from econ32b.json after the pass-2 run
(rerun build_scope.py; it reads `pairs.<pair>.E_dir.<h>` when present).**

| pair | T at 30/60/120/240 | E_dir60: mu*_mkt / mu10K_mkt / m* / m10K / cap (ticks) | E_dir30 | E_dir120 | E_dir240 |
|---|---|---|---|---|---|
| bulenox|YM | 13/6/3/1 | 8.55 / 18.47 / 0.097 / 0.209 / 27 | 5.71 / 10.89 / 0.064 / 0.123 | 14.30 / u (>cap) / 0.161 / u | 18.13 / u (>cap) / 0.205 / u |
| topstep|MNQ | 13/6/3/1 | 7.34 / 29.35 / 0.036 / 0.145 / 61 | 5.06 / 15.82 / 0.025 / 0.078 | 11.29 / 54.95 / 0.056 / 0.271 | 29.60 / u (>cap) / 0.146 / u |
| tradeify|MNQ | 13/6/3/1 | 3.74 / 29.97 / 0.018 / 0.148 / 61 | 4.16 / 16.21 / 0.021 / 0.080 | 2.86 / 55.49 / 0.014 / 0.274 | 0.97 / u (>cap) / 0.005 / u |
| tradeify|YM | 13/6/3/1 | 1.89 / 8.58 / 0.021 / 0.097 / 27 | 2.07 / 5.31 / 0.023 / 0.060 | 1.65 / 14.67 / 0.019 / 0.166 | 0.00 / u (>cap) / 0.000 / u |
| topstep|YM | 13/6/3/1 | 0.00 / 5.66 / 0.000 / 0.064 / 27 | 0.59 / 3.60 / 0.007 / 0.041 | 0.00 / 9.55 / 0.000 / 0.108 | 0.00 / 23.78 / 0.000 / 0.269 |
| mffu|YM | 13/6/3/1 | 2.63 / 9.77 / 0.030 / 0.110 / 27 | 2.40 / 5.88 / 0.027 / 0.066 | 3.08 / 17.07 / 0.035 / 0.193 | 3.53 / u (>cap) / 0.040 / u |
| bulenox|RTY | 13/6/3/1 | 4.86 / 12.15 / 0.069 / 0.172 / 22 | 3.59 / 7.17 / 0.051 / 0.101 | 7.25 / 21.38 / 0.102 / 0.302 | 12.78 / u (>cap) / 0.181 / u |
| mffu|MNQ | 13/6/3/1 | 5.41 / 43.68 / 0.027 / 0.216 / 61 | 5.10 / 22.57 / 0.025 / 0.111 | 5.97 / u (>cap) / 0.029 / u | 7.34 / u (>cap) / 0.036 / u |
| topstep|RTY | 13/6/3/1 | 0.00 / 5.49 / 0.000 / 0.078 / 22 | 0.78 / 3.51 / 0.011 / 0.050 | 0.00 / 9.11 / 0.000 / 0.129 | 0.00 / u (>cap) / 0.000 / u |
| tradeify|RTY | 13/6/3/1 | 1.82 / 7.06 / 0.026 / 0.100 / 22 | 2.00 / 4.61 / 0.028 / 0.065 | 1.41 / 11.51 / 0.020 / 0.163 | 0.00 / u (>cap) / 0.000 / u |
| lucid|YM | 13/6/3/1 | 1.96 / 8.37 / 0.022 / 0.095 / 27 | 2.12 / 5.19 / 0.024 / 0.059 | 1.73 / 14.29 / 0.020 / 0.161 | 0.63 / u (>cap) / 0.007 / u |
| lucid|MNQ | 13/6/3/1 | 4.57 / 35.45 / 0.023 / 0.175 / 61 | 4.71 / 18.86 / 0.023 / 0.093 | 4.32 / u (>cap) / 0.021 / u | 4.13 / u (>cap) / 0.020 / u |
| mffu|RTY | 13/6/3/1 | 2.20 / 7.97 / 0.031 / 0.113 / 22 | 2.09 / 4.93 / 0.030 / 0.070 | 2.40 / 13.54 / 0.034 / 0.191 | 2.88 / u (>cap) / 0.041 / u |
| mffu|MYM | 13/6/3/1 | 5.13 / u (>cap) / 0.058 / u / 27 | 4.95 / 26.01 / 0.056 / 0.294 | 5.49 / u (>cap) / 0.062 / u | 7.94 / u (>cap) / 0.090 / u |
| topstep|ZL | 9/4/2/1 | 1.42 / 6.08 / 0.037 / 0.159 / 12 | 1.57 / 3.80 / 0.041 / 0.099 | 1.06 / 10.21 / 0.028 / 0.267 | 0.00 / u (>cap) / 0.000 / u |

Facts already in hand: E_dir60's mu*_mkt is 0.00 for topstep|YM and topstep|RTY (EV >= 0 at zero gross edge on the
grid) and mffu|MYM's mu10K_mkt is above its 27-tick cap. The zero is a model property, not an edge: under E_dir60's
parameters (T = min(20, floor(L_main/60)) round trips a day at sigma_60) the modelled campaign breaks even with no
edge per trade; this reflects the firm's fee and payout structure in E.28's model at that volatility, not evidence of
an edge; E.29's payout-reachability facts apply. **Flagged for the reviewer.**

Cost basis, stated once: F5's c_f includes the 0.5-tick slippage allowance (spec 7), while the economics' c_mkt does
not (spec 4 keeps E.28's model).

## 5. E.33's cost and trade-count facts (cited from reports/E.33c_RETURN.md sections 1 and 7; no outcome read)

- The search ran on 796 out-of-fold ZM dates (2020-12-30 to 2024-02-29) at 5 to 60 minutes; N went from 538 to 838.
- 61 of the 300 configurations traded often enough to pass its trade-count gate (G1).
- "The minimum edges this search could detect were roughly 1.5 to 4.4 ticks a trade at the trade rates seen" (section
  7). F5's e80 for ZM at the 20-entry cap is 0.30-2.17 ticks at the test and 0.35-2.59 at discovery G3 + G4 for 5-60
  minutes (section 1.5). The two are consistent in direction: E.33's configurations traded fewer times a day than the
  cap, so their detectable edge was larger. F5's e80 is a lower bound by construction.

## 6. The user's prior across all pairs, and where the facts disagree

| group | rows | holds | partly | fails |
|---|---|---|---|---|
| top-15 prop pairs | 15 | 15 | 0 | 0 |
| ibkr, all 35 survivor codes | 35 | 20 | 1 | 14 |
| ibkr, the five top-15 codes | 5 | 5 | 0 | 0 |

Where the facts agree with the prior: for every top-15 prop pair and for each top-15 code at the own broker, the
required gross per sigma is lowest at 15-60 minutes, and 1-2 minute holds need 1.8-3.5 x as much (per sigma) because
the round-trip cost c_f is 0.14-0.44 sigma_1 and the entry cap stops the trade count from growing below 15 minutes.

Where the facts disagree or qualify it (plainly):
1. "Hours" is not supported at the prop firms. No top-15 pair's B reaches 120 or 240 minutes; the longest member is
   60 minutes (mffu|MYM, topstep|ZL). At 120 minutes G is 1.13-1.56 x min G and at 240 minutes 1.50-2.53 x. The
   facts support "15 to 60 minutes", not "minutes to hours". At the own broker, B reaches 120 minutes for 19 of the 35
   codes, and only MYM among the top-15 codes. The verdict per the spec rule stays "holds" for all 15 top pairs;
   the facts favour 15 to 60 minutes and do not support holds of hours, because G rises past 60 minutes where the
   entry cap and the power term bind.
2. The band is largely set by the formula. With k falling as about 1/sqrt(h) (section 1.2) and n_cap = min(20,
   floor(L_main / h)), the power term is constant up to 15 minutes (L_main 390) and grows as 1/sqrt(n_cap) after;
   min G therefore sits at 15-30 minutes for any code whose cost per sigma at 15 minutes is of the order of SR80 /
   sqrt(20) = 0.043. The prior "holds" because of the cost-and-power arithmetic under the entry cap and the
   independent-trades assumption; it says nothing about where a directional edge exists. Raising or removing the
   20-entry cap would move the minimum shorter.
3. The required edge is large in ticks at the band. Breaking even at 30 minutes needs a 0.518-0.558 hit rate, and 80%
   power at the test needs a gross of 5.0-13.2 ticks a trade at 30 minutes (c_f + e80 test). E.33's stated
   detectable edges on ZM (1.5-4.4 ticks a trade, section 5) are of the same order.
4. At the own broker the prior fails on 14 of 35 codes: rates (ZB, ZN, ZT), the FX micros (M6A, M6E), MBT, MHG and
   the micro and mini grains (MZC, MZL, MZM, MZS, MZW, XC) plus ZC have min G at cc, the overnight close-to-close
   hold. For 8 of them B is non-empty (6 with intraday members; MZM and MZS with OC
   only; section 3.2). Among the survivors' firm-independent rows the same
   happens for MZC, MZW, ZB and ZN. These codes are not in the top 15, so no prop pair is affected.
5. Overnight holds, where the prior's "hours" might extend, are not allowed at any of the five prop firms; were they
   allowed, the DLL would be below 2 x sigma_cc v on 8 of the 15 pairs. Inside the session the DLL excludes OC on 6
   pairs (tradeify|YM, topstep|YM, mffu|YM, tradeify|RTY, lucid|YM, mffu|RTY), 240 minutes on 5 of them (all but
   topstep|YM) and 120 minutes on 2 (mffu|YM, lucid|YM). Those h are already outside B by G, so the DLL never sets a
   band edge; it would bind first on the longest holds.
6. S = 1 tick (u) for YM, MNQ, RTY, MYM and ZL, and Lucid's fees are RR-05 (u). YM, MNQ, RTY and MYM have no sourced
   spread figure. ZL's only figure is a snippet-only average of 2.06 ticks, so ZL's cost may be understated: c_RT
   would be 2.56 instead of 1.50 ticks at S = 2.06. A larger true spread raises k at every h and moves min G longer;
   the verdicts were not recomputed under another S.

## 7. Inputs

| input | sha256 |
|---|---|
| reports/stage_e32b_briefs/F5_holding.json | 212a29bbf4350cc3a086f7aef1da722fc5c143870ec4967116516eeeb8f076b8 |
| reports/stage_e32b_briefs/econ32b.json | e56734663dd7ef083462595636e0e6b20c28954e62add436a56b0483bbd54e4c |
| reports/stage_e32b_briefs/F4_facts.md | b795d48db10aad83967f9add2a38c04b4f3b4ec8f9d2cefa6d403227e877dc15 |
| reports/stage_e32b_briefs/F2_firms.md | f1538e2d316603bda62d01c25da2c5e25d4d2d524e6adb76a604ce17ad0dfd6f |
| reports/E.33c_RETURN.md | 876ed944d51bea16350547c4195d7cf866177bf8aa128a7ce561d47df2cf8bed |
| reports/stage_e32b_briefs/work/F5/README.md | 5a389618c87776d5b8342974b5c3f5da931e91a9e5488b7057b6025c58ba3795 |
| reports/stage_e32b_briefs/RULINGS.md | 3b12960545fc00cbe1e53cf38c26fb39347eef7b8ec6a3c2179b475b695ce45c |
