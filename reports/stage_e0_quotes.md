# Stage E.0 Databento quotes (GLBX.MDP3, 50 CME products)

Session `stage-E.0-2026-09-23`. Quotes only: every figure is a price Databento returned from the free metadata endpoints; nothing was bought.

- History (set A): ohlcv-1m, 2019-05-01..2026-06-21 (end exclusive, 00:00 UTC).
- Samples (sets B, C): 2025-05-14, 2025-08-13, 2025-11-12, 2026-02-11, 2026-04-15.
- ohlcv-1m record size 56 B; records = bytes / size.
- Quote events 5050 (4892 ok, 158 failed, 158 still failing); distinct requests 4892 of 5050 planned (158 not yet quoted); unresolved symbols 0.
- Ledger lines 452..5501 (5050 events); all zero-USD quotes: True; session committed $0.00; check passed: True.

## Totals

| scope | products | ohlcv-1m USD | ohlcv-1m GB | mbp-1 5d USD | mbp-1 5d GB | tbbo 5d USD | tbbo 5d GB |
|---|---:|---:|---:|---:|---:|---:|---:|
| K1 | 8 | $69.13 | 1.060 | $32.19 | 19.203 | $19.46 | 0.746 |
| K2 | 6 | $48.56 | 0.745 | $5.26 | 3.137 | $2.84 | 0.109 |
| K3 | 12 | $90.41 | 1.387 | $4.38 | 2.614 | $1.74 | 0.067 |
| K4 | 8 | $50.15 | 0.769 | $2.86 | 1.705 | $2.18 | 0.084 |
| K5 | 7 | $53.71 | 0.824 | $5.49 | 3.274 | $4.62 | 0.177 |
| K6 | 7 | $31.85 | 0.489 | $0.77 | 0.461 | $0.95 | 0.036 |
| K7 | 2 | $7.28 | 0.112 | $1.61 | 0.961 | $0.40 | 0.015 |
| universe | 50 | $351.10 | 5.386 | $52.56 | 31.354 | $32.19 | 1.234 |

## Per product

