"""Stage E.16 Task 4: assemble reports/stage_e16_prereg_H1.md .. _H5.md from their exact sources.

Each file quotes, verbatim and by line range: the stage prompt's hypothesis text (docs/prompts/STAGE_E.16.md), the
lead's operational spec for that test (reports/stage_e16_briefs/lead_spec.md section 4), and the overlap audit's
relation text (reports/stage_e16_overlap.md); then the test's fixed parameters (PER_TEST below), its power rows
(reports/stage_e16_power.json) and a pointer to the common file reports/stage_e16_prereg_common.md, which holds
every shared definition. Rerun after any change to the sources; the freeze manifest hashes the outputs.

    python3 reports/stage_e16_briefs/make_prereg.py
"""
from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PROMPT = REPO / "docs" / "prompts" / "STAGE_E.16.md"
SPEC = REPO / "reports" / "stage_e16_briefs" / "lead_spec.md"
OVERLAP = REPO / "reports" / "stage_e16_overlap.md"
POWER = REPO / "reports" / "stage_e16_power.json"

# (prompt lines, spec lines, overlap lines), 1-based inclusive, checked against their first words below.
RANGES = {
    "H1": ((83, 89), (120, 128), (113, 126)),
    "H2": ((91, 98), (129, 139), (156, 166)),
    "H3": ((100, 109), (140, 149), (192, 201)),
    "H4": ((111, 117), (150, 155), (240, 251)),
    "H5": ((119, 123), (156, 165), (266, 272)),
}
PER_TEST = {
    "H1": {"title": "settlement-window intraday momentum, pooled", "venue": "intraday; Topstep and IBKR",
           "products": "the 27 price paths (24 from 2010-07-01; RTY from listing 2017-07-10; TN from listing "
                       "2016-01-11; HE from 2017-07-03); vehicles per E.12/D2",
           "unit": "trade date (pooled equal-risk mean over products traded)", "nw_lags": 5, "year_units": 10,
           "notes": "Equity S_p was 15:15 CT before 2020-10-26 (R-S6; exits at the close of bar 15:14 by R-B1(a)); the result also shows the pooled statistics without product-dates with S_p > 15:08, marked descriptive (review F-14)."},
    "H2": {"title": "month-end NQ/ZN rebalancing pair", "venue": "multi-day; IBKR only",
           "products": "NQ (vehicle MNQ) and ZN (vehicle ZN), windows from 2010-07-01",
           "unit": "month (dated by its last joint trading day dL)", "nw_lags": 1, "year_units": 6,
           "notes": "Decision minute NQ's S on d5 (15:15 CT before 2020-10-26). Stated departure from the engine (review F-09): before 2020-10-26 NQ's entry is the open of the first bar after the 15:15 closure on the same trade date (R-B1(b)); none (equity before 2012-11-19): excluded, 'no entry bar'; counted 'entry after closure'. Warm-up 20 monthly units per leg (review F-15): no unit before 2016. H2 cannot pass on the fallback window (2 qualifying years)."},
    "H3": {"title": "Treasury auction cycle", "venue": "multi-day; IBKR only",
           "products": "ZT (2-Year), ZF (5-Year), ZN (10-Year), ZB (30-Year), windows from 2010-07-01",
           "unit": "auction (dated by its auction date t)", "nw_lags": 3, "year_units": 10,
           "notes": "Tightened (review F-04): announcemt_date on or before t-3, else excluded ('announced after entry'; 49 of 420 in 2010-06..2019-04 and 46 of 231 in 2019-05..2024-02, mostly 2-year notes); no date on file, excluded."},
    "H4": {"title": "next-day reversal of the settlement-window move", "venue": "intraday; Topstep and IBKR",
           "products": "as H1", "unit": "trade date (pooled, as H1)", "nw_lags": 5, "year_units": 10,
           "notes": "LE/HE entries at 08:01 in 2014-10-27..2016-02-28 pay the largest per-side slippage (R-B2); the result also shows the pooled statistics without those 'uncalibrated bucket' units, marked descriptive (review F-13)."},
    "H5": {"title": "equal-risk combination of H1 to H4", "venue": "mixed (H2 and H3 are IBKR only)",
           "products": "those of H1 to H4", "unit": "grid date (lead_spec section 4, H5)", "nw_lags": 5,
           "year_units": 10},
}
CHECKS = {"H1": ("H1, settlement-window", "H1 (settlement-window", "> H1 trades"),
          "H2": ("H2, month-end", "H2 (month-end", "> H2's bond leg"),
          "H3": ("H3, Treasury", "H3 (Treasury", "> H3 trades"),
          "H4": ("H4, next-day", "H4 (next-day", "> H4 enters"),
          "H5": ("H5, the combination", "H5 (combination", "> H5 combines")}


def lines(path: Path, span: tuple[int, int]) -> list[str]:
    text = path.read_text().splitlines()
    return text[span[0] - 1:span[1]]


