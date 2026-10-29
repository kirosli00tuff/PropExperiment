import json
def r(v, reason, unk=False): return {"value": v, "unknown": unk, "reason": reason}
D = {
 "V-FRQI": {
  "rel_age": r(0, "Founded 2010, platform launched 2012: well over 2 years at the 2026-10-21 lookup [I-8188056] [I-9791723]"),
  "rel_payout": r(1, "Federal court complaint filed 2026-04-09 (pro se) alleging rule changes used to block payouts, open: a documented payout dispute within 12 months [I-9404403] [I-5203277]"),
  "rel_rules": r(1, "Material adverse changes since the Sep/Oct 2025 observations: 50K payout cap $5,000 or 50% -> $2,000 [I-8074751], platforms cut to the firm's own only [I-8206118]; consistency rule changed [I-4756409] [I-4112139]; exact change dates not stated"),
  "rel_regulatory": r(0, "No regulatory action against the firm found (search-negative; NFA member per secondary press) [I-4580220] [I-1572424]"),
 },
 "V-PCDG": {
  "rel_age": r(1, "Operating since 2025 (waitlist page 2025-02-20; domain for sale 2024-09-01): under 2 years at the 2026-10-21 lookup [I-9375779] [I-4710756]"),
  "rel_payout": r(0, "Only review-site complaints (closures after payout approval, KYC locks) as pointers; no documented firm or regulator evidence [I-4117258] [I-1666918]", True),
  "rel_rules": r(1, "Within 12 months: split 100% of first $10k -> 90/10 (2025-11-28) and 50K evaluation fee $135 -> $172, reset $90 -> $120 (to 2026-10-05) [I-1735555] [I-7695386]; consistency 35% -> 40% is favourable"),
  "rel_regulatory": r(0, "None found (search-negative) [I-6243640] [I-8151075]"),
 },
 "V-PCAN": {
  "rel_age": r(0, "Site operating since at least 2022-12-05: about 3.9 years at lookup [I-9843044] [I-8936355]; a pointer says the futures program launched in 2024"),
  "rel_payout": r(0, "Review-site reports only (pointers); no firm or regulator evidence [I-8308966] [I-4305239]", True),
  "rel_rules": r(0, "Within 12 months only one clearly material adverse change (another plan's 50K target 2,500 -> 3,000, ~2026-04) plus a ~3% price rise and reset fees up on other sizes; the payout-balance change is dated 2025-09-12, outside the window; evaluation consistency removed is favourable; VPS clause content unknown [I-1314511] [I-3748198]"),
  "rel_regulatory": r(0, "None found (search-negative) [I-8403831] [I-9130969]"),
 },
 "V-CXFO": {
  "rel_age": r(0, "Operating since 2023 (site footer; month unverified): over 2 years at the 2026-10-21 lookup [I-7953269] [I-5272055]"),
  "rel_payout": r(0, "No firm or regulator evidence; third-party review pointers only; payout page states instant or 6-12 business-hour approval [I-6647421] [I-2983812]", True),
  "rel_rules": r(1, "Within 12 months: fee schedule raised (2025-10..2026-01), five products restricted from 2026-02-07, metals micro cap 5 at 50K from 2026-04-17, 7-day inactivity closure from 2026-08-25 [I-2907199] [I-1942835]"),
  "rel_regulatory": r(0, "None found (search-negative; a pointer says not registered, which is not an action) [I-4303166] [I-6322718]"),
 },
 "V-OJVP": {
  "rel_age": r(0, "Operating since 2021-06-12 or earlier [I-4816396] [I-3152090]"),
  "rel_payout": r(0, "Payout denials for 'flipping trading days' reported only on review sites and in search snippets [unverified] [I-8890274] [I-7825260] [I-0770312]", True),
  "rel_rules": r(1, "Within 12 months: automation narrowed to user-built tools with approval and a $100/month API fee, max funded accounts 11 -> 5, a platform removed (Dec 2025), 100%-of-first-$10k split removed and a cap from the 4th payout, inactivity rule, data fee up [I-8250711] [I-6930678]"),
  "rel_regulatory": r(0, "None found (search-negative) [I-9009153] [I-8752333]"),
 },
}
assert set(D) == set(json.load(open('/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e32b_briefs/F4_masked_firms.json'))['firms'])
json.dump(D, open('/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e32b_briefs/work/blind2/r_firms.json', 'w'), indent=1)
print('ok', len(D))
