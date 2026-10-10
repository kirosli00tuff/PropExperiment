
## 2026-10-09/10 — Stage E.17: C1 STOPPED at C10; the base-rule batch H1-H5 run once, all five FAIL ($121.86 spent)

Prompt docs/prompts/STAGE_E.17.md (V24-V30; V30 amended to a $124.00 budget). Lead Opus 5.5 xhigh, sessions 0dcecb5d
and c71b1fb9 (usage logged under 0dcecb5d). Return: reports/E.17_RETURN.md.

- **C1 (backward NG replication): STOPPED.**
  - Registered (N 471 -> 473), bought (642 chunks, $57.817332) and evaluated once under harness v11 (ba1ce996...).
  - The run stopped at guard C10: g17_mbt, live on 87/84 NG rows in E.12, is n/a by design in 2010-2019 (MBT did not
    exist), and the freeze has no exemption. That contradiction was decidable from frozen files before registration.
  - Fable verified the stop. Nothing was learned about the NG hypothesis; not rerun.
- **Base-rule batch E16-H1..H5: all five FAIL** (base case, Holm 0.05, N 478).
  - H1 mean -0.161 risk units, t -20.0. H2 +0.344, p 0.068, n 56. H3 -0.015, p 0.60. H4 -0.048, t -6.7. H5 -0.149,
    p 0.93.
  - DSR about 0; the stress and 1.5 x slippage cases are worse. Fable verified every verdict number (H5 with a note on
    its sparse-component sigma).
  - H1's gross momentum is positive but about a quarter of D8 cost.
  - No holdout-2 read and no meta-labeling (V28).
- **Purchase:** harness v12 (ece91ae8...) added plan ext2010h. The A3 selection (ZT ZF ZB CL ZL ZS UB TN RTY LE HE,
  933 chunks) cost $64.038166. Ten roots ran on the fallback window: YM HG 6S 6J 6A 6B 6N ZM ZW 6C.
- **Funds:** $121.855498 billed in the stage; acct-2 is about $3.14 short of the user's $125 figure.
- **Guardrails:** holdouts all_ok with 0 unlocks; REGISTRATION.md 0 bytes; every quote guarded by the run's own ledger
  lines. Commits a21d82d (v11), 558a7ce (C1), d30f50c (v12) and the final one. Suites: start 6815, v11 6815, v12 6916,
  end {{END_SUITE_SHORT}}.
- **Incident:** the first Claude session ended mid-buy (19:38); the buy resumed with the same command, leaving one
  $0.075 orphan commit. Long jobs then ran detached.

### Session cost

{{SESSION_COST_BODY}}
