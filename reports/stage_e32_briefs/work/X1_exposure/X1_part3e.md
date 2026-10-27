
Row count C3: 24 verbatim lines.

### C4. Other E.31 sources that carry steering-relevant facts (not statistics from the discovery dates)

| Item | Source | Recorded content |
|---|---|---|
| Volume check, ZM | reports/E.31_RETURN.md lines 128-141; reports/stage_e31_volume.md (not opened beyond the return) | window median 78,281.5 (own universe 79,512.0) over 2025-10-01..2026-09-30 (outside the discovery dates); per-quarter medians, 10th percentiles and front-month shares are in stage_e31_volume.md; "ZM's Q3 front-month share is low (about 0.08)" (E.31_RETURN.md line 139-140) |
| USDA calendar used for the splits | reports/E.31_RETURN.md lines 304-305; research/usda_releases.csv and usda_releases_ext.csv (E.31_RETURN.md lines 226-227) | WASDE, NASS and FAS rows; 88 FAS rows rule-derived or uncertain; NOPA not used; three 2022 FAS outage weeks skipped |
| Pilot spec definitions of the splits | reports/stage_e31_pilot_spec.md (not opened here); stats31.md line 1073 describes them | ZS and ZL move = sign of s x d, d = mid(t_f) - mid(t_f - L) in that contract's ticks; USDA = signed minutes from nearest release on the trade date; imbalance = s x I at j |
| Kill rule and verdict | reports/E.31_RETURN.md lines 18-24, 195-197 | ZM FAILS on K1 (model c, front, DAY, 10 s): -1.234 [-1.252, -1.214]; also fails at zero fee (gross -0.970 [-0.988, -0.950]) |
| Data on disk | reports/E.31_RETURN.md lines 25-28, 336-337 | 39 whole months 2020-12 to 2024-02, ZM MBO (ZM.v.0, ZM.v.1), ZS and ZL MBP-1 (front), definitions; 156 files, 24.2 GB; 816 trade dates measured; 764 DAY dates usable for the front month |
| Reviewer model deviation | reports/E.31_RETURN.md lines 29-33 | workers spawned as "Fable xhigh" ran on claude-sonnet-5-5 per transcript; verdict numbers rechecked by an Opus 5.5 xhigh worker: CONFIRMED |
Row count C4: 6.

## Not finished or not verified

- E.17 H1/H4/H5: that ZM actually entered the pooled series (on the fallback window) rests on reports/stage_e17_fallback.json rule A5 and reports/stage_e23_briefs/inventory/CDE.json (E16-H1 inputs: step2 27 roots); the pooled result files carry no per-root rows, and I did not open the bar-level units file (reports/stage_e17_runs/H1_units.jsonl).
- E.12 Gate 0 family-A pooling: whether the three K6-derived signals take values on all 28 exposures or only on soy and livestock legs was not extracted.
- Hold lengths for E16-H4 and E21-T1/T2, and the exact horizon units h60, h120, hF, were not extracted (named in Table B where so).
- The 471 baseline trials are not itemized in the registry; I itemized soy-involving ones from stage reports (K6 freeze, Gate 0 file). Other baseline trials (D.1 to D.1f MES families, K1-K5, K7-K9 members) were checked at cluster level in reports/stage_e16_overlap.md line 50 (roots list) and reports/stage_e23_briefs/inventory/CDE.json, not trial by trial.
- reports/stage_e12_gate0.json and the stage E.17 H result JSONs were read as result files (the H1 result printed daily pooled series once by mistake; no raw bars involved).
- stats31.json, stage_e31_volume.md and stage_e31_pilot_spec.md were not opened.
- Ledger summary prints only counts, dataset, schema, symbols, requested ranges (one extra check printed request start/end strings for the earliest mbo and mbp-1 lines). No key or other field was shown.
