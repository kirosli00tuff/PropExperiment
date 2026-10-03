# Stage E.11 interfaces: ml_route_v2 modules, signatures and data contracts

Written by the lead before the build (Tasks 2 to 5). The design is docs/STAGE_E_ML_V2_DESIGN.md (the
"V2.x" references below). All literals live in ml_route_v2/constants.py (written by the lead). A
worker that needs a new literal adds it to constants.py with a V2.x comment and reports it. A worker
that finds a contract here unworkable stops that piece and reports to the lead. It never silently
changes the contract.

## 0. Rules for every build worker

- **Synthetic data only.** Never open data/processed*, data/vendor, data/sealed, any *.parquet or
  *.dbn* in the repo, any Stage E screen, confirmation or result report, progress.md,
  docs/STAGES.md or .env. Generators: ml_route/synthetic.py (synthetic_bars, synthetic_events,
  synthetic_inputs, synthetic_matrix) and ml_route_v2/synthetic.py (Task 5).
- **Write only your own files** (ownership table, section 9). Import from ml_route/, screening/,
  rules/, sim/, data/, strategy/ and funnel/, but never edit them. Create nothing under those
  directories: they are harness directories, and an unlisted file there breaks the harness
  preflight.
- **Test files are named tests/test_ml_v2_<topic>.py**, never test_ml_route_*.py or _stage_e_*.py,
  which the harness manifest would freeze. Shared fixtures go in tests/ml_v2_fixtures.py (Task 5
  owns it; others may add a fixture there and say so).
- **Causality.** Every value used at decision time t is computed from bars whose open is <= t - 1 min
  (closed by t) and from calendars known in advance. Every signal returns its availability
  timestamp (section 3).
- **Determinism.** Seeds from constants.SEED. Results are identical across two runs; test it.
- **Compute.** `nice -n 10`. At most 8 threads for any learner, `OPENBLAS_NUM_THREADS=1` otherwise.
  Tests stay small (seconds). Run only your own tests, `uv run pytest -q tests/test_ml_v2_<x>.py`,
  with output to a file under reports/stage_e11_briefs/ and only the tail read. Never run the full
  suite; the lead does.
- **Code style.** Match ml_route/: module docstrings that cite the design section, frozen
  dataclasses, no mutation of inputs, small functions, explicit errors (raise with a named reason),
  no print in library code.
- **Return to the lead:** the paths written, a summary of at most 200 words, the test result line,
  every deviation from this file, and anything unfinished.

## 1. Time and bar conventions (from the repo)

- A bar frame per root is a pandas DataFrame with the repo's BAR_COLUMNS (data/stage_e_bars.py:66):
  - ts_event: int64, UTC ns of the bar OPEN; a bar closes 60 s later;
  - open, high, low, close: float64;
  - volume, instrument_id;
  - trade_date: an ISO 'YYYY-MM-DD' string, the CME trade date;
  - plus the engine's flag columns.
  ml_route/synthetic.synthetic_bars emits exactly this.
- Decision clock (V2.2): a decision at clock time t has decision_ts_ns = t, the close of the bar
  opening at t - 1 min, which is the engine's decision_ts of that bar. It may use bars with
  ts_event <= t - 60 s. The entry fills at the open of the bar with ts_event = t, or later under
  the D9.5a fill guard.
- Session clocks, flatten times and cost buckets are in America/Chicago. Reuse ml_route/inputs.py
  (sessions, S_X, releases) and rules/sessions.py (flatten).
- Prices for features and targets come from the price-path root (constants.UNIVERSE) and are
  converted to vehicle ticks: price units / the vehicle's tick size. The price path and the vehicle
  quote the same underlying in the same units.

## 2. clock.py (Task 2): decision rows

```python
def decision_times_ct(group: str) -> tuple[time, ...]          # V2.2 rule; pinned to constants.DECISION_TIMES_CT
def decision_rows(roots: Sequence[str], trade_dates: Mapping[str, Sequence[date]],
                  *, exclude: Mapping[str, frozenset[date]] | None = None) -> pd.DataFrame
```

DecisionRows has one row per (root, trade_date, t_index), sorted by (decision_ts_ns, root):

