# Stage E.32b provisional Layer 1 (C5a F5Runner, 2026-10-29 04:00 PDT)

**PROVISIONAL LAYER 1 ONLY. It comes from a score32b.py run on a STUB econ file (econ_stub_layer1only.json). Everything that run wrote about E, L2, the pair score S, pair ranks or the top 15 is MEANINGLESS and is not copied here; use none of it. Layer 1 (D1-D6, L1, the gate) does not read the econ file, so the Layer 1 values below are the exact spec-3 values for these inputs.**

Run note: score32b.py refused the original F2_attention.json (`codes` is a space-separated string, the script iterates a list: "code M under two underlyings (crude oil, crude oil)"). The run used F2_attention_listcodes.json, a format-only copy (`codes` split on spaces; every other field unchanged). The lead decides how the real run handles this.

Survivors (35): 6A, 6E, BTC, CL, GC, HG, M2K, M6A, M6E, MBT, MCL, MGC, MHG, MNG, MNQ, MYM, MZC, MZL, MZM, MZS, MZW, NG, RTY, XC, XK, YM, ZB, ZC, ZF, ZL, ZM, ZN, ZS, ZT, ZW

Gate failures (12):

- sigma_60 unknown (no owned bars and no sibling under 2.4): 10Y, 2YY, 30Y, 5YY, ETH, MET, SI, SIL (8)
- excluded (V49): NQ (1)
- D4 = 0: QG, QM, XW (3)

L1 < 2.00 (flagged, variant L1min2): M6E, MZC, MZL, MZM, MZS, MZW, QG, QM

## Per code (survivors first, then failures; alphabetical)

