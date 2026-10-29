# Stage E.32b: holding-time scope (F5; spec section 7)

Draft by ScopeWriter (Opus 5.5, high), 2026-10-29 from 05:27 PDT, for the lead. Facts only: every number comes from
the F5 script output (briefs/F5_holding.json, generated {{T:f5_generated}}), the econ model blocks (briefs/econ32b.json)
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

{{T:trades}}

L_main is 390 minutes (06:30-13:00 PT) for every code except the CBOT grains and their minis and micros (290
minutes, 06:30-11:20 PT). The grains sit next to two scheduled pauses: 07:45-08:30 CT (05:45-06:30 PT, "no orders
accepted", GRAINS-14) just before the main session, and the 13:20 CT day close (11:20 PT) with Globex reopening at
19:00 CT. Both are adjacent to, not inside, the main session. The other codes' daily 60-minute breaks (16:00-17:00 CT
or 17:00-18:00 ET, 14:00-15:00 PT) lie outside the main session.

### 1.2 k_RT(h) = c_RT / sigma_h, with where the power term reaches the cost term

"power >= cost from" is the first h at which SR80_test / sqrt(n_cap) >= c_RT / sigma_h (reading 10). From that h on,
the power term, not the cost, is the larger part of G.

{{T:surv_k}}

Square-root-of-time check: sigma(h1) / sigma(h2) x sqrt(h2 / h1) for each step (OC counted as L_main minutes). A value
of 1 means k falls exactly as 1/sqrt(h); above 1, sigma grows more slowly than sqrt(h) (k falls more slowly, the
curve flattens relative to a random walk); below 1, faster. Volatility statistics only (F3).

{{T:surv_rw}}

Reading of the two tables (facts): from 1 to 120 minutes every ratio lies between 0.97 and 1.07, so k(h) falls at
nearly the random-walk rate (about 0.71 per doubling of h) for every code; there is no horizon at which k levels off.
The largest departures are the rates and grains at 1-5 minutes (ratios up to 1.06: sigma grows a little slower than
sqrt(h), k falls a little slower) and the 240 -> OC step (0.84-0.99 for most codes; 1.05-1.12 for CL, MCL, NG, MNG),
where the open-to-close move is larger than the 240-minute scaling implies. k therefore has no flattening point; the
"power >= cost from" column marks where the power term, not the cost, becomes the larger part of G.

### 1.3 G_RT(h) (minimum in bold)

{{T:surv_G}}

Where the minimum lies:

{{T:surv_argmin}}

### 1.4 Hit rate needed (empirical m_h): break even / net 1 tick

Values above 1 are kept as computed (reading 12): at 1 minute some codes cannot break even with any sign forecast.
The normal-approximation p (p_norm) is in F5_holding.json beside each value and in the pair tables below.

{{T:surv_p}}

### 1.5 e80 at the test (ticks a trade, net)

Discovery values are fixed multiples of the test value because e80 = SR80 sigma_h / sqrt(n_cap): e80 disc G3 =
1.0458 x e80 test, e80 disc G3 + G4 = 1.1923 x e80 test (checked on every survivor row; full values in
F5_holding.json and in the pair tables). The gross needed for detection is c_RT + e80 (1.50 + the value below).

{{T:surv_e80}}

## 2. Top-15 pairs (firm rows, cost basis c_f)

### 2.1 Summary

{{T:pair_summary}}

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

{{T:pairs_detail}}

## 3. Overnight holds and the own-broker venue

### 3.1 Overnight holds beside the intraday rows

No prop firm in the top 15 allows an overnight hold in evaluation or funded, nor a weekend hold (F2_firms.md; F5
`overnight`). At ibkr overnight holds are allowed, carry the overnight initial margin and, on Tiered pricing only, an
overnight position fee of USD 0.10 a contract a night when the account just meets margin (0.05 at 2x, 0 at 3x).

{{T:overnight}}

Facts: in every top-15 pair and in the five ibkr rows, G at OC, cc and on is 0.20-0.23, 1.95-2.52 x the intraday
min G (1.40-1.66 x for MYM and ZL). The overnight rows' G is almost all power term (SR80_test / sqrt(1) = 0.194): one
trade a day cannot reach 80% power at the test unless the gross edge is 0.19-0.21 sigma a trade. At the prop firms
the DLL is below 2 x sigma_cc v on 8 of the 15 pairs (every YM and RTY pair except bulenox|RTY).

### 3.2 Own broker: all 35 codes (LR-F5-IBKR, LR-Q6d)

Venue: IBKR own account, British Columbia resident (Interactive Brokers Canada Inc.); no DLL, MLL or flat-by-close;
capital ceiling USD 6,000 (u: none recorded in docs/DECISIONS.md). Fee = 2 x (IBKR execution USD 0.85 + clearing 0 +
exchange fee + regulatory fee) a round trip. ">" marks a margin above the ceiling or a sigma_day above 2% of it
(USD 120).

{{T:ibkr_summary}}

Rows that do not hold, with the reason:

{{T:ibkr_fails}}

In 8 of the 14 "fails" rows B is non-empty (MHG, MZL, XC, ZB, ZC, ZT with intraday members; MZM and MZS with OC
only) and the verdict fails only because the
minimum G lies at cc; the cc G is 2-9% below the lowest intraday G there (columns "min G" and "min intraday G").
Spec 7's rule is literal (a minimum of G only at OC or overnight fails), so these rows are reported as "fails (min G
overnight)" with their intraday band beside (column "intraday B").

### 3.3 The five top-15 codes at ibkr (full detail)

{{T:ibkr_detail}}

Venue comparison (the same code at the prop firms and at ibkr):

{{T:venue_compare}}

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

{{T:edir}}

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

{{T:prior}}

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

{{T:sources}}