| column | dtype | meaning |
|---|---|---|
| root | str | vehicle root, a key of constants.UNIVERSE |
| path_root | str | price-path root |
| cluster | str | K1..K7 |
| group | str | session group (equity, rates, fx, energy, gold, copper, grains, livestock, crypto) |
| trade_date | datetime64[ns] | CME trade date, normalized |
| t_index | int8 | 1, 2 or 3 |
| decision_ts_ns | int64 | t in UTC ns |
| flatten_ts_ns | int64 | F_X of that date in UTC ns |

Excluded dates are dropped: roll blackout, early close or halt, and the caller's exclude map.

## 3. signals/ (Task 2): the library

```python
@dataclass(frozen=True)
class SignalSpec:
    name: str                 # feature column stem, e.g. "k4_eiafade_move" or "g01_ret30"
    family: str               # member id ("K4-eiafade-01") or generic id ("G1")
    cluster: str | None
    kind: str                 # "member" | "generic" | "flag" | "id"
    source: str               # file:line of the member definition or design section
    roots_read: tuple[str, ...]
    normalize: bool           # False for flags and identifiers
    fn: Callable[["SignalContext"], pd.DataFrame]

@dataclass(frozen=True)
class SignalContext:
    rows: pd.DataFrame                    # DecisionRows (all products)
    bars: Mapping[str, pd.DataFrame]      # by price-path root (plus signal-only roots such as MES)
    releases: Any                         # the release calendar object used by ml_route/inputs.py
    sigma_d: pd.Series                    # sigma_X,d in vehicle ticks, aligned to rows (from targets.py)

REGISTRY: Mapping[str, SignalSpec]        # signals/__init__.py; every V2.3 signal; order fixed
EXCLUDED: Mapping[str, str]               # family id -> reason it cannot be a causal signal
def compute_signals(ctx: SignalContext, names: Sequence[str] | None = None) -> pd.DataFrame
def assert_causal(signal_frame: pd.DataFrame, rows: pd.DataFrame) -> None   # raises CausalityError
```

- Each fn returns a frame aligned to ctx.rows (same index), with columns value (float64; NaN means
  missing for data reasons), applicable (float64 0/1) and avail_ts_ns (int64, at most
  decision_ts_ns).
- compute_signals returns raw_<name>, app_<name> and avail_<name> for each name, and
  assert_causal(...) has run on it.

## 4. normalize.py, targets.py, cost_filter.py, panel.py (Task 2)

```python
def zscore_causal(raw: pd.DataFrame, rows: pd.DataFrame, cols: Sequence[str], *,
                  window_dates: int = Z_WINDOW_DATES, min_dates: int = Z_MIN_DATES,
                  clip: float = Z_CLIP) -> pd.DataFrame       # per root, strictly earlier trade dates
def sigma_d(rows: pd.DataFrame, bars: Mapping[str, pd.DataFrame]) -> pd.Series   # v1 ML-A06, vehicle ticks
def build_targets(rows: pd.DataFrame, bars: Mapping[str, pd.DataFrame], *, releases: Any,
                  costs: Mapping[str, Any]) -> pd.DataFrame
def c_sigma_table(panel: pd.DataFrame) -> pd.DataFrame          # V2.2 filter, training rows only
def risk_table(panel: pd.DataFrame) -> pd.DataFrame             # sigma(p,h), L(p,h), mean cost
def build_panel(ctx: SignalContext, targets: pd.DataFrame, *, mode: str = "train") -> Panel
def assert_window(panel_or_rows: pd.DataFrame, mode: str = "train") -> None   # raises if any date >= FORBIDDEN_FROM in train mode
```

**targets** is aligned to rows. For each h in HORIZONS:
- y_gross_<h>: float64 vehicle ticks; NaN where the horizon does not exist or a bar is missing;
- cost_long_<h> and cost_short_<h>: the D8 round trip at size 1 in vehicle ticks: commission over
  tick value, plus the entry and exit side slippage from screening.stage_e_frozen ProductCosts,
  with the event-window rule;
- exit_ts_ns_<h>;
- y_norm_<h> = y_gross / sigma_d;
- ok_<h>: bool.

Also the columns entry_price and sigma_d.

**Panel** is a frozen dataclass:
- frame: pd.DataFrame, holding DecisionRows columns, then z_<name> features (0 where not
  applicable), app_<name> flags, id_root_<X> and id_cluster_<K> one-hots, then the targets
  columns;
