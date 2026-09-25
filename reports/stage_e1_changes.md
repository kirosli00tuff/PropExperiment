# Stage E.1 Task 1: every edit applying the user's decisions U1 to U9

Lead: Opus 5.5 (max). Applied 2026-09-24 by one script (exact-string replacements, each checked
to match the stated number of times in every target before anything was written; cluster edits
applied to the cluster file and to the same cluster's section of reports/stage_e0_catalog.md).
The decisions are quoted in docs/DECISIONS.md (entry of 2026-09-24) and in the stage prompt
(docs/prompts/STAGE_E.1.md, Task 1).

## Decision coverage

| Decision | Edits | Or: no edit needed, and why |
|---|---|---|
| U1 | D-02, D-03, D-04, D-05, K7-00 |  |
| U2 | D-01, D-02, D-03, D-05, D-15, D-16, D-21, D-22, D-28, D-30, K5-00, K5-10, K5-11, K5-12, K5-14, K5-15, K5-16, K5-17, K5-18, K5-19, K5-20, K5-21, K5-22, K5-24, K5-25, K5-26, K5-27, K5-28, K5-29, K5-30, K5-31, K5-34, A-01, JSON K5-cp1-01, JSON K5-cp2-01, JSON K5-cp3-01, JSON K5-ovr-01, JSON clusters[K5], JSON exposure_table[platinum], JSON totals, JSON projected_N | D2's rule text names no platinum contract (no edit there); D13's list is edited (D-28, D-30). |
| U3 | D-27, K1-00, K2-00, K8-00 |  |
| U4 | D-10, D-19, D-25, D-26, D-28, D-29, D-31, D-33 |  |
| U5 | D-32 | The account registry itself is code (data/config.py, Task 5), not a frozen file. |
| U6 | D-09, D-12, D-13, D-23, D-24, D-25, D-26, D-34, N-01, K1-00, K1-01, K2-00, K2-01, K3-00, K3-01, K4-00, K4-01, K5-00, K5-01, K6-00, K6-01, K7-00, K7-01, K8-00, K8-01, K1-02, K2-02, K3-02, K4-02, K5-02, K6-02, K7-02, K1-03, K3-03, K4-03, K5-03, K6-03, K7-03, K8-03, K2-03, K8-04, K5-13, K5-14, K5-31, K5-32, A-01, JSON K1-ml-01, JSON K2-ml-01, JSON K3-ml-01, JSON K4-ml-01, JSON K5-ml-01, JSON K6-ml-01, JSON K7-ml-01, JSON K8-ml-01, JSON clusters[K1], JSON clusters[K2], JSON clusters[K3], JSON clusters[K4], JSON clusters[K5], JSON clusters[K6], JSON clusters[K7], JSON clusters[K8], JSON exposure_table[K1 Nasdaq-100], JSON exposure_table[K2 ZN], JSON exposure_table[K3 EUR], JSON exposure_table[K4 crude], JSON exposure_table[K4 gas], JSON exposure_table[K5 gold], JSON exposure_table[K6 ZC], JSON exposure_table[K7 bitcoin], JSON exposure_table[K8 CAD], JSON totals, JSON projected_N |  |
| U7 | D-06, D-20, K3-00 |  |
| U8 | D-07, D-08, D-11, D-14, D-17, D-18, D-19 | D9, D10, D11 and D14 carry no 'User decides' line; accepted as drafted, no edit. Every member's parameters stay as E.0's rulings left them (no member edit). |
| U9 | K5-00, K5-14, K5-23, K5-31, K5-32, K5-33, K2-10, K2-11 | R-28's VXN item (K1-vxnband-01, K1-ml-01): E.2 confirms as written, no edit. R-28's K6 ZL tick item: the text is right, no edit. R-28's K3 CP2 item: no pre-amendment note was found in K3's CP2 entry (grep for 'latest-entry', 'no latest', 'unbounded' in reports/stage_e0_catalog_K3.md returned nothing), no edit. |
| U1-U9 (record) | D-00 | header note recording that the decisions were applied |

## Items found while applying the decisions, NOT applied (no decision covers them)

- F-1 (count). D1's table has 32 IN rows before U2, not 31 (K1 3, K2 6, K3 7, K4 4, K5 4, K6 7, K7 1); E.0's 96 port trials are 3 x 32. After U2 the count is 31, not the stage prompt's 30. The D1 result line now states 31 with a count note (D-02); no other text depends on the number. For the user.
- F-2 (fact). D13 says the largest single request is "one mbp-1 day of MNQ, about $2.7". E.0's own quote lines give MNQ 2026-02-11 $4.14 and MNQ 2025-11-12 $3.41, above the $3.00 request cap. Left unedited (a factual correction is not among U1-U9); the purchase path splits such requests into contiguous time pieces under the cap (reports/stage_e1_STATE.md S-2). For the auditor's grading.
- F-3 (R-04 carried item). The E.0 ruling on R-04 said "E.1 records every member's source windows before hashing". No decision among U1-U9 asks for it, and doing it would edit members. Not done. D7's accepted rule (U8) already treats a member without a recorded window as source-overlap, so the freeze stays conservative without it. For the user.
- F-4 (R-24 carried item). "K4-ovr-01 and K5-ovr-01 must carry one rule text; E.1 checks it before hashing". The lead's read-only check is in reports/stage_e1_freeze_rulings.md; no member text is changed by Task 1.
- F-5 (R-15 carried item). K2-aucpost-01's 5-minute lag rests on an unquoted passage; carried to the user, no edit.
- F-6 (D15 references). After U6, four non-ML members still cite D15 in their text: K4-ovr-01, K5-ovr-01 and K6-ovr-01 (excluded) cite "D15.4 B4", and K8-flight-01 cites "D15's B4 feature", each only as the reason for the fixed literal 20 (trailing trade dates); some common-convention sections cite D15.3 for the engine's next-open fill, which is the engine's own convention. D15's text stays in the design under its SUPERSEDED banner, so these references still resolve, and no member depends on a D15 rule. No edit.
- F-7 (R-24 check, read-only). K4-ovr-01 and K5-ovr-01 carry the same rule text: decile threshold over a 20-trade-date trailing reference, entry on the signal bar, exit at t + 59 (59-minute hold); they differ only in each product's decision clock (D6 session table). Consistent; no edit.

## Edits to the markdown files

### D-00 (U1-U9 (record)): file header

Files: docs/STAGE_E_DESIGN.md. Matches replaced per file: 1.

Old:

````text
the user changes) and buys the data. Every answer below is a proposal: the rule, the reasoning,
the alternatives considered, and what the user must decide.
````

New:

````text
the user changes) and buys the data. Every answer below is a proposal: the rule, the reasoning,
the alternatives considered, and what the user must decide.

**Stage E.1 (2026-09-24) applied the user's decisions U1 to U9 (docs/DECISIONS.md, entry of
2026-09-24) to this draft.** Every edit is logged in reports/stage_e1_changes.md (old text, new
text, decision). Changed passages carry a bracketed "[U#, 2026-09-24 ...]" note; superseded text
stays visible, struck through or bracketed, as in Stage E.0.
````

### D-01 (U2): D1 table, platinum row

Files: docs/STAGE_E_DESIGN.md. Matches replaced per file: 1.

Old:

````text
| K5 | platinum | PL 22,360 | yes | 0.991 | yes | IN | PL |
````

New:

````text
| K5 | platinum | PL 22,360 | yes | 0.991 | yes | ~~IN~~ **OUT** (user decision U2, 2026-09-24: Topstep's 50K volatility cap for PL is 0 and PL has no micro, so the bot cannot trade it) | — |
````

### D-02 (U1, U2): D1 result line

Files: docs/STAGE_E_DESIGN.md. Matches replaced per file: 1.

Old:

````text
**Result: 31 traded exposures, S&P 500 as a leg only, 3 exposures out (NKD, 6M, MET).** Every
````

New:

````text
**Result, after the user's decisions of 2026-09-24: 31 traded exposures, S&P 500 as a leg only,
4 exposures out: NKD, 6M and MET by the rule, confirmed by the user (U1), and platinum by the
user's decision (U2).** [Stage E.1 count note: the E.0 draft read "31 traded exposures, S&P 500
as a leg only, 3 exposures out", but the table above has 32 IN rows before U2 (K1 3, K2 6, K3 7,
K4 4, K5 4, K6 7, K7 1; E.0's 96 port trials are 3 x 32), so E.0's 31 was a miscount; after
platinum's removal the table has 31. The stage prompt's "30 traded exposures" repeats E.0's
miscount; the table rows govern and the discrepancy is logged for the user.] Every
````

### D-03 (U1, U2): D1 result paragraph, signal legs

Files: docs/STAGE_E_DESIGN.md. Matches replaced per file: 1.

Old:

````text
the member's own window. K7 is left with one traded exposure (bitcoin).
````

New:

````text
the member's own window (U1: this holds for NKD, 6M and MET). Platinum may not serve as a signal
leg either (U2): nothing in the catalog needs it. K7 is left with one traded exposure (bitcoin).
````

### D-04 (U1): D1, results for the user

Files: docs/STAGE_E_DESIGN.md. Matches replaced per file: 1.

Old:

````text
applied as written; the user may re-admit either.
````

New:

````text
applied as written; the user may re-admit either. [U1, 2026-09-24: the user read the reasons and
confirmed D1 as the rule gives it; NKD, 6M and MET stay OUT.]
````

### D-05 (U1, U2): D1, User decides

Files: docs/STAGE_E_DESIGN.md. Matches replaced per file: 1.

Old:

````text
dropped by (a) only because no public figure was found should be re-checked by hand.
````

New:

