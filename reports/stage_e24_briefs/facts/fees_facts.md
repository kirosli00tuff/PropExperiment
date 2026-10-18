# E.24 Part C fee facts (FeeReader-OpusMed)

Written 2026-10-18 01:45 PDT. Fetch records, terms review and sha256 values are in facts/fees_log.md.
Saved files are under reports/stage_e24_briefs/pages/fees/. Quotes come from the derived .txt or .md
copies and are copied verbatim, including the source's own typos. Line numbers refer to those copies.
No market data was fetched.

## F1. Alpaca regulatory fees on stock/ETF sales, and commissions
- Answer: SEC transaction fee $0.0000206 times trade value, on sells only (equal to $20.60 per
  $1M). FINRA TAF $0 per share on sells only, as printed in Alpaca's schedule. CAT fee $0.000003 per
  executed equivalent share on buys and sells. Fees are computed on the exact quantity, aggregated
  per fee type per account per day, and each daily total is rounded up to the nearest $0.01. No cap
  is stated in Alpaca's schedule. Commissions are $0 for standard equities. Exceptions: index
  options, the Elite Smart Router, and order flow judged non-retail. Schedule "Revised on October
  12, 2026".
- Quotes (alpaca_BrokFeeSched.pdf.txt):
  - l.113-117: "SEC Transaction Fee / $0.0000206 * Trade Value / When sells only / FINRA Trading Activity Fees (TAF) / $0 per share / When sells only"
  - l.120: "FINRA Consolidated Audit Trail Fee (CAT)              $0.000003 per executed equivalent share"
  - l.34-36: "Alpaca Securities does not charge commissions, except as described below. Commissions apply to index options trades, use of the Elite Smart Router under the Alpaca Elite offering, and order flow determined to be non-retail in nature."
  - l.188-191: "Fees are calculated on the exact executed quantity, including fractional shares, with no rounding of share quantity. Each fee type is aggregated separately at the daily, per-account level. After aggregation, each fee total is rounded up to the nearest cent ($0.01)."
  - l.275: "Revised on October 12, 2026"
  - docs_regulatory-fees.md (updatedAt 2025-10-03): "| Trading Activity Fee (TAF) | Sells only | FINRA |" and "We round up total fees based on the currency’s precision to the nearest decimal place."
- Note for the lead: Alpaca prints TAF as "$0 per share", while FINRA's current rule text (F3) gives
  $0.000166 per share. I have not resolved this discrepancy, and I have not interpreted it.
- URLs: https://files.alpaca.markets/disclosures/library/BrokFeeSched.pdf (alpaca_BrokFeeSched.pdf,
  2026-10-18T08:41:36Z); https://docs.alpaca.markets/docs/regulatory-fees.md (docs_regulatory-fees.md,
  08:41:39Z).

## F2. SEC Section 31 fee rate
- Answer: $20.60 per million dollars for covered sales on charge dates on or after April 4, 2026.
  The rate was $0.00 per million through April 3, 2026. It stays in effect until 60 days after the
  FY2027 appropriation is enacted. The advisories listing shows no FY2027 Section 31 advisory yet
  (the newest Section 31 item is the FY2026 one, dated Feb. 27, 2026), so no next change date is
  published.
- Quotes (sec_fee_advisory_2026-2.html.txt, l.136-138):
  - "Feb. 27, 2026 — The Securities and Exchange Commission today announced that starting on April 4, 2026, the fee rates applicable to most securities transactions will be set at $20.60 per million dollars."
  - "Consequently, each SRO will continue to pay the Commission a rate of $0.00 per million for covered sales occurring on charge dates through April 3, 2026, and a rate of $20.60 per million for covered sales occurring on charge dates on or after April 4, 2026."
  - "This fee rate will remain in effect until 60 calendar days after legislation is enacted that sets the amount of the Commission’s fiscal year 2027 appropriation."
  - Listing (sec_fee_rate_advisories.html.txt l.138-140): "Section 6(b) Filing Fee Rate Advisory for Fiscal Year 2027 - Aug. 21, 2026" / "Section 31 Transaction Fee Rate Advisory for Fiscal Year 2026 - Feb. 27, 2026"
- URLs: https://www.sec.gov/rules-regulations/fee-rate-advisories/2026-2 (sec_fee_advisory_2026-2.html,
  08:42:23Z); https://www.sec.gov/rules-regulations/fee-rate-advisories (sec_fee_rate_advisories.html,
  08:42:06Z).

## F3. FINRA TAF on covered equity sales
- Answer (version in force now): $0.000166 per share, maximum $8.30 per trade. No fee is charged if
  the execution price is below $0.000166. The page's version selector marks "Oct 01, 2026 - Dec 31,
  2026" as selected. The amendment history under the text ends at "SR-FINRA-2020-032 eff. Jan. 1,
  2024". The page also lists future versions (Jan 01 2027 - Dec 31 2028, 2029, 2030, 2031 onwards),
  so a schedule of changes exists. Those versions' rates are [unverified]: they were not fetched,
  because FINRA's terms bar scraping tools (see fees_log.md).
