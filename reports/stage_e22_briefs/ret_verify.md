| Cluster | Items (0-6) | Main evidence | Notes | Result |
|---|---|---|---|---|
| K5 | 1-6 VERIFIED; 0 WITH NOTES | own bootstrap and DSR/t/PBO to 1e-9; fomc series rebuilt from 34 trips with MGC's $1.92 commission and $1.00 tick (not GC's) | pmfix (excluded) executed by `--all`, present and not used; the coverage-excluded MHG trials classed inconclusive and blocking is the required reading of NULL_CRITERIA_E 1, 6 and the frozen code | no DISCREPANCY |
| K8 | 1-3, 5 VERIFIED; 0, 4, 6 WITH NOTES | 126 checks, 0 FAIL; HEOD 231/231 trips and 944/944 days exact with MGC's costs on GC bars; MES s_x 2020-02-03 | flight window starts 2020-02-04 (S_X date is a leg roll blackout); fewest-trips tie 231/231; PBO mixes MGC and 6C tick units by L-E5-3 | no DISCREPANCY |
| K3 | 1-3, 5 VERIFIED; 0, 4, 6 WITH NOTES | 25 run trials within 1e-9; ldnrev 6E/6J/6S rebuilt exactly; all 20,611 trips match the frozen cost table | no ldnrev trip on the 14 kept FX dates (cp3, ecbfix and one cp2 6J trip were force-flattened at 11:30 on them); the classification of coverage-excluded run trials as blocking follows NULL_CRITERIA_E 6 literally (decision 3) | no DISCREPANCY |
| K6 | 0-2, 4-6 VERIFIED; 3 WITH NOTES | all 27 trials bit-identical; limitcont HE 10 trips rebuilt exactly (series to 1e-14) | DSR differs from an exact inverse normal by 1.9e-8 relative (the program's Acklam approximation); PBO floor blocks drop 6 trailing dates (array_split sensitivity 0.586, also fails) | no DISCREPANCY |

No verdict figure was marked unverified; no second run was made.
