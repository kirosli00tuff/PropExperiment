
## 2026-10-03 — Stage E.12: ML route v2 frozen, phase 1 bought (all 28), Gate 0 run once: FAIL

Lead Opus 5.5 xhigh, 2026-10-03 07:51 to {{END_TIME}} PDT, unattended apart from one question to the user
(the held stores). Return: reports/E.12_RETURN.md.

**Gate 0 FAILED, so ML route v2 stops** (V2.2b): no phase-2 purchase, no model. No pair of 81 passes.
The best, NG h60, has a mean gross of 3.25 x cost but t_B 2.51 and p 0.0062 against a Holm threshold of
0.000183 (rank 1 of 273); no pair reaches t >= 3. Pooled family B: gross -0.72 ticks against 2.26 of
cost (t 0.28, 39,997 trades). Fable recomputed all 273 tests independently (agreement 1e-13): VERIFIED
WITH NOTES.

**What happened, in order:**
- V23 applied to the design and the code (gross cost-gate reading, tau 0.167, release-window rule,
  K9-anncday-01 with a new 2019-2024 EC-K9 calendar of 240 sourced dates, 150K figures from
  Topstep's pages). A real-data entry point (ml_route_v2/phase1) was built so Gate 0's code was frozen
  before any data.
- CME's margin pages refused automated access, so the purchase ranking used the frozen E|m_1|.
- Fable reviewed the freeze before the commit (0 blocking); commit 9466f2e, manifest a647cd06...
- Harness v8 (deccd17, 452c4a51...): acct-2 cap $249.67, key strip, a training-window-only purchase.
- The frozen subset rule selected all 28 exposures: 1,543 training-window chunks for $133.72
  (acct-1 $26.80, acct-2 $106.93), billed = quoted on every chunk, nothing from 2024-03 on.
- The store builder held 12 roots on 24 reopen-minute bars inside scheduled closures (2020
  quarter-ends); the user chose harness v9 (4b1e81e, 7fd757f6...): keep and flag, an enumerated
  ruling.
- Build: 28 vehicles; MES refused by the frozen loader (pre-registered P-1a: 3 signals out); MBT no
  row (D4 start 2024-01-02); 64 signals; 81 admissible pairs. List registered (53e7ef57...), then Gate 0
  ran once.

**N: 198 + 273 = 471.** Funds left: acct-1 $1.61, acct-2 $18.07. Holdout sealed, 0 unlocks.
REGISTRATION.md 0 bytes.

**Decision for the user:** accept the stop (recommended); the V22 personal-account path has no model
to move; the AiTrader Stage C readout is the recommended next live question.

{{COST}}