| root | group | first mapped | months | ohlcv-1m USD | records | rec/weekday | mbp-1 USD | tbbo USD | window CT | coverage mean |
|---|---|---|---:|---:|---:|---:|---:|---:|---|---:|
| ES | K1 | 2019-05-01 | 86/86 | $9.20 | 2,519,410 | 1,352 | $5.44 | $4.41 | 08:30-15:00 | 1.000 |
| NQ | K1 | 2019-05-01 | 86/86 | $9.20 | 2,519,225 | 1,352 | $5.92 | $3.58 | 08:30-15:00 | 1.000 |
| RTY | K1 | 2019-05-01 | 86/86 | $8.88 | 2,432,064 | 1,305 | $1.86 | $0.96 | 08:30-15:00 | 1.000 |
| YM | K1 | 2019-05-01 | 86/86 | $9.11 | 2,496,520 | 1,340 | $1.51 | $0.63 | 08:30-15:00 | 1.000 |
| MNQ | K1 | 2019-05-01 | 86/86 | $9.17 | 2,511,541 | 1,348 | $13.46 | $8.62 | 08:30-15:00 | 1.000 |
| M2K | K1 | 2019-05-01 | 86/86 | $8.68 | 2,376,886 | 1,276 | $1.34 | $0.48 | 08:30-15:00 | 1.000 |
| MYM | K1 | 2019-05-01 | 86/86 | $8.92 | 2,442,457 | 1,311 | $2.50 | $0.73 | 08:30-15:00 | 1.000 |
| NKD | K1 | 2019-05-01 | 86/86 | $5.98 | 1,638,201 | 879 | $0.16 | $0.03 | 08:30-15:00 | 0.621 |
| ZT | K2 | 2019-05-01 | 86/86 | $7.28 | 1,994,422 | 1,071 | $1.01 | $0.27 | 07:20-14:00 | 0.981 |
| ZF | K2 | 2019-05-01 | 86/86 | $8.36 | 2,289,380 | 1,229 | $1.07 | $0.64 | 07:20-14:00 | 0.997 |
| ZN | K2 | 2019-05-01 | 86/86 | $8.68 | 2,377,797 | 1,276 | $1.31 | $0.87 | 07:20-14:00 | 0.999 |
| TN | K2 | 2019-05-01 | 86/86 | $7.89 | 2,160,679 | 1,160 | $0.74 | $0.38 | 07:20-14:00 | 0.972 |
| ZB | K2 | 2019-05-01 | 86/86 | $8.11 | 2,221,943 | 1,193 | $0.60 | $0.35 | 07:20-14:00 | 0.985 |
| UB | K2 | 2019-05-01 | 86/86 | $8.24 | 2,258,098 | 1,212 | $0.52 | $0.32 | 07:20-14:00 | 0.982 |
| 6A | K3 | 2019-05-01 | 86/86 | $8.92 | 2,442,928 | 1,311 | $0.66 | $0.22 | 07:20-14:00 | 0.999 |
| 6B | K3 | 2019-05-01 | 86/86 | $8.54 | 2,337,861 | 1,255 | $0.44 | $0.16 | 07:20-14:00 | 0.987 |
| 6C | K3 | 2019-05-01 | 86/86 | $8.41 | 2,304,044 | 1,237 | $0.27 | $0.12 | 07:20-14:00 | 0.985 |
| 6E | K3 | 2019-05-01 | 86/86 | $9.05 | 2,479,705 | 1,331 | $0.86 | $0.42 | 07:20-14:00 | 0.998 |
| 6J | K3 | 2019-05-01 | 86/86 | $9.00 | 2,466,328 | 1,324 | $0.80 | $0.36 | 07:20-14:00 | 0.996 |
| 6S | K3 | 2019-05-01 | 86/86 | $7.55 | 2,068,683 | 1,110 | $0.20 | $0.12 | 07:20-14:00 | 0.970 |
| 6M | K3 | 2019-05-01 | 86/86 | $6.50 | 1,779,586 | 955 | $0.20 | $0.07 | 07:20-14:00 | 0.903 |
| 6N | K3 | 2019-05-01 | 86/86 | $8.03 | 2,200,073 | 1,181 | $0.32 | $0.09 | 07:20-14:00 | 0.957 |
| E7 | K3 | 2019-05-01 | 86/86 | $5.70 | 1,562,048 | 838 | $0.17 | $0.02 | 07:20-14:00 | 0.643 |
| M6E | K3 | 2019-05-01 | 86/86 | $7.84 | 2,146,759 | 1,152 | $0.26 | $0.10 | 07:20-14:00 | 0.952 |
| M6A | K3 | 2019-05-01 | 86/86 | $6.69 | 1,831,672 | 983 | $0.11 | $0.03 | 07:20-14:00 | 0.731 |
| M6B | K3 | 2019-05-01 | 86/86 | $4.18 | 1,144,309 | 614 | $0.10 | $0.02 | 07:20-14:00 | 0.615 |
| CL | K4 | 2019-05-01 | 86/86 | $9.12 | 2,498,814 | 1,341 | $0.89 | $0.79 | 08:00-13:30 | 1.000 |
| QM | K4 | 2019-05-01 | 86/86 | $7.04 | 1,926,991 | 1,034 | $0.13 | $0.03 | 08:00-13:30 | 0.870 |
| MCL | K4 | 2019-05-01 | 61/86 | $6.12 | 1,675,531 | 1,270 | $0.64 | $0.49 | 08:00-13:30 | 1.000 |
| NG | K4 | 2019-05-01 | 86/86 | $8.29 | 2,270,249 | 1,219 | $0.25 | $0.42 | 08:00-13:30 | 1.000 |
| QG | K4 | 2019-05-01 | 86/86 | $4.46 | 1,220,951 | 655 | $0.05 | $0.01 | 08:00-13:30 | 0.629 |
| MNG | K4 | 2019-05-01 | 41/86 | $1.95 | 534,845 | 287 | $0.13 | $0.06 | 08:00-13:30 | 0.928 |
| RB | K4 | 2019-05-01 | 86/86 | $6.50 | 1,779,166 | 955 | $0.43 | $0.17 | 08:00-13:30 | 1.000 |
| HO | K4 | 2019-05-01 | 86/86 | $6.68 | 1,830,238 | 982 | $0.34 | $0.19 | 08:00-13:30 | 1.000 |
| GC | K5 | 2019-05-01 | 86/86 | $9.11 | 2,495,995 | 1,340 | $1.03 | $1.08 | 07:20-12:30 | 1.000 |
| MGC | K5 | 2019-05-01 | 86/86 | $8.87 | 2,429,700 | 1,304 | $2.29 | $2.25 | 07:20-12:30 | 1.000 |
| SI | K5 | 2019-05-01 | 86/86 | $8.73 | 2,390,655 | 1,283 | $0.58 | $0.33 | 07:20-12:30 | 0.999 |
| SIL | K5 | 2019-05-01 | 86/86 | $6.77 | 1,854,001 | 995 | $0.66 | $0.52 | 07:20-12:30 | 0.990 |
| HG | K5 | 2019-05-01 | 86/86 | $8.80 | 2,410,411 | 1,294 | $0.26 | $0.19 | 07:20-12:30 | 0.997 |
| MHG | K5 | 2019-05-01 | 51/86 | $3.78 | 1,034,865 | 940 | $0.28 | $0.10 | 07:20-12:30 | 0.941 |
| PL | K5 | 2019-05-01 | 86/86 | $7.65 | 2,096,561 | 1,125 | $0.40 | $0.14 | 07:20-12:30 | 0.991 |
| ZC | K6 grains | 2019-05-01 | 86/86 | $5.55 | 1,521,549 | 817 | $0.09 | $0.13 | 08:30-13:20 | 1.000 |
| ZW | K6 grains | 2019-05-01 | 86/86 | $5.43 | 1,487,914 | 799 | $0.10 | $0.10 | 08:30-13:20 | 0.990 |
| ZS | K6 grains | 2019-05-01 | 86/86 | $6.12 | 1,675,690 | 899 | $0.21 | $0.22 | 08:30-13:20 | 1.000 |
| ZM | K6 grains | 2019-05-01 | 86/86 | $5.27 | 1,443,823 | 775 | $0.13 | $0.11 | 08:30-13:20 | 1.000 |
| ZL | K6 grains | 2019-05-01 | 86/86 | $5.91 | 1,619,993 | 870 | $0.15 | $0.20 | 08:30-13:20 | 1.000 |
| HE | K6 livestock | 2019-05-01 | 86/86 | $1.77 | 485,732 | 261 | $0.03 | $0.07 | 08:30-13:05 | 0.998 |
| LE | K6 livestock | 2019-05-01 | 86/86 | $1.79 | 489,134 | 263 | $0.06 | $0.12 | 08:30-13:05 | 0.999 |
| MBT | K7 | 2019-05-01 | 63/86 | $4.60 | 1,260,953 | 926 | $1.20 | $0.30 | 08:30-15:00 | 0.996 |
| MET | K7 | 2019-05-01 | 56/86 | $2.68 | 733,666 | 606 | $0.41 | $0.10 | 08:30-15:00 | 0.947 |