````text
dropped by (a) only because no public figure was found should be re-checked by hand.
[Decided 2026-09-24: U1 (D1 as the rule gives it; no exposure failed (a) for lack of a figure,
since the 2026 January-August ADV exists for all 50 products) and U2 (platinum OUT).]
````

### D-06 (U7): D2 rule, new bullet on M6E and M6A

Files: docs/STAGE_E_DESIGN.md. Matches replaced per file: 1.

Old:

````text
  value (same underlying, same quotes up to the multiplier), declared per exposure before any
  confirmation read (D4).
````

New:

````text
  value (same underlying, same quotes up to the multiplier), declared per exposure before any
  confirmation read (D4).
- Starred micros M6E and M6A (user decision U7, 2026-09-24): not D2 candidates until Topstep
  answers the user's support email about their star (drafted 2026-09-24, not yet answered;
  D9.8). If Topstep clears them before a cluster's screening session, a vehicle amendment may be
  written before that session reads any research-window bar, and the amendment is logged in
  docs/DECISIONS.md.
````

### D-07 (U8): D2, User decides

Files: docs/STAGE_E_DESIGN.md. Matches replaced per file: 1.

Old:

````text
**User decides:** the risk target (MES 2 micros); the band [0.5, 2.0]; whether exposures above the
band (probably ZB and UB) are dropped or traded at 1 contract with their own funnel-derived ε.
````

New:

````text
**User decides:** the risk target (MES 2 micros); the band [0.5, 2.0]; whether exposures above the
band (probably ZB and UB) are dropped or traded at 1 contract with their own funnel-derived ε.
[U8, 2026-09-24: accepted as drafted (the risk target, the band and the 1-lot cap). As drafted, an
exposure with no candidate is not traded in Stage E.]
````

### D-08 (U8): D3, User decides

Files: docs/STAGE_E_DESIGN.md. Matches replaced per file: 1.

Old:

````text
**User decides:** whether to accept min(translated, funnel) or the funnel figure alone.
````

New:

````text
**User decides:** whether to accept min(translated, funnel) or the funnel figure alone.
[U8, 2026-09-24: accepted as drafted: min(translated, funnel-derived), with the no-passing-cell rule.]
````

### D-09 (U6): D4, research window uses

Files: docs/STAGE_E_DESIGN.md. Matches replaced per file: 1.

Old:

````text
- Research window (screening, sizing inputs, cost calibration, ML tuning): trade dates
````

New:

