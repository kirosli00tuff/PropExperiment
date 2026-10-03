# Stage E.12 Task 2b: Topstep 150K figures (public help pages)

Worker: TopstepFacts-OpusMedium. Fetched 2026-10-03, 08:27 to 08:28 PDT, by curl (all 200, no
fallback needed). Full fetch log with UTC times and hashes: reports/stage_e12_briefs/topstepfacts_log.md.
Raw pages: reports/stage_e12_briefs/topstep_pages/. "Last updated" is the page's displayed date
text plus its JSON-LD dateModified (UTC). Quotes are verbatim from the saved HTML (tags stripped;
line breaks from table cells shown as " | ").

## 1. Figures

| # | Figure | Value | URL | Fetched (PDT) | Page last updated | Quote or image transcription | Page file, sha256 |
|---|---|---|---|---|---|---|---|
| 1 | 150K XFA Maximum Loss Limit | $4,500 (trailing; XFA starts at -$4,500, locks at $0) | https://help.topstep.com/en/articles/8284204-what-is-the-maximum-loss-limit | 2026-10-03 08:27:56 | "Updated over 2 weeks ago"; dateModified 2026-09-18T18:51:37Z | "Account Size \| Maximum Loss Limit \| $50K \| $2,000 \| $100K \| $3,000 \| $150K \| $4,500" ... "The MLL is a trailing limit. It rises as your end-of-day balance grows, but never moves down. Once it reaches your starting balance, it locks permanently." ... (Back2Funded FAQ) "Account Size \| Starting MLL \| $50K XFA \| -$2,000 \| $100K XFA \| -$3,000 \| $150K XFA \| -$4,500" "The MLL trails upward as your balance grows and locks at $0 once reached, same as a brand new XFA." | art_8284204.html, e42229a995b804d5b2f27239bb11a33978d64a31d7e5fd8ea886391ae8016f84 |
| 1a | MLL after first payout | set to $0 | same as row 1 | same | same | "After your first Payout: Your MLL is set to $0 regardless of where it was before. The remaining balance becomes your effective loss floor." | same |
| 1b | MLL monitoring | real time, realized + unrealized; updates end of day | same as row 1 | same | same | "The MLL updates at the end of each trading day but is monitored in real time throughout the session. Both realized and unrealized P&L count toward it." | same |
| 2 | 150K XFA Scaling Plan | 3 / 4 / 5 / 10 / 15 lots (table in section 2) | https://help.topstep.com/en/articles/8284223-what-is-the-scaling-plan (image "XFA charts - hc.png" embedded in it) | page 08:27:06, image 08:27:11 | "July 16, 2026"; dateModified 2026-07-16T14:03:03Z | Transcribed FROM AN IMAGE (see section 2). Page text: "The Scaling Plan is an Express Funded Account® (XFA) objective. It sets your Maximum Position Size — the max contracts you can hold at one time — based on your current account balance." "Your XFA starts at a $0 balance" "Your max contracts do not increase mid-session. Hit the threshold to release more buying power? Wait for the next session." "1 Mini = 10 Micro contracts" "Limits are based on mini-contract equivalents" | art_8284223.html, ba3cd3b0abdc413af3c3aafad38392a4a09b1bca42ac8f2a4109a5dd408e21b2; scaling_xfa_charts.png, 55ec76b4b293822849c9bf8a8ac2de362fa895010d39ce9c0d00f4ed275e6cbd |
| 3 | 150K Trading Combine monthly price | Standard Path $199/month; No Activation Fee Path $229/month | https://help.topstep.com/en/articles/14289835-topstep-pricing-and-payment-questions | 2026-10-03 08:27:42 | "Updated over a week ago"; dateModified 2026-09-25T22:00:42Z | "Trading Combine \| Account Size \| Standard Path \| No Activation Fee Path \| 50K \| $49/month \| $95/month \| 100K \| $99/month \| $149/month \| 150K \| $199/month \| $229/month" "⚠️ Important: Paths cannot be changed after purchase." | art_14289835.html, 36eb6af9d8d426c8adaa5db68079ae6341e98c1865a43d03b6fae7628824bec4 |
| 4 | 150K Trading Combine Reset price | Standard $199; No Activation Fee Path $229 | same as row 3 | same | same | "Reset Pricing \| Account Size \| Standard Path \| No Activation Fee Path \| 50K \| $49 \| $95 \| 100K \| $99 \| $149 \| 150K \| $199 \| $229" | same |
| 4a | Reset mechanics | 2 Resets per account per day; Reset pushes rebill 30 days; each monthly rebill adds 1 Reset Credit | https://help.topstep.com/en/articles/8284128-what-is-a-reset | 08:27:41 | "Updated over a week ago"; dateModified 2026-09-25T22:00:43Z | "A Reset returns your Trading Combine® to its original starting balance — Account Balance, Maximum Loss Limit (MLL), Consistency Target, and trading days all go back to day one." "Limit: 2 Resets per account each day." "Resetting your account pushes your Rebill date out 30 days from the date of purchase." "Every monthly Rebill adds 1 Reset Credit to your Reset Bank." | art_8284128.html, 31d80d9f91219bb6231aaa0808f12459d3065b558ebcb7085cd802b8799b1e18 |
| 4b | Combine subscription on MLL breach | keeps rebilling; no time limit to pass | https://help.topstep.com/en/articles/8284121-trading-combine-subscriptions | 08:27:42 | "Updated over a month ago"; dateModified 2026-09-04T12:58:40Z | "It Rebills every 30 days from your original sign-up date. Active until you pass and earn an Express Funded Account® (XFA) — or until you cancel. No time limit for passing." "Your account becomes ineligible for funding until it's reset. The subscription does not cancel — it keeps rebilling, and you can still trade for practice. You'll get a Reset Credit when your Rebill processes." | art_8284121.html, 0cd197bae16607a621f60b7ee19b771788bdbd8ab257ffa47ff79ed890b695d3 |
| 5 | XFA activation fee | $149 once per XFA on Standard Path; $0 on No Activation Fee Path | same as row 3 (also confirmed on activation article) | 08:27:42 (activation article 08:27:57) | as row 3; activation article dateModified 2026-09-24T20:17:59Z | Pricing page: "Standard Path: Lower monthly cost. $149 Activation Fee charged once per Express Funded Account (XFA) earned." "Depends on your path: Standard Path — $149, charged once per XFA earned. No Activation Fee Path — $0." Activation article (https://help.topstep.com/en/articles/8284217-express-funded-account-activation): "Standard Path \| $149 one-time activation fee per XFA \| No Activation Fee Path \| No activation fee" | art_14289835.html (above); art_8284217.html, fd429c1a3c7203fbbbceb74790f0a7c2d62319299a83ef2f75d4fe35509018ba |
| 6 | Back2Funded (XFA reactivation) price, 150K | $829 per reactivation ($50 off with a DLL at checkout) | https://help.topstep.com/en/articles/12060405-back2funded-rules-guidelines-and-how-it-works | 08:27:43 | "Updated this week"; dateModified 2026-09-29T20:43:51Z | "Account Size \| Reactivation Fee \| $50K XFA \| $599 \| $100K XFA \| $699 \| $150K XFA \| $829" "Prices exclude sales tax. Each purchase is separate, final, and non-refundable." "✅ $50 off → 150K (DLL: $3,000)". Pricing page agrees: "Reactivation fees: $50K XFA — $599 $100K XFA — $699 $150K XFA — $829" | art_12060405.html, a3e4d0af73cceb87d9ee22448e78c5ebec9adefc6cd2de1cc80fb313589931ea |
| 6a | Back2Funded conditions | before first payout only; up to 2 per XFA; 30-day window; same size and payout rules; full restart; tradable next session | same as row 6 | same | same | "Back2Funded gives you up to 2 Reactivations per account if you lose your Express Funded Account® (XFA) before your first Payout. Keep the same account size and Payout rules — no Trading Combine® required." "The XFA was closed due to a rule violation before taking a Payout" "⚠️ Once a Payout is taken from an XFA, it is no longer eligible for Back2Funded. Traders on the Focused Trader Plan (FTP) cannot use Back2Funded." "You have 30 calendar days from account closure to decide" "If you take no action within 30 days — the offer expires and is automatically declined" "After expiration, you must return to the Trading Combine® to earn a new XFA" "Your account is ready to trade at the start of the next trading session" "Everything resets to zero: balance, P&L, trade history, and winning days." "Back2Funded-eligible XFAs do not count toward your 5-account limit until the Reactivation fee is paid" | same |
| 6b | Responsible Trading discount, 150K | $30 off No-Activation-Fee Combine (monthly) with DLL; $50 off Back2Funded with DLL | same as row 3 | same | same | "There's now a Responsible Trading Discount when you add a DLL at purchase for No Activation Fee Trading Combines, Express Funded Account Activations, and Back2Funded Reactivations." Table: "No Activation Fee Trading Combine \| Back2Funded Reactivation" / "$10 off → 50K $20 off → 100K $30 off → 150K \| $50 off Reactivation Fees" "Discount recurs monthly." | art_14289835.html |
| 7 | Minimum trading days to pass the Trading Combine | 2 ("as few as two days") | https://help.topstep.com/en/articles/8284197-trading-combine-parameters | 08:27:41 | "Updated over a week ago"; dateModified 2026-09-24T20:21:06Z | "Can I pass the Trading Combine in one day? No. Big spike days don't build funded traders, consistency does. You can pass in as few as two days, but keep your best day below 55% of your Profit Target." | art_8284197.html, 9181f4511ab87625ba32245c8a8f4d20b5c277e17d2ea9bab25c06767fec46a0 |
| 7a | Pass-to-XFA timing | status update up to 30 min; Friday pass tradable Sunday 5 PM CT | same as row 7 | same | same | "The status update can take up to 30 minutes." "Passed on a Friday? You can pay the Activation Fee immediately, but your XFA won't be available to trade until markets reopen at 5 PM CT Sunday." "Profits don't transfer." | same |
| 7b | 150K Combine max position (context) | 15 contracts / 150 micros | same as row 7 | same | same | "Account Size \| Max Contracts \| Max Micros \| $50K \| 5 \| 50 \| $100K \| 10 \| 100 \| $150K \| 15 \| 150" | same |
| 8 | XFA count limit and breach outcome (context) | up to 5 active XFAs; breach closes the XFA | https://help.topstep.com/en/articles/8284215-express-funded-account-parameters | 08:27:40 | "August 5, 2026"; dateModified 2026-08-05T19:49:02Z | "You can hold up to 5 active XFAs at a time." "What happens if I breach the Maximum Loss Limit? Your account is liquidated and closed at the end of the day. Back2Funded lets you reactivate up to 2 times at the same size and Payout policy." "No monthly subscription fee after passing. A one-time Activation Fee applies per XFA (Unless you chose the No Activation Fee Trading Combine)." | art_8284215.html, 16af87ffa2bc5fecee76410a63867a7ec52d95d2102012a2cba1d67f9ca769b5 |

## 2. 150K XFA Scaling Plan (transcribed from an image)

Source: image "XFA charts - hc.png" (alt text) embedded in
https://help.topstep.com/en/articles/8284223-what-is-the-scaling-plan, saved as
topstep_pages/scaling_xfa_charts.png (5515x2474 px, sha256 55ec76b4...6cbd). The tiers below are
transcribed by reading the image; they are not page text. Balance is the XFA account balance,
which starts at $0. "Lots" are mini-contract equivalents (1 mini = 10 micros, per the page text).

Image, "$150K ACCOUNT", "Account Balance":

| Image label (verbatim) | Max lots (minis) | MES equivalent (10:1, per page text) |
|---|---|---|
| Below $1,500 | 3 Lots | 30 |
| $1,500 - $2,000 | 4 Lots | 40 |
| $2,000 - $3,000 | 5 Lots | 50 |
| $3,000 - $4,500 | 10 Lots | 100 |
| Above $4,500 | 15 Lots | 150 |

Inclusive or not: NOT stated. The image's ranges share endpoints ("$1,500 - $2,000" and
"$2,000 - $3,000"; "$3,000 - $4,500" and "Above $4,500"), and neither the image nor the page text
says which tier a balance exactly at $1,500, $2,000, $3,000 or $4,500 falls in. Only "Below
$1,500" makes $1,500 itself not part of the first tier. Timing rule from page text: limits change
only at the next session ("Your max contracts do not increase mid-session.").