- Quotes (finra_schedA_sec1.html.txt):
  - l.212: "* Trading Activity Fee rates are as follows: Each member shall pay to FINRA: (1) $0.000166 per share for each sale of a covered equity security, with a maximum charge of $8.30 per trade; ... In addition, if the execution price for a covered security is less than the Trading Activity Fee rate ($0.000166 for covered equity securities, ...) on a per share, per contract, or round turn transaction basis then no fee will be assessed."
  - l.213: "Amended by SR-FINRA-2020-032 eff. Jan. 1, 2024."
  - raw HTML version selector: `<option value="2009881">Jan 01, 2027 - Dec 31, 2028</option><option value="2009541" selected>Oct 01, 2026 - Dec 31, 2026</option>`
- URL: https://www.finra.org/rules-guidance/rulebooks/corporate-organization/section-1-member-regulatory-fees
  (finra_schedA_sec1.html, 08:42:36Z). finra_taf.html (08:42:40Z) points to Schedule A and gives no
  rate. Caveat: this page was fetched before the FINRA terms had been read. The lead decides
  whether it may be cited.

## F4. Alpaca margin interest
- Answer: 6.50% a year by default and 5.00% for Elite users. It is charged on the end-of-day
  settlement-date debit balance, divided by 360, accrues daily, and posts monthly. A Friday debit
  is charged for 3 days. Whether paper accounts simulate margin interest is [unverified]: the paper
  trading page lists "Margin Trading" as supported in paper and does not mention interest.
- Quotes:
  - alpaca_BrokFeeSched.pdf.txt l.23-27: "Default Margin Lending Interest Rate                                6.50%*" / "Alpaca Elite 100k Margin Lending Interest Rate                      5.00%*" / "*Charged on the daily balance at an annualized prevailing interest rate, which may change from time to time."
  - docs_margin-and-short-selling.md l.35-36 (updatedAt 2026-09-17): "`daily\_margin\_interest\_charge = (settlement\_date\_debit\_balance \* rate[non-elite: 0.0650 | elite: 0.0500])) / 360`" / "Interest will accrue daily and post to your account at the end of each month. Note that if you have a settlement date debit balance as of the end of day Friday, you will incur interest charges for 3 days (Fri, Sat, Sun)."
  - docs_paper-trading.md l.30: "| Margin Trading | ✅ | ✅ |" (paper | live). The page does not mention interest (grep "interest" found nothing).
- URLs: BrokFeeSched.pdf (as F1); https://docs.alpaca.markets/docs/margin-and-short-selling.md
  (08:41:37Z); https://docs.alpaca.markets/docs/paper-trading.md (08:41:38Z).

## F5. Alpaca stock borrow fees
- Answer: ETB names have no locate fee and no borrow fee. HTB names pay a one-time, non-refundable
  per-share locate fee quoted through the Locates API, plus a daily borrow fee. The daily fee uses
  the end-of-day short quantity rounded up to 100 shares, a collateral value of the prior close
  times 102% rounded up to the next dollar, and the annual rate on a 360-day year. It accrues every
  calendar day and posts by the next business day. Paper accounts do not simulate borrow fees.
- Quotes:
  - alpaca_BrokFeeSched.pdf.txt l.231-233: "Free (no locate or stock borrow fees on / Easy-to-Borrow Securities / Easy-to-Borrow securities)"
  - l.260-266: "A separate daily stock borrow fee applies to open HTB short positions. Borrow fees vary by security and change daily based on market conditions. Daily fees are based on your end-of-day short quantity (rounded up to the nearest 100-share lot), a per-share collateral value from the prior trading day's closing price (adjusted by 102% and rounded up to the nearest dollar), and the applicable annual borrow rate on a 360-day year. Fees accrue for each calendar day you keep the position open, including weekends and market holidays. They are calculated after the market close and typically post to your account by the following business day."
  - l.256-257 (footnote 1): "The locate fee is charged one-time when the locate is accepted, is non-refundable regardless of whether a short sale is executed, and cannot be reused if the short position is closed."
  - docs_margin-and-short-selling.md l.51: "\* \*\*Fees:\*\* $0 locate and borrow fees on all ETB shares for Trading API users."; l.62: "`Daily HTB stock borrow fee = Σ((each stock’s HTB short $ market value \_ that stock’s HTB rate) / 360)`"
  - docs_paper-trading.md l.33: "| Borrow Fees | ⛔️ (Coming Soon!) | ✅ |"; l.14-21: "paper trading does not account for: ... \* Regulatory fees \* Dividends"
- URLs: as F1 and F4.

## F6. NYSE holiday and early-close calendar, 2026-2029
- [unverified]. Not fetched. The ICE Terms of Use, which cover www.nyse.com, prohibit robots and
  automated tools (quoted in fees_log.md). Getting this needs a manual browser visit or the lead's
  decision.

## Row count
6 questions. Answered with quotes: F1, F2, F4 (except the paper-interest part), F5. Partly
answered: F3 (current rate only; future versions [unverified]; terms caveat). Unverified: F6.