````text
- Research window (screening, sizing inputs, cost calibration, ~~ML tuning~~ [U6, 2026-09-24:
  superseded; the ML route's data partition is set in docs/STAGE_E_ML_DESIGN.md]): trade dates
````

### D-10 (U4): D4, holdout-2 sentence

Files: docs/STAGE_E_DESIGN.md. Matches replaced per file: 1.

Old:

````text
- Holdout-2: trade dates 2024-04-01..2025-03-31, bought in E.1 and sealed on arrival exactly as
  MES's was
````

New:

````text
- Holdout-2: trade dates 2024-04-01..2025-03-31, ~~bought in E.1~~ bought per cluster in step 2
  (D13), just before that cluster's confirmation session [U4, 2026-09-24], and sealed on arrival exactly as
  MES's was
````

### D-11 (U8): D4, User decides

Files: docs/STAGE_E_DESIGN.md. Matches replaced per file: 1.

Old:

````text
**User decides:** whether holdout-1 for new products is left unbought (proposed) or bought and
sealed like MES's; whether full-size bars may stand in for a short-history micro.
````

New:

````text
**User decides:** whether holdout-1 for new products is left unbought (proposed) or bought and
sealed like MES's; whether full-size bars may stand in for a short-history micro.
[U8, 2026-09-24: accepted as drafted: holdout-1 not bought for new products; full-size bars as a
price path only if the power check fails and the user agrees.]
````

### D-12 (U6): D5, the ML member's Tier A sentence

Files: docs/STAGE_E_DESIGN.md. Matches replaced per file: 1.

Old:

````text
  passes the cluster's screening session's pre-declared screen on the research window. The ML member
  takes the same screen, on its nested outer-fold estimate (D15.5), and joins Tier A only if it passes
  (ruling on review R-01, 2026-09-24: one reading, D15.10's).
````

New:

````text
  passes the cluster's screening session's pre-declared screen on the research window. The ML member
  takes the same screen, on its nested outer-fold estimate (D15.5), and joins Tier A only if it passes
  (ruling on review R-01, 2026-09-24: one reading, D15.10's). [U6, 2026-09-24: superseded; the
  catalog has no ML member.]
````

### D-13 (U6): D5, program accounting

Files: docs/STAGE_E_DESIGN.md. Matches replaced per file: 1.

Old:

````text
  and grid point adds to it, section D15 for the ML members), DSR at N, PBO, and the per-cluster
  and program totals.
````

New:

````text
  and grid point adds to it, ~~section D15 for the ML members~~ [U6: the ML route counts its
  trials as docs/STAGE_E_ML_DESIGN.md sets out]), DSR at N, PBO, and the per-cluster
  and program totals.
- **Stage E.1 recount (after U2 and U6, 2026-09-24), from reports/stage_e0_catalog.json.** Active
  members / confirmation trials per cluster: K1 5 / 11; K2 8 / 44; K3 9 / 31; K4 8 / 19; K5 7 / 16;
  K6 7 / 27; K7 6 / 6; K8 3 / 4. **Total: 53 members, 158 trials** (93 port + 65 new + 0 ML).
  Arithmetic: E.0 left 61 members and 170 trials. U6 excludes the eight ML members (-8 members,
  -8 trials). U2 removes platinum from K5-cp1-01, K5-cp2-01, K5-cp3-01 and K5-ovr-01 (-4 trials;
  no member is lost, since none traded platinum alone). 61 - 8 = 53 members; 170 - 8 - 4 = 158
  trials. **Projected cumulative N = 58 + 158 = 216** (E.0: 228). The ML route's own trials are
  not in these figures (docs/STAGE_E_ML_DESIGN.md).
````

### D-14 (U8): D5, User decides

Files: docs/STAGE_E_DESIGN.md. Matches replaced per file: 1.

Old:

````text
**User decides:** the alpha split (equal over active clusters); the screen (t >= 1.0 on the
research window).
````

New:

````text
**User decides:** the alpha split (equal over active clusters); the screen (t >= 1.0 on the
research window). [U8, 2026-09-24: accepted as drafted.]
````

### D-15 (U2): D6 session table, platinum row

Files: docs/STAGE_E_DESIGN.md. Matches replaced per file: 1.

Old:

````text
| platinum (PL) | 07:20 | 12:05 | 15:08 |
````

New:

````text
| ~~platinum (PL)~~ [OUT, U2, 2026-09-24] | ~~07:20~~ | ~~12:05~~ | ~~15:08~~ |
````

### D-16 (U2): D6, count

Files: docs/STAGE_E_DESIGN.md. Matches replaced per file: 1.

Old:

````text
**Count.** Three trials per traded exposure. With about 30 traded exposures, about 90 port trials.
````

New:

````text
**Count.** Three trials per traded exposure. With about 30 traded exposures, about 90 port trials.
[Stage E.1 count after U2: 31 traded exposures, 93 port trials.]
````

### D-17 (U8): D6, User decides

Files: docs/STAGE_E_DESIGN.md. Matches replaced per file: 1.

Old:

````text
**User decides:** the three families; whether CP1 should also carry the (b) form.
````

New:

````text
**User decides:** the three families; whether CP1 should also carry the (b) form.
[U8, 2026-09-24: accepted as drafted: the three ports; CP1 in the (a) form only.]
````

### D-18 (U8): D7, User decides

Files: docs/STAGE_E_DESIGN.md. Matches replaced per file: 1.

Old:

````text
**User decides:** the pre-declared "inconclusive by design" exception; the per-cluster unit.
````

New:

````text
**User decides:** the pre-declared "inconclusive by design" exception; the per-cluster unit.
[U8, 2026-09-24: accepted as drafted, with the "source-overlap" rule.]
````

### D-19 (U8, U4): D8, User decides

Files: docs/STAGE_E_DESIGN.md. Matches replaced per file: 1.

Old:

````text
**User decides:** mbp-1 alone or mbp-1 plus tbbo; five dates or more.
````

New:

````text
**User decides:** mbp-1 alone or mbp-1 plus tbbo; five dates or more.
[U8 and U4, 2026-09-24: mbp-1 only, the five dates; no tbbo is bought.]
````

### D-20 (U7): D9.8 starred products

Files: docs/STAGE_E_DESIGN.md. Matches replaced per file: 1.

Old:

````text
   unresolved at E.1 is NOT a D2 candidate unless the user clears it; EUR and AUD then trade 6E and 6A
   at one contract.
````

New:

````text
   unresolved at E.1 is NOT a D2 candidate unless the user clears it; EUR and AUD then trade 6E and 6A
   at one contract. [U7, 2026-09-24: M6E and M6A stay non-candidates for D2 until Topstep answers
   the user's support email (drafted 2026-09-24, not yet answered). If Topstep clears them before a
   cluster's screening session, a vehicle amendment may be written before that session reads any
   research-window bar, and the amendment is logged in docs/DECISIONS.md.]
````

### D-21 (U2): D9.11 volatility caps, platinum

Files: docs/STAGE_E_DESIGN.md. Matches replaced per file: 1.

Old:

````text
   whenever they are candidates, and platinum (no micro) is flagged "may be suspended in volatile
   periods" for the user.
````

New:

````text
   whenever they are candidates, and platinum (no micro) is flagged "may be suspended in volatile
   periods" for the user. [U2, 2026-09-24: platinum is OUT for this reason: its 50K cap is 0 and it
   has no micro, so the bot cannot trade it. Topstep's quoted text above is kept as the source.]
````

### D-22 (U2): D9.12 CPI window, encoded list

Files: docs/STAGE_E_DESIGN.md. Matches replaced per file: 1.

Old:

````text
   position in [CPI - 5 min, CPI + 5 min] on NQ, RTY, YM, GC, SI, HG or PL (an entry whose fill would
````

New:

````text
   position in [CPI - 5 min, CPI + 5 min] on NQ, RTY, YM, GC, SI or HG (~~or PL~~: OUT, U2) (an entry whose fill would
````

### D-23 (U6): D9.9 unfair technology

Files: docs/STAGE_E_DESIGN.md. Matches replaced per file: 1.

Old:

````text
   ProjectX API, subject to standard platform rules" [F10.4]); the ML members are frozen models
   making at most 20 decisions a day. Flagged for the user in case Topstep reads "AI" more broadly.
````

New:

````text
   ProjectX API, subject to standard platform rules" [F10.4]); the ML members are frozen models
   making at most 20 decisions a day. Flagged for the user in case Topstep reads "AI" more broadly.
   [U6, 2026-09-24: superseded; no model is deployed or makes live decisions. The Stage E ML route
   is a discovery tool whose findings become plain rules (docs/STAGE_E_ML_DESIGN.md).]
````

### D-24 (U6): D11.7

Files: docs/STAGE_E_DESIGN.md. Matches replaced per file: 1.

Old:

````text
7. **The ML pipeline** (D15), with its leakage tests, before any fit.
````

New:

````text
7. ~~**The ML pipeline** (D15), with its leakage tests, before any fit.~~ [U6, 2026-09-24:
   replaced by the build list of the Stage E ML route, docs/STAGE_E_ML_DESIGN.md, once the user
   has reviewed it.]
````

### D-25 (U4, U6): D12 table, session 3

Files: docs/STAGE_E_DESIGN.md. Matches replaced per file: 1.

Old:

````text
| 3 | E.2b build and second purchase | generalized screening runner, ML pipeline and its leakage tests (D15), canaries, freeze manifest; buy the confirmation and holdout-2 history of the chosen vehicles, sealing holdout-2 on arrival (D13 step 2) | 8-12 h | 80-120M |
````

New:

````text
| 3 | E.2b build ~~and second purchase~~ | generalized screening runner, ~~ML pipeline and its leakage tests (D15)~~ [U6: the ML route's build, docs/STAGE_E_ML_DESIGN.md], canaries, freeze manifest; ~~buy the confirmation and holdout-2 history of the chosen vehicles, sealing holdout-2 on arrival (D13 step 2)~~ [U4, 2026-09-24: step 2 is bought per cluster, just before that cluster's confirmation session] | 8-12 h | 80-120M |
````

### D-26 (U4, U6): D12 table, sessions 4-17

Files: docs/STAGE_E_DESIGN.md. Matches replaced per file: 1.

Old:

````text
| 4-17 | one screening and one confirmation session per cluster | screening: members through screen_candidate on the research window, ML tuning, Tier A/B, power check, list hashed. Confirmation: the list on the confirmation window, independent Fable check, statements |
````

New:

````text
| 4-17 | one screening and one confirmation session per cluster | screening: members through screen_candidate on the research window, ~~ML tuning~~ [U6], Tier A/B, power check, list hashed. Confirmation: [U4: first the cluster's step 2 purchase, its holdout-2 chunks sealed on arrival;] the list on the confirmation window, independent Fable check, statements |
````

### D-27 (U3): D12, cluster order

Files: docs/STAGE_E_DESIGN.md. Matches replaced per file: 1.

Old:

````text
**Cluster order, by distance from MES's drivers:** K4 energy and K5 metals first, then K2 rates, K3 FX
````

New:

````text
**Cluster order (user decision U3, 2026-09-24):** K2 rates first, then K4 energy, K5 metals, K3 FX,
K6 agriculture and livestock, K7 crypto; then K1 equity-index siblings only if the user decides,
after K7, that it is needed; K8 last (its members read other clusters' products). K1's members stay
in the frozen catalog so that a later K1 session is pre-registered. The E.0 proposal that follows is
superseded:

~~**Cluster order, by distance from MES's drivers:**~~ K4 energy and K5 metals first, then K2 rates, K3 FX
````

### D-28 (U2, U4): D13, staged purchase lead-in

Files: docs/STAGE_E_DESIGN.md. Matches replaced per file: 1.

Old:

````text
**Proposed: buy in two steps, only what the design uses.** For the 31 traded exposures (D1), leaving
out NKD, 6M, MET and ES (MES bars, already owned, serve as the S&P leg on non-holdout dates):
````

New:

````text
**Proposed: buy in two steps, only what the design uses.** For the 31 traded exposures (D1), leaving
out NKD, 6M, MET and ES (MES bars, already owned, serve as the S&P leg on non-holdout dates):
[U2 and U4, 2026-09-24: the traded exposures are the 31 of D1 after platinum's removal (see D1's
count note), and platinum is left out as well. Step 1 in E.1 is the research window of every
admissible contract of those exposures (45 contracts) plus the mbp-1 sample on the five fixed
dates, with no tbbo. Step 2 is option (b) below: each cluster's 2019-05..2025-03 history of its
chosen vehicles is bought just before that cluster's confirmation session, with its holdout-2
chunks sealed on arrival. The ML route's data needs (docs/STAGE_E_ML_DESIGN.md) are decided
separately and may pull some step 2 purchases forward. Without platinum, re-summed from E.0's
quote lines in the ledger: step 1 research window $57.28, mbp-1 $45.95 (together $103.24);
step 2 range $164.15-189.31 (platinum's history was $6.24); total without tbbo $267.38-292.54.
The table below is E.0's, with platinum.]
````

### D-29 (U4): D13 table, step 2 row

Files: docs/STAGE_E_DESIGN.md. Matches replaced per file: 1.

Old:

````text
| 2 | E.2b | 2019-05..2025-03 history
````

New:

````text
| 2 | ~~E.2b~~ per cluster, before its confirmation session (U4) | 2019-05..2025-03 history
````

### D-30 (U2): D13, per-cluster K5 figures

Files: docs/STAGE_E_DESIGN.md. Matches replaced per file: 1.

Old:

````text
$21.24-28.34 + $5.49;
````

New:

````text
$21.24-28.34 + $5.49 [without platinum (U2): $8.99 + $15.00-22.10 + $5.09];
````

### D-31 (U4): D13, caps

Files: docs/STAGE_E_DESIGN.md. Matches replaced per file: 1.

Old:

````text
prompt before any purchase (E.1: about $115, or $146 with tbbo; E.2b: the chosen vehicles' quote plus
10%).
````

New:

````text
prompt before any purchase (E.1: about $115, or $146 with tbbo; E.2b: the chosen vehicles' quote plus
10%). [U4: step 2 is per cluster, so each cluster's step 2 session is capped at its own quote plus
10%.]
````

### D-32 (U5): D13, the account

Files: docs/STAGE_E_DESIGN.md. Matches replaced per file: 1.

Old:

````text
Databento account (about $33 of credit left) needs funding. E.0 did not change any cap.
````

New:

````text
Databento account (about $33 of credit left) needs funding. E.0 did not change any cap.

**[U5, 2026-09-24: the program moves to a second Databento account.]** acct-2: $125.00 of credit,
used only by this repository; every Stage E purchase from E.1 on draws on it. acct-1: the old
account, shared with the archived MLCryptoEngine, $91.59 spent (MLCryptoEngine's ledger plus this
repository's lines before E.1); it is closed to new spend by this program. data/config.py carries
both accounts with their caps (acct-1 $120.00 with the external MLCryptoEngine ledger, acct-2
$125.00 with none), and the spend gate sums spend per account (Stage E.1 Task 5).
````

### D-33 (U4): D13, cheaper alternatives

Files: docs/STAGE_E_DESIGN.md. Matches replaced per file: 1.

Old:

````text
**Cheaper alternatives the user can choose.** (a) Skip tbbo (already the proposal). (b) Buy each
````

New:

````text
**Cheaper alternatives the user can choose.** [U4, 2026-09-24: (a) and (b) chosen; (c) not.] (a) Skip tbbo (already the proposal). (b) Buy each
````

### D-34 (U6): D15 heading

Files: docs/STAGE_E_DESIGN.md. Matches replaced per file: 1.

Old:

````text
## D15. The machine-learning member protocol (common to all eight clusters)

````

New:

````text
## D15. The machine-learning member protocol (common to all eight clusters)

> **SUPERSEDED (user decision U6, 2026-09-24).** This section no longer governs any Stage E member.
> The eight K#-ml-01 entries are excluded ("excluded: superseded by the Stage E ML route (user
> decision 2026-09-24)"), and the machine-learning work moves to a separate Stage E ML route,
> **docs/STAGE_E_ML_DESIGN.md** (a DRAFT written in Stage E.1 for the user's review; Stage E.2
> freezes it before any ML fit and before any research-window bar is read). The route's purpose,
> set by the user: ML is a strategy-discovery tool. Its findings become plain rules that are
> pre-registered and tested like any other member. No model is deployed or makes live decisions.
> The text below stays for the record.

````

### N-01 (U6): section 2, ML members

Files: docs/NULL_CRITERIA_E.md. Matches replaced per file: 1.

Old:

````text
- ML members (D15): one trial each, tested exactly like any member with its frozen model (sha256 in
  the list); the 48-configuration research-window grid is reported beside it.
````

New:

````text
- ML members (D15): one trial each, tested exactly like any member with its frozen model (sha256 in
  the list); the 48-configuration research-window grid is reported beside it. [U6, 2026-09-24:
  superseded; the catalog has no ML member. Rules found by the Stage E ML route are pre-registered
  and tested as ordinary members (docs/STAGE_E_ML_DESIGN.md).]
````

### K1-00 (U6, U3 (recount)): title banner

Files: reports/stage_e0_catalog_K1.md, reports/stage_e0_catalog.md (section K1). Matches replaced per file: 1.

Old:

````text
# Stage E.0 hypothesis catalog, cluster K1 (equity index: MNQ, NQ, M2K, RTY, MYM, YM)

````

New:

````text
# Stage E.0 hypothesis catalog, cluster K1 (equity index: MNQ, NQ, M2K, RTY, MYM, YM)

> **[Stage E.1, 2026-09-24: the user's decisions applied (docs/DECISIONS.md, U1 to U9; every edit in
> reports/stage_e1_changes.md).]** U6: K1-ml-01 is excluded: superseded by the Stage E ML route
> (user decision 2026-09-24); its text stays visible below and it adds 0 trials. U3: K1 runs only if the user decides, after K7, that it is needed; its members stay in the frozen catalog so that a later K1 session is pre-registered.
> **K1 after the decisions: 5 active members, 11 confirmation trials** (2 new + 3 core ports; 9 port + 2 new trials). Header
> and section 6 totals below are superseded where they differ.

````

### K1-01 (U6): K1-ml-01 heading

Files: reports/stage_e0_catalog_K1.md, reports/stage_e0_catalog.md (section K1). Matches replaced per file: 1.

Old:

````text
### K1-ml-01 (the ML member, D15; this entry fills only D15.10's fields)

````

New:

````text
### K1-ml-01 (the ML member, D15; this entry fills only D15.10's fields)

> **[EXCLUDED: superseded by the Stage E ML route (user decision 2026-09-24, U6). Stage E.1.
> The text below stays visible for the record. This entry is not a Stage E member and adds 0
> trials; the ML route (docs/STAGE_E_ML_DESIGN.md) is separate.]**

````

### K2-00 (U6, U3 (recount)): title banner

Files: reports/stage_e0_catalog_K2.md, reports/stage_e0_catalog.md (section K2). Matches replaced per file: 1.

Old:

````text
# Stage E.0 hypothesis catalog, cluster K2 (rates: ZT, ZF, ZN, TN, ZB, UB)

````

New:

````text
# Stage E.0 hypothesis catalog, cluster K2 (rates: ZT, ZF, ZN, TN, ZB, UB)

> **[Stage E.1, 2026-09-24: the user's decisions applied (docs/DECISIONS.md, U1 to U9; every edit in
> reports/stage_e1_changes.md).]** U6: K2-ml-01 is excluded: superseded by the Stage E ML route
> (user decision 2026-09-24); its text stays visible below and it adds 0 trials. U3: K2 is the first cluster.
> **K2 after the decisions: 8 active members, 44 confirmation trials** (5 new + 3 core ports; 18 port + 26 new trials). Header
> and section 6 totals below are superseded where they differ.

````

### K2-01 (U6): K2-ml-01 heading

Files: reports/stage_e0_catalog_K2.md, reports/stage_e0_catalog.md (section K2). Matches replaced per file: 1.

Old:

````text
### K2-ml-01 (the ML member, D15; this entry fills only D15.10's fields)

````

New:

````text
### K2-ml-01 (the ML member, D15; this entry fills only D15.10's fields)

> **[EXCLUDED: superseded by the Stage E ML route (user decision 2026-09-24, U6). Stage E.1.
> The text below stays visible for the record. This entry is not a Stage E member and adds 0
> trials; the ML route (docs/STAGE_E_ML_DESIGN.md) is separate.]**

````

### K3-00 (U6, U7 (recount)): title banner

Files: reports/stage_e0_catalog_K3.md, reports/stage_e0_catalog.md (section K3). Matches replaced per file: 1.

Old:

````text
# Stage E.0 hypothesis catalog, cluster K3 (FX: 6E, E7, M6E, 6A, M6A, 6B, M6B, 6C, 6J, 6S, 6N)

````

New:

````text
# Stage E.0 hypothesis catalog, cluster K3 (FX: 6E, E7, M6E, 6A, M6A, 6B, M6B, 6C, 6J, 6S, 6N)

> **[Stage E.1, 2026-09-24: the user's decisions applied (docs/DECISIONS.md, U1 to U9; every edit in
> reports/stage_e1_changes.md).]** U6: K3-ml-01 is excluded: superseded by the Stage E ML route
> (user decision 2026-09-24); its text stays visible below and it adds 0 trials. U7: M6E and M6A stay non-candidates for D2 until Topstep answers the user's support email (D2, D9.8).
> **K3 after the decisions: 9 active members, 31 confirmation trials** (6 new + 3 core ports; 21 port + 10 new trials). Header
> and section 6 totals below are superseded where they differ.

````

### K3-01 (U6): K3-ml-01 heading

Files: reports/stage_e0_catalog_K3.md, reports/stage_e0_catalog.md (section K3). Matches replaced per file: 1.

Old:

````text
### K3-ml-01 (the ML member, D15; this entry fills only D15.10's fields)

````

New:

````text
### K3-ml-01 (the ML member, D15; this entry fills only D15.10's fields)

> **[EXCLUDED: superseded by the Stage E ML route (user decision 2026-09-24, U6). Stage E.1.
> The text below stays visible for the record. This entry is not a Stage E member and adds 0
> trials; the ML route (docs/STAGE_E_ML_DESIGN.md) is separate.]**

````

### K4-00 (U6 (recount)): title banner

Files: reports/stage_e0_catalog_K4.md, reports/stage_e0_catalog.md (section K4). Matches replaced per file: 1.

Old:

````text
# Stage E.0 hypothesis catalog, cluster K4 (energy: CL, QM, MCL, NG, QG, MNG, RB, HO)

````

New:

````text
# Stage E.0 hypothesis catalog, cluster K4 (energy: CL, QM, MCL, NG, QG, MNG, RB, HO)

> **[Stage E.1, 2026-09-24: the user's decisions applied (docs/DECISIONS.md, U1 to U9; every edit in
> reports/stage_e1_changes.md).]** U6: K4-ml-01 is excluded: superseded by the Stage E ML route
> (user decision 2026-09-24); its text stays visible below and it adds 0 trials.
> **K4 after the decisions: 8 active members, 19 confirmation trials** (5 new + 3 core ports (K4-ngrev-01 excluded on review R-06); 12 port + 7 new trials). Header
> and section 6 totals below are superseded where they differ.

````

### K4-01 (U6): K4-ml-01 heading

Files: reports/stage_e0_catalog_K4.md, reports/stage_e0_catalog.md (section K4). Matches replaced per file: 1.

Old:

````text
### K4-ml-01 (the ML member, D15; this entry fills only D15.10's fields)

````

New:

````text
### K4-ml-01 (the ML member, D15; this entry fills only D15.10's fields)

> **[EXCLUDED: superseded by the Stage E ML route (user decision 2026-09-24, U6). Stage E.1.
> The text below stays visible for the record. This entry is not a Stage E member and adds 0
> trials; the ML route (docs/STAGE_E_ML_DESIGN.md) is separate.]**

````

### K5-00 (U6, U2, U9 (recount)): title banner

Files: reports/stage_e0_catalog_K5.md, reports/stage_e0_catalog.md (section K5). Matches replaced per file: 1.

Old:

````text
# Stage E.0 hypothesis catalog, cluster K5 (metals: GC, MGC, SI, SIL, HG, MHG, PL)

````

New:

````text
# Stage E.0 hypothesis catalog, cluster K5 (metals: GC, MGC, SI, SIL, HG, MHG, PL)

> **[Stage E.1, 2026-09-24: the user's decisions applied (docs/DECISIONS.md, U1 to U9; every edit in
> reports/stage_e1_changes.md).]** U6: K5-ml-01 is excluded: superseded by the Stage E ML route
> (user decision 2026-09-24); its text stays visible below and it adds 0 trials. U2: platinum (PL) is OUT, as a traded exposure and as a signal leg (Topstep's 50K volatility cap for PL is 0 and PL has no micro). Every statement below that makes platinum a traded exposure is struck through with a [U2] note; descriptive platinum facts (auction clock times, fees, Topstep's quoted text, question texts) are kept for the record and bind nothing. U9 (review R-28): K5-preauc-01's trial count is 2, as the 01:47 ruling set it.
> **K5 after the decisions: 7 active members, 16 confirmation trials** (4 new + 3 core ports; 9 port + 7 new trials). Header
> and section 6 totals below are superseded where they differ.

````

### K5-01 (U6): K5-ml-01 heading

Files: reports/stage_e0_catalog_K5.md, reports/stage_e0_catalog.md (section K5). Matches replaced per file: 1.

Old:

````text
### K5-ml-01 (the ML member, D15; this entry fills only D15.10's fields)

````

New:

````text
### K5-ml-01 (the ML member, D15; this entry fills only D15.10's fields)

> **[EXCLUDED: superseded by the Stage E ML route (user decision 2026-09-24, U6). Stage E.1.
> The text below stays visible for the record. This entry is not a Stage E member and adds 0
> trials; the ML route (docs/STAGE_E_ML_DESIGN.md) is separate.]**

````

### K6-00 (U6 (recount)): title banner

Files: reports/stage_e0_catalog_K6.md, reports/stage_e0_catalog.md (section K6). Matches replaced per file: 1.

Old:

````text
# Stage E.0 hypothesis catalog, cluster K6 (agriculture and livestock: ZC, ZW, ZS, ZM, ZL, HE, LE)

````

New:

````text
# Stage E.0 hypothesis catalog, cluster K6 (agriculture and livestock: ZC, ZW, ZS, ZM, ZL, HE, LE)

> **[Stage E.1, 2026-09-24: the user's decisions applied (docs/DECISIONS.md, U1 to U9; every edit in
> reports/stage_e1_changes.md).]** U6: K6-ml-01 is excluded: superseded by the Stage E ML route
> (user decision 2026-09-24); its text stays visible below and it adds 0 trials.
> **K6 after the decisions: 7 active members, 27 confirmation trials** (4 new + 3 core ports (K6-ovr-01 excluded by the lead); 21 port + 6 new trials). Header
> and section 6 totals below are superseded where they differ.

