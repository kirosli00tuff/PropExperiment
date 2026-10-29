"""CRUDE_items_B.py: T2b CME volume-incentive programs from CFTC filings (new fetches)."""
from CRUDE_lib import it, src, write
items = [
 it(25, ["CL","MCL","QM"], "T2b", "mm_program", "NYMEX Crude and Refined Futures Volume Incentive Program (CL, HO, RB on Globex)", "product", "2018-02-01..2025-01-31 (term as amended by Submission 23-491, filed 2023-12-15)",
    "Volume-incentive program for large participants in CL outright futures on Globex; predetermined volume thresholds; in force through 2021-2024 per the stated term. Applies to MCL and QM only as their leader's (CL) program.",
    "Crude Oil Futures (“CL”), NY Harbor ULSD Futures (“HO”), and RBOB Gasoline Futures (“RB”) that are traded on Globex® (“Products”). | Start date is February 1, 2018. End date is January 31, 2024 January 31, 2025.",
    src("cftc_nymex_23-491_crude_refined_VIP.pdf.txt"), "full_text"),
 it(26, ["CL","MCL","QM"], "T2b", "mm_program", "NYMEX Crude Oil Incentive Program (CL and BZ on Globex)", "product", "2024-02-15..2025-01-31 (Submission 24-365 extension, effective 2024-09-01)",
    "Liquidity-building incentive program covering CL outrights; participants unlimited; incentives on meeting requirements. Leader program for MCL and QM.",
    "Crude Oil Futures (“CL”) and Brent Last Day Financial Futures (“BZ”) that are traded on the CME Globex Platform (“Products”). | Start date is February 15, 2024. End date is August 31, 2024 January 31, 2025.",
    src("cftc_nymex_24-365_crude_oil_IP.pdf.txt"), "full_text"),
 it(27, ["CL","MCL","QM"], "T2b", "mm_program", "NYMEX Oil Incentive Program: does not cover CL (third-party-assessment crude products only)", "product_group", "extended to 2026-01-31 (Submission 24-472, effective 2024-12-01)",
    "Scope is North American crude futures and options priced off a third-party assessment; CL (an exchange price) is not in scope by the stated definition. Recorded so the lead does not count it for CL.",
    "All North American crude oil futures and options products that incorporate a third-party price assessment as either the price of the contract or the price of the first leg of the contract (“Products”).",
    src("cftc_nymex_24-472_oil_IP.pdf.txt"), "full_text", negative=True),
]
write("B", items)