| code | family | F3 | S | c_RT | D1 | D2 | D3 | D4 | D5 | D6 | L1 | gate | arithmetic | L | J | Sat | Sat rule |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 6A | fx | owned | 1.00 | 1.50 | 2.25 | 2.00 | 4.00 | 3.00 | 4.00 | 3.00 | 2.875 | pass | sigma_60 = 22.36 ticks vs 2 x (1 + 0.5) = 3.00 ticks | 0 | 1 | 0 | none of (i)-(iii) |
| 6E | fx | owned | 1.00 | 1.50 | 2.50 | 1.00 | 3.00 | 3.00 | 3.00 | 2.00 | 2.4 | pass | sigma_60 = 26.19 ticks vs 2 x (1 + 0.5) = 3.00 ticks | 0 | 1 | 0 | none of (i)-(iii) |
| BTC | crypto | OC1 | 1.00 | 1.50 | 3.00 | 1.00 | 3.00 | 2.00 | 1.00 | 4.00 | 2.5 | pass | sigma_60 = 36.67 ticks vs 2 x (1 + 0.5) = 3.00 ticks | 1 | 1 | 0 | none of (i)-(iii) |
| CL | crude | owned | 1.00 | 1.50 | 3.50 | 0.00 | 4.00 | 3.00 | 3.00 | 2.00 | 2.7 | pass | sigma_60 = 48.28 ticks vs 2 x (1 + 0.5) = 3.00 ticks | 0 | 1 | 0 | none of (i)-(iii) |
| GC | metals | owned | 1.00 | 1.50 | 3.00 | 0.00 | 4.00 | 2.00 | 3.00 | 3.00 | 2.55 | pass | sigma_60 = 39.09 ticks vs 2 x (1 + 0.5) = 3.00 ticks | 1 | 1 | 0 | none of (i)-(iii) |
| HG | metals | owned | 1.00 | 1.50 | 2.50 | 1.50 | 3.00 | 3.00 | 4.00 | 2.00 | 2.575 | pass | sigma_60 = 22.74 ticks vs 2 x (1 + 0.5) = 3.00 ticks | 0 | 1 | 0 | none of (i)-(iii) |
| M2K | equity | OC1 | 1.00 | 1.50 | 3.75 | 2.00 | 4.00 | 2.00 | 2.00 | 3.00 | 2.975 | pass | sigma_60 = 70.77 ticks vs 2 x (1 + 0.5) = 3.00 ticks | 0 | 0 | 1 | (i) sibling notional-ADV ratio 22.7 >= 5; leader RTY |
| M6A | fx | OC1 | 1.00 | 1.50 | 1.25 | 2.00 | 4.00 | 1.00 | 4.00 | 3.00 | 2.275 | pass | sigma_60 = 11.18 ticks vs 2 x (1 + 0.5) = 3.00 ticks | 1 | 0 | 1 | (i) sibling notional-ADV ratio 112.3 >= 5; leader 6A |
| M6E | fx | OC1 | 1.00 | 1.50 | 1.50 | 1.00 | 3.00 | 2.00 | 3.00 | 2.00 | 1.95 | pass | sigma_60 = 13.10 ticks vs 2 x (1 + 0.5) = 3.00 ticks | 0 | 0 | 1 | (i) sibling notional-ADV ratio 74.3 >= 5; leader 6E |
| MBT | crypto | owned | 1.00 | 1.50 | 3.00 | 1.00 | 3.00 | 1.00 | 1.00 | 4.00 | 2.35 | pass | sigma_60 = 36.67 ticks vs 2 x (1 + 0.5) = 3.00 ticks | 1 | 0 | 1 | (i) ADV ratio to a larger-size sibling unknown -> holds (u); leader BTC |
| MCL | crude | owned | 1.00 | 1.50 | 3.50 | 0.00 | 4.00 | 2.00 | 1.00 | 2.00 | 2.35 | pass | sigma_60 = 48.34 ticks vs 2 x (1 + 0.5) = 3.00 ticks | 0 | 0 | 1 | (i) sibling notional-ADV ratio 28.8 >= 5; (ii) financially settled off a sibling's settlement (sourced); leader CL |
| MGC | metals | owned | 1.00 | 1.50 | 3.00 | 0.00 | 4.00 | 2.00 | 3.00 | 3.00 | 2.55 | pass | sigma_60 = 39.25 ticks vs 2 x (1 + 0.5) = 3.00 ticks | 0 | 0 | 1 | (i) sibling notional-ADV ratio 30.4 >= 5; leader GC |
| MHG | metals | owned | 1.00 | 1.50 | 2.50 | 1.50 | 3.00 | 1.00 | 2.00 | 2.00 | 2.075 | pass | sigma_60 = 23.07 ticks vs 2 x (1 + 0.5) = 3.00 ticks | 1 | 0 | 1 | (i) sibling notional-ADV ratio 136.2 >= 5; (ii) financially settled off a sibling's settlement (sourced); leader HG |
| MNG | natgas | OC1 | 1.00 | 1.50 | 3.50 | 0.00 | 3.00 | 1.00 | 1.00 | 3.00 | 2.2 | pass | sigma_60 = 47.26 ticks vs 2 x (1 + 0.5) = 3.00 ticks | 1 | 0 | 1 | (i) sibling notional-ADV ratio 61.9 >= 5; (ii) financially settled off a sibling's settlement (sourced); leader NG |
| MNQ | equity | OC1 | 1.00 | 1.50 | 4.00 | 1.00 | 4.00 | 3.00 | 0.00 | 3.00 | 2.85 | pass | sigma_60 = 202.67 ticks vs 2 x (1 + 0.5) = 3.00 ticks | 0 | 1 | 0 | none of (i)-(iii) |
| MYM | equity | OC1 | 1.00 | 1.50 | 4.00 | 2.00 | 3.00 | 2.00 | 3.00 | 3.00 | 3 | pass | sigma_60 = 88.56 ticks vs 2 x (1 + 0.5) = 3.00 ticks | 0 | 0 | 1 | (i) sibling notional-ADV ratio 14.2 >= 5; leader YM |
| MZC | grains | OC1 | 1.00 | 1.50 | 0.50 | 1.50 | 4.00 | 1.00 | 0.00 | 3.00 | 1.575 | pass | sigma_60 = 5.91 ticks vs 2 x (1 + 0.5) = 3.00 ticks | 1 | 0 | 1 | (i) ADV ratio to a larger-size sibling unknown -> holds (u); (ii) financially settled off a sibling's settlement (sourced); leader ZC |
| MZL | grains | OC1 | 1.00 | 1.50 | 2.00 | 2.00 | 3.00 | 1.00 | 1.00 | 2.00 | 1.9 | pass | sigma_60 = 19.10 ticks vs 2 x (1 + 0.5) = 3.00 ticks | 1 | 0 | 1 | (i) ADV ratio to a larger-size sibling unknown -> holds (u); (ii) financially settled off a sibling's settlement (sourced); leader ZL |
| MZM | grains | OC1 | 1.00 | 1.50 | 1.50 | 1.50 | 3.00 | 1.00 | 1.00 | 3.00 | 1.825 | pass | sigma_60 = 11.20 ticks vs 2 x (1 + 0.5) = 3.00 ticks | 1 | 0 | 1 | (i) ADV ratio to a larger-size sibling unknown -> holds (u); (ii) financially settled off a sibling's settlement (sourced); leader ZM |
| MZS | grains | OC1 | 1.00 | 1.50 | 1.50 | 0.50 | 4.00 | 1.00 | 1.00 | 3.00 | 1.825 | pass | sigma_60 = 11.35 ticks vs 2 x (1 + 0.5) = 3.00 ticks | 1 | 0 | 1 | (i) ADV ratio to a larger-size sibling unknown -> holds (u); (ii) financially settled off a sibling's settlement (sourced); leader ZS |
| MZW | grains | OC1 | 1.00 | 1.50 | 1.00 | 1.50 | 2.00 | 1.00 | 1.00 | 2.00 | 1.375 | pass | sigma_60 = 9.23 ticks vs 2 x (1 + 0.5) = 3.00 ticks | 1 | 0 | 1 | (i) ADV ratio to a larger-size sibling unknown -> holds (u); (ii) financially settled off a sibling's settlement (sourced); leader ZW |
| NG | natgas | owned | 1.00 | 1.50 | 3.50 | 0.00 | 3.00 | 3.00 | 3.00 | 3.00 | 2.7 | pass | sigma_60 = 47.26 ticks vs 2 x (1 + 0.5) = 3.00 ticks | 0 | 1 | 0 | none of (i)-(iii) |
| RTY | equity | owned | 1.00 | 1.50 | 3.75 | 2.00 | 4.00 | 3.00 | 2.00 | 3.00 | 3.125 | pass | sigma_60 = 70.77 ticks vs 2 x (1 + 0.5) = 3.00 ticks | 0 | 1 | 0 | none of (i)-(iii); (iii) unknown -> 0 (u) |
| XC | grains | OC1 | 1.00 | 1.50 | 2.50 | 1.50 | 4.00 | 1.00 | 2.00 | 3.00 | 2.375 | pass | sigma_60 = 23.66 ticks vs 2 x (1 + 0.5) = 3.00 ticks | 1 | 0 | 1 | (i) sibling notional-ADV ratio 396.3 >= 5; leader ZC |
| XK | grains | OC1 | 1.00 | 1.50 | 3.50 | 0.50 | 4.00 | 1.00 | 3.00 | 3.00 | 2.625 | pass | sigma_60 = 45.42 ticks vs 2 x (1 + 0.5) = 3.00 ticks | 1 | 0 | 1 | (i) sibling notional-ADV ratio 196.6 >= 5; leader ZS |
| YM | equity | owned | 1.00 | 1.50 | 4.00 | 2.00 | 3.00 | 3.00 | 4.00 | 3.00 | 3.25 | pass | sigma_60 = 88.56 ticks vs 2 x (1 + 0.5) = 3.00 ticks | 0 | 1 | 0 | none of (i)-(iii); (iii) unknown -> 0 (u) |
| ZB | rates | owned | 1.00 | 1.50 | 1.00 | 1.00 | 4.00 | 3.00 | 3.00 | 3.00 | 2.25 | pass | sigma_60 = 7.80 ticks vs 2 x (1 + 0.5) = 3.00 ticks | 0 | 1 | 0 | none of (i)-(iii) |
| ZC | grains | owned | 1.00 | 1.50 | 1.50 | 1.50 | 4.00 | 3.00 | 3.00 | 3.00 | 2.475 | pass | sigma_60 = 11.83 ticks vs 2 x (1 + 0.5) = 3.00 ticks | 0 | 1 | 0 | none of (i)-(iii); (iii) unknown -> 0 (u) |
| ZF | rates | owned | 1.00 | 1.50 | 1.50 | 1.00 | 4.00 | 3.00 | 3.00 | 3.00 | 2.4 | pass | sigma_60 = 11.57 ticks vs 2 x (1 + 0.5) = 3.00 ticks | 0 | 1 | 0 | none of (i)-(iii) |
| ZL | grains | owned | 1.00 | 1.50 | 3.00 | 2.00 | 3.00 | 3.00 | 4.00 | 2.00 | 2.8 | pass | sigma_60 = 38.21 ticks vs 2 x (1 + 0.5) = 3.00 ticks | 0 | 1 | 0 | none of (i)-(iii) |
| ZM | grains | owned | 1.00 | 1.50 | 2.50 | 1.50 | 3.00 | 3.00 | 4.00 | 3.00 | 2.725 | pass | sigma_60 = 22.40 ticks vs 2 x (1 + 0.5) = 3.00 ticks | 0 | 1 | 0 | none of (i)-(iii) |
| ZN | rates | owned | 1.00 | 1.50 | 1.00 | 0.00 | 4.00 | 3.00 | 3.00 | 3.00 | 2.1 | pass | sigma_60 = 7.99 ticks vs 2 x (1 + 0.5) = 3.00 ticks | 0 | 1 | 0 | none of (i)-(iii) |
| ZS | grains | owned | 1.00 | 1.50 | 2.50 | 0.50 | 4.00 | 3.00 | 4.00 | 3.00 | 2.725 | pass | sigma_60 = 22.71 ticks vs 2 x (1 + 0.5) = 3.00 ticks | 0 | 1 | 0 | none of (i)-(iii) |
| ZT | rates | owned | 1.00 | 1.50 | 1.50 | 1.00 | 4.00 | 3.00 | 3.00 | 3.00 | 2.4 | pass | sigma_60 = 11.00 ticks vs 2 x (1 + 0.5) = 3.00 ticks | 0 | 1 | 0 | none of (i)-(iii) |
| ZW | grains | owned | 1.00 | 1.50 | 2.00 | 1.50 | 2.00 | 3.00 | 4.00 | 2.00 | 2.275 | pass | sigma_60 = 18.45 ticks vs 2 x (1 + 0.5) = 3.00 ticks | 0 | 1 | 0 | none of (i)-(iii); (iii) unknown -> 0 (u) |
| 10Y | rates | unknown | 1.00 | 1.50 | - | 1.00 | 3.00 | 2.00 | 0.00 | 3.00 | - | FAIL: sigma_60 unknown (no owned bars and no sibling under 2.4) | sigma_60 unknown (no owned bars and no sibling under 2.4) | 1 | 1 | 0 | none of (i)-(iii); (iii) unknown -> 0 (u) |
| 2YY | rates | unknown | 1.00 | 1.50 | - | 1.00 | 3.00 | 1.00 | 0.00 | 3.00 | - | FAIL: sigma_60 unknown (no owned bars and no sibling under 2.4) | sigma_60 unknown (no owned bars and no sibling under 2.4) | 2 | 1 | 0 | none of (i)-(iii); (iii) unknown -> 0 (u) |
| 30Y | rates | unknown | 1.00 | 1.50 | - | 1.00 | 3.00 | 1.00 | 0.00 | 3.00 | - | FAIL: sigma_60 unknown (no owned bars and no sibling under 2.4) | sigma_60 unknown (no owned bars and no sibling under 2.4) | 2 | 1 | 0 | none of (i)-(iii); (iii) unknown -> 0 (u) |
| 5YY | rates | unknown | 1.00 | 1.50 | - | 1.00 | 3.00 | 1.00 | 0.00 | 3.00 | - | FAIL: sigma_60 unknown (no owned bars and no sibling under 2.4) | sigma_60 unknown (no owned bars and no sibling under 2.4) | 2 | 1 | 0 | none of (i)-(iii); (iii) unknown -> 0 (u) |
| ETH | crypto | unknown | 1.00 | 1.50 | - | 2.00 | 3.00 | 3.00 | 0.00 | 2.00 | - | FAIL: sigma_60 unknown (no owned bars and no sibling under 2.4) | sigma_60 unknown (no owned bars and no sibling under 2.4) | 0 | 1 | 0 | none of (i)-(iii); (iii) unknown -> 0 (u) |
| MET | crypto | unknown | 1.00 | 1.50 | - | 2.00 | 3.00 | 1.00 | 1.00 | 2.00 | - | FAIL: sigma_60 unknown (no owned bars and no sibling under 2.4) | sigma_60 unknown (no owned bars and no sibling under 2.4) | 0 | 1 | 1 | (i) sibling notional-ADV ratio 66.0 >= 5; leader ETH |
| NQ | equity | - | - | - | - | - | - | - | - | - | - | FAIL: excluded (V49) | - | - | - | - | - |
| QG | natgas | OC1 | 1.00 | 1.50 | 1.00 | 0.00 | 3.00 | 0.00 | 3.00 | 3.00 | 1.5 | FAIL: D4 = 0 | sigma_60 = 9.45 ticks vs 2 x (1 + 0.5) = 3.00 ticks | 1 | 1 | 1 | (i) sibling notional-ADV ratio 86.7 >= 5; (ii) financially settled off a sibling's settlement (sourced); leader NG |
| QM | crude | OC1 | 1.00 | 1.50 | 2.00 | 0.00 | 4.00 | 0.00 | 3.00 | 2.00 | 1.8 | FAIL: D4 = 0 | sigma_60 = 19.31 ticks vs 2 x (1 + 0.5) = 3.00 ticks | 1 | 1 | 1 | (i) ADV ratio to a larger-size sibling unknown -> holds (u); (ii) financially settled off a sibling's settlement (sourced); leader CL |
| SI | metals | unknown | 1.00 | 1.50 | - | 1.50 | 4.00 | 3.00 | 2.00 | 3.00 | - | FAIL: sigma_60 unknown (no owned bars and no sibling under 2.4) | sigma_60 unknown (no owned bars and no sibling under 2.4) | 0 | 1 | 0 | none of (i)-(iii); (iii) unknown -> 0 (u) |
| SIL | metals | unknown | 1.00 | 1.50 | - | 1.50 | 4.00 | 3.00 | 3.00 | 3.00 | - | FAIL: sigma_60 unknown (no owned bars and no sibling under 2.4) | sigma_60 unknown (no owned bars and no sibling under 2.4) | 0 | 1 | 0 | none of (i)-(iii); (iii) unknown -> 0 (u) |
| XW | grains | OC1 | 1.00 | 1.50 | 3.00 | 1.50 | 2.00 | 0.00 | 3.00 | 2.00 | 2.025 | FAIL: D4 = 0 | sigma_60 = 36.90 ticks vs 2 x (1 + 0.5) = 3.00 ticks | 2 | 0 | 1 | (i) sibling notional-ADV ratio 213.5 >= 5; leader ZW |

