# Stage E.33 run marker (run-once; C1)

The E.33 ZM discovery search is registered and runs once on the discovery data. A second search run under E33 is not
allowed: the registry refuses a second registration under E33, and every restart resumes from the DONE markers and
re-checks the one registration with trial_registry.require_registered (protocol P7.1).

- Registration: ledger/trial_registrations.jsonl entry r009-E33, test E33, 300 ids, N 538 -> 838, at
  2026-10-28T14:23:13-07:00 (Stage E.33b lead, session b8cfc9d8-3e96-415a-a441-462542346e80).
- Configuration freeze: reports/stage_e33_c1_freeze.json, sha256
  ea002c609f8470becc430cb76380d9603b336a08c00196fd814621bb48dc9a6e (300 configurations: 60 per set S1-S5, 50 per
  label, 180 LOGIT and 120 LGBM).
- Pipeline freeze: reports/stage_e33_pipeline_freeze.sha256, sha256
  eb565a37f814953d0f86dd99e15a34c3bd19c7f0f670a8e7e1a44853a085173e (227 files; verify --remeasure 0 differences;
  check-proofs 0 differences), with reports/stage_e33_pipeline_inputs.sha256 (4,125 derived inputs, 60.8 GiB).
- Protocol: reports/stage_e32_discovery_protocol.md, sha256
  c4ffb9d79af4bbbf10574ac138668aa49a80b22a8f5fba5879184d357d2c7e05.
- Readings: reports/stage_e33_protocol_readings.md (FINAL), sha256
  da58c77f1edc4b1615d37a3e56d851205ab1efe4128e6faf4ddea063ed00fd80.
- Harness: v14, sha256 2e908c81e01d0aad835b30ab7b95f628182666dd8d76301cdd4ea465bb41edd1 (preflight confirmed by
  the register call).
- Evidence behind the freeze GO: reports/stage_e33_freeze_evidence.sha256 (124 files, PipelineReview N18).
- P5 projection (reference for P10's 3x stop): 2,255.8 s; written to reports/stage_e33_STATE.md before the first
  real-outcome fit.
- Stores: features derived/e33/features/2b30cb0e953b (816 dates); labels derived/e33/labels/b15c4ca10d68 (the
  frozen label code; built after this registration for the dates not yet built).
