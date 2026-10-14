# Stage E.21: calendar-only counts (no bar row read)

Written 2026-10-14T03:50:38-07:00. Inputs: calendars, the settlement table, the windows, the release rules and each store's roll metadata (preflight, no row). A required bar is assumed present inside the session; missing bars inside it: 0.

## Rebalance dates (T1, T2) per root

| Root | Window start | Months | Rebalance dates | Moved earlier | No eligible date |
|---|---|---|---|---|---|
| NG | 2010-07-01 | 164 | 164 | 5 | 0 |
| NQ | 2010-07-01 | 164 | 164 | 4 | 0 |
| ZN | 2010-07-01 | 164 | 164 | 55 | 0 |
| 6E | 2010-07-01 | 164 | 164 | 8 | 0 |
| GC | 2010-07-01 | 164 | 164 | 65 | 0 |
| ZC | 2010-07-01 | 164 | 162 | 19 | 2 |
| ZT | 2010-07-01 | 164 | 164 | 54 | 0 |
| ZF | 2010-07-01 | 164 | 164 | 54 | 0 |
| ZB | 2010-07-01 | 164 | 164 | 54 | 0 |
| UB | 2010-07-01 | 164 | 164 | 54 | 0 |
| TN | 2016-01-11 | 98 | 98 | 31 | 0 |
| CL | 2010-07-01 | 164 | 164 | 5 | 0 |
| ZL | 2010-07-01 | 164 | 162 | 11 | 2 |
| ZS | 2010-07-01 | 164 | 164 | 15 | 0 |
| RTY | 2017-07-10 | 80 | 80 | 2 | 0 |
| HE | 2017-07-01 | 80 | 80 | 4 | 0 |
| LE | 2014-12-15 | 111 | 111 | 6 | 0 |

Skipped later dates by reason, per root:

- NG: moved by 1 trade date(s) 2, moved by 2 trade date(s) 3, moved earlier 5, no 1-month reference 1, no 12-month reference 12, no 3-month reference 3, skipped date: early halt 8
- NQ: moved by 1 trade date(s) 1, moved by 2 trade date(s) 3, moved earlier 4, no 1-month reference 1, no 12-month reference 12, no 3-month reference 3, skipped date: early halt 7
- ZN: moved by 1 trade date(s) 19, moved by 2 trade date(s) 22, moved by 3 trade date(s) 12, moved by 4 trade date(s) 1, moved by 5 trade date(s) 1, moved earlier 55, no 1-month reference 1, no 12-month reference 12, no 3-month reference 3, skipped date: early halt 9, skipped date: roll blackout 99
- 6E: moved by 1 trade date(s) 5, moved by 2 trade date(s) 3, moved earlier 8, no 1-month reference 1, no 12-month reference 12, no 3-month reference 3, skipped date: early halt 11
- GC: moved by 1 trade date(s) 1, moved by 2 trade date(s) 41, moved by 3 trade date(s) 20, moved by 4 trade date(s) 3, moved earlier 65, no 1-month reference 1, no 12-month reference 12, no 3-month reference 3, skipped date: early halt 8, skipped date: roll blackout 147
- ZC: moved by 1 trade date(s) 2, moved by 2 trade date(s) 1, moved by 3 trade date(s) 8, moved by 4 trade date(s) 7, moved by 5 trade date(s) 1, moved earlier 19, no 1-month reference 1, no 12-month reference 11, no 3-month reference 3, no eligible rebalance date 2, skipped date: early halt 5, skipped date: roll blackout 56
- ZT: moved by 1 trade date(s) 14, moved by 2 trade date(s) 23, moved by 3 trade date(s) 15, moved by 4 trade date(s) 1, moved by 5 trade date(s) 1, moved earlier 54, no 1-month reference 1, no 12-month reference 12, no 3-month reference 3, skipped date: early halt 8, skipped date: roll blackout 106
- ZF: moved by 1 trade date(s) 13, moved by 2 trade date(s) 27, moved by 3 trade date(s) 12, moved by 4 trade date(s) 1, moved by 5 trade date(s) 1, moved earlier 54, no 1-month reference 1, no 12-month reference 12, no 3-month reference 3, skipped date: early halt 8, skipped date: roll blackout 104
- ZB: moved by 1 trade date(s) 18, moved by 2 trade date(s) 27, moved by 3 trade date(s) 8, moved by 4 trade date(s) 1, moved earlier 54, no 1-month reference 1, no 12-month reference 12, no 3-month reference 3, skipped date: early halt 7, skipped date: roll blackout 93
- UB: moved by 1 trade date(s) 18, moved by 2 trade date(s) 24, moved by 3 trade date(s) 10, moved by 4 trade date(s) 1, moved by 5 trade date(s) 1, moved earlier 54, no 1-month reference 1, no 12-month reference 12, no 3-month reference 3, skipped date: early halt 9, skipped date: roll blackout 96
- TN: moved by 1 trade date(s) 8, moved by 2 trade date(s) 14, moved by 3 trade date(s) 8, moved by 4 trade date(s) 1, moved earlier 31, no 1-month reference 1, no 12-month reference 12, no 3-month reference 3, skipped date: early halt 4, skipped date: roll blackout 60
- CL: moved by 1 trade date(s) 2, moved by 2 trade date(s) 3, moved earlier 5, no 1-month reference 1, no 12-month reference 12, no 3-month reference 3, skipped date: early halt 8
- ZL: moved by 1 trade date(s) 5, moved by 2 trade date(s) 3, moved by 3 trade date(s) 1, moved by 4 trade date(s) 1, moved by 5 trade date(s) 1, moved earlier 11, no 1-month reference 1, no 12-month reference 12, no 3-month reference 3, no eligible rebalance date 2, skipped date: early halt 4, skipped date: roll blackout 19
- ZS: moved by 1 trade date(s) 4, moved by 2 trade date(s) 3, moved by 3 trade date(s) 6, moved by 4 trade date(s) 1, moved by 5 trade date(s) 1, moved earlier 15, no 1-month reference 1, no 12-month reference 12, no 3-month reference 3, skipped date: early halt 4, skipped date: roll blackout 33
- RTY: moved by 1 trade date(s) 1, moved by 2 trade date(s) 1, moved earlier 2, no 1-month reference 1, no 12-month reference 12, no 3-month reference 3, skipped date: early halt 3
- HE: moved by 1 trade date(s) 4, moved earlier 4, no 1-month reference 1, no 12-month reference 12, no 3-month reference 3, skipped date: early halt 1, skipped date: fill guard 3
- LE: moved by 1 trade date(s) 6, moved earlier 6, no 1-month reference 1, no 12-month reference 12, no 3-month reference 3, skipped date: early halt 2, skipped date: fill guard 3, skipped date: unsourced calendar date 1

## T3 units (NQ, RTY)

- NQ: 164 months; entry: early halt 2, exit: early halt 3, sigma warm-up (calendar estimate) 3, store boundary 1, traded (calendar estimate) 154, window end 1
- RTY: 80 months; entry: early halt 1, exit: early halt 1, sigma warm-up (calendar estimate) 3, store boundary 1, traded (calendar estimate) 73, window end 1

## S_M (calendar-defined divisor)

164 months; values [13, 14, 15, 17]. First month with each value: 13: 2011-07, 14: 2015-12, 15: 2017-01, 17: 2018-07

Full per-month values in the JSON (S_M, T3.S_u).
