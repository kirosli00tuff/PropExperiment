Every decision a lead made on its own, with the reason. Session 1 numbers (OC-1 to OC-7, OC-11) are from
reports/stage_e28_STATE.md and the rulings files; OC-8 to OC-10 are not recorded on disk (session 1's transcript uses
"OC-10" only as a group label for the A3 rulings below), so those choices are listed by content.

Session 1 (Parts C, A and B1/B2):
- OC-1: price statistics in ticks for a candidate with no owned window data are derived from an owned sibling on the
  same underlying price (x_ticks(cand) = x_ticks(sibling) x tick(sibling) / tick(cand)); volume never transfers.
  Reason: the same price process; the alternative leaves 10 micros and minis unscored. QM's rank depends on it.
- OC-2: ADV from owned v.0 front-month bars where owned, else the published figure. Reason: one source per
  contract where possible; a variant OC2_published is shown.
- OC-3: firm reliability: no deduction for an undocumented item; an unknown founding date deducts. Reason: absence of
  a record is not evidence of a problem, but an unknown age is a real risk.
- OC-4: the F (fill) criterion rated on the API platform the strategy would use. Reason: that is the fill rule the
  strategy would meet.
- OC-5: no quote, balance check or purchase before Parts A and C were finished. Reason: the prompt's order.
- OC-6: a C6 rating may not rest only on abstract or snippet evidence at either extreme (no 0, no >= 3). Reason:
  unverified evidence cannot exclude or promote a contract.
- OC-7: futures-broad order-book evidence floors C6 at 2 (the spec's level-2 anchor). Reason: the spec's own words.
- OC-A3-1 to OC-A3-11 (rulings v1, A3_lead_rulings.json, written at 15:13 before any ranking output was read):
  MNG passes the 60-date listing gate by the common inference; unknown D and E components score 1 (variants at 0
  shown); FactTable's QV and C4 readings accepted (variants shown); big-move counts transfer to OC-1 siblings
  (primary; no-transfer variant shown); a 0-contract cap at 50K means not listed; the rest accepted as written.
  BlindScorer's alternatives: the primary ratings stand (C07, C15; F04 A = 2).
- OC-11 (rulings v2, A3_lead_rulings_v2.json, 16:36, written after RankingReviewer and after the v1 top pair was
  known): RR-01 applied literally (QG's all-UNKNOWN C1(b) = high; QG fails the L1 gate), RR-03 (abstract-only grain
  C6 capped at 2), RR-04 (Topstep R by size), RR-05 (Lucid fee unknown, u-rule). Reason: each is the literal reading
  of the frozen spec or of the lead's v1 clauses; DeltaReviewer confirms RR-01 is literal and notes that leaving
  partly evidenced ratings as rated is itself a choice. This changed the top pair from Topstep QG to Topstep QM.
- MathReviewer findings: all BLOCKING and SHOULD FIX applied as proposed; NOTEs only where factual with exact text.
  Reason: no basis to overrule a reviewer that re-derived each item.
- Usage-limit handling: the review prompt was amended to write R_math files early; fewer agents at once after the
  cuts; cut agents' complete files reused as they stand (Bulenox reader; MathReviewer G1, G4, G6) and EconCoder
  resumed. Reason: workflow agents cut by a limit lose unsaved work.
- B1/B2: PilotCoder's ambiguity 14 resolved by trade date (request end 2024-02-29T22:00:00Z, no record of trade date
  2024-03-01); its other 14 resolutions accepted. QM's FIFO matching confirmed by the lead from SpecReviewer's saved
  CME sheets (later re-confirmed by DeltaReviewer). Topstep's fee: the per-product 3.42 USD round trip is primary
  (RR-02); 3.70 USD per lot read as per side is reported as the conservative alternative.
- The spec was re-filled for QM after SpecReviewer had reviewed the QG version; QM's parameters were reviewed only by
  E.28b's DeltaReviewer.

Session 2 (E.28b):
- OC-B1: no Fable on the Pro plan; every remaining Fable review became DeltaReviewer-OpusXHigh in a fresh context
  (prompt E.28b). Reason: the prompt; cost: correlated errors with the Opus-written work are less likely to be caught.
- S1 done by one worker (PilotFixer-OpusXHigh) rather than the lead. Reason: test runs and edits across seven modules
  would have filled the lead's small Pro context.
- OC-B2 to OC-B6 (PilotFixer round 1 questions): --root left to the reviewer (it became RD-01 and was fixed); VPO also
  reported at the 0.296 fee (extra conservative output, headline unchanged); verify always run with
  --purchase-record (later made mandatory, RD-03); "fills within 60 s" includes the 50 ms cancel latency as the spec
  says (wording only); RS-13 implemented as a clip, not an assert (identical under the spec grid).
- RD-01 to RD-03 rulings: QM is the only root any pilot_pull mode accepts; one purchase on acct-3; the request end must
  equal 2024-02-29T22:00:00Z; verify.py refuses to run without the purchase record and checks every file's sha256.
  Reason: each closes a path to buying the wrong thing; none changes the frozen spec.
- OC-B7 to OC-B9 (round 2 questions): verify.py and measure.py not pinned to QM (they act on the bought file and its
  record); --quote allowed after a purchase (free; adds a ledger line); any committed acct-3 purchase blocks a second
  (acct-3 is pilot-only, V45). DeltaReviewer rated all three NOTE.
- The key was absent at the start. The lead finished S1 and S2 anyway so the code would be ready, sent the user one
  push notification, and polled for the key by name only (never the value) every 60 s until 20:25.
- reports/stage_e28_ranking.md built from the v2 table verbatim with a new front page (rank_front_v2.md); session 1's
  QG-era front is kept unchanged in work/lead/rank_front.md.
- Session cost from reports/stage_e26_briefs/cost.py (the rglob copy that counts workflow agents); the E.10 script
  misses them.
@@OC_TAIL@@
