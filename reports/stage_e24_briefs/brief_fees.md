# Brief: FeeReader-OpusMed (worker-medium, opus). Stage E.24 Part C, a narrow bounded lookup

Read-only, official pages only (Alpaca's own fee schedule, disclosures and support pages; sec.gov; finra.org; nyse.com).
Read each site's terms/robots before any automated fetch. Save each page raw under
reports/stage_e24_briefs/pages/fees/ with URL, UTC fetch time and sha256 in reports/stage_e24_briefs/facts/fees_log.md;
read by grep. Fetch order: WebFetch, then `scrapling extract get`, then `scrapling extract fetch`. Private scripts in
reports/stage_e24_briefs/scripts/fees/. Stop on any web-budget notice and log it. No account, no API, no key, no market
data (no prices, spreads or quotes of any security).

Questions (one numbered row each in reports/stage_e24_briefs/facts/fees_facts.md: answer, verbatim quote, URL, saved
file, UTC time; or [unverified]):
F1. Alpaca's regulatory fees passed to customers on stock/ETF sales: SEC Section 31 fee and FINRA Trading Activity Fee
    (rates, per-share or per-dollar, rounding, caps), and any commission (should be zero) — Alpaca's fee schedule page.
F2. The current SEC Section 31 fee rate (per million dollars of sales) and its effective date (sec.gov fee rate
    advisory), and the next scheduled change if published.
F3. The current FINRA TAF rate per share for covered equity sales and its per-trade maximum (finra.org), with the
    effective date and any published schedule of increases.
F4. Alpaca's margin interest rate (annual, on debit balances) and how it is charged (daily accrual, day count), and
    whether paper accounts simulate margin interest.
F5. Alpaca's stock borrow fees: easy-to-borrow vs hard-to-borrow, how the fee is computed and charged, and whether
    paper accounts simulate it.
F6. NYSE's published holiday and early-close calendar for 2026, 2027, 2028 and 2029 (nyse.com), quoted.
Return: the facts path, a summary of at most 150 words, anything unfinished.