## D4 inputs and unknown notes

| code | ADV (kind) | spread sourced | touch sourced | J: R_d p99 x v (USD) vs 1,000 | u notes |
|---|---|---|---|---|---|
| 6A | 82950 (v0_front_median) | yes, 1 | no | 1815 | - |
| 6E | 176291 (v0_front_median) | yes, 1 | no | 2658 | - |
| BTC | unknown (unknown) | no | no | 17611 | S: no sourced spread -> 1 tick (u); D2 a (BTC): unknown -> 1 (u); D4 L: ADV unknown -> L = 1 (u); D5 k: price unknown -> 1 (u) |
| CL | 227772 (v0_front_median) | yes, 1 | no | 5695 | - |
| GC | 160118 (v0_front_median) | yes, 1 | yes, 4.62 | 5677 | - |
| HG | 59578 (v0_front_median) | yes, 1 | no | 4434 | - |
| M2K | 79724 (published_all_expiry) | no | no | 411 | S: no sourced spread -> 1 tick (u) |
| M6A | 7384 (published_all_expiry) | no | no | 182 | S: no sourced spread -> 1 tick (u) |
| M6E | 23742 (published_all_expiry) | no | no | 266 | S: no sourced spread -> 1 tick (u) |
| MBT | 6678 (v0_front_median) | no | no | 352 | S: no sourced spread -> 1 tick (u); Sat (i): ADV ratio to larger-size sibling BTC unknown -> holds (u); D2 a (BTC): unknown -> 1 (u) |
| MCL | 79142 (v0_front_median) | no | no | 571 | S: no sourced spread -> 1 tick (u); Sat (i): ADV ratio to larger-size sibling QM unknown -> holds (u) |
| MGC | 52744 (v0_front_median) | no | no | 571 | S: no sourced spread -> 1 tick (u) |
| MHG | 4373 (v0_front_median) | no | no | 439 | S: no sourced spread -> 1 tick (u) |
| MNG | 13781 (published_all_expiry) | no | yes, 3 | 705 | S: no sourced spread -> 1 tick (u); Sat (iii): unknown -> 0 (u) |
| MNQ | 1600000 (published_all_expiry) | no | no | 1133 | S: no sourced spread -> 1 tick (u) |
| MYM | 114779 (published_all_expiry) | no | no | 525 | S: no sourced spread -> 1 tick (u) |
| MZC | unknown (unknown) | no | no | 180 | S: no sourced spread -> 1 tick (u); Sat (i): ADV ratio to larger-size sibling XC unknown -> holds (u); Sat (i): ADV ratio to larger-size sibling ZC unknown -> holds (u); Sat (iii): unknown -> 0 (u); D4 L: ADV unknown -> L = 1 (u); D5 k: price unknown -> 1 (u) |
| MZL | unknown (unknown) | no | no | 224 | S: no sourced spread -> 1 tick (u); Sat (i): ADV ratio to larger-size sibling ZL unknown -> holds (u); D4 L: ADV unknown -> L = 1 (u); D5 k: price unknown -> 1 (u) |
| MZM | unknown (unknown) | no | no | 227 | S: no sourced spread -> 1 tick (u); Sat (i): ADV ratio to larger-size sibling ZM unknown -> holds (u); D4 L: ADV unknown -> L = 1 (u); D5 k: price unknown -> 1 (u) |
| MZS | unknown (unknown) | no | no | 259 | S: no sourced spread -> 1 tick (u); Sat (i): ADV ratio to larger-size sibling XK unknown -> holds (u); Sat (i): ADV ratio to larger-size sibling ZS unknown -> holds (u); D4 L: ADV unknown -> L = 1 (u); D5 k: price unknown -> 1 (u) |
| MZW | unknown (unknown) | no | no | 269 | S: no sourced spread -> 1 tick (u); Sat (i): ADV ratio to larger-size sibling XW unknown -> holds (u); Sat (i): ADV ratio to larger-size sibling ZW unknown -> holds (u); Sat (iii): unknown -> 0 (u); D4 L: ADV unknown -> L = 1 (u); D5 k: price unknown -> 1 (u) |
| NG | 85334 (v0_front_median) | yes, 1 | yes, 5 | 7047 | - |
| RTY | 181060 (v0_front_median) | no | no | 4111 | S: no sourced spread -> 1 tick (u); Sat (iii): unknown -> 0 (u) |
| XC | 1160 (published_all_expiry) | no | no | 361 | S: no sourced spread -> 1 tick (u); Sat (iii): unknown -> 0 (u); D5 k: price unknown -> 1 (u) |
| XK | 1980 (published_all_expiry) | no | no | 518 | S: no sourced spread -> 1 tick (u); D5 k: price unknown -> 1 (u) |
| YM | 163416 (v0_front_median) | no | no | 5247 | S: no sourced spread -> 1 tick (u); Sat (iii): unknown -> 0 (u) |
| ZB | 291523 (v0_front_median) | yes, 1 | no | 3771 | - |
| ZC | 91946 (v0_front_median) | yes, 1 | no | 1803 | Sat (iii): unknown -> 0 (u) |
| ZF | 927861 (v0_front_median) | yes, 1 | no | 1614 | - |
| ZL | 42686 (v0_front_median) | no | no | 2245 | S: no sourced spread -> 1 tick (u) |
| ZM | 36690 (v0_front_median) | no | no | 2265 | S: no sourced spread -> 1 tick (u) |
| ZN | 1385806 (v0_front_median) | yes, 1 | no | 2088 | - |
| ZS | 77862 (v0_front_median) | yes, 1 | no | 2588 | - |
| ZT | 472003 (v0_front_median) | no | no | 2072 | S: no sourced spread -> 1 tick (u) |
| ZW | 39362 (v0_front_median) | no | no | 2686 | S: no sourced spread -> 1 tick (u); Sat (iii): unknown -> 0 (u) |
| 10Y | 1277 (published_all_expiry) | no | no | unknown | S: no sourced spread -> 1 tick (u); Sat (iii): unknown -> 0 (u); D4 J: R_d p99 or tick value unknown -> J = 1 (u); D5 k: price unknown -> 1 (u) |
| 2YY | 0 (published_all_expiry) | no | no | unknown | S: no sourced spread -> 1 tick (u); Sat (iii): unknown -> 0 (u); D4 J: R_d p99 or tick value unknown -> J = 1 (u); D5 k: price unknown -> 1 (u) |
| 30Y | 0 (published_all_expiry) | no | no | unknown | S: no sourced spread -> 1 tick (u); Sat (iii): unknown -> 0 (u); D4 J: R_d p99 or tick value unknown -> J = 1 (u); D5 k: price unknown -> 1 (u) |
| 5YY | 0 (published_all_expiry) | no | no | unknown | S: no sourced spread -> 1 tick (u); Sat (iii): unknown -> 0 (u); D4 J: R_d p99 or tick value unknown -> J = 1 (u); D5 k: price unknown -> 1 (u) |
| ETH | 19000 (published_all_expiry) | no | no | unknown | S: no sourced spread -> 1 tick (u); Sat (iii): unknown -> 0 (u); D2 a (ETH): unknown -> 1 (u); D4 J: R_d p99 or tick value unknown -> J = 1 (u); D5 k: price unknown -> 1 (u) |
| MET | 144000 (published_all_expiry) | no | no | unknown | S: no sourced spread -> 1 tick (u); Sat (iii): unknown -> 0 (u); D2 a (ETH): unknown -> 1 (u); D4 J: R_d p99 or tick value unknown -> J = 1 (u) |
| NQ | excluded (V49) | - | - | - | - |
| QG | 3937 (published_all_expiry) | yes, 1 | yes, 10 | 1762 | Sat (iii): unknown -> 0 (u) |
| QM | unknown (unknown) | no | no | 2848 | S: no sourced spread -> 1 tick (u); Sat (i): ADV ratio to larger-size sibling CL unknown -> holds (u); D4 L: ADV unknown -> L = 1 (u) |
| SI | 64000 (published_all_expiry) | yes, 1 | yes, 6.56 | unknown | Sat (iii): unknown -> 0 (u); D4 J: R_d p99 or tick value unknown -> J = 1 (u); D5 h: MBO start unknown -> 1 (u) |
| SIL | 74000 (published_all_expiry) | no | no | unknown | S: no sourced spread -> 1 tick (u); Sat (iii): unknown -> 0 (u); D4 J: R_d p99 or tick value unknown -> J = 1 (u) |
| XW | 922 (published_all_expiry) | no | no | 537 | S: no sourced spread -> 1 tick (u); Sat (iii): unknown -> 0 (u); D5 k: price unknown -> 1 (u) |

