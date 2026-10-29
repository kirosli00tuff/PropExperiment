"""CRUDE_items_F.py: T1 CL spread and touch from CME publications via Wayback (Q1 2023 whitepaper, 2019 article)."""
from CRUDE_lib import it, src, write
WP = src("wayback_cme_asia_hours_whitepaper.html.txt", "Table 3 and Table 4; parsed by work/CRUDE/CRUDE_parse_cme_tables.py")
AR = src("wayback_cme_asia_us_oil_exports.html.txt", "line 44")
items = [
 it(48, ["CL","MCL","QM"], "T1", "median_spread_ticks", 1.28, "product", "Q1 2023, most active CL month, hourly averages",
    "CME whitepaper 'Leveraging CME Group Asia Trading Hours Liquidity for Cross Commodity Trading' (Wayback 2024 copy). Table 3, WTI column, average best bid/ask spread in ticks by hour (Singapore time). US day session 9:00-14:30 ET = 22:00-03:30 SGT in Q1 2023 (EST): hourly averages 1.28, 1.29, 1.28, 1.27, 1.29, 1.28. All 24 hours 1.27 to 1.73 (widest 6:00 SGT, around the daily pause). These are time averages by hour, not medians. CL only; MCL and QM leader fact.",
    "Table 3 shows the average bid/ask spread by hour of the most active contract month in each market during the first quarter of 2023. | The bid/ask spread is expressed in number of minimum price fluctuations (ticks) | 22:00 row WTI 1.28; 0:00 row WTI 1.28",
    WP, "full_text"),
 it(49, ["CL","MCL","QM"], "T1", "touch_size", 8, "product", "Q1 2023, most active CL month, hourly averages",
    "Same whitepaper, Table 4, WTI column, average top-of-book bid/ask order quantity (lots) by hour (SGT). US day-session hours 22:00-03:00 SGT: 7.59, 7.70, 7.98, 8.30, 8.62, 9.12 (about 8 lots); lowest 4.38 at 6:00 SGT. Averages, not medians. CL only; MCL and QM leader fact.",
    "It measures the average top-of-book bid and ask order quantity in number of contracts on CME Globex. | 0:00 row WTI 7.98; 3:00 row WTI 9.12",
    WP, "full_text"),
 it(50, ["CL","MCL","QM"], "T1", "touch_size", 25, "product", "2018 (CME data), US trading hours",
    "CME article 'Asia is a key destination for U.S. oil exports' (17 Apr 2019, Wayback 2024 copy). Average executable lots at the best bid-ask: 25 in US hours, 23 in Singapore hours; 123 and 111 lots within a 3 basis-point spread. Measure differs from item CRUDE-49 (definition not given; possibly both sides or cumulative at best price).",
    "On average, a trader can execute 25 lots at the best bid-ask prices during U.S. trading hours, and 23 during Singapore trading hours.",
    AR, "full_text"),
]
write("F", items)
