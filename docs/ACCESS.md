# Access notes

## TopstepX / ProjectX

Not accessed. No credential exists for this project, and none was created, stubbed or referenced in Stage A.1. This section is reserved for Stage A.2.

## Databento (GLBX.MDP3) — Stage A.1, 2026-09-16

- **Credential.** The key is read from `DATABENTO_API_KEY` in this repo's git-ignored `.env`, through `data/config.py::require_databento_key`. It is the same account key as MLCryptoEngine's `MLCE_DATABENTO_API_KEY`; the match was confirmed by comparing SHA-256 prefixes, and the value was never printed. No key value appears in any source file.
- **Spend gate.** Every billable request was priced first with `metadata.get_cost` and `metadata.get_billable_size`, then checked against both caps, then committed to `ledger/databento_spend.jsonl` before download. The code is `data/spend_gate.py` and `data/adapter.py`.
  - Session cap: $15.00.
  - Shared account cap: $120.00, counting MLCryptoEngine's `data/vendor/spend_ledger.jsonl`, which is read and never written.
- **Refusals this session: none.** Everything planned fit inside both caps, so there is no stopped request to document. If the gate ever refuses, `SpendGate.authorize` appends an itemized note (quoted cost, exact request parameters, reason) at the end of this file, directly below this section.
- **Free metadata calls.** These are not billable and were not priced or ledgered: `metadata.get_dataset_range`, `metadata.get_dataset_condition` (cached under `data/vendor/databento/condition/`), `symbology.resolve`, and the cost/billable-size quote endpoints themselves (whose quotes *are* ledgered).