## Layer 1 notes the script raised for the lead

- D2 c (10Y): provisional, notional ADV unknown for 10Y, 2YY, 30Y, 5YY in family rates (ADV, multiplier or F3 median close unknown); compared among known codes only
- D2 c (2YY): provisional, notional ADV unknown for 10Y, 2YY, 30Y, 5YY in family rates (ADV, multiplier or F3 median close unknown); compared among known codes only
- D2 c (30Y): provisional, notional ADV unknown for 10Y, 2YY, 30Y, 5YY in family rates (ADV, multiplier or F3 median close unknown); compared among known codes only
- D2 c (5YY): provisional, notional ADV unknown for 10Y, 2YY, 30Y, 5YY in family rates (ADV, multiplier or F3 median close unknown); compared among known codes only
- D2 c (BTC): provisional, notional ADV unknown for BTC, ETH, MET in family crypto (ADV, multiplier or F3 median close unknown); compared among known codes only
- D2 c (CL): provisional, notional ADV unknown for QM in family crude (ADV, multiplier or F3 median close unknown); compared among known codes only
- D2 c (ETH): provisional, notional ADV unknown for BTC, ETH, MET in family crypto (ADV, multiplier or F3 median close unknown); compared among known codes only
- D2 c (GC): provisional, notional ADV unknown for SI, SIL in family metals (ADV, multiplier or F3 median close unknown); compared among known codes only
- D2 c (HG): provisional, notional ADV unknown for SI, SIL in family metals (ADV, multiplier or F3 median close unknown); compared among known codes only
- D2 c (SI): provisional, notional ADV unknown for SI, SIL in family metals (ADV, multiplier or F3 median close unknown); compared among known codes only
- D2 c (SIL): provisional, notional ADV unknown for SI, SIL in family metals (ADV, multiplier or F3 median close unknown); compared among known codes only
- D2 c (ZB): provisional, notional ADV unknown for 10Y, 2YY, 30Y, 5YY in family rates (ADV, multiplier or F3 median close unknown); compared among known codes only
- D2 c (ZC): provisional, notional ADV unknown for MZC, MZL, MZM, MZS, MZW in family grains (ADV, multiplier or F3 median close unknown); compared among known codes only
- D2 c (ZF): provisional, notional ADV unknown for 10Y, 2YY, 30Y, 5YY in family rates (ADV, multiplier or F3 median close unknown); compared among known codes only
- D2 c (ZL): provisional, notional ADV unknown for MZC, MZL, MZM, MZS, MZW in family grains (ADV, multiplier or F3 median close unknown); compared among known codes only
- D2 c (ZM): provisional, notional ADV unknown for MZC, MZL, MZM, MZS, MZW in family grains (ADV, multiplier or F3 median close unknown); compared among known codes only
- D2 c (ZN): provisional, notional ADV unknown for 10Y, 2YY, 30Y, 5YY in family rates (ADV, multiplier or F3 median close unknown); compared among known codes only
- D2 c (ZS): provisional, notional ADV unknown for MZC, MZL, MZM, MZS, MZW in family grains (ADV, multiplier or F3 median close unknown); compared among known codes only
- D2 c (ZT): provisional, notional ADV unknown for 10Y, 2YY, 30Y, 5YY in family rates (ADV, multiplier or F3 median close unknown); compared among known codes only
- D2 c (ZW): provisional, notional ADV unknown for MZC, MZL, MZM, MZS, MZW in family grains (ADV, multiplier or F3 median close unknown); compared among known codes only
- leader: leader from F4 (notional ADV not computable for every sibling)