## Set C coverage per date (records / window minutes)

| root | 2025-05-14 | 2025-08-13 | 2025-11-12 | 2026-02-11 | 2026-04-15 |
|---|---:|---:|---:|---:|---:|
| ES | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| NQ | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| RTY | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| YM | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| MNQ | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| M2K | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| MYM | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| NKD | 0.718 | 0.536 | 0.577 | 0.615 | 0.659 |
| ZT | 0.995 | 0.978 | 0.973 | 0.975 | 0.988 |
| ZF | 0.993 | 0.995 | 1.000 | 1.000 | 0.998 |
| ZN | 1.000 | 0.998 | 1.000 | 0.998 | 1.000 |
| TN | 0.990 | 0.938 | 0.983 | 0.993 | 0.960 |
| ZB | 0.978 | 0.985 | 0.988 | 0.990 | 0.983 |
| UB | 1.000 | 0.965 | 0.993 | 0.988 | 0.968 |
| 6A | 1.000 | 0.995 | 1.000 | 1.000 | 1.000 |
| 6B | 1.000 | 0.980 | 0.973 | 0.995 | 0.985 |
| 6C | 0.995 | 0.983 | 0.960 | 0.998 | 0.988 |
| 6E | 1.000 | 0.998 | 0.995 | 1.000 | 1.000 |
| 6J | 1.000 | 0.993 | 0.993 | 1.000 | 0.993 |
| 6S | 1.000 | 0.963 | 0.975 | 0.935 | 0.978 |
| 6M | 0.895 | 0.877 | 0.782 | 1.000 | 0.963 |
| 6N | 0.978 | 0.922 | 0.945 | 0.988 | 0.955 |
| E7 | 0.713 | 0.565 | 0.535 | 0.765 | 0.637 |
| M6E | 0.993 | 0.953 | 0.912 | 0.963 | 0.938 |
| M6A | 0.858 | 0.657 | 0.522 | 0.875 | 0.743 |
| M6B | 0.600 | 0.562 | 0.600 | 0.790 | 0.522 |
| CL | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| QM | 0.891 | 0.800 | 0.903 | 0.788 | 0.970 |
| MCL | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| NG | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| QG | 0.655 | 0.597 | 0.785 | 0.739 | 0.370 |
| MNG | 0.945 | 0.909 | 0.979 | 0.958 | 0.852 |
| RB | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| HO | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| GC | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| MGC | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| SI | 1.000 | 0.997 | 1.000 | 1.000 | 1.000 |
| SIL | 0.965 | 0.987 | 1.000 | 1.000 | 1.000 |
| HG | 1.000 | 0.990 | 0.997 | 1.000 | 0.997 |
| MHG | 0.965 | 0.852 | 0.958 | 0.997 | 0.935 |
| PL | 0.997 | 0.994 | 1.000 | 0.994 | 0.971 |
| ZC | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| ZW | 0.993 | 0.983 | 0.986 | 0.993 | 0.997 |
| ZS | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| ZM | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| ZL | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| HE | 1.000 | 0.996 | 0.996 | 0.996 | 1.000 |
| LE | 1.000 | 1.000 | 1.000 | 1.000 | 0.996 |
| MBT | 0.995 | 1.000 | 1.000 | 1.000 | 0.987 |
| MET | 0.913 | 1.000 | 0.995 | 0.918 | 0.910 |