def power_rows(test: str) -> str:
    if not POWER.is_file():
        return "(power table pending: reports/stage_e16_power.json not written yet)"
    body = json.loads(POWER.read_text())
    if body.get("provisional"):
        raise SystemExit("power table is provisional; rerun it with the real inputs first")
    rows = [r for r in body["power"]["rows"] if r["test"] == test]
    out = ["| Window | Prior | Net Sharpe (annual) | Units (calendar-only) | Qualifying years | "
           "P(pass all bars), Holm step 0.01 | at 0.05 | Analytic one-sided t power, 0.01 | at 0.05 |",
           "|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        sim, ana = r["sim_pass_all_bars"], r["analytic_t_power"]
        out.append(f"| {r['window']} | {r['prior']} | {r['sr_annual']} | {r['n_units']} | "
                   f"{r['qualifying_years']} | {sim['0.01']:.3f} | {sim['0.05']:.3f} | {ana['0.01']:.3f} | "
                   f"{ana['0.05']:.3f} |")
    return "\n".join(out)


def spec_span(test: str) -> tuple[int, int]:
    """The test's paragraph in lead_spec.md section 4: from 'Hn (' to the line before the next one or '## 5'."""
    text = SPEC.read_text().splitlines()
    start = next(i for i, s in enumerate(text) if s.startswith(f"{test} ("))
    end = next(i for i in range(start + 1, len(text))
               if text[i].startswith(("H1 (", "H2 (", "H3 (", "H4 (", "H5 (", "## 5")))
    while not text[end - 1].strip():
        end -= 1
    return start + 1, end


def build(test: str) -> str:
    (p_span, _, o_span), t = RANGES[test], PER_TEST[test]
    s_span = spec_span(test)
    prompt, spec, rel = lines(PROMPT, p_span), lines(SPEC, s_span), lines(OVERLAP, o_span)
    want = CHECKS[test]
    if not (prompt[0].startswith(want[0]) and spec[0].startswith(want[1]) and rel[0].startswith(want[2])):
        raise SystemExit(f"{test}: a source line range moved; fix RANGES")
    rel_text = "\n".join(rel)
    return f"""# Stage E.16 pre-registration {test}: {t['title']}

Status: FROZEN by the Stage E.16 freeze (reports/stage_e16_freeze.json; commit "E.16 base-rule freeze"). NOT
REGISTERED: Stage E.17 registers H1 to H5 together (N + 5) and runs this test once, in the order of
reports/stage_e16_handoff.md. Every definition shared by the five tests (prices and clock, costs, exclusions,
windows, the 2010-2024 splice and fallback rules, risk scaling, statistics, the pass bar, run discipline, the user
rulings U1 to U3b of 2026-10-09 and the lead's rulings) is in reports/stage_e16_prereg_common.md, which is part of
this pre-registration. Nothing here may be loosened; the code is base_rules/ as hashed in the freeze manifest.

## 1. The hypothesis as the stage prompt fixes it (docs/prompts/STAGE_E.16.md lines {p_span[0]}-{p_span[1]}, verbatim)

```
{chr(10).join(prompt)}
```

## 2. The operational definition (reports/stage_e16_briefs/lead_spec.md lines {s_span[0]}-{s_span[1]}, verbatim)

```
{chr(10).join(spec)}
```

## 3. Fixed parameters of this test

- Products and vehicles: {t['products']}.
- Venue: {t['venue']}.
- Unit of the test statistic: {t['unit']}.
- Cost cases: base (frozen D8, size one; decides the pass, U3a); stress (base plus one tick per side; reported;
  must-survive at any later holdout-2 registration, U3a); 1.5 x slippage (reported).
- One-sided p: the larger of the plain-t p (Student t, n - 1 df) and the Newey-West p with {t['nw_lags']} lag(s).
- Year stability: net P&L positive in at least two thirds of the calendar years holding at least
  {t['year_units']} units; fewer than 3 such years fails.
- Pass: Holm rejection at family-wise 0.05 across the registered tests, net mean > 0, n >= 30, year stability.
- Reported beside it: DSR at the program's N at run time, the stress and 1.5 x cases, exclusions by reason,
  per-product and per-year tables.
- Notes: {t.get('notes', 'none beyond the common file.')}

## 4. Relation to tested members (reports/stage_e16_overlap.md lines {o_span[0]}-{o_span[1]}, verbatim; lead ruling: KEEP)

{rel_text}

## 5. Power at the priors (reports/stage_e16_power.json; method in the common file)

{power_rows(test)}
"""


def main() -> None:
    for test in RANGES:
        out = REPO / "reports" / f"stage_e16_prereg_{test}.md"
        out.write_text(build(test))
        print(out.relative_to(REPO), len(out.read_text().splitlines()), "lines")


if __name__ == "__main__":
    main()
