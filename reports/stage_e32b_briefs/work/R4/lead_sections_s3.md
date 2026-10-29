# R4 lead sections (Stage E.32b; written by the lead, Opus 5.5 max, 2026-10-29 06:47-06:52 PDT)

These are the judgment parts of reports/stage_e32b_recommendations.md (spec 8.3 R4): the cases, the priors with their
base rates, the kill criteria, the non-prop paragraph and the stop rule. The fact tables, pre-registration outlines and
data purchase plans are the RecsDrafter's (work/R4/draft_sections.md). Numbers below come from briefs/r3_out.json and
briefs/R2_combinations.json (primary, after LR-Q3a and LR-V31); per-trade figures are in ticks of each contract.

## Base rates used for every prior

- The program's own record: 23 closed lines, 838 trials, no pass (briefs/R1_closed_lines.md). The closest searches to
  the remaining candidates all ended clean: ZM's 5-60 minute cross-asset, crush and order-flow families (E.33c, V56),
  E.20's ML search over the 17 roots including RTY and ZL (R1-15), the rest-of-day momentum rule in E16-H1 (a pooled test whose roots included YM) and on
  NQ (E.20 H6: T1 gross 1.25 ticks against a 4.08-tick cost, t -0.53), and the F08-type reversal E16-H4 (pooled, YM included).
  A Laplace estimate of a new registered line passing is (0 + 1) / (23 + 2) = 4%.
