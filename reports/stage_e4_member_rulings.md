# Stage E.4 Part 1, Task 4: the lead's rulings on the K4 fidelity audit

Lead: Opus 5.5 (xhigh), 2026-09-27, 04:30-04:45 PDT. Audit: reports/stage_e4_member_audit.md Part 1
(MemberAuditor-K4-FableXHigh, fable xhigh, 04:12-04:30, which wrote none of the code, specs or tests):
BLOCKING 1, SHOULD FIX 0, NOTE 9. All 12 trials implement their frozen entries and nothing more; every
literal table recomputed from its sources is equal row for row; 236 tests pass; 31 literal mutants killed;
no vacuous test.

## BLOCKING

**B-1. DROPPED_WPSR 2025-07-16 is not supported by its cited evidence.** Ruling R-T3-1: accepted; the
release is restored (verdict keep). The capture the checker cited (20250716160433, "95 minutes after the
slot, still the previous release") was served from the 2025-07-15 snapshot (manifest effective_url), and
the real 07-16 12:04 ET capture already shows the release; C9's first drop rule does not fire. Fix, inside
the frozen entry, no member module changed:
- reports/stage_e4_release_check.json row WPSR-2025-07-16: verdict keep, with the original verdict and
  reason kept under `lead_ruling` (sha256 now 4c71d7985c3471a86cbbd88b613b9a2f81d1b08f7aa60eb442f3c77834a04896);
  reports/stage_e4_release_check.md: counts and a lead note;
- reports/stage_e4_member_specs.md section 11 and K4-L-15;
- MemberCoder-B-OpusXHigh (resumed) regenerated strategy/members/k4/_releases.py from
  reports/stage_e4_briefs/gen_k4_releases.py and updated tests/test_e4_k4_members_b*.py (section below).
Effect: apipre, eiamom and eiafade each have one research-window event more (56 standard weeks).

## NOTE

| Note | Finding | Ruling |
|---|---|---|
| N-1 | NGS 2025-12-29's `latest_prior_path` names the 11-28 file for the 12-03 capture | Documentation only: the CDX digests of the 11-28..12-03 captures are identical. No change |
| N-2 | D9.5a moves ngpre's 09:30 CT entry fill to 09:32 on Wednesday 12:00 ET storage days (2025-06-18, 11-26, 12-31), because the frozen calendar lists NG among the WPSR's products | Harness behaviour (specs section 0, updated at 04:14); listed in the return beside CP1's FOMC case. No change |
| N-3 | the "D9.7" tests use a test-only rules subclass, because MCL and NG are DCB-only (no hard price limit) | Adequate: the tests pin the member's reaction to an engine-forced exit (S0.7). D9.7 never binds on K4's vehicles. No change |
| N-4 | cp2's resend of a refused 75-bar exit is untested | The exit cannot be refused for min-hold and any other refusal is the engine's flatten path. No change |
| N-5 | ovr.py's WINDOW_END_CT is a literal equal to the last decision time + 60 minutes; coverage only | Cosmetic. No change |
| N-6 | apipre's Tuesday minutes (offset 0) are measured on every research date | The lead's reading K4-L-07 (a proxy, as E.3-L-17). No change |
| N-7 | F-7: ovr.py's energy-specific content is the clock, the calendar import and N-5's literal | Confirms F-7. Part 2 (K5) checks K5-ovr-01 against it |
| N-8 | K4-L-01: pre-window rows unchecked, including an NGS "(Updated)" row on 2025-01-08 whose earliest marked capture is after the release | In neither window. A Tier A event member's confirmation session runs C9 on 2019-05..2024-02 first (K4-L-01). No change |
| N-9 | three NGS rows kept "unverifiable" | C9's letter; K4-ngpre-01 NG carries "calendar partly unverified" into the return. No change |

## Readings

The auditor agreed with every lead reading (section 10 of the specs), the adopted E.3 readings and K4-L-01..
K4-L-14, and with K4-L-15 for 2026-05-28 under its caveat.

## The fix (R-T3-1)

Applied 04:36-04:38 PDT: the lead amended the release check (JSON row and .md), specs section 11 and K4-L-15;
MemberCoder-B-OpusXHigh (resumed) removed 2025-07-16 from SECTION11_WPSR in the generator, regenerated
_releases.py (WPSR 369 rows, 317 standard; research window 62 rows, 56 standard; DROPPED_WPSR 2025-12-29 and
2026-05-28) and updated its pin tests; its reference command ended `149 passed in 1.79s`. No member module
changed: against reports/stage_e4_briefs/k4_files_pre_audit.sha256 exactly three files differ
(strategy/members/k4/_releases.py, tests/test_e4_k4_members_b.py, tests/test_e4_k4_members_b_eia.py).
Check by the lead at 04:40: the auditor's own script (reports/stage_e4_briefs/audit/recompute_tables.py, independent
of the generator) reports WPSR 369 EQUAL, NGS 372 EQUAL, DROPPED_WPSR == the check's non-keep rows,
FEDERAL_MONDAY_HOLIDAYS 46 EQUAL, ENERGY_FULL_SESSIONS 1,784 EQUAL; apipre 56 and eiamom 56 standard events in
the research window. The auditor re-confirms the table as item 0 of Task 6.

| File | sha256 after the fix |
|---|---|
| strategy/members/k4/_releases.py | 35bd4730d12386f4e31f7f045d95afe9a9f7843c686899557a944bcfa68dd1f0 |
| tests/test_e4_k4_members_b.py | 06fd77e62865f6dfc8f9b4e7b9535b8a2ed3e4136814d0d422f5d2ba3b79616b |
| tests/test_e4_k4_members_b_eia.py | d6037d73f2d9b6f6241d7638b4edb5a386274de2def73f7972c8e2cc0b12be52 |
| reports/stage_e4_briefs/gen_k4_releases.py | b2e067bb1ced44feda4f13bce0082ef769983544d414d8dd503e5a6967f78d16 |
| reports/stage_e4_release_check.json | 4c71d7985c3471a86cbbd88b613b9a2f81d1b08f7aa60eb442f3c77834a04896 |

Cluster freeze (write_cluster_freeze, 04:33): reports/stage_e_k4_member_freeze.json, sha256
cf066cb0507134e2553781f42699165b471be45ebec6b07bfb0d75680e879d1a, 12 members, 14 files; load_cluster_freeze +
verify_cluster_code OK.