- feature_cols: tuple[str, ...], the ordered model inputs (z_*, app_*, id_*);
- signal_names: tuple[str, ...];
- horizons: tuple[str, ...];
- avail_max_ts_ns: np.ndarray.

**c_sigma_table** and **risk_table** return one row per (root, horizon):
- c_ticks: mean of max(cost_long, cost_short);
- sigma_ticks: sd of y_gross;
- ratio, admissible: ratio <= C_SIGMA_TAU;
- loss_ticks: the LOSS_QUANTILE of |y_gross|;
- n_rows.

## 5. configs.py, models.py, cpcv.py, gate0.py, decide.py (Task 3)

```python
@dataclass(frozen=True)
class ModelSpec: kind: str; param: float; model_id: str        # "ridge" lambda | "lgbm" max_depth
@dataclass(frozen=True)
class Config: config_id: str; model: ModelSpec; k: float; horizon: str
CONFIGS: tuple[Config, ...]                                     # the 45, fixed order
def tie_break_key(config: Config) -> tuple                      # V2.9 smaller-model order
class ConfigLedger:                                             # append-only JSONL, resumable
    def __init__(self, path: Path) -> None
    def register(self, entry_id: str, kind: str, spec: Mapping) -> None   # "config" | "gate0_A" | "gate0_B"; same id + different spec raises
    def n_registered(self, kind: str | None = None) -> int
    def n_total(self, n_program: int = N_PROGRAM_AT_DRAFT) -> int

@dataclass(frozen=True)
class FittedModel: spec: ModelSpec; sha256: str; payload: bytes
def fit_model(spec: ModelSpec, X: np.ndarray, y: np.ndarray, *, seed: int = SEED) -> FittedModel
def predict(model: FittedModel, X: np.ndarray) -> np.ndarray   # float64, deterministic

@dataclass(frozen=True)
class Split: index: int; test_blocks: tuple[int, ...]; train_dates: frozenset[date];
             test_dates: frozenset[date]; embargo_dates: frozenset[date]
def calendar_blocks(dates: Sequence[date], n_blocks: int = N_BLOCKS) -> tuple[tuple[date, ...], ...]
def outer_splits(blocks) -> tuple[Split, ...]                   # C(6,2) = 15
def inner_splits(outer: Split, blocks) -> tuple[Split, ...]     # 4 leave-one-block-out folds inside outer train
def split_masks(split: Split, trade_date: np.ndarray, decision_ts_ns: np.ndarray,
                exit_ts_ns: np.ndarray) -> tuple[np.ndarray, np.ndarray]   # purge + embargo
def assemble_paths(splits: Sequence[Split], n_blocks: int = N_BLOCKS) -> tuple[dict[int, int], ...]  # 5 paths: block -> split index
def nested_cpcv(panel: Panel, configs: Sequence[Config], score_fn: ScoreFn, *,
                ledger: ConfigLedger, state_dir: Path) -> NestedResult   # resumable per (config, split)
def final_selection(panel, configs, score_fn, *, ledger, state_dir) -> FinalResult
def pbo_cscv(perf: np.ndarray, n_blocks: int = PBO_BLOCKS) -> dict    # rows = dates, cols = configs; reuse funnel.multiple_comparisons
def dsr_at_n(daily: np.ndarray, n_trials: int, sharpe_variance: float) -> dict   # reuse funnel.multiple_comparisons

ScoreFn = Callable[[pd.DataFrame, np.ndarray, Config], "SplitScore"]   # (test rows, r_hat in vehicle ticks, config)
@dataclass(frozen=True)
class SplitScore: sharpe: float; n_trades: int; daily: pd.Series      # daily net $ indexed by trade_date, zeros on no-trade dates

@dataclass(frozen=True)
class Gate0Rule: cost_multiple=GATE0_COST_MULTIPLE; t_min=GATE0_T_MIN; alpha=GATE0_FAMILY_ALPHA;
                 top_fraction=GATE0_TOP_FRACTION; min_trades=GATE0_MIN_TRADES;
                 holm_includes_a=GATE0_HOLM_INCLUDES_FAMILY_A
def gate0_family_a(panel: Panel, *, ledger: ConfigLedger) -> list[Gate0Test]
def gate0_family_b(panel: Panel, *, ledger: ConfigLedger, state_dir: Path) -> list[Gate0Test]
def gate0_verdict(tests: Sequence[Gate0Test], rule: Gate0Rule = Gate0Rule()) -> Gate0Verdict

def cost_gate(r_hat_ticks: np.ndarray, cost_long: np.ndarray, cost_short: np.ndarray,
              k: float) -> tuple[np.ndarray, np.ndarray]    # (side int8 in {-1,0,1}, edge/cost)
def candidates(rows: pd.DataFrame, r_hat_ticks: np.ndarray, config: Config) -> pd.DataFrame  # section 6 contract
```

