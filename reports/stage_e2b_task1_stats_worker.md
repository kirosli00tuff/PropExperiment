# Stage E.2b Task 1 (statistics): ScreenStatsCoder-OpusXHigh worker report

Status: DONE, 2026-09-26 13:08 PDT. Signatures were first posted at about 12:50 PDT; the version
below is final. Changes since that first post:
- Tier values follow lead ruling OC-H: `ClusterTiers.excluded` replaces `untiered`, and
  `TierRulingRequired` is gone. `k_from_tiers` was added.
- `PowerCheck` gains `epsilon_table_sha256`, `n_b_censored` and `zero_variance_draws`.
- Lead ruling OC-I (received about 13:03 PDT) adds n_a:
  - **`power_check` now takes `cluster`**: `power_check(series, cluster, ordinal, supply_days)`.
  - `PowerCheck` gains `cluster`, `cluster_members`, `alpha_a`, `z_a` and the `n_a_*` fields.
  - The curve points are now `CurvePoint`.

## Public signatures (for RunnerCoder)

Import everything from `screening.stage_e_stats`. It re-exports the units, power and start-rule
modules.

Every series and every epsilon uses one unit: **net ticks per contract per day of the vehicle**
("ticks/ct/day"). This is the unit of eps_X (`eps_operative`) in reports/stage_e2a_epsilon.json.
Frozen values (eps_X, q_c, tick value) are read from that file by vehicle and never passed in.
No function reads a bar.