````

### K6-01 (U6): K6-ml-01 heading

Files: reports/stage_e0_catalog_K6.md, reports/stage_e0_catalog.md (section K6). Matches replaced per file: 1.

Old:

````text
### K6-ml-01 (the ML member, D15; this entry fills only D15.10's fields)

````

New:

````text
### K6-ml-01 (the ML member, D15; this entry fills only D15.10's fields)

> **[EXCLUDED: superseded by the Stage E ML route (user decision 2026-09-24, U6). Stage E.1.
> The text below stays visible for the record. This entry is not a Stage E member and adds 0
> trials; the ML route (docs/STAGE_E_ML_DESIGN.md) is separate.]**

````

### K7-00 (U6, U1 (recount)): title banner

Files: reports/stage_e0_catalog_K7.md, reports/stage_e0_catalog.md (section K7). Matches replaced per file: 1.

Old:

````text
# Stage E.0 hypothesis catalog, cluster K7 (crypto: MBT traded; MET as a signal leg only)

````

New:

````text
# Stage E.0 hypothesis catalog, cluster K7 (crypto: MBT traded; MET as a signal leg only)

> **[Stage E.1, 2026-09-24: the user's decisions applied (docs/DECISIONS.md, U1 to U9; every edit in
> reports/stage_e1_changes.md).]** U6: K7-ml-01 is excluded: superseded by the Stage E ML route
> (user decision 2026-09-24); its text stays visible below and it adds 0 trials. U1: MET stays OUT; it may serve only as a signal leg under D9's member-level coverage check.
> **K7 after the decisions: 6 active members, 6 confirmation trials** (3 new + 3 core ports; 3 port + 3 new trials). Header
> and section 6 totals below are superseded where they differ.