Gate0Test (frozen dataclass) has these fields:
- test_id, family ("A" or "B"), signal (A) or root (B), horizon;
- n_dates, n_obs;
- mean (A: mean of m_d; B: mean gross ticks per trade);
- t, p (A two-sided, B one-sided);
- cost_ticks (B), n_trades (B), ic_spearman (A).

Every test is registered in the ledger before it is computed.

Gate0Verdict carries passed (bool), passing (tuple of test_id), n_tests and a holm table (list of
dicts).

Rows are reduced to dates before t (date clustering, V2.2b).

## 6. Candidate trades (decide.candidates output, the Task 3 to Task 4 contract)

One row per decision row where the cost gate says trade. Columns:
- root, cluster, trade_date, decision_ts_ns, horizon;
- exit_ts_ns: the horizon's exit, or the flatten;
- side: int8, +1 or -1;
- r_hat_ticks: float64;
- cost_ticks: float64, the side's round trip;
- edge_over_cost: float64.

portfolio.py joins risk_table (sigma_ticks, loss_ticks) and the vehicle facts (tick_value_usd,
lot_equiv) itself.

## 7. account.py, sizing.py, portfolio.py, selection_metric.py, killswitch.py, simulate.py, payout_sim.py (Task 4)

```python
@dataclass(frozen=True)
class AccountSpec:  # V2.0, V2.8, V2.9; sources in field comments
    name: str; mll_usd: float; dll_usd: float; standard_cap_usd: float; consistency_cap_usd: float
    dll_cap_multiplier: float; balance_ceiling_frac: float; min_payout_usd: float; split: float
    standard_min_days: int; standard_winning_day_usd: float; consistency_min_days: int
    consistency_largest_frac: float; base_lots: float; scaling_tiers: tuple[tuple[float, bool, float], ...]
ACCOUNT_50K: AccountSpec      # from rules.xfa_rules.XFA_50K and the facts file
ACCOUNT_150K: AccountSpec     # facts F12.2a-c, V22 MLL $4,500; 50K tiers until confirmed (V2.12 item 12)

def contracts(*, d_open: float, d_now: float, sigma_ticks: float, loss_ticks: float, cost_ticks: float,
              tick_value_usd: float, product_cap: int, capacity_contracts: int,
              multiplier: float = 1.0) -> int                       # V2.8; 0 means no trade
def accept_trades(cands: pd.DataFrame, risk: pd.DataFrame, account: AccountSpec, *,
                  d_fixed: float | None) -> pd.DataFrame            # caps in time order; adds contracts
def fixed_d_daily_pnl(accepted: pd.DataFrame, targets: pd.DataFrame) -> pd.Series   # net $ per trade_date
def score_split(test_rows: pd.DataFrame, r_hat_ticks: np.ndarray, config: Config, *,
                risk: pd.DataFrame, account: AccountSpec = ACCOUNT_50K) -> SplitScore   # the ScoreFn

class KillSwitches: ...       # V2.8 KS1-KS5 state machine; pure transitions returning new state
def run_portfolio(frames: Mapping[str, pd.DataFrame], schedule: pd.DataFrame, risk: pd.DataFrame,
                  *, account: AccountSpec = ACCOUNT_50K, rules_kwargs: Mapping | None = None) -> PortfolioRun
@dataclass(frozen=True)
class TradeRecord: root: str; horizon: str; trade_date: date; contracts: int; pnl_usd_per_contract: float
                   worst_usd_per_contract: float; sigma_ticks: float; loss_ticks: float; cost_ticks: float
                   tick_value_usd: float; lot_equiv: float
@dataclass(frozen=True)
class DayRecord: trade_date: date; trades: tuple[TradeRecord, ...]
def run_path(days: Sequence[DayRecord], account: AccountSpec, *, path_type: str, dll: bool,
             ks: bool = True) -> PathResult                         # deterministic; tests pin it
def simulate_payouts(days: Sequence[DayRecord], account: AccountSpec, *, path_type: str, dll: bool,
                     n_paths: int = PAYOUT_PATHS, horizon: int = PAYOUT_HORIZON_DATES,
                     block_mean: int = PAYOUT_BLOCK_MEAN, seed: int = SEED,
                     n_accounts: int = N_COPIED_ACCOUNTS) -> PayoutSummary
```