```python
# ---- units and series (screening/stage_e_stats_units.py)
@dataclass(frozen=True)
class Trip:
    trade_date: date          # the trade date the round trip closes on
    net_usd: float            # round-trip net P&L after costs, USD, whole position
    contracts: int            # the trip's own contract quantity, >= 1

@dataclass(frozen=True)
class DailySeries:            # build it with the two constructors below
    member_id: str
    vehicle: str              # the (primary-leg) vehicle whose eps_X applies
    dates: tuple[date, ...]   # every research-window trade date after exclusions, strictly ascending
    values: tuple[float, ...] # ticks/ct/day, 0.0 on a window date without a trip
    n_trips: int
    def array(self) -> np.ndarray: ...

def daily_series_from_trips(member_id: str, vehicle: str, trips: Sequence[Trip],
                            window_dates: Sequence[date]) -> DailySeries
    # single-vehicle member: per date, sum of net_usd / (contracts * tick_value_usd[vehicle]);
    # a trip dated outside window_dates, contracts < 1 or a non-finite net_usd raises.
def daily_series_from_leg_dollars(member_id: str, primary_vehicle: str,
                                  daily_net_usd: Mapping[date, float],
                                  window_dates: Sequence[date], n_trips: int) -> DailySeries
    # multi-leg member (NULL_CRITERIA_E 3): combined net USD per day at the frozen leg sizes
    # / (q_c * tick_value_usd) of the primary leg; a window date absent from the mapping is 0.0.

@dataclass(frozen=True)
class FrozenEpsilon:
    vehicle: str; eps_ticks: int; q_c: int; tick_value_usd: float
    eps_usd_per_day_at_q: float   # eps_ticks * q_c * tick_value_usd
    source_sha256: str            # sha256 of reports/stage_e2a_epsilon.json
def frozen_epsilon(vehicle: str) -> FrozenEpsilon        # unknown vehicle (e.g. MES) raises KeyError
def ticks_to_usd_per_day(ticks_per_contract: float, q_c: int, tick_value_usd: float) -> float

# ---- D5 screen and tiers (screening/stage_e_stats.py)
SCREEN_T_MIN = 1.0
class ScreenUndefined(ValueError)
@dataclass(frozen=True)
class ScreenResult:
    member_id: str; n_days: int; n_trips: int
    mean_ticks: float             # ticks/ct/day over every window date, zeros included
    sd_pop_ticks: float           # population sd (ddof 0), as in D.1f 3.2's pinned daily t
    t_daily: float | None         # mean / (sd_pop / sqrt(n)); None only when sd = 0 and mean <= 0
    passes: bool                  # mean > 0 and t_daily >= 1.0
def screen(series: DailySeries) -> ScreenResult
    # raises ScreenUndefined for n < 2, a non-finite value, or sd = 0 with mean > 0

D9_LABELS = ("coverage_below_0.95", "mean_holding_below_10min",
             "entries_above_20_per_day", "hold_below_2min")
@dataclass(frozen=True)
class TierInput:
    member_id: str
    screen: ScreenResult | None   # None only with "coverage_below_0.95" (never screened)
    labels: tuple[str, ...] = ()  # D9 exclusion labels
@dataclass(frozen=True)
class MemberTier:
    member_id: str; tier: str     # "A", "B" or "excluded"
    screen: ScreenResult | None; labels: tuple[str, ...]; note: str
@dataclass(frozen=True)
class ClusterTiers:
    cluster: str; members: tuple[MemberTier, ...]
    tier_a: tuple[str, ...]       # property
    tier_b: tuple[str, ...]       # property
    excluded: tuple[str, ...]     # property
    has_tier_a: bool              # property: Tier A only (counts toward K)
def assign_tiers(cluster: str, members: Sequence[TierInput]) -> ClusterTiers
def k_from_tiers(tiers: Sequence[ClusterTiers], *, route_tested: bool) -> int
    # clusters with a non-empty Tier A, + 1 when the ML route has a tested rule (V6; F-4); 0 raises

# ---- Holm at alpha_k = 0.05 / K (screening/stage_e_stats.py)
FAMILY_ALPHA = 0.05; MAX_CLUSTERS = 8; MAX_FAMILIES = 9   # V6: the ML route is a ninth family
def holm_alpha_k(k_clusters: int) -> float        # K (families) an int in 1..9 (bool, float, str rejected)
@dataclass(frozen=True)
class HolmRow: member_id: str; p_value: float; rank: int; threshold: float; reject: bool
@dataclass(frozen=True)
class HolmResult:
    k_clusters: int; alpha_k: float; m: int; rows: tuple[HolmRow, ...]   # ascending p, ties by id
    rejected: tuple[str, ...]   # property
def holm_tier_a(pvalues: Mapping[str, float], k_clusters: int) -> HolmResult
    # empty family, or p outside [0, 1] / non-finite, raises

# ---- D4 power check (screening/stage_e_stats_power.py)
POWER_SEED_BASE = 20260922     # seed = POWER_SEED_BASE + ordinal
POWER_REPLICATIONS = 2000
POWER_GRID = (10, 15, 20, 30, 50, 75, 100, 150, 200, 300, 500, 750, 1000, 1500, 2000, 3000)
LABEL_INCONCLUSIVE = "inconclusive by design"; LABEL_SUFFICIENT = "power sufficient"
class PowerCheckUndefined(ValueError)
CLUSTER_MEMBER_COUNTS = {"K1": 5, "K2": 8, "K3": 9, "K4": 8, "K5": 7, "K6": 7, "K7": 6, "K8": 3}
    # read-only mapping; the frozen E.1 recount, docs/STAGE_E_DESIGN.md D5 (OC-I)
def detection_alpha(cluster: str) -> float       # 0.05 / (9 * m_c); unknown cluster raises
@dataclass(frozen=True)
class CurvePoint:
    n: int; power_b: float; se_b: float; power_a: float | None; se_a: float | None
@dataclass(frozen=True)
class PowerCheck:
    member_id: str; vehicle: str; cluster: str; ordinal: int; seed: int
    eps_ticks: int; eps_usd_per_day_at_q: float; epsilon_table_sha256: str
    research_days: int; mean_ticks: float; sd_day_ticks: float   # sd with ddof 1
    lag1: float; vif_boot: float; vif_floored: bool
    n_b_analytic: int; n_b_sim: float | None; n_b_censored: bool; diff_b_pct: float | None
    n_b_chosen: int | None      # None: the simulation never reached 80% on the grid
    cluster_members: int        # m_c (OC-I)
    alpha_a: float; z_a: float  # 0.05 / (9 * m_c) and its one-sided z
    n_a_analytic: int; n_a_sim: float | None; n_a_censored: bool; diff_a_pct: float | None
    n_a_chosen: int | None      # descriptive only (OC-I)
    supply_days: int            # confirmation-window days after exclusions (the runner computes it)
    inconclusive_by_design: bool  # n_b_chosen > supply_days; n_b alone decides
    label: str
    flags: tuple[str, ...]      # _b flags and _a flags as in D.1e
    curve: tuple[CurvePoint, ...]
    replications: int; lengths: tuple[int, ...]; zero_variance_draws: int
def power_check(series: DailySeries, cluster: str, ordinal: int, supply_days: int) -> PowerCheck
    # cluster "K1".."K8" (a cross-cluster member: "K8"). ordinal, supply_days: ints >= 0.
    # Lengths: the grid plus n_a plus n_b, each only if <= 3,000, exactly D.1e's rule.
    # A zero-variance research series (for example, no trips) raises PowerCheckUndefined; the
    # runner catches and records it (lead ruling). A never-reached grid whose label cannot be
    # decided also raises.
# lower level (tests, and the D.1e reproduction; Stage E sessions call power_check):
def null_power_figures(daily, eps_ticks, seed, lengths=None, replications=2000,
                       z_detect=None) -> NullPowerFigures

# ---- D4 start rule (screening/stage_e_stats_start.py); reads no bars
BINDING_FRACTION = 0.25; SENSITIVITY_FRACTIONS = (0.15, 0.40)
REFERENCE_MONTHS = ("2025-04", ..., "2026-05")      # 14 months
EXTENSION_MONTHS = ("2019-05", ..., "2024-02")      # 58 months
EARLIEST_START = date(2019, 5, 6)
@dataclass(frozen=True)
class StartAt: fraction: float; threshold: float; m_star: str | None; s: date | None
@dataclass(frozen=True)
class StartRule:
    vehicle: str; v_ref: float    # contracts per one-minute day-session bar
    reference_monthly_medians: tuple[tuple[str, float], ...]
    extension_monthly_medians: tuple[tuple[str, float | None], ...]
    binding: StartAt; sensitivity: tuple[StartAt, StartAt]   # 0.15, 0.40: descriptive
    s_x: date | None; empty_window: bool
def first_trade_dates_by_month(trade_dates: Iterable[date]) -> dict[str, date]
    # first trade date with bars per month; dates before 2019-05-06 dropped; a date after 2024-02-29 raises
def start_rule(vehicle: str, reference_medians: Mapping[str, float],
               extension_medians: Mapping[str, float | None],
               first_trade_dates: Mapping[str, date]) -> StartRule
    # strict: exactly the 14 reference months; extension keys only 2019-05..2024-02; medians finite
    # and >= 0 (a month without bars: omit it or pass None, and it cannot qualify); V_ref = 0 raises;
    # a first date outside its month, or a 2019-05 date before 2019-05-06, raises.
```