## Failures and unresolved symbols

- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MCL.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2019-05-01", "end": "2019-06-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MCL.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2019-06-01", "end": "2019-07-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MCL.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2019-07-01", "end": "2019-08-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MCL.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2019-08-01", "end": "2019-09-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MCL.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2019-09-01", "end": "2019-10-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MCL.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2019-11-01", "end": "2019-12-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MCL.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2019-10-01", "end": "2019-11-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MCL.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2019-12-01", "end": "2020-01-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MCL.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2020-02-01", "end": "2020-03-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MCL.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2020-01-01", "end": "2020-02-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MCL.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2020-03-01", "end": "2020-04-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MCL.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2020-04-01", "end": "2020-05-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MCL.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2020-06-01", "end": "2020-07-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MCL.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2020-05-01", "end": "2020-06-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MCL.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2020-08-01", "end": "2020-09-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MCL.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2020-09-01", "end": "2020-10-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MCL.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2020-07-01", "end": "2020-08-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MCL.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2020-11-01", "end": "2020-12-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MCL.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2020-10-01", "end": "2020-11-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MCL.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2021-01-01", "end": "2021-02-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MCL.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2020-12-01", "end": "2021-01-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MCL.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2021-02-01", "end": "2021-03-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MCL.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2021-04-01", "end": "2021-05-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MCL.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2021-05-01", "end": "2021-06-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MCL.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2021-03-01", "end": "2021-04-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MNG.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2020-02-01", "end": "2020-03-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MNG.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2020-03-01", "end": "2020-04-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MNG.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2020-04-01", "end": "2020-05-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MNG.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2020-07-01", "end": "2020-08-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MNG.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2020-01-01", "end": "2020-02-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MNG.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2020-05-01", "end": "2020-06-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MNG.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2020-08-01", "end": "2020-09-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MNG.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2020-10-01", "end": "2020-11-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MNG.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2020-11-01", "end": "2020-12-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MNG.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2020-12-01", "end": "2021-01-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MNG.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2021-02-01", "end": "2021-03-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MNG.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2021-01-01", "end": "2021-02-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MNG.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2021-03-01", "end": "2021-04-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MNG.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2021-04-01", "end": "2021-05-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MNG.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2021-05-01", "end": "2021-06-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MNG.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2020-06-01", "end": "2020-07-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MNG.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2020-09-01", "end": "2020-10-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MNG.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2021-07-01", "end": "2021-08-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MNG.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2021-08-01", "end": "2021-09-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MNG.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2021-06-01", "end": "2021-07-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MNG.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2021-09-01", "end": "2021-10-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MNG.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2021-11-01", "end": "2021-12-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MNG.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2021-12-01", "end": "2022-01-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MNG.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2022-02-01", "end": "2022-03-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MNG.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2022-01-01", "end": "2022-02-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MNG.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2022-03-01", "end": "2022-04-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MNG.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2022-04-01", "end": "2022-05-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MNG.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2022-05-01", "end": "2022-06-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MNG.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2022-06-01", "end": "2022-07-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MNG.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2022-08-01", "end": "2022-09-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MNG.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2022-07-01", "end": "2022-08-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MNG.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2022-09-01", "end": "2022-10-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MNG.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2022-11-01", "end": "2022-12-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MNG.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2021-10-01", "end": "2021-11-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MNG.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2022-12-01", "end": "2023-01-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MNG.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2023-02-01", "end": "2023-03-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MNG.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2023-04-01", "end": "2023-05-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MNG.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2023-03-01", "end": "2023-04-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MNG.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2022-10-01", "end": "2022-11-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MNG.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2023-05-01", "end": "2023-06-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MNG.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2023-06-01", "end": "2023-07-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MNG.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2023-01-01", "end": "2023-02-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MNG.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2023-08-01", "end": "2023-09-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MNG.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2023-09-01", "end": "2023-10-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MNG.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2023-07-01", "end": "2023-08-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MHG.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2019-05-01", "end": "2019-06-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MHG.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2019-06-01", "end": "2019-07-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MHG.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2019-07-01", "end": "2019-08-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MHG.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2019-08-01", "end": "2019-09-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MHG.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2019-11-01", "end": "2019-12-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MHG.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2019-09-01", "end": "2019-10-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MHG.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2019-12-01", "end": "2020-01-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MHG.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2019-10-01", "end": "2019-11-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MHG.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2020-01-01", "end": "2020-02-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MHG.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2020-03-01", "end": "2020-04-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MHG.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2020-02-01", "end": "2020-03-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MHG.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2020-06-01", "end": "2020-07-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MHG.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2020-05-01", "end": "2020-06-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MHG.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2020-07-01", "end": "2020-08-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MHG.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2020-10-01", "end": "2020-11-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MHG.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2020-09-01", "end": "2020-10-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MHG.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2020-11-01", "end": "2020-12-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MHG.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2020-12-01", "end": "2021-01-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MHG.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2020-08-01", "end": "2020-09-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MHG.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2021-02-01", "end": "2021-03-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MHG.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2021-01-01", "end": "2021-02-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MHG.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2020-04-01", "end": "2020-05-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MHG.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2021-05-01", "end": "2021-06-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MHG.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2021-07-01", "end": "2021-08-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MHG.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2021-04-01", "end": "2021-05-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MHG.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2021-08-01", "end": "2021-09-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MHG.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2021-10-01", "end": "2021-11-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MHG.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2021-11-01", "end": "2021-12-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MHG.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2021-03-01", "end": "2021-04-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MHG.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2022-01-01", "end": "2022-02-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MHG.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2021-12-01", "end": "2022-01-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MHG.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2022-02-01", "end": "2022-03-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MHG.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2022-03-01", "end": "2022-04-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MHG.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2021-06-01", "end": "2021-07-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MHG.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2021-09-01", "end": "2021-10-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MBT.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2019-05-01", "end": "2019-06-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MBT.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2019-06-01", "end": "2019-07-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MBT.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2019-09-01", "end": "2019-10-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MBT.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2019-08-01", "end": "2019-09-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MBT.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2019-07-01", "end": "2019-08-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MBT.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2019-10-01", "end": "2019-11-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MBT.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2020-01-01", "end": "2020-02-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MBT.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2020-03-01", "end": "2020-04-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MBT.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2020-02-01", "end": "2020-03-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MBT.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2019-12-01", "end": "2020-01-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MBT.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2020-04-01", "end": "2020-05-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MBT.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2020-05-01", "end": "2020-06-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MBT.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2020-06-01", "end": "2020-07-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MBT.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2019-11-01", "end": "2019-12-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MBT.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2020-08-01", "end": "2020-09-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MBT.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2020-10-01", "end": "2020-11-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MBT.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2020-09-01", "end": "2020-10-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MBT.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2020-12-01", "end": "2021-01-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MBT.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2020-11-01", "end": "2020-12-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MBT.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2021-02-01", "end": "2021-03-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MBT.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2021-01-01", "end": "2021-02-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MBT.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2021-03-01", "end": "2021-04-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MBT.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2020-07-01", "end": "2020-08-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MET.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2019-05-01", "end": "2019-06-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MET.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2019-06-01", "end": "2019-07-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MET.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2019-08-01", "end": "2019-09-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MET.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2019-07-01", "end": "2019-08-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MET.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2019-09-01", "end": "2019-10-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MET.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2019-11-01", "end": "2019-12-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MET.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2020-01-01", "end": "2020-02-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MET.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2019-12-01", "end": "2020-01-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MET.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2020-02-01", "end": "2020-03-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MET.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2019-10-01", "end": "2019-11-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MET.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2020-04-01", "end": "2020-05-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MET.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2020-06-01", "end": "2020-07-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MET.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2020-08-01", "end": "2020-09-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MET.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2020-05-01", "end": "2020-06-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MET.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2020-07-01", "end": "2020-08-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MET.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2020-10-01", "end": "2020-11-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MET.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2020-09-01", "end": "2020-10-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MET.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2021-01-01", "end": "2021-02-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MET.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2021-02-01", "end": "2021-03-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MET.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2021-03-01", "end": "2021-04-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MET.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2020-11-01", "end": "2020-12-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MET.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2021-04-01", "end": "2021-05-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MET.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2021-06-01", "end": "2021-07-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MET.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2021-05-01", "end": "2021-06-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MET.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2021-07-01", "end": "2021-08-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MET.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2021-08-01", "end": "2021-09-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MET.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2021-10-01", "end": "2021-11-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MET.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2021-09-01", "end": "2021-10-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MET.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2020-03-01", "end": "2020-04-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- quote failed: `{"dataset": "GLBX.MDP3", "symbols": ["MET.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2020-12-01", "end": "2021-01-01"}`: quote failed: BentoClientError: 422 symbology_invalid_request
None of the symbols could be resolved
documentation: https://databento.com/docs/api-reference-historical/basics/symbology
- no unresolved symbols
