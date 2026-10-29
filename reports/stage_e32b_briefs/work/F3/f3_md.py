"""Write reports/stage_e32b_briefs/F3_vol.md from F3_vol.json, work/F3/regression.json, parts and the check files.

Run from the repo root: uv run python reports/stage_e32b_briefs/work/F3/f3_md.py
"""
from __future__ import annotations

import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
BRIEFS = REPO / "reports/stage_e32b_briefs"
D = json.loads((BRIEFS / "F3_vol.json").read_text())
REG = json.loads((HERE / "regression.json").read_text())["roots"]
H = ("1", "2", "5", "15", "30", "60", "120", "240")


def f(x, nd=2) -> str:
    return "-" if x is None else f"{x:,.{nd}f}"


def part(code: str) -> dict:
    return json.loads((HERE / "parts" / f"{code}.json").read_text())


def table_main() -> list[str]:
    head = ("| Code | Status | Transfer | Tick | Dates | L_main | " + " | ".join(f"s{h}" for h in H)
            + " | OC s (m) | cc s | on s | R_d med (p99) | Main range med | Median close |")
    out = [head, "|" + "---|" * (head.count("|") - 1)]
    for c, r in D["roots"].items():
        tr = f"{r['oc1_source']} x {r['oc1_factor']:g}" if r["status"] == "OC1" else ""
        hs = " | ".join(f(r["h"][h]["sigma"]) for h in H)
        out.append(f"| {c} | {r['status']} | {tr} | {r['tick_size']:g} | {r['n_dates']} | {r['L_main'] or '-'} | "
                   f"{hs} | {f(r['OC']['sigma'])} ({f(r['OC']['m'])}) | {f(r['overnight']['cc']['sigma'])} | "
                   f"{f(r['overnight']['on']['sigma'])} | {f(r['R_d']['median'], 1)} ({f(r['R_d']['p99'], 1)}) | "
                   f"{f(r['main_range_median'], 1)} | {r['median_close'] if r['median_close'] is not None else '-'} |")
    return out


def table_m_p99() -> list[str]:
    out = ["| Code (owned) | " + " | ".join(f"m{h} / med{h} / p99_{h}" for h in ("5", "60", "240")) + " | n5 | n60 | n240 |",
           "|---|---|---|---|---|---|---|"]
    for c, r in D["roots"].items():
        if r["status"] != "owned":
            continue
        cells = [f"{f(r['h'][h]['m'])} / {f(r['h'][h]['median_abs'], 1)} / {f(r['h'][h]['p99_abs'], 1)}"
                 for h in ("5", "60", "240")]
        out.append(f"| {c} | " + " | ".join(cells) + " | " + " | ".join(str(r["h"][h]["n"]) for h in ("5", "60", "240"))
                   + " |")
    return out


def table_transfers() -> list[str]:
    out = ["| Code | Source | Own tick | Source tick | Factor | Tick source | Session |", "|---|---|---|---|---|---|---|"]
    for c, r in D["roots"].items():
        if r["status"] != "OC1":
            continue
        src = D["roots"][r["oc1_source"]]
        sess = next((x for x in r["flags"] if x.startswith("session")), "")
        out.append(f"| {c} | {r['oc1_source']} | {r['tick_size']:g} | {src['tick_size']:g} | {r['oc1_factor']:g} | "
                   f"{r['tick_source']} | {sess} |")
    return out


def table_unknown() -> list[str]:
    out = ["| Code | Tick | Tick source | Reason |", "|---|---|---|---|"]
    for c, r in D["roots"].items():
        if r["status"] == "unknown":
            out.append(f"| {c} | {r['tick_size']:g} | {r['tick_source']} | {r['flags'][-1]} |")
    return out


def table_holidays() -> list[str]:
    out = ["| Root | Calendar | Trade dates in data | Regular (used) | EARLY_HALT excluded | US holidays booked as trade "
           "dates | of which excluded | kept | cc/on pairs spanning an excluded date |", "|---|---|---|---|---|---|---|---|---|"]
    for c, r in D["roots"].items():
        if r["status"] != "owned":
            continue
        p = part(c)
        hd = p["holidays"]
        out.append(f"| {c} | {p['early_halt_calendar']} | {p['trade_dates_all']} | {p['n_dates']} | "
                   f"{len(p['early_halt_dates_excluded'])} | {hd['us_holiday_trade_dates_in_sample']} | "
                   f"{hd['us_holiday_dates_excluded']} | {hd['us_holiday_dates_kept']} | "
                   f"{p['overnight_pairs_span_excluded_date']} |")
    return out


