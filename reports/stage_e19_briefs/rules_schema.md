# Stage E.19 rules JSON schema (lead, binding for Task 1 and Task 2)

Task 1 writes reports/stage_e19_rules.json in exactly this structure. Task 2's loader (prop_econ/rules.py) reads it and
nothing else for rule values. A provisional file in the same structure, built from the E.0 / E.12 facts (2026-09-16 to
2026-10-03, NOT re-verified), is reports/stage_e19_briefs/rules_provisional.json: development and tests only, never
for results.

## Top level

```
{
  "schema_version": "e19-rules-1",
  "generated_pdt": "2026-10-10T17:30:00-07:00",
  "status": "FINAL" | "PROVISIONAL",
  "sources": { "S01": {"url": str, "title": str, "fetched_utc": str, "fetched_pdt": str,
                       "file": str (repo path of the raw saved page), "sha256": str,
                       "page_updated": str | null, "method": "curl" | "WebFetch" | "scrapling get" | ...}, ... },
  "terms_check": {"robots_txt": str, "automated_access_clause": str (verbatim or "none found"),
                  "source": "Sxx" | null, "decision": str},
  "global": { ... see below ... },
  "sizes": {"50K": SIZE, "100K": SIZE, "150K": SIZE},
  "rules": [RULE, ...],
  "prohibited": [PRACTICE, ...]
}
```

## global

```
"global": {
  "max_active_xfas": int,                 # 5
  "profit_split_trader": float,           # 0.9 = 90% to the trader
  "billing_period_calendar_days": int,    # Combine rebill period (30)
  "rebill_adds_reset_credit": bool,
  "reset_pushes_rebill": bool,
  "resets_per_day": int | null,
  "combine_time_limit_days": int | null,  # null = no time limit
  "payout_min_request_usd": float,        # 125
  "payout_day_counts_toward_next_window": bool,  # false per E.0
  "xfa_inactivity_close_days": int | null,
  "callup": {"type": "none" | "after_n_payouts" | "payout_total_usd" | "discretionary",
             "n": int | null, "usd": float | null,
             "closes_all_xfas": bool | null, "xfa_balance_on_callup": str},
  "dll_doubles_payout_caps": bool         # the DLL "double per-request payout caps" offer, if still live
}
```

## SIZE

```
{
  "combine": {
    "monthly_price_usd": {"standard": float, "no_activation_fee": float},
    "reset_price_usd":   {"standard": float, "no_activation_fee": float},
    "dll_discount_monthly_usd": {"standard": float | null, "no_activation_fee": float | null},
    "profit_target_usd": float,
    "mll_usd": float,
    "mll_trail": "eod" | "intraday",
    "mll_floor_max_rel_usd": float,     # highest the floor can trail to, relative to the start balance (0 = locks at start)
    "dll_usd": float | null,            # Combine daily loss limit, null if none
    "consistency": {"type": "best_day_max_frac_of_profit" | "best_day_max_frac_of_target" | "none",
                    "frac": float | null},
    "min_trading_days": int,
    "max_minis": int
  },
  "activation_fee_usd": {"standard": float, "no_activation_fee": float},
  "xfa": {
    "start_balance_usd": float,         # 0
    "mll_usd": float,
    "mll_trail": "eod" | "intraday",
    "mll_floor_lock_usd": float,        # floor stops trailing at this balance (0)
    "mll_after_first_payout_usd": float | null,  # floor set to this balance after the first payout (0); null = unchanged
    "dll_option_usd": float | null,
    "scaling": [{"below_usd": float | null, "max_minis": int}, ...],   # ascending; last has below_usd null
    "scaling_boundary": "lower" | "upper",   # a balance exactly on a boundary takes the lower or the upper tier
    "payout": {
      "standard":    {"winning_day_usd": float, "winning_days": int, "frac_of_balance": float,
                      "cap_usd": float, "cap_usd_dll": float | null, "net_positive_since_last": bool},
      "consistency": {"traded_days": int, "best_day_max_frac": float, "frac_of_balance": float,
                      "cap_usd": float, "cap_usd_dll": float | null, "net_positive_since_last": bool}
    },
    "payout_count_limit": int | null,
    "back2funded": {"price_usd": float, "dll_discount_usd": float | null, "max_per_xfa": int,
                    "before_first_payout_only": bool, "window_calendar_days": int}
  }
}
```

## RULE (one per structured leaf value, keyed by its dotted path)

```
{"id": "R001", "path": "sizes.50K.combine.profit_target_usd", "value": 3000,
 "status": "SOURCED" | "UNSOURCED" | "CONFLICT" | "INFERRED",
 "readings": [3000] | [primary, alternative, ...],   # first = the value in the structured part
 "source": "S03" | null, "quote": "verbatim text" | null, "note": str}
```

- SOURCED: a verbatim quote from a saved page states it. INFERRED: follows from quoted text by arithmetic or a
  stated equivalence (the note says how). UNSOURCED: no page states it; `readings` lists every plausible reading,
  the conservative one first. CONFLICT: two pages disagree; both quotes in `note`, the stricter reading first.
- Every leaf of `global` and `sizes` has exactly one RULE whose `path` points to it (paths into lists use the index:
  `sizes.150K.xfa.scaling.2.max_minis`).
- If Topstep publishes a rule this schema has no field for (for example a payout-path choice deadline, a minimum
  balance for payouts, a per-day profit cap), add it under `global` or the size block with a clear name, give it a
  RULE, and list it in the md's "Fields added" section; the lead decides whether the simulator models it.

## PRACTICE (prohibited or restricted trading practices)

```
{"id": "P01", "practice": "Account stacking", "quote": "verbatim", "source": "S07",
 "applies_to": ["combine", "xfa", "lfa"], "bot_implication": "one sentence: what a bot must or must not do"}
```
