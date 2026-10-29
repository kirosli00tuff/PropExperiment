"""Write the E.33c Part D briefs from the E.33b drafts: asserted path/protocol replacements plus an E.33c addendum."""
from pathlib import Path

B, C = Path("reports/stage_e33b_briefs"), Path("reports/stage_e33c_briefs")
PROT_OLD = "reports/stage_e32_discovery_protocol.md (sha256 c4ffb9d7...; refuse if it differs)"
PROT_NEW = ("reports/stage_e32_discovery_protocol_v0.3.md (protocol 0.3, sha256 a2a2856f...; refuse if it differs)")
PROT_OLD2 = "reports/stage_e32_discovery_protocol.md (sha256 c4ffb9d7...)"
PROT_NEW2 = "reports/stage_e32_discovery_protocol_v0.3.md (protocol 0.3, sha256 a2a2856f...; refuse if it differs)"
COMMON = [("Stage E.33b", "Stage E.33c"),
          ("reports/stage_e33_briefs/work/D_stats", "reports/stage_e33c_briefs/work/D_stats"),
          ("reports/stage_e33_briefs/work/D4_verify.md", "reports/stage_e33c_briefs/work/D4_verify.md")]
ADD_ALL = """
## E.33c addendum (lead, 2026-10-28 PDT; governs where it differs from the text above)
- Binding protocol: 0.3 = reports/stage_e32_discovery_protocol_v0.3.md, sha256
  a2a2856f49723f97319a4db2819ba4d1b5c4b8a1dc86a596e7c48110dbb48246 (check it; refuse if it differs). It is v1.0
  (c4ffb9d7) plus one amendment of the P5/P10 compute reference only (reports/stage_e33c_briefs/protocol_v0.3.diff);
  P3, P6, P7, P8, P10's null report and every threshold read exactly as in v1.0. The readings file
  reports/stage_e33_protocol_readings.md (FINAL) cites v1.0; its rulings govern 0.3 unchanged.
- N = 838: trial_registry.current_n() after the E33 registration r009-E33 (no E33A registration exists).
- The search is finished: 300 configuration DONE markers (counts and failures in
  reports/stage_e33c_briefs/search_end.txt). The outcome seal is lifted for Part D. Search root
  /mnt/large-storage/market_data/PropExperiment/derived/e33 (search/<cid>/); feature store features/2b30cb0e953b
  (sigma_zm in _day/); label store labels/b15c4ca10d68; schemas in reports/stage_e33_briefs/INTERFACE.md 4.1-4.3.
- The selection: reports/stage_e33c_briefs/select/P8_select33.json, written by the frozen select33.py (sha256
  9b9928066a35..., freeze list reports/stage_e33_pipeline_freeze.sha256 eb565a37) on all 300 at N 838, Tier B
  reading "continue" (readings R-L8); its stdout is P8_select33.out beside it.
- The branch (N: Tier A empty; T: Tier A not empty) is named in the spawn message.
- Python: run with `uv run python` from the repo root at nice 10, with PYTHONPYCACHEPREFIX set to a folder under
  your own scratch path, so no __pycache__ lands in the frozen pipeline folder.
- Times from `date`, in PDT. Do not end your turn while a job of your own runs.
"""
ADD = {
 "StatsCoder": """- Outputs (E.33c paths): reports/stage_e33c_briefs/work/D_stats.md and D_stats.json; code with tests under
  reports/stage_e33c_briefs/work/stats/; figures under reports/stage_e33c_briefs/work/stats/fig/; large outputs under
  derived/e33/stats_c/.
- D3 correction: B5's null search is 20 seeds x 20 configurations (S5 x {F15, T30} x 10 grid points; 400 series;
  reports/stage_e33_briefs/work/B5_proofs.md lines 3 and 38-41; series in
  derived/e33/proofs/seed1..seed20/search/<cid>/). Show the 300 real SR_d beside the 400 null per-configuration SR_d
  (same statistic, 796 dates), and the 20 null per-seed maxima labelled as maxima over 20 configurations: they are not
  the null of the maximum over 300. If you give an expected null maximum over 300, derive it from the null's
  per-configuration spread, state the method, and label it a report.
- Independence: the VerifyWorker recomputes in parallel. Do not read its files under work/verify/ or share code.
""",
 "VerifyWorker": """- Model: Fable at xhigh (V55: independent verifiers on Fable). Fresh context.
- Outputs (E.33c paths): reports/stage_e33c_briefs/work/D4_verify.md; your code under
  reports/stage_e33c_briefs/work/verify/ (not work/stats/, which is the StatsCoder's and which you must not read
  before your own numbers are written); large outputs under derived/e33/verify_c/.
- Compare with the selection output as soon as your own numbers are written. The StatsCoder's D_stats.json may not
  exist yet when you finish: if it is absent, write "StatsCoder comparison pending" in D4_verify.md and return; the
  lead will send a short follow-up.
""",
 "StatsReviewer": """- Model: Fable at xhigh, fresh context. Output: reports/stage_e33c_briefs/review/StatsReview_c.md.
- Read the StatsCoder's reports/stage_e33c_briefs/work/D_stats.md, D_stats.json and work/stats/; the VerifyWorker's
  reports/stage_e33c_briefs/work/D4_verify.md and work/verify/; the selection output above; and the lead's draft
  sections 3-5 of reports/E.33c_RETURN.md when the lead sends them.
- D3 check: B5's null is 20 seeds x 20 configurations (400 series; per-seed maxima over 20, not 300).
""",
}
REPL = {
 "StatsCoder": [("reports/stage_e33_briefs/work/stats/", "reports/stage_e33c_briefs/work/stats/"),
                ("all 300 x 20 null-seed Sharpes, and\nseparately the 20 per-seed maxima",
                 "the 400 null per-configuration Sharpes\n(20 seeds x 20 configurations; see the addendum), and separately the 20 per-seed maxima")],
 "VerifyWorker": [("VerifyWorker-OpusXHigh", "VerifyWorker-FableXHigh"),
                  ("reports/stage_e33_briefs/work/verify/", "reports/stage_e33c_briefs/work/verify/"),
                  ("work/stats/", "reports/stage_e33c_briefs/work/stats/")],
 "StatsReviewer": [("reports/stage_e33_briefs/review/StatsReview_b.md", "reports/stage_e33c_briefs/review/StatsReview_c.md"),
                   ("reports/E.33b_RETURN.md", "reports/E.33c_RETURN.md"),
                   ("work/stats/", "reports/stage_e33c_briefs/work/stats/"),
                   ("work/verify/", "reports/stage_e33c_briefs/work/verify/")],
}
for name in ("StatsCoder", "VerifyWorker", "StatsReviewer"):
    t = (B / f"brief_{name}_b.md").read_text()
    for old, new in [(PROT_OLD, PROT_NEW), (PROT_OLD2, PROT_NEW2)] + COMMON + REPL[name]:
        n = t.count(old)
        if old in (PROT_OLD, PROT_OLD2, "reports/stage_e33_briefs/work/D_stats", "reports/stage_e33_briefs/work/D4_verify.md"):
            t = t.replace(old, new)
            print(name, "optional", repr(old[:40]), n)
            continue
        assert n >= 1, (name, old)
        t = t.replace(old, new)
        print(name, "replaced", repr(old[:40]), n)
    (C / f"brief_{name}_c.md").write_text(t + ADD_ALL + ADD[name])
    print(name, "->", C / f"brief_{name}_c.md", len(t))
