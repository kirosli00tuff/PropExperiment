#!/usr/bin/env bash
# Usage: FIRMS_wb.sh <original_url> <outfile> <note>  -- latest Wayback capture (status 200) via CDX, raw (id_) copy
set -u
U="$1"; OUT="$2"; NOTE="$3"
TS=$(curl -s --max-time 40 "https://web.archive.org/cdx/search/cdx?url=$U&output=json&filter=statuscode:200&limit=-1&fl=timestamp" | python3 -c "import json,sys
try:
    d=json.load(sys.stdin); print(d[-1][0] if len(d)>1 else '')
except Exception: print('')")
if [ -z "$TS" ]; then echo "NO CAPTURE $U"; exit 1; fi
sleep 2
/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e32b_briefs/work/FIRMS/FIRMS_fetch.sh "https://web.archive.org/web/${TS}id_/$U" "$OUT" "$NOTE (Wayback capture $TS)" "wayback curl"
