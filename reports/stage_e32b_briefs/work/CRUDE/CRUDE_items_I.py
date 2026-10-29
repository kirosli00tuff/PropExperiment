"""CRUDE_items_I.py: T2a CME 2010 algorithmic share."""
from CRUDE_lib import it, src, write
items = [
 it(55, ["CL","MCL","QM"], "T2a", "auto_share_pct", 35.34, "product", "Q1 2010",
    "CME Group research note 'Algo and HFT Trading' (June 2010; Wayback copy). Share of CL (Crude Oil futures) volume from algorithmic trading (AT, identified by Globex tag) 35.34%; 71.24% of message traffic. Pre-2012 figure; exchange publication. Lowest of the five products shown (E-mini S&P 51.66%, EuroFX 69.32%, Eurodollar 51.29%, 10-Yr 49.88%). Post-2012 CL shares are in the CFTC series owned by RatesReader (F2_shared_cftc_automation.json).",
    "Exhibit 1: Algorithmic Activity | (1st Qtr 2010) | Crude Oil Futures 35.34% 71.24% | displaying the least amount of AT activity.",
    src("wayback_cme_algo_hft_trading_0610.pdf.txt"), "full_text"),
]
write("I", items)
