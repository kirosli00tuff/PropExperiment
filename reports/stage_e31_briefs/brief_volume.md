# Brief: VolumeCoder-OpusHigh (worker-high, model opus) - Stage E.31 Part 1 measures

Objective (one): implement exactly the "V3 measures, fixed details" and "Kill rules" sections of
reports/stage_e31_volume_request.md (read it whole; it is binding and frozen, sha256 09d83f43...),
run it once on the purchased file, and write the results.

Inputs:
- the request file above; the purchased DBN file: path in
  reports/stage_e31_briefs/work/pilot/runs/vol_purchase_manifest.json (ohlcv-1d, QM.FUT + ZM.FUT parent,
  2023-01-01 to 2026-10-22T00:00Z). Check its sha256 against the manifest before use.
- databento python package (installed in the project venv) for DBNStore and its symbol mappings.

Outputs:
- code: reports/stage_e31_briefs/work/pilot/vol_measure.py (CLI: --dbn PATH --out-json PATH --out-md PATH)
- tests: reports/stage_e31_briefs/work/pilot/tests/test_vol_measure.py, synthetic arrays only
  (delivery-year decode incl. decade wrap, hyphen filter, zero-fill on union universe, weekend drop,
  front month = earliest delivery, window = last 12 full months before an exclusive end, quarter stats).
  Run: uv run pytest -q -p no:cacheprovider reports/stage_e31_briefs/work/pilot/tests/test_vol_measure.py
- results: reports/stage_e31_briefs/work/pilot/runs/vol_measures.json and reports/stage_e31_volume.md
  (per root x quarter table: days, median, p10, front-month share, top-volume share; the window and its
  day counts; both universes; the check lines; weekend bars count/volume; the two verdicts in the
  request's words, with the median numbers). Also record the instrument count per root and the
  number of hyphen symbols dropped.

Rules:
- Prices are never used, printed, stored or reported. Decode with DBNStore.to_ndarray() (or
  equivalent) and keep only ts_event, instrument_id, volume immediately.
- If any instrument id has no raw symbol in the DBN mappings, stop and report it (do not call any API).
- No Databento or any network call. No other data file is opened (in particular no ZM one-minute bars,
  nothing under data/ other than the purchased file). Do not edit anything outside the three output
  paths above plus the tests folder. No commits.
- Keep command output short (pytest -q; scripts print summaries only).
Return: the paths, a summary of at most 200 words (both medians and verdicts), and anything unfinished.
