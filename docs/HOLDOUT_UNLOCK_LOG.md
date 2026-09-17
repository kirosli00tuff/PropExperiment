# Holdout unlock log

Append-only. `data/holdout.py` writes each entry BEFORE any sealed byte is decrypted. Do not edit or delete entries.

## 2026-09-17T14:47:27.806548+00:00 SEALED

- holdout trade dates 2026-06-22..2026-09-16 (85198 bars)
- sealed raw files: range=2026-06-01_2026-07-01.dbn.zst, range=2026-07-01_2026-08-01.dbn.zst, range=2026-08-01_2026-09-01.dbn.zst, range=2026-09-01_2026-09-16.dbn.zst
- manifest sha256: 0c8d7edb869a66682c0c957d226140408b8265d9a236ea6feac1baa04ef76490

## 2026-09-17T22:14:30.118839+00:00 MANIFEST HARDENED

- added repo-relative paths (a moved repo must not look unsealed and get re-bought)
- pinned this log's byte length and sha256 so a deletion or rewrite fails verify_seal
- no sealed bytes were read or decrypted