## Lead rulings, as encoded

### OC-H (12:58 PDT): tiers

D9, read literally:
- Coverage below 0.95 means "excluded before screening".
- Mean hold below 10 minutes (floor (c)) means "excluded before confirmation".
- A breach of (a), at most 20 entries per product per trade date, or of (b), the 2-minute minimum
  hold, is excluded the same way.

`tier` therefore takes the values "A", "B" or "excluded". An excluded member stays in the record
with its label(s) and belongs to neither Tier A nor Tier B. A coverage-excluded member must have
`screen=None`; passing a screen raises. A member excluded for (a), (b) or (c) must carry its
computed ScreenResult; omitting it raises. The exclusion applies whatever the screen says.
`has_tier_a` counts Tier A only. D9_LABELS includes the (a) and (b) labels. N accounting is not
computed here.

### OC-I (received about 13:03 PDT): n_a is computed, descriptive only

NULL_CRITERIA_E 5 names "analytic n_b and n_a" as part of the D.1e method.
- **Level:** one-sided z at alpha = 0.05 / (9 x m_c), Holm's most stringent step fixed in advance.
  The 9 is at most 8 clusters plus the ML route (V6, audit ML-A14).
- **m_c:** the cluster's active member count in the frozen E.1 recount (D5). It is the module
  constant `CLUSTER_MEMBER_COUNTS`, cited in the code and read-only: K1 5, K2 8, K3 9, K4 8, K5 7,
  K6 7, K7 6, K8 3.
- **Simulation:** n_a joins the lengths exactly as in D.1e. Its detection curve and 15% rule
  (flags `sim_*_a`) are computed on the same draws.
- **Label:** `label_power` receives n_b only.
- The D.1e bit-identity test stays at D.1e's own m = 58 through the lengths path.