For comparison, the same image's other panels (transcribed): $50K: Below $1,500 2 Lots; $1,500 -
$2,000 3 Lots; Above $2,000 5 Lots. $100K: Below $1,500 3 Lots; $1,500 - $2,000 4 Lots; $2,000 -
$3,000 5 Lots; Above $3,000 10 Lots.

## 3. Differences from V22 / the design draft / the facts file

- MLL: $4,500 confirmed for the 150K XFA. No difference from V22.
- Scaling: the design draft (docs/STAGE_E_ML_V2_DESIGN.md line ~53) uses the 50K tiers for 150K
  until read. The published 150K schedule is larger at every balance (3 vs 2 lots below $1,500;
  4 vs 3 at $1,500-$2,000; 5 from $2,000; 10 from $3,000; 15 above $4,500). The 50K panel matches
  the design's 50K tiers (2 / 3 at $1,500 / 5 above $2,000).
- DLL $3,000 for 150K (facts F12.2c, F9.4): reconfirmed on the Back2Funded page ("150K (DLL:
  $3,000)"). No difference.
- Responsible Trading discount 150K $30 / Back2Funded $50 (facts F9.4, F12.2c): unchanged.
- The facts file held no MLL, Combine price, Reset price, activation fee or Back2Funded price, so
  there is nothing to differ from for those.
