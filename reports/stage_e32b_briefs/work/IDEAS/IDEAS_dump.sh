#!/bin/bash
# IDEAS helper: compact dump of T3/T4/T6/T7 items of F2 family files (id, codes, topic, value, window, verified, neg, pointer, detail, quote, file)
cd /home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e32b_briefs
for f in crude natgas metals grains rates equity fx crypto; do
  jq -r '.items[] | select(.topic=="T3" or .topic=="T4" or .topic=="T6" or .topic=="T7") |
   "\(.id)\t\(.codes|join(","))\t\(.topic)\t\(.field)\tval=\(.value|tostring|.[0:120])\twin=\(.window|tostring|.[0:60])\tv=\(.verified)\tneg=\(.negative)\tptr=\(.pointer)\tD=\(.detail|tostring|.[0:400])\tQ=\(.quote|tostring|.[0:300])\tF=\(.source.file|tostring)"' F2_$f.json
done > work/IDEAS/IDEAS_items.tsv
wc -l work/IDEAS/IDEAS_items.tsv