### Rulings on my earlier questions (received about 13:03 PDT)

1. The zero-variance refusal (`PowerCheckUndefined`) stays as a named refusal. It goes to the
   user's question list, and the runner catches and records it.
2. See OC-I above.
3. `frozen_epsilon("MES")` keeps refusing, so MES cannot be a primary leg.
4. The bound labelling for a never-reached grid is accepted as a conservative deviation from D.1e.
   It is documented in the module docstring.

## Files created (nothing else was modified)

- screening/stage_e_stats.py (312 lines): the facade and its signature docstring, the screen,
  tiers, K and Holm.
- screening/stage_e_stats_units.py (203 lines): the unit, the frozen-epsilon lookup and the series
  constructors.
- screening/stage_e_stats_power.py (561 lines): the power check. It restates the D.1e Task 3
  inference core so the frozen screening/ harness carries it, and its only import outside screening/
  is `funnel.null_generator.stationary_bootstrap_indices`.
- screening/stage_e_stats_start.py (174 lines): the start rule.
- tests/test_stage_e_stats.py, tests/test_stage_e_stats_power.py, tests/test_stage_e_stats_start.py.

## Tests: 59 test functions, 95 pytest cases, all passing (17.5 s)

Coverage of the new modules: stats 99%, power 98%, start 99%, units 96%.

tests/test_stage_e_stats_power.py (22 functions):
- Equality with D.1e's functions:
  - `test_variance_functions_equal_d1e` checks autocovariances, VIF and lag-1, bit-equal to
    `_d1e_power_stats` on AR(1) series with t(4) shocks at phi 0, 0.3, -0.4 and 0.8.
  - `test_analytic_sample_size_equals_d1e_and_the_closed_form` and
    `test_interpolation_and_censoring_equal_d1e` do the same for the analytic size and the threshold
    helpers.
  - `test_simulated_curve_equals_d1e_simulate_powers` shows the curve (power_b, se_b, and power_a
    through `z_detect`) is identical to D.1e's `simulate_powers` at the same seed and lengths.
- `test_every_measured_d1e_member_analytic_figures_reproduced`: for all 95 measured D.1e members at
  eps 34, sd_day, vif_boot and n_b_analytic equal reports/stage_d1e_power.json.
- `test_d1e_simulated_days_reproduced_for_mes`: eight or more D.1e rows are reproduced from their
  recorded series at seed 20260922 + D.1e index, D.1e's lengths and n_a at D.1e's own
  0.05 / 58.
  - The rows cover the 3 sim_used_larger_b rows and one each of sim_smaller_ignored_b, censored_b,
    sim_used_larger_a (2 rows), sim_smaller_ignored_a and censored_a, plus one plain row.
  - Every curve point's power_b and power_a is bit-equal.
  - n_a and n_b analytic, sim, chosen, diff and the _a and _b flags all match.
  - The Stage E default lengths (`_default_lengths([n_a, n_b])`) equal D.1e's recorded lengths.
- `test_d1e_sim_used_larger_rows_exist_so_the_switch_is_exercised`: the recorded rows really do
  exercise the switch.
- `test_switch_rule` (6 cases): exactly 15% keeps the analytic figure; 15.5% larger uses the
  simulated one (ceil); more than 15% smaller is ignored; within 15% keeps analytic; censored keeps
  analytic; a never-reached grid gives None. Each case is checked for both the b tag and the a tag.
  `test_switch_rule_rejects_an_unknown_tag` covers a bad tag.
- `test_label_boundary_n_b_equal_to_supply_is_sufficient`: n_b = supply is sufficient and
  supply + 1 is inconclusive.
- `test_label_when_the_simulation_never_reaches_80_percent`: covers the conservative bounds and the
  named refusal.
- `test_power_check_labels_a_noisy_member_inconclusive_and_a_quiet_one_sufficient`: runs on MGC
  (frozen eps 71), checks the seed is base + ordinal, and checks the closed-form n_b.
- `test_power_check_is_deterministic_per_ordinal`.
- `test_power_check_units_follow_the_frozen_epsilon`: MCL, q_c 4, $1 tick; eps 21 = $84 a day; the
  series is USD / 4.
