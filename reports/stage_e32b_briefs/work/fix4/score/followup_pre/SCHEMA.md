# Stage E.32b scoring inputs and outputs (score32b.py, r3_score.py)

ScoreCoder, 2026-10-28. Extends the shared data contract in briefs/brief_wave_b.md: field names there are unchanged;
fields marked **added** are new. Spec = reports/stage_e32b_ranking_spec.md, sha256 09ebe697...cf1a4eb58635; both
scripts refuse to run on any other hash, and refuse an input whose own `spec_sha256` differs. "(u)" = the spec's
unknown rule for that criterion; "lead" = a case the spec does not settle, applied as stated and listed in the output's
`for_lead`.

Numbers may be JSON numbers or decimal strings; the scripts compute with exact fractions of their decimal text, so a
value on a band boundary lands on it exactly (boundaries to the higher score).

## 1. F3_vol.json (VolCoder): `roots.<CODE>`

| field | used for | unknown rule |
|---|---|---|
| status `owned` / `OC1` / `unknown` | which statistics exist; OC1_off treats `OC1` as unknown | `unknown` or absent: every statistic unknown |
| h.`30` `60` `120` `240`.sigma | D1 r_h (3 D1), gate (3 gate), D uses h.240 (4 D) | sigma_60 unknown: gate fails; another D1 horizon unknown: gate fails (lead) |
| h.`5` `15`.sigma, OC.sigma | r_5, r_15, r_OC reported; D1_all variant | as above under D1_all |
| h.*.m, OC.m | variant mad (m_h in D1 and the gate) | as sigma |
| R_d.p99 (ticks) | D4 J (x tick_value_usd > USD 1,000) | J = 1 (u) |
| R_d.median (ticks) | D room_b = MLL / (R_d v) | band 1 (u) |
| median_close (price units) | D2 c and D4 Sat (i) notional = ADV x multiplier x close | a code without one borrows a same-price sibling's close (spec 2.4 groups, `SAME_PRICE_GROUPS`); else notional unknown (lead) |
| tick_size | cross-checked against F4 (soft check) | - |