- The literature: no published post-2015 intraday effect on these underlyings exceeds 1.5 times the round trip, apart
  from three working-paper effects that are not significant after 2015 (V38 as amended by V45 item 4). Every primary
  R4 candidate has Q2 <= 2: there is no product-specific study at its horizon, so each is a discovery search for an
  unpublished effect (the user's V51 thesis), not a replication.
- Crowding: every surviving code carries D2 a = 1 (a published automated or HFT share of at least 50% for it or its
  group) and a market-maker or volume-incentive program in 2021-2026 (D2 b = 1 for 42 of the 47 codes' own ratings and 46 of 47 as scored, where satellites take their leader's value).
- Power: the minimum detectable edges below are at 80% power with the DSR at N = 838 over a 43-month test, assuming
  independent trades, which flatters the continuous families (nine to thirteen 30-minute trades a day are not
  independent draws).

A prior below is P(a real edge of at least the detectable size exists in the family on that product) x P(the
discovery stage finds it) x P(it persists into the sealed test). The last two are about 0.7 each for a well-powered
continuous family and lower for once-a-day families.

## The candidates (primary R4, r3 order)

### 1-2. ZL x F09 cross-market lead-lag and ZL x F10 order-book state, at Topstep (C 2.75 each), one program

Case. Soybean oil is the least crowded of the products that survive with a clean test window: its 30-minute move
(28.1 ticks) is large against a 2.38-tick round trip at Topstep (c_f / sigma = 0.085), it trades nine non-overlapping
30-minute holds in its 290-minute main session, and its one-shot test window 2017-05..2020-11 is sealed (V56 item 1
keeps it "for a future hypothesis family"). F09 asks whether the rest of the soy complex (ZS and ZM) leads ZL at 15 to 60 minutes, through crush margins that a slower participant set prices with a delay (the dossier's F09 covers ZS and ZM, not crude or heating oil); F10 asks whether the order book's state predicts the next 15 to 60 minutes. Both families get one registration,
because the seal allows a single read. Against it: the only ZL evidence is cointegration (Q2 = 2), and the same
families failed cleanly on its crush sibling ZM at 5-60 minutes (E.33c), where ZL was an input leg.
Prior: about 4% for the program (F09 about 3%, F10 about 2%, not additive because one registration shares the hurdle):
P(edge of 4.2 ticks gross per 30-minute trade, 0.15 sigma) about 0.07 for F09 and 0.04 for F10, times 0.7 x 0.7.
Kill criteria: (K0) the user keeps V31's cost-feasibility gate in force for discovery searches (no published expected
gross exists for either family): not run. (K1) The pre-registered discovery gate fails (the E.32 protocol's P7 tests at
the new N): stop, no test read. (K2) The best discovery configuration's net edge per trade is below the test's
minimum detectable edge (1.8 ticks for a 30-minute hold): stop, the test could not detect it. (K3) The sealed test
fails: the ZL program closes and counts toward the stop rule. (K4) A configuration that needs entries inside a firm's
news windows or holds past the main session's end is excluded by design.

### 3. RTY x F09 cross-market lead-lag, at Topstep (C 2.60)

Case. The Russell 2000 future against the large-cap index futures at 15 to 30 minutes; the dossier's evidence (F09.E06) has the Russell leading ES, so the family's direction is an open question, not a small-cap lag. The arithmetic is good (c_f / sigma = 0.044; 13 trades a day; test
minimum detectable edge 2.8 ticks against a 51.8-tick sigma), but RTY has no clean test window before 2024-03 (E.16, E.20 and E.21 read it), so a test needs data from 2024-03 onward, which V51 keeps closed unless the user approves it, and E.20's
ML search over RTY (R1-15) was negative out of sample.
Prior: under 1% (P(edge) about 0.04, discovery about 0.7; RTY's unread data after 2024-03 is 2024-03..2025-03 (13 months, about 273 dates) and 2026-06-17 onward, both needing the user's approval; on 273 dates the test's daily hurdle rises from 0.165 to 0.296 and its power at the 43-month detectable size falls to about 0.05).
Kill criteria: (K0) no user approval of 2024-03+ data: not run; (K1)-(K3) as for ZL, with a 2.8-tick K2 threshold.

### 4-5. MNQ x F08 and YM x F08 session and overnight-to-day handoff, at Topstep (C 2.55 each)

Case. The handoff from the overnight session to the US day session is the clearest predictable-time mechanism left
(Q1 = 3): overnight order flow and the European close are digested at the US open. But it trades once a day, so the
test can only detect an edge of 0.19 sigma per trade (12.3 ticks on YM, 28.5 on MNQ) on top of the cost; no published
post-2015 effect at that size exists on index futures; E16-H4, an F08-type reversal, failed in a pooled test that included YM; and both products
lack a usable clean test window (MNQ: read by E.20 and E.21; YM: V31 forbids variants on E.16's YM window and any YM
purchase).
Prior: about 1.5% for YM if V31 were narrowed (P(edge) about 0.05, discovery about 0.6 at one trade a day, persistence about 0.5) and under 1% for MNQ, whose unread data after 2024-03 is the same short windows (power about 0.05 on 273 dates); on Topstep's Standard Path MNQ's C falls to 2.40.
Kill criteria: (K0) YM: V31 not narrowed by the user: not run; MNQ: no approval of 2024-03+ data: not run; (K1)-(K3)
as above with K2 thresholds of 12.3 (YM) and 28.5 ticks (MNQ).

### Gated: the Dow, Nasdaq and Russell F01 (intraday momentum into the close)

The pair ranking's leaders (YM, MNQ, RTY) have their best family closed: F01's rest-of-day rule at a 30-minute hold was already read on YM in E16-H1's pooled test (V31) and on NQ (E.20 H6), and K1-cp1-01 traded the same 14:30-14:59 CT window on MYM and
M2K (LR-Q3a). On NQ the measured gross over 2020-06..2024-02 was 1.25 ticks a trade, under 1% of a 30-minute sigma (147 ticks in F3's window),
where Baltussen et al.'s out-of-sample estimate implies about 15%: the published effect looks spent on these contracts.

## The non-prop alternative

The best own-broker combination is the same ZL F09 program at IBKR (C 2.60 against 2.75 at Topstep): its round trip is
about the same (2.50 against 2.38 ticks), it drops the prop rules but needs margin and its daily risk at one contract
exceeds 2% of the USD 6,000 (u) ceiling (Q6 = 3), and the user cannot fund an own account yet (V32). The facts do not
favour it now; if the ZL program passed its sealed test, an own account would be the natural second venue once funded.

## Stop rule for the whole directional program

1. Run at most one more registered build: the ZL program above. If it fails its discovery gate or its sealed test, the directional program stops. RTY F09, MNQ F08 and YM F08 are not fallbacks: their only test windows are closed by V31 or, after 2024-03, so short that the test's power at the detectable size is about 0.05.
2. Independent of order, stop before any purchase or registration when the best remaining candidate's prior, as
   estimated here and lowered after each failure, is below 2%, or when its K0 condition fails.
3. After a stop, a restart needs a new information source the program has not used (for example options-dealer
   positioning, physical-market or fund-flow data with a documented intraday channel), not another product or family on
   the same bars and books.
Why: after 23 closed lines the remaining candidates have no product-specific evidence, priors of 1.5-4%, and minimum
detectable edges above every published intraday effect on these underlyings; each further search costs a stage, adds to
N and raises every later DSR hurdle.

## Decisions for the user (with recommendations)

- D1 V31's scope for YM (no variant on E.16's windows, no purchase of the fallback roots): recommend keeping it. The
  Dow's best family is closed and its next one (F08) has a 1.5% prior; narrowing V31 would make YM F08 the top
  candidate (C 2.85) without changing that prior.
- D2 The ZL sealed window's single read: recommend assigning it to the ZL program (F09 + F10), registered before any
  further ZL read, if the user accepts a prior of about 4%; otherwise stop the directional program now.
- D3 V31's cost-feasibility gate for discovery searches: recommend stating explicitly that a V51-style discovery search
  is admitted without a published expected gross, judged instead by the power rule (K2), or else keeping the gate,
  which stops every primary candidate before any purchase.
- D4 Data from 2024-03 onward (V51): recommend keeping it closed unless the ZL program passes; it only enables the weaker RTY and MNQ candidates, at a power of about 0.05 on the 13 unread months.
