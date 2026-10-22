
## 2026-10-21 — Stage E.28: methods brief, firm-contract ranking (Topstep x QM first), pilot ready but not bought (key absent); N = 538

Prompts docs/prompts/STAGE_E.28.md (V44) and docs/prompts/STAGE_E.28b.md (the same stage continued on the Pro plan,
V46). Return: reports/E.28_RETURN.md; working files reports/stage_e28_briefs/; STATE reports/stage_e28_STATE.md.
Holdout unlocks_logged 0 at start and end; REGISTRATION.md 0 bytes; nothing quoted, bought, tested or registered; no
outcome data read; no Databento call in either session.

**What ran.**
- Session 1 (bc87cf0f, Opus 5.5 xhigh, Max plan, ultracode on, 02:06-16:43 with three usage-limit pauses): Part C,
  the methods brief (methods inventory, 11 method readers, MathReviewer-FableXHigh G1-G6, six fixers); Part A, the
  blind ranking (spec hashed 02:14 before any lookup; contract, firm and platform readers; fact table, blind scorer,
  economics; RankingReviewer-FableXHigh); Part B1/B2, the pilot spec and code (PilotCoder; SpecReviewer-FableXHigh).
  Lead rulings v2 after RR-01 moved the top pair from Topstep x QG to Topstep x QM; the spec was re-filled for QM and
  frozen. The session was cut at 16:43 when the user moved to the Pro plan.
- Session 2, E.28b (c4961140, Opus 5.5 high, Pro plan, ultracode off, at most 2 workers, from 16:51): S1
  PilotFixer-OpusXHigh applied the spec fixes for QM (168, then 204 of 204 tests); S2 DeltaReviewer-OpusXHigh (the
  stand-in for Fable on Pro, fresh context) returned NO GO on RD-01 (any root accepted, a second buy possible) and
  RD-02 (request end not pinned), both fixed, then GO on one re-check. S3 did not run: DATABENTO_API_KEY3 was absent
  by name from 16:53 through the 20:30 deadline. The laptop rebooted at 20:42; the session resumed at 21:54 for S5.

**Results.**
- **Methods brief** (reports/stage_e28_methods_brief.md): costs, power, data granularity, firm rules and data access
  bound the program, not missing mathematics; 14 of 19 method families never used, 5 in part; at retail latency the
  methods measure a passive order's worth rather than supply an edge. Phased design: Phase 0 pilot, Phase 1 one
  contract with a model ladder counted into N, Phase 2 a pooled model tested on an unseen contract.
- **Ranking** (reports/stage_e28_ranking.md, v2): Topstep x QM 2.484, MFFU x QM 2.427, Tradeify x QM 2.415, Bulenox x
  QM 2.388, Lucid x QM 2.353; MNQ 14th. QM's place rests on CL-derived statistics (OC-1); with OC-1 off Topstep x ZM
  leads; under the v1 rulings Topstep x QG leads.
- **Pilot**: spec reports/stage_e28_pilot_spec.md frozen (sha256 89377403...; QM.v.0, mbp-1, FIFO, tick 0.025, fee
  0.1368 tick per side and 0.296 conservative, trade-through-only fills, span [2024-01-12, 2024-02-29T22:00:00Z),
  target USD 121.25 on acct-3). Code GO; nothing bought; the pilot on hold (V47); acct-3 at 0 of 125, kept.

**For the user** (return section 7): V47 (21:53-21:57) already holds the purchase and keeps acct-3. Open: how to
revise the pilot spec if QM passes E.30 (each V47 change touches a pinned guard: QM only, end 2024-02-29T22:00:00Z,
one purchase; a 2025-2026 sample lies after 2024-03-01, which E.28 forbade), or which contract replaces QM if it
fails (Topstep x ZM leads with OC-1 off); the review standard; the v2 rulings; the Topstep fee reading. E.29 may
start now. Max-sized: a Fable review of the revised spec, Phase 1 and Phase 2 of the methods brief.

@@COST_PROGRESS@@