````

### K7-01 (U6): K7-ml-01 heading

Files: reports/stage_e0_catalog_K7.md, reports/stage_e0_catalog.md (section K7). Matches replaced per file: 1.

Old:

````text
### K7-ml-01 (the ML member, D15; this entry fills only D15.10's fields)

````

New:

````text
### K7-ml-01 (the ML member, D15; this entry fills only D15.10's fields)

> **[EXCLUDED: superseded by the Stage E ML route (user decision 2026-09-24, U6). Stage E.1.
> The text below stays visible for the record. This entry is not a Stage E member and adds 0
> trials; the ML route (docs/STAGE_E_ML_DESIGN.md) is separate.]**

````

### K8-00 (U6, U3 (recount)): title banner

Files: reports/stage_e0_catalog_K8.md, reports/stage_e0_catalog.md (section K8). Matches replaced per file: 1.

Old:

````text
# Stage E.0 hypothesis catalog, cluster K8 (cross-cluster relationships)

````

New:

````text
# Stage E.0 hypothesis catalog, cluster K8 (cross-cluster relationships)

> **[Stage E.1, 2026-09-24: the user's decisions applied (docs/DECISIONS.md, U1 to U9; every edit in
> reports/stage_e1_changes.md).]** U6: K8-ml-01 is excluded: superseded by the Stage E ML route
> (user decision 2026-09-24); its text stays visible below and it adds 0 trials. U3: K8 runs last.
> **K8 after the decisions: 3 active members, 4 confirmation trials** (3 new, no ports; K8-flight-01 2, K8-oilcad-01 1, K8-wkndbtc-01 1). Header
> and section 6 totals below are superseded where they differ.

````

### K8-01 (U6): K8-ml-01 heading

Files: reports/stage_e0_catalog_K8.md, reports/stage_e0_catalog.md (section K8). Matches replaced per file: 1.

Old:

````text
### K8-ml-01 (the ML member, D15; this entry fills only D15.10's fields)

````

New:

````text
### K8-ml-01 (the ML member, D15; this entry fills only D15.10's fields)

> **[EXCLUDED: superseded by the Stage E ML route (user decision 2026-09-24, U6). Stage E.1.
> The text below stays visible for the record. This entry is not a Stage E member and adds 0
> trials; the ML route (docs/STAGE_E_ML_DESIGN.md) is separate.]**

````

### K1-02 (U6): section 6 trial table, ML row

Files: reports/stage_e0_catalog_K1.md, reports/stage_e0_catalog.md (section K1). Matches replaced per file: 1.

Old:

````text
| K1-ml-01 | Nasdaq-100 (no fallback) | 48 in research-window accounting only (D15.8) | 1 |
````

New:

````text
| ~~K1-ml-01~~ [excluded, U6] | Nasdaq-100 (no fallback) | ~~48 in research-window accounting only (D15.8)~~ | 0 (E.0: 1) |
````

### K2-02 (U6): section 6 trial table, ML row

Files: reports/stage_e0_catalog_K2.md, reports/stage_e0_catalog.md (section K2). Matches replaced per file: 1.

Old:

````text
| K2-ml-01 | ZN (fallback ZF) | 48 in research-window accounting only (D15.8) | 1 |
````

New:

````text
| ~~K2-ml-01~~ [excluded, U6] | ZN (fallback ZF) | ~~48 in research-window accounting only (D15.8)~~ | 0 (E.0: 1) |
````

### K3-02 (U6): section 6 trial table, ML row

Files: reports/stage_e0_catalog_K3.md, reports/stage_e0_catalog.md (section K3). Matches replaced per file: 1.

Old:

````text
| K3-ml-01 | EUR (no fallback) | 48 in research-window accounting only (D15.8) | 1 |
````

New:

````text
| ~~K3-ml-01~~ [excluded, U6] | EUR (no fallback) | ~~48 in research-window accounting only (D15.8)~~ | 0 (E.0: 1) |
````

### K4-02 (U6): section 6 trial table, ML row

Files: reports/stage_e0_catalog_K4.md, reports/stage_e0_catalog.md (section K4). Matches replaced per file: 1.

Old:

````text
| K4-ml-01 | crude (no fallback) | 48 in research-window accounting only (D15.8) | 1 |
````

New:

````text
| ~~K4-ml-01~~ [excluded, U6] | crude (no fallback) | ~~48 in research-window accounting only (D15.8)~~ | 0 (E.0: 1) |
````

### K5-02 (U6): section 6 trial table, ML row

Files: reports/stage_e0_catalog_K5.md, reports/stage_e0_catalog.md (section K5). Matches replaced per file: 1.

Old:

````text
| K5-ml-01 | gold (fallback silver, then copper: lead ruling) | 48 in research-window accounting only (D15.8) | 1 |
````

New:

````text
| ~~K5-ml-01~~ [excluded, U6] | gold (fallback silver, then copper: lead ruling) | ~~48 in research-window accounting only (D15.8)~~ | 0 (E.0: 1) |
````

### K6-02 (U6): section 6 trial table, ML row

Files: reports/stage_e0_catalog_K6.md, reports/stage_e0_catalog.md (section K6). Matches replaced per file: 1.

Old:

````text
| K6-ml-01 | ZC (no fallback) | 48 in research-window accounting only (D15.8) | 1 |
````

New:

````text
| ~~K6-ml-01~~ [excluded, U6] | ZC (no fallback) | ~~48 in research-window accounting only (D15.8)~~ | 0 (E.0: 1) |
````

### K7-02 (U6): section 6 trial table, ML row

Files: reports/stage_e0_catalog_K7.md, reports/stage_e0_catalog.md (section K7). Matches replaced per file: 1.

Old:

````text
| K7-ml-01 | bitcoin (no fallback) | 48 in research-window accounting only (D15.8) | 1 |
````

New:

````text
| ~~K7-ml-01~~ [excluded, U6] | bitcoin (no fallback) | ~~48 in research-window accounting only (D15.8)~~ | 0 (E.0: 1) |
````

### K1-03 (U6): section 0 header, ML grid row

Files: reports/stage_e0_catalog_K1.md, reports/stage_e0_catalog.md (section K1). Matches replaced per file: 1.

Old:

````text
| ML grid | 48 configurations, counted only in the K1 screening session's research-window accounting (D15.8) |
````

New:

````text
| ML grid | ~~48 configurations, counted only in the K1 screening session's research-window accounting (D15.8)~~ [superseded, U6: no ML member] |
````

### K3-03 (U6): section 0 header, ML grid row

Files: reports/stage_e0_catalog_K3.md, reports/stage_e0_catalog.md (section K3). Matches replaced per file: 1.

Old:

````text
| ML grid | 48 configurations, counted only in the K3 screening session's research-window accounting (D15.8) |
````

New:

````text
| ML grid | ~~48 configurations, counted only in the K3 screening session's research-window accounting (D15.8)~~ [superseded, U6: no ML member] |
````

### K4-03 (U6): section 0 header, ML grid row

Files: reports/stage_e0_catalog_K4.md, reports/stage_e0_catalog.md (section K4). Matches replaced per file: 1.

Old:

````text
| ML grid | 48 configurations, counted only in the K4 screening session's research-window accounting (D15.8) |
````

New:

````text
| ML grid | ~~48 configurations, counted only in the K4 screening session's research-window accounting (D15.8)~~ [superseded, U6: no ML member] |
````

