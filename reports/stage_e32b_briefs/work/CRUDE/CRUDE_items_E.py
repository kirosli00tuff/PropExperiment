"""CRUDE_items_E.py: additional T2b filings (2023-2024 liquidity programs)."""
from CRUDE_lib import it, src, write
items = [
 it(46, ["CL","MCL","QM"], "T2b", "mm_program", "NYMEX Crude Liquidity Program (CL and BZ on Globex), volume-threshold incentives", "product", "2024-06-01..2025-01-31 (Submission 24-221)",
    "Third CL-covering incentive program found for 2021-2026. Volume thresholds, no quoting obligation stated. Leader program for MCL and QM.",
    "Crude Oil Futures (“CL”) and Brent Last Day Financial Futures (“BZ”) traded on the CME Globex Platform (“Products”). | Start date is June 1, 2024. End date is January 31, 2025.",
    src("cftc_nymex_24-221_crude_liquidity_program.pdf.txt"), "full_text"),
 it(47, ["CL","MCL","QM"], "T2b", "mm_program", "NYMEX Oil Liquidity Provider Program: covers WTI Houston and WTI Midland (Argus) vs WTI Trade Month futures, not CL outrights", "product_group", "2022-10-01..2024-01-31 (Submission 23-190)",
    "Quoting program on crude differential futures (HTT, WTT); CL outrights not in scope. The 2025-12-02 'Modifications to the NYMEX Oil Liquidity Provider Program' filing was not read; its scope may differ.",
    "WTI Houston (Argus) vs. WTI Trade Month Futures (“HTT”) and WTI Midland (Argus) vs. WTI Trade Month Futures (“WTT”) that are traded on Globex (“Products”).",
    src("cftc_nymex_23-190_oil_LPP.pdf.txt"), "full_text", negative=True),
]
write("E", items)
