#!/bin/bash
# retrying wrapper: A1_rates_rfetch.sh url out note
D=/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e28_briefs
for i in 1 2 3 4; do
  R=$($D/work/A1_rates/A1_rates_fetch.sh "$1" "$2" "$3 try$i" 2>/dev/null | tail -1)
  case "$R" in *http=200*) echo "$R"; exit 0;; esac
  # drop failed log line
  sed -i '$d' $D/pages/A1_rates/log.tsv; rm -f $D/pages/A1_rates/$2
  sleep 15
done
echo "FAIL $2 $R"
