# Stage E.22 Part A: review of the four confirmation lists before any confirmation read

Reviewer: ListReviewer-FableXHigh (Fable 5.1, xhigh), independent of the E.22 lead (Opus 5.5) who wrote the
lists. Brief: reports/stage_e22_briefs/brief_list_review.md. Written 2026-10-16 02:25-02:45 PDT. Read-only
except this file; dry runs only, into the scratchpad; no confirmation-window bar value was read by anything I
ran (the runner's `--dry-run` reads timestamps and trade dates only and wrote nothing; the four scratch out-dirs
do not exist afterwards).

Reviewed as written: reports/stage_e22_k5_confirmation_list.json 18c9c0e9de5a5a03..., _k3_ 1ce822ad09240ed7...,
_k6_ f2c671a5b9ba5a21..., _k8_ 627d1fe168fb5721..., reports/stage_e22_confirmation_list.md ce5d38a5c87c6b89...
(sha256 recomputed by me; all equal the lead's). Harness v13 dd2bcc6025144e0d... (= sha256 of the committed
reports/stage_e2b_harness_freeze.json at e40ca85).

## Verdict in one line

No BLOCKING finding. 5 SHOULD FIX (one list-builder bug, two labelling or ruling gaps to settle before the read,
two commit-scope items), 7 NOTE. Every one of the 72 frozen trials is listed once with the right identity, tier,
D9 labels, source-overlap label, eps, seed and window; every power object equals its v13 research re-run; all
four dry runs resolve every member under the committed harness.

Counts: BLOCKING 0 | SHOULD FIX 5 | NOTE 7.

## Findings

### SHOULD FIX

**F1 (SHOULD FIX). No list hashes the start-rule file that gave its S_X; build_list.py reads the wrong
provenance key.** All four lists; field `inputs`. `screening.stage_e_start_dates.start_dates_for` returns
provenance entries as `{"s_x", "step2_sha256", "files": [{"path", "sha256"}]}` (screening/stage_e_start_dates.py:716-717);
reports/stage_e22_briefs/build_list.py:139 collects `v["file"]` (singular), which never matches, so the start-rule
files are silently dropped from `inputs` (my verifier: `start-rule files hashed in inputs ([])` for K5, K3, K6, K8).
E.5's K4 list did hash reports/stage_e_start_rule_K4.json, so this is a regression from the precedent, and the
lists' windows (K5's MGC -> GC 2019-05-06, K8's six roots) have no pinned provenance inside the hashed artifact.
Fix: `v["files"]` and iterate the list (`for f in v["files"]: inputs[f["path"]] = f["sha256"]`), rebuild the four
JSONs and the md (the lists are not yet committed, so the rebuild costs nothing but new hashes). Expected
additions: K5 -> stage_e_start_rule_K5.json and _K8.json (GC); K3 -> _K3.json; K6 -> _K6.json;
K8 -> _K8.json and _K4.json or _K8.json for MCL (whichever `load_start_entries` merges; both give 2021-07-12).

