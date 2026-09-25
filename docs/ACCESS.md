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

### Databento request refused by spend gate — 2026-09-25T03:59:11.776918+00:00

- session: `stage-E.1-2026-09-24`
- Databento account: `acct-2`
- quoted cost (USD): nan
- request parameters: `{"dataset": "GLBX.MDP3", "symbols": ["ZL.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2025-08-01", "end": "2025-09-01"}`
- session spent before: $54.1499 (cap $113.48)
- account acct-2 spent before: $54.1499 (cap $125.00)
- reason stopped: unpriceable request (quote=None): never assumed cheap

### Databento request refused by spend gate — 2026-09-25T04:12:39.420164+00:00

- session: `stage-E.1-2026-09-24`
- Databento account: `acct-2`
- quoted cost (USD): nan
- request parameters: `{"dataset": "GLBX.MDP3", "symbols": ["LE.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2026-01-01", "end": "2026-02-01"}`
- session spent before: $55.4138 (cap $113.48)
- account acct-2 spent before: $55.4138 (cap $125.00)
- reason stopped: unpriceable request (quote=None): never assumed cheap

### Databento request refused by spend gate — 2026-09-25T04:14:06.064485+00:00

- session: `stage-E.1-2026-09-24`
- Databento account: `acct-2`
- quoted cost (USD): nan
- request parameters: `{"dataset": "GLBX.MDP3", "symbols": ["LE.v.0"], "schema": "ohlcv-1m", "stype_in": "continuous", "start": "2026-02-01", "end": "2026-03-01"}`
- session spent before: $55.4539 (cap $113.48)
- account acct-2 spent before: $55.4539 (cap $125.00)
- reason stopped: unpriceable request (quote=None): never assumed cheap

### Databento request refused by spend gate — 2026-09-25T04:38:23.030063+00:00

- session: `stage-E.1-2026-09-24`
- Databento account: `acct-2`
- quoted cost (USD): nan
- request parameters: `{"dataset": "GLBX.MDP3", "symbols": ["NQ.v.0"], "schema": "mbp-1", "stype_in": "continuous", "start": "2026-02-10T23:00:00Z", "end": "2026-02-11T22:00:00Z"}`
- session spent before: $74.0412 (cap $113.48)
- account acct-2 spent before: $74.0412 (cap $125.00)
- reason stopped: unpriceable request (quote=None): never assumed cheap

### Databento request refused by spend gate — 2026-09-25T04:39:22.859845+00:00

- session: `stage-E.1-2026-09-24`
- Databento account: `acct-2`
- quoted cost (USD): nan
- request parameters: `{"dataset": "GLBX.MDP3", "symbols": ["NQ.v.0"], "schema": "mbp-1", "stype_in": "continuous", "start": "2026-02-10T23:00:00Z", "end": "2026-02-11T22:00:00Z"}`
- session spent before: $74.0412 (cap $113.48)
- account acct-2 spent before: $74.0412 (cap $125.00)
- reason stopped: unpriceable request (quote=None): never assumed cheap

### Databento request refused by spend gate — 2026-09-25T04:39:56.597764+00:00

- session: `stage-E.1-2026-09-24`
- Databento account: `acct-2`
- quoted cost (USD): nan
- request parameters: `{"dataset": "GLBX.MDP3", "symbols": ["NQ.v.0"], "schema": "mbp-1", "stype_in": "continuous", "start": "2026-02-10T23:00:00Z", "end": "2026-02-11T22:00:00Z"}`
- session spent before: $74.0412 (cap $113.48)
- account acct-2 spent before: $74.0412 (cap $125.00)
- reason stopped: unpriceable request (quote=None): never assumed cheap

### Databento request refused by spend gate — 2026-09-25T04:40:27.268632+00:00

- session: `stage-E.1-2026-09-24`
- Databento account: `acct-2`
- quoted cost (USD): nan
- request parameters: `{"dataset": "GLBX.MDP3", "symbols": ["NQ.v.0"], "schema": "mbp-1", "stype_in": "continuous", "start": "2026-02-10T23:00:00Z", "end": "2026-02-11T22:00:00Z"}`
- session spent before: $74.0412 (cap $113.48)
- account acct-2 spent before: $74.0412 (cap $125.00)
- reason stopped: unpriceable request (quote=None): never assumed cheap

### Databento request refused by spend gate — 2026-09-25T04:47:18.529388+00:00

- session: `stage-E.1-2026-09-24`
- Databento account: `acct-2`
- quoted cost (USD): nan
- request parameters: `{"dataset": "GLBX.MDP3", "symbols": ["RTY.v.0"], "schema": "mbp-1", "stype_in": "continuous", "start": "2025-05-13T22:00:00Z", "end": "2025-05-14T21:00:00Z"}`
- session spent before: $76.6283 (cap $113.48)
- account acct-2 spent before: $76.6283 (cap $125.00)
- reason stopped: unpriceable request (quote=None): never assumed cheap

### Databento request refused by spend gate — 2026-09-25T04:47:53.179787+00:00

- session: `stage-E.1-2026-09-24`
- Databento account: `acct-2`
- quoted cost (USD): nan
- request parameters: `{"dataset": "GLBX.MDP3", "symbols": ["RTY.v.0"], "schema": "mbp-1", "stype_in": "continuous", "start": "2025-05-13T22:00:00Z", "end": "2025-05-14T21:00:00Z"}`
- session spent before: $76.6283 (cap $113.48)
- account acct-2 spent before: $76.6283 (cap $125.00)
- reason stopped: unpriceable request (quote=None): never assumed cheap

### Databento request refused by spend gate — 2026-09-25T04:48:19.248012+00:00

- session: `stage-E.1-2026-09-24`
- Databento account: `acct-2`
- quoted cost (USD): nan
- request parameters: `{"dataset": "GLBX.MDP3", "symbols": ["RTY.v.0"], "schema": "mbp-1", "stype_in": "continuous", "start": "2025-05-13T22:00:00Z", "end": "2025-05-14T21:00:00Z"}`
- session spent before: $76.6283 (cap $113.48)
- account acct-2 spent before: $76.6283 (cap $125.00)
- reason stopped: unpriceable request (quote=None): never assumed cheap

### Databento request refused by spend gate — 2026-09-25T04:52:10.856288+00:00

- session: `stage-E.1-2026-09-24`
- Databento account: `acct-2`
- quoted cost (USD): nan
- request parameters: `{"dataset": "GLBX.MDP3", "symbols": ["RTY.v.0"], "schema": "mbp-1", "stype_in": "continuous", "start": "2026-02-10T23:00:00Z", "end": "2026-02-11T22:00:00Z"}`
- session spent before: $77.7556 (cap $113.48)
- account acct-2 spent before: $77.7556 (cap $125.00)
- reason stopped: unpriceable request (quote=None): never assumed cheap

### Databento request refused by spend gate — 2026-09-25T04:53:39.712892+00:00

- session: `stage-E.1-2026-09-24`
- Databento account: `acct-2`
- quoted cost (USD): nan
- request parameters: `{"dataset": "GLBX.MDP3", "symbols": ["RTY.v.0"], "schema": "mbp-1", "stype_in": "continuous", "start": "2026-02-10T23:00:00Z", "end": "2026-02-11T22:00:00Z"}`
- session spent before: $77.7556 (cap $113.48)
- account acct-2 spent before: $77.7556 (cap $125.00)
- reason stopped: unpriceable request (quote=None): never assumed cheap
