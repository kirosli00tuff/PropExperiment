# Stage E.29 return: combining the ranked contracts in one prop account (simulation study)

Lead: Opus 5.5, effort high, Pro plan (Ultracode off; review by an Opus 5.5 xhigh agent in a fresh context, V46
item 5). Session 488b039c-486e-454d-a9bd-0fba40def8ea. Times PDT. Prompt: docs/prompts/STAGE_E.29.md. Status file:
reports/stage_e29_STATE.md.

## 1. Summary

@@SUMMARY@@

## 2. Guardrail evidence

Start checks (19:20, reports/stage_e29_briefs/start_checks.txt, script checks.sh), verbatim excerpts:

```
@@START@@
```

End checks (reports/stage_e29_briefs/end_checks.txt):

```
@@END@@
```

Test suite: @@PYTEST@@

Scope kept: no outcome, holdout, embargo, research-window or E.28 pilot data was read; the only market data read was
owned one-minute bars of CL, ZM, GC and NQ dated 2022-10-01 to 2023-11-01 by file name (CorrMeasurer, holdout status
checked before and after: all_ok true, unlocks_logged 0 both times). No purchase, no Databento call, acct-3
untouched; nothing registered or frozen; N stays 538; REGISTRATION.md 0 bytes; prop_econ/ and every E.28 file
unedited (E.28's model imported read-only, sha256 in the STATE file); nothing under live/ or ops/; no key printed;
no push.

## 3. Results

### 3.1 The model (Z3)

The model was declared in reports/stage_e29_model.md (sha256 f393759f4af712a8...) before any E.29 code or run. In
short: each member of a basket trades T_i of 20 daily round trips (B3 7/7/6, the others 10/10), 1 contract each,
with gross P&L per trade normal(mu_i, sigma_1m,i^2) and E.28's limit-case cost. Members' daily P&L are normal with
mean m_i = T_i (mu_i - c_i) v_i and SD s_i = sqrt(T_i) sigma_i v_i, pairwise correlation rho on {0, 0.25, 0.5, 0.75}.
The account's day is their sum, normal(M, S^2) with S^2 = sum s_i^2 + 2 rho sum_{i<j} s_i s_j, and the combined
intraday path is a Brownian motion, so every rule E.28 mapped acts on the combined account through (M, S) on E.28's
own common random numbers; B0 is E.28's QM pair draw for draw. Position limits: only Topstep's 2-lot first XFA tier
can bind (B3 = QM + ZM + 0.1 MGC = 2.1 lots); primary form no-overlap (P&L-neutral in this model), sensitivity MGC
dropped on those days. Topstep's Tier 1 window is a scheduling constraint for size-1 trades (non-binding). Edge
setting (i): every member at k times its own E.28 break-even; setting (ii): QM at mu_QM, the others at zero edge.

### 3.2 Measured correlations (reference only, not an input)

Owned one-minute bars, front contract (highest-volume outright per trade date, roll dates dropped, early-halt dates
excluded), trade dates 2022-11-01 to 2023-10-31 (reports/stage_e29_briefs/E29_correlations.md). Pearson, 233 to 240
days:

| pair | daily return | daily range (% of price) |
|---|---|---|
| CL-ZM | 0.107 | 0.038 |
| CL-GC | 0.118 | 0.395 |
| CL-NQ | 0.088 | 0.143 |
| ZM-GC | -0.013 | 0.019 |
| ZM-NQ | -0.026 | 0.048 |
| GC-NQ | 0.159 | 0.378 |

On the rho grid: every return correlation sits between 0 and 0.25 (closest to 0 for the ZM pairs and about 0.1 for
CL with ZM, GC or NQ); range correlations reach 0.40 (CL-GC, GC-NQ), between 0.25 and 0.5. These are price
correlations. The model's rho is the correlation of a strategy's daily P&L. For direction-neutral one-minute trading,
P&L correlation follows from shared volatility days (closer to the range correlations, through the P&L variance)
more than from price direction, so the lead takes rho = 0 to 0.25 as the realistic band and 0.5 as a stress value.
This is a judgment, not a measurement.

### 3.3 Tables (Z4)

@@TABLES@@

### 3.4 Answers

@@ANSWERS@@

### 3.5 The ranking these results would imply (conditional)

@@RANKING@@

## 4. Delegation record

@@DELEGATION@@

## 5. Verification

@@VERIFICATION@@

## 6. Open choices

@@OC@@

## 7. Decisions for the user

@@DECISIONS@@

## 8. Session cost

@@COST@@