def table_regression() -> list[str]:
    out = ["| Root | Dates F3 / A0 | Halt lists equal | sigma_1m A0-convention F3 / A0 (diff %) | changes F3 / A0 | "
           "sigma_1 spec F3 (diff % vs A0) | n_1 spec | R_d median F3 / A0 | implied RMS of the dropped open-minute "
           "changes (ticks, approx.) |", "|---|---|---|---|---|---|---|---|---|"]
    for c, v in REG.items():
        sa, n_a = v["sigma_1m_A0_convention"][0], v["n_changes_A0_convention"][0]
        ss, n_s = v["sigma_1_spec"][0], v["n_1_spec"][0]
        k = n_a - n_s
        rms = math.sqrt(max((n_a - 1) * sa ** 2 - (n_s - 1) * ss ** 2, 0.0) / k) if k else None
        out.append(f"| {c} | {v['n_dates'][0]} / {v['n_dates'][1]} | {v['early_halt_lists_equal']} | "
                   f"{sa:.4f} / {v['sigma_1m_A0_convention'][1]:.4f} ({v['sigma_1m_A0_convention'][2]:+.4f}) | "
                   f"{n_a} / {v['n_changes_A0_convention'][1]} | {ss:.4f} ({v['sigma_1_spec'][2]:+.3f}) | {n_s} | "
                   f"{v['R_d_median'][0]:g} / {v['R_d_median'][1]:.1f} | {f(rms, 1)} (k = {k}) |")
    return out


def table_pairs() -> list[str]:
    out = ["| Owned micro / owned full-size | " + " | ".join(f"s{h} ratio" for h in ("5", "30", "60", "240"))
           + " | R_d median ratio |", "|---|---|---|---|---|---|"]
    for a, b in (("MCL", "CL"), ("MGC", "GC"), ("MHG", "HG")):
        ra, rb = D["roots"][a], D["roots"][b]
        cells = [f"{ra['h'][h]['sigma'] / rb['h'][h]['sigma']:.3f}" for h in ("5", "30", "60", "240")]
        out.append(f"| {a} / {b} | " + " | ".join(cells) + f" | {ra['R_d']['median'] / rb['R_d']['median']:.3f} |")
    return out


def checks(name: str) -> list[str]:
    lines = (HERE / name).read_text().splitlines()
    return ["    " + x for x in lines]


def opens_summary() -> tuple[int, int]:
    log = (HERE / "opens.log").read_text().splitlines()
    return sum("| OPEN |" in x for x in log), sum("| REFUSED |" in x for x in log)


def main() -> None:
    n_open, n_ref = opens_summary()
    counts = {s: sum(r["status"] == s for r in D["roots"].values()) for s in ("owned", "OC1", "unknown")}
    owned = [c for c, r in D["roots"].items() if r["status"] == "owned"]
    text = TEMPLATE.format(
        gen=D["generated_pdt"], sha=D["spec_sha256"], match=D["spec_sha256_matches_frozen"], n_files=len(D["files_opened"]),
        n_open=n_open, n_ref=n_ref, owned=counts["owned"], oc1=counts["OC1"], unk=counts["unknown"],
        owned_list=" ".join(owned),
        t_main="\n".join(table_main()), t_mp="\n".join(table_m_p99()), t_tr="\n".join(table_transfers()),
        t_unk="\n".join(table_unknown()), t_hol="\n".join(table_holidays()), t_reg="\n".join(table_regression()),
        t_pairs="\n".join(table_pairs()), before="\n".join(checks("holdout_before.txt")),
        after="\n".join(checks("holdout_after.txt")))
    (BRIEFS / "F3_vol.md").write_text(text)
    print(f"wrote {BRIEFS / 'F3_vol.md'} ({len(text.splitlines())} lines)")