## Inputs

- F3: reports/stage_e32b_briefs/F3_vol.json (sha256 9ba14d568d283d11c2a19889ea57c3b6dcc12fa11682b44f6eecd32a3ea18fcc)
- F4: reports/stage_e32b_briefs/F4_facts_unmasked.json (sha256 4a4d1e2965ee6dbc8497c6dc2b08ac74fa51b61df548cd1b2173ecbf4171397c)
- blind: reports/stage_e32b_briefs/F4_blind_unmasked.json (sha256 aeae3296aa685c51d1eed76eaa27e492ee78e247f7878bcce51f9b3b197c46de)
- econ: reports/stage_e32b_briefs/work/F5run/econ_stub_layer1only.json (sha256 3e0afed44a3ce60a41fd853af617ff33da0e2057ae0daed9263a6de2ca6bfc66)
- attention: reports/stage_e32b_briefs/work/F5run/F2_attention_listcodes.json (sha256 7ae497c00a2fda85e82cd0952f800c5f06514c6c00db1f0f5df30856ef8d657d)
- data_access: reports/stage_e32b_briefs/F2_data_access.json (sha256 4bad06bd9d34c9132db11c0f10ae8b8cee9d5e0f0dca185687128d8d7fc1e1b0)
- score_stub_layer1only: /home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e32b_briefs/work/F5run/score_stub_layer1only.json (sha256 9dd1361b3bca7ac5ef7f1b75c71ef8ac4057ac9242a557941d94e79f5265a4a9)