**F2 (SHOULD FIX). K6-limitcont-01 LE: "power check undefined" has no ruling; a zero-trip outcome blocks the K6
null statement.** K6 list, ordinal 24, fields `power`, `labels`, `run`. The research series has zero variance
(0 trips in 15 months), so the frozen power check cannot measure n_b (`power.status` "power check undefined",
copied verbatim into the list; the replay's one K6 difference is this cluster-file entry). The list runs it as a
plain covered Tier B trial, which is right by the letter (D4 labels "inconclusive by design" only when n_b >
supply; NULL_CRITERIA_E 5 says the same), and the harness then decides: zero trips or SE_boot = 0 on the
confirmation window reads "inconclusive" (stage_e_verdict.py:492-498), and an inconclusive covered trial makes
the cluster's statement "no statement" (NULL_CRITERIA_E 1 and 6; `null_statement` :622-644). Its Sharpe would be
0.0 in K6's DSR variance set (`moments` returns 0.0 at sd 0, :178-184) and a constant row in PBO, so neither is
undefined. The point: K6's null statement hinges on whether LE limitcont trades at all in 2019-05..2024-02, a
foreseeable outcome the D4 check could not classify, and no ruling in partA_rulings.md says so. Deciding it after
the read would be a post-hoc choice. Fix: one ruling (R-E22-A16) before the commit: "K6-limitcont-01 LE: power
check undefined (zero-variance research series); listed run and covered; a zero-trip confirmation outcome reads
'inconclusive' and K6 then gets no statement (NULL_CRITERIA_E 3, 6); accepted before the read." Put it in
partA_rulings.md (a hashed input; the F1 rebuild carries it) and, if the lead wants it in the list itself, a
NOTES entry for the trial. No label change: "inconclusive by design" would misstate D4.

**F3 (SHOULD FIX). K8-wkndbtc-01 MNQ: the labels mix two readings of D2/D4 and the prompt's A2.** K8 list,
ordinal 4, fields `labels`, `price_path`, `s_x`, `power`; reports/stage_e22_untestable_K8.json; the MNQ entry of
reports/stage_e22_price_paths.json. The brief asks whether R-E22-A5 (MNQ -> NQ) is defensible or whether the
trial should read "untestable (missing MNQ)". My reading:
- D2 (docs/STAGE_E_DESIGN.md:173-177) and D4 (:265-268) substitute the full-size contract for "a micro whose own
  history is too short for D4's power check" / "micros listed after 2019-05". MNQ was listed 2019-05-06, the
  program's earliest S_X; its history is not short, it is not owned (never bought: E.9). R-E22-A5 reads "the
  power check fails on owned data", which turns "not bought" into "too short". That is a stretch of D2/D4's text.
- The prompt's A2 names MGC and MBT as the short-history micros, then rules separately: "a member whose required
  leg is not owned for its window is labelled 'untestable on owned data' with the missing leg named, not bought".
  MNQ is wkndbtc's traded, required leg and is not owned: by the prompt's own rule the trial is "untestable on
  owned data (missing leg MNQ)". On the other side, A2 lists NQ among Part A's owned stores, which only makes sense
  as MNQ's path, and V39 delegates "full-size price paths where D4's power check fails"; so the planner expected
  the lead's reading.
- Under the lead's reading the "untestable" label is a misnomer: the declaration names missing_leg "MBT", but MBT
  is owned (R-E22-A3, step 2 store from 2021-05-03); what fails is MBT's power (supply 34 < n_b 43: that is
  exactly D4's "inconclusive by design"), and BTC is an optional U8 substitute, not a required leg. Under the
  strict reading "untestable (missing leg MNQ)" is exactly right and "inconclusive by design" would not be
  computed from an NQ-keyed window. The list carries both labels and the NQ price path, so it borrows the label
  from one reading and the window from the other. `not_run_label` picks "untestable on owned data" first, so the
  verdict's not-covered reason will read "untestable", which under R-E22-A5 misdescribes the facts.
- What changes in K8 under either consistent option: nothing in the verdict. The trial is not run either way;
  Holm m = 2 with wkndbtc at p = 1 (R-E22-A13); DSR variance and PBO over the three run trials (V14 c, L-E5-3,
  R-E22-A14); covered set {H30, HEOD, oilcad}. What differs is the list text: under the strict reading the K8
  list's `start_dates`, `confirmation_window`, `price_paths` lose MNQ, the trial's `s_x`, `price_path` and
  `power` change (no MBT-limited power check), the declaration's missing_leg becomes MNQ, and the MNQ entry
  leaves reports/stage_e22_price_paths.json (which also removes N-8 below). Under the lead's reading kept
  consistently, the declaration becomes a reason-only "inconclusive by design" entry (the runner accepts it,
  harness_change.md O-5) and the "untestable" label is dropped; `run: false` then rests on the by-design label.
Fix (lead's choice, both pre-read and verdict-neutral): adopt one of the two consistent labellings and rebuild
K8's list and declaration, or record in partA_rulings.md why the mixed labelling stands and what the not-covered
reason will say in the return. My recommendation is the strict reading: it follows the prompt's A2 wording, needs
no stretch of D2/D4, and removes the vehicle-keyed MNQ -> NQ declaration that would otherwise apply to K1.

**F4 (SHOULD FIX). N = 533 rests on an uncommitted ledger line.** All four lists, field `program_n`.
ledger/trial_registrations.jsonl is tracked-MODIFIED: HEAD has 7 lines (last r006-E21, n_after 532); the working
tree adds r007-E22 (n_before 532, n_after 533, freeze reports/stage_e22_prereg_F1.md 04ef33a6..., which equals
the committed file's sha256, time_local 02:12:01, before the lists at 02:20). So N = 533 was the program N at list
time, as E.5's rule has it (E.5: N at its list), and the v13 `registry_n` check will read 533 at run time. But a
reader of the list commit would find 532 in HEAD's registry. Fix: include ledger/trial_registrations.jsonl in the
list commit (or commit it first).

**F5 (SHOULD FIX). Hashed inputs and the run's inputs are untracked; the list commit must carry them.** The lists
hash reports/stage_e22_briefs/partA_rulings.md, reports/stage_e22_untestable_K8.json and 72 research records under
reports/stage_e22_power_k{3,5,6,8}/; the dry runs read reports/stage_e_start_rule_K3.json, _K6.json, _K8.json;
the lead's scripts are reports/stage_e22_briefs/build_list.py, render_list_md.py, prerun_check.py. All of these
are untracked (`git ls-files`); only price_paths.json, epsilon.json, the amendment, the docs and the K5 start rule
are tracked and clean. prerun_check.py checks that the list is tracked and unchanged, not its inputs. Fix: add
every file above to the "E.22 confirmation lists" commit so the hashes in `inputs` resolve at that commit.

### NOTE

**N-1 (NOTE). The builder leaves an "inconclusive by design" trial `run: true` unless its supply is 0; R-E22-A9
says "it is not run".** build_list.py:88-92 sets `run = False` for a by-design trial only when `supply_days == 0`;
R-E22-A9 ("n_b > supply labels the trial ... and it is not run") and R-E22-A13 (a by-design Tier A trial enters
Holm at p = 1) assume not run always. No trial in these lists is affected: the only by-design trial (wkndbtc,
supply 34) is `run: false` through the untestable declaration. Had it not been declared untestable, it would have
been listed run, produced a record, and entered Holm with its real p_upper (stage_e_verdict.py:543-545), against
A13. If the builder is reused: `run = False` for every by-design trial, and put the member in the `--untestable`
declaration as a reason-only "inconclusive by design" entry, or `check_list_against_plan` refuses (the run:false
set must equal the declared set; runner :805-809).

**N-2 (NOTE). reports/stage_e_start_rule_K8.json records harness 8cd39432..., a speculative uncommitted tree
(STATE A3a/A3b, 01:40:51-01:41:20), not v12 or v13.** The file was not rebuilt under the committed v13 (the
power re-runs were; their `power` fields equal W1's for all 72 records, checked). harness_change.md "Review
fixes" states that W1 -> W2 touched only screening/stage_e_runner.py, screening/stage_e_verdict.py and two test
files, so the start-rule code that produced the K8 file is the committed code; and its values are corroborated
(MCL 2021-07-12 = K4's file; 6C 2019-05-06 = K3's file; MES 2020-02-03 = D.1f's S; GC, NQ 2019-05-06 are the
earliest possible). Precedent accepts start-rule files from earlier harness versions (K5's is v6). Suggest: a line
in the return naming the W1 provenance and the "same files only" attestation, rather than a rebuild (a rebuild
would change the file's sha256 and every K8 power record's `start_rule` hashes).

**N-3 (NOTE). K = 5 is sourced correctly; K4 was tested at K = 9, so the program bound still holds.** D5
(docs/STAGE_E_DESIGN.md:306-308) and NULL_CRITERIA_E:70 define K as the clusters with a non-empty Tier A: K3, K4,
K5, K6, K8 (K1, K2, K7 empty; K9 never a cluster, V21; the ML route's Tier A empty, V23/V24/V38). V14 (b)'s
K = 9 ran "until every cluster and the ML route have been screened"; that condition lapsed (V17, V24, V38).
E.5 tested K4 at 0.05/9 = 0.00556, stricter than 0.01, so the mixed design keeps the program-level family-wise
error at most 0.00556 + 4 x 0.01 < 0.05. Suggest the return states this arithmetic beside R-E22-A10.

**N-4 (NOTE). N = 533 follows E.5's rule once F4 is fixed.** The prompt's A4 says N is unchanged by confirmations
of already-counted members unless E.5 says otherwise; E.5 used the program N at list time (150). Here the
program N at list time was 533 because E22-F1's registration (02:12) preceded the lists (02:20). Consistent;
also the conservative direction for DSR. Nothing to change.

**N-5 (NOTE). R-E22-A13 matches the v13 verdict code.** `edge_chain` takes `rows[m].get("p_upper", 1.0)` for every
Tier A trial, so a not-run Tier A trial enters Holm at p = 1 with `m` counting it (stage_e_verdict.py:543-545);
`covered` is false for it (:284-285); the not-covered reason is "not run: <label>" (:627-630). The chain verdict
string for such a trial is "no edge" (first failing step "holm"; harness_change.md O-4), which for wkndbtc would
read as a tested negative. Suggest the return words it "not tested on owned data; Holm p = 1 by rule
(R-E22-A13)".

**N-6 (NOTE). E.8's lead labels are carried as notes, and R-E22-A15's "unit history not separately verified"
label is carried nowhere.** LIST_LABELS is closed (stage_e_verdict.py:112-116), so "Tier A on a single trip",
the K6-L-07 and D9.7-proxy labels and the K6 cp2 tick-history label ride in `notes`, which the verdict ignores;
R-E22-A2 says the single-trip "label is carried" (it is, as a note). R-E22-A15 announces a label "unit history
not separately verified" that appears in no list field. Suggest: say "note" in the return, and add A15's wording
to NOTES (per cluster) in the F1 rebuild if the lead wants it in the hashed artifact.

**N-7 (NOTE). The price-path declaration is vehicle-keyed; the MNQ -> NQ entry would govern any future K1 run
under v13.** reports/stage_e22_price_paths.json is pinned and keyed by vehicle (harness_change.md O-2;
harness_review.md N-14); K1's eleven MNQ trials were screened on MNQ's own research bars. No K1 confirmation is
planned (K1's Tier A is empty), so this is latent; adopting F3's strict reading removes it, otherwise a `members`
or `cluster` scope on the declaration (a harness change) or a line in the return.

## What I verified, and how

Everything below was computed by my own script (scratchpad lr_verify.py, 1,658 checks passed, 4 real failures =
F1) from the sources, not from build_list.py's logic, plus hand reads of the rules.

1. **Identity (brief item 1).** For each cluster: `load_cluster_freeze` gives 11 / 30 / 27 / 4 members (K5, K3,
   K6, K8); the list's ordinals equal the freeze's; each trial's `member` equals the freeze label, `vehicle` the
   single traded leg, `legs` the frozen legs in order; `cluster_freeze_sha256` equals the loaded freeze's sha256
   and the sha256 of reports/stage_e_<k>_member_freeze.json (K5 1d0c974f..., K3 c4fb5da4..., K6 a6f8b497...,
   K8 99f5a6ce...). Tiers equal the screening cluster records (stage_e4b/4c/8/9 `tiers.members`): Tier A exactly
   K5-fomc-01 MGC, K3-ldnrev-01 6E, K6-limitcont-01 HE, K8-flight-01 HEOD MGC, K8-wkndbtc-01 MNQ; excluded exactly
   K5 cp1 MHG, cp2 MHG, pmfix MGC, K3 cp1 6S, cp1 6N, cp2 6N. D9 labels equal the records' (coverage_below_0.95 x 5,
   mean_holding_below_10min x 1). Seeds = 20260923 + ordinal for all 72. q_c, eps_ticks and $/day equal
   reports/stage_e2a_epsilon.json `eps_operative` x q_c x tick_value_usd for every vehicle (MGC 71/$71, MHG 27 at
   q 2/$67.50, 6E 12/$75, 6A 11/$55, 6B 8/$50, 6C 9/$45, 6J 10/$62.50, 6S 13/$81.25, 6N 10/$50, ZC 4/$50,
   ZW 4/$50, ZS 5/$62.50, ZM 5/$50, ZL 11/$66, HE 7/$70, LE 8/$80, MNQ 170/$85), as R-E22-A12 lists. Run flags:
   every Tier A/B trial run except wkndbtc (declared); no excluded trial run. This also covers harness review
   R-1 (freeze sha and vehicles), independently of prerun_check.py.
2. **Labels (item 2).** Source-overlap derived by parsing the amendment table's governing column
   (reports/stage_e2a_source_window_amendment.md: 37 members; "not source-overlap" exactly K2-predrift-01,
   K3-ldnmom-01, K3-mehedge-01, K4-ngpre-01, K8-flight-01, K8-oilcad-01) with members absent from the table
   (K5-fomc-01, K5-ovr-01, K6-wasdepre-01, K8-wkndbtc-01) treated as source-overlap by R-04
   (docs/NULL_CRITERIA_E.md:85-86); the lists agree for all 72. "inconclusive by design" appears exactly where
   the re-run's `power.check.inconclusive_by_design` is true (wkndbtc only); "untestable on owned data" exactly
   on the declared member, whose declared missing leg is a frozen leg.
3. **Windows (item 3).** Each trial's `s_x[root]` and the list's `start_dates`/`confirmation_window` equal the
   `products[path_root].s_x` of the start-rule files (MGC -> GC and MNQ -> NQ through the declaration), and the
   files agree wherever a root appears in two (6C in K3 and K8; MCL in K4 and K8). MES 2020-02-03 from K8's
   file (= D.1f). Price paths in each trial equal reports/stage_e22_price_paths.json for its legs; the lists'
   `price_paths` equal the declaration for their roots. Cross-product windows are the runner's intersections
   (dry-run supplies: flight 944 on GC from 2020-02-03; oilcad 569 from 2021-07-12; crushgap 1028 on the union
   of ZS/ZM/ZL blackouts). The MNQ -> NQ question is answered in F3.
4. **Power (item 4).** For 66 trials with a research record whose power ran, the list's power object equals the
   record's `supply_days` and `check` fields one by one; for LE limitcont the raw "power check undefined" object
   is copied verbatim; the 5 excluded trials without a record carry `power: null`. n_b_chosen follows the frozen
   15% rule for every record (analytic unless |sim - analytic| > 15%, then the larger, censored -> analytic;
   screening/stage_e_stats_power.py:240-248); by_design == n_b_chosen > supply for every record; each record's
   member, ordinal, window "research", harness v13 and freeze sha are right; each record's sha256 is in `inputs`
   and unchanged. Replays: c2_compare files K5 23/23, K3 61/61, K8 9/9, K6 54/55 where the one difference is the
   cluster file's `power_check_undefined` (LE limitcont), i.e. power only. W1 vs v13 `power` fields identical for
   all 72 records (my comparison of reports/stage_e22_briefs/power_w1/ with reports/stage_e22_power_k*/).
5. **K and N (item 5).** N-3, N-4, N-5, F4 above.
6. **Outcome knowledge (item 6).** Nothing in the lists depends on a confirmation outcome: the start rule reads
   confirmation-window volumes by design (D4); power uses research series and date counts; the declaration's
   "34 days against n_b 43" is a date count. Departures from "exactly as frozen" are the declared price paths
   (D2/D4), the harness's own calendar on K3's 14 FX_FULL_SESSIONS dates (noted on every K3 trial, R-A2-1) and
   MES read from the Stage D store (v13 N3), all pre-declared.
7. **Dry runs (item 7).** `uv run python -m screening.stage_e_runner --harness-sha256 dd2bcc60... --cluster KX
   --all --window confirmation --research-root data/processed --step2-root data/processed_step2 --out-dir
   <scratchpad>/lr_dry_KX --dry-run` (K8 with `--untestable reports/stage_e22_untestable_K8.json`), under
   nice -n 10, serially, 02:30:02-02:33:25 PDT (K5 30 s, K3 100 s, K6 53 s, K8 20 s); rc 0 for all four; "N members
   resolved, nothing written" (11, 30, 27, 4); no refusal; no out-dir created. Per member, the dry run's s_x, supply
   and price path equal the list's for every trial with a power object (72 lines compared; the excluded trials
   without a research record resolve to a supply the list does not carry, which is right: they are listed, not
   run). Stores: GC 341bb6b5 for every MGC trial; MES Stage D confirmation parquet 82e256b4 for flight.
8. **Markdown.** reports/stage_e22_confirmation_list.md embeds the four JSON sha256s and each cluster's summary
   row (sha, freeze sha, run / listed = 8/11, 27/30, 27/27, 3/4) exactly.
9. **Inputs.** Every `inputs` entry of every list resolves to a file whose sha256 is unchanged now (including
   partA_rulings.md, price_paths.json, untestable_K8.json, epsilon.json, the amendment, the three docs).

## Not done

- No start rule was recomputed (it reads confirmation-window volumes; the files are taken as recorded, N-2).
- No bar value, trip or P&L was read; no run, no marker, no commit, no edit outside this file.
- The holdout status command was not run by me (the lead runs it at start and end).

## Recheck (02:40-02:47 PDT, after the lead's fixes)

Rebuilt lists verified: reports/stage_e22_k5_confirmation_list.json d2a230f3f46c7c0b..., _k3_ 43456def5b4f627e...,
_k6_ ebb3d034ed001498..., _k8_ 28ad6f63630681db..., reports/stage_e22_confirmation_list.md 6f2fbf381c95ee57...
(sha256 recomputed; equal to the lead's prefixes; the md embeds the four JSON hashes and the summary rows 8/11,
27/30, 27/27, 3/4). The same independent verifier re-derived every field from the sources: 1,743 checks pass, 0
real failures. Against the version reviewed above, only `created_pdt`, `inputs` (start-rule files added), and
K8-wkndbtc-01's `labels`, `run` reason and `notes` differ; no K5, K3 or K6 trial carries a not-run note, no trial
anywhere carries "untestable on owned data", and every run flag, tier, label, seed, eps, window, price path and
power object is as verified before. K8 dry run with `--untestable reports/stage_e22_notrun_K8.json` into a
scratchpad out-dir: rc 0, 02:40:56-02:41:11, "4 members resolved, nothing written", wkndbtc "not run
(inconclusive by design)", the three run members' S_X, supply (944, 944, 569) and paths unchanged, out-dir absent.

| Finding | Status | Checked |
|---|---|---|
| F1 start-rule files not hashed | RESOLVED | build_list.py:131-133 iterates provenance `files`; inputs now hash stage_e_start_rule_K5+K8 (K5), K3+K8 (K3), K6 (K6), K3+K4+K8 (K8): the merged sources per root; every hash equals the file on disk |
| F2 limitcont LE undefined power | RESOLVED | R-E22-A16 appended to partA_rulings.md (listed run and covered; zero-trip or SE_boot = 0 outcome reads inconclusive; K6 then no statement; accepted before the read); LE's list entry unchanged (run true, source-overlap, power verbatim), as it should be |
| F3 wkndbtc mixed labelling | RESOLVED (lead's choice: the declared reading kept consistently) | labels exactly [source-overlap, inconclusive by design]; run false; reports/stage_e22_notrun_K8.json is a reason-only "inconclusive by design" entry (missing_leg null) matching the power check (34 < 43); reports/stage_e22_untestable_K8.json absent; R-E22-A6 revised records the strict reading (missing MNQ) as the open choice; verdict unchanged (Holm m = 2, p = 1; DSR and PBO over the three run trials); confirm_run.sh points at the new declaration |
| F4 ledger line uncommitted | OPEN UNTIL THE COMMIT | ledger/trial_registrations.jsonl still tracked-MODIFIED with r007-E22 (n_after 533); the lead's plan puts it in the list commit; nothing more checkable now |
| F5 untracked inputs | OPEN UNTIL THE COMMIT | the rulings, the not-run declaration, start rules K3/K6/K8, the four power dirs, the c2 comparisons, the scripts and this review are in the lead's commit plan (STATE A7b); verify with `git ls-files` after the commit |
| N-1 builder by-design run flag | RESOLVED | build_list.py:106-108 sets run false for every by-design trial; :117-118 refuses a by-design trial absent from the declaration |
| N-2 K8 start-rule provenance | RESOLVED | recorded in partA_rulings.md (N-2 note) and bound for the return; file kept, as recommended |
| N-3 K = 5 arithmetic | TO THE RETURN | lead's statement |
| N-4 N = 533 | NOTHING TO CHANGE | as before |
| N-5 "no edge" wording for a not-run Tier A | OPEN (return wording) | lead's call at the return |
| N-6 E.8 labels as notes; A15's label | OPEN, non-blocking | notes unchanged; A15's "unit history not separately verified" still carried nowhere |
| N-7 vehicle-keyed MNQ -> NQ reaches K1 | OPEN, latent | the NQ path stays declared; R-E22-A6 (revised) calls it a v13 frozen input this trial does not exercise; no K1 run planned |

NEW BLOCKING: none. New observations: none that affect the read (the declaration keeps the runner's schema name
`stage_e_untestable/1`, which the runner requires; STATE row A3d still names the withdrawn file as history).

Recheck counts: BLOCKING 0 | SHOULD FIX 5 (3 RESOLVED, 2 open only until the commit) | NOTE 7 (2 RESOLVED,
1 to the return, 1 nothing to change, 3 open and non-blocking).
