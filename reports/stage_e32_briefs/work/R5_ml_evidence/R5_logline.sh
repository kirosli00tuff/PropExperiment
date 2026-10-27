#!/usr/bin/env bash
# usage: R5_logline.sh <url> <method> <file> <note>   (for terms decisions / non-curl fetches)
D=/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e32_briefs/pages/R5_ml_evidence
utc=$(date -u +%Y-%m-%dT%H:%M:%SZ); pdt=$(TZ=America/Vancouver date +%Y-%m-%dT%H:%M:%S%Z)
sha="-"; [ -f "$D/$3" ] && sha=$(sha256sum "$D/$3" | cut -d' ' -f1)
printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\n" "$1" "$utc" "$pdt" "$2" "$sha" "$3" "$4" >> "$D/log.tsv"