- Refusals:
  - `test_zero_variance_series_is_refused_by_name`
  - `test_bad_ordinal_or_supply_is_refused` (4 cases)
  - `test_non_finite_or_short_series_is_refused`
  - `test_analytic_n_b_above_the_grid_is_not_simulated_at_its_own_length` (memory guard: an
    analytic n_b above 3,000 is never simulated at its own length).
- OC-I:
  - `test_cluster_member_counts_are_the_frozen_e1_recount`: the counts equal D5's, sum to 53 and
    are read-only.
  - `test_detection_level_is_the_most_stringent_step_over_nine_families` (K1, K3, K8): alpha is
    0.05 / (9 m_c) and z is its one-sided quantile.
  - `test_unknown_cluster_is_refused`.
  - `test_power_check_computes_n_a_descriptively_and_labels_on_n_b_alone` (MGC, K2):
    - checks alpha 0.05 / 72, the closed-form n_a, and that n_a and n_b are both in the lengths;
    - chosen n_a exceeds supply while chosen n_b does not, and the member is labelled "power
      sufficient".

tests/test_stage_e_stats.py (25 functions):
- Units:
  - `test_frozen_epsilon_reads_the_e2a_table` checks MGC 71/1/$1, MCL 21/4/$1 (D3's worked example
    floor(85/4) = 21, $84 a day) and MNQ $85.
  - `test_frozen_epsilon_refuses_an_unknown_vehicle` (MES) and `test_ticks_to_usd_per_day`.
- Trips to ticks:
  - `test_trips_become_ticks_per_contract_with_zeros_on_no_trade_days` checks each trip is divided
    by its own contracts, same-date trips are summed, and no-trade dates are 0.
  - `test_trip_conversion_reproduces_d1e_per_micro_series_for_mes` shows the aggregation at a $1.25
    tick reproduces D.1e's `daily_net_ticks_per_micro` from the recorded trip P&Ls and micros for
    6 trial members (the R-1 unit).
  - `test_leg_dollars_use_the_primary_legs_q_and_tick`.
  - Construction refusals: `test_series_construction_refusals` (4 cases) and
    `test_trip_with_bad_contracts_or_value_is_refused`.
- Screen:
  - `test_screen_t_exactly_one_passes`: [3, -1, 3, -1] has mean 1, population sd 2 and n 4, so
    t = 1.0 exactly, which passes.
  - `test_screen_t_just_below_one_fails`.
  - `test_screen_t_is_the_programs_pinned_daily_t`: equals `harvey_liu_zhu_verdict` with population
    sd.
  - `test_screen_counts_zeros_on_no_trade_days`: two trades over 10 window days give mean 0.6 and
    t by hand.
  - `test_screen_negative_mean_fails_and_idle_member_fails`,
    `test_screen_refuses_constant_positive_series_and_one_day` and
    `test_screen_is_unit_free_per_micro_or_per_contract`.
- Tiers (OC-H):
  - `test_tiers_a_b_and_excluded_per_lead_ruling_oc_h` covers all four labels, a coverage-excluded
    member with screen None, and a hold-excluded member that passed its screen yet is excluded.
  - `test_cluster_with_only_excluded_passers_has_no_tier_a`.
  - `test_tier_refusals` (7 cases).
  - `test_k_counts_clusters_with_a_non_empty_tier_a`.
- Holm:
  - `test_holm_textbook_example`: Holm 1979 as taught, with p = .01, .04, .03 and .005 at 0.05;
    H4 and H1 are rejected.
  - `test_holm_at_alpha_k_splits_alpha_over_clusters`: at K = 2 only H4 is rejected.
  - `test_holm_step_down_stops_at_the_first_failure`.
  - `test_holm_matches_d1f_holm_on_random_families`: matches D.1f's `holm` at 0.05 / K for
    K = 1..8.
  - `test_holm_k_is_validated` (6 cases) and `test_holm_p_values_are_validated` (4 cases).

tests/test_stage_e_stats_start.py (12 functions):
- `test_reproduces_the_d1f_mes_start_rule`: from reports/stage_d1f_step5_start_rule.json's recorded
  medians and first dates, V_ref = 1763.0 and threshold 440.75 give M* 2020-02 and S = 2020-02-03.
  At 0.15, S is 2020-01-02 and at 0.40 it is 2020-03-02, all as recorded.
