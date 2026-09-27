# Stage E.3 member rulings and the K2 cluster freeze (Task 4)

Written by the Stage E.3 lead (Opus 5.5, xhigh), 2026-09-27 00:30-00:35 PDT, after the fidelity audit
(reports/stage_e3_member_audit.md part 1, MemberAuditor-FableXHigh, 0 BLOCKING, 0 SHOULD FIX, 12 NOTE) and
before any member has run on data.

## 1. Rulings on the audit findings

No BLOCKING or SHOULD FIX finding exists, so no member code changed after the audit. The 15 audited files
(reports/stage_e3_briefs/k2_files_pre_audit.sha256) were re-checked at 00:29, all OK, before the freeze.

| Finding | Ruling | Change |
|---|---|---|
| N-1 write_k2_freeze.py needs the repository root on sys.path | Accepted. Run with `PYTHONPATH=.`, as the freeze was written at 00:29. The script is a lead tool, not member code, and it is not frozen. | none |
| N-2 two copies of the asdict open read | No change. Each copy is one line with the ruling's comment or docstring, and merging them would couple the two coders' helper modules. | none |
| N-3 D6 CP1 takes the first bar's open where MES F3.3 used its close | A property of the frozen D6 text, which governs the ports (D line 373). The code follows D6. Reported in the return. | none |
| N-4 L-15's time filter is not exercised by any calendar row | No change. The filter is correct by reading, as the auditor confirmed. Every one of the 57 FOMC and 86 ISM rows is at the rule's time, so the table would be the same without it. A new test now would change the audited test file for no change in any trade. | none |
| N-5 CP2's window end is the literal 15:08 | No change. Members cannot import rules.sessions, and only the coverage check uses the window. | none |
| N-6 S0.12's aucpre window leaves out the 09:00 T_a (2019-12-24) | Clarification: S0.12's table governs, and L-17's "union over T_a variants" means the research-window variants 10:30 and 12:00. The only 09:00 T_a is an early-halt date, which is never traded, and it is in the confirmation window, which the coverage check does not measure. | none |
| N-7 CP3 does not read O_d | Equivalent to the frozen rule: no condition uses O_d, and the 07:20 bar is still required. | none |
| N-8 some boundaries pinned only by the auditor's scenarios | No change. The auditor's nine engine scenarios (reports/stage_e3_briefs/audit/scenarios.py) are the evidence and are cited in the return. | none |
| N-9 the two exit helpers differ on a same-signed pending order | No trade can differ: no K2 member can create that state. | none |
| N-10 the ISM fill guard concerns ZN and ZB, not TN | The frozen D9.5a and the frozen release calendar (E.2b ruling OC-N) govern. Informational. | none |
| N-11 the FOMC table starts 2019-05-01 | Harmless: the runner's window bounds the dates. | none |
| N-12 CP2 relies on the engine's flatten across a trade-date change | Documented reliance on D6's "or the engine's forced flatten at F". | none |

## 2. Rulings made during coding (Task 2)

- **R-T2-1 (00:11).** The frozen static check (screening.stage_e_freeze.check_member_source) refuses the
  attribute name `open`. A bar's open price is therefore read as `dataclasses.asdict(bar)["open"]` (cp1.py
  lines 54-57, _event_common.py lines 72-75), only on the bars that need it. The auditor confirmed it returns
  the bar's own field and opens no file (audit section 4).
- **L-23 (00:08).** The C9 XML check (reports/stage_e3_auction_xml_check.md): 340 of 340 agree, so
  DROPPED_AUCTIONS is empty. The two reopenings re-keyed by original_security_term (2019-11-05 10Y and
  2026-01-26 5Y) stay as the frozen text keys them (specs L-23). Flagged for the user.

## 3. The cluster freeze

- Written 2026-09-27 00:29:42 PDT (created_utc 2026-09-27T07:29:44+00:00) by
  `PYTHONPATH=. PYTHONPYCACHEPREFIX=<fresh scratch dir> uv run python reports/stage_e3_briefs/write_k2_freeze.py`,
  through screening.stage_e_freeze.write_cluster_freeze.
- File: reports/stage_e_k2_member_freeze.json (read-only, 12,588 bytes), schema stage_e_member_freeze/1.
- **Cluster freeze sha256: 8815a775e74996419b57751b1104ffa07cd4b3450eb18a9a92c6cbbd5615b7c5.**
- It holds 44 declarations (ordinals 1-44, specs S0.2) over 14 files: strategy/members/__init__.py (empty) and
  the 13 files of strategy/members/k2/. Checked at 00:31: load_cluster_freeze and verify_cluster_code pass,
  and all 44 labels resolve to factories whose member name equals the label and whose one leg is the declared
  root.
