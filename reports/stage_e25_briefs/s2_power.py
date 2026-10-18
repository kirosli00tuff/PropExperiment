"""Stage E.25 S2: hurdle ratios and research-window power at the PUBLISHED effect sizes.

Inputs are published figures quoted in the reader files (cited per row); no data is read.
Method: net per trade = gross - RT (D8 ticks; MES from the Stage D model); per-trade sd from
the published sd or from the published t over n; expected t on the research window
= (net / sd) * sqrt(n_rw); power = Phi(E[t] - z) at one-sided 5% (z 1.645) and at the
first Holm step for k = 5 registered trials (C1, C2, C3, C4, C5; z for 0.05 / 5 = 0.01, 2.326).
v2 (S4 review findings 1-5, 13): C1 dispersion is per TRADED day; C2/C3 event count from one
rule; C3 at the tradable 17:00 CT leg as well as the published upper bound; C4 as designed
(FOMC-conditional, n 3); C5's sd is DF3's inference.
Usage: python3 -I reports/stage_e25_briefs/s2_power.py
"""
import math

Z_05 = 1.645
Z_HOLM5 = 2.326
RW_DAYS = 299  # equity trade dates 2025-04-01..2026-06-19 (E.7 count, K1 inventory)
# Event-count rule for C2/C3 (DF2): the 15 monthly a.m.-settlement expiries in the RW, the two
# Thursday-shifted ones (2025-04-17, 2026-06-18) included; 5 are quarterly. If the program's roll
# blackout removes the quarterly dates, n = 10. Unchecked against docs/SCREENING.md.
N_EXPIRY_ALL, N_EXPIRY_OFFQ = 15, 10


