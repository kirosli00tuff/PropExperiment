"""CRUDE_items_H.py: Brent intraday efficiency (other venue, same asset)."""
from CRUDE_lib import it, src, write
items = [
 it(54, ["MCL","QM","CL"], "T6", "directional_study", "ICE Brent: inefficient on average at sampling under 10 minutes; efficiency at lower frequencies (up to 2 hours) improves over 2006-2021; costs not included", "other_venue", "ICE Brent futures 2006-2021, 1-minute to 2-hour sampling",
    "Smith-Meyer, Haugom and Ewald (2025), International Review of Financial Analysis 105:104424 (open access). Efficiency measure (AMIM, autocorrelation-based), not a trading test; authors state transaction costs not included. Same asset (crude), another benchmark and venue.",
    "At very high sampling frequencies (less than 10 min), the market is on average inefficient. For lower sampling frequencies, efficiency in Brent oil futures generally improves over the examined sample period.",
    src("gla_363709_brent_intraday_efficiency.pdf.txt"), "full_text"),
]
write("H", items)
