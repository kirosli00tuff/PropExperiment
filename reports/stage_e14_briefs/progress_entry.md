
## 2026-10-05 — Stage E.14: C1 frozen, awaiting funds; C2 stopped at its power rule (nothing bought)

Prompt docs/prompts/STAGE_E.14.md (revision V26). Lead Opus 5.5 xhigh, session 19c73927. Return:
reports/E.14_RETURN.md.

- C2 (GEX-conditioned S&P late-session momentum, Baltussen et al.) stopped before its freeze at its power rule:
  - only 135 eligible 2011-05..2019-04 dates had a negative lag-1 GEX, under the 200 floor;
  - no calendar can lift it above 146;
  - Fable recomputed it independently.
  - Nothing was registered or bought, and no ES bar was read. The user decides its next step; the lead
    recommends closing it.
- C1 (backward NG replication) is FROZEN, AWAITING FUNDS:
  - the calendar probe passed;
  - the 2010-2019 calendars (six CME groups, plus NGS, WPSR and FOMC releases) have 0 unsourced dates;
  - frozen in commit 1680982 (prereg sha256 afc5c10f...);
  - q reproduced exactly (q_h60 0.033735, q_hF 0.083193);
  - M1 fitted once (payload sha256s 9c2d9986... and 153c2bdc...), which Fable reran bit-identically.
  - It needs an acct-2 top-up of at least $41.41 (quote $57.74), then one completion session.
- Harness v10 (dc93e9b, manifest fde3a49c...):
  - adds the hist plans, stores, calendars and the append-only trial registry;
  - the E.14 caps are 0.00, and the acct-2 cap is unchanged at 249.67.
- Spend $0.00 (738 quote lines). Funds: acct-1 $1.61, acct-2 $18.07. N stays 471. Holdouts all_ok, 0 unlocks.
- Fable reviews:
  - the freeze review returned APPROVE WITH FIXES; its one BLOCKING finding (the later-harness clause) was fixed;
  - the verification matched every verdict number.
  - Incident: the verifier briefly printed two GEX rows' values, after the stop.

### Session cost

