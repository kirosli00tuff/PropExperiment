"""CRUDE_items_G.py: T4 absorption evidence (post-EIA drift or reversal)."""
from CRUDE_lib import it, src, write
LK = src("luo_kang_cl_inventory_news_firecrawl_quotes.md")
RS = {"file": "reports/stage_e28_briefs/pages/A1_crude/rousse_sevi_2016_feem.txt", "field": "lines 37-38, 965-969",
      "url": "https://feem-media.s3.eu-central-1.amazonaws.com/wp-content/uploads/NDL2016-070.pdf", "fetched_utc": "2026-10-21T12:16:08Z",
      "sha256": "66b425760be6cea48d1ce25ab87e6517eba16a66e3b9622eb74f520059d86b50"}
items = [
 it(51, ["MCL","QM","CL"], "T4", "event", "EIA crude-inventory shock does not predict nearby CL returns after the release (10:35-11:00 and 11:00-15:00 ET); it does predict returns in the 30 minutes and overnight before (leakage)", "product", "5-minute CL futures, about 2003-07..2010-12",
    "Luo and Kang (Illinois Institute of Technology), 'A Closer Look at High-frequency Prices and Trading Activities', ACFR conference paper (working paper). Absorption: within the 10:30-10:35 interval; no drift from 10:35 to 15:00 ET. Pre-release predictability is conditional on the ex-post shock (not an ex-ante signal). Text from a Firecrawl directQuote extraction of the PDF (raw PDF blocked by Cloudflare).",
    "we find that the inventory shock has no power to explain the return in the subsequent period after announcement (10:35AM to 11:00AM Wednesday) as well as in the remaining period (11:00AM to 3:00PM Wednesday)",
    LK, "full_text", negative=True),
 it(52, ["MCL","QM","CL"], "T4", "event", "after positive EIA surprises CL over-reacts: average drop about 0.5%, half reversed four hours later", "product", "CL front month 2007-2014",
    "Rousse and Sevi (2016), FEEM NDL2016-070 (Energy Journal 2019). Post-release movement over hours is a partial reversal, not a continuation (drift) of the initial move.",
    "days with positive surprises are characterized by a large average price drop of about 0.5% – traders take short positions as inventories are larger than expected – which is partly corrected in the hours following the news release. Four hours later, the drop is half as large, i.e. 0.25%.",
    RS, "full_text"),
 it(53, ["MCL","QM","CL"], "T4", "event", "announcement-day effect and pre-release anticipation at daily frequency (futures and options)", "product", "2003-06-16..2011-12-30 (446 EIA releases), daily returns",
    "Miao, Ramchander, Wang and Yang (2017 version), 'The Impact of Crude Oil Inventory Announcements on Prices: Evidence from Derivatives Markets' (CSU repository). Daily horizon only; no intraday absorption measure.",
    "We document evidence of a strong announcement day effect on both markets, and find prices to move in anticipation of the inventory surprise.",
    src("mountainscholar_miao_etal_inventory.pdf.txt"), "full_text"),
]
write("G", items)