### K5-03 (U6): section 0 header, ML grid row

Files: reports/stage_e0_catalog_K5.md, reports/stage_e0_catalog.md (section K5). Matches replaced per file: 1.

Old:

````text
| ML grid | 48 configurations, counted only in the K5 screening session's research-window accounting (D15.8) |
````

New:

````text
| ML grid | ~~48 configurations, counted only in the K5 screening session's research-window accounting (D15.8)~~ [superseded, U6: no ML member] |
````

### K6-03 (U6): section 0 header, ML grid row

Files: reports/stage_e0_catalog_K6.md, reports/stage_e0_catalog.md (section K6). Matches replaced per file: 1.

Old:

````text
| ML grid | 48 configurations, counted only in the K6 screening session's research-window accounting (D15.8) |
````

New:

````text
| ML grid | ~~48 configurations, counted only in the K6 screening session's research-window accounting (D15.8)~~ [superseded, U6: no ML member] |
````

### K7-03 (U6): section 0 header, ML grid row

Files: reports/stage_e0_catalog_K7.md, reports/stage_e0_catalog.md (section K7). Matches replaced per file: 1.

Old:

````text
| ML grid | 48 configurations, counted only in the K7 screening session's research-window accounting (D15.8) |
````

New:

````text
| ML grid | ~~48 configurations, counted only in the K7 screening session's research-window accounting (D15.8)~~ [superseded, U6: no ML member] |
````

### K8-03 (U6): section 0 header, ML grid row

Files: reports/stage_e0_catalog_K8.md, reports/stage_e0_catalog.md (section K8). Matches replaced per file: 1.

Old:

````text
| ML grid | 48 configurations, counted only in the K8 screening session's research-window accounting (D15.8) |
````

New:

````text
| ML grid | ~~48 configurations, counted only in the K8 screening session's research-window accounting (D15.8)~~ [superseded, U6: no ML member] |
````

### K2-03 (U6): section 0 header, ML grid row

Files: reports/stage_e0_catalog_K2.md, reports/stage_e0_catalog.md (section K2). Matches replaced per file: 1.

Old:

````text
| ML grid (research-window accounting only, D15.8) | 48 configurations, counted in the K2 screening session's research-window DSR for K2-ml-01 |
````

New:

````text
| ML grid (research-window accounting only, D15.8) | ~~48 configurations, counted in the K2 screening session's research-window DSR for K2-ml-01~~ [superseded, U6: no ML member] |
````

### K8-04 (U6): section 0 header, trials row

Files: reports/stage_e0_catalog_K8.md, reports/stage_e0_catalog.md (section K8). Matches replaced per file: 1.

Old:

````text
K8-flight-01 2 (exit grid), K8-oilcad-01 1, K8-wkndbtc-01 1, K8-ml-01 1.
````

New:

````text
K8-flight-01 2 (exit grid), K8-oilcad-01 1, K8-wkndbtc-01 1, ~~K8-ml-01 1~~ [U6: excluded; K8 has 4 trials].
````

### K5-10 (U2): section 0 header, products

Files: reports/stage_e0_catalog_K5.md, reports/stage_e0_catalog.md (section K5). Matches replaced per file: 1.

Old:

````text
| Products | GC, MGC, SI, SIL, HG, MHG (COMEX); PL (NYMEX) |
````

New:

````text
| Products | GC, MGC, SI, SIL, HG, MHG (COMEX); ~~PL (NYMEX)~~ [OUT, U2] |
````

### K5-11 (U2): section 0 header, exposures

Files: reports/stage_e0_catalog_K5.md, reports/stage_e0_catalog.md (section K5). Matches replaced per file: 1.

Old:

````text
| Exposures | gold {GC, MGC}; silver {SI, SIL}; copper {HG, MHG}; platinum {PL} (partition section 1) |
````

New:

````text
| Exposures | gold {GC, MGC}; silver {SI, SIL}; copper {HG, MHG}; ~~platinum {PL}~~ [OUT, U2] (partition section 1) |
````

### K5-12 (U2): section 0 header, D1

Files: reports/stage_e0_catalog_K5.md, reports/stage_e0_catalog.md (section K5). Matches replaced per file: 1.

Old:

````text
**D1 applied: all four K5 exposures IN; platinum flagged (may be suspended).**
````

New:

