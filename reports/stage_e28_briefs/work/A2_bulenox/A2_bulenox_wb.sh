#!/bin/bash
# usage: A2_bulenox_wb.sh <timestamp> <original-url> <outfile>  (Wayback id_ fetch into pages dir, logged)
P=/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e28_briefs/pages/A2_bulenox
UA='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36'
w="https://web.archive.org/web/${1}id_/${2}"
code=$(curl -g -sL --compressed -m 120 -A "$UA" -H 'Accept-Language: en-US,en;q=0.9' -o "$P/$3" -w '%{http_code}' "$w")
/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e28_briefs/work/A2_bulenox/A2_bulenox_log.sh "$w" "wayback (curl of archive.org, HTTP $code)" "$3" "capture $1 of $2"
echo "$code $(wc -c < $P/$3) $3"
