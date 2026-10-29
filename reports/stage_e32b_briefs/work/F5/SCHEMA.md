# F5 schemas (E.32b, spec section 7)

Written by HoldingCoder (Opus 5.5, xhigh) on 2026-10-28 from 23:22 PDT. The fact field names follow the shared data
contract in reports/stage_e32b_briefs/brief_wave_b.md and ScoreCoder's conventions in work/score/s32b_layer1.py and
s32b_layer2.py. work/score/SCHEMA.md did not exist when this file was written. If it later differs from what is read
below, it governs, and f5_holding.py needs a matching change. Every JSON input must carry
`"spec_sha256": "09ebe6970fcf027009152fa81a414360a015d535b095138cdf65cf1a4eb58635"`, or the script refuses to run.

## Inputs

### SR80.json (work/F5/SR80.json, written by sr80.py)

    { "spec_sha256", "generated_pdt", "generated_by", "inputs": {"N", "T_disc", "T_test", ...},
      "formula": {...}, "thresholds": {"SR0_disc", "SR0_test", "G3", "t_bar_test", "DSR_test", "b_test", "G4",
      "G3_G4_binding"},
      "SR80": {"disc_G3", "disc_G3G4", "test"},            # used by f5_holding.py (daily Sharpe)
      "SR80_exact_root": {...}, "power_at_SR80_by_p7_power": {...}, "bars": {...},
      "cross_check": {..., "checks": {...}, "pass": true} } # f5_holding.py refuses unless pass is true

### F3_vol.json (VolCoder; read fields only)

`roots.<CODE>`: `tick_size`, `L_main`, `main_session_pt` ["HH:MM", "HH:MM"] (PT), `h."<h>".{sigma, m, n}` for
h in 1, 2, 5, 15, 30, 60, 120, 240, `OC.{sigma, m, n}`, `overnight.cc.{sigma, m, n}`, `overnight.on.{sigma, m, n}`,
`status`, and `oc1_source`. The statistics are in ticks of the code's own tick. A null sigma is unknown.

### F4_facts_unmasked.json (FactTable; read fields only)