- `test_constants_are_the_frozen_text`.
- `test_month_exactly_at_the_threshold_qualifies`: 25.0 = 0.25 x 100 qualifies, giving
  S = 2019-05-06.
- `test_a_failing_month_moves_the_start_after_it`, including the sensitivity figures.
- `test_last_month_failing_empties_the_window`.
- `test_a_month_without_bars_cannot_qualify` (None and absent).
- `test_short_history_product_starts_at_its_listing`.
- `test_v_ref_is_the_median_of_the_fourteen_monthly_medians`: 0..13 gives 6.5.
- `test_input_refusals` (7 cases), `test_zero_reference_volume_is_refused`,
  `test_first_date_rules` and `test_first_trade_dates_by_month_applies_the_earliest_start`.

## Commands run

- `uv run --no-sync pytest -q tests/test_stage_e_stats*.py` failed at collection before the modules
  existed (RED), then gave 87 passed, and 88 passed after the V_ref = 0 refusal was added (13 s).
- `pytest --cov=screening`: stats 99%, power 98%, start 99%, units 96%. `--cov=<module>` failed with
  numpy's "cannot load module more than once", a pytest-cov quirk; `--cov=screening` works.
- `ruff check` on the 7 new files: all checks passed.
- A one-off full reproduction through `reports/stage_e2b_briefs/heavy.sh`, using the scratchpad
  script repro_d1e_all.py (not a repo file). OMP=1, slot 1, 12:57:48 PDT, 9.6 GB available, 107.5 s:
  - all 95 measured D.1e members at eps 34 give 0 mismatches;
  - 1,689 curve points are bit-equal;
  - n_b_analytic, n_b_sim, chosen_b, diff and _b flags all match, and the flag counts match D.1e's
    (censored 22, smaller ignored 15, zero-variance draws 22, used larger 3).
  - The cost is about 1.1 s per member, so the 53 Stage E members take about 1 minute on one thread.
- After OC-I, the same reproduction was re-run with n_a at D.1e's 0.05 / 58 and the default-lengths
  check. Slot 1, 13:04:25 PDT, 10.0 GB available, 104.6 s:
  - 95 members give 0 mismatches, and all 1,689 curve points are bit-equal on both power_b and
    power_a;
  - n_a analytic, sim, chosen and _a flags match (used larger 7, censored 6, smaller ignored 4, all
    as in D.1e), and so does every n_b figure;
  - the Stage E default lengths equal D.1e's for all 95 members.
- After OC-I: `pytest` on the 3 files gives 95 passed. Coverage: stats 99%, power 98%, start 99%,
  units 96%. Ruff: all checks passed. Every name in `screening.stage_e_stats.__all__` resolves.

## Choices made where the frozen text is silent (the lead may overrule)

1. **Seed**: `20260922 + ordinal`, D.1e's seed base, which is what lets the D.1e reproduction be
   exact. I recommend the runner pass the member's ordinal in its cluster list, the same ordinal
   NULL_CRITERIA_E 3 uses with 20260923.
2. **Stage E lengths** (settled by OC-I): the D.1e grid (10..3,000) plus n_a and n_b, each only
   when <= 3,000, which is D.1e's rule.
   - Because n_a's level depends on m_c, the RNG stream, and so n_b_sim, depends slightly on the
     cluster. This is the D.1e coupling, and the lead accepted it.
   - A never-reached n_a is handled like n_b: chosen None with the flag
     `power_a_never_reaches_target`. It is descriptive only.
3. **Never-reached grid** (accepted by the lead as a conservative deviation): this deviates from
   D.1e, which never met the case; D.1e's code would silently keep the analytic figure.
   - n_b_chosen is None, and the label comes from bounds. It is inconclusive when analytic > supply,
     or when the longest length is >= supply and >= 1.15 x analytic, because the simulated
     threshold then governs and exceeds supply.
   - Otherwise it raises PowerCheckUndefined. With supply of at most about 1,210 days that branch
     cannot be reached.
4. **Memory guard**: an analytic n_a or n_b above 3,000 is not simulated at its own length (such a
   length could need gigabytes); it is flagged `n_a_analytic_above_grid` or
   `n_b_analytic_above_grid`. The label is unaffected, because the chosen n_b is never below the
   analytic figure and 3,000 is more than any supply.
