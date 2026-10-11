## 3. Results per task

Full results: reports/stage_e19_results.md (narrative, key numbers, and the machine tables T1-T8 with every grid
point) and reports/stage_e19_results.json (4,464 records). Model: reports/stage_e19_briefs/sim_spec.md and lead
decisions L-1..L-21 (section 6).

### Task 0: startup
Start checks at 17:03 passed (section 2). The lead wrote the binding model spec, the rules-JSON schema and the shared
interface (prop_econ/types.py) before any spawn.

### Task 1: rules and terms (TopstepRules-OpusHigh)
reports/stage_e19_rules.json and .md hold 214 rules from 41 Topstep help-centre and terms pages, fetched one at a
time by curl on 2026-10-10. Counts: 198 SOURCED, 6 INFERRED, 7 UNSOURCED, 3 CONFLICT; 42 prohibited or restricted
practices. Every quote is verbatim (validated by script, re-validated by Fable: 207/207 rules, 42/42 practices).
- The terms reading: ToU section 28 bans crawling and spidering; fetching named pages one by one is outside it (L-11,
  upheld by RulesReviewer).
- Changes from the earlier facts: Combine consistency is now "best day below 55% of total profit"; the Live Funded
  call-up is discretionary, closes all XFAs and transfers capped balances; the API costs $14.50/month; a VPS is not
  allowed; XFAs close after 30 days without trading.
- Key rules (value [source]; the UNSOURCED scaling boundary runs both readings):

{RULE_TABLE}

### Task 2: simulator (FunnelCoder-OpusXHigh)
prop_econ/rules.py (loader with reading overrides), funnel.py (the scalar reference), vec.py (vectorized; equal to the
scalar path for path) and assemble.py (fees, rebills, credits, resets, activation, Back2Funded, cycles, campaigns).
- 117 tests pin the hand-computed paths the prompt names: a pass then a payout, a fail and reset, a drawdown lock, a
  payout under each path, and the five-account cap. 148 prop_econ tests in all.
- Speed: 20,000 XFAs x 756 days in 0.3 to 0.6 s.
- GridCoder-OpusHigh added grid.py (the 780-job grid, resumable, seeded with common random numbers) and report.py
  (the aggregator).

### Task 3: return models (lead, with ReturnsCoder-OpusHigh)
Day-session holds from the owned E.12 training stores, read for return magnitudes only. Each path is demeaned, so
zero edge has exactly zero gross drift; the direction is a fair coin each day; draws are 5-day block bootstrap blocks
pooled over the five paths, against a normal comparison. The EconReviewer rebuilt this table independently: it
matches to 1e-9, with a mean of 0.

{RETURNS_TABLE}

Costs: the D8 round trip per contract, 1 or 3 per day. Measured on the vehicles actually traded, zero gross edge is
a net Sharpe of about -0.5 at one round trip a day and -1.5 at three. Edges S are net of costs.

### Task 4: results (lead)
Key numbers (headline configuration at each rule set's best band f; API fee included; B2F = Back2Funded):

{KEY_NUMBERS}

Break-even net Sharpe (T3; linear interpolation over S; '< 0' means positive already at S = 0):

{BREAK_EVEN}

Campaigns to $5,000 and $10,000 of withdrawn cash (T4, five slots, best band f, DLL and Back2Funded off, API in):

{CAMPAIGNS}

Sensitivities (T5; details in the results md, section 4):
- Normal tails make zero edge $34 to $230 less negative.
- A long-only direction is $31 to $325 worse.
- The cost wall is $36 to $975 worse.
- Integer single-product contracts are much worse for 6E, CL and GC.
- Keep-D payouts are better with any edge (+$209 at 50K Standard, net Sharpe 0.5).
- A call-up after the first payout costs $132 to $1,048 per cycle.
- The UNSOURCED scaling boundary and the CONFLICT consistency boundary have no effect.
- ACH payouts cost $10 to $42 per cycle.
- Copy-trading five accounts multiplies results by about five, but trips the Responsible Trading Program.

No sensitivity turns zero edge positive inside the band.

### Task 5: review (RulesReviewer-FableXHigh, EconReviewer-FableXHigh)
Section 5.
