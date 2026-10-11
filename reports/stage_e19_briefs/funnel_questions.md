# Stage E.19 Task 2: open modelling questions (FunnelCoder-OpusXHigh, 2026-10-10)

Questions on sim_spec.md sections 2 to 5 that the spec leaves open. Each one is implemented the way the
spec's wording favours and marked `QUESTION` in the code. The lead decides; changing a reading is a
local edit at the place named.

## A. Daily step and phases (prop_econ/funnel.py, mirrored in prop_econ/vec.py)

1. **k at a Sharpe edge.** Section 2.4 names k (round trips a day) only for the zero edge. At a Sharpe
   edge k cancels from the close (net = n x sigma x (z + S/sqrt 252)) but stays in Worst (- n x k x rt).
   Implemented as `Policy.k`, default 1, applied in both modes. Which k should the Sharpe grid use?
2. **Scaling tier after a morning payout.** "Read from the balance at the prior session's close" is
   implemented literally: a payout at the start of day d does not lower day d's tier. The alternative
   is the post-payout balance. The FINAL file's added field `global.scaling_updates_next_session_only:
   true` fits the literal reading.
3. **DLL tie (numerical).** After one DLL stop from the trailing peak, D_open = MLL - DLL. That equals
   the DLL whenever MLL = 2 x DLL (50K: 2000 / 1000), so "DLL < D_open" meets exact ties, and float noise
   (1000.0000000000001) decided them. In one case that left an account at D = 0. Ties within 1e-6 USD
   now read as DLL >= D_open, so the MLL governs, as in exact arithmetic (`DLL_TIE_USD`). Please confirm
   that the MLL, not the DLL, governs at D_open = DLL.
4. **Combine DLL.** Per the lead's note of 17:30: when the DLL is chosen, the Combine uses
   `combine.dll_option_usd` (an added field). `combine.dll_usd` is a mandatory Combine DLL. If both
   were ever set, the smaller applies. No file has both. If `dll_chosen` is set and the size has no
   `dll_option_usd`, the code raises.
5. **D_open <= 0 after a payout.** This is possible only if frac_of_balance = 1 with keep-D 0, or if
   mll_after_first_payout_usd exceeds the post-payout balance. The spec says D_open > 0 while alive and
   gives no rule for it, so both simulators raise `FunnelError`. Neither the FINAL nor the provisional
   values can reach it.
6. **Consistency path and `net_positive_since_last`.** The consistency path requires window net > 0
   whatever that flag says, per spec section 4. The flag is read only on the standard path. On the
   standard path before the first payout, the test is B > 0 (literal; equal to window net > 0 since
   start_balance = 0).
7. **End-day convention.** All counts are elapsed trading days. A call-up or payout limit right after a
   payout at the start of day d ends the XFA at elapsed d, with no trading that day. If the call-up and
   payout_count_limit fire together, the reason is recorded as call-up.
8. **Rule values that raise `UnsupportedRule`** (the spec does not model them): mll_trail "intraday";
   callup type "payout_total_usd"; combine_time_limit_days not null. Call-up "discretionary" runs like
   "none" (lead, 17:30). after_n_payouts runs through
   `apply_readings(..., allow_unlisted=True)`, because the FINAL file lists `global.callup.n` with the
   single reading [null] and `callup.type` with ["discretionary"]. Overrides outside the readings are
   recorded in `RuleBook.unlisted`.

## B. Fees, cycles, campaigns (prop_econ/assemble.py)

9. **Rebill and reset on the same day.** The rebill is processed first, and its credit then pays the
   reset. The alternative is reset first, then the rebill. With P = R and reset_pushes_rebill the two
   cost the same; they differ when the DLL discount lowers P only, or when the reset does not push the
   rebill.
10. **DLL discount on the reset price.** The schema has `dll_discount_monthly_usd` only, so the discount
    lowers P and not R.
11. **Timing.** The XFA starts, and the activation fee is paid, the trading day after the pass. A
    Back2Funded XFA starts, and its fee is paid, the day after the breach. Back2Funded follows the
    file's `before_first_payout_only` field: true in both files, which matches the spec text.
    `window_calendar_days`, `resets_per_day` and `xfa_inactivity_close_days` cannot bind for a bot that
    trades every day and reactivates at once, so they are ignored.
12. **Payout record overflow (spec: padded to 64).** In a worst-case timing run where no XFA
    breached, the standard path paid 106 times and the consistency path 189 times in 756 days (one
    payout per 3 traded days plus the excluded request day). High-edge configurations will overflow 64.
    Totals stay exact (`total_gross`, `n_payouts`). For campaign timing, the unrecorded remainder is
    credited at the XFA's end, which is late and therefore conservative, and is counted in
    `overflow_xfas`. Suggest running with `Policy(max_payouts=192)` (about 46 MB for 20,000 XFAs).
13. **Campaign purchase cap of 400.** A replication counts as "reached" only if no more than 400
    Combine purchases have been made by the time the target is reached. Purchases and fees on the same
    day as the target payout count. XFAs still live after the 401st purchase do not add cash.
14. **Added FINAL fields the simulator does not use**: payout fees (`global.payout_fee_usd`: ACH and
    wire $30, Wise $0), `xfa_min_payout_balance_after_first_required` (CONFLICT), the call-up LFA terms,
    `reset_credit_expiry_days`, `rtp_*`. Their effect is not modelled. The lead decides whether any of
    them enters the model.