NQ must be present (it is MNQ's transfer source and enters the equity notional comparison).

## 2. F4_facts_unmasked.json (FactTable)

`codes.<CODE>`: every one of the 47 spec codes (the run refuses a missing code unless `--allow-partial-universe`,
which is for synthetic fixtures only). `family` must equal spec section 0's; `excluded` is true for NQ only.

| field | used for | unknown rule |
|---|---|---|
| tick_value_usd, multiplier, tick_size | J, D (v), notional; multiplier x tick_size = tick_value_usd checked (soft) | v unknown: J = 1, D bands 1 |
| adv.value (contracts) | D4 L, D2 c, Sat (i), leader | L = 1 (u) (a sourced spread or touch can still make it 2); notional unknown |
| spread_S.value, **spread_S.sourced** (bool) | S in c_RT = S + 0.5 (D1, gate) and L's spread test | not sourced: S = 1 (u) for c_RT; L ignores it |
| touch.value, **touch.sourced** | L's touch test | not sourced: ignored |
| siblings [codes], leader | Sat (i), the leader (D2 a b c and D6 of a satellite) | leader computed from notional ADV; F4's `leader` used when not computable (lead); a mismatch uses the computed one (lead) |
| settles_off_sibling.value, .sibling, .item | Sat (ii) | value true without `item` (no source): does not count (u) |
| data_access.mbo_start (`YYYY-MM-DD` or `YYYY-MM`) | D5 h | 1 (u) |
| data_access.k_usd_month, k_kind | D5 k | null or kind `unknown`: 1 (u) |
| data_access.o_owned_36m (bool) | D5 o | null: 1 (u, the spec's else branch) |
| data_access.p_all_read (bool) | D5 p | null: 0 (u) |
| underlying, main_session_pt, pauses, listing | not scored here (F5, reports) | - |

`firms.<firm>` (topstep, lucid, tradeify, mffu, bulenox):

| field | used for | unknown rule |
|---|---|---|
| dll_50k: number, or **"none"** when the firm has no daily loss limit | D room_a = DLL_f / (sigma_240 v); "none": the MLL | null: band 1 (lead) |
| mll_50k | D room_b | null: band 1 (lead) |
| bc_accepts (bool) | Layer 2 gate | null: excluded (lead) |
| p_inputs.native_api (bool) | P | null: deduction (u) |
| p_inputs.oco_api (bool) | P | null: deduction (u) |
| p_inputs.vps_chicago: **"allowed" / "prohibited" / "unknown"** (or true / false) | P | not "allowed": deduction |
| p_inputs.api_rate_limit_per_s: number, or **"no_limit"** (documented absence) | P: < 10 deducts; exactly 10 does not | null or "unknown": deduction (u) |

`pairs.<firm>|<CODE>`: listed_50k (bool; false: gate; null: excluded, lead), fee_rt_usd and fee_kind (reported; the fee
enters through econ32b.json).

## 3. F4_blind_unmasked.json (BlindScorer, unmasked by the lead)

Each rating R = {"value", "unknown", "reason"} plus optional **"unverified": true** when the rating rests only on an
abstract or a snippet (spec 1): the script then caps D6 (at most 2 from above, at least 1 from below) and D3 s1, s2
(2 becomes 1). A missing R, `unknown: true` or `value: null` takes the rule below; a value outside the scale is refused.

| key | scale | unknown rule |
|---|---|---|
| codes.D2a | 0, 1 | 1 |
| codes.D2b | 0, 0.5, 1 | 0.5 |
| codes.s1, s2 / s3 | 0-2 / 0-1 | 0 (unsourced items score 0) |
| codes.sat_iii | 0, 1 | 0 |
| codes.D6 | 0-4 | 1 |
| pairs.R | 1-4 | 1 |
| pairs.A | 0-4 (0 = gate) | 1 |
| firms.rel_age, rel_payout, rel_rules / rel_regulatory | deduction 0-1 / 0 or 2 | 0, no deduction (lead; E.28 score.py did the same) |

Ratings are needed for NQ and for every leader of a satellite even where the leader is not scored: a satellite's
D2 a, b and D6 are its leader's (MNQ takes NQ's).

## 4. econ32b.json (EconCoder): `pairs.<firm>|<CODE>.<block>`

Blocks `primary` (E), `E_dir60` (variant E_dir60), `spread1` (variant spread1); each {mu_star_mkt, mu10K_mkt,
above_cap {mu_star, mu10K}, cost_per_attempt, sigma60, m_star, m10K, grid_cap}. Required for every pair with
listed_50k = true whose code has F3 status owned or OC1 (NQ apart), because a variant can make such a code survive;
the run refuses otherwise. E = 0.75 s(m_star; 0.20) + 0.25 s(m10K; 0.30); `above_cap` true scores that component 0
and counts m* as infinite in the tie chain; m_star null without above_cap is refused. sigma60 is cross-checked
against F3 (soft). cost_per_attempt: lower wins the third tie level (any consistent unit).

## 5. F2_attention.json (AttentionCounter) and F2_data_access.json (DataAccess)

F2_attention: `underlyings.<name>` {codes [..], status, count}. A count is used only when status is 200 (or "200",
"ok") and count is a non-negative integer. Terciles among underlyings with a count: k = the number with a strictly
larger count, n = the number with a count; top (d = 1) if k < n/3, middle (0.5) if k < 2n/3, else bottom (0). Equal
counts share k, so they take the higher tier (as written). No count, or a code under no underlying: d = 0.5 (u). A
code under two underlyings is refused.

F2_data_access (optional `--data-access`): `codes.<CODE>` mbo_start, k_usd_month, o_owned_36m, p_all_read are
compared with F4's data_access block (soft check); D5 is scored from F4.

## 6. Lead-ruling variants (`--rulings`, the spec 5 hook)

    {"rulings": [{"name": "RL-01", "ruling": "<id or text>", "description": "...",
                  "params": {"slip": "0.5", "dispersion": "sigma|mad", "d1_all": false, "e_dir60": false,
                             "oc1_off": false, "sat_deduction": 2, "d2_own": false, "l1min2": false,
                             "spread1": false},
                  "patches": [{"file": "F3|F4|blind|econ|attention|data_access", "path": ["codes", "SI", "..."],
                               "value": <any>, "source": "..."}]}]}

Each ruling runs on a patched copy of the inputs (the primary is never changed), is validated like the primary, and
is reported with its top 5, MNQ ranks and `top5_same_as_primary` (the lead keeps those that change the top 5).
Names may not repeat a declared variant.

## 7. Combinations file (r3_score.py, spec 8.3)

    {"spec_sha256": "<frozen hash, optional>",
     "sr80_test": {"value": <SR80 at the test, T = 870>, "source": "briefs/work/F5/SR80.json <key>"},
     "own_account_capital_ceiling_usd": {"value": null | number, "source": "docs/DECISIONS.md ..."},
     "rho_measured": {"<CODE>|<CODE>": {"value": rho, "source": "E.29 section 3.2 ..."}},
     "combinations": [{
        "id": "C01", "product": "<CODE>" | null, "pool": null | {"name": "<pool>", "members": ["<CODE>", ...]},
        "venue": "topstep|lucid|tradeify|mffu|bulenox|ibkr", "family": "<idea family>",
        "band": ["5","15","30","60","120","240","OC" subset], "h_c": "<member of band>",
        "Q1": R, "Q2": R, "Q3": R,              (CombinationScorer, R as in section 3; required, 0-4)
        "members": [{                           (one per product; one per pool member)
           "code", "asset_class" (default: the code's E.28 family),
           "c_f_ticks", "sigma_hc_ticks", "tick_value_usd", "K_test" (trades in the 43-month test), "L_main",
           "n_per_day" (trades a day, for the payout test),
           "dll_usd" (number or "none"), "mll_usd", "payout_threshold_usd" (daily payout qualification),
           "news_stop_events_per_week" (scheduled events a week around which the firm's news windows stop the family),
           "gate": {"news_window_covers_event_trade", "overnight_needed_but_prohibited", "holds_past_flat_by_close"},
           "initial_margin_usd", "sigma_day_ticks"          (own-broker venue only)}],
        "data": {"discovery_cost_usd" (0 if owned), "all_data_cost_usd", "clean_test_window_months", "windows"}}]}

Required: sr80_test.value, Q1-Q3, and per member c_f_ticks, sigma_hc_ticks, tick_value_usd, K_test (L_main unless
h_c = OC); refused otherwise. Q4 = band of x = c_f / sigma_hc (a pool: its worst member, lead). Q5 = band of
q = SR80_test sqrt(870 / K), K = K_test, or for a pool K_eff = sum K_test / (1 + (m - 1) rho) with rho the mean
pairwise rho (measured, else 0.5 within an asset class, 0.3 across). Q6 at a prop venue: 4 - (2 if DLL_f / (sigma_hc v)
< 1.5, else 1 if < 3) - (1 if payout threshold > sqrt(n_per_day) sigma_hc v) - (1 if news events >= 2), floor 0;
own-broker: 4 - (2 if margin > ceiling) - (1 if sigma_day v > 2% of ceiling), ceiling USD 6,000 (u) when null; a
pool takes its worst member's Q6. Q7 = 4 - (1 if discovery > USD 50) - (1 if all data > USD 200) - (1 if the clean
test window < 36 months, 2 if < 24), floor 0. Unknown Q6 or Q7 inputs deduct (lead). Gates (excluded, listed): Q3 = 0,
or any member gate flag true (a pool is excluded if any member is, lead).

## 8. Outputs

score32b.py `--out`: {spec_sha256, generated_pdt, inputs {name: {path, sha256}}, input_checks [soft findings],
for_lead [{note, where}], primary {layer1 {CODE: row}, pairs [ranked first, then the rest], ties, top15, n_ranked,
layer1_survivors, L1_below_2, MNQ_ranks, params, f5_handoff {layer1_survivors [{code, family, f3_status}], top15}},
moves_vs_e28 {rows [{firm, code, rank_e28, status_e28, rank_here, status_here, rank_change, S_e28, S_here, contrib,
moved_by}]}, variants {name: {kind, params_changed, top5, top5_same_as_primary, MNQ_ranks, n_ranked,
layer1_survivors}}}. Layer 1 row: S, c_RT, disp, r (all horizons), D1_bands, D1..D6 with *_parts, L1, L1_below_2,
gate_pass, gate_reasons, gate_arithmetic ("sigma_60 = x ticks vs 2 x (S + 0.5) = y ticks"), u, lead. Pair row: E R A D
Rel P, L2, S, S_rounded, m_star, cost_per_attempt, room_a, room_b, deductions, status (ranked, Layer 1 gate, Layer 2
gate, excluded (V49)), gate_reasons, rank. `--md` writes the same as tables. Fractions are written as floats; an
infinite m* as "inf".

r3_score.py `--out`: {combinations [eligible ranked first, then excluded], ties, R4 {candidates [{rank,
product_or_pool, family, id, best_venue, band, h_c, C, C_rounded, weak}], n_reaching_2, fewer_than_3_reach_2},
R4_prop_only (same, prop venues only), best_own_broker, capital_ceiling_usd, capital_ceiling_u, for_lead}.