- Wording difference between Topstep pages (not a number): the XFA parameters page says on an MLL
  breach the account "is liquidated and closed at the end of the day", while the MLL page says the
  XFA "is liquidated immediately" on a touch and "permanently closed". Both say the XFA closes.
- Back2Funded window was 7 days before 2026-05-29 and is 30 days now (page: "On May 29th, 2026,
  the Reactivation window increased from 7 days to 30 days!").

## 4. Not found / open

- Tier boundary inclusivity for the 150K (and 50K/100K) scaling plan: not published (see section 2).
- Whether the Responsible Trading discount applies to the $149 XFA Activation Fee: the pricing
  page's sentence names "Express Funded Account Activations", but its discount table has only the
  No Activation Fee Trading Combine and Back2Funded columns; no activation-fee discount amount is
  published. Open, not resolved here.
- A minimum count of trading days in the XFA before a breach-free restart: not applicable; the only
  published minimum found is the Combine's "as few as two days". Back2Funded restores trading at
  the next session; the Combine route needs a Reset or new Combine plus at least 2 trading days
  plus activation (Friday passes wait until Sunday 5 PM CT).
- Profit Target for the 150K Combine: not fetched (outside the brief).
- www.topstep.com has no static pricing page (/pricing returned 404; the sitemap lists none; the
  static homepage has no 150K price text). All prices come from the help-center pricing article.
- Sales tax is excluded from all prices ("Prices exclude sales tax" on the Back2Funded page;
  "Sales tax may be added at checkout where applicable" on the pricing page).
