# Brief: ConfirmAuditor-K4-FableXHigh, Part 1 (Stage E.5 Task C3: the K4-ngpre-01 table amendment audit)

Repository: /home/kiros-li/Documents/GitHub/PropExperiment. Read CLAUDE.md's "Context hygiene" paragraph first. Times PDT.
You are an independent auditor (Fable): you wrote none of what you check. You do not spawn workers. Part 2 (the
recomputation of K4's confirmation verdicts, Task C6) comes later as a follow-up message to you; do not start it.

## Objective (one)
Check that K4-ngpre-01's literal NGS table changed by exactly C9's drops of its confirmation window and nothing else, that
each drop is right against the check and its sources, and that the research series is unchanged.

## Inputs
- The rule: reports/stage_e0_catalog_K4.md lines 135-170 (C9, EC-NGS, the two drop rules). Lead ruling R-C3-1: the five
  `drop_actual_differs` rows on or after S_NG = 2019-05-06 (reports/stage_e_start_rule_K4.json) are dropped; no row is
  added (the four Friday releases are not substituted: only a drop is allowed).
- The check: reports/stage_e5_ngs_check.json and .md (ReleaseChecker-OpusMed; 252 rows 2019-05-06..2024-02-29: 247 keep,
  5 drop_actual_differs) and its saved pages under data/vendor/release_pages/e5/ (manifest.jsonl there).
- The change: `git diff HEAD -- strategy/members/k4/_releases.py tests/test_e4_k4_members_b.py` and the coder's report
  reports/stage_e5_k4_table_amendment.md.
- The new K4 cluster freeze reports/stage_e_k4_member_freeze.json (written by the lead after the change; the old one,
  sha256 cf066cb0507134e2553781f42699165b471be45ebec6b07bfb0d75680e879d1a, is at HEAD: `git show HEAD:reports/stage_e_k4_member_freeze.json`).

## Check, at least
1. The NGS tuple lost exactly the five rows and nothing else; every other table in the file (WPSR, API, NYSE, holidays)
   and every other constant are byte-identical except the declared drop record, E.5 check constants, docstring and counts.
2. Each of the five drops is right: open the saved capture(s) the check cites for that week and quote the passage (EIA's
   "Released: ... Next Release: ..." line, or the NGWU notice for 2023-11-09) and the schedule capture before it. Also
   spot-check at least 10 `keep` rows spread over 2019-2024 the same way (verify date and time against the saved capture).
3. The new freeze differs from the old one only in strategy/members/k4/_releases.py's hash (members, ordinals, legs,
   factories unchanged); `verify_cluster_code` passes on it.
4. The research series is unchanged: run K4-ngpre-01's research window under the harness in force with the new freeze,
   `PYTHONPYCACHEPREFIX=<fresh dir outside the repo> nice -n 10 uv run python -m screening.stage_e_runner --harness-sha256
   9a8ebe7364beb7980eaea923888e06c2da253b7ff8ce2ce771b55045caf22f87 --cluster K4 --member "K4-ngpre-01 NG" --window research
   --research-root data/processed --step2-root data/processed_step2 --out-dir reports/stage_e5_briefs/audit_k4_research/`,
   and compare its record and trip list field by field with reports/stage_e4_k4_screen/K4_K4-ngpre-01_NG_research.json
   and _trips.json: only harness_sha256, cluster_freeze_sha256, created_utc, power and the trip file's record_sha256 may
   differ (the series, daily_net_usd, every trip identical).
5. The test file: the recomputation applies both checks and pins the E.5 check's sha256; run
   `uv run pytest -q tests/test_e4_k4_members_b.py`.

## Output
reports/stage_e5_k4_audit.md, "Part 1: the table amendment": each check VERIFIED, VERIFIED WITH NOTES or DISCREPANCY,
with the evidence (quoted passages, commands and their result lines). Scratch under reports/stage_e5_briefs/audit_k4_*.

## Boundaries
Read-only on every repository file except your report and your scratch directories. No confirmation-window run (the
confirmation window is not read before the list is hashed), no commits, no freeze writing, no web (the saved pages
suffice; if one is missing, say so).

## Return
The report path, a summary of at most 150 words (each check's verdict), and anything you could not check.
