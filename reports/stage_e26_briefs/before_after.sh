#!/usr/bin/env bash
# Stage E.26 T1.4 / T1.6: the move plan's step-1 (before) and step-4 (after) checks, read-only.
# Usage: before_after.sh before|after. Writes reports/stage_e26_briefs/<phase>_*.{txt,json,out}.
# The sha256 move manifest (step 1 item 4) is move_data.py's own command, run separately.
set -u
cd "$(dirname "$0")/../.."
PH=${1:?before or after}
B=reports/stage_e26_briefs
DEST=/mnt/large-storage/market_data/PropExperiment
SOURCES="data/sealed data/processed_hist data/processed_step2 data/vendor/databento"
H=dd2bcc6025144e0debd19be1ca8d43c983872a27c9258895ef55ee3c138609e4
{
echo "\$ date"; TZ=America/Vancouver date
echo "\$ step 0 preconditions"
mountpoint /mnt/large-storage
echo "open data handles: $(lsof -nP 2>/dev/null | grep -cE 'PropExperiment/data/(vendor|processed|sealed)')"
# real pytest processes only (pgrep -f pytest also matches any shell whose command line names pytest)
for p in $(ps -eo pid,args | awk '$2 ~ /python/ && /-m pytest|bin\/pytest/ {print $1}'); do echo "pytest pid $p cwd $(readlink /proc/$p/cwd 2>/dev/null)"; done
free -m | sed -n 2p
if [ "$PH" = after ]; then
  echo "\$ link guard"
  for s in $SOURCES; do
    if test -L "$s" && test -e "$s" && test "$(readlink -f "$s")" = "$DEST/$s"; then echo "OK   $s -> $(readlink "$s")"; else echo "FAIL $s"; fi
  done
  test -d data/vendor/databento/GLBX.MDP3/ohlcv-1m/MES_v_0 && echo "OK   MES_v_0 reachable" || echo "FAIL MES_v_0"
fi
} > $B/${PH}_step0.txt 2>&1
bash $B/checks.sh $H > $B/${PH}_checks.txt 2>&1
uv run python -m data.holdout status > $B/holdout_${PH}.json 2>/dev/null
python3 -c 'import json,sys;d=json.load(open(sys.argv[1]));h=d["holdout_2"];print(d["all_ok"],d["unlocks_logged"],d["research_parquet_ok"],d["research_has_no_holdout_rows"],h["unlocks_logged"],h["confirmation_has_no_holdout2_rows"],h["unsealed_plaintext_present"],{r:(p["all_ok"],p["store_has_no_embargo_or_holdout2_rows"],p["unsealed_plaintext_present"]) for r,p in h["products"].items()})' $B/holdout_${PH}.json > $B/holdout_${PH}_fields.txt 2>&1
PYTHONPATH=. nice -n 10 uv run python $B/loader_reads.py $B/loader_${PH}.json > $B/loader_${PH}.txt 2>&1
for s in $SOURCES; do
  n=$(echo "$s" | tr '/' '_')
  # review finding 6: directory sizes depend on history, so they are not listed
  find "$s/" \( -type f -printf '%P f %m %s %T@\n' \) -o \( -type d -printf '%P d %m %T@\n' \) | sort > $B/find_${PH}_$n.txt
done
nice -n 10 uv run pytest -q -p no:cacheprovider -rs tests/test_holdout.py tests/test_d1f_holdout2.py \
  tests/test_ml_route_store.py tests/test_base_rules_store.py tests/test_k1_members_tables.py \
  tests/test_build_release_calendar.py tests/test_d1f_confirmation_window.py tests/test_leakage_canaries.py \
  > $B/pytest_subset_${PH}.out 2>&1
echo "done $(TZ=America/Vancouver date +%H:%M:%S)" >> $B/${PH}_step0.txt
