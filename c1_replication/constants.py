"""Test C1's fixed parameters (the backward NG replication; reports/stage_e14_prereg_C1.md).

Every constant of the replication lives here, never in ml_route_v2/constants.py, which stays
byte-identical (rulings C1, C2): a changed constants fingerprint makes E.12's build and Gate 0
state unreadable. Each value names its source.
"""

from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

from data.config import REPO_ROOT

# ------------------------------------------------------------------ the test ----
TEST = "C1"  # the trial registry's label (screening.trial_registry)
TEST_IDS = ("C1-T1", "C1-T2")  # prereg section 5: T1 = NG h60, T2 = NG hF
HORIZON_OF = {"C1-T1": "h60", "C1-T2": "hF"}
HORIZONS_TESTED = ("h60", "hF")  # prereg section 1: exactly two tests
VEHICLE = "NG"  # prereg section 2: NG.v.0, NG's own vehicle
PLAN = "ext2010"  # harness v10 store plan (data.pull_hist.EXT2010)
LEG_ROOTS = ("NQ", "ZN", "6E", "GC", "ZC")  # G17 leads live on NG rows (prereg section 2)
STORE_ROOTS = (VEHICLE, *LEG_ROOTS)  # the six ext2010 stores
EMPTY_ROOTS = ("CL", "MBT")  # ruling C7: empty frames, CL never live on NG rows, MBT not listed
WINDOW_FIRST = date(2010, 6, 7)  # ruling C5: fixed start for every root
WINDOW_LAST = date(2019, 4, 30)  # ruling C6: the quote end, no May-2019 splice

# ------------------------------------------------------------------ the pass bar ----
# Prereg section 5 (ruling C16): gate0._b_test's statistic; pass iff mean g >= 1.5 c, one-sided
# p <= 0.025 (Bonferroni 0.05 / 2) and at least 30 trades; the replication passes iff T1 or T2.
COST_MULTIPLE = 1.5
ALPHA_ONE_SIDED = 0.025
MIN_TRADES = 30
PASS, FAIL, STOPPED = "PASS", "FAIL", "STOPPED"

# ------------------------------------------------------------------ calendars ----
C12_MAX_SHARE = 0.02  # ruling C12: stop when more than 2% of the dates are excluded as unsourced
D8_RELEASES = ("NGS", "WPSR", "FOMC")  # NG's D8 list (reports/stage_e2b_release_calendar.json)
NGS = "NGS"
RELEASE_GRADES_SOURCED = ("official", "secondary")  # calendar_rules.md "Grades"
RELEASE_SCHEMA = "e14_release_calendar/1"
FULL_SESSIONS_KEY = "ENERGY_FULL_SESSIONS"  # reports/stage_e14_cal_energy_full_sessions.json
# Rule H-1 (rules/sessions.py lines 20-40, Stage E.5): each weekday the (hist) equity calendar
# lists is "markets closed" (full closure) or close-by = the equity halt minus the lead; the lead
# is 30 minutes, the earliest published one (lead ruling L-E5-2); every July 3 is unsettled (no
# row). The derived rows stop before rules.sessions.TOPSTEP_DERIVED_FIRST (2019-05-01), where
# E.5's own rows begin.
H1_LEAD = timedelta(minutes=30)
H1_SOURCE = "topstep_derived_e14_c1_hist_equity_calendar"
H1_UNSETTLED = (7, 3)  # (month, day): every July 3
H1_LEAD_YEARS = tuple(range(2010, 2019))  # TOPSTEP_EARLY_CLOSE_LEAD gains these years (30 min)

# ------------------------------------------------------------------ frozen E.12 facts ----
# reports/stage_e12_ml_v2_freeze.json (E.12 Task 3), the manifest every phase-1 step verified; a
# C1 step verifies it again, so every ml_route_v2 file is the one E.12 ran.
V2_FREEZE_MANIFEST = REPO_ROOT / "reports" / "stage_e12_ml_v2_freeze.json"
V2_FREEZE_SHA256 = "a647cd06c8f71f9549c0afa1c740bc32bad05e8f83ed57c87642a1586a0cad5b"
# E.12 Gate 0's report and test list (committed at 94a92b6).
E12_GATE0_REPORT = REPO_ROOT / "reports" / "stage_e12_gate0.json"
E12_GATE0_REPORT_SHA256 = "c0af61c2f7c94ac188d4eaedcfb9d8b224947fa299e82aeea058769d99414806"
E12_GATE0_LIST = REPO_ROOT / "reports" / "stage_e12_gate0_list.json"
E12_GATE0_LIST_SHA256 = "53e7ef576feba9959360b52a633b793175bce98d62a839fefa0f41baf19fa8ea"
ML_LEDGER = REPO_ROOT / "ledger" / "ml_v2_config_ledger.jsonl"  # E.12's Gate 0 registrations
E12_GATE0_DIR = "gate0"  # gate0_stage.GATE0_DIR under the state dir
STATE_MANIFEST_SCHEMA = "e14_e12_state_manifest/1"
REPRO_TOLERANCE = 1e-9  # ruling C4: floats compared ABSOLUTE |a - b| <= 1e-9; counts exactly

# ------------------------------------------------------------------ outputs ----
MODEL_SCHEMA = "stage_e14_c1_model/1"
RESULT_SCHEMA = "stage_e14_c1_result/1"
MARKER_SCHEMA = "stage_e14_c1_run_once/1"
MODEL_JSON = REPO_ROOT / "reports" / "stage_e14_c1_model.json"
MARKER_PATH = REPO_ROOT / "reports" / "stage_e14_c1_RUN_ONCE.json"
FREEZE_PATH = REPO_ROOT / "reports" / "stage_e14_prereg_C1.md"
CODE_DIR = Path(__file__).resolve().parent
RC_REFUSED = 2  # nothing written, nothing run
RC_STOP = 3  # q_m1: "C1 STOP" (a reproduction mismatch or a guard), nothing else written

__all__ = [n for n in dir() if n.isupper()]