**The schedule** is the candidates frame of section 6, decided ahead of time from the model's
predictions. run_portfolio sizes each trade at its decision time from the engine's account view (D
from balance and floor). It issues market intents at decision_ts and exits at exit_ts, or lets the
engine's flatten close the position.

**PortfolioRules** subclasses screening.stage_e_rules.StageERules. It differs only as V2.8 states:
- no engine_second_leg_position;
- the member lot-equivalent cap applies per product.

The engine's XFA gate, fills, costs, fill guard, CPI window, price-limit rules, flatten, entry cap,
minimum hold and MLL are inherited unchanged. Tests:
- a single-product schedule reproduces the frozen StageERules path fill for fill;
- a hand-computed two-product day matches to the cent.

PortfolioRun carries engine_result, trips, days (tuple of DayRecord) and the daily net dollars.

## 8. synthetic.py, pipeline.py, probe.py and the canaries (Task 5)

```python
def synthetic_universe(roots: Sequence[str], first: date, last: date, *, seed: int,
                       plant: Mapping[str, Any] | None = None) -> SyntheticWorld   # bars by root, releases, costs
def run_pipeline(world: SyntheticWorld, *, state_dir: Path, configs: Sequence[Config] = CONFIGS,
                 timing: bool = True) -> PipelineReport   # panel -> filter -> Gate 0 -> nested CPCV -> final -> simulate -> payouts
```

- probe.py is a CLI: `python -m ml_route_v2.probe --products 28|8 --state-dir <dir>`. It writes
  per-stage wall time, peak RSS and disk.
- tests/test_ml_v2_leakage.py holds the canaries of V2.9 and the Gate 0 canaries.
- tests/test_ml_v2_e2e.py holds the small end-to-end run.

## 9. Ownership

| Owner | Files |
|---|---|
| lead | ml_route_v2/__init__.py, constants.py, this file, the design draft |
| Task 2 SignalCoder | ml_route_v2/clock.py, signals/ (package), normalize.py, targets.py, cost_filter.py, panel.py; tests/test_ml_v2_clock.py, _signals.py, _normalize.py, _targets.py, _panel.py; reports/stage_e11_signal_coverage.md |
| Task 3 ModelCoder | ml_route_v2/configs.py, models.py, cpcv.py, gate0.py, decide.py; tests/test_ml_v2_models.py, _cpcv.py, _gate0.py, _decide.py, _configs.py |
| Task 4 PortfolioCoder | ml_route_v2/account.py, sizing.py, portfolio.py, selection_metric.py, killswitch.py, simulate.py, payout_sim.py; tests/test_ml_v2_sizing.py, _portfolio.py, _killswitch.py, _simulate.py, _payout.py |
| Task 5 CanaryCoder | ml_route_v2/synthetic.py, pipeline.py, probe.py; tests/ml_v2_fixtures.py, tests/test_ml_v2_leakage.py, tests/test_ml_v2_e2e.py; reports/stage_e11_runtime_probe.md |
| Task 6 KeyFix | data/config.py, tests/test_stage_e_config_keys.py, the harness manifest |

**Cross-task imports while building in parallel.** Task 3 depends on Task 2's Panel only through
the frame's columns, and Task 4 on Task 3 only through Config, SplitScore and the candidates frame.
A worker whose dependency is not written yet:
- builds a minimal synthetic frame with the documented columns in its own tests;
- imports Config and SplitScore lazily; or
- defines a local Protocol with the same names, which it removes once the module exists.
