=== PURCHASE_SUMMARY ===
Nothing was bought: DATABENTO_API_KEY3 was absent by name from 16:53 through the 20:30 PDT deadline (the delta
review gave GO at 17:22). No Databento call was made; acct-3 keeps its USD 125. The user has since put the pilot on
hold (V47, 21:53-21:57) until a QM volume check (E.30) passes and the spec is revised.
=== PILOT_SUMMARY ===
Not run (no data). The code passes 204 of 204 tests; the exact commands are in section 3.
=== DECIDE_SUMMARY ===
how to revise the pilot spec if QM passes E.30 (V47), or which contract replaces QM if it fails; the review
standard; the v2 rulings and the Topstep fee reading (section 7).
=== EVENTS_TAIL ===
- 19:15 user commit 84704b4 (V46, the E.29 prompt) appeared during the wait; not this stage's file, not staged.
- 20:25 the key watch's planned end; it reported completion (exit 0), but its output file was on /tmp (RAM) and was
  lost in the reboot.
- 20:30 purchase deadline passed with the key absent: nothing bought (S3).
- 20:42 the laptop rebooted (uptime -s 20:42:39). 21:54 session resumed; the user confirmed the key still absent. The
  key watch was not restarted.
- 21:58 user commit 54f07ab (V47: QM research, the pilot on hold, acct-3 kept; the E.30 prompt), seen at the end
  checks; not this stage's file, not staged. Section 7 follows it.
- @@T_S5@@
=== PURCHASE_DETAIL ===
none. No quote was taken either: a quote needs the key, and the spend rule (RS-08) approves exactly a fresh quote
logged just before the buy. The ledger's line count and sha256 are the same at session 1's start, session 2's start
and the end (section 2). The commands below buy the frozen spec, which V47 has put on hold; they apply only if the
user lifts the hold with the spec unchanged. From work/B_pilot/README.md sections 2-4 (P=reports/stage_e28_briefs/
work/B_pilot; B = acct-3's balance, at most 125.00; D = the first trade date the span search returns, no later than
2024-01-12; APPROVED = exactly the fresh quote):

  ```bash
  uv run python $P/pilot_pull.py --span-search --root QM --balance-usd B --out $P/runs/span_QM.json
  uv run python $P/pilot_pull.py --quote --root QM --first-trade-date D --out $P/runs/quote_QM.json
  LOG=$P/runs/buy_QM.log
  setsid nohup bash -c "nice -n 10 uv run python $P/pilot_pull.py --buy --root QM \
      --first-trade-date D --balance-usd B --approved-usd APPROVED >> $LOG 2>&1; \
      echo \"rc=\$? \$(TZ=America/Vancouver date '+%F %T %Z')\" >> $LOG" > /dev/null 2>&1 &
  ```

  Then verify.py (README section 5) with the required --purchase-record. "ACCOUNT_3 SAFE TO WIPE" goes into the STATE
  file with the time only after verify.py exits 0, or 3 for data-quality findings only (RS-09).
=== PILOT_DETAIL ===
not run (no data). Command (README section 6), DBN being the verified file under
  /mnt/large-storage/market_data/PropExperiment/data/vendor/databento/GLBX.MDP3/mbp-1/QM_v_0/:

  ```bash
  OUT=$P/runs/measure_QM; LOG=$P/runs/measure_QM.log
  setsid nohup bash -c "uv run python $P/measure.py --root QM --tick 0.025 --fee-side 0.1368 \
      --fee-side-alt 0.296 --sim-rule trade_through_only --dbn $DBN --out-dir $OUT --workers 2 \
      --label Topstep >> $LOG 2>&1; \
      echo \"rc=\$? \$(TZ=America/Vancouver date '+%F %T %Z')\" >> $LOG" > /dev/null 2>&1 &
  ```

  measure.py sets nice 10 itself. Its run time on real data is not measured.
=== OC_TAIL ===
- No quote was taken while waiting, though a quote is free: a quote needs the key, and the spend rule wants a fresh
  one right before the buy.
- After the reboot the key watch was not restarted (user instruction); the key's absence after 20:30 rests on the
  user's word and on the end check by name.
