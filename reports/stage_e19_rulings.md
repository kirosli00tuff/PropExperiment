# Stage E.19 rulings (lead)

Lead rulings on the Fable review findings. RR-n: RulesReviewer-FableXHigh (reports/stage_e19_review_rules.md, rule
table and terms). ER-n: EconReviewer-FableXHigh (reports/stage_e19_review.md, simulator and recomputation). Times PDT.

## Rules review (RulesReviewer-FableXHigh, returned 18:00)

- RR-1 (BLOCKING, account stacking and "Excessive purchases of Trading Combines or Resets"): ACCEPTED. The funnel's
  buy-after-fail loop is the practice Topstep names once it is run aggressively or at a high rate. Fix (18:00):
  (a) churn metrics per configuration in the aggregator (Combine purchases and MLL breaches per 21 Combine-phase
  trading days, XFA breaches per 21 XFA days, campaign purchases per 21 elapsed days); (b) a churn label, lead rule
  L-19: "low" at <= 2.0 Combine purchases per 21 Combine-phase trading days per account, "medium" <= 4.0, "high"
  above; (c) a forfeiture column (cycle net if every payout were denied = minus the fees) for medium and high churn;
  (d) recommendations come only from low-churn configurations inside the policy band (f <= 0.25); f 0.35 / 0.50 are
  diagnostics and never recommended; (e) the recommended stop rule caps total purchases (section 7 of the return).
  Topstep publishes no threshold, so "low" is the lead's reading of "not excessive", stated as such.
- RR-2 (SHOULD FIX, full Maximum Position Size into scheduled news; the RTP "max position" trigger): ACCEPTED as a
  bot constraint; no rerun. The model cuts n to the tier cap only when f x D exceeds it (mainly ZN, a full-size-only
  path, on an XFA's first tier); the bot rule in the return: never hold the tier's full size through a scheduled
  release, keep at most the V23 item 11 release-window fraction of the tier open in [r - 5 min, r + 30 min).
- RR-3 (SHOULD FIX, cross-account hedging from independent slots): ACCEPTED; no rerun. The five-slot campaign's
  independence is read as five accounts trading five different products (one path each), never opposite positions
  in the same or a closely related product; the pooled draw's same-product overlaps are a modelling approximation
  of that, stated in the results. Bot rule: one product per account, or the same direction (copying) on all.
- RR-4 (SHOULD FIX, P35 misread): ACCEPTED and fixed by the lead at 18:01: P35's bot_implication in
  reports/stage_e19_rules.json and .md now reads it as a purchase-rate clause (Combines, Resets). Only that text
  field changed; the file was re-serialized (sha256 now ebc29f8b41edfdb0...), so the grid's settings fingerprint
  changed mid-run; GridCoder was told that jobs under the old fingerprint 1509fa8a6926cde9 stay valid.
- RR-5 (SHOULD FIX, copy-traded five accounts and the RTP trigger): ACCEPTED; the copy-traded figure carries the
  caveat that five copied accounts breach on the same day, which can place the trader in the Responsible Trading
  Program (forced DLL, Consistency path only), so it cannot be repeated freely.
- RR-6 to RR-19 (NOTEs): acknowledged. RR-10: the model runs the "no minimum payout balance" reading of R058 (no
  amount is published; the results say so). RR-11 (credits lost at a pass) and RR-14 (payout one day later than the
  fastest legal cycle) are conservative and small. RR-8: Wise is $0 on Topstep's side for Canada, with Wise's own
  conversion fee. RR-19: the API fee is $14.50 with the "topstep" code ($29 list); the results give the arithmetic
  for the list price.

## Model review (EconReviewer-FableXHigh: Phase A blind 17:43-17:59, Phase B 19:27-19:46)

The headline reproduces: an independent simulator agrees with prop_econ per path to 1e-11 on identical shocks, and
all 60 independently recomputed configurations (each size and path, zero edge and net Sharpe 0.5, every band f) agree
with the grid in sign, best band f and within 2.6 total Monte Carlo SD; 11/11 hand paths to the cent; the returns
table rebuilt from the stores matches to 1e-9 with a demeaned mean of 0.

- ER-1 (SHOULD FIX, SEs omit the pools' sampling error): ACCEPTED; text fix, no rerun. The results state that SEs are
  conditional on the 20,000-path pools and that the total SE is about 1.3x (50K) to 2.5x (150K) at zero edge; the
  reviewer found no sign, ranking or break-even change from it.
- ER-2 (SHOULD FIX, the churn metric's floor and credit-paid resets): ACCEPTED; text fix. The label stays (a
  reset-inclusive per-account rate is still <= 2.0 in the band; five accounts make about 4-5 purchases or resets per
  21 trading days); the results say the label is partly definitional, and the recommendations rest on a fixed fee
  budget and the qualitative terms, not on the label.
- ER-4 (NOTE): ACCEPTED as a correction to the lead's draft, which had said f 0.50 stays negative at zero edge: the
  zero-edge mean is positive only at f 0.50 with the DLL (+27 at 50K Standard) and, without the API fee, for integer
  MNQ on 50K Consistency. The verdict now says so.
- ER-5 (NOTE): adopted in the text (Standard path rises past the band; Consistency path interior at S >= 0.5).
- ER-3, ER-6 to ER-12 (NOTEs): acknowledged; ER-11 (quote the effective Sharpe next to "zero edge") and ER-12 (integer
  NQ / ZN do not depend on f) are in the results text; ER-8 is defensive only (no result change); ER-9: "days to
  first payout" are traded days before the first request.
- ER-13 (NOTE, coverage): the lead asked for Phase C (19:46), an independent cross-check of the verdict cells not yet
  recomputed: the 5-slot campaign quantiles, the DLL-on and Back2Funded-on 50K Consistency cells, keep-D, and the f
  0.50 DLL-on zero-edge cell.

## Phase C (EconReviewer-FableXHigh, 19:46-19:56): the verdict cells

All cited cells recomputed with the reviewer's own extended simulator on the grid's shocks and on independent shocks:
the 48 five-slot campaign P50 / P80 purchase and fee quantities agree within one purchase or 1.3%; the DLL-on,
Back2Funded-on and keep-D cycle cells agree within |z| <= 1.1.
- ER-14 (SHOULD FIX, the positive zero-edge cell outside the band): ACCEPTED; text fix. 50K Standard, DLL on, f 0.50,
  zero edge reads +27 (+34 with Back2Funded) in the grid but +2.5 (SE 10) / -16 (SE 15) on independent shocks; the
  results now say its sign is not established and that aggressive sizing lifts zero edge to about break-even at best.
  Nothing inside the policy band changes.
- Final counts: BLOCKING 0, SHOULD FIX 3 (ER-1, ER-2, ER-14; all text fixes, applied), NOTE 11.
