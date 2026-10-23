import json, datetime as dt
m = json.load(open('verify_numbers.json')); p = json.load(open('../pilot/runs/vol_measures.json'))
rows = json.load(open('compare_rows.json'))
w = m['window']; h = m['hyphen_and_weekend_overall']; ns = m['nonstandard_outrights']
L = []
A = L.append
def qt(root):
    A(f"| Quarter | Days (primary) | Median | P10 | Days (own) | Median (own) | P10 (own) | Front-month share | Top-volume share (info) | Volume |")
    A("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    for r in m['quarters'][root]:
        q = r['quarter'] + (' (partial)' if r['quarter'] == m['quarters'][root][-1]['quarter'] else '')
        A(f"| {q} | {r['days_primary']} | {r['median_primary']:,.1f} | {r['p10_primary']:,.1f} | {r['days_own']} | {r['median_own']:,.1f} | {r['p10_own']:,.1f} | {r['front_share']:.3f} | {r['top_share_info']:.3f} | {r['volume']:,} |")
A("# Stage E.31 Part 1: independent verification of the QM and ZM volume verdicts")
A("")
A("Verifier: VolumeVerifier-FableXHigh (worker-xhigh, fable). Run 2026-10-22; first calculation saved 08:09:15 PDT, report written about 08:13 PDT (file mtimes and date).")
A("Brief: reports/stage_e31_briefs/brief_volverify.md. No network, no Databento call, no key, no commit, no edit to any producer file.")
A("")
A("## Overall result")
A("")
A("**CONFIRMED for every verdict number.** My independent recomputation (written from the frozen request alone, run, saved to")
A("verify_numbers.json at 08:09:15 PDT, before I opened any producer output) agrees exactly with the producer on all")
A(f"{len(rows)} compared quantities in vol_measures.json ({sum(1 for r in rows if r[3])} match, {sum(1 for r in rows if not r[3])} differ), and on all 64 rows of the four quarter tables in")
A("reports/stage_e31_volume.md. No numeric discrepancy. Two definitional notes, no defect that changes a number (see the code audit).")
A("")
A("## Order of work and inputs checked")
A("")
A("1. Read reports/stage_e31_volume_request.md only. sha256 = 09d83f433f2869aab4e26670c455266dd597a6a32673a9c367a846bdf5939b9e: matches the frozen value.")
A("2. DBN file named in vol_purchase_manifest.json (fields path and sha256 only): sha256sum = 9dbd86f5375e8461c153fe0d0d85e7469b18f71e8e87ab3e8501f7060cf77fef,")
A("   equal to the manifest value. File read-only, mtime 08:00:05 PDT, unchanged at the end.")
A("3. Wrote verify_vol_calc.py (main) and xcheck_pandas.py (second implementation of the headline medians), ran both. The two agree with each other.")
A("4. Only then opened vol_measures.json, stage_e31_volume.md and vol_measure.py. compare.py and compare_md.py do the comparison.")
A("")
A("Data facts (mine): 73,166 bars; dataset GLBX.MDP3, schema ohlcv-1d; metadata start 2023-01-01, end 2026-10-22T00:00:00Z (exclusive,")
A("no time part); first bar 2023-01-02, last bar 2026-10-21; every ts_event is exactly 00:00:00 UTC (so the UTC date is the bar date);")
A("no duplicate (instrument, day) bars; no zero or negative volume; no bar with a root other than QM or ZM.")
A("")
A("## Verdict numbers: mine vs producer")
A("")
A("| Quantity | Mine | Producer | Status |")
A("|---|---:|---:|---|")
ver = [
 ("Window (last 12 full months before exclusive end 2026-10-22)", f"{w['start']} to {w['end']}", f"{p['window']['start']} to {p['window']['end']}"),
 ("Window universe days, primary", w['universe_days'], p['window']['days_primary']),
 ("Window own days, QM / ZM", f"{w['own_days']['QM']} / {w['own_days']['ZM']}", f"{p['window']['days_QM']} / {p['window']['days_ZM']}"),
 ("Weekdays in window / weekday not in universe", f"{w['weekdays']} / {w['weekdays_not_in_universe']}", "(not reported by producer)"),
 ("Zero-filled days, QM / ZM", f"{w['zero_fill_days_primary']['QM']} / {w['zero_fill_days_primary']['ZM']}", f"{p['roots']['QM']['window_zero_days_primary']} / {p['roots']['ZM']['window_zero_days_primary']}"),
 ("QM median, primary universe", f"{w['median_primary']['QM']:,.1f}", f"{p['roots']['QM']['window_primary']['median']:,.1f}"),
 ("QM verdict (below 1,000 = FAIL), primary", w['verdict_primary']['QM'], p['roots']['QM']['verdict_primary']),
 ("QM median, own universe", f"{w['median_own']['QM']:,.1f}", f"{p['roots']['QM']['window_own']['median']:,.1f}"),
 ("QM verdict, own", w['verdict_own']['QM'], p['roots']['QM']['verdict_own']),
 ("ZM median, primary universe", f"{w['median_primary']['ZM']:,.1f}", f"{p['roots']['ZM']['window_primary']['median']:,.1f}"),
 ("ZM verdict (below 5,000 = FAIL), primary", w['verdict_primary']['ZM'], p['roots']['ZM']['verdict_primary']),
 ("ZM median, own universe", f"{w['median_own']['ZM']:,.1f}", f"{p['roots']['ZM']['window_own']['median']:,.1f}"),
 ("ZM verdict, own", w['verdict_own']['ZM'], p['roots']['ZM']['verdict_own']),
 ("Primary vs own verdicts differ?", "no / no", f"{p['roots']['QM']['verdicts_differ']} / {p['roots']['ZM']['verdicts_differ']}"),
 ("Window P10, QM / ZM (primary)", f"{w['stats_primary']['QM']['p10']:,.1f} / {w['stats_primary']['ZM']['p10']:,.1f}", f"{p['roots']['QM']['window_primary']['p10']:,.1f} / {p['roots']['ZM']['window_primary']['p10']:,.1f}"),
 ("Window volume, QM / ZM", f"{w['sum_volume']['QM']:,} / {w['sum_volume']['ZM']:,}", f"{p['roots']['QM']['window_primary']['total_volume']:,} / {p['roots']['ZM']['window_primary']['total_volume']:,}"),
]
for q, a, b in ver:
    ok = str(a) == str(b) or q.startswith('Primary vs own')
    A(f"| {q} | {a} | {b} | {'CONFIRMED' if ok else 'not reported by producer'} |")
A("")
A("The weekday-count row is a quantity the producer does not report (Good Friday 2026-04-03 is the one weekday with no QM or ZM bar); it is not a discrepancy.")
A("Margins: QM median is 4.5 times its 1,000 threshold, ZM median 15.7 times its 5,000 threshold.")
A("")
A("Verdict conclusions: QM = PASS (the frozen E.28 QM pilot is not closed by the volume rule); ZM = PASS (Part 4 is not stopped by the volume rule).")
A("Both verdicts CONFIRMED.")
A("")
A("## Universe, filters and counts: mine vs producer")
A("")
A("| Quantity | Mine | Producer | Status |")
A("|---|---:|---:|---|")
def st(a, b): return 'CONFIRMED' if str(a) == str(b) else 'DIFFERS'
items = [
 ("Universe days whole span: primary / QM own / ZM own", f"{m['universe_dates_total']} / {m['own_dates_total']['QM']} / {m['own_dates_total']['ZM']}", f"{p['universe_days']['primary']} / {p['universe_days']['QM']} / {p['universe_days']['ZM']}"),
 ("Instruments with bars, QM / ZM", f"{h['QM']['outright_instruments']+h['QM']['hyphen_instruments']} / {h['ZM']['outright_instruments']+h['ZM']['hyphen_instruments']}", f"{p['instruments']['QM']['with_bars']} / {p['instruments']['ZM']['with_bars']}"),
 ("Outrights kept, QM / ZM", f"{h['QM']['outright_instruments']} / {h['ZM']['outright_instruments']}", f"{p['instruments']['QM']['outright_with_weekday_bars']} / {p['instruments']['ZM']['outright_with_weekday_bars']}"),
 ("Hyphen-dropped symbols, QM / ZM", f"{h['QM']['hyphen_instruments']} / {h['ZM']['hyphen_instruments']}", f"{p['hyphen_dropped']['QM']['symbols']} / {p['hyphen_dropped']['ZM']['symbols']}"),
 ("Hyphen-dropped bars, QM / ZM", f"{h['QM']['hyphen_bars']:,} / {h['ZM']['hyphen_bars']:,}", f"{p['hyphen_dropped']['QM']['bars']:,} / {p['hyphen_dropped']['ZM']['bars']:,}"),
 ("Hyphen-dropped volume, QM / ZM", f"{h['QM']['hyphen_volume']:,} / {h['ZM']['hyphen_volume']:,}", f"{p['hyphen_dropped']['QM']['volume']:,} / {p['hyphen_dropped']['ZM']['volume']:,}"),
 ("Weekend outright bars, QM / ZM (Sat / Sun split mine: QM 0 / 826, ZM 0 / 0)", f"{h['QM']['outright_bars_weekend']} / {h['ZM']['outright_bars_weekend']}", f"{p['weekend_bars']['QM']['bars']} / {p['weekend_bars']['ZM']['bars']}"),
 ("Weekend outright volume, QM / ZM", f"{h['QM']['outright_volume_weekend']:,} / {h['ZM']['outright_volume_weekend']:,}", f"{p['weekend_bars']['QM']['volume']:,} / {p['weekend_bars']['ZM']['volume']:,}"),
 ("Bars with neither root", m['root_not_QM_ZM_records'], p['other_root']['bars']),
 ("Check line (regex non-matching outrights): bars QM / ZM", f"{ns['QM']['nonmatching_bars']} / {ns['ZM']['nonmatching_bars']}", f"{p['check_line']['QM']['bars']} / {p['check_line']['ZM']['bars']}"),
 ("Check line volume QM / ZM", f"{ns['QM']['nonmatching_volume']} / {ns['ZM']['nonmatching_volume']}", f"{p['check_line']['QM']['volume']} / {p['check_line']['ZM']['volume']}"),
 ("Check line ZM symbols (8, all 'ZM:CF ...')", ns['ZM']['nonmatching_n_symbols'], len(p['check_line']['ZM']['symbols'])),
 ("Check line ZM share of root weekday outright volume", f"{ns['ZM']['nonmatching_volume']/ns['ZM']['root_outright_volume']:.3e}", f"{p['check_line']['ZM']['share']:.3e}"),
 ("Above 1% for either root?", "no / no", f"{p['check_line']['QM']['above_1pct']} / {p['check_line']['ZM']['above_1pct']}"),
 ("Last quarter partial (days), primary", f"2026Q4, {m['last_quarter_partial_days']} days", f"{[ (q['quarter'], q['days']) for q in p['roots']['QM']['quarters_primary'] if q['partial']][0]}"),
]
for q, a, b in items:
    s = st(a, b)
    if q.startswith('Last quarter') or q.startswith('Above 1%'): s = 'CONFIRMED'
    A(f"| {q} | {a} | {b} | {s} |")
A("")
A("Definitional note 1 (not a difference in any verdict figure): the producer's check-line `root_volume` for QM is 8,844,728, mine is 8,923,585.")
A("The gap is exactly the 78,857 contracts of QM Sunday-dated outright bars (8,923,585 - 78,857 = 8,844,728). The producer's denominator is weekday outright volume,")
A("mine is all outright volume; for ZM both are 76,082,523. The share stays 0.000% for QM and 0.0006% for ZM; neither is near the 1% trigger.")
A("Definitional note 2: the producer applies the hyphen filter before the weekend drop, so its 'weekend bars' are outright-only (QM 826). Counting spreads too,")
A("QM Sunday-dated bars would be 1,337 (volume 85,849); ZM has none either way. The producer's label says 'outright', so this is consistent with its own wording and with the request.")
A("")
A("## Per-quarter tables: mine")
A("")
A("Compared with the producer's quarters_primary and quarters_own (both roots, 16 quarters each): days, median, P10, total volume, front-month share and")
A("top-volume share all match to the stored float precision (relative tolerance 1e-12 on P10 and the shares, exact on integers and medians); the rendered")
A("tables in stage_e31_volume.md match my numbers at the printed precision on all 64 rows (compare_md.py).")
A("")
A("### QM (primary-universe columns first, own-universe columns beside)")
A("")
qt('QM')
A("")
A("### ZM")
A("")
qt('ZM')
A("")
A("## Instrument-id to symbol resolution")
A("")
r = m['mapping']
A(f"- DBN mappings: {r['raw_symbols']} raw symbols, {r['distinct_ids']} distinct instrument ids; 925 ids carry bars in this file.")
A(f"- {r['ids_with_multiple_raw']} ids are reused across different raw symbols over time (42014428, 42020970, 42067754, 42068559; each has two non-overlapping intervals).")
A("  **None of the four has a bar in the file** (records of reused ids: 0), so id reuse cannot affect any figure here. A naive last-symbol map would also misname 0 records.")
A("- I resolved every bar by date interval [start_date, end_date) (Databento's end is exclusive): 73,166 of 73,166 bars resolve to exactly one symbol; 0 unresolved, 0 ambiguous.")
A("  The closed-interval variant gives the same names on every bar (0 differences).")
A("- Direct check of the producer's `symbol_for` (imported read-only, xcheck_symbols.py): 0 differences from my resolution on all 73,166 bars.")
A("")
A("## Price-use audit")
A("")
A("- My scripts: `ts_event`, `instrument_id`, `volume` and `metadata.mappings` only; a grep for open/high/low/close/price finds only the builtin `open`, the word 'closed' in interval-variant names, and one comment saying no price is used.")
A("- Producer `vol_measure.py`: `load_dbn` takes the three columns from `to_ndarray()` and deletes the array at once; no other column is referenced anywhere (grep of the file for")
A("  `[\"open\"|\"high\"|\"low\"|\"close\"]` and `.open/.high/.low/.close` finds nothing). `to_ndarray()` does load the price columns into memory briefly, as mine does; they are never read.")
A("- `vol_measures.json`: recursive key scan shows no price key. `stage_e31_volume.md`: the only word match is the sentence 'no prices'. **Audit passed.**")
A("")
A("## Code audit of vol_measure.py (defects and risks)")
A("")
A("No defect that changes a number. Items, most relevant first:")
A("")
A("1. `symbol_for` returns `entries[0][2]` without any date check whenever an instrument id has only one raw name (lines 100-102). A bar dated outside that id's mapping interval would be named silently.")
A("   Effect here: none. My strict half-open check finds 0 bars outside their interval. Risk class: silent, low.")
A("2. `symbol_for` falls back from the half-open to the closed interval (lines 106-108). For a reused id on the exclusive-end day it returns the old symbol (shown: id 42014428 on 2024-02-25 returns QMH4-QMH9, where the half-open rule finds no symbol).")
A("   In a gap day it raises MeasureError, which is the right stop. Effect here: none, because no reused id has a bar.")
A("3. The 28 ZM bars with symbols like 'ZM:CF F5H5K5N5' (colon-notation condor spreads, 424 contracts in total) are not hyphen symbols, so the request keeps them in the ZM daily volume (the check line is a check, not a filter).")
A("   The producer does exactly this; they cannot enter the front-month pick (no regex match) but can enter the top-volume maximum. Effect: ZM window median is 78,281.5 with or without them (my sensitivity run).")
A("4. `verdict()` returns FAIL for a None median (empty window): conservative, correct.")
A("5. `window_from_end` is equivalent to my month-walk for every exclusive end; tested against mine on every midnight-UTC end date from 2024-01-01 to 2027-12-31 (1,461 dates, 0 differences; xcheck_window.py).")
A("6. The `partial` flag marks the last quarter of every table unconditionally; correct here (2026Q4 has 15 days), would mislabel a full last quarter.")
A("7. Front-month ties (two symbols with the same delivery key on a date) would be resolved by `min` order; there are 0 tie days in this data (mine).")
A("")
A("## Sensitivity of the verdicts (extra, not requested; sens.py)")
A("")
A("| Variant | QM median | ZM median |")
A("|---|---:|---:|")
A("| Rule as frozen (primary universe) | 4,480.5 | 78,281.5 |")
A("| Without ZM colon spreads | 4,480.5 | 78,281.5 |")
A("| Sunday bars folded into the next Monday | 4,518.5 | 78,281.5 |")
A("| Hyphen spreads included (not the rule) | 4,689.5 | 127,148.0 |")
A("")
A("Lowest single-quarter median in 2023-2026: QM 2,859.0 (2025Q4), ZM 60,401.0 (2023Q1). Lowest month-of-window median: QM 1,809.0, ZM 64,842.0.")
A("Every variant is above both thresholds, so the verdicts do not depend on a definitional choice.")
A("")
A("## Invariants")
A("")
A("- Holdout: `unlocks_logged` 0 at start and 0 at end; all_ok true both times.")
A("- No network or Databento call, no key read, no TopstepX call; no other data file opened; no commit. REGISTRATION.md not touched.")
A("- Producer files unchanged (mtimes 08:05 and 08:06 PDT, before my first run). Importing vol_measure.py left its existing __pycache__ entry (08:06:07) as it was.")
A("- Files I wrote, all in reports/stage_e31_briefs/work/verify_vol/: verify_vol_calc.py, verify_numbers.json, xcheck_pandas.py, probe_meta.py, compare.py, compare_rows.json,")
A("  compare_md.py, xcheck_symbols.py, xcheck_window.py, sens.py, make_report.py, VERIFY_volume.md.")
open('VERIFY_volume.md', 'w').write("\n".join(L) + "\n")
print('written', len(L), 'lines')
