"""Stage E ML route (docs/STAGE_E_ML_DESIGN.md, frozen by E.2a; built in E.2b Task 2).

Public interfaces (details in each module's docstring):

- Job entry (E.ML-train), ``ml_route.train``:
    python -m ml_route.train fit --challenger {lgbm,lstm} --horizon {h30,h120,hF}
        --store-root <step 2 store root> --out-dir <dir> --harness-sha256 <sha256>
    python -m ml_route.train finalize --out-dir <dir> --harness-sha256 <sha256>
  Both call screening.harness_freeze.preflight(expected) first and write its return value into
  every ledger record, candidates file and the route manifest.
- Store reader, ``ml_route.store``: ``read_product_bars(store_root, root, s_x)`` and
  ``assert_store_root(store_root)`` (path allowlist; data/processed refused; rows dated on or
  after 2024-03-01 refused; the S_X cut asserted).
- Rule wrapper, ``ml_route.rule_wrapper``: ``rule_spec_from_json`` and
  ``DistilledRuleStrategy`` (a strategy.interface.Strategy; ``observe_lead`` for F16's lead).

Modules: constants (frozen values), inputs (frozen tables, sessions; S_X and the release
calendar refuse until wired), blocks (M7.3), features/rows/dataset (M4, M7.1), selection
(ML-A01), lgbm/lstm/lstm_data/adapters (M3), ledger (M7.6), surrogate (M5), manifest, probes (M8),
synthetic (tests and probes only).
"""
