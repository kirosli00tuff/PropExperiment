# Stage E.18 rulings (lead)

All times PDT, from `date`. Findings are in reports/stage_e18_review.md.

## Step 2: DiffReviewer-FableXHigh (APPROVE WITH FIXES; 0 BLOCKING, 1 SHOULD FIX, 9 NOTE; review 11:58-12:14)

- R-1 (S-1, SHOULD FIX) accepted and fixed before the freeze: section 3's exempt criterion no longer says "as in
  training" (false read literally: E.12 had g17_mbt applicable on 87 / 84 NG rows). It now reads "the treatment
  section 2 gives an unlisted or own-cluster leg, as training gave MBT before its listing" (the reviewer's wording).
  Fixed in make_c1b_text.py replacement 4, the text regenerated (12:14), the diff regenerated (12:15).
- R-2 (N-1) accepted: the criterion sentence now says why CL qualifies although it is listed ("the Stage E.18 prompt
  and V31 name both; CL is listed, so for CL the operative test is section 2's 'not applicable by design', the
  prompt's stated reason").
- R-3 (N-2, N-3) accepted as text-only precision: section 2 names the composite H5 beside H1 and H4; section 11 names
  E.17's ext2010h session constants among data/config.py's v12 changes.
- R-4 (N-6) accepted in the text, not the code: section 9 step 7 names the result path
  reports/stage_e18_c1b_result.json. The CLI keeps C1's required --out; the run-once guard is the fixed marker path
  (evaluate.preconditions refuses when the marker exists, whatever --out is), so no code change is needed.
- R-5 (N-4, N-5, N-7, N-8, N-9) no action: the result's code_sha256 will list c1b.py beside C1's ten files (expected,
  and useful); C1's log and schema strings stay (changing them would touch C1's code); the test misses do not weaken
  clause 2's coverage; the text change went through the generator and the diff was regenerated (N-8); the
  long-established contracts' launch dates stay [unverified] (no doubt; the two dates that matter are verified).
