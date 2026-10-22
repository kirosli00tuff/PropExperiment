## 2026-10-22 — Stage E.29: basket simulation; no basket beats QM alone under a QM-only edge, correlation barely matters; N = 538

Prompt docs/prompts/STAGE_E.29.md (V46, Pro plan). Return: reports/E.29_RETURN.md; declaration
reports/stage_e29_model.md (sha256 f393759f...8164); working files reports/stage_e29_briefs/; STATE
reports/stage_e29_STATE.md. Holdout unlocks_logged 0 at start and end; REGISTRATION.md 0 bytes; nothing quoted,
bought, frozen or registered; no Databento call; acct-3 untouched. No outcome, holdout, embargo, research-window or
pilot data was read. The only market data read was owned one-minute CL, ZM, GC and NQ bars from 2022-11 to 2023-10,
for reference correlations. prop_econ/ and E.28's files were not edited.

**What ran.** Session 488b039c (Opus 5.5 high, Pro plan, ultracode off), 10-21 19:19 to 10-22 @@END_TIME@@ PDT. It
had two usage-limit pauses with a reboot in each (19:37 to 21:53, reboot 20:42; 22:18 to 02:41, reboot 22:21). The
Z3 model was declared and hashed (19:24) before any code. CorrMeasurer-OpusHigh measured the reference
correlations. BasketCoder-OpusXHigh built the basket module on E.28's funnel; the usage limit cut it twice, and after
the second reboot the lead restarted the resumable grid run (02:41 to 02:51). BasketReviewer-OpusXHigh reviewed the
work in a fresh context (GO WITH FIXES, 0 BLOCKING). The lead fixed both SHOULD FIX items: a full grid
confirmation (0 of 470 thresholds moved) and the vanish-rho table.

**Results** (return section 3):
- B0 reproduces E.28's QM exactly at all five firms (limit and market break-even, mu10K, cost per attempt).
- Setting (ii), QM-only edge: 0 of 80 cells beat B0. Each basket raises QM's break-even by 0.08 to 1.39 ticks, and
  the mu10K analogue rises in every cell. A zero-edge member never helps.
- Setting (i), every member at k times its own break-even: 27 of 76 runnable cells beat B0 (Topstep and Tradeify B2
  and B3; Bulenox B1 from rho 0.25, B2 and B3). 24 of them contain MGC. MGC's alone break-even (6.3 to 8.3 ticks)
  comes from payout thresholds a one-lot micro rarely clears, so its win is an artifact of the unit. B1 (QM + ZM)
  moves no break-even outside Bulenox and lowers the mu10K multiplier by 7 to 17%. B4 (QM + MNQ) never helps.
- Rho: no flag turns off between 0 and 0.75; the account's daily SD is 5 to 9% of the 2,000 loss limit. Measured
  price correlations: returns -0.03 to 0.16, ranges up to 0.40. The realistic P&L rho of 0 to 0.25 is a judgment.
- E.28's v2 firm order stands. B0 has the lowest QM break-even at every firm under a QM-only edge.

**For the user** (return section 7):
- D1: keep the pilot and the first evaluation on QM alone (recommended: yes).
- D2: if E.30 fails QM, rerun E.29 with ZM as the anchor. This needs a new basket table and a new declaration.
- D3: no sigma-unit re-expression of setting (i) for now.
- D4: no change to E.28's L2 scores.

E.30 may start.

### Session cost

@@COST@@
