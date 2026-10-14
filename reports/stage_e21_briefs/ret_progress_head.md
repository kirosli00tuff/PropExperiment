## 2026-10-14 — Stage E.21: multi-day round (TSMOM-12, trend blend, turn of the month, combined book); all four FAIL; N = 532

Prompt docs/prompts/STAGE_E.21.md (V38). Lead Opus 5.5 xhigh, ultracode on, session 13fe2d4e, unattended, no
pauses. Return: reports/E.21_RETURN.md.

- **Step 1 (four opus-high readers at once, 03:13-03:33):** T1 matches MOP 2012. HOP's 10% portfolio
  scaling for T2 was not adopted, a declared deviation (A6). The T3 parenthetical was corrected (day -2 =
  the second-to-last trade date). From the calendar-only counts, T3 was renumbered on NYSE trading days
  (A12: the futures calendar books US holidays as trade dates). PropEd: no public page grants automation
  (terms "only where supported and permitted"; FAQ: bots not allowed).
- **Freeze:** multiday/ (62 synthetic tests). FreezeReviewer-FableXHigh: APPROVE WITH FIXES, then APPROVE.
  Freeze 0bb899e5..., commit 839efc9. Registered r006-E21 (E21-T1..T4), N 528 -> 532. Evaluated once
  (marker 04:12:28; 2:11 wall, 1.47 GB).
- **Verdicts (base case, Holm 0.025):**
  - T1: net Sharpe 0.50 [-0.06, 1.05], t 1.78, p 0.042.
  - T2: 0.44 [-0.11, 0.98], t 1.56, p 0.064.
  - T3: 0.15, p 0.30.
  - T4: 0.12, p 0.34.
  - All FAIL. T1 and T2 clear the 0.3 bar but are underpowered: about 25 years are needed at a Sharpe of
    0.5. Published post-2010: AQR TSMOM 0.39 gross, SG Trend 0.35 net.
  - T4 is dominated by H5-scaling spikes at H2's hold starts.
  - VerdictVerifier-FableXHigh matched all 152 numbers (VERIFIED WITH NOTES). The 171 missing lookbacks in
    ZC, ZL, ZS, LE and HE come from double weekend roll instants in the store metadata (VV-1).
- **F8 (descriptive):** the 17-root book needs $323K-$691K at one contract or more per root (LE binds).
  PropEd cannot hold it: roots not listed, 46-100% of 21-day windows breach the drawdown. T3 fits several
  plans but failed.
- **Guardrails:**
  - Holdout all_ok, 0 unlocks, at start and end. REGISTRATION.md 0 bytes.
  - Spend ledger unchanged (36,402 lines, 034a454b...). Harness v12 and the E.14/E.16/E.18/E.20 freezes
    verify.
  - Nothing dated 2024-03-01 or later was read. No purchase, no Databento or TopstepX call, no push.
  - Suites: start 7340 passed, end 7402 passed (+62 multiday).
- **For the user:** close the trend test route on owned data, close T3 and T4, and make no PropEd purchase.
  Pause the futures program until the AiTrader readout (2026-10-23); then stop, or register a forward paper
  record (return section 7).

