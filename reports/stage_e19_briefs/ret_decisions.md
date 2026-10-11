## 7. Decisions for the user (each with a recommendation)

1. **Buy a Combine at all?** Recommendation: **not yet.** With no validated edge (N = 480, nothing has passed), the
   funnel loses money in expectation at every size, path, pricing and sizing: the best case is -$250 per 50K cycle
   (-$94 without the API fee), and half of all cycles lose every fee paid. Buy only when a strategy has passed a
   registered test with a net Sharpe of about 0.5 or more after costs (a gross Sharpe near 1.0 at one round trip a
   day). Even then the gain is modest: +$278 to +$906 per 50K cycle. Payout luck is weak evidence of edge: at zero
   edge a cycle pays something 52% of the time on the Standard path, at a net Sharpe of 0.5 64% of the time. So no
   number of Combines bought will tell an edge from luck in a useful time.
2. **Which size?** Recommendation: **50K.** It has the lowest break-even (net Sharpe about 0), the smallest zero-edge
   loss and the cheapest failures. 100K is positive at a net Sharpe of 0.5 only on the Consistency path (or with
   Back2Funded). 150K needs a net Sharpe of 0.5 to 0.9 to break even, because its Combine is slow and billed at
   $199 a month.
3. **Which payout path and options?** Recommendation, for a bot with a validated edge: **Consistency path, DLL added
   at purchase, Standard pricing ($49/month + $149 activation), Back2Funded used when an XFA is lost before its first
   payout, and a keep-D payout policy** (leave half the MLL in the account after each payout). At a net Sharpe of 0.5
   on 50K the best tested combination is +$477 per cycle with the DLL and +$906 with Back2Funded as well (payout
   policy max). Keep-D was tested separately, with the DLL and Back2Funded off. Keep-D
   adds $42 (Consistency) to $209 (Standard) on 50K at a net Sharpe of 0.5, and more on the larger sizes. Choose the Standard path instead if fewer empty
   cycles matter more than the mean: 36% of cycles pay nothing, against 54% on the Consistency path. The No Activation
   Fee pricing path is worse, except at 150K with the DLL.
4. **How many attempts to budget?** With five accounts and a net Sharpe of 0.5 on 50K, withdrawing $5,000 takes about
   51 Combine purchases and $4,100 of fees with 50% probability, or 76 purchases and $5,900 with 80%. That is 255 to
   383 trading days. $10,000 takes 86 / 121 purchases and $6,900 / $9,500. At zero edge, $5,000 takes $7,900 / $11,500
   of fees. Recommendation: **no Combine budget at zero edge.** With a validated edge, see the fee table in section 3
   (T4), and note that $4,000 to $6,000 of fees is about what a small personal micro-futures account needs, which is
   the user's real goal (V32).
5. **Stop rule.** Recommendation: **a hard fee budget fixed before the first purchase, and never raised after
   losses.** Suggested: at most $1,000 on 50K, about two cycles. Stop at once when the budget is spent, when the bot's
   own tracked net Sharpe over 60 or more trading days falls below 0, or at a Live Funded call-up (the LFA bans the
   API). Never buy faster after losses: that is the account-stacking pattern.
6. **What a bot must and must not do under Topstep's terms.**
   - **Must:** run on the user's own machine (no VPS, VPN or remote server); use the TopstepX / ProjectX API only on
     Combines and XFAs; be flat by 15:10 CT, with no new positions after 15:08 CT; keep the position below the
     tier's full size through scheduled releases (the V23 item 11 release-window fraction).
   - **Must:** trade one product per account, or the same direction on every copied account; size at or below
     f = 0.25 of the drawdown distance; keep Combine and Reset purchases modest (L-19: about two per account per
     month at most); stop all automation at a call-up.
   - **Must not:** hedge across accounts, even briefly; trade full size into news; scalp SIM fills or make hundreds of
     rapid trades; trade outside the best bid or offer; use the diagnostic sizes (0.35, 0.50), which raise expected
     cash only by breaching faster; or rotate through accounts after MLL hits (account stacking).
   - **Note:** several accounts hitting the MLL on the same day can put the trader in the Responsible Trading
     Program. That makes copy-trading five accounts riskier than its arithmetic.