- V47 (committed 21:58, during S5) was read and section 7 written to follow it: no purchase is recommended, and the
  open items are framed around E.30 and the spec revision V47 asks for.
- Commit scope: this stage's documents and the briefs' notes, tables, scripts, tests and logs; not the raw fetched
  pages under reports/stage_e28_briefs/pages/ (876 MB with duplicates), the CFTC COT downloads under work/A1_*/cot/,
  or raw .html/.xml/.js under work/, as in E.23 and E.25 (whose pages are untracked). They stay on disk.
- cost/per_agent.py changed to print PDT times and a minutes column; session 1's table was regenerated (tokens
  unchanged).
- Session 2's cost was computed just before the commit; the few calls after it (staging, the commit, the closing
  reply) are not in its table.
=== DECISIONS ===
Already decided by the user in V47 (21:53-21:57): the pilot purchase is on hold; acct-3 is kept, not wiped; no
QM-only purchase until E.30's QM volume check passes and the pilot spec is revised. What remains open:

Pro-fit: runs in a short Pro session (opus high, at most 2 workers). Max-sized: needs Max usage, Fable or a long
session.

1. **The spec revision, if QM passes E.30 (Pro-fit for the drafting and code; the review is Max-sized if Fable).**
   The frozen spec and the code pin QM as the only root, the request end at 2024-02-29T22:00:00Z and one purchase on
   acct-3. Each of V47's changes touches those guards. A synchronized CL top of book is a second contract, which
   every pilot_pull mode now refuses (RD-01). A 2025-2026 sample lies after 2024-03-01, where E.28's prompt forbade
   any read or purchase (research window, holdout-2, embargo), so it needs the user's ruling on those windows as well
   as the separate approval V47 names. A back-of-queue model beside trade-through-only is a new measure path, and the
   kill rule is a new pre-purchase declaration. So the revised spec needs a new freeze, code changes, tests and an
   independent review before any purchase. Recommendation: write it as a new spec file (keep the frozen one and its
   hash as the record) and review it with Fable when available.
2. **If QM fails E.30: which contract replaces it (Pro-fit).** In stage_e28_ranking.md's variants, Topstep x ZM leads
   with OC-1 off, followed by MGC pairs. V47 item 4's research on ZM and MGC feeds this. Recommendation: choose the
   replacement by the ranking with OC-1 off for the excluded contract only, and re-fill a new spec for it.
3. **Review standard for any later purchase (Pro-fit).** Accept an Opus stand-in review in a fresh context (V46
   item 5, while Fable is unavailable) or wait for Fable xhigh. Recommendation: for a bounded pilot-only spend, the Opus
   stand-in is acceptable. Have Fable check the pilot's numbers before any verdict rests on them.
4. **The v2 rulings (Pro-fit).** RR-01, RR-03, RR-04 and RR-05 were written after the v1 top pair was known.
   Recommendation: accept; RR-01 is the spec's literal text for a candidate with no evidence (R_delta.md, section a).
   Alternative: v1, under which Topstep x QG leads.
5. **Topstep's QM fee (Pro-fit).** USD 3.42 per round trip (per-product, primary) or USD 3.70 per lot read as per
   side (conservative, 0.296 tick per side). The measurement reports both; which governs a verdict is the user's
   call. Recommendation: check Topstep's current fee page or ask support before any measurement is read.
6. **Unfinished review items (Max-sized if done by Fable).** R_delta.md lists three items it did not finish: a
   field-by-field v1/v2 diff, the rank-10 tie against the tie rule, and E for the 37 rows with a non-numeric input.
   It confirmed the top five by its own recomputation.
7. **Next steps by size.** Pro-fit: E.30's volume check, the spec revision and its code, E.29's simulation (its
   prompt, line 24, allows it "after E.28b ends without one"). Max-sized: a Fable review of the revised spec, the
   methods brief's Phase 1 (one contract, a five-rung model ladder counted into N, purged and embargoed CV, Fable
   reviews) and Phase 2's pooled model on 2-3 contracts (GPU, more data purchases).