5. **Daily t**: mean / (population sd / sqrt(n)) through `harvey_liu_zhu_verdict`, exactly D.1f
   3.2's pinned daily t. With ddof 1 it would be about 0.17% smaller at n = 300, which matters only
   at the boundary.
6. **Screen refusal**: sd = 0 with mean > 0 raises ScreenUndefined. It is practically impossible
   with zeros on no-trade days. sd = 0 with mean <= 0 fails the screen, so a zero-trip member goes
   to Tier B.

## Open items

1. **For the user's question list** (lead ruling): what label a member gets when its research-window
   series has zero variance (for example, no trips). `power_check` refuses it with
   `PowerCheckUndefined`, and the runner catches and records it. Its screen puts it in Tier B.
2. **Harness freeze**: the four new screening/stage_e_stats*.py files must be in
   reports/stage_e2b_harness_freeze.json (screening/ is in its scope). The functions read
   reports/stage_e2a_epsilon.json directly, relying on the entry point's `preflight()` for its
   hash, and carry its sha256 in every FrozenEpsilon and PowerCheck. They are not entry points and
   read no bars, so there is no preflight test here.
3. **For RunnerCoder**: `power_check` now needs `cluster` ("K1".."K8"; a cross-cluster member is
   "K8").

## Unfinished

Nothing in the brief. N accounting was not computed, per the lead's instruction.

## Follow-up F-4 (Fable review reports/stage_e2b_harness_review.md, SHOULD FIX; fixed 18:26 PDT)

Finding: `holm_alpha_k(9)` raised, and `k_from_tiers` could not count the ML route family. V6
(docs/DECISIONS.md, audit ML-A14) says D5's K counts every family with a non-empty tested set, the
route included once it has a tested rule. Every family then tests at 0.05 / (K + 1), and "at most
8" reads "at most 9". The lead ruled the fix below, in screening/stage_e_stats.py and its tests
only.

- **`MAX_FAMILIES = 9`**: set as `MAX_CLUSTERS + 1`. `MAX_CLUSTERS = 8` is kept for cluster ids.
  `holm_alpha_k` and `holm_tier_a` validate K in 1..9. The parameter keeps its name `k_clusters`
  so existing callers do not break; its docstring says it counts families.
- **`k_from_tiers(tiers, *, route_tested: bool)`**: `route_tested` is a required keyword with no
  default, so leaving it out, or passing it positionally, is a TypeError. A non-bool raises. It
  counts the clusters with a non-empty Tier A (more than 8 raises), plus one when the route has a
  tested rule. K = 0 raises.
- **Callers**: none in screening/ (grep for k_from_tiers and holm_alpha_k: only stage_e_stats.py
  and its tests). The runner uses `screen`, `assign_tiers`, `power_check` and `D9_LABELS`, none of
  them changed. The lead said MLTestCoder updates ml_route's use.
- **New and changed tests** in tests/test_stage_e_stats.py:
  - `test_k_adds_one_for_a_tested_route_rule_v6`: 2 clusters plus the route give K = 3, and alpha
    = 0.05 / 3 is checked against the hand value 0.0166666... The route alone gives K = 1.
  - `test_k_reaches_nine_with_eight_clusters_and_the_route`: 8 clusters give 8, and with the route
    9 = MAX_FAMILIES. alpha 0.05 / 9 is checked against the hand value 0.0055555..., and Holm at
    K = 9 works.
  - `test_k_route_tested_is_a_required_bool_keyword`: a missing or positional argument is a
    TypeError, 1 is refused, and 9 clusters with a Tier A are refused.
  - Existing tests updated: K validation now refuses 10 instead of 9; the D.1f Holm cross-check
    runs K = 1..9; `holm_alpha_k(9) == 0.05 / 9`.
- **Results**:
  - `pytest` on tests/test_stage_e_stats.py, tests/test_stage_e_stats_start.py,
    tests/test_stage_e_stats_power.py and tests/test_stage_e_runner.py: 106 passed, 16 failed.
  - My three files all pass (98 cases).
  - All 16 failures are in tests/test_stage_e_runner.py, and every one is `ModuleNotFoundError:
    No module named 'strategy.members.k1'`. That member-module package belongs to another worker
    and does not exist in the tree yet, so the failures are unrelated to this fix.
  - Ruff: all checks passed.

