# Stage E.16 Task 3: release types touching an H fill minute

From the frozen release calendar alone (reports/stage_e2b_release_calendar.json, sha256 839f2437bedbeb7b3423d7058a9955a0d4ccd1aebc4b01c62be624ab11d7bcb8, 1771 rows 2019-05-01..2024-02-29). A fill at f is touched when r <= f < r + 30 min (D8 event cost) for a release r concerning the product (price-path or vehicle root); `guard` counts fills inside r <= f < r + 2 min (D9.5a). Fill minutes: H1 S-30 and S, H4 O+1 and S-31 (every trade date), H2 the decision minute on d5 and S on dL, H3 S on t-3, t, t+5 (kept windows), and every calendar date's 23:59 and 00:00 UTC bar of NQ, ZN, ZT, ZF, ZB (a superset of the roll fills). Settlement minutes from /home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e16_settlement.json.

| type | event fills | guard fills | tests | products | CT clock times | rows before 2019-05 | fallback applies |
|---|---|---|---|---|---|---|---|
| FOMC | 874 | 190 | H1, H4 | 6A, 6B, 6C, 6E, 6J, 6N, 6S, CL, HE, LE, NG, TN, UB, ZB, ZC, ZF, ZL, ZM, ZN, ZS, ZT, ZW | 13:00 | yes | no |

Types that never touch an H fill minute: API_WSB, CPI, CROP, CROP_ANNUAL, CROP_PROGRESS, G17, ISM_SERVICES, NFP, NGS, PPI, TREASURY_AUCTION, WASDE, WPSR.

Examples (first three per type):

- FOMC: H4 ZT 2019-05-01 fill 18:29Z; H4 ZT 2019-06-19 fill 18:29Z; H4 ZT 2019-07-31 fill 18:29Z