def phi(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def row(name, gross_ticks, rt_ticks, sd_ticks, n_rw, note):
    net = gross_ticks - rt_ticks
    exp_t = net / sd_ticks * math.sqrt(n_rw)
    print(f"{name:40s} gross {gross_ticks:6.2f} RT {rt_ticks:5.3f} ratio {gross_ticks / rt_ticks:5.2f} "
          f"net {net:6.2f} sd {sd_ticks:7.1f} n_rw {n_rw:4d} E[t] {exp_t:5.2f} "
          f"power05 {phi(exp_t - Z_05):4.2f} powerHolm5 {phi(exp_t - Z_HOLM5):4.2f} | {note}")


# C1 noise-area momentum (R10-C1, DF1): 4.0 bp gross per trade; at ES 6,000 = 9.6 MES ticks, at NQ 24,000
# = 38.4 MNQ ticks. The published daily t 5.34 is over 2,620 TRADED days in a sample of about 4,280 trading
# days (May 2007-Apr 2024; DF1 l.38, l.47), so the SR 0.1043 is per traded day; 7,668 trades / 2,620 = 2.93
# trades per traded day. Expected traded days in the RW = 299 x 2,620 / 4,280.
TRADED_SHARE = 2620 / 4280
SR_TRADED_DAY = 5.34 / math.sqrt(2620)
TRADES_PER_TRADED_DAY = 7668 / 2620
for micro, gross, rt in (("MES", 9.6, 2.03), ("MNQ", 38.4, 4.119)):
    g_day = gross * TRADES_PER_TRADED_DAY
    sd_day = g_day / SR_TRADED_DAY
    row(f"C1 noise-area momentum {micro} (traded days)", g_day, rt * TRADES_PER_TRADED_DAY, sd_day,
        round(RW_DAYS * TRADED_SHARE), "R10-C1/DF1; NQ 24,000 for MNQ; published SR treated as gross")
# Forward record of 250 trading days (C1 design): 153 expected traded days.
for micro, gross, rt in (("MES", 9.6, 2.03), ("MNQ", 38.4, 4.119)):
    g_day = gross * TRADES_PER_TRADED_DAY
    row(f"C1 forward 250 days {micro}", g_day, rt * TRADES_PER_TRADED_DAY, g_day / SR_TRADED_DAY,
        round(250 * TRADED_SHARE), "C1 forward design")

bp_to_mes = 6000 / 10000 / 0.25
# C2 3rd-Friday reversal leg (RD4-C1/R12-C1/R17-C1, DF2): -12.89 bp open-to-close, sd 80.45 bp, ES 6,000.
for n in (N_EXPIRY_OFFQ, N_EXPIRY_ALL):
    row(f"C2 3rd-Fri open->close short n{n}", 12.89 * bp_to_mes, 2.03, 80.45 * bp_to_mes, n,
        "DF2-verified Table II; n 10 if the roll blackout removes quarterly dates")
# C3 run-up leg: published Thu RTH close -> Fri open +14.30 bp (upper bound for a 17:00 CT entry) and the
# tradable 17:00 CT -> open leg +12.75 bp (DF2, digitized from the 2026 figure); sd 60.53 bp.
for bp, lab in ((14.30, "published 14.30 (upper bound)"), (12.75, "17:00 CT leg 12.75 (digitized)")):
    for n in (N_EXPIRY_OFFQ, N_EXPIRY_ALL):
        row(f"C3 run-up {bp:.2f}bp n{n}", bp * bp_to_mes, 2.03, 60.53 * bp_to_mes, n, f"DF2: {lab}")


def zn(bp_cash):
    """Cash 10-year return in bp -> ZN ticks (x0.69 futures/cash, ZN price 111, tick 1/64)."""
    return bp_cash * 0.69 * 111 / 10000 * 64


# C4 pre-refunding Treasury gain (RD2-C1, DF3) as designed: only pre-TRA days with an FOMC statement in the
# preceding five days, 3 in the RW (DF3). Unconditional 12.62 bp (sd 43.15) and the paper's conditional
# "FOMC Earlier" cell 23.65 bp (SE 6.15), using the full-sample sd 43.15 (the cell's sd is not published).
row("C4 pre-refunding ZN 12.62bp n3", zn(12.62), 1.168, zn(43.15), 3, "DF3; unconditional size, conditional n")
row("C4 pre-refunding ZN cond 23.65bp n3", zn(23.65), 1.168, zn(43.15), 3, "DF3 Table 11 cell; full-sample sd")
row("C4 pre-refunding ZN 12.62bp n5 (uncond.)", zn(12.62), 1.168, zn(43.15), 5, "all five pre-TRA days")
# C5 pre-FOMC Treasury drift (RD2-C2, DF3): 7.26 bp on 10-year futures, t 2.82; per-event sd inferred by DF3
# from N about 171 (not published).
g5 = 7.26 * 111 / 10000 * 64
row("C5 pre-FOMC drift ZN n10", g5, 1.168, g5 / (2.82 / math.sqrt(171)), 10, "DF3; sd inferred (N ~171)")

print("--- sensitivity at the verified post-2015 / later-draft sizes (DF2, DF3) ---")
row(f"C2s reversal 14.8bp n{N_EXPIRY_ALL}", 14.8 * bp_to_mes, 2.03, 80.45 * bp_to_mes, N_EXPIRY_ALL,
    "DF2 2022-23 subperiod, digitized; not significant alone")
row(f"C3s run-up 4.2bp n{N_EXPIRY_ALL}", 4.2 * bp_to_mes, 2.03, 60.53 * bp_to_mes, N_EXPIRY_ALL, "DF2 2015-23 subperiod")
row(f"C3s run-up 1.6bp n{N_EXPIRY_ALL}", 1.6 * bp_to_mes, 2.03, 60.53 * bp_to_mes, N_EXPIRY_ALL, "DF2 2022-23 subperiod")
row("C4s pre-refunding FE 9.40bp n3", zn(9.40), 1.168, zn(4.03 * math.sqrt(129)), 3,
    "DF3: WZ fixed-effects estimate (unconditional size)")
g5s = 6.9 * 111 / 10000 * 64
row("C5s pre-FOMC Dec-2025 draft n10", g5s, 1.168, g5s / (2.24 / math.sqrt(171)), 10, "DF3: earlier draft figure")