TEMPLATE = """# Stage E.32b F3: volatility at horizons (spec section 2)

Worker VolCoder (Opus 5.5, xhigh), JSON generated {gen}. Facts only: volatility statistics, no signed, conditional or
autocorrelation statistic, nothing about any strategy. Contract: reports/stage_e32b_ranking_spec.md sections 0 and 2
(sha256 {sha}, matches the frozen hash: {match}). Machine-readable output: reports/stage_e32b_briefs/F3_vol.json
(schema of brief_wave_b.md "Shared data contract"; extra keys per root: family, tick_source, flags, and for owned roots
early_halt_dates_excluded_n, us_holiday_trade_dates, overnight_pairs_span_excluded_date). Code, tests and logs:
reports/stage_e32b_briefs/work/F3/ (f3_guard.py, f3_core.py, f3_vol.py, f3_md.py, test_f3.py, run.log, opens.log,
parts/<ROOT>.json, regression.json, holdout_before.txt, holdout_after.txt, time_run.txt).

Counts: {owned} owned, {oc1} OC1, {unk} unknown (47 codes). Owned: {owned_list}. NQ is computed as MNQ's transfer
source and flagged "excluded from scoring (V49)".

## Data rule, as applied (spec 2.1)

- Every bar file was opened through f3_guard.BarGuard. It resolves the path (os.path.realpath; data/vendor/.../ohlcv-1m
  is a symlink to /mnt/large-storage/...) and refuses before opening unless the resolved path is exactly
  <resolved ohlcv-1m>/<ROOT>_v_0/range=YYYY-MM-01_YYYY-MM-01.dbn.zst with ROOT one of the 47 codes and the range one of
  the 12 months 2022-11 .. 2023-10, and the file is a regular file. Any given or resolved path containing mbo, mbp,
  tbbo, holdout, sealed or enc (case-insensitive) is refused first. The reader is called on the resolved (checked)
  path. Every open and refusal is logged with its PDT time in work/F3/opens.log.
- Files opened: {n_files} distinct (22 roots x 12 months); opens.log has {n_open} OPEN lines and {n_ref} REFUSED lines
  (one probe run on ZC, then the full run, which skipped ZC's finished part; the re-assembly opened nothing). Nothing
  outside the 12 allow-listed months was opened: not the 2022-10 file E.28 A0 also read (so trade date 2022-11-01
  lacks its 17:00-19:00 CT evening bars; its main session is complete), no pilot, research, holdout-2 or embargo file,
  no mbo, mbp-1 or tbbo file, nothing of the E.32 soy test seal (2017-05 .. 2020-11).
- Guard unit tests (test_f3.py, synthetic file tree): allowed files pass and are logged; refused, with the reader never
  called: the months 2022-10, 2023-11 and 2024-03, a root outside the 47 (MES), a wrong suffix, an absent allowed
  name, a ../ traversal to MES, a path into mbp-1, a symlink whose given path contains each forbidden token, a symlink
  resolving into mbp-1 and one resolving outside the ohlcv-1m folder; on the real tree, 2024-03, 2023-11 and a 2019 ZS
  path are refused without opening.

Before the run (work/F3/holdout_before.txt):

{before}

After the run (work/F3/holdout_after.txt; identical apart from the header and the date):

{after}

## Method (spec 2.2 to 2.4; E.28 A0 code reused)

- Trade dates, scheduled grid, main session and EARLY_HALT exclusion are A0's functions, copied unchanged into
  f3_core.py: trade date by the 17:00 CT rule (Saturday and Sunday roll to Monday); the grid is the group calendar's
  scheduled minutes (data/calendars/<group>.py SESSIONS) cut to the trade date's first and last bar; main session =
  grid minutes whose start is in [06:30, 13:00) America/Vancouver, which gives 06:30-13:00 (390 minutes) for equity,
  rates, fx, energy, metals and crypto and 06:30-11:20 (290 minutes) for grains; close carried forward from the last
  bar at or before each grid minute; the instrument at a grid minute is that bar's instrument_id. Dates in the group's
  EARLY_HALT list are excluded (data.cme_calendar for equity, data/calendars/<group>.py otherwise). L_main and
  main_session_pt are read off the group calendar on a regular date (2023-06-14); the most frequent number of main grid
  minutes per date in the data equals L_main for every owned root.
- Ticks: price changes in vendor fixed-point units divided by the vendor tick (rules/products.py tick_size x
  vendor_price_factor), so every change is an exact multiple of a tick. tick_size and median_close in the JSON are in
  the exchange units of rules/products.py (USD per bushel, pound, ton, barrel, MMBtu or ounce; index points; points of
  par; USD per foreign unit). Codes absent from rules/products.py (BTC, MET, ETH, 2YY, 5YY, 10Y, 30Y, MZC, MZS, MZW,
  MZL, MZM, XC, XK, XW) take E.28 A1_<family>.json tick_size, converted from US cents to USD where A1 states cents, and
  are flagged.
- D_h(t) = close(t+h) - close(t) for every main grid minute t whose t+h is a main grid minute of the same trade date,
  with the same instrument at both ends (overlapping starts), h in 1, 2, 5, 15, 30, 60, 120, 240. sigma_h = SD (ddof 1);
  m = mean |D_h|; median |D_h|; p99 |D_h| (numpy linear interpolation); n = count of pairs.
- OC = close at the last main grid minute minus close at the first main grid minute, same instrument at both ends
  (sigma, mean |OC|).
- Overnight: cc = last main close of a trade date minus that of the previous sample trade date; on = first main close of
  a trade date minus the previous sample trade date's last main close; each kept only with the same instrument at both
  ends. "Consecutive" = consecutive regular (non-excluded) trade dates in the data, so a pair can span an excluded
  EARLY_HALT date (counted per root in the holiday table; under CME's own convention the holiday session belongs to the
  next trade date anyway).
- R_d: E.28's definition, the full trade date's high minus low of the bars of the instrument traded in the day's last
  bar; median and p99 over regular dates. Main range: high minus low of the bars that start on a main grid minute, of the
  instrument of the last such bar; median over dates.
- median_close: the median over regular dates of the last main-session close (exchange units).
- OC-1 (spec 2.4): a code without the 12 window files takes its sibling's tick statistics (sigma, m, median |D|, p99,
  OC, cc, on, R_d, main range) times sibling tick / own tick; counts (n, n_dates) are the sibling's; median_close is
  the sibling's price (same price of the same underlying). L_main and main_session_pt come from the code's own group
  calendar where data.calendars lists the code, else from the sibling (flagged). Unknown: no transfer (SI, SIL, MET,
  ETH: no owned sibling; 2YY, 5YY, 10Y, 30Y: yield-quoted).

One property of the spec's D_h definition, reported for the lead (not changed): because both t and t+h must be main
minutes, the move of the first main bar itself (06:30-06:31 PT, the US cash open for equity index futures) is never
part of any D_h; OC starts at the same close. E.28 A0's sigma_1m counted it (the change from 06:29 to 06:30). See the
regression section.

## Table 1. Volatility per code, ticks of the code's own tick (window 2022-11-01..2023-10-31, regular trade dates)

s<h> = sigma of D_h. OC s (m) = SD (mean |OC|). cc, on = overnight SDs. R_d and main range in ticks. Median close in
exchange units.

{t_main}

## Table 2. Owned roots: mean |D_h| / median |D_h| / p99 |D_h| and pair counts at h = 5, 60, 240

{t_mp}

## Table 3. OC-1 transfers

{t_tr}

## Table 4. Unknown (no sigma)

{t_unk}

## Table 5. Trade-date quirk (E.21): US holidays booked as trade dates, per owned root

A0's handling: EARLY_HALT dates of the group calendar are excluded. "US holidays booked as trade dates" counts trade
dates in the raw window data that appear in data.cme_calendar.HOLIDAYS (the US holiday list). Equity: all 10
excluded. Rates, energy and metals: all excluded except 2023-07-03 (the day before Independence Day), which their group
calendars do not list (energy and metals have no 2023-04-07 bars: full closure). Fx and crypto: their calendars list
only 2022-11-25 and 2023-04-07 as EARLY_HALT, so the other 8 US holiday sessions (2022-11-24, 2023-01-16, 2023-02-20,
2023-05-29, 2023-06-19, 2023-07-03, 2023-07-04, 2023-09-04) stay in the sample as short days (A0 caveat 3). Grains:
2023-07-03 stays.

{t_hol}

## Regression against E.28 A0 (reports/stage_e28_briefs/A0_contract_stats.json), all 22 owned roots

Statistics both compute on the same window: the number of regular trade dates, the EARLY_HALT list, sigma_1m and its
count of changes, and the R_d median. F3 also computes A0's sigma_1m convention (the change ending at each main minute)
as a diagnostic only (not in F3_vol.json).

{t_reg}

- Under A0's convention every root matches exactly: same dates, same EARLY_HALT lists, same change counts, sigma_1m
  equal to at least 4 decimals, R_d medians equal (A0's values differ only by float rounding). Not opening the 2022-10
  file changes nothing here.
- The spec-literal sigma_1 is lower by 0.07% to 1.04% on the 17 roots whose 06:29 PT minute is on the grid, and equal
  for the 5 grain roots (06:29 PT is in the 07:45-08:30 CT break, so A0 also dropped that change). The count gap is
  exactly one change per trade date (k = n_dates). Above 1%: RTY (-1.04%). Explanation: the dropped change is the move
  of the 06:30 PT bar, the equity cash open; the implied RMS of those changes is 2.2 to 3.0 times sigma_1 for the
  three equity roots and 1.3 to 1.7 times for the others (last column, an approximation from the two SDs and counts),
  so dropping 249 of 97,110 changes lowers the SD by about 1.0% for RTY, 0.8% for YM and 0.5% for NQ. This follows
  from the spec's definition; it is not a bug.

## OC-1 check on owned pairs (micro vs full-size, same tick)

The three owned micro/full-size pairs on the same tick show how close a transferred statistic is to an owned one.

{t_pairs}

## Run

`flock reports/stage_e32b_briefs/work/heavy.lock nice -n 10 uv run python reports/stage_e32b_briefs/work/F3/f3_vol.py`,
one process, resumable (one part per root). Free memory before: about 10.5 GB available. Probe on ZC: 0.8 s; full run
(21 roots plus assembly): 7.2 s wall, peak RSS 214 MB (/usr/bin/time, work/F3/time_run.txt). Unit tests:
`uv run pytest -q reports/stage_e32b_briefs/work/F3/test_f3.py` (29 passed).
"""

if __name__ == "__main__":
    main()