A fact may be a bare value or `{"value": ..., <source fields>}`. `{"unknown": true}` or a null value means unknown.
- `codes.<CODE>`: `tick_size` (must equal F3's), `tick_value_usd` (v, required, > 0), and `spread_S` as
  `{"value", "sourced", "item"}`. S is used only when `sourced` is true and `value` is not null. Otherwise
  S = 1 (u). The block also gives `pauses` (list; an item with `start_pt` and `end_pt` "HH:MM" PT gets a relation
  to the main session: inside, adjacent or outside; other items pass through as given), `main_session_pt`
  (reported beside F3's), and `excluded` (a survivor marked excluded is refused).
- `firms.<firm>`: `dll_50k` (USD, "none" = no daily limit, so DLL_f = MLL_f; null = unknown), `mll_50k` (USD),
  `mll_type`, `flat_by_close`, `overnight` (object; `allowed` true or false is read, the rest passes through), and
  `news_windows` (passes through).
  `flat_by_close` forms: "13:10 PT", "15:10 CT", "4:10 PM ET", `{"time": "15:10", "tz": "CT"}`, `{"pt": "13:10"}`,
  any of these under `{"value": ...}`, "none", `false` or `{"none": true}` (no rule), or null / `{"unknown": true}`
  (unknown). A time without a zone is refused. Zones: PT, MT, CT and ET (with S/D variants) and the matching IANA
  names. The conversion uses fixed offsets from PT, because US zones change DST together.
- `pairs."<firm>|<CODE>"`: `listed_50k` (must be true), `fee_rt_usd` (F_rt,f, required, >= 0), `fee_kind`
  ("stated" or "RR-05 (u)"), and `news_window_items` (passes through).

### Selection (`--selection`): either form

1. Minimal `F5_selection.json`, written by the lead from the score output:

       { "spec_sha256": "09eb...8635", "source": "<score output path>", "generated_pdt": "...",
         "layer1_survivors": ["CODE", ...],
         "top15": [ {"rank": 1, "firm": "<firm>", "code": "<CODE>"}, ... ] }

2. ScoreCoder's score output itself. The top-level `spec_sha256` and `primary.f5_handoff.layer1_survivors`
   (`[{"code", ...}]`) and `primary.f5_handoff.top15` (`[{"rank", "firm", "code", ...}]`) are read.

Rules, each refused when broken:
- the survivors are distinct, exist in F3 roots and F4 codes, are not NQ, and have a known sigma_60;
- top15 holds at most 15 entries, ranked 1..n in order, with no duplicate pair;
- every top-15 code is a survivor, and every pair exists in F4 pairs and its firm in F4 firms.

## Output: F5_holding.json (default reports/stage_e32b_briefs/F5_holding.json) and F5_holding.md

    { "spec_sha256", "generated_pdt", "generated_by",
      "inputs": {"f3"|"f4"|"sr80"|"selection": {"path", "sha256"}, "selection_form"},
      "SR80": {"disc_G3", "disc_G3G4", "test"},
      "constants": {"slippage_rt_ticks": 0.5, "S_unknown": 1, "entry_cap": 20, "days_per_year": 252,
                    "normal_factor": 1.596, "band_candidates": ["5","15","30","60","120","240","OC"],
                    "band_G_factor": 1.10, "band_dll_min": 2, "rel_tol": 1e-12},
      "survivors": { "<CODE>": {
          "code", "status", "oc1_source", "tick_size", "tick_value_usd", "S", "S_unknown", "c_RT",
          "cost_basis": "c_RT", "L_main", "main_session_pt", "main_session_pt_F4",
          "pauses": [{"pause", "relation_to_main_session"}],
          "rows": {"1"|"2"|"5"|"15"|"30"|"60"|"120"|"240"|"OC": ROW},
          "overnight_rows": {"cc"|"on": ROW},
          "G_min", "G_argmin": [...], "u": [...] } },
      "pairs": { "<firm>|<CODE>": {
          "rank", "firm", "code", "tick_value_usd", "fee_rt_usd", "fee_kind", "fee_ticks", "S", "S_unknown",
          "c_RT", "c_f", "cost_basis": "c_f", "DLL_f", "dll_source", "MLL_f", "mll_type",
          "flat_by_close": {"raw", "status": "time|none|unknown", "pt": "HH:MM"|null},
          "main_session_pt", "flat_minus_main_end_min", "overnight", "overnight_allowed",
          "news_windows", "news_window_items", "pauses",
          "rows": {...: ROW + PROP}, "overnight_rows": {"cc"|"on": ROW + PROP + {"overnight_allowed"}},
          "G_min", "G_argmin",
          "band": {"members", "shortest", "longest", "contiguous", "excluded": {"<h>": [reasons]},
                   "unknown_conditions": {"<h>": [...]}, "k_step_ratios": {"1->2": r, ...},
                   "power_term_exceeds_cost_from": "<h>"|null},
          "verdict": {"value": "holds|partly|fails", "reason"}, "u": [...] } } }

ROW (one horizon; c = the row set's cost basis, c_RT for survivors and c_f for pairs; null when unknown):

    sigma, m, n_pairs                      F3 sigma_h, m_h = mean |D_h|, count
    k_RT = c_RT / sigma_h, k = c / sigma_h  the cost-per-sigma curve
    g_be = c, g_1 = c + 1                  gross edge per trade to break even / to net 1 tick
    p_be_emp, p_1_emp = 0.5 + g / (2 m_h); p_be_norm, p_1_norm = 0.5 + g / (1.596 sigma_h)  (values > 1 kept)
    n_max = floor(L_main / h) (OC, cc, on: 1), n_cap = min(20, n_max), trades_per_year = 252 n_cap
    e80_<k> = SR80_<k> sigma_h / sqrt(n_cap), gross_detect_<k> = c + e80_<k>, for k in disc_G3, disc_G3G4, test
    G_cost_term = c / sigma_h, G_power_term = SR80_test / sqrt(n_cap), G = their sum
    (pairs, rows 1..OC only) G_over_min = G / G_min, in_band

PROP (pairs): `dll_ratio` = DLL_f / (sigma_h v), `mll_ratio` = MLL_f / (sigma_h v), `latest_start_pt`
(the latest start of an h-minute hold that ends by min(main-session end, flat-by-close); for OC, the main-session
start), and `fits_flat_by_close` (true, false, or null for unknown).

## Own-broker venue (optional `--venue-file`, added 2026-10-29 by F5Runner; f5_venue.py)

Input (briefs/F4_venue_ibkr.json, read fields): `spec_sha256` (frozen hash, else refused); `dll`, `mll`,
`flat_by_close` (must be null: LR-F5-IBKR's band assumes none; a stated value is refused); `capital_ceiling_usd`
(null -> USD 6,000 (u)); `overnight_holds_allowed`; `overnight_position_fee` (passed through, not applied);
`codes.<CODE>`: `fee_per_side_usd` (F_rt = 2 x this; null -> not computed), `fee_rt_usd` (if present must equal
2 x per side, else refused), `fee_status`, `margin_intraday_initial_usd`, `margin_overnight_initial_usd`,
`margin_overnight_maintenance_usd` (null -> u). Tick size, tick value and S come from F3 and F4 as for the pairs.

Output: `inputs.venue {path, sha256}` and

    "own_broker": { "venue", "venue_key": "ibkr", "source", "fee_rule_file", "rulings": {"LR-F5-IBKR", "LR-Q6d"},
      "capital_ceiling_usd", "capital_ceiling_u", "overnight_allowed", "limits_note",
      "not_computed": {"<CODE>": reason},
      "rows": { "ibkr|<CODE>": {
          "venue", "code", "tick_value_usd", "fee_per_side_usd", "fee_rt_usd", "fee_rule", "fee_status",
          "fee_rt_usd_stated", "fee_ticks", "S", "S_unknown", "c_RT", "c_f", "cost_basis": "c_f",
          "DLL_f": null, "MLL_f": null, "flat_by_close": "none (own account)", "limits", "main_session_pt",
          "overnight_allowed", "overnight_position_fee", "margin_intraday_initial_usd",
          "margin_overnight_initial_usd", "margin_overnight_maintenance_usd",
          "rows": {"1".."240"|"OC": ROW + {"latest_start_pt", "fits_main_session", "G_over_min", "in_band"}},
          "overnight_rows": {"cc"|"on": ROW + {"overnight_allowed", "margin_overnight_initial_usd",
                                               "margin_overnight_maintenance_usd"}},
          "G_min", "G_argmin", "band": {"members", "shortest", "longest", "contiguous", "excluded", "rule",
                                         "k_step_ratios", "power_term_exceeds_cost_from"},
          "verdict": {"value", "reason"},
          "Q6_inputs": {"capital_ceiling_usd", "capital_ceiling_u", "margin_intraday_initial_usd",
                        "margin_overnight_initial_usd", "margin_intraday_exceeds_ceiling",
                        "margin_overnight_exceeds_ceiling", "sigma_day_basis", "sigma_cc_ticks", "sigma_day_usd",
                        "sigma_day_limit_usd", "sigma_day_limit_rule", "sigma_day_exceeds_limit", "sigma_OC_ticks",
                        "sigma_OC_usd"},
          "u": [...] } } }

"exceeds" is strict (>), as spec 8.3 writes it; null when the input is unknown. Q6 itself is not scored here.
A band member whose hold does not fit inside the main session is kept (the ruling's band is G only) and flagged in u.