````text
**D1 applied: all four K5 exposures IN; platinum flagged (may be suspended).** [U2, 2026-09-24: platinum OUT by the user's decision; three K5 exposures are traded.]
````

### K5-13 (U6): section 0 header, members

Files: reports/stage_e0_catalog_K5.md, reports/stage_e0_catalog.md (section K5). Matches replaced per file: 1.

Old:

````text
| Members | **8 = 4 new + 3 core ports + 1 ML member.** Budget 15
````

New:

````text
| Members | **8 = 4 new + 3 core ports + 1 ML member.** [E.1: 7 = 4 new + 3 core ports; K5-ml-01 excluded, U6.] Budget 15
````

### K5-14 (U9, U2, U6): section 0 header, trials

Files: reports/stage_e0_catalog_K5.md, reports/stage_e0_catalog.md (section K5). Matches replaced per file: 1.

Old:

````text
| Trials in N (confirmation) | **22 if D2 admits all four exposures:** 12 port + 9 new + 1 ML.
````

New:

````text
| Trials in N (confirmation) | ~~**22 if D2 admits all four exposures:** 12 port + 9 new + 1 ML.~~ [E.1. U9 (review R-28): after the 01:47 ruling put K5-preauc-01 at 2 trials the figure was 21 = 12 port + 8 new + 1 ML. After U2 and U6: **16 if D2 admits gold, silver and copper: 9 port + 7 new**; in general 4E + 3a_G + a_S, where E counts admitted exposures among gold, silver and copper. The E.0 formula follows.]
````

### K5-15 (U2): C6 size table, PL row

Files: reports/stage_e0_catalog_K5.md, reports/stage_e0_catalog.md (section K5). Matches replaced per file: 1.

Old:

````text
  | PL | 1 | 1 | 0 at Topstep's discretion | 1 (may be suspended) |
````

New:

````text
  | ~~PL~~ [OUT, U2] | ~~1~~ | ~~1~~ | 0 (Topstep F12.1c) | — |
````

### K5-16 (U2): K5-cp1-01, traded exposures

Files: reports/stage_e0_catalog_K5.md, reports/stage_e0_catalog.md (section K5). Matches replaced per file: 1.

Old:

````text
- **Traded exposures** (each a separate trial): gold {GC, MGC}, silver {SI, SIL}, copper {HG, MHG},
  platinum {PL}. Each is traded only if D2 admits it. **Vehicle:** D2 (chosen in E.2).
````

New:

````text
- **Traded exposures** (each a separate trial): gold {GC, MGC}, silver {SI, SIL}, copper {HG, MHG}
  ~~, platinum {PL}~~ [U2: platinum OUT]. Each is traded only if D2 admits it. **Vehicle:** D2 (chosen in E.2).
````

### K5-17 (U2): K5-cp1-01, instantiation row

Files: reports/stage_e0_catalog_K5.md, reports/stage_e0_catalog.md (section K5). Matches replaced per file: 1.

Old:

````text
  | platinum | 07:20 / 12:05 / 15:08 | 07:49 | 11:34, 11:35 | 12:03, 12:04 | 29 min |
````

New:

````text
  | ~~platinum~~ [OUT, U2] | ~~07:20 / 12:05 / 15:08~~ | ~~07:49~~ | ~~11:34, 11:35~~ | ~~12:03, 12:04~~ | ~~29 min~~ |
````

### K5-18 (U2): K5-cp2-01, exposures

Files: reports/stage_e0_catalog_K5.md, reports/stage_e0_catalog.md (section K5). Matches replaced per file: 1.

Old:

````text
- **Exposures:** gold, silver, copper, platinum, one trial each, each traded only if D2 admits it.
````

New:

````text
- **Exposures:** gold, silver, copper ~~, platinum~~ [U2: platinum OUT], one trial each, each traded only if D2 admits it.
````

### K5-19 (U2): K5-cp2-01, instantiation row

Files: reports/stage_e0_catalog_K5.md, reports/stage_e0_catalog.md (section K5). Matches replaced per file: 1.

Old:

````text
  | platinum | [07:20, 07:35) | [07:35, 12:05) | PL tick 0.10, so 0.40 | PL $20 | 07:36 / 12:05 | 13:20 |
````

New:

````text
  | ~~platinum~~ [OUT, U2] | ~~[07:20, 07:35)~~ | ~~[07:35, 12:05)~~ | ~~PL tick 0.10, so 0.40~~ | ~~PL $20~~ | ~~07:36 / 12:05~~ | ~~13:20~~ |
````

### K5-20 (U2): K5-cp3-01, exposures

Files: reports/stage_e0_catalog_K5.md, reports/stage_e0_catalog.md (section K5). Matches replaced per file: 1.

Old:

````text
- **Exposures:** gold, silver, copper, platinum, each traded only if D2 admits it. **Vehicle:** D2 (chosen in
````

New:

````text
- **Exposures:** gold, silver, copper ~~, platinum~~ [U2: platinum OUT], each traded only if D2 admits it. **Vehicle:** D2 (chosen in
````

### K5-21 (U2): K5-cp3-01, instantiation row

Files: reports/stage_e0_catalog_K5.md, reports/stage_e0_catalog.md (section K5). Matches replaced per file: 1.

Old:

````text
  | platinum | [07:20, 12:05) | 12:04 | 07:20, 07:21 | 12:03, 12:04 | 283 min |
````

New:

````text
  | ~~platinum~~ [OUT, U2] | ~~[07:20, 12:05)~~ | ~~12:04~~ | ~~07:20, 07:21~~ | ~~12:03, 12:04~~ | ~~283 min~~ |
````

### K5-22 (U2): K5-cp1-01, K5-cp2-01, K5-cp3-01, K5-ovr-01: trials in N

Files: reports/stage_e0_catalog_K5.md, reports/stage_e0_catalog.md (section K5). Matches replaced per file: 4.

Old:

````text
- **Trials in N:** 1 per admitted exposure (at most 4).
````

New:

````text
- **Trials in N:** 1 per admitted exposure (at most 3 after U2; E.0: at most 4).
````

### K5-23 (U9): K5-preauc-01, trials in N

Files: reports/stage_e0_catalog_K5.md, reports/stage_e0_catalog.md (section K5). Matches replaced per file: 1.

Old:

````text
- **Trials in N:** 3 (one per exposure).
````

New:

````text
- **Trials in N:** ~~3 (one per exposure)~~ 2 (gold and silver, one each, as the 01:47 ruling set it; text fixed in Stage E.1 under U9, review R-28).
````

### K5-24 (U2): K5-ovr-01, traded exposures

Files: reports/stage_e0_catalog_K5.md, reports/stage_e0_catalog.md (section K5). Matches replaced per file: 1.

Old:

````text
- **Traded exposures** (each a separate trial; each only if D2 admits it): gold, silver, platinum and copper.
````

New:

````text
- **Traded exposures** (each a separate trial; each only if D2 admits it): gold, silver ~~, platinum~~ and copper [U2: platinum OUT].
````

### K5-25 (U2): K5-ovr-01, decision times

Files: reports/stage_e0_catalog_K5.md, reports/stage_e0_catalog.md (section K5). Matches replaced per file: 1.

Old:

````text
10:20, 11:20, 12:20 (five). Copper: 08:10, 09:10, 10:10, 11:10 (four). Platinum: 08:20, 09:20, 10:20,
  11:20 (four).
````

New:

````text
10:20, 11:20, 12:20 (five). Copper: 08:10, 09:10, 10:10, 11:10 (four). ~~Platinum: 08:20, 09:20, 10:20,
  11:20 (four).~~ [U2: platinum OUT.]
````

### K5-26 (U2): K5-ovr-01, session window

Files: reports/stage_e0_catalog_K5.md, reports/stage_e0_catalog.md (section K5). Matches replaced per file: 1.

Old:

````text
  platinum 08:20-12:19. Flat by F.
````

New:

````text
  ~~platinum 08:20-12:19~~ [U2: platinum OUT]. Flat by F.
````

### K5-27 (U2): section 6, K5-cp1-01 row

Files: reports/stage_e0_catalog_K5.md, reports/stage_e0_catalog.md (section K5). Matches replaced per file: 1.

Old:

````text
| K5-cp1-01 | gold, silver, copper, platinum | 1 | 4 |
````

New:

````text
| K5-cp1-01 | gold, silver, copper ~~, platinum~~ [U2] | 1 | 3 (E.0: 4) |
````

### K5-28 (U2): section 6, K5-cp2-01 row

Files: reports/stage_e0_catalog_K5.md, reports/stage_e0_catalog.md (section K5). Matches replaced per file: 1.

Old:

````text
| K5-cp2-01 | gold, silver, copper, platinum | 1 | 4 |
````

New:

````text
| K5-cp2-01 | gold, silver, copper ~~, platinum~~ [U2] | 1 | 3 (E.0: 4) |
````

### K5-29 (U2): section 6, K5-cp3-01 row

Files: reports/stage_e0_catalog_K5.md, reports/stage_e0_catalog.md (section K5). Matches replaced per file: 1.

Old:

````text
| K5-cp3-01 | gold, silver, copper, platinum | 1 | 4 |
````

New:

````text
| K5-cp3-01 | gold, silver, copper ~~, platinum~~ [U2] | 1 | 3 (E.0: 4) |
````

### K5-30 (U2): section 6, K5-ovr-01 row

Files: reports/stage_e0_catalog_K5.md, reports/stage_e0_catalog.md (section K5). Matches replaced per file: 1.

Old:

````text
| K5-ovr-01 | gold, silver, platinum, copper | 1 | 4 |
````

New:

````text
| K5-ovr-01 | gold, silver ~~, platinum~~ [U2], copper | 1 | 3 (E.0: 4) |
````

### K5-31 (U9, U2, U6): section 6, cluster total

Files: reports/stage_e0_catalog_K5.md, reports/stage_e0_catalog.md (section K5). Matches replaced per file: 1.

Old:

````text
| **Cluster total** | | | **22** = 12 port + 9 new + 1 ML. In general 4E + 3a_G + a_S + a_P + 1. Without platinum: 17. Gold only: 8 |
````

New:

````text
| **Cluster total** | | | ~~**22** = 12 port + 9 new + 1 ML. In general 4E + 3a_G + a_S + a_P + 1. Without platinum: 17. Gold only: 8~~ [E.1: U9 (R-28) corrects the E.0 figure to 21 after the 01:47 ruling; after U2 and U6: **16** = 9 port + 7 new. In general 4E + 3a_G + a_S. Gold only: 7] |
````

### K5-32 (U9, U6): section 6, the without-platinum note

Files: reports/stage_e0_catalog_K5.md, reports/stage_e0_catalog.md (section K5). Matches replaced per file: 1.

Old:

````text
The "without platinum" figure: 3 x 3 ports + 3 ovr + 2 preauc + 1 pmfix + 1 fomc + 1 ML = 17.
````

New:

````text
The "without platinum" figure: 3 x 3 ports + 3 ovr + 2 preauc + 1 pmfix + 1 fomc + 1 ML = 17.
[E.1: with platinum OUT (U2) and K5-ml-01 excluded (U6): 9 + 3 + 2 + 1 + 1 = 16.]
````

### K5-33 (U9): section 7 item 3, K5-preauc-01 cost

Files: reports/stage_e0_catalog_K5.md, reports/stage_e0_catalog.md (section K5). Matches replaced per file: 1.

Old:

````text
   - It costs 3 trials.
````

New:

````text
   - It costs 3 trials. [E.1, U9 (review R-28): 2 trials after the 01:47 ruling.]
````

### K5-34 (U2): section 7 item 8, platinum

Files: reports/stage_e0_catalog_K5.md, reports/stage_e0_catalog.md (section K5). Matches replaced per file: 1.

Old:

````text
8. **Platinum.**

````

New:

````text
8. **Platinum.** [Decided by the user, U2, 2026-09-24: platinum is OUT.]

````

### K2-10 (U9): K2-cp2-01, pre-amendment note

Files: reports/stage_e0_catalog_K2.md, reports/stage_e0_catalog.md (section K2). Matches replaced per file: 1.

Old:

````text
- **Note for the lead (not a change; the text is copied unchanged):** D6's text has no
  latest-entry time.
````

New:

````text
- **Note for the lead (not a change; the text is copied unchanged):** [Superseded (review R-28,
  applied in Stage E.1 under U9): the lead's 21:12 amendment bounds entries at C, as the
  instantiation above states; this note predates it.] D6's text has no
  latest-entry time.
````

### K2-11 (U9): section 7 item 1, pre-amendment note

Files: reports/stage_e0_catalog_K2.md, reports/stage_e0_catalog.md (section K2). Matches replaced per file: 1.

Old:

````text
1. **CP2 has no latest-entry time.** It is copied verbatim from D6.
````

New:

````text
1. **CP2 has no latest-entry time.** [Superseded (review R-28, U9): the lead's 21:12 amendment
   bounds entries at C.] It is copied verbatim from D6.
````

### A-01 (U2, U6 (recount)): assembled header

Files: reports/stage_e0_catalog.md (header). Matches replaced per file: 1.

Old:

````text
> **Post-review figures (lead, Task 8, 2026-09-24 06:21 PDT):** 61 active members, 170 confirmation trials, projected cumulative N = 58 + 170 = 228.
````

New:

````text
> **Stage E.1 figures (lead, 2026-09-24, after the user's decisions U1 to U9; docs/DECISIONS.md;
> every edit in reports/stage_e1_changes.md). These govern over every figure and table below.**
> 53 active members, 158 confirmation trials, projected cumulative N = 58 + 158 = 216.
>
> | Cluster | Active members | Confirmation trials | Change from E.0 |
> |---|---|---|---|
> | K1 | 5 (2 new + 3 ports) | 11 | K1-ml-01 excluded (U6); run only if the user decides after K7 (U3) |
> | K2 | 8 (5 new + 3 ports) | 44 | K2-ml-01 excluded (U6); first cluster (U3) |
> | K3 | 9 (6 new + 3 ports) | 31 | K3-ml-01 excluded (U6) |
> | K4 | 8 (5 new + 3 ports) | 19 | K4-ml-01 excluded (U6) |
> | K5 | 7 (4 new + 3 ports) | 16 | K5-ml-01 excluded (U6); platinum OUT (U2): -1 trial each on K5-cp1-01, K5-cp2-01, K5-cp3-01, K5-ovr-01 |
> | K6 | 7 (4 new + 3 ports) | 27 | K6-ml-01 excluded (U6) |
> | K7 | 6 (3 new + 3 ports) | 6 | K7-ml-01 excluded (U6) |
> | K8 | 3 (3 new) | 4 | K8-ml-01 excluded (U6); last cluster (U3) |
> | **Total** | **53** | **158** (93 port + 65 new + 0 ML) | |
>
> Arithmetic: E.0's post-review catalog had 61 members and 170 trials. U6 excludes the eight
> K#-ml-01 members (-8 members, -8 trials). U2 removes platinum from four members (-4 trials, no
> member lost). 61 - 8 = 53; 170 - 8 - 4 = 158; N = 58 + 158 = 216. The ML grid configurations (E.0:
> 384) no longer exist. The per-exposure table below still lists platinum and the ML members: both
> are superseded (reports/stage_e0_catalog.json carries the E.1 figures).
>
> **Post-review figures (lead, Task 8, 2026-09-24 06:21 PDT):** 61 active members, 170 confirmation trials, projected cumulative N = 58 + 170 = 228.
````

## Edits to reports/stage_e0_catalog.json

| Field | Old | New | Decision |
|---|---|---|---|
| K1-ml-01 | status active, trials 1 | status excluded_superseded_ml_route, trials 0 | U6 |
| K2-ml-01 | status active, trials 1 | status excluded_superseded_ml_route, trials 0 | U6 |
| K3-ml-01 | status active, trials 1 | status excluded_superseded_ml_route, trials 0 | U6 |
| K4-ml-01 | status active, trials 1 | status excluded_superseded_ml_route, trials 0 | U6 |
| K5-cp1-01 | exposures ['gold', 'silver', 'copper', 'platinum'], trials 4 | exposures ['gold', 'silver', 'copper'], trials 3 | U2 |
| K5-cp2-01 | exposures ['gold', 'silver', 'copper', 'platinum'], trials 4 | exposures ['gold', 'silver', 'copper'], trials 3 | U2 |
| K5-cp3-01 | exposures ['gold', 'silver', 'copper', 'platinum'], trials 4 | exposures ['gold', 'silver', 'copper'], trials 3 | U2 |
| K5-ovr-01 | exposures ['gold', 'silver', 'platinum', 'copper'], trials 4 | exposures ['gold', 'silver', 'copper'], trials 3 | U2 |
| K5-ml-01 | status active, trials 1 | status excluded_superseded_ml_route, trials 0 | U6 |
| K6-ml-01 | status active, trials 1 | status excluded_superseded_ml_route, trials 0 | U6 |
| K7-ml-01 | status active, trials 1 | status excluded_superseded_ml_route, trials 0 | U6 |
| K8-ml-01 | status active, trials 1 | status excluded_superseded_ml_route, trials 0 | U6 |
| clusters[K1] | members_active 6, trials 12, exposures ['Nasdaq-100', 'Russell 2000', 'Dow'] | members_active 5, trials 11, exposures ['Nasdaq-100', 'Russell 2000', 'Dow'] | U6 |
| clusters[K2] | members_active 9, trials 45, exposures ['ZT', 'ZF', 'ZN', 'TN', 'ZB', 'UB'] | members_active 8, trials 44, exposures ['ZT', 'ZF', 'ZN', 'TN', 'ZB', 'UB'] | U6 |
| clusters[K3] | members_active 10, trials 32, exposures ['EUR', 'AUD', 'GBP', 'CAD', 'JPY', 'CHF', 'NZD'] | members_active 9, trials 31, exposures ['EUR', 'AUD', 'GBP', 'CAD', 'JPY', 'CHF', 'NZD'] | U6 |
| clusters[K4] | members_active 9, trials 20, exposures ['crude', 'gas', 'RBOB', 'ULSD'] | members_active 8, trials 19, exposures ['crude', 'gas', 'RBOB', 'ULSD'] | U6 |
| clusters[K5] | members_active 8, trials 21, exposures ['gold', 'silver', 'copper', 'platinum'] | members_active 7, trials 16, exposures ['gold', 'silver', 'copper'] | U6, U2 |
| clusters[K6] | members_active 8, trials 28, exposures ['ZC', 'ZW', 'ZS', 'ZM', 'ZL', 'HE', 'LE'] | members_active 7, trials 27, exposures ['ZC', 'ZW', 'ZS', 'ZM', 'ZL', 'HE', 'LE'] | U6 |
| clusters[K7] | members_active 7, trials 7, exposures ['bitcoin'] | members_active 6, trials 6, exposures ['bitcoin'] | U6 |
| clusters[K8] | members_active 4, trials 5, exposures ['gold', 'CAD', 'Nasdaq-100'] | members_active 3, trials 4, exposures ['gold', 'CAD', 'Nasdaq-100'] | U6 |
| exposure_table[K1 Nasdaq-100] | members ['K1-cp1-01', 'K1-cp2-01', 'K1-cp3-01', 'K1-vxnband-01', 'K1-vwap-01', 'K1-ml-01'], trials 6 | members ['K1-cp1-01', 'K1-cp2-01', 'K1-cp3-01', 'K1-vxnband-01', 'K1-vwap-01'], trials 5 | U6 (and R-06 carried) |
| exposure_table[K2 ZN] | members ['K2-cp1-01', 'K2-cp2-01', 'K2-cp3-01', 'K2-aucpre-01', 'K2-aucpost-01', 'K2-fomcpost-01', 'K2-predrift-01', 'K2-monthend-01', 'K2-ml-01'], trials 9 | members ['K2-cp1-01', 'K2-cp2-01', 'K2-cp3-01', 'K2-aucpre-01', 'K2-aucpost-01', 'K2-fomcpost-01', 'K2-predrift-01', 'K2-monthend-01'], trials 8 | U6 (and R-06 carried) |
| exposure_table[K3 EUR] | members ['K3-cp1-01', 'K3-cp2-01', 'K3-cp3-01', 'K3-ldnrev-01', 'K3-ldnmom-01', 'K3-mehedge-01', 'K3-ecbfix-01', 'K3-ml-01'], trials 8 | members ['K3-cp1-01', 'K3-cp2-01', 'K3-cp3-01', 'K3-ldnrev-01', 'K3-ldnmom-01', 'K3-mehedge-01', 'K3-ecbfix-01'], trials 7 | U6 (and R-06 carried) |
| exposure_table[K4 crude] | members ['K4-cp1-01', 'K4-cp2-01', 'K4-cp3-01', 'K4-apipre-01', 'K4-eiafade-01', 'K4-eiamom-01', 'K4-ovr-01', 'K4-ml-01'], trials 8 | members ['K4-cp1-01', 'K4-cp2-01', 'K4-cp3-01', 'K4-apipre-01', 'K4-eiafade-01', 'K4-eiamom-01', 'K4-ovr-01'], trials 7 | U6 (and R-06 carried) |
| exposure_table[K4 gas] | members ['K4-cp1-01', 'K4-cp2-01', 'K4-cp3-01', 'K4-ngpre-01', 'K4-ngrev-01', 'K4-ovr-01'], trials 6 | members ['K4-cp1-01', 'K4-cp2-01', 'K4-cp3-01', 'K4-ngpre-01', 'K4-ovr-01'], trials 5 | R-06 carried (K4-ngrev-01, excluded in E.0, dropped from the member list; relabelled on audit FA-12) |
| exposure_table[K5 gold] | members ['K5-cp1-01', 'K5-cp2-01', 'K5-cp3-01', 'K5-preauc-01', 'K5-pmfix-01', 'K5-fomc-01', 'K5-ovr-01', 'K5-ml-01'], trials 8 | members ['K5-cp1-01', 'K5-cp2-01', 'K5-cp3-01', 'K5-preauc-01', 'K5-pmfix-01', 'K5-fomc-01', 'K5-ovr-01'], trials 7 | U6 (and R-06 carried) |
| exposure_table[platinum] | {"exposure": "platinum", "cluster": "K5", "members": ["K5-cp1-01", "K5-cp2-01", "K5-cp3-01", "K5-ovr-01"], "trials": 4} | removed | U2 |
| exposure_table[K6 ZC] | members ['K6-cp1-01', 'K6-cp2-01', 'K6-cp3-01', 'K6-wasdepre-01', 'K6-wasdepost-01', 'K6-ml-01'], trials 6 | members ['K6-cp1-01', 'K6-cp2-01', 'K6-cp3-01', 'K6-wasdepre-01', 'K6-wasdepost-01'], trials 5 | U6 (and R-06 carried) |
| exposure_table[K7 bitcoin] | members ['K7-cp1-01', 'K7-cp2-01', 'K7-cp3-01', 'K7-expiry-01', 'K7-rev2h-01', 'K7-montrend-01', 'K7-ml-01'], trials 7 | members ['K7-cp1-01', 'K7-cp2-01', 'K7-cp3-01', 'K7-expiry-01', 'K7-rev2h-01', 'K7-montrend-01'], trials 6 | U6 (and R-06 carried) |
| exposure_table[K8 CAD] | members ['K8-oilcad-01', 'K8-ml-01'], trials 2 | members ['K8-oilcad-01'], trials 1 | U6 (and R-06 carried) |
| totals | {"active_members": 61, "confirmation_trials": 170, "ml_grid_configs": 384} | {"active_members": 53, "confirmation_trials": 158, "ml_grid_configs": 0, "note": "E.1: ML members superseded by the Stage E ML route (U6); platinum OUT (U2)"} | U2, U6 |
| projected_N | {"before": 58, "stage_e_trials": 170, "projected": 228} | {"before": 58, "stage_e_trials": 158, "projected": 216} | U2, U6 |
| clusters[K1..K8].members_excluded_e1 | (absent) | the cluster's K#-ml-01 (8 fields) | U6 (row added on audit FA-12) |
| members[*].e1_ruling | (absent) | set on the 8 ML members and K5-cp1/cp2/cp3, K5-ovr-01 (12 fields) | U6, U2 (row added on audit FA-12) |
| totals.note | (absent) | "E.1: ML members superseded by the Stage E ML route (U6); platinum OUT (U2)" | U2, U6 (row added on audit FA-12) |
| e1_patch | (absent) | E.1 patch description | record (row added on audit FA-12) |
