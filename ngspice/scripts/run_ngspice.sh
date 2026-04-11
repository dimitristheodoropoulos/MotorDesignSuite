#!/bin/bash
# run_ngspice.sh is at: ngspice/scripts/run_ngspice.sh
# so two levels up = project root
project_root=$(dirname "$(dirname "$(realpath "$0")")")
circuits_dir="$project_root/ngspice/circuits"
log_dir="$project_root/results/logs"

mkdir -p "$log_dir"

if ! ls "$circuits_dir"/*.cir 1>/dev/null 2>&1; then
    echo "⚠️  No .cir files found in $circuits_dir"
    exit 0
fi

for cir in "$circuits_dir"/*.cir; do
    echo "  → Running $(basename $cir)"
    ngspice -b "$cir" \
        -o "$log_dir/$(basename "$cir" .cir).log" && \
        echo "  ✅ $(basename $cir)" || \
        echo "  ⚠️  $(basename $cir) failed"
done